"""Canonical exercise templates for the four curriculum blocks shared by all paths.

The four blocks below Core Python, Practical Python, Software Engineering and
Algorithms and Math are byte-identical across the three launch paths, so one
template per day fills that day in every path. Sixty templates therefore unlock a
hundred and eighty day-slots, which is why this file is keyed by `day` rather
than rotated by block.

Each template follows the same contract as the domain templates: values are drawn
from pools, the prompt states the values it was drawn, the solution uses only the
standard library, and the generator executes every variant before it is allowed
to reach the database. Where a concept has nothing meaningful to randomise, the
pool is empty and `n_variants` is 1 rather than pretending a repeated draw is a
distinct exercise.
"""
from __future__ import annotations

from app.exercise_gen import ExerciseTemplate

R = (
    "Code must run without raising, define at least one function, and print the stated output.",
    "The required constructs must appear so the idea is practised, not bypassed.",
    "Changing one input value must change the output in the way the prompt predicts.",
)


def _t(**kw) -> ExerciseTemplate:
    return ExerciseTemplate(rubric=R, **kw)


CORE_PYTHON: tuple[ExerciseTemplate, ...] = (

    _t(id="cp-15-boolean", block="Core Python", day=15, skill="Boolean values and truthiness",
       prompt=(
           "Given the values <<values>>, write `describe(v)` that reports `truthy` or `falsy` for "
           "each value using `bool()`. Print one line per value, then print how many were truthy. "
           "Empty containers count as falsy, so a run containing an empty list must include one "
           "`falsy` line."),
       solution='''VALUES = [0, 1, "", "hello", [], [0], None, 0.0]


def describe(v):
    return 'truthy' if bool(v) else 'falsy'


def main(values=VALUES):
    for v in values:
        print(f'{v!r:<10} {describe(v)}')
    print('truthy count:', sum(1 for v in values if describe(v) == 'truthy'))


main()''',
       required_patterns=("def ", "bool(", "for ", "print("),
       params={"values": ('''0, 1, "", "hello", [], [0], None, 0.0''',
                           '''1, 0, "a", "", (), (0,), False, 3.5''',
                           '''"", "x", [], {}, None, 0, -1, []''')},
       expect=("truthy count:",),
       n_variants=3),

    _t(id="cp-16-comparison", block="Core Python", day=16, skill="Chained comparisons",
       prompt=(
           "For the pair <<pair>> write `in_range(v, lo, hi)` returning True when `lo <= v <= hi`. "
           "Print the result for that pair. Then write `outside(values, lo, hi)` filtering the list "
           "<<values>> to those outside the range, and print the survivors in order."),
       solution='''PAIR = (7, 1, 10)
VALUES = [-4, 0, 1, 5, 9, 10, 11, 42]


def in_range(v, lo, hi):
    return lo <= v <= hi


def outside(values, lo, hi):
    return [v for v in values if not in_range(v, lo, hi)]


def main(pair=PAIR, values=VALUES):
    v, lo, hi = pair
    print(f'in_range({v}, {lo}, {hi}):', in_range(v, lo, hi))
    kept = outside(values, lo, hi)
    print('outside:', kept)
    print('count outside:', len(kept))


main()''',
       required_patterns=("def ", "return ", "<=", "print("),
       params={"pair": ("(7, 1, 10)", "(3, 10, 1)", "(-2, -5, 5)"),
               "values": ("[-4, 0, 1, 5, 9, 10, 11, 42]", "[1, 2, 3, 4, 5]", "[0, 100]")},
       expect=("count outside:",),
       n_variants=3),

    _t(id="cp-17-elif", block="Core Python", day=17, skill="if / elif decision trees",
       prompt=(
           "Write `band(score)` returning `fail` below <<cut1>>, `pass` up to <<cut2>>, `distinction` "
           "up to <<cut3>>, and `merit` above that. Print the band for each score in <<scores>>. "
           "A score of exactly the cut must fall in the higher band."),
       solution='''SCORES = [35, 50, 65, 78, 91]


def band(score, cuts=(<<cut1>>, <<cut2>>, <<cut3>>)):
    c1, c2, c3 = cuts
    if score < c1:
        return 'fail'
    elif score < c2:
        return 'pass'
    elif score < c3:
        return 'distinction'
    return 'merit'


def main(scores=SCORES, cuts=(<<cut1>>, <<cut2>>, <<cut3>>)):
    for s in scores:
        print(f'{s:>3} -> {band(s, cuts)}')


main()''',
       required_patterns=("def ", "if ", "elif ", "return"),
       params={"scores": ("[35, 50, 65, 78, 91]", "[49, 50, 64, 65, 77, 78, 100]",
                          "[0, 49, 50, 64, 65, 77, 78, 120]"),
               "cut1": ("50", "40", "10"), "cut2": ("65", "55", "60"),
               "cut3": ("78", "70", "80")},
       expect=("-> merit",),
       n_variants=3),

    _t(id="cp-18-nested", block="Core Python", day=18, skill="Nested conditions",
       prompt=(
           "A ticket is valid when the seat exists and the age is between <<min_age>> and "
           "<<max_age>> inclusive. Write `check(seat, age)` returning one of `ok`, `no seat`, "
           "`too young`, `too old`. Print the verdict for each pair in <<cases>>."),
       solution='''CASES = [('B4', 30), ('A1', 9), ('Z9', 30), ('C7', 70), ('C7', 25)]


def check(seat, age, min_age=<<min_age>>, max_age=<<max_age>>):
    seats = {'A1', 'B4', 'C7'}
    if seat not in seats:
        return 'no seat'
    if age < min_age:
        return 'too young'
    if age > max_age:
        return 'too old'
    return 'ok'


def main(cases=CASES):
    for seat, age in cases:
        print(f'{seat} age {age:<3} -> {check(seat, age)}')


main()''',
       required_patterns=("def ", "if ", "return", "for "),
       params={"cases": ("[('B4', 30), ('A1', 9), ('Z9', 30), ('C7', 70), ('C7', 25)]",
                          "[('A1', 10), ('A1', 65), ('A1', 66), ('B4', 9)]",
                          "[('C7', 11), ('X1', 20), ('C7', 64)]"),
               "min_age": ("10", "16", "5"), "max_age": ("65", "60", "70")},
       expect=("-> ok",),
       n_variants=3),

    _t(id="cp-19-while", block="Core Python", day=19, skill="while loops and accumulators",
       prompt=(
           "Write `collatz(n)` that applies the Collatz step until the value reaches 1, using a "
           "while loop, and returns the number of steps taken. For n = <<n>> print the step count. "
           "Reject n below 1 with ValueError."),
       solution='''def collatz(n):
    if n < 1:
        raise ValueError('n must be at least 1')
    steps = 0
    while n != 1:
        n = 3 * n + 1 if n % 2 else n // 2
        steps += 1
    return steps


def main(n=<<n>>):
    return collatz(n)


for start in (<<n>>, 7, 27):
    print(f'start {start:<3} steps {collatz(start)}')
try:
    collatz(0)
except ValueError as err:
    print('rejected:', err)''',
       required_patterns=("def ", "while ", "raise ", "print("),
       params={"n": ("6", "7", "27")},
       expect=("steps",),
       n_variants=1),

    _t(id="cp-20-loop-control", block="Core Python", day=20, skill="break, continue and else",
       prompt=(
           "Write `first_big(values, limit)` returning the first value above `limit`, or None when "
           "there is none. Use `break` for the early exit and the `else` clause of the loop to "
           "report that nothing was found. For <<values>> with limit <<limit>> print the result and "
           "a line saying whether the search completed."),
       solution='''VALUES = [3, 7, 12, 4, 20]
LIMIT = 10


def first_big(values, limit):
    for v in values:
        if v > limit:
            return v
    else:
        return None


def main(values=VALUES, limit=LIMIT):
    found = first_big(values, limit)
    print('first above limit:', found)
    if found is None:
        print('search completed: no value above', limit)
    else:
        print('stopped early at', found)


main()''',
       required_patterns=("def ", "for ", "break", "else:"),
       params={"values": ("[3, 7, 12, 4, 20]", "[1, 2, 3]", "[10, 10, 10, 11]"),
               "limit": ("10", "9", "99")},
       expect=("first above limit:",),
       n_variants=3),

    _t(id="cp-21-string-index", block="Core Python", day=21, skill="String indexing and slicing",
       prompt=(
           "Write `edges(text)` returning the first and last characters and the middle character of "
           "`<<text>>`. Reject a string shorter than 3 characters with ValueError. Then write "
           "`every_other(text)` returning the characters at even positions, and print both results."),
       solution='''TEXT = "abcdefghij"


def edges(text):
    if len(text) < 3:
        raise ValueError('need at least three characters')
    return text[0], text[len(text) // 2], text[-1]


def every_other(text):
    return text[::2]


def main(text=TEXT):
    first, middle, last = edges(text)
    print(f'{text!r} first {first!r} middle {middle!r} last {last!r}')
    print('every other:', every_other(text))


main()
try:
    edges('ab')
except ValueError as err:
    print('rejected:', err)''',
       required_patterns=("def ", "return ", "[0]", "print("),
       params={"text": ('"abcdefghij"', '"python"', '"abcdef"')},
       expect=("every other:",),
       n_variants=3),

    _t(id="cp-22-string-methods", block="Core Python", day=22, skill="String methods that return new strings",
       prompt=(
           "Strings are immutable, so every transforming method hands back a new string. Given "
           "`<<raw>>`, write `tidy(raw)` that strips it, collapses repeated spaces to one, and "
           "title-cases it. Print the original and the result so the difference is visible, and "
           "print the original's length before and after to prove it did not change."),
       solution='''RAW = "  the   QUICK  brown\\tfox  "


def tidy(text):
    return ' '.join(text.split()).title()


def main(raw=RAW):
    before = raw
    result = tidy(raw)
    print('before:', repr(before), 'len', len(before))
    print('after :', repr(result), 'len', len(result))
    print('original untouched:', len(before) == len(RAW))


main()''',
       required_patterns=("def ", "split()", ".strip()", "print("),
       params={"raw": ('"  the   QUICK  brown\\tfox  "', '"  hello   world  "',
                       '" a  b  c   d "')},
       expect=("original untouched: True",),
       n_variants=3),

    _t(id="cp-23-list-methods", block="Core Python", day=23, skill="In-place versus returning list methods",
       prompt=(
           "`sort()` changes a list and returns None, while `sorted()` returns a new list. For "
           "<<values>> print the result of assigning `out = values.sort()` to show what that returns, "
           "then print the list to show it did change, then print `sorted(values, reverse=True)` to "
           "show a new list instead."),
       solution='''VALUES = [5, 2, 9, 1]


def main(values=VALUES):
    work = list(values)
    out = work.sort()
    print('sort() returned:', out)
    print('list after sort():', work)
    print('sorted() returned:', sorted(work, reverse=True))
    print('list still:', work)
    print('work is values:', work is VALUES)


main()''',
       required_patterns=("def ", ".sort(", "sorted(", "print("),
       params={"values": ("[5, 2, 9, 1]", "[3, 1, 2]", "[10, 0, 7, 7]")},
       expect=("sort() returned: None",),
       n_variants=3),

    _t(id="cp-24-tuples", block="Core Python", day=24, skill="Tuples and unpacking",
       prompt=(
           "A record is the triple (name, score, grade). For the records <<records>>, write "
           "`summarise(records)` that unpacks each record, keeps the top two by score, and returns "
           "their names. Print the names in order and the mean score."),
       solution='''RECORDS = [
    ('Asha', 88, 'A'),
    ('Rohan', 74, 'B'),
    ('Meera', 91, 'A'),
    ('Kabir', 66, 'C'),
]


def summarise(records):
    top = sorted(records, key=lambda r: r[1], reverse=True)[:2]
    return [r[0] for r in top], sum(r[1] for r in records) / len(records)


def main(records=RECORDS):
    names, mean = summarise(records)
    print('top two:', ', '.join(names))
    print(f'mean score {mean:.2f}')


main()''',
       required_patterns=("def ", "sorted(", "for ", "print("),
       params={"records": ("""[('Asha', 88, 'A'), ('Rohan', 74, 'B'), ('Meera', 91, 'A'), ('Kabir', 66, 'C')]""",
                           """[('A', 50, 'C'), ('B', 90, 'A'), ('C', 70, 'B')]""",
                           """[('X', 10, 'C'), ('Y', 20, 'B'), ('Z', 30, 'A'), ('W', 40, 'A')]""")},
       expect=("mean score",),
       n_variants=3),

    _t(id="cp-25-sets", block="Core Python", day=25, skill="Sets and set operations",
       prompt=(
           "Write `overlap(a, b)` returning the values common to both lists, `only_in(a, b)` for the "
           "values in the first but not the second, and print both for <<a>> and <<b>>. Then print "
           "the number of duplicates in the concatenation, showing why a set is the right tool."),
       solution='''A = [1, 2, 3, 4, 5]
B = [4, 5, 6, 7]


def overlap(a, b):
    return sorted(set(a) & set(b))


def only_in(a, b):
    return sorted(set(a) - set(b))


def main(a=A, b=B):
    print('overlap:', overlap(a, b))
    print('only in first:', only_in(a, b))
    combined = list(a) + list(b)
    print('combined length:', len(combined))
    print('as a set:', len(set(combined)))
    print('duplicates:', len(combined) - len(set(combined)))


main()''',
       required_patterns=("def ", "set(", "return", "print("),
       params={"a": ("[1, 2, 3, 4, 5]", "[10, 20, 30]", "[1, 1, 2, 2]"),
               "b": ("[4, 5, 6, 7]", "[20, 30, 40]", "[2, 3]")},
       expect=("duplicates:",),
       n_variants=3),

    _t(id="cp-26-dict-methods", block="Core Python", day=26, skill="Dictionary methods and safe access",
       prompt=(
           "Write `summarise_counts(pairs)` building a dict from (key, value) pairs by summing values "
           "per key, then `lookup(d, key)` that returns a default of 0 for a missing key instead of "
           "raising. Use the pairs <<pairs>> and print the totals, then print the total for a key "
           "that does not exist."),
       solution='''PAIRS = [('a', 3), ('b', 5), ('a', 4), ('c', 1), ('b', 2)]


def summarise_counts(pairs):
    totals = {}
    for key, value in pairs:
        totals[key] = totals.get(key, 0) + value
    return totals


def lookup(d, key):
    return d.get(key, 0)


def main(pairs=PAIRS):
    totals = summarise_counts(pairs)
    for key in sorted(totals):
        print(f'{key}: {totals[key]}')
    print('missing key total:', lookup(totals, 'zzz'))


main()''',
       required_patterns=("def ", "get(", "for ", "print("),
       params={"pairs": ("[('a', 3), ('b', 5), ('a', 4), ('c', 1), ('b', 2)]",
                         "[('x', 1), ('y', 2), ('x', 1)]",
                         "[('p', 10), ('q', 20), ('r', 30), ('p', 5)]")},
       expect=("missing key total: 0",),
       n_variants=3),

    _t(id="cp-27-params", block="Core Python", day=27, skill="Parameters, defaults and keywords",
       prompt=(
           "For the list <<values>>, write `scale(values, factor=<<factor>>, cap=None)` that "
           "multiplies every value by `factor` and, when `cap` is given, clips the result to `cap`. "
           "Call it three times: "
           "positionally, by keyword, and with a cap. Print each result so the difference between "
           "the three call styles is visible."),
       solution='''VALUES = [2, 5, 9]


def scale(values, factor=2, cap=None):
    out = [v * factor for v in values]
    if cap is not None:
        out = [min(v, cap) for v in out]
    return out


def main(values=VALUES):
    print('positional :', scale(values, 3))
    print('keyword    :', scale(values, factor=4))
    print('with cap   :', scale(values, factor=4, cap=20))


main()''',
       required_patterns=("def ", "if ", "return", "print("),
       params={"values": ("[2, 5, 9]", "[1, 10]", "[3, 3, 3]"),
               "factor": ("2", "3", "5")},
       expect=("with cap   :",),
       n_variants=3),

    _t(id="cp-28-returns", block="Core Python", day=28, skill="Return values and multiple returns",
       prompt=(
           "Write `stats(values)` that returns the minimum, maximum and mean, and raises ValueError "
           "on an empty list. Write `first_failure(checks)` that returns the label of the first check "
           "that fails, or the string `all passed`. Use the values <<values>> and the checks "
           "<<checks>>, and print both results."),
       solution='''VALUES = [4, 8, 15, 16, 23, 42]
CHECKS = ['len ok', 'range ok', 'sorted ok']


def stats(values):
    if not values:
        raise ValueError('values must not be empty')
    return min(values), max(values), sum(values) / len(values)


def first_failure(checks):
    for label in checks:
        if 'fail' in label:
            return label
    return 'all passed'


def main(values=VALUES, checks=CHECKS):
    lo, hi, mean = stats(values)
    print(f'min {lo} max {hi} mean {mean:.4f}')
    print('first failure:', first_failure(checks))


main()''',
       required_patterns=("def ", "return", "raise ", "print("),
       params={"values": ("[4, 8, 15, 16, 23, 42]", "[1, 2]", "[5]"),
               "checks": ("['len ok', 'range ok', 'sorted ok']",
                          "['len ok', 'range fail', 'sorted ok']",
                          "['a ok', 'b ok']")},
       expect=("first failure:",),
       n_variants=3),

    _t(id="cp-29-scope", block="Core Python", day=29, skill="Scope and the global statement",
       prompt=(
           "Write `make_counter()` returning a function that counts up and returns the running total. "
           "Then show that a name assigned inside a function is not visible outside it by printing it "
           "through a lookup, and show a module-level counter that a function updates with `global`. "
           "Print the counter sequence and the local lookup result."),
       solution='''def make_counter():
    total = 0

    def bump():
        nonlocal total
        total += 1
        return total

    return bump


def reveal():
    hidden = 'only inside'
    return 'found'


RUNS = 0


def add_run():
    global RUNS
    RUNS += 1
    return RUNS


counter = make_counter()
print('counter:', counter(), counter(), counter())
print('local lookup:', reveal())
print('global runs:', add_run(), add_run())
try:
    print(hidden)
except NameError as err:
    print('not visible outside:', type(err).__name__)''',
       required_patterns=("def ", "nonlocal ", "global ", "print("),
       params={},
       expect=("not visible outside: NameError",),
       n_variants=1),
)


