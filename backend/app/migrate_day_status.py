"""Schema migration: give lessons an explicit day_type and release status.

Two things were missing. `lessons` had no column recording what kind of day a
row is, so a concept day and a generated practice day were indistinguishable once
written; and it had no way to mark a day as not yet releaseable, so a stub that
nobody had rewritten was served to students exactly like a finished lesson.

Both are added non-destructively. Existing rows keep their content untouched; the
new columns are populated from the classifier and from the audit inventory, so
the values are derived rather than typed in by hand.

Running the script twice must change nothing the second time. That is checked
here rather than assumed, because a migration that is only idempotent by luck is
a migration nobody can safely re-run after a partial failure.
"""
from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.day_type import classify  # noqa: E402

DB_PATH = Path(__file__).resolve().parent.parent / "pyschool.db"
INVENTORY = Path("/tmp/kilo/d75_149_audit.json")

ADDED: list[str] = []


def ensure_column(conn: sqlite3.Connection, table: str, column: str, decl: str) -> bool:
    """Add a column only if absent. Returns True when it was added."""
    cols = {r[1] for r in conn.execute(f"PRAGMA table_info({table})")}
    if column in cols:
        return False
    conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {decl}")
    ADDED.append(f"{table}.{column}")
    return True


def ensure_index(conn: sqlite3.Connection, name: str, ddl: str) -> None:
    conn.execute(f"CREATE INDEX IF NOT EXISTS {name} {ddl}")


def backfill_day_type(conn: sqlite3.Connection) -> tuple[int, int]:
    """Classify every lesson. Returns (classified, skipped_as_practice)."""
    rows = conn.execute(
        """
        SELECT l.id, l.title, l.theory, l.questions, l.code_example, l.homework
        FROM lessons l JOIN paths p ON p.id = l.path_id
        """
    ).fetchall()

    classified = 0
    already_practice = 0
    for r in rows:
        if (r["theory"] or "").find("This is a practice day") != -1:
            dt = "practice"
            already_practice += 1
        else:
            dt = classify(
                r["title"], r["theory"], r["questions"], r["code_example"], r["homework"]
            )
        conn.execute("UPDATE lessons SET day_type = ? WHERE id = ?", (dt, r["id"]))
        classified += 1
    return classified, already_practice


def backfill_status(conn: sqlite3.Connection, inventory_path: Path) -> tuple[int, int]:
    """Mark unreleased days from the audit inventory.

    Only days the audit covers are marked in_progress. A day the audit never
    looked at is left active rather than being silently withheld, so the count of
    hidden days always equals the number of days someone deliberately held back.
    """
    if not inventory_path.exists():
        return 0, 0
    items = json.loads(inventory_path.read_text())
    held: list[tuple[str, int, str]] = []
    for x in items:
        if x.get("recommended") != "rewrite_new":
            continue
        if x.get("tier") != "B":
            continue
        held.append(
            (x["slug"], int(x["day"]), x.get("status_reason") or "held: no corpus support")
        )

    applied = 0
    for slug, day, reason in held:
        row = conn.execute(
            "SELECT l.id FROM lessons l JOIN paths p ON p.id = l.path_id "
            "WHERE p.slug = ? AND l.day_number = ?",
            (slug, day),
        ).fetchone()
        if row is None:
            continue
        conn.execute(
            "UPDATE lessons SET status = 'in_progress', status_reason = ? WHERE id = ?",
            (reason, row["id"]),
        )
        applied += 1
    return applied, len(held)


