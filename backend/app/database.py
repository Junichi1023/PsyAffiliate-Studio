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

CREATE TABLE IF NOT EXISTS import_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_type TEXT NOT NULL,
    source_name TEXT,
    status TEXT NOT NULL,
    total_items INTEGER DEFAULT 0,
    sanitized_items INTEGER DEFAULT 0,
    candidate_count INTEGER DEFAULT 0,
    redaction_summary TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS import_candidates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    category TEXT NOT NULL,
    content TEXT NOT NULL,
    source TEXT,
    confidence_score INTEGER DEFAULT 70,
    redaction_notes TEXT,
    selected INTEGER DEFAULT 1,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (session_id) REFERENCES import_sessions(id)
);

CREATE TABLE IF NOT EXISTS note_funnel_pages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    note_url TEXT NOT NULL,
    purpose TEXT,
    target_theme TEXT,
    target_reader TEXT,
    article_type TEXT,
    pr_disclosure TEXT DEFAULT '【PR】',
    status TEXT DEFAULT 'draft',
    memo TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS fortune_a8_offers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    offer_name TEXT NOT NULL,
    advertiser_name TEXT,
    service_type TEXT,
    affiliate_url TEXT,
    lp_url TEXT,
    reward_amount REAL,
    conversion_condition TEXT,
    rejection_conditions TEXT,
    first_time_bonus TEXT,
    consultation_genres TEXT,
    lp_impression TEXT,
    approval_rate TEXT,
    recommended_use TEXT,
    prohibited_claims TEXT,
    is_active INTEGER DEFAULT 1,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS threads_post_templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    template_type TEXT NOT NULL,
    target_theme TEXT,
    structure TEXT NOT NULL,
    example_post TEXT,
    cta_style TEXT,
    prohibited_patterns TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS typefully_schedule_jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    draft_id INTEGER NOT NULL,
    typefully_draft_id TEXT,
    social_set_id TEXT,
    scheduled_at TEXT,
    status TEXT DEFAULT 'created',
    schedule_mode TEXT DEFAULT 'draft_only',
    typefully_url TEXT,
    error_message TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (draft_id) REFERENCES content_drafts(id)
);

CREATE TABLE IF NOT EXISTS note_cta_templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    cta_type TEXT NOT NULL,
    text TEXT NOT NULL,
    target_note_page_id INTEGER,
    use_pr_disclosure INTEGER DEFAULT 1,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (target_note_page_id) REFERENCES note_funnel_pages(id)
);

CREATE TABLE IF NOT EXISTS threads_30day_plan_tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    day_number INTEGER NOT NULL,
    phase TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    status TEXT DEFAULT 'todo',
    created_at TEXT NOT NULL,
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
    "note_page_id": "INTEGER",
    "fortune_offer_id": "INTEGER",
    "threads_template_id": "INTEGER",
    "typefully_job_id": "INTEGER",
    "traffic_destination": "TEXT DEFAULT 'profile_note'",
    "direct_a8_link_detected": "INTEGER DEFAULT 0",
    "profile_note_cta_included": "INTEGER DEFAULT 0",
    "human_review_required": "INTEGER DEFAULT 1",
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

NOTE_FUNNEL_PAGE_SEEDS = [
    {
        "title": "【PR】電話占いを初めて使う前に知っておくこと",
        "note_url": "https://note.com/your_account/first-time-phone-fortune",
        "purpose": "電話占いを使う前の基本姿勢と注意点を伝える",
        "target_theme": "初めての電話占い",
        "target_reader": "恋愛相談をしたいが不安がある人",
        "article_type": "first_time_guide",
        "status": "idea",
    },
    {
        "title": "復縁相談で電話占いを使うときの質問例10個",
        "note_url": "https://note.com/your_account/reunion-question-examples",
        "purpose": "復縁相談前に聞きたいことを整理する",
        "target_theme": "復縁",
        "target_reader": "元彼・元カノとの関係に悩む人",
        "article_type": "question_examples",
        "status": "idea",
    },
    {
        "title": "電話占いで後悔しないための注意点",
        "note_url": "https://note.com/your_account/avoid-phone-fortune-mistakes",
        "purpose": "使いすぎや依存を避けるチェックポイントをまとめる",
        "target_theme": "電話占いの注意点",
        "target_reader": "不安が強く連続相談しがちな人",
        "article_type": "avoid_mistakes",
        "status": "idea",
    },
    {
        "title": "恋愛占いは当たる？依存しない使い方を解説",
        "note_url": "https://note.com/your_account/love-fortune-no-dependency",
        "purpose": "占いを答えではなく気持ち整理の補助として使う考え方を伝える",
        "target_theme": "恋愛占い",
        "target_reader": "相手の気持ちを知りたくて苦しい人",
        "article_type": "dependency_prevention",
        "status": "idea",
    },
    {
        "title": "電話占い・チャット占い・占いアプリの違い",
        "note_url": "https://note.com/your_account/fortune-service-comparison",
        "purpose": "相談スタイルごとの向き不向きを比較する",
        "target_theme": "占いサービス比較",
        "target_reader": "どの相談方法を選ぶか迷っている人",
        "article_type": "comparison",
        "status": "idea",
    },
]

