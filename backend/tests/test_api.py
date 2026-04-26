from __future__ import annotations

import importlib

import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("PSYAFFILIATE_DB_PATH", str(tmp_path / "test.sqlite3"))
    monkeypatch.setenv("PSYAFFILIATE_SETTINGS_PATH", str(tmp_path / "settings.json"))
    from app import database
    from app.main import app

    importlib.reload(database)
    database.init_db()
    return TestClient(app)


def test_health(client: TestClient):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


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

    listed = client.get("/api/knowledge")
    assert listed.status_code == 200
    assert len(listed.json()) == 1

    updated = client.put(f"/api/knowledge/{item_id}", json={"title": "Voice"})
    assert updated.status_code == 200
    assert updated.json()["title"] == "Voice"

    deleted = client.delete(f"/api/knowledge/{item_id}")
    assert deleted.status_code == 204
    assert client.get(f"/api/knowledge/{item_id}").status_code == 404


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
    assert created.json()["is_active"] is True

    updated = client.put(f"/api/affiliate-products/{product_id}", json={"priority": 8, "is_active": False})
    assert updated.status_code == 200
    assert updated.json()["priority"] == 8
    assert updated.json()["is_active"] is False

    listed = client.get("/api/affiliate-products")
    assert listed.status_code == 200
    assert len(listed.json()) == 1

    deleted = client.delete(f"/api/affiliate-products/{product_id}")
    assert deleted.status_code == 204


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


def test_draft_save_and_csv_export(client: TestClient):
    payload = {
        "platform": "threads",
        "theme": "先延ばしを減らすAI活用",
        "body": "#PR 小さく始めるAI活用の話",
        "caption": None,
        "cta": "プロフィールのリンクからどうぞ。",
        "compliance_score": 92,
        "risk_notes": "PR表記あり",
        "status": "draft",
    }
    created = client.post("/api/drafts", json=payload)
    assert created.status_code == 201
    assert created.json()["theme"] == payload["theme"]

    listed = client.get("/api/drafts")
    assert listed.status_code == 200
    assert len(listed.json()) == 1

    exported = client.get("/api/drafts/export.csv")
    assert exported.status_code == 200
    assert "content_drafts.csv" in exported.headers["content-disposition"]
    assert "先延ばしを減らすAI活用" in exported.text
