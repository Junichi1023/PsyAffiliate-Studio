from __future__ import annotations

from fastapi.testclient import TestClient


def test_knowledge_crud(client: TestClient):
    payload = {
        "title": "Brand Voice",
        "category": "brand_voice",
        "content": "落ち着いた実用的な口調",
        "source": "manual",
    }
    created = client.post("/api/knowledge", json=payload)
    assert created.status_code == 201
    item_id = created.json()["id"]

    assert len(client.get("/api/knowledge").json()) == 1

    updated = client.put(f"/api/knowledge/{item_id}", json={"title": "Voice"})
    assert updated.status_code == 200
    assert updated.json()["title"] == "Voice"

    assert client.delete(f"/api/knowledge/{item_id}").status_code == 204
    assert client.get(f"/api/knowledge/{item_id}").status_code == 404