PRACTICAL_PYTHON: tuple[ExerciseTemplate, ...] = (

    _t(id="pp-30-modules", block="Practical Python", day=30, skill="Importing from modules",
       prompt=(
           "Put two helpers in a module: `slugify(text)` lowercasing and replacing spaces with "
           "hyphens, and `shout(text)` uppercasing. Write a `main` that imports both and prints "
           "their output for `<<text>>`. Import the module by name, not with a star import."),
       solution='''TEXT = "Hello There World"


def slugify(text):
    return '-'.join(text.lower().split())


def shout(text):
    return text.upper()


def main(text=TEXT):
    print('slug:', slugify(text))
    print('shout:', shout(text))


main()''',
       required_patterns=("def ", "import ", ".split()", "print("),
       params={"text": ('"Hello There World"', '"  Spaced   Out  "', '"One"')},
       expect=("slug:",),
       n_variants=3),

    _t(id="pp-31-stdlib", block="Practical Python", day=31, skill="Finding the right standard library tool",
       prompt=(
           "Use only the standard library: `statistics.mean` and `math` to report the mean, the "
           "smallest value at or above it, and how many values are even, for <<values>>. Print each "
           "figure with a label. The point is choosing the library function instead of reimplementing "
           "it."),
       solution='''VALUES = [12, 7, 19, 7, 24, 3]


def main(values=VALUES):
    from statistics import mean
    from math import ceil

    m = mean(values)
    at_or_above = min(v for v in values if v >= m)
    even = sum(1 for v in values if v % 2 == 0)
    print(f'mean      {m:.4f}')
    print(f'smallest >= mean: {at_or_above}')
    print(f'even count: {even}')
    print(f'rounded mean: {ceil(m)}')


main()''',
       required_patterns=("import ", "from ", "def ", "print("),
       params={"values": ("[12, 7, 19, 7, 24, 3]", "[4, 8, 15, 16]", "[1, 2, 3, 4, 5, 6, 7, 8]")},
       expect=("mean",),
       n_variants=3),

    _t(id="pp-32-argparse", block="Practical Python", day=32, skill="Command-line arguments with argparse",
       prompt=(
           "Build a parser accepting a required `--name`, an optional `--count` defaulting to <<default>>, "
           "and a `--loud` flag. Print the parsed name, count, and whether loud is set. Run the parser "
           "twice: once with arguments supplied, once with none, to show the default."),
       solution='''import argparse


def build_parser():
    parser = argparse.ArgumentParser(description='greet someone')
    parser.add_argument('--name', required=True)
    parser.add_argument('--count', type=int, default=<<default>>)
    parser.add_argument('--loud', action='store_true')
    return parser


def main(argv):
    args = build_parser().parse_args(argv)
    print('name:', args.name)
    print('count:', args.count)
    print('loud:', args.loud)


main(['--name', 'Asha'])
main(['--name', 'Rohan', '--count', '3', '--loud'])''',
       required_patterns=("import argparse", "add_argument", "required=True", "print("),
       params={"default": ("1", "2", "5")},
       expect=("loud:",),
       n_variants=3),

    _t(id="pp-33-validation", block="Practical Python", day=33, skill="Validating input before use",
       prompt=(
           "Write `parse_count(text)` that accepts digits only, rejects an empty string and anything "
           "non-numeric with ValueError, and caps the result at <<cap>>. For <<inputs>> print either the "
           "parsed value or the rejection message, so the failure path is visible."),
       solution='''INPUTS = ['42', '', 'abc', '999']


def parse_count(text, cap=<<cap>>):
    if not text:
        raise ValueError('value must not be empty')
    if not text.isdigit():
        raise ValueError(f'not a number: {text!r}')
    return min(int(text), cap)


def main(inputs=INPUTS):
    for raw in inputs:
        try:
            print(f'{raw!r:<7} ->', parse_count(raw))
        except ValueError as err:
            print(f'{raw!r:<7} -> rejected: {err}')


main()''',
       required_patterns=("def ", "raise ", "try:", "except ", "print("),
       params={"cap": ("100", "50", "1000"),
               "inputs": ("['42', '', 'abc', '999']", "['7', 'x', '0']", "['12', '-3', '']")},
       expect=("rejected:",),
       n_variants=3),

    _t(id="pp-34-exceptions", block="Practical Python", day=34, skill="Catching the right exception",
       prompt=(
           "Write `safe_divide(a, b)` that returns the quotient as a float, or the string `undefined` "
           "when `b` is zero, catching ZeroDivisionError specifically. Add `safe_index(items, i)` "
           "that returns `out of range` on IndexError. Call both with <<cases>> and print the results, "
           "so the two failure modes are visibly different."),
       solution='''CASES = [(8, 2), (8, 0)]


def safe_divide(a, b):
    try:
        return a / b
    except ZeroDivisionError:
        return 'undefined'


def safe_index(items, i):
    try:
        return items[i]
    except IndexError:
        return 'out of range'


def main(cases=CASES):
    for a, b in cases:
        print(f'{a} / {b} ->', safe_divide(a, b))
    print('index 0 ->', safe_index([1, 2, 3], 0))
    print('index 9 ->', safe_index([1, 2, 3], 9))


main()''',
       required_patterns=("def ", "try:", "except ", "print("),
       params={"cases": ("[(8, 2), (8, 0)]", "[(9, 3), (1, 0)]", "[(100, 7), (5, 5)]")},
       expect=("out of range",),
       n_variants=3),

    _t(id="pp-35-custom-exc", block="Practical Python", day=35, skill="Writing a custom exception",
       prompt=(
           "Define a `ValidationError(Exception)` carrying the offending field name. Write "
           "`validate(record)` that raises it when a required field is missing or empty, and returns "
           "a cleaned record otherwise. Print the result for <<records>>, showing which field failed "
           "each time."),
       solution='''RECORDS = [
    {'name': 'Asha', 'email': 'a@b.co'},
    {'name': 'Rohan'},
    {'email': 'c@d.co'},
]


class ValidationError(Exception):
    def __init__(self, field):
        self.field = field
        super().__init__(f'missing field: {field}')


REQUIRED = ('name', 'email')


def validate(record):
    out = {}
    for key in REQUIRED:
        # A required field that is absent is as much a failure as one that is
        # present but empty, so both are checked explicitly.
        if key not in record:
            raise ValidationError(key)
        value = record[key]
        if value is None or value == '':
            raise ValidationError(key)
        out[key] = value
    return out


def main(records=RECORDS):
    for record in records:
        try:
            print('ok:', validate(record))
        except ValidationError as err:
            print('rejected on', err.field)


main()''',
       required_patterns=("class ", "Exception", "raise ", "except "),
       # Every pool contains at least one invalid record, so every variant
       # exercises the failure path as well as the success path.
       params={"records": ("[{'name': 'Asha', 'email': 'a@b.co'}, {'name': 'Rohan'}, {'email': 'c@d.co'}]",
                           "[{'a': 1}, {'a': ''}, {'a': 3}]",
                           "[{'x': 1, 'y': 2}, {'x': 1}, {}]")},
       expect=("rejected on",),
       n_variants=3),

    _t(id="pp-36-files", block="Practical Python", day=36, skill="Reading and writing text files",
       prompt=(
           "Using a temporary file, write the lines <<lines>> one per line, then read the file back "
           "and print each line with its 1-based line number. Finish by using a `with` block for both "
           "operations and print how many lines were read, so the file is always closed."),
       solution='''LINES = ['first', 'second', 'third']


def write_lines(path, lines):
    with open(path, 'w', encoding='utf-8') as handle:
        for line in lines:
            handle.write(line + chr(10))
    return path


def read_lines(path):
    with open(path, encoding='utf-8') as handle:
        return [line.rstrip(chr(10)) for line in handle]


def main(lines=LINES):
    import tempfile, os
    fd, path = tempfile.mkstemp(suffix='.txt')
    os.close(fd)
    try:
        write_lines(path, lines)
        got = read_lines(path)
        for number, line in enumerate(got, 1):
            print(f'{number}: {line}')
        print('lines read:', len(got))
    finally:
        os.unlink(path)


main()''',
       required_patterns=("def ", "with open(", "for ", "print("),
       params={"lines": ("['first', 'second', 'third']", "['only']",
                         "['a', 'b', 'c', 'd', 'e']")},
       expect=("lines read:",),
       n_variants=3),

    _t(id="pp-37-csv", block="Practical Python", day=37, skill="Reading and writing CSV",
       prompt=(
           "Write the records <<records>> to a temporary CSV file with a header row, read them back "
           "with `csv.DictReader`, and print each row's columns and total row count. Use the `csv` "
           "module rather than splitting on commas by hand, and say so in a comment."),
       solution='''RECORDS = [('Asha', 88), ('Rohan', 74), ('Meera', 91)]


def write_csv(path, records):
    # The csv module handles quoting; splitting on commas by hand does not.
    import csv
    with open(path, 'w', encoding='utf-8', newline='') as handle:
        writer = csv.writer(handle)
        writer.writerow(['name', 'score'])
        for name, score in records:
            writer.writerow([name, score])


def read_csv(path):
    import csv
    with open(path, encoding='utf-8', newline='') as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def main(records=RECORDS):
    import tempfile, os
    fd, path = tempfile.mkstemp(suffix='.csv')
    os.close(fd)
    try:
        write_csv(path, records)
        rows = read_csv(path)
        for row in rows:
            print(row['name'], row['score'])
        print('row count:', len(rows))
    finally:
        os.unlink(path)


main()''',
       required_patterns=("import csv", "DictReader", "def ", "print("),
       params={"records": ("[('Asha', 88), ('Rohan', 74), ('Meera', 91)]",
                          "[('A', 1), ('B', 2)]",
                          "[('X', 10), ('Y', 20), ('Z', 30), ('W', 40)]")},
       expect=("row count:",),
       n_variants=3),

    _t(id="pp-38-json", block="Practical Python", day=38, skill="JSON round-trips",
       prompt=(
           "Serialise the record <<record>> to a JSON string with sorted keys, print the string, "
           "then parse it back and print the restored record. Also print what happens when parsing "
           "malformed JSON, caught as ValueError, so the failure path is explicit."),
       solution='''RECORD = {'name': 'Asha', 'scores': [88, 74], 'active': True}


def main(record=RECORD):
    import json

    text = json.dumps(record, sort_keys=True)
    print('serialised:', text)
    restored = json.loads(text)
    print('restored :', restored)
    print('round trip equal:', restored == record)
    try:
        json.loads('{"name": }')
    except ValueError as err:
        print('malformed rejected:', type(err).__name__)


main()''',
       required_patterns=("import json", "dumps", "loads", "print("),
       params={"record": ("{'name': 'Asha', 'scores': [88, 74], 'active': True}",
                          "{'id': 1, 'tags': ['a', 'b'], 'ok': False}",
                          "{'x': 1.5, 'y': None}")},
       expect=("round trip equal: True",),
       n_variants=3),

    _t(id="pp-39-comprehensions", block="Practical Python", day=39, skill="Comprehensions versus loops",
       prompt=(
           "For <<values>>, write the same result three ways: a loop into a list, a list "
           "comprehension, and a generator expression. Print each result, confirm all three agree, "
           "and print the memory hint that a comprehension builds a list while a generator does not."),
       solution='''VALUES = [1, 2, 3, 4, 5, 6]


def by_loop(values):
    out = []
    for v in values:
        if v % 2 == 0:
            out.append(v * 10)
    return out


def by_comprehension(values):
    return [v * 10 for v in values if v % 2 == 0]


def by_generator(values):
    return (v * 10 for v in values if v % 2 == 0)


def main(values=VALUES):
    a = by_loop(values)
    b = by_comprehension(values)
    c = list(by_generator(values))
    print('loop        :', a)
    print('comprehension:', b)
    print('generator   :', c)
    print('all agree   :', a == b == c)
    print('hint: the comprehension materialises a list; the generator is lazy')


main()''',
       required_patterns=("def ", "for ", "return", "print("),
       params={"values": ("[1, 2, 3, 4, 5, 6]", "[1, 2, 3]", "[2, 4, 6, 8, 10, 12, 14]")},
       expect=("all agree   : True",),
       n_variants=3),

    _t(id="pp-40-lambda", block="Practical Python", day=40, skill="Lambdas and the key function",
       prompt=(
           "Sort the records <<records>> three ways: by score descending with a lambda, with a "
           "named function, and with `operator.itemgetter`. Print each ordering and confirm they "
           "agree, showing when a lambda is clearer than a named function and when it is not."),
       solution='''RECORDS = [('Asha', 88), ('Rohan', 74), ('Meera', 91), ('Kabir', 66)]


def by_score(record):
    return -record[1]


def main(records=RECORDS):
    import operator

    with_lambda = sorted(records, key=lambda r: -r[1])
    with_named = sorted(records, key=by_score)
    with_getter = sorted(records, key=operator.itemgetter(1), reverse=True)
    print('lambda:', with_lambda)
    print('named :', with_named)
    print('getter:', with_getter)
    print('all agree:', with_lambda == with_named == with_getter)


main()''',
       required_patterns=("def ", "lambda", "sorted(", "print("),
       params={"records": ("[('Asha', 88), ('Rohan', 74), ('Meera', 91), ('Kabir', 66)]",
                          "[('A', 1), ('B', 9), ('C', 5)]",
                          "[('P', 50), ('Q', 20), ('R', 70), ('S', 60), ('T', 30)]")},
       expect=("all agree: True",),
       n_variants=3),

    _t(id="pp-41-iterators", block="Practical Python", day=41, skill="Iterators and iterables",
       prompt=(
           "Write `countdown(n)` returning an iterator that yields from n down to 1, and show that "
           "it is exhausted after one pass: print the first list, then print a second list from the "
           "same iterator to show it is empty. Also print `iter(<<values>>) is iter(<<values>>)` to "
           "show a list is not its own iterator."),
       solution='''VALUES = [1, 2, 3]


def countdown(n):
    while n > 0:
        yield n
        n -= 1


def main(values=VALUES):
    it = countdown(5)
    print('first pass :', list(it))
    print('second pass:', list(it))
    print('list is its own iterator:', iter(values) is values)
    print('iterator is its own iterator:', iter(it) is it)


main()''',
       required_patterns=("def ", "yield", "iter(", "print("),
       params={"values": ("[1, 2, 3]", "['a', 'b']", "[1]")},
       expect=("second pass: []",),
       n_variants=3),

    _t(id="pp-42-generators", block="Practical Python", day=42, skill="Generators and laziness",
       prompt=(
           "Write `fib(limit)` as a generator yielding Fibonacci numbers, and print the first <<n>> "
           "values. Then write `cumulative(values)` yielding the running total, and show that it "
           "never materialises a list by printing how many values it produced for an input of that "
           "length."),
       solution='''def fib(limit):
    a, b = 0, 1
    for _ in range(limit):
        yield a
        a, b = b, a + b


def cumulative(values):
    total = 0
    for v in values:
        total += v
        yield total


def main(n=<<n>>):
    print('fib:', list(fib(n)))
    values = list(range(1, 11))
    produced = 0
    for _ in cumulative(values):
        produced += 1
    print('input length :', len(values))
    print('values yielded:', produced)
    print('last total   :', list(cumulative(values))[-1])


main()''',
       required_patterns=("def ", "yield", "for ", "print("),
       params={"n": ("8", "10", "6")},
       expect=("fib:",),
       n_variants=3),

    _t(id="pp-43-recursion", block="Practical Python", day=43, skill="Recursion and its base case",
       prompt=(
           "Write `factorial(n)` recursively, raising `RecursionError` for a negative input and "
           "returning 1 for 0. Then write `flatten(nested)` that recursively flattens a nested list "
           "of depth <<depth>>. Print the factorial of <<n>> and the flattened depth-<<depth>> list, "
           "and print the recursion limit you were given so the cost is visible."),
       solution='''NESTED = [1, [2, [3, [4]]]]


def factorial(n):
    if n < 0:
        raise ValueError('n must not be negative')
    if n == 0:
        return 1
    return n * factorial(n - 1)


def flatten(nested):
    out = []
    for item in nested:
        if isinstance(item, list):
            out.extend(flatten(item))
        else:
            out.append(item)
    return out


def main(n=<<n>>):
    import sys
    print(f'factorial({n}) =', factorial(n))
    print('flattened:', flatten(NESTED))
    print('depth:', <<depth>>, 'recursion limit:', sys.getrecursionlimit())


main()''',
       required_patterns=("def ", "return ", "isinstance", "print("),
       params={"n": ("5", "6", "3"), "depth": ("4", "3", "2")},
       expect=("flattened:",),
       n_variants=3),

    _t(id="pp-44-cli", block="Practical Python", day=44, skill="Assembling a small command-line tool",
       prompt=(
           "Build a tiny tool: `normalise(pairs)` collapses whitespace and lowercases each label, and "
           "`report(pairs)` prints an index, the normalised label and the count. Use <<pairs>> and print "
           "the report plus the total number of characters normalised away, so the tool has a visible "
           "result rather than only side effects."),
       solution='''PAIRS = [('  Ada Lovelace  ', 3), ('Grace   Hopper', 1), ('  ALAN  TURING', 2)]


def normalise(pairs):
    return [(' '.join(label.split()).lower(), n) for label, n in pairs]


def report(pairs):
    rows = normalise(pairs)
    saved = 0
    for index, (label, n) in enumerate(rows, 1):
        saved += 0
        print(f'{index:>2}. {label:<18} {n}')
    return rows


def main(pairs=PAIRS):
    original = sum(len(label) for label, _ in pairs)
    rows = report(pairs)
    cleaned = sum(len(label) for label, _ in rows)
    print('rows:', len(rows))
    print('characters removed by normalising:', original - cleaned)


main()''',
       required_patterns=("def ", "for ", "enumerate(", "print("),
       params={"pairs": ("[('  Ada Lovelace  ', 3), ('Grace   Hopper', 1), ('  ALAN  TURING', 2)]",
                          "[('A B', 1), ('  C  D  ', 2)]",
                          "[('  x  ', 1), ('y   z', 2), ('   w', 3)]")},
       expect=("rows:",),
       n_variants=3),
)


