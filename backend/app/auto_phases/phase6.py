PHASE = (
    "Testing, Packaging and DevOps",
    "Turn a working automation script into a tested, packaged and releasable tool using checks that run deterministically without a real disk, clock or network.",
    {
        150: dict(
            topic="Orientation: shipping a script",
            idea=(
                "Shipping a script is a different skill from writing one. A script that runs on your machine becomes "
                "shippable when someone else can run it without asking you questions: it states what it needs, refuses "
                "bad input early, prints a short summary, and exits with a meaningful status. Think of it as a small "
                "product with a contract. The contract includes the files it reads and writes, the settings it "
                "accepts, the output format, and the exit codes. Writing that contract down before the last line of "
                "code is written turns vague hopes into checks. Today you model that contract as data: a list of "
                "capabilities a shippable automation must have, and a tiny function that inspects a description of a "
                "script and reports what is missing. The point is not the checker itself, but the habit of making "
                "readiness measurable. A checklist you can run beats a feeling that the script is probably fine. In "
                "the coming days each item on this list gets its own technique: tests, fakes, golden outputs, "
                "linting, packaging, entry points, dependency pinning, secret handling, CI and versioning. By the end "
                "you will have a complete release routine for small tools. The exercise is deliberately modest, "
                "because shipping discipline is built from small, repeatable checks rather than one heroic review."
            ),
            code=(
                'CHECKS = [\n'
                '    "parses settings",\n'
                '    "validates input",\n'
                '    "prints summary",\n'
                '    "exits nonzero on failure",\n'
                ']\n'
                '\n'
                'def ship(script):\n'
                '    report = [(name, name in script.get("features", [])) for name in CHECKS]\n'
                '    return report, all(flag for _, flag in report)\n'
                '\n'
                'script = {\n'
                '    "name": "archive_reports",\n'
                '    "features": ["parses settings", "validates input", "prints summary"],\n'
                '}\n'
                'report, ok = ship(script)\n'
                'for name, flag in report:\n'
                '    print("ok" if flag else "missing", "-", name)\n'
                'print("shippable:", ok)\n'
                '\n'
                'assert ok is False\n'
                'assert [n for n, f in report if not f] == ["exits nonzero on failure"]'
            ),
            variant_b='add a "documents settings" capability to the checklist and mark it missing',
            variant_c='describe a second script with every capability and assert it is shippable',
            mistakes=[
                "Treating a script that works locally as shipped, without stating its inputs and exit codes.",
                "Writing a checklist nobody runs instead of making readiness a function that returns data.",
                "Adding capabilities without updating the tests that decide whether the script is ready.",
            ],
            q1=(
                "Why model shipping readiness as data instead of a feeling?",
                "A data checklist can be run and asserted on, so gaps are visible and a release decision is repeatable.",
            ),
            homework=(
                "Write `ship(script)` that compares a script description against a checklist and returns a report "
                "plus a boolean. Describe two scripts, one missing two capabilities, print both reports, and "
                "comment which line turns the checklist into a release decision."
            ),
            patterns=["def ship", "CHECKS", "print("],
            mapping=(
                "Release checklists in CI are the same idea scaled up: `pytest`, `tox`, `ruff` and a build job each "
                "turn one readiness claim into a command that can fail."
            ),
        ),
        151: dict(
            topic="Unit tests for tasks",
            idea=(
                "A unit test is a small, fast, deterministic check of one behaviour through a public seam. The best "
                "first tests are not clever; they call a function with an input you chose, compare the result to an "
                "expected value, and stop. `assert` is enough to start, because a failing assertion prints the "
                "expression that went wrong and the values involved. The important discipline is choosing the seam. "
                "Test a pure function that takes data and returns data, not a function that reaches into global state "
                "or the filesystem, and the test needs no setup at all. Write the test before or after the code, but "
                "write it against the behaviour you intend, not the implementation you happened to produce. Keep one "
                "reason to fail per test, name tests after the behaviour, and include the empty and malformed cases "
                "that occur in real inputs. A test suite that is slow or flaky stops being run, so speed and "
                "determinism are features, not luxuries. Today you write a normaliser and a handful of "
                "assertion-based tests for it, including the empty string and extra whitespace. Notice how each test "
                "documents one rule and how the failure message points directly at the broken rule. This is the "
                "foundation every later testing technique builds on."
            ),
            code=(
                'def normalise(name):\n'
                '    return "-".join(part for part in name.lower().split() if part)\n'
                '\n'
                'def test_basic():\n'
                '    assert normalise("Q1 Sales") == "q1-sales"\n'
                '\n'
                'def test_whitespace():\n'
                '    assert normalise("  Alpha   Beta  ") == "alpha-beta"\n'
                '\n'
                'def test_empty():\n'
                '    assert normalise("   ") == ""\n'
                '\n'
                'tests = [test_basic, test_whitespace, test_empty]\n'
                'for test in tests:\n'
                '    test()\n'
                '    print("passed:", test.__name__)\n'
                '\n'
                'assert normalise("A B") == normalise(" a  b ")\n'
                'print("all", len(tests), "tests passed")'
            ),
            variant_b='add a case that strips slashes before joining and assert "a/b" becomes "ab"',
            variant_c='write a test that pins the collision between "A B" and "a-b" and explains the rule',
            mistakes=[
                "Testing private helpers instead of the public behaviour the task promises.",
                "Writing one huge test with many unrelated assertions, so a failure hides the real rule.",
                "Depending on the current directory or clock so the test passes only on one machine.",
            ],
            q1=(
                "What makes a good first unit test?",
                "One behaviour, one deterministic input, one expected result, and a failure message that names the rule that broke.",
            ),
            homework=(
                "Write `normalise(name)` plus at least three `test_` functions using plain asserts, and a `run_tests` "
                "function that calls each and prints its name. Cover whitespace, an empty string and mixed case, then "
                "comment which test would fail if the lowercasing were removed."
            ),
            patterns=["def normalise", "assert", "def test_"],
            mapping=(
                "`pytest` discovers the same `test_` functions and reports assertion values; starting with plain "
                "asserts makes the transition a matter of installing a runner, not rewriting the suite."
            ),
        ),
        152: dict(
            topic="Fakes for filesystem and clock",
            idea=(
                "Tests become slow and flaky when they touch the real world, and code becomes hard to test when it "
                "reaches for the real world internally. The fix is dependency injection with a very small surface: "
                "pass the filesystem operations and the clock in as values instead of calling them inside the task. "
                "For a filesystem, a dictionary from path to text is a complete fake for read, write, exists and "
                "list, and it is reset for free at the start of every test. For a clock, pass a function that "
                "returns a fixed timestamp, so a report header or an expiry decision is reproducible. This is not "
                "mocking frameworks; it is just data and callables. The design pressure is healthy: if a task only "
                "needs `read`, `write` and `now`, the code says so, and a real adapter can wrap `pathlib` and the "
                "system clock at the edge. Keep fakes honest by implementing only the operations the task uses and "
                "by making failures explicit, such as raising `KeyError` on a missing path. Today you build a "
                "dict-backed fake filesystem and a fixed clock, then run a small task against both and assert the "
                "recorded output. Because nothing is real, the test can check the exact bytes written and the exact "
                "timestamp, which is usually impossible against a live disk and wall clock."
            ),
            code=(
                'def write(fs, path, text):\n'
                '    fs = dict(fs)\n'
                '    fs[path] = text\n'
                '    return fs\n'
                '\n'
                'def read(fs, path):\n'
                '    if path not in fs:\n'
                '        raise KeyError(path)\n'
                '    return fs[path]\n'
                '\n'
                'def stamp(clock):\n'
                '    return clock()\n'
                '\n'
                'def fixed_clock():\n'
                '    return "2026-01-01T00:00:00"\n'
                '\n'
                'fs = write({}, "out/report.txt", f"generated at {stamp(fixed_clock)}")\n'
                'print("files:", sorted(fs))\n'
                'print("content:", read(fs, "out/report.txt"))\n'
                '\n'
                'assert read(fs, "out/report.txt").endswith("2026-01-01T00:00:00")\n'
                'try:\n'
                '    read(fs, "missing.txt")\n'
                'except KeyError as error:\n'
                '    print("missing raised:", error)\n'
                'assert "missing.txt" not in fs\n'
                'print("fake filesystem and fixed clock kept the test deterministic")'
            ),
            variant_b='add a `list_dir(fs, prefix)` helper and assert it returns only paths under "out/"',
            variant_c='pass a clock that advances one hour each call and check the second report differs',
            mistakes=[
                "Writing to a real temporary folder when a dictionary fake would test the same logic faster.",
                "Calling `datetime.now()` inside the task, so the result can never be asserted exactly.",
                "Building a fake that silently returns empty text for missing files instead of raising.",
            ],
            q1=(
                "Why pass a fake filesystem and a fixed clock into a task?",
                "It removes real I/O and wall-clock time from the test, so results are fast, exact and repeatable.",
            ),
            homework=(
                "Write `write(fs, path, text)`, `read(fs, path)` and `save_report(fs, clock, path)` where `clock` is "
                "a zero-argument callable. Run it against a dict and a fixed clock, print the stored text, and "
                "comment which line keeps the test independent of the real disk."
            ),
            patterns=["def write", "def read", "clock"],
            mapping=(
                "Pytest fixtures commonly provide `tmp_path` and a frozen clock; the same seam lets production code "
                "use `pathlib` and `datetime` while tests use tiny fakes."
            ),
        ),
        153: dict(
            topic="Fixtures and builders",
            idea=(
                "As tests multiply, repeated setup becomes a second codebase that nobody maintains. Two tools keep it "
                "small. A fixture is a value prepared once and shared by tests that need the same starting state. A "
                "builder is a function that produces a valid example with sensible defaults and lets a test override "
                "only the fields that matter. Builders are especially useful for records with many keys: without "
                "one, every test spells out every field, and adding a field means editing every test. With one, a "
                "test reads as a statement about the single field under examination. The rule of thumb is that a "
                "fixture should be immutable from the test's point of view; if a test needs a variation, it builds a "
                "new value instead of mutating the shared one. That avoids order-dependent failures that appear only "
                "when tests run in a different sequence. Keep builders close to the production data shape and make "
                "their defaults realistic enough to catch mistakes: an empty name or a zero quantity is a poor "
                "default because it hides validation bugs. Today you write a builder for a small job record, derive "
                "two fixtures from it, and test a function that filters jobs. Notice how each test mentions only the "
                "field it cares about, and how a shared fixture keeps the unrelated fields consistent."
            ),
            code=(
                'def make_job(**overrides):\n'
                '    job = {"id": 1, "name": "nightly", "enabled": True, "retries": 2}\n'
                '    job.update(overrides)\n'
                '    return job\n'
                '\n'
                'def enabled_jobs(jobs):\n'
                '    return [job["name"] for job in jobs if job["enabled"]]\n'
                '\n'
                'fixture = [make_job(), make_job(id=2, name="weekly")]\n'
                'print("fixture:", fixture)\n'
                '\n'
                'def test_default_is_enabled():\n'
                '    assert enabled_jobs(fixture) == ["nightly", "weekly"]\n'
                '\n'
                'def test_disabled_is_skipped():\n'
                '    jobs = [make_job(), make_job(id=3, name="paused", enabled=False)]\n'
                '    assert enabled_jobs(jobs) == ["nightly"]\n'
                '\n'
                'for test in (test_default_is_enabled, test_disabled_is_skipped):\n'
                '    test()\n'
                '    print("passed:", test.__name__)\n'
                '\n'
                'assert make_job(id=9)["name"] == "nightly"\n'
                'assert fixture[0] is not fixture[1]\n'
                'print("builders keep each test focused on one field")'
            ),
            variant_b='add a "tags" list to the builder and assert two jobs do not share the same list object',
            variant_c='build a fixture with three jobs and assert the filter preserves input order',
            mistakes=[
                "Mutating a shared fixture inside a test, so a later test sees the changed value.",
                "Repeating every field in every test, so adding a key requires editing the whole suite.",
                "Choosing empty or zero defaults that make the builder produce invalid records.",
            ],
            q1=(
                "Why prefer a builder with defaults over copying a full literal in each test?",
                "Each test can override only the relevant field, while the remaining fields stay valid and consistent.",
            ),
            homework=(
                "Write `make_job(**overrides)` returning a valid job dict with defaults, and `enabled_jobs(jobs)` "
                "returning names of enabled jobs. Derive a fixture of two jobs, write two asserts that override one "
                "field each, and comment which line prevents shared mutable state."
            ),
            patterns=["def make_job", "**overrides", "assert"],
            mapping=(
                "Pytest fixtures and factory libraries such as `factory_boy` formalise builders; the value is the "
                "same: valid defaults plus targeted overrides keep tests readable as the schema grows."
            ),
        ),
        154: dict(
            topic="Golden outputs",
            idea=(
                "Some outputs are easier to compare as a whole than to take apart: rendered reports, generated "
                "configuration, formatted tables, command help. A golden test stores the expected output as a "
                "constant and compares the produced text to it exactly. This catches accidental changes anywhere in "
                "the output, including spacing and ordering, which is precisely what downstream tools and humans "
                "notice. It is also blunt: any intended change requires updating the golden value, so the diff must "
                "be reviewed rather than blindly accepted. That review is the point. The technique works best on a "
                "pure render function that takes data and returns a string. Keep the golden value beside the test, "
                "small enough to read, and make the comparison print both versions on failure so the difference is "
                "obvious. Avoid goldens for outputs that legitimately vary, such as timestamps or absolute paths, or "
                "normalise those parts first. A good pattern is one golden per format, not one per input, plus "
                "targeted assertions for the rules that matter. Today you render a tiny CSV report from records and "
                "compare it to a string constant, then change one input and watch the comparison fail in a way that "
                "names the changed line. This is the quickest regression net for text output."
            ),
            code=(
                'GOLDEN = "day,count\\nmon,2\\ntue,3"\n'
                '\n'
                'def render(rows):\n'
                '    lines = ["day,count"]\n'
                '    lines.extend(f"{day},{count}" for day, count in rows)\n'
                '    return "\\n".join(lines)\n'
                '\n'
                'rows = [("mon", 2), ("tue", 3)]\n'
                'actual = render(rows)\n'
                'print(actual)\n'
                'print("matches golden:", actual == GOLDEN)\n'
                '\n'
                'assert actual == GOLDEN\n'
                '\n'
                'changed = render([("mon", 2), ("tue", 4)])\n'
                'diff = [\n'
                '    (want, got)\n'
                '    for want, got in zip(GOLDEN.splitlines(), changed.splitlines())\n'
                '    if want != got\n'
                ']\n'
                'print("changed lines:", diff)\n'
                'assert diff == [("tue,3", "tue,4")]'
            ),
            variant_b='add a header flag to `render` and create a second golden with a different header',
            variant_c='normalise a final newline before comparing and explain why the golden stays stable',
            mistakes=[
                "Updating the golden file whenever a test fails without reviewing the actual diff.",
                "Including timestamps or absolute paths in the golden, so it fails on every machine.",
                "Storing a golden that is too large to read, so no reviewer can tell what changed.",
            ],
            q1=(
                "When is a golden-output test the right tool?",
                "When the whole rendered text is the contract and small formatting or ordering changes must be noticed and reviewed.",
            ),
            homework=(
                "Write `render(rows)` that turns day/count pairs into CSV text and `check_golden(actual, golden)` "
                "that returns the differing line pairs. Call it with one matching and one changed input, print the "
                "diff, and comment which line makes formatting changes visible."
            ),
            patterns=["GOLDEN", "def render", "assert"],
            mapping=(
                "Snapshot testing in Jest and pytest plugins follows this pattern; the useful versions force a "
                "review of the diff rather than accepting new output automatically."
            ),
        ),
        155: dict(
            topic="Property checks for transforms",
            idea=(
                "Example-based tests check specific inputs; property checks state rules that must hold for every "
                "input. You do not need a property library to start. Pick a small domain, loop over it, and assert "
                "invariants: a normaliser is idempotent, a sort does not change length, a slug contains no "
                "whitespace, an encoder followed by its decoder returns the original. These checks catch cases you "
                "would never think to write by hand, especially around empty strings, repeated separators and "
                "characters that look like separators. The key is choosing properties that are true by design, not "
                "accidentally true for the samples you picked. State them in words before writing the loop, because "
                "a vague property produces a vague test. Combine two styles: examples pin exact expected values, and "
                "properties cover many inputs cheaply. Keep the domain small and explicit, such as all strings of "
                "length zero to four over a tiny alphabet, so the test stays fast and reproducible. When a property "
                "fails, shrink the input by hand until the smallest counterexample is clear; that failing case often "
                "becomes a new example test. Today you write a slug transform and check idempotence, character set "
                "and round-trip behaviour over an exhaustive little input set. The result is broader coverage than a "
                "handful of examples for almost the same amount of code."
            ),
            code=(
                'import re\n'
                '\n'
                'def slug(text):\n'
                '    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")\n'
                '\n'
                'samples = ["", "A", "Hello World", " a  b ", "Q1/Q2", "---"]\n'
                'for text in samples:\n'
                '    value = slug(text)\n'
                '    assert value == slug(value), ("not idempotent", text)\n'
                '    assert re.fullmatch(r"[a-z0-9-]*", value), ("bad characters", value)\n'
                '    assert not value.startswith("-") and not value.endswith("-")\n'
                '    print(repr(text), "->", repr(value))\n'
                '\n'
                'assert slug("Hello World") == "hello-world"\n'
                'assert slug("Q1/Q2") == "q1-q2"\n'
                'assert slug("") == ""\n'
                'print("properties held for", len(samples), "samples")'
            ),
            variant_b='add a property that the slug length never exceeds the source length and check every sample',
            variant_c='add a decode-free round trip by stripping dashes and comparing to a lowercased alphanumeric form',
            mistakes=[
                "Stating a property that only holds for the chosen examples rather than by design.",
                "Using an unseeded random generator, so a failure cannot be reproduced.",
                "Running a huge input space in a unit test, making the suite slow enough to skip.",
            ],
            q1=(
                "What is the difference between an example test and a property check?",
                "An example pins one input to one output; a property asserts a rule that must hold across many inputs.",
            ),
            homework=(
                "Write `slug(text)` using `re.sub`, then a `check_properties(samples)` function that asserts "
                "idempotence and an allowed-character rule for each sample. Add one example assertion for a known "
                "input, print the slug for each sample, and comment which loop covers unseen cases."
            ),
            patterns=["def slug", "re.sub", "assert"],
            mapping=(
                "Hypothesis turns these loops into generated and shrunk cases, but the invariant-first thinking is "
                "the transferable part and works with plain asserts and small exhaustive domains."
            ),
        ),
        156: dict(
            topic="Linting and formatting",
            idea=(
                "Linting is automated reading of code and data for rules that are cheap to state and expensive to "
                "notice by eye. Formatting is the subset that has exactly one correct layout, which is why it can be "
                "applied mechanically and checked in CI. Both are useful for automations because a script that will "
                "be reviewed and rerun should look like the other scripts around it. You can build a small, honest "
                "linter with the standard library: `fnmatch` selects files by pattern, `re` checks line rules, and "
                "plain functions report violations as data. Common rules are a line-length limit, no trailing "
                "whitespace, no tabs where spaces are expected, and a naming convention for functions. Report the "
                "file, line number and rule so the fix is obvious, and return a non-empty list from a check function "
                "so CI can fail on it. Be careful not to conflate style with correctness: a lint rule should be "
                "explainable in one sentence and should not require reading the whole program. Start with a handful "
                "of rules, keep them deterministic, and format code with a tool rather than arguing about layout. "
                "Today you select Python files with `fnmatch`, run three regex checks over in-memory source lines, "
                "and print the violations. The same shape scales to a real repository by replacing the fake file "
                "list with a walk, while the checks stay readable."
            ),
            code=(
                'import fnmatch\n'
                'import re\n'
                '\n'
                'RULES = [\n'
                '    ("trailing-space", re.compile(r"\\s+$")),\n'
                '    ("long-line", re.compile(r".{41,}")),\n'
                '    ("bad-name", re.compile(r"^def [A-Z]")),\n'
                ']\n'
                '\n'
                'def lint(files):\n'
                '    problems = []\n'
                '    for name, lines in sorted(files.items()):\n'
                '        if not fnmatch.fnmatch(name, "*.py"):\n'
                '            continue\n'
                '        for number, line in enumerate(lines, 1):\n'
                '            for rule, pattern in RULES:\n'
                '                if pattern.search(line):\n'
                '                    problems.append((name, number, rule))\n'
                '    return problems\n'
                '\n'
                'files = {\n'
                '    "good.py": ["def run():", "    return 1"],\n'
                '    "bad.py": ["def Run():", "    return 1  ", "# " + "x" * 40],\n'
                '    "notes.txt": ["def NotChecked():   "],\n'
                '}\n'
                'for problem in lint(files):\n'
                '    print(problem)\n'
                '\n'
                'assert ("bad.py", 1, "bad-name") in lint(files)\n'
                'assert all(name.endswith(".py") for name, _, _ in lint(files))\n'
                'assert lint({"good.py": ["def run():"]}) == []'
            ),
            variant_b='add a rule that rejects tabs used for indentation and a sample file that triggers it',
            variant_c='ignore lines that start with a comment before applying the long-line rule',
            mistakes=[
                "Mixing style rules with behavioural assertions, so a formatting change fails a correctness test.",
                "Reporting only a count of problems instead of file, line and rule to make the fix actionable.",
                "Applying rules to every file type instead of selecting targets with a pattern.",
            ],
            q1=(
                "Why separate lint rules from behavioural tests?",
                "Lint rules are cheap, local statements about form; behaviour tests state what the program must do, and mixing them obscures both failures.",
            ),
            homework=(
                "Write `lint(files)` that uses `fnmatch` to select Python files and `re` to report long lines and "
                "function names starting with a capital. Return tuples of file, line and rule, print them for a "
                "small in-memory mapping, and comment which line keeps non-Python files out of the check."
            ),
            patterns=["fnmatch", "re.compile", "def lint"],
            mapping=(
                "`ruff`, `flake8`, `black` and `isort` are the production versions; wiring one check command into "
                "CI is the usual first quality gate for an automation repository."
            ),
        ),
        157: dict(
            topic="Packaging into modules",
            idea=(
                "A single long script is fine until two scripts need the same helper, or until someone wants to "
                "import the logic without running the command. Packaging is mostly the discipline of deciding what "
                "is a library and what is an executable. Put the reusable functions in modules with clear names, "
                "keep the command-line handling at the edge, and give the package a manifest that states its name, "
                "version, module list and supported Python version. That manifest is data, so you can check it before "
                "believing it. A useful check walks the declared modules, verifies that each name is a valid "
                "identifier, catches duplicates and reports missing dependencies between modules. The exercise is "
                "not about building a wheel; it is about noticing that packaging starts with a layout decision. A "
                "flat package of four small modules is easier to test than one file with forty functions, because "
                "each module can be imported and exercised alone. Naming matters too: a module called `utils` becomes "
                "a dumping ground, while `paths`, `tasks` and `cli` describe seams. Today you describe a package as a "
                "dictionary, validate its module names and dependencies, and print a summary. The same manifest "
                "shape could be rendered into `pyproject.toml`, but keeping it as data first makes the requirements "
                "explicit and testable."
            ),
            code=(
                'MANIFEST = {\n'
                '    "name": "autotools",\n'
                '    "version": "1.0.0",\n'
                '    "python": ">=3.10",\n'
                '    "modules": ["paths", "tasks", "cli"],\n'
                '    "requires": {"cli": ["paths", "tasks"], "tasks": ["paths"], "paths": []},\n'
                '}\n'
                '\n'
                'def check(manifest):\n'
                '    modules = manifest["modules"]\n'
                '    problems = []\n'
                '    if len(set(modules)) != len(modules):\n'
                '        problems.append("duplicate module")\n'
                '    for module in modules:\n'
                '        if not module.isidentifier():\n'
                '            problems.append(f"bad name: {module}")\n'
                '    for module, needs in manifest["requires"].items():\n'
                '        for need in needs:\n'
                '            if need not in modules:\n'
                '                problems.append(f"{module} needs missing {need}")\n'
                '    return problems\n'
                '\n'
                'print("package:", MANIFEST["name"], MANIFEST["version"])\n'
                'print("modules:", MANIFEST["modules"])\n'
                'print("problems:", check(MANIFEST))\n'
                '\n'
                'assert check(MANIFEST) == []\n'
                'assert check({"modules": ["a", "a"], "requires": {}})\n'
                'assert check({"modules": ["a"], "requires": {"a": ["b"]}}) == ["a needs missing b"]'
            ),
            variant_b='add a module "report" that depends on "tasks" and confirm the manifest check still passes',
            variant_c='add a module named "2fast" and assert the identifier rule reports it',
            mistakes=[
                "Leaving all logic in `__main__` so nothing can be imported or tested without running the CLI.",
                "Declaring modules that do not exist or depending on a module missing from the manifest.",
                "Creating a catch-all `utils` module that hides where each responsibility actually lives.",
            ],
            q1=(
                "Why split a script into modules before packaging it?",
                "Modules create importable seams, so helpers can be tested and reused while the CLI stays a thin edge.",
            ),
            homework=(
                "Write `check(manifest)` that validates module names, detects duplicates and reports dependencies "
                "missing from the module list. Describe a package with three modules and one bad dependency, print "
                "the problems, and comment which line proves the valid manifest is clean."
            ),
            patterns=["def check", "manifest", "print("],
            mapping=(
                "`pyproject.toml` plus a build backend is the real packaging path; the manifest-as-data check maps "
                "directly onto metadata validation and import smoke tests in CI."
            ),
        ),
        158: dict(
            topic="Entry points",
            idea=(
                "An entry point is the small, stable surface a user or installer sees. Instead of telling people to "
                "run a file with a long path, you give each command a name and route that name to a function. Keeping "
                "the routing table as data has three benefits: it documents the available commands, it makes unknown "
                "commands fail predictably, and it lets you test dispatch without a shell. The functions behind the "
                "table should take plain data and return plain data; printing and exiting belong at the outer edge. "
                "A dispatcher then looks up the name, reports a clear error when it is missing, and calls the "
                "function. This is also the layer where you decide the contract for arguments: a dictionary is "
                "enough for small tools, and it keeps the entry point testable. Be strict about the table: duplicate "
                "names should be rejected, and every function should be callable. In a real package the table maps "
                "onto console scripts in `pyproject.toml`, but the logic is identical. Today you build two tiny "
                "commands, register them in a dictionary, dispatch by name, and assert both the success path and "
                "the unknown-name failure. Notice that no argument parsing or printing happens inside the command "
                "functions, which is what makes them reusable from tests and from other commands."
            ),
            code=(
                'def greet(payload):\n'
                '    return "hello " + payload["name"]\n'
                '\n'
                'def count(payload):\n'
                '    return str(len(payload["items"]))\n'
                '\n'
                'ENTRY_POINTS = {"auto-greet": greet, "auto-count": count}\n'
                '\n'
                'def dispatch(name, payload):\n'
                '    if name not in ENTRY_POINTS:\n'
                '        raise KeyError(f"unknown command: {name}")\n'
                '    return ENTRY_POINTS[name](payload)\n'
                '\n'
                'print("commands:", sorted(ENTRY_POINTS))\n'
                'print(dispatch("auto-greet", {"name": "sam"}))\n'
                'print(dispatch("auto-count", {"items": ["a", "b", "c"]}))\n'
                '\n'
                'try:\n'
                '    dispatch("auto-nope", {})\n'
                'except KeyError as error:\n'
                '    print("rejected:", error)\n'
                '\n'
                'assert dispatch("auto-count", {"items": [1, 2]}) == "2"\n'
                'assert all(callable(fn) for fn in ENTRY_POINTS.values())\n'
                'assert len(set(ENTRY_POINTS)) == len(ENTRY_POINTS)'
            ),
            variant_b='add an "auto-upper" command that upper-cases payload["text"] and dispatch it',
            variant_c='make the dispatcher accept a default command and explain when that hides mistakes',
            mistakes=[
                "Hard-coding file paths in the user-facing command instead of naming a stable entry point.",
                "Doing argument parsing and printing inside every command function, which makes them hard to test.",
                "Allowing unknown commands to fall through silently instead of failing with a clear message.",
            ],
            q1=(
                "Why keep command functions separate from the dispatcher and the CLI edge?",
                "The functions stay pure and testable, while dispatch, parsing and output formatting remain one small outer layer.",
            ),
            homework=(
                "Write `greet(payload)` and `count(payload)` plus an `ENTRY_POINTS` dictionary and a `dispatch(name, "
                "payload)` function that raises `KeyError` for unknown names. Print one successful call and the "
                "unknown-name error, and comment which line makes the command surface data."
            ),
            patterns=["ENTRY_POINTS", "def dispatch", "KeyError"],
            mapping=(
                "Console scripts in `pyproject.toml` bind a command name to a callable; testing the dispatcher "
                "directly gives the same confidence without invoking the installed binary."
            ),
        ),
        159: dict(
            topic="Dependencies and virtualenvs",
            idea=(
                "A virtual environment is a private set of installed packages for one project. It exists so that two "
                "projects can use different versions of the same library without fighting, and so that the system "
                "Python stays clean. The practical rule is simple: create an environment per project, install only "
                "what the project declares, and record exact versions in a lock file. Without a lock, two installs "
                "on two days can produce different code paths and a bug that cannot be reproduced. Dependency "
                "resolution itself is a graph problem: each package may need others, some constraints conflict, and "
                "cycles must be reported rather than silently accepted. You can model that graph as a dictionary and "
                "compute an install order with a depth-first walk. Doing so makes the assumptions visible: a missing "
                "dependency, a version conflict or a cycle becomes a message instead of an install-time surprise. It "
                "also teaches why lock files are useful even when the resolver is good. Today you build a tiny "
                "resolver over a dictionary of requirements, detect a missing dependency and a cycle, and print a "
                "valid install order. In a real project the same thinking maps onto `venv`, `pip`, `pip-tools` or "
                "`uv`, but the lesson is about making the dependency graph explicit and checking it before installing "
                "anything."
            ),
            code=(
                'DEPS = {\n'
                '    "app": ["cli", "tasks"],\n'
                '    "cli": ["tasks"],\n'
                '    "tasks": ["paths"],\n'
                '    "paths": [],\n'
                '}\n'
                '\n'
                'def install_order(graph):\n'
                '    order = []\n'
                '    state = {}\n'
                '    def visit(node):\n'
                '        if state.get(node) == "visiting":\n'
                '            raise ValueError(f"cycle at {node}")\n'
                '        if state.get(node) == "done":\n'
                '            return\n'
                '        if node not in graph:\n'
                '            raise KeyError(f"missing dependency: {node}")\n'
                '        state[node] = "visiting"\n'
                '        for need in graph[node]:\n'
                '            visit(need)\n'
                '        state[node] = "done"\n'
                '        order.append(node)\n'
                '    for node in sorted(graph):\n'
                '        visit(node)\n'
                '    return order\n'
                '\n'
                'print("install order:", install_order(DEPS))\n'
                'try:\n'
                '    install_order({"app": ["nope"]})\n'
                'except KeyError as error:\n'
                '    print("bad graph:", error)\n'
                'try:\n'
                '    install_order({"a": ["b"], "b": ["a"]})\n'
                'except ValueError as error:\n'
                '    print("bad graph:", error)\n'
                '\n'
                'assert install_order(DEPS).index("paths") < install_order(DEPS).index("app")'
            ),
            variant_b='add a "report" package that shares the "paths" dependency and confirm "paths" appears once',
            variant_c='record a version string per dependency and assert a conflict is reported instead of resolved',
            mistakes=[
                "Installing project dependencies into the system interpreter instead of a virtual environment.",
                "Listing dependencies without pinning exact versions, so builds drift between machines.",
                "Ignoring a dependency cycle until the installer fails with an opaque message.",
            ],
            q1=(
                "Why use a virtual environment and a lock file together?",
                "The environment isolates the project's packages, and the lock file makes the exact resolved versions reproducible.",
            ),
            homework=(
                "Write `install_order(graph)` that returns dependencies before dependents, raises `KeyError` for a "
                "missing node and `ValueError` for a cycle. Run it on a four-node graph, print the order and both "
                "error cases, and comment which line enforces the install precondition."
            ),
            patterns=["def install_order", "cycle", "print("],
            mapping=(
                "`venv`, `pip`, `pip-tools`, `poetry` and `uv` all implement this graph work; a pinned lock file plus "
                "a clean environment is the baseline for reproducible CI."
            ),
        ),
        160: dict(
            topic="Secrets and config",
            idea=(
                "Configuration is the set of values that differ between environments; secrets are the subset that "
                "must never be printed, logged or committed. Mixing the two is a common leak: a debug line dumps the "
                "whole settings dictionary and a token ends up in a CI log forever. The fix has two parts. First, "
                "keep secrets in environment variables or a secret store, and only merge them into the runtime "
                "configuration at the edge. Second, make redaction explicit: a function that knows which keys are "
                "sensitive and replaces their values with a fixed marker before anything is rendered or logged. "
                "Layering is also important. Defaults live in the repository, overrides come from the environment, "
                "and an explicit local file can sit in between. Later layers win, but the result should still be "
                "validated, because a secret being present does not mean the configuration is correct. Test the "
                "redaction path directly: render a configuration containing a fake token and assert the token never "
                "appears in the output. That test is cheap and catches the leak that matters most. Today you merge "
                "layers, redact sensitive keys, print the safe view and check both precedence and non-disclosure. "
                "The values here are fake and in memory, but the shape is exactly what a real deploy script needs."
            ),
            code=(
                'DEFAULTS = {"region": "eu", "retries": 2, "token": ""}\n'
                'SECRET_KEYS = {"token", "api_key", "password"}\n'
                '\n'
                'def merge(*layers):\n'
                '    config = {}\n'
                '    for layer in layers:\n'
                '        config.update(layer)\n'
                '    return config\n'
                '\n'
                'def redact(config):\n'
                '    return {\n'
                '        key: ("***" if key in SECRET_KEYS and value else value)\n'
                '        for key, value in config.items()\n'
                '    }\n'
                '\n'
                'env = {"token": "fake-token-123", "retries": 5}\n'
                'config = merge(DEFAULTS, env)\n'
                'safe = redact(config)\n'
                'print("safe config:", safe)\n'
                'print("token leaked:", "fake-token-123" in str(safe))\n'
                '\n'
                'assert safe["token"] == "***"\n'
                'assert safe["retries"] == 5\n'
                'assert "fake-token-123" not in str(safe)\n'
                'assert config["token"] == "fake-token-123"\n'
                'print("redaction hides secrets while preserving runtime values")'
            ),
            variant_b='add an "api_key" to the environment layer and assert it is masked as well',
            variant_c='add a validation rule that rejects an empty region and run it on the merged config',
            mistakes=[
                "Printing the whole settings dictionary in a debug log, exposing tokens to CI output.",
                "Committing a real secret to the repository instead of reading it from the environment.",
                "Redacting only at the print site, so another logger or error message still leaks the value.",
            ],
            q1=(
                "Why redact secrets at the rendering boundary instead of trusting each caller?",
                "A single redaction function applied before output covers every caller and removes the chance of one forgotten log line leaking a token.",
            ),
            homework=(
                "Write `merge(*layers)` and `redact(config)` with a `SECRET_KEYS` set, then `show_config(config)` "
                "that returns the redacted view as text. Merge a fake token, print the safe text, and comment which "
                "line guarantees the secret never appears."
            ),
            patterns=["SECRET_KEYS", "def redact", "assert"],
            mapping=(
                "Twelve-factor configuration, CI secret variables and secret managers all follow this split; a "
                "redaction test belongs in the suite next to any code that logs settings."
            ),
        ),
        161: dict(
            topic="CI for automation",
            idea=(
                "Continuous integration is a robot that runs your checks on every change. For an automation project "
                "the useful pipeline is short: install the pinned dependencies in a clean environment, run the lint "
                "check, run the tests, and build or package the tool. Each stage should be a command with an exit "
                "code, and the pipeline should stop at the first failure so the log points at the first broken "
                "promise rather than a cascade. A pipeline is also data: a list of named stages with a command and "
                "an expected status. Modelling it that way lets you test the pipeline logic itself without a CI "
                "service, including fail-fast behaviour and the summary that tells a human what happened. Two habits "
                "make CI trustworthy. Keep it deterministic: pin versions, avoid network access in tests, and use "
                "fakes for time and files. Keep it fast: run the cheapest checks first so obvious mistakes fail in "
                "seconds. Today you simulate a small pipeline over stage dictionaries, run a green pipeline and a "
                "failing one, and assert that later stages are skipped after a failure. The simulation is fake, but "
                "the control flow, exit codes and log lines are the same ones a real runner produces, which is "
                "exactly what you need to reason about a failing build."
            ),
            code=(
                'STAGES = [\n'
                '    {"name": "lint", "code": 0},\n'
                '    {"name": "test", "code": 0},\n'
                '    {"name": "build", "code": 0},\n'
                ']\n'
                '\n'
                'def run_pipeline(stages):\n'
                '    log = []\n'
                '    for stage in stages:\n'
                '        log.append((stage["name"], stage["code"]))\n'
                '        if stage["code"] != 0:\n'
                '            return {"ok": False, "failed": stage["name"]}, log\n'
                '    return {"ok": True, "failed": None}, log\n'
                '\n'
                'summary, log = run_pipeline(STAGES)\n'
                'print("green:", summary, log)\n'
                '\n'
                'broken = [\n'
                '    {"name": "lint", "code": 0},\n'
                '    {"name": "test", "code": 1},\n'
                '    {"name": "build", "code": 0},\n'
                ']\n'
                'summary, log = run_pipeline(broken)\n'
                'print("red:", summary, log)\n'
                '\n'
                'assert run_pipeline(STAGES)[0] == {"ok": True, "failed": None}\n'
                'assert summary["failed"] == "test"\n'
                'assert [name for name, _ in log] == ["lint", "test"]'
            ),
            variant_b='add a "package" stage after build and confirm a green run includes it',
            variant_c='collect all failures instead of stopping early and compare the two summaries',
            mistakes=[
                "Running stages that depend on a failed stage, producing a noisy cascade of errors.",
                "Letting tests reach the network or the clock so CI flakes for reasons unrelated to the change.",
                "Reporting a green pipeline when a stage returned a nonzero code that was never checked.",
            ],
            q1=(
                "Why stop a CI pipeline at the first failing stage?",
                "The first failure is the root cause; later stages often fail only as a consequence and hide the real error.",
            ),
            homework=(
                "Write `run_pipeline(stages)` that executes stage dictionaries in order, stops on the first nonzero "
                "code and returns a summary plus a log. Run one green and one failing pipeline, print both, and "
                "comment which line enforces fail-fast behaviour."
            ),
            patterns=["def run_pipeline", '"code"', "print("],
            mapping=(
                "GitHub Actions, GitLab CI and Jenkins express the same stages and exit-code contract; keeping the "
                "checks local and deterministic is what makes those runners reliable."
            ),
        ),
        162: dict(
            topic="Versioning scripts",
            idea=(
                "Version numbers are a communication protocol. When a script is used by other scripts, a scheduler "
                "or a runbook, the version tells consumers whether an upgrade is safe. The common convention is "
                "semantic versioning: major for incompatible changes, minor for backwards-compatible features, and "
                "patch for fixes. You do not need a library to implement the mechanics; parse the three numeric "
                "parts into a tuple, compare tuples, and provide a bump function. The hard part is judgement, not "
                "code: removing a flag, changing an output column or making a required setting mandatory is a major "
                "change even if the diff is small. Automate the mechanical part and document the rule so the "
                "decision is consistent. Two details prevent confusion. Always print or record the version in the "
                "tool's output, so a bug report can name the build. And reject malformed versions early, because a "
                "string sort puts 1.10 before 1.9 and silently breaks release ordering. Today you parse versions, "
                "compare them correctly as integers, apply patch and minor bumps, and assert that a malformed value "
                "is refused. The example is tiny, but it is the same logic used by packaging tools and release "
                "scripts. Once versions are data, changelog entries and upgrade notes become much easier to keep "
                "honest."
            ),
            code=(
                'def parse_version(text):\n'
                '    parts = text.split(".")\n'
                '    if len(parts) != 3 or not all(p.isdigit() for p in parts):\n'
                '        raise ValueError(f"bad version: {text}")\n'
                '    return tuple(int(p) for p in parts)\n'
                '\n'
                'def bump(text, part="patch"):\n'
                '    major, minor, patch = parse_version(text)\n'
                '    if part == "major":\n'
                '        return f"{major + 1}.0.0"\n'
                '    if part == "minor":\n'
                '        return f"{major}.{minor + 1}.0"\n'
                '    return f"{major}.{minor}.{patch + 1}"\n'
                '\n'
                'print("compare:", parse_version("1.10.0") > parse_version("1.9.0"))\n'
                'print("patch:", bump("1.9.0"))\n'
                'print("minor:", bump("1.9.0", "minor"))\n'
                'print("major:", bump("1.9.0", "major"))\n'
                '\n'
                'assert parse_version("1.10.0") > parse_version("1.9.0")\n'
                'assert bump("2.3.4", "patch") == "2.3.5"\n'
                'assert bump("2.3.4", "minor") == "2.4.0"\n'
                'try:\n'
                '    parse_version("1.2")\n'
                'except ValueError as error:\n'
                '    print("rejected:", error)\n'
                'assert "1.2" not in [bump("1.2.0")]'
            ),
            variant_b='add a pre-release suffix "rc1" and assert it sorts before the final release',
            variant_c='write a rule that compares versions by tuple and explain why string comparison is wrong',
            mistakes=[
                'Comparing version strings lexicographically, so "1.10" sorts before "1.9".',
                "Treating a removed flag or changed output column as a patch release.",
                "Failing to print the version, so a bug report cannot identify the running build.",
            ],
            q1=(
                "Why compare versions as integer tuples rather than strings?",
                'String comparison is lexicographic, so "1.10" sorts before "1.9"; integer tuples compare each numeric part correctly.',
            ),
            homework=(
                "Write `parse_version(text)`, `bump(text, part=\"patch\")` and a `compare(a, b)` helper using parsed "
                'tuples. Print the result of bumping patch, minor and major, assert "1.10.0" is newer than "1.9.0", '
                "and comment why parsing must happen before comparison."
            ),
            patterns=["def parse_version", "def bump", "assert"],
            mapping=(
                "`packaging.version`, setuptools and release automation follow the same rules; correct ordering and a "
                "visible version string are what let consumers and CI reason about upgrades."
            ),
        ),
        163: dict(
            topic="Documenting a runbook",
            idea=(
                "A runbook is the operational half of a script: how to run it, what to check, what to do when it "
                "fails, and how to undo it. Writing one forces the vague parts of a tool into the open. If a step "
                "cannot be described as a command plus an expected result, it probably is not repeatable yet. The "
                "best runbooks are short, ordered and testable. Each step names the command, the expected output or "
                "exit code, and the recovery action when it does not match. Put the prerequisites first, then the "
                "normal path, then troubleshooting, then rollback. Avoid prose that explains the architecture; link "
                "to it and keep the runbook focused on action. Treat the document as data too: a list of steps with "
                "fields can be rendered into Markdown, checked for missing fields and printed in an incident. That "
                "makes completeness measurable and stops a critical step from being forgotten. Today you model "
                "three steps as dictionaries, render a numbered runbook, and assert that every step has a command "
                "and an expected result. The output looks like a wiki page, but it comes from checked data, which is "
                "the difference between documentation that survives and documentation that rots."
            ),
            code=(
                'STEPS = [\n'
                '    {"name": "check config", "command": "auto --check", "expect": "exit 0"},\n'
                '    {"name": "run export", "command": "auto export", "expect": "exit 0"},\n'
                '    {"name": "verify rows", "command": "auto verify", "expect": "0 missing"},\n'
                ']\n'
                '\n'
                'def check(steps):\n'
                '    problems = []\n'
                '    for number, step in enumerate(steps, 1):\n'
                '        for field in ("name", "command", "expect"):\n'
                '            if not step.get(field):\n'
                '                problems.append(f"step {number} missing {field}")\n'
                '    return problems\n'
                '\n'
                'def render(steps):\n'
                '    lines = ["# Runbook", ""]\n'
                '    for number, step in enumerate(steps, 1):\n'
                '        lines.append(f"{number}. {step[\'name\']}")\n'
                '        lines.append(f"   - run: {step[\'command\']}")\n'
                '        lines.append(f"   - expect: {step[\'expect\']}")\n'
                '    return "\\n".join(lines)\n'
                '\n'
                'print(render(STEPS))\n'
                'print("problems:", check(STEPS))\n'
                '\n'
                'assert check(STEPS) == []\n'
                'assert render(STEPS).count("expect:") == len(STEPS)\n'
                'assert check([{"name": "broken"}]) == [\n'
                '    "step 1 missing command", "step 1 missing expect"\n'
                ']'
            ),
            variant_b='add a rollback step and assert the rendered runbook numbers it after the normal steps',
            variant_c='render the steps as a checklist with a placeholder box before each name',
            mistakes=[
                "Writing narrative documentation with no commands, so an on-call engineer cannot act on it.",
                "Omitting the expected result, so the operator cannot tell whether a step succeeded.",
                "Skipping the rollback path until an incident makes it obvious that it was needed.",
            ],
            q1=(
                "What belongs in a runbook step?",
                "A command, the expected result or exit code, and a recovery action when the result does not match.",
            ),
            homework=(
                "Write `render(steps)` that produces numbered Markdown from step dictionaries, and `check(steps)` "
                "that reports missing name, command or expect fields. Render three valid steps, print the text and "
                "the empty problem list, and comment which line makes missing fields visible."
            ),
            patterns=["def render", "def check", "expect"],
            mapping=(
                "Good release docs and incident playbooks use the same command/expected/recovery shape; storing "
                "runbook steps as data lets CI validate that the documented commands still exist."
            ),
        ),
        164: dict(
            topic="Review: testing, packaging and devops checklist",
            idea=(
                "Today you assemble the checklist that the previous two weeks have been building toward. A release "
                "review is not a memory test; it is a set of questions with evidence, and every question should be "
                "answerable by running something. Are there tests that fail when the behaviour changes? Do they run "
                "without the network, a real clock or a writable working directory? Is the code linted and "
                "formatted? Is there a manifest with modules and a version? Is the command reachable through an "
                "entry point rather than a path? Are dependencies pinned and installed in an isolated environment? "
                "Are secrets kept out of the repository and redacted from logs? Does CI run the same checks? Can "
                "someone follow the runbook under pressure? Is the version visible in output? Each yes is a claim "
                "you can demonstrate. The point of collecting them in one review is to catch the gap between the "
                "checks you wrote and the checks you actually run. A checklist that no one executes is decoration, "
                "so this one takes a submission description and returns the missing items as data. That makes the "
                "review repeatable and lets another person reproduce the conclusion. The capstone builds on exactly "
                "this: a small automation with a suite, a manifest, a pinned environment, a CI definition and a "
                "runbook that agree with one another."
            ),
            code=(
                'CHECKS = [\n'
                '    ("tests", "test"),\n'
                '    ("deterministic", "fake-clock"),\n'
                '    ("linted", "lint"),\n'
                '    ("manifest", "pyproject"),\n'
                '    ("entry-point", "console-script"),\n'
                '    ("pinned-deps", "lock-file"),\n'
                '    ("secrets-redacted", "redact"),\n'
                '    ("ci", "pipeline"),\n'
                '    ("runbook", "steps"),\n'
                '    ("version-visible", "--version"),\n'
                ']\n'
                '\n'
                'def review(submission):\n'
                '    present = set(submission.get("artifacts", []))\n'
                '    missing = [name for name, artefact in CHECKS if artefact not in present]\n'
                '    return {"score": len(CHECKS) - len(missing), "total": len(CHECKS), "missing": missing}\n'
                '\n'
                'partial = {"artifacts": ["test", "lint", "pyproject", "pipeline"]}\n'
                'result = review(partial)\n'
                'print("score:", result["score"], "of", result["total"])\n'
                'print("missing:", result["missing"])\n'
                '\n'
                'full = {"artifacts": [artefact for _, artefact in CHECKS]}\n'
                'assert review(full) == {"score": 10, "total": 10, "missing": []}\n'
                'assert result["missing"] == [\n'
                '    "deterministic", "entry-point", "pinned-deps",\n'
                '    "secrets-redacted", "runbook", "version-visible",\n'
                ']\n'
                'print("a release review is a list of demonstrable claims")'
            ),
            variant_b='add a "changelog" artefact to the checklist and review a submission that lacks it',
            variant_c='weight the checks and compute a percentage score instead of a raw count',
            mistakes=[
                "Treating the checklist as documentation and never running it against a real submission.",
                "Accepting an artefact name without checking that the corresponding command or file exists.",
                "Leaving the review result verbal instead of returning data another person can reproduce.",
            ],
            q1=(
                "Why turn a release checklist into a function over a submission?",
                "It makes each claim testable and repeatable, so two reviewers reach the same conclusion from evidence rather than memory.",
            ),
            homework=(
                "Write `review(submission)` that compares an artifacts list against a `CHECKS` table and returns "
                "score, total and missing items. Review one partial and one complete submission, print both results, "
                "and comment which line makes the missing artefacts explicit."
            ),
            patterns=["CHECKS", "def review", "missing"],
            mapping=(
                "Release gates in CI, security checklists and SRE readiness reviews all use evidence-backed items; "
                "the Python version is a small, testable model of the same ritual."
            ),
        ),
    },
)
