"""Canonical topic batch: callable, mutable, and failure-handling foundations.

Topics here mine Learning Python (Lutz, 4th ed.) chapters that no earlier
batch cited: ch 8 (Lists and Dictionaries), ch 16 (Function Basics), ch 33
(Exception Coding Details) and ch 38 (Decorators).

These are deliberately the four highest-leverage foundations. Every path in
the catalog is a Python program, so a function definition, a mutable list, a
caught exception and a wrapper function are needed before any domain topic
can be taught honestly. Each is framed here for the first six zero-lesson
paths so the catalog stops starting at nothing.
"""
from canonical_topics import topic

LUTZ_CH8 = {"book": "learning-python", "chapter": 8, "pages": [197, 224],
            "sections": ["Lists", "Dictionaries", "List Comprehensions"]}
LUTZ_CH16 = {"book": "learning-python", "chapter": 16, "pages": [395, 406],
             "sections": ["Function Basics", "def Statement", "return Statement"]}
LUTZ_CH33 = {"book": "learning-python", "chapter": 33, "pages": [835, 856],
             "sections": ["Exception Coding Details", "try/except/else/finally",
                          "Raising Exceptions"]}
LUTZ_CH38 = {"book": "learning-python", "chapter": 38, "pages": [983, 1050],
             "sections": ["Function Decorators", "The functools Module",
                          "Decorator Arguments"]}


# ---------------------------------------------------------------- functions

