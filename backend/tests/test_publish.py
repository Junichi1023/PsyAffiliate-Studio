from __future__ import annotations

from fastapi.testclient import TestClient


def _create_draft(client: TestClient, **overrides):
    payload = {
        "platform": "threads",
        "theme": "金運不安の整え方",
        "body": "#PR 不安な時ほど、今日できる小さな行動を1つ確認しましょう。",
        "cta": "必要な人はプロフィールのリンクからどうぞ。",
        "compliance_score": 95,
        "empathy_score": 82,
        "risk_notes": "PR表記あり",
        "empathy_notes": "読者の不安を受け止めています",
        "status": "approved",
        "affiliate_intent": "soft",
    }
    payload.update(overrides)
    response = client.post("/api/drafts", json=payload)
    assert response.status_code == 201
    return response.json()


def test_non_approved_draft_cannot_mock_publish(client: TestClient):
    draft = _create_draft(client, status="draft")
    response = client.post(f"/api/publish/drafts/{draft['id']}/mock")
    assert response.status_code == 400


def test_low_compliance_draft_cannot_mock_publish(client: TestClient):
    draft = _create_draft(client, compliance_score=60)
    response = client.post(f"/api/publish/drafts/{draft['id']}/mock")
    assert response.status_code == 400


def test_low_empathy_draft_cannot_mock_publish(client: TestClient):
    draft = _create_draft(client, empathy_score=50)
    response = client.post(f"/api/publish/drafts/{draft['id']}/mock")
    assert response.status_code == 400


def test_publish_ready_draft_can_mock_publish(client: TestClient):
    draft = _create_draft(client)
    assert draft["publish_ready"] is True
    response = client.post(f"/api/publish/drafts/{draft['id']}/mock")
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True
    assert data["provider_results"][0]["provider"] == "threads"
