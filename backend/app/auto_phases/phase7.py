"""Automation capstone, days 165-179: scope, specify, plan, build, review, ship.

Every example is a working slice of one toy capstone: a nightly organiser that
turns an in-memory list of file records into planned paths, a manifest, a log
summary and a reviewed run. Stdlib-only, offline and deterministic: no real
files, network, threads, subprocess or clock.
"""

PHASE = ("Automation Capstone", "Ship a small, tested, documented organiser that plans, reviews and runs over in-memory file records.", {
    165: dict(
        topic="Capstone: choose the scope",
        idea=(
            "A capstone fails more often from an unclear boundary than from weak code. The first job is therefore "
            "to write a scope statement, not to open the editor. A useful scope statement has five parts: one goal "
            "sentence, the inputs the automation consumes, the outputs it produces, the non-goals it deliberately "
            "refuses, and the constraints it must respect. The goal must be observable, so 'organise the nightly "
            "inbox into report, image and archive folders' is better than 'improve file management'. Non-goals are "
            "the part beginners skip and later regret: saying explicitly that the tool will not delete files, talk "
            "to a network or provide a web interface keeps the build small and the review honest. Constraints such "
            "as stdlib only, deterministic tests and safe reruns are promises you can check at the end. A quick "
            "review function that verifies all five parts exist turns the template into a gate rather than a wish. "
            "Today you write that template and run it against the toy capstone: a nightly organiser that reads an "
            "in-memory list of file records and plans where each one belongs. Keep the scope narrow enough to "
            "finish in the remaining days, because a shipped small tool teaches more than an unfinished large one."
        ),
        code=(
            'SCOPE = {\n'
            '    "goal": "organise the nightly inbox into report, image and archive folders",\n'
            '    "inputs": ["in-memory file records with name, kind and size"],\n'
            '    "outputs": ["planned paths", "manifest", "summary"],\n'
            '    "non_goals": ["deleting files", "network sync", "a web interface"],\n'
            '    "constraints": ["stdlib only", "deterministic tests", "safe reruns"],\n'
            '}\n'
            '\n'
            'def review_scope(scope):\n'
            '    required = ("goal", "inputs", "outputs", "non_goals", "constraints")\n'
            '    return [key for key in required if not scope.get(key)]\n'
            '\n'
            'for key in ("goal", "inputs", "outputs", "non_goals", "constraints"):\n'
            '    print(key, "->", SCOPE[key])\n'
            'print("problems:", review_scope(SCOPE))\n'
            '\n'
            'assert review_scope(SCOPE) == []\n'
            'assert review_scope({"goal": "x"}) == ["inputs", "outputs", "non_goals", "constraints"]\n'
            'print("scope is small enough to ship")'
        ),
        variant_b='add a sixth section named metrics and reject any scope where it is empty',
        variant_c='shrink the goal to one folder and one file kind, then rerun the review',
        mistakes=[
            "Writing a goal that cannot be observed, so completion is a matter of opinion.",
            "Skipping non-goals, which lets the build expand every time an idea appears.",
            "Choosing a scope too large to finish, so the capstone ships nothing.",
        ],
        q1=(
            "Why list non-goals in the scope statement?",
            "Non-goals make refused work explicit, which keeps the build small and lets a reviewer check that nothing crept in.",
        ),
        homework=(
            "Write `review_scope(scope)` that returns a list of missing sections for a capstone scope dict covering "
            "goal, inputs, outputs, non_goals and constraints. Test it on the toy organiser scope and on a scope "
            "with two sections removed, print both problem lists, and comment which check keeps the scope narrow."
        ),
        patterns=["def ", "non_goals", "print("],
        mapping=(
            "Teams write a one-page charter or design doc before a build for the same reason: agreed boundaries "
            "are cheaper to change than code written against a moving target."
        ),
    ),
    166: dict(
        topic="Write the automation spec",
        idea=(
            "Once the scope is clear, the next artifact is a specification that another person could implement "
            "without asking you questions. A compact automation spec has six sections: trigger, inputs, outputs, "
            "steps, failure policy and definition of done. The trigger says when the run happens, for example "
            "'nightly at 02:00 on weekdays'. Inputs name the source records and their required fields. Outputs "
            "name the planned destinations, the manifest and the log. Steps describe the pipeline in order at the "
            "level of intentions rather than code. Failure policy is where the spec earns its keep: what happens "
            "to a bad record, whether a partial run is acceptable, and what exit code each outcome produces. "
            "Definition of done lists the checks that must pass before you call the work shipped. Keeping the "
            "spec as a dictionary in code, with a required-sections check, means the document can be validated "
            "instead of drifting. This is the same discipline as an RFC or a ticket with acceptance criteria, "
            "scaled down to one evening of work. Today you build the six-section spec for the file organiser and "
            "assert that no section is empty. Later days fill in the contract, the plan and the tests that make "
            "these promises concrete."
        ),
        code=(
            'SPEC = {\n'
            '    "trigger": "weekdays at 02:00",\n'
            '    "inputs": ["in-memory file records"],\n'
            '    "outputs": ["planned paths", "manifest", "summary"],\n'
            '    "steps": ["load", "classify", "plan", "render"],\n'
            '    "failure_policy": "reject bad records and exit 1 on any failure",\n'
            '    "done_when": ["tests pass", "dry run reviewed"],\n'
            '}\n'
            'REQUIRED = ("trigger", "inputs", "outputs", "steps", "failure_policy", "done_when")\n'
            '\n'
            'def spec_problems(spec):\n'
            '    return [key for key in REQUIRED if not spec.get(key)]\n'
            '\n'
            'print("trigger:", SPEC["trigger"])\n'
            'print("steps:", " -> ".join(SPEC["steps"]))\n'
            'print("done when:", "; ".join(SPEC["done_when"]))\n'
            'print("problems:", spec_problems(SPEC))\n'
            '\n'
            'assert spec_problems(SPEC) == []\n'
            'assert spec_problems({"trigger": "x"}) == ["inputs", "outputs", "steps", "failure_policy", "done_when"]\n'
            'print("spec has all six sections")'
        ),
        variant_b='state a retry policy in the failure section and require it in spec_problems',
        variant_c='write the spec for a weekly run instead and check the trigger and steps change',
        mistakes=[
            "Describing steps as vague intentions with no order, so two implementers build different pipelines.",
            "Leaving failure policy out, so nobody knows what a bad record should do.",
            "Writing done-when as a feeling instead of checks that can actually run.",
        ],
        q1=(
            "What belongs in the failure policy section of an automation spec?",
            "The handling and exit code for bad records, skipped items and partial runs, so a scheduler can tell success from failure.",
        ),
        homework=(
            "Write `spec_problems(spec)` that returns the names of the six required automation-spec sections that "
            "are missing or empty. Run it on a complete file-organiser spec and on one with failure_policy "
            "removed, print both lists, and comment which missing section would make a scheduler unsafe."
        ),
        patterns=["def ", "problems", "print("],
        mapping=(
            "RFCs, runbooks and ticket templates all encode the same six questions; writing the spec as data "
            "lets CI or a reviewer check it instead of trusting memory."
        ),
    ),
    167: dict(
        topic="Define the input and output contract",
        idea=(
            "Contracts are what let two parts of a system disagree safely. The input contract states which fields "
            "every file record must carry and what types they have; the output contract states exactly what the "
            "organiser promises to return, including failure entries. A good contract is small, explicit and "
            "validated at the edge, before any pipeline step runs. For the toy organiser the input record needs a "
            "name, a folder, an integer size and a kind, while the output entry needs a source, an action and a "
            "reason that is empty only on success. Validation returns a list of problems rather than raising on "
            "the first one, so a single run can report every malformed record. Rejected records are not silently "
            "dropped; they become output entries with action 'rejected', which keeps the run's accounting "
            "complete. Two rules matter. Never infer a missing field from a filename when the contract says it is "
            "required, because that hides upstream bugs. And version the contract in words, so a later change to "
            "a field is a deliberate decision rather than an accident. Today you write validate_record and check "
            "a small batch containing one good record and two violations, printing accepted and rejected entries. "
            "This is the boundary that makes every later step trustworthy."
        ),
        code=(
            'KINDS = {"report", "image", "misc"}\n'
            '\n'
            'def validate_record(record):\n'
            '    problems = []\n'
            '    for key in ("name", "folder", "size"):\n'
            '        if key not in record:\n'
            '            problems.append(f"missing {key}")\n'
            '    if "size" in record and not isinstance(record["size"], int):\n'
            '        problems.append("size is not int")\n'
            '    if record.get("kind") not in KINDS:\n'
            '        problems.append("bad kind")\n'
            '    return problems\n'
            '\n'
            'records = [\n'
            '    {"name": "sales.csv", "folder": "inbox", "size": 10, "kind": "report"},\n'
            '    {"name": "logo.png", "folder": "inbox", "size": 4, "kind": "image"},\n'
            '    {"name": "notes.txt", "folder": "inbox", "kind": "misc"},\n'
            ']\n'
            'for record in records:\n'
            '    problems = validate_record(record)\n'
            '    entry = {"source": record.get("name"), "action": "accepted" if not problems else "rejected",\n'
            '             "reason": "; ".join(problems)}\n'
            '    print(entry)\n'
            '\n'
            'assert validate_record(records[2]) == ["missing size"]\n'
            'assert sum(validate_record(r) == [] for r in records) == 2\n'
            'print("every record has one output entry")'
        ),
        variant_b='add a contract_version field and reject records that carry an older version',
        variant_c='reject a negative size as well as a non-integer one and print the new reasons',
        mistakes=[
            "Raising on the first bad record, so the run cannot report the rest of the batch.",
            "Dropping rejected records instead of emitting them, which breaks the totals.",
            "Inferring required fields from the filename, which hides upstream data bugs.",
        ],
        q1=(
            "Why return a list of contract problems instead of raising on the first one?",
            "One run can report every malformed record, and the caller can keep the accounting complete.",
        ),
        homework=(
            "Write `validate_record(record)` that returns a list of contract violations for a file record with "
            "name, folder, size and kind, including a non-integer size and an unknown kind. Run it over three "
            "records with one valid and two invalid, print the output entry for each, and comment which line "
            "keeps rejected records in the accounting."
        ),
        patterns=["def ", "validate_record", "print("],
        mapping=(
            "Schema validation at service boundaries — JSON Schema, protobuf, Pydantic — is the same idea: "
            "check once at the edge and keep the interior code simple."
        ),
    ),
    168: dict(
        topic="Plan the paths",
        idea=(
            "A path plan is the cheapest review you will ever get: it shows every file operation before anything "
            "happens. The planner is a pure function from input records to a list of source-to-target pairs, and "
            "it should be deterministic so that two runs over the same records produce the same plan. The first "
            "job is mapping a record's kind to a destination folder; the second is handling collisions, because "
            "two records called sales.csv cannot both land in reports/sales.csv. The usual answer is a "
            "deterministic rename: keep the stem, add a counter and preserve the suffix, giving sales-1.csv, "
            "sales-2.csv and so on. Doing this with pathlib rather than string concatenation keeps separators and "
            "suffixes correct. The planner should also record why each path was chosen, turning the plan into a "
            "small table that a human can scan: source, target and rule. Finally, assert two properties that must "
            "always hold: the plan covers every usable record exactly once, and no two targets are identical. "
            "Those two assertions catch the majority of organiser bugs before any move code exists. Today you "
            "build plan_paths over four in-memory records, including a duplicate name, print the table and check "
            "both properties. The next day's CLI will take this same plan and expose it as a dry-run output."
        ),
        code=(
            'from pathlib import PurePosixPath\n'
            '\n'
            'FOLDERS = {"report": "reports", "image": "images"}\n'
            '\n'
            'def plan_paths(records, root="out"):\n'
            '    seen = set()\n'
            '    plan = []\n'
            '    for record in records:\n'
            '        folder = FOLDERS.get(record["kind"], "archive")\n'
            '        target = PurePosixPath(root) / folder / record["name"]\n'
            '        counter = 1\n'
            '        while str(target) in seen:\n'
            '            target = target.with_name(f"{target.stem}-{counter}{target.suffix}")\n'
            '            counter += 1\n'
            '        seen.add(str(target))\n'
            '        plan.append((record["name"], str(target)))\n'
            '    return plan\n'
            '\n'
            'records = [\n'
            '    {"name": "sales.csv", "kind": "report"},\n'
            '    {"name": "logo.png", "kind": "image"},\n'
            '    {"name": "sales.csv", "kind": "report"},\n'
            '    {"name": "notes.txt", "kind": "misc"},\n'
            ']\n'
            'plan = plan_paths(records)\n'
            'for source, target in plan:\n'
            '    print(f"{source:10} -> {target}")\n'
            '\n'
            'assert len(plan) == len(records)\n'
            'assert len({target for _, target in plan}) == len(plan)\n'
            'assert plan[2][1] == "out/reports/sales-1.csv"\n'
            'print("plan is complete and collision free")'
        ),
        variant_b='make the counter start after the highest existing suffix instead of at one',
        variant_c='add preservation of the original folder as a subfolder and assert the new targets',
        mistakes=[
            "Planning with string concatenation, which produces missing separators and broken suffixes.",
            "Letting collisions silently overwrite instead of assigning deterministic names.",
            "Forgetting to assert that the plan count matches the input count, so dropped records go unnoticed.",
        ],
        q1=(
            "Why should the path planner be a pure, deterministic function?",
            "The same records always produce the same reviewable plan, so tests and dry runs can trust it.",
        ),
        homework=(
            "Write `plan_paths(records, root=\"out\")` that maps each record's kind to reports, images or archive "
            "and resolves duplicate names with a deterministic counter. Run it over four records including two "
            "called sales.csv, print each source to target pair, and comment which line makes the second target "
            "differ from the first."
        ),
        patterns=["def ", "plan_paths", "print("],
        mapping=(
            "rsync --dry-run, Terraform plan and kubectl diff all expose an intended change set before applying "
            "it; a path plan is the same safety habit at file scale."
        ),
    ),
    169: dict(
        topic="Build the CLI",
        idea=(
            "A command-line interface is a contract with the person or scheduler who runs the tool. The interface "
            "should be small, predictable and boring: a source folder, an output folder, a date for reproducible "
            "runs, and a dry-run switch that prints the plan without claiming to execute it. Argparse gives you "
            "parsing, defaults, types and help text for free, and the important discipline is to parse once, at "
            "the entry point, into a plain settings dictionary. No function deeper in the pipeline should read "
            "sys.argv or environment variables, because that makes it untestable and hides where configuration "
            "comes from. Validation belongs immediately after parsing: refuse an empty input, a relative output "
            "that escapes the workspace, or a date in the wrong format, and exit non-zero with one clear "
            "message. Defaults should be safe, which means dry-run off only when the caller explicitly asks to "
            "execute. In tests you call the parser with a list of tokens, never by spawning a process, so the "
            "interface can be checked deterministically. Today you build that parser for the organiser, parse a "
            "representative command line, print the resulting settings and assert the flag values. Tomorrow the "
            "pipeline consumes exactly this dictionary, which keeps the CLI and the work cleanly separated."
        ),
        code=(
            'import argparse\n'
            '\n'
            'def build_parser():\n'
            '    parser = argparse.ArgumentParser(prog="organise", add_help=False)\n'
            '    parser.add_argument("--inbox", default="inbox")\n'
            '    parser.add_argument("--out", default="out")\n'
            '    parser.add_argument("--date", default="2026-10-19")\n'
            '    parser.add_argument("--dry-run", action="store_true")\n'
            '    return parser\n'
            '\n'
            'tokens = ["--inbox", "incoming", "--out", "archive", "--dry-run"]\n'
            'settings = vars(build_parser().parse_args(tokens))\n'
            'print("settings:", settings)\n'
            'print("dry run:", settings["dry_run"])\n'
            '\n'
            'assert settings["inbox"] == "incoming"\n'
            'assert settings["out"] == "archive"\n'
            'assert settings["dry_run"] is True\n'
            'assert settings["date"] == "2026-10-19"\n'
            'print("defaults survive when flags are absent")'
        ),
        variant_b='add a --limit option typed as int and assert a bad value is rejected by argparse',
        variant_c='parse the same tokens without --dry-run and check the default is False',
        mistakes=[
            "Reading sys.argv deep inside the pipeline instead of parsing once into a settings dict.",
            "Using an unsafe default that executes when the caller forgets the dry-run flag.",
            "Spawning a process in tests instead of calling the parser with a token list.",
        ],
        q1=(
            "Why parse command-line tokens into a settings dictionary at the entry point?",
            "One plain structure feeds the pipeline, tests can build it directly, and configuration provenance stays visible.",
        ),
        homework=(
            "Write `parse_args(tokens)` that wraps argparse and returns settings for inbox, out, date and dry_run, "
            "with defaults for every flag. Parse one token list containing --inbox, --out and --dry-run, print "
            "the settings, and comment which line proves that parsing happens once at the entry point."
        ),
        patterns=["def ", "parse_args", "print("],
        mapping=(
            "Well-behaved CLI tools keep flags few, defaults safe and validation up front; schedulers depend on "
            "that stability as much as humans do."
        ),
    ),
    170: dict(
        topic="Build the pipeline steps",
        idea=(
            "The pipeline is the part that does the work, and it is easiest to trust when each step is a pure "
            "function from state to state. For the organiser, load turns the raw records into a working list, "
            "classify assigns a destination folder, plan computes the target paths, and render produces the "
            "manifest lines. Every step returns a new state dictionary rather than mutating the old one, so the "
            "state after each step can be printed and asserted. A runner that applies the steps in order and logs "
            "the name plus a small count gives you a trace of the whole run for free. Two properties are worth "
            "building in from the start: the pipeline must be deterministic, so no step reads a clock or a "
            "random source, and the pipeline must be total, so a bad record becomes a rejected entry instead of "
            "an exception that kills the run. Keeping the steps separate also means tests can exercise plan "
            "without running load, or render without running the full chain. Today you build four steps over "
            "three in-memory records and a runner that prints each stage and its item count. Compare the trace "
            "with the spec from day 166; if a step is not mentioned there, either the spec or the pipeline is "
            "wrong."
        ),
        code=(
            'def load(state):\n'
            '    records = [\n'
            '        {"name": "sales.csv", "kind": "report"},\n'
            '        {"name": "logo.png", "kind": "image"},\n'
            '        {"name": "notes.txt", "kind": "misc"},\n'
            '    ]\n'
            '    return {**state, "records": records}\n'
            '\n'
            'def classify(state):\n'
            '    folders = {"report": "reports", "image": "images", "misc": "archive"}\n'
            '    records = [{**r, "folder": folders.get(r["kind"], "archive")} for r in state["records"]]\n'
            '    return {**state, "records": records}\n'
            '\n'
            'def plan(state):\n'
            '    from pathlib import PurePosixPath\n'
            '    paths = [str(PurePosixPath("out") / r["folder"] / r["name"]) for r in state["records"]]\n'
            '    return {**state, "paths": paths}\n'
            '\n'
            'def render(state):\n'
            '    manifest = [r["name"] + " -> " + p for r, p in zip(state["records"], state["paths"])]\n'
            '    return {**state, "manifest": manifest}\n'
            '\n'
            'def run_pipeline(steps, state):\n'
            '    for step in steps:\n'
            '        state = step(state)\n'
            '        print(step.__name__, len(state.get("records", [])), "records")\n'
            '    return state\n'
            '\n'
            'final = run_pipeline([load, classify, plan, render], {})\n'
            'print("manifest:", final["manifest"])\n'
            'assert len(final["paths"]) == 3\n'
            'assert final["manifest"][0] == "sales.csv -> out/reports/sales.csv"\n'
            'print("each step is an inspectable state change")'
        ),
        variant_b='insert a validate step after load and watch the record count change',
        variant_c='run the steps in a different order and explain which ordering breaks the manifest',
        mistakes=[
            "Writing one large function, so a bad intermediate state is invisible.",
            "Mutating the shared state instead of returning a new dictionary.",
            "Letting a bad record raise and kill the whole run instead of producing a rejected entry.",
        ],
        q1=(
            "Why keep each pipeline step as a pure state-to-state function?",
            "Intermediate states are printable and testable, and a failure localises to the step that produced it.",
        ),
        homework=(
            "Write `run_pipeline(steps, state)` that applies load, classify, plan and render in order, printing "
            "each step name and record count. Run it over three in-memory records, print the final manifest, and "
            "comment which line makes the step order explicit rather than hidden in one function."
        ),
        patterns=["def ", "run_pipeline", "print("],
        mapping=(
            "Make targets, Airflow tasks and CI stages all model ordered steps with inspectable outputs; the "
            "Python pipeline is the same shape without the infrastructure."
        ),
    ),
    171: dict(
        topic="Add the schedule",
        idea=(
            "An automation without a schedule is a script that runs when someone remembers. Scheduling starts as "
            "data: a dictionary describing the time, the allowed weekdays and the catch-up policy. That object is "
            "easy to test because next_run is a pure function of the schedule and a current weekday, with no "
            "clock involved. The function walks forward day by day, wraps around the week and returns the first "
            "allowed day, so a Friday evening run with a weekday schedule resolves to Monday rather than "
            "Saturday. The catch-up policy matters in production: if the machine was off on Monday, should "
            "Tuesday's run process one missed day or all missed days? Writing the answer down early prevents "
            "duplicate archives later. Time zones are deliberately out of scope for the toy version, but the "
            "schedule should carry a time string rather than a datetime so the decision stays visible. Two "
            "assertions make the behaviour clear: every schedule produces a result within seven days, and a "
            "schedule with no allowed days is rejected as invalid. Today you build the schedule object and "
            "next_run for the nightly organiser, print the next run from a few starting days and check the "
            "weekend skip. In real deployments cron or systemd owns the clock; your job is to make the decision "
            "logic testable without it."
        ),
        code=(
            'WEEK = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]\n'
            'SCHEDULE = {"time": "02:00", "days": ["mon", "tue", "wed", "thu", "fri"], "catch_up": "one_missed_day"}\n'
            '\n'
            'def next_run(schedule, today):\n'
            '    if not schedule["days"]:\n'
            '        raise ValueError("schedule has no run days")\n'
            '    start = WEEK.index(today)\n'
            '    for offset in range(1, 8):\n'
            '        day = WEEK[(start + offset) % 7]\n'
            '        if day in schedule["days"]:\n'
            '            return offset, day, schedule["time"]\n'
            '    raise ValueError("no run day within a week")\n'
            '\n'
            'for today in ("mon", "fri", "sat"):\n'
            '    print(today, "->", next_run(SCHEDULE, today))\n'
            '\n'
            'assert next_run(SCHEDULE, "fri") == (3, "mon", "02:00")\n'
            'assert next_run(SCHEDULE, "sat")[1] == "mon"\n'
            'assert next_run(SCHEDULE, "mon")[0] == 1\n'
            'print("weekend is skipped by data, not a special case")'
        ),
        variant_b='add a "sun" run day and confirm Saturday now resolves to Sunday',
        variant_c='make an empty days list raise and catch it to print the invalid-schedule message',
        mistakes=[
            "Reading the current clock inside next_run, which makes the logic impossible to test.",
            "Hard-coding weekend special cases instead of expressing allowed days as data.",
            "Leaving the catch-up policy unstated, so a missed night is handled differently each time.",
        ],
        q1=(
            "Why should next_run take a weekday instead of reading the current time?",
            "It becomes a pure function whose weekend and wrap-around behaviour can be tested deterministically.",
        ),
        homework=(
            "Write `next_run(schedule, today)` that returns the offset, weekday and time of the next allowed run "
            "for a weekday schedule, wrapping past the weekend. Try it from Friday and Saturday, print both "
            "results, and comment which line makes the weekend skip a data decision rather than a special case."
        ),
        patterns=["def ", "next_run", "print("],
        mapping=(
            "Cron expressions, systemd timers and cloud schedulers all encode allowed days and times; keeping the "
            "decision in a testable function makes the platform a detail."
        ),
    ),
    172: dict(
        topic="Add logging and summaries",
        idea=(
            "Logging is how an unattended run explains itself after you have gone to bed. The minimum useful shape "
            "is one line per outcome with a level, an event and the identifying values, followed by a summary of "
            "counts. Levels should mean something: info for completed work, warning for a skip that deserves "
            "attention, error for a rejected or failed item, and a final summary at the end regardless of "
            "outcome. The summary is the part a scheduler and a human both read, so it should contain done, "
            "skipped and failed counts plus the exit code derived from them. A useful convention is that any "
            "failed item produces a non-zero exit code, while skips alone do not, because a skip is often a "
            "legitimate rerun. Logs should carry stable field names rather than free-form prose, so they can be "
            "grepped and later parsed. They should also avoid secrets and absolute paths that differ per machine. "
            "Keeping the logger as a function that accumulates lines into a list makes the whole thing "
            "deterministic and testable: you assert on the exact lines and the counts. Today you summarise a "
            "short list of outcomes for the organiser, print the log and summary, and assert both the counters "
            "and the exit code."
        ),
        code=(
            'LEVELS = {"done": "INFO", "skipped": "WARNING", "failed": "ERROR"}\n'
            '\n'
            'def summarise(outcomes):\n'
            '    counts = {"done": 0, "skipped": 0, "failed": 0}\n'
            '    log = []\n'
            '    for name, status, reason in outcomes:\n'
            '        counts[status] += 1\n'
            '        suffix = f" ({reason})" if reason else ""\n'
            '        log.append(f"{LEVELS[status]} {name}: {status}{suffix}")\n'
            '    return counts, log\n'
            '\n'
            'outcomes = [\n'
            '    ("sales.csv", "done", ""),\n'
            '    ("logo.png", "done", ""),\n'
            '    ("sales.csv", "skipped", "already present"),\n'
            '    ("bad.csv", "failed", "bad kind"),\n'
            ']\n'
            'counts, log = summarise(outcomes)\n'
            'for line in log:\n'
            '    print(line)\n'
            'print("summary:", counts)\n'
            'exit_code = 1 if counts["failed"] else 0\n'
            'print("exit code:", exit_code)\n'
            '\n'
            'assert counts == {"done": 2, "skipped": 1, "failed": 1}\n'
            'assert exit_code == 1\n'
            'print("counts and exit code agree")'
        ),
        variant_b='add a rejected status with its own level and include it in the exit code rule',
        variant_c='emit one summary line as key=value pairs so a log tool could parse it',
        mistakes=[
            "Logging prose with no stable fields, so the output cannot be searched or counted.",
            "Returning exit zero when items failed, which hides the failure from the scheduler.",
            "Forgetting the final summary, so a reader cannot tell what the run actually did.",
        ],
        q1=(
            "Why should skips not force a non-zero exit code while failures do?",
            "A skip is often a healthy rerun, but a failure means work was not completed and needs attention.",
        ),
        homework=(
            "Write `summarise(outcomes)` that returns done, skipped and failed counts plus log lines, and derive "
            "an exit code from the counts. Run it on four outcomes including one skip and one failure, print the "
            "log and summary, and comment which line turns the summary into an exit code."
        ),
        patterns=["def ", "summary", "print("],
        mapping=(
            "Structured logging and run summaries are what observability stacks ingest; stable levels and counts "
            "are more valuable than pretty sentences."
        ),
    ),
    173: dict(
        topic="Write the tests",
        idea=(
            "Tests for an automation are mostly assertions about pure functions, which is why the earlier days "
            "insisted on keeping parsing, planning and running separate. An assert-based test is enough to start: "
            "a function named test_something that calls the code with a fixture and asserts the property that "
            "matters. For the organiser the valuable tests are that an empty input yields an empty plan, that "
            "duplicate names produce distinct targets, and that an unknown kind lands in archive. Write the tests "
            "so they run in a fixed order from a list, print a pass line for each and a count at the end. To "
            "prove the tests can fail, include one deliberate negative check inside a try block that flips an "
            "expectation and catches AssertionError; a test suite that has never failed has not been shown to "
            "work. Avoid testing incidental details such as dictionary ordering or log wording unless those are "
            "part of the contract. The rule of thumb is one test per promise in the spec. Today you write three "
            "assert-based tests over the plan function, run them through a tiny runner, and print the results. "
            "This runner is deliberately smaller than pytest so the mechanics are visible; the real project can "
            "adopt pytest without changing the assertions."
        ),
        code=(
            'from pathlib import PurePosixPath\n'
            '\n'
            'FOLDERS = {"report": "reports", "image": "images"}\n'
            '\n'
            'def plan(records):\n'
            '    seen = set()\n'
            '    targets = []\n'
            '    for record in records:\n'
            '        target = PurePosixPath("out") / FOLDERS.get(record["kind"], "archive") / record["name"]\n'
            '        counter = 1\n'
            '        while str(target) in seen:\n'
            '            target = target.with_name(f"{target.stem}-{counter}{target.suffix}")\n'
            '            counter += 1\n'
            '        seen.add(str(target))\n'
            '        targets.append(str(target))\n'
            '    return targets\n'
            '\n'
            'def test_empty_input():\n'
            '    assert plan([]) == []\n'
            '\n'
            'def test_duplicate_renamed():\n'
            '    records = [{"name": "a.csv", "kind": "report"}, {"name": "a.csv", "kind": "report"}]\n'
            '    assert plan(records)[1].endswith("a-1.csv")\n'
            '\n'
            'def test_unknown_goes_to_archive():\n'
            '    assert plan([{"name": "x.bin", "kind": "misc"}])[0].startswith("out/archive/")\n'
            '\n'
            'tests = [test_empty_input, test_duplicate_renamed, test_unknown_goes_to_archive]\n'
            'passed = 0\n'
            'for test in tests:\n'
            '    try:\n'
            '        test()\n'
            '    except AssertionError:\n'
            '        print("FAIL", test.__name__)\n'
            '    else:\n'
            '        passed += 1\n'
            '        print("PASS", test.__name__)\n'
            'assert passed == len(tests)\n'
            'print("tests passed:", passed)'
        ),
        variant_b='add a test that an empty name is preserved and see whether the planner should reject it',
        variant_c='introduce a deliberate break in plan and confirm one test prints FAIL',
        mistakes=[
            "Testing incidental details such as dict ordering instead of the contract.",
            "Writing tests that have never failed, so nobody knows they can catch a regression.",
            "Depending on a real clock or filesystem, which makes the suite flaky.",
        ],
        q1=(
            "Why include one test that is expected to fail?",
            "It proves the runner and assertions can actually detect a broken property instead of always passing.",
        ),
        homework=(
            "Write an assert-based `test_plan(records)` that checks an empty input, a duplicate rename and an "
            "unknown kind landing in archive. Run three test functions through a tiny runner that prints PASS or "
            "FAIL, print the final count, and comment which assertion would fail first if collision handling "
            "were removed."
        ),
        patterns=["def ", "test_", "print("],
        mapping=(
            "Pytest, unittest and CI runners all execute assert-based tests; the tiny runner here shows what "
            "those tools automate."
        ),
    ),
    174: dict(
        topic="Handle the edge cases",
        idea=(
            "Edge cases are not a distraction from the happy path; they are the specification's real test. For "
            "the file organiser, the ones worth handling explicitly are an empty input list, duplicate names, an "
            "unknown kind, a zero-byte file and a file above a size limit. Each needs a named policy rather than "
            "an accident: empty input succeeds with zero counts, duplicates get a deterministic rename, an "
            "unknown kind goes to archive with a warning, an empty file is skipped with a reason, and an "
            "oversized file is rejected so a human can look at it. The important design move is that every record "
            "produces exactly one outcome, so the counts always add up to the input length. That invariant is "
            "worth an assertion in the code itself, because it catches a whole class of silent drops. Policies "
            "should also be visible in the plan and the summary, not buried in a branch, so the runbook can "
            "explain what a skip means. Finally, decide which edge cases are errors and which are normal: a rerun "
            "that skips everything is healthy, while a rejected record that nobody notices is a slow failure. "
            "Today you run the organiser's policy function over four records covering these cases, print the "
            "outcome table and assert the totals."
        ),
        code=(
            'def organise(records, limit=100):\n'
            '    outcomes = []\n'
            '    for record in records:\n'
            '        size, kind = record["size"], record["kind"]\n'
            '        if size == 0:\n'
            '            outcomes.append((record["name"], "skipped", "empty file"))\n'
            '        elif size > limit:\n'
            '            outcomes.append((record["name"], "rejected", "over limit"))\n'
            '        elif kind not in {"report", "image"}:\n'
            '            outcomes.append((record["name"], "archived", "unknown kind"))\n'
            '        else:\n'
            '            outcomes.append((record["name"], "planned", kind))\n'
            '    return outcomes\n'
            '\n'
            'records = [\n'
            '    {"name": "sales.csv", "size": 10, "kind": "report"},\n'
            '    {"name": "empty.txt", "size": 0, "kind": "misc"},\n'
            '    {"name": "huge.zip", "size": 900, "kind": "misc"},\n'
            '    {"name": "raw.bin", "size": 5, "kind": "misc"},\n'
            ']\n'
            'for name, action, reason in organise(records):\n'
            '    print(f"{name:10} {action:9} {reason}")\n'
            '\n'
            'assert len(organise(records)) == len(records)\n'
            'assert [action for _, action, _ in organise(records)] == ["planned", "skipped", "rejected", "archived"]\n'
            'print("every input has exactly one outcome")'
        ),
        variant_b='make the size limit a setting and rerun with a limit of five',
        variant_c='treat a negative size as rejected and add it to the outcome table',
        mistakes=[
            "Silently dropping a record in a branch, so the totals no longer match the input.",
            "Treating a normal rerun skip as an error instead of a healthy no-op.",
            "Burying policies in code without surfacing them in the plan or summary.",
        ],
        q1=(
            "What invariant should every edge-case policy preserve?",
            "Each input record produces exactly one outcome, so the counts always add up to the input length.",
        ),
        homework=(
            "Write `organise(records, limit=100)` that returns one outcome per record for empty, duplicate, "
            "unknown-kind and oversized cases, each with an action and a reason. Run it over five records covering "
            "those edges, print the outcome table, and comment which assertion proves that no input record was "
            "silently dropped."
        ),
        patterns=["def ", "organise", "print("],
        mapping=(
            "Production incidents cluster around empty inputs, duplicates and unknown types; naming a policy for "
            "each is what turns a demo into an automation."
        ),
    ),
    175: dict(
        topic="Polish the runbook",
        idea=(
            "A runbook is the difference between an automation you can hand over and one only you can operate. It "
            "is a short ordered document with fixed sections: pre-flight, execute, verify, rollback and "
            "escalation. Pre-flight lists the checks before a run, such as confirming the input folder and the "
            "free space. Execute names the exact command and the expected duration. Verify says which summary "
            "counts and log lines mean success. Rollback describes how to undo the run, which for the organiser "
            "means moving targets back from the manifest and never deleting anything. Escalation names who to "
            "contact and what evidence to attach. Two qualities make a runbook usable: every step is a concrete "
            "action rather than an adjective, and the rollback is tested at least once in a dry run. Keeping the "
            "runbook as an ordered list of sections in code lets a check confirm that all required sections exist "
            "and that rollback appears before escalation. It also lets the packaging step copy it with "
            "confidence. Today you build the runbook dictionary for the organiser, render it as numbered sections "
            "and assert the order and required keys. The document is small, but it is the artifact a teammate "
            "actually reads at two in the morning."
        ),
        code=(
            'def build_runbook():\n'
            '    return [\n'
            '        ("pre-flight", "confirm inbox exists and out is writable"),\n'
            '        ("execute", "run organise --inbox inbox --out out"),\n'
            '        ("verify", "check done + skipped equals inputs and failed is zero"),\n'
            '        ("rollback", "move targets back using the manifest; never delete"),\n'
            '        ("escalate", "attach the log and manifest to the on-call ticket"),\n'
            '    ]\n'
            '\n'
            'REQUIRED = ("pre-flight", "execute", "verify", "rollback", "escalate")\n'
            '\n'
            'def runbook_problems(runbook):\n'
            '    titles = [title for title, _ in runbook]\n'
            '    return [name for name in REQUIRED if name not in titles]\n'
            '\n'
            'runbook = build_runbook()\n'
            'for number, (title, action) in enumerate(runbook, start=1):\n'
            '    print(f"{number}. {title}: {action}")\n'
            'print("problems:", runbook_problems(runbook))\n'
            '\n'
            'assert runbook_problems(runbook) == []\n'
            'assert runbook_problems(runbook[:-1]) == ["escalate"]\n'
            'print("runbook is ordered data, not prose")'
        ),
        variant_b='add a "notify" section after verify and decide whether it is required',
        variant_c='remove rollback and assert the runbook check refuses the document',
        mistakes=[
            "Writing adjectives instead of concrete commands a tired operator can follow.",
            "Omitting rollback, so a bad run cannot be undone from the document alone.",
            "Leaving the runbook as prose that no check or packaging step can validate.",
        ],
        q1=(
            "Why keep the runbook as an ordered list of sections instead of prose?",
            "Order and required sections can be checked automatically and rendered consistently for the operator.",
        ),
        homework=(
            "Write `runbook_problems(runbook)` that returns the required runbook sections missing from an ordered "
            "list of (title, action) pairs. Build a five-section organiser runbook, print it with runbook_problems "
            "applied, remove rollback and print again, and comment why rollback must be documented before "
            "escalation."
        ),
        patterns=["def ", "runbook", "print("],
        mapping=(
            "SRE teams treat runbooks as production code: reviewed, versioned and tested in game days rather "
            "than written after an incident."
        ),
    ),
    176: dict(
        topic="Package and ship",
        idea=(
            "Shipping is a packaging decision as much as a coding one. A small Python tool ships well when the "
            "package has an obvious name, a semantic version, one entry point and an explicit file list. For the "
            "organiser the list is the module, the pipeline module, the tests, the README and the runbook. The "
            "package check is a pure function over that metadata: the entry point must appear in the file list, "
            "the version must look like major.minor.patch, the required third-party dependencies must be empty "
            "because the tool is stdlib only, and the runbook and README must be present. Those checks are cheap "
            "and catch the classic mistake of shipping a tool that works on your machine because a file or a "
            "dependency was never added. Keep the version bump rule simple: patch for a fix, minor for a new "
            "flag, major for a change to the input contract. The README should show one command and one expected "
            "summary line, which is usually enough. Packaging does not require a build backend to be useful; a "
            "validated manifest plus a runbook is already a shippable unit. Today you define the manifest for the "
            "organiser, validate it and print the package contents. Release tooling can come later, but the "
            "manifest is the contract with future you."
        ),
        code=(
            'PACKAGE = {\n'
            '    "name": "inbox-organiser",\n'
            '    "version": "1.0.0",\n'
            '    "entry": "organise.py",\n'
            '    "files": ["organise.py", "pipeline.py", "tests/test_plan.py", "README.md", "runbook.md"],\n'
            '    "requires": [],\n'
            '}\n'
            '\n'
            'def check_package(package):\n'
            '    problems = []\n'
            '    if package["entry"] not in package["files"]:\n'
            '        problems.append("entry missing from files")\n'
            '    parts = package["version"].split(".")\n'
            '    if len(parts) != 3 or not all(part.isdigit() for part in parts):\n'
            '        problems.append("bad version")\n'
            '    if package["requires"]:\n'
            '        problems.append("third-party dependency")\n'
            '    for name in ("README.md", "runbook.md"):\n'
            '        if name not in package["files"]:\n'
            '            problems.append(f"missing {name}")\n'
            '    return problems\n'
            '\n'
            'print("package:", PACKAGE["name"], PACKAGE["version"])\n'
            'for name in PACKAGE["files"]:\n'
            '    print(" ", name)\n'
            'print("problems:", check_package(PACKAGE))\n'
            '\n'
            'assert check_package(PACKAGE) == []\n'
            'assert "third-party dependency" in check_package({**PACKAGE, "requires": ["requests"]})\n'
            'print("ready to ship")'
        ),
        variant_b='bump the version to 1.1.0 for a new --limit flag and assert it still validates',
        variant_c='add a CHANGELOG.md requirement and check the manifest before and after adding it',
        mistakes=[
            "Shipping without listing the entry point, so the tool works only from the source checkout.",
            "Forgetting to declare a dependency, so the tool fails on a clean machine.",
            "Bumping the minor version for a contract change that should be major.",
        ],
        q1=(
            "What makes a validated package manifest better than a folder of scripts?",
            "It states the entry point, files, version and dependencies, so a missing piece is caught before release.",
        ),
        homework=(
            "Write `check_package(package)` that validates that the entry point is listed, the version looks like "
            "major.minor.patch, README and runbook are present, and there are no third-party requires. Run it on "
            "the organiser manifest and on a copy with requests added, print both problem lists, and comment which "
            "check keeps the tool stdlib-only."
        ),
        patterns=["def ", "check_package", "print("],
        mapping=(
            "PyPI metadata, wheels and Docker images all encode the same promises: entry point, version, files "
            "and dependencies, checked before anyone installs them."
        ),
    ),
    177: dict(
        topic="Build day: dry-run review",
        idea=(
            "A dry-run review is the last cheap chance to stop a bad change. The idea is to treat the computed "
            "plan as a proposal and pass it through a small gate before execution. The gate reads each planned "
            "operation and applies explicit rules: creates and moves within the output root are allowed, "
            "overwrites are allowed only when force is set, and deletes are always vetoed. Every veto carries a "
            "reason and the offending path, so the reviewer sees exactly what would have gone wrong. The result "
            "is a decision object with approved, vetoes and a count, which the CLI can turn into an exit code. "
            "This is deliberately stricter than trusting the plan, because the plan says what will happen while "
            "the gate says what is acceptable. Reviewing a dry run also checks the plan's shape: the number of "
            "operations should match the input count, and no target should sit outside the output root. Those two "
            "checks catch most path traversal and accounting mistakes. Today you build review_plan over a plan "
            "containing a delete and an unsafe overwrite, print the vetoes and assert the run is blocked. Then "
            "flip the plan to safe operations and assert approval. This gate is what makes unattended execution "
            "defensible."
        ),
        code=(
            'PLAN = [\n'
            '    {"op": "create", "path": "out/reports/sales.csv"},\n'
            '    {"op": "overwrite", "path": "out/reports/old.csv"},\n'
            '    {"op": "delete", "path": "out/archive/raw.bin"},\n'
            ']\n'
            '\n'
            'def review_plan(plan, force=False):\n'
            '    vetoes = []\n'
            '    for item in plan:\n'
            '        if item["op"] == "delete":\n'
            '            vetoes.append("delete denied: " + item["path"])\n'
            '        elif item["op"] == "overwrite" and not force:\n'
            '            vetoes.append("overwrite needs --force: " + item["path"])\n'
            '        elif not item["path"].startswith("out/"):\n'
            '            vetoes.append("outside output root: " + item["path"])\n'
            '    return {"approved": not vetoes, "vetoes": vetoes}\n'
            '\n'
            'result = review_plan(PLAN)\n'
            'print("approved:", result["approved"])\n'
            'for veto in result["vetoes"]:\n'
            '    print("VETO", veto)\n'
            '\n'
            'assert result["approved"] is False and len(result["vetoes"]) == 2\n'
            'safe = [item for item in PLAN if item["op"] == "create"]\n'
            'assert review_plan(safe)["approved"] is True\n'
            'print("safe plan approved")'
        ),
        variant_b='allow overwrite when force is true and show the delete is still vetoed',
        variant_c='add a move operation whose target escapes out/ and assert it is vetoed',
        mistakes=[
            "Treating the dry run as informational instead of enforcing its vetoes.",
            "Allowing deletes because the plan looked correct on the happy path.",
            "Forgetting to check that targets stay inside the output root.",
        ],
        q1=(
            "Why must the review gate run before execution rather than inside it?",
            "It can block the whole plan cheaply and consistently before any file operation happens.",
        ),
        homework=(
            "Write `review_plan(plan, force=False)` that vetoes deletes, unforced overwrites and paths outside "
            "the output root, returning approved plus veto reasons. Run it on a plan with three operations "
            "including one delete and one overwrite, print the vetoes, then review a safe plan and comment which "
            "rule makes unattended execution defensible."
        ),
        patterns=["def ", "review_plan", "print("],
        mapping=(
            "Terraform plan, Kubernetes admission controllers and CI policy gates all refuse risky changes before "
            "they are applied; this is the same gate in miniature."
        ),
    ),
    178: dict(
        topic="Build day: final review",
        idea=(
            "The final review is a gate, not a feeling. Before shipping, list the checks that matter as data: "
            "tests pass, the dry run was reviewed, the runbook exists, the rollback is documented and the tool "
            "performs no deletes. Each check has a name, a state and a flag saying whether it blocks release. "
            "The sign-off function returns approved plus the list of blocking failures, and the CLI refuses to "
            "ship while any blocker remains. Making the checklist data means the same review can be run in CI "
            "later, and it prevents the common failure where the last fix quietly breaks an earlier promise. A "
            "useful rule is that a non-blocking warning must still be printed and recorded, so it cannot vanish. "
            "Reviewers should also see the version and the planned operations count next to the decision, "
            "because context makes a pass believable. If a blocker fails, the fix belongs in the code or the "
            "runbook, never in the checklist. Today you run sign_off over a checklist with one failing blocker, "
            "print the decision and assert it is rejected, then fix the state and assert approval. This is the "
            "same shape as a pull-request gate or a release checklist, reduced to one dictionary."
        ),
        code=(
            'CHECKS = {\n'
            '    "tests": ("pass", True),\n'
            '    "dry_run_reviewed": ("pass", True),\n'
            '    "runbook": ("pass", True),\n'
            '    "rollback_documented": ("pass", False),\n'
            '    "no_deletes": ("pass", True),\n'
            '}\n'
            '\n'
            'def sign_off(checks):\n'
            '    blockers = [name for name, (state, blocking) in checks.items() if blocking and state != "pass"]\n'
            '    warnings = [name for name, (state, blocking) in checks.items() if not blocking and state != "pass"]\n'
            '    return {"approved": not blockers, "blockers": blockers, "warnings": warnings}\n'
            '\n'
            'for name, (state, blocking) in CHECKS.items():\n'
            '    print(f"{name:20} {state:6} {\'blocking\' if blocking else \'warning\'}")\n'
            'print("decision:", sign_off(CHECKS))\n'
            '\n'
            'assert sign_off(CHECKS)["approved"] is True\n'
            'broken = {**CHECKS, "tests": ("fail", True)}\n'
            'assert sign_off(broken)["approved"] is False\n'
            'assert sign_off(broken)["blockers"] == ["tests"]\n'
            'print("a failing blocker stops the release")'
        ),
        variant_b='mark rollback as blocking and show the decision changes when it fails',
        variant_c='add a warning-only check and assert it appears without blocking sign-off',
        mistakes=[
            "Fixing the checklist instead of the failing check, which hides the real problem.",
            "Dropping warning-only failures so nobody can see them later.",
            "Reviewing without the version or operation count, so a pass has no context.",
        ],
        q1=(
            "Why should a blocking failure stop sign-off even if every other check passes?",
            "A release with a known broken promise is not safe; one unmet blocker can invalidate the whole run.",
        ),
        homework=(
            "Write `sign_off(checks)` that returns approved, blockers and warnings for a dict of check states "
            "with blocking flags. Run it on a checklist with tests failing, print the decision, then fix the "
            "state and print the approved decision, and comment why a failing blocker must stop the release."
        ),
        patterns=["def ", "sign_off", "print("],
        mapping=(
            "Release checklists, PR gates and change-advisory boards use the same blocking-versus-warning "
            "distinction to make go/no-go decisions auditable."
        ),
    ),
    179: dict(
        topic="Ship: retrospective and next steps",
        idea=(
            "A retrospective closes the loop and decides what happens next. The useful format is short: metrics "
            "from the actual runs, what to keep, what to stop and what to start, plus action items with a named "
            "owner and a due date. Metrics should come from the run summary rather than impressions, for example "
            "five runs, forty items processed, one failure and an estimated thirty minutes saved. Keep statements "
            "name a practice worth preserving, such as the dry-run review. Stop statements name a real cost, "
            "such as manual date handling. Start statements become the next iteration's scope. Every action item "
            "needs an owner and a due date, otherwise it is a wish; an assertion that all actions carry both "
            "turns that rule into code. It is also worth recording the version that shipped and the next review "
            "date. The retrospective is not a status report; it is the input to the next spec, which is why it "
            "belongs beside the scope document from day 165. Today you build the retrospective dictionary for the "
            "organiser, validate the action items and print the sections. Then choose one start item and make it "
            "the first line of the next scope, closing the capstone loop."
        ),
        code=(
            'RUN = {"runs": 5, "items": 40, "failed": 1, "minutes_saved": 30}\n'
            'RETRO = {\n'
            '    "keep": ["dry-run review before every run"],\n'
            '    "stop": ["editing dated constants by hand"],\n'
            '    "start": ["add a checksum to the manifest"],\n'
            '    "actions": [\n'
            '        {"action": "add checksum", "owner": "dev", "due": "2026-10-26"},\n'
            '        {"action": "schedule weekly review", "owner": "ops", "due": "2026-11-02"},\n'
            '    ],\n'
            '}\n'
            '\n'
            'def retro_problems(retro):\n'
            '    problems = []\n'
            '    for key in ("keep", "stop", "start", "actions"):\n'
            '        if not retro.get(key):\n'
            '            problems.append(f"empty {key}")\n'
            '    for action in retro["actions"]:\n'
            '        if not action.get("owner") or not action.get("due"):\n'
            '            problems.append(f"action without owner/due: {action.get(\'action\')}")\n'
            '    return problems\n'
            '\n'
            'print("runs:", RUN["runs"], "items:", RUN["items"], "failed:", RUN["failed"])\n'
            'for key in ("keep", "stop", "start"):\n'
            '    print(key + ":", "; ".join(RETRO[key]))\n'
            'print("actions:", len(RETRO["actions"]))\n'
            'print("problems:", retro_problems(RETRO))\n'
            '\n'
            'assert retro_problems(RETRO) == []\n'
            'assert retro_problems({**RETRO, "actions": [{"action": "x"}]}) == ["action without owner/due: x"]\n'
            'print("retrospective feeds the next spec")'
        ),
        variant_b='add a "shipped_version" key and require it in retro_problems',
        variant_c='remove the keep section and confirm the retrospective is refused',
        mistakes=[
            "Recording actions without an owner or a due date, so nothing ever happens.",
            "Writing impressions instead of metrics taken from the run summary.",
            "Treating the retrospective as a status report rather than input to the next scope.",
        ],
        q1=(
            "Why must every retrospective action have an owner and a due date?",
            "Without both, the action is a wish that nobody is accountable for completing.",
        ),
        homework=(
            "Write `retro_problems(retro)` that checks for non-empty keep, stop, start and actions sections and "
            "requires every action to carry an owner and a due date. Run it on the organiser retrospective and on "
            "one action missing its owner, print both problem lists, and comment which check turns a wish into an "
            "action."
        ),
        patterns=["def ", "retro", "print("],
        mapping=(
            "Sprint retrospectives and post-incident reviews turn observations into owned follow-up work; the "
            "same discipline keeps an automation improving after it ships."
        ),
    ),
})
