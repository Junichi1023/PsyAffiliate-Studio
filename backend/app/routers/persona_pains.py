from __future__ import annotations

from fastapi import APIRouter, Response

from ..repositories import (
    create_persona_pain,
    delete_persona_pain,
    get_persona_pain,
    list_persona_pains,
    update_persona_pain,
)
from ..schemas import PersonaPain, PersonaPainCreate, PersonaPainUpdate


router = APIRouter(prefix="/api/persona-pains", tags=["persona-pains"])


@router.get("", response_model=list[PersonaPain])
def list_items() -> list[dict]:
    return list_persona_pains()


@router.post("", response_model=PersonaPain, status_code=201)
def create_item(payload: PersonaPainCreate) -> dict:
    return create_persona_pain(payload.model_dump())


@router.get("/{persona_id}", response_model=PersonaPain)
def get_item(persona_id: int) -> dict:
    return get_persona_pain(persona_id)


@router.put("/{persona_id}", response_model=PersonaPain)
def update_item(persona_id: int, payload: PersonaPainUpdate) -> dict:
    return update_persona_pain(persona_id, payload.model_dump())


@router.delete("/{persona_id}", status_code=204)
def delete_item(persona_id: int) -> Response:
    delete_persona_pain(persona_id)
    return Response(status_code=204)
