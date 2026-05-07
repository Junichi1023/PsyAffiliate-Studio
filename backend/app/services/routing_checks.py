from __future__ import annotations

import re
from urllib.parse import urlparse


ASP_PATTERNS = [
    r"a8\.net",
    r"px\.a8\.net",
    r"af\.moshimo\.com",
    r"accesstrade\.net",
    r"valuecommerce\.com",
    r"rentracks\.jp",
]

PROFILE_NOTE_PATTERNS = [
    "プロフィールのnote",
    "プロフのnote",
    "プロフィールにまとめています",
    "プロフにまとめています",
    "noteにまとめています",
    "下のリンクにまとめています",
    "プロフィールリンク",
]


def _normalize_url(value: str) -> str:
    value = value.strip()
    if not value:
        return ""
    parsed = urlparse(value if "://" in value else f"https://{value}")
    host = parsed.netloc.lower().removeprefix("www.")
    path = parsed.path.rstrip("/")
    return f"{host}{path}"


def detect_direct_a8_link(text: str, registered_urls: list[str] | None = None) -> bool:
    if not text:
        return False
    lowered = text.lower()
    if any(re.search(pattern, lowered) for pattern in ASP_PATTERNS):
        return True
    for url in registered_urls or []:
        normalized = _normalize_url(url)
        if normalized and normalized in lowered:
            return True
        if url and url.lower() in lowered:
            return True
    return False


def detect_profile_note_cta(text: str) -> bool:
    if not text:
        return False
    return any(pattern in text for pattern in PROFILE_NOTE_PATTERNS)
