"""Student dashboard: calendar, progress, streak, level, schedule overview."""
from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException

from ..db import get_conn
from .lessons import verify_enrollment_token

router = APIRouter()


@router.get("/enrollments/{enrollment_id}/dashboard", dependencies=[Depends(verify_enrollment_token)])
def dashboard(enrollment_id: int):
    conn = get_conn()
    try:
        enroll = conn.execute(
            "SELECT * FROM enrollments WHERE id = ?", (enrollment_id,)
        ).fetchone()
        if not enroll:
            raise HTTPException(status_code=404, detail="Enrollment not found")

        path = conn.execute(
            "SELECT p.name, p.libraries, p.slug FROM paths p WHERE id = ?",
            (enroll["path_id"],),
        ).fetchone()
        student = conn.execute(
            "SELECT name, email FROM students WHERE id = ?", (enroll["student_id"],)
        ).fetchone()

        total_lessons = conn.execute(
            "SELECT COUNT(*) AS c FROM lessons WHERE path_id = ?", (enroll["path_id"],)
        ).fetchone()["c"]
        done_lessons = enroll["current_day"] - 1
        progress_pct = min(100, round(done_lessons / max(total_lessons, 1) * 100))

        attendance_rows = conn.execute(
            "SELECT day, date, present FROM attendance WHERE enrollment_id = ? ORDER BY day",
            (enrollment_id,),
        ).fetchall()
        attended_days = [r["day"] for r in attendance_rows if r["present"]]
        review_ready = conn.execute(
            "SELECT COUNT(*) AS c FROM mastery_records WHERE enrollment_id = ? AND status = 'ready_for_review'",
            (enrollment_id,),
        ).fetchone()["c"]
        starting = None
        if enroll["starting_milestone_id"]:
            starting_row = conn.execute(
                "SELECT code, title FROM milestones WHERE id = ?", (enroll["starting_milestone_id"],)
            ).fetchone()
            starting = dict(starting_row) if starting_row else None

        today = date.today()
        yesterday = today - timedelta(days=1)
        tomorrow = today + timedelta(days=1)

        return {
            "student_name": student["name"],
            "student_email": student["email"],
            "path_id": enroll["path_id"],
            "path_name": path["name"],
            "path_libraries": path["libraries"],
            "level": enroll["level"],
            "level_score": enroll["level_score"],
            "current_day": enroll["current_day"],
            "streak": enroll["streak"],
            "penalty_points": enroll["penalty_points"],
            "xp": enroll["xp"],
            "total_lessons": total_lessons,
            "progress_pct": progress_pct,
            "attended_days": attended_days,
            "review_ready": review_ready,
            "starting_milestone": starting,
            "schedule": {
                "yesterday": {"day": max(1, enroll["current_day"] - 1), "date": yesterday.isoformat()},
                "today": {"day": enroll["current_day"], "date": today.isoformat(), "is_active": True},
                "tomorrow": {"day": enroll["current_day"] + 1, "date": tomorrow.isoformat()},
            },
        }
    finally:
        conn.close()
