"""Seed the PySchool database from seed_data (idempotent)."""
import json

from .db import get_conn
from .seed_data import (
    ASSESSMENT_BASE,
    CATEGORIES,
    CURRICULA,
    extended_curriculum,
    LAUNCH_PATH_SLUGS,
    PATHS,
    PATH_FLAGSHIP_QUESTIONS,
)

SEED_VERSION = 3  # v3: authored Days 15-180 content + enrollment access tokens


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
            added = _seed_extended_curricula(conn)
            conn.execute(
                "UPDATE paths SET duration_days = 180 WHERE slug IN ('agi-research', 'data-science', 'web-dev')"
            )
            conn.commit()
            print(f"[seed] curriculum checked — {added} 180-day lessons added")
            return

        conn.executescript("""
            DELETE FROM mastery_records;
            DELETE FROM milestone_prerequisites;
            DELETE FROM lesson_milestones;
            DELETE FROM assignments;
            DELETE FROM lesson_progress;
            DELETE FROM homework_submissions;
            DELETE FROM attendance;
            DELETE FROM enrollments;
            DELETE FROM students;
            DELETE FROM lessons;
            DELETE FROM milestones;
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
                "INSERT INTO paths (category_id, name, description, libraries, slug, difficulty, is_launch_ready, duration_days) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (cat_idx, name, desc, libs, slug, diff, int(slug in LAUNCH_PATH_SLUGS), 180 if slug in LAUNCH_PATH_SLUGS else 0),
            )

        # The three launch tracks have a deliberately authored 14-day foundation
        # curriculum. Catalog entries outside these tracks are not treated as courses.
        for slug, lessons in CURRICULA.items():
            row = conn.execute("SELECT id FROM paths WHERE slug = ?", (slug,)).fetchone()
            if not row:
                continue
            path_id = row["id"]
            previous_milestone_id = None
            for day_num, (title, domain, objective, code, homework, required_patterns, theory) in enumerate(lessons, start=1):
                milestone = conn.execute(
                    """
                    INSERT INTO milestones
                    (path_id, code, title, domain, objective, estimated_minutes, sort_order, mastery_criteria, remediation_note)
                    VALUES (?, ?, ?, ?, ?, 60, ?, ?, ?)
                    """,
                    (
                        path_id, f"{slug.upper()}-{day_num:03d}", title, domain, objective, day_num,
                        "Pass the concept check, submit code that meets the assignment rubric, and complete a later review.",
                        "Re-read the worked example, change one value, and submit again with a short explanation.",
                    ),
                )
                milestone_id = milestone.lastrowid
                if previous_milestone_id:
                    conn.execute(
                        "INSERT INTO milestone_prerequisites (milestone_id, prerequisite_milestone_id) VALUES (?, ?)",
                        (milestone_id, previous_milestone_id),
                    )
                previous_milestone_id = milestone_id
                lesson = conn.execute(
                    "INSERT INTO lessons (path_id, day_number, title, theory, code_example, questions, answers, homework) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (
                        path_id, day_num, title,
                        f"**Learning objective**\\n{objective}\\n\\n**Why it matters for {domain}**\\n{theory}\\n\\n**Practice before submitting**\\nRun the example, change one value, and predict the output before you execute it.",
                        code,
                        json.dumps(["What does this lesson help you do?", "Which line in the example would you change to test your understanding?"]),
                        json.dumps([objective, "Any one line, with a reason for the change."]),
                        homework,
                    ),
                )
                lesson_id = lesson.lastrowid
                conn.execute("INSERT INTO lesson_milestones (lesson_id, milestone_id) VALUES (?, ?)", (lesson_id, milestone_id))
                conn.execute(
                    "INSERT INTO assignments (lesson_id, prompt, required_patterns, min_lines, rubric) VALUES (?, ?, ?, ?, ?)",
                    (lesson_id, homework, json.dumps(required_patterns), 3, "Code must parse, contain the required Python constructs, and include at least three non-empty lines."),
                )

        _seed_extended_curricula(conn)

        # Assessment questions
        all_paths = conn.execute("SELECT id, slug FROM paths").fetchall()
        for row in all_paths:
            path_id = row["id"]
            slug = row["slug"]
            base_qs = ASSESSMENT_BASE
            extra = PATH_FLAGSHIP_QUESTIONS.get(slug, [])
            for q_text, a, b, c, d, correct, diff in base_qs + extra:
                topic = "python-basics" if diff <= 2 else "python-practice"
                if slug in LAUNCH_PATH_SLUGS and (path_q := PATH_FLAGSHIP_QUESTIONS.get(slug)) and (q_text, a, b, c, d, correct, diff) in path_q:
                    topic = "track-basics"
                conn.execute(
                    "INSERT INTO assessment_questions (path_id, question, option_a, option_b, option_c, option_d, correct, difficulty, topic) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (path_id, q_text, a, b, c, d, correct, diff, topic),
                )

        conn.execute(
            "INSERT OR REPLACE INTO meta (key, value) VALUES ('seed_version', ?)",
            (str(SEED_VERSION),),
        )
        conn.commit()
        print(f"[seed] OK — {len(CATEGORIES)} categories, {len(PATHS)} paths, "
              f"{conn.execute('SELECT COUNT(*) AS c FROM lessons').fetchone()['c']} authored lessons seeded.")
    finally:
        conn.close()


def _seed_extended_curricula(conn) -> int:
    """Append Days 15–180 without resetting existing learners or progress."""
    added = 0
    for slug in LAUNCH_PATH_SLUGS:
        path = conn.execute("SELECT id FROM paths WHERE slug = ?", (slug,)).fetchone()
        if not path:
            continue
        path_id = path["id"]
        for day_num, (title, domain, objective, code, homework, required_patterns, theory) in enumerate(extended_curriculum(slug), start=15):
            exists = conn.execute(
                "SELECT id FROM lessons WHERE path_id = ? AND day_number = ?", (path_id, day_num)
            ).fetchone()
            if exists:
                continue
            previous = conn.execute(
                "SELECT id FROM milestones WHERE path_id = ? AND sort_order = ?", (path_id, day_num - 1)
            ).fetchone()
            milestone = conn.execute(
                """
                INSERT INTO milestones
                (path_id, code, title, domain, objective, estimated_minutes, sort_order, mastery_criteria, remediation_note)
                VALUES (?, ?, ?, ?, ?, 60, ?, ?, ?)
                """,
                (
                    path_id, f"{slug.upper()}-{day_num:03d}", title, domain, objective, day_num,
                    "Pass the concept check, submit code that meets the assignment rubric, explain the idea, and revisit it during review.",
                    "Re-read the worked example, reduce the problem to one small input, and submit a revised explanation.",
                ),
            )
            milestone_id = milestone.lastrowid
            if previous:
                conn.execute(
                    "INSERT OR IGNORE INTO milestone_prerequisites (milestone_id, prerequisite_milestone_id) VALUES (?, ?)",
                    (milestone_id, previous["id"]),
                )
            lesson = conn.execute(
                "INSERT INTO lessons (path_id, day_number, title, theory, code_example, questions, answers, homework) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    path_id, day_num, title,
                    theory, code,
                    json.dumps([f"What problem does {title} help solve?", "Which part of the example would you change, and why?"]),
                    json.dumps([objective, "A specific code change plus the reason for it."]),
                    homework,
                ),
            )
            lesson_id = lesson.lastrowid
            conn.execute("INSERT INTO lesson_milestones (lesson_id, milestone_id) VALUES (?, ?)", (lesson_id, milestone_id))
            conn.execute(
                "INSERT INTO assignments (lesson_id, prompt, required_patterns, min_lines, rubric) VALUES (?, ?, ?, ?, ?)",
                (lesson_id, homework, json.dumps(required_patterns), 3, "Code must parse, include a function and output, and contain at least three non-empty lines."),
            )
            added += 1
    return added


def get_level(score: int, total: int) -> str:
    pct = (score / total * 100) if total else 0
    if pct < 25:
        return "Foundation"
    if pct < 40:
        return "Beginner"
    if pct < 70:
        return "Intermediate"
    return "Advanced"


if __name__ == "__main__":
    from .db import init_db
    init_db()
    seed()
