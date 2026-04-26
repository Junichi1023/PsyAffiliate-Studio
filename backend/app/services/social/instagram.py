from __future__ import annotations

from .base import SocialPublisher


class InstagramPublisher(SocialPublisher):
    def publish_text(self, text: str) -> dict:
        return {
            "ok": True,
            "provider": "instagram",
            "mock": True,
            "message": "Mock Instagram text post accepted. Real Graph API integration is reserved for Phase 2.",
        }

    def publish_image_post(self, caption: str, image_path: str) -> dict:
        return {
            "ok": True,
            "provider": "instagram",
            "mock": True,
            "message": "Mock Instagram image post accepted. Real Graph API integration is reserved for Phase 2.",
        }
