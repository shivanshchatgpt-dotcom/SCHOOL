"""API Building phase 5: data, storage and integrations behind the API.

Fifteen days, each with a stdlib-only example that runs offline: sqlite3 in
memory or a temporary directory, csv/io/json, hashlib/hmac, and in-memory
simulations of queues, caches, replicas and outbound transports. No server
and no third-party package is needed to execute any lesson.
"""

PHASE = (
    "Data, Storage and Integrations",
    "Keep an API's data correct, fast and recoverable when storage, networks and partners misbehave.",
    {
        135: dict(
            topic="SQL schema for an API",
            idea=(
                "An API's contract is not only its JSON; it is also the shape its data is allowed to take. A "
                "schema declares that a book must have a title, that a price cannot be negative, that every book "
                "points at an author that exists, and that two authors cannot share an email. Those rules belong "
                "in the database because every writer — an HTTP handler, an import script, a background job — "
                "passes through the same gate. Application validation still matters for friendly 422 responses, "
                "but it cannot be the only defence: two concurrent requests, a manual fix in a SQL console, or a "
                "forgotten code path will eventually bypass it. Constraints turn silent corruption into a loud, "
                "immediate error at the moment of writing. The schema also documents intent for the next "
                "engineer: a NOT NULL column says 'this is required' more reliably than a comment. Choosing "
                "types is part of the same decision. Money as integer cents avoids float drift, timestamps as "
                "UTC text or integers avoid timezone ambiguity, and foreign keys name the relationships the API "
                "exposes. Today you create two related tables with real constraints and watch the database "
                "reject a bad row, because seeing the rejection is what makes the constraint credible."
            ),
            code=r'''import sqlite3

conn = sqlite3.connect(":memory:")
conn.execute("PRAGMA foreign_keys = ON")
conn.executescript("""
CREATE TABLE authors (
    id INTEGER PRIMARY KEY,
    email TEXT NOT NULL UNIQUE
);
CREATE TABLE books (
    id INTEGER PRIMARY KEY,
    author_id INTEGER NOT NULL REFERENCES authors(id),
    title TEXT NOT NULL,
    price_cents INTEGER NOT NULL CHECK (price_cents >= 0)
);
""")
conn.execute("INSERT INTO authors (email) VALUES (?)", ("ada@example.com",))
conn.execute("INSERT INTO books (author_id, title, price_cents) VALUES (?, ?, ?)", (1, "Dune", 999))
print("tables:", [r[0] for r in conn.execute(
    "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")])
print("book:", conn.execute("SELECT title, price_cents FROM books").fetchone())
try:
    conn.execute("INSERT INTO books (author_id, title, price_cents) VALUES (?, ?, ?)", (1, "Bad", -5))
except sqlite3.IntegrityError as exc:
    print("rejected:", exc)
print("rows after rejection:", conn.execute("SELECT COUNT(*) FROM books").fetchone()[0])''',
            variant_b='drop the CHECK on price_cents (the negative row is now accepted)',
            variant_c='insert a book whose author_id is 99 with PRAGMA foreign_keys ON',
            mistakes=[
                "Relying only on application validation, so a script or console bypasses every rule.",
                "Storing money as a float, where 9.99 is not exactly 9.99.",
                "Declaring a foreign key but never enabling PRAGMA foreign_keys in SQLite.",
            ],
            q1=(
                "Why keep constraints in the database when the handler already validates the request?",
                "Every writer reaches the database, while handler validation only covers one code path; constraints are the last gate that cannot be skipped.",
            ),
            homework=(
                "Write `create_schema(conn)` that creates the authors and books tables with NOT NULL, UNIQUE "
                "and CHECK constraints, then inserts one valid and one invalid row. Run it on two different "
                "schemas (with and without the price CHECK), print both outcomes, and comment which line turns "
                "corruption into an immediate error."
            ),
            patterns=["def ", "CREATE TABLE", "print("],
            mapping=(
                "Alembic migrations add and change exactly these constraints; SQLAlchemy models declare them "
                "beside the columns. Keep the constraint in the database even when the ORM also validates, "
                "because the ORM is not the only client."
            ),
        ),
        136: dict(
            topic="Transactions and consistency",
            idea=(
                "Some writes only make sense as a group. Moving money from one account to another is two "
                "updates: subtract from the source, add to the destination. If the process dies between them, "
                "the money has vanished from the ledger, and no amount of careful HTTP handling repairs that. A "
                "transaction tells the database to treat the group as one unit: either every statement lands or "
                "none does. The same pattern covers creating an order and its line items, reserving stock and "
                "recording a payment, or writing a user and their default settings. The key property is "
                "atomicity, but the practical rule is simpler: any invariant that spans more than one row needs "
                "a transaction boundary. That boundary also interacts with concurrency. Two simultaneous "
                "withdrawals can each read a balance of 100, each decide that 60 is affordable, and together "
                "overdraw the account. Isolation levels and row locks exist to stop that race, and the check "
                "constraint is the last line of defence. Today you transfer between two accounts, roll back an "
                "overdraft, and confirm the balances return exactly to their starting values. A commit that is never reached is the same as no write at all, which is why the transaction boundary has to wrap every statement the invariant depends on."
            ),
            code=r'''import sqlite3

conn = sqlite3.connect(":memory:")
conn.execute("CREATE TABLE accounts (id INTEGER PRIMARY KEY, balance INTEGER NOT NULL CHECK (balance >= 0))")
conn.executemany("INSERT INTO accounts VALUES (?, ?)", [(1, 100), (2, 40)])
conn.commit()

def transfer(source, target, amount):
    try:
        conn.execute("BEGIN")
        conn.execute("UPDATE accounts SET balance = balance - ? WHERE id = ?", (amount, source))
        conn.execute("UPDATE accounts SET balance = balance + ? WHERE id = ?", (amount, target))
        conn.execute("COMMIT")
        return "committed"
    except sqlite3.IntegrityError as exc:
        conn.execute("ROLLBACK")
        return "rolled back: " + str(exc)

print("valid transfer:", transfer(1, 2, 30))
print("balances:", conn.execute("SELECT id, balance FROM accounts ORDER BY id").fetchall())
print("overdraft:", transfer(1, 2, 1000))
print("balances:", conn.execute("SELECT id, balance FROM accounts ORDER BY id").fetchall())''',
            variant_b='start with balances 50 and 10, then transfer 30 (does it still commit?)',
            variant_c='remove the CHECK on balance and rerun the overdraft (what is now inconsistent?)',
            mistakes=[
                "Updating two rows without a transaction, so a crash leaves one half applied.",
                "Catching the error but forgetting ROLLBACK, leaving the transaction open.",
                "Reading a balance and deciding from it without locking, letting two requests overdraw.",
            ],
            q1=(
                "What exactly does rolling back an overdraft restore here?",
                "Every uncommitted statement in the transaction, so both balances return to the values they had before the first update.",
            ),
            homework=(
                "Write `transfer(conn, source, target, amount)` that wraps two balance updates in a transaction, "
                "commits on success and rolls back on a constraint violation. Run it on a valid transfer and an "
                "overdraft, print the balances after each, and comment which line guarantees that neither half "
                "lands alone."
            ),
            patterns=["def ", "BEGIN", "ROLLBACK"],
            mapping=(
                "SQLAlchemy sessions commit and roll back the same boundaries; Django's atomic() wraps a block. "
                "The rule does not change: keep every multi-row invariant inside one transaction."
            ),
        ),
        137: dict(
            topic="Connection handling",
            idea=(
                "Opening a database connection is not free. Each one may involve a TCP handshake, "
                "authentication, TLS negotiation and server-side memory, so an API that opens a connection per "
                "request spends a noticeable slice of every request paying for setup and hands the database a "
                "burst of short-lived clients under load. A pool keeps a small set of connections open and lends "
                "them out, which bounds concurrency at a number the database can survive. That bound is the real "
                "feature: without it, a traffic spike creates hundreds of connections and the database spends "
                "its time context-switching instead of serving queries. A pool also needs a discipline. Every "
                "checkout must be returned in a finally block, because a leaked connection is permanently "
                "unavailable even though the process is healthy. Connections must not be shared across threads "
                "without care, and stale connections need health checks or recycling. Timeouts matter too: "
                "waiting forever for a pool slot turns a slow database into a hung API. Today you build a tiny "
                "pool with a fixed size, reuse a returned connection, and count how many were actually opened, "
                "which makes the lifecycle visible instead of invisible. Notice also that a pool is a queue with a hard ceiling: when all connections are checked out the next request waits, so the timeout on that wait is as important as the query timeout itself."
            ),
            code=r'''import os
import sqlite3
import tempfile

class Pool:
    def __init__(self, path, size):
        self.path = path
        self.size = size
        self.free = []
        self.opened = 0
        self.checked_out = 0

    def acquire(self):
        if self.free:
            conn = self.free.pop()
            print("reused a connection; free now", len(self.free))
        else:
            assert self.opened < self.size, "pool exhausted"
            conn = sqlite3.connect(self.path)
            self.opened += 1
            print("opened connection", self.opened)
        self.checked_out += 1
        return conn

    def release(self, conn):
        self.checked_out -= 1
        self.free.append(conn)
        print("released a connection; free now", len(self.free))

with tempfile.TemporaryDirectory() as tmp:
    path = os.path.join(tmp, "app.db")
    setup = sqlite3.connect(path)
    setup.execute("CREATE TABLE visits (id INTEGER PRIMARY KEY, path TEXT)")
    setup.commit()
    setup.close()

    pool = Pool(path, size=2)
    a = pool.acquire()
    a.execute("INSERT INTO visits (path) VALUES ('/books')")
    a.commit()
    b = pool.acquire()
    b.execute("INSERT INTO visits (path) VALUES ('/authors')")
    b.commit()
    pool.release(a)
    c = pool.acquire()
    print("same object reused:", c is a)
    pool.release(b)
    pool.release(c)
    print("opened total:", pool.opened, "| still checked out:", pool.checked_out)''',
            variant_b='size=1 and acquire twice without releasing (watch the assert fire)',
            variant_c='release the same connection twice (what does the free list now contain?)',
            mistakes=[
                "Opening a fresh connection per request and exhausting the database under load.",
                "Forgetting to release in a finally block, so a healthy process leaks its pool.",
                "Making the pool larger than the database can serve, which moves the queue to the server.",
            ],
            q1=(
                "Why does a pool improve latency even when the database is fast?",
                "It removes connection setup from the request path and reuses an already authenticated connection, so the request only pays for its query.",
            ),
            homework=(
                "Write `Pool(path, size)` with acquire and release methods that track opened and checked-out "
                "counts. Run a sequence that exhausts and then reuses a pool of size two, print every transition, "
                "and comment which line prevents a leaked connection from being checked out twice."
            ),
            patterns=["def acquire", "def release", "print("],
            mapping=(
                "SQLAlchemy's engine keeps a pool behind every session; PgBouncer does the same for Postgres "
                "processes. Size the pool below the database connection limit and always return connections."
            ),
        ),
        138: dict(
            topic="Migrations",
            idea=(
                "Schemas change after the first deploy. A new field, a new index, a renamed column, a backfill — "
                "each is a change that must reach every environment in the same order, without losing the rows "
                "already there. Doing this by hand in a SQL console works once and fails the moment there are two "
                "developers, a staging database and a production replica. A migration is a versioned, repeatable "
                "step recorded in a table so the system knows what has already run. The record is what makes "
                "deployment safe: applying the same migration twice should be a no-op, not a duplicate column "
                "error. Good migrations are also small and backwards compatible. Adding a nullable column is "
                "safe; dropping a column that old code still reads is not. The standard sequence is expand, "
                "backfill, switch reads and writes, then contract later, after the old version is gone. That "
                "ordering lets the API roll forward and back without a maintenance window. Today you build a "
                "migration runner over SQLite, apply two versions, and prove that an existing row survives an "
                "added column with a default. The version table itself should be created by the first migration, so a brand-new database and an ancient one converge on the same history."
            ),
            code=r'''import sqlite3

conn = sqlite3.connect(":memory:")
conn.execute("CREATE TABLE schema_migrations (version INTEGER PRIMARY KEY)")
conn.execute("CREATE TABLE books (id INTEGER PRIMARY KEY, title TEXT NOT NULL)")
conn.execute("INSERT INTO schema_migrations VALUES (1)")
conn.execute("INSERT INTO books (title) VALUES ('Dune')")
conn.commit()
print("v1 columns:", [r[1] for r in conn.execute("PRAGMA table_info(books)")])

migrations = {
    2: "ALTER TABLE books ADD COLUMN price_cents INTEGER NOT NULL DEFAULT 0",
    3: "CREATE INDEX books_title_idx ON books(title)",
}

for version in (2, 3):
    done = conn.execute("SELECT 1 FROM schema_migrations WHERE version = ?", (version,)).fetchone()
    if done:
        print("version", version, "already applied")
        continue
    conn.execute("BEGIN")
    conn.execute(migrations[version])
    conn.execute("INSERT INTO schema_migrations VALUES (?)", (version,))
    conn.execute("COMMIT")
    print("applied version", version)

print("v3 columns:", [r[1] for r in conn.execute("PRAGMA table_info(books)")])
print("old row:", conn.execute("SELECT title, price_cents FROM books").fetchone())
print("versions:", [r[0] for r in conn.execute("SELECT version FROM schema_migrations ORDER BY version")])''',
            variant_b='run the loop twice (versions 2 and 3 must be skipped, not applied again)',
            variant_c='migration 2 adds a nullable column with no default (what does the old row hold?)',
            mistakes=[
                "Editing a migration that has already run in production, so environments diverge.",
                "Dropping a column before the code that reads it has been deployed away.",
                "Applying SQL by hand without recording the version, so the next deploy repeats it.",
            ],
            q1=(
                "Why must a migration be safe to run twice?",
                "Deployments retry, environments lag and operators rerun commands; the version table must make the second run a no-op instead of an error.",
            ),
            homework=(
                "Write `run_migrations(conn, migrations)` that checks the version table, applies only pending "
                "steps inside a transaction and records each one. Run it twice on the same connection, print "
                "both reports, and comment which line makes the second run a no-op instead of a duplicate-column "
                "error."
            ),
            patterns=["def ", "schema_migrations", "COMMIT"],
            mapping=(
                "Alembic and Django migrations are this runner with history, downgrade steps and dependency "
                "ordering. Use expand-and-contract for zero-downtime changes: add, backfill, switch, then drop."
            ),
        ),
        139: dict(
            topic="ORMs: what they hide",
            idea=(
                "An ORM turns rows into objects and queries into method calls, which is genuinely convenient "
                "until you need to know what SQL it emitted. The classic example is the N+1 query: fetch twenty "
                "authors with one query, then ask each author for their books, and the database sees twenty-one "
                "round trips instead of one join. The code looks like a loop over in-memory objects, so nothing "
                "in the source hints at the network cost. ORMs also hide transaction boundaries, lazy loading, "
                "cascade deletes and the difference between filtering in Python and filtering in SQL. None of "
                "that makes ORMs bad; it makes them leaky. The professional habit is to log queries in "
                "development, count them for a representative page, and learn the escape hatch for the heavy "
                "paths. You should be able to explain what SQL each endpoint runs and why. Today you reproduce "
                "the N+1 pattern with plain sqlite3 calls, count the queries, then replace it with a join and "
                "watch the count drop from many to one. That number is the lesson. Once you can count queries, the next step is to decide which count is acceptable for each endpoint and to keep it from creeping upward as features are added."
            ),
            code=r'''import sqlite3

conn = sqlite3.connect(":memory:")
conn.executescript("""
CREATE TABLE authors (id INTEGER PRIMARY KEY, name TEXT NOT NULL);
CREATE TABLE books (id INTEGER PRIMARY KEY, author_id INTEGER NOT NULL, title TEXT NOT NULL);
INSERT INTO authors VALUES (1, 'Ada'), (2, 'Grace');
INSERT INTO books VALUES (1, 1, 'Dune'), (2, 1, 'Foundation'), (3, 2, 'Cosmos');
""")
conn.commit()

queries = 0

def find(sql, params=()):
    global queries
    queries += 1
    return conn.execute(sql, params).fetchall()

authors = find("SELECT id, name FROM authors ORDER BY id")
rows = []
for author_id, name in authors:
    titles = find("SELECT title FROM books WHERE author_id = ?", (author_id,))
    rows.append((name, [t[0] for t in titles]))
print("naive result:", rows)
print("naive queries:", queries)

queries = 0
joined = find(
    "SELECT authors.name, books.title FROM authors "
    "JOIN books ON books.author_id = authors.id ORDER BY books.id"
)
print("join result:", joined)
print("join queries:", queries)''',
            variant_b='add a third author with no books (does the join keep them?)',
            variant_c='use a LEFT JOIN to include authors without books (how do the rows change?)',
            mistakes=[
                "Looping over parents and querying children per row instead of joining once.",
                "Assuming attribute access is free when a lazy relationship triggers a query.",
                "Filtering in Python after loading a whole table, which moves the cost but not the win.",
            ],
            q1=(
                "Why is the naive loop slower even though each individual query is fast?",
                "The cost is the number of round trips: N extra queries each pay network and parsing overhead, so total latency grows with the number of authors.",
            ),
            homework=(
                "Write `author_titles(conn)` that loads authors and their books twice, once with a per-author "
                "query and once with a join, counting queries in each version. Run it on two author sets, print "
                "both counts, and comment which line removes the N+1 pattern."
            ),
            patterns=["def ", "JOIN", "print("],
            mapping=(
                "SQLAlchemy's lazy='select' relationships produce N+1; selectinload or a join fixes it. Enable "
                "SQL echo in development and count queries per endpoint, because the ORM will not warn you."
            ),
        ),
        140: dict(
            topic="File uploads",
            idea=(
                "An upload is untrusted bytes with metadata attached, and every part of that sentence matters. "
                "The filename is client-supplied, so it may contain path separators, absurd lengths or a "
                "misleading extension. The declared content type is also client-supplied and may disagree with "
                "the bytes. The size is unknown until you have already received it, which is why servers enforce "
                "limits before and during the read rather than after. A robust endpoint checks the extension and "
                "the content type, enforces a maximum size, computes a checksum for integrity and deduplication, "
                "and stores the file under a generated name rather than the original. It never joins the client "
                "filename to a server path. For CSV imports the next step is parsing with a real CSV reader that "
                "handles quoting, not splitting on commas. Errors need to be specific: too large is 413, "
                "unsupported type is 415, malformed content is 422. Today you simulate a multipart request in "
                "memory, validate its metadata, compute a hash, write it to a temporary file and read it back "
                "with csv, so the whole path is visible without a network. The same checks apply whether the destination is local disk or object storage: validate first, write under a key you control, and keep the original metadata for auditing."
            ),
            code=r'''import csv
import hashlib
import io
import os
import tempfile

raw = (
    "filename: books.csv\r\n"
    "Content-Type: text/csv\r\n"
    "\r\n"
    "title,price_cents\nDune,999\nFoundation,1200\n"
)
MAX_BYTES = 64

def receive(raw):
    head, body = raw.split("\r\n\r\n", 1)
    meta = {}
    for line in head.split("\r\n"):
        key, value = line.split(": ", 1)
        meta[key.lower()] = value
    encoded = body.encode("utf-8")
    assert meta["content-type"] == "text/csv", "unsupported type"
    assert meta["filename"].endswith(".csv"), "bad extension"
    assert len(encoded) <= MAX_BYTES, "upload too large"
    digest = hashlib.sha256(encoded).hexdigest()[:12]
    return meta["filename"], body, len(encoded), digest

name, body, size, digest = receive(raw)
print("accepted:", name, "| bytes:", size, "| sha256:", digest)
print("parsed rows:", list(csv.DictReader(io.StringIO(body))))

with tempfile.TemporaryDirectory() as tmp:
    path = os.path.join(tmp, "stored-upload.csv")
    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(body)
    with open(path, encoding="utf-8", newline="") as fh:
        print("stored rows:", sum(1 for _ in csv.DictReader(fh)))''',
            variant_b='filename "../../etc/passwd.csv" with a generated storage name (what changes on disk?)',
            variant_c='a 200-byte body with MAX_BYTES at 64 (which status should the endpoint return?)',
            mistakes=[
                "Joining the client filename to a storage path, which enables directory traversal.",
                "Trusting the declared Content-Type instead of validating the bytes or extension.",
                "Reading an unbounded body into memory before checking its size.",
            ],
            q1=(
                "Why store the upload under a generated name instead of the client's filename?",
                "The client name is untrusted and may contain path separators or collide with another file; a generated name is unique and cannot escape the storage directory.",
            ),
            homework=(
                "Write `receive(raw, max_bytes)` that parses upload metadata, rejects a wrong type, a wrong "
                "extension or an oversized body, and returns the filename, size and checksum. Run it on two "
                "uploads, print both outcomes, and comment which line keeps a client filename out of the storage "
                "path."
            ),
            patterns=["def ", "hashlib", "print("],
            mapping=(
                "FastAPI's UploadFile and Flask's request.files stream the same bytes; S3 keys should be "
                "generated, not client names. Validate type, size and checksum before handing the object to a "
                "background job."
            ),
        ),
        141: dict(
            topic="Background jobs",
            idea=(
                "Not every task belongs inside the request that triggered it. Sending a receipt, resizing an "
                "image, calling a partner API or rebuilding a search index can take seconds, and holding the "
                "client connection open for that work makes the API slow and fragile. A background job moves the "
                "work to a worker, while the request returns quickly with an accepted status and some way to "
                "check progress. The queue is the contract between them: a job has a type, a payload, an attempt "
                "count and a status. Failures are normal, so the worker must distinguish a transient error worth "
                "retrying from a permanent one worth dead-lettering. Retries need a limit, or one poisoned job "
                "loops forever and starves the queue. They also need to be safe to repeat, because a worker can "
                "crash after doing the work but before recording success. That is idempotency again: the job "
                "should check whether its effect already exists. Today you build a small in-memory queue with "
                "retries and a dead-letter list, then run it to completion and print every transition, so the "
                "lifecycle is explicit rather than hidden inside a library. The queue is also an observability surface: a rising dead-letter count is often the first sign that a partner changed its contract."
            ),
            code=r'''from collections import deque

queue = deque()
dead_letters = []

def enqueue(job):
    job = dict(job)
    job["attempts"] = 0
    queue.append(job)
    print("enqueued:", job["id"])

def work(max_attempts=2):
    while queue:
        job = queue.popleft()
        job["attempts"] += 1
        if job["attempts"] <= job["fail_until"]:
            if job["attempts"] >= max_attempts:
                dead_letters.append(job["id"])
                print("dead-lettered:", job["id"], "after", job["attempts"], "attempts")
            else:
                queue.append(job)
                print("retrying:", job["id"], "attempt", job["attempts"])
        else:
            print("done:", job["id"], "after", job["attempts"], "attempts")

enqueue({"id": "send-receipt-1", "fail_until": 0})
enqueue({"id": "resize-cover-1", "fail_until": 2})
work()
print("queue remaining:", len(queue))
print("dead letters:", dead_letters)''',
            variant_b='max_attempts=4 for resize-cover-1 (does it finish instead of dying?)',
            variant_c='fail_until=0 for both jobs (what order are they completed in?)',
            mistakes=[
                "Doing slow work inside the request handler and calling it a background job.",
                "Retrying forever without a limit, so one poisoned job blocks the queue.",
                "Assuming a crash after the work but before the ack cannot happen, and duplicating effects.",
            ],
            q1=(
                "Why does a worker need an attempt count on the job itself?",
                "The count must survive worker restarts and retries; without it a failing job is retried forever or dead-lettered at an arbitrary point.",
            ),
            homework=(
                "Write `work(queue, max_attempts)` that processes jobs, retries transient failures, dead-letters "
                "jobs at the limit and returns the dead-letter list. Run it on two queues with different failure "
                "counts, print every transition, and comment which line stops an endless retry loop."
            ),
            patterns=["def ", "deque", "print("],
            mapping=(
                "Celery, RQ and SQS all implement this lifecycle with visibility timeouts and DLQs. Make handlers "
                "idempotent and keep retry limits finite, because at-least-once delivery is the norm."
            ),
        ),
        142: dict(
            topic="Webhooks",
            idea=(
                "A webhook is an inbound HTTP request from a service you do not control, and it arrives with "
                "three problems attached. First, anyone can POST to a public URL, so the payload needs an "
                "authenticating signature computed with a shared secret over the exact raw bytes. Parsing and "
                "re-serialising JSON before verifying changes the bytes and breaks the check. Second, delivery is "
                "at-least-once: the sender retries on timeouts, so the same event will arrive more than once. The "
                "handler must be idempotent, usually by storing the event id and ignoring duplicates. Third, the "
                "sender expects a fast 2xx, because a slow handler looks like a failure and triggers still more "
                "retries. The usual pattern is to verify, persist the raw event, enqueue the work and return "
                "immediately. A webhook endpoint is therefore a thin, hostile boundary rather than a place for "
                "business logic. Today you sign a payload with HMAC, accept it once, reject a replay, and reject "
                "a tampered body, using only stdlib hashlib and hmac. The order of those checks is itself part of "
                "the design. Signature first, then deduplication, then parsing the business payload: a forged request should cost almost nothing, and a repeated one should never reach your side effects."
            ),
            code=r'''import hashlib
import hmac
import json

SECRET = b"whsec_test_only"
seen = set()

def sign(body):
    return hmac.new(SECRET, body, hashlib.sha256).hexdigest()

def handle(headers, body):
    if headers.get("X-Signature") != sign(body):
        return 401, {"error": "bad signature"}
    event = json.loads(body)
    if event["id"] in seen:
        return 200, {"status": "duplicate"}
    seen.add(event["id"])
    return 200, {"status": "processed", "type": event["type"]}

body = json.dumps(
    {"id": "evt_1", "type": "book.created", "book_id": 7}, sort_keys=True
).encode()
headers = {"X-Signature": sign(body)}
print("first delivery:", handle(headers, body))
print("replayed delivery:", handle(headers, body))
tampered = body.replace(b"book.created", b"book.deleted")
print("tampered body:", handle(headers, tampered))''',
            variant_b='change one byte of the signature in headers (which check rejects it?)',
            variant_c='send a second event with the same id but a different type (still a duplicate?)',
            mistakes=[
                "Verifying a parsed and re-serialised body, whose bytes differ from the signed payload.",
                "Processing the same event twice because the event id is never recorded.",
                "Doing slow work before returning 2xx, which invites even more retries.",
            ],
            q1=(
                "Why must the signature be checked over the raw request bytes?",
                "The sender signed exactly those bytes; parsing and dumping JSON can reorder or reformat text, so a valid signature would appear invalid.",
            ),
            homework=(
                "Write `handle(headers, body)` that verifies an HMAC signature, rejects a replay by event id and "
                "returns a status and body. Run it on a fresh delivery and a repeat, print both, and comment "
                "which line makes redelivery harmless."
            ),
            patterns=["def ", "hmac", "print("],
            mapping=(
                "Stripe-style webhooks use an HMAC header over the raw body plus a timestamp; store event ids "
                "with a unique constraint so concurrent retries cannot both process. Return 2xx before enqueueing "
                "heavy work."
            ),
        ),
        143: dict(
            topic="Outbound API calls",
            idea=(
                "When your API calls someone else's API, their failures become your latency. A request that "
                "hangs holds a worker and a client connection; a 500 from a partner can cascade into your own "
                "outage if you retry blindly. Three habits keep this bounded. Set a timeout on every call, "
                "because the default is often effectively infinite. Retry only what is safe to retry: network "
                "errors, timeouts and 5xx responses, never a 400 that will fail identically every time. Use "
                "exponential backoff with a cap and jitter so a hundred clients do not hammer the recovering "
                "service in lockstep. For writes, attach an idempotency key so a retry after a timeout does not "
                "create a second order. Also decide what your endpoint returns when the dependency is down: a "
                "cached value, a partial response with a clear status, or a 503 with a retry hint. Today you "
                "simulate a flaky partner with a fixed list of responses, count attempts, stop on a permanent "
                "error and reuse one idempotency key across retries. No sockets are involved, but the policy is "
                "the same one a real client library implements. Write the policy down beside the call, because a retry count that lives only in someone's memory is not a policy and will not survive the next refactor."
            ),
            code=r'''RETRYABLE = {500, 502, 503, 504}

def call_partner(responses):
    headers = {"Idempotency-Key": "order-42"}
    for attempt, status in enumerate(responses, start=1):
        print("attempt", attempt, "->", status, "key", headers["Idempotency-Key"])
        if status not in RETRYABLE:
            return status, attempt
    return responses[-1], len(responses)

print("transient:", call_partner([503, 503, 200]))
print("permanent:", call_partner([400]))
print("exhausted:", call_partner([503, 503, 503]))''',
            variant_b='responses [429, 200] (is 429 retryable, and after what delay?)',
            variant_c='responses [200] (how many attempts does a healthy call need?)',
            mistakes=[
                "Calling a partner without a timeout and holding your own worker hostage.",
                "Retrying a 400 or a validation error that will fail identically every time.",
                "Retrying a write without an idempotency key, so a timeout creates a duplicate order.",
            ],
            q1=(
                "Why is an idempotency key necessary when retrying a write?",
                "The first request may have succeeded even though the response was lost; the key lets the partner recognise the retry instead of creating a second record.",
            ),
            homework=(
                "Write `call_partner(responses)` that retries only 5xx statuses, stops on a permanent error and "
                "reuses one idempotency key. Run it on a transient sequence and a 400 sequence, print both "
                "attempt counts, and comment which line prevents a duplicate write after a timeout."
            ),
            patterns=["def ", "RETRYABLE", "print("],
            mapping=(
                "httpx and requests both need explicit timeouts and retry policies; resilience libraries add "
                "backoff and circuit breakers. Send idempotency keys on POST and cap attempts so a partner "
                "outage stays a dependency failure, not your outage."
            ),
        ),
        144: dict(
            topic="Caching responses",
            idea=(
                "A cache is a bet that the same question will be asked again before the answer changes. When "
                "that bet is right, it removes database work and latency; when it is wrong, it serves stale data "
                "and the bug looks like a ghost. Three decisions make the bet explicit: what the key is, how long "
                "an entry lives, and what invalidates it. The key must include everything that changes the "
                "response, including query parameters, pagination cursors, the authenticated user or tenant, and "
                "the representation. TTL is the simplest expiry policy and the easiest to reason about, but it "
                "only bounds staleness; it does not make data fresh. Invalidation on write is more precise and "
                "much easier to get wrong, especially when one write touches several cached views. Caches also "
                "need a story for missing entries, or a burst of identical requests all miss and hit the database "
                "together. Today you build a small in-memory cache with an explicit logical clock, so behaviour "
                "is deterministic and testable: the same key is a hit before expiry, a miss after it, and a "
                "write can evict it. Redis later is the same ideas with a network in between. The hit and miss counters are not decoration: a hit rate near zero usually means the key includes a value that changes on every request."
            ),
            code=r'''class TTLCache:
    def __init__(self):
        self.store = {}
        self.hits = 0
        self.misses = 0

    def get(self, key, now):
        entry = self.store.get(key)
        if entry is not None and entry["expires"] > now:
            self.hits += 1
            return entry["value"]
        self.misses += 1
        return None

    def set(self, key, value, now, ttl):
        self.store[key] = {"value": value, "expires": now + ttl}

    def evict(self, key):
        self.store.pop(key, None)

cache = TTLCache()

def books_endpoint(cache, now):
    cached = cache.get("/books?page=1", now)
    if cached is not None:
        return cached
    value = [{"id": 1, "title": "Dune"}]
    cache.set("/books?page=1", value, now, ttl=5)
    return value

print("t=0:", books_endpoint(cache, 0), "| hits", cache.hits, "misses", cache.misses)
print("t=3:", books_endpoint(cache, 3), "| hits", cache.hits, "misses", cache.misses)
print("t=6:", books_endpoint(cache, 6), "| hits", cache.hits, "misses", cache.misses)
cache.evict("/books?page=1")
print("after write eviction:", books_endpoint(cache, 6))''',
            variant_b='ttl=2 instead of 5 (which request becomes a miss?)',
            variant_c='key "/books" ignoring the page parameter (what does page two now receive?)',
            mistakes=[
                "Caching per user data under a key that omits the user or tenant.",
                "Using a TTL but never invalidating on write, so a change waits for expiry.",
                "Caching errors or empty results for as long as successful responses.",
            ],
            q1=(
                "Why does the cache key need to include query parameters and tenant identity?",
                "Different inputs and different users produce different responses; sharing one key returns another caller's data or the wrong page.",
            ),
            homework=(
                "Write `TTLCache` with get, set and evict methods driven by an explicit `now` argument, and a "
                "`books_endpoint` that caches one response. Run requests at times 0, 3 and 6, print hits and "
                "misses, and comment which line makes the third request fetch again."
            ),
            patterns=["def get", "def set", "print("],
            mapping=(
                "Redis gives shared TTL caches across processes; HTTP Cache-Control gives clients and CDNs the "
                "same decision. Never cache authenticated responses without a key that includes the identity, and "
                "invalidate on write when freshness matters."
            ),
        ),
        145: dict(
            topic="Pagination at scale",
            idea=(
                "Returning a whole table works until the table is large. Pagination is how an API keeps response "
                "size and query cost bounded, but the common offset approach has a subtle flaw: OFFSET 20000 "
                "tells the database to read and discard twenty thousand rows before returning twenty, so deep "
                "pages get slower as the dataset grows. It is also unstable. If a row is inserted before the "
                "current offset while a client is paging, the next page repeats an item or skips one, because the "
                "window shifted underneath the reader. Cursor pagination, also called keyset pagination, avoids "
                "both problems by asking for rows after a known position — WHERE id > last_id ORDER BY id LIMIT "
                "n. The cursor must be stable and unique, which usually means a compound key such as created_at "
                "plus id. The client treats the cursor as opaque, and the server can index the ordering columns to "
                "keep every page equally fast. The trade-off is that arbitrary page numbers disappear; for feeds "
                "and exports that is a feature. Today you page through SQLite both ways, insert a row "
                "mid-traversal, and watch the offset page duplicate what the cursor page does not. Return the next cursor even on the last page, as null, so clients have one loop instead of a special case."
            ),
            code=r'''import sqlite3

conn = sqlite3.connect(":memory:")
conn.execute("CREATE TABLE events (id INTEGER PRIMARY KEY, kind TEXT NOT NULL)")
conn.executemany(
    "INSERT INTO events (kind) VALUES (?)",
    [("view",), ("click",), ("view",), ("buy",), ("view",), ("click",), ("buy",)],
)
conn.commit()

def page(after_id, limit=3):
    return conn.execute(
        "SELECT id, kind FROM events WHERE id > ? ORDER BY id LIMIT ?",
        (after_id, limit),
    ).fetchall()

first = page(0)
print("page 1 keyset:", first)
cursor = first[-1][0]

conn.execute("INSERT INTO events (id, kind) VALUES (0, 'late')")
conn.commit()

print("page 2 keyset:", page(cursor))
print("page 2 offset:", conn.execute(
    "SELECT id, kind FROM events ORDER BY id LIMIT 3 OFFSET 3").fetchall())
print("ids never repeat in keyset:", sorted({r[0] for r in first + page(cursor)}) ==
      sorted(r[0] for r in first + page(cursor)))''',
            variant_b='limit=2 (walk three cursor pages and list every id)',
            variant_c='order by kind, id and use the pair as the cursor (why must the cursor be unique?)',
            mistakes=[
                "Using OFFSET for deep pages, which scans and discards every skipped row.",
                "Assuming a non-unique cursor (created_at alone) never repeats or skips rows.",
                "Letting clients build raw SQL from the cursor instead of treating it as opaque server data.",
            ],
            q1=(
                "Why does inserting a row mid-traversal break an offset page but not a cursor page?",
                "OFFSET counts from the start, so a new earlier row shifts the window; a cursor names a position, so the next page still starts after the same id.",
            ),
            homework=(
                "Write `page(conn, after_id, limit)` that returns a keyset page, then walk a table while "
                "inserting one row mid-traversal. Run it with limits of two and three, print every page, and "
                "comment which line keeps already-seen ids from repeating."
            ),
            patterns=["def ", "LIMIT", "print("],
            mapping=(
                "APIs expose an opaque `next_cursor` rather than page numbers for large feeds; SQLAlchemy and "
                "Django support keyset queries directly. Index the ordering columns, and use a unique tiebreaker "
                "such as id after created_at."
            ),
        ),
        146: dict(
            topic="Consistent reads and replicas",
            idea=(
                "When a database is replicated, writes go to a primary and reads may go to a replica that is a "
                "little behind. That lag is usually milliseconds, and usually invisible — until a user updates a "
                "profile, the page reloads from a replica, and their change is gone. This is the read-your-writes "
                "problem, and it is a product bug even though every individual query succeeded. The fix is not to "
                "abandon replicas; it is to make freshness a decision. Track a version or log position on the "
                "write, return it to the client, and route reads that must see it back to the primary until the "
                "replica catches up. Alternatively, pin a session to the primary for a short window after a "
                "write. Analytics, search and old pages can tolerate stale reads; a checkout confirmation "
                "cannot. The same reasoning applies to caches: after a write, a cached read can serve the "
                "pre-write value. Today you simulate a primary and a replica with an explicit replication step, "
                "show a stale read, then use a version check to force a primary read until the replica has "
                "caught up. No clocks and no randomness, so the failure is reproducible. Write the required version into the response of the write, so the client can hand it back on the next read without guessing."
            ),
            code=r'''primary = {"id": 1, "title": "Dune", "version": 1}
replica = {"id": 1, "title": "Dune", "version": 1}

def replicate():
    replica.update(primary)
    print("replica caught up to version", replica["version"])

def read(required_version):
    if replica["version"] < required_version:
        print("replica is stale; reading primary")
        return dict(primary)
    return dict(replica)

primary["title"] = "Dune Messiah"
primary["version"] = 2
print("after write, primary:", primary)
print("plain replica read:", dict(replica))
print("read-your-writes read:", read(primary["version"]))

replicate()
print("read after replication:", read(primary["version"]))''',
            variant_b='read with required_version=1 after the write (the stale replica is allowed)',
            variant_c='skip replicate() entirely (what does the primary read keep returning?)',
            mistakes=[
                "Sending every read to a replica and breaking read-your-writes on the next page load.",
                "Comparing timestamps from different servers instead of a replication position or version.",
                "Assuming a cache flush also refreshes a replica that has not applied the write yet.",
            ],
            q1=(
                "Why does a version number make the freshness decision testable?",
                "The writer knows the version it produced and the replica reports the version it has applied, so a read can compare integers instead of guessing whether lag has passed.",
            ),
            homework=(
                "Write `read(primary, replica, required_version)` that serves the replica only when its version "
                "is at least the required one, otherwise falls back to the primary. Run it before and after a "
                "replication step, print both reads, and comment which line prevents a stale read after a write."
            ),
            patterns=["def ", "version", "print("],
            mapping=(
                "Postgres streaming replicas expose a log position; routers such as pgpool and application code "
                "can pin a session to the primary after writes. Cache invalidation and replica lag must be "
                "reasoned about together, because both can serve yesterday's answer."
            ),
        ),
        147: dict(
            topic="Data import and export",
            idea=(
                "Data arrives from spreadsheets, partners and old systems, and it leaves as exports, backups and "
                "migrations. Both directions are trust boundaries. An import may contain a missing column, a "
                "quoted comma, a duplicate key, a negative price or a number written as text; a good importer "
                "validates each row, records why it was rejected and commits the accepted rows in a controlled "
                "way. Failing the whole file because row 4,000 is malformed is often worse than accepting the "
                "good rows and reporting the bad ones, but that choice must be deliberate and visible. Exports "
                "have their own risks: the shape people consume becomes a contract, so column order and types "
                "deserve the same care as an API response. Money, dates and text encoding are the classic export "
                "bugs. A round trip — export, re-import, compare — is a cheap test that catches most of them. "
                "Streaming matters at scale; building a giant string in memory works for a thousand rows and dies "
                "at a million. Today you import CSV into SQLite with per-row rejections, export the accepted rows "
                "as JSON and assert the round trip preserves every field. Keep the rejection report beside the imported data; months later it is the only record of what never made it in."
            ),
            code=r'''import csv
import io
import json
import sqlite3

raw = "title,price_cents\nDune,999\nFoundation,abc\nCosmos,1500\n"
conn = sqlite3.connect(":memory:")
conn.execute(
    "CREATE TABLE books (id INTEGER PRIMARY KEY, title TEXT NOT NULL, price_cents INTEGER NOT NULL)"
)

accepted, rejected = [], []
for row in csv.DictReader(io.StringIO(raw)):
    try:
        price = int(row["price_cents"])
        if price < 0:
            raise ValueError("negative price")
        conn.execute(
            "INSERT INTO books (title, price_cents) VALUES (?, ?)",
            (row["title"], price),
        )
        accepted.append(row["title"])
    except (KeyError, ValueError) as exc:
        rejected.append((row["title"], str(exc)))
conn.commit()

print("accepted:", accepted)
print("rejected:", rejected)
rows = [{"id": r[0], "title": r[1], "price_cents": r[2]} for r in conn.execute(
    "SELECT id, title, price_cents FROM books ORDER BY id")]
wire = json.dumps(rows, sort_keys=True)
print("export:", wire)
print("round trip rows:", len(json.loads(wire)))''',
            variant_b='a quoted title "Dune, Part Two" (does DictReader keep it as one field?)',
            variant_c='a duplicate title appearing twice (should the importer reject or update?)',
            mistakes=[
                "Splitting CSV lines on commas, which breaks every quoted field containing one.",
                "Aborting the whole import on one bad row without reporting which row failed and why.",
                "Exporting floats for money or local timestamps that re-import ambiguously.",
            ],
            q1=(
                "Why record rejected rows instead of silently skipping them?",
                "The count and reasons are part of the import result; silent skips make a partial dataset look complete and leave nobody able to fix the source rows.",
            ),
            homework=(
                "Write `import_books(text, conn)` that uses csv.DictReader, validates each price and returns "
                "accepted and rejected lists, then `export_books(conn)` returning JSON. Run both on two CSV "
                "texts, print the round trip, and comment which line keeps a quoted comma intact."
            ),
            patterns=["def ", "DictReader", "print("],
            mapping=(
                "Bulk endpoints and admin tools use the same validate-then-commit pattern; pandas and csv both "
                "handle quoting, so never parse by hand. Stream large exports and version the schema, because "
                "consumers build on the columns you ship."
            ),
        ),
        148: dict(
            topic="Handling partial failures",
            idea=(
                "A batch request is a promise you may not be able to keep. Ten items arrive, seven are valid, "
                "two conflict with current stock and one is malformed. Returning a bare 500 loses the seven "
                "successes; returning 200 hides the three failures. The useful answer is a structured partial "
                "result: an overall status, a count of successes, and a per-item outcome that names the reason "
                "for each failure. The storage decisions behind it matter just as much. If each item is "
                "independent, give each its own transaction so one bad item does not roll back the rest. If the "
                "items form one logical unit, use a single transaction and fail all of them together, because a "
                "half-applied batch is worse than none. Either way, retries must be safe: a client that retries "
                "the failed items should not double-charge the ones that already succeeded, so each item needs a "
                "stable identifier and the handler must recognise a repeat. Today you process a batch against "
                "SQLite, let two items succeed, reject one for insufficient stock and one for an unknown key, and "
                "print a summary that separates the outcomes. Design the response before the handler: a client should be able to retry exactly the failed items by reading the per-item errors, without guessing which requests already landed."
            ),
            code=r'''import sqlite3

conn = sqlite3.connect(":memory:")
conn.execute(
    "CREATE TABLE inventory (sku TEXT PRIMARY KEY, qty INTEGER NOT NULL CHECK (qty >= 0))"
)
conn.executemany("INSERT INTO inventory VALUES (?, ?)", [("A-1", 5), ("B-2", 0)])
conn.commit()

items = [
    {"sku": "A-1", "qty": 2},
    {"sku": "B-2", "qty": 1},
    {"sku": "C-3", "qty": 4},
]

results = []
for item in items:
    try:
        conn.execute("BEGIN")
        cur = conn.execute(
            "UPDATE inventory SET qty = qty - ? WHERE sku = ? AND qty >= ?",
            (item["qty"], item["sku"], item["qty"]),
        )
        if cur.rowcount == 0:
            raise ValueError("insufficient stock or unknown sku")
        conn.execute("COMMIT")
        results.append((item["sku"], 204, "reserved"))
    except (sqlite3.Error, ValueError) as exc:
        conn.execute("ROLLBACK")
        results.append((item["sku"], 409, str(exc)))

print("results:", results)
print("inventory:", conn.execute("SELECT sku, qty FROM inventory ORDER BY sku").fetchall())
print("succeeded:", sum(1 for r in results if r[1] == 204),
      "| failed:", sum(1 for r in results if r[1] != 204))''',
            variant_b='wrap the whole loop in one transaction (one failure now rolls back every success)',
            variant_c='retry only the failed items (which ones succeed on the second pass?)',
            mistakes=[
                "Returning a bare 500 for a batch where most items succeeded.",
                "Using one transaction for independent items, so one conflict discards all the good work.",
                "Retrying a whole batch without item ids, so already-applied items are applied twice.",
            ],
            q1=(
                "When should a batch use one transaction for all items?",
                "When the items form a single logical unit, such as a transfer and its ledger entries; independent items should each get their own transaction so one failure does not erase the rest.",
            ),
            homework=(
                "Write `apply_batch(conn, items)` that gives each item its own transaction and returns a list of "
                "per-item statuses, then a summary counting successes and failures. Run it on two batches, print "
                "both results, and comment which line stops one bad item from rolling back the others."
            ),
            patterns=["def ", "BEGIN", "print("],
            mapping=(
                "Bulk APIs return 207-style per-item results; payment and inventory systems pair this with "
                "idempotency keys. Independent items get independent transactions, and every failure carries a "
                "machine-readable reason."
            ),
        ),
        149: dict(
            topic="Review: data behind the API",
            idea=(
                "Today is a review, so the work is to connect the pieces rather than add another. A schema gives "
                "the data a shape and refuses impossible rows. A transaction keeps multi-row invariants true. A "
                "connection pool bounds concurrency and makes lifecycle visible. A migration carries schema "
                "changes safely across environments. An ORM is convenient until it hides a query count. Uploads "
                "need validation, limits and generated storage names. Background jobs, webhooks and outbound "
                "calls all need retries and idempotency, because networks fail in the middle of work. Caches and "
                "replicas trade freshness for speed, so freshness must become an explicit decision. Pagination "
                "decides how a growing table is read, and import and export decide how data crosses the system "
                "boundary. Partial failures decide what a batch means when only some items succeed. The common "
                "thread is that every one of these is a place where an API can silently lie about what happened. "
                "The review question is not 'does it work on the happy path' but 'what does the client see when "
                "the database, the network or the partner misbehaves'. Today you assemble a small reporting "
                "endpoint and print the pieces that make its answer trustworthy. If you can explain, for each line of that endpoint, which failure it survives and which it does not, the phase has done its job."
            ),
            code=r'''import sqlite3

conn = sqlite3.connect(":memory:")
conn.execute("PRAGMA foreign_keys = ON")
conn.executescript("""
CREATE TABLE authors (id INTEGER PRIMARY KEY, name TEXT NOT NULL);
CREATE TABLE books (
    id INTEGER PRIMARY KEY,
    author_id INTEGER NOT NULL REFERENCES authors(id),
    title TEXT NOT NULL
);
INSERT INTO authors VALUES (1, 'Ada'), (2, 'Grace');
INSERT INTO books VALUES (1, 1, 'Dune'), (2, 1, 'Foundation'), (3, 2, 'Cosmos');
""")
conn.execute("CREATE INDEX books_author_idx ON books(author_id)")
conn.commit()

def report(author_id, limit=2):
    items = conn.execute(
        "SELECT id, title FROM books WHERE author_id = ? ORDER BY id LIMIT ?",
        (author_id, limit),
    ).fetchall()
    total = conn.execute(
        "SELECT COUNT(*) FROM books WHERE author_id = ?", (author_id,)
    ).fetchone()[0]
    return {"items": items, "total": total, "limit": limit}

print("authors:", conn.execute("SELECT id, name FROM authors ORDER BY id").fetchall())
print("report author 1:", report(1))
print("report author 2:", report(2))
print("foreign keys:", conn.execute("PRAGMA foreign_keys").fetchone()[0])
plan = conn.execute(
    "EXPLAIN QUERY PLAN SELECT id FROM books WHERE author_id = ?", (1,)
).fetchall()
print("query plan:", plan[0][3])
print("checklist: schema, transaction, index, pagination, errors")''',
            variant_b='ask for limit=1 (does total still report every book for that author?)',
            variant_c='drop the index and compare the query plan for author_id',
            mistakes=[
                "Judging the endpoint only by its happy-path output and never by its failure modes.",
                "Forgetting that a page limit changes items but not the total count.",
                "Shipping a schema change without a migration or a rollback plan.",
            ],
            q1=(
                "Why is the total count computed separately from the paginated items?",
                "The limit bounds the page size, while the client still needs the full size of the collection to know whether another page exists.",
            ),
            homework=(
                "Write `report(conn, author_id, limit)` that returns a paginated item list plus a full total, "
                "and assert the foreign keys are enabled. Run it on two authors with different limits, print "
                "both reports, and comment which line keeps the total correct when the page is truncated."
            ),
            patterns=["def ", "SELECT", "print("],
            mapping=(
                "This is the shape of a production read endpoint: constrained schema, indexed query, bounded "
                "page and a total for the client. Everything from this phase — transactions, migrations, "
                "replicas, caches and retries — exists to keep that small answer honest under failure."
            ),
        ),
    },
)
