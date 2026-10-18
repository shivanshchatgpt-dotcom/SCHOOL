"""Audit the d75-149 domain blocks and recommend a treatment per day.

The launch tracks' domain blocks are not homogeneous. Inside one block some days
introduce an idea the student has not met, and other days take a core skill and
apply it to that domain. The first kind needs an authored body; the second is
better served by a generated exercise, because the student is not learning a new
concept, they are building fluency with one they already have.

This module produces that judgement as a machine-readable inventory so it can be
reviewed before anything is rewritten. It reads only; it writes nothing.
"""
from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / ".books"))
from app.day_type import classify, detect_template, _words  # noqa: E402

DB_PATH = Path(__file__).resolve().parent.parent / "pyschool.db"

DOMAIN_RANGE = (75, 149)

# Skills the canonical library already teaches. A day whose title matches one of
# these is applying something the student has met, so it converts to practice
# rather than demanding a new authored body.
CORE_SKILLS = [
    r"csv\b", r"column", r"row", r"filter", r"missing", r"duplicat", r"data type",
    r"group", r"merg", r"datetime", r"validat", r"reproducib", r"ethics",
    r"select", r"report", r"sort", r"statistic", r"mean", r"median", r"variance",
    r"standard deviation", r"distribution", r"sampling", r"probabilit",
    r"correlation", r"confound", r"hypothes", r"confidence", r"a/b", r"ab test",
    r"outlier", r"skew", r"chart", r"plot", r"line chart", r"bar chart",
    r"histogram", r"scatter", r"subplot", r"label", r"legend", r"color",
    r"accessib", r"seaborn", r"dashboard", r"narrative", r"feature", r"label",
    r"split", r"regression", r"logistic", r"neighbour", r"neighbor", r"tree",
    r"forest", r"scal", r"pipeline", r"cross-valid", r"hyperparameter",
    r"overfit", r"explainab", r"metric", r"precision", r"recall", r"leakage",
    r"bias", r"error analysis", r"saving", r"loading", r"\bapi\b", r"version",
    r"monitor", r"stakeholder", r"portfolio", r"product",
    # scientific-python vocabulary the canonical library genuinely covers
    r"numpy", r"array", r"shape", r"vector", r"matrix", r"broadcast",
    r"pandas", r"table", r"tensor", r"notebook", r"seed", r"feature engineer",
    r"baseline", r"aggregation", r"indexing", r"slicing", r"reshap",
    r"concatenat", r"masking", r"ufunc",
    # web and infrastructure vocabulary
    r"database", r"sql", r"query", r"endpoint", r"route", r"middleware",
    r"auth", r"request", r"response", r"template", r"\bcss\b", r"\bhtml\b",
    r"\bdom\b", r"event", r"component", r"state", r"fetch", r"async",
    r"await", r"cache", r"deploy", r"server", r"client", r"session", r"cookie",
    r"static", r"schema", r"index", r"transaction", r"migration",
]

CANONICAL_INDEX: list[tuple[str, set[str]]] = []

CORE_RE = re.compile("|".join(CORE_SKILLS), re.I)

PROJECT_TITLE = re.compile(r"\b(project|capstone|portfolio|application)\b", re.I)
REVIEW_TITLE = re.compile(r"\b(review|reflection|recap|revision|checkpoint)\w*", re.I)

STOP = {
    "as", "and", "the", "of", "a", "an", "to", "in", "for", "with", "vs", "by",
    "at", "on", "or", "from", "into", "is", "are", "be", "its", "it",
}


def _tokens(text: str) -> set[str]:
    return {t for t in re.findall(r"[a-z0-9]+", (text or "").lower()) if t not in STOP and len(t) > 2}


def _canonical_index() -> list[tuple[str, set[str]]]:
    """Canonical topics as (id, meaningful name tokens), for objective matching."""
    from canonical_topics import all_topics

    out = []
    for tid, rec in all_topics().items():
        label = tid.split(":", 1)[-1]
        out.append((tid, _tokens(label)))
    return out


def match_canonical(title: str, index: list[tuple[str, set[str]]]) -> tuple[str, float]:
    """Return the best canonical topic covering this day, and its score.

    Score is token overlap between the day's skill title and the topic's name,
    so the match is explainable rather than a hidden heuristic. A score of zero
    means the corpus genuinely has nothing for this day, which is a gap worth
    reporting rather than a reason to guess.
    """
    day = _tokens(title)
    best, best_score = "", 0.0
    for tid, toks in index:
        if not toks:
            continue
        overlap = day & toks
        if not overlap:
            continue
        score = len(overlap) / len(day | toks)
        if score > best_score:
            best, best_score = tid, score
    return best, best_score


