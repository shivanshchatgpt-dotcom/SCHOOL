"""Web Scraping phase 4, days 120-134: crawling many pages without breaking things.

Every example runs offline. Pages, links and responses live in dictionaries so the
learner can study frontier behaviour, politeness and recovery without a network.
"""

PHASE = (
    "Robust Crawling",
    "Crawl many pages with a bounded, polite, resumable frontier instead of one long for-loop.",
    {
        120: dict(
            topic="A crawler is a queue",
            idea=(
                "The mental model that unlocks crawling is simple: a crawler is a queue of URLs plus a set "
                "of URLs it has already accepted. You start by pushing a seed, then repeatedly pop one URL "
                "and push the links discovered inside it. That is the whole machine. The queue is what "
                "turns a single page parser into something that can walk a site, and the seen set is what "
                "stops the same page being fetched twice. This loop is deliberately boring, because the "
                "hard parts of crawling are all consequences of it: ordering comes from the queue policy, "
                "politeness comes from how fast you pop, recovery comes from what you save between pops. "
                "Writing the loop by hand first matters. If you begin with a framework you learn its "
                "configuration vocabulary without learning the control flow it hides. In this example the "
                "pages dictionary stands in for the network, so you can watch a page enter the frontier "
                "exactly once and see the visit order without waiting on sockets. Notice that discovery "
                "and fetching are separate steps: a page can link to a URL that is queued but not yet "
                "fetched, and a broken URL may still occupy the queue. Keep that distinction in your head, "
                "because most crawler bugs are really bookkeeping bugs in this pair of structures."
            ),
            code=(
                'from collections import deque\n'
                '\n'
                'pages = {\n'
                '    "https://shop.test/": ["https://shop.test/a", "https://shop.test/b"],\n'
                '    "https://shop.test/a": ["https://shop.test/c"],\n'
                '    "https://shop.test/b": ["https://shop.test/c"],\n'
                '    "https://shop.test/c": [],\n'
                '}\n'
                '\n'
                'frontier = deque(["https://shop.test/"])\n'
                'seen = {"https://shop.test/"}\n'
                'visited = []\n'
                'while frontier:\n'
                '    url = frontier.popleft()\n'
                '    visited.append(url)\n'
                '    for link in pages.get(url, []):\n'
                '        if link not in seen:\n'
                '            seen.add(link)\n'
                '            frontier.append(link)\n'
                '\n'
                'print("visit order:", visited)\n'
                'print("pages:", len(visited), "links seen:", len(seen))\n'
                'assert len(visited) == len(pages)\n'
                'print("every page queued once")'
            ),
            variant_b='add a second seed "https://shop.test/b" to the initial frontier',
            variant_c='remove the seen set and observe how /c is queued twice',
            mistakes=[
                "Checking seen only after fetching, so duplicate URLs still cost a request.",
                "Pushing links during parsing without recording them, so the frontier explodes.",
                "Treating the visited list as the seen set, which grows only after a fetch completes.",
            ],
            q1=(
                "Why does a crawler need a seen set as well as a queue?",
                "The queue holds work still to do; the seen set records every URL already accepted, so links pointing to known pages are not queued again.",
            ),
            homework=(
                "Write `crawl_frontier(pages, seeds)` that returns the visit order for a dictionary of "
                "page links using a deque and a seen set. Run it on two different page maps, print both "
                "orders, and comment on which line prevents a duplicate from entering the queue."
            ),
            patterns=["deque(", "seen", ".popleft()"],
            mapping=(
                "Scrapy's scheduler is this queue with persistence and priorities attached. The same two "
                "structures appear in every crawler: a frontier of pending URLs and a deduplication store "
                "of what has already been scheduled."
            ),
        ),
        121: dict(
            topic="Breadth-first vs depth-first",
            idea=(
                "A frontier can be a FIFO queue or a LIFO stack, and that single choice changes the shape "
                "of the crawl. Breadth-first pops the oldest URL, so it finishes all links at depth one "
                "before touching depth two, spreading requests evenly across the site. Depth-first pops "
                "the newest URL, plunges down one branch, and may not return to the homepage for hours. "
                "For a scraper the trade-off is practical rather than academic. Breadth-first gives you "
                "quick coverage of top-level categories and makes it easy to stop after a shallow pass, "
                "which is exactly what you want when estimating site size or checking a new site's "
                "structure. Depth-first is better when a branch is small and self-contained, such as "
                "walking one documentation tree or one product's variants, because it keeps related "
                "context close in time and memory. The same seen set is valid for both, which is the "
                "important lesson: the deduplication rule and the traversal rule are independent. You "
                "can swap traversal without touching how URLs are recorded. That independence is what "
                "lets you experiment with crawl order safely. A useful exercise is to run both policies "
                "on the same graph and confirm they visit the same pages in different sequences, then "
                "ask which order matches the questions your dataset needs answered first."
            ),
            code=(
                'from collections import deque\n'
                '\n'
                'graph = {"home": ["a", "b"], "a": ["c"], "b": ["d"], "c": [], "d": []}\n'
                '\n'
                'def bfs(graph, start):\n'
                '    frontier, seen, order = deque([start]), {start}, []\n'
                '    while frontier:\n'
                '        node = frontier.popleft()\n'
                '        order.append(node)\n'
                '        for nxt in graph[node]:\n'
                '            if nxt not in seen:\n'
                '                seen.add(nxt)\n'
                '                frontier.append(nxt)\n'
                '    return order\n'
                '\n'
                'def dfs(graph, start):\n'
                '    frontier, seen, order = [start], {start}, []\n'
                '    while frontier:\n'
                '        node = frontier.pop()\n'
                '        order.append(node)\n'
                '        for nxt in reversed(graph[node]):\n'
                '            if nxt not in seen:\n'
                '                seen.add(nxt)\n'
                '                frontier.append(nxt)\n'
                '    return order\n'
                '\n'
                'print("bfs:", bfs(graph, "home"))\n'
                'print("dfs:", dfs(graph, "home"))\n'
                'assert set(bfs(graph, "home")) == set(dfs(graph, "home"))\n'
                'print("same pages, different order")'
            ),
            variant_b='reverse the order of each adjacency list before running both traversals',
            variant_c='add a third branch "e" under home and predict where each policy visits it',
            mistakes=[
                "Using pop(0) on a list for breadth-first, which is quadratic on a large frontier.",
                "Pushing a node when it is popped instead of when it is discovered, causing duplicates.",
                "Forgetting that depth-first order depends on link order inside each page.",
            ],
            q1=(
                "Which crawl order finishes the homepage's immediate links first, and why?",
                "Breadth-first, because a FIFO queue appends new links behind everything already waiting at the current depth.",
            ),
            homework=(
                "Write `walk(graph, start, mode)` that returns visit order using a deque when mode is "
                "`bfs` and a list stack when it is `dfs`. Run it on two different graphs, print both "
                "orders, and comment on which data structure changed the sequence."
            ),
            patterns=["deque(", ".pop()", "append("],
            mapping=(
                "Scrapy exposes breadth-first order through its default LIFO or FIFO scheduler settings. "
                "Search engines usually crawl breadth-first for coverage, while focused scrapers go deep "
                "into one section before moving on."
            ),
        ),
        122: dict(
            topic="Canonicalising URLs",
            idea=(
                "The same page can be advertised by many strings: a trailing fragment, a default port, "
                "uppercase scheme, query parameters in a different order, or a relative link that resolves "
                "to an absolute one. If you treat each string as a distinct page, your crawler fetches the "
                "same HTML repeatedly and your dataset gains duplicates that look like separate records. "
                "Canonicalisation is the step that reduces those spellings to one chosen form before the "
                "URL reaches the seen set. The usual moves are mechanical: resolve relative links against "
                "the page URL, lowercase the scheme and host, drop the fragment because it never reaches "
                "the server, remove a default port, and sort query parameters when their order carries no "
                "meaning. Each move encodes an assumption about the site, so canonicalisation is not a "
                "universal truth; it is a policy you choose and should be able to explain. Removing all "
                "query strings, for example, would collapse genuinely different product pages into one. "
                "That is why the function is small and testable: you can feed it a list of spellings and "
                "assert how many unique pages remain. Once the count stops matching reality, you know the "
                "policy, not the crawler, needs changing. Keep the original URL too, so provenance is not "
                "lost when the canonical form is surprising."
            ),
            code=(
                'from urllib.parse import urljoin, urlsplit, urlunsplit\n'
                '\n'
                'def canonical(base, link):\n'
                '    parts = urlsplit(urljoin(base, link))\n'
                '    host = parts.netloc.lower()\n'
                '    if host.endswith(":80"):\n'
                '        host = host[:-3]\n'
                '    query = "&".join(sorted(parts.query.split("&"))) if parts.query else ""\n'
                '    path = parts.path or "/"\n'
                '    return urlunsplit((parts.scheme.lower(), host, path, query, ""))\n'
                '\n'
                'base = "https://Shop.test/catalog/"\n'
                'links = ["../item/7", "https://shop.test/item/7#reviews",\n'
                '         "HTTPS://SHOP.TEST:80/item/7?b=2&a=1", "/item/7"]\n'
                'cleaned = [canonical(base, link) for link in links]\n'
                'print("cleaned:", cleaned)\n'
                'print("unique:", len(set(cleaned)))\n'
                'assert len(set(cleaned)) == 2\n'
                'print("fragment, case and port folded")'
            ),
            variant_b='add "?utm_source=newsletter" to one link and decide whether to strip it',
            variant_c='change the base path to /catalog/shoes/ so ../item/7 resolves elsewhere',
            mistakes=[
                "Lowercasing the path as well as the host, which breaks case-sensitive servers.",
                "Dropping every query parameter, collapsing genuinely different pages into one.",
                "Canonicalising after the seen check, so duplicates still enter the frontier.",
            ],
            q1=(
                "Why should canonicalisation run before the seen check rather than after it?",
                "The seen set is only as good as its keys; cleaning first means two spellings of one page map to the same key and the duplicate is rejected.",
            ),
            homework=(
                "Write `canonical(base, link)` that resolves a link and removes fragments, default ports "
                "and query-order differences. Run it on two lists of messy links, print the unique counts, "
                "and comment on one assumption your policy makes about the site."
            ),
            patterns=["urljoin(", "urlsplit(", "urlunsplit("],
            mapping=(
                "Scrapy has canonicalisation helpers and link extractors that resolve relative URLs before "
                "scheduling. Most duplicate-page problems in real crawls are URL policy problems, not "
                "parser problems."
            ),
        ),
        123: dict(
            topic="Staying on the same site",
            idea=(
                "A crawler that follows every link it finds does not stay a crawler for long. One click "
                "from a blog post can lead to an ad network, a social profile, a CDN, a login domain and "
                "a partner store, and soon most of your requests are spent somewhere you never intended "
                "to scrape. Scope is the rule that decides which URLs are yours to fetch. The simplest "
                "useful scope compares the hostname of a resolved link with the hostname of the seed, and "
                "rejects everything else before it enters the frontier. That one check saves bandwidth, "
                "keeps the dataset coherent and prevents accidental load on third parties who never "
                "invited you. Hostname equality is a starting point, not a complete policy. Some sites "
                "serve content from www and apex variants, or split sections across subdomains, and "
                "sometimes you deliberately want those; other times you want to exclude a staging host "
                "or an infinite search endpoint. The important habit is to write scope as a predicate "
                "with a name, apply it during link discovery, and record what was rejected and why. A "
                "crawler that silently drops half its links is impossible to debug; one that logs the "
                "external host it skipped gives you a map of where the site points. Check scheme too, so "
                "mailto and javascript links do not masquerade as pages."
            ),
            code=(
                'from urllib.parse import urljoin, urlsplit\n'
                '\n'
                'def same_site(base, link):\n'
                '    host = urlsplit(urljoin(base, link)).hostname\n'
                '    return host == urlsplit(base).hostname\n'
                '\n'
                'base = "https://shop.test/blog/"\n'
                'links = ["post-1", "/about", "https://shop.test/help",\n'
                '         "https://ads.test/click", "mailto:hi@shop.test", "javascript:void(0)"]\n'
                'kept, rejected = [], []\n'
                'for link in links:\n'
                '    (kept if same_site(base, link) else rejected).append(link)\n'
                'print("kept:", kept)\n'
                'print("rejected:", rejected)\n'
                'assert len(kept) == 3\n'
                'print("external and non-http links filtered")'
            ),
            variant_b='allow both shop.test and docs.shop.test by comparing registrable suffixes',
            variant_c='add a protocol-relative link "//shop.test/faq" and check how it resolves',
            mistakes=[
                "Comparing the raw href with the seed instead of resolving it first.",
                "Allowing every subdomain when only one host actually serves the catalogue.",
                "Filtering links after fetching them, which spends requests on the wrong site.",
            ],
            q1=(
                "Why must a relative link be resolved before the host check?",
                "A relative link has no host of its own; only urljoin against the page URL reveals which site the browser would actually request.",
            ),
            homework=(
                "Write `in_scope(base, link)` that resolves a link and returns True only for the same "
                "hostname. Run it on two lists mixing internal, external and mailto links, print both "
                "partitions, and comment on which check rejects the non-http schemes."
            ),
            patterns=["urljoin(", "hostname", "True"],
            mapping=(
                "Scrapy's `allowed_domains` setting is exactly this predicate enforced by the scheduler. "
                "robots.txt sits beside it as a second, site-declared boundary rather than a replacement."
            ),
        ),
        124: dict(
            topic="Politeness: delays and concurrency",
            idea=(
                "Politeness is not a feeling; it is a schedule. A crawler is polite when the gap between "
                "two requests to the same host is at least the delay that host expects, no matter how "
                "many URLs are waiting. That sentence contains the key design constraint: the delay is "
                "per host, not per crawler. If you sleep between every request globally, you waste time "
                "when several hosts are available and still hammer one host if you run workers in "
                "parallel. The correct bookkeeping stores, for each host, the earliest time the next "
                "request may start. When a worker takes a URL, it looks up that host's timestamp, waits "
                "if necessary, performs the request, and pushes the timestamp forward by the delay. "
                "Concurrency then becomes safe rather than contradictory: many workers can be active, "
                "but they coordinate through the per-host clock. In this simulation time is just an "
                "integer, so you can inspect the schedule directly instead of measuring wall-clock "
                "jitter. A host with five queued URLs should show starts at zero, two, four and so on, "
                "while a second host proceeds independently. This is also where rate limits and "
                "robots.txt crawl-delay meet your code: both are inputs to the same per-host schedule. "
                "The habit to build is to log the intended start time and the host, then verify the gap."
            ),
            code=(
                'tasks = [("a.test/1", "a.test"), ("b.test/1", "b.test"), ("a.test/2", "a.test"),\n'
                '         ("a.test/3", "a.test"), ("b.test/2", "b.test")]\n'
                'DELAY = 2\n'
                'clock = 0\n'
                'next_allowed = {}\n'
                'schedule = []\n'
                'for url, host in tasks:\n'
                '    start = max(clock, next_allowed.get(host, 0))\n'
                '    schedule.append((start, url, host))\n'
                '    next_allowed[host] = start + DELAY\n'
                '    clock = max(clock, start + 1)\n'
                '\n'
                'for start, url, host in schedule:\n'
                '    print(f"t={start:02d} {host:<6} {url}")\n'
                'same = [t for t in schedule if t[2] == "a.test"]\n'
                'gaps = [b[0] - a[0] for a, b in zip(same, same[1:])]\n'
                'print("a.test gaps:", gaps)\n'
                'assert all(gap >= DELAY for gap in gaps)\n'
                'print("per-host delay honoured")'
            ),
            variant_b='set DELAY to 5 and compare the a.test start times',
            variant_c='add "a.test/4" and see which host now determines the next free slot',
            mistakes=[
                "Sleeping once per loop instead of tying the delay to each host's last request.",
                "Sharing one global next-allowed time so one slow host stalls every other host.",
                "Setting the delay to zero because the site loaded quickly during a manual test.",
            ],
            q1=(
                "Why is a single global delay worse than a per-host delay?",
                "A global delay underuses other hosts but can still overload one host under concurrency; per-host clocks enforce the real constraint and let independent hosts proceed.",
            ),
            homework=(
                "Write `schedule(tasks, delay)` that assigns a start time to every (url, host) pair "
                "respecting a per-host delay. Run it on two task lists with different host mixes, print "
                "both schedules, and comment on which host set the pace."
            ),
            patterns=["next_allowed", "max(", "DELAY"],
            mapping=(
                "Scrapy implements this through AutoThrottle and DOWNLOAD_DELAY. robots.txt crawl-delay "
                "is another per-host input, and queue schedulers use the same next-allowed timestamp."
            ),
        ),
        125: dict(
            topic="A retry taxonomy",
            idea=(
                "Not every failed request deserves another attempt. A crawler that retries everything "
                "wastes time on pages that will never exist and can turn a temporary server problem into "
                "a sustained attack. The mature approach is a small taxonomy of outcomes. Success means "
                "parse the page. Not found or gone means drop the URL and move on. Forbidden means stop "
                "asking for that resource, because repeating the request will not change the answer and "
                "may look hostile. A rate-limit or temporary server error means wait and try again, but "
                "with a bounded number of attempts and a growing pause. Redirects need their own "
                "handling so you follow the target rather than counting the redirect as content. The "
                "taxonomy matters because it turns retry policy from a global switch into a decision "
                "attached to a status. Writing it as a function makes the decision testable: feed it "
                "status codes and assert what should happen. It also prevents the common bug where a "
                "worker retries a 404 three times, then reports the page as a network failure and "
                "pollutes your error metrics. Retry budgets are part of the same idea. An attempt limit "
                "protects the crawl from one pathological URL, while jitter and exponential backoff "
                "protect the server from synchronised retries. Record the final classification, not just "
                "the last status code, so the dataset can explain why a page is missing."
            ),
            code=(
                'ACTIONS = {200: "ok", 301: "follow", 403: "stop", 404: "drop", 410: "drop",\n'
                '           429: "retry", 500: "retry", 503: "retry"}\n'
                '\n'
                'def action(status):\n'
                '    return ACTIONS.get(status, "retry")\n'
                '\n'
                'def fetch_with_retries(statuses, limit=3):\n'
                '    for attempt, status in enumerate(statuses, 1):\n'
                '        decision = action(status)\n'
                '        print(f"attempt {attempt}: {status} -> {decision}")\n'
                '        if decision != "retry":\n'
                '            return decision, attempt\n'
                '    return "gave up", limit\n'
                '\n'
                'print("transient:", fetch_with_retries([503, 500, 200]))\n'
                'print("missing:", fetch_with_retries([404]))\n'
                'print("blocked:", fetch_with_retries([403, 403]))\n'
                'assert action(404) == "drop" and action(503) == "retry"\n'
                'print("taxonomy applied")'
            ),
            variant_b='change the sequence to [429, 200] and confirm only one retry is needed',
            variant_c='feed four 500s to a limit of 2 and check which attempt is reported',
            mistakes=[
                "Retrying every non-200 status, including 404 and 403, with the same delay.",
                "Retrying forever because the limit is checked after the next request is scheduled.",
                "Classifying a redirect as a failure instead of following its target.",
            ],
            q1=(
                "Why should a 403 be dropped or stopped rather than retried like a 503?",
                "A 403 is a stable refusal that another identical request will not change, while a 503 is usually temporary and can succeed after a bounded wait.",
            ),
            homework=(
                "Write `attempt(statuses, limit)` that prints one decision per status and returns the "
                "final action and attempt count. Run it on two sequences, including at least one 404 and "
                "one 503, print both results, and comment on where the attempt limit took effect."
            ),
            patterns=["404", "503", "for "],
            mapping=(
                "Scrapy's retry middleware has the same shape: status code plus exception type decide "
                "whether a request is rescheduled. Real crawlers also add backoff and jitter so retries "
                "do not arrive in lockstep."
            ),
        ),
        126: dict(
            topic="Sitemaps and feeds",
            idea=(
                "Following links from a homepage is discovery by guessing. Sitemaps and feeds are the "
                "site telling you where its pages are. An XML sitemap lists URLs, often with a last "
                "modified date and a priority, and a feed lists recent items with timestamps and links. "
                "For a crawler these are high-value seeds: they arrive before the crawl, they usually "
                "cover pages that are hard to reach by navigation, and they let you skip a full walk of "
                "the site when you only need the catalogue. The parsing skills are ordinary XML or feed "
                "skills, but the crawl decisions around them are not. A sitemap can be enormous, so you "
                "stream or cap it rather than loading everything into memory. It can contain URLs outside "
                "your scope, stale pages or private sections, so each entry still passes the same scope "
                "and budget checks as a discovered link. It can also be a sitemap index pointing at "
                "other sitemaps, which means the frontier temporarily holds sitemap URLs as well as page "
                "URLs. Feeds add a different rhythm: they are naturally incremental, so a crawler that "
                "remembers the newest timestamp can fetch only what changed. The practical lesson is "
                "that seeds and discovered links should enter the same queue, carrying their source. A "
                "page found through a sitemap and a page found through navigation are the same page, and "
                "deduplication should say so."
            ),
            code=(
                'import xml.etree.ElementTree as ET\n'
                '\n'
                'xml = """<?xml version="1.0"?>\n'
                '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                '  <url><loc>https://shop.test/</loc><priority>1.0</priority></url>\n'
                '  <url><loc>https://shop.test/docs/</loc><priority>0.8</priority></url>\n'
                '  <url><loc>https://shop.test/private/</loc><priority>0.1</priority></url>\n'
                '</urlset>"""\n'
                '\n'
                'ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}\n'
                'root = ET.fromstring(xml)\n'
                'urls = []\n'
                'for node in root.findall("sm:url", ns):\n'
                '    loc = node.findtext("sm:loc", namespaces=ns)\n'
                '    priority = float(node.findtext("sm:priority", "0", ns))\n'
                '    if priority >= 0.5 and not loc.endswith("/private/"):\n'
                '        urls.append(loc)\n'
                'print("sitemap seeds:", urls)\n'
                'assert len(urls) == 2\n'
                'print("priority filter seeded the frontier")'
            ),
            variant_b='raise the priority threshold to 0.9 so only the homepage qualifies',
            variant_c='add a <sitemapindex> example and list the child sitemap URLs instead of pages',
            mistakes=[
                "Treating sitemap URLs as trusted and skipping scope or budget checks.",
                "Loading a multi-megabyte sitemap into memory instead of streaming entries.",
                "Crawling a feed every minute when its entries change only once a day.",
            ],
            q1=(
                "Why should URLs from a sitemap still pass through the normal scope checks?",
                "A sitemap is a claim by the site, not a guarantee; it can list private, stale or off-domain URLs, and the crawler's own policy must still decide what to fetch.",
            ),
            homework=(
                "Write `sitemap_urls(xml_text, min_priority)` that parses a sitemap and returns allowed "
                "locations. Run it on two sitemap strings with different priorities, print both lists, "
                "and comment on which entry the filter removed."
            ),
            patterns=["ET.fromstring", "findall", "loc"],
            mapping=(
                "Search engines begin with robots.txt, which names sitemap locations, then merge those "
                "seeds with link discovery. Scrapy projects often read sitemaps as a starting queue "
                "rather than crawling navigation first."
            ),
        ),
        127: dict(
            topic="Detecting page changes",
            idea=(
                "Most repeated crawls should not re-download the world to learn that nothing changed. "
                "Change detection compares a stable fingerprint of a page with the fingerprint from the "
                "previous run and reports only the difference. The fingerprint is usually a hash of "
                "normalised content, not of raw bytes, because raw HTML churns constantly: session "
                "tokens, timestamps, advertisement slots and whitespace all move without changing what "
                "the reader sees. Normalising whitespace and case before hashing removes a large class "
                "of false positives, and stripping known volatile elements removes another. The result "
                "is a short string per URL that you can store cheaply and compare in one pass. This is "
                "the core of incremental scraping. Instead of treating every run as a fresh dataset, "
                "you keep the previous fingerprints and classify each URL as unchanged, changed, new or "
                "gone. That classification drives very different downstream work: unchanged pages can "
                "be skipped entirely, changed pages need a re-parse and possibly a diff, new pages need "
                "discovery, and gone pages should be marked rather than silently retained. There is a "
                "trade-off between sensitivity and noise. Too aggressive normalisation hides real price "
                "changes; too little turns every rotating banner into an alert. The honest approach is "
                "to decide which fields matter, fingerprint those, and test the detector against two "
                "snapshots where you know exactly what changed."
            ),
            code=(
                'import hashlib\n'
                '\n'
                'def fingerprint(html):\n'
                '    text = " ".join(html.split()).lower()\n'
                '    return hashlib.sha256(text.encode()).hexdigest()[:12]\n'
                '\n'
                'before = {\n'
                '    "https://shop.test/": "<h1> Sale </h1>",\n'
                '    "https://shop.test/about": "<p>Team</p>",\n'
                '}\n'
                'after = {\n'
                '    "https://shop.test/": "<h1>  SALE  </h1>",\n'
                '    "https://shop.test/about": "<p>New team</p>",\n'
                '    "https://shop.test/jobs": "<p>Hiring</p>",\n'
                '}\n'
                'old = {url: fingerprint(html) for url, html in before.items()}\n'
                'new = {url: fingerprint(html) for url, html in after.items()}\n'
                'changed = sorted(u for u in old.keys() & new.keys() if old[u] != new[u])\n'
                'added = sorted(new.keys() - old.keys())\n'
                'removed = sorted(old.keys() - new.keys())\n'
                'print("changed:", changed)\n'
                'print("added:", added, "removed:", removed)\n'
                'assert changed == ["https://shop.test/about"] and not removed\n'
                'print("whitespace noise ignored")'
            ),
            variant_b='change the homepage headline from Sale to Clearance and count it as changed',
            variant_c='remove the about page from the second snapshot and inspect the removed list',
            mistakes=[
                "Hashing raw HTML so rotating tokens and whitespace mark every page as changed.",
                "Storing only the latest hash, losing the ability to say what changed.",
                "Normalising away prices or stock text along with harmless markup noise.",
            ],
            q1=(
                "Why hash normalised text instead of the raw HTML response?",
                "Raw HTML changes for reasons that do not affect content; normalising first makes the fingerprint track meaningful page changes and avoids false alerts.",
            ),
            homework=(
                "Write `diff_pages(before, after)` that fingerprints normalised HTML and returns changed, "
                "added and removed URLs. Run it on two snapshot pairs, print all three lists, and comment "
                "on one kind of noise your normalisation ignores."
            ),
            patterns=["sha256", "changed", "sorted("],
            mapping=(
                "Incremental crawlers store content hashes in the same database as the URL frontier, so "
                "a scheduler can skip unchanged pages. Search engines and price monitors use the same "
                "four-way classification: unchanged, changed, new, gone."
            ),
        ),
        128: dict(
            topic="Logging crawl progress",
            idea=(
                "A crawl is a long-running process, and a long-running process with no output is "
                "indistinguishable from a hung one. Progress logging is not decoration; it is the "
                "instrument panel that tells you whether the frontier is draining, whether failures are "
                "clustering on one host, and whether the crawl will finish before your budget or your "
                "patience runs out. Good log lines are cheap and structured: a timestamp or sequence "
                "number, the URL or host, the status, and running counters. The counters are the part "
                "beginners skip. Without them you can see that a page was fetched but not that forty "
                "percent of requests are returning 403, which is the signal that your scope or user "
                "agent is wrong. With them, the same line answers the important questions at a glance. "
                "Progress should be measured against a denominator you actually have. If the frontier "
                "is open-ended, the percentage is a lie; report pages fetched, queue depth and failure "
                "counts instead. If you do have a bounded seed set, a percentage is useful. The habit "
                "to build is to log one line per page and one summary per batch, and to make the summary "
                "reconcile: fetched should equal ok plus failed plus skipped, and queue depth should "
                "shrink by the number processed. When those numbers do not add up, you have found a "
                "bookkeeping bug before it corrupts the dataset."
            ),
            code=(
                'pages = ["/", "/a", "/b", "/missing", "/c"]\n'
                'stats = {"fetched": 0, "ok": 0, "failed": 0}\n'
                '\n'
                'def log(url, status, stats, total):\n'
                '    pct = round(100 * stats["fetched"] / total)\n'
                '    print(f"{stats[\'fetched\']:>2}/{total} {pct:>3}% {status:<3} {url}")\n'
                '\n'
                'for url in pages:\n'
                '    status = 404 if url == "/missing" else 200\n'
                '    stats["fetched"] += 1\n'
                '    stats["ok" if status == 200 else "failed"] += 1\n'
                '    log(url, status, stats, len(pages))\n'
                '\n'
                'print("summary:", stats)\n'
                'assert stats["fetched"] == stats["ok"] + stats["failed"]\n'
                'print("counters reconcile")'
            ),
            variant_b='make two pages return 503 and watch the failed counter outpace ok',
            variant_c='drop the total denominator and log queue depth instead of a percentage',
            mistakes=[
                "Printing only the URL, so a rising failure rate is invisible until the end.",
                "Computing a percentage from an open-ended frontier that has no true total.",
                "Letting counters diverge from reality because skipped pages are never recorded.",
            ],
            q1=(
                "Which three counters make a crawl log trustworthy at a glance?",
                "Fetched, succeeded and failed, because they both show progress and reconcile to prove no page was lost or double-counted.",
            ),
            homework=(
                "Write `crawl_log(urls, statuses)` that prints one progress line per URL and a final "
                "summary with fetched, ok, failed and percent. Run it on two status lists with different "
                "failure rates, print both summaries, and comment on which counter warned you first."
            ),
            patterns=["fetched", "failed", "print("],
            mapping=(
                "Scrapy emits stats through its stats collector and logs each response at DEBUG level. "
                "Production crawlers ship the same counters to a dashboard so operators can stop a run "
                "that is failing rather than discovering it hours later."
            ),
        ),
        129: dict(
            topic="Checkpoints and failure recovery",
            idea=(
                "Long crawls fail. The process is killed, the machine reboots, the network drops, or a "
                "disk fills. A crawler that keeps its entire state in memory loses every fetched page and "
                "restarts from the seed, which is both wasteful and impolite. Checkpointing is the "
                "discipline of writing enough state to resume: the URLs still waiting, the URLs already "
                "completed, and whatever counters or timestamps the next run needs. The temptation is to "
                "save after every single page, which is safe but slow, or never to save, which is fast "
                "until it is catastrophic. A practical middle ground is a batch or time interval, plus a "
                "final save on a clean stop. The checkpoint format should be boring and inspectable. "
                "JSON is usually enough for a frontier and a done set; a database is better once state is "
                "large or must be shared between workers. The important property is that saving and "
                "loading are exact inverses: whatever you write can be read back into the same two "
                "structures, with no page silently marked done before it was stored. Resume then becomes "
                "ordinary code: load the frontier, load done, seed the seen set from done, and continue "
                "the same loop. Test it by simulating a crash after two pages and proving the third is "
                "the next one fetched. That small test is the difference between a resumable crawler and "
                "a crawler that merely claims to be resumable."
            ),
            code=(
                'import json\n'
                '\n'
                'def checkpoint(frontier, done):\n'
                '    return json.dumps({"frontier": list(frontier), "done": sorted(done)})\n'
                '\n'
                'def restore(blob):\n'
                '    data = json.loads(blob)\n'
                '    return data["frontier"], set(data["done"])\n'
                '\n'
                'frontier = ["/a", "/b", "/c"]\n'
                'done = set()\n'
                'for url in frontier[:2]:\n'
                '    done.add(url)\n'
                'blob = checkpoint(frontier[2:], done)\n'
                'print("saved:", blob)\n'
                '\n'
                'restored_frontier, restored_done = restore(blob)\n'
                'print("resumed with:", restored_frontier, "already done:", sorted(restored_done))\n'
                'assert restored_done == {"/a", "/b"}\n'
                'assert restored_frontier == ["/c"]\n'
                'print("restart skips completed pages")'
            ),
            variant_b='save after only the first page and compare the frontier on resume',
            variant_c='add a "depth" value per pending URL and check it survives the round trip',
            mistakes=[
                "Marking a URL done before its parsed row is safely stored.",
                "Serialising a set directly with json, which raises instead of writing a list.",
                "Saving only the queue, so resumed runs fetch completed pages again.",
            ],
            q1=(
                "Which two pieces of state must a checkpoint preserve to resume correctly?",
                "The pending frontier and the set of completed URLs; together they prevent both lost work and duplicate fetches.",
            ),
            homework=(
                "Write `save_state(frontier, done)` and `load_state(blob)` that round-trip a crawl "
                "frontier through JSON. Simulate a stop after two pages, run recovery on two different "
                "states, and comment on which URL is fetched next after each restart."
            ),
            patterns=["json", "frontier", "done"],
            mapping=(
                "Scrapy's JOBDIR persists requests and dupefilter state so a stopped crawl can resume. "
                "Queue-backed crawlers get the same property by acknowledging a URL only after its row "
                "is committed."
            ),
        ),
        130: dict(
            topic="Avoiding infinite loops",
            idea=(
                "The web is full of cycles. A category links to its products, each product links back to "
                "the category, and a calendar links to next month forever. Without deduplication a "
                "crawler follows those cycles until the budget dies, fetching the same content thousands "
                "of times. The first defence is the seen set you already met, but it only works if the "
                "keys are stable. This is where canonicalisation becomes a safety feature rather than a "
                "tidiness feature: a fragment, a tracking parameter or a trailing slash variant can make "
                "the same page look new on every visit. Some cycles are not duplicate URLs at all. "
                "Pagination that always links to a slightly different query, or a search endpoint that "
                "reflects the current URL into the next link, can generate an unbounded family of "
                "distinct addresses. A seen set cannot stop that alone; you need a depth limit, a "
                "per-prefix cap, or a rule that ignores certain query keys. The right combination is "
                "layered. Canonicalise before checking, record every accepted URL exactly once, cap "
                "depth so the crawl cannot walk forever, and log how many duplicates were blocked. "
                "That last number is diagnostic: zero blocked duplicates on a real site usually means "
                "your canonicalisation is too weak, while a huge number may mean the site is mostly "
                "navigation. Test the crawler on a deliberately cyclic fixture, where the correct result "
                "is a small finite set and a non-zero duplicate count."
            ),
            code=(
                'from collections import deque\n'
                'from urllib.parse import urlsplit, urlunsplit\n'
                '\n'
                'def clean(url):\n'
                '    parts = urlsplit(url)\n'
                '    path = parts.path.rstrip("/") or "/"\n'
                '    return urlunsplit((parts.scheme, parts.netloc, path, "", ""))\n'
                '\n'
                'pages = {\n'
                '    "/": ["/a", "/a#top", "/a?utm_source=x"],\n'
                '    "/a": ["/b", "/"],\n'
                '    "/b": ["/a", "/?page=2"],\n'
                '}\n'
                'frontier = deque(["/"])\n'
                'seen = {"/"}\n'
                'visited, blocked = [], 0\n'
                'while frontier:\n'
                '    url = frontier.popleft()\n'
                '    visited.append(url)\n'
                '    for link in pages.get(url, []):\n'
                '        key = clean(link)\n'
                '        if key in seen:\n'
                '            blocked += 1\n'
                '            continue\n'
                '        seen.add(key)\n'
                '        frontier.append(key)\n'
                '\n'
                'print("visited:", visited)\n'
                'print("duplicates blocked:", blocked)\n'
                'assert len(visited) == 3\n'
                'print("cycle terminated")'
            ),
            variant_b='stop stripping the query and watch /?page=2 create a new frontier entry',
            variant_c='remove the trailing-slash normalisation and predict how /a and /a/ behave',
            mistakes=[
                "Canonicalising after the seen check, so every spelling slips into the frontier first.",
                "Relying on a depth limit alone, which bounds damage but still refetches duplicates.",
                "Stripping all query parameters and accidentally merging distinct paginated pages.",
            ],
            q1=(
                "Why can a seen set fail to stop a cycle even when the same content repeats?",
                "The same content can appear under different URL strings, and the set stores strings; without canonicalisation each spelling looks new.",
            ),
            homework=(
                "Write `crawl_cycles(pages, start)` that canonicalises links, tracks seen URLs and counts "
                "blocked duplicates. Run it on two cyclic page maps, print visited pages and blocked "
                "counts, and comment on which normalisation broke each loop."
            ),
            patterns=["seen", "clean(", "blocked"],
            mapping=(
                "Scrapy's dupefilter plus link canonicalisation is the production version of this loop "
                "guard. Schedulers also cap depth and requests per domain because some sites generate "
                "endless distinct URLs."
            ),
        ),
        131: dict(
            topic="Crawl scope and budgets",
            idea=(
                "Every crawl needs a stopping rule that is chosen before it starts. Without one, the "
                "answer to how many pages to fetch is whatever the site happens to contain, which is "
                "unbounded and often enormous. A budget turns that open question into a bounded job: at "
                "most this many pages, this deep, under this path, for this long. Budgets are not just "
                "resource limits. They are a statement of what the dataset is for. If you are checking "
                "prices across a catalogue, fetching blog posts wastes requests; if you are building a "
                "documentation index, following every product variant is noise. Scope and budget work "
                "together. Scope decides which URLs are eligible, and the budget decides how much of the "
                "eligible set you will actually process. The crawler should record why it stopped, not "
                "merely that it stopped. A run that hit max pages tells you the site is bigger than "
                "expected; a run that exhausted the frontier tells you coverage is complete; a run that "
                "hit max depth tells you content lives deeper than planned. Those are different "
                "engineering facts and they lead to different next actions. Counters for each skip "
                "reason make this visible. The trap is to enforce the budget only at the end, after the "
                "frontier has already ballooned. Check it at discovery time so ineligible or over-budget "
                "URLs never occupy memory. A budget that cannot be explained in one sentence is probably "
                "really two crawls."
            ),
            code=(
                'BUDGET = {"max_pages": 5, "max_depth": 2, "prefix": "/docs/"}\n'
                'links = [("/docs/start", 1), ("/docs/api", 1), ("/blog/post", 1),\n'
                '         ("/docs/api/v2", 2), ("/docs/guide", 2),\n'
                '         ("/docs/api/v2/errors", 3), ("/docs/faq", 2)]\n'
                '\n'
                'visited, skipped = [], []\n'
                'for url, depth in links:\n'
                '    if len(visited) >= BUDGET["max_pages"]:\n'
                '        skipped.append((url, "budget"))\n'
                '    elif depth > BUDGET["max_depth"]:\n'
                '        skipped.append((url, "depth"))\n'
                '    elif not url.startswith(BUDGET["prefix"]):\n'
                '        skipped.append((url, "scope"))\n'
                '    else:\n'
                '        visited.append(url)\n'
                '\n'
                'print("visited:", visited)\n'
                'for url, reason in skipped:\n'
                '    print(f"skip {reason:<6} {url}")\n'
                'assert len(visited) == BUDGET["max_pages"]\n'
                'print("three stop reasons recorded")'
            ),
            variant_b='raise max_depth to 3 and see which previously skipped URL is admitted',
            variant_c='change the prefix to /blog/ and watch the budget fill from a different section',
            mistakes=[
                "Checking the page budget only after fetching, so the crawl always overshoots.",
                "Using a prefix check that matches /docs-old/ because the slash is omitted.",
                "Reporting a stopped crawl as complete without recording which limit fired.",
            ],
            q1=(
                "Why does a budget need a recorded stop reason, not just a page count?",
                "The reason distinguishes an exhausted site from a truncated crawl, which decides whether the dataset is complete or needs another run with a larger budget.",
            ),
            homework=(
                "Write `apply_budget(links, budget)` that returns visited URLs and skip reasons for page, "
                "depth and prefix limits. Run it on two link lists with different budgets, print both "
                "results, and comment on which limit stopped the first one."
            ),
            patterns=["max_pages", "max_depth", "skipped"],
            mapping=(
                "Scrapy projects express this as CLOSESPIDER_PAGECOUNT, DEPTH_LIMIT and URL allow rules. "
                "Schedulers need the same reasons in logs, because a budget stop and a completed crawl "
                "look identical from the output rows alone."
            ),
        ),
        132: dict(
            topic="Throttling concurrent requests",
            idea=(
                "Concurrency and politeness pull in opposite directions. Parallel workers make a crawl "
                "fast, but ten workers aimed at one host can produce a burst that looks exactly like an "
                "attack. Throttling is the mechanism that lets you keep workers busy without exceeding "
                "the rate a host can tolerate. The simplest useful model is a token bucket per host. "
                "Each host has a small number of tokens, one token is spent per request, and tokens "
                "refill at a fixed interval up to a cap. When the bucket is empty the request waits or "
                "is rescheduled, even if other workers are free. This gives you two knobs that mean "
                "different things: the bucket size controls burstiness, and the refill rate controls "
                "sustained load. A large bucket allows a short burst; a small bucket smooths requests "
                "out. Separating hosts is "
                "essential. A global bucket makes one host's limit hold back every other host, which is "
                "the same mistake as a global delay. With per-host buckets, a crawl can run at full "
                "speed across many sites while remaining gentle on each individual one. The remaining "
                "work is observability. Log when a request is allowed and when it is delayed, and count "
                "both, so you can tell whether the throttle is shaping traffic or merely starving the "
                "crawl. In a simulation, a tick counter replaces the wall clock and makes the policy "
                "easy to inspect."
            ),
            code=(
                'requests = ["a/1", "a/2", "a/3", "b/1", "b/2"]\n'
                'CAPACITY = 2\n'
                'REFILL_EVERY = 2\n'
                '\n'
                'buckets = {}\n'
                'allowed, delayed = [], []\n'
                'for tick, req in enumerate(requests):\n'
                '    host = req.split("/")[0]\n'
                '    tokens, last = buckets.get(host, (CAPACITY, 0))\n'
                '    tokens = min(CAPACITY, tokens + (tick - last) // REFILL_EVERY)\n'
                '    if tokens > 0:\n'
                '        buckets[host] = (tokens - 1, tick)\n'
                '        allowed.append((tick, req))\n'
                '    else:\n'
                '        buckets[host] = (tokens, tick)\n'
                '        delayed.append((tick, req))\n'
                '\n'
                'print("allowed:", allowed)\n'
                'print("delayed:", delayed)\n'
                'assert len(allowed) + len(delayed) == len(requests)\n'
                'print("per-host token buckets throttled")'
            ),
            variant_b='set CAPACITY to 1 and compare which a-host requests are delayed',
            variant_c='set REFILL_EVERY to 1 and confirm every request is allowed',
            mistakes=[
                "Using one global bucket so a busy host throttles unrelated hosts.",
                "Refilling tokens on every request instead of by elapsed time.",
                "Letting the bucket grow without a cap, permitting a huge later burst.",
            ],
            q1=(
                "What do bucket capacity and refill interval each control?",
                "Capacity controls how large a burst a host may receive; the refill interval controls the sustained request rate after the burst is spent.",
            ),
            homework=(
                "Write `throttle(requests, capacity, refill_every)` that simulates per-host token "
                "buckets and returns allowed and delayed requests. Run it on two request sequences with "
                "different capacities, print both partitions, and comment on when the first delay hit."
            ),
            patterns=["tokens", "buckets", "delayed"],
            mapping=(
                "Scrapy's AutoThrottle adjusts delay from observed latency, while download slots cap "
                "concurrency per host. Token buckets are the usual lower-level implementation behind "
                "API rate limits and queue schedulers."
            ),
        ),
        133: dict(
            topic="Testing a crawler with fixtures",
            idea=(
                "A crawler that can only be tested against the live web is a crawler you cannot test. "
                "The page changes, the network fails, the site rate-limits you, and the test that passed "
                "yesterday now proves nothing about your code. The alternative is dependency injection "
                "in its simplest form: the crawl loop takes a fetch function instead of calling the "
                "network directly. In production that function performs an HTTP request; in tests it "
                "returns a string from a dictionary of fixtures. The loop under test does not know the "
                "difference, so frontier, deduplication and parsing logic run in milliseconds with exact "
                "expectations. Fixtures let you test cases the live web rarely gives you: an empty page "
                "with no links, a page that links to "
                "itself, a duplicate link in two places, a missing title, a 404. Each fixture encodes a "
                "scenario and an expected result, and together they become a regression suite for the "
                "crawler's behaviour rather than the site's behaviour. This separation is what makes "
                "parsers testable, extended one level up. A useful rule is that the crawl "
                "function accepts two things it does not construct: where to start and how to fetch. "
                "Everything else, including the shape of the output, is its responsibility. When a site "
                "change breaks the parser, you add a fixture that reproduces it and fix the parser until "
                "the suite is green again, with no network and no guessing."
            ),
            code=(
                'PAGES = {\n'
                '    "https://fixture.test/": "<title>Home</title><a href=\\"/a\\">A</a>",\n'
                '    "https://fixture.test/a": "<title>Article</title>",\n'
                '}\n'
                '\n'
                'def fake_fetch(url):\n'
                '    if url not in PAGES:\n'
                '        raise LookupError(url)\n'
                '    return PAGES[url]\n'
                '\n'
                'def crawl(fetch, start):\n'
                '    import re\n'
                '    from collections import deque\n'
                '    queue, seen, titles = deque([start]), {start}, []\n'
                '    while queue:\n'
                '        url = queue.popleft()\n'
                '        html = fetch(url)\n'
                '        title = re.search(r"<title>(.*?)</title>", html).group(1)\n'
                '        titles.append((url, title))\n'
                '        for href in re.findall(r\'href="([^"]+)"\', html):\n'
                '            link = "https://fixture.test" + href\n'
                '            if link not in seen:\n'
                '                seen.add(link)\n'
                '                queue.append(link)\n'
                '    return titles\n'
                '\n'
                'print("run 1:", crawl(fake_fetch, "https://fixture.test/"))\n'
                'empty = lambda url: "<title>Empty</title>"\n'
                'print("run 2:", crawl(empty, "https://fixture.test/"))\n'
                'assert crawl(fake_fetch, "https://fixture.test/")[1][1] == "Article"\n'
                'print("fixtures prove the crawl without a network")'
            ),
            variant_b='add a fixture page that links back to "/" and check it is not fetched twice',
            variant_c='make the second fixture return a page with no title and decide the expected error',
            mistakes=[
                "Calling the HTTP client inside the crawl loop, leaving no seam for a fake fetch.",
                "Making fixtures depend on network order or live content instead of fixed strings.",
                "Testing only the happy path and never a duplicate, empty page or missing field.",
            ],
            q1=(
                "Why should the crawl function receive its fetch function as an argument?",
                "It creates a seam: production passes a network fetcher, tests pass a dictionary-backed fake, and the crawl logic runs identically without the network.",
            ),
            homework=(
                "Write `crawl(fetch, start)` that walks injected pages and returns (url, title) pairs. "
                "Run it with two different fetch fixtures, one with a link cycle and one empty, print "
                "both results, and comment on which fixture exposed the deduplication behaviour."
            ),
            patterns=["fetch", "assert", "deque("],
            mapping=(
                "Scrapy projects test parsers and spiders with saved HTML responses and fake responses "
                "rather than hitting the site. The same seam also lets you replay a real crawl after an "
                "outage to reproduce a bug deterministically."
            ),
        ),
        134: dict(
            topic="Review: a polite crawler",
            idea=(
                "This final day puts the pieces back together: a crawler is not any single one of them. "
                "It is a loop that canonicalises links, filters scope, respects an allow rule, spends a "
                "budget, records progress and stops for a named reason. Each earlier "
                "lesson fixed one failure mode in isolation; the review asks whether they still compose "
                "when they run together. The order of operations is the thing to inspect. A link should "
                "be resolved and canonicalised before it reaches the seen set, or duplicates slip "
                "through. Scope and allow rules should be checked before the URL is queued, or the "
                "frontier fills with work that will be skipped anyway. The budget check belongs at the "
                "same boundary, so the queue never grows past what the run can afford. Politeness belongs "
                "at the moment of fetching, not at the moment of discovery, because the same host can "
                "receive work from many parts of the frontier. The example uses a whitelist to stand in "
                "for a robots.txt decision and a counter to stand in for elapsed time. It is deliberately "
                "small, but the shape is real: every accepted page passes the same gate, and every "
                "rejected one is recorded. The final check is not that the crawler visited a lot of "
                "pages. It is that you can explain, for each page it did not visit, which rule stopped "
                "it and why that rule was the right one for this job."
            ),
            code=(
                'from collections import deque\n'
                'from urllib.parse import urljoin, urlsplit\n'
                '\n'
                'PAGES = {\n'
                '    "/": ["/a", "/b", "/admin", "https://other.test/x"],\n'
                '    "/a": ["/b", "/a?ref=nav"],\n'
                '    "/b": [],\n'
                '    "/admin": ["/"],\n'
                '}\n'
                'ALLOW = ("/", "/a", "/b")\n'
                '\n'
                'def allowed(path):\n'
                '    return any(path == p or path.startswith(p + "/") for p in ALLOW)\n'
                '\n'
                'queue = deque(["https://shop.test/"])\n'
                'seen = {"/"}\n'
                'rows, skipped, clock = [], [], 0\n'
                'while queue:\n'
                '    url = queue.popleft()\n'
                '    parts = urlsplit(url)\n'
                '    path = parts.path or "/"\n'
                '    if parts.netloc != "shop.test" or not allowed(path):\n'
                '        skipped.append((url, "scope"))\n'
                '        continue\n'
                '    clock += 2\n'
                '    rows.append((clock, path))\n'
                '    for link in PAGES.get(path, []):\n'
                '        nxt = urljoin("https://shop.test", link)\n'
                '        nparts = urlsplit(nxt)\n'
                '        key = nparts.path or "/"\n'
                '        if key not in seen:\n'
                '            seen.add(key)\n'
                '            queue.append(nxt)\n'
                '\n'
                'print("crawl:", rows)\n'
                'print("skipped:", skipped)\n'
                'assert [row[1] for row in rows] == ["/", "/a", "/b"]\n'
                'print("polite crawl finished within budget")'
            ),
            variant_b='remove "/b" from ALLOW and confirm it is skipped rather than fetched',
            variant_c='enqueue the external link without the netloc check and watch scope fail',
            mistakes=[
                "Canonicalising after enqueueing, so the seen set stores unclean duplicates.",
                "Enforcing politeness at discovery, where many workers can still hit one host at once.",
                "Reporting a crawl as complete when it actually stopped at a budget or allow rule.",
            ],
            q1=(
                "Why should scope and budget checks happen before a URL enters the queue?",
                "Rejecting early keeps the frontier honest and small; enqueueing first means the crawler stores work it has already decided not to do.",
            ),
            homework=(
                "Write `polite_crawl(pages, seeds, allow, max_pages)` combining canonicalisation, scope "
                "filtering, a seen set and a page budget. Run it on two page maps with different allow "
                "lists, print visited and skipped pages, and comment on which rule stopped each skip."
            ),
            patterns=["deque(", "seen", "skipped"],
            mapping=(
                "This is the skeleton Scrapy fills in with middleware, dupefilters, robots.txt handling "
                "and close signals. Whether you write it by hand or configure a framework, the review "
                "questions are the same: what entered, what was rejected, and why did the run end."
            ),
        ),
    },
)
