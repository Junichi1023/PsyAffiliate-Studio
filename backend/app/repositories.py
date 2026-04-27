from __future__ import annotations

import csv
import io
from datetime import datetime, timezone
from typing import Any

from fastapi import HTTPException

from .database import get_connection, row_to_dict


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _bool_to_int(value: Any) -> Any:
    if isinstance(value, bool):
        return 1 if value else 0
    return value


def _normalize_product(row: dict[str, Any]) -> dict[str, Any]:
    row["is_active"] = bool(row.get("is_active"))
    return row


def _normalize_draft(row: dict[str, Any]) -> dict[str, Any]:
    row["publish_ready"] = bool(row.get("publish_ready"))
    return row


def _publish_evaluation(data: dict[str, Any]) -> tuple[int, str | None]:
    reasons: list[str] = []
    if data.get("status") != "approved":
        reasons.append("まだ承認済みではありません")
    if (data.get("compliance_score") or 0) < 90:
        reasons.append("安全性スコアが90未満です")
    if (data.get("empathy_score") or 0) < 75:
        reasons.append("寄り添いスコアが75未満です")
    if reasons:
        return 0, "; ".join(reasons)
    return 1, None


def list_knowledge() -> list[dict[str, Any]]:
    with get_connection() as connection:
        rows = connection.execute(
            "SELECT * FROM knowledge_items ORDER BY updated_at DESC, id DESC"
        ).fetchall()
    return [dict(row) for row in rows]


def get_knowledge(item_id: int) -> dict[str, Any]:
    with get_connection() as connection:
        row = connection.execute("SELECT * FROM knowledge_items WHERE id = ?", (item_id,)).fetchone()
    item = row_to_dict(row)
    if not item:
        raise HTTPException(status_code=404, detail="Knowledge item not found")
    return item


def create_knowledge(data: dict[str, Any]) -> dict[str, Any]:
    now = utc_now()
    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO knowledge_items (title, category, content, source, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (data["title"], data["category"], data["content"], data.get("source"), now, now),
        )
    return get_knowledge(cursor.lastrowid)


def update_knowledge(item_id: int, data: dict[str, Any]) -> dict[str, Any]:
    get_knowledge(item_id)
    updates = {key: value for key, value in data.items() if value is not None}
    if not updates:
        return get_knowledge(item_id)
    updates["updated_at"] = utc_now()
    set_clause = ", ".join(f"{key} = ?" for key in updates)
    values = list(updates.values()) + [item_id]
    with get_connection() as connection:
        connection.execute(f"UPDATE knowledge_items SET {set_clause} WHERE id = ?", values)
    return get_knowledge(item_id)


def delete_knowledge(item_id: int) -> None:
    get_knowledge(item_id)
    with get_connection() as connection:
        connection.execute("DELETE FROM knowledge_items WHERE id = ?", (item_id,))


def list_products(active_only: bool = False) -> list[dict[str, Any]]:
    where = "WHERE is_active = 1" if active_only else ""
    with get_connection() as connection:
        rows = connection.execute(
            f"SELECT * FROM affiliate_products {where} ORDER BY priority DESC, updated_at DESC, id DESC"
        ).fetchall()
    return [_normalize_product(dict(row)) for row in rows]


def get_product(product_id: int) -> dict[str, Any]:
    with get_connection() as connection:
        row = connection.execute("SELECT * FROM affiliate_products WHERE id = ?", (product_id,)).fetchone()
    product = row_to_dict(row)
    if not product:
        raise HTTPException(status_code=404, detail="Affiliate product not found")
    return _normalize_product(product)


def create_product(data: dict[str, Any]) -> dict[str, Any]:
    now = utc_now()
    payload = {key: _bool_to_int(value) for key, value in data.items()}
    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO affiliate_products (
                name, asp_name, affiliate_url, display_url, category, target_pain,
                commission_type, commission_amount, prohibited_claims, priority,
                is_active, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                payload["name"],
                payload.get("asp_name"),
                payload["affiliate_url"],
                payload.get("display_url"),
                payload.get("category"),
                payload.get("target_pain"),
                payload.get("commission_type"),
                payload.get("commission_amount"),
                payload.get("prohibited_claims"),
                payload.get("priority", 0),
                payload.get("is_active", 1),
                now,
                now,
            ),
        )
    return get_product(cursor.lastrowid)


def update_product(product_id: int, data: dict[str, Any]) -> dict[str, Any]:
    get_product(product_id)
    updates = {key: _bool_to_int(value) for key, value in data.items() if value is not None}
    if not updates:
        return get_product(product_id)
    updates["updated_at"] = utc_now()
    set_clause = ", ".join(f"{key} = ?" for key in updates)
    values = list(updates.values()) + [product_id]
    with get_connection() as connection:
        connection.execute(f"UPDATE affiliate_products SET {set_clause} WHERE id = ?", values)
    return get_product(product_id)


def delete_product(product_id: int) -> None:
    get_product(product_id)
    with get_connection() as connection:
        connection.execute("DELETE FROM affiliate_products WHERE id = ?", (product_id,))


