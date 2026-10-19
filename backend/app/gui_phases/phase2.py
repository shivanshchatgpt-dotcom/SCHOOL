"""GUI Applications phase 2, days 90-104: events, callbacks and state as data.

Every example is stdlib-only, offline and deterministic. Nothing is drawn and no
window opens: an event is a dictionary or a tiny object, bindings are lists of
handlers, observers are callables, and undo is a pair of lists. The same shapes
appear in Tkinter and Qt once a display is attached.
"""

PHASE = ("Events, Callbacks and State", "Model events, state and undo as plain data so a desktop interface stays testable, deterministic and easy to change.", {
    90: dict(
        topic="Orientation: events drive the app",
        idea=(
            "A GUI program spends most of its life waiting. It does not run from the first line to the last and exit; "
            "it sits in a loop while the operating system hands it messages: a click, a key, a window resize, a timer. "
            "Every message is an event, and every event goes to code you registered earlier, a handler. That inversion "
            "is the biggest shift from scripting. You no longer decide when your code runs; the user does, and your job "
            "is to respond predictably. The healthy model is a tiny machine with three parts. Events go in, a handler "
            "turns the current state plus the event into new state, and the view redraws from that state. Keep those "
            "parts separate and the application stays understandable at 2am. Let handlers mutate widgets directly and "
            "scatter decisions, and every new feature becomes a hunt through callbacks. Today you model the loop without "
            "a toolkit: a list of event dictionaries, one handler that updates a dict, and a printed log of what "
            "happened. Nothing is drawn, yet the control flow is exactly what Tkinter's mainloop or Qt's event loop will "
            "run for you later. Read the log and check that the order matches what a user would experience."
        ),
        code="""def handle(state, event):
    if event["name"] == "click":
        return {**state, "clicks": state["clicks"] + 1}, "click counted"
    if event["name"] == "key":
        return {**state, "text": state["text"] + event["key"]}, "text changed"
    return state, "ignored " + event["name"]

state = {"clicks": 0, "text": ""}
events = [
    {"name": "click"},
    {"name": "key", "key": "a"},
    {"name": "key", "key": "b"},
    {"name": "blur"},
]
for event in events:
    state, note = handle(state, event)
    print(f"{event['name']:6} -> {note:16} state={state}")
assert state == {"clicks": 1, "text": "ab"}
print("the loop turned events into state")
""",
        variant_b="add a `reset` event that clears both counts and print the state after it",
        variant_c="queue the events, drain them in a while loop, and assert that order still gives the same state",
        mistakes=[
            "Thinking the app runs once top to bottom instead of looping while it waits for events.",
            "Letting handlers edit widgets and state directly, so the same fact lives in two places.",
            "Assuming every event name is known, so an unhandled message disappears without a trace.",
        ],
        q1=(
            "What three parts make an event-driven program easy to reason about?",
            "An event going in, a handler that turns old state plus the event into new state, and a view derived from that state.",
        ),
        homework=(
            "Write `run_events(state, events)` that applies a list of event dictionaries, counts clicks, appends "
            "typed characters to text, prints each event's effect, and returns the final state. Fire four events "
            "including one unknown name and assert the count."
        ),
        patterns=["def run_events", "for ", "print("],
        mapping=(
            "Tkinter's `mainloop` and Qt's `QApplication.exec` are the waiting loop; every `command=` or "
            "`clicked.connect` you write is a handler in that loop."
        ),
    ),
    91: dict(
        topic="Event objects and payloads",
        idea=(
            "An event is not just a name. When a user presses a key, the toolkit knows which key, whether Shift was "
            "held, and which field had focus. When a mouse moves, it knows coordinates and buttons. Putting those facts "
            "in a payload next to the name keeps handlers from guessing, and it makes the same handler reusable across "
            "widgets. The alternative, a handler that reads the focused widget from somewhere global or parses a "
            "string, couples every callback to one concrete screen. A small Event object with a name and a payload "
            "dictionary is enough for most desktop work. Give it safe access with a `get` method and a useful `repr`, "
            "and debugging becomes reading one line. The important discipline is that the payload is data, not "
            "behaviour: coordinates, text, modifiers, identifiers. Handlers decide what the data means. This separation "
            "pays off in tests, because you can construct the exact event that broke production without synthesising a "
            "real keyboard. Today you define an event class, emit three events with different payloads, and print the "
            "resulting state and the last event. Notice that the click event is ignored by the key handler because the "
            "handler checks the name first. That check is a contract, and contracts are what keep event-driven code from "
            "turning into a pile of coincidences."
        ),
        code="""class Event:
    def __init__(self, name, **payload):
        self.name = name
        self.payload = payload

    def get(self, key, default=None):
        return self.payload.get(key, default)

    def __repr__(self):
        return f"Event({self.name!r}, {self.payload})"


def on_key(state, event):
    if event.name != "key":
        return state
    return {**state, "text": state["text"] + event.get("char", "")}


events = [Event("key", char="h"), Event("key", char="i"), Event("click", x=3, y=4)]
state = {"text": ""}
for event in events:
    state = on_key(state, event)
print(state)
print(events[-1])
assert state["text"] == "hi"
print("payloads travel with the event")
""",
        variant_b="add a `mods` payload to the key events and print it alongside the resulting text",
        variant_c="make the handler reject events with an empty `char` and prove the click payload stays untouched",
        mistakes=[
            "Reading focus or widget text from globals instead of taking the facts from the event payload.",
            "Putting behaviour in the event object so payloads cannot be built and compared in a test.",
            "Forgetting that a handler for one event name can still receive every other event too.",
        ],
        q1=(
            "Why should event payloads carry data rather than behaviour?",
            "Data can be constructed, printed and asserted in tests, while handlers keep the single job of interpreting it.",
        ),
        homework=(
            "Write `Event` with `name` and `payload`, then `handle_key(state, event)` that appends "
            "`event.get(\"char\", \"\")` to `state[\"text\"]`. Emit three events, print state and the last event, "
            "and assert the text."
        ),
        patterns=["class Event", "def handle_key", "print("],
        mapping=(
            "Tkinter passes an `event` object to a bound callback; Qt passes a typed event to `event()` or a signal "
            "argument. Both carry a payload you should read, not guess."
        ),
    ),
    92: dict(
        topic="Binding and unbinding handlers",
        idea=(
            "Binding connects an event name to a handler; unbinding disconnects it. The subtle part is identity. If you "
            "bind a lambda and later try to remove it by writing the same lambda again, you have created a different "
            "function object, so nothing is removed. Real toolkits solve this by returning a token or by requiring the "
            "original callable. Model the token approach: `bind` returns an identifier, `unbind` removes exactly that "
            "identifier, and emitting calls the handlers that remain in order. Binding twice is legal and means the "
            "action runs twice. That is occasionally what you want, but far more often it is a leak: a dialog opens, "
            "subscribes, closes without unsubscribing, and the next open has two listeners. In a long-lived app those "
            "leaks accumulate quietly until one click triggers five requests. The discipline is symmetrical: every "
            "bind has an owner, and that owner has a matching unbind on teardown. Today you build a tiny bus with a "
            "handler list per event, bind two listeners to save, unbind one, and print the log. The order matters, and "
            "the assertion shows that only the surviving listener runs. This is the same shape as `widget.bind` and "
            "`signal.disconnect`, reduced to data you can inspect."
        ),
        code="""class Bus:
    def __init__(self):
        self.handlers = {}
        self.next_id = 1

    def bind(self, name, handler):
        token = self.next_id
        self.next_id += 1
        self.handlers.setdefault(name, []).append((token, handler))
        return token

    def unbind(self, name, token):
        self.handlers[name] = [
            (t, h) for t, h in self.handlers.get(name, []) if t != token
        ]

    def emit(self, name, *args):
        for _token, handler in list(self.handlers.get(name, [])):
            handler(*args)


log = []
bus = Bus()
a = bus.bind("save", lambda where: log.append("audit:" + where))
b = bus.bind("save", lambda where: log.append("ui:" + where))
bus.emit("save", "draft")
bus.unbind("save", a)
bus.emit("save", "final")
print(log)
assert log == ["audit:draft", "ui:draft", "ui:final"]
print("unbinding removes only the returned token")
""",
        variant_b="bind the same handler twice, emit once, then unbind one token and show the second still runs",
        variant_c="make unbind return the removed handler count and assert a stale token removes nothing",
        mistakes=[
            "Unbinding a freshly written lambda instead of the original function or the token returned by bind.",
            "Subscribing in a dialog and never unsubscribing, so each open adds another listener.",
            "Mutating the handler list during emit, which skips the next handler in the iteration.",
        ],
        q1=(
            "Why does bind return a token in this model?",
            "So unbind can remove one exact registration, which a rewritten lambda or duplicate handler cannot identify.",
        ),
        homework=(
            "Write `Bus` with `bind(name, handler)` returning a token, `unbind(name, token)`, and "
            "`emit(name, value)`. Bind two handlers, emit, unbind the first, emit again, print the log and assert "
            "the surviving order."
        ),
        patterns=["def bind", "def unbind", "print("],
        mapping=(
            "Tkinter's `bind` and `unbind` take a sequence id or callable; Qt's `signal.connect` pairs with "
            "`disconnect`. Leaked connections are the same bug in both."
        ),
    ),
    93: dict(
        topic="The callback queue",
        idea=(
            "Events do not always run the instant they arrive. A toolkit queues them so that one handler cannot "
            "recursively re-enter the whole application, and so that painting and input stay in a sane order. The queue "
            "is first in, first out: the click that happened first is handled first even if a later event is more "
            "urgent to the user. That ordering is a feature, not an accident, and bugs appear when code assumes "
            "otherwise. A queue also gives you a natural boundary for testing: push a list of events, drain it, inspect "
            "the state. If handlers only transform state and never call each other directly, the drain is "
            "deterministic. Beware of handlers that enqueue more events. That is legal and often useful, but it can loop "
            "forever if an event reproduces itself. A simple guard, such as a maximum number of turns, turns a hang into "
            "a visible error. Today you use `collections.deque` as the queue, push four events, and drain them in order "
            "while recording what was processed. The reset in the middle proves that order changes the answer: the same "
            "events in another order would give a different total. Keep that property in mind whenever you replay a "
            "session or debug a race that is really just ordering."
        ),
        code="""from collections import deque


def handle(state, event):
    if event[0] == "add":
        return {**state, "total": state["total"] + event[1]}
    if event[0] == "reset":
        return {**state, "total": 0}
    return state


queue = deque()
for event in [("add", 3), ("add", 4), ("reset",), ("add", 5)]:
    queue.append(event)

state = {"total": 0}
processed = []
while queue:
    event = queue.popleft()
    state = handle(state, event)
    processed.append(event[0])
print("processed:", processed)
print("state:", state)
assert state == {"total": 5}
print("FIFO means the last event wins on state")
""",
        variant_b="enqueue two more add events from inside the drain and show the queue handles them in turn",
        variant_c="reverse the input order before draining and assert the total changes, proving order matters",
        mistakes=[
            "Processing the newest event first and expecting the same result as arrival order.",
            "Letting one handler call another handler directly, which bypasses the queue and its ordering.",
            "Enqueuing an event that enqueues itself with no turn limit, turning a bug into a hang.",
        ],
        q1=(
            "Why does a FIFO queue make event handling easier to test?",
            "A known input order drains to a known state, so the same log always produces the same result without timing.",
        ),
        homework=(
            "Write `drain(events, state, handle)` that uses `collections.deque`, applies `handle` to each event in "
            "FIFO order, prints the sequence, and returns the final state. Include a reset event in the middle and "
            "assert the total."
        ),
        patterns=["deque", "popleft", "print("],
        mapping=(
            "Tkinter's event queue and Qt's posted events both preserve arrival order; `after` or `postEvent` adds "
            "work without re-entering the current handler."
        ),
    ),
    94: dict(
        topic="Commands as small objects",
        idea=(
            "A command is a small object that packages one user intention: add ten, delete a row, rename a document. "
            "Compared with a bare callback, a command carries its arguments and can implement both `execute` and "
            "`undo`. That pairing is why command objects are the backbone of undo, macros, and scripted UI tests. The "
            "handler becomes boring: take the command, run it, append it to history. The command owns the details. "
            "There is a real trade-off. A command class for every tiny action is ceremony, so use plain functions until "
            "you need reversal, logging, or replay. The moment two of those appear, the object earns its keep. Keep "
            "commands free of widget references; they should operate on state or on a small domain API. If a command "
            "holds a label widget and sets its text directly, undo has to remember widget internals and the command "
            "cannot run headless. Today you define an `AddCommand` with `execute` and `undo`, run three of them, then "
            "undo in reverse order and assert the total returns to zero. Reverse order is not a stylistic choice; it is "
            "what makes nested or dependent changes unwind correctly. Notice how little the loop knows about the "
            "arithmetic. It only knows the command protocol, which is exactly the seam you will want when the actions "
            "become real."
        ),
        code="""class AddCommand:
    def __init__(self, amount):
        self.amount = amount

    def execute(self, state):
        return {**state, "total": state["total"] + self.amount}

    def undo(self, state):
        return {**state, "total": state["total"] - self.amount}


commands = [AddCommand(10), AddCommand(-3), AddCommand(7)]
state = {"total": 0}
for command in commands:
    state = command.execute(state)
    print("run", command.amount, "->", state["total"])
for command in reversed(commands):
    state = command.undo(state)
print("after undo all:", state)
assert state == {"total": 0}
print("commands know how to reverse themselves")
""",
        variant_b="add a `RenameCommand` that changes a `name` field and undo the mixed command list in reverse",
        variant_c="give the command a `label` string and print the history in the order it was executed",
        mistakes=[
            "Putting the arithmetic in the event handler so undo cannot know what to reverse.",
            "Holding a widget inside the command, which makes the command impossible to run in a test.",
            "Undoing in execution order, which corrupts dependent changes instead of unwinding them.",
        ],
        q1=(
            "When does a command object earn its keep over a plain callback?",
            "When the action needs its arguments, reversal, logging or replay, because the object can carry all of them together.",
        ),
        homework=(
            "Write `AddCommand` with `execute(state)` and `undo(state)` plus a `run(commands)` helper that runs them "
            "forward, prints totals, then unwinds in reverse. Assert the state returns to zero."
        ),
        patterns=["def execute", "def undo", "print("],
        mapping=(
            "Qt's `QUndoCommand` is exactly this protocol; Tkinter apps usually grow a command list once undo "
            "appears. The execute and undo pair is the reusable seam."
        ),
    ),
    95: dict(
        topic="State as the source of truth",
        idea=(
            "The most valuable decision in an event-driven app is to make state the source of truth. Handlers do not "
            "reach into widgets and edit text; they produce a new state value, and the view renders that value. One "
            "dict or dataclass holds what the user has done and what is pending, and every event is a pure function "
            "from old state to new state. This is the reducer pattern, and it is not only a web idea. Desktop apps that "
            "follow it are dramatically easier to test and to debug because the entire application can be "
            "reconstructed from an event log. The hard part is honesty. It is tempting to keep a little state in the "
            "widget, a little in a closure, and a little in the model, and then spend a week reconciling three truths. "
            "Pick one home for each fact. Derived values, like an error message or a character count, should not be "
            "stored at all; compute them from the state when rendering. Today you write a `reduce` function that "
            "handles typing, clearing and submitting, then feed it four actions and print the result. Nothing in the "
            "loop knows what a text box is. The assertion checks that submission moved the draft into a saved list, "
            "which is the kind of behaviour a widget cannot verify for you. That is the payoff: the logic is ordinary "
            "Python."
        ),
        code="""def reduce(state, action):
    kind = action["type"]
    if kind == "type":
        return {**state, "draft": state["draft"] + action["char"]}
    if kind == "clear":
        return {**state, "draft": ""}
    if kind == "submit":
        return {
            **state,
            "saved": state["saved"] + [state["draft"]],
            "draft": "",
        }
    return state


state = {"draft": "", "saved": []}
for action in [
    {"type": "type", "char": "h"},
    {"type": "type", "char": "i"},
    {"type": "submit"},
    {"type": "type", "char": "x"},
]:
    state = reduce(state, action)
print(state)
assert state["saved"] == ["hi"]
print("state is the only thing the view needs")
""",
        variant_b="add a `backspace` action that drops the last draft character and replay the same sequence",
        variant_c="return `(state, changed)` from reduce and assert that an unknown action reports no change",
        mistakes=[
            "Storing a character count and an error message as separate state that can drift from the draft.",
            "Letting the handler update both the model and the widget, creating two competing truths.",
            "Making reduce depend on a global or the clock, so the same action can produce different states.",
        ],
        q1=(
            "Why should derived values be computed instead of stored in state?",
            "A computed value cannot go stale or disagree with its source, which removes a whole class of update bugs.",
        ),
        homework=(
            "Write `reduce(state, action)` handling `type`, `clear` and `submit`, where submit appends the draft to "
            "`saved` and clears it. Feed five actions, print state, and assert the saved list and empty draft."
        ),
        patterns=["def reduce", "return {**state", "print("],
        mapping=(
            "Tkinter `StringVar` and Qt models can hold state, but a plain reducer keeps the rules testable and "
            "the widgets replaceable."
        ),
    ),
    96: dict(
        topic="The view model",
        idea=(
            "A view model is the layer between raw state and the widgets. Raw state says `draft` is two spaces; the "
            "view model says the preview is empty, the counter reads 2/20, and the save button is disabled. Widgets "
            "should not perform that reasoning, because then every widget duplicates it and the rules drift. The view "
            "model is computed fresh from state, never stored and never mutated. That single rule removes a whole "
            "family of bugs where a label shows stale text because someone forgot to update it after a branch. In "
            "Tkinter you might build a dictionary of strings and booleans, then assign them to variables; in Qt you "
            "might expose properties or use a model class. The shape is the same. Keep formatting in one place, and "
            "keep it total: every state, including empty and invalid ones, must produce a rendering rather than an "
            "exception. Today you write `render(state)` returning a heading, a preview, a counter and a boolean, then "
            "render two states. The second state enables saving, the first does not. Because `render` is pure, "
            "printing it twice gives identical output, which is exactly what a snapshot test wants. Later, when the "
            "design changes, you edit one function instead of hunting every label assignment in the file."
        ),
        code="""def render(state):
    draft = state["draft"]
    return {
        "heading": state["title"],
        "preview": draft.strip() or "(empty)",
        "counter": f"{len(draft)}/20",
        "save_enabled": bool(draft.strip()) and len(draft) <= 20,
    }


state = {"title": "Note", "draft": "  "}
print(render(state))
state = {**state, "draft": "milk"}
print(render(state))
assert render(state)["save_enabled"] is True
assert render(state)["preview"] == "milk"
print("the view model is computed, never stored")
""",
        variant_b="add a `too_long` boolean for drafts over twenty characters and render a 25-character draft",
        variant_c="give each rendered field a display string instead of a raw boolean and assert the disabled label",
        mistakes=[
            "Storing the preview text beside the draft and updating it only on some code paths.",
            "Letting `render` mutate state or read the clock, which makes snapshots and repeated calls unstable.",
            "Crashing on an empty draft instead of rendering a safe placeholder for every valid state.",
        ],
        q1=(
            "What makes a view model safe to snapshot-test?",
            "It is pure and total: the same state always gives the same output, and even empty states render instead of raising.",
        ),
        homework=(
            "Write `render(state)` returning `preview`, `counter` and `save_enabled`, and `render_all(states)` that "
            "prints one line per state. Assert that whitespace-only drafts disable saving."
        ),
        patterns=["def render", "save_enabled", "print("],
        mapping=(
            "Tkinter variables and Qt model roles both hand widgets ready-to-display values; the view model is "
            "where that formatting rule lives."
        ),
    ),
    97: dict(
        topic="Observers and change notification",
        idea=(
            "Observers let interested code react to state changes without the store knowing who is listening. The store "
            "keeps a list of callables, updates state, and calls each one with the new value. This is the "
            "publish-subscribe seam behind Qt signals, Tkinter variable traces, and most desktop event buses. Two "
            "details separate a toy from something usable. First, notify only when the state actually changed; a store "
            "that fires on every `set` call wakes the UI for nothing and can create feedback loops. Second, iterate "
            "over a copy of the observer list, because an observer may subscribe or unsubscribe during notification, "
            "and mutating a list you are iterating is a classic source of skipped callbacks. You should also decide "
            "whether observers receive the whole state or a diff. Whole state is simpler and fast enough for small "
            "apps. Today you build a `Store` with `subscribe` and `set`, attach one observer that records every state "
            "it sees, and perform three updates, one of which changes nothing. The observer runs twice, and the "
            "printed last value proves it saw the real change. The assertion is the contract: no event, no "
            "notification. When you move to a toolkit, that same contract prevents redraw storms."
        ),
        code="""class Store:
    def __init__(self, state):
        self.state = state
        self.observers = []

    def subscribe(self, observer):
        self.observers.append(observer)
        return observer

    def set(self, **changes):
        new_state = {**self.state, **changes}
        if new_state == self.state:
            return False
        self.state = new_state
        for observer in list(self.observers):
            observer(self.state)
        return True


seen = []
store = Store({"count": 0, "label": "zero"})
store.subscribe(lambda state: seen.append(dict(state)))
store.set(count=1)
store.set(count=1)
store.set(label="one")
print("notifications:", len(seen))
print("last:", seen[-1])
assert len(seen) == 2
print("observers run once per real change")
""",
        variant_b="add a second observer that prints only the count and show both fire on a real change",
        variant_c="let an observer unsubscribe itself during notification and assert the copied list still completes",
        mistakes=[
            "Notifying on every set call, including writes that leave the state unchanged, causing redraw loops.",
            "Iterating the live observer list while callbacks add or remove observers, skipping some of them.",
            "Forgetting to unsubscribe a destroyed widget, so its handler keeps receiving state forever.",
        ],
        q1=(
            "Why notify observers only when the new state differs from the old one?",
            "Unchanged writes would trigger pointless redraws and can start feedback loops between store and view.",
        ),
        homework=(
            "Write `Store` with `subscribe`, `set` and a notification count. Update the same value twice, then a "
            "different value, print the notifications and the last state, and assert the count is two."
        ),
        patterns=["def subscribe", "def set", "print("],
        mapping=(
            "Qt signals, Tkinter variable traces and `<<Modified>>` bindings are observers; notifying only on change "
            "is what prevents redraw loops."
        ),
    ),
    98: dict(
        topic="Debouncing rapid events",
        idea=(
            "Some events arrive far faster than the app should react. Typing in a search box can produce a keystroke "
            "every few milliseconds, and running a filter, a query or a redraw for each one wastes work and makes the "
            "interface feel worse. Debouncing collapses a burst into one action after the burst settles. Throttling is "
            "the cousin: act at most once per interval while the burst continues. Both need a notion of time, but for a "
            "deterministic model you can use a logical tick instead of the wall clock. That substitution is not "
            "cheating; it is what makes the behaviour testable. A debouncer stores the latest value and the tick when "
            "it arrived. When a new tick is at least `delay` beyond that arrival, the pending value is released. A "
            "flush at the end handles the final value that would otherwise wait forever. The subtle bug is releasing "
            "before accepting the next event: order matters, or you either lose the settled value or act on it twice. "
            "Today you feed five keystrokes at ticks 0, 1, 2, 5 and 6 with a delay of 3, print both the raw input and "
            "the released searches, and assert that only `abc` and `abcde` are acted on. The test runs in microseconds "
            "and does not depend on machine speed."
        ),
        code="""class Debouncer:
    def __init__(self, delay):
        self.delay = delay
        self.pending = []
        self.last_tick = None

    def flush(self, tick, force=False):
        if not self.pending:
            return []
        if force or tick - self.last_tick >= self.delay:
            value = self.pending[-1]
            self.pending = []
            return [value]
        return []

    def offer(self, tick, value):
        ready = self.flush(tick)
        self.pending = [value]
        self.last_tick = tick
        return ready


debouncer = Debouncer(delay=3)
events = [(0, "a"), (1, "ab"), (2, "abc"), (5, "abcd"), (6, "abcde")]
out = []
for tick, value in events:
    out.extend(debouncer.offer(tick, value))
    out.extend(debouncer.flush(tick))
out.extend(debouncer.flush(9, force=True))
print("keystrokes:", [value for _tick, value in events])
print("searches:", out)
assert out == ["abc", "abcde"]
print("only the settled value is acted on")
""",
        variant_b="change the delay to 2 and predict which values are released before rerunning",
        variant_c="treat each field as a separate key and prove a burst in one field does not discard the other",
        mistakes=[
            "Using wall-clock sleeps in the test, which makes it slow and flaky on a loaded machine.",
            "Releasing the pending value after replacing it, so the settled input is lost.",
            "Debouncing the state update instead of the expensive action, leaving the UI behind the keyboard.",
        ],
        q1=(
            "Why model debounce timing with logical ticks instead of the wall clock?",
            "Ticks make the behaviour deterministic and instant to test, while still exercising the same settle rule.",
        ),
        homework=(
            "Write `Debouncer(delay)` with `offer(tick, value)` and `flush(tick, force=False)`. Replay ticks 0, 1, "
            "2, 5, 6 plus a final force flush, print released values, and assert only settled values appear."
        ),
        patterns=["def offer", "def flush", "print("],
        mapping=(
            "Text widgets fire on every keystroke; debouncing with `after` or a `QTimer` is the standard way to "
            "avoid a query or validation per character."
        ),
    ),
    99: dict(
        topic="Keyboard and mouse events",
        idea=(
            "Keyboard and mouse events look simple until modifiers, focus and coordinates enter the picture. A key "
            "press is not just a character; it is a physical key plus a modifier set, and the same shortcut may be "
            "reported differently across platforms. Mouse events add button, position and sometimes click count. The "
            "robust pattern is to normalise early. Convert raw toolkit events into a small, stable action vocabulary "
            "such as `ctrl+s`, `enter`, or `click:10,4`, then let the rest of the app match on that vocabulary. "
            "Handlers become readable, and tests can construct actions without simulating hardware. Normalisation is "
            "also where you decide precedence: Ctrl plus a letter should beat the plain letter, and a right click "
            "should not be mistaken for a left click. Case folding belongs here too, because users do not think about "
            "whether Shift produced an uppercase character. Today you write `normalize(event)` over four raw "
            "dictionaries and print the resulting list. The first event becomes `ctrl+s`, the second a plain `a`, the "
            "third a click with coordinates, and the right click is ignored. Notice that no handler had to know about "
            "dictionaries or modifier flags. That boundary is the point: raw input is messy and platform-specific, "
            "while actions are yours to define and test."
        ),
        code="""def normalize(event):
    if event["kind"] == "key":
        key = event["key"].lower()
        if event.get("ctrl"):
            return "ctrl+" + key
        return key
    if event["kind"] == "mouse" and event.get("button") == "left":
        return "click:" + str(event["x"]) + "," + str(event["y"])
    return "ignore"


raw = [
    {"kind": "key", "key": "S", "ctrl": True},
    {"kind": "key", "key": "a"},
    {"kind": "mouse", "button": "left", "x": 10, "y": 4},
    {"kind": "mouse", "button": "right", "x": 1, "y": 1},
]
actions = [normalize(event) for event in raw]
print(actions)
assert actions[0] == "ctrl+s"
assert actions[3] == "ignore"
print("modifiers belong in the action, not the handler")
""",
        variant_b="add `shift` handling so a held Shift produces `shift+tab` and print the normalised actions",
        variant_c="include double clicks by checking a `count` field and assert a single right click is ignored",
        mistakes=[
            "Letting every handler inspect raw modifier flags instead of normalising once at the boundary.",
            "Forgetting to fold key case, so Ctrl+S and Ctrl+s reach different branches.",
            "Treating any mouse button as a left click, which fires destructive actions on right click.",
        ],
        q1=(
            "Why normalise raw input events into a small action vocabulary?",
            "Handlers become readable and testable, and platform-specific details stop leaking through the whole app.",
        ),
        homework=(
            "Write `normalize(event)` mapping key and mouse dictionaries to strings like `ctrl+s` and `click:10,4`. "
            "Normalise four events, print the list, assert modifier precedence and that right clicks are ignored."
        ),
        patterns=["def normalize", "ctrl+", "print("],
        mapping=(
            "Tkinter gives `<Control-s>` style bindings with `event.state`; Qt uses `QKeySequence` and "
            "`QMouseEvent`. Normalising early keeps handlers portable."
        ),
    ),
    100: dict(
        topic="Focus and tab order",
        idea=(
            "Focus decides which widget receives a key press, and tab order decides how focus moves. Users who never "
            "touch a mouse depend on both, so this is an accessibility requirement, not a polish item. The good news "
            "is that tab order can be data: a list of widget identifiers in the order they should be visited. Moving "
            "forward increments an index modulo the length; moving backward decrements it, and Python's modulo "
            "handles the wrap into negative numbers correctly. Disabled or hidden widgets complicate the simple list, "
            "which is why real toolkits expose a `takefocus` flag or a tab chain. You can model that by filtering the "
            "order before moving, but keep the rule in one function rather than scattering index arithmetic through "
            "event handlers. Focus also has an owner: the application should know which widget has it, and losing "
            "focus is an event worth handling when a field validates or commits on blur. Today you take four widgets "
            "in a ring, move forward three times from the first, then move backward once, and print the whole path. The "
            "assertion shows the wrap and the reverse step. Because the path is computed from plain data, you can test "
            "keyboard navigation without a display, which is exactly what a CI machine gives you."
        ),
        code="""order = ["name", "email", "password", "submit"]
focus = "name"


def move(current, reverse=False):
    step = -1 if reverse else 1
    index = (order.index(current) + step) % len(order)
    return order[index]


path = [focus]
for _ in range(3):
    focus = move(focus)
    path.append(focus)
focus = move(focus, reverse=True)
path.append(focus)
print("tab path:", " -> ".join(path))
assert path == ["name", "email", "password", "submit", "password"]
print("focus order is data, so it can be tested")
""",
        variant_b="skip a disabled widget by filtering it out of the order and show the path changes",
        variant_c="start at `submit`, tab forward once, and assert the wrap lands on `name`",
        mistakes=[
            "Computing the next index with plain subtraction, which wraps to the wrong end on a negative value.",
            "Scattering focus arithmetic through key handlers instead of keeping one move function.",
            "Leaving disabled widgets in the tab order, so keyboard users land on controls that do nothing.",
        ],
        q1=(
            "Why is focus order better represented as a list than as hard-coded branches per key press?",
            "One ordered list makes forward, reverse and wrap rules testable in one place and keeps accessibility visible.",
        ),
        homework=(
            "Write `move_focus(order, current, reverse=False)` and `focus_path(order, start, steps)`. Walk a "
            "four-widget ring forward and backward, print the path and assert the wraparound."
        ),
        patterns=["def move_focus", "def focus_path", "print("],
        mapping=(
            "Tkinter's `tk_focusNext` and Qt's tab chain both follow an order you can inspect; accessibility audits "
            "check that this order matches the visual one."
        ),
    ),
    101: dict(
        topic="Validating on input",
        idea=(
            "Validating on input means checking a field as the user types rather than waiting for submit. Used well, "
            "it shortens the feedback loop; used badly, it scolds people while they are still halfway through a word. "
            "The model should separate validity from presentation. A pure function takes the current fields and returns "
            "a dictionary of errors, and the view decides when to show them: after the first blur, after a failed "
            "submit, or once the field has enough characters. Keep the rules small and explicit. An email check in a "
            "teaching example can require exactly one `@` and a non-empty tail, while a password rule can require a "
            "minimum length; neither pretends to be a complete specification. The important property is that the same "
            "function runs on every keystroke and on submit, so the button state and the final check cannot disagree. "
            "Today you validate three snapshots of an email and password, print the errors, and assert that the last "
            "snapshot is clean. The middle snapshot fails both rules, which is more useful than a single happy path "
            "because it proves the error map can hold two entries. In a real app, map each key to the widget that "
            "displays it, and never disable the submit button without also explaining why it is disabled."
        ),
        code="""def validate(fields):
    errors = {}
    if fields["email"].count("@") != 1:
        errors["email"] = "need one @"
    if len(fields["password"]) < 6:
        errors["password"] = "too short"
    return errors


snapshots = [
    {"email": "a", "password": ""},
    {"email": "ab", "password": "abc"},
    {"email": "a@b", "password": "abcdef"},
]
for fields in snapshots:
    errors = validate(fields)
    state = "ok" if not errors else "; ".join(sorted(errors.values()))
    print(fields["email"], "->", state)
assert validate(snapshots[-1]) == {}
assert len(validate(snapshots[1])) == 2
print("validation runs on every keystroke")
""",
        variant_b="add a rule requiring the local part before the @ and recheck the middle snapshot",
        variant_c="treat an empty password as untouched and only report it after a submit flag is set",
        mistakes=[
            "Disabling submit without showing which field is wrong, leaving the user stuck with no explanation.",
            "Writing different rules in the key handler and the submit handler so the two disagree.",
            "Showing every error from the first keystroke, which punishes typing that is still in progress.",
        ],
        q1=(
            "Why should the same validation function serve both typing and submit?",
            "One rule set means the disabled button and the final check can never disagree about what is valid.",
        ),
        homework=(
            "Write `validate(fields)` returning an error dict for email and password, and `validate_all(snapshots)` "
            "printing one line per snapshot. Assert the clean snapshot has no errors and the broken one has two."
        ),
        patterns=["def validate", "errors", "print("],
        mapping=(
            "Tkinter `validatecommand` and Qt validators run per edit; a pure `validate(fields)` keeps the same rule "
            "in front of the button and the submit path."
        ),
    ),
    102: dict(
        topic="Undo and redo",
        idea=(
            "Undo and redo are stacks, but the details decide whether they feel right. Before a change, push the "
            "previous value onto the undo stack. To undo, push the current value onto the redo stack and pop the undo "
            "stack back into place. To redo, reverse that operation. The easy-to-miss rule is that any new edit clears "
            "the redo stack: once you branch, the old future is gone. Getting this wrong produces the eerie bug where "
            "redo restores text from a document state the user abandoned. Storing whole snapshots is perfectly "
            "acceptable for small documents and is much simpler than inverse operations; memory is cheap, and "
            "correctness is not. For large documents, store commands or diffs instead, but keep the same stack "
            "protocol. Coalescing adjacent keystrokes is a later refinement, and it should be an explicit rule, not an "
            "accident of timing. Today you build an `Editor` with a text string and two stacks, type three chunks, undo "
            "twice, redo once, and print the text after each phase. The assertion checks the final string, and the "
            "class shows how little code the protocol needs. Notice that `type` is the only method that clears redo, "
            "which mirrors the rule that only new user intent destroys history. Test the branch case explicitly when "
            "you adapt this."
        ),
        code="""class Editor:
    def __init__(self):
        self.text = ""
        self.undo_stack = []
        self.redo_stack = []

    def type(self, chunk):
        self.undo_stack.append(self.text)
        self.text += chunk
        self.redo_stack.clear()

    def undo(self):
        if self.undo_stack:
            self.redo_stack.append(self.text)
            self.text = self.undo_stack.pop()

    def redo(self):
        if self.redo_stack:
            self.undo_stack.append(self.text)
            self.text = self.redo_stack.pop()


editor = Editor()
for chunk in ["ab", "cd", "ef"]:
    editor.type(chunk)
editor.undo()
editor.undo()
print("after undo:", editor.text)
editor.redo()
print("after redo:", editor.text)
editor.type("!")
print("after branch:", editor.text)
assert editor.text == "abcd!"
assert editor.redo_stack == []
print("new typing clears the redo future")
""",
        variant_b="add `delete_last()` that removes one character and show undo restores it",
        variant_c="print both stack depths after each operation to see how snapshots move between them",
        mistakes=[
            "Forgetting to clear redo on a new edit, so redo restores a future the user abandoned.",
            "Pushing the new text before a change, which makes undo skip one state.",
            "Undoing by guessing the inverse operation instead of restoring the saved previous value.",
        ],
        q1=(
            "Why does a new edit clear the redo stack?",
            "The user has branched from the old history, so the previously undone future no longer belongs to this document.",
        ),
        homework=(
            "Write `Editor` with `type`, `undo` and `redo` using two lists. Type three chunks, undo twice, redo once, "
            "print after each step, and assert that a new edit clears redo."
        ),
        patterns=["def type", "def undo", "print("],
        mapping=(
            "Qt's undo framework and Tkinter's text widget both use paired stacks; the rule that new input clears "
            "redo is universal."
        ),
    ),
    103: dict(
        topic="Replaying events in tests",
        idea=(
            "A reproducible bug is a gift, and event replay is how you turn a user report into one. Record the events, "
            "in order, with their payloads. Then run the same pure reducer over the log in a test and compare the final "
            "state with what the user saw. No window, no timing, no flaky sleep. This only works if the handlers are "
            "deterministic and side effects are separated. If a handler reads the clock, a random value, or a network "
            "response, the replay diverges; the fix is to capture those inputs as events too, or to inject them. "
            "Replay also gives you a cheap regression suite: every fixed bug leaves behind its event log, and the suite "
            "grows with real usage instead of invented scenarios. A replay test should assert something stronger than "
            "`it did not crash`. Compare the full final state, and when practical compare intermediate states at "
            "chosen checkpoints. You can also replay the log against two implementations to prove a refactor is "
            "behaviour-preserving. Today you write a small reducer for typing, backspace and clear, replay the same "
            "four-event log into two fresh states, print both, and assert they match the expected text. The two runs "
            "are deliberately independent, so a hidden global would show up immediately. That is the discipline: if "
            "the state is real, the log is enough to rebuild it."
        ),
        code="""def reduce(state, event):
    if event["type"] == "type":
        return {**state, "text": state["text"] + event["char"]}
    if event["type"] == "backspace":
        return {**state, "text": state["text"][:-1]}
    if event["type"] == "clear":
        return {**state, "text": ""}
    return state


log = [
    {"type": "type", "char": "h"},
    {"type": "type", "char": "i"},
    {"type": "backspace"},
    {"type": "type", "char": "!"},
]
first = {"text": ""}
second = {"text": ""}
for event in log:
    first = reduce(first, event)
for event in log:
    second = reduce(second, event)
print("first:", first)
print("second:", second)
assert first == second == {"text": "h!"}
print("event logs replay to the same state")
""",
        variant_b="insert a `clear` event in the middle of the log and assert both fresh runs still agree",
        variant_c="record the state after every event and compare the two checkpoint lists instead of only the end",
        mistakes=[
            "Replaying events but comparing only that the app did not crash, which misses wrong final state.",
            "Leaving a clock or random call inside the reducer, so two replays of the same log diverge.",
            "Sharing the initial state dict between runs, which hides mutation bugs and makes replay meaningless.",
        ],
        q1=(
            "What must be true of handlers for an event log to replay deterministically?",
            "They must be pure or have their external inputs captured as events, so the same log always produces the same state.",
        ),
        homework=(
            "Write `replay(log, initial)` that folds events through `reduce` and returns the final state. Run one log "
            "into two fresh states, print both, assert equality and the expected text."
        ),
        patterns=["def replay", "for event in log", "print("],
        mapping=(
            "Recorded event logs are the desktop equivalent of a UI test script; both Tkinter and Qt can replay "
            "synthetic events, but a pure reducer is faster and steadier."
        ),
    ),
    104: dict(
        topic="Review: events and state checklist",
        idea=(
            "This review ties the phase together with a checklist you can apply to any event-driven screen. First, is "
            "there one state object that a reducer owns, or is truth scattered across widgets and closures? Second, "
            "are events normalised into a small vocabulary before handlers see them? Third, does every subscription "
            "have a matching teardown, and does the store notify only on real change? Fourth, is the view model "
            "computed from state rather than stored beside it? Fifth, can you replay a recorded event log and get the "
            "same state without a display? Sixth, are keyboard focus and undo treated as first-class behaviour rather "
            "than afterthoughts? A screen that passes these is not automatically beautiful, but it is debuggable, "
            "testable and safe to change. Use the checklist as a review comment, not a score: each failed item names a "
            "concrete risk. The most common failure is a handler that both mutates state and updates widgets, because "
            "now two sources of truth can disagree. The second most common is a listener that is never removed. Today "
            "you run a tiny combined example: a reducer sets a name, submit validates it, and a purity check confirms "
            "that submitting twice yields the same state. The printed PASS lines are the checklist in miniature. Keep "
            "this list next to the next screen you build."
        ),
        code="""def reducer(state, action):
    if action["type"] == "set":
        return {**state, "name": action["value"]}
    if action["type"] == "submit":
        return {**state, "submitted": bool(state["name"].strip())}
    return state


checks = []
state = {"name": "", "submitted": False}
state = reducer(state, {"type": "set", "value": "ada"})
checks.append(("state in one dict", state["name"] == "ada"))
state = reducer(state, {"type": "submit"})
checks.append(("submit validates", state["submitted"] is True))
checks.append(("reducer is pure", reducer(state, {"type": "submit"}) == state))
for label, passed in checks:
    print(("PASS" if passed else "FAIL"), label)
assert all(passed for _label, passed in checks)
print("events in, state out, view derived")
""",
        variant_b="add a check that an empty name fails submission and print FAIL for that scenario",
        variant_c="turn the checks into a `review(fn)` helper that records failures instead of stopping at the first",
        mistakes=[
            "Treating the checklist as a style score instead of a list of concrete failure modes.",
            "Passing a screen that notifies on every write, which hides redraw loops until the app grows.",
            "Skipping the replay check, so a hidden global only shows up in production.",
        ],
        q1=(
            "What is the most common state bug this checklist catches?",
            "A handler that mutates both state and widgets, leaving two sources of truth that can disagree.",
        ),
        homework=(
            "Write `audit(state, log)` returning a list of `(label, passed)` checks for pure replay, non-empty "
            "validation and notification-on-change. Print PASS or FAIL for each, then assert every check passes."
        ),
        patterns=["def audit", "PASS", "print("],
        mapping=(
            "Use the checklist in code review for Tkinter and Qt screens alike; each item maps to a concrete failure "
            "such as duplicate connections or stale labels."
        ),
    ),
})
