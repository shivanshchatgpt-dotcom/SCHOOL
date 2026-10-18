"""Curriculum day scheduler.

Given a path's block layout, decide for every day what it should be. Two things
are decided here and nowhere else:

* which days become generated practice, because the canonical library already
  has an exercise template for that block's skill;
* where review checkpoints sit, because a review is only meaningful at a point
  where the material actually turns over. Review days are therefore placed by
  this schedule at block boundaries and never chosen by the generator.

The scheduler is pure: it returns a plan and writes nothing. Turning a plan into
rows is a separate, explicit step, so a plan can be reviewed before it touches
the database.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable

from app.exercise_templates import TEMPLATES
from app.exercise_gen import ExerciseTemplate

# The three launch tracks share one layout. Each block is 15 days from d15, with
# a 14-day foundation opening and a single closing reflection day.
FOUNDATION = (1, 14)
CLOSING = 180
BLOCKS: tuple[tuple[str, int, int], ...] = (
    ("Core Python", 15, 29),
    ("Practical Python", 30, 44),
    ("Software Engineering", 45, 59),
    ("Algorithms and Math", 60, 74),
    ("Data Workflow", 75, 89),
    ("Statistics", 90, 104),
    ("Visualization", 105, 119),
    ("Predictive Modelling", 120, 134),
    ("Evaluation and Deployment", 135, 149),
    ("Applied Projects", 150, 164),
    ("Capstone", 165, 179),
)

# Which block each exercise template belongs to, keyed by template block name.
TEMPLATES_BY_BLOCK: dict[str, list[ExerciseTemplate]] = {}
for _t in TEMPLATES:
    TEMPLATES_BY_BLOCK.setdefault(_t.block, []).append(_t)

# Block name to canonical block label, so a template written for one track can
# serve another track whose block carries a different label.
BLOCK_ALIASES = {
    "Core Python": "Core Python",
    "Practical Python": "Practical Python",
    "Software Engineering": "Software Engineering",
    "Algorithms and Math": "Algorithms and Math",
    "Data Workflow": "Data Workflow",
    "Statistics": "Statistics",
    "Visualization": "Visualization",
    "Predictive Modelling": "Predictive Modelling",
    "Evaluation and Deployment": "Evaluation and Deployment",
}


@dataclass(frozen=True)
class DayPlan:
    day: int
    block: str
    day_type: str          # concept | practice | project | review
    source: str            # authored | generator | schedule
    template_id: str = ""
    note: str = ""


def block_of(day: int) -> str:
    if day <= FOUNDATION[1]:
        return "Foundation"
    if day == CLOSING:
        return "Closing"
    for name, lo, hi in BLOCKS:
        if lo <= day <= hi:
            return name
    return "Unknown"


def review_days() -> list[int]:
    """Review checkpoints, one at the end of every block.

    A block boundary is the only place a checkpoint is worth anything, so this is
    derived from the block layout rather than chosen. The closing day also gets
    one, which makes the count 12 boundaries plus the close.
    """
    return [hi for _n, _lo, hi in BLOCKS] + [CLOSING]


def project_days() -> list[int]:
    """Days already authored as build prompts, by the block layout's own naming.

    This is only a starting point for planning; the authoritative signal is the
    stored title, which `audit` uses.
    """
    return []


def plan_path(slug: str, *, practice_share: float = 0.5) -> list[DayPlan]:
    """Plan one path's 180 days.

    practice_share is the fraction of each block's non-project days that should
    become generated practice. The remainder stay concept days, because the
    generator can only supply exercises for skills a template already covers and
    the rest genuinely need a written body.
    """
    reviews = set(review_days())
    plans: list[DayPlan] = []

    for name, lo, hi in BLOCKS:
        aliases = [name, BLOCK_ALIASES.get(name, name)]
        pool: list[ExerciseTemplate] = []
        for a in aliases:
            pool.extend(TEMPLATES_BY_BLOCK.get(a, []))
        span = hi - lo + 1
        # Reserve the last day of the block for the checkpoint, so it is never
        # double-booked as practice.
        practice_days = [d for d in range(lo, hi + 1) if d not in reviews]
        n_practice = int(round(span * practice_share))
        if pool:
            n_practice = min(n_practice, len(practice_days))
        else:
            n_practice = 0
        # Spread practice evenly through the block rather than bunching it at
        # the front, so the block alternates teaching and drilling.
        chosen: set[int] = set()
        if n_practice and practice_days:
            step = len(practice_days) / n_practice
            for i in range(n_practice):
                chosen.add(practice_days[min(len(practice_days) - 1, int(i * step))])

        for day in range(lo, hi + 1):
            if day in reviews:
                plans.append(DayPlan(day, name, "review", "schedule",
                                     note="block checkpoint"))
            elif day in chosen and pool:
                tpl = pool[(day - lo) % len(pool)]
                plans.append(DayPlan(day, name, "practice", "generator",
                                     template_id=tpl.id, note=tpl.skill))
            else:
                plans.append(DayPlan(day, name, "concept", "authored",
                                     note="needs authored body"))
    return plans


def summarise(plans: Iterable[DayPlan]) -> dict[str, int]:
    out: dict[str, int] = {}
    for p in plans:
        out[p.day_type] = out.get(p.day_type, 0) + 1
    return out


if __name__ == "__main__":
    for slug in ("agi-research", "data-science", "web-dev"):
        plans = plan_path(slug)
        s = summarise(plans)
        print(f"{slug:<16} " + " ".join(f"{k}={v}" for k, v in sorted(s.items())))
    print()
    print("review days:", review_days())
    print("blocks with templates:", sorted(TEMPLATES_BY_BLOCK))
