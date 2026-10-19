"""Flagship Computer Vision curriculum: hand-authored days 9-14 and 75-179.

Days 1-8 keep the canonical pixel-and-annotation lessons, days 9-14 are the
authored foundation arc, days 15-74 are the shared authored Python phases
(preserved), and days 75-179 are seven domain phases written for this track.
Every worked example is stdlib-only and runs offline: images are nested lists,
filters are loops, and masks are inspectable data, so no lesson needs OpenCV,
torchvision or an image file.

Each phase entry is ``(name, goal, {day: day_dict})``. A day dict carries the
topic, the idea in plain language, runnable code, two variants, three common
mistakes, one lesson-specific Q&A, a named-function homework task, the patterns
that homework must contain, and the real-world mapping.
"""

from __future__ import annotations

from .cv_phases.foundation import FOUNDATION
from .cv_phases import phase1, phase2, phase3, phase4, phase5, phase6, phase7

DOMAIN = "Computer Vision"

PHASES = [
    phase1.PHASE,
    phase2.PHASE,
    phase3.PHASE,
    phase4.PHASE,
    phase5.PHASE,
    phase6.PHASE,
    phase7.PHASE,
]
