"""Authored lessons, safe assignment checks, and progress gates."""
import ast
import json
import re

from fastapi import APIRouter, Depends, HTTPException
from fastapi.params import Header

from ..db import get_conn
from ..personalize import lesson_personalization, record_topic, weak_topics
from ..schemas import HomeworkSubmit

router = APIRouter()


def verify_enrollment_token(
    enrollment_id: int,
    x_enrollment_token: str | None = Header(default=None, alias="X-Enrollment-Token"),
) -> None:
    """MVP-safe access control: requests must present the enrollment's token.

    The token is issued once at assessment time and kept in the student's
    browser. This prevents trivially tampering with other learners by guessing
    or editing URL ids, without introducing a full authentication system.
    """
    conn = get_conn()
    try:
        row = conn.execute(
            "SELECT access_token FROM enrollments WHERE id = ?", (enrollment_id,)
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Enrollment not found")
        stored = row["access_token"]
        if not stored or not x_enrollment_token or not re.fullmatch(r"[\w-]+", x_enrollment_token):
            raise HTTPException(
                status_code=401,
                detail="Missing or invalid enrollment token. Please re-enroll from the path page.",
            )
        import hmac

        if not hmac.compare_digest(stored.encode(), x_enrollment_token.encode()):
            raise HTTPException(status_code=401, detail="This learner session does not match this enrollment.")
    finally:
        conn.close()


def _is_word(char: str) -> bool:
    return char.isalnum() or char == "_"


def _rubric_regex(pattern: str) -> re.Pattern:
    """Compile a rubric pattern into a whitespace-tolerant regex.

    Examples of what this accepts versus the old literal substring check:
      "print("     matches  print(x), print (x), print(  x)
      "def "       matches  def foo(...)   but still rejects  define(...)
      "with open(" matches  with open(x),  with  open (x)
      "try:"       matches  try: and try :
    Word characters keep boundary guards so bare keywords never match inside
    longer identifiers; optional whitespace is allowed wherever Python allows
    it between a word character and a punctuation character.
    """
    pieces: list[str] = []
    for token in pattern.split():
        piece = ""
        for index, char in enumerate(token):
            piece += re.escape(char)
            nxt = token[index + 1] if index + 1 < len(token) else None
            if nxt is not None and _is_word(char) != _is_word(nxt):
                piece += r"\s*"
        if _is_word(token[0]):
            piece = r"\b" + piece
        if _is_word(token[-1]):
            piece += r"\b"
        pieces.append(piece)
    return re.compile(r"\s+".join(pieces))


def pattern_found(pattern: str, code: str) -> bool:
    """Whitespace-tolerant required-pattern check for homework rubrics."""
    return _rubric_regex(pattern).search(code) is not None


def _lesson_for_day(conn, enrollment_id: int, day: int):
    return conn.execute(
        """
        SELECT l.*, m.id AS milestone_id, m.code AS milestone_code, m.domain,
               m.objective, m.mastery_criteria, m.remediation_note,
               a.id AS assignment_id, a.prompt AS assignment_prompt,
               a.required_patterns, a.min_lines, a.rubric
        FROM enrollments e
        JOIN lessons l ON l.path_id = e.path_id AND l.day_number = ?
        JOIN lesson_milestones lm ON lm.lesson_id = l.id
        JOIN milestones m ON m.id = lm.milestone_id
        LEFT JOIN assignments a ON a.lesson_id = l.id
        WHERE e.id = ?
        """,
        (day, enrollment_id),
    ).fetchone()


# Days are authored over time, so a curriculum day can exist as a placeholder
# that has not been written to the teaching standard yet. Serving one would hand
# the student a stub dressed as a lesson, which is worse than refusing: the
# honest answer is that this day is not available yet.
def _next_active_day(conn, enrollment_id: int, day: int) -> int | None:
    row = conn.execute(
        """
        SELECT MIN(l.day_number) AS d FROM enrollments e
        JOIN lessons l ON l.path_id = e.path_id
        WHERE e.id = ? AND l.status = 'active' AND l.day_number > ?
        """,
        (enrollment_id, day),
    ).fetchone()
    return row["d"] if row and row["d"] is not None else None


@router.get("/enrollments/{enrollment_id}/lesson", dependencies=[Depends(verify_enrollment_token)])
def get_lesson(enrollment_id: int, day: int | None = None):
    """Return an authored lesson and its transparent coding rubric."""
    conn = get_conn()
    try:
        enrollment = conn.execute(
            "SELECT id, path_id, level, current_day FROM enrollments WHERE id = ?", (enrollment_id,)
        ).fetchone()
        if not enrollment:
            raise HTTPException(status_code=404, detail="Enrollment not found")
        target_day = day or enrollment["current_day"]
        lesson = _lesson_for_day(conn, enrollment_id, target_day)
        if not lesson:
            raise HTTPException(
                status_code=409,
                detail="This 180-day programme is complete. Your next module will be published separately.",
            )
        if lesson["status"] != "active":
            upcoming = _next_active_day(conn, enrollment_id, target_day)
            raise HTTPException(
                status_code=409,
                detail={
                    "message": f"Day {target_day} is being written and is not available yet.",
                    "day": target_day,
                    "status": lesson["status"] or "in_progress",
                    "next_available_day": upcoming,
                },
            )
        submission = conn.execute(
            """SELECT passed, feedback FROM homework_submissions
               WHERE enrollment_id = ? AND lesson_id = ? ORDER BY id DESC LIMIT 1""",
            (enrollment_id, lesson["id"]),
        ).fetchone()
        return {
            "id": lesson["id"], "path_id": lesson["path_id"], "day_number": lesson["day_number"],
            "title": lesson["title"], "theory": lesson["theory"], "code_example": lesson["code_example"],
            "questions": json.loads(lesson["questions"]), "answers": json.loads(lesson["answers"]),
            "homework": lesson["homework"],
            # Read the real state rather than reporting a hardcoded false. The
            # body the generator writes says so, and a day can be a generated
            # practice day or an authored concept day.
            "generated": "This is a practice day" in (lesson["theory"] or ""),
            "day_type": lesson["day_type"] if "day_type" in lesson.keys() else None,
            "status": lesson["status"] if "status" in lesson.keys() else None,
            "milestone": {
                "id": lesson["milestone_id"], "code": lesson["milestone_code"], "domain": lesson["domain"],
                "objective": lesson["objective"], "mastery_criteria": lesson["mastery_criteria"],
                "remediation_note": lesson["remediation_note"],
            },
            "assignment": {
                "id": lesson["assignment_id"], "prompt": lesson["assignment_prompt"],
                "required_patterns": json.loads(lesson["required_patterns"]), "min_lines": lesson["min_lines"],
                "rubric": lesson["rubric"],
            },
            # Delivery adapted to this learner: scaffolding depth, focus topics
            # from their concept state, and any adaptive extra requirement.
            "personalization": lesson_personalization(conn, enrollment, lesson),
            "submission": dict(submission) if submission else None,
        }
    finally:
        conn.close()


@router.post("/enrollments/{enrollment_id}/complete", dependencies=[Depends(verify_enrollment_token)])
def complete_lesson(enrollment_id: int):
    """Advance exactly once after a passing assignment; safe on repeated clicks."""
    conn = get_conn()
    try:
        conn.execute("BEGIN IMMEDIATE")
        enrollment = conn.execute("SELECT * FROM enrollments WHERE id = ?", (enrollment_id,)).fetchone()
        if not enrollment:
            raise HTTPException(status_code=404, detail="Enrollment not found")
        lesson = _lesson_for_day(conn, enrollment_id, enrollment["current_day"])
        if not lesson:
            raise HTTPException(status_code=409, detail="No next authored lesson is available yet.")
        passed = conn.execute(
            """SELECT 1 FROM homework_submissions WHERE enrollment_id = ? AND lesson_id = ? AND passed = 1
               LIMIT 1""", (enrollment_id, lesson["id"])
        ).fetchone()
        if not passed:
            raise HTTPException(status_code=409, detail="Submit and pass today's coding practice before completing this milestone.")

        day = enrollment["current_day"]
        conn.execute("INSERT OR IGNORE INTO attendance (enrollment_id, day, present) VALUES (?, ?, 1)", (enrollment_id, day))
        conn.execute(
            """INSERT INTO lesson_progress (enrollment_id, lesson_id, status, submitted_at, passed)
               VALUES (?, ?, 'completed', datetime('now'), 1)
               ON CONFLICT(enrollment_id, lesson_id) DO UPDATE SET status = 'completed', passed = 1""",
            (enrollment_id, lesson["id"]),
        )
        conn.execute(
            """INSERT INTO mastery_records (enrollment_id, milestone_id, quiz_score, code_passed, status, mastered_at)
               VALUES (?, ?, 0, 1, 'ready_for_review', datetime('now'))
               ON CONFLICT(enrollment_id, milestone_id) DO UPDATE SET code_passed = 1, status = 'ready_for_review'""",
            (enrollment_id, lesson["milestone_id"]),
        )
        xp = enrollment["xp"] + 10
        streak = enrollment["streak"] + 1
        next_day = day + 1
        conn.execute(
            "UPDATE enrollments SET current_day = ?, xp = ?, streak = ? WHERE id = ?",
            (next_day, xp, streak, enrollment_id),
        )
        # Adaptive next step: the next lesson personalises on this state, and we
        # say out loud whether a review is the honest next move.
        review = weak_topics(conn, enrollment_id, limit=3)
        conn.commit()
        message = (
            f"{lesson['milestone_code']} practice completed. +10 XP. Your explanation and "
            "spaced review remain part of full mastery."
        )
        if review:
            topics = ", ".join(item["topic"].replace("-", " ") for item in review)
            message += f" Next step: revisit {topics} before it costs you later."
        return {
            "current_day": next_day, "xp": xp, "streak": streak,
            "review_topics": [item["topic"] for item in review],
            "message": message,
        }
    finally:
        conn.close()


@router.get("/enrollments/{enrollment_id}/homework", dependencies=[Depends(verify_enrollment_token)])
def get_pending_homework(enrollment_id: int):
    conn = get_conn()
    try:
        enrollment = conn.execute("SELECT current_day FROM enrollments WHERE id = ?", (enrollment_id,)).fetchone()
        if not enrollment:
            raise HTTPException(status_code=404, detail="Enrollment not found")
        lesson = _lesson_for_day(conn, enrollment_id, enrollment["current_day"])
        if not lesson:
            return {"homework": "No published assignment is available yet.", "lesson_id": None}
        return {"homework": lesson["assignment_prompt"], "lesson_id": lesson["id"], "rubric": lesson["rubric"]}
    finally:
        conn.close()


@router.post("/homework/submit")
def submit_homework(payload: HomeworkSubmit, x_enrollment_token: str | None = Header(default=None, alias="X-Enrollment-Token")):
    """Check source structure only. Student code is never executed by this API.

    Returns structured per-requirement results so the UI can render an exact
    pass/fail checklist instead of one opaque blob of text.
    """
    # Body-carries-enrollment: verify the token manually against the payload.
    conn = get_conn()
    try:
        token_row = conn.execute(
            "SELECT access_token FROM enrollments WHERE id = ?", (payload.enrollment_id,)
        ).fetchone()
        if not token_row:
            raise HTTPException(status_code=404, detail="Enrollment not found")
        import hmac

        stored = token_row["access_token"] or ""
        if not x_enrollment_token or not hmac.compare_digest(stored.encode(), x_enrollment_token.encode()):
            raise HTTPException(
                status_code=401,
                detail="Missing or invalid enrollment token. Please re-enroll from the path page.",
            )

        enrollment = conn.execute(
            "SELECT * FROM enrollments WHERE id = ?", (payload.enrollment_id,)
        ).fetchone()
        lesson = _lesson_for_day(conn, payload.enrollment_id, enrollment["current_day"])
        if not lesson or lesson["id"] != payload.lesson_id:
            raise HTTPException(status_code=409, detail="Submit the assignment for your current milestone only.")

        feedback: list[str] = []

        # Check 1: syntax (AST parse only — code is never executed).
        try:
            ast.parse(payload.code)
            syntax_ok = True
            feedback.append("Python syntax looks valid.")
        except SyntaxError as error:
            syntax_ok = False
            hint = ""
            if error.msg and "invalid" in error.msg.lower():
                hint = " Check for a missing colon, bracket or quote just before that line."
            feedback.append(f"Syntax error on line {error.lineno}: {error.msg}.{hint}")

        # Check 2: minimum non-empty lines.
        non_empty_lines = [line for line in payload.code.splitlines() if line.strip()]
        min_lines = lesson["min_lines"] or 3
        line_ok = len(non_empty_lines) >= min_lines
        if line_ok:
            feedback.append(f"You wrote {len(non_empty_lines)} non-empty lines (need {min_lines}). ✓")
        else:
            feedback.append(
                f"You wrote {len(non_empty_lines)} non-empty line(s) but today's rubric needs at least {min_lines}. "
                "Expand your example instead of padding with blank lines."
            )

        # Check 3: required language constructs (whitespace-tolerant). A learner
        # who is struggling gets one adaptive extra requirement — a self-check —
        # so mastery is re-proved rather than assumed.
        personalization = lesson_personalization(conn, enrollment, lesson)
        patterns = json.loads(lesson["required_patterns"]) if lesson["required_patterns"] else []
        patterns = patterns + [p for p in personalization["extra_patterns"] if p not in patterns]
        pattern_results = [
            {"pattern": pattern, "found": pattern_found(pattern, payload.code)}
            for pattern in patterns
        ]
        missing = [item["pattern"] for item in pattern_results if not item["found"]]
        if missing:
            feedback.append(
                "Required concept(s) not detected yet: "
                + ", ".join(f"`{item}`" for item in missing)
                + ". Write real code using them — spacing before brackets like `print (...)` is fine."
            )
        elif patterns:
            feedback.append("All required language constructs found. ✓")

        passed = syntax_ok and line_ok and not missing
        already_passed = conn.execute(
            "SELECT 1 FROM homework_submissions WHERE enrollment_id = ? AND lesson_id = ? AND passed = 1",
            (payload.enrollment_id, payload.lesson_id),
        ).fetchone()
        if passed:
            feedback.append("Practice rubric passed. You can now complete the milestone.")
        else:
            feedback.append(
                "Not passed yet. Fix the failed checks above and submit again—no penalty is added for practice."
            )
        conn.execute(
            """INSERT INTO homework_submissions (enrollment_id, lesson_id, code, passed, feedback, checked_at)
               VALUES (?, ?, ?, ?, ?, datetime('now'))""",
            (payload.enrollment_id, payload.lesson_id, payload.code, int(passed), " ".join(feedback)),
        )
        if passed and not already_passed:
            conn.execute("UPDATE enrollments SET xp = xp + 15 WHERE id = ?", (payload.enrollment_id,))
        # Concept-level state for the next lesson's personalisation.
        record_topic(
            conn, payload.enrollment_id, lesson["title"],
            source="homework", ref_day=enrollment["current_day"], correct=bool(passed),
        )
        conn.commit()
        return {
            "passed": passed,
            "feedback": " ".join(feedback),
            "penalty_added": False,
            "checks": {
                "syntax_ok": syntax_ok,
                "lines_written": len(non_empty_lines),
                "min_lines": min_lines,
                "lines_ok": line_ok,
                "patterns": pattern_results,
            },
        }
    finally:
        conn.close()
