"""Canonical topic batch: numeric types (Lutz ch 5, pp. 105-142).

Companion to topics_lutz_foundation.py; split out so each file stays reviewable.
"""
from canonical_topics import topic

DAY = 2

LUTZ_CH5 = {
    "book": "learning-python",
    "chapter": 5,
    "pages": [105, 142],
    "sections": ["Numeric Type Basics", "Numbers in Action", "Floor versus truncation", "Other Built-in Numeric Tools"],
}


topic(
    "canonical:numbers-and-precision",
    "Integers are exact and unbounded, floats are approximations, and the three divisions behave differently",
    sources=[dict(LUTZ_CH5)],
    concept=(
        "Python has three divisions and the difference between them is the first thing that "
        "makes numeric code behave unexpectedly. True division, written with a single slash, "
        "always returns a float, even when both operands are integers and the result is "
        "whole. Floor division, the double slash, discards the fractional part, and it floors "
        "rather than truncates, so a negative quotient moves further from zero rather than "
        "closer. The modulo operator returns the remainder, and it follows the sign of the "
        "divisor, so the two are consistent: any integer divided and then modded by the same "
        "divisor reconstructs the original. Integers have unlimited precision and never "
        "overflow, while floats are hardware binary approximations, which is why comparing "
        "two floats for equality is unreliable and a small tolerance is used instead. Mixed "
        "arithmetic promotes upward to the wider type, so an integer plus a float is a float. "
        "Choosing the right division, and knowing which result type each one produces, is "
        "what keeps a numeric script from accumulating small errors that only appear later in "
        "the output."
    ),
    prerequisites=["canonical:object-type-categories"],
    pitfalls=[
        "Using / for whole-item arithmetic and passing the resulting float where an integer "
        "index or count is required.",
        "Assuming // rounds toward zero, so a negative quotient comes back one lower than "
        "expected.",
        "Comparing two floats with == after arithmetic and getting False for two values that "
        "print identically.",
    ],
    adapters={
        "machine-learning": {
            "framing": (
                "Feature scaling is division applied to a column, and the choice of division "
                "decides whether the result is a clean fraction or a value that must be "
                "converted back before it is used as an index."
            ),
            "application": (
                "Walk the example as a normalisation step. The range is found with min and max, "
                "and each value is scaled by true division, which always yields a float, so the "
                "scaled features are fractions between zero and one. The count of buckets, by "
                "contrast, uses floor division, because a bucket number has to be a whole "
                "integer to be usable as a position. Notice that mixing the two would be "
                "silent: true division on evenly divisible values still returns a float, so the "
                "code would keep running and only break when the float reached a place "
                "expecting an index. When a scaled value looks wrong, the first thing to check "
                "is which division produced it, because the operator, not the inputs, sets the "
                "result's type."
            ),
            "example_hint": "scale features with true division and derive bucket numbers with floor division",
            "assessment_angle": "which division produces a float and which an integer, and why that matters for indices",
            "day": DAY,
            "title": "Scale with One Slash, Bucket with Two: Division Picks the Result Type",
            "code": """values = [4, 9, 15, 22, 30]
lo, hi = min(values), max(values)

scaled = [(v - lo) / (hi - lo) for v in values]     # true division -> floats
print("scaled:", [round(s, 3) for s in scaled])

bucket_size = 10
buckets = [(v - lo) // bucket_size for v in values]  # floor division -> ints
print("buckets:", buckets)
print("bucket count:", max(buckets) + 1)
""",
            "questions": [
                "Why is scaled a list of floats even though every input value and both range bounds are integers?",
                "What do the two floor-division results for 15 and 22 tell you about how the buckets were counted?",
                "A bucket number is later used to index a list. Why would true division be wrong there even when it divides evenly?",
            ],
            "answers": [
                "Because true division always returns a float in Python 3, regardless of the operand types, and scaling used that operator.",
                "Both fall in the range 11 to 20, so floor division by the bucket size gives 1 for each, showing the quotient is floored to a whole bucket index.",
                "True division returns a float even for exact results, and a float cannot be used as a list index, so it would raise a TypeError at that point.",
            ],
            "homework": (
                "Write feature_scaling.py that starts from a list of at least six integer values. "
                "Print the min-max scaled value of each one using true division, rounded to three "
                "places, and the bucket number of each one using floor division with a bucket size of "
                "your choosing. Then print the number of distinct buckets used and one scaled value "
                "multiplied by an integer, showing the result stays a float. Observable output: four "
                "lines showing the scaled list, the bucket list, the bucket count and the product."
            ),
            "required_patterns": ["min(", "max(", "//", "/]", "print("],
        },
        "data-viz": {
            "framing": (
                "A plot is drawn on a pixel grid, so chart coordinates are computed as whole "
                "numbers while the data values they label are floats. Confusing the two is "
                "what puts a tick in the wrong place by less than a pixel and makes the whole "
                "axis look slightly off."
            ),
            "application": (
                "Walk the example as an axis being drawn. The data range is mapped onto the "
                "available width, and the mapping is the interesting part: multiplying a "
                "fraction by the pixel width gives a float, and converting it with int gives "
                "the whole column the pixel grid needs. The labels, by contrast, keep their "
                "float precision because a reader wants to see the real value. So the same "
                "underlying scale is materialised twice, once as an integer position and once "
                "as a float label, and the only difference between them is the conversion "
                "applied. When a tick lands between two pixels, or a label shows more decimals "
                "than the axis can resolve, the cause is that the two forms were swapped or "
                "mixed."
            ),
            "example_hint": "map a data range onto pixel columns as integers while keeping float labels",
            "assessment_angle": "why positions are whole numbers and labels stay floats from the same scale",
            "day": DAY,
            "title": "Pixel Columns Are Ints, Tick Labels Are Floats: Split the Scale",
            "code": """series = [0.0, 2.5, 5.0, 7.5, 10.0]
lo, hi = min(series), max(series)
WIDTH, MARGIN = 40, 4

for value in series:
    fraction = (value - lo) / (hi - lo)        # float 0.0 to 1.0
    column = MARGIN + int(fraction * WIDTH)    # integer pixel column
    print(f"{value:5.1f} -> column {column:2d}")
""",
            "questions": [
                "Why is the pixel column computed with int() around the product rather than used directly as a float?",
                "Two adjacent data values differ by 2.5. What changes that difference after mapping to columns, and what introduces the change?",
                "The label prints 7.5 while the column prints a whole number. What single decision in the code created that split?",
            ],
            "answers": [
                "Because the pixel grid is addressed by whole columns, and the mapped position is a float that has to be converted to an integer before it names a column.",
                "The labels stay 2.5 apart, but the column difference is about ten positions after scaling by the width, so multiplication by the width, not the data, sets the spacing.",
                "Using int() on the scaled position for the column while leaving the unconverted value for the label, which keeps the integer and float forms of the same scale separate.",
            ],
            "homework": (
                "Write axis_positions.py that plots a series of at least six float values across a "
                "pixel width of your choosing. For each value print the float label, the fractional "
                "position computed by true division, and the integer column after conversion. Then "
                "print the data range, the column of the minimum value and the column of the maximum "
                "value, and confirm the two endpoints differ by the full width. Observable output: "
                "one line per value plus three summary lines."
            ),
            "required_patterns": ["min(", "max(", "int(", "/ ", "print("],
        },
        "api-building": {
            "framing": (
                "Pagination is arithmetic on three integers: total items, page size and page "
                "number. Getting the page count right is a floor-division problem, and the "
                "edge case is the last page that is only partly full."
            ),
            "application": (
                "Walk the example as a pagination helper. The number of pages is the total "
                "divided by the page size, and because a part-full final page still has to "
                "exist, the total is nudged up by one less than the page size before floor "
                "division. The offset, which is what the database or list slice actually "
                "needs, is the page index times the page size, and it must be an integer to "
                "serve as a slice bound. Notice that true division would break both: the page "
                "count would become a float, and the offset would fail the moment it was used "
                "to slice. The remainder is worth computing too, because it tells you whether "
                "the last page is full, which is what a client needs to decide whether to "
                "offer a next link."
            ),
            "example_hint": "compute page count and offset from three integers with floor division",
            "assessment_angle": "why the page count needs the adjusted dividend and the offset needs an integer",
            "day": DAY,
            "title": "Page Counts and Offsets: Pagination Is Integer Arithmetic",
            "code": """total, per_page, page = 23, 10, 2

page_count = (total + per_page - 1) // per_page     # account for a part-full last page
offset = (page - 1) * per_page                      # integer slice bound
items_here = min(per_page, total - offset)

print(f"pages: {page_count}, offset: {offset}")
print(f"page {page} of {page_count}: {items_here} items")
print("remainder on last page:", total % per_page or per_page)
""",
            "questions": [
                "Why is the total increased by per_page minus one before the floor division, and what would go wrong without it?",
                "The offset is used as a slice bound. Why must it be an integer rather than a float?",
                "What does total % per_page report, and why does the code fall back to per_page when it is zero?",
            ],
            "answers": [
                "Because a part-full final page still counts as a page, and floor division alone would drop it; the adjustment makes any positive remainder round up to one more page.",
                "Because slice bounds must be integers, and true division would return a float even for exact multiples, so the slice would raise a TypeError.",
                "It reports how many items sit on the final page when that page is part full; a zero remainder means the last page is exactly full, so the full page size is the correct count.",
            ],
            "homework": (
                "Write pagination_math.py that models a collection of a chosen total size and a chosen "
                "page size. Print the total page count, and for each page number print its offset and "
                "the number of items it holds, using floor division and the remainder. Include a total "
                "that is not a multiple of the page size so the final page is part full, and print "
                "explicitly which page is the last one. Observable output: one line per page plus a "
                "line naming the final page."
            ),
            "required_patterns": ["//", "%", "min(", "*", "print("],
        },
        "web-scraping": {
            "framing": (
                "A scrape reports aggregate statistics, and averaging is true division. "
                "Whether the average is a float or is floored to a whole number is a "
                "decision, not an accident."
            ),
            "application": (
                "Walk the example as a summary being built after a crawl. The counts of "
                "items per page are summed, and the average uses true division, so it is a "
                "float that may carry decimals a reader does not need. Flooring it is a "
                "separate, deliberate step, and it is worth keeping the raw average around "
                "because flooring loses information that a later comparison may want. The "
                "pages-scraped figure, by contrast, is a whole count, and len keeps it "
                "usable as a divisor. The distinction worth internalising is that the average "
                "is a derived float that represents a rate, while the counts are integers "
                "that represent discrete items, and only the second group should ever be "
                "handed to anything that expects a whole number."
            ),
            "example_hint": "sum scraped counts, average them with true division, keep whole counts separate",
            "assessment_angle": "which scraped figures are rates and which are counts, and what each one's type should be",
            "day": DAY,
            "title": "Averages Are Rates, Counts Are Ints: Report Scraped Stats by Type",
            "code": """counts = [12, 15, 9, 20, 14, 18]
total_items = sum(counts)
pages = len(counts)

average = total_items / pages                    # true division -> float
whole_average = total_items // pages             # floor division -> int

print(f"pages scraped: {pages}")
print(f"total items: {total_items}, average: {average:.2f}")
print(f"floored average: {whole_average}")
print("items in fullest page:", max(counts))
""",
            "questions": [
                "Why does average come out as a float while whole_average is an integer, when both divide the same two integers?",
                "What information is lost by reporting whole_average instead of average, and when would that matter?",
                "max(counts) is used as a headline figure. Why is it safe to treat as an integer when average is not?",
            ],
            "answers": [
                "Because the operators differ: true division always returns a float, while floor division returns an integer when both operands are integers.",
                "The fractional part of the rate is dropped, which matters whenever the average is compared against a threshold or multiplied by a page count later.",
                "Because it is an observed count of discrete items taken straight from the data, not a quotient, so it is an integer by construction.",
            ],
            "homework": (
                "Write scrape_stats.py that holds item counts for at least seven pages. Print the "
                "number of pages, the total items, the average items per page to two decimals, the "
                "floored average, and the fullest page's count. Then compute and print the difference "
                "between the true average and the floored one, to show what the floor division "
                "discarded. Observable output: six lines distinguishing the rate from the counts."
            ),
            "required_patterns": ["sum(", "len(", "/ ", "//", "print("],
        },
        "testing-qa": {
            "framing": (
                "Float results cannot be asserted equal, they have to be asserted close. A "
                "test suite that compares computed numbers with == passes locally and fails "
                "on a different platform for no visible reason."
            ),
            "application": (
                "Walk the example as a suite asserting on numeric output. The first assertion "
                "compares two floats computed by different routes, and comparing them with "
                "equality fails because the two arrive with tiny differences from the "
                "approximation. The fix is a tolerance: the absolute difference is compared "
                "against a small epsilon, which is how every numeric assertion should be "
                "written. The second assertion, on an integer count, uses equality safely, "
                "because an integer is exact. The lesson is to classify the expected value "
                "before choosing the comparison: integers are asserted exactly, floats are "
                "asserted within a tolerance, and mixing the two is what produces the flaky "
                "test that fails once a month and nobody can reproduce."
            ),
            "example_hint": "assert floats within a tolerance and integers exactly",
            "assessment_angle": "why the float assertion needs a tolerance and the integer one does not",
            "day": DAY,
            "title": "Assert Integers Exactly, Floats Within a Tolerance",
            "code": """def close_to(actual, expected, epsilon=1e-9):
    return abs(actual - expected) < epsilon

computed = 0.1 + 0.2
print("literal sum prints as:", computed)
print("== comparison:", computed == 0.3)
print("tolerance comparison:", close_to(computed, 0.3))

count = 10 // 3 + 10 % 3
print("integer count is exact:", count == 13)
""",
            "questions": [
                "Why does computed == 0.3 print False when computed itself prints as 0.3?",
                "What does close_to actually compare, and why is a small epsilon used instead of zero?",
                "The integer assertion uses == without a tolerance. What property of integers makes that safe?",
            ],
            "answers": [
                "Because the float sum is a binary approximation that differs from 0.3 in a low-order bit, and printing rounds the display while == compares the underlying values.",
                "It compares the absolute difference against a small epsilon, which treats two values as equal when their gap is below a threshold the approximation cannot reach.",
                "Integers are exact and unbounded in Python, so a computed integer is the precise value it claims to be and needs no tolerance.",
            ],
            "homework": (
                "Write numeric_assertions.py with a close_to(actual, expected, epsilon) function and at "
                "least four assertions: two on float sums that require the tolerance and two on "
                "integer results computed with floor division and modulo. Print each assertion's "
                "actual value, its expected value and whether it passed. Include one float case where "
                "the difference clearly exceeds a tight epsilon so a deliberate failure appears. "
                "Observable output: one line per assertion, naming pass or fail."
            ),
            "required_patterns": ["abs(", "def ", "//", "%", "print("],
        },
        "devops-scripting": {
            "framing": (
                "Everything an ops script reports is a byte count, and humans want units. "
                "Converting bytes to gibibytes is floor division, and the remainder is the "
                "part of the number that does not fit a whole unit."
            ),
            "application": (
                "Walk the example as a disk report being formatted. Dividing the byte count "
                "by the unit with true division would give a float, which is why the code "
                "uses floor division and reports whole gibibytes. The remainder from modulo "
                "is not waste; it is the precise leftover that distinguishes two disks that "
                "both report as one gibibyte, and printing it is what makes the report "
                "useful for capacity planning. The two operators are consistent by design, "
                "so dividing and modding by the same unit reconstructs the original count. "
                "When a report rounds a disk up and a later alert says it is nearly full, "
                "the cause is usually that true division was used where a whole unit was "
                "needed, and the alert compared the rounded figure."
            ),
            "example_hint": "convert byte counts to whole units with floor division and report the remainder",
            "assessment_angle": "why whole units use floor division and what the remainder contributes",
            "day": DAY,
            "title": "Bytes to Gibibytes: Whole Units by Floor, Leftover by Modulo",
            "code": """GiB = 1024 ** 3
disks = {"root": 5368709120, "data": 3221225472, "scratch": 1073741824}

for name, byte_count in disks.items():
    whole = byte_count // GiB                    # whole gibibytes
    leftover = byte_count % GiB                  # bytes that do not fill a unit
    print(f"{name}: {whole} GiB + {leftover} bytes")

total = sum(disks.values())
print(f"total: {total // GiB} GiB, float view: {total / GiB:.2f}")
""",
            "questions": [
                "Why does the report print whole gibibytes rather than the float form, and where is the float form still shown?",
                "What does the leftover tell you that the whole unit figure alone does not?",
                "The last line shows both divisions of the same total. What does the comparison reveal about each one's purpose?",
            ],
            "answers": [
                "Because disk units are reported as whole gibibytes for capacity planning, and the code uses floor division for that; the float form is still shown once, to express the same size as a fractional quantity.",
                "It gives the exact bytes that do not fill a complete unit, which distinguishes two disks that both round to the same whole gibibyte and reveals how much room is really unused.",
                "That floor division reports whole usable units while true division reports the size as a continuous quantity, so the first is for counting units and the second is for expressing a size.",
            ],
            "homework": (
                "Write disk_report.py that holds byte counts for at least four mounts. For each one "
                "print the whole gibibytes and the leftover bytes, using floor division and modulo by "
                "1024 cubed. Then print the fleet total three ways: whole gibibytes, the float form "
                "to two decimals, and the sum of all leftover bytes. Observable output: one line per "
                "mount plus three total lines, each showing a different numeric representation."
            ),
            "required_patterns": ["//", "%", "**", "/ ", "print("],
        },
        "algo-trading": {
            "framing": (
                "A budget buys whole shares, never a fraction of one. Position sizing is "
                "floor division, and the unspent cash is what remains, and both figures have "
                "to appear in the order ticket."
            ),
            "application": (
                "Walk the example as an order being sized. The affordable share count is the "
                "budget divided by the price using floor division, because a partial share "
                "cannot be bought, and the leftover cash is the same two values under "
                "subtraction after multiplying the share count back. The average fill price, "
                "by contrast, is true division, because it is a rate that legitimately "
                "carries decimals and is what a performance report needs. Notice that the "
                "three results come from two operands and three operators, and that using "
                "true division for the share count would silently produce a float that looks "
                "correct until it is sent as a quantity. Position sizing is where the choice "
                "of division becomes a property of the order rather than a stylistic "
                "preference."
            ),
            "example_hint": "size a whole-share position with floor division and track leftover cash",
            "assessment_angle": "why share counts are integers while an average price is a float",
            "day": DAY,
            "title": "Whole Shares, Leftover Cash: Size a Position with the Right Division",
            "code": """budget = 10000
price = 37.5

shares = int(budget // price)          # whole shares only
spent = shares * price
leftover = budget - spent

print(f"shares: {shares}")
print(f"spent: {spent:.2f}, leftover: {leftover:.2f}")

fills = [37.40, 37.55, 37.48]
avg = sum(fills) / len(fills)          # a rate, so true division
print(f"average fill: {avg:.4f}")
""",
            "questions": [
                "Why is the share count produced by floor division instead of true division, even though the price is a float?",
                "What does the leftover cash represent, and why is it computed by subtraction after multiplying back?",
                "The average fill price uses true division over three float prices. What kind of quantity is it, and why does that justify the operator?",
            ],
            "answers": [
                "Because shares are discrete and only whole ones can be bought, so the quotient has to be floored to an integer; true division would return a fractional share count.",
                "The part of the budget that could not buy a further whole share, computed by multiplying the whole share count back by the price to find what was actually spent.",
                "It is a rate, an average price per share, which is a continuous quantity that legitimately carries decimals rather than a count of discrete items.",
            ],
            "homework": (
                "Write position_sizing.py that takes a budget and a share price, then prints the whole "
                "number of shares affordable, the amount spent and the cash left over. Repeat the "
                "sizing for at least three different prices and print each result, then compute and "
                "print the average of the three leftover amounts using true division. Observable "
                "output: one block per price plus the final average line, with every whole-share "
                "figure shown without decimals and every rate shown with them."
            ),
            "required_patterns": ["//", "int(", "len(", "/ ", "print("],
        },
        "numerical-methods": {
            "framing": (
                "Grid cells are indexed by whole numbers while the quantities inside them are "
                "floats. Converting a continuous coordinate to a cell index is the whole of "
                "discretisation, and it is a conversion, not a computation."
            ),
            "application": (
                "Walk the example as a continuous domain being discretised. A coordinate in "
                "the interval zero to one is mapped to a cell index by multiplying by the "
                "number of cells and taking the whole part, and the conversion is what makes "
                "the result a usable index. The coordinate itself stays a float, and printing "
                "both side by side shows the discretisation: many different floats fall into "
                "the same integer cell. That is the source of both the method's speed and its "
                "error, because the cell index loses the position within the cell, and a "
                "refinement study is precisely the act of increasing the cell count and "
                "watching the integer grid approach the continuous truth. The distance into "
                "the cell is sometimes as valuable as the index, and it is available by "
                "subtracting the whole part from the scaled coordinate."
            ),
            "example_hint": "map continuous coordinates to whole cell indices and keep the within-cell offset",
            "assessment_angle": "what the cell index discards about the coordinate and what the offset preserves",
            "day": DAY,
            "title": "Discretise a Domain: Continuous Coordinate, Integer Cell",
            "code": """CELLS = 5
coords = [0.03, 0.21, 0.41, 0.62, 0.79, 0.97]

for c in coords:
    scaled = c * CELLS
    index = int(scaled)                # whole cell containing the coordinate
    into = scaled - index              # position within the cell
    print(f"{c:.2f} -> cell {index}, {into:.2f} into the cell")

h = 1.0 / CELLS                        # cell width is a float
print(f"cell width: {h}, cells: {CELLS}")
""",
            "questions": [
                "Why does the mapping convert the scaled coordinate to a whole number rather than keeping it as a float?",
                "Two coordinates fall into the same cell. What distinguishes them, and where is that distinguishing information stored?",
                "The cell width is computed with true division. What would change about the grid if floor division were used there instead?",
            ],
            "answers": [
                "Because a cell index has to be a whole number to select one element of the grid, and the scaled coordinate is a float that names a position, not a cell.",
                "Their positions within the cell differ, and that distance is stored in the offset computed by subtracting the whole index from the scaled coordinate.",
                "It would report a whole number of cells per unit, which is one, and lose the actual cell width, so the grid's resolution would no longer be recoverable from it.",
            ],
            "homework": (
                "Write discretise.py that defines a cell count and a list of at least six float "
                "coordinates between zero and one. For each one print the coordinate, the whole cell "
                "index that contains it and its distance into that cell. Then double the cell count "
                "and print the new index of the same coordinates, showing how the finer grid "
                "separates values that shared a cell. Observable output: one line per coordinate in "
                "each grid, plus a line stating the two cell widths."
            ),
            "required_patterns": ["int(", "* ", "- ", "/ ", "print("],
        },
    },
)
