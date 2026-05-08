from __future__ import annotations

import json
from collections import Counter
from typing import Any, BinaryIO

from .importers.facebook_archive import FacebookImportError, extract_facebook_archive
from .importers.knowledge_mapper import build_knowledge_candidates
from .importers.pii_sanitizer import sanitize_text


def _redaction_summary(stats: Counter[str], skipped_files: list[str], sanitized_items: int) -> str:
    payload = {
        "email_removed": stats.get("email_removed", 0),
        "phone_removed": stats.get("phone_removed", 0),
        "url_removed": stats.get("url_removed", 0),
        "facebook_url_removed": stats.get("facebook_url_removed", 0),
        "instagram_url_removed": stats.get("instagram_url_removed", 0),
        "x_url_removed": stats.get("x_url_removed", 0),
        "postal_code_removed": stats.get("postal_code_removed", 0),
        "long_id_removed": stats.get("long_id_removed", 0),
        "credit_card_like_removed": stats.get("credit_card_like_removed", 0),
        "username_removed": stats.get("username_removed", 0),
        "line_id_removed": stats.get("line_id_removed", 0),
        "address_like_removed": stats.get("address_like_removed", 0),
        "name_like_warning": stats.get("name_like_warning", 0),
        "skipped_message_files": stats.get("skipped_message_files", 0),
        "message_files_processed": stats.get("message_files_processed", 0),
        "skipped_json_files": stats.get("skipped_json_files", 0),
        "skipped_html_files": stats.get("skipped_html_files", 0),
        "json_files_processed": stats.get("json_files_processed", 0),
        "html_files_processed": stats.get("html_files_processed", 0),
        "duplicate_texts_skipped": stats.get("duplicate_texts_skipped", 0),
        "sanitized_text_fragments": sanitized_items,
        "skipped_files": skipped_files[:20],
    }
    return json.dumps(payload, ensure_ascii=False)


def build_candidates_from_facebook_zip(
    filename: str,
    payload: bytes | BinaryIO,
    limit: int = 40,
    *,
    max_items: int = 2000,
    include_messages: bool = False,
    use_ai_summary: bool = False,
) -> dict[str, Any]:
    """Build summarized knowledge candidates from a Facebook archive.

    `use_ai_summary` is accepted for forward compatibility. Phase 1 keeps the
    transformation deterministic so imports work without an OpenAI API key.
    """
    archive_result = extract_facebook_archive(
        payload,
        include_messages=include_messages,
        max_items=max(1, max_items),
    )
    candidates = build_knowledge_candidates(archive_result.texts[:max_items], filename)[:limit]
    if not candidates:
        raise FacebookImportError("Facebookデータからナレッジ候補を作成できませんでした。postsを含むJSON形式のZIPを選択してください。")
    return {
        "total_items": archive_result.total_items,
        "sanitized_items": archive_result.sanitized_items,
        "candidates": candidates,
        "redaction_summary": _redaction_summary(
            archive_result.stats,
            archive_result.skipped_files,
            archive_result.sanitized_items,
        ),
        "use_ai_summary": use_ai_summary,
    }
