from __future__ import annotations

class SocialPublisher:
    def publish_text(self, text: str) -> dict:
        raise NotImplementedError

    def publish_image_post(self, caption: str, image_path: str) -> dict:
        raise NotImplementedError
