from __future__ import annotations

from typing import Any

from ...models import GenerateContentRequest
from ...repositories import list_products
from ..knowledge.search import get_profile_and_voice, search_knowledge
from ..settings_service import get_runtime_settings


def tone_label(tone: str) -> str:
    return {
        "empathy": "共感的",
        "practical": "実用的",
        "story": "ストーリー調",
        "educational": "教育的",
        "soft_sales": "控えめな販売導線",
    }.get(tone, tone)


def build_generation_context(request: GenerateContentRequest, product: dict[str, Any] | None) -> dict[str, Any]:
    profile_voice = get_profile_and_voice()
    relevant_knowledge = search_knowledge(
        f"{request.theme} {request.target_reader} psychology ai_prompt brand_voice prohibited_expression",
        limit=8,
    )
    settings = get_runtime_settings()
    return {
        "request": request.model_dump(),
        "profile": profile_voice.get("profile"),
        "brand_voice": profile_voice.get("brand_voice") or settings.brand_voice_summary,
        "prohibited_expressions": profile_voice.get("prohibited_expression"),
        "related_knowledge": relevant_knowledge,
        "selected_affiliate_product": product,
        "active_affiliate_products": list_products(active_only=True)[:5],
        "pr_disclosure_requirement": settings.default_pr_disclosure or "#PR",
        "must_follow": [
            "読者を騙してリンクを踏ませない",
            "PR表記を明示する",
            "医療的断定を避ける",
            "収益保証をしない",
            "不安を過度に煽らない",
            "読者に価値提供し、売り込み過多を避ける",
        ],
        "tone_label": tone_label(request.tone),
    }
