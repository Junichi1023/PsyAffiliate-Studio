from __future__ import annotations

from fastapi import APIRouter, File, UploadFile

from ..repositories import (
    commit_import_session,
    create_import_session,
    get_import_session,
    list_import_candidates,
    list_import_sessions,
    update_import_candidate,
)
from ..schemas import ImportCandidate, ImportCandidateUpdate, ImportCommitResult, ImportSession, KnowledgeItem
from ..services.facebook_importer import build_candidates_from_facebook_zip


router = APIRouter(prefix="/api/import", tags=["import"])


@router.post("/facebook/preview", response_model=ImportSession, status_code=201)
async def preview_facebook_zip(file: UploadFile = File(...)) -> dict:
    payload = await file.read()
    result = build_candidates_from_facebook_zip(file.filename or "facebook.zip", payload)
    return create_import_session(
        source_name=file.filename,
        total_items=result["total_items"],
        candidates=result["candidates"],
        redaction_summary=result["redaction_summary"],
    )


@router.get("/sessions", response_model=list[ImportSession])
def sessions() -> list[dict]:
    return list_import_sessions()


@router.get("/sessions/{session_id}", response_model=ImportSession)
def session(session_id: int) -> dict:
    return get_import_session(session_id)


@router.get("/sessions/{session_id}/candidates", response_model=list[ImportCandidate])
def candidates(session_id: int) -> list[dict]:
    return list_import_candidates(session_id)


@router.put("/candidates/{candidate_id}", response_model=ImportCandidate)
def update_candidate(candidate_id: int, payload: ImportCandidateUpdate) -> dict:
    return update_import_candidate(candidate_id, payload.model_dump())


@router.post("/sessions/{session_id}/commit", response_model=ImportCommitResult)
def commit_session(session_id: int) -> dict[str, int | list[KnowledgeItem]]:
    items = commit_import_session(session_id)
    return {"committed_count": len(items), "knowledge_items": items}
