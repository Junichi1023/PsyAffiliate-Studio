from __future__ import annotations

from fastapi import APIRouter, Response

from ..models import AffiliateProduct, AffiliateProductCreate, AffiliateProductUpdate
from ..repositories import create_product, delete_product, get_product, list_products, update_product


router = APIRouter(prefix="/api/affiliate-products", tags=["affiliate-products"])


@router.get("", response_model=list[AffiliateProduct])
def list_items() -> list[dict]:
    return list_products()


@router.post("", response_model=AffiliateProduct, status_code=201)
def create_item(payload: AffiliateProductCreate) -> dict:
    return create_product(payload.model_dump())


@router.get("/{product_id}", response_model=AffiliateProduct)
def get_item(product_id: int) -> dict:
    return get_product(product_id)


@router.put("/{product_id}", response_model=AffiliateProduct)
def update_item(product_id: int, payload: AffiliateProductUpdate) -> dict:
    return update_product(product_id, payload.model_dump())


@router.delete("/{product_id}", status_code=204)
def delete_item(product_id: int) -> Response:
    delete_product(product_id)
    return Response(status_code=204)
