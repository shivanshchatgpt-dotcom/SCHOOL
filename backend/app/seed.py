"""Seed the PySchool database from seed_data (idempotent)."""
import importlib
import json
import os

from .db import get_conn
from .curriculum_automation import AUTOMATION_DAY_1
from .curriculum_automation_day2 import AUTOMATION_DAY_2
from .curriculum_automation_day3 import AUTOMATION_DAY_3
from .curriculum_automation_day4 import AUTOMATION_DAY_4
from .curriculum_web_dev import WEB_DEV_DAY_1
from .seed_data import (
    CATEGORIES,
    CURRICULA,
    extended_curriculum,
    LAUNCH_PATH_SLUGS,
    PATHS,
    PATH_FLAGSHIP_QUESTIONS,
    PROFILE_QUESTIONS,
)

SEED_VERSION = 10  # v10: per-path placement questions + profiling step


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
            _seed_automation_day_one(conn)
            _seed_automation_day_two(conn)
            _seed_automation_day_three(conn)
            _seed_automation_day_four(conn)
            canonical_added = _seed_canonical_lessons(conn)
            catalog_added = _seed_catalog_curricula(conn)
            question_added = _seed_assessment_questions(conn)
            _seed_profile_questions(conn)
            _refresh_catalog_content(conn)
            conn.commit()  # appliers read through their own connection
            authored = _apply_authored_curricula(conn)
            conn.execute(
                "UPDATE paths SET duration_days = 180, is_launch_ready = 1 WHERE slug IN ('agi-research', 'data-science', 'web-dev')"
            )
            conn.execute(
                "INSERT OR REPLACE INTO meta (key, value) VALUES ('seed_version', ?)",
                (str(SEED_VERSION),),
            )
            conn.commit()
            print(f"[seed] curriculum checked — {added} 180-day lessons added, "
                  f"{canonical_added} canonical lessons added, {catalog_added} catalog lessons added, "
                  f"{question_added} questions added, {authored} authored lessons applied")
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
                if slug == "web-dev" and day_num == 1:
                    authored = WEB_DEV_DAY_1
                    title, domain, objective = authored["title"], authored["domain"], authored["objective"]
                    code, homework, required_patterns, theory = authored["code_example"], authored["homework"], authored["required_patterns"], authored["theory"]
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
                        json.dumps(WEB_DEV_DAY_1["questions"] if slug == "web-dev" and day_num == 1 else ["What does this lesson help you do?", "Which line in the example would you change to test your understanding?"]),
                        json.dumps(WEB_DEV_DAY_1["answers"] if slug == "web-dev" and day_num == 1 else [objective, "Any one line, with a reason for the change."]),
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
        _seed_automation_day_one(conn)
        _seed_automation_day_two(conn)
        _seed_automation_day_three(conn)
        _seed_automation_day_four(conn)
        canonical_added = _seed_canonical_lessons(conn)
        _seed_catalog_curricula(conn)

        # Per-path placement questions + self-report profiling options.
        _seed_assessment_questions(conn)
        _seed_profile_questions(conn)
        conn.execute("INSERT OR REPLACE INTO meta (key, value) VALUES ('catalog_depth', '3')")
        conn.commit()  # appliers read through their own connection
        authored = _apply_authored_curricula(conn)

        conn.execute(
            "INSERT OR REPLACE INTO meta (key, value) VALUES ('seed_version', ?)",
            (str(SEED_VERSION),),
        )
        conn.commit()
        print(f"[seed] OK — {len(CATEGORIES)} categories, {len(PATHS)} paths, "
              f"{conn.execute('SELECT COUNT(*) AS c FROM lessons').fetchone()['c']} lessons seeded, "
              f"{canonical_added} canonical lessons added, {authored} authored lessons applied.")
    finally:
        conn.close()


