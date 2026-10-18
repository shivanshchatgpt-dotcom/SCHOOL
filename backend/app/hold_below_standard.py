"""Hold every lesson that has not been written up to the current standard.

The catalog was filled by seeding, and most of what it filled was a placeholder:
a title, a one-line objective, an eighty-word body and a homework line whose
code sample was often about a different subject than the title claimed. Those
days are indistinguishable from finished lessons once they are in the database,
so the API serves them and a student's roadmap shows them as real work.

This script applies the one rule that is objective and checkable. A day is
released when it either teaches properly, meaning a body at or above the theory
word budget, or was produced by the exercise generator, which is marked by its
own body text. Everything else is held with a reason, so nothing is silently
withdrawn and the held set can be reversed by re-running with a different rule.

The script is idempotent. Running it twice writes nothing the second time, which
matters because the point of the rule is that it can be re-applied as more days
get written.
"""
from __future__ import annotations

import argparse
import re
import sqlite3
import sys
from collections import Counter
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "pyschool.db"

MIN_THEORY_WORDS = 450
GENERATED_MARKER = "This is a practice day"
HOLD_REASON = "content expansion pending: body below the 450-word teaching standard"


def words(text: str) -> int:
    return len(re.findall(r"\b[\w'-]+\b", text or ""))


def ensure_column(conn: sqlite3.Connection, table: str, column: str, decl: str) -> None:
    cols = {r[1] for r in conn.execute(f"PRAGMA table_info({table})")}
    if column not in cols:
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {decl}")


def classify_content(theory: str) -> str:
    """generated | authored_full | shell"""
    if (theory or "").find(GENERATED_MARKER) != -1:
        return "generated"
    return "authored_full" if words(theory) >= MIN_THEORY_WORDS else "shell"


def apply_rule(conn: sqlite3.Connection, *, dry_run: bool) -> dict:
    rows = conn.execute(
        "SELECT id, title, theory, status, status_reason FROM lessons"
    ).fetchall()

    held = released = unchanged = 0
    detail: Counter = Counter()
    per_path: dict[str, Counter] = {}

    for r in rows:
        kind = classify_content(r["theory"])
        if kind == "shell":
            if r["status"] != "in_progress":
                held += 1
                if not dry_run:
                    conn.execute(
                        "UPDATE lessons SET status = 'in_progress', status_reason = ? WHERE id = ?",
                        (HOLD_REASON, r["id"]),
                    )
            else:
                unchanged += 1
        else:
            if r["status"] == "in_progress":
                # A held day that now meets the standard is released again, so
                # that rewriting a day is all it takes to un-hold it.
                released += 1
                if not dry_run:
                    conn.execute(
                        "UPDATE lessons SET status = 'active', status_reason = ? WHERE id = ?",
                        ("", r["id"]),
                    )
            else:
                unchanged += 1
        detail[kind] += 1

    if not dry_run:
        conn.commit()
    return {"held": held, "released": released, "unchanged": unchanged,
            "detail": detail, "total": len(rows)}


def snapshot(conn: sqlite3.Connection) -> list[tuple]:
    return [tuple(r) for r in conn.execute(
        "SELECT id, status, status_reason FROM lessons ORDER BY id")]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--db", default=str(DB_PATH))
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    conn = sqlite3.connect(args.db)
    conn.row_factory = sqlite3.Row
    ensure_column(conn, "lessons", "status", "TEXT DEFAULT 'active'")
    ensure_column(conn, "lessons", "status_reason", "TEXT DEFAULT ''")
    ensure_column(conn, "lessons", "status_note", "TEXT DEFAULT ''")
    conn.commit()

    before_n = conn.execute("SELECT COUNT(*) FROM lessons").fetchone()[0]
    before = snapshot(conn)

    res = apply_rule(conn, dry_run=args.dry_run)
    print(f"lessons: {before_n}")
    print(f"held now: {res['held']}  released: {res['released']}  "
          f"already correct: {res['unchanged']}")
    print("content types: " + "  ".join(f"{k}={v}" for k, v in res["detail"].most_common()))

    if args.dry_run:
        print("dry run: nothing written")
        return 0

    after_n = conn.execute("SELECT COUNT(*) FROM lessons").fetchone()[0]
    print(f"\nlessons after: {after_n}  "
          f"({'unchanged' if before_n == after_n else 'CHANGED!'})")

    print("\n=== status distribution ===")
    for r in conn.execute("SELECT status, COUNT(*) n FROM lessons GROUP BY status ORDER BY n DESC"):
        print(f"   {r['status']:<14}{r['n']}")

    print("\n=== per path: active vs in_progress ===")
    print(f"   {'path':<16}{'active':>8}{'in_progress':>13}{'total':>7}")
    q = """
    SELECT p.slug,
           SUM(CASE WHEN l.status='active' THEN 1 ELSE 0 END) a,
           SUM(CASE WHEN l.status='in_progress' THEN 1 ELSE 0 END) b,
           COUNT(*) t
    FROM lessons l JOIN paths p ON p.id=l.path_id
    GROUP BY p.id HAVING t > 1 ORDER BY a DESC
    """
    ta = tb = 0
    for r in conn.execute(q):
        print(f"   {r['slug']:<16}{r['a']:>8}{r['b']:>13}{r['t']:>7}")
        ta += r["a"]; tb += r["b"]
    print(f"   {'TOTAL':<16}{ta:>8}{tb:>13}{ta+tb:>7}")

    print("\n=== quality of what remains active ===")
    act = conn.execute("SELECT theory FROM lessons WHERE status='active'").fetchall()
    kinds = Counter(classify_content(r["theory"]) for r in act)
    for k, v in kinds.most_common():
        print(f"   {k:<18}{v}")
    shells = kinds.get("shell", 0)
    print(f"   -> active days below standard: {shells}")

    print("\n=== idempotency: second run must write nothing ===")
    mid = snapshot(conn)
    apply_rule(conn, dry_run=False)
    end = snapshot(conn)
    diff = sum(1 for a, b in zip(mid, end) if a != b)
    print(f"rows changed on second run: {diff}  "
          f"({'IDEMPOTENT' if diff == 0 else 'NOT IDEMPOTENT'})")
    return 0 if diff == 0 else 3


if __name__ == "__main__":
    raise SystemExit(main())
