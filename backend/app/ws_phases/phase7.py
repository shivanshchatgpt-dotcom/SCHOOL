"""Web Scraping capstone, days 165-179: build, test, operate and review one dataset.

The examples stay offline and stdlib-only, exactly like the earlier phases. Each
day advances the same deliverable: a small catalogue dataset that is fetched
politely, parsed into a fixed schema, stored without duplicates, tested against
saved fixtures, monitored, documented and finally presented.
"""

PHASE = (
    "Web Scraping Capstone",
    "Build, test, operate and present one trustworthy scraped dataset from a scoped public target.",
    {
        165: dict(
            topic="Choose a public target and scope",
            idea=(
                "Choosing a target is an eligibility decision before it is a technical one. Start by asking whether "
                "the site is public, whether its robots.txt and terms permit automated reading, whether the markup "
                "is stable enough to parse, and whether the data contains personal information. A site that fails "
                "those checks is not a capstone target, it is an incident waiting for a date. Prefer a sandbox "
                "catalogue, a government open-data index, or a practice shop with no login. Public visibility is not "
                "the same as permission, so record the answer you relied on and the date you checked it. Once the "
                "target passes, write the scope as a contract: one category, a named page range, the fields you will "
                "keep, the things you will explicitly ignore, and the snapshot date. For this capstone the scope is "
                "the books sandbox catalogue, listing pages one to fifty, book metadata only, with detail pages, "
                "reviews and images excluded. That boundary is deliberately small. You can finish it, rerun it, and "
                "explain every row. Ambition is not the scarce resource in a capstone; a defensible, reproducible "
                "boundary is. Write the scope down before you write a selector, because every later stage inherits "
                "it, and scope creep is the most common reason a promising capstone never produces a usable table."
            ),
            code=(
                'candidates = [\n'
                '    {"name": "books sandbox", "public": True, "robots": True, "terms": True, "pages": 50, "stable": True},\n'
                '    {"name": "social feed", "public": False, "robots": False, "terms": False, "pages": 10000, "stable": False},\n'
                '    {"name": "news archive", "public": True, "robots": True, "terms": False, "pages": 800, "stable": True},\n'
                ']\n'
                '\n'
                'def score(site):\n'
                '    if not (site["public"] and site["robots"] and site["terms"]):\n'
                '        return None\n'
                '    return site["pages"] // 50 - (0 if site["stable"] else 2)\n'
                '\n'
                'chosen = None\n'
                'for site in candidates:\n'
                '    value = score(site)\n'
                '    print(site["name"], "->", "reject" if value is None else f"score {value}")\n'
                '    if value is not None and (chosen is None or value > chosen[1]):\n'
                '        chosen = (site, value)\n'
                'print("scope:", chosen[0]["name"], "| pages:", min(chosen[0]["pages"], 50))\n'
                'assert chosen[0]["name"] == "books sandbox"\n'
                'print("scope frozen: one category, listing pages 1-50, no detail pages")'
            ),
            variant_b='make the news archive terms-allow reading and compare which target wins',
            variant_c='add a practice site with 20 stable pages and explain why scope beats score',
            mistakes=[
                "Picking a target because it is interesting, before checking robots and terms.",
                "Defining scope as a vague goal such as all books on the site.",
                "Including detail pages and images, which doubles work without improving the dataset.",
            ],
            q1=(
                "Why should the scope be written before the first selector is written?",
                "Every later stage inherits the page range and field list; a written boundary prevents silent scope creep and makes the run reproducible.",
            ),
            homework=(
                "Write `choose_target(candidates)` that rejects sites failing public, robots or terms checks and "
                "returns the eligible site with the best bounded page count. Run it on two candidate lists, print "
                "the rejected names and the chosen scope, and comment which line turns permission into a hard gate."
            ),
            patterns=["def ", "return", "print("],
            mapping=(
                "The chosen scope becomes the first line of the capstone runbook and the page list passed to the "
                "fetch layer on day 167. Excluded content is recorded, not quietly forgotten."
            ),
        ),
        166: dict(
            topic="Define the output schema",
            idea=(
                "A schema is the promise the pipeline makes to everything downstream. It names the fields, fixes "
                "their types, marks which are required, and decides what happens when a value is missing. Do this "
                "before writing the parser, because a parser shaped by whatever happened to be on the page produces "
                "a table that nobody can join to anything else. For the catalogue, the schema keeps six fields: "
                "title as text, price as a float, currency as a three-letter code, rating as an optional integer, "
                "in_stock as a boolean, and url as the product identity. Price is not stored as a display string; "
                "the currency is separate so amounts remain comparable. Rating is optional because some books have "
                "none, while title and url are required because a row without them cannot be identified. The "
                "missing-value policy belongs here too: skip the row if a required field is absent, keep the row "
                "with None if an optional field is absent, and never invent a default price. Version the schema so "
                "a later change is visible in the run log rather than discovered by a confused analyst. The schema "
                "also drives tests: every fixture row is checked against exactly these names and types. When the "
                "site adds a field, you decide whether it belongs in the contract; when it removes one, validation "
                "tells you immediately. A stable schema is what turns page scraps into a dataset someone can trust."
            ),
            code=(
                'SCHEMA = {\n'
                '    "title": (str, True),\n'
                '    "price": (float, True),\n'
                '    "currency": (str, True),\n'
                '    "rating": (int, False),\n'
                '    "in_stock": (bool, True),\n'
                '    "url": (str, True),\n'
                '}\n'
                '\n'
                'rows = [\n'
                '    {"title": "Dune", "price": 9.99, "currency": "GBP", "rating": 5, "in_stock": True, "url": "/dune/1"},\n'
                '    {"title": "Foundation", "price": "12.50", "currency": "GBP", "in_stock": True, "url": "/foundation/2"},\n'
                ']\n'
                '\n'
                'def check(row):\n'
                '    problems = []\n'
                '    for name, (kind, required) in SCHEMA.items():\n'
                '        if name not in row:\n'
                '            if required:\n'
                '                problems.append("missing:" + name)\n'
                '            continue\n'
                '        if not isinstance(row[name], kind):\n'
                '            problems.append("type:" + name)\n'
                '    return problems\n'
                '\n'
                'for row in rows:\n'
                '    print(row["title"], "->", check(row) or "ok")\n'
                'assert check(rows[1]) == ["type:price"]\n'
                'print("schema v1: six fields, price is numeric, rating is optional")'
            ),
            variant_b='add an optional published_year field and validate a row that omits it',
            variant_c='change rating to required and see which fixture row now fails',
            mistakes=[
                "Storing price as text, which makes sorting and averaging silently wrong.",
                "Using blank strings for missing optional values instead of None.",
                "Adding fields to the parser without updating the schema and its tests.",
            ],
            q1=(
                "Why is currency a separate field instead of part of the price string?",
                "Separating the amount from its currency keeps price numeric and comparable, and makes a currency change visible instead of hidden in text.",
            ),
            homework=(
                "Write `validate_row(row, schema)` that returns a list of missing required fields and wrong-typed "
                "values. Run it on two rows, one valid and one with a text price, print both problem lists, and "
                "comment which line enforces the required-versus-optional distinction."
            ),
            patterns=["def ", "isinstance(", "return"],
            mapping=(
                "This exact schema becomes the SQLite table in day 169 and the data dictionary in the runbook. "
                "The parser's only job is to produce rows that pass this check."
            ),
        ),
        167: dict(
            topic="Build the fetch layer",
            idea=(
                "The fetch layer is the only part of the pipeline that talks to the network, and its job is to hide "
                "that fact from everything else. It accepts a path, applies a timeout, sends an honest user agent, "
                "records the status and returns a structured result containing ok, status, body and the number of "
                "attempts. It never parses, never stores, and never decides what a row means. That separation is "
                "what lets you test the whole capstone offline: replace the transport with a dictionary of canned "
                "responses and the calling code cannot tell the difference. Today's fixture fetch models three "
                "outcomes: a page that succeeds immediately, a transient 503 that disappears on the second attempt, "
                "and a 404 that must not be retried. Notice that failure is a normal return value, not an exception "
                "escaping into the crawl loop. The caller can then count, log and decide whether to continue. Keep "
                "the response body as text at this boundary, because decoding belongs to the layer that understands "
                "the page's declared charset. Add timeouts and retry limits as parameters rather than constants so "
                "tests can drive them without sleeping. A fetch layer that is boring, bounded and observable is the "
                "difference between a script that works once and a pipeline that can run tomorrow."
            ),
            code=(
                'FIXTURES = {\n'
                '    "/page-1.html": [(200, "<article>Dune</article>")],\n'
                '    "/page-2.html": [(503, "busy"), (200, "<article>Foundation</article>")],\n'
                '}\n'
                '\n'
                'def fetch(path, attempts=2):\n'
                '    replies = FIXTURES.get(path, [(404, "")])\n'
                '    for number in range(1, attempts + 1):\n'
                '        status, body = replies[min(number - 1, len(replies) - 1)]\n'
                '        print(f"attempt {number} {path} -> {status}")\n'
                '        if status == 200:\n'
                '            return {"ok": True, "status": status, "body": body, "attempts": number}\n'
                '        if status < 500:\n'
                '            return {"ok": False, "status": status, "body": "", "attempts": number}\n'
                '    return {"ok": False, "status": status, "body": "", "attempts": attempts}\n'
                '\n'
                'for path in ["/page-1.html", "/page-2.html", "/missing.html"]:\n'
                '    result = fetch(path)\n'
                '    print(path, "ok:", result["ok"], "status:", result["status"], "attempts:", result["attempts"])\n'
                'assert fetch("/missing.html")["attempts"] == 1\n'
                'print("fetch contract: result record, no parsing, no exception leak")'
            ),
            variant_b='give the transient page three 503 replies and confirm the attempts cap is respected',
            variant_c='add a fixture that returns 200 with an empty body and decide whether that is success',
            mistakes=[
                "Parsing inside fetch, which makes offline tests depend on real markup.",
                "Retrying a 404 and wasting requests on a page that will never exist.",
                "Letting a transport exception escape and abort every remaining page.",
            ],
            q1=(
                "Why does the fetch layer return a result dictionary instead of raising on failure?",
                "A result keeps the run alive and carries status and attempts, so the caller can classify, count and report the failure without losing good pages.",
            ),
            homework=(
                "Write `fetch_all(paths, fixtures)` that returns one result dictionary per path, retries only 5xx "
                "responses up to two attempts, and never retries a 404. Run it on two fixture sets, print statuses "
                "and attempt counts, and comment which line separates retryable from permanent failures."
            ),
            patterns=["def ", "return", "for "],
            mapping=(
                "Day 177 calls this layer with the scoped page list. Swapping the fixture dictionary for a real "
                "HTTP client later changes only the transport, not the crawl or parser."
            ),
        ),
        168: dict(
            topic="Build the parser",
            idea=(
                "The parser turns one saved page into zero or more rows that match the schema. It receives text, "
                "walks the card markup, and reads each field by its own selector. Keep the card boundary explicit: "
                "start a record when an article opens, fill fields while inside it, and append only when the "
                "article closes. That structure prevents a missing price in one card from stealing the price from "
                "the next. Required fields are checked at the end of each card; a card without a title or price is "
                "reported as a parse failure rather than emitted as a half-row. Optional fields such as rating may "
                "be absent without rejecting the book. Resist the temptation to clean everything here. Convert the "
                "price to a float because the schema says float, and turn the stock phrase into a boolean, but leave "
                "whitespace normalisation and URL canonicalisation to their own small functions. Today's example "
                "uses the standard library's event-driven HTML parser, which is deliberately more verbose than a "
                "selector library. That verbosity is useful: you can see exactly where each value came from. When a "
                "friendlier parser arrives later, it will be a convenience over this model, not a replacement for "
                "it. A parser that can say which card failed, and why, is worth more than one that silently returns "
                "fewer rows."
            ),
            code=(
                'from html.parser import HTMLParser\n'
                '\n'
                'page = (\n'
                '    \'<article class="product" data-url="/dune/1"><h3>Dune</h3>\'\n'
                '    \'<span class="price">9.99</span><span class="stock">In stock</span></article>\'\n'
                '    \'<article class="product" data-url="/foundation/2"><h3>Foundation</h3>\'\n'
                '    \'<span class="price">12.50</span><span class="stock">Out of stock</span></article>\'\n'
                ')\n'
                '\n'
                'class Catalog(HTMLParser):\n'
                '    def __init__(self):\n'
                '        super().__init__()\n'
                '        self.rows, self.card, self.field = [], None, None\n'
                '    def handle_starttag(self, tag, attrs):\n'
                '        attrs = dict(attrs)\n'
                '        if tag == "article":\n'
                '            self.card = {"url": attrs.get("data-url"), "title": "", "price": 0.0, "in_stock": True}\n'
                '        elif self.card is not None and tag == "h3":\n'
                '            self.field = "title"\n'
                '        elif self.card is not None and "class" in attrs:\n'
                '            self.field = attrs["class"]\n'
                '    def handle_data(self, data):\n'
                '        if self.card is None or self.field is None:\n'
                '            return\n'
                '        text = data.strip()\n'
                '        if self.field == "price":\n'
                '            self.card["price"] = float(text)\n'
                '        elif self.field == "stock":\n'
                '            self.card["in_stock"] = "Out" not in text\n'
                '        elif self.field == "title":\n'
                '            self.card["title"] = text\n'
                '        self.field = None\n'
                '    def handle_endtag(self, tag):\n'
                '        if tag == "article" and self.card is not None:\n'
                '            self.rows.append(self.card)\n'
                '            self.card = None\n'
                '\n'
                'parser = Catalog()\n'
                'parser.feed(page)\n'
                'for row in parser.rows:\n'
                '    print(row)\n'
                'assert len(parser.rows) == 2 and parser.rows[1]["in_stock"] is False\n'
                'print("parser emitted", len(parser.rows), "complete rows")'
            ),
            variant_b='add a third card with no price and make the parser report it instead of emitting a row',
            variant_c='include an optional rating span and keep it as None when the span is absent',
            mistakes=[
                "Reading fields with page-wide searches, so one card can consume another card's price.",
                "Emitting a row before checking required fields, leaving half-valid data downstream.",
                "Cleaning URLs and whitespace in the parser instead of in dedicated normalisers.",
            ],
            q1=(
                "Why should the parser check required fields per card rather than after the whole page?",
                "Per-card checks identify the exact failing card and prevent a missing value from being filled by a neighbouring card.",
            ),
            homework=(
                "Write `parse_catalog(html)` that returns complete rows and a list of card-level errors, using the "
                "schema fields title, price, currency, in_stock and url. Run it on two pages, one clean and one with "
                "a missing price, print rows and errors, and comment which line keeps the bad card out of the output."
            ),
            patterns=["class ", "def ", "assert "],
            mapping=(
                "This parser is the component under test on day 170 and the parse stage of the day 177 integration. "
                "Its card-level error list feeds the run summary."
            ),
        ),
        169: dict(
            topic="Store and deduplicate rows",
            idea=(
                "Storage is where a scrape becomes a dataset, and the central question is identity. Two rows are the "
                "same record when they describe the same product, not when their text looks similar. Choose a stable "
                "key such as the canonical product URL or an ISBN, declare it as the primary key, and let the "
                "database enforce uniqueness instead of trusting a Python set that disappears when the process "
                "ends. Use an insert-or-ignore policy when the first observation is authoritative, or insert-or-"
                "replace when the latest price should win. Either way, write the decision down, because a silent "
                "change from one policy to the other rewrites history. Batch inserts inside one transaction so a "
                "crash cannot leave half a page in the table. Count both parsed rows and inserted rows: three parsed "
                "rows producing two stored rows is expected when a duplicate exists, but thirty parsed rows "
                "producing two stored rows is a warning about the key. Keep timestamps for first seen and last seen "
                "if prices change, and keep the raw price text alongside the numeric value when provenance matters. "
                "Finally, prove idempotency by running the same batch twice and checking that the table size does "
                "not move. A pipeline that duplicates data on every rerun is not a pipeline, it is a growing pile."
            ),
            code=(
                'import sqlite3\n'
                '\n'
                'rows = [\n'
                '    {"url": "/dune/1", "title": "Dune", "price": 9.99},\n'
                '    {"url": "/foundation/2", "title": "Foundation", "price": 12.50},\n'
                '    {"url": "/dune/1", "title": "Dune", "price": 9.99},\n'
                ']\n'
                '\n'
                'db = sqlite3.connect(":memory:")\n'
                'db.execute("CREATE TABLE books (url TEXT PRIMARY KEY, title TEXT, price REAL)")\n'
                '\n'
                'def store(batch):\n'
                '    before = db.execute("SELECT COUNT(*) FROM books").fetchone()[0]\n'
                '    db.executemany("INSERT OR IGNORE INTO books VALUES (:url, :title, :price)", batch)\n'
                '    db.commit()\n'
                '    after = db.execute("SELECT COUNT(*) FROM books").fetchone()[0]\n'
                '    return {"parsed": len(batch), "inserted": after - before, "total": after}\n'
                '\n'
                'print("first run:", store(rows))\n'
                'print("second run:", store(rows))\n'
                'print("stored:", db.execute("SELECT url, price FROM books ORDER BY url").fetchall())\n'
                'assert db.execute("SELECT COUNT(*) FROM books").fetchone()[0] == 2\n'
                'print("idempotent: 3 parsed rows became 2 unique books")'
            ),
            variant_b='switch to INSERT OR REPLACE and change the Dune price on the second run',
            variant_c='use a Python set before insert and show why it forgets across process restarts',
            mistakes=[
                "Deduplicating only in memory, so a second run duplicates every row.",
                "Using the display title as the primary key when two books share a title.",
                "Committing each row separately and leaving a partial page when the run dies.",
            ],
            q1=(
                "Why should uniqueness be enforced by the database primary key rather than a Python set?",
                "A set lives only for one process; a primary key protects every run, every writer and every restart, and makes duplicate inserts fail or be ignored deterministically.",
            ),
            homework=(
                "Write `store_rows(rows, db)` that creates a books table keyed by canonical URL, inserts a batch "
                "idempotently and returns parsed, inserted and total counts. Run it twice on two batches, print the "
                "counts, and comment which line makes the rerun safe."
            ),
            patterns=["sqlite3", "PRIMARY KEY", "executemany("],
            mapping=(
                "This table is the capstone's durable output on day 178. The insert and duplicate counts become "
                "fields in the scheduled run report on day 172."
            ),
        ),
        170: dict(
            topic="Test the parser with fixtures",
            idea=(
                "A fixture is a saved page that never changes, and it is the closest thing a scraper has to a unit "
                "test. Save small anonymised HTML snapshots for the normal page, a page with a missing optional "
                "field, a page with broken card markup, and a page that is empty after a successful fetch. Then "
                "assert the exact rows the parser should produce. Exact expected dictionaries are better than count-"
                "only checks, because a count of two can hide swapped prices or titles. The most valuable fixture is "
                "the one that reproduces yesterday's bug: it turns a one-off fix into a permanent guard. Tests must "
                "run offline, fast and without credentials, so the fetch layer is replaced by strings. Include a "
                "zero-row guard: a non-empty page that produces no rows is almost always a selector change, not an "
                "empty catalogue, and it should fail loudly. Do not let a test quietly accept an empty list just "
                "because the parser did not raise. When the site changes, first save the new page as a fixture, then "
                "watch the old tests fail, then update the parser and add the new expectation. That order proves the "
                "test actually observes the change. Fixtures are executable documentation of the markup contract, "
                "and they are the reason you can refactor a parser without fear."
            ),
            code=(
                'import re\n'
                '\n'
                'FIXTURES = {\n'
                '    "normal": \'<article class="product" data-url="/a"><h3>A</h3><span class="price">9.99</span></article>\',\n'
                '    "missing_price": \'<article class="product" data-url="/b"><h3>B</h3></article>\',\n'
                '    "changed_markup": \'<div class="card" data-url="/c"><h3>C</h3><span class="price">7.00</span></div>\',\n'
                '}\n'
                '\n'
                'def parse(html):\n'
                '    rows = []\n'
                '    pattern = r\'<article class="product" data-url="([^"]+)">(.*?)</article>\'\n'
                '    for url, block in re.findall(pattern, html, re.S):\n'
                '        title = re.search(r"<h3>(.*?)</h3>", block)\n'
                '        price = re.search(r\'class="price">([\\d.]+)<\', block)\n'
                '        if title and price:\n'
                '            rows.append({"url": url, "title": title.group(1), "price": float(price.group(1))})\n'
                '    return rows\n'
                '\n'
                'def checked(html):\n'
                '    rows = parse(html)\n'
                '    if not rows and html.strip():\n'
                '        raise ValueError("non-empty page produced zero rows")\n'
                '    return rows\n'
                '\n'
                'for name, html in FIXTURES.items():\n'
                '    try:\n'
                '        print(name, "->", checked(html))\n'
                '    except ValueError as error:\n'
                '        print(name, "-> error:", error)\n'
                'assert len(checked(FIXTURES["normal"])) == 1\n'
                'print("fixture suite: one pass, two documented failures")'
            ),
            variant_b='add a duplicate-card fixture and assert that the parser returns both rows for storage to deduplicate',
            variant_c='save a page where price is nested in a span inside the price element and update the expectation',
            mistakes=[
                "Testing only row counts, which cannot detect a title and price swapped between rows.",
                "Accepting zero rows from a non-empty page as a valid empty catalogue.",
                "Hitting the live site in tests, making results depend on today's markup.",
            ],
            q1=(
                "Why is a fixture-based test better than a test that fetches the live page?",
                "A fixture is stable and offline, so a failure points at the parser rather than at the network, the site or the day's markup.",
            ),
            homework=(
                "Write `run_fixtures(fixtures)` that parses each saved page, compares the rows with an expected "
                "dictionary and raises on any mismatch or unexplained zero-row page. Run it on two fixture sets, one "
                "passing and one with changed markup, print both reports, and comment which assertion catches the "
                "silent selector failure."
            ),
            patterns=["assert ", "raise ", "print("],
            mapping=(
                "These fixtures live beside the capstone parser and run before every change. The changed-markup "
                "fixture becomes the regression case for day 175."
            ),
        ),
        171: dict(
            topic="Add politeness and retries",
            idea=(
                "Politeness is not a courtesy added at the end; it is part of the fetch contract. A polite scraper "
                "waits between requests, limits concurrency, identifies itself honestly, honours robots.txt and "
                "treats 429 responses as a signal to slow down rather than a challenge to evade. Retries are the "
                "other half of that contract. Retry timeouts and 5xx responses a small bounded number of times, with "
                "increasing waits and a little jitter so several workers do not synchronise into a new spike. Never "
                "retry a 404 or a 403, and never retry forever. Honour a Retry-After header when one is present, even "
                "in a simplified model. The useful engineering trick is to make time injectable: pass a virtual clock "
                "into the retry function so tests can prove the backoff schedule without sleeping for real. Then the "
                "policy is observable and cheap to change. Keep the delay, attempt cap and backoff curve in one "
                "place, because scattered sleeps are impossible to audit. For a fifty-page capstone, one request "
                "every second and no concurrency is already enough. The goal is not maximum throughput; it is a run "
                "that finishes, does not harm the server, and can be repeated tomorrow without being blocked."
            ),
            code=(
                'responses = {"/a": [503, 200], "/b": [200], "/c": [404]}\n'
                'clock = [0.0]\n'
                '\n'
                'def fetch(path, max_attempts=3):\n'
                '    trace = []\n'
                '    for attempt in range(1, max_attempts + 1):\n'
                '        queue = responses[path]\n'
                '        status = queue.pop(0) if len(queue) > 1 else queue[0]\n'
                '        trace.append((round(clock[0], 1), attempt, status))\n'
                '        if status == 200:\n'
                '            return {"ok": True, "trace": trace}\n'
                '        if status < 500:\n'
                '            return {"ok": False, "kind": "permanent", "trace": trace}\n'
                '        clock[0] += 2 ** attempt\n'
                '    return {"ok": False, "kind": "exhausted", "trace": trace}\n'
                '\n'
                'results = {}\n'
                'for path in responses:\n'
                '    results[path] = fetch(path)\n'
                '    clock[0] += 1.0\n'
                '    print(path, results[path]["trace"], results[path].get("kind", "ok"))\n'
                'assert results["/c"]["kind"] == "permanent"\n'
                'print("backoff waits:", [row[0] for row in results["/a"]["trace"]])'
            ),
            variant_b='add a Retry-After value of 10 seconds for the 503 and place it in the trace',
            variant_c='raise max_attempts to five for a path that always returns 500 and show the cap',
            mistakes=[
                "Sleeping a fixed short time and retrying a permanent 404 forever.",
                "Running many workers in parallel on a small target and turning a polite crawl into a burst.",
                "Hard-coding sleep inside the parser, where it cannot be tested or audited.",
            ],
            q1=(
                "Why should the retry delay double with each attempt instead of staying constant?",
                "Exponential backoff gives an overloaded server room to recover and reduces repeated collisions, while a constant delay keeps the same pressure on every retry.",
            ),
            homework=(
                "Write `retry_schedule(statuses, max_attempts)` that returns the wait time before each attempt and "
                "stops immediately on 404 or 403. Run it on two status sequences, one recovering from 503 and one "
                "hitting a permanent failure, print both schedules, and comment which line prevents the endless retry."
            ),
            patterns=["for ", "return", "print("],
            mapping=(
                "Day 177 runs the scoped pages through this policy, and the attempt counts appear in the day 172 "
                "run summary. Real sleeps are added only when the fixture transport is replaced."
            ),
        ),
        172: dict(
            topic="Schedule and monitor the run",
            idea=(
                "A scraper that only runs when you remember it is a demo. Scheduling makes it a pipeline, and "
                "monitoring makes the schedule trustworthy. The scheduler can be cron, systemd, or a platform job, "
                "but the pipeline must behave well under it: exit non-zero on a real failure, write a run manifest, "
                "and take a lock so two runs cannot overlap. The manifest is the single most useful artifact. It "
                "records the start time, duration, pages attempted, pages parsed, rows emitted, duplicate rows, "
                "error counts by kind, and the previous run's totals. From those numbers you can derive three "
                "signals: success rate, row drift and freshness. A run that parses thirty of fifty pages is not a "
                "success just because it exited cleanly. A run that emits forty rows where the previous one emitted "
                "nine hundred is probably a selector regression or a blocked request. Compare against the previous "
                "run rather than a magic constant, and alert on thresholds you can explain. Store one JSON line per "
                "run so history is cheap to inspect. Today's example turns two synthetic run records into summaries "
                "and an alert decision. Notice that the second run has a perfect exit story and still fails the "
                "health check, which is exactly why row counts belong in monitoring."
            ),
            code=(
                'runs = [\n'
                '    {"started": "2026-10-19T02:00:00", "attempted": 50, "ok": 48, "rows": 962, "previous": 958},\n'
                '    {"started": "2026-10-20T02:00:00", "attempted": 50, "ok": 31, "rows": 40, "previous": 962},\n'
                ']\n'
                '\n'
                'def report(run):\n'
                '    success = round(100 * run["ok"] / run["attempted"])\n'
                '    drift = run["rows"] - run["previous"]\n'
                '    if run["ok"] < run["attempted"] * 0.8:\n'
                '        state = "alert"\n'
                '    elif abs(drift) > max(10, run["previous"] * 0.1):\n'
                '        state = "warn"\n'
                '    else:\n'
                '        state = "ok"\n'
                '    return {"success_pct": success, "row_delta": drift, "state": state}\n'
                '\n'
                'for run in runs:\n'
                '    summary = report(run)\n'
                '    print(run["started"], summary)\n'
                '    if summary["state"] != "ok":\n'
                '        print("  action: inspect failed pages and the parser fixture")\n'
                'assert report(runs[0])["state"] == "ok" and report(runs[1])["state"] == "alert"\n'
                'print("monitor thresholds: 80% pages parsed and 10% row drift")'
            ),
            variant_b='give the second run 45 successful pages and make row drift the trigger instead',
            variant_c='add a duration field and alert when a run takes twice as long as the previous one',
            mistakes=[
                "Treating a zero exit code as proof that the data is complete.",
                "Alerting on absolute row counts instead of comparing with the previous run.",
                "Allowing two scheduled runs to overlap and write the same rows at once.",
            ],
            q1=(
                "Why is row drift more informative than exit status alone?",
                "A run can exit cleanly after parsing almost nothing; comparing row counts with the previous run reveals silent selector or blocking failures.",
            ),
            homework=(
                "Write `run_health(run, previous)` that returns success percentage, row delta and an alert state "
                "based on two documented thresholds. Run it on two run records, one healthy and one degraded, print "
                "both summaries, and comment which line turns a raw count into an actionable signal."
            ),
            patterns=["def ", "if ", "print("],
            mapping=(
                "Each capstone execution appends one manifest line. The final report on day 178 reads the latest "
                "manifest so the dataset always carries its own freshness and health."
            ),
        ),
        173: dict(
            topic="Document the pipeline",
            idea=(
                "Documentation is a deliverable, not an afterthought. The test of a finished pipeline is simple: "
                "someone else can run it from a clean checkout, understand what it produces, and know what to do "
                "when it fails. That requires more than a list of commands. Write a short README with the purpose "
                "and target scope, the exact run command, the schedule, the output location, and the owner. Add a "
                "data dictionary generated from the schema so field names and types cannot drift apart from the "
                "code. Add a failure playbook: check the run manifest, rerun only the failed pages, inspect the "
                "saved raw fixture, and open an issue with the run id. Record the provenance of the target and the "
                "date the terms were reviewed. Keep a changelog for parser versions, because a selector change is a "
                "data change and downstream users deserve to know. The best documentation is close to the code it "
                "describes: a command in the README should be copy-pasteable, and a field in the dictionary should "
                "match the schema exactly. Today you generate the runbook from a small configuration dictionary, "
                "which makes the relationship visible. If the generator is too much, a hand-written page with the "
                "same headings is fine. What is not fine is an undocumented pipeline that only its author can "
                "resurrect."
            ),
            code=(
                'config = {\n'
                '    "target": "books sandbox, catalogue listing pages 1-50",\n'
                '    "command": "python -m scraper.run --pages 1-50",\n'
                '    "schedule": "daily at 02:00 UTC",\n'
                '    "owner": "data team",\n'
                '}\n'
                'schema = [("title", "str"), ("price", "float"), ("in_stock", "bool"), ("url", "str")]\n'
                '\n'
                'def build_runbook(config, schema):\n'
                '    lines = ["# Catalogue pipeline", "", "## Scope", config["target"], "", "## Run", "```",\n'
                '             config["command"], "```", "", "## Schedule", config["schedule"], "", "## Data dictionary"]\n'
                '    lines += [f"- {name}: {kind}" for name, kind in schema]\n'
                '    lines += ["", "## Failure playbook", "1. Read the latest run manifest.",\n'
                '              "2. Rerun the failed page range.", "3. Save the raw page as a fixture before patching."]\n'
                '    return "\\n".join(lines)\n'
                '\n'
                'doc = build_runbook(config, schema)\n'
                'print(doc)\n'
                'assert "price: float" in doc and "--pages 1-50" in doc\n'
                'print("runbook sections:", doc.count("##"))'
            ),
            variant_b='add a provenance section with the robots and terms review date',
            variant_c='add a changelog entry for a parser selector change and print the updated runbook',
            mistakes=[
                "Documenting the goal but not the exact command and page range.",
                "Letting the data dictionary drift from the schema and parser.",
                "Omitting the failure playbook, leaving the next operator to improvise.",
            ],
            q1=(
                "Why should the runbook include a failure playbook instead of only setup instructions?",
                "Most pipeline incidents happen during a run; a playbook tells the next operator which artifact to inspect and which safe rerun to perform.",
            ),
            homework=(
                "Write `build_readme(config, schema, failures)` that renders scope, command, schedule, data "
                "dictionary and a numbered failure playbook. Run it on two configurations, one with retries and one "
                "with a parser change, print both documents, and comment which line keeps field types aligned with "
                "the schema."
            ),
            patterns=["def ", "return", "print("],
            mapping=(
                "The capstone's README, data dictionary and failure playbook are generated or checked in beside the "
                "code. The day 179 review marks the runbook as complete only if a new operator can follow it."
            ),
        ),
        174: dict(
            topic="Ethics and legal review",
            idea=(
                "A public page is not automatically a public dataset. Before the capstone runs on any target, write "
                "a short review that answers five questions: does robots.txt allow the path, do the terms permit "
                "automated reading, is any personal data involved, is the content copyrighted, and what request rate "
                "is defensible. Each answer changes the design. Personal data requires a lawful basis and a "
                "retention rule, so the simplest capstone decision is to exclude it entirely. Copyrighted "
                "descriptions should not be republished in full; store facts such as title, price and availability, "
                "and quote only what you genuinely need. Respect rate limits and identify the crawler honestly. "
                "Never bypass a login, a paywall or a CAPTCHA, and never disguise traffic to avoid a block. Record "
                "the review date and the exact policy text you relied on, because terms change and memory is not "
                "evidence. Today's example turns a small policy record into a list of blockers and mitigations. The "
                "code is not legal advice, and it does not decide difficult cases; it forces the questions into the "
                "open before work begins. If a blocker cannot be removed, choose a different target. That is a "
                "successful review, not a failed project. Ethics is part of the engineering, and the best time to "
                "discover a problem is before the first request."
            ),
            code=(
                'review = {\n'
                '    "robots_allowed": True,\n'
                '    "terms_allow_read": True,\n'
                '    "personal_data": False,\n'
                '    "copyrighted_text": True,\n'
                '    "requests_per_minute": 20,\n'
                '    "purpose": "price trend research",\n'
                '}\n'
                '\n'
                'def findings(item):\n'
                '    notes = []\n'
                '    if not item["robots_allowed"]:\n'
                '        notes.append("block: robots.txt disallows this path")\n'
                '    if not item["terms_allow_read"]:\n'
                '        notes.append("block: terms forbid automated access")\n'
                '    if item["personal_data"]:\n'
                '        notes.append("block: personal data needs a lawful basis")\n'
                '    if item["copyrighted_text"]:\n'
                '        notes.append("mitigate: store facts, not full descriptions")\n'
                '    if item["requests_per_minute"] > 30:\n'
                '        notes.append("mitigate: lower the request rate")\n'
                '    return notes\n'
                '\n'
                'notes = findings(review)\n'
                'print("purpose:", review["purpose"])\n'
                'for note in notes or ["no findings"]:\n'
                '    print("-", note)\n'
                'assert any(note.startswith("mitigate") for note in notes)\n'
                'print("decision: collect metadata and prices, exclude descriptions and personal data")'
            ),
            variant_b='set personal_data to True and show that the review now has a hard blocker',
            variant_c='raise requests_per_minute to 60 and explain which mitigation changes',
            mistakes=[
                "Assuming public access means the terms permit scraping.",
                "Storing full descriptions and then calling the dataset factual.",
                "Ignoring a 403 or robots restriction and trying to look like a browser.",
            ],
            q1=(
                "Why is excluding personal data often the right capstone decision?",
                "Personal data adds legal basis, retention and deletion obligations that a small capstone cannot justify; excluding it keeps the dataset factual and the project defensible.",
            ),
            homework=(
                "Write `review_target(policy)` that returns separate hard blockers and mitigations for robots, "
                "terms, personal data, copyright and request rate. Run it on two policy records, one clean and one "
                "with personal data, print both decisions, and comment which line separates a blocker from a "
                "mitigation."
            ),
            patterns=["def ", "if ", "return"],
            mapping=(
                "The capstone record includes the review date, the chosen purpose and the excluded fields. A hard "
                "blocker stops the run; a mitigation becomes a documented design constraint."
            ),
        ),
        175: dict(
            topic="Handle one failure end to end",
            idea=(
                "Every scraper eventually meets the same incident: the page still returns 200, but the parser now "
                "emits zero rows. The professional response is a loop, not a guess. First reproduce the failure "
                "from a saved raw page, because a live page may change again while you debug. Second, classify it: "
                "is the status wrong, is the page blocked, or did the markup move a field? Third, patch the "
                "smallest layer that owns the problem. A moved price attribute belongs in the parser, not in the "
                "fetch layer and not behind a broad exception handler. Fourth, add the failing page as a regression "
                "fixture and watch it fail before the fix. Fifth, rerun only the affected stage and compare counts "
                "with the previous run. Finally, write a short incident note: symptom, root cause, fix, fixture and "
                "run id. Today's example moves a price from element text into a data-amount attribute. The old "
                "parser raises, the new one reads the attribute, and both old and new fixtures pass after the "
                "patch. Notice that the fix is a selector change plus a guard, not a rewrite. The loop matters more "
                "than the specific bug: reproduce, classify, patch narrowly, lock with a fixture, verify, document. "
                "Practise it once here and every future markup change becomes routine instead of alarming."
            ),
            code=(
                'old_page = \'<article class="product" data-url="/dune"><h3>Dune</h3><span class="price">9.99</span></article>\'\n'
                'new_page = \'<article class="product" data-url="/dune"><h3>Dune</h3><span class="price" data-amount="9.99">GBP 9.99</span></article>\'\n'
                '\n'
                'def parse(html, mode="old"):\n'
                '    title = html.split("<h3>")[1].split("</h3>")[0]\n'
                '    if mode == "old":\n'
                '        price = float(html.split(\'class="price">\')[1].split("<")[0])\n'
                '    else:\n'
                '        price = float(html.split(\'data-amount="\')[1].split(\'"\')[0])\n'
                '    return {"title": title, "price": price}\n'
                '\n'
                'print("old markup:", parse(old_page))\n'
                'try:\n'
                '    parse(new_page)\n'
                'except (IndexError, ValueError) as error:\n'
                '    print("regression reproduced:", type(error).__name__)\n'
                'fixed = parse(new_page, mode="new")\n'
                'print("patched parser:", fixed)\n'
                'assert parse(old_page)["price"] == 9.99 and fixed["price"] == 9.99\n'
                'print("both fixtures pass after a selector-only patch")'
            ),
            variant_b='move the title into a data-title attribute and patch the title selector instead',
            variant_c='keep the old price text in the page and prefer data-amount only when present',
            mistakes=[
                "Wrapping the whole parser in a broad try block so the failure disappears from the report.",
                "Patches the parser without saving the failing page as a regression fixture.",
                "Rewriting the fetch layer when only a selector changed.",
            ],
            q1=(
                "Why reproduce the failure from a saved raw page before changing the parser?",
                "The saved page is stable evidence; it lets you diagnose and test the exact failure without the live site changing again during debugging.",
            ),
            homework=(
                "Write `diagnose(old_html, new_html)` that parses both pages, reports the failing field, and returns "
                "a narrow patch result for the new markup. Run it on two markup-change pairs, print both diagnoses, "
                "and comment which line proves the old fixture still passes after the patch."
            ),
            patterns=["def ", "try:", "assert "],
            mapping=(
                "The capstone parser keeps this new page as a regression fixture and records the selector change in "
                "the runbook changelog. The incident note becomes part of the handoff on day 179."
            ),
        ),
        176: dict(
            topic="Present the dataset",
            idea=(
                "A dataset is finished when someone else can understand it, not when the script stops. Presentation "
                "starts with the audience and the question: what decision will this table support? Then show the "
                "smallest useful summary. For the catalogue that means row count, unique titles, priced rows, "
                "missing-price count, minimum, maximum and mean price, plus the snapshot date. One clear table with "
                "units and labels beats six decorative charts. If a chart is added, label both axes and state the "
                "date range. Accompany the numbers with provenance: which target, which pages, which parser version, "
                "and which run produced them. State the limitations plainly, including missing prices, unparsed "
                "pages and the fact that a price is a single observation rather than a historical series. A small "
                "sample of real rows helps readers sanity-check what a record looks like. Do not overclaim "
                "completeness from a scoped crawl. The dataset card is the deliverable: purpose, scope, schema, "
                "counts, quality signals, provenance, limitations and a reproducible command. Today you compute that "
                "summary from a small list of rows and render it as a markdown table. The exercise is deliberately "
                "plain, because clarity is the skill. If the reader cannot tell how many rows are missing a price, "
                "the presentation has failed regardless of how attractive it looks."
            ),
            code=(
                'rows = [\n'
                '    {"title": "Dune", "price": 9.99, "rating": 5},\n'
                '    {"title": "Foundation", "price": 12.50, "rating": 4},\n'
                '    {"title": "Dune", "price": 9.99, "rating": 5},\n'
                '    {"title": "Emma", "price": None, "rating": 3},\n'
                ']\n'
                '\n'
                'def summarise(rows):\n'
                '    prices = [row["price"] for row in rows if row["price"] is not None]\n'
                '    return {\n'
                '        "rows": len(rows),\n'
                '        "unique_titles": len({row["title"] for row in rows}),\n'
                '        "priced_rows": len(prices),\n'
                '        "missing_price": len(rows) - len(prices),\n'
                '        "min_price": min(prices),\n'
                '        "max_price": max(prices),\n'
                '        "mean_price": round(sum(prices) / len(prices), 2),\n'
                '    }\n'
                '\n'
                'summary = summarise(rows)\n'
                'print("| metric | value |")\n'
                'print("|---|---|")\n'
                'for name, value in summary.items():\n'
                '    print(f"| {name} | {value} |")\n'
                'print("limitation: one snapshot; 1 row has no price")\n'
                'assert summary["unique_titles"] == 3 and summary["missing_price"] == 1\n'
                'print("dataset card summary complete")'
            ),
            variant_b='add a currency column and split the mean price by currency',
            variant_c='add a rating distribution and decide whether one low-priced outlier distorts the mean',
            mistakes=[
                "Reporting only the row count and hiding missing or failed records.",
                "Presenting prices without the snapshot date or currency.",
                "Calling a scoped sample complete and implying it represents the whole site.",
            ],
            q1=(
                "Why should the dataset card report missing prices as well as the price statistics?",
                "Missing values change how much confidence the mean deserves; hiding them makes an incomplete sample look cleaner than it is.",
            ),
            homework=(
                "Write `dataset_card(rows, run_id)` that returns counts, unique titles, missing-price count, price "
                "range and a limitations line. Run it on two row sets, one complete and one with gaps, print both "
                "cards, and comment which line keeps missing data visible."
            ),
            patterns=["def ", "return", "print("],
            mapping=(
                "The capstone deliverable ends with this dataset card plus the runbook. Both are shown in the final "
                "review and stored alongside the SQLite output."
            ),
        ),
        177: dict(
            topic="Capstone build: fetch and parse",
            idea=(
                "Today the separate pieces become one crawl. The capstone does not need a new technique; it needs a "
                "clean composition. Take the scoped page list, fetch each page through the bounded fetch layer, keep "
                "the raw body, parse it with the tested parser, and collect two outputs: rows and failures. The loop "
                "must continue after a page fails, because one broken page should not discard the rest, but the "
                "failure must be named and counted. Save or retain the raw body for every failure so it can become "
                "a fixture later. End the run with a summary that states pages requested, pages fetched, pages "
                "parsed, rows emitted and failures by kind. Compare that summary with the scope: fifty pages "
                "requested and two rows emitted is not a successful run, even if no exception was raised. This is "
                "also the moment to check that the parser contract and the fetch contract still match: fetch "
                "returns text, parse consumes text, and neither knows about storage. Keep the integration function "
                "small enough to read in one screen. Today's fixture includes two good pages and one maintenance "
                "page; the crawl reports two rows and one parse failure. That output is the raw material for "
                "storage tomorrow, and the failure list is the beginning of the monitoring story."
            ),
            code=(
                'PAGES = {\n'
                '    "/page-1.html": \'<article class="product" data-url="/dune"><h3>Dune</h3><span class="price">9.99</span></article>\',\n'
                '    "/page-2.html": \'<article class="product" data-url="/emma"><h3>Emma</h3><span class="price">7.50</span></article>\',\n'
                '    "/page-3.html": "<html>maintenance</html>",\n'
                '}\n'
                '\n'
                'def fetch(path):\n'
                '    body = PAGES.get(path)\n'
                '    return {"ok": body is not None, "status": 200 if body else 404, "body": body or ""}\n'
                '\n'
                'def parse(html):\n'
                '    rows = []\n'
                '    for chunk in html.split(\'<article class="product"\')[1:]:\n'
                '        rows.append({\n'
                '            "url": chunk.split(\'data-url="\')[1].split(\'"\')[0],\n'
                '            "title": chunk.split("<h3>")[1].split("</h3>")[0],\n'
                '            "price": float(chunk.split(\'class="price">\')[1].split("<")[0]),\n'
                '        })\n'
                '    return rows\n'
                '\n'
                'def crawl(paths):\n'
                '    rows, failures = [], []\n'
                '    for path in paths:\n'
                '        result = fetch(path)\n'
                '        if not result["ok"]:\n'
                '            failures.append((path, result["status"]))\n'
                '            continue\n'
                '        try:\n'
                '            page_rows = parse(result["body"])\n'
                '            if not page_rows:\n'
                '                failures.append((path, "no rows"))\n'
                '            rows.extend(page_rows)\n'
                '        except (IndexError, ValueError):\n'
                '            failures.append((path, "parse"))\n'
                '    return rows, failures\n'
                '\n'
                'rows, failures = crawl(PAGES)\n'
                'print("rows:", len(rows), "| failures:", failures)\n'
                'for row in rows:\n'
                '    print(row)\n'
                'assert len(rows) == 2 and failures == [("/page-3.html", "no rows")]\n'
                'print("crawl summary: 3 fetched, 2 rows, 1 failure")'
            ),
            variant_b='add a page with one good card and one malformed card and report both the row and the failure',
            variant_c='skip the maintenance page but record its status instead of treating it as a parse error',
            mistakes=[
                "Letting the first failed page abort the whole crawl and lose later rows.",
                "Treating a successful fetch with zero rows as a healthy empty page.",
                "Parsing inside the fetch function and losing the raw body needed for diagnosis.",
            ],
            q1=(
                "Why does the crawl return rows and failures instead of only rows?",
                "Failures are data too; keeping them lets the run summary expose partial crawls and turns each failed page into a future fixture.",
            ),
            homework=(
                "Write `crawl(pages)` that fetches each path, parses rows, records failures with a reason, and prints "
                "a requested-fetched-parsed-rows summary. Run it on two page sets, one all good and one with "
                "maintenance markup, print both summaries, and comment which line keeps a bad page from stopping the "
                "rest."
            ),
            patterns=["def ", "for ", "append("],
            mapping=(
                "This integration is the first half of the capstone deliverable. Its row list goes to storage on "
                "day 178, and its failure list goes into the run manifest."
            ),
        ),
        178: dict(
            topic="Capstone build: store and report",
            idea=(
                "The final build step closes the loop: parsed rows become durable records, and the run produces a "
                "report that says what happened. Reuse the idempotent store from day 169 and the summary habits "
                "from day 172. Insert the batch in one transaction, count parsed, inserted and total rows, then "
                "query the table for the counts and aggregates the dataset card needs. Run the same batch twice in "
                "the exercise. The second run should insert nothing and leave the total unchanged, which proves the "
                "primary key and the insert policy are doing their job. If a later run changes a price, decide "
                "whether the table keeps the first value or the latest; do not let the choice emerge accidentally "
                "from whichever SQL variant you typed. A report is not a second program. It is a small view over the "
                "same data: total books, priced rows, average price, cheapest and most expensive, plus the run id "
                "and timestamp. Write it next to the manifest so the dataset always has a provenance line. This is "
                "the point where the pipeline earns the word finished: another person can inspect the table, read "
                "the report and reproduce both from the saved fixtures. Today's example stores three parsed rows as "
                "two unique books, reruns without change and prints the report. Tomorrow you review the whole "
                "system against the rubric."
            ),
            code=(
                'import sqlite3\n'
                '\n'
                'rows = [\n'
                '    {"url": "/dune", "title": "Dune", "price": 9.99},\n'
                '    {"url": "/emma", "title": "Emma", "price": 7.50},\n'
                '    {"url": "/dune", "title": "Dune", "price": 9.99},\n'
                ']\n'
                '\n'
                'db = sqlite3.connect(":memory:")\n'
                'db.execute("CREATE TABLE books (url TEXT PRIMARY KEY, title TEXT, price REAL)")\n'
                '\n'
                'def save(batch):\n'
                '    before = db.execute("SELECT COUNT(*) FROM books").fetchone()[0]\n'
                '    db.executemany("INSERT OR IGNORE INTO books VALUES (:url, :title, :price)", batch)\n'
                '    db.commit()\n'
                '    after = db.execute("SELECT COUNT(*) FROM books").fetchone()[0]\n'
                '    return {"parsed": len(batch), "inserted": after - before, "total": after}\n'
                '\n'
                'def report():\n'
                '    total, average, cheapest = db.execute(\n'
                '        "SELECT COUNT(*), ROUND(AVG(price), 2), MIN(price) FROM books"\n'
                '    ).fetchone()\n'
                '    return {"total": total, "avg_price": average, "cheapest": cheapest}\n'
                '\n'
                'print("run 1:", save(rows))\n'
                'print("run 2:", save(rows))\n'
                'print("report:", report())\n'
                'assert report()["total"] == 2 and report()["cheapest"] == 7.5\n'
                'print("stored dataset is idempotent and reportable")'
            ),
            variant_b='change the Dune price on the second run and compare INSERT OR IGNORE with OR REPLACE',
            variant_c='add a first_seen timestamp and report the oldest and newest record',
            mistakes=[
                "Reinserting the same batch without a key, doubling the dataset on every run.",
                "Reporting only the inserted count and never checking the resulting table.",
                "Mixing storage and HTML parsing in one function so neither can be tested alone.",
            ],
            q1=(
                "What proves that the storage step is idempotent?",
                "Running the identical batch twice leaves the table total unchanged and inserts zero new rows the second time.",
            ),
            homework=(
                "Write `store_and_report(rows, db)` that inserts a batch idempotently and returns inserted, total, "
                "average price and cheapest price. Run it twice on two batches, one with a duplicate URL, print both "
                "reports, and comment which line proves the rerun added nothing."
            ),
            patterns=["executemany(", "SELECT", "print("],
            mapping=(
                "This is the capstone's durable output and its operational report. The totals, freshness and run id "
                "are the facts quoted in the day 176 dataset card."
            ),
        ),
        179: dict(
            topic="Capstone review and next steps",
            idea=(
                "A capstone review is not a victory lap; it is an honest audit against a rubric. Correctness asks "
                "whether the rows match the schema and the fixtures. Robustness asks what happens on a 503, a "
                "maintenance page or a moved attribute. Politeness asks whether the crawl respects robots, rate and "
                "identity. Idempotency asks whether a second run duplicates data. Testability asks whether the "
                "parser can be checked offline. Documentation asks whether someone else can run the pipeline. "
                "Ethics asks whether the target, fields and retention were reviewed. Reproducibility asks whether "
                "the same fixtures and command produce the same report. Score each item yes or no, then choose one "
                "gap as the next step. A list of ten improvements is a wish; one completed improvement is progress. "
                "The most common gaps at this stage are missing run monitoring and no handling for a markup change, "
                "so those are sensible next steps. Beyond the capstone, the same pipeline can grow incremental "
                "crawling, change detection, a warehouse load or an alert when a field disappears. But the "
                "foundation is already complete: scoped fetch, tested parse, idempotent store, visible run, written "
                "review. Finish by archiving the fixtures, the runbook and the report, and write a handoff sentence "
                "that names the owner, the schedule and the known limitation."
            ),
            code=(
                'CHECKLIST = {\n'
                '    "scope documented": True,\n'
                '    "tests cover parser": True,\n'
                '    "retries bounded": True,\n'
                '    "dedup by URL": True,\n'
                '    "run summary logged": False,\n'
                '    "ethics review": True,\n'
                '    "runbook current": True,\n'
                '}\n'
                '\n'
                'def review(checklist):\n'
                '    passed = sum(checklist.values())\n'
                '    gaps = [name for name, ok in checklist.items() if not ok]\n'
                '    return passed, len(checklist), gaps\n'
                '\n'
                'passed, total, gaps = review(CHECKLIST)\n'
                'print(f"rubric: {passed}/{total} checks passed")\n'
                'for gap in gaps:\n'
                '    print("next step:", gap)\n'
                'print("handoff: data team, daily 02:00 UTC, prices are one snapshot")\n'
                'assert passed == 6 and gaps == ["run summary logged"]\n'
                'print("choose one gap, close it, then schedule the next review")'
            ),
            variant_b='mark the runbook stale and show which gap becomes the highest-priority next step',
            variant_c='add an incremental-crawl item and decide whether it belongs in the capstone or the roadmap',
            mistakes=[
                "Scoring the rubric from memory instead of checking each artifact.",
                "Listing every possible improvement and finishing none of them.",
                "Calling the project done without a handoff owner, schedule and known limitation.",
            ],
            q1=(
                "Why should the review choose one next step instead of listing every possible improvement?",
                "A ranked list of ten is a wish; one closed gap changes the pipeline, and the next review can pick the following item with evidence.",
            ),
            homework=(
                "Write `review_capstone(checklist)` that returns passed count, gaps and one recommended next step "
                "using a documented priority order. Run it on two checklists, one nearly complete and one missing "
                "tests, print both reviews, and comment which line prevents the recommendation from becoming a wish "
                "list."
            ),
            patterns=["def ", "return", "print("],
            mapping=(
                "The review closes the capstone with a scored rubric, one concrete next step and a handoff line. "
                "The archived fixtures, runbook and report are the evidence behind the score."
            ),
        ),
    },
)
