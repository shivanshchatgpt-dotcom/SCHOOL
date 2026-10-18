"""Bridge between the local book corpus and the seeding layer.

``seed.py`` must not know where the corpus lives or how a canonical topic is
composed. This module is the only thing it imports, and it answers one
question: which composed lessons are available right now?

The corpus (``.books/``) sits outside the backend package because it is local
reference material, so its directory is put on ``sys.path`` here rather than
packaged. If the corpus is absent, composing is impossible and this raises an
explicit error instead of quietly returning an empty curriculum.
"""
from __future__ import annotations

import sys
from pathlib import Path

# backend/app/canonical_topics_proxy.py -> app -> backend -> SCHOOL -> .books
_BOOKS = Path(__file__).resolve().parent.parent.parent / ".books"
if str(_BOOKS) not in sys.path:
    sys.path.insert(0, str(_BOOKS))

from canonical_topics import all_topics  # noqa: E402

from .lesson_composer import compose_all  # noqa: E402


def composed_lessons() -> list[dict]:
    """Every lesson the canonical library can currently compose, in stable order.

    Order is by topic id then path slug, so two runs over the same corpus
    produce the same lesson list and the same database rows.
    """
    return [lesson for topic_id in sorted(all_topics()) for lesson in compose_all(topic_id)]


def provenance_report() -> list[dict]:
    """One row per composed lesson: where its content comes from."""
    return [
        {
            "path": lesson["path"],
            "day": lesson["day"],
            "title": lesson["title"],
            "canonical_topic": lesson["canonical_topic"],
            "coverage": lesson["coverage"],
            "sources": lesson["provenance"],
        }
        for lesson in composed_lessons()
    ]
