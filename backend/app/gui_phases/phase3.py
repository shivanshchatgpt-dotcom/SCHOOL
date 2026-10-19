"""GUI Applications phase 3, days 105-119: forms, data and validation.

Every example is stdlib-only, offline, headless and deterministic. Forms are
modelled as dictionaries, tables as lists of rows, persistence as JSON text,
and validation as small pure functions, so each idea runs and tests the same
way before Tkinter or Qt draws a single widget.
"""

PHASE = ("Forms, Data and Validation", "Turn user input into typed, validated and recoverable data before a toolkit ever draws a field.", {
    105: dict(
        topic="Orientation: forms are data entry",
        idea=(
            "Every desktop form starts as a promise: a set of named fields that will turn keystrokes into "
            "structured values. Before any toolkit draws an entry box, decide what the form collects, which "
            "type each answer has, and what an empty answer means. Model it as a dictionary keyed by field "
            "name, where each value records its type, its current value and whether it is required. That one "
            "decision changes how you work. Rendering becomes a loop over the dictionary, because a form is "
            "data entry and the screen is just a projection of it. Testing becomes ordinary Python: fill the "
            "dict, inspect it, compare it. It also exposes the questions a toolkit hides, such as what happens "
            "when a number field holds text, or when a checkbox is missing entirely. Today you build a "
            "registration form as nested dictionaries and print each field with its type and value. Notice "
            "that no widget appears anywhere, yet the shape of the eventual dialog is already visible. Keep "
            "that separation, because the rest of this phase adds parsing, validation, error display and "
            "persistence around this small core. The form is not the pixels; the pixels are one view of the "
            "form. Get the values right first and the widgets become a small rendering problem."
        ),
        code=(
            'def describe(form):\n'
            '    for name in sorted(form):\n'
            '        field = form[name]\n'
            '        kind, value = field["type"], field["value"]\n'
            '        print(f"{name:8} type={kind:6} value={value!r}")\n'
            '\n'
            'form = {\n'
            '    "name": {"type": "text", "value": "Ada"},\n'
            '    "age": {"type": "int", "value": 36},\n'
            '    "news": {"type": "bool", "value": True},\n'
            '}\n'
            'describe(form)\n'
            'print("fields:", len(form))\n'
            'assert len(form) == 3\n'
            'print("a form is data, not pixels")'
        ),
        variant_b='add a required "email" field with an empty value and print the form again',
        variant_c='write `values(form)` returning a plain name-to-value dict and print it',
        mistakes=[
            "Building widgets first and deciding what the form collects afterwards.",
            "Storing the same answer in several places so one copy is always stale.",
            "Treating an empty string, a missing key and a false value as the same thing.",
        ],
        q1=(
            "What does it mean to say a form is data entry rather than a set of widgets?",
            "The form is a named collection of typed values, and widgets are only one possible view that reads and writes those values.",
        ),
        homework=(
            "Write `form_fields(form)` that returns a list of (name, type) pairs sorted by name, then print "
            "one line per pair. Add a fourth field to the form and confirm the function needs no change; "
            "comment which line keeps the output independent of any widget."
        ),
        patterns=["def ", "return", "print("],
        mapping=(
            "Tkinter's `Entry` and Qt's `QLineEdit` are just editors for values you can model and test before "
            "the dialog exists."
        ),
    ),
    106: dict(
        topic="Field models and types",
        idea=(
            "Field models turn a vague label like age into a small contract. A field model says what kind of "
            "value it holds, such as text, integer, boolean or choice, what the default is, and how to convert "
            "a raw string from the screen into that kind. Once fields are described as data, the form itself "
            "can be generated: the code asks each field for a label, a default and a parser instead of "
            "hard-coding a different branch per input. It also keeps conversion rules in one place, so the "
            "same integer field behaves identically on a registration form and in a settings panel. The "
            "important distinction is between the value the user sees and the value the program stores; "
            "parsing is the bridge, and it must report failure rather than raise an exception the interface "
            "cannot show. In the example you define a tiny registry of field types and build a form from it. "
            "Each descriptor records a kind and a default, while a coerce function returns either a typed "
            "value or an error message. That pair is deliberate: the caller must handle both outcomes, which "
            "is exactly what a form needs. Keep descriptors declarative and keep behaviour in the registry, "
            "so adding a decimal field later does not touch every screen that shows one."
        ),
        code=(
            'def to_bool(raw):\n'
            '    return raw.strip().lower() in ("1", "true", "yes")\n'
            '\n'
            'REGISTRY = {\n'
            '    "text": (str, ""),\n'
            '    "int": (int, 0),\n'
            '    "bool": (to_bool, False),\n'
            '}\n'
            '\n'
            'def coerce(kind, raw):\n'
            '    parser, _default = REGISTRY[kind]\n'
            '    try:\n'
            '        return parser(raw), None\n'
            '    except (TypeError, ValueError):\n'
            '        return None, f"not a valid {kind}"\n'
            '\n'
            'raw = {"name": "Ada", "age": "36", "news": "yes"}\n'
            'for name, kind in [("name", "text"), ("age", "int"), ("news", "bool")]:\n'
            '    value, error = coerce(kind, raw[name])\n'
            '    print(name, kind, "->", value if error is None else error)\n'
            'assert coerce("int", "x")[1] == "not a valid int"\n'
            'print("field types centralise parsing")'
        ),
        variant_b='add a "choice" kind that accepts one of a fixed tuple and returns an error otherwise',
        variant_c='make coerce return (value, error) for an empty string without raising',
        mistakes=[
            "Spreading type checks across the form instead of describing a field once.",
            "Letting conversion raise so the interface has no message to display.",
            "Using a mutable default value that every form instance then shares.",
        ],
        q1=(
            "Why should a field describe its type instead of every screen checking it separately?",
            "One descriptor becomes the single place that defines parsing and defaults, so every screen treats the field consistently.",
        ),
        homework=(
            "Write `build_field(kind, label, default)` that returns a descriptor dict and a `coerce_all(spec, "
            "raw)` function that returns typed values plus a list of errors. Build three fields, coerce a good "
            "payload and a bad one, print both results, and comment where the registry is consulted."
        ),
        patterns=["def ", "REGISTRY", "print("],
        mapping=(
            "Qt's delegates and Tkinter validation hooks both attach a type and a conversion rule to an editor; "
            "this registry is the same idea without the toolkit."
        ),
    ),
    107: dict(
        topic="Parsing and formatting values",
        idea=(
            "Users type text; programs need numbers, dates and money. Parsing is the boundary where a string "
            "becomes a typed value, and formatting is the reverse journey when a value goes back to the "
            "screen. Treat both as named functions so every field uses the same rules and every error has a "
            "consistent message. A good parser strips surrounding whitespace, rejects empty input explicitly, "
            "and returns a result rather than throwing at the caller. A good formatter is stable: two decimal "
            "places for money, no trailing zeros for counts, and a fixed separator so the display does not "
            "drift with locale settings. Rounding deserves its own sentence, because floats and money "
            "disagree. The lazy and correct approach is to store money as integer cents and divide only when "
            "displaying. Today you parse a price typed with a comma and a currency symbol, format it back with "
            "two decimals, and reject an empty or non-numeric amount. You will see that the round trip is "
            "only safe when both functions agree on the unit. That agreement is what later validation and "
            "persistence rely on, and it prevents the classic bug where a value is saved as text and then "
            "compared as a number."
        ),
        code=(
            'def parse_money(raw):\n'
            '    cleaned = raw.replace("$", "").replace(",", "").strip()\n'
            '    if not cleaned:\n'
            '        return None, "amount is required"\n'
            '    try:\n'
            '        return int(round(float(cleaned) * 100)), None\n'
            '    except ValueError:\n'
            '        return None, "amount must be a number"\n'
            '\n'
            'def format_money(cents):\n'
            '    sign = "-" if cents < 0 else ""\n'
            '    cents = abs(cents)\n'
            '    return f"{sign}${cents // 100}.{cents % 100:02d}"\n'
            '\n'
            'for raw in ["$1,234.50", "12", "  ", "abc"]:\n'
            '    cents, error = parse_money(raw)\n'
            '    shown = format_money(cents) if error is None else error\n'
            '    print(repr(raw), "->", shown)\n'
            'assert format_money(parse_money("$1,234.50")[0]) == "$1234.50"\n'
            'print("parse in, format out, same unit")'
        ),
        variant_b='accept a trailing percent sign and return basis points as an integer',
        variant_c='add a format_count function that omits trailing zeros and prints three examples',
        mistakes=[
            "Storing money as a float and losing a cent to rounding on the way back.",
            "Formatting in several places so the same value appears differently on two screens.",
            "Letting an empty string reach float() instead of returning a clear error.",
        ],
        q1=(
            "Why store money as integer cents rather than a float?",
            "Cents stay exact through arithmetic and serialisation, while binary floats can lose a cent during rounding.",
        ),
        homework=(
            "Write `parse_quantity(raw)` and `format_quantity(n)` for whole units, returning an error string "
            "for blanks and decimals. Parse four inputs including one bad value, print each result, and comment "
            "which line guarantees the display uses the stored unit."
        ),
        patterns=["def ", "return", "print("],
        mapping=(
            "Every toolkit entry returns a string, so desktop forms always need an explicit parse and format "
            "layer before the value reaches a model or a database."
        ),
    ),
    108: dict(
        topic="Validation rules as functions",
        idea=(
            "A validation rule is a function that takes a field value and returns either nothing or a "
            "message. Small rules compose: required, minimum length, range, pattern. Keeping them as separate "
            "functions means you can test each one by calling it with a value, and you can report every "
            "problem at once instead of stopping at the first failure. A form-level validator then loops over "
            "the fields and collects messages into a dictionary keyed by field name. That dictionary is the "
            "contract the view renders. The rule functions must be pure: no reading widgets, no printing, no "
            "global flags. If a rule needs context, such as confirming that two passwords match, pass the "
            "whole form to a separate form-level check instead of smuggling state in. In the example you "
            "write three small rules and a validate function that applies them and reports a list of errors. "
            "Notice how easy it is to add a fourth rule without touching the widgets or the submit handler. "
            "That is the test of a good validation design. Each rule stays tiny enough to read and test in one "
            "sitting. The next lesson places these messages next to the fields they belong to, which is only "
            "possible because they are already keyed by field name."
        ),
        code=(
            'def required(value):\n'
            '    return None if str(value).strip() else "this field is required"\n'
            '\n'
            'def min_len(n):\n'
            '    def rule(value):\n'
            '        text = str(value)\n'
            '        return None if len(text) >= n else f"use at least {n} characters"\n'
            '    return rule\n'
            '\n'
            'RULES = {"name": [required, min_len(3)], "email": [required]}\n'
            '\n'
            'def validate(form):\n'
            '    errors = {}\n'
            '    for field, rules in RULES.items():\n'
            '        for rule in rules:\n'
            '            message = rule(form.get(field, ""))\n'
            '            if message:\n'
            '                errors[field] = message\n'
            '                break\n'
            '    if form.get("email") != form.get("confirm"):\n'
            '        errors["confirm"] = "values must match"\n'
            '    return errors\n'
            '\n'
            'print(validate({"name": "Al", "email": "a@b.c", "confirm": "a@b.c"}))\n'
            'print(validate({"name": "", "email": "a@b.c", "confirm": "x"}))\n'
            'assert validate({"name": "Ada", "email": "a@b.c", "confirm": "a@b.c"}) == {}\n'
            'print("rules are small, pure and composable")'
        ),
        variant_b='add a max_len rule and show a value that fails both length rules',
        variant_c='return a list of (field, message) pairs instead of a dict and print both shapes',
        mistakes=[
            "Validating by printing from inside a rule instead of returning a message.",
            "Stopping at the first error so the user fixes fields one at a time.",
            "Duplicating a rule in the submit handler and letting the two copies drift.",
        ],
        q1=(
            "Why return a message from a rule instead of raising an exception?",
            "The caller can collect every message and show them together, and a bad field stays an ordinary value rather than a crash.",
        ),
        homework=(
            "Write `validate(form)` using three rule functions, one of them built by a `range_rule(low, high)` "
            "factory. Test one completely valid form and one with two problems, print both error dicts, and "
            "comment which loop collects the messages."
        ),
        patterns=["def ", "range_rule", "validate("],
        mapping=(
            "Tkinter validation callbacks and Qt validators both run per-field checks; keeping the rules pure "
            "lets you test them once and attach them to any editor."
        ),
    ),
    109: dict(
        topic="Surfacing errors next to fields",
        idea=(
            "An error message is useful only when it appears at the right place. A banner at the bottom saying "
            "something went wrong forces the user to hunt; a message under the offending entry tells them "
            "exactly where to look. The headless version of that idea is a mapping from field name to message, "
            "plus a render function that prints each field with its label, value and error. Nothing about the "
            "rendering loop is toolkit-specific: a Tkinter label or a Qt form row would consume the same "
            "mapping. Keep three distinctions clear. A field can be valid but untouched, invalid and "
            "untouched, or invalid and touched. Shouting before the user has edited a field is hostile, so "
            "the example keeps a touched set and only surfaces errors for fields already visited. It also "
            "keeps the form usable by printing a summary count, which is what a status bar would display. The "
            "render output is deterministic text, so you can assert on it. When you later replace the text "
            "with widgets, the data structure does not change. Remember that clearing an error is as "
            "important as setting one; a stale message next to a corrected field erodes trust faster than a "
            "missing message."
        ),
        code=(
            'FIELDS = ["email", "age"]\n'
            'ERRORS = {"email": "invalid address", "age": "must be 18 or older"}\n'
            'TOUCHED = {"email"}\n'
            '\n'
            'def render(fields, values, errors, touched):\n'
            '    lines = []\n'
            '    for field in fields:\n'
            '        error = errors.get(field, "") if field in touched else ""\n'
            '        marker = "!" if error else " "\n'
            '        line = f"{marker} {field:6} {values.get(field, \'\'):12} {error}"\n'
            '        lines.append(line.rstrip())\n'
            '    return lines\n'
            '\n'
            'values = {"email": "ada@", "age": "17"}\n'
            'shown = render(FIELDS, values, ERRORS, TOUCHED)\n'
            'for line in shown:\n'
            '    print(line)\n'
            'visible = sum(1 for f in FIELDS if f in TOUCHED and f in ERRORS)\n'
            'print("visible errors:", visible)\n'
            'assert shown[0].startswith("!") and shown[1].startswith(" ")\n'
            'print("errors follow the field, not a banner")'
        ),
        variant_b='mark corrected fields with a check and remove their error from the mapping',
        variant_c='render a field summary that counts shown errors and untouched fields',
        mistakes=[
            "Showing every error immediately, before the user has edited anything.",
            "Leaving an old message in place after the value becomes valid.",
            "Rendering the error list in a separate panel from the fields it describes.",
        ],
        q1=(
            "Why key error messages by field name instead of keeping one list of strings?",
            "Each message has an address, so the view can place it beside the right editor and clear it independently.",
        ),
        homework=(
            "Write `render_rows(fields, values, errors)` that returns one line per field with a marker and a "
            "message, showing errors only for touched fields passed in a set. Print the rows for two touched "
            "sets, and comment which line decides whether a message is visible."
        ),
        patterns=["def ", "touched", "print("],
        mapping=(
            "Desktop form layouts put a helper label under each editor; this mapping is exactly what such a "
            "label reads, so the error placement is decided before layout."
        ),
    ),
    110: dict(
        topic="Required, optional and defaults",
        idea=(
            "Required and optional are not the same as empty and non-empty. An optional text field that is "
            "blank is valid; a required text field that is blank is an error; an optional field with a "
            "default is pre-filled and still optional in the sense that clearing it is allowed. Getting these "
            "three cases into one model prevents most form bugs. Store for each field whether it is required, "
            "what its default is, and how to interpret an empty raw value. Then resolve the form in one pass: "
            "apply defaults to missing values, validate required fields, and skip value rules for fields the "
            "user left blank when they are optional. A useful distinction is between missing and empty: a key "
            "absent from the submitted dictionary is not the same as a key whose value is the empty string, "
            "and a choice field may legitimately use None. The example shows a profile form with a required "
            "email, an optional nickname with a default, and an optional age. It prints the resolved values "
            "and the errors. The lesson is that defaults belong in the model, never in the widget "
            "constructor, or you end up with two places that decide what a blank field means."
        ),
        code=(
            'SPEC = {\n'
            '    "email": {"required": True, "default": ""},\n'
            '    "nickname": {"required": False, "default": "friend"},\n'
            '    "age": {"required": False, "default": None},\n'
            '}\n'
            '\n'
            'def resolve(spec, submitted):\n'
            '    values, errors = {}, []\n'
            '    for name, field in spec.items():\n'
            '        raw = submitted.get(name, field["default"])\n'
            '        if str(raw).strip() == "" and field["required"]:\n'
            '            errors.append(f"{name} is required")\n'
            '            continue\n'
            '        if str(raw).strip() == "":\n'
            '            values[name] = field["default"]\n'
            '        else:\n'
            '            values[name] = raw\n'
            '    return values, errors\n'
            '\n'
            'values, errors = resolve(SPEC, {"email": "ada@example.com", "age": "36"})\n'
            'print("resolved:", values)\n'
            'print("errors:", errors)\n'
            'assert values["nickname"] == "friend"\n'
            'assert resolve(SPEC, {"email": " "})[1] == ["email is required"]\n'
            'print("required, optional and defaults resolved once")'
        ),
        variant_b='treat a key present with None as a deliberate clear instead of a missing value',
        variant_c='add a required choice field whose default is None and show the resulting error',
        mistakes=[
            "Setting defaults in the widget so a cleared optional field looks required.",
            "Confusing a missing key with an empty string and dropping one of them.",
            "Validating optional blank values with rules meant for filled ones.",
        ],
        q1=(
            "Why is an optional blank field valid while a required blank field is an error?",
            "Optionality changes what blank means: for an optional field blank is an accepted answer, while a required field needs a real value.",
        ),
        homework=(
            "Write `resolve(spec, submitted)` that returns values and errors, applies defaults for missing or "
            "blank optional fields, and reports each missing required field. Run it with one complete payload "
            "and one missing required value, print both results, and comment where defaults are applied."
        ),
        patterns=["def ", "required", "print("],
        mapping=(
            "Qt's `QSettings` and Tkinter preference panels both need exactly this rule: absent values fall "
            "back to defaults, but a required field must be present."
        ),
    ),
    111: dict(
        topic="Form state machines",
        idea=(
            "Forms are little state machines, whether or not you name the states. A fresh form is clean; "
            "editing makes it dirty; a valid dirty form can be submitted; a successful submission moves it to "
            "confirmed. Add an error state and a cancelled state and you have the whole life cycle. The value "
            "of writing states down is that illegal transitions become visible: you cannot submit a clean "
            "form, you cannot confirm one with errors, and you cannot edit after confirmation without "
            "starting a new draft. Implement transitions as a table mapping state and event to a new state, "
            "then drive the form with events. This is the same dispatcher pattern from the foundations phase, "
            "applied to something users recognise. It also gives you a clean place to decide what a button "
            "does: its enabled-ness is a property of the current state, not a flag toggled by callbacks. In "
            "the example a form moves from empty to dirty to valid to submitted, with an invalid edit in "
            "between showing the error branch. Print each transition and assert the final state. When the "
            "flow grows, the table is still small enough to read at a glance, which is the point of naming "
            "the states at all."
        ),
        code=(
            'TRANSITIONS = {\n'
            '    ("empty", "edit"): "dirty",\n'
            '    ("dirty", "validate_ok"): "valid",\n'
            '    ("dirty", "validate_fail"): "error",\n'
            '    ("error", "edit"): "dirty",\n'
            '    ("valid", "submit"): "submitted",\n'
            '}\n'
            '\n'
            'def step(state, event):\n'
            '    target = TRANSITIONS.get((state, event))\n'
            '    if target is None:\n'
            '        print(f"  refused {event} in {state}")\n'
            '        return state\n'
            '    print(f"  {state} --{event}--> {target}")\n'
            '    return target\n'
            '\n'
            'state = "empty"\n'
            'for event in ["edit", "validate_fail", "edit", "validate_ok", "submit", "edit"]:\n'
            '    state = step(state, event)\n'
            'assert state == "submitted"\n'
            'print("final:", state)'
        ),
        variant_b='add a "cancel" event from every non-submitted state and print the new flow',
        variant_c='make step return (state, changed) and assert refused events report False',
        mistakes=[
            "Toggling button states from callbacks instead of deriving them from the form state.",
            "Allowing submit from every state, so a clean or invalid form can be confirmed.",
            "Letting an unknown event silently do nothing without recording that it was refused.",
        ],
        q1=(
            "What does a transition table make easier than scattered if-statements?",
            "Every legal move is visible in one place, so impossible transitions and missing events are easy to spot and test.",
        ),
        homework=(
            "Write `step(state, event, table)` that returns the next state, refusing unknown pairs, and drive "
            "a form through four events including one refusal. Print each transition, assert the final state, "
            "and comment which lookup enforces the rule."
        ),
        patterns=["def ", "TRANSITIONS", "print("],
        mapping=(
            "Real dialogs enable and disable OK and Apply buttons from state; a transition table is the "
            "testable form of that policy, independent of Tkinter or Qt."
        ),
    ),
    112: dict(
        topic="Submission and confirmation",
        idea=(
            "Submission is where a form stops being a draft and becomes a fact. The handler should do three "
            "things in order: validate, produce a result, and return a confirmation that the view can show. "
            "Keep those steps separate so a failed validation never looks like a successful save. A "
            "confirmation is not just a success flag; it should carry the values that were accepted and "
            "something stable the user can refer to, such as a reference number. Because this curriculum "
            "forbids clocks and random identifiers, the example uses a counter to build a deterministic "
            "reference. That is not a limitation of desktop apps but a reminder that identifiers should come "
            "from one authority, not from whatever the interface happens to have handy. The handler also "
            "needs to be idempotent: pressing the button twice should not create two records. The example "
            "guards with the form state, accepting only from the valid state and moving to confirmed "
            "afterwards. Print the confirmation, attempt a second submission, and show that it is refused. A "
            "refused submission returns the state unchanged with a message, never a silent no-op. When you "
            "wire a real button, this handler stays the same; only the rendering of the confirmation changes. "
            "The final lesson of the phase builds a checklist from these habits."
        ),
        code=(
            'def submit(form, state, counter):\n'
            '    if state != "valid":\n'
            '        return state, counter, "cannot submit yet"\n'
            '    ref = f"REG-{counter:03d}"\n'
            '    return "confirmed", counter + 1, f"thanks {form[\'name\']}, reference {ref}"\n'
            '\n'
            'form = {"name": "Ada", "email": "ada@example.com"}\n'
            'state, counter, message = submit(form, "valid", 7)\n'
            'print(message)\n'
            'print("state:", state, "counter:", counter)\n'
            'state, counter, message = submit(form, state, counter)\n'
            'print(message)\n'
            'assert state == "confirmed" and counter == 8\n'
            'print("second click creates no second record")'
        ),
        variant_b='return a dict confirmation with reference, name and accepted fields instead of a sentence',
        variant_c='add a reason to the refusal and assert the counter is unchanged',
        mistakes=[
            "Saving before validating, so an invalid form still leaves a record behind.",
            "Generating the reference from a widget value instead of a single authority.",
            "Letting a double click submit the same form twice and duplicate the record.",
        ],
        q1=(
            "Why must submission check the form state instead of trusting the button?",
            "The handler can be called by a keyboard shortcut, a test or a double click, so the state is the only reliable guard against an invalid or repeated save.",
        ),
        homework=(
            "Write `submit(form, state, counter)` returning the next state, the next counter and a "
            "confirmation dict. Show one accepted submission and one refused repeat, print both confirmation "
            "dicts, and comment which line enforces idempotence."
        ),
        patterns=["def ", "submit(", "print("],
        mapping=(
            "A desktop OK button ultimately calls a handler like this; the confirmation dialog should display "
            "the returned receipt, not a separately built success message."
        ),
    ),
    113: dict(
        topic="File and folder dialogs",
        idea=(
            "File and folder dialogs are ordinary functions that return a path or nothing, but they feel "
            "special because they block the app and touch the outside world. Before calling one, decide what "
            "you accept, what you do when the user cancels, and how you display a long path. Model the dialog "
            "as data in tests: a starting folder, a list of entries, a chosen entry. That makes the filtering "
            "rules testable without opening a window. A browser dialog usually needs an extension filter, a "
            "way to distinguish files from folders, and a sensible empty state. The example lists a fixed set "
            "of entries, filters for a document extension, prints the visible names, and simulates choosing "
            "one. It also shows the difference between an absolute path and the name shown to the user; keep "
            "the full path in the model and display the last component. Only the call that opens the window is "
            "untestable, so keep everything else here. Cancellation is a normal outcome, not "
            "an error, so return None and let the caller decide. When you move to Tkinter or Qt, only the call "
            "that produces the path changes. The model, the filter and the error handling you wrote here are "
            "reusable, which is exactly why this is worth doing headlessly."
        ),
        code=(
            'ENTRIES = [\n'
            '    {"name": "notes.txt", "kind": "file"},\n'
            '    {"name": "report.pdf", "kind": "file"},\n'
            '    {"name": "drafts", "kind": "folder"},\n'
            '    {"name": "photo.png", "kind": "file"},\n'
            ']\n'
            '\n'
            'def visible(entries, ext):\n'
            '    return [e for e in entries if e["kind"] == "folder" or e["name"].endswith(ext)]\n'
            '\n'
            'def display(entry):\n'
            '    return entry["name"] + ("/" if entry["kind"] == "folder" else "")\n'
            '\n'
            'shown = visible(ENTRIES, ".pdf")\n'
            'for entry in shown:\n'
            '    print(display(entry))\n'
            'print("count:", len(shown))\n'
            'choice = shown[0]["name"] if shown else None\n'
            'print("chosen:", choice)\n'
            'assert choice == "report.pdf"\n'
            'print("cancel returns None; a path is just data")'
        ),
        variant_b='filter for several extensions at once and keep folders visible above files',
        variant_c='return the full path for a chosen entry and print it beside the display name',
        mistakes=[
            "Treating a cancelled dialog as an error and showing a failure message.",
            "Filtering only by the text after the last dot, so folders disappear from the browser.",
            "Showing the full path in the list instead of the entry name the user recognises.",
        ],
        q1=(
            "Why should a cancelled file dialog return None instead of raising?",
            "Cancelling is a normal user choice, so the caller can simply keep the previous value or do nothing without an error path.",
        ),
        homework=(
            "Write `choose(entries, ext)` that returns the first matching file entry or None, and a "
            "`label(entry)` helper for display. Call it with a matching extension and with an unmatched one, "
            "print both results, and comment which line keeps cancellation non-exceptional."
        ),
        patterns=["def ", "None", "print("],
        mapping=(
            "Tkinter's `filedialog.askopenfilename` and Qt's `QFileDialog` both return an empty value on "
            "cancel; the filtering and display logic here wraps either one unchanged."
        ),
    ),
    114: dict(
        topic="Tables and list views",
        idea=(
            "A table is a list of rows plus a description of columns. Once you see it that way, alignment, "
            "sorting and rendering stop being widget tricks. Each column has a key, a heading, a width and an "
            "alignment rule. The renderer computes the width from the heading and the longest cell, then "
            "prints each row padded to fit. Numeric columns align right so digits line up; text columns align "
            "left. A list view is the same structure with one column, which is why the two controls share so "
            "much behaviour. The example builds a small contacts table, computes column widths, prints a "
            "header and three rows, then asserts that every row provides every column. That last check "
            "catches the most common table bug: a row missing a field renders silently shifted. Keep the rows "
            "as dictionaries rather than tuples so a missing key is an explicit error and a new column does "
            "not force every caller to change position. When the table grows, pagination and sorting are "
            "operations on the row list, not on the widget. The same data structure feeds a Tkinter Treeview "
            "or a Qt table model with no change to the computation, which is the reason to get the structure "
            "right first."
        ),
        code=(
            'ROWS = [\n'
            '    {"name": "Ada", "city": "London", "score": 91},\n'
            '    {"name": "Grace", "city": "New York", "score": 88},\n'
            '    {"name": "Alan", "city": "Manchester", "score": 74},\n'
            ']\n'
            'COLUMNS = [("name", 10, "<"), ("city", 12, "<"), ("score", 5, ">")]\n'
            '\n'
            'def render(rows, columns):\n'
            '    header = []\n'
            '    for heading, width, align in columns:\n'
            '        header.append(heading.ljust(width) if align == "<" else heading.rjust(width))\n'
            '    print(" | ".join(header))\n'
            '    for row in rows:\n'
            '        cells = []\n'
            '        for key, width, align in columns:\n'
            '            text = str(row[key])\n'
            '            cells.append(text.ljust(width) if align == "<" else text.rjust(width))\n'
            '        print(" | ".join(cells))\n'
            '\n'
            'render(ROWS, COLUMNS)\n'
            'assert all(all(key in row for key, _w, _a in COLUMNS) for row in ROWS)\n'
            'print("rows:", len(ROWS), "columns:", len(COLUMNS))'
        ),
        variant_b='add an "email" column and let the renderer compute its width from the longest value',
        variant_c='render a single-column list view of names and assert the same renderer still works',
        mistakes=[
            "Keeping rows as tuples so adding a column shifts every value by one position.",
            "Aligning numeric columns left, which makes digits hard to compare.",
            "Rendering rows before checking that each one has every declared column.",
        ],
        q1=(
            "Why keep table rows as dictionaries keyed by column name?",
            "A missing or added column is explicit and does not silently shift the values of neighbouring cells.",
        ),
        homework=(
            "Write `render_table(rows, columns)` that prints a padded header and one line per row, using "
            "left alignment for text and right alignment for numbers. Add a fourth row, print the table, and "
            "comment which loop keeps every cell aligned to its column."
        ),
        patterns=["def ", "render_table", "print("],
        mapping=(
            "Tkinter's `Treeview` and Qt's `QTableView` consume rows and column definitions; the alignment and "
            "width arithmetic is the model layer they expect."
        ),
    ),
    115: dict(
        topic="Filtering and search",
        idea=(
            "Filtering is a pure function from rows and a query to a smaller list. Search should be "
            "case-insensitive, should ignore surrounding whitespace, and should look at the fields the user "
            "expects, not at every internal key. Sorting is another pure function and usually pairs with "
            "filtering: filter first, sort second, then render. Keeping the three steps separate makes each "
            "one testable and makes the empty result an ordinary case instead of a special branch hidden in "
            "the widget. An empty query returns every row, which is the natural default. A useful habit is to expose the active filter in the same state dictionary as the "
            "rows, so the view can show what is applied and a reset is just setting the query back to empty. "
            "The example has four contacts, filters by a two-letter query across name and city, sorts the "
            "result by name, and prints both the matches and the count. It then asserts that an unmatched "
            "query returns an empty list rather than None, because callers should not have to handle two "
            "shapes of nothing. When you connect a search box, call this function on every keystroke; it is "
            "cheap for small lists and predictable. For large data sets the same shape survives, only the "
            "indexing strategy changes."
        ),
        code=(
            'ROWS = [\n'
            '    {"name": "Ada", "city": "London"},\n'
            '    {"name": "Grace", "city": "New York"},\n'
            '    {"name": "Alan", "city": "Manchester"},\n'
            '    {"name": "Emma", "city": "Madrid"},\n'
            ']\n'
            '\n'
            'def search(rows, query, keys):\n'
            '    q = query.strip().casefold()\n'
            '    if not q:\n'
            '        return list(rows)\n'
            '    return [r for r in rows if any(q in str(r[k]).casefold() for k in keys)]\n'
            '\n'
            'def sorted_by(rows, key):\n'
            '    return sorted(rows, key=lambda r: r[key].casefold())\n'
            '\n'
            'hits = sorted_by(search(ROWS, "ma", ("name", "city")), "name")\n'
            'for row in hits:\n'
            '    print(row["name"], "-", row["city"])\n'
            'print("matches:", len(hits))\n'
            'assert search(ROWS, "zzz", ("name",)) == []\n'
            'print("filter, sort, render are separate steps")'
        ),
        variant_b='search only one key and show that a city match disappears from the results',
        variant_c='add a `visible(rows, query)` wrapper that returns both hits and the active query',
        mistakes=[
            "Filtering with a case-sensitive comparison so a capitalised query misses matches.",
            "Sorting before filtering, then assuming the match count is still correct.",
            "Returning None for no matches so every caller needs an extra check.",
        ],
        q1=(
            "Why is returning an empty list better than returning None when nothing matches?",
            "The result keeps one shape, so the renderer and count logic can run without a special missing-value branch.",
        ),
        homework=(
            "Write `filter_rows(rows, query, keys)` and `sort_rows(rows, key)` as separate functions, then "
            "compose them and print the names and the match count. Test a blank query and an unmatched query, "
            "and comment which line makes the search case-insensitive."
        ),
        patterns=["def ", "casefold", "print("],
        mapping=(
            "Desktop search boxes call a filter on every edit; keeping it pure means the same function can "
            "back a Tkinter entry, a Qt line edit or a command-line check."
        ),
    ),
    116: dict(
        topic="Persistence to JSON",
        idea=(
            "JSON is the friendliest persistence format for small desktop apps: text, readable, and already "
            "in the standard library. The important decisions are what to save and how to recognise it later. "
            "Save a version number with the payload, keep the structure flat where possible, and store typed "
            "values as JSON can represent them. Dates become ISO strings, money becomes integer cents, and "
            "sets become sorted lists. Loading must be defensive: a missing file, malformed text or an old "
            "version should produce a clear failure path rather than a half-populated form. The example "
            "serialises a small profile with json.dumps, prints the text, loads it back with json.loads, and "
            "asserts that the round trip preserves the values and their types. It also shows the version "
            "check that lets a future loader migrate old data. Do not write files in this exercise; the "
            "string is the whole payload, which is exactly what a real save function would hand to disk. That "
            "separation makes the encoding testable and keeps file errors out of the model. The text produced "
            "by json.dumps is stable enough to diff in a test. When you add a "
            "settings file later, the same encode, version and decode pattern applies with defaults merged "
            "in."
        ),
        code=(
            'import json\n'
            '\n'
            'def save(profile):\n'
            '    payload = {"version": 2, "profile": profile}\n'
            '    return json.dumps(payload, sort_keys=True)\n'
            '\n'
            'def load(text):\n'
            '    data = json.loads(text)\n'
            '    if data.get("version") != 2:\n'
            '        return None, "unsupported version"\n'
            '    return data["profile"], None\n'
            '\n'
            'profile = {"name": "Ada", "age": 36, "tags": ["math", "code"]}\n'
            'text = save(profile)\n'
            'print(text)\n'
            'restored, error = load(text)\n'
            'print("restored:", restored, "error:", error)\n'
            'assert restored == profile and error is None\n'
            'print("round trip keeps values and types")'
        ),
        variant_b='add a saved_at field as a fixed ISO date string and show it survives the round trip',
        variant_c='load an older version payload and return a migration message instead of data',
        mistakes=[
            "Saving a Python object with repr and hoping it loads back as the same type.",
            "Forgetting a version field, so old and new payloads cannot be told apart.",
            "Assuming a missing key exists and populating half a form before failing.",
        ],
        q1=(
            "Why include a version number in a saved JSON payload?",
            "It lets the loader detect the format it received and choose a migration or a clear error instead of guessing.",
        ),
        homework=(
            "Write `to_json(state)` and `from_json(text)` for a profile with a name and a list of tags, "
            "returning (data, error) on load. Round-trip one profile and print both the text and the restored "
            "dict; comment which line proves the value types survived."
        ),
        patterns=["def ", "json.", "print("],
        mapping=(
            "Both Tkinter and Qt apps usually persist a small JSON file under the user profile; keeping "
            "encode and decode separate is what makes that file safe to evolve."
        ),
    ),
    117: dict(
        topic="Settings and preferences",
        idea=(
            "Settings are a form that persists, with one extra rule: missing values must fall back to "
            "defaults instead of failing. The clean model is a dictionary of defaults, a dictionary of saved "
            "values, and a merge function that keeps only keys the app knows about and coerces each value to "
            "its expected type. Ignoring unknown keys matters because an older or newer version may have "
            "written something this build does not understand. Coercion also protects against a settings file "
            "edited by hand. It matters because JSON round trips "
            "preserve types, but old versions and hand edits do not. The example defines defaults for "
            "theme, font size and autosave interval, applies a saved payload that is missing one key and "
            "holds a numeric string for another, and prints the resolved settings. It asserts that the "
            "default survived and the string became an integer. The same function can back a settings panel: "
            "the panel edits a copy, and saving merges it over the defaults before encoding. Keep the "
            "defaults in one place, never duplicated in the dialog constructor, or resetting a setting will "
            "restore the wrong value. This is the same required, optional and defaults problem from earlier "
            "in the phase, applied to configuration rather than user data."
        ),
        code=(
            'import json\n'
            '\n'
            'DEFAULTS = {"theme": "light", "font_size": 12, "autosave_seconds": 30}\n'
            '\n'
            'def resolve(saved):\n'
            '    settings = dict(DEFAULTS)\n'
            '    for key, default in DEFAULTS.items():\n'
            '        if key in saved:\n'
            '            settings[key] = type(default)(saved[key])\n'
            '    return settings\n'
            '\n'
            'saved = json.loads(\'{"theme": "dark", "font_size": "14", "unknown": true}\')\n'
            'settings = resolve(saved)\n'
            'print(settings)\n'
            'print("resolved keys:", sorted(settings))\n'
            'assert settings == {"theme": "dark", "font_size": 14, "autosave_seconds": 30}\n'
            'print("unknown keys ignored, defaults preserved")'
        ),
        variant_b='add a boolean "confirm_exit" setting and coerce strings like "false" correctly',
        variant_c='return the list of ignored keys alongside the resolved settings',
        mistakes=[
            "Letting a missing saved key erase the default and produce None.",
            "Trusting the stored type so a hand-edited string breaks the font size.",
            "Copying default values into every dialog instead of one settings module.",
        ],
        q1=(
            "Why merge saved settings over a defaults dictionary?",
            "Missing keys then keep a known good value, while present keys override only what the user actually changed.",
        ),
        homework=(
            "Write `resolve(saved, defaults)` that merges known keys, coerces each to the default type and "
            "ignores unknown keys. Test a partial payload with one wrong type, print the resolved settings and "
            "the ignored keys, and comment where coercion happens."
        ),
        patterns=["def ", "DEFAULTS", "print("],
        mapping=(
            "Preference dialogs in Tkinter and Qt read a settings store at startup; this merge function is the "
            "policy layer between a saved file and the widgets that display it."
        ),
    ),
    118: dict(
        topic="Autosave and recovery",
        idea=(
            "Autosave is a promise that unsaved work survives a crash, and recovery is the code that keeps "
            "that promise. The practical design is a snapshot: every N changes, encode the current state and "
            "keep the last few snapshots labelled with a change counter. On startup, load the newest snapshot "
            "that decodes correctly and is newer than the last explicit save; if none qualifies, start clean. "
            "Counters rather than timestamps keep the logic deterministic and testable, and the ordering is "
            "all the recovery decision needs. The example records changes to a draft note, takes a snapshot "
            "every two changes, simulates a failure by dropping the live state, then recovers the newest "
            "snapshot. A snapshot is cheap because the state is a plain dictionary that copies in one line. It "
            "prints each snapshot label and the recovered text, and asserts that older work is "
            "never chosen over newer work. Notice that recovery is a pure function of the snapshot list; "
            "nothing needs a filesystem to be correct. When you write snapshots to disk later, the same "
            "payload goes through json.dumps, one file per label. Also decide when to discard snapshots: "
            "after a successful save, or when the user confirms they do not want to recover. Leaving them "
            "forever is how autosave turns into clutter."
        ),
        code=(
            'def snapshot(state, change):\n'
            '    return {"change": change, "state": dict(state)}\n'
            '\n'
            'def recover(snapshots, last_saved):\n'
            '    valid = [s for s in snapshots if s["change"] > last_saved]\n'
            '    return max(valid, key=lambda s: s["change"]) if valid else None\n'
            '\n'
            'snaps = []\n'
            'draft = {"text": ""}\n'
            'for change, word in enumerate(["one", "two", "three", "four"], start=1):\n'
            '    draft = {"text": (draft["text"] + " " + word).strip()}\n'
            '    if change % 2 == 0:\n'
            '        snaps.append(snapshot(draft, change))\n'
            '        print("snapshot at change", change, "->", draft["text"])\n'
            '\n'
            'draft = {"text": ""}\n'
            'print("live state lost:", draft)\n'
            'best = recover(snaps, last_saved=1)\n'
            'print("recovered:", best["state"]["text"], "from change", best["change"])\n'
            'assert best["state"]["text"] == "one two three four"\n'
            'print("recovery picks the newest unsaved snapshot")'
        ),
        variant_b='snapshot every third change and show recovery falling back to an earlier label',
        variant_c='ignore the newest snapshot when it fails a decode check and pick the next one',
        mistakes=[
            "Saving on a clock interval, which is untestable and loses the change ordering.",
            "Choosing the oldest snapshot, so recovery silently discards recent work.",
            "Never deleting snapshots after a successful save, so recovery offers stale drafts.",
        ],
        q1=(
            "Why order snapshots by a change counter rather than a wall-clock time?",
            "The counter gives a deterministic order that tests can reproduce and that does not depend on clock drift or timezone.",
        ),
        homework=(
            "Write `recover(snapshots, last_saved)` that returns the newest snapshot after the last save or "
            "None, and a `should_snap(change, every)` predicate. Simulate six changes, print the chosen "
            "snapshot, and comment which line ignores work older than the last save."
        ),
        patterns=["def ", "recover(", "print("],
        mapping=(
            "Crash recovery in a desktop editor is a snapshot store plus a startup decision; Tkinter or Qt only "
            "adds the timer and the file directory around this logic."
        ),
    ),
    119: dict(
        topic="Review: forms and validation checklist",
        idea=(
            "A review is a checklist applied to a small app, not a reread of the tutorial. The checklist for "
            "forms and validation is short: fields have types, parsing returns results instead of raising, "
            "errors are keyed by field, required and optional are distinct, invalid submissions cannot reach "
            "the save path, and persistence round-trips. Turn each item into a predicate over a sample state "
            "and print pass or fail with a reason. That turns a vague sense of done into evidence, and it "
            "shows which habit is missing before a user finds it. Keep the checklist in the repository, beside "
            "the tests it will grow into. The example builds one profile form, "
            "applies six checks, and prints a summary line with the pass count. It deliberately includes a "
            "failing check so you see the report handle both outcomes; a checklist that can only pass is "
            "decoration. In a real desktop app these predicates become assertions in a test file, or guard "
            "clauses in the submit handler. They are cheap because the form is data. Finish by choosing one "
            "failed check from your own homework and fixing the code rather than the checklist. That is the "
            "difference between reviewing and rationalising. The phase ends here, but every later screen "
            "reuses these six habits."
        ),
        code=(
            'CHECKS = [\n'
            '    ("fields typed", lambda app: all(f["type"] for f in app["fields"].values())),\n'
            '    ("errors keyed", lambda app: isinstance(app["errors"], dict)),\n'
            '    ("required distinct", lambda app: "email" in app["required"]),\n'
            '    ("submit guarded", lambda app: app["state"] in ("dirty", "valid")),\n'
            '    ("round trip equal", lambda app: app["saved"] == app["draft"]),\n'
            '    ("cancel is None", lambda app: app["chosen"] is None),\n'
            ']\n'
            '\n'
            'app = {\n'
            '    "fields": {"email": {"type": "text"}, "age": {"type": "int"}},\n'
            '    "errors": {},\n'
            '    "required": {"email"},\n'
            '    "state": "dirty",\n'
            '    "draft": {"name": "Ada "},\n'
            '    "saved": {"name": "Ada"},\n'
            '    "chosen": None,\n'
            '}\n'
            '\n'
            'passed = 0\n'
            'for label, check in CHECKS:\n'
            '    ok = check(app)\n'
            '    passed += ok\n'
            '    print(("PASS" if ok else "FAIL"), label)\n'
            'print("passed", passed, "of", len(CHECKS))\n'
            'assert passed == len(CHECKS) - 1\n'
            'print("a checklist turns done into evidence")'
        ),
        variant_b='fix the failing check by trimming the draft before comparison and show six passes',
        variant_c='add a seventh check that a required field has a non-empty value and run it',
        mistakes=[
            "Rewriting the checklist until everything passes instead of fixing the form.",
            "Checking only the happy path, so cancellation and invalid input are untested.",
            "Treating a checklist as paperwork rather than executable evidence about the app.",
        ],
        q1=(
            "What makes a review checklist useful rather than decorative?",
            "Each item is an executable predicate with a reason, so it can fail, expose a missing habit and then guard against a regression.",
        ),
        homework=(
            "Write `audit(app)` that runs six named checks over a form state and returns a list of (label, "
            "passed) pairs, plus a `report(app)` that prints them and the pass count. Include one deliberately "
            "failing state, print the report, and comment which check guards the save path."
        ),
        patterns=["def ", "audit(", "print("],
        mapping=(
            "A desktop app ships with a manual smoke checklist; this executable version is what turns those "
            "clicks into repeatable assertions around the toolkit."
        ),
    ),
})
