"""Durable curriculum worker for PySchool.

Runs sequentially through catalog paths, asks the local DeepSeek bridge for one
strict JSON lesson at a time, validates the result, and commits it to SQLite.
It never overwrites the three existing launch curricula and never executes
student-submitted code.
"""
from __future__ import annotations

import ast
import json
import os
import re
import sqlite3
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path

from .db import DB_PATH
from .seed import _seed_automation_day_one, _seed_automation_day_two, seed

BRIDGE_URL = "http://127.0.0.1:8787/ask"
CHATGPT_URL = "http://127.0.0.1:8788/ask"
STATE_PATH = Path.home() / ".local/state/pyschool-curriculum-worker.json"
LOCK_PATH = Path.home() / ".local/state/pyschool-curriculum-worker.lock"
LAUNCH_PATHS = {"web-dev", "data-science", "agi-research"}
TOTAL_DAYS = 180
MIN_THEORY_WORDS = 450
MAX_THEORY_WORDS = 900


@dataclass(frozen=True)
class CatalogPath:
    slug: str
    name: str
    description: str
    libraries: str
    category: str


def load_state() -> dict:
    if STATE_PATH.exists():
        return json.loads(STATE_PATH.read_text())
    return {"status": "idle", "path_index": 0, "day": 3, "updated_at": None, "last_error": None}


