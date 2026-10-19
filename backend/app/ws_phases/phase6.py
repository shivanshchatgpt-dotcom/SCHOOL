"""Web Scraping phase 6, days 150-164: pipelines and operations.

Each example runs offline on in-memory fixtures with the standard library only.
The phase treats a scraper as a service with stages, schedules, budgets and an
owner, not as a one-off script.
"""

PHASE = (
    "Pipelines and Operations",
    "Turn a working scraper into a scheduled, observable, deployable pipeline that survives real operations.",
    {
        150: dict(
            topic="Spider design",
            idea=(
                "A spider is a contract for one site, not a script that happens to work on today's markup. The "
                "contract has a name, one or more entry points, a set of allowed domains, and a parse method that "
                "turns a page into records or into further requests. Writing it as a class makes those decisions "
                "explicit and keeps them in one place: the scheduler can import the spider, the test suite can call "
                "parse on a saved page, and a second site gets its own spider instead of a pile of conditionals. "
                "The important boundary is between crawl policy and extraction. Which pages are allowed, how deep "
                "to follow, and which links are worth queueing belong to the spider's policy; pulling a title out "
                "of a heading belongs to a pure parser that the spider calls. When those two are mixed, every "
                "selector change risks changing crawl behaviour as well. Keep parse free of network calls so it can "
                "run against fixtures, and let the engine own fetching, retries and concurrency. A good spider is "
                "small enough to read in one sitting and boring enough that its name tells you exactly which site "
                "it owns. Today you build that shape on an in-memory page map and check that it emits the rows you "
                "expect without any download."
            ),
            code=(
                'class Spider:\n'
                '    name = "catalog"\n'
                '    start_urls = ["https://shop.example/catalog"]\n'
                '    allowed = ("shop.example",)\n'
                '\n'
                '    def parse(self, url, html):\n'
                '        if "<li>" not in html:\n'
                '            return []\n'
                '        return [{"url": url, "title": part.split("</li>")[0]}\n'
                '                for part in html.split("<li>")[1:]]\n'
                '\n'
                'pages = {\n'
                '    "https://shop.example/catalog": "<ul><li>Dune</li><li>Foundation</li></ul>",\n'
                '    "https://shop.example/about": "<p>About the shop</p>",\n'
                '}\n'
                'spider = Spider()\n'
                'rows = []\n'
                'for url in spider.start_urls:\n'
                '    rows.extend(spider.parse(url, pages[url]))\n'
                '\n'
                'print("spider:", spider.name, "| rows:", len(rows))\n'
                'for row in rows:\n'
                '    print(row["title"])\n'
                'assert len(rows) == 2\n'
                'print("spider contract holds")\n'
            ),
            variant_b='add "https://shop.example/deals" to start_urls with a two-item page and compare the row count',
            variant_c='make parse return one request for a "next" page when the fixture contains a nexthref',
            mistakes=[
                "Putting the fetch loop inside parse, so the spider cannot be tested without a network.",
                "Letting one spider handle several unrelated sites through conditionals on the domain.",
                "Returning follow-up links without checking them against the allowed domains.",
            ],
            q1=(
                "Why should a spider's parse method avoid making network calls itself?",
                "A pure parse can be tested against saved fixtures and reused by any engine; the engine owns fetching, retries and concurrency.",
            ),
            homework=(
                "Write `CatalogSpider.parse(url, html)` that returns one dictionary per list item and no rows for "
                "a page without a list. Run it on a catalog fixture and an about fixture, print both row lists, and "
                "comment which line keeps crawl policy separate from extraction."
            ),
            patterns=["class ", "def parse", "print("],
            mapping=(
                "Scrapy spiders follow exactly this shape: name, start_urls, allowed_domains and parse. The engine "
                "supplies the scheduler and downloader, so the spider stays a small description of one site."
            ),
        ),
        151: dict(
            topic="Item pipelines",
            idea=(
                "Between a parsed item and a stored row there is usually a chain of small corrections: trim "
                "whitespace, convert price text to a number, reject records missing a required field, drop "
                "duplicates, attach a fetch timestamp. A pipeline makes that chain explicit. Each stage receives one "
                "item, returns either a cleaned item or a drop signal, and does not know about the stages after it. "
                "That narrow contract is what makes the chain safe to reorder, test and extend. Order matters more "
                "than it looks: cleaning before validation means validation sees normalised text, while "
                "deduplication before canonicalisation keeps two spellings of the same record. Counters at every "
                "stage turn a mysterious short dataset into a readable story about where rows disappeared. The other "
                "design rule is that storage should stay dumb. If the database layer is deciding what a valid price "
                "is, that rule now lives in two places and will drift. Put the decision in a pipeline stage and let "
                "the writer receive rows that are already acceptable. Today you run four stages over three items "
                "and print the surviving count, then remove a stage and watch the numbers change. The pipeline is "
                "just functions over a list, which is enough to learn the contract before a framework supplies the "
                "same idea under a settings key."
            ),
            code=(
                'items = [\n'
                '    {"title": "  Dune ", "price": "$9.99", "sku": "A1"},\n'
                '    {"title": "Dune", "price": "$9.99", "sku": "A1"},\n'
                '    {"title": "Foundation", "price": "free", "sku": "B2"},\n'
                ']\n'
                '\n'
                'def clean(item):\n'
                '    item = dict(item)\n'
                '    item["title"] = " ".join(item["title"].split())\n'
                '    return item\n'
                '\n'
                'def validate(item):\n'
                '    try:\n'
                '        item["price"] = float(item["price"].lstrip("$").replace(",", ""))\n'
                '    except ValueError:\n'
                '        return None\n'
                '    return item\n'
                '\n'
                'def dedupe(items):\n'
                '    seen, out = set(), []\n'
                '    for item in items:\n'
                '        if item["sku"] in seen:\n'
                '            continue\n'
                '        seen.add(item["sku"])\n'
                '        out.append(item)\n'
                '    return out\n'
                '\n'
                'cleaned = [clean(item) for item in items]\n'
                'valid = [row for row in (validate(item) for item in cleaned) if row]\n'
                'final = dedupe(valid)\n'
                'print("in:", len(items), "| valid:", len(valid), "| unique:", len(final))\n'
                'for item in final:\n'
                '    print(item["sku"], item["title"], item["price"])\n'
                'assert len(final) == 1\n'
                'print("pipeline order: clean -> validate -> dedupe")\n'
            ),
            variant_b='change the duplicate SKU to B2 and see which record survives the dedupe stage',
            variant_c='return a tuple (item, None) or (None, reason) from validate and count drop reasons',
            mistakes=[
                "Validating before cleaning, so padded or currency-decorated text fails for the wrong reason.",
                "Raising on a bad item instead of dropping it with a reason the run summary can count.",
                "Letting the storage layer re-validate, which duplicates the rule and slowly drifts.",
            ],
            q1=(
                "Why should cleaning happen before validation in an item pipeline?",
                "Validation should judge normalised values; otherwise a stray space or currency symbol produces a false failure.",
            ),
            homework=(
                "Write `run_pipeline(items, stages)` that feeds each item through stages in order, drops items when "
                "a stage returns None, and prints per-stage counts. Run it on a clean batch and a batch containing "
                "one invalid price, then comment which stage removed the bad row."
            ),
            patterns=["def ", "return", "print("],
            mapping=(
                "Scrapy's ITEM_PIPELINES setting is this chain: every enabled class sees each item in order and can "
                "return it or drop it. Counters per stage are what make a short output explainable."
            ),
        ),
        152: dict(
            topic="Middlewares",
            idea=(
                "Some concerns apply to every request rather than to one page: attaching a user agent, rotating a "
                "proxy, adding a session cookie, waiting for a per-domain rate limit, retrying a temporary failure. "
                "Copying that code into every spider guarantees it will be forgotten in the next spider. Middleware "
                "is the layer for cross-cutting behaviour. Picture an onion around the downloader: request "
                "middleware runs from the outside inward, the downloader fetches, and response middleware runs from "
                "the inside outward. That ordering is the whole mental model, and getting it wrong produces bugs "
                "that look impossible, such as a retry middleware that never sees the 429 because a response "
                "middleware already converted it. Middleware should change transport concerns only. Parsing, "
                "validation and storage rules belong elsewhere; a middleware that knows about book titles has "
                "quietly become a spider with worse visibility. Keep each layer small and log decisions at debug "
                "level so you can reconstruct a single request's journey. Test the chain with fake request and "
                "response dictionaries, as today's example does, and assert the order in the trace. When the chain "
                "grows long, the trace is your evidence that every layer ran exactly once. Document the order "
                "next to the chain, because one layer inserted in the wrong place is enough to invalidate it."
            ),
            code=(
                'trace = []\n'
                '\n'
                'def user_agent(request):\n'
                '    trace.append("ua:request")\n'
                '    headers = dict(request.get("headers", {}))\n'
                '    headers["User-Agent"] = "catalog/1.0"\n'
                '    return dict(request, headers=headers)\n'
                '\n'
                'def retry(request):\n'
                '    trace.append("retry:request")\n'
                '    return request\n'
                '\n'
                'def block_external(response):\n'
                '    trace.append("block:response")\n'
                '    if "blocked" in response.get("body", ""):\n'
                '        return dict(response, status=403)\n'
                '    return response\n'
                '\n'
                'def record(response):\n'
                '    trace.append("record:response")\n'
                '    return response\n'
                '\n'
                'request = {"url": "https://shop.example/1"}\n'
                'response = {"status": 200, "body": "ok"}\n'
                'for middleware in (user_agent, retry):\n'
                '    request = middleware(request)\n'
                'for middleware in reversed((block_external, record)):\n'
                '    response = middleware(response)\n'
                '\n'
                'print("trace:", " -> ".join(trace))\n'
                'print("user-agent:", request["headers"]["User-Agent"], "| status:", response["status"])\n'
                'assert len(trace) == 4\n'
                'print("request runs top-down, response bottom-up")\n'
            ),
            variant_b='add a proxy middleware before user_agent and check that it appears first in the request trace',
            variant_c='make retry return a new request only when the previous response was 429',
            mistakes=[
                "Putting HTML parsing in a middleware, where it cannot see the spider's item schema.",
                "Reversing the response chain incorrectly, so an outer layer never observes the final status.",
                "Swallowing an exception in middleware and returning a fake success response.",
            ],
            q1=(
                "Why do response middlewares run in the reverse order of request middlewares?",
                "They form an onion around the downloader: the outermost request layer must be the last to inspect the response on the way back.",
            ),
            homework=(
                "Write `run_chain(request, response, request_layers, response_layers)` that applies request layers "
                "top-down and response layers bottom-up and returns the trace. Run it with two layers and with "
                "three, print both traces, and comment which loop creates the reversal."
            ),
            patterns=["for ", "reversed(", "print("],
            mapping=(
                "Scrapy's downloader middlewares wrap every request in exactly this order and are configured per "
                "project. Proxies, retry policies and rate limits live there so spiders stay about content."
            ),
        ),
        153: dict(
            topic="Scheduling recurring runs",
            idea=(
                "A scraper that runs once produces a file; a scraper that runs nightly produces a dataset. The "
                "difference is scheduling, and scheduling is harder than a line in crontab. The first question is "
                "cadence: how fresh must the data be, and what does a missed window mean for the consumer? The "
                "second is overlap: cron will happily start a second copy while the first is still crawling, so the "
                "job needs a lock, a lease or a heartbeat that says it is alive. The third is catch-up policy. If "
                "the process was down for six hours, replaying every missed interval may hammer the site, while "
                "running once may be enough. Decide deliberately and record the decision. Schedule in a fixed "
                "timezone, preferably UTC, and keep the run itself idempotent so a retry after a partial failure "
                "does not duplicate rows. Add jitter when many instances share a schedule, and separate the "
                "trigger from the work so a manual backfill uses the same entry point as the timer. Today you "
                "compute the next run times from an anchor and decide whether the current time is due. That small "
                "amount of arithmetic is the part cron cannot do for you: knowing whether the job that should be "
                "running is actually running."
            ),
            code=(
                'from datetime import datetime, timedelta\n'
                '\n'
                'def due(last_run, now, interval_minutes):\n'
                '    return now - last_run >= timedelta(minutes=interval_minutes)\n'
                '\n'
                'def next_after(anchor, now, interval_minutes):\n'
                '    step = timedelta(minutes=interval_minutes)\n'
                '    candidate = anchor + step\n'
                '    while candidate <= now:\n'
                '        candidate += step\n'
                '    return candidate\n'
                '\n'
                'anchor = datetime(2026, 10, 19, 2, 0)\n'
                'now = datetime(2026, 10, 19, 8, 30)\n'
                'print("due now:", due(anchor, now, 360))\n'
                'print("last run:", anchor.isoformat(timespec="minutes"))\n'
                'cursor = now\n'
                'for _ in range(3):\n'
                '    cursor = next_after(anchor, cursor, 360)\n'
                '    print("next:", cursor.isoformat(timespec="minutes"))\n'
                'assert due(anchor, now, 360)\n'
                'print("missed windows are not replayed blindly")\n'
            ),
            variant_b='interval_minutes=45 (what happens to the number of runs per day?)',
            variant_c='anchor at 02:10 and now at 08:30, then explain which window shifted',
            mistakes=[
                "Starting a second run while the first is still active, so both write the same output.",
                "Replaying every missed interval after an outage and overwhelming the target site.",
                "Scheduling in local time without recording the timezone, so daylight saving moves the run.",
            ],
            q1=(
                "Why does a recurring scraper need a lock or heartbeat in addition to a cron entry?",
                "Cron starts jobs on time but does not know whether the previous run finished, so overlap can duplicate writes or overload the site.",
            ),
            homework=(
                "Write `next_runs(anchor, now, interval_minutes, count)` that returns the next run datetimes after "
                "now. Run it on a six-hour interval and a forty-five minute interval, print both lists, and comment "
                "how the interval changes the daily run count."
            ),
            patterns=["timedelta", "def ", "print("],
            mapping=(
                "Cron, systemd timers or a Kubernetes CronJob trigger the process; a lock table, Redis lease or "
                "single-replica deployment prevents overlap. The scheduler owns timing; the scraper owns idempotency."
            ),
        ),
        154: dict(
            topic="Monitoring a scraper",
            idea=(
                "A crashing scraper announces itself; a scraper that returns zero rows quietly poisons everything "
                "downstream. Monitoring exists to notice the quiet failures. The useful signals are simple and "
                "per-run: pages attempted, pages parsed, rows emitted, errors by kind, duration, and the age of the "
                "newest record. Compare those against a recent baseline rather than a number invented last year. A "
                "zero-row run on a site that usually yields thousands is an incident even though every process "
                "exited successfully. A row count that halves for three runs is a selector drifting. A freshness "
                "alert catches the case where the scheduler stopped firing and no run exists to inspect. Alerts "
                "should be few, actionable and owned; a dashboard nobody reads is not monitoring. Pair the metrics "
                "with a dead man's switch: the run pings a health endpoint on success, and silence itself raises the "
                "alarm. Write each threshold and its owner beside the alert, so the person paged can tune a noisy "
                "rule instead of muting it. Today you summarise three runs, flag the empty one and compute an error "
                "rate. The point is to practise reading a run history the way an operator does, asking what changed "
                "and whether the data is still arriving, not merely whether the last process crashed."
            ),
            code=(
                'runs = [\n'
                '    {"run": "r1", "pages": 20, "rows": 18, "errors": 2, "seconds": 14},\n'
                '    {"run": "r2", "pages": 20, "rows": 0, "errors": 0, "seconds": 9},\n'
                '    {"run": "r3", "pages": 20, "rows": 20, "errors": 0, "seconds": 11},\n'
                ']\n'
                '\n'
                'def summarize(runs):\n'
                '    pages = sum(run["pages"] for run in runs)\n'
                '    rows = [run["rows"] for run in runs]\n'
                '    return {\n'
                '        "runs": len(runs),\n'
                '        "avg_rows": round(sum(rows) / len(rows), 1),\n'
                '        "zero_row_runs": [run["run"] for run in runs if run["rows"] == 0],\n'
                '        "error_rate": round(sum(run["errors"] for run in runs) / pages, 3),\n'
                '    }\n'
                '\n'
                'summary = summarize(runs)\n'
                'print(summary)\n'
                'alerts = []\n'
                'if summary["zero_row_runs"]:\n'
                '    alerts.append("zero rows in " + ",".join(summary["zero_row_runs"]))\n'
                'if summary["error_rate"] > 0.05:\n'
                '    alerts.append("error rate above 5 percent")\n'
                'print("alerts:", alerts if alerts else ["none"])\n'
                'assert summary["zero_row_runs"] == ["r2"]\n'
                'print("absence of data is the loudest signal")\n'
            ),
            variant_b='make r2 return 3 rows instead of 0 and decide whether any alert still fires',
            variant_c='add a run with 12 errors on 20 pages and read the error rate again',
            mistakes=[
                "Alerting only on process exit codes, which treats a zero-row run as healthy.",
                "Setting thresholds with no baseline, so normal seasonal variation pages someone at night.",
                "Monitoring row counts without monitoring freshness, so a stopped scheduler looks calm.",
            ],
            q1=(
                "Why is a zero-row run more dangerous than a visible crash?",
                "A crash is noticed immediately, while an empty run can look successful and silently starve every downstream consumer.",
            ),
            homework=(
                "Write `health(runs)` that returns run count, average rows, zero-row run ids and error rate. Feed it "
                "one healthy history and one with an empty run, print both summaries, and comment which value would "
                "have raised an alert first."
            ),
            patterns=["def ", "return", "print("],
            mapping=(
                "Production scrapers export these counters to Prometheus, CloudWatch or a database table and alert "
                "on zero rows, error spikes and stale data. A daily heartbeat is often the simplest dead man's switch."
            ),
        ),
        155: dict(
            topic="Logging and observability",
            idea=(
                "When a run goes wrong at 3am, the log is the only witness. A good scraper log is a sequence of "
                "structured events, not a stream of sentences. Each event should carry a stable name and fields the "
                "reader can filter on: run id, stage, url or sku, duration, status and a short reason. That is the "
                "difference between grepping for a phrase someone happened to write and asking for every dropped "
                "row in one run. Levels must mean something. Debug is per page and usually off, info marks run "
                "start, milestones and run end, warning records a data-quality decision such as a dropped item, and "
                "error records a failure that needs attention. Logging every page at info makes the signal "
                "unreadable, while logging nothing about drops makes the dataset unexplainable. Emit logs at stage "
                "boundaries, include the run id on every line, and never log tokens, cookies or personal data; "
                "redaction belongs at the logging call, not in a later cleanup. Observability is broader than logs: "
                "metrics aggregate, traces connect one request across stages, and logs explain the specific case. "
                "Today you emit JSON lines with a filtered level and read them as records. The habit to build is to "
                "log the decision, not just the symptom."
            ),
            code=(
                'import json\n'
                'import logging\n'
                'import sys\n'
                '\n'
                'logger = logging.getLogger("catalog")\n'
                'logger.setLevel(logging.INFO)\n'
                'logger.propagate = False\n'
                'handler = logging.StreamHandler(sys.stdout)\n'
                'handler.setFormatter(logging.Formatter("%(message)s"))\n'
                'logger.addHandler(handler)\n'
                '\n'
                'def emit(level, event, **fields):\n'
                '    record = {"level": logging.getLevelName(level), "event": event}\n'
                '    record.update(fields)\n'
                '    logger.log(level, json.dumps(record, sort_keys=True))\n'
                '\n'
                'emit(logging.INFO, "run_start", run="r7", pages=3)\n'
                'emit(logging.DEBUG, "page_fetch", run="r7", url="https://shop.example/1")\n'
                'emit(logging.INFO, "page_ok", run="r7", url="https://shop.example/1", rows=2)\n'
                'emit(logging.WARNING, "row_dropped", run="r7", sku="B2", reason="missing price")\n'
                'emit(logging.INFO, "run_end", run="r7", rows=4)\n'
                '\n'
                'assert logger.level == logging.INFO\n'
                'print("debug events filtered; warning and above survive")\n'
            ),
            variant_b='raise the logger level to WARNING and predict which of the five events still appear',
            variant_c='add a token field to one event and redact it before serialising',
            mistakes=[
                "Logging full responses or credentials, turning the log itself into a security incident.",
                "Using info for every page, so a real warning is buried in thousands of routine lines.",
                "Writing free-form sentences with no run id, making one run impossible to reconstruct.",
            ],
            q1=(
                "What makes a structured log event easier to investigate than a printed sentence?",
                "Stable field names can be filtered, counted and joined across events; a sentence has to be parsed by eye and changes with the author.",
            ),
            homework=(
                "Write `emit(logger, level, event, **fields)` that writes one JSON object per line with a level and "
                "event name. Emit a start, a dropped row and an end for one run, capture the lines, and comment "
                "which field makes all three belong to the same run."
            ),
            patterns=["json.dumps", "logging", "print("],
            mapping=(
                "Scrapy's LOG_LEVEL and Python logging handlers control this stream, while containers simply collect "
                "stdout. Log aggregators index the JSON fields, so run id and event become searchable dimensions."
            ),
        ),
        156: dict(
            topic="Isolating failures",
            idea=(
                "Failures have a blast radius, and the job of operations is to keep that radius small. A bad price "
                "on one product should not erase the other thousand products, but a wrong database password should "
                "stop the run before it wastes an hour. Those are different failure domains, so they deserve "
                "different boundaries. Item-level parsing gets a try and a quarantine bucket; page-level fetching "
                "gets a retry budget and a failure record; run-level configuration, authentication and disk space "
                "get fail-fast checks at startup. The quarantine is the important habit: keep the offending input, "
                "the exception type and enough context to reproduce it, rather than dropping it into a bare except. "
                "A quarantine with entries is a work queue for tomorrow, and an empty one is evidence that the "
                "batch was clean. Bounded retries belong here too. Retrying a malformed record will never succeed, "
                "while retrying a timeout a couple of times often will. Repeated 5xx or 429 responses should trip a "
                "circuit breaker and pause the domain instead of burning the whole run. Today you process five items "
                "where three fail for different reasons, count the good and quarantined rows, and assert that no "
                "item vanished. That assertion is the real lesson: isolation changes where a failure goes, never "
                "whether it is recorded."
            ),
            code=(
                'items = [\n'
                '    {"sku": "A1", "price": "9.99"},\n'
                '    {"sku": "B2", "price": "free"},\n'
                '    {"sku": "C3"},\n'
                '    {"sku": "D4", "price": "-1.00"},\n'
                '    {"sku": "E5", "price": "12.50"},\n'
                ']\n'
                '\n'
                'def parse_item(item):\n'
                '    price = float(item["price"].lstrip("$"))\n'
                '    if price < 0:\n'
                '        raise ValueError("negative price")\n'
                '    return {"sku": item["sku"], "price": price}\n'
                '\n'
                'good, quarantine = [], []\n'
                'for item in items:\n'
                '    try:\n'
                '        good.append(parse_item(item))\n'
                '    except (KeyError, ValueError) as error:\n'
                '        quarantine.append({"sku": item.get("sku", "?"), "error": type(error).__name__})\n'
                '\n'
                'print("good:", len(good), "| quarantined:", len(quarantine))\n'
                'for entry in quarantine:\n'
                '    print(entry)\n'
                'assert len(good) + len(quarantine) == len(items)\n'
                'print("one bad item cannot empty the batch")\n'
            ),
            variant_b='add a sixth item with price " 8.00 " and decide whether parsing should strip first',
            variant_c='give the negative price one retry after correction and print how the buckets change',
            mistakes=[
                "Catching a broad exception and continuing without recording which item failed.",
                "Retrying a malformed item forever instead of quarantining it for inspection.",
                "Isolating a configuration or authentication error so the run limps on with no useful data.",
            ],
            q1=(
                "Why quarantine a bad item instead of silently skipping it?",
                "Quarantine preserves the input and reason, so the failure can be reproduced and counted rather than disappearing from the dataset.",
            ),
            homework=(
                "Write `partition(items)` that returns good rows and quarantine entries with sku and error type. Run "
                "it on a batch with a missing field and a batch with a malformed price, print both partitions, and "
                "comment which exception path keeps the batch alive."
            ),
            patterns=["try:", "except", "print("],
            mapping=(
                "This is a bulkhead in miniature: Scrapy's errback and item-drop counters play the quarantine role, "
                "while health checks and startup validation fail fast for problems no retry can fix."
            ),
        ),
        157: dict(
            topic="Testing parsers with fixtures",
            idea=(
                "A parser is the part of a scraper most likely to break and least likely to be exercised by a unit "
                "test written from imagination. Fixtures fix that. Save real pages, or realistic excerpts, as frozen "
                "inputs next to an expected record. The parser is pure, so the test needs no network, no server and "
                "no waiting; it either reproduces the expected record or shows a diff. Build a fixture set that "
                "covers more than the happy path: a normal card, a missing price, a changed wrapper element, an "
                "empty list, and odd whitespace or encoding. The failures you have already seen in production are "
                "the most valuable fixtures, because they turn one incident into a permanent regression test. Keep "
                "each fixture small and anonymised, and name it for the layout it represents rather than the date "
                "it was saved. When the site changes, update the fixture deliberately and review the new expected "
                "record; a fixture that updates itself has stopped testing anything. Today's harness is deliberately "
                "plain: a list of input and expected pairs, a loop, and a printed mismatch report. That is enough "
                "to teach the contract before a test framework adds nicer output. The key discipline is that the "
                "fixture is the specification: if the parser and the fixture disagree, one of them is wrong and the "
                "test forces you to say which."
            ),
            code=(
                'def parse_card(html):\n'
                '    title = html.split("<h2>")[1].split("</h2>")[0].strip()\n'
                '    price_text = html.split(\'<span class="price">\')[1].split("</span>")[0].strip()\n'
                '    if not price_text.startswith("$"):\n'
                '        return {"title": title, "price": None}\n'
                '    return {"title": title, "price": float(price_text[1:].replace(",", ""))}\n'
                '\n'
                'FIXTURES = [\n'
                '    (\'<h2>Dune</h2><span class="price">$9.99</span>\', {"title": "Dune", "price": 9.99}),\n'
                '    (\'<h2>Foundation</h2><span class="price">$12.50</span>\', {"title": "Foundation", "price": 12.5}),\n'
                '    (\'<h2>Sold Out</h2><span class="price">n/a</span>\', {"title": "Sold Out", "price": None}),\n'
                ']\n'
                '\n'
                'def run_tests(cases):\n'
                '    failures = []\n'
                '    for index, (html, expected) in enumerate(cases, 1):\n'
                '        got = parse_card(html)\n'
                '        if got != expected:\n'
                '            failures.append((index, got, expected))\n'
                '    return failures\n'
                '\n'
                'failures = run_tests(FIXTURES)\n'
                'print("fixtures:", len(FIXTURES), "| failures:", len(failures))\n'
                'for failure in failures:\n'
                '    print("mismatch:", failure)\n'
                'assert failures == []\n'
                'print("parser agrees with every frozen page")\n'
            ),
            variant_b='add a fixture with a comma price such as $1,250.00 and check the conversion',
            variant_c='add an empty-list page fixture and decide whether the parser should raise or return []',
            mistakes=[
                "Testing only markup you invented, which misses the wrappers and quirks real pages carry.",
                "Fetching the live site inside the test, making results depend on today's network and content.",
                "Auto-updating expected fixtures, so a parser regression is silently declared correct.",
            ],
            q1=(
                "Why is a saved HTML fixture more valuable than a live-site test for a parser?",
                "It is deterministic, offline and reviewable; it isolates parser logic from network and site changes and turns past failures into regressions.",
            ),
            homework=(
                "Write `run_tests(cases)` that compares `parse_card` against (html, expected) fixtures and returns "
                "mismatches. Run it with three passing fixtures and with one broken expectation, print both reports, "
                "and comment which fixture represents a past production failure."
            ),
            patterns=["def ", "for ", "print("],
            mapping=(
                "Teams keep a fixtures directory beside the spider and run it in CI on every change. When a site "
                "redesign breaks the build, the failing fixture names the layout that changed."
            ),
        ),
        158: dict(
            topic="Packaging a scraper CLI",
            idea=(
                "A scraper that only runs from an interactive session is not deployable. The command line is the "
                "stable interface between the code and everything that invokes it: a human debugging, a cron entry, "
                "a container entrypoint, a backfill script. Treat it as a contract. Subcommands such as run, check "
                "and backfill say what the process intends; flags such as limit and dry-run make small, safe "
                "experiments possible; exit codes tell the caller what happened. Zero means success, one means the "
                "run completed with a data or partial failure that needs attention, and two means the arguments "
                "were wrong. Cron and orchestrators act on those codes, so returning zero after every crash is a "
                "silent outage. Keep stdout for records and summaries and stderr for logs, so a caller can pipe the "
                "result without capturing noise. Never prompt for input in an unattended process, and never put a "
                "secret in a flag where it appears in process lists; read secrets from the environment. Argparse "
                "gives you help, type conversion and clear usage errors for free, which is usually enough. Today you "
                "parse a fixed argument list, build the run plan and print it without touching a site. That "
                "separation between argument parsing and work is what lets the same entry point be tested and "
                "scheduled."
            ),
            code=(
                'import argparse\n'
                '\n'
                'def build_parser():\n'
                '    parser = argparse.ArgumentParser(prog="catalog-scraper")\n'
                '    parser.add_argument("--limit", type=int, default=5)\n'
                '    parser.add_argument("--dry-run", action="store_true")\n'
                '    parser.add_argument("--fail-on-empty", action="store_true")\n'
                '    return parser\n'
                '\n'
                'def plan(limit, dry_run):\n'
                '    pages = [f"https://shop.example/page/{n}" for n in range(1, limit + 1)]\n'
                '    return {"mode": "dry-run" if dry_run else "live", "pages": pages}\n'
                '\n'
                'args = build_parser().parse_args(["--limit", "2", "--dry-run"])\n'
                'result = plan(args.limit, args.dry_run)\n'
                'print("mode:", result["mode"], "| pages:", len(result["pages"]))\n'
                'for page in result["pages"]:\n'
                '    print(" ", page)\n'
                'assert result["mode"] == "dry-run" and len(result["pages"]) == 2\n'
                'print("exit code would be 0")\n'
            ),
            variant_b='parse ["--limit", "4"] without --dry-run and compare the mode line',
            variant_c='add a check subcommand that validates config and returns exit code 2 on a missing value',
            mistakes=[
                "Exiting with status zero after a failed run, so the scheduler records a false success.",
                "Printing logs to stdout, where they corrupt a piped JSON or CSV stream.",
                "Putting an API token in a command-line flag, where it is visible in process listings.",
            ],
            q1=(
                "Why should an unattended scraper have meaningful exit codes?",
                "Cron and orchestrators cannot read prose; they branch on the exit status to retry, alert or mark the run failed.",
            ),
            homework=(
                "Write `build_parser()` with run and check subcommands plus a --limit flag, then parse two different "
                "argument lists, print the resulting namespace for each, and comment which exit code a missing "
                "required option should produce."
            ),
            patterns=["argparse", "def ", "print("],
            mapping=(
                "A console_scripts entry point or `python -m scraper` makes the same command available locally, in "
                "cron and as a Docker ENTRYPOINT. Orchestrators key retries and alerts off its exit code."
            ),
        ),
        159: dict(
            topic="Configuration and secrets",
            idea=(
                "Environment-specific values should not be edited into source code. A scraper needs a concurrency "
                "limit, a timeout, an output path, a base URL and a credential, and those values differ between a "
                "laptop, CI and production. Use one resolution order and make it boring: defaults, then a config "
                "file, then environment variables, then explicit flags, with the later source winning. Print the "
                "resolved configuration once at startup, with secrets redacted, so the run record says what it "
                "actually used. Validate before the first request: a missing token or a non-numeric timeout should "
                "stop the process in the first second, not after an hour of crawling. Typed conversion matters too, "
                "because the string eight from the environment is not the integer eight your worker pool expects. "
                "Secrets are a separate discipline. They belong in a secret manager or the process environment, "
                "never in the repository, a fixture, a log line or a container image layer. Access tokens rotate, so "
                "read them at start rather than baking them in, and redact them at the logging boundary. Keep "
                "separate configuration per environment and avoid a hidden default that silently points production "
                "at a staging database. Today you resolve four sources and mask the token before printing. The "
                "lesson is that configuration is an input to be validated, exactly like a scraped page."
            ),
            code=(
                'DEFAULTS = {"concurrency": 2, "timeout": 10, "output": "out/items.jsonl"}\n'
                'FILE_CONFIG = {"concurrency": 4, "timeout": 15}\n'
                'ENV = {"SCRAPER_CONCURRENCY": "8", "SCRAPER_API_TOKEN": "secret-abc123"}\n'
                'CLI = {"output": "out/nightly.jsonl"}\n'
                '\n'
                'def resolve(defaults, file_config, env, cli):\n'
                '    config = dict(defaults)\n'
                '    config.update(file_config)\n'
                '    for key in ("concurrency", "timeout"):\n'
                '        name = "SCRAPER_" + key.upper()\n'
                '        if name in env:\n'
                '            config[key] = int(env[name])\n'
                '    config["token"] = env.get("SCRAPER_API_TOKEN")\n'
                '    config.update(cli)\n'
                '    missing = [key for key in ("token", "output") if not config.get(key)]\n'
                '    if missing:\n'
                '        raise ValueError("missing config: " + ", ".join(missing))\n'
                '    return config\n'
                '\n'
                'def redact(config):\n'
                '    safe = dict(config)\n'
                '    if safe.get("token"):\n'
                '        safe["token"] = safe["token"][:4] + "***"\n'
                '    return safe\n'
                '\n'
                'config = resolve(DEFAULTS, FILE_CONFIG, ENV, CLI)\n'
                'print("resolved:", redact(config))\n'
                'assert config["concurrency"] == 8 and config["output"] == "out/nightly.jsonl"\n'
                'print("CLI beats env beats file beats defaults")\n'
            ),
            variant_b='remove SCRAPER_API_TOKEN and confirm the resolver raises before any work begins',
            variant_c='put a token in CLI instead of ENV and explain why that is a worse practice',
            mistakes=[
                "Committing a real token to the repository or baking it into a container image layer.",
                "Leaving concurrency as the string from the environment and passing it to a numeric API.",
                "Logging the full resolved config, including the credential, at info level.",
            ],
            q1=(
                "Why validate configuration at startup rather than when the first request needs it?",
                "Failing early avoids wasted crawling and makes the error a clear configuration problem instead of a confusing runtime symptom.",
            ),
            homework=(
                "Write `resolve(defaults, file_config, env, cli)` with a documented precedence order and a required "
                "token check. Run it with all four sources and with the token removed, print both results, and "
                "comment which source won for the output path."
            ),
            patterns=["dict(", "def ", "print("],
            mapping=(
                "Twelve-factor deployments pass configuration through env vars, secret managers inject credentials "
                "at runtime, and Docker images stay free of secrets. Validation in the entry point is the last gate."
            ),
        ),
        160: dict(
            topic="Deployment basics",
            idea=(
                "Deployment is the act of turning a repository into a repeatable process somewhere else. The safest "
                "version of that act is to build one immutable artifact, give it a content digest, and run that "
                "exact artifact in every environment. If the laptop and production run different files, a bug is "
                "either an environment problem or a version problem and you cannot tell which. Pin dependencies, "
                "keep the image or virtual environment reproducible, and record the version in the run log. The "
                "process itself should be boring: one scraper process per container, configuration from the "
                "environment, output written to a mounted volume or an external store, logs on stdout, and a "
                "healthcheck that reflects actual readiness. Handle shutdown. Orchestrators send SIGTERM and expect "
                "the process to finish the current item, flush and exit; a scraper that ignores it leaves truncated "
                "files. Publish results atomically by writing to a temporary path and renaming when complete, so a "
                "reader never sees half a dataset. Add a smoke run against a fixed fixture as part of the deploy, "
                "and keep the previous digest available for rollback. Today you build a small artifact manifest and "
                "check its required files. The deployment checklist is not bureaucracy; it is the difference "
                "between a run you can reproduce and one you can only remember."
            ),
            code=(
                'import hashlib\n'
                '\n'
                'files = {\n'
                '    "run.py": "from spider import Spider",\n'
                '    "spider.py": "class Spider: pass",\n'
                '    "pipelines.py": "def validate(item): return item",\n'
                '}\n'
                'required = {"run.py", "spider.py"}\n'
                '\n'
                'manifest = {name: hashlib.sha256(text.encode()).hexdigest()[:10]\n'
                '            for name, text in sorted(files.items())}\n'
                'missing = sorted(required - set(manifest))\n'
                '\n'
                'print("files:", len(manifest), "| missing:", missing)\n'
                'for name in sorted(manifest):\n'
                '    print(" ", name, manifest[name])\n'
                'assert not missing\n'
                'print("deploy the digest; mount output; pass secrets as env")\n'
            ),
            variant_b='remove spider.py from files and confirm the manifest check reports it missing',
            variant_c='add an empty requirements.txt entry and explain why pinned versions matter more than the file name',
            mistakes=[
                "Deploying a different working tree than the one that was tested, so the version on disk is unknown.",
                "Writing results directly to the final path, so readers can observe a partially written file.",
                "Ignoring SIGTERM, leaving an orchestrator to kill the process mid-write.",
            ],
            q1=(
                "Why deploy an immutable artifact identified by a digest rather than a mutable checkout?",
                "A digest proves exactly which files ran, makes rollback a matter of starting the previous digest, and removes environment drift as an explanation.",
            ),
            homework=(
                "Write `manifest(files)` that returns a name-to-digest mapping and a `missing_files` check against a "
                "required set. Run it on a complete file set and on one missing the entrypoint, print both results, "
                "and comment which check should block a deploy."
            ),
            patterns=["hashlib", "dict(", "print("],
            mapping=(
                "Docker images, tagged releases and virtualenv lock files are all attempts at this immutable artifact. "
                "A container with an ENTRYPOINT, an env-driven config and a mounted output volume is the common shape."
            ),
        ),
        161: dict(
            topic="Scaling horizontally",
            idea=(
                "When one worker cannot finish before the next run is due, the obvious move is to start more "
                "workers. The obvious move fails unless the work is partitioned and the writes are idempotent. Two "
                "workers given the same URL will fetch it twice, and two workers upserting the same row may produce "
                "a race. A shared frontier solves this with leases: a worker claims a URL for a limited time, "
                "renews the lease while working and releases it on completion, so a crashed worker's claim expires "
                "and the URL becomes available again. That gives at-least-once delivery, which is acceptable only "
                "if storage is idempotent, for example by keying rows on a stable identity and upserting. "
                "Partitioning by a hash of the URL or domain spreads work predictably and lets you reason about "
                "ownership, while a simple modulo changes almost every assignment when the worker count changes. "
                "Watch for the new bottleneck: a single database or a global per-domain rate limiter can make ten "
                "workers no faster than two. Measure rows per worker per minute, not just total rows, and log which "
                "worker handled which URL. Today you shard a URL list across three simulated workers and assert "
                "that every URL has exactly one owner. That assertion is the foundation of safe parallelism."
            ),
            code=(
                'import hashlib\n'
                '\n'
                'urls = [f"https://shop.example/item/{n}" for n in range(1, 7)]\n'
                'workers = 3\n'
                '\n'
                'def shard(url, count):\n'
                '    digest = hashlib.sha256(url.encode()).hexdigest()\n'
                '    return int(digest, 16) % count\n'
                '\n'
                'buckets = {worker: [] for worker in range(workers)}\n'
                'for url in urls:\n'
                '    buckets[shard(url, workers)].append(url)\n'
                '\n'
                'print("urls:", len(urls), "| workers:", workers)\n'
                'for worker, chunk in sorted(buckets.items()):\n'
                '    print("worker", worker, "->", len(chunk), "urls")\n'
                '\n'
                'assigned = [url for chunk in buckets.values() for url in chunk]\n'
                'assert sorted(assigned) == sorted(urls)\n'
                'assert len(assigned) == len(set(assigned))\n'
                'print("each url has exactly one owner")\n'
            ),
            variant_b='set workers=4 and compare how the buckets move for the same six urls',
            variant_c='give one URL to two workers by appending it twice and show why the uniqueness assertion fails',
            mistakes=[
                "Starting more workers without a shared frontier, so the same URLs are crawled repeatedly.",
                "Assuming exactly-once delivery instead of designing storage to tolerate at-least-once retries.",
                "Ignoring a shared database or per-domain rate limit that becomes the real bottleneck.",
            ],
            q1=(
                "Why does horizontal scraping require idempotent writes?",
                "Leases and retries produce at-least-once delivery, so the same item may be processed twice; idempotent upserts make the duplicate harmless.",
            ),
            homework=(
                "Write `partition(urls, workers)` that assigns URLs by a stable hash and returns a list of buckets. "
                "Run it with three workers and four workers, print both distributions, and comment how many URLs "
                "changed owner."
            ),
            patterns=["hashlib", "def ", "print("],
            mapping=(
                "Scrapy clusters, Celery workers and queue-backed crawlers use a shared scheduler plus leases or "
                "acknowledgements. Storage uses primary keys and upserts so a redelivered message does not duplicate rows."
            ),
        ),
        162: dict(
            topic="Cost and storage budgets",
            idea=(
                "Every page has a price even when the site is free. Requests consume bandwidth and sometimes paid "
                "API quota; parsing consumes CPU; raw HTML consumes disk; keeping history consumes it every day. "
                "The budget conversation starts before the run, not after the invoice. Estimate pages per run, "
                "average kilobytes per page, runs per day and retention days, and multiply. Then decide what to "
                "keep. Raw HTML is valuable for debugging a parser change but expensive to retain forever; parsed "
                "records are smaller and usually what consumers need; aggregates may be enough for old periods. "
                "Compression and a shorter raw-retention window often cut storage by an order of magnitude without "
                "losing the current dataset. Set explicit caps: a maximum pages per run, a maximum bytes written and "
                "a monthly cost ceiling, with a check that fails the run before it exceeds them. Alert at a "
                "percentage of the budget so there is time to react. Also weigh freshness against spend: crawling "
                "an unchanged catalog hourly is usually waste, while a price-sensitive feed may justify it. Today "
                "you project daily storage and monthly request cost from a handful of parameters, compare them to a "
                "budget, and print the decision. Numbers like these turn an argument about scraping into an "
                "engineering choice with a ceiling."
            ),
            code=(
                'def project(pages_per_run, kb_per_page, runs_per_day, retention_days, cost_per_1k_requests):\n'
                '    raw_mb = pages_per_run * kb_per_page / 1024\n'
                '    daily_mb = raw_mb * runs_per_day\n'
                '    stored_mb = daily_mb * retention_days\n'
                '    monthly_requests = pages_per_run * runs_per_day * 30\n'
                '    cost = monthly_requests / 1000 * cost_per_1k_requests\n'
                '    return {\n'
                '        "daily_mb": round(daily_mb, 1),\n'
                '        "stored_mb": round(stored_mb, 1),\n'
                '        "monthly_cost": round(cost, 2),\n'
                '    }\n'
                '\n'
                'result = project(5000, 120, 1, 30, 0.5)\n'
                'budget = {"storage_mb": 20000, "cost": 100.0}\n'
                'print(result)\n'
                'print("over storage:", result["stored_mb"] > budget["storage_mb"])\n'
                'print("over cost:", result["monthly_cost"] > budget["cost"])\n'
                'assert result["stored_mb"] > 0\n'
                'print("decide before the run, not after the invoice")\n'
            ),
            variant_b='raise runs_per_day to 4 and compare both the stored megabytes and the monthly cost',
            variant_c='cut retention_days from 30 to 7 and explain what history the saving gives up',
            mistakes=[
                "Retaining raw HTML forever because it might be useful, without pricing the growth.",
                "Crawling at maximum cadence when the data changes far less often than the schedule.",
                "Discovering the storage limit only when the disk fills and the run fails mid-write.",
            ],
            q1=(
                "Why estimate storage from pages, bytes and retention before changing the schedule?",
                "Those three factors multiply, so a modest cadence change or a longer retention window can turn a comfortable budget into a failed run.",
            ),
            homework=(
                "Write `project(pages_per_run, kb_per_page, runs_per_day, retention_days, cost_per_1k)` and a "
                "`within_budget` check. Run it on a daily crawl and an hourly crawl, print both projections, and "
                "comment which parameter drives the largest difference."
            ),
            patterns=["def ", "return", "print("],
            mapping=(
                "Cloud storage bills, egress charges and request quotas all follow these multiplications. Budget "
                "alerts and max-pages caps are the operational guardrails around a crawl."
            ),
        ),
        163: dict(
            topic="Data refresh and versioning",
            idea=(
                "A scraped dataset is not a single table; it is a series of observations over time. Treating each "
                "refresh as a fresh overwrite throws away the evidence you need when a number looks wrong. The "
                "usual shape is two layers: a current table keyed by a stable identity, and an append-only history "
                "of changes. On each run, compare the new record with the stored one using a content hash rather "
                "than a fetch timestamp, because timestamps change even when the data does not. An unseen key is an "
                "insert, a different hash is an update, and an identical hash is unchanged. A key that disappears "
                "from the source should be marked missing with the date it was last seen, not silently deleted; "
                "sites hide products temporarily and reappear. Record first_seen and last_seen so freshness is "
                "answerable per row. Schema changes deserve their own version: if the parser starts emitting a new "
                "field, old and new rows must remain interpretable, which usually means a schema_version column and "
                "a migration plan. Keep the refresh idempotent so rerunning the same input produces no new history "
                "entries. Today you compare an old snapshot with a new one and print a ledger of inserts, updates "
                "and unchanged rows. The ledger is the audit trail that makes tomorrow's question answerable."
            ),
            code=(
                'old = {"A1": {"hash": "h123", "price": 9.99}, "B2": {"hash": "h456", "price": 12.5}}\n'
                'scraped = {\n'
                '    "A1": {"hash": "h123", "price": 9.99},\n'
                '    "B2": {"hash": "h789", "price": 13.0},\n'
                '    "C3": {"hash": "h999", "price": 7.0},\n'
                '}\n'
                '\n'
                'def refresh(old, new, seen_on):\n'
                '    counts = {"insert": 0, "update": 0, "unchanged": 0, "missing": 0}\n'
                '    ledger = []\n'
                '    for sku, item in new.items():\n'
                '        if sku not in old:\n'
                '            counts["insert"] += 1\n'
                '            ledger.append((sku, "insert", seen_on))\n'
                '        elif old[sku]["hash"] != item["hash"]:\n'
                '            counts["update"] += 1\n'
                '            ledger.append((sku, "update", seen_on))\n'
                '        else:\n'
                '            counts["unchanged"] += 1\n'
                '    for sku in old:\n'
                '        if sku not in new:\n'
                '            counts["missing"] += 1\n'
                '            ledger.append((sku, "mark_missing", seen_on))\n'
                '    return counts, ledger\n'
                '\n'
                'counts, ledger = refresh(old, scraped, "2026-10-19")\n'
                'print(counts)\n'
                'for row in ledger:\n'
                '    print(row)\n'
                'assert counts == {"insert": 1, "update": 1, "unchanged": 1, "missing": 0}\n'
                'print("history stays append-only; disappearances get a tombstone")\n'
            ),
            variant_b='remove C3 from the scraped snapshot and confirm it becomes a missing row',
            variant_c='change B2 price but keep the same hash and explain why the refresh would now be wrong',
            mistakes=[
                "Overwriting the current table without recording what changed or when.",
                "Deleting disappeared rows immediately instead of marking them missing with a last-seen date.",
                "Comparing fetch timestamps instead of content hashes, so every run looks like an update.",
            ],
            q1=(
                "Why compare content hashes rather than timestamps when deciding whether a record changed?",
                "A fetch timestamp changes on every run even when the row is identical; a content hash changes only when the data does.",
            ),
            homework=(
                "Write `refresh(old, new, seen_on)` that returns change counts and a ledger of inserts, updates and "
                "missing rows. Run it on a snapshot with one new and one changed item and on one with a removed "
                "item, print both ledgers, and comment which entry preserves history."
            ),
            patterns=["def ", "items()", "print("],
            mapping=(
                "Warehouse tables keep current and historical layers, with dbt snapshots or merge statements doing "
                "this comparison. Content hashes make reruns idempotent and tombstones keep vanished products auditable."
            ),
        ),
        164: dict(
            topic="Review: production scraping",
            idea=(
                "A production scraper is the sum of the habits in this phase, and the test is whether you can "
                "operate it without heroics. The spider describes one site and returns records. Pure parsers are "
                "checked against fixtures, and a pipeline cleans, validates and deduplicates before storage. "
                "Middlewares hold transport policy, the scheduler owns cadence, and a lock prevents overlap. A run "
                "summary reports pages, rows, drops and duration; structured logs explain individual decisions; "
                "monitoring alerts on empty runs and stale data. Failures are isolated per item or page, quarantined "
                "with evidence, and configuration is validated at startup with secrets kept out of logs. Deployment "
                "runs an immutable artifact with an atomic output path, and scaling partitions work rather than "
                "duplicating it. Budgets cap pages and storage before they surprise you, and refresh records change "
                "history instead of overwriting it. None of these pieces is clever on its own. The professional "
                "skill is keeping them boring and connected, so a broken selector produces a specific alert and a "
                "reversible fix rather than a silent data outage. Today you run the whole shape once over two "
                "fixtures and read the summary as an operator would. The remaining work is not another abstraction; "
                "it is a runbook, an owner and a review of what the last incident taught you."
            ),
            code=(
                'FIXTURES = {\n'
                '    "https://shop.example/1": "<li>Dune|9.99</li><li>Foundation|12.50</li>",\n'
                '    "https://shop.example/2": "<li>Dune|9.99</li><li>Broken|n/a</li>",\n'
                '}\n'
                '\n'
                'def parse_page(html):\n'
                '    rows = []\n'
                '    for chunk in html.split("<li>")[1:]:\n'
                '        title, _, price = chunk.partition("|")\n'
                '        try:\n'
                '            rows.append({"title": title.strip(), "price": float(price.split("</li>")[0])})\n'
                '        except ValueError:\n'
                '            continue\n'
                '    return rows\n'
                '\n'
                'def run(pages):\n'
                '    items, failed = [], 0\n'
                '    for url, html in sorted(pages.items()):\n'
                '        try:\n'
                '            items.extend(parse_page(html))\n'
                '        except Exception:\n'
                '            failed += 1\n'
                '    return items, failed\n'
                '\n'
                'items, failed = run(FIXTURES)\n'
                'seen, unique = set(), []\n'
                'for item in items:\n'
                '    key = (item["title"], item["price"])\n'
                '    if key not in seen:\n'
                '        seen.add(key)\n'
                '        unique.append(item)\n'
                '\n'
                'print("pages:", len(FIXTURES), "| parsed:", len(items), "| unique:", len(unique), "| failed:", failed)\n'
                'for item in unique:\n'
                '    print(item["title"], item["price"])\n'
                'assert len(unique) == 2 and failed == 0\n'
                'print("run summary: every stage reported, nothing vanished")\n'
            ),
            variant_b='make parse_page raise on the malformed item instead of skipping it, then decide which layer should catch it',
            variant_c='add a third fixture with a duplicate title at a new price and discuss whether it is an update or a duplicate',
            mistakes=[
                "Treating the first successful run as the finish line instead of writing the runbook and alert owner.",
                "Hiding a stage failure by skipping it silently, so the summary looks clean and the dataset is short.",
                "Adding complexity to handle a hypothetical site before the current pipeline is observable and tested.",
            ],
            q1=(
                "What makes a scraper production-ready rather than merely working?",
                "It is scheduled, observable, tested against fixtures, isolated in failure, configurable, deployable and budgeted, with a known owner and runbook.",
            ),
            homework=(
                "Write `run(pages)` that parses fixtures, skips malformed rows, deduplicates records and returns a "
                "summary with pages, parsed, unique and failed counts. Run it on a clean fixture set and one with a "
                "broken row, print both summaries, and comment which count reveals the silent drop."
            ),
            patterns=["def ", "try:", "print("],
            mapping=(
                "This is the checklist an on-call engineer uses: spider, pipeline, middleware, schedule, logs, "
                "alerts, quarantine, CLI, config, deployment, sharding, budget and versioned refresh."
            ),
        ),
    },
)
