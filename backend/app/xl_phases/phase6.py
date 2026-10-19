"""Scaling, testing and performance, days 150-164.

Every example is stdlib-only, offline and deterministic: rows stream from
in-memory lists, indexes and caches are plain dicts, and work is measured by
counting iterations or comparisons rather than by timing. That keeps the
printed output stable while still showing the shapes a real pipeline needs.
"""

PHASE = (
    "Scaling, Testing and Performance",
    "Make spreadsheet pipelines survive growing data by streaming, bounding memory, measuring work and testing every transform.",
    {
        150: dict(
            topic="Orientation: growing data",
            idea=(
                "Growing data changes the shape of a solution before it changes the code. A sheet that fits in a "
                "glance can be held in a list, searched with a loop and reprinted whenever you like; the same sheet "
                "with a hundred thousand rows punishes every one of those habits. The first step in scaling is "
                "therefore orientation, not optimisation: count how many rows arrive, how wide each row is, how "
                "often the pipeline runs and how fast it must finish. Multiplication does the rest, because cells, "
                "not rows, are what consume memory, and a modest row count with a wide layout can be larger than a "
                "big narrow one. This lesson sets up the rest of the phase by making growth explicit. You will build "
                "a small in-memory sheet, report its rows, width and cell count, and multiply those numbers to see "
                "what happens at two and four times the size. The printed total is the baseline every later "
                "optimisation has to improve on, not a guess. The important habit is to reason from measured "
                "counts instead of guessing, and to notice which parts of your current script would need every row at "
                "once. Those parts are the ones the next lessons replace."
            ),
            code=(
                'ROWS = 1000\n'
                'WIDTH = 6\n'
                '\n'
                'def dataset(rows, width):\n'
                '    return [["c%d" % column for column in range(width)] for _ in range(rows)]\n'
                '\n'
                'sheet = dataset(ROWS, WIDTH)\n'
                'cells = len(sheet) * len(sheet[0])\n'
                'print("rows", len(sheet), "width", len(sheet[0]), "cells", cells)\n'
                '\n'
                'for factor in (1, 2, 4):\n'
                '    rows = ROWS * factor\n'
                '    print(f"scale x{factor}: {rows} rows, {rows * WIDTH} cells")\n'
                '\n'
                'assert cells == 6000\n'
                'assert len(sheet) * 4 * WIDTH == 24000\n'
                'print("growth is rows x width, not just rows")'
            ),
            variant_b="double the row count and halve the width, then compare the cell totals",
            variant_c="add a fourth scale factor of eight and print how many cells the sheet would hold",
            mistakes=[
                "Reasoning about rows only, so a wide sheet is underestimated.",
                "Guessing where the pipeline slows down instead of counting rows and columns.",
                "Assuming the sample size is representative of the production export.",
            ],
            q1=(
                "Why is cell count a better size estimate than row count?",
                "Memory and copying grow with rows times width, so a wide sheet costs more than its row count suggests.",
            ),
            homework=(
                "Write `scale_report(rows, width)` that returns a dict with row count, cell count and the cell "
                "count at four times the size, then prints each value. Run it for a sheet of three rows and six "
                "columns, and comment which line shows why width multiplies the cost."
            ),
            patterns=["def ", "print(", "cells"],
            mapping=(
                "pandas users see this as `shape` and chunk sizing; measuring rows, columns and cells first tells "
                "you whether `read_csv(chunksize=...)` is even necessary."
            ),
        ),
        151: dict(
            topic="Streaming rows instead of loading all",
            idea=(
                "Streaming is the habit of handling one row at a time instead of collecting every row first. In "
                "Python the natural tool is a generator: a function containing yield that produces values on demand "
                "and keeps only its current position. When you pass that generator into a loop, memory stays "
                "roughly constant no matter how long the input is, because the producer and the consumer take "
                "turns. That property is what makes streaming worth the extra indirection. It also brings "
                "constraints. A stream can be consumed once, so sorting it, scanning it twice or storing it in a "
                "list quietly undoes the benefit. You must decide the output before you start: a total, a count, a "
                "filtered stream or a small summary can all be produced in one pass, while an operation that needs "
                "the whole set cannot. Today you write a generator over an in-memory list, feed it to a function "
                "that tallies quantities, and print how many rows were consumed. The data is tiny, but the shape is "
                "the one you would use for a million rows, and the row count proves that the consumer never needed "
                "the rest of the list. A generator is a contract about consumption: whoever receives it must finish the pass or explicitly stop."
            ),
            code=(
                'SHEET = [\n'
                '    ["item", "qty"],\n'
                '    ["widget", "3"],\n'
                '    ["gizmo", "5"],\n'
                '    ["cable", "2"],\n'
                ']\n'
                '\n'
                'def stream_rows(rows):\n'
                '    for row in rows:\n'
                '        yield row\n'
                '\n'
                'def total_qty(rows):\n'
                '    total = 0\n'
                '    seen = 0\n'
                '    for row in rows:\n'
                '        total += int(row[1])\n'
                '        seen += 1\n'
                '    return total, seen\n'
                '\n'
                'total, seen = total_qty(stream_rows(SHEET[1:]))\n'
                'print("rows consumed", seen)\n'
                'print("total qty", total)\n'
                'assert seen == 3 and total == 10\n'
                'print("one row in memory at a time")'
            ),
            variant_b="filter the generator so only rows with qty above 2 reach the consumer",
            variant_c="chain two generators, one to skip the header and one to parse quantities, then total them",
            mistakes=[
                "Converting the generator back to a list, which loads every row again.",
                "Trying to iterate the same stream twice and silently getting nothing on the second pass.",
                "Sorting the whole stream before the one-pass total, defeating the memory saving.",
            ],
            q1=(
                "What does a generator save compared with returning a list of rows?",
                "It keeps only the current row and position instead of every row, so memory stays roughly constant as input grows.",
            ),
            homework=(
                "Write `consume_stream(rows)` that turns a list of rows into a generator, sums a numeric column, "
                "and returns both the total and the number of rows consumed. Run it on five rows, print both "
                "values, and comment which line proves the input was never copied into a new list."
            ),
            patterns=["def ", "yield", "print("],
            mapping=(
                "pandas exposes the same idea through `chunksize` iterators; the generator discipline here is what "
                "lets a pipeline consume a large export without materialising it."
            ),
        ),
        152: dict(
            topic="Bounded memory patterns",
            idea=(
                "Bounded memory means deciding in advance what you are willing to forget. Many spreadsheet tasks "
                "look like they need the full table but actually need a summary: a running total, a count, a "
                "minimum, the last few rows, the largest few values. Each of those can be maintained in a fixed "
                "amount of space while rows pass by. The technique is to keep only the state the answer requires "
                "and to replace it as new rows arrive. A running total needs one number, a maximum needs one "
                "value, and a short recent window needs a fixed-length buffer. The danger is accidental retention: "
                "appending to a list because it is convenient, keeping every intermediate record for debugging, or "
                "building a lookup you never query. Those choices turn a constant-memory job into a copy of the "
                "input. The discipline is to name your state, state its size, and check that the loop only touches "
                "that state. Today you compute a total and keep the last two names using a fixed-length buffer, "
                "then print both. Notice that the answer is identical to the one a full list would give, while the "
                "memory ceiling is independent of how many rows the sheet contains. If the answer needs every row after all, admit it and choose a different pattern."
            ),
            code=(
                'from collections import deque\n'
                '\n'
                'ROWS = [("a", 5), ("b", 9), ("c", 2), ("d", 7), ("e", 4)]\n'
                'RECENT = deque(maxlen=2)\n'
                'total = 0\n'
                'largest = None\n'
                '\n'
                'for name, value in ROWS:\n'
                '    total += value\n'
                '    RECENT.append(name)\n'
                '    largest = value if largest is None else max(largest, value)\n'
                '\n'
                'print("rows", len(ROWS))\n'
                'print("total", total)\n'
                'print("largest", largest)\n'
                'print("recent", list(RECENT))\n'
                '\n'
                'assert total == 27 and largest == 9\n'
                'assert list(RECENT) == ["d", "e"]\n'
                'print("bounded state kept last 2, not all 5")'
            ),
            variant_b="also track a running minimum and print all four summary values",
            variant_c="keep the three largest values in a bounded list instead of only the single maximum",
            mistakes=[
                "Appending every row to a debug list, so memory grows with the input anyway.",
                "Using an unbounded deque by forgetting maxlen, which defeats the whole pattern.",
                "Sharing one mutable buffer between two summaries that need different windows.",
            ],
            q1=(
                "How do you know a pipeline can use bounded memory?",
                "When its output is a fixed-size summary such as a total, count or short window, it never needs the full table at once.",
            ),
            homework=(
                "Write `bounded_summary(rows, window)` that returns the total, the maximum and a list holding only "
                "the last `window` values. Run it on six values with window 2, print the result, and comment which "
                "line shows the memory does not grow with the input."
            ),
            patterns=["def ", "return", "print("],
            mapping=(
                "This is the mental model behind pandas `chunksize` plus a running aggregate: keep the summary, "
                "discard the chunk, and never concatenate the whole export."
            ),
        ),
        153: dict(
            topic="Processing in chunks",
            idea=(
                "Chunking is the middle ground between one row at a time and the whole sheet at once. You take a "
                "batch of rows, do some work on that batch, merge the result into a running summary, and move on. "
                "Batches make several practical things easier: a progress line per batch, a retry boundary when "
                "one batch fails, and a natural place to checkpoint partial results. They also make aggregation "
                "slightly more careful, because a group can appear in several chunks and the merge step must add "
                "rather than replace. The usual bug is treating the final partial chunk as if it were full, or "
                "assuming a chunk boundary aligns with a group boundary. Neither assumption is safe. A robust "
                "chunk loop only depends on the list of rows and a positive size, and it handles a last chunk that "
                "is shorter than the rest. Today you split seven records into chunks of three, aggregate each "
                "chunk locally, then merge the local totals into a global one. The printed chunk count and totals "
                "show that no row was lost at a boundary and that the short final chunk was processed like any "
                "other. Choosing the batch size is a trade-off between overhead per chunk and memory per chunk, not a magic constant."
            ),
            code=(
                'ROWS = [\n'
                '    ("north", "5"), ("south", "7"), ("north", "4"),\n'
                '    ("east", "6"), ("south", "3"), ("north", "1"), ("west", "8"),\n'
                ']\n'
                '\n'
                'def chunks(items, size):\n'
                '    for start in range(0, len(items), size):\n'
                '        yield items[start:start + size]\n'
                '\n'
                'totals = {}\n'
                'chunk_count = 0\n'
                'for chunk in chunks(ROWS, 3):\n'
                '    chunk_count += 1\n'
                '    local = {}\n'
                '    for region, value in chunk:\n'
                '        local[region] = local.get(region, 0) + int(value)\n'
                '    for region in sorted(local):\n'
                '        totals[region] = totals.get(region, 0) + local[region]\n'
                '\n'
                'print("chunks", chunk_count)\n'
                'for region in sorted(totals):\n'
                '    print(region, totals[region])\n'
                'assert chunk_count == 3\n'
                'assert totals == {"east": 6, "north": 10, "south": 10, "west": 8}\n'
                'print("partial final chunk merged cleanly")'
            ),
            variant_b="use a chunk size of two and check that the group totals are unchanged",
            variant_c="print the row count of each chunk to see the short final batch explicitly",
            mistakes=[
                "Replacing group totals per chunk instead of adding them, so later chunks overwrite earlier ones.",
                "Assuming every chunk has the requested size and indexing past the end of the last one.",
                "Sharing one local accumulator across chunks and forgetting to reset it.",
            ],
            q1=(
                "Why must chunk totals be merged by addition rather than assignment?",
                "A group can appear in several chunks, so assignment would keep only the last chunk's partial total.",
            ),
            homework=(
                "Write `chunk_totals(rows, size)` that yields chunks, sums each chunk, and returns the merged "
                "totals plus the number of chunks. Run it on seven rows with size 3, print the totals, and comment "
                "which line keeps the short final chunk from being dropped."
            ),
            patterns=["def ", "yield", "print("],
            mapping=(
                "This is exactly what pandas `chunksize` gives you: independent frames that must be reduced and "
                "combined, with the last frame allowed to be short."
            ),
        ),
        154: dict(
            topic="Indexing for fast lookups",
            idea=(
                "An index is a dictionary built once so that later lookups do not scan. Without one, finding a "
                "record means comparing the key against each row in turn: fine for ten rows, expensive when every "
                "row does it. With one, the same lookup is a hash of the key and a single dictionary access, so the "
                "cost stops growing with the table. The price is paid up front in one pass and in the memory the "
                "dictionary occupies. Two decisions matter. First, keys must be unique or you must define which "
                "duplicate wins; silently overwriting one record is how an index becomes a data-loss bug. Second, "
                "the index must be rebuilt when the underlying rows change, or it will keep answering with stale "
                "values. Missing keys also need a policy: returning None is honest if callers check it, while a "
                "default can hide a typo. Today you build an index of records by id and compare one scan against "
                "one indexed lookup, counting comparisons rather than timing them. The counts are stable on any "
                "machine, which is the point: the index changes the amount of work, not the speed of the computer, "
                "and the measured difference is what justifies keeping it."
            ),
            code=(
                'RECORDS = [{"id": "K%d" % i, "value": i * 10} for i in range(1, 7)]\n'
                '\n'
                'def linear_lookup(records, key):\n'
                '    comparisons = 0\n'
                '    for record in records:\n'
                '        comparisons += 1\n'
                '        if record["id"] == key:\n'
                '            return record["value"], comparisons\n'
                '    return None, comparisons\n'
                '\n'
                'INDEX = {record["id"]: record for record in RECORDS}\n'
                '\n'
                'def indexed_lookup(table, key):\n'
                '    record = table.get(key)\n'
                '    return (record["value"] if record else None), 1\n'
                '\n'
                'target = "K5"\n'
                'linear_value, linear_steps = linear_lookup(RECORDS, target)\n'
                'fast_value, fast_steps = indexed_lookup(INDEX, target)\n'
                'print("linear", linear_value, "steps", linear_steps)\n'
                'print("indexed", fast_value, "steps", fast_steps)\n'
                'assert linear_value == fast_value == 50\n'
                'assert linear_steps == 5 and fast_steps == 1\n'
                'print("build the index once, then look up")'
            ),
            variant_b="index the records by value and look up a value that appears twice to see the overwrite",
            variant_c="use a tuple of region and month as a composite key and look up one combination",
            mistakes=[
                "Rebuilding the index inside the loop, turning a one-time cost into a quadratic one.",
                "Assuming keys are unique without checking, so one record silently replaces another.",
                "Keeping an index after editing the rows, so lookups return stale data.",
            ],
            q1=(
                "What is the trade-off of building an index before a batch of lookups?",
                "You pay one pass and extra memory up front, but every later lookup becomes a single dictionary access instead of a scan.",
            ),
            homework=(
                "Write `build_index(records, key)` that returns a dict keyed by one field, and `lookup(index, key)` "
                "that returns the record or None. Build it for four records, look up one present and one missing "
                "key, print both results, and comment which line makes duplicate keys visible."
            ),
            patterns=["def ", "return", "print("],
            mapping=(
                "pandas `set_index` and `merge` use the same trade-off; understanding the one-time build and the "
                "staleness rule keeps joins predictable."
            ),
        ),
        155: dict(
            topic="Caching aggregations",
            idea=(
                "Caching is reusing an answer you already computed instead of computing it again. For report work "
                "the unit is usually an aggregate: the total for a region, the count for a month, the lookup for "
                "an id. A dictionary keyed by the inputs is enough. The rule that keeps a cache correct is simple "
                "and unforgiving: the key must capture every input that can change the answer. If the aggregation "
                "depends on the rows, the rows are part of the key, or the cache must be cleared whenever they "
                "change. Caches also hide work, so instrument them with hits and misses; a cache that never hits is "
                "just overhead, and one that always hits after the first call is doing its job. Results should be "
                "treated as immutable, because a caller who mutates a cached list can corrupt every later answer. "
                "Today you cache totals per region, request one region twice, and count how many times the real "
                "computation ran. Two regions and three requests produce two computations, which is the whole idea: "
                "repeated questions become cheap, and the counter makes that saving visible without a stopwatch. A cache is a correctness decision disguised as a speed trick, and it deserves the same review."
            ),
            code=(
                'ROWS = [\n'
                '    {"region": "north", "amount": "10"},\n'
                '    {"region": "south", "amount": "7"},\n'
                '    {"region": "north", "amount": "5"},\n'
                ']\n'
                'CACHE = {}\n'
                'CALLS = {"computations": 0, "hits": 0}\n'
                '\n'
                'def compute_total(rows, region):\n'
                '    CALLS["computations"] += 1\n'
                '    return sum(int(row["amount"]) for row in rows if row["region"] == region)\n'
                '\n'
                'def cached_total(rows, region):\n'
                '    if region in CACHE:\n'
                '        CALLS["hits"] += 1\n'
                '        return CACHE[region]\n'
                '    CACHE[region] = compute_total(rows, region)\n'
                '    return CACHE[region]\n'
                '\n'
                'print("north", cached_total(ROWS, "north"))\n'
                'print("north again", cached_total(ROWS, "north"))\n'
                'print("south", cached_total(ROWS, "south"))\n'
                'print("computations", CALLS["computations"])\n'
                'print("hits", CALLS["hits"])\n'
                'assert CALLS == {"computations": 2, "hits": 1}\n'
                'assert CACHE == {"north": 15, "south": 7}\n'
                'print("two regions, two computations")'
            ),
            variant_b="add a cache key that includes the row count and show why changing the rows forces a miss",
            variant_c="clear the cache after appending a row and compare the computed totals before and after",
            mistakes=[
                "Keying only by region while the underlying rows have changed, so stale totals win.",
                "Caching an unhashable or mutable input without a stable key.",
                "Returning a cached list that a caller then mutates, corrupting later answers.",
            ],
            q1=(
                "What must a cache key include to stay correct?",
                "Every input that can change the answer, such as the region plus the dataset version, or the cache must be cleared when data changes.",
            ),
            homework=(
                "Write `memo_total(rows, region, cache)` that reuses a cached total keyed by region and returns the "
                "value plus whether it was a hit. Request two regions three times, print the hit flags, and "
                "comment which line keeps the cache honest when the rows would change."
            ),
            patterns=["def ", "print(", "cache"],
            mapping=(
                "pandas users memoise expensive groupbys or repeated merges the same way; the key and invalidation "
                "rules decide whether the cache is an optimisation or a correctness bug."
            ),
        ),
        156: dict(
            topic="Measuring work by counting operations",
            idea=(
                "Timing is a poor measurement for a lesson and a fragile one in a test: the same code runs at "
                "different speeds on different machines, under different loads, and even between two runs on the "
                "same laptop. Counting work is better. You add a counter where the work happens, increment it once "
                "per iteration or once per comparison, and compare implementations by the number that comes out. "
                "The counts are integers, so they are reproducible, printable and assertable. They are also a model "
                "rather than a truth: Python does more behind each comparison than your counter sees, and constants "
                "matter at small sizes. What the counter captures reliably is how the amount of work grows as the "
                "data grows, which is exactly the question scaling asks. The technique is to count at the boundary "
                "of the algorithm, not inside library calls you do not control, and to compare two implementations "
                "on identical input. Today you find duplicates twice, once with every pair and once with a set, "
                "counting checks in each. The pair version makes ten checks for five values and the set version "
                "makes five, so the difference is visible before any stopwatch is involved. Count once, print the number, and keep it beside the implementation so a future change can be compared."
            ),
            code=(
                'VALUES = ["a", "b", "c", "a", "d"]\n'
                '\n'
                'def pair_checks(values):\n'
                '    checks = 0\n'
                '    duplicates = 0\n'
                '    for i in range(len(values)):\n'
                '        for j in range(i + 1, len(values)):\n'
                '            checks += 1\n'
                '            if values[i] == values[j]:\n'
                '                duplicates += 1\n'
                '    return duplicates, checks\n'
                '\n'
                'def set_checks(values):\n'
                '    checks = 0\n'
                '    duplicates = 0\n'
                '    seen = set()\n'
                '    for value in values:\n'
                '        checks += 1\n'
                '        if value in seen:\n'
                '            duplicates += 1\n'
                '        seen.add(value)\n'
                '    return duplicates, checks\n'
                '\n'
                'slow_dupes, slow_checks = pair_checks(VALUES)\n'
                'fast_dupes, fast_checks = set_checks(VALUES)\n'
                'print("pair checks", slow_checks, "duplicates", slow_dupes)\n'
                'print("set checks", fast_checks, "duplicates", fast_dupes)\n'
                'assert slow_dupes == fast_dupes == 1\n'
                'assert slow_checks == 10 and fast_checks == 5\n'
                'print("counted work, not elapsed time")'
            ),
            variant_b="add a sixth value and predict both counts before running the comparison",
            variant_c="count character comparisons in a string search and compare a naive scan with a dictionary",
            mistakes=[
                "Using elapsed time in an assertion, so the test fails on a slow or busy machine.",
                "Counting calls to a library instead of the loop you actually control.",
                "Concluding the faster implementation is faster at every size from one small count.",
            ],
            q1=(
                "Why count comparisons instead of timing a loop?",
                "Counts are deterministic and machine-independent, so they can be asserted and compared reliably while still showing how work grows.",
            ),
            homework=(
                "Write `count_work(values)` that returns the number of comparisons made by a pair scan and by a "
                "set scan. Run it on five values containing one duplicate, print both counts, and comment which "
                "loop line is the one being counted instead of timed."
            ),
            patterns=["def ", "return", "print("],
            mapping=(
                "The same reasoning explains why vectorised pandas operations beat row-wise Python: fewer counted "
                "steps per row, and the step count is what a benchmark should compare."
            ),
        ),
        157: dict(
            topic="Unit tests for transforms",
            idea=(
                "A unit test for a transform is a small, fast check that a pure function turns known input into "
                "known output. Pure matters: if the function reads a file, calls the network or depends on the "
                "clock, the test becomes a setup problem instead of a logic check. The pattern is arrange, act, "
                "assert: build the input, call the function once, compare the result to the expected value. Tables "
                "of cases are useful because they keep the examples side by side and make missing cases obvious. "
                "The cases worth writing are the boring ones: an empty string, a value surrounded by spaces, mixed "
                "capitalisation, a missing optional field. Those are exactly the inputs that real exports contain "
                "and that a happy-path example never exercises. A good failure message includes the input, the "
                "actual result and the expected result, so a red test explains itself. Tests also serve as "
                "executable documentation: a reader can see the promised behaviour without running the whole "
                "pipeline. Today you test a small name-cleaning transform against four cases, including empty and "
                "whitespace-padded input, and print how many passed. The transform is trivial; the habit of "
                "checking it before it enters a report is not. Run the cheap tests on every change; they are fast enough that skipping them is never justified."
            ),
            code=(
                'def clean_name(value):\n'
                '    return value.strip().title()\n'
                '\n'
                'CASES = [\n'
                '    ("  ada ", "Ada"),\n'
                '    ("BOB", "Bob"),\n'
                '    ("", ""),\n'
                '    ("grace hopper", "Grace Hopper"),\n'
                ']\n'
                '\n'
                'def run_tests():\n'
                '    passed = 0\n'
                '    for given, expected in CASES:\n'
                '        actual = clean_name(given)\n'
                '        assert actual == expected, (given, actual, expected)\n'
                '        passed += 1\n'
                '    return passed\n'
                '\n'
                'print("cases", len(CASES))\n'
                'print("passed", run_tests())\n'
                'assert run_tests() == 4\n'
                'print("transform checked before it is trusted")'
            ),
            variant_b="add a case where the input is already clean and confirm title-casing leaves it unchanged",
            variant_c="change one expected value so the assertion fails and read the tuple in the error message",
            mistakes=[
                "Testing through the whole pipeline so a failure could come from any of five steps.",
                "Only testing the happy path and never the empty or whitespace-padded input.",
                "Depending on the current date or a real file inside the transform under test.",
            ],
            q1=(
                "What makes a transform easy to unit test?",
                "It is pure: its return value depends only on its arguments, with no file, network or clock involved.",
            ),
            homework=(
                "Write `test_clean(value)` that asserts a cleaning rule against a table of at least four cases, "
                "including an empty string. Run the table, print the number of cases passed, and comment which line "
                "would show the input and expected value when an assertion fails."
            ),
            patterns=["def ", "assert", "print("],
            mapping=(
                "pandas users wrap their cleaning steps in small functions for the same reason; a tested transform "
                "is safe to reuse in the next chunked run."
            ),
        ),
        158: dict(
            topic="Golden-file report tests",
            idea=(
                "A golden-file test compares a generated report against a stored copy of the exact output you "
                "expect. It is the right tool for formatting-heavy work, because it catches a changed header, a "
                "missing newline, a different column order or an unrounded total that a numeric assertion would "
                "miss. The golden file is reviewed like code: when the output changes on purpose, you regenerate it "
                "and read the diff; when it changes by accident, the test fails and tells you where. The weakness "
                "is brittleness. Output containing timestamps, random ids, absolute paths or unstable row order "
                "will fail for reasons unrelated to the logic, so those values must be fixed, injected or "
                "normalised before comparison. Line endings also deserve normalising, because the same writer can "
                "emit different endings on different platforms. Keep the fixture small enough that a human can read "
                "the whole golden file in one screen. Today you generate a tiny CSV report, compare it to a golden "
                "string, and print the first differing line if it does not match. The passing case is quiet; the "
                "useful part is that any future formatting change now has to be acknowledged rather than discovered "
                "in production. A golden file is also documentation of the agreed report format, readable by anyone who opens it."
            ),
            code=(
                'def build_report(rows):\n'
                '    totals = {}\n'
                '    for region, amount in rows:\n'
                '        totals[region] = totals.get(region, 0) + int(amount)\n'
                '    lines = ["region,total"]\n'
                '    for region in sorted(totals):\n'
                '        lines.append(f"{region},{totals[region]}")\n'
                '    return "\\n".join(lines) + "\\n"\n'
                '\n'
                'GOLDEN = "region,total\\nnorth,15\\nsouth,7\\n"\n'
                'actual = build_report([("north", "10"), ("south", "7"), ("north", "5")])\n'
                'print(actual, end="")\n'
                '\n'
                'if actual != GOLDEN:\n'
                '    for number, (got, want) in enumerate(zip(actual.splitlines(), GOLDEN.splitlines())):\n'
                '        if got != want:\n'
                '            print("first diff line", number + 1, repr(got), "!=", repr(want))\n'
                'assert actual == GOLDEN\n'
                'print("report matches the golden file")'
            ),
            variant_b="change a total by one and print the first differing line instead of only failing",
            variant_c="normalise CRLF to LF before comparing and show that the same report still matches",
            mistakes=[
                "Embedding the current date in the report, so the golden file changes every day.",
                "Regenerating the golden file without reviewing the diff, accepting a real regression.",
                "Comparing reports whose row order is unstable because the query was not sorted.",
            ],
            q1=(
                "When is a golden-file test better than checking a few numbers?",
                "When the exact shape, order and formatting of the report matter, since the golden file captures all of it at once.",
            ),
            homework=(
                "Write `golden_check(rows, golden)` that builds report text, compares it to the stored golden "
                "string, and returns the first differing line number or zero. Run it once with a matching golden and "
                "once with a changed total, print both results, and comment why the comparison normalises line "
                "endings."
            ),
            patterns=["def ", "return", "print("],
            mapping=(
                "A pandas report exported with `to_csv` is a natural golden candidate; the test pins the exact text "
                "that downstream people open in Excel."
            ),
        ),
        159: dict(
            topic="Fixtures and sample sheets",
            idea=(
                "Fixtures are named, reusable pieces of input data that make tests readable. Instead of building a "
                "sheet inline in every test, you define a small builder with sensible defaults and call it with "
                "only the values the test cares about. The name of the fixture then documents the scenario: a "
                "normal sheet, an empty sheet with only a header, a sheet with a missing optional column, a sheet "
                "with a duplicate id. Good fixtures are small, deterministic and obvious. They should not be shared "
                "mutable objects, because one test that edits a row can break the next test in a way that is hard "
                "to see. A builder function avoids that by returning a fresh structure on every call. It also keeps "
                "the shape consistent, so every test exercises the same header and the same column order. Too many "
                "fixtures is its own problem; a handful that cover the interesting shapes beats a library of "
                "near-duplicates. Today you define two fixture builders, one populated and one header-only, and a "
                "helper that counts data rows. The same helper works on both, which is the point: a well-shaped "
                "fixture lets the test focus on behaviour instead of setup. Name fixtures after the scenario, not after the test that happens to use them today."
            ),
            code=(
                'def make_sheet(*rows):\n'
                '    return [["id", "region", "amount"]] + [list(row) for row in rows]\n'
                '\n'
                'def fixture_small():\n'
                '    return make_sheet(("1", "north", "10"), ("2", "south", "7"))\n'
                '\n'
                'def fixture_header_only():\n'
                '    return make_sheet()\n'
                '\n'
                'def data_rows(sheet):\n'
                '    return sheet[1:]\n'
                '\n'
                'for name, fixture in [("small", fixture_small), ("header-only", fixture_header_only)]:\n'
                '    sheet = fixture()\n'
                '    print(name, "rows", len(data_rows(sheet)), "width", len(sheet[0]))\n'
                '\n'
                'empty = fixture_header_only()\n'
                'empty[0][0] = "changed"\n'
                'assert fixture_header_only()[0][0] == "id"\n'
                'assert len(data_rows(fixture_small())) == 2\n'
                'print("each call returns a fresh sheet")'
            ),
            variant_b="add a fixture with a duplicate id and use it in a test that expects a rejected row",
            variant_c="give `make_sheet` an optional header argument and build a fixture with different columns",
            mistakes=[
                "Reusing one module-level sheet across tests so one test's edit leaks into another.",
                "Building fixture data inline in every test, hiding which shapes are actually covered.",
                "Making fixtures so large that a failing assertion is hard to trace back to a row.",
            ],
            q1=(
                "Why return a fresh sheet from a fixture builder instead of sharing one sheet object?",
                "A fresh object prevents one test's mutation from changing the input of a later test.",
            ),
            homework=(
                "Write `fixture(rows)` that returns a fresh sheet with a fixed header, and `rows_of(sheet)` that "
                "counts data rows. Build a populated fixture and a header-only fixture, print both counts, and "
                "comment which line guarantees the two tests cannot share mutable data."
            ),
            patterns=["def ", "return", "print("],
            mapping=(
                "Small DataFrames built by a fixture function serve the same role in pandas tests as these sheet "
                "builders, and they keep chunk-boundary cases reproducible."
            ),
        ),
        160: dict(
            topic="Property checks for cleaning rules",
            idea=(
                "Example tests check inputs you thought of. Property checks state a rule that must hold for every "
                "input and then verify it across a set of samples. Cleaning rules have several natural properties. "
                "Idempotence: cleaning an already clean record changes nothing. Key stability: the set of keys after "
                "cleaning is exactly the normalised set before, with no keys invented or lost. Value preservation: "
                "cleaning may trim or re-case, but it must not replace a blank with a made-up value. Length "
                "preservation: one input record produces one output record, unless the rule explicitly says "
                "otherwise. These checks are cheap to write with plain loops and assert statements, and they catch "
                "a class of bug that a single example misses, such as a rule that works once but keeps changing the "
                "record on every pass. They do not replace example tests; they complement them. Keep the sample set "
                "small but varied, including odd spacing, empty values and mixed case. Today you run four "
                "properties over three sample records and print a line for each. The output is boring on purpose: "
                "the properties hold, and the code shows exactly what would have to break for them to fail. Keep the property list short and meaningful; three strong invariants beat twenty weak assertions."
            ),
            code=(
                'def clean_record(record):\n'
                '    return {key.strip().lower(): str(value).strip() for key, value in record.items()}\n'
                '\n'
                'SAMPLES = [\n'
                '    {" Item ": " widget ", "Qty": "3"},\n'
                '    {"item": "gizmo", " qty ": "  "},\n'
                '    {"ITEM": "cable", "QTY": "2"},\n'
                ']\n'
                '\n'
                'for sample in SAMPLES:\n'
                '    once = clean_record(sample)\n'
                '    twice = clean_record(once)\n'
                '    assert once == twice\n'
                '    assert set(once) == {key.strip().lower() for key in sample}\n'
                '    assert len(once) == len(sample)\n'
                '    assert all(value == value.strip() for value in once.values())\n'
                '    print("ok", sorted(once))\n'
                '\n'
                'assert clean_record({"Item": "  "})["item"] == ""\n'
                'print("properties held for all samples")'
            ),
            variant_b="add the property that cleaning never turns an empty value into a non-empty one",
            variant_c="add a sample with mixed-case keys to show key stability across spelling variants",
            mistakes=[
                "Checking one example and calling it a property, so unanticipated inputs are never covered.",
                "Writing a property that restates the implementation instead of an independent invariant.",
                "Using a shared sample that a previous check has already mutated.",
            ],
            q1=(
                "What does idempotence mean for a cleaning rule?",
                "Cleaning an already cleaned record produces exactly the same record, so a second pass changes nothing.",
            ),
            homework=(
                "Write `check_properties(records)` that verifies idempotence, key stability, and that no blank "
                "value is replaced, returning the number of properties that held. Run it on three records, print "
                "the count, and comment which assertion catches a rule that changes a record on a second pass."
            ),
            patterns=["def ", "assert", "print("],
            mapping=(
                "pandas cleaning chains are hard to reason about by example; stating invariants such as idempotence "
                "makes a chunked cleaning step safe to rerun."
            ),
        ),
        161: dict(
            topic="Refactoring a long script",
            idea=(
                "A long script is not wrong, it is just expensive to change and impossible to test in pieces. "
                "Refactoring means improving its structure without changing what it produces. The reliable order is "
                "to capture the current output first, then extract one responsibility at a time, checking after "
                "each step that the output is identical. In a spreadsheet pipeline the natural seams are reading, "
                "parsing, transforming, aggregating and formatting. Each becomes a function with a clear input and "
                "output, and the top-level function becomes a short composition of those steps. Smaller functions "
                "are easier to name, easier to test and easier to reuse in tomorrow's report. They also make the "
                "work visible: a function called `parse` that converts strings to numbers is obviously a different "
                "concern from one called `totals` that groups them. The temptation is to rewrite everything at "
                "once, which turns a safe refactor into a debugging session. Today you compare a single long block "
                "with the same logic split into three functions and assert that both produce the same rows. The "
                "comparison is the safety net; the split is what makes the next change cheap. Commit or save the captured output before touching the code, so the comparison survives a mistake."
            ),
            code=(
                'ROWS = [["north", "10"], ["south", "7"], ["north", "5"]]\n'
                '\n'
                'def parse(rows):\n'
                '    return [(region, int(amount)) for region, amount in rows]\n'
                '\n'
                'def totals(records):\n'
                '    result = {}\n'
                '    for region, amount in records:\n'
                '        result[region] = result.get(region, 0) + amount\n'
                '    return result\n'
                '\n'
                'def format_report(totals_map):\n'
                '    return [(region, totals_map[region]) for region in sorted(totals_map)]\n'
                '\n'
                'def pipeline(rows):\n'
                '    return format_report(totals(parse(rows)))\n'
                '\n'
                'def long_style(rows):\n'
                '    numbers = {}\n'
                '    for region, amount in rows:\n'
                '        numbers[region] = numbers.get(region, 0) + int(amount)\n'
                '    return [(region, numbers[region]) for region in sorted(numbers)]\n'
                '\n'
                'print("refactored", pipeline(ROWS))\n'
                'assert pipeline(ROWS) == long_style(ROWS)\n'
                'print("same output after splitting the steps")'
            ),
            variant_b="extract the formatting step into its own function and confirm the report is unchanged",
            variant_c="add a skipped-row count from parse and thread it through to the final report",
            mistakes=[
                "Changing behaviour while moving code, so a refactor becomes an untested rewrite.",
                "Extracting a function that still depends on globals, which keeps the seam untestable.",
                "Deleting the old version before the new one is proven to produce identical output.",
            ],
            q1=(
                "What is the safety net that makes a refactor trustworthy?",
                "Capturing the old output and asserting the refactored pipeline produces exactly the same result after each extraction.",
            ),
            homework=(
                "Write `refactor(rows)` that splits parsing, totaling and formatting into three named helpers and "
                "returns the same report rows as one long inline block. Run both versions on four rows, print "
                "whether they match, and comment which helper is the seam you could test alone."
            ),
            patterns=["def ", "return", "print("],
            mapping=(
                "Breaking a pandas script into read, transform and write functions is the same refactor; the seams "
                "are what let you test each stage and swap chunked execution in later."
            ),
        ),
        162: dict(
            topic="Handling very wide sheets",
            idea=(
                "Wide sheets break the assumption that a row is small. A sheet with two hundred columns may have few "
                "rows and still be expensive to copy, because every projection, sort and intermediate list carries "
                "all that width. Most transformations need only a handful of columns, so the first move is to "
                "project: map the header names you need to their positions once, then build a narrow record "
                "containing only those fields. This also makes the code robust to reordering, since the position "
                "lookup follows the name rather than a fixed offset. Missing columns should fail loudly at the "
                "projection step, where the message can name the column, instead of producing a record with silent "
                "holes. A second useful idea is to process columns in groups when the work is column-wise, such as "
                "validating each field or applying a type conversion. Transposing a wide sheet into a narrow tall "
                "form is often the cleanest fix, because it turns many columns into many rows that the existing "
                "row-wise code already handles. Today you project three columns out of an eight-column row, print "
                "the width before and after, and assert the selected values. The sheet is small, but the reduction "
                "from eight fields to three is the same one that makes a real wide export manageable."
            ),
            code=(
                'HEADER = ["id", "name", "region", "amount", "note", "owner", "month", "source"]\n'
                'ROW = ["7", "widget", "north", "10", "rush", "ada", "2024-01", "web"]\n'
                'WANTED = ["id", "region", "amount"]\n'
                '\n'
                'def project(header, row, wanted):\n'
                '    positions = {name: header.index(name) for name in wanted}\n'
                '    return {name: row[positions[name]] for name in wanted}\n'
                '\n'
                'picked = project(HEADER, ROW, WANTED)\n'
                'print("sheet width", len(HEADER))\n'
                'print("projected width", len(picked))\n'
                'print(picked)\n'
                '\n'
                'assert picked == {"id": "7", "region": "north", "amount": "10"}\n'
                'assert set(picked) == set(WANTED)\n'
                'print("touched 3 of 8 columns")'
            ),
            variant_b="ask for a column that is missing and raise ValueError naming it before any row is read",
            variant_c="transpose the eight-column row into name/value pairs and print only the wanted three",
            mistakes=[
                "Copying every column into intermediate records when only three fields are used.",
                "Hard-coding positions in a wide layout that gets reordered by a human editor.",
                "Ignoring a missing column and writing records with absent fields.",
            ],
            q1=(
                "Why project a wide row down to the needed columns before transforming it?",
                "Every later copy carries only the useful fields, so memory and per-row work stop growing with sheet width.",
            ),
            homework=(
                "Write `project_row(header, row, wanted)` that maps column names to positions once and returns only "
                "the wanted fields. Run it on an eight-column row selecting three columns, print the projected "
                "dict, and comment how a missing column should fail loudly."
            ),
            patterns=["def ", "return", "print("],
            mapping=(
                "pandas users do this with `usecols` at read time and `df[[...]]` after; either way, width is a "
                "cost to control before the chunk is processed."
            ),
        ),
        163: dict(
            topic="Tuning the pipeline",
            idea=(
                "Tuning starts with a measurement, not a guess. Before changing anything, capture the current cost "
                "using whatever stable metric you have: counted operations, rows read, lookups performed or passes "
                "over the data. Then change exactly one thing, run the same input again, and compare the counts. "
                "Changing several things at once feels faster but tells you nothing about which change helped. The "
                "usual wins in a spreadsheet pipeline are removing a repeated scan, hoisting an index out of a loop, "
                "avoiding a second parse of the same value, and merging two passes that could be one. The usual "
                "non-wins are micro-optimisations in code that runs once per report, and any change that trades "
                "correctness for speed without a test proving the result is unchanged. A tuning change should "
                "always be paired with the assertion that the output still matches the untuned version. Today you "
                "compare a two-pass pipeline with a one-pass pipeline on the same records, counting steps in each. "
                "Both produce the same total, and the counted difference is the evidence. The lesson is not that one "
                "pass is always better, but that a stable metric makes the comparison honest. Record the metric next to the change so the next person does not repeat the same experiment."
            ),
            code=(
                'RECORDS = [{"name": "item-%d" % i, "amount": str(i % 5)} for i in range(1, 9)]\n'
                '\n'
                'def two_pass(records):\n'
                '    steps = 0\n'
                '    kept = []\n'
                '    for record in records:\n'
                '        steps += 1\n'
                '        kept.append(record)\n'
                '    total = 0\n'
                '    for record in kept:\n'
                '        steps += 1\n'
                '        total += int(record["amount"])\n'
                '    return total, steps\n'
                '\n'
                'def one_pass(records):\n'
                '    steps = 0\n'
                '    total = 0\n'
                '    for record in records:\n'
                '        steps += 1\n'
                '        total += int(record["amount"])\n'
                '    return total, steps\n'
                '\n'
                'before, before_steps = two_pass(RECORDS)\n'
                'after, after_steps = one_pass(RECORDS)\n'
                'print("before", before, "steps", before_steps)\n'
                'print("after", after, "steps", after_steps)\n'
                'assert before == after\n'
                'assert after_steps < before_steps\n'
                'print("same total, fewer counted steps")'
            ),
            variant_b="add a `startswith` filter to the one-pass version and compare the new step count",
            variant_c="hoist a repeated dictionary lookup out of the loop and count how many accesses disappear",
            mistakes=[
                "Tuning by intuition without a before-and-after count on the same input.",
                "Changing several parts at once, so the cause of any speedup is unknown.",
                "Dropping a correctness assertion because the faster version appears to work.",
            ],
            q1=(
                "Why change only one thing at a time when tuning a pipeline?",
                "Then the before-and-after counts attribute the difference to that change instead of to a mixture of edits.",
            ),
            homework=(
                "Write `tune(records)` that runs a two-pass and a one-pass total, returns both totals and both "
                "counted step counts, and asserts the totals match. Run it on six records, print the counts, and "
                "comment which line makes the comparison about work rather than time."
            ),
            patterns=["def ", "return", "assert"],
            mapping=(
                "The same discipline applies to pandas: measure passes, merges and allocations before rewriting a "
                "pipeline for speed, and keep a test that the result is unchanged."
            ),
        ),
        164: dict(
            topic="Review: scaling and testing checklist",
            idea=(
                "A scaling review is a checklist you run before trusting a pipeline on real data. Does it stream "
                "rows, or does it hold the whole sheet? Is the memory it keeps bounded and named, or does it grow "
                "with input? Are chunks handled at their boundaries, including a short final one? Is the index "
                "built once and rebuilt when data changes? Does every cache key include the inputs that affect the "
                "answer, and are hits and misses counted? Is the work measured by counted operations rather than "
                "wall-clock time? Do transforms have table-driven unit tests, does the report have a golden check, "
                "and do fixtures cover empty and malformed shapes? Do the cleaning rules hold their properties, and "
                "does the refactored script still produce the original output? Does a wide sheet get projected to "
                "the columns actually needed? The checklist is worth writing as code when you can, because a check "
                "that runs is harder to skip than a note that is read once. Today you run five such checks over a "
                "tiny dataset and print pass or fail for each. None of the individual checks is clever; together "
                "they are the difference between a script that works on the sample and a pipeline that survives a "
                "growing export."
            ),
            code=(
                'ROWS = [{"id": "K1", "value": 10}, {"id": "K2", "value": 20}, {"id": "K3", "value": 30}]\n'
                'INDEX = {row["id"]: row for row in ROWS}\n'
                'CACHE = {}\n'
                '\n'
                'def cached_value(key):\n'
                '    if key not in CACHE:\n'
                '        CACHE[key] = INDEX[key]["value"]\n'
                '    return CACHE[key]\n'
                '\n'
                'def check(name, condition):\n'
                '    print("PASS" if condition else "FAIL", name)\n'
                '    return condition\n'
                '\n'
                'seen = set()\n'
                'for row in ROWS:\n'
                '    seen.add(row["id"])\n'
                '\n'
                'results = [\n'
                '    check("rows streamed", len(seen) == len(ROWS)),\n'
                '    check("index covers ids", set(INDEX) == seen),\n'
                '    check("index built once", INDEX["K2"]["value"] == 20),\n'
                '    check("cache reuses value", cached_value("K2") == cached_value("K2") == 20),\n'
                '    check("counted work stable", len(ROWS) == 3),\n'
                ']\n'
                'print("passed", sum(results), "of", len(results))\n'
                'assert all(results)'
            ),
            variant_b="add a golden-report check and confirm an intentionally changed total fails it",
            variant_c="add a wide-sheet projection check and count how many checks now run",
            mistakes=[
                "Treating the checklist as paperwork and skipping the checks that are hard to automate.",
                "Passing every check on the sample sheet but never running the same checks on a chunk-sized input.",
                "Checking output values without checking memory, cache keys or index freshness.",
            ],
            q1=(
                "Why express a scaling checklist as runnable checks?",
                "Checks that execute cannot be forgotten and fail visibly, while a written checklist is easy to skip under deadline.",
            ),
            homework=(
                "Write `review(rows)` that runs at least four checks — bounded memory, index coverage, cache key "
                "correctness and a golden report match — and returns the list of failed check names. Run it on a "
                "small clean dataset, print the failures, and comment which check you would add first for a wider "
                "sheet."
            ),
            patterns=["def ", "return", "print("],
            mapping=(
                "This checklist maps onto a chunked pandas pipeline: bounded chunks, stable keys, fresh indexes, "
                "golden outputs and counted work are all testable before the next large export arrives."
            ),
        ),
    },
)
