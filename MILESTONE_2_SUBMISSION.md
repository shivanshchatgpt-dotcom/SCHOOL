# Milestone 2 Report: PySchool

**Project:** PySchool, a goal-based Python learning platform
**Submitted to:** Skills Development Monitoring System (SDMS), MITS-DU Gwalior
**Milestone:** 2 of 3, Content Depth and Pedagogy
**Date:** 30 September 2026
**Team:** Shivansh (shivanshchatgpt@gmail.com)
**Builds on:** Milestone 1 (Core MVP, commit `7d73f1a`)

---

## Objective

Milestone 1 proved the platform works end to end. It did not prove the
teaching was any good, and that was the problem worth fixing. A student could
work through 180 days of material, but a large part of that material was
generated from templates. It covered the right topics in the right order, and
it read like a syllabus rather than a teacher.

Milestone 2 focused on the content itself: replacing template material with
really written lessons, and adding a feature that makes students think before
they move on. The goal was to raise the quality of a single day, not to add
more days.

---

## What was delivered

**1. The Data Science track, fully authored**

All 105 track-phase days of the Data Science programme, covering Days 15 to
179, were written out by hand. This was the largest single piece of work in the
milestone, roughly 1,000 lines of authored curriculum across six phase
modules. Each of these days now has real theory explaining what is actually
happening, a worked example that runs, layered questions, and a homework task.

The written material for the Data Science track now stands at about 383,000
characters of theory, 117,000 characters of code examples, 43,000 characters of
questions and 87,000 characters of answers, across all 180 days. For
comparison, the Web Development track holds 428,000 characters of theory, so
the two flagship tracks are now of comparable depth.

**2. Think Check, a new lesson feature**

Every one of the 705 lessons in the system now carries a set of questions and a
set of answers. The dashboard renders these as a "Think check" panel: the
student sees a question, answers it in their own head or on paper, and only
then clicks to reveal the answer. There is no partial credit for guessing.

This was added because reading a lesson and understanding a lesson are different
things, and the platform had no way to tell the difference. A student who
cannot answer the questions has not finished the day, even if they scrolled
through all the text.

**3. Foundation theory rewritten**

The first three days of the foundation block were rewritten after working
through Mark Lutz's *Learning Python* Chapter 6. The original lessons
described variables as boxes holding values. The rewrite explains the reference
model properly: variables are references to objects, the type belongs to the
object rather than the name, and that is why reassignment behaves the way it
does. Students who learn Python this way do not have to unlearn it later.

---

## Technology

Unchanged from Milestone 1, which is itself worth noting. This milestone added
no new dependencies, no new frameworks and no architectural changes. The
backend is Python with FastAPI, SQLAlchemy and SQLite; the frontend is React
with TypeScript and Vite. The new lesson fields are stored in the existing
`lessons` table, and the Think Check component is a self-contained React
component in the dashboard.

Total change across the milestone: 10 files, about 1,060 lines added.

---

## Main design decisions

**One track done properly before three done partly.** The Data Science track
was chosen rather than spreading effort across all three. The Web Development
track was already the deepest, so the weakest flagship track was the right place
to spend the time. All three will be brought to the same standard, one at a
time.

**Questions the student cannot scroll past.** Requiring an explicit reveal
before the answer appears adds a small amount of friction on purpose. It is
the difference between a lesson that was read and a lesson that was learned.

**Reference model taught on day one.** Most introductory courses describe
variables as containers, and students then have to unlearn that idea before
objects and references make sense. Teaching it correctly at the start costs
more words on Day 1 and saves rework later.

**No new architecture.** Adding a separate service for questions, or a
different rendering path for authored versus generated content, would have made
this milestone more interesting to build and the product worse to maintain. The
same lesson pipeline serves both kinds of lesson.

---

## Outcome

| Objective | Status |
|---|---|
| Data Science track fully authored | Done, 105 track-phase days written by hand |
| Theory grounded in a reference text | Done, Days 1 to 3 rewritten from Lutz Chapter 6 |
| Think Check question and answer feature | Done, shipped on all 705 lessons |
| Comparable depth across flagship tracks | Partly, Data Science now matches Web Development |
| Equal depth across all three tracks | Not yet, Python for AI Research is lighter |
| No regression in existing behaviour | Done, no architectural change, seeding unchanged |

---

## What comes next

The immediate work is finishing the same job on the Python for AI Research
track, which currently carries about 253,000 characters of theory against
roughly 380,000 and 428,000 for the other two. It is written and functional
across all 180 days, but the material is lighter and needs the same treatment.

Beyond that, the remaining items from Milestone 1 still stand: real student
accounts, a sandboxed execution service so assignments can be tested for
behaviour rather than only structure, spaced-repetition revision using the
existing mastery data, project weeks, portfolio export, and deployment.

---

## Summary

Milestone 2 was about teaching rather than building. Roughly a thousand lines
of curriculum were written by hand to replace generated material, the first
three days were rebuilt on a proper model of how Python variables work, and
every lesson in the system now asks the student a question before it shows them
the answer. A student working through PySchool today is reading material
written for them, and is being made to think before they are allowed to move
on.



