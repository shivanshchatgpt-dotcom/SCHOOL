"""Assessment endpoints: fetch questions, submit answers, judge level, enroll."""
import secrets

from fastapi import APIRouter, HTTPException

from ..db import get_conn
from ..schemas import AssessmentSubmit
from ..seed import get_level

router = APIRouter()


@router.get("/assessment/{path_id}/questions")
def get_questions(path_id: int):
    conn = get_conn()
    try:
        rows = conn.execute(
            """
            SELECT id, path_id, question, option_a, option_b, option_c, option_d, difficulty
            FROM assessment_questions
            WHERE path_id = ?
            ORDER BY difficulty
            """,
            (path_id,),
        ).fetchall()
        if not rows:
            raise HTTPException(status_code=404, detail="No assessment questions for this path")
        return [dict(r) for r in rows]
    finally:
        conn.close()


@router.post("/assessment/submit")
def submit_assessment(payload: AssessmentSubmit):
    conn = get_conn()
    try:
        path_row = conn.execute("SELECT * FROM paths WHERE id = ?", (payload.path_id,)).fetchone()
        if not path_row:
            raise HTTPException(status_code=404, detail="Path not found")
        if not path_row["is_launch_ready"]:
            raise HTTPException(status_code=409, detail="This path is in the future catalog and does not have a curriculum yet.")

        name = payload.student_name.strip()
        email = payload.student_email.strip().lower()
        if not name or "@" not in email:
            raise HTTPException(status_code=422, detail="Please provide a name and a valid email address.")

        # Create or fetch student
        student = conn.execute(
            "SELECT id FROM students WHERE email = ?", (email,)
        ).fetchone()
        if student:
            student_id = student["id"]
        else:
            cur = conn.execute(
                "INSERT INTO students (name, email) VALUES (?, ?)",
                (name, email),
            )
            student_id = cur.lastrowid

        # Grade answers
        questions = conn.execute(
            "SELECT id, correct, topic FROM assessment_questions WHERE path_id = ?", (payload.path_id,)
        ).fetchall()
        submitted = {answer.question_id: answer.selected.upper() for answer in payload.answers}
        score = sum(1 for question in questions if submitted.get(question["id"]) == question["correct"])
        total = len(questions)
        level = get_level(score, total)
        missed_topics = sorted({question["topic"] for question in questions if submitted.get(question["id"]) != question["correct"]})

        # Placement is transparent and deterministic. Stronger students can start
        # later, while every milestone still exposes its prerequisite chain.
        start_order = 1 if level == "Foundation" else (4 if level == "Beginner" else (7 if level == "Intermediate" else 10))
        starting_milestone = conn.execute(
            "SELECT id, code, title FROM milestones WHERE path_id = ? AND sort_order = ?",
            (payload.path_id, start_order),
        ).fetchone()
        if not starting_milestone:
            raise HTTPException(status_code=500, detail="Curriculum is not available for this path")

        # Upsert enrollment
        existing = conn.execute(
            "SELECT id FROM enrollments WHERE student_id = ? AND path_id = ?",
            (student_id, payload.path_id),
        ).fetchone()
        if existing:
            conn.execute(
                "UPDATE enrollments SET level = ?, level_score = ?, current_day = ?, starting_milestone_id = ? WHERE id = ?",
                (level, score, start_order, starting_milestone["id"], existing["id"]),
            )
            enrollment_id = existing["id"]
            existing_token_row = conn.execute(
                "SELECT access_token FROM enrollments WHERE id = ?", (enrollment_id,)
            ).fetchone()
            access_token = existing_token_row["access_token"] or secrets.token_urlsafe(24)
            feedback = "Assessment re-done — level updated."
        else:
            access_token = secrets.token_urlsafe(24)
            cur = conn.execute(
                "INSERT INTO enrollments (student_id, path_id, level, level_score, current_day, starting_milestone_id, access_token) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (student_id, payload.path_id, level, score, start_order, starting_milestone["id"], access_token),
            )
            enrollment_id = cur.lastrowid
            feedback = (
                f"Welcome, {name}! Your placement is {level}. Start at {starting_milestone['code']}: "
                f"{starting_milestone['title']}."
            )

        conn.commit()
        return {
            "enrollment_id": enrollment_id,
            "student_id": student_id,
            "path_id": payload.path_id,
            "score": score,
            "total": total,
            "level": level,
            "feedback": feedback,
            "starting_milestone": dict(starting_milestone),
            "weak_topics": missed_topics,
            # MVP-safe access control: the browser stores this and presents it
            # as X-Enrollment-Token on every enrollment-scoped request.
            "access_token": access_token,
        }
    finally:
        conn.close()
