"""Locally authored Automation / Scripting Day 4."""

AUTOMATION_DAY_4 = {
    "day": 4,
    "title": "Error Handling and Reliable Batch Processing",
    "domain": "Automation Foundations",
    "objective": "Handle predictable input and file errors without losing a batch, and make recovery behavior observable.",
    "theory": """Reliable automation does not assume that every input is perfect. Files can be missing, permissions can change, a disk can be unavailable, and individual records can contain unexpected values. Error handling is the practice of deciding what should happen when an operation fails. The goal is not to hide every exception. The goal is to preserve useful work, report the failure clearly, and avoid repeating work that already succeeded.

Python distinguishes syntax errors from runtime exceptions. A syntax error prevents a program from starting. A runtime exception occurs while the program is running, such as FileNotFoundError, PermissionError, ValueError, or OSError. Automation scripts should anticipate the exceptions that are part of their normal operating boundary. For example, a missing input file is a normal condition that should produce a clear message and a non-zero exit status. A malformed numeric field inside a batch is different: one bad record should be counted and skipped while the remaining records continue.

The mental model is an airport baggage system. Bags travel through several stations. If one bag has a damaged tag, the system diverts that bag to a manual-review area instead of stopping the entire conveyor. The operator records the reason, the system keeps moving the remaining bags, and the final report says how many items were accepted and how many were diverted. This is graceful degradation. A second useful pattern is fail fast: if the destination database is unavailable, continuing to process more records may create duplicate or misleading output. Use fail fast for unrecoverable shared resources and graceful degradation for independent records.

Exception handling should be narrow. Catch the specific exception you expect and can explain. A broad except Exception can hide programming mistakes such as a misspelled variable or a broken function call. When an exception is handled, the program should do something meaningful: report the file path, count the rejected record, write a warning, or exit with a documented status. Silent failure is dangerous because the operator may believe a report was created when it was not.

Recovery also requires an idempotency strategy. Re-running a script should not double-count records or duplicate database rows. Use a stable identifier such as a transaction ID, check whether the identifier has already been processed, and write output to a temporary file before replacing the final report. A temporary file prevents a crash halfway through writing from destroying the previous good report. After writing, flush and close the file, then verify that it exists and has the expected shape.

For this lesson, you will build a small resilient batch reader. It will distinguish a missing file from a malformed record, count warnings, continue processing valid records, and return a summary that the caller can inspect. The design keeps file handling separate from record parsing, so one failure does not contaminate the other. It also gives the operator observable evidence: accepted count, rejected count, and a clear failure message.

Common mistakes include catching exceptions and immediately printing a generic message, continuing after a critical shared resource fails, opening the final output file before the input has been validated, and re-running a non-idempotent operation without checking previous state. Avoid these mistakes by separating error classes, documenting the recovery policy, using temporary output files, and making the summary report part of the normal successful path.""",
    "code_example": """import os
import tempfile


def read_records(path):
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    records = []
    rejected = 0
    with open(path, 'r', encoding='utf-8') as source:
        for line in source:
            if not line.strip():
                continue
            parts = [part.strip() for part in line.split(',')]
            if len(parts) != 3:
                rejected += 1
                continue
            date, category, amount_text = parts
            try:
                amount = float(amount_text)
            except ValueError:
                rejected += 1
                continue
            if amount < 0:
                rejected += 1
                continue
            records.append({'date': date, 'category': category, 'amount': amount})
    return records, rejected


def write_report(records, rejected, output_path):
    directory = os.path.dirname(output_path) or '.'
    os.makedirs(directory, exist_ok=True)
    fd, temporary_path = tempfile.mkstemp(dir=directory, suffix='.tmp')
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as report:
            report.write('date | category | amount\\n')
            for record in records:
                report.write(f"{record['date']} | {record['category']} | {record['amount']:.2f}\\n")
            report.write(f'accepted={len(records)}\\n')
            report.write(f'rejected={rejected}\\n')
        os.replace(temporary_path, output_path)
    except Exception:
        if os.path.exists(temporary_path):
            os.unlink(temporary_path)
        raise


def main():
    try:
        records, rejected = read_records('expenses.csv')
    except FileNotFoundError as error:
        print(f'Input unavailable: {error}')
        return 1
    write_report(records, rejected, 'reports/expenses.txt')
    print(f'Accepted {len(records)} records; rejected {rejected}.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())""",
    "questions": [
        "When should an automation script use graceful degradation instead of failing fast?",
        "Why is writing the report to a temporary file and using os.replace safer than writing directly to the final path?",
        "Why is catching Exception too broad for a reliable batch-processing script?",
    ],
    "answers": [
        "Use graceful degradation for independent records where one bad item should be skipped and the rest should continue. Use fail fast for a critical shared resource whose failure makes all further output unreliable.",
        "The temporary file prevents a crash or partial write from destroying the previous good report. os.replace then promotes the complete file into place as one operation.",
        "A broad handler can hide programming errors such as misspelled names or broken calls. Catch the specific expected exceptions and let unexpected errors remain visible.",
    ],
    "homework": "Create resilient_report.py with read_records(path), write_report(records, rejected, output_path), and main(). The reader must handle a missing file with a clear message and return exit status 1, skip blank, malformed, negative, and non-numeric records while counting them, and continue valid records. The writer must create the output directory, write to a temporary file, replace the final report only after successful completion, and remove the temporary file on failure. Test with a missing path, a clean file, and a file containing four bad records. Observable output: the console reports accepted and rejected counts, the final report exists only after success, and the script returns the documented status.",
    "required_patterns": ["try:", "except", "raise", "with ", "for ", "if ", "return ", "os.replace"],
}
