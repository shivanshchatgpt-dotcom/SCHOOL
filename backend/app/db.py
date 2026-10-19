"""SQLite database layer for PySchool. Uses Python's built-in sqlite3."""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "pyschool.db"


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


SCHEMA = """
CREATE TABLE IF NOT EXISTS meta (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    icon TEXT NOT NULL DEFAULT '🌊',
    depth_label TEXT NOT NULL DEFAULT 'Surface',
    sort_order INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS paths (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id INTEGER NOT NULL REFERENCES categories(id),
    name TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    libraries TEXT NOT NULL DEFAULT '',
    slug TEXT NOT NULL UNIQUE,
    difficulty INTEGER NOT NULL DEFAULT 1,
    is_launch_ready INTEGER NOT NULL DEFAULT 0,
    duration_days INTEGER NOT NULL DEFAULT 180
);

CREATE TABLE IF NOT EXISTS assessment_questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    path_id INTEGER NOT NULL REFERENCES paths(id),
    question TEXT NOT NULL,
    option_a TEXT NOT NULL,
    option_b TEXT NOT NULL,
    option_c TEXT NOT NULL,
    option_d TEXT NOT NULL,
    correct TEXT NOT NULL,
    difficulty INTEGER NOT NULL DEFAULT 1,
    topic TEXT NOT NULL DEFAULT 'python-basics'
);

CREATE TABLE IF NOT EXISTS lessons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    path_id INTEGER NOT NULL REFERENCES paths(id),
    day_number INTEGER NOT NULL,
    title TEXT NOT NULL,
    theory TEXT NOT NULL,
    code_example TEXT NOT NULL DEFAULT '',
    questions TEXT NOT NULL DEFAULT '[]',
    answers TEXT NOT NULL DEFAULT '[]',
    homework TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL DEFAULT 'active',
    status_reason TEXT NOT NULL DEFAULT '',
    status_note TEXT NOT NULL DEFAULT '',
    day_type TEXT NOT NULL DEFAULT 'concept',
    UNIQUE(path_id, day_number)
);

CREATE TABLE IF NOT EXISTS milestones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    path_id INTEGER NOT NULL REFERENCES paths(id),
    code TEXT NOT NULL,
    title TEXT NOT NULL,
    domain TEXT NOT NULL,
    objective TEXT NOT NULL,
    estimated_minutes INTEGER NOT NULL DEFAULT 60,
    sort_order INTEGER NOT NULL,
    mastery_criteria TEXT NOT NULL,
    remediation_note TEXT NOT NULL DEFAULT '',
    UNIQUE(path_id, code),
    UNIQUE(path_id, sort_order)
);

CREATE TABLE IF NOT EXISTS milestone_prerequisites (
    milestone_id INTEGER NOT NULL REFERENCES milestones(id),
    prerequisite_milestone_id INTEGER NOT NULL REFERENCES milestones(id),
    PRIMARY KEY (milestone_id, prerequisite_milestone_id)
);

CREATE TABLE IF NOT EXISTS lesson_milestones (
    lesson_id INTEGER NOT NULL REFERENCES lessons(id),
    milestone_id INTEGER NOT NULL REFERENCES milestones(id),
    PRIMARY KEY (lesson_id, milestone_id)
);

CREATE TABLE IF NOT EXISTS assignments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lesson_id INTEGER NOT NULL UNIQUE REFERENCES lessons(id),
    prompt TEXT NOT NULL,
    required_patterns TEXT NOT NULL DEFAULT '[]',
    min_lines INTEGER NOT NULL DEFAULT 3,
    rubric TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS enrollments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL REFERENCES students(id),
    path_id INTEGER NOT NULL REFERENCES paths(id),
    level TEXT NOT NULL DEFAULT 'Beginner',
    level_score INTEGER NOT NULL DEFAULT 0,
    current_day INTEGER NOT NULL DEFAULT 1,
    streak INTEGER NOT NULL DEFAULT 0,
    penalty_points INTEGER NOT NULL DEFAULT 0,
    xp INTEGER NOT NULL DEFAULT 0,
    starting_milestone_id INTEGER REFERENCES milestones(id),
    enrolled_at TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(student_id, path_id)
);

CREATE TABLE IF NOT EXISTS lesson_progress (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    enrollment_id INTEGER NOT NULL REFERENCES enrollments(id),
    lesson_id INTEGER NOT NULL REFERENCES lessons(id),
    status TEXT NOT NULL DEFAULT 'assigned',
    submitted_at TEXT,
    passed INTEGER NOT NULL DEFAULT 0,
    UNIQUE(enrollment_id, lesson_id)
);

CREATE TABLE IF NOT EXISTS mastery_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    enrollment_id INTEGER NOT NULL REFERENCES enrollments(id),
    milestone_id INTEGER NOT NULL REFERENCES milestones(id),
    quiz_score INTEGER NOT NULL DEFAULT 0,
    code_passed INTEGER NOT NULL DEFAULT 0,
    status TEXT NOT NULL DEFAULT 'in_progress',
    mastered_at TEXT,
    UNIQUE(enrollment_id, milestone_id)
);

CREATE TABLE IF NOT EXISTS homework_submissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    enrollment_id INTEGER NOT NULL REFERENCES enrollments(id),
    lesson_id INTEGER NOT NULL REFERENCES lessons(id),
    code TEXT NOT NULL DEFAULT '',
    checked_at TEXT,
    passed INTEGER NOT NULL DEFAULT 0,
    feedback TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    enrollment_id INTEGER NOT NULL REFERENCES enrollments(id),
    day INTEGER NOT NULL,
    date TEXT NOT NULL DEFAULT (date('now')),
    present INTEGER NOT NULL DEFAULT 0,
    UNIQUE(enrollment_id, day)
);

CREATE TABLE IF NOT EXISTS profile_questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key TEXT NOT NULL UNIQUE,
    question TEXT NOT NULL,
    options TEXT NOT NULL DEFAULT '[]',
    sort_order INTEGER NOT NULL DEFAULT 0
);

-- Concept-level learner state: what this student has shown they know and do
-- not. Written from placement misses and homework evidence, read back to
-- personalise the next lesson. Deliberately small: one row per weak/strong
-- topic per learner, not a record of everything they ever touched.
CREATE TABLE IF NOT EXISTS learner_topics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    enrollment_id INTEGER NOT NULL REFERENCES enrollments(id),
    topic TEXT NOT NULL,
    source TEXT NOT NULL DEFAULT 'homework',
    ref_day INTEGER,
    misses INTEGER NOT NULL DEFAULT 0,
    hits INTEGER NOT NULL DEFAULT 0,
    last_seen TEXT,
    UNIQUE(enrollment_id, topic, source)
);
"""


