"""Compose path-specific lessons from canonical shared topics.

A canonical topic holds the concept and its sources. This module turns one
record, applied to one path, into the lesson structure PySchool already
consumes: the dict shape that `curriculum_worker.validate()` checks and that
`seed.py` writes into the `lessons` table.

The composition is deterministic: the same (topic, path) always yields the same
lesson, because every varying piece — framing, worked example, questions,
homework — is an authored adapter value rather than generated prose. The
canonical concept paragraph is carried into theory, but the lesson's worked
example, practice and assessment are always the path's own.

Lesson theory is assembled from parts, and the word budget of the existing
validator (450-900 words) is enforced here so a bad adapter fails loudly at
composition time instead of at seed time.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

# backend/app/lesson_composer.py -> repository root -> .books
_BOOKS = Path(__file__).resolve().parent.parent.parent / ".books"
if str(_BOOKS) not in sys.path:
    sys.path.insert(0, str(_BOOKS))

from canonical_topics import by_id  # noqa: E402
from source_index import provenance_line  # noqa: E402

# Minimum/maximum theory words, copied from curriculum_worker.validate().
MIN_THEORY_WORDS = 450
MAX_THEORY_WORDS = 900

# Every lesson must expose exactly three question/answer pairs.
QUESTION_COUNT = 3


def _word_count(text: str) -> int:
    return len(re.findall(r"\b[\w'-]+\b", text))


def _path_domain(slug: str) -> str:
    """Short domain label per path, matching the style seed.py already uses."""
    labels = {
        "network-programming": "Network Programming",
        "etl-pipelines": "ETL Pipelines",
        "excel-automation": "Office Automation",
    }
    return labels.get(slug, slug.replace("-", " ").title())


def _example_for(adapter: dict, record: dict, slug: str) -> str:
    """Return the path-specific worked example.

    Examples are authored per path in the adapter and stored under `code`.
    They are stored here rather than generated, so the lesson is stable.
    """
    code = adapter.get("code")
    if code is None:
        raise ValueError(f"adapter for {record['id']} on {slug} has no code")
    return code


def _theory_for(record: dict, adapter: dict, slug: str) -> str:
    """Assemble theory from the canonical concept plus the path's framing."""
    lines = [
        f"**Learning objective**",
        f"Explain {_objective_topic(record, adapter)} for {_path_domain(slug)}, "
        f"and apply it in a worked example.",
        "",
        f"**The core idea**",
        record["concept"],
        "",
        f"**What this means in {_path_domain(slug)}**",
        adapter["framing"],
        "",
        f"**Working through it in {_path_domain(slug)}**",
        adapter["application"],
        "",
        f"**Common mistakes**",
    ]
    for pitfall in record["pitfalls"]:
        lines.append(f"- {pitfall}")
    if record["gap_note"]:
        lines += ["", "**Source gap, stated plainly**", record["gap_note"]]
    lines += [
        "",
        "**Where this comes from**",
        "This lesson is grounded in: " + "; ".join(
            provenance_line(s) for s in record["sources"]
        ) + ".",
        "",
        "**Practice before submitting**",
        "Run the example, change one value, and predict the output before you execute it.",
    ]
    return "\n".join(lines)


def _objective_topic(record: dict, adapter: dict) -> str:
    return record["name"].split(":")[-1].split(" — ")[-1].strip().rstrip(".").lower()


def compose(topic_id: str, slug: str) -> dict:
    """Compose one lesson from a canonical topic for one path."""
    record = by_id(topic_id)
    adapter = record["adapters"].get(slug)
    if adapter is None:
        raise KeyError(
            f"{topic_id} has no adapter for {slug}; "
            f"available: {sorted(record['adapters'])}"
        )

    code = _example_for(adapter, record, slug)
    theory = _theory_for(record, adapter, slug)
    questions = list(adapter["questions"])
    answers = list(adapter["answers"])
    homework = adapter["homework"]
    patterns = list(adapter["required_patterns"])

    words = _word_count(theory)
    if not MIN_THEORY_WORDS <= words <= MAX_THEORY_WORDS:
        raise ValueError(
            f"{topic_id}/{slug}: theory has {words} words, "
            f"expected {MIN_THEORY_WORDS}-{MAX_THEORY_WORDS}"
        )
    if len(questions) != QUESTION_COUNT or len(answers) != QUESTION_COUNT:
        raise ValueError(
            f"{topic_id}/{slug}: expected {QUESTION_COUNT} questions and answers"
        )
    if not all(isinstance(p, str) and p for p in patterns):
        raise ValueError(f"{topic_id}/{slug}: required_patterns must be non-empty strings")

    return {
        "path": slug,
        "day": adapter["day"],
        "title": adapter["title"],
        "domain": _path_domain(slug),
        "objective": (
            f"Explain {_objective_topic(record, adapter)} and apply it in a "
            f"{_path_domain(slug).lower()} worked example."
        ),
        "theory": theory,
        "code_example": code,
        "questions": questions,
        "answers": answers,
        "homework": homework,
        "required_patterns": patterns,
        "canonical_topic": topic_id,
        "provenance": [provenance_line(s) for s in record["sources"]],
        "coverage": record["coverage"],
    }


def compose_all(topic_id: str) -> list[dict]:
    """Compose one canonical topic for every path it has an adapter for."""
    record = by_id(topic_id)
    return [compose(topic_id, slug) for slug in sorted(record["adapters"])]
