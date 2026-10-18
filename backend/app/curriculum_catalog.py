"""180-day catalog curriculum for every non-launch path.

The three launch tracks keep their hand-authored curricula; this module covers
the other 97 paths so each one is a real 180-day course instead of a catalog
stub. Content grade is the same template grade the launch tracks already serve
on generated days (see ``extended_curriculum``): deterministic, stdlib-only
worked examples, honest rubrics, no new dependencies.

Layout per path (180 days):
  Days 1-14   foundation arc, framed in the path's domain (mirrors CURRICULA).
  Days 15-74  shared COMMON_180_PHASES, fully authored, reused verbatim.
  Days 75-179 seven 15-day domain phases built from the path's libraries.
  Day 180     capstone reflection.

``catalog_day`` is pure and deterministic: same inputs always give the same
day, so seeding is idempotent and safe to re-run.
"""

from .seed_data import COMMON_180_PHASES, COMMON_TOPIC_LIBRARY

CAPSTONE = (
    "180-day capstone reflection",
    "Capstone",
    "Review your final project, explain your design choices, and plan the next learning milestone.",
    "def reflect(project):\n    print('What I built:', project)\n\nreflect('my 180-day capstone')",
    "Write a function that prints your capstone name, one skill you learned, and one next-step goal.",
    ["def ", "print("],
    "**Finish line**\n\nA strong capstone includes working code, clear documentation, honest limitations and an explanation in your own words.",
)

# (title, objective, code, homework, patterns, pitfall) for Days 1-14.
# __LIB__ / __DOMAIN__ are replaced with the path's first library / domain.
_FOUNDATION = [
    ("First Python program",
     "Run a first Python program with variables, strings and print().",
     '# My first __DOMAIN__ program\ntool = "__LIB__"\nprint("Hello from", tool)\nprint("Domain: __DOMAIN__")\nprint("Length of tool name:", len(tool))\nprint("Ready to learn")',
     "Write a program of at least three non-empty lines: store a tool name in a variable with =, then print two lines about it.",
     ["print(", "="],
     "Forgetting quotes around the tool name, which makes Python read it as a variable instead of text."),
    ("Variables and values",
     "Store numbers and text in variables and print them back.",
     '# Values for __DOMAIN__\ncount = 3\nlabel = "__LIB__"\nratio = count / 2\nprint(label, "count:", count)\nprint("Half count:", ratio)\nprint("Types:", type(count).__name__, type(label).__name__)',
     "Write at least three non-empty lines using = to store two different values, then print both.",
     ["=", "print("],
     "Reusing one variable for two different meanings so the first value is lost before it is printed."),
    ("Input and strings",
     "Read user input and build strings from it.",
     'name = input("Your name: ")\nfocus = "__DOMAIN__"\ngreeting = "Hello, " + name\nprint(greeting)\nprint("Focus: " + focus)\nprint("Name length:", len(name))',
     "Write at least three non-empty lines that use input( to read a value and print( to greet the user with it.",
     ["input(", "print("],
     "Forgetting that input( always returns text, so adding two inputs concatenates instead of summing."),
    ("Decisions with if and else",
     "Branch on a condition with if and else.",
     'score = 85\nlimit = 50\nif score >= limit:\n    print("__LIB__ check: passed")\n    print("Margin:", score - limit)\nelse:\n    print("__LIB__ check: retry")\n    print("Needed:", limit - score)',
     "Write at least four non-empty lines with an if / else branch that prints a different message per branch.",
     ["if ", "print("],
     "Writing = instead of == or >= in the condition, which assigns instead of comparing."),
    ("Loops with for",
     "Repeat work with a for loop over a range.",
     'rounds = 3\nfor i in range(rounds):\n    print("Round", i + 1, "of __LIB__ practice")\nprint("Done:", rounds, "rounds")\nprint("Last index was", rounds - 1)',
     "Write at least three non-empty lines with a for loop that prints once per round.",
     ["for ", "print("],
     "Indentation slips: the line that should repeat sits outside the loop and runs only once."),
    ("Lists",
     "Keep ordered items in a list and loop over them.",
     'topics = ["setup", "__LIB__", "review"]\nprint("First:", topics[0])\nfor t in topics:\n    print("Step:", t)\nprint("Steps:", len(topics))\nprint("Last:", topics[-1])',
     "Write at least four non-empty lines: build a three-item list, loop over it with for, and print each item.",
     ["for ", "print("],
     "Indexing past the end of the list (topics[3] on three items) instead of using topics[-1] or len()."),
    ("Functions",
     "Group steps into a reusable function with def.",
     'def greet(tool):\n    print("Using", tool, "for __DOMAIN__")\n    return "greeted " + tool\n\ngreet("__LIB__")\ngreet("Python")\nprint(greet("review"))',
     "Define a function with def that prints something, then call it on two different inputs (at least four non-empty lines).",
     ["def ", "print("],
     "Defining the function but never calling it, so nothing is printed at all."),
    ("Return values",
     "Return computed values from functions.",
     'def double(n):\n    return n * 2\n\nfirst = double(4)\nsecond = double(10)\nprint("First:", first)\nprint("Second:", second)\nprint("Sum:", first + second)',
     "Define a function with def that uses return, call it twice, and print both results (at least four non-empty lines).",
     ["def ", "return"],
     "Printing inside the function and returning nothing, so the caller receives None."),
    ("Dictionaries",
     "Store labelled data in a dictionary.",
     'config = {"tool": "__LIB__", "domain": "__DOMAIN__"}\nprint(config["tool"])\nprint("Keys:", list(config))\nconfig["level"] = 1\nprint("Level:", config["level"])\nprint("Entries:", len(config))',
     "Build a dictionary with { } holding two entries, then print a value looked up by its key (at least three non-empty lines).",
     ["{", "print("],
     "Looking up a key that was never added instead of checking the keys first."),
    ("Debugging with try and except",
     "Handle a failing conversion without crashing.",
     'samples = ["42", "oops", "7"]\nfor raw in samples:\n    try:\n        print(raw, "->", int(raw) + 1)\n    except ValueError:\n        print(raw, "-> not a number")\nprint("Finished all samples")',
     "Write a try: / except block that converts a string with int( and prints a fallback message on failure (at least four non-empty lines).",
     ["try:", "except"],
     "Wrapping ten lines in one try so you cannot tell which line actually failed."),
    ("Reading and writing files",
     "Persist text with open() and read it back.",
     'lines = ["__LIB__ practice", "second line"]\nwith open("notes.txt", "w") as f:\n    for line in lines:\n        f.write(line + "\\n")\nwith open("notes.txt") as f:\n    print(f.read())\nprint("Lines written:", len(lines))',
     "Use with open( to write two lines to a file and read them back with print (at least four non-empty lines).",
     ["with ", "open("],
     "Opening with 'w' when you meant to read, which silently empties the file."),
    ("Testing with assert",
     "State expectations with assert so mistakes fail loudly.",
     'def add(a, b):\n    return a + b\n\nassert add(2, 3) == 5\nassert add(0, 0) == 0\nprint("assert passed for __LIB__")\nprint("add(20, 22) =", add(20, 22))',
     "Define a small function, check it with an assert statement, and print a confirmation (at least four non-empty lines).",
     ["assert ", "print("],
     "Asserting only the example's values instead of fresh ones you invent yourself."),
    ("Breaking problems down",
     "Split a task into small functions with clear jobs.",
     'def load():\n    return [1, 2, 3]\n\ndef total(rows):\n    return sum(rows)\n\ndef report(rows):\n    print("__DOMAIN__ rows:", len(rows), "total:", total(rows))\n\nreport(load())',
     "Write two small functions with def where one feeds the other, and print the final result (at least five non-empty lines).",
     ["def ", "print("],
     "One giant function doing everything instead of two small ones with clear jobs."),
    ("Foundation capstone",
     "Combine variables, a function, a loop and a collection in one script.",
     'def show(items):\n    for item in items:\n        print("-", item)\n    return len(items)\n\nsteps = ["read", "__LIB__", "practice"]\ndone = show(steps)\nprint("Capstone done:", done, "steps shown")',
     "Combine a list, a for loop and a def function with prints in one script of at least six non-empty lines.",
     ["def ", "print("],
     "Doing everything at the top level with no function, so nothing is reusable."),
]

