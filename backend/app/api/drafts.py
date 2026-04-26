from __future__ import annotations

from fastapi import APIRouter, Response
from fastapi.responses import StreamingResponse

from ..models import Draft, DraftCreate, DraftUpdate
from ..repositories import create_draft, delete_draft, drafts_to_csv, get_draft, list_drafts, update_draft


router = APIRouter(prefix="/api/drafts", tags=["drafts"])


@router.post("", response_model=Draft, status_code=201)
def create_item(payload: DraftCreate) -> dict:
    return create_draft(payload.model_dump())


@router.get("", response_model=list[Draft])
def list_items() -> list[dict]:
    return list_drafts()


@router.get("/export.csv")
def export_csv() -> StreamingResponse:
    csv_body = drafts_to_csv()
    return StreamingResponse(
        iter([csv_body]),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": "attachment; filename=content_drafts.csv"},
    )


@router.get("/{draft_id}", response_model=Draft)
def get_item(draft_id: int) -> dict:
    return get_draft(draft_id)


@router.put("/{draft_id}", response_model=Draft)
def update_item(draft_id: int, payload: DraftUpdate) -> dict:
    return update_draft(draft_id, payload.model_dump())


@router.delete("/{draft_id}", status_code=204)
def delete_item(draft_id: int) -> Response:
    delete_draft(draft_id)
    return Response(status_code=204)
