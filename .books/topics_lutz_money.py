"""Canonical topic batch: numeric accuracy and money (Lutz ch 5 precision)."""
from canonical_topics import topic

LUTZ_CH5_PRECISION = {
    "book": "learning-python",
    "chapter": 5,
    "pages": [105, 142],
    "sections": ["Decimal Type", "Fraction Type", "Numeric accuracy"],
}


topic(
    "canonical:numeric-accuracy-money",
    "A float cannot represent most decimal fractions exactly, so money and other exact quantities need a decimal type that is set up deliberately",
    sources=[dict(LUTZ_CH5_PRECISION)],
    concept=(
        "Floating point stores numbers in binary, and most everyday decimal fractions, "
        "including the prices and percentages a program works with every day, have no exact "
        "binary representation. The result is that adding and subtracting money with floats "
        "leaves tiny residuals that are invisible when printed but decisive when compared or "
        "accumulated. The Decimal type exists for exactly this case: it represents decimal "
        "fractions exactly, so point one plus point two equals point three and a running "
        "total of many small values stays correct to the last cent. Using it well is a matter "
        "of discipline rather than difficulty. The value has to be constructed from a "
        "string rather than from a float, because the float is already inexact by the time "
        "the constructor sees it. The precision has to be decided once and applied "
        "consistently, since mixing contexts produces different numbers of digits in "
        "different parts of the program. And rounding has to be chosen explicitly for the "
        "domain, because the default is not always the banker's or trader's rule the "
        "business expects. Decimal is slower than float and more verbose, so it belongs "
        "where exactness matters, not as a universal replacement. The Fraction type answers "
        "a different question exactly, the ratio of two integers, and is the right tool when "
        "a computation must stay exact through several steps of division."
    ),
    prerequisites=["canonical:numbers-and-precision"],
    pitfalls=[
        "Constructing a Decimal from a float instead of a string, which imports the "
        "inexactness the type was chosen to avoid.",
        "Comparing two floats for equality, or against a literal, and relying on the "
        "residual being absent.",
        "Mixing float and Decimal operands in one expression, which raises instead of "
        "silently converting, and signals that a boundary has been crossed without thought.",
    ],
    adapters={
        "machine-learning": {
            "framing": (
                "Probabilities and losses live in floats, but when a metric is reported as a "
                "percentage or a score has to be compared to a threshold, display rounding "
                "and exact comparison are different problems."
            ),
            "application": (
                "Walk the example as a threshold check being made safe. A model's aggregated "
                "score is compared against a cutoff, and the direct equality test fails not "
                "because the model is wrong but because the float has a residual, so the "
                "check is rewritten as a distance from the threshold. That distinction is "
                "the transferable skill: floats are for computation and comparison within a "
                "tolerance, never for equality. The second half shows why the display is a "
                "separate concern: the same score is shown rounded for a reader, and "
                "rounding it for display would break the threshold check if it were applied "
                "to the stored value. Keeping the exact value for logic and the rounded "
                "value only for output is the pattern, and it is the same one used for "
                "money elsewhere."
            ),
            "example_hint": "compare a score to a threshold within a tolerance and round only the display",
            "assessment_angle": "why equality fails on floats and how display rounding differs from stored precision",
            "day": 8,
            "title": "Tolerate the Residual: Compare Within, Round Only the Display",
            "code": """from decimal import Decimal, ROUND_HALF_UP

THRESHOLD = 0.6
score = 0.1 + 0.2 + 0.3        # intended 0.6

print("direct equality:", score == THRESHOLD)
print("raw score:", score)

within = abs(score - THRESHOLD) < 1e-9
print("within tolerance:", within)

shown = Decimal(str(score)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
print("reported:", shown)
""",
            "questions": [
                "Why does the direct equality test print false when three scores of one, two and three tenths were meant to total six tenths?",
                "What does the tolerance check replace, and why is it the correct way to compare two floats?",
                "The score is quantised to two places for the report. Why is that done on a display copy rather than on the stored value?",
            ],
            "answers": [
                "Because none of 0.1, 0.2 and 0.3 has an exact binary representation, so adding them accumulates a residual and the total lands just beside 0.6 instead of on it.",
                "It replaces equality with a distance check, which is correct because float residuals are expected, so the question is whether two values are close enough rather than identical.",
                "Because rounding for display is a presentation choice, and applying it to the stored value would discard precision that the threshold check depends on.",
            ],
            "homework": (
                "Write tolerance_check.py with a threshold and a score built by summing decimal "
                "fractions that have no exact binary form. Print the direct equality result, the "
                "raw score with its residual, a within-tolerance check against the threshold, and "
                "a report copy quantised to two decimal places using the rounding mode of your "
                "choice. Then repeat for a second score that does reach the threshold to show the "
                "check accepts it. Observable output: eight lines, with the raw scores showing "
                "their residuals."
            ),
            "required_patterns": ["abs(", "Decimal(", ".quantize(", "ROUND_", "print("],
        },
        "data-viz": {
            "framing": (
                "A chart that rounds its own values before plotting can hide the very "
                "difference it was drawn to show, so the display scale and the data scale "
                "have to stay separate."
            ),
            "application": (
                "Walk the example as two series being compared on one axis. The values are "
                "computed in floats and the axis is labelled in a rounded scale, but the "
                "series themselves are stored unrounded so the visual gap is faithful. The "
                "useful comparison is between building a tick label, which is formatting "
                "applied to a copy, and clamping the data to that scale, which would move "
                "the points and could merge two distinguishable series into one. Decimal "
                "appears when a label has to be exact, for example a currency axis where the "
                "tick must read a whole cent and not its nearest binary approximation. The "
                "discipline generalises: whatever a chart draws is the data, whatever it "
                "prints is presentation, and only one of those should ever be rounded."
            ),
            "example_hint": "label the axis in a rounded scale while keeping the series unrounded",
            "assessment_angle": "which of the two scales may be rounded and what clamping would cost",
            "day": 8,
            "title": "Round the Axis Labels, Never the Series",
            "code": """from decimal import Decimal

series_a = [0.10, 0.25, 0.50, 0.75]
series_b = [0.11, 0.24, 0.49, 0.74]

print("distinct at full precision:", len(set(series_a + series_b)))

ticks = [Decimal(str(v)).quantize(Decimal("0.1")) for v in (0.0, 0.5, 1.0)]
print("axis ticks:", [str(t) for t in ticks])

for a, b in zip(series_a, series_b):
    print(f"a {a:.2f}  b {b:.2f}  gap {abs(a - b):.4f}")
""",
            "questions": [
                "The two series differ by a hundredth at each point. What would happen to that difference if the values were rounded to one place before plotting?",
                "Why is each axis tick built from a string with Decimal rather than from the float directly?",
                "Which of the two scales in this example is allowed to be rounded, and why does the other have to stay exact?",
            ],
            "answers": [
                "The rounding would collapse each pair to the same value, so the visual gap between the series would disappear even though the underlying data still differs.",
                "Because the float is already an inexact binary value, so building the Decimal from it would import the residual, while the string carries the intended decimal digits.",
                "The axis labels, which are presentation and may be rounded for readability; the series values must stay exact because they are what the chart actually shows.",
            ],
            "homework": (
                "Write axis_scales.py with two lists of at least six float values differing by "
                "small amounts. Print how many distinct values exist across both series at full "
                "precision, then build three axis tick labels in Decimal from strings and print "
                "them, and finally print each pair of values with the absolute gap to four decimal "
                "places. Observable output: a tick line, a distinct count line, and one line per "
                "pair."
            ),
            "required_patterns": ["Decimal(", "abs(", "zip(", "set(", "print("],
        },
        "api-building": {
            "framing": (
                "A payments or pricing endpoint crosses the exactness boundary in both "
                "directions: a request carries a price as text, the computation is decimal, "
                "and the response has to come back unchanged in meaning."
            ),
            "application": (
                "Walk the example as a price being accepted and totalled. The request "
                "supplies the amount as a string, which is the right shape because a price "
                "sent as a float is already inexact before the server reads it, so the "
                "endpoint constructs a Decimal from that text and the exactness is "
                "preserved from the boundary inward. The total is then the sum of several "
                "such values with no residual, which is what money requires. Two things are "
                "worth noticing. The response is serialised back to text, because a round "
                "trip through a float would undo the whole point. And mixing a Decimal with "
                "a float raises, which is a feature rather than a nuisance: it marks the "
                "exactness boundary so a programmer cannot cross it by accident. Choosing "
                "the rounding mode for a per-item tax line is the domain decision the code "
                "has to make explicit instead of inheriting a default."
            ),
            "example_hint": "accept a price as text, total it in Decimal, serialise back as text",
            "assessment_angle": "why the amount travels as a string and what a mixed-type operation signals",
            "day": 8,
            "title": "Money Crosses the Wire as Text, Computes as Decimal",
            "code": """from decimal import Decimal, ROUND_HALF_UP

request_items = [("book", "12.99"), ("pen", "1.25"), ("notebook", "3.40")]
TAX_RATE = Decimal("0.08")


def total_cart(items):
    lines = []
    subtotal = Decimal("0")
    for name, price_text in items:
        price = Decimal(price_text)          # from text, never from a float
        subtotal += price
        lines.append((name, price))
    tax = (subtotal * TAX_RATE).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return lines, subtotal, tax, subtotal + tax


lines, subtotal, tax, total = total_cart(request_items)
for name, price in lines:
    print(f"{name:<9} {price}")
print(f"{'subtotal':<9} {subtotal}")
print(f"{'tax':<9} {tax}")
print(f"{'total':<9} {total}")
print("response value:", str(total))
""",
            "questions": [
                "Why does the endpoint build the price with Decimal(price_text) instead of Decimal(float(price_text))?",
                "The tax is quantised to two places with an explicit rounding mode. What would happen if no rounding mode were chosen, and why does that matter for money?",
                "The final total is sent back with str(total). What would a round trip through a float cost?",
            ],
            "answers": [
                "Because the text carries the intended decimal digits, whereas a float would already be the nearest binary approximation, importing the residual the type was chosen to avoid.",
                "The default rounding mode would apply, which may not be the rule the business expects for tax, so the per-line amount could differ from the books by a cent or two.",
                "It would re-introduce the inexactness that the decimal computation removed, so the response could show a value that no longer equals the totalled amount.",
            ],
            "homework": (
                "Write cart_total.py with a list of at least five name and price-string pairs and a "
                "tax rate as a Decimal string. Write a total_cart function that builds each price "
                "from the text, sums a subtotal, computes tax quantised to two places with an "
                "explicit rounding mode, and returns the parts and the grand total. Print one line "
                "per item, the subtotal, the tax and the total, and finally the string form of the "
                "total as it would be returned to a caller. Observable output: eight lines or more, "
                "with the total correct to the cent."
            ),
            "required_patterns": ["Decimal(", ".quantize(", "ROUND_", "str(", "print("],
        },
        "web-scraping": {
            "framing": (
                "A scraped price page offers totals and averages that the scraper has to "
                "recompute, and if the page's own total is compared against the scraper's, "
                "float residuals make the comparison look like a bug."
            ),
            "application": (
                "Walk the example as a scraper validating its own arithmetic against the "
                "page. The item prices are collected as text, which is the honest form "
                "because a price on a page is decimal text, and the scraper totals them in "
                "Decimal so its own total is exact. The page's stated total is then compared "
                "against the computed one, and the comparison is meaningful only if both "
                "sides are exact, because a residual of a fraction of a cent would otherwise "
                "read as a miscounted scrape. That is the practical reason the type matters "
                "here: it converts a suspicious mismatch into a real signal, so a "
                "discrepancy means the page actually disagrees with its own items and is "
                "worth reporting. Building the average as a Decimal division with a chosen "
                "precision is the same discipline applied to a derived figure."
            ),
            "example_hint": "collect prices as text, total in Decimal, compare against the page's stated total",
            "assessment_angle": "what exactness contributes to validating scraped totals",
            "day": 8,
            "title": "Recompute the Page's Total and Compare It Exactly",
            "code": """from decimal import Decimal, ROUND_HALF_UP

scraped_prices = ["12.99", "8.50", "3.40", "24.95"]
page_states_total = "49.84"

computed = sum((Decimal(p) for p in scraped_prices), Decimal("0"))
stated = Decimal(page_states_total)
average = (computed / len(scraped_prices)).quantize(
    Decimal("0.01"), rounding=ROUND_HALF_UP
)

print(f"items:    {len(scraped_prices)}")
print(f"computed: {computed}")
print(f"stated:   {stated}")
print(f"matches:  {computed == stated}")
print(f"average:  {average}")
""",
            "questions": [
                "Why are the prices collected as strings and totalled in Decimal rather than summed as floats?",
                "What does a false from the matches line mean, as opposed to a float comparison that drifts by a tiny amount?",
                "The average is quantised to two places after the division. Why is the rounding applied to a derived figure rather than built into the total?",
            ],
            "answers": [
                "Because the page's prices are decimal text, and summing them as floats would introduce residuals, so the total would not match the page's stated figure even when the scrape is correct.",
                "It means the page genuinely disagrees with its own item prices, a real discrepancy worth reporting, rather than an artifact of binary arithmetic.",
                "Because the total must stay exact for the comparison while the average is a derived figure shown to a reader, so only the presentation value is rounded.",
            ],
            "homework": (
                "Write validate_totals.py with a list of at least six prices as strings and a "
                "stated total as a string that does not match the items. Compute the total in "
                "Decimal from the strings, compare it to the stated total, compute the average "
                "quantised to two places with an explicit rounding mode, and print the item count, "
                "the computed total, the stated total, whether they match and the average. "
                "Observable output: five lines, with the mismatch reported as a real discrepancy."
            ),
            "required_patterns": ["Decimal(", "sum(", "ROUND_", "==", "print("],
        },
        "testing-qa": {
            "framing": (
                "A test that asserts money equals money has to be exact, and a test that "
                "asserts on floats has to be tolerant. Choosing the wrong one for the "
                "situation is the defect."
            ),
            "application": (
                "Walk the example as two assertions written side by side. The money "
                "assertion compares two Decimals with equality, which is exactly right "
                "because a Decimal is exact and a residual would indicate a real bug. The "
                "float assertion compares two scores with a tolerance, because the "
                "residual is inherent and an equality assertion would fail spuriously. The "
                "skill being exercised is telling the two cases apart, and the test suite "
                "is where that decision has to be made explicitly for every comparison, "
                "since a silent float equality assertion is a test that will fail one day "
                "for no reason and erode trust in the suite. Building a helper for each "
                "case is what keeps the intent visible at the call site, and it is the "
                "reason both assertions exist rather than one tolerant check used "
                "everywhere."
            ),
            "example_hint": "assert money exactly and floats within a tolerance, with a helper for each",
            "assessment_angle": "which comparison belongs to which type and what a wrong choice costs",
            "day": 8,
            "title": "Assert Money Exactly, Assert Floats Within a Tolerance",
            "code": """from decimal import Decimal


def assert_money(actual, expected):
    if actual != expected:
        raise AssertionError(f"money mismatch: {actual} != {expected}")
    return True


def assert_close(actual, expected, tolerance=1e-9):
    if abs(actual - expected) > tolerance:
        raise AssertionError(f"float {actual} not within {tolerance} of {expected}")
    return True


total = Decimal("12.99") + Decimal("3.40") + Decimal("8.50")
print("money exact:", assert_money(total, Decimal("24.89")))

score = 0.1 + 0.2
print("float close:", assert_close(score, 0.3))

try:
    assert_close(0.1, 0.2)
except AssertionError as exc:
    print("caught:", exc)
""",
            "questions": [
                "Why is equality acceptable in the money assertion and unacceptable in the float assertion?",
                "What does the tolerance argument buy a test suite that a plain equality helper would not?",
                "The float helper raises with both values in the message. Why is that more useful than a bare failure?",
            ],
            "answers": [
                "Because a Decimal is exact so a mismatch is a real bug, while a float carries an inherent residual so equality would fail spuriously on values that are meant to be equal.",
                "It lets each comparison state how close is close enough for its own domain, instead of forcing one universal rule onto every kind of number.",
                "Because the two values are the evidence needed to judge the failure, so naming them turns an opaque failure into one that can be triaged immediately.",
            ],
            "homework": (
                "Write assert_helpers.py with an assert_money helper using equality on Decimals and "
                "an assert_close helper using a tolerance on floats. Verify at least three exact "
                "money sums, at least three float sums that are only equal within a tolerance, and "
                "deliberately trigger one float failure to show the message. Observable output: "
                "seven lines or more, including the caught failure naming both values."
            ),
            "required_patterns": ["Decimal(", "abs(", "AssertionError", "raise", "print("],
        },
        "devops-scripting": {
            "framing": (
                "Quotas, billing and capacity figures are money or near-money, and a "
                "script that reports a monthly cost has to total it exactly rather than "
                "approximately."
            ),
            "application": (
                "Walk the example as a monthly cost report being assembled. Each line is a "
                "service with a cost as text, and the report totals them in Decimal so the "
                "sum across many small values has no residual, because a budget alert that "
                "fires a hundredth of a unit early or late is a false alarm either way. The "
                "share of the budget consumed is computed as a Decimal division and shown "
                "as a percentage, which is where the derived figure gets its own precision. "
                "What transfers to other scripts is the habit of treating any figure that "
                "will be compared against a limit as money: build it from text, total it in "
                "Decimal, and round only the report. The alternative, summing floats and "
                "hoping the residual stays below the alert threshold, is exactly how a "
                "quota check becomes intermittently wrong."
            ),
            "example_hint": "total service costs in Decimal and compare against a budget limit",
            "assessment_angle": "why a limit comparison has to be exact and what the residual would cost",
            "day": 8,
            "title": "Total the Bill Exactly Before You Compare It to the Budget",
            "code": """from decimal import Decimal, ROUND_HALF_UP

BUDGET = Decimal("1000.00")
services = [("compute", "412.75"), ("storage", "88.40"), ("network", "31.10")]

spent = sum((Decimal(cost) for _, cost in services), Decimal("0"))
remaining = BUDGET - spent
share = (spent / BUDGET * 100).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)

print(f"services:  {len(services)}")
print(f"spent:     {spent}")
print(f"budget:    {BUDGET}")
print(f"remaining: {remaining}")
print(f"share:     {share}%")
print(f"over:      {spent > BUDGET}")
""",
            "questions": [
                "Why does the over-budget check use a Decimal comparison rather than comparing floats?",
                "What does summing with a starting value of Decimal('0') achieve that summing the strings alone would not?",
                "The share is computed as a percentage and quantised to one place. Why is it acceptable to round this figure while the spent total is not?",
            ],
            "answers": [
                "Because the Decimal total is exact, so the comparison answers a real question about the budget, whereas a float residual could flip the result near the limit.",
                "It gives the sum an exact starting value of the right type, so every addition stays within Decimal instead of starting from an integer or an inexact float.",
                "Because the share is presentation that a reader scans, while the spent total is compared against the budget and therefore has to carry every cent.",
            ],
            "homework": (
                "Write budget_report.py with a budget as a Decimal string and a list of at least "
                "seven services with costs as strings. Total the costs in Decimal, compute the "
                "remaining budget, the share of budget spent quantised to one decimal place, and "
                "whether spending is over budget. Print the service count, the spend, the budget, "
                "the remainder, the share with a percent sign and the over-budget flag. Observable "
                "output: six lines."
            ),
            "required_patterns": ["Decimal(", "sum(", ".quantize(", "ROUND_", "print("],
        },
        "algo-trading": {
            "framing": (
                "Position sizing, fees and realised profit are money in both directions, "
                "and a residual in the cash account is a reconciliation failure that nobody "
                "will accept as a rounding story."
            ),
            "application": (
                "Walk the example as a round trip in one instrument. A buy and a sell are "
                "recorded with prices and a fee, and the realised profit is computed in "
                "Decimal so that the cash account balances to the cent at the end of the "
                "day. The fee is the figure most often mishandled, because it is small and "
                "multiplied by a quantity, so a float residual that looks negligible on one "
                "trade becomes visible across a thousand. Quantising the fee with an "
                "explicit rounding rule is not decoration here, it is the difference "
                "between a book that reconciles and one that drifts, and the rule has to be "
                "the one the broker actually uses. The remaining cash check at the end is "
                "an equality assertion, and it is only safe to write as equality because "
                "every figure on the way was exact."
            ),
            "example_hint": "compute realised profit on a round trip in Decimal with an explicit fee rule",
            "assessment_angle": "why the fee has to be exact and what makes the final equality check safe",
            "day": 8,
            "title": "Reconcile the Round Trip: Price, Fee, Cash, to the Cent",
            "code": """from decimal import Decimal, ROUND_HALF_UP

FEE_RATE = Decimal("0.0005")
qty = Decimal("100")
buy = Decimal("182.4175")
sell = Decimal("185.9000")


def realised(qty, buy, sell, fee_rate):
    gross = (sell - buy) * qty
    fee = (buy * qty * fee_rate + sell * qty * fee_rate).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )
    return gross, fee, gross - fee


gross, fee, net = realised(qty, buy, sell, FEE_RATE)
print(f"gross:      {gross}")
print(f"fees:       {fee}")
print(f"net:        {net}")
print(f"cash check: {(sell * qty - fee) - (buy * qty) == net}")
""",
            "questions": [
                "Why is the fee quantised with an explicit rounding mode rather than left as the product of the multiplication?",
                "The cash check at the end is an equality assertion. What makes equality safe in this code when it would not be in float code?",
                "The fee is computed on both the buy and the sell notional rather than once on the profit. What does that choice reflect about the domain?",
            ],
            "answers": [
                "Because the raw product has more decimal places than the account records, so the broker's rounding rule decides the exact cent, and leaving it unquantised would make the books unreconcilable.",
                "Because every figure in the computation is a Decimal and therefore exact, so there is no residual to make an equality assertion spuriously fail.",
                "That a fee is charged on each trade's notional value, not on the profit, so both legs of the round trip incur a charge.",
            ],
            "homework": (
                "Write round_trip.py with a fee rate, a quantity and buy and sell prices, all as "
                "Decimal strings or Decimals. Write a realised function that computes the gross "
                "profit, the fees on both legs quantised to two places with an explicit rounding "
                "mode, and the net profit. Print the gross, the fees and the net, then print an "
                "equality check confirming that the cash account reconciles. Repeat with a second "
                "trade whose fee rate differs. Observable output: eight lines, with both "
                "reconciliation checks true."
            ),
            "required_patterns": ["Decimal(", ".quantize(", "ROUND_", "==", "print("],
        },
        "numerical-methods": {
            "framing": (
                "A method that iterates towards an answer has to decide when the change is "
                "genuinely smaller than the noise, and that is a question about precision, "
                "not about effort."
            ),
            "application": (
                "Walk the example as a stopping rule being made trustworthy. The change "
                "between successive approximations is compared against a tolerance, and the "
                "tolerance has to sit above the float's own resolution for the stopping "
                "decision to mean anything, since a tolerance smaller than the residual "
                "makes the loop run forever chasing noise. Decimal answers the opposite "
                "case: when the answer has to be exact, as a rational quantity expressed "
                "exactly, the Fraction type keeps it exact through repeated division where "
                "floats would drift. The transferable insight is that numerical code has "
                "three precisions to keep apart, the method's true accuracy, the "
                "tolerance it stops at, and the display precision it reports, and "
                "confusing them produces either a loop that never ends or a report that "
                "claims accuracy the method never achieved. Naming all three in the output "
                "is what keeps them honest."
            ),
            "example_hint": "separate the method's accuracy, the stopping tolerance and the display precision",
            "assessment_angle": "why the tolerance must exceed the float resolution and what the three precisions are",
            "day": 8,
            "title": "Three Precisions: Accuracy, Tolerance, Display",
            "code": """from decimal import Decimal
from fractions import Fraction

TOLERANCE = Decimal("1e-6")
MACHINE = Decimal(2 ** -52)

print(f"machine resolution: {MACHINE:.3e}")
print(f"stopping tolerance: {TOLERANCE:.3e}")
print(f"tolerance above noise: {TOLERANCE > MACHINE}")

exact = Fraction(1, 10) + Fraction(2, 10)
print(f"exact sum of tenths: {exact} = {float(exact):.10f}")
print(f"float approximation: {0.1 + 0.2:.17f}")
""",
            "questions": [
                "Why must the stopping tolerance be larger than the machine resolution for the loop's decision to be meaningful?",
                "What does the Fraction comparison demonstrate that the float on the next line cannot?",
                "The three quantities in the report are accuracy, tolerance and display precision. Which one decides when to stop, and which one decides what the reader sees?",
            ],
            "answers": [
                "Because below the resolution the computed change is dominated by representation noise, so the loop would chase differences that are not real signal and might never terminate.",
                "That one tenth plus two tenths is exactly three tenths, whereas the float sum carries a residual visible in its final digits.",
                "The tolerance decides when to stop, since it is the threshold the change is judged against, and the display precision decides what the reader sees.",
            ],
            "homework": (
                "Write precisions.py that defines a stopping tolerance and the machine resolution as "
                "Decimals and prints both in scientific notation along with whether the tolerance "
                "sits above the noise. Then build at least four exact rational sums with Fraction, "
                "print each as an exact fraction and as a float to ten places, and beside each "
                "print the same sum computed in floats to seventeen places to expose the residual. "
                "Observable output: three header lines and four comparison pairs."
            ),
            "required_patterns": ["Decimal(", "Fraction(", "float(", "print(", "f\""],
        },
    },
)