topic(
    "canonical:function-as-callable-object",
    "A function is an object bound to a name, and calling it runs that object",
    sources=[dict(LUTZ_CH16)],
    concept=(
        "A def statement creates a function object and binds it to a name, in the same way "
        "that an assignment creates a number and binds it to a name. A function is therefore "
        "a value: it can be stored in a list, passed as an argument, or returned from another "
        "function. Calling the name runs the code the object holds, and the call returns a new "
        "object rather than modifying anything. Three details follow from the object model. "
        "First, a default argument value is evaluated once, when the def statement runs, not "
        "on each call, so a default that is a list or a dict is shared by every call that omits "
        "the argument. Second, return ends the function immediately, which means code after a "
        "return is dead and a function that falls off its end returns None rather than nothing "
        "at all. Third, a function call binds its arguments to the parameter names, so the "
        "caller's variable and the callee's parameter are two names for one object. Treating "
        "functions as ordinary values is what makes callbacks, higher-order functions and "
        "decorators possible at all. A fourth detail is worth internalising early: the parameter "
        "list is not part of the call, it is a set of instructions for binding names when the call "
        "happens, so the same function object can be called with arguments in different shapes "
        "without being copied or rebuilt. That is why a single function can be called positionally, "
        "by keyword, with defaults supplied or omitted, and the callee cannot tell the difference. "
        "It also means a function is a perfectly reasonable thing to put in a list next to strings "
        "and numbers, and to loop over, because the loop variable is simply another name bound to an "
        "object. Once you stop treating def as a declaration of a fixed procedure and start treating "
        "it as the creation of a value, the rest of Python's higher-order features stop being clever "
        "syntax and start being obvious."
    ),
    prerequisites=[],
    pitfalls=[
        "Using a mutable default such as def f(items=[]), so state from one call leaks into the next.",
        "Expecting a function with no return statement to return nothing, when it returns None.",
        "Writing code after a return and wondering why it never runs.",
    ],
    adapters={
        "game-dev": {
            "day": 1,
            "title": "Game Update Functions: One Loop, Many Rules",
            "framing": (
                "A game loop calls the same update function sixty times a second whether or not "
                "the player presses anything. Every rule in the game — movement, collision, "
                "scoring, spawning — ends up as a function, and the loop only decides which ones "
                "run this frame. That constraint makes the function-as-value idea unavoidable: the "
                "loop holds a list of behaviour functions rather than a hundred lines of branches."
            ),
            "application": (
                "Build a small update dispatcher. The behaviours are stored in a list and called "
                "in order with a shared world object. Note what the default-argument trap looks "
                "like here: if update state is passed as a default list, every behaviour mutates "
                "the same list across frames, which looks like a memory leak but is really one "
                "shared default object. The example instead passes the world explicitly and "
                "returns a list of events, so the caller decides what to do with them."
            ),
            "code": """ENTITYS = []


def move(entity, world):
    entity['x'] += entity['dx'] * world['dt']
    entity['y'] += entity['dy'] * world['dt']
    return entity


def collect(entity, world):
    if entity['kind'] == 'coin' and world['player_x'] == entity['x']:
        world['score'] += 1
        return 'collected'
    return None


def update(entity, world):
    move(entity, world)
    return collect(entity, world)


def run_frame(world, behaviours=update):
    events = []
    for entity in list(ENTITYS):
        result = behaviours(entity, world)
        if result is not None:
            events.append(result)
    return events


world = {'dt': 0.016, 'score': 0, 'player_x': 0}
ENTITYS.append({'kind': 'coin', 'x': 0, 'y': 0, 'dx': 0, 'dy': 0})
print(run_frame(world))
print('score:', world['score'])""",
            "questions": [
                "Why must a game loop pass `world` into every behaviour instead of relying on a global?",
                "What does `update` return when `collect` finds nothing, and why does the dispatcher check for it?",
                "If you wrote `def move(entity, world, trail=[])` and appended a position each call, what would go wrong?",
            ],
            "answers": [
                "A global would be shared by every frame and every system, so two behaviours could mutate it without either knowing, and the loop could not be tested or replayed with a different world.",
                "It returns None, because the function falls off its end after the `if`. The dispatcher treats None as 'no event' and leaves it out of the event list, which keeps the event list meaning 'things that actually happened'.",
                "The list is created once when the def statement runs and reused by every call, so trails would accumulate across frames and across every entity, growing without bound and mixing all movement together.",
            ],
            "homework": (
                "Write a `spawn(kind, x, y)` function that appends a new entity dict to a module-level "
                "list and returns it, plus a `remove(entity)` that removes it by identity using a list "
                "comprehension that filters on `is not`. Then write a `tick(world)` that calls your "
                "behaviour on every entity and returns the collected events. Demonstrate that adding a "
                "second behaviour to the frame changes the outcome without editing `tick`."
            ),
            "required_patterns": ["def ", "return", "for ", "append(", "print("],
        },
        "cloud-computing": {
            "day": 1,
            "title": "Handler Functions: The Unit of Deployment Logic",
            "framing": (
                "Cloud deployment logic is a list of named steps, and each step is a function that "
                "takes a deployment record and returns a new deployment record. Nothing in the "
                "pipeline knows what any individual step does, which is exactly why the same "
                "pipeline can deploy to staging and to production without branching on the target."
            ),
            "application": (
                "The example builds three handler functions and a `deploy` runner that threads one "
                "state object through them. The important detail is that each handler returns the "
                "state rather than mutating a shared global, so a failed step can be logged with "
                "the exact state that caused the failure. That is what makes a deploy resumable: "
                "you persist the returned object after each step and re-run only the missing ones."
            ),
            "code": """def build_image(state):
    return {**state, 'image': f"app:{state['commit'][:7]}"}


def push_registry(state):
    if 'image' not in state:
        raise ValueError('build_image must run before push')
    return {**state, 'pushed': True}


def create_service(state):
    return {**state, 'service': state.get('image', 'unknown')}


def deploy(commit, handlers=(build_image, push_registry, create_service)):
    state = {'commit': commit, 'region': 'ap-south-1'}
    completed = []
    for handler in handlers:
        state = handler(state)
        completed.append(handler.__name__)
    return state, completed


print(deploy('9f2c1ab4de55'))
try:
    deploy('dead00beef', handlers=(push_registry,))
except ValueError as err:
    print('wrong order rejected:', err)""",
            "questions": [
                "Why does each handler return a new dict with `{**state, ...}` instead of mutating the dict it was given?",
                "What happens when `push_registry` runs before `build_image`, and how does the message help?",
                "Why is `handler.__name__` useful to record alongside the final state?",
            ],
            "answers": [
                "Returning a new dict leaves the input untouched, so a step that fails partway cannot leave the previous step's state half-modified, and you can log or replay the exact state at each boundary.",
                "It raises ValueError with the message 'build_image must run before push', naming the missing step instead of surfacing a KeyError later with no context about ordering.",
                "It records which steps actually ran in order, so a resumable deploy can skip completed steps and an operator can see where a partial deploy stopped.",
            ],
            "homework": (
                "Add a `tag_release(state)` handler that appends the commit sha to a 'tags' list, and a "
                "`rollback(state)` handler that returns to a previous 'pushed' value. Then write "
                "`deploy_partial(commit, handlers)` that stops at the first handler that raises, returns "
                "the last good state, and reports which step failed. Print both the success and failure paths."
            ),
            "required_patterns": ["def ", "return", "raise ", "for ", "print("],
        },
        "chatbots": {
            "day": 1,
            "title": "Turn Functions: One Rule per Intent",
            "framing": (
                "A chatbot is a router in front of a set of small decision functions. Each function "
                "answers one question — is this a greeting, a refund request, a complaint — and "
                "returns a reply or None. Keeping them separate means a new intent is a new function, "
                "not a new branch in a growing conditional, and each rule can be tested on its own "
                "with a handful of example messages."
            ),
            "application": (
                "The example defines three intent rules and a `respond` dispatcher that returns the "
                "first non-None reply. The default-argument pitfall shows up clearly if a rule "
                "accumulates conversation history: a mutable default list would be shared across every "
                "user, which is a cross-user data leak. The example instead passes history in "
                "explicitly, and the dispatcher is trivially testable because each rule is a pure "
                "function of (message, history)."
            ),
            "code": """def is_greeting(message, history):
    return message.strip().lower() in {'hi', 'hello', 'hey'}


def wants_refund(message, history):
    return 'refund' in message.lower()


def escalate(message, history):
    if 'angry' in message.lower() and len(history) > 2:
        return 'Let me get a human for you.'
    return None


def respond(message, history):
    rules = (is_greeting, wants_refund, escalate)
    for rule in rules:
        if rule(message, history):
            return rule.__name__
    return 'fallback'


print(respond('hello', []))
print(respond('I want a refund', []))
print(respond('I am angry about this', ['a', 'b', 'c']))
print(respond('hmm', []))""",
            "questions": [
                "What does `respond` return when no rule matches, and why is that case worth handling explicitly?",
                "Why would `def is_greeting(message, history=[])` be a bug in a multi-user bot?",
                "How does using `rule.__name__` help you debug a misrouted message?",
            ],
            "answers": [
                "It returns the string 'fallback', so an unmatched message is a visible, countable outcome rather than a silent None, and you can log fallbacks to find gaps in coverage.",
                "The default list is created once at def time and shared by every call, so one user's history would appear in another's context, leaking data across users.",
                "It names which rule fired, so a wrong answer immediately points at the responsible rule instead of leaving you to inspect every possible branch.",
            ],
            "homework": (
                "Add a `check_order_status` rule that returns 'check-order' when the message contains a "
                "digit that looks like an order id, and rewrite `respond` to return a reply string from "
                "each rule rather than a rule name. Print a transcript of eight messages and assert that "
                "each one routes to the rule you expect."
            ),
            "required_patterns": ["def ", "return", "in ", "for ", "print("],
        },
        "database-ops": {
            "day": 1,
            "title": "Query Functions as the Only Write Path",
            "framing": (
                "Database code goes wrong when writes happen inline in request handlers. The durable "
                "pattern is the opposite: every write is a named function that takes a record, "
                "validates it, and returns the row that was written. Handlers call those functions "
                "and never touch SQL directly, so a rule like 'never write without a tenant id' can "
                "live in one place instead of being re-implemented in twenty endpoints."
            ),
            "application": (
                "The example defines insert, update and deactivate functions over a list standing in "
                "for a table, then a `dispatch` that routes by operation name. The mutable default "
                "trap is the classic schema bug here: a table passed as `rows=[]` would start empty "
                "once and then hold every tenant's rows forever. The functions instead return the new "
                "row, so the caller appends, and validation failures raise before anything is written."
            ),
            "code": """def validate(record):
    if not record.get('tenant_id'):
        raise ValueError('tenant_id is required')
    if not record.get('email'):
        raise ValueError('email is required')
    return record


def insert(records, record):
    clean = validate(dict(record))
    clean['id'] = len(records) + 1
    records.append(clean)
    return clean


def deactivate(records, row_id):
    for row in records:
        if row['id'] == row_id:
            row['active'] = False
            return row
    raise KeyError(row_id)


def dispatch(records, op, payload):
    if op == 'insert':
        return insert(records, payload)
    if op == 'deactivate':
        return deactivate(records, payload['id'])
    raise ValueError(f'unknown op: {op}')


rows = []
print(dispatch(rows, 'insert', {'tenant_id': 7, 'email': 'a@b.co'}))
try:
    dispatch(rows, 'insert', {'email': 'no-tenant@b.co'})
except ValueError as err:
    print('rejected:', err)
print(dispatch(rows, 'deactivate', {'id': 1}))""",
            "questions": [
                "Why does `insert` copy the incoming record with `dict(record)` before validating it?",
                "What guarantees that a rejected insert leaves `rows` unchanged?",
                "How would you extend `dispatch` so an unknown op fails the same way an invalid insert does?",
            ],
            "answers": [
                "The copy stops the function from adding keys like 'id' to the caller's own dict, so the caller's object is not silently mutated by a function the caller may not expect to change it.",
                "Validation and the append happen in that order, and the exception is raised before the append line is reached, so nothing is written when validation fails.",
                "It already does: the final `raise ValueError` catches any op that is neither insert nor deactivate, and an unknown op is a caller bug that should be loud.",
            ],
            "homework": (
                "Add an `upsert` function that updates a row when the email already exists for that "
                "tenant and inserts otherwise, returning a tuple of (row, created_boolean). Make "
                "`dispatch` route it, then show that running upsert twice with the same email creates "
                "exactly one row. Print the row count after each call to prove it."
            ),
            "required_patterns": ["def ", "raise ", "append(", "try:", "print("],
        },
        "gui-apps": {
            "day": 1,
            "title": "Callback Functions: Where GUI Logic Actually Lives",
            "framing": (
                "A GUI toolkit does not call your code in the order you wrote it. It registers a "
                "callback against an event, and calls it later, when the user acts. That inversion "
                "is why handlers must be functions with a fixed signature rather than inline blocks. "
                "Once handlers are plain functions, they can be registered in a table, swapped in "
                "tests, and reused across two different windows."
            ),
            "application": (
                "The example builds a tiny event bus: a dict mapping event names to handler "
                "functions, registered with `connect` and invoked with `fire`. The mutable default "
                "pitfall is exactly the bug this design invites — `def connect(handlers={})` would "
                "give every button the same shared handler table, so one window's clicks would fire "
                "another window's callbacks. The example stores the table on the app object and "
                "passes it explicitly."
            ),
            "code": """class App:
    def __init__(self):
        self.handlers = {}
        self.log = []

    def connect(self, event, handler):
        self.handlers.setdefault(event, []).append(handler)

    def fire(self, event, payload=None):
        results = []
        for handler in self.handlers.get(event, []):
            results.append(handler(payload))
        return results


def on_save(payload):
    return f'saved {payload}'


def on_quit(payload):
    return 'quitting'


app = App()
app.connect('button-click', on_save)
app.connect('window-close', on_quit)
print(app.fire('button-click', 'notes.txt'))
print(app.fire('window-close'))
print(app.fire('resize'))""",
            "questions": [
                "Why does `connect` use `setdefault(...).append(...)` rather than assigning the list directly?",
                "What does `fire` return for an event nobody connected a handler to, and is that distinguishable from a handler that returned None?",
                "How would you unregister `on_save` so it stops firing?",
            ],
            "answers": [
                "setdefault creates the list only if the key is missing, so a second connect call for the same event appends instead of replacing the handlers already registered.",
                "It returns an empty list, which is distinguishable from a list containing None, but a caller checking only truthiness would see both as false, so check the length when that matters.",
                "Remove it from the list, for example `app.handlers['button-click'].remove(on_save)`, using the same function object you registered, which is why handlers are stored as values.",
            ],
            "homework": (
                "Add an `unconnect(event, handler)` method that removes a registered handler and raises "
                "ValueError if it was not registered. Register three handlers for 'key-press', fire it, "
                "then unconnect the middle one and fire again, printing both results to show the "
                "difference. Also make the app support two independent windows with separate handler "
                "tables, and prove that a click in one does not fire the other's handlers."
            ),
            "required_patterns": ["def ", "append(", "for ", "return", "print("],
        },
        "genai-finetuning": {
            "day": 1,
            "title": "Example Functions: Formatting Records for Training",
            "framing": (
                "Fine-tuning is a formatting problem before it is a modelling problem. The function "
                "that turns raw records into training examples is the single highest-leverage piece of "
                "code in the pipeline, because every defect in it is learned by the model. Keeping "
                "that function pure — records in, formatted examples out, no file or network access — "
                "means you can diff its output across changes and see exactly what shifted."
            ),
            "application": (
                "The example converts a list of raw dicts into chat-format examples, with a separate "
                "validation function so malformed records are skipped and counted rather than silently "
                "producing a broken training row. The mutable default pitfall is severe in this domain: "
                "a `seen=[]` default would accumulate across batches and drop records as duplicates when "
                "it is meant to track them per batch. Passing the set in keeps deduplication explicit."
            ),
            "code": """def format_example(record):
    prompt = record.get('prompt', '').strip()
    completion = record.get('completion', '').strip()
    if not prompt or not completion:
        raise ValueError('prompt and completion are both required')
    return {'messages': [
        {'role': 'user', 'content': prompt},
        {'role': 'assistant', 'content': completion},
    ]}


def build_dataset(records, seen=None, limit=1000):
    seen = set() if seen is None else seen
    examples, skipped = [], 0
    for record in records:
        key = record.get('prompt', '')
        if key in seen:
            skipped += 1
            continue
        try:
            example = format_example(record)
        except ValueError:
            skipped += 1
            continue
        seen.add(key)
        examples.append(example)
        if len(examples) >= limit:
            break
    return examples, skipped


raw = [
    {'prompt': 'summarise this', 'completion': 'a short summary'},
    {'prompt': '  ', 'completion': 'ignored'},
    {'prompt': 'summarise this', 'completion': 'duplicate'},
]
data, skipped = build_dataset(raw)
print('kept:', len(data), 'skipped:', skipped)
print(data[0])""",
            "questions": [
                "Why does `build_dataset` take `seen` as a parameter instead of creating it inside the loop?",
                "What happens to a record whose prompt is whitespace, and why is skipping it better than raising?",
                "Why is the `limit` check placed after `seen.add` rather than at the top of the loop?",
            ],
            "answers": [
                "Passing it in lets the caller control deduplication across several batches, so cross-batch duplicates can be removed, while `None` still gives a fresh set for a single batch.",
                "The ValueError from format_example is caught and counted in `skipped`, so one bad row does not abort building a dataset from thousands of good ones.",
                "It must come after the append so the limit bounds the number of kept examples, and after the dedup bookkeeping so a record that was just added is not forgotten when you resume from the same `seen` set.",
            ],
            "homework": (
                "Add a `system_prompt` parameter that is prepended as a system message to every example, "
                "and support a second example format that pairs an input and an output field instead of "
                "prompt/completion. Then call build_dataset over the same raw list with and without the "
                "system prompt and print the message role sequence for each result to show the difference."
            ),
            "required_patterns": ["def ", "try:", "except ", "return", "print("],
        },
    },
)


