"""Excel Automation foundations, days 9-14: spreadsheets as data you can automate.

Every example is stdlib-only, offline and deterministic (CSV in memory, no
openpyxl or pandas install, no real workbook on disk), so the applier can
execute it and produce the same output on every run. The domain phases keep the
same discipline: a sheet is a list of rows, a row is a dict keyed by header, and
a report is a small transform over those rows.
"""

FOUNDATION = {
    9: dict(
        topic="A sheet is rows of data",
        idea=(
            "Spreadsheet automation gets much easier once you stop thinking in cells and start thinking in rows. "
            "A worksheet is a header row plus records, and each record is a row whose values are addressed by "
            "column name rather than by letter. That shift matters because code that says `row[\"total\"]` still "
            "works after someone inserts a column, while code that says `cell C7` breaks the moment the layout "
            "moves. It also matches how every library hands you data: openpyxl reads rows, pandas gives you "
            "columns, and a CSV reader yields lists. Today you represent a small sheet as a list of rows with a "
            "header, and write two helpers: one to find a column index by name, and one to read a field from a "
            "row. The important habit is to separate the layout (where things are) from the logic (what you do "
            "with them), so the layout can change without touching the rules. This is the same decoupling you "
            "already know from databases and APIs, applied to the least formal data store most offices have."
        ),
        code=(
            'SHEET = [\n'
            '    ["item", "qty", "price"],\n'
            '    ["widget", "3", "2.50"],\n'
            '    ["gizmo", "1", "9.00"],\n'
            ']\n'
            '\n'
            'def column_index(header, name):\n'
            '    return header.index(name)\n'
            '\n'
            'def read(row, header, name):\n'
            '    return row[column_index(header, name)]\n'
            '\n'
            'header, *rows = SHEET\n'
            'for row in rows:\n'
            '    print(read(row, header, "item"), "->", read(row, header, "qty"))\n'
            '\n'
            'assert read(rows[0], header, "price") == "2.50"\n'
            'print("columns are addressed by name, not letter")'
        ),
        variant_b='add a "supplier" column and read it from every row without changing the helpers',
        variant_c='write `row_dict(header, row)` that returns a dict keyed by column name and print all rows',
        mistakes=[
            "Hard-coding column letters, so inserting a column silently shifts which data is read.",
            "Treating the header as just another row when iterating, so it becomes a bogus record.",
            "Duplicating column positions in several places instead of looking them up once.",
        ],
        q1=(
            "Why address columns by header name instead of letter or index?",
            "Names survive column insertions and reordering, and they make the code read like the sheet instead of like the layout.",
        ),
        homework=(
            "Write `to_records(sheet)` that takes a list of rows whose first row is the header and returns a "
            "list of dicts keyed by column name. Build a three-column sheet, print every record, and comment "
            "which line skips the header row."
        ),
        patterns=["def ", "header", "print("],
        mapping=(
            "openpyxl's `ws.iter_rows` and pandas' `read_excel` both surface the header/record shape; keeping "
            "that shape in plain data means your logic is testable without a workbook."
        ),
    ),
    10: dict(
        topic="Read text files as tables",
        idea=(
            "Most automation starts with a file someone else exported. Reading it well means two things: using "
            "the standard `csv` module rather than splitting on commas by hand, and reading into a structure your "
            "logic can consume rather than a blob of text. The `csv` module already handles quoted fields, "
            "embedded commas and configurable delimiters, which manual `split(',')` does not. Reading from an "
            "in-memory string with `io.StringIO` keeps the lesson offline and deterministic while using exactly "
            "the same API you would use on a real file. The other half is shape: read the header once, produce "
            "one dict per data row, and keep values as strings until you deliberately convert them. Converting "
            "too early is a common bug, because a ZIP code or an account number should stay text even though it "
            "looks numeric. Today you parse a small CSV from a string into records and print them. This same "
            "function is the front door of every later phase, whether the source is a CSV export, a copied "
            "worksheet or a tab-separated dump."
        ),
        code=(
            'import csv\n'
            'import io\n'
            '\n'
            'RAW = "item,qty,price\\nwidget,3,2.50\\ngizmo,1,9.00\\n"\n'
            '\n'
            'def read_csv(text):\n'
            '    reader = csv.DictReader(io.StringIO(text))\n'
            '    return [dict(row) for row in reader]\n'
            '\n'
            'records = read_csv(RAW)\n'
            'for record in records:\n'
            '    print(record["item"], record["qty"], record["price"])\n'
            '\n'
            'assert records[0] == {"item": "widget", "qty": "3", "price": "2.50"}\n'
            'assert all(isinstance(v, str) for r in records for v in r.values())\n'
            'print("csv.DictReader gives header-keyed records")'
        ),
        variant_b='read a semicolon-separated string by passing delimiter=";" to DictReader',
        variant_c='read with csv.reader (no header) and build the dicts yourself to see what DictReader adds',
        mistakes=[
            "Splitting lines on commas by hand, so quoted fields containing commas break the parse.",
            "Converting every value to a number on read, losing leading zeros in codes.",
            "Assuming the header exists and forgetting to handle an empty file.",
        ],
        q1=(
            "Why use the csv module instead of splitting each line on commas?",
            "It correctly handles quoting, embedded delimiters and line endings that a naive split misreads.",
        ),
        homework=(
            "Write `read_csv(text)` that returns a list of dicts using `csv.DictReader` over `io.StringIO`. "
            "Parse a two-column, three-row string, print each record, and comment which line keeps every value "
            "as text."
        ),
        patterns=["import csv", "DictReader", "print("],
        mapping=(
            "Exports from Excel, Google Sheets and most reporting tools are CSV; parsing them with the stdlib "
            "is the reliable first step before any openpyxl or pandas work."
        ),
    ),
    11: dict(
        topic="Clean before you compute",
        idea=(
            "Real exports are messy: stray spaces, inconsistent capitalisation, blank cells and duplicate rows. "
            "Cleaning is not busywork; it is the step that makes every later number trustworthy, and it is "
            "easier to test than the report itself. The useful discipline is to make each cleaning rule a small "
            "pure function over a record, so you can apply them in a fixed order and assert the result. Usually "
            "the order is: normalise the keys (headers), normalise the values (trim and case), then handle "
            "blanks, then deduplicate. Doing it in a different order can hide problems — for example, removing "
            "duplicates before trimming keeps rows that only differ by whitespace. Today you write three "
            "cleaning helpers and pipe a small set of records through them, printing before and after. Notice "
            "that cleaning never drops information silently; when a required field is blank, the honest move is "
            "to flag the record, not to invent a value. That flag becomes the reconciliation check in later "
            "phases and the reason a report can say, credibly, how many rows were excluded."
        ),
        code=(
            'def clean_keys(record):\n'
            '    return {k.strip().lower(): v for k, v in record.items()}\n'
            '\n'
            'def clean_values(record):\n'
            '    return {k: v.strip() for k, v in record.items()}\n'
            '\n'
            'def drop_blank_keys(record, required):\n'
            '    return all(record.get(key, "").strip() for key in required)\n'
            '\n'
            'rows = [\n'
            '    {"Item": " Widget ", " Qty": "3"},\n'
            '    {"Item": "widget", " Qty": "3"},\n'
            '    {"Item": "", " Qty": "5"},\n'
            ']\n'
            'cleaned = [clean_values(clean_keys(r)) for r in rows]\n'
            'kept = [r for r in cleaned if drop_blank_keys(r, ["item"])]\n'
            '\n'
            'print("kept rows:", kept)\n'
            'assert kept == [\n'
            '    {"item": "Widget", "qty": "3"},\n'
            '    {"item": "widget", "qty": "3"},\n'
            ']\n'
            'print("clean, then filter; never invent a value")'
        ),
        variant_b='add a case-insensitive title-casing rule so "widget" and "Widget" both become "Widget"',
        variant_c='remove duplicate records after cleaning and print how many were dropped',
        mistakes=[
            "Trimming after deduplication, so rows differing only by whitespace both survive as separate records.",
            "Silently replacing blank required values with defaults, hiding incomplete data.",
            "Cleaning headers in one place and values in another, so the rules are impossible to reason about.",
        ],
        q1=(
            "Why clean keys and values before removing duplicates?",
            "Otherwise records that differ only by stray spaces or casing are treated as distinct and survive as false duplicates.",
        ),
        homework=(
            "Write `clean(records, required)` that trims and lowercases keys, strips values, and drops records "
            "with a blank required field. Run three records including one blank, print the survivors, and "
            "comment which line decides what a valid record is."
        ),
        patterns=["def ", "strip", "print("],
        mapping=(
            "pandas users call this `str.strip` and `dropna`; the same work in plain Python keeps the rules "
            "visible and unit-testable before any dependency is involved."
        ),
    ),
    12: dict(
        topic="Group, sum and report",
        idea=(
            "The reason anyone automates a spreadsheet is to turn rows into a summary: totals per category, "
            "counts per month, averages per region. The reliable pattern is a fold over the records into a "
            "dictionary keyed by the group, accumulating totals, and then formatting the result. Doing it with "
            "plain dicts keeps the logic obvious and makes it easy to add a second metric, filter a group, or "
            "sort the output. A subtle but important point is the distinction between counting rows and counting "
            "distinct things; both use the same loop but mean different things in a report, and mixing them is "
            "how a total quietly becomes wrong. Another is numeric conversion: values arrive as strings, so you "
            "convert once, deliberately, and decide what to do with a value that will not convert rather than "
            "crashing the whole run. Today you build a group-by function that sums a numeric column and counts "
            "rows per group, then print a small report. This report shape — one row per group, a count and a "
            "total — is the core of almost every automation you will write later."
        ),
        code=(
            'def group_sum(records, key_field, value_field):\n'
            '    totals = {}\n'
            '    for record in records:\n'
            '        group = record[key_field]\n'
            '        bucket = totals.setdefault(group, {"rows": 0, "total": 0.0})\n'
            '        bucket["rows"] += 1\n'
            '        bucket["total"] += float(record[value_field])\n'
            '    return totals\n'
            '\n'
            'records = [\n'
            '    {"region": "north", "amount": "10"},\n'
            '    {"region": "north", "amount": "5"},\n'
            '    {"region": "south", "amount": "7"},\n'
            ']\n'
            'report = group_sum(records, "region", "amount")\n'
            'for region in sorted(report):\n'
            '    row = report[region]\n'
            '    print(f"{region:6} rows={row[\'rows\']} total={row[\'total\']:.2f}")\n'
            '\n'
            'assert report["north"] == {"rows": 2, "total": 15.0}\n'
            'print("grouped by key, counted rows, summed values")'
        ),
        variant_b='add an "avg" field computed as total / rows and print it for each region',
        variant_c='count distinct "customer" values per region instead of counting every row, and print both',
        mistakes=[
            "Converting the whole column only if every value parses, so one bad cell aborts the report.",
            "Confusing the row count with the count of distinct items in a group.",
            "Accumulating into a shared mutable default instead of a fresh bucket per group.",
        ],
        q1=(
            "Why keep the row count and the total separately in each group bucket?",
            "They answer different questions, and reports routinely need both a count and a sum of the same group.",
        ),
        homework=(
            "Write `group_report(records, key_field, value_field)` returning per-group dicts with rows, total "
            "and avg. Run it over four records across two groups, print each group sorted by name, and comment "
            "which line creates a fresh bucket for a new group."
        ),
        patterns=["def ", "setdefault", "print("],
        mapping=(
            "This is a pivot table in miniature; pandas `groupby` and Excel PivotTables compute the same thing "
            "for larger data."
        ),
    ),
    13: dict(
        topic="Write a report as data",
        idea=(
            "Producing the output file is a separate concern from computing the numbers, and treating it that "
            "way is what lets you test a report without opening a spreadsheet. Build the report rows as data "
            "first — a header plus a list of rows — and then have one thin function serialise that structure to "
            "CSV text. The same structure can later be written by openpyxl to a real workbook, which is why the "
            "split pays off. Two details make reports trustworthy. Always write the header, even for an empty "
            "report, so a downstream reader does not mistake a headerless file for garbage. And always apply "
            "the same formatting rules you asserted on, so the file cannot disagree with what your tests "
            "checked. Rounding is worth doing deliberately, because floating point totals otherwise print as "
            "long tails that look like errors to a human reader. Today you build a report structure, serialise "
            "it to CSV in memory, and check the exact text. The key idea is that the serialiser is trivial "
            "because all the thinking already happened upstream."
        ),
        code=(
            'import csv\n'
            'import io\n'
            '\n'
            'def to_csv(header, rows):\n'
            '    buffer = io.StringIO()\n'
            '    writer = csv.writer(buffer)\n'
            '    writer.writerow(header)\n'
            '    writer.writerows(rows)\n'
            '    return buffer.getvalue()\n'
            '\n'
            'header = ["region", "rows", "total"]\n'
            'rows = [["north", 2, "15.00"], ["south", 1, "7.00"]]\n'
            'text = to_csv(header, rows)\n'
            'print(text, end="")\n'
            '\n'
            'assert text.splitlines()[0] == "region,rows,total"\n'
            'assert text.endswith("south,1,7.00\\r\\n") or text.endswith("south,1,7.00\\n")\n'
            'print("report rows first, serialisation last")'
        ),
        variant_b='write an empty report (header only) and assert the header line is still present',
        variant_c='format totals with f"{value:.2f}" before writing and show the difference in the output text',
        mistakes=[
            "Interleaving computation with string concatenation, so the report cannot be tested as data.",
            "Skipping the header on an empty report, leaving a file with no columns.",
            "Leaving raw float totals unrounded, so the file shows long floating point tails.",
        ],
        q1=(
            "Why build the report rows as data before writing CSV text?",
            "Then the report can be tested as a structure, and the writer stays a trivial serialiser that a different backend could replace.",
        ),
        homework=(
            "Write `report_to_csv(records, key_field, value_field)` that groups records, rounds totals to two "
            "decimals, and returns CSV text with a header. Run it on a small record list, print the text, and "
            "comment which line guarantees the header is always written."
        ),
        patterns=["def ", "writerow", "return"],
        mapping=(
            "The same rows-plus-header structure maps directly onto an openpyxl worksheet or a pandas frame, so "
            "the report logic survives a change of writer."
        ),
    ),
    14: dict(
        topic="A tiny automation, end to end",
        idea=(
            "Today you connect the pieces: read a CSV from text, clean the records, group and total them, build "
            "report rows, and serialise the result back to CSV. It is the whole pipeline in one small script, "
            "and it runs nowhere near a spreadsheet program or a real file, which means it is fast, "
            "deterministic and testable. Notice the seams: reading produces records, cleaning produces "
            "trustworthy records, grouping produces numbers, reporting produces rows, serialising produces "
            "text. Each seam is a value you can print and assert on, and a failure at any seam is easy to "
            "localise because you can inspect what came out of the step before. That is the practical payoff of "
            "the whole foundation week. The script also makes an honest choice about bad data: a row whose "
            "amount will not convert is skipped and counted, so the report can state how many rows were "
            "excluded rather than quietly changing the total. Carry that habit forward; in the domain phases the "
            "inputs get bigger and the sources messier, but the shape of the solution stays exactly this."
        ),
        code=(
            'import csv\n'
            'import io\n'
            '\n'
            'RAW = "region,amount\\nnorth,10\\nnorth,5\\nsouth,7\\nbroken,x\\n"\n'
            '\n'
            'def pipeline(text):\n'
            '    records = [dict(r) for r in csv.DictReader(io.StringIO(text))]\n'
            '    totals = {}\n'
            '    skipped = 0\n'
            '    for record in records:\n'
            '        try:\n'
            '            amount = float(record["amount"])\n'
            '        except ValueError:\n'
            '            skipped += 1\n'
            '            continue\n'
            '        bucket = totals.setdefault(record["region"], {"rows": 0, "total": 0.0})\n'
            '        bucket["rows"] += 1\n'
            '        bucket["total"] += amount\n'
            '    rows = [[region, data["rows"], f"{data[\'total\']:.2f}"] for region, data in sorted(totals.items())]\n'
            '    buffer = io.StringIO()\n'
            '    writer = csv.writer(buffer)\n'
            '    writer.writerow(["region", "rows", "total"])\n'
            '    writer.writerows(rows)\n'
            '    return buffer.getvalue(), skipped\n'
            '\n'
            'text, skipped = pipeline(RAW)\n'
            'print(text, end="")\n'
            'print("skipped rows:", skipped)\n'
            'assert "north,2,15.00" in text and skipped == 1'
        ),
        variant_b='raise the skipped count into the report as a final summary row',
        variant_c='sort groups by total descending and confirm the order changes but the totals do not',
        mistakes=[
            "Letting one unparseable value abort the whole run instead of skipping and counting it.",
            "Mixing report computation and file writing so neither can be tested in isolation.",
            "Forgetting to record how many rows were excluded, so the report hides missing data.",
        ],
        q1=(
            "Why count and report skipped rows rather than silently dropping them?",
            "It keeps the report honest about its inputs, so a reader can tell whether a number is complete or filtered.",
        ),
        homework=(
            "Write `pipeline(text)` that reads CSV text, skips unparseable amounts while counting them, groups "
            "the rest, and returns CSV report text plus the skipped count. Run it on input with one bad row, "
            "print both results, and comment which line isolates the failure to a single record."
        ),
        patterns=["def ", "return", "print("],
        mapping=(
            "This read-clean-group-write pipeline is exactly what a scheduled Excel automation does; swapping "
            "the CSV reader and writer for openpyxl changes only the ends."
        ),
    ),
}
