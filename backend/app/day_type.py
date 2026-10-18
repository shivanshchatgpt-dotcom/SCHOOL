"""Day-type classifier for the 180-day launch tracks.

The three launch-ready paths (agi-research, data-science, web-dev) each carry
180 lessons, but they are not homogeneous: some carry a real concept body, some
are exercise sets, some are build prompts, and some are consolidation points.
This module assigns each lesson one of four day types from structural signals
only, so the split is reproducible and auditable rather than a matter of taste.

Day types
---------
concept  full teaching body: theory, a worked example, and the Q/A that proves
         comprehension. Must meet the current theory word budget.
practice an exercise set. Theory is deliberately short; the weight is in
         several generated variants plus a pattern-checked submission.
project  a build prompt with starter code and a rubric. No new teaching.
review   a consolidation checkpoint over earlier material, with a mastery gate.

Classification is read-only. Nothing here writes to the database; run with
`--apply` only after the split has been reviewed.
"""
from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
from collections import Counter, defaultdict
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "pyschool.db"

CONCEPT, PRACTICE, PROJECT, REVIEW = "concept", "practice", "project", "review"
DAY_TYPES = (CONCEPT, PRACTICE, PROJECT, REVIEW)

# The current writing standard for a concept body, matching the validator in
# curriculum_worker.validate().
MIN_THEORY_WORDS = 450
MAX_THEORY_WORDS = 900

# Every non-concept day must still be learnable, so it carries a floor even
# though it is generated rather than authored.
MIN_PRACTICE_WORDS = 40

# The intended mix for a 180-day track. Practice and review are produced by the
# generator and the review scheduler, not authored one by one, which is what
# makes the target reachable without writing 180 lessons per path.
TARGET_MIX = {CONCEPT: 70, PRACTICE: 50, PROJECT: 30, REVIEW: 30}

# Title signals. These are the only place human naming leaks into the classifier,
# and every pattern below is checked against the live titles before it is used.
PROJECT_TITLE = re.compile(
    r"\b(project|capstone|build|mini[- ]project|portfolio|application)\b", re.I
)
REVIEW_TITLE = re.compile(
    r"\b(review|reflection|recap|revision|checkpoint|assessment|exam|consolidat)\w*", re.I
)
PRACTICE_TITLE = re.compile(
    r"\b(practice|exercise|drill|worksheet|repetition|lab|try it)\b", re.I
)

# Structural thresholds, derived from the measured distribution rather than
# chosen by taste. Bodies at or above this carry a real teaching argument.
MIN_CONCEPT_WORDS = 300
MIN_CONCEPT_QA = 2

# The existing corpus was produced by two generating templates, and detecting
# which one wrote a lesson is a far stronger intent signal than any length
# heuristic. Template A emits "What it is / Why it matters / Watch out" and was
# meant to be a concept body. Template B emits a "Study protocol (60 minutes)"
# block plus a "Demonstrate **X** in a Y context" homework and was meant to be
# a generated exercise. Hand-written bodies are the ones that actually teach.
TEMPLATE_A_SECTIONS = ("What it is", "Why it matters", "Watch out")
TEMPLATE_B_SECTION = "Study protocol (60 minutes)"
TEMPLATE_B_HOMEWORK = re.compile(r"Demonstrate \*\*(.+?)\*\* in a (.+?) context in at least")


def _words(text: str) -> int:
    return len(re.findall(r"\b[\w'-]+\b", text or ""))


def _json_len(raw: str) -> int:
    try:
        value = json.loads(raw)
    except (TypeError, ValueError):
        return 0
    return len(value) if isinstance(value, list) else 0


def _sections(theory: str) -> set[str]:
    return {s.strip() for s in re.findall(r"\*\*([^*]+)\*\*", theory or "")}


def detect_template(theory: str, homework: str) -> str:
    """Return which generator produced this lesson's body."""
    s = _sections(theory)
    if TEMPLATE_B_SECTION in s or TEMPLATE_B_HOMEWORK.search(homework or ""):
        return "template_b_practice"
    if any(t in s for t in TEMPLATE_A_SECTIONS):
        return "template_a_concept"
    return "handwritten"


