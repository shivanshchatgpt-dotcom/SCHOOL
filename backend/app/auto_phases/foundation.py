"""Automation / Scripting foundations, days 9-14: tasks as data you can test.

Every example is stdlib-only, offline and deterministic: paths use
`pathlib.PurePosixPath` (no filesystem access), configuration is plain dicts,
and the "tasks" are functions over in-memory data. The domain phases keep the
same discipline, so an automation can be planned, run and asserted on without
touching a real disk, a real clock or a real shell.
"""

FOUNDATION = {
    9: dict(
        topic="Paths as data",
        idea=(
            "Before a script can move, rename or read a file, it has to build a path, and building paths with "
            "string concatenation is the source of a hundred small bugs: a missing separator, a suffix replaced "
            "by accident, a name that only works on one operating system. `pathlib` exists so that a path is a "
            "value with methods, and `PurePosixPath` gives you those methods without ever touching a disk, which "
            "makes it perfect for planning and for tests. You can ask a path for its name, its suffix, its stem "
            "and its parent, and you compose one with the `/` operator. The mindset shift is that an automation "
            "should first compute the paths it intends to use and print them, and only then act on them. That "
            "planning step catches almost every mistake before anything is moved. Today you build paths, swap "
            "suffixes and derive output names, all in memory. Everything later in the track — scanning folders, "
            "renaming batches, writing reports — is built on getting paths right, so it is worth being precise "
            "here rather than clever."
        ),
        code=(
            'from pathlib import PurePosixPath\n'
            '\n'
            'source = PurePosixPath("reports/2026/q1/sales.csv")\n'
            'print("name:", source.name)\n'
            'print("stem:", source.stem)\n'
            'print("suffix:", source.suffix)\n'
            'print("parent:", source.parent)\n'
            '\n'
            'archive = source.parent / "archive" / source.name\n'
            'renamed = source.with_suffix(".backup")\n'
            'print("archive:", archive)\n'
            'print("renamed:", renamed)\n'
            '\n'
            'assert source.stem == "sales" and source.suffix == ".csv"\n'
            'assert renamed.name == "sales.backup"\n'
            'assert str(archive) == "reports/2026/q1/archive/sales.csv"\n'
            'print("paths are values, not string concatenation")'
        ),
        variant_b='take a file "invoice.tar.gz" and print its name, stem and suffixes to see how suffixes behaves',
        variant_c='derive "sales_report.csv" from the source name and assert the folder is unchanged',
        mistakes=[
            "Joining paths with string concatenation, so a missing separator only shows up at runtime.",
            "Using plain string replace on the extension, which also rewrites dots inside the filename.",
            "Assuming Windows separators work everywhere instead of using pathlib's composition.",
        ],
        q1=(
            "Why plan and print paths before acting on them?",
            "A wrong path is visible immediately in the plan, so the mistake is caught before any file is moved or overwritten.",
        ),
        homework=(
            "Write `output_path(source, suffix=\"_report\")` that returns a sibling path with the extra suffix "
            "added to the stem and the same extension. Try it on two inputs with different folders, print both "
            "results, and comment which line keeps the parent folder unchanged."
        ),
        patterns=["from pathlib", "def ", "print("],
        mapping=(
            "`shutil`, `os.path` and `glob` all interoperate with pathlib; teams migrating scripts to pathlib "
            "usually fix a class of platform bugs as a side effect."
        ),
    ),
    10: dict(
        topic="Arguments and configuration",
        idea=(
            "An automation that hard-codes its folders and dates is impossible to schedule or reuse. The fix is "
            "to separate what the script does from the values it runs with, and to treat arguments as data: a "
            "dictionary of parsed options with defaults, validation and provenance. Whether those values arrive "
            "from the command line, an environment variable or a config file, the rest of the script should read "
            "them from one structure. An important rule is precedence: command-line flags beat environment "
            "variables, which beat config file defaults, so a one-off override does not require editing a shared "
            "file. Just as important is validation up front; a script that discovers its output folder is "
            "missing after an hour of work has wasted the hour. Today you build a tiny parser that turns a list "
            "of flag strings into a settings dictionary with defaults, then validate it. Nothing here needs "
            "`argparse` yet, because the goal is to see that arguments are just key-value data. Once that is "
            "clear, swapping in a real parser is mechanical, and testing the script no longer means invoking a "
            "shell."
        ),
        code=(
            'DEFAULTS = {"input": "reports", "output": "out", "dry_run": False}\n'
            '\n'
            'def parse(args, defaults):\n'
            '    settings = dict(defaults)\n'
            '    for token in args:\n'
            '        if token == "--dry-run":\n'
            '            settings["dry_run"] = True\n'
            '        elif token.startswith("--input="):\n'
            '            settings["input"] = token.split("=", 1)[1]\n'
            '        elif token.startswith("--output="):\n'
            '            settings["output"] = token.split("=", 1)[1]\n'
            '    return settings\n'
            '\n'
            'def validate(settings):\n'
            '    problems = []\n'
            '    if not settings["input"]:\n'
            '        problems.append("input folder is empty")\n'
            '    return problems\n'
            '\n'
            'settings = parse(["--input=inbox", "--dry-run"], DEFAULTS)\n'
            'print("settings:", settings)\n'
            'print("problems:", validate(settings))\n'
            '\n'
            'assert settings["input"] == "inbox" and settings["dry_run"] is True\n'
            'assert validate({"input": "", "output": "out", "dry_run": False}) == ["input folder is empty"]'
        ),
        variant_b='add an "--output-dir=" flag and confirm the default is used when it is absent',
        variant_c='read a value from an env-like dict and make it win over the default but lose to a flag',
        mistakes=[
            "Reaching into `sys.argv` from deep inside the logic instead of parsing once into a settings dict.",
            "Discovering invalid or missing settings halfway through the run instead of validating first.",
            "Mixing precedence so a config default silently overrides an explicit command-line flag.",
        ],
        q1=(
            "Why should flags beat environment variables, which beat config defaults?",
            "The most explicit, local choice should win, so a one-off override works without editing shared configuration.",
        ),
        homework=(
            "Write `parse(args, defaults)` that returns settings for input, output and a dry-run flag, plus "
            "`validate(settings)` returning a list of problems. Parse one token list with a flag and check the "
            "default path when it is absent, print both, and comment which line preserves the default."
        ),
        patterns=["def ", "dict(defaults)", "print("],
        mapping=(
            "`argparse`, `click` and `typer` formalise this, and `os.environ` plus a config module provide the "
            "other sources; the settings dict is the seam between them and the work."
        ),
    ),
    11: dict(
        topic="Tasks in order",
        idea=(
            "Automation is a sequence of steps over data, and the cleanest way to write it is a list of steps "
            "where each step is a function that takes the current state and returns a new one. This is the pipe "
            "pattern, and its main virtue is that every intermediate state is a value you can inspect, print and "
            "assert on. When something goes wrong you can see exactly which step produced the bad state, instead "
            "of debugging one hundred lines of interleaved mutation. It also makes the script composable: "
            "reordering steps or inserting a new one is a list edit, not a refactor. Two details matter in "
            "practice. A step should be idempotent or clearly marked otherwise, so running the pipeline twice "
            "does not duplicate work. And a step should report a small result — how many items it handled or "
            "skipped — so the run log can explain what happened. Today you build a pipeline runner and three "
            "tiny steps that transform a list of records, printing the state after each. This is the skeleton "
            "for every later phase: scheduling decides when to run it, errors and logging wrap each step, and "
            "tests run the pipeline over fixtures."
        ),
        code=(
            'def load(state):\n'
            '    return {**state, "rows": [" a ", "b", ""]}\n'
            '\n'
            'def clean(state):\n'
            '    rows = [r.strip() for r in state["rows"] if r.strip()]\n'
            '    return {**state, "rows": rows}\n'
            '\n'
            'def upper(state):\n'
            '    return {**state, "rows": [r.upper() for r in state["rows"]]}\n'
            '\n'
            'def run_pipeline(steps, state):\n'
            '    for step in steps:\n'
            '        state = step(state)\n'
            '        print(step.__name__, "->", state)\n'
            '    return state\n'
            '\n'
            'final = run_pipeline([load, clean, upper], {})\n'
            'assert final["rows"] == ["A", "B"]\n'
            'print("each step is a value transformation")'
        ),
        variant_b='add a "count" key updated by each step and print how the count changes down the pipeline',
        variant_c='put the steps in a different order and explain which orderings are wrong and why',
        mistakes=[
            "Interleaving all the work in one function, so a bad intermediate state is invisible.",
            "Writing steps that mutate a shared list instead of returning new state.",
            "Making steps non-idempotent without marking it, so a retry duplicates records.",
        ],
        q1=(
            "Why write automation as a list of state-to-state step functions?",
            "Each intermediate state is inspectable and testable, failures localise to a step, and steps can be reordered or reused.",
        ),
        homework=(
            "Write `run_pipeline(steps, state)` that applies each step in order and returns the final state, "
            "printing progress. Add a load step, a clean step and a compute step over a list, run them, print "
            "the final state, and comment which line makes the order explicit."
        ),
        patterns=["def ", "for ", "return"],
        mapping=(
            "Makefiles, Airflow DAGs and shell pipelines all express this idea of ordered steps over data; the "
            "Python version is the same concept with inspectable state."
        ),
    ),
    12: dict(
        topic="Idempotent operations",
        idea=(
            "An automation that is safe to run twice is worth far more than one that is not, because reruns "
            "happen: a job fails halfway, someone triggers it manually, a scheduler fires twice. Idempotence "
            "means the result of running the operation once or many times is the same. For file-like work the "
            "usual technique is a marker: check whether the output already exists and is current before doing "
            "the work, and skip when it is. The subtle part is deciding what makes an item 'already done' — a "
            "name, a size, a checksum, a recorded timestamp — because a too-weak check silently skips needed "
            "work, while a too-strong one never skips and wastes time. The honest approach is to compute a key "
            "for each item from its inputs, record the keys that succeeded, and skip only those. That record is "
            "also your audit trail and your resume point. Today you build a small processed-keys store and a "
            "loop that skips known keys and records new ones, printing what was done and what was skipped. Notice "
            "that the store is just data, so the whole behaviour is testable without a scheduler or a disk."
        ),
        code=(
            'def is_done(store, key):\n'
            '    return key in store\n'
            '\n'
            'def process(item, store):\n'
            '    key = item.lower().strip()\n'
            '    if is_done(store, key):\n'
            '        return store, "skipped"\n'
            '    store = {**store, key: "ok"}\n'
            '    return store, "done"\n'
            '\n'
            'store = {}\n'
            'items = ["Alpha", " beta ", "Alpha"]\n'
            'results = []\n'
            'for item in items:\n'
            '    store, result = process(item, store)\n'
            '    results.append((item, result))\n'
            '\n'
            'for item, result in results:\n'
            '    print(f"{item!r:9} -> {result}")\n'
            '\n'
            'assert results[-1][1] == "skipped"\n'
            'assert len(store) == 2\n'
            'print("a rerun does the same work exactly once")'
        ),
        variant_b='store the key plus a checksum of the content and only skip when both match',
        variant_c='make the store persist as a JSON string and reload it before the second run',
        mistakes=[
            "Using a check so weak (just the output name) that changed inputs are silently skipped.",
            "Recording success before the work actually finishes, so a crash marks failed items as done.",
            "Rebuilding the processed set on every run instead of persisting it between runs.",
        ],
        q1=(
            "What makes a good key for deciding an item is already done?",
            "It must change whenever the inputs change, so a completed item is skipped while a modified one is reprocessed.",
        ),
        homework=(
            "Write `process_all(items, store)` that skips items whose normalised key is already recorded and "
            "returns the updated store plus a list of per-item results. Run it on a list containing a "
            "duplicate, print the results for each run, and comment which line makes the second run a no-op."
        ),
        patterns=["def ", "in store", "print("],
        mapping=(
            "Build systems, ETL tools and backup scripts all track processed keys; the idea is the same whether "
            "the store is a file, a database table or a set in memory."
        ),
    ),
    13: dict(
        topic="Errors, logs and exit codes",
        idea=(
            "The difference between a script and an automation is how it behaves when something goes wrong. A "
            "useful automation isolates failures per item, records what happened, and reports a meaningful exit "
            "code, so a scheduler can tell success from partial success from failure. The core discipline is to "
            "catch only the errors you understand, at the level where you can do something about them, and to "
            "let the rest propagate rather than swallowing everything with a bare except. Each handled failure "
            "should produce a log line with enough context to act on, and each run should end with a summary: "
            "how many items succeeded, failed and were skipped. Exit codes turn that summary into something "
            "another program can use: zero for fully successful, non-zero for anything that needs attention. "
            "Today you build a per-item runner that catches a specific error, logs it, and returns a summary and "
            "an exit code. The logs here are just strings in a list, which keeps the lesson deterministic while "
            "teaching the exact shape a real logger produces. This is the layer that makes automation "
            "trustworthy enough to schedule unattended."
        ),
        code=(
            'def run_item(item):\n'
            '    return int(item)\n'
            '\n'
            'def run_all(items):\n'
            '    summary = {"ok": 0, "failed": 0}\n'
            '    log = []\n'
            '    for item in items:\n'
            '        try:\n'
            '            value = run_item(item)\n'
            '        except ValueError as error:\n'
            '            summary["failed"] += 1\n'
            '            log.append(f"item {item!r} failed: {error}")\n'
            '            continue\n'
            '        summary["ok"] += 1\n'
            '        log.append(f"item {item!r} -> {value}")\n'
            '    return summary, log\n'
            '\n'
            'summary, log = run_all(["1", "two", "3"])\n'
            'for line in log:\n'
            '    print(line)\n'
            'print("summary:", summary)\n'
            'exit_code = 0 if summary["failed"] == 0 else 1\n'
            'print("exit code:", exit_code)\n'
            '\n'
            'assert summary == {"ok": 2, "failed": 1} and exit_code == 1'
        ),
        variant_b='add a "skipped" counter for empty strings and include it in the summary and exit code',
        variant_c='catch two different error types and prefix each log line with the error kind',
        mistakes=[
            "Using a bare `except` that swallows programming errors as if they were bad data.",
            "Failing the whole run on the first bad item instead of isolating it.",
            "Always returning exit code zero, so a scheduler cannot detect a partial failure.",
        ],
        q1=(
            "Why catch a specific error type rather than using a bare except?",
            "A bare except hides bugs in the code itself along with expected bad data, making real failures invisible.",
        ),
        homework=(
            "Write `run_all(items)` that processes each item, records successes and failures in a summary and a "
            "log, and returns an exit code. Run it on a list with two good and one bad item, print the log and "
            "summary, and comment which line turns the summary into an exit code."
        ),
        patterns=["try", "except", "print("],
        mapping=(
            "Cron, systemd and CI runners read exit codes to decide whether to alert; structured logs plus a "
            "summary are what make that possible."
        ),
    ),
    14: dict(
        topic="A tiny automation, end to end",
        idea=(
            "Today you connect the week: parse settings from argument tokens, plan the paths you will touch, run "
            "a pipeline of steps over items, keep a processed store so reruns are safe, and finish with a "
            "summary and an exit code. It is a small script, but it has every part a real automation needs, and "
            "it runs entirely on in-memory data so it is fast and reproducible. Notice how the pieces reinforce "
            "each other. Settings make the paths configurable, the path plan makes the intended work visible "
            "before it happens, the pipeline keeps each state inspectable, the processed store makes the second "
            "run a no-op, and the summary turns the outcome into something a scheduler can act on. If you had to "
            "name the single habit that separates a fragile script from a dependable one, it would be making "
            "reruns safe and outcomes observable. Keep that in mind as the domain phases add real folder scans, "
            "scheduling, retries and packaging; the structure you build today is the one they extend, not "
            "replace. The capstone at the end will look like a larger version of this exact shape."
        ),
        code=(
            'def parse(args, defaults):\n'
            '    settings = dict(defaults)\n'
            '    for token in args:\n'
            '        if token == "--dry-run":\n'
            '            settings["dry_run"] = True\n'
            '        elif token.startswith("--input="):\n'
            '            settings["input"] = token.split("=", 1)[1]\n'
            '    return settings\n'
            '\n'
            'def plan(settings):\n'
            '    from pathlib import PurePosixPath\n'
            '    source = PurePosixPath(settings["input"]) / "data.csv"\n'
            '    return [str(source), str(source.parent / "archive" / source.name)]\n'
            '\n'
            'def run(items, settings):\n'
            '    seen = set()\n'
            '    summary = {"done": 0, "skipped": 0}\n'
            '    for item in items:\n'
            '        key = item.strip().lower()\n'
            '        if key in seen:\n'
            '            summary["skipped"] += 1\n'
            '            continue\n'
            '        seen.add(key)\n'
            '        summary["done"] += 1\n'
            '    return summary\n'
            '\n'
            'settings = parse(["--input=reports/2026", "--dry-run"], {"input": ".", "dry_run": False})\n'
            'paths = plan(settings)\n'
            'summary = run(["a", " a ", "b"], settings)\n'
            'print("settings:", settings)\n'
            'print("plan:", paths)\n'
            'print("summary:", summary)\n'
            '\n'
            'assert settings["dry_run"] is True\n'
            'assert paths[0] == "reports/2026/data.csv"\n'
            'assert summary == {"done": 2, "skipped": 1}'
        ),
        variant_b='make the dry-run flag skip the run entirely and confirm the summary becomes empty',
        variant_c='add a "failed" count for a value that cannot be processed and adjust the exit code',
        mistakes=[
            "Doing the work before printing the path plan, so a mistake cannot be caught cheaply.",
            "Mixing parsing, planning and running in one function, so none can be tested alone.",
            "Forgetting the processed store, so a rerun double-counts the work.",
        ],
        q1=(
            "Why print the plan before running the pipeline?",
            "It makes the intended filesystem changes reviewable and catches path mistakes before any work or mutation happens.",
        ),
        homework=(
            "Write `automate(args, items)` that parses settings, returns a path plan and runs the items with a "
            "seen-set, then returns settings, plan and summary. Call it twice with the same items, print both "
            "summaries, and comment which lines make the second call differ from the first."
        ),
        patterns=["def ", "summary", "print("],
        mapping=(
            "This is the shape of a production automation: configurable, idempotent, inspectable and "
            "schedulable, with the details scaled up by the later phases."
        ),
    ),
}
