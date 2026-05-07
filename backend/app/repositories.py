from __future__ import annotations

import csv
import io
from datetime import datetime, timezone
from typing import Any

from fastapi import HTTPException

from .database import get_connection, row_to_dict
from .services.routing_checks import detect_direct_a8_link, detect_profile_note_cta


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
    row["direct_a8_link_detected"] = bool(row.get("direct_a8_link_detected"))
    row["profile_note_cta_included"] = bool(row.get("profile_note_cta_included"))
    row["human_review_required"] = bool(row.get("human_review_required", 1))
    return row


def _normalize_bool_fields(row: dict[str, Any], fields: tuple[str, ...]) -> dict[str, Any]:
    for field in fields:
        if field in row:
            row[field] = bool(row.get(field))
    return row


def _registered_affiliate_urls() -> list[str]:
    urls: list[str] = []
    with get_connection() as connection:
        for table, column in (("affiliate_products", "affiliate_url"), ("fortune_a8_offers", "affiliate_url")):
            rows = connection.execute(f"SELECT {column} FROM {table} WHERE {column} IS NOT NULL").fetchall()
            urls.extend(row[column] for row in rows if row[column])
    return urls


def _draft_text(data: dict[str, Any]) -> str:
    return "\n".join(str(part) for part in [data.get("body"), data.get("caption"), data.get("cta")] if part)


def _apply_draft_route_checks(data: dict[str, Any]) -> dict[str, Any]:
    text = _draft_text(data)
    data["direct_a8_link_detected"] = 1 if detect_direct_a8_link(text, _registered_affiliate_urls()) else 0
    data["profile_note_cta_included"] = 1 if detect_profile_note_cta(text) else 0
    data["traffic_destination"] = data.get("traffic_destination") or "profile_note"
    data["human_review_required"] = 1 if data.get("human_review_required", True) else 0
    return data


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
    data = _apply_draft_route_checks(data)
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
                note_page_id, fortune_offer_id, threads_template_id, typefully_job_id,
                traffic_destination, direct_a8_link_detected, profile_note_cta_included,
                human_review_required,
                created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                data.get("note_page_id"),
                data.get("fortune_offer_id"),
                data.get("threads_template_id"),
                data.get("typefully_job_id"),
                data.get("traffic_destination") or "profile_note",
                data.get("direct_a8_link_detected", 0),
                data.get("profile_note_cta_included", 0),
                data.get("human_review_required", 1),
                now,
                now,
            ),
        )
    return get_draft(cursor.lastrowid)


def update_draft(draft_id: int, data: dict[str, Any]) -> dict[str, Any]:
    current = get_draft(draft_id)
    updates = {key: value for key, value in data.items() if value is not None}
    draft_for_evaluation = {**current, **updates}
    draft_for_evaluation = _apply_draft_route_checks(draft_for_evaluation)
    updates["direct_a8_link_detected"] = draft_for_evaluation["direct_a8_link_detected"]
    updates["profile_note_cta_included"] = draft_for_evaluation["profile_note_cta_included"]
    updates["traffic_destination"] = draft_for_evaluation["traffic_destination"]
    updates["human_review_required"] = draft_for_evaluation["human_review_required"]
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
        today_scheduled_count = connection.execute(
            "SELECT COUNT(*) FROM typefully_schedule_jobs WHERE scheduled_at LIKE ?", (f"{today_prefix}%",)
        ).fetchone()[0]
        typefully_waiting_count = connection.execute(
            "SELECT COUNT(*) FROM typefully_schedule_jobs WHERE status IN ('created', 'scheduled')"
        ).fetchone()[0]
        note_missing_draft_count = connection.execute(
            "SELECT COUNT(*) FROM content_drafts WHERE note_page_id IS NULL"
        ).fetchone()[0]
        a8_link_detected_count = connection.execute(
            "SELECT COUNT(*) FROM content_drafts WHERE direct_a8_link_detected = 1"
        ).fetchone()[0]
        facebook_candidate_count = connection.execute(
            "SELECT COUNT(*) FROM import_candidates WHERE selected = 1"
        ).fetchone()[0]
        plan_done_count = connection.execute(
            "SELECT COUNT(*) FROM threads_30day_plan_tasks WHERE status = 'done'"
        ).fetchone()[0]
        plan_total_count = connection.execute("SELECT COUNT(*) FROM threads_30day_plan_tasks").fetchone()[0]
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
        "today_scheduled_count": today_scheduled_count,
        "typefully_waiting_count": typefully_waiting_count,
        "note_missing_draft_count": note_missing_draft_count,
        "a8_link_detected_count": a8_link_detected_count,
        "facebook_candidate_count": facebook_candidate_count,
        "plan_done_count": plan_done_count,
        "plan_total_count": plan_total_count,
        "weekly_post_type_distribution": {
            "恋愛・復縁の共感投稿": 40,
            "占いの使い方・注意点": 25,
            "質問例・チェックリスト": 20,
            "記事誘導": 10,
            "自分の考え・体験談": 5,
        },
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
        "note_page_id",
        "fortune_offer_id",
        "threads_template_id",
        "typefully_job_id",
        "traffic_destination",
        "direct_a8_link_detected",
        "profile_note_cta_included",
        "human_review_required",
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