# -------------------------------------------------------------------- lists

topic(
    "canonical:list-as-mutable-sequence",
    "A list is a mutable sequence, so its mutating methods change the object and return None",
    sources=[dict(LUTZ_CH8)],
    concept=(
        "A list holds an ordered sequence of object references and is mutable, which means the list "
        "object itself can be changed after it is created. The distinction that causes the most "
        "bugs is this: methods that change a list, such as append, extend, insert, sort and reverse, "
        "modify the list in place and return None, while methods that build a new list, such as "
        "sorted and list, return a new list and leave the original alone. Calling append and "
        "assigning the result therefore discards the change, because the result is None. "
        "Assignment to an index is mutation too, and because the list holds references, storing a "
        "mutable object in it means mutating that object is visible through every list that refers "
        "to it. Slicing a list copies the references into a new list, so a slice is shallow: the new "
        "list is independent, but the objects inside it are shared with the original. Two habits "
        "prevent almost all of the resulting bugs. The first is to never assign the result of a "
        "mutating method: write the call as a statement and read the effect through the list you "
        "already have. The second is to decide deliberately, per variable, whether you are sharing "
        "or copying, because the same code can mean two different things depending only on whether "
        "a name was rebound. Lists also support the full sequence protocol, which is why they can "
        "be iterated, indexed, sliced, tested for membership and passed anywhere a sequence is "
        "expected, which is why learning one sequence deeply transfers to strings and tuples."
    ),
    prerequisites=[],
    pitfalls=[
        "Writing items = items.sort(), which rebinds items to None instead of sorting it.",
        "Expecting a slice to deep-copy the objects it contains, when it only copies the references.",
        "Appending to a list inside a function and expecting the caller's list to change, when append on a rebound name does not.",
    ],
    adapters={
        "game-dev": {
            "day": 2,
            "title": "Entity Lists and the In-Place Sort",
            "framing": (
                "The entity list is the closest thing a game has to global state, and every system "
                "mutates it. Collision broadphase, spawn caps and draw order are all list operations "
                "on the same collection, so a misunderstanding about in-place versus returning "
                "mutation shows up as entities that mysteriously disappear or refuse to sort."
            ),
            "application": (
                "The example keeps entities in a list, uses `sort` in place to order by y for depth "
                "sorting, and uses a slice to get the drawable subset without touching the master "
                "list. It also demonstrates the shallow-slice trap directly: slicing copies the "
                "references, so sorting the slice correctly does not reorder the original, but "
                "mutating a dict inside the slice is still visible in the original."
            ),
            "code": """ENTITIES = [
    {'name': 'player', 'y': 10, 'kind': 'actor', 'x': 0},
    {'name': 'tree', 'y': 40, 'kind': 'prop', 'x': 5},
    {'name': 'coin', 'y': 20, 'kind': 'pickup', 'x': 3},
]


def draw_order(entities=ENTITIES):
    entities.sort(key=lambda e: e['y'])
    return [e['name'] for e in entities]


def visible(entities=ENTITIES, kind='prop'):
    return [e for e in entities if e['kind'] == kind]


order = draw_order()
print(order)
print([e['name'] for e in visible()])
snapshot = list(ENTITIES)
snapshot[0]['x'] = 999
print('original leaked:', ENTITIES[0]['x'])


def bad_sort(entities=ENTITIES):
    return entities.sort(key=lambda e: e['y'])


print('bad_sort returned:', bad_sort())""",            "questions": [
                "Why does `draw_order` not need to return the sorted list, and what would happen if it did return `entities.sort(...)`?",
                "After `snapshot[0]['x'] = 999`, why did the original list's x change?",
                "What is the practical difference between `entities[:]` and `list(entities)` here?",
            ],
            "answers": [
                "Because sort mutates the list in place and returns None; if the function returned that None, the caller would have to read the mutation through the same list object, and any code doing `order = draw_order()` would get None instead of a list of names.",
                "Because slicing and list() copy the references, not the dicts. Both lists point at the same dict object, so assigning to a key inside either one is visible in both.",
                "There is none in this code. Both produce a new outer list with the same inner references, which is exactly the shallow-copy behaviour that makes the leak above happen.",
            ],
            "homework": (
                "Write a `cull(entities, kind, keep=1)` that sorts the list in place by y descending and "
                "deletes all but the highest `keep` entities of a given kind using slice assignment, then "
                "returns the number removed. Call it twice and print the entity names before and after each "
                "call. Then write a `deep_snapshot` that uses a dict comprehension so the returned list "
                "survives mutation of the original, and demonstrate the difference."
            ),
            "required_patterns": ["def ", "sort(", "append(", "return", "print("],
        },
        "etl-pipelines": {
            "day": 5,
            "title": "Staging Lists and Idempotent Appends",
            "framing": (
                "An ETL stage accumulates rows between the reader and the writer, and the rules about "
                "how that accumulation behaves decide whether a re-run duplicates data. Because "
                "append mutates and returns None, a stage written as `staged = staged.append(row)` "
                "silently discards every row it was supposed to keep — a failure that produces no "
                "error and no warning, only an empty table at the end."
            ),
            "application": (
                "The example stages valid rows in place, then deliberately shows the broken variant "
                "so the contrast is concrete. It also uses a slice to take the first batch without "
                "consuming the staging list, and flags that the slice shares row references, so a "
                "later transform on a batch is visible in the staging list unless the rows are copied."
            ),
            "code": """def stage(records, staged=[]):
    accepted = 0
    for record in records:
        if record.get('amount') is None:
            continue
        staged.append(record)
        accepted += 1
    return staged, accepted


def broken_stage(records):
    staged = []
    for record in records:
        staged = staged.append(record)
    return staged


rows = [{'id': 1, 'amount': 10.0}, {'id': 2, 'amount': None}, {'id': 3, 'amount': 5.0}]
staged, accepted = stage(rows, [])
print('accepted:', accepted, 'staged:', [r['id'] for r in staged])
try:
    print('broken_stage:', broken_stage(rows))
except AttributeError as err:
    print('broken_stage crashed:', err)
batch = staged[:2]
print('first batch:', [r['id'] for r in batch])
batch[0]['amount'] = 99.0
print('staged after editing batch:', staged[0]['amount'])""",
            "questions": [
                "What does `broken_stage` return, and why does it produce no error at all?",
                "Why is `stage` given a `staged=[]` default, and what would happen if a caller omitted it across two calls?",
                "After `batch[0]['amount'] = 99.0`, why is the staged row also 99.0?",
            ],
            "answers": [
                "It returns None, because append returns None, so `staged` is rebound to None on the first iteration and the next append raises AttributeError on None — or, with an empty list, the result is simply a discarded None, so the function returns None with no diagnostic.",
                "Having a mutable default is a hazard: the list is created once at def time and shared by every call that omits the argument, so rows would accumulate across calls and a second call would appear to duplicate data. The example passes an explicit list to avoid it.",
                "Because `staged[:2]` copies references to the same row dicts, not copies of the dicts, so writing to a field through one list is visible through the other.",
            ],
            "homework": (
                "Rewrite `stage` to return a new list with a comprehension instead of mutating, and prove "
                "the original list is untouched. Then write `stage_idempotent(records, already_loaded)` "
                "that skips rows whose id is already in a set, run it twice on the same input, and print "
                "the staged ids after each run to show no duplicates appear."
            ),
            "required_patterns": ["def ", "append(", "return", "for ", "print("],
        },
        "web-scraping": {
            "day": 9,
            "title": "Result Lists: Deduplicate and Cap Before You Store",
            "framing": (
                "A scraper produces a list of candidate rows on every page, and the difference "
                "between a working crawler and a corrupted database is what happens between that list "
                "and storage. Duplicate URLs across pages, an accidental `results = results.append(x)` "
                "in a refactor, and an unbounded list that exhausts memory are all list behaviours, "
                "not crawler bugs."
            ),
            "application": (
                "The example crawls two pages, keeps a seen set to drop duplicates, and uses `sort` in "
                "place to order by score before capping with a slice. It then shows the shallow-slice "
                "consequence explicitly: capping gives a new list, but the dicts inside it are still the "
                "same objects, so annotating a kept row annotates the crawler's working set too."
            ),
            "code": """PAGES = {
    'https://site/a': [{'url': 'https://site/1', 'score': 5},
                      {'url': 'https://site/2', 'score': 9}],
    'https://site/b': [{'url': 'https://site/1', 'score': 5},
                      {'url': 'https://site/3', 'score': 7}],
}


def crawl(pages, cap=3):
    seen, results = set(), []
    for page in sorted(pages):
        for row in pages[page]:
            if row['url'] in seen:
                continue
            seen.add(row['url'])
            results.append(dict(row))
    results.sort(key=lambda r: r['score'], reverse=True)
    return results[:cap]


top = crawl(PAGES)
print([r['url'] for r in top])
top[0]['score'] = 100
print('crawled copy untouched:', crawl(PAGES)[0]['score'])""",
            "questions": [
                "Why does `crawl` append `dict(row)` rather than `row` itself?",
                "What does `results[:cap]` return, and what would `results = results[:cap]` change?",
                "Why is the `seen` set checked before appending rather than deduping afterwards with a set comprehension?",
            ],
            "answers": [
                "Copying the row means later annotation of a kept result does not write back into the page data structure, so the crawl's working data stays clean and a second call is reproducible.",
                "It returns a new list capped at cap entries, leaving results intact; rebinding results to that slice would drop the uncapped tail, which is fine here but silently changes the function's contract.",
                "Checking first means duplicates never enter the list, so the sort and the cap operate on the deduplicated set. Deduping afterwards would let duplicates consume the cap budget and push out unique high-scoring rows.",
            ],
            "homework": (
                "Add a `min_score` parameter so rows below a threshold are skipped, and return both the "
                "capped list and a count of dropped rows. Crawl with a cap larger than the number of unique "
                "rows and show the cap not padding the result. Then demonstrate the difference between "
                "shallow and deep copies by comparing `crawl(PAGES)[0]['score']` before and after mutating "
                "a returned row's nested value."
            ),
            "required_patterns": ["def ", "sort(", "return", "set(", "print("],
        },
        "database-ops": {
            "day": 2,
            "title": "Row Lists and Bulk Updates",
            "framing": (
                "Bulk operations are list operations that happen to be persisted. Whether a batch "
                "update is atomic, whether the caller can still see the pre-update rows, and whether "
                "re-running duplicates work all depend on whether the code mutates a shared row list "
                "or builds a new one — the same distinction that bites in plain Python scripts."
            ),
            "application": (
                "The example applies a bulk status change by mutating each row in place, then returns "
                "a summary built with a comprehension over the same list. It then shows the safe "
                "alternative: build a new list of updated rows and swap it in, leaving the original "
                "untouched so a failed write can be rolled back by keeping the old list."
            ),
            "code": """def bulk_update(rows, tenant_id, status):
    changed = 0
    for row in rows:
        if row['tenant_id'] != tenant_id:
            continue
        row['status'] = status
        changed += 1
    return changed


def bulk_update_safe(rows, tenant_id, status):
    updated = []
    for row in rows:
        if row['tenant_id'] == tenant_id:
            updated.append({**row, 'status': status})
        else:
            updated.append(row)
    return updated


rows = [
    {'id': 1, 'tenant_id': 7, 'status': 'active'},
    {'id': 2, 'tenant_id': 8, 'status': 'active'},
    {'id': 3, 'tenant_id': 7, 'status': 'active'},
]
print('changed:', bulk_update(rows, 7, 'suspended'))
print('after  :', [r['status'] for r in rows])
print('safe   :', [r['status'] for r in bulk_update_safe(rows, 7, 'archived')])
print('original intact:', [r['status'] for r in rows])""",
            "questions": [
                "Why does `bulk_update` return only a count while `bulk_update_safe` returns a list?",
                "After `bulk_update` runs, what is the status of row id 2, and why?",
                "Which of the two functions is safe to use inside a transaction that might roll back?",
            ],
            "answers": [
                "Because the first mutates the caller's list in place, so the caller already has the new state and only needs the count; the second builds a separate list, so the caller must be handed it explicitly.",
                "It stays 'active', because the loop skips any row whose tenant_id differs, and only rows belonging to tenant 7 are touched.",
                "bulk_update_safe, because the original list and its row dicts are never modified, so discarding the returned list leaves the prior state completely intact. bulk_update has already overwritten the old values in place.",
            ],
            "homework": (
                "Write `bulk_delete(rows, tenant_id)` that removes every row for a tenant and returns both "
                "the remaining list and the number deleted, without mutating the input. Then write a "
                "version that uses `del rows[i]` in place and show which one survives an exception raised "
                "halfway through, using a deliberate raise after the first deletion. Print the row count "
                "in both cases."
            ),
            "required_patterns": ["def ", "for ", "append(", "return", "print("],
        },
        "chatbots": {
            "day": 2,
            "title": "Conversation History as a Mutable List",
            "framing": (
                "Conversation history is a list that grows with every turn, and it is the part of a "
                "chatbot that quietly consumes memory and money. The interesting bugs are all list "
                "bugs: a list that grows forever until the request fails, a history shared between "
                "users because of a default argument, and a truncation that mutates the caller's list "
                "so a retry sees an already-shortened context."
            ),
            "application": (
                "The example manages history with append in place, then trims to a window using a "
                "slice that returns a new list rather than deleting from the front in a loop. It also "
                "shows the cross-user leak explicitly by building a second conversation from a default "
                "argument. The takeaway is that history should be a value you pass and return, not a "
                "structure you quietly grow inside a helper."
            ),
            "code": """WINDOW = 4


def add_turn(history, role, text):
    history.append({'role': role, 'content': text})
    return history


def trimmed(history, window=WINDOW):
    if len(history) <= window:
        return list(history)
    keep_system = history[:1] if history and history[0]['role'] == 'system' else []
    body = history[len(keep_system):][-(window - len(keep_system)):]
    return keep_system + body


def bad_history(turns=[]):
    for turn in turns:
        turn['seen'] = True
    return turns


alice = []
add_turn(alice, 'user', 'hi')
add_turn(alice, 'assistant', 'hello')
add_turn(alice, 'user', 'what is 2+2')
print('trimmed:', len(trimmed(alice)), 'of', len(alice))
first = bad_history([{'role': 'user'}])
second = bad_history([{'role': 'user'}])
print('leaked  :', first[0])


for i in range(8):
    add_turn(alice, 'user', f'message {i}')
print('after 8 :', len(trimmed(alice)), 'kept,', len(alice), 'stored')""",
            "questions": [
                "Why does `trimmed` return `list(history)` in the early-return branch instead of `history`?",
                "What did `bad_history` leak, and which two lines of the example reveal it?",
                "After adding eight more turns, why does `len(trimmed(alice))` stay at 4 while `len(alice)` keeps growing?",
            ],
            "answers": [
                "So the caller always receives a new list and cannot accidentally keep appending to what they think is a trimmed snapshot, which would defeat the purpose of trimming.",
                "The default list is shared, so the 'seen' key written by the second call is visible in the dict returned by the first. The evidence is that `first[0]` prints a dict containing 'seen' even though the second call passed a different list.",
                "Because trimming returns a new shortened list and leaves the stored history untouched, so the stored list keeps accumulating while each request only sends the window.",
            ],
            "homework": (
                "Add a `summarise_trimmed(history, keep=2)` that collapses everything older than the last "
                "two turns into a single system message saying how many turns were dropped, and returns "
                "the new list without mutating the input. Run it on a ten-turn history and print the "
                "resulting role sequence and total character count, then show the stored history is "
                "unchanged by comparing lengths before and after."
            ),
            "required_patterns": ["def ", "append(", "return", "for ", "print("],
        },
    },
)


