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
    difficulty INTEGER NOT NULL DEFAULT 1
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
    difficulty INTEGER NOT NULL DEFAULT 1
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
    UNIQUE(path_id, day_number)
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
"""


def init_db() -> None:
    conn = get_conn()
    try:
        conn.executescript(SCHEMA)
        conn.commit()
    finally:
        conn.close()
