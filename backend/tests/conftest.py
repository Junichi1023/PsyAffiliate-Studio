from __future__ import annotations

import importlib

import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("PSYAFFILIATE_DB_PATH", str(tmp_path / "test.sqlite3"))
    monkeypatch.setenv("OPENAI_API_KEY", "")
    from app import database
    from app.main import app

    importlib.reload(database)
    database.init_db()
    return TestClient(app)
