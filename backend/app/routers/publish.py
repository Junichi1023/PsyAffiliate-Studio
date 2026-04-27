from __future__ import annotations

from fastapi import APIRouter, HTTPException

from ..repositories import get_draft
from ..schemas import PublishResult
from ..services.social.instagram import InstagramPublisher
from ..services.social.threads import ThreadsPublisher


router = APIRouter(prefix="/api/publish", tags=["publish"])


def _validate_publish_ready(draft: dict) -> None:
    if draft.get("status") != "approved":
        raise HTTPException(status_code=400, detail="まだ承認済みではありません")
    if (draft.get("compliance_score") or 0) < 90:
        raise HTTPException(status_code=400, detail="安全性スコアが90未満です")
    if (draft.get("empathy_score") or 0) < 75:
        raise HTTPException(status_code=400, detail="寄り添いスコアが75未満です")
    if not draft.get("publish_ready"):
        raise HTTPException(status_code=400, detail=draft.get("publish_block_reason") or "投稿準備OKになっていません")


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
        "message": "mock投稿が完了しました。実投稿ではないため posted_at は更新していません。",
    }
