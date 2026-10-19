"""Excel Automation flagship: gates, scope, idempotent apply."""
import hashlib

from app.apply_excel_automation import OWNED_DAYS, apply, collect
from app.curriculum_excel_automation import PHASES


def test_collect_covers_owned_days_with_unique_titles():
    lessons = collect()
    assert len(lessons) == 111
    assert {day for day, _, _ in lessons} == set(OWNED_DAYS)
    assert len({l["title"] for _, _, l in lessons}) == 111
    phases = [p for _, p, _ in lessons]
    assert len(set(phases)) == 8  # Excel Automation Foundations + 7 domain phases


def test_apply_rewrites_only_owned_days_idempotently(tmp_path, monkeypatch):
    monkeypatch.setenv("PYSCHOOL_SKIP_CATALOG", "1")
    from app import db
    from app.seed import _seed_catalog_curricula

    monkeypatch.setattr(db, "DB_PATH", tmp_path / "xl.db")
    db.init_db()
    from app.seed import seed
    seed()
    monkeypatch.delenv("PYSCHOOL_SKIP_CATALOG")
    conn = db.get_conn()
    try:
        xl_id = conn.execute("SELECT id FROM paths WHERE slug = 'excel-automation'").fetchone()["id"]
        assert _seed_catalog_curricula(conn, only_slugs=["excel-automation"]) > 0
        conn.commit()
        before_launch = {}
        for slug in ("web-dev", "data-science", "agi-research"):
            h = hashlib.md5()
            for r in conn.execute(
                "SELECT l.theory FROM lessons l JOIN paths p ON p.id = l.path_id WHERE p.slug = ? ORDER BY l.day_number",
                (slug,),
            ):
                h.update(r[0].encode())
            before_launch[slug] = h.hexdigest()
        canon_day1 = conn.execute(
            "SELECT theory FROM lessons WHERE path_id = ? AND day_number = 1", (xl_id,)
        ).fetchone()[0]
        conn.close()
        result = apply(db.DB_PATH, check_only=False)
        assert result == {"checked": 111, "updated": 111, "skipped": 0}
        again = apply(db.DB_PATH, check_only=False)
        assert again["updated"] == 0
        conn = db.get_conn()
        for slug, digest in before_launch.items():
            h = hashlib.md5()
            for r in conn.execute(
                "SELECT l.theory FROM lessons l JOIN paths p ON p.id = l.path_id WHERE p.slug = ? ORDER BY l.day_number",
                (slug,),
            ):
                h.update(r[0].encode())
            assert h.hexdigest() == digest, slug
        assert conn.execute(
            "SELECT theory FROM lessons WHERE path_id = ? AND day_number = 1", (xl_id,)
        ).fetchone()[0] == canon_day1
        row = conn.execute(
            "SELECT title, questions, answers FROM lessons WHERE path_id = ? AND day_number = 75", (xl_id,)
        ).fetchone()
        assert row[0].startswith("Rows, Columns and Cells:")
        import json
        assert len(json.loads(row[1])) == 3 and len(json.loads(row[2])) == 3
        ms = conn.execute(
            """SELECT m.title, m.domain FROM milestones m JOIN lesson_milestones lm ON lm.milestone_id = m.id
               JOIN lessons l ON l.id = lm.lesson_id WHERE l.path_id = ? AND l.day_number = 75""",
            (xl_id,),
        ).fetchone()
        assert ms[0].startswith("Rows, Columns and Cells:") and ms[1] == "Excel Automation"
    finally:
        conn.close()


def test_seven_phases_of_fifteen():
    counts = {phase: len(days) for phase, _goal, days in PHASES}
    assert counts == {
        "Rows, Columns and Cells": 15,
        "Cleaning and Transforming Data": 15,
        "Aggregation and Reports": 15,
        "Files, Formats and Integration": 15,
        "Automation, Scheduling and Reliability": 15,
        "Scaling, Testing and Performance": 15,
        "Excel Automation Capstone": 15,
    }
