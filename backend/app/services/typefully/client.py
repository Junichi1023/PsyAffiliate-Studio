from __future__ import annotations

from typing import Any

import httpx

from ..settings_service import get_effective_typefully_api_key, get_runtime_settings


TYPEFULLY_BASE_URL = "https://api.typefully.com/v2"


def _posts_from_text(text: str) -> list[dict[str, str]]:
    parts = [part.strip() for part in text.split("\n---\n") if part.strip()]
    return [{"text": part} for part in parts] or [{"text": text.strip()}]


def _publish_at(schedule_mode: str, scheduled_at: str | None) -> str | None:
    if schedule_mode == "next_free_slot":
        return "next-free-slot"
    if schedule_mode == "scheduled_time":
        return scheduled_at
    return None


def create_or_schedule_threads_post(
    text: str,
    schedule_mode: str = "draft_only",
    scheduled_at: str | None = None,
) -> dict[str, Any]:
    settings = get_runtime_settings()
    api_key = get_effective_typefully_api_key()
    social_set_id = settings.typefully_social_set_id
    publish_at = _publish_at(schedule_mode, scheduled_at)
    payload: dict[str, Any] = {
        "platforms": {
            "threads": {
                "enabled": True,
                "posts": _posts_from_text(text),
            }
        }
    }
    if publish_at:
        payload["publish_at"] = publish_at

    if not api_key or not social_set_id:
        return {
            "mock": True,
            "ok": True,
            "typefully_draft_id": f"mock-{schedule_mode}",
            "social_set_id": social_set_id or "mock-social-set",
            "typefully_url": None,
            "payload": payload,
            "message": "TYPEFULLY_API_KEY または TYPEFULLY_SOCIAL_SET_ID 未設定のためmock予約として保存しました。",
        }

    url = f"{TYPEFULLY_BASE_URL}/social-sets/{social_set_id}/drafts"
    try:
        response = httpx.post(
            url,
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json=payload,
            timeout=20,
        )
        response.raise_for_status()
        data = response.json()
        draft_id = data.get("id") or data.get("draft_id") or data.get("typefully_draft_id")
        return {
            "mock": False,
            "ok": True,
            "typefully_draft_id": draft_id,
            "social_set_id": social_set_id,
            "typefully_url": data.get("url") or data.get("typefully_url"),
            "payload": payload,
            "response": data,
            "message": "Typefullyへ送信しました。",
        }
    except Exception as exc:
        return {
            "mock": False,
            "ok": False,
            "typefully_draft_id": None,
            "social_set_id": social_set_id,
            "typefully_url": None,
            "payload": payload,
            "error": str(exc),
            "message": "Typefully送信に失敗しました。",
        }
