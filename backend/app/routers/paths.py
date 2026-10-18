"""Catalog browsing. Release status belongs in the payload, not in the UI.

A path is only worth enrolling in if it has enough released days to be a
course. `available_days` is counted from lessons that are actually live rather
than read from a stored column, so it cannot drift away from the content, and
every response carries it so the catalog can say "N of M days available" instead
of implying a promise the content does not meet."""
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
                   (SELECT COUNT(*) FROM assessment_questions aq WHERE aq.path_id = p.id) AS assessment_count,
                   (SELECT COUNT(*) FROM lessons l
                     WHERE l.path_id = p.id AND l.status = 'active') AS available_days_live
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
            # The live count wins over the stored column so a content change is
            # reflected the moment it is made.
            live = d.pop("available_days_live", 0) or 0
            d["available_days"] = live
            d["total_days"] = d.get("total_days") or 180
            # A path is only "coming soon" while it has nothing to offer. Once
            # every day is live the stored flag is stale, and showing both
            # "180 of 180 available" and "coming soon" contradicts itself.
            d["is_coming_soon"] = live < d["total_days"]
            d["coming_soon_days"] = d["total_days"] - live
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
                   (SELECT COUNT(*) FROM lessons l WHERE l.path_id = p.id) AS lesson_count,
                   (SELECT COUNT(*) FROM lessons l
                     WHERE l.path_id = p.id AND l.status = 'active') AS available_days_live,
                   (SELECT COUNT(*) FROM lessons l
                     WHERE l.path_id = p.id AND l.status = 'in_progress') AS coming_soon_days
            FROM paths p
            JOIN categories c ON c.id = p.category_id
            WHERE p.slug = ?
            """,
            (slug,),
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Path not found")
        d = dict(row)
        live = d.pop("available_days_live", 0) or 0
        total = d.get("total_days") or 180
        d["available_days"] = live
        d["total_days"] = total
        d["is_coming_soon"] = live < total
        d["coming_soon_days"] = total - live
        return d
    finally:
        conn.close()
