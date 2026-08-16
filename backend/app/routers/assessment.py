"""Assessment endpoints: fetch questions, submit answers, judge level, enroll."""
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

        # Create or fetch student
        student = conn.execute(
            "SELECT id FROM students WHERE email = ?", (payload.student_email,)
        ).fetchone()
        if student:
            student_id = student["id"]
        else:
            cur = conn.execute(
                "INSERT INTO students (name, email) VALUES (?, ?)",
                (payload.student_name, payload.student_email),
            )
            student_id = cur.lastrowid

        # Grade answers
        score = 0
        for answer in payload.answers:
            row = conn.execute(
                "SELECT correct FROM assessment_questions WHERE id = ? AND path_id = ?",
                (answer.question_id, payload.path_id),
            ).fetchone()
            if row and row["correct"] == answer.selected.upper():
                score += 1

        total = len(payload.answers)
        level = get_level(score, total)

        # Upsert enrollment
        existing = conn.execute(
            "SELECT id FROM enrollments WHERE student_id = ? AND path_id = ?",
            (student_id, payload.path_id),
        ).fetchone()
        if existing:
            conn.execute(
                "UPDATE enrollments SET level = ?, level_score = ? WHERE id = ?",
                (level, score, existing["id"]),
            )
            enrollment_id = existing["id"]
            feedback = "Assessment re-done — level updated."
        else:
            cur = conn.execute(
                "INSERT INTO enrollments (student_id, path_id, level, level_score) VALUES (?, ?, ?, ?)",
                (student_id, payload.path_id, level, score),
            )
            enrollment_id = cur.lastrowid
            feedback = (
                f"Welcome!, {payload.student_name}! You are at {level} level for "
                f"{path_row['name']}. Your daily 1-hour Python class starts now."
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
        }
    finally:
        conn.close()
