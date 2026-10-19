"""API Building phase 6, days 150-164: testing, documentation and operations.

Every example runs offline against in-memory requests, responses and fixed
fixtures. No server, no network, no test framework and no current time: the
learner can run each snippet and see the same output every time.
"""

PHASE = (
    "Testing, Docs and Operations",
    "Prove an API works, describe it honestly, and keep it healthy after deployment.",
    {
        150: dict(
            topic="Unit testing handlers",
            idea=(
                "Testing a handler has nothing to do with starting a server. The handler is a function: give it a "
                "request dictionary, read the status and body it returns, and compare both with what the contract "
                "promises. That is a unit test, and it runs in milliseconds because no socket, no port and no "
                "framework lifecycle are involved. The discipline is arrange, act, assert: build a fixed request, "
                "call the function once, and make each assertion name one promise. A test that only checks the "
                "status code is half a test; the body is part of the response contract. Keep fixtures literal so a "
                "failure points at behavior rather than at a clever helper. Write one test for the change you "
                "just made and run the whole file after every edit. Tests also document intent: a new teammate "
                "reads the rejected case and learns that a missing title means a 400, without opening the handler. "
                "The goal is not a large suite; it is a suite whose failures are trustworthy, fast and specific "
                "enough to tell you which promise you broke. Small functions with explicit inputs make every one "
                "of those properties easier to keep. A broken test should send you to one small function, not a whole stack."
            ),
            code=(
                'def create_book(request):\n'
                '    payload = request.get("json") or {}\n'
                '    if "title" not in payload:\n'
                '        return 400, {"error": "title required"}\n'
                '    return 201, {"id": 1, "title": payload["title"]}\n'
                '\n'
                'def test_created():\n'
                '    status, body = create_book({"json": {"title": "Dune"}})\n'
                '    assert status == 201\n'
                '    assert body["title"] == "Dune"\n'
                '    return "created"\n'
                '\n'
                'def test_rejected():\n'
                '    status, body = create_book({"json": {}})\n'
                '    assert status == 400\n'
                '    assert body["error"] == "title required"\n'
                '    return "rejected"\n'
                '\n'
                'results = [test_created(), test_rejected()]\n'
                'print("passed:", results)\n'
                'print("count:", len(results))'
            ),
            variant_b='a request body {"title": "Emma", "price": 12.5} (an extra field is ignored)',
            variant_c='a request body {"price": 12.5} (the title is missing, so the 400 branch runs)',
            mistakes=[
                "Asserting only the status and never the response body.",
                "Sharing one mutable request dictionary between tests.",
                "Calling a private helper instead of the handler the client hits.",
            ],
            q1=(
                "What belongs in a unit test of a handler?",
                "A fixed request, one call to the handler, and assertions on both the returned status and body.",
            ),
            homework=(
                "Write `test_read_book(store, book_id)` that calls a handler directly with a fixture store and "
                "asserts the status and body for an existing id and a missing id. Run it on those two cases, print "
                "both results, and comment which assertion proves the contract rather than the implementation."
            ),
            patterns=["def test_", "assert", "print("],
            mapping=(
                "In pytest or unittest this function becomes a test discovered by name, but the shape is the same: "
                "arrange a fixture, act on the handler, assert on the response."
            ),
        ),
        151: dict(
            topic="Testing with a real client",
            idea=(
                "A unit test calls the handler directly, which means it skips routing, header parsing and response "
                "serialization — exactly the layers where integration bugs live. A test client sends a method and "
                "path through the same routing table the server uses and returns a response object with status, "
                "headers and a decoded body. That single extra layer catches the mistakes unit tests cannot see: a "
                "route registered under the wrong verb, a path parameter parsed as a string, a 404 that returns "
                "HTML when the client expected JSON. In pytest the tool is usually TestClient or httpx; the shape "
                "is the same in every stack. Test the public contract, not private helpers, because clients only "
                "know URLs and payloads. Seed the store before the client call and assert on the response, not on "
                "the database. Keep one client per test module and reset state between tests. When a route "
                "changes, the client test is the alarm that tells you a client-facing promise moved. Run it after "
                "every route change, and keep the cases small: list, create and an unknown path cover most "
                "routing mistakes cheaply. If the client test and the unit test disagree, believe the client test. The client is the closest you can get to a real consumer without a network."
            ),
            code=(
                'ROUTES = {\n'
                '    ("GET", "/books"): lambda: (200, [{"id": 1, "title": "Dune"}]),\n'
                '    ("POST", "/books"): lambda: (201, {"id": 2, "title": "Emma"}),\n'
                '}\n'
                '\n'
                'def client(method, path):\n'
                '    handler = ROUTES.get((method, path))\n'
                '    if handler is None:\n'
                '        return {"status": 404, "json": {"error": "not found"}}\n'
                '    status, payload = handler()\n'
                '    return {"status": status, "json": payload}\n'
                '\n'
                'def test_list():\n'
                '    response = client("GET", "/books")\n'
                '    assert response["status"] == 200\n'
                '    assert isinstance(response["json"], list)\n'
                '    return "list ok"\n'
                '\n'
                'def test_unknown_path():\n'
                '    response = client("GET", "/authors")\n'
                '    assert response["status"] == 404\n'
                '    assert response["json"]["error"] == "not found"\n'
                '    return "404 ok"\n'
                '\n'
                'print("routes:", sorted(ROUTES))\n'
                'print("tests:", [test_list(), test_unknown_path()])\n'
                'print("unknown route:", client("GET", "/authors"))'
            ),
            variant_b='send POST to /books and assert the 201 plus the new title',
            variant_c='send DELETE to /books and observe that the router has no such method',
            mistakes=[
                "Asserting on the handler return value instead of the client response.",
                "Forgetting to reset the store, so one test sees another test's writes.",
                "Testing a private function when the bug is in the route registration.",
            ],
            q1=(
                "What does a test client check that a direct handler call cannot?",
                "It checks routing, method and path matching, status mapping and response serialization along the way.",
            ),
            homework=(
                "Write `exercise_routes(client, cases)` that loops over a list of (method, path, expected_status) "
                "tuples, calls the client, and returns the failures. Run it on a case list with a valid route and "
                "an unknown route, print both responses, and comment where routing rather than logic decided the "
                "status."
            ),
            patterns=["client(", "assert", "status"],
            mapping=(
                "Starlette and FastAPI ship TestClient, Flask ships a test client, and Go has httptest. Each one "
                "drives the real router without binding a production port."
            ),
        ),
        152: dict(
            topic="Fixtures and test data",
            idea=(
                "Fixtures are the setup a test needs before it can assert: a database row, a logged-in user, a "
                "store with two books. Written badly they become a second codebase. Written well they are small "
                "functions with explicit inputs that return fresh data on every call. The failure mode to watch is "
                "shared mutable state: one module-level dictionary reused across tests means the first test that "
                "appends a role changes what every later test sees, and the suite starts passing or failing "
                "depending on order. Either build a new fixture per test, or deep-copy the shared one, and assert "
                "that two calls are independent. Prefer semantic builders such as a function that accepts only the "
                "fields a test cares about and fills the rest with fixed defaults, so the test reads as a "
                "statement about behavior rather than a wall of boilerplate. Keep identifiers fixed and "
                "recognizable, never random, so failures are reproducible. Test data should also cover the "
                "interesting shapes: empty list, one item, duplicate title. A fixture is not a fixture if the "
                "reader cannot tell what is in it, and a builder that takes twenty arguments is a sign the test is "
                "asserting too many things at once."
            ),
            code=(
                'def new_user(name="Ada", roles=None):\n'
                '    return {"name": name, "roles": list(roles or [])}\n'
                '\n'
                'def test_admin_role():\n'
                '    user = new_user()\n'
                '    user["roles"].append("admin")\n'
                '    assert user["roles"] == ["admin"]\n'
                '    return user\n'
                '\n'
                'def test_independent_fixtures():\n'
                '    first = new_user()\n'
                '    second = new_user()\n'
                '    first["roles"].append("admin")\n'
                '    assert second["roles"] == []\n'
                '    return second\n'
                '\n'
                'shared = new_user("Grace", ["reader"])\n'
                'shared["roles"].append("editor")\n'
                'print("built user:", test_admin_role())\n'
                'print("fresh user:", test_independent_fixtures())\n'
                'print("shared before:", shared)\n'
                'assert new_user()["roles"] is not new_user()["roles"]\n'
                'print("each fixture owns its list")'
            ),
            variant_b='new_user(roles=["reader"]) and append a second role',
            variant_c='build two users at once and mutate only the first',
            mistakes=[
                "Reusing a module-level dictionary so tests leak state into each other.",
                "Using random identifiers that make a failure impossible to reproduce.",
                "Passing twenty fields when the test only depends on two of them.",
            ],
            q1=(
                "Why should a fixture builder return fresh mutable data on every call?",
                "So a test that mutates its fixture cannot change the state another test will observe.",
            ),
            homework=(
                "Write `book_factory(title, price=9.99)` that returns a fresh record with fixed author and stock "
                "defaults, then write two tests that mutate their own record. Run both, print the two records, and "
                "comment how the factory prevented the mutation from leaking between cases."
            ),
            patterns=["def ", "return", "assert"],
            mapping=(
                "pytest fixtures, factory functions and setUp methods all solve the same problem: give a test a "
                "known starting state that no other test can quietly change."
            ),
        ),
        153: dict(
            topic="Error-path tests",
            idea=(
                "Happy-path tests prove the feature exists; error-path tests prove it is safe. Every endpoint has "
                "a set of predictable failures: a missing required field, a value of the wrong type, an unknown "
                "identifier, a duplicate that violates uniqueness, a dependency that is down. Each should have a "
                "test that asserts the status code, the error body shape and the absence of internal details such "
                "as stack traces, SQL or file paths. A structured error like a body with an error key is a "
                "contract the client can branch on; a prose sentence is not. Test that validation happens before "
                "any write, so a rejected request leaves the store unchanged. Test the boundary: the largest "
                "allowed value, the empty string, the identifier that does not exist. These cases are cheap to "
                "write and expensive to miss, because the first person to hit them is usually a real client at an "
                "inconvenient hour. Organize them beside the success test for the same handler so the contract is "
                "visible in one place. The habit to build is simple: whenever you add a branch that can return an "
                "error, add the case that drives it and one assertion per promise, including the promise that "
                "nothing was persisted."
            ),
            code=(
                'STORE = {1: "Dune"}\n'
                '\n'
                'def get_book(store, book_id):\n'
                '    if book_id not in store:\n'
                '        return 404, {"error": "book not found"}\n'
                '    return 200, {"id": book_id, "title": store[book_id]}\n'
                '\n'
                'def create_book(store, payload):\n'
                '    if not payload.get("title"):\n'
                '        return 400, {"error": "title required"}\n'
                '    if payload["title"] in store.values():\n'
                '        return 409, {"error": "title already exists"}\n'
                '    return 201, {"id": 2, "title": payload["title"]}\n'
                '\n'
                'status, body = get_book(STORE, 99)\n'
                'assert status == 404\n'
                'assert body == {"error": "book not found"}\n'
                'print("missing book:", status, body)\n'
                '\n'
                'assert create_book(STORE, {})[0] == 400\n'
                'assert create_book(STORE, {"title": "Dune"})[0] == 409\n'
                'assert create_book(STORE, {"title": "Emma"})[0] == 201\n'
                'print("validation and conflict paths covered")\n'
                'print("store unchanged:", STORE)'
            ),
            variant_b='request the id 1, which exists, and assert the 200 path',
            variant_c='create a duplicate title and then assert the store still has one copy',
            mistakes=[
                "Testing only the status and ignoring the error body shape.",
                "Letting a rejected request write to the store before validation.",
                "Returning internal exception text to the client.",
            ],
            q1=(
                "Why assert the store after a rejected write?",
                "Because a 400 or 409 is only safe if the failed request left no partial state behind.",
            ),
            homework=(
                "Write `assert_error(response, status, key)` that checks the status code and that the body has a "
                "string under the given key. Run it on a 404 missing-book response and a 400 missing-title "
                "response, print both, and comment which assertion would catch a leaked traceback."
            ),
            patterns=["assert", "return", "error"],
            mapping=(
                "Error-path tests are what make an API predictable under bad input; pytest parametrisation is a "
                "common way to keep the happy and failing cases side by side."
            ),
        ),
        154: dict(
            topic="Contract tests",
            idea=(
                "A contract test checks the shape of what the API promises, not the business outcome of one call. "
                "The contract includes which fields exist, their types, which are required, which status codes "
                "appear and how errors are structured. If the response gains, loses or renames a field, a client "
                "can break even when the handler still returns 200. Contract tests catch that drift before "
                "deployment. Keep the schema in one place and run every representative response through a checker "
                "that collects all problems instead of stopping at the first, so a refactor reports the full list. "
                "Version the schema with the route: v1 and v2 can differ, and the test for v1 keeps protecting old "
                "clients while v2 evolves. Be careful about what you freeze: field order and free-text error "
                "messages are usually not promises, while names, types and nullability are. A contract test is "
                "also documentation that runs, which makes it more trustworthy than a wiki page nobody updates. "
                "Add it to continuous integration and treat a failure as a release blocker, because a broken "
                "contract reaches every client at once. When the contract must change, update the version and the "
                "test together, never the test alone. Write the schema down before the handler grows, not after a client complains."
            ),
            code=(
                'SCHEMA = {\n'
                '    "required": ["id", "title", "price"],\n'
                '    "types": {"id": int, "title": str, "price": float},\n'
                '}\n'
                '\n'
                'def check_contract(payload, schema):\n'
                '    problems = []\n'
                '    for field in schema["required"]:\n'
                '        if field not in payload:\n'
                '            problems.append("missing " + field)\n'
                '    for field, kind in schema["types"].items():\n'
                '        if field in payload and not isinstance(payload[field], kind):\n'
                '            problems.append(field + " is not " + kind.__name__)\n'
                '    return problems\n'
                '\n'
                'good = {"id": 1, "title": "Dune", "price": 9.99}\n'
                'bad = {"id": "1", "price": "9.99"}\n'
                'extra = {"id": 2, "title": "Emma", "price": 12.5, "isbn": "x"}\n'
                '\n'
                'print("good:", check_contract(good, SCHEMA) or "valid")\n'
                'print("bad:", check_contract(bad, SCHEMA))\n'
                'print("extra field accepted:", check_contract(extra, SCHEMA) or "valid")\n'
                'assert check_contract(good, SCHEMA) == []\n'
                'assert "amount is not float" not in check_contract(good, SCHEMA)\n'
                'print("v1 contract holds")'
            ),
            variant_b='check a response where price is an int (9) rather than a float',
            variant_c='check a v2 response that adds an author field and keeps every v1 field',
            mistakes=[
                "Checking only required keys and never their types.",
                "Freezing field order or an exact error sentence as part of the contract.",
                "Updating the test to match a breaking handler change instead of versioning.",
            ],
            q1=(
                "What does a contract test protect that a business-logic test does not?",
                "The response shape clients depend on: field names, types, required keys and error structure.",
            ),
            homework=(
                "Write `check_contract(payload, schema)` that returns every missing field and type mismatch as a "
                "list. Run it on a valid response and on one with a string id, print both lists, and comment which "
                "problem a client would notice first."
            ),
            patterns=["def ", "assert", "return"],
            mapping=(
                "OpenAPI schemas, JSON Schema and Pact all formalise this idea; a contract test is the cheapest "
                "version you can run before adopting one of those tools."
            ),
        ),
        155: dict(
            topic="Coverage that matters",
            idea=(
                "Coverage measures which lines executed, not which promises were checked. A suite can reach one "
                "hundred percent by calling every handler and asserting nothing, and it will still ship broken "
                "responses. The useful question is whether every branch that can produce a different outcome has "
                "at least one assertion attached to it. A handler with a success path and a validation path has "
                "two behaviors, so it needs two tests and two assertions. Look for branches that only appear on "
                "failure: missing rows, duplicate keys, dependency timeouts. Those are the lines that tend to be "
                "unexecuted and the ones that page someone at night. Branch coverage is a better signal than line "
                "coverage because it distinguishes an if that was taken from one that was skipped. Treat the "
                "number as a smoke detector, not a score: a drop is worth investigating, a high number is not "
                "proof of quality. The practical move is to open the report, find the uncovered error branch, and "
                "write the test that drives it. Then check that the test fails when you deliberately break the "
                "handler, because a test that never fails has never proved anything. Coverage is a map of what you have exercised, not a certificate of correctness."
            ),
            code=(
                'ALL_LINES = {"entry", "success", "error"}\n'
                '\n'
                'def handler(status):\n'
                '    covered = {"entry"}\n'
                '    if status == "ok":\n'
                '        covered.add("success")\n'
                '        return 200, covered\n'
                '    covered.add("error")\n'
                '    return 400, covered\n'
                '\n'
                'def exercise(statuses):\n'
                '    got = set()\n'
                '    for status in statuses:\n'
                '        _, lines = handler(status)\n'
                '        got |= lines\n'
                '    return got\n'
                '\n'
                'happy_only = exercise(["ok"])\n'
                'both = exercise(["ok", "bad"])\n'
                '\n'
                'print("happy-only lines:", sorted(happy_only))\n'
                'print("uncovered:", sorted(ALL_LINES - happy_only))\n'
                'print("with both cases:", sorted(both))\n'
                'assert "error" not in happy_only\n'
                'assert "error" in both\n'
                'assert ALL_LINES - both == set()\n'
                'print("error branch now exercised")'
            ),
            variant_b='run only the error case and list which success line stays uncovered',
            variant_c='add a third branch for a missing resource and see coverage fall until it is tested',
            mistakes=[
                "Calling every handler without asserting any response.",
                "Chasing a percentage instead of the uncovered error branch.",
                "Counting a test as coverage when its assertion can never fail.",
            ],
            q1=(
                "Why is an executed line not the same as a covered behavior?",
                "Execution only proves the line ran; the behavior is covered only when a test asserts what that branch produced.",
            ),
            homework=(
                "Write `coverage_gaps(all_lines, statuses)` that runs the handler over the given statuses and "
                "returns the lines never executed. Run it with only the happy case and with both cases, print the "
                "two gap sets, and comment which error branch the first run missed."
            ),
            patterns=["assert", "set(", "print("],
            mapping=(
                "Coverage.py reports line and branch coverage for pytest runs; use it to find untested failure "
                "paths, then add assertions rather than empty calls."
            ),
        ),
        156: dict(
            topic="OpenAPI documentation",
            idea=(
                "An OpenAPI document is a machine-readable description of your API: paths, methods, parameters, "
                "request bodies, response codes and schemas. Once it exists, tools can render interactive docs, "
                "generate typed clients, mock servers and lint breaking changes. The point is not the pretty page; "
                "it is that the description and the implementation are checked against each other. Write the "
                "document as data, keep it in version control, and add a test that every route in the router "
                "appears in the document and every documented operation declares at least one response. Drift is "
                "the enemy: a handler that starts returning 409 without documenting it is invisible to clients "
                "until they hit it. Describe errors as carefully as success, because that is where integrators "
                "spend their time. Schemas should name types and required fields, and examples should be valid. In "
                "FastAPI the document is generated from type hints, which reduces drift but does not remove the "
                "need to review it. In hand-written frameworks the document is a separate artifact and deserves "
                "its own test. Treat the spec as part of the public contract: changing it is a product decision, "
                "not a formatting detail someone can slip into a refactor. A stale document is worse than none, because it teaches the wrong contract."
            ),
            code=(
                'SPEC = {\n'
                '    "openapi": "3.1.0",\n'
                '    "paths": {\n'
                '        "/books": {\n'
                '            "get": {"responses": {"200": {"description": "list books"}}},\n'
                '            "post": {\n'
                '                "responses": {\n'
                '                    "201": {"description": "created"},\n'
                '                    "400": {"description": "invalid body"},\n'
                '                    "409": {"description": "duplicate title"},\n'
                '                }\n'
                '            },\n'
                '        }\n'
                '    },\n'
                '}\n'
                '\n'
                'ROUTES = {("GET", "/books"), ("POST", "/books")}\n'
                '\n'
                'def documented_routes(spec):\n'
                '    found = set()\n'
                '    for path, operations in spec["paths"].items():\n'
                '        for method in operations:\n'
                '            found.add((method.upper(), path))\n'
                '    return found\n'
                '\n'
                'for path, operations in SPEC["paths"].items():\n'
                '    for method, operation in operations.items():\n'
                '        assert "responses" in operation, (method, path)\n'
                '\n'
                'print("openapi:", SPEC["openapi"])\n'
                'print("documented:", sorted(documented_routes(SPEC)))\n'
                'print("missing from docs:", sorted(ROUTES - documented_routes(SPEC)) or "none")\n'
                'assert documented_routes(SPEC) == ROUTES\n'
                'print("every route is documented")'
            ),
            variant_b='remove the 409 response from the POST operation and watch the missing response test',
            variant_c='add GET /books/{id} to the router without touching the spec',
            mistakes=[
                "Documenting only success responses and leaving errors implicit.",
                "Maintaining the spec by hand without a test that routes and docs agree.",
                "Publishing examples that do not validate against the declared schema.",
            ],
            q1=(
                "What makes an OpenAPI document trustworthy?",
                "A test that compares it with the real routes and response shapes so drift fails the build.",
            ),
            homework=(
                "Write `missing_routes(spec, routes)` that returns the (method, path) pairs present in the router "
                "but absent from the spec. Run it on a matching pair and on a router with an extra endpoint, print "
                "both results, and comment which change would break a generated client."
            ),
            patterns=["def ", "assert", "paths"],
            mapping=(
                "FastAPI generates an OpenAPI schema from type hints and serves it at /docs; Flask and Django "
                "usually add a spec package, but the drift test is your responsibility either way."
            ),
        ),
        157: dict(
            topic="Logging and metrics",
            idea=(
                "Logs and metrics answer different questions. A log line tells you what happened in one request; "
                "a metric tells you how often something happens across all requests. Both need structure. A "
                "useful log record is JSON with a request identifier, method, path, status, duration and the user "
                "or tenant when it is safe to include. Never log passwords, tokens, full card numbers or raw "
                "request bodies that may contain them. The request identifier is what lets you follow one call "
                "across services and match it to the client report. Metrics are cheap counters and histograms: "
                "requests by route and status, latency buckets, queue depth, dependency failures. Keep labels "
                "low-cardinality, because a label with a user identifier will explode the time-series database. "
                "Emit them at the edge so every route is covered without editing each handler. In tests, assert "
                "that a successful call increments the success counter and that a rejected call increments the "
                "client-error counter, using fixed inputs so the expected values are exact. Logging is not "
                "debugging by print: if a message does not help an operator decide something, it is noise that "
                "costs money and hides the signal. Keep the field names stable so queries and dashboards survive a refactor."
            ),
            code=(
                'import json\n'
                '\n'
                'COUNTERS = {}\n'
                '\n'
                'def log_request(request_id, method, path, status, ms):\n'
                '    key = str(status)\n'
                '    COUNTERS[key] = COUNTERS.get(key, 0) + 1\n'
                '    record = {\n'
                '        "rid": request_id,\n'
                '        "method": method,\n'
                '        "path": path,\n'
                '        "status": status,\n'
                '        "ms": ms,\n'
                '    }\n'
                '    return json.dumps(record, sort_keys=True)\n'
                '\n'
                'lines = [\n'
                '    log_request("req-1", "GET", "/books", 200, 12),\n'
                '    log_request("req-2", "POST", "/books", 201, 31),\n'
                '    log_request("req-3", "POST", "/books", 400, 8),\n'
                ']\n'
                'print("\\n".join(lines))\n'
                'print("counters:", dict(sorted(COUNTERS.items())))\n'
                'print("client errors:", COUNTERS.get("400", 0))\n'
                'assert COUNTERS == {"200": 1, "201": 1, "400": 1}\n'
                'assert "password" not in lines[1]\n'
                'print("log fields and counters verified")'
            ),
            variant_b='log a 500 response and confirm the error counter increases by one',
            variant_c='add a duration field in milliseconds and check the JSON still parses',
            mistakes=[
                "Logging the raw request body, which may contain a password or token.",
                "Using a user id as a metric label and creating unbounded cardinality.",
                "Writing only free-text lines that no query can group by route or status.",
            ],
            q1=(
                "Why must log fields be structured and low-cardinality labels be used in metrics?",
                "Structured fields make logs queryable; bounded labels keep metrics affordable and aggregatable.",
            ),
            homework=(
                "Write `log_request(request_id, method, path, status, ms)` that returns one JSON line and updates a "
                "counter dict. Run it on a success and a client error, print both lines and the counters, and "
                "comment which field would let you trace one request across services."
            ),
            patterns=["json.", "assert", "print("],
            mapping=(
                "Prometheus scrapes counters and histograms, while structured JSON logs flow to a log store; both "
                "systems need stable field names to join on a request id."
            ),
        ),
        158: dict(
            topic="Health checks and alerts",
            idea=(
                "Health checks are how the platform decides whether your process should receive traffic. Liveness "
                "asks whether the process is alive; readiness asks whether it can serve requests right now. "
                "Confusing them causes outages: a process that is alive but cannot reach its database should fail "
                "readiness and be removed from the load balancer, not be killed and restarted in a loop. A "
                "readiness check should verify the dependencies that matter on the request path and finish "
                "quickly, with a short timeout, so a slow dependency does not hang the probe. Return a small "
                "structured body naming each dependency and its state, but do not expose credentials or internal "
                "addresses. Alerts are separate from health checks. A health check reports state on demand; an "
                "alert fires when a symptom crosses a threshold for long enough to matter. Alert on user-visible "
                "symptoms such as error rate or latency, not on every CPU spike, and include a threshold, a "
                "duration and a clear owner. Test the unhealthy branch by injecting a failing dependency and "
                "asserting that readiness flips while liveness stays true. That test is the difference between a "
                "probe that works and one that has never been exercised. A probe that has never failed in a test is a probe nobody should trust."
            ),
            code=(
                'def health(checks):\n'
                '    failed = sorted(name for name, ok in checks.items() if not ok)\n'
                '    return {\n'
                '        "live": True,\n'
                '        "ready": not failed,\n'
                '        "failed": failed,\n'
                '    }\n'
                '\n'
                'def should_alert(error_rate, threshold=0.05, sustained=True):\n'
                '    return sustained and error_rate > threshold\n'
                '\n'
                'healthy = health({"db": True, "cache": True})\n'
                'degraded = health({"db": False, "cache": True})\n'
                '\n'
                'print("healthy:", healthy)\n'
                'print("degraded:", degraded)\n'
                'print("alert at 0.08:", should_alert(0.08))\n'
                'print("alert at 0.01:", should_alert(0.01))\n'
                'assert healthy["ready"] is True\n'
                'assert degraded["ready"] is False\n'
                'assert degraded["failed"] == ["db"]\n'
                'assert degraded["live"] is True\n'
                'assert should_alert(0.08) and not should_alert(0.01)\n'
                'print("readiness flips while liveness stays true")'
            ),
            variant_b='mark the cache as failed and confirm readiness is false but liveness is true',
            variant_c='evaluate a one-minute error spike that does not last long enough to alert',
            mistakes=[
                "Killing a live process because a dependency is temporarily unavailable.",
                "Letting readiness perform an expensive query without a timeout.",
                "Alerting on every CPU spike instead of a sustained user-visible symptom.",
            ],
            q1=(
                "Why should a missing database fail readiness rather than liveness?",
                "The process is still alive, so restarting it will not help; removing it from traffic lets other instances serve.",
            ),
            homework=(
                "Write `health_report(checks)` that returns live, ready and the sorted failed dependency names. Run "
                "it on all-healthy checks and on a case where the database fails, print both reports, and comment "
                "which field the load balancer should read."
            ),
            patterns=["def ", "assert", "ready"],
            mapping=(
                "Kubernetes uses liveness and readiness probes, load balancers consume readiness, and Prometheus "
                "alert rules add the threshold and duration that turn a signal into a page."
            ),
        ),
        159: dict(
            topic="Deploying an API",
            idea=(
                "Deployment is a sequence of decisions, not a single command. Build an immutable artifact, apply "
                "configuration from the environment, run migrations in a backward-compatible order, start the new "
                "version, check its health, and only then shift traffic. If health fails, roll back to the "
                "previous artifact instead of debugging forward on the production path. A rolling deployment "
                "replaces instances gradually so capacity stays available; blue-green runs two environments and "
                "switches traffic at once; canary sends a small share first and watches error rate and latency. "
                "Any of them is safe only if the release is observable and reversible. The smoke test after deploy "
                "should exercise one real read and one real write through the public interface, because a process "
                "that started is not necessarily serving. Keep the rollback plan written before the deploy, "
                "including the database step, since schema changes are the part that cannot always be undone by "
                "swapping artifacts. Record which version is live and who approved it. The goal is boring "
                "releases: small, frequent, measured and easy to reverse. Today you model that sequence and watch "
                "a failed health check trigger the rollback branch instead of a long night of improvisation. Small releases shrink the blast radius and make the recovery path obvious."
            ),
            code=(
                'STEPS = ["build", "migrate", "start"]\n'
                '\n'
                'def deploy(version, health_ok):\n'
                '    log = []\n'
                '    for step in STEPS:\n'
                '        log.append((version, step, "done"))\n'
                '    if not health_ok:\n'
                '        log.append((version, "rollback", "restored"))\n'
                '        return log, "rolled back"\n'
                '    log.append((version, "smoke", "passed"))\n'
                '    return log, "live"\n'
                '\n'
                'failed_log, failed_state = deploy("v2", False)\n'
                'for row in failed_log:\n'
                '    print(row)\n'
                'print("state:", failed_state)\n'
                '\n'
                'live_log, live_state = deploy("v3", True)\n'
                'print("---")\n'
                'print("state:", live_state, "| steps:", len(live_log))\n'
                'assert failed_state == "rolled back"\n'
                'assert failed_log[-1][1] == "rollback"\n'
                'assert live_state == "live"\n'
                'print("health gate decided the outcome")'
            ),
            variant_b='run the deploy with health true and confirm the smoke step runs',
            variant_c='move migrate after start and explain why that order is unsafe',
            mistakes=[
                "Switching all traffic before running any smoke check.",
                "Treating a schema change as something a rollback can always undo.",
                "Debugging the new version in production without a written rollback path.",
            ],
            q1=(
                "What should happen when the new version fails its health check?",
                "Traffic should stay on or return to the previous version, and the deploy should report a rollback rather than continue.",
            ),
            homework=(
                "Write `deploy(version, health_ok)` that returns a step log and a final state, including a rollback "
                "step on failure. Run it on a failing release and a healthy one, print both logs, and comment "
                "which step must never be skipped before traffic moves."
            ),
            patterns=["def ", "rollback", "assert"],
            mapping=(
                "Kubernetes rolling updates, blue-green switchovers and canary releases all implement this same "
                "health-gated, reversible sequence with different traffic mechanics."
            ),
        ),
        160: dict(
            topic="Containers and config",
            idea=(
                "A container packages your application and its runtime, but configuration must stay outside the "
                "image. The same image should run in staging and production with different environment variables, "
                "which is the core of twelve-factor configuration. Bake in defaults for safe values such as port "
                "and log level, and require secrets explicitly so a missing value fails at startup rather than at "
                "the first request. Never copy an environment file containing real secrets into the image or the "
                "repository; inject it at runtime and keep it out of logs. Keep the image small and the process in "
                "the foreground so the platform can send signals and read logs. Add a health check that matches "
                "the readiness probe, and run as a non-root user. Configuration parsing deserves a test: one case "
                "with a complete environment, one missing a required secret, and one with an invalid port. The "
                "parser should return a clear list of problems, not a stack trace. When the container starts, log "
                "the resolved configuration with secret values redacted. That line is the fastest way to answer "
                "the question every incident begins with: what settings was this process actually using? Without "
                "it, every diagnosis starts with a guess. Keep the environment names identical across stages so the same config code runs everywhere."
            ),
            code=(
                'DEFAULTS = {"PORT": "8000", "LOG_LEVEL": "info"}\n'
                'REQUIRED = ["SECRET_KEY"]\n'
                '\n'
                'def load_config(env, defaults=DEFAULTS, required=REQUIRED):\n'
                '    config = dict(defaults)\n'
                '    for key, value in env.items():\n'
                '        config[key] = value\n'
                '    missing = [key for key in required if not config.get(key)]\n'
                '    if "PORT" in config and not config["PORT"].isdigit():\n'
                '        missing.append("PORT must be numeric")\n'
                '    return config, missing\n'
                '\n'
                'complete, problems = load_config(\n'
                '    {"APP_ENV": "prod", "PORT": "9000", "SECRET_KEY": "fixed-demo-key"}\n'
                ')\n'
                'print("config:", complete)\n'
                'print("problems:", problems)\n'
                '\n'
                'incomplete, problems = load_config({"APP_ENV": "prod", "PORT": "bad"})\n'
                'print("incomplete problems:", problems)\n'
                'assert problems == ["SECRET_KEY", "PORT must be numeric"]\n'
                'assert complete["PORT"] == "9000"\n'
                'print("startup validation fails fast")'
            ),
            variant_b='pass PORT=70000 and decide whether the parser should reject it',
            variant_c='provide SECRET_KEY but omit LOG_LEVEL and show the default taking effect',
            mistakes=[
                "Baking a real secret into the image or committing it to the repository.",
                "Starting with missing configuration and failing on the first request instead of at boot.",
                "Running the process in the background so the container stops receiving signals.",
            ],
            q1=(
                "Why should a missing secret fail at startup rather than on the first request?",
                "A misconfigured instance should never join the load balancer; failing fast keeps the broken config out of traffic.",
            ),
            homework=(
                "Write `load_config(env, defaults, required)` that merges values, applies defaults and returns the "
                "config plus a list of missing keys. Run it on a complete environment and a partial one, print both "
                "results, and comment which values are safe to default and which must be required."
            ),
            patterns=["def ", "return", "assert"],
            mapping=(
                "Docker images stay immutable while environment variables and secrets are injected per "
                "environment; Kubernetes ConfigMaps and Secrets are one common way to do that split."
            ),
        ),
        161: dict(
            topic="Versioning and migration rollouts",
            idea=(
                "APIs change, and clients change slower. Versioning is the promise that old clients keep working "
                "while new ones get new behavior. Put the version where clients can see it, typically in the path "
                "such as /v1/books or in a header, and keep one version alive long enough for consumers to "
                "migrate. Prefer additive changes: a new optional field rarely breaks anyone, while renaming or "
                "removing one breaks everyone who reads it. Database migrations follow the expand-contract "
                "pattern. First expand: add the new column or table without changing reads. Then dual-write or "
                "backfill, so old and new data agree. Then switch reads. Only after every consumer has moved do "
                "you contract, dropping the old shape. Each step is deployable and reversible on its own, which is "
                "what makes a rollout safe at three in the morning. Test both versions against the same fixture "
                "and assert the old response shape is unchanged. Publish a deprecation date and return a header "
                "that names the successor. The migration is finished when the old path can be deleted without any "
                "client noticing, not when the new code merges. Rushing the contract step is how a routine release "
                "becomes an incident. Announce the deprecation before the migration, not after the contract step."
            ),
            code=(
                'BOOK = {"id": 7, "title": "Dune", "author": "Herbert"}\n'
                '\n'
                'def v1(book):\n'
                '    return {"id": book["id"], "title": book["title"]}\n'
                '\n'
                'def v2(book):\n'
                '    return {\n'
                '        "id": book["id"],\n'
                '        "title": book["title"],\n'
                '        "author": book.get("author", "unknown"),\n'
                '    }\n'
                '\n'
                'MIGRATION = [\n'
                '    "expand: add author column, nullable",\n'
                '    "backfill: copy author for existing rows",\n'
                '    "switch: v2 reads author",\n'
                '    "contract: make author required",\n'
                ']\n'
                '\n'
                'print("v1:", v1(BOOK))\n'
                'print("v2:", v2(BOOK))\n'
                'for step in MIGRATION:\n'
                '    print(step)\n'
                'print("old clients still get:", sorted(v1(BOOK)))\n'
                'assert set(v1(BOOK)) == {"id", "title"}\n'
                'assert set(v2(BOOK)) == {"id", "title", "author"}\n'
                'assert v1(BOOK) == {"id": 7, "title": "Dune"}\n'
                'print("v1 contract unchanged during v2 rollout")'
            ),
            variant_b='a book fixture without author and see what v2 returns before backfill',
            variant_c='a v2 response that renames title to name and explain why that needs a new version',
            mistakes=[
                "Removing a field in the same deploy that introduces its replacement.",
                "Dropping the old column before every consumer has migrated.",
                "Changing the meaning of an existing field while keeping the same version.",
            ],
            q1=(
                "Why does expand-contract keep every migration step reversible?",
                "Each step leaves both the old and new shape valid, so reads and writes keep working while clients move.",
            ),
            homework=(
                "Write `serve(version, book)` that returns the v1 or v2 shape and asserts the v1 keys stay stable. "
                "Run it on the same book for both versions, print the responses, and comment which change could be "
                "additive rather than breaking."
            ),
            patterns=["def ", "assert", "return"],
            mapping=(
                "Path or header versioning, feature flags and expand-contract database migrations are the standard "
                "way to ship a change without forcing every client to upgrade on the same day."
            ),
        ),
        162: dict(
            topic="Performance and load",
            idea=(
                "Performance work starts with a measurement, not a hunch. Capture latency for a representative "
                "workload and report percentiles: the median describes the typical request, while p95 and p99 "
                "describe the slow tail that users remember and alerts fire on. An average hides the tail "
                "completely, which is why it is a poor primary metric. Throughput is requests completed per unit "
                "of time, and it only means something alongside latency and concurrency; a service can accept many "
                "requests and answer all of them slowly. Look for the usual causes: a query inside a loop, a "
                "missing index, payloads larger than needed, a connection pool too small, or a dependency called "
                "on every request that could be cached. Change one thing, measure again with the same workload, "
                "and keep the numbers. A load test that never exceeds production traffic proves little; ramp until "
                "latency crosses the budget, then note where it broke. Test the calculation itself with fixed "
                "samples so the percentile function is trustworthy. Optimization without a before-and-after number "
                "is just rearranging code. Today you compute p50, p95 and the share of requests over budget from a "
                "fixed sample set, then compare a faster variant against the same samples. Record the workload and version beside every benchmark so someone can reproduce it."
            ),
            code=(
                'SAMPLES_MS = [120, 130, 125, 900, 140, 135, 128, 150, 160, 200]\n'
                'BUDGET_MS = 300\n'
                '\n'
                'def percentile(values, p):\n'
                '    ordered = sorted(values)\n'
                '    index = int(round((p / 100) * (len(ordered) - 1)))\n'
                '    return ordered[index]\n'
                '\n'
                'def over_budget(values, budget=BUDGET_MS):\n'
                '    return [value for value in values if value > budget]\n'
                '\n'
                'completed, seconds = 1000, 20\n'
                'print("p50:", percentile(SAMPLES_MS, 50))\n'
                'print("p95:", percentile(SAMPLES_MS, 95))\n'
                'print("max:", max(SAMPLES_MS))\n'
                'print("over budget:", len(over_budget(SAMPLES_MS)), "of", len(SAMPLES_MS))\n'
                'print("throughput rps:", completed / seconds)\n'
                'assert percentile([1, 2, 3, 4, 5], 50) == 3\n'
                'assert percentile([1, 2, 3, 4, 5], 95) == 5\n'
                'assert over_budget([100, 301, 299]) == [301]\n'
                'print("percentiles and budget share verified")'
            ),
            variant_b='remove the 900 ms outlier and compare p95 before and after',
            variant_c='raise the budget to 250 ms and recount the over-budget requests',
            mistakes=[
                "Reporting only the average and hiding the slow tail.",
                "Optimizing without capturing a before-and-after measurement.",
                "Testing at a load far below production and calling it capacity.",
            ],
            q1=(
                "Why are p95 and p99 more useful than the average latency?",
                "They describe the slow requests users actually feel, while an average lets a few extreme values disappear.",
            ),
            homework=(
                "Write `percentile(values, p)` and `over_budget(values, budget)` using fixed samples. Run them on "
                "the reference sample and on a faster variant with the outlier removed, print both summaries, and "
                "comment which number changed most and why."
            ),
            patterns=["def ", "assert", "print("],
            mapping=(
                "Load tools such as k6 and Locust produce latency distributions, and Prometheus histograms record "
                "the same percentiles continuously in production."
            ),
        ),
        163: dict(
            topic="Monitoring in production",
            idea=(
                "Production monitoring is the practice of knowing whether users are being served well before they "
                "tell you. Four signals cover most systems: traffic, errors, latency and saturation. Traffic tells "
                "you how much work arrives; errors tell you how much fails; latency tells you how slow the "
                "successful work is; saturation tells you how close a resource is to its limit. Watch them per "
                "route, not only in aggregate, because a single endpoint can be failing while the overall number "
                "looks healthy. Define a service-level objective, such as ninety-nine percent of requests "
                "succeeding under three hundred milliseconds over thirty days, and derive an error budget from it. "
                "The budget turns reliability into a number the team can spend deliberately. Dashboards are for "
                "exploration; alerts are for action, so every alert needs a threshold, a duration, an owner and a "
                "runbook link. Trace a slow request across services with a correlation identifier, and sample "
                "traces so cost stays bounded. Review incidents by asking what signal was missing, then add it. "
                "Monitoring is not a wall of graphs; it is the small set of measurements that lets an on-call "
                "engineer decide what to do next. If a graph cannot change a decision, it is decoration."
            ),
            code=(
                'BUCKETS = [\n'
                '    {"minute": "10:00", "requests": 100, "errors": 1, "p95_ms": 180},\n'
                '    {"minute": "10:01", "requests": 120, "errors": 0, "p95_ms": 190},\n'
                '    {"minute": "10:02", "requests": 80, "errors": 8, "p95_ms": 420},\n'
                ']\n'
                'SLO_ERROR_RATE = 0.01\n'
                '\n'
                'def summarize(buckets, slo_error_rate=SLO_ERROR_RATE):\n'
                '    total = sum(bucket["requests"] for bucket in buckets)\n'
                '    errors = sum(bucket["errors"] for bucket in buckets)\n'
                '    rate = errors / total\n'
                '    return {\n'
                '        "requests": total,\n'
                '        "errors": errors,\n'
                '        "error_rate": round(rate, 4),\n'
                '        "worst_p95_ms": max(b["p95_ms"] for b in buckets),\n'
                '        "slo_ok": rate <= slo_error_rate,\n'
                '    }\n'
                '\n'
                'summary = summarize(BUCKETS)\n'
                'print("summary:", summary)\n'
                'worst = max(BUCKETS, key=lambda b: b["errors"])\n'
                'print("worst minute:", worst["minute"], "errors:", worst["errors"])\n'
                'print("always healthy:", summarize(BUCKETS[:2]))\n'
                'assert summary["error_rate"] == 0.03\n'
                'assert summary["slo_ok"] is False\n'
                'assert summarize(BUCKETS[:2])["slo_ok"] is True\n'
                'print("per-minute view exposes the breach")'
            ),
            variant_b='use only the first two buckets and confirm the SLO passes',
            variant_c='add a bucket with 50 requests and 0 errors and recompute the aggregate rate',
            mistakes=[
                "Watching only the aggregate and missing one failing route.",
                "Creating alerts without a threshold, duration or owner.",
                "Adding dashboards that no incident decision ever uses.",
            ],
            q1=(
                "Why break monitoring down by route instead of one global number?",
                "A single endpoint can breach its objective while healthy routes hide the failure in the aggregate.",
            ),
            homework=(
                "Write `summarize(buckets)` that returns total requests, errors, error rate, worst p95 and whether "
                "the SLO holds. Run it on the full bucket list and on the healthy prefix, print both summaries, and "
                "comment which bucket caused the breach."
            ),
            patterns=["def ", "assert", "sum("],
            mapping=(
                "Prometheus records counters and histograms, Grafana renders them, and an SLO with an error budget "
                "is the usual way to decide whether a release should pause."
            ),
        ),
        164: dict(
            topic="Review: operating an API",
            idea=(
                "Operating an API is a loop: test the behavior, document the contract, deploy safely, observe the "
                "result and feed what you learn back into the tests. The pieces from this phase fit together, and "
                "the review is about seeing the connections. A unit test protects a handler, a client test "
                "protects routing and serialization, a contract test protects the shape clients depend on, and "
                "coverage tells you which branches still lack any of them. Documentation is the contract made "
                "readable, and a test that the document matches the routes keeps it honest. Deployment is safe "
                "when it is reversible and observed, which requires health checks and logs emitted at the edge. "
                "Monitoring turns those signals into alerts tied to a service-level objective, so the team argues "
                "about user impact rather than CPU graphs. The final habit is the release checklist: tests green, "
                "contract unchanged or versioned, docs updated, migration reversible, health check exercised, "
                "rollback written. None of these steps is glamorous, and each one removes a category of "
                "three-in-the-morning surprise. Today you score a release against that checklist and decide "
                "whether it is ready, blocked, or ready only with a rollback plan. The checklist is the phase in "
                "one page."
            ),
            code=(
                'WEIGHTS = {"tests": 3, "contract": 2, "docs": 1, "health": 2, "rollback": 3}\n'
                '\n'
                'def release_state(checks, weights=WEIGHTS):\n'
                '    blocking = sorted(name for name, ok in checks.items() if not ok)\n'
                '    score = sum(weight for name, weight in weights.items() if checks.get(name))\n'
                '    total = sum(weights.values())\n'
                '    if blocking:\n'
                '        state = "blocked"\n'
                '    elif checks.get("rollback"):\n'
                '        state = "ready"\n'
                '    else:\n'
                '        state = "ready with rollback plan"\n'
                '    return {\n'
                '        "state": state,\n'
                '        "score": score,\n'
                '        "total": total,\n'
                '        "blocking": blocking,\n'
                '    }\n'
                '\n'
                'full = {"tests": True, "contract": True, "docs": True, "health": True, "rollback": True}\n'
                'missing_tests = dict(full, tests=False)\n'
                '\n'
                'print("full:", release_state(full))\n'
                'print("no tests:", release_state(missing_tests))\n'
                'print("max score:", release_state(full)["score"], "of", release_state(full)["total"])\n'
                'assert release_state(full)["state"] == "ready"\n'
                'assert release_state(missing_tests)["blocking"] == ["tests"]\n'
                'assert release_state(full)["score"] == 11\n'
                'print("release gates enforced")'
            ),
            variant_b='mark docs false and observe that the release is blocked by a missing contract record',
            variant_c='mark rollback false and decide whether the release may proceed with a written plan',
            mistakes=[
                "Treating a green test suite as the whole release checklist.",
                "Deploying with no written rollback step for the migration.",
                "Calling monitoring optional once the feature works.",
            ],
            q1=(
                "Which release checks should block a deploy rather than merely warn?",
                "Failing tests, an unreviewed contract change and an absent rollback path should block; cosmetic docs can warn.",
            ),
            homework=(
                "Write `release_state(checks, weights)` that returns state, score, total and sorted blocking items. "
                "Run it on a complete checklist and on one with tests false, print both results, and comment which "
                "missing item you would fix first and why."
            ),
            patterns=["def ", "assert", "return"],
            mapping=(
                "Teams encode this checklist in CI pipelines and release runbooks; the tooling changes, but the "
                "gates that keep a deploy reversible and observable do not."
            ),
        ),
    },
)
