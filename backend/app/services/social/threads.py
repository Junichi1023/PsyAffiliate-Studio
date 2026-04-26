from __future__ import annotations

from .base import SocialPublisher


class ThreadsPublisher(SocialPublisher):
    def publish_text(self, text: str) -> dict:
        return {
            "ok": True,
            "provider": "threads",
            "mock": True,
            "message": "Mock Threads post accepted. Real Threads API integration is reserved for Phase 2.",
        }

    def publish_image_post(self, caption: str, image_path: str) -> dict:
        return {
            "ok": True,
            "provider": "threads",
            "mock": True,
            "message": "Mock Threads image post accepted. Real image publishing is reserved for Phase 2.",
        }
