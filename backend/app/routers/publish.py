from __future__ import annotations

from fastapi import APIRouter, HTTPException

from ..repositories import get_draft
from ..schemas import PublishResult
from ..services.social.instagram import InstagramPublisher
from ..services.social.threads import ThreadsPublisher


router = APIRouter(prefix="/api/publish", tags=["publish"])


def _validate_publish_ready(draft: dict) -> None:
    if draft.get("status") != "approved":
        raise HTTPException(status_code=400, detail="Draft status must be approved before mock publish")
    if (draft.get("compliance_score") or 0) < 90:
        raise HTTPException(status_code=400, detail="Compliance score must be 90 or higher")
    if (draft.get("empathy_score") or 0) < 75:
        raise HTTPException(status_code=400, detail="Empathy score must be 75 or higher")
    if not draft.get("publish_ready"):
        raise HTTPException(status_code=400, detail=draft.get("publish_block_reason") or "Draft is not publish ready")


@router.post("/drafts/{draft_id}/mock", response_model=PublishResult)
def mock_publish(draft_id: int) -> dict:
    draft = get_draft(draft_id)
    _validate_publish_ready(draft)

    text = "\n\n".join(part for part in [draft["body"], draft.get("caption"), draft.get("cta")] if part)
    provider_results = []
    if draft["platform"] in ("threads", "both"):
        provider_results.append(ThreadsPublisher().publish_text(text))
    if draft["platform"] in ("instagram", "both"):
        provider_results.append(InstagramPublisher().publish_text(text))

    return {
        "ok": True,
        "draft_id": draft_id,
        "provider_results": provider_results,
        "message": "Mock publish completed. posted_at was not updated.",
    }
