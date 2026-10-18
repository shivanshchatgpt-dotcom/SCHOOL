"""Grep the full book corpus for every slot the audit marked `rewrite_new`.

The audit's canonical-topic matching only knows about the 24 authored topics. The
corpus is much larger: four books held as plain text plus 120 catalogued
chapters. A day can be flagged as a corpus gap against the topic library while
the underlying book still covers it, so this module re-checks every such slot
against the actual text and records where the support lives.

Attribution works by building a chapter-offset index for each book first, so a
hit is reported as a book plus a catalogued chapter and page rather than as a
bare line number. Results carry the terms that matched and a short context
snippet, because a term hit is evidence to review, not proof of coverage: a
book that mentions "attention" once is not teaching self-attention.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

BOOKS_DIR = Path(__file__).resolve().parents[2] / ".books"
INVENTORY = BOOKS_DIR / "inventory.json"

TEXT_FILES = {
    "learning-python": "Learning_Python.txt",
    "learning-python-networking": "Learning_Python_Networking_(en).txt",
    "python-data-science-handbook": "Python_Data_Science_Handbook_(en).txt",
    "python-programming": "Python_Programming.txt",
}

# Words that carry no signal about whether a book covers a domain topic. Left in
# place they would let "data" match every data-science heading.
STOP = {
    "the", "a", "an", "and", "or", "of", "to", "in", "for", "with", "by", "at",
    "on", "from", "into", "is", "are", "be", "its", "it", "as", "vs", "how",
    "what", "why", "using", "use", "used", "your", "you", "we", "their", "our",
    "part", "one", "two", "three", "first", "second", "next", "then", "than",
    "that", "this", "these", "those", "can", "will", "not", "but", "all", "any",
    "new", "own", "get", "set", "add", "run", "make", "work", "using",
}

# Domain terms that must be searched with a hyphen-insensitive pattern, because
# books write them several ways.
SEPARATORS = re.compile(r"[\s\-_/]+")


def load_texts() -> dict[str, str]:
    out = {}
    for book, fname in TEXT_FILES.items():
        p = BOOKS_DIR / "txt" / fname
        out[book] = p.read_text(errors="replace")
    return out


# Chapter anchors, in descending order of trust. The extracted texts are not
# uniform, so a single pattern does not fit all four books:
#
#   PAGE_FOOTER  "144 | Chapter 6: The Dynamic Typing Interlude" carries both a
#                page and a chapter, and repeats on every page of that chapter.
#                Only the Learning Python extraction kept running footers.
#   CHAPTER_HEAD "Chapter 2. Enhanced Interactive Features" at the start of a
#                line. The Data Science Handbook and Python Programming extractions
#                use this, though the Handbook wraps its titles across lines.
#   TITLE_BODY   the chapter title on its own line. Works as a fallback but is
#                weak: in some extractions the title only ever appears in the
#                front matter, which is what made earlier refs unreliable.
#
# Numbered section headings ("3.1 Something") were tried first and do not exist in
# these extractions: the count is zero for the Learning Python text, and the few
# matches in the others are figure captions and contents lines, not headings.
PAGE_FOOTER = re.compile(r"^\s*(\d{1,4})\s*\|\s*Chapter\s+(\d+)\b")
CHAPTER_HEAD = re.compile(r"^\s*Chapter\s+(\d+)\s*[.:]")
ENTITY = re.compile(r"&#x[0-9A-Fa-f]+;|&nbsp;|&#\d+;")


def _clean(text: str) -> str:
    """Drop the HTML entities the web-scraped extractions left behind."""
    return ENTITY.sub(" ", text) if "&" in text[:200000] else text


def chapter_index(book: str, text: str, chapters: list[dict]) -> list[tuple[int, int, int]]:
    """Return (offset, chapter, page) sorted by offset for a book's text.

    Page footers win when present because they are unambiguous and dense. Chapter
    headings are the fallback, and the title lookup is the last resort.
    """
    out: list[tuple[int, int, int]] = []
    pos = 0
    for line in text.splitlines(keepends=True):
        m = PAGE_FOOTER.match(CONTROL.sub("", line))
        if m:
            out.append((pos, int(m.group(2)), int(m.group(1))))
        pos += len(line)
    if len(out) >= 8:
        out.sort(key=lambda t: t[0])
        return out

    out = []
    pos = 0
    for line in text.splitlines(keepends=True):
        m = CHAPTER_HEAD.match(CONTROL.sub("", _clean(line.rstrip())))
        if m:
            out.append((pos, int(m.group(1)), 0))
        pos += len(line)
    if len(out) >= 8:
        out.sort(key=lambda t: t[0])
        return out

    return _title_index(text, chapters)


def _title_index(text: str, chapters: list[dict]) -> list[tuple[int, int, int]]:
    low = text.lower()
    found: list[tuple[int, int, int]] = []
    for ch in chapters:
        anchor = ch.get("title") or next(iter(ch.get("sections") or []), None)
        if not anchor:
            continue
        key = anchor.lower().strip()
        if len(key) < 6:
            continue
        pos = low.find(key)
        if pos == -1:
            continue
        found.append((pos, int(ch["chapter"]), int(ch.get("page") or 0)))
    found.sort(key=lambda t: t[0])
    return found


def locate(index: list[tuple[int, int, int]], offset: int,
           page_lookup: dict[int, int] | None = None) -> tuple[int, int]:
    """Return the (chapter, page) covering a byte offset.

    Only the page-footer strategy carries a real page number. For the other
    strategies the page is looked up from the catalogue by chapter number, so a
    ref is never reported with a placeholder page of zero.
    """
    lo, hi = 0, len(index) - 1
    best = (0, 0)
    while lo <= hi:
        mid = (lo + hi) // 2
        if index[mid][0] <= offset:
            best = (index[mid][1], index[mid][2])
            lo = mid + 1
        else:
            hi = mid - 1
    chapter, page = best
    if not page and page_lookup:
        page = page_lookup.get(chapter, 0)
    return chapter, page


def terms_for(title: str) -> list[str]:
    """Search terms for a day title: the whole skill phrase, then its tokens.

    The phrase carries the most signal, so it is tried first. Tokens are kept
    only when they are long enough to be domain vocabulary rather than grammar.
    """
    skill = title.split(":")[-1].strip()
    terms: list[str] = [skill]
    for tok in SEPARATORS.split(skill.lower()):
        if len(tok) > 3 and tok not in STOP:
            terms.append(tok)
    # De-duplicate while keeping order, and drop a token already inside the phrase.
    out: list[str] = []
    for t in terms:
        if t and t not in out:
            out.append(t)
    return out


HEADING_MAX = 70
# A period is allowed only when it is part of numbering, because chapter headings
# in these extractions read "Chapter 36. Visualization with Matplotlib" and
# forbidding every period rejected the real ones. A period followed by a letter or
# space would end a sentence, which a heading does not do.
HEADING_RE = re.compile(r"^(?:[A-Z][\w'&/+-]*\.?\s+)?[A-Z0-9][^.\n]{2,%d}$" % HEADING_MAX)
NUMBERED_HEADING = re.compile(r"^(?:Chapter\s+)?\d+(\.\d+)*\.?\s+\S")
# A table-of-contents line is padded with leader dots. It is not a heading.
TOC_RE = re.compile(r"\.{4,}")

# Words that almost never begin a heading, used to tell a heading apart from an
# ordinary sentence that happens to start with a capital letter.
PROSE_OPENERS = re.compile(
    r"^(The|This|That|These|Those|It|If|When|While|You|Your|We|Our|They|Their|"
    r"But|And|Or|So|Now|Here|There|Because|Since|Although|Though|Unless|Until|"
    r"After|Before|In|On|At|For|With|From|To|As|By|Of|Is|Are|Be|Do|Does|Did|"
    r"Consider|Imagine|Suppose|Note|Keep|Remember|Let|Use|Note that)\b"
)
COMMA_RE = re.compile(r",\s")


def phrase_regex(phrase: str) -> re.Pattern:
    """Word-boundary pattern for a phrase, tolerant of internal spacing.

    Boundaries matter: without them "forms" matches "transforms" and
    "informs", which is how a heading search reports twenty-one hits for a
    concept a book never actually has.
    """
    parts = [re.escape(p) for p in SEPARATORS.split(phrase) if p]
    if not parts:
        return re.compile(r"(?!x)x")
    body = r"[\s\-_]+".join(parts)
    return re.compile(rf"(?<![A-Za-z0-9]){body}(?![A-Za-z0-9])", re.I)


def _title_case_ratio(line: str) -> float:
    words = [w for w in re.findall(r"[A-Za-z][A-Za-z'\-]*", line) if w]
    if len(words) < 2:
        return 1.0 if words else 0.0
    capitalised = sum(1 for w in words if w[0].isupper())
    return capitalised / len(words)


CONTROL = re.compile(r"^[\x00-\x1f\x7f]+")


def is_heading(line: str) -> bool:
    """True only for a real book heading.

    A permissive rule that merely requires a leading capital matches ordinary
    prose, and then every word that appears anywhere in a sentence starts
    reporting as coverage. Book headings are short, mostly title-cased, and
    rarely open with a word that a sentence would use.

    Leading control characters are stripped first: the PDF extractions put a form
    feed at the top of every page, so a real chapter heading arrives as
    "\\x0cChapter 36. Visualization with" and would otherwise be rejected as
    indented text.
    """
    line = CONTROL.sub("", line or "")
    if not line or line[0].isspace():
        return False
    if TOC_RE.search(line) or COMMA_RE.search(line):
        return False
    if len(line) > HEADING_MAX:
        return False
    # Numbered headings are tested first. "Chapter 36. Visualization with
    # Matplotlib" carries a period as part of its numbering, so the strict
    # pattern below would reject it, and this extractions wrap long titles
    # across lines, leaving the key term on the first one.
    if NUMBERED_HEADING.match(line):
        return len(line.split()) >= 2
    if not HEADING_RE.match(line):
        return False
    if PROSE_OPENERS.match(line):
        return False
    if len(line.split()) < 2:
        return False
    return _title_case_ratio(line) >= 0.6


def index_coverage(index: list[tuple[int, int, int]], text_len: int) -> float:
    """Fraction of a book's text that lies inside located chapter anchors.

    Some extractions keep the table of contents but drop the running chapter
    titles, so every anchor clusters in the front matter and the rest of the book
    has no chapter to attach to. Where coverage is low, any chapter number this
    module reports is a guess, and the inventory says so rather than presenting a
    plausible-looking page number.
    """
    if not index or text_len <= 0:
        return 0.0
    first, last = index[0][0], index[-1][0]
    if last <= first:
        return 0.0
    return (last - first) / text_len


RANK = {"heading": 2, "phrase": 1, "token_only": 0}


def headings_of(text: str) -> list[tuple[int, str]]:
    """Line-initial headings with their offsets.

    A phrase that appears only in running prose is not evidence that a book
    covers a concept: "memory" occurs constantly meaning RAM, "forms" occurs as
    part of "information", and "accuracy" appears in timing advice. A heading is
    the one place a book commits to a topic by name, so it is the signal worth
    trusting.
    """
    out: list[tuple[int, str]] = []
    pos = 0
    for line in text.splitlines(keepends=True):
        stripped = CONTROL.sub("", line.rstrip())
        if is_heading(stripped):
            out.append((pos, stripped.strip()))
        pos += len(line)
    return out


def heading_hits(text: str, heads: list[tuple[int, str]], phrase: str,
                 tokens: list[str]) -> tuple[int, str | None, int]:
    """Count headings containing the phrase, then the best heading over tokens.

    Returns (phrase_heading_count, best_heading_line, its_offset).
    """
    pre = phrase_regex(phrase) if phrase else None
    tok_res = [re.compile(rf"(?<![A-Za-z0-9]){re.escape(t)}(?![A-Za-z0-9])", re.I)
               for t in tokens]
    n = 0
    best, best_off = None, 0
    for off, line in heads:
        hit_phrase = bool(pre.search(line)) if pre else False
        if hit_phrase:
            n += 1
            if best is None:
                best, best_off = line, off
            continue
        score = sum(1 for r in tok_res if r.search(line))
        if score >= 2 and (best is None or score >= 3):
            best, best_off = line, off
    return n, best, best_off


def search(book: str, text: str, index: list[tuple[int, int, int]],
           terms: list[str], *, min_hits: int,
           heads: list[tuple[int, str]] | None = None,
           page_lookup: dict[int, int] | None = None) -> dict | None:
    """Return the strongest match for one book, or None if unsupported.

    Tiers, strongest first:
      heading     the concept is named in one of the book's own headings
      phrase      the exact phrase appears in running prose only
      token_only  individual words appear, which proves nothing

    Only `heading` is reported as corpus support. The other two are surfaced so
    a human can promote or discard them, but a prose mention is not coverage.
    """
    heads = heads or []
    low = text.lower()
    phrase = terms[0].lower()

    n_head, head_line, head_off = heading_hits(text, heads, phrase, list(terms[1:]))
    if n_head:
        chapter, page = locate(index, head_off, page_lookup)
        return {
            "book": book, "chapter": chapter, "page": page,
            "strength": "heading", "in_front_matter": False,
            "phrase_hits": n_head,
            "token_hits": {"<heading>": n_head},
            "context": head_line or "",
        }

    pre = phrase_regex(phrase)
    phrase_hits = len(pre.findall(text)) if phrase else 0
    token_hits: dict[str, int] = {}
    for tok in terms[1:]:
        n = len(re.compile(rf"(?<![A-Za-z0-9]){re.escape(tok)}(?![A-Za-z0-9])", re.I).findall(text))
        if n:
            token_hits[tok] = n
    if phrase_hits == 0 and len(token_hits) < min_hits:
        return None

    strong = phrase_hits > 0
    if not strong and len(token_hits) < max(2, min_hits):
        return None

    m = pre.search(text)
    anchor = m.start() if m else low.find(sorted(token_hits)[0])
    if anchor == -1:
        return None
    chapter, page = locate(index, anchor, page_lookup)
    in_front_matter = bool(index) and anchor < index[0][0]

    return {
        "book": book, "chapter": chapter, "page": page,
        "strength": "phrase" if strong else "token_only",
        "in_front_matter": in_front_matter,
        "phrase_hits": phrase_hits,
        "token_hits": dict(sorted(token_hits.items(), key=lambda kv: -kv[1])[:6]),
        "context": " ".join(text[max(0, anchor - 90):anchor + 130].split()),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--inventory", default=str(INVENTORY))
    ap.add_argument("--out", required=True, help="updated audit inventory JSON")
    ap.add_argument("--min-tokens", type=int, default=2,
                    help="distinct tokens required when the phrase is absent")
    args = ap.parse_args()

    inv = json.loads(Path(args.inventory).read_text())
    items = json.loads(Path(args.out).read_text())

    texts = load_texts()
    indexes = {
        book: chapter_index(book, texts[book], inv[book]["chapters"])
        for book in inv
    }
    heads = {book: headings_of(texts[book]) for book in texts}
    cover = {b: index_coverage(idx, len(texts[b])) for b, idx in indexes.items()}
    pages = {b: {int(c["chapter"]): int(c.get("page") or 0) for c in inv[b]["chapters"]}
             for b in inv}
    valid_chapters = {b: set(pages[b]) for b in pages}
    for book, idx in indexes.items():
        print(f"  {book:<34} {len(idx):>3} chapters, {len(heads[book]):>5} headings, "
              f"index covers {cover[book]*100:>3.0f}% of text "
              f"({'refs reliable' if cover[book] >= 0.5 else 'chapter refs UNRELIABLE'})")

    targets = [i for i in items if i["recommended"] == "rewrite_new"]
    print(f"\nchecking {len(targets)} rewrite_new slots against {len(texts)} book texts\n")

    hits = weak = unclear = 0
    for item in targets:
        terms = terms_for(item["title"])
        best = None
        for book in texts:
            found = search(book, texts[book], indexes[book], terms,
                           min_hits=args.min_tokens, heads=heads[book],
                           page_lookup=pages.get(book))
            if found is None:
                continue
            # A front-matter match is a table-of-contents echo, never coverage.
            if found["in_front_matter"] and found["strength"] != "heading":
                continue
            # A contents listing numbers sections, not chapters, so a match can
            # resolve to a chapter number the book does not have. Such a ref is
            # not merely imprecise, it is impossible, and is dropped.
            if found["chapter"] and found["chapter"] not in valid_chapters.get(book, set()):
                found["invalid_chapter"] = True
                continue
            rank = (RANK[found["strength"]], found["phrase_hits"])
            if best is None or rank > (RANK[best["strength"]], best["phrase_hits"]):
                best = found

        item["matched_terms"] = []
        item["source_context"] = ""
        item["source_book"] = None
        item["source_chapter"] = None
        item["source_page"] = None
        item["match_strength"] = ""
        item["source_ref"] = ""
        item["ref_confidence"] = ""
        item["ref_note"] = ""

        if best is None:
            item["corpus_support"] = "none"
        else:
            tier = {"heading": "found", "phrase": "weak", "token_only": "unclear"}[best["strength"]]
            if best["strength"] == "heading":
                hits += 1
            elif best["strength"] == "phrase":
                weak += 1
            else:
                unclear += 1
            item["corpus_support"] = tier
            item["match_strength"] = best["strength"]
            item["source_ref"] = (
                f"{best['book']} ch{best['chapter']} (p{best['page']})"
                f" {best['strength']}={best['phrase_hits']}"
            )
            item["source_book"] = best["book"]
            item["source_chapter"] = best["chapter"]
            item["source_page"] = best["page"]
            item["ref_confidence"] = (
                "reliable" if cover[best["book"]] >= 0.5 else "unreliable_index"
            )
            item["index_coverage"] = round(cover[best["book"]], 3)
            item["ref_note"] = (
                "" if cover[best["book"]] >= 0.5
                else f"this book's chapter titles appear only in the front matter, "
                     f"so ch{best['chapter']} is a guess, not a verified location"
            )
            item["matched_terms"] = list(best["token_hits"].keys())
            item["source_context"] = best["context"]

    Path(args.out).write_text(json.dumps(items, indent=2))

    print(f"HEADING-supported {hits} | prose-only {weak} | word-only {unclear} | "
          f"unsupported {len(targets) - hits - weak - unclear}  of {len(targets)}\n")

    by_path: dict[str, Counter] = defaultdict(Counter)
    for i in targets:
        by_path[i["slug"]][i["corpus_support"]] += 1
    print(f"  {'path':<16}{'found':>8}{'weak':>8}{'unclear':>9}{'none':>8}{'total':>8}")
    print("  " + "-" * 56)
    for slug in sorted(by_path):
        c = by_path[slug]
        print(f"  {slug:<16}{c['found']:>8}{c['weak']:>8}{c['unclear']:>9}{c['none']:>8}{sum(c.values()):>8}")

    print("\n  HEADING-supported, by source book:")
    books = Counter(i["source_book"] for i in targets if i["corpus_support"] == "found")
    for b, n in books.most_common():
        print(f"    {b:<34} {n}")

    print("\n  HEADING-supported (the book names this concept as a heading):")
    for i in [x for x in targets if x["corpus_support"] == "found"]:
        print(f"    d{i['day']:<4} {i['title'][:40]:<42} {i['source_ref']}")

    print("\n  prose-only (exact phrase in running text, NOT counted as support):")
    for i in [x for x in targets if x["corpus_support"] == "weak"]:
        print(f"    d{i['day']:<4} {i['title'][:40]:<42} {i['source_ref'][:60]}")

    print(f"\ninventory updated: {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