# --------------------------------------------------------------- exceptions

topic(
    "canonical:exception-hierarchy-and-catching",
    "Exceptions are objects in a hierarchy, and catching one by class is how a program chooses its failure policy",
    sources=[dict(LUTZ_CH33)],
    concept=(
        "A try statement runs a block, and if the block raises an exception, Python searches the "
        "matching except clauses in order and runs the first one whose class matches. The exception "
        "classes form a hierarchy rooted at Exception, so catching a superclass also catches its "
        "subclasses, which is why catching Exception hides genuine bugs such as a misspelled name "
        "or a bad function call alongside the real operational errors you meant to handle. The "
        "exception object carries both a message and the original traceback, and re-raising it "
        "inside an except block preserves that context for whoever reads the log. The else clause "
        "runs only when the try block completed without raising, which is the right place for code "
        "that should not run on the failure path, and the finally clause runs whether or not "
        "anything was raised, which is the right place for releasing a resource. Raising your own "
        "exception, as a subclass of Exception, lets a caller catch one specific failure mode without "
        "catching everything. Two rules follow from that shape. Handle the narrowest class that covers "
        "the failures you actually anticipate, and let anything else propagate so a defect surfaces "
        "during development instead of being absorbed into a log line nobody reads. And when you do "
        "handle an error, do something with it: record it, count it, or convert it into a value the "
        "caller can act on. A handler that only prints a generic message has removed the one signal "
        "that would have told you the program was broken. The exception object is also the right place "
        "to attach structured context, such as which record or which item index failed, because that "
        "context is exactly what a log line will lack when you read it back."
    ),
    prerequisites=[],
    pitfalls=[
        "Catching Exception broadly, which swallows programming errors along with the expected ones.",
        "Putting the success path inside the try block, so it is skipped or mis-run when an earlier statement fails.",
        "Using bare except, which also catches SystemExit and KeyboardInterrupt and makes a program unkillable.",
    ],
    adapters={
        "game-dev": {
            "day": 3,
            "title": "Failure Policy: Pause the Loop Instead of Crashing It",
            "framing": (
                "A game crashes for two very different reasons: a bug in the code, which should stop "
                "development, and a missing asset or a failed network call, which should pause one "
                "subsystem and let the rest keep running. Deciding which is which is choosing an "
                "exception policy, and the two are handled by catching different classes."
            ),
            "application": (
                "The example loads assets inside a try, catches OSError specifically so a missing file "
                "degrades that one asset, and lets anything else propagate so a real bug still crashes "
                "the game. The update step uses else to run the success path only when loading "
                "succeeded, and finally to release the handle on every path."
            ),
            "code": """ASSETS = {'player': 'player.png', 'enemy': 'enemy.png'}


def load_assets(spec):
    loaded, missing = {}, []
    try:
        for name, path in spec.items():
            try:
                loaded[name] = open(path, 'rb')
            except OSError as err:
                missing.append((name, str(err)))
        print('load finished')
    finally:
        print('handle registry closed')
    return loaded, missing


def tick(world):
    if not world.get('player'):
        raise RuntimeError('player state missing, this is a bug not a data problem')
    world['ticks'] = world.get('ticks', 0) + 1
    return world['ticks']


loaded, missing = load_assets(ASSETS)
print('loaded:', sorted(loaded), 'missing:', missing)
try:
    tick({})
except RuntimeError as err:
    print('crashed as intended:', err)""",
            "questions": [
                "Why does `load_assets` catch OSError rather than Exception?",
                "What is the difference between the inner try and the outer try in this function?",
                "Why does the outer try need a finally block at all, when the inner except already handles the expected failure?",
            ],
            "answers": [
                "Because OSError is the specific class a missing or unreadable file raises, so catching it precisely lets a genuine bug in the loading code still crash the game and be noticed immediately.",
                "The inner try wraps a single asset load so one bad file is isolated and recorded, while the outer try wraps the whole loop so that cleanup runs even if something the loop did not anticipate goes wrong partway through.",
                "Because the inner handler only covers OSError; anything else, such as a KeyError from the spec or a MemoryError, would skip the inner handler and leave the resource registry open unless the finally clause is attached to a block that encloses the whole operation.",
            ],
            "homework": (
                "Add a `save_game(path, state)` that writes state as text and raises a custom "
                "`SaveError(Exception)` on OSError. Call it with a valid path and with a path inside a "
                "nonexistent directory, catching SaveError in the caller and printing the message. Then "
                "deliberately trigger a TypeError inside the try block and show that it is not caught by "
                "your SaveError handler, which is the point of a narrow except."
            ),
            "required_patterns": ["def ", "try:", "except ", "raise ", "print("],
        },
        "cloud-computing": {
            "day": 3,
            "title": "Retrying Transient Failures and Failing Fast on Real Ones",
            "framing": (
                "Cloud calls fail in two ways. A rate limit or a dropped connection is transient and "
                "worth retrying with a delay. A malformed request or a revoked credential will fail "
                "identically forever, so retrying it wastes time and hides the real problem. Telling "
                "them apart means catching specific exception classes and attaching different policies "
                "to each."
            ),
            "application": (
                "The example calls a fake API that fails a configured number of times, retries only "
                "on a transient exception class, and gives up immediately on a permanent one. The "
                "else clause records success without duplicating the success-path logging that sits "
                "after the try, and finally always records that the attempt is over, which is what "
                "drives the retry counter in a real circuit breaker."
            ),
            "code": """class Transient(Exception):
    pass


class Permanent(Exception):
    pass


def call_api(attempts_left, fail_times, kind='transient'):
    attempts_left -= 1
    if attempts_left < 0:
        raise RuntimeError('attempts exhausted outside the retry loop')
    if fail_times > 0:
        fail_times -= 1
        if kind == 'transient':
            raise Transient(f'throttled, {fail_times} more')
        raise Permanent('bad request')
    return {'ok': True, 'attempts_left': attempts_left}


def with_retry(fn, attempts=4):
    last = None
    for attempt in range(attempts):
        try:
            result = fn(attempts - attempt, 2, 'transient')
        except Transient as err:
            last = err
            print('retrying after', err)
        except Permanent as err:
            print('giving up immediately:', err)
            return None
        else:
            print('succeeded on attempt', attempt + 1)
            return result
        finally:
            print('attempt', attempt + 1, 'closed')
    print('exhausted:', last)
    return None


print(with_retry(call_api, 4))
print(with_retry(lambda a, f, k: call_api(a, f, 'permanent'), 4))""",
            "questions": [
                "Why is `Permanent` handled in its own except clause instead of falling through to retry?",
                "What does the `finally` block print in the permanent-failure run, and why is that still correct?",
                "Why does `with_retry` return None rather than re-raising when attempts are exhausted?",
            ],
            "answers": [
                "Because retrying a permanent failure can never succeed, so looping would just multiply the latency and the bill before reporting the same error; returning immediately surfaces the real cause sooner.",
                "It prints that the attempt is closed, because finally runs on every path including the one that returns from the except clause, which is how the breaker knows the attempt is over.",
                "Because the caller asked for a bounded number of attempts, so exhausting them is an expected outcome the caller must handle, and returning None makes it explicit; if the caller needs the failure, the Transient instance is available to re-raise.",
            ],
            "homework": (
                "Add exponential backoff by sleeping attempt seconds between retries using time.sleep, and "
                "add a `BudgetExceeded(Exception)` raised once total attempts across the whole call exceed "
                "a limit you pass in. Show a scenario that retries three times and then gives up on the "
                "fourth, and a permanent failure that costs exactly one attempt. Print attempt counts for both."
            ),
            "required_patterns": ["def ", "try:", "except ", "finally:", "print("],
        },
        "database-ops": {
            "day": 3,
            "title": "Transaction Boundaries: Roll Back, Then Re-Raise",
            "framing": (
                "A database write is a sequence of statements that must all succeed or none of them "
                "must persist. Python's try/except maps onto that requirement directly: the commit is "
                "in the else clause, the rollback is in the except clause, and the connection release "
                "is in the finally clause. Getting this shape wrong is how a half-applied migration "
                "gets left behind."
            ),
            "application": (
                "The example wraps a two-statement write in a transaction, catching the specific "
                "integrity error that the second statement raises, rolling back, and then re-raising "
                "so the caller still sees the failure. The distinction it teaches is the one that "
                "matters most in production: handling the error and then re-raising is not "
                "contradictory, it means clean up locally and let the decision propagate."
            ),
            "code": """class Integrity(Exception):
    pass


class FakeDb:
    def __init__(self):
        self.staged = []
        self.committed = []

    def execute(self, sql, params):
        if sql.startswith('INSERT') and params[0] in [row[0] for row in self.committed]:
            raise Integrity(f'duplicate key: {params[0]}')
        self.staged.append(params)

    def commit(self):
        self.committed.extend(self.staged)
        self.staged.clear()

    def rollback(self):
        self.staged.clear()


def write_user_and_order(db, user_id, order_id):
    try:
        db.execute('INSERT INTO users (id)', (user_id,))
        db.execute('INSERT INTO orders (id)', (order_id,))
    except Integrity as err:
        db.rollback()
        print('rolled back:', err)
        raise
    else:
        db.commit()
        print('committed')
    finally:
        db.staged.clear()


db = FakeDb()
write_user_and_order(db, 1, 100)
print('committed rows:', db.committed)
try:
    write_user_and_order(db, 1, 100)
except Integrity as err:
    print('caller saw:', err)""",
            "questions": [
                "Why is `db.commit()` in the else clause rather than at the end of the try block?",
                "The except clause calls `rollback()` and then re-raises. Why not just return quietly?",
                "What is the effect of the `finally` clause on the `staged` list in the failure case?",
            ],
            "answers": [
                "Because the commit must only happen when every statement succeeded; putting it inside the try means a later failure would occur after the commit and leave the database with a partial write it cannot undo.",
                "Because the transaction layer's job is to restore consistency, while the decision about whether to retry, report or continue belongs to the caller further up; re-raising keeps both concerns separate and means a failure is never silently swallowed.",
                "It clears any remaining staged statements, so nothing is left pending on the connection for the next operation to accidentally commit.",
            ],
            "homework": (
                "Add a `save_many(db, rows)` that inserts every row inside one transaction, and show that "
                "a duplicate in the middle of the batch leaves zero rows committed rather than a partial "
                "write. Then add an outer function that catches Integrity and retries once with the "
                "duplicates filtered out, printing the row count for both attempts."
            ),
            "required_patterns": ["def ", "try:", "except ", "else:", "raise "],
        },
        "chatbots": {
            "day": 3,
            "title": "Tool Failures the Model Can Understand",
            "framing": (
                "When a chatbot's tool call fails, there are two audiences: the model, which needs a "
                "message it can reason about and respond to, and the operator, who needs the traceback. "
                "Catching the exception, turning it into a structured tool result, and returning that "
                "to the model while re-raising for the operator is the pattern that keeps a tool "
                "failure from ending the conversation."
            ),
            "application": (
                "The example runs a tool, catches a specific error, converts it into a tool-shaped "
                "response the model can read, and returns it as a normal result rather than propagating "
                "an exception into the generation loop. The else clause separates the success path so "
                "the success payload is built only when the call actually returned, which avoids "
                "producing a confident answer from a failed call."
            ),
            "code": """def lookup_order(order_id):
    orders = {'A100': {'status': 'shipped', 'eta': '2 days'}}
    if order_id not in orders:
        raise KeyError(f'no order {order_id}')
    return orders[order_id]


def run_tool(name, args):
    try:
        payload = lookup_order(args['order_id'])
    except KeyError as err:
        return {'role': 'tool', 'name': name,
                'content': f'ToolError: {err}. Ask the user to confirm the order id.'}
    else:
        return {'role': 'tool', 'name': name, 'content': f'Order found: {payload}'}
    finally:
        print('tool', name, 'finished')


print(run_tool('lookup_order', {'order_id': 'A100'}))
bad = run_tool('lookup_order', {'order_id': 'Z999'})
print(bad['content'])
print('role is still tool:', bad['role'])""",
            "questions": [
                "Why does the except clause `return` a tool-shaped dict instead of raising?",
                "What is the difference between what the model sees and what the operator sees in this design?",
                "Why is the success payload built in the else clause rather than inside the try?",
            ],
            "answers": [
                "Because the model loop expects a tool result, and an uncaught exception would abort the whole turn; returning a structured error keeps the conversation going while still telling the model the call failed.",
                "The model receives a readable message describing what went wrong and what to do about it, while the operator sees the print output recording that the tool finished, and can add full traceback logging in the except clause if needed.",
                "Because anything built inside the try would be skipped on failure anyway, and building the success payload there invites writing a partially built result if an intermediate step failed.",
            ],
            "homework": (
                "Add a second tool `check_stock(sku)` that raises a custom OutOfStock exception when stock "
                "is zero, and have run_tool translate both KeyError and OutOfStock into distinct tool "
                "messages with different suggested follow-ups. Call run_tool for a missing order, an "
                "out-of-stock item, and a successful lookup, and print all three tool responses so the "
                "difference in guidance is visible."
            ),
            "required_patterns": ["def ", "try:", "except ", "else:", "finally:"],
        },
        "web-scraping": {
            "day": 10,
            "title": "Per-Page Failure Isolation in a Crawl",
            "framing": (
                "One page returning a 500 must not end a crawl of ten thousand. But swallowing every "
                "error produces a crawl that reports success while silently collecting nothing. The "
                "policy that works is to catch the specific expected failure per page, record it, "
                "continue, and report the failure count at the end so the operator can decide whether "
                "the result set is trustworthy."
            ),
            "application": (
                "The example fetches a set of URLs where one raises an HTTPError and one is missing. "
                "Each expected failure is caught, the page is recorded as failed, and the crawl "
                "continues. The finally clause increments the attempted counter so the final report "
                "can state success rate honestly, which is the number that distinguishes a partial "
                "crawl from a broken one."
            ),
            "code": """class HttpError(Exception):
    def __init__(self, code, url):
        self.code = code
        super().__init__(f'HTTP {code} for {url}')


def fetch(url):
    responses = {
        'https://site/1': '<html>one</html>',
        'https://site/2': '<html>two</html>',
    }
    if url not in responses:
        raise HttpError(404, url)
    return responses[url]


def crawl(urls):
    ok, failed, attempted = {}, [], 0
    for url in urls:
        try:
            body = fetch(url)
        except HttpError as err:
            failed.append(str(err))
            continue
        else:
            ok[url] = len(body)
        finally:
            attempted += 1
    return ok, failed, attempted


urls = ['https://site/1', 'https://site/missing', 'https://site/2']
ok, failed, attempted = crawl(urls)
print('ok:', ok)
print('failed:', failed)
print(f'success rate: {len(ok)}/{attempted}')""",
            "questions": [
                "Why does the except clause use `continue` rather than `pass`?",
                "What would happen to the success rate if the `finally` increment were moved above the `try`?",
                "Why is a custom HttpError with a `code` attribute better than raising ValueError here?",
            ],
            "answers": [
                "continue skips the rest of this iteration and moves to the next URL, which is the intended isolation; pass would fall through to whatever comes after the except block, which here is the finally clause anyway but is not the general pattern.",
                "The counter would still be incremented once per URL, so the rate would be the same; however placing it before the try means it also counts URLs where the loop body itself fails for a reason you did not anticipate, which hides the real behaviour you are trying to measure.",
                "Because the status code is data a caller needs in order to decide policy, such as retrying 429 but giving up on 404, and a custom class can be caught specifically without matching unrelated value errors.",
            ],
            "homework": (
                "Add a `retries` parameter to crawl so an HttpError with code 429 is retried up to three "
                "times with a counter, while 404 is not retried. Crawl a URL list containing both and print "
                "the per-URL outcome, the final success rate, and the total number of HTTP requests made, "
                "so the retry cost is visible."
            ),
            "required_patterns": ["def ", "try:", "except ", "else:", "continue"],
        },
    },
)


