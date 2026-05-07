from __future__ import annotations

from fastapi import APIRouter, HTTPException

from ..repositories import (
    create_typefully_job,
    get_draft,
    get_typefully_job,
    list_typefully_jobs,
    update_draft,
    update_typefully_job,
)
from ..schemas import TypefullyScheduleJob, TypefullyScheduleRequest, TypefullyScheduleResult
from ..services.typefully.client import create_or_schedule_threads_post


router = APIRouter(prefix="/api/typefully", tags=["typefully"])


def _validate_typefully_ready(draft: dict) -> None:
    if draft.get("status") != "approved":
        raise HTTPException(status_code=400, detail="まだ承認済みではありません")
    if (draft.get("compliance_score") or 0) < 90:
        raise HTTPException(status_code=400, detail="安全性スコアが90未満です")
    if (draft.get("empathy_score") or 0) < 75:
        raise HTTPException(status_code=400, detail="寄り添いスコアが75未満です")
    if draft.get("direct_a8_link_detected"):
        raise HTTPException(status_code=400, detail="Threads本文にA8直リンクらしきURLが含まれています")
    if not draft.get("profile_note_cta_included"):
        raise HTTPException(status_code=400, detail="プロフィールnoteへの導線が含まれていません")
    if not draft.get("note_page_id"):
        raise HTTPException(status_code=400, detail="note記事URLが設定されていません")


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
