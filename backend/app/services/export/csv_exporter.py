from __future__ import annotations

from ...repositories import drafts_to_csv


def export_drafts_csv() -> str:
    return drafts_to_csv()
