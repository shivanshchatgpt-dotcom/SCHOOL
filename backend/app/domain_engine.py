"""Reusable domain-aware curriculum engine for catalog batches.

A DomainPack carries explicit path knowledge (domain, subdomains, concepts,
tools, workflows, project types, mistakes, assessment patterns, career
context, phase sequence). build_lesson() composes a DB-ready lesson from one
day-spec; the spec's topic-specific fields (idea/detail/tradeoff/code/qa/...)
are what make lessons genuinely different -- the composer never invents
domain content, it only assembles it.

Quality gates extend the flagship pattern (450-900 theory words, 3 Q&As,
runnable example, homework>=120 chars, no placeholders, unique titles) with
uniqueness enforcement: generic question/homework stems are rejected and
pairwise Jaccard similarity above threshold fails validation.
"""
from __future__ import annotations

import ast
import contextlib
import io
import re
import signal
from dataclasses import dataclass, field

MIN_THEORY_WORDS = 450
MAX_THEORY_WORDS = 900

# Stems that indicate filler rather than lesson-specific assessment.
BANNED_Q_FRAGMENTS = (
    "what is the main topic",
    "which statement best describes",
    "what did you learn today",
    "practice what you learned",
    "submit your work",
)
BANNED_HW_FRAGMENTS = (
    "practice what you learned and submit your work",
    "write code related to today's topic",
)
PLACEHOLDER_TOKENS = ("__LIB__", "__DOMAIN__", "{lib}", "{name}", "TODO", "lorem")
NON_LATIN = re.compile(r"[Ѐ-џͰ-Ͽ一-鿿]")

_STOPWORDS = set(
    "about above after again against among because been before being below between both during "
    "each either even every from further have having into itself more most must often only other "
    "ought same should since such than that then there these they this those through under until "
    "what when where which while with within without would your today lesson topic learn learned "
    "work worked example reference write your own version rather copying compare outputs output "
    "running prints turn variants each same problem different values value happens work first proof "
    "second predict before adapt print result common mistakes going further inside larger practice "
    "task week notice where idea strains next study protocol minutes read change exactly either way "
    "scratch while explaining choices comments summary matters because remember core trade going "
    "small testable python explain apply domain objective theory code questions answers homework "
    "patterns required today turn variant common going going".split()
)


def _words(text: str) -> int:
    return len(re.findall(r"\b[\w'-]+\b", text or ""))


def run_code(code: str) -> str:
    """Execute a lesson example, capture stdout. Raises on failure/silence."""

    def _timeout(_signum, _frame):
        raise TimeoutError("example did not finish in time")

    buf = io.StringIO()
    previous = signal.signal(signal.SIGALRM, _timeout)
    signal.alarm(10)
    try:
        with contextlib.redirect_stdout(buf):
            exec(compile(code, "<catalog-example>", "exec"), {"__name__": "__catalog_example__"})
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, previous)
    out = buf.getvalue().strip()
    if not out:
        raise ValueError("example runs silently")
    return out


@dataclass
class DomainPack:
    slug: str
    domain: str
    career: str
    phases: list = field(default_factory=list)  # (phase, goal, {day: spec})
    foundation: dict = field(default_factory=dict)  # {day: spec}


def _spec_words(spec: dict) -> str:
    return " ".join([
        spec["topic"], spec["idea"], spec["detail"], spec["tradeoff"],
        " ".join(spec["mistakes"]), spec["mapping"],
        " ".join(spec["qa"][0]), " ".join(spec["qa"][1]),
        spec["homework"], spec["variant_b"], spec["variant_c"],
    ])


def jaccard(a: str, b: str) -> float:
    ta = set(re.findall(r"[a-z]{3,}", a.lower()))
    tb = set(re.findall(r"[a-z]{3,}", b.lower()))
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / len(ta | tb)


def build_lesson(pack: DomainPack, phase: str, spec: dict) -> dict:
    """Compose the DB-ready lesson dict. Example output is captured, not written."""
    output = run_code(spec["code"])
    questions, answers = spec["qa"]
    title = spec["topic"] if not phase else f"{phase}: {spec['topic']}"
    theory = "\n".join([
        f"**Today: {spec['topic']}**",
        "",
        spec["idea"],
        "",
        "**Why it matters**",
        f"As a {pack.career}, you meet {spec['topic']} whenever {spec['mapping'].lower()} "
        f"Concretely: {spec['detail']}",
        "",
        "**How it works**",
        spec["tradeoff"],
        "",
        "**Worked example**",
        "This is the reference. Write your own version rather than copying it, then compare outputs.",
        "",
        "```python",
        spec["code"],
        "```",
        "",
        "Running it prints:",
        "",
        "```",
        output,
        "```",
        "",
        "**Your turn — two variants**",
        "Each one is the same problem with different values, so a value that happens to work in the first is not proof the second will. Predict each output before running it.",
        "",
        f"**Variant 1** — {spec['variant_b']}",
        "Adapt the worked example to these values and print the result.",
        "",
        f"**Variant 2** — {spec['variant_c']}",
        "Adapt the worked example to these values and print the result.",
        "",
        "**Common mistakes**",
        *[f"- {m}" for m in spec["mistakes"]],
        "",
        "**Going further**",
        f"Use {spec['topic']} inside a larger {pack.domain} practice task this week, and notice where the idea strains. That strain is the map of what to learn next.",
        "Write down one input that would break a naive implementation and keep it as your personal regression case for the week.",
        "",
        "**Study protocol (60 minutes)**",
        "1. Read the worked example and predict its output before running it.",
        "2. Change exactly one value and predict again — either way you learn.",
        "3. Write today's practice from scratch while explaining choices in comments.",
        "4. Explain the fix for the most likely mistake to a peer (or a rubber duck) before submitting.",
        "",
        "**Summary**",
        f"{spec['topic']} matters because {spec['mapping'].lower()} "
        f"Remember the core idea ({spec['idea'].split('.')[0].lower()}) and the trade-off ({spec['tradeoff'].split('.')[0].lower()}).",
    ])
    return {
        "title": title,
        "domain": pack.domain,
        "objective": f"Explain and apply {spec['topic']} for {pack.domain} in a small, testable Python example.",
        "theory": theory,
        "code_example": spec["code"],
        "questions": list(questions),
        "answers": list(answers),
        "homework": spec["homework"],
        "required_patterns": list(spec["patterns"]),
    }


