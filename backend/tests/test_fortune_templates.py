from __future__ import annotations

from fastapi.testclient import TestClient


def test_fortune_templates_crud(client: TestClient):
    payload = {
        "name": "人間関係占いテンプレート",
        "fortune_type": "oracle",
        "target_pain_category": "relationship",
        "structure": "1. 気持ちを受け止める\n2. 距離感を整える\n3. 小さな行動を出す",
        "example_output": "無理に近づかなくても大丈夫です。",
        "prohibited_patterns": "相手を思い通りにする",
    }
    created = client.post("/api/fortune-templates", json=payload)
    assert created.status_code == 201
    template_id = created.json()["id"]

    listed = client.get("/api/fortune-templates")
    assert listed.status_code == 200
    assert any(item["name"] == payload["name"] for item in listed.json())
    assert any(item["name"] == "金運占い投稿テンプレート" for item in listed.json())
    assert any(item["name"] == "金運の不安に寄り添う投稿" for item in listed.json())

    updated = client.put(f"/api/fortune-templates/{template_id}", json={"fortune_type": "general"})
    assert updated.status_code == 200
    assert updated.json()["fortune_type"] == "general"

    assert client.delete(f"/api/fortune-templates/{template_id}").status_code == 204
    assert client.get(f"/api/fortune-templates/{template_id}").status_code == 404
