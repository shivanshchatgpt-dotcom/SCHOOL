"""API Building phase 1, days 75-89: HTTP foundations for APIs.

Fifteen hand-authored days on designing and speaking HTTP. Every worked example
is stdlib-only and runs offline against in-memory request/response fixtures, so
no lesson binds a socket or imports a framework. Query strings are parsed with
urllib to keep the examples honest about how parameters actually arrive.
"""

PHASE = (
    "HTTP Foundations for APIs",
    "Learn to design and speak HTTP APIs by modelling requests, responses, status codes and errors with stdlib Python.",
    {
        75: dict(
            topic="Orientation: what an API is",
            idea=(
                "An API is a promise between two programs: a client sends a request describing what it wants, and a "
                "server replies with a result or a reason it could not comply. The request names a resource with a "
                "path, chooses an action with a method, carries metadata in headers, and may include a body. The "
                "response carries a status code, its own headers, and usually a body. What makes this an interface "
                "rather than a function call is that both sides agree only on the shape of the messages, not on each "
                "other's code, language, or database. That separation is why a mobile app, a browser, and a "
                "command-line tool can all talk to the same service. The contract has to be explicit because the two "
                "sides ship independently: a field you promise today is a field a client will depend on next year. So "
                "an API is really a published boundary with rules about inputs, outputs, and failures. Today you "
                "build the smallest possible version by hand, a request dictionary in and a status plus body out, so "
                "the message shape is visible before any framework hides it. Keep an eye on which parts of the reply "
                "are data and which parts are metadata, because clients use both."
            ),
            code=r'''import json


def api(method, path, body=None):
    if method == "GET" and path == "/books/1":
        return {"status": 200, "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"id": 1, "title": "Dune"})}
    return {"status": 404, "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": {"code": "not_found"}})}


request = {"method": "GET", "path": "/books/1", "headers": {}, "body": None}
response = api(request["method"], request["path"], request["body"])
print("request:", request["method"], request["path"])
print("status:", response["status"])
print("content-type:", response["headers"]["Content-Type"])
print("body:", response["body"])
assert response["status"] == 200
assert json.loads(response["body"])["title"] == "Dune"
print("one request, one response, one contract")
''',
            variant_b="a POST /books request with a JSON body, and the status it should return",
            variant_c="a request for an unknown path and the structured 404 it should produce",
            mistakes=[
                "Confusing the interface with the implementation, so the message shape is never written down.",
                "Returning a bare value with no status, so the client cannot tell success from failure.",
                "Letting a client depend on an undocumented field that a later change removes.",
            ],
            q1=("What makes an API a contract rather than a function call?",
                "Both sides agree on the message shapes, method, path, headers, status and body, while staying free to change their own implementation."),
            homework=(
                "Write `describe_api(request)` that takes a request dictionary with method, path, headers and body "
                "and returns a status plus a JSON body string describing the resource. Run it on two different "
                "requests, print both status and body pairs, and comment which line makes the response a contract "
                "rather than a bare value."
            ),
            patterns=["def ", "return", "print("],
            mapping=(
                "Every framework, FastAPI, Flask, Django REST or Express, exists to build these request and response "
                "messages, and each one hands you the same method, path, headers and body. Knowing the message shape "
                "makes the framework a convenience rather than a mystery."
            ),
        ),
        76: dict(
            topic="Methods and what they mean",
            idea=(
                "A method states what a request does to a resource, and the small set of standard methods is a shared "
                "vocabulary clients already understand. GET reads a representation and must not change server state. "
                "POST submits data, usually creating a subordinate resource, and is neither safe nor idempotent. PUT "
                "replaces a resource at a known URL and is idempotent: sending it twice leaves the same result. PATCH "
                "applies a partial modification. DELETE removes a resource and is also idempotent, because deleting "
                "something already gone should not create a second effect. Two properties organise all of this. Safe "
                "methods cause no intended change, so crawlers and caches may retry them freely. Idempotent methods "
                "may change state but repeated identical requests converge to one outcome, which is what makes "
                "retries after a timeout survivable. Confusing POST with PUT is the classic bug: a client retries a "
                "timed-out POST and accidentally creates two orders. Choosing the method carefully is how you decide "
                "whether a retry is harmless or dangerous before writing a single handler. Treat the method table as "
                "documentation of your service's retry behaviour. It is also how a client decides whether it "
                "may retry a failed request without asking a human first."
            ),
            code=r'''methods = {
    "GET": {"safe": True, "idempotent": True, "effect": "read"},
    "POST": {"safe": False, "idempotent": False, "effect": "create"},
    "PUT": {"safe": False, "idempotent": True, "effect": "replace"},
    "PATCH": {"safe": False, "idempotent": False, "effect": "modify"},
    "DELETE": {"safe": False, "idempotent": True, "effect": "remove"},
}

for name in ["GET", "POST", "PUT", "DELETE"]:
    props = methods[name]
    print(name, "safe=" + str(props["safe"]), "idempotent=" + str(props["idempotent"]))

retry_safe = [m for m, p in methods.items() if p["safe"] or p["idempotent"]]
print("retry without creating a duplicate:", sorted(retry_safe))
assert "POST" not in retry_safe and "PUT" in retry_safe
print("method choice decides whether retries are safe")
''',
            variant_b="PATCH applied to one field, and whether it is idempotent",
            variant_c="HEAD on /books, which is both safe and idempotent",
            mistakes=[
                "Using GET for a request that changes state, so caches and crawlers mutate data.",
                "Treating POST as idempotent and retrying it after a timeout, creating duplicates.",
                "Choosing PUT when only part of the resource changes, forcing the client to send every field.",
            ],
            q1=("Why does it matter whether POST is idempotent?",
                "A retried POST can create a second resource, so clients must not blindly retry it the way they may retry PUT or DELETE."),
            homework=(
                "Write `method_properties()` that returns a dictionary mapping each of GET, POST, PUT and DELETE to "
                "whether it is safe and whether it is idempotent. Call it, print each method with both flags, and "
                "comment which line decides whether a retried request can create a duplicate."
            ),
            patterns=["def ", "for ", "print("],
            mapping=(
                "FastAPI's @app.get versus @app.post and Flask's methods=[...] are just declarations of this "
                "semantic choice. Getting the method wrong is a data-integrity bug, not a style issue, because retry "
                "behaviour follows directly from it."
            ),
        ),
        77: dict(
            topic="Status codes as a contract",
            idea=(
                "A status code is the first thing a client reads and often the only thing an intermediary acts on. The "
                "first digit is the category: 2xx means success, 3xx means the resource moved or a cached version "
                "applies, 4xx means the client's request is wrong, and 5xx means the server failed. The specific code "
                "adds precision inside that category. 200 is fine for a successful read, 201 when a POST created "
                "something and should come with a Location header, and 204 when there is genuinely no body to "
                "return. In the 4xx family, 400 is a malformed request, 401 missing or bad credentials, 403 valid "
                "credentials without permission, 404 no such resource, 409 a conflict with current state, and 422 "
                "syntactically valid but semantically wrong fields. The 5xx family says the fault is yours, not the "
                "caller's, and should never expose internals. The contract point is subtle: clients write control "
                "flow against these numbers, so returning 200 with an error field inside breaks every generic "
                "handler. Pick the code first, then shape the body to match it. A status is a summary decision, and "
                "the body expands it. A well-chosen status tells the truth even when the body is long, "
                "short, or entirely absent."
            ),
            code=r'''def category(status):
    names = {2: "success", 3: "redirect", 4: "client error", 5: "server error"}
    return names[status // 100]


cases = [
    (200, "read succeeded"),
    (201, "resource created"),
    (400, "malformed body"),
    (401, "missing token"),
    (404, "no such book"),
    (422, "invalid field"),
    (500, "server bug"),
]
for status, why in cases:
    print(status, category(status), "|", why)

client_errors = [s for s, _ in cases if s // 100 == 4]
print("client errors:", client_errors)
assert category(422) == "client error" and 201 in [s for s, _ in cases]
print("the first digit carries the category")
''',
            variant_b="a 201 with a Location header and explain why not 200",
            variant_c="a 409 conflict on a duplicate title",
            mistakes=[
                "Returning 200 with an error field, which lies to every generic client and cache.",
                "Using 404 for a validation failure when 422 states the body was understood but rejected.",
                "Exposing a stack trace in a 500 instead of a generic server-error message.",
            ],
            q1=("Why is returning 200 with an error field inside a problem?",
                "Generic clients and caches trust the status line, and a 200 claims success, so their error handling never fires."),
            homework=(
                "Write `classify(status)` that returns the category word for a status code together with a short "
                "reason, then use it to print four codes of your choice. Run it on two different sets of codes, "
                "print every line, and comment which line separates a client error from a server error."
            ),
            patterns=["def ", "print(", "return"],
            mapping=(
                "FastAPI's status_code argument and Flask's returned tuples both set this contract. HTTP clients, "
                "proxies and caches branch on the number, which is why the body alone can never substitute for it."
            ),
        ),
        78: dict(
            topic="Headers: content type and auth",
            idea=(
                "Headers are the envelope around the body, carrying facts the body cannot state about itself. "
                "Content-Type tells the receiver how to interpret the bytes and, for requests with a body, is "
                "mandatory. Accept says what the sender is willing to receive back. Authorization carries proof of "
                "identity, usually a bearer token or credentials, and must travel over TLS because it is not "
                "encrypted by HTTP itself. Content-Length or Transfer-Encoding describes the framing, while caching "
                "headers such as Cache-Control decide how long a response may be reused. Case does not matter: "
                "Content-Type and content-type are the same header, so any code that fetches a header must normalise "
                "the name. Many implementations use a structure that is case-insensitive by design, which is why you "
                "should never rely on the exact spelling from a raw log. When a request is rejected before its body "
                "is even read, the reason is almost always a header: a missing token, an unsupported content type, or "
                "a version the server will not serve. Treat headers as part of the contract, not decoration, because "
                "they decide whether a handler ever runs. Normalise the names once, at the boundary, so every "
                "handler downstream can trust the value it reads."
            ),
            code=r'''headers = {"Content-Type": "application/json", "Authorization": "Bearer tok-123"}


def get_header(headers, name):
    lowered = {k.lower(): v for k, v in headers.items()}
    return lowered.get(name.lower())


print("content type:", get_header(headers, "content-type"))
token = get_header(headers, "AUTHORIZATION")
print("authorised:", token is not None and token.startswith("Bearer "))
print("missing header:", get_header(headers, "X-Trace-Id"))
assert get_header(headers, "CONTENT-TYPE") == "application/json"
assert get_header(headers, "authorization").endswith("tok-123")
print("header lookup ignores case")
''',
            variant_b="an Authorization header with a malformed scheme",
            variant_c="a request missing Content-Type but carrying a body",
            mistakes=[
                "Fetching a header with exact case, so Content-Type and content-type are treated as different.",
                "Sending Authorization over plain HTTP, exposing the token to anyone on the path.",
                "Declaring Content-Type: application/json while sending form-encoded bytes.",
            ],
            q1=("Why must header lookup ignore case?",
                "Header names are case-insensitive on the wire, so raw log spellings differ from code constants and an exact match silently misses."),
            homework=(
                "Write `header(headers, name)` that looks a header up case-insensitively and returns its value or "
                "None when it is absent. Run it on two different header dictionaries, print both lookups including "
                "a missing header, and comment which line makes the lookup independent of spelling."
            ),
            patterns=["def ", "print(", ".lower()"],
            mapping=(
                "FastAPI's Header dependency, Flask's request.headers and Starlette's Headers all normalise case for "
                "you. Auth middleware runs before your handler precisely because a missing or invalid Authorization "
                "header must be rejected at the boundary."
            ),
        ),
        79: dict(
            topic="Query parameters: filter, sort, page",
            idea=(
                "Query parameters refine a collection request without changing which resource you are addressing. "
                "They live after the question mark as key and value pairs joined by ampersands, and a single key may "
                "repeat. The three jobs you will implement most are filtering, sorting, and paging. Filtering narrows "
                "rows, for example status=active. Sorting chooses an order, often sort=-created_at where a leading "
                "minus means descending, which keeps the parameter a single token rather than two. Paging bounds the "
                "response, usually with page and per_page together, or an offset and a limit. The defaults matter as "
                "much as the names, because a client that sends no parameters still gets a sensible, documented "
                "result. Everything arriving in the query string is text, so numeric limits and booleans must be "
                "parsed and validated rather than trusted, and an unknown sort field should be a clear error instead "
                "of a silent fallback. Because parameters are optional by nature, the handler reads them defensively, "
                "applies each only when present, and never assumes order. Compose the three ideas in one function and "
                "the collection becomes an interface. Document the defaults next to the endpoint name, so a "
                "client knows what an empty query string returns without having to probe for it."
            ),
            code=r'''from urllib.parse import parse_qs

books = [
    {"id": 1, "title": "Dune", "year": 1965, "status": "active"},
    {"id": 2, "title": "Foundation", "year": 1951, "status": "active"},
    {"id": 3, "title": "Hyperion", "year": 1989, "status": "archived"},
]


def list_books(raw_query):
    params = {k: v[0] for k, v in parse_qs(raw_query).items()}
    rows = [b for b in books if params.get("status", b["status"]) == b["status"]]
    sort = params.get("sort", "id")
    field = sort.lstrip("-")
    rows.sort(key=lambda b: b[field], reverse=sort.startswith("-"))
    per_page = int(params.get("per_page", 2))
    page = int(params.get("page", 1))
    start = (page - 1) * per_page
    return rows[start:start + per_page]


print("default:", [b["id"] for b in list_books("")])
print("active, sort=-year:", [b["id"] for b in list_books("status=active&sort=-year")])
print("page 2:", [b["id"] for b in list_books("per_page=2&page=2")])
assert [b["id"] for b in list_books("status=active&sort=-year")] == [1, 2]
print("filter, sort and page compose")
''',
            variant_b="sort=title ascending instead of descending",
            variant_c="per_page=1&page=3 on the same fixture",
            mistakes=[
                "Trusting per_page from the query string without a maximum, so one request can dump the table.",
                "Ignoring an unknown sort field instead of returning an error for it.",
                "Applying filters after paging, so a page can come back empty while matching rows exist.",
            ],
            q1=("Why should an unknown sort field be an error rather than ignored?",
                "Silently ignoring it returns a plausible but differently ordered list, hiding the client's typo and keeping the bug invisible."),
            homework=(
                "Write `list_books(raw_query)` that parses a query string, filters by status, sorts by a field with "
                "an optional leading minus, and pages with per_page and page. Run it on two different query strings, "
                "print the id lists, and comment which line applies the descending order."
            ),
            patterns=["def ", "parse_qs", "print("],
            mapping=(
                "FastAPI models these as typed Query parameters with defaults, and Flask reads request.args. The "
                "parsing and clamping you do by hand is exactly what those declarations generate for you."
            ),
        ),
        80: dict(
            topic="Path parameters and identifiers",
            idea=(
                "Path parameters identify which resource a request concerns, and they sit inside the path rather than "
                "the query because they name the thing, not refine it. The pattern GET /books/{id} promises that the "
                "segment after /books is an identifier. The handler extracts that segment as text and converts it to "
                "the type its store expects, usually an integer or an opaque string. Conversion is a contract "
                "decision: if a client sends /books/abc and the identifier must be numeric, the right answer is a 404 "
                "or a 422, never a 500 from an unhandled parse error. Opaque identifiers, such as slugs or UUID-like "
                "tokens, should be treated as strings and matched exactly, while numeric ids invite range and sign "
                "validation. A path parameter is part of the resource's address, so changing its meaning breaks "
                "bookmarks and caches, unlike a query parameter that merely tweaks a view. Nested resources, like "
                "/authors/{author_id}/books/{book_id}, express containment and often require checking that the child "
                "truly belongs to the parent before returning it. Validate the shape first, then look it up. Treat the "
                "identifier as untrusted text until your store's own type system has accepted it, and query "
                "the store exactly once."
            ),
            code=r'''store = {1: {"id": 1, "title": "Dune"}, 2: {"id": 2, "title": "Foundation"}}


def get_book(path):
    parts = path.strip("/").split("/")
    if len(parts) != 2 or parts[0] != "books":
        return 404, {"error": {"code": "not_found"}}
    raw = parts[1]
    if not raw.isdigit():
        return 422, {"error": {"code": "invalid_id"}}
    book = store.get(int(raw))
    if book is None:
        return 404, {"error": {"code": "not_found"}}
    return 200, {"data": book}


for path in ["/books/1", "/books/7", "/books/abc", "/books/1/reviews"]:
    print(path, "->", get_book(path))
assert get_book("/books/abc")[0] == 422
assert get_book("/books/1")[1]["data"]["title"] == "Dune"
print("path identifiers are text until validated")
''',
            variant_b="/authors/5/books/2, a nested path parameter",
            variant_c="/books/0, an id that is numeric but absent",
            mistakes=[
                "Letting a non-numeric id raise an unhandled error instead of returning 404 or 422.",
                "Comparing an id as text in one place and as an integer elsewhere, so /books/01 misses.",
                "Changing what a path parameter means, which breaks bookmarks and caches.",
            ],
            q1=("Why is /books/abc not a 500?",
                "A non-numeric identifier is invalid client input that must be validated and answered with 404 or 422, not an unhandled parse crash."),
            homework=(
                "Write `get_book(path)` that extracts an identifier from a path, validates it is numeric, and "
                "returns 200, 404 or 422 with a structured body. Run it on two different paths, print both "
                "responses, and comment which line turns the text segment into a typed value."
            ),
            patterns=["def ", "split(", "print("],
            mapping=(
                "FastAPI's path converters and Flask's `<int:id>` rule automate the text-to-type step you wrote by "
                "hand. The 404-versus-422 decision is still yours to make, and the framework will not make it for you."
            ),
        ),
        81: dict(
            topic="Request bodies and JSON contracts",
            idea=(
                "A request body carries the data a client wants to submit, and for JSON APIs it is a JSON document "
                "whose shape is part of the contract. The handler parses the text, confirms it is an object when one "
                "is required, checks required fields, and checks the type of each field before trusting it. Missing "
                "and wrong-type values are different failures: a missing required field and a string where an integer "
                "belongs both deserve a 422 with a specific field list, while an unparseable body deserves a 400. "
                "Additional properties are a policy choice; by default many APIs ignore unknown fields, but strict "
                "ones reject them to catch typos early. The body is untrusted input at a trust boundary, so "
                "validation happens before any storage or side effect, and the handler works only with clean values "
                "afterwards. Sending the response back with the created resource and its generated id lets the "
                "client stop guessing about server-assigned data. A body contract written down once saves every "
                "client a round of trial and error. A short schema in the documentation, naming each field "
                "and its type, removes most of the guesswork a client would otherwise do. Validate the whole "
                "body completely, then mutate."
            ),
            code=r'''import json


def create_book(request):
    try:
        data = json.loads(request["body"])
    except json.JSONDecodeError:
        return 400, {"error": {"code": "malformed_json"}}
    if not isinstance(data, dict):
        return 422, {"error": {"code": "body_must_be_object"}}
    missing = [f for f in ("title", "year") if f not in data]
    if missing:
        return 422, {"error": {"code": "missing_fields", "fields": missing}}
    if not isinstance(data["year"], int) or isinstance(data["year"], bool):
        return 422, {"error": {"code": "invalid_type", "field": "year"}}
    return 201, {"id": 10, "title": data["title"], "year": data["year"]}


cases = [
    '{"title": "Dune", "year": 1965}',
    '{"title": "Dune"}',
    '{"title": "Dune", "year": "1965"}',
    "not json",
]
for body in cases:
    status, payload = create_book({"body": body})
    print(status, payload)
assert create_book({"body": cases[0]})[0] == 201
assert create_book({"body": cases[1]})[0] == 422
print("validate the body before trusting a field")
''',
            variant_b="a body with an extra unknown field and decide whether to reject it",
            variant_c="a body with year as a boolean instead of an integer",
            mistakes=[
                "Mutating storage before the body has passed validation.",
                "Accepting a missing required field and storing a null where a value belongs.",
                "Trusting a field's type because the JSON parsed, when a string arrived where an integer was required.",
            ],
            q1=("Why check field types after parsing JSON?",
                "Valid JSON can still carry a string where an integer is required, so type checks turn that into a 422 instead of a deep failure later."),
            homework=(
                "Write `create_book(request)` that parses a JSON body, checks required fields and their types, and "
                "returns 201 or a structured 4xx on failure. Run it on two different bodies including one missing a "
                "field, print both responses, and comment which line keeps validation ahead of any side effect."
            ),
            patterns=["def ", "json.loads", "print("],
            mapping=(
                "FastAPI uses Pydantic models to enforce exactly this parse-then-validate order, while Flask relies "
                "on manual checks or a library such as marshmallow. The 400-versus-422 split maps to malformed text "
                "versus rejected fields."
            ),
        ),
        82: dict(
            topic="Content negotiation and Accept",
            idea=(
                "Content negotiation lets one URL serve several representations, and the client states its preference "
                "with the Accept header. The value is a comma-separated list, each item optionally carrying a quality "
                "weight like q=0.9, and the server is expected to pick the best match it can produce. A wildcard such "
                "as */* or application/* means the client accepts a family. If the server cannot satisfy any offered "
                "type, the honest answer is 406 Not Acceptable rather than a default the client never asked for. In "
                "practice most JSON APIs support only application/json, but the machinery still matters the moment "
                "you add CSV export, a vendor media type such as application/vnd.example.v2+json, or an HTML view for "
                "browsers. The same negotiation idea appears on requests through Content-Type, which is an assertion "
                "the server may reject with 415 Unsupported Media Type when it cannot parse the declared format. "
                "Parsing Accept means splitting on commas, stripping parameters, sorting by weight, and matching "
                "against the types the server can render, all before choosing a body to send. When in doubt, prefer standard, "
                "readable content types and reserve vendor types for genuinely new semantics. Negotiate the "
                "representation first, then render it."
            ),
            code=r'''def parse_accept(header):
    choices = []
    for part in header.split(","):
        token, _, params = part.strip().partition(";")
        q = 1.0
        if "q=" in params:
            q = float(params.split("q=")[1])
        choices.append((q, token.strip()))
    choices.sort(reverse=True)
    return [token for _, token in choices]


def render(accept):
    supported = {"application/json": '{"id": 1}', "text/csv": "id,title"}
    for token in parse_accept(accept):
        if token in supported:
            return 200, token, supported[token]
        if token.endswith("/*"):
            family = token.split("/")[0]
            for kind in supported:
                if kind.startswith(family + "/"):
                    return 200, kind, supported[kind]
    return 406, "text/plain", "no acceptable representation"


for header in ["application/json", "text/csv;q=0.9, application/json;q=0.5", "image/png"]:
    print(header, "->", render(header))
assert render("image/png")[0] == 406
assert render("text/csv;q=0.9, application/json;q=0.5")[1] == "text/csv"
print("the client states a preference, the server picks")
''',
            variant_b="Accept: application/*, a wildcard family",
            variant_c="Accept: text/csv;q=1.0, application/json;q=0.1, a weighted preference",
            mistakes=[
                "Returning a default representation the client never accepted instead of 406.",
                "Ignoring quality weights and choosing the first type listed rather than the best match.",
                "Treating Content-Type on a request as advisory instead of rejecting an unsupported format with 415.",
            ],
            q1=("When should a server return 406?",
                "When the client's Accept header offers no representation the server can produce, so no honest default exists."),
            homework=(
                "Write `negotiate(accept)` that parses an Accept header with quality weights and returns the best "
                "supported media type or 406 when none matches. Run it on two different headers, print both choices, "
                "and comment which line sorts the client's preferences by weight."
            ),
            patterns=["def ", "for ", "print("],
            mapping=(
                "FastAPI returns 406 through response classes and Starlette parses Accept for you, while Flask "
                "leaves negotiation to the view function. The weights and wildcard rules are the same protocol "
                "underneath either framework."
            ),
        ),
        83: dict(
            topic="Idempotency and safety",
            idea=(
                "Idempotency and safety are properties that decide whether a retry is harmless, and they are the "
                "reason methods are chosen carefully. A method is safe when it has no intended effect on state, so a "
                "network that retries it cannot cause damage; GET, HEAD, and OPTIONS are safe. A method is idempotent "
                "when performing it many times has the same effect as performing it once; GET, PUT, DELETE, and HEAD "
                "qualify, while POST generally does not. These are not implementation details, they are promises a "
                "client and any intermediary rely on. When a POST times out, the client cannot know whether the order "
                "was created, so well-designed APIs offer a way to make creation retry-safe, typically an idempotency "
                "key the server remembers for a while. DELETE returning 404 on a second call is a subtle contract "
                "question: strictly, idempotency concerns the server's state, so returning 404 while leaving state "
                "unchanged is still idempotent, even if it annoys clients. Understanding this lets you reason about "
                "exactly what repeated traffic does to your data. Repetition, not the method name, is the real test. A "
                "retry policy is only safe when it knows which methods it may repeat, so publish the method "
                "table where clients can find it."
            ),
            code=r'''def handle(method, state, title="Dune"):
    if method == "GET":
        return state, 200
    if method == "POST":
        return state + [{"id": len(state) + 1, "title": title}], 201
    if method == "PUT":
        return [{"id": 1, "title": title}], 200
    if method == "DELETE":
        return [], 204
    return state, 405


for times in (1, 2):
    state = [{"id": 1, "title": "Foundation"}]
    for _ in range(times):
        state, _status = handle("PUT", state, "Dune")
    print("PUT applied", times, "time(s):", state)

state, _ = handle("PUT", [], "Dune")
state, _ = handle("POST", state, "Hyperion")
state, _ = handle("POST", state, "Hyperion")
print("POST twice:", len(state), "books")
base = [{"id": 1, "title": "Foundation"}]
assert handle("PUT", base, "Dune")[0] == handle("PUT", handle("PUT", base, "Dune")[0], "Dune")[0]
print("PUT is idempotent, POST is not")
''',
            variant_b="applying DELETE twice to the same id",
            variant_c="applying GET repeatedly and confirming no state change",
            mistakes=[
                "Retrying a POST after a timeout, which creates a duplicate resource.",
                "Assuming idempotent means safe, when PUT still changes state.",
                "Making DELETE return a different effect each call, so repetitions do not converge.",
            ],
            q1=("Why is DELETE idempotent even when it returns 404 the second time?",
                "Idempotency is about the server's state, which is unchanged after the first delete, not about returning the same status every call."),
            homework=(
                "Write `apply_requests(method, count)` that applies one method to an in-memory list count times and "
                "returns the resulting list, so PUT and DELETE converge while POST grows. Run it on two different "
                "method and count pairs, print both results, and comment which line demonstrates idempotency."
            ),
            patterns=["def ", "for ", "print("],
            mapping=(
                "FastAPI and Flask do not enforce idempotency for you. Retry-safety is a design decision you make "
                "with PUT and DELETE, or with an idempotency-key header on POST as Stripe documents it."
            ),
        ),
        84: dict(
            topic="Errors at the HTTP layer",
            idea=(
                "Errors at the HTTP layer are not exceptions leaking out; they are first-class responses with a "
                "status, a stable shape, and enough detail for a machine to act. Two layers cooperate: the HTTP "
                "status names the category, and an application error code names the specific reason inside it. A "
                "consistent envelope such as a single error object with code, message, and optional details means a "
                "client writes one handler and a test suite asserts one shape. The categories earn their distinction. "
                "400 says the request itself is malformed, 401 says credentials are absent or invalid, 403 says they "
                "are valid but insufficient, 404 says the resource is absent, 409 says the request conflicts with "
                "current state, 422 says the fields are well-formed but semantically rejected, and 429 says slow "
                "down. A 5xx must never include a stack trace or query fragment, because that turns a bug into a "
                "disclosure. The single most common mistake is returning 200 with an error field, which lies to every "
                "generic client and cache. Decide the code, then build the body to match it, never the reverse. One "
                "envelope, chosen once, is the whole point. Structure beats prose every time a machine is "
                "the reader."
            ),
            code=r'''def error(status, code, message, details=None):
    return status, {"error": {"code": code, "message": message, "details": details or {}}}


responses = [
    error(400, "malformed_json", "body is not valid JSON"),
    error(401, "missing_token", "Authorization header is required"),
    error(403, "forbidden", "you cannot edit this book"),
    error(404, "not_found", "no book with that id"),
    error(422, "validation_failed", "year must be an integer", {"field": "year"}),
    error(429, "rate_limited", "too many requests"),
]
for status, body in responses:
    print(status, body["error"]["code"])

shapes = {tuple(sorted(body["error"])) for _, body in responses}
print("distinct error shapes:", len(shapes))
assert len(shapes) == 1
assert all(status >= 400 for status, _ in responses)
print("every error uses one envelope")
''',
            variant_b="a 403 for a book the caller may not edit",
            variant_c="a 405 for a method the resource does not support",
            mistakes=[
                "Using a different error shape per endpoint, forcing client-side special cases.",
                "Including SQL fragments or stack traces in a 500 response.",
                "Returning 200 with an error body, so status-based control flow never triggers.",
            ],
            q1=("Why keep both a status code and an application error code?",
                "The status gives the category every client understands, and the code names the exact reason so clients can react without parsing prose."),
            homework=(
                "Write `error(status, code, message, details)` that returns a response with one stable error "
                "envelope, then build four different errors with it. Run it on two different sets of errors, print "
                "each status and code, and comment which line guarantees the shape never changes."
            ),
            patterns=["def ", "return", "print("],
            mapping=(
                "FastAPI's HTTPException and Flask's errorhandler wire straight into this envelope. The rule that "
                "survives every framework is one shape, chosen once and used everywhere without exception."
            ),
        ),
        85: dict(
            topic="Rate limits: 429 and Retry-After",
            idea=(
                "Rate limiting protects a service from being overwhelmed and tells clients how to behave, and the "
                "status code for a refused request is 429 Too Many Requests. A fixed window counts requests per key, "
                "often an API token or an IP address, resetting after the window elapses; if the count exceeds the "
                "limit, the server returns 429 instead of doing the work. The response should carry Retry-After, "
                "either seconds or an HTTP date, so the client knows when to try again, and healthy responses can "
                "advertise the policy with headers such as X-RateLimit-Limit and X-RateLimit-Remaining. Well-behaved "
                "clients back off exponentially and respect Retry-After rather than hammering, and a server that "
                "omits Retry-After forces every client to guess. The limit must be keyed carefully: too coarse and "
                "one client starves everyone, too fine and abuse slips through. The window approach is simple but "
                "allows a burst at the boundary, which is why sliding windows and token buckets exist. Implement the "
                "simple counter first, then reach for the smoother version only when traffic proves you need it. Always "
                "tell the client the limit and the reset, not only the refusal, so well-behaved clients stay "
                "well-behaved. The clock here is a fixed fixture, not the real time."
            ),
            code=r'''LIMIT = 3
counts = {}


def rate_limit(key, now):
    window = now // 10
    if counts.get((key, "window")) != window:
        counts[(key, "window")] = window
        counts[key] = 0
    counts[key] += 1
    remaining = LIMIT - counts[key]
    if remaining < 0:
        retry_after = (window + 1) * 10 - now
        return 429, {"Retry-After": str(retry_after), "X-RateLimit-Remaining": "0"}
    return 200, {"X-RateLimit-Remaining": str(remaining)}


for now in [1, 2, 3, 4]:
    status, headers = rate_limit("tok-1", now)
    print("t=", now, "status:", status, headers)
status, headers = rate_limit("tok-1", 11)
print("new window t=11 status:", status, headers)
assert rate_limit("tok-2", 1)[0] == 200
assert rate_limit("tok-1", 12)[0] == 200
print("the window resets and 429 carries Retry-After")
''',
            variant_b="a second key that still has quota while the first is limited",
            variant_c="a call one second before the window resets",
            mistakes=[
                "Returning 429 without Retry-After, leaving clients to guess the backoff.",
                "Keying the limit so coarsely that one client exhausts the quota for everyone.",
                "Forgetting to reset the counter when the window rolls over.",
            ],
            q1=("Why must a 429 response include Retry-After?",
                "Without it clients can only guess when to retry, while a correct client backs off for exactly the interval the server states."),
            homework=(
                "Write `rate_limit(key, now)` that uses a fixed window, returns 429 with Retry-After once the limit "
                "is exceeded, and resets in the next window. Run it on two different sequences of calls, print every "
                "status, and comment which line computes the retry delay."
            ),
            patterns=["def ", "print(", "return"],
            mapping=(
                "Production gateways such as nginx or a hosted API gateway implement the same fixed window and emit "
                "the same headers, while FastAPI and Flask middleware can add them closer to the handler."
            ),
        ),
        86: dict(
            topic="Versioning an API",
            idea=(
                "Versioning an API is how you change a contract without breaking clients that already depend on the "
                "old one, and the version belongs somewhere stable and visible. The three common strategies are a "
                "path prefix such as /v1/books, a media type such as application/vnd.example.v1+json, and a custom "
                "request header. The path prefix is the most discoverable and the easiest to route, which is why it "
                "dominates public APIs, at the cost of putting a version into the URL that is not really a resource. "
                "A version is a promise about compatibility: adding an optional response field is usually safe, while "
                "renaming a field, changing a type, or removing an endpoint is breaking and demands a new version. "
                "Good practice keeps only a few versions alive, documents a deprecation timeline, and signals "
                "sunsetting with a Sunset or Deprecation header. Routing both versions to different handlers lets old "
                "clients keep working while new ones get the new shape. The goal is not to freeze anything, it is to "
                "change safely and predictably. A version you never intend to retire is a commitment, so plan the "
                "exit when you introduce it. Choose one strategy for the whole API and apply it without "
                "exception."
            ),
            code=r'''HANDLERS = {
    ("v1", "GET", "/books"): lambda: {"items": ["Dune"]},
    ("v2", "GET", "/books"): lambda: {"items": [{"title": "Dune", "year": 1965}], "count": 1},
}


def route(path):
    parts = path.strip("/").split("/")
    if not parts or parts[0] not in ("v1", "v2"):
        return 404, {"error": {"code": "unknown_version"}}
    version = parts[0]
    resource = "/" + "/".join(parts[1:])
    handler = HANDLERS.get((version, "GET", resource))
    if handler is None:
        return 404, {"error": {"code": "not_found"}}
    return 200, handler()


for path in ["/v1/books", "/v2/books", "/v3/books"]:
    print(path, "->", route(path))
assert route("/v2/books")[1]["count"] == 1
assert route("/v3/books")[0] == 404
print("one route table serves two versions")
''',
            variant_b="/v2/books/{id} responding with a richer record",
            variant_c="a request to /v3/books and the 404 for an unknown version",
            mistakes=[
                "Keeping an unbounded set of versions, so every old client must be served forever.",
                "Changing a response field's type under the same version, breaking existing parsers.",
                "Versioning a media type but not documenting how clients should request it.",
            ],
            q1=("Why is adding an optional response field usually safe when renaming one is not?",
                "Old clients ignore fields they do not know, but a renamed field disappears from their view and breaks parsing."),
            homework=(
                "Write `route(path)` that reads a version prefix and dispatches to a version-specific handler, "
                "returning 404 for an unknown version. Run it on two different paths, print both responses, and "
                "comment which line isolates one version from another."
            ),
            patterns=["def ", "for ", "print("],
            mapping=(
                "FastAPI can mount two routers under /v1 and /v2, and Flask blueprints with a url_prefix do the "
                "equivalent. The media-type approach appears in APIs such as GitHub's version request header."
            ),
        ),
        87: dict(
            topic="Curl as your first client",
            idea=(
                "Curl is the smallest useful HTTP client and the fastest way to see a raw request without a "
                "framework, a browser, or an SDK. You choose the method with -X, add headers with -H, pass a body "
                "with -d, and control the response view with flags such as -i or -v. Because every option maps "
                "one-to-one onto an HTTP concept, building a curl command from a request dictionary is a good test of "
                "whether you understand the message: if you cannot write the curl, your request model is probably "
                "wrong. The output is equally instructive. The status line, the response headers, and the body are "
                "three distinct sections, and curl can show the whole exchange when you want to see redirects or the "
                "exact headers a server set. For JSON, remember that -d alone usually sends a form content type, so "
                "you must set Content-Type explicitly, a mistake that produces a confusing 415. Treating curl as the "
                "reference client keeps your API honest, because anything you can describe with curl is something any "
                "client can call. Save the exact command that reproduced a bug and you have a test any "
                "teammate can rerun in a terminal. Build the command, not the network call."
            ),
            code=r'''def to_curl(method, path, headers=None, body=None):
    parts = ["curl", "-X", method]
    for name, value in (headers or {}).items():
        parts += ["-H", name + ": " + value]
    if body is not None:
        parts += ["-d", body]
    parts.append("https://api.example.com" + path)
    return " ".join(parts)


print(to_curl("GET", "/books", {"Accept": "application/json"}))
print(to_curl("POST", "/books", {"Content-Type": "application/json"}, '{"title": "Dune"}'))
print(to_curl("DELETE", "/books/1"))
cmd = to_curl("POST", "/books", {"Content-Type": "application/json"}, "{}")
assert cmd.startswith("curl -X POST")
assert cmd.count("-H") == 1 and "-d" in cmd
print("every request field becomes one curl option")
''',
            variant_b="a GET with an Accept header added",
            variant_c="a PUT with a JSON body and Content-Type set",
            mistakes=[
                "Sending a JSON body with -d but forgetting to set Content-Type, producing a 415.",
                "Quoting the whole curl command incorrectly so a header value swallows the next option.",
                "Reading only the body and ignoring the status line and headers that explain it.",
            ],
            q1=("Why is curl useful even when an SDK exists?",
                "It shows the raw request and response with nothing hidden, so you can confirm exactly what your code sends and receives."),
            homework=(
                "Write `to_curl(method, path, headers, body)` that turns a request dictionary into a curl command "
                "string with -X, -H and -d options. Run it on two different requests, print both commands, and "
                "comment which line sets the content type."
            ),
            patterns=["def ", "for ", "join("],
            mapping=(
                "Documentation for real APIs, from Stripe to GitHub, gives curl examples first because they are "
                "unambiguous. Reproducing a bug with curl removes your client code from the picture entirely."
            ),
        ),
        88: dict(
            topic="Reading an API like a client",
            idea=(
                "Reading an API as a client means pretending you did not write it: you have only a base URL and "
                "documentation, and you must get useful data out of it. That stance surfaces every ambiguity the "
                "server left behind. You look for the resource paths, the method for each, the request and response "
                "schemas, the status codes each endpoint can return, and how errors are shaped. You check pagination, "
                "because a collection that silently truncates at a hundred items is a trap, and you follow the links "
                "or cursor it provides rather than guessing an offset. You read the rate-limit headers before writing "
                "a loop and the auth scheme before writing the first request. Authentication timing, idempotency keys "
                "for creation, and partial failures all matter in ways the happy path hides. When something surprises "
                "you, the response is evidence: a status that contradicts the documented one, a field of an "
                "unexpected type, or an error shape that differs per endpoint. Reading APIs this way is a skill, and "
                "it makes you a better designer of your own, because you feel your contract from the other side. The "
                "documentation describes intent while the responses reveal reality, so read both. Look for "
                "what the docs do not say."
            ),
            code=r'''import json
from urllib.parse import urlparse, parse_qs

response = {
    "status": 200,
    "headers": {"Content-Type": "application/json", "Link": '</books?page=2>; rel="next"'},
    "body": '{"items": [{"id": 1, "title": "Dune"}], "next_page": 2}',
}

print("status ok:", response["status"] == 200)
print("content type:", response["headers"]["Content-Type"])
data = json.loads(response["body"])
print("first title:", data["items"][0]["title"])
link = response["headers"]["Link"]
target = link.split(">")[0].strip("<")
query = parse_qs(urlparse(target).query)
print("next page:", query["page"][0], "from", target)
assert query["page"] == ["2"] and data["next_page"] == 2
print("read the contract, not just the payload")
''',
            variant_b="a 404 response whose body carries an error code",
            variant_c="a collection whose Link header points to page 3",
            mistakes=[
                "Assuming a collection is complete when the response was actually paginated.",
                "Following an offset blindly after the underlying data changed between pages.",
                "Ignoring documented error shapes and crashing on an unexpected status.",
            ],
            q1=("Why follow the pagination link instead of incrementing an offset?",
                "The server controls the cursor, so a link stays correct when items are inserted or the ordering changes between pages."),
            homework=(
                "Write `read_response(response)` that checks the status, parses the JSON body, and follows a "
                "pagination link to extract the next page number. Run it on two different responses, print the "
                "extracted values, and comment which line treats the response as evidence about the contract."
            ),
            patterns=["def ", "json.loads", "print("],
            mapping=(
                "OpenAPI documents exist to answer exactly these questions, and tools such as Swagger UI render "
                "them. Reading the contract before coding is the client-side counterpart of designing it well."
            ),
        ),
        89: dict(
            topic="Review: speaking HTTP correctly",
            idea=(
                "Today you assemble everything: a request with a method, path, headers, query string, and body; "
                "validation at the boundary; a handler that respects safety and idempotency; a response with the "
                "right status, content type, and JSON shape; and an error envelope shared across failures. The point "
                "is not a big program but a correct one, where each decision is visible and defensible. A GET carries "
                "no body and changes nothing. A POST validates before it mutates and returns 201 with the new "
                "resource. A PUT replaces and stays idempotent under repetition. A missing resource is a 404, a "
                "malformed body a 400, invalid fields a 422, and a refused burst a 429 with Retry-After. The content "
                "type is declared on both sides, negotiation is respected, and the version is explicit in the path. "
                "Those choices are the whole discipline of speaking HTTP correctly, and they transfer directly to any "
                "framework because frameworks only automate them. From here the track turns to the plumbing around "
                "the contract, persistence, authentication, and the client code that consumes it, but the grammar you "
                "practised this phase stays exactly the same. Read it once more with a client's eyes before you move "
                "on, and review your own choices critically."
            ),
            code=r'''import json

BOOKS = {1: {"id": 1, "title": "Dune", "year": 1965}}
JSON = "application/json"


def handle(method, path, query="", headers=None, body=""):
    headers = headers or {}
    parts = path.strip("/").split("/")
    if method == "GET" and parts == ["books"]:
        return 200, {"Content-Type": JSON}, json.dumps({"items": list(BOOKS.values())})
    if method == "GET" and len(parts) == 2 and parts[0] == "books":
        book = BOOKS.get(int(parts[1])) if parts[1].isdigit() else None
        if book is None:
            return 404, {"Content-Type": JSON}, json.dumps({"error": {"code": "not_found"}})
        return 200, {"Content-Type": JSON}, json.dumps(book)
    if method == "POST" and parts == ["books"]:
        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            return 400, {"Content-Type": JSON}, json.dumps({"error": {"code": "malformed_json"}})
        if not isinstance(data, dict) or "title" not in data:
            return 422, {"Content-Type": JSON}, json.dumps({"error": {"code": "validation_failed"}})
        new_id = max(BOOKS) + 1
        BOOKS[new_id] = {"id": new_id, "title": data["title"]}
        headers_out = {"Content-Type": JSON, "Location": "/books/" + str(new_id)}
        return 201, headers_out, json.dumps(BOOKS[new_id])
    return 404, {"Content-Type": JSON}, json.dumps({"error": {"code": "not_found"}})


for method, path, body in [("GET", "/books", ""), ("GET", "/books/1", ""),
                           ("POST", "/books", '{"title": "Foundation"}'),
                           ("POST", "/books", "{}"), ("GET", "/books/99", "")]:
    status, headers, payload = handle(method, path, body=body)
    print(method, path, "->", status, json.loads(payload))
assert handle("POST", "/books", body='{"title": "Hyperion"}')[0] == 201
print("the whole grammar in one round trip")
''',
            variant_b="PUT /books/1 replacing a record and staying idempotent",
            variant_c="DELETE /books/1 returning 204 and then 404",
            mistakes=[
                "Mixing idempotent and non-idempotent methods so retries behave unpredictably.",
                "Letting each endpoint invent its own error shape instead of one envelope.",
                "Forgetting the content type on a response so clients parse the body as text.",
            ],
            q1=("What single property ties this phase together?",
                "Every decision, method, status, header, body and error shape, is part of one published contract that clients and intermediaries rely on."),
            homework=(
                "Write `handle(method, path, body)` that supports GET a collection, GET one item, and POST create, "
                "returning correct statuses, a Location header on 201, and a shared error envelope otherwise. Run it "
                "on two different requests, print both responses, and comment which line keeps the contract "
                "consistent across endpoints."
            ),
            patterns=["def ", "json.loads", "print("],
            mapping=(
                "This is the discipline FastAPI and Flask assume you already have, since they automate the plumbing "
                "but not the judgement. From here the track adds persistence, authentication and clients on top of "
                "the same grammar."
            ),
        ),
    },
)
