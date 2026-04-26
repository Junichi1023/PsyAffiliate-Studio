from __future__ import annotations

from ..repositories import get_persona_pain


EMOTION_WORDS = ["不安", "つらい", "怖い", "迷う", "焦る", "苦しい", "心配", "悩む", "しんどい"]
ACK_WORDS = ["大丈夫", "わかります", "自然です", "責めなくていい", "無理しなくていい", "不安ですよね", "つらいですよね"]
BLAME_WORDS = ["あなたが悪い", "努力不足", "甘え", "自己責任", "だからダメ"]
FEAR_WORDS = ["手遅れ", "不幸になる", "損", "危険", "終わり", "取り返しがつかない"]
DEPENDENCY_WORDS = ["毎日占いを見ないと", "占いだけを信じて", "これだけ信じて", "依存", "救われる"]
PREDICTION_WORDS = ["必ず", "絶対", "100%", "確実", "運命は決まっています"]
SMALL_ACTION_WORDS = ["今日", "ひとつ", "1つ", "小さく", "少し", "メモ", "書き出", "深呼吸", "確認"]
AFFILIATE_WORDS = ["#PR", "アフィリエイトリンク", "プロフィール", "リンク", "必要な人"]
FORCED_PURCHASE_WORDS = ["買えば救われる", "買わないと", "今すぐ買", "購入しないと"]


def _contains_any(text: str, words: list[str]) -> bool:
    return any(word in text for word in words)


def _risk_level(score: int) -> str:
    if score >= 80:
        return "良好"
    if score >= 60:
        return "要軽微修正"
    if score >= 40:
        return "要レビュー"
    return "投稿非推奨"


def check_empathy(
    body: str,
    caption: str | None = None,
    target_reader: str | None = None,
    persona_pain_id: int | None = None,
) -> dict[str, object]:
    text = "\n".join(part for part in [body, caption or "", target_reader or ""] if part)
    persona = None
    if persona_pain_id:
        try:
            persona = get_persona_pain(persona_pain_id)
            text = "\n".join(
                [
                    text,
                    persona.get("pain_summary") or "",
                    persona.get("emotional_state") or "",
                    persona.get("forbidden_approach") or "",
                ]
            )
        except Exception:
            persona = None

    checks = {
        "acknowledges_emotion": _contains_any(text, EMOTION_WORDS) or _contains_any(body, ACK_WORDS),
        "avoids_blame": not _contains_any(body, BLAME_WORDS),
        "avoids_fear_pressure": not _contains_any(body, FEAR_WORDS),
        "avoids_dependency": not _contains_any(body, DEPENDENCY_WORDS),
        "avoids_deterministic_prediction": not _contains_any(body, PREDICTION_WORDS),
        "has_small_action": _contains_any(body, SMALL_ACTION_WORDS),
        "affiliate_cta_is_natural": ("#PR" not in body and "リンク" not in body) or (
            _contains_any(body, AFFILIATE_WORDS) and not _contains_any(body, FORCED_PURCHASE_WORDS)
        ),
        "avoids_buy_to_be_saved": not _contains_any(body, FORCED_PURCHASE_WORDS),
    }

    score = 100
    notes: list[str] = []
    penalties = {
        "acknowledges_emotion": 18,
        "avoids_blame": 18,
        "avoids_fear_pressure": 18,
        "avoids_dependency": 14,
        "avoids_deterministic_prediction": 14,
        "has_small_action": 12,
        "affiliate_cta_is_natural": 10,
        "avoids_buy_to_be_saved": 16,
    }

    positive_notes = {
        "acknowledges_emotion": "読者の不安や迷いを受け止めています。",
        "avoids_blame": "読者を責める表現は目立ちません。",
        "avoids_fear_pressure": "恐怖で急かす表現は抑えられています。",
        "avoids_dependency": "占い依存を促す表現は目立ちません。",
        "avoids_deterministic_prediction": "断定予言を避けています。",
        "has_small_action": "行動提案が小さく現実的です。",
        "affiliate_cta_is_natural": "アフィリエイト導線は比較的自然です。",
        "avoids_buy_to_be_saved": "購入すれば救われるという表現はありません。",
    }
    negative_notes = {
        "acknowledges_emotion": "冒頭で読者の感情をもう少し受け止めてください。",
        "avoids_blame": "読者を責める印象の表現があります。",
        "avoids_fear_pressure": "不安や恐怖を煽る表現があります。",
        "avoids_dependency": "占い依存につながる表現があります。",
        "avoids_deterministic_prediction": "断定予言に見える表現があります。",
        "has_small_action": "今日できる小さな行動提案を追加してください。",
        "affiliate_cta_is_natural": "商品導線が唐突または強すぎます。",
        "avoids_buy_to_be_saved": "買えば救われる印象を弱めてください。",
    }

    for key, ok in checks.items():
        if ok:
            notes.append(positive_notes[key])
        else:
            score -= penalties[key]
            notes.append(negative_notes[key])

    if persona and persona.get("forbidden_approach") and persona["forbidden_approach"] in body:
        score -= 12
        notes.append("選択ペルソナの避けるべき接し方に触れています。")

    final_score = max(0, min(100, score))
    suggested_fix = " ".join(note for key, note in negative_notes.items() if not checks[key])
    if not suggested_fix:
        suggested_fix = "公開前に文脈を確認し、必要な人だけに届く導線に整えてください。"

    return {
        "empathy_score": final_score,
        "risk_level": _risk_level(final_score),
        "checks": checks,
        "notes": notes,
        "suggested_fix": suggested_fix,
    }
