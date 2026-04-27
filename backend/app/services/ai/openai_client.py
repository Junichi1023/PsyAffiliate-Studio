from __future__ import annotations

import json
from typing import Any

from openai import OpenAI

from ...models import GenerateContentRequest
from ...repositories import get_product
from ..compliance import check_compliance
from ..settings_service import get_effective_openai_api_key, get_runtime_settings
from .prompt_builder import build_generation_context


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
        "empathy_score": {"type": ["integer", "null"], "minimum": 0, "maximum": 100},
        "empathy_notes": {"type": "array", "items": {"type": "string"}},
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
        "empathy_score",
        "empathy_notes",
        "suggested_hashtags",
    ],
}


def _fallback_generation(
    request: GenerateContentRequest,
    product: dict[str, Any] | None,
    reason: str,
) -> dict[str, Any]:
    pr = "#PR"
    product_line = ""
    if product:
        product_line = f"\n\n関連: {product['name']}\n{product.get('display_url') or product['affiliate_url']}"

    body = (
        "これはOPENAI_API_KEY未設定時のサンプル投稿です。"
        "AIと心理学を使って、今日できる小さな一歩を整理します。#PR\n\n"
        f"テーマ: {request.theme}\n"
        f"読者: {request.target_reader}"
        f"{product_line}"
    ).strip()
    caption = None
    if request.platform in ("instagram", "both"):
        caption = (
            f"{request.theme}について、今日から使える考え方をまとめました。\n"
            "無理に変えようとせず、行動を小さく分けて試してみてください。"
        )

    cta = "必要な人はプロフィールのリンクからどうぞ。"
    return {
        "platform": request.platform,
        "theme": request.theme,
        "body": body,
        "caption": caption,
        "cta": cta,
        "pr_disclosure": pr,
        "affiliate_product_id": product["id"] if product else None,
        "compliance_score": 90,
        "risk_notes": ["モック生成", "PR表記あり", reason],
        "empathy_score": 82,
        "empathy_notes": ["読者の不安を受け止めるモック生成です。", "今日できる小さな行動提案を含めています。"],
        "suggested_hashtags": ["#AI活用", "#心理学", "#PR"],
    }


def generate_content(request: GenerateContentRequest) -> dict[str, Any]:
    product = get_product(request.selected_product_id) if request.selected_product_id else None
    api_key = get_effective_openai_api_key()
    settings = get_runtime_settings()

    if not api_key:
        return _fallback_generation(request, product, "OPENAI_API_KEY 未設定のためテンプレート生成を返しました。")

    context = build_generation_context(request, product)
    client = OpenAI(api_key=api_key)
    instructions = (
        "あなたは占い、心理学、AI活用、アフィリエイト倫理に詳しいSNS編集者です。"
        "Threads/Instagram向けの投稿案をJSONだけで返してください。"
        "占いは断定予言ではなく、自己理解と行動整理の補助として扱います。"
        "PR表記、医療的断定の回避、誇大表現の回避、不安煽りと占い依存の回避、読者への価値提供を必ず守ります。"
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
    from ..empathy import check_empathy

    empathy = check_empathy(
        body=generated.get("body", ""),
        caption=generated.get("caption"),
        target_reader=request.target_reader,
        persona_pain_id=request.persona_pain_id,
    )
    generated["empathy_score"] = int(empathy["empathy_score"])
    generated["empathy_notes"] = list(empathy["notes"])
    merged_notes = list(generated.get("risk_notes") or [])
    for note in compliance["risk_notes"]:
        if note not in merged_notes:
            merged_notes.append(note)
    generated["risk_notes"] = merged_notes
    if product and not generated.get("affiliate_product_id"):
        generated["affiliate_product_id"] = product["id"]
    return generated
