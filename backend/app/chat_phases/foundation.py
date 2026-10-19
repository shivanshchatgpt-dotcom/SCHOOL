"""Chatbot foundations, days 9-14: conversation as data you can test.

Every example is stdlib-only, offline and deterministic (no network, no model
call, no clock), so the applier can execute it and produce the same output every
run. The domain phases keep the same discipline: a message is a dict, history is
a list, intent routing is a table, and a tool call is just another message — so
the whole conversation can be replayed and asserted on without an API key.
"""

FOUNDATION = {
    9: dict(
        topic="Messages are data",
        idea=(
            "Every chatbot, from a keyword bot to a tool-using assistant, is built on the same primitive: a "
            "message with a role and some content. Once messages are plain dictionaries, history is a list, "
            "routing is a lookup, and a whole conversation is a value you can print, store and replay. That is "
            "what makes chatbots testable. The alternative — passing raw strings into functions that also mutate "
            "global state — works for a demo and collapses the moment you need to add a system prompt, a tool "
            "result or a correction. The role field matters because the same text means different things "
            "depending on who said it: instructions from the system, a question from the user, an answer from "
            "the assistant, a result from a tool. Today you build messages as dicts, append them to a list, and "
            "print a transcript. Notice that nothing here is specific to any vendor SDK; provider formats are "
            "just serialisations of this idea. Keep the schema small and consistent, because every later topic "
            "— context windows, intent routing, tool calls, evaluation — reads from this same message list."
        ),
        code=(
            'def message(role, content):\n'
            '    return {"role": role, "content": content}\n'
            '\n'
            'history = [\n'
            '    message("system", "You answer in one short sentence."),\n'
            '    message("user", "What is a token?"),\n'
            '    message("assistant", "A token is a chunk of text the model reads."),\n'
            ']\n'
            '\n'
            'for m in history:\n'
            '    print(f"{m[\'role\']:9}: {m[\'content\']}")\n'
            '\n'
            'assert [m["role"] for m in history] == ["system", "user", "assistant"]\n'
            'assert all(set(m) == {"role", "content"} for m in history)\n'
            'print("a conversation is a list of role/content dicts")'
        ),
        variant_b='add a tool message with role "tool" and a result payload, then print the transcript again',
        variant_c='write `last_user_message(history)` and print it for a conversation with two user turns',
        mistakes=[
            "Passing bare strings around and losing which speaker produced them.",
            "Using different keys for the same idea in different parts of the code.",
            "Mutating a shared history list from inside a helper without saying so.",
        ],
        q1=(
            "Why keep role and content as separate fields instead of one formatted string?",
            "Routing, truncation and provider adapters need to reason about the speaker independently of the text.",
        ),
        homework=(
            "Write `append_turn(history, role, content)` that returns a new history list with one message "
            "added. Build a three-turn conversation, print every role and content, and comment which line keeps "
            "the original history unchanged."
        ),
        patterns=["def ", "append", "print("],
        mapping=(
            "Provider APIs accept a list of role/content messages; tools such as LangChain and LlamaIndex wrap "
            "this same structure rather than replacing it."
        ),
    ),
    10: dict(
        topic="Conversation state and history",
        idea=(
            "A chatbot needs two different things that beginners often merge: the transcript and the state. The "
            "transcript is what was said, in order. The state is what the bot currently believes — the user's "
            "name, the chosen plan, whether a confirmation is pending. If you derive everything from the "
            "transcript, every new turn re-parses the entire conversation and the bot becomes slow and "
            "inconsistent. If you keep only state and discard the transcript, you cannot show context or debug "
            "why it answered the way it did. Keep both, with a clear owner for each: append turns to history, "
            "and update state through small functions that take the old state and a turn and return a new one. "
            "This is the same model/view split you meet in desktop apps, applied to dialogue. Today you build a "
            "history list plus a state dict, update the state from a user turn, and print both. The key test is "
            "that state is a function of the turns so far, so replaying the same turns rebuilds the same state. "
            "That property is what later lets you save a session, resume it, and evaluate the bot offline."
        ),
        code=(
            'def apply_turn(state, turn):\n'
            '    text = turn["content"].lower()\n'
            '    new = dict(state)\n'
            '    if "my name is" in text:\n'
            '        new["name"] = turn["content"].split("is", 1)[1].strip().title()\n'
            '    if "plan" in text:\n'
            '        new["wants_plan"] = True\n'
            '    return new\n'
            '\n'
            'history = []\n'
            'state = {"name": None, "wants_plan": False}\n'
            'turns = [\n'
            '    {"role": "user", "content": "Hi, my name is ada"},\n'
            '    {"role": "user", "content": "I need a study plan"},\n'
            ']\n'
            'for turn in turns:\n'
            '    history.append(turn)\n'
            '    state = apply_turn(state, turn)\n'
            '\n'
            'print("history length:", len(history))\n'
            'print("state:", state)\n'
            'assert state == {"name": "Ada", "wants_plan": True}\n'
            'print("state is derived from the turns")'
        ),
        variant_b='add a "topic" field set when the user mentions a subject, and print state after three turns',
        variant_c='rebuild state by replaying the same turns into a fresh dict and assert both are equal',
        mistakes=[
            "Re-parsing the whole transcript on every turn instead of maintaining explicit state.",
            "Letting a helper mutate the shared history list as a hidden side effect.",
            "Storing the same fact in both a message and a state field, then letting them disagree.",
        ],
        q1=(
            "Why keep a transcript as well as a state dict?",
            "State answers current questions quickly, while the transcript preserves what was actually said for context, debugging and replay.",
        ),
        homework=(
            "Write `replay(turns)` that starts from an empty state and applies every turn in order, returning "
            "the final state. Run it on two turn lists, print both states, and comment which line makes the "
            "result independent of how many times you call it."
        ),
        patterns=["def ", "return", "print("],
        mapping=(
            "Frameworks call this the conversation store or session state; production bots persist both the "
            "transcript and a small state object per session."
        ),
    ),
    11: dict(
        topic="Intent routing",
        idea=(
            "Before a bot can answer, it has to decide what the user is trying to do. The simplest honest "
            "approach is a routing table: a list of intents, each with a predicate and a handler. This is not "
            "as clever as a classifier, and that is the point — it is inspectable, testable and fast, and it "
            "covers a surprising amount of real traffic in narrow domains. The design questions are which "
            "intent wins when two predicates match, and what happens when none does. Order the rules from most "
            "specific to most general, always provide a fallback, and return the matched name so the caller can "
            "log it. A routing table also makes evaluation easy: you can feed labelled example utterances and "
            "measure how often the right intent fires. Today you build a table of three intents plus a "
            "fallback, route a handful of messages, and print the decision. Notice that handlers are separate "
            "from matching: matching decides what, handling decides the reply. That separation lets you add a "
            "model-based classifier later without rewriting the responder, and it keeps every response "
            "reproducible in a test."
        ),
        code=(
            'def wants_help(text):\n'
            '    return "help" in text or "how do i" in text\n'
            '\n'
            'def wants_price(text):\n'
            '    return "price" in text or "cost" in text\n'
            '\n'
            'def greeting(text):\n'
            '    return text in {"hi", "hello", "hey"}\n'
            '\n'
            'rules = [\n'
            '    ("price", wants_price),\n'
            '    ("help", wants_help),\n'
            '    ("greeting", greeting),\n'
            ']\n'
            '\n'
            'def route(text):\n'
            '    lowered = text.lower().strip()\n'
            '    for name, matches in rules:\n'
            '        if matches(lowered):\n'
            '            return name\n'
            '    return "fallback"\n'
            '\n'
            'for text in ["Hi", "How do I reset my password?", "What is the price?", "tell me a joke"]:\n'
            '    print(f"{text!r:38} -> {route(text)}")\n'
            '\n'
            'assert route("What is the cost?") == "price"\n'
            'assert route("hello") == "greeting"\n'
            'assert route("sing") == "fallback"'
        ),
        variant_b='add an "hours" intent matching "open" or "hours" and place it above the greeting rule',
        variant_c='return a list of all matching intents and explain when the first-match policy is wrong',
        mistakes=[
            "Writing rules from general to specific, so a broad predicate swallows every specific one.",
            "Forgetting a fallback, so unmatched input silently returns nothing.",
            "Burying the reply text inside the matcher instead of keeping matching and handling separate.",
        ],
        q1=(
            "Why order intent rules from most specific to most general?",
            "The first match wins, so a broad rule placed first hides the narrower rules that should have taken precedence.",
        ),
        homework=(
            "Write `route(text, rules)` that returns the name of the first matching rule or \"fallback\". "
            "Register three rules including a greeting, test five utterances covering each rule and a miss, "
            "print the decisions, and comment which line guarantees a fallback."
        ),
        patterns=["def ", "for ", "return"],
        mapping=(
            "Dialogflow, Rasa and Amazon Lex all expose intents with example utterances; classic bots are "
            "essentially this table with a scoring layer."
        ),
    ),
    12: dict(
        topic="Slot filling",
        idea=(
            "Most useful requests carry details: not just 'book a table' but 'book a table for four at seven'. "
            "Slot filling extracts those details into named fields so the handler can act on them. The pattern "
            "is: a slot schema declares what is needed, extractors pull candidates from the text, and a "
            "completeness check decides whether to answer or ask a follow-up. Two disciplines make this "
            "robust. First, extract to typed values — an integer party size, a normalised time — not raw "
            "substrings, because 'for 4' and 'for four' should behave the same. Second, always report which "
            "slots are still missing rather than guessing, because a bot that invents a party size is worse "
            "than one that asks. Today you implement a small slot schema for a booking, fill it from an "
            "utterance with simple parsing, and print both the filled slots and the missing ones. The "
            "important design choice is that filling is a pure function of text, so the same utterance always "
            "produces the same slots. That determinism is what makes the next lesson — asking the user for the "
            "missing piece — straightforward to test."
        ),
        code=(
            'def fill_slots(text, slots):\n'
            '    words = text.lower().split()\n'
            '    filled = dict(slots)\n'
            '    for i, word in enumerate(words):\n'
            '        if word in {"for", "party"} and i + 1 < len(words):\n'
            '            digits = "".join(ch for ch in words[i + 1] if ch.isdigit())\n'
            '            if digits:\n'
            '                filled["party_size"] = int(digits)\n'
            '        if word == "at" and i + 1 < len(words):\n'
            '            time = words[i + 1].strip(".,")\n'
            '            if ":" in time:\n'
            '                filled["time"] = time\n'
            '    return filled\n'
            '\n'
            'def missing(slots):\n'
            '    return [name for name, value in slots.items() if value is None]\n'
            '\n'
            'slots = {"party_size": None, "time": None, "date": None}\n'
            'filled = fill_slots("Book a table for 4 at 7:30", slots)\n'
            'print("filled:", filled)\n'
            'print("still needed:", missing(filled))\n'
            '\n'
            'assert filled["party_size"] == 4 and filled["time"] == "7:30"\n'
            'assert missing(filled) == ["date"]\n'
            'print("slots are typed values with an explicit missing list")'
        ),
        variant_b='add a "date" slot that matches words like "today" or "tomorrow"',
        variant_c='accept word numbers ("for four") by mapping a small dictionary before parsing',
        mistakes=[
            "Storing raw substrings as slot values, so downstream code has to re-parse them.",
            "Guessing a missing value instead of asking the user for it.",
            "Returning only the filled slots, hiding which required ones are still empty.",
        ],
        q1=(
            "Why return both the filled slots and the missing ones?",
            "The handler needs the values it has and an explicit next question, and a visible missing list prevents silent guessing.",
        ),
        homework=(
            "Write `fill_slots(text, schema)` that fills named slots from an utterance and returns a dict. "
            "Use a schema with three fields, test a partial utterance and a complete one, print the filled dict "
            "and the missing list for both, and comment which line enforces the schema."
        ),
        patterns=["def ", "return", "print("],
        mapping=(
            "This is what Rasa calls slot filling and what function-calling APIs describe as extracting "
            "arguments; the schema is the tool's parameter list."
        ),
    ),
    13: dict(
        topic="Tool calls and results as messages",
        idea=(
            "When a bot needs a fact or an action, it does not have to know the answer — it can call a tool and "
            "put the result back into the conversation. The clean way to model this is with messages: the "
            "assistant emits a tool-call message naming the tool and its arguments, your code validates and "
            "executes it, then appends a tool-result message with the output. The model never executes anything "
            "itself, which is exactly why the boundary is safe and testable. Three rules keep this honest. "
            "Validate arguments before calling, because an LLM can produce a plausible but invalid value. "
            "Return errors as results rather than raising, because the next turn needs to see what went wrong. "
            "Keep tools small and named after one action each, because a tool that does several things is hard "
            "to retry and hard to authorise. Today you implement a dispatcher with two tools, run a valid call "
            "and an invalid one, and print the result messages. The transcript after a tool call is just more "
            "messages, which means the whole exchange replays exactly like any other conversation."
        ),
        code=(
            'def get_weather(city):\n'
            '    table = {"london": "rain", "cairo": "sun"}\n'
            '    return table.get(city.lower(), "unknown")\n'
            '\n'
            'def add(a, b):\n'
            '    if not isinstance(a, int) or not isinstance(b, int):\n'
            '        raise ValueError("add expects integers")\n'
            '    return a + b\n'
            '\n'
            'TOOLS = {"weather": get_weather, "add": add}\n'
            '\n'
            'def call_tool(name, args):\n'
            '    if name not in TOOLS:\n'
            '        return {"role": "tool", "name": name, "content": "error: unknown tool"}\n'
            '    try:\n'
            '        result = TOOLS[name](**args)\n'
            '    except Exception as error:\n'
            '        return {"role": "tool", "name": name, "content": f"error: {error}"}\n'
            '    return {"role": "tool", "name": name, "content": str(result)}\n'
            '\n'
            'results = [\n'
            '    call_tool("weather", {"city": "Cairo"}),\n'
            '    call_tool("add", {"a": 2, "b": "three"}),\n'
            '    call_tool("delete", {}),\n'
            ']\n'
            'for r in results:\n'
            '    print(r["name"], "->", r["content"])\n'
            'assert results[0]["content"] == "sun"\n'
            'assert results[1]["content"].startswith("error:")'
        ),
        variant_b='add a "time" tool returning a fixed string and test it with a city argument',
        variant_c='return structured args in the error result so the next turn can correct them',
        mistakes=[
            "Letting the model execute code directly instead of emitting a call your dispatcher validates.",
            "Raising on bad arguments, which kills the turn instead of letting the conversation recover.",
            "Building one giant tool that performs several unrelated actions, making retries ambiguous.",
        ],
        q1=(
            "Why return tool errors as messages instead of raising exceptions?",
            "The next turn can see the failure, explain it or retry with corrected arguments, and the transcript stays replayable.",
        ),
        homework=(
            "Write `dispatch(tools, name, args)` that validates the tool name, calls it, and returns a "
            "tool-result dict on success or a readable error dict on failure. Register two tools, make one "
            "deliberately fail, print both results, and comment which line keeps the error in the conversation."
        ),
        patterns=["def ", "try", "return"],
        mapping=(
            "OpenAI function calling, Anthropic tool use and LangChain tools all follow this call/result "
            "message pattern with provider-specific field names."
        ),
    ),
    14: dict(
        topic="A tiny chatbot, end to end",
        idea=(
            "Today you connect the pieces into one scripted conversation: history as a list of messages, a "
            "router that picks an intent, a slot extractor for one request, and a tool call whose result is "
            "appended as a message. The bot is small, but the shape is the shape of every chatbot you will "
            "build later. Because the input is a fixed list of turns and nothing touches a network or a clock, "
            "the entire conversation is reproducible, so you can assert on the final transcript instead of "
            "eyeballing logs. Notice where each concern lives: routing decides what, handlers decide the reply, "
            "the tool layer returns data, and the loop only orders turns. The bot should always end with a "
            "message — even when the intent is unknown — because silence is the worst failure mode in a chat. "
            "It should also make clear what it did: a tool result is visible as a tool message rather than "
            "being silently folded into prose. Those two habits, never silent and always inspectable, are what "
            "make a bot debuggable in production. Keep the state dict small and derived, and this skeleton will "
            "survive every later feature."
        ),
        code=(
            'def respond(text):\n'
            '    lowered = text.lower()\n'
            '    if "weather" in lowered:\n'
            '        city = "cairo" if "cairo" in lowered else "london"\n'
            '        return [\n'
            '            {"role": "assistant", "content": f"Looking up {city}."},\n'
            '            {"role": "tool", "name": "weather", "content": "sun" if city == "cairo" else "rain"},\n'
            '        ]\n'
            '    if "hello" in lowered or "hi" in lowered:\n'
            '        return [{"role": "assistant", "content": "Hello! Ask me about the weather."}]\n'
            '    return [{"role": "assistant", "content": "I did not understand that."}]\n'
            '\n'
            'history = [{"role": "system", "content": "Short answers only."}]\n'
            'for user_text in ["Hi", "What is the weather in Cairo?", "Sing"]:\n'
            '    history.append({"role": "user", "content": user_text})\n'
            '    history.extend(respond(user_text))\n'
            '\n'
            'for m in history:\n'
            '    print(f"{m[\'role\']:9}: {m[\'content\']}")\n'
            '\n'
            'assert history[-1]["role"] == "assistant"\n'
            'assert any(m.get("name") == "weather" for m in history if m["role"] == "tool")\n'
            'print("every turn ends with a visible message")'
        ),
        variant_b='add an "hours" branch that answers with a fixed string and test it as a fourth turn',
        variant_c='return a single message per turn instead of a list, and explain what you lose for tool calls',
        mistakes=[
            "Leaving an unknown intent without a reply, so the user sees nothing at all.",
            "Hiding tool output inside assistant prose, making it impossible to verify what was called.",
            "Letting the loop depend on global state instead of the history it was given.",
        ],
        q1=(
            "Why should every turn end with a visible message, even for an unknown intent?",
            "Silence looks like a crash; an explicit fallback tells the user the bot is alive and what it can do.",
        ),
        homework=(
            "Write `chat(turns)` that replays a list of user strings and returns the full history including "
            "assistant and tool messages. Handle greeting, one tool intent and a fallback, print the transcript, "
            "and comment which line guarantees a reply for every turn."
        ),
        patterns=["def ", "return", "print("],
        mapping=(
            "This is the same loop production assistants run; the difference is a model choosing intents and "
            "tools instead of hand-written rules."
        ),
    ),
}
