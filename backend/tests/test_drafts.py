from __future__ import annotations

from fastapi.testclient import TestClient


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
