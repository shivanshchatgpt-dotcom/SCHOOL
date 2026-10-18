"""Student dashboard: calendar, progress, streak, level, schedule overview.

Progress is measured against released days, not against the catalogue's nominal
length. A path is still being written, and a learner who is told they are 3% of
the way through a 180-day path when only 68 days exist is being told something
false. The response therefore carries both numbers: what is available now, and
what is still to come, so the UI can show a truthful bar and an honest roadmap.
"""
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
            "SELECT p.name, p.libraries, p.slug, p.duration_days FROM paths p WHERE id = ?",
            (enroll["path_id"],),
        ).fetchone()
        student = conn.execute(
            "SELECT name, email FROM students WHERE id = ?", (enroll["student_id"],)
        ).fetchone()

        total_lessons = conn.execute(
            "SELECT COUNT(*) AS c FROM lessons WHERE path_id = ?", (enroll["path_id"],)
        ).fetchone()["c"]
        # Only released days are taught, so only released days count as progress.
        available_lessons = conn.execute(
            "SELECT COUNT(*) AS c FROM lessons WHERE path_id = ? AND status = 'active'",
            (enroll["path_id"],),
        ).fetchone()["c"]
        coming_soon_days = conn.execute(
            "SELECT COUNT(*) AS c FROM lessons WHERE path_id = ? AND status = 'in_progress'",
            (enroll["path_id"],),
        ).fetchone()["c"]
        # Done is capped at what actually exists, otherwise a learner parked on a
        # day that has not been written yet reads as 100% of nothing.
        done_lessons = min(max(enroll["current_day"] - 1, 0), available_lessons)
        progress_pct = min(100, round(done_lessons / max(available_lessons, 1) * 100))

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
        # ponytail: domain of the current day doubles as the phase label — no extra paths column.
        phase_row = conn.execute(
            """SELECT m.domain FROM lessons l
               JOIN lesson_milestones lm ON lm.lesson_id = l.id
               JOIN milestones m ON m.id = lm.milestone_id
               WHERE l.path_id = ? AND l.day_number = ?""",
            (enroll["path_id"], enroll["current_day"]),
        ).fetchone()
        phase = phase_row["domain"] if phase_row else "Foundation"

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
            "available_lessons": available_lessons,
            "coming_soon_days": coming_soon_days,
            "phase": phase,
            "catalog_days": path["duration_days"] or total_lessons,
            "done_lessons": done_lessons,
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
