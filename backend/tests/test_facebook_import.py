from __future__ import annotations

import io
import json
import zipfile

from fastapi.testclient import TestClient

from app.services.facebook_importer import build_candidates_from_facebook_zip, sanitize_text
from app.services.importers.facebook_archive import extract_facebook_archive
from app.services.link_safety import detect_direct_affiliate_link
from app.services.note_cta_detector import detect_profile_note_cta
from app.services.publishing_gate import validate_typefully_ready


def _zip(files: dict[str, bytes | str]) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        for path, content in files.items():
            archive.writestr(path, content)
    return buffer.getvalue()


def _json_bytes(data: object, *, bom: bool = False) -> bytes:
    raw = json.dumps(data, ensure_ascii=False).encode("utf-8")
    return (b"\xef\xbb\xbf" + raw) if bom else raw


def _sample_text() -> str:
    return "札幌で友人と話していると、恋愛の不安は相手を変えるより自分の気持ちを整理することが大事だと感じました。"


def test_sanitize_text_removes_sensitive_patterns():
    sanitized, notes = sanitize_text(
        "mail@example.com 090-1234-5678 https://facebook.com/me 1234567890123 @junichi LINE ID: abc123 060-0000"
    )
    assert "mail@example.com" not in sanitized
    assert "090-1234-5678" not in sanitized
    assert "https://facebook.com" not in sanitized
    assert "1234567890123" not in sanitized
    assert "@junichi" not in sanitized
    assert notes


def test_extracts_posts_from_nested_facebook_zip():
    payload = _zip({"facebook-yourname/posts/your_posts_1.json": _json_bytes({"posts": [{"text": _sample_text()}]})})
    result = extract_facebook_archive(payload)
    assert result.sanitized_items == 1
    assert "恋愛の不安" in result.texts[0].text


def test_extracts_posts_from_facebook_html_export():
    html = """
    <html><body>
      <section class="_a6-g">
        <h2 class="_2ph_ _a6-h _a6-i">2026年5月7日</h2>
        <div class="_2ph_ _a6-p">札幌で友人と話していると、恋愛の不安は相手を変えるより自分の気持ちを整理することが大事だと感じました。</div>
      </section>
    </body></html>
    """
    payload = _zip({"your_facebook_activity/posts/your_posts__check_ins__photos_and_videos_1.html": html})
    result = extract_facebook_archive(payload)
    assert result.sanitized_items == 1
    assert result.stats["html_files_processed"] == 1
    assert result.stats["json_files_processed"] == 0
    assert "恋愛の不安" in result.texts[0].text


def test_include_messages_false_skips_inbox():
    payload = _zip({
        "posts/your_posts_1.json": _json_bytes({"posts": [{"text": _sample_text()}]}),
        "messages/inbox/message_1.json": _json_bytes({"messages": [{"content": "これはMessenger由来のかなり長い個人的な会話テキストです。"}]}),
    })
    result = extract_facebook_archive(payload, include_messages=False)
    assert result.stats["skipped_message_files"] == 1
    assert all(not item.from_messages for item in result.texts)


def test_include_messages_true_marks_message_sources():
    payload = _zip({"messages/inbox/message_1.json": _json_bytes({"messages": [{"content": "これはMessenger由来のかなり長い個人的な会話テキストです。気持ちの整理に関する内容です。"}]})})
    result = extract_facebook_archive(payload, include_messages=True)
    assert result.stats["message_files_processed"] == 1
    assert any(item.from_messages for item in result.texts)
    candidates = build_candidates_from_facebook_zip("facebook.zip", payload, include_messages=True)["candidates"]
    assert any("Messenger由来" in (candidate["redaction_notes"] or "") for candidate in candidates)


def test_broken_json_does_not_break_import_and_bom_json_is_read():
    payload = _zip({
        "posts/broken.json": "{not-json",
        "posts/your_posts_1.json": _json_bytes({"posts": [{"text": _sample_text()}]}, bom=True),
    })
    result = extract_facebook_archive(payload)
    assert result.stats["skipped_json_files"] == 1
    assert result.sanitized_items == 1


