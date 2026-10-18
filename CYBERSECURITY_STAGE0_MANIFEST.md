# Stage 0 — Cybersecurity Flagship: Inventory + Write Manifest (APPROVAL REQUIRED)

**Mode:** inspection only. Zero file edits, zero DB writes performed. No reseed, no version bump.
**Date:** 2026-10-01. **DB:** `backend/pyschool.db` (meta: `seed_version=9`, `catalog_depth=3`, `catalog_topics=catalog-basics`).

## 1. Inventory

**Cybersecurity paths found (4 genuine + 1 excluded):**

| id | slug | name | diff | lessons | canonical | theory/d | questions | status |
|---|---|---|---|---|---|---|---|---|
| 25 | cybersecurity | Cybersecurity / Pentesting | 4 | 180 | 0 | 1,471 | 13 (10+3 gen) | all active |
| 27 | cryptography | Cryptography Implementation | 4 | 180 | 0 | 1,491 | 13 (10+3 gen) | all active |
| 92 | malware-analysis | Malware Analysis / Reverse Engineering | 5 | 180 | 0 | 1,489 | 13 (10+3 gen) | all active |
| 93 | forensics | Digital Forensics Tooling | 5 | 180 | 0 | 1,468 | 13 (10+3 gen) | all active |
| 52 | crypto-bots | Crypto Trading Bots | 4 | — | — | — | — | EXCLUDED: trading, not security |

All four: 180 milestones, 180 assignments, prerequisite chains complete (no missing d→d−1 edges), days 1–14 = generic catalog foundation, days 15–74 = shared Python phases, days 75–179 = generic 15-frame template (lib name in strings only), day 180 = capstone reflection.

**Considered and excluded:** `api-building`, `network-programming`, `testing-qa`, `database-ops`, `devops-scripting`, `cloud-computing`, `package-dev` — different architectures/safety controls; would need separate review. Not in scope unless approved.

**Protected content (never touched):** web-dev (428k), data-science (383k), machine-learning flagship (380k), agi-research, automation days 1–4 (`AUTOMATION-001…004`), all canonical/book-grounded lessons (none exist on the 4 target paths — verified 0), shared days 15–74 on every path, all other 93 paths in full.

**Existing applier pattern (to reuse):** `backend/app/apply_ml.py` — `--apply` gated (default dry-run/check), allowlist `OWNED_DAYS`, refuses to create rows, compare-before-write, idempotency self-check, updates lessons + assignments + milestone title/domain/objective only (codes/ids/edges untouched). Quality gates: 450–900 theory words, code executes with captured output, exactly 3 Q&As, homework ≥120 chars, non-empty patterns, no placeholder tokens. Tests: `backend/tests/test_ml_flagship.py`.

**Environment constraint (verified):** `.venv` has sklearn/pandas/pytest but **no bcrypt, no PyCryptodome, no scapy**. New dependencies are forbidden → all crypto demos use stdlib (`hashlib`, `hmac`, `secrets`, `hashlib.pbkdf2_hmac` for password hashing — stated honestly as PBKDF2, not bcrypt); network demos use synthetic logs/sockets on localhost only; malware/forensics use synthetic byte samples, never live malware.

**UI entry points:** `frontend/src/App.tsx` — `/` Home, `/paths`, `/paths/:slug/assessment`, `/dashboard/:id` (lesson detail + Think Check + homework + progress live here). No SPA admin route.

**Test commands:** `cd backend && .venv/bin/python -m pytest -q` (currently 39 passed); `cd frontend && npm run build`. Scratch DBs: file-copy of `pyschool.db` to `/tmp/*.db` + `DB_PATH` override (established pattern; prior `/tmp/*.bak` files exist but were **not** relied on — live DB inspected directly).

**Git state:** working tree dirty (prior approved work uncommitted: `db.py`, `seed.py`, routers, `curriculum_ml.py`+`apply_ml.py` untracked, etc.). No commits will be made without request.

