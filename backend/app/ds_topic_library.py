"""Authored Data Science track content (Days 15–179).

Every topic in TRACK_180_PHASES["data-science"] gets fully authored theory,
a runnable worked example, layered questions with answers, and homework —
the same quality bar as COMMON_TOPIC_LIBRARY. Keys must match the topic
strings in seed_data.TRACK_180_PHASES exactly.
"""

DS_TOPIC_LIBRARY: dict[str, dict] = {}

def _t(topic, theory, code, questions, answers, homework):
    DS_TOPIC_LIBRARY[topic] = {
        "theory": theory, "code": code,
        "questions": questions, "answers": answers, "homework": homework,
    }

from .ds_topics_phase1_2 import PHASE_1_2  # noqa: E402
from .ds_topics_phase3 import PHASE_3_TO_7  # noqa: E402
from .ds_topics_phase4 import PHASE_4  # noqa: E402
from .ds_topics_phase5 import PHASE_5  # noqa: E402
from .ds_topics_phase6_7 import PHASE_6_7  # noqa: E402

DS_TOPIC_LIBRARY.update(PHASE_1_2)
DS_TOPIC_LIBRARY.update(PHASE_3_TO_7)
DS_TOPIC_LIBRARY.update(PHASE_4)
DS_TOPIC_LIBRARY.update(PHASE_5)
DS_TOPIC_LIBRARY.update(PHASE_6_7)
