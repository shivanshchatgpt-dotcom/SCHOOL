# PySchool Book Corpus — Inventory & Canonical Topic Plan

Status: **pilot complete and seeded** (steps 1–9 done; steps 10+ = scaling)

---

## 0. Pilot result (2026-09-27)

One canonical-topic batch of four concepts × three real zero-lesson paths,
composed, validated, seeded and served end to end.

| Canonical topic | Provenance | Coverage | Days |
|---|---|---|---|
| `canonical:variable-binds-to-object` | Lutz ch 6, pp. 143–154 | full | 1/1/1 |
| `canonical:mutable-sequence-vs-copy` | Lutz ch 8, pp. 197–224 | full | 3/2/2 |
| `canonical:dict-as-mapping` | Lutz ch 8 pp. 197–224 + LPN ch 1 pp. 35–105 | full | 2/3/3 |
| `canonical:protocol-as-contract` | LPN ch 1, pp. 35–105 | partial | 4/4/4 |

Paths: `network-programming` (id 26), `etl-pipelines` (id 19),
`excel-automation` (id 10) — all three previously had zero lessons.

Verified:

- 12/12 composed lessons pass `curriculum_worker.validate()`.
- 12/12 worked examples execute and produce sane output.
- Database diff vs a pre-seed backup: 544 → 556 lessons, **0 modified, 0 removed**
  across lessons, milestones, assignments, lesson_milestones,
  milestone_prerequisites, paths, categories, assessment_questions.
- Backend test suite: 26 passed, 5 failed — the same 5 failures occur on the
  pre-seed backup, so they are pre-existing and unrelated.
- API round trip on `network-programming` day 1: lesson fetched (200), rubric
  accepted a compliant submission (`passed: True`) and rejected a weak one
  (`passed: False`, missing patterns reported by name).
- `seed()` is idempotent: a second run adds 0 canonical lessons.

Remaining gap is volume, not mechanism: `python -m gap_audit` reports 93 of 100
paths still empty and 117 of 120 corpus chapters still uncited.

---

## 1. Books found

Four source PDFs, all inside the repository (gitignored, never to be committed):

| Key | Title | Author | Edition | Pages | Words extracted |
|---|---|---|---|---|---|
| `learning-python` | Learning Python | Mark Lutz | 4th | 1213 | ~415,800 |
| `learning-python-networking` | Learning Python Networking | Fauno, Wade, et al. | 2nd | 697 | ~96,500 |
| `python-data-science-handbook` | Python Data Science Handbook | Jake VanderPlas | 2nd | 789 | ~121,800 |
| `python-programming` | Python Programming | Hans-Petter Halvorsen | 2026 | 143 | ~25,300 |

Text was extracted with `pdftotext -layout` into `.books/txt/`. Every chapter
entry below carries a **printed page number** recovered from form-feed (`\f`)
page boundaries, so any topic can be cited back to a real page range.

Extraction is done by `.books/parse_toc.py`, which writes `.books/inventory.json`.

## 2. Chapters/topics discovered — 120 chapters

**Learning Python (Lutz) — 39/39 chapters, pages 3–1051**
The deep Python core. Object types (ch 4–9: numbers, dynamic typing, strings,
lists/dicts, tuples/files), statements (ch 10–14), functions (ch 16–20), modules
(ch 21–24), OOP (ch 25–31), exceptions (ch 32–35), advanced (ch 36–39:
Unicode/bytes, managed attributes, decorators, metaclasses). This book alone
covers the entire foundation layer of every one of the 100 paths.

