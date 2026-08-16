"""Lessons, homework, attendance, and penalty (school rules) endpoints."""
import json

from fastapi import APIRouter, HTTPException

from ..db import get_conn
from ..schemas import HomeworkSubmit

router = APIRouter()


def _penalty_for(enrollment_id: int, conn) -> int:
    """Penalty = missed previous homework + rule violations. Extra homework lessons are
       generated on the fly based on penalty points."""
    row = conn.execute(
        "SELECT penalty_points FROM enrollments WHERE id = ?", (enrollment_id,)
    ).fetchone()
    return row["penalty_points"] if row else 0


@router.get("/enrollments/{enrollment_id}/lesson")
def get_lesson(enrollment_id: int, day: int | None = None):
    """Get the lesson for the current (or specified) school day."""
    conn = get_conn()
    try:
        enroll = conn.execute(
            "SELECT * FROM enrollments WHERE id = ?", (enrollment_id,)
        ).fetchone()
        if not enroll:
            raise HTTPException(status_code=404, detail="Enrollment not found")

        target_day = day or enroll["current_day"]
        lesson = conn.execute(
            """
            SELECT l.* FROM lessons l
            WHERE l.path_id = ? AND l.day_number = ?
            """,
            (enroll["path_id"], target_day),
        ).fetchone()

        if not lesson:
            # No pre-built lesson: generate a penalty/continuation lesson on the fly
            lesson_data = _generate_lesson(conn, enroll["path_id"], target_day)
            return {
                "id": None,
                "path_id": enroll["path_id"],
                "day_number": target_day,
                "title": lesson_data["title"],
                "theory": lesson_data["theory"],
                "code_example": lesson_data["code_example"],
                "questions": lesson_data["questions"],
                "answers": lesson_data["answers"],
                "homework": lesson_data["homework"],
                "generated": True,
            }

        return {
            "id": lesson["id"],
            "path_id": lesson["path_id"],
            "day_number": lesson["day_number"],
            "title": lesson["title"],
            "theory": lesson["theory"],
            "code_example": lesson["code_example"],
            "questions": json.loads(lesson["questions"]),
            "answers": json.loads(lesson["answers"]),
            "homework": lesson["homework"],
            "generated": False,
        }
    finally:
        conn.close()


def _generate_lesson(conn, path_id: int, day_number: int) -> dict:
    """Generate a practice/penalty lesson dynamically for paths whose full curriculum
       is not yet author-written. Builds on the topics the student already saw."""
    path = conn.execute("SELECT name, libraries FROM paths WHERE id = ?", (path_id,)).fetchone()
    path_name = path["name"]
    libs = path["libraries"]
    penalty = day_number % 3  # simulate escalating pressure as days advance

    title = f"Day {day_number}: Deep Practice in {path_name}"
    theory = (
        f"Today is Day {day_number} of your **{path_name}** journey.\n\n"
        f"Your toolkit: `{libs}`\n\n"
        "**Practice makes permanent.** Today's session is about drilling the core ideas "
        "of your path — the fundamentals that every professional uses daily. "
        "Write code, break it, debug it, fix it. That is how you learn.\n\n"
        "**School Rule reminder:** Complete today's homework before tomorrow's class. "
        "Missing homework adds penalty homework — and more homework is not fun."
    )
    code_example = (
        "# Day {} — Practice drill\n"
        "def core_practice():\n"
        "    # TODO: write a small program that uses the core skill of your path\n"
        "    pass\n"
    ).format(day_number)
    questions = [
        "What is the single most important library for your path?",
        "How would you test a small piece of code in Python?",
        "What does practice + review + homework build over time?",
    ]
    answers = [
        "The core library you chose for your path (see theory).",
        "Write a small script and run it (or use pytest for automated tests).",
        "Long-term skill and a strong portfolio — that's the PySchool way.",
    ]
    homework = (
        f"Write a small program in your path area using at least one library from "
        f"`{libs}`. It must accept input and produce meaningful output. "
        "Submit the code here — it will be checked."
    )
    return {
        "title": title,
        "theory": theory,
        "code_example": code_example,
        "questions": questions,
        "answers": answers,
        "homework": homework,
    }


