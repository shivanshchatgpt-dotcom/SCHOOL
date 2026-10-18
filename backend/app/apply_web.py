"""Apply the web-development domain templates to the web-dev path.

The five domain blocks cover seventy-five days of a single path, so this applier is
narrower than the shared one: it takes one slug and refuses to write outside the
blocks it knows. Nothing is written unless --apply is passed, every stored
solution is executed again after writing, and a second run must change nothing.
"""
from __future__ import annotations

import argparse
import io
import json
import re
import sqlite3
import sys
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.exercise_gen import generate, render_exercise_body  # noqa: E402
from app.web_templates import WEB_BLOCKS  # noqa: E402

DB_PATH = Path(__file__).resolve().parent.parent / "pyschool.db"
SLUG = "web-dev"
DOMAIN = "Web Development"
GENERATED_MARKER = "This is a practice day"
MIN_THEORY_WORDS = 200


def _words(t: str) -> int:
    return len(re.findall(r"\b[\w'-]+\b", t or ""))


def build_day(tpl) -> dict:
    variants = generate(tpl, seed=20260927)
    first = variants[0]
    lines = [
        f"**Today: {first.skill}**",
        "",
        f"This is a practice day inside the **{tpl.block}** block of the {DOMAIN} programme. "
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
        "- Validating only the happy path, so the failure branch is never exercised.",
    ]
    return {
        "skill": first.skill, "template_id": tpl.id, "variants": len(variants),
        "day": tpl.day, "block": tpl.block,
        "title": f"Practice: {first.skill}",
        "theory": "\n".join(lines),
        "code_example": first.solution,
        "questions": [
            f"What does {first.skill} let you express that hard-coding the answer would not?",
            "Which part of your solution handles the failure case, and what happens if you omit it?",
            "Your second variant has different values. Which assumption in your logic did it break?",
        ],
        "answers": [
            f"{first.skill} is a rule you can apply to any input of that shape, which is the "
            "difference between solving one case and being able to solve the next one.",
            "The branch that rejects the bad input, because without it the program either crashes or "
            "silently accepts something it should not, and both are worse than a clear refusal.",
            "The usual assumptions are a fixed length, a value in range, or a single element. A "
            "second variant with different values exposes whichever of those you relied on.",
        ],
        "homework": first.prompt,
        "required_patterns": list(first.required_patterns),
        "rubric": " ".join(tpl.rubric),
    }


def plan(conn: sqlite3.Connection, slug: str) -> list[dict]:
    out = []
    for tpl in WEB_BLOCKS:
        row = conn.execute(
            "SELECT l.id FROM lessons l JOIN paths p ON p.id = l.path_id "
            "WHERE p.slug = ? AND l.day_number = ?", (slug, tpl.day)).fetchone()
        if row is None:
            print(f"  ! no day {tpl.day} for {slug}, skipping")
            continue
        day = build_day(tpl)
        day["lesson_id"] = row["id"]
        out.append(day)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--db", default=str(DB_PATH))
    ap.add_argument("--slug", default=SLUG)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--dump", metavar="FILE")
    args = ap.parse_args()

    conn = sqlite3.connect(args.db)
    conn.row_factory = sqlite3.Row
    plans = plan(conn, args.slug)
    print(f"\nplanned {len(plans)} day-slots for {args.slug}")
    from collections import Counter
    for block, n in Counter(p["block"] for p in plans).most_common():
        print(f"   {block:<28}{n}")
    tw = [_words(p["theory"]) for p in plans]
    print(f"theory words: min {min(tw)} max {max(tw)} avg {sum(tw)//len(tw)}")
    print(f"variants per day: min {min(p['variants'] for p in plans)} "
          f"max {max(p['variants'] for p in plans)}")

    if args.dump:
        Path(args.dump).write_text(json.dumps(plans, indent=2))
        print(f"plan written to {args.dump}")
    if not args.apply:
        print("\nDRY RUN. pass --apply to write.")
        return 0

    n_before = conn.execute("SELECT COUNT(*) FROM lessons").fetchone()[0]
    print("\n=== applying ===")
    written = skipped = 0
    for p in plans:
        row = conn.execute("SELECT theory FROM lessons WHERE id = ?", (p["lesson_id"],)).fetchone()
        if row and GENERATED_MARKER in (row["theory"] or ""):
            skipped += 1
            continue
        conn.execute(
            """UPDATE lessons SET title = ?, theory = ?, code_example = ?,
               questions = ?, answers = ?, homework = ?, day_type = 'practice',
               status = 'active', status_reason = ?, status_note = '' WHERE id = ?""",
            (p["title"], p["theory"], p["code_example"], json.dumps(p["questions"]),
             json.dumps(p["answers"]), p["homework"],
             f"generated from {p['template_id']} (day {p['day']}, {p['block']})", p["lesson_id"]))
        a = conn.execute("SELECT id FROM assignments WHERE lesson_id = ?", (p["lesson_id"],)).fetchone()
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

    print("\n=== verify: re-read and execute every stored solution ===")
    ok = bad = 0
    problems = []
    for p in plans:
        r = conn.execute(
            """SELECT l.theory, l.questions, l.answers, l.code_example, l.homework,
                      l.day_type, l.status, a.required_patterns
               FROM lessons l LEFT JOIN assignments a ON a.lesson_id = l.id
               WHERE l.id = ?""", (p["lesson_id"],)).fetchone()
        issues = []
        if GENERATED_MARKER not in (r["theory"] or ""):
            issues.append("not a generated day")
        if r["day_type"] != "practice":
            issues.append(f"day_type={r['day_type']}")
        if r["status"] != "active":
            issues.append(f"status={r['status']}")
        if _words(r["theory"]) < MIN_THEORY_WORDS:
            issues.append(f"theory {_words(r['theory'])}w")
        try:
            if len(json.loads(r["questions"])) != 3 or len(json.loads(r["answers"])) != 3:
                issues.append("q/a count")
            if not all(isinstance(x, str) and x for x in json.loads(r["required_patterns"] or "[]")):
                issues.append("patterns")
        except Exception:
            issues.append("json")
        if len(r["homework"] or "") < 120:
            issues.append("homework short")
        try:
            with redirect_stdout(io.StringIO()):
                exec(compile(r["code_example"], f"d{p['day']}", "exec"), {})
        except Exception as err:
            issues.append(f"code {type(err).__name__}: {str(err)[:40]}")
        if issues:
            bad += 1
            problems.append(f"d{p['day']}: {'; '.join(issues)}")
        else:
            ok += 1
    print(f"verified ok {ok}, bad {bad}")
    for pr in problems[:10]:
        print("   ", pr)

    print("\n=== idempotency: second run must write 0 ===")
    again = plan(conn, args.slug)
    w2 = 0
    for p in again:
        row = conn.execute("SELECT theory FROM lessons WHERE id = ?", (p["lesson_id"],)).fetchone()
        if row and GENERATED_MARKER not in (row["theory"] or ""):
            w2 += 1
    print(f"days that would be written again: {w2}  "
          f"({'IDEMPOTENT' if w2 == 0 else 'NOT IDEMPOTENT'})")

    n_after = conn.execute("SELECT COUNT(*) FROM lessons").fetchone()[0]
    print(f"\nlessons: {n_before} -> {n_after} ({'unchanged' if n_before == n_after else 'CHANGED'})")
    return 0 if (bad == 0 and w2 == 0) else 1


if __name__ == "__main__":
    raise SystemExit(main())