def save_state(state: dict) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    state["updated_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    tmp = STATE_PATH.with_suffix(".tmp")
    tmp.write_text(json.dumps(state, indent=2) + "\n")
    tmp.replace(STATE_PATH)


def acquire_lock():
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    try:
        fd = os.open(LOCK_PATH, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        # Recover a lock left behind by a crashed/duplicate worker.
        try:
            owner = int(LOCK_PATH.read_text().strip())
            os.kill(owner, 0)
            return None
        except (ValueError, ProcessLookupError, PermissionError):
            try:
                LOCK_PATH.unlink()
            except FileNotFoundError:
                pass
            fd = os.open(LOCK_PATH, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    os.write(fd, str(os.getpid()).encode())
    os.close(fd)
    return LOCK_PATH


def release_lock(lock) -> None:
    if lock:
        try:
            lock.unlink()
        except FileNotFoundError:
            pass


def catalog(conn: sqlite3.Connection) -> list[CatalogPath]:
    rows = conn.execute(
        "SELECT p.slug, p.name, p.description, p.libraries, c.name AS category "
        "FROM paths p JOIN categories c ON c.id = p.category_id "
        "ORDER BY p.id"
    ).fetchall()
    return [CatalogPath(*row) for row in rows if row["slug"] not in LAUNCH_PATHS]


def next_target(conn: sqlite3.Connection, paths: list[CatalogPath]) -> tuple[CatalogPath, int] | None:
    for index, path in enumerate(paths):
        row = conn.execute(
            "SELECT COALESCE(MAX(day_number), 0) AS day FROM lessons WHERE path_id = "
            "(SELECT id FROM paths WHERE slug = ?)", (path.slug,)
        ).fetchone()
        day = int(row["day"]) + 1
        if day <= TOTAL_DAYS:
            return path, day
    return None


def ask_deepseek(path: CatalogPath, day: int, attempts: int = 4) -> str:
    """DeepSeek is the data scout: short, factual, no JSON lesson payload."""
    prompt = f"""For PySchool path '{path.name}' (slug {path.slug}), Day {day}/{TOTAL_DAYS}, gather a compact factual source brief. Context: {path.description}. Libraries: {path.libraries}. Return 400-700 words of professional English: prerequisites, key concepts, technical accuracy notes, realistic worked-example ideas, common mistakes, practice roles, and authoritative source suggestions. Do not write the lesson. Do not claim code was run."""
    last_error = None
    for attempt in range(1, attempts + 1):
        try:
            payload = json.dumps({"prompt": prompt, "timeout": 300}).encode()
            request = urllib.request.Request(BRIDGE_URL, data=payload, headers={"Content-Type": "application/json"}, method="POST")
            with urllib.request.urlopen(request, timeout=330) as response:
                envelope = json.load(response)
            if not envelope.get("ok"):
                raise RuntimeError(envelope.get("error", "DeepSeek bridge error"))
            return envelope["message"]["text"]
        except Exception as exc:
            last_error = exc
            if attempt < attempts:
                time.sleep(min(20, attempt * 5))
    raise RuntimeError(f"DeepSeek data scout failed: {last_error}")


def ask_chatgpt(path: CatalogPath, day: int, source_brief: str, attempts: int = 4) -> dict:
    prompt = f"""You are the senior curriculum author and technical reviewer for PySchool. Write ONE complete lesson for {path.name} (slug {path.slug}), Day {day}/{TOTAL_DAYS}. Path context: {path.description}. Libraries: {path.libraries}. Source brief: {source_brief}

Return EXACTLY these plain-text sections, in this order, with no JSON and no markdown fences around the whole answer:
TITLE: one specific lesson title
DOMAIN: short domain
OBJECTIVE: one measurable objective
THEORY: 450-650 words of professional English with a mental model, intuition, worked example, common mistakes, safety/quality notes, and practical application to {path.name}
CODE:
```python
valid Python 3 program; every block has an indented statement; balanced quotes/brackets; no pseudocode
```
QUESTIONS:
1. question one
2. question two
3. question three
ANSWERS:
1. answer one
2. answer two
3. answer three
HOMEWORK: a practical 45-60 minute task with explicit requirements and observable output
PATTERNS: one literal Python pattern per line

Rules: exactly 3 questions and 3 answers; theory must be 450-650 words; code must compile under Python 3; never truncate; no claims that code was executed."""
    last_error = None
    for attempt in range(1, attempts + 1):
        try:
            payload = json.dumps({"prompt": prompt, "timeout": 300}).encode()
            request = urllib.request.Request(CHATGPT_URL, data=payload, headers={"Content-Type": "application/json"}, method="POST")
            with urllib.request.urlopen(request, timeout=330) as response:
                envelope = json.load(response)
            if not envelope.get("ok"):
                raise RuntimeError(envelope.get("error", "ChatGPT bridge error"))
            raw = envelope["text"]
            def section(name: str, nxt: str) -> str:
                a = raw.find(name + ":")
                b = raw.find(nxt + ":", a + len(name) + 1)
                if a < 0 or b < 0: raise ValueError(f"missing section {name}")
                return raw[a + len(name) + 1:b].strip()
            code = section("CODE", "QUESTIONS").replace("```python", "").replace("```", "").strip()
            qs = [re.sub(r"^\s*\d+[.)]\s*", "", x).strip() for x in section("QUESTIONS", "ANSWERS").splitlines() if x.strip()][:3]
            ans = [re.sub(r"^\s*\d+[.)]\s*", "", x).strip() for x in section("ANSWERS", "HOMEWORK").splitlines() if x.strip()][:3]
            patterns = [x.strip("-* \t") for x in section("PATTERNS", "END").splitlines() if x.strip()] if "PATTERNS:" in raw else []
            if not patterns: patterns = [lesson_code_line for lesson_code_line in code.splitlines() if lesson_code_line.strip()][:1]
            obj = {"path": path.slug, "day": day, "title": section("TITLE", "DOMAIN"), "domain": section("DOMAIN", "OBJECTIVE"), "objective": section("OBJECTIVE", "THEORY"), "theory": section("THEORY", "CODE"), "code_example": code, "questions": qs, "answers": ans, "homework": section("HOMEWORK", "PATTERNS") if "PATTERNS:" in raw else section("HOMEWORK", "END"), "required_patterns": patterns}
            validate(obj)
            return obj
        except Exception as exc:
            last_error = exc
            if attempt < attempts: time.sleep(min(20, attempt * 5))
    raise RuntimeError(f"ChatGPT lesson author failed: {last_error}")


def validate(lesson: dict) -> None:
    required = {"path", "day", "title", "domain", "objective", "theory", "code_example", "questions", "answers", "homework", "required_patterns"}
    missing = required - lesson.keys()
    if missing:
        raise ValueError(f"missing fields: {sorted(missing)}")
    if not isinstance(lesson["questions"], list) or len(lesson["questions"]) != 3:
        raise ValueError("questions must contain exactly 3 items")
    if not isinstance(lesson["answers"], list) or len(lesson["answers"]) != 3:
        raise ValueError("answers must contain exactly 3 items")
    words = len(re.findall(r"\b[\w'-]+\b", lesson["theory"]))
    if not MIN_THEORY_WORDS <= words <= MAX_THEORY_WORDS:
        raise ValueError(f"theory has {words} words, expected {MIN_THEORY_WORDS}-{MAX_THEORY_WORDS}")
    ast.parse(lesson["code_example"])
    if len(lesson["homework"]) < 120:
        raise ValueError("homework is too short")
    if not isinstance(lesson["required_patterns"], list) or not all(isinstance(x, str) and x for x in lesson["required_patterns"]):
        raise ValueError("required_patterns must be non-empty strings")


def insert_lesson(conn: sqlite3.Connection, path: CatalogPath, lesson: dict) -> None:
    validate(lesson)
    row = conn.execute("SELECT id FROM paths WHERE slug = ?", (path.slug,)).fetchone()
    if row is None:
        raise ValueError(f"catalog path missing: {path.slug}")
    if conn.execute("SELECT id FROM lessons WHERE path_id = ? AND day_number = ?", (row["id"], lesson["day"])).fetchone():
        return
    day = lesson["day"]
    conn.execute(
        "INSERT INTO lessons (path_id, day_number, title, theory, code_example, questions, answers, homework) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (row["id"], day, lesson["title"], lesson["theory"], lesson["code_example"],
         json.dumps(lesson["questions"]), json.dumps(lesson["answers"]), lesson["homework"]),
    )
    lesson_id = conn.execute("SELECT last_insert_rowid() AS id").fetchone()["id"]
    conn.execute(
        "INSERT INTO milestones (path_id, code, title, domain, objective, estimated_minutes, sort_order, mastery_criteria, remediation_note) "
        "VALUES (?, ?, ?, ?, ?, 60, ?, ?, ?)",
        (row["id"], f"{path.slug.upper()}-{day:03d}", lesson["title"], lesson["domain"], lesson["objective"], day,
         "Pass the concept check, submit code matching the assignment patterns, and explain the solution.",
         "Re-read the example, test a small input, and revise after observing the output."),
    )
    milestone_id = conn.execute("SELECT last_insert_rowid() AS id").fetchone()["id"]
    conn.execute("INSERT INTO lesson_milestones (lesson_id, milestone_id) VALUES (?, ?)", (lesson_id, milestone_id))
    conn.execute(
        "INSERT INTO assignments (lesson_id, prompt, required_patterns, min_lines, rubric) VALUES (?, ?, ?, 3, ?)",
        (lesson_id, lesson["homework"], json.dumps(lesson["required_patterns"]),
         "Code must parse, include the required constructs, and produce the stated observable result."),
    )


def run() -> None:
    lock = acquire_lock()
    if lock is None:
        return
    state = load_state()
    try:
        seed()
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        try:
            paths = catalog(conn)
            while True:
                target = next_target(conn, paths)
                if target is None:
                    state.update(status="complete", last_error=None, updated_at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
                    save_state(state)
                    return
                path, day = target
                state.update(status="generating", path=path.slug, day=day, last_error=None)
                save_state(state)
                try:
                    lesson = ask_chatgpt(path, day, "No external source brief. Rely on your own curriculum expertise and state only evidence-bound content.")
                    insert_lesson(conn, path, lesson)
                    conn.commit()
                    state.update(status="idle", day=day + 1, last_verified_path=path.slug, last_verified_day=day, last_error=None)
                except Exception as exc:
                    conn.rollback()
                    state.update(status="error", path=path.slug, day=day, last_error=repr(exc))
                    save_state(state)
                    print(f"[worker] rejected {path.slug} day {day}: {exc}", flush=True)
                    time.sleep(min(120, 10 * day))
                    continue
                save_state(state)
        finally:
            conn.close()
    finally:
        release_lock(lock)


if __name__ == "__main__":
    run()
