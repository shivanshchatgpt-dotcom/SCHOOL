"""Web Scraping phase 2, days 90-104: parsing HTML into records.

Every example runs offline on in-memory HTML fixtures and uses only the
standard library, so the applier can execute it without a network. The point
is the parsing model, not a particular library: the same node selection,
text cleaning and record building appears later in BeautifulSoup, lxml and
Scrapy code.
"""

PHASE = (
    "Parsing HTML",
    "Turn scraped HTML strings into clean, stable records with stdlib parsing, selection, and extraction habits that transfer directly to BeautifulSoup, lxml, and Scrapy.",
    {
        90: dict(
            topic="Parsing with html.parser",
            idea=(
                "A scraped page arrives as one long string, and the first useful act is to stop treating it "
                "as text. Python's html.parser walks that string and calls methods on your object as it meets "
                "start tags, end tags, and character data. You subclass HTMLParser, call feed with the markup, "
                "and collect state in attributes you control. The callback named handle_starttag receives the "
                "tag name and a list of attribute pairs, handle_data receives text in chunks, and handle_endtag "
                "closes the element. That is the whole contract. There is no tree unless you build one, which "
                "is exactly why the standard library parser is a good first teacher: you feel the responsibility "
                "that libraries usually hide. A common first mistake is to assume handle_data gives you a "
                "complete text node; it may arrive in several pieces, so append to a buffer and join at the end. "
                "Remember also to call super().__init__(), or the parser's internal bookkeeping never starts. "
                "Today's fixture is small on purpose. The habit to install is simple: one parser class, one "
                "piece of page state, one list of extracted values, and a printed assertion proving the parse "
                "did what you claimed. Keep the class small enough that every callback can be explained in one sentence."
            ),
            code="""from html.parser import HTMLParser

class HeadlineParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_h2 = False
        self.buffer = []
        self.headlines = []

    def handle_starttag(self, tag, attrs):
        if tag == "h2":
            self.in_h2 = True
            self.buffer = []

    def handle_data(self, data):
        if self.in_h2:
            self.buffer.append(data)

    def handle_endtag(self, tag):
        if tag == "h2" and self.in_h2:
            text = " ".join("".join(self.buffer).split())
            if text:
                self.headlines.append(text)
            self.in_h2 = False

html = "<h2>Dune</h2><p>9.99</p><h2>Foundation &amp; Empire</h2>"
parser = HeadlineParser()
parser.feed(html)
print("headlines:", parser.headlines)
assert parser.headlines == ["Dune", "Foundation & Empire"]
print("parsed", len(parser.headlines), "headlines")
""",
            variant_b="put a span inside the second h2 and confirm its text is still joined",
            variant_c="add an empty h2 containing only spaces and decide whether it should be a headline",
            mistakes=[
                "Forgetting super().__init__(), so the parser's internal state is never initialised.",
                "Assuming handle_data arrives once per element instead of buffering the chunks.",
                "Reaching for a regex over tags when the standard parser already exposes attributes cleanly.",
            ],
            q1=(
                "Why must text from handle_data be buffered before it becomes a field?",
                "HTMLParser may deliver one text node in several chunks, so joining at the closing tag prevents silently truncated values.",
            ),
            homework=(
                "Write `extract_headlines(html)` using an HTMLParser subclass that collects every h2, normalises "
                "whitespace, and skips empty text. Run it on two different HTML fixtures, print both lists, and "
                "comment which line proves the parser state was reset for each heading."
            ),
            patterns=["HTMLParser", "handle_starttag", "print("],
            mapping=(
                "BeautifulSoup wraps this same event stream in a tree and gives you select; lxml does it in C. "
                "Knowing the callbacks makes a surprising selector result explainable instead of mysterious."
            ),
        ),
        91: dict(
            topic="The parser is event-driven",
            idea=(
                "The parser has no opinion about structure; it reports events in the order they appear. That "
                "ordering is the real model behind every HTML API you will use. A start event opens an element, "
                "text events fill it, and an end event closes it, but malformed pages can violate the pairing. "
                "To reason about nesting you keep your own depth counter: increment on a normal start tag, "
                "decrement on an end tag, and record the depth with each event. Now the log tells a story you "
                "can debug. Text inside a div is deeper than text inside the body, a sibling starts at the same "
                "depth, and a child is one level deeper. Void elements such as br and img never close, so they "
                "must not increment depth, and self-closing syntax reaches handle_startendtag instead of the "
                "two callbacks. Libraries such as BeautifulSoup build a tree from these same events; lxml uses "
                "a faster parser but exposes the same parent-child relationships. When a selector later returns "
                "a surprise, print the event log at the suspect subtree and read the nesting aloud. Most "
                "selection bugs are depth bugs in disguise: the text you wanted was one level outside the node "
                "you matched. Today you produce that log with no library and prove the opening event comes "
                "first."
            ),
            code="""from html.parser import HTMLParser

VOID = {"br", "img", "hr", "meta", "input", "link"}

class EventLog(HTMLParser):
    def __init__(self):
        super().__init__()
        self.events = []
        self.depth = 0

    def handle_starttag(self, tag, attrs):
        self.events.append(("start", tag, self.depth))
        if tag not in VOID:
            self.depth += 1

    def handle_endtag(self, tag):
        self.depth = max(0, self.depth - 1)
        self.events.append(("end", tag, self.depth))

    def handle_data(self, data):
        text = data.strip()
        if text:
            self.events.append(("text", text, self.depth))

    def handle_startendtag(self, tag, attrs):
        self.events.append(("self", tag, self.depth))

html = "<div><p>Hello <b>world</b></p><br><p>Bye</p></div>"
parser = EventLog()
parser.feed(html)
for kind, value, depth in parser.events:
    print(kind, value, "depth", depth)
assert parser.events[0] == ("start", "div", 0)
print("events:", len(parser.events))
""",
            variant_b="replace br with a self-closing img and check the event kind it produces",
            variant_c="insert a stray end tag and decide what the depth counter should do",
            mistakes=[
                "Incrementing depth for void elements, so every following sibling looks one level too deep.",
                "Treating start and end events as guaranteed pairs instead of validating the stack.",
                "Forgetting that text may be split across events and assuming one event per node.",
            ],
            q1=(
                "Why does a void element need special treatment in a depth counter?",
                "It has no closing event, so incrementing depth for br or img leaves the counter permanently one level too high.",
            ),
            homework=(
                "Write `event_trace(html)` that logs start, end and text events with a depth number, skipping void "
                "closes. Run it on two fixtures, one balanced and one with a stray end tag, print both traces, "
                "and comment which line shows the nesting error first."
            ),
            patterns=["handle_starttag", "handle_endtag", "print("],
            mapping=(
                "BeautifulSoup's tree is built from these events; lxml exposes the same opening and closing "
                "relationships faster. Printing an event trace is a portable way to debug any parser."
            ),
        ),
        92: dict(
            topic="Find one node vs find all",
            idea=(
                "Scrapers ask two different questions that look similar: what is the first price on this page, "
                "and what are all the prices? The first question wants one record and is allowed to stop looking "
                "after the first match; the second wants a complete list. Mixing them up produces subtle bugs. "
                "If a helper always returns a list, callers start indexing it, and an empty page raises IndexError "
                "far from the parser. If a helper returns only the first match when the task needed every card, "
                "the dataset is silently short and no error ever appears. Make the contract explicit in the "
                "function name and in the return type. A first-match helper returns a value or None; an all-match "
                "helper returns a list, possibly empty. Both are honest. The parser itself can collect everything "
                "and the caller can choose, but then the stopping rule is invisible and memory grows on huge "
                "pages. For a listing page, collect all and count. For a detail page with a canonical title, "
                "first match is exactly right. The quality check differs too: first match checks for None, all "
                "match checks the count against the number of cards you expected. Today's fixture contains two "
                "spans with the same class so the difference is visible in one print statement. Say which "
                "contract your function offers before you write its body."
            ),
            code="""from html.parser import HTMLParser

class PriceParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.prices = []
        self.in_price = False
        self.buffer = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "span" and "price" in attrs.get("class", "").split():
            self.in_price = True
            self.buffer = []

    def handle_data(self, data):
        if self.in_price:
            self.buffer.append(data)

    def handle_endtag(self, tag):
        if tag == "span" and self.in_price:
            self.prices.append("".join(self.buffer).strip())
            self.in_price = False

html = '<h1>Dune</h1><span class="price">$9.99</span><span class="price">$19.99</span>'
parser = PriceParser()
parser.feed(html)
first = parser.prices[0] if parser.prices else None
print("all prices:", parser.prices)
print("first price:", first)
assert first == "$9.99" and len(parser.prices) == 2
print("first and all selected from one parse")
""",
            variant_b="use a fixture with no price span and print the first-match value",
            variant_c="put one price span inside another and compare the all-match count",
            mistakes=[
                "Returning a list from a first-match helper, forcing callers to index and crash on empty pages.",
                "Returning only the first match while the task visibly needs every repeated block.",
                "Forgetting that nested matches can double-count the same value in an all-match helper.",
            ],
            q1=(
                "When should a parser helper return one value instead of a list?",
                "When the page has one canonical value such as a detail title; a first-match contract returns a value or None and never forces callers to index.",
            ),
            homework=(
                "Write `first_price(html)` and `all_prices(html)` with explicit contracts, returning None or an "
                "empty list rather than raising. Run both on two fixtures, one with two prices and one with none, "
                "print all results, and comment which line distinguishes the two contracts."
            ),
            patterns=["def ", "return", "print("],
            mapping=(
                "BeautifulSoup offers find for one node and find_all for many; Scrapy selectors have get and getall. "
                "The first-versus-all contract is the same decision in every library."
            ),
        ),
        93: dict(
            topic="Selecting by tag, class and attribute",
            idea=(
                "A tag name alone is rarely a selector; p appears everywhere. Classes narrow the match, and data "
                "attributes often carry the stable identifier a scraper actually needs. The class attribute is a "
                "space-separated list, not a single string, so the correct test is membership after splitting, "
                "not a substring check. The substring check looks harmless until card matches cardboard and your "
                "dataset quietly gains unrelated rows. Data attributes such as data-sku or data-product-id are "
                "usually placed for scripts and integrations, which makes them more stable than visual classes. "
                "Still, treat them as claims to verify, not magic keys. A good selector combines several "
                "predicates: the element is an article, it carries the card class, and it has a data-sku. Each "
                "predicate removes ambiguity, and the set of predicates documents what the page fragment means. "
                "When the site redesigns, the failure is local and readable. The alternative, a long chain of "
                "nth-child positions, breaks when one banner is inserted. Today's parser converts the attribute "
                "list to a dictionary once, checks membership in the class list, and requires the data attribute "
                "before starting a record. The fixture includes a decoy article so a selector that only checks "
                "the tag fails loudly in the assertion."
            ),
            code="""from html.parser import HTMLParser

class CardParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_card = False
        self.sku = None
        self.buffer = []
        self.records = []

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        classes = attributes.get("class", "").split()
        if tag == "article" and "card" in classes and "data-sku" in attributes:
            self.in_card = True
            self.sku = attributes["data-sku"]
            self.buffer = []

    def handle_data(self, data):
        if self.in_card:
            self.buffer.append(data)

    def handle_endtag(self, tag):
        if tag == "article" and self.in_card:
            title = " ".join("".join(self.buffer).split())
            self.records.append({"sku": self.sku, "title": title})
            self.in_card = False

html = ('<article class="card" data-sku="A1"><h3>Dune</h3><span>$9.99</span></article>'
        '<article class="card promo" data-sku="B2"><h3>Foundation</h3></article>'
        '<article class="note"><h3>Skip me</h3></article>')
parser = CardParser()
parser.feed(html)
print("cards:", parser.records)
assert len(parser.records) == 2 and parser.records[0]["sku"] == "A1"
print("selected", len(parser.records), "cards by tag, class and attribute")
""",
            variant_b="require data-sku on the promo card and remove it to watch the card disappear",
            variant_c="change the decoy article to class card without data-sku and explain the count",
            mistakes=[
                "Testing class with a substring, so card also matches cardboard and unrelated markup.",
                "Checking only the tag name, which floods the result with every article on the page.",
                "Reading an absent data attribute directly instead of testing membership first.",
            ],
            q1=(
                "Why is `'card' in attrs['class']` wrong even when it happens to work?",
                "It is a substring test, so classes such as cardboard or card-wide match too; splitting the class value and testing membership is exact.",
            ),
            homework=(
                "Write `select_cards(html)` that keeps only articles with the card class and a data-sku "
                "attribute, returning sku and flattened text. Run it on two fixtures, one with a decoy article, "
                "print both result lists, and comment which predicate removes the decoy."
            ),
            patterns=["get(\"class\"", "split()", "print("],
            mapping=(
                "BeautifulSoup spells this soup.select('article.card[data-sku]'); lxml uses XPath or CSS through "
                "cssselect. The predicate set, not the syntax, is the durable skill."
            ),
        ),
        94: dict(
            topic="CSS-selector thinking",
            idea=(
                "A CSS selector is a compact description of a node: a tag, a class, an id, an attribute, and a "
                "relationship to ancestors. Writing selectors well is mostly about choosing which of those facts "
                "is stable. The browser's copy-selector command produces something like div:nth-child(3) > "
                "div:nth-child(2) > span, which is precise today and useless after a layout change. A better "
                "selector names the semantic container and the role inside it: article.card h3, or "
                "span.price[data-currency]. Descendant means any depth, while the child combinator means exactly "
                "one level, and confusing them creates both misses and duplicates. Specificity matters when two "
                "rules could match: an id beats a class, and a longer compound beats a short one, which is why a "
                "selector that works in the browser console can still surprise you in a scraper with a smaller "
                "document. For parsing, the practical rule is to prefer the shortest selector that is still "
                "unambiguous, then assert the match count. If a selector returns three nodes where you expected "
                "one, the selector is not necessarily broken; the page may genuinely repeat the block, and your "
                "record model needs to say so. Today you implement a tiny tag-dot-class matcher and compare it "
                "with a class-agnostic one to see the ambiguity appear."
            ),
            code="""from html.parser import HTMLParser

class Selector(HTMLParser):
    def __init__(self, selector):
        super().__init__()
        self.tag, _, self.cls = selector.partition(".")
        self.matches = []
        self.depth = 0
        self.open_depth = None
        self.buffer = []

    def handle_starttag(self, tag, attrs):
        classes = dict(attrs).get("class", "").split()
        self.depth += 1
        if self.open_depth is None and tag == self.tag and (not self.cls or self.cls in classes):
            self.open_depth = self.depth
            self.buffer = []

    def handle_data(self, data):
        if self.open_depth is not None:
            self.buffer.append(data)

    def handle_endtag(self, tag):
        if self.open_depth == self.depth and tag == self.tag:
            self.matches.append(" ".join("".join(self.buffer).split()))
            self.open_depth = None
        self.depth -= 1

html = ('<div class="card"><h2>Dune</h2></div>'
        '<div class="card wide"><h2>Foundation</h2></div>'
        '<div class="note"><h2>Ignore</h2></div>')
parser = Selector("div.card")
parser.feed(html)
print("div.card ->", parser.matches)
assert parser.matches == ["Dune", "Foundation"]
print("selector matched", len(parser.matches), "blocks")
""",
            variant_b="use the selector div without a class and explain why the note block joins the result",
            variant_c="rename one class to card-wide and decide whether the exact class matcher should include it",
            mistakes=[
                "Copying a browser nth-child selector that breaks as soon as one banner is inserted.",
                "Confusing descendant matching with direct-child matching, so nested blocks are counted twice.",
                "Writing a selector with no expected match count, so an over-broad match looks like success.",
            ],
            q1=(
                "Why is a copied nth-child selector fragile for scraping?",
                "It encodes visual position rather than meaning, so any inserted banner or reordered block silently changes what it selects.",
            ),
            homework=(
                "Write `select_text(html, selector)` supporting tag and tag.class, returning flattened text for "
                "every match. Run it with two selectors on one fixture, print both results, and comment which "
                "selector is more stable against a layout change."
            ),
            patterns=["partition(", "handle_starttag", "print("],
            mapping=(
                "BeautifulSoup's select and Scrapy's css both accept this selector language; lxml supports it via "
                "cssselect. Prefer semantic classes and attributes over positional chains."
            ),
        ),
        95: dict(
            topic="Extracting text without noise",
            idea=(
                "Asking for an element's text usually returns more than the words a human sees. Script and style "
                "contents are text nodes, comments are not visible, and inline markup fragments a sentence into "
                "several data events. A naive join can also glue words together, turning 'Frank' and 'Herbert' "
                "into 'FrankHerbert' because the space lived in the markup between them. The first job is to "
                "exclude nodes that never belong in visible copy: script, style, noscript, and often template. The "
                "second is to normalise whitespace after extraction, collapsing runs of spaces, tabs and newlines "
                "into single spaces, then trimming the ends. The third is to preserve deliberate separation "
                "between block elements so two paragraphs do not become one word salad. BeautifulSoup's get_text "
                "has a separator argument for exactly this reason. Hidden elements are harder: display none is a "
                "styling decision, and an HTML parser does not run CSS, so a scraper cannot always know what a "
                "browser would hide. Accept that limit and use the rendered page only when visibility truly "
                "matters. Today's fixture mixes a heading, a script, a paragraph with irregular spacing, and a "
                "style block; the assertion checks that the script source is absent and that the visible author "
                "name survived intact."
            ),
            code="""from html.parser import HTMLParser

class VisibleText(HTMLParser):
    def __init__(self):
        super().__init__()
        self.skip = 0
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "noscript"):
            self.skip += 1

    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript") and self.skip:
            self.skip -= 1

    def handle_data(self, data):
        if not self.skip:
            self.parts.append(data)

html = ('<h1>Dune</h1><script>var price = 9.99;</script>'
        '<p>Frank   Herbert</p><style>.x { color: red; }</style>')
parser = VisibleText()
parser.feed(html)
text = " ".join(" ".join(parser.parts).split())
print("visible text:", text)
assert "var price" not in text and "Frank Herbert" in text
print("visible words:", len(text.split()))
""",
            variant_b="add a noscript block with fallback copy and decide whether it is visible text",
            variant_c="add two paragraphs and check that the normalisation keeps a space between them",
            mistakes=[
                "Joining data chunks with an empty string, which fuses words that markup separated.",
                "Including script and style contents, so CSS and JavaScript pollute extracted copy.",
                "Normalising only leading and trailing spaces while leaving internal runs untouched.",
            ],
            q1=(
                "Why can a parser not reliably drop elements hidden with CSS?",
                "CSS is applied by a rendering engine after parsing; an HTML parser sees the markup but not the computed display value.",
            ),
            homework=(
                "Write `visible_text(html)` that skips script, style and noscript content, joins block text with "
                "spaces, and collapses whitespace. Run it on two fixtures, one with a script and one with nested "
                "inline tags, print both strings, and comment which line removes the script noise."
            ),
            patterns=["script", "split()", "print("],
            mapping=(
                "BeautifulSoup's get_text(separator=' ') and lxml's text_content do this job; Scrapy users often "
                "call selector.css('::text').getall() and join the pieces. Normalise in one place."
            ),
        ),
        96: dict(
            topic="Tables into rows",
            idea=(
                "A table is the friendliest structure on the web because it already declares its own column "
                "names. The header row holds th cells, each data row holds td cells, and the mapping from header "
                "to value is the record you want. Parse the rows first, then treat the first row as keys and every "
                "later row as values. Do not hard-code column positions; sites reorder columns, and a positional "
                "parser silently swaps title and price. Two details ruin naive table scrapers. First, rows can "
                "have different cell counts because of malformed markup, merged cells, or a missing value, and "
                "zip simply truncates, hiding the loss. Check the width before zipping and decide whether to skip "
                "or pad. Second, colspan and rowspan mean one cell can cover several logical columns; an HTML "
                "parser reports the attributes but does not expand the grid for you. Handle the easy rectangular "
                "tables first and log the irregular ones. Nested tables are another trap: a tr inside an inner "
                "table belongs to a different record, so if you need nesting you must track depth. Today's fixture "
                "is rectangular on purpose, and the assertion checks that the header mapping produced the "
                "expected first record rather than relying on cell order."
            ),
            code="""from html.parser import HTMLParser

class Table(HTMLParser):
    def __init__(self):
        super().__init__()
        self.rows = []
        self.row = None
        self.cell = None
        self.buffer = []

    def handle_starttag(self, tag, attrs):
        if tag == "tr":
            self.row = []
        elif tag in ("td", "th") and self.row is not None:
            self.cell = tag
            self.buffer = []

    def handle_data(self, data):
        if self.cell:
            self.buffer.append(data)

    def handle_endtag(self, tag):
        if tag in ("td", "th") and self.cell:
            value = " ".join("".join(self.buffer).split())
            self.row.append(value)
            self.cell = None
        elif tag == "tr" and self.row is not None:
            self.rows.append(self.row)
            self.row = None

html = ('<table><tr><th>Title</th><th>Price</th></tr>'
        '<tr><td>Dune</td><td>9.99</td></tr>'
        '<tr><td>Foundation</td><td>12.50</td></tr></table>')
parser = Table()
parser.feed(html)
header = parser.rows[0]
records = [dict(zip(header, row)) for row in parser.rows[1:]]
print("header:", header)
for record in records:
    print(record)
assert records[0]["Title"] == "Dune" and len(records) == 2
print("built", len(records), "records from the table")
""",
            variant_b="add a row with only one cell and decide whether to skip it or pad the missing price",
            variant_c="swap the two columns in the header and confirm the names still produce the right record",
            mistakes=[
                "Hard-coding cell indexes instead of mapping through the header row.",
                "Using zip on a ragged row, which truncates silently and loses values.",
                "Ignoring nested tables, where inner rows get appended to the outer table's record.",
            ],
            q1=(
                "Why build records from the header row instead of from fixed cell indexes?",
                "Header names survive column reordering; fixed indexes silently swap fields when the site changes the table layout.",
            ),
            homework=(
                "Write `table_records(html)` that reads th cells as keys, checks each row width, skips ragged "
                "rows, and returns dictionaries. Run it on two tables, one rectangular and one with a short row, "
                "print both record lists, and comment which line rejects the bad row."
            ),
            patterns=["handle_starttag", "zip(", "print("],
            mapping=(
                "pandas.read_html is the shortcut once BeautifulSoup or lxml has parsed the page; Scrapy users "
                "often build the same header mapping by hand. Always inspect row width before trusting it."
            ),
        ),
        97: dict(
            topic="Links and relative URLs",
            idea=(
                "Link extraction looks trivial until the same destination appears in five spellings. A page can "
                "use /books/dune, books/dune, ../books/dune, an absolute URL, or an anchor with a tracking "
                "parameter. Deduplication by raw href is therefore wrong: it treats equivalent targets as "
                "different and inflates crawl counts. Resolve every href against the page's base URL with "
                "urljoin, then split the result and strip the fragment, which only changes browser scroll "
                "position. Decide explicitly what to do with query strings, because some identify content and "
                "some are tracking noise. Also filter schemes before resolving: javascript: and mailto: are not "
                "crawl targets, and a bare #top is the current page. A base tag in the document can override the "
                "URL you fetched, so honour it if present. Finally, remember that resolving is not the same as "
                "authorising: a link may point off-site, and following it may violate the crawl scope you "
                "intended. Store the resolved absolute URL on the record, not the raw href, so later stages never "
                "have to guess the page base again. Today's fixture repeats a link and mixes relative, fragment and JavaScript targets; "
                "the output shows the resolved list and the smaller unique set, which is the number a crawl "
                "frontier should actually receive."
            ),
            code="""from html.parser import HTMLParser
from urllib.parse import urljoin, urlsplit

class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.hrefs = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            href = dict(attrs).get("href")
            if href:
                self.hrefs.append(href)

html = ('<a href="/books/dune">Dune</a><a href="../about">About</a>'
        '<a href="javascript:void(0)">Menu</a><a href="#top">Top</a>'
        '<a href="/books/dune">Dune again</a>')
parser = Links()
parser.feed(html)
base = "https://shop.example/catalog/"
resolved = []
for href in parser.hrefs:
    if href.startswith(("javascript:", "mailto:", "#")):
        continue
    parts = urlsplit(urljoin(base, href))
    resolved.append(parts._replace(fragment="").geturl())
print("resolved:", resolved)
print("unique:", sorted(set(resolved)))
assert "https://shop.example/books/dune" in set(resolved)
print(len(resolved), "links,", len(set(resolved)), "unique")
""",
            variant_b="add a link with a ?ref=home query and decide whether it is a new destination",
            variant_c="change the base to https://shop.example/catalog/books/ and see which paths move",
            mistakes=[
                "Deduplicating raw hrefs before resolving them, so equivalent URLs both survive.",
                "Following javascript:, mailto: and fragment links as if they were pages.",
                "Ignoring an off-site link because it resolved successfully, when crawl scope should reject it.",
            ],
            q1=(
                "Why must urljoin run before deduplication?",
                "Relative and absolute spellings can identify the same page; resolving first makes comparison meaningful, otherwise duplicates survive.",
            ),
            homework=(
                "Write `page_links(html, base)` that resolves anchors, drops fragments and non-HTTP schemes, and "
                "returns sorted unique URLs. Run it on two base URLs, print both lists, and comment which line "
                "prevents the duplicate Dune link from being counted twice."
            ),
            patterns=["urljoin(", "urlsplit(", "print("],
            mapping=(
                "Scrapy resolves links against response.url before it schedules them, and BeautifulSoup users "
                "call urljoin the same way. The crawl frontier must receive canonical URLs, not raw hrefs."
            ),
        ),
        98: dict(
            topic="Nested cards and repeated blocks",
            idea=(
                "Listing pages repeat a block: a card with a title, a price, sometimes a rating and a nested "
                "metadata row. The repeated element is the record boundary, and every field belongs to the "
                "nearest enclosing boundary. This is where flat state machines fail. If you start collecting a "
                "title whenever you see an h3, a nested recommendation card inside the outer card will overwrite "
                "or append to the wrong record. The fix is to track the depth at which the card opened and only "
                "accept fields while that card is still open. When the closing div returns the parser to the "
                "card's depth, finalise the record. Nested divs are the normal case, not an edge case, so the "
                "closing condition must compare depth as well as tag name. A related bug is counting the same "
                "card twice because a selector matches both an outer and an inner element with the same class; "
                "the depth check prevents that too. Field state should reset at every new card, and the closing "
                "handler should append only a record that has real content. Print the number of cards you "
                "expected beside the number you produced. Today's fixture places the price inside a nested meta "
                "div so a parser that assumes direct children fails, while the depth-aware version records both "
                "books correctly."
            ),
            code="""from html.parser import HTMLParser

class CardParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.depth = 0
        self.card_depth = None
        self.record = None
        self.field = None
        self.buffer = []
        self.records = []

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        self.depth += 1
        if tag == "div" and "card" in attributes.get("class", "").split() and self.card_depth is None:
            self.card_depth = self.depth
            self.record = {"title": "", "price": ""}
        elif self.card_depth is not None and tag == "h3":
            self.field = "title"
            self.buffer = []
        elif self.card_depth is not None and tag == "span" and "price" in attributes.get("class", "").split():
            self.field = "price"
            self.buffer = []

    def handle_data(self, data):
        if self.field:
            self.buffer.append(data)

    def handle_endtag(self, tag):
        if self.field == "title" and tag == "h3":
            self.record["title"] = " ".join("".join(self.buffer).split())
            self.field = None
        elif self.field == "price" and tag == "span":
            self.record["price"] = " ".join("".join(self.buffer).split())
            self.field = None
        if self.card_depth is not None and self.depth == self.card_depth and tag == "div":
            self.records.append(self.record)
            self.card_depth = None
            self.record = None
        self.depth -= 1

html = ('<section>'
        '<div class="card"><h3>Dune</h3><div class="meta"><span class="price">$9.99</span></div></div>'
        '<div class="card"><h3>Foundation</h3><div class="meta"><span class="price">$12.50</span></div></div>'
        '</section>')
parser = CardParser()
parser.feed(html)
print("records:", parser.records)
assert [r["title"] for r in parser.records] == ["Dune", "Foundation"]
print("built", len(parser.records), "nested card records")
""",
            variant_b="add a third card with an extra nested div around the title and keep the depth logic unchanged",
            variant_c="remove the meta wrapper so price becomes a direct child and confirm the record still forms",
            mistakes=[
                "Finalising a card on the first closing div, which often closes a nested wrapper instead.",
                "Collecting fields whenever a tag appears, so nested recommendation cards leak into the parent.",
                "Resetting the title buffer but not the field flag, so later text appends to a stale value.",
            ],
            q1=(
                "Why must card completion compare the current depth with the depth where the card opened?",
                "Many divs close inside a card; only the close at the opening depth ends the record, and a tag-only check fires too early.",
            ),
            homework=(
                "Write `parse_cards(html)` that tracks the card's opening depth, reads title and price from nested "
                "containers, and emits one dictionary per card. Run it on two fixtures with different nesting, "
                "print both record lists, and comment which line ends the outer card."
            ),
            patterns=["card_depth", "depth -= 1", "print("],
            mapping=(
                "BeautifulSoup's find_all('div', class_='card') scopes nested fields naturally, but a descendant "
                "selector can still double-match; Scrapy users use relative XPath from each card node."
            ),
        ),
        99: dict(
            topic="Surviving malformed HTML",
            idea=(
                "Real pages are not well-formed XML. Browsers tolerate unclosed list items, stray end tags, "
                "duplicate attributes and tags nested in impossible ways, which means scraper code must tolerate "
                "them too. Python's html.parser is deliberately forgiving: it reports what it can and keeps "
                "going, but it does not repair a tree for you. Your handlers therefore need a recovery policy. "
                "Keep a stack of open elements, close an implicit element when a sibling starts, and on a stray "
                "end tag pop only down to a matching ancestor if one exists. At the end of the document, flush "
                "whatever is still open so the last record is not lost. Never assume every start has an end. "
                "Notice also that tolerance can hide a bug: a parser that silently drops half a page looks "
                "successful unless you compare extracted counts with an expectation. Print the count of records "
                "and of recovery events, and keep that number in the run summary. When the markup is truly "
                "unrecoverable, the honest outcome is a parse failure for that page, not a plausible partial "
                "record. Today's fixture omits the closing li tags and includes an unclosed paragraph; the "
                "recovery logic still produces two list items, which is the difference between robust and "
                "brittle parsing."
            ),
            code="""from html.parser import HTMLParser

class Tolerant(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack = []
        self.items = []
        self.buffer = []

    def handle_starttag(self, tag, attrs):
        if tag == "li":
            self._flush()
            self.stack.append("li")

    def handle_data(self, data):
        if self.stack:
            self.buffer.append(data)

    def handle_endtag(self, tag):
        if tag in ("li", "ul"):
            self._flush()
        if tag == "ul":
            while self.stack:
                self.stack.pop()

    def _flush(self):
        text = " ".join("".join(self.buffer).split())
        if text:
            self.items.append(text)
        self.buffer = []

    def close(self):
        super().close()
        self._flush()
        self.stack = []

html = "<ul><li>Dune<li>Foundation</ul><p>Unclosed paragraph"
parser = Tolerant()
parser.feed(html)
parser.close()
print("recovered items:", parser.items)
assert parser.items == ["Dune", "Foundation"]
print("recovered", len(parser.items), "items from broken markup")
""",
            variant_b="add a stray </li> after the list and confirm it does not create a duplicate item",
            variant_c="leave the ul unclosed as well and check that close() still flushes the last item",
            mistakes=[
                "Assuming every li has a closing tag, so only the last item in the list is captured.",
                "Ignoring close(), which leaves buffered text from the final unclosed element unrecorded.",
                "Treating a partial parse as success without comparing record counts to the visible page.",
            ],
            q1=(
                "Why call parser.close() before reading the extracted items?",
                "It signals end of input and lets pending text and unclosed elements be flushed, so the final record is not silently dropped.",
            ),
            homework=(
                "Write `recover_items(html)` that handles missing li close tags, stray end tags, and an unclosed "
                "list, counting recovery events as it goes. Run it on two malformed fixtures, print the items and "
                "counts, and comment which line flushes the last item."
            ),
            patterns=["close()", "_flush", "print("],
            mapping=(
                "lxml's HTML parser repairs broken markup into a tree, while BeautifulSoup uses a chosen parser "
                "and still exposes surprises; Scrapy's parsel inherits lxml. Always log parse quality."
            ),
        ),
        100: dict(
            topic="Embedded data: JSON-LD and data attributes",
            idea=(
                "Many pages publish the same facts twice: once as visible markup and once as structured data for "
                "search engines or front-end code. JSON-LD sits inside a script tag with type application/ld+json "
                "and contains a JSON object that often names the product, price and availability directly. Data "
                "attributes such as data-product-id or data-price are the other common channel. Both are worth "
                "checking before you scrape pixels, because they are less likely to break when visual layout "
                "changes. The parsing pattern is still HTMLParser: detect the script type, buffer its contents, "
                "then hand the completed string to json.loads only after the element closes. Never call json.loads "
                "on a partial buffer. In JSON-LD, the top level may be a single object or a list, and the field "
                "you want may be nested under offers or aggregateRating, so inspect the shape instead of assuming "
                "one path. Data attributes arrive as strings even when they look numeric, so convert deliberately. "
                "Finally, embedded data can disagree with the visible page: a stale JSON-LD block is a real "
                "failure mode. Treat it as evidence, not truth, and when both sources exist, record which one you "
                "used. Today's fixture carries both channels and the code proves they can be recovered from one "
                "pass."
            ),
            code="""from html.parser import HTMLParser
import json

class Embedded(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_json = False
        self.buffer = []
        self.json_blocks = []
        self.data_attrs = []

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag == "script" and attributes.get("type") == "application/ld+json":
            self.in_json = True
            self.buffer = []
        for key, value in attrs:
            if key.startswith("data-"):
                self.data_attrs.append((key, value))

    def handle_data(self, data):
        if self.in_json:
            self.buffer.append(data)

    def handle_endtag(self, tag):
        if tag == "script" and self.in_json:
            self.json_blocks.append("".join(self.buffer))
            self.in_json = False

html = ('<div data-product-id="42" data-category="books">Dune</div>'
        '<script type="application/ld+json">'
        '{"@type": "Product", "name": "Dune", "offers": {"price": "9.99"}}'
        '</script>')
parser = Embedded()
parser.feed(html)
data = json.loads(parser.json_blocks[0])
print("name:", data["name"], "| price:", data["offers"]["price"])
print("data attributes:", parser.data_attrs)
assert data["name"] == "Dune" and ("data-product-id", "42") in parser.data_attrs
print("recovered", len(parser.data_attrs), "data attributes and one JSON-LD block")
""",
            variant_b="make the JSON-LD top level a list containing one product and adjust the lookup",
            variant_c="remove the offers key and decide whether the record should fail or carry a missing price",
            mistakes=[
                "Parsing JSON before the script closes, so the buffer is truncated and json.loads raises.",
                "Assuming the top-level JSON-LD is always an object rather than an object or a list.",
                "Trusting JSON-LD over the visible page without recording which source produced the value.",
            ],
            q1=(
                "Why does the parser wait for the script's closing tag before calling json.loads?",
                "The JSON text arrives through multiple handle_data events; only the closing tag proves the complete document has been buffered.",
            ),
            homework=(
                "Write `embedded_record(html)` that extracts the JSON-LD name and price plus all data-* attributes, "
                "returning one dictionary. Run it on two fixtures, one with a list-shaped JSON-LD block, print "
                "both records, and comment which line confirms the script has ended."
            ),
            patterns=["application/ld+json", "json.loads", "print("],
            mapping=(
                "BeautifulSoup lets you select script[type='application/ld+json'] and call json.loads on its "
                "string; Scrapy users often find the same payload in response.css or response.xpath results."
            ),
        ),
        101: dict(
            topic="Regular expressions as a last resort",
            idea=(
                "Regular expressions are excellent at flat, stable text and dangerous at nested markup. A pattern "
                "can pull a price out of a sentence, validate a SKU, or clean a currency string, and it does so "
                "without any parser state. That is the right job for regex: a local transformation after the "
                "markup has already been reduced to text. The wrong job is matching whole elements, because HTML "
                "nesting and optional attributes turn every clever pattern into a pile of non-greedy groups that "
                "still fails on one page. The classic symptom is a pattern that works on the fixture and returns "
                "empty or double matches in production, usually because a new attribute or a nested span changed "
                "the shape. Use regex when the input contract is genuinely simple: one line, one known separator, "
                "no nesting. Compile the pattern once, name its groups, and anchor it to the part of the string you "
                "control. Prefer character classes that exclude the delimiter over wildcards, so a missing closing "
                "delimiter fails instead of swallowing the rest of the page. Test the pattern against at least one "
                "negative case. And when the markup becomes irregular, move back to the parser instead of adding "
                "another optional group. Today's fixture is deliberately flat: one paragraph per row with a known "
                "separator. The lesson is not that regex is bad; it is that regex needs a stronger guarantee than "
                "HTML usually offers."
            ),
            code="""import re

fragment = ('<p>Dune - $9.99 (in stock)</p>'
            '<p>Foundation - $12.50 (sold out)</p>'
            '<p>No price here</p>')
pattern = re.compile(r"<p>([^<]+) - \\$(\\d+\\.\\d{2})")
rows = [{"title": match.group(1), "price": float(match.group(2))}
        for match in pattern.finditer(fragment)]
print("rows:", rows)
print("matched:", len(rows), "of 3 paragraphs")
assert rows[1]["price"] == 12.50
print("regex handled the flat rows and skipped the odd one")
""",
            variant_b="add an attribute to the p tag and decide whether the pattern should be updated or replaced",
            variant_c="change the separator to an em dash and see the match count fall to zero",
            mistakes=[
                "Matching whole nested elements with non-greedy groups instead of using a parser.",
                "Using a greedy wildcard that swallows everything after a missing closing delimiter.",
                "Testing only the perfect fixture and never a negative or malformed case.",
            ],
            q1=(
                "When is a regular expression the right tool for scraped content?",
                "When the input is already flat and its format is known, such as cleaning a price or validating an identifier, not when markup nesting is involved.",
            ),
            homework=(
                "Write `flat_rows(fragment)` that extracts title and price only from paragraphs matching the "
                "documented pattern and skips everything else. Run it on two fragments, one well-formed and one "
                "with a changed separator, print both results, and comment which line keeps the mismatch visible."
            ),
            patterns=["re.compile", "finditer", "print("],
            mapping=(
                "lxml and BeautifulSoup users often run a regex over get_text for a final cleanup; Scrapy has "
                "re() and re_first() on selectors for the same narrow job. Keep the parser responsible for structure."
            ),
        ),
        102: dict(
            topic="Pagination patterns",
            idea=(
                "Pagination is a set of links with semantics, not a number you invent. One site uses ?page=3, "
                "another uses /page/3, a third uses a cursor token that looks like garbage but matters. The page "
                "usually tells you the next target: an anchor with rel=next, a link whose text is Next, or a "
                "numbered control. Read that signal before constructing anything by hand. Resolve the href against "
                "the current URL, because relative pagination paths break the moment the base path changes. Then "
                "keep a visited set and a stop rule. The stop rule can be a missing next link, an empty result "
                "list, a page number beyond a known total, or a repeated URL; relying on one of these alone is "
                "fragile, so combine the cheap ones. Never loop until the site itself errors, and never assume "
                "page numbers are contiguous. Query strings deserve care: page and filter parameters can be "
                "reordered, and tracking parameters create infinite duplicates. Canonicalise the URL before "
                "adding it to the frontier. Today's fixture exposes prev, next and numbered links, and the code "
                "resolves all of them, extracts the page numbers, and prints the exact next URL. That is the "
                "input a crawl loop needs, and it is evidence that the site's own semantics, not your guess, "
                "drive the traversal."
            ),
            code="""from html.parser import HTMLParser
from urllib.parse import urljoin, urlsplit, parse_qs

class Pagination(HTMLParser):
    def __init__(self):
        super().__init__()
        self.anchors = []

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag == "a" and attributes.get("href"):
            self.anchors.append((attributes["href"], attributes.get("rel", "")))

html = ('<a href="/list?page=1" rel="prev">1</a>'
        '<a href="/list?page=3" rel="next">Next</a>'
        '<a href="/list?page=2">2</a>')
parser = Pagination()
parser.feed(html)
base = "https://shop.example/catalog/list?page=2"
next_url = None
pages = set()
for href, rel in parser.anchors:
    url = urljoin(base, href)
    if rel == "next":
        next_url = url
    query = parse_qs(urlsplit(url).query)
    if "page" in query:
        pages.add(int(query["page"][0]))
print("next:", next_url)
print("page numbers:", sorted(pages))
assert next_url == "https://shop.example/list?page=3" and pages == {1, 2, 3}
print("pagination links resolved from the page itself")
""",
            variant_b="replace rel=next with link text Next and decide what signal the parser should trust",
            variant_c="add a page=4 link that repeats the current filters and check that it resolves cleanly",
            mistakes=[
                "Constructing page URLs by incrementing a number while the site uses cursor tokens.",
                "Resolving relative page links against the wrong base path, producing 404s after page one.",
                "Looping without a visited set, so a self-referential next link crawls forever.",
            ],
            q1=(
                "Why prefer the page's rel=next link over incrementing a page number?",
                "The site's own link encodes the real next target, including cursor or filter state, while an invented number may point nowhere.",
            ),
            homework=(
                "Write `next_page(html, base)` that resolves rel=next and numbered page links, returning the next "
                "URL and the sorted page numbers. Run it on two fixtures, one relative and one absolute, print "
                "both results, and comment which line prevents an off-site next URL."
            ),
            patterns=["rel", "urljoin(", "print("],
            mapping=(
                "Scrapy's LinkExtractor can follow pagination links and its response.follow resolves them; "
                "BeautifulSoup users read rel and href directly. Always combine the link signal with a visited set."
            ),
        ),
        103: dict(
            topic="Parse once, reuse everywhere",
            idea=(
                "Parsing is the expensive, stateful part of scraping, so do it once and keep the result. A parser "
                "object is not a document you can query repeatedly without care: its buffers and flags describe "
                "the last element it saw, and feeding the same string twice appends duplicates to its lists. The "
                "disciplined shape is a pure function that takes HTML and returns a list of plain dictionaries. "
                "Once those records exist, every later question is cheap and safe: how many books are under ten "
                "dollars, what is the average price, which titles are duplicates, what would the CSV look like. "
                "This separation also makes testing honest, because you can test the parser on a fixture once and "
                "then test analysis functions on hand-written records with no HTML at all. It matches the "
                "fetch-parse-store pipeline from the foundations: fetching produces text, parsing produces "
                "records, analysis consumes records. A common anti-pattern is a function that parses the same "
                "page again for each field, which multiplies both runtime and the chance that two fields come "
                "from different parser states. Another is returning live parser objects, which leak "
                "implementation details into every caller. Today's fixture is parsed once, then used to print "
                "titles, filter cheap books and compute an average, proving that one immutable record list can "
                "answer several questions without touching the HTML again."
            ),
            code="""from html.parser import HTMLParser

class Cards(HTMLParser):
    def __init__(self):
        super().__init__()
        self.records = []
        self.current = None
        self.field = None
        self.buffer = []

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag == "article" and "book" in attributes.get("class", "").split():
            self.current = {"title": "", "price": 0.0}
        elif self.current is not None and tag == "h3":
            self.field = "title"
            self.buffer = []
        elif self.current is not None and tag == "span" and "price" in attributes.get("class", "").split():
            self.field = "price"
            self.buffer = []

    def handle_data(self, data):
        if self.field:
            self.buffer.append(data)

    def handle_endtag(self, tag):
        if self.field == "title" and tag == "h3":
            self.current["title"] = " ".join("".join(self.buffer).split())
            self.field = None
        elif self.field == "price" and tag == "span":
            self.current["price"] = float("".join(self.buffer).strip().lstrip("$"))
            self.field = None
        elif tag == "article" and self.current is not None:
            self.records.append(self.current)
            self.current = None

html = ('<article class="book"><h3>Dune</h3><span class="price">$9.99</span></article>'
        '<article class="book"><h3>Foundation</h3><span class="price">$12.50</span></article>'
        '<article class="book"><h3>Hyperion</h3><span class="price">$7.25</span></article>')
parser = Cards()
parser.feed(html)
records = parser.records
print("records:", len(records))
print("titles:", [record["title"] for record in records])
print("cheap:", [record["title"] for record in records if record["price"] < 10])
print("average:", round(sum(r["price"] for r in records) / len(records), 2))
assert len(records) == 3 and records[2]["title"] == "Hyperion"
print("one parse answered three questions")
""",
            variant_b="build the parser twice on the same html and compare record counts to see the duplication",
            variant_c="add a fourth book with a missing price and decide whether records or analysis should handle it",
            mistakes=[
                "Feeding the same HTML into one parser twice, which appends duplicate records to its lists.",
                "Returning the parser object instead of plain records, so callers depend on internal flags.",
                "Parsing the page again for each field, wasting work and risking inconsistent state.",
            ],
            q1=(
                "Why return plain dictionaries instead of the parser object?",
                "Records are stable data that analysis and storage can consume; a parser carries mutable state tied to one input and is not reusable.",
            ),
            homework=(
                "Write `parse_books(html)` returning a list of typed dictionaries, then compute a count, a filter "
                "and an average from that list only. Run it on two fixtures, print all three views for each, and "
                "comment which line guarantees the HTML is parsed once."
            ),
            patterns=["def ", "records", "print("],
            mapping=(
                "This is the parse step in a Scrapy pipeline or a BeautifulSoup helper: return data, not the tree "
                "or parser. Downstream items, filters and exporters then operate on plain records."
            ),
        ),
        104: dict(
            topic="Review: HTML to records",
            idea=(
                "The phase ends with the full conversion you will repeat on every scraping job: one HTML string "
                "becomes a list of records with stable keys. The pipeline is visible in a single function. Parse "
                "the markup once, scope each record to its repeated container, read only the fields inside that "
                "container, normalise text and URLs, convert types deliberately, and assert the shape of the "
                "result. The review is not a new idea but a chance to notice which step you still skip under "
                "pressure. Most people skip normalisation, then spend an afternoon debugging duplicate links. "
                "Others skip the count check, then discover a selector matched twice. The record contract is the "
                "real deliverable: title, price as a number, and an absolute link, with no missing keys. If a "
                "field is absent, decide whether the record is invalid or the field is optional, and encode that "
                "decision. Keep the parser separate from the normaliser and from the summary so each piece can be "
                "tested on saved HTML without a network. That structure survives site redesigns far better than "
                "one long function. Today's fixture combines nested cards, relative links and text noise, and the "
                "final print is the kind of run summary you should expect to see: records produced, titles, and "
                "the cheapest item. If you can rebuild this from memory, the parsing phase is installed."
            ),
            code="""from html.parser import HTMLParser
from urllib.parse import urljoin

class Catalog(HTMLParser):
    def __init__(self):
        super().__init__()
        self.records = []
        self.current = None
        self.field = None
        self.buffer = []
        self.href = None

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag == "article" and "book" in attributes.get("class", "").split():
            self.current = {"title": "", "price": 0.0, "link": ""}
        elif self.current is not None and tag == "h3":
            self.field = "title"
            self.buffer = []
        elif self.current is not None and tag == "span" and "price" in attributes.get("class", "").split():
            self.field = "price"
            self.buffer = []
        elif self.current is not None and tag == "a":
            self.href = attributes.get("href", "")

    def handle_data(self, data):
        if self.field:
            self.buffer.append(data)

    def handle_endtag(self, tag):
        if self.field == "title" and tag == "h3":
            self.current["title"] = " ".join("".join(self.buffer).split())
            self.field = None
        elif self.field == "price" and tag == "span":
            self.current["price"] = float("".join(self.buffer).strip().lstrip("$"))
            self.field = None
        elif tag == "a" and self.href:
            self.current["link"] = urljoin("https://shop.example/", self.href)
            self.href = None
        elif tag == "article" and self.current is not None:
            self.records.append(self.current)
            self.current = None

html = ('<article class="book"><h3>Dune</h3>'
        '<span class="price">$9.99</span><a href="/books/dune">details</a></article>'
        '<article class="book"><h3>Foundation</h3>'
        '<span class="price">$12.50</span><a href="/books/foundation">details</a></article>')
parser = Catalog()
parser.feed(html)
records = parser.records
print("records:", len(records))
for record in records:
    print(record["title"], record["price"], record["link"])
cheapest = min(records, key=lambda record: record["price"])
print("cheapest:", cheapest["title"], "at", cheapest["price"])
assert all(record["link"].startswith("https://shop.example/") for record in records)
print("all links absolute and", len(records), "records complete")
""",
            variant_b="add a third book whose link is already absolute and confirm urljoin leaves it alone",
            variant_c="remove the link from one card and decide whether the record should fail or carry an empty link",
            mistakes=[
                "Returning records with relative links that break when the crawl moves to another base path.",
                "Leaving price as a string, so comparisons and the minimum sort behave like text.",
                "Skipping the final count assertion, so a doubled selector reaches storage unnoticed.",
            ],
            q1=(
                "What makes a parsed record complete in this phase?",
                "It has the agreed keys, normalised text, a numeric price and an absolute link, verified by a count and shape check before storage.",
            ),
            homework=(
                "Write `catalog_records(html, base)` that parses repeated book cards into complete records, "
                "normalises text and links, converts prices, and asserts the record count. Run it on two fixtures, "
                "one nested and one with a missing link, print both summaries, and comment which line enforces the "
                "record contract."
            ),
            patterns=["HTMLParser", "urljoin(", "print("],
            mapping=(
                "This is the shape of a real Scrapy item pipeline or a BeautifulSoup extraction module: parse, "
                "normalise, validate, then hand plain records to storage. The library changes; the contract does not."
            ),
        ),
    },
)
