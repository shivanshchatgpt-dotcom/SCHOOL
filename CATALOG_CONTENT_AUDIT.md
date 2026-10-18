# Catalog Content Quality Audit — 97 generated paths (+ 3 launch tracks)

**Date:** 1 October 2026. **Mode:** read-only. No reseed, no version bump, no content/schema/code changes were made.
**Database:** `backend/pyschool.db` (dev copy state: 18,000 lessons, 1,300 questions, 100 paths).
**Scope:** all 100 paths; launch tracks (web-dev, data-science, agi-research) checked for intactness only.

**Overall summary:** Structure is complete and mechanically sound (180/180 days, 13/13 questions, 0 broken links, 0 placeholder tokens, 0 output mismatches in 10,185 verified examples). But only **15 distinct lessons exist per 105 domain days** — each frame repeats 7× with identical body — and every worked example is **domain-agnostic** (the path library appears only inside string literals). One path (`automation`) was missed by the refresh and still serves the old shallow template. Nothing here is high quality yet by flagship standards; it is honest template grade. Details and severity-ranked findings below.

**Method — automated (scripts `/tmp/audit1.py`, `/tmp/audit2.py`, full-table SELECT scans):**
89,460 lesson rows scanned across checks; every code example on domain days re-executed and stdout compared to the embedded "Running it prints" block (10,185 days).

**Method — manual (human-read, full lessons):** quantum-computing day 75 (full read), web-scraping day 1 (full read, canonical), bioinformatics day 120, load-testing day 30, game-dev day 180, automation day 80, machine-learning days 1–8 titles + assessment triplet for quantum-computing. Findings marked [manual] vs [auto] below.

---

## 1. Inventory [auto]

| Check | Result |
|---|---|
| Paths | 100/100 present |
| Lessons per path | 180/180 on all 100 paths |
| Milestones per path | 180/180, sort_order 1–180 contiguous, no gaps |
| Assignments per path | 180/180, min_lines = 3 everywhere |
| Assessment questions per path | 13/13 on all 100 paths (1,300 total) |
| Day continuity | 0 missing / 0 duplicate days on every path |
| Prerequisite edges (day d → d−1) | complete on all 100 paths; every lesson has exactly one milestone link |
| Placeholder tokens (`__LIB__`, `__DOMAIN__`, `{lib}`, TODO, lorem, TBD …) | 0 hits in 18,000 lessons |
| Launch tracks intact | web-dev 428,009 / data-science 383,479 / agi-research 253,413 theory chars — byte-identical to pre-upgrade snapshots |
| Automation hand-authored days 1–4 | intact (verified day-1 theory prefix match) |
| Correct-answer distribution (1300 Qs) | A 55% / B 23% / C 15% / D 8% — skewed by the pre-existing 10-question base set (6×A), not by generated triplets |

## 2. Critical failures (fix before any new authoring)

**C1 — `automation` path serves stale shallow content on 176/180 days [auto].**
Days 5–180 still carry the pre-deepening template (no variants, no mistakes section, no captured outputs, 2 Q&As instead of 3). Cause identified (not fixed): the refresh heuristic skips any lesson whose milestone code starts with `AUTOMATION-`, but catalog-filled days on this path also carry `AUTOMATION-005…180` codes — so the whole path was excluded except nothing. Evidence: `automation` day 80 theory opens with the old `**Where this fits**` template; 176 lessons with Q/A ≠ 3, all on this slug, zero elsewhere.
Recommended fix (needs approval): narrow the exclusion to the four hand-authored codes (`AUTOMATION-001…004`) and re-run the refresh for days 5–180 only.

**C2 — Only 15 distinct lessons per 105 domain days; each repeats 7× byte-identically [auto + manual].**
Days 75/90/105/120/135/150/165 (frame 1) on quantum-computing are character-identical; only the phase prefix in the title differs. Counts of duplicate-theory rows: 90 on single-library paths, 60–75 on multi-library paths (lib rotation changes tokens). A student re-reads "Orientation: what Qiskit is for" seven times.
Recommended fix: 105 distinct days per path — either 7 genuinely different phases or per-phase frame variants. This is the core reason the next flagship path must be hand-authored, not regenerated.

