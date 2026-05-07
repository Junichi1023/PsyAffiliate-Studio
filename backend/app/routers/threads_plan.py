from __future__ import annotations

from fastapi import APIRouter

from ..repositories import list_threads_30day_plan, update_threads_30day_plan_task
from ..schemas import Threads30DayPlan, Threads30DayPlanTask, Threads30DayPlanTaskUpdate


router = APIRouter(prefix="/api/threads-30day-plan", tags=["threads-30day-plan"])

POST_TYPE_DISTRIBUTION = {
    "恋愛・復縁の共感投稿": 40,
    "占いの使い方・注意点": 25,
    "質問例・チェックリスト": 20,
    "記事誘導": 10,
    "自分の考え・体験談": 5,
}


@router.get("", response_model=Threads30DayPlan)
def list_plan() -> dict:
    return {"tasks": list_threads_30day_plan(), "post_type_distribution": POST_TYPE_DISTRIBUTION}


@router.put("/{item_id}", response_model=Threads30DayPlanTask)
def update_plan_item(item_id: int, payload: Threads30DayPlanTaskUpdate) -> dict:
    return update_threads_30day_plan_task(item_id, payload.model_dump())