def _seed_automation_day_one(conn) -> int:
    """Seed the first authored Automation day without changing launch tracks."""
    path = conn.execute("SELECT id FROM paths WHERE slug = 'automation'").fetchone()
    if not path:
        return 0
    if conn.execute(
        "SELECT id FROM lessons WHERE path_id = ? AND day_number = 1", (path["id"],)
    ).fetchone():
        return 0
    lesson = conn.execute(
        "INSERT INTO lessons (path_id, day_number, title, theory, code_example, questions, answers, homework) "
        "VALUES (?, 1, ?, ?, ?, ?, ?, ?)",
        (
            path["id"],
            AUTOMATION_DAY_1["title"],
            f"**Learning objective**\\n{AUTOMATION_DAY_1['objective']}\\n\\n**Why it matters for {AUTOMATION_DAY_1['domain']}**\\n{AUTOMATION_DAY_1['theory']}\\n\\n**Practice before submitting**\\nRun the example on a small sample file, change one value, and predict the output before you execute it.",
            AUTOMATION_DAY_1["code_example"],
            json.dumps(AUTOMATION_DAY_1["questions"]),
            json.dumps(AUTOMATION_DAY_1["answers"]),
            AUTOMATION_DAY_1["homework"],
        ),
    )
    milestone = conn.execute(
        "INSERT INTO milestones (path_id, code, title, domain, objective, estimated_minutes, sort_order, mastery_criteria, remediation_note) "
        "VALUES (?, 'AUTOMATION-001', ?, ?, ?, 60, 1, ?, ?)",
        (
            path["id"], AUTOMATION_DAY_1["title"], AUTOMATION_DAY_1["domain"], AUTOMATION_DAY_1["objective"],
            "Pass the concept check, submit safe code that reads an input and writes a separate output, and explain the input-output boundary.",
            "Test with a three-line sample, preserve the input file, and revise the script after inspecting the generated report.",
        ),
    )
    conn.execute("INSERT INTO lesson_milestones (lesson_id, milestone_id) VALUES (?, ?)", (lesson.lastrowid, milestone.lastrowid))
    conn.execute(
        "INSERT INTO assignments (lesson_id, prompt, required_patterns, min_lines, rubric) VALUES (?, ?, ?, 3, ?)",
        (
            lesson.lastrowid,
            AUTOMATION_DAY_1["homework"],
            json.dumps(AUTOMATION_DAY_1["required_patterns"]),
            "Code must parse, preserve the input file, read and write files, include the required Python constructs, and produce an observable report.",
        ),
    )
    return 1


def _seed_automation_day_two(conn) -> int:
    """Seed the second authored Automation day without changing launch tracks."""
    path = conn.execute("SELECT id FROM paths WHERE slug = 'automation'").fetchone()
    if not path or conn.execute(
        "SELECT id FROM lessons WHERE path_id = ? AND day_number = 2", (path["id"],)
    ).fetchone():
        return 0
    lesson = conn.execute(
        "INSERT INTO lessons (path_id, day_number, title, theory, code_example, questions, answers, homework) "
        "VALUES (?, 2, ?, ?, ?, ?, ?, ?)",
        (
            path["id"], AUTOMATION_DAY_2["title"],
            f"**Learning objective**\\n{AUTOMATION_DAY_2['objective']}\\n\\n**Why it matters for {AUTOMATION_DAY_2['domain']}**\\n{AUTOMATION_DAY_2['theory']}\\n\\n**Practice before submitting**\\nRun the example on a small sample file, change one value, and predict the output before you execute it.",
            AUTOMATION_DAY_2["code_example"], json.dumps(AUTOMATION_DAY_2["questions"]),
            json.dumps(AUTOMATION_DAY_2["answers"]), AUTOMATION_DAY_2["homework"],
        ),
    )
    milestone = conn.execute(
        "INSERT INTO milestones (path_id, code, title, domain, objective, estimated_minutes, sort_order, mastery_criteria, remediation_note) "
        "VALUES (?, 'AUTOMATION-002', ?, ?, ?, 60, 2, ?, ?)",
        (
            path["id"], AUTOMATION_DAY_2["title"], AUTOMATION_DAY_2["domain"], AUTOMATION_DAY_2["objective"],
            "Pass the concept check, submit code that stores validated records and computes summary totals, and explain the input-output boundary.",
            "Test with a small sample, preserve the input file, and revise the script after inspecting the generated summary.",
        ),
    )
    conn.execute("INSERT INTO lesson_milestones (lesson_id, milestone_id) VALUES (?, ?)", (lesson.lastrowid, milestone.lastrowid))
    conn.execute(
        "INSERT INTO assignments (lesson_id, prompt, required_patterns, min_lines, rubric) VALUES (?, ?, ?, 3, ?)",
        (
            lesson.lastrowid, AUTOMATION_DAY_2["homework"], json.dumps(AUTOMATION_DAY_2["required_patterns"]),
            "Code must parse, preserve the input file, store validated records, compute totals, include required constructs, and produce an observable report.",
        ),
    )
    return 1


