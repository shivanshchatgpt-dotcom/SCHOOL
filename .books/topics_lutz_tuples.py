"""Canonical topic batch: tuples as fixed records (Lutz ch 9)."""
from canonical_topics import topic

LUTZ_CH9_TUPLES = {
    "book": "learning-python",
    "chapter": 9,
    "pages": [225, 256],
    "sections": ["Tuples", "Tuples in Action"],
}


topic(
    "canonical:tuple-as-fixed-record",
    "A tuple is a fixed-length, immutable sequence whose position order carries meaning, which is what makes it the right shape for a record",
    sources=[dict(LUTZ_CH9_TUPLES)],
    concept=(
        "A tuple is a sequence, so it supports indexing, slicing, concatenation and "
        "iteration exactly as a list does, but it is immutable and fixed in length, so it "
        "supports none of the in-place change operations. Those two properties together "
        "give the tuple its real role: its positions can carry an agreed meaning, so a "
        "pair can be an x and a y, or a triple a name, a quantity and a price, and that "
        "meaning is stable because nobody can append to or reorder it later. Writing a "
        "one-item tuple needs a trailing comma, because parentheses alone are just "
        "grouping, and that is the detail that most often confuses a first encounter. "
        "Unpacking is the idiom that makes tuples readable: assigning a tuple's items to "
        "named variables in one statement expresses the record's meaning in code, and "
        "swapping two values with no temporary is the same operation. A tuple is also "
        "hashable when all its contents are, which is why it can serve as a dictionary "
        "key or a set member where a list cannot, and that property is what makes it the "
        "natural type for compound keys. Choosing a tuple over a list is a statement "
        "about intent: the positions mean something fixed, the length will not change, "
        "and the record should be safe to share without a copy."
    ),
    prerequisites=["canonical:object-type-categories"],
    pitfalls=[
        "Writing (value) when a one-item tuple is meant, which produces a parenthesised "
        "expression and not a tuple at all.",
        "Accessing a tuple's positions by bare index in code that others have to read, "
        "when unpacking to names would state what each position means.",
        "Using a list as a dictionary key or set member, which raises because a mutable "
        "object has no stable hash, where a tuple of the same values would work.",
    ],
    adapters={
        "machine-learning": {
            "framing": (
                "A dataset's categorical fields combine into compound keys, and a tuple "
                "is the type that can key a dictionary or a set where a list cannot."
            ),
            "application": (
                "Walk the example as counts being aggregated over two categorical fields "
                "together. Each record yields a pair, and that pair is used as a "
                "dictionary key because it is a tuple and therefore hashable, whereas a "
                "list of the same two values would raise. Unpacking the key back into two "
                "names at the point of use is what keeps the printout readable, since "
                "positional access like key[0] hides which field is which. The "
                "transferable point is that a compound key is a fixed record: its length "
                "will not change and its positions have agreed meanings, so the tuple is "
                "the type that says so in the code. Sorting the finished counts by value "
                "then gives a ranked view, and the key's immutability is what guarantees "
                "that the ranking reflects the data the loop actually saw."
            ),
            "example_hint": "aggregate counts over pairs as tuple keys and unpack them when reporting",
            "assessment_angle": "why the key must be a tuple and what unpacking adds to readability",
            "day": 6,
            "title": "Two Fields, One Key: Compound Counts with Tuples",
            "code": """records = [
    ("north", "retail"), ("north", "retail"), ("north", "online"),
    ("south", "online"), ("south", "online"), ("south", "online"),
    ("east", "retail"),
]

counts = {}
for region, channel in records:
    key = (region, channel)
    counts[key] = counts.get(key, 0) + 1

ranked = sorted(counts.items(), key=lambda item: item[1], reverse=True)
for (region, channel), n in ranked:
    print(f"{region:<6} {channel:<8} {n}")

print("single-item tuple:", ("only",), "not", ("only"))
print("usable as a set member:", {("north", "retail")} < set(counts))
""",
            "questions": [
                "Why is the key built as a tuple rather than a list?",
                "The reporting loop writes (region, channel), n rather than using indexes. What does that add?",
                "What does the set-membership check demonstrate about the pair's values?",
            ],
            "answers": [
                "Because the pair is used as a dictionary key and a tuple is hashable, whereas a list is mutable and would raise rather than serve as a key.",
                "It unpacks each key into two names that state what the positions mean, so the reader sees the fields instead of having to know that index 0 is the region.",
                "That the pair is hashable and comparable, so it can belong to a set, which is the property that also lets it key the dictionary.",
            ],
            "homework": (
                "Write compound_counts.py with a list of at least twelve records, each a pair of "
                "two categorical fields. Aggregate their frequencies in a dictionary keyed by a "
                "tuple of the two fields, then print the frequencies in descending order with the "
                "key unpacked into two named variables. Finally print a one-item tuple with its "
                "trailing comma and demonstrate a tuple used as a set member. Observable output: "
                "one ranked line per distinct pair plus two closing demonstration lines."
            ),
            "required_patterns": ["(,", ".get(", "sorted(", "for ", "print("],
        },
        "data-viz": {
            "framing": (
                "A plotted point is an x and a y in a fixed order, and a series of such "
                "pairs is exactly the shape a tuple record describes."
            ),
            "application": (
                "Walk the example as a series of coordinate pairs being prepared and "
                "queried. Each point is a two-item tuple whose positions mean x then y, "
                "and unpacking them in a loop names both coordinates so the drawing code "
                "reads as geometry rather than as index arithmetic. Because the points "
                "are tuples, they can be put in a set to remove duplicates and used as "
                "dictionary keys mapping a point to a label, neither of which would be "
                "possible with lists. The fixed-length property is what makes the record "
                "trustworthy: a consumer of the series can assume exactly two positions "
                "per point, and that assumption is protected by immutability, since no "
                "step of the pipeline can append a third. Computing the bounding box from "
                "the unpacked coordinates is the kind of operation that depends on that "
                "stability, because it reads each point the same way."
            ),
            "example_hint": "treat points as fixed tuples, unpack them, deduplicate with a set",
            "assessment_angle": "what the fixed length guarantees and what set membership buys",
            "day": 6,
            "title": "A Point Is a Fixed Pair: Unpack It, Deduplicate It, Key It",
            "code": """points = [(1, 2), (3, 5), (1, 2), (6, 1), (3, 5), (8, 4)]

unique = list(dict.fromkeys(points))
print("unique points:", unique)

seen = set(unique)
print("candidate already plotted:", (3, 5) in seen)

for x, y in unique:
    print(f"x={x} y={y}")

xs = [x for x, y in unique]
ys = [y for x, y in unique]
print(f"span: x {min(xs)}..{max(xs)}, y {min(ys)}..{max(ys)}")

labels = {(0, 0): "origin", (8, 4): "peak"}
print("label found:", labels.get((8, 4), "none"))
""",
            "questions": [
                "Why can the points be deduplicated with dict.fromkeys and used as dictionary keys?",
                "The loop writes for x, y in unique. What does that statement express, and what would the alternative look like?",
                "What does the fixed length of each point guarantee for the comprehension that builds xs and ys?",
            ],
            "answers": [
                "Because tuples are hashable when their contents are, so each point has a stable identity that a set or a dictionary key can rely on, which a list would not provide.",
                "That each point unpacks into an x and a y, giving both coordinates names; the alternative would be indexing each point twice by position, which hides which coordinate is which.",
                "That every point has exactly two positions, so unpacking into two names never fails and both comprehensions see a consistent shape.",
            ],
            "homework": (
                "Write point_records.py with a list of at least ten coordinate pairs including "
                "duplicates. Deduplicate the list with dict.fromkeys, print each unique point with "
                "its coordinates unpacked into named variables, compute and print the x and y "
                "spans of the set, and build a dictionary mapping two of the points to labels and "
                "look one up. Observable output: the unique list, one line per point, the span "
                "line and the label lookup."
            ),
            "required_patterns": ["dict.fromkeys", "for ", "min(", "max(", "print("],
        },
        "api-building": {
            "framing": (
                "A paginated response is a fixed record: the page of items, the page "
                "number, and whether more pages follow. That shape never changes within "
                "a client, so it is a tuple."
            ),
            "application": (
                "Walk the example as a client consuming pages. Each response is "
                "unpacked into three names, and because the record is a tuple the client "
                "cannot accidentally mutate the page number or append an item to the "
                "page before passing it on. Using the record as a cache key is what "
                "makes the tuple earn its type: a (resource, page) pair keys a cache "
                "dictionary, which a list could not do. The fixed positional meaning is "
                "what lets the client trust the shape across many endpoints, and the "
                "trailing-comma detail appears whenever a single-item record is needed, "
                "since a parenthesised value would silently be the value itself. The "
                "discipline worth carrying away is that an agreed positional contract is "
                "expressed by choosing a tuple, so a reader knows the length and the "
                "order are part of the interface."
            ),
            "example_hint": "unpack each page response into named fields and key a cache on the pair",
            "assessment_angle": "what the tuple says about the contract and why the cache key works",
            "day": 6,
            "title": "A Page Response Is a Fixed Record: Unpack It, Cache It",
            "code": """def fetch(resource, page):
    size = 3
    start = (page - 1) * size
    items = [f"{resource}-{i}" for i in range(start, start + size)]
    return items, page, start + size < 9   # items, page, has_more

cache = {}
all_items = []
for page in (1, 2, 3):
    key = ("items", page)
    if key not in cache:
        cache[key] = fetch("items", page)
    items, number, has_more = cache[key]
    all_items.extend(items)
    print(f"page {number}: {len(items)} items, more={has_more}")

print("collected:", all_items)
print("cache keys:", sorted(cache))
print("single-item record:", ("page-1",), type(("page-1",)).__name__)
""",
            "questions": [
                "Why is the cache keyed on a tuple rather than a list?",
                "What does unpacking each response into items, number, has_more tell a reader about the interface?",
                "What does the final line demonstrate about ('page-1') written without a trailing comma?",
            ],
            "answers": [
                "Because a cache key must be hashable, and a tuple of a resource name and a page number is, whereas the equivalent list would raise when used as a key.",
                "That every response carries exactly those three values in that order, so the positional contract of the interface is visible in the code that consumes it.",
                "That the parentheses alone are grouping, so the value is a string, and only the trailing comma makes it a one-item tuple.",
            ],
            "homework": (
                "Write page_client.py with a fetch function returning a three-item record of "
                "items, page number and a has-more flag. Loop over at least four pages, key a "
                "cache dictionary on a tuple of resource and page, unpack each cached response "
                "into three named variables, extend a collected list, and print a line per page. "
                "Then print the collected items, the sorted cache keys, and a one-item tuple "
                "shown beside its type. Observable output: one line per page plus three closing "
                "lines."
            ),
            "required_patterns": ["(,", "for ", "sorted(", "if ", "print("],
        },
        "web-scraping": {
            "framing": (
                "A scraped record is a fixed row: a name, a price, a stock state. Storing "
                "it as a tuple says the shape will not change on the way to the exporter."
            ),
            "application": (
                "Walk the example as scraped rows being turned into records and "
                "deduplicated. Each row is built as a tuple of three positions with "
                "agreed meanings, and because it is a tuple it can be put into a set to "
                "collapse duplicates across pages, which is a common need when a site's "
                "pagination overlaps. Unpacking when computing the total keeps the "
                "arithmetic readable, since price has a name rather than index 1. The "
                "reason a tuple is the right choice here rather than a list is that the "
                "export contract downstream expects a fixed shape: a CSV writer takes "
                "the fields in an agreed order, and immutability is what guarantees that "
                "a cleaning step cannot silently add a fourth column to some rows. When "
                "a scraper's output later has inconsistent row lengths, the type choice "
                "is where the bug usually started."
            ),
            "example_hint": "build fixed-shape row tuples, deduplicate with a set, unpack to total",
            "assessment_angle": "why the row is a tuple and what that guarantees downstream",
            "day": 6,
            "title": "A Scraped Row Keeps Its Shape: Deduplicate, Export, Total",
            "code": """raw = [
    ("Mug", "12.5", "in"), ("Kettle", "34.0", "out"),
    ("Mug", "12.5", "in"), ("Bowl", "8.25", "in"),
    ("Kettle", "34.0", "out"),
]

rows = {(name, float(price), stock) for name, price, stock in raw}
print("distinct rows:", len(rows), "from", len(raw), "raw")

for name, price, stock in sorted(rows):
    print(f"{name:<8} {price:>6} {stock}")

available = sum(price for _, price, stock in rows if stock == "in")
print(f"value available: {available:.2f}")
""",
            "questions": [
                "Why are the distinct rows stored in a set, and what property of the tuple makes that possible?",
                "The total uses for _, price, stock in rows. What does the underscore communicate?",
                "What does the tuple guarantee about the rows that a list would not, once they reach an exporter?",
            ],
            "answers": [
                "Because the same product can appear on overlapping pages and a set collapses the duplicates, which is possible because tuples are hashable and can be set members.",
                "That the first position is intentionally unused in this computation, so the reader knows the price and stock are the only fields that matter here.",
                "That every row has exactly three fields in the agreed order, so an exporter can write them without checking, whereas a list could have been appended to mid-pipeline.",
            ],
            "homework": (
                "Write dedupe_rows.py with a list of at least twelve raw scraped triples, including "
                "several exact duplicates across pages. Build a set of tuples that converts the "
                "price text to a float, print how many distinct rows resulted, print each row with "
                "the fields unpacked into names, and print the total value of the rows whose stock "
                "field indicates availability, using an underscore for the unused field. "
                "Observable output: a distinct-count line, one line per row and the total."
            ),
            "required_patterns": ["{", "for ", "sorted(", "sum(", "print("],
        },
        "testing-qa": {
            "framing": (
                "A test case is a fixed record: a name, the input, and the expected "
                "output. Writing it as a tuple makes the table of cases self-documenting."
            ),
            "application": (
                "Walk the example as a table of cases being run against a function. Each "
                "case is a three-item tuple and the loop unpacks it into a name, an input "
                "and an expected value, so the table reads as a specification and the "
                "loop reads as an execution of it. Because each case is a tuple, the "
                "table itself can be compared for equality between runs or stored, since "
                "its shape cannot drift; that stability is what makes a case table a "
                "trustworthy artefact rather than a pile of arguments. The reporting "
                "pattern is the useful transferable part: a failure names the case and "
                "both values, and the count of failures is tracked separately from the "
                "loop, so a suite can report a summary without stopping at the first "
                "problem. Choosing a tuple here is what tells the next reader that every "
                "case has exactly those three parts."
            ),
            "example_hint": "run a table of tuple test cases and report failures with the case name",
            "assessment_angle": "what the case table's fixed shape buys and how failures are reported",
            "day": 6,
            "title": "A Case Table of Fixed Records: Run It, Name the Failures",
            "code": """def normalise(text):
    return " ".join(text.split()).lower()


cases = [
    ("mixed case", "  Hello ", "hello"),
    ("extra spaces", "a   b", "a b"),
    ("tabs collapse", "a\\tb", "a b"),
    ("already clean", "ok", "ok"),
]

failures = 0
for name, given, expected in cases:
    actual = normalise(given)
    if actual != expected:
        failures += 1
        print(f"FAIL {name}: got {actual!r}, want {expected!r}")

print(f"ran {len(cases)} cases, {failures} failed")
print("table is a tuple of:", type(cases[0]).__name__, "length", len(cases[0]))
""",
            "questions": [
                "What does unpacking each case into name, given, expected tell a reader about the table?",
                "Why is the failure count kept in a variable rather than raised on the first failure?",
                "What makes the case table a stable artefact that could be compared between runs?",
            ],
            "answers": [
                "That every case is a fixed record of a name, an input and an expected value, so the table reads as a specification of behaviour rather than as a list of arguments.",
                "So the suite reports a summary of all failures instead of stopping at the first one, which is what makes a run useful when several cases are broken.",
                "The tuples' fixed length and immutability, so no case can change shape or content while the table is stored, transported or compared.",
            ],
            "homework": (
                "Write case_table.py with a normalise function and a list of at least six test "
                "cases, each a tuple of a case name, an input and an expected value, including two "
                "deliberately wrong expectations. Loop over the table unpacking three names, "
                "compare the result, and print a line naming every failing case with both values, "
                "then print how many cases ran and how many failed. Observable output: two failure "
                "lines and a summary line."
            ),
            "required_patterns": ["for ", "f\"", "len(", "!=", "print("],
        },
        "devops-scripting": {
            "framing": (
                "An inventory row is a host with a role and a region, and a "
                "host-to-attributes mapping keyed on a tuple keeps that grouping exact."
            ),
            "application": (
                "Walk the example as an inventory being grouped. Each host's attributes "
                "are stored as a tuple, and grouping is done by a tuple key of role and "
                "region, so the counts are exact because the key is hashable and its "
                "shape cannot change between grouping and reporting. Unpacking the key "
                "when printing turns a count into a labelled row, and the fixed positional "
                "meaning is what makes the grouping readable rather than a pair of bare "
                "values. The transferable pattern is keyed aggregation with a compound "
                "key: whenever a script groups by more than one field, the tuple is the "
                "type that expresses the combination, and the alternative of concatenating "
                "strings loses the boundary between fields and invites collisions. When "
                "two different field combinations would produce the same joined string, "
                "the tuple keeps them distinct."
            ),
            "example_hint": "group inventory rows by a tuple key and unpack the groups when reporting",
            "assessment_angle": "why grouping uses a tuple key and what a joined string would cost",
            "day": 6,
            "title": "Group by Role and Region: The Tuple Key Keeps Them Exact",
            "code": """hosts = [
    ("web-1", "web", "us"), ("web-2", "web", "us"), ("web-3", "web", "eu"),
    ("db-1", "db", "us"), ("db-2", "db", "eu"), ("cache-1", "cache", "eu"),
]

groups = {}
for name, role, region in hosts:
    key = (role, region)
    groups.setdefault(key, []).append(name)

for (role, region), names in sorted(groups.items()):
    print(f"{role:<6} {region:<3} {len(names)} -> {', '.join(names)}")

print("groups:", len(groups))
print("string key collision check:", ("web", "eu") in groups)
""",
            "questions": [
                "Why is the group key a tuple of role and region rather than a joined string?",
                "What does setdefault contribute to the grouping loop?",
                "The reporting loop unpacks (role, region), names. What makes that unpacking safe for every key?",
            ],
            "answers": [
                "Because the tuple keeps the two fields as separate positions, so no two different combinations can collide the way they could in a joined string, and it is hashable so it can key the dictionary.",
                "It creates the list for a new key on first use and returns the existing one otherwise, so the append always has somewhere to go without a separate membership test.",
                "Every key is a tuple of exactly two items built the same way, so unpacking into two names always matches and never raises.",
            ],
            "homework": (
                "Write inventory_groups.py with a list of at least twelve host records, each a "
                "tuple of name, role and region. Group the names in a dictionary keyed by a tuple "
                "of role and region using setdefault, then print each group with the key unpacked "
                "into two names, the count and the joined host names. Finally print the number of "
                "groups and a membership check on one tuple key. Observable output: one line per "
                "group plus two closing lines."
            ),
            "required_patterns": ["(,", "setdefault", "sorted(", "len(", "print("],
        },
        "algo-trading": {
            "framing": (
                "An order is a fixed record of side, symbol and quantity, and a fill is a "
                "tuple of price and size. Neither shape changes between entry and "
                "reconciliation."
            ),
            "application": (
                "Walk the example as orders being matched against fills. Each fill is a "
                "tuple of price and size, and unpacking it in the matching loop makes the "
                "arithmetic state which value is which, which matters because a swap of "
                "price and size would produce a nonsense notional. Using a tuple key to "
                "record the best price seen per symbol is what puts the type to work, "
                "since a compound key needs to be hashable. The immutability is the "
                "property that matters for reconciliation: an order record created at "
                "entry time cannot be edited by the matching loop, so the reconciliation "
                "at the end can compare the orders against the fills and trust that the "
                "entry data is unchanged, which is exactly the guarantee a trading "
                "system needs before it reports a profit figure."
            ),
            "example_hint": "match fixed-shape fills against orders, key the best price per symbol",
            "assessment_angle": "what immutability guarantees for reconciliation and why unpacking matters",
            "day": 6,
            "title": "An Order Keeps Its Shape from Entry to Reconciliation",
            "code": """orders = [("buy", "AAPL", 100), ("sell", "MSFT", 40), ("buy", "TSLA", 200)]
fills = [(182.41, 100), (415.02, 40), (248.75, 150)]

best = {}
for (side, symbol, qty), (price, size) in zip(orders, fills):
    if symbol not in best or price > best[symbol]:
        best[symbol] = price

print("best prices:", sorted(best.items()))

notional = 0.0
for (side, symbol, qty), (price, size) in zip(orders, fills):
    matched = min(qty, size)
    notional += price * matched
    print(f"{side:<5} {symbol:<5} matched {matched} @ {price}")

print(f"total notional: {notional:,.2f}")
print("order still intact:", orders[0])
""",
            "questions": [
                "The matching loop unpacks each fill into price, size. What mistake does that make impossible, and why does it matter?",
                "What does the unchanged orders[0] at the end prove, and why does a trading system need it?",
                "Why is min(qty, size) the right matched quantity rather than qty alone?",
            ],
            "answers": [
                "It makes swapping the two values impossible, which matters because multiplying the wrong pair would produce a nonsensical notional figure reported as money.",
                "That the matching loop never edited the entry record, so a later reconciliation can compare the original orders against the fills and trust the entry data.",
                "Because a fill may be smaller than the order, so the matched quantity is whatever both sides actually share, not the amount that was requested.",
            ],
            "homework": (
                "Write reconcile_orders.py with lists of at least six orders and six fills, each "
                "an order tuple of side, symbol and quantity and a fill tuple of price and size. "
                "Zip them, unpack each pair, match the smaller of quantity and size, accumulate a "
                "notional and print one line per match with the side, symbol, matched quantity and "
                "price. Then print the total notional with a thousands separator and one order "
                "tuple to prove the entry record is unchanged. Observable output: one line per "
                "match plus two closing lines."
            ),
            "required_patterns": ["zip(", "min(", "for ", "f\"", "print("],
        },
        "numerical-methods": {
            "framing": (
                "A computed point on a curve is an x with its f of x, and a table of such "
                "pairs is a fixed record that a plotter or a solver can consume."
            ),
            "application": (
                "Walk the example as a function being tabulated. Each point is built as "
                "a pair, and unpacking it when searching for a sign change names both "
                "values, which is what makes the bracketing step readable: the code "
                "compares f values and reads the x that produced them, rather than "
                "indexing a pair twice. Because the points are tuples they can be stored "
                "in a set to detect that a sample was taken twice, and they can key a "
                "cache mapping a sample point to its value, which is what a solver does "
                "to avoid recomputing an expensive function at the same argument. The "
                "fixed length is the guarantee the consumer relies on, since a root "
                "bracketing algorithm assumes each entry is exactly an argument and its "
                "value, and the immutability is what lets that assumption survive every "
                "stage of the pipeline."
            ),
            "example_hint": "tabulate points as pairs, key a value cache, bracket a sign change",
            "assessment_angle": "what the pair's fixed shape guarantees for the solver and what caching buys",
            "day": 6,
            "title": "Tabulate the Curve: Fixed Pairs, Cached Values, One Bracket",
            "code": """def f(x):
    return x * x - 2.0


cache = {}
table = []
for x in (-2, -1, 0, 1, 2):
    if x not in cache:
        cache[x] = f(x)
    table.append((x, cache[x]))

for x, y in table:
    print(f"f({x}) = {y}")

bracket = None
for (xa, ya), (xb, yb) in zip(table, table[1:]):
    if ya == 0 or ya * yb < 0:
        bracket = (xa, xb)
        break

print("sign change between:", bracket)
print("cache size:", len(cache), "samples:", len(table))
""",
            "questions": [
                "What does keying the cache on the sample point let the tabulation avoid, and why can the point be a key?",
                "The bracketing loop unpacks (xa, ya), (xb, yb). What does each name hold, and what does the sign test look for?",
                "What does the fixed length of each table entry guarantee for the zip in the bracketing loop?",
            ],
            "answers": [
                "It avoids recomputing the function at an argument already evaluated, and the point can be a key because a tuple of numbers is hashable.",
                "xa and xb are consecutive arguments and ya and yb their values; the sign test looks for a product below zero, meaning the function crossed the axis between the two samples.",
                "That both halves of each zipped pair have exactly two positions, so unpacking into four names always succeeds and the loop never fails on a malformed entry.",
            ],
            "homework": (
                "Write tabulate_curve.py with a nonlinear function and a list of at least eight "
                "sample arguments. Tabulate the function into a list of argument-value tuples, "
                "caching each value in a dictionary keyed on the argument so repeated arguments are "
                "not recomputed, and print one line per point with both values unpacked into "
                "names. Then scan consecutive pairs for a sign change and print the bracketing "
                "interval, the cache size and the sample count. Observable output: one line per "
                "sample plus a bracket line and two counts."
            ),
            "required_patterns": ["(,", "zip(", "for ", "len(", "print("],
        },
    },
)
