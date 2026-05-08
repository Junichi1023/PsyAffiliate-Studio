from __future__ import annotations

import json
import re
import zipfile
from collections import Counter
from dataclasses import dataclass
from html import unescape
from html.parser import HTMLParser
from io import BytesIO
from pathlib import PurePosixPath
from typing import Any, BinaryIO

from .pii_sanitizer import sanitize_text_with_summary


READ_ENCODINGS = ("utf-8-sig", "utf-8", "utf-16", "latin-1")
MESSAGE_PARTS = {"messages", "messenger", "inbox"}
DEFAULT_EXCLUDED_PARTS = {
    "friends",
    "security_and_login_information",
    "ads_information",
    "payment_history",
    "location",
    "contacts",
    "device_information",
}
PREFERRED_PARTS = {
    "posts",
    "comments_and_reactions",
    "likes_and_reactions",
    "profile_information",
    "photos_and_videos",
    "albums",
    "saved_items",
}
PRIORITY_KEYS = {
    "text",
    "title",
    "description",
    "caption",
    "post",
    "content",
    "message",
    "name",
    "comment",
    "data",
    "attachments",
    "media",
}
IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".gif", ".webp", ".heic", ".mp4", ".mov")
IMPORT_EXTENSIONS = (".json", ".html", ".htm")
IGNORED_HTML_TAGS = {"script", "style", "noscript", "svg"}
BLOCK_HTML_TAGS = {
    "address",
    "article",
    "aside",
    "blockquote",
    "br",
    "dd",
    "div",
    "dl",
    "dt",
    "figcaption",
    "footer",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "header",
    "li",
    "main",
    "p",
    "section",
    "td",
    "th",
    "tr",
}


class FacebookImportError(ValueError):
    pass


@dataclass
class ExtractedText:
    text: str
    source_path: str
    from_messages: bool = False


@dataclass
class FacebookArchiveResult:
    texts: list[ExtractedText]
    total_items: int
    sanitized_items: int
    stats: Counter[str]
    skipped_files: list[str]


def _path_parts(path: str) -> set[str]:
    return {part.lower() for part in PurePosixPath(path).parts if part not in {"", "."}}


def _is_message_path(path: str) -> bool:
    return bool(_path_parts(path) & MESSAGE_PARTS)


def _should_skip(path: str, include_messages: bool) -> bool:
    parts = _path_parts(path)
    if not path.lower().endswith(IMPORT_EXTENSIONS):
        return True
    if not include_messages and parts & MESSAGE_PARTS:
        return True
    return bool(parts & DEFAULT_EXCLUDED_PARTS)


def _path_priority(path: str) -> int:
    parts = _path_parts(path)
    lower_path = path.lower()
    filename = PurePosixPath(lower_path).name
    if "your_posts" in filename:
        return 0
    if parts & {"posts"}:
        if "posts_on_other_pages" in filename:
            return 1
        if "album" in parts or "photos" in filename or "videos" in filename:
            return 4
        return 2
    if parts & {"comments_and_reactions", "likes_and_reactions"}:
        return 3
    if parts & {"profile_information"}:
        return 5
    if parts & {"photos_and_videos", "albums", "saved_items"}:
        return 6
    if parts & MESSAGE_PARTS:
        return 9
    if parts & PREFERRED_PARTS:
        return 4
    return 7


def _decode_bytes(payload: bytes) -> str:
    last_error: Exception | None = None
    for encoding in READ_ENCODINGS:
        try:
            return payload.decode(encoding)
        except UnicodeDecodeError as error:
            last_error = error
    raise FacebookImportError("Facebookエクスポートファイルの文字コードを判別できませんでした") from last_error


def _repair_facebook_text(value: str) -> str:
    if "ã" in value or "Â" in value:
        try:
            repaired = value.encode("latin-1").decode("utf-8")
            if repaired.count("�") <= value.count("�"):
                return repaired
        except UnicodeError:
            return value
    return value


def _is_natural_text(value: str) -> bool:
    text = _repair_facebook_text(value).strip()
    if len(text) < 20:
        return False
    if re.fullmatch(r"https?://\S+|www\.\S+", text, re.IGNORECASE):
        return False
    if re.fullmatch(r"\d{8,}", text):
        return False
    if re.fullmatch(r"[\W_]+", text):
        return False
    if text.lower().endswith(IMAGE_EXTENSIONS):
        return False
    if re.fullmatch(r"[\w./-]+\.(?:jpg|jpeg|png|gif|webp|heic|mp4|mov)", text, re.IGNORECASE):
        return False
    if len(re.sub(r"[\W_]+", "", text)) < 8:
        return False
    return True


def _walk_texts(value: Any, parent_key: str = "") -> list[str]:
    texts: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            key_text = str(key).lower()
            if isinstance(child, str) and (key_text in PRIORITY_KEYS or _is_natural_text(child)):
                texts.append(child)
            else:
                texts.extend(_walk_texts(child, key_text))
    elif isinstance(value, list):
        for child in value:
            texts.extend(_walk_texts(child, parent_key))
    elif isinstance(value, str) and _is_natural_text(value):
        texts.append(value)
    return texts