def _seed_automation_day_three(conn) -> int:
    """Seed the locally authored third Automation day."""
    path = conn.execute("SELECT id FROM paths WHERE slug = 'automation'").fetchone()
    if not path or conn.execute(
        "SELECT id FROM lessons WHERE path_id = ? AND day_number = 3", (path["id"],)
    ).fetchone():
        return 0
    lesson = conn.execute(
        "INSERT INTO lessons (path_id, day_number, title, theory, code_example, questions, answers, homework) "
        "VALUES (?, 3, ?, ?, ?, ?, ?, ?)",
        (
            path["id"],
            AUTOMATION_DAY_3["title"],
            f"**Learning objective**\\n{AUTOMATION_DAY_3['objective']}\\n\\n**Core theory**\\n{AUTOMATION_DAY_3['theory']}\\n\\n**Practice**\\nRun the example, then write and test one function contract.",
            AUTOMATION_DAY_3["code_example"],
            json.dumps(AUTOMATION_DAY_3["questions"]),
            json.dumps(AUTOMATION_DAY_3["answers"]),
            AUTOMATION_DAY_3["homework"],
        ),
    )
    milestone = conn.execute(
        "INSERT INTO milestones (path_id, code, title, domain, objective, estimated_minutes, sort_order, mastery_criteria, remediation_note) "
        "VALUES (?, 'AUTOMATION-003', ?, ?, ?, 60, 3, ?, ?)",
        (
            path["id"], AUTOMATION_DAY_3["title"], AUTOMATION_DAY_3["domain"], AUTOMATION_DAY_3["objective"],
            "Submit small functions with explicit inputs and returns, test invalid records, and explain each function contract.",
            "Revise the refactor after a failing edge-case test and keep the batch behavior unchanged.",
        ),
    )
    conn.execute("INSERT INTO lesson_milestones (lesson_id, milestone_id) VALUES (?, ?)", (lesson.lastrowid, milestone.lastrowid))
    conn.execute(
        "INSERT INTO assignments (lesson_id, prompt, required_patterns, min_lines, rubric) VALUES (?, ?, ?, 3, ?)",
        (lesson.lastrowid, AUTOMATION_DAY_3["homework"], json.dumps(AUTOMATION_DAY_3["required_patterns"]),
         "Code must define focused functions, return values, handle invalid records, include required constructs, and produce observable output."),
    )
    return 1


