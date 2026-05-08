from __future__ import annotations

from .link_safety import detect_direct_affiliate_link
from .note_cta_detector import detect_profile_note_cta as detect_profile_note_cta_detail


def detect_direct_a8_link(text: str, registered_urls: list[str] | None = None) -> bool:
    return bool(detect_direct_affiliate_link(text, registered_urls)["detected"])


def detect_profile_note_cta(text: str) -> bool:
    return bool(detect_profile_note_cta_detail(text)["detected"])
