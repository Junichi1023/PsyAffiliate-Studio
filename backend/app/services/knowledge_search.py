from __future__ import annotations

from typing import Any

from ..database import get_connection


def search_knowledge(query: str, limit: int = 8) -> list[dict[str, Any]]:
    terms = [term for term in query.replace("　", " ").split(" ") if term]
    if not terms:
        return []

    clauses = []
    params: list[str] = []
    for term in terms:
        like = f"%{term}%"
        clauses.append("(title LIKE ? OR category LIKE ? OR content LIKE ?)")
        params.extend([like, like, like])

    sql = f"""
        SELECT * FROM knowledge_items
        WHERE {" OR ".join(clauses)}
        ORDER BY updated_at DESC, id DESC
        LIMIT ?
    """
    params.append(str(limit))
    with get_connection() as connection:
        rows = connection.execute(sql, params).fetchall()
    return [dict(row) for row in rows]


def get_profile_and_voice() -> dict[str, str]:
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT category, content FROM knowledge_items
            WHERE category IN ('profile', 'brand_voice', 'prohibited_expression')
            ORDER BY updated_at DESC, id DESC
            """
        ).fetchall()
    result = {"profile": "", "brand_voice": "", "prohibited_expression": ""}
    for row in rows:
        key = row["category"]
        if not result[key]:
            result[key] = row["content"]
    return result
