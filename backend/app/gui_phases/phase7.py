"""GUI Applications capstone, days 165-179: scope to shipped app, day by day.

Every example stays stdlib-only, offline and deterministic: no display, no
toolkit import, no threads and no file I/O. Persistence is shown with
``json.dumps``/``json.loads`` and slow work is modelled as a job queue instead
of a real worker, so the applier can run each slice and get the same output on
every machine. The fifteen days follow one toy task manager from a written
scope through model, tree, layout, events, persistence, threading, theming,
tests, playtesting, packaging, accessibility and a final retrospective.
"""

PHASE = (
    "GUI Applications Capstone",
    "Ship a small, tested, packaged desktop task manager from a written scope to a headless-tested release.",
    {
        165: dict(
            topic="Capstone: choose the scope",
            idea=(
                "A capstone fails from unbounded scope far more often than from a missing skill. Today you practise "
                "the technique that prevents it: writing the scope as data before writing any UI. A scope template "
                "has three lists — must, should and out — and the out list does the real work, because naming what "
                "this build will not do is what makes the deadline survivable. Each entry is a feature with a short "
                "id, a one-line description and an effort guess in hours; the in-scope set is must plus should, and "
                "the rule is that the must list alone must fit your remaining budget with room to spare. When the "
                "estimate for must exceeds the budget, you move the lowest-value entry to should or out rather than "
                "quietly planning overtime. For a task manager, must might be adding a task, toggling it done and "
                "keeping the list; should might be due dates and search; out might be sync, accounts and attachments. "
                "Today you build a scope dictionary with those three lists, compute the in-scope count and the total "
                "effort, and assert the must-only effort fits the budget. The numbers are invented, but the "
                "discipline is real: scope is a decision you write down, not a mood you drift into."
            ),
            code=(
                'budget_hours = 12\n'
                'scope = {\n'
                '    "must": [("add", "add a task", 2), ("toggle", "mark done", 1), ("list", "show tasks", 2)],\n'
                '    "should": [("due", "due dates", 3), ("search", "filter text", 3)],\n'
                '    "out": ["sync", "accounts", "attachments"],\n'
                '}\n'
                '\n'
                'def effort(features):\n'
                '    return sum(hours for _, _, hours in features)\n'
                '\n'
                'in_scope = scope["must"] + scope["should"]\n'
                'print("must effort:", effort(scope["must"]))\n'
                'print("in scope:", len(in_scope), "features,", effort(in_scope), "hours")\n'
                'print("out:", scope["out"])\n'
                'assert effort(scope["must"]) <= budget_hours\n'
                'assert "sync" in scope["out"]\n'
                'print("scope written down: must fits the budget")'
            ),
            variant_b='add a "priority" feature to must with a 2-hour guess and re-check the budget assertion',
            variant_c='move "search" to the out list and print how the in-scope effort changes',
            mistakes=[
                "Planning only the must list in your head instead of writing must, should and out down.",
                "Letting the must list exceed the budget and assuming overtime will cover the gap.",
                "Never naming what is out of scope, so every new idea silently joins the build.",
            ],
            q1=(
                "Why does writing an out list make a capstone deadline more achievable?",
                "It turns unbounded ambition into an explicit decision, so time goes to the small must set and new ideas are deferred on purpose rather than by accident.",
            ),
            homework=(
                "Write `scope_plan(budget, must, should, out)` that builds a scope dict, prints the in-scope effort "
                "and returns True only when the must list fits the budget. Call it with one plan that fits and one "
                "that does not, print both verdicts, and comment which line enforces the budget."
            ),
            patterns=["def ", "return", "print("],
            mapping=(
                "Every desktop release is a scope decision: the must list is what ships, the out list is what the "
                "issue tracker keeps, and the budget line is the same gate a real product manager applies."
            ),
        ),
        166: dict(
            topic="Write the UI spec",
            idea=(
                "A UI spec is a contract between the person who wants the app and the person who builds it, and the "
                "cheapest place to fix a design problem is on paper. Today you write the spec as data: a dictionary "
                "of screens, each with a purpose, a list of widgets and the states that screen can be in. Every "
                "widget entry carries an id that is unique within the screen, a kind drawn from a small vocabulary "
                "(label, entry, listbox, button), and the state key it displays or edits, or None if it is purely "
                "decorative. The moment a widget declares its state binding, half your future bugs are already ruled "
                "out, because a widget that binds to nothing is either a mistake or decoration, and both are visible "
                "at review time. You also list the screen's states explicitly — empty, loading, populated, error — so "
                "the empty-list case is designed rather than discovered in testing. Today you build a spec for the "
                "main task screen, assert that all widget ids are unique, and assert that the two interactive "
                "widgets bind to the keys draft and tasks. The spec is only dictionaries and asserts, yet it already "
                "catches the classic omission: a list with no empty-state label."
            ),
            code=(
                'spec = {\n'
                '    "screens": {\n'
                '        "main": {\n'
                '            "purpose": "list and add tasks",\n'
                '            "widgets": [\n'
                '                {"id": "title", "kind": "label", "binds": None},\n'
                '                {"id": "entry", "kind": "entry", "binds": "draft"},\n'
                '                {"id": "list", "kind": "listbox", "binds": "tasks"},\n'
                '                {"id": "add", "kind": "button", "binds": None},\n'
                '            ],\n'
                '        }\n'
                '    }\n'
                '}\n'
                '\n'
                'main = spec["screens"]["main"]\n'
                'ids = [w["id"] for w in main["widgets"]]\n'
                'print("screen:", main["purpose"])\n'
                'print("widgets:", ids)\n'
                'bound = [w["binds"] for w in main["widgets"] if w["binds"]]\n'
                'print("bound to state:", bound)\n'
                'assert len(ids) == len(set(ids)), "widget ids must be unique"\n'
                'assert set(bound) == {"draft", "tasks"}\n'
                'print("spec is data: every widget has an id and a state binding")'
            ),
            variant_b='add a "clear" button and a "count" label bound to the tasks key, then re-check uniqueness',
            variant_c='give the main screen an explicit "states" list and print the empty-state label design',
            mistakes=[
                "Describing the screen in prose instead of a structured spec a program could read.",
                "Leaving a widget with no state binding and no note, so nobody knows if it is decoration or a bug.",
                "Designing only the populated state and leaving the empty list to be discovered at runtime.",
            ],
            q1=(
                "Why does recording each widget's state binding in the spec prevent bugs?",
                "It makes every widget either clearly decorative or clearly tied to one piece of state, so unbound or doubly-bound widgets are caught on paper before any code exists.",
            ),
            homework=(
                "Write `check_spec(spec)` that walks the screens, returns a list of problems for duplicate widget "
                "ids or missing state bindings, and prints the widget ids per screen. Test it on the worked spec and "
                "on one with a duplicate id, print both results, and comment which line finds the duplicate."
            ),
            patterns=["def ", "return", "print("],
            mapping=(
                "A real UI spec is the input a designer hands to a Tkinter or Qt developer; keeping it machine-"
                "readable is what lets tools and reviewers check it instead of arguing over a mockup."
            ),
        ),
        167: dict(
            topic="Model the data",
            idea=(
                "The data model is where a small app either stays easy for months or becomes a maze of special cases. "
                "Today you model tasks as a list of records with stable ids, and derive lookup structures rather than "
                "storing them. Each task is a dictionary with an id, the text and a done flag; ids come from a counter "
                "so they never collide, and text is stripped once at creation so comparison is honest later. From the "
                "list you derive an index, a dictionary from id to task, which makes toggling and deleting a lookup "
                "instead of a scan. Keeping the index derived, not stored, means it can never disagree with the list, "
                "which is the same single-source-of-truth rule you met in the view-model lesson, now applied to "
                "collections. You also write down the invariants and assert them: every id is unique, no text is "
                "empty, and done is a real boolean. Invariants are the part beginners skip and the part that pays "
                "off, because a cheap assertion at the boundary turns a silent corruption into a loud failure. Today "
                "you build three tasks, derive the index, and print the ids and the first task's text. The model is "
                "plain data, so every later lesson — persistence, threading, packaging — inherits it unchanged."
            ),
            code=(
                'def new_task(tasks, text, tid=None):\n'
                '    tid = tid or f"t{len(tasks) + 1}"\n'
                '    return tasks + [{"id": tid, "text": text.strip(), "done": False}]\n'
                '\n'
                'def by_id(tasks):\n'
                '    return {task["id"]: task for task in tasks}\n'
                '\n'
                'tasks = []\n'
                'tasks = new_task(tasks, "buy milk")\n'
                'tasks = new_task(tasks, "write spec")\n'
                'index = by_id(tasks)\n'
                'print("ids:", [task["id"] for task in tasks])\n'
                'print("index keys:", sorted(index))\n'
                'print("first text:", index["t1"]["text"])\n'
                'assert len(index) == len(tasks)\n'
                'assert all(task["text"] == task["text"].strip() for task in tasks)\n'
                'print("model has stable ids and a derived index")'
            ),
            variant_b='add a `toggle(tasks, tid)` that flips one task through the index and print the done flags',
            variant_c='add a `remove(tasks, tid)` and assert the derived index shrinks with the list',
            mistakes=[
                "Using the list position as the task identity, so deleting one task silently renames the rest.",
                "Storing the lookup dictionary separately from the list, letting the two drift out of sync.",
                "Normalising text only when displaying it, so \u201c buy milk \u201d and \u201cbuy milk\u201d compare as different tasks.",
            ],
            q1=(
                "Why derive the id-to-task index instead of storing it alongside the list?",
                "A derived index is rebuilt from the single source of truth, so it can never disagree with the list the way a separately maintained copy would.",
            ),
            homework=(
                "Write `build_model(texts)` that turns a list of strings into task records with stable ids and "
                "returns both the list and the derived index. Feed it three texts with stray spaces, print the ids "
                "and the index keys, and comment which line keeps the index derived."
            ),
            patterns=["def ", "return", "print("],
            mapping=(
                "Qt model classes and Tkinter string vars both assume one authoritative model; deriving lookups "
                "instead of duplicating them is what keeps a live desktop list view consistent."
            ),
        ),
        168: dict(
            topic="Design the widget tree",
            idea=(
                "A widget tree is the skeleton of the interface, and building it as nested dictionaries before any "
                "toolkit call makes structure visible and testable. Each node is a dictionary with a kind, optional "
                "properties and a list of children; the root is the window and everything else hangs from it. The "
                "technique worth practising is the walk: a generator that yields each node with its depth, because "
                "almost every later feature is a walk in disguise. Styling walks the tree applying tokens, theming "
                "walks it resolving colours, accessibility auditing walks it looking for unlabelled controls, and "
                "layout walks it assigning geometry. A generator keeps those operations lazy and composable, and the "
                "depth value gives you indentation in text and nesting level in a real toolkit. You also learn to "
                "separate structure from content: the entry, list and button live under a frame, so moving the frame "
                "moves the whole group without touching any child. Today you build a small window with a panel holding "
                "an entry, a listbox and a button, walk it, and print the tree indented, asserting the widget count. "
                "The indented output is exactly the kind of summary a real debugging session prints from a live tree."
            ),
            code=(
                'def widget(kind, **props):\n'
                '    return {"kind": kind, "children": [], **props}\n'
                '\n'
                'root = widget("window", title="Tasks")\n'
                'panel = widget("frame")\n'
                'root["children"].append(panel)\n'
                'panel["children"].append(widget("entry", name="draft"))\n'
                'panel["children"].append(widget("listbox", name="tasks"))\n'
                'panel["children"].append(widget("button", name="add", label="Add"))\n'
                '\n'
                'def walk(node, depth=0):\n'
                '    yield depth, node\n'
                '    for child in node["children"]:\n'
                '        yield from walk(child, depth + 1)\n'
                '\n'
                'for depth, node in walk(root):\n'
                '    print("  " * depth + node["kind"])\n'
                'count = sum(1 for _ in walk(root))\n'
                'assert count == 5\n'
                'print("tree walked:", count, "widgets")'
            ),
            variant_b='add a "status" label under the frame and re-print the indented tree and its count',
            variant_c='write `find(node, name)` that returns the first node with a matching name and print its kind',
            mistakes=[
                "Building the tree directly in toolkit calls, so no part of the structure can be walked or tested.",
                "Nesting widgets under the wrong parent, so moving one frame scatters its children.",
                "Writing a recursive walk with no depth, so every later pass has to recompute nesting by hand.",
            ],
            q1=(
                "Why is a generator-based tree walk more useful than printing the tree once?",
                "The same walk powers styling, theming, layout and accessibility passes, so each new feature reuses the traversal instead of rewriting it.",
            ),
            homework=(
                "Write `walk(node)` as a generator yielding `(depth, node)` and `count_widgets(node)` that sums it. "
                "Build a window with at least three nested levels, print the indented kinds and the count, and "
                "comment which line separates structure from the walk."
            ),
            patterns=["def ", "yield", "print("],
            mapping=(
                "Tkinter's and Qt's widget trees are exactly these nested containers; walking them generically is how "
                "real apps apply a theme or an accessibility pass to every control."
            ),
        ),
        169: dict(
            topic="Implement layout",
            idea=(
                "Layout is arithmetic you can do without a screen, and today you compute a toolbar that must fill its "
                "width exactly. The rule is the same one that governs grid weights and flex factors: subtract the gaps "
                "first, split what remains in proportion to the weights, then give the leftover pixels to one widget "
                "so the parts and gaps add back to the whole. Each widget spec carries an id and a weight; the entry "
                "is wide and the add button is narrow, so weights four and one express that intent without hard-coded "
                "pixels. The placement loop walks the specs in order, handing each a running x offset and a computed "
                "width, which is precisely what a packing geometry manager does internally. The identity to assert is "
                "that the last widget's right edge equals the container width — if it does not, you lost or gained "
                "pixels to integer rounding, and the fix is to give the remainder to the last item rather than round "
                "each share independently. Padding and alignment are refinements layered on this same computation, so "
                "getting the conservation right is the whole game. Today you distribute five hundred pixels across two "
                "weighted widgets with a six-pixel gap, print each box, and assert the sum lands exactly on the edge."
            ),
            code=(
                'def distribute(total, weights, gap=0):\n'
                '    usable = total - gap * (len(weights) - 1)\n'
                '    share = usable // sum(weights)\n'
                '    sizes = [weight * share for weight in weights]\n'
                '    sizes[-1] += usable - sum(sizes)\n'
                '    return sizes\n'
                '\n'
                'def place(width, specs, gap=6):\n'
                '    sizes = distribute(width, [s["weight"] for s in specs], gap)\n'
                '    boxes = []\n'
                '    x = 0\n'
                '    for spec, size in zip(specs, sizes):\n'
                '        boxes.append((spec["id"], x, size))\n'
                '        x += size + gap\n'
                '    return boxes\n'
                '\n'
                'toolbar = [{"id": "entry", "weight": 4}, {"id": "add", "weight": 1}]\n'
                'for name, x, size in place(500, toolbar):\n'
                '    print(f"{name:6} x={x:3} w={size:3}")\n'
                'last = place(500, toolbar)[-1]\n'
                'assert last[1] + last[2] == 500\n'
                'print("layout fills the toolbar exactly, gaps included")'
            ),
            variant_b='give the entry weight 3 and the button weight 1, then re-check the right edge equals 500',
            variant_c='add a fixed 40-pixel icon button and shrink the weighted entry so the row still fits',
            mistakes=[
                "Hard-coding pixel positions instead of computing them from the container width.",
                "Forgetting to subtract the gaps before splitting the remaining space between widgets.",
                "Losing the rounding remainder, so the row ends a few pixels short of the container edge.",
            ],
            q1=(
                "Why must the last widget's right edge equal the container width after distribution?",
                "It proves the arithmetic conserved every pixel, so the layout fills its container exactly at any width instead of drifting short or over.",
            ),
            homework=(
                "Write `place_row(width, specs, gap)` that returns each widget's x and width and leaves the rounding "
                "remainder on the last widget. Run it at two widths, print each box and the right edge, and comment "
                "which line hands the remainder to the last item."
            ),
            patterns=["def ", "return", "print("],
            mapping=(
                "Tkinter's grid weights, Qt's stretch factors and pack/grid managers all perform this distribution; "
                "computing it by hand is what makes a real layout debuggable by numbers."
            ),
        ),
        170: dict(
            topic="Wire events and validation",
            idea=(
                "Events and validation are two halves of one rule: a handler may only commit a change the data agrees "
                "to. Today you wire a small event layer where handlers replace state, and a validation function "
                "decides whether an action is even allowed. The important design choice is that validation is a pure "
                "function returning a list of error strings, not a boolean buried inside the handler, because a list "
                "tells the interface what to show and where. The add handler calls validation first and, when there "
                "are errors, returns the state and the messages unchanged; when the data is clean it builds the new "
                "task and clears the draft. This keeps the same shape across every action — read state, validate, "
                "commit or report — so adding a rename or a delete is mechanical rather than a new pattern. Notice "
                "that the handler never reads a widget and never prints; it transforms state, and printing is left to "
                "the caller so the logic stays testable in a headless run. Today you add a valid task, then attempt a "
                "blank one, print the resulting task list and the errors, and assert that the empty draft was rejected "
                "while the good one landed. That asymmetry is the lesson: valid input changes state, invalid input "
                "changes nothing but the message."
            ),
            code=(
                'def validate(state):\n'
                '    errors = []\n'
                '    if not state["draft"].strip():\n'
                '        errors.append("task text is empty")\n'
                '    if len(state["draft"]) > 40:\n'
                '        errors.append("task text is too long")\n'
                '    return errors\n'
                '\n'
                'def add(state):\n'
                '    errors = validate(state)\n'
                '    if errors:\n'
                '        return state, errors\n'
                '    task = {"text": state["draft"].strip(), "done": False}\n'
                '    return {"draft": "", "tasks": state["tasks"] + [task]}, []\n'
                '\n'
                'state = {"draft": "write spec", "tasks": []}\n'
                'state, errors = add(state)\n'
                'print("after add:", state["tasks"], "errors:", errors)\n'
                'state, errors = add({"draft": "   ", "tasks": state["tasks"]})\n'
                'print("after blank add:", len(state["tasks"]), "errors:", errors)\n'
                'assert len(state["tasks"]) == 1 and errors\n'
                'print("handlers change state; validation gates the change")'
            ),
            variant_b='add a maximum of ten tasks to `validate` and check an eleventh add is rejected',
            variant_c='make `add` return the state untouched on error and assert the task count does not grow',
            mistakes=[
                "Validating inside the widget callback with a boolean, so the interface cannot say what was wrong.",
                "Mutating the task list in place before validation passes, leaving half-finished state behind.",
                "Reading the entry widget from inside the handler, which makes the logic impossible to test headless.",
            ],
            q1=(
                "Why should validation return a list of messages rather than a single boolean?",
                "A list carries what went wrong for each field, so the interface can show specific feedback and the caller can test each failure separately.",
            ),
            homework=(
                "Write `commit(state, handlers, event)` that validates the event, applies the matching handler on "
                "success and returns `(state, errors)`. Fire one valid event and one invalid one, print both states "
                "and the errors, and comment which line enforces commit-or-report."
            ),
            patterns=["def ", "return", "print("],
            mapping=(
                "A Tkinter `command=` callback or a Qt slot should do just this: validate, then commit; keeping "
                "validation pure is what lets a real form show inline errors next to each field."
            ),
        ),
        171: dict(
            topic="Add persistence",
            idea=(
                "Persistence turns a running app into a product, and the technique is a versioned JSON round trip. You "
                "write a save function that wraps the state in an envelope with a version number and serialises it "
                "with json.dumps, and a load function that parses with json.loads, checks the version and returns the "
                "state. The envelope is the whole point: without a version tag, the day you add a field you have two "
                "formats on disk and no way to tell them apart. Because the model is already plain dictionaries and "
                "lists of primitives, serialisation is nearly free, which is a quiet payoff of the earlier data-model "
                "lesson; the moment state contains sets, custom objects or tuples, JSON either refuses or silently "
                "changes the type on the way back. The test to write is a round trip: save a populated state, load it, "
                "and assert equality, because a state that survives the round trip unchanged is exactly the promise "
                "persistence makes. Handle the failure path too, raising a clear error on an unknown version rather "
                "than loading something half-understood. Today you save a state with one task, print the byte length "
                "and the blob, restore it, and assert the cycle is lossless. The same blob is what the app writes on "
                "quit and reads on launch."
            ),
            code=(
                'import json\n'
                '\n'
                'def save(state):\n'
                '    return json.dumps({"version": 1, "state": state}, sort_keys=True)\n'
                '\n'
                'def load(blob):\n'
                '    data = json.loads(blob)\n'
                '    if data.get("version") != 1:\n'
                '        raise ValueError("unsupported version")\n'
                '    return data["state"]\n'
                '\n'
                'state = {"tasks": [{"text": "buy milk", "done": False}], "draft": ""}\n'
                'blob = save(state)\n'
                'print("bytes:", len(blob))\n'
                'print("blob:", blob)\n'
                'restored = load(blob)\n'
                'print("round trip equal:", restored == state)\n'
                'assert restored == state\n'
                'try:\n'
                '    load(\'{"version": 2, "state": {}}\')\n'
                'except ValueError as exc:\n'
                '    print("rejected:", exc)\n'
                'print("state survives a versioned JSON round trip")'
            ),
            variant_b='add a second task, re-save, and assert the reloaded state has two tasks in order',
            variant_c='bump the version in `save` and check that `load` rejects the mismatch with a clear error',
            mistakes=[
                "Saving state without a version tag, so an added field silently breaks old files.",
                "Storing tuples or sets in state and assuming JSON brings the same type back.",
                "Mutating the loaded dictionary as if it were the live state, so the in-memory truth and disk diverge.",
            ],
            q1=(
                "Why wrap the saved state in a versioned envelope instead of dumping the state alone?",
                "The version tag lets `load` tell formats apart, so a future field addition can migrate old files instead of misreading them.",
            ),
            homework=(
                "Write `round_trip(state)` that saves with `json.dumps`, reloads with `json.loads`, and returns True "
                "only when the restored state equals the original. Test it on a state with two tasks and on one "
                "holding a tuple, print both results, and comment which line enforces the version check."
            ),
            patterns=["def ", "json", "return"],
            mapping=(
                "Tkinter and Qt apps both persist state this way on quit and launch; a versioned JSON envelope is the "
                "smallest thing that keeps old user data readable after a release changes the model."
            ),
        ),
        172: dict(
            topic="Move slow work off the UI thread",
            idea=(
                "Responsiveness is about keeping each turn of the event loop short, not about adding threads first, "
                "and today you model the standard fix as data: a job queue the interface polls. Slow work is submitted "
                "as a job with an id and a description; the interface keeps a pending list and a results dictionary, "
                "sets its status to working, and continues to handle events. On each idle tick it calls poll, which "
                "drains the pending list into results and flips the status back to idle. Because the worker and the "
                "loop only meet at the queue and the results map, there is no shared mutable structure to corrupt, "
                "which is the same rule real threads obey when they post events instead of touching widgets. The "
                "pattern also gives you a natural place for progress and cancellation later: a job is just a record "
                "you can inspect. Modelling it deterministically with a scripted result means you can assert the exact "
                "states — idle before submit, working while pending, idle after poll — without a real thread and "
                "without flaking. Today you submit one job, print the status and pending ids before and after the "
                "poll, and assert the result landed and the queue emptied. The real toolkit swaps the scripted result "
                "for a thread, but the contract stays the same."
            ),
            code=(
                'def submit(pending, job_id, work):\n'
                '    return pending + [{"id": job_id, "work": work, "result": work.upper()}]\n'
                '\n'
                'def poll(state):\n'
                '    done, state["pending"] = state["pending"], []\n'
                '    for job in done:\n'
                '        state["results"][job["id"]] = job["result"]\n'
                '    return state\n'
                '\n'
                'state = {"pending": [], "results": {}, "status": "idle"}\n'
                'state["pending"] = submit(state["pending"], "j1", "parse import")\n'
                'state["status"] = "working"\n'
                'print("status:", state["status"])\n'
                'print("pending:", [job["id"] for job in state["pending"]])\n'
                'state = poll(state)\n'
                'state["status"] = "idle"\n'
                'print("results:", state["results"])\n'
                'assert state["results"]["j1"] == "PARSE IMPORT"\n'
                'assert state["pending"] == []\n'
                'print("the UI thread only polls finished jobs; the work ran elsewhere")'
            ),
            variant_b='submit two jobs before one poll and assert both results land in the same tick',
            variant_c='add a "failed" result and assert the loop records it without raising',
            mistakes=[
                "Doing the slow work inside the event handler, so the window cannot redraw until it finishes.",
                "Letting a worker write into the widget tree directly instead of posting a result for the loop.",
                "Polling only after the job is done, so the interface shows a frozen working state with no progress.",
            ],
            q1=(
                "Why does the worker communicate through a queue and results map instead of touching the UI?",
                "Only the UI thread may safely change widgets, so the worker hands data back through a shared record the loop polls, avoiding concurrent mutation of the tree.",
            ),
            homework=(
                "Write `run_jobs(jobs)` that submits each job to a pending list, polls once, and returns the results "
                "map. Feed it two jobs, print the pending ids before the poll and the results after, and comment "
                "which line moves finished work back to the UI thread."
            ),
            patterns=["def ", "return", "print("],
            mapping=(
                "Tkinter needs `after` or a queue with the main loop, and Qt uses signals across threads; both are "
                "this submit-and-poll contract, which is why it is worth modelling before touching a real thread."
            ),
        ),
        173: dict(
            topic="Theme and polish",
            idea=(
                "Theming is one palette and many tokens, and the technique is indirection: widgets never name a colour "
                "directly, they name a role that a theme resolves. Today you build a small theme where a palette holds "
                "the raw colours and each component's tokens map roles like fg and bg onto palette entries. A resolve "
                "function walks the token map and substitutes each role with its colour, so a button and a label share "
                "the same text colour because both point at the text role, not because someone copied a hex code "
                "twice. The payoff is that a restyle is one edit in the palette; the failure mode you avoid is the "
                "classic app where changing the accent colour means hunting twenty hard-coded hex strings. Keeping the "
                "palette flat and the tokens declarative also lets you later add a dark palette with no change to any "
                "component, which is the same separation of structure from presentation that governs real stylesheets. "
                "The assert you write pins the indirection: the button's background must equal the palette's accent "
                "entry, so the link is tested rather than assumed. Today you resolve a button and a label against one "
                "palette, print the resolved colours, and assert both roles resolve to the palette values they name. "
                "Polish is often just this kind of mechanical consistency, applied everywhere at once."
            ),
            code=(
                'theme = {\n'
                '    "palette": {"text": "#111111", "accent": "#2d6cdf", "paper": "#fafafa"},\n'
                '    "button": {"fg": "text", "bg": "accent"},\n'
                '    "label": {"fg": "text", "bg": "paper"},\n'
                '}\n'
                '\n'
                'def resolve(tokens, palette):\n'
                '    return {key: palette[value] for key, value in tokens.items()}\n'
                '\n'
                'button = resolve(theme["button"], theme["palette"])\n'
                'label = resolve(theme["label"], theme["palette"])\n'
                'print("button:", button)\n'
                'print("label:", label)\n'
                'assert button["bg"] == theme["palette"]["accent"]\n'
                'assert label["bg"] == theme["palette"]["paper"]\n'
                'assert button["fg"] == label["fg"]\n'
                'print("one palette, many tokens: restyle once, apply everywhere")'
            ),
            variant_b='add a "disabled" button token using a muted palette entry and print its resolved colours',
            variant_c='build a dark palette and assert every token still resolves to a real colour',
            mistakes=[
                "Writing raw hex colours into each widget, so a restyle means editing every component.",
                "Letting a token name a role the palette does not define, which fails only at render time.",
                "Duplicating colour definitions in the palette, so two entries drift apart on the next tweak.",
            ],
            q1=(
                "Why resolve colours through named tokens instead of naming hex values in each widget?",
                "Components depend on roles, not raw colours, so the whole app restyles from one palette edit and the token-to-palette link can be asserted.",
            ),
            homework=(
                "Write `apply_theme(tokens, palette)` that returns resolved colours and raises a clear error for an "
                "unknown role. Resolve one theme with three tokens, print the result, and comment which line turns a "
                "role name into a colour."
            ),
            patterns=["def ", "return", "print("],
            mapping=(
                "Qt stylesheets, Tkinter's `ttk` themes and CSS custom properties all implement palette-plus-tokens; "
                "this indirection is what makes a professional-looking desktop app restylable."
            ),
        ),
        174: dict(
            topic="Write headless tests",
            idea=(
                "Headless tests are the discipline that lets you change a GUI app without fear, and the technique is a "
                "tiny runner over assert-based functions. Each test is a plain function that sets up a small state, "
                "performs one operation, and asserts the result; there is no framework, no fixture magic and no "
                "display, because everything the app does is a function over dictionaries. The runner takes a list of "
                "(name, function) pairs, calls each one, catches AssertionError, prints PASS or FAIL with the message, "
                "and returns the counts. That is enough to catch the two failure modes that matter: a test that should "
                "pass but fails, and — just as important — a test written so loosely it cannot fail, which you expose "
                "by deliberately including one that is wrong and confirming the runner reports it. Keeping tests as "
                "data beside the app also makes coverage visible: if a handler has no test entry, the gap is obvious "
                "in the list. The whole thing runs in milliseconds and needs no window, so it runs on every save. Today "
                "you write three tests, run them, print the pass and fail tallies, and assert the runner reported "
                "exactly two passes and one failure. When you later swap the text model for real widgets, this runner "
                "and its assertions come with you unchanged."
            ),
            code=(
                'def test_add_task():\n'
                '    tasks = []\n'
                '    tasks.append({"text": "write spec", "done": False})\n'
                '    assert len(tasks) == 1\n'
                '\n'
                'def test_toggle():\n'
                '    task = {"text": "x", "done": False}\n'
                '    task["done"] = not task["done"]\n'
                '    assert task["done"] is True\n'
                '\n'
                'def test_bad():\n'
                '    assert 2 + 2 == 5, "deliberately wrong"\n'
                '\n'
                'def run(tests):\n'
                '    passed = failed = 0\n'
                '    for name, fn in tests:\n'
                '        try:\n'
                '            fn()\n'
                '            passed += 1\n'
                '            print("PASS", name)\n'
                '        except AssertionError as exc:\n'
                '            failed += 1\n'
                '            print("FAIL", name, "-", exc)\n'
                '    return passed, failed\n'
                '\n'
                'tests = [("add_task", test_add_task), ("toggle", test_toggle), ("bad", test_bad)]\n'
                'passed, failed = run(tests)\n'
                'print(f"{passed} passed, {failed} failed")\n'
                'assert (passed, failed) == (2, 1)\n'
                'print("headless: tests run without a window or a display")'
            ),
            variant_b='add a `test_empty_rejected` test and assert the pass tally grows to three',
            variant_c='make `run` print the names of the failures at the end and assert it reports only the wrong test',
            mistakes=[
                "Writing tests so loose they pass on any input, so they never catch a regression.",
                "Needing a running display to test logic that is really just functions over state.",
                "Testing several behaviours in one function, so the first failure hides the rest.",
            ],
            q1=(
                "Why is a deliberately failing test worth including in the runner demo?",
                "It proves the runner actually reports failures; without it a green board could mean the checks never ran or cannot fail.",
            ),
            homework=(
                "Write `run_suite(tests)` that calls each test function, catches AssertionError, prints PASS or FAIL, "
                "and returns the pass and fail counts. Include one deliberately failing test, print the tally, and "
                "comment which line catches the failure."
            ),
            patterns=["def ", "assert", "print("],
            mapping=(
                "The logic of a Tkinter or Qt app can be tested this way without launching it, which is why teams "
                "keep the model separate from the widgets and run a headless suite on every change."
            ),
        ),
        175: dict(
            topic="Playtest the flows",
            idea=(
                "Playtesting is replaying a scripted user flow and checking the outcome, and doing it as code turns a "
                "vague 'it feels fine' into a reproducible trace. Today you write a play function that reads a script "
                "of events — type, add, toggle — applies them to state in order, and records a trace of what changed "
                "after each step. The trace is the useful part: it shows the count of tasks and the draft after every "
                "event, so when the flow ends in the wrong place you can point at the exact step that diverged. This "
                "is flow coverage rather than code coverage: you pick the journeys a real user takes, like adding two "
                "tasks and completing the first, and assert the final board, including the empty-input path where add "
                "should be a no-op. Because the script is data, you can extend it, shuffle it or replay a bug report "
                "verbatim, and the same function runs in a test or in a debug console. The technique also surfaces "
                "awkward sequencing early — a toggle before any task exists — which is cheap to guard here and "
                "expensive to find in a live app. Today you replay a five-step script that adds two tasks and toggles "
                "the first, print the trace, and assert the first task is done and the list holds two entries."
            ),
            code=(
                'def play(state, script):\n'
                '    trace = []\n'
                '    for event in script:\n'
                '        kind = event["type"]\n'
                '        if kind == "type":\n'
                '            state["draft"] += event["text"]\n'
                '        elif kind == "add" and state["draft"].strip():\n'
                '            state["tasks"].append({"text": state["draft"].strip(), "done": False})\n'
                '            state["draft"] = ""\n'
                '        elif kind == "toggle":\n'
                '            task = state["tasks"][event["index"]]\n'
                '            task["done"] = not task["done"]\n'
                '        trace.append((kind, len(state["tasks"]), state["draft"]))\n'
                '    return state, trace\n'
                '\n'
                'script = [\n'
                '    {"type": "type", "text": "buy milk"},\n'
                '    {"type": "add"},\n'
                '    {"type": "type", "text": "walk dog"},\n'
                '    {"type": "add"},\n'
                '    {"type": "toggle", "index": 0},\n'
                ']\n'
                'state, trace = play({"tasks": [], "draft": ""}, script)\n'
                'for step in trace:\n'
                '    print(step)\n'
                'assert state["tasks"][0]["done"] is True\n'
                'assert len(state["tasks"]) == 2\n'
                'print("flow replayed from a script, one deterministic outcome")'
            ),
            variant_b='add a step that toggles a task back and assert the done flag returns to False',
            variant_c='append a blank add event and assert the trace shows the task count does not change',
            mistakes=[
                "Relying on clicking through the app by hand, so a fixed flow cannot be repeated or shared.",
                "Recording only the final state, so a divergence halfway through cannot be located.",
                "Forgetting the empty-input path, so adding a blank task slips through the playtest unnoticed.",
            ],
            q1=(
                "Why record a trace of every step instead of only the final state?",
                "The trace pinpoints the exact event where behaviour diverged, turning a failing flow into a specific, reproducible bug rather than a vague final mismatch.",
            ),
            homework=(
                "Write `play(state, script)` that replays typed events and returns the final state plus a per-step "
                "trace. Run a flow with two adds and a toggle, print the trace, and comment which line makes the "
                "replay deterministic."
            ),
            patterns=["def ", "return", "print("],
            mapping=(
                "This is the same as a scripted UI test in a real toolkit; capturing the event script from a manual "
                "session is how a desktop bug report becomes a replayable headless test."
            ),
        ),
        176: dict(
            topic="Package the app",
            idea=(
                "Packaging is a manifest, and a manifest is data you can validate before you ever bundle anything. "
                "Today you write the app's manifest as a dictionary: the name, a semantic version, the entry point, "
                "the list of files that ship, the dependency list and the minimum Python version. The entry point must "
                "be one of the shipped files, the version must be major.minor.patch, and for a stdlib-only build the "
                "dependency list must be empty; each rule becomes one check, and the checks return a list of problems "
                "rather than crashing on the first. Keeping the manifest in code lets you assert it in the same "
                "headless test run as everything else, so a missing file or a stray dependency fails long before a "
                "user sees a broken package. The list of files is also the answer to the question every packager "
                "asks: what is inside the box? Stating it explicitly prevents shipping a stray database or a test "
                "fixture by accident. The real tools — PyInstaller, Briefcase, a Debian control file — each consume a "
                "variant of this structure, so writing it by hand first makes their configuration files readable. "
                "Today you build a manifest for the task manager, run the checks, print the entry point and file "
                "count, and assert there are no problems. A clean manifest is the last gate before build day."
            ),
            code=(
                'manifest = {\n'
                '    "name": "taskboard",\n'
                '    "version": "1.0.0",\n'
                '    "entry": "main.py",\n'
                '    "files": ["main.py", "model.py", "theme.py", "README.md"],\n'
                '    "dependencies": [],\n'
                '    "python": ">=3.10",\n'
                '}\n'
                '\n'
                'def check(manifest):\n'
                '    problems = []\n'
                '    if manifest["entry"] not in manifest["files"]:\n'
                '        problems.append("entry point is not in the file list")\n'
                '    if manifest["dependencies"]:\n'
                '        problems.append("stdlib-only build should ship no dependencies")\n'
                '    if manifest["version"].count(".") != 2:\n'
                '        problems.append("version must be major.minor.patch")\n'
                '    return problems\n'
                '\n'
                'problems = check(manifest)\n'
                'print("entry:", manifest["entry"])\n'
                'print("files:", len(manifest["files"]))\n'
                'print("problems:", problems)\n'
                'assert problems == []\n'
                'print("manifest is valid: entry present, stdlib only, version pinned")'
            ),
            variant_b='remove "main.py" from the file list and assert `check` reports the missing entry point',
            variant_c='add a dependency to the manifest and assert the stdlib-only check flags it',
            mistakes=[
                "Naming an entry point that is not in the shipped files, so the build has nothing to launch.",
                "Never listing the files, so stray data or test fixtures get bundled by accident.",
                "Adding a dependency without recording it, so the package fails on a machine that lacks it.",
            ],
            q1=(
                "Why keep the manifest as data the code can validate?",
                "Then a missing entry point, a stray dependency or a malformed version fails in the headless test run, before any packaging step bundles a broken app.",
            ),
            homework=(
                "Write `check_manifest(manifest)` that returns a list of problems for a missing entry point, a "
                "non-empty dependency list or a bad version. Validate one good and one broken manifest, print both "
                "problem lists, and comment which line enforces the entry point rule."
            ),
            patterns=["def ", "return", "print("],
            mapping=(
                "PyInstaller spec files, Briefcase's `pyproject.toml` and Debian control files are all manifests; "
                "writing one by hand is what makes a real desktop release reproducible."
            ),
        ),
        177: dict(
            topic="Build day: accessibility pass",
            idea=(
                "Accessibility is not a coat of paint at the end; it is a set of properties you can audit over the "
                "widget tree, and today you write that audit. Each interactive widget must have an accessible label, "
                "images must have alt text or be marked decorative, and the focus order must be a deliberate sequence "
                "rather than whatever order the widgets happened to be created in. The audit is a walk that returns "
                "findings: for every entry, button and listbox without a label, and every unlabelled image, it records "
                "a short message naming the widget id. A parallel pass collects the focusable widgets in their "
                "intended tab order so you can assert the sequence is exactly what you designed. This is the same walk "
                "you wrote when you built the tree, applied to a different property, which is the point: once structure "
                "is data, every kind of check is another pass over it. Start the day by adding labels and a first-focus "
                "rule, then run the audit and watch the findings shrink to the one genuinely decorative item. Today you "
                "audit four widgets, print each finding and the focus order, and assert the order is entry, add, list "
                "while the logo image is flagged. Every modern toolkit exposes these properties; the audit keeps them "
                "honest."
            ),
            code=(
                'widgets = [\n'
                '    {"id": "entry", "kind": "entry", "label": "New task", "focusable": True},\n'
                '    {"id": "add", "kind": "button", "label": "Add", "focusable": True},\n'
                '    {"id": "logo", "kind": "image", "label": None, "focusable": False},\n'
                '    {"id": "list", "kind": "listbox", "label": "Tasks", "focusable": True},\n'
                ']\n'
                '\n'
                'def audit(widgets):\n'
                '    findings = []\n'
                '    for w in widgets:\n'
                '        if w["kind"] in ("entry", "button", "listbox") and not w["label"]:\n'
                '            findings.append(w["id"] + " has no accessible label")\n'
                '        if w["kind"] == "image" and not w["label"]:\n'
                '            findings.append(w["id"] + " needs alt text or is decorative")\n'
                '    return findings\n'
                '\n'
                'findings = audit(widgets)\n'
                'for finding in findings:\n'
                '    print("finding:", finding)\n'
                'order = [w["id"] for w in widgets if w["focusable"]]\n'
                'print("focus order:", order)\n'
                'assert order == ["entry", "add", "list"]\n'
                'assert any("logo" in finding for finding in findings)\n'
                'print("accessibility audit runs over the widget tree, no display needed")'
            ),
            variant_b='give the logo image alt text and assert the findings list becomes empty',
            variant_c='reorder the focusable widgets and assert a deliberately wrong focus order fails',
            mistakes=[
                "Leaving interactive controls unlabelled, so a screen reader announces only the widget type.",
                "Letting tab order follow creation order instead of a designed sequence.",
                "Treating accessibility as a final visual tweak rather than a property to audit in the tree.",
            ],
            q1=(
                "Why can accessibility be audited headlessly over the widget tree?",
                "Labels and focus order are properties stored on the widgets, so a walk can check them against the design without rendering anything.",
            ),
            homework=(
                "Write `audit_tree(widgets)` that returns findings for unlabelled controls and a separate focus order "
                "list. Run it over four widgets, print the findings and the order, and comment which line checks the "
                "tab sequence."
            ),
            patterns=["def ", "return", "print("],
            mapping=(
                "Tkinter's `takefocus` and accessible names, and Qt's accessibility interfaces, expose exactly these "
                "properties; auditing them in the tree is how a desktop app stays usable for every user."
            ),
        ),
        178: dict(
            topic="Build day: final review",
            idea=(
                "Final review is a list of checks, not an opinion, and today you turn the ship checklist into a "
                "function. Each check is a named boolean decision the app must satisfy before it is done: the scope "
                "fits the budget, validation rejects empty input, state round-trips through JSON, the headless tests "
                "pass, the focus order is documented. The review function runs the list, prints each check as ok or "
                "FAIL, collects the failures, and returns whether the app is ready to ship. Writing the checklist as "
                "data has two benefits that matter on a deadline: the whole team reviews the same list rather than "
                "arguing from memory, and any failing check names exactly one thing to fix instead of a vague 'not "
                "done yet'. Keep the checks honest by insisting each one is falsifiable — if you cannot describe what "
                "would make it fail, it is a slogan, not a check. This is also the moment to re-run the whole headless "
                "suite rather than trusting yesterday's run, because the last edits before shipping are exactly the "
                "ones most likely to break something unrelated. Today you run five checks, print the verdicts, and "
                "assert that a single known gap is reported as the only failure. The discipline is simple: no green "
                "board, no ship."
            ),
            code=(
                'def review(checks):\n'
                '    results = [(name, bool(ok)) for name, ok in checks]\n'
                '    failed = [name for name, ok in results if not ok]\n'
                '    return results, failed\n'
                '\n'
                'checks = [\n'
                '    ("scope fits budget", True),\n'
                '    ("validation covers empty input", True),\n'
                '    ("state round-trips through JSON", True),\n'
                '    ("headless tests pass", True),\n'
                '    ("focus order documented", False),\n'
                ']\n'
                'results, failed = review(checks)\n'
                'for name, ok in results:\n'
                '    print(("ok  " if ok else "FAIL"), name)\n'
                'print("ship ready:", not failed)\n'
                'assert failed == ["focus order documented"]\n'
                'print("a review is a list of checks, not an opinion")'
            ),
            variant_b='mark the focus order check as done and assert the app reports itself ready to ship',
            variant_c='add a falsifiable "empty state renders" check and print the new verdict list',
            mistakes=[
                "Reviewing from memory instead of a fixed checklist, so a different gap is missed each time.",
                "Writing checks that cannot fail, so a green board proves nothing about the app.",
                "Skipping the final headless run and trusting an earlier pass after late edits.",
            ],
            q1=(
                "What makes a review check useful rather than just motivational?",
                "It is falsifiable: you can say exactly what failure looks like, so a passing mark is evidence the app met a specific requirement.",
            ),
            homework=(
                "Write `review(checks)` that runs named boolean checks, prints ok or FAIL for each, and returns the "
                "list of failures. Include one failing check, print whether the app is ready, and comment which line "
                "defines the ship gate."
            ),
            patterns=["def ", "return", "print("],
            mapping=(
                "A shipping gate is standard desktop practice; turning the release checklist into a runnable function "
                "is what stops the last-minute regressions that reach users."
            ),
        ),
        179: dict(
            topic="Ship: retrospective and next steps",
            idea=(
                "A retrospective converts a finished build into knowledge, and the technique is summarising the work "
                "log as data. Each session is a record with a day, a kind — feature, test, polish, fix, package — and "
                "the hours spent, and a summarise function groups the hours by kind, totals them and counts the "
                "sessions. The point is not accounting for its own sake but seeing the shape of the build: how much "
                "time went to features versus the tests, polish and fixes that keep a product shippable, and whether "
                "the estimate you wrote on day one survived contact with reality. From that shape you choose the next "
                "steps honestly — add due dates, write the parser test you skipped, keep the headless suite green "
                "before every change — because the retrospective names what actually helped and what was avoided. It "
                "is also the moment to mark the habits worth carrying forward: writing scope first, modelling state as "
                "data, testing without a display, auditing the tree. Today you summarise five sessions, print the hours "
                "by kind and the total, and assert the total matches the records. Shipping is not the end of the loop; "
                "the retrospective is what makes the next loop shorter, and a small, tested, packaged task manager is "
                "a real thing you built from a written scope to a release."
            ),
            code=(
                'import json\n'
                '\n'
                'events = [\n'
                '    {"day": 171, "kind": "feature", "hours": 3},\n'
                '    {"day": 173, "kind": "polish", "hours": 2},\n'
                '    {"day": 174, "kind": "test", "hours": 2},\n'
                '    {"day": 176, "kind": "package", "hours": 1},\n'
                '    {"day": 177, "kind": "fix", "hours": 2},\n'
                ']\n'
                '\n'
                'def summarise(events):\n'
                '    hours = {}\n'
                '    for event in events:\n'
                '        hours[event["kind"]] = hours.get(event["kind"], 0) + event["hours"]\n'
                '    return {"total": sum(hours.values()), "by_kind": hours, "events": len(events)}\n'
                '\n'
                'report = summarise(events)\n'
                'print("retro:", json.dumps(report["by_kind"], sort_keys=True))\n'
                'print("total hours:", report["total"], "over", report["events"], "sessions")\n'
                'assert report["total"] == 10\n'
                'assert report["events"] == 5\n'
                'print("next: add due dates, keep the headless test habit")'
            ),
            variant_b='add two more sessions and assert the total and the session count both grow',
            variant_c='print the kind with the most hours and assert it matches your own read of the log',
            mistakes=[
                "Shipping and moving on without recording what took longer than expected and why.",
                "Counting only features and ignoring the test, polish and fix hours that made the app shippable.",
                "Writing next steps as vague intentions instead of the specific gap the log revealed.",
            ],
            q1=(
                "Why summarise the work log by kind in a retrospective?",
                "It shows where the time actually went, so the next estimate is grounded in the real split between features and the tests, polish and fixes that keep a product shippable.",
            ),
            homework=(
                "Write `summarise(events)` that groups hours by kind, totals them and counts sessions, returning a "
                "report dict. Run it over your own week of sessions, print the totals, and comment which line picks out "
                "the kind that consumed the most time."
            ),
            patterns=["def ", "return", "print("],
            mapping=(
                "Real desktop projects close with a retrospective and a short backlog; summarising the work log as "
                "data is how the next release estimate gets better instead of repeating the last one."
            ),
        ),
    },
)
