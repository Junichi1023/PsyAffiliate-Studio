from __future__ import annotations

from fastapi.testclient import TestClient


def test_affiliate_products_crud(client: TestClient):
    payload = {
        "name": "AI Note Template",
        "asp_name": "Sample ASP",
        "affiliate_url": "https://example.com/a",
        "display_url": "https://example.com",
        "category": "ai",
        "target_pain": "先延ばし",
        "commission_type": "fixed",
        "commission_amount": 1000,
        "prohibited_claims": "必ず改善",
        "priority": 5,
        "is_active": True,
    }
    created = client.post("/api/affiliate-products", json=payload)
    assert created.status_code == 201
    product_id = created.json()["id"]

    updated = client.put(f"/api/affiliate-products/{product_id}", json={"priority": 8, "is_active": False})
    assert updated.status_code == 200
    assert updated.json()["priority"] == 8
    assert updated.json()["is_active"] is False

    assert len(client.get("/api/affiliate-products").json()) == 1
    assert client.delete(f"/api/affiliate-products/{product_id}").status_code == 204
