from __future__ import annotations

from .base import SocialPostResult, SocialPublisher


class ThreadsPublisher(SocialPublisher):
    def publish(self, body: str, media_paths: list[str] | None = None) -> SocialPostResult:
        return SocialPostResult(
            ok=False,
            provider="threads",
            message="Threads API integration is reserved for Phase 2. Approval is required before posting.",
        )
