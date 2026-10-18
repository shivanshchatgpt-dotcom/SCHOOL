"""Exercise templates for the five domain blocks of the 180-day tracks.

Each template is one skill expressed as a parameterised problem: value pools to
draw from, a student-facing prompt, a reference solution, and the substrings the
solution's output must contain. `exercise_gen` draws variants, renders both sides
from the same draw, and executes every solution, so a template that drifts out of
sync with its prompt fails here rather than in front of a student.

Solutions use only the standard library. The rest of the corpus already teaches
these ideas in pure Python, and a student must be able to run an exercise
without installing a scientific stack first.
"""
from __future__ import annotations

from app.exercise_gen import ExerciseTemplate

RUBRIC_STD = (
    "Code must run without raising, define at least one function, and print the stated output.",
    "The required constructs must be present so the pattern is actually used, not bypassed.",
    "Changing one input value must change the output in the direction the prompt predicts.",
)

TEMPLATES: tuple[ExerciseTemplate, ...] = (

    # ------------------------------------------------------- Data Workflow
    ExerciseTemplate(
        id="dw-csv-parse",
        skill="Parsing CSV text into records",
        block="Data Workflow",
        prompt=(
            "You are given CSV text with a header row and <<nrows>> data rows. Write a function "
            "`parse(text)` that splits the header from the body and returns a list of dicts, one "
            "per row, keyed by the header names. Print the number of rows parsed and the value of "
            "the `<<key>>` field for the first row. It must print <<nrows>> for the row count."
        ),
        solution='''import csv
import io

TEXT = """name,score,subject
Asha,88,math
Rohan,74,science
Meera,91,math
Kabir,66,science
Ila,79,math"""


def parse(text):
    reader = csv.DictReader(io.StringIO(text))
    rows = [dict(row) for row in reader]
    return reader.fieldnames, rows


def main(text=TEXT, key="score"):
    header, rows = parse(text)
    first = rows[0]
    return header, len(rows), first[key]


header, count, first_value = main()
print('columns:', ','.join(header))
print('rows parsed:', count)
print('first score:', first_value)''',
        required_patterns=("def ", "csv.", "DictReader", "print("),
        rubric=RUBRIC_STD,
        params={"nrows": (4, 5), "key": ("score", "subject", "name")},
        expect=("rows parsed:",),
        n_variants=4,
    ),
    ExerciseTemplate(
        id="dw-select-columns",
        skill="Selecting and renaming columns",
        block="Data Workflow",
        prompt=(
            "Given a list of dicts, write `select(rows, fields)` that returns a new list of dicts "
            "containing only the requested fields, preserving row order. For this run the fields "
            "are <<fields>>. Print the keys of the first result row and the number of rows returned. "
            "It must print <<n>> for the row count."
        ),
        solution='''ROWS = [
    {'name': 'Asha', 'score': 88, 'subject': 'math'},
    {'name': 'Rohan', 'score': 74, 'subject': 'science'},
    {'name': 'Meera', 'score': 91, 'subject': 'math'},
    {'name': 'Kabir', 'score': 66, 'subject': 'science'},
]


def select(rows, fields):
    return [{f: row[f] for f in fields if f in row} for row in rows]


def main(rows=ROWS, fields="<<fields>>"):
    wanted = [f.strip() for f in fields.split(",")]
    out = select(rows, wanted)
    return out, sorted(out[0].keys()), len(out)


out, keys, count = main()
print('kept fields:', ','.join(keys))
print('rows returned:', count)
print('first row:', out[0])''',
        required_patterns=("def ", "for ", "return", "print("),
        rubric=RUBRIC_STD,
        params={
            "fields": ("name,score", "name,subject", "score,subject"),
            "n": (4,),
        },
        expect=("rows returned: 4",),
        n_variants=3,
    ),
    ExerciseTemplate(
        id="dw-filter-threshold",
        skill="Filtering rows by a threshold",
        block="Data Workflow",
        prompt=(
            "Write `above(rows, field, threshold)` returning only the rows whose `<<field>>` is at "
            "least `<<threshold>>`, sorted by that field descending. Print how many rows survived and "
            "the highest value kept. It must print <<kept>> for the count."
        ),
        solution='''ROWS = [
    {'name': 'Asha', 'score': 88},
    {'name': 'Rohan', 'score': 74},
    {'name': 'Meera', 'score': 91},
    {'name': 'Kabir', 'score': 66},
    {'name': 'Ila', 'score': 79},
]


def above(rows, field, threshold):
    kept = [r for r in rows if r[field] >= threshold]
    kept.sort(key=lambda r: r[field], reverse=True)
    return kept


def main(rows=ROWS, field='score', threshold=80):
    kept = above(rows, field, threshold)
    return kept, len(kept), kept[0][field] if kept else None


kept, count, top = main()
print('rows kept:', count)
print('highest kept:', top)
print('names:', ', '.join(r['name'] for r in kept))''',
        required_patterns=("def ", "if ", "sort(", "print("),
        rubric=RUBRIC_STD,
        params={"field": ("score",), "threshold": (75, 80, 85), "kept": (2, 3, 3)},
        expect=("rows kept:",),
        n_variants=4,
    ),
    ExerciseTemplate(
        id="dw-missing-values",
        skill="Detecting and filling missing values",
        block="Data Workflow",
        prompt=(
            "Some records are missing the `<<field>>` field. Write `impute(rows, field, fill)` that "
            "counts the missing values, replaces each with `fill`, and returns the repaired rows "
            "plus the count it replaced. Print the count of values imputed. For this variant the "
            "sentinel you substitute is <<fill>>."
        ),
        solution='''ROWS = [
    {'name': 'Asha', 'score': 88},
    {'name': 'Rohan', 'score': None},
    {'name': 'Meera', 'score': 91},
    {'name': 'Kabir', 'score': None},
]


def impute(rows, field, fill):
    repaired, missing = [], 0
    for row in rows:
        fixed = dict(row)
        if fixed.get(field) is None:
            fixed[field] = fill
            missing += 1
        repaired.append(fixed)
    return repaired, missing


def main(rows=ROWS, field='score', fill=<<fill>>):
    repaired, missing = impute(rows, field, fill)
    return repaired, missing, [r[field] for r in repaired]


repaired, missing, values = main()
print('values imputed:', missing)
print('scores now:', values)''',
        required_patterns=("def ", "is None", "dict(", "print("),
        rubric=RUBRIC_STD,
        params={"field": ("score",), "fill": (0, -1)},
        expect=("values imputed: 2",),
        n_variants=2,
    ),
    ExerciseTemplate(
        id="dw-group-count",
        skill="Grouping rows and counting per group",
        block="Data Workflow",
        prompt=(
            "Write `group_counts(rows, field)` that returns a dict mapping each distinct value of "
            "`<<field>>` to how many rows carry it. Print the counts sorted by group name."
        ),
        solution='''ROWS = [
    {'name': 'Asha', 'subject': 'math'},
    {'name': 'Rohan', 'subject': 'science'},
    {'name': 'Meera', 'subject': 'math'},
    {'name': 'Kabir', 'subject': 'science'},
    {'name': 'Ila', 'subject': 'math'},
]


def group_counts(rows, field):
    counts = {}
    for row in rows:
        key = row[field]
        counts[key] = counts.get(key, 0) + 1
    return counts


def main(rows=ROWS, field='subject'):
    return group_counts(rows, field)


counts = main()
for key in sorted(counts):
    print(f'{key}: {counts[key]}')''',
        required_patterns=("def ", "get(", "for ", "print("),
        rubric=RUBRIC_STD,
        params={"field": ("subject",), },
        expect=("math: 3", "science: 2"),
        n_variants=1,
    ),
    ExerciseTemplate(
        id="dw-merge-tables",
        skill="Merging two tables on a key",
        block="Data Workflow",
        prompt=(
            "You have a `scores` table keyed by `name` and a `classes` table keyed by the same "
            "field. Write `merge(left, right, key)` that returns a new list of dicts combining both "
            "sides, keeping only rows whose key exists in both. Print how many rows were joined and "
            "the joined value for the first name. It must print <<joined>> for the join count. In this "
            "variant Asha and Ila are both in class <<cls>>, and Ila appears in `scores` but not in "
            "`classes`, so the join must drop her."
        ),
        solution='''SCORES = [
    {'name': 'Asha', 'score': 88},
    {'name': 'Rohan', 'score': 74},
    {'name': 'Meera', 'score': 91},
]
CLASSES = [
    {'name': 'Asha', 'class': '<<cls>>'},
    {'name': 'Rohan', 'class': '9B'},
    {'name': 'Ila', 'class': '<<cls>>'},
]


def merge(left, right, key):
    index = {row[key]: row for row in right}
    joined = []
    for row in left:
        if row[key] in index:
            merged = dict(row)
            merged.update(index[row[key]])
            joined.append(merged)
    return joined


def main(left=SCORES, right=CLASSES, key='name'):
    return merge(left, right, key)


joined = main()
print('rows joined:', len(joined))
print('first joined:', joined[0])
print('classes:', ', '.join(r['class'] for r in joined))''',
        required_patterns=("def ", "dict(", "update(", "print("),
        rubric=RUBRIC_STD,
        params={"joined": (2,), "cls": ("9A", "9B")},
        expect=("rows joined: 2",),
        n_variants=2,
    ),

    # ---------------------------------------------------------- Statistics
    ExerciseTemplate(
        id="st-mean-median",
        skill="Mean versus median under an outlier",
        block="Statistics",
        prompt=(
            "Given these values: <<data>>, write `summarise(values)` returning the mean, the median and "
            "the range. Print all three. Then add one very large value, reprint, and observe that "
            "the mean moves while the median barely does. Both summaries must be printed."
        ),
        solution='''def mean(values):
    return sum(values) / len(values)


def median(values):
    ordered = sorted(values)
    mid = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[mid]
    return (ordered[mid - 1] + ordered[mid]) / 2


def summarise(values):
    return mean(values), median(values), max(values) - min(values)


def main(raw="<<data>>"):
    values = tuple(int(v) for v in raw.split(","))
    m, md, rng = summarise(values)
    print(f'before -> mean {m:.2f} median {md:.2f} range {rng}')
    spiked = list(values) + [500]
    m2, md2, rng2 = summarise(spiked)
    print(f'after  -> mean {m2:.2f} median {md2:.2f} range {rng2}')
    print(f'mean moved {m2 - m:+.2f}, median moved {md2 - md:+.2f}')


main()''',
        required_patterns=("def ", "sorted(", "sum(", "print("),
        rubric=RUBRIC_STD,
        params={"data": ("22,24,26,25,23,27", "31,35,33,36,34,38", "8,12,9,14,11,15")},
        expect=("mean", "median", "range"),
        n_variants=3,
    ),
    ExerciseTemplate(
        id="st-variance-stddev",
        skill="Variance and standard deviation",
        block="Statistics",
        prompt=(
            "For the values <<data>>, write `spread(values)` that returns the population variance and "
            "standard deviation, computing the mean first and averaging squared deviations. Print "
            "both. Then print the coefficient of variation, which is the standard deviation divided "
            "by the mean."
        ),
        solution='''def mean(values):
    return sum(values) / len(values)


def variance(values):
    m = mean(values)
    return sum((v - m) ** 2 for v in values) / len(values)


def stddev(values):
    return variance(values) ** 0.5


def coefficient_of_variation(values):
    return stddev(values) / mean(values)


def main(raw="<<data>>"):
    values = tuple(int(v) for v in raw.split(","))
    return variance(values), stddev(values), coefficient_of_variation(values)


values = tuple(int(v) for v in "<<data>>".split(","))


var, sd, cv = main()
_ = values
print(f'variance {var:.4f}')
print(f'stddev   {sd:.4f}')
print(f'cv       {cv:.4f}')''',
        required_patterns=("def ", "** 2", "return", "print("),
        rubric=RUBRIC_STD,
        params={"data": ("12,15,18,21,24", "40,44,41,47,45", "5,9,6,11,7")},
        expect=("variance", "stddev", "cv"),
        n_variants=3,
    ),
    ExerciseTemplate(
        id="st-correlation",
        skill="Correlation between two variables",
        block="Statistics",
        prompt=(
            "Given the observation pairs <<data>> (each entry is `x,y`), write `pearson(xs, ys)` "
            "returning the Pearson "
            "correlation coefficient. Print it, and print a one-word reading: `positive`, "
            "`negative` or `none` based on the sign. A coefficient near 1 must print `positive`."
        ),
        solution='''def mean(values):
    return sum(values) / len(values)


def pearson(xs, ys):
    if len(xs) != len(ys):
        raise ValueError('lengths must match')
    mx, my = mean(xs), mean(ys)
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    dx = sum((x - mx) ** 2 for x in xs) ** 0.5
    dy = sum((y - my) ** 2 for y in ys) ** 0.5
    if dx == 0 or dy == 0:
        return 0.0
    return num / (dx * dy)


def reading(r):
    if r > 0.3:
        return 'positive'
    if r < -0.3:
        return 'negative'
    return 'none'


def main(raw="<<data>>"):
    pairs = [tuple(float(v) for v in part.split(",")) for part in raw.split()]
    xs = [p[0] for p in pairs]
    ys = [p[1] for p in pairs]
    return pearson(xs, ys)


r = main()
print(f'correlation {r:.4f}')
print('reading:', reading(r))''',
        required_patterns=("def ", "zip(", "raise ", "print("),
        rubric=RUBRIC_STD,
        params={"data": ("1,2 2,4 3,6 4,8 5,10",
                        "2,1 4,3 6,5 8,7 10,9",
                        "10,5 20,9 30,14 40,18 50,25")},
        expect=("positive",),
        n_variants=3,
    ),
    ExerciseTemplate(
        id="st-outliers-iqr",
        skill="Finding outliers with the IQR rule",
        block="Statistics",
        prompt=(
            "For the values <<data>>, write `iqr_bounds(values)` returning the lower and upper fence "
            "using the 1.5 times IQR rule, and `find_outliers(values)` returning the values outside "
            "those fences. Print both fences, the outliers, and the mean before and after removing "
            "them."
        ),
        solution='''def quantile(ordered, p):
    if not ordered:
        raise ValueError('empty input')
    idx = p * (len(ordered) - 1)
    low = int(idx)
    high = min(low + 1, len(ordered) - 1)
    return ordered[low] + (ordered[high] - ordered[low]) * (idx - low)


def iqr_bounds(values):
    ordered = sorted(values)
    q1 = quantile(ordered, 0.25)
    q3 = quantile(ordered, 0.75)
    iqr = q3 - q1
    return q1 - 1.5 * iqr, q3 + 1.5 * iqr


def find_outliers(values):
    lo, hi = iqr_bounds(values)
    return [v for v in values if v < lo or v > hi]


def mean(values):
    return sum(values) / len(values)


def main(raw="<<data>>"):
    values = tuple(int(v) for v in raw.split(","))
    lo, hi = iqr_bounds(values)
    out = find_outliers(values)
    kept = [v for v in values if v not in out]
    return lo, hi, out, mean(values), mean(kept)


lo, hi, out, before, after = main()
print(f'fences {lo:.2f} .. {hi:.2f}')
print('outliers:', out)
print(f'mean before {before:.2f} after {after:.2f}')''',
        required_patterns=("def ", "sorted(", "raise ", "print("),
        rubric=RUBRIC_STD,
        params={"data": ("12,14,13,15,12,400,14,13", "30,32,31,33,29,29,900,31", "5,7,6,8,5,4,7,6")},
        expect=("outliers:", "fences"),
        n_variants=3,
    ),
    ExerciseTemplate(
        id="st-confidence-interval",
        skill="A confidence interval from repeated sampling",
        block="Statistics",
        prompt=(
            "Write `bootstrap_ci(values, rounds, seed)` that resamples the values with replacement "
            "using a seeded generator, computes the mean of each resample, and returns the 2.5th "
            "and 97.5th percentiles of those means. Use seed <<seed>> so the answer is reproducible. "
            "Print both bounds."
        ),
        solution='''import random


def mean(values):
    return sum(values) / len(values)


def percentile(ordered, p):
    idx = p * (len(ordered) - 1)
    low = int(idx)
    high = min(low + 1, len(ordered) - 1)
    return ordered[low] + (ordered[high] - ordered[low]) * (idx - low)


def bootstrap_ci(values, rounds=200, seed=7):
    rng = random.Random(seed)
    n = len(values)
    means = []
    for _ in range(rounds):
        sample = [values[rng.randrange(n)] for _ in range(n)]
        means.append(mean(sample))
    means.sort()
    return percentile(means, 0.025), percentile(means, 0.975)


def main(values=(12, 15, 14, 13, 16, 15, 14, 13), seed=7):
    return bootstrap_ci(values, 200, seed)


lo, hi = main()
print(f'95% CI for the mean: {lo:.3f} .. {hi:.3f}')
print('observed mean:', f'{mean((12, 15, 14, 13, 16, 15, 14, 13)):.3f}')''',
        required_patterns=("def ", "random.Random", "range(", "print("),
        rubric=RUBRIC_STD,
        params={"seed": (7, 11, 13)},
        expect=("95% CI",),
        n_variants=3,
    ),

    # ----------------------------------------------------- Visualisation
    ExerciseTemplate(
        id="vz-choose-chart",
        skill="Choosing a chart from the data shape",
        block="Visualization",
        prompt=(
            "Write `choose_chart(x, y)` that returns the chart name for the data's relationship: "
            "`scatter` when both columns are continuous, `bar` when x is a small set of repeated "
            "categories, `line` when x is ordered and continuous. Print the chosen chart for each "
            "of the three cases. The trend case must print `line`."
        ),
        solution='''def choose_chart(x, y):
    if len(set(x)) <= max(3, len(x) // 10):
        return 'bar'
    if x == sorted(x) and len(set(x)) == len(x):
        return 'line'
    return 'scatter'


def main():
    return [
        choose_chart([1.2, 2.4, 3.1, 4.8], [5, 9, 4, 7]),
        choose_chart(['a', 'b', 'a', 'c', 'b', 'a'], [3, 7, 2, 5, 6, 4]),
        choose_chart([1, 2, 3, 4, 5, 6], [2, 4, 5, 8, 9, 12]),
    ]


labels = ['continuous pair', 'repeated categories', 'ordered continuous']
for label, chart in zip(labels, main()):
    print(f'{label:<20} -> {chart}')''',
        required_patterns=("def ", "set(", "if ", "print("),
        rubric=RUBRIC_STD,
        params={},
        expect=("-> line",),
        n_variants=1,
    ),
    ExerciseTemplate(
        id="vz-axis-labels",
        skill="Labelling axes so the chart is readable",
        block="Visualization",
        prompt=(
            "Write `axis_labels(chart)` returning the x-axis label, the y-axis label and the title "
            "for a named chart, and print all three on separate lines. Produce the labels for the "
            "<<chart>> chart. The `line` chart must print `time (s)` as its x label."
        ),
        solution='''LABELS = {
    'line': ('time (s)', 'value', 'Value over Time'),
    'bar': ('category', 'count', 'Count per Category'),
    'scatter': ('x', 'y', 'Relationship between x and y'),
}


def axis_labels(chart):
    if chart not in LABELS:
        raise ValueError(f'unknown chart: <<chart>>')
    return LABELS[chart]


def main(chart="<<chart>>"):
    return axis_labels(chart)


for chart in ("<<chart>>",):
    x, y, title = axis_labels(chart)
    print(f'chart    <<chart>>')
    print(f'  x label {x}')
    print(f'  y label {y}')
    print(f'  title   {title}')''',
        required_patterns=("def ", "if ", "raise ", "print("),
        rubric=RUBRIC_STD,
        params={"chart": ("line", "bar")},
        expect=("chart", "x label"),
        n_variants=2,
    ),
    ExerciseTemplate(
        id="vz-bucket-histogram",
        skill="Bucketing values into a histogram",
        block="Visualization",
        prompt=(
            "Write `histogram(values, buckets)` that splits the value range into equal-width buckets "
            "and returns a list of counts. Print each bucket's range and count. With <<buckets>> "
            "buckets over the given data, the counts must sum to the number of values."
        ),
        solution='''def histogram(values, buckets):
    lo, hi = min(values), max(values)
    if hi == lo:
        return [len(values)] + [0] * (buckets - 1)
    width = (hi - lo) / buckets
    counts = [0] * buckets
    for v in values:
        idx = int((v - lo) / width)
        if idx == buckets:
            idx = buckets - 1
        counts[idx] += 1
    return counts


def main(values=(1, 2, 2, 3, 3, 3, 4, 4, 5, 5, 5, 5), buckets=4):
    return histogram(list(values), buckets)


data = (1, 2, 2, 3, 3, 3, 4, 4, 5, 5, 5, 5)
counts = main(data, 4)
lo, hi = min(data), max(data)
width = (hi - lo) / 4
for i, c in enumerate(counts):
    print(f'[{lo + i * width:.2f}, {lo + (i + 1) * width:.2f}) -> {c}')
print('total counted:', sum(counts))''',
        required_patterns=("def ", "range(", "for ", "print("),
        rubric=RUBRIC_STD,
        params={"buckets": (4, 5, 6)},
        expect=("total counted: 12",),
        n_variants=3,
    ),

    # ----------------------------------------------- Predictive Modelling
    ExerciseTemplate(
        id="pm-train-test-split",
        skill="Splitting data into train and test",
        block="Predictive Modelling",
        prompt=(
            "Write `split(rows, fraction, seed)` that shuffles rows with a seeded generator and "
            "returns the first `round(len(rows) * fraction)` rows as the training set and the rest "
            "as the test set. Use seed <<seed>>. Print both sizes; the split must be reproducible, so "
            "calling it twice must give the same answer."
        ),
        solution='''import random


def split(rows, fraction, seed=0):
    shuffled = list(rows)
    random.Random(seed).shuffle(shuffled)
    cut = round(len(shuffled) * fraction)
    return shuffled[:cut], shuffled[cut:]


def main(rows, seed):
    return split(rows, 0.8, seed)


ROWS = [{'x': i, 'y': i * 2} for i in range(10)]
train, test = main(ROWS, 5)
print('train size:', len(train))
print('test size:', len(test))
print('overlap:', len(set(id(r) for r in train) & set(id(r) for r in test)))
again, _ = split(ROWS, 0.8, 5)
print('reproducible:', [r['x'] for r in again] == [r['x'] for r in train])''',
        required_patterns=("def ", "random.Random", "shuffle", "print("),
        rubric=RUBRIC_STD,
        params={"seed": (0, 5, 42)},
        expect=("train size: 8", "test size: 2", "reproducible: True"),
        n_variants=3,
    ),
    ExerciseTemplate(
        id="pm-linear-regression",
        skill="Least-squares linear regression by hand",
        block="Predictive Modelling",
        prompt=(
            "Write `fit_line(xs, ys)` computing the slope and intercept that minimise squared error, "
            "and `predict(line, x)`. Print the slope, the intercept, and the prediction for x = <<xq>>. "
            "Raising ValueError when the inputs have different lengths is required."
        ),
        solution='''def mean(values):
    return sum(values) / len(values)


def fit_line(xs, ys):
    if len(xs) != len(ys):
        raise ValueError('xs and ys must have equal length')
    if len(xs) < 2:
        raise ValueError('need at least two points')
    mx, my = mean(xs), mean(ys)
    denom = sum((x - mx) ** 2 for x in xs)
    if denom == 0:
        raise ValueError('x values are all identical')
    slope = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / denom
    return slope, my - slope * mx


def predict(line, x):
    slope, intercept = line
    return slope * x + intercept


def main(xs, ys, xq):
    return fit_line(xs, ys), predict(fit_line(xs, ys), xq)


line, yhat = main((1, 2, 3, 4, 5), (2, 4, 6, 8, 10), 6)
print(f'slope     {line[0]:.4f}')
print(f'intercept {line[1]:.4f}')
print(f'prediction at 6: {yhat:.4f}')
print('fit is exact:', abs(yhat - 12) < 1e-9)''',
        required_patterns=("def ", "zip(", "raise ", "print("),
        rubric=RUBRIC_STD,
        params={"xq": (6, 7)},
        expect=("slope", "prediction at"),
        n_variants=2,
    ),
    ExerciseTemplate(
        id="pm-accuracy-confusion",
        skill="Accuracy from a confusion matrix",
        block="Predictive Modelling",
        prompt=(
            "Given actual labels <<actual>> and predicted labels <<predicted>>, write `score(actual, "
            "predicted)` that builds a confusion matrix and returns accuracy, precision and "
            "recall. Print all three. Handle a zero denominator by returning 0.0 rather than "
            "raising, and print the case count."
        ),
        solution='''def score(actual, predicted):
    if len(actual) != len(predicted):
        raise ValueError('lengths must match')
    tp = sum(1 for a, p in zip(actual, predicted) if a == 1 and p == 1)
    tn = sum(1 for a, p in zip(actual, predicted) if a == 0 and p == 0)
    fp = sum(1 for a, p in zip(actual, predicted) if a == 0 and p == 1)
    fn = sum(1 for a, p in zip(actual, predicted) if a == 1 and p == 0)
    n = tp + tn + fp + fn
    accuracy = (tp + tn) / n if n else 0.0
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    return {'tp': tp, 'tn': tn, 'fp': fp, 'fn': fn,
            'accuracy': accuracy, 'precision': precision, 'recall': recall}


def main(raw_actual, raw_predicted):
    to_int = lambda s: tuple(int(v) for v in s.split(","))
    return score(to_int(raw_actual), to_int(raw_predicted))


m = main("<<actual>>", "<<predicted>>")
print(f"tp {m['tp']} tn {m['tn']} fp {m['fp']} fn {m['fn']}")
print(f"accuracy  {m['accuracy']:.3f}")
print(f"precision {m['precision']:.3f}")
print(f"recall    {m['recall']:.3f}")''',
        required_patterns=("def ", "zip(", "raise ", "print("),
        rubric=RUBRIC_STD,
        params={"actual": ("1,1,0,0,1,0", "1,0,1,0,0,1", "0,0,0,1,1,1"),
                "predicted": ("1,0,0,1,1,0", "1,1,1,0,0,0", "0,0,1,0,1,1")},
        expect=("accuracy", "precision", "recall"),
        n_variants=3,
    ),
    ExerciseTemplate(
        id="pm-knn-predict",
        skill="Predicting with a nearest-neighbour classifier",
        block="Predictive Modelling",
        prompt=(
            "Write `knn_predict(train, point, k)` that finds the k nearest training points by "
            "Euclidean distance and returns the majority label. Predict the label for the query "
            "point <<query>> using k = <<k>>, and print the prediction together with the labels of "
            "the <<k>> neighbours it used. Tie-breaking must be deterministic, so sorting by "
            "distance before counting is required."
        ),
        solution='''def distance(a, b):
    return sum((x - y) ** 2 for x, y in zip(a, b)) ** 0.5


def knn_predict(train, point, k=3):
    if k < 1:
        raise ValueError('k must be positive')
    if k > len(train):
        raise ValueError('k cannot exceed the training set size')
    ranked = sorted(train, key=lambda row: distance(row['features'], point))
    nearest = ranked[:k]
    counts = {}
    for row in nearest:
        label = row['label']
        counts[label] = counts.get(label, 0) + 1
    best = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
    return best[0][0], [row['label'] for row in nearest]


def main(raw_point, k):
    point = tuple(float(v) for v in raw_point.split(","))
    return knn_predict(TRAIN, point, k)


TRAIN = [
    {'features': (1.0, 1.0), 'label': 'a'},
    {'features': (1.5, 1.2), 'label': 'a'},
    {'features': (8.0, 8.0), 'label': 'b'},
    {'features': (8.5, 9.0), 'label': 'b'},
    {'features': (2.0, 1.8), 'label': 'a'},
]
label, used = main("<<query>>", <<k>>)
print('prediction:', label)
print('neighbours used:', used)''',
        required_patterns=("def ", "sorted(", "raise ", "print("),
        rubric=RUBRIC_STD,
        params={"query": ("1.8,1.5", "1.2,0.9", "8.2,8.4"), "k": (3, 5)},
        expect=("prediction:", "neighbours used:"),
        n_variants=3,
    ),
    ExerciseTemplate(
        id="pm-scaling",
        skill="Standardising features before distance work",
        block="Predictive Modelling",
        prompt=(
            "Write `standardise(rows, index)` returning each row with the `<<col>>` feature replaced "
            "by its z-score. Print the mean and standard deviation of that column before and "
            "after; after standardisation the mean must be within 0.001 of 0."
        ),
        solution='''def mean(values):
    return sum(values) / len(values)


def stddev(values):
    m = mean(values)
    return (sum((v - m) ** 2 for v in values) / len(values)) ** 0.5


def standardise(rows, index):
    column = [row[index] for row in rows]
    m, sd = mean(column), stddev(column)
    if sd == 0:
        raise ValueError('cannot standardise a constant column')
    return [{**row, index: (row[index] - m) / sd} for row in rows]


def main(rows, index):
    return standardise(rows, index)


ROWS = [
    {'height': 160, 'weight': 50},
    {'height': 170, 'weight': 60},
    {'height': 180, 'weight': 72},
]
out = main(ROWS, "<<col>>")
column = [r["<<col>>"] for r in out]
print(f"before mean {mean([r['<<col>>'] for r in ROWS]):.4f} sd {stddev([r['<<col>>'] for r in ROWS]):.4f}")
print(f"after  mean {mean(column):.4f} sd {stddev(column):.4f}")
print('centred:', abs(mean(column)) < 0.001)''',
        required_patterns=("def ", "raise ", "** 2", "print("),
        rubric=RUBRIC_STD,
        params={"col": ("height", "weight")},
        expect=("centred: True",),
        n_variants=2,
    ),
    ExerciseTemplate(
        id="pm-overfitting-check",
        skill="Detecting overfitting with a train/test gap",
        block="Predictive Modelling",
        prompt=(
            "Write `gap(train_errors, test_errors)` that returns the difference in mean error and "
            "classifies the fit as `underfit`, `overfit` or `ok` using thresholds on train and test "
            "error. Print the classification. A high train error must print `underfit`."
        ),
        solution='''def mean(values):
    return sum(values) / len(values)


def gap(train_errors, test_errors):
    tr, te = mean(train_errors), mean(test_errors)
    if tr > 0.2:
        return tr, te, tr - te, 'underfit'
    if te - tr > 0.15:
        return tr, te, te - tr, 'overfit'
    return tr, te, te - tr, 'ok'


def main(train, test):
    return gap(train, test)


for label, train, test in (
    ('underfit', (0.35, 0.33, 0.36), (0.38, 0.37, 0.39)),
    ('ok', (0.10, 0.09, 0.11), (0.12, 0.13, 0.11)),
    ('overfit', (0.02, 0.01, 0.02), (0.30, 0.28, 0.31)),
):
    tr, te, g, verdict = main(train, test)
    print(f'{label:<10} train {tr:.3f} test {te:.3f} gap {g:+.3f} -> {verdict}')''',
        required_patterns=("def ", "return", "if ", "print("),
        rubric=RUBRIC_STD,
        params={},
        expect=("underfit", "overfit", "ok"),
        n_variants=1,
    ),

    # ------------------------------------------- Evaluation and Deployment
    ExerciseTemplate(
        id="ed-mae-rmse",
        skill="Regression error metrics",
        block="Evaluation and Deployment",
        prompt=(
            "For actual values <<actual>> and predicted values <<predicted>>, write `mae(actual, "
            "predicted)` and `rmse(actual, predicted)`, raising ValueError on a length mismatch "
            "or an empty input. Print both, and print which metric is larger, which for the same "
            "data is always the case and is why you should report both."
        ),
        solution='''def mae(actual, predicted):
    if len(actual) != len(predicted):
        raise ValueError('lengths must match')
    if not actual:
        raise ValueError('empty input')
    return sum(abs(a - p) for a, p in zip(actual, predicted)) / len(actual)


def rmse(actual, predicted):
    if len(actual) != len(predicted):
        raise ValueError('lengths must match')
    if not actual:
        raise ValueError('empty input')
    return (sum((a - p) ** 2 for a, p in zip(actual, predicted)) / len(actual)) ** 0.5


def main(raw_a, raw_p):
    a = tuple(float(v) for v in raw_a.split(","))
    p = tuple(float(v) for v in raw_p.split(","))
    return mae(a, p), rmse(a, p)


a, p = main("<<actual>>", "<<predicted>>")
print(f'mae  {a:.4f}')
print(f'rmse {p:.4f}')
print('rmse is larger:', p > a)''',
        required_patterns=("def ", "zip(", "raise ", "print("),
        rubric=RUBRIC_STD,
        params={"actual": ("10,20,30", "5,9,14,18", "100,120,95,130"),
                "predicted": ("12,18,33", "4,11,13,20", "90,125,100,122")},
        expect=("rmse is larger: True",),
        n_variants=3,
    ),
    ExerciseTemplate(
        id="ed-leakage-guard",
        skill="Guarding against data leakage",
        block="Evaluation and Deployment",
        prompt=(
            "Write `audit_split(train, test, key)` that raises ValueError if any key appears in both "
            "sets, which is how target leakage between train and test is caught. The clean split "
            "holds u1 and u2 in train and u3 in test; the leaky split repeats <<leak>> across the "
            "boundary. Print the audit result for both, showing that only the leaky one is caught."
        ),
        solution='''def keys_of(rows, key):
    return {row[key] for row in rows}


def audit_split(train, test, key):
    overlap = keys_of(train, key) & keys_of(test, key)
    if overlap:
        raise ValueError(f'leakage on key {key!r}: {sorted(overlap)}')
    return 'clean'


def main(clean_train, clean_test, leaky_train, leaky_test):
    out = {}
    out['clean'] = audit_split(clean_train, clean_test, 'user')
    try:
        audit_split(leaky_train, leaky_test, 'user')
    except ValueError as err:
        out['leaky'] = f'caught: {err}'
    return out


clean_train = [{'user': 'u1'}, {'user': 'u2'}]
clean_test = [{'user': 'u3'}]
leaky_train = [{'user': 'u1'}, {'user': 'u2'}]
leaky_test = [{'user': '<<leak>>'}]
result = main(clean_train, clean_test, leaky_train, leaky_test)
print('clean split ->', result['clean'])
print('leaky split ->', result['leaky'])''',
        required_patterns=("def ", "raise ", "try:", "except ", "print("),
        rubric=RUBRIC_STD,
        params={"leak": ("u2", "u1")},
        expect=("clean split -> clean", "caught:"),
        n_variants=2,
    ),
    ExerciseTemplate(
        id="ed-error-buckets",
        skill="Bucketing errors for analysis",
        block="Evaluation and Deployment",
        prompt=(
            "Write `error_buckets(actual, predicted, size)` that assigns each row to a bucket based "
            "on the size of its absolute error and returns the count per bucket plus a count of "
            "rows that were exact. For this run the bucket width is <<size>>. Print the buckets and "
            "the exact count. Raising ValueError on a length mismatch is required."
        ),
        solution='''def error_buckets(actual, predicted, size):
    if len(actual) != len(predicted):
        raise ValueError('lengths must match')
    if size <= 0:
        raise ValueError('size must be positive')
    counts = {}
    exact = 0
    for a, p in zip(actual, predicted):
        err = abs(a - p)
        if err == 0:
            exact += 1
        low = int(err // size) * size
        key = f'{low}-{low + size}'
        counts[key] = counts.get(key, 0) + 1
    return counts, exact


def main(raw_a, raw_p, size):
    a = tuple(int(v) for v in raw_a.split(","))
    p = tuple(int(v) for v in raw_p.split(","))
    return error_buckets(a, p, size)


counts, exact = main("10,20,30,40", "10,18,33,45", <<size>>)
for bucket in sorted(counts):
    print(f'error {bucket:<8} {counts[bucket]}')
print('exact predictions:', exact)''',
        required_patterns=("def ", "zip(", "raise ", "print("),
        rubric=RUBRIC_STD,
        params={"size": (5, 10, 4)},
        expect=("exact predictions:",),
        n_variants=3,
    ),
    ExerciseTemplate(
        id="ed-report-card",
        skill="Building a results report you can defend",
        block="Evaluation and Deployment",
        prompt=(
            "Write `report(metrics)` that formats accuracy, precision, recall and sample size into "
            "a short report string, refusing to publish when the sample size is below a threshold. "
            "The well-powered run in this variant reports n = <<n>>; the thin one reports n = 1. "
            "Print both reports, showing that only the thin run is withheld."
        ),
        solution='''MIN_SAMPLES = 30


def report(metrics, min_samples=MIN_SAMPLES):
    n = metrics.get('samples', 0)
    if n < min_samples:
        return f"WITHHELD: only {n} samples, need {min_samples}"
    return (
        f"accuracy {metrics['accuracy']:.3f} | "
        f"precision {metrics['precision']:.3f} | "
        f"recall {metrics['recall']:.3f} | n={n}"
    )


def main(good, thin):
    return report(good), report(thin)


good = {'accuracy': 0.82, 'precision': 0.79, 'recall': 0.85, 'samples': int("<<n>>")}
thin = {'accuracy': 0.95, 'precision': 0.94, 'recall': 0.96, 'samples': 1}
ok, withheld = main(good, thin)
print('published :', ok)
print('withheld  :', withheld)''',
        required_patterns=("def ", "get(", "return", "print("),
        rubric=RUBRIC_STD,
        params={"n": ("240", "60", "8")},
        expect=("WITHHELD", "published"),
        n_variants=3,
    ),
)
