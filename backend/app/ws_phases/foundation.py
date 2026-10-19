"""Web Scraping foundations, days 9-14: the vocabulary the domain phases build on.

Every example here runs offline on in-memory strings, so the applier can execute
it without a network. The domain phases that follow keep the same discipline:
the idea is explained in plain language, the code demonstrates it on a fixture,
and the learner adapts it to their own values.
"""

FOUNDATION = {
    9: dict(
        topic="A scraped row is a dictionary",
        idea=(
            "A scraper's job is to turn an unpredictable page into a predictable record. The page gives you "
            "position, nesting and markup; the record gives you names. A dictionary is the smallest honest "
            "version of that record: {'title': 'Dune', 'price': 9.99, 'in_stock': True} says what each value "
            "means, survives reordering, and makes a typo fail immediately instead of silently reading the "
            "wrong column. That matters more in scraping than in most programming because the source changes "
            "without warning. A site can add a badge, move a price into a nested span, or swap two columns; "
            "positional code breaks silently, while name-based code either keeps working or raises a KeyError "
            "at the exact line that needs attention. Dictionaries also give you a natural place to record "
            "provenance: the URL the row came from, the time it was fetched, and the selector that produced "
            "it. Those fields are not decoration. When a dataset looks wrong three weeks later, provenance is "
            "the difference between a five-minute fix and an afternoon of guessing. Today you build one row by "
            "hand from fields a parser would hand you, then check that every row has the same keys. That key "
            "check is the first data-quality gate in every pipeline you will write: a record missing a key is "
            "not a small formatting issue, it is a row whose meaning is incomplete."
        ),
        code=(
            'fields = ["Dune", "9.99", "yes"]\n'
            'row = {"title": fields[0], "price": float(fields[1]), "in_stock": fields[2] == "yes"}\n'
            '\n'
            'print("title:", row["title"])\n'
            'print("price:", row["price"], type(row["price"]).__name__)\n'
            'print("keys:", sorted(row))\n'
            'required = {"title", "price", "in_stock"}\n'
            'assert set(row) == required, "incomplete record"\n'
            'print("record complete")'
        ),
        variant_b='fields = ["Foundation", "12.50", "no"] (same code, different values)',
        variant_c='drop the in_stock key before the assertion and explain the failure',
        mistakes=[
            "Keeping price as the string '9.99', so later arithmetic silently concatenates text.",
            "Using positional indexes throughout, so adding a column shifts every value.",
            "Assuming every row has every key instead of asserting the schema.",
        ],
        q1=(
            "Why is a dictionary safer than a positional list for a scraped row?",
            "Names survive reordering and markup changes; positions break silently when the source adds or moves a field.",
        ),
        homework=(
            "Write `book_row(parts)` that turns a three-item list (title, price text, stock text) into a typed "
            "dictionary and asserts the required keys. Run it on two different lists, print both rows, and "
            "comment which line converts the price from text to a number."
        ),
        patterns=["{", "assert", "print("],
        mapping=(
            "Every record this track emits is a dictionary before it becomes CSV, JSON or a SQLite row. "
            "Libraries such as BeautifulSoup hand you strings; the dictionary is where you decide their types."
        ),
    ),
    10: dict(
        topic="One function transforms one page",
        idea=(
            "The most useful habit in scraping is to make one function responsible for one transformation. A "
            "function like `parse_price(text) -> float` can be tested with a dozen inputs, reused on every "
            "page, and replaced when the site changes, all without touching the code that fetches pages or "
            "the code that stores rows. This separation is what lets a scraper survive. When a site changes "
            "its currency format, you edit one function and rerun its tests; when it changes its HTML, you "
            "edit the function that locates the price, not the storage layer. Functions also force you to name "
            "the contract: what goes in, what comes out, and what happens on bad input. A parser that returns "
            "None for 'not found' is honest and composable; one that raises deep inside a loop takes down a "
            "whole crawl for one malformed page. Today the transform is deliberately small: clean a price "
            "string. The point is not the arithmetic. The point is that the function is pure, has one job, and "
            "can be checked without a network. That property is what makes a pipeline testable, and testable "
            "pipelines are the only ones you can safely run on a schedule. Notice also that the function "
            "returns a value rather than printing it. Printing is the caller's job; returning makes the "
            "function usable in the next step, in an assertion, or in a test fixture."
        ),
        code=(
            'def parse_price(text):\n'
            '    cleaned = text.strip().replace("$", "").replace(",", "")\n'
            '    return float(cleaned) if cleaned else None\n'
            '\n'
            'samples = ["$9.99", " 1,250.00 ", "", "free"]\n'
            'for sample in samples:\n'
            '    try:\n'
            '        value = parse_price(sample)\n'
            '        print(repr(sample), "->", value)\n'
            '    except ValueError:\n'
            '        print(repr(sample), "-> invalid price")\n'
            '\n'
            'assert parse_price("$9.99") == 9.99\n'
            'assert parse_price("") is None\n'
            'print("parser contract holds")'
        ),
        variant_b='allow a trailing currency code, e.g. "9.99 USD", by stripping it first',
        variant_c='make an unparseable value return None instead of raising, and say which contract is safer',
        mistakes=[
            "Fetching inside the parser, so the function cannot be tested offline.",
            "Printing the result instead of returning it, which makes reuse impossible.",
            "Letting one bad row raise without deciding whether it should skip or fail the run.",
        ],
        q1=(
            "Why should the price parser not fetch the page itself?",
            "Keeping fetch and parse separate lets each be tested and changed independently; the parser receives text and returns a value.",
        ),
        homework=(
            "Write `parse_rating(text)` that converts strings like '4.5 out of 5' or '3,9/5' into a float and "
            "returns None for missing text. Run it on at least four samples, print each result, and comment "
            "which line separates cleaning from conversion."
        ),
        patterns=["def ", "return", "print("],
        mapping=(
            "The same shape appears later as `parse_card`, `parse_table_row` and `parse_json_item`: one pure "
            "function per page fragment, tested on saved fixtures before it ever sees the live site."
        ),
    ),
    11: dict(
        topic="Loops turn pages into a table",
        idea=(
            "A single page is an anecdote; a list of records is data. The loop is the bridge. The pattern is "
            "always the same: start with an empty list, transform each page into zero or more rows, extend the "
            "list, then report how many rows came from how many pages. Writing it this way gives you an "
            "immediate quality signal. If you fetched ten pages and produced zero rows, the parser is wrong. "
            "If you produced ten times more rows than expected, a selector is matching nested elements twice. "
            "The loop also makes failure visible in the right place: wrap the transform for one page, record "
            "the error next to that page, and continue. One broken page should not erase nine good ones, but "
            "it must not disappear either. In real scrapers this accumulates into a run summary — pages "
            "attempted, pages parsed, rows emitted, pages failed — and that summary is the first thing you "
            "check when a dataset looks short. Today's fixture pages are strings, so nothing can fail for "
            "network reasons; the only variable is your parsing logic. That is deliberate. Learn the counting "
            "habit while the input is calm, so it is automatic when the input is not. Keep the output flat: a "
            "list of dictionaries is easy to filter, deduplicate and write to CSV. Nested lists should be "
            "flattened at the boundary, not carried deeper into the pipeline."
        ),
        code=(
            'pages = [\n'
            '    "<h2>Dune</h2><p>$9.99</p>",\n'
            '    "<h2>Foundation</h2><p>$12.50</p>",\n'
            '    "<h2>No Price</h2><p>sold out</p>",\n'
            ']\n'
            '\n'
            'def rows_from_page(html):\n'
            '    title = html.split("<h2>")[1].split("</h2>")[0]\n'
            '    price_text = html.split("<p>")[1].split("</p>")[0]\n'
            '    if not price_text.startswith("$"):\n'
            '        return []\n'
            '    return [{"title": title, "price": float(price_text[1:])}]\n'
            '\n'
            'rows = []\n'
            'for page in pages:\n'
            '    rows.extend(rows_from_page(page))\n'
            '\n'
            'print("pages:", len(pages), "| rows:", len(rows))\n'
            'for row in rows:\n'
            '    print(row["title"], row["price"])\n'
            'assert len(rows) == 2\n'
            'print("row count matches the two priced pages")'
        ),
        variant_b='add a page with an empty title and decide whether it is a row or an error',
        variant_c='collect failures in a separate list instead of silently returning []',
        mistakes=[
            "Returning a dictionary instead of a list, so extend iterates its keys.",
            "Letting one malformed page abort the loop and discard the good rows.",
            "Forgetting to count pages and rows, so a silent zero-row run looks like success.",
        ],
        q1=(
            "Why print pages attempted and rows emitted after the loop?",
            "The ratio exposes parser failures and selector double-matches immediately, before the bad data reaches storage.",
        ),
        homework=(
            "Write `scrape_pages(pages)` that loops over HTML strings, extracts a title and optional price, "
            "returns a flat list of dictionaries, and prints pages attempted versus rows emitted. Run it on at "
            "least three fixtures, print the summary, and comment which line keeps one bad page from stopping "
            "the rest."
        ),
        patterns=["for ", "extend(", "print("],
        mapping=(
            "This is the inner loop of every later crawler: a page source yields rows, a run summary counts "
            "both sides, and failures are recorded rather than swallowed."
        ),
    ),
    12: dict(
        topic="Errors are data, not surprises",
        idea=(
            "Networks fail. Pages disappear, servers time out, credentials expire, and markup changes without "
            "notice. A scraper that treats every failure as an exception is a scraper that stops on the first "
            "bad afternoon. The professional habit is to classify failures: a 404 means the resource is gone "
            "and retrying is pointless; a 429 means you are going too fast and should wait; a 500 may be "
            "temporary; a parse error means the page arrived but your selector is wrong. Those are different "
            "decisions, so they deserve different outcomes. Returning a result object such as {'ok': False, "
            "'kind': 'timeout', 'url': ...} keeps the run alive while preserving the diagnosis. It also makes "
            "the run summary meaningful: ten timeouts suggest a network or concurrency problem, ten parse "
            "errors suggest a markup change, and ten 403s suggest a policy problem. None of those should be "
            "retried the same way. Today you model this without a real network, so you can focus on the "
            "decision table rather than on socket behaviour. Write the classifier, feed it status codes and "
            "error names, and print the action each one should trigger. When you reach the fetching phases, "
            "the same table becomes the retry policy. The rule to internalise now: never let an error vanish "
            "because the row count looked plausible. A missing row and a missing key are both data-quality "
            "events, and both need a name before they can be fixed."
        ),
        code=(
            'def classify(outcome):\n'
            '    if outcome["ok"]:\n'
            '        return "store"\n'
            '    code = outcome.get("status")\n'
            '    if code == 404:\n'
            '        return "skip permanently"\n'
            '    if code == 429:\n'
            '        return "wait and retry"\n'
            '    if code and 500 <= code < 600:\n'
            '        return "retry with backoff"\n'
            '    if outcome.get("parse_error"):\n'
            '        return "fix selector"\n'
            '    return "report"\n'
            '\n'
            'outcomes = [\n'
            '    {"ok": True, "status": 200},\n'
            '    {"ok": False, "status": 404},\n'
            '    {"ok": False, "status": 429},\n'
            '    {"ok": False, "status": 503},\n'
            '    {"ok": True, "status": 200, "parse_error": "missing title"},\n'
            ']\n'
            'for outcome in outcomes:\n'
            '    print(outcome, "->", classify(outcome))\n'
            'assert classify(outcomes[1]) == "skip permanently"\n'
            'print("error policy is explicit")'
        ),
        variant_b='add a 403 case and decide whether it is retryable or a policy stop',
        variant_c='add a timeout with no status code and route it to retry with backoff',
        mistakes=[
            "Retrying every failure, which hammers servers and hides permanent problems.",
            "Catching a broad exception and continuing without recording what failed.",
            "Treating a parse error as a network error, so the retry loop never fixes anything.",
        ],
        q1=(
            "Why should a 404 and a 500 trigger different actions?",
            "A 404 is permanent and retrying wastes requests; a 500 may be temporary, so a bounded retry is reasonable.",
        ),
        homework=(
            "Write `decide(outcome)` that returns one of store, skip, retry or fix for success, 404, 429, 5xx "
            "and parse errors. Feed it at least five outcomes, print the decision for each, and comment which "
            "line prevents a permanent failure from being retried forever."
        ),
        patterns=["def ", "if ", "return"],
        mapping=(
            "Later, the fetch layer turns this table into real timeout, retry and backoff settings; the parser "
            "layer reports parse failures separately so a markup change is never mistaken for a network blip."
        ),
    ),
    13: dict(
        topic="Bytes, text and file boundaries",
        idea=(
            "A web page is bytes on the wire, not text. The bytes have to be decoded with the right character "
            "encoding before Python can treat them as a string, and getting that step wrong produces the "
            "classic mojibake: 'Ã©' where 'é' belonged. Scrapers meet this constantly because sites mix UTF-8, "
            "declared charsets and occasional legacy encodings. The rule is simple: keep bytes at the "
            "boundary, decode once with an explicit encoding, and fail loudly when the declared encoding is "
            "wrong rather than silently replacing characters. The same boundary thinking applies to files. "
            "When you save raw pages for debugging, save bytes or decode deliberately; when you write CSV, let "
            "the csv module handle quoting rather than joining strings with commas. A surprising number of "
            "scraping bugs are really boundary bugs: a price with a non-breaking space, a name with a curly "
            "quote, a CSV field containing a comma. Today's example works entirely in memory, so you can watch "
            "the difference between the byte length and the character length, and see why len() gives a "
            "different answer after decoding. That difference is the reason you never slice bytes as if they "
            "were characters. It is also why a defensive pipeline normalises text early, once, at the edge, "
            "instead of letting three downstream systems each guess. Decode at the edge, normalise once, store "
            "a clean string, and keep the raw bytes only when debugging provenance truly requires them."
        ),
        code=(
            'raw = "Café — 9,99 €".encode("utf-8")\n'
            'print("bytes:", len(raw), "| type:", type(raw).__name__)\n'
            '\n'
            'text = raw.decode("utf-8")\n'
            'print("text:", len(text), "| value:", text)\n'
            '\n'
            'cleaned = " ".join(text.replace("—", "-").split())\n'
            'print("normalised:", cleaned)\n'
            '\n'
            'try:\n'
            '    raw.decode("ascii")\n'
            'except UnicodeDecodeError as error:\n'
            '    print("strict decode refused:", error.reason)\n'
            '\n'
            'assert len(raw) != len(text)\n'
            'assert cleaned == "Café - 9,99 €"\n'
            'print("decode once at the boundary")'
        ),
        variant_b='decode the same bytes as latin-1 and compare the printed text',
        variant_c='normalise a string containing a non-breaking space and a newline',
        mistakes=[
            "Calling len() on bytes and assuming it equals the visible character count.",
            "Decoding with errors='ignore', which deletes evidence of an encoding problem.",
            "Joining CSV fields with commas by hand instead of using the csv module.",
        ],
        q1=(
            "Why does len(raw) differ from len(text) here?",
            "UTF-8 uses multiple bytes for accented and symbol characters, so byte length counts encoding units, not characters.",
        ),
        homework=(
            "Write `decode_page(raw, encoding)` that decodes bytes strictly, normalises whitespace, and raises "
            "a clear error on failure. Run it on UTF-8 and latin-1 fixtures, print the resulting text and "
            "lengths, and comment which line keeps decoding at the edge of the pipeline."
        ),
        patterns=["encode(", "decode(", "print("],
        mapping=(
            "HTTP responses arrive as bytes; the fetch layer will read them, honour the declared charset, and "
            "hand plain text to the parser. Storage then writes UTF-8 consistently."
        ),
    ),
    14: dict(
        topic="A tiny scraper, end to end",
        idea=(
            "Today you assemble the pieces you have met: a page, a parser, a loop, a record and a quality "
            "check. The target is deliberately modest — extract links from an in-memory HTML page, resolve "
            "them against a base URL, keep unique same-site links, and print a small table. Doing the whole "
            "shape once is worth more than perfecting any single stage, because it shows where the seams are. "
            "The parser produces raw values; the normaliser resolves relative URLs; the collector deduplicates; "
            "the report counts what came in and what survived. Each stage has one job, and each can be tested "
            "on its own. This is also your first encounter with a subtle scraping rule: the same destination "
            "can be written many ways (/about, /about/, ../about, an absolute URL, a URL with a tracking "
            "parameter). Deduplication by raw string is not enough; normalisation has to happen first. Keep "
            "the example offline and stdlib-only. The HTML parser from html.parser is verbose, which is "
            "instructive: it shows that parsing is event-driven underneath the friendly libraries you will use "
            "later. When BeautifulSoup or lxml arrives, it will be a convenience over this same model, not "
            "magic. End the day by writing down the pipeline contract in one sentence per stage: fetch gives "
            "text, parse gives candidates, normalise gives canonical values, store gives unique records. If "
            "you can say that sentence without looking, the foundation is installed."
        ),
        code=(
            'from html.parser import HTMLParser\n'
            'from urllib.parse import urljoin, urlsplit, urlunsplit\n'
            '\n'
            'class Links(HTMLParser):\n'
            '    def __init__(self):\n'
            '        super().__init__()\n'
            '        self.hrefs = []\n'
            '    def handle_starttag(self, tag, attrs):\n'
            '        if tag == "a":\n'
            '            for name, value in attrs:\n'
            '                if name == "href" and value:\n'
            '                    self.hrefs.append(value)\n'
            '\n'
            'def canonical(url, base):\n'
            '    parts = urlsplit(urljoin(base, url))\n'
            '    return urlunsplit((parts.scheme, parts.netloc, parts.path.rstrip("/") or "/", "", ""))\n'
            '\n'
            'page = """<a href="/about">About</a><a href="about/">About again</a>\n'
            '<a href="https://shop.example/books?ref=home">Books</a><a href="/about">About</a>"""\n'
            'parser = Links()\n'
            'parser.feed(page)\n'
            '\n'
            'base = "https://shop.example/catalog/"\n'
            'unique = sorted({canonical(href, base) for href in parser.hrefs})\n'
            'print("raw links:", len(parser.hrefs), "| unique:", len(unique))\n'
            'for link in unique:\n'
            '    print(" ", link)\n'
            'assert all(link.startswith("https://shop.example") for link in unique)\n'
            'print("small scraper complete")'
        ),
        variant_b='keep only links whose path starts with /books and explain the filter line',
        variant_c='preserve query parameters and see how many new unique links appear',
        mistakes=[
            "Deduplicating before resolving relative URLs, so /about and about/ look different.",
            "Following every link including external domains by accident.",
            "Treating the parser as the place to clean data instead of normalising in a separate stage.",
        ],
        q1=(
            "Why must links be normalised before deduplication?",
            "The same destination has many spellings; comparing raw strings keeps duplicates and inflates crawl counts.",
        ),
        homework=(
            "Write `extract_links(html, base)` that parses anchors, resolves them with urljoin, strips fragments "
            "and trailing slashes, and returns sorted unique same-site URLs. Run it on two fixtures, print the "
            "before/after counts, and comment which line prevents duplicate crawl targets."
        ),
        patterns=["class ", "def ", "print("],
        mapping=(
            "This fetch → parse → normalise → deduplicate shape is the skeleton of the remaining 105 days; "
            "each phase deepens exactly one stage without changing the overall contract."
        ),
    ),
}
