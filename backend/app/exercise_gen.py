"""Parameterised exercise generator.

The existing practice days are shells: a topic name is slotted into a fixed
sentence, and the code that ships with the day is often unrelated to that topic.
This module replaces that with real exercises.

An exercise template names a skill, a pool of values to draw from, a prompt, and
a reference solution. Asking for N variants samples the pools, renders both the
student prompt and the reference solution from the same draw, and then executes
every solution to confirm it runs and prints what the prompt claims it will.
A template that cannot produce a working solution is a bug, and the generator
refuses to emit it.

Everything is deterministic given a seed, so a batch can be regenerated
identically and diffed. Solutions use only the standard library, matching the
convention the rest of the corpus already follows, so a student can run a
generated exercise without installing anything.
"""
from __future__ import annotations

import random
import re
import sys
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ExerciseTemplate:
    """One parameterised exercise, renderable into many concrete variants."""

    id: str
    skill: str
    block: str
    prompt: str
    solution: str
    required_patterns: tuple[str, ...]
    rubric: tuple[str, ...]
    params: dict[str, tuple[Any, ...]] = field(default_factory=dict)
    # Substrings the solution's stdout must contain for the variant to pass.
    expect: tuple[str, ...] = ()
    n_variants: int = 4
    day_type: str = "practice"
    # The curriculum day this exercise belongs to. The four shared blocks are
    # byte-identical across the launch paths, so one template keyed by day fills
    # the same day in every path rather than needing a copy per path.
    day: int = 0

    def pool_sizes(self) -> dict[str, int]:
        return {k: len(v) for k, v in self.params.items()}

    def capacity(self) -> int:
        n = 1
        for values in self.params.values():
            n *= len(values)
        return n


@dataclass(frozen=True)
class Variant:
    """One concrete exercise instance produced from a template."""

    template_id: str
    skill: str
    block: str
    day_type: str
    index: int
    draw: dict[str, Any]
    prompt: str
    solution: str
    required_patterns: tuple[str, ...]
    rubric: tuple[str, ...]
    stdout: str

    def to_assignment(self) -> dict[str, Any]:
        """Shape the existing assignments table expects."""
        return {
            "prompt": self.prompt,
            "required_patterns": list(self.required_patterns),
            "min_lines": 4,
            "rubric": " ".join(self.rubric),
        }

    def to_lesson(self, *, path: str, day: int, domain: str) -> dict[str, Any]:
        """Shape the existing lessons table expects.

        A generated practice day carries no new teaching, so its theory is a
        short orientation note rather than a full body. The weight sits in the
        assignment the student actually has to do.
        """
        lines = [
            f"**Today: {self.skill}**",
            "",
            f"This is a practice day. You are not learning a new concept here; you are "
            f"building fluency with **{self.skill}** inside the **{self.block}** block "
            f"of the {domain} programme.",
            "",
            "**What to do**",
            "1. Read the prompt below and predict the output before writing anything.",
            "2. Write the solution yourself. Do not copy the reference.",
            "3. Run it, compare against the stated expected output, then change one "
            "   value and predict the new result before running again.",
            "4. Your submission is checked for the required constructs and for the "
            "   output it produces, not for matching the reference text.",
            "",
            "**Why practise this here**",
            f"{self.skill} is used repeatedly in the {self.block} block that follows. "
            "Doing it here while the idea is fresh is much cheaper than meeting it for "
            "the first time under deadline.",
        ]
        return {
            "path": path,
            "day": day,
            "title": f"Practice: {self.skill}",
            "domain": domain,
            "objective": f"Apply {self.skill} to a {self.block.lower()} problem and verify the result.",
            "theory": "\n".join(lines),
            "code_example": self.solution,
            "questions": [
                f"What does {self.skill} give you that writing the logic by hand would not?",
                "Which line in your solution is doing the real work, and why?",
                "What breaks if the input collection is empty?",
            ],
            "answers": [
                f"{self.skill} is a repeatable, testable shape for this kind of problem, so it survives being reused on larger data without rewriting the logic.",
                "The line that transforms the input into the value you return, because that is the only step that encodes the specific rule; everything around it is plumbing.",
                "Most implementations raise or return an empty result rather than crashing, because an empty input is a normal condition rather than a bug, and it should be handled deliberately.",
            ],
            "homework": self.prompt,
            "required_patterns": list(self.required_patterns),
            "day_type": self.day_type,
            "template_id": self.template_id,
        }


class ExecutionError(RuntimeError):
    pass


PLACEHOLDER = re.compile(r"<<(\w+)>>")


def _render(template: str, draw: dict[str, Any]) -> str:
    """Substitute <<name>> placeholders from draw.

    Angle-bracket delimiters are used deliberately. Solutions contain real Python
    f-strings, so brace-delimited placeholders would collide with the code being
    substituted into and the "did everything render" check would produce false
    failures on legitimate code.
    """
    missing: set[str] = set()

    def sub(m: re.Match[str]) -> str:
        key = m.group(1)
        if key not in draw:
            missing.add(key)
            return m.group(0)
        return str(draw[key])

    out = PLACEHOLDER.sub(sub, template)
    if missing:
        raise ExecutionError(f"no value drawn for {sorted(missing)}")
    return out


