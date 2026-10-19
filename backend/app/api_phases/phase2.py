"""API Building phase 2, days 90-104: designing resources and contracts.

Every example is stdlib only and runs offline against in-memory fixtures. The
phase moves from naming resources, through request/response schemas and
validation, into pagination, filtering, relationships, status codes, errors,
versioning, and finally a machine-readable contract that can be tested.
"""

PHASE = (
    "Designing Resources and Contracts",
    "Name resources clearly, define request and response contracts, and test the promises a client depends on.",
    {
        90: dict(
            topic="Resources are nouns",
            idea=(
                "A resource is the thing a client talks about, not the operation it performs. In a library API "
                "the resources are books, authors, loans and members; the operations are listing, fetching, "
                "creating, updating and deleting them. When you name the resource first, the URL, the method, the "
                "request body and the response all have a subject to agree on, and the design becomes explainable "
                "to somebody who has never seen the code. Nouns also expose the model: if you cannot name the "
                "resource, you probably have not decided what the API stores. Actions such as search, checkout or "
                "publish are still legitimate, but they should hang off a clear resource rather than replace it. A "
                "path like /getAllBooks mixes verb and noun, and it forces every client to learn your private "
                "vocabulary. A path like /books says what exists and leaves the how to HTTP. The same rule applies "
                "inside payloads: fields should name data, not instructions. Write the catalogue before the first "
                "endpoint, because renaming a resource after clients ship is a breaking change, while renaming an "
                "internal function is not. The catalogue is also the seed of your OpenAPI document: every noun "
                "becomes a path, every identity becomes a parameter, and every relationship becomes a link. Today "
                "you catalogue resources, separate them from actions, and check that each collection path is a "
                "plural noun with a stable identity."
            ),
            code=(
                'library = {\n'
                '    "books": {"fields": ["id", "title", "price_cents"], "collection": "/books"},\n'
                '    "authors": {"fields": ["id", "name"], "collection": "/authors"},\n'
                '    "loans": {"fields": ["id", "book_id", "member_id"], "collection": "/loans"},\n'
                '}\n'
                'actions = ["search", "checkout", "getAll"]\n'
                '\n'
                'for name, spec in library.items():\n'
                '    print(name, "->", spec["collection"], "| has identity:", "id" in spec["fields"])\n'
                '\n'
                'accidental_verbs = [a for a in actions if a in library]\n'
                'print("action names hiding as resources:", accidental_verbs or "none")\n'
                'assert "books" in library and not accidental_verbs\n'
                'print("resource catalogue uses nouns with stable collections")'
            ),
            variant_b='add "members" with fields ["id", "email"] and collection /members',
            variant_c='rename /loans to /borrow and explain why existing clients would have to relearn the model',
            mistakes=[
                "Putting the verb in the path, so /getAllBooks competes with /books for the same resource.",
                "Naming a resource after a database table, exposing storage choices as the public contract.",
                "Leaving a collection without a stable id field, so clients cannot address one item.",
            ],
            q1=(
                "Why is /books a better resource path than /getAllBooks?",
                "The noun names what exists and lets HTTP supply the operation; the verb path duplicates the method and trains clients in a private vocabulary.",
            ),
            homework=(
                "Write `resource_catalogue(resources)` that prints each resource name, its collection path and "
                "whether it has an id field, and returns the list of names that look like verbs. Run it on the "
                "library catalogue and on a second catalogue with members and loans, print both results, and "
                "comment which line separates nouns from actions."
            ),
            patterns=["def ", "print(", "return "],
            mapping=(
                "OpenAPI path items are keyed by these resource paths, and FastAPI routers group them by the same "
                "noun. Naming the noun first is what keeps those generated docs readable."
            ),
        ),
        91: dict(
            topic="REST is a style, not a rule",
            idea=(
                "REST is a set of architectural constraints, not a certificate and not a syntax checker. The "
                "constraints that matter here are a uniform interface, stateless requests, cacheable responses and "
                "a clear separation between client and server. An API can follow those ideas and still choose "
                "between two reasonable shapes for the same read. Searching books with GET /books?title=dune is "
                "safe, bookmarkable and cacheable, while POST /books/search can carry a large structured query and "
                "is easier to express in some clients. Neither is illegal. What matters is that the choice is made "
                "deliberately, written down, and applied consistently, because clients build caching, retries and "
                "permissions around the method semantics you chose. The style also does not demand hypermedia links "
                "or forbid every action endpoint; it asks you to keep the interface uniform and the request "
                "self-contained. A handler that depends on a previous request is a stateful conversation in "
                "disguise, and it breaks under retries and load balancers. Today you model both search shapes, "
                "compare their safety and cacheability, and state which one your API promises. The lesson is "
                "judgement, not purity: document the trade-off instead of pretending a style rule decided for you, "
                "and tell clients what to expect."
            ),
            code=(
                'operations = [\n'
                '    {"method": "GET", "target": "/books?title=dune", "safe": True, "cacheable": True},\n'
                '    {"method": "POST", "target": "/books/search", "safe": False, "cacheable": False},\n'
                ']\n'
                '\n'
                'for op in operations:\n'
                '    print(op["method"], op["target"], "| safe:", op["safe"], "| cacheable:", op["cacheable"])\n'
                '\n'
                'reads = [op for op in operations if op["safe"]]\n'
                'print("operations a client may retry or cache:", len(reads))\n'
                'print("chosen read shape:", reads[0]["target"])\n'
                'assert reads[0]["target"].startswith("/books?")\n'
                'print("style choice recorded instead of assumed")'
            ),
            variant_b='add a POST /books/bulk-import with safe False and explain why it is still a reasonable action',
            variant_c='make the GET search depend on a cookie set by a previous call and describe which constraint it breaks',
            mistakes=[
                "Treating REST as a rule that forbids every action endpoint, then contorting the resource model.",
                "Using GET for a state-changing search that writes a query log the client must repeat.",
                "Choosing a style per endpoint with no documented pattern, so clients cannot predict behaviour.",
            ],
            q1=(
                "If REST is only a style, what still forces your search choice to be consistent?",
                "Clients cache, retry and authorize based on method semantics; an undocumented mix makes those decisions unsafe.",
            ),
            homework=(
                "Write `read_ops(operations)` that filters a list of operation dictionaries down to the safe reads, "
                "prints each target and its cacheability, and returns the chosen read shape. Run it on the two "
                "search operations and on a second list that adds a bulk import, print both choices, and comment "
                "which line encodes the style decision."
            ),
            patterns=["def ", "for ", "print("],
            mapping=(
                "REST-style HTTP APIs and RPC-style ones both appear in production; OpenAPI lets you document each "
                "operation's method and semantics so clients can cache and retry correctly."
            ),
        ),
        92: dict(
            topic="CRUD maps to methods",
            idea=(
                "CRUD is a mapping, not a law. Create becomes POST on a collection and normally returns 201 with "
                "the new identity, often in a Location header. Read becomes GET on the item and returns 200, or 404 "
                "when the identity does not exist. Update splits into PUT, which replaces the whole representation "
                "and is idempotent, and PATCH, which changes selected fields and is only idempotent if you design "
                "it that way. Delete becomes DELETE, and repeating it should leave the same end state even if the "
                "second response is 404 instead of 204. The value of the mapping is predictability: a client that "
                "knows the resource can guess the method without reading custom documentation. The trap is forcing "
                "every business operation into four verbs. Publishing a book, cancelling a loan or approving a "
                "member may deserve their own action resource, and that is fine as long as the core CRUD paths "
                "stay honest. Idempotence is the property to test, not just the verb name: send the same PUT or "
                "DELETE twice and compare the stored state and the responses. Today you drive a small in-memory "
                "store through create, read, replace and delete, then repeat the mutating calls to prove they do "
                "not double-apply. That check is the difference between a CRUD-shaped API and a correct one."
            ),
            code=(
                'books = {1: {"id": 1, "title": "Dune", "price_cents": 999}}\n'
                '\n'
                'def create(record):\n'
                '    new_id = max(books) + 1\n'
                '    books[new_id] = {"id": new_id, **record}\n'
                '    return 201, {"id": new_id}, {"Location": f"/books/{new_id}"}\n'
                '\n'
                'def read(book_id):\n'
                '    if book_id in books:\n'
                '        return 200, books[book_id], {}\n'
                '    return 404, {"error": "not_found"}, {}\n'
                '\n'
                'def replace(book_id, record):\n'
                '    books[book_id] = {"id": book_id, **record}\n'
                '    return 200, books[book_id], {}\n'
                '\n'
                'def delete(book_id):\n'
                '    books.pop(book_id, None)\n'
                '    return 204, None, {}\n'
                '\n'
                'print("create:", create({"title": "Hyperion", "price_cents": 1200}))\n'
                'print("read:", read(1))\n'
                'print("replace twice:", replace(1, {"title": "Dune", "price_cents": 1099}),\n'
                '      replace(1, {"title": "Dune", "price_cents": 1099}))\n'
                'print("delete twice:", delete(2), delete(2))\n'
                'assert read(2)[0] == 404 and read(1)[1]["price_cents"] == 1099\n'
                'print("methods carry CRUD and repeats do not double-apply")'
            ),
            variant_b='add a PATCH that changes only price_cents and check that title survives',
            variant_c='return 404 on the second DELETE and explain why the end state is still idempotent',
            mistakes=[
                "Using POST for an update and creating a duplicate record on every retry.",
                "Treating PUT as a partial update, so omitted fields are silently left at their old values.",
                "Returning 200 for a create without the new id or Location, leaving the client unable to address it.",
            ],
            q1=(
                "Why must a repeated PUT or DELETE leave the same end state?",
                "Networks retry; idempotent methods let clients resend safely without creating duplicates or compounding changes.",
            ),
            homework=(
                "Write `crud_roundtrip(store, record)` that creates, reads, replaces and deletes a record, printing "
                "the status and headers from each call. Run it with two different stores, call replace and delete "
                "twice inside each run, print both runs, and comment which lines prove idempotence."
            ),
            patterns=["def ", "return ", "print("],
            mapping=(
                "FastAPI and Flask map these verbs to route decorators; OpenAPI lists them per path. Pydantic "
                "models usually define the POST and PUT bodies while the handler owns the status codes."
            ),
        ),
        93: dict(
            topic="URL design and nesting",
            idea=(
                "URLs are the addresses clients store in logs, bookmarks and documentation, so they deserve the "
                "same care as a public function name. Nesting expresses ownership: /authors/7/books reads well when "
                "the books only make sense under an author. But deep nesting multiplies path segments and makes "
                "every operation depend on the whole ancestry, so most APIs stop at one level and use a query "
                "filter for the rest. If book ids are globally unique, /books/42 is a better canonical address than "
                "/authors/7/books/42, and the author becomes a filter or a link. Decide which URL is canonical and "
                "redirect or reject the other, because two addresses for one resource split caches and confuse "
                "clients. Identifiers should be opaque and stable; exposing a raw auto-increment key is acceptable "
                "but a public slug or UUID avoids leaking table size and survives migrations. Avoid verbs, file "
                "extensions that pretend to be formats, and trailing-slash ambiguity: pick one spelling and keep "
                "it. Path parameters should be validated like any other input, since /books/abc is a client error, "
                "not a server crash. Today you generate flat and nested paths, measure their depth, and choose the "
                "canonical form. The goal is a small, predictable address space rather than the shortest possible "
                "string."
            ),
            code=(
                'def book_path(book_id, author_id=None, nested=False):\n'
                '    if nested and author_id is not None:\n'
                '        return f"/authors/{author_id}/books/{book_id}"\n'
                '    return f"/books/{book_id}"\n'
                '\n'
                'def depth(path):\n'
                '    return len([part for part in path.split("/") if part])\n'
                '\n'
                'flat = book_path(42, author_id=7, nested=False)\n'
                'nested = book_path(42, author_id=7, nested=True)\n'
                'too_deep = "/authors/7/books/42/reviews/9"\n'
                '\n'
                'for path in (flat, nested, too_deep):\n'
                '    print(path, "| depth:", depth(path), "| acceptable:", depth(path) <= 4)\n'
                '\n'
                'print("canonical item:", flat, "| author filter:", "/books?author=7")\n'
                'assert depth(too_deep) > 4 and depth(flat) == 2\n'
                'print("the canonical address stays flat and stable")'
            ),
            variant_b='add /authors/7/books as a collection under the author and decide whether it redirects',
            variant_c='use a slug such as /books/dune instead of /books/42 and explain which clients break',
            mistakes=[
                "Nesting four levels deep, so every request carries ancestry it does not need.",
                "Offering both /books/42 and /authors/7/books/42 as equally canonical, splitting caches.",
                "Treating /books/abc as a server error instead of validating the path parameter.",
            ],
            q1=(
                "Why prefer a flat /books/42 when the id is globally unique?",
                "One stable address is easier for clients, caches and logs, and the author becomes a filter rather than part of the identity.",
            ),
            homework=(
                "Write `canonical_path(resource, item_id, parent=None)` that returns a flat item path, an optional "
                "nested collection path, and a boolean saying whether the path exceeds the depth limit. Run it for "
                "a book under an author and for a review under a book, print both results, and comment which line "
                "decides the canonical form."
            ),
            patterns=["def ", "return ", "print("],
            mapping=(
                "OpenAPI path templates such as /books/{id} describe these addresses, and FastAPI path parameters "
                "give you typed validation. Keeping one canonical form keeps generated clients and caches sane."
            ),
        ),
        94: dict(
            topic="Request schemas",
            idea=(
                "A request schema is the contract for writes. It says which fields exist, what type each one has, "
                "which are required, what defaults apply, and what happens to fields the client invents. Without "
                "that contract the handler becomes a pile of defensive checks, and each endpoint invents its own "
                "rules for the same record. Write the schema down once and validate at the boundary, before any "
                "storage or business logic runs. Distinguish three states carefully: absent, present with null, and "
                "present with a value. An absent optional field may take a default; an explicit null may mean "
                "remove this value; conflating them produces surprises that clients cannot debug. Decide your "
                "unknown-field policy too. Rejecting unknown fields catches typos such as price_cent, while "
                "ignoring them keeps older clients working when you add fields. Either is defensible; silence is "
                "not, because the client never learns that its field had no effect. Type checking must be precise: "
                "in Python a bool is an int, so a price of true can slip through a naive check. Integers should be "
                "integers, strings should be non-empty where required, and arrays should have an item type. Today "
                "you define a create-book schema, validate a valid and an invalid payload, and return clean values "
                "to the handler. The schema is a small amount of code that removes a whole class of downstream "
                "mistakes."
            ),
            code=(
                'schema = {\n'
                '    "title": {"type": str, "required": True},\n'
                '    "price_cents": {"type": int, "required": True},\n'
                '    "tags": {"type": list, "required": False, "default": []},\n'
                '}\n'
                '\n'
                'def validate(payload, schema):\n'
                '    errors, clean = [], {}\n'
                '    for name, rule in schema.items():\n'
                '        if name not in payload:\n'
                '            if rule["required"]:\n'
                '                errors.append({"field": name, "reason": "required"})\n'
                '            else:\n'
                '                clean[name] = rule.get("default")\n'
                '            continue\n'
                '        value = payload[name]\n'
                '        wrong = not isinstance(value, rule["type"])\n'
                '        if rule["type"] is int and isinstance(value, bool):\n'
                '            wrong = True\n'
                '        if wrong:\n'
                '            errors.append({"field": name, "reason": "wrong_type"})\n'
                '        else:\n'
                '            clean[name] = value\n'
                '    return errors, clean\n'
                '\n'
                'valid = {"title": "Dune", "price_cents": 999}\n'
                'invalid = {"title": "Dune", "price_cents": "999"}\n'
                'for payload in (valid, invalid):\n'
                '    errors, clean = validate(payload, schema)\n'
                '    print("payload:", payload, "->", errors or clean)\n'
                'assert validate(valid, schema)[0] == []\n'
                'assert validate(invalid, schema)[0][0]["reason"] == "wrong_type"\n'
                'print("the write contract is checked before the handler")'
            ),
            variant_b='send price_cents as true and explain why the bool check is needed',
            variant_c='add an unknown field "price_cent" and choose whether to reject or report it',
            mistakes=[
                "Validating inside the storage layer, so every caller must remember the same checks.",
                "Using isinstance(value, int) alone, which accepts True as a price.",
                "Treating missing and null as the same thing, silently erasing fields the client did not send.",
            ],
            q1=(
                "Why must a schema distinguish a missing field from an explicit null?",
                "Missing usually means leave the default alone, while null can mean clear the value; merging them makes updates destructive.",
            ),
            homework=(
                "Write `validate_create(payload, schema)` that returns an errors list and a clean field dictionary, "
                "defaulting optional fields. Run it on a valid book and on one with a string price and a missing "
                "title, print both results, and comment which line separates a missing field from a wrong type."
            ),
            patterns=["def ", "return ", "print("],
            mapping=(
                "Pydantic models are exactly this schema plus coercion and error formatting; FastAPI uses them to "
                "reject bad bodies before the handler. OpenAPI requestBody schemas describe the same contract."
            ),
        ),
        95: dict(
            topic="Response schemas",
            idea=(
                "A response is a promise, and an unspecified response grows accidental fields. Every endpoint "
                "should name the fields it returns, their types and their meaning, because clients will write code "
                "against that shape and break when it changes. The most common leak is returning an internal record "
                "directly: it carries cost, internal notes, password hashes or database bookkeeping that the client "
                "never asked for and that you now have to keep stable. Build a separate public representation and "
                "copy only the allowed fields. Decide the envelope once, too. Some APIs return the object bare, "
                "others wrap it in a data field, and collections usually need items plus paging metadata. Whatever "
                "you choose, apply it everywhere, because a client-side parser that special-cases each endpoint is "
                "a sign the contract was never designed. Null handling needs a decision as well: an absent optional "
                "value can be omitted or returned as null, but not both depending on the day. Links are useful for "
                "related resources and for the item itself, and they belong in the response rather than being "
                "guessed from the URL. Finally, the representation should be stable across storage changes: if the "
                "database column is renamed, the public field should not move. Today you take an internal record, "
                "build its public version, and prove that private fields cannot escape. The test is simple and "
                "worth keeping: assert the public schema contains exactly the promised keys."
            ),
            code=(
                'internal = {"id": 7, "title": "Dune", "price_cents": 999,\n'
                '            "cost_cents": 400, "internal_note": "damaged"}\n'
                '\n'
                'public_fields = ("id", "title", "price_cents")\n'
                '\n'
                'def public_book(record):\n'
                '    return {name: record[name] for name in public_fields}\n'
                '\n'
                'def book_response(record):\n'
                '    body = {"data": public_book(record), "links": {"self": f"/books/{record[\'id\']}"}}\n'
                '    return 200, body\n'
                '\n'
                'print("internal keys:", sorted(internal))\n'
                'status, body = book_response(internal)\n'
                'print("public:", status, body)\n'
                'leaked = sorted(set(body["data"]) & {"cost_cents", "internal_note"})\n'
                'print("leaked internal fields:", leaked or "none")\n'
                'assert list(body["data"]) == list(public_fields) and not leaked\n'
                'print("response schema is exactly the promised keys")'
            ),
            variant_b='add a genre field to public_fields and return it without changing the internal record',
            variant_c='return the internal record directly and list which fields should never reach a client',
            mistakes=[
                "Serialising the database row directly, so internal columns become an accidental API contract.",
                "Using a different envelope for single items and collections, forcing client-side special cases.",
                "Changing a public field name when the storage column changes, breaking every consumer.",
            ],
            q1=(
                "Why build a public representation instead of returning the stored record?",
                "The public shape is a promise you control; returning storage leaks private columns and couples clients to schema changes.",
            ),
            homework=(
                "Write `public_view(record, fields)` that returns a new dictionary containing only the allowed "
                "fields and raises no KeyError when a field is missing. Run it on the internal book above and on a "
                "second record with a genre, print both views, and comment which line prevents private data from "
                "escaping."
            ),
            patterns=["def ", "return ", "print("],
            mapping=(
                "Pydantic response models and FastAPI's response_model filter fields exactly this way; OpenAPI "
                "components schemas document the same promised shape for generated clients."
            ),
        ),
        96: dict(
            topic="Validation rules",
            idea=(
                "Types are the first layer of validation, not the whole job. A title can be the right type and "
                "still be empty; a price can be an integer and still be negative; a genre can be a string and "
                "still be outside the set you support. Real contracts also have cross-field rules: a discount "
                "cannot exceed the price, a loan due date cannot precede its start, a password confirmation must "
                "match. Write these rules as named checks so the error can name the field and the rule that "
                "failed, instead of returning a generic bad request. Collect all failures in one pass. Stopping at "
                "the first error forces a client to fix one field, resend, discover the next error, and repeat; "
                "returning the full list lets a form highlight every problem at once. Keep the error codes stable "
                "and machine-readable, with a human message beside them, because clients branch on codes and "
                "humans read messages. Be careful not to validate and coerce at the same time without saying so: "
                "quietly turning the string 10 into the integer 10 hides a client bug, while accepting a numeric "
                "string with an explicit coercion rule is a documented choice. Validation belongs at the boundary, "
                "before storage and business logic, and it must be tested with a payload that violates several "
                "rules at once. Today you run a small rule set over a deliberately bad book and print every "
                "failure, including a cross-field one."
            ),
            code=(
                'rules = {\n'
                '    "title": [("required", lambda v: bool(v)), ("max_length", lambda v: len(v) <= 80)],\n'
                '    "price_cents": [("positive", lambda v: v > 0)],\n'
                '    "genre": [("allowed", lambda v: v in {"fiction", "history", "science"})],\n'
                '}\n'
                '\n'
                'def check(payload):\n'
                '    errors = []\n'
                '    for field, tests in rules.items():\n'
                '        value = payload.get(field)\n'
                '        for code, test in tests:\n'
                '            if value is None and code == "required":\n'
                '                errors.append({"field": field, "code": code})\n'
                '                break\n'
                '            if value is not None and not test(value):\n'
                '                errors.append({"field": field, "code": code})\n'
                '    if "discount_cents" in payload and payload["discount_cents"] > payload.get("price_cents", 0):\n'
                '        errors.append({"field": "discount_cents", "code": "exceeds_price"})\n'
                '    return errors\n'
                '\n'
                'bad = {"title": "", "price_cents": -5, "genre": "poetry"}\n'
                'print("errors:", check(bad))\n'
                'print("reported together:", len(check(bad)))\n'
                'cross = {"title": "Dune", "price_cents": 100, "genre": "fiction", "discount_cents": 150}\n'
                'print("cross-field:", check(cross))\n'
                'assert len(check(bad)) == 3 and check(cross)[0]["code"] == "exceeds_price"\n'
                'print("validation collects failures instead of stopping early")'
            ),
            variant_b='add a max_length rule on title and send an 81-character title',
            variant_c='send a missing genre and explain why it reports required rather than allowed',
            mistakes=[
                "Returning only the first error, so clients need one round trip per bad field.",
                "Using prose messages as the only identifier, which breaks clients that branch on the reason.",
                "Silently coercing a string to a number and calling it validation.",
            ],
            q1=(
                "Why report every validation failure in one response?",
                "The client can fix the whole payload in one round trip, and the error list documents all broken rules at once.",
            ),
            homework=(
                "Write `validate_book(payload, rules)` that collects every failed rule with a field and code, "
                "including one cross-field discount check, and returns the list. Run it on a payload with three "
                "bad fields and on a valid payload with a bad discount, print both lists, and comment which line "
                "prevents early exit."
            ),
            patterns=["def ", "for ", "return "],
            mapping=(
                "Pydantic validators and FastAPI request models implement per-field and cross-field rules; the "
                "resulting 422 body is the same collected-details shape used here."
            ),
        ),
        97: dict(
            topic="Pagination design",
            idea=(
                "A collection endpoint that returns everything works on day one and fails in production. "
                "Pagination is part of the contract: the client needs a bounded page size, a stable order and a "
                "reliable way to ask for the next page. Offset pagination with limit and offset is easy to explain, "
                "but it drifts when items are inserted or deleted, because page boundaries move and the same record "
                "can appear twice or vanish. Cursor pagination fixes that by continuing after a known value, "
                "usually the last id or a sort key plus id. The cursor must be opaque to clients and must encode "
                "enough to keep the order deterministic. Always return metadata: the next cursor, whether more "
                "exists, and enough information to build links. Do not let clients request an unbounded limit, and "
                "cap it server-side so one request cannot exhaust memory. Keep the default small enough to be safe "
                "and large enough to be useful, and document the cap in the response or the OpenAPI description. "
                "Pagination also interacts with filtering and sorting: the cursor must respect the chosen order, "
                "otherwise pages overlap. Today you walk a fixed list of seven ids in pages of three using a cursor "
                "and prove that every item appears exactly once. That proof is the minimum bar for any pagination "
                "scheme, because duplicate or missing rows are the failure clients notice immediately."
            ),
            code=(
                'book_ids = [1, 2, 3, 4, 5, 6, 7]\n'
                'limit = 3\n'
                '\n'
                'def page(cursor):\n'
                '    start = 0 if cursor is None else book_ids.index(cursor) + 1\n'
                '    chunk = book_ids[start:start + limit]\n'
                '    next_cursor = chunk[-1] if start + limit < len(book_ids) else None\n'
                '    return {"items": chunk, "limit": limit, "next_cursor": next_cursor,\n'
                '            "has_more": next_cursor is not None}\n'
                '\n'
                'cursor, seen = None, []\n'
                'while True:\n'
                '    body = page(cursor)\n'
                '    print("page:", body)\n'
                '    seen += body["items"]\n'
                '    cursor = body["next_cursor"]\n'
                '    if not body["has_more"]:\n'
                '        break\n'
                '\n'
                'print("collected:", seen)\n'
                'assert seen == book_ids and len(set(seen)) == len(book_ids)\n'
                'print("cursor pagination visits every item exactly once")'
            ),
            variant_b='limit = 2 and explain how many pages the same seven ids need',
            variant_c='delete id 4 after the first page and explain why offset pagination would skip an item but this cursor does not',
            mistakes=[
                "Letting the client choose an unlimited page size, so one request can return the whole table.",
                "Returning no next cursor or has_more flag, leaving the client to guess when to stop.",
                "Combining a cursor with a different sort order than the one that produced it.",
            ],
            q1=(
                "Why is a cursor more stable than an offset when records are inserted?",
                "The cursor continues after a known item, while an offset counts positions that shift when rows are added or removed.",
            ),
            homework=(
                "Write `walk_pages(items, limit)` that yields page dictionaries with items, next_cursor and "
                "has_more, then collects the ids it visited. Run it on seven fixed ids with limits two and three, "
                "print the collected ids from both runs, and comment which line guarantees the walk terminates."
            ),
            patterns=["def ", "while ", "print("],
            mapping=(
                "FastAPI and Flask expose cursor and limit as query parameters; OpenAPI documents them, and the "
                "same next_cursor pattern powers most large production collection endpoints."
            ),
        ),
        98: dict(
            topic="Filtering and sorting",
            idea=(
                "Filtering and sorting are a query contract, not an open invitation to pass SQL through the URL. "
                "Decide which fields may be filtered, which operators each one supports, and which fields may be "
                "sorted. Publish that allowlist, and reject a request that names anything else with a clear 400 "
                "instead of silently ignoring it. Silent ignoring is worse than an error because the client "
                "believes the filter applied and makes decisions on the wrong rows. Keep parameter names stable "
                "and predictable: genre for an exact match, max_price_cents for an upper bound, and a sort "
                "parameter that combines a field and a direction. Sorting needs a deterministic tie-breaker, "
                "usually the id, or two records with the same price can swap order between requests and break "
                "pagination. Arrays and repeated parameters need a documented rule as well; if a client sends two "
                "genre values, say whether that means either or both. Filtering also has a cost dimension: an "
                "unindexed field can turn a cheap list into a table scan, so the allowlist is both a security "
                "boundary and a performance boundary. Return the applied filters and sort in collection metadata, "
                "and keep the response shape identical to the unfiltered list. "
                "Today you implement an allowlisted query over four fixed books, sort by price with an id "
                "tie-breaker, and reject an unknown sort field. The rejection is the important half: a contract "
                "that cannot say no is only a suggestion."
            ),
            code=(
                'books = [\n'
                '    {"id": 1, "title": "Dune", "genre": "fiction", "price_cents": 999},\n'
                '    {"id": 2, "title": "Cosmos", "genre": "science", "price_cents": 1299},\n'
                '    {"id": 3, "title": "Foundation", "genre": "fiction", "price_cents": 799},\n'
                '    {"id": 4, "title": "Silent Spring", "genre": "science", "price_cents": 1099},\n'
                ']\n'
                'sortable = {"price": "price_cents", "title": "title"}\n'
                '\n'
                'def query(genre=None, max_price=None, sort="id"):\n'
                '    if sort not in sortable and sort != "id":\n'
                '        return 400, {"error": "unknown_sort", "allowed": sorted(sortable) + ["id"]}\n'
                '    rows = books\n'
                '    if genre is not None:\n'
                '        rows = [b for b in rows if b["genre"] == genre]\n'
                '    if max_price is not None:\n'
                '        rows = [b for b in rows if b["price_cents"] <= max_price]\n'
                '    if sort != "id":\n'
                '        rows = sorted(rows, key=lambda b: (b[sortable[sort]], b["id"]))\n'
                '    return 200, {"items": rows, "count": len(rows)}\n'
                '\n'
                'print("fiction under 1000:", query(genre="fiction", max_price=1000))\n'
                'print("sorted by price:", [b["id"] for b in query(sort="price")[1]["items"]])\n'
                'print("bad sort:", query(sort="cost"))\n'
                'assert query(sort="cost")[0] == 400 and query(genre="fiction")[1]["count"] == 2\n'
                'print("filters and sorts are allowlisted, not guessed")'
            ),
            variant_b='filter genre="science" and sort by title, then compare the id order',
            variant_c='send sort="price DESC" and explain why the field-and-direction pair needs parsing',
            mistakes=[
                "Passing the sort parameter straight into a query, allowing arbitrary columns or injection.",
                "Ignoring an unknown filter and returning all rows, so the client trusts a filter that never ran.",
                "Sorting without an id tie-breaker, so equal values reorder between pages.",
            ],
            q1=(
                "Why reject an unknown sort field instead of falling back to the default?",
                "A silent fallback hides the client's mistake and returns a result that does not match the requested contract.",
            ),
            homework=(
                "Write `apply_query(rows, genre=None, max_price=None, sort='id')` that filters on an allowlist, "
                "sorts with an id tie-breaker, and returns a 400 result for an unknown sort. Run it on the four "
                "books with two different query combinations, print both results, and comment which line enforces "
                "the allowlist."
            ),
            patterns=["def ", "sorted(", "print("],
            mapping=(
                "FastAPI query parameters and OpenAPI parameter definitions document the allowlist; the same "
                "discipline keeps ORM filters bounded and prevents clients from choosing arbitrary sort columns."
            ),
        ),
        99: dict(
            topic="Nested and related resources",
            idea=(
                "Resources do not live alone: a book has an author, an author has books, a loan points at both. "
                "The design question is whether to embed the related data in the response or return a reference "
                "the client can fetch. Embedding avoids extra round trips and is right when the related object is "
                "small and always needed with the parent. Referencing keeps responses small and avoids N-plus-one "
                "expansion when the client only needs the parent, but it pushes the cost to the client. A common "
                "compromise is a summary by default and an expand parameter for callers that need the full "
                "representation. Whatever you choose, keep one representation per resource: a book should look "
                "the same whether it appears under an author or at its own URL, or clients need two parsers. Watch "
                "for cycles, because author embeds books and books embed author produces infinite nesting, and "
                "watch for duplication, because embedding the same author on every book can inflate a page. Use "
                "stable links with the relationship name rather than exposing raw foreign keys, and document which "
                "relationships are included by default. Nested routes and embedded payloads are separate decisions: "
                "the route /authors/7/books can return books that link to /books/42, which is often the cleanest "
                "combination. Today you build a summary response with links and an expanded response with the same "
                "books, then prove the identity is consistent. Expansion changes shape, never identity."
            ),
            code=(
                'authors = {7: {"id": 7, "name": "Frank Herbert"}}\n'
                'books = [\n'
                '    {"id": 1, "author_id": 7, "title": "Dune"},\n'
                '    {"id": 2, "author_id": 7, "title": "Dune Messiah"},\n'
                ']\n'
                '\n'
                'def author_response(author_id, expand=False):\n'
                '    author = authors[author_id]\n'
                '    related = [b for b in books if b["author_id"] == author_id]\n'
                '    if expand:\n'
                '        return 200, {"data": {**author, "books": related}}\n'
                '    linked = [{"id": b["id"], "href": f"/books/{b[\'id\']}"} for b in related]\n'
                '    return 200, {"data": {**author, "books": linked}}\n'
                '\n'
                'print("summary:", author_response(7))\n'
                'print("expanded:", author_response(7, expand=True))\n'
                'linked = author_response(7)[1]["data"]["books"][0]\n'
                'expanded = author_response(7, expand=True)[1]["data"]["books"][0]\n'
                'assert linked["id"] == expanded["id"] and "title" not in linked\n'
                'print("links and expansion keep the same identity")'
            ),
            variant_b='add a third book by a different author and confirm it is excluded from author 7',
            variant_c='embed the author inside every book as well and describe the cycle that creates',
            mistakes=[
                "Embedding related objects everywhere, so responses grow and cycles become possible.",
                "Returning a different book shape under the author than at /books/{id}, forcing two parsers.",
                "Exposing a raw author_id with no link or documentation of how to resolve it.",
            ],
            q1=(
                "When is embedding a related resource better than returning a link?",
                "When the related object is small, always needed with the parent, and embedding avoids an extra round trip without bloating the page.",
            ),
            homework=(
                "Write `author_view(author, books, expand=False)` that returns linked book summaries by default "
                "and full book objects when expand is true. Run it on one author with two books and on a second "
                "author with one book, print both forms, and comment which line keeps the identity stable."
            ),
            patterns=["def ", "return ", "print("],
            mapping=(
                "OpenAPI links and JSON:API-style relationships document embed-versus-reference choices; FastAPI "
                "response models can define separate summary and expanded schemas for the same resource."
            ),
        ),
        100: dict(
            topic="Status code selection",
            idea=(
                "The status code is the first thing every client, proxy and monitoring system reads, so it must "
                "tell the truth. Use the category correctly: 2xx means the request was understood and accepted, "
                "3xx means look elsewhere, 4xx means the client must change something, and 5xx means the server "
                "failed. Inside those categories choose the most specific code that fits. A create that returns "
                "the new resource should be 201, not 200, and should include a Location header. A successful "
                "delete with no body is 204, not 200 with an empty object. A request that cannot be parsed is 400, "
                "while a well-formed request whose fields fail business rules is 422. Missing credentials are 401, "
                "valid credentials without permission are 403, a missing resource is 404, and a duplicate that "
                "conflicts with existing state is 409. Use 429 when rate limiting and include a retry hint. Never "
                "return 200 with an error field, because every generic client will treat it as success and skip the "
                "error path. Avoid inventing codes outside the standard where a standard one already exists, and "
                "document which codes each operation can return so generated clients handle them. Consistency "
                "matters more than cleverness: one endpoint returning 422 and another 400 for the same validation "
                "failure makes the API feel unreliable. Today you map a fixed set of outcomes to exact statuses "
                "and assert each one. That map is the skeleton of every later error handler."
            ),
            code=(
                'outcomes = [\n'
                '    ("create", 201),\n'
                '    ("read", 200),\n'
                '    ("delete", 204),\n'
                '    ("missing", 404),\n'
                '    ("duplicate_title", 409),\n'
                '    ("bad_field", 422),\n'
                '    ("unknown_sort", 400),\n'
                ']\n'
                '\n'
                'def status_for(outcome):\n'
                '    table = {\n'
                '        "create": 201,\n'
                '        "read": 200,\n'
                '        "delete": 204,\n'
                '        "missing": 404,\n'
                '        "duplicate_title": 409,\n'
                '        "bad_field": 422,\n'
                '        "unknown_sort": 400,\n'
                '    }\n'
                '    return table[outcome]\n'
                '\n'
                'for outcome, expected in outcomes:\n'
                '    actual = status_for(outcome)\n'
                '    print(outcome, "->", actual, "| expected:", expected)\n'
                'assert all(status_for(o) == code for o, code in outcomes)\n'
                'print("each outcome has one specific, truthful status")'
            ),
            variant_b='add "accepted_for_processing" mapped to 202 and explain what the body must then contain',
            variant_c='map duplicate_title to 422 and explain what a client loses compared with 409',
            mistakes=[
                "Returning 200 with an error body, so generic clients believe the call succeeded.",
                "Using 404 for a permission failure, which also hides whether the resource exists.",
                "Using 400 for every client mistake, erasing the difference between malformed and invalid.",
            ],
            q1=(
                "Why is 409 a better fit than 422 for a duplicate title?",
                "The request is well-formed and the fields are valid; the conflict is with existing server state, which is exactly what 409 describes.",
            ),
            homework=(
                "Write `status_for(outcome)` that returns the exact status for create, read, delete, missing, "
                "duplicate and invalid outcomes. Run it over the full outcome table and over a second table that "
                "adds a rate-limit outcome, print both mappings, and comment which line would change for a 202 "
                "accepted response."
            ),
            patterns=["def ", "return ", "print("],
            mapping=(
                "FastAPI's status_code argument and Flask's return tuples set these codes; OpenAPI responses "
                "document each one so generated clients can handle success and failure separately."
            ),
        ),
        101: dict(
            topic="Error response design",
            idea=(
                "Every failure should look the same, because clients do not want a different parser for each "
                "endpoint. A single error envelope with a stable code, a human message, optional field details and "
                "a request identifier lets one client-side handler cover validation, conflicts, rate limits and "
                "server faults. The code is the machine contract: use durable values such as validation_failed or "
                "duplicate_title, never prose that changes with wording. The message is for humans and may be "
                "localised later. Details should point at the specific field and rule, so a form can highlight the "
                "right input. The request identifier is what makes support possible: the client reports it, and "
                "you find the matching log line without guessing. A retryable flag tells the client whether trying "
                "again could help, which is true for 429 and many 503s but not for 422. Do not leak stack traces, "
                "SQL, file paths or internal hostnames in a 500; log them with the identifier and return a generic "
                "message. Do not confirm the existence of a private resource in a 404 if that existence is itself "
                "sensitive. Keep the envelope identical whether the status is 400, 409 or 500, and document the "
                "shape once in the spec. Today you build one constructor and prove that every failure it produces "
                "has the same keys. That uniformity is not cosmetic: it is what makes error handling testable "
                "across an entire API."
            ),
            code=(
                'def error(status, code, message, details=None, retryable=False, request_id="req-42"):\n'
                '    body = {"error": {"code": code, "message": message, "details": details or [],\n'
                '                      "retryable": retryable, "request_id": request_id}}\n'
                '    return status, body\n'
                '\n'
                'responses = [\n'
                '    error(422, "validation_failed", "One or more fields are invalid",\n'
                '          [{"field": "title", "code": "required"}]),\n'
                '    error(409, "duplicate_title", "A book with this title already exists"),\n'
                '    error(429, "rate_limited", "Too many requests", retryable=True),\n'
                '    error(500, "internal_error", "Unexpected server error"),\n'
                ']\n'
                '\n'
                'for status, body in responses:\n'
                '    inner = body["error"]\n'
                '    print(status, inner["code"], "| retryable:", inner["retryable"], "| id:", inner["request_id"])\n'
                '\n'
                'shapes = {tuple(sorted(body["error"])) for _, body in responses}\n'
                'print("distinct error shapes:", len(shapes), "| keys:", shapes.pop())\n'
                'assert len({tuple(sorted(body["error"])) for _, body in responses}) == 1\n'
                'print("one envelope for every failure")'
            ),
            variant_b='add a 404 not_found error and confirm it uses the same five keys',
            variant_c='include a stack trace in the 500 details and explain what must be logged instead',
            mistakes=[
                "Using a different error shape per endpoint, forcing clients to special-case each failure.",
                "Putting a stack trace or SQL fragment in a 500 response where any caller can read it.",
                "Returning a retryable true for a validation failure that will fail identically on retry.",
            ],
            q1=(
                "Why does every error carry both a stable code and a human message?",
                "Clients branch on the code without parsing prose, while humans read the message; changing wording then never breaks a client.",
            ),
            homework=(
                "Write `error_response(status, code, details=None, retryable=False)` that returns the shared "
                "envelope with a request id, and use it for a validation failure and a rate limit. Print both "
                "responses, assert their key sets match, and comment which line keeps the shape stable."
            ),
            patterns=["def ", "return ", "print("],
            mapping=(
                "FastAPI HTTPException handlers and Flask errorhandler functions centralise this envelope; "
                "OpenAPI components can define the error schema once and reference it from every response."
            ),
        ),
        102: dict(
            topic="Versioning and compatibility",
            idea=(
                "Every API changes, and the contract decides who pays for the change. Additive changes are usually "
                "safe: a new optional response field that clients can ignore, a new endpoint, a new optional query "
                "parameter with a default. Breaking changes are the ones that invalidate existing client code: "
                "removing a field, renaming it, changing its type, making an optional request field required, "
                "tightening a validation rule, or changing a status code for the same outcome. You can version in "
                "the URL such as /v1/books, in a header, or in a media type. URL versioning is the most visible and "
                "the easiest to route and cache; header versioning keeps URLs stable but hides the version from "
                "logs. Whichever you choose, state the rules and keep the old version working for a published "
                "deprecation window. Versioning is not a substitute for compatibility discipline: creating v2 for "
                "every small change multiplies maintenance and fragments clients. Prefer an additive change when "
                "it is genuinely additive, and reserve a new version for changes a reasonable client cannot absorb. "
                "Document what each version guarantees, and test the old contract after deploying the new one. "
                "Today you write a compatibility check that classifies a field addition as safe and a field "
                "removal or type change as breaking. Run it on two proposed changes before deciding whether to "
                "bump the version. That check turns a vague argument about compatibility into a repeatable gate."
            ),
            code=(
                'def compatibility(old, new):\n'
                '    removed = sorted(set(old) - set(new))\n'
                '    added = sorted(set(new) - set(old))\n'
                '    changed = sorted(k for k in set(old) & set(new) if old[k] != new[k])\n'
                '    return {"breaking": bool(removed or changed), "removed": removed,\n'
                '            "changed": changed, "added": added}\n'
                '\n'
                'v1 = {"id": "int", "title": "str", "price_cents": "int"}\n'
                'additive = {"id": "int", "title": "str", "price_cents": "int", "genre": "str"}\n'
                'breaking = {"id": "int", "title": "str", "price": "int"}\n'
                '\n'
                'for name, candidate in (("additive", additive), ("breaking", breaking)):\n'
                '    print(name, "->", compatibility(v1, candidate))\n'
                '\n'
                'assert compatibility(v1, additive)["breaking"] is False\n'
                'assert compatibility(v1, breaking)["breaking"] is True\n'
                'print("additions are safe; removals and retypes need a version")'
            ),
            variant_b='change price_cents from "int" to "str" and classify the change',
            variant_c='add a required genre to the v1 request and explain why it is breaking even though it is an addition',
            mistakes=[
                "Renaming a response field in place because the new name is clearer, breaking every consumer.",
                "Creating a new version for every additive change, multiplying maintenance for no client benefit.",
                "Deprecating an old version without a migration window or a documented replacement.",
            ],
            q1=(
                "Why can adding a required request field be breaking while adding an optional response field is not?",
                "Existing clients do not send the new required field, so their valid requests start failing; an extra response field is ignored by most parsers.",
            ),
            homework=(
                "Write `compatibility(old, new)` that classifies removed, changed and added fields and returns "
                "whether the change is breaking. Run it on an additive response change and on a renamed field, "
                "print both classifications, and comment which line decides that a removal needs a new version."
            ),
            patterns=["def ", "return ", "print("],
            mapping=(
                "OpenAPI documents each version's schemas; URL prefixes such as /v1 are the common routing choice, "
                "while semantic-versioned specs and deprecation headers communicate the migration window."
            ),
        ),
        103: dict(
            topic="Describing an API with OpenAPI",
            idea=(
                "An API that only exists in prose is expensive to integrate with. OpenAPI turns the contract into a "
                "machine-readable document: the version, the API name, the paths, each operation's method, "
                "parameters, request body and possible responses, plus reusable component schemas. Tools consume "
                "that document to generate documentation, client SDKs, server stubs and contract tests, so one "
                "careful description replaces a lot of manual explanation. The document is not a replacement for "
                "the implementation; it is a second expression of the same contract, and the two must be checked "
                "against each other. Start small: describe one collection and one item path, give every operation "
                "at least one success response and the obvious error responses, and name the request and response "
                "schemas in components. Reuse schemas instead of copying field lists, because a copy will drift. "
                "Include examples for the tricky fields, especially money, dates and enums, so a generated client "
                "shows the right representation. Keep the spec in version control beside the code and fail the "
                "build when an operation has no documented responses. Validation matters because an unread spec "
                "rots quietly. Today you build a minimal OpenAPI-shaped dictionary for the books API, print its "
                "operations and check that every one declares responses. The shape is simplified, but the "
                "discipline is the real one: if you cannot describe the operation, you have not finished "
                "designing it."
            ),
            code=(
                'import json\n'
                '\n'
                'spec = {\n'
                '    "openapi": "3.1.0",\n'
                '    "info": {"title": "Library API", "version": "1.0.0"},\n'
                '    "paths": {\n'
                '        "/books": {\n'
                '            "get": {"responses": {"200": {"description": "A page of books"}}},\n'
                '            "post": {"responses": {"201": {"description": "Book created"},\n'
                '                                   "422": {"description": "Invalid fields"}}},\n'
                '        },\n'
                '        "/books/{id}": {\n'
                '            "get": {"parameters": [{"name": "id", "in": "path", "required": True}],\n'
                '                    "responses": {"200": {"description": "One book"},\n'
                '                                  "404": {"description": "Not found"}}},\n'
                '        },\n'
                '    },\n'
                '}\n'
                '\n'
                'operations = [(path, method) for path, item in spec["paths"].items() for method in item]\n'
                'missing = [(path, method) for path, item in spec["paths"].items()\n'
                '           for method, op in item.items() if "responses" not in op]\n'
                'print("operations:", operations)\n'
                'print("operations without responses:", missing or "none")\n'
                'print("info:", json.dumps(spec["info"], sort_keys=True))\n'
                'assert not missing\n'
                'print("every documented operation declares its responses")'
            ),
            variant_b='add a DELETE /books/{id} operation with 204 and document its missing case',
            variant_c='move the book schema into components and reference it from both operations',
            mistakes=[
                "Documenting only the happy path, so generated clients have no idea what a failure looks like.",
                "Copying schemas per endpoint instead of referencing components, so the copies drift apart.",
                "Letting the spec diverge from the implementation because nothing checks the two together.",
            ],
            q1=(
                "Why does every operation need its error responses in the description?",
                "Clients and generated SDKs need to know which failures are possible, just as they need the success shape; an undocumented error becomes an unhandled surprise.",
            ),
            homework=(
                "Write `describe_api(paths)` that returns an OpenAPI-shaped dictionary, lists every operation and "
                "raises if one has no documented responses. Run it on the two books paths and on a second set that "
                "adds a delete, print both summaries, and comment which line enforces the response rule."
            ),
            patterns=["def ", "print(", "responses"],
            mapping=(
                "FastAPI generates this document from route decorators and Pydantic models; Flask needs an "
                "extension or a hand-written spec. Either way, generated clients and contract tests consume it."
            ),
        ),
        104: dict(
            topic="Review: a contract you can test",
            idea=(
                "The contract is only real when a test can fail because of it. A contract test pins the parts a "
                "client depends on: the status code, the important headers, the presence and type of fields, and "
                "the behaviour on failure. It does not assert internal function names or exact log lines, because "
                "those are free to change. Write the cases from the client's point of view: a successful list, a "
                "successful create, an invalid create, a missing item, and a duplicate if the resource has one. "
                "Each case supplies a request and checks the response against the promise. Run the same suite "
                "against a fake handler today and against the real implementation later; if both satisfy the "
                "contract, storage and framework can change freely. Failure output should "
                "name the case, the expected status and the missing key, so a red test points at the contract "
                "rather than at a diff. Keep the suite small enough to read in one sitting; a hundred shallow "
                "checks are less useful than ten that cover the promises clients actually rely on. Review the "
                "whole phase through this lens: nouns became paths, schemas became types, validation became "
                "errors, pagination and filtering became parameters, and status codes and error envelopes became "
                "the failure contract. Today you write a runner over four fixed cases and prove they all pass. "
                "Then change one expected status and watch the suite catch it, proving the contract has teeth."
            ),
            code=(
                'def fake_handler(method, path, body=None):\n'
                '    if method == "GET" and path == "/books":\n'
                '        return 200, {"items": [{"id": 1, "title": "Dune"}], "next_cursor": None}\n'
                '    if method == "POST" and path == "/books":\n'
                '        if not body or "title" not in body:\n'
                '            return 422, {"error": {"code": "validation_failed"}}\n'
                '        return 201, {"id": 2, "title": body["title"]}\n'
                '    return 404, {"error": {"code": "not_found"}}\n'
                '\n'
                'contracts = [\n'
                '    ("GET", "/books", None, 200, ("items", "next_cursor")),\n'
                '    ("POST", "/books", {"title": "Hyperion"}, 201, ("id", "title")),\n'
                '    ("POST", "/books", {}, 422, ("error",)),\n'
                '    ("GET", "/books/99", None, 404, ("error",)),\n'
                ']\n'
                '\n'
                'def run_contracts(handler):\n'
                '    results = []\n'
                '    for method, path, body, status, keys in contracts:\n'
                '        got_status, got_body = handler(method, path, body)\n'
                '        ok = got_status == status and all(k in got_body for k in keys)\n'
                '        results.append((method, path, got_status, ok))\n'
                '    return results\n'
                '\n'
                'results = run_contracts(fake_handler)\n'
                'for row in results:\n'
                '    print(row)\n'
                'assert all(ok for *_, ok in results)\n'
                'print("contract suite passes every promise")'
            ),
            variant_b='change the expected create status to 200 and confirm the suite fails in exactly one case',
            variant_c='add a case for a duplicate title expecting 409 and explain what the handler must change',
            mistakes=[
                "Testing private function names and log strings, which break on safe refactors.",
                "Asserting only the status and ignoring the body shape the client parses.",
                "Keeping the suite so large and shallow that nobody reads it before changing the contract.",
            ],
            q1=(
                "Why should a contract test assert body keys rather than the whole exact payload?",
                "Clients depend on the promised fields; pinning every incidental value makes harmless changes fail and hides the real contract.",
            ),
            homework=(
                "Write `run_contracts(handler, cases)` that executes request cases and reports status and missing "
                "keys for each, returning whether all passed. Run it on the four cases above and on a second suite "
                "with a deliberately wrong status, print both reports, and comment which line turns a promise into "
                "a failing test."
            ),
            patterns=["def ", "for ", "assert "],
            mapping=(
                "OpenAPI schemas feed generated contract tests, and tools such as Schemathesis or Dredd check a "
                "running server against the spec; the runner here is the same idea in miniature."
            ),
        ),
    },
)
