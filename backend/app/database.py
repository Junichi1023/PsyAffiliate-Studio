from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import get_db_path


SCHEMA = """
CREATE TABLE IF NOT EXISTS knowledge_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    category TEXT NOT NULL,
    content TEXT NOT NULL,
    source TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS affiliate_products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    asp_name TEXT,
    affiliate_url TEXT NOT NULL,
    display_url TEXT,
    category TEXT,
    target_pain TEXT,
    commission_type TEXT,
    commission_amount REAL,
    prohibited_claims TEXT,
    priority INTEGER DEFAULT 0,
    is_active INTEGER DEFAULT 1,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS content_drafts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    platform TEXT NOT NULL,
    theme TEXT NOT NULL,
    body TEXT NOT NULL,
    caption TEXT,
    cta TEXT,
    affiliate_product_id INTEGER,
    compliance_score INTEGER,
    risk_notes TEXT,
    status TEXT DEFAULT 'draft',
    scheduled_at TEXT,
    posted_at TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (affiliate_product_id) REFERENCES affiliate_products(id)
);

CREATE TABLE IF NOT EXISTS persona_pains (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    pain_summary TEXT NOT NULL,
    emotional_state TEXT,
    desired_future TEXT,
    forbidden_approach TEXT,
    recommended_tone TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS fortune_templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    fortune_type TEXT NOT NULL,
    target_pain_category TEXT,
    structure TEXT NOT NULL,
    example_output TEXT,
    prohibited_patterns TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS app_settings (
    key TEXT PRIMARY KEY,
    value TEXT,
    updated_at TEXT NOT NULL
);
"""

CONTENT_DRAFT_EXTRA_COLUMNS = {
    "fortune_type": "TEXT",
    "persona_pain_id": "INTEGER",
    "fortune_template_id": "INTEGER",
    "affiliate_intent": "TEXT",
    "empathy_score": "INTEGER",
    "empathy_notes": "TEXT",
    "publish_ready": "INTEGER DEFAULT 0",
    "publish_block_reason": "TEXT",
}

FORTUNE_TEMPLATE_SEEDS = [
    {
        "name": "金運の不安に寄り添う投稿",
        "fortune_type": "money_luck",
        "target_pain_category": "money",
        "structure": "\n".join(
            [
                "1. お金の不安を受け止める",
                "2. 今の金運の流れをやさしく表現する",
                "3. 一発逆転ではなく整える視点を出す",
                "4. 今日できる小さな行動を1つ提案する",
                "5. 関連商品がある場合だけ自然に紹介する",
                "6. #PRを明記する",
            ]
        ),
        "prohibited_patterns": "\n".join(
            ["必ずお金が入る", "金運が爆上がり", "買わないと損", "今すぐ買わないと運気が落ちる"]
        ),
    },
    {
        "name": "相手の気持ちに悩む人への投稿",
        "fortune_type": "love_luck",
        "target_pain_category": "love",
        "structure": "\n".join(
            [
                "1. 相手の気持ちがわからない不安を受け止める",
                "2. 断定せず、可能性として流れを伝える",
                "3. 相手を操作する方向にしない",
                "4. 読者自身の気持ちを確認する",
                "5. 自分を大切にする小さな行動を提案する",
                "6. #PRを明記する",
            ]
        ),
        "prohibited_patterns": "\n".join(["必ず復縁できる", "相手から連絡が来る", "相手を思い通りにする", "この方法で愛される"]),
    },
    {
        "name": "仕事と将来不安に寄り添う投稿",
        "fortune_type": "work_luck",
        "target_pain_category": "work",
        "structure": "\n".join(
            [
                "1. 仕事や将来への不安を受け止める",
                "2. 今の流れを整理する",
                "3. 向いている行動を小さく提案する",
                "4. 転職成功や収益を保証しない",
                "5. 学びや整理ツールとして商品を自然に紹介する",
                "6. #PRを明記する",
            ]
        ),
        "prohibited_patterns": "\n".join(["必ず転職成功", "絶対稼げる", "これだけで人生逆転", "誰でも簡単に成功"]),
    },
    {
        "name": "金運占い投稿テンプレート",
        "fortune_type": "money_luck",
        "target_pain_category": "money",
        "structure": "\n".join(
            [
                "1. 読者の不安を受け止める",
                "2. 今の金運の流れをやさしく表現する",
                "3. 注意点を恐怖訴求にしない",
                "4. 今日できる小さな行動を1つ示す",
                "5. 関連商品がある場合は自然に紹介する",
                "6. #PRを明記する",
            ]
        ),
        "prohibited_patterns": "\n".join(
            ["必ずお金が入る", "買わないと損", "今すぐ行動しないと金運が落ちる", "これで金運が爆上がり"]
        ),
    },
    {
        "name": "恋愛占い投稿テンプレート",
        "fortune_type": "love_luck",
        "target_pain_category": "love",
        "structure": "\n".join(
            [
                "1. 相手の気持ちで悩む読者に共感する",
                "2. 断定せず、可能性として表現する",
                "3. 読者自身の気持ちを確認する",
                "4. 相手を操作する方向に誘導しない",
                "5. 自分を大切にする行動を提案する",
                "6. #PRを明記する",
            ]
        ),
        "prohibited_patterns": "\n".join(["相手は必ず戻ってくる", "この方法で復縁できる", "相手を思い通りにする", "連絡させる"]),
    },
    {
        "name": "仕事運占い投稿テンプレート",
        "fortune_type": "work_luck",
        "target_pain_category": "work",
        "structure": "\n".join(
            [
                "1. 仕事や将来不安を受け止める",
                "2. 現在の流れを整理する",
                "3. 向いている行動を小さく提案する",
                "4. 収益保証・転職成功保証をしない",
                "5. 関連商品がある場合は学びや整理ツールとして紹介する",
                "6. #PRを明記する",
            ]
        ),
        "prohibited_patterns": "\n".join(["必ず転職成功", "絶対稼げる", "これだけで人生逆転", "誰でも簡単に成功"]),
    },
]


def get_connection() -> sqlite3.Connection:
    db_path = get_db_path()
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def init_db() -> None:
    with get_connection() as connection:
        connection.executescript(SCHEMA)
        _ensure_content_draft_columns(connection)
        _seed_fortune_templates(connection)


def _ensure_content_draft_columns(connection: sqlite3.Connection) -> None:
    existing = {
        row["name"]
        for row in connection.execute("PRAGMA table_info(content_drafts)").fetchall()
    }
    for column, definition in CONTENT_DRAFT_EXTRA_COLUMNS.items():
        if column not in existing:
            connection.execute(f"ALTER TABLE content_drafts ADD COLUMN {column} {definition}")


def _seed_fortune_templates(connection: sqlite3.Connection) -> None:
    now = datetime.now(timezone.utc).isoformat()
    for template in FORTUNE_TEMPLATE_SEEDS:
        exists = connection.execute(
            "SELECT 1 FROM fortune_templates WHERE name = ?", (template["name"],)
        ).fetchone()
        if exists:
            continue
        connection.execute(
            """
            INSERT INTO fortune_templates (
                name, fortune_type, target_pain_category, structure, example_output,
                prohibited_patterns, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                template["name"],
                template["fortune_type"],
                template["target_pain_category"],
                template["structure"],
                template.get("example_output"),
                template["prohibited_patterns"],
                now,
                now,
            ),
        )


def row_to_dict(row: sqlite3.Row | None) -> dict[str, Any] | None:
    if row is None:
        return None
    return dict(row)
