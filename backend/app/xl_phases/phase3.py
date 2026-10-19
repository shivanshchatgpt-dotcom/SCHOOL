"""Excel Automation phase 3, days 105-119: aggregation and reports.

Same discipline as the foundation arc: every example is stdlib-only, offline and
deterministic. Records are plain dicts, a report is a small transform over those
records, and statistics are computed on ordinary sorted lists rather than numpy.
The phase walks from raw rows to grouped summaries, then shows that the shapes
built here are the shapes PivotTables and pandas groupby hand back.
"""

PHASE = (
    "Aggregation and Reports",
    "Collapse flat rows into grouped, checked summaries by hand, then recognise the same shapes in PivotTables and pandas groupby.",
    {
        105: dict(
            topic="Orientation: from rows to reports",
            idea=(
                "A report is just a list of rows that someone has agreed to look at differently. The raw sheet "
                "holds one row per transaction, but the reader wants one line per region, per month or per "
                "product, and the whole job of aggregation is to collapse many rows into a few meaningful ones. "
                "This week you build the machinery for that collapse, one idea at a time, using nothing but "
                "dictionaries and loops over in-memory records. The mental shift is to stop asking where a number "
                "lives in the grid and start asking which rows contribute to it; once the contributing set is "
                "clear, the sum, the count and the average all fall out of the same loop. You also learn to keep "
                "the two stages apart: first group the records, then compute the metric on each group, because "
                "mixing the two is what makes report code hard to change. Finally you build the habit of making "
                "the report a piece of data you can print and assert on, so a wrong total is a failing line "
                "rather than a spot you have to eyeball in a workbook. Everything here maps directly onto Excel's "
                "PivotTable and onto pandas groupby, so what you build by hand is the same shape those tools "
                "hand back to you."
            ),
            code="""RECORDS = [
    {"region": "north", "amount": "10"},
    {"region": "north", "amount": "5"},
    {"region": "south", "amount": "7"},
]

def summarize(records):
    report = {}
    for record in records:
        bucket = report.setdefault(record["region"], 0.0)
        report[record["region"]] = bucket + float(record["amount"])
    return report

report = summarize(RECORDS)
for region in sorted(report):
    print(region, report[region])

assert report["north"] == 15.0
print("rows in, one line per group out", "groups:", len(report))
""",
            variant_b='add a `count` field per region and print it beside each total',
            variant_c='keep totals as integer cents and divide by 100 only when printing',
            mistakes=[
                "Starting to sum before the groups are fully collected, so a group gets summed twice.",
                "Printing the dict directly and calling the unsorted output a finished report.",
                "Keeping the report as strings throughout, so a later average or share cannot be computed.",
            ],
            q1=(
                "What is the first decision in turning rows into a report?",
                "Deciding which field groups the rows — the key that defines one report line — before any metric is computed.",
            ),
            homework=(
                "Write `group_totals(records, key_field, value_field)` that returns a dict mapping each group to "
                "the sum of its converted numeric values. Run it on five records across two groups, print one line "
                "per group in sorted order, and comment which line creates a new group. Keep every input value as "
                "text and convert only at the moment of summing."
            ),
            patterns=["def ", "sorted", "print("],
            mapping=(
                "This collapse of many rows into one line per group is exactly what an Excel PivotTable does "
                "when you drag a field to Rows and another to Values; pandas groupby produces the same table."
            ),
        ),
        106: dict(
            topic="Grouping with dictionaries",
            idea=(
                "Grouping is the one operation that turns a flat table into a report, and the dictionary is the "
                "simplest tool for it. You pick a key field, walk the records once, and append each record to the "
                "bucket for its key, creating the bucket the first time you see that key. The result is a mapping "
                "from group name to the rows that belong to it, and from there every later metric is a small loop "
                "over a bucket rather than a scan of the whole table. Two habits keep this reliable. First, always "
                "create a fresh bucket per key, because a shared mutable default is the classic way every group "
                "silently ends up holding the same values. Second, normalise the key before grouping, since stray "
                "spaces or inconsistent case split one real group into two that look different to a reader and "
                "inflate the report. Sorting the group names before printing keeps the output stable between runs, "
                "which matters when the report is compared or diffed. This bucket-per-key structure is the ground "
                "floor of every aggregation you write this week, and it is exactly what a PivotTable builds "
                "internally when you drag a field into the Rows area and let it collect the matching rows."
            ),
            code="""RECORDS = [
    {"region": "north", "product": "widget", "amount": "10"},
    {"region": "south", "product": "gizmo", "amount": "7"},
    {"region": "north", "product": "gizmo", "amount": "5"},
    {"region": "south", "product": "widget", "amount": "4"},
]

def group_by(records, key_field):
    groups = {}
    for record in records:
        groups.setdefault(record[key_field], []).append(record)
    return groups

groups = group_by(RECORDS, "region")
for region in sorted(groups):
    print(region, "rows:", len(groups[region]))

assert len(groups["north"]) == 2
print("grouped rows, every record kept intact")
""",
            variant_b='group by product instead of region and compare the bucket sizes',
            variant_c='return a count per group directly instead of keeping the records',
            mistakes=[
                "Appending to one shared list for every key instead of a fresh list per group.",
                "Grouping on values with stray spaces or mixed case, splitting one group into two.",
                "Iterating the groups dict directly, so the report order changes between runs.",
            ],
            q1=(
                "Why keep full records in each bucket rather than only the value being totalled?",
                "Keeping whole records lets the same grouping serve counts, sums, averages and filters without regrouping.",
            ),
            homework=(
                "Write `group_by(records, key_field)` that returns a dict mapping each key to the list of records "
                "in that group, using `setdefault` to create a bucket on first sight. Run it on six records across "
                "three groups, print each group name with its bucket size in sorted order, and comment which line "
                "appends a record to a group."
            ),
            patterns=["def ", "setdefault", "append("],
            mapping=(
                "An Excel PivotTable is a grouping engine with a fixed menu of aggregate functions; grouping into "
                "plain dict buckets lets you attach any later metric, and pandas groupby exposes the same buckets "
                "as group objects."
            ),
        ),
        107: dict(
            topic="Counting and summing",
            idea=(
                "A count and a sum look similar and answer different questions: how many rows are in this group, "
                "and what do their values add up to. Keeping both in the same bucket means one pass over the data "
                "produces the whole report, and it also exposes the distinction between counting rows and summing "
                "a field, which is where honest reports either succeed or quietly go wrong. Values arrive as text "
                "from a spreadsheet export, so conversion has to happen, and the place it happens matters. "
                "Converting inside the loop, per record, lets a single unparseable cell be skipped and counted "
                "while the rest of the report still completes; converting the whole column up front means one bad "
                "cell aborts everything. The count of skipped rows is not a nuisance, it is part of the report, "
                "because a reader needs to know whether a total represents everything or everything that happened "
                "to parse. This is the same trade-off every data pipeline makes, and the same one you meet when a "
                "PivotTable's count disagrees with the sheet because blank or text cells were quietly excluded "
                "from a numeric value field."
            ),
            code="""RECORDS = [
    {"region": "north", "amount": "10"},
    {"region": "north", "amount": "5"},
    {"region": "south", "amount": "7"},
    {"region": "south", "amount": "oops"},
]

def count_and_sum(records, key_field, value_field):
    stats = {}
    skipped = 0
    for record in records:
        bucket = stats.setdefault(record[key_field], {"count": 0, "sum": 0.0})
        try:
            value = float(record[value_field])
        except ValueError:
            skipped += 1
            continue
        bucket["count"] += 1
        bucket["sum"] += value
    return stats, skipped

stats, skipped = count_and_sum(RECORDS, "region", "amount")
for region in sorted(stats):
    row = stats[region]
    print(region, "count:", row["count"], "sum:", row["sum"])
print("skipped:", skipped)

assert stats["north"] == {"count": 2, "sum": 15.0}
print("one pass, two metrics, bad values counted not crashed")
""",
            variant_b='count distinct products per region instead of summing amounts',
            variant_c='skip a group entirely when every one of its values fails to convert',
            mistakes=[
                "Counting every row when the question asked for distinct items.",
                "Letting one unparseable value raise and abort the whole report.",
                "Accumulating into an integer sum and silently truncating the cents.",
            ],
            q1=(
                "Why convert each value inside the loop rather than converting the whole column first?",
                "Per-value conversion lets one bad cell be skipped and counted while the rest of the report still completes.",
            ),
            homework=(
                "Write `count_and_sum(records, key_field, value_field)` returning a per-group dict with `count` "
                "and `sum`, plus the number of rows skipped because a value would not convert. Run it on six "
                "records including one bad amount, print each group sorted by name, and comment which line "
                "isolates the failure to a single record."
            ),
            patterns=["def ", "try:", "sum"],
            mapping=(
                "PivotTables offer Count and Sum of a value field and a separate distinct count; pandas groupby "
                "gives both through `.size()` and `.sum()`, and the skip-and-count habit keeps either one honest."
            ),
        ),
        108: dict(
            topic="Averages, medians and modes",
            idea=(
                "Totals hide the shape of the data; the mean, median and mode reveal it. The mean is the sum "
                "divided by the count and is sensitive to a single large value, the median is the value at the "
                "middle of the sorted list and is not, and the mode is whichever value occurs most often. "
                "Computing them by hand forces two ideas into the open. The first is that the median needs the "
                "values sorted before the middle position means anything, and that an even count has no single "
                "middle, so the median is the average of the two central values. The second is that a mode is not "
                "always unique: when several values tie for most frequent, the honest answer is a list, not an "
                "arbitrary pick. Both details are exactly where hand-rolled statistics go wrong, and both are "
                "visible the moment you print the sorted list beside the result. Excel's AVERAGE, MEDIAN and MODE "
                "functions look like single answers, but underneath they follow the same rules, including the tie "
                "behaviour you are about to implement, so understanding them here makes the spreadsheet functions "
                "predictable rather than magic."
            ),
            code="""VALUES = ["10", "5", "7", "5", "9"]

def summarize(values):
    numbers = sorted(float(value) for value in values)
    count = len(numbers)
    mean = sum(numbers) / count
    middle = count // 2
    if count % 2:
        median = numbers[middle]
    else:
        median = (numbers[middle - 1] + numbers[middle]) / 2
    frequencies = {}
    for number in numbers:
        frequencies[number] = frequencies.get(number, 0) + 1
    top = max(frequencies.values())
    modes = sorted(number for number, seen in frequencies.items() if seen == top)
    return {"mean": mean, "median": median, "mode": modes}

stats = summarize(VALUES)
for key in sorted(stats):
    print(key, stats[key])

assert stats["median"] == 7.0
print("mean, median and mode from one sorted list")
""",
            variant_b='use the statistics module and confirm its mean and median match your versions',
            variant_c='report the median only for odd-sized groups and note the even case explicitly',
            mistakes=[
                "Finding the median by averaging the first and last values of the unsorted list.",
                "Forgetting that an even count has a median equal to the mean of the two middle values.",
                "Reporting a single mode when several values tie for most frequent.",
            ],
            q1=(
                "Why sort the values before finding the median?",
                "The median is defined by position in the ordered list, so sorting is what makes the middle element meaningful.",
            ),
            homework=(
                "Write `describe(values)` that converts strings to floats, sorts them, and returns `mean`, "
                "`median` and `mode`, where mode is a sorted list to allow ties. Run it on a list with an even "
                "count and a tied mode, print each statistic on its own line, and comment which branch handles "
                "the even-length median."
            ),
            patterns=["def ", "sorted", "median"],
            mapping=(
                "Excel's AVERAGE, MEDIAN and MODE functions are these same three computations; doing them on a "
                "sorted Python list shows why MEDIAN needs an ordered column, and pandas describes the same set "
                "in a single call."
            ),
        ),
        109: dict(
            topic="Min, max and percentiles",
            idea=(
                "Min and max are the easiest summaries because they need only an ordered list, but percentiles "
                "are where people guess and get it wrong. A percentile is a position in the sorted data, and "
                "because most positions fall between two values it has to interpolate. The 25th percentile sits a "
                "quarter of the way along the ordered values, the median sits in the middle, and the 90th "
                "percentile sits near the top. Different tools interpolate slightly differently, which is why p50 "
                "and the median agree only when the same definition is used, and why a quartile from one system "
                "can differ by a hair from another. Building the interpolation yourself makes the rule explicit: "
                "find the fractional position, take the lower and upper neighbours, and blend by the fraction "
                "between them. Two guard cases matter — a single value has no neighbours to blend, and a position "
                "at the very end must not index past the list. Once these are right, min, the quartiles, the "
                "median and the interquartile range all fall out of one ordered list, which is the same list a "
                "spreadsheet sorts before it draws a box plot."
            ),
            code="""VALUES = [3, 7, 8, 10, 12, 15, 18]

def percentile(sorted_values, fraction):
    if len(sorted_values) == 1:
        return float(sorted_values[0])
    position = fraction * (len(sorted_values) - 1)
    lower = int(position)
    upper = min(lower + 1, len(sorted_values) - 1)
    weight = position - lower
    return sorted_values[lower] * (1 - weight) + sorted_values[upper] * weight

numbers = sorted(VALUES)
for label, fraction in [("p25", 0.25), ("p50", 0.50), ("p90", 0.90)]:
    print(label, round(percentile(numbers, fraction), 2))
print("min", numbers[0], "max", numbers[-1])

assert percentile(numbers, 0.5) == 10.0
print("percentiles interpolate between neighbouring values")
""",
            variant_b='report the interquartile range as p75 minus p25',
            variant_c='switch to a nearest-rank percentile and show how the answers shift',
            mistakes=[
                "Computing a percentile on the unsorted list, giving a meaningless position.",
                "An off-by-one between the sample and population definitions of a percentile.",
                "Reading min and max as [0] and [1] instead of the first and last of the sorted list.",
            ],
            q1=(
                "Why does the 50th percentile equal the median?",
                "Both mark the value with half the ordered data on each side, so they are the same position by definition.",
            ),
            homework=(
                "Write `percentile(sorted_values, fraction)` implementing linear interpolation, and a "
                "`five_number(values)` that returns min, p25, median, p75 and max in that order. Print the five "
                "numbers for a sorted list of eight values, and comment the line that clamps the upper index at "
                "the end."
            ),
            patterns=["def ", "percentile", "print("],
            mapping=(
                "Excel has PERCENTILE.INC and QUARTILE for this; the interpolation rule matters because p50 and "
                "the median only agree when the same rule is used, and pandas quantile makes the choice explicit."
            ),
        ),
        110: dict(
            topic="Pivot tables as nested dicts",
            idea=(
                "A pivot table is a grouping by two fields at once, and the natural Python shape for it is a "
                "dictionary of dictionaries. The outer key is the row field, the inner key is the column field, "
                "and the value is whatever you aggregated, usually a sum or a count. Building it is one loop: "
                "look up or create the row bucket, then look up or create the column cell inside it, then add. "
                "The subtleties are the same ones that make pivot tables confusing in Excel. Missing combinations "
                "are real gaps and should print as zero or a dash rather than crashing an index. The set of "
                "columns must be collected across every row, because one row may have a column another lacks. "
                "And the inner dict must be fresh per outer key, or every row ends up sharing one bucket. When "
                "you print the grid you are looking at exactly what a PivotTable renders: labels down the left, "
                "labels along the top, and aggregated values in the body. pandas hands the same grid back from "
                "pivot_table, so the nested-dict version is not an approximation of that output, it is the "
                "structure those tools wrap in formatting and filters."
            ),
            code="""RECORDS = [
    {"region": "north", "product": "widget", "amount": "10"},
    {"region": "north", "product": "gizmo", "amount": "5"},
    {"region": "south", "product": "widget", "amount": "7"},
    {"region": "south", "product": "gizmo", "amount": "3"},
]

def pivot(records, row_field, col_field, value_field):
    table = {}
    for record in records:
        row = table.setdefault(record[row_field], {})
        row[record[col_field]] = row.get(record[col_field], 0.0) + float(record[value_field])
    return table

table = pivot(RECORDS, "region", "product", "amount")
columns = sorted({column for row in table.values() for column in row})
print("region", *columns)
for region in sorted(table):
    print(region, *[f"{table[region].get(column, 0.0):.1f}" for column in columns])

assert table["north"]["gizmo"] == 5.0
print("nested dicts are a pivot table")
""",
            variant_b='add a margins row that totals each product column down the table',
            variant_c='print missing combinations as a dash instead of zero',
            mistakes=[
                "Sharing one inner dict across row keys, so every row ends up with the same values.",
                "Assuming every row has every column, then indexing a missing key and crashing.",
                "Deriving the column list from unsorted keys, so the grid order varies between runs.",
            ],
            q1=(
                "What two structures does a pivot table need?",
                "An outer dict keyed by the row field and an inner dict keyed by the column field, holding the aggregated value.",
            ),
            homework=(
                "Write `pivot(records, row_field, col_field, value_field)` returning a dict of dicts of sums, and "
                "a helper that prints it as an aligned grid using a sorted column list. Run it on five records and "
                "comment which line creates the inner dict for a new column. Use `setdefault` for the outer dict "
                "and `.get` for the inner."
            ),
            patterns=["def ", "setdefault", "print("],
            mapping=(
                "This is literally the PivotTable layout — Rows on the left, Columns along the top, Values in "
                "the body — and pandas returns the identical grid as a DataFrame from pivot_table."
            ),
        ),
        111: dict(
            topic="Running totals and moving sums",
            idea=(
                "Some report lines depend on the lines before them. A running total adds each row to everything "
                "above it, and a moving sum or average looks at a fixed window of recent rows. Both are easy to "
                "do badly. Recomputing the running total from scratch at each row turns a single pass into a "
                "nested loop for no reason, when all you need is a variable that carries the previous value "
                "forward. The moving window has its own trap: the slice that defines the window is famously off "
                "by one, covering one row too many or too few, and the first few rows need a deliberate decision "
                "about partial windows. Averaging rather than summing is a common variant, and a seven-day moving "
                "average is the same machinery with a division at the end. These patterns matter because a "
                "running total underlies a balance column and a moving average underlies a trend line, and both "
                "are trivially wrong in ways that are hard to see in a grid. Excel users express them with growing "
                "and sliding ranges; writing the loop makes the window boundary and the partial-window rule "
                "explicit and testable."
            ),
            code="""DAILY = [("mon", 10), ("tue", 5), ("wed", 8), ("thu", 2), ("fri", 9)]

def running_total(pairs):
    total = 0.0
    out = []
    for label, value in pairs:
        total += value
        out.append((label, total))
    return out

def moving_sum(pairs, window):
    values = [value for _, value in pairs]
    out = []
    for index in range(len(values)):
        start = max(0, index - window + 1)
        out.append((pairs[index][0], sum(values[start:index + 1])))
    return out

for label, total in running_total(DAILY):
    print("running", label, total)
for label, total in moving_sum(DAILY, 3):
    print("moving3", label, total)

assert running_total(DAILY)[-1][1] == 34
print("running total and a 3-day moving sum")
""",
            variant_b='compute a 7-day moving average instead of a sum and round to two decimals',
            variant_c='start the moving window only once enough days exist, skipping partial windows',
            mistakes=[
                "Recomputing the running total from scratch each row, turning a linear pass into a nested loop.",
                "Slicing the moving window with an off-by-one start, so it covers four days instead of three.",
                "Letting the running total drift by re-rounding it at every step.",
            ],
            q1=(
                "Why can a running total be built in a single pass?",
                "Each step needs only the previous running value plus the current row, so no earlier rows are revisited.",
            ),
            homework=(
                "Write `running_total(pairs)` returning a list of `(label, cumulative)` tuples in input order, "
                "and `moving_sum(pairs, window)` returning the sum of the last `window` values at each point. Run "
                "both on a week of daily figures, print them, and comment which line handles the partial window "
                "at the start."
            ),
            patterns=["def ", "moving_sum", "print("],
            mapping=(
                "Excel builds running totals with a growing range like =SUM($B$2:B2) and moving sums with "
                "=SUM(B2:B4) dragged down; the loop version makes the window definition explicit and testable."
            ),
        ),
        112: dict(
            topic="Percentages and shares",
            idea=(
                "A percentage is a ratio whose denominator someone forgot to agree on. Before you compute a share "
                "you must fix the total you are dividing by — the grand total of all groups, the total of some "
                "subset, or the size of the largest group — because each choice gives a different, defensible "
                "number. Getting the denominator right at the start also gives you a free check: shares of a "
                "grand total must sum to one, and if they do not, either a group is missing or the denominator "
                "was wrong. Rounding is the other trap. Round every share to a whole percent and the displayed "
                "numbers may sum to ninety-nine or a hundred and one, which looks like an error even though the "
                "underlying arithmetic is exact; print rounded values for the reader and compare the unrounded "
                "ones for the check. Finally, a share of an empty total is a division by zero, so the empty case "
                "needs a defined answer rather than a crash. These are the same questions a PivotTable asks when "
                "you choose Percentage of Grand Total, Row Total or Column Total, and the same ones pandas asks "
                "when you divide a column by its total."
            ),
            code="""TOTALS = {"north": 15.0, "south": 7.0, "east": 8.0}

def shares(totals):
    if not totals:
        return {}
    grand = sum(totals.values())
    return {key: value / grand for key, value in totals.items()}

parts = shares(TOTALS)
for key in sorted(parts):
    print(key, f"{parts[key] * 100:.1f}%")

assert abs(sum(parts.values()) - 1.0) < 1e-9
print("shares sum to one")
""",
            variant_b="show each group's share of the largest group instead of the grand total",
            variant_c='flag any group whose share falls below five percent',
            mistakes=[
                "Dividing by the row count instead of the grand total, so the shares do not sum to one.",
                "Rounding every share to a whole percent before checking that they sum to a hundred.",
                "Computing a share of an empty total and triggering a division by zero.",
            ],
            q1=(
                "Why compute the grand total once before the shares?",
                "Every share uses the same denominator; recomputing it risks drift and hides that all shares must sum to one.",
            ),
            homework=(
                "Write `shares(totals)` that returns each key's fraction of the grand total, and a printer that "
                "renders them as percentages with one decimal place. Guard against an empty dict, print the "
                "shares in sorted order, and comment which line computes the common denominator."
            ),
            patterns=["def ", "sum(", "print("],
            mapping=(
                "In a PivotTable you get this by setting the value field to show values as percent of grand "
                "total, and pandas reproduces it with division by the total — same denominator discipline either way."
            ),
        ),
        113: dict(
            topic="Conditional highlights as rules",
            idea=(
                "Conditional formatting is a rule engine, and the useful way to build one is to treat the rules as "
                "data rather than as control flow. A rule is a pair: a predicate over a value and a label "
                "describing what to do when it matches. An ordered list of such pairs is evaluated top to bottom, "
                "and the first match wins, which is exactly how Excel's conditional formatting rules behave and "
                "why their order is adjustable. Keeping the rules in a list means you can print them, reorder "
                "them, reuse them for a second column, and test the classifier without touching the report loop. "
                "The two failure modes are worth naming. If the rules are written as an if-elif chain buried in "
                "the loop that formats cells, the thresholds end up duplicated and drift apart. And if no rule "
                "matches, a value falls through to nothing, so the classifier needs a defined default rather than "
                "an accidental blank. A small function that returns a label for any value is easier to reason "
                "about than colouring code scattered through the aggregation, and it has the same shape as a "
                "lookup that maps bands of values to names."
            ),
            code="""THRESHOLDS = [
    (lambda value: value >= 90, "green"),
    (lambda value: value >= 50, "amber"),
    (lambda value: value < 50, "red"),
]

def classify(value, rules):
    for predicate, label in rules:
        if predicate(value):
            return label
    return "none"

SCORES = [("alice", 95), ("bob", 72), ("carol", 40)]

for name, score in sorted(SCORES):
    print(name, score, classify(score, THRESHOLDS))

assert classify(72, THRESHOLDS) == "amber"
print("rules as ordered data, first match wins")
""",
            variant_b='add a fourth rule for scores of exactly zero so every value matches something',
            variant_c='return a colour pair (fill, font) instead of one label to mirror Excel styles',
            mistakes=[
                "Writing the rules as an if-elif chain inside the loop, so thresholds live in two places.",
                "Ordering the rules loosely, so a broad rule shadows a narrower one.",
                "Forgetting a fall-through case, so an unmatched value returns nothing.",
            ],
            q1=(
                "Why express the highlights as an ordered list of rules rather than an if-elif chain?",
                "The rules become data you can print, reorder and test, and the first-match order is explicit instead of buried in control flow.",
            ),
            homework=(
                "Write `classify(value, rules)` that walks an ordered list of `(predicate, label)` rules and "
                "returns the first match, with an explicit fall-through label. Define three threshold rules, "
                "classify five scores, print each name with its label, and comment which line guarantees an "
                "unmatched value still gets an answer."
            ),
            patterns=["def ", "for ", "print("],
            mapping=(
                "Excel conditional formatting is exactly this: an ordered set of rules evaluated top to bottom "
                "with first-match-wins; coding it as data keeps a report's colours and a pivot's colour scale in sync."
            ),
        ),
        114: dict(
            topic="Multi-sheet reports",
            idea=(
                "A workbook is not one table, it is a small collection of tables that people read together. "
                "Modelling it as a dictionary of sheet name to rows, where every sheet keeps the same "
                "header-plus-rows shape, means one printer, one validator and one row counter serve the whole "
                "workbook instead of one of each per tab. The shape discipline is what makes that possible: a "
                "sheet whose first row is always the header and whose remaining rows are always data can be "
                "summarised generically, so a new sheet costs nothing but a dictionary entry. Two habits keep "
                "multi-sheet reports predictable. Iterate the sheet names in sorted order, because dictionary "
                "order depends on insertion history and a reader should not see the tabs shuffle between runs. "
                "And never assume a sheet exists; a missing name should produce a clear error listing what is "
                "available, not a stack trace. This mirrors how openpyxl exposes a workbook, as named worksheets "
                "you iterate in order, and how pandas reads all sheets of a file into a dictionary keyed by sheet "
                "name, so the structure you build by hand is the one those libraries hand back."
            ),
            code="""SHEETS = {
    "Summary": [["region", "total"], ["north", "15.00"]],
    "Detail": [["region", "amount"], ["north", "10.00"], ["north", "5.00"]],
}

def sheet_names(sheets):
    return sorted(sheets)

def sheet_rows(sheets, name):
    header, *rows = sheets[name]
    return header, rows

for name in sheet_names(SHEETS):
    header, rows = sheet_rows(SHEETS, name)
    print(name, "columns:", header, "data rows:", len(rows))

assert sheet_names(SHEETS) == ["Detail", "Summary"]
print("one workbook, many sheets, one shape each")
""",
            variant_b='add a Notes sheet with a single column and confirm the printer still handles it',
            variant_c='raise an error listing the available sheets when a requested name is missing',
            mistakes=[
                "Assuming a sheet exists and crashing when a name is mistyped.",
                "Treating the header as a data row, inflating every row count by one.",
                "Iterating the sheets dict directly, so the sheet order changes between runs.",
            ],
            q1=(
                "Why give every sheet the same header-plus-rows shape?",
                "A single shape means one reader, one writer and one printer handle every sheet, so adding a sheet costs no new code.",
            ),
            homework=(
                "Write `describe_workbook(sheets)` that walks the sheets in sorted-name order and returns a list "
                "of `(name, column_count, row_count)` tuples. Build a workbook with three sheets, print the "
                "description, and comment which line skips the header when counting data rows."
            ),
            patterns=["def ", "sorted", "print("],
            mapping=(
                "A workbook with several tabs is a dict of tables; openpyxl's wb.sheetnames is the same walk, and "
                "pandas read_excel(sheet_name=None) returns a dict keyed by tab name."
            ),
        ),
        115: dict(
            topic="Chart data preparation",
            idea=(
                "Between a summary and a chart there is a small, unglamorous step: turning your numbers into two "
                "aligned lists. A chart pairs a category and a value by position, so the category list and every "
                "value series must be the same length and in the same order. That single fact explains most chart "
                "bugs. If you sort the categories one way and the values another, every bar is labelled with the "
                "wrong name, and because the picture still looks plausible nobody notices. If one series drops a "
                "category another keeps, the remaining bars shift by one. So the rule is to build the category "
                "list and the value lists together from the same sorted source, and to assert that their lengths "
                "match. Ranking a bar chart is then just a different sort of the same pairs, with category and "
                "value moving as a unit. Excel charts accept a category range plus one or more value ranges and "
                "rely on you keeping them aligned; preparing those lists is the whole job before a chart object "
                "ever sees them, and pandas plotting reads the same aligned columns back."
            ),
            code="""SALES = [("north", 15.0), ("south", 7.0), ("east", 8.0)]

def chart_data(pairs):
    ordered = sorted(pairs)
    categories = [label for label, _ in ordered]
    values = [value for _, value in ordered]
    return categories, values

categories, values = chart_data(SALES)
print("categories:", categories)
print("values:", values)
print("max index:", values.index(max(values)))

assert len(categories) == len(values)
print("aligned categories and series for a chart")
""",
            variant_b='sort by value descending so the chart reads as a ranked bar chart',
            variant_c='stack two series that share the same category list and print both value lists',
            mistakes=[
                "Sorting the categories and the values separately, so bars line up with the wrong labels.",
                "Plotting raw strings without converting them to numbers, leaving the axis empty.",
                "Dropping empty categories from one series but not the other, breaking the alignment.",
            ],
            q1=(
                "Why must categories and values be sorted together?",
                "A chart pairs each category with its value by position, so sorting them separately silently mislabels every bar.",
            ),
            homework=(
                "Write `chart_data(pairs)` returning a `(categories, values)` pair sorted by label, plus "
                "`ranked(pairs)` that re-sorts by value descending. Run both on five figures and comment which "
                "line keeps the category and value lists aligned."
            ),
            patterns=["def ", "sorted", "return"],
            mapping=(
                "Excel builds a chart from a category range and one or more equal-length value ranges; producing "
                "those two aligned lists in code is the whole of chart preparation before openpyxl creates a chart."
            ),
        ),
        116: dict(
            topic="Summary and totals rows",
            idea=(
                "A report usually needs a final line that says what the column adds up to, and how you add it "
                "decides whether the report can be trusted. The totals row belongs to the presentation, not to "
                "the body: it must be visually distinct and, more importantly, recognisable to code so that "
                "anything summing the body later does not count the total a second time. That is the classic "
                "double-count bug, where a grand total is fed back through the same aggregation and the number "
                "quietly doubles. Building the totals row from the body, summing each numeric column across the "
                "body rows while skipping the label column, keeps the derived total consistent with what the "
                "reader sees, and marking the row lets a later reader exclude it on purpose. A related decision "
                "is granularity: one grand total, or a subtotal after each group. The arithmetic is the same "
                "summation, but the level must be chosen deliberately, because a subtotal and a grand total in "
                "the same column look alike and mean different things. Excel's Subtotal command and PivotTable "
                "grand totals automate this; doing it by hand shows exactly what they inserted."
            ),
            code="""ROWS = [
    ("north", 10, 2),
    ("north", 5, 1),
    ("south", 7, 3),
]

def add_totals(rows, total_label):
    body = [list(row) for row in rows]
    totals = [total_label]
    for column in range(1, len(rows[0])):
        totals.append(sum(row[column] for row in rows))
    return body + [totals]

table = add_totals(ROWS, "TOTAL")
for row in table:
    print(row)

assert table[-1] == ["TOTAL", 22, 6]
print("totals row appended, never mixed into the body")
""",
            variant_b='insert a subtotal row after each region instead of one grand total',
            variant_c='mark the totals row so a later reader can exclude it from further aggregation',
            mistakes=[
                "Summing the totals row again on a second pass, doubling the grand total.",
                "Totalling text columns and crashing on the label.",
                "Confusing a subtotal per group with one grand total over everything.",
            ],
            q1=(
                "Why keep the totals row separate from the body rows?",
                "Code that sums the body would otherwise count the total a second time; keeping it distinct makes the total safe to read and safe to ignore.",
            ),
            homework=(
                "Write `add_totals(rows, total_label)` that sums every numeric column and returns the body rows "
                "followed by one totals row, plus `is_total_row(row, label)` that recognises it later. Print the "
                "table, run the check, and comment which line builds the summed values."
            ),
            patterns=["def ", "sum(", "print("],
            mapping=(
                "Excel's Subtotal command and PivotTable grand totals both add these rows for you; knowing how "
                "they are built is what stops a copied total being counted twice when the sheet is exported."
            ),
        ),
        117: dict(
            topic="Reconciliation checks",
            idea=(
                "A reconciliation check is the report proving itself against its source. The simplest form "
                "compares the sum of the report's parts with an independent total — a control figure, a ledger "
                "line, a known count — and reports the difference. The discipline is to compare like with like: "
                "the parts summed before rounding against the whole before rounding, not a rounded report against "
                "a precise total, or the check will show differences that are only presentation. Floating point "
                "makes an exact zero comparison fragile, so a tolerance is normal and should be stated, typically "
                "a fraction of a cent for money. A useful check reports three things: what was computed, what was "
                "expected, and the signed difference. The sign tells you which way the error leans and the size "
                "tells you whether it is a rounding artefact or a genuinely missing row, which is exactly the "
                "information a bare pass or fail withholds. Reconciling per group rather than only in total "
                "localises the mistake to one bucket. This is the control-total habit an analyst does with a "
                "scratch cell, made repeatable and impossible to skip in an exported file."
            ),
            code="""GROUPS = {"north": 15.0, "south": 7.0}
LEDGER_TOTAL = 22.0

def reconcile(parts, expected):
    computed = sum(parts.values())
    difference = round(computed - expected, 2)
    return {"computed": computed, "expected": expected, "difference": difference}

CHECK = reconcile(GROUPS, LEDGER_TOTAL)
for key in sorted(CHECK):
    print(key, CHECK[key])

assert CHECK["difference"] == 0.0
print("parts sum to the whole" if CHECK["difference"] == 0.0 else "MISMATCH")
""",
            variant_b='add an expected value per group and list only the groups that disagree',
            variant_c='treat any difference under one cent as a rounding artefact, not a real mismatch',
            mistakes=[
                "Comparing floats exactly with no tolerance, so a rounding artefact looks like a failure.",
                "Reconciling after the totals were rounded, so the check hides small differences.",
                "Reporting only that it failed, without the size or sign of the difference.",
            ],
            q1=(
                "Why report the difference rather than just pass or fail?",
                "The size and sign of the difference tell you whether it is a rounding artefact or a genuinely missing row.",
            ),
            homework=(
                "Write `reconcile(parts, expected, tolerance)` returning computed, expected and difference, plus "
                "a flag that the difference is within tolerance. Run it once where the parts match and once where "
                "a row is missing, print both results, and comment which line decides the tolerance."
            ),
            patterns=["def ", "difference", "print("],
            mapping=(
                "This is the control-total discipline Excel users apply with a scratch cell comparing two sums; "
                "in code every report can carry its own proof that the totals still agree."
            ),
        ),
        118: dict(
            topic="Rounding and presentation rules",
            idea=(
                "Numbers arrive at full precision and leave the report formatted, and the gap between the two is "
                "where money goes wrong. The rule is to compute at full precision and round exactly once, at the "
                "boundary where a number becomes a value someone will act on. Rounding at every intermediate step "
                "compounds small errors until a total disagrees with the detail it came from by a visible amount. "
                "The rounding rule itself is not neutral: Python's built-in round uses banker's rounding, "
                "rounding half to even, while finance usually expects half-up, so Python turns 2.5 into two where "
                "a finance sheet shows three. The standard-library answer is the decimal module, which rounds "
                "exactly the value you mean and lets you name the mode, ROUND_HALF_UP for money. Keeping the "
                "computed Decimal separate from the formatted string is the second half of the discipline: format "
                "for display with a fixed number of places, but never let the formatted string flow back into "
                "arithmetic. Excel's ROUND family encodes the same choice, and matching it is what lets a Python "
                "report replace a spreadsheet without the finance team filing a bug."
            ),
            code="""from decimal import Decimal, ROUND_HALF_UP

def round_money(value):
    return Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

def money_text(value):
    return f"{value:.2f}"

for value in [2.675, 1.005, 3.335]:
    print(value, "->", money_text(round_money(value)))

assert round_money("2.675") == Decimal("2.68")
print("half-up money rounding via Decimal")
""",
            variant_b='round to whole units for a summary and keep cents only in the detail sheet',
            variant_c="try Python's built-in round and show where it differs from half-up on a tie",
            mistakes=[
                "Rounding values at every intermediate step, so errors accumulate into the total.",
                "Relying on banker's rounding for money when the finance rule is half-up.",
                "Formatting a raw float for display instead of the value you actually computed.",
            ],
            q1=(
                "Why round only at the end rather than at every step?",
                "Each rounding step introduces a small error; rounding once at the boundary keeps the accumulated total closer to the true value.",
            ),
            homework=(
                "Write `round_money(value)` using `decimal.Decimal` and `ROUND_HALF_UP` to return a two-decimal "
                "result, and `money_text(value)` to render it. Run the pair over three tie values, print each "
                "input beside its output, and comment which line names the rounding mode."
            ),
            patterns=["def ", "Decimal", "print("],
            mapping=(
                "Excel's ROUND rounds half away from zero while ROUNDUP and ROUNDDOWN are directional; matching "
                "that rule in code stops a Python report disagreeing with the finance spreadsheet it replaces."
            ),
        ),
        119: dict(
            topic="Review: aggregation and reports checklist",
            idea=(
                "This is the day the pieces become a habit rather than a list of tricks. Everything this phase "
                "did — grouping, counting, summing, averaging, percentages, totals rows, rounding, reconciling — "
                "collapses into a short checklist you run before any report leaves your machine. Does every "
                "source row land in exactly one group, so the counts reconcile? Do the parts sum to the whole, "
                "within a stated tolerance? Are totals rounded once and clearly distinguished from body rows? Is "
                "the output sorted deterministically, so two runs produce the same text? Are malformed rows "
                "skipped and counted rather than silently dropped? A report that passes those checks is "
                "trustworthy for reasons you can state, not because it looked right in a screenshot. The deeper "
                "habit is to make each check a small function that returns a list of failures, empty when all is "
                "well, so the checklist can be asserted in a test and reused on every report. That is what "
                "separates automation from a one-off macro: the checks are code, they run every time, and a "
                "failure is loud. Excel's PivotTable gives you the aggregation; only you can give the report its "
                "proof."
            ),
            code="""RECORDS = [
    {"region": "north", "amount": "10"},
    {"region": "north", "amount": "5"},
    {"region": "south", "amount": "7"},
]

def build_report(records):
    groups = {}
    for record in records:
        bucket = groups.setdefault(record["region"], {"count": 0, "total": 0.0})
        bucket["count"] += 1
        bucket["total"] += float(record["amount"])
    return [(name, data["count"], round(data["total"], 2)) for name, data in sorted(groups.items())]

def checklist(rows, records):
    failures = []
    if not rows:
        failures.append("empty report")
    if sum(row[1] for row in rows) != len(records):
        failures.append("counts do not reconcile")
    if sum(row[2] for row in rows) != 22.0:
        failures.append("totals do not reconcile")
    return failures

rows = build_report(RECORDS)
for row in rows:
    print(row)
print("failures:", checklist(rows, RECORDS))

assert checklist(rows, RECORDS) == []
print("checklist passed")
""",
            variant_b='add a uniqueness check that no group name appears twice in the report',
            variant_c='turn the checklist into named (label, predicate) rules and print each result',
            mistakes=[
                "Trusting a report because it runs without error, without reconciling its counts and totals.",
                "Checking the report against itself rather than against the original rows.",
                "Forgetting an earlier failure once a later check passes.",
            ],
            q1=(
                "What makes a reconciliation check meaningful?",
                "It compares the report against the source rows — the counts and the totals — not against the report's own intermediate values.",
            ),
            homework=(
                "Write `build_report(records)` returning sorted `(name, count, total)` rows, and "
                "`checklist(rows, records)` returning a list of failure descriptions, empty when counts and "
                "totals reconcile. Run both on six records, print the failures, and comment which line compares "
                "the report to the source."
            ),
            patterns=["def ", "failures", "print("],
            mapping=(
                "This mirrors the final pass an analyst makes over a PivotTable before sending it: row counts "
                "tie, totals tie, and every step has a check that can fail loudly instead of silently."
            ),
        ),
    },
)