def recommend(title: str, theory: str, homework: str, current: str) -> tuple[str, str, str]:
    """Return (treatment, reason, canonical_match) for one day.

    The rule is objective on purpose. A day converts to practice only when the
    corpus already has something that covers it, either a canonical topic or a
    core skill the exercise templates target. Anything else is a real gap and is
    reported as needing an authored body, rather than being guessed at.
    """
    title = title or ""
    if PROJECT_TITLE.search(title):
        return "keep_project", "title declares a build prompt", ""
    if REVIEW_TITLE.search(title):
        return "keep_review", "title declares a consolidation point", ""

    word_count = _words(theory)
    if word_count >= 300:
        return "keep_concept", f"already carries a body ({word_count} words)", ""

    tid, score = match_canonical(title, CANONICAL_INDEX)
    if score >= 0.5:
        return (
            "convert_practice",
            f"corpus already covers this: {tid} (overlap {score:.2f})",
            tid,
        )
    if CORE_RE.search(title):
        return (
            "convert_practice",
            f"applies a core skill with a generator template: {title.split(':')[-1].strip()}",
            tid,
        )
    return (
        "rewrite_new",
        f"corpus gap: no canonical topic matches (best {tid or 'none'} at {score:.2f})",
        tid,
    )


def audit(conn: sqlite3.Connection, slug: str) -> list[dict]:
    rows = conn.execute(
        """
        SELECT l.day_number, l.title, l.theory, l.questions, l.answers,
               l.code_example, l.homework
        FROM lessons l JOIN paths p ON p.id = l.path_id
        WHERE p.slug = ? AND l.day_number BETWEEN ? AND ?
        ORDER BY l.day_number
        """,
        (slug, *DOMAIN_RANGE),
    ).fetchall()

    out = []
    global CANONICAL_INDEX
    if not CANONICAL_INDEX:
        CANONICAL_INDEX = _canonical_index()
    for r in rows:
        current = classify(r["title"], r["theory"], r["questions"], r["code_example"], r["homework"])
        treatment, reason, match = recommend(r["title"], r["theory"], r["homework"], current)
        out.append(
            {
                "slug": slug,
                "day": r["day_number"],
                "title": r["title"],
                "block": r["title"].split(":")[0] or "uncategorised",
                "current_day_type": current,
                "template": detect_template(r["theory"], r["homework"]),
                "theory_words": _words(r["theory"]),
                "recommended": treatment,
                "reason": reason,
                "canonical_match": match,
            }
        )
    return out


def summarise(items: list[dict]) -> dict:
    per_path = Counter(i["recommended"] for i in items)
    blocks: dict[str, Counter] = defaultdict(Counter)
    for i in items:
        block = i["title"].split(":")[0] or "uncategorised"
        blocks[block][i["recommended"]] += 1
    return {"total": len(items), "per_path": dict(per_path), "blocks": {k: dict(v) for k, v in blocks.items()}}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--db", default=str(DB_PATH))
    ap.add_argument("--paths", nargs="*", default=["agi-research", "data-science", "web-dev"])
    ap.add_argument("--json", metavar="FILE", help="write the full inventory as JSON")
    args = ap.parse_args()

    conn = sqlite3.connect(args.db)
    conn.row_factory = sqlite3.Row

    all_items: list[dict] = []
    for slug in args.paths:
        items = audit(conn, slug)
        all_items.extend(items)
        s = summarise(items)
        print(f"\n=== {slug} (d75-149, {s['total']} days) ===")
        for k, v in sorted(s["per_path"].items(), key=lambda kv: -kv[1]):
            print(f"   {k:<18} {v}")
        print("   by block:")
        for b in sorted(s["blocks"]):
            detail = ", ".join(f"{k}={v}" for k, v in sorted(s["blocks"][b].items()))
            print(f"     {b:<32} {detail}")

    combined = Counter(i["recommended"] for i in all_items)
    print(f"\n=== ALL PATHS ({len(all_items)} day-slots) ===")
    for k, v in combined.most_common():
        print(f"   {k:<18} {v}")

    if args.json:
        Path(args.json).write_text(json.dumps(all_items, indent=2))
        print(f"\ninventory written to {args.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