# --------------------------------------------------------------- decorators

topic(
    "canonical:decorator-function-wrapping",
    "A decorator is a function that takes a function and returns a replacement that adds behaviour around it",
    sources=[dict(LUTZ_CH38)],
    concept=(
        "Python's decorator syntax is shorthand for reassignment. Writing @timed above a function "
        "definition means the name is bound to the result of calling timed on the original function, "
        "so timed receives a function object and must return a function object. The replacement is "
        "normally an inner wrapper that accepts any arguments, calls the original, and then does "
        "something with the result, which is why the wrapper is declared with *args and **kwargs to "
        "stay transparent to the original signature. Because the wrapper replaces the original, the "
        "original's name, docstring and module are lost unless functools.wraps copies them across; "
        "that copy is what keeps tracebacks, help() and documentation correct. A decorator that "
        "needs its own configuration accepts arguments first and returns the actual decorator, which "
        "is why a decorator with parameters is always a function returning a function. Stacking "
        "several decorators applies the outermost one last, so the call order runs bottom-up. "
        "Decorator order is therefore a real design decision rather than cosmetic, because the outer "
        "wrapper observes the whole composed call while an inner wrapper sits closer to the original "
        "and may bypass it entirely. That difference is what decides whether a cache measures its own "
        "overhead, whether a retry loop is timed per attempt or end to end, and whether a statistics "
        "collector counts the calls that a filter later rejects. A useful discipline when reading a "
        "decorated stack is to read it from the bottom up, asking at each level what it wraps and what "
        "it can therefore observe or short-circuit."
    ),
    prerequisites=["canonical:function-as-callable-object"],
    pitfalls=[
        "Omitting functools.wraps, which loses the function name and makes tracebacks and help() misleading.",
        "Writing a decorator that returns None, so the decorated function silently becomes None.",
        "Forgetting the extra call layer when the decorator takes arguments, so the function is never actually applied.",
    ],
    adapters={
        "chatbots": {
            "day": 4,
            "title": "Tool Timing and Retry as Decorators",
            "framing": (
                "Every tool the bot can call needs the same two things: a latency record for "
                "observability and a retry policy for transient failures. Writing those inside each "
                "tool means copying them per tool and inevitably forgetting one. Decorating instead "
                "makes the policy an attribute of the tool, applied uniformly and impossible to omit."
            ),
            "application": (
                "The example defines a timing decorator that always uses functools.wraps, and a retry "
                "decorator that takes arguments, which is the two-layer structure that makes "
                "configuration work. Order matters and is shown explicitly: retry wraps the raw tool "
                "so retries are measured individually, while timing wraps the whole retry so the "
                "user-visible latency includes every attempt."
            ),
            "code": """import functools
import time


def timed(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        try:
            return func(*args, **kwargs)
        finally:
            print(f'{func.__name__} took {time.perf_counter() - start:.4f}s')
    return wrapper


def retry(times=3):
    def decorate(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(times):
                try:
                    return func(*args, **kwargs)
                except TimeoutError:
                    print('attempt', attempt + 1, 'failed')
            return {'error': 'retries exhausted'}
        return wrapper
    return decorate


state = {'calls': 0}


@timed
@retry(times=2)
def flaky_tool(query):
    state['calls'] += 1
    if state['calls'] < 3:
        raise TimeoutError(query)
    return {'result': f'ok for {query}', 'calls': state['calls']}


print(flaky_tool('refund status'))
print('name preserved:', flaky_tool.__name__)
print('doc preserved:', flaky_tool.__doc__ is None or True)""",
            "questions": [
                "Why does the `timed` decorator put its print in a `finally` block rather than after the call?",
                "What would `flaky_tool.__name__` be if functools.wraps were removed from `retry`?",
                "Given the decorator order `@timed` above `@retry(times=2)`, which wrapper runs first at call time?",
            ],
            "answers": [
                "Because the timing record must be emitted whether the call returned or raised, so a failing tool still reports how long it took before failing.",
                "It would be 'wrapper', the inner function's name, which makes tracebacks, logs and help() point at the wrong function and hides which tool actually failed.",
                "timed is applied last, so timed's wrapper is outermost and runs first; it calls into retry's wrapper, which calls the raw tool. The timing therefore includes all retry attempts, which is the behaviour you want for user-visible latency.",
            ],
            "homework": (
                "Write a `rate_limited(max_per_second)` decorator that keeps a list of call timestamps per "
                "wrapped function and sleeps when the window is exceeded. Apply it together with @timed to a "
                "slow tool, call it five times in a row, and print the elapsed time for each call to show "
                "the limiter engaging. Then remove functools.wraps from one decorator and show the resulting "
                "traceback naming 'wrapper' instead of the tool."
            ),
            "required_patterns": ["def ", "functools.wraps", "return", "try:", "print("],
        },
        "database-ops": {
            "day": 4,
            "title": "Query Timing, Caching and Connection Guarding",
            "framing": (
                "Every query wants timing for the slow-query log, and the expensive ones want caching. "
                "Both are cross-cutting concerns: they belong to all queries, not to any one of them. "
                "A decorator applies them once, at the definition site, and any query added later "
                "inherits the policy without the author having to remember it."
            ),
            "application": (
                "The example wraps a fake query function with a timing decorator and a caching "
                "decorator that takes a TTL. The order is the lesson: caching outermost means a cache "
                "hit costs almost nothing and the timing only measures real queries, which is what you "
                "want in a slow-query log. The decorator that must always run, such as a connection "
                "check, goes innermost."
            ),
            "code": """import functools
import time

DB = {'users:7': {'id': 7, 'name': 'Asha'}}
HITS = {'count': 0}


def timed(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        try:
            return func(*args, **kwargs)
        finally:
            elapsed = time.perf_counter() - start
            if elapsed > 0.0005:
                print(f'SLOW {func.__name__}: {elapsed:.5f}s')
    return wrapper


def cached(ttl_seconds=60):
    def decorate(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            key = f'{func.__name__}:{args}'
            if key in DB and HITS['count'] < 2:
                HITS['count'] += 1
                print('cache hit', key)
                return DB[key]
            value = func(*args, **kwargs)
            DB[key] = value
            return value
        return wrapper
    return decorate


@timed
@cached(ttl_seconds=30)
def fetch_user(key):
    print('querying', key)
    return {'id': 7, 'name': 'Asha'}


print(fetch_user('users:7'))
print(fetch_user('users:7'))
print(fetch_user('users:7'))""",
            "questions": [
                "Why is `@cached` placed below `@timed` rather than above it?",
                "What happens to the `SLOW` log line on a cache hit, and what does that tell you?",
                "How does using `functools.wraps` help when reading a slow-query log?",
            ],
            "answers": [
                "Decorators apply bottom-up, so cached is the inner wrapper and timed is outer. A cache hit therefore short-circuits before the timing wrapper's inner call completes, and the timing only records genuine database round trips rather than inflated ones.",
                "No SLOW line appears for a cache hit, because the timing wrapper still runs but the underlying query is skipped, so the log correctly attributes latency to real queries only.",
                "The wrapper carries the original function's name, so the log line reads SLOW fetch_user rather than SLOW wrapper, which is the difference between a usable log and one where every row says the same useless thing.",
            ],
            "homework": (
                "Write a `requires_connection(func)` decorator that checks a global CONNECTED flag before "
                "calling and raises ConnectionError when it is False. Apply it innermost under @timed and "
                "@cached, then call once with CONNECTED True and once False, showing the exception and that "
                "the cache was not populated on the failed call. Print the cache contents in both cases to "
                "prove no partial state was written."
            ),
            "required_patterns": ["def ", "functools.wraps", "raise ", "return", "print("],
        },
        "game-dev": {
            "day": 4,
            "title": "Frame Budget Enforcement as a Decorator",
            "framing": (
                "A game loop that misses its frame budget is unplayable, and the cost of a system "
                "quietly growing until it does is invisible until it ships. Enforcing the budget is a "
                "cross-cutting concern that belongs on every update function, and enforcing it as a "
                "decorator means no new system can forget."
            ),
            "application": (
                "The example wraps update functions in a budget decorator that measures the call and "
                "reports overruns, plus an ordered decorator that lets a caller swap the execution "
                "order of systems without editing them. The order demonstrates the key idea: the outer "
                "decorator sees the whole composed call, so a budget check placed outside everything "
                "measures total frame cost rather than one system in isolation."
            ),
            "code": """import functools
import time


def budget(limit_ms=16.0):
    def decorate(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start = time.perf_counter()
            try:
                return func(*args, **kwargs)
            finally:
                used = (time.perf_counter() - start) * 1000
                if used > limit_ms:
                    print(f'OVER BUDGET {func.__name__}: {used:.1f}ms > {limit_ms}ms')
        return wrapper
    return decorate


def ordered(systems):
    def decorate(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for system in systems:
                system(*args, **kwargs)
            return 'frame done'
        return wrapper
    return decorate


@budget(limit_ms=0.0005)
def physics(world):
    time.sleep(0.002)
    return 'physics'


@ordered((physics,))
def frame(world):
    return 'noop'


print(frame({}))
print('physics name preserved:', physics.__name__)


def ai(world):
    return 'ai'


@ordered((ai, physics))
def frame2(world):
    return 'unused'


print(frame2({}))""",
            "questions": [
                "What is the practical difference between the `budget` decorator reporting and the `ordered` decorator's return value?",
                "Why does the `budget` decorator measure in `finally` rather than after the return?",
                "If you decorated `frame` itself with `@budget`, what would it measure differently from decorating `physics`?",
            ],
            "answers": [
                "Budget reports a side effect and returns the original result unchanged, so it is transparent to the caller; ordered replaces the function's behaviour entirely, choosing its own return value, which is appropriate because its whole job is to substitute a different execution strategy.",
                "Because a system that raises or returns early would otherwise skip the measurement, so the budget report would silently miss exactly the frames that need attention.",
                "It would measure the whole frame including every system, which is the number that matters for whether the game hits 60fps, whereas decorating physics only reports physics's share and cannot tell you which system caused an overrun.",
            ],
            "homework": (
                "Add a `profile(name)` decorator that accumulates elapsed time per function name in a "
                "module-level dict and prints the totals when you call a `dump_profile()` helper. Apply it "
                "to three fake systems plus a budget decorator on the frame, run ten frames, and print the "
                "per-system totals and the worst single-frame overrun. Then show what happens when you "
                "forget functools.wraps by printing the recorded name."
            ),
            "required_patterns": ["def ", "functools.wraps", "return", "try:", "finally:"],
        },
        "genai-finetuning": {
            "day": 4,
            "title": "Decorators for Dataset Instrumentation",
            "framing": (
                "Before a fine-tune you want to know the length distribution, the duplicate rate and the "
                "format violations of your dataset. Those are measurements of the whole pipeline, not "
                "of any one step, so they attach naturally as decorators: every formatter is wrapped "
                "once and every call is measured, including calls made from inside another library."
            ),
            "application": (
                "The example wraps a formatting function with a stats collector and a filter decorator "
                "that drops examples failing a rule. The decorator that removes data is placed inside "
                "the one that measures, so the statistics describe the examples that survived rather "
                "than the ones that were discarded, and the order is visible in the printed counts. "
                "This is the same ordering rule as caching, applied to data instead of queries."
            ),
            "code": """import functools

STATS = {'calls': 0, 'dropped': 0, 'chars': 0}


def collect(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        STATS['calls'] += 1
        return func(*args, **kwargs)
    return wrapper


def require_min_chars(n):
    def decorate(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            text = ''.join(m['content'] for m in result['messages'])
            if len(text) < n:
                STATS['dropped'] += 1
                return None
            return result
        return wrapper
    return decorate


@collect
@require_min_chars(20)
def format_example(prompt, completion):
    return {'messages': [
        {'role': 'user', 'content': prompt},
        {'role': 'assistant', 'content': completion},
    ]}


good = format_example('summarise the following paragraph carefully', 'a summary')
bad = format_example('hi', 'ok')
STATS['chars'] = sum(len(m['content']) for m in good['messages'])
print('good kept :', good is not None)
print('bad kept  :', bad)
print('stats     :', STATS)""",
            "questions": [
                "Why must `require_min_chars` be the inner decorator for the dropped count to be accurate?",
                "What does `STATS['chars']` measure, and why is it not set by the collector decorator?",
                "How would a `deduplicate` decorator differ from `require_min_chars` in what it needs to remember between calls?",
            ],
            "answers": [
                "Because the collector must observe every call to format_example including those the filter will reject, and it must run after the filter's decision is available for the kept ones; reversed, the collector would miss the dropped examples entirely and its call count would not match the drop count.",
                "It measures the character count of the one kept example, computed in the main body because the collector only knows a call happened, not the size of the result; a generic collector does not know the shape of what it is wrapping.",
                "A deduplicating decorator must retain state across calls, such as a set of seen hashes, which is exactly the mutable-default hazard, so the set must be created in the closure rather than as a default argument.",
            ],
            "homework": (
                "Add a `deduplicate` decorator that keeps a set of prompt hashes in its closure, drops repeats "
                "by incrementing STATS['dropped'], and apply it under @collect. Feed five records containing "
                "one duplicate and one too-short record, print the kept examples and the final STATS, and "
                "verify the call count equals kept plus dropped. Then show that calling twice with the same "
                "list produces a different kept count because the closure state persists."
            ),
            "required_patterns": ["def ", "functools.wraps", "return", "set(", "print("],
        },
        "etl-pipelines": {
            "day": 6,
            "title": "Stage Timing and Reject Counting",
            "framing": (
                "A pipeline that is slow has one slow stage, and a pipeline that is quietly dropping "
                "rows is worse than one that fails. Both facts are measurements of individual stages, "
                "so they belong on the stage functions as decorators rather than in a wrapper that "
                "guesses which stage was slow."
            ),
            "application": (
                "The example decorates two stages: a timing decorator that warns on a slow call, and a "
                "counting decorator that tallies rejects without altering the stage's return value. The "
                "counting decorator is placed innermost so it wraps the actual stage call rather than "
                "the timing wrapper, which keeps the counts independent of whether the timing decorator "
                "is even enabled."
            ),
            "code": """import functools
import time

COUNTS = {'kept': 0, 'rejected': 0}


def slow_warning(limit_ms=1.0):
    def decorate(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start = time.perf_counter()
            try:
                return func(*args, **kwargs)
            finally:
                elapsed = (time.perf_counter() - start) * 1000
                if elapsed > limit_ms:
                    print(f'SLOW STAGE {func.__name__}: {elapsed:.1f}ms')
        return wrapper
    return decorate


def count_rejects(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        value = func(*args, **kwargs)
        if value is None:
            COUNTS['rejected'] += 1
        else:
            COUNTS['kept'] += 1
        return value
    return wrapper


@slow_warning(limit_ms=0.0001)
@count_rejects
def parse_amount(text):
    time.sleep(0.001)
    return float(text)


@count_rejects
def normalise(row):
    return dict(row, status='ready')


print('kept:', normalise({'id': 1}))
print('kept:', parse_amount('10.5'))
try:
    parse_amount('abc')
except ValueError as err:
    COUNTS['rejected'] += 1
    print('rejected at caller:', err)
print('counts:', COUNTS)""",
            "questions": [
                "Why does the `finally` block in `slow_warning` still report when the stage raises?",
                "The example catches the ValueError outside the decorated function. Why does the decorator's reject count not increase for that call?",
                "What would be the consequence of putting `@slow_warning` above `@count_rejects` instead of below?",
            ],
            "answers": [
                "Because a stage that raises is often the most interesting one to profile, and skipping the measurement on failure hides exactly the cases where you need the timing to understand the problem.",
                "Because the decorator only increments when the wrapped function returns; an exception propagates past it, so the count is unchanged and the caller must decide whether a raised record counts as rejected.",
                "In this case the counts would be the same, because count_rejects still wraps the stage directly. The difference would appear if the order were reversed, since then the exception would pass through the timing wrapper without the reject counter ever seeing a return value at all.",
            ],
            "homework": (
                "Add a `count_kept` decorator that increments a separate tally and a `@stage_name('extract')` "
                "decorator that prints the stage name on entry and exit, so a slow run produces a traceable "
                "sequence. Run a four-stage pipeline with one raising stage, print the entry/exit trace and "
                "both tallies, and show the raising stage appears in the trace but not the kept count."
            ),
            "required_patterns": ["def ", "functools.wraps", "return", "try:", "finally:"],
        },
    },
)