class _FacebookHtmlTextParser(HTMLParser):
    """Extract visible text chunks from Facebook's HTML archive export."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._ignored_depth = 0
        self._section_depth = 0
        self._current_section: list[str] = []
        self._all_text: list[str] = []
        self.sections: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        if tag in IGNORED_HTML_TAGS:
            self._ignored_depth += 1
            return
        if self._ignored_depth:
            return
        if tag == "section":
            if self._section_depth == 0:
                self._current_section = []
            self._section_depth += 1
        if tag in BLOCK_HTML_TAGS:
            self._append(" ")

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag in IGNORED_HTML_TAGS and self._ignored_depth:
            self._ignored_depth -= 1
            return
        if self._ignored_depth:
            return
        if tag in BLOCK_HTML_TAGS:
            self._append(" ")
        if tag == "section" and self._section_depth:
            self._section_depth -= 1
            if self._section_depth == 0:
                section_text = _normalize_html_text(" ".join(self._current_section))
                if _is_natural_text(section_text):
                    self.sections.append(section_text)
                self._current_section = []

    def handle_data(self, data: str) -> None:
        if self._ignored_depth:
            return
        self._append(data)

    def _append(self, text: str) -> None:
        if not text:
            return
        self._all_text.append(text)
        if self._section_depth:
            self._current_section.append(text)

    @property
    def fallback_text(self) -> str:
        return _normalize_html_text(" ".join(self._all_text))


def _normalize_html_text(text: str) -> str:
    normalized = unescape(text)
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized.strip()


def _walk_html_texts(decoded_html: str) -> list[str]:
    parser = _FacebookHtmlTextParser()
    try:
        parser.feed(decoded_html)
        parser.close()
    except Exception:
        return []
    if parser.sections:
        return parser.sections
    fallback = parser.fallback_text
    return [fallback] if _is_natural_text(fallback) else []


def _open_archive(source: bytes | BinaryIO) -> zipfile.ZipFile:
    if isinstance(source, bytes):
        return zipfile.ZipFile(BytesIO(source))
    source.seek(0)
    return zipfile.ZipFile(source)


def extract_facebook_archive(payload: bytes | BinaryIO, *, include_messages: bool = False, max_items: int = 2000) -> FacebookArchiveResult:
    stats: Counter[str] = Counter()
    skipped_files: list[str] = []
    seen: set[str] = set()
    texts: list[ExtractedText] = []
    json_file_count = 0
    total_items = 0

    try:
        archive = _open_archive(payload)
    except zipfile.BadZipFile as error:
        raise FacebookImportError("Facebook ZIPを読み取れませんでした。FacebookのエクスポートZIPを、解凍せずそのまま選択してください。") from error

    with archive:
        import_infos = [
            info for info in archive.infolist()
            if info.filename.lower().endswith(IMPORT_EXTENSIONS) and not _should_skip(info.filename, include_messages)
        ]
        import_infos.sort(key=lambda item: (_path_priority(item.filename), item.filename))
        if not import_infos:
            raise FacebookImportError("Facebook ZIP内に読み取り対象のJSON/HTMLファイルが見つかりませんでした。FacebookのダウンロードZIPを確認してください。")

        for info in import_infos:
            if len(texts) >= max_items:
                break
            lower_filename = info.filename.lower()
            is_json = lower_filename.endswith(".json")
            is_html = lower_filename.endswith((".html", ".htm"))
            if is_json:
                json_file_count += 1
                stats["json_files_processed"] += 1
            elif is_html:
                stats["html_files_processed"] += 1
            if _is_message_path(info.filename):
                stats["message_files_processed"] += 1
            try:
                raw = archive.read(info)
                decoded = _decode_bytes(raw)
                if is_json:
                    data = json.loads(decoded)
                    raw_texts = _walk_texts(data)
                else:
                    raw_texts = _walk_html_texts(decoded)
            except Exception:
                if is_json:
                    stats["skipped_json_files"] += 1
                else:
                    stats["skipped_html_files"] += 1
                skipped_files.append(info.filename)
                continue

            total_items += len(raw_texts)
            for raw_text in raw_texts:
                if len(texts) >= max_items:
                    break
                if not _is_natural_text(raw_text):
                    continue
                sanitized, _, counts = sanitize_text_with_summary(_repair_facebook_text(raw_text))
                stats.update(counts)
                if not _is_natural_text(sanitized):
                    continue
                normalized = re.sub(r"\s+", " ", sanitized).strip()
                if normalized in seen:
                    stats["duplicate_texts_skipped"] += 1
                    continue
                seen.add(normalized)
                texts.append(
                    ExtractedText(
                        text=sanitized,
                        source_path=info.filename,
                        from_messages=_is_message_path(info.filename),
                    )
                )

    if json_file_count == 0 and stats["html_files_processed"] == 0:
        raise FacebookImportError("Facebook ZIP内にJSON/HTMLファイルが1件も見つかりませんでした。")
    if total_items == 0:
        raise FacebookImportError("Facebook ZIPから投稿テキストを抽出できませんでした。posts や comments_and_reactions が含まれているか確認してください。")
    if not texts:
        raise FacebookImportError("個人情報除去後にナレッジ候補へ使えるテキストが残りませんでした。max_itemsを増やすか、postsを含むZIPを選択してください。")

    if not include_messages:
        skipped_messages = [
            info.filename for info in archive.infolist()
            if info.filename.lower().endswith(IMPORT_EXTENSIONS) and _is_message_path(info.filename)
        ]
        stats["skipped_message_files"] += len(skipped_messages)

    return FacebookArchiveResult(
        texts=texts,
        total_items=total_items,
        sanitized_items=len(texts),
        stats=stats,
        skipped_files=skipped_files,
    )
