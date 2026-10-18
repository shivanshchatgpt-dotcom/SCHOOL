"""Batch B (database-ops) guards: schema, scope, protected, uniqueness, exec, idempotency, e2e."""
import hashlib
import json
import sqlite3

from app.apply_catalog_batch_b import APPROVED_DAYS, APPROVED_PATH_ID, SLUG, apply, dry_run_report
from app.domain_engine import _words, jaccard, run_code
from app.domain_packs_database_ops import collect

CANONICAL_REFUSED = [1, 2, 3, 4]  # book-grounded days, resolved from DB
EFFECTIVE = 115  # 119 owned minus 4 canonical


def _scratch(tmp_path, monkeypatch):
    """State-independent scratch DB: fresh seed + template catalog rows for database-ops."""
    monkeypatch.setenv("PYSCHOOL_SKIP_CATALOG", "1")
    from app import db
    from app.seed import _seed_catalog_curricula, seed

    monkeypatch.setattr(db, "DB_PATH", tmp_path / "batchb.db")
    db.init_db()
    seed()
    monkeypatch.delenv("PYSCHOOL_SKIP_CATALOG")
    conn = db.get_conn()
    try:
        assert _seed_catalog_curricula(conn, only_slugs=["database-ops"]) > 0
        conn.commit()
    finally:
        conn.close()
    return tmp_path / "batchb.db"


def test_collect_schema_and_gates():
    items = collect()
    assert len(items) == 119
    titles = [l["title"] for _, _, l in items]
    assert len(set(titles)) == 119
    for day, _, l in items:
        assert len(l["questions"]) == 3 and len(l["answers"]) == 3
        assert 450 <= _words(l["theory"]) <= 900
        assert len(l["homework"]) >= 120
        assert l["required_patterns"]


def test_collect_day_scope():
    items = collect()
    assert sorted(d for d, _, _ in items) == sorted(APPROVED_DAYS)
    assert not (set(range(15, 75)) & {d for d, _, _ in items})
    assert 180 not in {d for d, _, _ in items}


def test_examples_execute_with_output():
    for day, _, l in collect():
        out = run_code(l["code_example"])
        assert out, day
        assert out in l["theory"], day  # captured output embedded


def test_question_homework_uniqueness():
    items = collect()
    qs = [" | ".join(l["questions"]) for _, _, l in items]
    hws = [l["homework"] for _, _, l in items]
    worst_q = worst_h = 0.0
    for i in range(len(qs)):
        for j in range(i + 1, len(qs)):
            worst_q = max(worst_q, jaccard(qs[i], qs[j]))
            worst_h = max(worst_h, jaccard(hws[i], hws[j]))
    assert worst_q <= 0.62, worst_q
    assert worst_h <= 0.62, worst_h
    for _, _, l in items:
        blob = " ".join(l["questions"]).lower()
        assert "what is the main topic" not in blob
        assert "what did you learn today" not in blob
        assert "practice what you learned and submit your work" not in l["homework"].lower()


def test_dry_run_mutates_nothing(tmp_path, monkeypatch):
    dest = _scratch(tmp_path, monkeypatch)
    before = hashlib.md5(open(dest, "rb").read()).hexdigest()
    rep = dry_run_report(dest)
    assert rep["refused"] == CANONICAL_REFUSED  # canonical preserved
    assert len(rep["planned"]) == EFFECTIVE
    after = hashlib.md5(open(dest, "rb").read()).hexdigest()
    assert before == after


