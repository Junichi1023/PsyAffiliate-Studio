from __future__ import annotations

from pathlib import Path


def test_japanese_ui_label_mappings_exist():
    labels = Path(__file__).parents[2] / "frontend" / "src" / "constants" / "labels.ts"
    source = labels.read_text(encoding="utf-8")

    for text in [
        "ダッシュボード",
        "アフィリエイト商品",
        "悩みペルソナ",
        "占いテンプレート",
        "投稿作成",
        "下書き・投稿管理",
        "安全性 高",
        "寄り添い度 高",
        "金運",
        "控えめに紹介",
    ]:
        assert text in source
