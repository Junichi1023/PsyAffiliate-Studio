from __future__ import annotations

from fastapi import APIRouter

from ..repositories import (
    create_threads_post_template,
    delete_threads_post_template,
    get_threads_post_template,
    list_threads_post_templates,
    update_threads_post_template,
)
from ..schemas import ThreadsPostTemplate, ThreadsPostTemplateCreate, ThreadsPostTemplateUpdate


router = APIRouter(prefix="/api/threads-post-templates", tags=["threads-post-templates"])


@router.get("", response_model=list[ThreadsPostTemplate])
def list_items() -> list[dict]:
    return list_threads_post_templates()


@router.post("", response_model=ThreadsPostTemplate, status_code=201)
def create_item(payload: ThreadsPostTemplateCreate) -> dict:
    return create_threads_post_template(payload.model_dump())


@router.get("/{item_id}", response_model=ThreadsPostTemplate)
def get_item(item_id: int) -> dict:
    return get_threads_post_template(item_id)


@router.put("/{item_id}", response_model=ThreadsPostTemplate)
def update_item(item_id: int, payload: ThreadsPostTemplateUpdate) -> dict:
    return update_threads_post_template(item_id, payload.model_dump())


@router.delete("/{item_id}", status_code=204)
def delete_item(item_id: int) -> None:
    delete_threads_post_template(item_id)