def test_apply_scope_and_protected(tmp_path, monkeypatch):
    dest = _scratch(tmp_path, monkeypatch)
    c = sqlite3.connect(dest)
    pre_ids = c.execute(
        "SELECT id, day_number FROM lessons WHERE path_id = ? ORDER BY day_number", (APPROVED_PATH_ID,)
    ).fetchall()
    pre_codes = c.execute(
        "SELECT id, code FROM milestones WHERE path_id = ? ORDER BY sort_order", (APPROVED_PATH_ID,)
    ).fetchall()
    pre_edges = c.execute(
        "SELECT milestone_id, prerequisite_milestone_id FROM milestone_prerequisites "
        "WHERE milestone_id IN (SELECT id FROM milestones WHERE path_id = ?) ORDER BY 1, 2",
        (APPROVED_PATH_ID,),
    ).fetchall()
    pre_other = hashlib.sha256(
        repr(c.execute(
            "SELECT id, path_id, day_number, title, theory FROM lessons WHERE path_id != ? ORDER BY path_id, day_number",
            (APPROVED_PATH_ID,),
        ).fetchall()).encode()
    ).hexdigest()
    pre_keep = c.execute(
        "SELECT id, day_number, title, theory FROM lessons WHERE path_id = ? AND ((day_number >= 15 AND day_number <= 74) OR day_number = 180) ORDER BY day_number",
        (APPROVED_PATH_ID,),
    ).fetchall()
    c.close()

    r1 = apply(dest, check_only=False)
    assert r1["checked"] == 119 and r1["updated"] == EFFECTIVE and r1["refused"] == CANONICAL_REFUSED
    r2 = apply(dest, check_only=False)
    assert r2["updated"] == 0 and r2["skipped"] == EFFECTIVE  # idempotent

    c = sqlite3.connect(dest)
    post_ids = c.execute(
        "SELECT id, day_number FROM lessons WHERE path_id = ? ORDER BY day_number", (APPROVED_PATH_ID,)
    ).fetchall()
    assert post_ids == pre_ids  # lesson ids preserved
    post_codes = c.execute(
        "SELECT id, code FROM milestones WHERE path_id = ? ORDER BY sort_order", (APPROVED_PATH_ID,)
    ).fetchall()
    assert post_codes == pre_codes  # milestone ids/codes preserved
    post_edges = c.execute(
        "SELECT milestone_id, prerequisite_milestone_id FROM milestone_prerequisites "
        "WHERE milestone_id IN (SELECT id FROM milestones WHERE path_id = ?) ORDER BY 1, 2",
        (APPROVED_PATH_ID,),
    ).fetchall()
    assert len(post_edges) == 179 and set(pre_edges) <= set(post_edges)
    added = set(post_edges) - set(pre_edges)
    by_sort = {r[0]: r[1] for r in
               c.execute("SELECT sort_order, id FROM milestones WHERE path_id = ?", (APPROVED_PATH_ID,))}
    chain = {(by_sort[o], by_sort[o - 1]) for o in range(2, 181)}
    assert added <= chain  # repair fills chain gaps only
    post_other = hashlib.sha256(
        repr(c.execute(
            "SELECT id, path_id, day_number, title, theory FROM lessons WHERE path_id != ? ORDER BY path_id, day_number",
            (APPROVED_PATH_ID,),
        ).fetchall()).encode()
    ).hexdigest()
    assert post_other == pre_other  # no out-of-scope rows modified
    post_keep = c.execute(
        "SELECT id, day_number, title, theory FROM lessons WHERE path_id = ? AND ((day_number >= 15 AND day_number <= 74) OR day_number = 180) ORDER BY day_number",
        (APPROVED_PATH_ID,),
    ).fetchall()
    assert post_keep == pre_keep  # days 15-74 + 180 unchanged
    n_assign = c.execute(
        "SELECT COUNT(*) FROM assignments a JOIN lessons l ON l.id = a.lesson_id "
        "WHERE l.path_id = ? AND ((l.day_number <= 14) OR (l.day_number >= 75 AND l.day_number <= 179))",
        (APPROVED_PATH_ID,),
    ).fetchone()[0]
    assert n_assign == 119
    c.close()


def test_e2e_lesson_flow(tmp_path, monkeypatch):
    """Enroll → lesson → dashboard shape on scratch-applied DB."""
    dest = _scratch(tmp_path, monkeypatch)
    apply(dest, check_only=False)
    c = sqlite3.connect(dest)
    c.row_factory = sqlite3.Row
    row = c.execute(
        "SELECT id, title, theory, code_example, questions, answers, homework FROM lessons "
        "WHERE path_id = ? AND day_number = 75",
        (APPROVED_PATH_ID,),
    ).fetchone()
    assert row and row["theory"] and row["code_example"]
    q, a = json.loads(row["questions"]), json.loads(row["answers"])
    assert len(q) == 3 and len(a) == 3
    ms = c.execute(
        "SELECT m.code, m.title FROM milestones m JOIN lesson_milestones lm ON lm.milestone_id = m.id "
        "WHERE lm.lesson_id = ?",
        (row["id"],),
    ).fetchone()
    assert ms and ms["code"].startswith("DATABASE-OPS-")
    c.close()
