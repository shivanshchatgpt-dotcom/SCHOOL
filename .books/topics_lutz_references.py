"""Canonical topic batch: references versus copies (Lutz ch 9)."""
from canonical_topics import topic

LUTZ_CH9_COPIES = {
    "book": "learning-python",
    "chapter": 9,
    "pages": [225, 256],
    "sections": ["References Versus Copies", "Assignment Creates References, Not Copies",
                 "Built-in Type Gotchas"],
}


topic(
    "canonical:references-vs-copies",
    "Assignment shares an object rather than duplicating it, so when a container must be independent of its source you have to copy it on purpose",
    sources=[dict(LUTZ_CH9_COPIES)],
    concept=(
        "Assigning a name to an existing object, or passing one into a function, or "
        "nesting it inside another container, creates a reference to that object and not "
        "a second copy of it. Two names can therefore point at one list, and an in-place "
        "change made through either name is visible through the other, because there is "
        "only ever one list. This is usually desirable, since it is what makes programs "
        "cheap and data easy to share, but it becomes a defect whenever a piece of code "
        "assumes it owns an independent copy of something it merely holds a reference to. "
        "The remedy is to copy on purpose, and there are two depths to choose between. A "
        "shallow copy duplicates the outermost container, so the new object's elements "
        "still reference the same nested objects, and it is enough when only the outer "
        "structure has to be independent. A deep copy duplicates recursively, so nested "
        "containers are duplicated too, and it is required when the nested objects will "
        "also be mutated. The choice of depth is the real decision, because a shallow "
        "copy is fast and usually adequate while a deep copy can be expensive and can "
        "copy more than intended. The way to reason about any case is to ask which level "
        "of the structure will be changed in place, and to copy exactly that level."
    ),
    prerequisites=["canonical:variable-binds-to-object"],
    pitfalls=[
        "Appending to a list that was assigned from another name and expecting the "
        "source to be unaffected, because both names hold one object.",
        "Taking a shallow copy of a list of lists and mutating a nested list, which "
        "changes the source too because the inner lists are still shared.",
        "Copying by hand with a loop that only reads the values, which shares any mutable "
        "element it does not explicitly reconstruct.",
    ],
    adapters={
        "machine-learning": {
            "framing": (
                "A preprocessing function that modifies a caller's dataset in place is a "
                "silent corruption, because the caller still holds a reference to the same "
                "arrays."
            ),
            "application": (
                "Walk the example as a scaling function that must not touch the caller's "
                "data. The function copies the rows it receives before changing them, so "
                "the caller's originals stay as they were, and the printed comparison "
                "proves it. The interesting case is the nested one: a list of feature "
                "lists needs a deep copy, because a shallow copy would leave the inner "
                "lists shared and a change to a feature vector would still reach the "
                "caller. Choosing the depth is the judgement this topic trains, and the "
                "test is always the same question: which level of the structure gets "
                "modified in place? Copy that level. When a function reports that it "
                "transformed the data and the caller later finds its own copy changed, "
                "the missing copy at the mutating level is the cause, and it is a bug "
                "that produces no error message at all."
            ),
            "example_hint": "copy before transforming and verify the caller's data is untouched",
            "assessment_angle": "when a shallow copy is enough and when a deep copy is required",
            "day": 7,
            "title": "Transform a Copy, Leave the Caller's Data Alone",
            "code": """import copy

features = [[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]]


def scale(rows, factor):
    result = copy.deepcopy(rows)          # inner lists are also copied
    for row in result:
        for i in range(len(row)):
            row[i] *= factor
    return result


doubled = scale(features, 2.0)
print("input :", features)
print("output:", doubled)

shallow = copy.copy(features)
shallow[0][0] = 99
print("after shallow copy mutation:", features)
""",
            "questions": [
                "Why does scale use deepcopy instead of copy for a list of lists?",
                "After the shallow copy is mutated, why does the original features change too?",
                "What symptom would this defect produce in a caller that never looks at the function's internals?",
            ],
            "answers": [
                "Because the function modifies the inner lists in place, so those inner lists have to be independent copies too, and copy would still share them with the caller.",
                "Because a shallow copy duplicates only the outer list, so its inner lists are the same objects as the caller's, and changing one through the copy reaches the original.",
                "Silently wrong data with no error raised, since the caller's dataset would have been changed through the shared inner objects while every reported output looked correct.",
            ],
            "homework": (
                "Write transform_copy.py with a list of at least five feature lists of varying "
                "length. Write a function that deep-copies the input and scales every value by a "
                "factor in place, then print the input and the returned output to show the input "
                "is unchanged. Then make a shallow copy of the input, mutate one element of a "
                "nested list, and print the original to show the sharing. Observable output: four "
                "lines, the last one showing the original changed by the shallow copy."
            ),
            "required_patterns": ["copy.deepcopy", "copy.copy", "for ", "range(", "print("],
        },
        "data-viz": {
            "framing": (
                "A figure is often built from a template series, and mutating the "
                "template while building the figure corrupts the next chart that uses it."
            ),
            "application": (
                "Walk the example as two charts built from one shared template. The "
                "first chart appends to a copy of the template and the second to another "
                "copy, so both are built from an intact base, whereas a code path that "
                "appends to the template itself would leak the first chart's annotations "
                "into the second. The useful generalisation is that any reusable "
                "structure used as a starting point has to be copied before it is "
                "changed, because a template is shared by design and shared means "
                "mutable-visible-to-everyone. A shallow copy is enough when the template "
                "holds only numbers and strings, since those are immutable and cannot be "
                "changed in place, which is the case where the cheaper copy is genuinely "
                "adequate. Recognising that case is the skill: the depth of the copy "
                "should match the depth at which mutation happens, and no deeper."
            ),
            "example_hint": "copy a shared template before annotating each chart from it",
            "assessment_angle": "what a shared template costs and when the shallow copy suffices",
            "day": 7,
            "title": "Copy the Template Per Chart, Keep the Base Reusable",
            "code": """import copy

template = {"title": "Untitled", "points": [], "unit": "count"}


def build(source, name, values):
    chart = copy.deepcopy(source)
    chart["title"] = name
    chart["points"] = list(values)
    return chart


a = build(template, "North", [10, 20, 30])
b = build(template, "South", [5, 15, 25])

print("chart A:", a)
print("chart B:", b)
print("template intact:", template)

broken = copy.copy(template)
broken["points"].append(999)
print("after shallow mutation:", template)
""",
            "questions": [
                "Why does build copy the template instead of annotating it directly?",
                "The template's title and unit are strings, so why is a shallow copy of them harmless even though the final example shows sharing?",
                "What does the final printed template show, and what would happen to a third chart built after that mutation?",
            ],
            "answers": [
                "Because the template is a shared starting point, so annotating it directly would carry the first chart's title and points into every chart built afterwards.",
                "Because strings are immutable and cannot be changed in place, so sharing them cannot cause leakage; the danger is only in the mutable nested list, which is what the final example demonstrates.",
                "It shows the points list now contains 999, because a shallow copy shares that list, so a third chart built from the mutated template would inherit the stray point.",
            ],
            "homework": (
                "Write template_charts.py with a template dictionary containing a title, an empty "
                "points list and a unit string. Write a build function that deep-copies the "
                "template, sets the title and replaces the points with a supplied list, then build "
                "at least three charts from it and print each one. Print the template at the end to "
                "show it is intact, then make a shallow copy of it, append to its points, and "
                "print the template again to expose the sharing. Observable output: three chart "
                "lines, the intact template, then the corrupted template."
            ),
            "required_patterns": ["copy.deepcopy", "copy.copy", "list(", "for ", "print("],
        },
        "api-building": {
            "framing": (
                "A request handler that caches a payload and later mutates it is changing "
                "the caller's object, because the cache stored a reference."
            ),
            "application": (
                "Walk the example as a cache storing incoming payloads. The handler "
                "stores a copy of the payload, so a later normalisation step performed on "
                "the cached entry does not also edit the object the caller still holds. "
                "That distinction is invisible in the happy path and shows up only when a "
                "caller inspects its own object after the call and finds it changed, "
                "which is why the discipline is worth building in from the start. The "
                "depth question appears concretely: a payload of flat key-value pairs "
                "needs only a shallow copy because the values are immutable, while a "
                "payload with nested lists needs a deep one, and a request schema with "
                "fixed top-level fields is the practical test of which case you are in. "
                "The transferable rule is that any structure a function intends to keep "
                "and later modify has to be copied at exactly the level of the intended "
                "modification."
            ),
            "example_hint": "copy a payload before caching and normalise only the copy",
            "assessment_angle": "what the copy protects the caller from and which depth applies",
            "day": 7,
            "title": "Cache a Copy: Later Normalisation Must Not Reach the Caller",
            "code": """import copy

cache = []


def handle(payload):
    stored = copy.deepcopy(payload)
    stored["tags"] = sorted(set(stored["tags"]))
    stored["status"] = "processed"
    cache.append(stored)
    return stored["status"]


incoming = {"id": 7, "tags": ["beta", "alpha", "beta"], "notes": ["first"]}
status = handle(incoming)

print("status:", status)
print("cached:", cache[0])
print("caller's payload:", incoming)
print("caller untouched:", incoming["tags"] != cache[0]["tags"])
""",
            "questions": [
                "Why does the handler store a copy of the payload rather than the payload itself?",
                "The tags list is normalised on the stored copy. What would the caller observe if the payload had been stored directly?",
                "Suppose a payload contained only flat immutable values and no lists. Which copy depth would be sufficient, and why?",
            ],
            "answers": [
                "Because the handler changes the stored entry later, and a direct store would share the caller's object, so those changes would reach the caller's copy too.",
                "Its own tags list would arrive sorted and deduplicated after the call, even though the caller never asked for that, and no error would be raised.",
                "A shallow copy, because there would be no mutable nested object to share, so duplicating the outer dictionary is enough to isolate every later change.",
            ],
            "homework": (
                "Write cache_copy.py with a handle function that deep-copies an incoming payload, "
                "sorts and deduplicates a nested list on the copy, sets a status field, appends the "
                "copy to a cache list and returns the status. Call it with at least three payloads "
                "whose nested lists contain duplicates and print the status, the cache entry and "
                "the caller's payload for one of them, plus a boolean showing the caller's list "
                "differs from the cached one. Observable output: at least one set of four lines per "
                "payload, with the caller's list unsorted."
            ),
            "required_patterns": ["copy.deepcopy", "sorted(", "set(", "for ", "print("],
        },
        "web-scraping": {
            "framing": (
                "A scrape accumulates results into a shared list, and a helper that "
                "mutates the accumulator directly can corrupt the caller's copy of the "
                "same records."
            ),
            "application": (
                "Walk the example as a page parser returning records that get merged "
                "into an accumulator. The parser builds its own list rather than "
                "appending to the caller's list, and the merge step extends an "
                "independent accumulator, so the caller's earlier records survive intact. "
                "The trap that this topic is really about is subtler: a deduplication "
                "step that sorts the caller's list in place, meaning to produce a report, "
                "changes the caller's data order permanently. Sorting returns a new list, "
                "which is why it is the safe choice for a report, and the contrast with "
                "sort in place is the exact shape of the whole topic: some operations "
                "return a new object and some change the shared one, and knowing which is "
                "which is what prevents a report step from corrupting the dataset it "
                "reports on."
            ),
            "example_hint": "build fresh lists per page and sort a copy for the report",
            "assessment_angle": "which operations return new objects and which change shared ones",
            "day": 7,
            "title": "Report from a Sorted Copy, Never Reorder the Caller's Data",
            "code": """accumulated = [{"name": "Kettle"}, {"name": "Mug"}, {"name": "Bowl"}]


def parse_page(items):
    records = []                     # fresh list, not the caller's
    for item in items:
        records.append({"name": item})
    return records


accumulated.extend(parse_page(["Plate", "Cup"]))
print("accumulated:", [r["name"] for r in accumulated])

report = sorted(accumulated, key=lambda r: r["name"])
print("report order:", [r["name"] for r in report])
print("unchanged:", [r["name"] for r in accumulated])

accumulated.sort(key=lambda r: r["name"])
print("after in-place sort:", [r["name"] for r in accumulated])
""",
            "questions": [
                "Why does parse_page build a new list rather than appending to the accumulator it was given?",
                "The report is produced with sorted while the last step uses sort in place. What is the difference in what each leaves behind?",
                "What would a caller observe if the reporting step had used the in-place sort instead?",
            ],
            "answers": [
                "Because the parser is a helper whose only job is to produce records, so building its own list keeps it from changing a structure the caller owns and still holds.",
                "sorted returns a new ordered list and leaves the original as it was, while sort changes the one list in place and returns nothing.",
                "Its own accumulated records would be permanently reordered after the call, with no error raised, so the dataset would silently differ from what the caller assembled.",
            ],
            "homework": (
                "Write accumulator_safety.py with an accumulated list of at least six record "
                "dictionaries and a parse_page function that builds and returns a fresh list rather "
                "than mutating an argument. Extend the accumulator with the function's result and "
                "print the names. Then build a report with sorted and print both the report order "
                "and the original order to show they differ, and finally call sort in place and "
                "print the list once more. Observable output: four name lists, the last one "
                "showing the original changed."
            ),
            "required_patterns": ["sorted(", ".sort(", ".append(", "for ", "print("],
        },
        "testing-qa": {
            "framing": (
                "A test that mutates shared input fixtures makes later tests depend on "
                "execution order, which is the hardest suite defect to diagnose."
            ),
            "application": (
                "Walk the example as two tests sharing one fixture. The first test copies "
                "the fixture before modifying it, so the second test still sees the "
                "original state and the suite is order-independent; the counter-example "
                "shows the same test mutating the shared fixture directly and the second "
                "test's expectation then depending on whether the first one ran. That is "
                "the whole reason fixtures in a test suite are copied or rebuilt: a suite "
                "is only trustworthy if each test's outcome depends on the test itself "
                "and not on what ran before it. The diagnostic is distinctive, too, "
                "because an order-dependent suite passes when run in one order and fails "
                "in another, and the fixture-sharing is the first thing to suspect. "
                "Choosing a shallow copy is correct when a test replaces whole fields "
                "rather than mutating inside them, which is a real and common case worth "
                "naming."
            ),
            "example_hint": "copy a shared fixture in each test so the suite is order-independent",
            "assessment_angle": "what fixture sharing does to a suite and how the failure appears",
            "day": 7,
            "title": "Copy the Fixture Per Test: Keep the Suite Order-Independent",
            "code": """import copy

FIXTURE = {"items": ["a", "b"], "limit": 2}


def test_add_copy():
    state = copy.deepcopy(FIXTURE)
    state["items"].append("c")
    return len(state["items"]) == FIXTURE["limit"] + 1


def test_fixture_intact():
    return len(FIXTURE["items"]) == FIXTURE["limit"]


print("test 1 passes:", test_add_copy())
print("test 2 passes:", test_fixture_intact())
print("fixture after tests:", FIXTURE)

FIXTURE["items"].append("c")          # the failure mode
print("test 2 after mutation:", test_fixture_intact())
""",
            "questions": [
                "Why does the first test copy the fixture instead of appending to it directly?",
                "What symptom does an order-dependent suite show, and what is the first cause to suspect?",
                "The final line mutates the shared fixture directly. What does the second test then report, and why does no error appear?",
            ],
            "answers": [
                "Because the test needs a modified state to make its assertion, and modifying the shared fixture would leave the next test seeing a state it did not set up.",
                "It passes in one execution order and fails in another, and the first cause to suspect is a fixture shared between tests without a copy.",
                "It reports false, because the items list now holds three entries while the limit is two, and no error appears because the lengths simply disagree rather than any type or lookup failing.",
            ],
            "homework": (
                "Write fixture_isolation.py with a module-level fixture dictionary containing a "
                "list and a numeric limit. Write one test that deep-copies the fixture, appends to "
                "the copy's list and asserts on its length, and a second that asserts the fixture "
                "is still at its original length. Print both results and the fixture, then "
                "deliberately mutate the shared fixture and print the second test's result again. "
                "Observable output: four lines, the last one showing the second test failing."
            ),
            "required_patterns": ["copy.deepcopy", "len(", "==", "for ", "print("],
        },
        "devops-scripting": {
            "framing": (
                "A script that loads a baseline inventory and then modifies it per "
                "environment needs a copy per environment, or every environment sees the "
                "first one's edits."
            ),
            "application": (
                "Walk the example as a baseline config being specialised for each "
                "environment. Each environment takes a deep copy of the baseline before "
                "its overrides are applied, so the baseline stays reusable for the next "
                "environment and each environment's file is written from an independent "
                "structure. The bug this prevents is distinctive: the second "
                "environment's output would contain the first environment's overrides, "
                "and only the last environment written would look right. The depth "
                "choice is a real decision here, because a baseline with nested lists of "
                "hosts needs a deep copy while a flat baseline of scalar settings needs "
                "only a shallow one, and the deep copy is not free when the inventory is "
                "large. The way to choose is to look at which level the overrides touch, "
                "and copy exactly that level, which is the rule that keeps a config "
                "generator correct without making it slow."
            ),
            "example_hint": "deep-copy a baseline per environment before applying overrides",
            "assessment_angle": "what sharing a baseline costs and how to choose the copy depth",
            "day": 7,
            "title": "One Baseline, Independent Environments: Copy Before Overriding",
            "code": """import copy

baseline = {"name": "base", "hosts": ["web-1"], "settings": {"workers": 4}}
overrides = {
    "prod": {"name": "prod", "hosts": ["web-1", "web-2"], "settings": {"workers": 8}},
    "dev": {"name": "dev", "hosts": ["dev-1"]},
}

rendered = {}
for env, changes in overrides.items():
    config = copy.deepcopy(baseline)
    for key, value in changes.items():
        if isinstance(value, dict):
            config[key].update(value)
        else:
            config[key] = value
    rendered[env] = config

for env, config in rendered.items():
    print(env, config)

print("baseline intact:", baseline)
""",
            "questions": [
                "Why does each environment get its own copy of the baseline instead of applying overrides to the baseline itself?",
                "The override for prod contains a settings dictionary, handled with update rather than assignment. What does that avoid?",
                "What would the dev environment's output contain if the prod overrides had been applied to the shared baseline?",
            ],
            "answers": [
                "Because the baseline is reused for every environment, so applying overrides to it directly would carry each environment's changes into the next one rendered.",
                "It merges prod's settings into the baseline's settings rather than replacing the whole dictionary, so a key the override does not mention still survives.",
                "Prod's hosts and worker count, because those changes would already be in the baseline that dev copied from.",
            ],
            "homework": (
                "Write env_render.py with a baseline config containing a name, a hosts list and a "
                "nested settings dictionary, plus overrides for at least three environments where "
                "some override the hosts and some update only part of settings. Deep-copy the "
                "baseline for each environment, apply its overrides with update for dictionaries "
                "and assignment otherwise, and print each rendered config. Finally print the "
                "baseline to show it is unchanged. Observable output: one line per environment "
                "plus the intact baseline."
            ),
            "required_patterns": ["copy.deepcopy", "for ", "isinstance(", ".update(", "print("],
        },
        "algo-trading": {
            "framing": (
                "A strategy is backtested against many scenarios built from one base "
                "market, and each scenario has to be independent or the scenarios "
                "contaminate each other."
            ),
            "application": (
                "Walk the example as scenarios being derived from a shared base market. "
                "Each scenario deep-copies the base before its prices are perturbed, so "
                "the base remains identical for every scenario and each backtest runs "
                "against data that no other scenario touched. The cost question is real "
                "here, because a market of many bars is expensive to deep-copy many "
                "times, and the honest alternative is to build each scenario from the "
                "base by constructing a new list rather than copying and mutating, which "
                "is cheaper and just as independent. That is the deeper lesson of this "
                "topic: copying is the general remedy for sharing, but constructing fresh "
                "is often the better one when the derived object can be built directly. "
                "The failure mode that motivates both is that a scenario contaminated by "
                "a previous one produces a backtest result that looks valid and is not, "
                "which is precisely the kind of defect that survives a review because "
                "nothing raises."
            ),
            "example_hint": "derive independent scenarios from a shared base market and backtest each",
            "assessment_angle": "why scenarios must be independent and when constructing beats copying",
            "day": 7,
            "title": "Independent Scenarios: Copy the Base, or Build Anew",
            "code": """import copy

base = [100.0, 101.0, 102.0, 101.5, 103.0]


def perturb(prices, shift):
    scenario = copy.deepcopy(prices)
    return [round(p + shift, 2) for p in scenario]


def built(prices, shift):
    return [round(p + shift, 2) for p in prices]


scenarios = {
    "up": perturb(base, 1.0),
    "down": perturb(base, -1.0),
    "flat": built(base, 0.0),
}

for name, series in scenarios.items():
    print(f"{name:<5} {series}  peak {max(series)}")

print("base untouched:", base)
print("independent:", scenarios["up"][0] != scenarios["down"][0])
""",
            "questions": [
                "Why does each scenario get a copy of the base rather than perturbing the base itself?",
                "The flat scenario is built with a comprehension over base instead of copy plus mutation. Why is that equally independent, and what does it save?",
                "What would a backtest of a contaminated scenario report, and why is that hard to catch in review?",
            ],
            "answers": [
                "Because the base is reused for every scenario, so perturbing it directly would make each later scenario start from a market the earlier ones had already changed.",
                "Because the comprehension reads the base and constructs a brand-new list, so nothing is shared, and it avoids duplicating the whole series only to change every value of the copy.",
                "A plausible-looking result computed on data that was silently altered by another scenario, which is hard to catch because nothing raises and the numbers are internally consistent.",
            ],
            "homework": (
                "Write scenarios.py with a base market of at least ten prices and two functions: "
                "one that deep-copies the base and returns a shifted list, and one that builds the "
                "shifted list directly from the base with a comprehension. Build at least four "
                "scenarios using both functions, print each with its peak, then print the base to "
                "show it is unchanged and a boolean confirming two scenarios differ at their first "
                "price. Observable output: one line per scenario plus two closing lines."
            ),
            "required_patterns": ["copy.deepcopy", "for ", "max(", "round(", "print("],
        },
        "numerical-methods": {
            "framing": (
                "An iterative method updates a vector, and if the previous vector is "
                "needed for a convergence check it has to be kept on purpose, because an "
                "in-place update destroys it."
            ),
            "application": (
                "Walk the example as a vector being updated while its previous state is "
                "retained. The loop keeps a copy of the current vector before overwriting "
                "it, so the change between the two states can be measured, and without "
                "that copy the previous state would simply be gone. This is the sharpest "
                "form of the whole topic: a reference is free and a copy costs memory, so "
                "the question is always which object has to survive the next statement, "
                "and a value needed after an update must be copied before it. The "
                "alternative pattern, building the next vector as a new object instead of "
                "updating the old one, achieves the same thing by construction and is "
                "often clearer, since the previous state survives automatically. Choosing "
                "between copy-then-update and build-anew is a readability decision once "
                "both are known to be correct, and numerical code benefits from the "
                "second because it keeps each iteration's result immutable and "
                "inspectable."
            ),
            "example_hint": "copy the previous iterate before updating so the change can be measured",
            "assessment_angle": "why the previous state must be copied and what building anew avoids",
            "day": 7,
            "title": "Keep the Previous Iterate: Copy Before You Overwrite",
            "code": """import copy

state = [1.0, 1.0]
TOLERANCE = 1e-3

for step in range(5):
    previous = copy.deepcopy(state)
    state = [0.5 * (previous[0] + 1.0), 0.5 * (previous[1] + 2.0)]
    change = max(abs(a - b) for a, b in zip(state, previous))
    print(f"step {step + 1}: {state} change {change:.4f}")
    if change < TOLERANCE:
        break

print("final:", state)
print("previous survived:", previous)
""",
            "questions": [
                "Why is previous a copy of state rather than an assignment of it?",
                "The update builds a brand-new list for state instead of changing state in place. What does that make unnecessary, and why?",
                "Why would measuring convergence be impossible without the copy?",
            ],
            "answers": [
                "Because assignment would make both names point at one list, so the later update would change previous too and the previous state would be lost instead of retained.",
                "It makes the copy before the update unnecessary for that step, since the old list is never mutated, so a reference to it would have survived anyway.",
                "Because the change is the difference between the new and the old state, and the old state only still exists to subtract from if it was copied before it was replaced.",
            ],
            "homework": (
                "Write iterate_copy.py with an initial two-element vector and a tolerance. Run at "
                "most ten iterations, each time deep-copying the current vector into a previous "
                "name, then building a new vector from previous, and printing the step number, the "
                "new vector and the largest absolute change computed by zipping the two. Stop when "
                "the change falls below the tolerance and print the final vector and the surviving "
                "previous one. Observable output: one line per step plus two closing lines."
            ),
            "required_patterns": ["copy.deepcopy", "zip(", "max(", "abs(", "print("],
        },
    },
)
