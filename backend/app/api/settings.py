from __future__ import annotations

from fastapi import APIRouter

from ..models import AppSettingsOut, AppSettingsUpdate
from ..services.settings_service import settings_response, update_runtime_settings


router = APIRouter(prefix="/api/settings", tags=["settings"])


@router.get("", response_model=AppSettingsOut)
def get_settings() -> dict:
    return settings_response()


@router.put("", response_model=AppSettingsOut)
def update_settings(payload: AppSettingsUpdate) -> dict:
    return update_runtime_settings(payload.model_dump())
