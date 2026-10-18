"""Apply generated practice days to a path's domain blocks.

Reads the audit's recommendation for each day in the domain range and, for the
days recommended `convert_practice`, replaces the thin stub with a generated
exercise: a short orientation body, a worked example drawn from the exercise
templates, a pattern-checked assignment, and a rubric.

Nothing is written unless --apply is passed. The applier is idempotent: a day
that already carries a generated body is left alone, so running twice produces
the same database. Before writing it verifies that every generated solution
executes, and after writing it re-reads the rows and diffs them.
"""
from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / ".books"))

from app.day_audit import audit  # noqa: E402
from app.exercise_templates import TEMPLATES  # noqa: E402
from app.exercise_gen import generate, ExecutionError, render_exercise_body  # noqa: E402

DB_PATH = Path(__file__).resolve().parent.parent / "pyschool.db"
SEED = 20260927

# Blocks that have exercise templates, and the order templates are cycled in.
BY_BLOCK: dict[str, list] = {}
for _t in TEMPLATES:
    BY_BLOCK.setdefault(_t.block, []).append(_t)

DOMAIN = "Data Science"


def _words(t: str) -> int:
    return len(re.findall(r"\b[\w'-]+\b", t or ""))


def is_generated(theory: str) -> bool:
    """A generated practice day is recognisable by its own body text."""
    return "This is a practice day" in (theory or "")


def build_practice_day(item: dict, domain: str) -> dict | None:
    """Return a ready-to-write practice lesson for one day, or None to skip."""
    block = item["block"]
    pool = BY_BLOCK.get(block)
    if not pool:
        return None
    tpl = pool[item["day"] % len(pool)]
    try:
        variants = generate(tpl, seed=SEED)
    except ExecutionError as err:
        print(f"  ! {tpl.id} day {item['day']}: {err}")
        return None

    first = variants[0]
    theory_lines = [
        f"**Today: {first.skill}**",
        "",
        f"This is a practice day inside the **{block}** block of the {domain} programme. "
        "It introduces nothing new; it builds fluency with a skill you already have.",
        "",
        render_exercise_body(variants),
        "",
        "**The exercise set**",
        f"Run all {len(variants)} variants below. Each one is the same problem with different "
        "values, so a value that happens to work in the first is not proof the second will. "
        "Predict each output before running it.",
        "",
    ]
    for i, v in enumerate(variants, 1):
        theory_lines += [
            f"**Variant {i}** — drawn {v.draw}",
            "",
            v.prompt,
            "",
        ]
    theory_lines += [
        "**Common mistakes**",
        "- Copying the worked example instead of writing your own version.",
        "- Hard-coding the value you happened to test with, so a second variant fails.",
        "- Printing the intermediate list rather than the transformed result the prompt asks for.",
    ]
    theory = "\n".join(theory_lines)

    return {
        "day": item["day"],
        "title": f"Practice: {first.skill}",
        "theory": theory,
        "code_example": first.solution,
        "questions": [
            f"What does {first.skill} let you express that hard-coding the answer would not?",
            "Which line in your solution is doing the real work, and what breaks if you remove it?",
            "Your second variant has different values. Which parts of your logic did you assume?",
        ],
        "answers": [
            f"{first.skill} is a rule you can apply to any input of that shape, which is the difference between solving one case and being able to solve the next one.",
            "The line that performs the transformation itself, because the surrounding lines only move data in and out; removing it leaves the plumbing intact and the result wrong, which is how you can tell it was the real work.",
            "The usual assumptions are a fixed length, a sorted input, a value that happens to be in range, or a single element. A second variant with different values exposes whichever of those you relied on.",
        ],
        "homework": first.prompt,
        "required_patterns": list(first.required_patterns),
        "rubric": " ".join(first.rubric),
        "template_id": first.template_id,
        "variants": len(variants),
    }


def plan(conn: sqlite3.Connection, slug: str) -> list[dict]:
    items = audit(conn, slug)
    out = []
    for item in items:
        if item["recommended"] != "convert_practice":
            continue
        built = build_practice_day(item, DOMAIN)
        if built is None:
            continue
        built["slug"] = slug
        out.append(built)
    return out


def report(conn: sqlite3.Connection, plans: list[dict]) -> None:
    kinds = Counter()
    for p in plans:
        kinds[p["template_id"]] += 1
    print(f"  would write {len(plans)} practice days across {len(kinds)} templates")
    for tid, n in sorted(kinds.items(), key=lambda kv: -kv[1]):
        print(f"    {tid:<32} {n} days")
    tw = [_words(p['theory']) for p in plans]
    print(f"  theory words: min {min(tw)} max {max(tw)} avg {sum(tw)//len(tw)}")
    hw = [len(p['homework']) for p in plans]
    print(f"  homework chars: min {min(hw)} max {max(hw)}")


