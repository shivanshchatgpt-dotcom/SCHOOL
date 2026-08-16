"""Seed the PySchool database from seed_data (idempotent)."""
import json

from .db import get_conn
from .seed_data import CATEGORIES, PATHS, ASSESSMENT_BASE, PATH_FLAGSHIP_QUESTIONS, LESSON_TEMPLATES

SEED_VERSION = 1


def _level_feedback(level: str, path_name: str) -> str:
    if level == "Beginner":
        return (
            f"Tumhara {path_name} journey abhi shuru hui hai. Hum base se start karenge — "
            "no stress, har great developer kahin se shuru hota hai. 1 hour daily class + homework."
        )
    if level == "Intermediate":
        return (
            f"Tumhe Python ka base pata hai. Hum {path_name} ke core topics "
            "aur real projects par focus karenge. 1 hour daily class + homework + projects."
        )
    return (
        f"Wah! Tum advanced level par ho. Hum {path_name} ke deep topics, optimization aur "
        "production-grade projects karenge. Expected: fast pace, tough homework."
    )


def _needs_seed(conn) -> bool:
    try:
        row = conn.execute("SELECT value FROM meta WHERE key = 'seed_version'").fetchone()
        return not row or int(row["value"]) < SEED_VERSION
    except Exception:
        return True


def seed() -> None:
    conn = get_conn()
    try:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS meta (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );
        """)

        if not _needs_seed(conn):
            print("[seed] skip — already seeded")
            return

        conn.executescript("""
            DELETE FROM lesson_progress;
            DELETE FROM homework_submissions;
            DELETE FROM attendance;
            DELETE FROM enrollments;
            DELETE FROM students;
            DELETE FROM lessons;
            DELETE FROM assessment_questions;
            DELETE FROM paths;
            DELETE FROM categories;
            DELETE FROM sqlite_sequence;
        """)

        # Categories
        for name, icon, label, sort_order in CATEGORIES:
            conn.execute(
                "INSERT INTO categories (name, icon, depth_label, sort_order) VALUES (?, ?, ?, ?)",
                (name, icon, label, sort_order),
            )

        # Paths
        for cat_idx, name, desc, libs, slug, diff in PATHS:
            conn.execute(
                "INSERT INTO paths (category_id, name, description, libraries, slug, difficulty) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (cat_idx, name, desc, libs, slug, diff),
            )

        # Lessons for flagship paths
        for slug, lessons in LESSON_TEMPLATES.items():
            row = conn.execute("SELECT id FROM paths WHERE slug = ?", (slug,)).fetchone()
            if not row:
                continue
            path_id = row["id"]
            for day_num, (title, theory, code, questions, answers, homework) in enumerate(lessons, start=1):
                conn.execute(
                    "INSERT INTO lessons (path_id, day_number, title, theory, code_example, questions, answers, homework) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (path_id, day_num, title, theory, code, json.dumps(questions), json.dumps(answers), homework),
                )

        # Assessment questions
        all_paths = conn.execute("SELECT id, slug FROM paths").fetchall()
        for row in all_paths:
            path_id = row["id"]
            slug = row["slug"]
            base_qs = ASSESSMENT_BASE[:5]
            extra = PATH_FLAGSHIP_QUESTIONS.get(slug, [])
            for q_text, a, b, c, d, correct, diff in base_qs + extra:
                conn.execute(
                    "INSERT INTO assessment_questions (path_id, question, option_a, option_b, option_c, option_d, correct, difficulty) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (path_id, q_text, a, b, c, d, correct, diff),
                )

        conn.execute(
            "INSERT OR REPLACE INTO meta (key, value) VALUES ('seed_version', ?)",
            (str(SEED_VERSION),),
        )
        conn.commit()
        print(f"[seed] OK — {len(CATEGORIES)} categories, {len(PATHS)} paths, "
              f"{conn.execute('SELECT COUNT(*) AS c FROM lessons').fetchone()['c']} lessons seeded.")
    finally:
        conn.close()


def get_level(score: int, total: int) -> str:
    pct = (score / total * 100) if total else 0
    if pct < 40:
        return "Beginner"
    if pct < 70:
        return "Intermediate"
    return "Advanced"


if __name__ == "__main__":
    from .db import init_db
    init_db()
    seed()
