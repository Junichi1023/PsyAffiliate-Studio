from __future__ import annotations

from .facebook_archive import ExtractedText


LOVE_WORDS = ("恋", "復縁", "片思い", "連絡", "相手", "好き", "不安", "寂しい", "会いたい", "人間関係")
DAILY_WORDS = ("今日", "写真", "カフェ", "札幌", "友達", "家族", "仕事", "日常", "ありがとう", "嬉しい")
SOFT_WORDS = ("思う", "感じ", "少し", "たぶん", "かもしれない", "大切", "大事", "ありがたい", "落ち着く")
REFLECTION_WORDS = ("自分", "気持ち", "整理", "考える", "迷う", "選ぶ", "距離", "向き合う")


def _count_terms(texts: list[str], terms: tuple[str, ...]) -> int:
    joined = "\n".join(texts)
    return sum(joined.count(term) for term in terms)


def _inferred_phrase_guidance(summary: dict[str, int | list[str]]) -> list[str]:
    """Return synthetic guidance instead of copying Facebook text fragments."""
    guidance = [
        "実投稿の文をそのまま使わず、短くやわらかい一文から入る。",
        "断定よりも「かもしれない」「一度整理してみる」のような余白を残す。",
        "相手の気持ちを決めつけず、読者自身の気持ちに戻す。",
    ]
    if int(summary.get("daily_count", 0)) > 0:
        guidance.append("日常の小さな場面や体感を添えると、発信者らしさが出やすい。")
    if int(summary.get("reflection_count", 0)) > 0:
        guidance.append("最後は大きな決断ではなく、今日できる小さな確認に落とす。")
    return guidance


def _style_summary(texts: list[str]) -> dict[str, int | list[str]]:
    return {
        "love_count": _count_terms(texts, LOVE_WORDS),
        "daily_count": _count_terms(texts, DAILY_WORDS),
        "soft_count": _count_terms(texts, SOFT_WORDS),
        "reflection_count": _count_terms(texts, REFLECTION_WORDS),
    }


def _candidate(title: str, category: str, content: str, source: str, confidence: int, notes: list[str]) -> dict:
    return {
        "title": title,
        "category": category,
        "content": content.strip(),
        "source": source,
        "confidence_score": confidence,
        "redaction_notes": " / ".join(notes) if notes else "生投稿全文は保存せず、傾向だけに変換済み",
        "selected": True,
    }


def build_knowledge_candidates(texts: list[ExtractedText], filename: str) -> list[dict]:
    sanitized_texts = [item.text for item in texts]
    summary = _style_summary(sanitized_texts)
    message_note = "Messenger由来のテキストを含みます。登録前に個人情報を必ず確認してください" if any(item.from_messages for item in texts) else ""
    common_notes = ["生投稿全文は保存せず、複数投稿から要約化"]
    if message_note:
        common_notes.append(message_note)

    phrase_line = "実投稿をコピーしない言い換え方: " + " / ".join(_inferred_phrase_guidance(summary))

    source = f"facebook_import:{filename}"
    return [
        _candidate(
            "Facebookから抽出した自分らしい口調",
            "brand_voice",
            "\n".join(
                [
                    "過去投稿の傾向として、強く断定するよりも、少し迷いや体感を残しながら言葉にする口調が合う。",
                    "Threads投稿では「少し」「かもしれない」「大切」「気持ちを整理する」のような柔らかい表現を使うと自然。",
                    "恋愛・復縁・片思いの投稿でも、相手を決めつけず、読者が自分の気持ちを見直せる余白を残す。",
                    f"柔らかい表現の出現目安: {summary['soft_count']} / 気持ち整理系の出現目安: {summary['reflection_count']}",
                    phrase_line,
                ]
            ),
            source,
            84,
            common_notes,
        ),
        _candidate(
            "Facebookから見える価値観と発信者らしさ",
            "profile",
            "\n".join(
                [
                    "日常の小さな出来事、人との関わり、感謝や安心感を大切にする発信者像として扱う。",
                    "占い投稿では、正解を押しつけるより「一緒に整理する」「一度立ち止まる」方向が合う。",
                    "電話占い・占いアプリへの導線も、悩みを解決すると断定せず、相談前の準備や選び方を支える立ち位置にする。",
                    f"日常・人との関わり系の出現目安: {summary['daily_count']}",
                ]
            ),
            source,
            80,
            common_notes,
        ),
        _candidate(
            "Facebook由来のThreads冒頭フック候補",
            "threads_hook",
            "\n".join(
                [
                    "「連絡が来ないだけで、全部終わった気がしてしまう夜がある」",
                    "「相手の気持ちを知りたい時ほど、自分の本音が見えなくなることがある」",
                    "「復縁したい気持ちは、弱さではなく、それだけ大切だった証拠かもしれない」",
                    "「待つ恋が苦しい時は、相手を変える前に、自分の限界を言葉にしてみる」",
                    "保存されやすいよう、短文・余白・感情の言語化から入る。",
                ]
            ),
            source,
            82,
            common_notes,
        ),
        _candidate(
            "Facebook過去投稿から抽出した人間味ある表現",
            "past_post",
            "\n".join(
                [
                    "過去投稿の人間味は、特別な実績よりも、日常の感情を丁寧に拾うところにある。",
                    "投稿では、断定的な占い結果よりも「嬉しい」「ありがたい」「少し落ち着いた」のような体感語を混ぜると自然。",
                    "恋愛投稿では、相手の本音を当てに行くより、読者の苦しさを言語化してから小さな行動に戻す。",
                    phrase_line,
                ]
            ),
            source,
            78,
            common_notes,
        ),
        _candidate(
            "自然な会話口調を活かしたCTA",
            "cta_template",
            "\n".join(
                [
                    "詳しくはプロフィールのnoteにまとめています。",
                    "不安なまま占いを使いすぎないためのチェックリストは、プロフィールのnoteに置いています。",
                    "復縁や片思いで相談する前に、聞きたいことを3つに絞る方法をプロフィールのnoteにまとめています。",
                    "CTAは売り込みではなく、相談前に気持ちを整理したい人だけが読める案内にする。",
                ]
            ),
            source,
            81,
            common_notes,
        ),
        _candidate(
            "恋愛・人間関係投稿に使える寄り添い表現",
            "persona_pain",
            "\n".join(
                [
                    "連絡がない時に苦しいのは、相手の答えが見えないまま自分だけが考え続けてしまうから。",
                    "復縁したい気持ちを責めず、同時に待ち続けるつらさも置き去りにしない。",
                    "片思い・曖昧な関係では、相手を操作する表現を避け、自分が大切にしたい関係性へ戻す。",
                    "占いは当てるものではなく、気持ちを整理して次の一歩を選ぶ補助として扱う。",
                    f"恋愛・人間関係系の出現目安: {summary['love_count']}",
                ]
            ),
            source,
            83,
            common_notes,
        ),
    ]