SOFTWARE_ENGINEERING: tuple[ExerciseTemplate, ...] = (

    _t(id="se-45-style", block="Software Engineering", day=45, skill="Naming and readable structure",
       prompt=(
           "Write `total_spend(items)` where each item is a (name, amount) pair. Use names that say "
           "what a value is, keep lines under a readable length, and return the total for "
           "<<items>>. Then print the total and, deliberately, a badly named version, and explain in "
           "a comment why the second one is worse even though it works."),
       solution='''ITEMS = [('rent', 950), ('food', 420), ('travel', 180)]


def total_spend(items):
    running_total = 0
    for item_name, amount in items:
        running_total += amount
    return running_total


def t(i):
    return sum(a for _, a in i)


def main(items=ITEMS):
    print('readable name :', total_spend(items))
    # The version below works and is still worse: `t` and `i` say nothing about
    # what they hold, so a reader has to infer both meanings from the call site.
    print('opaque names  :', t(items))


main()''',
       required_patterns=("def ", "for ", "return", "print("),
       params={"items": ("[('rent', 950), ('food', 420), ('travel', 180)]",
                         "[('a', 1), ('b', 2), ('c', 3)]",
                         "[('rent', 1200), ('bills', 300)]")},
       expect=("readable name :",),
       n_variants=3),

    _t(id="se-46-docstrings", block="Software Engineering", day=46, skill="Docstrings that say more than the name",
       prompt=(
           "Write `repeat(text, times)` with a docstring stating what it returns, what it raises, and "
           "one worked example. Reject a negative `times` with ValueError. Print the docstring's "
           "first line and run the example, so the docstring is shown doing its job rather than "
           "merely existing."),
       solution='''def repeat(text, times):
    """Return `text` repeated `times` times with no separator.

    Args:
        text: the string to repeat.
        times: how many copies to produce.

    Returns:
        A string of length len(text) * times.

    Raises:
        ValueError: if times is negative.

    Example:
        >>> repeat('ab', 3)
        'ababab'
    """
    if times < 0:
        raise ValueError('times must not be negative')
    return text * times


def main():
    doc = repeat.__doc__ or ''
    print('first line:', doc.splitlines()[0])
    print('example   :', repeat('ab', 3))
    try:
        repeat('ab', -1)
    except ValueError as err:
        print('raised    :', err)


main()''',
       required_patterns=('"""', "def ", "raise ", "print("),
       params={},
       expect=("first line:",),
       n_variants=1),

    _t(id="se-47-typing", block="Software Engineering", day=47, skill="Type hints that catch real mistakes",
       prompt=(
           "Annotate `average(values: list[float]) -> float` and `label(score: float) -> str`. Print "
           "the annotations with `__annotations__` so they are visible, then call `average` with "
           "<<values>> and print the result. Passing a list of the wrong kind is the mistake these "
           "hints are meant to surface, so say so in a comment."),
       solution='''from typing import List


def average(values: List[float]) -> float:
    # The hint is documentation first and a tool second, but it does make the
    # expected element type explicit at the call site.
    if not values:
        raise ValueError('values must not be empty')
    return sum(values) / len(values)


def label(score: float) -> str:
    return 'pass' if score >= 50 else 'fail'


def main(values: List[float]):
    print('average hints:', average.__annotations__)
    print('label hints  :', label.__annotations__)
    print('average      :', average(values))
    print('label        :', label(average(values)))


main([<<values>>])''',
       required_patterns=("def ", "-> ", ": List", "print("),
       params={"values": ("88.0, 74.0, 91.0", "1.5, 2.5", "60.0, 70.0, 80.0, 90.0")},
       expect=("average      :",),
       n_variants=3),

    _t(id="se-48-venv", block="Software Engineering", day=48, skill="Virtual environments and isolation",
       prompt=(
           "Model what a virtual environment gives you without creating one: write `environment_report()` "
           "that reports the interpreter path, whether the process is inside a virtual environment, and "
           "the first few entries on the import path. Use <<packages>> to list the third-party packages "
           "you can currently import. Print all of it, since the point is to see where code is looking."),
       solution='''PACKAGES = <<packages>>


def environment_report():
    import sys, os
    return {
        'interpreter': sys.executable,
        'in_venv': sys.prefix != sys.base_prefix,
        'path_head': sys.path[:3],
    }


def installed(packages):
    import importlib.util
    found, missing = [], []
    for name in packages:
        (found if importlib.util.find_spec(name) else missing).append(name)
    return found, missing


def main(packages=PACKAGES):
    report = environment_report()
    for key in ('interpreter', 'in_venv'):
        print(f'{key:<12}: {report[key]}')
    for entry in report['path_head']:
        print('  path       :', entry)
    found, missing = installed(packages)
    print('found       :', found or 'none')
    print('missing     :', missing or 'none')


main()''',
       required_patterns=("def ", "import ", "sys", "print("),
       params={"packages": ("['fastapi', 'pytest']", "['json', 'csv']", "['fastapi', 'pydantic', 'uvicorn']")},
       expect=("in_venv",),
       n_variants=3),

    _t(id="se-49-pip", block="Software Engineering", day=49, skill="Declaring and pinning dependencies",
       prompt=(
           "Write `parse_requirements(text)` that reads a requirements listing, strips comments and "
           "blank lines, splits each `name==version` pin into a name and a version, and rejects an "
           "unpinned requirement with ValueError. Print the parsed pins for <<requirements>> and the "
           "error for any unpinned entry, so both outcomes are visible."),
       solution='''REQUIREMENTS = <<requirements>>


def parse_requirements(text):
    pins = {}
    for raw in text.splitlines():
        line = raw.split('#', 1)[0].strip()
        if not line:
            continue
        if '==' not in line:
            raise ValueError(f'not pinned: {line!r}')
        name, version = line.split('==', 1)
        pins[name.strip()] = version.strip()
    return pins


def main(text=REQUIREMENTS):
    try:
        pins = parse_requirements(text)
    except ValueError as err:
        print('rejected:', err)
        return
    for name in sorted(pins):
        print(f'{name}=={pins[name]}')


main()''',
       required_patterns=("def ", "raise ", "split(", "print("),
       params={"requirements": ('"fastapi==0.115.6\\nuvicorn>=0.34.0"', '"# comment\\n\\na==1.0\\nb==2.0"',
                                '"x==1\\ny\\nz==3"')},
       expect=("",),
       n_variants=3),

    _t(id="se-50-structure", block="Software Engineering", day=50, skill="Project layout and import boundaries",
       prompt=(
           "Model a small project layout: `build_tree(files)` returns a nested dict of directories to "
           "file names, and `import_map(tree)` returns which module would be imported for each path. "
           "Use <<files>> and print the tree and the import map, so the boundary between a package's "
           "modules and its data files is visible."),
       solution='''FILES = <<files>>


def build_tree(files):
    tree = {}
    for path in files:
        parts = path.split('/')
        node = tree
        for part in parts[:-1]:
            node = node.setdefault(part, {})
        node[parts[-1]] = True
    return tree


def modules(files):
    out = []
    for path in files:
        if path.endswith('.py'):
            out.append(path[:-3].replace('/', '.'))
        else:
            out.append(f'{path} (data, not importable)')
    return out


def main(files=FILES):
    print('tree:')
    for name, value in sorted(build_tree(files).items()):
        # A top-level entry is either a directory or a file, and the marker for
        # a file is a plain True, so the two must be printed differently.
        if value is True:
            print(f'  {name} (file)')
        else:
            print(f'  {name}/ {sorted(value)}')
    print('imports:')
    for name in modules(files):
        print('  ', name)


main()''',
       required_patterns=("def ", "for ", "split(", "print("),
       params={"files": ("['app/main.py', 'app/routers/api.py', 'app/models.py', 'data/seed.json']",
                         "['pkg/__init__.py', 'pkg/core.py', 'README.md']",
                         "['src/lib/a.py', 'src/lib/b.py', 'tests/test_a.py', 'pyproject.toml']")},
       expect=("imports:",),
       n_variants=3),

    _t(id="se-51-git", block="Software Engineering", day=51, skill="A commit history you could bisect",
       prompt=(
           "Model commits as (sha, message, files_changed). Write `history(commits)` that prints each "
           "commit in order, and `files_touched(commits)` returning the files that changed more than "
           "once, which are the ones worth splitting into their own commit. Use <<commits>> and print "
           "both, so the argument for small commits is visible rather than asserted."),
       solution='''COMMITS = <<commits>>


def history(commits):
    for sha, message, files in commits:
        print(f'{sha}  {message}')
        print(f'          {", ".join(files)}')


def files_touched(commits):
    counts = {}
    for _sha, _message, files in commits:
        for name in files:
            counts[name] = counts.get(name, 0) + 1
    return sorted(name for name, n in counts.items() if n > 1)


def main(commits=COMMITS):
    print('history:')
    history(commits)
    print('changed more than once:', files_touched(commits))


main()''',
       required_patterns=("def ", "for ", "get(", "print("),
       params={"commits": ("""[('a1b2c3', 'add parser', ['app/parse.py']), ('d4e5f6', 'parser handles empty input', ['app/parse.py', 'tests/test_parse.py']), ('7a8b9c', 'rename flag', ['app/parse.py'])]""",
                           """[('aaa111', 'initial', ['a.py', 'b.py']), ('bbb222', 'fix a', ['a.py']), ('ccc333', 'fix b', ['b.py'])]""",
                           """[('111', 'one', ['x.py']), ('222', 'two', ['x.py', 'y.py']), ('333', 'three', ['y.py', 'z.py'])]""")},
       expect=("changed more than once:",),
       n_variants=3),

    _t(id="se-52-branches", block="Software Engineering", day=52, skill="Branches and conflicts",
       prompt=(
           "Model a three-way merge. Start from the base lines <<base>>, change one line on our side "
           "and the same line differently on theirs, and write `merge(base, ours, theirs)` that "
           "reports each line as `ours`, `theirs`, `both` or `conflict`. Print the classification so "
           "a conflict is visible as a conflict rather than silently resolved."),
       solution='''BASE = <<base>>


def merge(base, ours, theirs):
    out = []
    for b, o, t in zip(base, ours, theirs):
        if o == t:
            out.append(('both', o))
        elif o == b:
            out.append(('theirs', t))
        elif t == b:
            out.append(('ours', o))
        else:
            out.append(('conflict', f'{o!r} vs {t!r}'))
    return out


def main(base=BASE):
    ours = list(base)
    theirs = list(base)
    ours[0] = 'ours changed this'
    theirs[0] = 'theirs changed this'
    for where, line in merge(base, ours, theirs):
        print(f'{where:<9} {line}')


main()''',
       required_patterns=("def ", "for ", "zip(", "print("),
       params={"base": ("['shared', 'other', 'third']", "['a', 'b', 'c', 'd']", "['one', 'two']")},
       expect=("conflict",),
       n_variants=3),

    _t(id="se-53-unit-tests", block="Software Engineering", day=53, skill="Unit tests with plain asserts",
       prompt=(
           "Write `parse_price(text)` that returns a float price from a string, raising ValueError on "
           "anything malformed. Then write `test_parse_price()` using bare `assert` statements to "
           "cover a good input, a zero, and a bad input caught by `pytest.raises`-style handling. Run "
           "the test function and print whether it passed, using only the standard library."),
       solution='''def parse_price(text):
    if not text or text[0] not in '0123456789':
        raise ValueError(f'not a price: {text!r}')
    return float(text.rstrip('p').strip())


def raises(fn, *args):
    try:
        fn(*args)
    except ValueError:
        return True
    return False


def test_parse_price():
    assert parse_price('12.50') == 12.5
    assert parse_price('0') == 0.0
    assert raises(parse_price, 'abc')
    assert raises(parse_price, '')


def main():
    try:
        test_parse_price()
        print('test_parse_price: PASSED')
    except AssertionError as err:
        print('test_parse_price: FAILED', err)


main()''',
       required_patterns=("def ", "assert ", "raise ", "print("),
       params={},
       expect=("PASSED",),
       n_variants=1),

    _t(id="se-54-pytest", block="Software Engineering", day=54, skill="Parametrised tests and assertions",
       prompt=(
           "Using only the standard library, write a small test runner that takes a list of "
           "`(name, function)` cases and reports each pass or fail. Define cases for `add`, "
           "`multiply` and `divide`, including a division by zero that must raise, then run the "
           "runner over the built-in cases plus <<extra>> and print the tally. This is what a test "
           "framework does for you, in miniature."),
       solution='''def add(a, b):
    return a + b


def multiply(a, b):
    return a * b


def divide(a, b):
    if b == 0:
        raise ZeroDivisionError('division by zero')
    return a / b


def run(cases):
    passed = failed = 0
    for name, fn, args, expected in cases:
        try:
            got = fn(*args)
            ok = got == expected
        except Exception:
            ok = False
        if ok:
            passed += 1
            print(f'PASS {name}')
        else:
            failed += 1
            print(f'FAIL {name}')
    return passed, failed


def main(extra=<<extra>>):
    cases = [
        ('add', add, (2, 3), 5),
        ('multiply', multiply, (4, 5), 20),
        ('divide zero', divide, (1, 0), None),
    ]
    cases.extend(extra)
    passed, failed = run(cases)
    print(f'{passed} passed, {failed} failed')


main()''',
       required_patterns=("def ", "raise ", "for ", "try:", "print("),
       params={"extra": ("[]", "[('add big', add, (100, 200), 300)]", "[('mul zero', multiply, (0, 9), 0)]")},
       expect=("passed,",),
       n_variants=3),

    _t(id="se-55-fixtures", block="Software Engineering", day=55, skill="Reusable test setup",
       prompt=(
           "Write a `make_fixture()` factory that returns a fresh mutable sample list each time it is "
           "called, then show why sharing one list between tests is a bug: mutate the list returned by "
           "the first call and print the length seen by a second call. Use <<n>> as the starting size. "
           "The demonstration is the lesson."),
       solution='''SAMPLE = [[1, 2, 3, 4, 5, 6, 7, 8, 9, 10][:<<n>>]]


def make_fixture(base):
    # A new list per call, so one test cannot corrupt another's data.
    return list(base)


def main(base=SAMPLE):
    first = make_fixture(base)
    print('first call  :', first)
    first.append(999)
    second = make_fixture(base)
    print('after mutate, second call:', second)
    print('independent:', 999 not in second)
    shared = base
    one, two = shared, shared
    one.append(111)
    print('shared shows the change :', 111 in two)


main()''',
       required_patterns=("def ", "append(", "return", "print("),
       params={"n": ("10", "5", "8")},
       expect=("independent: True",),
       n_variants=3),

    _t(id="se-56-logging", block="Software Engineering", day=56, skill="Logging instead of print",
       prompt=(
           "Configure the standard `logging` module to write to a temporary file at INFO level, log a "
           "start, a warning and an error with `extra` context, then read the file back and print its "
           "lines. Show the level filter doing its job by logging one DEBUG line that must not appear."),
       solution='''import logging
import tempfile
import os


def main():
    fd, path = tempfile.mkstemp(suffix='.log')
    os.close(fd)
    try:
        logging.basicConfig(filename=path, level=logging.INFO, force=True,
                            format='%(levelname)s %(message)s')
        log = logging.getLogger('batch')
        log.debug('this line is filtered out')
        log.info('batch started with %d rows', 3)
        log.warning('row 2 skipped', extra={'row': 2})
        log.error('batch failed')
        logging.shutdown()
        with open(path, encoding='utf-8') as handle:
            lines = [line.rstrip() for line in handle if line.strip()]
        for line in lines:
            print(line)
        print('debug line present:', any('filtered out' in l for l in lines))
    finally:
        os.unlink(path)


main()''',
       required_patterns=("import logging", "basicConfig", "getLogger", "print("),
       params={},
       expect=("debug line present: False",),
       n_variants=1),

    _t(id="se-57-config", block="Software Engineering", day=57, skill="Configuration with defaults",
       prompt=(
           "Write `load_config(text)` that reads `key=value` lines, ignores blanks and `#` comments, "
           "coerces numbers and booleans, and falls back to supplied defaults for missing keys. Use "
           "<<config>> and print the loaded settings and the defaults that were applied, so what came "
           "from the file and what came from code is distinguishable."),
       solution='''CONFIG = <<config>>


def coerce(raw):
    if raw.lower() in ('true', 'false'):
        return raw.lower() == 'true'
    try:
        return int(raw)
    except ValueError:
        pass
    try:
        return float(raw)
    except ValueError:
        return raw


def load_config(text, defaults):
    settings = dict(defaults)
    applied = []
    for raw in text.splitlines():
        line = raw.split('#', 1)[0].strip()
        if not line or '=' not in line:
            continue
        key, value = line.split('=', 1)
        settings[key.strip()] = coerce(value.strip())
        applied.append(key.strip())
    return settings, applied


def main(text=CONFIG):
    defaults = {'host': 'localhost', 'port': 8000, 'debug': False}
    settings, applied = load_config(text, defaults)
    for key in sorted(settings):
        print(f'{key:<6} = {settings[key]!r}')
    print('from file :', sorted(applied))
    print('from defaults:', sorted(set(settings) - set(applied)))


main()''',
       required_patterns=("def ", "for ", "split(", "print("),
       params={"config": ('"host=0.0.0.0\\nport=9000\\n# a comment\\ndebug=true"',
                          '"port=8080"',
                          '"host=example.org\\nport=443\\ndebug=false\\nextra=1.5"')},
       expect=("from defaults:",),
       n_variants=3),

    _t(id="se-58-refactor", block="Software Engineering", day=58, skill="Refactoring with a safety net",
       prompt=(
           "Write a long, repetitive `process(records)` that inlines validation, and a refactored "
           "version that pulls out `validate`, `transform` and `normalise` without changing behaviour. "
           "Print both outputs for <<records>> and assert they agree, which is what makes a refactor "
           "safe rather than a rewrite."),
       solution='''RECORDS = <<records>>


def validate(records):
    return [r for r in records if r.get('name')]


def transform(records):
    return [{'name': r['name'].strip(), 'score': int(r['score'])} for r in records]


def normalise(records):
    for r in records:
        r['name'] = ' '.join(r['name'].split()).lower()
    return records


def process(records):
    return normalise(transform(validate(records)))


def process_inline(records):
    # The original shape: everything in one body, each step easy to skip.
    out = []
    for r in records:
        if r.get('name'):
            name = r['name'].strip()
            if name:
                out.append({'name': ' '.join(name.split()).lower(), 'score': int(r['score'])})
    return out


def main(records=RECORDS):
    refactored = process([dict(r) for r in records])
    inline = process_inline([dict(r) for r in records])
    print('refactored:', refactored)
    print('inline    :', inline)
    print('behaviour unchanged:', refactored == inline)


main()''',
       required_patterns=("def ", "return", "for ", "print("),
       params={"records": ("[{'name': ' Asha ', 'score': '88'}, {'name': 'Rohan', 'score': '74'}]",
                          "[{'name': 'A B', 'score': '1'}]",
                          "[{'name': '  X  Y ', 'score': '9'}, {'name': 'Z', 'score': '2'}]")},
       expect=("behaviour unchanged: True",),
       n_variants=3),

    _t(id="se-59-debugging", block="Software Engineering", day=59, skill="A reproducible debugging loop",
       prompt=(
           "Write a function that is deliberately wrong, run it under `traceback` to capture the real "
           "error, then write `find_cause(tb_text)` that pulls out the exception type and the line "
           "number, and print a one-line diagnosis. Use <<data>> as the input, so the fix is a real "
           "fix rather than a description of one."),
       solution='''DATA = <<data>>


def average(values):
    return sum(values) / len(values)


def find_cause(tb_text):
    lines = [ln for ln in tb_text.strip().splitlines() if ln.strip()]
    last = lines[-1]
    parts = [p.strip() for p in last.split(',')]
    kind = parts[0]
    where = ''
    for part in parts[1:]:
        if part.startswith('line '):
            where = part
    return f'{kind} at {where}' if where else kind


def main(data=DATA):
    import traceback
    # The empty list always reproduces the failure, so the diagnosis step is
    # part of every variant rather than only when the drawn data happens to be empty.
    try:
        average([])
    except Exception:
        print('diagnosis:', find_cause(traceback.format_exc()))
    print('guarded on drawn data:', guarded(data))


def guarded(values):
    if not values:
        return 0.0
    return average(values)


main()''',
       required_patterns=("def ", "try:", "except ", "traceback", "print("),
       params={"data": ("[]", "[1, 2, 3]", "[5]")},
       expect=("diagnosis:",),
       n_variants=3),
)