def list_persona_pains() -> list[dict[str, Any]]:
    with get_connection() as connection:
        rows = connection.execute("SELECT * FROM persona_pains ORDER BY updated_at DESC, id DESC").fetchall()
    return [dict(row) for row in rows]


def get_persona_pain(persona_id: int) -> dict[str, Any]:
    with get_connection() as connection:
        row = connection.execute("SELECT * FROM persona_pains WHERE id = ?", (persona_id,)).fetchone()
    persona = row_to_dict(row)
    if not persona:
        raise HTTPException(status_code=404, detail="Persona pain not found")
    return persona


def create_persona_pain(data: dict[str, Any]) -> dict[str, Any]:
    now = utc_now()
    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO persona_pains (
                name, category, pain_summary, emotional_state, desired_future,
                forbidden_approach, recommended_tone, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data["name"],
                data["category"],
                data["pain_summary"],
                data.get("emotional_state"),
                data.get("desired_future"),
                data.get("forbidden_approach"),
                data.get("recommended_tone"),
                now,
                now,
            ),
        )
    return get_persona_pain(cursor.lastrowid)


def update_persona_pain(persona_id: int, data: dict[str, Any]) -> dict[str, Any]:
    get_persona_pain(persona_id)
    updates = {key: value for key, value in data.items() if value is not None}
    if not updates:
        return get_persona_pain(persona_id)
    updates["updated_at"] = utc_now()
    set_clause = ", ".join(f"{key} = ?" for key in updates)
    values = list(updates.values()) + [persona_id]
    with get_connection() as connection:
        connection.execute(f"UPDATE persona_pains SET {set_clause} WHERE id = ?", values)
    return get_persona_pain(persona_id)


def delete_persona_pain(persona_id: int) -> None:
    get_persona_pain(persona_id)
    with get_connection() as connection:
        connection.execute("DELETE FROM persona_pains WHERE id = ?", (persona_id,))


def list_fortune_templates() -> list[dict[str, Any]]:
    with get_connection() as connection:
        rows = connection.execute("SELECT * FROM fortune_templates ORDER BY updated_at DESC, id DESC").fetchall()
    return [dict(row) for row in rows]


def get_fortune_template(template_id: int) -> dict[str, Any]:
    with get_connection() as connection:
        row = connection.execute("SELECT * FROM fortune_templates WHERE id = ?", (template_id,)).fetchone()
    template = row_to_dict(row)
    if not template:
        raise HTTPException(status_code=404, detail="Fortune template not found")
    return template


def create_fortune_template(data: dict[str, Any]) -> dict[str, Any]:
    now = utc_now()
    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO fortune_templates (
                name, fortune_type, target_pain_category, structure,
                example_output, prohibited_patterns, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data["name"],
                data["fortune_type"],
                data.get("target_pain_category"),
                data["structure"],
                data.get("example_output"),
                data.get("prohibited_patterns"),
                now,
                now,
            ),
        )
    return get_fortune_template(cursor.lastrowid)


def update_fortune_template(template_id: int, data: dict[str, Any]) -> dict[str, Any]:
    get_fortune_template(template_id)
    updates = {key: value for key, value in data.items() if value is not None}
    if not updates:
        return get_fortune_template(template_id)
    updates["updated_at"] = utc_now()
    set_clause = ", ".join(f"{key} = ?" for key in updates)
    values = list(updates.values()) + [template_id]
    with get_connection() as connection:
        connection.execute(f"UPDATE fortune_templates SET {set_clause} WHERE id = ?", values)
    return get_fortune_template(template_id)


def delete_fortune_template(template_id: int) -> None:
    get_fortune_template(template_id)
    with get_connection() as connection:
        connection.execute("DELETE FROM fortune_templates WHERE id = ?", (template_id,))


def list_drafts() -> list[dict[str, Any]]:
    with get_connection() as connection:
        rows = connection.execute(
            "SELECT * FROM content_drafts ORDER BY created_at DESC, id DESC"
        ).fetchall()
    return [_normalize_draft(dict(row)) for row in rows]


def get_draft(draft_id: int) -> dict[str, Any]:
    with get_connection() as connection:
        row = connection.execute("SELECT * FROM content_drafts WHERE id = ?", (draft_id,)).fetchone()
    draft = row_to_dict(row)
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")
    return _normalize_draft(draft)


def create_draft(data: dict[str, Any]) -> dict[str, Any]:
    now = utc_now()
    data = dict(data)
    publish_ready, block_reason = _publish_evaluation(data)
    data["publish_ready"] = publish_ready
    data["publish_block_reason"] = block_reason
    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO content_drafts (
                platform, theme, body, caption, cta, affiliate_product_id,
                compliance_score, risk_notes, status, scheduled_at, posted_at,
                fortune_type, persona_pain_id, fortune_template_id, affiliate_intent,
                empathy_score, empathy_notes, publish_ready, publish_block_reason,
                created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data["platform"],
                data["theme"],
                data["body"],
                data.get("caption"),
                data.get("cta"),
                data.get("affiliate_product_id"),
                data.get("compliance_score"),
                data.get("risk_notes"),
                data.get("status", "draft"),
                data.get("scheduled_at"),
                data.get("posted_at"),
                data.get("fortune_type"),
                data.get("persona_pain_id"),
                data.get("fortune_template_id"),
                data.get("affiliate_intent") or "none",
                data.get("empathy_score"),
                data.get("empathy_notes"),
                data.get("publish_ready", 0),
                data.get("publish_block_reason"),
                now,
                now,
            ),
        )
    return get_draft(cursor.lastrowid)


