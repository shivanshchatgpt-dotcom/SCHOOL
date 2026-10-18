"""Verified DeepSeek-authored Day 2 content for the Automation / Scripting track."""

AUTOMATION_DAY_2 = {
    "day": 2,
    "title": "Lists and Loops: Summarizing Multiple Records",
    "domain": "Automation Foundations",
    "objective": "Use lists to store multiple records, loop over them, and generate a summary report from a file.",
    "theory": """Day 1 introduced reading a file line by line and writing a report. That works for simple cases, but automation often requires summarizing many records: totals, averages, counts, and grouping. To do that efficiently, you need two core tools: lists and loops. A list is an ordered collection of items. In Python, you create a list with square brackets, e.g., records = []. You can add items with the append() method. A for loop lets you visit each item in a list one by one. Together, they let you collect all records into one structure, then process them multiple times without re-reading the file.

Mental model: imagine a mailroom. Each piece of mail (record) arrives on a conveyor belt. Instead of processing each letter immediately, you place them into a sorting bin (list). Once all letters are collected, you sit at a desk and go through the bin one by one, tallying totals, checking addresses, and writing a summary. The list is the bin; the loop is your hands moving each letter. This separation is powerful: you can sort the list, filter it, or count items without worrying about the original file.

Practical automation relevance: almost every real automation script processes multiple records. Examples include summarizing daily sales from a CSV, counting errors in a log file, calculating average response times from a server log, or aggregating expenses by category. Lists and loops are the foundation for these tasks. They also make your code safer: you can validate all records before writing any output, and you can re-run calculations on the same list without touching the input file again.

Common mistakes. First, forgetting to create an empty list before the loop. If you try to append to a variable that is not a list, you get an AttributeError. Always initialize: records = []. Second, using the wrong index when accessing list items. Remember that list indices start at 0, and the last index is len(list) - 1. Using an index out of range raises IndexError. Third, modifying a list while iterating over it. For example, removing items inside a for loop can cause items to be skipped. If you need to remove items, iterate over a copy or build a new list. Fourth, not converting data types. When reading from a file, all values are strings. If you append a string like '100' to a list and later try to sum it, you will get a TypeError. Convert to int or float immediately when parsing. Fifth, forgetting to strip newline characters. Lines from a file end with a newline character. Use line.strip() before splitting. Sixth, not handling malformed lines. One bad line can crash your script. Use try/except or check the number of fields. By avoiding these mistakes, your batch processing will be robust and reliable.

In this day, you will build on Day 1 by reading multiple records into a list, then looping over that list to compute summary statistics and write a clean report. This pattern—read, store, process, output—is the backbone of automation.""",
    "code_example": """# summarize_expenses.py
import os

input_file = 'expenses.csv'
output_file = 'expense_summary.txt'

if not os.path.exists(input_file):
    print(f'Error: {input_file} not found.')
    exit(1)

records = []
with open(input_file, 'r') as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        parts = line.split(',')
        if len(parts) != 3:
            print(f'Skipping malformed line: {line}')
            continue
        date = parts[0].strip()
        category = parts[1].strip()
        try:
            amount = float(parts[2].strip())
        except ValueError:
            print(f'Skipping invalid amount: {line}')
            continue
        records.append([date, category, amount])

total = 0.0
for record in records:
    total += record[2]

average = total / len(records) if records else 0.0

with open(output_file, 'w') as f:
    f.write('Expense Summary\\n')
    f.write('===============\\n')
    for record in records:
        f.write(f'{record[0]} | {record[1]} | {record[2]:.2f}\\n')
    f.write('---------------\\n')
    f.write(f'Total records: {len(records)}\\n')
    f.write(f'Total amount: {total:.2f}\\n')
    f.write(f'Average amount: {average:.2f}\\n')

print(f'Summary written to {output_file}')""",
    "questions": [
        "Why is it useful to store records in a list before processing them, instead of processing each line immediately?",
        "How do you create an empty list in Python, and how do you add an item to it?",
        "What happens if you add a string to a list and then sum it without converting it to a number? How can you avoid that?",
    ],
    "answers": [
        "It allows you to process all records multiple times, such as computing totals and averages, without re-reading the file, and it makes validation easier.",
        "Use empty square brackets: records = []. Add items with records.append(item).",
        "You get a TypeError. Avoid it by converting values to int or float while parsing each record, before appending.",
    ],
    "homework": "Create transaction_summary.py that reads transactions.txt, where each line has date, type (deposit or withdrawal), and amount separated by commas. Check that the input exists; skip empty lines; validate exactly three fields and a valid float amount; store valid records as [date, type, amount] in records; compute deposits, withdrawals, and net balance; write each transaction plus totals to transaction_report.txt with two decimal places; and print confirmation. Use only Day 1 and Day 2 concepts. Observable output: transaction_report.txt contains correct totals and the console shows confirmation.",
    "required_patterns": ["for ", "in ", "append(", "print(", "=", "[]", "open(", "with "],
}
