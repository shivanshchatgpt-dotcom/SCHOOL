"""Parse the table of contents of each source PDF into a chapter inventory."""
import json
import re
from pathlib import Path

TXT = Path("/mnt/storage/SCHOOL/.books/txt")


def parse_learning_python():
    """Learning Python, Lutz 4th ed. — TOC pages near the front of the file."""
    txt = (TXT / "Learning_Python.txt").read_text(errors="ignore")
    lines = txt.splitlines()
    # TOC occupies roughly lines 280-1100 in the extracted text.
    out, seen = [], set()
    for idx, ln in enumerate(lines[:1400]):
        m = re.match(r"^\s*(\d{1,2})\.\s+([A-Za-z].+?)\s*(?:\.\s*){2,}(\d{1,4})\s*$", ln)
        if not m:
            continue
        n = int(m.group(1))
        if n in seen or not (1 <= n <= 45):
            continue
        seen.add(n)
        out.append(
            {"chapter": n, "title": m.group(2).strip(), "page": int(m.group(3))}
        )
    return sorted(out, key=lambda r: r["chapter"])


def parse_lpn():
    """Learning Python Networking — TOC lists bare 'N. Title' lines, and the
    same line also opens the chapter body, so page numbers can be counted."""
    txt = (TXT / "Learning_Python_Networking_(en).txt").read_text(errors="ignore")
    # Body openings start a page as a bare title line after a form feed
    # ("\fNetwork Programming with Python"), without the chapter number.
    # The front TOC has the numbered form but no page break.
    titles = {}
    for m in re.finditer(r"^\s*(\d{1,2})\.\s+([A-Z][^\n]{5,70})$", txt, re.M):
        n, t = int(m.group(1)), m.group(2).strip()
        if t.startswith("Section "):
            continue
        nxt = txt[m.end() : m.end() + 80].splitlines()
        if nxt and re.match(r"^[A-Za-z][^\n]{5,70}$", nxt[0].strip()):
            t = f"{t} {nxt[0].strip()}"
        if n not in titles:
            titles[n] = t
    pages = {}
    for n, title in titles.items():
        # The body heading wraps across lines, so match its leading words.
        # Use as many words as fit on the first body line: single-word titles
        # are ambiguous and can match an earlier chapter's opening.
        words = title.split(" ")
        prefix = re.escape(" ".join(words[:3])) if len(words) > 2 else re.escape(words[0])
        for m in re.finditer(r"\f" + prefix + r"[^\n]{0,70}\n", txt):
            head = txt[m.start() : m.start() + 1200]
            if re.search(r"(Technical requirements|In this chapter|following topics will be covered)", head):
                pages[n] = txt.count("\f", 0, m.start()) + 1
                break
    return [
        {"chapter": n, "title": titles[n], "page": pages.get(n)}
        for n in sorted(titles)
    ]


def parse_pdsh():
    """Python Data Science Handbook, VanderPlas 2nd ed.

    Chapter openings read "Chapter N. Title" and the title often wraps onto
    the next line ("Chapter 4. Understanding Data\\nTypes in Python").
    """
    txt = (TXT / "Python_Data_Science_Handbook_(en).txt").read_text(errors="ignore")
    out, seen = [], set()
    # pdsh body text contains cross-references like "...in Chapter 9." which
    # would be false positives. Real chapter openings follow a page break,
    # which pdsh emits as a form feed (\f) at the top of the page.
    for m in re.finditer(r"\f\s*\n?Chapter (\d{1,2})\.\s*([^\n]{3,60})", txt):
        n = int(m.group(1))
        if n in seen:
            continue
        seen.add(n)
        title = m.group(2).strip()
        # Titles wrap onto the next line(s) when they overflow the page width.
        nxt = txt[m.end() : m.end() + 160].splitlines()
        # The first split element is the tail of the heading line; skip it.
        rest = nxt[1:] if nxt and nxt[0] == "" else nxt
        for line in rest:
            if re.match(r"^[A-Za-z ,&':’?-]{3,50}$", line.strip()):
                # A hyphenated word split across lines joins without a space.
                if title.endswith("-"):
                    title = f"{title}{line.strip()}"
                else:
                    title = f"{title} {line.strip()}"
            else:
                break
        # One form feed per printed page: this page's index is the number of
        # page breaks already passed, plus one.
        page = txt.count("\f", 0, m.start()) + 1
        out.append({"chapter": n, "title": title, "page": page})
    return sorted(out, key=lambda r: r["chapter"])


def parse_halvorsen():
    """Python Programming, Halvorsen — numbered sections 'N.M Title ... page'."""
    txt = (TXT / "Python_Programming.txt").read_text(errors="ignore")
    sections = []
    seen = set()
    for ln in txt.splitlines():
        m = re.match(r"^\s*(\d{1,2})\.(\d{1,2})\s+(.+?)\s*(?:\.\s*){2,}(\d{1,4})\s*$", ln)
        if not m:
            continue
        ch, sec = int(m.group(1)), int(m.group(2))
        title = m.group(3).strip()
        key = (ch, sec)
        if key in seen or len(title) < 3:
            continue
        seen.add(key)
        sections.append(
            {"chapter": ch, "section": sec, "title": title, "page": int(m.group(4))}
        )
    chapters = {}
    for s in sections:
        ch = s["chapter"]
        if ch not in chapters:
            chapters[ch] = {"chapter": ch, "title": None, "sections": []}
        chapters[ch]["sections"].append(s)
    return [
        {
            "chapter": ch,
            "title": None,
            "page": chapters[ch]["sections"][0]["page"] if chapters[ch]["sections"] else None,
            "sections": [x["title"] for x in chapters[ch]["sections"]],
        }
        for ch in sorted(chapters)
    ]


if __name__ == "__main__":
    inv = {
        "learning-python": {
            "title": "Learning Python",
            "author": "Mark Lutz",
            "edition": "4th",
            "pages": 1213,
            "chapters": parse_learning_python(),
        },
        "learning-python-networking": {
            "title": "Learning Python Networking",
            "author": "Fauno, Wade, et al.",
            "edition": "2nd",
            "pages": 697,
            "chapters": parse_lpn(),
        },
        "python-data-science-handbook": {
            "title": "Python Data Science Handbook",
            "author": "Jake VanderPlas",
            "edition": "2nd",
            "pages": 789,
            "chapters": parse_pdsh(),
        },
        "python-programming": {
            "title": "Python Programming",
            "author": "Hans-Petter Halvorsen",
            "edition": "2026",
            "pages": 143,
            "chapters": parse_halvorsen(),
        },
    }
    for key, book in inv.items():
        print(f"\n=== {book['title']} ({book['author']}, {book['edition']}) — {len(book['chapters'])} chapters ===")
        for c in book["chapters"]:
            label = f"{c['chapter']}."
            if c.get("sections"):
                print(f"  {label} {len(c['sections'])} sections, first: {c['sections'][0]}  (p{c['page']})")
            else:
                print(f"  {label} {c['title']}  (p{c['page']})")
    Path("/mnt/storage/SCHOOL/.books/inventory.json").write_text(json.dumps(inv, indent=1))
    total = sum(len(b["chapters"]) for b in inv.values())
    print(f"\nTOTAL: {total} chapters across {len(inv)} books")
