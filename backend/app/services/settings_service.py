from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

from ..config import get_openai_api_key, get_openai_model
from ..repositories import get_setting, set_setting


_runtime_openai_api_key: str | None = None
_runtime_typefully_api_key: str | None = None


@dataclass
class RuntimeSettings:
    openai_model: str = "gpt-5.5"
    default_platform: str = "threads"
    default_pr_disclosure: str = "#PR"
    brand_voice_summary: str = ""
    typefully_social_set_id: str | None = None
    typefully_default_schedule_mode: str = "draft_only"
    profile_note_url: str | None = None


def _read_saved_settings() -> dict[str, Any]:
    keys = [
        "openai_model",
        "default_platform",
        "default_pr_disclosure",
        "brand_voice_summary",
        "typefully_social_set_id",
        "typefully_default_schedule_mode",
        "profile_note_url",
    ]
    return {key: get_setting(key) for key in keys}


def _write_saved_settings(settings: dict[str, Any]) -> None:
    for key, value in settings.items():
        if key != "openai_api_key":
            set_setting(key, value)


def get_runtime_settings() -> RuntimeSettings:
    saved = _read_saved_settings()
    return RuntimeSettings(
        openai_model=saved.get("openai_model") or get_openai_model(),
        default_platform=saved.get("default_platform") or "threads",
        default_pr_disclosure=saved.get("default_pr_disclosure") or "#PR",
        brand_voice_summary=saved.get("brand_voice_summary") or "",
        typefully_social_set_id=saved.get("typefully_social_set_id") or os.getenv("TYPEFULLY_SOCIAL_SET_ID"),
        typefully_default_schedule_mode=saved.get("typefully_default_schedule_mode") or os.getenv("TYPEFULLY_DEFAULT_SCHEDULE_MODE") or "draft_only",
        profile_note_url=saved.get("profile_note_url") or os.getenv("PROFILE_NOTE_URL"),
    )


def get_effective_openai_api_key() -> str | None:
    return _runtime_openai_api_key or get_openai_api_key() or get_setting("openai_api_key")


def is_openai_api_key_set() -> bool:
    return bool(get_effective_openai_api_key())


def get_effective_typefully_api_key() -> str | None:
    return _runtime_typefully_api_key or os.getenv("TYPEFULLY_API_KEY") or get_setting("typefully_api_key")


def is_typefully_api_key_set() -> bool:
    return bool(get_effective_typefully_api_key())


def update_runtime_settings(payload: dict[str, Any]) -> dict[str, Any]:
    global _runtime_openai_api_key, _runtime_typefully_api_key

    if payload.get("openai_api_key"):
        _runtime_openai_api_key = payload["openai_api_key"]
        set_setting("openai_api_key", payload["openai_api_key"])

    if payload.get("typefully_api_key"):
        _runtime_typefully_api_key = payload["typefully_api_key"]
        set_setting("typefully_api_key", payload["typefully_api_key"])

    current = _read_saved_settings()
    for key in (
        "openai_model",
        "default_platform",
        "default_pr_disclosure",
        "brand_voice_summary",
        "typefully_social_set_id",
        "typefully_default_schedule_mode",
        "profile_note_url",
    ):
        if payload.get(key) is not None:
            current[key] = payload[key]
            if key == "openai_model":
                os.environ["OPENAI_MODEL"] = payload[key]

    _write_saved_settings(current)
    return settings_response()


def settings_response() -> dict[str, Any]:
    settings = get_runtime_settings()
    return {
        "openai_api_key_set": is_openai_api_key_set(),
        "openai_model": settings.openai_model,
        "default_platform": settings.default_platform,
        "default_pr_disclosure": settings.default_pr_disclosure,
        "brand_voice_summary": settings.brand_voice_summary,
        "typefully_api_key_set": is_typefully_api_key_set(),
        "typefully_social_set_id": settings.typefully_social_set_id,
        "typefully_default_schedule_mode": settings.typefully_default_schedule_mode,
        "profile_note_url": settings.profile_note_url,
    }
