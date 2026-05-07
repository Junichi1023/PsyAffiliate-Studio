from __future__ import annotations

import json
import re
import zipfile
from io import BytesIO
from typing import Any


EMAIL_RE = re.compile(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}")
PHONE_RE = re.compile(r"(?:\+?\d[\d\-()\s]{8,}\d)")
URL_RE = re.compile(r"https?://\S+")

SKIP_PATH_KEYWORDS = ("message", "messenger", "inbox", "chat", "security", "ads")
TEXT_KEYS = {"text", "title", "description", "caption", "post", "content", "message"}


def sanitize_text(text: str) -> tuple[str, list[str]]:
    notes: list[str] = []
    sanitized = EMAIL_RE.sub("[メールアドレス削除]", text)
    if sanitized != text:
        notes.append("メールアドレスを削除")
    text = sanitized
    sanitized = PHONE_RE.sub("[電話番号削除]", text)
    if sanitized != text:
        notes.append("電話番号を削除")
    text = sanitized
    sanitized = URL_RE.sub("[URL削除]", text)
    if sanitized != text:
        notes.append("URLを削除")
    return sanitized.strip(), notes


def _walk_json(value: Any) -> list[str]:
    texts: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            if key in TEXT_KEYS and isinstance(child, str):
                texts.append(child)
            else:
                texts.extend(_walk_json(child))
    elif isinstance(value, list):
        for child in value:
            texts.extend(_walk_json(child))
    return texts


def _category_for_text(text: str, index: int) -> str:
    if any(word in text for word in ("恋", "好き", "連絡", "復縁", "片思い", "人間関係")):
        return "persona_pain"
    if any(word in text for word in ("思う", "大事", "大切", "感じ", "自分")):
        return "brand_voice"
    if index % 3 == 0:
        return "threads_hook"
    return "past_post"


def build_candidates_from_facebook_zip(filename: str, payload: bytes, limit: int = 40) -> dict[str, Any]:
    total_items = 0
    candidates: list[dict[str, Any]] = []
    redaction_counts: dict[str, int] = {}

    with zipfile.ZipFile(BytesIO(payload)) as archive:
        for info in archive.infolist():
            path = info.filename.lower()
            if not path.endswith(".json") or any(keyword in path for keyword in SKIP_PATH_KEYWORDS):
                continue
            try:
                data = json.loads(archive.read(info).decode("utf-8"))
            except Exception:
                continue
            for raw_text in _walk_json(data):
                total_items += 1
                if not raw_text or len(raw_text.strip()) < 24:
                    continue
                sanitized, notes = sanitize_text(raw_text)
                if len(sanitized) < 24:
                    continue
                for note in notes:
                    redaction_counts[note] = redaction_counts.get(note, 0) + 1
                category = _category_for_text(sanitized, len(candidates))
                candidates.append(
                    {
                        "title": f"Facebook由来ナレッジ候補 {len(candidates) + 1}",
                        "category": category,
                        "content": sanitized[:1600],
                        "source": f"facebook:{filename}:{info.filename}",
                        "confidence_score": 78 if category in {"brand_voice", "threads_hook"} else 70,
                        "redaction_notes": "、".join(notes) if notes else "個人情報の明確なパターンなし",
                        "selected": True,
                    }
                )
                if len(candidates) >= limit:
                    break
            if len(candidates) >= limit:
                break

    redaction_summary = " / ".join(f"{key}: {value}" for key, value in redaction_counts.items()) or "PIIパターン検出なし"
    return {
        "total_items": total_items,
        "candidates": candidates,
        "redaction_summary": redaction_summary,
    }
