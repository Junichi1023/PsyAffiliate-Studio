from __future__ import annotations

import io
import json
import zipfile

from fastapi.testclient import TestClient

from app.services.facebook_importer import sanitize_text


def _zip_bytes() -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr(
            "posts/your_posts.json",
            json.dumps(
                {
                    "posts": [
                        {
                            "text": "札幌で人と話していると、恋愛の悩みは相手を変えるより自分の気持ちを整理することが大事だと感じます。mail@example.com 090-1111-2222"
                        }
                    ]
                },
                ensure_ascii=False,
            ),
        )
        archive.writestr("messages/inbox/thread.json", json.dumps({"messages": [{"content": "保存しないメッセージ"}]}, ensure_ascii=False))
    return buffer.getvalue()


def _note_page(client: TestClient) -> dict:
    response = client.post(
        "/api/note-funnel-pages",
        json={"title": "復縁相談前の質問リスト", "note_url": "https://note.com/example/reunion", "status": "published"},
    )
    assert response.status_code == 201
    return response.json()


def _approved_draft(client: TestClient, **overrides) -> dict:
    note = overrides.pop("note", None) or _note_page(client)
    payload = {
        "platform": "threads",
        "theme": "復縁相談前に整理すること",
        "body": "【PR】連絡が来ない時ほど、相手の気持ちを決めつけず、自分が聞きたいことを整理しましょう。プロフィールのnoteにまとめています。",
        "cta": "詳しくはプロフィールのnoteへ。",
        "status": "approved",
        "compliance_score": 95,
        "empathy_score": 82,
        "note_page_id": note["id"],
    }
    payload.update(overrides)
    response = client.post("/api/drafts", json=payload)
    assert response.status_code == 201
    return response.json()


def test_facebook_pii_sanitizer():
    sanitized, notes = sanitize_text("連絡は test@example.com または 090-1234-5678、https://example.com まで")
    assert "test@example.com" not in sanitized
    assert "090-1234-5678" not in sanitized
    assert "https://example.com" not in sanitized
    assert notes


def test_facebook_preview_and_commit(client: TestClient):
    response = client.post(
        "/api/import/facebook/preview",
        files={"file": ("facebook.zip", _zip_bytes(), "application/zip")},
    )
    assert response.status_code == 201
    session = response.json()
    assert session["candidate_count"] >= 1

    candidates = client.get(f"/api/import/sessions/{session['id']}/candidates").json()
    assert "mail@example.com" not in candidates[0]["content"]
    assert "保存しないメッセージ" not in candidates[0]["content"]

    committed = client.post(f"/api/import/sessions/{session['id']}/commit")
    assert committed.status_code == 200
    assert committed.json()["committed_count"] >= 1


def test_note_funnel_pages_crud(client: TestClient):
    page = _note_page(client)
    updated = client.put(f"/api/note-funnel-pages/{page['id']}", json={"status": "ready"})
    assert updated.status_code == 200
    assert updated.json()["status"] == "ready"
    assert client.delete(f"/api/note-funnel-pages/{page['id']}").status_code == 204


def test_fortune_a8_offers_crud(client: TestClient):
    created = client.post(
        "/api/fortune-a8-offers",
        json={"offer_name": "電話占いA", "affiliate_url": "https://px.a8.net/svt/ejp?a8mat=test", "service_type": "phone_fortune"},
    )
    assert created.status_code == 201
    offer_id = created.json()["id"]
    assert client.put(f"/api/fortune-a8-offers/{offer_id}", json={"reward_amount": 12000}).json()["reward_amount"] == 12000


def test_threads_template_and_cta_seeds(client: TestClient):
    templates = client.get("/api/threads-post-templates").json()
    ctas = client.get("/api/note-cta-templates").json()
    assert any(item["name"] == "恋愛悩みの共感投稿" for item in templates)
    assert any("プロフィールのnote" in item["text"] for item in ctas)


def test_draft_detects_direct_a8_link_and_profile_note_cta(client: TestClient):
    client.post("/api/fortune-a8-offers", json={"offer_name": "A8", "affiliate_url": "https://px.a8.net/svt/ejp?a8mat=abc"})
    draft = _approved_draft(client, body="【PR】プロフィールのnoteにまとめています。https://px.a8.net/svt/ejp?a8mat=abc")
    assert draft["direct_a8_link_detected"] is True
    assert draft["profile_note_cta_included"] is True


def test_typefully_rejects_invalid_drafts(client: TestClient):
    draft = _approved_draft(client, body="【PR】プロフィールのnoteにまとめています。https://a8.net/example")
    assert client.post(f"/api/typefully/drafts/{draft['id']}/schedule", json={"schedule_mode": "draft_only"}).status_code == 400

    draft = _approved_draft(client, status="draft")
    assert client.post(f"/api/typefully/drafts/{draft['id']}/schedule", json={"schedule_mode": "draft_only"}).status_code == 400

    draft = _approved_draft(client, compliance_score=70)
    assert client.post(f"/api/typefully/drafts/{draft['id']}/schedule", json={"schedule_mode": "draft_only"}).status_code == 400

    draft = _approved_draft(client, empathy_score=60)
    assert client.post(f"/api/typefully/drafts/{draft['id']}/schedule", json={"schedule_mode": "draft_only"}).status_code == 400

    draft = _approved_draft(client, note_page_id=None)
    assert client.post(f"/api/typefully/drafts/{draft['id']}/schedule", json={"schedule_mode": "draft_only"}).status_code == 400


def test_typefully_mock_schedule_without_api_key(client: TestClient, monkeypatch):
    monkeypatch.delenv("TYPEFULLY_API_KEY", raising=False)
    monkeypatch.delenv("TYPEFULLY_SOCIAL_SET_ID", raising=False)
    draft = _approved_draft(client)
    response = client.post(f"/api/typefully/drafts/{draft['id']}/schedule", json={"schedule_mode": "next_free_slot"})
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True
    assert data["provider_result"]["mock"] is True


def test_threads_30day_plan_seed(client: TestClient):
    response = client.get("/api/threads-30day-plan")
    assert response.status_code == 200
    data = response.json()
    assert len(data["tasks"]) >= 5
    assert data["post_type_distribution"]["恋愛・復縁の共感投稿"] == 40
