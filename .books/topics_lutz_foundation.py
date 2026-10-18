"""Canonical topic batch: Lutz chapters 4-7, the shared Python foundation.

Dependency order within this batch is the day number each adapter uses, so a
path that takes every topic gets a contiguous run of days with no gaps.

Topics here are corpus-grounded in:
  * ch 4  Introducing Python Object Types   (pp. 75-104)
  * ch 5  Numeric Types                     (pp. 105-142)
  * ch 7  Strings                           (pp. 155-196)

Every section named in provenance below was verified present in the extracted
source text before it was recorded.
"""
from canonical_topics import topic

DAY = {
    "object-type-categories": 1,
    "numbers-and-precision": 2,
    "string-as-immutable-sequence": 3,
    "string-formatting-output": 4,
    "numeric-accuracy-money": 8,
}

# Paths this foundation batch serves.
PATHS = (
    "machine-learning",
    "data-viz",
    "api-building",
    "web-scraping",
    "testing-qa",
    "devops-scripting",
    "algo-trading",
    "numerical-methods",
)

PATHS_NEEDING_EXACT_ARITHMETIC = (
    "machine-learning",
    "testing-qa",
    "algo-trading",
    "numerical-methods",
)

LUTZ_CH4 = {
    "book": "learning-python",
    "chapter": 4,
    "pages": [75, 104],
    "sections": ["Sequence Operations", "Type-Specific Methods", "Nesting Revisited", "Other Core Types"],
}
LUTZ_CH5 = {
    "book": "learning-python",
    "chapter": 5,
    "pages": [105, 142],
    "sections": ["Numeric Type Basics", "Numbers in Action", "Floor versus truncation", "Other Built-in Numeric Tools"],
}
LUTZ_CH5_PRECISION = {
    "book": "learning-python",
    "chapter": 5,
    "pages": [105, 142],
    "sections": ["Decimal Type", "Fraction Type", "Numeric accuracy"],
}
LUTZ_CH7 = {
    "book": "learning-python",
    "chapter": 7,
    "pages": [155, 196],
    "sections": ["Strings in Action", "Indexing and Slicing", "String Methods"],
}
LUTZ_CH7_FORMAT = {
    "book": "learning-python",
    "chapter": 7,
    "pages": [155, 196],
    "sections": ["String Formatting Method Calls", "String Conversion Tools"],
}


