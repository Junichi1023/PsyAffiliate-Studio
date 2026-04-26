from __future__ import annotations

from fastapi.testclient import TestClient


def test_empathy_check_detects_low_quality_post(client: TestClient):
    response = client.post(
        "/api/content/empathy-check",
        json={
            "body": "今すぐ買わないと不幸になる。これを信じれば必ず運命が変わる。リンクから購入してください。",
            "target_reader": "将来が不安な人",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["empathy_score"] < 75
    assert data["checks"]["avoids_fear_pressure"] is False
    assert data["checks"]["avoids_deterministic_prediction"] is False


def test_empathy_check_scores_supportive_post_high(client: TestClient):
    response = client.post(
        "/api/content/empathy-check",
        json={
            "body": "将来が不安になる日もありますよね。まず今日できる小さな行動を1つだけ、気持ちを書き出して確認してみてください。",
            "target_reader": "将来が不安な人",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["empathy_score"] >= 75
    assert data["checks"]["acknowledges_emotion"] is True
    assert data["checks"]["has_small_action"] is True
