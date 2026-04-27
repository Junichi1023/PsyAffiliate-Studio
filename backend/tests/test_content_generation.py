from __future__ import annotations

from fastapi.testclient import TestClient


def test_generate_accepts_fortune_type_and_affiliate_intent(client: TestClient):
    product = client.post(
        "/api/affiliate-products",
        json={
            "name": "占いノート講座",
            "affiliate_url": "https://example.com/fortune-note",
            "display_url": "https://example.com/fortune-note",
            "prohibited_claims": "必ず当たる",
            "is_active": True,
        },
    ).json()
    persona = client.post(
        "/api/persona-pains",
        json={
            "name": "金運が不安な読者",
            "category": "money",
            "pain_summary": "支出が増えて将来のお金が不安",
        },
    ).json()
    template = client.get("/api/fortune-templates").json()[0]

    response = client.post(
        "/api/content/generate",
        json={
            "theme": "金運の不安を整える",
            "target_reader": "お金の不安で行動が止まりがちな人",
            "platform": "threads",
            "tone": "empathy",
            "selected_product_id": product["id"],
            "fortune_type": "money_luck",
            "persona_pain_id": persona["id"],
            "fortune_template_id": template["id"],
            "affiliate_intent": "soft",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["platform"] == "threads"
    assert data["affiliate_product_id"] == product["id"]
    assert data["empathy_score"] is not None
    assert "#PR" in data["pr_disclosure"]