def _seed_automation_day_four(conn) -> int:
    """Seed the locally authored fourth Automation day."""
    path = conn.execute("SELECT id FROM paths WHERE slug = 'automation'").fetchone()
    if not path or conn.execute("SELECT id FROM lessons WHERE path_id = ? AND day_number = 4", (path["id"],)).fetchone():
        return 0
    lesson = conn.execute(
        "INSERT INTO lessons (path_id, day_number, title, theory, code_example, questions, answers, homework) VALUES (?, 4, ?, ?, ?, ?, ?, ?)",
        (path["id"], AUTOMATION_DAY_4["title"], f"**Learning objective**\\n{AUTOMATION_DAY_4['objective']}\\n\\n**Core theory**\\n{AUTOMATION_DAY_4['theory']}", AUTOMATION_DAY_4["code_example"], json.dumps(AUTOMATION_DAY_4["questions"]), json.dumps(AUTOMATION_DAY_4["answers"]), AUTOMATION_DAY_4["homework"]),
    )
    milestone = conn.execute(
        "INSERT INTO milestones (path_id, code, title, domain, objective, estimated_minutes, sort_order, mastery_criteria, remediation_note) VALUES (?, 'AUTOMATION-004', ?, ?, ?, 60, 4, ?, ?)",
        (path["id"], AUTOMATION_DAY_4["title"], AUTOMATION_DAY_4["domain"], AUTOMATION_DAY_4["objective"], "Handle expected failures, preserve valid batch work, and produce an observable recovery summary.", "Test missing, malformed, and interrupted-output scenarios."),
    )
    conn.execute("INSERT INTO lesson_milestones (lesson_id, milestone_id) VALUES (?, ?)", (lesson.lastrowid, milestone.lastrowid))
    conn.execute("INSERT INTO assignments (lesson_id, prompt, required_patterns, min_lines, rubric) VALUES (?, ?, ?, 3, ?)", (lesson.lastrowid, AUTOMATION_DAY_4["homework"], json.dumps(AUTOMATION_DAY_4["required_patterns"]), "Code must handle expected errors, use safe output replacement, and report accepted and rejected records."))
    return 1


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


def _seed_canonical_lessons(conn) -> int:
    """Fill empty (path, day) slots with book-grounded canonical lessons.

    Non-destructive: a slot that already holds a lesson is never touched, so
    every authored curriculum stays authoritative. Each canonical topic carries
    its own provenance, which is embedded in the lesson theory.
    """
    from .canonical_topics_proxy import composed_lessons

    added = 0
    for lesson in composed_lessons():
        path = conn.execute("SELECT id FROM paths WHERE slug = ?", (lesson["path"],)).fetchone()
        if not path:
            continue
        path_id = path["id"]
        day_num = lesson["day"]
        if conn.execute(
            "SELECT id FROM lessons WHERE path_id = ? AND day_number = ?", (path_id, day_num)
        ).fetchone():
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
                path_id, f"{lesson['path'].upper()}-{day_num:03d}", lesson["title"],
                lesson["domain"], lesson["objective"], day_num,
                "Pass the concept check, submit code that meets the assignment rubric, and be able to explain the worked example.",
                "Re-read the worked example, change one value, predict the output, and submit again with a short explanation.",
            ),
        )
        milestone_id = milestone.lastrowid
        if previous:
            conn.execute(
                "INSERT OR IGNORE INTO milestone_prerequisites (milestone_id, prerequisite_milestone_id) VALUES (?, ?)",
                (milestone_id, previous["id"]),
            )
        row = conn.execute(
            "INSERT INTO lessons (path_id, day_number, title, theory, code_example, questions, answers, homework) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                path_id, day_num, lesson["title"], lesson["theory"], lesson["code_example"],
                json.dumps(lesson["questions"]), json.dumps(lesson["answers"]), lesson["homework"],
            ),
        )
        lesson_id = row.lastrowid
        conn.execute("INSERT INTO lesson_milestones (lesson_id, milestone_id) VALUES (?, ?)", (lesson_id, milestone_id))
        conn.execute(
            "INSERT INTO assignments (lesson_id, prompt, required_patterns, min_lines, rubric) VALUES (?, ?, ?, ?, ?)",
            (
                lesson_id, lesson["homework"], json.dumps(lesson["required_patterns"]), 3,
                "Code must parse, include the required Python constructs, and include at least three non-empty lines.",
            ),
        )
        added += 1
    return added