# 15 applied frames reused across the seven domain phases. Each frame carries
# everything one flagship-shaped day needs: the idea, a runnable worked
# example (stdlib only, prints only — its real output is captured at
# generation time), two variant datasets, the homework function contract,
# and three classic mistakes.
_FRAMES = [
    dict(
        title="Orientation: what {lib} is for",
        idea="Knowing what a tool is for tells you when to reach for it and when not to.",
        code=(
            '# Where __LIB__ fits in __DOMAIN__\n'
            'tasks = ["collect input", "transform values", "report results"]\n'
            'uses_lib = [True, True, False]\n'
            '\n'
            'def describe(tasks, uses_lib):\n'
            '    lines = []\n'
            '    for task, flag in zip(tasks, uses_lib):\n'
            '        helper = "__LIB__" if flag else "plain Python"\n'
            '        lines.append(task + " -> " + helper)\n'
            '    return lines\n'
            '\n'
            'for line in describe(tasks, uses_lib):\n'
            '    print(line)\n'
            'print("Tasks covered:", sum(uses_lib), "of", len(tasks))\n'
            'print("--- second look ---")\n'
            'print(describe(["plan", "ship"], [False, True]))\n'
            'assert describe(["a"], [True]) == ["a -> __LIB__"]\n'
            'print("Pairing proven")'
        ),
        variant_b='tasks = ["fetch rows", "clean text"], uses_lib = [True, False]',
        variant_c='tasks = ["plot chart"], uses_lib = [True]',
        func="describe(tasks, uses_lib)",
        homework="Write `describe(tasks, uses_lib)` that pairs each task with '__LIB__' or 'plain Python' and returns the list of lines. Run it on two different task lists, print both results, and comment which line makes the pairing decision.",
        mistakes=["Describing the tool instead of matching it to a concrete task.", "Hard-coding the example's three tasks instead of using the parameters.", "Printing inside the loop but forgetting to return the list the prompt asks for."],
    ),
    dict(
        title="Setup and first runnable example",
        idea="A working setup you can re-run is the base every later day builds on.",
        code=(
            '# First run with __LIB__ for __DOMAIN__\n'
            'checks = ["interpreter starts", "__LIB__ available", "output prints"]\n'
            '\n'
            'def setup_report(checks):\n'
            '    passed = 0\n'
            '    for check in checks:\n'
            '        print("check:", check, "-> OK")\n'
            '        passed += 1\n'
            '    return passed\n'
            '\n'
            'done = setup_report(checks)\n'
            'print("Setup:", done, "of", len(checks), "checks passed")\n'
            'print("--- second look ---")\n'
            'assert setup_report(["one"]) == 1\n'
            'print("Counting proven")'
        ),
        variant_b='checks = ["interpreter starts", "files writable"]',
        variant_c='checks = ["interpreter starts", "__LIB__ available", "output prints", "folders exist"]',
        func="setup_report(checks)",
        homework="Write `setup_report(checks)` that prints each check with '-> OK', returns the count, and prints a final summary line. Run it on two different check lists, print both summaries, and comment which line counts a passing check.",
        mistakes=["Printing the checks but never returning the count.", "Counting with a second loop instead of the one that prints.", "Forgetting the summary line the prompt asks for."],
    ),
    dict(
        title="Core objects and key calls",
        idea="Every library has a small core: the objects you create and the calls you make most.",
        code=(
            '# Core objects behind __LIB__\n'
            'names = ["__LIB__ object one", "__LIB__ object two", "__LIB__ object three"]\n'
            '\n'
            'def core_demo(names):\n'
            '    built = []\n'
            '    for name in names:\n'
            '        built.append("ready: " + name)\n'
            '    print("Core objects:", len(built))\n'
            '    return built\n'
            '\n'
            'result = core_demo(names)\n'
            'for line in result:\n'
            '    print(line)\n'
            'print("--- second look ---")\n'
            'assert core_demo(["extra"]) == ["ready: extra"]\n'
            'print("Labels proven")'
        ),
        variant_b='names = ["single object"]',
        variant_c='names = ["a", "b", "c", "d"]',
        func="core_demo(names)",
        homework="Write `core_demo(names)` that builds 'ready: ...' labels, prints the count, and returns the list. Run it on two different name lists, print both results, and comment which line builds a label.",
        mistakes=["Returning the count instead of the list of labels.", "Building labels but printing the raw input instead.", "Using a global list so the second run repeats the first run's items."],
    ),
    dict(
        title="Reading input the {lib} way",
        idea="Real work starts with input: files, user entries, or data handed to your script.",
        code=(
            '# Input handling for __LIB__\n'
            'raw_rows = ["  sample one  ", "sample two", "   "]  \n'
            '\n'
            'def read_input(rows):\n'
            '    cleaned = []\n'
            '    for row in rows:\n'
            '        text = row.strip()\n'
            '        if text:\n'
            '            cleaned.append(text)\n'
            '    print("Read for __LIB__:", len(cleaned), "usable of", len(rows))\n'
            '    return cleaned\n'
            '\n'
            'good = read_input(raw_rows)\n'
            'for row in good:\n'
            '    print("row:", row)\n'
            'print("--- second look ---")\n'
            'assert read_input(["  padded  ", "", "ok"]) == ["padded", "ok"]\n'
            'print("Blanks proven dropped")'
        ),
        variant_b='raw_rows = ["  padded  ", "", "ok"]',
        variant_c='raw_rows = ["", "   "]',
        func="read_input(rows)",
        homework="Write `read_input(rows)` that strips each row, drops blanks, prints how many survived, and returns the clean list. Run it on two different row lists, print both results, and comment which line drops a blank row.",
        mistakes=["Stripping but keeping the blank rows anyway.", "Counting the raw rows instead of the cleaned ones in the report.", "Returning None because the return line sits inside the loop."],
    ),
    dict(
        title="Transforming results step by step",
        idea="Transformations should be small visible steps, never one giant leap.",
        code=(
            '# Step-by-step transform for __LIB__\n'
            'values = [1, 2, 3, 4]\n'
            '\n'
            'def transform(values):\n'
            '    out = []\n'
            '    for v in values:\n'
            '        doubled = v * 2\n'
            '        out.append(doubled)\n'
            '    print("__LIB__ transformed:", out)\n'
            '    return out\n'
            '\n'
            'first = transform(values)\n'
            'print("Total:", sum(first))\n'
            'print("Runs:", transform([10]))\n'
            'print("--- second look ---")\n'
            'assert transform([10, 20]) == [20, 40]\n'
            'print("Doubling proven")'
        ),
        variant_b='values = [10, 20]',
        variant_c='values = [0, -1, 5]',
        func="transform(values)",
        homework="Write `transform(values)` that doubles each value, prints the new list, and returns it. Run it on [1, 2, 3] and [10, 20], print both results, and comment which line does the doubling.",
        mistakes=["Printing each value instead of collecting and returning the list.", "Doubling the whole list with values * 2 instead of each item.", "Forgetting the return so the second use of the result crashes."],
    ),
    dict(
        title="Messy input and how to survive it",
        idea="Real input is messy: blanks, wrong types, missing fields. Plan for it.",
        code=(
            '# Surviving messy input in __DOMAIN__\n'
            'raw = ["7", "oops", "3", "n/a", "11"]\n'
            '\n'
            'def safe_number(text):\n'
            '    try:\n'
            '        return int(text)\n'
            '    except ValueError:\n'
            '        print("Skipping bad input for __LIB__:", text)\n'
            '        return 0\n'
            '\n'
            'def clean_all(raw):\n'
            '    nums = [safe_number(t) for t in raw]\n'
            '    print("Cleaned:", nums)\n'
            '    return nums\n'
            '\n'
            'nums = clean_all(raw)\n'
            'print("Usable sum:", sum(nums))\n'
            'print("--- second look ---")\n'
            'assert clean_all(["5", "bad"]) == [5, 0]\n'
            'print("Cleaning proven")'
        ),
        variant_b='raw = ["5", "bad", "5"]',
        variant_c='raw = ["x", "y"]',
        func="safe_number(text)",
        homework="Write `safe_number(text)` that returns int(text) but prints a skip message and returns 0 on bad input. Run it on two different strings, print both results, and comment which line catches the failure.",
        mistakes=["Catching the error but crashing anyway by re-raising it.", "Returning None instead of 0 so later sums fail.", "Wrapping the whole loop in one try so one bad value kills the rest."],
    ),
    dict(
        title="Wrapping the workflow in functions",
        idea="A workflow wrapped in functions can be tested, reused and explained.",
        code=(
            '# A reusable __LIB__ workflow\n'
            'source = ["row one", "row two", "row three"]\n'
            '\n'
            'def load():\n'
            '    print("__LIB__ loaded", len(source), "rows")\n'
            '    return list(source)\n'
            '\n'
            'def run():\n'
            '    rows = load()\n'
            '    print("__LIB__ rows ready:", len(rows))\n'
            '    return rows\n'
            '\n'
            'finished = run()\n'
            'print("First row:", finished[0])\n'
            'print("--- second look ---")\n'
            'assert run() == source\n'
            'print("Workflow repeatable")'
        ),
        variant_b='source = ["only row"]',
        variant_c='source = ["a", "b", "c", "d", "e"]',
        func="load() and run()",
        homework="Write `load()` returning three rows and `run()` that loads, prints the count, and returns the rows. Call run() twice, print both results, and comment which line connects the two functions.",
        mistakes=["Calling load() but ignoring what it returns.", "Printing inside load() and returning nothing.", "Copying the source list by reference so later edits leak between runs."],
    ),
    dict(
        title="Debugging a broken script",
        idea="Debugging is print, isolate, fix one thing, re-run. No step can be skipped.",
        code=(
            '# Debugging math behind __LIB__\n'
            'pairs = [(10, 2), (9, 3), (10, 0)]\n'
            '\n'
            'def buggy(total, count):\n'
            '    if count == 0:\n'
            '        print("__LIB__ guard: empty input")\n'
            '        return 0\n'
            '    return total / count\n'
            '\n'
            'def report(pairs):\n'
            '    results = []\n'
            '    for total, count in pairs:\n'
            '        value = buggy(total, count)\n'
            '        print(total, "/", count, "=", value)\n'
            '        results.append(value)\n'
            '    return results\n'
            '\n'
            'print("All results:", report(pairs))\n'
            'print("--- second look ---")\n'
            'assert report([(8, 2), (5, 0)]) == [4.0, 0]\n'
            'print("Guard proven")'
        ),
        variant_b='pairs = [(8, 2), (5, 0)]',
        variant_c='pairs = [(1, 1)]',
        func="buggy(total, count)",
        homework="Write `buggy(total, count)` that guards divide-by-zero with a printed warning and returns 0. Run it on (10, 2) and (10, 0), print both results, and comment which line is the guard.",
        mistakes=["Checking the wrong variable for zero.", "Printing the warning but dividing anyway.", "Returning a string so later math on the result fails."],
    ),
    dict(
        title="Reading error messages and docs",
        idea="Error messages name the line and the complaint; docs name the intended use. Read both.",
        code=(
            '# Errors you will meet with __LIB__\n'
            'attempts = [(4, 2), (4, 0), (7, 1)]\n'
            '\n'
            'def divide(a, b):\n'
            '    try:\n'
            '        return a / b\n'
            '    except ZeroDivisionError:\n'
            '        print("__LIB__ caught: division by zero")\n'
            '        return None\n'
            '\n'
            'def run_all(attempts):\n'
            '    ok = 0\n'
            '    for a, b in attempts:\n'
            '        value = divide(a, b)\n'
            '        print(a, "/", b, "->", value)\n'
            '        if value is not None:\n'
            '            ok += 1\n'
            '    return ok\n'
            '\n'
            'print("Succeeded:", run_all(attempts), "of", len(attempts))\n'
            'print("--- second look ---")\n'
            'assert run_all([(6, 3), (6, 0)]) == 1\n'
            'print("Handling proven")'
        ),
        variant_b='attempts = [(6, 3), (6, 0)]',
        variant_c='attempts = [(9, 0), (8, 0)]',
        func="divide(a, b)",
        homework="Write `divide(a, b)` that catches ZeroDivisionError with a printed message and returns None. Run it on (4, 2) and (4, 0), print both results, and comment which line catches the error.",
        mistakes=["Catching Exception so real bugs get hidden too.", "Returning 0 instead of None so callers cannot tell failure from zero.", "Putting the print after the return so it never runs."],
    ),
    dict(
        title="End-to-end mini project",
        idea="A mini project chains load, transform and report into one runnable script.",
        code=(
            '# Mini __DOMAIN__ pipeline with __LIB__\n'
            'incoming = [3, 1, 2]\n'
            '\n'
            'def load():\n'
            '    print("__LIB__ loaded:", incoming)\n'
            '    return list(incoming)\n'
            '\n'
            'def transform(rows):\n'
            '    ordered = sorted(rows)\n'
            '    print("__LIB__ ordered:", ordered)\n'
            '    return ordered\n'
            '\n'
            'def report(rows):\n'
            '    print("__LIB__ report: items =", len(rows), "first =", rows[0])\n'
            '    return rows\n'
            '\n'
            'report(transform(load()))\n'
            'print("Pipeline complete")\n'
            'print("--- second look ---")\n'
            'assert report(transform(load())) == [1, 2, 3]\n'
            'print("Pipeline proven")'
        ),
        variant_b='incoming = [9, 4]',
        variant_c='incoming = [5]',
        func="load(), transform(rows), report(rows)",
        homework="Write load/transform/report functions that chain into one pipeline call, printing at each stage. Run the pipeline on two different inputs, print both final reports, and comment which line chains the stages.",
        mistakes=["Calling the stages in the wrong order.", "Dropping a return so the next stage receives None.", "Printing but not returning, so the chain cannot be tested."],
    ),
    dict(
        title="Testing with asserts",
        idea="An assert after each change tells you within seconds whether the change helped.",
        code=(
            '# Proving __LIB__ helpers behave\n'
            'def double(n):\n'
            '    return n * 2\n'
            '\n'
            'def triple(n):\n'
            '    return n * 3\n'
            '\n'
            'assert double(3) == 6\n'
            'assert double(0) == 0\n'
            'assert triple(4) == 12\n'
            'print("__LIB__ checks passed: double and triple behave")\n'
            'print("double(21) =", double(21))\n'
            'print("--- second look ---")\n'
            'assert double(-2) == -4\n'
            'assert triple(0) == 0\n'
            'print("Negatives and zero behave")'
        ),
        variant_b='check double(-2) == -4 and triple(0) == 0',
        variant_c='check double(100) == 200 and triple(1) == 3',
        func="double(n)",
        homework="Write `double(n)`, check it with two assert statements on different inputs, and print a confirmation. Change one assert to a wrong expectation, watch it fail, then fix it and comment what the failure taught you.",
        mistakes=["Asserting the exact example values instead of fresh ones.", "Writing asserts with no message and no print, so passes are invisible.", "Testing only the happy path and never zero or negatives."],
    ),
    dict(
        title="Making it faster",
        idea="First make it correct, then measure, then speed up only the slow part.",
        code=(
            '# Timing a __LIB__ helper the honest way\n'
            'def total(rows):\n'
            '    s = 0\n'
            '    for r in rows:\n'
            '        s += r\n'
            '    return s\n'
            '\n'
            'small = [1, 2, 3]\n'
            'big = list(range(1000))\n'
            'print("__LIB__ small total:", total(small))\n'
            'print("__LIB__ big total:", total(big))\n'
            'print("Built-in check:", sum(big) == total(big))\n'
            'print("--- second look ---")\n'
            'assert total([]) == 0\n'
            'assert total([-1, 1]) == 0\n'
            'print("Edges behave")'
        ),
        variant_b='small = [5], big = list(range(10))',
        variant_c='small = [0, 0, 7], big = list(range(5000))',
        func="total(rows)",
        homework="Write `total(rows)` with an explicit loop, compare it against sum() on two different lists, print both comparisons, and comment which version you would keep and why.",
        mistakes=["Optimizing before measuring which part is slow.", "Replacing a clear loop with a clever one-liner nobody can debug.", "Timing with prints inside the loop, which dominates the measurement."],
    ),
    dict(
        title="Combining {lib} with the standard library",
        idea="The standard library multiplies any tool: files, JSON, dates and paths come free.",
        code=(
            '# __LIB__ plus the standard library\n'
            'import json\n'
            '\n'
            'payload = {"tool": "__LIB__", "ok": True, "runs": 3}\n'
            '\n'
            'def save(payload):\n'
            '    text = json.dumps(payload)\n'
            '    print("__LIB__ saved:", text)\n'
            '    return text\n'
            '\n'
            'def load(text):\n'
            '    back = json.loads(text)\n'
            '    print("__LIB__ loaded runs =", back.get("runs"))\n'
            '    return back\n'
            '\n'
            'load(save(payload))\n'
            'print("Round-trip complete")\n'
            'print("--- second look ---")\n'
            'assert load(save({"n": 1})) == {"n": 1}\n'
            'print("Round-trip proven")'
        ),
        variant_b='payload = {"tool": "__LIB__", "ok": False, "runs": 1}',
        variant_c='payload = {"tool": "__LIB__", "ok": True, "runs": 0}',
        func="save(payload) and load(text)",
        homework="Write save/load functions that round-trip a dictionary through json.dumps/loads. Run them on two different payloads, print both round-trips, and comment which line converts back to a dictionary.",
        mistakes=["Dumping but never loading back to prove the round-trip.", "Assuming key order or spacing in the JSON text.", "Forgetting that JSON turns tuples into lists."],
    ),
    dict(
        title="Common pitfalls",
        idea="Every tool has classic mistakes; learning them on purpose is cheaper than in production.",
        code=(
            '# Classic traps around __LIB__\n'
            'seen = []\n'
            'for i in [1, 2, 2, 3, 1]:\n'
            '    if i not in seen:\n'
            '        seen.append(i)\n'
            'print("__LIB__ deduped:", seen)\n'
            '\n'
            'counts = {}\n'
            'for i in [1, 2, 2, 3, 1]:\n'
            '    counts[i] = counts.get(i, 0) + 1\n'
            'print("__LIB__ counts:", counts)\n'
            'print("Unique items:", len(seen), "total items: 5")\n'
            'print("--- second look ---")\n'
            'def dedupe(items):\n'
            '    out = []\n'
            '    for i in items:\n'
            '        if i not in out:\n'
            '            out.append(i)\n'
            '    return out\n'
            '\n'
            'assert dedupe([1, 1, 2]) == [1, 2]\n'
            'print("Dedupe proven:", dedupe([7, 7, 8]))'
        ),
        variant_b='items = [1, 1, 1]',
        variant_c='items = [4, 5, 4, 6, 5, 4]',
        func="dedupe(items)",
        homework="Write `dedupe(items)` that returns each value once in first-seen order. Run it on two different lists with repeats, print both results, and comment which line skips a duplicate.",
        mistakes=["Using set() and silently losing the original order.", "Mutating the input list while iterating over it.", "Counting with counts[i] += 1 before the key exists."],
    ),
    dict(
        title="Phase review and practice set",
        idea="Review sticks when you rebuild from memory instead of re-reading.",
        code=(
            '# Rebuilding the phase from memory\n'
            'points = ["setup", "__LIB__ core", "debug", "test", "ship"]\n'
            '\n'
            'def review(points):\n'
            '    for p in points:\n'
            '        print("Recap:", p)\n'
            '    return len(points)\n'
            '\n'
            'def drill(n):\n'
            '    total = review(points[:n])\n'
            '    print("Drilled", total, "of", len(points), "points")\n'
            '    return total\n'
            '\n'
            'drill(3)\n'
            'drill(5)\n'
            'print("--- second look ---")\n'
            'assert drill(1) == 1\n'
            'print("Drill proven")'
        ),
        variant_b='points = ["setup", "core"]',
        variant_c='points = ["a", "b", "c", "d", "e", "f"]',
        func="review(points)",
        homework="Write `review(points)` that prints each point with a 'Recap:' prefix and returns the count. Run it on two different point lists, print both counts, and comment which line produces the prefix.",
        mistakes=["Re-reading notes instead of rebuilding from memory.", "Reviewing everything shallowly instead of a few items deeply.", "Skipping the second run that proves the first one stuck."],
    ),
]

