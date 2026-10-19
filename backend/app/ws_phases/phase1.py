"""Web Scraping flagship, phase 1: fetching the web, days 75-89.

Every example is stdlib-only and offline. Network behaviour is modelled with
in-memory responses so the decision table can be tested deterministically;
urllib is used for request objects and URL handling, never to open a socket.
"""

PHASE = (
    "Fetching the Web",
    "Turn a URL into a validated, decoded response and a clean record, without hammering the site.",
    {
        75: dict(
            topic="Orientation: a scraper is a pipeline",
            idea=(
                "A scraper is not one clever function; it is a pipeline with named stages. Fetch turns a URL "
                "into a response, decode turns bytes into text, parse turns text into candidate values, "
                "normalize turns those values into typed fields, and store appends one record and its "
                "provenance. Each stage has a contract: what it receives, what it returns, and how it fails. "
                "Keeping the stages separate is what makes the system debuggable, because a wrong price can be "
                "traced to exactly one boundary instead of blamed on the whole script. If ten pages produce zero "
                "rows, the parser is suspect; if rows appear with empty titles, normalization is suspect; if the "
                "same URL appears twice, the store's deduplication is suspect. A pipeline also lets you replace a "
                "part without rewriting the rest: an HTTP client can become a browser session, or a hand-written "
                "parser can become BeautifulSoup, while the record shape and storage stay identical. Today's "
                "example builds the skeleton on an in-memory archive, so no network can distract from the design. "
                "Notice that every stage takes a value and returns a value rather than mutating hidden state. That "
                "purity is a testability decision. Write the stages on one page before you write a crawler; the "
                "crawler is only this pipeline inside a loop."
            ),
            code=(
                'pages = {\n'
                '    "https://shop.example/1": "<h1>Dune</h1><span>$9.99</span>",\n'
                '    "https://shop.example/2": "<h1>Foundation</h1><span>$12.50</span>",\n'
                '}\n'
                '\n'
                'def fetch(url, archive):\n'
                '    return archive[url]\n'
                '\n'
                'def parse(html):\n'
                '    title = html.split("<h1>")[1].split("</h1>")[0]\n'
                '    price = float(html.split("<span>$")[1].split("</span>")[0])\n'
                '    return {"title": title, "price": price}\n'
                '\n'
                'def store(row, url):\n'
                '    return {**row, "source": url}\n'
                '\n'
                'rows = []\n'
                'for url in pages:\n'
                '    rows.append(store(parse(fetch(url, pages)), url))\n'
                '\n'
                'print("fetched:", len(pages), "| stored:", len(rows))\n'
                'for row in rows:\n'
                '    print(row["title"], row["price"], row["source"])\n'
                'required = {"title", "price", "source"}\n'
                'assert all(set(row) == required for row in rows)\n'
                'print("every row carries its source")'
            ),
            variant_b='add a third page with an empty title and decide whether it becomes a row or a failure',
            variant_c='make parse return None for a page without a price and count the dropped pages',
            mistakes=[
                "Fetching and parsing in one function, so the parser cannot be tested on saved pages.",
                "Losing the source URL, which makes every later data question impossible to trace.",
                "Letting one bad page abort the loop and discard the pages that parsed correctly.",
            ],
            q1=("Why does the pipeline keep fetch and parse in separate functions?",
                "Each stage can be tested and replaced alone: fetch can be simulated offline while the parser is exercised on fixtures."),
            homework=(
                "Write `run_pipeline(archive)` that fetches each URL from a dictionary, parses title and price, "
                "and returns records with a source field. Run it on two different archives, print the row counts, "
                "and comment which line keeps the stages independent."
            ),
            patterns=["def ", "print("],
            mapping=(
                "This fetch, parse, normalize, store skeleton is the shape of every later scraper; requests or "
                "Scrapy replace one stage at a time without changing the record contract."
            ),
        ),
        76: dict(
            topic="HTTP is a request and a response",
            idea=(
                "HTTP is a text conversation with two messages. The client sends a request: a method such as GET, "
                "a path and query, a version, then headers, then an optional body. The server answers with a "
                "status line, its own headers, and usually a body. That is the entire protocol at the level a "
                "scraper cares about. Once you see a request as a string, several confusing behaviours become "
                "obvious. The path is not the same as the full URL; the Host header supplies the domain. The method "
                "decides whether a body is expected. Headers are case-insensitive names with values that may "
                "repeat. The body's length is described by Content-Length or by chunked framing, not by where the "
                "HTML happens to end. A response can be a redirect, an error page, or a binary file, and the status "
                "line is the first clue about which. Reading raw messages is also the fastest way to debug a client "
                "library. When a request fails, print the method, URL, headers and status before guessing. Today "
                "you construct a request and parse a response from strings, proving that the shape you send "
                "matches the shape you receive. The exact wire format will become invisible behind urllib, "
                "requests or a browser, but it never stops being what happens."
            ),
            code=(
                'from urllib.parse import urlsplit\n'
                '\n'
                'url = "https://shop.example/books?page=2"\n'
                'parts = urlsplit(url)\n'
                'request = "\\r\\n".join([\n'
                '    f"GET {parts.path}?{parts.query} HTTP/1.1",\n'
                '    f"Host: {parts.netloc}",\n'
                '    "User-Agent: school-scraper/1.0",\n'
                '    "Accept: text/html",\n'
                '])\n'
                'print(request.replace("\\r\\n", "\\n"))\n'
                '\n'
                'raw = ("HTTP/1.1 200 OK\\r\\n"\n'
                '       "Content-Type: text/html; charset=utf-8\\r\\n"\n'
                '       "Content-Length: 32\\r\\n\\r\\n"\n'
                '       "<html><title>Dune</title></html>")\n'
                'head, _, body = raw.partition("\\r\\n\\r\\n")\n'
                'lines = head.split("\\r\\n")\n'
                'version, code, reason = lines[0].split(" ", 2)\n'
                'headers = {k.strip().lower(): v.strip()\n'
                '           for k, v in (line.split(":", 1) for line in lines[1:])}\n'
                'print("status:", code, reason, "| version:", version)\n'
                'print("content-type:", headers["content-type"])\n'
                'assert int(headers["content-length"]) == len(body)\n'
                'print("body length matches the declared content-length")'
            ),
            variant_b='change the method to HEAD and drop the body, then explain what Content-Length means',
            variant_c='use a URL with a port, e.g. https://shop.example:8443/books, and print the Host header',
            mistakes=[
                "Treating the path as the whole URL and omitting the Host header.",
                "Associating a response body with a request before checking the status line.",
                "Splitting headers on every colon, which corrupts values that contain a colon.",
            ],
            q1=("Why does the Host header matter when the path is already in the request line?",
                "One server address can host many sites: Host tells the server which site's content to return for that path."),
            homework=(
                "Write `show_exchange(url, raw)` that prints the request line and parses a raw response into "
                "status, headers and body. Run it on two raw responses, print both parsed results, and comment "
                "which line separates headers from the body."
            ),
            patterns=["split(", "print("],
            mapping=(
                "urllib, requests and browser devtools all show this same exchange; when a site behaves oddly, "
                "the raw request and response are the ground truth."
            ),
        ),
        77: dict(
            topic="Status codes tell the truth",
            idea=(
                "Status codes are the server's summary of what happened, and they are more trustworthy than the "
                "body. A 200 means the request succeeded; the body should contain what you asked for. A 301 or 302 "
                "means the resource moved, and the Location header names the new address; following it is part of "
                "fetching, not a parser bug. A 304 means your cached copy is still current. A 404 means the "
                "resource is gone and retrying will not help. A 429 means you are asking too fast. A 500 or 503 "
                "means the server failed, possibly temporarily. The first digit carries the meaning: 2xx success, "
                "3xx redirection, 4xx client mistake, 5xx server failure. Scrapers break when they check only for "
                "exceptions and never for the status code, because many servers return a perfectly valid HTML page "
                "explaining the error with a 404 or 403 status. If you parse that page as if it were the product "
                "page, you record error text as data. The fix is a single gate right after the response arrives: "
                "accept 2xx, follow a bounded number of redirects, and classify everything else into skip, wait, or "
                "report. Today you build that table from a list of simulated responses and print the action for "
                "each. The table is the contract your future fetch layer must honour."
            ),
            code=(
                'raw_statuses = [\n'
                '    "HTTP/1.1 200 OK",\n'
                '    "HTTP/1.1 301 Moved Permanently",\n'
                '    "HTTP/1.1 404 Not Found",\n'
                '    "HTTP/1.1 429 Too Many Requests",\n'
                '    "HTTP/1.1 503 Service Unavailable",\n'
                ']\n'
                '\n'
                'def action(status):\n'
                '    if 200 <= status < 300:\n'
                '        return "parse the body"\n'
                '    if 300 <= status < 400:\n'
                '        return "follow Location once"\n'
                '    if status == 404:\n'
                '        return "skip permanently"\n'
                '    if status == 429:\n'
                '        return "wait, then retry"\n'
                '    if 500 <= status < 600:\n'
                '        return "retry later, with a cap"\n'
                '    return "report for a human"\n'
                '\n'
                'for line in raw_statuses:\n'
                '    version, code, reason = line.split(" ", 2)\n'
                '    status = int(code)\n'
                '    print(status, reason, "->", action(status))\n'
                'assert action(301) != action(404) and action(503) == "retry later, with a cap"\n'
                'print("status classes map to different actions")'
            ),
            variant_b='add 403 Forbidden and 304 Not Modified, then argue which action each deserves',
            variant_c='add 204 No Content and notice that a successful response can still have no body',
            mistakes=[
                "Treating every non-empty body as success and ignoring the status code.",
                "Retrying a 404, which wastes requests because the resource is permanently absent.",
                "Following redirects forever instead of limiting the chain length.",
            ],
            q1=("Why is a 200 status not proof that the page contains the data you wanted?",
                "The request succeeded, but the server may have returned a soft 404, a consent page or a changed layout that your selector cannot read."),
            homework=(
                "Write `decide(status)` returning parse, follow, skip, wait or report for each status class. "
                "Run it on two lists of codes, print every decision, and comment which line prevents a permanent "
                "404 from being retried."
            ),
            patterns=["if ", "return"],
            mapping=(
                "Requests exposes response.status_code and Scrapy exposes response.status; both are checked "
                "before any selector runs, and both feed the retry middleware."
            ),
        ),
        78: dict(
            topic="Headers: who you are, what you accept",
            idea=(
                "Headers are how a request introduces itself and how a response describes what it returned. On the "
                "request side, User-Agent identifies the client, Accept lists the representations you can handle, "
                "Accept-Language states preferences, and Referer says where you came from. On the response side, "
                "Content-Type tells you how to read the body, Content-Language tells you which audience it serves, "
                "and Cache-Control, ETag and Last-Modified describe how long it may be reused. Two habits separate "
                "reliable scrapers from rude ones. First, send an honest User-Agent with a contact URL or address; "
                "anonymous default clients are the ones sites block first. Second, ask for what you can actually "
                "parse. If you send Accept: application/json but only know how to parse HTML, a server that "
                "honours the header will hand you JSON and your parser will fail. Header names are case-insensitive, "
                "values may contain quality weights such as text/html;q=0.9, and servers may ignore your "
                "preferences entirely. That is why the response's Content-Type, not the request's Accept, decides "
                "how you decode. Treat every header value as a claim to verify against the response, not as a "
                "command. Today you build a request header set, negotiate a representation, and read a response "
                "header case-insensitively."
            ),
            code=(
                'def build_headers(accept, language, contact):\n'
                '    return {\n'
                '        "User-Agent": f"school-scraper/1.0 (+{contact})",\n'
                '        "Accept": accept,\n'
                '        "Accept-Language": language,\n'
                '    }\n'
                '\n'
                'def preferred(accept):\n'
                '    choices = []\n'
                '    for part in accept.split(","):\n'
                '        media, _, quality = part.strip().partition(";q=")\n'
                '        choices.append((float(quality) if quality else 1.0, media.strip()))\n'
                '    return max(choices)[1]\n'
                '\n'
                'request_headers = build_headers(\n'
                '    "text/html;q=0.8, application/json;q=0.9", "en", "https://example.org/bot")\n'
                'print("user-agent:", request_headers["User-Agent"])\n'
                'print("accept:", request_headers["Accept"])\n'
                'print("preferred type:", preferred(request_headers["Accept"]))\n'
                '\n'
                'response_headers = {"Content-Type": "application/json; charset=utf-8"}\n'
                'lowered = {name.lower(): value for name, value in response_headers.items()}\n'
                'print("response content-type:", lowered["content-type"])\n'
                'assert preferred(request_headers["Accept"]) == "application/json"\n'
                'print("headers are case-insensitive and quality-aware")'
            ),
            variant_b='ask for text/html with q=1.0 and application/json with q=0.5, then compare the choice',
            variant_c='drop the contact URL from the User-Agent and say what a site operator loses',
            mistakes=[
                "Sending a fake browser User-Agent while still scraping, which misrepresents the client.",
                "Declaring Accept: application/json but decoding the response as HTML when the server obeys.",
                "Reading response header names with exact case, so Content-Type and content-type look different.",
            ],
            q1=("Why does the response Content-Type override what you put in Accept?",
                "Accept is a preference the server may ignore; the response header states what was actually sent, so it controls decoding."),
            homework=(
                "Write `request_headers(accept, language, contact)` and `pick_type(accept)` that build and rank "
                "representations. Run it on two Accept strings, print the chosen types, and comment which line "
                "applies the quality weight."
            ),
            patterns=["def ", "return"],
            mapping=(
                "requests accepts a headers dictionary; Scrapy sets DEFAULT_REQUEST_HEADERS. A truthful "
                "User-Agent plus a realistic Accept is the baseline of being a good citizen."
            ),
        ),
        79: dict(
            topic="Query strings and URL building",
            idea=(
                "URLs are structured, and query strings are the part scrapers get wrong most often. A URL has a "
                "scheme, a host, a path, a query and a fragment; the fragment never reaches the server, so it must "
                "not be used as a cache key or pagination state. The query is a sequence of key-value pairs, but "
                "it is not a dictionary: keys can repeat, order can matter to some servers, and values must be "
                "percent-encoded. Spaces become %20 or plus signs, non-ASCII characters become UTF-8 bytes in "
                "percent form, and reserved characters such as & and = must be escaped when they are data. "
                "Building URLs by f-strings works until a search term contains an ampersand and silently creates a "
                "new parameter. The professional habit is to build with urlencode and read with parse_qs or "
                "parse_qsl, then inspect the result. Pagination deserves special care: page numbers, cursors, sort "
                "keys and filters all live in the query, and a crawler that increments page but forgets the filter "
                "will wander into unrelated results. Today you construct a filtered, paginated URL, round-trip it "
                "through parsing, and confirm that repeated filters survive. The assertion is the point: if "
                "encoding loses a value, the bug appears here rather than three hundred requests later."
            ),
            code=(
                'from urllib.parse import parse_qs, urlencode, urlsplit\n'
                '\n'
                'base = "https://shop.example/search"\n'
                'params = [\n'
                '    ("q", "dune & foundation"),\n'
                '    ("page", 1),\n'
                '    ("tag", "sci-fi"),\n'
                '    ("tag", "classic"),\n'
                ']\n'
                'url = base + "?" + urlencode(params)\n'
                'print("built:", url)\n'
                '\n'
                'page_two = [("q", "dune & foundation"), ("page", 2),\n'
                '            ("tag", "sci-fi"), ("tag", "classic")]\n'
                'print("page 2:", base + "?" + urlencode(page_two))\n'
                '\n'
                'parsed = parse_qs(urlsplit(url).query)\n'
                'print("search term:", parsed["q"][0])\n'
                'print("tags:", parsed["tag"])\n'
                'round_trip = parse_qs(urlencode(params))\n'
                'assert round_trip["tag"] == ["sci-fi", "classic"]\n'
                'assert round_trip["q"] == ["dune & foundation"]\n'
                'print("reserved characters and repeated keys survive")'
            ),
            variant_b='add a cursor parameter with a base64-looking value and confirm it is not mangled',
            variant_c='put the same parameters in a different order and check whether the server-visible URL changes',
            mistakes=[
                "Building query strings with f-strings, so a value containing & creates an extra parameter.",
                "Using a dictionary when a key repeats, which silently drops every tag but the last.",
                "Including the fragment in the request URL, where the server can never see it.",
            ],
            q1=("Why is a query string better represented as a list of pairs than as a dictionary?",
                "Keys such as tag can repeat, and a dictionary would keep only one value while the server may honour all of them."),
            homework=(
                "Write `search_url(base, term, page, tags)` that builds an encoded URL with repeated tag values. "
                "Run it on two terms and tag lists, print both URLs and their parsed queries, and comment which "
                "line escapes the ampersand."
            ),
            patterns=["urlencode(", "print("],
            mapping=(
                "Requests takes a params dictionary or list of tuples; Scrapy forms URLs the same way. The URL "
                "you encode is the URL the server logs, so correctness here is both technical and courteous."
            ),
        ),
        80: dict(
            topic="Text, bytes and encoding",
            idea=(
                "HTTP delivers bytes, and bytes become text only when you choose an encoding. Two sources claim to "
                "know the encoding: the Content-Type header's charset parameter and a meta tag inside the HTML. The "
                "header wins when present because it describes the actual transfer; the meta tag is a fallback for "
                "files and misconfigured servers. Decode once, explicitly, at the boundary. Guessing with "
                "errors='replace' hides corruption by turning unknown bytes into question marks, and errors='ignore' "
                "deletes evidence entirely. A wrong decode produces mojibake such as Ã© where é should be, and the "
                "damage survives into your database, where it looks like a content problem rather than a fetch "
                "problem. Byte length and character length are also different: UTF-8 uses one to four bytes per "
                "code point, so slicing bytes by character count corrupts multi-byte sequences. Store the decoded "
                "string, keep the raw bytes only when debugging or when the content is genuinely binary. Normalise "
                "whitespace and Unicode forms once, early, so every downstream stage sees one representation. Today "
                "you read a declared charset, decode strictly, compare byte and character lengths, and deliberately "
                "decode the same bytes with the wrong encoding to see mojibake appear. Recognising that pattern on "
                "sight is a practical skill."
            ),
            code=(
                'body = "Café — 9,99 €".encode("utf-8")\n'
                'content_type = "text/html; charset=utf-8"\n'
                '\n'
                'def charset_of(content_type, body):\n'
                '    if "charset=" in content_type:\n'
                '        return content_type.split("charset=")[1].split(";")[0].strip()\n'
                '    return "utf-8"\n'
                '\n'
                'encoding = charset_of(content_type, body)\n'
                'text = body.decode(encoding)\n'
                'wrong = body.decode("latin-1")\n'
                'print("declared:", encoding)\n'
                'print("text:", text)\n'
                'print("characters:", len(text), "| bytes:", len(body))\n'
                'print("wrong decode looks like:", wrong)\n'
                'assert text.count("é") == 1 and len(body) > len(text)\n'
                'print("decode once, with the charset the response declared")'
            ),
            variant_b='change the header to charset=iso-8859-1 and decode the same bytes, then compare',
            variant_c='remove the charset parameter and fall back to a meta tag declaring utf-8',
            mistakes=[
                "Decoding with errors='ignore', which deletes the evidence that the encoding was wrong.",
                "Slicing the byte string by character count before decoding, which splits multi-byte characters.",
                "Letting each downstream stage re-decode the raw bytes with its own guess.",
            ],
            q1=("Why should the Content-Type charset win over a meta tag inside the page?",
                "The header describes the bytes actually transferred; a meta tag may belong to a different saved copy or be stale."),
            homework=(
                "Write `decode_response(body, content_type)` that selects the declared charset, decodes strictly, "
                "and normalises whitespace. Run it on two byte fixtures with different charsets, print the text and "
                "lengths, and comment which line decides the encoding."
            ),
            patterns=["decode(", "print("],
            mapping=(
                "Requests exposes response.encoding and response.text; urllib leaves decoding to you. Both reward "
                "the same discipline: inspect the headers first, decode once, and never let mojibake into storage."
            ),
        ),
        81: dict(
            topic="HTML anatomy: elements, attributes, text",
            idea=(
                "HTML is a tree, but you read it as a stream of events: a start tag with a name and attributes, "
                "text, an end tag, comments, entities. An element is a tag plus its attributes plus its content; "
                "attributes carry data that is not visible on the page, such as identifiers, classes, links and "
                "data-* values. Text may contain entities like &amp; or &nbsp;, which the parser decodes, and "
                "whitespace that the browser collapses. Scrapers fail when they assume structure that is not there: "
                "a missing attribute, a nested element that changes the text content, or two cards with the same "
                "class. The robust approach is to identify the smallest stable anchor, often a data attribute "
                "rather than a visual class, then extract fields relative to it. Print the parsed structure before "
                "writing selectors, because what you imagine the markup says and what the parser sees are "
                "frequently different. Attributes are also where provenance hides: a product id in data-sku is more "
                "reliable than a title string. Today you parse a small card list with the standard library's "
                "HTMLParser, capture tag names, attributes and text, and turn each card into a dictionary. The "
                "output shows why a parser is not the same as a regular expression: nesting and entities are "
                "handled, and the record shape is explicit."
            ),
            code=(
                'from html.parser import HTMLParser\n'
                '\n'
                'page = (\'<article class="card" data-sku="A1"><h2>Dune &amp; Sons</h2>\'\n'
                '        \'<span class="price">$9.99</span></article>\'\n'
                '        \'<article class="card" data-sku="B2"><h2>Foundation</h2>\'\n'
                '        \'<span class="price">$12.50</span></article>\')\n'
                '\n'
                'class Cards(HTMLParser):\n'
                '    def __init__(self):\n'
                '        super().__init__()\n'
                '        self.cards = []\n'
                '        self.current = None\n'
                '        self.field = None\n'
                '    def handle_starttag(self, tag, attrs):\n'
                '        attrs = dict(attrs)\n'
                '        if tag == "article":\n'
                '            self.current = {"sku": attrs.get("data-sku"), "title": "", "price": ""}\n'
                '            self.cards.append(self.current)\n'
                '        elif tag == "h2":\n'
                '            self.field = "title"\n'
                '        elif tag == "span" and attrs.get("class") == "price":\n'
                '            self.field = "price"\n'
                '    def handle_endtag(self, tag):\n'
                '        if tag in ("h2", "span"):\n'
                '            self.field = None\n'
                '    def handle_data(self, data):\n'
                '        if self.current and self.field:\n'
                '            self.current[self.field] += data.strip()\n'
                '\n'
                'parser = Cards()\n'
                'parser.feed(page)\n'
                'for card in parser.cards:\n'
                '    print(card)\n'
                'assert parser.cards[0]["title"] == "Dune & Sons"\n'
                'print("parsed", len(parser.cards), "cards with attributes and decoded text")'
            ),
            variant_b='add a card without a data-sku attribute and print None instead of guessing an id',
            variant_c='add a nested <b> inside the h2 and see how text collection changes',
            mistakes=[
                "Selecting on a visual class that a redesign can rename overnight.",
                "Ignoring attributes and reconstructing an id by splitting the title string.",
                "Assuming text has no entities or nested tags, so titles arrive with markup inside them.",
            ],
            q1=("Why is a data-sku attribute a better anchor than the card's CSS class?",
                "The class describes appearance and changes with design; the data attribute identifies the record and is usually stable across redesigns."),
            homework=(
                "Write `parse_cards(html)` using HTMLParser to return one dictionary per article with sku, title "
                "and price. Run it on two pages, print every record, and comment which handler turns text into a "
                "field value."
            ),
            patterns=["class ", "def ", "print("],
            mapping=(
                "BeautifulSoup exposes the same tag, attribute and text model with a friendlier API; CSS selectors "
                "and XPath are shorthand over this tree. Learn the anatomy first, then the selector syntax."
            ),
        ),
        82: dict(
            topic="Fetching with urllib.request",
            idea=(
                "urllib.request is the standard library's HTTP client. The central object is Request: you give it a "
                "URL, optional headers, an optional body and a method, and it represents the message you intend to "
                "send. urlopen then performs the network exchange and returns a response object with status, "
                "headers and a readable body. For scraping, that means four steps: build a Request with an honest "
                "User-Agent, open it with a timeout, check the status, and read the body as bytes. Each step is a "
                "place to fail differently. A malformed URL fails before any network call; a DNS or connection "
                "failure happens inside urlopen; a non-2xx status returns a response whose body may still be "
                "readable; a slow server needs a timeout or the script hangs. urlopen raises HTTPError for error "
                "statuses, and HTTPError is also a response, so the error path must read it deliberately rather "
                "than discard it. The response object is a context manager, and reading it twice requires care. "
                "Today the example builds a real Request and inspects its method, URL and headers, then sends it to "
                "a simulated transport that returns a fixture. The network call is replaced, not imitated: the "
                "object shape you debug is the one urlopen would consume."
            ),
            code=(
                'from urllib.parse import urlencode\n'
                'from urllib.request import Request\n'
                '\n'
                'fixtures = {\n'
                '    "https://shop.example/books?page=2": b"<h1>Page 2</h1>",\n'
                '}\n'
                '\n'
                'def transport(request):\n'
                '    if request.full_url not in fixtures:\n'
                '        raise KeyError("no fixture for " + request.full_url)\n'
                '    return fixtures[request.full_url]\n'
                '\n'
                'url = "https://shop.example/books?" + urlencode({"page": 2})\n'
                'request = Request(url, headers={"User-Agent": "school-scraper/1.0"}, method="GET")\n'
                'print("method:", request.get_method())\n'
                'print("url:", request.full_url)\n'
                'print("headers:", request.headers)\n'
                '\n'
                'body = transport(request)\n'
                'print("body:", body.decode("utf-8"))\n'
                'print("bytes:", len(body))\n'
                'assert request.get_method() == "GET" and body.startswith(b"<h1>")\n'
                'print("request built; transport is the only network seam")'
            ),
            variant_b='send method="HEAD" and an extra Accept header, then inspect the Request again',
            variant_c='request a URL with a missing fixture and print the KeyError instead of a crash trace',
            mistakes=[
                "Calling urlopen without a timeout, so one stalled server blocks the whole run.",
                "Reading the body before checking the status, which parses error pages as data.",
                "Building the Request without a User-Agent and wondering why the site returns 403.",
            ],
            q1=("What does the Request object represent before any network call happens?",
                "The message you intend to send: its URL, method, headers and optional body, which urlopen then transmits."),
            homework=(
                "Write `build_request(url, page, agent)` that returns a urllib Request with a query string and "
                "headers. Run it on two URLs, print each method, full_url and headers, and comment which line is "
                "the only place a real network call would occur."
            ),
            patterns=["Request(", "print("],
            mapping=(
                "urlopen is fine for a script, while requests wraps the same exchange with sessions and friendlier "
                "errors; Scrapy's downloader sits behind both. The Request contract is universal."
            ),
        ),
        83: dict(
            topic="Timeouts and bounded retries",
            idea=(
                "Networks are slow and unreliable, so every fetch needs a ceiling. A timeout says how long one "
                "attempt may take; without it a single unresponsive server can stall an entire crawl. Retries "
                "handle transient failures, but they must be bounded and selective. Retry a timeout, a connection "
                "reset, a 429 or a 5xx; do not retry a 404, a 401 or a 403, because waiting will not change the "
                "answer. Cap the number of attempts and the total elapsed time, and increase the delay between "
                "attempts so a struggling server is not hit in a tight loop. The simplest policy is a small fixed "
                "number of tries with a short backoff; the professional policy also records every attempt so the "
                "run summary can distinguish one flaky page from a site-wide outage. Be careful with non-idempotent "
                "requests: retrying a GET is safe, retrying a POST that creates an order is not. Today you model a "
                "fetch that times out twice and then succeeds. The example counts attempts, respects a per-attempt "
                "timeout, and raises a clear error when the budget is exhausted. The numbers are simulated so the "
                "output is deterministic, but the decision table is exactly the one a real client uses."
            ),
            code=(
                'outcomes = [("timeout", None), ("timeout", None), ("ok", 200)]\n'
                '\n'
                'def fetch(outcomes, max_attempts=3, timeout=2.0):\n'
                '    for attempt, (kind, status) in enumerate(outcomes[:max_attempts], 1):\n'
                '        if kind == "timeout":\n'
                '            print(f"attempt {attempt}: no response after {timeout}s")\n'
                '            continue\n'
                '        print(f"attempt {attempt}: status {status}")\n'
                '        return status\n'
                '    raise TimeoutError("retry budget exhausted")\n'
                '\n'
                'try:\n'
                '    print("final:", fetch(outcomes))\n'
                'except TimeoutError as error:\n'
                '    print("failed:", error)\n'
                '\n'
                'try:\n'
                '    fetch([("timeout", None)] * 3)\n'
                'except TimeoutError as error:\n'
                '    print("bounded failure:", error)\n'
                '\n'
                'assert fetch([("timeout", None), ("ok", 200)]) == 200\n'
                'print("retries stop at the cap and after success")'
            ),
            variant_b='set max_attempts=2 on the three-outcome list and watch the successful third attempt disappear',
            variant_c='add a 404 outcome and explain why the retry loop should stop immediately instead of trying again',
            mistakes=[
                "Retrying forever, which turns one bad URL into an unbounded load on the server.",
                "Retrying a 404 or 403, where the answer is permanent and waiting changes nothing.",
                "Setting a timeout but no overall deadline, so many slow attempts still stall the run.",
            ],
            q1=("Why should a 404 not be retried while a 503 may be?",
                "A 404 says the resource is permanently absent, while a 503 says the server is temporarily unable to serve it."),
            homework=(
                "Write `fetch_with_retry(outcomes, max_attempts, timeout)` that logs each attempt and raises after "
                "the budget. Run it on two outcome lists, print the logs, and comment which line stops a permanent "
                "failure from consuming every retry."
            ),
            patterns=["def ", "TimeoutError", "print("],
            mapping=(
                "requests uses timeout= and urllib passes timeout= to urlopen; both can be wrapped in a retry "
                "adapter. Scrapy's RetryMiddleware does the same bounded loop with configurable statuses."
            ),
        ),
        84: dict(
            topic="Sessions and cookies",
            idea=(
                "Sessions exist because HTTP is stateless. Each request arrives without memory of the last, so "
                "servers use cookies to recognise a returning client. A response sends Set-Cookie with a name, "
                "value, and attributes such as Path, Domain, Expires, Max-Age, Secure and HttpOnly. The client "
                "stores the cookie and sends it back in a Cookie header on matching requests. That is how logins, "
                "carts, consent banners and CSRF protection work. A scraper that ignores cookies will appear to be "
                "a new visitor on every request, which can break pagination, trigger repeated consent walls, or "
                "lose an authenticated view. A scraper that copies cookies carelessly can leak a session or violate "
                "a site's expectations. The practical rules are: keep one cookie jar per identity, respect expiry "
                "and path, never log secret cookie values, and do not reuse a logged-in session for unrelated work. "
                "When a site requires a browser flow, a real browser session may be the honest tool; when it does "
                "not, a small jar and a consistent User-Agent are enough. Today you parse Set-Cookie headers, build "
                "a jar, and show the Cookie header that the next request would carry. The example also demonstrates "
                "why a fresh jar produces a different request."
            ),
            code=(
                'from http.cookies import SimpleCookie\n'
                '\n'
                'jar = {}\n'
                '\n'
                'def absorb(set_cookie):\n'
                '    parsed = SimpleCookie()\n'
                '    parsed.load(set_cookie)\n'
                '    for name, morsel in parsed.items():\n'
                '        jar[name] = morsel.value\n'
                '        print("stored", name, "path", morsel["path"] or "/")\n'
                '\n'
                'def cookie_header():\n'
                '    return "; ".join(f"{name}={value}" for name, value in sorted(jar.items()))\n'
                '\n'
                'absorb("session=abc123; Path=/; HttpOnly")\n'
                'absorb("currency=EUR; Path=/books")\n'
                'print("jar:", sorted(jar))\n'
                'print("next request Cookie:", cookie_header())\n'
                'assert jar["session"] == "abc123"\n'
                'print("cookie state carried into the next request")'
            ),
            variant_b='add a cookie with Max-Age=0 and remove it from the jar instead of sending it again',
            variant_c='use two separate jars and show that a login in one does not affect the other',
            mistakes=[
                "Sending every cookie to every host, including cookies scoped to another domain.",
                "Logging session identifiers in plain text where they can leak into shared output.",
                "Assuming a cookie is permanent when it expires or is replaced by Set-Cookie on a later response.",
            ],
            q1=("Why does a cookie need a Path and Domain attribute rather than being sent everywhere?",
                "Those attributes scope the cookie to the requests that need it, limiting leakage and preventing unrelated hosts from receiving it."),
            homework=(
                "Write `Session` with `absorb(set_cookie)` and `headers()` that store cookies and build the Cookie "
                "header. Run it on two sequences of Set-Cookie lines, print both next-request headers, and comment "
                "which line keeps each session's state separate."
            ),
            patterns=["def ", "print("],
            mapping=(
                "requests.Session and Scrapy's cookie middleware keep a jar automatically; a real browser does the "
                "same plus JavaScript-set cookies. Keep identity per session, not per request."
            ),
        ),
        85: dict(
            topic="robots.txt and polite scraping",
            idea=(
                "robots.txt is a site's published crawling policy. It lives at the root of the host, lists "
                "user-agent groups, and gives Allow and Disallow rules for paths, sometimes with Crawl-delay and "
                "Sitemap entries. A scraper should fetch it before crawling, choose the group that matches its "
                "User-Agent, and obey the most specific rule. The standard library's RobotFileParser can parse the "
                "file and answer can_fetch, which is enough for the common cases. What robots.txt is not: it is not "
                "authorization, not a licence, and not a substitute for reading the terms of service. It cannot "
                "protect a page you have no right to access, and it does not override authentication or copyright. "
                "Conversely, a permissive robots.txt does not mean unlimited requests; politeness still requires "
                "rate limits, caching and an identifiable User-Agent. Disallow rules also interact with wildcards "
                "and path matching, and a naive prefix check can disagree with a real crawler. Treat the parser as "
                "advice, then apply judgement: if the page is private, personal or clearly against the site's "
                "terms, stop. Today you parse a small robots.txt from memory, test several paths against two user "
                "agents, and print the decisions. The output makes the rules concrete, including the difference "
                "between a missing rule and an explicit Allow."
            ),
            code=(
                'from urllib.robotparser import RobotFileParser\n'
                '\n'
                'lines = [\n'
                '    "User-agent: SchoolScraper",\n'
                '    "Disallow: /admin",\n'
                '    "Allow: /admin/public",\n'
                '    "Crawl-delay: 2",\n'
                '    "",\n'
                '    "User-agent: *",\n'
                '    "Disallow: /private",\n'
                ']\n'
                '\n'
                'parser = RobotFileParser()\n'
                'parser.parse(lines)\n'
                'for agent, path in [\n'
                '    ("SchoolScraper", "/admin/secret"),\n'
                '    ("SchoolScraper", "/admin/public/report"),\n'
                '    ("SchoolScraper", "/books"),\n'
                '    ("OtherBot", "/private/data"),\n'
                ']:\n'
                '    print(agent, path, "->", parser.can_fetch(agent, path))\n'
                'print("crawl delay for SchoolScraper:", parser.crawl_delay("SchoolScraper"))\n'
                'assert not parser.can_fetch("SchoolScraper", "/admin/secret")\n'
                'assert parser.can_fetch("SchoolScraper", "/admin/public/report")\n'
                'print("rules applied, including the explicit allow")'
            ),
            variant_b='add "User-agent: OtherBot" with Disallow: / and show that its access differs',
            variant_c='remove Crawl-delay and fall back to your own fixed request interval',
            mistakes=[
                "Fetching robots.txt once and assuming it never changes while a long crawl runs.",
                "Treating a missing Disallow rule as permission to ignore the terms of service.",
                "Ignoring Crawl-delay and sending requests as fast as the event loop allows.",
            ],
            q1=("Does a permissive robots.txt give you permission to scrape any page?",
                "No: it expresses crawling preferences only, while terms of service, copyright, privacy and authentication still apply."),
            homework=(
                "Write `allowed(robots_text, agent, path)` that parses rules and returns a decision plus crawl "
                "delay. Run it on two robots files with different agents, print every decision, and comment which "
                "line selects the agent-specific group."
            ),
            patterns=["RobotFileParser(", "print("],
            mapping=(
                "Scrapy respects ROBOTSTXT_OBEY; requests has no built-in policy, so you implement it. Either way, "
                "robots.txt is the start of politeness, not the end of it."
            ),
        ),
        86: dict(
            topic="JSON APIs: the easier path",
            idea=(
                "Many sites offer a JSON API behind the page you were about to scrape, and using it is usually the "
                "better engineering choice. A JSON endpoint returns structured data, stable field names and "
                "pagination metadata instead of markup you must reverse-engineer. The flow is still HTTP: build the "
                "URL, send headers, check the status, read the body, and decode it with json.loads. Once parsed, a "
                "JSON object is a dictionary and a list is a list, so you index by name rather than by selector. "
                "That does not make the data trustworthy. Fields can be missing, null, renamed or typed "
                "inconsistently; pagination can use page numbers, cursors or next URLs; rate limits and "
                "authentication still apply. A robust parser uses .get with defaults, validates the fields it needs, "
                "and stops when the next-page marker is absent or repeated. It also inspects the Content-Type, "
                "because an HTML error page served with a 200 status will make json.loads fail with a confusing "
                "message. Today you parse a paginated JSON response from a fixture, turn items into records, and "
                "construct the next request from the response's own link rather than guessing the page number. That "
                "last choice is what keeps a crawler correct when the API changes its pagination scheme."
            ),
            code=(
                'import json\n'
                'from urllib.parse import urljoin\n'
                '\n'
                'payload = json.dumps({\n'
                '    "items": [{"title": "Dune", "price": 9.99}, {"title": "Foundation"}],\n'
                '    "next": "/api/books?page=2&limit=2",\n'
                '})\n'
                'data = json.loads(payload)\n'
                'rows = [\n'
                '    {"title": item.get("title", ""), "price": item.get("price", 0.0)}\n'
                '    for item in data.get("items", [])\n'
                ']\n'
                'print("records:", rows)\n'
                '\n'
                'base = "https://api.example"\n'
                'next_url = urljoin(base, data.get("next", ""))\n'
                'print("next request:", next_url)\n'
                'assert len(rows) == 2 and rows[1]["price"] == 0.0\n'
                'assert next_url.startswith("https://api.example/api/books?")\n'
                'print("missing fields defaulted; next link taken from the response")'
            ),
            variant_b='change next to an absolute URL and confirm urljoin leaves it untouched',
            variant_c='remove the next key and make the loop stop instead of requesting page 2',
            mistakes=[
                "Guessing page numbers instead of following the API's own next cursor or link.",
                "Indexing item['price'] when optional fields may be absent, so one bad item kills the page.",
                "Calling json.loads on an error page without first checking the status and Content-Type.",
            ],
            q1=("Why should a crawler follow the API's next link instead of incrementing a page number?",
                "The server owns the pagination scheme; following its link survives cursor changes and skipped or filtered pages."),
            homework=(
                "Write `items_from_json(text, base)` that parses a page, defaults missing fields, and returns "
                "records plus the next URL. Run it on two payloads with different next forms, print both, and "
                "comment which line avoids guessing the next page."
            ),
            patterns=["json.loads(", "print("],
            mapping=(
                "Requests offers response.json() and Scrapy offers response.json; both are json.loads with a "
                "Content-Type assumption. Prefer the documented API over reverse-engineering HTML."
            ),
        ),
        87: dict(
            topic="Rate limits and backoff",
            idea=(
                "Rate limits are part of the contract, not an obstacle to defeat. A server may allow a fixed number "
                "of requests per minute, per token or per connection, and it signals the limit with a 429 status "
                "and often a Retry-After header. The correct response is to wait at least that long, reduce "
                "concurrency, and retry a bounded number of times. Exponential backoff means doubling the delay "
                "after each failure, with a cap so the crawl does not sleep for hours; jitter means adding a small "
                "random offset so many workers do not retry in lockstep. A 503 with Retry-After is similar but may "
                "indicate maintenance rather than quota. The wrong responses are to rotate proxies to evade the "
                "limit, to hammer harder, or to treat the limit as a parser bug. Those behaviours turn a technical "
                "problem into an ethical and legal one. Good scrapers also budget the whole run: a maximum number "
                "of requests, a maximum wall-clock time, and a clear stop condition. Today you simulate a sequence "
                "of 429, 429 and 200 responses, read Retry-After when present, fall back to a capped "
                "exponential delay, and print the wait plan. The example never sleeps, so the schedule is visible "
                "and testable; in production the same numbers feed time.sleep."
            ),
            code=(
                'responses = [\n'
                '    (429, {"Retry-After": "2"}),\n'
                '    (429, {"Retry-After": "5"}),\n'
                '    (200, {}),\n'
                ']\n'
                '\n'
                'total_wait = 0\n'
                'for attempt, (status, headers) in enumerate(responses, 1):\n'
                '    if status == 200:\n'
                '        print(f"attempt {attempt}: 200 OK, continue crawling")\n'
                '        break\n'
                '    if "Retry-After" in headers:\n'
                '        delay = int(headers["Retry-After"])\n'
                '    else:\n'
                '        delay = min(2 ** attempt, 30)\n'
                '    total_wait += delay\n'
                '    print(f"attempt {attempt}: {status}, wait {delay}s (total {total_wait}s)")\n'
                '\n'
                'print("total delay:", total_wait)\n'
                'assert total_wait == 7\n'
                'print("wait plan respects Retry-After and stays bounded")'
            ),
            variant_b='replace Retry-After with a missing header and compare the exponential delays',
            variant_c='add a cap of 4 seconds on every delay and print the new total',
            mistakes=[
                "Retrying a 429 immediately, which increases the load that caused the limit.",
                "Sleeping for Retry-After but ignoring that several workers will wake at the same moment.",
                "Raising concurrency to compensate for throttling instead of lowering it.",
            ],
            q1=("Why is Retry-After more trustworthy than your own backoff calculation when it is present?",
                "The server knows when it can serve you again; its stated delay is the minimum that respects that limit."),
            homework=(
                "Write `wait_plan(responses)` that returns delays for each 429 and stops on 200. Run it on two "
                "response sequences, print the plans and totals, and comment which line prefers Retry-After over "
                "the exponential fallback."
            ),
            patterns=["for ", "print("],
            mapping=(
                "Requests users add Retry or tenacity; Scrapy has AUTOTHROTTLE and Retry-After support. The "
                "principle is constant: slow down, cap the wait, and stop when the budget is gone."
            ),
        ),
        88: dict(
            topic="Caching fetched pages",
            idea=(
                "Caching is the cheapest speedup and the politest optimization in scraping. If the same URL is "
                "requested twice in a short window, the second request wastes bandwidth, adds load, and can push "
                "you toward a rate limit. A cache maps a normalized URL to a stored response and a timestamp; a "
                "lookup returns the stored body when it is fresh and refetches when it is stale. The key must be "
                "normalized: lowercase the host, drop the fragment, sort query parameters when order is not "
                "meaningful, and decide deliberately whether tracking parameters belong. Otherwise "
                "/books?page=1 and /books?page=1&utm_source=x become different entries and the cache misses. A "
                "time-to-live is a policy choice, not a universal constant; prices need minutes, documentation can "
                "last hours or days. HTTP offers finer tools: ETag and Last-Modified enable conditional requests, "
                "and a 304 response refreshes the cache without resending the body. Persist the cache if a crawl "
                "spans restarts, but version its format. Never cache errors, redirects or partial bodies as if they "
                "were success. Today you build a tiny URL cache with a TTL, print hit and miss decisions, and show "
                "a stale entry being refetched. The timestamps are simulated so the middle step is visible."
            ),
            code=(
                'from urllib.parse import urlsplit, urlunsplit\n'
                '\n'
                'cache = {}\n'
                '\n'
                'def normalize(url):\n'
                '    parts = urlsplit(url)\n'
                '    return urlunsplit((parts.scheme.lower(), parts.netloc.lower(),\n'
                '                       parts.path or "/", parts.query, ""))\n'
                '\n'
                'def fetch(url, now, ttl=60):\n'
                '    key = normalize(url)\n'
                '    if key in cache and now - cache[key][0] < ttl:\n'
                '        print("HIT ", key)\n'
                '        return cache[key][1]\n'
                '    print("MISS", key)\n'
                '    body = f"<h1>{key}</h1>"\n'
                '    cache[key] = (now, body)\n'
                '    return body\n'
                '\n'
                'first = fetch("https://Shop.example/books?page=1#top", 100)\n'
                'second = fetch("https://shop.example/books?page=1", 130)\n'
                'third = fetch("https://shop.example/books?page=1", 175)\n'
                'print("cache entries:", len(cache))\n'
                'assert first == second and second == third\n'
                'print("fresh copy reused, stale copy refetched under the same key")'
            ),
            variant_b='set ttl=20 and check whether the request at t=130 becomes a miss',
            variant_c='add a different query parameter and show a second cache entry instead of a hit',
            mistakes=[
                "Caching by the raw URL, so fragments and host casing create duplicate entries.",
                "Serving stale data forever because the cache has no expiry or revalidation rule.",
                "Caching an error page or a partial download and treating it as a valid response.",
            ],
            q1=("Why must the URL be normalized before it becomes a cache key?",
                "Equivalent spellings would otherwise create separate entries, causing needless refetches and inconsistent stored bodies."),
            homework=(
                "Write `cached_fetch(url, now, ttl)` with URL normalization and hit/miss reporting. Run it on two "
                "URL spellings at two timestamps, print every decision, and comment which line makes the fragment "
                "irrelevant to the key."
            ),
            patterns=["def ", "print("],
            mapping=(
                "requests-cache and Scrapy's HTTPCACHE middleware implement this with disk storage and conditional "
                "requests; the key hygiene and TTL policy are exactly what you write by hand here."
            ),
        ),
        89: dict(
            topic="Review: fetch a page correctly",
            idea=(
                "The review day is a checklist applied to one page. Start with the URL: is it absolute, correctly "
                "encoded, and free of fragments that never reach the server? Send a request with a truthful "
                "User-Agent and an Accept header you can actually handle. Apply a timeout and a bounded retry "
                "policy, and follow redirects only within a limit. Check the status before touching the body, "
                "because error pages are still HTML. Read the Content-Type, honour its charset, and decode strictly; "
                "compare the byte count with the character count if something looks odd. Parse with an anchor that "
                "is stable, extract typed fields, and keep the source URL and fetch time beside them. Validate the "
                "record: required keys present, numbers actually numeric, no empty title. Cache the response if the "
                "same URL will be needed again, and respect robots.txt and the site's rate limit. Finally, log what "
                "happened — status, bytes, duration, retries — so the next failure has evidence. Today's example "
                "performs this whole sequence against a simulated response: build the URL, construct headers, fetch "
                "a fixture, verify status and type, decode, parse a title, and return a record with provenance. "
                "Every stage is small enough to test, which is the real lesson of the phase."
            ),
            code=(
                'from html.parser import HTMLParser\n'
                'from urllib.parse import urlencode\n'
                '\n'
                'class Title(HTMLParser):\n'
                '    def __init__(self):\n'
                '        super().__init__()\n'
                '        self.inside = False\n'
                '        self.text = ""\n'
                '    def handle_starttag(self, tag, attrs):\n'
                '        if tag == "title":\n'
                '            self.inside = True\n'
                '    def handle_endtag(self, tag):\n'
                '        if tag == "title":\n'
                '            self.inside = False\n'
                '    def handle_data(self, data):\n'
                '        if self.inside:\n'
                '            self.text += data\n'
                '\n'
                'def fetch(url):\n'
                '    body = "<html><title>Dune — €9.99</title></html>".encode("utf-8")\n'
                '    return {"status": 200,\n'
                '            "headers": {"content-type": "text/html; charset=utf-8"},\n'
                '            "body": body}\n'
                '\n'
                'def scrape(base, query):\n'
                '    url = base + "?" + urlencode(query)\n'
                '    response = fetch(url)\n'
                '    if response["status"] != 200:\n'
                '        raise ValueError("bad status " + str(response["status"]) + " for " + url)\n'
                '    charset = response["headers"]["content-type"].split("charset=")[1]\n'
                '    text = response["body"].decode(charset)\n'
                '    parser = Title()\n'
                '    parser.feed(text)\n'
                '    return {"title": parser.text, "url": url}\n'
                '\n'
                'record = scrape("https://shop.example/books", {"page": 2, "q": "dune"})\n'
                'print(record)\n'
                'assert record["title"] == "Dune — €9.99" and "q=dune" in record["url"]\n'
                'print("page checked, decoded and parsed into one record")'
            ),
            variant_b='change the response status to 404 and confirm the record is refused before parsing',
            variant_c='change the charset to iso-8859-1 and watch the decode assertion fail, then fix the fixture',
            mistakes=[
                "Parsing before checking the status, so an error page becomes a record with nonsense fields.",
                "Keeping the response body as bytes all the way into storage, where text comparisons fail.",
                "Omitting provenance, so a bad record cannot be traced back to the URL that produced it.",
            ],
            q1=("Why does the final function check status and charset before constructing a record?",
                "Both determine whether the bytes are the page you asked for and how to read them; parsing first records garbage as data."),
            homework=(
                "Write `scrape_page(base, query)` that builds the URL, checks a simulated response, decodes by "
                "Content-Type, parses the title and returns provenance. Run it on two query sets, print both "
                "records, and comment which line prevents an error response from becoming data."
            ),
            patterns=["def ", "print("],
            mapping=(
                "This checklist is what requests plus BeautifulSoup, Scrapy or a browser automation script must "
                "still satisfy underneath: correct URL, honest headers, bounded fetch, status gate, charset, "
                "stable selector and provenance."
            ),
        ),
    },
)
