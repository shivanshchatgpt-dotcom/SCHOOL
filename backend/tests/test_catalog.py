"""Catalog curriculum: deterministic 180-day generator + idempotent fill."""
import ast

from app.curriculum_catalog import catalog_days, extra_questions, path_placement_questions
from app.seed_data import PATHS


def test_generator_yields_180_unique_days():
    days = catalog_days("Web Scraping", "Extract data from websites", "BeautifulSoup, Scrapy")
    assert len(days) == 180
    titles = [d[0] for d in days]
    assert len(set(titles)) == 180
    assert days[0][0] == "First Python program"
    assert days[179][0] == "180-day capstone reflection"
    # Days 15-74 are the shared authored phases.
    assert days[14][0].startswith("Core Python:")


def test_generator_is_deterministic():
    kwargs = dict(name="Q", description="D", libraries="L")
    assert catalog_days(**kwargs) == catalog_days(**kwargs)


def test_all_generated_code_parses_and_rubrics_honest():
    for name, desc, libs in [
        ("Web Scraping", "Extract data from websites", "BeautifulSoup, Scrapy"),
        ("Quantum Computing", "Program quantum algorithms", "Qiskit"),
    ]:
        for day in catalog_days(name, desc, libs):
            title, domain, objective, code, homework, patterns, theory, questions, answers = day
            ast.parse(code)
            assert patterns, title
            assert len(theory) > 100, title
            assert len(questions) == 3 and len(answers) == 3, title


def test_extra_questions_valid_for_all_paths():
    meta = [(p[1], p[2], p[3]) for p in PATHS]
    assert len(meta) == 100
    for i in range(len(meta)):
        triplet = extra_questions(meta, i)
        assert len(triplet) == 3
        for q_text, a, b, c, d, correct, diff in triplet:
            assert len({o.lower() for o in (a, b, c, d)}) == 4
            assert correct in "ABCD" and diff in (1, 2)


def test_placement_bank_is_per_path_and_valid():
    """Each path's bank differs from every other path's, and options are sane."""
    meta = [(p[1], p[2], p[3]) for p in PATHS]
    banks = [path_placement_questions(meta, i) for i in range(len(meta))]
    for bank in banks:
        assert len(bank) == 13
        for q_text, a, b, c, d, correct, diff in bank:
            assert len({o.lower() for o in (a, b, c, d)}) == 4, q_text
            assert correct in "ABCD" and diff in (1, 2, 3, 4)
    # No two paths share a question text — the whole point of the rewrite.
    seen = [q[0] for bank in banks for q in bank]
    assert len(set(seen)) == len(seen)


def test_catalog_fill_completes_one_path_idempotently(tmp_path, monkeypatch):
    """Full seed (skipping catalog), then fill a single path to 180 days."""
    monkeypatch.setenv("PYSCHOOL_SKIP_CATALOG", "1")
    from app import db
    from app.seed import seed, _seed_catalog_curricula, _seed_assessment_questions

    monkeypatch.setattr(db, "DB_PATH", tmp_path / "catalog.db")
    db.init_db()
    seed()
    conn = db.get_conn()
    try:
        slug = "web-scraping"
        path_id = conn.execute("SELECT id FROM paths WHERE slug = ?", (slug,)).fetchone()["id"]
        before = conn.execute(
            "SELECT COUNT(*) AS c FROM lessons WHERE path_id = ?", (path_id,)
        ).fetchone()["c"]
        assert 0 < before < 180
        monkeypatch.delenv("PYSCHOOL_SKIP_CATALOG")
        assert _seed_catalog_curricula(conn, only_slugs=[slug]) == 180 - before
        conn.commit()
        assert conn.execute(
            "SELECT COUNT(*) AS c FROM lessons WHERE path_id = ?", (path_id,)
        ).fetchone()["c"] == 180
        # Milestone chain covers every day exactly once.
        assert conn.execute(
            "SELECT COUNT(*) AS c FROM milestones WHERE path_id = ?", (path_id,)
        ).fetchone()["c"] == 180
        # Second run adds nothing.
        assert _seed_catalog_curricula(conn, only_slugs=[slug]) == 0
        # Placement bank is per-path and built once (guarded by meta key).
        assert conn.execute(
            "SELECT COUNT(*) AS c FROM assessment_questions WHERE path_id = ?", (path_id,)
        ).fetchone()["c"] == 13
        assert _seed_assessment_questions(conn) == 0
        # In-place deepening rewrites owned rows once, then the guard skips.
        from app.seed import _refresh_catalog_content
        conn.execute("DELETE FROM meta WHERE key = 'catalog_depth'")
        assert _refresh_catalog_content(conn) == 0  # fresh content already matches
        conn.execute(
            "UPDATE lessons SET theory = 'stale' WHERE id IN (SELECT l.id FROM lessons l JOIN paths p ON p.id = l.path_id "
            "WHERE p.slug = ?)",
            (slug,),
        )
        conn.execute("DELETE FROM meta WHERE key = 'catalog_depth'")
        assert _refresh_catalog_content(conn) >= 1  # owned rows repaired; canonical skipped
        conn.commit()
        conn.execute("DELETE FROM meta WHERE key = 'catalog_depth'")
        assert _refresh_catalog_content(conn) == 0
    finally:
        conn.close()
