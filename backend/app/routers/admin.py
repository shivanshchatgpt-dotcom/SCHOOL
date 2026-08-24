"""Admin (teacher) endpoints: all students, enrollments, submissions, penalty control.

MVP-safe protection: every admin route requires the X-Admin-Token header to
match the PYSCHOOL_ADMIN_TOKEN environment variable (default "pyschool-admin"
for local development only). This keeps the teacher API out of student reach
without a full authentication system.
"""
import hmac
import os

from fastapi import APIRouter, Depends, Header, HTTPException

from ..db import get_conn


def require_admin(x_admin_token: str | None = Header(default=None, alias="X-Admin-Token")) -> None:
    expected = os.environ.get("PYSCHOOL_ADMIN_TOKEN", "pyschool-admin")
    if not x_admin_token or not hmac.compare_digest(expected.encode(), x_admin_token.encode()):
        raise HTTPException(status_code=401, detail="Teacher access requires a valid X-Admin-Token header.")


router = APIRouter(dependencies=[Depends(require_admin)])


@router.get("/students")
def all_students():
    conn = get_conn()
    try:
        rows = conn.execute(
            """
            SELECT s.id, s.name, s.email, s.created_at,
                   COUNT(e.id) AS enrollment_count
            FROM students s
            LEFT JOIN enrollments e ON e.student_id = s.id
            GROUP BY s.id
            ORDER BY s.created_at DESC
            """
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


@router.get("/enrollments")
def all_enrollments():
    conn = get_conn()
    try:
        rows = conn.execute(
            """
            SELECT e.id, e.level, e.level_score, e.current_day, e.streak,
                   e.penalty_points, e.xp, e.enrolled_at,
                   s.name AS student_name, s.email AS student_email,
                   p.name AS path_name, p.slug AS path_slug
            FROM enrollments e
            JOIN students s ON s.id = e.student_id
            JOIN paths p ON p.id = e.path_id
            ORDER BY e.enrolled_at DESC
            """
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


@router.get("/students/{student_id}")
def student_detail(student_id: int):
    conn = get_conn()
    try:
        student = conn.execute(
            "SELECT * FROM students WHERE id = ?", (student_id,)
        ).fetchone()
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")

        enrollments = conn.execute(
            """
            SELECT e.*, p.name AS path_name, p.slug AS path_slug
            FROM enrollments e
            JOIN paths p ON p.id = e.path_id
            WHERE e.student_id = ?
            """,
            (student_id,),
        ).fetchall()

        subs = conn.execute(
            """
            SELECT hs.*, l.day_number, l.title AS lesson_title, p.name AS path_name
            FROM homework_submissions hs
            JOIN lessons l ON l.id = hs.lesson_id
            JOIN enrollments e ON e.id = hs.enrollment_id
            JOIN paths p ON p.id = e.path_id
            WHERE e.student_id = ?
            ORDER BY hs.checked_at DESC
            """,
            (student_id,),
        ).fetchall()

        return {
            "student": dict(student),
            "enrollments": [dict(e) for e in enrollments],
            "submissions": [dict(s) for s in subs],
        }
    finally:
        conn.close()


@router.post("/enrollments/{enrollment_id}/penalty")
def add_penalty(enrollment_id: int, amount: int = 1):
    """Teacher gives extra homework pressure (penalty points)."""
    conn = get_conn()
    try:
        enroll = conn.execute(
            "SELECT id FROM enrollments WHERE id = ?", (enrollment_id,)
        ).fetchone()
        if not enroll:
            raise HTTPException(status_code=404, detail="Enrollment not found")
        conn.execute(
            "UPDATE enrollments SET penalty_points = penalty_points + ? WHERE id = ?",
            (amount, enrollment_id),
        )
        conn.commit()
        return {"message": f"+{amount} penalty point added. Detention homework issued."}
    finally:
        conn.close()


@router.delete("/enrollments/{enrollment_id}/penalty/reset")
def reset_penalty(enrollment_id: int):
    conn = get_conn()
    try:
        conn.execute(
            "UPDATE enrollments SET penalty_points = 0 WHERE id = ?", (enrollment_id,)
        )
        conn.commit()
        return {"message": "Penalty points reset. Clean slate — welcome back!"}
    finally:
        conn.close()
