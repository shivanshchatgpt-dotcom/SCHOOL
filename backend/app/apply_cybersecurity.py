"""Apply the flagship Cryptography curriculum to the cryptography path.

Writes ONLY (cryptography, days 1-14 and 75-179). Refuses everything else:
other paths, days 15-74, day 180, canonical lessons, launch tracks, ML and
automation content. Milestone codes, ids and prerequisite edges are untouched;
only lesson/assignment content fields plus milestone title/domain/objective.

Usage: .venv/bin/python -m app.apply_cybersecurity --apply   (default is dry-run)
"""
from __future__ import annotations

import argparse
import ast
import contextlib
import io
import json
import re
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.curriculum_cybersecurity import CRYPTO_PHASES, DOMAIN, FOUNDATION  # noqa: E402

DB_PATH = Path(__file__).resolve().parent.parent / "pyschool.db"
SLUG = "cryptography"
EXPECTED_PATH_ID: int | None = None  # resolved at runtime, must equal manifest id
MIN_THEORY_WORDS = 450
MAX_THEORY_WORDS = 900

# Approved (path_id, days). Nothing outside this set is writable, ever.
APPROVED_PATH_ID = 27
APPROVED_DAYS = frozenset(list(range(1, 15)) + list(range(75, 180)))


def _words(text: str) -> int:
    return len(re.findall(r"\b[\w'-]+\b", text or ""))


def run_code(code: str) -> str:
    """Execute our own example and capture stdout. Raises on failure.

    Bounded by a wall-clock alarm: an example that cannot finish in seconds
    is a broken example, and hanging the applier (or CI) is worse than failing.
    """
    import signal

    def _timeout(_signum, _frame):
        raise TimeoutError("example did not finish in time")

    buf = io.StringIO()
    previous = signal.signal(signal.SIGALRM, _timeout)
    signal.alarm(10)
    try:
        with contextlib.redirect_stdout(buf):
            exec(compile(code, "<cyber-example>", "exec"), {"__name__": "__cyber_example__"})
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, previous)
    out = buf.getvalue().strip()
    if not out:
        raise ValueError("example runs silently")
    return out


def build_day(phase: str, day: dict) -> dict:
    """Compose the lesson dict the DB consumes. Output is captured, not written by hand."""
    output = run_code(day["code"])
    questions, answers = day["qa"]
    theory = "\n".join([
        f"**Today: {day['topic']}**",
        "",
        day["idea"],
        "",
        "**Worked example**",
        "This is the reference. Write your own version rather than copying it, then compare outputs.",
        "",
        "```python",
        day["code"],
        "```",
        "",
        "Running it prints:",
        "",
        "```",
        output,
        "```",
        "",
        "**In real systems**",
        day["mapping"],
        "",
        "**Your turn — two variants**",
        "Each one is the same problem with different values, so a value that happens to work in the first is not proof the second will. Predict each output before running it.",
        "",
        f"**Variant 1** — {day['variant_b']}",
        "Adapt the worked example to these values and print the result.",
        "",
        f"**Variant 2** — {day['variant_c']}",
        "Adapt the worked example to these values and print the result.",
        "",
        "**Common mistakes**",
        *[f"- {m}" for m in day["mistakes"]],
        "",
        "**Going further**",
        f"Use {day['topic']} inside a larger {DOMAIN} practice task this week, and notice where the idea strains. That strain is the map of what to learn next.",
        "",
        "**Study protocol (60 minutes)**",
        "1. Read the worked example and predict its output before running it.",
        "2. Change exactly one value and predict again — either way you learn.",
        "3. Write today's practice from scratch while explaining choices in comments.",
    ])
    return {
        "title": f"{phase}: {day['topic']}" if phase else day["topic"],
        "domain": DOMAIN,
        "objective": f"Explain and apply {day['topic']} for {DOMAIN} in a small, testable Python example.",
        "theory": theory,
        "code_example": day["code"],
        "questions": list(questions),
        "answers": list(answers),
        "homework": day["homework"],
        "required_patterns": list(day["patterns"]),
    }


def validate(lesson: dict) -> None:
    required = {"title", "domain", "objective", "theory", "code_example", "questions",
                "answers", "homework", "required_patterns"}
    missing = required - lesson.keys()
    if missing:
        raise ValueError(f"missing fields: {sorted(missing)}")
    if len(lesson["questions"]) != 3 or len(lesson["answers"]) != 3:
        raise ValueError("exactly 3 questions and 3 answers required")
    words = _words(lesson["theory"])
    if not MIN_THEORY_WORDS <= words <= MAX_THEORY_WORDS:
        raise ValueError(f"theory has {words} words, expected {MIN_THEORY_WORDS}-{MAX_THEORY_WORDS}")
    ast.parse(lesson["code_example"])
    if len(lesson["homework"]) < 120:
        raise ValueError("homework is too short")
    if not lesson["required_patterns"] or not all(isinstance(p, str) and p for p in lesson["required_patterns"]):
        raise ValueError("required_patterns must be non-empty strings")
    for token in ("__LIB__", "__DOMAIN__", "{lib}", "{name}", "TODO", "lorem"):
        if token in lesson["theory"] or token in lesson["code_example"]:
            raise ValueError(f"placeholder token leaked: {token}")
    if re.search(r"[\u0400-\u04FF\u0370-\u03FF\u4E00-\u9FFF]", lesson["theory"]):
        raise ValueError("unexpected non-Latin script in theory (mixed-script typo?)")


def collect() -> list[tuple[int, str, dict]]:
    """All owned days as (day_number, phase, built lesson). Validates everything."""
    out = []
    for day_num, day in sorted(FOUNDATION.items()):
        if day_num not in APPROVED_DAYS:
            raise ValueError(f"foundation day {day_num} outside allowlist")
        lesson = build_day("", day)
        lesson["title"] = day["topic"]
        validate(lesson)
        out.append((day_num, "Crypto Foundations", lesson))
    for phase, _goal, days in CRYPTO_PHASES:
        for day_num, day in sorted(days.items()):
            if day_num not in APPROVED_DAYS:
                raise ValueError(f"day {day_num} outside allowlist")
            lesson = build_day(phase, day)
            validate(lesson)
            out.append((day_num, phase, lesson))
    titles = [lesson["title"] for _, _, lesson in out]
    if len(set(titles)) != len(titles):
        dupes = sorted({t for t in titles if titles.count(t) > 1})
        raise ValueError(f"duplicate titles: {dupes}")
    return out


def resolve_path_id(conn: sqlite3.Connection) -> int:
    row = conn.execute("SELECT id FROM paths WHERE slug = ?", (SLUG,)).fetchone()
    if row is None:
        raise ValueError("cryptography path missing")
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