topic(
    "canonical:object-type-categories",
    "Object types come in families that share operations, and they nest freely",
    sources=[dict(LUTZ_CH4)],
    concept=(
        "Python keeps a small set of built-in object types, and the useful way to learn "
        "them is by family rather than by method list. A family shares operations: every "
        "sequence, whether a string, a list or a tuple, answers to indexing, slicing, "
        "concatenation with plus, repetition with star, and iteration; every mapping "
        "answers to key lookup and membership instead of position. When you know which "
        "family an object belongs to, you already know most of what you can legally do "
        "with it, and the type-specific methods are a smaller layer on top. Objects also "
        "nest without restriction. A list can hold mappings and a mapping can hold lists, "
        "and real records are usually built exactly that way: an outer collection of inner "
        "records, each one holding a row, a sample or a host. The name you assign to an "
        "object carries no type constraint, so the object itself decides which operations "
        "are legal. Reading a value's family before guessing its methods is the habit this "
        "topic trains, and it transfers to every library built on these types."
    ),
    prerequisites=[],
    pitfalls=[
        "Calling a mapping method on a sequence, or a sequence operation on a mapping, "
        "because the object's family was never checked first.",
        "Assuming a collection is a list when it is a mapping, so positional indexing "
        "raises a lookup error instead of returning the intended value.",
        "Hand-flattening data that could have stayed structured, because nesting was not "
        "recognised as allowed.",
    ],
    adapters={
        "machine-learning": {
            "framing": (
                "A dataset is a sequence of records, and each record is a mapping from "
                "column name to value. Before any model code, you have to read that "
                "structure correctly, because the family decides what you can do to it."
            ),
            "application": (
                "Walk the example as a reader of someone else's dataset. len(samples) is a "
                "sequence operation, so it counts records, not features. samples[0] is "
                "indexing into the sequence, so it yields the first record. That record is "
                "a mapping, so reaching a value needs its key, samples[0]['label'], and a "
                "second positional index would be meaningless. Slicing, samples[-2:], is a "
                "family operation again, so it works on the dataset and gives the last two "
                "records. Notice that no single idea here is specific to machine learning: "
                "the whole skill is looking at a nested structure and naming each level's "
                "family before reaching for an operation, and every later topic in this "
                "track assumes you can do that without thinking."
            ),
            "example_hint": "build a dataset as a sequence of mappings, then count, index, slice and look up",
            "assessment_angle": "which operations are legal at each nesting level and why",
            "day": DAY["object-type-categories"],
            "title": "Read the Structure First: Sequences of Records in a Dataset",
            "code": """samples = [
    {"label": "spam", "length": 41, "punct": 2},
    {"label": "ham", "length": 12, "punct": 0},
    {"label": "spam", "length": 63, "punct": 4},
    {"label": "ham", "length": 9, "punct": 1},
]

print("records:", len(samples))            # sequence operation
first = samples[0]                         # indexing the sequence
print("first record:", first)
print("first label:", first["label"])      # lookup inside a mapping
print("last two:", samples[-2:])           # slicing the sequence
""",
            "questions": [
                "Why does len(samples) count records, while reaching a value inside one record needs a column name?",
                "What does samples[-2:] return, and why is that available on this dataset at all?",
                "A teammate runs samples[0] = 99. Why does that not change the label of the first record?",
            ],
            "answers": [
                "The dataset is a sequence, so len counts its items, the records; each record is a mapping, so its values are reached by key rather than by position.",
                "The last two records, because negative offsets count from the end and slicing is a family operation every sequence supports.",
                "It replaces the whole record at position 0 with the integer 99, so the mapping that held the label is discarded rather than updated.",
            ],
            "homework": (
                "Write dataset_families.py that builds a list of at least four record dicts, each "
                "with a name key and two numeric keys of your choosing. Print the record count with "
                "len, the first record's name by indexing then key lookup, the last two records by "
                "slicing, and one field read from the third record. Then add a fifth record that "
                "itself stores a list under one key, and print the length of that inner list, to "
                "show nesting works. Observable output: five lines showing count, name, the last "
                "two records, the third record's field, and the inner list length."
            ),
            "required_patterns": ["len(", "[-2:]", "[0]", "dict", "print("],
        },
        "data-viz": {
            "framing": (
                "A chart is described with nested collections: one mapping for the figure, "
                "each series a sequence of numbers. Confusing the two families is the usual "
                "reason an early plotting snippet fails with a confusing error."
            ),
            "application": (
                "Walk the example as a chart description being assembled. config is a "
                "mapping, so its entries are reached by key: config['title'] works and "
                "config[0] does not. prices is a sequence, so it answers to len, to "
                "indexing and to slicing, and slicing a series is how you plot a window of "
                "it. The nesting is what makes the structure usable: the series lives "
                "inside the mapping under 'series', so reaching it is lookup first, then "
                "sequence operations. When a plot call later complains about a value, the "
                "first question to ask is which family the value belonged to, because "
                "passing a mapping where a sequence was expected is the mistake this "
                "structure makes easy to spot."
            ),
            "example_hint": "store a figure config as a mapping wrapping a numeric series, then read both levels",
            "assessment_angle": "which of len, indexing, slicing and key lookup apply at each level",
            "day": DAY["object-type-categories"],
            "title": "A Figure Is a Mapping of Series: Read Both Levels Correctly",
            "code": """config = {
    "title": "Daily closing price",
    "series": [41.2, 42.0, 41.8, 43.1, 44.6],
    "unit": "USD",
}

print("title:", config["title"])              # lookup in a mapping
prices = config["series"]                     # reach the inner sequence
print("points:", len(prices))                 # sequence operation
print("first and last:", prices[0], prices[-1])
print("window:", prices[1:4])                 # slicing the sequence
""",
            "questions": [
                "Why is config['title'] valid while config[0] raises an error?",
                "What two operations are needed to print the last three values of the series, and in what order?",
                "A series is moved out of the mapping into its own variable. Which of its behaviours change, and which stay the same?",
            ],
            "answers": [
                "config is a mapping, so its entries are reached by key; 0 is not a key in it, so the lookup fails.",
                "Key lookup on the mapping to get the series, then slicing on that sequence, so config['series'][-3:].",
                "None of its behaviours change, because slicing and len belong to the series itself, not to the mapping that held it.",
            ],
            "homework": (
                "Write figure_structure.py that builds one mapping holding a title string, a unit "
                "string and two named series, each a list of at least five numbers. Print the title "
                "and unit by key lookup, the length of each series, the first and last value of the "
                "first series, and a three-value slice of the second series. Then add a nested "
                "mapping under the key 'axes' with two keys of your own and print one of them. "
                "Observable output: seven lines in total, each produced by naming the family of the "
                "value you read."
            ),
            "required_patterns": ["len(", "[-3:]", "[0]", "[-1]", "print("],
        },
        "api-building": {
            "framing": (
                "An incoming request arrives as a mapping, and the collection you send back "
                "is a sequence. The boundary between the two is exactly where their "
                "operations differ, and code that crosses it has to switch families."
            ),
            "application": (
                "Walk the example as a request handler. request is a mapping, so the query "
                "arguments are reached by key, and the value stored there is a sequence, so "
                "it is counted and indexed rather than looked up. Building the response "
                "goes the other way: you assemble a sequence of record mappings, then "
                "slice it to honour a page size. Notice that pagination is a family "
                "operation applied to a sequence, while selecting one argument by name is a "
                "mapping operation, and the two never substitute for each other. When a "
                "handler misbehaves, printing the value and naming its family usually "
                "localises the bug faster than reading the traceback, because the traceback "
                "names the operation that failed, not the value that was wrong."
            ),
            "example_hint": "read a request mapping containing a sequence of arguments, build a paginated response",
            "assessment_angle": "when to use key lookup and when to use positional indexing or slicing",
            "day": DAY["object-type-categories"],
            "title": "Requests Are Mappings, Responses Are Sequences: Cross the Boundary",
            "code": """request = {"path": "/items", "args": ["new", "blue", "large"], "limit": 2}

args = request["args"]                    # lookup in the request mapping
print("arg count:", len(args))            # sequence operation
print("first arg:", args[0])

items = [
    {"id": 1, "name": "Mug"},
    {"id": 2, "name": "Kettle"},
    {"id": 3, "name": "Bowl"},
]
page = items[: request["limit"]]          # slice a sequence by a value from the mapping
print("page:", page)
""",
            "questions": [
                "Why is request['args'] followed by args[0] rather than request['args'][0] written as one step differently?",
                "What does items[: request['limit']] show about mixing the two families?",
                "The limit is removed from the request mapping and passed as a separate variable. What changes about the slicing expression?",
            ],
            "answers": [
                "The first step is key lookup on the mapping, which yields the sequence; the second is positional indexing on that sequence, so the two operations target different families.",
                "It shows that a value read from a mapping can be used as an operand for a sequence operation, without either value changing family.",
                "Only where the number comes from; the slice itself is still a sequence operation, so items[:limit] behaves identically.",
            ],
            "homework": (
                "Write request_families.py with a request mapping holding a path string, a sequence "
                "of at least four filter strings, and a page size. Build a list of at least six "
                "record mappings. Print the path and the filter count, the first and last filters by "
                "indexing, and one page of records sliced by the page size. Then print a single "
                "field of the first record on the page, using both a positional index and a key "
                "lookup in the same expression. Observable output: six lines showing each family "
                "operation applied at the right level."
            ),
            "required_patterns": ["len(", "[:", "[0]", "[-1]", "print("],
        },
        "web-scraping": {
            "framing": (
                "A scraped page yields one long sequence of raw strings. You group those "
                "into a sequence of mappings so every row can be reached by column name "
                "instead of by position you have to remember."
            ),
            "application": (
                "Walk the example as a parser that has just pulled text off a page. raw is "
                "a sequence of strings, so iterating it and slicing it are the natural "
                "operations. After the split, each row becomes a mapping, so the fields are "
                "read by name, which is what makes the parsed data safe to extend: adding a "
                "column changes no positional index anywhere downstream. Compare with "
                "keeping rows as lists, where a new column inserted in the middle silently "
                "shifts every later index. The transformation is the point of the parse, "
                "and it is a change of family, from a sequence of strings to a sequence of "
                "mappings, which is why the code reads differently before and after it."
            ),
            "example_hint": "turn a sequence of raw strings into a sequence of mappings, then read fields by name",
            "assessment_angle": "why the parse is a change of family and what that buys downstream",
            "day": DAY["object-type-categories"],
            "title": "Raw Strings to Named Rows: Change the Family in the Parse",
            "code": """raw = ["Mug,2.50", "Kettle,12.00", "Bowl,4.25"]

rows = []                                  # will become a sequence of mappings
for line in raw:                           # iterating a sequence
    name, price = line.split(",")          # splitting a string yields a sequence
    rows.append({"name": name, "price": float(price)})

print("rows parsed:", len(rows))
first = rows[0]                            # indexing the sequence of mappings
print("first name:", first["name"])        # lookup inside a mapping
print("every price:", [row["price"] for row in rows])
""",
            "questions": [
                "Before the parse, how do you reach the second item of the page, and after it, how do you reach the second field of the first row?",
                "Why does adding a column to the mapping version break no downstream positional index?",
                "line.split(',') returns a sequence. Why is that not enough on its own to finish the parse?",
            ],
            "answers": [
                "Before, by indexing the sequence of strings, raw[1]; after, by key lookup inside the first mapping, rows[0]['price'], because the row is a mapping.",
                "Because fields in a mapping are reached by name, and a new key does not renumber the existing ones, unlike a positional list.",
                "Because it yields a bare sequence of two strings, so the code still has to pair each position with a field name to make the row readable.",
            ],
            "homework": (
                "Write parse_to_named_rows.py that starts with a list of at least five raw strings in "
                "'name,quantity,price' form. Parse each into a mapping with those three keys, "
                "converting quantity to int and price to float. Print the number of rows parsed, the "
                "name and price of the first row by key lookup, the whole last row by slicing, and "
                "the total quantity summed by reading the quantity key from every row. Observable "
                "output: five lines, with every field reached by name rather than by position."
            ),
            "required_patterns": ["split(", "float(", "int(", "for ", "print("],
        },
        "testing-qa": {
            "framing": (
                "A test case is a mapping of inputs and expectation, and a suite is a "
                "sequence of cases. Runners rely on exactly that distinction, and so does "
                "anyone reading a failure report."
            ),
            "application": (
                "Walk the example as a tiny test runner. cases is a sequence, so iterating "
                "it and indexing it are the legal operations; each case is a mapping, so "
                "its inputs and expected value are read by name. That separation is what "
                "lets the runner stay generic: the loop reads the same keys from every "
                "case, and a new case adds a sequence entry rather than changing the "
                "runner. When a case fails, the report prints case['name'], a lookup, and "
                "the count of failures is a len over a sequence. The habit worth building "
                "is to name the family of a value before you operate on it, because a test "
                "runner that assumed cases were lists would break the moment one case "
                "gained a field."
            ),
            "example_hint": "iterate a sequence of test-case mappings and read every field by name",
            "assessment_angle": "which operations the runner applies to the suite and which to each case",
            "day": DAY["object-type-categories"],
            "title": "Cases Are Mappings, Suites Are Sequences: Run Them Separately",
            "code": """cases = [
    {"name": "empty input", "input": [], "expected": 0},
    {"name": "one item", "input": [7], "expected": 7},
    {"name": "three items", "input": [2, 9, 4], "expected": 15},
]

failures = []
for case in cases:                                  # iterating a sequence
    total = sum(case["input"])                       # lookup inside a mapping
    if total != case["expected"]:
        failures.append(case["name"])

print("cases run:", len(cases))
print("first case name:", cases[0]["name"])
print("failures:", failures)
""",
            "questions": [
                "Why does the loop read case['expected'] instead of case[2]?",
                "What does len(cases) count, and what does sum(case['input']) count?",
                "A fourth case is added without an 'expected' key. Where does the error surface, and why?",
            ],
            "answers": [
                "Because each case is a mapping, so its fields are reached by name; position 2 has no defined meaning in a mapping.",
                "len(cases) counts the test cases in the suite; sum(case['input']) adds the values inside one case's input list.",
                "At the key lookup inside the loop, because the missing key is read the moment the runner tries to compare its expectation.",
            ],
            "homework": (
                "Write suite_families.py with a list of at least five test-case mappings, each holding "
                "a name, an input list of numbers, and an expected total. Iterate the suite, sum each "
                "input, and collect the name of every case whose total differs from its expectation. "
                "Print the number of cases run, the name of the first case by indexing and key "
                "lookup, and the list of failing names. Include one deliberately failing case so the "
                "failure list is non-empty. Observable output: three lines proving the runner treats "
                "the suite as a sequence and each case as a mapping."
            ),
            "required_patterns": ["sum(", "len(", "for ", "if ", "print("],
        },
        "devops-scripting": {
            "framing": (
                "An inventory file becomes a sequence of host mappings. Which operations "
                "are legal on the whole file, and which on one host, is decided by family, "
                "and scripting over inventories is mostly that distinction."
            ),
            "application": (
                "Walk the example as a script that loads an inventory. hosts is a "
                "sequence, so iterating, counting and slicing it are the operations that "
                "apply; each host is a mapping, so its role and address are read by name. "
                "Filtering is a mix: the loop iterates the sequence and the condition "
                "looks up a key in each mapping. That mix is the whole pattern of "
                "configuration scripting, and it is why a playbook that treats hosts as "
                "lists breaks when an inventory gains a field. When a run reports the "
                "wrong host count, check first whether the code counted the sequence or "
                "summed something inside a mapping, because those two mistakes look "
                "identical in the output."
            ),
            "example_hint": "load a sequence of host mappings, count, slice and filter by key lookup",
            "assessment_angle": "which operation belongs to the inventory and which to one host",
            "day": DAY["object-type-categories"],
            "title": "Inventories Are Sequences of Host Mappings: Filter by Key",
            "code": """hosts = [
    {"name": "web-1", "role": "web", "env": "prod"},
    {"name": "web-2", "role": "web", "env": "prod"},
    {"name": "db-1", "role": "db", "env": "prod"},
    {"name": "stage-1", "role": "web", "env": "stage"},
]

print("hosts:", len(hosts))                           # sequence operation
print("first two:", [h["name"] for h in hosts[:2]])    # slice then lookup

prod_web = []
for host in hosts:                                    # iterating a sequence
    if host["role"] == "web" and host["env"] == "prod":   # lookups in a mapping
        prod_web.append(host["name"])
print("prod web:", prod_web)
""",
            "questions": [
                "Why is hosts[:2] followed by h['name'] rather than by h[0]?",
                "What does len(hosts) count, and why is that not the number of production web hosts?",
                "The inventory gains a 'region' key on every host. Which parts of the script need changing, and which cannot be affected?",
            ],
            "answers": [
                "hosts[:2] is a slice of the sequence, so it yields mappings; a mapping is read by key, so the name comes from h['name'] and h[0] is meaningless.",
                "It counts every host in the inventory, because len counts the sequence's items; the production web hosts are a filtered subset computed by the loop.",
                "Only the filter condition can change, if region becomes part of it; counting, slicing and iteration are family operations and are unaffected by a new key.",
            ],
            "homework": (
                "Write inventory_families.py that builds an inventory of at least six host mappings with "
                "name, role, environment and address keys. Print the host count, the names of the first "
                "three hosts by slicing, and a filtered list of names for hosts whose role is one "
                "specific value and whose environment is another. Then print the address of one chosen "
                "host by looking it up in its mapping. Observable output: four lines, each showing a "
                "sequence operation applied to the inventory or a key lookup applied to one host."
            ),
            "required_patterns": ["len(", "[:3]", "for ", "if ", "print("],
        },
        "algo-trading": {
            "framing": (
                "A market data feed is a sequence of ticks, and each tick is a mapping of "
                "field names to values. You slice the sequence to get a window and look up "
                "fields inside each tick, and the two never substitute."
            ),
            "application": (
                "Walk the example as a strategy reading a feed. ticks is a sequence, so "
                "len reports how many arrived, slicing gives the most recent window, and "
                "negative offsets reach the end without knowing the count. Each tick is a "
                "mapping, so price and size are read by name, which is what lets a "
                "strategy stay valid when the feed adds a field such as an exchange "
                "identifier: named lookups do not renumber. Reading a moving window is "
                "therefore two operations from two families, slicing the sequence then "
                "key lookup inside each element, and writing them in that order is what "
                "keeps windowed indicators readable."
            ),
            "example_hint": "slice a tick sequence into a window and read named fields from each tick",
            "assessment_angle": "why a window is slicing and a field is lookup, never the reverse",
            "day": DAY["object-type-categories"],
            "title": "Windows Are Slices, Fields Are Lookups: Read a Tick Feed",
            "code": """ticks = [
    {"price": 101.0, "size": 20},
    {"price": 101.5, "size": 8},
    {"price": 102.0, "size": 30},
    {"price": 101.8, "size": 14},
    {"price": 102.4, "size": 22},
]

print("ticks:", len(ticks))
window = ticks[-3:]                                  # slicing the sequence
print("window prices:", [t["price"] for t in window])
last = window[-1]                                    # indexing within the slice
print("last price:", last["price"], "size:", last["size"])
""",
            "questions": [
                "Why is the recent window obtained with ticks[-3:] instead of by looking up a key?",
                "What does len(ticks) report, and why is it not the number of prices in the window?",
                "The feed starts carrying an exchange key on every tick. Why can the window code stay unchanged?",
            ],
            "answers": [
                "Because the recent ticks are the last items of a sequence, and taking the last items is slicing, an operation no mapping supports.",
                "It reports the number of ticks in the whole feed, since len counts the sequence; the window is a separate slice holding three of them.",
                "Because fields are read by name, and adding a key to a mapping does not renumber or displace the existing ones the way a list insertion would.",
            ],
            "homework": (
                "Write tick_families.py with a list of at least eight tick mappings, each holding "
                "price, size and symbol keys. Print the tick count, the prices of the most recent "
                "four ticks by slicing, and the symbol and size of the final tick by indexing and key "
                "lookup. Then compute and print the average price over the same four-tick window, "
                "reading each price by name. Observable output: five lines showing slicing on the "
                "sequence and key lookup inside each tick."
            ),
            "required_patterns": ["len(", "[-4:]", "[-1]", "for ", "print("],
        },
        "numerical-methods": {
            "framing": (
                "A vector is a sequence of numbers and a matrix is a sequence of vectors. "
                "Indexing picks a row, a second index picks an entry, and that behaviour "
                "comes from the family, not from any library."
            ),
            "application": (
                "Walk the example as grid arithmetic. matrix is a sequence whose items are "
                "themselves sequences, so matrix[1] is a whole row and matrix[1][2] is one "
                "entry of it, read left to right as row then column. Slicing, matrix[:2], "
                "yields the first two rows and is the same operation that works on any "
                "sequence, which is why it also works on a row to take a run of entries. "
                "That regularity is what makes hand-written solvers possible before any "
                "array library is introduced: every level answers to indexing, slicing and "
                "iteration, so the same loop shape walks rows and entries. The mistake to "
                "avoid is treating a row as a scalar, because it is still a sequence and "
                "reports its own length."
            ),
            "example_hint": "index a matrix by row then column, slice rows, and measure each row",
            "assessment_angle": "what each index level returns and which operations repeat at every level",
            "day": DAY["object-type-categories"],
            "title": "Matrices Are Sequences of Sequences: Index Row, Then Column",
            "code": """matrix = [
    [2.0, 0.0, 1.0],
    [0.0, 3.0, 0.0],
    [1.0, 0.0, 4.0],
]

print("rows:", len(matrix))                 # count of rows
row = matrix[1]                             # indexing the outer sequence
print("row 1:", row, "entries:", len(row))  # a row is itself a sequence
print("entry (1,2):", matrix[1][2])         # row index then column index
print("first two rows:", matrix[:2])        # slicing rows
""",
            "questions": [
                "Why does matrix[1][2] read as row 1, column 2 rather than the reverse?",
                "What does len(row) report, and why is that a meaningful question about a single row?",
                "matrix[:2] is applied to the matrix and row[:2] could be applied to one row. What do the two have in common?",
            ],
            "answers": [
                "Because the first index selects an item of the outer sequence, which is a whole row, and the second index then selects an item of that row.",
                "It reports the number of entries in the row, because a row is itself a sequence and supports the same counting operation.",
                "Both are slicing, an operation shared by every sequence, so the same syntax takes a run of rows or a run of entries.",
            ],
            "homework": (
                "Write matrix_families.py that builds a three-by-four matrix as a list of lists of "
                "floats. Print the number of rows, the number of entries in the second row, one entry "
                "chosen by row and column index, and the first two rows as a slice. Then compute and "
                "print the sum of one column of your choice, by indexing the same column position in "
                "every row. Observable output: five lines, each showing an indexing or slicing "
                "operation applied at the level the value belongs to."
            ),
            "required_patterns": ["len(", "[1][2]", "[:2]", "for ", "print("],
        },
    },
)