def init_db() -> None:
    conn = get_conn()
    try:
        conn.executescript(SCHEMA)
        # Small, forward-compatible migrations for databases created by early MVPs.
        _add_column_if_missing(conn, "paths", "is_launch_ready INTEGER NOT NULL DEFAULT 0")
        _add_column_if_missing(conn, "paths", "duration_days INTEGER NOT NULL DEFAULT 180")
        _add_column_if_missing(conn, "assessment_questions", "topic TEXT NOT NULL DEFAULT 'python-basics'")
        _add_column_if_missing(conn, "enrollments", "starting_milestone_id INTEGER REFERENCES milestones(id)")
        _add_column_if_missing(conn, "enrollments", "access_token TEXT")
        _add_column_if_missing(conn, "enrollments", "profile TEXT NOT NULL DEFAULT '{}'")
        _add_column_if_missing(conn, "lessons", "status TEXT NOT NULL DEFAULT 'active'")
        _add_column_if_missing(conn, "lessons", "status_reason TEXT NOT NULL DEFAULT ''")
        _add_column_if_missing(conn, "lessons", "status_note TEXT NOT NULL DEFAULT ''")
        _add_column_if_missing(conn, "lessons", "day_type TEXT NOT NULL DEFAULT 'concept'")
        # Backfill random access tokens for enrollments created before the
        # MVP access-control change, so every row is protected.
        import secrets

        for row in conn.execute("SELECT id FROM enrollments WHERE access_token IS NULL").fetchall():
            conn.execute(
                "UPDATE enrollments SET access_token = ? WHERE id = ?",
                (secrets.token_urlsafe(24), row["id"]),
            )
        conn.commit()
    finally:
        conn.close()


def _add_column_if_missing(conn: sqlite3.Connection, table: str, definition: str) -> None:
    column = definition.split()[0]
    existing = {row["name"] for row in conn.execute(f"PRAGMA table_info({table})")}
    if column not in existing:
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {definition}")