RESOURCE_COLUMNS: dict[str, tuple[str, ...]] = {
    "note_funnel_pages": (
        "title",
        "note_url",
        "purpose",
        "target_theme",
        "target_reader",
        "article_type",
        "pr_disclosure",
        "status",
        "memo",
    ),
    "fortune_a8_offers": (
        "offer_name",
        "advertiser_name",
        "service_type",
        "affiliate_url",
        "lp_url",
        "reward_amount",
        "conversion_condition",
        "rejection_conditions",
        "first_time_bonus",
        "consultation_genres",
        "lp_impression",
        "approval_rate",
        "recommended_use",
        "prohibited_claims",
        "is_active",
    ),
    "threads_post_templates": (
        "name",
        "template_type",
        "target_theme",
        "structure",
        "example_post",
        "cta_style",
        "prohibited_patterns",
    ),
    "note_cta_templates": (
        "name",
        "cta_type",
        "text",
        "target_note_page_id",
        "use_pr_disclosure",
    ),
}

RESOURCE_BOOL_FIELDS = {
    "fortune_a8_offers": ("is_active",),
    "note_cta_templates": ("use_pr_disclosure",),
}


def _resource_not_found(table: str) -> HTTPException:
    return HTTPException(status_code=404, detail=f"{table} item not found")


def _normalize_resource(table: str, row: dict[str, Any]) -> dict[str, Any]:
    return _normalize_bool_fields(row, RESOURCE_BOOL_FIELDS.get(table, ()))


def list_resource(table: str) -> list[dict[str, Any]]:
    if table not in RESOURCE_COLUMNS:
        raise ValueError(f"Unsupported resource table: {table}")
    with get_connection() as connection:
        rows = connection.execute(f"SELECT * FROM {table} ORDER BY updated_at DESC, id DESC").fetchall()
    return [_normalize_resource(table, dict(row)) for row in rows]


def get_resource(table: str, item_id: int) -> dict[str, Any]:
    if table not in RESOURCE_COLUMNS:
        raise ValueError(f"Unsupported resource table: {table}")
    with get_connection() as connection:
        row = connection.execute(f"SELECT * FROM {table} WHERE id = ?", (item_id,)).fetchone()
    item = row_to_dict(row)
    if not item:
        raise _resource_not_found(table)
    return _normalize_resource(table, item)


def create_resource(table: str, data: dict[str, Any]) -> dict[str, Any]:
    columns = RESOURCE_COLUMNS[table]
    now = utc_now()
    payload = {key: _bool_to_int(value) for key, value in data.items() if key in columns}
    names = list(payload.keys()) + ["created_at", "updated_at"]
    placeholders = ", ".join("?" for _ in names)
    values = [payload.get(name) for name in payload] + [now, now]
    with get_connection() as connection:
        cursor = connection.execute(
            f"INSERT INTO {table} ({', '.join(names)}) VALUES ({placeholders})",
            values,
        )
    return get_resource(table, cursor.lastrowid)


def update_resource(table: str, item_id: int, data: dict[str, Any]) -> dict[str, Any]:
    get_resource(table, item_id)
    columns = RESOURCE_COLUMNS[table]
    updates = {
        key: _bool_to_int(value)
        for key, value in data.items()
        if key in columns and value is not None
    }
    if not updates:
        return get_resource(table, item_id)
    updates["updated_at"] = utc_now()
    set_clause = ", ".join(f"{key} = ?" for key in updates)
    values = list(updates.values()) + [item_id]
    with get_connection() as connection:
        connection.execute(f"UPDATE {table} SET {set_clause} WHERE id = ?", values)
    return get_resource(table, item_id)


def delete_resource(table: str, item_id: int) -> None:
    get_resource(table, item_id)
    with get_connection() as connection:
        connection.execute(f"DELETE FROM {table} WHERE id = ?", (item_id,))


def list_note_funnel_pages() -> list[dict[str, Any]]:
    return list_resource("note_funnel_pages")


