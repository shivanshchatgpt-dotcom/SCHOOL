"""Web Scraping phase 3, days 105-119: structuring and storing data.

The scrape is finished once pages become rows; this phase is about making those
rows trustworthy and durable. Every example is stdlib-only and works on
in-memory fixtures: dictionaries, strings, CSV text, JSON lines and an
in-memory SQLite database. Nothing here touches a network, so the storage
decisions can be practised without a live site.
"""

PHASE = (
    "Structuring and Storing Data",
    "Turn raw scraped rows into consistent, validated, deduplicated records and store them without losing or corrupting data.",
    {
        105: dict(
            topic="Records are dictionaries",
            idea=(
                "A scraped row becomes useful the moment it stops being a stretch of text and starts being a "
                "record. For this track a record is a dictionary with a fixed set of keys, and each key carries "
                "a value of the right type: the title is a string, the price is a float, the stock flag is a "
                "boolean. That contract lets the next stage work without re-reading the page. It also "
                "makes mistakes visible. If a parser returns the price as '9.99' instead of 9.99, arithmetic "
                "later either fails or silently concatenates text; if two rows have different key sets, one row "
                "is incomplete and downstream cleaning cannot invent the absent meaning. A good "
                "record also keeps a deliberate vocabulary. Decide once whether the field is called "
                "price or price_text, whether a missing value is None or an empty string, and whether the "
                "source URL belongs in the row or in a separate provenance column. Scrapers that improvise "
                "field names page by page end up with a table that contains three spellings of the same idea "
                "and no way to tell which one is authoritative. Today's exercise builds records from "
                "positional parser output, then checks the key set and the value types. Treat the check as part "
                "of the record: a row that fails it should be rejected or repaired "
                "before it reaches storage, because a dictionary is the last place where fixing it is cheap."
            ),
            code=(
                'parts_rows = [\n'
                '    ["Dune", "9.99", "in stock"],\n'
                '    ["Foundation", "12.50", "out of stock"],\n'
                ']\n'
                '\n'
                'def make_record(parts):\n'
                '    title, price_text, stock_text = parts\n'
                '    return {\n'
                '        "title": title,\n'
                '        "price": float(price_text),\n'
                '        "in_stock": stock_text == "in stock",\n'
                '    }\n'
                '\n'
                'required = {"title", "price", "in_stock"}\n'
                'records = [make_record(parts) for parts in parts_rows]\n'
                'for record in records:\n'
                '    assert set(record) == required, set(record)\n'
                '\n'
                'print("records:", len(records))\n'
                'print("first:", records[0])\n'
                'print("types:", {key: type(value).__name__ for key, value in records[0].items()})\n'
                'assert all(isinstance(row["price"], float) for row in records)\n'
                'print("schema and types agree")'
            ),
            variant_b='parts_rows uses ["The Left Hand of Darkness", "18", "yes"] and a second row with "no"',
            variant_c='add a "currency" key to the required set but omit it from make_record; explain the assertion',
            mistakes=[
                "Leaving price as text, so later arithmetic concatenates instead of adding.",
                "Letting rows carry different key sets, which silently makes one record incomplete.",
                "Choosing field names ad hoc per page, so the same concept arrives under several spellings.",
            ],
            q1=(
                "Why is a dictionary a better row container than the parser's positional list?",
                "Names survive reordering and parser changes, and a wrong key fails at the line that reads it instead of returning a plausible wrong value.",
            ),
            homework=(
                "Write `make_record(parts)` that converts a three-item list (title, price text, stock text) into "
                "a typed dictionary and checks the required key set. Run it on two different lists, print both "
                "records and their value types, and comment which line performs the type conversion."
            ),
            patterns=["def ", "{", "assert"],
            mapping=(
                "ETL tools such as pandas and dbt assume named columns for the same reason: a record without "
                "stable names cannot be joined, filtered or trusted. A DataFrame row is this dictionary with "
                "indexing and column types bolted on."
            ),
        ),
        106: dict(
            topic="Normalising whitespace and text",
            idea=(
                "Scraped text is full of invisible differences that look identical on screen. A title can carry "
                "a leading space, a non-breaking space between words, a zero-width character from a lazy "
                "template, a newline in the middle, or repeated spaces left by collapsed markup. Two rows that "
                "read the same to a human can compare unequal in Python, which breaks deduplication, joins and "
                "grouping. Normalisation is the deliberate reduction of those differences to one canonical "
                "form before the value is stored. The useful order is to replace known troublemakers first, "
                "then collapse every run of whitespace to a single space, then strip the ends. Do it once, at "
                "the boundary where text enters the pipeline, rather than repeatedly in every consumer. Keep "
                "the transformation honest: do not lowercase a title unless case is genuinely meaningless, and "
                "do not strip punctuation that carries meaning in a product name or a model number. Record "
                "what you changed when the change is consequential. For today's exercise, clean a handful of "
                "malformed titles and confirm that cleaning is idempotent, meaning a second pass changes "
                "nothing. Idempotence is the property that makes a normaliser safe to rerun on already stored "
                "rows, and it is the quiet reason a repair script can be applied twice without producing a "
                "third kind of mess."
            ),
            code=(
                'import re\n'
                '\n'
                'raw_titles = [\n'
                '    "  Dune   (Deluxe) ",\n'
                '    "Found\\u00a0ation\\n",\n'
                '    "The\\u200bLeft   Hand",\n'
                '    "   ",\n'
                ']\n'
                '\n'
                'def clean_text(value):\n'
                '    value = value.replace("\\u200b", " ").replace("\\u00a0", " ")\n'
                '    value = re.sub(r"\\s+", " ", value)\n'
                '    return value.strip()\n'
                '\n'
                'cleaned = [clean_text(title) for title in raw_titles]\n'
                'print("cleaned:", cleaned)\n'
                'print("empty after cleaning:", sum(1 for value in cleaned if not value))\n'
                'assert clean_text("  A\\t B\\n") == "A B"\n'
                'assert all(clean_text(clean_text(value)) == clean_text(value) for value in raw_titles)\n'
                'print("normalisation is idempotent")'
            ),
            variant_b='raw_titles contains "  Café  Society " and "Cafe\\u0301 Society"; compare the two results',
            variant_c='make clean_text collapse hyphens surrounded by spaces and check which title changes meaning',
            mistakes=[
                "Calling .strip() only, which removes the ends but leaves doubled inner spaces.",
                "Lowercasing every string, which destroys meaningful case in titles and codes.",
                "Normalising in three different consumers, so each one produces a slightly different canonical form.",
            ],
            q1=(
                "Why does clean_text run the whitespace substitution before strip?",
                "Collapsing first turns leading, trailing and internal runs into single spaces, so the final strip removes exactly the boundary spaces and nothing is left doubled.",
            ),
            homework=(
                "Write `clean_text(value)` that replaces non-breaking and zero-width spaces, collapses whitespace "
                "runs, and strips the ends. Run it on two lists of messy titles, print the before and after "
                "values, and comment which line makes the function safe to apply twice."
            ),
            patterns=["def ", "re.sub", "strip("],
            mapping=(
                "Warehouse loaders normalise text before joining keys, and pandas users routinely chain "
                ".str.replace and .str.strip for this reason. Cleaning at ingestion keeps every downstream join "
                "from needing its own private rules."
            ),
        ),
        107: dict(
            topic="Missing fields and optional values",
            idea=(
                "Missing data is normal in scraping, but it must have one meaning. If an absent ISBN sometimes "
                "arrives as an empty string, sometimes as 'N/A', sometimes as the literal word 'None' and "
                "sometimes as a missing key, every consumer has to guess. The fix is to choose a single "
                "in-memory representation for absence, usually None, and convert every known spelling to that "
                "value at the boundary. Then distinguish required fields from optional ones. A record without "
                "a title is not a record; a record without an ISBN may still be useful. That distinction "
                "belongs in code, not in a comment, because it drives whether the row is rejected, stored with "
                "a null, or sent to a repair queue. A second trap is conflating missing with false or zero. An "
                "empty price is not 0.0, and an unknown stock flag is not False; storing those substitutes "
                "creates data that looks complete and is wrong. When a field is optional, keep the key present "
                "with None so the schema stays stable, and count how many nulls each field carries. That count "
                "is a quality signal: a column that is null in most rows may not be worth storing, while a "
                "sudden jump in nulls usually means the page changed. Today you build a tiny converter that "
                "maps blanks and placeholder strings to None, preserves genuine zeroes, and reports which "
                "fields are missing."
            ),
            code=(
                'rows = [\n'
                '    {"title": "Dune", "price": "9.99", "isbn": "9780441013593"},\n'
                '    {"title": "Foundation", "price": "", "isbn": "N/A"},\n'
                '    {"title": "Neuromancer", "price": "0", "isbn": None},\n'
                ']\n'
                '\n'
                'PLACEHOLDERS = {"", "n/a", "none", "null", "-"}\n'
                '\n'
                'def optional(value):\n'
                '    if value is None:\n'
                '        return None\n'
                '    text = str(value).strip()\n'
                '    return None if text.casefold() in PLACEHOLDERS else text\n'
                '\n'
                'def to_price(value):\n'
                '    text = optional(value)\n'
                '    return None if text is None else float(text)\n'
                '\n'
                'records = [\n'
                '    {"title": row["title"], "price": to_price(row["price"]), "isbn": optional(row["isbn"])}\n'
                '    for row in rows\n'
                ']\n'
                'for record in records:\n'
                '    print(record)\n'
                'print("null prices:", sum(1 for record in records if record["price"] is None))\n'
                'assert records[1]["price"] is None and records[1]["isbn"] is None\n'
                'assert records[2]["price"] == 0.0\n'
                'print("absence is explicit and zero survives")'
            ),
            variant_b='add a row with isbn "unknown" and decide whether that spelling joins PLACEHOLDERS',
            variant_c='treat an absent isbn key with row.get("isbn") instead of row["isbn"] and compare behaviour',
            mistakes=[
                "Storing 0.0 or False for unknown values, which turns absence into a false fact.",
                "Using an empty string in one place and None in another, so consumers need two checks.",
                "Dropping the whole row because an optional field is absent, discarding usable data.",
            ],
            q1=(
                "Why keep an optional key with None instead of removing it from the record?",
                "A stable key set lets every consumer read the same fields and distinguishes an unknown value from a field the schema never contained.",
            ),
            homework=(
                "Write `optional(value)` that maps blanks and placeholder strings to None while preserving real "
                "zero values, then apply it to price and isbn in two row sets. Print every resulting record and "
                "comment which line distinguishes a missing value from a legitimate zero."
            ),
            patterns=["def ", "None", "print("],
            mapping=(
                "SQL has NULL for exactly this purpose, and pandas represents absent values as NaN or None. "
                "Deciding the sentinel once at load time prevents the classic warehouse bug where 'N/A' becomes "
                "a category in a report."
            ),
        ),
        108: dict(
            topic="Stable IDs and deduplication",
            idea=(
                "The same item will be scraped more than once: a crawl revisits a page, a category lists a "
                "product twice, a retry produces a second copy. Removing duplicates requires deciding what "
                "makes two rows the same, and that decision has to survive whitespace changes and reruns. A "
                "database auto-increment key does not help here, because it identifies the insertion event, "
                "not the item. What you need is a stable identity derived from the values that define the "
                "entity, such as a normalised title plus a normalised price or an ISBN when one exists. Hash "
                "that canonical string to keep the key short and fixed-width. The hash must be computed from "
                "normalised fields in a fixed order, otherwise the same item produces a different identifier "
                "on the next run. Choose the key fields deliberately: including a field that changes often, "
                "such as stock status or a view count, makes the identity unstable; excluding a field that "
                "distinguishes two genuinely different items causes false merges. Once the identifier exists, "
                "deduplication is simple: keep the first or the most recent row per identifier, and count what "
                "was dropped. Report that count, because a sudden increase in duplicates often signals a "
                "selector matching the same element twice or a pagination loop revisiting a page. Today you "
                "normalise title and price, derive a short SHA-1 key, and collapse duplicate records while "
                "keeping the first occurrence."
            ),
            code=(
                'import hashlib\n'
                '\n'
                'rows = [\n'
                '    {"title": "Dune", "price": 9.99},\n'
                '    {"title": "  Dune ", "price": 9.99},\n'
                '    {"title": "Foundation", "price": 12.5},\n'
                '    {"title": "Dune", "price": 10.5},\n'
                ']\n'
                '\n'
                'def canonical(row):\n'
                '    title = " ".join(row["title"].split()).casefold()\n'
                '    return "{}|{:.2f}".format(title, row["price"])\n'
                '\n'
                'def record_id(row):\n'
                '    return hashlib.sha1(canonical(row).encode("utf-8")).hexdigest()[:12]\n'
                '\n'
                'unique = {}\n'
                'for row in rows:\n'
                '    unique.setdefault(record_id(row), row)\n'
                '\n'
                'print("input rows:", len(rows), "| unique:", len(unique))\n'
                'for key, row in unique.items():\n'
                '    print(key, row["title"], row["price"])\n'
                'assert len(unique) == 3\n'
                'assert record_id(rows[0]) == record_id(rows[1])\n'
                'print("same item, same id")'
            ),
            variant_b='add a second Foundation row with price 12.50 and confirm it collapses to the same id',
            variant_c='include stock status in the canonical string and explain why a restock creates a new id',
            mistakes=[
                "Hashing the raw strings, so a stray space or different case creates a new identity.",
                "Using a database auto-increment id as the item identity, which changes on every rerun.",
                "Silently dropping duplicates without counting them, hiding a broken selector.",
            ],
            q1=(
                "Why must the canonical string be built from normalised fields in a fixed order?",
                "Any variation in spacing, case or field order changes the hash, so the same item would receive different identifiers and escape deduplication.",
            ),
            homework=(
                "Write `record_id(row)` that normalises title and price, joins them in a fixed order, and "
                "returns a short hash. Run it on two lists containing near-duplicates, print each id and the "
                "deduplicated count, and comment which line makes whitespace differences irrelevant."
            ),
            patterns=["hashlib", "def ", "setdefault("],
            mapping=(
                "Warehouse tables use natural or surrogate keys for the same reason, and dbt tests often assert "
                "uniqueness on a hashed key. Content addressing in object storage is the same idea: the key is "
                "derived from content, not from arrival order."
            ),
        ),
        109: dict(
            topic="Writing CSV safely",
            idea=(
                "CSV looks trivial until a title contains a comma, a description contains a newline, or a "
                "field starts with a character a spreadsheet treats as a formula. Hand-built output like "
                "','.join(values) works on the happy path and corrupts rows on the first awkward value. The "
                "standard library's csv module exists to handle quoting, escaping and embedded line breaks "
                "correctly, and using it costs almost nothing. Write through a DictWriter with an explicit "
                "field order so the header cannot drift when a key is added, and pass a consistent line "
                "terminator rather than relying on the platform default. Use UTF-8 and decide up front whether "
                "you want a byte-order mark for spreadsheet compatibility; that is a delivery decision, not an "
                "accident. The second half of safe writing is verification: after producing the text, read it "
                "back with DictReader and compare a field containing a comma or newline to the value you "
                "started with. A round trip is the cheapest proof that quoting worked. Also think about nulls: "
                "the csv module writes None as an empty field, which is indistinguishable from an empty string, "
                "so decide whether that is acceptable or whether you need a separate encoding. Today you write "
                "two hostile rows to an in-memory buffer, print the escaped result, and parse it back to prove "
                "the data survived."
            ),
            code=(
                'import csv\n'
                'import io\n'
                '\n'
                'rows = [\n'
                '    {"title": "Dune, Book One", "notes": "line one\\nline two", "price": 9.99},\n'
                '    {"title": \'The "Left" Hand\', "notes": "", "price": 12.5},\n'
                ']\n'
                'fields = ["title", "notes", "price"]\n'
                '\n'
                'buffer = io.StringIO()\n'
                'writer = csv.DictWriter(buffer, fieldnames=fields, lineterminator="\\n")\n'
                'writer.writeheader()\n'
                'writer.writerows(rows)\n'
                'text = buffer.getvalue()\n'
                '\n'
                'print(text)\n'
                'restored = list(csv.DictReader(io.StringIO(text)))\n'
                'print("round-trip rows:", len(restored))\n'
                'assert restored[0]["title"] == "Dune, Book One"\n'
                'assert restored[0]["notes"] == "line one\\nline two"\n'
                'print("commas and newlines survived quoting")'
            ),
            variant_b='add a field containing the literal text "=SUM(1,2)" and inspect how it is written',
            variant_c='write with delimiter=";" and read back with the same delimiter; say what breaks if only one side changes',
            mistakes=[
                "Building CSV with join and commas, which corrupts any field containing a comma or newline.",
                "Letting each writer choose its own column order, so the header no longer matches production.",
                "Skipping the read-back check, so quoting bugs are discovered by the analyst instead of the pipeline.",
            ],
            q1=(
                "Why write CSV through the csv module instead of joining fields with commas?",
                "The module escapes embedded commas, quotes and newlines and re-reads them correctly; manual joins produce rows that parse into the wrong columns.",
            ),
            homework=(
                "Write `to_csv(rows, fields)` that writes dictionaries through DictWriter and returns the text, "
                "then reads it back with DictReader. Run it on two row sets including a comma and a newline, "
                "print both outputs, and comment which line preserves the embedded newline."
            ),
            patterns=["import csv", "DictWriter", "DictReader"],
            mapping=(
                "Every analyst-facing export is a CSV contract, and broken quoting is one of the most common "
                "ingestion failures in data teams. The same round-trip test belongs in a warehouse load check "
                "before a file is promoted to a shared bucket."
            ),
        ),
        110: dict(
            topic="JSON and JSON Lines",
            idea=(
                "CSV is flat by construction, so nested scraped data such as a price with a currency, a list of "
                "tags or a seller object has to be flattened or dropped. JSON keeps that structure, and JSON "
                "Lines keeps it while remaining streamable: one complete JSON value per line, so a reader can "
                "process a million rows without loading the whole file. The discipline is to serialise each "
                "record on its own with a stable key order, write exactly one newline after it, and parse lines "
                "individually rather than splitting the entire document. Use ensure_ascii=False so accented "
                "characters stay readable, and choose compact separators when file size matters. Two decisions "
                "need care. First, JSON has no tuple and no set, so convert those before dumping or the output "
                "will not round-trip to the same Python object. Second, NaN and Infinity are not valid JSON, and "
                "Python will happily emit them unless you pass allow_nan=False or clean the values first. A "
                "JSON Lines file with one malformed line should be diagnosed by line number, not treated as a "
                "single broken document. Today you turn two nested records into lines, print them, parse them "
                "back and verify the nested values are intact. The point is not the dumps call; it is that the "
                "storage format preserves the shape the scraper actually collected."
            ),
            code=(
                'import json\n'
                '\n'
                'rows = [\n'
                '    {"title": "Dune", "price": {"amount": 9.99, "currency": "EUR"}, "tags": ["sf", "classic"]},\n'
                '    {"title": "Foundation", "price": {"amount": 12.5, "currency": "EUR"}, "tags": []},\n'
                ']\n'
                '\n'
                'def to_line(row):\n'
                '    return json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":"))\n'
                '\n'
                'lines = [to_line(row) for row in rows]\n'
                'print("jsonl:")\n'
                'print("\\n".join(lines))\n'
                '\n'
                'restored = [json.loads(line) for line in "\\n".join(lines).splitlines()]\n'
                'print("restored:", len(restored), "records")\n'
                'assert restored == rows\n'
                'assert restored[0]["price"]["currency"] == "EUR"\n'
                'print("nested structure survived the round trip")'
            ),
            variant_b='serialise a record containing a tuple of tags and show what JSON turns it into',
            variant_c='set allow_nan=False and try a record whose price is float("nan"); explain the error',
            mistakes=[
                "Dumping a whole list as one JSON array when the consumer expects one record per line.",
                "Using ensure_ascii default settings and then wondering why names look like escape codes.",
                "Assuming NaN is valid JSON, so a downstream parser rejects the entire file.",
            ],
            q1=(
                "What makes JSON Lines easier to stream than one large JSON array?",
                "Each line is a complete record, so a reader can parse and process it immediately without loading or balancing the whole document.",
            ),
            homework=(
                "Write `to_jsonl(rows)` that serialises each dictionary on its own line with stable key order, "
                "then `read_jsonl(text)` that parses it back. Run both on two nested record sets, print the "
                "lines and restored values, and comment which line guarantees one record per line."
            ),
            patterns=["json.dumps", "json.loads", "join("],
            mapping=(
                "Object storage commonly holds JSON Lines because files can be split and processed in parallel, "
                "and tools such as Spark and BigQuery ingest newline-delimited JSON directly. Nested records "
                "also map naturally to document stores."
            ),
        ),
        111: dict(
            topic="SQLite for scraped rows",
            idea=(
                "A growing scrape quickly outgrows a list in memory. SQLite is the smallest sensible step up: a "
                "real relational database in a single file, available in the standard library, with "
                "transactions and indexes. The table is the schema made concrete, so create it explicitly "
                "instead of letting a loader infer types from whatever happened to arrive. Declare primary "
                "keys, NOT NULL constraints and the column types you actually need; those constraints catch "
                "malformed rows at insert time, which is much earlier than an analyst noticing a broken chart. "
                "Insert in a batch with executemany inside one transaction rather than committing after every "
                "row, because per-row commits are dramatically slower and leave a half-written table if the "
                "process dies. Query through parameters, never string formatting, so a title containing a "
                "quote cannot break the statement or inject SQL. A first load should end with a count and a "
                "small sample query, and that count should be compared with the number of parsed rows. If they "
                "differ, the database or the insert logic is lying to you. Today you create an in-memory "
                "database, insert a few books in one transaction, query them back with a parameter, and prove "
                "the stored count matches the input. The connection is temporary, but every habit transfers to "
                "the file-backed database used later."
            ),
            code=(
                'import sqlite3\n'
                '\n'
                'rows = [\n'
                '    ("9780441013593", "Dune", 9.99),\n'
                '    ("9780553293357", "Foundation", 12.50),\n'
                '    ("9780441569595", "Neuromancer", 8.75),\n'
                ']\n'
                '\n'
                'conn = sqlite3.connect(":memory:")\n'
                'conn.execute(\n'
                '    "CREATE TABLE books (isbn TEXT PRIMARY KEY, title TEXT NOT NULL, price REAL NOT NULL)"\n'
                ')\n'
                'conn.executemany("INSERT INTO books VALUES (?, ?, ?)", rows)\n'
                'conn.commit()\n'
                '\n'
                'for title, price in conn.execute(\n'
                '    "SELECT title, price FROM books WHERE price < ? ORDER BY price", (10.0,)\n'
                '):\n'
                '    print(title, price)\n'
                '\n'
                'stored = conn.execute("SELECT COUNT(*) FROM books").fetchone()[0]\n'
                'print("stored rows:", stored)\n'
                'assert stored == len(rows)\n'
                'conn.close()\n'
                'print("table accepted every row")'
            ),
            variant_b='insert a duplicate ISBN and explain which constraint rejects it',
            variant_c='drop NOT NULL from price, insert a row with None, and query for null prices',
            mistakes=[
                "Committing after every insert, which is slow and can leave partial loads after a crash.",
                "Building SQL with f-strings, so a quote in a title breaks the statement or injects code.",
                "Letting column types be inferred from a sample instead of declaring them in the schema.",
            ],
            q1=(
                "Why insert the batch inside one transaction instead of committing each row?",
                "One transaction is far faster, and it makes the load atomic: either every row is stored or none is, so a crash cannot leave a half-written table.",
            ),
            homework=(
                "Write `load_books(rows)` that creates an in-memory SQLite table with a primary key, inserts the "
                "batch with executemany, and returns the stored count. Run it on two row sets, print the count "
                "and one parameterised query, and comment which line makes the whole load atomic."
            ),
            patterns=["import sqlite3", "executemany", "commit("],
            mapping=(
                "SQLite is the same SQL dialect used by many production warehouses at small scale, and the "
                "transaction habit matters more as loads grow. A file-backed database is the natural next step "
                "when a scrape must persist between runs."
            ),
        ),
        112: dict(
            topic="Schemas and validation",
            idea=(
                "A schema is a promise about the shape of every row, written down where code can enforce it. "
                "Without one, a scraper quietly produces records with a missing title, a price as a string, or "
                "a stock flag that is neither True nor False, and each consumer has to defend itself. A small "
                "declarative schema is enough: field name, expected type, whether it is required, and any "
                "domain rule such as a positive price. Validation then returns a list of problems instead of "
                "raising on the first one, because a batch with twenty bad rows should be diagnosed as a batch "
                "rather than fixed one crash at a time. Keep the validator pure and independent of the parser, "
                "so the same function can check rows from a saved fixture and rows from a live run. Distinguish "
                "three outcomes: valid, repairable and rejected. A price stored as '9.99' can often be "
                "converted, while a negative price or a missing title should not be guessed at. The most "
                "important design choice is where validation runs. Put it at the boundary between parsing and "
                "storage, before any deduplication or writing, so no invalid row can acquire an identifier or "
                "occupy a database key. Report the validation summary with the run, including counts per "
                "problem type. That summary is how a schema change on the source site becomes visible as a "
                "trend instead of a mystery months later."
            ),
            code=(
                'SCHEMA = {"title": str, "price": float, "in_stock": bool}\n'
                '\n'
                'rows = [\n'
                '    {"title": "Dune", "price": 9.99, "in_stock": True},\n'
                '    {"title": "", "price": -1.0, "in_stock": True},\n'
                '    {"title": "Foundation", "price": "12.50"},\n'
                ']\n'
                '\n'
                'def validate(row):\n'
                '    errors = []\n'
                '    for field, expected in SCHEMA.items():\n'
                '        if field not in row:\n'
                '            errors.append(f"missing {field}")\n'
                '        elif not isinstance(row[field], expected):\n'
                '            errors.append(f"{field} is {type(row[field]).__name__}")\n'
                '    if not row.get("title", "").strip():\n'
                '        errors.append("title is blank")\n'
                '    if isinstance(row.get("price"), float) and row["price"] <= 0:\n'
                '        errors.append("price must be positive")\n'
                '    return errors\n'
                '\n'
                'for row in rows:\n'
                '    print(row.get("title") or "<blank>", "->", validate(row) or "valid")\n'
                'assert validate(rows[0]) == []\n'
                'assert len(validate(rows[1])) == 2\n'
                'print("validation reports all problems at once")'
            ),
            variant_b='add an "isbn" field that is optional but must be a string when present',
            variant_c='require price to be at most 1000 and show which row now fails for a second reason',
            mistakes=[
                "Raising on the first error, so a batch is repaired one crash at a time.",
                "Checking types in the parser as well as the validator, leaving two drifting definitions of valid.",
                "Validating after insertion, when the invalid row already occupies a primary key.",
            ],
            q1=(
                "Why should the validator collect all errors instead of raising on the first?",
                "A batch report shows every malformed row and problem type in one pass, so the source change can be diagnosed and fixed as a whole.",
            ),
            homework=(
                "Write `validate(row)` driven by a schema dictionary that checks presence, type, blank text and a "
                "positive price, returning a list of messages. Run it on two batches with different defects, "
                "print every report, and comment which line keeps one bad field from hiding the others."
            ),
            patterns=["SCHEMA", "def validate", "errors"],
            mapping=(
                "Warehouse tools express this as column contracts and dbt tests, while pandas has dtype checks "
                "and Pydantic-style validators in application code. The principle is identical: reject bad "
                "shapes before they become stored facts."
            ),
        ),
        113: dict(
            topic="Incremental scraping",
            idea=(
                "Scraping everything again on every run is wasteful, slow and rude to the source. Incremental "
                "scraping stores a watermark and processes only what is newer than it. The watermark can be a "
                "timestamp from the last successful run, a page cursor, or a set of item identifiers already "
                "seen; each has different failure modes. A timestamp is simple but can miss rows that were "
                "updated without changing their published date. An identifier set is exact for new items but "
                "grows without bound and cannot detect edits. Whichever you choose, advance the watermark only "
                "after the rows are safely stored, never before the fetch. If you advance first and the write "
                "fails, the missed window is gone. A rerun should therefore be safe and produce zero new rows, "
                "which is the observable proof that the watermark works. Compare timestamps as real datetimes "
                "in a single timezone rather than as strings, because text comparison breaks when formats "
                "differ or offsets change. Keep the previous watermark alongside the new one in the run report, "
                "so a suspicious zero-row run can be explained. Today you process a small batch of timestamped "
                "pages, select the rows newer than the stored watermark, then rerun against the advanced "
                "watermark and confirm nothing is added twice."
            ),
            code=(
                'from datetime import datetime\n'
                '\n'
                'pages = [\n'
                '    {"url": "/dune", "fetched_at": "2026-10-01T08:00:00+00:00", "title": "Dune"},\n'
                '    {"url": "/foundation", "fetched_at": "2026-10-02T09:30:00+00:00", "title": "Foundation"},\n'
                '    {"url": "/neuromancer", "fetched_at": "2026-10-03T11:15:00+00:00", "title": "Neuromancer"},\n'
                ']\n'
                'state = {"watermark": "2026-10-01T12:00:00+00:00"}\n'
                '\n'
                'def newer_than(page, watermark):\n'
                '    moment = datetime.fromisoformat(page["fetched_at"])\n'
                '    return moment > datetime.fromisoformat(watermark)\n'
                '\n'
                'fresh = [page for page in pages if newer_than(page, state["watermark"])]\n'
                'print("fresh:", [page["title"] for page in fresh])\n'
                '\n'
                'if fresh:\n'
                '    state["watermark"] = max(page["fetched_at"] for page in fresh)\n'
                'print("new watermark:", state["watermark"])\n'
                '\n'
                'rerun = [page for page in pages if newer_than(page, state["watermark"])]\n'
                'print("second run rows:", len(rerun))\n'
                'assert len(fresh) == 2 and rerun == []\n'
                'print("watermark advanced after processing")'
            ),
            variant_b='start the watermark at 2026-10-02T00:00:00+00:00 and predict which two rows survive',
            variant_c='mix a +02:00 offset into fetched_at; explain why fromisoformat still compares correctly',
            mistakes=[
                "Advancing the watermark before the rows are written, so a failed write loses the window.",
                "Comparing ISO timestamp strings lexically across different formats or offsets.",
                "Using an item-id set but never pruning it, so the state grows without limit.",
            ],
            q1=(
                "Why must the watermark advance only after the new rows are stored?",
                "If the write fails after the watermark moves, those rows fall behind the new boundary and will never be selected again.",
            ),
            homework=(
                "Write `select_new(pages, watermark)` that parses timestamps, returns rows strictly newer than the "
                "watermark, and returns the advanced watermark. Run it on two batches with different timestamps, "
                "print the fresh rows and the second-run count, and comment which line proves the rerun is safe."
            ),
            patterns=["datetime", "def ", "watermark"],
            mapping=(
                "Airflow and dbt incremental models use a high-water mark in exactly this way, storing it in a "
                "metadata table. Real pipelines also persist the watermark transactionally with the output rows "
                "so the two cannot disagree."
            ),
        ),
        114: dict(
            topic="Provenance and timestamps",
            idea=(
                "A row without provenance is an assertion with no witness. When a stored value looks wrong, the "
                "first questions are where it came from, when it was captured, which parser produced it and "
                "which run inserted it. Answering those from memory is impossible after a week. Provenance "
                "fields are cheap to add and expensive to reconstruct, so attach them while the row is created: "
                "the source URL, the selector or parser version, the run identifier and a timestamp in UTC. Use "
                "timezone-aware datetimes, because a naive timestamp is ambiguous across machines and daylight "
                "saving changes, and store them in one canonical format such as ISO 8601 with an explicit "
                "offset. The timestamp should mean the moment of capture, not the moment of export; those are "
                "different facts and only one of them is evidence about the page. Keep the fields separate "
                "rather than packing them into a free-text note, so they can be filtered and joined. Also "
                "consider row-level lineage: the URL usually identifies the page, while the parser version "
                "identifies the code that interpreted it. If either changes, old and new rows are not directly "
                "comparable until you account for the difference. Today you stamp a few records with a fixed "
                "run id and capture time, then verify that the timestamp carries an offset and that provenance "
                "survives a round trip through JSON."
            ),
            code=(
                'import json\n'
                'from datetime import datetime, timezone\n'
                '\n'
                'def stamp(row, run_id, source_url, parser, captured_at=None):\n'
                '    moment = captured_at or datetime.now(timezone.utc)\n'
                '    record = dict(row)\n'
                '    record.update({\n'
                '        "run_id": run_id,\n'
                '        "source_url": source_url,\n'
                '        "parser": parser,\n'
                '        "captured_at": moment.replace(microsecond=0).isoformat(),\n'
                '    })\n'
                '    return record\n'
                '\n'
                'rows = [\n'
                '    stamp({"title": "Dune", "price": 9.99}, "run-42", "https://shop.example/dune", "v3",\n'
                '          datetime(2026, 10, 19, 10, 25, tzinfo=timezone.utc)),\n'
                '    stamp({"title": "Foundation", "price": 12.5}, "run-42",\n'
                '          "https://shop.example/foundation", "v3",\n'
                '          datetime(2026, 10, 19, 10, 30, tzinfo=timezone.utc)),\n'
                ']\n'
                'for row in rows:\n'
                '    print(json.dumps(row, ensure_ascii=False, sort_keys=True))\n'
                'assert rows[1]["captured_at"] == "2026-10-19T10:30:00+00:00"\n'
                'assert all(row["source_url"].startswith("https://") for row in rows)\n'
                'print("provenance attached and timestamp is timezone-aware")'
            ),
            variant_b='use a parser label "v4-2026-10" and explain why the version belongs in the row',
            variant_c='stamp one row with datetime.now() without a timezone and inspect the missing offset',
            mistakes=[
                "Storing naive local timestamps, which become ambiguous and inconsistent across machines.",
                "Recording the export time instead of the capture time, losing the evidence about the page.",
                "Packing run id, URL and parser into one opaque note that cannot be filtered or joined.",
            ],
            q1=(
                "Why should captured_at be timezone-aware UTC rather than a naive local timestamp?",
                "An explicit offset makes the moment unambiguous across machines, time zones and daylight-saving changes, so rows from different runs can be ordered and compared.",
            ),
            homework=(
                "Write `stamp(row, run_id, source_url, parser, captured_at=None)` that returns a copy with "
                "provenance fields and an ISO timestamp. Run it on two rows with different source URLs, print "
                "them as JSON, and comment which line guarantees the timestamp has an offset."
            ),
            patterns=["timezone.utc", "isoformat()", "source_url"],
            mapping=(
                "Data catalogs and lakehouse tables track source, load time and job id for exactly this reason, "
                "and audit requirements often make row-level lineage mandatory. Object storage metadata can "
                "hold the same facts beside the object."
            ),
        ),
        115: dict(
            topic="Data-quality checks",
            idea=(
                "Validation asks whether one row is well formed; data-quality checks ask whether the dataset as "
                "a whole is believable. Both are needed. A batch can pass every per-row schema check and still "
                "be useless because every price is the same value, twenty identifiers repeat, or a currency "
                "column contains four spellings of the same currency. Quality checks are small aggregate "
                "assertions with names, expected ranges and clear failure messages. Good checks are cheap to "
                "run, specific about what broke, and stable enough that they do not cry wolf on normal "
                "variation. Typical families include completeness, uniqueness, range, allowed-set membership "
                "and consistency between fields. Report counts rather than only pass or fail, because a "
                "duplicate rate moving from zero to two percent is a signal even before it breaches a "
                "threshold. Decide which failures block the load and which merely warn. A blank optional field "
                "may be a warning; a duplicated primary key or a negative price should stop the write. Keep the "
                "report machine-readable so it can be stored with the run and compared over time. Today you "
                "compute a compact report over a small batch: row count, blank titles, non-positive prices, "
                "duplicate identifiers and unexpected currencies. Then you decide, in code, which of those "
                "conditions makes the dataset unfit to store. The checks are deliberately simple; the habit of "
                "naming and counting failures is what matters."
            ),
            code=(
                'rows = [\n'
                '    {"id": "a1", "title": "Dune", "price": 9.99, "currency": "EUR"},\n'
                '    {"id": "a2", "title": "  ", "price": 12.5, "currency": "EUR"},\n'
                '    {"id": "a2", "title": "Foundation", "price": 0.0, "currency": "eur"},\n'
                '    {"id": "a3", "title": "Neuromancer", "price": -3.0, "currency": "USD"},\n'
                ']\n'
                '\n'
                'def quality_report(rows):\n'
                '    ids = [row["id"] for row in rows]\n'
                '    return {\n'
                '        "rows": len(rows),\n'
                '        "blank_titles": sum(1 for row in rows if not row["title"].strip()),\n'
                '        "nonpositive_prices": sum(1 for row in rows if row["price"] <= 0),\n'
                '        "duplicate_ids": len(ids) - len(set(ids)),\n'
                '        "unexpected_currency": sum(1 for row in rows if row["currency"] != "EUR"),\n'
                '    }\n'
                '\n'
                'report = quality_report(rows)\n'
                'for name, value in report.items():\n'
                '    print(f"{name}: {value}")\n'
                '\n'
                'blocking = report["duplicate_ids"] or report["nonpositive_prices"]\n'
                'print("load allowed:", not blocking)\n'
                'assert report["duplicate_ids"] == 1 and report["blank_titles"] == 1\n'
                'assert blocking\n'
                'print("quality report names what must block the load")'
            ),
            variant_b='allow both "EUR" and "eur" as valid currencies and see which count changes',
            variant_c='add a check for titles longer than 80 characters and decide whether it warns or blocks',
            mistakes=[
                "Reporting only pass or fail, so a rising duplicate rate is invisible until it breaches a threshold.",
                "Treating every warning as blocking, which makes the pipeline brittle to harmless variation.",
                "Checking quality after the write, when bad rows are already visible to downstream users.",
            ],
            q1=(
                "Why report counts for each quality check instead of a single boolean?",
                "Counts show the size and direction of a problem, so a small regression is visible before it becomes a failure and can be compared across runs.",
            ),
            homework=(
                "Write `quality_report(rows)` that returns counts for blank titles, non-positive prices, duplicate "
                "ids and unexpected currencies, plus a blocking decision. Run it on two batches with different "
                "defects, print every report, and comment which check you chose to block the load."
            ),
            patterns=["def quality_report", "sum(", "print("],
            mapping=(
                "Great Expectations and dbt tests formalise exactly these aggregate assertions, and warehouse "
                "teams store quality metrics per run. The report is also the evidence used when deciding "
                "whether a dataset is fit to publish."
            ),
        ),
        116: dict(
            topic="Sorting and grouping results",
            idea=(
                "Sorting and grouping turn a pile of rows into answers. Sorting is not cosmetic: a deterministic "
                "order makes diffs meaningful, exports reproducible and pagination stable. Grouping then lets "
                "you compute counts, sums and averages per category, which is usually the first thing anyone "
                "asks of scraped data. Python's sort is stable, so a secondary key survives when the primary "
                "key ties, and a tuple key expresses the priority directly. Put the most significant field "
                "first and negate numeric fields when you want descending order, or sort ascending and reverse "
                "the whole list if every field should reverse. Grouping is easiest after sorting, because "
                "itertools.groupby only groups adjacent items; forgetting the sort produces scattered groups "
                "that look plausible and are simply wrong. Always convert each group iterator to a list before "
                "using it twice, since groupby yields a fresh iterator per group and the previous one is "
                "exhausted. Decide how to handle missing values in sort keys: None cannot be compared with a "
                "string, so either filter it, map it to a sentinel or supply a default. Also decide whether "
                "group totals should count rows or sum a meaningful numeric column; both are useful but they "
                "answer different questions. Today you sort by category, descending price and title, then "
                "group and print counts and totals per category."
            ),
            code=(
                'from itertools import groupby\n'
                '\n'
                'rows = [\n'
                '    {"title": "Dune", "category": "fiction", "price": 9.99},\n'
                '    {"title": "Foundation", "category": "fiction", "price": 12.5},\n'
                '    {"title": "Clean Code", "category": "technical", "price": 32.0},\n'
                '    {"title": "Neuromancer", "category": "fiction", "price": 8.75},\n'
                ']\n'
                '\n'
                'ordered = sorted(rows, key=lambda row: (row["category"], -row["price"], row["title"]))\n'
                'print("order:", [(row["category"], row["title"]) for row in ordered])\n'
                '\n'
                'for category, items in groupby(ordered, key=lambda row: row["category"]):\n'
                '    group = list(items)\n'
                '    total = sum(row["price"] for row in group)\n'
                '    print(category, "count:", len(group), "total:", round(total, 2))\n'
                '\n'
                'assert ordered[0]["title"] == "Foundation"\n'
                'assert ordered[-1]["title"] == "Clean Code"\n'
                'print("groups are adjacent and totals match the sorted rows")'
            ),
            variant_b='sort by category ascending and price ascending, then change the group aggregate to average',
            variant_c='add a row with category None and explain what the sort key does before you fix it',
            mistakes=[
                "Calling groupby without sorting by the same key, which yields repeated non-adjacent groups.",
                "Reusing a group iterator after converting it once, so the second loop sees an empty group.",
                "Comparing None with strings in the sort key, which raises a TypeError mid-sort.",
            ],
            q1=(
                "Why must the rows be sorted by the same key used in groupby?",
                "groupby only combines adjacent equal keys; without the sort, equal categories are scattered and produce several partial groups.",
            ),
            homework=(
                "Write `group_totals(rows)` that sorts by category and descending price, then returns a dictionary "
                "of category to count and total. Run it on two row sets including a repeated category, print the "
                "groups, and comment which line makes equal categories adjacent."
            ),
            patterns=["sorted(", "groupby", "sum("],
            mapping=(
                "SQL's GROUP BY and ORDER BY express the same two operations, and pandas users chain sort_values "
                "with groupby. In both systems, grouping without a defined order is a common source of "
                "nondeterministic reports."
            ),
        ),
        117: dict(
            topic="Exporting for analysis",
            idea=(
                "The storage format is for the pipeline; the export is for a human or a notebook. Those are "
                "different contracts. An analysis export should have a stable column order, readable names, "
                "one row per observation, and the computed fields the analyst would otherwise rebuild by hand. "
                "Decide the grain before writing: is a row a product, a product snapshot, or a product per "
                "day? Mixing grains in one file is a classic way to double-count totals. Flatten nested "
                "structures deliberately, for example turning a price object into amount and currency columns, "
                "rather than dumping a dictionary repr into a cell. Keep identifiers as text even when they "
                "look numeric, because spreadsheet programs love to reinterpret leading zeroes and long "
                "integers. Format money with a fixed number of decimals, but do not add currency symbols to the "
                "numeric column if the analyst needs to sum it. Include the capture date as a real column so "
                "trend analysis is possible, and write the file through csv.DictWriter with an explicit header. "
                "Finally, document the grain and units somewhere the consumer will see: a header comment, a "
                "sidecar file or a data dictionary. An export that requires a conversation to interpret is not "
                "finished. Today you take stored records and produce a flat analysis table with a price band, "
                "a numeric price, an ISO date and a fixed column order, then print it and verify the header."
            ),
            code=(
                'import csv\n'
                'import io\n'
                '\n'
                'rows = [\n'
                '    {"title": "Dune", "price": 9.99, "currency": "EUR", "captured_at": "2026-10-19"},\n'
                '    {"title": "Foundation", "price": 12.5, "currency": "EUR", "captured_at": "2026-10-19"},\n'
                '    {"title": "Clean Code", "price": 32.0, "currency": "EUR", "captured_at": "2026-10-20"},\n'
                ']\n'
                '\n'
                'FIELDS = ["captured_at", "title", "price", "price_band"]\n'
                '\n'
                'def price_band(price):\n'
                '    if price < 10:\n'
                '        return "low"\n'
                '    return "mid" if price < 25 else "high"\n'
                '\n'
                'def analysis_row(row):\n'
                '    return {\n'
                '        "captured_at": row["captured_at"],\n'
                '        "title": row["title"],\n'
                '        "price": "{:.2f}".format(row["price"]),\n'
                '        "price_band": price_band(row["price"]),\n'
                '    }\n'
                '\n'
                'buffer = io.StringIO()\n'
                'writer = csv.DictWriter(buffer, fieldnames=FIELDS, lineterminator="\\n")\n'
                'writer.writeheader()\n'
                'writer.writerows(analysis_row(row) for row in rows)\n'
                'print(buffer.getvalue())\n'
                '\n'
                'header = buffer.getvalue().splitlines()[0].split(",")\n'
                'assert header == FIELDS\n'
                'print("export has a stable header and one defined grain")'
            ),
            variant_b='add a "currency" column and keep the numeric price untouched for summing',
            variant_c='export one row per category-day instead of one per product; explain why the grain changed',
            mistakes=[
                "Mixing product rows and daily totals in one export, so any sum double-counts.",
                "Formatting money as text with a currency symbol, which blocks numeric aggregation.",
                "Letting DictWriter infer columns from the first row, so a later field silently disappears.",
            ],
            q1=(
                "Why must the export's grain be decided before adding computed columns?",
                "The grain defines what one row represents; mixing product rows with totals or daily snapshots makes every aggregate ambiguous and often double-counted.",
            ),
            homework=(
                "Write `analysis_rows(rows)` that flattens each record to a fixed column set with a computed price "
                "band and a numeric price, then writes it with DictWriter. Run it on two record sets, print both "
                "CSV outputs, and comment which line fixes the grain and header."
            ),
            patterns=["DictWriter", "FIELDS", "def "],
            mapping=(
                "Analysts consume Parquet or CSV tables with documented columns and grain in tools such as "
                "pandas, DuckDB and BI dashboards. A stable export contract is what lets a dashboard be "
                "refreshed without rewriting every query."
            ),
        ),
        118: dict(
            topic="Idempotent writes",
            idea=(
                "A pipeline you can run twice without changing the result is a pipeline you can trust. That "
                "property is idempotence, and it matters most at the write step. A plain INSERT makes a rerun "
                "duplicate every row, which turns a harmless retry into a corrupted dataset. The fix is to "
                "write against a stable key with an upsert: insert when the key is new, update when it exists, "
                "and leave it untouched when the incoming values are identical. The last clause is what makes "
                "the operation cheap and observable. If every rerun rewrites every row, timestamps churn and "
                "you cannot tell a real change from a no-op. Count inserted, updated and unchanged rows, and "
                "treat a second identical run as a test: inserted and updated should both be zero. Be careful "
                "with the update condition. Updating on every conflict is still logically idempotent for the "
                "final state, but it produces write amplification and misleading audit trails. Also make the "
                "key genuinely stable; an id derived from a field that changes every scrape defeats the whole "
                "design. Wrap the batch in one transaction so a failed rerun cannot leave a partial state. "
                "Today you build a tiny SQLite upsert, run the same batch twice, and then change one price to "
                "prove that only the changed row is touched."
            ),
            code=(
                'import sqlite3\n'
                '\n'
                'conn = sqlite3.connect(":memory:")\n'
                'conn.execute("CREATE TABLE prices (id TEXT PRIMARY KEY, price REAL NOT NULL)")\n'
                '\n'
                'def upsert(rows):\n'
                '    before = conn.total_changes\n'
                '    conn.executemany(\n'
                '        "INSERT INTO prices (id, price) VALUES (?, ?) "\n'
                '        "ON CONFLICT(id) DO UPDATE SET price = excluded.price "\n'
                '        "WHERE excluded.price != prices.price",\n'
                '        rows,\n'
                '    )\n'
                '    conn.commit()\n'
                '    return conn.total_changes - before\n'
                '\n'
                'batch = [("a1", 9.99), ("a2", 12.5)]\n'
                'first = upsert(batch)\n'
                'second = upsert(batch)\n'
                'changed = upsert([("a1", 10.5), ("a2", 12.5)])\n'
                'print("first write changed:", first)\n'
                'print("same batch again changed:", second)\n'
                'print("one price changed:", changed)\n'
                '\n'
                'stored = conn.execute("SELECT id, price FROM prices ORDER BY id").fetchall()\n'
                'print("stored:", stored)\n'
                'assert (first, second, changed) == (2, 0, 1)\n'
                'assert stored == [("a1", 10.5), ("a2", 12.5)]\n'
                'conn.close()\n'
                'print("reruns converge on the same state")'
            ),
            variant_b='drop the WHERE clause so every conflict updates; compare the changed-row count',
            variant_c='add a third column "updated_at" and decide whether an identical rerun should touch it',
            mistakes=[
                "Using plain INSERT, so a retry duplicates every row instead of converging.",
                "Updating on every conflict, which churns unchanged rows and hides real changes in the audit trail.",
                "Deriving the key from a volatile field, so the same item looks new on each run.",
            ],
            q1=(
                "Why should an identical rerun report zero inserted and zero updated rows?",
                "The write already matches the incoming values, so touching them would create churn without changing the final state, and the counts are the proof that idempotence holds.",
            ),
            homework=(
                "Write `upsert(rows)` that inserts or updates by primary key and returns the number of changed "
                "rows. Run the same batch twice, then change one price, print all three counts, and comment "
                "which line prevents an unchanged row from being rewritten."
            ),
            patterns=["ON CONFLICT", "executemany", "commit("],
            mapping=(
                "Warehouse MERGE statements and dbt incremental models implement the same insert-or-update "
                "contract, and orchestration systems retry tasks precisely because writes are expected to be "
                "safe to repeat."
            ),
        ),
        119: dict(
            topic="Review: a clean dataset",
            idea=(
                "The phase ends by joining the stages into one small pipeline: parse, normalise, identify, "
                "validate, deduplicate, store and export. The order is not arbitrary. Normalise before "
                "deriving an identifier, or near-duplicates escape. Validate before storing, or a bad row "
                "occupies a key. Deduplicate before the write, or the database has to absorb rows that should "
                "never have existed. Store with a stable key and an upsert, so rerunning the whole script is "
                "safe. Export only after the stored data has been checked, and let the export declare its "
                "grain and columns. This ordering is the practical content of the phase; individual functions "
                "are easy, but a pipeline is defined by its contracts between stages. Each stage should have "
                "one input shape and one output shape, and each should be testable on a fixture without a "
                "network. A run report closes the loop: input rows, rejected rows, duplicates removed, rows "
                "written and rows unchanged. Those five numbers tell you whether the pipeline did what you "
                "think it did. Keep the final example intentionally compact. It is a reference for the shape, "
                "not a production scraper. When you extend it, add a stage at a time and rerun the report, so "
                "a regression shows up as a changed count rather than as a subtly wrong dataset discovered "
                "weeks later."
            ),
            code=(
                'import csv\n'
                'import io\n'
                'import re\n'
                'import sqlite3\n'
                '\n'
                'raw = ["  Dune |9.99", "Dune|9.99", "Foundation|12.50", "  |7.00"]\n'
                '\n'
                'def clean(value):\n'
                '    return re.sub(r"\\s+", " ", value.replace("\\u00a0", " ")).strip()\n'
                '\n'
                'def parse(line):\n'
                '    title, price = line.rsplit("|", 1)\n'
                '    return {"title": clean(title), "price": float(price)}\n'
                '\n'
                'conn = sqlite3.connect(":memory:")\n'
                'conn.execute("CREATE TABLE books (id TEXT PRIMARY KEY, title TEXT NOT NULL, price REAL NOT NULL)")\n'
                'report = {"input": 0, "rejected": 0, "duplicates": 0, "written": 0}\n'
                'seen = set()\n'
                'for line in raw:\n'
                '    report["input"] += 1\n'
                '    row = parse(line)\n'
                '    if not row["title"] or row["price"] <= 0:\n'
                '        report["rejected"] += 1\n'
                '        continue\n'
                '    key = "{}|{:.2f}".format(row["title"].casefold(), row["price"])\n'
                '    if key in seen:\n'
                '        report["duplicates"] += 1\n'
                '        continue\n'
                '    seen.add(key)\n'
                '    conn.execute("INSERT INTO books VALUES (?, ?, ?)", (key, row["title"], row["price"]))\n'
                '    report["written"] += 1\n'
                'conn.commit()\n'
                '\n'
                'rows = conn.execute("SELECT title, price FROM books ORDER BY title").fetchall()\n'
                'for title, price in rows:\n'
                '    print(title, f"{price:.2f}")\n'
                'print("report:", report)\n'
                'assert report == {"input": 4, "rejected": 1, "duplicates": 1, "written": 2}\n'
                'assert len(rows) == 2\n'
                'conn.close()\n'
                'print("clean dataset: validated, deduplicated, stored")'
            ),
            variant_b='add "Neuromancer|0" to raw and explain which rejection rule catches it',
            variant_c='rerun the insert loop against the same connection and make the write an upsert',
            mistakes=[
                'Deduplicating before normalisation, so "  Dune" and "Dune" both survive.',
                "Storing before validation, so a blank title consumes a primary key.",
                "Skipping the run report, so a rejected row looks like a successful load.",
            ],
            q1=(
                "Why does the pipeline normalise and validate before it computes the deduplication key?",
                "Normalisation makes equal items hash equally, and validation keeps invalid rows out of the key space; doing either later lets duplicates or blank records reach storage.",
            ),
            homework=(
                "Write `build_dataset(raw_lines)` that parses, normalises, validates, deduplicates and stores rows "
                "in SQLite, returning a run report. Run it on two different raw inputs, print each report and "
                "the stored rows, and comment which stage prevented the invalid row from being written."
            ),
            patterns=["def build_dataset", "sqlite3", "report"],
            mapping=(
                "This is the shape of a small ELT job: land raw text, normalise and validate, deduplicate, load "
                "with a stable key, then publish a report. The same stages map to pandas transforms, SQL MERGE "
                "statements and orchestrated tasks as the dataset grows."
            ),
        ),
    },
)