_PHASES = [
    ("{lib} foundations", "Lay the groundwork: what the tool is, how to set it up, and the core moves."),
    ("{lib} core workflows", "Practice the everyday workflow end to end until it feels routine."),
    ("{lib} input and data handling", "Take messy real input and turn it into clean, usable values."),
    ("{lib} debugging and edge cases", "Find failures fast, guard the edges, and read errors properly."),
    ("{lib} testing and confidence", "Prove the code works with asserts and repeatable checks."),
    ("{lib} performance and polish", "Measure, speed up the slow part, and combine tools cleanly."),
    ("{name} capstone preparation", "Assemble everything into portfolio-ready project work."),
]

_DOMAIN_PATTERNS = ["def ", "print("]


def _fill(text: str, lib: str, domain: str) -> str:
    return text.replace("__LIB__", lib).replace("__DOMAIN__", domain).replace("{lib}", lib)


def _foundation_theory(title: str, objective_core: str, pitfall: str, name: str,
                     description: str, lib: str, domain: str, code: str) -> str:
    return (
        f"**Learning objective**\n{objective_core}\n\n"
        f"**Why it matters for {domain}**\n{description}. "
        f"The {lib} ecosystem assumes you can do this fluently: every script you write for {name} "
        f"stands on this exact skill.\n\n"
        f"**Working through the example**\nRead the code below top to bottom and say out loud what each "
        f"line does before you run it. Then run it, change one value, and predict the new output before "
        f"you run it again. The prediction habit is the whole lesson.\n\n"
        f"```python\n{code}\n```\n\n"
        f"**Watch out**\n- {pitfall}\n"
        f"- Testing only the exact values in the example instead of ones you invent.\n\n"
        f"**Practice before submitting**\nWrite today's assignment from scratch while explaining each choice in a comment."
    )


