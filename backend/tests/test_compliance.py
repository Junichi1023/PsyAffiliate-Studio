from __future__ import annotations

from fastapi.testclient import TestClient


def test_compliance_detects_dangerous_terms(client: TestClient):
    response = client.post(
        "/api/content/compliance-check",
        json={"body": "この方法なら絶対に治る。医師不要です。"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "絶対" in data["flagged_terms"]
    assert "治る" in data["flagged_terms"]
    assert data["compliance_score"] < 90
    assert data["suggested_fix"]


def test_compliance_warns_affiliate_without_pr(client: TestClient):
    product = client.post(
        "/api/affiliate-products",
        json={"name": "Tool", "affiliate_url": "https://example.com/tool", "is_active": True},
    ).json()
    response = client.post(
        "/api/content/compliance-check",
        json={"body": "便利なツールです。リンクからどうぞ。", "affiliate_product_id": product["id"]},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["has_pr_disclosure"] is False
    assert any("#PR" in note for note in data["risk_notes"])


def test_compliance_detects_fortune_dangerous_terms(client: TestClient):
    response = client.post(
        "/api/content/compliance-check",
        json={"body": "この占いは必ず当たる。金運が爆上がりします。"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "必ず当たる" in data["flagged_terms"]
    assert "金運が爆上がり" in data["flagged_terms"]
