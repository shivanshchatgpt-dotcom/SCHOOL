"""Canonical shared-topic library for PySchool.

One record per reusable concept, with source provenance attached. A canonical
topic is deliberately NOT a finished lesson: it holds the concept, its sources,
and per-path adapters. `backend/app/lesson_composer.py` turns a record into a
lesson for a specific path.

Rules this library follows (from the corpus-driven methodology):
  * Provenance is mandatory and machine-verifiable. Every `sources` entry names
    a real book, chapter and page range present in `.books/inventory.json`.
  * Content is transformed, never copied. `concept` is a short original
    explanation; the books are read for grounding, not quoted.
  * Gaps are explicit. `coverage: insufficient` marks a topic the corpus cannot
    fully support, rather than fabricating content.
  * Adapters vary framing, example, practice and assessment per path while the
    canonical concept stays constant.

Add topics by appending to TOPICS. The composer and seeder pick them up
automatically; nothing downstream needs editing.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

CANONICAL_TOPICS: dict[str, dict[str, Any]] = {}


def topic(
    topic_id: str,
    name: str,
    *,
    sources: list[dict],
    concept: str,
    prerequisites: list[str],
    pitfalls: list[str],
    coverage: str = "full",
    gap_note: str = "",
    adapters: dict[str, dict],
) -> dict:
    """Register one canonical topic. See module docstring for the contract."""
    if topic_id in CANONICAL_TOPICS:
        raise ValueError(f"duplicate canonical topic id: {topic_id}")
    if not sources:
        raise ValueError(f"{topic_id}: at least one source is required")
    for src in sources:
        if "pages" in src and (not isinstance(src["pages"], list) or len(src["pages"]) != 2):
            raise ValueError(f"{topic_id}: pages must be [first, last]")
    if coverage not in ("full", "partial", "insufficient"):
        raise ValueError(f"{topic_id}: bad coverage {coverage!r}")
    if coverage != "full" and not gap_note:
        raise ValueError(f"{topic_id}: coverage {coverage} requires gap_note")
    record = {
        "id": topic_id,
        "name": name,
        "sources": sources,
        "concept": concept,
        "prerequisites": prerequisites,
        "pitfalls": pitfalls,
        "coverage": coverage,
        "gap_note": gap_note,
        "adapters": adapters,
    }
    CANONICAL_TOPICS[topic_id] = record
    return record


topic(
    "canonical:variable-binds-to-object",
    "A variable is a name bound to an object, not a box holding a value",
    sources=[
        {
            "book": "learning-python",
            "chapter": 6,
            "pages": [143, 154],
            "sections": [
                "The Dynamic Typing Interlude",
                "Shared References",
                "Shared References and In-Place Changes",
            ],
        },
    ],
    concept=(
        "In Python, an assignment does not copy a value into a named box. It creates an object "
        "and then attaches a name to that object, like a label tied to a parcel. When a second "
        "name is assigned the same value, both labels end up tied to the same parcel, so the "
        "two names are references to one shared object. The type belongs to the object, not to "
        "the name, which is why a name may be rebound to an object of a completely different "
        "type at any time. The practical consequence is about who can observe a change. If an "
        "object is mutable and two names refer to it, altering it through one name is visible "
        "through the other, and that is often the source of a bug that looks inexplicable. "
        "Before mutating anything, ask whether another name still points at the same object."
    ),
    prerequisites=[],
    pitfalls=[
        "Two names share one list and an edit through one of them surprises the other holder.",
        "Treating a variable as a fixed container and being surprised when it is rebound to a "
        "different type.",
        "Confusing shared references with copies when passing an object into a function.",
    ],
    adapters={
        "network-programming": {
            "framing": (
                "A server keeps one connection object under two names — the session registry and "
                "the active handler. Closing it through one name affects what the other sees."
            ),
            "application": (
                "Walk the example through the lens of a connection handler. The registry list "
                "and the handler variable are two names for one object, so appending a session "
                "id through the registry is immediately visible to the handler that thought it "
                "owned an empty list. Trace it in three steps: before the call, both names see "
                "an empty list because both point at the same empty object; inside the call, "
                "append grows that one object; after the call, the handler reads the length "
                "again and finds one entry, without anyone assigning to it. Nothing was passed "
                "back and nothing was returned. The object changed in place, and every name "
                "attached to it reports the new state. When you need the handler to hold a "
                "private snapshot, copy the object at the moment of assignment so the two "
                "names point at two objects, and the registry's later appends stay invisible."
            ),
            "example_hint": "bind two names to one list, mutate it, then print both names",
            "assessment_angle": "what the two names see after one of them mutates the shared "
                "object, and how to make a private copy instead",
            "day": 1,
            "title": "Names Bind to Objects: Two Variables, One Connection",
            "code": (
                "# A session registry and a handler can both name the same list.\n"
                "sessions = []\n"
                "active = sessions          # 'active' is another label on the same object\n"
                "\n"
                "def register(session_id):\n"
                "    sessions.append(session_id)\n"
                "\n"
                "register('conn-1')\n"
                "print('registry:', sessions)\n"
                "print('active view:', active)   # sees conn-1 too: one object, two names\n"
                "\n"
                "# A private copy keeps the two views independent.\n"
                "snapshot = list(active)\n"
                "snapshot.append('conn-2')\n"
                "print('snapshot only:', snapshot)\n"
                "print('registry still:', sessions)"
            ),
            "questions": [
                "After `active = sessions` and `sessions.append('x')`, what does `active` contain, and why?",
                "Why does `snapshot = list(active)` protect the registry from later edits?",
                "If a handler closes a connection stored under two names, what does the other name observe?",
            ],
            "answers": [
                "`active` shows the appended item as well, because both names refer to the same list object; appending mutates that one object.",
                "`list(active)` builds a new list, so edits to the copy never reach the object the registry still names.",
                "It sees the closed state, since both names point at one connection object and closing mutates that object in place.",
            ],
            "homework": (
                "Write session_refs.py with a module-level `sessions` list, an `active` name bound "
                "to it, and functions register(session_id) and snapshot() that returns a private "
                "copy. Then prove the rule: call register twice, print both names, append to the "
                "snapshot only, and print the registry again to show it is unchanged. Add a third "
                "function close(session_id) that removes a session from the shared list, and show "
                "that a variable that still held the old list length now reports the new length. "
                "Observable output: four printed lines that demonstrate the shared view, plus one "
                "line proving the copy is independent."
            ),
            "required_patterns": ["append", "list(", "print(", "def "],
        },
        "etl-pipelines": {
            "framing": (
                "A batch record handed from extract to transform is still one object. If either "
                "stage edits it in place, the other stage's view changes underneath it."
            ),
            "application": (
                "Walk the example through the lens of an extract stage. The caller holds a "
                "list of records and passes it to a transform function; the function sorts or "
                "filters it and returns nothing, because the caller believes the list was only "
                "read. Trace it in three steps: before the call, the caller's list and the "
                "parameter name point at the same object; inside the call, an in-place sort or "
                "a clear rewrites that object; after the call, the caller sees the reordered "
                "or emptied list, even though it never touched it. The bug is not in the "
                "function, it is in the shared reference. The fix is a local copy: when a "
                "stage needs to mutate, it copies first and mutates the copy, so the caller's "
                "view is preserved. In a pipeline, each stage should treat its input as "
                "read-only and hand the next stage a fresh object."
            ),
            "example_hint": "pass one record list into a function, mutate inside, then inspect the caller's list",
            "assessment_angle": "why an in-place edit inside the transform stage is visible to "
                "the extract stage that still holds the same reference",
            "day": 1,
            "title": "Shared Batch Records: Extract and Transform View One Object",
            "code": (
                "# An extracted batch is handed to transform as a reference, not a copy.\n"
                "batch = [{'id': 1, 'amount': '10.5'}, {'id': 2, 'amount': '20.0'}]\n"
                "\n"
                "def normalise(rows):\n"
                "    for row in rows:\n"
                "        row['amount'] = float(row['amount'])   # edits the shared object\n"
                "\n"
                "normalise(batch)\n"
                "print('after transform:', batch)   # extract's own list changed\n"
                "\n"
                "# Keep stages independent by copying at the boundary.\n"
                "def normalise_copy(rows):\n"
                "    rows = [dict(row) for row in rows]\n"
                "    for row in rows:\n"
                "        row['amount'] = float(row['amount'])\n"
                "    return rows\n"
                "\n"
                "raw = [{'id': 3, 'amount': '5.0'}]\n"
                "clean = normalise_copy(raw)\n"
                "print('raw untouched:', raw)\n"
                "print('clean result:', clean)"
            ),
            "questions": [
                "Why does `batch` show floats after `normalise(batch)` returns, even though extract never edited it?",
                "What does `[dict(row) for row in rows]` achieve at the start of normalise_copy?",
                "Give one pipeline symptom that would reveal a stage mutating a record it received by reference.",
            ],
            "answers": [
                "`batch` and the function's `rows` are two names for one list, so the in-place edit is visible through both names.",
                "It builds a fresh list of fresh dictionaries, so every later edit stays inside the function and the caller's records are untouched.",
                "A stage reports values it never wrote, or an audit of the raw input shows numbers where strings were expected.",
            ],
            "homework": (
                "Write stage_refs.py with extract() returning a list of three records (id plus a "
                "string amount), transform_inplace(rows) that converts amounts to float in place, and "
                "transform_copy(rows) that converts and returns a new list of new dicts. Call the "
                "in-place version first and print the original list to prove it changed; then call "
                "the copying version on a fresh extract and print both lists to prove the raw one "
                "survived. Add one assertion-style check: print 'PASS' only if the raw list still "
                "contains strings after the copying transform. Observable output: six lines showing "
                "the shared mutation, the independent copy, and the final check."
            ),
            "required_patterns": ["for ", "float(", "dict(", "def ", "print("],
        },
        "excel-automation": {
            "framing": (
                "A worksheet object reached through two variables is still one worksheet. Editing "
                "through one variable changes what the other variable reads back."
            ),
            "application": (
                "Walk the example through the lens of a report script. One name is your "
                "working list of rows, another is a saved range you exported earlier, and "
                "both point at the same list. When the script appends a totals row to the "
                "working list, the 'saved' range reports the totals too, even though it was "
                "never written to again. Trace it in three steps: assignment makes the second "
                "name a label on the same object; append grows that object; reading either "
                "name shows the new rows. For small scripts this looks like a mystery until "
                "you check that no copy was ever made. The fix is explicit and worth "
                "memorising now: copy with list() or a slice at the moment you want a private "
                "snapshot, and from then on the two names track two independent objects. "
                "Edits to one no longer leak into the other."
            ),
            "example_hint": "reach one list of rows through two names, edit one, read both",
            "assessment_angle": "what the second name reports after the first edits the shared "
                "list, and which operation would have avoided it",
            "day": 1,
            "title": "Two Variables, One Sheet: Edits Are Visible to Both Names",
            "code": (
                "# A report builder holds the same row list as the reader.\n"
                "rows = [['Q1', '100'], ['Q2', '250']]\n"
                "report = rows            # another label on the same list object\n"
                "\n"
                "def fix_amounts(data):\n"
                "    for row in data:\n"
                "        row[1] = int(row[1])   # mutates the shared rows too\n"
                "\n"
                "fix_amounts(report)\n"
                "print('reader view:', rows)   # integers, though rows was never passed\n"
                "\n"
                "# Copy before editing to keep the two views independent.\n"
                "def fix_amounts_copy(data):\n"
                "    data = [list(row) for row in data]\n"
                "    for row in data:\n"
                "        row[1] = int(row[1])\n"
                "    return data\n"
                "\n"
                "source = [['Q3', '300']]\n"
                "fixed = fix_amounts_copy(source)\n"
                "print('source untouched:', source)\n"
                "print('fixed report:', fixed)"
            ),
            "questions": [
                "After `report = rows` and a call that edits `report`, why does printing `rows` show the change?",
                "What does `[list(row) for row in data]` do to keep the caller's rows safe?",
                "Name a spreadsheet-automation bug that shared references would explain.",
            ],
            "answers": [
                "Both names are labels on one list, so mutating the object through either name is visible through the other.",
                "It builds a new list of new row lists, so every edit lands on the copy and the caller's sheet rows stay unchanged.",
                "A reader prints corrected numbers it never asked for, or two reports disagree about the same cell because one edited the shared rows.",
            ],
            "homework": (
                "Write sheet_refs.py holding a module-level `rows` list of three [quarter, amount] "
                "pairs with string amounts, a name `report` bound to it, fix_inplace(data) that "
                "converts amounts to int in place, and fix_copy(data) that returns corrected copies "
                "without touching the input. Call the in-place fix through `report` and print `rows` "
                "to show it changed; then rebuild a fresh `rows` list, call the copying fix, and print "
                "both to show the source survived. Add a final printed line that says 'PASS' only "
                "when the fresh source still contains a string amount after the copy-based fix. "
                "Observable output: six lines plus the final check."
            ),
            "required_patterns": ["int(", "list(", "for ", "def ", "print("],
        },
    },
)


topic(
    "canonical:mutable-sequence-vs-copy",
    "Mutable sequences: in-place change versus making a copy",
    sources=[
        {
            "book": "learning-python",
            "chapter": 8,
            "pages": [197, 224],
            "sections": ["Lists in Action", "Changing Lists In-Place"],
        },
    ],
    concept=(
        "A list holds an ordered series of items and, unlike a string or a tuple, it can be "
        "changed after it is created. There are two ways to change a list, and they are not "
        "interchangeable. Assignment to an index, `L[0] = 99`, alters the existing object: any "
        "other name bound to that same list sees the change too. An operation such as "
        "`L + [99]` or `sorted(L)` does not touch the original; it builds and returns a new "
        "list, so the original is left exactly as it was. The distinction is ownership. Ask "
        "who else references the object before mutating it: if a caller, a cache or another "
        "function still holds it, an in-place edit is a side effect they did not ask for. When "
        "in doubt, make the copy explicit — `L[:]` or `list(L)` — and mutate that."
    ),
    prerequisites=["canonical:variable-binds-to-object"],
    pitfalls=[
        "Mutating a list that the caller still references, so a helper function silently "
        "corrupts the caller's data.",
        "Writing `L = L.append(x)` and ending up with `None`, because append returns None "
        "rather than the list.",
        "Assuming `L + [x]` appended in place; the returned new list is discarded and L is "
        "unchanged.",
    ],
    adapters={
        "network-programming": {
            "framing": (
                "A socket server keeps a list of connected clients. Editing that list in place "
                "while the event loop iterates over it corrupts the loop; the safe pattern is "
                "to iterate over a copy."
            ),
            "application": (
                "Walk the example through the lens of a client monitor. You keep a list of "
                "connected clients and want to log it while new clients keep arriving. If the "
                "logger iterates the same list the server appends to, the loop can see the "
                "list change underneath it. Trace the two operations: append adds one element "
                "to the existing object and returns None, so it is an in-place change; "
                "concatenation with plus builds a brand-new list and leaves the original "
                "untouched. That distinction is the whole lesson. The safe pattern is to "
                "iterate over a snapshot copy, so the loop's view is fixed even while the "
                "live list grows. Read the example twice, once watching what append returns "
                "and once watching the identity of the list before and after a "
                "concatenation; the second list is a different object, which is why "
                "reassigning it never reaches the original."
            ),
            "example_hint": "append to a client list, then iterate over a snapshot copy",
            "assessment_angle": "which call mutates and which returns a new list, and why the "
                "distinction matters when two parts of the server share the client list",
            "day": 3,
            "title": "Client Lists: Append Mutates, Concatenate Returns a New List",
            "code": (
                "# A server keeps a client list that an event loop also reads.\n"
                "clients = ['conn-1', 'conn-2']\n"
                "\n"
                "def handle_new(name, roster):\n"
                "    roster.append(name)      # mutates the object the loop shares\n"
                "\n"
                "handle_new('conn-3', clients)\n"
                "print('roster now:', clients)\n"
                "\n"
                "# Iterating over a copy keeps the loop stable while the list grows.\n"
                "def broadcast(message, roster):\n"
                "    for name in list(roster):        # snapshot, then iterate\n"
                "        print(f'{name} <- {message}')\n"
                "\n"
                "broadcast('hello', clients)\n"
                "\n"
                "# Contrast: concatenation builds a new list and leaves the original alone.\n"
                "bigger = clients + ['conn-4']\n"
                "print('after concat:', clients)"
            ),
            "questions": [
                "Why does iterating over `list(roster)` keep a broadcast loop safe from a list that is still growing?",
                "What does `clients + ['conn-4']` do to `clients`, and what is the value of `bigger`?",
                "Why is `roster = roster.append(name)` a bug rather than an assignment?",
            ],
            "answers": [
                "`list(roster)` takes a snapshot of the current membership, so entries added during the loop do not shift the iteration.",
                "`clients` is unchanged; concatenation returns a new list, so `bigger` has four entries while the roster still has three.",
                "`append` returns None, so the roster name would end up bound to None and the connection list would be lost.",
            ],
            "homework": (
                "Write client_list.py with a module-level `clients` list, accept(name) that appends "
                "and returns nothing, broadcast(message, roster) that iterates over a copy and prints "
                "one line per client, and a dropped(name) function that removes a client by value. "
                "Accept two clients, broadcast once, then call accept inside a loop that also "
                "broadcasts, to show the snapshot keeps the loop stable while the list grows. Print "
                "the final list length and prove concatenation never changed the original by printing "
                "it after building a longer list with `+`. Observable output: broadcast lines, two "
                "length prints, and one line showing the original list after concatenation."
            ),
            "required_patterns": ["append", "list(", "for ", "def ", "print("],
        },
        "etl-pipelines": {
            "framing": (
                "An extract stage accumulates rows in a list before writing them. Mutating in "
                "place is fine while the batch is local, but once a row is handed to the "
                "transform stage it must not be edited underneath it."
            ),
            "application": (
                "Walk the example through the lens of a batch accumulator. An extract stage "
                "collects rows into a list with append, because append mutates in place and "
                "costs nothing on copies, which matters when a batch holds thousands of rows. "
                "Then the stage hands the batch downstream. If it hands over the same list "
                "and a later stage sorts it in place, the extract stage's own view is now "
                "sorted too. Trace the two operations: append mutates the one object; "
                "concatenation builds a new object and returns it. So the hand-off must pass "
                "a copy, not the live accumulator, otherwise the stages share one object and "
                "the order of operations decides what each stage sees. Read the example and "
                "predict which names still point at the original list after the copy is "
                "handed over; that prediction is the skill being trained."
            ),
            "example_hint": "accumulate rows with append, then pass a copy to the next stage",
            "assessment_angle": "when an in-place edit is safe inside one stage and when it "
                "becomes a cross-stage bug",
            "day": 2,
            "title": "Batch Accumulation: Append in Place, Hand Over a Copy",
            "code": (
                "# Extract accumulates rows; transform must not see them change.\n"
                "extracted = []\n"
                "\n"
                "def extract(value):\n"
                "    extracted.append(value)        # local accumulation: in place is fine\n"
                "\n"
                "extract('a')\n"
                "extract('b')\n"
                "print('extracted:', extracted)\n"
                "\n"
                "# A sorted view is a new list: the extraction order survives.\n"
                "view = sorted(extracted, reverse=True)\n"
                "print('sorted view:', view)\n"
                "print('still extracted:', extracted)\n"
                "\n"
                "# Hand the next stage a copy so later edits stay local.\n"
                "def stage_copy(rows):\n"
                "    rows = list(rows)\n"
                "    rows.append('staged')\n"
                "    return rows\n"
                "\n"
                "handed = stage_copy(extracted)\n"
                "print('handed to next stage:', handed)\n"
                "print('extracted untouched:', extracted)"
            ),
            "questions": [
                "Why is `extracted.append(value)` safe here while `sorted(extracted, reverse=True)` never modifies `extracted`?",
                "What does the copy inside stage_copy protect against?",
                "How would you diagnose a transform stage that receives a list and then finds new rows in it mid-run?",
            ],
            "answers": [
                "Appending mutates a list the extract stage owns alone, so there is no second holder to surprise; sorted builds and returns a new list instead of editing.",
                "It stops the transform stage's own appends from being visible to extract, which still holds a reference to the original list.",
                "Print the list identity and contents at the stage boundary and again mid-run; a growing list means both stages share one object.",
            ],
            "homework": (
                "Write batch_accumulate.py with extract_batch(values) that appends each value to a "
                "module-level list and returns the count, sorted_view(rows) that returns a new sorted "
                "list without touching the input, and stage_copy(rows) that copies, appends a marker, "
                "and returns the copy. Extract three values, then prove sorted_view left the batch "
                "alone by printing it before and after. Hand the batch to stage_copy and print both "
                "lists to show the marker appears only in the copy. End by printing 'PASS' only if "
                "the original batch still has exactly three entries. Observable output: seven lines "
                "plus the final check."
            ),
            "required_patterns": ["append", "sorted(", "list(", "def ", "print("],
        },
        "excel-automation": {
            "framing": (
                "A script reads rows from a spreadsheet into a list of records. Fixing a cell "
                "in place is tempting, but the workbook object and the row list then disagree, "
                "and re-saving writes unexpected data."
            ),
            "application": (
                "Walk the example through the lens of a spreadsheet correction pass. You read "
                "rows from a sheet into a list, then fix a column's values, then write the "
                "list back. The question is which list you wrote back. If you concatenated a "
                "header row onto your data, the concatenation produced a new list, so writing "
                "that back is safe; but if you appended the header, you mutated the data list "
                "in place, and any earlier reference to it, such as a cached range, now "
                "includes the header too. Trace the two operations in the example and notice "
                "which one returns a value and which one returns None. The rule to carry "
                "into every report script is: append and sort change the object you already "
                "have, plus and sorted give you a new object, and only the new object is safe "
                "to share with a stage that must not see your edits."
            ),
            "example_hint": "read rows into a list, fix values on a copy, write the copy back",
            "assessment_angle": "why editing the copy before writing back is safer than editing "
                "the list the reader still holds",
            "day": 2,
            "title": "Edit the Copy, Not the Sheet: Append and Copy in Report Scripts",
            "code": (
                "# Rows read from a sheet are shared with the workbook's own view.\n"
                "sheet_rows = [['Jan', '120'], ['Feb', '150']]\n"
                "\n"
                "def append_total(rows):\n"
                "    rows.append(['TOTAL', '270'])      # in place: the sheet view sees it\n"
                "\n"
                "append_total(sheet_rows)\n"
                "print('sheet view:', sheet_rows)\n"
                "\n"
                "# A corrected report is built on a copy, then written back.\n"
                "def build_report(rows):\n"
                "    rows = [list(row) for row in rows]      # copy first\n"
                "    for row in rows:\n"
                "        row[1] = int(row[1])\n"
                "    return rows\n"
                "\n"
                "report = build_report(sheet_rows)\n"
                "print('report values:', report)\n"
                "print('sheet unchanged:', sheet_rows)"
            ),
            "questions": [
                "Why does the sheet view show the TOTAL row after append_total runs?",
                "What does `[list(row) for row in rows]` do before the amounts are converted to integers?",
                "Why should the write-back step receive the report list rather than the original rows?",
            ],
            "answers": [
                "append mutates the one list both the script and the sheet's reader reference, so the new row is visible through either name.",
                "It builds a fresh list of fresh row lists, so the integer conversion lands on the report copy and the sheet rows keep their strings.",
                "Because the report copy is the corrected data; writing the original would persist unconverted values and undo the report's fixes.",
            ],
            "homework": (
                "Write report_copy.py with sheet_rows holding three [month, amount] pairs as strings, "
                "append_total(rows) that adds a TOTAL row in place, and build_report(rows) that "
                "returns a copy with amounts converted to int. Append the total and print the sheet "
                "view; then build the report and print both lists to show the sheet still holds "
                "strings while the report holds integers. Add a final write-back step that prints "
                "only the corrected report list, and a 'PASS' line that appears only when the sheet "
                "rows still contain strings. Observable output: five lines plus the final check."
            ),
            "required_patterns": ["append", "list(", "int(", "def ", "print("],
        },
    },
)


topic(
    "canonical:dict-as-mapping",
    "Dictionaries: lookup by key instead of position",
    sources=[
        {
            "book": "learning-python",
            "chapter": 8,
            "pages": [197, 224],
            "sections": ["Dictionaries in Action", "Basic Dictionary Operations"],
        },
        {
            "book": "learning-python-networking",
            "chapter": 1,
            "pages": [35, 105],
            "sections": ["An introduction to TCP/IP networking", "IP addresses and ports"],
        },
    ],
    concept=(
        "A dictionary maps keys to values. Where a list is fetched by position, a dictionary "
        "is fetched by the key itself, so a lookup becomes `prices['spam']` rather than a scan "
        "through the whole collection. Keys must be immutable and unique; values may be "
        "anything. Because the dictionary is optimised for fast key lookup, it stores items in "
        "whatever internal order suits that lookup, so the iteration order is not the order in "
        "which the pairs were written. Operations that assume a stable left-to-right order, "
        "such as slicing, do not apply. To walk the pairs in a deterministic order, sort the "
        "keys first. The practical payoff is naming: instead of remembering that the third "
        "field of a record is the port, the code says `record['port']`, and the reader no "
        "longer has to count columns."
    ),
    prerequisites=["canonical:mutable-sequence-vs-copy"],
    pitfalls=[
        "Expecting keys to come out in insertion order and writing logic that silently depends "
        "on it.",
        "Using a mutable key such as a list, which Python rejects because the key must be "
        "hashable.",
        "Indexing a dictionary by position, which raises KeyError, or confusing a missing key "
        "with a present one.",
    ],
    adapters={
        "network-programming": {
            "framing": (
                "Network configuration is naturally a mapping: a service name maps to a port, "
                "a host maps to its address. A dictionary turns `socket.connect((host, port))` "
                "into `connect(SERVICES['web'])`, and the port table becomes documentation."
            ),
            "application": (
                "Walk the example through the lens of a service table. You keep a mapping "
                "from service name to host and port, and the code dials by name instead of by "
                "position, so adding a new service does not shift the numbers every other "
                "service relies on. Trace the three operations the example performs: a lookup "
                "by key returns the stored tuple; assigning to an existing key replaces the "
                "value rather than duplicating the key; and looking up a missing key raises "
                "KeyError, which is why the example tests membership first or supplies a "
                "default. Compare that with a list of pairs, where finding a service means "
                "scanning every entry. The mapping is the right structure whenever the code "
                "answers the question 'which one is this?' by name. Keys are unique because "
                "a lookup has to resolve to one answer, and immutable keys are required so a "
                "key cannot be changed after it was filed away."
            ),
            "example_hint": "map service names to (host, port) tuples, then dial by name",
            "assessment_angle": "why a service-to-port mapping is fetched by key rather than "
                "searched by position, and what happens when a requested service is absent",
            "day": 2,
            "title": "Service Tables: Look Up a Destination by Name, Not Position",
            "code": (
                "# A service table documents the port contract at a glance.\n"
                "SERVICES = {\n"
                "    'web': ('example.com', 80),\n"
                "    'secure': ('example.com', 443),\n"
                "    'metrics': ('collector.local', 9090),\n"
                "}\n"
                "\n"
                "def dial(service):\n"
                "    host, port = SERVICES[service]      # fetch by key, not offset\n"
                "    print(f'connecting to {host}:{port}')\n"
                "\n"
                "dial('web')\n"
                "dial('metrics')\n"
                "\n"
                "# A missing service should fail with a message the operator can act on.\n"
                "def dial_safe(service):\n"
                "    entry = SERVICES.get(service)\n"
                "    if entry is None:\n"
                "        print(f'unknown service: {service}')\n"
                "        return False\n"
                "    host, port = entry\n"
                "    print(f'connecting to {host}:{port}')\n"
                "    return True\n"
                "\n"
                "dial_safe('ftp')\n"
                "\n"
                "# Deterministic iteration needs sorted keys.\n"
                "for name in sorted(SERVICES):\n"
                "    print(name, SERVICES[name][1])"
            ),
            "questions": [
                "Why does `SERVICES['web']` find the destination without scanning the whole table?",
                "What happens with `SERVICES['ftp']`, and why is `SERVICES.get('ftp')` safer for a script that runs unattended?",
                "Why is `sorted(SERVICES)` used when printing the table, and what cannot be done to a dictionary that a list allows?",
            ],
            "answers": [
                "A dictionary is indexed by key and uses hashing internally, so the lookup goes straight to the entry instead of walking the collection.",
                "Indexing a missing key raises KeyError and stops the script; `.get()` returns None, so the code can report the unknown service and continue.",
                "Keys are stored in whatever order suits the hash table, so sorting gives a stable, repeatable listing; position-based operations like slicing do not apply to dictionaries.",
            ],
            "homework": (
                "Write service_table.py with a SERVICES mapping of at least four service names to "
                "(host, port) tuples. Implement dial(service) that unpacks the entry and prints the "
                "destination, dial_safe(service) that reports an unknown service without crashing, and "
                "list_services() that prints every name and port in sorted order. Call dial and "
                "dial_safe on a known service and an unknown one, then print the sorted table. Add a "
                "line printing 'PASS' only if every known service resolves and the unknown one is "
                "reported rather than raised. Observable output: five connection or report lines, the "
                "sorted listing, and the final check."
            ),
            "required_patterns": ["dict", ".get(", "sorted(", "for ", "print("],
        },
        "etl-pipelines": {
            "framing": (
                "A transformed row is easier to handle as a mapping from column name to value "
                "than as a positional tuple. Downstream code references `row['amount']` by "
                "name, so a schema change in an upstream column does not silently shift every "
                "index."
            ),
            "application": (
                "Walk the example through the lens of a row-to-record conversion. A flat CSV "
                "row is positional, so column four is only meaningful if you remember what "
                "column four was. Zipping the header row with a data row produces a dict "
                "keyed by column name, and from then on the code asks for 'customer_id' "
                "instead of index three. Trace what that buys the pipeline: a missing column "
                "can be reported by name in the error message; a column reorder in the source "
                "file does not silently shift every index; and routing decisions read as "
                "sentences rather than offsets. Trace also what it costs: the header must be "
                "trusted, so the example validates that every expected key is present before "
                "the row is used. When the example looks up a key that is absent, note that "
                "the failure is loud rather than a wrong value, which is exactly the property "
                "an extract stage wants from its records."
            ),
            "example_hint": "zip a header row with a data row into a dict, then route by column name",
            "assessment_angle": "how a named mapping protects the pipeline when the source adds "
                "or reorders a column",
            "day": 3,
            "title": "Named Records: Zip a Header with a Row to Look Fields Up by Name",
            "code": (
                "# Pairing a header with a row turns positions into names.\n"
                "header = ['id', 'region', 'amount']\n"
                "row = ['7', 'north', '12.5']\n"
                "\n"
                "record = dict(zip(header, row))\n"
                "print('amount by name:', record['amount'])\n"
                "print('whole record:', record)\n"
                "\n"
                "# Inserting a column changes nothing downstream.\n"
                "header2 = ['id', 'region', 'currency', 'amount']\n"
                "row2 = ['8', 'south', 'EUR', '20.0']\n"
                "record2 = dict(zip(header2, row2))\n"
                "print('amount still named:', record2['amount'])\n"
                "\n"
                "# Missing fields are reported, not silently wrong.\n"
                "def amount_of(rec):\n"
                "    value = rec.get('amount')\n"
                "    if value is None:\n"
                "        print('missing amount field')\n"
                "        return None\n"
                "    return float(value)\n"
                "\n"
                "print(amount_of(record))\n"
                "print(amount_of({'id': '9'}))"
            ),
            "questions": [
                "How does `dict(zip(header, row))` protect the pipeline when the source inserts a column?",
                "Why is `record['amount']` safer than `row[2]` after an upstream schema change?",
                "What does `amount_of` do when the amount field is absent, and why is that preferable to a positional lookup?",
            ],
            "answers": [
                "The pairing keys each value by its column name, so a new or moved column is fetched by name and the code never relies on a fixed position.",
                "A named lookup either finds the field or fails at that exact key, while a positional index silently returns whatever value now sits at index 2.",
                "It reports the missing field and returns None instead of returning the wrong column's value, so a schema drift becomes a visible error rather than corrupt data.",
            ],
            "homework": (
                "Write named_records.py with a header list, three data rows, and to_records(header, "
                "rows) that returns a list of dicts built with dict(zip(...)). Add amount_of(record) "
                "that returns the amount as a float or reports a missing field, and "
                "total_by_name(records) that sums the amounts of the named field. Convert all three "
                "rows, then deliberately feed a row whose header lacks 'amount' and show the missing "
                "field is reported. Print the named total. Observable output: the record listings, "
                "one missing-field report, and the total."
            ),
            "required_patterns": ["zip(", "dict(", "float(", "def ", "print("],
        },
        "excel-automation": {
            "framing": (
                "A spreadsheet row paired with its header becomes a dictionary keyed by column "
                "name. Cell lookups then read `row['Total']` instead of `row[5]`, so inserting "
                "a column no longer breaks every formula in the script."
            ),
            "application": (
                "Walk the example through the lens of cell lookup. A worksheet is a grid of "
                "columns and rows, and reading a cell by its column name instead of its "
                "column number is what makes a script survive a report redesign. The example "
                "pairs a header row with a data row to build a dict, then reads a named cell "
                "from it. Trace the three operations: lookup by name returns the cell's "
                "value; a repeated column name keeps only the last value, which is why "
                "duplicate headers must be detected and reported; and a missing name raises "
                "KeyError rather than returning an empty cell silently. Compare with "
                "index-based access, where inserting one column before the ones you need "
                "silently shifts every number. When a script must be rerun next month on a "
                "similar sheet, name-based lookup is what keeps it working, and the header "
                "check is what makes a mismatch fail loudly instead of producing a subtly "
                "wrong report."
            ),
            "example_hint": "pair a header row with each data row into a dict and look cells up by name",
            "assessment_angle": "why keying a record by column name survives a spreadsheet edit "
                "that a positional index would not",
            "day": 3,
            "title": "Header-Paired Rows: Read a Cell by Column Name",
            "code": (
                "# A sheet is read as a header plus rows; names replace column numbers.\n"
                "header = ['Month', 'Region', 'Total']\n"
                "rows = [\n"
                "    ['Jan', 'north', '120'],\n"
                "    ['Feb', 'south', '150'],\n"
                "]\n"
                "\n"
                "def to_records(head, data):\n"
                "    return [dict(zip(head, row)) for row in data]\n"
                "\n"
                "records = to_records(header, rows)\n"
                "print('first total by name:', records[0]['Total'])\n"
                "\n"
                "# Inserting a column before Total changes nothing.\n"
                "header2 = ['Month', 'Region', 'Owner', 'Total']\n"
                "rows2 = [['Mar', 'east', 'ana', '210']]\n"
                "rec2 = to_records(header2, rows2)[0]\n"
                "print('total still named:', rec2['Total'])\n"
                "\n"
                "# A renamed heading is caught at read time.\n"
                "def total_of(rec):\n"
                "    value = rec.get('Total')\n"
                "    if value is None:\n"
                "        print('heading Total not found')\n"
                "        return 0\n"
                "    return int(value)\n"
                "\n"
                "print(total_of(rec2))\n"
                "print(total_of({'Month': 'Apr'}))"
            ),
            "questions": [
                "Why does reading `records[0]['Total']` survive the insertion of an Owner column?",
                "What would `rows[0][2]` return after that insertion, and why is that fragile?",
                "How does total_of turn a renamed heading into a caught problem?",
            ],
            "answers": [
                "The value is fetched by column name, so its position in the row is irrelevant once the header and row are paired.",
                "It would return 'north' — the region — because every value after the insertion shifted left, and the script would keep using it as if it were the total.",
                "It uses `.get('Total')`, so a missing heading yields None, the function prints a clear message, and the script stops instead of computing on a wrong value.",
            ],
            "homework": (
                "Write header_rows.py with a header of at least three columns, four data rows, "
                "to_records(head, data) returning dicts built with zip, and total_of(record) that "
                "returns the Total as an int or reports a missing heading. Convert all rows and print "
                "each record's total by name. Then simulate an inserted column by rebuilding the "
                "header and rows with an extra field before Total, convert again, and print the "
                "totals to show they still resolve by name. Finish with one call whose record lacks "
                "the heading, and print 'PASS' only when that case reports the missing heading. "
                "Observable output: eight total lines plus the report and the final check."
            ),
            "required_patterns": ["zip(", "dict(", "int(", "def ", "print("],
        },
    },
)


topic(
    "canonical:protocol-as-contract",
    "Protocols: the contract two programs agree to obey",
    sources=[
        {
            "book": "learning-python-networking",
            "chapter": 1,
            "pages": [35, 105],
            "sections": [
                "An introduction to TCP/IP networking",
                "Protocol concepts and the problems that protocols solve",
                "IP addresses and ports",
            ],
        },
    ],
    concept=(
        "Two programs on different machines cannot share memory, so they must agree on the "
        "shape of every message before either one is written. That agreement is a protocol: "
        "which end speaks first, what fields appear in what order, what each field means, and "
        "what happens when a field is missing. TCP gives reliable, ordered delivery, so a "
        "protocol built on it may assume bytes arrive in the order they were sent; UDP does "
        "not promise that, so a protocol built on UDP must number or timestamp its messages "
        "itself. Addresses and ports are the part of the contract that names the participants: "
        "an address identifies a machine, a port identifies the service on that machine. The "
        "discipline is to make the contract explicit in code — a fixed header the reader can "
        "see — rather than leaving it implicit in the order of two send calls."
    ),
    prerequisites=["canonical:dict-as-mapping"],
    pitfalls=[
        "Sending two messages with two separate send calls and assuming the receiver reads them "
        "as two separate messages, when TCP may merge them into one delivery.",
        "Designing a protocol around UDP and then depending on order or delivery.",
        "Leaving the message format implicit, so the sender and reader disagree about which "
        "field comes first.",
    ],
    coverage="partial",
    gap_note=(
        "The corpus covers protocol concepts at the introductory level (LPN ch. 1). "
        "Message-framing algorithms — length prefixes and delimiters that solve the "
        "TCP stream-merging problem — are described only in passing; deep framing and "
        "concurrency details are not in the local books and must be supplemented from "
        "elsewhere before an advanced lesson."
    ),
    adapters={
        "network-programming": {
            "framing": (
                "A client and server exchange a fixed header of fields. The sender builds the "
                "header, the receiver parses it, and both sides read the same contract."
            ),
            "application": (
                "Walk the example through the lens of two programs that must agree before "
                "they exchange a byte. The sender names every field it puts on the wire and "
                "the reader names every field it expects, so a missing or renamed field is "
                "caught at the boundary instead of silently corrupting a later computation. "
                "Trace the exchange: one side builds a message as named fields, the other "
                "side reads each field by name and checks that the expected set is present, "
                "and only then does either side act on the content. The discipline is that "
                "the field list is decided once, in one place, and both ends refer to it. "
                "What the corpus does not supply is the framing algorithm itself, how the "
                "reader knows where one message ends and the next begins, because that "
                "belongs to a transport chapter rather than the introductory networking "
                "chapter this topic is drawn from; treat that as the next topic to source, "
                "not as something to guess at."
            ),
            "example_hint": "define a header of named fields, send it, then parse it on the other end",
            "assessment_angle": "what TCP does and does not promise, and why an explicit header "
                "is safer than relying on the order of send calls",
            "day": 4,
            "title": "Explicit Message Contracts: Name Every Field You Send",
            "code": (
                "# A contract stated in code is a contract both sides can read.\n"
                "def build_header(service, length):\n"
                "    return {\n"
                "        'service': service,\n"
                "        'length': length,\n"
                "    }\n"
                "\n"
                "header = build_header('web', 4)\n"
                "wire = f\"{header['service']}:{header['length']};\"\n"
                "print('sent:', wire)\n"
                "\n"
                "# The receiver parses according to the same agreed shape.\n"
                "def parse_header(text):\n"
                "    body, _, _ = text.partition(';')\n"
                "    service, _, length = body.partition(':')\n"
                "    return build_header(service, int(length))\n"
                "\n"
                "print('parsed:', parse_header(wire))\n"
                "\n"
                "# Two send calls may arrive as one delivery on TCP.\n"
                "merged = build_header('web', 2)\n"
                "merged2 = build_header('metrics', 3)\n"
                "stream = f\"{merged['service']}:{merged['length']};{merged2['service']}:{merged2['length']};\"\n"
                "print('one delivery, two messages:', stream)"
            ),
            "questions": [
                "Why can two separate send calls arrive as a single read on the receiving end?",
                "What does the trailing ';' contribute to the contract between the two sides?",
                "What does TCP guarantee that UDP does not, and what must a UDP-based protocol then do itself?",
            ],
            "answers": [
                "TCP is a byte stream, so the receiver sees one ordered stream of bytes and the boundary between the two messages is not preserved automatically.",
                "It marks the end of the first message, so the receiver can split the stream back into the two headers the sender intended.",
                "TCP promises ordered, reliable delivery, so the protocol may rely on order; UDP does not, so a UDP protocol must number or timestamp its messages itself.",
            ],
            "homework": (
                "Write message_contract.py with build_header(service, length) returning a dict, "
                "serialize(header) producing one 'service:length;' string, and parse_stream(text) "
                "that splits a stream on ';' and returns a list of parsed headers, ignoring any "
                "empty final field. Serialize three headers, concatenate them into one stream to "
                "simulate TCP merging, then parse the stream and print each recovered header to "
                "prove the delimiters restored the original messages. Add a check that prints "
                "'PASS' only when exactly three headers are recovered and their lengths match what "
                "was sent. Observable output: the serialized stream, the three recovered headers, "
                "and the final check."
            ),
            "required_patterns": ["partition(", "split(", "int(", "def ", "print("],
        },
        "etl-pipelines": {
            "framing": (
                "A pipeline is a contract between stages too: the extract stage promises fields, "
                "the transform stage consumes them. Writing that contract down as a schema makes "
                "a broken upstream change loud rather than silent."
            ),
            "application": (
                "Walk the example through the lens of a stage boundary. Each stage declares "
                "the fields it requires from a row, and every row arriving is checked against "
                "that declaration before it is transformed. Trace what changes when the "
                "declaration is explicit: a column dropped by an upstream source fails at the "
                "check, with the field name in the message, instead of surfacing later as an "
                "index error or a silent None; a column renamed by a vendor fails the same "
                "way; and a new column added upstream is ignored rather than quietly shifting "
                "downstream offsets. The contract is a list of names that both the producer "
                "and the consumer can read, and it is worth writing before any transform "
                "code, because it forces the pipeline's assumptions out into the open. Note "
                "the gap honestly: the corpus's introductory networking chapter motivates this "
                "discipline but does not describe schema-evolution practice, so keep the "
                "check simple and add to it as real mismatches appear."
            ),
            "example_hint": "declare the expected fields once and validate each extracted row against them",
            "assessment_angle": "how a written field contract turns an upstream schema drift into "
                "a caught error instead of corrupt output",
            "day": 4,
            "title": "Stage Contracts: Declare the Fields, Validate Every Row",
            "code": (
                "# The contract between extract and transform, written down once.\n"
                "REQUIRED = ['id', 'region', 'amount']\n"
                "\n"
                "def validate(row):\n"
                "    missing = [field for field in REQUIRED if field not in row]\n"
                "    if missing:\n"
                "        print(f'rejected: missing {missing}')\n"
                "        return False\n"
                "    return True\n"
                "\n"
                "good = {'id': '7', 'region': 'north', 'amount': '12.5'}\n"
                "bad = {'id': '8', 'region': 'south'}\n"
                "print(validate(good))\n"
                "print(validate(bad))\n"
                "\n"
                "# An upstream rename becomes a loud failure instead of a silent one.\n"
                "renamed = {'id': '9', 'area': 'east', 'amount': '3.0'}\n"
                "print(validate(renamed))\n"
                "\n"
                "# A contract version lets both stages coordinate a change.\n"
                "print('schema version:', '1.1')"
            ),
            "questions": [
                "Why does declaring REQUIRED turn an upstream rename into a caught error?",
                "What would happen without validation if the source renamed 'region' to 'area'?",
                "Why is a schema version useful to both stages of a pipeline?"
            ],
            "answers": [
                "Validation checks every row for the named fields, so a renamed column fails the check and is reported instead of being processed as if nothing changed.",
                "The transform stage would either key on a missing field and crash, or silently produce records whose region is empty, passing corrupt data downstream.",
                "It lets extract and transform agree on which field set is in force, so a planned change is made on both sides instead of surprising one of them.",
            ],
            "homework": (
                "Write stage_contract.py with a REQUIRED list of three fields, validate(row) that "
                "prints the missing fields and returns False for a bad row, and validate_all(rows) "
                "that returns a list of accepted rows plus a count of rejections. Build five rows "
                "including one missing 'amount' and one with a renamed field, run validate_all, and "
                "print the accepted rows and the rejection count. Add a schema_version constant and "
                "print it so both stages can coordinate. Finish with a 'PASS' line that appears only "
                "when exactly three rows are accepted and two are rejected. Observable output: the "
                "rejection reports, the accepted rows, the version, and the final check."
            ),
            "required_patterns": ["for ", "in ", "def ", "return ", "print("],
        },
        "excel-automation": {
            "framing": (
                "A report generator is a small contract: the sheet promises columns, the "
                "formatter consumes them. Stating the contract up front keeps the report working "
                "when someone renames a column."
            ),
            "application": (
                "Walk the example through the lens of a report that must not silently produce "
                "wrong numbers. The script lists the columns it depends on and checks the "
                "sheet has them before it formats anything, so a renamed or deleted column "
                "stops the run at the check with the column name in the message. Trace the "
                "difference without the check: the script reads a column by index, the report "
                "template moves a column, and the totals row is computed from the wrong "
                "column with no error at all. Trace it with the check: the run fails early, "
                "names the missing column, and a human fixes the sheet. The contract is "
                "small, a list of column names the report needs, and it belongs at the top of "
                "the script where it can be read in one glance. The corpus's introductory "
                "networking chapter supplies the motivating idea, naming what each side "
                "expects, but not spreadsheet-specific practice, so the check here is "
                "deliberately minimal."
            ),
            "example_hint": "list the columns the report depends on and check the sheet has them before formatting",
            "assessment_angle": "why naming the columns a script depends on catches a renamed "
                "heading at read time instead of at reporting time",
            "day": 4,
            "title": "Report Contracts: Check the Columns Before You Format",
            "code": (
                "# The report depends on named columns; say so before touching data.\n"
                "NEEDED = ['Month', 'Region', 'Total']\n"
                "\n"
                "def check_sheet(header):\n"
                "    missing = [name for name in NEEDED if name not in header]\n"
                "    if missing:\n"
                "        print(f'report blocked: missing {missing}')\n"
                "        return False\n"
                "    return True\n"
                "\n"
                "print(check_sheet(['Month', 'Region', 'Total', 'Owner']))\n"
                "print(check_sheet(['Month', 'Area', 'Total']))\n"
                "\n"
                "# Formatting only runs when the contract holds.\n"
                "def format_row(header, row):\n"
                "    if not check_sheet(header):\n"
                "        return None\n"
                "    record = dict(zip(header, row))\n"
                "    return f\"{record['Month']} in {record['Region']}: {record['Total']}\"\n"
                "\n"
                "print(format_row(['Month', 'Region', 'Total'], ['Jan', 'north', '120']))\n"
                "print(format_row(['Month', 'Area', 'Total'], ['Feb', 'south', '150']))"
            ),
            "questions": [
                "Why is a missing column reported before formatting rather than during it?",
                "What does `dict(zip(header, row))` add once the contract check has passed?",
                "Give one real-world spreadsheet event that a written column contract would catch.",
            ],
            "answers": [
                "The check runs once against the header, so the script stops before doing work it would have to discard, and the message names exactly what is missing.",
                "It lets the formatter read each cell by column name, so the output code does not depend on where a column happens to sit.",
                "A colleague renames 'Total' to 'Amount', or inserts a column before it; the contract check reports the missing heading instead of the report silently using the wrong column.",
            ],
            "homework": (
                "Write report_contract.py with a NEEDED list of three headings, check_sheet(header) "
                "that reports missing headings and returns a boolean, and format_rows(header, rows) "
                "that returns formatted strings only when the sheet passes the check. Use one header "
                "that satisfies the contract and one that has a renamed heading, and format both to "
                "show the second is blocked. Print a line for each formatted row, then print 'PASS' "
                "only when the good sheet yields the expected number of formatted rows and the "
                "renamed sheet yields none. Observable output: the blocking report, the formatted "
                "rows, and the final check."
            ),
            "required_patterns": ["for ", "in ", "zip(", "def ", "print("],
        },
    },
)


def _load_batches() -> None:
    """Import topic-batch modules so their `topic()` calls register here.

    Every module named `topics_*.py` in this directory is a batch and is loaded
    in sorted order. Each one imports `topic` from this module and calls it at
    import time, so importing this module is enough to load every batch.
    """
    import importlib
    import pkgutil

    for info in sorted(pkgutil.iter_modules([str(Path(__file__).resolve().parent)]),
                       key=lambda m: m.name):
        if info.name.startswith("topics_"):
            try:
                importlib.import_module(info.name)
            except Exception as exc:  # a broken batch must not kill the library
                print(f"[canonical_topics] warning: could not load {info.name}: {exc}",
                      file=sys.stderr)


_load_batches()


def all_topics() -> dict[str, dict]:
    return dict(CANONICAL_TOPICS)


def by_id(topic_id: str) -> dict:
    if topic_id not in CANONICAL_TOPICS:
        raise KeyError(f"unknown canonical topic: {topic_id}")
    return CANONICAL_TOPICS[topic_id]


if __name__ == "__main__":
    from source_index import chapter_range, provenance_line

    print(f"{len(CANONICAL_TOPICS)} canonical topics\n")
    for record in CANONICAL_TOPICS.values():
        print(f"## {record['name']}  [{record['coverage']}]")
        for src in record["sources"]:
            first, last = chapter_range(src["book"], src["chapter"])
            print(f"    {provenance_line(src)}  (chapter spans pp. {first}–{last})")
        for slug, ad in record["adapters"].items():
            print(f"    -> {slug} (day {ad['day']})")
        if record["gap_note"]:
            print(f"    GAP: {record['gap_note']}")
        print()
