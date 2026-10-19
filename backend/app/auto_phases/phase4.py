"""Pipelines and task orchestration, days 120-134: many steps, one goal.

Every example is stdlib-only, offline and deterministic. Run graphs are plain
dicts and lists, ordering uses Kahn's algorithm with explicit loops, and
retries, timeouts and checkpoints are modelled as data counted by integers. No
threads, clocks, files or network are involved, so a pipeline can be planned,
run, resumed and asserted on in memory.
"""

PHASE = ("Pipelines and Task Orchestration", "Compose dependent steps into an ordered, observable run that can be retried, resumed and reviewed.", {
    120: dict(
        topic="Orientation: many steps, one goal",
        idea=(
            "An automation rarely fails because a single step is hard; it fails because many small steps lose "
            "sight of the goal they were assembled to serve. Pipeline thinking starts by naming that goal in one "
            "sentence, then listing the steps that exist only to move data toward it. Each step should have a "
            "narrow job, a clear input, a clear output and a reason to be there. When you can read the list of "
            "steps and see how each one shortens the distance to the goal, you have a design rather than a pile "
            "of scripts. This orientation matters because orchestration tools will happily run any graph you give "
            "them, including a graph that computes the wrong thing efficiently. A useful habit is to write the "
            "goal at the top of the file and name steps as verbs: fetch, clean, validate, load, report. Verbs "
            "make gaps obvious, because a missing verb is easier to notice than a missing function. Today you "
            "build a tiny run plan as a list of step dictionaries, print it in order, and assert that the last "
            "step is the one that produces the goal. No scheduling or failure handling yet; the point is to see "
            "the whole job as data before adding machinery. Everything in this phase adds one property to this "
            "same shape: ordering, data flow, parallelism, resumption and observability."
        ),
        code=(
            'steps = [\n'
            '    {"name": "fetch", "goal": "collect raw rows"},\n'
            '    {"name": "clean", "goal": "drop blank rows"},\n'
            '    {"name": "report", "goal": "publish the daily summary"},\n'
            ']\n'
            '\n'
            'print("goal: publish a trustworthy daily report")\n'
            'for index, step in enumerate(steps, start=1):\n'
            '    print(f"{index}. {step[\'name\']:6} -> {step[\'goal\']}")\n'
            '\n'
            'assert len(steps) == 3\n'
            'assert steps[-1]["name"] == "report"\n'
            'print("many steps, one goal: every step serves the final object")'
        ),
        variant_b='add a "notify" step after report and decide whether it serves the goal or is a side quest',
        variant_c='rename the steps with weaker verbs and see which gaps in the flow become harder to notice',
        mistakes=[
            "Collecting steps with no stated goal, so every addition feels justified on its own.",
            "Naming steps after tools rather than verbs, which hides missing stages in the flow.",
            "Designing for a goal that no single step actually produces at the end.",
        ],
        q1=(
            "Why state the pipeline goal before listing its steps?",
            "It gives every step a test for relevance, so the graph stays minimal and the final step has a clear contract.",
        ),
        homework=(
            "Write `plan_steps(goal, steps)` that returns a list of step dictionaries and prints each step with "
            "its index, then asserts the last step produces the goal. Call it with three steps and print the "
            "goal line, and comment which assertion ties the plan back to the goal."
        ),
        patterns=["def plan_steps", "for ", "assert "],
        mapping=(
            "Airflow and Dagster both start from a DAG whose purpose is documented at the top; a clear goal is "
            "what stops a workflow from becoming a junk drawer of tasks."
        ),
    ),
    121: dict(
        topic="Steps as state transforms",
        idea=(
            "The most testable pipeline design treats every step as a pure function: it receives the current "
            "state and returns a new state, leaving the old one untouched. That single rule buys a lot. You can "
            "run any step against a fixture, compare the before and after values, and know exactly what it "
            "changed. You can also replay a run by feeding recorded states back through the steps. The "
            "alternative, steps that mutate a shared dictionary or write files in place, couples every step to "
            "everything that ran before it and makes failures hard to localise. Pure transforms also make the "
            "data flow explicit, because the keys a step reads and the keys it writes are visible in its body. "
            "When a key is missing, the failure happens at the boundary of that step rather than three steps "
            "later. In real systems you eventually need side effects, writing a table or sending a message, so "
            "the usual compromise is to keep the computation pure and push the effect to the edge of the step, "
            "recording what it did in the returned state. Today you build two transforms over a state dictionary, "
            "print the state after each, and assert the final value. Notice that the runner is a plain loop; "
            "ordering, retries and logging all wrap this loop later without changing the shape of the steps."
        ),
        code=(
            'def add_rows(state):\n'
            '    return {**state, "rows": state["rows"] + [" a ", "b"], "stage": "added"}\n'
            '\n'
            'def normalise(state):\n'
            '    rows = [row.strip().upper() for row in state["rows"]]\n'
            '    return {**state, "rows": rows, "stage": "normalised"}\n'
            '\n'
            'state = {"rows": [], "stage": "new"}\n'
            'for step in (add_rows, normalise):\n'
            '    before = state["stage"]\n'
            '    state = step(state)\n'
            '    print(f"{before:9} -> {state}")\n'
            '\n'
            'assert state["rows"] == ["A", "B"]\n'
            'assert state["stage"] == "normalised"\n'
            'print("a step is a function from state to a new state")'
        ),
        variant_b='add a transform that deduplicates rows and print the state after each of the three steps',
        variant_c='return a copy with a "changed" boolean and assert that every step reports False on a no-op input',
        mistakes=[
            "Mutating the incoming state in place, so the before and after values can no longer be compared.",
            "Letting a step read keys it did not declare, which breaks when an earlier step is reordered.",
            "Mixing side effects into the transform, so tests need a disk or a network to observe the result.",
        ],
        q1=(
            "What does a step return if it is written as a state transform?",
            "A new state value containing the changes, while the input state is left untouched and remains inspectable.",
        ),
        homework=(
            "Write `apply_steps(steps, state)` that applies state-to-state functions in order and returns the "
            "final state. Add `add_rows` and `normalise` transforms, print each intermediate state, and comment "
            "which line guarantees the input state is not mutated."
        ),
        patterns=["def apply_steps", "return {**", "print("],
        mapping=(
            "Dagster ops and Airflow task functions are usually written as data-in, data-out calls; keeping them "
            "pure is what lets the orchestrator retry or replay them safely."
        ),
    ),
    122: dict(
        topic="Passing data between steps",
        idea=(
            "Once steps are transforms, the next question is what exactly travels between them. A pipeline is a "
            "series of handoffs, and every handoff is a contract: this step promises those keys, and the next "
            "step may rely on them. Writing those promises down, even as a small note or a dictionary of "
            "expected keys, prevents a class of bugs where a rename in one step silently breaks a consumer. The "
            "common failure is a step returning only the new value and dropping the context that later steps "
            "need, so the data either disappears or has to be fetched again. The lazy and robust pattern is to "
            "return the accumulated state, updating only the keys the step owns. That keeps each contract "
            "additive: a step adds or replaces its own keys and passes the rest through. It also keeps the "
            "handoff visible when you print the state between steps. In larger systems the payload may be a file "
            "path, a table name or a message id rather than the data itself, but the contract idea is identical. "
            "Today you build three steps that pass a dictionary along, print the keys each step produces, and "
            "assert that the final consumer can read what it needs. Watch how each step reads only the keys the "
            "previous one guarantees."
        ),
        code=(
            'def extract(data):\n'
            '    return {"rows": ["x", "y"], "count": 2}\n'
            '\n'
            'def transform(data):\n'
            '    return {"rows": [row.upper() for row in data["rows"]], "count": data["count"]}\n'
            '\n'
            'def load(data):\n'
            '    return {"written": data["rows"], "total": data["count"]}\n'
            '\n'
            'data = {}\n'
            'for step in (extract, transform, load):\n'
            '    data = step(data)\n'
            '    print(step.__name__, "produced", sorted(data))\n'
            '\n'
            'print("final:", data)\n'
            'assert data["total"] == 2 and data["written"] == ["X", "Y"]\n'
            'print("each step reads the keys the previous step guarantees")'
        ),
        variant_b='make transform preserve an extra "source" key and print it after load to prove it survived',
        variant_c='drop "count" from extract and watch the failure move to the step that first needs it',
        mistakes=[
            "Returning only the newly computed value, so context needed later disappears at the boundary.",
            "Renaming a key in one step without checking every consumer of that key.",
            "Passing large objects between steps when a stable reference or summary would do.",
        ],
        q1=(
            "What should a step return so the next step still has everything it needs?",
            "The accumulated state with the step's own keys updated, so earlier context passes through unchanged.",
        ),
        homework=(
            "Write `handoff(steps, data)` that runs each step over a shared dictionary and returns the "
            "accumulated state. Build `extract`, `transform` and `load` so each adds its own keys, print the "
            "keys after every step, and comment which line keeps older keys alive."
        ),
        patterns=["def handoff", "{**", "print("],
        mapping=(
            "XCom in Airflow and metadata passing in Dagster are explicit versions of this contract; small "
            "payloads and stable references age better than large serialised objects."
        ),
    ),
    123: dict(
        topic="Dependency ordering and toposort",
        idea=(
            "A list of steps is only enough while the pipeline is linear. As soon as two branches feed a join, "
            "the real information is the dependency graph: which steps must finish before which others may "
            "start. A topological sort turns that graph into a runnable order where every dependency appears "
            "before its dependant. Kahn's algorithm is the simplest version and needs no recursion: repeatedly "
            "take every node whose dependencies are already satisfied, append it to the order, remove it from "
            "the graph, and repeat. If a pass finds nothing ready while nodes remain, the graph has a cycle and "
            "no valid order exists, which is exactly the error a scheduler should raise instead of looping "
            "forever. Sorting the ready set each pass makes the result deterministic, so tests can assert on a "
            "single order rather than a set. The order is not unique, and that is fine; any order that respects "
            "the edges is correct. What matters is that the dependency relation, not the file order, drives the "
            "run. Today you build an adjacency dictionary, run Kahn's algorithm with plain loops, print the "
            "order, and assert that key dependencies come first. Later lessons limit how many ready steps run at "
            "once, but the ordering logic stays the same."
        ),
        code=(
            'graph = {\n'
            '    "extract": [],\n'
            '    "validate": ["extract"],\n'
            '    "transform": ["extract"],\n'
            '    "load": ["validate", "transform"],\n'
            '    "report": ["load"],\n'
            '}\n'
            '\n'
            'def toposort(graph):\n'
            '    remaining = {name: set(deps) for name, deps in graph.items()}\n'
            '    order = []\n'
            '    while remaining:\n'
            '        ready = sorted(name for name, deps in remaining.items() if not deps)\n'
            '        if not ready:\n'
            '            raise ValueError("cycle detected")\n'
            '        for name in ready:\n'
            '            order.append(name)\n'
            '            del remaining[name]\n'
            '        for deps in remaining.values():\n'
            '            deps.difference_update(ready)\n'
            '    return order\n'
            '\n'
            'order = toposort(graph)\n'
            'print("order:", order)\n'
            'assert order.index("extract") < order.index("load") < order.index("report")\n'
            'print("toposort turns dependencies into a runnable order")'
        ),
        variant_b='add a second consumer of transform and confirm both it and load appear after transform',
        variant_c='add an edge from report back to extract and confirm the cycle is reported instead of hanging',
        mistakes=[
            "Running steps in file order and hoping the dependencies happen to line up.",
            "Recursing through dependencies without tracking visited nodes, so a cycle recurses forever.",
            "Treating one valid topological order as the only correct one and asserting on the exact list.",
        ],
        q1=(
            "How does Kahn's algorithm detect a cycle?",
            "If a pass finds no node with all dependencies satisfied while nodes remain, the remaining graph has a cycle.",
        ),
        homework=(
            "Write `toposort(graph)` that returns a dependency-respecting order using repeated ready passes, "
            "raising on a cycle. Run it on a five-node graph, print the order, add a cycle and print the error, "
            "and comment which line removes satisfied edges."
        ),
        patterns=["def toposort", "while ", "raise ValueError"],
        mapping=(
            "Airflow refuses to schedule a DAG containing a cycle, and Make reports circular dependencies; both "
            "are applying a topological check before any work starts."
        ),
    ),
    124: dict(
        topic="Parallel-safe step design",
        idea=(
            "Parallelism in a pipeline is not about threads in your code; it is a property of the graph. Two "
            "steps are parallel-safe when neither depends on the other and they do not write the same output. "
            "If both conditions hold, the scheduler may run them in the same wave, in either order, or one "
            "without the other. If either fails, running them together introduces a race that is painful to "
            "reproduce. The practical technique is to compute waves from the dependency graph: wave zero is "
            "every step with no dependencies, and each later wave contains steps whose dependencies all appear "
            "in earlier waves. That is the same ready-set loop as a topological sort, grouped by pass instead of "
            "flattened. Designing for this means giving each step explicit inputs and outputs, so collisions are "
            "visible in the data rather than discovered at runtime. It also means a step must not rely on a "
            "global mutable object or on being the only writer of a shared resource. A useful test is to imagine "
            "the wave in reverse order and ask whether the result changes; if it does, the steps were not "
            "parallel-safe. Today you group a graph into waves and print how many steps can run together. No "
            "threads are started; the schedule is data, which is exactly what a real orchestrator consumes."
        ),
        code=(
            'deps = {"extract": [], "clean_a": ["extract"], "clean_b": ["extract"], "join": ["clean_a", "clean_b"]}\n'
            '\n'
            'def waves(deps):\n'
            '    remaining = {name: set(parents) for name, parents in deps.items()}\n'
            '    levels = []\n'
            '    while remaining:\n'
            '        ready = sorted(name for name, parents in remaining.items() if not parents)\n'
            '        levels.append(ready)\n'
            '        for name in ready:\n'
            '            del remaining[name]\n'
            '        for parents in remaining.values():\n'
            '            parents.difference_update(ready)\n'
            '    return levels\n'
            '\n'
            'levels = waves(deps)\n'
            'for index, level in enumerate(levels):\n'
            '    print(f"wave {index}: {level} ({len(level)} parallel-safe)")\n'
            '\n'
            'assert levels[1] == ["clean_a", "clean_b"]\n'
            'print("steps in one wave touch different outputs and may run at once")'
        ),
        variant_b='add clean_c that writes the same output as clean_a and explain why they must not share a wave',
        variant_c='move the join into wave one by removing one dependency and see which invariant breaks',
        mistakes=[
            "Assuming steps can run together because they look independent, while both write one shared output.",
            "Using a global mutable cache from parallel steps, so results depend on which step ran first.",
            "Conflating a wave with a thread pool, then expecting the scheduler to fix unsafe data access.",
        ],
        q1=(
            "What two conditions make two steps safe to run in the same wave?",
            "Neither may depend on the other, and they must not write the same output or shared mutable state.",
        ),
        homework=(
            "Write `waves(deps)` that groups nodes into dependency levels and returns a list of sorted waves. "
            "Run it on a graph with two independent cleaners, print each wave and its size, and comment which "
            "line proves the cleaners have no unmet dependencies."
        ),
        patterns=["def waves", "levels.append", "print("],
        mapping=(
            "Airflow's parallelism settings and Dagster's multiprocess executor both schedule independent tasks "
            "concurrently; the graph must declare independence before that is safe."
        ),
    ),
    125: dict(
        topic="Checkpoints and resume",
        idea=(
            "Long pipelines fail partway, and rerunning everything from the start is both slow and risky. A "
            "checkpoint records which steps completed and what they produced, so a later run can skip the "
            "recorded steps and continue from the first missing one. The record should be written after a step "
            "genuinely succeeds, not before, or a crash turns unfinished work into a false completion. It should "
            "also be keyed by something that changes when the inputs change, otherwise a resumed run will happily "
            "reuse stale results. The simplest model is a dictionary from step name to a small result summary, "
            "loaded before the run and updated as steps finish. Resuming then becomes a check at the top of the "
            "loop: if the step is recorded and still valid, print that it was resumed and move on; otherwise run "
            "it and record the result. This design has a pleasant property: the checkpoint is just data, so you "
            "can inspect it, test resume behaviour without failing anything, and even hand-edit it during an "
            "incident. The hard part in production is validity, not storage, because a checkpoint that is never "
            "invalidated slowly becomes a cache of wrong answers. Today you resume a run from a small checkpoint "
            "and assert that recorded steps are skipped while the rest execute."
        ),
        code=(
            'checkpoint = {"extract": "rows=3", "clean": "rows=2"}\n'
            'steps = ["extract", "clean", "transform", "load"]\n'
            '\n'
            'done = dict(checkpoint)\n'
            'for name in steps:\n'
            '    if name in done:\n'
            '        print(f"{name:9} resumed -> {done[name]}")\n'
            '        continue\n'
            '    result = f"{name}-ok"\n'
            '    done[name] = result\n'
            '    print(f"{name:9} ran -> {result}")\n'
            '\n'
            'assert done["clean"] == "rows=2"\n'
            'assert done["load"] == "load-ok"\n'
            'print("resume skips recorded steps and replays the rest")'
        ),
        variant_b='key the checkpoint by an input version and show a stale version forcing every step to rerun',
        variant_c='record each step only after a success flag and print the checkpoint after a mid-run stop',
        mistakes=[
            "Writing the checkpoint before the step finishes, so a crash marks incomplete work as done.",
            "Never invalidating a checkpoint, so changed inputs silently reuse stale results.",
            "Storing only a boolean instead of the result the next step needs, forcing a partial rerun anyway.",
        ],
        q1=(
            "When should a pipeline write a step's checkpoint?",
            "Only after the step has fully succeeded, so a crash cannot leave unfinished work recorded as complete.",
        ),
        homework=(
            "Write `resume(steps, checkpoint)` that skips recorded steps, runs the rest, and returns the updated "
            "checkpoint. Start from two recorded steps, print each action, then rerun with the completed "
            "checkpoint and comment which line makes the second run skip everything."
        ),
        patterns=["def resume", "in checkpoint", "print("],
        mapping=(
            "Airflow task retries and Dagster's resume runs both rely on durable per-step state; the same idea "
            "appears in build systems that skip targets whose outputs are current."
        ),
    ),
    126: dict(
        topic="Partial failure handling",
        idea=(
            "Real pipelines rarely fail as a unit. One branch breaks while another is still healthy, and the "
            "interesting engineering is deciding what may continue and what must stop. The core rule is simple: "
            "a step whose dependency failed cannot run, so it is blocked, not failed. Steps that do not depend on "
            "the failure may still be worth running, because finishing the independent branch preserves work and "
            "gives a more useful report. Modelling this means tracking a status per step and propagating it along "
            "the edges: if any parent is not successful, mark the child blocked and move on; otherwise run it or "
            "record its modelled failure. The result is a run where failures do not cascadingly rewrite history "
            "as failed work, but as a mix of failed and blocked nodes that explains itself. This distinction "
            "matters for alerting, because a blocked step needs no retry until its parent is fixed, while a failed "
            "step may deserve one. It also matters for cleanup, since only steps that actually ran may need "
            "compensation. Today you process a small graph in dependency order, mark one step as failing, and "
            "print the resulting statuses. The statuses are plain strings in a dictionary, which is enough to "
            "show the propagation rule without a scheduler or an exception framework."
        ),
        code=(
            'deps = {"extract": [], "clean": ["extract"], "enrich": ["extract"], "load": ["clean", "enrich"]}\n'
            'failed = {"enrich"}\n'
            'status = {}\n'
            '\n'
            'for name in ("extract", "clean", "enrich", "load"):\n'
            '    parents = deps[name]\n'
            '    if any(status.get(parent) != "ok" for parent in parents):\n'
            '        status[name] = "blocked"\n'
            '    elif name in failed:\n'
            '        status[name] = "failed"\n'
            '    else:\n'
            '        status[name] = "ok"\n'
            '    print(f"{name:7} {status[name]}")\n'
            '\n'
            'assert status["clean"] == "ok"\n'
            'assert status["load"] == "blocked"\n'
            'print("independent branches continue while dependants are blocked")'
        ),
        variant_b='let clean fail as well and confirm load is still blocked while enrich reports failed',
        variant_c='retry the failed step once and show load unblocking when the retry succeeds',
        mistakes=[
            "Marking blocked steps as failed, which hides the difference between broken work and work never attempted.",
            "Aborting the whole run on the first failure, throwing away healthy parallel branches.",
            "Retrying a blocked step before fixing the parent that caused the block.",
        ],
        q1=(
            "What is the difference between a failed step and a blocked step?",
            "A failed step ran and broke; a blocked step never ran because one of its dependencies did not succeed.",
        ),
        homework=(
            "Write `run_graph(deps, failed)` that returns a status per step, marking dependants blocked when a "
            "parent is not ok. Run it with one failing branch, print each status, assert the independent branch "
            "still succeeded, and comment which line propagates the failure."
        ),
        patterns=["def run_graph", "blocked", "print("],
        mapping=(
            "Airflow marks downstream tasks upstream_failed or skipped, and Dagster distinguishes failed assets "
            "from ones that never materialised because an upstream asset broke."
        ),
    ),
    127: dict(
        topic="Rolling back a step",
        idea=(
            "Some steps change the world, and when a later step fails you want the earlier changes undone rather "
            "than left half-applied. The standard pattern is compensation: for every step that supports it, "
            "define an inverse action, record the inverse when the forward step succeeds, and on failure run the "
            "recorded inverses in reverse order. Reverse order matters because the steps may have built on each "
            "other; undoing the foundation before the structure leaves the world in an inconsistent state. Not "
            "every step needs an inverse. Read-only work can be skipped, and some effects are simply not "
            "reversible, which is a fact to design around rather than hide. The compensation log is also a useful "
            "audit artefact: it says exactly what was done and what was undone. This is not the same as a "
            "database transaction, although the intuition is similar. A transaction is enforced by the storage "
            "engine, while pipeline compensation is application logic that you must write and test. The lazy "
            "version, and the one that stays honest, is a small stack of undo callables or undo descriptions "
            "pushed as steps complete. Today you model three steps where the third fails, print the forward "
            "successes, then pop and apply the recorded undos in reverse. Nothing is actually changed; the log "
            "shows the discipline."
        ),
        code=(
            'steps = [\n'
            '    ("reserve", "release", True),\n'
            '    ("write", "delete", True),\n'
            '    ("publish", "unpublish", False),\n'
            ']\n'
            '\n'
            'undo_stack = []\n'
            'for run, undo, succeeds in steps:\n'
            '    if not succeeds:\n'
            '        print(f"{run} failed")\n'
            '        break\n'
            '    undo_stack.append(undo)\n'
            '    print(f"{run} ok")\n'
            '\n'
            'for undo in reversed(undo_stack):\n'
            '    print("rollback:", undo)\n'
            '\n'
            'assert undo_stack == ["release", "delete"]\n'
            'print("compensations run in reverse completion order")'
        ),
        variant_b='make the first step irreversible and print a warning instead of pretending it can be undone',
        variant_c='add a fourth step that fails and confirm the rollback list grows by exactly one entry',
        mistakes=[
            "Running compensations in completion order, so later effects are undone before the ones beneath them.",
            "Pretending an irreversible step can be rolled back instead of warning and designing around it.",
            "Recording a compensation before the forward step succeeds, so rollback undoes work that never happened.",
        ],
        q1=(
            "Why run compensations in reverse order of completion?",
            "Later steps may depend on earlier ones, so undoing the foundation first would leave the intermediate state inconsistent.",
        ),
        homework=(
            "Write `run_with_rollback(steps)` where each entry carries a run name, an undo name and a success "
            "flag. Push undos for successful steps, stop on failure, then print the rollback list in reverse and "
            "comment which line enforces that order."
        ),
        patterns=["def run_with_rollback", "reversed(", "print("],
        mapping=(
            "Saga patterns in distributed systems use the same compensate-on-failure idea, and deployment tools "
            "often keep an explicit rollback plan for each applied change."
        ),
    ),
    128: dict(
        topic="Dry-run for pipelines",
        idea=(
            "A dry run answers a cheap question before an expensive one: what would this pipeline do? The "
            "implementation is a flag that changes the effect of each step while keeping the plan identical. A "
            "step that would create a table prints that it would create it; a step that would write rows prints "
            "the count it would write. Because the plan is produced by the same code path as the real run, the "
            "dry run is not a separate document that can drift. This is the key property: a hand-written summary "
            "of intended actions rots as soon as the pipeline changes, while a generated plan cannot. The usual "
            "mistake is to skip side effects but still perform expensive reads or validation that only makes "
            "sense during a real run, which turns a fast preview into a slow one. Keep the dry run at the level "
            "of decisions and counts. It is also worth printing the resolved settings and the step order alongside "
            "the actions, because many incidents are configuration mistakes rather than code mistakes. Today you "
            "write a tiny executor that takes a dry-run flag, print the plan in dry mode, then run the same steps "
            "for real and compare. The same list of strings comes back with a different verb, which is exactly "
            "what makes the preview trustworthy."
        ),
        code=(
            'def execute(steps, dry_run):\n'
            '    log = []\n'
            '    for name, action in steps:\n'
            '        verb = "would" if dry_run else "did"\n'
            '        log.append(f"{verb} {action}")\n'
            '    return log\n'
            '\n'
            'steps = [\n'
            '    ("create", "create table"),\n'
            '    ("fill", "insert 3 rows"),\n'
            '    ("index", "build index"),\n'
            ']\n'
            '\n'
            'plan = execute(steps, dry_run=True)\n'
            'actual = execute(steps, dry_run=False)\n'
            'for line in plan:\n'
            '    print(line)\n'
            '\n'
            'assert plan[1] == "would insert 3 rows"\n'
            'assert actual[1] == "did insert 3 rows"\n'
            'print("dry-run proves the plan without changing state")'
        ),
        variant_b='include the resolved output name in every action so the dry run doubles as a config check',
        variant_c='make one step read a count first and show why that read belongs in both modes',
        mistakes=[
            "Hand-writing the dry-run plan next to the real logic, so the two drift apart after a change.",
            "Skipping side effects but still doing expensive reads, making the preview nearly as slow as the run.",
            "Treating a clean dry run as proof of correctness rather than proof that the plan is well formed.",
        ],
        q1=(
            "Why should the dry-run plan be generated by the same code that performs the real run?",
            "So the preview cannot drift from reality when the pipeline changes; only the effect of each step differs.",
        ),
        homework=(
            "Write `execute(steps, dry_run)` that returns one descriptive line per step, using would or did "
            "depending on the flag. Build three steps, print the dry-run lines, compare against the real run, and "
            "comment which line keeps both modes on one code path."
        ),
        patterns=["def execute", "dry_run", "print("],
        mapping=(
            "Airflow's dry-run behaviour, Terraform plan and Make's -n flag all preview intended actions; the "
            "value comes from generating the preview from the same plan the real run uses."
        ),
    ),
    129: dict(
        topic="Retries per step",
        idea=(
            "A retry is a small loop around one step, not a loop around the whole pipeline. Putting the policy at "
            "the step keeps successful work intact and limits the blast radius of a transient failure. The "
            "minimal policy has three parts: how many attempts are allowed, which errors are worth retrying, and "
            "what to do when attempts run out. Attempts are counted with an integer, and the count is part of the "
            "result because the log needs it and metrics need it. Retrying everything is a common mistake. A "
            "validation error or a missing input will fail identically on every attempt, so retrying it only "
            "wastes time and delays the alert. Retry transient conditions such as a busy resource or a flaky "
            "remote call, and fail fast on deterministic ones. It is equally important that the step be safe to "
            "run twice; a retry of a non-idempotent write can duplicate data, which is worse than the original "
            "failure. In production you also add a delay between attempts and often exponential backoff, but "
            "timing is deliberately omitted here so the example stays deterministic. Today you model a step that "
            "fails once then succeeds, count the attempts, and return both the outcome and the count. The loop "
            "prints each attempt, which is exactly what you want to see in a run log."
        ),
        code=(
            'def run_step(name, failures_before_success, max_attempts=3):\n'
            '    attempts = 0\n'
            '    while attempts < max_attempts:\n'
            '        attempts += 1\n'
            '        ok = attempts > failures_before_success\n'
            '        print(f"{name} attempt {attempts}: {\'ok\' if ok else \'error\'}")\n'
            '        if ok:\n'
            '            return True, attempts\n'
            '    return False, attempts\n'
            '\n'
            'result = run_step("fetch", 1)\n'
            'print("result:", result)\n'
            '\n'
            'assert result == (True, 2)\n'
            'assert run_step("fetch", 5, max_attempts=2) == (False, 2)\n'
            'print("retry policy is data: attempts are counted, not slept on")'
        ),
        variant_b='set max_attempts to one and confirm the same failure is reported without a second attempt',
        variant_c='return a log list of attempt outcomes and assert the last entry explains the final result',
        mistakes=[
            "Retrying deterministic errors such as bad input, which fail identically every time.",
            "Wrapping the whole pipeline in the retry loop, so successful steps run again unnecessarily.",
            "Retrying a non-idempotent write, which duplicates work instead of recovering from it.",
        ],
        q1=(
            "Which errors deserve a retry and which should fail fast?",
            "Transient conditions such as a busy resource may be retried; deterministic errors such as invalid input will never succeed and should fail immediately.",
        ),
        homework=(
            "Write `run_step(name, failures_before_success, max_attempts)` that counts attempts and returns a "
            "success flag plus the count. Run one case that succeeds on the second attempt and one that exhausts "
            "its budget, print both results, and comment which condition exits the loop."
        ),
        patterns=["def run_step", "attempts += 1", "print("],
        mapping=(
            "Airflow exposes retries and retry_delay per task, and Dagster has retry policies per op; scoping the "
            "policy to a step is what keeps a retry from replaying the entire DAG."
        ),
    ),
    130: dict(
        topic="Timeouts conceptually",
        idea=(
            "A timeout is a promise about how long a step is allowed to occupy the pipeline. Conceptually it is "
            "just a budget compared against an elapsed cost: if the cost exceeds the budget, the step is declared "
            "timed out and its dependants are blocked, just like any other failure. Modelling it as data makes "
            "the policy visible and testable without waiting for a real clock. In a real runner the cost comes "
            "from a monotonic clock and the budget might be enforced by cancelling the work, but the decision "
            "logic is the comparison you write here. Timeouts exist because a stuck step is worse than a failed "
            "one: it holds resources, hides the failure and delays every downstream alert. The budget should "
            "reflect the normal distribution of runtimes, not the worst case ever observed, and it should be "
            "per step rather than per pipeline so one slow stage does not starve the others. A pipeline-level "
            "deadline is still useful as a backstop, because a sequence of individually acceptable steps can add "
            "up to an unacceptable total. Notice that a timeout is not a retry. Retrying a step that times out "
            "may be right for transient slowness and wrong for a step that is simply too expensive for its "
            "budget. Today you compare modelled costs to per-step budgets, print the outcome, and accumulate the "
            "total until a step exceeds its allowance."
        ),
        code=(
            'steps = [("fetch", 4, 5), ("parse", 2, 5), ("upload", 6, 5)]\n'
            'total = 0\n'
            '\n'
            'for name, cost, budget in steps:\n'
            '    if cost > budget:\n'
            '        print(f"{name:6} timed out: cost {cost} > budget {budget}")\n'
            '        break\n'
            '    total += cost\n'
            '    print(f"{name:6} ok: {cost}/{budget} units, total {total}")\n'
            '\n'
            'assert total == 6\n'
            'assert cost > budget\n'
            'print("a timeout is a budget compared to a modelled cost")'
        ),
        variant_b='tighten the parse budget to one and show the pipeline stopping there instead of reaching upload',
        variant_c='add a total pipeline deadline and show it firing even when every individual step is within budget',
        mistakes=[
            "Setting one pipeline timeout so generous that it never catches the slow step causing the damage.",
            "Choosing budgets from the slowest run ever seen, which makes the timeout meaningless.",
            "Treating a timeout as automatically retryable when the step is simply too expensive for its budget.",
        ],
        q1=(
            "Why apply timeouts per step rather than only to the whole pipeline?",
            "A per-step budget localises the slow stage and stops it from consuming the time allowed to everything else.",
        ),
        homework=(
            "Write `run_with_deadlines(steps)` where each step has a name, a modelled cost and a budget. Stop at "
            "the first over-budget step, return the completed steps and the total cost, print each decision, and "
            "comment which comparison enforces the timeout."
        ),
        patterns=["def run_with_deadlines", "cost > budget", "print("],
        mapping=(
            "Airflow task timeouts, Dagster run timeouts and CI job limits all encode a budget; the useful ones "
            "are per step with an overall deadline as a backstop."
        ),
    ),
    131: dict(
        topic="Logging each step",
        idea=(
            "A pipeline that cannot explain itself is not operable. When a run takes longer than expected or "
            "produces the wrong output, the log is the only evidence of what happened and in what order. The "
            "useful unit of logging is one structured record per step attempt, carrying the step name, the "
            "outcome, the attempt number and a small cost or row count. Structured means the fields are separate "
            "values rather than a sentence, so they can be filtered, counted and compared without parsing prose. "
            "Printing the same record as key=value lines is enough for a lesson and mirrors what a JSON logger "
            "does in production. Two rules keep logs trustworthy. Log the end of an attempt as well as the start, "
            "so a crashed step is visibly unfinished rather than silently absent. And log at the boundary, where "
            "the runner knows the outcome, rather than scattering prints inside business logic, so the format "
            "stays consistent. A summary derived from the records, such as the list of failed steps, is worth "
            "printing at the end, because that is what a human reads first. Today you build a run log as a list "
            "of dictionaries, print one line per record, and derive the failures from the same data. Notice that "
            "the summary is computed, not hand-written, so it cannot disagree with the log."
        ),
        code=(
            'run = [\n'
            '    {"step": "extract", "status": "ok", "attempt": 1, "units": 4},\n'
            '    {"step": "clean", "status": "ok", "attempt": 1, "units": 2},\n'
            '    {"step": "load", "status": "failed", "attempt": 2, "units": 3},\n'
            ']\n'
            '\n'
            'for record in run:\n'
            '    line = " ".join(f"{key}={record[key]}" for key in ("step", "status", "attempt", "units"))\n'
            '    print(line)\n'
            '\n'
            'failed = [record["step"] for record in run if record["status"] != "ok"]\n'
            'print("failed:", failed)\n'
            'print("attempts:", sum(record["attempt"] for record in run))\n'
            '\n'
            'assert failed == ["load"]\n'
            'print("one structured record per step is enough to explain a run")'
        ),
        variant_b='add a "reason" field only for failures and include it in the failure summary line',
        variant_c='log both start and end records and show how an unfinished step becomes visible',
        mistakes=[
            "Logging free-form sentences inside business logic, so every step invents a different format.",
            "Logging only successes, so a crashed step leaves no trace of having been attempted.",
            "Hand-writing the end-of-run summary instead of deriving it from the recorded steps.",
        ],
        q1=(
            "Why log structured fields instead of a sentence per step?",
            "Separate fields can be filtered, counted and compared automatically, while prose has to be parsed again for every question.",
        ),
        homework=(
            "Write `step_log(records)` that prints one key=value line per record and returns the failed step names "
            "plus the total attempts. Build three records including one failure, print the summary, and comment "
            "which line derives failures from the same data."
        ),
        patterns=["def step_log", "for record in", "print("],
        mapping=(
            "Orchestrators attach task-instance logs to every attempt and surface them in the UI; consistent "
            "fields are what make those logs searchable across runs."
        ),
    ),
    132: dict(
        topic="Reporting the run graph",
        idea=(
            "A finished run is easiest to understand as a graph annotated with outcomes. Tables of timings are "
            "precise but slow to read, while a graph shows the shape of the work: what fed what, where it "
            "branched, and which nodes failed. The minimal report is one line per step with its status and its "
            "parents, plus a count of edges so the reader can tell a wide graph from a deep one. This is the same "
            "dependency data the scheduler used, presented rather than recomputed, which keeps the report honest. "
            "When you add counts of ok, failed and blocked nodes, the report answers the first three questions "
            "anyone asks after an incident: how much finished, what broke, and what never got a chance to run. "
            "It is also worth showing the edges in the parent direction rather than the child direction, because "
            "during a postmortem people reason backwards from the broken node to its inputs. A good report is "
            "short enough to read in a terminal and structured enough to diff between runs. That combination "
            "makes it useful both to a human at 3am and to a script comparing last night's shape with tonight's. "
            "Today you print an annotated graph from a dependency dictionary and a status dictionary, count the "
            "edges, and assert that every step is accounted for. The report is generated, so it cannot omit a node "
            "that the run actually scheduled."
        ),
        code=(
            'deps = {"extract": [], "clean": ["extract"], "load": ["extract"], "join": ["clean", "load"]}\n'
            'status = {"extract": "ok", "clean": "ok", "load": "failed", "join": "blocked"}\n'
            '\n'
            'for name, parents in deps.items():\n'
            '    arrow = " <- " + ", ".join(parents) if parents else ""\n'
            '    print(f"{status[name]:7} {name}{arrow}")\n'
            '\n'
            'edges = sum(len(parents) for parents in deps.values())\n'
            'summary = {value: list(status.values()).count(value) for value in ("ok", "failed", "blocked")}\n'
            'print("edges:", edges, "summary:", summary)\n'
            '\n'
            'assert edges == 4 and summary["blocked"] == 1\n'
            'assert set(status) == set(deps)\n'
            'print("a run graph is edges plus per-node status")'
        ),
        variant_b='print children instead of parents and compare which direction is easier to read after a failure',
        variant_c='add a per-node row count and show how it turns the report into a data-volume summary',
        mistakes=[
            "Reporting only the failed step, so the reader cannot see which healthy branch was wasted.",
            "Recomputing the graph for the report, which may disagree with the graph the scheduler actually ran.",
            "Printing timings without statuses, so the report shows effort but not outcomes.",
        ],
        q1=(
            "What should a minimal run-graph report contain?",
            "One line per step with status and parents, plus edge and status counts, all derived from the graph the run used.",
        ),
        homework=(
            "Write `report_graph(deps, status)` that prints one annotated line per step and returns the edge count "
            "plus a status summary. Run it on a branched graph with one failure, print the summary, and comment "
            "which line keeps the report aligned with the dependency data."
        ),
        patterns=["def report_graph", "sum(", "print("],
        mapping=(
            "Airflow's graph view and Dagster's asset lineage are rich versions of this report; a text rendering "
            "is often faster during an incident than loading the UI."
        ),
    ),
    133: dict(
        topic="Testing a pipeline end to end",
        idea=(
            "Testing a pipeline end to end means feeding a fixture through the real step sequence and asserting on "
            "the final values, not mocking each stage into agreeing with itself. The value is in the integration: "
            "a step that works alone can still drop a key, reorder rows or break a contract with its neighbour, "
            "and only a full run catches that. Good pipeline tests are small and boring. Use a tiny fixture that "
            "exercises the branches you care about, run the whole pipeline, and assert on the output. Add one "
            "edge-case fixture, usually empty input, because empty data is where pipelines most often divide by "
            "zero or index an empty list. Assertions should describe behaviour, not implementation: the count, "
            "the contents and the ordering rather than the exact internal dictionary. That keeps the test useful "
            "when the pipeline is refactored. It also helps to wrap assertions in a tiny check helper that prints "
            "pass or fail, so the test output doubles as the lesson's output and reads like a report. Finally, "
            "test the properties you rely on in production, especially idempotence: running the pipeline twice on "
            "the same input should not change the result. Today you build a two-step pipeline, run a normal and "
            "an empty fixture, and assert both. The tests are plain functions and asserts, with no framework, "
            "which is all a small pipeline needs to start."
        ),
        code=(
            'def pipeline(rows):\n'
            '    cleaned = [row.strip().lower() for row in rows if row.strip()]\n'
            '    return {"rows": cleaned, "count": len(cleaned)}\n'
            '\n'
            'def check(name, actual, expected):\n'
            '    print(f"{name}: {\'pass\' if actual == expected else \'fail\'}")\n'
            '    assert actual == expected\n'
            '\n'
            'result = pipeline([" A ", "", "B"])\n'
            'check("rows", result["rows"], ["a", "b"])\n'
            'check("count", result["count"], 2)\n'
            'check("empty input", pipeline([])["count"], 0)\n'
            'check("idempotent", pipeline(result["rows"]), result)\n'
            'print("end to end means fixtures in, asserted values out")'
        ),
        variant_b='add a fixture with duplicate rows and decide whether the pipeline or the test owns deduplication',
        variant_c='run the same fixture twice and assert the second result equals the first to prove idempotence',
        mistakes=[
            "Mocking every step, so the test never checks that the steps actually fit together.",
            "Asserting on internal dictionaries, so a harmless refactor breaks the test without changing behaviour.",
            "Testing only the happy path and never running the pipeline on empty input.",
        ],
        q1=(
            "Why run a fixture through the whole pipeline instead of unit-testing each step?",
            "Only a full run reveals broken handoffs, such as a dropped key or a changed row order between steps.",
        ),
        homework=(
            "Write `test_pipeline(pipeline_fn)` that runs a normal fixture and an empty fixture, prints pass or "
            "fail for each check, and asserts counts and contents. Include an idempotence check and comment which "
            "assertion would catch a step dropping a key."
        ),
        patterns=["def test_pipeline", "assert ", "print("],
        mapping=(
            "Airflow and Dagster both support running a DAG or asset job against test fixtures; CI often runs that "
            "end-to-end smoke test before promoting a workflow."
        ),
    ),
    134: dict(
        topic="Review: pipeline orchestration checklist",
        idea=(
            "Orchestration knowledge is easy to acquire and easy to forget under pressure, so the final artifact "
            "of this phase is a checklist you can apply to any pipeline before trusting it. The checklist should "
            "cover the properties built up over the previous days: a stated goal, steps as transforms, explicit "
            "handoffs, a checked dependency order, parallel safety, checkpoints, partial-failure semantics, "
            "rollback, dry run, retries, timeouts, logging and end-to-end tests. A checklist is not bureaucracy "
            "when each item maps to a failure you have actually seen. The point is to make the review repeatable, "
            "so a tired reviewer at the end of a sprint asks the same questions as a fresh one on Monday. The "
            "checklist should also produce a decision, not just a score: ship, ship with known gaps, or fix first. "
            "That forces the reviewer to separate a missing nicety from a missing safety property. In practice you "
            "would store the checklist with the pipeline and run it as part of review, and some items can even be "
            "automated, such as detecting a cycle or an unlogged step. Today you model a review as data, print "
            "each item with a pass mark, derive the missing items, and print a verdict. The same technique scales "
            "to a real deployment gate: a list of named checks and a computed outcome."
        ),
        code=(
            'run = {"ordered": True, "retries": True, "timeout": False, "checkpoint": True, "log": True}\n'
            'checks = [\n'
            '    ("dependency order", run["ordered"]),\n'
            '    ("retry policy", run["retries"]),\n'
            '    ("timeout budget", run["timeout"]),\n'
            '    ("checkpoint stored", run["checkpoint"]),\n'
            '    ("per-step log", run["log"]),\n'
            ']\n'
            '\n'
            'for name, passed in checks:\n'
            '    print(f"[{\'x\' if passed else \' \'}] {name}")\n'
            '\n'
            'missing = [name for name, passed in checks if not passed]\n'
            'print("verdict:", "ship" if not missing else "fix: " + ", ".join(missing))\n'
            '\n'
            'assert missing == ["timeout budget"]\n'
            'print("a checklist turns a run review into a repeatable decision")'
        ),
        variant_b='add an "idempotent" and an "end-to-end test" check and show the verdict changing to ship',
        variant_c='weight the checks as safety versus polish and show a polish gap not blocking the verdict',
        mistakes=[
            "Treating a checklist as a score to maximise rather than a set of distinct safety properties.",
            "Reviewing by memory instead of running the same named checks on every pipeline.",
            "Blocking a release on a missing nicety while ignoring a missing rollback or timeout.",
        ],
        q1=(
            "What makes a pipeline checklist useful rather than ceremonial?",
            "Each item maps to a real failure mode, is checked the same way every time, and produces a clear ship or fix verdict.",
        ),
        homework=(
            "Write `review_pipeline(run)` that evaluates five named safety checks over a run dictionary, prints "
            "each with a pass mark, and returns the missing checks and a verdict string. Run it on a run with one "
            "gap, print the verdict, and comment which line separates safety gaps from polish."
        ),
        patterns=["def review_pipeline", "missing", "print("],
        mapping=(
            "Production readiness reviews for Airflow DAGs and Dagster jobs use the same shape: named checks, a "
            "recorded outcome, and a gate that blocks promotion until safety gaps are closed."
        ),
    ),
})
