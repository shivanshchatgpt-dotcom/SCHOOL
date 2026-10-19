"""API Building phase 3, days 105-119: implementing a JSON API.

The phase starts with a handler as a plain function and ends with a working
in-memory API that has routing, validation, SQLite storage, one error
envelope, request logs, CORS, health probes, shutdown and file responses.

Every example is stdlib-only and runs offline: requests are dictionaries,
storage is ``:memory:`` SQLite, and the ``http.server`` handler is exercised
through a fake ``self`` without binding a port.
"""

PHASE = (
    "Building a JSON API",
    "Implement a small JSON API end to end, from one handler function through routing, validation, SQLite storage, errors, logging, CORS, probes and shutdown.",
    {
        105: dict(
            topic="A handler is a function",
            idea=(
                "A handler is a function with a narrow contract: it receives everything it needs about a "
                "request and returns a status plus a body. In the stdlib server, the framework calls a method "
                "such as do_GET, but the method is still a function, and it still has one job. A useful habit "
                "is to keep the transport out of it. If the handler writes directly to the socket, you cannot "
                "test it without a server, cannot reuse it from a script, and cannot reproduce a bug from a log "
                "line. Today you build a handler object whose handle method takes an in-memory request "
                "dictionary and returns a tuple of status and body. The same code could later be wrapped by "
                "http.server, Flask or FastAPI. Notice what the handler does not do: it does not parse URL "
                "query strings, does not open a database and does not print. Those are separate concerns that "
                "will get their own days. The point is to make the smallest useful unit of an API explicit, so "
                "routing, storage and serialisation can be added around it without rewriting it. When a "
                "handler is this small, a test is three lines and a bug has nowhere to hide. The return value "
                "is the contract, and everything else is plumbing."
            ),
            code=(
                'class BookHandler:\n'
                '    def handle(self, request):\n'
                '        if request["method"] != "GET":\n'
                '            return 405, {"error": {"code": "method_not_allowed"}}\n'
                '        return 200, {"items": ["Dune", "Foundation"], "count": 2}\n'
                '\n'
                'requests = [\n'
                '    {"method": "GET", "path": "/books", "headers": {}, "body": ""},\n'
                '    {"method": "POST", "path": "/books", "headers": {}, "body": ""},\n'
                ']\n'
                '\n'
                'handler = BookHandler()\n'
                'for request in requests:\n'
                '    status, body = handler.handle(request)\n'
                '    print(request["method"], request["path"], "->", status, body)\n'
                '\n'
                'assert handler.handle(requests[0])[0] == 200\n'
                'assert handler.handle(requests[1])[0] == 405\n'
                'print("handler is a function with a contract")'
            ),
            variant_b='make the handler accept a query dictionary and return only the titles that match',
            variant_c='return 204 with None for an empty collection and explain why the caller must handle None',
            mistakes=[
                "Writing directly to the socket inside the handler, so it can no longer be tested alone.",
                "Letting one handler route, validate, store and format all at once.",
                "Printing inside the handler instead of returning a value the adapter can send.",
            ],
            q1=(
                "Why should a handler return status and body instead of writing a response?",
                "A return value can be called and asserted without a server; the adapter owns the socket and the handler stays reusable and testable.",
            ),
            homework=(
                "Write `handle(request)` that accepts a request dictionary, rejects anything except GET with "
                "405, and returns 200 plus a two-item collection. Call it with a GET and a POST request, print "
                "both status/body pairs, and comment which line keeps the handler transport-independent."
            ),
            patterns=["def ", "return ", "print("],
            mapping=(
                "FastAPI and Flask register functions of exactly this shape as endpoints; the framework adapts "
                "the wire request into arguments and serialises the return value, but the function body does "
                "not change."
            ),
        ),
        106: dict(
            topic="Routing with stdlib http.server",
            idea=(
                "Routing is a lookup from a method and a path to a handler. The stdlib http.server gives you "
                "BaseHTTPRequestHandler, whose do_GET and do_POST methods receive the parsed request through "
                "self.path and self.headers. It does not give you a router, so a subclass usually grows a long "
                "if/elif chain. Replace that chain with a table. Each row is a method, a path pattern and a "
                "function; dispatch walks the rows, compares the method, matches literal segments, and fills "
                "in placeholders such as book_id. Two behaviours matter as much as the happy path. A method "
                "that exists on another path must produce 405 rather than 404, and an unknown path must "
                "produce a structured 404 rather than an empty 200. Normalise a trailing slash before matching "
                "so /books and /books/ do not become different resources by accident. Query strings must be "
                "split off before matching, because the path is the route and the query is data. Today you "
                "dispatch in-memory requests through a route table from a BaseHTTPRequestHandler subclass "
                "without binding a port, and you print the match, the miss and the extracted id. The fake self "
                "is enough because the method only needs self.path, which proves the routing logic is testable "
                "without a socket."
            ),
            code=(
                'import urllib.parse\n'
                'from http.server import BaseHTTPRequestHandler\n'
                '\n'
                'def list_books(request):\n'
                '    return 200, {"items": ["Dune"]}\n'
                '\n'
                'def get_book(request, id):\n'
                '    return 200, {"id": id, "title": "Dune"}\n'
                '\n'
                'ROUTES = [\n'
                '    ("GET", "/books", list_books),\n'
                '    ("GET", "/books/{id}", get_book),\n'
                ']\n'
                '\n'
                'def route(method, raw_path):\n'
                '    parsed = urllib.parse.urlsplit(raw_path)\n'
                '    path = parsed.path.rstrip("/") or "/"\n'
                '    parts = [part for part in path.split("/") if part]\n'
                '    for allowed, pattern, handler in ROUTES:\n'
                '        if method != allowed:\n'
                '            continue\n'
                '        pattern_parts = [part for part in pattern.split("/") if part]\n'
                '        if len(parts) != len(pattern_parts):\n'
                '            continue\n'
                '        params = {}\n'
                '        for actual, expected in zip(parts, pattern_parts):\n'
                '            if expected.startswith("{") and expected.endswith("}"):\n'
                '                params[expected[1:-1]] = actual\n'
                '            elif actual != expected:\n'
                '                break\n'
                '        else:\n'
                '            request = {"method": method, "path": path, "query": parsed.query}\n'
                '            return handler(request, **params)\n'
                '    return 404, {"error": {"code": "not_found"}}\n'
                '\n'
                'class ApiHandler(BaseHTTPRequestHandler):\n'
                '    def do_GET(self):\n'
                '        return route("GET", self.path)\n'
                '\n'
                'fake = type("Fake", (), {"path": "/books/7?fields=title"})()\n'
                'print("GET /books/7 ->", ApiHandler.do_GET(fake))\n'
                'fake.path = "/authors"\n'
                'print("GET /authors ->", ApiHandler.do_GET(fake))\n'
                'assert ApiHandler.do_GET(fake)[0] == 404\n'
                'print("stdlib handler method delegates to the route table")'
            ),
            variant_b='add ("DELETE", "/books/{id}", get_book) and explain why the handler name is now misleading',
            variant_c='make "/books/" match "/books" by normalising the trailing slash before the table lookup',
            mistakes=[
                "Letting a long if/elif chain in do_GET become the router, so routes cannot be listed or tested.",
                "Forgetting to separate the query string, so /books?page=2 no longer matches /books.",
                "Returning 404 for a known path with the wrong method instead of 405.",
            ],
            q1=(
                "Why split the query string off before matching the route?",
                "The route is the path alone; query parameters are data for the handler, and leaving them on makes every parameterised URL a different route.",
            ),
            homework=(
                "Write `route(method, path, routes)` that matches literal and `{id}` patterns, extracts the id, "
                "returns 404 for a miss and 405 for a known path with the wrong method. Test it with two routes "
                "and four requests, print every result, and comment which line separates the path from the query."
            ),
            patterns=["BaseHTTPRequestHandler", "for ", "return "],
            mapping=(
                "Flask's @app.route and FastAPI's decorators build the same table at import time; their path "
                "converters add type checks that a hand-written matcher must perform itself."
            ),
        ),
        107: dict(
            topic="Parsing JSON bodies safely",
            idea=(
                "JSON arrives as text, and text is not a dictionary until you parse it. The body of a request "
                "can be empty, truncated, malformed, valid but not an object, or accompanied by the wrong "
                "Content-Type. Each of those is a different client mistake and deserves a different status: "
                "415 for the wrong media type, 400 for malformed or empty JSON, 422 for valid JSON that cannot "
                "serve as the endpoint's input. Parse once, at the boundary, then pass a clean value inward. Do "
                "not sprinkle json.loads through the handler, and do not catch every exception: JSONDecodeError "
                "names exactly the failure you expect, while a blanket except hides programming bugs. Check "
                "that the parsed value is a dictionary when the contract expects fields; a JSON array is valid "
                "JSON and still wrong for a create endpoint. Treat the declared Content-Type as part of the "
                "contract rather than trusting the body's first character. Finally, remember that the body is "
                "bytes on the wire: the server decodes it using the charset, then parses it. Today you write a "
                "parser that returns either data or a structured error, and prove that a malformed body never "
                "reaches handler logic. The parser is the only place that knows JSON text is involved."
            ),
            code=(
                'import json\n'
                '\n'
                'def parse_json_body(request):\n'
                '    media = request["headers"].get("Content-Type", "").split(";")[0].strip().lower()\n'
                '    if media != "application/json":\n'
                '        return None, (415, {"error": {"code": "unsupported_media_type"}})\n'
                '    body = request.get("body", "")\n'
                '    if not body.strip():\n'
                '        return None, (400, {"error": {"code": "empty_body"}})\n'
                '    try:\n'
                '        payload = json.loads(body)\n'
                '    except json.JSONDecodeError:\n'
                '        return None, (400, {"error": {"code": "malformed_json"}})\n'
                '    if not isinstance(payload, dict):\n'
                '        return None, (422, {"error": {"code": "object_required"}})\n'
                '    return payload, None\n'
                '\n'
                'cases = [\n'
                '    {"headers": {"Content-Type": "application/json"}, "body": \'{"title": "Dune"}\'},\n'
                '    {"headers": {"Content-Type": "application/json"}, "body": "{not json"},\n'
                '    {"headers": {"Content-Type": "text/plain"}, "body": \'{"title": "Dune"}\'},\n'
                '    {"headers": {"Content-Type": "application/json"}, "body": "[1, 2]"},\n'
                ']\n'
                '\n'
                'for request in cases:\n'
                '    payload, error = parse_json_body(request)\n'
                '    print(request["headers"]["Content-Type"], "->", payload if error is None else error)\n'
                '\n'
                'assert parse_json_body(cases[0])[0] == {"title": "Dune"}\n'
                'assert parse_json_body(cases[1])[1][0] == 400\n'
                'assert parse_json_body(cases[2])[1][0] == 415\n'
                'print("bad bodies never reach the handler")'
            ),
            variant_b='send an empty body with application/json and decide between 400 and 422',
            variant_c='add "; charset=utf-8" to Content-Type and confirm the media check still passes',
            mistakes=[
                "Calling json.loads on request bytes without deciding how malformed input should be reported.",
                "Catching every exception, so a bug in the handler looks like a bad client request.",
                "Accepting a JSON array because it parsed, even though the endpoint needs named fields.",
            ],
            q1=(
                "Why catch JSONDecodeError instead of a blanket Exception around json.loads?",
                "JSONDecodeError is the exact expected failure; a blanket catch also hides programming errors and turns them into misleading 400 responses.",
            ),
            homework=(
                "Write `parse_json_body(request)` that checks Content-Type, rejects empty and malformed bodies "
                "with distinct statuses, and returns either a dictionary or a structured error. Run it on two "
                "different bad requests, print both errors, and comment which line keeps parsing at the boundary."
            ),
            patterns=["json.loads", "except json.JSONDecodeError", "return "],
            mapping=(
                "FastAPI parses the body before your function and reports malformed JSON as 422 by default; "
                "Flask exposes request.get_json(), which raises unless you handle the failure. The boundary "
                "decision is yours in either framework."
            ),
        ),
        108: dict(
            topic="Serialising responses",
            idea=(
                "Serialising is the return journey: a Python value becomes bytes that a client can parse. "
                "json.dumps returns text, not bytes, and the HTTP response needs bytes so that Content-Length "
                "counts octets rather than characters. That difference matters as soon as a title contains an "
                "accent or an emoji. Encode as UTF-8, declare application/json with the charset, and set "
                "Content-Length from the encoded bytes. Use a fixed serialisation policy so two identical "
                "responses are byte-identical: sort keys, choose compact separators, and set ensure_ascii to "
                "False for readable names. Decide how to represent values JSON does not have. Decimal money "
                "becomes integer cents or a string, dates become ISO 8601 strings, and a float that is NaN must "
                "not silently become invalid JSON, so pass allow_nan=False and fix the value instead. Never let "
                "a generic default function stringify arbitrary objects; that turns a bug into a plausible "
                "response. A serialiser is also a contract: clients parse the same fields, so stable names and "
                "types matter more than pretty output. Today you build a response helper, print the wire text, "
                "and prove the encoded length is honest. The response is a status, headers and bytes, ready for "
                "any adapter to send."
            ),
            code=(
                'import json\n'
                '\n'
                'def json_response(status, payload):\n'
                '    wire = json.dumps(payload, ensure_ascii=False, sort_keys=True, allow_nan=False)\n'
                '    body = wire.encode("utf-8")\n'
                '    headers = {\n'
                '        "Content-Type": "application/json; charset=utf-8",\n'
                '        "Content-Length": str(len(body)),\n'
                '    }\n'
                '    return status, headers, body\n'
                '\n'
                'record = {"id": 2, "title": "Café Society", "tags": ["film", "drama"], "price_cents": 999}\n'
                'status, headers, body = json_response(200, record)\n'
                '\n'
                'print("status:", status)\n'
                'print("headers:", headers)\n'
                'print("wire:", body.decode("utf-8"))\n'
                'print("round trip equal:", json.loads(body) == record)\n'
                '\n'
                'assert headers["Content-Length"] == str(len(body))\n'
                'assert b"Caf\\xc3\\xa9" in body\n'
                'assert json.loads(body) == record\n'
                'print("response is bytes with an honest length")'
            ),
            variant_b='serialise a record containing a date object and choose an ISO 8601 string instead of default=str',
            variant_c='set ensure_ascii=True and compare the byte length of the same accented title',
            mistakes=[
                "Sending str from json.dumps without encoding, so Content-Length counts characters instead of bytes.",
                "Using default=str everywhere, which turns a serialisation bug into an unexpected response shape.",
                "Omitting the JSON content type, so a correct body is still misread by strict clients.",
            ],
            q1=(
                "Why must Content-Length be computed from the encoded bytes?",
                "HTTP counts octets; an accented character is multiple bytes, so character length understates the body and truncates it for the client.",
            ),
            homework=(
                "Write `json_response(status, payload)` that dumps deterministic UTF-8 JSON, returns headers "
                "with the real byte length, and keeps non-ASCII text readable. Run it on two records, print the "
                "wire text and headers, and comment which line makes the output byte-stable."
            ),
            patterns=["json.dumps", ".encode(", "Content-Length"],
            mapping=(
                "FastAPI's JSONResponse and Flask's jsonify both encode UTF-8 and set the content type for you; "
                "knowing the byte-length rule explains why a manually built response sometimes truncates."
            ),
        ),
        109: dict(
            topic="In-memory CRUD",
            idea=(
                "CRUD is four operations over a collection: create, read, update and delete, plus list. In "
                "memory the store can be a dictionary keyed by integer id. The dictionary is not the lesson; "
                "the contract is. Create returns 201 and the new record with its id. List returns 200 and a "
                "collection wrapper, not a bare list, so pagination and counts can be added later without "
                "breaking clients. Read returns 200 or a structured 404. Update returns 200 with the new "
                "representation, or 404 when the id is unknown. Delete returns 204 with no body, because there "
                "is nothing left to describe. Keep the next id monotonic even after deletion, so an id is never "
                "reused for a different item. Return copies rather than the stored dictionaries, or a caller "
                "can mutate server state by accident. Do not mutate the store before validation passes, and do "
                "not hide a missing id behind a successful empty response. These rules are small, but they are "
                "exactly what clients depend on. Today you implement the five operations against a dictionary "
                "and print the full sequence, including the 404 after a delete. The state transitions are the "
                "thing to watch, not the Python syntax, because the transitions are what clients observe."
            ),
            code=(
                'class BookStore:\n'
                '    def __init__(self):\n'
                '        self.rows = {}\n'
                '        self.next_id = 1\n'
                '\n'
                '    def create(self, title):\n'
                '        book = {"id": self.next_id, "title": title}\n'
                '        self.rows[book["id"]] = book\n'
                '        self.next_id += 1\n'
                '        return 201, dict(book)\n'
                '\n'
                '    def list(self):\n'
                '        items = [dict(row) for row in self.rows.values()]\n'
                '        return 200, {"items": items, "count": len(items)}\n'
                '\n'
                '    def get(self, book_id):\n'
                '        row = self.rows.get(book_id)\n'
                '        if row is None:\n'
                '            return 404, {"error": {"code": "not_found"}}\n'
                '        return 200, dict(row)\n'
                '\n'
                '    def update(self, book_id, title):\n'
                '        row = self.rows.get(book_id)\n'
                '        if row is None:\n'
                '            return 404, {"error": {"code": "not_found"}}\n'
                '        row["title"] = title\n'
                '        return 200, dict(row)\n'
                '\n'
                '    def delete(self, book_id):\n'
                '        if self.rows.pop(book_id, None) is None:\n'
                '            return 404, {"error": {"code": "not_found"}}\n'
                '        return 204, None\n'
                '\n'
                'store = BookStore()\n'
                'print("create:", store.create("Dune"))\n'
                'print("create:", store.create("Foundation"))\n'
                'print("list:", store.list())\n'
                'print("get 2:", store.get(2))\n'
                'print("update 2:", store.update(2, "Foundation (Revised)"))\n'
                'print("delete 1:", store.delete(1))\n'
                'print("get 1:", store.get(1))\n'
                '\n'
                'assert store.list()[1]["count"] == 1\n'
                'assert store.get(1)[0] == 404\n'
                'print("crud state is consistent")'
            ),
            variant_b='return 400 for a create with a blank title and check that the next id did not advance',
            variant_c='return the stored dictionary instead of a copy, then mutate the response and inspect the store',
            mistakes=[
                "Mutating the store before validation succeeds, leaving a rejected record behind.",
                "Returning the internal dictionary, so a caller can change server state without an endpoint.",
                "Reusing an id after deletion, so old links silently point at a different item.",
            ],
            q1=(
                "Why return copies from list and get instead of the stored dictionaries?",
                "A copy keeps the response from sharing identity with server state, so a caller cannot mutate the store by editing a returned record.",
            ),
            homework=(
                "Write a `BookStore` with `create`, `list`, `get`, `update` and `delete`, returning the statuses "
                "described in the lesson. Run the full sequence on two different stores, print every response, "
                "and comment which line prevents a deleted id from being reused."
            ),
            patterns=["def ", "dict(", "return "],
            mapping=(
                "This store is the layer a real service puts in front of a database; Flask and FastAPI examples "
                "usually call it a repository. The status contract is independent of whether the rows live in a "
                "dict or a table."
            ),
        ),
        110: dict(
            topic="Persisting with SQLite",
            idea=(
                "An in-memory store disappears when the process exits, so persistence starts with a database. "
                "SQLite ships with Python, runs in a single file, and supports the same SQL you will use later. "
                "Start by declaring the table instead of letting a loader infer it: column names, types, a "
                "primary key, NOT NULL, and a CHECK for values that must never be negative. Constraints are "
                "validation that survives every code path, including the one you forget to test. Insert a "
                "batch inside one transaction so a crash cannot leave half the rows. executemany is the right "
                "tool for a list of records, and a single commit at the end is both faster and atomic. Read "
                "rows back with a query and compare the stored count with the number you inserted; a mismatch "
                "means the insert logic and the schema disagree. Use row_factory when you want named columns, "
                "and close the connection when the work is done. Today you use an in-memory database so nothing "
                "touches disk, but the schema, transaction and count check are exactly the ones you would use "
                "with a file-backed database in production. The transaction is the unit that makes a batch "
                "trustworthy, not the individual INSERT statement."
            ),
            code=(
                'import sqlite3\n'
                '\n'
                'SCHEMA = """\n'
                'CREATE TABLE books (\n'
                '    id INTEGER PRIMARY KEY,\n'
                '    title TEXT NOT NULL,\n'
                '    price_cents INTEGER NOT NULL CHECK (price_cents >= 0)\n'
                ')\n'
                '"""\n'
                '\n'
                'rows = [(1, "Dune", 999), (2, "Foundation", 1250), (3, "Neuromancer", 875)]\n'
                '\n'
                'conn = sqlite3.connect(":memory:")\n'
                'conn.row_factory = sqlite3.Row\n'
                'conn.execute(SCHEMA)\n'
                'with conn:\n'
                '    conn.executemany("INSERT INTO books (id, title, price_cents) VALUES (?, ?, ?)", rows)\n'
                '\n'
                'stored = conn.execute("SELECT COUNT(*) AS n FROM books").fetchone()["n"]\n'
                'print("stored rows:", stored)\n'
                'for row in conn.execute("SELECT id, title, price_cents FROM books ORDER BY id"):\n'
                '    print(dict(row))\n'
                '\n'
                'assert stored == len(rows)\n'
                'conn.close()\n'
                'print("transaction committed the whole batch")'
            ),
            variant_b='insert a row with a negative price and explain which constraint rejects it',
            variant_c='add a UNIQUE constraint on title, insert a duplicate, and report the sqlite3 error',
            mistakes=[
                "Committing after every row, which is slow and leaves a partial table after a crash.",
                "Letting the schema be inferred from sample values instead of declaring types and constraints.",
                "Skipping the stored-count check, so a silent insert failure looks like a successful load.",
            ],
            q1=(
                "Why insert the batch inside one transaction instead of committing each row?",
                "One transaction is faster and atomic: either every row is stored or none is, so a crash cannot leave a half-written table.",
            ),
            homework=(
                "Write `load_books(rows)` that creates the books table, inserts a batch with executemany inside "
                "one transaction, and returns the stored count. Run it on two row sets, print the count and the "
                "rows, and comment which line makes the whole load atomic."
            ),
            patterns=["import sqlite3", "executemany", "commit("],
            mapping=(
                "SQLite is the database an API reaches for before a server exists, and the same SQL and "
                "transaction habits carry over to PostgreSQL. A file path instead of :memory: is the only "
                "change needed to survive a restart."
            ),
        ),
        111: dict(
            topic="Parameterised queries",
            idea=(
                "SQL injection begins with string concatenation. The moment a query is built as SELECT with the "
                "user value appended, the user's value stops being data and becomes part of the program. A "
                "quote closes the string, and the rest of the input is read as SQL. Parameterised queries "
                "remove the possibility: the statement and the values travel separately, and the driver binds "
                "each value as data with its own type. Use placeholders, never percent-formatting or f-strings, "
                "for every value including numbers and dates. The rule has an important edge: placeholders bind "
                "values, not identifiers. You cannot parameterise a column name or an ORDER BY direction, so "
                "those must come from a fixed allowlist, never straight from the query string. LIKE patterns "
                "are values and can be bound, but the wildcard characters inside them still need escaping when "
                "the user's text should be literal. Today you run a harmless injection against a table, then "
                "run the same input through a placeholder query and show that it returns nothing. The "
                "difference is one character in the code and the whole security model in the result. Treat "
                "every request value as hostile, even when the current client is your own test script. That "
                "separation is the whole defence."
            ),
            code=(
                'import sqlite3\n'
                '\n'
                'conn = sqlite3.connect(":memory:")\n'
                'conn.execute("CREATE TABLE books (id INTEGER PRIMARY KEY, title TEXT NOT NULL)")\n'
                'conn.executemany(\n'
                '    "INSERT INTO books (id, title) VALUES (?, ?)",\n'
                '    [(1, "Dune"), (2, "Foundation"), (3, "O\'Brien")],\n'
                ')\n'
                '\n'
                'user_input = "Dune\' OR \'1\'=\'1"\n'
                'unsafe_sql = "SELECT id, title FROM books WHERE title = \'" + user_input + "\'"\n'
                'safe_sql = "SELECT id, title FROM books WHERE title = ?"\n'
                '\n'
                'print("unsafe rows:", conn.execute(unsafe_sql).fetchall())\n'
                'print("safe rows:", conn.execute(safe_sql, (user_input,)).fetchall())\n'
                'print("real lookup:", conn.execute(safe_sql, ("O\'Brien",)).fetchall())\n'
                '\n'
                'assert conn.execute(safe_sql, (user_input,)).fetchall() == []\n'
                'assert len(conn.execute(safe_sql, ("O\'Brien",)).fetchall()) == 1\n'
                'print("the value stayed a value, never SQL")\n'
                'conn.close()'
            ),
            variant_b='bind a numeric id from the query string and confirm the driver converts it safely',
            variant_c='try to bind a column name for ORDER BY and explain why an allowlist is required instead',
            mistakes=[
                "Building SQL with f-strings, so a quote in a title changes the statement.",
                "Trying to parameterise a table or column name when only values can be bound.",
                "Escaping quotes by hand instead of letting the driver bind the value.",
            ],
            q1=(
                "Why can a placeholder bind a title but not a column name?",
                "A placeholder substitutes a value inside the already-parsed statement; identifiers define the statement's shape and cannot be supplied as data, so they need an allowlist.",
            ),
            homework=(
                "Write `find_books(conn, title)` that queries by title using a placeholder and returns the rows. "
                "Run it on two cases, a normal title and a quote-containing injection string, print both "
                "results, and comment which line keeps the input out of the SQL text."
            ),
            patterns=["SELECT", "?", "execute("],
            mapping=(
                "Every database driver exposes parameter binding, and ORMs such as SQLAlchemy generate bound "
                "queries for the same reason. Raw SQL is fine; concatenated SQL is not."
            ),
        ),
        112: dict(
            topic="Validation at the boundary",
            idea=(
                "Validation belongs at the boundary, before data reaches storage or business logic. A request "
                "can be missing a field, carry the wrong type, use an empty string where text is required, or "
                "include keys the endpoint does not accept. Check all of those deliberately and collect every "
                "problem instead of raising on the first one, because a client fixing three fields should "
                "learn about all three in one response. Return a 422 with a stable error code and a details "
                "list naming each field and reason. Distinguish validation from parsing: malformed JSON is a "
                "400, semantically invalid fields are a 422. Be strict about types: a string price is not an "
                "integer, and a boolean is not a price even though Python treats bool as a subclass of int, so "
                "check for bool explicitly. Decide whether unknown fields are rejected or ignored; rejecting "
                "them catches client typos early. Normalise only when the rule is unambiguous, such as "
                "stripping surrounding whitespace, and never silently coerce a value that the client sent "
                "wrongly. Validation is also not authentication, and it does not replace database constraints; "
                "each layer catches a different class of mistake. Today you validate create payloads and show "
                "that nothing invalid reaches the store."
            ),
            code=(
                'def validate_book(payload):\n'
                '    errors = []\n'
                '    title = payload.get("title")\n'
                '    price = payload.get("price_cents")\n'
                '    if not isinstance(title, str) or not title.strip():\n'
                '        errors.append({"field": "title", "reason": "non-empty string required"})\n'
                '    if not isinstance(price, int) or isinstance(price, bool):\n'
                '        errors.append({"field": "price_cents", "reason": "integer required"})\n'
                '    elif price < 0:\n'
                '        errors.append({"field": "price_cents", "reason": "must be >= 0"})\n'
                '    unknown = sorted(set(payload) - {"title", "price_cents"})\n'
                '    if unknown:\n'
                '        errors.append({"field": "unknown", "reason": ", ".join(unknown)})\n'
                '    return errors\n'
                '\n'
                'cases = [\n'
                '    {"title": "Dune", "price_cents": 999},\n'
                '    {"title": "   ", "price_cents": -5},\n'
                '    {"title": "Foundation", "price_cents": "1250", "extra": True},\n'
                ']\n'
                '\n'
                'for payload in cases:\n'
                '    errors = validate_book(payload)\n'
                '    status = 201 if not errors else 422\n'
                '    print(status, payload, "->", errors or "accepted")\n'
                '\n'
                'assert validate_book(cases[0]) == []\n'
                'assert len(validate_book(cases[1])) == 2\n'
                'assert validate_book({"title": "Dune", "price_cents": True})\n'
                'print("invalid payloads stop before storage")'
            ),
            variant_b='allow only title, price_cents and in_stock, then send a payload with a published key',
            variant_c='accept a price string and report every reason it should still be rejected',
            mistakes=[
                "Raising on the first bad field, so the client needs three round trips to fix three mistakes.",
                "Treating a boolean as a valid integer because Python subclasses bool from int.",
                "Coercing a wrong type silently instead of telling the client which field is wrong.",
            ],
            q1=(
                "Why collect all validation errors instead of returning on the first one?",
                "A client can fix every reported field in one pass; failing fast turns one bad response into several avoidable round trips.",
            ),
            homework=(
                "Write `validate_book(payload)` that checks required fields, types, ranges and unknown keys, "
                "returning a list of field/reason dictionaries. Run it on two invalid payloads, print all "
                "errors, and comment which line catches a boolean masquerading as an integer."
            ),
            patterns=["def ", "errors", "return "],
            mapping=(
                "FastAPI uses Pydantic models to perform this check before the handler runs; Flask usually "
                "needs an explicit validator. Both should return one shape with per-field reasons."
            ),
        ),
        113: dict(
            topic="Consistent error handling",
            idea=(
                "Errors are part of the API contract, and a contract with five shapes is five contracts. "
                "Choose one envelope and use it for every failure: a machine-readable code, a human-readable "
                "message, and an optional details list. HTTP status carries the category, while the code "
                "carries the specific reason, so a client can branch without parsing prose. A handler should "
                "raise an application exception such as ApiError, and one wrapper should translate it into a "
                "response. That wrapper is also where unexpected exceptions are caught and converted into a "
                "generic 500. The generic response must not contain a traceback, a SQL fragment, a file path or "
                "an internal hostname; those belong in the server log, not in the client's hands. Meanwhile, "
                "expected failures should be cheap to express: a missing resource is a 404, a bad field is a "
                "422, a duplicate is a 409. Keeping all of them in one place means tests assert on one shape "
                "and clients handle one shape. Today you build the exception, the envelope and the wrapper, and "
                "print a handled validation error beside an unexpected crash. The crash still returns JSON, so "
                "even the worst path keeps the contract. The client gets a stable shape; the operator gets the "
                "detail."
            ),
            code=(
                'class ApiError(Exception):\n'
                '    def __init__(self, status, code, message, details=None):\n'
                '        self.status = status\n'
                '        self.code = code\n'
                '        self.message = message\n'
                '        self.details = details or []\n'
                '\n'
                'def error_body(code, message, details=None):\n'
                '    body = {"error": {"code": code, "message": message}}\n'
                '    if details:\n'
                '        body["error"]["details"] = details\n'
                '    return body\n'
                '\n'
                'def run(handler, request):\n'
                '    try:\n'
                '        return handler(request)\n'
                '    except ApiError as exc:\n'
                '        return exc.status, error_body(exc.code, exc.message, exc.details)\n'
                '    except Exception:\n'
                '        return 500, error_body("internal_error", "The request could not be completed")\n'
                '\n'
                'def create_book(request):\n'
                '    title = request.get("title", "").strip()\n'
                '    if not title:\n'
                '        raise ApiError(\n'
                '            422, "validation_failed", "title is required", [{"field": "title"}]\n'
                '        )\n'
                '    return 201, {"id": 1, "title": title}\n'
                '\n'
                'print("valid:", run(create_book, {"title": "Dune"}))\n'
                'print("invalid:", run(create_book, {"title": "   "}))\n'
                'print("crash:", run(lambda request: 1 / 0, {}))\n'
                '\n'
                'assert run(create_book, {})[0] == 422\n'
                'assert run(lambda request: 1 / 0, {})[1]["error"]["code"] == "internal_error"\n'
                'print("all failures share one envelope")'
            ),
            variant_b='add a 409 duplicate_title error and check that the details list stays optional',
            variant_c='raise ApiError(404, "not_found", ...) from a lookup and confirm the wrapper keeps the status',
            mistakes=[
                "Returning 200 with an error field, so clients that trust the status code treat a failure as success.",
                "Letting an unexpected exception escape as an HTML traceback from the server.",
                "Using a different error shape on every endpoint, forcing clients to special-case each one.",
            ],
            q1=(
                "Why keep both an HTTP status and an application error code?",
                "The status gives every HTTP client the category; the code names the specific reason so application code can branch without parsing the message.",
            ),
            homework=(
                "Write `run(handler, request)` that translates ApiError into a stable envelope and unexpected "
                "exceptions into a generic 500. Run it on two handlers, one raising a validation error and one "
                "raising ZeroDivisionError, print both responses, and comment which line keeps internals out."
            ),
            patterns=["class ApiError", "except", "return "],
            mapping=(
                "FastAPI's HTTPException and Flask's error handlers can emit the same envelope; the discipline "
                "is to construct every failure in one place so clients never see a second shape."
            ),
        ),
        114: dict(
            topic="Logging requests",
            idea=(
                "A request log is the API's flight recorder. Write one line per request after the response is "
                "decided, containing the method, the path, the status, the duration in milliseconds, and a "
                "request id that also appears in error responses. Use the logging module rather than print, "
                "because logging has levels, handlers and a standard format that production tools can parse. "
                "Choose the level from the outcome: INFO for success, WARNING for a client error, ERROR for a "
                "server error. Never log the request body or the Authorization header by default; passwords, "
                "tokens and personal data end up in logs that are copied, shipped and retained. Log the path "
                "without query values when those values may be sensitive, or redact known keys. Record the "
                "duration from a monotonic clock, not from wall-clock arithmetic, because wall clocks jump. The "
                "request id is what turns five scattered lines into one story when a client reports a problem. "
                "Today you log a fixed batch of requests to an in-memory stream and print the lines, so the "
                "output is deterministic and the habit is visible. Logging is part of the request lifecycle, "
                "not an afterthought added when something breaks. Silence is not an option: an unlogged "
                "request cannot be debugged after the fact."
            ),
            code=(
                'import io\n'
                'import logging\n'
                '\n'
                'stream = io.StringIO()\n'
                'logger = logging.getLogger("api.requests")\n'
                'logger.handlers.clear()\n'
                'logger.setLevel(logging.INFO)\n'
                'handler = logging.StreamHandler(stream)\n'
                'handler.setFormatter(logging.Formatter("%(levelname)s %(message)s"))\n'
                'logger.addHandler(handler)\n'
                'logger.propagate = False\n'
                '\n'
                'def log_request(method, path, status, elapsed_ms, request_id):\n'
                '    if status >= 500:\n'
                '        level = logging.ERROR\n'
                '    elif status >= 400:\n'
                '        level = logging.WARNING\n'
                '    else:\n'
                '        level = logging.INFO\n'
                '    logger.log(\n'
                '        level,\n'
                '        "method=%s path=%s status=%d elapsed_ms=%d request_id=%s",\n'
                '        method, path, status, elapsed_ms, request_id,\n'
                '    )\n'
                '\n'
                'fixtures = [\n'
                '    ("GET", "/books", 200, 12, "req-1"),\n'
                '    ("POST", "/books", 422, 3, "req-2"),\n'
                '    ("GET", "/missing", 404, 1, "req-3"),\n'
                '    ("GET", "/books/1", 500, 41, "req-4"),\n'
                ']\n'
                '\n'
                'for record in fixtures:\n'
                '    log_request(*record)\n'
                '\n'
                'text = stream.getvalue()\n'
                'print(text.strip())\n'
                'print("error lines:", sum(1 for line in text.splitlines() if line.startswith("ERROR")))\n'
                '\n'
                'assert "req-2" in text and "password" not in text\n'
                'assert text.count("request_id") == len(fixtures)\n'
                'print("one line per request, no secrets")'
            ),
            variant_b='redact the query string from one path and compare the logged line',
            variant_c='use a 401 fixture and decide whether it is WARNING, INFO or its own audit level',
            mistakes=[
                "Logging request bodies and Authorization headers, leaking secrets into a shared log store.",
                "Using print without levels, so errors and successes cannot be filtered apart.",
                "Timing with wall-clock differences, which can produce negative or wildly wrong durations.",
            ],
            q1=(
                "Why does a request id belong in both the log line and the error response?",
                "It lets a client report a failure with an identifier that finds the exact server-side line, instead of matching timestamps by guesswork.",
            ),
            homework=(
                "Write `log_request(logger, method, path, status, elapsed_ms, request_id)` that selects a level "
                "from the status and emits one structured line. Run it on two batches with different statuses, "
                "print the stream, and comment which line keeps secrets out of the log."
            ),
            patterns=["logging.", "def ", "level"],
            mapping=(
                "Production services ship structured logs to a collector; middleware in FastAPI or a Flask "
                "before/after hook is where this line is usually emitted. A request id from an incoming header "
                "connects the whole trace."
            ),
        ),
        115: dict(
            topic="CORS and browser clients",
            idea=(
                "Browsers enforce the same-origin policy: JavaScript served from one origin cannot read "
                "responses from another unless that server opts in with CORS headers. A simple request may "
                "proceed, but the browser still checks Access-Control-Allow-Origin before exposing the body. A "
                "request with JSON, a custom header or a non-simple method triggers a preflight OPTIONS "
                "request, and that preflight must be answered before normal routing, usually with 204 and no "
                "body. Return the exact origin, not a wildcard, when credentials are involved; wildcard and "
                "credentials are incompatible. Add Vary: Origin so caches do not serve one origin's permission "
                "to another. List only the methods and headers the API actually needs. An unknown origin "
                "should not receive the allow headers, and the response should still be a normal error rather "
                "than a misleading success. CORS is not authentication: it protects the browser's user, not the "
                "server, so never treat it as access control. Today you build the preflight and simple-request "
                "headers for an allowed and a disallowed origin and print both. The preflight is answered "
                "before the router, because there is no application path to look up. The browser sends Origin "
                "on cross-origin calls, and the server decides whether to echo it back."
            ),
            code=(
                'ALLOWED_ORIGINS = {"https://app.example.com"}\n'
                '\n'
                'def cors_headers(origin):\n'
                '    if origin not in ALLOWED_ORIGINS:\n'
                '        return {}\n'
                '    return {\n'
                '        "Access-Control-Allow-Origin": origin,\n'
                '        "Access-Control-Allow-Methods": "GET, POST, DELETE, OPTIONS",\n'
                '        "Access-Control-Allow-Headers": "Content-Type, Authorization",\n'
                '        "Vary": "Origin",\n'
                '    }\n'
                '\n'
                'def handle_options(request):\n'
                '    origin = request["headers"].get("Origin", "")\n'
                '    headers = cors_headers(origin)\n'
                '    if not headers:\n'
                '        return 403, {"error": {"code": "origin_not_allowed"}}, {}\n'
                '    return 204, None, headers\n'
                '\n'
                'allowed = {"headers": {"Origin": "https://app.example.com"}}\n'
                'blocked = {"headers": {"Origin": "https://evil.example.com"}}\n'
                '\n'
                'print("preflight allowed:", handle_options(allowed))\n'
                'print("preflight blocked:", handle_options(blocked))\n'
                'print("simple GET headers:", cors_headers(allowed["headers"]["Origin"]))\n'
                '\n'
                'assert handle_options(allowed)[0] == 204\n'
                'assert handle_options(blocked)[0] == 403\n'
                'assert "Access-Control-Allow-Origin" not in handle_options(blocked)[2]\n'
                'print("preflight answered before routing")'
            ),
            variant_b='allow a second origin and confirm Vary: Origin is still present on both responses',
            variant_c='add Access-Control-Allow-Credentials and explain why a wildcard origin is then invalid',
            mistakes=[
                "Answering OPTIONS through the normal router, so the preflight receives a 404 or 405.",
                "Using * together with credentials, which browsers reject and which hides the origin decision.",
                "Treating CORS as authentication and assuming a blocked origin cannot call the API directly.",
            ],
            q1=(
                "Why is a wildcard Access-Control-Allow-Origin wrong when credentials are enabled?",
                "Browsers refuse to expose a credentialed response to a wildcard origin because it would let any site read the user's authenticated data.",
            ),
            homework=(
                "Write `cors_headers(origin, allowed)` that returns the CORS headers for an allowed origin and "
                "an empty dictionary otherwise, including Vary: Origin. Run it on two origins, print both "
                "results, and comment which line prevents a cached response leaking across origins."
            ),
            patterns=["Access-Control-Allow-Origin", "OPTIONS", "Vary"],
            mapping=(
                "FastAPI's CORSMiddleware and Flask-CORS implement this handshake, including the preflight. "
                "They still need a deliberate allowlist; the library only writes the headers."
            ),
        ),
        116: dict(
            topic="Health and readiness endpoints",
            idea=(
                "Health and readiness answer different questions. Liveness asks whether the process is alive "
                "and should not be killed; it should be cheap, unauthenticated and not touch dependencies, "
                "because a slow database must not cause the orchestrator to restart a healthy process. "
                "Readiness asks whether the instance can serve traffic right now; it checks the database "
                "connection and the schema, and returns 503 when a dependency is missing so the load balancer "
                "stops sending requests. Keep both responses small and structured: a status and a mapping of "
                "checks, never credentials, connection strings or stack traces. Do not run an expensive query "
                "on every probe; SELECT 1 and a schema existence check are enough. A readiness check that "
                "always returns 200 is worse than none, because it makes a broken deployment look healthy. A "
                "liveness check that checks the database is also worse than none, because it turns a "
                "dependency outage into a restart loop. Today you implement both against an in-memory database, "
                "once with the table present and once without, and show the 200 and 503 outcomes. The two "
                "endpoints are deliberately boring; boring probes are reliable probes. Keep the two routes "
                "separate even when they share a helper; their failure meanings differ."
            ),
            code=(
                'import sqlite3\n'
                '\n'
                'def health():\n'
                '    return 200, {"status": "ok"}\n'
                '\n'
                'def readiness(conn):\n'
                '    checks = {}\n'
                '    try:\n'
                '        conn.execute("SELECT 1").fetchone()\n'
                '        checks["database"] = "ok"\n'
                '        tables = conn.execute(\n'
                '            "SELECT name FROM sqlite_master WHERE type=\'table\'"\n'
                '        ).fetchall()\n'
                '        has_books = any(name == "books" for (name,) in tables)\n'
                '        checks["schema"] = "ok" if has_books else "missing"\n'
                '    except sqlite3.Error:\n'
                '        checks["database"] = "error"\n'
                '        checks["schema"] = "unknown"\n'
                '    status = 200 if all(value == "ok" for value in checks.values()) else 503\n'
                '    state = "ready" if status == 200 else "not_ready"\n'
                '    return status, {"status": state, "checks": checks}\n'
                '\n'
                'healthy = sqlite3.connect(":memory:")\n'
                'healthy.execute("CREATE TABLE books (id INTEGER PRIMARY KEY)")\n'
                'empty = sqlite3.connect(":memory:")\n'
                '\n'
                'print("GET /health ->", health())\n'
                'print("GET /ready healthy ->", readiness(healthy))\n'
                'print("GET /ready empty ->", readiness(empty))\n'
                '\n'
                'assert health()[0] == 200\n'
                'assert readiness(healthy)[0] == 200\n'
                'assert readiness(empty)[0] == 503\n'
                'print("liveness and readiness answer different questions")'
            ),
            variant_b='close the database before the readiness call and inspect the sqlite3 error branch',
            variant_c='add a second required table to the schema check and show the 503 until it exists',
            mistakes=[
                "Checking the database in the liveness probe, turning an outage into a restart loop.",
                "Returning 200 from readiness unconditionally, so bad deployments receive traffic.",
                "Exposing connection strings or exception text in the probe response.",
            ],
            q1=(
                "Why should liveness avoid checking the database?",
                "A dependency outage is not a reason to restart a healthy process; liveness should only report whether the process itself is running.",
            ),
            homework=(
                "Write `readiness(conn)` that runs SELECT 1, checks for the books table, and returns 200 or 503 "
                "with a checks mapping. Run it on two connections, one with the table and one without, print "
                "both responses, and comment which line makes a missing schema visible."
            ),
            patterns=["SELECT 1", "503", "def "],
            mapping=(
                "Kubernetes uses liveness and readiness probes with exactly this split; cloud load balancers "
                "use the readiness endpoint as a health check target. FastAPI and Flask expose them as ordinary "
                "routes."
            ),
        ),
        117: dict(
            topic="Graceful shutdown and restarts",
            idea=(
                "A clean shutdown is a sequence, not a single call. Stop accepting new requests, mark the "
                "instance not ready so the load balancer drains it, let in-flight requests finish up to a "
                "timeout, then commit or roll back, close the database and exit. On SIGTERM a server gets a "
                "short grace period; work that ignores it is killed, and a half-written transaction is exactly "
                "what the grace period exists to prevent. The database connection must be closed after the "
                "drain, not before, or the last requests fail for no good reason. Restart safety is the other "
                "half: every startup should be able to run against an existing database, so schema creation "
                "uses IF NOT EXISTS and migrations are idempotent. A restart must not duplicate rows or erase "
                "committed data. Test the sequence by starting a server object, sending a request, shutting it "
                "down, and starting a new one against the same schema. Today you simulate that with an "
                "in-memory database, print the refusal after shutdown, and prove the second start creates the "
                "table without error. The flag that stops accepting work is the first line of defence, not the "
                "last. A shutdown that skips the drain drops work the client already considers sent."
            ),
            code=(
                'import sqlite3\n'
                '\n'
                'class Server:\n'
                '    def __init__(self, conn):\n'
                '        self.conn = conn\n'
                '        self.accepting = True\n'
                '        self.in_flight = 0\n'
                '        self.closed = False\n'
                '\n'
                '    def begin(self):\n'
                '        if not self.accepting:\n'
                '            return 503, {"error": {"code": "shutting_down"}}\n'
                '        self.in_flight += 1\n'
                '        return 200, {"status": "started"}\n'
                '\n'
                '    def finish(self):\n'
                '        self.in_flight -= 1\n'
                '\n'
                '    def request(self, work):\n'
                '        status, _ = self.begin()\n'
                '        if status != 200:\n'
                '            return status\n'
                '        try:\n'
                '            return work(self.conn)\n'
                '        finally:\n'
                '            self.finish()\n'
                '\n'
                '    def shutdown(self):\n'
                '        self.accepting = False\n'
                '        while self.in_flight:\n'
                '            self.in_flight -= 1\n'
                '        self.conn.commit()\n'
                '        self.conn.close()\n'
                '        self.closed = True\n'
                '\n'
                'def write_book(conn):\n'
                '    conn.execute(\n'
                '        "CREATE TABLE IF NOT EXISTS books (id INTEGER PRIMARY KEY, title TEXT)"\n'
                '    )\n'
                '    conn.execute("INSERT INTO books (title) VALUES (?)", ("Dune",))\n'
                '    return 201\n'
                '\n'
                'conn = sqlite3.connect(":memory:")\n'
                'server = Server(conn)\n'
                'print("request before shutdown:", server.request(write_book))\n'
                'server.shutdown()\n'
                'print("accepting:", server.accepting, "| closed:", server.closed)\n'
                'print("request after shutdown:", server.request(write_book))\n'
                '\n'
                'restarted = Server(sqlite3.connect(":memory:"))\n'
                'print("restart migration:", restarted.request(write_book))\n'
                '\n'
                'assert server.closed and not server.accepting\n'
                'assert restarted.request(write_book) == 201\n'
                'print("shutdown drained and restart is idempotent")'
            ),
            variant_b='raise in the middle of work and confirm finish still runs so in_flight returns to zero',
            variant_c='remove IF NOT EXISTS and run the restart twice; explain which error the second start sees',
            mistakes=[
                "Closing the database before in-flight requests finish, so the last responses fail.",
                "Running a non-idempotent startup that duplicates rows every time the process restarts.",
                "Ignoring SIGTERM and forcing the orchestrator to kill the process mid-transaction.",
            ],
            q1=(
                "Why set the shutdown flag before draining in-flight requests?",
                "New work must stop entering while existing work finishes; without the flag, the drain never catches up and the server keeps accepting requests.",
            ),
            homework=(
                "Write `Server.shutdown()` for a class that tracks accepting and in_flight, draining work before "
                "closing the connection. Run it on two cases, a request before shutdown and a restart on a fresh "
                "database, print both outcomes, and comment which line makes the restart schema idempotent."
            ),
            patterns=["IF NOT EXISTS", "shutdown", "finally:"],
            mapping=(
                "SIGTERM handlers, Kubernetes preStop hooks and ASGI lifespan events all implement this drain. "
                "The idempotent migration is the same reason every framework's migration tool records which "
                "versions have already run."
            ),
        ),
        118: dict(
            topic="Serving file responses",
            idea=(
                "An API often returns files, not just JSON: a report, an image, a CSV export. The response is "
                "bytes and needs three headers to be correct: Content-Type from the file extension, "
                "Content-Length in bytes, and a sensible Content-Disposition. Guess the type with mimetypes "
                "rather than hardcoding it, and fall back to application/octet-stream for unknown extensions. "
                "For large files, stream in chunks instead of reading everything into memory; the client starts "
                "receiving data sooner and the server stays within its memory budget. Security starts with the "
                "path. Join the requested name to a fixed root, normalise the result, and reject anything that "
                "escapes the root, because a parent-directory segment is the classic way to read a file the "
                "endpoint never intended to expose. Return a structured 404 for a missing file, not an empty "
                "200. Decide whether the file should download or display, and set Content-Disposition "
                "accordingly. Today you serve files from an in-memory registry, test a normal path and a "
                "traversal attempt, and print the headers and byte lengths. The path check is part of the "
                "endpoint's contract, not a detail of the filesystem. The response is still a normal HTTP "
                "response; only the body happens to be bytes from a file."
            ),
            code=(
                'import mimetypes\n'
                'import posixpath\n'
                '\n'
                'FILES = {\n'
                '    "reports/books.json": b\'{"items": ["Dune"]}\',\n'
                '    "reports/cover.png": b"\\x89PNG\\r\\n\\x1a\\n",\n'
                '}\n'
                '\n'
                'def safe_path(raw):\n'
                '    cleaned = posixpath.normpath("/" + raw).lstrip("/")\n'
                '    return cleaned if cleaned in FILES else None\n'
                '\n'
                'def file_response(raw_path):\n'
                '    path = safe_path(raw_path)\n'
                '    if path is None:\n'
                '        return 404, {"Content-Type": "application/json"}, b\'{"error":{"code":"not_found"}}\'\n'
                '    body = FILES[path]\n'
                '    content_type, _ = mimetypes.guess_type(path)\n'
                '    headers = {\n'
                '        "Content-Type": content_type or "application/octet-stream",\n'
                '        "Content-Length": str(len(body)),\n'
                '        "Content-Disposition": \'inline; filename="\' + posixpath.basename(path) + \'"\',\n'
                '    }\n'
                '    return 200, headers, body\n'
                '\n'
                'for path in ["reports/books.json", "reports/cover.png", "../app.conf", "reports/missing.txt"]:\n'
                '    status, headers, body = file_response(path)\n'
                '    print(path, "->", status, headers.get("Content-Type"), len(body))\n'
                '\n'
                'assert file_response("../app.conf")[0] == 404\n'
                'assert file_response("reports/books.json")[1]["Content-Length"] == str(\n'
                '    len(FILES["reports/books.json"])\n'
                ')\n'
                'assert file_response("reports/cover.png")[1]["Content-Type"] == "image/png"\n'
                'print("paths normalised, errors typed, lengths honest")'
            ),
            variant_b='serve the JSON file as an attachment and change Content-Disposition to attachment',
            variant_c='request "reports/../reports/books.json" and confirm normalisation still lands inside the root',
            mistakes=[
                "Joining the raw user path to a directory without normalising it, permitting parent-directory escapes.",
                "Reading a whole large file into memory when streaming would keep the server responsive.",
                "Hardcoding application/octet-stream for every file, so browsers cannot display known types.",
            ],
            q1=(
                "Why normalise and check the requested path before looking up a file?",
                "Normalisation exposes parent-directory segments, so the check can reject anything outside the root before the filesystem or registry is touched.",
            ),
            homework=(
                "Write `file_response(raw_path, files)` that normalises the path, rejects traversal and missing "
                "entries, and returns a content type and byte length. Run it on two paths, one valid and one "
                "traversal attempt, print both responses, and comment which line keeps the lookup inside the root."
            ),
            patterns=["mimetypes", "Content-Length", "normpath"],
            mapping=(
                "FastAPI's FileResponse and Flask's send_file set these headers and stream the body; both still "
                "expect you to constrain the path. The traversal check is application logic, not framework magic."
            ),
        ),
        119: dict(
            topic="Review: a working JSON API",
            idea=(
                "Today the pieces become one small API. A request arrives, the router chooses a handler, the "
                "body is parsed, the payload is validated, the database is queried through placeholders, and "
                "the response is serialised with a consistent envelope. Errors from any stage come back through "
                "the same constructor, and every request leaves a log line. Every route returns one envelope, "
                "so success and failure are observable in the same place. None of these pieces is large on its "
                "own; the achievement is that they agree. "
                "Test the whole path rather than each function in isolation: create a book, list the "
                "collection, fetch the new id, send an invalid body, request an unknown route, and confirm that "
                "the statuses and shapes match the contract. This is the point where a framework starts to look "
                "attractive, and it should: FastAPI and Flask automate exactly this plumbing. But you now know "
                "what the automation is doing, so a strange 422 or a missing CORS header is a familiar line of "
                "code rather than magic. Keep the fixture-driven test; it will catch regressions when you port "
                "the API. A working small API is mostly a set of agreements kept in one place, and that "
                "agreement is the product."
            ),
            code=(
                'import json\n'
                'import sqlite3\n'
                '\n'
                'class LibraryAPI:\n'
                '    def __init__(self):\n'
                '        self.conn = sqlite3.connect(":memory:")\n'
                '        self.conn.row_factory = sqlite3.Row\n'
                '        self.conn.execute(\n'
                '            "CREATE TABLE books (id INTEGER PRIMARY KEY, title TEXT NOT NULL)"\n'
                '        )\n'
                '        self.log = []\n'
                '\n'
                '    def error(self, status, code, message):\n'
                '        return status, {"Content-Type": "application/json"}, {\n'
                '            "error": {"code": code, "message": message}\n'
                '        }\n'
                '\n'
                '    def ok(self, status, payload):\n'
                '        return status, {"Content-Type": "application/json"}, payload\n'
                '\n'
                '    def dispatch(self, method, path, request):\n'
                '        if method == "GET" and path == "/books":\n'
                '            rows = self.conn.execute(\n'
                '                "SELECT id, title FROM books ORDER BY id"\n'
                '            ).fetchall()\n'
                '            items = [dict(row) for row in rows]\n'
                '            return self.ok(200, {"items": items, "count": len(items)})\n'
                '        if method == "POST" and path == "/books":\n'
                '            try:\n'
                '                payload = json.loads(request.get("body", ""))\n'
                '            except json.JSONDecodeError:\n'
                '                return self.error(400, "malformed_json", "Body is not valid JSON")\n'
                '            if not isinstance(payload, dict):\n'
                '                return self.error(422, "validation_failed", "Object required")\n'
                '            title = payload.get("title")\n'
                '            if not isinstance(title, str) or not title.strip():\n'
                '                return self.error(422, "validation_failed", "title is required")\n'
                '            cur = self.conn.execute(\n'
                '                "INSERT INTO books (title) VALUES (?)", (title.strip(),)\n'
                '            )\n'
                '            self.conn.commit()\n'
                '            return self.ok(201, {"id": cur.lastrowid, "title": title.strip()})\n'
                '        if method == "GET" and path.startswith("/books/"):\n'
                '            try:\n'
                '                book_id = int(path.rsplit("/", 1)[1])\n'
                '            except ValueError:\n'
                '                return self.error(404, "not_found", "Book does not exist")\n'
                '            row = self.conn.execute(\n'
                '                "SELECT id, title FROM books WHERE id = ?", (book_id,)\n'
                '            ).fetchone()\n'
                '            if row is None:\n'
                '                return self.error(404, "not_found", "Book does not exist")\n'
                '            return self.ok(200, dict(row))\n'
                '        return self.error(404, "not_found", "Route does not exist")\n'
                '\n'
                '    def handle(self, request):\n'
                '        status, headers, body = self.dispatch(\n'
                '            request["method"], request["path"], request\n'
                '        )\n'
                '        self.log.append(\n'
                '            {"method": request["method"], "path": request["path"], "status": status}\n'
                '        )\n'
                '        return status, headers, body\n'
                '\n'
                'api = LibraryAPI()\n'
                'requests = [\n'
                '    {"method": "POST", "path": "/books", "body": \'{"title": "Dune"}\'},\n'
                '    {"method": "POST", "path": "/books", "body": \'{"title": "   "}\'},\n'
                '    {"method": "POST", "path": "/books", "body": "{oops"},\n'
                '    {"method": "GET", "path": "/books", "body": ""},\n'
                '    {"method": "GET", "path": "/books/1", "body": ""},\n'
                '    {"method": "GET", "path": "/authors", "body": ""},\n'
                ']\n'
                '\n'
                'for request in requests:\n'
                '    status, headers, body = api.handle(request)\n'
                '    print(request["method"], request["path"], "->", status, body)\n'
                '\n'
                'assert api.handle({"method": "POST", "path": "/books", "body": "{}"})[0] == 422\n'
                'assert len(api.log) == len(requests) + 1\n'
                'print("every layer agrees on one contract")'
            ),
            variant_b='add DELETE /books/{id} returning 204 and confirm the list shrinks after the call',
            variant_c='add a 409 for a duplicate title and explain which layer should raise it',
            mistakes=[
                "Letting each endpoint invent its own error shape instead of reusing the constructor.",
                "Testing only the happy path, so validation, routing and storage failures go unnoticed.",
                "Skipping the log append, so a request that changed state leaves no trace.",
            ],
            q1=(
                "Why test the whole request path instead of only each helper function?",
                "The contract lives in the composition: routing, parsing, validation, storage and serialisation can each pass alone while disagreeing at the boundary.",
            ),
            homework=(
                "Write a `LibraryAPI` whose `handle(request)` routes health, list, create and fetch-by-id "
                "through one SQLite connection and one error envelope. Run two full request batches, print every "
                "status and body, and comment which line keeps the handlers from inventing a second error shape."
            ),
            patterns=["def handle(", "sqlite3", "return "],
            mapping=(
                "This is the skeleton FastAPI or Flask would wrap: the framework supplies the socket, the "
                "router and the JSON encoder, while validation, storage and error policy remain your code."
            ),
        ),
    },
)