def apply(conn: sqlite3.Connection, plans: list[dict], *, force: bool) -> dict:
    written = skipped = 0
    for p in plans:
        row = conn.execute(
            """SELECT l.id, l.theory FROM lessons l JOIN paths p ON p.id = l.path_id
               WHERE p.slug = ? AND l.day_number = ?""",
            (p["slug"], p["day"]),
        ).fetchone()
        if row is None:
            skipped += 1
            continue
        if is_generated(row["theory"]) and not force:
            skipped += 1
            continue
        conn.execute(
            """UPDATE lessons SET title = ?, theory = ?, code_example = ?,
               questions = ?, answers = ?, homework = ? WHERE id = ?""",
            (
                p["title"], p["theory"], p["code_example"],
                json.dumps(p["questions"]), json.dumps(p["answers"]),
                p["homework"], row["id"],
            ),
        )
        a = conn.execute("SELECT id FROM assignments WHERE lesson_id = ?", (row["id"],)).fetchone()
        if a is None:
            conn.execute(
                """INSERT INTO assignments (lesson_id, prompt, required_patterns, min_lines, rubric)
                   VALUES (?, ?, ?, 4, ?)""",
                (row["id"], p["homework"], json.dumps(p["required_patterns"]), p["rubric"]),
            )
        else:
            conn.execute(
                "UPDATE assignments SET prompt = ?, required_patterns = ?, min_lines = 4, rubric = ? WHERE id = ?",
                (p["homework"], json.dumps(p["required_patterns"]), p["rubric"], a["id"]),
            )
        written += 1
    conn.commit()
    return {"written": written, "skipped": skipped}


def verify(conn: sqlite3.Connection, slug: str, plans: list[dict]) -> dict:
    """Re-read what was written and confirm it is what was intended."""
    ok = bad = 0
    problems: list[str] = []
    for p in plans:
        r = conn.execute(
            """SELECT l.*, a.required_patterns FROM lessons l JOIN paths p ON p.id = l.path_id
               LEFT JOIN assignments a ON a.lesson_id = l.id
               WHERE p.slug = ? AND l.day_number = ?""",
            (p["slug"], p["day"]),
        ).fetchone()
        if r is None:
            bad += 1
            problems.append(f"d{p['day']} missing")
            continue
        issues = []
        if not is_generated(r["theory"]):
            issues.append("body is not a generated practice day")
        try:
            q = json.loads(r["questions"])
            a = json.loads(r["answers"])
            if len(q) != 3 or len(a) != 3:
                issues.append(f"q/a {len(q)}/{len(a)}")
        except Exception:
            issues.append("questions not valid json")
        if r["required_patterns"] is None:
            issues.append("no assignment row")
        else:
            try:
                pats = json.loads(r["required_patterns"])
                if not all(isinstance(x, str) and x for x in pats):
                    issues.append("bad required_patterns")
            except Exception:
                issues.append("required_patterns not valid json")
        if not (r["code_example"] or "").strip():
            issues.append("no code example")
        if issues:
            bad += 1
            problems.append(f"d{p['day']}: {'; '.join(issues)}")
        else:
            ok += 1
    return {"ok": ok, "bad": bad, "problems": problems}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--db", default=str(DB_PATH))
    ap.add_argument("--path", default="data-science")
    ap.add_argument("--apply", action="store_true", help="write to the database")
    ap.add_argument("--force", action="store_true", help="rewrite even already-generated days")
    ap.add_argument("--dump", metavar="FILE", help="write the planned lessons as JSON")
    args = ap.parse_args()

    conn = sqlite3.connect(args.db)
    conn.row_factory = sqlite3.Row

    plans = plan(conn, args.path)
    if not plans:
        print("nothing to do")
        return 0

    print(f"=== plan for {args.path} ===")
    report(conn, plans)

    if args.dump:
        Path(args.dump).write_text(json.dumps(plans, indent=2))
        print(f"  plan written to {args.dump}")

    if not args.apply:
        print("\nDRY RUN. pass --apply to write.")
        return 0

    print("\n=== applying ===")
    res = apply(conn, plans, force=args.force)
    print(f"  written {res['written']}, skipped {res['skipped']}")

    print("=== verify ===")
    v = verify(conn, args.path, plans)
    print(f"  ok {v['ok']}, bad {v['bad']}")
    for p in v["problems"][:10]:
        print(f"    {p}")

    print("=== idempotency: second run must write 0 ===")
    again = plan(conn, args.path)
    res2 = apply(conn, again, force=False)
    print(f"  written {res2['written']}, skipped {res2['skipped']}")
    if res2["written"] != 0:
        print("  NOT IDEMPOTENT")
        return 3
    return 0 if v["bad"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
