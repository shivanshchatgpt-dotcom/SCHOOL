"""API Building foundations, days 9-14: the vocabulary the domain phases build on.

Every example runs offline on in-memory request/response dictionaries, so the
applier can execute it without starting a server. The domain phases keep the
same discipline: one idea, a runnable fixture, and a homework function the
learner adapts.
"""

FOUNDATION = {
    9: dict(
        topic="A request is a dictionary",
        idea=(
            "An HTTP request is a structured message, and the quickest way to stop fearing it is to model it "
            "as a dictionary. It has a method, a path, a collection of headers and an optional body. Every "
            "framework you will meet — Flask, FastAPI, Django, Express — is ultimately handing you those four "
            "things in some wrapper. When you can build the dictionary by hand, you can test an endpoint "
            "without a server, reproduce a bug from a log line, and see exactly which part of the request your "
            "code actually reads. The body is usually text even when it represents JSON, so parsing is an "
            "explicit step with its own failure mode. A malformed body should produce a clear 400, not a "
            "traceback, because the client sent data your contract does not accept and the response has to say "
            "so. Headers matter too: Content-Type tells you how to interpret the body, Authorization carries "
            "credentials, and Accept says what the client can read. Today you build one request, parse its "
            "body, and check the fields your handler depends on. That habit — validate at the boundary, then "
            "work with clean values — prevents a surprising share of production API bugs."
        ),
        code=(
            'import json\n'
            '\n'
            'request = {\n'
            '    "method": "POST",\n'
            '    "path": "/books",\n'
            '    "headers": {"Content-Type": "application/json"},\n'
            '    "body": \'{"title": "Dune", "price": 9.99}\',\n'
            '}\n'
            '\n'
            'payload = json.loads(request["body"])\n'
            'print("method:", request["method"], "| path:", request["path"])\n'
            'print("content type:", request["headers"]["Content-Type"])\n'
            'print("fields:", sorted(payload))\n'
            '\n'
            'required = {"title", "price"}\n'
            'missing = required - set(payload)\n'
            'print("missing:", sorted(missing) or "none")\n'
            'assert not missing\n'
            'print("request is valid at the boundary")'
        ),
        variant_b='body = \'{"title": "Dune"}\' (the price is missing)',
        variant_c='body = "not json" and explain which status the handler should return',
        mistakes=[
            "Treating the body as a Python dict before parsing the JSON text.",
            "Reading a header with the wrong case, when header names are case-insensitive.",
            "Letting a malformed body raise a traceback instead of returning a 400.",
        ],
        q1=(
            "Why parse and validate the body before calling the handler logic?",
            "The handler should receive values that satisfy the contract; boundary validation turns bad client data into a clear 400 instead of a deep crash.",
        ),
        homework=(
            "Write `read_request(request, required)` that parses a JSON body, checks the required fields, and "
            "returns either {'ok': True, 'data': ...} or {'ok': False, 'missing': [...]}. Run it on a valid and "
            "an incomplete request, print both results, and comment which line separates parsing from "
            "validation."
        ),
        patterns=["json.loads", "def ", "return"],
        mapping=(
            "Frameworks hide this dictionary, but they do not change it: FastAPI injects a parsed model, Flask "
            "hands you `request.json`, and both still require you to decide what a missing field means."
        ),
    ),
    10: dict(
        topic="One function per endpoint",
        idea=(
            "An endpoint should be one function with a narrow contract: it receives a request and returns a "
            "status plus a body. That shape makes endpoints independently testable, keeps routing separate from "
            "business logic, and stops the common slide where one giant handler validates input, queries a "
            "database, formats a response and sends an email. When each endpoint is a function, you can call it "
            "directly from a test with a fixture request and assert on the returned pair. You can also reuse it "
            "from a command-line tool or a background job without starting a web server. The function should "
            "not print, should not call `sys.exit`, and should not depend on global request state; those are "
            "signs that transport concerns have leaked into logic. Keep the return value explicit: a status "
            "code and a JSON-serialisable body. Once that is the contract, a router becomes a lookup table from "
            "method and path to function, and the web framework becomes a thin adapter around code you can "
            "test in milliseconds. Today you write two endpoint functions by hand and call them with request "
            "dictionaries, before any server exists. The point is to feel how little an endpoint needs to be."
        ),
        code=(
            'def list_books(request):\n'
            '    return 200, {"items": ["Dune", "Foundation"], "count": 2}\n'
            '\n'
            'def create_book(request):\n'
            '    import json\n'
            '    data = json.loads(request["body"])\n'
            '    if not data.get("title"):\n'
            '        return 422, {"error": "title is required"}\n'
            '    return 201, {"id": 3, "title": data["title"]}\n'
            '\n'
            'print("GET  /books ->", list_books({"method": "GET", "path": "/books"}))\n'
            'print("POST /books ->", create_book({"method": "POST", "body": \'{"title": "Hyperion"}\'}))\n'
            'print("POST empty ->", create_book({"method": "POST", "body": "{}"}))\n'
            'status, body = create_book({"method": "POST", "body": \'{"title": "Hyperion"}\'})\n'
            'assert status == 201 and body["title"] == "Hyperion"\n'
            'print("endpoint contract holds")'
        ),
        variant_b='return 204 with no body for a DELETE endpoint and check the caller handles None',
        variant_c='move the json import to the top of the module and explain why imports belong there',
        mistakes=[
            "Making one handler do routing, validation, storage and formatting at once.",
            "Returning a bare body with no status, so callers cannot distinguish created from updated.",
            "Printing inside the handler, which mixes observability with the response contract.",
        ],
        q1=(
            "Why should an endpoint return a status and a body instead of writing a response directly?",
            "A plain return value can be tested and reused without a server; the framework adapter is the only place that needs to know about the wire.",
        ),
        homework=(
            "Write `update_book(request)` that parses a JSON body, rejects a missing title with 422, and "
            "returns 200 with the updated record otherwise. Call it with a valid and an invalid request, print "
            "both status/body pairs, and comment which line keeps transport out of the handler."
        ),
        patterns=["def ", "return ", "print("],
        mapping=(
            "Flask and FastAPI register these functions as route handlers; the function body stays the same, "
            "and the framework supplies the request and serialises the return value."
        ),
    ),
    11: dict(
        topic="Routing is a table of paths",
        idea=(
            "Routing looks magical until you see it as a lookup. A router maps a method and a path pattern to a "
            "handler, and a request is dispatched by finding the first matching row. Static routes such as "
            "`GET /books` are direct keys; dynamic routes such as `GET /books/{id}` need a pattern match and "
            "then extract the parameter. Writing the table yourself makes the important decisions visible: "
            "which method wins when two patterns overlap, whether trailing slashes are equivalent, and what "
            "happens when nothing matches. The last question is the one beginners skip, and it is the one "
            "clients notice first: an unmatched route must return a structured 404, not an empty 200 or a "
            "server error. A small table also gives you a cheap way to list the API's surface area, which is "
            "the beginning of documentation. Today you build a router from tuples and dispatch a few requests, "
            "including one that should miss. The matching rule is deliberately simple so the lesson is about "
            "the idea rather than a regex. Once the table exists, adding an endpoint is one row, and the "
            "behaviour of unknown paths is decided once for the whole API."
        ),
        code=(
            'def list_books(request):\n'
            '    return 200, {"items": []}\n'
            '\n'
            'def get_book(request, book_id):\n'
            '    return 200, {"id": book_id, "title": "Dune"}\n'
            '\n'
            'routes = [\n'
            '    ("GET", "/books", list_books),\n'
            '    ("GET", "/books/{id}", get_book),\n'
            ']\n'
            '\n'
            'def dispatch(method, path):\n'
            '    for route_method, pattern, handler in routes:\n'
            '        if method != route_method:\n'
            '            continue\n'
            '        if "{" not in pattern and path == pattern:\n'
            '            return handler({"method": method, "path": path})\n'
            '        if "{" in pattern:\n'
            '            prefix = pattern.split("{")[0]\n'
            '            if path.startswith(prefix) and path != prefix:\n'
            '                return handler({"method": method, "path": path}, path[len(prefix):])\n'
            '    return 404, {"error": "route not found"}\n'
            '\n'
            'for method, path in [("GET", "/books"), ("GET", "/books/7"), ("GET", "/authors")]:\n'
            '    print(method, path, "->", dispatch(method, path))\n'
            'assert dispatch("GET", "/authors")[0] == 404\n'
            'print("router table dispatches and misses cleanly")'
        ),
        variant_b='add ("POST", "/books", list_books) as a placeholder and explain why the handler name is wrong',
        variant_c='make "/books/" match "/books" by normalising the trailing slash before lookup',
        mistakes=[
            "Returning an empty 200 for an unknown route, so clients cannot tell a miss from an empty list.",
            "Matching methods case-sensitively when HTTP methods are conventionally uppercase.",
            "Letting a dynamic pattern swallow a more specific static route.",
        ],
        q1=(
            "Why should an unknown route return 404 with a body rather than an empty 200?",
            "A 200 claims the request succeeded; 404 states that no resource exists and gives the client a machine-readable error.",
        ),
        homework=(
            "Write `dispatch(routes, method, path)` that matches static and `{id}` patterns, extracts the "
            "parameter, and returns 404 with an error body for misses. Test it with three routes and at least "
            "four requests, print every result, and comment which line decides the miss."
        ),
        patterns=["def ", "for ", "return"],
        mapping=(
            "Flask's `@app.route` and FastAPI's decorators are sugar over this table; path converters such as "
            "`{id:int}` add type checks that a hand-written router must perform itself."
        ),
    ),
    12: dict(
        topic="JSON in, JSON out",
        idea=(
            "JSON is the default language of APIs because it maps cleanly onto the data structures most "
            "languages already have: objects become dictionaries, arrays become lists, strings, numbers, "
            "booleans and null map directly. The two operations that matter are parsing text into values and "
            "serialising values back into text. Both have traps. Numbers can lose precision, dates have no "
            "native type, and non-ASCII text may arrive escaped or literal depending on the encoder. A good API "
            "decides these rules once: money as a string or integer minor units, timestamps as ISO 8601 UTC, "
            "and `ensure_ascii=False` so human-readable names survive. The response must also declare "
            "`Content-Type: application/json`, because a correct body with the wrong header is still a bug to "
            "many clients. On the input side, reject anything that is not an object when your contract expects "
            "one; a JSON array or a bare string is valid JSON but wrong for your endpoint. Today you round-trip "
            "a record through JSON and inspect the exact text that crosses the wire. Seeing the wire format "
            "explicitly is the fastest way to stop guessing why a client parsed your response differently than "
            "you expected."
        ),
        code=(
            'import json\n'
            '\n'
            'def to_json(payload):\n'
            '    return json.dumps(payload, ensure_ascii=False, sort_keys=True)\n'
            '\n'
            'record = {"id": 1, "title": "Café Society", "price": "9.99", "tags": ["film", "drama"]}\n'
            'wire = to_json(record)\n'
            'print("wire:", wire)\n'
            '\n'
            'back = json.loads(wire)\n'
            'print("round trip equal:", back == record)\n'
            'print("types:", {k: type(v).__name__ for k, v in back.items()})\n'
            '\n'
            'try:\n'
            '    json.loads("[1, 2, 3]")\n'
            '    print("array is valid JSON")\n'
            'except json.JSONDecodeError:\n'
            '    print("array is not valid JSON")\n'
            '\n'
            'assert back == record and "Café" in wire\n'
            'print("JSON contract preserved")'
        ),
        variant_b='set ensure_ascii=True and compare the escaped output',
        variant_c='serialise a decimal price as a float and inspect the changed representation',
        mistakes=[
            "Forgetting Content-Type: application/json on the response.",
            "Sending money as a float, so 9.99 becomes a binary approximation.",
            "Assuming every valid JSON document is an object your endpoint can accept.",
        ],
        q1=(
            "Why send money as a string or integer minor units instead of a JSON float?",
            "JSON numbers are binary floats, so decimal money can lose precision; strings or integer cents preserve the exact value.",
        ),
        homework=(
            "Write `json_response(payload)` that returns a status, a Content-Type header and a deterministic "
            "JSON string. Call it with a nested record containing a non-ASCII title, print the wire text and "
            "the parsed round trip, and comment which option keeps the title readable."
        ),
        patterns=["json.dumps", "json.loads", "print("],
        mapping=(
            "FastAPI serialises return values with its own encoder; Flask needs `jsonify`; both still honour "
            "the same decisions about money, dates and non-ASCII text."
        ),
    ),
    13: dict(
        topic="Errors have a shape",
        idea=(
            "Clients do not read prose; they read fields. An error response should be as structured as a "
            "success response, because the client needs to decide what to do without parsing English. A "
            "consistent shape such as {'error': {'code': 'validation_failed', 'message': '...', 'details': [...]}} "
            "lets every endpoint share one client-side handler, one log query and one test helper. HTTP status "
            "carries the category: 400 for malformed input, 401 for missing credentials, 403 for insufficient "
            "permission, 404 for a missing resource, 409 for a conflict, 422 for semantically invalid fields, "
            "and 500 for a bug on the server. The code field carries the specific reason inside that category. "
            "Both matter: a client that only sees 400 knows the request was bad, while a client that sees "
            "'price_must_be_positive' knows exactly which field to fix. Error shape also affects security. A "
            "500 must not leak a stack trace or a database query, while a 404 should not confirm whether a "
            "private resource exists. Today you build a small error constructor and print several responses, "
            "paying attention to which information belongs in the body and which belongs only in the log. "
            "Consistency here is a feature, not polish."
        ),
        code=(
            'def error(status, code, message, details=None):\n'
            '    body = {"error": {"code": code, "message": message}}\n'
            '    if details:\n'
            '        body["error"]["details"] = details\n'
            '    return status, body\n'
            '\n'
            'cases = [\n'
            '    error(400, "malformed_json", "Body is not valid JSON"),\n'
            '    error(401, "missing_token", "Authorization header is required"),\n'
            '    error(422, "validation_failed", "One or more fields are invalid",\n'
            '          [{"field": "price", "reason": "must be positive"}]),\n'
            '    error(404, "not_found", "Book does not exist"),\n'
            ']\n'
            'for status, body in cases:\n'
            '    print(status, body["error"]["code"], "|", body["error"]["message"])\n'
            '\n'
            'status, body = cases[2]\n'
            'assert status == 422 and body["error"]["details"][0]["field"] == "price"\n'
            'print("errors share one shape")'
        ),
        variant_b='add a 409 conflict for a duplicate title and choose the code string',
        variant_c='return a 500 with a generic message and explain what must never appear in it',
        mistakes=[
            "Returning 200 with an error field, which breaks every client that trusts status codes.",
            "Using different error shapes on different endpoints, forcing client-side special cases.",
            "Leaking a stack trace or SQL fragment in a 500 response.",
        ],
        q1=(
            "Why keep both an HTTP status and an application error code?",
            "The status gives the category every HTTP client understands; the code names the specific reason so the client can react without parsing prose.",
        ),
        homework=(
            "Write `validation_error(fields)` that returns a 422 response with a stable code, a message and a "
            "details list built from a dictionary of field-to-reason. Run it on two different field sets, print "
            "both responses, and comment which line keeps the shape identical across calls."
        ),
        patterns=["def ", "return ", "error"],
        mapping=(
            "FastAPI's HTTPException and Flask's error handlers can both emit this shape; the important part is "
            "that every endpoint uses the same constructor."
        ),
    ),
    14: dict(
        topic="A tiny API, end to end",
        idea=(
            "Today you assemble the pieces: a request dictionary, a route table, endpoint functions, JSON "
            "serialisation and a shared error shape. The API is deliberately small — list and create books in "
            "memory — but it already has the properties that matter. Routing is data, handlers are pure "
            "functions, validation happens at the boundary, and every response is a status plus a "
            "JSON-serialisable body. You can call the whole thing without a socket, which means you can test it "
            "without a running server and debug it without a network. The in-memory store will be replaced by "
            "SQLite later, and the router by a framework, but the contract will not change. That is the point "
            "of building the skeleton by hand first: the framework becomes an implementation detail rather than "
            "the thing you are learning. Notice how the POST handler returns 201 and a body containing the new "
            "id, while the GET handler returns 200 and a collection. Notice also that the unknown route and the "
            "invalid body both return structured errors. Those four decisions — route table, pure handlers, "
            "boundary validation, consistent errors — are the core of every API you will build for the rest of "
            "the track."
        ),
        code=(
            'import json\n'
            '\n'
            'books = [{"id": 1, "title": "Dune"}]\n'
            '\n'
            'def list_books(request):\n'
            '    return 200, {"items": books, "count": len(books)}\n'
            '\n'
            'def create_book(request):\n'
            '    try:\n'
            '        data = json.loads(request["body"])\n'
            '    except json.JSONDecodeError:\n'
            '        return 400, {"error": {"code": "malformed_json"}}\n'
            '    if not isinstance(data, dict) or not data.get("title"):\n'
            '        return 422, {"error": {"code": "validation_failed"}}\n'
            '    book = {"id": max(b["id"] for b in books) + 1, "title": data["title"]}\n'
            '    books.append(book)\n'
            '    return 201, book\n'
            '\n'
            'routes = {("GET", "/books"): list_books, ("POST", "/books"): create_book}\n'
            '\n'
            'def handle(method, path, body=""):\n'
            '    handler = routes.get((method, path))\n'
            '    if handler is None:\n'
            '        return 404, {"error": {"code": "not_found"}}\n'
            '    return handler({"method": method, "path": path, "body": body})\n'
            '\n'
            'print(handle("GET", "/books"))\n'
            'print(handle("POST", "/books", \'{"title": "Hyperion"}\'))\n'
            'print(handle("POST", "/books", "{}"))\n'
            'print(handle("GET", "/authors"))\n'
            'assert handle("GET", "/books")[1]["count"] == 2\n'
            'print("tiny API complete")'
        ),
        variant_b='add GET /books/{id} and return 404 for a missing id',
        variant_c='reject a duplicate title with 409 and explain why 409 fits better than 422',
        mistakes=[
            "Mutating the store before validation has passed.",
            "Returning the mutable internal list, so a caller can change server state by accident.",
            "Letting a missing route fall through to a 500 instead of a structured 404.",
        ],
        q1=(
            "Why can this API be tested without starting a web server?",
            "Routing and handlers are plain functions that take a request dictionary and return status plus body; the socket is only one possible adapter.",
        ),
        homework=(
            "Write `handle(routes, method, path, body)` that dispatches to a handler, returns a structured 404 "
            "for an unknown route, and preserves the handler's status. Test it with a successful GET, a "
            "successful POST, an invalid body and a missing route, print all four, and comment which line "
            "keeps the transport boundary thin."
        ),
        patterns=["def ", "routes", "return"],
        mapping=(
            "This is the same skeleton FastAPI generates for you: a route table, request parsing, validation, "
            "handler logic and a serialised response. The framework adds HTTP plumbing, not a new architecture."
        ),
    ),
}
