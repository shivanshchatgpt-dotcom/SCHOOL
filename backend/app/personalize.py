"""Read-time personalisation of the next lesson.

The school does not keep one lesson file per student. It keeps a small
concept-level state per learner — which topics the placement test and the
homework checks say are weak — and adapts the *delivery* of the same authored
lesson: how much scaffolding, which focus topics to revisit, and whether a
struggling learner must add one more piece of evidence before moving on.

Everything here is deterministic and read-only apart from ``record_topic``,
which is the only writer.
"""
import json

# placement level -> how much scaffolding the delivery carries
_DELIVERY = {
    "Foundation": "guided",
    "Beginner": "guided",
    "Intermediate": "standard",
    "Advanced": "concise",
}

_LEVEL_NOTE = {
    "guided": "Guided mode: the worked example is shown and the hints walk you through it one step at a time.",
    "standard": "Standard mode: read the objective, write your own attempt, then compare with the worked example.",
    "concise": "Concise mode: no hand-holding. Attempt the practice before you look at the example, then push one step further.",
}

_CHALLENGE = (
    "Add one case the example does not cover (empty input, a zero, or a wrong type) "
    "and guard it with an `assert` that proves your fix."
)

# Only these count as demonstrated struggle for the hard gate. Placement misses
# suggest review, they never block a learner on their first day.
_STRUGGLE_FAILS = 2


def record_topic(conn, enrollment_id: int, topic: str, *, source: str,
                 ref_day: int | None = None, correct: bool) -> None:
    """Bump a learner's hits or misses for one topic (idempotent per submit)."""
    if not topic:
        return
    column = "hits" if correct else "misses"
    conn.execute(
        f"""INSERT INTO learner_topics (enrollment_id, topic, source, ref_day, misses, hits, last_seen)
            VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
            ON CONFLICT(enrollment_id, topic, source) DO UPDATE SET
                {column} = {column} + 1,
                ref_day = COALESCE(excluded.ref_day, ref_day),
                last_seen = datetime('now')""",
        (enrollment_id, topic, source, ref_day, 0 if correct else 1, 1 if correct else 0),
    )


def weak_topics(conn, enrollment_id: int, limit: int = 3) -> list[dict]:
    """Topics where misses outnumber hits, weakest first."""
    rows = conn.execute(
        """SELECT topic, source, ref_day, misses, hits
           FROM learner_topics
           WHERE enrollment_id = ? AND misses > hits
           ORDER BY (misses - hits) DESC, last_seen DESC
           LIMIT ?""",
        (enrollment_id, limit),
    ).fetchall()
    return [dict(row) for row in rows]


def _focus(conn, enrollment, limit: int = 3) -> list[dict]:
    """Weak topics with a concrete, do-able drill — the learner's next step.

    A homework-derived topic can point back at the exact lesson that taught it,
    so the "focus" block is a re-drill of real material rather than advice.
    """
    entries = []
    for weak in weak_topics(conn, enrollment["id"], limit=limit):
        entry = dict(weak)
        row = None
        if weak["ref_day"]:
            row = conn.execute(
                "SELECT title, questions, homework FROM lessons WHERE path_id = ? AND day_number = ?",
                (enrollment["path_id"], weak["ref_day"]),
            ).fetchone()
        if row:
            entry["ref_title"] = row["title"]
            questions = json.loads(row["questions"] or "[]")
            entry["drill"] = questions[0] if questions else (row["homework"] or "")[:240]
        else:
            entry["drill"] = (
                f"Revisit the {weak['topic'].replace('-', ' ')} ideas your placement test flagged."
            )
        entries.append(entry)
    return entries


def _hints(delivery: str, patterns: list[str]) -> list[str]:
    hints = ["Read the objective and the practice prompt before typing anything."]
    if patterns:
        hints.append("Your submission must use: " + ", ".join(f"`{p.strip()}`" for p in patterns) + ".")
    if delivery == "guided":
        hints.append("Run the worked example, change one value, and predict the new output before you write your own.")
        hints.append("Write your solution one line at a time and test after each line.")
    elif delivery == "standard":
        hints.append("Write your own attempt first, then compare it against the worked example.")
    else:
        hints.append("Try to finish without the example; once it passes, add an edge case of your own.")
    return hints


def lesson_personalization(conn, enrollment, lesson) -> dict:
    """The delivery plan for one learner on one lesson.

    ``extra_patterns`` is the adaptive gate: a learner who has clearly struggled
    with this lesson must include a self-checking ``assert`` before they can move
    on. ``focus`` is the review list built from their concept-level state.
    """
    level = (enrollment["level"] if enrollment["level"] else "Beginner")
    delivery = _DELIVERY.get(level, "standard")

    fails = conn.execute(
        "SELECT COUNT(*) AS c FROM homework_submissions "
        "WHERE enrollment_id = ? AND lesson_id = ? AND passed = 0",
        (enrollment["id"], lesson["id"]),
    ).fetchone()["c"]
    topic_row = conn.execute(
        "SELECT misses, hits FROM learner_topics "
        "WHERE enrollment_id = ? AND topic = ? AND source = 'homework'",
        (enrollment["id"], lesson["title"]),
    ).fetchone()
    struggling = fails >= _STRUGGLE_FAILS or (
        topic_row is not None and topic_row["misses"] > topic_row["hits"]
    )

    # Never strip scaffolding from someone who is struggling, whatever their
    # placement level claims.
    if struggling and delivery == "concise":
        delivery = "standard"

    patterns = json.loads(lesson["required_patterns"] or "[]")
    return {
        "delivery_level": delivery,
        "level_note": _LEVEL_NOTE[delivery],
        "show_example": delivery != "concise",
        "hints": _hints(delivery, patterns),
        "focus": _focus(conn, enrollment),
        "remediation": struggling,
        "extra_patterns": ["assert"] if struggling else [],
        "challenge": _CHALLENGE if delivery == "concise" else None,
    }
