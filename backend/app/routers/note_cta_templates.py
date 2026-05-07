from __future__ import annotations

from fastapi import APIRouter

from ..repositories import (
    create_note_cta_template,
    delete_note_cta_template,
    get_note_cta_template,
    list_note_cta_templates,
    update_note_cta_template,
)
from ..schemas import NoteCtaTemplate, NoteCtaTemplateCreate, NoteCtaTemplateUpdate


router = APIRouter(prefix="/api/note-cta-templates", tags=["note-cta-templates"])


@router.get("", response_model=list[NoteCtaTemplate])
def list_items() -> list[dict]:
    return list_note_cta_templates()


@router.post("", response_model=NoteCtaTemplate, status_code=201)
def create_item(payload: NoteCtaTemplateCreate) -> dict:
    return create_note_cta_template(payload.model_dump())


@router.get("/{item_id}", response_model=NoteCtaTemplate)
def get_item(item_id: int) -> dict:
    return get_note_cta_template(item_id)


@router.put("/{item_id}", response_model=NoteCtaTemplate)
def update_item(item_id: int, payload: NoteCtaTemplateUpdate) -> dict:
    return update_note_cta_template(item_id, payload.model_dump())


@router.delete("/{item_id}", status_code=204)
def delete_item(item_id: int) -> None:
    delete_note_cta_template(item_id)
