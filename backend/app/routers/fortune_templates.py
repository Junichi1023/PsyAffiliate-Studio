from __future__ import annotations

from fastapi import APIRouter, Response

from ..repositories import (
    create_fortune_template,
    delete_fortune_template,
    get_fortune_template,
    list_fortune_templates,
    update_fortune_template,
)
from ..schemas import FortuneTemplate, FortuneTemplateCreate, FortuneTemplateUpdate


router = APIRouter(prefix="/api/fortune-templates", tags=["fortune-templates"])


@router.get("", response_model=list[FortuneTemplate])
def list_items() -> list[dict]:
    return list_fortune_templates()


@router.post("", response_model=FortuneTemplate, status_code=201)
def create_item(payload: FortuneTemplateCreate) -> dict:
    return create_fortune_template(payload.model_dump())


@router.get("/{template_id}", response_model=FortuneTemplate)
def get_item(template_id: int) -> dict:
    return get_fortune_template(template_id)


@router.put("/{template_id}", response_model=FortuneTemplate)
def update_item(template_id: int, payload: FortuneTemplateUpdate) -> dict:
    return update_fortune_template(template_id, payload.model_dump())


@router.delete("/{template_id}", status_code=204)
def delete_item(template_id: int) -> Response:
    delete_fortune_template(template_id)
    return Response(status_code=204)