## 2. Proposed batches (each needs separate promotion approval)

| Batch | Path(s) | Days/path | Lessons | Why this order |
|---|---|---|---|---|
| 1 (pilot) | cryptography (id 27) | 1–14 + 75–179 | 119 | Safest: pure-stdlib crypto, zero offensive-content risk; proves pipeline |
| 2 | cybersecurity (id 25) | 1–14 + 75–179 | 119 | Defensive framing required; pentesting path needs strict lab-only rules |
| 3a | forensics (id 93) | 1–14 + 75–179 | 119 | Synthetic-evidence only |
| 3b | malware-analysis (id 92) | 1–14 + 75–179 | 119 | Highest sensitivity: static-analysis-only, synthetic samples, no evasion/persistence content |

Days 15–74 (shared Python phases) preserved on all four, as in the ML precedent. Total: 476 authored lessons.

**Taxonomy map (A–G → actual days):** A Foundations → days 1–14 per path (security-framed Python: CIA triad, threat models, hashes, auth, parsing untrusted input); B–F → seven 15-day domain phases per path (e.g. crypto: encodings → hashes → symmetric → asymmetric → TLS/PKI → password storage → capstone); G → phase-7 capstone + review days per path.

## 3. File-change plan (proposed, not started)

- `backend/app/curriculum_cybersecurity.py` (new): per-batch content dicts (Batch 1 first; later batches appended after Batch 1 promotion).
- `backend/app/apply_cybersecurity.py` (new): `--apply` gated, allowlist `{(slug, days)}` per approved batch only, dry-run report (inserts/updates/skips/refusals), compare-before-write, idempotency self-check, transaction + rollback on failure.
- `backend/tests/test_cybersecurity_flagship.py` (new): scope safety (unapproved slugs/days refused, dry-run mutates nothing), content gates (schema, 3 lesson-specific Q&As, no duplicates/placeholders, prereq validity), execution (examples run, outputs match, idempotent), e2e (enroll→lesson→dashboard on scratch).
- No changes to `seed.py`, schema, routers, frontend, or any existing curriculum file.

## 4. Exact write manifest — Batch 1 (cryptography, id 27)

- Rows: 119 lesson UPDATEs (title/theory/code_example/questions/answers/homework) + 119 assignment UPDATEs (prompt/required_patterns) + 119 milestone UPDATEs (title/domain/objective only) for `(path_id=27, day IN 1–14, 75–179)`.
- Milestone codes (`CRYPTOGRAPHY-001…`), ids, and all `milestone_prerequisites` edges: untouched.
- Refusals guaranteed: any other `path_id`, days 15–74 and day 180 on path 27, all canonical/automation/launch/ML rows.
- Predicates are exact `(path_id, day_number)` pairs — no broad UPDATEs.

## 5. Validation plan per batch (Stage 3)

1. Record git diff + protected-content hashes (launch tracks, automation 1–4, ML path, canonical sample).
2. File-copy backup (`/tmp/pyschool.pre-cyber-b<N>.bak`), verify byte size.
3. Scratch copy in `/tmp`, confirm separate path; dry-run report review.
4. Apply batch to scratch only; check: row counts (119/119/119), gates (450–900w, exec outputs match, 3 specific Q&As, no placeholders/dupes), idempotency (2nd run 0 changes), protected hashes identical, prereq chain 179/179, pytest green, e2e enroll→lesson→homework→dashboard, UI spot-check (lesson render, Think Check, roadmap) with honestly stated limits.
5. Report PASS/BLOCKED/NOT RUN per check. Stop. Wait for promotion approval. Only then apply to dev DB (fresh backup first), re-verify, report.

**STOPPING HERE. No content written, no database mutated. Awaiting approval of this manifest to begin Stage 1 (Batch 1 module + applier + tests, then Batch 1 authoring).**
