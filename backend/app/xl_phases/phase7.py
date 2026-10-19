"""Excel Automation Capstone, days 165-179.

The final phase of the Excel Automation track. Every day is a concrete build or
review step against one small capstone: a monthly sales report that reads CSV
text, cleans it, derives an amount, totals revenue per region and writes a CSV
report. Examples stay stdlib-only, offline and deterministic (CSV in memory, no
openpyxl or pandas, no real file, no clock), so the whole capstone can be
exercised without touching a workbook or the network.
"""

PHASE = (
    "Excel Automation Capstone",
    "Ship one honest monthly sales report: a scoped, cleaned, tested CSV pipeline built a step at a time.",
    {
        165: dict(
            topic="Capstone: choose the scope",
            idea=(
                "The capstone starts with a written brief, not a keyboard. You are building one small but "
                "complete automation: a monthly sales report that reads CSV text, cleans it, totals revenue "
                "per region and writes a CSV report. Scope has two halves. In scope: the reader, the cleaner, "
                "a derived amount column, a per-region total, a CSV writer and an assert-based test. Out of "
                "scope: a live database, charts, email delivery, merging several files and anything that "
                "needs a network or a third-party package. Writing the non-goals down is what keeps a "
                "two-week build shippable. The brief also fixes acceptance criteria before any code exists: "
                "one row per region, revenue rounded to two decimals, the header always present, and the "
                "whole script running offline. A capstone you cannot describe in a handful of deliverables is "
                "a capstone you cannot finish. Sign the brief today by running a small scope script green, "
                "and let it govern every later decision. When a tempting feature appears late, the brief, "
                "not mood, answers whether it belongs. Keep the scope as data other days import, so it is a "
                "deliverable rather than a paragraph you have to remember. A frozen scope is also what makes "
                "the final review on day 178 meaningful, because it gives that review something fixed and "
                "external to check the finished build against."
            ),
            code=(
                '''SCOPE = {
    "name": "monthly sales report",
    "in_scope": ["read CSV text", "clean records", "total revenue per region", "write CSV report"],
    "out_of_scope": ["live database", "charts", "email delivery", "multi-file merge"],
    "acceptance": ["one row per region", "revenue rounded to 2dp", "runs offline on stdlib"],
}
print("capstone:", SCOPE["name"])
for item in SCOPE["in_scope"]:
    print("  in: ", item)
for item in SCOPE["out_of_scope"]:
    print("  out:", item)
for rule in SCOPE["acceptance"]:
    print("  ok: ", rule)
assert "charts" in SCOPE["out_of_scope"]
assert len(SCOPE["in_scope"]) == 4
print("scope frozen:", len(SCOPE["in_scope"]), "deliverables")
'''
            ),
            variant_b="choose a monthly expense report instead and list its four deliverables and non-goals",
            variant_c="add a fifth in-scope item and say which acceptance rule now has to change",
            mistakes=[
                "Starting to code before the scope is written down.",
                "Listing deliverables but never recording the non-goals.",
                "Scoping so much work that no single file could ever finish it.",
            ],
            q1=(
                "Why write the non-goals down instead of only the deliverables?",
                "Exclusions keep the build finite; without them every tempting feature looks in scope and the capstone never ships.",
            ),
            homework=(
                "Write `choose_scope(deliverables, exclusions)` that returns a dict with a name, the in-scope "
                "items and the non-goals. Run it on two candidate capstones, print both briefs, and comment "
                "which line records the exclusions that keep the build finite."
            ),
            patterns=["def choose_scope", "return", "print("],
            mapping=(
                "The brief becomes the acceptance criteria the day-178 review scores against, so scoping is the "
                "first deliverable, not a warm-up."
            ),
        ),
        166: dict(
            topic="Write the report spec",
            idea=(
                "The report spec is the contract for the output, and writing it before the code stops a dozen "
                "small decisions from being made at random. A useful spec is data, not prose: the column names "
                "in order, the key to sort by, the number of decimal places for money, and whether the header "
                "is written even when there are no rows. Fixing decimal places in the spec matters because "
                "floating point totals otherwise print as long tails that look like errors to a human reader. "
                "Fixing the sort key matters because a report whose row order changes between runs is hard to "
                "diff and hard to trust. In this capstone the spec says three columns, region then orders then "
                "revenue, sorted alphabetically by region, money to two decimals, header always present. Every "
                "later day reads this spec instead of hard-coding a column list, so changing the output means "
                "changing one dictionary. Today you write the spec as data and a small formatter that renders a "
                "revenue value according to it. Notice the formatter is trivially testable: you can assert an "
                "exact string without touching any real data, which is the whole point of deciding format "
                "before content. Pin the spec down once and every later argument about how the report looks "
                "becomes a small edit to one dictionary rather than a debate."
            ),
            code=(
                '''SPEC = {
    "columns": ["region", "orders", "revenue"],
    "sort_by": "region",
    "decimals": 2,
    "always_header": True,
}

def money(value, spec):
    return f"{value:.{spec['decimals']}f}"

def spec_row(spec):
    return " | ".join(spec["columns"])

print("report spec:")
print("  columns:", spec_row(SPEC))
print("  sort by:", SPEC["sort_by"])
print("  money:  ", money(16.5, SPEC), money(5.0, SPEC))
assert money(16.4999, SPEC) == "16.50"
assert SPEC["columns"][0] == "region"
print("spec fixes columns, order and precision before any data is read")
'''
            ),
            variant_b="change decimals to 0 and 3 and print the same value under each to see the difference",
            variant_c="add a fourth column `avg_order` to the spec and update spec_row to render it",
            mistakes=[
                "Formatting money inside the aggregation instead of from one spec value.",
                "Letting the report's row order depend on dictionary insertion order.",
                "Rounding only sometimes, so the file shows inconsistent decimal places.",
            ],
            q1=(
                "Why keep decimals and sort order in the spec rather than in the writer?",
                "One dictionary then governs every part of the output, so the format cannot drift between the numbers and the file.",
            ),
            homework=(
                "Write `report_spec(columns, sort_by, decimals)` that returns a spec dict and a `money(value, "
                "spec)` formatter. Print a rendered row for two values and comment which line keeps the decimal "
                "places driven by the spec and not the caller."
            ),
            patterns=["def report_spec", "def money", "print("],
            mapping=(
                "In a real workbook the spec maps onto the column headers and number formats you would set once "
                "on a template sheet instead of per cell."
            ),
        ),
        167: dict(
            topic="Define the input contract",
            idea=(
                "The input contract says what a valid source file looks like before you read a single row. For "
                "the sales CSV the contract is four required columns, region, rep, units and price, of which "
                "units and price must parse as numbers and neither may be blank. Checking the header against "
                "the contract up front turns a confusing crash halfway through a run into one clear message at "
                "the start: which columns are missing. The same contract documents the assumptions the cleaner "
                "will rely on, so the two days agree about what a well-formed record is. There is a design "
                "choice worth naming: validate the shape once, then trust it downstream, rather than sprinkling "
                "defensive checks through every function. That keeps the reader small and puts the one honest "
                "error message where a human can act on it. It also makes a bad file fail fast, before any "
                "partial report has been written. Today you write a checker that returns the missing required "
                "columns for a given header, and assert that a good header yields nothing missing while a "
                "truncated header names exactly what is gone. Notice the checker describes a contract; it does "
                "not repair the file, because silently inventing a missing column is how reports start lying."
            ),
            code=(
                '''CONTRACT = {
    "required": ["region", "rep", "units", "price"],
    "numeric": ["units", "price"],
}

def check_header(header, contract):
    return [column for column in contract["required"] if column not in header]

good = ["region", "rep", "units", "price"]
truncated = ["region", "rep"]
print("good header missing:", check_header(good, CONTRACT))
print("truncated missing:  ", check_header(truncated, CONTRACT))
assert check_header(good, CONTRACT) == []
assert check_header(truncated, CONTRACT) == ["units", "price"]
print("contract checked before a single row is read")
'''
            ),
            variant_b="require a fifth column, date, and show which header now fails the check",
            variant_c="add a check that rejects a header with unexpected extra columns and print the extras",
            mistakes=[
                "Discovering a missing column only when a later line raises a KeyError.",
                "Silently supplying a default for a column the contract demands.",
                "Validating required columns inside every function instead of once at the boundary.",
            ],
            q1=(
                "Why validate the header once at the boundary instead of checking columns in every function?",
                "Failing fast with one clear message keeps the rest of the code simple and stops a bad file from producing a partial report.",
            ),
            homework=(
                "Write `check_contract(header, contract)` that returns the required columns absent from the "
                "header and the numeric columns present. Run it on a good header and a truncated one, print both "
                "results, and comment which line fails the file fast at the boundary."
            ),
            patterns=["def check_contract", "return", "print("],
            mapping=(
                "This is the same guard as asserting a sheet has the expected headers before openpyxl reads "
                "values by name; the check is cheap and the failure is early."
            ),
        ),
        168: dict(
            topic="Build the reader",
            idea=(
                "The reader is thin on purpose. It parses CSV text into a list of header-keyed records and does "
                "nothing else, because every decision about meaning belongs to the cleaner and the transforms. "
                "Using `csv.DictReader` over `io.StringIO` gives you the same API you would use on a real file "
                "while staying offline and deterministic, and it correctly handles quoting and embedded commas "
                "that a hand-rolled split would misread. One discipline matters more than the code: keep every "
                "value as a string on read. Converting to numbers here would be tempting and wrong, because a "
                "postal code or account number should stay text even when it looks numeric, and because a "
                "single unparseable cell would then abort the whole read. The string-in, string-out rule is "
                "what lets the cleaner decide, deliberately, what to do with a bad value. Today you write the "
                "reader and assert two things: that the first record is what you expect, and that every value "
                "in every record is still text. That second assertion is the reader's contract with the rest of "
                "the pipeline, and it stays true for the rest of the capstone. Keeping the reader this small "
                "and dumb has a second benefit: the one place that touches raw text is the one place you have "
                "to review when the source format changes."
            ),
            code=(
                '''import csv
import io

RAW = "region,rep,units,price\\nnorth,ada,3,2.50\\nnorth,bob,1,9.00\\nsouth,cy,4,1.25\\n"

def read_csv(text):
    return [dict(row) for row in csv.DictReader(io.StringIO(text))]

records = read_csv(RAW)
for record in records:
    print(record["region"], record["rep"], record["units"], record["price"])

assert records[0] == {"region": "north", "rep": "ada", "units": "3", "price": "2.50"}
assert all(isinstance(value, str) for record in records for value in record.values())
print("read", len(records), "records, every value still text")
'''
            ),
            variant_b='parse a semicolon-separated export by passing delimiter=";" to DictReader',
            variant_c="read a header-only file and assert the result is an empty list, not an error",
            mistakes=[
                "Converting values to numbers on read, so one bad cell aborts the whole file.",
                "Splitting lines on commas by hand and breaking on quoted fields.",
                "Treating the header row as a data record by iterating over raw rows.",
            ],
            q1=(
                "Why keep every value as a string when reading the CSV?",
                "Text preserves codes and partial values, and it lets the cleaner decide deliberately what to convert instead of failing during the read.",
            ),
            homework=(
                "Write `read_csv(text)` that returns a list of dicts using `csv.DictReader` over `io.StringIO`. "
                "Parse a four-column, three-row string, print each record, and comment which line keeps every "
                "value as text on purpose."
            ),
            patterns=["def read_csv", "DictReader", "print("],
            mapping=(
                "This is the front door of every Excel automation: a CSV export, a copied range or a "
                "tab-separated dump all arrive as text and become records here."
            ),
        ),
        169: dict(
            topic="Build the cleaner",
            idea=(
                "The cleaner makes records trustworthy by applying fixed, testable rules in a deliberate order. "
                "First normalise the keys, trimming and lowercasing them, so `Region` and ` region ` become the "
                "same field. Then normalise the values, stripping stray whitespace. Only then decide which "
                "records to keep, by checking that every required field has content. Order matters: "
                "deduplicating or filtering before trimming keeps rows that differ only by whitespace, and "
                "normalising values before keys means the two rules fight each other. Cleaning never drops "
                "information silently; when a required field is blank the honest move is to exclude the record "
                "and count it, not to invent a value. That count is what lets a later report say credibly how "
                "many rows were left out. In this capstone the cleaner keeps any record whose region, rep, "
                "units and price are all non-empty after trimming, and it returns both the survivors and the "
                "number dropped. Making each rule a small pure function over one record means you can assert "
                "the output exactly, which is far easier than testing the report as a whole. Return the dropped "
                "count alongside the survivors, because a cleaner that discards rows without tallying them has "
                "already started hiding problems from whoever reads the final report."
            ),
            code=(
                '''def clean(records, required):
    kept, dropped = [], 0
    for record in records:
        row = {key.strip().lower(): value.strip() for key, value in record.items()}
        if all(row.get(field) for field in required):
            kept.append(row)
        else:
            dropped += 1
    return kept, dropped

raw = [
    {"Region": " North ", "Rep": "Ada", "Units": "3", "Price": "2.50"},
    {"Region": "", "Rep": "Bo", "Units": "1", "Price": "1.00"},
    {"region": "south", "rep": "Cy", "units": "4", "price": "1.25"},
]
kept, dropped = clean(raw, ["region", "rep", "units", "price"])
for record in kept:
    print("kept:", record["region"], record["rep"], record["units"], record["price"])
print("dropped:", dropped)
assert len(kept) == 2 and dropped == 1
assert kept[0]["region"] == "North"
print("cleaned keys and values, then filtered, never inventing a value")
'''
            ),
            variant_b='add a rule that lowercases the rep name so "Ada" and "ada" compare equal',
            variant_c="remove duplicate records after cleaning and print how many extra rows were dropped",
            mistakes=[
                "Filtering before trimming, so rows differing only by whitespace both survive.",
                "Filling a blank required field with a default instead of excluding the record.",
                "Normalising values in one function and keys in another, so the order is unclear.",
            ],
            q1=(
                "Why clean and strip before deciding which records to keep?",
                "Otherwise a record that is blank only because of stray whitespace is kept, and duplicates that differ by spacing slip through.",
            ),
            homework=(
                "Write `clean(records, required)` that trims and lowercases keys, strips values, and returns the "
                "kept records plus the dropped count. Run it on three records including one blank, print the "
                "survivors and the count, and comment which line decides what a valid record is."
            ),
            patterns=["def clean", "return", "print("],
            mapping=(
                "This is pandas `str.strip` and `dropna` done with plain data, keeping the rules visible and "
                "unit-testable before any dependency is involved."
            ),
        ),
        170: dict(
            topic="Build the transforms",
            idea=(
                "A transform derives new fields from existing ones, and the discipline is to make it pure: it "
                "returns a new record and never mutates the one it was handed. Here the transform turns units "
                "and price into an amount, parsing the strings the reader preserved and rounding to two "
                "decimals so cents stay exact. Rounding at the point of derivation, not at the point of "
                "printing, is deliberate: it means every downstream total is built from the same money values "
                "that will appear in the report, so the numbers cannot disagree with the file. There is one "
                "tempting shortcut to avoid here, and it is the theme of today: doing the conversion and the "
                "multiplication and the rounding inside the grouping loop. That works once and then becomes "
                "impossible to test alone, and it hides the place where a bad value would blow up. Keep the "
                "transform separate so you can feed it one record and assert the amount, including a record "
                "with an awkward value. The transform also leaves the source record intact, which means the raw "
                "data stays available for the edge-case handling on day 174. Pure input, pure output, one job; "
                "the smaller the transform the easier it is to assert on a value you worked out by hand."
            ),
            code=(
                '''def add_amount(record):
    row = dict(record)
    row["amount"] = round(int(row["units"]) * float(row["price"]), 2)
    return row

records = [
    {"region": "north", "units": "3", "price": "2.50"},
    {"region": "south", "units": "4", "price": "1.25"},
]
priced = [add_amount(record) for record in records]
for record in priced:
    print(record["region"], record["units"], record["price"], "->", record["amount"])

assert priced[0]["amount"] == 7.5
assert priced[1]["amount"] == 5.0
assert "amount" not in records[0]
print("transform derives amount and leaves the source record untouched")
'''
            ),
            variant_b="derive the amount without rounding and print the unrounded float to see the tail",
            variant_c="add a `rounded` field that rounds to whole units and print both amounts side by side",
            mistakes=[
                "Mutating the source record in place instead of returning a new one.",
                "Doing the conversion inside the grouping loop, so the transform cannot be tested alone.",
                "Rounding only at print time, so totals and rows can disagree.",
            ],
            q1=(
                "Why return a new record from the transform instead of editing the original?",
                "Keeping the source intact makes the step pure and testable, and leaves the raw values available for edge-case handling later.",
            ),
            homework=(
                "Write `add_amount(record)` that returns a new dict with an `amount` field equal to units times "
                "price, rounded to two decimals. Run it on two records, print each result, and comment which "
                "line leaves the original record unchanged."
            ),
            patterns=["def add_amount", "return", "print("],
            mapping=(
                "This is a calculated column in Excel, except the formula lives in code where you can assert it "
                "on awkward values before it ever reaches a sheet."
            ),
        ),
        171: dict(
            topic="Build the aggregations",
            idea=(
                "Aggregation turns many records into few: a count of orders and a sum of revenue per region. "
                "The reliable pattern is a fold into a dictionary keyed by the group, with a fresh bucket "
                "created the first time a group appears. `setdefault` is the idiomatic way to create that "
                "bucket, and using it once per record avoids the classic bug of a shared mutable default that "
                "quietly collects every group's rows. Two distinctions matter for honesty. Counting rows is "
                "not the same as counting distinct things, and a report that conflates orders with customers "
                "is wrong in a way nobody notices until the numbers are questioned. And a missing group must "
                "appear as a real row rather than being dropped, because an omitted region looks like a "
                "region that had no sales. Today you write the group-by and print one line per region, sorted "
                "so the output is stable between runs. This small report, one row per group with a count and "
                "a total, is the core of almost every spreadsheet automation. Build it here against a "
                "handful of records you can verify by hand, then trust it on the real file. Because the same "
                "loop works for any grouping key, swapping region for rep or month costs one argument, not a "
                "new function."
            ),
            code=(
                '''def group_report(records, key_field, value_field):
    totals = {}
    for record in records:
        bucket = totals.setdefault(record[key_field], {"orders": 0, "revenue": 0.0})
        bucket["orders"] += 1
        bucket["revenue"] += record[value_field]
    return totals

records = [
    {"region": "north", "amount": 7.5},
    {"region": "north", "amount": 9.0},
    {"region": "south", "amount": 5.0},
]
report = group_report(records, "region", "amount")
for region in sorted(report):
    bucket = report[region]
    print(f"{region:6} orders={bucket['orders']} revenue={bucket['revenue']:.2f}")

assert report["north"] == {"orders": 2, "revenue": 16.5}
assert report["south"]["orders"] == 1
print("folded records into per-region counts and totals")
'''
            ),
            variant_b='add an "avg" field computed as revenue / orders and print it for each region',
            variant_c="count distinct reps per region as well as rows, and print both counts side by side",
            mistakes=[
                "Using a shared mutable default bucket, so all groups accumulate into one.",
                "Confusing the number of rows with the number of distinct items in a group.",
                "Dropping a group with an odd name instead of reporting it honestly.",
            ],
            q1=(
                "Why create a fresh bucket with setdefault for each new group?",
                "A shared default bucket would collect every group's rows into one and silently corrupt the totals.",
            ),
            homework=(
                "Write `group_report(records, key_field, value_field)` returning per-group dicts with orders "
                "and revenue. Run it over four records across two groups, print each group sorted by name, and "
                "comment which line creates a fresh bucket for a new group."
            ),
            patterns=["def group_report", "setdefault", "print("],
            mapping=(
                "This is a pivot table in miniature; pandas `groupby` and an Excel PivotTable compute exactly "
                "the same count-and-sum for larger data."
            ),
        ),
        172: dict(
            topic="Write the report",
            idea=(
                "Writing the report is a separate concern from computing the numbers, and treating it that way "
                "is what lets you test the report without opening a spreadsheet. Build the rows as data first, "
                "a header plus a list of rows, and then have one thin function serialise that structure to CSV "
                "text. The same structure maps directly onto an openpyxl worksheet later, so the split survives "
                "a change of writer. Two details make the output trustworthy. Always write the header, even for "
                "an empty report, so a downstream reader does not mistake a headerless file for garbage. And "
                "apply the spec's formatting, so the file cannot disagree with what your tests checked. The "
                "serialiser itself should be boring: a StringIO buffer and a csv.writer, nothing clever. All "
                "the thinking already happened in the spec, the cleaner and the aggregation. If the writer "
                "looks complicated, it means logic has leaked into the wrong layer. Today you take report rows "
                "and turn them into exact CSV text, then assert the header line and one data line so the output "
                "format is pinned down precisely. A writer this small is a feature, not an absence of one: it "
                "means every remaining doubt about the output belongs to the spec rather than to this "
                "function."
            ),
            code=(
                '''import csv
import io

def report_to_csv(header, rows):
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(header)
    writer.writerows(rows)
    return buffer.getvalue()

header = ["region", "orders", "revenue"]
rows = [["north", 2, "16.50"], ["south", 1, "5.00"]]
text = report_to_csv(header, rows)
print(text, end="")

assert text.splitlines()[0] == "region,orders,revenue"
assert "north,2,16.50" in text
print("report built as rows, serialised last")
'''
            ),
            variant_b="write an empty report, header only, and assert the header line is still present",
            variant_c="drop the header and print the result to see what a downstream reader would lose",
            mistakes=[
                "Building CSV text by string concatenation while still computing the numbers.",
                "Omitting the header on an empty report, leaving a file with no columns.",
                "Writing raw float totals so the file shows long floating point tails.",
            ],
            q1=(
                "Why build the report rows as data before serialising to CSV text?",
                "The report can then be tested as a structure, and the writer stays a trivial serialiser that another backend could replace.",
            ),
            homework=(
                "Write `report_to_csv(header, rows)` that returns CSV text with the header always written. Run "
                "it on two data rows and on an empty row list, print both results, and comment which line "
                "guarantees the header is present even when there is no data."
            ),
            patterns=["def report_to_csv", "writerow", "print("],
            mapping=(
                "The rows-plus-header structure maps directly onto an openpyxl worksheet or a pandas frame, so "
                "the report logic outlives a change of writer."
            ),
        ),
        173: dict(
            topic="Write the tests",
            idea=(
                "A test is a small, runnable claim about your code, and an assert-based function is enough for "
                "a capstone. The value of writing it now is that it turns the capstone from something that "
                "happened to work once into something that keeps working when you change the cleaner or the "
                "spec tomorrow. Good tests pick the boundaries: an empty list, a single record, and several "
                "records, because those are the shapes that break folds and joins. They also check the exact "
                "value, not merely that something ran, so asserting an exact total on one record is stronger "
                "than a truthiness check. Keep the test data tiny and obvious so a failure points at the logic "
                "rather than at a mysterious fixture. You do not need a framework; a plain function full of "
                "asserts, called at the bottom of the script, is a real test and it stays offline and "
                "deterministic. Today you write `test_total_revenue` covering empty, single and multiple "
                "records, and run it. Later days run this same test after every change, which is what "
                "makes a confident refactor possible. The empty case is worth its own assertion precisely "
                "because folds most often fail on it, and the several-record case guards against a loop that "
                "quietly drops the first or last element."
            ),
            code=(
                '''def total_revenue(records):
    return round(sum(record["amount"] for record in records), 2)

def test_total_revenue():
    assert total_revenue([]) == 0.0
    assert total_revenue([{"amount": 1.5}]) == 1.5
    assert total_revenue([{"amount": 1.0}, {"amount": 2.0}]) == 3.0
    assert total_revenue([{"amount": 0.1}, {"amount": 0.2}]) == 0.3

test_total_revenue()
print("empty, single and multiple records all pass")
assert total_revenue([{"amount": 5.0}]) == 5.0
print("assert-based tests need no framework")
'''
            ),
            variant_b="add a case with a negative amount and decide whether the total should include it",
            variant_c="split the test into three functions, one per shape, and call each at the bottom",
            mistakes=[
                "Testing only that the code ran, never the exact value it produced.",
                "Using large random fixtures that hide which input caused a failure.",
                "Writing the test after the code is final, so it never catches a real regression.",
            ],
            q1=(
                "Why assert exact values instead of just checking that a function returns something?",
                "An exact expectation catches a wrong total, while a truthiness check passes on almost any non-empty result and hides the bug.",
            ),
            homework=(
                "Write `test_total_revenue()` that asserts a total function over an empty list, one record and "
                "several records. Run it at the bottom of the script, print a line when it passes, and comment "
                "which assertion covers the empty-input boundary."
            ),
            patterns=["def test_total_revenue", "assert", "print("],
            mapping=(
                "These tests are the offline proof that a report is correct; you run them before trusting a "
                "spreadsheet export that no one can inspect by eye."
            ),
        ),
        174: dict(
            topic="Handle the edge cases",
            idea=(
                "Real files contain rows that cannot be converted, and the honest response is to skip and "
                "count them, not to crash and not to hide them. Today you wrap the numeric conversion in a "
                "try/except that catches both a bad value and a missing key, returning a sentinel the caller "
                "can recognise. The key design point is where the failure is isolated: because conversion "
                "happens in one small function, one broken row costs one skipped row rather than the whole "
                "run. That is very different from a bare `float(...)` deep inside the grouping loop, where a "
                "single mistyped cell aborts everything after it. Counting the skips is part of the contract: "
                "a report that says how many rows it excluded is trustworthy, while one that silently drops "
                "them is quietly wrong and cannot be audited. Two other edges belong here too: an empty input "
                "should produce a header-only report rather than an error, and a missing required column "
                "should already have failed fast at the reader. Today you build the safe conversion, skip two "
                "bad rows, and assert the kept and skipped counts, so the report's honesty is itself tested. "
                "When you later write the summary line, that skipped count is the one number that tells a "
                "reader how much of the input actually made it into the total."
            ),
            code=(
                '''def safe_amount(record):
    try:
        return round(int(record["units"]) * float(record["price"]), 2)
    except (ValueError, KeyError):
        return None

records = [
    {"region": "north", "units": "3", "price": "2.50"},
    {"region": "south", "units": "x", "price": "1.25"},
    {"region": "east", "units": "2"},
]
good, skipped = [], 0
for record in records:
    amount = safe_amount(record)
    if amount is None:
        skipped += 1
    else:
        good.append({"region": record["region"], "amount": amount})
print("kept:", len(good), good)
print("skipped:", skipped)

assert good == [{"region": "north", "amount": 7.5}]
assert skipped == 2
print("bad rows are counted, never silently dropped")
'''
            ),
            variant_b="raise the skipped count into the report as a final summary note",
            variant_c="catch only ValueError and watch the missing-key row crash, then add KeyError back",
            mistakes=[
                "Letting one unparseable value abort the whole run instead of skipping it.",
                "Dropping bad rows without counting them, so the report hides missing data.",
                "Catching every exception, including bugs that should surface during development.",
            ],
            q1=(
                "Why count skipped rows rather than dropping them silently?",
                "It keeps the report honest about its inputs, so a reader can tell whether a total is complete or filtered.",
            ),
            homework=(
                "Write `safe_amount(record)` that returns units times price rounded to two decimals, or None "
                "on a bad value or missing key. Run it over three records including two bad ones, print the kept "
                "and skipped counts, and comment which line isolates a failure to one record."
            ),
            patterns=["def safe_amount", "except", "print("],
            mapping=(
                "A spreadsheet full of error cells maps onto these skipped rows; surfacing the count is how a "
                "report stays auditable instead of merely tidy."
            ),
        ),
        175: dict(
            topic="Polish the output",
            idea=(
                "Polishing is where the report becomes something a person would actually read, and it is almost "
                "entirely about consistency. Sort the rows so two runs of the same file produce byte-identical "
                "output, which makes the report diffable and reviewable. Round every money value to the spec's "
                "decimal places so one row does not betray the format. Write the header unconditionally, even "
                "when the totals dictionary is empty. Those three rules sound cosmetic, but each one prevents a "
                "real failure: unstable order breaks diffs and hides changes, mixed precision makes a reader "
                "suspect the arithmetic, and a missing header makes a downstream loader fail. The deeper point "
                "is that polish should come from the spec and one render function, not from hand-editing the "
                "output. If you find yourself special-casing a single row, the rule belongs in the renderer so "
                "it applies everywhere. Today you write a render function that sorts, formats and always "
                "writes the header, and assert the exact text. Notice that the earlier tests still pass "
                "unchanged, which is the sign that polish added no new behaviour, only a stricter shape. Once "
                "the renderer owns these rules, a reviewer can compare two reports line by line and see real "
                "changes instead of noise."
            ),
            code=(
                '''import csv
import io

def render_report(totals, decimals):
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["region", "orders", "revenue"])
    for region in sorted(totals):
        bucket = totals[region]
        writer.writerow([region, bucket["orders"], f"{bucket['revenue']:.{decimals}f}"])
    return buffer.getvalue()

totals = {
    "south": {"orders": 1, "revenue": 5.0},
    "north": {"orders": 2, "revenue": 16.499999},
}
text = render_report(totals, 2)
print(text, end="")

assert text.splitlines()[0] == "region,orders,revenue"
assert "north,2,16.50" in text and "south,1,5.00" in text
assert text.index("north") < text.index("south")
print("sorted, rounded and header always present")
'''
            ),
            variant_b="render an empty totals dict and assert the header is still the only line",
            variant_c="sort by revenue descending instead of region and confirm the totals are unchanged",
            mistakes=[
                "Sorting by insertion order, so the report changes between runs.",
                "Rounding one value by hand, so a single row breaks the format.",
                "Skipping the header when there is no data, leaving an unreadable file.",
            ],
            q1=(
                "Why does stable sort order matter for a report?",
                "It makes two runs byte-identical, so the file can be diffed and reviewed instead of looking different every time.",
            ),
            homework=(
                "Write `render_report(totals, decimals)` that sorts regions, formats revenue to the given "
                "decimals and always writes the header. Run it on two regions and on an empty dict, print both "
                "results, and comment which line keeps the row order stable."
            ),
            patterns=["def render_report", "sorted(", "print("],
            mapping=(
                "This is number formatting and a fixed sort on a real sheet; doing it in the renderer means the "
                "workbook and the CSV never disagree on how money looks."
            ),
        ),
        176: dict(
            topic="Package the script",
            idea=(
                "Packaging is what turns a script that works on your machine into one a colleague can run, and "
                "the minimum version is a small manifest plus a guarded entry point. The manifest names the "
                "script, declares its entry file, states the required Python version, lists its dependencies "
                "(none, for a stdlib-only tool) and gives one usage line. Writing the dependencies list as "
                "explicitly empty is not pedantry: it is a claim the checker can verify, and it advertises that "
                "the tool runs anywhere without an install step. The guarded entry point, the familiar `if "
                "__name__ == \"__main__\"` block, means the module can be imported and tested without also "
                "running the report as a side effect, which is exactly what day 173 relies on. A checker that "
                "walks the manifest and reports problems keeps the package honest as it grows, and it is "
                "trivial to test. Today you write the manifest and the checker and assert that the declared "
                "package is clean. The habit to carry away: a deliverable is not finished until someone other "
                "than you can find, read and run it from its packaging alone. The usage line doubles as "
                "documentation and as a promise about the input and output, so a wrong usage string is a "
                "bug you can review before anyone runs the tool."
            ),
            code=(
                '''MANIFEST = {
    "name": "monthly_report",
    "entry": "report.py",
    "python": ">=3.10",
    "deps": [],
    "usage": "python report.py < sales.csv > report.csv",
}

def check_manifest(manifest):
    problems = []
    if not manifest["entry"].endswith(".py"):
        problems.append("entry must be a python file")
    if manifest["deps"]:
        problems.append("deps must be empty for a stdlib-only tool")
    if manifest["python"] == "":
        problems.append("python version must be declared")
    return problems

print("package:", MANIFEST["name"], "->", MANIFEST["entry"])
print("deps:  ", MANIFEST["deps"])
print("usage: ", MANIFEST["usage"])
print("problems:", check_manifest(MANIFEST))

assert check_manifest(MANIFEST) == []
assert MANIFEST["deps"] == []
print("manifest declares entry, deps and usage; entry point is guarded")
'''
            ),
            variant_b="add a bogus dependency to deps and watch the checker flag the package",
            variant_c='add a "tested" key and have check_manifest require it to be True',
            mistakes=[
                "Shipping without a usage line, so a colleague cannot run the tool.",
                "Pulling in a dependency the manifest never declares.",
                "Running the report at import time, so tests trigger it as a side effect.",
            ],
            q1=(
                "Why declare an explicitly empty dependency list in the manifest?",
                "It is a verifiable claim that the tool is stdlib-only and installs anywhere, and the checker can enforce it.",
            ),
            homework=(
                "Write `check_manifest(manifest)` that returns a list of problems with entry, deps and the "
                "python version declared. Run it on a good manifest and a broken one, print both problem lists, "
                "and comment which line keeps the package honest about its dependencies."
            ),
            patterns=["def check_manifest", "return", "print("],
            mapping=(
                "A real Excel automation ships alongside a README and a requirements file; this manifest is the "
                "same promise in miniature, keeping the tool dependency-free and runnable."
            ),
        ),
        177: dict(
            topic="Build day: performance pass",
            idea=(
                "This build day is a performance pass, and the honest way to measure performance without a "
                "clock is to count operations. On the toy data, the interesting question is how many times you "
                "walk the records: a two-pass version reads the list once to count and again to sum, while a "
                "one-pass version accumulates both in a single loop. Counting the passes and the conversions "
                "gives a deterministic, offline measure of the work, so the lesson holds even though timing is "
                "banned. The real insight is that the same reasoning applies to a spreadsheet whose reads are "
                "expensive: fewer passes over the data means less I/O and less recalculation. The one-pass "
                "fold also converts each record exactly once, which is where a spreadsheet-style tool spends "
                "most of its time. Beware of optimising the wrong thing, though; correctness comes first, and "
                "the day-173 tests must still pass after the change. Today you write both versions, show they "
                "produce identical results, and print the pass and conversion counts so the improvement is "
                "visible and testable rather than a guess. On real workbooks the same reasoning holds at a "
                "larger scale: reading a used range once into memory beats re-reading cells inside every "
                "formula, and the pass count makes that saving something you can point at."
            ),
            code=(
                '''def total_two_pass(records):
    count = len(records)
    revenue = round(sum(record["amount"] for record in records), 2)
    return count, revenue, 2

def total_one_pass(records):
    count = 0
    revenue = 0.0
    for record in records:
        count += 1
        revenue += record["amount"]
    return count, round(revenue, 2), 1

records = [{"amount": float(index)} for index in range(5)]
c2, r2, passes_two = total_two_pass(records)
c1, r1, passes_one = total_one_pass(records)
print("two-pass:", c2, r2, "passes:", passes_two)
print("one-pass:", c1, r1, "passes:", passes_one)

assert (c1, r1) == (c2, r2)
assert passes_one < passes_two
print("same result in fewer passes over the data")
'''
            ),
            variant_b="count conversions instead of passes and show that the one-pass version halves them",
            variant_c="add a 100-record list and print the counts to see the pass saving stay constant",
            mistakes=[
                "Optimising before the correctness tests pass, so the change is unverifiable.",
                "Measuring with a real clock, making the result non-deterministic and hard to trust.",
                "Rewriting the reader for speed when the aggregation was the actual bottleneck.",
            ],
            q1=(
                "Why count passes and conversions instead of timing the run?",
                "Operation counts are deterministic and offline, and for spreadsheet data they predict I/O far better than a noisy wall-clock number.",
            ),
            homework=(
                "Write `total_one_pass(records)` that returns the row count and revenue in a single loop, and "
                "compare it against a two-pass version. Print both results and the pass counts, and comment "
                "which line proves the two versions agree."
            ),
            patterns=["def total_one_pass", "for ", "print("],
            mapping=(
                "Fewer passes over data is the same principle as reading a sheet once into memory rather than "
                "re-reading ranges per formula, which is where large workbooks get slow."
            ),
        ),
        178: dict(
            topic="Build day: final review",
            idea=(
                "Final review is a checklist run against the acceptance criteria you wrote on day 165, and it "
                "must be mechanical rather than a feeling. Each criterion becomes a boolean: does the reader "
                "parse CSV text, does the cleaner flag bad rows, does the aggregation total revenue per region, "
                "does the writer always emit a header, do the tests pass offline. Collecting those booleans in a "
                "dictionary and reporting which failed turns a vague sense of done into a list of concrete "
                "gaps, and the review function is itself testable. The discipline this enforces is that a "
                "capstone is called done against the brief, not against how tired you are. Running the review "
                "should surface at most a small number of failures, because earlier days each closed a gap; if "
                "it surfaces many, that is the honest signal that the brief outran the build. Today you write "
                "the review over an all-true checklist and assert there are no failures. Keep the checklist as "
                "data alongside the scope, so the claim `this shipped` is backed by checks a reader can rerun "
                "rather than by a sentence in a message. If a check fails, that failure is the next task, and "
                "the review is what lets you say precisely which part of the brief is still open."
            ),
            code=(
                '''CHECKS = {
    "reads csv text": True,
    "cleans and flags bad rows": True,
    "groups and totals per region": True,
    "writes csv with a header": True,
    "tests pass offline": True,
}

def review(checks):
    return [name for name, ok in checks.items() if not ok]

print("acceptance review:")
for name, ok in CHECKS.items():
    print(" ", "PASS" if ok else "FAIL", name)

failed = review(CHECKS)
print("failed:", failed)

assert failed == []
assert len(CHECKS) == 5
print("all acceptance checks pass; ready to ship")
'''
            ),
            variant_b="flip the tests check to False and print the failed list the review now reports",
            variant_c='add a sixth check for "handles an empty file" and set it True',
            mistakes=[
                "Declaring the capstone done without checking it against the brief.",
                "Treating a missing acceptance criterion as obvious rather than recording its status.",
                "Reviewing only the happy path and ignoring the edge-case and empty-input checks.",
            ],
            q1=(
                "Why run the review as a checklist against the brief rather than by feel?",
                "A checklist turns done into specific, rerunnable claims, so a gap shows up as a named failure instead of being missed.",
            ),
            homework=(
                "Write `review(checks)` that returns the names of failed checks. Run it on an all-true checklist "
                "and on one with a failure, print both results, and comment which line ties the review back to "
                "the day-165 acceptance criteria."
            ),
            patterns=["def review", "return", "print("],
            mapping=(
                "This is the check a team runs before calling an automation production-ready: each acceptance "
                "criterion either passes or it does not."
            ),
        ),
        179: dict(
            topic="Ship: retrospective and next steps",
            idea=(
                "Shipping is a moment to record what actually got built and what you would do next, because a "
                "capstone you cannot summarise is a capstone you have not understood. The retrospective names "
                "the shipped pieces plainly: reader, cleaner, transform, aggregation, report writer and tests. "
                "Then it lists the next steps honestly, and the good ones are concrete and small: handle "
                "several months in one run, add a summary row, write to a real workbook with openpyxl. Notice "
                "that the next steps point outward from the stdlib core you built, not inward; because the "
                "report was kept as data, swapping the CSV writer for an openpyxl one is an afternoon, not a "
                "rewrite. That is the payoff of every separation this phase insisted on. A retrospective also "
                "names one thing you would change, which keeps it from turning into a victory lap. Today you "
                "summarise the shipped pieces and the next steps as data and assert the summary is complete. "
                "Then you close the loop: the scope from day 165, the checks from day 178 and this summary "
                "together are the record that the automation was built and shipped. That record, more than "
                "the code itself, is what lets someone else pick the project up next week without replaying "
                "the whole fortnight in their head."
            ),
            code=(
                '''SHIPPED = ["reader", "cleaner", "transform", "aggregation", "report writer", "tests"]
NEXT_STEPS = ["handle several months", "add a summary row", "write xlsx with openpyxl"]

def summarise(shipped, next_steps):
    return {"shipped": list(shipped), "next": list(next_steps)}

summary = summarise(SHIPPED, NEXT_STEPS)
print("shipped:")
for item in summary["shipped"]:
    print("  -", item)
print("next:")
for item in summary["next"]:
    print("  -", item)

assert len(summary["shipped"]) == 6
assert "write xlsx with openpyxl" in summary["next"]
print("retrospective recorded; capstone shipped")
'''
            ),
            variant_b="add a `would_change` field naming one part you would rewrite and print it",
            variant_c="promote the xlsx next step into the shipped list and note what it would require",
            mistakes=[
                "Blaming the tools instead of naming a concrete thing you would change.",
                "Listing vague next steps like 'make it better' that no one can start.",
                "Claiming results the day-178 review did not actually verify.",
            ],
            q1=(
                "Why do the next steps point outward from the stdlib core you built?",
                "Because the report was kept as data, adding a real workbook writer later swaps one end of the pipeline instead of rewriting it.",
            ),
            homework=(
                "Write `summarise(shipped, next_steps)` that returns a dict with both lists. Run it on the "
                "capstone's six shipped pieces and three next steps, print both lists, and comment which line "
                "keeps the record of what shipped separate from what comes next."
            ),
            patterns=["def summarise", "return", "print("],
            mapping=(
                "A real automation handover ends with a short note of what runs, what is next and what to "
                "change; this summary is that note, backed by the tests and review you wrote."
            ),
        ),
    },
)
