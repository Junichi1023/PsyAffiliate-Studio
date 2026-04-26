from __future__ import annotations

from typing import Any

from ...models import GenerateContentRequest
from ...repositories import get_fortune_template, get_persona_pain, list_products
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
    selected_persona = get_persona_pain(request.persona_pain_id) if request.persona_pain_id else None
    selected_template = get_fortune_template(request.fortune_template_id) if request.fortune_template_id else None
    relevant_knowledge = search_knowledge(
        " ".join(
            [
                request.theme,
                request.target_reader,
                request.fortune_type or "",
                selected_persona.get("category", "") if selected_persona else "",
                "fortune_telling_method tarot_reading astrology numerology oracle_card",
                "money_luck love_luck work_luck relationship_worry spiritual_expression",
                "fortune_disclaimer affiliate_offer cta_template persona_pain threads_hook",
            ]
        ),
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
        "selected_persona_pain": selected_persona,
        "selected_fortune_template": selected_template,
        "active_affiliate_products": list_products(active_only=True)[:5],
        "fortune_type": request.fortune_type,
        "affiliate_intent": request.affiliate_intent,
        "pr_disclosure_requirement": settings.default_pr_disclosure or "#PR",
        "must_follow": [
            "読者を騙してリンクを踏ませない",
            "PR表記を明示する",
            "医療的断定を避ける",
            "収益保証をしない",
            "不安を過度に煽らない",
            "占いは断定予言ではなく、自己理解と行動整理の補助として扱う",
            "占い依存、霊感商法的な表現、買えば救われる表現を避ける",
            "商品導線は自然に、必要な人だけに案内する",
            "読者に価値提供し、売り込み過多を避ける",
        ],
        "tone_label": tone_label(request.tone),
    }
