"""Canonical topic batch: strings as an immutable sequence (Lutz ch 7)."""
from canonical_topics import topic

LUTZ_CH7 = {
    "book": "learning-python",
    "chapter": 7,
    "pages": [155, 196],
    "sections": ["Strings in Action", "Indexing and Slicing", "String Methods"],
}


topic(
    "canonical:string-as-immutable-sequence",
    "A string is an immutable sequence of characters, so every transforming method returns a new string",
    sources=[dict(LUTZ_CH7)],
    concept=(
        "A string is a sequence of characters, and it is immutable, which means no operation "
        "ever changes the string it is given. Indexing reads one character, slicing reads a "
        "run of them, and negative offsets count from the end, exactly as they do on a list; "
        "but assigning to a position raises an error, because there is no position to write "
        "into. Every method that looks like it modifies a string, whether it strips padding, "
        "splits on a separator, changes case, or replaces a substring, hands back a brand-new "
        "string and leaves the original untouched. That has two consequences worth learning "
        "before anything else. First, chaining works, because each method's result is itself "
        "a string with the same methods. Second, the common beginner bug of calling a "
        "transforming method and ignoring its result produces code that runs cleanly and "
        "does nothing. Immutability is also what makes strings safe to share between parts "
        "of a program and usable as mapping keys, because a value that cannot change cannot "
        "be invalidated later by somebody else holding a reference to it."
    ),
    prerequisites=["canonical:object-type-categories"],
    pitfalls=[
        "Calling a transforming method such as strip or replace without using the returned "
        "string, so the change silently never happens.",
        "Treating a string like a list and trying to assign to an index, which raises an "
        "error because strings have no writable positions.",
        "Expecting split to return a string instead of a list of strings, then indexing the "
        "result as if it were still text.",
    ],
    adapters={
        "machine-learning": {
            "framing": (
                "Raw labels arrive dirty: mixed case, stray spaces, trailing punctuation. "
                "Cleaning them is a chain of string methods, and each link in the chain is a "
                "new string."
            ),
            "application": (
                "Walk the example as a label being normalised before it is used as a category "
                "key. The raw value is stripped, lowered and replaced, and because every one of "
                "those methods returns a new string, the calls chain into one expression that "
                "reads in order. The original raw label is still intact afterwards, which is "
                "worth verifying, because it proves the transform never edited the input. Two "
                "records whose raw labels differ only in case or padding collapse to the same "
                "normalised key, which is the point of normalising, and it would not work if "
                "any step mutated in place. When a group-by later shows fewer categories than "
                "the raw data suggested, the cleaning chain is the reason, and the reason it "
                "is trustworthy is that every step is a pure function of its input."
            ),
            "example_hint": "chain strip, lower and replace to normalise raw labels into category keys",
            "assessment_angle": "why the chain works, what it returns at each step, and what happens to the raw input",
            "day": 3,
            "title": "Clean Labels with a Chain: Every Method Returns a New String",
            "code": """raw_labels = ["  SPAM ", "Ham", "spam,", " HAM ", "ham."]

def normalise(label):
    return label.strip().lower().replace(",", "").replace(".", "")

clean = [normalise(label) for label in raw_labels]
print("raw:", raw_labels)
print("clean:", clean)
print("unchanged raw:", raw_labels[0])
print("distinct:", sorted(set(clean)))
""",
            "questions": [
                "Why can the three transforms be written as one chained expression rather than three separate statements?",
                "After the loop runs, why does raw_labels[0] still show its original padding and case?",
                "What does the distinct count tell you about the raw labels, and which method made that reduction possible?",
            ],
            "answers": [
                "Because each method returns a new string, so the result of one is immediately a valid receiver for the next.",
                "Because strings are immutable, so strip, lower and replace build new strings and never write into the original label.",
                "That several raw labels differed only in case or punctuation, and lower plus the punctuation replacements collapsed them into shared keys.",
            ],
            "homework": (
                "Write normalise_labels.py with a list of at least six dirty labels containing mixed "
                "case, leading or trailing spaces, and at least two kinds of trailing punctuation. "
                "Write a normalise function that chains strip, lower and two replace calls, then "
                "print the raw list, the cleaned list, the first raw label to prove it is untouched, "
                "and the sorted set of distinct cleaned labels. Observable output: four lines, with "
                "the distinct count smaller than the raw count."
            ),
            "required_patterns": [".strip()", ".lower()", ".replace(", "set(", "print("],
        },
        "data-viz": {
            "framing": (
                "Axis and legend text has to fit a fixed width. Truncating or padding a label "
                "is string slicing and string methods, and the string never changes while you "
                "do it."
            ),
            "application": (
                "Walk the example as a legend being fitted to a column. A long label is sliced "
                "to a width and given an ellipsis, and a short one is padded with a method so "
                "the labels line up. Slicing with a positive stop takes a prefix, which is a "
                "sequence operation the string shares with lists, and the string methods that "
                "pad and centre return new strings. The important detail is that none of this "
                "edits the original category names, so the plot's labels and its data remain "
                "consistent even though the displayed text is shortened. When a chart shows a "
                "truncated label and a reader needs the full text, the full string is still "
                "available untouched, which is the practical payoff of immutability."
            ),
            "example_hint": "slice long labels to a width, pad short ones, keep the originals intact",
            "assessment_angle": "what slicing takes, what methods return, and why the original stays available",
            "day": 3,
            "title": "Fit Labels to a Column: Slice, Pad, Keep the Original",
            "code": """categories = ["Revenue", "Operating expenses", "Net income", "Tax"]
WIDTH = 14

def fit(label):
    if len(label) > WIDTH:
        return label[: WIDTH - 1] + "…"
    return label.ljust(WIDTH)

for name in categories:
    print(f"{fit(name)} | {len(name)} chars")

print("unchanged:", categories[1])
""",
            "questions": [
                "Why does the fit function use label[: WIDTH - 1] rather than assigning a shorter value back into the string?",
                "What does ljust return, and what happens to the original short label as a result?",
                "The full category name is shown truncated in the output. Where is the untruncated text still available, and why?",
            ],
            "answers": [
                "Because slicing is the way to take a prefix of a sequence, and strings have no writable position to assign a shorter value into.",
                "It returns a new string padded to the width with spaces; the original short label is untouched, since strings are immutable.",
                "In the original categories list, because every transformation produced a new string and left the source values exactly as they were.",
            ],
            "homework": (
                "Write fit_labels.py with a list of at least six category names of varying length. "
                "Write a fit function that slices any name longer than a chosen width and appends an "
                "ellipsis, and otherwise pads the name to that width. Print each fitted label beside "
                "the original length, then print the untouched original of the longest name. "
                "Observable output: one line per category plus a final line proving the originals "
                "survived."
            ),
            "required_patterns": ["len(", "[:", ".ljust(", "if ", "print("],
        },
        "api-building": {
            "framing": (
                "A URL path is a string with structure, and routing means splitting it apart "
                "and inspecting the pieces. Every step yields a new string or a list of "
                "strings, never an edit."
            ),
            "application": (
                "Walk the example as a router matching an incoming path. The path is stripped "
                "of its leading separator and split into segments, and split returns a list, "
                "so the code that consumes it is sequence code from that point on. Each "
                "segment is then inspected with methods that test rather than transform, "
                "which is worth distinguishing: startswith answers a question and returns a "
                "boolean, while replace returns a string, and confusing the two categories is "
                "a common silent bug. The original path string remains available for logging "
                "or error reporting throughout, which is why a handler can report the request "
                "it actually received even after it has dissected the path into pieces."
            ),
            "example_hint": "strip and split a path into segments, then test segments with string predicates",
            "assessment_angle": "which calls return strings, which return lists, and which return booleans",
            "day": 3,
            "title": "Split a Path, Keep It Intact: Routing Reads, Never Writes",
            "code": """path = "/api/v1/items/42"

segments = path.strip("/").split("/")
print("segments:", segments)
print("count:", len(segments))
print("first:", segments[0])
print("last is numeric:", segments[-1].isdigit())
print("has version prefix:", segments[1].startswith("v"))
print("original path:", path)
""",
            "questions": [
                "What does split return, and why does the code immediately switch to indexing and len?",
                "Why can the handler still print the original path after splitting it into segments?",
                "startswith and replace are both string methods. What category of answer does each one return, and why does that matter in a router?",
            ],
            "answers": [
                "It returns a list of strings, so from that point the code operates on a sequence and uses indexing and len rather than string methods.",
                "Because splitting is a transformation that returns a new list of new strings, leaving the original path string untouched.",
                "startswith returns a boolean that a condition can test directly, while replace returns a new string that has to be used; treating replace as a test makes the condition always true.",
            ],
            "homework": (
                "Write route_segments.py with at least five URL paths of varying depth. For each "
                "one, strip the surrounding separators, split into segments, and print the segment "
                "list, its length, the first and last segment, and whether the last segment is "
                "numeric. Finally print one original path unchanged. Observable output: five lines "
                "per path plus the closing line, with every string operation returning a value that "
                "is used."
            ),
            "required_patterns": [".strip(", ".split(", ".isdigit()", ".startswith(", "len("],
        },
        "web-scraping": {
            "framing": (
                "Scraped text is never clean. It arrives with whitespace, entity remnants and "
                "inconsistent separators, and cleaning it is a chain of non-mutating string "
                "methods."
            ),
            "application": (
                "Walk the example as a field being cleaned off a page. The raw cell text is "
                "stripped of surrounding whitespace, its internal runs of whitespace are "
                "collapsed, and a separator is normalised, so two cells that looked different "
                "on the page become the same field name. Each step returns a new string, and "
                "that is exactly what makes the chain safe to apply to untrusted input: the "
                "page's original text is never edited, so if a later step raises, the earlier "
                "work is still inspectable. The collapse step is the one that pays in "
                "practice, because inconsistent whitespace across pages is the most common "
                "reason a scrape yields duplicate-looking keys that do not match."
            ),
            "example_hint": "strip, collapse internal whitespace and normalise separators in scraped cells",
            "assessment_angle": "why cleaning is a chain of new strings and what that guarantees about the raw input",
            "day": 3,
            "title": "Clean Scraped Cells: Collapse, Normalise, Never Edit the Source",
            "code": """raw_cells = ["  Product   Name ", "product\tname", " Product Name ", "product  name"]

def clean_cell(text):
    return " ".join(text.split()).replace(" ", "_").lower()

clean = [clean_cell(cell) for cell in raw_cells]
print("raw:", raw_cells)
print("clean:", clean)
print("distinct fields:", sorted(set(clean)))
print("raw untouched:", repr(raw_cells[0]))
""",
            "questions": [
                "What does ' '.join(text.split()) achieve, and why does it work on both spaces and tabs?",
                "Why is the raw cell still exactly as it was after cleaning?",
                "Two raw cells differ only in whitespace kind and amount. What does the distinct count show, and which step caused it?",
            ],
            "answers": [
                "It splits the text on any run of whitespace, discarding the separators, then rejoins the words with single spaces, so tabs and multiple spaces collapse alike.",
                "Because every method in the chain returns a new string and strings are immutable, so the raw cell is never written into.",
                "That the two cells are the same field after cleaning, and the collapse step reduced them to one key by normalising the whitespace.",
            ],
            "homework": (
                "Write clean_cells.py with a list of at least six raw scraped strings containing "
                "leading and trailing spaces, internal runs of spaces or tabs, and mixed case. Write "
                "a clean_cell function that collapses whitespace, replaces spaces with underscores "
                "and lowercases the result. Print the raw list, the cleaned list, the sorted set of "
                "distinct fields, and the repr of one raw cell to prove it is unchanged. Observable "
                "output: four lines, with the distinct count smaller than the raw count."
            ),
            "required_patterns": [".split(", ".join(", ".lower(", ".replace(", "set("],
        },
        "testing-qa": {
            "framing": (
                "Assertions on text compare strings that were produced by different routes, "
                "and normalising both sides is what makes that comparison meaningful instead "
                "of brittle."
            ),
            "application": (
                "Walk the example as an assertion helper. Two strings are normalised the same "
                "way before comparison, and the helper returns a boolean, so the test can "
                "report the exact mismatch rather than a bare failure. Building the expected "
                "message from a template with formatting is the other half of the skill: the "
                "message is assembled from parts, and the parts are strings, so every join "
                "and replace is a new string. The reason normalisation lives in a helper is "
                "that the two sides come from different code paths, one computed and one "
                "authored, and their only guaranteed common ground is the cleaned form, so "
                "that is the only form worth comparing."
            ),
            "example_hint": "normalise both sides of a text assertion and build failure messages from parts",
            "assessment_angle": "why comparison happens on the normalised form and what the failure message is built from",
            "day": 3,
            "title": "Compare the Normalised Form, Report the Raw Mismatch",
            "code": """def normalise(text):
    return " ".join(text.split()).lower()

def assert_same(actual, expected):
    if normalise(actual) == normalise(expected):
        return True, "match"
    return False, f"got {actual!r}, want {expected!r}"

ok, message = assert_same("  Hello   World ", "hello world")
print("same after normalise:", ok, "|", message)

ok, message = assert_same("loaded 3 rows", "loaded 4 rows")
print("different:", ok, "|", message)
""",
            "questions": [
                "Why is the comparison performed on the normalised form instead of on the two raw strings?",
                "The failure message is built with an f-string from two values. What does each value contribute, and why is it shown with repr?",
                "normalise returns a string while assert_same returns a tuple. Why is that distinction useful to the caller?",
            ],
            "answers": [
                "Because the two sides arrive from different code paths with different whitespace and case, so only the cleaned form is a fair basis for comparison.",
                "The actual and expected values are inserted so the failure names both sides, and repr shows the exact whitespace and quoting that a plain display would hide.",
                "Because the caller needs both a boolean to branch on and a message to report, and a string alone cannot convey the pass or fail decision.",
            ],
            "homework": (
                "Write assert_text.py with a normalise function and an assert_same helper that "
                "returns a boolean and a message. Check at least five pairs: three that match only "
                "after normalisation and two that differ in content. For each pair print the "
                "decision and the message, and use repr in the message so whitespace is visible. "
                "Observable output: one line per pair, naming match or mismatch with both values."
            ),
            "required_patterns": [".split(", ".join(", ".lower(", "f\"", "print("],
        },
        "devops-scripting": {
            "framing": (
                "Log lines are strings with a fixed shape, and parsing one means splitting it "
                "into fields you can act on. The line is never modified, only read."
            ),
            "application": (
                "Walk the example as a log being filtered. Each line is split on a separator "
                "into fields, and because split returns a list, the field selection is "
                "sequence code from there. The level is compared after uppercasing, which "
                "returns a new string, so the raw line stays available for the report that "
                "prints it back. The pattern worth noticing is that parsing a line converts a "
                "string into structured values, and each conversion is one-way: split gives a "
                "list, join gives back a string, and the two are not interchangeable. When a "
                "filter matches the wrong lines, the first thing to check is which field "
                "index was compared, because off-by-one in a split result is the usual "
                "cause."
            ),
            "example_hint": "split log lines into fields, compare a field case-insensitively, print the matched line",
            "assessment_angle": "what split returns, why the comparison is uppercased, and what stays unchanged",
            "day": 3,
            "title": "Parse a Log Line: Split into Fields, Compare One, Keep the Line",
            "code": """lines = [
    "2026-09-27 INFO  service started",
    "2026-09-27 WARN  retrying connection",
    "2026-09-27 ERROR disk nearly full",
    "2026-09-27 INFO  cache warmed",
]

for line in lines:
    fields = line.split(None, 2)          # split on whitespace, at most 3 parts
    level = fields[1].upper()
    if level in ("WARN", "ERROR"):
        print(f"{level}: {fields[2]}")
print("total lines:", len(lines))
""",
            "questions": [
                "What does split(None, 2) return, and why does the code then use fields[1] and fields[2]?",
                "Why is the level uppercased before comparison, and what does that guarantee about the raw line?",
                "The loop prints a message built from fields but the total comes from len(lines). Why is the original list still complete?",
            ],
            "answers": [
                "A list of at most three strings, splitting on runs of whitespace, so the level is the second element and the message the third.",
                "So that mixed-case levels in the log match the comparison set, and because upper returns a new string the raw line is unchanged.",
                "Because splitting creates new strings in a new list and never edits the source lines, so the original list is intact for the count.",
            ],
            "homework": (
                "Write filter_logs.py with at least eight log lines in 'DATE LEVEL MESSAGE' form, "
                "using mixed case for the levels. Split each line on whitespace into at most three "
                "parts, uppercase the level, and print every line whose level is a warning or an "
                "error. Then print the total number of lines read and the number that matched. "
                "Observable output: one line per match plus two summary counts."
            ),
            "required_patterns": [".split(", ".upper()", "in ", "len(", "print("],
        },
        "algo-trading": {
            "framing": (
                "Instrument identifiers arrive in inconsistent forms: lowercase, with spaces, "
                "with an exchange suffix. Normalising them is the only way to join two feeds "
                "on the same instrument."
            ),
            "application": (
                "Walk the example as two symbol lists being reconciled. Each raw symbol is "
                "stripped, uppercased and separated from any exchange suffix, and because "
                "those steps return new strings, the two feeds can be compared on their "
                "cleaned form while the raw originals stay for audit. The join works because "
                "the normalisation is deterministic: the same raw symbol always cleans to the "
                "same key, which is what makes a set intersection meaningful. When a "
                "strategy finds no common instruments between two feeds and the trader knows "
                "there should be one, the normalisation is the first suspect, because a "
                "suffix or a case difference is enough to keep two identical symbols apart."
            ),
            "example_hint": "normalise instrument symbols from two feeds and intersect the cleaned sets",
            "assessment_angle": "why the join happens on cleaned keys and what determinism contributes",
            "day": 3,
            "title": "Join Two Feeds on the Cleaned Symbol, Not the Raw One",
            "code": """feed_a = [" AAPL ", "msft", "GOOG.N", "tsla"]
feed_b = ["AAPL", "MSFT", "goog.n", "TSLA.US"]


def clean_symbol(raw):
    return raw.strip().upper().split(".")[0]


set_a = {clean_symbol(s) for s in feed_a}
set_b = {clean_symbol(s) for s in feed_b}

print("common:", sorted(set_a & set_b))
print("only in A:", sorted(set_a - set_b))
print("only in B:", sorted(set_b - set_a))
print("raw A untouched:", feed_a)
""",
            "questions": [
                "Why is the intersection computed on the cleaned sets rather than on the two raw lists?",
                "What does split('.')[0] contribute, and why does it not modify the original symbol?",
                "The same raw symbol is cleaned twice, once per feed. Why is it safe to assume both results match?",
            ],
            "answers": [
                "Because the raw symbols differ in case, padding and suffix, so only the cleaned keys expose the instruments the two feeds actually share.",
                "It discards the exchange suffix by taking the part before the dot, and it returns a new string, leaving the original symbol intact.",
                "Because normalisation is deterministic, so identical raw input always yields the same cleaned key in both feeds.",
            ],
            "homework": (
                "Write reconcile_feeds.py with two lists of at least seven instrument identifiers each, "
                "differing in case, surrounding spaces and exchange suffixes. Write a clean_symbol "
                "function that strips, uppercases and drops the suffix, then print the instruments "
                "common to both feeds, those only in the first feed, those only in the second, and "
                "one raw symbol to prove the inputs are unmodified. Observable output: four lines."
            ),
            "required_patterns": [".strip(", ".upper()", ".split(", "&", "print("],
        },
        "numerical-methods": {
            "framing": (
                "Numerical data often arrives as text that has to be parsed into numbers, and "
                "the parse is string work that precedes every computation."
            ),
            "application": (
                "Walk the example as a column of measurements being read from text. Each raw "
                "value is stripped of padding and its thousands separator removed, then "
                "converted to a float, and the conversion is the boundary between string "
                "code and numeric code. Before it, every operation returns a new string; "
                "after it, every operation returns a number, and mixing the two is what "
                "produces a confusing TypeError. The reason the cleaning must precede the "
                "conversion is that a comma or a space makes the float call fail, so the "
                "string has to be fully normalised first. Printing both the raw text and the "
                "parsed number side by side is how you verify the parse, and it is worth "
                "doing because a silent misparse, say reading a label as a value, is much "
                "harder to find than a crash."
            ),
            "example_hint": "strip and un-separator numeric text, then convert and compute",
            "assessment_angle": "where string work ends and numeric work begins, and why order matters",
            "day": 3,
            "title": "Parse Before You Compute: Text In, Numbers Out",
            "code": """raw_values = [" 1,024.5 ", "3,200", " 512.75 ", "2,048.0"]


def parse_number(text):
    cleaned = text.strip().replace(",", "")
    return float(cleaned)


values = [parse_number(raw) for raw in raw_values]
print("parsed:", values)
print("total:", sum(values))
print("mean:", sum(values) / len(values))
print("raw text:", raw_values[0])
""",
            "questions": [
                "Why must the strip and replace happen before the float conversion?",
                "After parse_number returns, the code uses sum and division. What changed about the values that makes that possible?",
                "The first raw value still prints with its comma and spaces. Why?",
            ],
            "answers": [
                "Because float cannot parse a string containing a comma or surrounding spaces, so the text has to be cleaned into a bare numeric string first.",
                "They are now floats rather than strings, so arithmetic is defined, whereas arithmetic on the raw text would have been a type error.",
                "Because replace and strip returned a new string used only for the conversion, and never wrote into the original raw value.",
            ],
            "homework": (
                "Write parse_measurements.py with a list of at least eight numeric strings in text "
                "form, some containing commas as thousands separators and some with surrounding "
                "spaces. Write a parse_number function that cleans the text then converts it, and "
                "print the parsed list, the total, the mean to four decimals, and the repr of one "
                "raw string to show it is unmodified. Observable output: five lines."
            ),
            "required_patterns": [".strip()", ".replace(", "float(", "sum(", "print("],
        },
    },
)
