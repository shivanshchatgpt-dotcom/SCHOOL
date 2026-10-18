"""Apply the shared-block exercise templates to every path that has those days.

The four shared blocks are byte-identical across the launch paths, so one
template per day fills that day everywhere. Sixty templates therefore cover a
hundred and eighty day-slots, and the same generated day appearing in three paths
is a feature: the paths differ in their domain blocks, not in their Python.

Nothing is written unless --apply is passed. The applier is idempotent, refuses
to touch a day that is not one of the four shared blocks, and re-reads every row
after writing so the result is checked rather than assumed.
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

from app.exercise_gen import generate, render_exercise_body  # noqa: E402
from app.exercise_templates_shared import (  # noqa: E402
    ALGORITHMS_AND_MATH, CORE_PYTHON, PRACTICAL_PYTHON, SOFTWARE_ENGINEERING,
)

DB_PATH = Path(__file__).resolve().parent.parent / "pyschool.db"
SEED = 20260927
DOMAINS = {
    "agi-research": "AI Research",
    "data-science": "Data Science",
    "web-dev": "Web Development",
}
SHARED = CORE_PYTHON + PRACTICAL_PYTHON + SOFTWARE_ENGINEERING + ALGORITHMS_AND_MATH
GENERATED_MARKER = "This is a practice day"


def _words(t: str) -> int:
    return len(re.findall(r"\b[\w'-]+\b", t or ""))


def build_day(tpl, domain: str) -> dict:
    variants = generate(tpl, seed=SEED)
    first = variants[0]
    lines = [
        f"**Today: {first.skill}**",
        "",
        f"This is a practice day inside the **{tpl.block}** block of the {domain} programme. "
        "It introduces nothing new; it builds fluency with a skill you already have.",
        "",
        render_exercise_body(variants),
        "",
        "**The exercise set**",
        f"Run all {len(variants)} variants below. Each is the same problem with different values, "
        "so a value that happens to work in the first is not proof the second will. Predict each "
        "output before running it.",
        "",
    ]
    for i, v in enumerate(variants, 1):
        lines += [f"**Variant {i}**", "", v.prompt, ""]
    lines += [
        "**Common mistakes**",
        "- Copying the worked example instead of writing your own version.",
        "- Hard-coding the value you happened to test with, so a second variant fails.",
        "- Handling the error case in a way the prompt does not ask for, which changes what the "
        "program prints on the failure path.",
    ]
    return {
        "skill": first.skill,
        "template_id": tpl.id,
        "variants": len(variants),
        "title": f"Practice: {first.skill}",
        "theory": "\n".join(lines),
        "code_example": first.solution,
        "questions": [
            f"What does {first.skill} let you express that hard-coding the answer would not?",
            "Which line in your solution is doing the real work, and what breaks if you remove it?",
            "Your second variant has different values. Which parts of your logic did you assume?",
        ],
        "answers": [
            f"{first.skill} is a rule you can apply to any input of that shape, which is the "
            "difference between solving one case and being able to solve the next one.",
            "The line that performs the transformation itself, because the surrounding lines only "
            "move data in and out; removing it leaves the plumbing intact and the result wrong.",
            "The usual assumptions are a fixed length, a sorted input, a value that happens to be in "
            "range, or a single element. A second variant with different values exposes whichever of "
            "those you relied on.",
        ],
        "homework": first.prompt,
        "required_patterns": list(first.required_patterns),
        "rubric": " ".join(tpl.rubric),
    }


def plan(conn: sqlite3.Connection, paths: list[str]) -> list[dict]:
    out = []
    for tpl in SHARED:
        for slug in paths:
            row = conn.execute(
                "SELECT l.id, l.theory FROM lessons l JOIN paths p ON p.id = l.path_id "
                "WHERE p.slug = ? AND l.day_number = ?",
                (slug, tpl.day),
            ).fetchone()
            if row is None:
                continue
            day = build_day(tpl, DOMAINS.get(slug, slug))
            day.update({"slug": slug, "day": tpl.day, "block": tpl.block, "lesson_id": row["id"]})
            out.append(day)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--db", default=str(DB_PATH))
    ap.add_argument("--paths", nargs="*", default=list(DOMAINS))
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--dump", metavar="FILE")
    args = ap.parse_args()

    conn = sqlite3.connect(args.db)
    conn.row_factory = sqlite3.Row
    plans = plan(conn, args.paths)
    if not plans:
        print("nothing to plan")
        return 0

    per_block = Counter(p["block"] for p in plans)
    per_path = Counter(p["slug"] for p in plans)
    tw = [_words(p["theory"]) for p in plans]
    print(f"planned {len(plans)} day-slots across {len(per_block)} blocks")
    for b, n in per_block.most_common():
        print(f"   {b:<24}{n}")
    for s, n in per_path.most_common():
        print(f"   {s:<24}{n}")
    print(f"theory words: min {min(tw)} max {max(tw)} avg {sum(tw)//len(tw)}")
    print(f"variants per day: min {min(p['variants'] for p in plans)} "
          f"max {max(p['variants'] for p in plans)}")

    if args.dump:
        Path(args.dump).write_text(json.dumps(plans, indent=2))
        print(f"plan written to {args.dump}")

    if not args.apply:
        print("\nDRY RUN. pass --apply to write.")
        return 0

    print("\n=== applying ===")
    written = skipped = 0
    for p in plans:
        row = conn.execute("SELECT theory FROM lessons WHERE id = ?", (p["lesson_id"],)).fetchone()
        if row and GENERATED_MARKER in (row["theory"] or ""):
            skipped += 1
            continue
        conn.execute(
            """UPDATE lessons SET title = ?, theory = ?, code_example = ?,
               questions = ?, answers = ?, homework = ?,
               day_type = 'practice', status = 'active', status_reason = ?,
               status_note = '' WHERE id = ?""",
            (p["title"], p["theory"], p["code_example"],
             json.dumps(p["questions"]), json.dumps(p["answers"]), p["homework"],
             f"generated from {p['template_id']} (day {p['day']}, {p['block']})",
             p["lesson_id"]),
        )
        a = conn.execute("SELECT id FROM assignments WHERE lesson_id = ?",
                         (p["lesson_id"],)).fetchone()
        if a is None:
            conn.execute(
                """INSERT INTO assignments (lesson_id, prompt, required_patterns, min_lines, rubric)
                   VALUES (?, ?, ?, 4, ?)""",
                (p["lesson_id"], p["homework"], json.dumps(p["required_patterns"]), p["rubric"]))
        else:
            conn.execute(
                "UPDATE assignments SET prompt = ?, required_patterns = ?, min_lines = 4, rubric = ? WHERE id = ?",
                (p["homework"], json.dumps(p["required_patterns"]), p["rubric"], a["id"]))
        written += 1
    conn.commit()
    print(f"written {written}, skipped {skipped}")

    print("\n=== verify: re-read and execute every stored code example ===")
    ok = bad = 0
    problems = []
    for p in plans:
        r = conn.execute(
            """SELECT l.*, a.required_patterns FROM lessons l
               LEFT JOIN assignments a ON a.lesson_id = l.id WHERE l.id = ?""",
            (p["lesson_id"],)).fetchone()
        issues = []
        if GENERATED_MARKER not in (r["theory"] or ""):
            issues.append("not a generated day")
        if r["day_type"] != "practice":
            issues.append(f"day_type={r['day_type']}")
        if r["status"] != "active":
            issues.append(f"status={r['status']}")
        try:
            if len(json.loads(r["questions"])) != 3 or len(json.loads(r["answers"])) != 3:
                issues.append("q/a count")
        except Exception:
            issues.append("q/a not json")
        try:
            if not all(isinstance(x, str) and x for x in json.loads(r["required_patterns"] or "[]")):
                issues.append("patterns")
        except Exception:
            issues.append("patterns not json")
        if len(r["homework"] or "") < 120:
            issues.append("homework short")
        try:
            import io
            from contextlib import redirect_stdout
            with redirect_stdout(io.StringIO()):
                exec(compile(r["code_example"], f"d{r['day_number']}", "exec"), {})
        except Exception as e:
            issues.append(f"code {type(e).__name__}")
        if issues:
            bad += 1
            problems.append(f"{p['slug']} d{p['day']}: {'; '.join(issues)}")
        else:
            ok += 1
    print(f"verified ok {ok}, bad {bad}")
    for pr in problems[:10]:
        print("   ", pr)

    print("\n=== idempotency: second run must write 0 ===")
    again = plan(conn, args.paths)
    w2 = 0
    for p in again:
        row = conn.execute("SELECT theory FROM lessons WHERE id = ?", (p["lesson_id"],)).fetchone()
        if row and GENERATED_MARKER not in (row["theory"] or ""):
            w2 += 1
    print(f"days that would be written again: {w2}  ({'IDEMPOTENT' if w2 == 0 else 'NOT IDEMPOTENT'})")

    n = conn.execute("SELECT COUNT(*) FROM lessons").fetchone()[0]
    print(f"\nlessons: {n}  ({'unchanged' if n == 705 else 'CHANGED!'})")
    return 0 if (bad == 0 and w2 == 0) else 1


if __name__ == "__main__":
    raise SystemExit(main())
