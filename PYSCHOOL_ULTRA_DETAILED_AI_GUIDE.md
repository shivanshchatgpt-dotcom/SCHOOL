# PySchool - ULTRA DETAILED AI GUIDE
## 100% Complete Understanding for Any AI System

---

## 🎯 QUICK START FOR AI

**IF YOU ARE AN AI READING THIS:** This single file contains EVERYTHING you need to understand the PySchool project completely. You will find:
- ✅ Complete system architecture
- ✅ Every line of important code explained
- ✅ Database schema with actual SQL
- ✅ API endpoints with actual request/response examples
- ✅ Step-by-step workflow with real data
- ✅ File-by-file breakdown
- ✅ Safety mechanisms explained
- ✅ How to run, test, and extend the project

**Estimated Reading Time for AI:** 5-10 minutes to achieve 100% understanding

---

# 📌 TABLE OF CONTENTS (Jump to Section)

1. [EXECUTIVE SUMMARY - What PySchool Does](#-executive-summary)
2. [CORE CONCEPT - The Learning Philosophy](#-core-concept)
3. [SYSTEM ARCHITECTURE - How Everything Connects](#-system-architecture)
4. [DATABASE - Complete Schema with Actual SQL](#-database-complete-schema)
5. [BACKEND - File by File Breakdown with Code](#-backend-file-by-file)
6. [FRONTEND - Component by Component with Code](#-frontend-component-by-component)
7. [API - Every Endpoint with Real Examples](#-api-every-endpoint-with-examples)
8. [WORKFLOW - Step by Step User Journey](#-workflow-step-by-step)
9. [CURRICULUM - How Lessons Are Structured](#-curriculum-how-lessons-are-structured)
10. [SAFETY - Why Student Code Never Executes](#-safety-why-student-code-never-executes)
11. [HOW TO RUN - Exact Commands](#-how-to-run-exact-commands)
12. [CODE EXAMPLES - Real Snippets You Can Copy](#-code-examples-real-snippets)
13. [DEBUGGING - Common Issues and Fixes](#-debugging-common-issues)
14. [EXTENDING - How to Add New Features](#-extending-how-to-add-new-features)

---

# 🎯 EXECUTIVE SUMMARY

## What PySchool Is

PySchool is a **goal-based Python learning platform** that works like a real school. Instead of students wandering through endless free resources, they:

```
1. PICK A CAREER PATH (What they want to become)
   ↓
2. TAKE A PLACEMENT TEST (Determines their level)
   ↓
3. GET A DAILY 1-HOUR CLASS (Structured lesson)
   ↓
4. DO HOMEWORK (Code that gets checked)
   ↓
5. TRACK PROGRESS (XP, streaks, completion %)
   ↓
6. REPEAT FOR 180 DAYS
```

## The Problem It Solves

```
BEFORE PySchool:
- Too many free Python resources
- Students don't know where to start
- No structure, no progression
- Overwhelming choices

AFTER PySchool:
- Clear career paths
- Deterministic placement
- Structured daily lessons
- Automated progress tracking
```

## Key Numbers

```
📊 100 Career Paths (organized in 10 categories)
🎯 3 Fully Implemented Paths (180 days each)
📚 540 Total Lessons (180 per path)
✅ 1,300+ Assessment Questions
💾 15 Database Tables
🔌 22 API Endpoints
💻 ~7,000 Lines of Code
```

---

# 🧠 CORE CONCEPT

## The Learning Philosophy

### Principle 1: Goal-Oriented Learning
```
INSTEAD OF: "Learn Python"
PYSCHOOL: "Become a Web Developer" or "Become a Data Scientist"
```

### Principle 2: Deterministic Placement
```
Same answers = Same placement = Same starting point
No randomness, no luck, just transparent assessment
```

### Principle 3: Daily Commitment
```
1 hour per day × 180 days = Python mastery
Realistic for college students with other courses
```

### Principle 4: Safe Practice
```
Student code is NEVER executed on the server
Only parsed for syntax and patterns
100% safe from malicious code
```

### Principle 5: Progressive Mastery
```
Theory → Example → Practice → Check → Explain → Review
Each step builds on the previous one
```

---

# 🏗️ SYSTEM ARCHITECTURE

## Visual Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              USER (Browser)                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    FRONTEND (React/TypeScript)                         │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                     │   │
│  │  │   Home      │  │   Paths     │  │  Assessment  │                     │   │
│  │  │ (Landing)   │  │ (Catalog)   │  │ (Test)      │                     │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘                     │   │
│  │  ┌─────────────────────────────────────────────────────────────┐   │   │
│  │  │                         Dashboard                                 │   │   │
│  │  │  (Daily Learning Interface)                                     │   │   │
│  │  └─────────────────────────────────────────────────────────────┘   │   │
│  │                                                                      │   │
│  │  ┌─────────────────────────────────────────────────────────────┐   │   │
│  │  │                    api.ts (HTTP Client)                          │   │   │
│  │  │  - GET /api/categories                                          │   │   │
│  │  │  - GET /api/paths                                               │   │   │
│  │  │  - POST /api/assessment/submit                                 │   │   │
│  │  │  - GET /api/enrollments/{id}/lesson                            │   │   │
│  │  │  - POST /api/homework/submit                                   │   │   │
│  │  │  - POST /api/enrollments/{id}/complete                        │   │   │
│  │  └─────────────────────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                              │                                             │
│                              ▼ (HTTP Requests + Headers)                  │
│                              │                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           NETWORK (localhost:8000)                            │
└─────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                             BACKEND (FastAPI)                               │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         main.py (Entrypoint)                           │   │
│  │  - FastAPI app initialization                                        │   │
│  │  - CORS middleware setup                                              │   │
│  │  - Database connection (SQLite)                                       │   │
│  │  - Seed on startup (idempotent)                                        │   │
│  │  - Router registration                                                │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                      │   │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │   │
│  │  paths.py   │  │ assessment.py│  │  lessons.py │  │ dashboard.py │    │   │
│  │ (Catalog)   │  │ (Test)       │  │ (Learning)  │  │ (Progress)  │    │   │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘    │   │
│                                                                      │   │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         admin.py (Teacher)                            │   │
│  │  - View all students                                                 │   │
│  │  - View all enrollments                                               │   │
│  │  - Add/remove penalty points                                          │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                      │   │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      Authentication Layer                             │   │
│  │  - verify_enrollment_token() for student endpoints                     │   │
│  │  - require_admin() for admin endpoints                                │   │
│  │  - HMAC-safe token comparison                                        │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                      │   │
└─────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           DATABASE (SQLite: pyschool.db)                       │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                       │
│  │  categories  │  │    paths    │  │  students   │                       │
│  │   (10)      │  │   (100)     │  │   (N)      │                       │
│  └─────────────┘  └─────────────┘  └─────────────┘                       │
│         │               │               │                               │
│         ▼               ▼               ▼                               │
│  ┌─────────────────────┐ ┌─────────────┐ ┌─────────────┐               │
│  │  assessment_        │ │   lessons    │ │  enrollments│               │
│  │   questions          │ │   (540)      │ │   (N)       │               │
│  └─────────────────────┘ └─────────────┘ └─────────────┘               │
│                              │               │                               │
│                              ▼               ▼                               │
│                     ┌─────────────────┐ ┌─────────────┐                │
│                     │  milestones      │ │  homework_  │                │
│                     │   (540)          │ │  submissions│                │
│                     └─────────────────┘ └─────────────┘                │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

# 🗃️ DATABASE - COMPLETE SCHEMA

## Actual SQL Schema (from db.py)

```sql
-- Table 1: Meta (Application metadata)
CREATE TABLE IF NOT EXISTS meta (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

-- Table 2: Categories (10 learning domains)
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    icon TEXT NOT NULL DEFAULT '🌊',
    depth_label TEXT NOT NULL DEFAULT 'Surface',
    sort_order INTEGER NOT NULL DEFAULT 0
);

-- Table 3: Paths (100 career paths)
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

-- Table 4: Assessment Questions (~1,300 total)
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

-- Table 5: Lessons (540 total)
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

-- Table 6: Milestones (540 total)
CREATE TABLE IF NOT EXISTS milestones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    path_id INTEGER NOT NOT NULL REFERENCES paths(id),
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

-- Table 7: Milestone Prerequisites
CREATE TABLE IF NOT EXISTS milestone_prerequisites (
    milestone_id INTEGER NOT NULL REFERENCES milestones(id),
    prerequisite_milestone_id INTEGER NOT NULL REFERENCES milestones(id),
    PRIMARY KEY (milestone_id, prerequisite_milestone_id)
);

-- Table 8: Lesson-Milestone Mapping
CREATE TABLE IF NOT EXISTS lesson_milestones (
    lesson_id INTEGER NOT NULL REFERENCES lessons(id),
    milestone_id INTEGER NOT NULL REFERENCES milestones(id),
    PRIMARY KEY (lesson_id, milestone_id)
);

-- Table 9: Assignments (540 total)
CREATE TABLE IF NOT EXISTS assignments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lesson_id INTEGER NOT NULL UNIQUE REFERENCES lessons(id),
    prompt TEXT NOT NULL,
    required_patterns TEXT NOT NULL DEFAULT '[]',
    min_lines INTEGER NOT NULL DEFAULT 3,
    rubric TEXT NOT NULL DEFAULT ''
);

-- Table 10: Students
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Table 11: Enrollments
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
    access_token TEXT,  -- MVP-safe access control
    enrolled_at TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(student_id, path_id)
);

-- Table 12: Lesson Progress
CREATE TABLE IF NOT EXISTS lesson_progress (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    enrollment_id INTEGER NOT NULL REFERENCES enrollments(id),
    lesson_id INTEGER NOT NULL REFERENCES lessons(id),
    status TEXT NOT NULL DEFAULT 'assigned',
    submitted_at TEXT,
    passed INTEGER NOT NULL DEFAULT 0,
    UNIQUE(enrollment_id, lesson_id)
);

-- Table 13: Mastery Records
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

-- Table 14: Homework Submissions
CREATE TABLE IF NOT EXISTS homework_submissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    enrollment_id INTEGER NOT NULL REFERENCES enrollments(id),
    lesson_id INTEGER NOT NULL REFERENCES lessons(id),
    code TEXT NOT NULL DEFAULT '',
    checked_at TEXT,
    passed INTEGER NOT NULL DEFAULT 0,
    feedback TEXT NOT NULL DEFAULT ''
);

-- Table 15: Attendance
CREATE TABLE IF NOT EXISTS attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    enrollment_id INTEGER NOT NULL REFERENCES enrollments(id),
    day INTEGER NOT NULL,
    date TEXT NOT NULL DEFAULT (date('now')),
    present INTEGER NOT NULL DEFAULT 0,
    UNIQUE(enrollment_id, day)
);
```

---

# 💻 BACKEND - FILE BY FILE BREAKDOWN

## File: backend/app/main.py (The Heart of the Backend)

```python
"""PySchool — FastAPI application entrypoint."""
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from .db import init_db
from .seed import seed
from .routers import paths, assessment, lessons, dashboard, admin


@asynccontextmanager
async def lifespan(app: FastAPI):
    # THIS IS CRUCIAL: Database is initialized and seeded on startup
    init_db()      # Creates tables if they don't exist
    seed()         # Populates tables with data (categories, paths, lessons, etc.)
    yield


app = FastAPI(
    title="PySchool API",
    version="0.1.0",
    lifespan=lifespan  # This runs init_db() and seed() when app starts
)

# CORS Configuration - Security Feature
_default_origins = "http://localhost:5173,http://127.0.0.1:5173"
_cors_origins = [
    origin.strip()
    for origin in os.environ.get("PYSCHOOL_CORS_ORIGINS", _default_origins).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,      # Only these origins can access API
    allow_credentials=True,             # Allows cookies if needed
    allow_methods=["*"],               # All HTTP methods allowed
    allow_headers=["*"],               # All headers allowed
)

# Register all routers (each router is a group of endpoints)
app.include_router(paths.router, prefix="/api", tags=["paths"])
app.include_router(assessment.router, prefix="/api", tags=["assessment"])
app.include_router(lessons.router, prefix="/api", tags=["lessons"])
app.include_router(dashboard.router, prefix="/api", tags=["dashboard"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])


@app.get("/", include_in_schema=False)
def frontend_redirect():
    # Redirects root to frontend URL
    frontend_url = os.environ.get("PYSCHOOL_FRONTEND_URL", "http://127.0.0.1:5173/")
    return RedirectResponse(url=frontend_url)


@app.get("/api/health")
def health():
    # Health check endpoint - used to verify backend is running
    return {"status": "ok", "app": "PySchool"}
```

**KEY POINTS:**
- Uses FastAPI (modern Python web framework)
- Database initialized and seeded automatically on startup
- CORS restricted to specific origins (security)
- 5 router groups registered
- Health check endpoint for monitoring

---

## File: backend/app/db.py (Database Layer)

```python
"""SQLite database layer for PySchool. Uses Python's built-in sqlite3."""
import sqlite3
from pathlib import Path

# Database file location (relative to this file)
DB_PATH = Path(__file__).resolve().parent.parent / "pyschool.db"


def get_conn() -> sqlite3.Connection:
    """Get a database connection with proper settings"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row      # Return rows as dictionaries
    conn.execute("PRAGMA foreign_keys = ON")  # Enforce foreign key constraints
    return conn
```

**SCHEMA:** (Already shown above - all 15 tables)

**MIGRATION SYSTEM:**
```python
def _add_column_if_missing(conn: sqlite3.Connection, table: str, definition: str) -> None:
    """Add a column if it doesn't exist (for backward compatibility)"""
    column = definition.split()[0]  # Extract column name from definition
    existing = {row["name"] for row in conn.execute(f"PRAGMA table_info({table})")}
    if column not in existing:
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {definition}")


def init_db() -> None:
    """Initialize database: create all tables and run migrations"""
    conn = get_conn()
    try:
        # Execute the entire schema (all CREATE TABLE statements)
        conn.executescript(SCHEMA)
        
        # Run migrations for older databases
        _add_column_if_missing(conn, "paths", "is_launch_ready INTEGER NOT NULL DEFAULT 0")
        _add_column_if_missing(conn, "paths", "duration_days INTEGER NOT NULL DEFAULT 180")
        _add_column_if_missing(conn, "assessment_questions", "topic TEXT NOT NULL DEFAULT 'python-basics'")
        _add_column_if_missing(conn, "enrollments", "starting_milestone_id INTEGER REFERENCES milestones(id)")
        _add_column_if_missing(conn, "enrollments", "access_token TEXT")
        
        # Backfill access tokens for existing enrollments
        import secrets
        for row in conn.execute("SELECT id FROM enrollments WHERE access_token IS NULL").fetchall():
            conn.execute(
                "UPDATE enrollments SET access_token = ? WHERE id = ?",
                (secrets.token_urlsafe(24), row["id"]),
            )
        conn.commit()
    finally:
        conn.close()
```

**KEY POINTS:**
- SQLite database (no server needed, file-based)
- Foreign key constraints enabled
- Automatic migrations for backward compatibility
- Access tokens backfilled for security

---

## File: backend/app/schemas.py (Data Models)

```python
"""Pydantic schemas for PySchool API."""
from pydantic import BaseModel


# CATEGORY SCHEMAS
class CategoryOut(BaseModel):
    id: int
    name: str
    icon: str
    depth_label: str
    sort_order: int


# PATH SCHEMAS
class PathOut(BaseModel):
    id: int
    category_id: int
    name: str
    description: str
    libraries: str
    slug: str
    difficulty: int


class PathDetailOut(PathOut):
    category_name: str
    category_icon: str
    assessment_count: int


# ASSESSMENT SCHEMAS
class QuestionOut(BaseModel):
    id: int
    path_id: int
    question: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    difficulty: int


class AssessmentAnswer(BaseModel):
    question_id: int
    selected: str


class AssessmentSubmit(BaseModel):
    path_id: int
    student_name: str
    student_email: str
    answers: list[AssessmentAnswer]


class AssessmentResultOut(BaseModel):
    enrollment_id: int
    student_id: int
    path_id: int
    score: int
    total: int
    level: str
    feedback: str
    # Additional fields returned but not in schema (for flexibility)
    # starting_milestone, weak_topics, access_token


# LESSON SCHEMAS
class LessonOut(BaseModel):
    id: int
    path_id: int
    day_number: int
    title: str
    theory: str
    code_example: str
    questions: list[str]
    answers: list[str]
    homework: str


# HOMEWORK SCHEMAS
class HomeworkSubmit(BaseModel):
    enrollment_id: int
    lesson_id: int
    code: str


class HomeworkResultOut(BaseModel):
    passed: bool
    feedback: str


# ENROLLMENT SCHEMAS
class EnrollmentOut(BaseModel):
    id: int
    path_id: int
    path_name: str
    level: str
    level_score: int
    current_day: int
    streak: int
    penalty_points: int
    xp: int


# STUDENT SCHEMAS
class StudentCreate(BaseModel):
    name: str
    email: str


class AttendanceOut(BaseModel):
    day: int
    date: str
    present: int
```

**KEY POINTS:**
- Pydantic models for request/response validation
- Type hints for all fields
- Separate schemas for input/output
- Inheritance for extended models

---

## Router: backend/app/routers/paths.py

```python
"""Category + path browsing endpoints."""
from fastapi import APIRouter, HTTPException
from ..db import get_conn

router = APIRouter()


@router.get("/categories")
def list_categories(include_future: bool = False):
    """
    Get all categories.
    By default, only returns categories that have launch-ready paths.
    """
    conn = get_conn()
    try:
        query = "SELECT id, name, icon, depth_label, sort_order FROM categories"
        if not include_future:
            # Only show categories with at least one launch-ready path
            query += " WHERE EXISTS (SELECT 1 FROM paths WHERE paths.category_id = categories.id AND paths.is_launch_ready = 1)"
        query += " ORDER BY sort_order"
        rows = conn.execute(query).fetchall()
        return [dict(r) for r in rows]  # Convert SQLite rows to dicts
    finally:
        conn.close()


@router.get("/paths")
def list_paths(category_id: int | None = None, q: str | None = None, include_future: bool = False):
    """
    Get all paths with optional filtering.
    By default, only returns launch-ready paths.
    """
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
        if q:  # Search query
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
            # Rename category_id to match schema (it was popping it above)
            d["category_id"] = d.pop("category_id")
            d["assessment_count"] = d.pop("assessment_count")
            result.append(d)
        return result
    finally:
        conn.close()


@router.get("/paths/{slug}")
def path_detail(slug: str):
    """
    Get details for a specific path by slug.
    """
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
```

**KEY POINTS:**
- 3 endpoints: categories, paths, path detail
- Filtering by category, search, launch-ready status
- Returns enriched data with joins
- Proper error handling (404 for not found)

---

## Router: backend/app/routers/assessment.py (The Most Important Router)

```python
"""Assessment endpoints: fetch questions, submit answers, judge level, enroll."""
import secrets
from fastapi import APIRouter, HTTPException
from ..db import get_conn
from ..schemas import AssessmentSubmit
from ..seed import get_level  # Function to calculate level from score

router = APIRouter()


@router.get("/assessment/{path_id}/questions")
def get_questions(path_id: int):
    """
    Get all assessment questions for a path.
    Ordered by difficulty (easiest first).
    """
    conn = get_conn()
    try:
        rows = conn.execute(
            """
            SELECT id, path_id, question, option_a, option_b, option_c, option_d, difficulty
            FROM assessment_questions
            WHERE path_id = ?
            ORDER BY difficulty
            """,
            (path_id,),
        ).fetchall()
        if not rows:
            raise HTTPException(status_code=404, detail="No assessment questions for this path")
        return [dict(r) for r in rows]
    finally:
        conn.close()


@router.post("/assessment/submit")
def submit_assessment(payload: AssessmentSubmit):
    """
    Submit assessment answers, calculate level, create enrollment.
    This is where students get placed into their starting point.
    """
    conn = get_conn()
    try:
        # 1. Verify path exists and is launch-ready
        path_row = conn.execute("SELECT * FROM paths WHERE id = ?", (payload.path_id,)).fetchone()
        if not path_row:
            raise HTTPException(status_code=404, detail="Path not found")
        if not path_row["is_launch_ready"]:
            raise HTTPException(
                status_code=409, 
                detail="This path is in the future catalog and does not have a curriculum yet."
            )

        # 2. Validate student info
        name = payload.student_name.strip()
        email = payload.student_email.strip().lower()
        if not name or "@" not in email:
            raise HTTPException(status_code=422, detail="Please provide a name and a valid email address.")

        # 3. Create or get student
        student = conn.execute(
            "SELECT id FROM students WHERE email = ?", (email,)
        ).fetchone()
        
        if student:
            student_id = student["id"]
        else:
            cur = conn.execute(
                "INSERT INTO students (name, email) VALUES (?, ?)",
                (name, email),
            )
            student_id = cur.lastrowid

        # 4. Grade the answers
        questions = conn.execute(
            "SELECT id, correct, topic FROM assessment_questions WHERE path_id = ?", 
            (payload.path_id,)
        ).fetchall()
        
        # Build a dict of submitted answers: {question_id: selected_answer}
        submitted = {answer.question_id: answer.selected.upper() for answer in payload.answers}
        
        # Calculate score
        score = sum(1 for question in questions if submitted.get(question["id"]) == question["correct"])
        total = len(questions)
        
        # Determine level based on score percentage
        level = get_level(score, total)
        
        # Find weak topics (missed questions' topics)
        missed_topics = sorted({
            question["topic"] 
            for question in questions 
            if submitted.get(question["id"]) != question["correct"]
        })

        # 5. Determine starting milestone based on level
        # Foundation -> Day 1, Beginner -> Day 4, Intermediate -> Day 7, Advanced -> Day 10
        start_order = 1 if level == "Foundation" else (
            4 if level == "Beginner" else (7 if level == "Intermediate" else 10)
        )
        
        starting_milestone = conn.execute(
            "SELECT id, code, title FROM milestones WHERE path_id = ? AND sort_order = ?",
            (payload.path_id, start_order),
        ).fetchone()
        
        if not starting_milestone:
            raise HTTPException(status_code=500, detail="Curriculum is not available for this path")

        # 6. Create or update enrollment
        existing = conn.execute(
            "SELECT id FROM enrollments WHERE student_id = ? AND path_id = ?",
            (student_id, payload.path_id),
        ).fetchone()
        
        if existing:
            # Update existing enrollment
            conn.execute(
                "UPDATE enrollments SET level = ?, level_score = ?, current_day = ?, starting_milestone_id = ? WHERE id = ?",
                (level, score, start_order, starting_milestone["id"], existing["id"]),
            )
            enrollment_id = existing["id"]
            existing_token_row = conn.execute(
                "SELECT access_token FROM enrollments WHERE id = ?", (enrollment_id,)
            ).fetchone()
            access_token = existing_token_row["access_token"] or secrets.token_urlsafe(24)
            feedback = "Assessment re-done — level updated."
        else:
            # Create new enrollment
            access_token = secrets.token_urlsafe(24)
            cur = conn.execute(
                """INSERT INTO enrollments 
                   (student_id, path_id, level, level_score, current_day, starting_milestone_id, access_token) 
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (student_id, payload.path_id, level, score, start_order, starting_milestone["id"], access_token),
            )
            enrollment_id = cur.lastrowid
            feedback = (
                f"Welcome, {name}! Your placement is {level}. Start at {starting_milestone['code']}: "
                f"{starting_milestone['title']}."
            )

        conn.commit()
        
        # 7. Return the result (includes access token for future requests)
        return {
            "enrollment_id": enrollment_id,
            "student_id": student_id,
            "path_id": payload.path_id,
            "score": score,
            "total": total,
            "level": level,
            "feedback": feedback,
            "starting_milestone": dict(starting_milestone),
            "weak_topics": missed_topics,
            "access_token": access_token,  # MVP-safe: browser stores this
        }
    finally:
        conn.close()
```

**KEY POINTS:**
- 2 endpoints: get questions, submit assessment
- Complete placement logic
- Student creation/updating
- Enrollment creation with access token
- Level calculation: Foundation (<25%), Beginner (25-40%), Intermediate (40-70%), Advanced (>70%)
- Starting milestone: Day 1, 4, 7, or 10 based on level

---

## Router: backend/app/routers/lessons.py (The Learning Engine)

```python
"""Authored lessons, safe assignment checks, and progress gates."""
import ast
import json
import re
import hmac
from fastapi import APIRouter, Depends, HTTPException
from fastapi.params import Header
from ..db import get_conn
from ..schemas import HomeworkSubmit

router = APIRouter()


def verify_enrollment_token(
    enrollment_id: int,
    x_enrollment_token: str | None = Header(default=None, alias="X-Enrollment-Token"),
) -> None:
    """
    MVP-safe access control: requests must present the enrollment's token.
    The token is issued once at assessment time and kept in the student's browser.
    """
    conn = get_conn()
    try:
        row = conn.execute(
            "SELECT access_token FROM enrollments WHERE id = ?", (enrollment_id,)
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Enrollment not found")
        stored = row["access_token"]
        
        # Validate token format
        if not stored or not x_enrollment_token or not re.fullmatch(r"[\w-]+", x_enrollment_token):
            raise HTTPException(
                status_code=401,
                detail="Missing or invalid enrollment token. Please re-enroll from the path page.",
            )
        
        # HMAC-safe comparison (prevents timing attacks)
        if not hmac.compare_digest(stored.encode(), x_enrollment_token.encode()):
            raise HTTPException(status_code=401, detail="This learner session does not match this enrollment.")
    finally:
        conn.close()


# Whitespace-tolerant pattern matching for code checking
def _rubric_regex(pattern: str) -> re.Pattern:
    """
    Compile a rubric pattern into a whitespace-tolerant regex.
    Example: "print(" matches "print(x)", "print (x)", "print(  x)"
    """
    pieces: list[str] = []
    for token in pattern.split():
        piece = ""
        for index, char in enumerate(token):
            piece += re.escape(char)
            nxt = token[index + 1] if index + 1 < len(token) else None
            if nxt is not None and _is_word(char) != _is_word(nxt):
                piece += r"\s*"  # Allow optional whitespace
        if _is_word(token[0]):
            piece = r"\b" + piece  # Word boundary at start
        if _is_word(token[-1]):
            piece += r"\b"  # Word boundary at end
        pieces.append(piece)
    return re.compile(r"\s+".join(pieces))


def pattern_found(pattern: str, code: str) -> bool:
    """Check if a pattern exists in code (whitespace-tolerant)."""
    return _rubric_regex(pattern).search(code) is not None


@router.get("/enrollments/{enrollment_id}/lesson")
def get_lesson(enrollment_id: int, day: int | None = None, 
               _: None = Depends(verify_enrollment_token)):
    """
    Return an authored lesson and its transparent coding rubric.
    """
    conn = get_conn()
    try:
        # Get current day if not specified
        target_day = day or conn.execute(
            "SELECT current_day FROM enrollments WHERE id = ?", (enrollment_id,)
        ).fetchone()["current_day"]
        
        # Get lesson with milestone and assignment data
        lesson = conn.execute(
            """
            SELECT l.*, m.id AS milestone_id, m.code AS milestone_code, m.domain,
                   m.objective, m.mastery_criteria, m.remediation_note,
                   a.id AS assignment_id, a.prompt AS assignment_prompt,
                   a.required_patterns, a.min_lines, a.rubric
            FROM enrollments e
            JOIN lessons l ON l.path_id = e.path_id AND l.day_number = ?
            JOIN lesson_milestones lm ON lm.lesson_id = l.id
            JOIN milestones m ON m.id = lm.milestone_id
            LEFT JOIN assignments a ON a.lesson_id = l.id
            WHERE e.id = ?
            """,
            (target_day, enrollment_id),
        ).fetchone()
        
        if not lesson:
            raise HTTPException(
                status_code=409,
                detail="This 180-day programme is complete. Your next module will be published separately.",
            )
        
        # Get latest submission
        submission = conn.execute(
            """SELECT passed, feedback FROM homework_submissions
               WHERE enrollment_id = ? AND lesson_id = ? ORDER BY id DESC LIMIT 1""",
            (enrollment_id, lesson["id"]),
        ).fetchone()
        
        return {
            "id": lesson["id"],
            "path_id": lesson["path_id"],
            "day_number": lesson["day_number"],
            "title": lesson["title"],
            "theory": lesson["theory"],
            "code_example": lesson["code_example"],
            "questions": json.loads(lesson["questions"]),
            "answers": json.loads(lesson["answers"]),
            "homework": lesson["homework"],
            "generated": False,
            "milestone": {
                "id": lesson["milestone_id"],
                "code": lesson["milestone_code"],
                "domain": lesson["domain"],
                "objective": lesson["objective"],
                "mastery_criteria": lesson["mastery_criteria"],
                "remediation_note": lesson["remediation_note"],
            },
            "assignment": {
                "id": lesson["assignment_id"],
                "prompt": lesson["assignment_prompt"],
                "required_patterns": json.loads(lesson["required_patterns"]),
                "min_lines": lesson["min_lines"],
                "rubric": lesson["rubric"],
            },
            "submission": dict(submission) if submission else None,
        }
    finally:
        conn.close()


@router.post("/homework/submit")
def submit_homework(payload: HomeworkSubmit, 
                    x_enrollment_token: str | None = Header(default=None, alias="X-Enrollment-Token")):
    """
    Check source structure only. Student code is NEVER executed by this API.
    Returns structured per-requirement results.
    """
    conn = get_conn()
    try:
        # Verify token
        token_row = conn.execute(
            "SELECT access_token FROM enrollments WHERE id = ?", (payload.enrollment_id,)
        ).fetchone()
        if not token_row:
            raise HTTPException(status_code=404, detail="Enrollment not found")
        
        import hmac
        stored = token_row["access_token"] or ""
        if not x_enrollment_token or not hmac.compare_digest(stored.encode(), x_enrollment_token.encode()):
            raise HTTPException(
                status_code=401,
                detail="Missing or invalid enrollment token. Please re-enroll from the path page.",
            )

        # Get enrollment and lesson
        enrollment = conn.execute(
            "SELECT * FROM enrollments WHERE id = ?", (payload.enrollment_id,)
        ).fetchone()
        lesson = conn.execute(
            """
            SELECT l.*, a.required_patterns, a.min_lines
            FROM lessons l
            JOIN lesson_milestones lm ON lm.lesson_id = l.id
            JOIN milestones m ON m.id = lm.milestone_id
            JOIN assignments a ON a.lesson_id = l.id
            WHERE l.path_id = ? AND l.day_number = ?
            """,
            (enrollment["path_id"], enrollment["current_day"]),
        ).fetchone()
        
        if not lesson or lesson["id"] != payload.lesson_id:
            raise HTTPException(status_code=409, detail="Submit the assignment for your current milestone only.")

        feedback: list[str] = []

        # CHECK 1: Syntax (AST parse only — NEVER executed)
        try:
            ast.parse(payload.code)
            syntax_ok = True
            feedback.append("Python syntax looks valid.")
        except SyntaxError as error:
            syntax_ok = False
            hint = ""
            if error.msg and "invalid" in error.msg.lower():
                hint = " Check for a missing colon, bracket or quote just before that line."
            feedback.append(f"Syntax error on line {error.lineno}: {error.msg}.{hint}")

        # CHECK 2: Minimum non-empty lines
        non_empty_lines = [line for line in payload.code.splitlines() if line.strip()]
        min_lines = lesson["min_lines"] or 3
        line_ok = len(non_empty_lines) >= min_lines
        if line_ok:
            feedback.append(f"You wrote {len(non_empty_lines)} non-empty lines (need {min_lines}). ✓")
        else:
            feedback.append(
                f"You wrote {len(non_empty_lines)} non-empty line(s) but today's rubric needs at least {min_lines}."
            )

        # CHECK 3: Required language constructs (whitespace-tolerant)
        patterns = json.loads(lesson["required_patterns"]) if lesson["required_patterns"] else []
        pattern_results = [
            {"pattern": pattern, "found": pattern_found(pattern, payload.code)}
            for pattern in patterns
        ]
        missing = [item["pattern"] for item in pattern_results if not item["found"]]
        if missing:
            feedback.append(
                "Required concept(s) not detected yet: "
                + ", ".join(f"`{item}`" for item in missing)
                + ". Write real code using them — spacing before brackets like `print (...)` is fine."
            )
        elif patterns:
            feedback.append("All required language constructs found. ✓")

        # Determine if passed
        passed = syntax_ok and line_ok and not missing
        
        # Check if already passed before
        already_passed = conn.execute(
            "SELECT 1 FROM homework_submissions WHERE enrollment_id = ? AND lesson_id = ? AND passed = 1",
            (payload.enrollment_id, payload.lesson_id),
        ).fetchone()
        
        if passed:
            feedback.append("Practice rubric passed. You can now complete the milestone.")
        else:
            feedback.append(
                "Not passed yet. Fix the failed checks above and submit again—no penalty is added for practice."
            )
        
        # Save submission
        conn.execute(
            """INSERT INTO homework_submissions 
               (enrollment_id, lesson_id, code, passed, feedback, checked_at)
               VALUES (?, ?, ?, ?, ?, datetime('now'))""",
            (payload.enrollment_id, payload.lesson_id, payload.code, int(passed), " ".join(feedback)),
        )
        
        # Award bonus XP for first-time pass
        if passed and not already_passed:
            conn.execute("UPDATE enrollments SET xp = xp + 15 WHERE id = ?", (payload.enrollment_id,))
        
        conn.commit()
        
        return {
            "passed": passed,
            "feedback": " ".join(feedback),
            "penalty_added": False,
            "checks": {
                "syntax_ok": syntax_ok,
                "lines_written": len(non_empty_lines),
                "min_lines": min_lines,
                "lines_ok": line_ok,
                "patterns": pattern_results,
            },
        }
    finally:
        conn.close()


@router.post("/enrollments/{enrollment_id}/complete")
def complete_lesson(enrollment_id: int, 
                    _: None = Depends(verify_enrollment_token)):
    """
    Advance exactly once after a passing assignment; safe on repeated clicks.
    """
    conn = get_conn()
    try:
        conn.execute("BEGIN IMMEDIATE")  # Start transaction
        
        enrollment = conn.execute("SELECT * FROM enrollments WHERE id = ?", (enrollment_id,)).fetchone()
        if not enrollment:
            raise HTTPException(status_code=404, detail="Enrollment not found")
        
        lesson = conn.execute(
            """
            SELECT l.*, m.id AS milestone_id
            FROM lessons l
            JOIN lesson_milestones lm ON lm.lesson_id = l.id
            JOIN milestones m ON m.id = lm.milestone_id
            WHERE l.path_id = ? AND l.day_number = ?
            """,
            (enrollment["path_id"], enrollment["current_day"]),
        ).fetchone()
        
        if not lesson:
            raise HTTPException(status_code=409, detail="No next authored lesson is available yet.")
        
        # Check if homework passed
        passed = conn.execute(
            """SELECT 1 FROM homework_submissions 
               WHERE enrollment_id = ? AND lesson_id = ? AND passed = 1
               LIMIT 1""", 
            (enrollment_id, lesson["id"])
        ).fetchone()
        
        if not passed:
            raise HTTPException(
                status_code=409, 
                detail="Submit and pass today's coding practice before completing this milestone."
            )

        day = enrollment["current_day"]
        
        # Record attendance
        conn.execute(
            "INSERT OR IGNORE INTO attendance (enrollment_id, day, present) VALUES (?, ?, 1)",
            (enrollment_id, day)
        )
        
        # Record lesson progress
        conn.execute(
            """INSERT INTO lesson_progress (enrollment_id, lesson_id, status, submitted_at, passed)
               VALUES (?, ?, 'completed', datetime('now'), 1)
               ON CONFLICT(enrollment_id, lesson_id) DO UPDATE SET status = 'completed', passed = 1""",
            (enrollment_id, lesson["id"]),
        )
        
        # Record mastery
        conn.execute(
            """INSERT INTO mastery_records (enrollment_id, milestone_id, quiz_score, code_passed, status, mastered_at)
               VALUES (?, ?, 0, 1, 'ready_for_review', datetime('now'))
               ON CONFLICT(enrollment_id, milestone_id) DO UPDATE SET code_passed = 1, status = 'ready_for_review'""",
            (enrollment_id, lesson["milestone_id"]),
        )
        
        # Update enrollment: advance day, award XP, increment streak
        xp = enrollment["xp"] + 10
        streak = enrollment["streak"] + 1
        next_day = day + 1
        
        conn.execute(
            "UPDATE enrollments SET current_day = ?, xp = ?, streak = ? WHERE id = ?",
            (next_day, xp, streak, enrollment_id),
        )
        
        conn.commit()
        
        return {
            "current_day": next_day,
            "xp": xp,
            "streak": streak,
            "message": f"{lesson['milestone_id']} practice completed. +10 XP. Your explanation and spaced review remain part of full mastery.",
        }
    finally:
        conn.close()
```