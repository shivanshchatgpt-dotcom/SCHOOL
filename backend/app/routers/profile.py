"""Profiling questions shown before the level test.

Rows live in the ``profile_questions`` table, so the question set is data, not
hardcoded UI. Options are returned as structured ``{value, label}`` pairs.
"""
import json

from fastapi import APIRouter

from ..db import get_conn

router = APIRouter()


@router.get("/profile/questions")
def get_profile_questions():
    conn = get_conn()
    try:
        rows = conn.execute(
            "SELECT id, key, question, options, sort_order FROM profile_questions ORDER BY sort_order, id"
        ).fetchall()
        return [
            {
                "id": row["id"],
                "key": row["key"],
                "question": row["question"],
                "options": json.loads(row["options"] or "[]"),
            }
            for row in rows
        ]
    finally:
        conn.close()
