from __future__ import annotations

import re
from collections import Counter


EMAIL_RE = re.compile(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}")
PHONE_RE = re.compile(r"(?:\+?\d[\d\-()\s]{8,}\d)")
URL_RE = re.compile(r"https?://[^\s]+|www\.[^\s]+", re.IGNORECASE)
POSTAL_CODE_RE = re.compile(r"\b\d{3}-\d{4}\b")
LONG_ID_RE = re.compile(r"\b\d{10,}\b")
CREDIT_CARD_LIKE_RE = re.compile(r"\b(?:\d[ -]?){13,16}\b")
USERNAME_RE = re.compile(r"(?<![\w.])@[A-Za-z0-9_.]{2,30}")
LINE_ID_RE = re.compile(r"(?:LINE\s*ID|ライン\s*ID|line\s*id)\s*[:：]?\s*[A-Za-z0-9_.-]+", re.IGNORECASE)
ADDRESS_LIKE_RE = re.compile(
    r"(?:北海道|青森県|岩手県|宮城県|秋田県|山形県|福島県|茨城県|栃木県|群馬県|埼玉県|千葉県|東京都|神奈川県|"
    r"新潟県|富山県|石川県|福井県|山梨県|長野県|岐阜県|静岡県|愛知県|三重県|滋賀県|京都府|大阪府|兵庫県|"
    r"奈良県|和歌山県|鳥取県|島根県|岡山県|広島県|山口県|徳島県|香川県|愛媛県|高知県|福岡県|佐賀県|"
    r"長崎県|熊本県|大分県|宮崎県|鹿児島県|沖縄県)[^\s、。]{2,40}"
)
NAME_LIKE_RE = re.compile(r"[\u3040-\u30ff\u3400-\u9fffA-Za-z]{2,12}(?:さん|ちゃん|君|くん)")

URL_LABELS = (
    ("facebook.com", "facebook_url_removed"),
    ("instagram.com", "instagram_url_removed"),
    ("twitter.com", "x_url_removed"),
    ("x.com", "x_url_removed"),
)


def _note_for_count(key: str) -> str:
    return {
        "email_removed": "メールアドレスを削除",
        "phone_removed": "電話番号を削除",
        "url_removed": "URLを削除",
        "facebook_url_removed": "Facebook URLを削除",
        "instagram_url_removed": "Instagram URLを削除",
        "x_url_removed": "X/Twitter URLを削除",
        "postal_code_removed": "郵便番号を削除",
        "long_id_removed": "長い数字IDを削除",
        "credit_card_like_removed": "カード番号風の数字列を削除",
        "username_removed": "@ユーザー名を削除",
        "line_id_removed": "LINE IDらしき表記を削除",
        "address_like_removed": "住所らしき表記を削除",
        "name_like_warning": "名前らしき表現あり。登録前に確認してください",
    }.get(key, key)


def _replace_url(match: re.Match[str], counts: Counter[str]) -> str:
    value = match.group(0).lower()
    if "note.com" not in value:
        counts["url_removed"] += 1
    for domain, key in URL_LABELS:
        if domain in value:
            counts[key] += 1
    return "[URL削除]"


def sanitize_text_with_summary(text: str) -> tuple[str, list[str], Counter[str]]:
    counts: Counter[str] = Counter()
    sanitized = text

    sanitized, email_count = EMAIL_RE.subn("[メールアドレス削除]", sanitized)
    counts["email_removed"] += email_count

    sanitized, line_count = LINE_ID_RE.subn("[LINE ID削除]", sanitized)
    counts["line_id_removed"] += line_count

    sanitized, url_count = URL_RE.subn(lambda match: _replace_url(match, counts), sanitized)
    if url_count:
        counts["url_removed"] += 0

    sanitized, postal_count = POSTAL_CODE_RE.subn("[郵便番号削除]", sanitized)
    counts["postal_code_removed"] += postal_count

    sanitized, credit_count = CREDIT_CARD_LIKE_RE.subn("[数字列削除]", sanitized)
    counts["credit_card_like_removed"] += credit_count

    sanitized, phone_count = PHONE_RE.subn("[電話番号削除]", sanitized)
    counts["phone_removed"] += phone_count

    sanitized, long_id_count = LONG_ID_RE.subn("[ID削除]", sanitized)
    counts["long_id_removed"] += long_id_count

    sanitized, username_count = USERNAME_RE.subn("[ユーザー名削除]", sanitized)
    counts["username_removed"] += username_count

    sanitized, address_count = ADDRESS_LIKE_RE.subn("[住所らしき表記削除]", sanitized)
    counts["address_like_removed"] += address_count

    name_warning_count = len(NAME_LIKE_RE.findall(sanitized))
    counts["name_like_warning"] += name_warning_count

    sanitized = re.sub(r"[ \t]+", " ", sanitized)
    sanitized = re.sub(r"\n{3,}", "\n\n", sanitized).strip()
    notes = [_note_for_count(key) for key, value in counts.items() if value > 0]
    return sanitized, notes, counts


def sanitize_text(text: str) -> tuple[str, list[str]]:
    sanitized, notes, _ = sanitize_text_with_summary(text)
    return sanitized, notes

