from __future__ import annotations

from fastapi import APIRouter

from ..models import DashboardStats
from ..repositories import dashboard_stats


router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("", response_model=DashboardStats)
def get_dashboard() -> dict:
    return dashboard_stats()