def get_note_funnel_page(item_id: int) -> dict[str, Any]:
    return get_resource("note_funnel_pages", item_id)


def create_note_funnel_page(data: dict[str, Any]) -> dict[str, Any]:
    return create_resource("note_funnel_pages", data)


def update_note_funnel_page(item_id: int, data: dict[str, Any]) -> dict[str, Any]:
    return update_resource("note_funnel_pages", item_id, data)


def delete_note_funnel_page(item_id: int) -> None:
    delete_resource("note_funnel_pages", item_id)


def list_fortune_a8_offers() -> list[dict[str, Any]]:
    return list_resource("fortune_a8_offers")


def get_fortune_a8_offer(item_id: int) -> dict[str, Any]:
    return get_resource("fortune_a8_offers", item_id)


def create_fortune_a8_offer(data: dict[str, Any]) -> dict[str, Any]:
    return create_resource("fortune_a8_offers", data)


def update_fortune_a8_offer(item_id: int, data: dict[str, Any]) -> dict[str, Any]:
    return update_resource("fortune_a8_offers", item_id, data)


def delete_fortune_a8_offer(item_id: int) -> None:
    delete_resource("fortune_a8_offers", item_id)


def list_threads_post_templates() -> list[dict[str, Any]]:
    return list_resource("threads_post_templates")


def get_threads_post_template(item_id: int) -> dict[str, Any]:
    return get_resource("threads_post_templates", item_id)


def create_threads_post_template(data: dict[str, Any]) -> dict[str, Any]:
    return create_resource("threads_post_templates", data)


def update_threads_post_template(item_id: int, data: dict[str, Any]) -> dict[str, Any]:
    return update_resource("threads_post_templates", item_id, data)


def delete_threads_post_template(item_id: int) -> None:
    delete_resource("threads_post_templates", item_id)


def list_note_cta_templates() -> list[dict[str, Any]]:
    return list_resource("note_cta_templates")


def get_note_cta_template(item_id: int) -> dict[str, Any]:
    return get_resource("note_cta_templates", item_id)


def create_note_cta_template(data: dict[str, Any]) -> dict[str, Any]:
    return create_resource("note_cta_templates", data)


def update_note_cta_template(item_id: int, data: dict[str, Any]) -> dict[str, Any]:
    return update_resource("note_cta_templates", item_id, data)


def delete_note_cta_template(item_id: int) -> None:
    delete_resource("note_cta_templates", item_id)


def list_threads_30day_plan() -> list[dict[str, Any]]:
    with get_connection() as connection:
        rows = connection.execute(
            "SELECT * FROM threads_30day_plan_tasks ORDER BY day_number ASC, id ASC"
        ).fetchall()
    return [dict(row) for row in rows]


