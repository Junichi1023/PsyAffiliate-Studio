from __future__ import annotations

from typing import Any

from ...models import GenerateContentRequest
from ...repositories import (
    get_fortune_a8_offer,
    get_fortune_template,
    get_note_cta_template,
    get_note_funnel_page,
    get_persona_pain,
    get_threads_post_template,
    list_products,
)
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
    selected_note_page = get_note_funnel_page(request.note_page_id) if request.note_page_id else None
    selected_threads_template = get_threads_post_template(request.threads_template_id) if request.threads_template_id else None
    selected_cta = get_note_cta_template(request.cta_template_id) if request.cta_template_id else None
    selected_fortune_offer = get_fortune_a8_offer(request.fortune_offer_id) if request.fortune_offer_id else None
    persona_category = selected_persona.get("category", "") if selected_persona else ""
    base_query = " ".join([request.theme, request.target_reader, request.fortune_type or "", persona_category])
    fortune_knowledge = search_knowledge(
        f"{base_query} fortune_telling_method tarot_reading astrology numerology oracle_card money_luck love_luck work_luck relationship_worry spiritual_expression",
        limit=8,
    )
    threads_hooks = search_knowledge(f"{request.theme} {persona_category} threads_hook", limit=5)
    cta_templates = search_knowledge(f"{request.theme} {request.affiliate_intent} cta_template affiliate_offer", limit=5)
    fortune_disclaimers = search_knowledge("fortune_disclaimer prohibited_expression", limit=5)
    facebook_voice = search_knowledge("facebook brand_voice threads_hook past_post cta_template persona_pain", limit=10)
    related_knowledge = search_knowledge(
        f"{base_query} fortune_disclaimer affiliate_offer cta_template persona_pain threads_hook prohibited_expression",
        limit=8,
    )
    settings = get_runtime_settings()
    return {
        "request": request.model_dump(),
        "profile": profile_voice.get("profile"),
        "brand_voice": profile_voice.get("brand_voice") or settings.brand_voice_summary,
        "prohibited_expressions": profile_voice.get("prohibited_expression"),
        "related_knowledge": related_knowledge,
        "fortune_knowledge": fortune_knowledge,
        "threads_hooks": threads_hooks,
        "cta_templates": cta_templates,
        "fortune_disclaimers": fortune_disclaimers,
        "facebook_imported_voice_knowledge": facebook_voice,
        "selected_affiliate_product": product,
        "selected_product_prohibited_claims": product.get("prohibited_claims") if product else None,
        "selected_persona_pain": selected_persona,
        "selected_fortune_template": selected_template,
        "selected_note_funnel_page": selected_note_page,
        "selected_threads_post_template": selected_threads_template,
        "selected_note_cta_template": selected_cta,
        "selected_fortune_a8_offer_for_note_only": selected_fortune_offer,
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
            "Threads本文にA8.net広告リンク、ASPリンク、登録済みaffiliate_urlを直接入れない",
            "note URLも原則本文に直貼りせず、プロフィールのnoteへ誘導する",
            "電話占い・占いアプリ案件はnote記事内で比較・注意点・質問例と一緒に紹介する",
            "復縁、片思い、音信不通、曖昧な関係、相手の気持ちを断定しない",
            "Facebook取り込み済みナレッジがある場合は、brand_voice、threads_hook、past_post、cta_templateを優先して自分らしい言葉に寄せる",
        ],
        "ideal_post_structure": [
            "読者の感情を受け止める",
            "恋愛・復縁・片思いの悩みをやさしく言語化する",
            "断定ではなく可能性として表現する",
            "相手を当てるより、自分の気持ちを整理する方向へ戻す",
            "必要な場合だけプロフィールのnoteへ自然に誘導する",
            f"{settings.default_pr_disclosure or '【PR】'} を冒頭または本文内に明記する",
        ],
        "recommended_safe_phrases": [
            "復縁について整理したい人向け",
            "相談の参考にしたい人向け",
            "相手の気持ちを考えるヒントになる",
            "不安を一人で抱え込まない選択肢",
            "選び方・相性の見極め方を紹介",
            "占いを依存せず使う方法",
            "相談前に聞きたいことを整理する",
        ],
        "tone_label": tone_label(request.tone),
    }