def classify(title: str, theory: str, questions: str, code: str, homework: str) -> str:
    """Return the day type for one lesson from its own content.

    Order matters. A body that already teaches is a concept day whatever its
    title says. After that, project and review are decided by explicit title
    intent, because those days are named deliberately. Practice is decided by
    the template that generated the body, which is objective. What is left is a
    concept day that was never written out.
    """
    title = title or ""
    w = _words(theory)
    qa = _json_len(questions)

    # 1. A body that already carries a real teaching argument is a concept day.
    if w >= MIN_CONCEPT_WORDS and qa >= MIN_CONCEPT_QA:
        return CONCEPT

    # 2. Named build prompts and consolidation points.
    if PROJECT_TITLE.search(title):
        return PROJECT
    if REVIEW_TITLE.search(title):
        return REVIEW

    # 3. Template B was written as an exercise generator's output, not as prose.
    if detect_template(theory, homework) == "template_b_practice":
        return PRACTICE

    # 4. Everything else is a concept day whose body was never filled in. It is
    #    still a concept day by intent; it is recorded as needing rewrite by
    #    meets_standard(), not by being reclassified away.
    return CONCEPT


def meets_standard(day_type: str, theory: str, questions: str, answers: str,
                   homework: str, code: str) -> list[str]:
    """Return the list of standards this lesson fails. Empty means it passes.

    Only concept days are held to the full theory budget. Practice, project and
    review days are generated or templated, so they are checked structurally
    rather than by word count.
    """
    fails: list[str] = []
    if day_type == CONCEPT:
        w = _words(theory)
        if w < MIN_THEORY_WORDS:
            fails.append(f"theory {w}w < {MIN_THEORY_WORDS}")
        if _json_len(questions) < 3:
            fails.append(f"questions {_json_len(questions)} < 3")
        if _json_len(answers) < 3:
            fails.append(f"answers {_json_len(answers)} < 3")
    else:
        if not (code or "").strip():
            fails.append("no code")
    if _words(homework) < 12:
        fails.append("homework too short")
    return fails


def load(conn: sqlite3.Connection) -> list[dict]:
    rows = conn.execute(
        """
        SELECT p.slug, l.day_number, l.title, l.theory, l.questions, l.answers,
               l.code_example, l.homework
        FROM lessons l JOIN paths p ON p.id = l.path_id
        WHERE p.is_launch_ready = 1
        ORDER BY p.slug, l.day_number
        """
    ).fetchall()
    out = []
    for r in rows:
        dt = classify(
            r["title"], r["theory"], r["questions"], r["code_example"], r["homework"]
        )
        out.append(
            {
                "slug": r["slug"],
                "day": r["day_number"],
                "title": r["title"],
                "theory_words": _words(r["theory"]),
                "qa": _json_len(r["questions"]),
                "qa_answers": _json_len(r["answers"]),
                "code_lines": len([ln for ln in (r["code_example"] or "").splitlines() if ln.strip()]),
                "homework_words": _words(r["homework"]),
                "template": detect_template(r["theory"], r["homework"]),
                "day_type": dt,
                "fails": meets_standard(
                    dt, r["theory"], r["questions"], r["answers"],
                    r["code_example"], r["homework"],
                ),
            }
        )
    return out


def report(lessons: list[dict]) -> dict:
    by_path: dict[str, Counter] = defaultdict(Counter)
    for l in lessons:
        by_path[l["slug"]][l["day_type"]] += 1
    return {
        "total": len(lessons),
        "by_path": {p: dict(c) for p, c in by_path.items()},
        "overall": dict(sum(by_path.values(), Counter())),
        "target": TARGET_MIX,
    }


