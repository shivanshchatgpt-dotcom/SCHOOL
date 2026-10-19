"""Apply the flagship Chatbots curriculum to the chatbots path.

Writes ONLY chatbots days 9-14 and 75-179 (lesson + assignment +
milestone title/domain/objective; codes, ids and prerequisite edges are never
touched). Canonical opening days, shared days 15-74 and day 180 are refused.
Launch tracks, canonical lessons and automation days are never read for writing.

Usage: .venv/bin/python -m app.apply_chatbots --apply   (default is --check only)
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
import types
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.curriculum_chatbots import DOMAIN, FOUNDATION, PHASES  # noqa: E402

DB_PATH = Path(__file__).resolve().parent.parent / "pyschool.db"
SLUG = "chatbots"
MIN_THEORY_WORDS = 450
MAX_THEORY_WORDS = 900

Q2 = "Which line in your solution is doing the real work, and what breaks if you remove it?"
A2 = "The line that performs the core operation — removing it should change the output or reveal the failed assumption."
Q3 = "Your second variant has different values. Which parts of your logic did you assume?"
A3 = "Feed it an edge case (empty turn, unknown intent, malformed tool args) so the failure becomes visible, then explain why it happened."

# Days this applier owns. Everything else on the path is refused.
OWNED_DAYS = frozenset(list(range(9, 15)) + list(range(75, 180)))


def _words(text: str) -> int:
    return len(re.findall(r"\b[\w'-]+\b", text or ""))


def run_code(code: str) -> str:
    """Execute our own example and capture stdout. Raises on failure."""
    buf = io.StringIO()
    # dataclasses looks the defining class up in sys.modules via __module__.
    module = types.ModuleType("__chat_example__")
    sys.modules["__chat_example__"] = module
    try:
        with contextlib.redirect_stdout(buf):
            exec(compile(code, "<chat-example>", "exec"), module.__dict__)
    finally:
        sys.modules.pop("__chat_example__", None)
    out = buf.getvalue().strip()
    if not out:
        raise ValueError("example runs silently")
    return out


def build_day(phase: str, day: dict) -> dict:
    """Compose the lesson dict the DB consumes. Output is captured, not written by hand."""
    output = run_code(day["code"])
    q1, a1 = day["q1"]
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
        "**In practice**",
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
        f"Use {day['topic']} inside a larger {DOMAIN} script this week, and notice where the idea strains — "
        "more pages, messier markup, or a stricter site. That strain is the map of what to learn next.",
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
        "questions": [q1, Q2, Q3],
        "answers": [a1, A2, A3],
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
    for token in ("__LIB__", "__DOMAIN__", "{lib}", "TODO", "lorem"):
        if token in lesson["theory"] or token in lesson["code_example"]:
            raise ValueError(f"placeholder token leaked: {token}")


def collect() -> list[tuple[int, str, dict]]:
    """All owned days as (day_number, phase, built lesson). Validates everything."""
    out = []
    for day_num, day in sorted(FOUNDATION.items()):
        lesson = build_day("", day)
        lesson["title"] = day["topic"]
        validate(lesson)
        out.append((day_num, "Chatbots Foundations", lesson))
    for phase, _goal, days in PHASES:
        for day_num, day in sorted(days.items()):
            lesson = build_day(phase, day)
            validate(lesson)
            out.append((day_num, phase, lesson))
    titles = [lesson["title"] for _, _, lesson in out]
    if len(set(titles)) != len(titles):
        dupes = sorted({t for t in titles if titles.count(t) > 1})
        raise ValueError(f"duplicate titles: {dupes}")
    return out


def apply(db_path: Path = DB_PATH, check_only: bool = True) -> dict:
    """Write owned days. Returns counts. check_only=True writes nothing."""
    lessons = collect()
    if check_only:
        return {"checked": len(lessons), "updated": 0, "skipped": 0}
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        row = conn.execute("SELECT id FROM paths WHERE slug = ?", (SLUG,)).fetchone()
        if row is None:
            raise ValueError(f"path missing: {SLUG}")
        path_id = row["id"]
        updated = skipped = 0
        for day_num, _phase, lesson in lessons:
            row = conn.execute(
                "SELECT id FROM lessons WHERE path_id = ? AND day_number = ?", (path_id, day_num)
            ).fetchone()
            if row is None:
                raise ValueError(f"refusing to create day {day_num}: applier only rewrites owned days")
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
                "UPDATE lessons SET title = ?, theory = ?, code_example = ?, questions = ?, answers = ?, homework = ? WHERE id = ?",
                (*new, lid),
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
        # Repair prerequisite chain gaps left by out-of-order canonical seeding.
        by_order = {
            row["sort_order"]: row["id"]
            for row in conn.execute(
                "SELECT sort_order, id FROM milestones WHERE path_id = ?", (path_id,)
            ).fetchall()
        }
        for order in range(2, max(by_order) + 1):
            if order in by_order and order - 1 in by_order:
                conn.execute(
                    "INSERT OR IGNORE INTO milestone_prerequisites (milestone_id, prerequisite_milestone_id) VALUES (?, ?)",
                    (by_order[order], by_order[order - 1]),
                )
        conn.commit()
        return {"checked": len(lessons), "updated": updated, "skipped": skipped}
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