def update_draft(draft_id: int, data: dict[str, Any]) -> dict[str, Any]:
    current = get_draft(draft_id)
    updates = {key: value for key, value in data.items() if value is not None}
    draft_for_evaluation = {**current, **updates}
    publish_ready, block_reason = _publish_evaluation(draft_for_evaluation)
    updates["publish_ready"] = publish_ready
    updates["publish_block_reason"] = block_reason
    if not updates:
        return get_draft(draft_id)
    updates["updated_at"] = utc_now()
    set_clause = ", ".join(f"{key} = ?" for key in updates)
    values = list(updates.values()) + [draft_id]
    with get_connection() as connection:
        connection.execute(f"UPDATE content_drafts SET {set_clause} WHERE id = ?", values)
    return get_draft(draft_id)


def delete_draft(draft_id: int) -> None:
    get_draft(draft_id)
    with get_connection() as connection:
        connection.execute("DELETE FROM content_drafts WHERE id = ?", (draft_id,))


def dashboard_stats() -> dict[str, Any]:
    today_prefix = datetime.now(timezone.utc).date().isoformat()
    with get_connection() as connection:
        knowledge_count = connection.execute("SELECT COUNT(*) FROM knowledge_items").fetchone()[0]
        affiliate_product_count = connection.execute("SELECT COUNT(*) FROM affiliate_products").fetchone()[0]
        persona_pain_count = connection.execute("SELECT COUNT(*) FROM persona_pains").fetchone()[0]
        fortune_template_count = connection.execute("SELECT COUNT(*) FROM fortune_templates").fetchone()[0]
        draft_count = connection.execute("SELECT COUNT(*) FROM content_drafts").fetchone()[0]
        today_drafts = connection.execute(
            "SELECT COUNT(*) FROM content_drafts WHERE created_at LIKE ?", (f"{today_prefix}%",)
        ).fetchone()[0]
        pending_review = connection.execute(
            "SELECT COUNT(*) FROM content_drafts WHERE status = 'needs_review'"
        ).fetchone()[0]
        publish_ready_count = connection.execute(
            "SELECT COUNT(*) FROM content_drafts WHERE publish_ready = 1"
        ).fetchone()[0]
        risky_draft_count = connection.execute(
            """
            SELECT COUNT(*) FROM content_drafts
            WHERE status = 'needs_review'
               OR COALESCE(compliance_score, 0) < 70
               OR COALESCE(empathy_score, 0) < 60
            """
        ).fetchone()[0]
        active_products = connection.execute(
            "SELECT COUNT(*) FROM affiliate_products WHERE is_active = 1"
        ).fetchone()[0]
        recent = connection.execute(
            "SELECT * FROM content_drafts ORDER BY created_at DESC, id DESC LIMIT 5"
        ).fetchall()
    return {
        "knowledge_count": knowledge_count,
        "affiliate_product_count": affiliate_product_count,
        "persona_pain_count": persona_pain_count,
        "fortune_template_count": fortune_template_count,
        "draft_count": draft_count,
        "today_drafts": today_drafts,
        "pending_review": pending_review,
        "publish_ready_count": publish_ready_count,
        "risky_draft_count": risky_draft_count,
        "active_products": active_products,
        "recent_drafts": [_normalize_draft(dict(row)) for row in recent],
    }


def drafts_to_csv() -> str:
    output = io.StringIO()
    fields = [
        "id",
        "platform",
        "theme",
        "body",
        "caption",
        "cta",
        "affiliate_product_id",
        "compliance_score",
        "risk_notes",
        "status",
        "scheduled_at",
        "posted_at",
        "fortune_type",
        "persona_pain_id",
        "fortune_template_id",
        "affiliate_intent",
        "empathy_score",
        "empathy_notes",
        "publish_ready",
        "publish_block_reason",
        "created_at",
        "updated_at",
    ]
    writer = csv.DictWriter(output, fieldnames=fields)
    writer.writeheader()
    for draft in list_drafts():
        writer.writerow({field: draft.get(field) for field in fields})
    return output.getvalue()


def get_setting(key: str) -> str | None:
    with get_connection() as connection:
        row = connection.execute("SELECT value FROM app_settings WHERE key = ?", (key,)).fetchone()
    if row is None:
        return None
    return row["value"]


def get_settings(keys: list[str]) -> dict[str, str | None]:
    return {key: get_setting(key) for key in keys}


def set_setting(key: str, value: str | None) -> None:
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO app_settings (key, value, updated_at)
            VALUES (?, ?, ?)
            ON CONFLICT(key) DO UPDATE SET value = excluded.value, updated_at = excluded.updated_at
            """,
            (key, value, utc_now()),
        )