def mark_tier_a(conn: sqlite3.Connection, inventory_path: Path) -> int:
    """Days cleared for rewriting are active and carry their provenance ref."""
    if not inventory_path.exists():
        return 0
    items = json.loads(inventory_path.read_text())
    n = 0
    for x in items:
        if x.get("recommended") != "rewrite_new" or x.get("tier") != "A":
            continue
        row = conn.execute(
            "SELECT l.id FROM lessons l JOIN paths p ON p.id = l.path_id "
            "WHERE p.slug = ? AND l.day_number = ?",
            (x["slug"], int(x["day"])),
        ).fetchone()
        if row is None:
            continue
        conn.execute(
            "UPDATE lessons SET status = 'active', status_reason = ? WHERE id = ?",
            (x.get("status_reason") or "cleared for rewrite", row["id"]),
        )
        n += 1
    return n


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--db", default=str(DB_PATH))
    ap.add_argument("--inventory", default=str(INVENTORY))
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    db = Path(args.db)
    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row

    before = conn.execute("SELECT COUNT(*) FROM lessons").fetchone()[0]
    print(f"lessons before: {before}")

    if args.dry_run:
        print("dry run: no changes written")
        return 0

    added_day = ensure_column(conn, "lessons", "day_type", "TEXT DEFAULT 'concept'")
    added_status = ensure_column(conn, "lessons", "status", "TEXT DEFAULT 'active'")
    added_reason = ensure_column(conn, "lessons", "status_reason", "TEXT DEFAULT ''")
    print(f"columns added this run: {ADDED or 'none (already present)'}")
    if not ADDED:
        print("all columns already present")

    classified, already = backfill_day_type(conn)
    held_applied, held_total = backfill_status(conn, Path(args.inventory))
    tier_a = mark_tier_a(conn, Path(args.inventory))
    conn.commit()

    print(f"day_type backfilled: {classified} lessons ({already} already generated practice)")
    print(f"status=in_progress applied: {held_applied}/{held_total} held days")
    print(f"tier A marked active: {tier_a}")

    ensure_index(conn, "idx_lessons_day_type", "ON lessons(day_type)")
    ensure_index(conn, "idx_lessons_status", "ON lessons(status)")
    conn.commit()
    print("indexes ensured on day_type and status")

    print("\n=== verification ===")
    after = conn.execute("SELECT COUNT(*) FROM lessons").fetchone()[0]
    print(f"lessons after: {after}  ({'unchanged' if before == after else 'CHANGED!'})")
    print("\nday_type distribution:")
    for row in conn.execute(
        "SELECT day_type, COUNT(*) n FROM lessons GROUP BY day_type ORDER BY n DESC"
    ):
        print(f"   {row['day_type'] or '(null)':<12} {row['n']}")
    print("\nstatus distribution:")
    for row in conn.execute(
        "SELECT status, COUNT(*) n FROM lessons GROUP BY status ORDER BY n DESC"
    ):
        print(f"   {row['status'] or '(null)':<14} {row['n']}")
    print("\nstatus_reason present on in_progress days:",
          conn.execute(
              "SELECT COUNT(*) FROM lessons WHERE status='in_progress' "
              "AND (status_reason IS NULL OR status_reason='')"
          ).fetchone()[0] == 0)

    print("\n=== idempotency: second run must change nothing ===")
    snapshot = conn.execute(
        "SELECT id, day_type, status, status_reason FROM lessons ORDER BY id"
    ).fetchall()
    ensure_column(conn, "lessons", "day_type", "TEXT DEFAULT 'concept'")
    ensure_column(conn, "lessons", "status", "TEXT DEFAULT 'active'")
    ensure_column(conn, "lessons", "status_reason", "TEXT DEFAULT ''")
    backfill_day_type(conn)
    backfill_status(conn, Path(args.inventory))
    mark_tier_a(conn, Path(args.inventory))
    conn.commit()
    again = conn.execute(
        "SELECT id, day_type, status, status_reason FROM lessons ORDER BY id"
    ).fetchall()
    diff = sum(1 for a, b in zip(snapshot, again) if tuple(a) != tuple(b))
    print(f"rows changed on second run: {diff}  ({'IDEMPOTENT' if diff == 0 else 'NOT IDEMPOTENT'})")
    return 0 if diff == 0 else 3


if __name__ == "__main__":
    raise SystemExit(main())
