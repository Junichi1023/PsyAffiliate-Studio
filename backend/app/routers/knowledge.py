from __future__ import annotations

from fastapi import APIRouter, Response

from ..repositories import create_knowledge, delete_knowledge, get_knowledge, list_knowledge, update_knowledge
from ..schemas import KnowledgeCreate, KnowledgeItem, KnowledgeUpdate


router = APIRouter(prefix="/api/knowledge", tags=["knowledge"])


@router.get("", response_model=list[KnowledgeItem])
def list_items() -> list[dict]:
    return list_knowledge()


@router.post("", response_model=KnowledgeItem, status_code=201)
def create_item(payload: KnowledgeCreate) -> dict:
    return create_knowledge(payload.model_dump())


@router.get("/{item_id}", response_model=KnowledgeItem)
def get_item(item_id: int) -> dict:
    return get_knowledge(item_id)


@router.put("/{item_id}", response_model=KnowledgeItem)
def update_item(item_id: int, payload: KnowledgeUpdate) -> dict:
    return update_knowledge(item_id, payload.model_dump())


@router.delete("/{item_id}", status_code=204)
def delete_item(item_id: int) -> Response:
    delete_knowledge(item_id)
    return Response(status_code=204)
