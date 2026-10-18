"""Locally authored Automation / Scripting Day 3."""

AUTOMATION_DAY_3 = {
    "day": 3,
    "title": "Functions: Building Reusable Automation Steps",
    "domain": "Automation Foundations",
    "objective": "Refactor repeated automation logic into small, testable Python functions with clear inputs and outputs.",
    "theory": """Functions are the main tool for making an automation script understandable, reusable, and testable. A function is a named block of instructions that accepts inputs, performs one clear job, and returns a result. Instead of writing the same parsing or validation code three times, you define it once and call it wherever it is needed. This is especially important in automation because scripts often process many records, and a small mistake repeated inside a loop can silently corrupt every output row.

The mental model is a workshop tool. A drill press does one job: it accepts a piece of wood and a depth, clamps the material, drills, and returns a finished hole. It does not decide what the entire workshop should build. Likewise, a function such as parse_record should parse one line and return a structured record or None for invalid input. The surrounding script decides what to do with the results. Small functions are easier to reason about because their preconditions and outputs are narrow. They are also easier to test without creating a real file or changing the operating system.

A useful function has a clear contract. The contract describes what arguments it accepts, what it returns, and what errors it handles. For example, parse_record(line) accepts a string and returns a dictionary containing a date, category, and amount. If the line is malformed, it can return None instead of raising an exception. The caller can then count the rejected line and continue. This pattern is called graceful degradation: one bad record should not destroy an entire batch. It is also better than a broad try/except block that hides the real problem.

Functions improve reuse. If a later lesson needs the same amount parser for a different file format, you can keep the parser unchanged and write a new function for the new format. Functions also make testing practical. You can call parse_record('2026-01-01,food,12.50') and assert that the result is correct. You can test an empty string, a missing field, and a non-numeric amount separately. Each test has one reason to fail, so the feedback is actionable.

Common mistakes include giving a function too many unrelated responsibilities, changing global variables inside it, returning different types for different inputs, and swallowing every exception. Avoid a function that reads a file, validates records, calculates totals, prints results, and writes a report; divide it into parse_record, read_records, summarize_records, and write_report. Avoid relying on global configuration when explicit parameters would make the dependency clear. Use return values rather than printing from low-level functions. Print at the program boundary where a human needs feedback. Finally, document assumptions with a short docstring and use descriptive names.

In today's lesson you will refactor a batch processor into functions. The mental model is a pipeline of small, testable tools connected by a short main routine. This approach is the foundation for reliable automation: functions isolate responsibilities, contracts make behavior predictable, and tests let you verify each transformation before processing a complete batch.""",
    "code_example": """def parse_record(line):
    parts = [part.strip() for part in line.split(',')]
    if len(parts) != 3:
        return None
    date, category, amount_text = parts
    try:
        amount = float(amount_text)
    except ValueError:
        return None
    return {'date': date, 'category': category, 'amount': amount}


def read_records(lines):
    records = []
    rejected = 0
    for line in lines:
        if not line.strip():
            continue
        record = parse_record(line)
        if record is None:
            rejected += 1
        else:
            records.append(record)
    return records, rejected


def summarize_records(records):
    total = 0.0
    for record in records:
        total += record['amount']
    return total


if __name__ == '__main__':
    sample = ['2026-01-01,food,12.50', 'bad line', '2026-01-02,travel,7.25']
    records, rejected = read_records(sample)
    print(f'Accepted: {len(records)}')
    print(f'Rejected: {rejected}')
    print(f'Total: {summarize_records(records):.2f}')""",
    "questions": [
        "Why is a function with one clear responsibility easier to test than a function that performs the entire batch job?",
        "What should parse_record return when a line has the wrong number of fields or an invalid amount, and why?",
        "Why should low-level functions return values instead of printing directly?",
    ],
    "answers": [
        "A narrow function can be tested with small inputs and one responsibility, so a failure is easy to locate and the rest of the program does not need to run.",
        "It can return None for a rejected record. The caller can count the rejection and continue processing other records instead of crashing the whole batch.",
        "Returned values are reusable by other functions, easier to test, and keep human-facing output at the program boundary where it belongs.",
    ],
    "homework": "Create functions.py containing parse_expense(line), read_expenses(lines), summarize_expenses(records), and format_summary(total, accepted, rejected). Each function should have one responsibility, explicit parameters, and a return value instead of printing. Test at least six inputs including two valid records, a blank line, a line with the wrong field count, a negative amount, and a non-numeric amount. Extend the main routine to print the accepted count, rejected count, and total with two decimal places. Observable output: the program prints the correct counts and total, and no invalid record is added to the records list.",
    "required_patterns": ["def ", "return ", "for ", "if ", "try:", "except", "print("],
}
