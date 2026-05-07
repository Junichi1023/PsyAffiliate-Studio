from __future__ import annotations

from fastapi import APIRouter

from ..repositories import (
    create_fortune_a8_offer,
    delete_fortune_a8_offer,
    get_fortune_a8_offer,
    list_fortune_a8_offers,
    update_fortune_a8_offer,
)
from ..schemas import FortuneA8Offer, FortuneA8OfferCreate, FortuneA8OfferUpdate


router = APIRouter(prefix="/api/fortune-a8-offers", tags=["fortune-a8-offers"])


@router.get("", response_model=list[FortuneA8Offer])
def list_items() -> list[dict]:
    return list_fortune_a8_offers()


@router.post("", response_model=FortuneA8Offer, status_code=201)
def create_item(payload: FortuneA8OfferCreate) -> dict:
    return create_fortune_a8_offer(payload.model_dump())


@router.get("/{item_id}", response_model=FortuneA8Offer)
def get_item(item_id: int) -> dict:
    return get_fortune_a8_offer(item_id)


@router.put("/{item_id}", response_model=FortuneA8Offer)
def update_item(item_id: int, payload: FortuneA8OfferUpdate) -> dict:
    return update_fortune_a8_offer(item_id, payload.model_dump())


@router.delete("/{item_id}", status_code=204)
def delete_item(item_id: int) -> None:
    delete_fortune_a8_offer(item_id)
