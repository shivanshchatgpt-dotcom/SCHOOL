"""Index the local book corpus by printed page number.

pdftotext -layout emits one form feed (\\f) per page, so the page index of any
offset in the extracted text is the number of page breaks before it, plus one.
Printed page numbers differ from that index by a per-book offset (front matter),
so this module calibrates the offset against the chapter inventory, which was
built from the books' own tables of contents.

The result is a map from (book, printed_page) -> text offset, which lets a
canonical topic request "give me the source text for pages 197-224 of Learning
Python" and receive the passages its provenance cites.
"""
from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path

BOOKS_DIR = Path(__file__).resolve().parent / "txt"
INVENTORY_PATH = Path(__file__).resolve().parent / "inventory.json"

# Short filename per inventory key.
BOOK_FILES = {
    "learning-python": "Learning_Python.txt",
    "learning-python-networking": "Learning_Python_Networking_(en).txt",
    "python-data-science-handbook": "Python_Data_Science_Handbook_(en).txt",
    "python-programming": "Python_Programming.txt",
}

# Human-readable book titles, for provenance reporting.
BOOK_TITLES = {
    "learning-python": "Learning Python (Mark Lutz, 4th ed.)",
    "learning-python-networking": "Learning Python Networking (Fauno, Wade, et al., 2nd ed.)",
    "python-data-science-handbook": "Python Data Science Handbook (Jake VanderPlas, 2nd ed.)",
    "python-programming": "Python Programming (Hans-Petter Halvorsen, 2026)",
}


@lru_cache(maxsize=1)
def _inventory() -> dict:
    return json.loads(INVENTORY_PATH.read_text())


@lru_cache(maxsize=4)
def _text(book: str) -> str:
    return (BOOKS_DIR / BOOK_FILES[book]).read_text(errors="ignore")


def _page_offsets(book: str) -> list[int]:
    """Return the offset at which each pdftotext page begins (0-based page -> offset)."""
    return [m.start() for m in re.finditer(r"\f", _text(book))]


def _calibrate(book: str) -> int:
    """Offset between a printed page number and its pdftotext page index.

    Derived from the inventory: each chapter's body opens on its printed page,
    so comparing the two for every chapter yields the constant shift.
    """
    chapters = [
        c for c in _inventory()[book]["chapters"]
        if c.get("page") and c.get("title")
    ]
    if len(chapters) < 3:
        return 0
    offsets = _page_offsets(book)
    votes: dict[int, int] = {}
    for chapter in chapters:
        # Locate the chapter's body opening and take its page index.
        txt = _text(book)
        needle = chapter["title"].split(" ")[0].strip()
        idx = -1
        for m in re.finditer(r"\f[^\n]{0,120}", txt):
            if needle in m.group(0):
                # Prefer an opening whose page is near the printed expectation.
                page_index = offsets.index(m.start()) if m.start() in offsets else None
                if page_index is not None:
                    guess = chapter["page"] - page_index
                    votes[guess] = votes.get(guess, 0) + 1
                idx = m.start()
                break
        if idx < 0:
            continue
    if not votes:
        return 0
    return max(votes.items(), key=lambda kv: kv[1])[0]


@lru_cache(maxsize=4)
def _page_index_map(book: str) -> dict[int, int]:
    """Map printed page number -> text offset."""
    offsets = _page_offsets(book)
    shift = _calibrate(book)
    out: dict[int, int] = {}
    for i, off in enumerate(offsets):
        printed = i + shift
        if printed > 0:
            out.setdefault(printed, off)
    return out


def page_range(book: str, first: int, last: int) -> str:
    """Return the extracted source text for a printed page range, inclusive."""
    index = _page_index_map(book)
    if book not in BOOK_FILES:
        raise KeyError(f"unknown book: {book}")
    text = _text(book)
    offsets = _page_offsets(book)
    if not offsets:
        return ""
    # Fall back to raw page indices when calibration produced nothing usable.
    shift = _calibrate(book)
    def offset_of(printed: int) -> int | None:
        hit = index.get(printed)
        if hit is not None:
            return hit
        raw = printed - shift
        return offsets[raw] if 0 <= raw < len(offsets) else None

    start = offset_of(first)
    if start is None:
        start = offsets[0]
    end = offset_of(last + 1)
    if end is None:
        end = len(text)
    return text[start:end]


def chapter_range(book: str, chapter: int) -> tuple[int, int]:
    """Return (first_printed_page, last_printed_page) for a chapter."""
    chapters = _inventory()[book]["chapters"]
    match = next((c for c in chapters if c["chapter"] == chapter), None)
    if not match or not match.get("page"):
        raise KeyError(f"no page data for {book} chapter {chapter}")
    nxt = next((c for c in chapters if c["chapter"] == chapter + 1), None)
    last = (nxt["page"] - 1) if nxt and nxt.get("page") else match["page"] + 30
    return match["page"], last


def section_snippet(book: str, chapter: int, section_hint: str, max_chars: int = 1400) -> str:
    """Return a small snippet around a named section within a chapter.

    Used to confirm a cited section actually exists in the source. Never used to
    copy text into a lesson — only to verify provenance and to ground the
    canonical concept while it is being authored.
    """
    first, last = chapter_range(book, chapter)
    body = page_range(book, first, last)
    pos = body.find(section_hint)
    if pos < 0:
        # Try a case-insensitive lookup as a fallback.
        pos = body.lower().find(section_hint.lower())
    if pos < 0:
        return ""
    return body[pos : pos + max_chars]


def provenance_line(source: dict) -> str:
    """Render one source citation as a readable provenance string."""
    book = source["book"]
    title = BOOK_TITLES.get(book, book)
    ch = source.get("chapter")
    pages = source.get("pages")
    sections = source.get("sections") or []
    parts = [title]
    if ch:
        inv = _inventory().get(book, {})
        ch_meta = next((c for c in inv.get("chapters", []) if c["chapter"] == ch), None)
        ch_title = ch_meta.get("title") if ch_meta else None
        parts.append(f"ch {ch}" + (f", “{ch_title}”" if ch_title else ""))
    if pages:
        if pages[0] == pages[1]:
            parts.append(f"p. {pages[0]}")
        else:
            parts.append(f"pp. {pages[0]}–{pages[1]}")
    if sections:
        parts.append("§ " + "; ".join(sections))
    return " — ".join(parts)


if __name__ == "__main__":
    for book in BOOK_FILES:
        first, last = chapter_range(book, _inventory()[book]["chapters"][0]["chapter"])
        sample = page_range(book, first, first + 1)
        print(f"{book}: calibrated shift={_calibrate(book)}, "
              f"pages indexed={len(_page_index_map(book))}, "
              f"ch1={first}-{last}, sample={sample.strip()[:60]!r}")