**Python Data Science Handbook (VanderPlas) — 50/50 chapters, pages 16–708**
Tooling (ch 1–3: IPython/Jupyter, interactivity, debugging/profiling), NumPy
(ch 4–12: types, arrays, ufuncs, aggregations, broadcasting, comparisons,
fancy indexing, sorting, structured arrays), Pandas (ch 13–24: objects,
indexing, operating, missing data, hierarchical indexing, concat/merge,
grouping, pivot tables, strings, time series, eval/query), Matplotlib (ch 25–36:
line/scatter/density plots, legends, colorbars, subplots, text, ticks,
config, 3D, Seaborn), Scikit-Learn (ch 37–50: ML framing, model validation,
feature engineering, Naive Bayes, linear regression, SVM, trees/forests,
PCA, manifold learning, k-means, GMMs, KDE, face-detection pipeline).

**Learning Python Networking (Fauno/Wade) — 12/12 chapters, pages 35–628**
TCP/IP programming, HTTP, APIs, web scraping (BeautifulSoup/Scrapy), email,
remote systems (SSH), IP/DNS, IPv6, network automation with Ansible, sockets,
async servers (asyncio/aiohttp), web applications. This is the only book that
reaches the networking/infra paths.

**Python Programming (Halvorsen) — 19 chapters, 143 pages**
Gentle introduction: IDEs, basic programs, if/else, loops, functions, modules,
error handling, pip, environments, Anaconda, VS Code/Visual Studio, Jupyter,
math functions, distributions. Short book, but the natural source for the
shallowest "Surface" paths where Lutz's 1200 pages is too dense.

### Coverage map (which books can serve which path depth)

- **Core Python**: all four books, with Lutz as the authoritative deep source
  and Halvorsen as the shallow on-ramp.
- **Data / ML / visualisation paths**: VanderPlas (50 chapters, all toolchain).
- **Networking / DevOps / infra paths**: LPN only.
- **Web/API paths**: LPN ch 2 (HTTP), ch 3 (APIs), ch 12 (web apps); plus Lutz
  for the Python underneath.
- **Theoretical / research paths (AGI, compilers, formal methods)**: **GAP** —
  no book covers theory of computation, distributed systems, or ML research
  methodology. These must be explicitly marked as corpus-insufficient.

## 3. Proposed canonical-topic schema

One record per reusable concept, with provenance attached. Stored as Python
modules for reviewability (matching the existing `ds_topic_library.py` style).

```python
{
    # Identity
    "id": "canonical:mutable-vs-immutable-sequence",
    "name": "Mutable vs immutable sequences",

    # Provenance (requirement 4) — never a fact without a source
    "sources": [
        {
            "book": "learning-python",
            "chapter": 8,              # Lutz, "Lists and Dictionaries"
            "pages": [197, 224],       # printed page range
            "sections": ["Lists", "List comprehension expressions"],
        },
        {
            "book": "python-programming",
            "chapter": 6,
            "pages": [61, 66],
            "sections": ["Lists"],
        },
    ],
    "coverage": "full",          # full | partial | insufficient

    # The teachable core, authored once (requirement 8: transformed, not copied)
    "concept": "...",            # 2-4 sentence canonical explanation
    "prerequisites": ["canonical:variable-as-reference", "canonical:sequence-basics"],
    "common_pitfalls": ["..."],

    # Path adapters — how the SAME topic is taught differently per audience
    # (requirement 6: sequencing/examples/practice stay path-specific)
    "adapters": {
        "web-dev": {
            "framing": "Why mutating a list in a request handler is safer than rebinding.",
            "example_hint": "append to a list of log entries inside a view",
        },
        "data-science": {
            "framing": "In-place array ops vs copies — memory in large datasets.",
            "example_hint": "in-place sort of a DataFrame column slice",
        },
        "networking": {
            "framing": "Mutable buffers vs immutable bytes when reading sockets.",
            "example_hint": "accumulate received chunks in a list before join()",
        },
    },
}
```

Composition rule: the canonical record supplies the **concept**, provenance, and
prerequisites. Each path supplies the **framing**, worked example, questions and
homework through its adapter. No adapter means the path falls back to the
default framing — and the lesson is marked `coverage: partial`.

## 4. How one canonical topic composes into multiple paths

Take `canonical:dict-as-mapping` (Lutz ch 8, pp 197–224; Halvorsen ch 6).