def test_preview_api_creates_session_and_summary_candidates(client: TestClient):
    raw_post = f"{_sample_text()} mail@example.com 090-1111-2222 https://example.com"
    payload = _zip({"your_facebook_activity/posts/your_posts_1.json": _json_bytes({"posts": [{"text": raw_post}]})})
    response = client.post(
        "/api/import/facebook/preview",
        data={"max_items": "500", "include_messages": "false", "use_ai_summary": "false"},
        files={"file": ("facebook.zip", payload, "application/zip")},
    )
    assert response.status_code == 201
    session = response.json()
    assert session["sanitized_items"] == 1
    candidates = client.get(f"/api/import/sessions/{session['id']}/candidates").json()
    assert len(candidates) >= 6
    assert "mail@example.com" not in candidates[0]["content"]
    assert "090-1111-2222" not in candidates[0]["content"]
    assert "https://example.com" not in candidates[0]["content"]
    assert raw_post not in candidates[0]["content"]
    assert "傾向" in candidates[0]["content"] or "要約" in candidates[0]["redaction_notes"]


def test_preview_api_accepts_html_facebook_export(client: TestClient):
    html = """
    <html><body>
      <section><h2>2026年5月7日</h2><div>札幌で友人と話していると、恋愛の不安は相手を変えるより自分の気持ちを整理することが大事だと感じました。</div></section>
    </body></html>
    """
    payload = _zip({"your_facebook_activity/posts/your_posts__check_ins__photos_and_videos_1.html": html})
    response = client.post(
        "/api/import/facebook/preview",
        data={"max_items": "500", "include_messages": "false", "use_ai_summary": "false"},
        files={"file": ("facebook-html.zip", payload, "application/zip")},
    )
    assert response.status_code == 201
    session = response.json()
    summary = json.loads(session["redaction_summary"])
    assert session["sanitized_items"] == 1
    assert summary["html_files_processed"] == 1
    candidates = client.get(f"/api/import/sessions/{session['id']}/candidates").json()
    assert len(candidates) >= 6
    assert "札幌で友人と話していると" not in candidates[0]["content"]


def test_commit_selected_candidates_only(client: TestClient):
    payload = _zip({"posts/your_posts_1.json": _json_bytes({"posts": [{"text": _sample_text()}]})})
    session = client.post("/api/import/facebook/preview", files={"file": ("facebook.zip", payload, "application/zip")}).json()
    candidates = client.get(f"/api/import/sessions/{session['id']}/candidates").json()
    first, second = candidates[0], candidates[1]
    assert client.put(f"/api/import/candidates/{first['id']}", json={"selected": False}).status_code == 200
    assert client.put(f"/api/import/candidates/{second['id']}", json={"title": "登録する候補", "selected": True}).status_code == 200
    committed = client.post(f"/api/import/sessions/{session['id']}/commit").json()
    titles = [item["title"] for item in committed["knowledge_items"]]
    assert "登録する候補" in titles
    assert first["title"] not in titles


def test_link_and_note_detectors():
    link = detect_direct_affiliate_link("詳しくはこちら https://px.a8.net/svt/ejp?a8mat=abc")
    note = detect_profile_note_cta("詳しくはプロフィールのnoteにまとめています。")
    assert link["detected"] is True
    assert note["detected"] is True


def test_publishing_gate_and_draft_auto_publish_ready(client: TestClient):
    note = client.post("/api/note-funnel-pages", json={"title": "note", "note_url": "https://note.com/example"}).json()
    safe_payload = {
        "platform": "threads",
        "theme": "復縁相談前の整理",
        "body": "【PR】連絡が来ない時ほど、相手を決めつけず自分の気持ちを整理しましょう。プロフィールのnoteにまとめています。",
        "cta": "詳しくはプロフィールのnoteへ。",
        "status": "approved",
        "compliance_score": 95,
        "empathy_score": 82,
        "note_page_id": note["id"],
    }
    draft = client.post("/api/drafts", json=safe_payload).json()
    assert draft["direct_a8_link_detected"] is False
    assert draft["profile_note_cta_included"] is True
    assert draft["publish_ready"] is True
    ready, reasons = validate_typefully_ready(draft)
    assert ready is True
    unsafe = client.post("/api/drafts", json={**safe_payload, "body": "【PR】必ず復縁できます。https://a8.net/example"}).json()
    assert unsafe["publish_ready"] is False
    assert unsafe["direct_a8_link_detected"] is True
    assert unsafe["publish_block_reason"]
