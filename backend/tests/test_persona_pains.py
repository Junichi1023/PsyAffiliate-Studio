from __future__ import annotations

from fastapi.testclient import TestClient


def test_persona_pains_crud(client: TestClient):
    payload = {
        "name": "金運不安ペルソナ",
        "category": "money",
        "pain_summary": "収入と支出のバランスが不安",
        "emotional_state": "焦りと不安",
        "desired_future": "落ち着いてお金と向き合いたい",
        "forbidden_approach": "買わないと損と急かす",
        "recommended_tone": "やさしく現実的",
    }
    created = client.post("/api/persona-pains", json=payload)
    assert created.status_code == 201
    persona_id = created.json()["id"]

    listed = client.get("/api/persona-pains")
    assert listed.status_code == 200
    assert len(listed.json()) == 1

    updated = client.put(f"/api/persona-pains/{persona_id}", json={"recommended_tone": "穏やか"})
    assert updated.status_code == 200
    assert updated.json()["recommended_tone"] == "穏やか"

    assert client.delete(f"/api/persona-pains/{persona_id}").status_code == 204
    assert client.get(f"/api/persona-pains/{persona_id}").status_code == 404
