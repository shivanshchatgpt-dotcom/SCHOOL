"""Chatbot capstone, days 165-179: ship one small bot, end to end.

Every example is stdlib-only, offline and deterministic (no network, no model
call, no clock, no files), so the applier executes it and gets the same output
every run. Each day is a working slice of one consistent toy assistant — a
study-room booking and support bot: a message model, an intent table, one tool,
a small memory, a guardrail and an assert-based evaluation.
"""

PHASE = (
    "Chatbot Capstone",
    "Design, build, evaluate and ship one small testable booking-and-support "
    "chatbot from scope contract to retrospective.",
    {
        165: dict(
            topic="Capstone: choose the scope",
            idea=(
                "A capstone fails on vague scope, and the fix is a scope contract you write before any code. "
                "One sentence names the user, the job and the boundary: a study-room booking assistant for "
                "students that books, checks hours and cancels. Then list what the bot refuses — refunds, "
                "medical and legal questions — because naming refusals first forces you to confront the traffic "
                "you cannot serve while changing course is still cheap. A bot that promises three intents and "
                "an honest fallback can be finished, tested and demonstrated; a bot that promises ten cannot be "
                "finished at all. Keep the contract as data, a dict, so later code can test membership instead "
                "of reasoning about prose. The point is not documentation for its own sake but a decision you "
                "can enforce: an out-of-scope intent should hit a refusal path, never a handler that half "
                "works. Today you write the contract as a dict, add an `in_scope` check, and print the goal "
                "next to one allowed and one refused intent. That single predicate is the line every later "
                "feature must respect, and it is the boundary that stops the project from growing without end. A scope you "
                "can reject requests against is worth more than one you can only describe, because it turns a "
                "sentence into a testable gate."
            ),
            code=(
                'scope = {\n'
                '    "goal": "book a study room",\n'
                '    "intents": ["book", "hours", "cancel", "help"],\n'
                '    "refuse": ["refund", "medical", "legal"],\n'
                '}\n'
                '\n'
                'def in_scope(intent):\n'
                '    return intent in scope["intents"]\n'
                '\n'
                'print("goal:", scope["goal"])\n'
                'for intent in ["book", "refund"]:\n'
                '    verdict = "ok" if in_scope(intent) else "refuse: out of scope"\n'
                '    print(f"  {intent:7} -> {verdict}")\n'
                '\n'
                'assert in_scope("book") and not in_scope("refund")\n'
                'assert set(scope["refuse"]) & {"refund"}\n'
                'print(len(scope["intents"]), "intents,", len(scope["refuse"]), "refusals")'
            ),
            variant_b='add a "help" intent as in-scope and a "payment" topic as refused, then reprint the verdicts',
            variant_c='store the boundary as a sentence and parse it, then explain why structured data is safer',
            mistakes=[
                "Promising every feature instead of choosing three intents and an honest fallback.",
                "Leaving refusals implicit, so out-of-scope requests reach a half-working handler.",
                "Keeping the scope in prose only, where no code can enforce it.",
            ],
            q1=(
                "Why list out-of-scope requests during scoping instead of after building?",
                "Naming refusals early exposes what the bot cannot serve, so the guardrail and fallback are designed in rather than bolted on.",
            ),
            homework=(
                "Write `define_scope(user, job, refused)` that returns a scope dict with the user, the job "
                "string, a list of served intents and the refused topics, plus an `in_scope(scope, intent)` "
                "helper. Print the goal and one allowed and one refused intent, and comment which line turns "
                "the refusal list into an enforced decision rather than a note."
            ),
            patterns=["def ", "in_scope", "print("],
            mapping=(
                "Product teams write a scope or charter before a bot sprint; the refused list becomes the "
                "escalation policy that production assistants hand to a human."
            ),
        ),
        166: dict(
            topic="Write the conversation spec",
            idea=(
                "A conversation spec is the sample script your bot must satisfy, written before the "
                "implementation. Each line pairs a concrete user utterance with the intent you expect it to "
                "trigger, and optionally the slot it should extract. This beats a feature list because a "
                "feature list is unfalsifiable — nobody can run 'supports booking' — while a spec can be "
                "executed and compared. Write the lines in the words real users type, including a greeting, a "
                "happy path, a follow-up and at least one nonsense turn, and mark the fallback explicitly. "
                "Keep it as data, a list of dicts, so the same structure later feeds your evaluation harness "
                "instead of being thrown away. The discipline is to commit to expected outcomes now rather "
                "than declaring success by whatever the bot happens to do, and when two engineers disagree "
                "about the right reply, the spec is the tie-breaker. Today you build a four-turn spec with "
                "intent labels, print each utterance next to its expectation, and assert that every case "
                "declares the two required fields. This small artefact turns opinions about the bot into a "
                "set of cases you can actually check. Because the spec is data, the same turns can later be replayed "
                "against a new implementation to see exactly which expectations changed."
            ),
            code=(
                'spec = [\n'
                '    {"user": "hi", "intent": "greeting"},\n'
                '    {"user": "book a room friday", "intent": "book", "slot": "friday"},\n'
                '    {"user": "what time do you open", "intent": "hours"},\n'
                '    {"user": "sing me a song", "intent": "fallback"},\n'
                ']\n'
                '\n'
                'for case in spec:\n'
                '    print(f"{case[\'user\']!r:26} -> {case[\'intent\']}")\n'
                '\n'
                'required = {"user", "intent"}\n'
                'assert all(required <= set(case) for case in spec)\n'
                'assert spec[-1]["intent"] == "fallback"\n'
                'print(len(spec), "turns specced, each with one expected intent")'
            ),
            variant_b='add a fifth case where the user corrects an earlier slot value and mark the follow-up intent',
            variant_c='move the spec into a JSON string and reload it, then explain what reloading proves',
            mistakes=[
                "Writing features to build instead of utterances with an expected outcome.",
                "Speccing only the happy path and forgetting a nonsense turn that must fall back.",
                "Storing cases as prose, so no harness can run them later.",
            ],
            q1=(
                "What does a conversation spec buy you that a feature list does not?",
                "It fixes the expected intent for concrete utterances, so every later implementation can be checked against the same examples.",
            ),
            homework=(
                "Write `make_spec(cases)` that stores a list of {user, intent} dicts and returns the number of "
                "cases whose intent is the fallback. Add at least four utterances covering greeting, booking, "
                "hours and nonsense, print each case next to its expectation, and comment which line makes the "
                "spec usable as a test rather than a wish list."
            ),
            patterns=["def ", "return", "print("],
            mapping=(
                "This is the golden-conversation file teams keep for chatbot regression testing; each labelled "
                "turn becomes a row in the eval set."
            ),
        ),
        167: dict(
            topic="Model messages and state",
            idea=(
                "Two things must be modelled: the transcript and the state. The transcript is what was said, in "
                "order, as role and content messages; the state is what the bot currently believes — the user's "
                "name, a chosen slot, a pending confirmation. Beginners merge the two and re-parse the entire "
                "conversation on every turn, which is slow and inconsistent. Keep them separate and give each "
                "an owner. Append turns to history, and update state through a pure function that takes the old "
                "state and one turn and returns a new state. Because state is a function of the turns so far, "
                "replaying the same turns rebuilds the same state, and that property is what later lets you "
                "save a session, resume it and evaluate the bot offline. The extra keyword arguments on a "
                "message let a tool result carry a name without inventing a second schema. Today you build a "
                "`message` helper, an `apply_turn` state update, run two turns and print the transcript. The "
                "assert checks that the derived state matches what the turns implied, which is exactly the "
                "property the rest of the capstone depends on for replay and testing. Nothing here is "
                "vendor-specific: a provider SDK's message format is only a serialisation of this list."
            ),
            code=(
                'def message(role, content, **extra):\n'
                '    m = {"role": role, "content": content}\n'
                '    m.update(extra)\n'
                '    return m\n'
                '\n'
                'def apply_turn(state, turn):\n'
                '    new = dict(state)\n'
                '    if "my name is" in turn["content"].lower():\n'
                '        new["name"] = turn["content"].split("is", 1)[1].strip().title()\n'
                '    return new\n'
                '\n'
                'history = [message("system", "You book study rooms.")]\n'
                'state = {"name": None, "slot": None}\n'
                'for text in ["Hi, my name is ada", "book a room"]:\n'
                '    history.append(message("user", text))\n'
                '    state = apply_turn(state, history[-1])\n'
                'history.append(message("assistant", f"Hello {state[\'name\']}, which day?"))\n'
                '\n'
                'for m in history:\n'
                '    print(f"{m[\'role\']:9}: {m[\'content\']}")\n'
                '\n'
                'assert state["name"] == "Ada"\n'
                'assert all({"role", "content"} <= set(m) for m in history)\n'
                'print("state is derived from the transcript")'
            ),
            variant_b='add a "topic" field to state set when the user names a subject, then print state after three turns',
            variant_c='rebuild the state by replaying the same turns into a fresh dict and assert both are equal',
            mistakes=[
                "Re-parsing the whole transcript every turn instead of maintaining explicit state.",
                "Letting a helper mutate the shared history list as a hidden side effect.",
                "Storing the same fact in a message and a state field, then letting them disagree.",
            ],
            q1=(
                "Why keep a transcript and a state dict instead of deriving everything from one?",
                "State answers the current question quickly while the transcript preserves what was said for context, debugging and replay.",
            ),
            homework=(
                "Write `apply_turn(state, turn)` returning a new state that captures the user's name when they "
                "say 'my name is', and `replay(turns)` folding `apply_turn` over a list from an empty state. "
                "Print the transcript and the final state, and comment which line keeps `replay` independent "
                "of how many times it is called."
            ),
            patterns=["def ", "return", "print("],
            mapping=(
                "Framework session stores keep exactly these two: a message log and a small state object per "
                "conversation, both persisted so a session can resume."
            ),
        ),
        168: dict(
            topic="Implement intents",
            idea=(
                "Intent routing is a table, not a pile of if-statements scattered through the reply code. Each "
                "entry pairs a name with a predicate, and the router returns the first name whose predicate "
                "matches, falling back to a catch-all. This is inspectable, testable and fast, and it covers "
                "most traffic in a narrow domain. The two real design questions are ordering and the fallback: "
                "put the most specific predicate first, because first match wins and a broad rule hides the "
                "narrow ones behind it, and always return something so the caller can log the decision. Keep "
                "matching and handling separate — the router decides what the user wants, handlers decide what "
                "to say — so you can later swap in a model classifier without rewriting a single response. "
                "Returning the intent name rather than the reply text also makes evaluation trivial: feed "
                "labelled utterances and compare the returned name against the label. Today you write three "
                "predicates plus a greeting, order them from specific to general, route a handful of messages "
                "and print each decision. The asserts pin both the ordering rule and the guaranteed fallback "
                "that keeps the bot from ever silently going quiet. Log the matched intent on every turn, because that "
                "routing decision is the single most useful line when a real user reports the wrong answer."
            ),
            code=(
                'def greeting(t):\n'
                '    return t in {"hi", "hello", "hey"}\n'
                '\n'
                'def wants_book(t):\n'
                '    return "book" in t or "reserve" in t\n'
                '\n'
                'def wants_hours(t):\n'
                '    return "open" in t or "hours" in t\n'
                '\n'
                'RULES = [("book", wants_book), ("hours", wants_hours), ("greeting", greeting)]\n'
                '\n'
                'def route(text):\n'
                '    t = text.lower().strip()\n'
                '    for name, matches in RULES:\n'
                '        if matches(t):\n'
                '            return name\n'
                '    return "fallback"\n'
                '\n'
                'for text in ["Hi", "Reserve a room", "When are you open?", "sing"]:\n'
                '    print(f"{text!r:24} -> {route(text)}")\n'
                '\n'
                'assert route("hi") == "greeting"\n'
                'assert route("reserve a room") == "book"\n'
                'assert route("dance") == "fallback"\n'
                'print("first match wins; fallback is last")'
            ),
            variant_b='add an "hours" style rule matching "when" and place it above the greeting rule, then retest',
            variant_c='return every matching intent name as a list and explain when first-match is the wrong policy',
            mistakes=[
                "Ordering rules from general to specific, so a broad predicate swallows every narrow one.",
                "Forgetting a fallback, so an unmatched utterance returns nothing at all.",
                "Putting reply text inside the matcher instead of keeping matching and handling apart.",
            ],
            q1=(
                "Why return the intent name from the router instead of the reply text?",
                "Separating what the user wants from what to say lets you test routing on its own and later swap the reply layer unchanged.",
            ),
            homework=(
                "Write `route(text, rules)` returning the first matching intent name or 'fallback'. Register "
                "three rules including a greeting, test five utterances covering each rule and a miss, print "
                "each decision, and comment which line guarantees the fallback is always returned."
            ),
            patterns=["def ", "for ", "return"],
            mapping=(
                "Dialogflow, Rasa and Lex all expose intents with example utterances; a classic bot is this "
                "table with a scoring layer on top."
            ),
        ),
        169: dict(
            topic="Add tools",
            idea=(
                "A tool call is a message, not a function call hidden inside a reply. The assistant emits a "
                "call naming the tool and its arguments; your dispatcher validates, executes and appends a "
                "result message. Three rules keep this safe. Validate arguments before calling, because a "
                "plausible value can still be invalid. Return errors as results instead of raising, so the next "
                "turn can see the failure and recover rather than killing the exchange. Keep each tool named "
                "after one action, because a tool doing several things is hard to retry and hard to authorise. "
                "In the capstone the tools are small and local: `availability` returns the slots for a day and "
                "`book` reserves one, raising if that slot is missing. The dispatcher catches the error and "
                "converts it into a tool message with an `error:` prefix, so the transcript stays honest and "
                "fully replayable. Today you wire the dispatcher, run a successful lookup and a failing "
                "booking, and print the resulting messages. The asserts confirm that failures arrive as "
                "messages in the conversation, never as uncaught exceptions that end the turn. That transcript-only discipline is what lets a reviewer "
                "replay the whole exchange and see precisely which arguments the model produced."
            ),
            code=(
                'def availability(day):\n'
                '    table = {"friday": ["9:00", "11:00"], "saturday": ["10:00"]}\n'
                '    return table.get(day.lower(), [])\n'
                '\n'
                'def book(day, slot):\n'
                '    if slot not in availability(day):\n'
                '        raise ValueError("slot unavailable")\n'
                '    return f"booked {day} {slot}"\n'
                '\n'
                'TOOLS = {"availability": availability, "book": book}\n'
                '\n'
                'def dispatch(name, **args):\n'
                '    if name not in TOOLS:\n'
                '        return {"role": "tool", "name": name, "content": "error: unknown tool"}\n'
                '    try:\n'
                '        return {"role": "tool", "name": name, "content": str(TOOLS[name](**args))}\n'
                '    except Exception as error:\n'
                '        return {"role": "tool", "name": name, "content": f"error: {error}"}\n'
                '\n'
                'for r in [dispatch("availability", day="friday"), dispatch("book", day="sunday", slot="9:00")]:\n'
                '    print(r["name"], "->", r["content"])\n'
                '\n'
                'assert dispatch("book", day="sunday", slot="9:00")["content"].startswith("error:")\n'
                'assert dispatch("cancel")["content"].startswith("error:")\n'
                'print("tool errors stay in the conversation")'
            ),
            variant_b='add a "cancel" tool that removes a booked slot and test it on a booking that exists',
            variant_c='return structured args in the error result so the next turn can correct just the bad field',
            mistakes=[
                "Letting a reply execute code directly instead of emitting a call the dispatcher validates.",
                "Raising on bad arguments, which kills the turn instead of letting the conversation recover.",
                "Building one giant tool that does several actions, making retries and auth ambiguous.",
            ],
            q1=(
                "Why does the dispatcher return errors as tool messages instead of raising them?",
                "The next turn can see the failure, explain or retry it, and the transcript stays replayable like any other conversation.",
            ),
            homework=(
                "Write `dispatch(tools, name, args)` that validates the tool name, calls it with the arguments, "
                "and returns a tool-result dict on success or a readable `error:` dict on failure. Register "
                "`availability` and `book`, make the booking fail once, print both results, and comment which "
                "line keeps the error inside the conversation."
            ),
            patterns=["def ", "try", "return"],
            mapping=(
                "OpenAI function calling, Anthropic tool use and LangChain tools all follow this call-and-result "
                "message pattern under different field names."
            ),
        ),
        170: dict(
            topic="Add memory",
            idea=(
                "Memory is state that persists across turns and, in production, across sessions. Ordinary state "
                "is rebuilt by replaying the transcript, but memory is something the bot should still know "
                "after the history is truncated. The honest capstone version is small: a dict holding the "
                "user's name and a stated preference, updated by a pure function from each user turn. The "
                "valuable part is reuse — a preference captured in one turn should influence a later one, so "
                "if the user says they prefer mornings, a subsequent 'book a room' fills the slot from memory "
                "instead of asking again. That reuse is the difference between a bot that listens and one that "
                "merely responds. Keep memory explicit and inspectable rather than buried inside reply logic, "
                "and make it a pure function of the turns so it stays reproducible and testable. Today you "
                "write `remember`, feed it three turns and print how the remembered fields change. The asserts "
                "show the name and the preferred slot surviving into the booking turn, the property that makes "
                "the assistant feel like it is paying attention to the conversation. In production this dict is replaced "
                "by a profile store, but the interface stays the same, which is why modelling it now pays off."
            ),
            code=(
                'def remember(memory, text):\n'
                '    new = dict(memory)\n'
                '    low = text.lower()\n'
                '    if "my name is" in low:\n'
                '        new["name"] = low.split("my name is", 1)[1].strip().title()\n'
                '    if "i prefer" in low:\n'
                '        new["preferred"] = low.split("i prefer", 1)[1].strip()\n'
                '    if "book" in low and new.get("preferred") and not new.get("slot"):\n'
                '        new["slot"] = new["preferred"]\n'
                '    return new\n'
                '\n'
                'memory = {"name": None, "preferred": None, "slot": None}\n'
                'for text in ["My name is ada", "I prefer mornings", "Book a room"]:\n'
                '    memory = remember(memory, text)\n'
                '    print("after", repr(text), "name:", memory["name"], "slot:", memory["slot"])\n'
                '\n'
                'assert memory["name"] == "Ada"\n'
                'assert memory["slot"] == "mornings"\n'
                'print("memory carries a preference into a later turn")'
            ),
            variant_b='add a "remembered_last" timestamp placeholder and explain why a real clock must stay outside the pure function',
            variant_c='clear the preferred field after it is used and argue for and against one-shot preferences',
            mistakes=[
                "Storing memory inside reply branches where it cannot be inspected or reset.",
                "Re-asking for a fact the user already gave, so the bot looks like it is not listening.",
                "Making memory mutable global state, so replaying turns no longer rebuilds it exactly.",
            ],
            q1=(
                "What makes memory different from ordinary state?",
                "Memory is state that must survive across turns and sessions, so it is persisted separately from the transcript you can replay.",
            ),
            homework=(
                "Write `remember(memory, text)` returning a new memory dict that captures a name and a stated "
                "preference, and reuse the preference to fill a booking slot on a later turn. Feed at least "
                "three turns, print the memory after each, and comment which line makes memory a pure function "
                "of the turns so it can be replayed."
            ),
            patterns=["def ", "return", "print("],
            mapping=(
                "Production assistants persist a profile or memory store per user; this dict is the toy version "
                "of the long-term memory layer."
            ),
        ),
        171: dict(
            topic="Add guardrails",
            idea=(
                "Guardrails are the checks that run before any handler, so a request the bot should never "
                "fulfil is stopped at the door. Two families matter. Content guardrails refuse sensitive "
                "topics — refunds, medical and legal questions — with a fixed, non-negotiable message that "
                "points to a human. Parameter guardrails validate the numbers and fields a request carries, "
                "rejecting a party size of twelve when the maximum is eight before the booking tool ever sees "
                "it. The design rule is that a guardrail returns either a refusal string or nothing, and the "
                "caller treats any non-None value as a hard stop, so guardrails compose by running one after "
                "another. Keep the refusal texts as constants rather than improvising them per turn, because "
                "consistency is what makes them defensible. Crucially, a guardrail must never silently swallow "
                "a request; it either answers with its refusal or lets the turn continue untouched. Today you "
                "write a `guard` function covering banned topics and a party-size bound, run one allowed and "
                "two refused cases, and print the verdicts. The asserts prove the refusals fire and that an "
                "in-range request passes straight through. Log every refusal with its reason, because a "
                "guardrail that fires silently is impossible to tune and impossible to defend."
            ),
            code=(
                'BANNED = ["refund", "medical", "legal"]\n'
                'MAX_PARTY = 8\n'
                '\n'
                'def guard(text, party=None):\n'
                '    low = text.lower()\n'
                '    for word in BANNED:\n'
                '        if word in low:\n'
                '            return f"I cannot help with {word}; please contact support."\n'
                '    if party is not None and not 1 <= party <= MAX_PARTY:\n'
                '        return f"Party size must be 1-{MAX_PARTY}."\n'
                '    return None\n'
                '\n'
                'cases = [("Can I get a refund?", None), ("book for 12", 12), ("book for 4", 4)]\n'
                'for text, party in cases:\n'
                '    blocked = guard(text, party)\n'
                '    print(f"{text!r:22} -> {blocked or \'allowed\'}")\n'
                '\n'
                'assert guard("legal advice") is not None\n'
                'assert guard("book for 4", 4) is None\n'
                'assert guard("book for 12", 12) is not None\n'
                'print("guardrails run before any intent handler")'
            ),
            variant_b='add a guardrail that rejects an empty message and test it alongside the party-size check',
            variant_c='chain two guardrail functions and explain why returning None means continue, not deny',
            mistakes=[
                "Validating after the handler already acted, so the bad request has already been served.",
                "Improvising a different refusal sentence each time instead of using one constant.",
                "Having a guardrail silently swallow the request instead of answering or continuing.",
            ],
            q1=(
                "Why run guardrails before any intent handler?",
                "A request the bot must refuse should be stopped before a handler executes or a tool fires, so the boundary is enforced, not hoped for.",
            ),
            homework=(
                "Write `guard(text, party=None)` that returns a refusal string for a banned topic or an "
                "out-of-range party size, and None when the request is allowed. Add a `run_guarded(text, party)` "
                "that stops on a refusal, test one allowed and two refused inputs, print the outcomes, and "
                "comment which line makes a guardrail a hard stop."
            ),
            patterns=["def ", "return", "None"],
            mapping=(
                "This is the moderation and policy layer every deployed assistant needs; refusals and escalations "
                "are written once and enforced before business logic."
            ),
        ),
        172: dict(
            topic="Write the eval suite",
            idea=(
                "An evaluation suite is a list of labelled cases plus a function that reports how many the bot "
                "gets right. Each case is an utterance and the intent you expect; the harness runs the router "
                "over every case, counts the hits and prints a row per case, so a failure is visible rather "
                "than buried in a summary. The discipline that separates a real suite from a demo is including "
                "cases you expect to fail. A suite where everything passes on the first run is usually too "
                "easy, or it is testing the examples you already tuned against. Recording a known miss "
                "statically — an assert that the pass count equals three of four — turns the gap into a "
                "documented decision instead of a surprise later. Keep the cases as data so you can add one "
                "line per bug you find, and re-run the whole thing after every change. Today you build four "
                "cases, a router over them and an `evaluate` function that prints each row and returns the "
                "counts. The final assert fixes the current score, so any future regression shows up "
                "immediately as a changed number rather than a quiet break. Keep the suite fast and offline so it can run "
                "on every edit; a test that needs a network is a test nobody runs."
            ),
            code=(
                'def route(text):\n'
                '    t = text.lower()\n'
                '    if "book" in t:\n'
                '        return "book"\n'
                '    if "open" in t:\n'
                '        return "hours"\n'
                '    return "fallback"\n'
                '\n'
                'CASES = [\n'
                '    ("book a room", "book"),\n'
                '    ("when do you open", "hours"),\n'
                '    ("sing", "fallback"),\n'
                '    ("reserve now", "book"),\n'
                ']\n'
                '\n'
                'def evaluate(cases, router):\n'
                '    passed = 0\n'
                '    for text, expected in cases:\n'
                '        got = router(text)\n'
                '        passed += got == expected\n'
                '        print(f"{text!r:20} expected={expected:9} got={got:9}")\n'
                '    return passed, len(cases)\n'
                '\n'
                'passed, total = evaluate(CASES, route)\n'
                'print(f"{passed}/{total} passed")\n'
                'assert passed == 3\n'
                'print("the eval names the gap instead of hiding it")'
            ),
            variant_b='fix the router so "reserve" maps to book, then update the assert to the new honest score',
            variant_c='add a per-intent breakdown of hits and misses and explain what the aggregate hides',
            mistakes=[
                "Writing only easy cases, so the suite passes and teaches you nothing.",
                "Hiding a known failure instead of asserting the exact current score.",
                "Keeping cases as one-off prints rather than data a harness can replay.",
            ],
            q1=(
                "Why does an eval suite need cases you expect to fail?",
                "A suite that never fails is too easy; including a known miss documents real gaps and makes the measured score trustworthy.",
            ),
            homework=(
                "Write `evaluate(cases, router)` that runs a router over labelled (utterance, intent) pairs, "
                "prints one row per case, and returns the passed and total counts. Include a case you expect "
                "to fail, assert the exact pass count, and comment which line turns a known miss into a "
                "documented decision."
            ),
            patterns=["def ", "return", "assert"],
            mapping=(
                "This is the offline eval harness real bot teams run in CI; labelled turns become the regression "
                "bar that must hold before a release."
            ),
        ),
        173: dict(
            topic="Stress the edge cases",
            idea=(
                "Edge cases are where hand-written bots break, and the first defence is normalisation. Before "
                "any matching, lowercase the text and collapse runs of whitespace, so 'BOOK A ROOM' and 'book "
                "a room' become the same input. Then bound the input: an empty or whitespace-only string should "
                "route to the fallback rather than crash a matcher, and an absurdly long string should be "
                "refused before it reaches a tool. The habit is to think in pairs — the normal case and its "
                "abuse — and to test the boundary explicitly rather than hoping. Empty string, all spaces, "
                "unexpected casing, punctuation and a very long message are the classic five, and each should "
                "produce a defined outcome, usually the fallback. Determinism helps here: because normalisation "
                "is a pure function, the same odd input always yields the same decision, so you can assert on "
                "it directly. Today you write `normalize`, guard the router against empty and over-long input, "
                "and run the five edge inputs, printing what each decides. The asserts pin the empty, "
                "whitespace and length boundaries, so a later change cannot quietly reintroduce a crash. This is the same normalisation a web server does "
                "before touching a request body, for the same reason: untrusted input is shaped before use."
            ),
            code=(
                'def normalize(text):\n'
                '    return " ".join(text.lower().split())\n'
                '\n'
                'def route(text):\n'
                '    t = normalize(text)\n'
                '    if not t or len(t) > 100:\n'
                '        return "fallback"\n'
                '    if "book" in t:\n'
                '        return "book"\n'
                '    return "fallback"\n'
                '\n'
                'edge = ["", "   ", "BOOK   A ROOM", "x" * 200, "book!"]\n'
                'for text in edge:\n'
                '    print(f"{text[:20]!r:24} -> {route(text)}")\n'
                '\n'
                'assert route("") == "fallback"\n'
                'assert route("   ") == "fallback"\n'
                'assert route("BOOK   A ROOM") == "book"\n'
                'assert route("x" * 200) == "fallback"\n'
                'print("case, whitespace and length are normalised first")'
            ),
            variant_b='add a punctuation strip so "book!" and "book?" route to book, then retest the five edges',
            variant_c='move the length bound into a named constant and explain what a guardrail without a name hides',
            mistakes=[
                "Matching raw text before lowercasing and collapsing whitespace.",
                "Letting an empty message reach a matcher and crash instead of falling back.",
                "Ignoring very long input, which can blow past a tool or a context window.",
            ],
            q1=(
                "What is the first thing to do with raw user text before matching?",
                "Normalise it — case, surrounding whitespace and length — so cosmetic differences cannot change the decision.",
            ),
            homework=(
                "Write `normalize(text)` that lowercases and collapses whitespace, and a `route(text)` that "
                "falls back on empty, whitespace-only and over-long input. Test the five classic edges — empty, "
                "spaces, odd casing, punctuation and a very long string — print each decision, and comment "
                "which line prevents the empty-string crash."
            ),
            patterns=["def ", "return", "print("],
            mapping=(
                "Production bots normalise and bound input at the gateway; the same five edges become the "
                "negative tests guarded in an eval suite."
            ),
        ),
        174: dict(
            topic="Polish the replies",
            idea=(
                "Reply polish is about consistency, not cleverness. Keep every canned response in one table "
                "keyed by intent, and route the fallback through the same lookup so an unknown intent always "
                "gets a defined, friendly sentence. Personalising is a small edit on top of a template, not a "
                "second copy of the wording: if a name is known and the intent is booking, prefix it, "
                "otherwise return the base template unchanged. That keeps the voice stable and the code short. "
                "The common failure is scattering reply strings through branches, so two paths drift apart and "
                "the bot starts to sound like two different products. A table also makes every reply "
                "reviewable at a glance and easy to edit without touching the logic that chooses it. Today you "
                "build a `TONES` table for booking, hours and fallback, a `reply` function that optionally "
                "personalises, and print the three outcomes for the same user. The asserts check that an "
                "unknown intent falls back to the shared sentence and that personalisation only happens when a "
                "name is present, so the polish never changes what the bot actually means. Finally, read the replies aloud once, because a "
                "sentence that looks fine in code can sound robotic or cold when a real person hears it."
            ),
            code=(
                'TONES = {\n'
                '    "book": "Great, let us find a slot.",\n'
                '    "hours": "We are open nine to five.",\n'
                '    "fallback": "I can help with booking or hours.",\n'
                '}\n'
                '\n'
                'def reply(intent, name=None):\n'
                '    base = TONES.get(intent, TONES["fallback"])\n'
                '    if name and intent == "book":\n'
                '        return f"{name}, {base[0].lower() + base[1:]}"\n'
                '    return base\n'
                '\n'
                'for intent in ["book", "hours", "sing"]:\n'
                '    print(f"{intent:9} -> {reply(intent, \'Ada\')}")\n'
                '\n'
                'assert reply("sing") == TONES["fallback"]\n'
                'assert reply("book", "Ada").startswith("Ada,")\n'
                'print("one fallback reply covers every unknown intent")'
            ),
            variant_b='add a "cancel" template and confirm an unknown intent still lands on the shared fallback',
            variant_c='move the templates into a JSON string, reload them, and explain what that buys for translation',
            mistakes=[
                "Scattering reply strings through branches, so the bot voice drifts between paths.",
                "Personalising by duplicating the whole sentence, which doubles the wording to maintain.",
                "Letting an unknown intent reach no template and returning an empty reply.",
            ],
            q1=(
                "Why keep reply templates in a table rather than inline in each branch?",
                "One table keeps the voice consistent, makes every reply reviewable at a glance, and lets you edit wording without touching routing logic.",
            ),
            homework=(
                "Write `reply(intent, name=None)` that looks a template up in a `TONES` table, falls back to "
                "the shared sentence for unknown intents, and personalises only when a name is present. Test "
                "booking, hours and an unknown intent, print each reply, and comment which line keeps every "
                "unknown intent on the same fallback sentence."
            ),
            patterns=["def ", "return", "TONES"],
            mapping=(
                "Locales and copy decks live beside the bot in production; a table like this is the seed of a "
                "translatable, brand-consistent response layer."
            ),
        ),
        175: dict(
            topic="Package the bot",
            idea=(
                "Packaging a bot means turning scattered functions into one describable bundle: a name, a "
                "version, the intents it serves, and the guardrails it enforces. A `build_bot` factory returns "
                "that bundle, and a `describe` function renders a one-line summary you can print in a demo or "
                "a log. The value is that everything downstream — the demo, the eval suite, the review "
                "checklist — reads from one source of truth instead of importing a handful of loose globals. "
                "Version strings matter the moment you ship, because 'the bot' is meaningless in a bug report "
                "without which build; even a simple major.minor count gives you that. Keep the bundle plain "
                "data, not a class with behaviour, so it stays easy to inspect, print and serialise. As the "
                "project grows you can add fields — a model name, a locale, a config path — without changing "
                "the shape of the code that reads them. Today you write the factory and the describer, print "
                "the summary and the intent and guardrail lists, and assert that the version is dotted and the "
                "fallback is present. This is the last structural step before the bot becomes something you "
                "can hand over rather than a folder of scripts. The bundle is also the seam where configuration enters, so "
                "a locale, a model name or a feature flag can be added without touching bot logic."
            ),
            code=(
                'def build_bot():\n'
                '    return {\n'
                '        "name": "roombot",\n'
                '        "version": "1.0",\n'
                '        "intents": ["book", "hours", "fallback"],\n'
                '        "guardrails": ["banned_topics", "max_party"],\n'
                '    }\n'
                '\n'
                'def describe(bot):\n'
                '    return f"{bot[\'name\']} v{bot[\'version\']} ({len(bot[\'intents\'])} intents)"\n'
                '\n'
                'bot = build_bot()\n'
                'print(describe(bot))\n'
                'print("intents:", ", ".join(bot["intents"]))\n'
                'print("guardrails:", ", ".join(bot["guardrails"]))\n'
                '\n'
                'assert bot["version"].count(".") == 1\n'
                'assert "fallback" in bot["intents"]\n'
                'assert bot["guardrails"]\n'
                'print("a bot is a named, versioned bundle")'
            ),
            variant_b='add a "locale" field and update describe to include it, then print the new summary',
            variant_c='return the bundle as a sorted tuple of pairs and explain which form is easier to diff',
            mistakes=[
                "Importing loose globals in every module instead of one described bundle.",
                "Shipping with no version, so a bug report cannot name the build.",
                "Giving the bundle behaviour, which makes it hard to inspect, print and serialise.",
            ],
            q1=(
                "What belongs in a packaged bot bundle besides the code?",
                "A name, a dotted version, the intents it serves and the guardrails it enforces — the facts downstream tools and bug reports need.",
            ),
            homework=(
                "Write `build_bot()` returning a dict with a name, a dotted version, a list of intents and a "
                "list of guardrails, and `describe(bot)` returning a one-line summary. Print the summary and "
                "the lists, and comment which line makes the version something a bug report can name."
            ),
            patterns=["def ", "return", "print("],
            mapping=(
                "A deployable assistant ships with a manifest: name, version, config and enabled policies — "
                "this bundle is that manifest in miniature."
            ),
        ),
        176: dict(
            topic="Demo the conversation",
            idea=(
                "A demo is a scripted conversation, chosen to show the shape of the bot in under a minute: a "
                "greeting, a happy path that triggers a tool, a question answered from policy, and a refusal "
                "that proves a guardrail works. Improvising live hides the failures and shows only the "
                "fortunate path; a fixed list of turns replays identically every time and makes the bot's "
                "behaviour something you can argue about with evidence. Write the turns as data, print both the "
                "user and the bot line for each, and finish by printing the resulting state so the audience "
                "sees what the bot remembered. The demo doubles as an acceptance test: because nothing touches "
                "a network or a clock, the same script runs in a terminal, in a test, and during a review. "
                "Choose the turns to include one of each interesting case rather than five of the same, and "
                "make sure the last turn leaves the bot with something to show — a booked slot, a remembered "
                "preference. Today you write a small `respond` loop over four turns and print the exchange and "
                "the final state. The asserts confirm the happy path booked and the refusal fired, the two "
                "moments a demo must contain. Aim to tell a small story too: greet, book, answer, refuse, so "
                "the audience understands what the bot is for and not only what it can do."
            ),
            code=(
                'def respond(text, state):\n'
                '    low = text.lower()\n'
                '    if "refund" in low:\n'
                '        return "I cannot help with refunds.", state\n'
                '    if "book" in low:\n'
                '        return "Booked for friday.", dict(state, slot="friday")\n'
                '    if "open" in low:\n'
                '        return "We are open nine to five.", state\n'
                '    return "I can book a room or share hours.", state\n'
                '\n'
                'state = {"slot": None}\n'
                'for text in ["Hi", "Book a room", "When open?", "refund please"]:\n'
                '    reply, state = respond(text, state)\n'
                '    print(f"user: {text}")\n'
                '    print(f"bot : {reply}")\n'
                '\n'
                'print("final state:", state)\n'
                'assert state["slot"] == "friday"\n'
                'assert "refunds" in respond("refund", {})[0]\n'
                'print("the demo covers a happy path and a refusal")'
            ),
            variant_b='add a turn that repeats an earlier request and show the bot answering consistently',
            variant_c='store the demo turns in a list of dicts and explain what changes when the script is data',
            mistakes=[
                "Improvising the demo live, which shows the lucky path and hides the failures.",
                "Showing five variants of the same intent instead of one of each interesting case.",
                "Ending on a turn that changes nothing, so the demo proves no behaviour at all.",
            ],
            q1=(
                "Why script the demo conversation instead of improvising it live?",
                "A fixed script replays identically, so the demo also acts as an acceptance test and the bot's behaviour is arguable with evidence.",
            ),
            homework=(
                "Write `chat_round(text, state)` returning a reply and a new state, and drive a four-turn demo "
                "including a booking, a policy question and a refusal. Print both sides of the exchange and the "
                "final state, and comment which line makes the whole demo replay identically every run."
            ),
            patterns=["def ", "return", "state"],
            mapping=(
                "Sales demos and acceptance tests are the same script at different audiences; a recorded golden "
                "conversation serves both."
            ),
        ),
        177: dict(
            topic="Build day: evaluation pass",
            idea=(
                "The evaluation pass is where the suite becomes a number you watch. Take every labelled case, "
                "run the classifier, count the hits, and report accuracy as a fraction and a percentage so "
                "progress is measurable across builds. Print a row per case with the expected and the actual "
                "label, because a single accuracy figure tells you something regressed but not what; the rows "
                "point straight at the utterance that drifted. Compare against the previous run rather than an "
                "absolute ideal — a bot at eight of ten that was at six is improving even though it is not "
                "perfect. The suite is only as honest as its cases, so keep the awkward ones in: the utterance "
                "that shares a keyword with the wrong intent is worth more than ten easy greetings. Store the "
                "score so the next build can compare against it, and treat a drop as a blocker rather than a "
                "curiosity. Today you assemble five labelled cases, a classifier, and a loop that prints each "
                "row and the accuracy, asserting a perfect score on this cleaned set. The point is the "
                "mechanism: after this, every change is followed by a number rather than an opinion. Save each run's score next to the commit, so "
                "the history of numbers itself becomes the record of the bot getting better over the build days."
            ),
            code=(
                'CASES = [\n'
                '    ("book", "book"),\n'
                '    ("book a room", "book"),\n'
                '    ("open", "hours"),\n'
                '    ("hours", "hours"),\n'
                '    ("sing", "fallback"),\n'
                ']\n'
                '\n'
                'def classify(text):\n'
                '    t = text.lower()\n'
                '    if "book" in t:\n'
                '        return "book"\n'
                '    if "open" in t or "hours" in t:\n'
                '        return "hours"\n'
                '    return "fallback"\n'
                '\n'
                'hits = 0\n'
                'for text, expected in CASES:\n'
                '    got = classify(text)\n'
                '    hits += got == expected\n'
                '    print(f"{text!r:14} {expected:9} {got:9} {\'ok\' if got == expected else \'FAIL\'}")\n'
                '\n'
                'accuracy = hits / len(CASES)\n'
                'print(f"accuracy {hits}/{len(CASES)} = {accuracy:.0%}")\n'
                'assert accuracy == 1.0\n'
                'print("evaluation is a number you watch, not a vibe")'
            ),
            variant_b='add a case that should fail and report accuracy honestly instead of asserting a perfect score',
            variant_c='track accuracy per intent and explain which single number was hiding a weak class',
            mistakes=[
                "Reporting only a total accuracy, so a broken intent hides behind easy cases.",
                "Deleting a failing case instead of fixing the bot or documenting the gap.",
                "Comparing against an ideal rather than the previous build, so progress is invisible.",
            ],
            q1=(
                "Why express an evaluation pass as accuracy over labelled cases?",
                "A single reproducible number lets you compare builds and catch a regression immediately, while per-case rows show exactly which utterance drifted.",
            ),
            homework=(
                "Write `evaluation_pass(cases, classify)` that prints a row per labelled case and returns "
                "accuracy as a fraction. Use at least five cases, assert a perfect score, and comment which "
                "line turns a regression into a changed number rather than a surprise."
            ),
            patterns=["def ", "return", "print("],
            mapping=(
                "This is the model-quality dashboard in production: labelled turns, a scored run, and a "
                "threshold that must hold before shipping."
            ),
        ),
        178: dict(
            topic="Build day: final review",
            idea=(
                "Final review is a checklist applied to the packaged bot, not a reread of the code. Each item "
                "is a predicate over the bundle: does it have a fallback, is there at least one guardrail, is "
                "it versioned, does it ship with evaluation cases. A checklist converts taste into a yes or no, "
                "so two reviewers agree and nothing is forgotten because it was boring. Keep the checks as a "
                "dict of small lambdas and print pass or fail for each, then assert that the shipped bot passes "
                "all of them. The beauty of writing the checklist before the review is that it doubles as the "
                "definition of done: you finish when the bundle satisfies every predicate, which is a clear "
                "target instead of a feeling. Add a rule each time something slips through — a bug that "
                "reached a user becomes a checklist item so it can never recur silently — and the list becomes "
                "a record of every lesson the project taught. Today you write four checks, run them over a "
                "complete bundle and over a deliberately empty one, and print the verdicts. The asserts prove "
                "that a real bot passes and that a hollow bundle is caught. Review is not the place for new features; if a "
                "check fails, you either fix the bot or consciously lower the bar and write down why."
            ),
            code=(
                'CHECKLIST = {\n'
                '    "fallback": lambda b: "fallback" in b["intents"],\n'
                '    "guardrail": lambda b: bool(b["guardrails"]),\n'
                '    "versioned": lambda b: bool(b["version"]),\n'
                '    "eval cases": lambda b: b["eval_cases"] > 0,\n'
                '}\n'
                '\n'
                'bot = {\n'
                '    "intents": ["book", "hours", "fallback"],\n'
                '    "guardrails": ["banned_topics"],\n'
                '    "version": "1.0",\n'
                '    "eval_cases": 5,\n'
                '}\n'
                '\n'
                'for name, check in CHECKLIST.items():\n'
                '    print(f"{name:11} {\'pass\' if check(bot) else \'FAIL\'}")\n'
                '\n'
                'assert all(check(bot) for check in CHECKLIST.values())\n'
                'hollow = {"intents": [], "guardrails": [], "version": "", "eval_cases": 0}\n'
                'assert not CHECKLIST["versioned"](hollow)\n'
                'print("review is a checklist, not a feeling")'
            ),
            variant_b='add a "has fallback reply" check and run the checklist over a bot missing one intent',
            variant_c='return the list of failing check names instead of printing, and explain which is easier to gate on',
            mistakes=[
                "Rereading code by eye instead of applying the same predicates every time.",
                "Treating review as taste, so two reviewers reach different verdicts.",
                "Forgetting to add a checklist item after a bug, so the same mistake recurs.",
            ],
            q1=(
                "Why use a checklist for final review instead of rereading the code?",
                "Predicates give the same yes-or-no answer to every reviewer, double as a definition of done, and never forget the boring checks.",
            ),
            homework=(
                "Write `review_bot(bot, checklist)` that applies a dict of predicate checks to a bot bundle and "
                "returns the list of failed names. Build four checks, run them over a complete bundle and an "
                "empty one, print the verdicts, and comment which line makes the checklist the definition of "
                "done."
            ),
            patterns=["def ", "return", "print("],
            mapping=(
                "Release reviews at bot teams are exactly this: a fixed set of gates a build must satisfy "
                "before it reaches users."
            ),
        ),
        179: dict(
            topic="Ship: retrospective and next steps",
            idea=(
                "A retrospective is a structured close, not a victory lap. Record what shipped with its "
                "version, what worked, what broke, and crucially what comes next. The next-steps list is the "
                "part people skip and the part that matters: shipping a bot and writing down three follow-ups "
                "turns a finished exercise into a roadmap, and it forces you to name the known gaps — no "
                "memory across sessions, no cancel intent — while you still remember why they were deferred. "
                "Keep the retro as data so a summary function can render it and so the list is greppable "
                "later; a paragraph in a chat message is forgotten by morning, a dict survives. The honest "
                "tone is the point: a shipped bot with two named gaps is more credible than one described as "
                "complete, and naming the gaps is what makes the next session productive. Today you write a "
                "retro dict, a `summarize` function and a loop over the next steps, printing the summary and "
                "each item. The asserts require at least one real gap and one next step, the two fields that "
                "make the document useful rather than decorative. Then rest before the next project, because "
                "a clear close stops the capstone's lessons from blurring into everything else you learned."
            ),
            code=(
                'RETRO = {\n'
                '    "shipped": "roombot v1.0",\n'
                '    "worked": ["intent table", "guardrails", "eval suite"],\n'
                '    "broke": ["no memory across sessions"],\n'
                '    "next": ["persist sessions", "add cancel intent", "log misroutes"],\n'
                '}\n'
                '\n'
                'def summarize(retro):\n'
                '    return (f"{retro[\'shipped\']}: {len(retro[\'worked\'])} wins, "\n'
                '            f"{len(retro[\'broke\'])} known gaps, {len(retro[\'next\'])} next steps")\n'
                '\n'
                'print(summarize(RETRO))\n'
                'for step in RETRO["next"]:\n'
                '    print("-", step)\n'
                '\n'
                'assert RETRO["next"] and RETRO["broke"]\n'
                'assert len(RETRO["worked"]) >= 3\n'
                'print("shipping means writing down what comes next")'
            ),
            variant_b='add a "metrics" field holding the final eval accuracy and include it in the summary line',
            variant_c='sort the next steps by impact and explain why ordering the list changes what gets done',
            mistakes=[
                "Describing the bot as complete instead of naming its known gaps.",
                "Skipping the next-steps list, so the momentum ends when the demo does.",
                "Writing the retro as prose that cannot be searched or summarised later.",
            ],
            q1=(
                "Why write the next-steps list before you feel done?",
                "Momentum fades at the finish; capturing follow-ups and known gaps while the context is fresh turns a finished exercise into a roadmap.",
            ),
            homework=(
                "Write `write_retro(shipped, worked, broke, next_steps)` returning a retro dict, and "
                "`summarize(retro)` rendering one line. Include at least three wins, one gap and three next steps, print "
                "the summary and each next step, and comment which line forces the gap to be named before "
                "shipping."
            ),
            patterns=["def ", "return", "print("],
            mapping=(
                "Shipping a bot ends with a retro and a backlog; the next-steps list is where the next "
                "iteration's tickets come from."
            ),
        ),
    },
)
