"""Audit the corpus for unexploited chapters and paths with no curriculum.

This is the scaling instrument. Adding a canonical topic to
``canonical_topics.py`` is the only action needed to populate more paths —
composer, validator and seeder already exist — so the question that matters is
*what to author next*, and this answers it from the inventory and the database:

1. which catalog paths still have zero lessons,
2. which book chapters are cited by no canonical topic yet,
3. which paths the corpus can serve and which it cannot (coverage: insufficient).

Run it:  .venv/bin/python -m books_gap_audit   (or .books/gap_audit.py)
"""
from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from canonical_topics import all_topics  # noqa: E402
from source_index import BOOK_TITLES, _inventory  # noqa: E402

DB_PATH = Path(__file__).resolve().parent.parent / "backend" / "pyschool.db"


def paths_without_lessons(db: sqlite3.Connection) -> list[tuple[int, str, str]]:
    rows = db.execute(
        """
        SELECT p.id, p.slug, p.name
        FROM paths p
        LEFT JOIN lessons l ON l.path_id = p.id
        WHERE l.id IS NULL
        ORDER BY p.id
        """
    ).fetchall()
    return [(r[0], r[1], r[2]) for r in rows]


def cited_chapters() -> set[tuple[str, int]]:
    out: set[tuple[str, int]] = set()
    for record in all_topics().values():
        for src in record["sources"]:
            if src.get("chapter"):
                out.add((src["book"], src["chapter"]))
    return out


def uncited_chapters() -> list[tuple[str, int, str, int | None]]:
    cited = cited_chapters()
    out = []
    for book, meta in _inventory().items():
        for ch in meta["chapters"]:
            if (book, ch["chapter"]) not in cited:
                out.append((book, ch["chapter"], ch.get("title") or "(sections only)", ch.get("page")))
    return out


def adapted_paths() -> set[str]:
    return {slug for record in all_topics().values() for slug in record["adapters"]}


def main() -> None:
    db = sqlite3.connect(DB_PATH)
    try:
        empty = paths_without_lessons(db)
    finally:
        db.close()

    print(f"=== Paths with zero lessons: {len(empty)} of 100 ===")
    print("  " + ", ".join(slug for _, slug, _ in empty))

    adapted = adapted_paths()
    print(f"\n=== Paths the canonical library already serves: {len(adapted)} ===")
    print("  " + ", ".join(sorted(adapted)))

    uncited = uncited_chapters()
    by_book: dict[str, int] = {}
    for book, _, _, _ in uncited:
        by_book[book] = by_book.get(book, 0) + 1
    print("\n=== Corpus chapters not yet cited by any canonical topic ===")
    for book in sorted(by_book):
        total = len(_inventory()[book]["chapters"])
        print(f"  {BOOK_TITLES[book]}: {by_book[book]} of {total} chapters unused")

    print("\n=== Coverage declarations on authored topics ===")
    for tid, record in sorted(all_topics().items()):
        adapters = ", ".join(sorted(record["adapters"]))
        print(f"  {record['coverage']:11s} {tid}  -> {adapters}")

    print("\n=== Next step ===")
    print("  Author one canonical topic citing an unused chapter above, give it an")
    print("  adapter for at least one zero-lesson path, then re-run seed(). The")
    print("  composer validates it and the seeder fills only empty (path, day) slots.")


if __name__ == "__main__":
    main()
