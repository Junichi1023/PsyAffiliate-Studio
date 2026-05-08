from __future__ import annotations

from fastapi import APIRouter, HTTPException

from ..repositories import (
    create_typefully_job,
    get_draft,
    get_typefully_job,
    list_typefully_jobs,
    registered_affiliate_urls,
    update_draft,
    update_typefully_job,
)
from ..schemas import TypefullyScheduleJob, TypefullyScheduleRequest, TypefullyScheduleResult
from ..services.publishing_gate import validate_typefully_ready
from ..services.typefully.client import create_or_schedule_threads_post


router = APIRouter(prefix="/api/typefully", tags=["typefully"])


def _validate_typefully_ready(draft: dict) -> None:
    ready, reasons = validate_typefully_ready(draft, registered_affiliate_urls())
    if not ready:
        raise HTTPException(status_code=400, detail=" / ".join(reasons))


@router.post("/drafts/{draft_id}/schedule", response_model=TypefullyScheduleResult)
def schedule_draft(draft_id: int, payload: TypefullyScheduleRequest) -> dict:
    draft = get_draft(draft_id)
    _validate_typefully_ready(draft)
    text = "\n\n".join(part for part in [draft.get("body"), draft.get("caption"), draft.get("cta")] if part)
    provider = create_or_schedule_threads_post(
        text=text,
        schedule_mode=payload.schedule_mode,
        scheduled_at=payload.scheduled_at,
    )
    status = "failed"
    if provider.get("ok"):
        status = "created" if payload.schedule_mode == "draft_only" else "scheduled"
    job = create_typefully_job(
        {
            "draft_id": draft_id,
            "typefully_draft_id": provider.get("typefully_draft_id"),
            "social_set_id": provider.get("social_set_id"),
            "scheduled_at": payload.scheduled_at if payload.schedule_mode == "scheduled_time" else None,
            "status": status,
            "schedule_mode": payload.schedule_mode,
            "typefully_url": provider.get("typefully_url"),
            "error_message": provider.get("error"),
        }
    )
    update_draft(draft_id, {"typefully_job_id": job["id"], "status": "scheduled" if status == "scheduled" else draft["status"]})
    return {
        "ok": bool(provider.get("ok")),
        "job": job,
        "provider_result": provider,
        "message": provider.get("message") or "Typefully処理が完了しました。",
    }


@router.get("/jobs", response_model=list[TypefullyScheduleJob])
def jobs() -> list[dict]:
    return list_typefully_jobs()


@router.get("/jobs/{job_id}", response_model=TypefullyScheduleJob)
def job(job_id: int) -> dict:
    return get_typefully_job(job_id)


@router.put("/jobs/{job_id}/cancel-local", response_model=TypefullyScheduleJob)
def cancel_local(job_id: int) -> dict:
    return update_typefully_job(job_id, {"status": "cancelled"})