def _seed_catalog_curricula(conn, only_slugs: list[str] | None = None) -> int:
    """Fill Days 1-180 for every non-launch path. Never touches existing lessons.

    Launch tracks keep their authored curricula; every other path gets the
    deterministic catalog curriculum. Paths that reach 180 lessons become
    enrollable. Skipped entirely when PYSCHOOL_SKIP_CATALOG is set (test speed).
    """
    if os.environ.get("PYSCHOOL_SKIP_CATALOG"):
        return 0
    from .curriculum_catalog import catalog_day

    added = 0
    paths = conn.execute("SELECT id, name, description, libraries, slug FROM paths").fetchall()
    for path in paths:
        slug = path["slug"]
        if slug in LAUNCH_PATH_SLUGS:
            continue
        if only_slugs is not None and slug not in only_slugs:
            continue
        path_id = path["id"]
        existing = {
            row[0] for row in conn.execute(
                "SELECT day_number FROM lessons WHERE path_id = ?", (path_id,)
            ).fetchall()
        }
        if len(existing) >= 180:
            continue
        for day_num in range(1, 181):
            if day_num in existing:
                continue
            title, domain, objective, code, homework, required_patterns, theory, questions, answers = catalog_day(
                slug, path["name"], path["description"], path["libraries"], day_num
            )
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
                    "Pass the concept check, submit code that meets the assignment rubric, and be able to explain the worked example.",
                    "Re-read the worked example, change one value, predict the output, and submit again with a short explanation.",
                ),
            )
            milestone_id = milestone.lastrowid
            if previous:
                conn.execute(
                    "INSERT OR IGNORE INTO milestone_prerequisites (milestone_id, prerequisite_milestone_id) VALUES (?, ?)",
                    (milestone_id, previous["id"]),
                )
            lesson = conn.execute(
                "INSERT INTO lessons (path_id, day_number, title, theory, code_example, questions, answers, homework) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    path_id, day_num, title, theory, code,
                    json.dumps(questions), json.dumps(answers), homework,
                ),
            )
            lesson_id = lesson.lastrowid
            conn.execute("INSERT INTO lesson_milestones (lesson_id, milestone_id) VALUES (?, ?)", (lesson_id, milestone_id))
            conn.execute(
                "INSERT INTO assignments (lesson_id, prompt, required_patterns, min_lines, rubric) VALUES (?, ?, ?, ?, ?)",
                (
                    lesson_id, homework, json.dumps(required_patterns), 3,
                    "Code must parse, include the required Python constructs, and include at least three non-empty lines.",
                ),
            )
            added += 1
    conn.execute(
        "UPDATE paths SET duration_days = 180, is_launch_ready = 1 WHERE id IN "
        "(SELECT path_id FROM lessons GROUP BY path_id HAVING COUNT(*) >= 180)"
    )
    return added


def _seed_assessment_questions(conn) -> int:
    """Rebuild every path's placement bank from its own name/description/libs.

    Each path gets 13 questions generated for it (a smaller bank plus the
    hand-authored flagship questions where they exist). Guarded by the
    ``assessment_v2`` meta key so re-seeding an existing database is a no-op.
    """
    try:
        row = conn.execute("SELECT value FROM meta WHERE key = 'assessment_v2'").fetchone()
        if row and row["value"] == "4":
            return 0
    except Exception:
        pass
    from .curriculum_catalog import PLACEMENT_TOPICS, path_placement_questions

    paths = conn.execute(
        "SELECT id, slug, name, description, libraries FROM paths ORDER BY id"
    ).fetchall()
    meta = [(p["name"], p["description"], p["libraries"]) for p in paths]
    added = 0
    for idx, path in enumerate(paths):
        conn.execute("DELETE FROM assessment_questions WHERE path_id = ?", (path["id"],))
        authored = PATH_FLAGSHIP_QUESTIONS.get(path["slug"], [])
        generated = [
            (q, PLACEMENT_TOPICS[i % len(PLACEMENT_TOPICS)])
            for i, q in enumerate(path_placement_questions(meta, idx))
        ]
        if authored:
            # Keep the hardest generated questions so adding authored items does
            # not just lop off the top end of the difficulty range.
            generated = sorted(generated, key=lambda qt: qt[0][6])[len(authored):]
        for (q_text, a, b, c, d, correct, diff), topic in [(q, "track-basics") for q in authored] + generated:
            conn.execute(
                "INSERT INTO assessment_questions (path_id, question, option_a, option_b, option_c, option_d, correct, difficulty, topic) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (path["id"], q_text, a, b, c, d, correct, diff, topic),
            )
            added += 1
    conn.execute("INSERT OR REPLACE INTO meta (key, value) VALUES ('assessment_v2', '4')")
    return added