def validate_lesson(lesson: dict) -> None:
    required = {"title", "domain", "objective", "theory", "code_example", "questions",
                "answers", "homework", "required_patterns"}
    missing = required - lesson.keys()
    if missing:
        raise ValueError(f"missing fields: {sorted(missing)}")
    if len(lesson["questions"]) != 3 or len(lesson["answers"]) != 3:
        raise ValueError("exactly 3 questions and 3 answers required")
    words = _words(lesson["theory"])
    if not MIN_THEORY_WORDS <= words <= MAX_THEORY_WORDS:
        raise ValueError(f"theory has {words} words, expected {MIN_THEORY_WORDS}-{MAX_THEORY_WORDS}")
    ast.parse(lesson["code_example"])
    if len(lesson["homework"]) < 120:
        raise ValueError("homework is too short")
    if not lesson["required_patterns"] or not all(isinstance(p, str) and p for p in lesson["required_patterns"]):
        raise ValueError("required_patterns must be non-empty strings")
    # Template-leftover scan runs on prose only (fenced code/output blocks
    # removed): braces inside f-strings are working interpolation, proven by
    # execution, while "{name}"-style tokens in explanatory prose are filler.
    prose = re.sub(r"```.*?```", "", lesson["theory"], flags=re.S)
    for token in PLACEHOLDER_TOKENS:
        if token in prose:
            raise ValueError(f"placeholder token leaked: {token}")
    # In code, {name}/{lib}-style braces are legitimate f-string interpolation
    # (executed, so undefined names fail loudly); only template-style sentinels
    # and TODO/lorem are rejected there.
    for token in ("__LIB__", "__DOMAIN__", "TODO", "lorem"):
        if token in lesson["code_example"]:
            raise ValueError(f"placeholder token leaked: {token}")
    if NON_LATIN.search(lesson["theory"]):
        raise ValueError("unexpected non-Latin script in theory")
    qtext = " ".join(lesson["questions"]).lower()
    for frag in BANNED_Q_FRAGMENTS:
        if frag in qtext:
            raise ValueError(f"banned generic question stem: {frag}")
    hw = lesson["homework"].lower()
    for frag in BANNED_HW_FRAGMENTS:
        if frag in hw:
            raise ValueError(f"banned generic homework: {frag}")
    # questions must reference the lesson: at least two of three share a
    # distinctive word with the lesson's own vocabulary (title/objective/theory
    # minus common English and minus the composer's fixed boilerplate). Banned
    # generic stems are rejected separately above; pairwise similarity below.
    vocab = set(re.findall(r"[a-z]{4,}", (lesson["title"] + " " + lesson["objective"] + " " + lesson["theory"]).lower())) - _STOPWORDS
    hits = sum(1 for q in lesson["questions"]
               if vocab & set(re.findall(r"[a-z]{4,}", q.lower())))
    if hits < 2:
        raise ValueError("questions do not reference the lesson topic")


def collect_pack(pack: DomainPack) -> list:
    """All owned days as (day_number, phase, built lesson). Validates everything."""
    out = []
    for day_num, spec in sorted(pack.foundation.items()):
        lesson = build_lesson(pack, "", spec)
        lesson["title"] = spec["topic"]
        validate_lesson(lesson)
        out.append((day_num, "Foundations", lesson))
    for phase, _goal, days in pack.phases:
        for day_num, spec in sorted(days.items()):
            lesson = build_lesson(pack, phase, spec)
            validate_lesson(lesson)
            out.append((day_num, phase, lesson))
    titles = [lesson["title"] for _, _, lesson in out]
    if len(set(titles)) != len(titles):
        dupes = sorted({t for t in titles if titles.count(t) > 1})
        raise ValueError(f"duplicate titles: {dupes}")
    # Pairwise uniqueness: reject mass-substitution (thresholds catch >~60% overlap).
    qs = [" | ".join(l["questions"]) for _, _, l in out]
    for i in range(len(qs)):
        for j in range(i + 1, len(qs)):
            if jaccard(qs[i], qs[j]) > 0.62:
                raise ValueError(f"questions too similar: days {out[i][0]} and {out[j][0]}")
    hws = [l["homework"] for _, _, l in out]
    for i in range(len(hws)):
        for j in range(i + 1, len(hws)):
            if jaccard(hws[i], hws[j]) > 0.62:
                raise ValueError(f"homework too similar: days {out[i][0]} and {out[j][0]}")
    return out
