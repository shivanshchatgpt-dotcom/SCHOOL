"""Tools and function calling, days 105-119: the model proposes, the host decides.

Examples stay stdlib-only, offline and deterministic: schemas, tool calls,
results, retries, plans and audit rows are plain dictionaries and lists, so the
same run prints the same transcript every time.
"""

PHASE = ("Tools and Function Calling", "Let a model request tools while the host validates, authorises, executes and audits every call.", {
    105: dict(
        topic="Orientation: tools the model can ask for",
        idea=(
            "The model does not execute anything. It can only emit a structured request saying which tool it "
            "wants and with what arguments; the host decides whether that request is valid, safe and available, "
            "then runs the Python function and sends the result back. This split is the whole architecture of "
            "function calling, and it is also the main safety boundary: a model that can only propose is far "
            "less dangerous than a model wired directly to a database. Today you build a tool registry as plain "
            "data — a name, a description and a parameter sketch — and a fake model output containing one tool "
            "call. Nothing is live: you print which tools exist, which one the model asked for, and whether the "
            "host can serve it. Notice that the registry is just a dict, so a test can assert on it. Notice also "
            "that the model's arguments arrive as data, not as Python keywords, which is why validation comes "
            "next. If you keep this shape — model proposes, host validates, host executes, result returns as a "
            "message — every later topic in this phase slots in without redesign. The temptation is to let the "
            "model call functions directly; resist it, because you lose the place where checks and logs belong."
        ),
        code=(
            'def tool(name, description, parameters):\n'
            '    return {"name": name, "description": description, "parameters": parameters}\n'
            '\n'
            'REGISTRY = {\n'
            '    "get_weather": tool("get_weather", "Weather for a city", {"city": "str"}),\n'
            '    "convert_currency": tool("convert_currency", "Convert money",\n'
            '                             {"amount": "float", "source": "str", "target": "str"}),\n'
            '}\n'
            '\n'
            'model_output = {\n'
            '    "role": "assistant",\n'
            '    "content": None,\n'
            '    "tool_calls": [{"name": "get_weather", "arguments": {"city": "Pune"}}],\n'
            '}\n'
            '\n'
            'print("available:", sorted(REGISTRY))\n'
            'for call in model_output["tool_calls"]:\n'
            '    print("model asked for:", call["name"], call["arguments"])\n'
            '    print("host can serve:", call["name"] in REGISTRY)\n'
            '\n'
            'assert all(set(t) == {"name", "description", "parameters"} for t in REGISTRY.values())\n'
            'print("the model proposes; the host executes")'
        ),
        variant_b='add a second tool call for an unknown tool name and print that the host rejects it',
        variant_c='give each registry entry a "dangerous" flag and print only the safe tool names',
        mistakes=[
            "Letting the model execute Python instead of emitting a request.",
            "Building a registry that is not inspectable data, so tests cannot assert on it.",
            "Forgetting that tool arguments arrive as untrusted data, not as keywords.",
        ],
        q1=(
            "Who executes a tool call, and why does that split matter?",
            "The host executes it; the model only proposes, which keeps validation, permissions and logging in code you control.",
        ),
        homework=(
            "Write `build_registry(entries)` that turns a list of (name, description) pairs into a dict of tool "
            "records. Add a `find_tool(registry, name)` helper that returns the record or None, then print lookups "
            "for one known and one unknown tool name."
        ),
        patterns=["build_registry", "find_tool", "print("],
        mapping=(
            "OpenAI and Anthropic tool use both return a structured call for the host to execute, and LangChain "
            "tools wrap the same contract as name plus description plus argument schema."
        ),
    ),
    106: dict(
        topic="A tool schema",
        idea=(
            "A tool schema is a contract written as data. It tells the model what the tool does, what arguments "
            "it accepts, which are required, and which values are allowed; it tells the host what to check before "
            "running anything. Think of it as a small, boring JSON-Schema subset: an object with named "
            "properties, a type per property, an optional enum, and a required list. Descriptions are not "
            "decoration — they are the part the model reads when deciding whether to call the tool, so vague text "
            "produces vague calls. Today you build one schema and a shape checker that reports missing required "
            "keys and unknown keys. Shape checking is deliberately separate from value checking: first confirm "
            "the object has the right fields, then confirm each value is sensible. Keep the schema beside the "
            "function it describes, and derive both from the same source when you can, or they will drift. The "
            "checker returns lists of problems rather than a single boolean so the caller can show the model "
            "everything that is wrong at once. A schema that only lives in prose will be violated, and a schema "
            "that is too permissive teaches the model to send junk. Small, explicit, testable: that is the whole "
            "lesson."
        ),
        code=(
            'SCHEMA = {\n'
            '    "name": "get_weather",\n'
            '    "description": "Current weather for one city",\n'
            '    "parameters": {\n'
            '        "type": "object",\n'
            '        "properties": {\n'
            '            "city": {"type": "string"},\n'
            '            "unit": {"type": "string", "enum": ["c", "f"]},\n'
            '        },\n'
            '        "required": ["city"],\n'
            '    },\n'
            '}\n'
            '\n'
            'def check_shape(schema, args):\n'
            '    spec = schema["parameters"]\n'
            '    missing = [key for key in spec["required"] if key not in args]\n'
            '    unknown = [key for key in args if key not in spec["properties"]]\n'
            '    return {"missing": missing, "unknown": unknown}\n'
            '\n'
            'print(SCHEMA["parameters"]["required"])\n'
            'print(check_shape(SCHEMA, {"city": "Pune", "unit": "c"}))\n'
            'print(check_shape(SCHEMA, {"unit": "c", "wind": 3}))\n'
            '\n'
            'assert check_shape(SCHEMA, {"city": "Pune"}) == {"missing": [], "unknown": []}\n'
            'print("schema checked before any work happens")'
        ),
        variant_b='add an optional "days" integer property and check a call that sends it as a string',
        variant_c='write a second schema for a currency converter with two required string fields',
        mistakes=[
            "Writing a schema so vague that every argument shape looks valid.",
            "Checking values before checking that required keys exist.",
            "Letting schema and implementation drift apart until calls fail in production.",
        ],
        q1=(
            "Why check shape before checking values?",
            "Missing or unknown fields make value checks meaningless, and separate checks give clearer error messages.",
        ),
        homework=(
            "Write `check_shape(schema, args)` for a schema with required and optional properties. Return a dict "
            "with missing and unknown keys, then test it on a complete call, a call missing a required key, and a "
            "call carrying an extra key."
        ),
        patterns=["def check_shape", "missing", "unknown"],
        mapping=(
            "OpenAI tools use a JSON Schema object for parameters, Anthropic input schemas are the same idea, and "
            "LangChain tools publish an args_schema built from a typed model."
        ),
    ),
    107: dict(
        topic="Validating arguments",
        idea=(
            "The model will send arguments you did not expect. Validation is the code that refuses them before "
            "they reach a database, a shell or a payment API. Shape checking is not enough: a city can be the "
            "empty string, a unit can be kilvin, a day count can be zero, negative, huge, or the boolean True, "
            "which Python happily treats as an integer. Good validation names each rule, reports every violation "
            "rather than stopping at the first, and produces a message the model can act on. Prefer allow-lists "
            "over deny-lists: accept c or f, not anything except g. Check types explicitly, because bool is a "
            "subclass of int and isinstance(True, int) is True. Validate lengths and ranges so a single call "
            "cannot ask for ten thousand pages. Keep validation pure: arguments in, list of errors out, with no "
            "side effects, so it is trivial to test. Do not silently coerce bad input into something acceptable; "
            "a model that sends days as a string should be corrected, not guessed at. Today you write a validator "
            "for three fields and run it against a valid call and two broken ones. The printed output is the contract the "
            "next stage relies on."
        ),
        code=(
            'def validate_args(args):\n'
            '    errors = []\n'
            '    city = args.get("city")\n'
            '    if not isinstance(city, str) or not city.strip():\n'
            '        errors.append("city must be a non-empty string")\n'
            '    unit = args.get("unit", "c")\n'
            '    if unit not in {"c", "f"}:\n'
            '        errors.append("unit must be c or f")\n'
            '    if "days" in args:\n'
            '        days = args["days"]\n'
            '        if isinstance(days, bool) or not isinstance(days, int) or not 1 <= days <= 7:\n'
            '            errors.append("days must be an int from 1 to 7")\n'
            '    return errors\n'
            '\n'
            'cases = [\n'
            '    {"city": "Pune"},\n'
            '    {"city": "", "unit": "k"},\n'
            '    {"city": "Pune", "days": True},\n'
            ']\n'
            'for args in cases:\n'
            '    print(args, "->", validate_args(args) or "ok")\n'
            '\n'
            'assert validate_args({"city": "Pune", "days": 3}) == []\n'
            'print("all violations reported, no guessing")'
        ),
        variant_b='add a maximum city length of 80 characters and show the error for a longer value',
        variant_c='make validation return (errors, cleaned_args) and clean only harmless whitespace',
        mistakes=[
            "Using isinstance(x, int) and forgetting that booleans pass that check.",
            "Returning on the first error so the model never learns the other problems.",
            "Coercing bad values silently instead of rejecting them with a reason.",
        ],
        q1=(
            "Why is an allow-list safer than a deny-list for a unit argument?",
            "Unknown or future values are rejected by default, while a deny-list lets anything not explicitly forbidden through.",
        ),
        homework=(
            "Write `validate_args(args)` for a tool that takes a non-empty name, an allowed mode from two options, "
            "and an integer count from 1 to 100. Collect every error in a list and print the result for one valid "
            "and two invalid calls."
        ),
        patterns=["def validate_args", "errors.append", "isinstance"],
        mapping=(
            "OpenAI and Anthropic do not validate tool arguments for you, so application code must; LangChain "
            "arg schemas help, but boundary validation is still your responsibility."
        ),
    ),
    108: dict(
        topic="Dispatching a tool call",
        idea=(
            "Dispatch is the small piece of code that turns a validated name and argument dict into a function "
            "call. Keep it a table, not a chain of if statements: map names to callables, look up the name, and "
            "refuse anything that is not in the table. That lookup is an allow-list for behaviour, not just "
            "naming. A good dispatcher also catches exceptions from the tool and converts them into a result "
            "object with ok false, because a crashing tool should not crash the whole conversation. Do not use "
            "eval or getattr on model-supplied strings; the table is the only route. Argument passing is a second "
            "decision: passing **args is fine only after validation has guaranteed the names and types. If the "
            "tool signature and schema drift, a TypeError is a host bug, so surface it clearly. Today you build "
            "two tiny tools, dispatch a valid call, an unknown tool, and a call that raises inside the tool. The "
            "output is uniform: every branch returns a dict with ok and either result or error. Uniform results "
            "are what make the next step, putting tool results back into the message history, mechanical rather "
            "than special-cased. That makes exhaustive routing tests very cheap indeed."
        ),
        code=(
            'def get_weather(city, unit="c"):\n'
            '    return {"city": city, "temp": 31 if unit == "c" else 88, "unit": unit}\n'
            '\n'
            'def add(a, b):\n'
            '    return a + b\n'
            '\n'
            'TOOLS = {"get_weather": get_weather, "add": add}\n'
            '\n'
            'def dispatch(name, args):\n'
            '    fn = TOOLS.get(name)\n'
            '    if fn is None:\n'
            '        return {"ok": False, "error": f"unknown tool: {name}"}\n'
            '    try:\n'
            '        return {"ok": True, "result": fn(**args)}\n'
            '    except Exception as exc:\n'
            '        return {"ok": False, "error": f"{type(exc).__name__}: {exc}"}\n'
            '\n'
            'print(dispatch("get_weather", {"city": "Pune"}))\n'
            'print(dispatch("add", {"a": 2, "b": 3}))\n'
            'print(dispatch("delete_everything", {}))\n'
            'print(dispatch("add", {"a": 2}))\n'
            '\n'
            'assert dispatch("add", {"a": 2, "b": 3})["result"] == 5\n'
            'print("dispatch is a table with uniform results")'
        ),
        variant_b='add a tool that raises ValueError on purpose and confirm the dispatcher returns ok false',
        variant_c='make the dispatcher reject argument keys that the function signature does not accept',
        mistakes=[
            "Dispatching with eval or getattr on a model-supplied string.",
            "Letting a tool exception escape and kill the whole conversation loop.",
            "Returning different shapes from different tools, forcing callers to special-case.",
        ],
        q1=(
            "Why does a dispatcher return an error dict instead of raising?",
            "The conversation can continue, the model can read the failure and recover, and the host stays in control.",
        ),
        homework=(
            "Write `dispatch(registry, name, args)` that looks a tool up in a dict, calls it with keyword "
            "arguments, and returns a uniform dict with ok plus result or error. Test a valid call, an unknown "
            "name, and a tool that raises."
        ),
        patterns=["def dispatch", "try:", "TOOLS"],
        mapping=(
            "In OpenAI and Anthropic flows the host performs exactly this lookup after the model returns a tool "
            "call; LangChain agents do it inside their executor with the same allow-list idea."
        ),
    ),
    109: dict(
        topic="Tool results as messages",
        idea=(
            "After the host runs a tool, the result must go back into the conversation as a message, not as a "
            "loose variable. That message carries a role, the call identifier it answers, the tool name and a "
            "content string. The identifier is what ties a result to a specific request when the model asked for "
            "several calls at once. Providers differ in field names, but the shape is consistent: assistant "
            "message with tool calls, then one tool message per call, then the assistant's next message that uses "
            "the results. Keep the result as text because that is what the model reads; if the tool returns a "
            "dict, serialise it deterministically. Do not paste raw objects or exception reprs into history: they "
            "are noisy and may leak internals. Do not drop the tool name either, because transcripts become hard "
            "to audit. Today you build a four-message history by hand and assert that the tool message points at "
            "the right call id. The important habit is that the whole exchange is data you can print and replay. "
            "The content can be long, but its shape stays simple and inspectable. Once results are messages, logging a "
            "conversation and reconstructing a failed run stop being separate features."
        ),
        code=(
            'history = [{"role": "user", "content": "Weather in Pune?"}]\n'
            '\n'
            'call = {"id": "call-1", "name": "get_weather", "arguments": {"city": "Pune"}}\n'
            'history.append({"role": "assistant", "content": None, "tool_calls": [call]})\n'
            '\n'
            'result = {"city": "Pune", "temp_c": 31}\n'
            'history.append({\n'
            '    "role": "tool",\n'
            '    "tool_call_id": "call-1",\n'
            '    "name": "get_weather",\n'
            '    "content": f"city={result[\'city\']} temp_c={result[\'temp_c\']}",\n'
            '})\n'
            'history.append({"role": "assistant", "content": "It is 31C in Pune."})\n'
            '\n'
            'for message in history:\n'
            '    print(message["role"], "|", message.get("content"))\n'
            '\n'
            'tool_message = history[2]\n'
            'assert tool_message["tool_call_id"] == call["id"]\n'
            'assert tool_message["name"] == call["name"]\n'
            'print("result linked to call", tool_message["tool_call_id"])'
        ),
        variant_b='add a second tool call and result so both tool messages appear before the final answer',
        variant_c='serialise the tool result with sorted keys and print the content string that results',
        mistakes=[
            "Losing the call id so a result cannot be matched to its request.",
            "Appending the final assistant answer before the tool result message.",
            "Dumping an object repr into content instead of a stable serialised form.",
        ],
        q1=(
            "What links a tool result message to the request that produced it?",
            "The tool call identifier, which the result echoes as tool_call_id.",
        ),
        homework=(
            "Write `append_tool_result(history, call, result)` that appends a tool message with the call id, tool "
            "name and a deterministic text content. Build a history with one call, print every role, and assert "
            "the ids match."
        ),
        patterns=["def append_tool_result", "tool_call_id", "history.append"],
        mapping=(
            "OpenAI uses role tool with tool_call_id and Anthropic uses tool_result blocks keyed by tool_use id; "
            "LangChain message objects carry the same linkage."
        ),
    ),
    110: dict(
        topic="Errors the model can recover from",
        idea=(
            "A tool failure is information, and some of it is useful to the model. The host should classify the "
            "failure before writing it into history: a bad unit is recoverable because the argument can change, "
            "a permission denial is usually fatal for this attempt, and a timeout may be worth one retry. Write "
            "that classification into the result as plain fields: ok, error code, message, allowed values or a "
            "hint, and a retryable flag. Never paste a traceback or a raw exception repr into the model's context; "
            "it is noisy, unstable and can leak internals. Keep the message short and actionable, for example "
            "bad_unit with allowed c and f. The model can then send a corrected call, and the host validates it "
            "again exactly as before. This is not the model debugging itself; it is the host giving a precise "
            "negative result and letting the model choose another valid action. Today a fake attempt list sends "
            "kelvin first and f second, and the loop stops at the first success. The attempt list stands in for a "
            "model, so the run is deterministic. Notice that the error object is the same shape as a success "
            "object, which keeps the loop simple."
        ),
        code=(
            'def run_tool(args):\n'
            '    unit = args.get("unit", "c")\n'
            '    if unit not in {"c", "f"}:\n'
            '        return {"ok": False, "error": "bad_unit", "allowed": ["c", "f"], "retryable": True}\n'
            '    return {"ok": True, "temp": 31 if unit == "c" else 88, "unit": unit}\n'
            '\n'
            'attempts = [\n'
            '    {"city": "Pune", "unit": "kelvin"},\n'
            '    {"city": "Pune", "unit": "f"},\n'
            ']\n'
            '\n'
            'for number, args in enumerate(attempts, 1):\n'
            '    outcome = run_tool(args)\n'
            '    print(number, args["unit"], outcome)\n'
            '    if outcome["ok"]:\n'
            '        print("recovered on attempt", number)\n'
            '        break\n'
            '\n'
            'assert outcome["ok"] and outcome["temp"] == 88\n'
            'print("structured errors let the caller correct course")'
        ),
        variant_b='add a "city_missing" error with retryable false and stop the loop when it appears',
        variant_c='include a hint string in each error and print only the hint the model would read',
        mistakes=[
            "Returning a traceback or exception repr to the model.",
            "Marking every error retryable so retries hammer a permanent failure.",
            "Using a different result shape for errors, forcing special cases everywhere.",
        ],
        q1=(
            "What makes a tool error recoverable?",
            "The caller can change something valid, such as an argument, and the error says precisely what to change.",
        ),
        homework=(
            "Write `run_tool(args)` that returns ok true or a structured error with code, message, allowed values "
            "and retryable. Drive it with a hard-coded attempt list, print each outcome, and stop at the first "
            "success."
        ),
        patterns=["def run_tool", "retryable", "allowed"],
        mapping=(
            "Both OpenAI and Anthropic feed tool errors back as ordinary tool results; LangChain tool exceptions "
            "can be configured to return a message so the agent can recover."
        ),
    ),
    111: dict(
        topic="Retries and backoff",
        idea=(
            "Retries are for transient failures, not for every failure. A rate limit, a timeout or a temporary "
            "server error may succeed on a second attempt; a validation error or a permission denial will not. "
            "Retrying the wrong class wastes time and can duplicate side effects. A retry policy has four parts: "
            "which errors are retryable, how many attempts, how long to wait between them, and what to do when "
            "the budget runs out. Exponential backoff multiplies the delay each time, and jitter spreads clients "
            "out so they do not synchronise. This lesson keeps only the schedule arithmetic: attempts are a "
            "deterministic list and the delays are counted, never slept. That is enough to test the decision "
            "logic. Always cap attempts and total delay; an unbounded retry loop is an outage. Do not retry inside "
            "a tool that already performed a side effect unless that operation is idempotent, which is the next "
            "topic but one. Today you walk a schedule of rate limit, timeout, success and print the attempt number "
            "and the next delay. You also handle a fatal outcome immediately. The retry policy lives in one function, so it can be fully unit-tested without a network or any real clock."
        ),
        code=(
            'def call_with_retry(outcomes, retryable=("rate_limit", "timeout"), base=0.5, cap=4.0):\n'
            '    delay = base\n'
            '    for attempt, outcome in enumerate(outcomes, 1):\n'
            '        print(f"attempt {attempt}: {outcome}")\n'
            '        if outcome == "ok":\n'
            '            return {"attempts": attempt, "next_delay": 0.0, "status": "ok"}\n'
            '        if outcome not in retryable:\n'
            '            return {"attempts": attempt, "next_delay": 0.0, "status": "fatal"}\n'
            '        print(f"  backing off {delay}s before a retry")\n'
            '        delay = min(cap, delay * 2)\n'
            '    return {"attempts": len(outcomes), "next_delay": delay, "status": "exhausted"}\n'
            '\n'
            'print(call_with_retry(["rate_limit", "timeout", "ok"]))\n'
            'print(call_with_retry(["bin_perm", "rate_limit"]))\n'
            '\n'
            'result = call_with_retry(["rate_limit", "ok"])\n'
            'assert result["attempts"] == 2 and result["status"] == "ok"\n'
            'print("retry only transient failures, with a capped schedule")'
        ),
        variant_b='add a total attempt cap of three and show what happens to a list of five failures',
        variant_c='use a deterministic jitter list such as [0.1, 0.2] added to each delay and print the schedule',
        mistakes=[
            "Retrying validation or permission errors that cannot succeed on a second try.",
            "Retrying forever with no attempt cap or total delay limit.",
            "Sleeping inside a loop with no way to cancel or observe the wait.",
        ],
        q1=(
            "Why apply backoff instead of retrying immediately?",
            "It gives a struggling service time to recover and prevents a burst of clients from making the overload worse.",
        ),
        homework=(
            "Write `call_with_retry(outcomes)` that walks a fixed outcome list, retries only named transient "
            "errors, doubles a delay up to a cap, and returns status, attempts and next delay. Add a fatal outcome "
            "case and print both results."
        ),
        patterns=["def call_with_retry", "retryable", "delay"],
        mapping=(
            "Provider SDKs implement retry and backoff around HTTP calls; LangChain exposes max_retries, while "
            "application-level tool retries still need your own policy."
        ),
    ),
    112: dict(
        topic="Timeouts and cancellation",
        idea=(
            "A tool call that never returns is worse than one that fails, because it holds a conversation open "
            "with no result. Timeouts bound each call; a deadline bounds the whole task. The two are related but "
            "not identical: one slow call can exhaust a task budget that several calls share. Pass the remaining "
            "budget down rather than starting a fresh generous timeout at every layer. Cancellation is "
            "cooperative: the caller marks the work as cancelled and each step checks before doing more. In this "
            "lesson there is no real clock, so costs are fixed numbers and the budget is arithmetic. That is a "
            "feature: the decision logic is what you are testing, not the scheduler. Always define what happens "
            "to partial work. A cancelled read is harmless; a cancelled write may have already changed state, "
            "which is why dangerous operations need confirmation and idempotency. Report the step where the "
            "budget ran out, not just a generic timeout, because that tells the user what was completed. Today you "
            "run a three-step plan against two budgets and print the completed steps, the cancelled step and the "
            "budget used. The shorter budget cuts the third step before it starts; the longer one finishes."
        ),
        code=(
            'OPERATIONS = [("lookup", 1.0), ("fetch_pages", 1.4), ("summarise", 2.0)]\n'
            '\n'
            'def run_with_budget(operations, budget):\n'
            '    used = 0.0\n'
            '    done = []\n'
            '    for name, cost in operations:\n'
            '        if used + cost > budget:\n'
            '            return {"done": done, "cancelled_at": name, "used": round(used, 1)}\n'
            '        used += cost\n'
            '        done.append(name)\n'
            '    return {"done": done, "cancelled_at": None, "used": round(used, 1)}\n'
            '\n'
            'print(run_with_budget(OPERATIONS, 3.0))\n'
            'print(run_with_budget(OPERATIONS, 1.5))\n'
            '\n'
            'short = run_with_budget(OPERATIONS, 2.5)\n'
            'assert short["done"] == ["lookup", "fetch_pages"]\n'
            'assert short["cancelled_at"] == "summarise"\n'
            'print("a budget stops work before it starts, not halfway through")'
        ),
        variant_b='add a per-call timeout of 1.5 and cancel any single operation whose cost exceeds it',
        variant_c='carry the remaining budget in the result so a follow-up call can resume with what is left',
        mistakes=[
            "Resetting the full timeout at every layer so the task can run far past its deadline.",
            "Cancelling without reporting which step completed and which was skipped.",
            "Treating cancellation as free for writes that may already have happened.",
        ],
        q1=(
            "What is the difference between a per-call timeout and a task deadline?",
            "A timeout bounds one call; a deadline bounds all the work and is shared across steps.",
        ),
        homework=(
            "Write `run_with_budget(operations, budget)` where operations are name and fixed cost pairs. Return "
            "the completed names, the cancelled step and the budget used. Print results for a budget that fits and "
            "one that does not."
        ),
        patterns=["def run_with_budget", "budget", "cancelled_at"],
        mapping=(
            "HTTP clients and OpenAI or Anthropic SDKs accept request timeouts; LangChain runnables can enforce "
            "timeouts, but sharing one deadline across tools remains application code."
        ),
    ),
    113: dict(
        topic="Idempotency for side effects",
        idea=(
            "A retry is safe only if repeating the operation has the same effect as doing it once. Reads are "
            "naturally idempotent; refunds, emails and account deletions are not. The standard fix is an "
            "idempotency key: the caller derives a stable key from the intent, sends it with the call, and the "
            "host records the key together with the outcome. If the same key arrives again, the host returns the "
            "stored outcome instead of performing the side effect a second time. The key must be stable across "
            "retries but different for genuinely different requests, so derive it from business identity such as "
            "order plus refund, not from a random value generated on each attempt. Store enough to replay the "
            "response, not only a boolean. Real systems also need TTLs, durability and a concurrency guarantee, "
            "because two simultaneous requests can both miss the first lookup; a lock or a unique constraint "
            "handles that. Today a dict stands in for that store and the calls are sequential, which is enough to "
            "see the protocol. The first refund writes one ledger row; the replay returns the same receipt and "
            "leaves the ledger untouched. The key is data, not magic; it is the caller's promise."
        ),
        code=(
            'LEDGER = []\n'
            'RECEIPTS = {}\n'
            '\n'
            'def send_refund(key, amount):\n'
            '    if key in RECEIPTS:\n'
            '        return {"replayed": True, "receipt": RECEIPTS[key], "rows": len(LEDGER)}\n'
            '    receipt = f"rcpt-{len(LEDGER) + 1}"\n'
            '    LEDGER.append({"key": key, "amount": amount})\n'
            '    RECEIPTS[key] = receipt\n'
            '    return {"replayed": False, "receipt": receipt, "rows": len(LEDGER)}\n'
            '\n'
            'print(send_refund("order-7-refund", 25))\n'
            'print(send_refund("order-7-refund", 25))\n'
            'print(send_refund("order-8-refund", 40))\n'
            'print("ledger rows:", len(LEDGER))\n'
            '\n'
            'assert len(LEDGER) == 2\n'
            'assert send_refund("order-7-refund", 25)["receipt"] == "rcpt-1"\n'
            'print("same key, same receipt, one side effect")'
        ),
        variant_b='add a mismatch check: same key with a different amount returns an error instead of a replay',
        variant_c='store the full response payload under the key and print the replay for a multi-field result',
        mistakes=[
            "Generating a fresh idempotency key on every retry, which defeats the whole mechanism.",
            "Storing only that a key was seen, not the response needed to replay it.",
            "Ignoring the race where two identical requests arrive at the same time.",
        ],
        q1=(
            "What should an idempotency key be derived from?",
            "Stable business identity for the intent, such as order and operation, not a random value per attempt.",
        ),
        homework=(
            "Write `send_refund(key, amount)` backed by a ledger list and a receipts dict. On a repeated key return "
            "the stored receipt without appending a row, and print the results of a first call, a replay and a new "
            "key."
        ),
        patterns=["def send_refund", "RECEIPTS", "replayed"],
        mapping=(
            "Payment APIs such as Stripe document idempotency keys explicitly; OpenAI and Anthropic retries need "
            "the same discipline for any tool that writes, and LangChain tools do not add it for you."
        ),
    ),
    114: dict(
        topic="Confirmation before dangerous actions",
        idea=(
            "Some tool calls should never execute on the model's say-so. Deleting an account, sending money or "
            "emailing a customer needs a human decision, and the confirmation must bind to the exact action the "
            "human saw. The lazy but wrong pattern is a boolean approved flag that any later code can set; the "
            "right pattern is a pending action with a token, a clear summary, and a single-use confirmation. The "
            "host stores the pending action, shows the summary, and executes only when a confirmation arrives "
            "with the matching token. A stale or missing token is a rejection, not a prompt to retry. The model may "
            "propose the action and may even propose the summary, but it must not be the approver. Confirmation "
            "also needs an expiry and a cancellation path, because a pending destructive action left open is a "
            "hazard. Today the first confirmation uses the wrong token and is rejected while the pending action "
            "remains; the second uses the right token and executes. Print both results and note that the rejected "
            "attempt changed nothing. That is the test: a failed confirmation leaves the world exactly as it was. "
            "Later, authorisation adds who is allowed to approve, and auditing records that they did."
        ),
        code=(
            'PENDING = {}\n'
            '\n'
            'def propose(action):\n'
            '    PENDING["token"] = "confirm-1"\n'
            '    PENDING["action"] = action\n'
            '    return {"status": "needs_confirmation", "token": "confirm-1", "action": action}\n'
            '\n'
            'def confirm(token, approved):\n'
            '    if token != PENDING.get("token"):\n'
            '        return {"status": "rejected", "reason": "stale token"}\n'
            '    action = PENDING.pop("action")\n'
            '    PENDING.pop("token", None)\n'
            '    if not approved:\n'
            '        return {"status": "cancelled", "action": action}\n'
            '    return {"status": "executed", "action": action}\n'
            '\n'
            'print(propose({"tool": "delete_account", "user": "u-4"}))\n'
            'print(confirm("confirm-9", True))\n'
            'print(confirm("confirm-1", True))\n'
            '\n'
            'assert "action" not in PENDING\n'
            'print("wrong token rejected; correct token executed once")'
        ),
        variant_b='add a denial path where approved is false and print the cancelled action summary',
        variant_c='store a copy of the action and check that the executed action equals the proposed one',
        mistakes=[
            "Letting the model set an approved flag and treating that as human consent.",
            "Accepting any token, or reusing one token for several dangerous actions.",
            "Leaving a pending destructive action alive after a rejection.",
        ],
        q1=(
            "Why bind confirmation to a single-use token instead of a boolean?",
            "The token ties the approval to one specific pending action and prevents stale or reused consent from executing something else.",
        ),
        homework=(
            "Write `propose(action)` and `confirm(token, approved)` with a pending dict. A wrong token must reject "
            "without changing state, a denial must cancel, and the correct token must execute once. Print all "
            "three results."
        ),
        patterns=["def propose", "def confirm", "PENDING"],
        mapping=(
            "OpenAI and Anthropic models can request a tool but cannot grant permission; human-in-the-loop "
            "confirmation is application logic, and LangChain supports it with interrupts around tools."
        ),
    ),
    115: dict(
        topic="Plan several tool calls",
        idea=(
            "Many requests need more than one tool. The model can propose a plan, but the plan is data: a list of "
            "steps, each with an identifier, a tool, and arguments that may refer to an earlier result. The host "
            "executes the steps in order, resolving references like step 2's id into step 3's argument. This is "
            "the difference between a plan and a pile of calls: dependencies are explicit. Keep identifiers short "
            "and local to the plan, and never let the model invent database ids that it has not seen; it should "
            "refer to a prior step instead. After each step, feed the result into the next resolution. If a step "
            "fails, stop and re-plan rather than improvising around it, because later steps may depend on the "
            "missing value. Bound the number of steps: a plan with fifty calls is usually a sign the task should "
            "be split. Today a hard-coded three-step plan looks up a customer, then their orders, then summarises "
            "those orders. The results are a dict keyed by step id, and a small resolver substitutes references. "
            "Print each resolved step and assert the final summary sees both orders. The output is the trace of a "
            "plan, which The content can be long, but its shape stays simple "
            "and inspectable."
        ),
        code=(
            'def make_plan():\n'
            '    return [\n'
            '        {"id": "1", "tool": "find_customer", "args": {"email": "ana@example.com"}},\n'
            '        {"id": "2", "tool": "list_orders", "args": {"customer": "$1.id"}},\n'
            '        {"id": "3", "tool": "summarise", "args": {"orders": "$2.rows"}},\n'
            '    ]\n'
            '\n'
            'FAKE_RESULTS = {\n'
            '    "1": {"id": "c-9"},\n'
            '    "2": {"rows": [{"total": 40}, {"total": 60}]},\n'
            '}\n'
            '\n'
            'def resolve(value, results):\n'
            '    if isinstance(value, str) and value.startswith("$"):\n'
            '        step, field = value[1:].split(".")\n'
            '        return results[step][field]\n'
            '    return value\n'
            '\n'
            'for step in make_plan():\n'
            '    args = {k: resolve(v, FAKE_RESULTS) for k, v in step["args"].items()}\n'
            '    print(step["id"], step["tool"], args)\n'
            '\n'
            'assert resolve("$2.rows", FAKE_RESULTS)[1]["total"] == 60\n'
            'print("plan steps resolve references to earlier results")'
        ),
        variant_b='add a failure result for step 2 and show that step 3 is skipped rather than run with no data',
        variant_c='topologically sort a plan that lists step 3 before step 1 and print the execution order',
        mistakes=[
            "Letting the model invent ids that no earlier step produced.",
            "Running later steps after a dependency failed.",
            "Emitting an unbounded plan with no step limit or progress check.",
        ],
        q1=(
            "Why store results by step id when executing a plan?",
            "Later steps can reference earlier outputs deterministically, and the whole plan can be traced and replayed.",
        ),
        homework=(
            "Write `make_plan()` and `resolve(value, results)` for a three-step plan where later arguments reference "
            "earlier step outputs. Print each resolved step in order and assert one resolved reference against a "
            "hard-coded result table."
        ),
        patterns=["def make_plan", "def resolve", "$"],
        mapping=(
            "OpenAI and Anthropic support multiple tool calls in one turn, while LangChain agents loop over a "
            "scratchpad; either way the host resolves dependencies and executes the list."
        ),
    ),
    116: dict(
        topic="Choosing between tools",
        idea=(
            "When several tools could fit, choosing is a ranking problem, not a coin flip. The model sees names and "
            "descriptions, so those descriptions are your interface: write them with the words a user will use. "
            "A host-side chooser can score candidate tools by overlap between the request and the description, "
            "then break ties by cost or specificity. Overlap is crude but deterministic and easy to test. The "
            "important part is the threshold: if nothing scores above zero, the correct answer is to ask for "
            "clarification or decline, not to pick the least-bad tool. A tool that cannot help is worse than no "
            "call because it produces a confident wrong answer. Also avoid letting a high-cost or dangerous tool win "
            "on a single keyword; rank dangerous tools lower or require confirmation, which the next lessons "
            "cover. Today three tools with short descriptions compete for three requests. A weather request picks "
            "weather, a currency request picks conversion, and an unrelated request scores zero and returns none. "
            "Print the request, the choice and the score. Reading the scores explains the choice, which is what "
            "makes this debuggable; a black-box choice you cannot explain is hard to trust and hard to fix when it "
            "goes wrong."
        ),
        code=(
            'TOOLS = {\n'
            '    "get_weather": {"desc": "current weather temperature city", "cost": 1},\n'
            '    "search_web": {"desc": "find recent news articles web", "cost": 3},\n'
            '    "convert_currency": {"desc": "convert amount between currencies", "cost": 1},\n'
            '}\n'
            '\n'
            'def choose(request, tools=TOOLS):\n'
            '    words = set(request.lower().split())\n'
            '    scored = []\n'
            '    for name, meta in tools.items():\n'
            '        overlap = len(words & set(meta["desc"].split()))\n'
            '        scored.append((overlap, -meta["cost"], name))\n'
            '    best = max(scored)\n'
            '    if best[0] == 0:\n'
            '        return {"tool": None, "score": 0, "reason": "no useful match"}\n'
            '    return {"tool": best[2], "score": best[0], "reason": "description overlap"}\n'
            '\n'
            'for request in ["weather in pune", "convert 10 usd to eur", "who won the match"]:\n'
            '    print(request, "->", choose(request))\n'
            '\n'
            'assert choose("weather in pune")["tool"] == "get_weather"\n'
            'assert choose("who won the match")["tool"] is None\n'
            'print("no match means ask, not guess")'
        ),
        variant_b='add a tie between two tools and break it with the lower cost, printing the full candidate list',
        variant_c='weight a description match by field name so a city word beats a generic mention',
        mistakes=[
            "Choosing the highest-scoring tool even when every score is zero.",
            "Writing tool descriptions that omit the words users actually say.",
            "Letting a dangerous tool win ties without confirmation or a lower rank.",
        ],
        q1=(
            "What should a chooser do when no tool description matches the request?",
            "Return no tool and ask for clarification rather than calling an irrelevant tool.",
        ),
        homework=(
            "Write `choose(request, tools)` that scores each tool by word overlap with its description, breaks ties "
            "by cost, and returns none below a zero threshold. Print choices for one matching and one unrelated "
            "request."
        ),
        patterns=["def choose", "overlap", "score"],
        mapping=(
            "OpenAI and Anthropic rely on tool names and descriptions for model-side selection; LangChain exposes "
            "tool descriptions the same way, and host-side ranking remains useful for routing and guardrails."
        ),
    ),
    117: dict(
        topic="Authorisation at the tool boundary",
        idea=(
            "Authentication says who is calling; authorisation says what they may do. The tool boundary is the "
            "right place to enforce the second, because it is the last point before a real effect. A system prompt "
            "that says be careful is not a control, and a model that was told the user is an admin is still just "
            "text. The host should look up the caller's scopes from its own trusted store, check that the tool "
            "requires one of them, and deny by default when the tool or scope is unknown. Deny by default matters "
            "because new tools get added and forgetting to register a scope should fail closed. Arguments cannot "
            "grant permission either: a user_id field in the arguments is data, not identity, and trusting it "
            "lets one user act as another. Keep the authorisation check separate from dispatch so it can be tested "
            "without running any tool and reused for every tool. Today two users with different scopes attempt "
            "four calls. Ana can read weather but not delete accounts; Bo can do neither; an unregistered tool is "
            "denied for everyone. Print each decision and assert the denials. The output is a small policy table, "
            "which is exactly what an auditor wants to see."
        ),
        code=(
            'USERS = {\n'
            '    "ana": {"scopes": {"weather:read"}},\n'
            '    "bo": {"scopes": set()},\n'
            '}\n'
            '\n'
            'TOOL_SCOPES = {\n'
            '    "get_weather": "weather:read",\n'
            '    "delete_account": "account:delete",\n'
            '}\n'
            '\n'
            'def authorised(user, tool):\n'
            '    need = TOOL_SCOPES.get(tool)\n'
            '    if need is None or user not in USERS:\n'
            '        return False\n'
            '    return need in USERS[user]["scopes"]\n'
            '\n'
            'cases = [\n'
            '    ("ana", "get_weather"),\n'
            '    ("ana", "delete_account"),\n'
            '    ("bo", "get_weather"),\n'
            '    ("bo", "wipe_disk"),\n'
            ']\n'
            'for user, tool in cases:\n'
            '    print(user, tool, "allowed" if authorised(user, tool) else "denied")\n'
            '\n'
            'assert authorised("ana", "get_weather")\n'
            'assert not authorised("ana", "delete_account")\n'
            'assert not authorised("bo", "wipe_disk")\n'
            'print("unknown tool and missing scope both fail closed")'
        ),
        variant_b='add an admin user whose scope covers account deletion and print the updated decision',
        variant_c='record the required scope in each denial message so the caller knows what is missing',
        mistakes=[
            "Trusting a user_id argument instead of the authenticated caller identity.",
            "Putting permission rules only in the system prompt.",
            "Allowing unknown tools by default because no scope is registered for them.",
        ],
        q1=(
            "Why check authorisation at the tool boundary rather than in the prompt?",
            "The boundary is enforced code before the effect; prompt text can be ignored or overridden by the model.",
        ),
        homework=(
            "Write `authorised(user, tool)` backed by a users dict of scopes and a tool-to-scope table. Deny "
            "unknown users and unknown tools, then print decisions for an allowed call, a missing scope and an "
            "unregistered tool."
        ),
        patterns=["def authorised", "scopes", "TOOL_SCOPES"],
        mapping=(
            "Tool use in OpenAI and Anthropic APIs carries no permissions of its own; application code must bind "
            "the caller identity to allowed tools, as LangChain deployments do with per-user tool sets."
        ),
    ),
    118: dict(
        topic="Auditing tool calls",
        idea=(
            "An audit log answers who called what, with which arguments, and what happened. It is not the same as "
            "a debug log: it is a durable record of decisions, including refusals and failures, kept in order and "
            "written at the boundary. The minimum fields are a sequence number, the caller, the tool, the "
            "arguments, and the outcome. Include a correlation id so a call can be matched to its result and to "
            "the conversation turn. Redact secrets before writing: passwords, tokens and full card numbers should "
            "never land in a log, because logs are copied, shipped and retained far beyond the original request. "
            "Log the denial too; an audit that only records successes cannot show attempted abuse. Use a logical "
            "sequence rather than a wall clock in this offline example, since a counter is deterministic and still "
            "shows order. Keep the record append-only: corrections are new rows, not edits. Real systems add "
            "retention, access control and tamper evidence, but those are deployment concerns around the same "
            "shape. Today you record a weather read and a denied deletion, redact a password field, and print the "
            "rows plus a count. The assertion checks that the secret never appears. That check is the point: if it "
            "fails, the log has become a liability."
        ),
        code=(
            'AUDIT = []\n'
            '\n'
            'def record(user, tool, args, outcome, correlation_id):\n'
            '    safe = {key: ("***" if "password" in key else value) for key, value in args.items()}\n'
            '    row = {\n'
            '        "seq": len(AUDIT) + 1,\n'
            '        "correlation_id": correlation_id,\n'
            '        "user": user,\n'
            '        "tool": tool,\n'
            '        "args": safe,\n'
            '        "outcome": outcome,\n'
            '    }\n'
            '    AUDIT.append(row)\n'
            '    return row\n'
            '\n'
            'record("ana", "get_weather", {"city": "Pune"}, "ok", "turn-12")\n'
            'record("bo", "delete_account", {"user": "u-4", "password": "hunter2"}, "denied", "turn-12")\n'
            '\n'
            'for row in AUDIT:\n'
            '    print(row)\n'
            'print("audited calls:", len(AUDIT))\n'
            '\n'
            'assert AUDIT[1]["args"]["password"] == "***"\n'
            'assert "hunter2" not in str(AUDIT)\n'
            'print("secrets redacted; denials recorded")'
        ),
        variant_b='add a failed tool call row with an error code and assert all three outcomes are present',
        variant_c='add a helper that filters audit rows by correlation id and print one conversation turn',
        mistakes=[
            "Logging only successful calls and losing the denials.",
            "Writing raw passwords or tokens into an append-only store.",
            "Editing old audit rows instead of appending a correction.",
        ],
        q1=(
            "Why should an audit log include denied calls?",
            "Denials reveal attempted misuse and policy gaps, which successes alone can never show.",
        ),
        homework=(
            "Write `record(user, tool, args, outcome, correlation_id)` that appends a redacted row to a list. Log "
            "one success and one denied call containing a password, print every row, and assert the secret is not "
            "present."
        ),
        patterns=["def record", "AUDIT", "redact"],
        mapping=(
            "OpenAI and Anthropic expose tool call ids that make correlation possible; LangChain callbacks provide "
            "hooks, but durable redacted audit storage remains application responsibility."
        ),
    ),
    119: dict(
        topic="Review: tools and function calling checklist",
        idea=(
            "The phase ends with a checklist, because tool calling fails in ordinary, repeatable ways. A call "
            "should have a schema, validated arguments, a dispatch route, a linked result message, a recoverable "
            "error shape, a retry policy for transient failures, a timeout budget, idempotency for writes, human "
            "confirmation before dangerous effects, a bounded plan for multi-step work, an explainable tool "
            "choice, an authorisation check at the boundary, and an audit row. That is thirteen items, and each "
            "one is cheap to test in isolation but expensive to discover missing in production. Today you encode "
            "the checklist as data: a dict of names to predicate functions, run them against one sample call, and "
            "print the failures. The sample is deliberately incomplete, so the output names what to fix instead "
            "of declaring success. A checklist that always passes is not a checklist. Keep the predicates small "
            "and total: they should return a boolean, never raise on a missing field. In a real system these run "
            "as tests, as a pre-deploy gate, or as runtime guards around high-risk tools. Run them early. The review is not "
            "ceremony; it is the difference between a demo that calls functions and a tool system you can operate."
        ),
        code=(
            'def build_call():\n'
            '    return {\n'
            '        "name": "send_email",\n'
            '        "arguments": {"to": "ana@example.com", "body": "hello"},\n'
            '        "approved": True,\n'
            '        "idempotency_key": "mail-1",\n'
            '        "authorised": True,\n'
            '        "audited": False,\n'
            '    }\n'
            '\n'
            'CHECKS = {\n'
            '    "schema": lambda c: c.get("name") and set(c.get("arguments", {})) == {"to", "body"},\n'
            '    "authorised": lambda c: c.get("authorised") is True,\n'
            '    "confirmed": lambda c: c.get("approved") is True,\n'
            '    "idempotent": lambda c: bool(c.get("idempotency_key")),\n'
            '    "audited": lambda c: c.get("audited") is True,\n'
            '}\n'
            '\n'
            'call = build_call()\n'
            'failed = [name for name, check in CHECKS.items() if not check(call)]\n'
            'print("checks:", len(CHECKS))\n'
            'print("failed:", failed or "none")\n'
            'print("ready" if not failed else "fix before shipping")\n'
            '\n'
            'assert failed == ["audited"]\n'
            'print("a checklist is only useful when it can fail")'
        ),
        variant_b='add checks for retry policy, timeout budget and bounded plan, and show the expanded failures',
        variant_c='run the checklist over three sample calls and print which call is furthest from ready',
        mistakes=[
            "Treating the checklist as documentation instead of executable checks.",
            "Writing predicates that raise on a missing field, stopping the whole review.",
            "Shipping when the only failure is the audit or confirmation gate.",
        ],
        q1=(
            "What is the value of encoding the tool checklist as predicates?",
            "It turns review into tests and runtime guards, so missing safeguards fail visibly instead of being remembered.",
        ),
        homework=(
            "Write `review(call, checks)` that runs a dict of predicate functions, returns the failed names, and "
            "prints a ready or fix message. Test it with one complete sample call and one missing the audit and "
            "confirmation fields."
        ),
        patterns=["def review", "checks", "failed"],
        mapping=(
            "OpenAI and Anthropic tool use and LangChain tool executors all converge on the same operational "
            "checklist: schema, validation, permission, confirmation, idempotency, limits and audit."
        ),
    ),
})
