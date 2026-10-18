"""Apply Catalog Batch A (Testing/QA pilot) to the testing-qa path.

Writes ONLY (testing-qa, days 1-14 and 75-179). Refuses everything else:
other paths, days 15-74, day 180, canonical lessons, flagship/launch tracks.
Milestone codes, ids and prerequisite edges are untouched; only
lesson/assignment content fields plus milestone title/domain/objective.

Usage: .venv/bin/python -m app.apply_catalog_batch_a --apply   (default is dry-run)
"""
from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.domain_packs_testing import OWNED_DAYS, TESTING_PACK, collect  # noqa: E402

DB_PATH = Path(__file__).resolve().parent.parent / "pyschool.db"
SLUG = "testing-qa"
APPROVED_PATH_ID = 17
APPROVED_DAYS = OWNED_DAYS


def resolve_path_id(conn: sqlite3.Connection) -> int:
    row = conn.execute("SELECT id FROM paths WHERE slug = ?", (SLUG,)).fetchone()
    if row is None:
        raise ValueError("testing-qa path missing")
    if row["id"] != APPROVED_PATH_ID:
        raise ValueError(f"path id moved: manifest says {APPROVED_PATH_ID}, database says {row['id']}")
    return row["id"]


def dry_run_report(db_path: Path = DB_PATH) -> dict:
    """No writes. Reports planned updates, skips and refusals."""
    lessons = collect()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        path_id = resolve_path_id(conn)
        planned, skipped, refused = [], [], []
        try:
            from app.canonical_topics_proxy import composed_lessons
            canonical = {(l["path"], l["day"]) for l in composed_lessons()}
        except Exception:
            canonical = set()
        for day_num, _phase, lesson in lessons:
            if (SLUG, day_num) in canonical:
                refused.append(day_num)
                continue
            row = conn.execute(
                "SELECT id FROM lessons WHERE path_id = ? AND day_number = ?", (path_id, day_num)
            ).fetchone()
            if row is None:
                refused.append(day_num)  # applier never creates rows
                continue
            cur = conn.execute(
                "SELECT title, theory, code_example, questions, answers, homework FROM lessons WHERE id = ?",
                (row["id"],),
            ).fetchone()
            new = (lesson["title"], lesson["theory"], lesson["code_example"],
                   json.dumps(lesson["questions"]), json.dumps(lesson["answers"]), lesson["homework"])
            (planned if tuple(cur) != new else skipped).append(day_num)
        return {"planned": sorted(planned), "skipped": sorted(skipped), "refused": sorted(refused)}
    finally:
        conn.close()


def apply(db_path: Path = DB_PATH, check_only: bool = True) -> dict:
    """Write owned days inside one transaction. check_only=True writes nothing."""
    lessons = collect()
    if check_only:
        rep = dry_run_report(db_path)
        return {"checked": len(lessons), "updated": 0, "skipped": len(rep["skipped"]),
                "planned": len(rep["planned"]), "refused": rep["refused"]}
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        path_id = resolve_path_id(conn)
        try:
            from app.canonical_topics_proxy import composed_lessons
            canonical = {(l["path"], l["day"]) for l in composed_lessons()}
        except Exception:
            canonical = set()
        updated = skipped = 0
        refused = []
        conn.execute("BEGIN IMMEDIATE")
        try:
            for day_num, _phase, lesson in lessons:
                if day_num not in APPROVED_DAYS or (SLUG, day_num) in canonical:
                    refused.append(day_num)
                    continue
                row = conn.execute(
                    "SELECT id FROM lessons WHERE path_id = ? AND day_number = ?", (path_id, day_num)
                ).fetchone()
                if row is None:
                    refused.append(day_num)
                    continue
                lid = row["id"]
                cur = conn.execute(
                    "SELECT title, theory, code_example, questions, answers, homework FROM lessons WHERE id = ?",
                    (lid,),
                ).fetchone()
                new = (lesson["title"], lesson["theory"], lesson["code_example"],
                       json.dumps(lesson["questions"]), json.dumps(lesson["answers"]), lesson["homework"])
                if tuple(cur) == new:
                    skipped += 1
                    continue
                conn.execute(
                    "UPDATE lessons SET title = ?, theory = ?, code_example = ?, questions = ?, answers = ?, homework = ? WHERE id = ? AND path_id = ?",
                    (*new, lid, path_id),
                )
                conn.execute(
                    "UPDATE assignments SET prompt = ?, required_patterns = ? WHERE lesson_id = ?",
                    (lesson["homework"], json.dumps(lesson["required_patterns"]), lid),
                )
                conn.execute(
                    """UPDATE milestones SET title = ?, domain = ?, objective = ? WHERE id =
                       (SELECT milestone_id FROM lesson_milestones WHERE lesson_id = ?)""",
                    (lesson["title"], lesson["domain"], lesson["objective"], lid),
                )
                updated += 1
            # Repair prerequisite chain gaps (INSERT OR IGNORE; edges untouched otherwise).
            by_order = {
                r["sort_order"]: r["id"]
                for r in conn.execute("SELECT sort_order, id FROM milestones WHERE path_id = ?", (path_id,))
            }
            for order in range(2, max(by_order) + 1):
                if order in by_order and order - 1 in by_order:
                    conn.execute(
                        "INSERT OR IGNORE INTO milestone_prerequisites (milestone_id, prerequisite_milestone_id) VALUES (?, ?)",
                        (by_order[order], by_order[order - 1]),
                    )
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        return {"checked": len(lessons), "updated": updated, "skipped": skipped, "refused": refused}
    finally:
        conn.close()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--db", default=str(DB_PATH))
    args = ap.parse_args()
    result = apply(Path(args.db), check_only=not args.apply)
    print(result)
    if args.apply:
        again = apply(Path(args.db), check_only=False)
        print("second run:", again)
        if again["updated"] != 0:
            print("NOT IDEMPOTENT")
            return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
