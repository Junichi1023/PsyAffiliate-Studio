from __future__ import annotations

from .base import SocialPublisher


class InstagramPublisher(SocialPublisher):
    def publish_text(self, text: str) -> dict:
        return {
            "ok": False,
            "provider": "instagram",
            "mock": True,
            "message": "Instagram text publishing is not implemented in Phase 1.",
        }

    def publish_image_post(self, caption: str, image_path: str) -> dict:
        return {
            "ok": False,
            "provider": "instagram",
            "mock": True,
            "message": "Instagram Graph API integration is reserved for Phase 2. Approval is required before posting.",
        }
