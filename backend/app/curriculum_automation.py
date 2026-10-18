"""Verified DeepSeek-authored Day 1 content for the Automation / Scripting track."""

AUTOMATION_DAY_1 = {
    "day": 1,
    "title": "What Is Automation? Scripts, Inputs, Outputs, and a Safe Batch Report",
    "domain": "Automation Foundations",
    "objective": "Understand automation concepts and write a safe Python script that reads an input file and produces a batch report as output.",
    "theory": """Automation means using code to perform tasks that would otherwise require manual effort. In everyday work, manual tasks are repetitive, time-consuming, and prone to human error. For example, copying data from one file to another, renaming hundreds of files, or calculating totals in a spreadsheet. Automation replaces those manual steps with a script: a Python file that executes a precise sequence of instructions. A script is like a recipe. It defines the steps, the ingredients (inputs), and the final dish (output). When you run a script, Python follows the recipe exactly, every time, without getting tired or distracted.

In automation, you must clearly identify inputs and outputs. Inputs are the data your script needs to do its job: files, user input, command-line arguments, or environment variables. Outputs are the results: new files, printed messages, logs, or updated data. A common and safe automation pattern is the file-based batch report. You have an input file containing raw data, such as sales records or expense entries. Your script reads the file, processes each line, performs calculations, and writes a summary report to a new output file. This approach is safe because it does not modify the original input; it creates a new file. Always preserve the original data.

Mental model: imagine a robot assistant in a kitchen. You give it a recipe (script) and ingredients (input file). The robot follows the steps, measures, mixes, and cooks, then produces a dish (output file). You do not need to watch every move; you trust the recipe. But you must write the recipe clearly and handle unexpected situations, like a missing ingredient. Safe automation follows several principles: always back up or avoid modifying original files; validate that inputs exist and are in the expected format; use a dry-run mode (print what would happen without writing) when testing; log actions and errors; and start with small sample data before running on large batches.

Practical automation relevance is enormous. Businesses use scripts to generate daily reports, clean data, send emails, back up databases, and monitor systems. For a beginner, a file-based batch report is an ideal first automation because it uses only basic Python: variables, strings, file reading and writing, loops, and conditionals. It teaches you to think in terms of inputs, processing, and outputs—the same structure used in complex automation pipelines. The time saved is significant: a task that takes 30 minutes manually can run in seconds, and it will be consistent every time.

Common mistakes in early automation. First, hardcoding values or file paths. If you write open('C:/Users/Alice/data.txt') and then share the script, it will break on another computer. Use relative paths or variables. Second, not checking if the input file exists. If the file is missing, Python raises a FileNotFoundError and crashes. Always check with os.path.exists() or handle exceptions. Third, overwriting the original file. Writing to the same file you read from can destroy data if something goes wrong. Always write to a new file or make a backup. Fourth, ignoring errors in data lines. A single malformed line can crash your script. Use try/except or skip bad lines with a warning. Fifth, not testing with a small sample. Running a script on a huge dataset without testing can produce garbage or take too long. Always test on a few lines first. By avoiding these mistakes, your automation will be reliable and safe.""",
    "code_example": """# safe_batch_report.py
# Reads a sales file, computes totals, writes a report.

import os

input_file = "sales_data.txt"
output_file = "sales_report.txt"

# Safety check: input file must exist
if not os.path.exists(input_file):
    print(f"Error: {input_file} not found. Please provide the input file.")
    exit(1)

# Read and process
grand_total = 0.0
report_lines = []

with open(input_file, "r") as f:
    for line in f:
        line = line.strip()
        if not line:  # skip empty lines
            continue
        parts = line.split(",")
        if len(parts) != 3:
            print(f"Skipping malformed line: {line}")
            continue
        item = parts[0].strip()
        quantity = int(parts[1].strip())
        price = float(parts[2].strip())
        line_total = quantity * price
        grand_total += line_total
        report_lines.append(f"{item}: {quantity} x {price} = {line_total:.2f}")

# Write report
with open(output_file, "w") as f:
    f.write("Sales Report\\n")
    f.write("============\\n")
    for report_line in report_lines:
        f.write(report_line + "\\n")
    f.write(f"Grand Total: {grand_total:.2f}\\n")

print(f"Report written to {output_file}")""",
    "questions": [
        "What is automation, and how does a script differ from manual work?",
        "Why is it important to separate inputs from outputs in a batch report?",
        "Name two safety practices when writing an automation script.",
    ],
    "answers": [
        "Automation uses code to perform repetitive tasks; a script is a reusable file of instructions, while manual work is done by hand and is slower and error-prone.",
        "Separating inputs from outputs preserves original data and allows safe re-runs; you read from an input file and write results to a new output file.",
        "Always check that input files exist, and avoid overwriting original files by writing to a new file or making backups.",
    ],
    "homework": "Create batch_report.py that reads expenses.txt, where each line contains an expense name and amount separated by a comma. Check that the input exists; skip empty lines; convert each amount to float; calculate total expenses and entry count; write each expense and amount to expenses_report.txt, ending with 'Total: X.XX' and 'Number of entries: N'; and print a confirmation. Use variables, strings, print, comments, basic file I/O, conditionals, and loops. Observable output: expenses_report.txt contains correct totals and the console shows the output filename.",
    "required_patterns": ["import ", "print(", "open(", "with ", "if ", "for "],
}
