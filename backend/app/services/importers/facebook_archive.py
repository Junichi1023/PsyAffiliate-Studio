from __future__ import annotations

import json
import re
import zipfile
from collections import Counter
from dataclasses import dataclass
from io import BytesIO
from pathlib import PurePosixPath
from typing import Any

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
    if not path.lower().endswith(".json"):
        return True
    if not include_messages and parts & MESSAGE_PARTS:
        return True
    return bool(parts & DEFAULT_EXCLUDED_PARTS)


def _path_priority(path: str) -> int:
    parts = _path_parts(path)
    if parts & {"posts"}:
        return 0
    if parts & {"comments_and_reactions", "likes_and_reactions"}:
        return 1
    if parts & {"profile_information"}:
        return 2
    if parts & {"photos_and_videos", "albums", "saved_items"}:
        return 3
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
    raise FacebookImportError("JSONファイルの文字コードを判別できませんでした") from last_error


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


def extract_facebook_archive(payload: bytes, *, include_messages: bool = False, max_items: int = 2000) -> FacebookArchiveResult:
    stats: Counter[str] = Counter()
    skipped_files: list[str] = []
    seen: set[str] = set()
    texts: list[ExtractedText] = []
    json_file_count = 0
    total_items = 0

    try:
        archive = zipfile.ZipFile(BytesIO(payload))
    except zipfile.BadZipFile as error:
        raise FacebookImportError("Facebook ZIPを読み取れませんでした。Facebookのエクスポート形式をJSONにして、ZIPファイルをそのまま選択してください。") from error

    with archive:
        json_infos = [
            info for info in archive.infolist()
            if info.filename.lower().endswith(".json") and not _should_skip(info.filename, include_messages)
        ]
        json_infos.sort(key=lambda item: (_path_priority(item.filename), item.filename))
        if not json_infos:
            raise FacebookImportError("Facebook ZIP内に読み取り対象のJSONファイルが見つかりませんでした。HTML形式ではなくJSON形式でダウンロードしてください。")

        for info in json_infos:
            if len(texts) >= max_items:
                break
            json_file_count += 1
            if _is_message_path(info.filename):
                stats["message_files_processed"] += 1
            try:
                raw = archive.read(info)
                decoded = _decode_bytes(raw)
                data = json.loads(decoded)
            except Exception:
                stats["skipped_json_files"] += 1
                skipped_files.append(info.filename)
                continue

            raw_texts = _walk_texts(data)
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

    if json_file_count == 0:
        raise FacebookImportError("Facebook ZIP内にJSONファイルが1件も見つかりませんでした。")
    if total_items == 0:
        raise FacebookImportError("Facebook ZIPから投稿テキストを抽出できませんでした。posts や comments_and_reactions が含まれているか確認してください。")
    if not texts:
        raise FacebookImportError("個人情報除去後にナレッジ候補へ使えるテキストが残りませんでした。max_itemsを増やすか、postsを含むZIPを選択してください。")

    if not include_messages:
        skipped_messages = [
            info.filename for info in archive.infolist()
            if info.filename.lower().endswith(".json") and _is_message_path(info.filename)
        ]
        stats["skipped_message_files"] += len(skipped_messages)

    return FacebookArchiveResult(
        texts=texts,
        total_items=total_items,
        sanitized_items=len(texts),
        stats=stats,
        skipped_files=skipped_files,
    )

