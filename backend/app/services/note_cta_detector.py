from __future__ import annotations


PROFILE_NOTE_PATTERNS = [
    "プロフィールのnote",
    "プロフのnote",
    "プロフィールにまとめています",
    "プロフにまとめています",
    "noteにまとめています",
    "プロフィールリンク",
    "下のリンク",
    "固定リンク",
    "詳しくはプロフィール",
    "プロフィールのリンク",
    "プロフリンク",
]


def detect_profile_note_cta(text: str) -> dict[str, object]:
    if not text:
        return {"detected": False, "matches": []}
    matches = [pattern for pattern in PROFILE_NOTE_PATTERNS if pattern in text]
    return {"detected": bool(matches), "matches": matches}