def _foundation_qa(title: str, objective_core: str) -> tuple[list[str], list[str]]:
    return (
        [
            f"What does {title} let a program do that it could not do before?",
            "Which line in the example would you change to test your understanding, and what would you expect?",
            "What breaks first if you remove one line, and why is that line load-bearing?",
        ],
        [
            objective_core,
            "Any one line, with a reason for the change and a predicted output.",
            "The line the rest depends on — run it without that line and explain the error.",
        ],
    )


def _run_example(code: str) -> str:
    """Capture what the worked example actually prints.

    Only our own stdlib-only templates ever reach here (never student code),
    and every frame snippet is verified runnable by the test suite. A fallback
    line keeps a failing snippet from breaking the seed.
    """
    import contextlib
    import io

    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            exec(compile(code, "<example>", "exec"), {"__name__": "__example__"})
    except Exception as exc:  # ponytail: honest fallback, fix the frame not the seeder
        return f"(Run it yourself — the sample raises {type(exc).__name__}.)"
    out = buf.getvalue().strip()
    return out if out else "(It runs silently — add a print to see the result.)"


def _domain_theory(topic: str, idea: str, phase_goal: str, name: str, description: str,
                   lib: str, code: str, variant_b: str, variant_c: str, mistakes: list[str]) -> str:
    output = _run_example(code)
    lines = [
        f"**Today: {topic}**",
        "",
        f"{idea} In {name} ({description}), this shows up whenever {lib} meets real input.",
        "",
        "**Worked example**",
        "This is the reference. Write your own version rather than copying it, then compare outputs.",
        "",
        "```python",
        code,
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
        f"**Variant 1** — {variant_b}",
        "Adapt the worked example to these values and print the result.",
        "",
        f"**Variant 2** — {variant_c}",
        "Adapt the worked example to these values and print the result.",
        "",
        "**Common mistakes**",
    ]
    lines += [f"- {m}" for m in mistakes]
    lines += [
        "",
        "**Going further**",
        f"Use {topic} inside a larger {name} script this week: call {lib}-shaped helpers from your own "
        f"functions, and notice where the idea strains — large inputs, surprising types, or silent wrong "
        f"answers. That strain is the map of what to learn next.",
        "",
        "**Study protocol (60 minutes)**",
        "1. Read the worked example and predict its output before running it.",
        "2. Change exactly one value and predict again — either way you learn.",
        "3. Write today's practice from scratch while explaining choices in comments.",
    ]
    return "\n".join(lines)


