"""GUI Applications foundations, days 9-14: desktop UI ideas, headless and runnable.

Every example is stdlib-only, offline and deterministic (fixed data, no display,
no clock), so the applier can execute it and produce the same output on every
run. The domain phases keep the same discipline: a widget tree is a data
structure, layout is arithmetic, and an event is just a value that reaches a
callback — all of which you can model in Python before Tkinter or Qt draws a
single pixel.
"""

FOUNDATION = {
    9: dict(
        topic="Widgets are objects",
        idea=(
            "A GUI is a tree of widgets, and every widget is an object with a parent, a position, a size and a "
            "vocabulary of events it can emit. If you describe that tree as data first — a label, a field, a "
            "button, each pointing at its parent — then layout, theming and testing all become operations over "
            "the tree instead of special cases written by hand. This is the mental model that makes toolkit "
            "documentation readable: `Tkinter` and `Qt` both hand you a parent to call, return a widget object, "
            "and let you read or write its properties. The trap for beginners is treating a widget as a drawn "
            "thing rather than a value. Once a widget is data, you can build a form in a loop over a field "
            "list, restyle every button by walking the tree, and even diff two UI states in a test without a "
            "display. Today you model a three-widget form as plain dictionaries and print the tree. The point "
            "is not to avoid the toolkit but to understand what the toolkit builds for you, so the same "
            "intuition applies whether the project uses Tkinter, PyQt or a web view."
        ),
        code=(
            'def make_widget(kind, parent, **props):\n'
            '    return {"kind": kind, "parent": parent, "props": props}\n'
            '\n'
            'root = make_widget("window", None, title="Login")\n'
            'field = make_widget("entry", "window", name="email")\n'
            'button = make_widget("button", "window", label="Sign in")\n'
            '\n'
            'tree = [root, field, button]\n'
            'for w in tree:\n'
            '    parent = w["parent"] or "<root>"\n'
            '    print(f"{w[\'kind\']:8} parent={parent:8} {w[\'props\']}")\n'
            '\n'
            'children = [w for w in tree if w["parent"] == "window"]\n'
            'assert len(children) == 2\n'
            'print("widgets are data you can walk and filter")'
        ),
        variant_b='add a "checkbox" child and print the children of the window in order',
        variant_c='write `find_by_kind(tree, kind)` and count how many buttons the form contains',
        mistakes=[
            "Thinking of a widget as something drawn rather than an object with properties and events.",
            "Keeping the widget tree only in the toolkit, so no part of the UI can be tested or restyled generically.",
            "Wiring a callback before the widget exists, then wondering why the reference is empty.",
        ],
        q1=(
            "Why is modelling the widget tree as data useful before touching a toolkit?",
            "It lets you build, restyle and test the interface as a structure, with the toolkit only rendering data you already control.",
        ),
        homework=(
            "Write `add_widget(tree, kind, parent, **props)` that appends a new widget dict to a list and "
            "returns it. Add a title label and a password entry under the window, print the whole tree, and "
            "comment which line records the parent relationship."
        ),
        patterns=["def ", "append", "print("],
        mapping=(
            "Tkinter's `Widget` and Qt's `QWidget` both form a parent-child tree; understanding it is what makes "
            "layout, styling and teardown predictable."
        ),
    ),
    10: dict(
        topic="Callbacks and event data",
        idea=(
            "A callback is just a function the toolkit calls later, and the most common GUI bug is a callback "
            "that assumes something about the moment it runs. The mature way to think about it is: an event is a "
            "value (which button, which key, what text) and the callback is a function whose job is to turn that "
            "value plus current state into new state. If the callback reads globals directly, it is untestable "
            "and it will break the day two things can fire in a different order. If it takes the event and the "
            "state as arguments, you can call it by hand in a test with no window at all. That is not a "
            "theoretical nicety in desktop apps; it is how you reproduce the bug where pressing Enter twice "
            "submits a form twice. Today you build a tiny event dispatcher: a mapping from an event name to a "
            "handler function, and a `dispatch` that looks up the handler and passes the event data. You will "
            "see that order matters and that silent missing handlers are a design smell worth guarding against. "
            "Later phases add queues and threading, but the contract stays the same."
        ),
        code=(
            'def on_click(state, event):\n'
            '    return {**state, "clicks": state["clicks"] + 1}\n'
            '\n'
            'def on_text(state, event):\n'
            '    return {**state, "text": event["value"]}\n'
            '\n'
            'handlers = {"click": on_click, "text": on_text}\n'
            '\n'
            'def dispatch(state, name, event):\n'
            '    handler = handlers.get(name)\n'
            '    if handler is None:\n'
            '        print("no handler for", name)\n'
            '        return state\n'
            '    return handler(state, event)\n'
            '\n'
            'state = {"clicks": 0, "text": ""}\n'
            'state = dispatch(state, "click", {})\n'
            'state = dispatch(state, "text", {"value": "ada"})\n'
            'state = dispatch(state, "submit", {})\n'
            'print(state)\n'
            'assert state == {"clicks": 1, "text": "ada"}'
        ),
        variant_b='add a "submit" handler that prints the current text and returns state unchanged',
        variant_c='make dispatch return (state, handled) and assert the unknown event is reported as unhandled',
        mistakes=[
            "Reading and writing global variables inside a callback instead of taking state and event as arguments.",
            "Assuming a handler exists for every event, so an unknown event fails silently.",
            "Connecting the same callback twice, so one click fires the action two times.",
        ],
        q1=(
            "Why pass the event data and state into a callback rather than reading globals?",
            "The callback becomes a pure transformation you can call in a test, and behaviour no longer depends on execution order or hidden context.",
        ),
        homework=(
            "Write `dispatch(state, name, event, handlers)` that looks up a handler by name, prints a warning "
            "for an unknown name, and returns the updated state. Register two handlers, fire three events "
            "including one unknown, print the final state, and comment which line handles the missing case."
        ),
        patterns=["def ", "handlers", "print("],
        mapping=(
            "Tkinter uses `command=` and `bind`, Qt uses signals and slots; both are this dispatcher with more "
            "machinery around delivering the event."
        ),
    ),
    11: dict(
        topic="Layout is arithmetic",
        idea=(
            "Geometry managers feel mysterious until you treat them as arithmetic. Grid layout answers one "
            "question per widget: which row and column, and how much of the leftover space does it take. Once "
            "you compute cell sizes from a fixed total and a set of weights, you can debug any layout by "
            "printing the numbers instead of squinting at a screen. This is exactly what a real toolkit does "
            "internally, and it is why a window that looks right at one size looks broken at another: the "
            "weights were guessed, not computed. The transferable skill is to separate constraints (minimum "
            "sizes, fixed margins) from distribution (expanding weight), resolve them in a defined order, and "
            "round consistently, because rounding is where the last row mysteriously gains a pixel. Today you "
            "write a function that distributes a total width across weighted columns with a gap between them, "
            "and verify the parts plus gaps add back up to the whole. That identity is the test that catches "
            "almost every layout bug. The same reasoning covers padding, alignment and scroll regions, which "
            "are all bookkeeping around this core."
        ),
        code=(
            'def distribute(total, weights, gap=0):\n'
            '    usable = total - gap * (len(weights) - 1)\n'
            '    share = usable // sum(weights)\n'
            '    sizes = [weight * share for weight in weights]\n'
            '    sizes[-1] += usable - sum(sizes)\n'
            '    return sizes\n'
            '\n'
            'widths = distribute(total=100, weights=[1, 2, 1], gap=4)\n'
            'print("column widths:", widths)\n'
            'print("sum:", sum(widths), "expected:", 100 - 4 * 2)\n'
            '\n'
            'assert sum(widths) == 100 - 4 * 2\n'
            'assert widths[1] == 2 * widths[0]  # middle column is twice the first\n'
            'print("parts plus gaps add back to the whole")'
        ),
        variant_b='distribute 120 across weights [3, 1] with a gap of 10 and check the total identity',
        variant_c='add a min_width per column and re-check that the total still fits the window',
        mistakes=[
            "Hard-coding pixel positions instead of computing them from the container size.",
            "Forgetting to subtract the gaps before splitting the space between columns.",
            "Losing the remainder to rounding, so the layout is a few pixels short or over.",
        ],
        q1=(
            "Why is the identity parts-plus-gaps-equals-whole the useful layout test?",
            "It proves the arithmetic conserves space, so no matter the window size the computed cells fill it exactly.",
        ),
        homework=(
            "Write `distribute_rows(total_height, weights, gap)` that returns each row's height and puts any "
            "rounding remainder on the last row. Test it with two weight sets, print the heights and their sum "
            "for each, and comment which line adds back the remainder."
        ),
        patterns=["def ", "sum(", "return"],
        mapping=(
            "Tkinter's grid weights, Qt's stretch factors and Flexbox's flex-grow are all this distribution step "
            "with different names and rounding rules."
        ),
    ),
    12: dict(
        topic="State and the view model",
        idea=(
            "The classic desktop bug is two sources of truth: the model says the email is empty while the entry "
            "widget still shows text, and nobody knows which one is right. The fix is a view model: one "
            "dictionary (or object) that holds the current form values, and widgets that only read from it and "
            "report changes back into it. The view becomes a pure function of state, which means you can test "
            "the form logic without a display, save and restore it, and enable or disable a submit button by "
            "computing a condition rather than chasing it through events. This separation also answers an "
            "everyday question cleanly: when the user edits a field, you do not update the model from the "
            "widget at submit time, you update it on every change so validity, previews and autosave have live "
            "data. Today you build a small form state and two pure functions, one to record a field edit and "
            "one to decide whether the form may be submitted. Nothing here is specific to Python GUIs; it is "
            "the same unidirectional flow that web frameworks popularised, and it is what makes the later "
            "validation and persistence lessons tractable."
        ),
        code=(
            'def edit(state, field, value):\n'
            '    return {**state, field: value}\n'
            '\n'
            'def can_submit(state):\n'
            '    return bool(state["email"].strip()) and state["age"] >= 18\n'
            '\n'
            'form = {"email": "", "age": 0}\n'
            'print("empty form submittable:", can_submit(form))\n'
            'form = edit(form, "email", "ada@example.com")\n'
            'form = edit(form, "age", 21)\n'
            'print("filled form submittable:", can_submit(form))\n'
            '\n'
            'assert can_submit(form)\n'
            'assert not can_submit(edit(form, "email", "  "))\n'
            'print("the widget never owns the truth; the state does")'
        ),
        variant_b='add a "confirm" field and require it to equal the email before submitting',
        variant_c='return a list of validation messages from a function instead of a single boolean',
        mistakes=[
            "Reading field values from widgets at submit time so live validation has stale data.",
            "Storing the same value in both a widget and a separate variable, letting them drift.",
            "Enabling buttons manually from event handlers instead of computing enabled-ness from state.",
        ],
        q1=(
            "What goes wrong when the widget and a separate variable both hold the field value?",
            "They drift out of sync, so validation sees one value while the screen shows another and no single source of truth exists.",
        ),
        homework=(
            "Write `validate(state)` that returns a list of error strings for a form with email and age, and "
            "`is_valid(state)` built on top of it. Test an empty state and a filled one, print both results, "
            "and comment which line makes the button state derived rather than stored."
        ),
        patterns=["def ", "return", "print("],
        mapping=(
            "Qt's model/view classes and MVVM in general formalise this: the view renders state and reports "
            "edits, the model holds the truth."
        ),
    ),
    13: dict(
        topic="Events in a queue",
        idea=(
            "A desktop app is an event loop: the toolkit hands you one event at a time, you handle it, then you "
            "return control so the next event can be delivered. That is why a long computation freezes the "
            "window, and why touching widgets from a worker thread crashes: you broke the single-threaded "
            "contract of the loop. Modelling the loop as an explicit queue makes the rules obvious. Events "
            "enter the queue, the loop pops one, looks up a handler, and updates state; nothing else runs "
            "concurrently with that update. You can drain a queue of scripted events in a test and assert on "
            "the final state, which is impossible if handling is scattered across callbacks that read globals. "
            "The queue also gives you a natural place to coalesce duplicate events, drop events after a "
            "quit, and schedule work to run later. Today you build a bounded event loop over a fixed list of "
            "events and print each step. The lesson to carry into later phases is that responsiveness is about "
            "keeping each turn of the loop short, not about adding threads first."
        ),
        code=(
            'def run_loop(events, state, handlers, limit=100):\n'
            '    steps = 0\n'
            '    queue = list(events)\n'
            '    while queue and steps < limit:\n'
            '        event = queue.pop(0)\n'
            '        handler = handlers.get(event["type"])\n'
            '        if handler:\n'
            '            state = handler(state, event)\n'
            '        print("step", steps, event["type"], "->", state)\n'
            '        steps += 1\n'
            '    return state, steps\n'
            '\n'
            'def inc(state, event):\n'
            '    return {**state, "count": state["count"] + event.get("by", 1)}\n'
            '\n'
            'events = [{"type": "inc"}, {"type": "inc", "by": 2}, {"type": "unknown"}]\n'
            'final, steps = run_loop(events, {"count": 0}, {"inc": inc})\n'
            'assert final["count"] == 3 and steps == 3\n'
            'print("queue drained:", final)'
        ),
        variant_b='make unknown events increment an "errors" counter in state',
        variant_c='add a "quit" event that stops the loop before the remaining events are processed',
        mistakes=[
            "Running a long task inside an event handler, so the window stops responding.",
            "Updating widgets from a worker thread instead of posting an event back to the loop.",
            "Looping without a step limit, so a self-feeding queue never ends.",
        ],
        q1=(
            "Why does a long computation in a handler freeze the interface?",
            "The single event loop cannot pop the next event while the handler runs, so input and redraw wait until it returns.",
        ),
        homework=(
            "Write `drain(events, state, handlers, limit)` that processes a queue with a hard step limit and "
            "returns the final state plus the number of steps taken. Feed it five events with an unknown type, "
            "print each step, and comment which line bounds the loop."
        ),
        patterns=["while ", "def ", "print("],
        mapping=(
            "Tkinter's `mainloop`, `after` and Qt's event loop with `QTimer` all implement this queue; "
            "`postEvent` exists precisely so other threads can send work back safely."
        ),
    ),
    14: dict(
        topic="A tiny app, end to end",
        idea=(
            "Today you connect the pieces into one headless 'application': a state dictionary, a few handlers "
            "registered for events, a queue of scripted events, and a layout computation printed as text rows. "
            "It is small, but it has the skeleton of every desktop app — model, event dispatch, derived view. "
            "Because nothing touches a real display, you can run it in a test, and because it is deterministic, "
            "the same events always produce the same output. Notice where each responsibility lives: handlers "
            "change state, a separate function decides what the screen should show, and the loop only decides "
            "order. That split is what lets you later swap the text renderer for Tkinter labels without "
            "rewriting a single rule. Keep the app's contract honest: an unknown event must not crash the loop, "
            "and the rendered text must be a pure function of state, so a replay after the same events is "
            "identical. This is also the moment to notice that validation is just another derived value. Build "
            "the skeleton here; every later GUI phase is replacing one of these stand-ins with the real toolkit "
            "feature or a more careful implementation."
        ),
        code=(
            'def app():\n'
            '    state = {"items": [], "draft": ""}\n'
            '\n'
            '    def handle(state, event):\n'
            '        if event["type"] == "type":\n'
            '            return {**state, "draft": state["draft"] + event["char"]}\n'
            '        if event["type"] == "enter" and state["draft"]:\n'
            '            return {**state, "items": state["items"] + [state["draft"]], "draft": ""}\n'
            '        return state\n'
            '\n'
            '    events = [\n'
            '        {"type": "type", "char": "m"},\n'
            '        {"type": "type", "char": "ilk"},\n'
            '        {"type": "enter"},\n'
            '        {"type": "type", "char": "eggs"},\n'
            '    ]\n'
            '    for event in events:\n'
            '        state = handle(state, event)\n'
            '    render = lambda s: " | ".join(s["items"] + ["_" + s["draft"]])\n'
            '    return state, render(state)\n'
            '\n'
            'state, screen = app()\n'
            'print("state:", state)\n'
            'print("screen:", screen)\n'
            'assert state["items"] == ["milk"] and state["draft"] == "eggs"\n'
            'print("render is a pure function of state")'
        ),
        variant_b='add a "backspace" event that removes the last character of the draft',
        variant_c='add a "clear" event and check the rendered screen becomes just the cursor',
        mistakes=[
            "Letting an unknown event raise, so one stray message kills the whole loop.",
            "Rendering by mutating state instead of reading it, so redraws change the model.",
            "Duplicating the draft into a widget variable that the renderer also reads.",
        ],
        q1=(
            "Why must render be a pure function of state in this app?",
            "Then the same state always produces the same screen, which makes replay, testing and redraw batching straightforward.",
        ),
        homework=(
            "Write `run(events)` that replays an event list through a state machine and returns the final state "
            "and the rendered string. Add one event type of your choice, run two event lists, print both "
            "results, and comment which line makes the output independent of the toolkit."
        ),
        patterns=["def ", "render", "print("],
        mapping=(
            "This is the same model-dispatch-view pipeline a real desktop app runs; swapping the text renderer "
            "for Tkinter widgets is the only remaining step."
        ),
    ),
}
