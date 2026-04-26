from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
DEFAULT_DB_PATH = DATA_DIR / "psyaffiliate.sqlite3"
DEFAULT_SETTINGS_PATH = DATA_DIR / "settings.json"

load_dotenv(PROJECT_ROOT / ".env")


def get_db_path() -> Path:
    path = Path(os.getenv("PSYAFFILIATE_DB_PATH", str(DEFAULT_DB_PATH))).expanduser()
    return path if path.is_absolute() else PROJECT_ROOT / path


def get_settings_path() -> Path:
    path = Path(os.getenv("PSYAFFILIATE_SETTINGS_PATH", str(DEFAULT_SETTINGS_PATH))).expanduser()
    return path if path.is_absolute() else PROJECT_ROOT / path


def get_openai_api_key() -> str | None:
    return os.getenv("OPENAI_API_KEY") or None


def get_openai_model() -> str:
    return os.getenv("OPENAI_MODEL", "gpt-5.5")


def ensure_data_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
