"""Canonical topic batch: files as an external interface (Lutz ch 9)."""
from canonical_topics import topic

LUTZ_CH9_FILES = {
    "book": "learning-python",
    "chapter": 9,
    "pages": [225, 256],
    "sections": ["Opening Files", "File context managers"],
}


topic(
    "canonical:file-as-external-interface",
    "A file is an interface to storage outside the program, and every read or write goes through an object whose position and lifetime you manage deliberately",
    sources=[dict(LUTZ_CH9_FILES)],
    concept=(
        "A file object is the program's interface to data that lives outside it, on disk or "
        "another device, and it behaves differently from every container type because it "
        "holds a position rather than a collection. Opening a file with the built-in open "
        "function, given a name and a mode, hands back such an object, and the mode decides "
        "what the program is allowed to do: read, create and overwrite, or append at the "
        "end. Reading consumes the file from the current position forward, so a second read "
        "continues where the first left off rather than starting over, and an iteration over "
        "the object yields one line at a time without ever loading the whole file into "
        "memory. Writing appends at the position and does not add a newline on its own, so "
        "the program has to terminate its own lines. Because a file holds an operating "
        "system resource, it has to be closed, and a file that is left open can prevent "
        "other programs from using it or keep buffered output from reaching disk. The "
        "context manager form, a with statement, is the disciplined way to handle that: it "
        "closes the file automatically when the block exits, even when the code inside "
        "raises, so the cleanup is not a detail the programmer has to remember at every "
        "exit point. Storing structured data as text is straightforward, but round-tripping "
        "Python objects through a plain file means choosing a format, which is why json and "
        "pickle exist as separate layers above this one."
    ),
    prerequisites=["canonical:string-as-immutable-sequence"],
    pitfalls=[
        "Reading a file twice in a row and expecting the second read to return the content "
        "again, when it continues from the current position and returns nothing.",
        "Writing lines without an explicit newline character, so the file ends up with all "
        "the values run together on one line.",
        "Opening a file for writing without a with statement and then raising partway "
        "through, so the close never runs and buffered output is lost.",
    ],
    adapters={
        "machine-learning": {
            "framing": (
                "A dataset is usually a file far larger than a notebook cell, so reading it "
                "as an iterable of lines instead of one string is what keeps memory bounded."
            ),
            "application": (
                "Walk the example as a dataset being read from disk. The file is opened in "
                "read mode inside a with statement, and the loop consumes it one line at a "
                "time, so a file of a million rows costs constant memory rather than "
                "growing with the data. Each line arrives with its trailing newline, so "
                "strip is part of the loop, and that detail is what makes the values usable "
                "as numbers or keys afterwards. The important contrast is with read, which "
                "pulls the whole file into a single string and is fine for small inputs but "
                "wasteful for large ones, and knowing which to reach for is the practical "
                "judgement this topic trains. Writing a processed subset back out is the "
                "mirror image: a second file is opened for writing, and each line is "
                "written with an explicit newline because the file object does not supply "
                "one."
            ),
            "example_hint": "stream a data file line by line, clean each line, write a filtered subset",
            "assessment_angle": "what iteration buys over read, why strip is needed, and why writes need newlines",
            "day": 5,
            "title": "Stream the Dataset Line by Line, Keep Memory Flat",
            "code": """import os

SAMPLE = "rows.txt"
with open(SAMPLE, "w") as out:
    out.write("id,label,value\\n")
    for i in range(6):
        out.write(f"{i},  row {i} ,{i * 2.5}\\n")

kept = []
with open(SAMPLE) as src:
    next(src)                      # skip the header line
    for line in src:
        parts = [p.strip() for p in line.split(",")]
        value = float(parts[2])
        if value >= 5.0:
            kept.append(parts)

print("rows kept:", len(kept))
for row in kept:
    print(row)

with open("kept.txt", "w") as out:
    for row in kept:
        out.write(",".join(row) + "\\n")

print("wrote:", os.path.getsize("kept.txt"), "bytes")
""",
            "questions": [
                "Why does the loop iterate over the file object instead of calling read first?",
                "Why is strip applied to every part, and what would happen to the label without it?",
                "Each written line ends with an explicit newline. Why is that necessary?",
            ],
            "answers": [
                "Because iterating yields one line at a time and holds only the current one, so memory stays flat, while read would load the entire file into a single string first.",
                "Because each line arrives with its trailing newline and the fields carry padding, so strip removes that noise before the value is parsed and the label is used as a key.",
                "Because the file's write method puts exactly the characters it is given on disk, so without a newline every row would run together on one line.",
            ],
            "homework": (
                "Write stream_rows.py that first creates a CSV-style data file with a header and at "
                "least ten data rows containing padded fields and floats, then opens it for reading "
                "with a with statement, skips the header, and processes each line by splitting on a "
                "comma and stripping every field. Keep the rows whose numeric field meets a "
                "threshold, print the count and the kept rows, then write the kept rows to a second "
                "file with an explicit newline per row and print its size. Observable output: the "
                "kept count, one line per kept row, and the byte size of the output file."
            ),
            "required_patterns": ["with open(", "for ", ".strip(", "float(", "print("],
        },
        "data-viz": {
            "framing": (
                "Charts read their data from a file and often write an export back. Both "
                "directions are file object work, and the direction decides the mode."
            ),
            "application": (
                "Walk the example as a plot script loading its series from a file. The "
                "input is opened for reading and its lines become the data points, with "
                "each line converted to a number; the export is opened for writing and the "
                "rendered summary is stored as text. The mode is what marks the direction "
                "of travel and it is the first thing to check when a script reports a "
                "permission or existence error, because write recreates a file while "
                "append keeps it and read requires it to exist. Iterating over the input "
                "rather than reading it whole also matters for figures built from large "
                "logs, since a plot only needs the numbers, not the entire file in memory "
                "at once. The newline detail appears on the writing side: an exported "
                "summary whose lines are not terminated is a file a later tool will read "
                "as a single long line."
            ),
            "example_hint": "load a series from a file, compute a summary, write it back as an export",
            "assessment_angle": "what the mode controls and why reading iterates instead of loading",
            "day": 5,
            "title": "Load the Series, Write the Export: Two Modes, One Discipline",
            "code": """VALUES = "series.txt"
with open(VALUES, "w") as out:
    out.write("41.2\\n42.0\\n41.8\\n43.1\\n44.6\\n43.9\\n")

series = []
with open(VALUES) as src:
    for line in src:
        series.append(float(line.strip()))

lo, hi = min(series), max(series)
span = hi - lo
print(f"points: {len(series)}  low: {lo}  high: {hi}  span: {span:.2f}")

with open("summary.txt", "w") as out:
    out.write(f"points,{len(series)}\\n")
    out.write(f"low,{lo}\\n")
    out.write(f"high,{hi}\\n")
    out.write(f"span,{span:.2f}\\n")

print(open("summary.txt").read())
""",
            "questions": [
                "The script opens one file for writing and another for reading. What does each mode allow, and which one would fail if the file did not exist?",
                "Why is the series built by iterating over the file rather than with a single read?",
                "Each exported line ends with a newline character. What would the file contain without them?",
            ],
            "answers": [
                "Write mode recreates the file for output while read mode requires an existing file and only allows input, so the read would fail if the file were absent.",
                "Because iterating yields one line per step and keeps only the current value, so memory stays small, whereas read would hold the whole file as one string.",
                "All four summary values run together on a single line, because write puts down exactly the characters it receives and nothing more.",
            ],
            "homework": (
                "Write series_io.py that writes at least eight numeric lines to a data file, then "
                "opens that file for reading with a with statement and builds a list of floats by "
                "stripping each line. Compute the point count, the low, the high and the span, "
                "print them, then write those four figures as comma-separated lines to an export "
                "file and print the export's contents. Observable output: a summary line, then the "
                "exported text with one value per line."
            ),
            "required_patterns": ["with open(", "float(", ".strip(", "min(", "print("],
        },
        "api-building": {
            "framing": (
                "An API often answers from a file or writes what it received, and a request "
                "handler that leaves a file open is a resource leak that shows up only "
                "under load."
            ),
            "application": (
                "Walk the example as a handler loading a small configuration and saving an "
                "incoming payload. The config is read inside a with block, so the file is "
                "closed the moment the block ends even though the handler keeps running, "
                "and that is the property that makes a with statement worth using over an "
                "open followed by a manual close at the bottom of a long function. The "
                "payload is written with an explicit newline per record so the file can be "
                "read back line by line later, which is the round trip the next request "
                "depends on. Appending rather than writing is the mode choice that matters "
                "for a request log, because write would erase the history every handler "
                "wrote before, and the mode is the only thing distinguishing those two "
                "behaviours."
            ),
            "example_hint": "read a config under a with statement and append each request to a log",
            "assessment_angle": "what a with statement guarantees and why a request log is appended",
            "day": 5,
            "title": "Open Under a With, Append Never Overwrite",
            "code": """from pathlib import Path

CONFIG = Path("config.txt")
CONFIG.write_text("name=pyschool\\nport=8080\\nregion=us-east\\n")

config = {}
with open(CONFIG) as src:
    for line in src:
        if "=" in line:
            key, value = line.strip().split("=", 1)
            config[key] = value
print("config:", config)

payloads = [{"id": 1}, {"id": 2}, {"id": 3}]
for payload in payloads:
    with open("requests.log", "a") as log:
        log.write(f"received id={payload['id']}\\n")

print("log lines:", len(open("requests.log").read().splitlines()))
""",
            "questions": [
                "What does the with statement guarantee about the config file, and why does that matter inside a request handler?",
                "The request log is opened in append mode rather than write mode. What would write mode cost?",
                "Each payload is written with a trailing newline. What does the final line count depend on?",
            ],
            "answers": [
                "It closes the file when the block ends, even if the code inside raises, so the handler cannot leak an open file handle across the rest of the request.",
                "It would truncate the log on every request, so only the last payload would survive and the history of received requests would be lost.",
                "On one newline character per written record, because the log is later split on line boundaries and a record without a newline would merge into the previous one.",
            ],
            "homework": (
                "Write handler_io.py that writes a three-line key-value config file, then reads it "
                "inside a with statement, splits each line on an equals sign, and builds a "
                "dictionary printed at the end. Then simulate at least five incoming request "
                "payloads, appending one line per payload to a log file inside a with statement, "
                "and print the number of lines the log finally contains. Observable output: the "
                "config dictionary and the log line count."
            ),
            "required_patterns": ["with open(", "\"a\"", "for ", ".split(", "print("],
        },
        "web-scraping": {
            "framing": (
                "A scraper must be safe to stop halfway, which means every page it fetches "
                "is persisted as it goes, not held in memory until the end."
            ),
            "application": (
                "Walk the example as a scrape that writes each result as it arrives. The "
                "output file is opened for appending inside a with statement, so a run "
                "that is interrupted has still kept everything fetched so far, and a "
                "re-run continues from where it left off rather than starting an empty "
                "file. That is the practical reason the mode and the resource management "
                "matter together: append preserves prior work and the with statement "
                "flushes each block's output on exit. Reading the file back at the end is "
                "the verification step, and it is done by iterating so the check itself "
                "does not load everything at once. A scraper that collected a thousand "
                "pages into a list and wrote them only at the end would lose all of them "
                "to a network error, which is the failure mode this pattern exists to "
                "avoid."
            ),
            "example_hint": "append each scraped record to a file as it is fetched, then read it back",
            "assessment_angle": "why append-plus-with makes a scraper interruptible",
            "day": 5,
            "title": "Persist Every Page as You Go, Not at the End",
            "code": """from pathlib import Path

out = Path("products.txt")
if out.exists():
    out.unlink()

pages = [(1, "Mug", "12.5"), (2, "Kettle", "34.0"), (3, "Bowl", "8.25")]

for page, name, price in pages:
    print(f"fetched page {page}")
    with open(out, "a") as dst:
        dst.write(f"{page}\\t{name}\\t{price}\\n")

count = 0
with open(out) as src:
    for line in src:
        count += 1
        print("stored:", line.strip())

print("records on disk:", count)
""",
            "questions": [
                "Why is each record written inside the loop instead of collecting them all and writing once at the end?",
                "What does opening in append mode guarantee about a re-run of the scraper?",
                "The final check reads the file back by iterating. What does that verify, and why does the count come out as it does?",
            ],
            "answers": [
                "So that an interrupted run has already saved every page it fetched, rather than losing all of them to a failure before the single final write.",
                "That the existing file is kept and new records are added after the old ones, so a re-run continues instead of starting from an empty file.",
                "That each fetched page really reached disk and is readable as a record, and the count equals the number of written lines because each had its own terminating newline.",
            ],
            "homework": (
                "Write incremental_scrape.py that removes any existing output file, then simulates "
                "fetching at least six pages, printing a fetched message and appending one "
                "tab-separated record per page inside a with statement. Finally open the file for "
                "reading, iterate its lines, print each stored record, and print the total record "
                "count. Observable output: one fetched line and one stored line per page, plus the "
                "final count."
            ),
            "required_patterns": ["with open(", "\"a\"", "for ", ".strip(", "print("],
        },
        "testing-qa": {
            "framing": (
                "A test fixture has to build a file, let the code under test use it, and "
                "clean up afterwards, and the with statement is what makes that safe."
            ),
            "application": (
                "Walk the example as a fixture writing a temporary file for a function to "
                "parse. The file is created inside a with statement, so it is closed "
                "before the code under test opens it, which matters because two open "
                "handles to the same file can see different states while output is still "
                "buffered. The function under test is then called with the filename and "
                "its result is asserted on, and the fixture cleans up at the end. The "
                "skill worth naming is that a test of file-reading code has to control "
                "the file's lifetime explicitly: creating it, closing it, and removing "
                "it are all part of the arrangement, and a fixture that leaves files "
                "behind makes later tests order-dependent. Writing the fixture with a "
                "known number of lines is what makes the expected value computable "
                "rather than guessed."
            ),
            "example_hint": "build a temp file in a with statement, call the parser, assert and clean up",
            "assessment_angle": "why the fixture closes the file before the code under test reads it",
            "day": 5,
            "title": "Build the Fixture, Close It, Then Let the Code Under Test Read",
            "code": """from pathlib import Path

FIXTURE = Path("fixture.csv")


def count_rows(path):
    with open(path) as src:
        return sum(1 for line in src if line.strip())


with open(FIXTURE, "w") as out:
    for i in range(5):
        out.write(f"row-{i}\\n")

total = count_rows(FIXTURE)
print(f"rows reported: {total}")
print("matches expected:", total == 5)

FIXTURE.unlink()
print("fixture removed:", not FIXTURE.exists())
""",
            "questions": [
                "Why is the fixture written inside a with statement and closed before count_rows opens it?",
                "The test expects the count to be five. What makes that number knowable in advance?",
                "Why does the fixture delete the file at the end instead of leaving it behind?",
            ],
            "answers": [
                "Because the with statement closes the file when the block ends, so all five lines are flushed to disk before the code under test opens the same file and reads them.",
                "Because the fixture itself wrote exactly five lines, so the expected value is determined by the arrangement rather than observed after the fact.",
                "Because a file left behind would still exist for the next test, making the suite order-dependent and able to pass or fail depending on what ran previously.",
            ],
            "homework": (
                "Write fixture_test.py with a count_rows function that opens a path with a with "
                "statement and counts its non-empty lines. Create a fixture file of exactly seven "
                "lines inside a with statement, call the function, print the reported count and "
                "whether it equals seven, then remove the fixture and print whether it is gone. "
                "Observable output: the reported count, a match line, and a removal confirmation."
            ),
            "required_patterns": ["with open(", "sum(", "for ", ".strip(", "print("],
        },
        "devops-scripting": {
            "framing": (
                "Config files, inventory files and state files are the everyday currency of "
                "scripting, and every one of them is read, transformed and written back "
                "through a file object."
            ),
            "application": (
                "Walk the example as a script that rewrites a config file in place, but "
                "safely. The source is read and parsed into values, then a new file is "
                "written, and only when that succeeds does the script replace the "
                "original, which is the pattern that keeps a config from being left "
                "half-written if the script fails midway. The distinction between "
                "writing to the real file directly and writing to a temporary file first "
                "is the transferable lesson: a crashed script that truncated the live "
                "config has destroyed the thing it was editing. Iterating over the input "
                "and stripping each line is how comments and blank lines get filtered "
                "out, and writing with explicit newlines is what keeps the output "
                "readable by the next tool in the pipeline."
            ),
            "example_hint": "read a config, write a replacement to a temp file, swap it in",
            "assessment_angle": "why the rewrite goes through a temporary file first",
            "day": 5,
            "title": "Rewrite Config Through a Temp File, Then Swap",
            "code": """from pathlib import Path
import os

config = Path("app.conf")
config.write_text("workers=4\\n# tuned by hand\\nthreads=8\\n\\nlevel=info\\n")

parsed = {}
with open(config) as src:
    for line in src:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        key, value = line.split("=", 1)
        parsed[key] = value

parsed["threads"] = "16"
print("parsed:", parsed)

staged = Path("app.conf.new")
with open(staged, "w") as out:
    for key, value in parsed.items():
        out.write(f"{key}={value}\\n")

os.replace(staged, config)
print("final config:")
print(config.read_text())
""",
            "questions": [
                "Why is the updated config written to a separate file and then moved over the original?",
                "What do the strip and the startswith check achieve in the reading loop?",
                "After os.replace runs, what does reading the original path return, and why is that safe?",
            ],
            "answers": [
                "So that a failure during writing cannot leave the live config half-truncated, since the real file is only replaced once the replacement is complete on disk.",
                "They drop blank lines and comment lines before parsing, so only real key-value pairs reach the dictionary.",
                "The new contents, because the replacement was moved into place atomically, so the original path now points at the finished file.",
            ],
            "homework": (
                "Write safe_rewrite.py that writes an app config file containing at least three "
                "key-value lines, a comment and a blank line. Read it with a with statement, skip "
                "blank and comment lines, parse the rest into a dictionary, change one value, then "
                "write the result to a separate staged file and move it over the original. Print "
                "the parsed dictionary and the final contents of the config path. Observable "
                "output: the dictionary and the rewritten config text."
            ),
            "required_patterns": ["with open(", "os.replace", ".strip(", "for ", "print("],
        },
        "algo-trading": {
            "framing": (
                "A strategy's historical data is a file too large to hold in memory and "
                "too valuable to lose, so it is streamed and its outputs are appended."
            ),
            "application": (
                "Walk the example as a backtest streaming a price file. Each line is one "
                "bar, and the loop converts it and updates a running statistic without "
                "ever holding the whole series, which is what makes the backtest's "
                "memory cost independent of the number of years of data. The output, a "
                "list of trades the strategy would have taken, is appended to a results "
                "file as each signal fires, so a backtest interrupted partway still has "
                "a partial trade log rather than nothing. Reading the input by position "
                "is the other detail: the file object advances on each read, so mixing a "
                "read with a loop over the same object double-consumes it, and the "
                "discipline of choosing one consumption method is what keeps the "
                "backtest's row count honest."
            ),
            "example_hint": "stream a price file bar by bar, emit signals, append each trade",
            "assessment_angle": "why the series is streamed and what appending buys a long backtest",
            "day": 5,
            "title": "Stream the Bars, Append the Trades: A Backtest That Scales",
            "code": """from pathlib import Path

bars_file = Path("bars.txt")
bars_file.write_text("101.0\\n101.8\\n102.4\\n101.9\\n103.1\\n102.7\\n104.0\\n")
results = Path("trades.log")
if results.exists():
    results.unlink()

window = []
with open(bars_file) as src:
    for line in src:
        price = float(line.strip())
        window.append(price)
        if len(window) > 3:
            window.pop(0)
        if len(window) == 3 and window[-1] > window[0]:
            with open(results, "a") as out:
                out.write(f"buy @{window[-1]:.2f}\\n")

print("bars processed")
with open(results) as src:
    for line in src:
        print("trade:", line.strip())
""",
            "questions": [
                "Why does the backtest iterate over the file instead of loading every price first?",
                "What does appending each trade as it fires guarantee about a backtest that is interrupted?",
                "The window keeps only the last three prices. What does that choice cost, and what makes it acceptable here?",
            ],
            "answers": [
                "Because iterating yields one bar at a time and keeps only the current price and a short window, so memory stays bounded no matter how many years the file covers.",
                "That a partial trade log is already on disk, since each signal was appended when it fired rather than held for a single final write.",
                "It discards older prices, so only a short trend can be detected; that is acceptable because the strategy is defined on a three-bar window and does not need the older data.",
            ],
            "homework": (
                "Write backtest_stream.py that writes at least twelve bar prices to a file, then "
                "streams it with a with statement, maintaining a window of the last four prices "
                "and appending a trade record to a results file whenever the last price exceeds "
                "the first in the window. Print a processed message, then read the results file "
                "back and print one line per trade. Observable output: a processed line and one "
                "trade line per signal."
            ),
            "required_patterns": ["with open(", "\"a\"", "float(", ".append(", "print("],
        },
        "numerical-methods": {
            "framing": (
                "Numerical results have to be saved exactly as computed, because a result "
                "that exists only in a terminal is a result that is lost when the session "
                "ends."
            ),
            "application": (
                "Walk the example as a computation that writes its iterations to a file "
                "and then reads them back for analysis. Each approximation is written as "
                "it is produced, so the file doubles as a progress record, and the "
                "precision written into each line is chosen with the analysis in mind, "
                "because a value stored with too few digits cannot be examined for "
                "convergence later. Reading the file back with iteration and conversion "
                "is the step that separates storage from analysis: the stored text is "
                "parsed into numbers again, and the difference between successive values "
                "is computed from the parsed series, not from memory. That separation is "
                "what makes the results reproducible, since another script can read the "
                "same file and reach the same conclusion without re-running the method. "
                "Writing with an explicit newline per iteration is what makes each "
                "approximation a separate record rather than a run of digits."
            ),
            "example_hint": "write each iteration to a file, read it back, compute the convergence series",
            "assessment_angle": "why stored precision matters and what reading back enables",
            "day": 5,
            "title": "Store Each Iteration, Read It Back, Measure Convergence",
            "code": """from pathlib import Path

log = Path("iterations.txt")
guess = 1.0
for _ in range(6):
    guess = 0.5 * (guess + 2.0 / guess)     # Newton step for sqrt(2)
    with open(log, "a") as out:
        out.write(f"{guess:.17g}\\n")

series = []
with open(log) as src:
    for line in src:
        series.append(float(line.strip()))

print("stored:", len(series), "iterations")
for previous, current in zip(series, series[1:]):
    print(f"change: {abs(current - previous):.3e}")

print(f"final: {series[-1]:.15f}")
""",
            "questions": [
                "Why is each iteration written with many more digits than a reader would want to see?",
                "What does reading the file back into a list make possible that the running computation alone does not?",
                "Why is each approximation written with its own newline character?",
            ],
            "answers": [
                "Because the stored values are analysed for convergence, so digits discarded in a rounded display could not be recovered later, and the analysis would see noise instead of the real change.",
                "It makes the whole series available at once, so differences between successive approximations can be computed after the fact by a separate script without re-running the method.",
                "So that each approximation is one record on its own line, because the file stores exactly what is written and would otherwise join every value into a single run of digits.",
            ],
            "homework": (
                "Write iterations_io.py that runs at least eight steps of an iterative method, "
                "appending each result to a log file inside a with statement with full precision. "
                "Then open the log for reading, parse the values into a list, print the number "
                "stored, print the absolute change between each successive pair in scientific "
                "notation, and print the final value to fifteen decimal places. Observable "
                "output: a count line, one change line per gap, and the final value."
            ),
            "required_patterns": ["with open(", "float(", "zip(", "abs(", "print("],
        },
    },
)
