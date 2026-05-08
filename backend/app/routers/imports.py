from __future__ import annotations

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from ..repositories import (
    commit_import_session,
    create_import_session,
    get_import_session,
    list_import_candidates,
    list_import_sessions,
    update_import_candidate,
)
from ..schemas import ImportCandidate, ImportCandidateUpdate, ImportCommitResult, ImportSession, KnowledgeItem
from ..services.facebook_importer import FacebookImportError, build_candidates_from_facebook_zip


router = APIRouter(prefix="/api/import", tags=["import"])


@router.post("/facebook/preview", response_model=ImportSession, status_code=201)
async def preview_facebook_zip(
    file: UploadFile | None = File(None),
    use_ai_summary: bool = Form(False),
    include_messages: bool = Form(False),
    max_items: int = Form(2000),
) -> dict:
    if file is None:
        raise HTTPException(status_code=400, detail="Facebook ZIPファイルを選択してください。")
    filename = file.filename or "facebook.zip"
    if not filename.lower().endswith(".zip"):
        raise HTTPException(status_code=400, detail="FacebookからダウンロードしたZIPファイルを、解凍せずそのまま選択してください。")
    try:
        file.file.seek(0, 2)
        size = file.file.tell()
        file.file.seek(0)
    except Exception:
        size = 0
    if not size:
        raise HTTPException(status_code=400, detail="選択されたファイルが空です。FacebookのZIPファイルを選択してください。")
    try:
        result = build_candidates_from_facebook_zip(
            filename,
            file.file,
            max_items=max(1, min(max_items, 5000)),
            include_messages=include_messages,
            use_ai_summary=use_ai_summary,
        )
    except FacebookImportError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    return create_import_session(
        source_name=filename,
        total_items=result["total_items"],
        sanitized_items=result["sanitized_items"],
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
