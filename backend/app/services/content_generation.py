from __future__ import annotations

import json
from typing import Any

from openai import OpenAI

from ..models import GenerateContentRequest
from ..repositories import get_product, list_products
from .compliance import check_compliance
from .knowledge_search import get_profile_and_voice, search_knowledge
from .settings_service import get_effective_openai_api_key, get_runtime_settings


OUTPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "platform": {"type": "string", "enum": ["threads", "instagram", "both"]},
        "theme": {"type": "string"},
        "body": {"type": "string"},
        "caption": {"type": ["string", "null"]},
        "cta": {"type": "string"},
        "pr_disclosure": {"type": "string"},
        "affiliate_product_id": {"type": ["integer", "null"]},
        "compliance_score": {"type": "integer", "minimum": 0, "maximum": 100},
        "risk_notes": {"type": "array", "items": {"type": "string"}},
        "suggested_hashtags": {"type": "array", "items": {"type": "string"}},
    },
    "required": [
        "platform",
        "theme",
        "body",
        "caption",
        "cta",
        "pr_disclosure",
        "affiliate_product_id",
        "compliance_score",
        "risk_notes",
        "suggested_hashtags",
    ],
}


def _tone_label(tone: str) -> str:
    return {
        "empathy": "共感的",
        "practical": "実用的",
        "story": "ストーリー調",
        "educational": "教育的",
        "soft_sales": "控えめな販売導線",
    }.get(tone, tone)


def _fallback_generation(
    request: GenerateContentRequest,
    product: dict[str, Any] | None,
    reason: str,
) -> dict[str, Any]:
    pr = "#PR" if product else ""
    product_line = ""
    if product:
        product_line = f"\n\n{pr} 関連: {product['name']}\n{product.get('display_url') or product['affiliate_url']}"

    body = (
        f"{request.theme}\n\n"
        f"{request.target_reader}に向けて、まずは小さく試せる視点を整理します。\n"
        "心理学の知見は万能薬ではありませんが、自分の反応を観察する助けになります。\n"
        "AIは判断を代わりにするものではなく、選択肢を言語化する相棒として使うのが安全です。"
        f"{product_line}"
    ).strip()
    caption = None
    if request.platform in ("instagram", "both"):
        caption = (
            f"{request.theme}について、今日から使える考え方をまとめました。\n"
            "無理に変えようとせず、行動を小さく分けて試してみてください。"
        )

    cta = "必要な人はプロフィールのリンクから確認してください。" if product else "あとで見返せるよう保存しておいてください。"
    compliance = check_compliance(
        body=body,
        caption=caption,
        cta=cta,
        affiliate_product_id=product["id"] if product else None,
        prohibited_claims=product.get("prohibited_claims") if product else None,
    )
    notes = [str(note) for note in compliance["risk_notes"]]
    notes.append(reason)
    return {
        "platform": request.platform,
        "theme": request.theme,
        "body": body,
        "caption": caption,
        "cta": cta,
        "pr_disclosure": pr or "#PR",
        "affiliate_product_id": product["id"] if product else None,
        "compliance_score": int(compliance["compliance_score"]),
        "risk_notes": notes,
        "suggested_hashtags": ["#AI活用", "#心理学"] + (["#PR"] if product else []),
    }


def _build_context(request: GenerateContentRequest, product: dict[str, Any] | None) -> dict[str, Any]:
    profile_voice = get_profile_and_voice()
    relevant_knowledge = search_knowledge(
        f"{request.theme} {request.target_reader} psychology ai_prompt brand_voice prohibited_expression",
        limit=8,
    )
    active_products = list_products(active_only=True)
    settings = get_runtime_settings()
    return {
        "request": request.model_dump(),
        "profile": profile_voice.get("profile"),
        "brand_voice": profile_voice.get("brand_voice") or settings.brand_voice_summary,
        "prohibited_expressions": profile_voice.get("prohibited_expression"),
        "related_knowledge": relevant_knowledge,
        "selected_affiliate_product": product,
        "active_affiliate_products": active_products[:5],
        "pr_disclosure_requirement": settings.default_pr_disclosure or "#PR",
        "must_follow": [
            "読者を騙してリンクを踏ませない",
            "PR表記を明示する",
            "医療的断定を避ける",
            "収益保証をしない",
            "不安を過度に煽らない",
            "読者に価値提供し、売り込み過多を避ける",
        ],
        "tone_label": _tone_label(request.tone),
    }


def generate_content(request: GenerateContentRequest) -> dict[str, Any]:
    product = get_product(request.selected_product_id) if request.selected_product_id else None
    api_key = get_effective_openai_api_key()
    settings = get_runtime_settings()

    if not api_key:
        return _fallback_generation(request, product, "OPENAI_API_KEY 未設定のためテンプレート生成を返しました。")

    context = _build_context(request, product)
    client = OpenAI(api_key=api_key)
    instructions = (
        "あなたは心理学、AI活用、アフィリエイト倫理に詳しいSNS編集者です。"
        "Threads/Instagram向けの投稿案をJSONだけで返してください。"
        "PR表記、医療的断定の回避、誇大表現の回避、読者への価値提供を必ず守ります。"
    )

    try:
        response = client.responses.create(
            model=settings.openai_model,
            reasoning={"effort": "medium"},
            text={
                "verbosity": "medium",
                "format": {
                    "type": "json_schema",
                    "name": "psy_affiliate_generated_content",
                    "schema": OUTPUT_SCHEMA,
                    "strict": True,
                },
            },
            input=[
                {"role": "system", "content": instructions},
                {"role": "user", "content": json.dumps(context, ensure_ascii=False)},
            ],
        )
        raw = response.output_text
        generated = json.loads(raw)
    except Exception as exc:
        return _fallback_generation(request, product, f"OpenAI生成に失敗したためテンプレート生成に切り替えました: {exc}")

    compliance = check_compliance(
        body=generated.get("body", ""),
        caption=generated.get("caption"),
        cta=generated.get("cta"),
        affiliate_product_id=generated.get("affiliate_product_id") or (product["id"] if product else None),
        prohibited_claims=product.get("prohibited_claims") if product else None,
    )
    generated["compliance_score"] = int(compliance["compliance_score"])
    merged_notes = list(generated.get("risk_notes") or [])
    for note in compliance["risk_notes"]:
        if note not in merged_notes:
            merged_notes.append(note)
    generated["risk_notes"] = merged_notes
    if product and not generated.get("affiliate_product_id"):
        generated["affiliate_product_id"] = product["id"]
    return generated