def _seed_profile_questions(conn) -> int:
    """Insert the self-report profiling questions once (never overwrite edits)."""
    added = 0
    for key, question, options, order in PROFILE_QUESTIONS:
        cur = conn.execute(
            "INSERT OR IGNORE INTO profile_questions (key, question, options, sort_order) VALUES (?, ?, ?, ?)",
            (key, question, json.dumps(options), order),
        )
        added += cur.rowcount
    return added


# Self-reported experience -> the difficulty band the level test draws from.
_PROFILE_DIFFICULTY_BANDS = {
    "beginner": (1, 2),
    "intermediate": (2, 3),
    "advanced": (3, 4),
}


def select_questions_for_profile(rows, profile: dict | None = None, limit: int = 10):
    """Pick up to ``limit`` questions tuned to the learner's reported level.

    Without a recognised ``experience`` value every question is returned, so
    the plain endpoint keeps its old contract.
    """
    experience = profile.get("experience") if isinstance(profile, dict) else None
    band = _PROFILE_DIFFICULTY_BANDS.get(str(experience).lower()) if experience else None
    items = [dict(r) for r in rows]
    if not band:
        return items
    lo, hi = band

    def rank(q):
        d = q["difficulty"]
        if lo <= d <= hi:
            return (0, d)
        return (1, min(abs(d - lo), abs(d - hi)), d)

    items.sort(key=rank)
    return items[:limit]


def _refresh_catalog_content(conn) -> int:
    """Rewrite existing catalog-generated lessons with the current generator.

    Seed v9 filled the 97 catalog paths with shallow template days; the
    deepened generator replaces that prose in place. Only rows the catalog
    filler owns are touched: non-launch paths, excluding canonical slots and
    the hand-authored automation days (milestone codes AUTOMATION-*). Launch
    tracks are never touched. Runs once per database (meta guard).
    """
    if os.environ.get("PYSCHOOL_SKIP_CATALOG"):
        return 0
    try:
        row = conn.execute("SELECT value FROM meta WHERE key = 'catalog_depth'").fetchone()
        if row and int(row["value"]) >= 3:
            return 0
    except Exception:
        pass
    updated = _refresh_catalog_rows(conn, only_slugs=None)
    conn.execute("INSERT OR REPLACE INTO meta (key, value) VALUES ('catalog_depth', '3')")
    return updated


# Hand-authored tracks shipped as a module + idempotent applier. They are
# applied once per database, after the catalog fill, so a fresh install serves
# the authored lessons instead of the generated placeholders.
AUTHORED_APPLY_VERSION = "2"
AUTHORED_PACKS = (
    ("machine-learning", "app.apply_ml"),
    ("cryptography", "app.apply_cybersecurity"),
    ("testing-qa", "app.apply_catalog_batch_a"),
    ("database-ops", "app.apply_catalog_batch_b"),
    ("web-scraping", "app.apply_web_scraping"),
    ("api-building", "app.apply_api_building"),
    ("game-dev", "app.apply_game_dev"),
)


