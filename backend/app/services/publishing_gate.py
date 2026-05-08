from __future__ import annotations

from .link_safety import detect_direct_affiliate_link
from .note_cta_detector import detect_profile_note_cta


NG_TERMS = ("必ず復縁", "100%当たる", "彼の本音が全部わかる")


def validate_typefully_ready(draft: dict, registered_urls: list[str] | None = None) -> tuple[bool, list[str]]:
    text = "\n".join(str(part) for part in [draft.get("body"), draft.get("caption"), draft.get("cta")] if part)
    reasons: list[str] = []

    if draft.get("status") != "approved":
        reasons.append("承認済みではありません")
    if (draft.get("compliance_score") or 0) < 90:
        reasons.append("安全性スコアが90未満です")
    if (draft.get("empathy_score") or 0) < 75:
        reasons.append("寄り添いスコアが75未満です")

    link_result = detect_direct_affiliate_link(text, registered_urls)
    if draft.get("direct_a8_link_detected") or link_result["detected"]:
        reasons.append("A8直リンクらしきURLが含まれています")

    note_result = detect_profile_note_cta(text)
    if not draft.get("profile_note_cta_included") and not note_result["detected"]:
        reasons.append("プロフィールnoteへの導線がありません")

    if not draft.get("note_page_id"):
        reasons.append("誘導先note記事が設定されていません")

    for term in NG_TERMS:
        if term in text:
            reasons.append(f"禁止表現「{term}」が含まれています")

    return len(reasons) == 0, list(dict.fromkeys(reasons))


def evaluate_publish_ready(draft: dict, registered_urls: list[str] | None = None) -> dict[str, object]:
    ready, reasons = validate_typefully_ready(draft, registered_urls)
    return {
        "ready": ready,
        "reasons": reasons,
        "block_reason": None if ready else " / ".join(reasons),
    }