@router.post("/enrollments/{enrollment_id}/complete")
def complete_lesson(enrollment_id: int):
    """Mark today's class as attended, advance to next day, update streak."""
    conn = get_conn()
    try:
        enroll = conn.execute(
            "SELECT * FROM enrollments WHERE id = ?", (enrollment_id,)
        ).fetchone()
        if not enroll:
            raise HTTPException(status_code=404, detail="Enrollment not found")

        current_day = enroll["current_day"]
        # attendance row
        conn.execute(
            "INSERT OR IGNORE INTO attendance (enrollment_id, day, present) VALUES (?, ?, 1)",
            (enrollment_id, current_day),
        )

        new_day = current_day + 1
        xp = enroll["xp"] + 10
        streak = enroll["streak"] + 1
        conn.execute(
            "UPDATE enrollments SET current_day = ?, xp = ?, streak = ? WHERE id = ?",
            (new_day, xp, streak, enrollment_id),
        )
        conn.commit()
        return {
            "current_day": new_day,
            "xp": xp,
            "streak": streak,
            "message": f"Day {current_day} completed! Next class: Day {new_day}. +10 XP",
        }
    finally:
        conn.close()


@router.get("/enrollments/{enrollment_id}/homework")
def get_pending_homework(enrollment_id: int):
    conn = get_conn()
    try:
        enroll = conn.execute(
            "SELECT * FROM enrollments WHERE id = ?", (enrollment_id,)
        ).fetchone()
        if not enroll:
            raise HTTPException(status_code=404, detail="Enrollment not found")

        # Find homework of the previous day (yesterday's lesson)
        prev_day = enroll["current_day"] - 1
        lesson = conn.execute(
            """
            SELECT id, title, homework FROM lessons
            WHERE path_id = ? AND day_number = ?
            """,
            (enroll["path_id"], prev_day),
        ).fetchone()

        if not lesson:
            return {"homework": "No homework assigned yet — enjoy your evening! 😄", "lesson_id": None}

        sub = conn.execute(
            "SELECT passed, feedback FROM homework_submissions WHERE enrollment_id = ? AND lesson_id = ?",
            (enrollment_id, lesson["id"]),
        ).fetchone()
        status = "submitted-passed" if sub and sub["passed"] else ("submitted-failed" if sub else "pending")
        feedback = sub["feedback"] if sub else ""

        return {
            "homework": lesson["homework"],
            "lesson_id": lesson["id"],
            "status": status,
            "feedback": feedback,
            "penalty_points": enroll["penalty_points"],
        }
    finally:
        conn.close()


@router.post("/homework/submit")
def submit_homework(payload: HomeworkSubmit):
    """Auto-check homework with heuristic checks: syntax via compile, plus length and
       content markers. Passed gives XP; failure adds penalty points."""
    conn = get_conn()
    try:
        enroll = conn.execute(
            "SELECT * FROM enrollments WHERE id = ?", (payload.enrollment_id,)
        ).fetchone()
        if not enroll:
            raise HTTPException(status_code=404, detail="Enrollment not found")

        code = payload.code
        feedback_lines = []

        # Syntax check with real Python compile
        import ast
        try:
            ast.parse(code)
            syntax_ok = True
        except SyntaxError as err:
            syntax_ok = False
            feedback_lines.append(f"Syntax error: {err}")

        has_print = "print(" in code
        length_ok = len(code) >= 60
        if length_ok:
            feedback_lines.append("Good length — real effort detected.")
        else:
            feedback_lines.append("Code is short — try to write more complete code.")

        passed = syntax_ok and has_print and length_ok
        if passed:
            feedback_lines.append("Homework passed! +15 XP — great work, keep the streak alive! 🔥")
        else:
            feedback_lines.append("Homework needs more work. Remember: missed homework = extra homework tomorrow.")

        # Insert submission
        conn.execute(
            """
            INSERT INTO homework_submissions (enrollment_id, lesson_id, code, passed, feedback, checked_at)
            VALUES (?, ?, ?, ?, ?, datetime('now'))
            """,
            (payload.enrollment_id, payload.lesson_id, code, 1 if passed else 0, " ".join(feedback_lines)),
        )

        if passed:
            conn.execute(
                "UPDATE enrollments SET xp = xp + 15 WHERE id = ?", (payload.enrollment_id,)
            )
        else:
            conn.execute(
                "UPDATE enrollments SET penalty_points = penalty_points + 1 WHERE id = ?",
                (payload.enrollment_id,),
            )
        conn.commit()
        return {"passed": passed, "feedback": " ".join(feedback_lines), "penalty_added": not passed}
    finally:
        conn.close()
