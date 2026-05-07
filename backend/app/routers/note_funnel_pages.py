from __future__ import annotations

from fastapi import APIRouter

from ..repositories import (
    create_note_funnel_page,
    delete_note_funnel_page,
    get_note_funnel_page,
    list_note_funnel_pages,
    update_note_funnel_page,
)
from ..schemas import NoteFunnelPage, NoteFunnelPageCreate, NoteFunnelPageUpdate


router = APIRouter(prefix="/api/note-funnel-pages", tags=["note-funnel-pages"])


@router.get("", response_model=list[NoteFunnelPage])
def list_items() -> list[dict]:
    return list_note_funnel_pages()


@router.post("", response_model=NoteFunnelPage, status_code=201)
def create_item(payload: NoteFunnelPageCreate) -> dict:
    return create_note_funnel_page(payload.model_dump())


@router.get("/{item_id}", response_model=NoteFunnelPage)
def get_item(item_id: int) -> dict:
    return get_note_funnel_page(item_id)


@router.put("/{item_id}", response_model=NoteFunnelPage)
def update_item(item_id: int, payload: NoteFunnelPageUpdate) -> dict:
    return update_note_funnel_page(item_id, payload.model_dump())


@router.delete("/{item_id}", status_code=204)
def delete_item(item_id: int) -> None:
    delete_note_funnel_page(item_id)