THREADS_POST_TEMPLATE_SEEDS = [
    {
        "name": "恋愛悩みの共感投稿",
        "template_type": "empathy",
        "target_theme": "恋愛・復縁・片思い",
        "structure": "\n".join(
            [
                "1. 読者の悩みを短く言語化",
                "2. 決めつけずに両面を見せる",
                "3. 相手の気持ちより自分の気持ち整理へ戻す",
                "4. noteへ誘導しない投稿でも成立させる",
                "5. PR表記を入れる",
            ]
        ),
        "example_post": "【PR】\n\n「連絡が来ない＝脈なし」って決めつけると、\n本当はまだ余地がある関係まで自分で終わらせてしまうことがある。\n\nでも逆に、\n待ち続けるだけで苦しくなる恋もある。\n\n大事なのは、\n相手の気持ちを“当てる”ことより、\n自分がどうしたいかを整理すること。",
        "cta_style": "none_or_soft_profile_note",
        "prohibited_patterns": "必ず復縁できます\n彼の本音が全部わかる\n相手を思い通りにする",
    },
    {
        "name": "電話占い前のチェックリスト投稿",
        "template_type": "checklist",
        "target_theme": "電話占いの使い方",
        "structure": "\n".join(
            [
                "1. 電話占いを使う前の注意点を提示",
                "2. 箇条書きで保存しやすくする",
                "3. 占い依存を避ける",
                "4. 詳細はプロフィールのnoteへ誘導",
                "5. PR表記を入れる",
            ]
        ),
        "example_post": "【PR】\n\n電話占いを使う前に決めておくこと。\n\n・相談時間の上限\n・聞きたいことは3つまで\n・相手を変える相談ではなく、自分の行動を決める相談にする\n・不安な時に連続で使いすぎない\n・口コミより「相談ジャンルとの相性」を見る\n\nこれだけで失敗しにくくなる。",
        "cta_style": "profile_note",
        "prohibited_patterns": "今すぐ申し込まないと損\nこの占い師だけが本物",
    },
    {
        "name": "占いで失敗しない使い方投稿",
        "template_type": "avoid_mistake",
        "target_theme": "占いの注意点",
        "structure": "\n".join(
            [
                "1. 占いで失敗しやすい使い方を示す",
                "2. よい使い方を対比で示す",
                "3. 最後は自分で決めることを強調",
                "4. 必要ならプロフィールnoteへ誘導",
                "5. PR表記を入れる",
            ]
        ),
        "example_post": "【PR】\n\n占いで失敗しやすい人は、\n「答えをもらうため」に使ってしまう人。\n\nうまく使える人は、\n「自分の気持ちを整理するため」に使っている。\n\n復縁、片思い、結婚、仕事。\nどの悩みでも、最後に決めるのは自分。",
        "cta_style": "soft_profile_note",
        "prohibited_patterns": "100%当たる\n登録しないと不幸になる",
    },
]

NOTE_CTA_TEMPLATE_SEEDS = [
    {"name": "プロフィールnote案内", "cta_type": "profile_note", "text": "詳しくはプロフィールのnoteにまとめています。"},
    {"name": "質問リスト案内", "cta_type": "question_list", "text": "電話占いを使う前の質問リストは、プロフィールのnoteに置いています。"},
    {"name": "使いすぎ防止チェック", "cta_type": "checklist", "text": "不安な時に使いすぎないためのチェックリストを、noteにまとめています。"},
    {"name": "復縁相談前の整理", "cta_type": "caution", "text": "復縁や片思いで相談する前に、聞きたいことを3つに絞る方法をnoteにまとめています。"},
]

