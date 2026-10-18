"""Cryptography flagship Batch 1: scope safety, content gates, idempotent apply."""
import hashlib
import json

from app.apply_cybersecurity import (
    APPROVED_DAYS,
    APPROVED_PATH_ID,
    SLUG,
    apply,
    collect,
    dry_run_report,
    resolve_path_id,
)
from app.curriculum_cybersecurity import CRYPTO_PHASES


def test_collect_covers_exactly_119_owned_days():
    lessons = collect()
    assert len(lessons) == 119
    assert {day for day, _, _ in lessons} == set(APPROVED_DAYS)
    assert len({l["title"] for _, _, l in lessons}) == 119
    phases = {p for _, p, _ in lessons}
    assert len(phases) == 8  # Crypto Foundations + 7 domain phases


def test_seven_phases_of_fifteen():
    counts = {phase: len(days) for phase, _goal, days in CRYPTO_PHASES}
    assert len(counts) == 7 and all(n == 15 for n in counts.values())


def test_all_qa_lesson_specific_no_generics():
    generic = {
        "Which line in your solution is doing the real work, and what breaks if you remove it?",
        "Your second variant has different values. Which parts of your logic did you assume?",
    }
    for _day, _phase, lesson in collect():
        assert len(lesson["questions"]) == 3 and len(lesson["answers"]) == 3
        assert not (set(lesson["questions"]) & generic), lesson["title"]


def test_no_teaching_cipher_claims_production():
    banned = ["production-ready", "military-grade", "unbreakable", "NSA-proof"]
    for _day, _phase, lesson in collect():
        blob = lesson["theory"] + lesson["code_example"]
        assert not any(b in blob for b in banned), lesson["title"]


def _tmp_db(tmp_path, monkeypatch):
    monkeypatch.setenv("PYSCHOOL_SKIP_CATALOG", "1")
    from app import db
    from app.seed import _seed_catalog_curricula, seed

    monkeypatch.setattr(db, "DB_PATH", tmp_path / "cyber.db")
    db.init_db()
    seed()
    monkeypatch.delenv("PYSCHOOL_SKIP_CATALOG")
    conn = db.get_conn()
    try:
        assert _seed_catalog_curricula(conn, only_slugs=["cryptography"]) > 0
        conn.commit()
    finally:
        conn.close()
    return db


def _fingerprints(conn, slugs):
    out = {}
    for slug in slugs:
        h = hashlib.md5()
        for r in conn.execute(
            "SELECT l.theory FROM lessons l JOIN paths p ON p.id = l.path_id WHERE p.slug = ? ORDER BY l.day_number",
            (slug,),
        ):
            h.update(r[0].encode())
        out[slug] = h.hexdigest()
    return out


def test_dry_run_mutates_nothing(tmp_path, monkeypatch):
    db = _tmp_db(tmp_path, monkeypatch)
    before = db.DB_PATH.read_bytes()
    rep = dry_run_report(db.DB_PATH)
    assert rep["planned"] and not rep["refused"]
    assert db.DB_PATH.read_bytes() == before


def test_apply_rewrites_only_crypto_batch_idempotently(tmp_path, monkeypatch):
    db = _tmp_db(tmp_path, monkeypatch)
    conn = db.get_conn()
    try:
        assert resolve_path_id(conn) == APPROVED_PATH_ID == 27
        protected = _fingerprints(conn, ("web-dev", "data-science", "machine-learning", "automation"))
        canon = conn.execute(
            "SELECT theory FROM lessons l JOIN paths p ON p.id = l.path_id WHERE p.slug = 'machine-learning' AND l.day_number = 1"
        ).fetchone()[0]
        conn.close()
        result = apply(db.DB_PATH, check_only=False)
        assert result["updated"] == 119 and not result["refused"]
        again = apply(db.DB_PATH, check_only=False)
        assert again["updated"] == 0
        conn = db.get_conn()
        assert _fingerprints(conn, ("web-dev", "data-science", "machine-learning", "automation")) == protected
        assert conn.execute(
            "SELECT theory FROM lessons l JOIN paths p ON p.id = l.path_id WHERE p.slug = 'machine-learning' AND l.day_number = 1"
        ).fetchone()[0] == canon
        crypto_id = conn.execute("SELECT id FROM paths WHERE slug = 'cryptography'").fetchone()[0]
        assert conn.execute(
            "SELECT COUNT(*) FROM lessons WHERE path_id = ? AND json_array_length(questions) = 3", (crypto_id,)
        ).fetchone()[0] == 180
        assert conn.execute(
            "SELECT COUNT(*) FROM milestones WHERE path_id = ?", (crypto_id,)
        ).fetchone()[0] == 180
        row = conn.execute(
            "SELECT title FROM lessons WHERE path_id = ? AND day_number = 75", (crypto_id,)
        ).fetchone()
        assert row[0].startswith("Encodings and Binary:")
        day15 = conn.execute(
            "SELECT title FROM lessons WHERE path_id = ? AND day_number = 15", (crypto_id,)
        ).fetchone()[0]
        assert "Encodings and Binary" not in day15
    finally:
        conn.close()


def test_out_of_scope_day_refused(tmp_path, monkeypatch):
    db = _tmp_db(tmp_path, monkeypatch)
    conn = db.get_conn()
    try:
        crypto_id = conn.execute("SELECT id FROM paths WHERE slug = 'cryptography'").fetchone()[0]
        before = conn.execute(
            "SELECT theory FROM lessons WHERE path_id = ? AND day_number = 20", (crypto_id,)
        ).fetchone()[0]
        conn.close()
        result = apply(db.DB_PATH, check_only=False)
        assert result["updated"] == 119
        conn = db.get_conn()
        after = conn.execute(
            "SELECT theory FROM lessons WHERE path_id = ? AND day_number = 20", (crypto_id,)
        ).fetchone()[0]
        assert after == before
    finally:
        conn.close()
