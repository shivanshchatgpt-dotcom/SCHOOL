"""Deep Learning flagship: gates, scope, idempotent apply."""
import hashlib

from app.apply_deep_learning import OWNED_DAYS, apply, collect
from app.curriculum_deep_learning import PHASES


def test_collect_covers_owned_days_with_unique_titles():
    lessons = collect()
    assert len(lessons) == 111
    assert {day for day, _, _ in lessons} == set(OWNED_DAYS)
    assert len({l["title"] for _, _, l in lessons}) == 111
    phases = [p for _, p, _ in lessons]
    assert len(set(phases)) == 8  # Deep Learning Foundations + 7 domain phases


def test_apply_rewrites_only_owned_days_idempotently(tmp_path, monkeypatch):
    monkeypatch.setenv("PYSCHOOL_SKIP_CATALOG", "1")
    from app import db
    from app.seed import _seed_catalog_curricula

    monkeypatch.setattr(db, "DB_PATH", tmp_path / "dl.db")
    db.init_db()
    from app.seed import seed
    seed()
    monkeypatch.delenv("PYSCHOOL_SKIP_CATALOG")
    conn = db.get_conn()
    try:
        dl_id = conn.execute("SELECT id FROM paths WHERE slug = 'deep-learning'").fetchone()["id"]
        assert _seed_catalog_curricula(conn, only_slugs=["deep-learning"]) > 0
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
            "SELECT theory FROM lessons WHERE path_id = ? AND day_number = 1", (dl_id,)
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
            "SELECT theory FROM lessons WHERE path_id = ? AND day_number = 1", (dl_id,)
        ).fetchone()[0] == canon_day1
        row = conn.execute(
            "SELECT title, questions, answers FROM lessons WHERE path_id = ? AND day_number = 75", (dl_id,)
        ).fetchone()
        assert row[0].startswith("Tensors and the Forward Pass:")
        import json
        assert len(json.loads(row[1])) == 3 and len(json.loads(row[2])) == 3
        ms = conn.execute(
            """SELECT m.title, m.domain FROM milestones m JOIN lesson_milestones lm ON lm.milestone_id = m.id
               JOIN lessons l ON l.id = lm.lesson_id WHERE l.path_id = ? AND l.day_number = 75""",
            (dl_id,),
        ).fetchone()
        assert ms[0].startswith("Tensors and the Forward Pass:") and ms[1] == "Deep Learning"
    finally:
        conn.close()


def test_seven_phases_of_fifteen():
    counts = {phase: len(days) for phase, _goal, days in PHASES}
    assert counts == {
        "Tensors and the Forward Pass": 15,
        "Backpropagation and Gradients": 15,
        "Training a Network": 15,
        "Convolution and Sequences": 15,
        "Optimization and Regularisation": 15,
        "Evaluation, Debugging and Deployment": 15,
        "Deep Learning Capstone": 15,
    }
