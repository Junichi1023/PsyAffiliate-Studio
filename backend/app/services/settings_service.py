from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any

from ..config import get_openai_api_key, get_openai_model, get_settings_path


_runtime_openai_api_key: str | None = None


@dataclass
class RuntimeSettings:
    openai_model: str = "gpt-5.5"
    default_platform: str = "threads"
    default_pr_disclosure: str = "#PR"
    brand_voice_summary: str = ""


def _read_saved_settings() -> dict[str, Any]:
    path = get_settings_path()
    if not path.exists():
        return {}
    try:
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)
    except (json.JSONDecodeError, OSError):
        return {}


def _write_saved_settings(settings: dict[str, Any]) -> None:
    path = get_settings_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    safe_settings = {key: value for key, value in settings.items() if key != "openai_api_key"}
    with path.open("w", encoding="utf-8") as file:
        json.dump(safe_settings, file, ensure_ascii=False, indent=2)


def get_runtime_settings() -> RuntimeSettings:
    saved = _read_saved_settings()
    return RuntimeSettings(
        openai_model=saved.get("openai_model") or get_openai_model(),
        default_platform=saved.get("default_platform") or "threads",
        default_pr_disclosure=saved.get("default_pr_disclosure") or "#PR",
        brand_voice_summary=saved.get("brand_voice_summary") or "",
    )


def get_effective_openai_api_key() -> str | None:
    return _runtime_openai_api_key or get_openai_api_key()


def is_openai_api_key_set() -> bool:
    return bool(get_effective_openai_api_key())


def update_runtime_settings(payload: dict[str, Any]) -> dict[str, Any]:
    global _runtime_openai_api_key

    if payload.get("openai_api_key"):
        _runtime_openai_api_key = payload["openai_api_key"]

    current = _read_saved_settings()
    for key in ("openai_model", "default_platform", "default_pr_disclosure", "brand_voice_summary"):
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
    }
