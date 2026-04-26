from __future__ import annotations

from fastapi import APIRouter

from ..repositories import dashboard_stats
from ..schemas import DashboardStats


router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("", response_model=DashboardStats)
def get_dashboard() -> dict:
    return dashboard_stats()