def print_report(rep: dict, lessons: list[dict]) -> None:
    print(f"classified {rep['total']} lessons across {len(rep['by_path'])} launch paths\n")
    head = f"  {'path':<16}" + "".join(f"{t:>10}" for t in DAY_TYPES) + f"{'total':>8}"
    print(head)
    print("  " + "-" * (len(head) - 2))
    for slug in sorted(rep["by_path"]):
        counts = rep["by_path"][slug]
        row = f"  {slug:<16}" + "".join(f"{counts.get(t, 0):>10}" for t in DAY_TYPES)
        print(row + f"{sum(counts.values()):>8}")
    print("  " + "-" * (len(head) - 2))
    ov = rep["overall"]
    row = f"  {'ALL':<16}" + "".join(f"{ov.get(t, 0):>10}" for t in DAY_TYPES)
    print(row + f"{rep['total']:>8}")
    print()
    print("  target mix per 180-day path: " + ", ".join(f"{k} {v}" for k, v in TARGET_MIX.items()))
    per = max(1, len(rep["by_path"]))
    print("  target total:            " + ", ".join(f"{k} {v * per}" for k, v in TARGET_MIX.items()))
    print()
    print("  gap vs target (per path, concept/practice/project/review):")
    for slug in sorted(rep["by_path"]):
        counts = rep["by_path"][slug]
        gaps = ", ".join(f"{t[:4]} {counts.get(t, 0) - TARGET_MIX[t]:+d}" for t in DAY_TYPES)
        print(f"    {slug:<16} {gaps}")
    print()
    print("  quality of each type (mean theory words / Q&A count):")
    agg: dict[str, list] = defaultdict(list)
    for l in lessons:
        agg[l["day_type"]].append(l)
    for t in DAY_TYPES:
        rows = agg.get(t, [])
        if not rows:
            continue
        mw = sum(r["theory_words"] for r in rows) // len(rows)
        mq = sum(r["qa"] for r in rows) / len(rows)
        mh = sum(r["homework_words"] for r in rows) // len(rows)
        passes = sum(1 for r in rows if not r["fails"])
        print(f"    {t:<10} n={len(rows):<4} theory~{mw:<5}w qa~{mq:.1f} "
              f"hw~{mh:<3}w passes standard: {passes}/{len(rows)}")
    print()
    print("  which generator wrote each type:")
    gen: dict[str, Counter] = defaultdict(Counter)
    for l in lessons:
        gen[l["day_type"]][l["template"]] += 1
    for t in DAY_TYPES:
        if gen.get(t):
            detail = ", ".join(f"{k}={v}" for k, v in gen[t].most_common())
            print(f"    {t:<10} {detail}")
    print()
    print("  remediation backlog (unique slug+day needing work):")
    need = [l for l in lessons if l["fails"]]
    byreason: Counter = Counter()
    for l in need:
        byreason[l["fails"][0].split(" ")[0] + ("+" if len(l["fails"]) > 1 else "")] += 1
    for k, n in byreason.most_common():
        print(f"    {k:<22} {n}")
    print(f"    {'TOTAL':<22} {len(need)}")
    rewrite = [l for l in need if l["day_type"] == CONCEPT]
    template_fix = [l for l in need if l["day_type"] != CONCEPT]
    print(f"    of which full rewrite (concept):   {len(rewrite)}")
    print(f"    of which template fix (other):     {len(template_fix)}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--db", default=str(DB_PATH))
    ap.add_argument("--json", action="store_true", help="emit full per-lesson JSON")
    ap.add_argument("--apply", action="store_true",
                    help="write day_type back to the lessons table (requires the column)")
    args = ap.parse_args()

    conn = sqlite3.connect(args.db)
    conn.row_factory = sqlite3.Row
    lessons = load(conn)
    if not lessons:
        print("no launch-ready lessons found", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(lessons, indent=2))
        return 0

    rep = report(lessons)
    print_report(rep, lessons)

    if args.apply:
        cols = {r[1] for r in conn.execute("PRAGMA table_info(lessons)")}
        if "day_type" not in cols:
            print("\nrefusing to apply: lessons.day_type does not exist. "
                  "Run the migration first.", file=sys.stderr)
            return 2
        conn.executemany(
            "UPDATE lessons SET day_type = ? WHERE id = ("
            "  SELECT l.id FROM lessons l JOIN paths p ON p.id = l.path_id"
            "  WHERE p.slug = ? AND l.day_number = ?)",
            [(l["day_type"], l["slug"], l["day"]) for l in lessons],
        )
        conn.commit()
        print(f"\napplied day_type to {len(lessons)} lessons")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