- **Web Development path** — framed as "routing tables": a dict maps URL
  patterns to view callables. Example builds a tiny dispatcher. Homework: add
  a route and a 404 fallback. Prereq: `canonical:function-basics`.
- **Data Science path** — framed as "column lookup": a dict maps column names
  to dtypes. Example builds a schema validator for a CSV. Homework: detect a
  mismatched column.
- **Networking path** — framed as "packet header fields": a dict maps header
  names to values parsed off the wire. Example parses a simple header block.
  Homework: handle a repeated header.
- **Surface path** (shallowest category) — framed as "phone contacts": keys are
  names, values are numbers. Example is 8 lines. Homework is one short task.

Same provenance line in all four (`Lutz ch 8, pp 197–224`), same underlying
concept paragraph, but four different framings, examples, practice tasks and
question sets. That satisfies requirements 5 and 6 by construction, and
requirement 7 is enforced because no lesson can exist without a `sources` entry.

## 5. Files to be created / modified

**Created (new, additive only):**

| File | Purpose |
|---|---|
| `.books/canonical_topics.py` | The canonical library: one record per topic with provenance + adapters. Populated incrementally. |
| `.books/build_chapter_index.py` | Indexes each book's text by page so a topic's source range can be re-read on demand. |
| `backend/app/canonical_library.py` | Importable copy of the canonical records (the seed layer reads this). |
| `backend/app/lesson_composer.py` | `compose_lesson(canonical_id, path_slug) -> lesson tuple` — turns a canonical record + adapter into the 7-tuple `seed.py` consumes. |
| `backend/app/canonical_provenance.py` | `provenance_report()` — lists every lesson's source book/chapter/pages, for the README and for gap auditing. |

**Modified (non-destructive, requirement 9):**

| File | Change |
|---|---|
| `backend/app/seed_data.py` | Add a `CANONICAL_TOPIC_IDS` map alongside the existing topic lists. Existing authored entries (`COMMON_TOPIC_LIBRARY`, `DS_TOPIC_LIBRARY`) stay authoritative; the composer only supplies lessons that are **not** already authored. |
| `backend/app/seed.py` | New `_seed_canonical_lessons()` that runs after existing seeding and only fills empty `(path, day)` slots — never overwrites a row that exists. |
| `README.md` | Add the provenance/corpus section. |

**Explicitly untouched:** all three existing launch curricula, `ds_topic_library*`,
`curriculum_automation*.py`, `curriculum_web_dev.py`, the frontend, and every
existing DB row.

## 6. Proposed pilot (before any scaling)

Scope: **one canonical topic → three paths**, end to end.

1. Author `canonical:dict-as-mapping` with provenance (Lutz ch 8 pp 197–224 +
   Halvorsen ch 6).
2. Implement `lesson_composer.compose_lesson()` and verify the output passes the
   existing `curriculum_worker.validate()` rules (3 questions, 3 answers,
   theory 450–900 words, code parses via `ast.parse`, homework >=120 chars,
   non-empty patterns).
3. Compose it for `web-dev`, `data-science`, and one currently-empty path.
4. Seed via the new non-destructive seeder, confirm the three rows land and the
   existing 540 lessons are unchanged (row count + spot-check).
5. Run the backend test suite.
6. Only then, scale the canonical library chapter by chapter, starting with
   Lutz ch 4–9 (the foundation layer every path needs).

## 7. Known gaps to mark explicitly (requirement 7)

- No source for theory of computation, distributed systems, ML research
  methodology, compilers, or formal verification → paths like `agi-research`
  and the deep theoretical categories will carry `coverage: insufficient`.
- LPN has no section-level page detail (12 chapters, page numbers only) →
  section-level provenance will be coarser for networking topics.
- Lutz 4th ed. covers Python 3 up to ~2009 → modern syntax (f-strings,
  `match`, `|` unions) is **not** in the corpus and must be marked
  `coverage: partial` with the gap stated in the lesson.
