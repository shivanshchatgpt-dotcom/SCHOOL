"""Shared fixtures: isolated temp database per test session."""
import sys
from pathlib import Path

import pytest

BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))


def _wrong_answers(client, path_id):
    """Answers guaranteed to be incorrect (correct answers live only in the DB)."""
    from app import db as db_module

    questions = client.get(f"/api/assessment/{path_id}/questions").json()
    conn = db_module.get_conn()
    try:
        correct = {
            row["id"]: row["correct"]
            for row in conn.execute(
                "SELECT id, correct FROM assessment_questions WHERE path_id=?", (path_id,)
            ).fetchall()
        }
    finally:
        conn.close()
    alternatives = {"A", "B", "C", "D"}
    return [
        {"question_id": q["id"], "selected": sorted(alternatives - {correct[q["id"]]})[0]}
        for q in questions
    ]


@pytest.fixture()
def client(tmp_path, monkeypatch):
    """FastAPI TestClient backed by a fresh, fully seeded temp database."""
    from app import db

    monkeypatch.setattr(db, "DB_PATH", tmp_path / "test-pyschool.db")
    # ponytail: the 97-path catalog fill is a seed-time bulk load, not unit
    # behaviour; skipping it keeps the suite fast (see test_catalog.py).
    monkeypatch.setenv("PYSCHOOL_SKIP_CATALOG", "1")
    from app.main import app
    from fastapi.testclient import TestClient

    with TestClient(app) as test_client:  # lifespan runs init_db + seed
        yield test_client


def submit_answers(client, path_id, name, email, answers):
    return client.post(
        "/api/assessment/submit",
        json={"path_id": path_id, "student_name": name, "student_email": email,
              "answers": answers},
    )


@pytest.fixture()
def enrollment(client):
    """A zero-score (Foundation -> Day 1) web-dev enrollment plus its token."""
    path_row = client.get("/api/paths/web-dev").json()
    result = submit_answers(
        client, path_row["id"], "Test Student", "test@example.com",
        _wrong_answers(client, path_row["id"]),
    ).json()
    assert result["level"] == "Foundation"
    assert result["score"] == 0
    return {
        "enrollment_id": result["enrollment_id"],
        "token": result["access_token"],
        "path_id": path_row["id"],
    }