def _exec_solution(solution: str, label: str) -> str:
    """Run a solution and return its stdout. Raises on any failure."""
    import io
    from contextlib import redirect_stdout

    buf = io.StringIO()
    try:
        with redirect_stdout(buf):
            exec(compile(solution, f"<exercise:{label}>", "exec"), {"__name__": "__main__"})
    except Exception as err:  # noqa: BLE001 - the point is to report any failure
        raise ExecutionError(f"{label}: {type(err).__name__}: {err}") from err
    return buf.getvalue()


def generate(template: ExerciseTemplate, *, seed: int, n: int | None = None) -> list[Variant]:
    """Produce n validated variants of one template.

    Each variant draws a fresh value per parameter, renders prompt and solution
    from that same draw, and executes the solution. A variant whose output does
    not contain every expected substring is a template bug and is rejected.
    """
    want = n if n is not None else template.n_variants
    # Distinct variants are bounded by the product of the parameter pools, so
    # check that up front rather than discovering it after a long retry loop.
    capacity = 1
    for values in template.params.values():
        capacity *= len(values)
    if want > capacity:
        raise ExecutionError(
            f"{template.id}: asked for {want} variants but the parameter pools can "
            f"only produce {capacity} ({template.pool_sizes()}); widen a pool or "
            f"lower n_variants"
        )
    rng = random.Random(f"{seed}:{template.id}")
    variants: list[Variant] = []
    seen: set[tuple] = set()

    attempts = 0
    while len(variants) < want and attempts < want * 20:
        attempts += 1
        draw = {k: rng.choice(list(v)) for k, v in template.params.items()}
        if draw and tuple(sorted(draw.items())) in seen:
            continue
        seen.add(tuple(sorted(draw.items())))

        prompt = _render(template.prompt, draw)
        solution = _render(template.solution, draw)
        label = f"{template.id}#{len(variants) + 1}"
        stdout = _exec_solution(solution, label)
        for needle in template.expect:
            if needle not in stdout:
                raise ExecutionError(
                    f"{label}: output missing {needle!r}\n--- got ---\n{stdout}"
                )
        variants.append(
            Variant(
                template_id=template.id,
                skill=template.skill,
                block=template.block,
                day_type=template.day_type,
                index=len(variants) + 1,
                draw=draw,
                prompt=prompt,
                solution=solution,
                required_patterns=template.required_patterns,
                rubric=template.rubric,
                stdout=stdout,
            )
        )
    if len(variants) < want:
        raise ExecutionError(
            f"{template.id}: only produced {len(variants)}/{want} distinct variants; "
            f"widen the parameter pools ({template.pool_sizes()})"
        )
    return variants


def render_exercise_body(variants: list[Variant]) -> str:
    """A short displayed example for the lesson body.

    The first variant's solution is shown, because a practice day should still
    demonstrate the shape being practised even though it teaches nothing new.
    """
    head = variants[0]
    lines = [
        f"**Worked shape: {head.skill}**",
        "",
        "This is the reference for the exercise below. Write your own version rather",
        "than copying it, then compare outputs.",
        "",
        "```python",
        head.solution.rstrip(),
        "```",
        "",
        "Running it prints:",
        "",
        "```",
        head.stdout.rstrip(),
        "```",
    ]
    return "\n".join(lines)


def review_body(block: str, covered: list[str], variant_ids: list[str]) -> str:
    """Body for a scheduled review checkpoint.

    Review days are placed by the curriculum schedule at block boundaries, never
    chosen by the generator, because a checkpoint only means something if it
    lands where the material actually turns over.
    """
    items = "\n".join(f"{i}. {s}" for i, s in enumerate(covered, 1))
    lines = [
        f"**Block review: {block}**",
        "",
        f"You have finished the **{block}** block. This day exists to consolidate it",
        "before new material arrives, so it contains no new teaching.",
        "",
        "**What the block covered**",
        items,
        "",
        "**How to use this day**",
        "1. Without notes, write one sentence per item above explaining it in your",
        "   own words. Anything you cannot write is what to re-read.",
        "2. Re-run each of the day's exercises with a different input and predict the",
        "   output before executing.",
        "3. Mark each item red, amber or green. Red means re-read that day; amber",
        "   means you can explain it but could not write the code unaided; green",
        "   means you can do both.",
        "4. Carry the red and amber items into the next block. Do not let them",
        "   accumulate silently.",
        "",
        f"**Exercises in this set** ({len(variant_ids)}): " + ", ".join(variant_ids),
    ]
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    """Validate every registered template without touching the database."""
    from app.exercise_templates import TEMPLATES

    seed = 20260927
    total = 0
    failures: list[str] = []
    for t in TEMPLATES:
        try:
            vs = generate(t, seed=seed)
        except ExecutionError as err:
            failures.append(str(err))
            print(f"  FAIL {t.id}: {err}")
            continue
        total += len(vs)
        print(f"  ok   {t.id:<38} {len(vs)} variants  skill={t.skill[:34]}")
    print(f"\n{total} variants generated, {len(failures)} templates failed")
    if failures:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
