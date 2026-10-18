"""Canonical topic batch: string formatting for output (Lutz ch 7)."""
from canonical_topics import topic

LUTZ_CH7_FORMAT = {
    "book": "learning-python",
    "chapter": 7,
    "pages": [155, 196],
    "sections": ["String Formatting Method Calls", "String Conversion Tools"],
}


topic(
    "canonical:string-formatting-output",
    "Formatting assembles computed values into fixed-shape output, and the field width, alignment and precision are the knobs that make it line up",
    sources=[dict(LUTZ_CH7_FORMAT)],
    concept=(
        "Formatting takes computed values, which vary in length and precision, and places "
        "them into output with a fixed shape. The modern way is an f-string: a literal with "
        "replacement fields, each holding an expression, so a value is written where its "
        "placeholder sits and the surrounding text supplies the structure. Inside a field, a "
        "colon begins the format specification, and that is where the useful knobs live. A "
        "number sets the minimum width, so columns align; a zero before the width pads with "
        "zeros instead of spaces; an alignment character chooses left, right or centred "
        "filling; and for numbers a precision after a dot sets how many digits are shown, "
        "which is how a float is presented as currency or a percentage without its full "
        "binary expansion leaking into the display. The older percent formatting and the "
        "str.format method produce the same output, so reading either is still a real skill, "
        "but writing new code in an f-string is clearer, because the value sits where it "
        "appears in the sentence rather than being listed at the end. Formatting never "
        "changes the underlying value, only how it is presented, which is why a number can "
        "be shown as rounded while the stored value stays exact."
    ),
    prerequisites=["canonical:object-type-categories"],
    pitfalls=[
        "Calling str on a value and then formatting it, so the format specification applies "
        "to the text rather than to the number and the precision is ignored.",
        "Writing a width or precision for the wrong type, such as asking for decimal places "
        "on an integer, which raises an error instead of aligning the column.",
        "Padding a value to a width that the data will eventually exceed, which silently "
        "breaks the alignment instead of raising, because the width is a minimum.",
    ],
    adapters={
        "machine-learning": {
            "framing": (
                "A report has to present a model's scores to a reader who is comparing "
                "numbers across rows, so precision and width matter more than anything else."
            ),
            "application": (
                "Walk the example as an evaluation summary being printed. Three scores have "
                "to line up in a column and each is a float with a long binary expansion, so "
                "a precision of four places is specified and the width makes the figures "
                "stack vertically. The choice of precision is a presentation decision, not a "
                "computation one, which is exactly why it lives in the field rather than "
                "rounding the score beforehand: the stored value keeps its full accuracy for "
                "later calculation while the display stays readable. When several models are "
                "compared in a table, the alignment is what lets a reader's eye find the "
                "best column, and a value that exceeds the chosen width would push the whole "
                "row out of alignment rather than being truncated."
            ),
            "example_hint": "format model scores with a shared width and precision into an aligned report",
            "assessment_angle": "what the width and the precision each control, and what stays exact",
            "day": 4,
            "title": "Present Scores to Four Places, Keep the Value Exact",
            "code": """scores = {"baseline": 0.841952, "tuned": 0.873341, "holdout": 0.862}

print(f"{'model':<10} {'score':>8}")
for name, value in scores.items():
    print(f"{name:<10} {value:8.4f}")

best = max(scores, key=scores.get)
print(f"best: {best} ({scores[best]:.4f})")
print("stored value:", scores["tuned"])
""",
            "questions": [
                "What do the 8 and the .4 in {value:8.4f} each control, and which one keeps the column aligned?",
                "The stored tuned score is printed at the end with no format specification. Why does it show more digits than the report does?",
                "Why is the precision written in the field instead of rounding the score before the loop?",
            ],
            "answers": [
                "The 8 is the minimum field width that aligns the column, and the .4 sets four digits after the decimal point shown for the score.",
                "Because the formatting only controls presentation, so the stored float keeps its full precision and prints with its natural digits.",
                "Because the display needs to be readable while the stored value stays accurate for later computation, and rounding first would lose that accuracy.",
            ],
            "homework": (
                "Write report_scores.py with a dictionary of at least five model names to float "
                "scores between zero and one. Print a header row and one row per model with the name "
                "left-aligned and the score shown to four decimal places in a fixed width. Then "
                "print the best model name with its formatted score and one raw stored value. "
                "Observable output: a header, five aligned rows, and two closing lines."
            ),
            "required_patterns": ["f\"", ":<", ":>", "max(", "print("],
        },
        "data-viz": {
            "framing": (
                "Every chart is surrounded by text: titles, axis labels, tick numbers and "
                "legends. Formatting is how that text is generated from data without being "
                "hand-written each time."
            ),
            "application": (
                "Walk the example as chart annotations being generated. A title is built "
                "from a category name and a count, a percentage field shows a share with a "
                "trailing percent sign, and a tick value is padded to a width so the axis "
                "labels do not jump. The important distinction is between text built from "
                "values and text written once: the title has to be an f-string because the "
                "count changes, and writing it by hand would make the annotation wrong the "
                "moment the data does. Formatting a percentage is the case where precision "
                "matters most, because a share printed at full precision is unreadable while "
                "the same share printed to one place is immediately legible, and both come "
                "from the same stored value."
            ),
            "example_hint": "generate chart titles, percentages and padded tick labels from data",
            "assessment_angle": "which text must be generated and why the percentage precision is a display choice",
            "day": 4,
            "title": "Generate the Chart's Text: Titles, Percentages, Padded Ticks",
            "code": """counts = {"north": 412, "south": 388, "east": 233, "west": 167}
total = sum(counts.values())

for region, count in counts.items():
    share = count / total
    title = f"{region} region: {count} records ({share:.1%})"
    print(f"{title}")

for value in sorted(counts.values(), reverse=True):
    print(f"{value:6d} - axis tick")
""",
            "questions": [
                "Why is the title built as an f-string from the region and the count rather than written as a literal?",
                "What does the .1% specification do to the share, and what does the trailing percent sign tell you about the field's meaning?",
                "The axis ticks are printed with {value:6d}. Why is the width applied to an integer safe even if the counts grow?",
            ],
            "answers": [
                "Because the count and the share change with the data, so a hand-written title would be wrong the moment the counts did.",
                "It shows the share as a percentage with one digit after the point, and the percent sign shows the value was scaled by a hundred for display.",
                "Because the width is a minimum, so a larger value simply takes the room it needs and the tick still prints correctly.",
            ],
            "homework": (
                "Write chart_text.py with a dictionary of at least six regions to record counts. "
                "For each region print a generated title string containing the region name, the count "
                "and the share formatted as a percentage to one decimal place. Then print every "
                "count sorted descending, right-aligned in a fixed width, labelled as an axis tick. "
                "Observable output: one title per region plus one tick line per region."
            ),
            "required_patterns": ["f\"", ".1%", "sum(", "sorted(", "print("],
        },
        "api-building": {
            "framing": (
                "An API's response is structured data, but its logs, request ids and error "
                "messages are formatted text, and they have to be built consistently."
            ),
            "application": (
                "Walk the example as request logging being generated. Each request has a "
                "method, a path, a status code and a duration, and the log line is built from "
                "all four in a fixed template so that a later grep finds a predictable shape. "
                "Zero-padding the request id is the detail that pays: a width with a leading "
                "zero makes ids sort lexically in the same order as numerically, which "
                "matters because log tools compare text, not numbers. The duration is shown "
                "with a precision so that a fast request is not printed with a misleading "
                "tail of digits, and a status code is printed as an integer in a fixed "
                "width so the column of statuses lines up for scanning. Formatting here is "
                "what makes logs machine-readable, because a stable template is what a "
                "filter can rely on."
            ),
            "example_hint": "build log lines and request ids from a fixed template with padded fields",
            "assessment_angle": "why the template is fixed, and what zero-padding an id achieves",
            "day": 4,
            "title": "Log with a Fixed Template: Pad the Id, Align the Status",
            "code": """requests = [
    ("GET", "/api/items", 200, 0.0312),
    ("POST", "/api/items", 201, 0.0879),
    ("GET", "/api/items/42", 404, 0.0144),
]

for index, (method, path, status, duration) in enumerate(requests, start=1):
    request_id = f"REQ-{index:04d}"
    print(f"{request_id} {method:<4} {status} {path:<16} {duration:.3f}s")
""",
            "questions": [
                "Why is the request id generated with {index:04d} rather than printed as the plain index?",
                "The duration is formatted with .3f while the status is formatted with no specification. Why the difference?",
                "What makes these log lines greppable, and which feature of the template provides that?",
            ],
            "answers": [
                "So that the ids are zero-padded to a fixed width and therefore sort in text order the same way they sort numerically.",
                "Because the duration is a float whose long tail would clutter the line, while the status is an integer that already prints cleanly and just needs the column to line up.",
                "The fixed template, since every line has the same fields in the same order, so a filter searching for a status or a path always matches the same position.",
            ],
            "homework": (
                "Write request_log.py with a list of at least eight tuples holding an HTTP method, a "
                "path, a status code and a float duration. For each one, generate a zero-padded "
                "request id and print a single log line containing the id, the method left-aligned, "
                "the status, the path and the duration to three decimal places. Observable output: "
                "eight lines, all fields vertically aligned."
            ),
            "required_patterns": ["f\"", "{index:04d}", ".3f", "enumerate(", "print("],
        },
        "web-scraping": {
            "framing": (
                "A scrape ends by reporting what it found, and that report is text built from "
                "counts, prices and urls. Formatting is what makes it scannable."
            ),
            "application": (
                "Walk the example as a scrape summary being generated. Each product row is "
                "built from a title, a price and a count, and the price is formatted as "
                "currency with two places because a scraped price arrives as a float whose "
                "third decimal is noise. Building a url from a template is the second skill: "
                "a base and a slug are assembled into a link, and the assembly has to be an "
                "f-string because the slug varies per product, so writing each url by hand "
                "would defeat the purpose of the scrape. The trap worth naming is "
                "formatting a value that has already been turned into text, because then "
                "the currency specification is silently ignored and the column shows the "
                "raw digits."
            ),
            "example_hint": "format scraped prices as currency and build urls from a template",
            "assessment_angle": "why currency formatting must apply to a number, and what a template gives you",
            "day": 4,
            "title": "Report a Scrape: Currency, Counts, and Built URLs",
            "code": """products = [("notebook", 12.5), ("pen set", 3.759), ("binder", 8)]
BASE = "https://shop.example.com/items"


def currency(value):
    return f"${value:,.2f}"


for index, (name, price) in enumerate(products, start=1):
    url = f"{BASE}/{name.replace(' ', '-')}-{index}"
    print(f"{index:>3} {name:<12} {currency(price):>8} {url}")

print(f"items: {len(products)} | total: {currency(sum(p for _, p in products))}")
""",
            "questions": [
                "What does ,.2f do to a price, and why does the function have to receive a float rather than the price as text?",
                "Why is the url built with an f-string from the base and the slug instead of written once?",
                "The summary line is built with len and sum. What does each contribute to the report?",
            ],
            "answers": [
                "It shows the value with a thousands separator and exactly two decimal places, and it must receive a float because applying it to text would ignore the specification and show the raw digits.",
                "Because the slug varies with each product, so a single literal could not point at more than one item, while the template generates a correct url per row.",
                "len gives the item count and sum gives the total value, so the closing line reports the size and the value of the scrape.",
            ],
            "homework": (
                "Write scrape_report.py with a list of at least seven products, each a name and a "
                "float price, some prices having three decimal places. Write a currency function "
                "that formats a float with a thousands separator and two decimals. For each product "
                "print an index, the name, the formatted price and a url built from a base string "
                "and the slug. End with a summary line giving the item count and the formatted "
                "total. Observable output: one row per product plus the summary."
            ),
            "required_patterns": ["f\"", ",.2f", "len(", "sum(", "print("],
        },
        "testing-qa": {
            "framing": (
                "A test's failure message has to name what actually happened. A formatted "
                "message built from the real values is what makes a failure fixable."
            ),
            "application": (
                "Walk the example as a comparison helper producing a message. The expected "
                "and actual values are both inserted into the message, and the numeric ones "
                "are formatted to a precision so that two floats that differ only in display "
                "do not produce a confusing message. Building the message from the values is "
                "what makes it trustworthy: a hand-written message goes stale, while one "
                "assembled from the actual inputs always describes the run that failed. The "
                "choice of precision in a message is worth thinking about, because too few "
                "places hides the difference that caused the failure and too many buries it "
                "in digits, so the message should show enough to see the gap and no more. "
                "For a list, the length and the first item are usually the two most useful "
                "facts to name."
            ),
            "example_hint": "build failure messages from actual values with a chosen precision",
            "assessment_angle": "what a message must name and how precision changes its usefulness",
            "day": 4,
            "title": "Build the Failure Message from the Values That Failed",
            "code": """def check_within(actual, expected, tolerance=1e-6):
    if abs(actual - expected) <= tolerance:
        return True, "within tolerance"
    return False, f"got {actual:.6f}, want {expected:.6f}, diff {abs(actual - expected):.6f}"


def check_length(values, expected):
    if len(values) == expected:
        return True, "length matches"
    return False, f"got {len(values)} items, want {expected}, first {values[0]!r}"


print(check_within(3.141592, 3.1415))
print(check_length(["a", "b"], 3))
""",
            "questions": [
                "Why is the difference between the two values computed and shown, rather than only the two values?",
                "Why does the length message name len(values) and values[0] specifically, and what does the !r add?",
                "Both helpers return a tuple rather than raising immediately. What does that buy a test suite?",
            ],
            "answers": [
                "Because the gap is what the reader needs to judge whether the failure is a rounding issue or a real mismatch, so showing it directly saves a step.",
                "The length is the fact that failed and the first item is the evidence of what the list actually holds, and repr shows the exact type and quoting of that item.",
                "It lets the caller decide how to report, accumulate several results, or continue collecting failures instead of stopping at the first one.",
            ],
            "homework": (
                "Write check_helpers.py with a check_within function that formats a numeric mismatch "
                "to six decimal places including the difference, and a check_length function that "
                "names the actual length, the expected length and the first item. Test each with at "
                "least three cases, two failing and one passing, and print the boolean and the "
                "message for every case. Observable output: six lines or more, each naming the "
                "actual values involved."
            ),
            "required_patterns": ["f\"", ".6f", "abs(", "len(", "print("],
        },
        "devops-scripting": {
            "framing": (
                "Disk, memory and network figures are byte counts so large that they are "
                "meaningless until they are scaled into units and formatted into a column."
            ),
            "application": (
                "Walk the example as a disk report being generated from byte counts. Each "
                "filesystem's used and total bytes are divided by a power of two, then "
                "formatted with a width and one decimal place, and the unit is part of the "
                "field so the figure and its label stay together. The division by a constant "
                "is what makes the number human-readable, and the precision is what stops it "
                "from showing a meaningless tail; the two together turn a raw byte count "
                "into something an operator can act on. Percentages in the same report are "
                "the case where a precision choice is a genuine decision, because a disk at "
                "97.8 percent full is a warning while one at 98 percent reads as an "
                "approximation, and the operator needs to see the gap between two "
                "filesystems clearly."
            ),
            "example_hint": "scale byte counts into units and format them into an aligned report",
            "assessment_angle": "what the division and the precision each contribute to readability",
            "day": 4,
            "title": "Scale Bytes, Format the Column: Reports an Operator Can Read",
            "code": """GIB = 1024 ** 3
filesystems = [("root", 38.2 * GIB, 100 * GIB), ("data", 412.9 * GIB, 500 * GIB)]

print(f"{'fs':<8} {'used':>8} {'total':>8} {'pct':>7}")
for name, used, total in filesystems:
    percent = used / total
    print(f"{name:<8} {used / GIB:8.1f} {total / GIB:8.1f} {percent:6.1%}")
""",
            "questions": [
                "What does dividing by GIB do, and why is the unit written into the field rather than into the value?",
                "The percent field uses 6.1%. What do the 6 and the .1 control, and why is the percent sign part of the specification?",
                "Why is the precision a real choice in this report rather than a detail?",
            ],
            "answers": [
                "It scales bytes into gibibytes so the figure is human-readable, and keeping the unit as a literal in the field keeps the value itself a plain number that can be compared or summed.",
                "The 6 is the minimum width aligning the column and the .1 shows one decimal place, while the percent sign shows the value was scaled by a hundred for display.",
                "Because the number of decimals decides whether the operator sees a genuine warning level or a rounded approximation, and too few places could hide the difference between two filesystems.",
            ],
            "homework": (
                "Write disk_report.py with a list of at least six filesystems, each a name with a "
                "used and total byte count built by multiplying a float by a gibibyte constant. "
                "Print a header row and one row per filesystem with the name left-aligned, the used "
                "and total figures scaled into gibibytes in a fixed width with one decimal place, "
                "and the share of space used as a percentage. Observable output: a header and six "
                "aligned rows."
            ),
            "required_patterns": ["f\"", "**", ":<", ".1%", "print("],
        },
        "algo-trading": {
            "framing": (
                "A trade blotter has to show prices, quantities and notional values that "
                "differ by orders of magnitude, and only formatting keeps them legible in "
                "one table."
            ),
            "application": (
                "Walk the example as a blotter row being generated. A price needs four "
                "decimal places because that is the tick convention, a quantity is an "
                "integer that has to line up, and a notional value needs a thousands "
                "separator because it is large. Each of those is a separate format "
                "specification applied to a different kind of number, which is the point "
                "worth grasping: the specification is chosen per field according to what "
                "that field means, not applied uniformly to the row. Computing the notional "
                "from price times quantity and formatting it separately keeps the value "
                "exact for the books while the display shows it rounded, so a blotter can "
                "be read by a trader without the underlying figures being altered. A "
                "padded trade id is what makes the rows sortable as text, the same way it "
                "does in a log."
            ),
            "example_hint": "format price, quantity and notional each with their own specification",
            "assessment_angle": "why each field has its own specification and what stays exact",
            "day": 4,
            "title": "One Table, Three Formats: Price, Quantity, Notional",
            "code": """trades = [
    ("AAPL", 182.4175, 150),
    ("MSFT", 415.02, 40),
    ("TSLA", 248.75, 1200),
]

print(f"{'id':<8} {'symbol':<7} {'price':>10} {'qty':>6} {'notional':>12}")
for index, (symbol, price, qty) in enumerate(trades, start=1):
    notional = price * qty
    print(f"T-{index:<7} {symbol:<7} {price:10.4f} {qty:6d} {notional:12,.2f}")
""",
            "questions": [
                "Why does the price use .4f while the quantity uses d and the notional uses ,.2f?",
                "The notional is computed as price times quantity and then formatted. Why is it not rounded before formatting?",
                "What does the padded trade id give you in a blotter, and what assumption does that make about ids?",
            ],
            "answers": [
                "Because each field means something different: the price follows a tick convention of four places, the quantity is a whole number, and the notional is large so it needs a thousands separator and two places.",
                "Because rounding first would change the value the books record, while formatting only controls the display, so the underlying notional stays exact.",
                "Text sorting that matches numeric order, which assumes the ids are zero-padded to a fixed width so a shorter id does not sort after a longer one.",
            ],
            "homework": (
                "Write blotter.py with a list of at least eight trades, each a symbol, a float "
                "price with four decimal places and an integer quantity of very different sizes. "
                "Print a header and one row per trade with a padded trade id, the symbol "
                "left-aligned, the price to four places, the quantity as an integer and the "
                "notional, computed as price times quantity, with a thousands separator and two "
                "decimals. Observable output: a header and eight aligned rows."
            ),
            "required_patterns": ["f\"", ".4f", ",.2f", "enumerate(", "print("],
        },
        "numerical-methods": {
            "framing": (
                "Numerical methods report approximations, and a report that shows twelve "
                "digits is not more precise, only less honest about what the method "
                "actually resolved."
            ),
            "application": (
                "Walk the example as an iteration being reported. The approximation is "
                "printed with a precision chosen to match the method's tolerance, so the "
                "digits shown are digits the method actually converged to, and the "
                "difference between successive approximations is printed separately to "
                "show convergence. The distinction that matters is between the value's "
                "precision and the method's accuracy: formatting to four places does not "
                "make the answer accurate to four places, and a naive reading of a long "
                "float assumes it does. That is why the report prints the tolerance as well "
                "as the answer, so the reader knows which digits carry meaning. A width is "
                "still applied for alignment, but the precision is the decision that "
                "carries the message, and choosing it below the tolerance would be "
                "misleading while choosing it far above would be noise."
            ),
            "example_hint": "report approximations with a precision matched to the method's tolerance",
            "assessment_angle": "the difference between displayed precision and actual accuracy",
            "day": 4,
            "title": "Show Only the Digits the Method Converged To",
            "code": """TOLERANCE = 1e-4
approx = 1.4142135623730951
previous = 1.4142

shown = f"{approx:.4f}"
delta = abs(approx - previous)
print(f"approximation: {shown}")
print(f"change:        {delta:.2e}")
print(f"tolerance:     {TOLERANCE:.2e}")
print(f"converged:     {delta <= TOLERANCE}")
print(f"full float:    {approx}")
""",
            "questions": [
                "Why is the approximation shown to four places when the full float has sixteen digits?",
                "What is the difference between the change printed in scientific notation and the tolerance printed beside it?",
                "Formatting to four places does not make the answer accurate to four places. What in the output tells the reader how much to trust it?",
            ],
            "answers": [
                "Because the tolerance is 1e-4, so only about four digits carry meaning, and showing more would imply a precision the method did not achieve.",
                "The change is how far the latest approximation moved, which is evidence of convergence, while the tolerance is the threshold the change is being judged against.",
                "The tolerance and the converged flag, since they state the standard the approximation was accepted against rather than letting the digit count imply accuracy.",
            ],
            "homework": (
                "Write report_approximation.py that holds an approximation, a previous approximation "
                "and a tolerance. Print the approximation to four decimal places, the absolute "
                "change in scientific notation, the tolerance in scientific notation, whether the "
                "change is within the tolerance, and the full float for comparison. Then repeat the "
                "precision choice with a second tolerance of 1e-8 and print the same five lines. "
                "Observable output: ten lines, showing the digit count following the tolerance."
            ),
            "required_patterns": ["f\"", ".4f", ".2e", "abs(", "print("],
        },
    },
)