**C3 — Worked examples are domain-agnostic; libraries appear only in string literals [manual].**
quantum-computing day 75 ("Orientation: what Qiskit is for") teaches `zip()` of two lists — zero quantum content; swapping Qiskit→Pandas changes only string text. True of all 15 frames: no frame imports, calls, or models its path's library (stdlib-only by design). A Bioinformatics student never touches biological data; a Robotics student never touches hardware concepts. The framing ("In Bioinformatics … whenever Biopython meets real input") over-claims what the code teaches.
Recommended fix: per-track worked examples that genuinely use the domain (even simulated with stdlib data shaped like the domain, e.g. DNA strings for bioinformatics, price series for trading). This cannot be templated once for 97 domains — it is the flagship-authoring work itself.

**C4 — Think-Check questions do not test lesson-specific understanding [auto + manual].**
Q1 ("What does {topic} let you express…") repeats per frame (672× each); Q2/Q3 are fully generic metacognitive prompts repeated **10,080× each** across 17,460 lessons. They are good study habits but interchangeable between any two lessons. (Precedent: flagship DS practice days use the same generic Q2/Q3 — so this matches flagship *practice-day* style, but no catalog lesson has a lesson-specific recall question.)
Recommended fix: during flagship authoring, write one lesson-specific Q1 per day (keep generic Q2/Q3).

**C5 — No difficulty ramp across the 105 domain days [manual].**
Phase 7 ("capstone preparation") serves the same 15 frames at the same difficulty as phase 1 ("foundations"). Titles claim progression; bodies do not progress. Within one phase the frame order (orientation → setup → … → review) is a sensible arc; across phases there is none.
Recommended fix: part of flagship authoring (basics → intermediate → project phases with distinct topics, as DS/Web tracks have).

**C6 — Assessment topic taxonomy is inverted [auto].**
Generated triplets are labeled `track-basics`, while the six hand-written non-launch flagship extras (automation, chatbots, machine-learning, web-scraping + 2) are labeled `python-basics`/`python-practice` (the `track-basics` label in seed applies only to launch slugs). So the label now means the opposite of its intent.
Recommended fix: relabel generated triplets (e.g. `catalog-basics`) or relabel hand-written ones — one UPDATE, after approval.

## 3. Medium / low findings (no action needed before flagship work, recorded for completeness)

- **M1.** Foundation (days 1–14) and shared-phase (15–74) homework lacks a named-function contract (~8,700 lessons without backticked function names). Matches flagship foundation style; not a defect.
- **M2.** Shared-phase theory averages 322 chars/day and has no fenced code in theory on ~6,197 lessons. Pre-existing authored style, shared with flagships; leave as is.
- **M3.** Day-180 capstone is thin (135 chars) on all catalog paths — identical text to the flagship capstone. Consistent; leave.
- **M4.** Answer-key A-bias (55%) comes from the pre-existing base set, predates this work, affects placement psychometrics mildly. Out of scope; noted.
- **M5.** Canonical book-grounded lessons (up to 10/path, e.g. web-scraping day 1, Lutz ch.4 with provenance) are the highest-quality catalog content. Must never be overwritten — current pipeline already excludes them.

## 4. Representative lesson reviews [manual]

- **quantum-computing day 75** (full read): structure complete, output block byte-accurate, variants/mistakes/homework coherent — but teaches list-zipping, not Qiskit. Verdict: good Python practice, misleading domain framing.
- **web-scraping day 1** (canonical, full read): genuinely domain-flavored (parse raw strings → named rows), sourced (Lutz ch.4), strong. Verdict: keep as the quality bar.
- **bioinformatics day 120**: identical body to day 75 modulo tokens ("Biopython … meets real input", same `describe()` code). Verdict: exhibits C2 + C3.
- **load-testing day 30** (shared phase): thin but correct and honest. Verdict: acceptable.
- **game-dev day 180**: capstone reflection, same as flagship text. Verdict: acceptable.
- **automation day 80**: stale shallow template (exhibits C1). Verdict: must be refreshed.
- **quantum assessment triplet** (all 3 read): correct answers, distinct plausible distractors, valid difficulties. Verdict: good.

## 5. Remediation plan (proposed, awaiting approval — nothing applied)

