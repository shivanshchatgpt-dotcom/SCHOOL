PHASE = ("Cleaning and Transforming Data",
         "Turn a messy export into a predictable table by inspecting, repairing and validating it in small, testable steps.",
         {
    90: dict(
        topic="Orientation: messy exports",
        idea=(
            "Messy exports rarely announce themselves. A file that looks fine in the grid may contain padded names, "
            "blank cells that mean different things, numbers stored as text, duplicate records and values that are "
            "simply wrong. The first job in any cleaning phase is not to fix anything but to look, because a fix "
            "applied before the problem is understood tends to hide it. Orientation means building a small inventory: "
            "for each row, which fields look suspicious, and across the sheet, how often each kind of problem appears. "
            "In code this is a scan that returns tags rather than edits. You keep the original data untouched, count "
            "what you find, and only then decide which repair belongs where. Doing it this way has a second benefit: "
            "the scan is a test you can run again after cleaning, and its count should fall to zero. Analysts often "
            "skip this step and start trimming, filling and deduplicating in one pass, then cannot explain why totals "
            "changed. A separate inspection pass also tells you whether a column is mostly empty, which may mean it "
            "should be dropped rather than filled. Today you tag a small export and print only the rows that need "
            "attention, plus a summary count that a later pass can drive down."
        ),
        code=r'''EXPORT = [
    {"name": "  Ada Lovelace ", "qty": "3", "price": "2.50", "note": ""},
    {"name": "Grace Hopper", "qty": "", "price": "9.00", "note": "rush"},
    {"name": "grace hopper", "qty": "1", "price": "9.00", "note": "rush"},
    {"name": "Alan Turing", "qty": "two", "price": "4.00", "note": None},
]

def issues(row):
    found = []
    if any(isinstance(v, str) and v != v.strip() for v in row.values()):
        found.append("padding")
    if any(v is None or (isinstance(v, str) and not v.strip()) for v in row.values()):
        found.append("blank")
    qty = row["qty"]
    if qty and not str(qty).strip().isdigit():
        found.append("bad_number")
    return found

for line_no, row in enumerate(EXPORT, 1):
    tags = issues(row)
    if tags:
        print(line_no, row["name"].strip(), tags)

flagged = sum(1 for row in EXPORT if issues(row))
print("rows:", len(EXPORT), "flagged:", flagged)''',
        variant_b='add a tag for rows whose name repeats another row after stripping and lowercasing',
        variant_c='collect the tags into a dict of counts per problem and print the counts instead of each row',
        mistakes=[
            "Cleaning while scanning, so the original evidence disappears before it is counted.",
            "Treating a blank string, a missing key and the text N/A as the same problem.",
            "Assuming text that looks numeric parsed as a number on import.",
        ],
        q1=(
            "Why scan for problems before repairing any of them?",
            "The scan preserves evidence, gives a baseline count to verify against, and stops a quick fix from hiding a structural issue.",
        ),
        homework=(
            "Write `audit_export(rows, fields)` that returns a dict mapping each field name to a list of row numbers "
            "where that field is blank, padded or non-numeric. Build a six-row in-memory list, print the dict, and "
            "comment which check would need a regex once names contain punctuation."
        ),
        patterns=["def audit_export", "for", "print("],
        mapping=(
            "Excel's filter arrows and conditional formatting are manual versions of this scan; openpyxl and pandas "
            "let you run the same inventory across thousands of rows before touching a single value."
        ),
    ),
    91: dict(
        topic="Trimming and normalising text",
        idea=(
            "Text from exports is full of invisible variation. A name may start with a stray space, contain a tab "
            "left by a copy-paste, use a non-breaking space, or differ from another row only in case. Humans read "
            "those as the same value; grouping, matching and deduplication do not. Normalising text means deciding on "
            "one canonical form and applying it consistently: strip the ends, collapse every run of whitespace to a "
            "single space, and pick a case convention. Lowercasing with `casefold` is safer than `lower` for "
            "comparisons because it handles more scripts, while display names often want title case instead. The "
            "important distinction is between a matching key and a display value. You may keep the title-cased name "
            "for the report but compare on a folded, whitespace-collapsed key. Doing both in one function hides that "
            "choice and makes later bugs hard to see, so write small helpers with clear names. Also resist stripping "
            "characters that carry meaning: removing all punctuation turns O'Brien into OBrien and mangles part "
            "numbers. Today you clean a handful of names, print the before and after visibly with `repr`, and sort "
            "the folded keys to show that values differing only in spacing and case collapse together. The set of keys "
            "is also the fastest way to see how many distinct values you actually have."
        ),
        code=r'''import re

def clean_text(value):
    return re.sub(r"\s+", " ", value.strip())

def match_key(value):
    return clean_text(value).casefold()

RAW = ["  Ada   Lovelace ", " grace\thopper", "ALAN  turing  ", "Ada Lovelace"]

for value in RAW:
    print(repr(value), "->", repr(clean_text(value)))

print("keys:", sorted({match_key(value) for value in RAW}))
print("unique keys:", len({match_key(value) for value in RAW}))''',
        variant_b='add a title-case display version and print both the display value and the folded match key',
        variant_c='replace runs of spaces but keep internal tabs, then explain why that is usually the wrong choice',
        mistakes=[
            "Using strip alone, which leaves doubled spaces inside the value untouched.",
            "Lowercasing the stored display name instead of keeping a separate comparison key.",
            "Stripping all punctuation, which destroys apostrophes and identifier characters.",
        ],
        q1=(
            "Why keep a folded match key separate from the display text?",
            "Comparisons need one predictable form, while reports should preserve the spelling and casing a human expects.",
        ),
        homework=(
            "Write `normalise_names(values)` that strips each value, collapses internal whitespace, and returns a "
            "list of `(display, key)` pairs where display is title case and key is casefolded. Print the pairs and "
            "assert that two inputs differing only by spacing share a key."
        ),
        patterns=["def normalise_names", "casefold", "print("],
        mapping=(
            "Power Query's Trim and Clean columns and pandas' `.str.strip()` / `.str.casefold()` express the same "
            "two-step idea: clean the display value, then build a stable key for joins and comparisons."
        ),
    ),
    92: dict(
        topic="Handling blank values",
        idea=(
            "A blank cell is ambiguous. It can mean zero, unknown, not applicable, or a failed lookup, and those "
            "meanings should not be collapsed by accident. Different tools also represent blankness differently: an "
            "empty string, a cell that was never written, the text N/A, a dash, or the word null pasted from another "
            "system. Before filling anything, write one predicate that answers whether a value counts as missing and "
            "keep its rules visible in a set. Then decide per column what a missing value should become. A quantity "
            "might default to zero, a price might stay missing so totals are not distorted, and a category might "
            "become the explicit label Unknown. Filling everything with zero is the classic mistake because it "
            "converts unknown into a confident wrong number. The other useful distinction is between filling for "
            "analysis and filling for display: a report can show a dash while the data keeps a real null. Today you "
            "classify several blank-looking values, fill some with a default, leave one deliberately missing, and "
            "count how many were changed. That count is the beginning of an audit trail that says how much of a "
            "column was invented rather than observed. Record the fill rule next to the column definition so the next "
            "reader knows what was assumed."
        ),
        code=r'''BLANK_TOKENS = {"", "n/a", "na", "null", "none", "-"}

def is_blank(value):
    if value is None:
        return True
    return isinstance(value, str) and value.strip().casefold() in BLANK_TOKENS

def fill(value, default):
    return default if is_blank(value) else value.strip()

ROWS = [
    {"city": " Pune ", "qty": None},
    {"city": "N/A", "qty": "0"},
    {"city": None, "qty": ""},
    {"city": "", "qty": "7"},
]

changed = 0
for row in ROWS:
    before_city, before_qty = row["city"], row["qty"]
    city = fill(row["city"], "Unknown")
    qty = fill(row["qty"], "missing")
    changed += (city != before_city) + (qty != before_qty)
    print(repr(before_city), repr(before_qty), "->", city, qty)

print("cells changed:", changed)
print("unknown cities:", sum(fill(r["city"], "Unknown") == "Unknown" for r in ROWS))''',
        variant_b='add a third column where blank means zero and show that its fill rule differs from the other two',
        variant_c='keep a parallel dict of flags recording which cells were filled so the report can show them',
        mistakes=[
            "Filling every blank with zero, turning unknown values into apparently measured ones.",
            "Checking only for `None` and missing empty strings and placeholder words.",
            "Filling before deduplicating, so records that were actually duplicates no longer match.",
        ],
        q1=(
            "Why is filling every blank with zero dangerous?",
            "It invents data: a missing measurement becomes a real zero and quietly biases sums, averages and counts.",
        ),
        homework=(
            "Write `fill_blanks(rows, rules)` where rules maps a field to either a default or None, meaning leave "
            "it blank. Return a new list of rows plus a count of filled cells, print both, and comment why one "
            "field is left unfilled."
        ),
        patterns=["def fill_blanks", "is_blank", "print("],
        mapping=(
            "pandas distinguishes `NaN`, `None` and empty strings, and openpyxl returns `None` for unwritten cells; "
            "an explicit blank-token set makes those differences deliberate instead of accidental."
        ),
    ),
    93: dict(
        topic="Coercing types safely",
        idea=(
            "Values arrive as text because a spreadsheet cell does not enforce a type. Converting them is necessary "
            "for arithmetic, but the conversion must fail in a way you can see. The unsafe pattern is a bare "
            "`int(value)` inside a loop: one bad row raises and the whole import stops, or a broad `except` swallows "
            "the row silently, and neither tells you how many values were lost. A safe converter returns a sentinel "
            "such as `None` on failure and lets the caller decide whether that is acceptable. `int` and `float` also "
            "have sharp edges. `int(\"3.0\")` fails, `float(\"1,200\")` fails because of the separator, and "
            "`int(True)` succeeds, so guard the input rather than the output. Write one helper per target type and "
            "keep them tiny. Then track failures with a count and, better, with the offending values so the report "
            "can name them. This is deliberately conservative: a value that does not parse is not guessed at, "
            "because a wrong guess is harder to detect later than an explicit failure. Today you convert a mixed "
            "list to integers and floats, print each result, and finish with a parse rate that tells you how much of "
            "the column survived. A parse rate that suddenly drops is an early warning that an upstream export changed."
        ),
        code=r'''def to_int(value):
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return None

def to_float(value):
    try:
        return float(str(value).replace(",", "").strip())
    except (TypeError, ValueError):
        return None

RAW = ["3", " 42 ", "1,200", "2.5", "", "n/a", "7"]

for value in RAW:
    print(repr(value), "int:", to_int(value), "float:", to_float(value))

parsed = sum(to_int(value) is not None for value in RAW)
print("integer parse rate:", parsed, "of", len(RAW))
print("failures:", [value for value in RAW if to_int(value) is None])''',
        variant_b='add `to_bool` accepting yes/no/true/false/1/0 and return None for anything else',
        variant_c='return a `(value, error)` pair instead of a sentinel and print the error text for each failure',
        mistakes=[
            "Letting one unparseable cell raise and abort the entire import.",
            "Catching every exception with a bare `except`, hiding typos in the converter itself.",
            "Guessing a value when parsing fails instead of returning an explicit failure.",
        ],
        q1=(
            "Why return `None` instead of raising or guessing when a value will not parse?",
            "The caller can count and report bad values without stopping the import, and no invented number enters the data.",
        ),
        homework=(
            "Write `safe_convert(values, kind)` where kind is the string `int` or `float`. Return two lists: "
            "converted values and rejected values. Print both lists, and comment how the caller should treat a "
            "rejected count above zero."
        ),
        patterns=["def safe_convert", "except", "print("],
        mapping=(
            "pandas offers `to_numeric(errors=\"coerce\")` and openpyxl gives raw cell types; wrapping conversion in "
            "your own helper preserves the rejected values that a coercing library call would replace with null."
        ),
    ),
    94: dict(
        topic="Renaming and normalising headers",
        idea=(
            "Headers are the contract between a sheet and your code, and exports break that contract constantly. "
            "One month the column is `Unit Price`, the next it is `unit price (USD)`, and a third source sends "
            "`Qty.`. Code that reads `row[\"Unit Price\"]` fails on two of those files. Normalising headers means "
            "mapping every spelling onto one canonical name your logic uses, and keeping that mapping in one place "
            "rather than scattering fallbacks through the code. A common convention is snake case: trim, lowercase, "
            "replace every run of non-alphanumeric characters with an underscore, then trim underscores from the "
            "ends. That turns `Unit Price (USD)` into `unit_price_usd`, which is stable, readable and easy to "
            "reference. Two cautions matter. First, normalisation can create collisions, such as `Order ID` and "
            "`Order-Id` both becoming `order_id`, so check that the result is unique and fail loudly if not. Second, "
            "keep a record of the original header, because the report may need to show the user the column they "
            "know. Today you normalise several awkward headers, print the old-to-new mapping, and assert that no two "
            "columns ended up with the same name. If a source renames a column every quarter, the mapping is the "
            "single place to update, and the rest of the pipeline keeps working unchanged."
        ),
        code=r'''import re

def normalise_header(name):
    text = name.strip().lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_")

HEADERS = [" Customer Name ", "Order ID", "Qty.", "Unit Price (USD)", "e-mail"]

MAPPING = {header: normalise_header(header) for header in HEADERS}
for old, new in MAPPING.items():
    print(repr(old), "->", new)

names = list(MAPPING.values())
print("unique:", len(set(names)) == len(names))
print("canonical:", sorted(names))''',
        variant_b='add a collision by including both Order ID and Order-Id, then print a warning instead of asserting',
        variant_c='build an explicit alias table mapping known spellings to canonical names and apply it first',
        mistakes=[
            "Normalising headers inside the row loop, repeating the work and hiding the mapping.",
            "Assuming normalisation cannot collide two different source columns.",
            "Discarding the original header that reports and support conversations refer to.",
        ],
        q1=(
            "Why check that normalised headers are unique?",
            "Two source columns can map to the same canonical name, which silently overwrites or conflates data.",
        ),
        homework=(
            "Write `normalise_headers(headers)` returning a dict from original to snake-case name, and raise "
            "`ValueError` if two originals collide. Print the mapping for five awkward headers and comment where "
            "the collision check runs."
        ),
        patterns=["def normalise_headers", "ValueError", "print("],
        mapping=(
            "pandas' `.rename(columns=...)` and openpyxl's header row both expect exact names; a normalisation "
            "mapping makes imports survive the small header changes that every recurring export eventually ships."
        ),
    ),
    95: dict(
        topic="Splitting one column into many",
        idea=(
            "A single text column often hides several fields. `Lovelace, Ada` contains a last name and a first name; "
            "`12 Mill Lane, Pune 411001` contains an address, a city and a postcode; a tags cell may hold three "
            "labels separated by semicolons. Splitting is the operation that turns that packed text into columns you "
            "can filter and join, but it is also where naive code does damage. `split()` with no argument collapses "
            "repeated separators, which may be what you want for tags but not for fixed-position data. "
            "`split(\",\")` on an address breaks when a line contains a comma inside a company name, so prefer a "
            "limit and strip each part. Names are especially tricky: not every culture writes family name first, and "
            "some people have three or four parts, so a split that assumes exactly two tokens will mislabel real "
            "records. The honest approach is to split with a documented rule, keep the original column, and flag "
            "values that do not match the expected shape rather than forcing them through. Today you split a "
            "`last, first` column, split a semicolon list into tags, and print both, including a value that has more "
            "parts than expected so the assumption becomes visible. Print the rejected shapes instead of dropping "
            "them quietly."
        ),
        code=r'''def split_name(value):
    last, separator, first = value.partition(",")
    if not separator:
        return None, None
    return first.strip(), last.strip()

def split_tags(value):
    return [part.strip().lower() for part in value.split(";") if part.strip()]

NAMES = ["Lovelace, Ada", "Hopper, Grace", "Turing, Alan", "Prince"]

for value in NAMES:
    first, last = split_name(value)
    print(repr(value), "->", first, last)

print("tags:", split_tags("math; logic ;; computing"))
print("missing comma:", sum(split_name(v)[0] is None for v in NAMES))''',
        variant_b='split `City, State ZIP` with `rsplit(",", 1)` and then separate the last token',
        variant_c='split on a semicolon but cap the number of results and report any extra remainder',
        mistakes=[
            "Using `split()` and unpacking into two names, which crashes on a single-token value.",
            "Splitting an address on every comma, so a company name inside the address is torn apart.",
            "Overwriting the original column before the split has been checked for odd shapes.",
        ],
        q1=(
            "Why use `partition` or a limited split instead of unpacking `split(\",\")` into two names?",
            "It handles values with no separator or extra separators without crashing or silently discarding parts.",
        ),
        homework=(
            "Write `split_location(value)` that takes `City, State ZIP` and returns a dict with city, state and "
            "postcode keys, returning None for the whole result when the shape is wrong. Print results for three "
            "values including one malformed value."
        ),
        patterns=["def split_location", "rsplit", "print("],
        mapping=(
            "Excel's Text to Columns and pandas' `.str.split(expand=True)` do the same job; the difference is that "
            "code can keep the original value and flag shapes that do not fit the rule."
        ),
    ),
    96: dict(
        topic="Merging columns together",
        idea=(
            "Merging is the inverse of splitting and just as easy to get subtly wrong. You combine several fields "
            "into one display string: a full address, a display name, a compound key. The first decision is the "
            "separator, and the second is what to do with missing parts. A naive `\" \".join(...)` on a list that "
            "contains `None` raises, and joining with a comma when one part is empty produces a doubled separator "
            "or a leading comma. The usual rule is to drop empty parts before joining, then use the separator only "
            "between real values. That single rule fixes most address labels. A second distinction is between a "
            "display merge and a matching key: display merges may use commas and title case, while keys should be "
            "folded, delimiter-safe and unambiguous. If the pieces can contain the delimiter, choose a separator "
            "that cannot appear in them or escape it, otherwise two different records can produce the same key. "
            "Today you join address parts while skipping blanks, print the labels, and build a folded compound key "
            "to show that formatting and identity are separate concerns. Keep the source columns; a merged string "
            "is for reading, not for recovering the parts later. A merged label should never be the only copy of "
            "its parts."
        ),
        code=r'''def join_parts(parts, separator=", "):
    cleaned = [str(part).strip() for part in parts if part is not None and str(part).strip()]
    return separator.join(cleaned)

def compound_key(parts):
    return "|".join(str(part).strip().casefold() for part in parts if str(part).strip())

ROWS = [
    {"line1": "12 Mill Lane", "city": "Pune", "postcode": "411001"},
    {"line1": "", "city": " Pune ", "postcode": ""},
    {"line1": "5 Hill Road", "city": "", "postcode": None},
]

for row in ROWS:
    label = join_parts([row["line1"], row["city"], row["postcode"]])
    print(label)

print("with pipes:", join_parts(["a", " ", "b"], " | "))
print("key:", compound_key(["Pune", " 411001 "]))''',
        variant_b='merge first and last name into a display name, skipping a missing middle name',
        variant_c='use an empty separator to build a fixed-width code and explain when that is useful',
        mistakes=[
            "Joining values that may be `None`, which raises before the empty check can help.",
            "Leaving separators around empty parts, producing doubled or trailing commas.",
            "Using a display string with commas as a matching key when the parts can contain commas.",
        ],
        q1=(
            "Why filter out empty parts before joining them?",
            "Otherwise the separator still appears for the missing value, creating doubled or leading delimiters that look like data.",
        ),
        homework=(
            "Write `merge_address(row)` that joins street, city and postcode with commas while skipping blanks, "
            "and `address_key(row)` that builds a delimiter-safe folded key. Print both for three rows including "
            "one with a missing city."
        ),
        patterns=["def merge_address", "join", "print("],
        mapping=(
            "Excel's `TEXTJOIN` with its ignore-empty flag is the spreadsheet version of this rule, and pandas' "
            "`.str.cat(sep=..., na_rep=\"\")` is the library version; both still need a deliberate key format."
        ),
    ),
    97: dict(
        topic="Removing duplicate rows",
        idea=(
            "Duplicates are rarely exact copies. One row has a trailing space in the email, another differs in case, "
            "and a third has the same customer but a newer timestamp. Deciding what counts as the same record is a "
            "business decision before it is a coding one. The practical technique is to define a key from the fields "
            "that identify a record, normalise those fields the same way you would for matching, and keep the first "
            "row seen for each key. Using a set of keys makes the pass linear and lets you count how many rows were "
            "dropped. The word first matters: input order determines which row survives, so sort deliberately "
            "before deduplicating if the newest or most complete record should win. A simple `set(rows)` approach "
            "only works for hashable exact rows and is usually the wrong tool because it cannot express the key. "
            "Also report the duplicates rather than deleting them silently; a high count often means an export was "
            "run twice or a join fanned out. Today you deduplicate by normalised email, keep the first occurrence, "
            "print the surviving names and the number removed, and note why the key choice determines the result, printing a couple of the dropped rows so the key choice can "
            "be reviewed."
        ),
        code=r'''def dedupe(rows, key_fields):
    seen = set()
    kept = []
    for row in rows:
        key = tuple(str(row[field]).strip().casefold() for field in key_fields)
        if key in seen:
            continue
        seen.add(key)
        kept.append(row)
    return kept

ROWS = [
    {"email": "ada@example.com", "name": "Ada"},
    {"email": " ADA@example.com ", "name": "Ada L."},
    {"email": "grace@example.com", "name": "Grace"},
    {"email": "ada@example.com", "name": "Ada again"},
]

KEPT = dedupe(ROWS, ["email"])
for row in KEPT:
    print(row["name"], "<" + row["email"].strip() + ">")

print("kept:", len(KEPT), "removed:", len(ROWS) - len(KEPT))''',
        variant_b='keep the last occurrence instead of the first by iterating in reverse and reversing the result',
        variant_c='deduplicate on `(email, name)` and show which extra row survives compared with email alone',
        mistakes=[
            "Using `set(rows)` on dicts, which raises because rows are not hashable.",
            "Comparing raw values, so case and padding differences defeat the duplicate check.",
            "Deleting duplicates without a count, hiding a double export or a fan-out join.",
        ],
        q1=(
            "Why does the choice of key fields change which rows survive?",
            "The key defines what counts as the same record, so a narrower key merges more rows and a wider key keeps more of them.",
        ),
        homework=(
            "Write `dedupe_rows(rows, keys)` that keeps the first row per normalised key and returns `(kept, "
            "removed_count)`. Print both for a five-row list containing case and spacing variants, and comment who "
            "decides the key."
        ),
        patterns=["def dedupe_rows", "seen", "print("],
        mapping=(
            "pandas' `drop_duplicates(subset=...)` and Excel's Remove Duplicates dialog both ask for the key columns; "
            "normalising them first is what makes the result agree with a human's idea of the same record."
        ),
    ),
    98: dict(
        topic="Filtering rows by rules",
        idea=(
            "Filtering looks trivial until the rules interact. A row should be kept when the status is active, the "
            "quantity is at least five and the postcode is in the service area, but what happens when one of those "
            "fields is missing? A bare chain of `and` conditions either crashes on `None` or silently drops the row, "
            "and the two outcomes mean different things. The usual approach is to write a predicate function with a "
            "clear name and keep each rule on its own line so the combination is visible. Return false early for a "
            "missing field only when missing means ineligible; otherwise decide explicitly. Also distinguish "
            "inclusion rules from exclusion rules. It is easier to reason about a predicate that says what to keep "
            "than one with several negations, and easier to test a small predicate directly with hand-written rows. "
            "Counts are the other half of trust: print how many rows were kept, dropped and dropped for each "
            "reason, because a filter that removes everything usually has one inverted comparison. Today you filter "
            "a small list with three rules, print the surviving ids, and report the kept and dropped totals. The "
            "same predicate can later be reused by a validation report."
        ),
        code=r'''def keep(row):
    if row["status"] != "active":
        return False
    if row["qty"] < 5:
        return False
    return row["postcode"].startswith("41")

ROWS = [
    {"id": 1, "status": "active", "qty": 12, "postcode": "411001"},
    {"id": 2, "status": "paused", "qty": 20, "postcode": "411002"},
    {"id": 3, "status": "active", "qty": 3, "postcode": "411003"},
    {"id": 4, "status": "active", "qty": 7, "postcode": "560001"},
    {"id": 5, "status": "active", "qty": 5, "postcode": "410001"},
]

KEPT = [row for row in ROWS if keep(row)]
print("kept ids:", [row["id"] for row in KEPT])
print("kept:", len(KEPT), "dropped:", len(ROWS) - len(KEPT))
print("all kept active:", all(row["status"] == "active" for row in KEPT))''',
        variant_b='replace the postcode prefix rule with a set membership test and print which ids leave the result',
        variant_c='add a rule that rows with missing qty are kept but flagged, and show the difference in counts',
        mistakes=[
            "Combining negations until the predicate is unreadable and the intent is lost.",
            "Assuming a row with a missing field should be dropped without deciding what missing means.",
            "Not counting dropped rows, so a filter that removes everything looks like clean data.",
        ],
        q1=(
            "Why write the filter as a named predicate instead of one long list comprehension condition?",
            "A named predicate can be tested with hand-written rows, reused by other passes, and documents what to keep.",
        ),
        homework=(
            "Write `select_rows(rows, min_qty, prefix)` returning kept and dropped lists. Print the kept ids and "
            "the count dropped for each of the three rules, and comment which order of checks avoids a missing "
            "field error."
        ),
        patterns=["def select_rows", "return", "print("],
        mapping=(
            "Excel's AutoFilter and pandas' boolean masks express the same predicate; naming the rule in code makes "
            "it testable and keeps the filtering logic out of the reporting layer."
        ),
    ),
    99: dict(
        topic="Sorting rows deterministically",
        idea=(
            "Sorting is a transformation that people trust, which makes a hidden instability expensive. Python's "
            "sort is stable, so equal keys keep their input order, but that order may come from a file and can "
            "change between exports. A deterministic sort therefore needs enough key fields to break ties: sort by "
            "score, then by date, then by name. It also needs a rule for missing values, because comparing `None` "
            "to an integer raises. A common trick is to prepend a boolean such as `value is None`, because `False` "
            "sorts before `True`, placing real values first. Descending order adds another trap: negating a numeric "
            "score is easy but impossible for strings, so `reverse=True` is usually clearer, though it reverses all "
            "fields at once. If one field must ascend and another descend, negate the numeric one or sort in stages, "
            "which is safe because the sort is stable. Finally, sort a copy rather than the caller's list unless "
            "in-place behaviour is explicitly wanted. Today you sort rows by score descending with missing scores "
            "last, then by date and name, and print the result along with a check that the tie order is fixed. The goal is an order that a reader can "
            "reproduce from the data alone, without knowing which file was loaded first."
        ),
        code=r'''ROWS = [
    {"name": "Ada", "score": 90, "joined": "2024-02-01"},
    {"name": "Grace", "score": 90, "joined": "2023-11-15"},
    {"name": "Alan", "score": None, "joined": "2024-01-05"},
    {"name": "Barbara", "score": 85, "joined": "2024-01-05"},
]

def sort_key(row):
    score = row["score"]
    return (score is None, -(score or 0), row["joined"], row["name"])

ORDERED = sorted(ROWS, key=sort_key)
for row in ORDERED:
    print(row["name"], row["score"] or "missing", row["joined"])

print("stable ties:", [row["name"] for row in ORDERED if row["score"] == 90])
print("original untouched:", ROWS[0]["name"])''',
        variant_b='sort by date ascending then name ascending, and show that reversing only the date needs a staged sort',
        variant_c='sort with a text key and a `None` mixed in without the boolean guard to see the failure',
        mistakes=[
            "Sorting only on a non-unique field and assuming the remaining order is meaningful.",
            "Comparing `None` with numbers directly, which raises a `TypeError`.",
            "Sorting the caller's list in place when a new ordered list was expected.",
        ],
        q1=(
            "Why include extra fields in a sort key beyond the obvious one?",
            "Without tie-breakers the order of equal rows depends on input order, which can change between exports.",
        ),
        homework=(
            "Write `sort_rows(rows, fields)` supporting one ascending and one descending field with missing values "
            "last. Print the ordered names and assert that the original list is unchanged, and comment where the "
            "tie-breaker is applied."
        ),
        patterns=["def sort_rows", "sorted", "print("],
        mapping=(
            "pandas' `sort_values` takes a list of columns and `na_position`; the same discipline applies, because a "
            "report sorted on one column alone can reshuffle equal rows on every refresh."
        ),
    ),
    100: dict(
        topic="Derived and calculated columns",
        idea=(
            "A derived column is a value computed from other fields rather than typed in. Line totals, margins, "
            "age bands and flags all belong here. The attraction is that derived values cannot drift out of sync "
            "with their inputs, but only if the formula is written once and applied everywhere. Two hazards dominate. "
            "The first is numeric type: floats cannot represent most decimal fractions exactly, so money computed as "
            "`qty * float(price)` accumulates tiny errors that surface when totals are compared. The `decimal` module "
            "with an explicit rounding mode avoids that, and it makes the rounding rule visible. The second hazard "
            "is treating a derived column as source data: if someone edits the quantity later, the stored total is "
            "now stale. Prefer recomputing derived fields at read time or clearly marking a materialised column as "
            "generated. Missing or invalid inputs also need a policy: produce `None` rather than zero so a bad row "
            "does not contribute a plausible-looking amount. Today you compute line totals from quantity and price "
            "with `Decimal`, round only at the end, accumulate a grand total, and print each line so the arithmetic "
            "can be checked by eye. Name the rounding rule once and reuse it for every money column so reports agree "
            "to the cent."
        ),
        code=r'''from decimal import Decimal, ROUND_HALF_UP

CENT = Decimal("0.01")

def line_total(row):
    quantity = Decimal(row["qty"])
    price = Decimal(row["price"])
    return (quantity * price).quantize(CENT, rounding=ROUND_HALF_UP)

ROWS = [
    {"sku": "A1", "qty": "3", "price": "2.505"},
    {"sku": "B2", "qty": "2", "price": "9.99"},
    {"sku": "C3", "qty": "0", "price": "4.00"},
]

grand = Decimal("0")
for row in ROWS:
    total = line_total(row)
    grand += total
    print(row["sku"], row["qty"], "x", row["price"], "=", total)

print("grand total:", grand.quantize(CENT))
print("rows with value:", sum(line_total(row) > 0 for row in ROWS))''',
        variant_b='add a discount percentage column and compute the discounted total with the same rounding rule',
        variant_c='compute the total with plain floats and print the difference on a value like 0.1 + 0.2',
        mistakes=[
            "Rounding each unit price before multiplying, which changes the total compared with the invoice.",
            "Using binary floats for money and assuming the tiny residue is harmless.",
            "Storing a derived total as if it were source data that survives later edits.",
        ],
        q1=(
            "Why use `Decimal` rather than float for a money total?",
            "Decimal represents the written value exactly and makes the rounding rule explicit, while floats leave small residues that break comparisons.",
        ),
        homework=(
            "Write `add_line_totals(rows, qty_field, price_field)` returning new rows with a rounded `total` key "
            "and a grand total. Print each row and the grand total, and comment why rounding happens after "
            "multiplication."
        ),
        patterns=["def add_line_totals", "Decimal", "print("],
        mapping=(
            "Excel stores numbers as binary doubles too, which is why invoice formulas often wrap results in "
            "`ROUND`; pandas' `.round()` plays that role, and `Decimal` is the stricter option in Python."
        ),
    ),
    101: dict(
        topic="Parsing dates and numbers",
        idea=(
            "Dates and numbers look unambiguous until they cross a border. `03/04/2024` is March the fourth in one "
            "convention and April the third in another, and no amount of staring at the string resolves it. That is "
            "why a parser should require an explicit format rather than guess. `strptime` with a fixed pattern is "
            "deterministic and fails loudly when the input does not match, which lets you try a short list of known "
            "formats in a documented order and report anything left over. Never use `today` or `now` in a transform: "
            "the output would change overnight and tests would drift. Numbers have parallel issues. Thousands "
            "separators and currency symbols must be removed deliberately, percentages need dividing by one hundred, "
            "and a decimal comma conflicts with a thousands dot. Keep the cleaning steps separate from the "
            "conversion so each is visible. Dates should end up as ISO strings or date objects, never as ambiguous "
            "text, and numbers as `Decimal` or a float when the precision does not matter. Today you parse dates from "
            "three fixed formats, parse money with a symbol and separators, and print a `None` for the strings that "
            "do not fit any rule, with their row numbers so the owner can fix the source."
        ),
        code=r'''from datetime import datetime

def parse_date(value):
    for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d %b %Y"):
        try:
            return datetime.strptime(value.strip(), fmt).date().isoformat()
        except ValueError:
            continue
    return None

def parse_money(value):
    text = value.strip().replace("$", "").replace(",", "")
    try:
        return round(float(text), 2)
    except ValueError:
        return None

for value in ["31/01/2024", "2024-02-15", "03 Mar 2024", "15/31/2024"]:
    print(repr(value), "->", parse_date(value))

print("amounts:", [parse_money(v) for v in ["$1,200.50", "89.999", "n/a"]])
print("formats tried:", 3)''',
        variant_b='add the format `%d-%m-%Y` after the existing ones and show which date now parses',
        variant_c='parse a percentage string by stripping the sign and dividing by one hundred, keeping two decimals',
        mistakes=[
            "Letting a library guess the day and month order, which silently swaps dates around the twelfth.",
            "Using `datetime.now` inside a transform, making output and tests depend on the run date.",
            "Forgetting to strip a currency symbol before numeric conversion.",
        ],
        q1=(
            "Why pass an explicit format to `strptime` instead of guessing the date order?",
            "An explicit format is deterministic and rejects values that do not match, while guessing can silently swap day and month.",
        ),
        homework=(
            "Write `parse_records(rows)` that converts a `date` field using three fixed formats and an `amount` "
            "field with symbols and separators removed. Print parsed and rejected rows separately, and comment why "
            "no current date is used."
        ),
        patterns=["def parse_records", "strptime", "print("],
        mapping=(
            "Power Query's locale setting and pandas' `to_datetime(format=...)` exist because guessing is unreliable; "
            "stating the format is the same reason openpyxl returns dates rather than preformatted strings."
        ),
    ),
    102: dict(
        topic="Bounds and sanity checks",
        idea=(
            "Type conversion answers whether a value can be represented; sanity checks answer whether it makes sense. "
            "A quantity of minus four is a valid integer, and so is five thousand, but neither is credible for a "
            "retail order. Bounds checks encode those expectations as explicit rules: a minimum, a maximum, a set of "
            "allowed labels, and relationships between fields such as an end date that cannot precede a start date. "
            "Keeping the rules in one function that returns a list of problems, rather than raising on the first "
            "failure, lets a row report everything wrong with it at once. That matters for the person fixing the "
            "source, who would rather see three issues than discover them one run at a time. Distinguish hard "
            "failures from warnings: an impossible date range is a failure, while an unusually large quantity might "
            "only deserve a flag. Both can be returned, tagged, and counted. Be careful with inclusive boundaries: "
            "write `0 <= qty <= 1000` and test the exact edges rather than relying on intuition. Today you check "
            "range, sign and cross-field ordering on four rows, print the problems per row, and finish with a count "
            "of clean rows so the effect of the checks is measurable."
        ),
        code=r'''def check(row):
    problems = []
    if not 0 <= row["qty"] <= 1000:
        problems.append("qty out of range")
    if row["price"] < 0:
        problems.append("negative price")
    if row["end"] < row["start"]:
        problems.append("end before start")
    return problems

ROWS = [
    {"id": 1, "qty": 5, "price": 2.5, "start": 10, "end": 20},
    {"id": 2, "qty": 5000, "price": 2.5, "start": 10, "end": 20},
    {"id": 3, "qty": 5, "price": -1.0, "start": 20, "end": 10},
    {"id": 4, "qty": 0, "price": 0.0, "start": 0, "end": 0},
]

bad = [(row["id"], check(row)) for row in ROWS if check(row)]
for row_id, problems in bad:
    print("id", row_id, problems)

print("clean:", len(ROWS) - len(bad), "of", len(ROWS))
print("range edges accepted:", check({"qty": 1000, "price": 0, "start": 1, "end": 1}))''',
        variant_b='split problems into errors and warnings and print them under separate headings',
        variant_c='add an allowed-status set and show a row failing it alongside a row failing only a warning',
        mistakes=[
            "Using `0 < qty < 1000`, which rejects the valid boundary values at both ends.",
            "Raising on the first problem, so a row with three issues takes three runs to fix.",
            "Treating every out-of-range value as fatal when some are only worth flagging.",
        ],
        q1=(
            "Why return all problems for a row instead of raising on the first one?",
            "The person repairing the source can fix every issue in one pass, and the report looks the same on each run.",
        ),
        homework=(
            "Write `check_row(row)` returning a list of problems for quantity, price and date order, using "
            "inclusive bounds. Print the problems for three rows including the exact boundary values, and comment "
            "which problem is a warning rather than a failure."
        ),
        patterns=["def check_row", "problems", "print("],
        mapping=(
            "Excel Data Validation encodes ranges at entry time, while pandas and openpyxl checks run afterwards; "
            "both work best when the boundary values are written explicitly and tested."
        ),
    ),
    103: dict(
        topic="Validation reports for bad rows",
        idea=(
            "A validation report is the hand-off between cleaning code and the humans who own the data. It should "
            "answer three questions quickly: which rows are bad, what exactly is wrong with each, and how many of "
            "each problem exist. The first design choice is the unit of the report. A list of `(row_number, "
            "problems)` entries is more useful than a single exception, because it survives multiple failures and "
            "can be printed, stored or attached to an email. Row numbers should match what the user sees in the "
            "spreadsheet, which usually means adding two to a zero-based index: one for the header and one because "
            "spreadsheets start at one. Keep machine-readable identifiers such as the record id alongside the "
            "human-readable row number, since ids survive sorting and re-exports. It also helps to separate missing "
            "required fields from malformed values, because the fixes differ. Finally, do not let the report depend "
            "on printing: return a structure, then render it in whatever format the moment needs. Today you validate "
            "a small export for required fields and a malformed email, print one line per bad row, and finish with a "
            "count and a summary by problem type. Silent fixes are the enemy here; a report makes the cleaning "
            "visible and reviewable."
        ),
        code=r'''def validate_rows(rows, required):
    report = []
    for line_no, row in enumerate(rows, start=2):
        problems = []
        for field in required:
            value = row.get(field)
            if value is None or (isinstance(value, str) and not value.strip()):
                problems.append("missing " + field)
        email = row.get("email")
        if email and "@" not in email:
            problems.append("bad email")
        if problems:
            report.append((line_no, row.get("id"), problems))
    return report

ROWS = [
    {"id": 1, "email": "ada@example.com", "city": "Pune"},
    {"id": 2, "email": "", "city": "Pune"},
    {"id": 3, "email": "grace.example.com", "city": "Pune"},
    {"id": 4, "email": "alan@example.com", "city": ""},
]

REPORT = validate_rows(ROWS, ["email", "city"])
for line_no, row_id, problems in REPORT:
    print("row", line_no, "id", row_id, ":", "; ".join(problems))

print("bad rows:", len(REPORT), "of", len(ROWS))
print("clean:", len(ROWS) - len(REPORT))''',
        variant_b='add a severity column to each problem and print errors before warnings',
        variant_c='group the report by problem text and print counts per issue instead of per row',
        mistakes=[
            "Raising on the first bad row, which hides all later rows from the report.",
            "Reporting a zero-based index that does not match the row number the spreadsheet shows.",
            "Fixing bad values silently inside the validator, so nothing reaches the data owner.",
        ],
        q1=(
            "Why report both row numbers and record ids?",
            "Row numbers match what the user sees now, while ids still identify the record after sorting or a new export.",
        ),
        homework=(
            "Write `build_report(rows, required)` returning a list of dicts with line, id and problems keys. Print "
            "one line per bad row plus a count by problem, and comment why the report returns data instead of "
            "printing inside the validator."
        ),
        patterns=["def build_report", "enumerate", "print("],
        mapping=(
            "This is the scripted version of Excel's error-checking and of a pandas assertion suite: the validator "
            "returns findings, and a separate renderer decides whether they become a console line, a column or a file."
        ),
    ),
    104: dict(
        topic="Review: cleaning and transforming checklist",
        idea=(
            "The review day is about sequence, not new syntax. Cleaning goes wrong most often because steps are "
            "applied in an order that destroys the evidence needed by a later step. A workable order is: inspect and "
            "count, normalise text, resolve blanks, coerce types, repair headers, split or merge as needed, "
            "deduplicate, filter, derive, parse, then validate. Each step is a small function over a list of dicts, "
            "so each can be tested alone and composed in a pipeline. The checklist should also say what is allowed "
            "to change. Keep the raw rows, write a cleaned copy, and record counts before and after every step that "
            "removes or invents data. If the totals do not reconcile, the difference tells you which step is "
            "suspect. Determinism is part of the checklist too: fixed date formats, explicit sort keys, no current "
            "time, no unseeded randomness. Finally, remember that cleaning is not the goal. The goal is a table that "
            "answers a question or feeds a report, so stop when the remaining problems do not affect that use. "
            "Today you run one small export through tidy, deduplicate, derive and validate in sequence, print the "
            "surviving rows and the before-and-after counts, and treat the pipeline itself as the review artifact."
        ),
        code=r'''ROWS = [
    {"name": " Ada  Lovelace ", "qty": "3", "price": "2.50"},
    {"name": "grace hopper", "qty": "", "price": "9.00"},
    {"name": "ADA LOVELACE", "qty": "3", "price": "2.50"},
]

def tidy(row):
    return {
        "name": " ".join(row["name"].split()).title(),
        "qty": int(row["qty"]) if row["qty"].strip() else 0,
        "price": float(row["price"]),
    }

TIDY = [tidy(row) for row in ROWS]

seen = set()
CLEAN = []
for row in TIDY:
    key = (row["name"].casefold(), row["qty"], row["price"])
    if key not in seen:
        seen.add(key)
        CLEAN.append(row)

for row in CLEAN:
    print(row["name"], row["qty"], row["price"])

print("rows in:", len(ROWS), "rows out:", len(CLEAN))
print("all quantities valid:", all(row["qty"] >= 0 for row in CLEAN))''',
        variant_b='reorder the pipeline so deduplication runs before type conversion and print the changed row count',
        variant_c='add a validation step that rejects rows with a zero quantity and show the final count',
        mistakes=[
            "Filling blanks before deduplicating, so records that should match no longer do.",
            "Running steps as one large function where no intermediate count can be checked.",
            "Continuing to clean after the remaining issues no longer affect the intended report.",
        ],
        q1=(
            "Why keep the raw rows and write cleaned output to a new list?",
            "The original evidence stays available for recounting, comparison and debugging when a later step changes the totals.",
        ),
        homework=(
            "Write `clean_pipeline(rows)` that tidies text, fills a missing quantity with zero, removes duplicates "
            "and validates the result, returning cleaned rows plus an audit dict of counts. Print the rows and the "
            "audit, and comment the order of the steps."
        ),
        patterns=["def clean_pipeline", "audit", "print("],
        mapping=(
            "This is the same shape as a pandas method chain or a Power Query applied-steps list: small named steps, "
            "a visible order, and counts recorded between steps so a surprising total can be traced."
        ),
    ),
})