ALGORITHMS_AND_MATH: tuple[ExerciseTemplate, ...] = (

    _t(id="am-60-design", block="Algorithms and Math", day=60, skill="Designing before coding",
       prompt=(
           "Write `design_problem(sizes)` that, given the input sizes <<sizes>>, counts how many "
           "operations a nested-loop algorithm performs and how many a single-loop one performs, "
           "then prints both counts and the ratio. The point is to estimate cost on paper before "
           "writing the loops."),
       solution='''SIZES = <<sizes>>


def design_problem(sizes):
    for n in sizes:
        nested = n * n
        single = n
        ratio = nested / single if single else 0
        print(f'n={n:<4} nested {nested:>6}  single {single:>5}  ratio {ratio:.1f}x')


def main(sizes=SIZES):
    design_problem(sizes)
    print('a quadratic beats a linear only while n is small')
    print('doubling n multiplies nested work by 4, single work by 2')


main()''',
       required_patterns=("def ", "for ", "return", "print("),
       params={"sizes": ("[10, 100, 1000]", "[4, 16, 64]", "[100, 1000, 10000]")},
       expect=("nested",),
       n_variants=3),

    _t(id="am-61-bigo", block="Algorithms and Math", day=61, skill="Big-O growth by measurement",
       prompt=(
           "Write `time_for(n, factor)` returning the operation count for an algorithm that does "
           "`factor` work per element at size `n`. Then write `classify(counts)` that labels a "
           "growth series as `linear`, `quadratic` or `factorial` by comparing successive ratios. "
           "Use <<sizes>> and print the counts and the classification, so the growth is measured "
           "rather than assumed."),
       solution='''SIZES = <<sizes>>


def time_for(n, factor):
    return n * factor


def classify(counts):
    labels = []
    for i in range(len(counts) - 1):
        ratio = counts[i + 1] / counts[i] if counts[i] else 0
        if ratio > 100:
            labels.append('quadratic')
        elif ratio > 10:
            labels.append('linear')
        else:
            labels.append('factorial')
    return labels


def main(sizes=SIZES):
    counts = [time_for(n, 3) for n in sizes]
    print('sizes :', sizes)
    print('counts:', counts)
    print('growth:', classify(counts))


main()''',
       required_patterns=("def ", "for ", "return", "print("),
       params={"sizes": ("[10, 20, 40, 80]", "[5, 10, 20, 40, 80]", "[2, 4, 8, 16]")},
       expect=("growth:",),
       n_variants=3),

    _t(id="am-62-lists", block="Algorithms and Math", day=62, skill="A hand-rolled linked list",
       prompt=(
           "Build a singly linked list from <<values>> without using a Python list, then write "
           "`to_list(node)` converting it back, and `length(node)` counting the nodes. Print the "
           "values, the length, and a reversed copy, so the links rather than the values are what "
           "the exercise manipulates."),
       solution='''VALUES = <<values>>


class Node:
    def __init__(self, value, nxt=None):
        self.value = value
        self.next = nxt


def build(values):
    head = None
    for v in reversed(values):
        head = Node(v, head)
    return head


def to_list(node):
    out = []
    while node is not None:
        out.append(node.value)
        node = node.next
    return out


def length(node):
    n = 0
    while node is not None:
        n += 1
        node = node.next
    return n


def reverse(node):
    prev = None
    while node is not None:
        node.next, prev, node = prev, node, node.next
    return prev


def main(values=VALUES):
    head = build(values)
    print('values :', to_list(head))
    print('length :', length(head))
    print('reversed:', to_list(reverse(build(values))))


main()''',
       required_patterns=("class ", "def ", "while ", "print("),
       params={"values": ("[1, 2, 3, 4, 5]", "[10, 20, 30]", "[7]")},
       expect=("reversed:",),
       n_variants=3),

    _t(id="am-63-stacks", block="Algorithms and Math", day=63, skill="Stacks and queues",
       prompt=(
           "Implement a stack with `push`, `pop` and `peek` that raises IndexError when empty, and a "
           "queue with `enqueue` and `dequeue` that does the same. Use <<values>>: fill the stack, "
           "drain it, and print the order; then fill the queue, drain it, and print the order. The "
           "two orders differ, and that difference is the lesson."),
       solution='''VALUES = <<values>>


def stack_ops(values):
    stack = []
    for v in values:
        stack.append(v)
    out = []
    while stack:
        out.append(stack.pop())
    return out


def queue_ops(values):
    queue = []
    for v in values:
        queue.append(v)
    out = []
    while queue:
        out.append(queue.pop(0))
    return out


def peek(values):
    if not values:
        raise IndexError('empty')
    return values[-1]


def main(values=VALUES):
    print('values  :', values)
    print('stack   :', stack_ops(values))
    print('queue   :', queue_ops(values))
    try:
        peek([])
    except IndexError as err:
        print('peek on empty rejected:', type(err).__name__)


main()''',
       required_patterns=("def ", "append(", "pop(", "print("),
       params={"values": ("[1, 2, 3, 4]", "['a', 'b', 'c']", "[1, 2, 3, 4, 5, 6]")},
       expect=("stack   :",),
       n_variants=3),

    _t(id="am-64-hashtables", block="Algorithms and Math", day=64, skill="Building a hash table",
       prompt=(
           "Write a `HashTable` class with `put`, `get` and `remove` that buckets by `hash(key) % "
           "size`, resolving collisions by chaining, and that rehashes when the load factor passes "
           "0.75. Put the pairs <<pairs>>, print the table state, remove one key, and print the size "
           "before and after so the rehash is visible."),
       solution='''PAIRS = <<pairs>>


class HashTable:
    def __init__(self, size=4):
        self.size = size
        self.buckets = [[] for _ in range(size)]
        self.count = 0

    def _index(self, key):
        return hash(key) % self.size

    def _load(self):
        return self.count / self.size

    def put(self, key, value):
        if self._load() > 0.75:
            old = self.buckets
            self.size *= 2
            self.buckets = [[] for _ in range(self.size)]
            self.count = 0
            for bucket in old:
                for k, v in bucket:
                    self.put(k, v)
        self.buckets[self._index(key)].append((key, value))
        self.count += 1

    def get(self, key, default=None):
        for k, v in self.buckets[self._index(key)]:
            if k == key:
                return v
        return default

    def remove(self, key):
        bucket = self.buckets[self._index(key)]
        for i, (k, _v) in enumerate(bucket):
            if k == key:
                bucket.pop(i)
                self.count -= 1
                return True
        return False


def main(pairs=PAIRS):
    table = HashTable()
    for k, v in pairs:
        table.put(k, v)
    print('size after puts:', table.size)
    for k, _v in pairs:
        print(f'  get({k!r}) ->', table.get(k))
    first = pairs[0][0]
    print('removed', first, table.remove(first))
    print('get after remove:', table.get(first, 'absent'))
    print('size now:', table.size)


main()''',
       required_patterns=("class ", "def ", "%", "print("),
       params={"pairs": ("""[('a', 1), ('b', 2), ('c', 3), ('d', 4), ('e', 5)]""",
                           """[('x', 10), ('y', 20), ('z', 30), ('w', 40)]""",
                           """[('k1', 1), ('k2', 2), ('k3', 3), ('k4', 4), ('k5', 5), ('k6', 6)]""")},
       expect=("size after puts:",),
       n_variants=3),

    _t(id="am-65-trees", block="Algorithms and Math", day=65, skill="Binary trees and traversal",
       prompt=(
           "Build a binary search tree from <<values>> by insertion, then write `inorder`, `preorder` "
           "and `height`. Print all three traversals and the height, so the sorted output of an "
           "in-order walk is visible and is the reason a search tree is worth building."),
       solution='''VALUES = <<values>>


class Tree:
    def __init__(self, value, left=None, right=None):
        self.value = value
        self.left = left
        self.right = right


def insert(root, value):
    if root is None:
        return Tree(value)
    if value < root.value:
        root.left = insert(root.left, value)
    else:
        root.right = insert(root.right, value)
    return root


def build(values):
    root = None
    for v in values:
        root = insert(root, v)
    return root


def inorder(node):
    if node is None:
        return []
    return inorder(node.left) + [node.value] + inorder(node.right)


def preorder(node):
    if node is None:
        return []
    return [node.value] + preorder(node.left) + preorder(node.right)


def height(node):
    if node is None:
        return 0
    return 1 + max(height(node.left), height(node.right))


def main(values=VALUES):
    root = build(values)
    print('inserted  :', values)
    print('inorder   :', inorder(root))
    print('preorder  :', preorder(root))
    print('height    :', height(root))
    print('inorder is sorted:', inorder(root) == sorted(values))


main()''',
       required_patterns=("class ", "def ", "return", "print("),
       params={"values": ("[50, 30, 70, 20, 40, 60, 80]", "[5, 3, 8, 1]", "[10, 20, 30, 40, 50]")},
       expect=("inorder is sorted: True",),
       n_variants=3),

    _t(id="am-66-graphs", block="Algorithms and Math", day=66, skill="Graphs and breadth-first search",
       prompt=(
           "Build an adjacency dict from <<edges>>, then write `bfs(graph, start)` returning the visit "
           "order and the distance from the start, and `components(graph)` counting connected groups. "
           "Print the BFS order with distances and the component count, so a traversal is a fact "
           "about the graph rather than a claim."),
       solution='''EDGES = <<edges>>


def build(edges):
    graph = {}
    for a, b in edges:
        graph.setdefault(a, []).append(b)
        graph.setdefault(b, []).append(a)
    for node in graph:
        graph[node].sort()
    return graph


def bfs(graph, start):
    order, distance = [start], {start: 0}
    queue = [start]
    while queue:
        node = queue.pop(0)
        for nxt in graph.get(node, []):
            if nxt not in distance:
                distance[nxt] = distance[node] + 1
                order.append(nxt)
                queue.append(nxt)
    return order, distance


def components(graph):
    seen, count = set(), 0
    for node in graph:
        if node in seen:
            continue
        count += 1
        order, _ = bfs(graph, node)
        seen.update(order)
    return count


def main(edges=EDGES):
    graph = build(edges)
    order, distance = bfs(graph, 'A')
    print('order    :', order)
    print('distance :', distance)
    print('components:', components(graph))


main()''',
       required_patterns=("def ", "for ", "while ", "print("),
       params={"edges": ("""[('A', 'B'), ('A', 'C'), ('B', 'D'), ('C', 'D'), ('E', 'F')]""",
                           """[('A', 'B'), ('B', 'C'), ('C', 'A')]""",
                           """[('X', 'Y'), ('Y', 'Z'), ('Z', 'X'), ('P', 'Q')]""")},
       expect=("components:",),
       n_variants=3),

    _t(id="am-67-searching", block="Algorithms and Math", day=67, skill="Searching a sorted list",
       prompt=(
           "Write `linear_search(values, target)` and `binary_search(values, target)`, both "
           "returning the index or -1, and `count_steps(fn, values, target)` that reports how many "
           "comparisons each made. Use <<values>> with target <<target>> and print the indices and "
           "both step counts, so the advantage of binary search is measured."),
       solution='''VALUES = <<values>>
TARGET = <<target>>


def linear_search(values, target):
    steps = 0
    for i, v in enumerate(values):
        steps += 1
        if v == target:
            return i, steps
    return -1, steps


def binary_search(values, target):
    lo, hi, steps = 0, len(values) - 1, 0
    while lo <= hi:
        steps += 1
        mid = (lo + hi) // 2
        if values[mid] == target:
            return mid, steps
        if values[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1, steps


def main(values=VALUES, target=TARGET):
    li, ls = linear_search(values, target)
    bi, bs = binary_search(values, target)
    print(f'values   : {values}')
    print(f'target   : {target}')
    print(f'linear   : index {li}, {ls} comparisons')
    print(f'binary   : index {bi}, {bs} comparisons')
    print('same answer:', li == bi)


main()''',
       required_patterns=("def ", "for ", "while ", "print("),
       params={"values": ("[1, 3, 5, 7, 9, 11, 13]", "[10, 20, 30, 40, 50, 60, 70, 80]",
                          "[2, 4, 6, 8, 10, 12, 14, 16, 18]"),
               "target": ("7", "35", "9")},
       expect=("same answer: True",),
       n_variants=3),

    _t(id="am-68-sorting", block="Algorithms and Math", day=68, skill="Sorting and verifying stability",
       prompt=(
           "Write `merge_sort(values)` and `is_sorted(values)`, then check stability by sorting "
           "(key, label) pairs on the key alone and printing whether equal keys kept their original "
           "order. Use <<values>> and print the sorted result, the verification, and the stability "
           "result."),
       solution='''VALUES = <<values>>
PAIRS = [('b', 1), ('a', 1), ('c', 0), ('d', 1)]


def merge_sort(values):
    if len(values) <= 1:
        return list(values)
    mid = len(values) // 2
    left = merge_sort(values[:mid])
    right = merge_sort(values[mid:])
    out = []
    i = j = 0
    while i < len(left) and j < len(right):
        # Taking from the left half on a tie is what makes this stable.
        if left[i] <= right[j]:
            out.append(left[i])
            i += 1
        else:
            out.append(right[j])
            j += 1
    return out + left[i:] + right[j:]


def is_sorted(values):
    return all(a <= b for a, b in zip(values, values[1:]))


def main(values=VALUES):
    result = merge_sort(values)
    print('before :', values)
    print('after  :', result)
    print('sorted :', is_sorted(result))
    by_key = merge_sort(PAIRS)
    ties = [p for p in by_key if p[1] == 1]
    print('ties kept in original order:', [t[0] for t in ties] == ['b', 'a', 'd'])


main()''',
       required_patterns=("def ", "return", "while ", "print("),
       params={"values": ("[38, 27, 43, 3, 9, 82, 10]", "[5, 4, 3, 2, 1]",
                          "[64, 25, 12, 22, 11, 90, 33, 7]")},
       expect=("sorted : True",),
       n_variants=3),

    _t(id="am-69-probability", block="Algorithms and Math", day=69, skill="Probability by simulation",
       prompt=(
           "Write `monte_carlo(trials, seed)` estimating the probability that two independent dice "
           "sum to more than <<threshold>>, using a seeded generator so the estimate is "
           "reproducible, and print the estimate with <<trials>> trials plus the exact fraction. The "
           "two should be close, and printing both makes the error visible."),
       solution='''THRESHOLD = <<threshold>>
TRIALS = <<trials>>


def exact(threshold):
    count = 0
    for a in range(1, 7):
        for b in range(1, 7):
            if a + b > threshold:
                count += 1
    return count / 36


def monte_carlo(threshold, trials, seed):
    import random
    rng = random.Random(seed)
    hits = 0
    for _ in range(trials):
        if rng.randint(1, 6) + rng.randint(1, 6) > threshold:
            hits += 1
    return hits / trials


def main(threshold=THRESHOLD, trials=TRIALS):
    estimate = monte_carlo(threshold, trials, 7)
    truth = exact(threshold)
    print(f'threshold sum > {threshold}')
    print(f'exact     : {truth:.4f}')
    print(f'estimated : {estimate:.4f} over {trials} trials')
    print(f'error     : {abs(estimate - truth):.4f}')


main()''',
       required_patterns=("def ", "random.Random", "for ", "print("),
       params={"threshold": ("7", "9", "5"), "trials": ("6000", "2000", "10000")},
       expect=("exact     :",),
       n_variants=3),

    _t(id="am-70-stats", block="Algorithms and Math", day=70, skill="Descriptive statistics",
       prompt=(
           "For <<values>>, write `describe(values)` returning count, mean, median, spread (the "
           "population standard deviation) and min/max, and print them. Then print the mean with and "
           "without the largest value so the difference between a mean and a median is visible on "
           "real numbers rather than asserted."),
       solution='''VALUES = <<values>>


def mean(values):
    return sum(values) / len(values)


def median(values):
    ordered = sorted(values)
    mid = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[mid]
    return (ordered[mid - 1] + ordered[mid]) / 2


def spread(values):
    m = mean(values)
    return (sum((v - m) ** 2 for v in values) / len(values)) ** 0.5


def describe(values):
    return {'n': len(values), 'mean': mean(values), 'median': median(values),
            'spread': spread(values), 'min': min(values), 'max': max(values)}


def main(values=VALUES):
    stats = describe(values)
    for key in ('n', 'mean', 'median', 'spread', 'min', 'max'):
        print(f'{key:<7}: {stats[key]:.4f}')
    trimmed = [v for v in values if v != max(values)]
    print(f'mean with max   : {mean(values):.4f}')
    print(f'mean without max: {mean(trimmed):.4f}')


main()''',
       required_patterns=("def ", "return", "sorted(", "print("),
       params={"values": ("[12, 15, 14, 13, 16, 15, 14, 200]", "[1, 2, 3, 4, 5]",
                          "[80, 85, 90, 95, 100, 400]")},
       expect=("median :",),
       n_variants=3),

    _t(id="am-71-vectors", block="Algorithms and Math", day=71, skill="Vector operations without a library",
       prompt=(
           "Write `add`, `scale`, `dot` and `magnitude` for plain Python lists, raising ValueError "
           "when the lengths differ. Use the pair of vectors <<pair>> and print each result, so the "
           "definitions are executable rather than symbolic."),
       solution='''PAIR = <<pair>>


def load(pair):
    a_text, b_text = pair
    import ast
    return ast.literal_eval(a_text), ast.literal_eval(b_text)


def add(a, b):
    if len(a) != len(b):
        raise ValueError('vectors must have equal length')
    return [x + y for x, y in zip(a, b)]


def scale(a, factor):
    return [x * factor for x in a]


def dot(a, b):
    if len(a) != len(b):
        raise ValueError('vectors must have equal length')
    return sum(x * y for x, y in zip(a, b))


def magnitude(a):
    return sum(x * x for x in a) ** 0.5


def main(pair=PAIR):
    a, b = load(pair)
    print('a        :', a)
    print('b        :', b)
    print('add      :', add(a, b))
    print('scale    :', scale(a, 2))
    print('dot      :', dot(a, b))
    print('magnitude:', round(magnitude(a), 4))


main()''',
       required_patterns=("def ", "zip(", "raise ", "print("),
       params={"pair": ("""("[1, 2, 3]", "[4, 5, 6]")""",
                         """("[2, 4, 6, 8]", "[1, 1, 1, 1]")""",
                         """("[5, 0, -3]", "[1, 1, 1]")""")},
       expect=("dot      :",),
       n_variants=3),

    _t(id="am-72-matrices", block="Algorithms and Math", day=72, skill="Matrices as nested lists",
       prompt=(
           "Represent a matrix as a list of rows. Write `shape`, `transpose`, `multiply` and "
           "`identity`, raising ValueError on a shape mismatch in `multiply`. Use the pair of "
           "matrices <<pair>> and print the shape, the transpose, and the product."),
       solution='''PAIR = <<pair>>


def load(pair):
    m_text, n_text = pair
    import ast
    return ast.literal_eval(m_text), ast.literal_eval(n_text)


def shape(matrix):
    rows = len(matrix)
    cols = len(matrix[0]) if rows else 0
    return rows, cols


def transpose(matrix):
    if not matrix:
        return []
    return [list(col) for col in zip(*matrix)]


def multiply(a, b):
    if shape(a)[1] != shape(b)[0]:
        raise ValueError(f'cannot multiply {shape(a)} by {shape(b)}')
    cols = shape(b)[1]
    return [[sum(a[i][k] * b[k][j] for k in range(shape(a)[1])) for j in range(cols)]
            for i in range(shape(a)[0])]


def identity(n):
    return [[1 if i == j else 0 for j in range(n)] for i in range(n)]


def main(pair=PAIR):
    m, n = load(pair)
    print('shape of m :', shape(m))
    print('transpose  :', transpose(m))
    print('m * n      :', multiply(m, n))
    print('identity 3 :', identity(3))


main()''',
       required_patterns=("def ", "zip(", "raise ", "print("),
       params={"pair": ("""("[[1, 2], [3, 4]]", "[[5, 6], [7, 8]]")""",
                         """("[[1, 2, 3], [4, 5, 6]]", "[[1, 0], [0, 1], [1, 1]]")""",
                         """("[[2, 0], [0, 2]]", "[[1, 1], [1, 1]]")""")},
       expect=("transpose  :",),
       n_variants=3),

    _t(id="am-73-functions", block="Algorithms and Math", day=73, skill="Functions plotted as data",
       prompt=(
           "Write `f(x)` returning <<f_expr>> for the given x, then `sample(fn, xs)` and "
           "`plot(fn, lo, hi, step)` returning a text chart built from a fixed-width block string, "
           "raising ValueError when `step` is not positive. Plot the function and print the chart, so "
           "its shape is something a reader can see."),
       solution='''def f(x):
    return <<f_expr>>


def sample(fn, xs):
    return [(x, fn(x)) for x in xs]


def plot(fn, lo, hi, step):
    if step <= 0:
        raise ValueError('step must be positive')
    if lo >= hi:
        raise ValueError('lo must be less than hi')
    xs = list(range(lo, hi, step)) or [lo]
    width = 40
    top = max(fn(x) for x in xs) or 1
    lines = []
    for x in xs:
        y = fn(x)
        filled = int(round(y / top * width))
        lines.append(f'x={x:<3} {y:>4} |' + '#' * max(0, filled))
    return lines


def main():
    for line in plot(f, -5, 10, 1):
        print(line)
    try:
        plot(f, 0, 5, 0)
    except ValueError as err:
        print('rejected:', err)


main()''',
       required_patterns=("def ", "return", "raise ", "print("),
       params={"f_expr": ("x ** 2", "abs(x)", "x * 2 + 1", "-x + 3")},
       expect=("rejected:",),
       n_variants=4),

    _t(id="am-74-problem", block="Algorithms and Math", day=74, skill="A worked problem end to end",
       prompt=(
           "Solve a small problem end to end: given coin values <<coins>> and an amount <<amount>>, "
           "write `fewest_coins(coins, amount)` that returns the fewest coins and how many ways reach "
           "it, raising ValueError when the amount cannot be made. Print the answer and the chosen "
           "coins, so the function's output is a result and not just a count."),
       solution='''COINS = <<coins>>
AMOUNT = <<amount>>


def fewest_coins(coins, amount):
    if amount < 0:
        raise ValueError('amount must not be negative')
    unreachable = amount + 1
    best = [unreachable] * (amount + 1)
    ways = [0] * (amount + 1)
    best[0], ways[0] = 0, 1
    for value in range(1, amount + 1):
        for coin in coins:
            if coin <= value and best[value - coin] + 1 < best[value]:
                best[value] = best[value - coin] + 1
                ways[value] = ways[value - coin]
            elif coin <= value and best[value - coin] + 1 == best[value]:
                ways[value] += ways[value - coin]
    if best[amount] == unreachable:
        raise ValueError(f'cannot make {amount} from {coins}')
    return best[amount], ways[amount]


def main(coins=COINS, amount=AMOUNT):
    count, ways = fewest_coins(coins, amount)
    print(f'coins  : {coins}')
    print(f'amount : {amount}')
    print(f'fewest : {count} coins, {ways} distinct ways')
    try:
        fewest_coins([4, 9], 7)
    except ValueError as err:
        print('impossible rejected:', err)


main()''',
       required_patterns=("def ", "raise ", "for ", "print("),
       params={"coins": ("[1, 5, 6, 9]", "[1, 3, 4]", "[2, 5, 10]"), "amount": ("11", "7", "27")},
       expect=("fewest :",),
       n_variants=3),
)