THREADS_30DAY_PLAN_SEEDS = [
    (1, "setup", "A8案件10〜20件リスト化", "1〜3日目: A8.netで電話占い・占いアプリ案件を10〜20件登録"),
    (4, "note", "比較noteを1本作る", "4〜7日目: 電話占い・占いアプリ比較のnote記事を1本作る"),
    (8, "posting", "Threads投稿を1日3本作成・予約", "8〜14日目: Threads投稿を1日3本作成しTypefullyへ予約"),
    (15, "note_expand", "反応が良いテーマでnoteを2本追加", "15〜21日目: 反応が良いテーマでnote記事を2本追加"),
    (22, "improve", "数字を見て投稿文とCTAを修正", "22〜30日目: A8クリック数・note閲覧数・Threads反応を見て改善"),
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
        _seed_note_funnel_pages(connection)
        _seed_threads_post_templates(connection)
        _seed_note_cta_templates(connection)
        _seed_threads_30day_plan(connection)


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


def _seed_note_funnel_pages(connection: sqlite3.Connection) -> None:
    now = datetime.now(timezone.utc).isoformat()
    for page in NOTE_FUNNEL_PAGE_SEEDS:
        exists = connection.execute("SELECT 1 FROM note_funnel_pages WHERE title = ?", (page["title"],)).fetchone()
        if exists:
            continue
        connection.execute(
            """
            INSERT INTO note_funnel_pages (
                title, note_url, purpose, target_theme, target_reader, article_type,
                pr_disclosure, status, memo, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                page["title"],
                page["note_url"],
                page.get("purpose"),
                page.get("target_theme"),
                page.get("target_reader"),
                page.get("article_type"),
                page.get("pr_disclosure", "【PR】"),
                page.get("status", "idea"),
                page.get("memo"),
                now,
                now,
            ),
        )


def _seed_threads_post_templates(connection: sqlite3.Connection) -> None:
    now = datetime.now(timezone.utc).isoformat()
    for template in THREADS_POST_TEMPLATE_SEEDS:
        exists = connection.execute("SELECT 1 FROM threads_post_templates WHERE name = ?", (template["name"],)).fetchone()
        if exists:
            continue
        connection.execute(
            """
            INSERT INTO threads_post_templates (
                name, template_type, target_theme, structure, example_post,
                cta_style, prohibited_patterns, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                template["name"],
                template["template_type"],
                template.get("target_theme"),
                template["structure"],
                template.get("example_post"),
                template.get("cta_style"),
                template.get("prohibited_patterns"),
                now,
                now,
            ),
        )


def _seed_note_cta_templates(connection: sqlite3.Connection) -> None:
    now = datetime.now(timezone.utc).isoformat()
    for cta in NOTE_CTA_TEMPLATE_SEEDS:
        exists = connection.execute("SELECT 1 FROM note_cta_templates WHERE name = ?", (cta["name"],)).fetchone()
        if exists:
            continue
        connection.execute(
            """
            INSERT INTO note_cta_templates (
                name, cta_type, text, target_note_page_id, use_pr_disclosure,
                created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                cta["name"],
                cta["cta_type"],
                cta["text"],
                cta.get("target_note_page_id"),
                cta.get("use_pr_disclosure", 1),
                now,
                now,
            ),
        )


def _seed_threads_30day_plan(connection: sqlite3.Connection) -> None:
    now = datetime.now(timezone.utc).isoformat()
    for day_number, phase, title, description in THREADS_30DAY_PLAN_SEEDS:
        exists = connection.execute(
            "SELECT 1 FROM threads_30day_plan_tasks WHERE day_number = ? AND phase = ?",
            (day_number, phase),
        ).fetchone()
        if exists:
            continue
        connection.execute(
            """
            INSERT INTO threads_30day_plan_tasks (
                day_number, phase, title, description, status, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (day_number, phase, title, description, "todo", now, now),
        )


def row_to_dict(row: sqlite3.Row | None) -> dict[str, Any] | None:
    if row is None:
        return None
    return dict(row)