1. **P0:** Fix C1 — narrow automation exclusion to `AUTOMATION-001…004`, refresh days 5–180 (~10 lines in `seed.py`, one boot).
2. **P0:** Fix C6 — relabel generated triplet topic (one UPDATE or one-line generator change + refresh).
3. **P1:** Author the recommended next flagship path lesson-by-lesson (plan below), which resolves C2–C5 for that path by construction.
4. **P2 (later):** repeat P1 per track, highest-demand first; revisit answer-key balance (M4) only with a psychometrics pass over the base set.

## 6. Rows, files, tests, limitations

- Rows inspected: 18,000 lessons + 18,000 milestones + 18,000 assignments + 18,000 lesson_milestones + ~18,000 prerequisite edges + 1,300 questions (full tables, SELECT-only). 10,185 domain code examples re-executed; 0 errors, 0 output mismatches.
- Files read: `backend/app/curriculum_catalog.py` (generator), `backend/app/seed.py` (fill/refresh/flags), `backend/app/seed_data.py` (PATHS, COMMON_180_PHASES, flagship questions), `backend/app/lesson_composer.py`, `backend/app/canonical_topics_proxy.py`, `backend/app/routers/assessment.py`, `backend/tests/test_catalog.py`.
- Tests run: `pytest -q` → 36 passed (includes catalog generator/fill/idempotency tests; suite uses throwaway tmp DBs, never the dev DB).
- Limitations: (a) automated output check covers only domain days 75–179 (foundation/common/capstone examples were parse-checked at authoring time, not re-executed here — day-3 `input()` and day-11 file writes are display-only by design); (b) manual review covered 7 lessons + 1 triplet in full — the C2/C3 verdicts generalize via byte-identity proofs, but prose quality of every one of 17,460 lessons was not human-read; (c) pedagogy judgments (C4/C5) are reviewer opinion against flagship precedent, stated as such; (d) no student outcome data exists, so "difficulty ramp" is assessed structurally, not empirically.

---

## 7. Recommendation: next flagship path — **Machine Learning** (`machine-learning`)

**Why this path:** (1) Surface category (category 1) — the beginner funnel where enrollment demand concentrates; (2) difficulty 3, the natural step after Data Science, reusing adjacent strength; (3) already has hand-written flagship assessment extras and **8 canonical ML-flavored foundation days** (days 1–8, e.g. "Stream the Dataset Line by Line", "Transform a Copy…") — the best starting base of any catalog path; (4) highest real-world student demand of the remaining tracks; (5) `scikit-learn` single library keeps worked examples coherent.

**Its major quality gaps (from this audit):** days 9–14 are generic catalog foundation ("Dictionaries", "Debugging…") with no ML framing; days 15–74 shared Python phases are fine as-is; days 75–179 are the generic 15-frame set with `scikit-learn` only in strings — no train/test split, no overfitting, no model evaluation is actually taught despite titles like "Scikit-learn performance and polish".

**Concrete implementation plan (after your approval, incremental with verification):**
1. New module `backend/app/curriculum_ml.py`: 7 hand-authored 15-day phases mirroring the DS pattern — ML Setup & Data → Regression → Classification → Trees & Forests → Overfitting & Validation → Pipelines & Tuning → ML Capstone (105 days). Each day: theory 450–900 words, runnable stdlib-worked example with captured output, 2 variants, 3 mistakes, 3 Q&As (1 lesson-specific), named-function homework with honest `required_patterns`. Reuse DS_TOPIC_LIBRARY predictive-modelling topics where they fit; write the rest.
2. New applier `backend/app/apply_ml.py` (`--apply` gated, validates + executes every example, idempotency self-check), following `apply_web.py` precedent — writes only `machine-learning` days 9–14 + 75–179, never launch tracks, never canonical slots, never automation.
3. Validation gates per day (same as `lesson_composer`/`curriculum_worker`): word budget, example runs, Q/A count, patterns satisfiable, no placeholder tokens.
4. Tests: extend `test_catalog.py`-style checks (105 distinct bodies, outputs match, idempotent re-apply adds 0); full suite must stay green.
5. Verify on scratch DB first (metrics vs DS track: ~380k theory chars target), then apply to dev DB, then report.

**Stopped here. Awaiting your approval** — for the P0 fixes (C1, C6) and/or the Machine Learning flagship plan — before changing anything.