def _apply_authored_curricula(conn) -> int:
    """Apply the hand-authored tracks once, after the catalog fill.

    Each applier rewrites only its own days and never creates rows, so a path
    the catalog did not fill is skipped rather than half-built. Guarded by a
    meta key so the ~600 worked examples are not re-executed on every boot.
    """
    if os.environ.get("PYSCHOOL_SKIP_CATALOG"):
        return 0
    row = conn.execute("SELECT value FROM meta WHERE key = 'authored_apply'").fetchone()
    if row and row["value"] == AUTHORED_APPLY_VERSION:
        return 0
    from . import db as db_module

    applied = 0
    for slug, module_name in AUTHORED_PACKS:
        exists = conn.execute(
            "SELECT 1 FROM lessons WHERE path_id = (SELECT id FROM paths WHERE slug = ?) LIMIT 1",
            (slug,),
        ).fetchone()
        if not exists:
            continue
        try:
            module = importlib.import_module(module_name)
            applied += module.apply(db_module.DB_PATH, check_only=False).get("updated", 0)
        except Exception as error:  # a broken pack must not block startup
            print(f"[seed] authored pack for {slug} skipped: {error}")
    conn.execute(
        "INSERT OR REPLACE INTO meta (key, value) VALUES ('authored_apply', ?)",
        (AUTHORED_APPLY_VERSION,),
    )
    return applied


# The four genuinely hand-authored automation lessons. Everything else on the
# automation path is catalog-generated and refreshable.
AUTOMATION_PROTECTED = frozenset({"AUTOMATION-001", "AUTOMATION-002", "AUTOMATION-003", "AUTOMATION-004"})


def _refresh_catalog_rows(conn, only_slugs: list[str] | None = None) -> int:
    """Rewrite catalog-owned lessons with the current generator, if different.

    Owned = non-launch paths, excluding canonical slots and AUTOMATION-001…004.
    Compares before writing, so re-runs are no-ops. Returns rows changed.
    """
    try:
        from .canonical_topics_proxy import composed_lessons
        canonical = {(lesson["path"], lesson["day"]) for lesson in composed_lessons()}
    except Exception:
        return 0  # ponytail: no corpus, no way to tell owned rows — touch nothing
    from .curriculum_catalog import catalog_day

    updated = 0
    paths = conn.execute("SELECT id, name, description, libraries, slug FROM paths").fetchall()
    for path in paths:
        slug = path["slug"]
        if slug in LAUNCH_PATH_SLUGS:
            continue
        if only_slugs is not None and slug not in only_slugs:
            continue
        rows = conn.execute(
            """SELECT l.id, l.day_number, l.title, l.theory, l.code_example, l.questions, l.answers,
                      l.homework, m.code AS mcode, a.prompt AS aprompt, a.required_patterns AS apat
               FROM lessons l
               JOIN lesson_milestones lm ON lm.lesson_id = l.id
               JOIN milestones m ON m.id = lm.milestone_id
               LEFT JOIN assignments a ON a.lesson_id = l.id
               WHERE l.path_id = ?""",
            (path["id"],),
        ).fetchall()
        for row in rows:
            day_num = row["day_number"]
            if (slug, day_num) in canonical:
                continue
            if (row["mcode"] or "") in AUTOMATION_PROTECTED:
                continue
            title, domain, objective, code, homework, required_patterns, theory, questions, answers = catalog_day(
                slug, path["name"], path["description"], path["libraries"], day_num
            )
            new_q, new_a, new_p = json.dumps(questions), json.dumps(answers), json.dumps(required_patterns)
            if (row["title"], row["theory"], row["code_example"], row["questions"], row["answers"],
                    row["homework"], row["aprompt"], row["apat"]) == (title, theory, code, new_q, new_a, homework, homework, new_p):
                continue
            conn.execute(
                "UPDATE lessons SET title = ?, theory = ?, code_example = ?, questions = ?, answers = ?, homework = ? WHERE id = ?",
                (title, theory, code, new_q, new_a, homework, row["id"]),
            )
            conn.execute(
                "UPDATE assignments SET prompt = ?, required_patterns = ? WHERE lesson_id = ?",
                (homework, new_p, row["id"]),
            )
            updated += 1
    return updated


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
