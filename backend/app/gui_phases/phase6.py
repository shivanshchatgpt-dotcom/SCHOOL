"""GUI Applications phase 6, days 150-164: architecture, testing and performance.

The arc: how to scale past one file, separate model from view, put interfaces at
the toolkit boundary, inject dialogs, test logic headless, fake dialogs and
pickers, assert on layout arithmetic, count work on the UI thread, virtualise
long lists, audit widget lifecycles, refactor callback spaghetti, ship behind
flags with migrations, run CI on the headless logic, document UI flows, and
close with a review checklist. Every example is stdlib-only, offline and
deterministic: no display, no clock, no threads, no file I/O, and work is
measured by counting operations rather than timing them.
"""

PHASE = (
    "Architecture, Testing and Performance",
    "Structure GUI code into testable layers, replace the untestable toolkit edges with fakes, and measure and bound the work the UI thread does.",
    {
        150: dict(
            topic="Orientation: scaling past one file",
            idea=(
                "Once a GUI outgrows a single file, the failure is rarely a missing widget; it is that everything "
                "knows about everything. The discipline that scales is layering: a domain layer that holds rules "
                "and knows nothing about the screen, a services layer that coordinates work, and a ui layer that "
                "turns events into calls. The one rule that keeps this honest is direction — dependencies point "
                "inward, never outward, so the domain never imports the ui and tests can exercise the rules "
                "without a display. Thinking in terms of a graph rather than a pile of files lets you answer real "
                "questions: what does the ui indirectly depend on, is there a cycle, and which module would I "
                "change to swap a widget for a label? Cycles are the smell; a module that imports its own "
                "consumer has accidentally merged two layers and will be impossible to test in isolation. This is "
                "the same architecture conversation every desktop codebase has, whether it ships as one file or a "
                "hundred, and the answer is always a small number of named layers with one-way edges. Today you "
                "model layers as a dictionary and compute indirect dependencies to prove the direction of the "
                "arrows before writing a single widget."
            ),
            code='''LAYERS = {
    "domain": [],
    "storage": ["domain"],
    "services": ["domain", "storage"],
    "ui": ["services"],
}

def reach(module, seen=None):
    seen = seen or set()
    for dep in LAYERS[module]:
        if dep not in seen:
            seen.add(dep)
            reach(dep, seen)
    return seen

print("ui indirectly depends on:", sorted(reach("ui")))
assert reach("ui") == {"services", "domain", "storage"}
assert reach("domain") == set()
print("layers:", len(LAYERS), "edges:", sum(len(v) for v in LAYERS.values()))
print("architecture is a graph, not a pile of files")''',
            variant_b="add a 'plugins' layer that depends on 'services' and recompute what the ui reaches",
            variant_c="write `find_cycles(layers)` and check whether adding a domain -> ui edge creates a cycle",
            mistakes=[
                "Letting every module import every other, so the ui and the domain merge into one untestable blob.",
                "Putting business rules in the window class because that is where the data happens to be visible.",
                "Creating a dependency cycle between layers and hiding it until a test cannot be run in isolation.",
            ],
            q1=(
                "Why should dependencies between layers point only inward, toward the domain?",
                "It keeps the rules independent of the screen, so they can be imported and tested without a display and swapped between toolkits.",
            ),
            homework=(
                "Write `layer_deps(layers, module)` that returns the set of modules a layer depends on directly and "
                "indirectly. Define four layers, call it for the ui layer, print the sorted result, and comment "
                "which line enforces the one-way direction."
            ),
            patterns=["def ", "layer_deps", "print("],
            mapping=(
                "Real desktop projects enforce this with import linters and package boundaries; Tkinter or Qt code "
                "lives only in the outer layer, so the rest can be tested headless."
            ),
        ),
        151: dict(
            topic="MVC and MVVM",
            idea=(
                "Model, view and view model split the same code three ways, and each split answers a different "
                "question. The model owns the data and the rules and knows nothing about rendering. The view knows "
                "how to draw and how to report a user gesture; it holds no business logic. The view model sits "
                "between them and exposes the data in exactly the shape the view needs — a count formatted as a "
                "label, a flag deciding whether a button is enabled — computed from the model on demand rather "
                "than stored. That last point is the one beginners miss: a view model should derive, not "
                "duplicate, so there is only ever one source of truth. In MVVM the view binds to view-model "
                "properties; in classic MVC the controller mediates, but the concern is identical. The practical "
                "payoff is testability: you can instantiate the view model over a plain model and check every "
                "displayed string without creating a window. It also tells you where a bug lives — wrong number "
                "shown but model correct means the view model; model correct but never updated means the input "
                "path. Today you build a tiny model, a deriving view model and a view that renders the view "
                "model as text, then watch the label change as data is added."
            ),
            code='''class Model:
    def __init__(self):
        self.items = []

    def add(self, text):
        self.items.append(text)


class ViewModel:
    def __init__(self, model):
        self.model = model

    def count_label(self):
        n = len(self.model.items)
        return f"{n} item" if n == 1 else f"{n} items"


class View:
    def __init__(self, vm):
        self.vm = vm

    def render(self):
        return ["[ list ]", self.vm.count_label()]


model = Model()
view = View(ViewModel(model))
print(view.render())
model.add("milk")
print(view.render())
model.add("eggs")
print(view.render())
assert view.render()[-1] == "2 items"
print("the view renders view-model state, never the model directly")''',
            variant_b="add a `summary()` to the view model that renders the items as a comma-joined string",
            variant_c="give the view model a `can_clear()` flag and have the view render it as a button state",
            mistakes=[
                "Storing a formatted string in the view model so it drifts out of sync with the model it summarises.",
                "Putting business rules in the view, so they cannot be tested without constructing a window.",
                "Reading the model directly from the view and skipping the view model, duplicating formatting logic.",
            ],
            q1=(
                "Why should a view model derive values rather than store them?",
                "Deriving keeps a single source of truth, so the display can never disagree with the model after an edit.",
            ),
            homework=(
                "Write `view_model(model)` returning a dict with `count_label` and `summary` derived from the "
                "model's items. Build a model with two items, print the rendered dict, and comment which line "
                "proves the values are computed rather than cached."
            ),
            patterns=["def ", "view_model", "return"],
            mapping=(
                "Qt's QAbstractItemModel and MVVM frameworks are this split made formal: the view renders "
                "view-model state and reports edits back, while tests drive the view model headless."
            ),
        ),
        152: dict(
            topic="Interfaces at the toolkit boundary",
            idea=(
                "Every toolkit boundary — a dialog, a file picker, a clipboard, a status bar — is a place where "
                "your logic stops being testable unless you describe it as an interface. An interface here is just "
                "a small contract: a name and the methods that matter, with no implementation. Python expresses it "
                "with typing.Protocol or simply with duck typing: if it has read and write, it is a clipboard. "
                "The mistake is reaching for the concrete class in the middle of a function, so that testing "
                "requires the real thing and the whole point of the boundary is lost. When the contract is "
                "explicit you gain three things: you can substitute a fake in tests, you can swap the toolkit "
                "later, and the function signature documents what it truly needs. This is the seam that makes the "
                "rest of this phase possible, because dialog boxes and file pickers are exactly the parts of a "
                "desktop app that cannot run in CI. Keep the interface as small as the use implies — read and "
                "write, not the twenty methods the real class happens to have — and put it where the toolkit meets "
                "your code. Today you define a clipboard contract, satisfy it with an in-memory fake, and run a "
                "function that only knows the contract."
            ),
            code='''from typing import Protocol


class Clipboard(Protocol):
    def read(self) -> str: ...
    def write(self, text: str) -> None: ...


class FakeClipboard:
    def __init__(self):
        self.value = ""

    def read(self):
        return self.value

    def write(self, text):
        self.value = text


def copy_upper(clip, text):
    clip.write(text.upper())
    return clip.read()


clip = FakeClipboard()
print("empty:", repr(clip.read()))
print("copy:", copy_upper(clip, "ada"))
assert clip.read() == "ADA"
print("the boundary is typed by behaviour, not by a concrete widget")''',
            variant_b="add a `clear()` method to the contract and a fake that resets its value to the empty string",
            variant_c="write `apply_all(clip, texts)` that writes each text and collects the read-back values in a list",
            mistakes=[
                "Importing the concrete dialog or clipboard class inside a function, forcing a real object in tests.",
                "Making the interface as wide as the real class, so every fake must implement methods nobody calls.",
                "Claiming to accept an interface but reaching for attributes the contract never promised.",
            ],
            q1=(
                "What does a small explicit interface at the toolkit boundary buy you?",
                "You can substitute a fake in tests, swap the toolkit later, and the signature documents exactly what the logic needs.",
            ),
            homework=(
                "Write `describe(clip)` where `clip` is any object with `read` and `write`; write a marker, read it "
                "back, and return a string describing the result. Pass a fake, print the description, and comment "
                "which line proves the function never names a concrete class."
            ),
            patterns=["def ", "describe", "write("],
            mapping=(
                "This is how GUI code stays testable: Qt and Tkinter objects satisfy small protocols, and the "
                "logic is written against the protocol so it runs with no toolkit installed."
            ),
        ),
        153: dict(
            topic="Dependency injection for dialogs",
            idea=(
                "Injecting a dialog means passing it in rather than constructing it inside the code that needs it. "
                "If an editor builds its own confirmation box, then deleting a draft always opens a window and can "
                "never be tested; if it receives a dialog object, the caller decides whether that is a real box, a "
                "fake that always says yes, or a fake that records what it was asked. This is dependency "
                "injection in its smallest, most useful form, and the pattern scales from one dialog to every "
                "service an application touches. Two details matter in practice. First, inject the narrowest "
                "contract, not the whole window: the editor needs confirm(message), nothing else. Second, make the "
                "fake observable — keep the list of prompts it received — so a test can assert not only the "
                "outcome but that the user was actually asked, which is where confirmation bugs hide. Prefer "
                "constructor injection for things that live as long as the object and method arguments for "
                "one-off choices. The result is code whose control flow is decided by its caller, which is "
                "precisely what makes it runnable headless. Today you build an editor that asks an injected dialog "
                "before it deletes, and drive the same editor with a yes fake and a no fake."
            ),
            code='''class FakeDialog:
    def __init__(self, answer):
        self.answer = answer
        self.asked = []

    def confirm(self, message):
        self.asked.append(message)
        return self.answer


class Editor:
    def __init__(self, dialog):
        self.dialog = dialog
        self.text = "draft"

    def delete(self):
        if self.dialog.confirm("Delete draft?"):
            self.text = ""
            return True
        return False


yes = FakeDialog(True)
confirmed = Editor(yes)
print("yes -> deleted:", confirmed.delete(), "text:", repr(confirmed.text))
no = FakeDialog(False)
refused = Editor(no)
print("no  -> deleted:", refused.delete(), "text:", repr(refused.text))
print("dialog prompts:", yes.asked, no.asked)
assert yes.asked == ["Delete draft?"] and confirmed.text == ""
assert refused.text == "draft"
print("the caller decides which dialog runs")''',
            variant_b="inject the confirmation message too, and test an editor whose prompt text differs",
            variant_c="add a `save()` that asks a dialog only when there are unsaved changes",
            mistakes=[
                "Constructing the real dialog inside the method, so the confirmation can never be bypassed in a test.",
                "Passing the whole main window just to get one confirmation, coupling the editor to the whole UI.",
                "Testing only the yes path, so the cancel branch and the prompt text are never exercised.",
            ],
            q1=(
                "Why inject a dialog instead of constructing it in the method that needs it?",
                "The caller chooses the implementation, so tests can supply a fake that answers yes, no, or records the prompt without a window.",
            ),
            homework=(
                "Write `Editor(dialog)` with a `delete()` that confirms before clearing its text. Build two "
                "editors over fakes answering True and False, print both outcomes, and comment which line makes "
                "the real dialog replaceable."
            ),
            patterns=["def ", "delete", "dialog"],
            mapping=(
                "Desktop apps wrap QMessageBox or tkinter.messagebox behind a tiny confirm service; the rest of "
                "the code injects it so business logic never opens a window."
            ),
        ),
        154: dict(
            topic="Testing logic headless",
            idea=(
                "Logic that never touches a widget can be tested with plain asserts, and doing so headless is the "
                "highest-leverage habit in this phase. A test is just a function that sets up a known input, calls "
                "the code, and asserts on the output; a runner is a loop that calls each test and counts the "
                "passes. You do not need a framework to learn the discipline, and on a desktop app you often "
                "cannot start one anyway if the code reaches for a window during import. The point of going "
                "headless first is feedback speed and reproducibility: the same three checks run in milliseconds, "
                "on a build server, with no display. Write the test around behaviour, not implementation — the "
                "total of a cart, not that a particular dictionary key exists — so refactoring the internals does "
                "not rewrite the suite. Start each test by constructing the smallest valid input, and let each one "
                "fail for a single reason, because a test that can fail two ways tells you nothing when it breaks. "
                "Keep assertions on values you chose, not values the code happened to produce, or you will happily "
                "lock in a bug. Today you write a cart function and three tiny tests plus a runner, then print the "
                "pass count."
            ),
            code='''def cart_total(items):
    return sum(price * qty for price, qty in items)


def test_empty():
    assert cart_total([]) == 0


def test_single():
    assert cart_total([(3, 2)]) == 6


def test_many():
    assert cart_total([(2, 1), (5, 3)]) == 17


def run_tests(tests):
    passed = 0
    for name, fn in tests:
        try:
            fn()
        except AssertionError:
            print("FAIL", name)
        else:
            passed += 1
            print("pass", name)
    return passed


checks = [("empty", test_empty), ("single", test_single), ("many", test_many)]
print(run_tests(checks), "of", len(checks), "passed headless")''',
            variant_b="add a test with a zero quantity and one with a large order, then rerun the suite",
            variant_c="make `cart_total` apply a percentage discount and add a test that would catch a missing discount",
            mistakes=[
                "Importing the toolkit in a test module, so the suite cannot start without a display server.",
                "Asserting on internal structure like dictionary keys instead of the visible behaviour.",
                "Writing expected values by reading them off the current implementation, cementing any existing bug.",
            ],
            q1=(
                "Why test the logic headless before adding any window?",
                "It runs fast and everywhere, including CI with no display, and it pins the rules independently of the toolkit you draw with.",
            ),
            homework=(
                "Write `checkout(items)` computing a total and a test function `test_checkout()` asserting on two "
                "cases. Add a small runner that prints the pass count, run it, and comment which line keeps the "
                "test free of any toolkit import."
            ),
            patterns=["def test_", "assert", "print("],
            mapping=(
                "This is the suite that runs in CI: no QApplication or Tk root is created, so model and layout "
                "rules are verified on every commit."
            ),
        ),
        155: dict(
            topic="Faking dialogs and file pickers",
            idea=(
                "A dialog is the obvious place to fake, but a file picker is the one that actually blocks testing, "
                "because it couples your logic to the file system, the platform and a human. The trick is to treat "
                "the picker as a service with two operations — open a path and save to a path — and back it with a "
                "dictionary in tests, so the whole file layer becomes an in-memory mapping you can inspect and "
                "assert on. Your application code then reads and writes through the injected picker and never "
                "mentions open() or a path traversal itself, which is also what makes it testable for free. Notice "
                "that the fake is not merely a stub that returns canned data; it is a small model of storage you "
                "can mutate and then read back, so a save-then-load round trip is a real test of your logic rather "
                "than of the operating system. Keep paths as plain strings and contents as text, and keep the fake "
                "honest about missing keys by raising, so a bug where you read the wrong file surfaces instead of "
                "silently returning None. This same substitution pattern later covers clipboards, notifications and "
                "network clients. Today you build an in-memory picker and a notes service that loads and saves "
                "through it, then assert on the round trip."
            ),
            code='''class FakePicker:
    def __init__(self, files):
        self.files = dict(files)

    def open(self, path):
        return self.files[path]

    def save(self, path, text):
        self.files[path] = text


class Notes:
    def __init__(self, picker):
        self.picker = picker

    def load(self, path):
        return self.picker.open(path)

    def save(self, path, text):
        self.picker.save(path, text)


picker = FakePicker({"a.txt": "hello"})
notes = Notes(picker)
print("loaded:", notes.load("a.txt"))
notes.save("b.txt", "world")
print("files now:", sorted(picker.files))
assert notes.load("b.txt") == "world"
print("file I/O faked in memory, no disk touched")''',
            variant_b="make `load` return an empty string for a missing path instead of raising, and test both",
            variant_c="add an `append(path, text)` that loads, concatenates and saves, then test a two-step edit",
            mistakes=[
                "Calling open() inside the service, so every test writes to the real disk and leaves files behind.",
                "Using a fake that returns canned data but never records saves, so the save path is never verified.",
                "Mixing the dialog confirmation and the file picker into one oversized fake, hiding what each test needs.",
            ],
            q1=(
                "Why is an in-memory fake picker more useful than patching open()?",
                "It models storage you can mutate and read back, so tests assert on your logic and never touch the disk or the platform.",
            ),
            homework=(
                "Write `Notes(picker)` with `save` and `load`, plus a `FakePicker(files)` backed by a dict. Perform "
                "a save then load in one test, print the fake's keys, and comment which line keeps the disk out of "
                "the loop."
            ),
            patterns=["def ", "FakePicker", "save("],
            mapping=(
                "QFileDialog and filedialog.askopenfilename are replaced by this service in tests, so import and "
                "export logic is verified without a human choosing a file."
            ),
        ),
        156: dict(
            topic="Layout tests with numbers",
            idea=(
                "Layout bugs are arithmetic bugs, and arithmetic is the easiest thing in a GUI to test, because the "
                "answer is numbers. Instead of eyeballing a window, you call your layout function with a fixed "
                "total and fixed weights and assert on the exact positions and sizes: where the second column "
                "starts, how wide the last cell is, whether the cells plus the gaps fill the container exactly. "
                "Those assertions are precise enough to catch the classic off-by-one where the final row swallows "
                "the rounding remainder, and they do not care which toolkit will eventually draw the result. The "
                "habit to build is to return geometry as data — a list of (x, width) pairs — rather than setting "
                "properties on widgets, so the calculation is separate from the rendering. Then a test is just a "
                "comparison against hand-computed values, and a failing test points at the formula, not at a "
                "screenshot. Use small, round numbers when you first derive the expected values so the test is "
                "readable, and add one case with an awkward remainder because that is where conservation of space "
                "breaks. Rounding policy should be stated once and applied consistently, usually by giving the "
                "leftover to the last cell. Today you return cell positions for a weighted row and assert on exact "
                "offsets and the total."
            ),
            code='''def grid_positions(total, weights, gap=0):
    usable = total - gap * (len(weights) - 1)
    share = usable // sum(weights)
    sizes = [w * share for w in weights]
    sizes[-1] += usable - sum(sizes)
    positions = []
    x = 0
    for size in sizes:
        positions.append((x, size))
        x += size + gap
    return positions


cells = grid_positions(100, [1, 2, 1], gap=4)
print("cells:", cells)
assert cells[0] == (0, 23)
assert cells[1][0] == 27
assert cells[-1][0] + cells[-1][1] == 100
print("last cell ends at", cells[-1][0] + cells[-1][1], "which fills the row")
print("layout is arithmetic you can assert on")''',
            variant_b="distribute 90 across weights [2, 1] with a gap of 6 and check the cells fill the row",
            variant_c="add a minimum width per column and assert the total never exceeds the container",
            mistakes=[
                "Testing layout by looking at a screenshot instead of asserting on the computed geometry.",
                "Forgetting to subtract the gaps, so the cells are a few pixels too wide and overflow the row.",
                "Losing the rounding remainder entirely, leaving a one-pixel strip unaccounted for at the edge.",
            ],
            q1=(
                "Why is asserting on exact cell positions a better layout test than reading a screenshot?",
                "The numbers prove space is conserved and point straight at the formula when they are wrong, with no display involved.",
            ),
            homework=(
                "Write `columns(total, weights, gap)` returning (x, width) pairs that fill the total exactly. Test "
                "it with a round case and an awkward remainder, print both, and comment which line gives the "
                "leftover to the last column."
            ),
            patterns=["def ", "columns", "sum("],
            mapping=(
                "This is the arithmetic behind Tkinter's grid column weights and Qt's stretch factors, verified "
                "headless so a resize bug is caught before anyone opens the window."
            ),
        ),
        157: dict(
            topic="Profiling the UI thread",
            idea=(
                "You cannot fix a slow interface by adding threads first; you find the heavy work and make each "
                "turn of the event loop shorter. Profiling a GUI therefore starts by measuring where the work goes "
                "in one frame, and the most robust way to reason about it — and the only way to do it offline and "
                "deterministically — is to count operations rather than to time them. Timing on a busy machine "
                "tells you little and varies between runs; counting tells you exactly which handler does the most "
                "per interaction and whether a frame exceeds a budget you have set. Give each kind of work a cost, "
                "multiply by how often it happens in the frame, and sort the result. The usual answer is that "
                "layout or painting dominates because it runs on every event, while a cheap handler that fires "
                "constantly can still be the real cost. Once the number is on the page, the fixes are ordinary: "
                "cache the expensive calculation, coalesce several events into one redraw, or move work out of the "
                "frame entirely. Keep the budget explicit so a regression is visible, and profile with "
                "representative data because one item is not a list. Today you count the operations per frame, "
                "print each contribution, and flag the hottest handler."
            ),
            code='''def profile_frame(events, cost):
    total = 0
    hottest = None
    for name, count in events:
        work = count * cost[name]
        total += work
        if hottest is None or work > hottest[1]:
            hottest = (name, work)
        print(f"{name:8} {count:3} x {cost[name]:2} = {work}")
    return total, hottest


cost = {"input": 1, "layout": 3, "paint": 5}
events = [("input", 4), ("layout", 6), ("paint", 2)]
total, hottest = profile_frame(events, cost)
print("total ops:", total, "hottest:", hottest)
assert total == 4 * 1 + 6 * 3 + 2 * 5
assert hottest == ("layout", 18)
print("cost is counted in operations, so the profile is deterministic")''',
            variant_b="double the layout frequency and check which handler becomes the hottest",
            variant_c="add a budget argument and print whether the total is over it",
            mistakes=[
                "Profiling with time.time(), so the numbers change on every machine and cannot be asserted on.",
                "Measuring the total only, without per-handler contributions, so the bottleneck stays invisible.",
                "Optimising the cheapest handler because it looks busy, instead of the one doing the most work.",
            ],
            q1=(
                "Why count operations per frame instead of timing the UI thread?",
                "Counting is deterministic and machine-independent, so you can compare handlers and assert on a budget without a clock.",
            ),
            homework=(
                "Write `frame_cost(events, cost)` returning the total operations and the name of the heaviest "
                "handler. Feed it three event kinds, print each contribution and the total, and comment which line "
                "avoids any timing call."
            ),
            patterns=["def ", "frame_cost", "total"],
            mapping=(
                "This is the reasoning behind Qt's event-loop warnings and Tkinter's sluggish-resize complaints: "
                "measure the work per turn before reaching for threads."
            ),
        ),
        158: dict(
            topic="Virtualising long lists",
            idea=(
                "A list with ten thousand rows does not need ten thousand widgets; it needs the handful that can "
                "fit on screen, plus arithmetic to work out which ones those are. That is virtualisation, and the "
                "reason it matters on the desktop is that every real widget costs memory and layout time, so "
                "handing a toolkit a huge list is what makes a window crawl. The idea is simple once stated: the "
                "scroll position is the first visible index, the viewport height is how many rows fit, and the "
                "visible window is a slice between them. Rendering asks the model for that slice and draws only "
                "it; a scroll event changes the start index and redraws the slice, not the list. The subtle parts "
                "are reuse and boundaries — clamping the start so the last window is not short, and handling a "
                "scroll past the end — which are again plain arithmetic and therefore testable without a screen. "
                "You can assert that the returned window has exactly the viewport size, that its first index "
                "matches the request, and that the offset and count stay in range for every position. This is the "
                "same reason list and table views in Qt and Tkinter's tree widgets expose a viewport and reuse row "
                "widgets. Today you return a window of a long list and print the first few rows plus the count of "
                "what was not drawn."
            ),
            code='''def visible_window(items, first, height):
    first = max(0, min(first, max(0, len(items) - 1)))
    end = min(len(items), first + height)
    return [(i, items[i]) for i in range(first, end)], end < len(items)


items = [f"row-{i:03d}" for i in range(1000)]
rows, more_below = visible_window(items, 480, 5)
for index, text in rows:
    print(index, text)
print("more below:", more_below, "| rendered:", len(rows), "of", len(items))
assert len(rows) == 5 and rows[0][0] == 480
print("a virtual list renders a window, never the whole model")''',
            variant_b="scroll to the last page and assert the window is shorter than the viewport height",
            variant_c="add a `clamp_scroll(first, total, height)` helper and test scrolling beyond the end",
            mistakes=[
                "Creating a widget for every row, so a long list allocates thousands of objects nothing displays.",
                "Forgetting to clamp the start index, so the final scroll position returns an empty or short window.",
                "Rendering outside the viewport then hiding it, which still pays the allocation and layout cost.",
            ],
            q1=(
                "Why does virtualising a long list keep the interface responsive?",
                "Only the visible rows are created and laid out, so cost tracks the viewport size rather than the length of the model.",
            ),
            homework=(
                "Write `window(items, first, height)` returning the visible (index, value) pairs and a flag for "
                "more below. Test a middle position and the last page, print both, and comment which line clamps "
                "the requested start index."
            ),
            patterns=["def ", "window", "min("],
            mapping=(
                "QListView and Tkinter's Treeview virtualise by default; this is the arithmetic behind their "
                "scroll-to-item and row-recycling behaviour."
            ),
        ),
        159: dict(
            topic="Memory and widget leaks",
            idea=(
                "Widgets own children, children hold references, and the leak happens when a destroyed window is "
                "still reachable from somewhere else — a callback list, a module global, a cache. The mental model "
                "is a tree: tearing down a parent must walk its descendants and release each, and any node the "
                "walk misses stays alive as a ghost. In a real toolkit the tree also holds native resources, so an "
                "orphan is not just memory but a window that may still respond to events. Testing for leaks "
                "headlessly means modelling the tree as nodes and counting what a destroy actually removes, then "
                "asserting the count equals the whole subtree and that nothing remains reachable from the root. "
                "The hard part is not the walk but the references hidden in closures and registries, which is why "
                "the discipline is to connect callbacks through a registry that is cleared on teardown and never "
                "to keep a strong reference in a global map. A weak reference, where available, is the belt to the "
                "registry's braces. The same reasoning explains why timers must be cancelled and why a signal "
                "connected to a deleted object can keep it alive. Today you build a small node tree, count its "
                "live members, destroy the root, and verify the removal count matches the subtree."
            ),
            code='''class Node:
    def __init__(self, name):
        self.name = name
        self.children = []


class Tree:
    def __init__(self, root):
        self.root = root

    def destroy(self, node):
        removed = 1
        for child in list(node.children):
            removed += self.destroy(child)
        node.children.clear()
        return removed


def walk(node):
    return [node] + [n for child in node.children for n in walk(child)]


root = Node("window")
for i in range(4):
    root.children.append(Node(f"panel-{i}"))
root.children[0].children.append(Node("label"))
print("alive before:", len(walk(root)))
removed = Tree(root).destroy(root)
print("removed:", removed, "| alive after:", len(walk(root)))
assert removed == 6 and walk(root) == [root]
print("destroy walks every child, so no widget is orphaned")''',
            variant_b="add a grandchild under a second panel and confirm the removal count follows the subtree",
            variant_c="add a `leaked(registry, dead)` check asserting no destroyed name remains in a callback map",
            mistakes=[
                "Deleting a parent without walking its children, leaving orphan widgets alive off the tree.",
                "Keeping destroyed widgets in a global callback registry that is never cleared on teardown.",
                "Assuming a reference dropped one place is collected everywhere, ignoring closures that still hold it.",
            ],
            q1=(
                "Why can a destroyed window still be alive in memory?",
                "Something else — a registry, a closure, a timer — still holds a reference, so the object is reachable and never released.",
            ),
            homework=(
                "Write `count_nodes(node)` that recursively counts a widget tree, then `destroy(root)` returning "
                "how many nodes it removed. Build a small tree, print the counts, and comment which line walks the "
                "children so nothing is orphaned."
            ),
            patterns=["def ", "count_nodes", "children"],
            mapping=(
                "Qt's parent-child ownership and Tkinter's destroy() follow this model; the leak shows up as a "
                "window that lingers in the task bar or a callback firing on a dead widget."
            ),
        ),
        160: dict(
            topic="Refactoring callback spaghetti",
            idea=(
                "Callback spaghetti is what you get when handling grows as nested ifs inside one handler; every new "
                "event adds a branch, and reading the function becomes a hunt through conditions. The cure is a "
                "dispatch table: a dictionary from an event name to a small function, so adding an event adds one "
                "row, not one branch. Each handler takes the state and the event and returns the new state, which "
                "keeps every piece independently callable and testable, and the runner becomes a loop that looks "
                "up a name and reports the unknown ones instead of falling through silently. This is the same shape "
                "we met with events in a queue, now applied as a refactor: the behaviour does not change, only its "
                "address. Two rules keep the table clean — handlers stay small and do one thing, and shared "
                "helpers such as normalisation are named functions rather than repeated inline, so the table reads "
                "like a list of intents. When a handler needs configuration, build it with a closure that captures "
                "the constant once, and keep state immutable by returning a copy rather than mutating in place, "
                "which is what stops order-dependent bugs. Today you replace a pile of conditionals with a "
                "name-to-handler table, run a few commands including an unknown one, and assert on the final state."
            ),
            code='''def normalize(text):
    return text.strip().lower()


def clear(state, event):
    return {**state, "text": ""}


HANDLERS = {
    "submit": lambda state, event: {**state, "text": normalize(event["value"])},
    "clear": clear,
    "toggle": lambda state, event: {**state, "enabled": not state["enabled"]},
}


def run(state, commands):
    for name, event in commands:
        handler = HANDLERS.get(name)
        if handler is None:
            print("unknown command:", name)
            continue
        state = handler(state, event)
    return state


state = run(
    {"text": "", "enabled": True},
    [("submit", {"value": "  Ada  "}), ("toggle", {}), ("frob", {})],
)
print(state)
assert state == {"text": "ada", "enabled": False}
print("a dispatch table replaces nested callbacks")''',
            variant_b="add a 'reset' command that restores both fields and include it in the command list",
            variant_c="make each handler return (state, handled) and count the unhandled commands",
            mistakes=[
                "Growing one handler with nested ifs until adding an event means editing three branches.",
                "Mutating the shared state dictionary in place, so handlers depend on the order they run in.",
                "Copying the normalisation logic into several branches instead of one named helper.",
            ],
            q1=(
                "What does a dispatch table improve over a handler full of ifs?",
                "Adding an event adds one row instead of a branch, and each handler stays small, independent and testable.",
            ),
            homework=(
                "Write `run(state, commands, handlers)` that looks up each command in a handler table, reports "
                "unknown names, and returns the final state. Register three handlers, run a list including an "
                "unknown one, and comment which line keeps state immutable."
            ),
            patterns=["def ", "run", "handlers"],
            mapping=(
                "This is the standard cleanup for Qt's connect soup and Tkinter's command= bindings: name each "
                "intent once and route events through a table."
            ),
        ),
        161: dict(
            topic="Feature flags and migrations",
            idea=(
                "Software changes shape over time, and every installed copy of an app carries an old shape with "
                "it, so a desktop program needs two related mechanisms: migrations that transform old data into "
                "the current shape, and feature flags that change behaviour without changing code. A migration is "
                "a small, ordered, idempotent function: it reads the version stamped in the config, applies each "
                "step it is missing, and rewrites the version, so running it twice is harmless. Keeping migrations "
                "one-way and versioned is what lets you reason about any file you find in the wild instead of "
                "guessing. A feature flag is a named switch consulted at the point of behaviour — read the flag "
                "here, choose dark here — so a half-finished path can ship dark and be turned on without a new "
                "build. The two compose: you migrate the data into a shape that has room for the new feature, then "
                "a flag decides whether the feature is active. In tests you set flags explicitly and assert both "
                "branches, which is impossible if flags are read from the environment at import time. Always "
                "default flags to a known value and keep the flag list short, because flags left in place become "
                "untested code. Today you write a migration and a flag application, then assert on the migrated "
                "config with the flags on."
            ),
            code='''FLAGS = {"dark_mode": True, "compact_rows": False}


def migrate(config):
    out = dict(config)
    if out.get("version", 0) < 2:
        out["theme"] = out.get("theme", "light")
        out["version"] = 2
    return out


def apply_flags(config, flags):
    out = dict(config)
    if flags.get("dark_mode"):
        out["theme"] = "dark"
    if flags.get("compact_rows"):
        out["density"] = "compact"
    return out


old = {"theme": "light"}
migrated = migrate(old)
print("migrated:", migrated)
print("with flags:", apply_flags(migrated, FLAGS))
print("migrate twice is stable:", migrate(migrated) == migrated)
assert migrate(migrated)["version"] == 2
assert apply_flags(migrated, FLAGS)["theme"] == "dark"
print("migrations change shape; flags change behaviour")''',
            variant_b="add a version 3 migration that introduces a numeric font scale with a default",
            variant_c="add a 'compact_rows' true case and assert both density values from the same config",
            mistakes=[
                "Writing a migration that is not idempotent, so re-running it changes the data again.",
                "Reading flags from the environment at import time, so tests cannot set both branches.",
                "Leaving old flags in the code forever, turning them into untested branches nobody dares remove.",
            ],
            q1=(
                "What is the difference between a migration and a feature flag?",
                "A migration changes the shape of stored data once per version, while a flag changes behaviour at runtime without changing data.",
            ),
            homework=(
                "Write `migrate(config)` that stamps a new version idempotently and `apply(config, flags)` that "
                "reads two named flags. Test an old config, print it before and after, and comment which line makes "
                "migration safe to run twice."
            ),
            patterns=["def migrate", "def apply", "version"],
            mapping=(
                "Desktop apps persist settings to disk, so this is the pattern behind rolling a config forward "
                "across releases while a dark-mode flag ships dark."
            ),
        ),
        162: dict(
            topic="CI for GUI logic",
            idea=(
                "Continuous integration for a GUI app sounds impossible until you split it in two: the logic runs "
                "headless on every commit, and only a thin smoke test needs a display. The logic suite is just the "
                "tests from this phase — model rules, layout arithmetic, migration and flag behaviour — and it "
                "runs anywhere because nothing in it opens a window or reads a real file. A CI job for this is a "
                "small script: import the modules, run each check, print a status per item, and exit non-zero if "
                "any failed. Two guardrails make it trustworthy. First, forbid GUI imports in the headless tests, "
                "because a single stray toolkit import turns the build into a machine that needs a display, and "
                "assert that rule rather than trusting code review. Second, test the version matrix that matters "
                "and keep the job deterministic, since a flaky gate is worse than no gate. Report per-check "
                "results, not one opaque failure, because the person reading the log at midnight is you. Keep the "
                "fast logic suite separate from the slow display suite so a red build is quick to classify, and "
                "make the smoke test use a virtual display or a wrapper object. Today you build a tiny checker that "
                "flags a lesson importing the toolkit, run it over three lessons, and count failures."
            ),
            code='''def check(lesson):
    problems = []
    if not lesson.get("code"):
        problems.append("empty code")
    if "tkinter" in lesson.get("imports", []):
        problems.append("gui import in headless test")
    return problems


LESSONS = [
    {"name": "cart", "code": "total()", "imports": []},
    {"name": "dialog", "code": "confirm()", "imports": []},
    {"name": "broken", "code": "", "imports": ["tkinter"]},
]


def run_ci(lessons):
    failures = 0
    for lesson in lessons:
        problems = check(lesson)
        status = "ok" if not problems else "fail"
        print(f"{lesson['name']:8} {status} {problems}")
        failures += bool(problems)
    return failures


failures = run_ci(LESSONS)
print("failures:", failures, "of", len(LESSONS))
assert failures == 1
print("CI tests the logic headless, with no display required")''',
            variant_b="add a rule flagging any import starting with 'PyQt' or 'PySide' and test a fourth lesson",
            variant_c="make `run_ci` return the list of failing names and print it instead of a count",
            mistakes=[
                "Letting a test import the toolkit, so the whole CI job now needs a display server to start.",
                "Reporting one boolean for the build instead of per-check results, so a failure is hard to place.",
                "Using wall-clock timing in the suite, making the gate flaky and the build red for no reason.",
            ],
            q1=(
                "How do you run continuous integration on a GUI app without a display?",
                "Split the logic suite from the smoke test: the model, layout and flag tests are headless and run everywhere, and only the smoke test needs a screen.",
            ),
            homework=(
                "Write `lint_lesson(lesson)` returning a list of problems, including a GUI import, and `run_ci(lessons)` "
                "printing a status per lesson. Run it over three lessons, print the failure count, and comment which "
                "line forbids the toolkit import."
            ),
            patterns=["def ", "run_ci", "print("],
            mapping=(
                "This is the headless job in a desktop repo's CI: it runs on every push, while a separate "
                "off-screen smoke test exercises the real Tkinter or Qt window."
            ),
        ),
        163: dict(
            topic="Documentation for UI flows",
            idea=(
                "A user interface flow — open a file, confirm a delete, export a report — is not documented by "
                "listing buttons; it is documented by naming the steps, the event that triggers each one, and "
                "where it goes next. Written that way, a flow is a small graph, and the same data can render a "
                "help page, a test that every step is reachable, and a checklist for review. The discipline pays "
                "for itself because UI bugs are usually broken flows: a dialog with no way back, a menu item that "
                "never enables, a save step that can be skipped. A flow record keeps three things per step — what "
                "the user does, what the code does in response, and the next step — plus the failure path that "
                "returns somewhere sensible. From that structure you can assert properties automatically: every "
                "step has a trigger, every non-terminal step has a successor, and the graph is connected. The "
                "writing is the work; the rendering is a loop. Keep the vocabulary the same one you use in the "
                "code, so the documentation cannot drift into a second, prettier truth. On a desktop app this "
                "doubles as the acceptance checklist before a release, since each step is something a person can "
                "actually perform. Today you encode a short flow and render it as readable lines, asserting that "
                "every step is documented."
            ),
            code='''FLOW = {
    "open": {"trigger": "Ctrl+O", "next": "pick_file"},
    "pick_file": {"trigger": "file dialog", "next": "load"},
    "load": {"trigger": "read file", "next": None},
}


def document(flow):
    lines = []
    for step, node in flow.items():
        nxt = node["next"] or "done"
        lines.append(f"{step} <- {node['trigger']} -> {nxt}")
    return lines


lines = document(FLOW)
for line in lines:
    print(line)
missing = [s for s in FLOW if "next" not in FLOW[s]]
print("steps:", len(lines), "| undocumented:", missing)
assert not missing and len(lines) == 3
print("every UI flow step names a trigger and a next step")''',
            variant_b="add a 'cancel' step reachable from the dialog and assert the flow stays connected",
            variant_c="write `reachable(flow, start)` and check every step can be reached from 'open'",
            mistakes=[
                "Documenting a flow as a list of buttons, hiding the order and the branches between them.",
                "Leaving a step with no next and no way back, so the user is stranded mid-task.",
                "Using different names in the docs than in the code, so the documentation drifts from the truth.",
            ],
            q1=(
                "Why document a UI flow as a graph of steps rather than a list of controls?",
                "The graph captures triggers, order and branches, so you can test reachability and spot a step with no way forward.",
            ),
            homework=(
                "Write `document(flow)` rendering each step as 'step <- trigger -> next', and `complete(flow)` "
                "raising or returning False for any step missing a trigger or successor. Test a small flow, print "
                "the lines, and comment which line checks the flow is fully specified."
            ),
            patterns=["def document", "def complete", "print("],
            mapping=(
                "This is the user-journey map behind desktop help, installers and wizards; encoding it as data "
                "lets release checklists verify every step is reachable."
            ),
        ),
        164: dict(
            topic="Review: architecture and testing checklist",
            idea=(
                "A checklist closes the phase because it turns everything you learned into a series of questions "
                "you can ask of any interface. Four families matter. Architecture: does the model import the ui, "
                "are dependencies pointing inward, is the widget tree data you can walk? Boundaries: are dialogs "
                "and pickers injected, described by the smallest contract, and fakeable? Testing: do the rules run "
                "headless, do the layout assertions check exact numbers, are flags and migrations covered both "
                "ways? Performance and lifecycle: is the hot handler counted and budgeted, are long lists "
                "virtualised, does teardown release every widget? A review is then mechanical — run the checklist "
                "over a small sample project, print a pass or fail for each item, and count the score, because an "
                "item you cannot evaluate is an item you cannot claim. The act of scoring is the lesson: it "
                "exposes the difference between code that merely works on your machine and code whose seams are "
                "explicit enough to change, test and ship. Keep the list short enough to actually run before every "
                "release, and delete items that never fail, since a checklist nobody trusts is theatre. Today you "
                "encode such a checklist, evaluate it against a sample project dictionary, and print the score "
                "with an assertion."
            ),
            code='''CHECKLIST = [
    ("model has no ui imports", lambda p: not any(i.startswith("ui") for i in p["imports"])),
    ("dialogs injected", lambda p: p["dialogs_injected"]),
    ("tests run headless", lambda p: p["headless_tests"]),
    ("lists virtualised", lambda p: p["virtual_lists"]),
]

PROJECT = {
    "imports": ["domain", "storage"],
    "dialogs_injected": True,
    "headless_tests": True,
    "virtual_lists": False,
}


def review(checklist, project):
    return [(name, bool(check(project))) for name, check in checklist]


results = review(CHECKLIST, PROJECT)
for name, ok in results:
    print("pass" if ok else "FAIL", name)
score = sum(ok for _, ok in results)
print("score:", score, "of", len(CHECKLIST))
assert score == 3
print("architecture is shippable when its seams are explicit")''',
            variant_b="mark virtualisation as done and confirm the score rises to four of four",
            variant_c="add a 'picker injected' item and evaluate it against a project that fails it",
            mistakes=[
                "Treating a review as a feeling about the code rather than a list of answerable questions.",
                "Keeping checklist items nobody can evaluate, so the review silently skips them.",
                "Never deleting items that always pass, until the checklist becomes theatre nobody runs.",
            ],
            q1=(
                "Why express an architecture review as a checklist of evaluable items?",
                "Each item becomes an answerable question with a pass or fail, so the review is mechanical and gaps are visible instead of guessed.",
            ),
            homework=(
                "Write `review(project, checklist)` where checklist is a list of (name, test) pairs, returning the "
                "results, and a `score` function that counts passes. Evaluate a sample project, print each item and "
                "the score, and comment which line makes an unanswerable item impossible."
            ),
            patterns=["def review", "def score", "print("],
            mapping=(
                "Mature desktop teams keep this as a pre-release gate: the same questions over model/view "
                "separation, injected dialogs and virtualised lists, checked before anything ships."
            ),
        ),
    },
)
