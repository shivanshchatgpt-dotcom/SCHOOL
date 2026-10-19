"""Excel Automation phase 1, days 75-89: rows, columns and cells.

Every example is stdlib-only, offline and deterministic: workbooks, sheets,
rows, cells and formats are plain dicts and lists. No workbook is opened and
nothing is written to disk, so the applier can execute each example and get the
same output on every run.
"""

PHASE = (
    "Rows, Columns and Cells",
    "Model workbooks, sheets, rows and cells as plain Python data so everyday Excel work can be automated and tested offline.",
    {
        75: dict(
            topic="Orientation: what Excel automation is",
            idea=(
                "Excel automation means writing code that performs the work a person would otherwise do by clicking: "
                "opening a workbook, finding a sheet, reading values, changing a few cells and saving the result. The "
                "point of orientation is to see that the spreadsheet application is only one client of the data, and "
                "that the data itself has a simple shape. A workbook holds sheets, a sheet holds rows, a row holds "
                "cells, and a cell holds a value with a type and often a format. If you can model those four levels in "
                "plain Python, you can reason about an automation before touching a library, and you can test the logic "
                "without Excel installed. Today's example represents a workbook as a dictionary of sheet names to lists "
                "of rows and prints a short description of each sheet. That model is deliberately incomplete: it has no "
                "formulas, styles or merged cells yet, because the first lesson is structural rather than "
                "feature-complete. Keep asking where each piece of information lives, and notice how much of the work "
                "is simply moving data between representations. Automation is not magic and it is not a macro recorder; "
                "it is ordinary code over ordinary values. Everything later in this phase adds capability to this same "
                "model, so time spent making the hierarchy obvious now pays off repeatedly."
            ),
            code=(
                'WORKBOOK = {\n'
                '    "Sales": [\n'
                '        ["region", "units"],\n'
                '        ["north", "12"],\n'
                '        ["south", "7"],\n'
                '    ],\n'
                '    "Inventory": [\n'
                '        ["item", "qty"],\n'
                '        ["widget", "40"],\n'
                '    ],\n'
                '}\n'
                '\n'
                'def describe(workbook):\n'
                '    for name in sorted(workbook):\n'
                '        header, *rows = workbook[name]\n'
                '        print(f"{name}: {len(header)} columns, {len(rows)} data rows")\n'
                '    return len(workbook)\n'
                '\n'
                'print("sheets:", describe(WORKBOOK))\n'
                'assert describe(WORKBOOK) == 2\n'
                'print("automation is code over data, not clicks")'
            ),
            variant_b="add a third sheet named Timesheet with four data rows and describe all three",
            variant_c="make describe return a list of (sheet, columns, rows) tuples instead of printing",
            mistakes=[
                "Starting with a library call before deciding what the data structure should be.",
                "Treating a workbook as one flat table and losing track of which sheet a row came from.",
                "Assuming automation must open Excel when plain Python can model the same data first.",
            ],
            q1=(
                "What are the four levels of the workbook model used in this phase?",
                "Workbook, sheet, row and cell, with a value in each cell and a header usually naming the columns.",
            ),
            homework=(
                "Write `describe_workbook(workbook)` that takes a dict of sheet names to rows, prints one line per "
                "sheet with its column count and data-row count, and returns the number of sheets. Build a "
                "two-sheet workbook, call it, print the return value, and comment which line splits header from rows."
            ),
            patterns=["def describe_workbook", "for ", "print("],
            mapping=(
                "openpyxl gives you a workbook object with named worksheets and cell values; this dict model is the "
                "same hierarchy with the file format removed."
            ),
        ),
        76: dict(
            topic="The workbook, sheet and cell model",
            idea=(
                "The workbook model is a nested structure, and naming each level precisely removes most confusion. A "
                "workbook is a collection of sheets; a sheet is a sequence of rows; a row is a sequence of cells. In "
                "code we usually attach the header to the sheet and address data rows by position, while a cell's "
                "meaning comes from combining its row with the column name in the header. It helps to distinguish a "
                "cell's coordinates from its content: `B2` is a location, forty is the value, and the header in "
                "column B is what tells you forty means quantity. Automation bugs often come from mixing those three "
                "ideas, for example treating a row number as a column name or assuming every sheet starts at A1. "
                "Today's example implements one small accessor that takes a sheet name, row index and column index "
                "and returns the cell value, plus a descriptor that reports where that value came from. Keeping the "
                "lookup in one function means later features, such as bounds checks or blank handling, have a single "
                "place to live. Notice that a sheet is not the workbook and a cell is not its address; keeping those "
                "concepts separate is what makes the following days straightforward."
            ),
            code=(
                'WORKBOOK = {\n'
                '    "Sales": [\n'
                '        ["region", "units"],\n'
                '        ["north", "12"],\n'
                '        ["south", "7"],\n'
                '    ],\n'
                '}\n'
                '\n'
                'def cell(workbook, sheet, row, column):\n'
                '    return workbook[sheet][row][column]\n'
                '\n'
                'def describe(workbook, sheet, row, column):\n'
                '    value = cell(workbook, sheet, row, column)\n'
                '    return {"sheet": sheet, "row": row, "column": column, "value": value}\n'
                '\n'
                'print(describe(WORKBOOK, "Sales", 1, 0))\n'
                'print(describe(WORKBOOK, "Sales", 2, 1))\n'
                'assert cell(WORKBOOK, "Sales", 1, 1) == "12"\n'
                'print("workbook -> sheet -> row -> cell")'
            ),
            variant_b="describe a cell in the Inventory sheet and include the header name for its column",
            variant_c="return a list of every cell descriptor for one row instead of a single cell",
            mistakes=[
                "Confusing a cell's address with its value, so `B2` and forty are treated as the same thing.",
                "Forgetting that row zero is the header when looking up data by position.",
                "Assuming every sheet begins at A1 and ignoring the real origin of a table.",
            ],
            q1=(
                "Why separate a cell's address from its value in the model?",
                "The address says where to look while the value is the data; keeping them distinct prevents layout changes from corrupting logic.",
            ),
            homework=(
                "Write `row_cells(workbook, sheet, row)` that returns a list of dicts with column, header and value "
                "for every cell in one row. Run it on a data row of a two-column sheet, print each dict, and comment "
                "which lookup supplies the header name."
            ),
            patterns=["def row_cells", "header", "print("],
            mapping=(
                "In openpyxl a worksheet is reached by name and a cell by `ws.cell(row=, column=)`; the nesting here "
                "mirrors `workbook[sheet][row][column]`."
            ),
        ),
        77: dict(
            topic="Sheets as lists of rows",
            idea=(
                "Once the header is separated, a sheet becomes a list of rows, and that is the representation most "
                "automation actually needs. Iterating a list of rows is simple, predictable and fast, and it matches "
                "what a CSV reader yields and what openpyxl produces when you ask for values only. The first habit "
                "is to split the header from the data once, with `header, *rows = sheet`, rather than re-checking "
                "row zero inside every loop. The second is to keep row numbers meaningful for humans: enumerate with "
                "a start offset so messages refer to the spreadsheet row a person would see, not the zero-based list "
                "index. A third is to avoid modifying the list while iterating it; build a new list instead, because "
                "removing rows during a loop skips entries. Today's example walks a timesheet, prints each row with "
                "its visible row number, and sums the hours column. The sum is computed with `header.index` so the "
                "code keeps working if a column is inserted later. That combination of a stable row loop, human "
                "numbering and name-based column lookup is the basic grammar of every sheet transformation in this "
                "phase. It is also the version of the data you can print and inspect without a spreadsheet."
            ),
            code=(
                'SHEET = [\n'
                '    ["day", "hours"],\n'
                '    ["mon", "8"],\n'
                '    ["tue", "7.5"],\n'
                '    ["wed", "8"],\n'
                ']\n'
                '\n'
                'header, *rows = SHEET\n'
                'print("header:", header)\n'
                'for index, row in enumerate(rows, start=2):\n'
                '    print(f"row {index}: {row}")\n'
                '\n'
                'hours = header.index("hours")\n'
                'total = sum(float(row[hours]) for row in rows)\n'
                'print("rows:", len(rows), "hours:", total)\n'
                'assert len(rows) == 3 and total == 23.5\n'
                'print("a sheet is a header plus a list of rows")'
            ),
            variant_b="add a Thursday row and print the new total without changing the summing logic",
            variant_c="skip rows whose hours are blank and print how many rows were used",
            mistakes=[
                "Re-checking the header inside every iteration instead of splitting it once.",
                "Reporting zero-based indexes to users who count spreadsheet rows from one.",
                "Removing rows from the list while looping over it, which skips the next row.",
            ],
            q1=(
                "Why use `header, *rows = sheet` before looping?",
                "It separates layout from data once, so the loop body deals only with data rows and cannot accidentally treat the header as a record.",
            ),
            homework=(
                "Write `hours_total(sheet)` that splits the header from the rows, finds the hours column by name, "
                "skips blank values, and returns the total plus the count of rows used. Run it on a timesheet with "
                "one blank row, print both results, and comment how the header is separated."
            ),
            patterns=["def hours_total", "*rows", "print("],
            mapping=(
                "openpyxl's `iter_rows(values_only=True)` yields exactly these row lists, so the same loop works after "
                "reading a real worksheet."
            ),
        ),
        78: dict(
            topic="Rows as dicts keyed by header",
            idea=(
                "Rows as lists are compact but brittle to read, because every access depends on remembering a column "
                "position. Turning a row into a dict keyed by the header solves that: `record[\"units\"]` stays "
                "correct when columns move, and the code reads like the table it processes. The conversion is one "
                "line with `zip`, and it should happen near the boundary where data enters your logic. After that "
                "point, functions accept records rather than rows, which makes them easier to test and easier to "
                "reuse across sheets with different layouts. There is a trade-off to notice: duplicate header names "
                "collapse in a dict, and a row shorter than the header silently loses keys. Later days add checks for "
                "both, but today's job is the conversion itself. Today's example reads a small sales sheet into "
                "records, prints selected fields by name, and shows one whole record. The important habit is to "
                "convert once at the edge rather than converting inside every calculation, because repeated "
                "conversion hides bugs and wastes effort. Once records exist, the rest of your program no longer "
                "needs to know which column number held what. That is the whole payoff of records, and it compounds as the program grows."
            ),
            code=(
                'SHEET = [\n'
                '    ["region", "units", "price"],\n'
                '    ["north", "12", "2.50"],\n'
                '    ["south", "7", "4.00"],\n'
                ']\n'
                '\n'
                'def to_record(header, row):\n'
                '    return dict(zip(header, row))\n'
                '\n'
                'header, *rows = SHEET\n'
                'records = [to_record(header, row) for row in rows]\n'
                'for record in records:\n'
                '    print(record["region"], record["units"])\n'
                '\n'
                'print(records[0])\n'
                'assert records[1]["price"] == "4.00"\n'
                'print("a row dict is keyed by header")'
            ),
            variant_b="add a `city` column to the header and rows, then print it from each record",
            variant_c="print only records whose units convert to a number above ten",
            mistakes=[
                "Converting the header row into a record along with the data rows.",
                "Using `zip` without checking that the row and header have the same length.",
                "Repeating the header-to-dict conversion inside every calculation instead of once at the edge.",
            ],
            q1=(
                "What breaks when a row is shorter than its header?",
                "`zip` stops at the shorter sequence, so the record silently lacks the trailing keys instead of raising an error.",
            ),
            homework=(
                "Write `to_records(sheet)` that separates the header and returns one dict per data row using `zip`. "
                "Build a three-column, two-row sheet, print each record, and comment which line guarantees the header "
                "is not itself returned as a record."
            ),
            patterns=["def to_records", "zip(", "print("],
            mapping=(
                "pandas frames and `csv.DictReader` both expose header-keyed records; this helper is the hand-built "
                "equivalent before either dependency is involved."
            ),
        ),
        79: dict(
            topic="Addressing a cell by name",
            idea=(
                "Spreadsheet addresses such as `B2` combine a column letter and a row number, and parsing them is a "
                "small but revealing exercise. Column letters are base-26 with no zero digit: A is one, Z is "
                "twenty-six, AA is twenty-seven. Row numbers are one-based, which means converting to a Python index "
                "always subtracts one. Writing the parser yourself makes clear why libraries expose both coordinate "
                "styles and why off-by-one errors are so common at this boundary. The parser should be strict about "
                "the two parts: letters then digits, nothing else, and a row number of at least one. Mixing case, "
                "such as a lowercase `b2`, is harmless if you uppercase before converting. Today's example implements "
                "`split_address`, `column_number` and `read`, then reads two cells from an inventory sheet. The "
                "separation matters: splitting is about syntax, the column conversion is about base-26, and reading "
                "is about indexing. Each is easy to test alone, and later you can add support for absolute markers "
                "or sheet prefixes without rewriting the other parts. Keep the address string as the user's view; "
                "convert it once at the boundary. Later, sheet-qualified addresses such as Sales!B2 simply split the sheet name off first, leaving the same core parser."
            ),
            code=(
                'SHEET = [\n'
                '    ["item", "qty"],\n'
                '    ["widget", "40"],\n'
                '    ["gizmo", "5"],\n'
                ']\n'
                '\n'
                'def split_address(address):\n'
                '    letters = "".join(ch for ch in address if ch.isalpha())\n'
                '    digits = "".join(ch for ch in address if ch.isdigit())\n'
                '    return letters, int(digits)\n'
                '\n'
                'def column_number(letters):\n'
                '    number = 0\n'
                '    for ch in letters.upper():\n'
                '        number = number * 26 + (ord(ch) - ord("A") + 1)\n'
                '    return number\n'
                '\n'
                'def read(sheet, address):\n'
                '    letters, row = split_address(address)\n'
                '    return sheet[row - 1][column_number(letters) - 1]\n'
                '\n'
                'print(split_address("B2"))\n'
                'print(read(SHEET, "B2"))\n'
                'assert read(SHEET, "B2") == "40"\n'
                'print("A1 addresses map to row and column indexes")'
            ),
            variant_b="read cell A3 and C1, and confirm what a column beyond the header should do",
            variant_c="add an `address_of(row, column)` function that converts indexes back to A1 notation",
            mistakes=[
                "Forgetting that rows are one-based, so B2 is read from index zero instead of one.",
                "Treating column letters as ASCII values, which breaks after Z and at AA.",
                "Accepting any mix of characters instead of validating letters followed by digits.",
            ],
            q1=(
                "Why does column AA map to 27 rather than 26 or 28?",
                "Columns use base-26 without a zero digit: A is 1, Z is 26, so AA is 26 * 1 + 1, which is 27.",
            ),
            homework=(
                "Write `read_cell(sheet, address)` that parses letters and digits, converts the column with base-26, "
                "and returns the cell value. Read B2 and A3 from an inventory sheet, print both, and comment which "
                "line applies the one-based row offset."
            ),
            patterns=["def read_cell", "ord(", "print("],
            mapping=(
                "openpyxl accepts `ws[\"B2\"]` or `ws.cell(row=2, column=2)`; writing the converter shows what those "
                "shortcuts do internally."
            ),
        ),
        80: dict(
            topic="Ranges and slices of rows",
            idea=(
                "A range is a rectangular selection, and Python slicing expresses the row part naturally while a "
                "column selection expresses the other. The combination `sheet[start:stop]` for rows and a list of "
                "column names for columns is enough to model most reporting ranges. The critical detail is that "
                "Python slices are half-open: `rows[1:3]` includes indexes one and two but not three. Spreadsheet "
                "users often describe ranges inclusively, so translating a human range like rows two to four "
                "requires adding one to the stop. A second detail is that the header is usually outside the range "
                "but still needed to interpret it, so a range function should take the header separately or preserve "
                "it. Today's example builds a `window` helper that selects rows and named columns from a timesheet, "
                "then prints two different windows. Selecting by name again protects against column insertions. The "
                "aim is not a general range engine but a clear mapping between a visible rectangle and a list of "
                "lists, so you can reason about what a report includes and excludes before formatting it. When a stop looks wrong, first print both the slice and the visible spreadsheet rows; the mismatch is usually a one-based description."
            ),
            code=(
                'SHEET = [\n'
                '    ["date", "hours", "note"],\n'
                '    ["2024-01-01", "8", "office"],\n'
                '    ["2024-01-02", "7.5", "remote"],\n'
                '    ["2024-01-03", "9", "office"],\n'
                '    ["2024-01-04", "6", "remote"],\n'
                ']\n'
                '\n'
                'def window(sheet, start, stop, columns):\n'
                '    header = sheet[0]\n'
                '    indexes = [header.index(name) for name in columns]\n'
                '    return [[row[i] for i in indexes] for row in sheet[start:stop]]\n'
                '\n'
                'print(window(SHEET, 1, 4, ["date", "hours"]))\n'
                'print("data rows:", len(SHEET) - 1)\n'
                'assert window(SHEET, 1, 3, ["hours"]) == [["8"], ["7.5"]]\n'
                'print("slices are half-open: rows[1:3] keeps two rows")'
            ),
            variant_b="select only the office rows by filtering after the slice and print the hours",
            variant_c="make the stop argument inclusive for human-friendly row ranges and test both forms",
            mistakes=[
                "Treating the slice stop as inclusive, which returns one extra row.",
                "Recomputing column indexes for every row instead of once per range.",
                "Including the header in the data window and then summing a text value.",
            ],
            q1=(
                "How many rows does `rows[1:3]` return, and which indexes?",
                "Two rows, at indexes one and two; the stop index is excluded.",
            ),
            homework=(
                "Write `window(sheet, start, stop, columns)` that returns selected rows and named columns, with the "
                "header read once. Build a five-row timesheet, print a two-column window, and comment which line makes "
                "the stop index exclusive."
            ),
            patterns=["def window", "header.index", "print("],
            mapping=(
                "openpyxl ranges such as `ws[\"A2:C4\"]` and pandas `.iloc[start:stop]` follow similar start/stop "
                "thinking, including half-open slices in pandas."
            ),
        ),
        81: dict(
            topic="Reading a sheet into records",
            idea=(
                "Reading a sheet into records is the boundary where layout stops and business logic begins. A good "
                "reader does three things: finds the header, converts each data row to a dict, and converts values "
                "deliberately rather than magically. Keeping raw values as strings is often right at first, because "
                "codes with leading zeros must not become numbers, but calculations need converted numbers. The "
                "practical compromise is to keep the record faithful to the sheet and convert at the point of use, or "
                "to produce a second typed record with explicit rules. Today's example reads an inventory sheet into "
                "records and adds a computed total per record. The total function converts quantity and price with "
                "`float` and leaves the SKU untouched. Notice how the reader knows nothing about totals, and the total "
                "function knows nothing about row positions; each has one job. That separation also makes it obvious "
                "where a bad value will fail, because only one function converts. A reader should also report how "
                "many records it returned, which is the first number any reconciliation check needs. Treat the reader "
                "as the front door of the program: if it is honest and simple, everything downstream is easier to "
                "trust. The reader stays boring on purpose."
            ),
            code=(
                'SHEET = [\n'
                '    ["sku", "qty", "price"],\n'
                '    ["A1", "4", "2.50"],\n'
                '    ["B2", "10", "1.25"],\n'
                ']\n'
                '\n'
                'def read_records(sheet):\n'
                '    header, *rows = sheet\n'
                '    return [dict(zip(header, row)) for row in rows]\n'
                '\n'
                'def with_total(record):\n'
                '    return {**record, "total": float(record["qty"]) * float(record["price"])}\n'
                '\n'
                'records = [with_total(record) for record in read_records(SHEET)]\n'
                'for record in records:\n'
                '    print(record["sku"], f"{record[\'total\']:.2f}")\n'
                '\n'
                'assert records[0]["total"] == 10.0\n'
                'print("records:", len(records))'
            ),
            variant_b="keep the total as a string formatted to two decimals instead of a float",
            variant_c="add a `stock_value` field that multiplies a new on_hand column by price",
            mistakes=[
                "Converting every field to a number, which destroys codes such as 00123.",
                "Letting the reader compute report totals instead of returning records.",
                "Forgetting to count records, so a silently short read goes unnoticed.",
            ],
            q1=(
                "Why keep SKU as text while converting quantity and price?",
                "SKUs are identifiers, and leading zeros or letters must survive; quantity and price are quantities that arithmetic needs.",
            ),
            homework=(
                "Write `read_records(sheet)` that returns header-keyed dicts, then `add_total(record)` that adds a "
                "numeric total. Run both over an inventory sheet, print each SKU with its total, and comment which "
                "line converts quantity and price."
            ),
            patterns=["def read_records", "def add_total", "print("],
            mapping=(
                "This is the same job as `pandas.read_excel` plus dtype selection, or `ws.iter_rows` plus dict "
                "conversion in openpyxl."
            ),
        ),
        82: dict(
            topic="Writing records back to rows",
            idea=(
                "Writing is the inverse of reading, and the clean way to do it is to turn records back into a header "
                "plus rows before any serialiser touches them. That intermediate structure is testable: you can "
                "assert the header, the row order and the exact cell strings without producing a file. The writer "
                "should take an explicit header rather than guessing from the first record, because records may have "
                "different keys and the sheet's column order is a layout decision. Missing keys should become an "
                "empty string, not a crash, and every value must be converted to text deliberately, since CSV cannot "
                "represent integers or dates directly. Today's example converts two inventory records into rows, "
                "serialises them with `csv.writer` over `io.StringIO`, and prints the exact text. The in-memory "
                "buffer keeps the lesson offline and deterministic while using the same writer you would use for a "
                "real file. Notice that the conversion and the serialisation are separate functions; that seam means "
                "you can later hand the same rows to openpyxl instead. Writing well is mostly about being explicit "
                "on purpose. Keeping conversion separate also lets you test it without importing csv at all, which is useful when the target becomes a workbook library."
            ),
            code=(
                'import csv\n'
                'import io\n'
                '\n'
                'def to_rows(records, header):\n'
                '    return [header] + [\n'
                '        [str(record.get(name, "")) for name in header]\n'
                '        for record in records\n'
                '    ]\n'
                '\n'
                'records = [\n'
                '    {"sku": "A1", "qty": 4},\n'
                '    {"sku": "B2", "qty": 10},\n'
                ']\n'
                'rows = to_rows(records, ["sku", "qty"])\n'
                'buffer = io.StringIO()\n'
                'csv.writer(buffer).writerows(rows)\n'
                'print(buffer.getvalue(), end="")\n'
                '\n'
                'assert rows[1] == ["A1", "4"]\n'
                'print("records became rows, header first")'
            ),
            variant_b="write a third record missing qty and confirm the empty cell appears",
            variant_c="build the header from the union of record keys and print the chosen column order",
            mistakes=[
                "Guessing the header from the first record, so later records with more keys lose columns.",
                "Passing integers and dates straight to the writer instead of converting to text.",
                "Letting a missing key raise a KeyError instead of writing an empty cell.",
            ],
            q1=(
                "Why pass the header explicitly when writing records?",
                "Because column order and inclusion are layout decisions; deriving them from one record makes the output depend on data order.",
            ),
            homework=(
                "Write `to_rows(records, header)` that always puts the header first, fills missing keys with an empty "
                "string, and converts values to text. Serialise two records in memory with `csv.writer`, print the "
                "text, and comment which line preserves the caller's column order."
            ),
            patterns=["def to_rows", "csv.writer", "print("],
            mapping=(
                "The same rows can be handed to `ws.append` in openpyxl or `DataFrame.to_excel` in pandas; only the "
                "final serialiser changes."
            ),
        ),
        83: dict(
            topic="Copying instead of mutating the source",
            idea=(
                "Automation often transforms a sheet, and transforming in place is a quiet source of expensive bugs. "
                "If a function mutates the caller's data, every later step sees the changed values, reruns are not "
                "repeatable, and comparisons against the original become impossible. The safer default is to copy "
                "first and return the result, leaving the input as a reference. For a list of lists, a shallow copy "
                "of the outer list is not enough because the rows are still shared; copy each row too. That is why "
                "the idiom `[row[:] for row in sheet]` exists, and it is the smallest correct copy for this model. "
                "Deep copying is only needed when cells themselves are mutable objects, which they are not here. "
                "Today's example applies a discount factor to a cloned inventory sheet and prints both source and "
                "copy to show the source is unchanged. The function also converts values explicitly, so the "
                "transformation is visible. This habit pays off when a report run fails midway: the original data is "
                "still intact and the run can be repeated without reloading. Prefer pure functions at the data "
                "boundary, and let mutation be a deliberate choice rather than an accident. Pure functions also make reruns safe."
            ),
            code=(
                'SHEET = [\n'
                '    ["sku", "qty"],\n'
                '    ["A1", "4"],\n'
                '    ["B2", "10"],\n'
                ']\n'
                '\n'
                'def copy_sheet(sheet):\n'
                '    return [row[:] for row in sheet]\n'
                '\n'
                'def apply_factor(sheet, factor):\n'
                '    cloned = copy_sheet(sheet)\n'
                '    qty = cloned[0].index("qty")\n'
                '    for row in cloned[1:]:\n'
                '        row[qty] = str(round(int(row[qty]) * factor))\n'
                '    return cloned\n'
                '\n'
                'scaled = apply_factor(SHEET, 0.5)\n'
                'print("source:", SHEET)\n'
                'print("copy:", scaled)\n'
                'assert SHEET[1][1] == "4" and scaled[1][1] == "2"\n'
                'print("the source sheet was not mutated")'
            ),
            variant_b="use a shallow `list(sheet)` copy and show which change leaks into the source",
            variant_c="return both the copy and a count of how many cells changed",
            mistakes=[
                "Using `list(sheet)` and believing the rows were copied, then changing the source by accident.",
                "Mutating a shared module-level sheet so a second run starts from changed data.",
                "Copying the data but not the reference used in the assertion, which can never detect the bug.",
            ],
            q1=(
                "Why is `list(sheet)` not enough to protect the source?",
                "It copies the outer list only; each row object is still shared, so editing a row changes both lists.",
            ),
            homework=(
                "Write `scaled_copy(sheet, factor)` that clones every row, multiplies the qty column by the factor, "
                "and returns the clone. Print the source and the clone, assert the source is unchanged, and comment "
                "which line copies each row rather than just the outer list."
            ),
            patterns=["def scaled_copy", "row[:]", "print("],
            mapping=(
                "openpyxl worksheets are mutable objects, so reading values into a fresh list before editing is the "
                "same protection as copying here."
            ),
        ),
        84: dict(
            topic="Cell types: text, number, date",
            idea=(
                "Every cell has a value and an implied type, and most spreadsheet surprises come from that type being "
                "different from what it looks like. Text stays text even when it resembles a number, which is why ZIP "
                "codes and account numbers need deliberate handling. Numbers are stored without their display "
                "formatting, so 2.50 and 2.5 can be the same value shown two ways. Dates are the trickiest: Excel "
                "stores them as serial numbers with a format applied, while Python may hold a date, a string or a "
                "number depending on how the data was read. The practical approach is to tag cells with an explicit "
                "type in your model and convert based on that tag, never by guessing from appearance. Today's example "
                "models three cells as dicts with `value` and `type`, converts each through one function, and prints "
                "the Python value with its resulting type. Notice that the text cell keeps its zeros and letters, the "
                "number becomes a float and the date becomes a tuple you control. The lesson is not that one "
                "representation is best, but that the type is information you must preserve. When you later read a "
                "real workbook, find out what the library gives you before writing conversion rules."
            ),
            code=(
                'CELLS = [\n'
                '    {"value": "widget", "type": "text"},\n'
                '    {"value": "12", "type": "number"},\n'
                '    {"value": "2024-01-15", "type": "date"},\n'
                ']\n'
                '\n'
                'def convert(cell):\n'
                '    if cell["type"] == "number":\n'
                '        return float(cell["value"])\n'
                '    if cell["type"] == "date":\n'
                '        year, month, day = cell["value"].split("-")\n'
                '        return (int(year), int(month), int(day))\n'
                '    return cell["value"]\n'
                '\n'
                'for cell in CELLS:\n'
                '    value = convert(cell)\n'
                '    print(cell["type"], value, type(value).__name__)\n'
                '\n'
                'assert convert(CELLS[1]) == 12.0\n'
                'print("type is data, not decoration")'
            ),
            variant_b="add a text cell containing 007 and show that it stays three characters",
            variant_c="make the date conversion return a plain ISO string and compare the printed types",
            mistakes=[
                "Guessing type from appearance, so a zero-padded code turns into a number.",
                "Assuming a date is already a date when it is usually a string or a serial number on read.",
                "Confusing a value with its display format, such as 2.5 versus 2.50.",
            ],
            q1=(
                "Why not infer cell types from how values look?",
                "Appearance is ambiguous: 007, 2.50 and a date-like string can all be numeric or textual; only stored type or an explicit rule is reliable.",
            ),
            homework=(
                "Write `convert_cell(cell)` that branches on an explicit type tag for text, number and date, and "
                "returns the converted Python value. Run it over three cells including a zero-padded code, print each "
                "type, and comment which branch preserves the leading zeros."
            ),
            patterns=["def convert_cell", "type", "print("],
            mapping=(
                "openpyxl exposes `cell.data_type` and number formats, while pandas infers dtypes; both show why "
                "explicit conversion rules beat guessing."
            ),
        ),
        85: dict(
            topic="Blank cells and missing columns",
            idea=(
                "Blank cells are normal in real sheets, and a shape mismatch is just a blank at the end of a row. The "
                "problem is that Python distinguishes between a missing key, an empty string and `None`, while a "
                "spreadsheet user often means the same thing by all three. A robust reader normalises a short row and "
                "a blank cell to one representation, usually `None`, and then business logic can test for it once. "
                "Indexing with `row[i]` assumes the cell exists; accessing a shorter row raises IndexError, while a "
                "dict lookup with `record[\"note\"]` raises KeyError. Both failures are useful in strict contexts and "
                "wrong at a trust boundary. Today's example converts two rows of different lengths into records using "
                "bounds checks and an empty-string test, so the missing note becomes `None` rather than an exception. "
                "It then prints both records and asserts the difference. The other half of the lesson is that a "
                "required missing column is a different problem from a blank value: one is a broken schema and should "
                "stop the run, while the other may be acceptable data. Deciding which is which is a domain judgement, "
                "but it must be explicit. Silent defaults are how spreadsheets lie."
            ),
            code=(
                'SHEET = [\n'
                '    ["sku", "qty", "note"],\n'
                '    ["A1", "4"],\n'
                '    ["B2", "10", "rush"],\n'
                ']\n'
                '\n'
                'def record_for(sheet, index):\n'
                '    header = sheet[0]\n'
                '    row = sheet[index]\n'
                '    return {\n'
                '        name: (row[i] if i < len(row) and row[i] != "" else None)\n'
                '        for i, name in enumerate(header)\n'
                '    }\n'
                '\n'
                'first = record_for(SHEET, 1)\n'
                'second = record_for(SHEET, 2)\n'
                'print(first)\n'
                'print(second)\n'
                'assert first["note"] is None and second["note"] == "rush"\n'
                'print("missing columns become None, never a crash")'
            ),
            variant_b="treat a required blank as an error and print which row and column failed",
            variant_c="distinguish a truly absent column from a present but blank one in the returned record",
            mistakes=[
                "Indexing a short row directly, so a blank trailing cell raises IndexError.",
                "Turning every blank into an empty string and then treating it as real data.",
                "Confusing a missing header column, which is a schema error, with a blank value.",
            ],
            q1=(
                "Why normalise a short row and a blank cell to the same value?",
                "Both mean the data is absent, so one representation lets downstream code test once instead of handling two failures.",
            ),
            homework=(
                "Write `safe_record(header, row)` that returns a dict with every header key, using `None` for a "
                "missing or blank cell. Run it on one full row and one short row, print both dicts, and comment which "
                "condition prevents the IndexError."
            ),
            patterns=["def safe_record", "None", "print("],
            mapping=(
                "pandas represents blanks as NaN, openpyxl returns `None`; normalising at read time keeps the rest of "
                "the code free of library-specific blanks."
            ),
        ),
        86: dict(
            topic="Formulas as strings",
            idea=(
                "To an automation, a formula is two things at once: a piece of text beginning with an equals sign, "
                "and a cached result that Excel computed when it last saved. Libraries differ in whether they return "
                "the formula, the cached value or both, so you must decide which one your program needs. If you are "
                "rewriting a workbook, preserve the formula text and let the spreadsheet recalculate. If you are "
                "building a report, you may want the cached value instead, because the text `=B2*C2` is not a number. "
                "The dangerous middle ground is treating formula text as data, which silently breaks sums or, worse, "
                "evaluates something you did not intend. Today's example models cells as pairs of formula and cached "
                "value, detects formula text by its leading equals sign, and prints both per row. The little cached "
                "calculation stands in for what Excel already did, and no formula is executed. Notice that detection "
                "is a separate function, so you can change the rule in one place. The broader lesson is that "
                "spreadsheets mix data and code in the same grid, and a careful automation keeps that distinction "
                "visible rather than blurring it. The separation also keeps the reporting code honest about what it is reading."
            ),
            code=(
                'SHEET = [\n'
                '    ["item", "qty", "price", "total"],\n'
                '    ["widget", "3", "2.50", "=B2*C2"],\n'
                '    ["gizmo", "2", "9.00", "=B3*C3"],\n'
                ']\n'
                '\n'
                'def is_formula(value):\n'
                '    return isinstance(value, str) and value.startswith("=")\n'
                '\n'
                'def cached_total(row):\n'
                '    return round(float(row[1]) * float(row[2]), 2)\n'
                '\n'
                'header, *rows = SHEET\n'
                'for row in rows:\n'
                '    print(row[0], "formula:", row[3], "cached:", cached_total(row))\n'
                '\n'
                'assert is_formula(rows[0][3]) and not is_formula(rows[0][1])\n'
                'print("formulas are text with a cached result")'
            ),
            variant_b="add a row with a plain numeric total and print it alongside the formula rows",
            variant_c="collect every formula cell into a list of addresses and print the count",
            mistakes=[
                "Summing a formula column directly, so strings such as =B2*C2 enter the arithmetic.",
                "Assuming every library returns cached values rather than formula text.",
                "Replacing formulas with computed values without deciding whether recalculation should stay in Excel.",
            ],
            q1=(
                "Why is a formula cell not safe to treat as a number?",
                "Its text begins with = and describes a calculation; only the cached value or a recalculation gives the numeric result.",
            ),
            homework=(
                "Write `formula_rows(sheet)` that returns rows whose total cell starts with `=`, then print each item "
                "with its formula and its separately computed value. Run it over three rows, and comment which "
                "function distinguishes formula text from data."
            ),
            patterns=["def formula_rows", "startswith", "print("],
            mapping=(
                "openpyxl loads formulas by default and cached values only if the file saved them; pandas normally "
                "returns values, which is why mixed sheets surprise people."
            ),
        ),
        87: dict(
            topic="Formatting as data",
            idea=(
                "Formatting looks cosmetic until an automation has to reproduce a report exactly. The useful mental "
                "model is that formatting is data about a column or cell, separate from the value it describes. A "
                "total of 7.5 and a displayed 7.50 are the same number with different format rules, and conflating "
                "the two means you either store strings where numbers belong or lose the intended presentation. Excel "
                "stores number formats as codes such as `0`, `0.00`, `#,##0` and `0%`, while openpyxl exposes them "
                "through `number_format`. Building your own tiny formatter makes the distinction obvious and keeps "
                "output deterministic. Today's example attaches a format dictionary to the inventory header and "
                "renders each value through one function, printing a small aligned table. The value stays numeric in "
                "the rows; the format is applied only when rendering. That separation lets the same data feed a CSV "
                "with raw values and a display table with two decimals. It also means formatting bugs are visible in "
                "one function instead of scattered through calculations. When formatting later moves into a real "
                "workbook, the rules are the same even though the storage is different. One function owns presentation, so a format change cannot break a total."
            ),
            code=(
                'SHEET = [\n'
                '    ["item", "qty", "price", "total"],\n'
                '    ["widget", "3", "2.50", "7.50"],\n'
                '    ["gizmo", "2", "9.00", "18.00"],\n'
                ']\n'
                '\n'
                'FORMATS = {"qty": "0", "price": "0.00", "total": "0.00"}\n'
                '\n'
                'def render(value, fmt):\n'
                '    if fmt == "0":\n'
                '        return f"{float(value):.0f}"\n'
                '    if fmt == "0.00":\n'
                '        return f"{float(value):.2f}"\n'
                '    return str(value)\n'
                '\n'
                'header, *rows = SHEET\n'
                'for row in rows:\n'
                '    print(" | ".join(render(value, FORMATS.get(name, "text"))\n'
                '                     for name, value in zip(header, row)))\n'
                '\n'
                'assert render("2.5", "0.00") == "2.50"\n'
                'print("number formats are data attached to columns")'
            ),
            variant_b="add a percent column and a 0% format, then render a 0.125 value as 12% or 13%",
            variant_c="skip the format argument entirely for text columns and show why float() must not run there",
            mistakes=[
                "Storing formatted strings as the data, so later arithmetic has to parse them again.",
                "Applying one format to every column, which turns quantities into decimals.",
                "Rounding values during calculation instead of rounding only at render time.",
            ],
            q1=(
                "Why keep the value numeric while the format is a separate rule?",
                "Then calculations use exact numbers and presentation can change without rewriting or reparsing the data.",
            ),
            homework=(
                "Write `render_table(sheet, formats)` that reads a per-column format dict, leaves text columns alone, "
                "and prints one line per row. Run it on an inventory sheet, confirm 2.5 prints as 2.50, and comment "
                "which line applies the format without changing the value."
            ),
            patterns=["def render_table", "format", "print("],
            mapping=(
                "In openpyxl you set `cell.number_format = \"0.00\"`; the value and the format stay separate properties, "
                "exactly as modelled here."
            ),
        ),
        88: dict(
            topic="Validating a sheet's shape",
            idea=(
                "Validation is the cheap check that prevents expensive wrong answers. Before computing anything, "
                "confirm that the sheet has a header, that every required column is present and that every data row "
                "has the same width as the header. Those three checks catch the majority of broken exports: a renamed "
                "column, a truncated file and a stray delimiter. Validation should fail loudly with enough context to "
                "find the problem, naming the missing column or the offending row number. It should run at the trust "
                "boundary, before any conversion or arithmetic, because a shape error downstream looks like a logic "
                "bug. Today's example writes `validate_sheet`, which raises ValueError for an empty sheet, missing "
                "columns or a short row, and returns the number of valid rows. The script validates a good sheet and "
                "catches the error for a bad one. Notice that the function does not repair the data; it reports, and "
                "the caller decides. Mixing repair into validation hides the defect and makes the report depend on "
                "silent guesses. A separate check function is also easy to unit test, which is why this pattern "
                "survives in production pipelines. A validator that returns rather than prints is also trivial to call from a test."
            ),
            code=(
                'SHEET = [\n'
                '    ["sku", "qty"],\n'
                '    ["A1", "4"],\n'
                '    ["B2", "10"],\n'
                ']\n'
                '\n'
                'def validate_sheet(sheet, required):\n'
                '    if not sheet:\n'
                '        raise ValueError("empty sheet")\n'
                '    header, *rows = sheet\n'
                '    missing = [name for name in required if name not in header]\n'
                '    if missing:\n'
                '        raise ValueError(f"missing columns: {missing}")\n'
                '    for index, row in enumerate(rows, start=2):\n'
                '        if len(row) != len(header):\n'
                '            raise ValueError(f"row {index} has {len(row)} cells, expected {len(header)}")\n'
                '    return len(rows)\n'
                '\n'
                'print("valid rows:", validate_sheet(SHEET, ["sku", "qty"]))\n'
                'try:\n'
                '    validate_sheet([["sku", "qty"], ["A1"]], ["sku", "qty"])\n'
                'except ValueError as error:\n'
                '    print("rejected:", error)\n'
                'assert validate_sheet(SHEET, ["sku"]) == 2\n'
                'print("validate the shape before trusting the data")'
            ),
            variant_b="add a duplicate-header check and reject a sheet that names the same column twice",
            variant_c="return a list of all problems instead of raising on the first one",
            mistakes=[
                "Validating after converting values, so a shape bug appears as a confusing TypeError.",
                "Raising a bare error with no row number or column name to locate the problem.",
                "Repairing missing cells inside the validator and hiding the broken input.",
            ],
            q1=(
                "What three shape checks does a basic sheet validator perform?",
                "A non-empty sheet with a header, required columns present, and every data row as wide as the header.",
            ),
            homework=(
                "Write `validate_sheet(sheet, required)` that rejects an empty sheet, missing columns and short rows "
                "with a ValueError naming the problem. Validate one good sheet, catch the error for one bad sheet, and "
                "comment which check reports the offending row number."
            ),
            patterns=["def validate_sheet", "raise ValueError", "print("],
            mapping=(
                "openpyxl and pandas both surface malformed workbooks late and obscurely; an explicit shape check "
                "turns those failures into clear messages at read time."
            ),
        ),
        89: dict(
            topic="Review: rows, columns and cells checklist",
            idea=(
                "This review turns the phase into a checklist you can run against any sheet automation. First, is the "
                "workbook modelled as sheets of rows, and is the header separated exactly once? Second, are columns "
                "addressed by name rather than hard-coded index, and are addresses parsed only at the boundary? "
                "Third, are ranges half-open and clearly translated from human row numbers? Fourth, are values kept "
                "faithful on read, with types converted deliberately and blanks normalised? Fifth, are formulas kept "
                "as text with cached values treated separately? Sixth, is formatting applied only at render time? "
                "Seventh, is the sheet validated before computation, and are missing columns distinguished from blank "
                "cells? Finally, does the transformation copy its input rather than mutating the caller's data? Today's "
                "example encodes several of these checks as a small function returning pass or fail per rule, then "
                "prints the results. The point is not the specific checks but the habit of making quality explicit. A "
                "checklist like this catches most defects before a report reaches a person, and it gives you a "
                "conversation starter when a real workbook misbehaves. Run it again after every new source arrives, and record which checks changed; that record becomes a small audit trail."
            ),
            code=(
                'SHEET = [\n'
                '    ["sku", "qty", "price"],\n'
                '    ["A1", "4", "2.50"],\n'
                '    ["B2", "10", "1.25"],\n'
                ']\n'
                '\n'
                'def checklist(sheet):\n'
                '    header, *rows = sheet\n'
                '    checks = {\n'
                '        "has header": bool(header),\n'
                '        "rows match header": all(len(row) == len(header) for row in rows),\n'
                '        "qty numeric": all(float(row[header.index("qty")]) >= 0 for row in rows),\n'
                '        "price present": all(row[header.index("price")] for row in rows),\n'
                '    }\n'
                '    return checks\n'
                '\n'
                'checks = checklist(SHEET)\n'
                'for name in checks:\n'
                '    print(("pass" if checks[name] else "fail"), name)\n'
                '\n'
                'assert all(checks.values())\n'
                'print("review: header, width, values, then compute")'
            ),
            variant_b="add a check that no SKU repeats and print the checklist again",
            variant_c="return the names of failed checks and print an empty list for a good sheet",
            mistakes=[
                "Treating the checklist as documentation and never running it against the actual sheet.",
                "Checking values before checking shape, so the first failure hides the real problem.",
                "Adding so many checks that the important schema rules are lost in noise.",
            ],
            q1=(
                "Why check the sheet's shape before its values?",
                "A shape problem makes value checks unreliable or impossible, so fixing the structure first avoids misleading failures.",
            ),
            homework=(
                "Write `audit_sheet(sheet)` that returns a dict of named pass/fail checks covering header presence, "
                "row width, a numeric column and a non-empty required column. Run it on a good sheet, print each "
                "check, and comment which check would catch a truncated row."
            ),
            patterns=["def audit_sheet", "all(", "print("],
            mapping=(
                "This checklist maps onto openpyxl and pandas work: confirm columns, widths and dtypes before "
                "building a pivot or writing a workbook."
            ),
        ),
    },
)
