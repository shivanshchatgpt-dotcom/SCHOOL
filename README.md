# PySchool

PySchool is a goal-based Python learning-school MVP: it asks *what you want to
become*, tests your level, then delivers a daily 1-hour class with homework,
progress tracking and streaks — like a real school.

## Architecture at a glance

- **Catalog:** 100 planned learning paths organised into 10 depth categories
  (Surface → AGI), defined in `backend/app/seed_data.py`.
- **Launch tracks:** 3 paths are fully implemented — **Web Development**,
  **Data Science / Analysis**, **Python for AI Research**
  (`LAUNCH_PATH_SLUGS`). Each carries a complete **180-day curriculum**:
  14 hand-authored foundation days, topic-driven days 15–179 drawn from an
  authored shared-topic library plus track-specific phase templates, and a
  Day-180 capstone reflection.
- **Future catalog:** the other 97 paths stay visible as future tracks and are
  deliberately *not* exposed as courses until real curricula exist
  (`is_launch_ready = 0`). This is a deliberate phased implementation, not a
  placeholder.
- **Placement:** every path has a multiple-choice level test. Score percentage
  maps to Foundation / Beginner / Intermediate / Advanced, which determines the
  starting day (1 / 4 / 7 / 10) and lists weak topics.

## Learning flow

```
pick path → placement test → starting milestone
→ daily lesson (theory + worked example + rubric)
→ coding practice (AST-parsed, never executed)
→ pass rubric → complete milestone → XP +10/+15, streak +1, day advances
→ repeat to Day 180
```

## Safety note

Assignment submissions are parsed with Python's `ast` module but **never
executed** on the API server. The checker validates syntax, minimum non-empty
lines and required language constructs using whitespace-tolerant matching
(e.g. `print ("hi")` passes a `print(` requirement). Running hidden behavioural
tests would require a separate sandboxed execution service before production.

## MVP access control

- Student endpoints under `/api/enrollments/{id}/…` require the
  `X-Enrollment-Token` header. The token is issued once by the assessment
  submit endpoint and stored in the learner's browser.
- Teacher endpoints under `/api/admin/…` require `X-Admin-Token` matching the
  `PYSCHOOL_ADMIN_TOKEN` environment variable (default `pyschool-admin` for
  local development only — set a real value before deploying).
- CORS origins are restricted to localhost dev origins by default; override
  with `PYSCHOOL_CORS_ORIGINS="https://yourdomain"` in deployment.

> Note: SEED_VERSION 3 re-seeds content on startup and regenerates access
> tokens; existing browser sessions may need to re-enroll once after upgrading.

## Run locally

Start the API in one terminal:

```bash
cd backend
python -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m uvicorn app.main:app --reload --port 8001
```

The SQLite database is created and seeded automatically when the API starts.
Reset it (wipes demo data) with:

```bash
rm -f backend/pyschool.db
```

Run the automated test suite:

```bash
cd backend
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m pytest -q
```

Start the web app in another terminal:

```bash
cd frontend
npm install
npm run dev
```

Open http://127.0.0.1:5173.
