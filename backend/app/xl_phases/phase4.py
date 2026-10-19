"""Excel Automation phase 4, days 120-134: files, formats and integration.

Everything here is stdlib-only, offline and deterministic. Files are modelled as
in-memory strings and folders as lists or sets of path strings, so examples run
without touching a real disk, clock or network.
"""

PHASE = (
    "Files, Formats and Integration",
    "Move data safely between CSV text, JSON and dated report files while keeping every step testable and reversible.",
    {
        120: dict(
            topic="Orientation: files and formats",
            idea=(
                "Automation begins with a model of the inputs, not with code that opens them. A file is bytes "
                "with a name, and the name's extension is a claim, not a guarantee: a .csv can be "
                "tab-separated, a .txt can hold JSON, and an .xlsx is really a zip archive. The useful model "
                "for this phase is simpler: a source has a path, a format, and a text body. Formats fall into "
                "families — rows and columns for CSV and TSV, trees for JSON, free text for logs and notes. "
                "Once you name the family, the operations become obvious: tables get parsed into records, trees "
                "get flattened into rows, and reports always leave as table-shaped text. You should also decide "
                "early where conversion happens. Reading is bytes to text, parsing is text to records, "
                "transforming is records to records, and writing is records back to text. Keeping those four "
                "steps separate is what makes a pipeline testable without a worksheet on disk. Today you "
                "classify a handful of in-memory files by extension and family, and print what each one would "
                "become after parsing. The point is not the classifier; it is the map of formats that tells you "
                "which tool to reach for next."
            ),
            code=(
                'FILES = [\n'
                '    ("sales.csv", "comma-separated rows"),\n'
                '    ("export.json", "nested records"),\n'
                '    ("notes.txt", "free text"),\n'
                '    ("report_2026-01-31.csv", "dated report"),\n'
                ']\n'
                '\n'
                'def extension(path):\n'
                '    return path.rsplit(".", 1)[-1].lower()\n'
                '\n'
                'def kind(path):\n'
                '    return {"csv": "table", "json": "tree", "txt": "text"}.get(extension(path), "unknown")\n'
                '\n'
                'for name, description in FILES:\n'
                '    print(f"{name:24} {extension(name):4} {kind(name):7} {description}")\n'
                '\n'
                'assert kind("a.CSV") == "table"\n'
                'print("format comes from the content, not the name")\n'
            ),
            variant_b='add a "tsv" family mapped to the table kind and classify a sample path',
            variant_c='return "unknown" for a path with no dot and print that result',
            mistakes=[
                "Trusting the extension instead of inspecting the actual content.",
                "Mixing reading, parsing and writing into one function that cannot be tested in parts.",
                "Crashing on a path without a dot instead of returning a deliberate unknown.",
            ],
            q1=(
                "Why treat reading, parsing, transforming and writing as separate steps?",
                "Each step becomes a value you can print, test and replace independently, so a format change only touches one edge.",
            ),
            homework=(
                "Write `classify(paths)` that takes a list of path strings and returns a dict mapping each "
                "lowercase extension to the number of files with it. Print the counts sorted by extension and "
                "comment which line handles a file with no dot."
            ),
            patterns=["def ", "rsplit", "print("],
            mapping=(
                "Excel exports, API dumps and copied text all arrive in different formats; naming the format "
                "family first is what tells you whether to reach for csv, json or an openpyxl reader."
            ),
        ),
        121: dict(
            topic="Reading CSV from text",
            idea=(
                "Reading CSV from text is the same operation whether the text came from a file, a clipboard, or "
                "a network response. The `csv` module is the right tool because it follows the quoting rules "
                "that exports actually use: a field may contain the delimiter inside double quotes, a quote "
                "inside a field is doubled, and line endings may be `\\n` or `\\r\\n`. Wrapping the string in "
                "`io.StringIO` gives the module a file-like object, so the code you write today is exactly the "
                "code you would run against a real file later. The important design choice is the output shape. "
                "`csv.reader` yields lists, which is honest but positional; building dicts keyed by the header "
                "row makes the rest of your logic independent of column order. Keep values as strings at this "
                "stage. A quantity of 3 and a code of 007 both arrive as text, and converting eagerly destroys "
                "information you may need. Today you read a small table that contains a quoted comma, print the "
                "header and each record by name, and assert that the quoted field stayed intact. Notice how "
                "little code is needed once parsing is delegated to the standard library, and how much manual "
                "splitting would have cost you."
            ),
            code=(
                'import csv\n'
                'import io\n'
                '\n'
                "RAW = 'name,qty,note\\nwidget,3,\"ships, boxed\"\\ngizmo,1,plain\\n'\n"
                '\n'
                'def read_table(text):\n'
                '    reader = csv.reader(io.StringIO(text))\n'
                '    header = next(reader)\n'
                '    return header, [dict(zip(header, row)) for row in reader]\n'
                '\n'
                'header, records = read_table(RAW)\n'
                'print("header:", header)\n'
                'for record in records:\n'
                '    print(record["name"], record["qty"], "|", record["note"])\n'
                '\n'
                'assert records[0]["note"] == "ships, boxed"\n'
                'print("quoted commas stay inside one field")\n'
            ),
            variant_b='add a row whose note contains a doubled quote and print the parsed value',
            variant_c='return records keyed by position instead of name and show why later code gets harder',
            mistakes=[
                "Splitting lines on commas by hand, so quoted fields containing commas break apart.",
                "Converting every value to a number on read, losing leading zeros in codes.",
                "Consuming the header twice or treating it as a data record.",
            ],
            q1=(
                "Why wrap an in-memory string in io.StringIO before parsing it with csv?",
                "It gives the csv module the file-like object it expects, so the same code works on text and on a real file.",
            ),
            homework=(
                "Write `read_records(text)` that uses `csv.reader` and returns a list of dicts keyed by the "
                "first row. Feed it a table with a quoted comma, print each record, and comment which line "
                "separates the header from the data rows."
            ),
            patterns=["def ", "csv.reader", "print("],
            mapping=(
                "This is the exact parse step for a CSV export saved from Excel; the resulting records feed "
                "every later transform in the pipeline."
            ),
        ),
        122: dict(
            topic="Writing CSV to text",
            idea=(
                "Writing CSV looks trivial until a value contains a comma, a quote, or a newline. The "
                "`csv.writer` handles all three by quoting only when necessary, which is why you should hand it "
                "rows rather than build strings with `join`. The same in-memory pattern used for reading "
                "applies in reverse: create a `StringIO` buffer, attach a writer, write the header, write the "
                "rows, and return `getvalue()`. Fixing the line terminator to `\\n` makes the output stable "
                "across platforms and makes assertions on exact text predictable; otherwise the writer may emit "
                "`\\r\\n` and your comparison fails for a reason unrelated to your logic. Two habits make written "
                "reports trustworthy. First, always write the header, even when there are no data rows, because "
                "a downstream reader needs the column names to interpret anything at all. Second, serialise the "
                "values exactly as you validated them, including rounding and text conversion, so the file "
                "cannot disagree with the numbers your checks approved. The header is also the contract: whoever "
                "reads the file depends on those exact column names, so changing them is a breaking change, not "
                "a cosmetic one. Today you build a tiny writer, feed it a value that needs quoting, print the "
                "resulting text, and assert one exact line. The writer is the last step of every report you will "
                "produce."
            ),
            code=(
                'import csv\n'
                'import io\n'
                '\n'
                'def write_table(header, rows):\n'
                '    buffer = io.StringIO()\n'
                '    writer = csv.writer(buffer, lineterminator="\\n")\n'
                '    writer.writerow(header)\n'
                '    writer.writerows(rows)\n'
                '    return buffer.getvalue()\n'
                '\n'
                'text = write_table(["item", "note"], [["widget", "plain"], ["gizmo", "has, comma"]])\n'
                'print(text, end="")\n'
                'print("lines:", len(text.splitlines()))\n'
                'print("quoted:", \'"has, comma"\' in text)\n'
                '\n'
                'assert text.splitlines()[2] == \'gizmo,"has, comma"\'\n'
                'print("writer quotes only when needed")\n'
            ),
            variant_b='write a header with no data rows and confirm the header still appears',
            variant_c='drop lineterminator and print repr(text) to see the platform line endings',
            mistakes=[
                "Joining fields with commas by hand, so values containing commas corrupt the row.",
                "Skipping the header when there are no data rows, leaving an unreadable file.",
                "Leaving raw floats unrounded so the file disagrees with the checked values.",
            ],
            q1=(
                "Why pass rows to csv.writer instead of joining fields into a line yourself?",
                "The writer applies correct quoting and escaping for commas, quotes and newlines that manual joining mishandles.",
            ),
            homework=(
                "Write `write_csv(header, rows)` that returns CSV text using `csv.writer` over `io.StringIO` "
                "with a fixed newline. Write one value containing a comma, print the text, and comment which "
                "line keeps the header even when rows is empty."
            ),
            patterns=["def ", "csv.writer", "print("],
            mapping=(
                "Reports saved from your scripts go through this exact serialiser; getting quoting and headers "
                "right is what makes them open cleanly in Excel."
            ),
        ),
        123: dict(
            topic="Tabs, semicolons and delimiters",
            idea=(
                "Delimiters are a property of the data, not of the file extension. The same export tool can emit "
                "commas, tabs, or semicolons depending on locale, and European spreads often use semicolons "
                "because the comma is the decimal separator. `csv.Sniffer` samples the text and guesses a "
                "dialect, which is convenient but not magic: a file with one column gives it nothing to count, "
                "and a file where commas appear inside fields can mislead it. The reliable pattern is to sniff a "
                "sample, then pass the delimiter explicitly to the reader, and to keep an override for the cases "
                "where detection is wrong. Detection should never be the only option in a production script. You "
                "also need to think about the interaction between delimiter and quoting. A semicolon-separated "
                "file may still quote a field that contains a semicolon, so parsing must go through the `csv` "
                "module rather than `split`. Today you build three short samples, detect each delimiter, re-read "
                "the rows with that delimiter, and print the header that came back. Then you test an ambiguous "
                "single-column sample and note that detection may return nothing. The lesson is to treat "
                "delimiter as input you verify, not as something you assume from a filename."
            ),
            code=(
                'import csv\n'
                'import io\n'
                '\n'
                'SAMPLES = {\n'
                '    "comma": "a,b,c\\n1,2,3\\n",\n'
                '    "tab": "a\\tb\\tc\\n1\\t2\\t3\\n",\n'
                '    "semicolon": "a;b;c\\n1;2;3\\n",\n'
                '}\n'
                '\n'
                'def pick(text):\n'
                '    try:\n'
                '        return csv.Sniffer().sniff(text, delimiters=",;\\t").delimiter\n'
                '    except csv.Error:\n'
                '        return None\n'
                '\n'
                'for label, text in SAMPLES.items():\n'
                '    delimiter = pick(text)\n'
                '    rows = list(csv.reader(io.StringIO(text), delimiter=delimiter))\n'
                '    print(label, "->", repr(delimiter), rows[0])\n'
                '\n'
                'assert pick(SAMPLES["semicolon"]) == ";"\n'
                'print("sniff a sample, then pass the delimiter explicitly")\n'
            ),
            variant_b='add a semicolon sample whose field is quoted and confirm the quotes are removed',
            variant_c='pass an explicit delimiter override and bypass sniffing entirely',
            mistakes=[
                "Assuming commas because the file ends in .csv, so tab-separated exports parse as one column.",
                "Using split on a delimiter instead of the csv module, breaking quoted fields.",
                "Letting sniffing be the only path, so a single-column file has no fallback.",
            ],
            q1=(
                "Why should delimiter detection be paired with an explicit override?",
                "Sniffing is a guess that fails on short or ambiguous samples, so callers need a way to state the delimiter definitively.",
            ),
            homework=(
                "Write `detect(text)` that returns the delimiter chosen by `csv.Sniffer` from comma, semicolon "
                "and tab, or None on failure. Test it on three samples, print each result, and comment which "
                "line keeps detection from being the only option."
            ),
            patterns=["def ", "Sniffer", "print("],
            mapping=(
                "Excel's regional settings change the default list separator, so a script that opens exported "
                "files must verify the delimiter before treating the data as columns."
            ),
        ),
        124: dict(
            topic="Encodings and the BOM",
            idea=(
                "Encoding problems look like corrupted text but are really a disagreement about bytes. A file "
                "written as UTF-8 and read as Latin-1 turns accented characters into mojibake, and a file "
                "written with a byte-order mark leaves an invisible character glued to the first header name. "
                "That single character is enough to break `record[\"name\"]`, because the key is now "
                "`\"\\ufeffname\"`. The standard fix is to decode with `utf-8-sig`, which removes the mark when "
                "present and behaves like plain UTF-8 when it is not. You can model the whole thing in memory: "
                "take a string, encode it to UTF-8 with a BOM, decode it with `utf-8-sig`, and compare the "
                "header before and after. The same reasoning applies to writing: if a downstream tool insists "
                "on a BOM, encode with `utf-8-sig`; otherwise write plain UTF-8 and say so in your "
                "documentation. Be explicit about encoding everywhere, because the default varies by platform "
                "and by Python version, and a script that works on one machine can corrupt accents on another. "
                "Today you decode a BOM-prefixed table, show that the first header loses the invisible mark, and "
                "assert the clean key. The habit worth keeping is to check the first header cell whenever a "
                "column mysteriously does not exist."
            ),
            code=(
                'import csv\n'
                'import io\n'
                '\n'
                'RAW_BYTES = "\\ufeffname,qty\\nwidget,3\\n".encode("utf-8")\n'
                '\n'
                'def decode(text_bytes):\n'
                '    return text_bytes.decode("utf-8-sig")\n'
                '\n'
                'text = decode(RAW_BYTES)\n'
                'header = next(csv.reader(io.StringIO(text)))\n'
                'print("first header:", repr(header[0]))\n'
                'print("starts with BOM:", text.startswith("\\ufeff"))\n'
                'print("first bytes:", text.encode("utf-8")[:8])\n'
                '\n'
                'assert header == ["name", "qty"]\n'
                'assert not text.startswith("\\ufeff")\n'
                'print("utf-8-sig strips the BOM on read")\n'
            ),
            variant_b='decode the same bytes as plain utf-8 and print the first header to see the mark',
            variant_c='re-encode the clean text with utf-8-sig and confirm the BOM comes back',
            mistakes=[
                "Reading a BOM-prefixed file as plain UTF-8, so the first header key carries an invisible character.",
                "Silently replacing undecodable bytes instead of surfacing the encoding mismatch.",
                "Relying on the platform default encoding, which differs between systems.",
            ],
            q1=(
                "Why does a BOM break a dict lookup on the first column name?",
                "The mark becomes part of that key, so the lookup string without it does not match the stored header.",
            ),
            homework=(
                "Write `read_bom(text_bytes)` that decodes UTF-8 with a BOM and returns the first header cell. "
                "Encode a sample string with `utf-8-sig`, print the cleaned header, and comment which line "
                "prevents the invisible mark from joining the column name."
            ),
            patterns=["def ", "utf-8-sig", "print("],
            mapping=(
                "Excel's Save as CSV often writes a BOM for compatibility; stripping it on read is what keeps "
                "header-based column access working."
            ),
        ),
        125: dict(
            topic="JSON to rows",
            idea=(
                "JSON is a tree, and most reports want a table, so the core skill is flattening without losing "
                "fields. A list of objects maps naturally to rows: take the union of keys as the header, then "
                "pull each key from each object. The subtle parts are missing keys and nested values. A record "
                "that lacks an optional field should become an empty cell rather than an error, and a nested "
                "object or list has to be either flattened with a dotted name or serialised back into a single "
                "cell. Both choices are defensible, but you must make one deliberately and apply it everywhere. "
                "Values also arrive typed: numbers stay numbers, booleans stay booleans, and null becomes None, "
                "which the CSV writer turns into an empty string. That is usually what you want, though it means "
                "a real zero and a missing value can look similar unless you choose a different sentinel. Today "
                "you parse a small JSON array, derive a fixed header, build the rows with `.get`, and write them "
                "to CSV text in memory. Then you print the result and assert that the missing field became a "
                "blank. This is the standard bridge from an API response to something a spreadsheet can open."
            ),
            code=(
                'import csv\n'
                'import io\n'
                'import json\n'
                '\n'
                'RAW = \'[{"item": "widget", "qty": 3}, {"item": "gizmo", "qty": 1, "note": "frail"}]\'\n'
                '\n'
                'def to_rows(text):\n'
                '    records = json.loads(text)\n'
                '    header = ["item", "qty", "note"]\n'
                '    rows = [[record.get(name, "") for name in header] for record in records]\n'
                '    return header, rows\n'
                '\n'
                'header, rows = to_rows(RAW)\n'
                'buffer = io.StringIO()\n'
                'writer = csv.writer(buffer, lineterminator="\\n")\n'
                'writer.writerow(header)\n'
                'writer.writerows(rows)\n'
                'print(buffer.getvalue(), end="")\n'
                'print("missing keys become blanks, not errors")\n'
                '\n'
                'assert rows[0] == ["widget", 3, ""]\n'
            ),
            variant_b='derive the header from the union of keys instead of hard-coding it',
            variant_c='flatten a nested object into dotted column names and print the wider row',
            mistakes=[
                "Assuming every object has every key, so one missing optional field aborts the run.",
                "Leaving a nested list in a cell so the CSV text contains unreadable Python or JSON fragments.",
                "Confusing null with zero instead of choosing and documenting a representation.",
            ],
            q1=(
                "What should happen when a JSON record lacks one of the header fields?",
                "Fill the cell with an empty string using a safe lookup, so the row shape stays consistent.",
            ),
            homework=(
                "Write `flatten(text)` that parses a JSON array of objects and returns a header plus rows, "
                "filling missing keys with an empty string. Print the CSV text for a sample with one missing "
                "field and comment which line chooses the blank instead of raising."
            ),
            patterns=["def ", "json.loads", "print("],
            mapping=(
                "API responses and Power Query JSON exports arrive as trees; flattening them to rows is the "
                "step that lets Excel formulas and PivotTables work on them."
            ),
        ),
        126: dict(
            topic="Rows to JSON",
            idea=(
                "Going the other way, from rows to JSON, is mostly about types and stability. CSV gives you "
                "strings; JSON consumers expect numbers to be numbers and booleans to be booleans, so the "
                "conversion has to be explicit. Do it field by field with named conversions rather than guessing "
                "from the text, because `\"007\"` and `\"1,234\"` are both traps for a generic converter. Once "
                "the records exist, `json.dumps` does the rest. Pass `sort_keys=True` so the output is stable "
                "regardless of dictionary insertion order, and choose an indent deliberately: compact output is "
                "better for machines, indented output is better for diffs and review. Keep the shape simple — a "
                "list of objects is the most portable form and maps cleanly onto both a spreadsheet and an API "
                "payload. Avoid wrapping the list in a custom envelope unless a consumer demands one. Keep the "
                "output one record per line when a streaming reader might consume it, because a single "
                "multi-megabyte array is harder to process incrementally. Today you convert a two-row table "
                "into typed records, serialise them, print the JSON, and parse it back to prove it is valid. "
                "The round trip is the check that matters: if `json.loads` returns what you expect, the file is "
                "usable by anything else."
            ),
            code=(
                'import json\n'
                '\n'
                'ROWS = [\n'
                '    {"item": "widget", "qty": "3"},\n'
                '    {"item": "gizmo", "qty": "1"},\n'
                ']\n'
                '\n'
                'def to_json(rows):\n'
                '    records = []\n'
                '    for row in rows:\n'
                '        records.append({"item": row["item"], "qty": int(row["qty"])})\n'
                '    return json.dumps(records, indent=2, sort_keys=True)\n'
                '\n'
                'text = to_json(ROWS)\n'
                'print(text)\n'
                '\n'
                'assert json.loads(text)[0]["qty"] == 3\n'
                'print("valid json:", json.loads(text)[0]["item"])\n'
            ),
            variant_b='add a "price" field converted with float and confirm the JSON type changes',
            variant_c='serialise with indent=None and compare the compact text with the indented version',
            mistakes=[
                "Guessing types from text, so a code like 007 becomes the number 7.",
                "Using insertion order as the output order, making diffs noisy between runs.",
                "Never parsing the output back, so invalid JSON ships unnoticed.",
            ],
            q1=(
                "Why convert fields explicitly instead of letting a generic converter guess types?",
                "Guessing destroys meaningful text such as leading zeros, while named conversions encode the actual rule for each column.",
            ),
            homework=(
                "Write `to_json(rows)` that converts CSV-style string rows into typed JSON text with integer "
                "quantities and sorted keys. Print the result, parse it back, and comment which line proves the "
                "output is valid JSON."
            ),
            patterns=["def ", "json.dumps", "print("],
            mapping=(
                "Feeding a spreadsheet extract to a web service or Power Automate flow requires exactly this "
                "typed JSON conversion."
            ),
        ),
        127: dict(
            topic="Combining several inputs",
            idea=(
                "Real reports rarely come from one source. You get orders in one export, prices in another, and "
                "customer names in a third, and the job is to join them on a shared key. The in-memory version "
                "of a join is a dictionary keyed by that shared identifier: read each input into a lookup, then "
                "loop over the primary source and attach the fields you need. This is the same idea as a "
                "spreadsheet `VLOOKUP` or a database join, with one important difference: you can see and test "
                "what happens when the key is missing. Decide the policy up front. A missing price can be skipped "
                "and counted, an unknown customer can be labelled, and a duplicate key should probably raise an "
                "error rather than silently keep the last row. Sorting the output by key makes runs comparable "
                "and diffs readable. You should also keep the inputs and the join separate, so each parser can "
                "be tested alone and the join can be tested with hand-built dictionaries. Today you join two "
                "tiny tables on id, compute a line total, print each row in key order, and assert one exact "
                "result. The counts of matched and unmatched rows are part of a trustworthy report, not an "
                "afterthought."
            ),
            code=(
                'import csv\n'
                'import io\n'
                '\n'
                'ORDERS = "id,qty\\n1,2\\n2,5\\n"\n'
                'PRICES = "id,price\\n1,2.50\\n2,1.00\\n"\n'
                '\n'
                'def rows(text):\n'
                '    return {row["id"]: row for row in csv.DictReader(io.StringIO(text))}\n'
                '\n'
                'def combine(orders_text, prices_text):\n'
                '    orders = rows(orders_text)\n'
                '    prices = rows(prices_text)\n'
                '    out = []\n'
                '    for key in sorted(orders, key=int):\n'
                '        qty = int(orders[key]["qty"])\n'
                '        price = float(prices[key]["price"])\n'
                '        out.append([key, qty, f"{qty * price:.2f}"])\n'
                '    return out\n'
                '\n'
                'for row in combine(ORDERS, PRICES):\n'
                '    print(row)\n'
                '\n'
                'assert combine(ORDERS, PRICES)[1] == ["2", 5, "5.00"]\n'
                'print("joined on id, sorted by id")\n'
            ),
            variant_b='add an unknown order id and print a clearly labelled missing-price row',
            variant_c='count matched and unmatched ids and print both totals',
            mistakes=[
                "Indexing the lookup without checking membership, so one missing key aborts the join.",
                "Keeping the last duplicate silently instead of detecting and reporting the clash.",
                "Producing output in dictionary order, making runs hard to compare.",
            ],
            q1=(
                "Why decide the missing-key policy before writing the join loop?",
                "Every lookup either skips, labels or raises, and choosing after the fact hides which rows changed the totals.",
            ),
            homework=(
                "Write `join(orders_text, prices_text)` that parses both CSV strings, keys records by id, and "
                "returns rows with quantity, price and line total. Print every joined row sorted by id and "
                "comment which line decides what happens to an unmatched id."
            ),
            patterns=["def ", "DictReader", "print("],
            mapping=(
                "This is a VLOOKUP or Power Query merge in code: multiple exported sheets combine on a key "
                "before any totals are calculated."
            ),
        ),
        128: dict(
            topic="Appending to an existing report",
            idea=(
                "Appending to an existing report is where many otherwise correct scripts break a file. The "
                "header must appear once, the new rows must use the same column order, and the file must not be "
                "truncated when something fails mid-write. In an in-memory model you can see the shape of the "
                "problem: split the existing text into lines, treat the first line as the header, parse the "
                "remaining lines as rows, add the new rows, and serialise everything fresh. That is "
                "intentionally not an in-place edit; rewriting the whole text is simpler to reason about and "
                "matches what a safe writer does through a temporary file. Two edge cases deserve attention. An "
                "empty existing report may still contain only the header, so appending is valid; a completely "
                "empty string has no header at all, so you must decide whether to reject it or treat the new "
                "rows as the start of a new report. Silently adding a second header is the worst outcome, "
                "because readers will treat it as data. Today you append two rows to a report that already has "
                "data, print the result, and assert that the header occurs exactly once. Keeping the header "
                "invariant is the whole lesson."
            ),
            code=(
                'import csv\n'
                'import io\n'
                '\n'
                'EXISTING = "item,qty\\nwidget,3\\n"\n'
                '\n'
                'def append_rows(report_text, new_rows):\n'
                '    lines = report_text.splitlines()\n'
                '    header = lines[0]\n'
                '    buffer = io.StringIO()\n'
                '    writer = csv.writer(buffer, lineterminator="\\n")\n'
                '    for line in lines[1:]:\n'
                '        writer.writerow(next(csv.reader([line])))\n'
                '    writer.writerows(new_rows)\n'
                '    return header + "\\n" + buffer.getvalue()\n'
                '\n'
                'text = append_rows(EXISTING, [["gizmo", 1], ["bolt", 4]])\n'
                'print(text, end="")\n'
                'print("data rows:", len(text.splitlines()) - 1)\n'
                '\n'
                'assert text.count("item,qty") == 1\n'
                'print("header written once, new rows appended")\n'
            ),
            variant_b='append to a report that has only a header and confirm the result is valid',
            variant_c='reject an empty existing report with a clear message instead of inventing a header',
            mistakes=[
                "Appending rows including their own header, so the file gains a second header line.",
                "Assuming the new rows have the same column order as the existing report.",
                "Truncating the file before the new rows are safely prepared.",
            ],
            q1=(
                "Why rewrite the whole report text instead of inserting rows in place?",
                "A full rewrite is simple to reason about and mirrors the temporary-file pattern that keeps partial writes from destroying data.",
            ),
            homework=(
                "Write `append(report_text, rows)` that keeps the existing header, adds the new rows and "
                "returns the full text. Print the result for a report with one existing row and comment which "
                "line guarantees the header appears only once."
            ),
            patterns=["def ", "splitlines", "print("],
            mapping=(
                "Daily batches often append to a running CSV used by Excel; keeping one header is what stops "
                "downstream formulas from treating it as a data row."
            ),
        ),
        129: dict(
            topic="Dated output filenames",
            idea=(
                "A report filename is part of the report. A dated name such as `report_2026-01-31.csv` sorts "
                "chronologically, never overwrites yesterday's run, and tells a human which period the numbers "
                "cover without opening the file. The key discipline is to pass the date in as a value, formatted "
                "once, rather than reading the clock deep inside a function. That makes the naming function "
                "deterministic and testable, and it means the run date can come from a command-line argument, a "
                "batch header, or a test. Use ISO dates — `YYYY-MM-DD` — because they sort lexically in the same "
                "order as they sort in time. When you need to find reports later, `fnmatch` with a pattern like "
                "`report_????-??-??.csv` selects exactly the dated files and ignores unrelated inputs. Note that "
                "this is a filename convention, not proof of content, so a scan should still open and validate "
                "what it finds; a renamed file is a common way a report ends up in the wrong period's folder. "
                "Today you build names from fixed date strings, classify them with a pattern, and print which "
                "ones match. The important test is that the same date always yields the same name, and that the "
                "function never reaches for the system clock."
            ),
            code=(
                'import fnmatch\n'
                '\n'
                'def report_name(date_text, suffix="csv"):\n'
                '    return f"report_{date_text}.{suffix}"\n'
                '\n'
                'def is_report(name):\n'
                '    return fnmatch.fnmatch(name, "report_????-??-??.csv")\n'
                '\n'
                'names = [report_name("2026-01-31"), report_name("2026-02-01"), "notes.csv"]\n'
                'for name in names:\n'
                '    print(name, "report" if is_report(name) else "other")\n'
                'print("matched:", [n for n in names if is_report(n)])\n'
                '\n'
                'assert report_name("2026-01-31") == "report_2026-01-31.csv"\n'
                'print("the date is passed in, never read from the clock")\n'
            ),
            variant_b='add a time suffix and use a pattern that still matches both variants',
            variant_c='pass a deliberately malformed date and show that the pattern rejects it',
            mistakes=[
                "Reading the clock inside the naming function, so the same call gives different names in tests.",
                "Using a local date format like 31-01-2026 that sorts as text in the wrong order.",
                "Assuming a matching filename guarantees the contents belong to that date.",
            ],
            q1=(
                "Why should the date be a parameter rather than read inside the naming function?",
                "A passed value keeps the function deterministic and lets tests and batch runs supply an explicit reporting date.",
            ),
            homework=(
                "Write `report_name(date_text)` that returns a dated CSV filename from a date string, plus "
                "`is_report(name)` using `fnmatch`. Print names for two fixed dates and classify them, "
                "commenting which line keeps the function independent of the clock."
            ),
            patterns=["def ", "fnmatch", "print("],
            mapping=(
                "Scheduled Excel report exports are usually named by period; ISO dates make the archive sort "
                "correctly in Explorer and in a script that scans it."
            ),
        ),
        130: dict(
            topic="Scanning a folder for inputs",
            idea=(
                "Scanning a folder is a filtering problem before it is an I/O problem. Model the folder as a "
                "list of path strings and the scan as a predicate: which paths match the patterns I care about? "
                "`fnmatch` gives you shell-style matching for `*.csv`, `sales_*.csv`, or "
                "`report_????-??-??.csv`, and `sorted` gives you a stable order so runs are reproducible. Think "
                "about what to exclude as carefully as what to include. Temporary files, lock files, previous "
                "outputs, and backups can all match a loose pattern, so either narrow the pattern or filter the "
                "names explicitly. Excluding a directory by prefix is another simple, readable rule. In a real "
                "script this list would come from `Path.glob`, but the logic that decides which files are inputs "
                "stays exactly what you write here, and it is the part most likely to be wrong. Counts are useful "
                "evidence: report how many candidates were found and how many were rejected, so a sudden drop "
                "from twelve inputs to two is visible instead of silent. Today you scan an in-memory folder, "
                "print the matching CSV paths, and show that a `.tmp` file is not picked up. Selection rules "
                "should be explicit, tested and easy to revise."
            ),
            code=(
                'import fnmatch\n'
                '\n'
                'FOLDER = [\n'
                '    "inputs/sales_jan.csv",\n'
                '    "inputs/sales_feb.csv",\n'
                '    "inputs/readme.txt",\n'
                '    "archive/sales_2025.csv",\n'
                '    "inputs/report_bad.csv.tmp",\n'
                ']\n'
                '\n'
                'def scan(paths, pattern):\n'
                '    return sorted(path for path in paths if fnmatch.fnmatch(path, pattern))\n'
                '\n'
                'csvs = scan(FOLDER, "inputs/*.csv")\n'
                'temp = scan(FOLDER, "*.tmp")\n'
                'print("csv inputs:", len(csvs))\n'
                'for path in csvs:\n'
                '    print(" ", path)\n'
                'print("temp files:", temp)\n'
                '\n'
                'assert csvs == ["inputs/sales_feb.csv", "inputs/sales_jan.csv"]\n'
                'print("patterns select files without touching the disk")\n'
            ),
            variant_b='also match a year-specific pattern and print only that subset',
            variant_c='return both matches and a count of rejected paths to make the scan auditable',
            mistakes=[
                "Using a pattern so loose that temporary or previous output files become inputs.",
                "Returning files in listing order so runs differ between machines.",
                "Scanning recursively without excluding an archive folder full of old reports.",
            ],
            q1=(
                "Why report rejected counts alongside the matched input files?",
                "A change in counts is the fastest signal that a naming rule or folder layout broke the scan.",
            ),
            homework=(
                "Write `scan(paths, pattern)` that returns sorted matches using `fnmatch`, plus a count of "
                "rejected paths. Run it over an in-memory list containing CSV, TXT and TMP files, print the "
                "matches, and comment which line keeps the order stable."
            ),
            patterns=["def ", "fnmatch", "print("],
            mapping=(
                "A batch that processes a drop folder in Excel automation starts with exactly this selection "
                "step, and a bad pattern is a common reason files go missing."
            ),
        ),
        131: dict(
            topic="Safe overwrite and backups",
            idea=(
                "Overwriting is the most common way an automation loses data. The safe pattern is simple: never "
                "replace a file that already exists without first preserving a uniquely named copy. A backup "
                "name can be derived with a counter — `report.csv.bak`, then `.bak1`, `.bak2` — chosen by "
                "checking which names already exist in the folder. The check and the write should feel atomic in "
                "your design even when the implementation is small: decide the destination, confirm it is free, "
                "and only then proceed. In a real filesystem you would use a temporary file in the same "
                "directory and rename it into place, because a rename is atomic while a partial write is not. "
                "You should also keep the backup next to the original, not in a distant folder, so recovery is "
                "obvious. The function that plans the write should return both the target and the backup name, "
                "which makes it testable without touching disk and makes the plan printable before anything "
                "happens. Today you model a folder as a set of names, ask for a backup of a report that already "
                "exists, print the plan, and assert that the first free suffix was chosen. Dry-run plans are how "
                "you make destructive steps reviewable."
            ),
            code=(
                'FOLDER = {"report.csv": "old", "report.csv.bak": "older"}\n'
                '\n'
                'def backup_name(existing, name):\n'
                '    candidate = name + ".bak"\n'
                '    counter = 1\n'
                '    while candidate in existing:\n'
                '        candidate = f"{name}.bak{counter}"\n'
                '        counter += 1\n'
                '    return candidate\n'
                '\n'
                'def plan_write(existing, name):\n'
                '    if name not in existing:\n'
                '        return name, None\n'
                '    return name, backup_name(existing, name)\n'
                '\n'
                'target, backup = plan_write(FOLDER, "report.csv")\n'
                'print("write:", target)\n'
                'print("backup to:", backup)\n'
                '\n'
                'assert backup == "report.csv.bak1"\n'
                'print("never overwrite without a unique backup name")\n'
            ),
            variant_b='plan a write for a filename that does not exist and print the None backup',
            variant_c='add a real file list with three backups and show the next free suffix',
            mistakes=[
                "Writing over the previous report before a backup name has been reserved.",
                "Reusing a fixed .bak name, so the second backup overwrites the first.",
                "Putting the backup in another folder that may not be writable.",
            ],
            q1=(
                "Why compute the backup name before any write starts?",
                "Reserving a free name first makes the destructive step reviewable and prevents a second run from clobbering the earlier backup.",
            ),
            homework=(
                "Write `plan_write(existing, name)` that returns the target name and a unique backup name "
                "chosen from the existing set. Test it with report.csv already present, print the plan, and "
                "comment which line makes the suffix unique."
            ),
            patterns=["def ", "while", "print("],
            mapping=(
                "Scheduled reports often rewrite the same workbook; a timestamped or suffixed backup next to it "
                "is what lets an operator recover yesterday's version."
            ),
        ),
        132: dict(
            topic="Reporting what changed",
            idea=(
                "A report that writes silently is only half a report; the other half says what changed. Comparing "
                "an old and a new dataset by key produces three useful groups: keys that appeared, keys that "
                "disappeared, and keys whose values differ. Computing all three in one pass over dictionaries is "
                "cheap and makes the change summary exact. Be careful with types and text forms, because the same "
                "quantity read from CSV is a string in both runs, while the same quantity read from JSON may be "
                "an integer in one and a string in the other. Normalise before comparing, or the diff will report "
                "noise as change. The output should name the keys and counts, not just a total, because three "
                "changes does not tell an operator whether to worry. A stable sort of key names keeps the "
                "summary readable across runs. In a real pipeline this summary goes into the email body or the "
                "log line next to the output filename, so a reader can see both what was produced and how it "
                "differs from last time. Today you diff two small record lists, print added, removed, and changed "
                "keys, and assert the exact summary. Treat the diff as a first-class output, not a debugging "
                "leftover."
            ),
            code=(
                'OLD = [{"id": "1", "qty": "2"}, {"id": "2", "qty": "5"}]\n'
                'NEW = [{"id": "1", "qty": "4"}, {"id": "3", "qty": "1"}]\n'
                '\n'
                'def diff(old_rows, new_rows):\n'
                '    before = {row["id"]: row for row in old_rows}\n'
                '    after = {row["id"]: row for row in new_rows}\n'
                '    added = sorted(set(after) - set(before))\n'
                '    removed = sorted(set(before) - set(after))\n'
                '    changed = sorted(k for k in set(before) & set(after) if before[k] != after[k])\n'
                '    return {"added": added, "removed": removed, "changed": changed}\n'
                '\n'
                'changes = diff(OLD, NEW)\n'
                'for key in sorted(changes):\n'
                '    print(key + ":", changes[key])\n'
                '\n'
                'assert changes == {"added": ["3"], "removed": ["2"], "changed": ["1"]}\n'
                'print("compare by key, then report each kind of change")\n'
            ),
            variant_b='normalise quantities to integers before comparing and note which rows still differ',
            variant_c='add a count per category and print a one-line summary next to the details',
            mistakes=[
                "Reporting only a total change count, so an operator cannot see what kind of change occurred.",
                "Comparing raw values across formats where one side is text and the other is numeric.",
                "Iterating an unordered set so the summary order changes between runs.",
            ],
            q1=(
                "Why are added, removed and changed keys reported separately?",
                "Each kind of change needs a different reaction, and a single total hides whether rows were lost or merely edited.",
            ),
            homework=(
                "Write `diff(old_rows, new_rows)` that returns added, removed and changed keys, each sorted. "
                "Run it over two small record lists, print each category, and comment which line normalises "
                "values before comparing them."
            ),
            patterns=["def ", "sorted", "print("],
            mapping=(
                "A daily Excel automation should log how many rows were new or corrected, which is what makes "
                "the report auditable rather than just available."
            ),
        ),
        133: dict(
            topic="Testing the file layer",
            idea=(
                "The file layer deserves tests because it is where quiet corruption happens. You do not need a "
                "framework to get most of the value: a small `check(name, condition)` helper that prints PASS or "
                "FAIL and asserts is enough for a lesson and for a smoke test. The highest-value test is a round "
                "trip: write rows to CSV text, read them back, and compare. That catches quoting bugs, newline "
                "mistakes, and accidental type conversions in one assertion. Add a test for a value containing "
                "the delimiter, a test for empty input, and a test for the header-only case. Each test should "
                "build its own input as a literal string and should not depend on another test having run. If a "
                "test needs a real file later, use a temporary directory, but keep the pure text tests as the "
                "core because they are fast and deterministic. Name tests after the behaviour they protect, not "
                "after the function they call, so a failure message describes the promise that broke. Today you "
                "write four checks against small in-memory inputs, print each result, and assert that all of "
                "them pass. The point is not coverage; it is that a change to the parser cannot silently break "
                "the writer."
            ),
            code=(
                'import csv\n'
                'import io\n'
                '\n'
                'def write_rows(rows):\n'
                '    buffer = io.StringIO()\n'
                '    writer = csv.writer(buffer, lineterminator="\\n")\n'
                '    writer.writerows(rows)\n'
                '    return buffer.getvalue()\n'
                '\n'
                'def read_rows(text):\n'
                '    return list(csv.reader(io.StringIO(text)))\n'
                '\n'
                'def check(name, condition):\n'
                '    print(("PASS " if condition else "FAIL ") + name)\n'
                '    assert condition\n'
                '\n'
                'check("round trip keeps values", read_rows(write_rows([["a", 1]])) == [["a", "1"]])\n'
                'check("embedded comma survives", read_rows(write_rows([["a", "x,y"]]))[0][1] == "x,y")\n'
                'check("empty input is empty list", read_rows("") == [])\n'
                'print("three checks, no framework needed")\n'
            ),
            variant_b='add a header-only report check and confirm it still has one row',
            variant_c='make check collect failures instead of asserting, so all problems print at once',
            mistakes=[
                "Testing only the happy path, so quoting and newline bugs reach production.",
                "Reusing mutable data between tests, so one test changes another's input.",
                "Naming tests after functions instead of the behaviour they guarantee.",
            ],
            q1=(
                "Why is a write-then-read round trip the highest-value file layer test?",
                "It exercises serialisation and parsing together, catching quoting, newline and type mistakes in one assertion.",
            ),
            homework=(
                "Write `check(name, condition)` and use it to test a CSV round trip, a quoted delimiter, and "
                "empty input. Print one line per check, assert all pass, and comment which check would fail "
                "first if quoting broke."
            ),
            patterns=["def ", "assert", "print("],
            mapping=(
                "Before scheduling an Excel import, these same checks prove that the generated CSV still "
                "parses and still preserves values."
            ),
        ),
        134: dict(
            topic="Review: files and formats checklist",
            idea=(
                "The review day is a checklist you can run, not a list you read. By now the file layer has a "
                "small set of invariants: delimiters are detected or declared, encodings are explicit and BOMs "
                "are stripped from header keys, rows survive a write-and-read round trip, missing values have a "
                "defined representation, and output names are dated and unique. Turn each invariant into a check "
                "over a tiny in-memory sample and print one line per item. A checklist earns its keep when it is "
                "executable, because a passing checklist before a batch run is stronger evidence than a memory "
                "of having done this before. It also gives you a template for the next phase: when the inputs "
                "change, the checks stay, and the failures tell you which assumption the new data broke. Keep the "
                "checks independent and keep the samples tiny, so a failure points at one rule. Two habits are "
                "worth carrying forward. First, always print or log the checklist result next to the output "
                "filename. Second, when a real run fails, add the smallest check that would have caught it. Today "
                "you run four checks over sample text and print a compact summary. The checklist is the "
                "deliverable."
            ),
            code=(
                'import csv\n'
                'import io\n'
                'import json\n'
                '\n'
                'def parse_csv(text):\n'
                '    return list(csv.DictReader(io.StringIO(text)))\n'
                '\n'
                'def no_bom(text):\n'
                '    return not text.startswith("\\ufeff")\n'
                '\n'
                'def parse_json(text):\n'
                '    return json.loads(text)\n'
                '\n'
                'checks = [\n'
                '    ("csv rows parsed", len(parse_csv("a\\n1\\n")) == 1),\n'
                '    ("bom stripped", no_bom("\\ufeffa\\n1\\n".encode("utf-8").decode("utf-8-sig"))),\n'
                '    ("json round trip", parse_json(json.dumps({"a": 1}))["a"] == 1),\n'
                '    ("empty csv is empty", parse_csv("") == []),\n'
                ']\n'
                '\n'
                'for name, passed in checks:\n'
                '    print(("ok  " if passed else "FAIL"), name)\n'
                '\n'
                'assert all(passed for _, passed in checks)\n'
                'print("checklist complete")\n'
            ),
            variant_b='add a delimiter check to the list and keep the summary shape unchanged',
            variant_c='return the list of pairs instead of asserting so a caller can log failures',
            mistakes=[
                "Treating the checklist as prose to read once rather than code to run before every batch.",
                "Combining several rules into one check, so a failure does not identify the broken assumption.",
                "Forgetting to include the BOM and delimiter cases that caused earlier problems.",
            ],
            q1=(
                "Why should the review checklist be executable code?",
                "A passing run before a batch is evidence about this input, while a remembered checklist proves nothing about the current data.",
            ),
            homework=(
                "Write `checklist(samples)` that runs at least four checks over sample strings and returns a "
                "list of (name, passed) pairs. Print each result and the total passed, and comment which check "
                "protects header keys from a BOM."
            ),
            patterns=["def ", "return", "print("],
            mapping=(
                "This is the pre-flight check for a scheduled Excel file import: it confirms formats, "
                "encodings and round trips before the real report is written."
            ),
        ),
    },
)
