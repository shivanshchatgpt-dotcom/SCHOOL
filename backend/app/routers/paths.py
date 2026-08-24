"""Category + path browsing endpoints."""
from fastapi import APIRouter, HTTPException

from ..db import get_conn

router = APIRouter()


@router.get("/categories")
def list_categories(include_future: bool = False):
    conn = get_conn()
    try:
        query = "SELECT id, name, icon, depth_label, sort_order FROM categories"
        if not include_future:
            query += " WHERE EXISTS (SELECT 1 FROM paths WHERE paths.category_id = categories.id AND paths.is_launch_ready = 1)"
        query += " ORDER BY sort_order"
        rows = conn.execute(query).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


@router.get("/paths")
def list_paths(category_id: int | None = None, q: str | None = None, include_future: bool = False):
    conn = get_conn()
    try:
        query = """
            SELECT p.*, c.name AS category_name, c.icon AS category_icon,
                   (SELECT COUNT(*) FROM assessment_questions aq WHERE aq.path_id = p.id) AS assessment_count
            FROM paths p
            JOIN categories c ON c.id = p.category_id
        """
        params: list = []
        conditions: list[str] = []
        if not include_future:
            conditions.append("p.is_launch_ready = 1")
        if category_id is not None:
            conditions.append("p.category_id = ?")
            params.append(category_id)
        if q:
            conditions.append("(p.name LIKE ? OR p.libraries LIKE ? OR p.description LIKE ?)")
            like = f"%{q}%"
            params.extend([like, like, like])
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        query += " ORDER BY p.difficulty, p.name"
        rows = conn.execute(query, params).fetchall()
        result = []
        for r in rows:
            d = dict(r)
            d["category_id"] = d.pop("category_id")
            d["assessment_count"] = d.pop("assessment_count")
            result.append(d)
        return result
    finally:
        conn.close()


@router.get("/paths/{slug}")
def path_detail(slug: str):
    conn = get_conn()
    try:
        row = conn.execute(
            """
            SELECT p.*, c.name AS category_name, c.icon AS category_icon,
                   (SELECT COUNT(*) FROM assessment_questions aq WHERE aq.path_id = p.id) AS assessment_count,
                   (SELECT COUNT(*) FROM lessons l WHERE l.path_id = p.id) AS lesson_count
            FROM paths p
            JOIN categories c ON c.id = p.category_id
            WHERE p.slug = ?
            """,
            (slug,),
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Path not found")
        return dict(row)
    finally:
        conn.close()
