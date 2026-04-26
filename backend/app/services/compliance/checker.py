from __future__ import annotations

import re

from ...repositories import get_product


DANGEROUS_TERMS = [
    "治る",
    "必ず改善",
    "絶対",
    "確実に稼げる",
    "医師不要",
    "薬に頼らない",
    "誰でも簡単に稼げる",
    "これだけで人生が変わる",
    "放置すると手遅れ",
    "今すぐ買わないと損",
]

PR_PATTERNS = [
    r"#PR\b",
    r"＃PR\b",
    r"PR\s*投稿",
    r"アフィリエイトリンクを含みます",
    r"広告を含みます",
]

MEDICAL_ASSERTION_TERMS = ["完治", "診断不要", "治療不要", "薬をやめられる", "病院に行かなくていい"]
MEDICAL_AD_PATTERNS = [
    r"うつ.{0,8}治る",
    r"うつ.{0,8}改善",
    r"不安障害.{0,8}治る",
    r"不安障害.{0,8}改善",
    r"適応障害.{0,8}治る",
    r"パニック障害.{0,8}改善",
]
INCOME_GUARANTEE_TERMS = ["月収保証", "収益保証", "必ず稼げる", "損しない"]
ANXIETY_PRESSURE_TERMS = ["今すぐやらないと手遅れ", "知らないと危険", "人生終了", "取り返しがつかない"]


def _split_claims(text: str | None) -> list[str]:
    if not text:
        return []
    return [item.strip() for item in re.split(r"[\n,、]+", text) if item.strip()]


def _risk_level(score: int) -> str:
    if score >= 90:
        return "低リスク"
    if score >= 70:
        return "要軽微修正"
    if score >= 40:
        return "要レビュー"
    return "投稿禁止推奨"


def _recommendation(score: int) -> str:
    if score >= 90:
        return "このまま投稿候補にできます。"
    if score >= 70:
        return "軽微な表現修正後に承認してください。"
    if score >= 40:
        return "人間のレビューを必須にしてください。"
    return "投稿を止め、内容を作り直してください。"


def _suggested_fix(score: int, has_pr_disclosure: bool, flagged_terms: list[str]) -> str:
    suggestions: list[str] = []
    if flagged_terms:
        suggestions.append("断定・保証・過度な不安訴求を、体験や選択肢を示す表現に弱めてください。")
    if not has_pr_disclosure:
        suggestions.append("#PR または「アフィリエイトリンクを含みます」を明記してください。")
    if score < 40:
        suggestions.append("投稿前提ではなく、構成から作り直してください。")
    if not suggestions:
        suggestions.append("現状の主要リスクは低いですが、公開前に人間が文脈を確認してください。")
    return " ".join(suggestions)


def check_compliance(
    body: str,
    caption: str | None = None,
    cta: str | None = None,
    affiliate_product_id: int | None = None,
    prohibited_claims: str | None = None,
) -> dict[str, object]:
    text = "\n".join(part for part in [body, caption or "", cta or ""] if part)
    flagged_terms: list[str] = []
    risk_notes: list[str] = []
    score = 100

    for term in DANGEROUS_TERMS:
        if term in text:
            flagged_terms.append(term)
            risk_notes.append(f"危険表現「{term}」を検出しました。")
            score -= 15

    for term in MEDICAL_ASSERTION_TERMS:
        if term in text:
            flagged_terms.append(term)
            risk_notes.append(f"医療的断定につながる表現「{term}」があります。")
            score -= 20

    for pattern in MEDICAL_AD_PATTERNS:
        if re.search(pattern, text):
            flagged_terms.append(pattern)
            risk_notes.append("医療広告的な効果断定に見える表現があります。")
            score -= 22

    for term in INCOME_GUARANTEE_TERMS:
        if term in text:
            flagged_terms.append(term)
            risk_notes.append(f"収益保証につながる表現「{term}」があります。")
            score -= 20

    for term in ANXIETY_PRESSURE_TERMS:
        if term in text:
            flagged_terms.append(term)
            risk_notes.append(f"不安を過度に煽る表現「{term}」があります。")
            score -= 12

    has_pr_disclosure = any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in PR_PATTERNS)

    product_claims = prohibited_claims
    if affiliate_product_id:
        try:
            product = get_product(affiliate_product_id)
            product_claims = product_claims or product.get("prohibited_claims")
        except Exception:
            risk_notes.append("紐づくアフィリエイト商品を確認できませんでした。")
            score -= 8

        if not has_pr_disclosure:
            risk_notes.append("#PR または「アフィリエイトリンクを含みます」の表記が必要です。")
            score -= 25

    for claim in _split_claims(product_claims):
        if claim and claim in text:
            flagged_terms.append(claim)
            risk_notes.append(f"商品の禁止訴求「{claim}」に触れています。")
            score -= 18

    if "不安" in text and ("買" in text or "申込" in text):
        risk_notes.append("不安訴求と購入導線が近いため、煽りすぎていないか確認してください。")
        score -= 8

    if not risk_notes:
        risk_notes.append("PR・医療的断定・誇大表現の主要チェックを通過しました。")

    final_score = max(0, min(100, score))
    return {
        "compliance_score": final_score,
        "risk_level": _risk_level(final_score),
        "has_pr_disclosure": has_pr_disclosure,
        "flagged_terms": sorted(set(flagged_terms)),
        "risk_notes": risk_notes,
        "suggested_fix": _suggested_fix(final_score, has_pr_disclosure, flagged_terms),
        "recommendation": _recommendation(final_score),
    }
