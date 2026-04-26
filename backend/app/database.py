from __future__ import annotations

import sqlite3
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

CREATE TABLE IF NOT EXISTS app_settings (
    key TEXT PRIMARY KEY,
    value TEXT,
    updated_at TEXT NOT NULL
);
"""


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


def row_to_dict(row: sqlite3.Row | None) -> dict[str, Any] | None:
    if row is None:
        return None
    return dict(row)
