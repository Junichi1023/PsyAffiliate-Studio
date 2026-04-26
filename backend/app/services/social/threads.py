from __future__ import annotations

from .base import SocialPublisher


class ThreadsPublisher(SocialPublisher):
    def publish_text(self, text: str) -> dict:
        return {
            "ok": False,
            "provider": "threads",
            "mock": True,
            "message": "Threads API integration is reserved for Phase 2. Approval is required before posting.",
        }

    def publish_image_post(self, caption: str, image_path: str) -> dict:
        return {
            "ok": False,
            "provider": "threads",
            "mock": True,
            "message": "Threads image publishing is not implemented in Phase 1.",
        }