def _domain_qa(topic: str, func: str) -> tuple[list[str], list[str]]:
    return (
        [
            f"What does {topic} let you express that hard-coding the answer would not?",
            f"Which line in your solution is doing the real work, and what breaks if you remove it?",
            f"Your second variant has different values. Which parts of your logic did you assume?",
        ],
        [
            f"{topic} is a rule you can apply to any input of that shape, which is the difference between solving one case and being able to solve the next one.",
            f"The line that performs the core operation in {func} — removing it should change the output or raise an error.",
            "Feed it an edge case (empty input, zero, or a wrong type) so the failure becomes visible, then explain why it happened.",
        ],
    )


def catalog_day(slug: str, name: str, description: str, libraries: str, day: int):
    """Return one day as (title, domain, objective, code, homework, patterns, theory)."""
    libs = [s.strip() for s in (libraries or "").split(",") if s.strip()] or ["Python"]
    lib = libs[0]
    domain = name

    if 1 <= day <= 14:
        title, objective_core, code, homework, patterns, pitfall = _FOUNDATION[day - 1]
        code = _fill(code, lib, domain)
        questions, answers = _foundation_qa(title, objective_core)
        return (
            title, domain, objective_core, code, homework,
            patterns, _foundation_theory(title, objective_core, pitfall, name, description, lib, domain, code),
            questions, answers,
        )
    if 15 <= day <= 74:
        index = day - 15
        phase_title, phase_domain, phase_goal, topics = COMMON_180_PHASES[index // 15]
        topic = topics[index % 15]
        authored = COMMON_TOPIC_LIBRARY[topic]
        objective = f"Explain and apply {topic} in a small, testable Python example."
        return (
            f"{phase_title}: {topic}", phase_domain, objective,
            authored["code"], authored["homework"], ["def ", "print("], authored["theory"],
            [f"What problem does {topic} solve, and in which situation would you avoid it?",
             "Which exact line in the worked example demonstrates it, and what changes if you delete that line?",
             f"How would you modify the example so a classmate could watch {topic} fail on purpose?"],
            [objective,
             "The line carrying the core operation — removing it should change the output or raise an error.",
             "Feed it an edge case (empty input, zero, or a wrong type) so the failure becomes visible, then explain why it happened."],
        )
    if 75 <= day <= 179:
        index = day - 75
        phase_template, phase_goal = _PHASES[index // 15]
        phase_lib = libs[(index // 15) % len(libs)]
        phase = _fill(phase_template, phase_lib, domain).replace("{name}", name)
        frame = _FRAMES[index % 15]
        topic = _fill(frame["title"], phase_lib, domain)
        code = _fill(frame["code"], phase_lib, domain)
        homework = (
            frame["homework"].replace("__LIB__", phase_lib)
            if "__LIB__" in frame["homework"] else frame["homework"]
        )
        questions, answers = _domain_qa(topic, frame["func"])
        return (
            f"{phase}: {topic}", domain,
            f"Explain and apply {topic} for {name} in a small, testable Python example.",
            code, homework, list(_DOMAIN_PATTERNS),
            _domain_theory(topic, frame["idea"], _fill(phase_goal, phase_lib, domain),
                           name, description, phase_lib, code,
                           frame["variant_b"], frame["variant_c"], frame["mistakes"]),
            questions, answers,
        )
    title, domain, objective, code, homework, patterns, theory = CAPSTONE
    return (title, domain, objective, code, homework, patterns, theory,
            ["What did the capstone prove you can do?",
             "Which design choice would you defend, and why?",
             "What is the next milestone after this programme?"],
            [objective,
             "Name one trade-off you made and the reason it was the right call.",
             "A concrete skill, project, or role you are aiming at next."])


def catalog_days(name: str, description: str, libraries: str):
    """All 180 days for one path, in order."""
    return [catalog_day("", name, description, libraries, day) for day in range(1, 181)]


def extra_questions(paths: list[tuple[str, str, str]], idx: int):
    """Three deterministic placement questions for the path at index ``idx``.

    ``paths`` is [(name, description, libraries), ...]. Distractors come from
    neighbouring paths; the correct slot rotates so the answer key is not all A.
    Returns [(question, a, b, c, d, correct, difficulty), ...].
    """
    n = len(paths)
    name, description, libraries = paths[idx]
    lib0 = (libraries.split(",")[0].strip() if libraries else "") or "Python"

    def peer_lib(k: int, used: set[str]) -> str:
        for j in range(1, n):
            cand = (paths[(idx + k * j) % n][2].split(",")[0].strip() or "Python")
            if cand.lower() != lib0.lower() and cand.lower() not in used:
                return cand
        return f"Tool-{idx}-{k}"

    def peer_desc(k: int, used: set[str]) -> str:
        for j in range(1, n):
            cand = paths[(idx + k * j) % n][1]
            if cand != description and cand not in used:
                return cand
        return f"Applied Python area {idx}-{k}"

    def peer_proj(k: int, used: set[str]) -> tuple[str, str]:
        for j in range(1, n):
            pname, _, plibs = paths[(idx + k * j) % n]
            if pname != name and pname not in used:
                return pname, (plibs.split(",")[0].strip() or "Python")
        return (f"Domain {idx}-{k}", "Python")

    def placed(options: list[str], pos: int) -> tuple[list[str], str]:
        correct = options[0]
        others = options[1:]
        ordered = others[:pos] + [correct] + others[pos:]
        return ordered, "ABCD"[pos]

    out = []
    used_libs = {lib0.lower()}
    libs = [lib0]
    for k in (1, 2, 3):
        cand = peer_lib(k, used_libs)
        used_libs.add(cand.lower())
        libs.append(cand)
    ordered, letter = placed(libs, idx % 3)
    out.append((f"Which library is most associated with {name}?", *ordered, letter, 1))
    used_descs = {description}
    descs = [description]
    for k in (1, 2, 3):
        cand = peer_desc(k, used_descs)
        used_descs.add(cand)
        descs.append(cand)
    ordered, letter = placed(descs, (idx + 1) % 3)
    out.append((f"What is the main focus of {name}?", *ordered, letter, 1))
    used_projs: set[str] = {name}
    projs = [f"A small {name} project using {lib0}"]
    for k in (1, 2, 3):
        pname, plib = peer_proj(k, used_projs)
        used_projs.add(pname)
        projs.append(f"A small {pname} project using {plib}")
    ordered, letter = placed(projs, (idx + 2) % 3)
    out.append((f"Which would you build while learning {name}?", *ordered, letter, 2))
    return out