def update_threads_30day_plan_task(item_id: int, data: dict[str, Any]) -> dict[str, Any]:
    with get_connection() as connection:
        row = connection.execute("SELECT * FROM threads_30day_plan_tasks WHERE id = ?", (item_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="30日運用プランが見つかりません")
    updates = {key: value for key, value in data.items() if key in {"status", "title", "description"} and value is not None}
    if not updates:
        return dict(row)
    updates["updated_at"] = utc_now()
    set_clause = ", ".join(f"{key} = ?" for key in updates)
    values = list(updates.values()) + [item_id]
    with get_connection() as connection:
        connection.execute(f"UPDATE threads_30day_plan_tasks SET {set_clause} WHERE id = ?", values)
        updated = connection.execute("SELECT * FROM threads_30day_plan_tasks WHERE id = ?", (item_id,)).fetchone()
    return dict(updated)


def create_import_session(source_name: str | None, total_items: int, candidates: list[dict[str, Any]], redaction_summary: str) -> dict[str, Any]:
    now = utc_now()
    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO import_sessions (
                source_type, source_name, status, total_items, sanitized_items,
                candidate_count, redaction_summary, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            ("facebook", source_name, "preview", total_items, len(candidates), len(candidates), redaction_summary, now, now),
        )
        session_id = cursor.lastrowid
        for candidate in candidates:
            connection.execute(
                """
                INSERT INTO import_candidates (
                    session_id, title, category, content, source, confidence_score,
                    redaction_notes, selected, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    session_id,
                    candidate["title"],
                    candidate["category"],
                    candidate["content"],
                    candidate.get("source"),
                    candidate.get("confidence_score", 70),
                    candidate.get("redaction_notes"),
                    1 if candidate.get("selected", True) else 0,
                    now,
                    now,
                ),
            )
    return get_import_session(session_id)


def list_import_sessions() -> list[dict[str, Any]]:
    with get_connection() as connection:
        rows = connection.execute("SELECT * FROM import_sessions ORDER BY created_at DESC, id DESC").fetchall()
    return [dict(row) for row in rows]


def get_import_session(session_id: int) -> dict[str, Any]:
    with get_connection() as connection:
        row = connection.execute("SELECT * FROM import_sessions WHERE id = ?", (session_id,)).fetchone()
    session = row_to_dict(row)
    if not session:
        raise HTTPException(status_code=404, detail="取り込みセッションが見つかりません")
    return session


def list_import_candidates(session_id: int) -> list[dict[str, Any]]:
    get_import_session(session_id)
    with get_connection() as connection:
        rows = connection.execute(
            "SELECT * FROM import_candidates WHERE session_id = ? ORDER BY id ASC",
            (session_id,),
        ).fetchall()
    return [_normalize_bool_fields(dict(row), ("selected",)) for row in rows]


def update_import_candidate(candidate_id: int, data: dict[str, Any]) -> dict[str, Any]:
    with get_connection() as connection:
        row = connection.execute("SELECT * FROM import_candidates WHERE id = ?", (candidate_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="候補が見つかりません")
    updates = {
        key: _bool_to_int(value)
        for key, value in data.items()
        if key in {"title", "category", "content", "source", "confidence_score", "redaction_notes", "selected"} and value is not None
    }
    if not updates:
        return _normalize_bool_fields(dict(row), ("selected",))
    updates["updated_at"] = utc_now()
    set_clause = ", ".join(f"{key} = ?" for key in updates)
    values = list(updates.values()) + [candidate_id]
    with get_connection() as connection:
        connection.execute(f"UPDATE import_candidates SET {set_clause} WHERE id = ?", values)
        updated = connection.execute("SELECT * FROM import_candidates WHERE id = ?", (candidate_id,)).fetchone()
    return _normalize_bool_fields(dict(updated), ("selected",))


def commit_import_session(session_id: int) -> list[dict[str, Any]]:
    candidates = [candidate for candidate in list_import_candidates(session_id) if candidate.get("selected")]
    created: list[dict[str, Any]] = []
    for candidate in candidates:
        created.append(
            create_knowledge(
                {
                    "title": candidate["title"],
                    "category": candidate["category"],
                    "content": candidate["content"],
                    "source": candidate.get("source") or f"facebook_import:{session_id}",
                }
            )
        )
    with get_connection() as connection:
        connection.execute(
            "UPDATE import_sessions SET status = ?, updated_at = ? WHERE id = ?",
            ("committed", utc_now(), session_id),
        )
    return created


def list_typefully_jobs() -> list[dict[str, Any]]:
    with get_connection() as connection:
        rows = connection.execute(
            "SELECT * FROM typefully_schedule_jobs ORDER BY created_at DESC, id DESC"
        ).fetchall()
    return [dict(row) for row in rows]


def get_typefully_job(job_id: int) -> dict[str, Any]:
    with get_connection() as connection:
        row = connection.execute("SELECT * FROM typefully_schedule_jobs WHERE id = ?", (job_id,)).fetchone()
    job = row_to_dict(row)
    if not job:
        raise HTTPException(status_code=404, detail="Typefully予約ジョブが見つかりません")
    return job


def create_typefully_job(data: dict[str, Any]) -> dict[str, Any]:
    now = utc_now()
    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO typefully_schedule_jobs (
                draft_id, typefully_draft_id, social_set_id, scheduled_at, status,
                schedule_mode, typefully_url, error_message, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data["draft_id"],
                data.get("typefully_draft_id"),
                data.get("social_set_id"),
                data.get("scheduled_at"),
                data.get("status", "created"),
                data.get("schedule_mode", "draft_only"),
                data.get("typefully_url"),
                data.get("error_message"),
                now,
                now,
            ),
        )
    return get_typefully_job(cursor.lastrowid)


def update_typefully_job(job_id: int, data: dict[str, Any]) -> dict[str, Any]:
    get_typefully_job(job_id)
    allowed = {"typefully_draft_id", "social_set_id", "scheduled_at", "status", "schedule_mode", "typefully_url", "error_message"}
    updates = {key: value for key, value in data.items() if key in allowed and value is not None}
    if not updates:
        return get_typefully_job(job_id)
    updates["updated_at"] = utc_now()
    set_clause = ", ".join(f"{key} = ?" for key in updates)
    values = list(updates.values()) + [job_id]
    with get_connection() as connection:
        connection.execute(f"UPDATE typefully_schedule_jobs SET {set_clause} WHERE id = ?", values)
    return get_typefully_job(job_id)
