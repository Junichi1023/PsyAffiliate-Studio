from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class SocialPostResult:
    ok: bool
    provider: str
    external_id: str | None = None
    message: str = ""


class SocialPublisher(ABC):
    @abstractmethod
    def publish(self, body: str, media_paths: list[str] | None = None) -> SocialPostResult:
        """Publish an approved post. Phase 1 implementations are intentionally mocked."""
