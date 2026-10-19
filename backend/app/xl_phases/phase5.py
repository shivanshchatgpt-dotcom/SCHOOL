PHASE = (
    "Automation, Scheduling and Reliability",
    "Turn a working script into a scheduled, observable and recoverable job you can trust unattended.",
    {
        135: dict(
            topic="Orientation: recurring jobs",
            idea=(
                "Automation begins when work repeats. A recurring job is not a reminder in a calendar; it is a rule "
                "that says what to do, over which input, and how often. Modelling that rule as data — a name, a "
                "period, an offset — lets you reason about it and test it, which a note-to-self never allows. Today "
                "you express a simple schedule as a dict and a function that answers a precise question: given a list "
                "of period numbers, which of them does this job fire on? The trick is modular arithmetic: a job with "
                "period 3 starting at 1 fires on 1, 4, 7 and so on. That is the same idea behind a cron */3 step, Task "
                "Scheduler repetitions, and every while-loop that works and then waits. The value of seeing it as a "
                "pure function is that you can check the schedule without waiting days for it to happen, and you can "
                "spot a job that almost never runs or one that overlaps another. Keep the definition separate from the "
                "trigger: the schedule says when, the script says what. That separation recurs through this whole "
                "phase, and it is what lets you rehearse a job, monitor it and recover it without rewriting the work "
                "it actually does."
            ),
            code=(
                'JOB = {"name": "nightly_report", "every": 3, "start": 1}\n'
                '\n'
                'def runs(job, days):\n'
                '    return [d for d in days if (d - job["start"]) % job["every"] == 0]\n'
                '\n'
                'schedule = runs(JOB, list(range(1, 11)))\n'
                'print(JOB["name"], "runs on days", schedule)\n'
                '\n'
                'assert schedule == [1, 4, 7, 10]\n'
                'print("a recurring job is a rule, not a reminder")'
            ),
            variant_b='change `every` to 2 and print which days change, leaving `start` alone',
            variant_c='add a `skip` list of days and filter scheduled days that cannot run',
            mistakes=[
                "Modelling the schedule as prose in a document nobody re-reads after the first month.",
                "Confusing the trigger (when to start) with the work (what the run does).",
                "Using a period that never lines up with the input data, so the job reports on an empty window.",
            ],
            q1=(
                "Why express a recurring schedule as a pure function of day numbers?",
                "Because then you can test and reason about when it fires without waiting for real time to pass.",
            ),
            homework=(
                "Write `runs(job, days)` that takes a job dict with `every` and `start` plus a list of integer day "
                "numbers, and return the days the job fires on. Call it with period 3 starting at 1, print the result, "
                "and comment which line decides membership of the schedule."
            ),
            patterns=["def runs", "%", "print("],
            mapping=(
                "This is the same predicate a scheduler evaluates constantly; cron, systemd timers and cloud schedulers "
                "differ only in the notation they wrap around it."
            ),
        ),
        136: dict(
            topic="Idempotent scripts",
            idea=(
                "An idempotent script is one you can run twice without the second run changing anything. It matters "
                "because scheduled jobs fail, get retried, get run by hand after an alert, and sometimes run while a "
                "previous copy is still finishing. If running it twice doubles a figure or appends a duplicate, the "
                "retry meant to save you has corrupted the output. The discipline is to express work as applying a "
                "change to a state so that applying the same change again is a no-op: set a value rather than "
                "increment it, overwrite a file rather than append to it, and key each record by an identifier rather "
                "than push it onto a growing list. Today you write a tiny apply that merges changes into a copy of a "
                "state, and you prove the result is identical after one run and after two. That assertion is the whole "
                "test of idempotence. In practice you make a run idempotent by deciding, for each side effect, what "
                "already done looks like: a row keyed by id, a file marked with the run version, a flag set to "
                "complete. When you cannot make an operation idempotent, that is the moment to reach for a lock or a "
                "guard rather than hope the duplicate never happens."
            ),
            code=(
                'def apply(state, changes):\n'
                '    nxt = dict(state)\n'
                '    nxt.update(changes)\n'
                '    return nxt\n'
                '\n'
                'CHANGES = {"total": 42, "status": "done"}\n'
                'state = {"total": 0, "status": "pending"}\n'
                '\n'
                'once = apply(state, CHANGES)\n'
                'twice = apply(once, CHANGES)\n'
                'print("after one run: ", once)\n'
                'print("after two runs:", twice)\n'
                '\n'
                'assert once == twice\n'
                'print("idempotent: rerunning changes nothing")'
            ),
            variant_b='add a counter that increments and show the two results now differ',
            variant_c='model the change as a dict keyed by record id and overwrite instead of appending',
            mistakes=[
                "Appending to a file or list on every run, so a retry silently duplicates the previous attempt.",
                "Incrementing a running total from the stored value, so replaying a run doubles it.",
                "Treating idempotence as a property of the code instead of each side effect it performs.",
            ],
            q1=(
                "What does it mean for a run to be idempotent?",
                "Running it again leaves the system in the same state as running it once, so retries are safe.",
            ),
            homework=(
                "Write `apply(state, changes)` that returns a new dict with the changes merged in, then apply the same "
                "changes twice and assert the two results are equal. Print both results and comment which line proves "
                "the operation is idempotent."
            ),
            patterns=["def apply", "assert", "print("],
            mapping=(
                "Cloud pipelines, payment posting and file synchronisers all rely on idempotent steps so that a "
                "retry after a network failure does not double the effect."
            ),
        ),
        137: dict(
            topic="Dry-run mode",
            idea=(
                "A dry-run mode runs the whole script but refuses to make changes, printing what it would have done. "
                "It is the cheapest safety feature in automation and the one people add last, usually after an "
                "incident. The implementation is a single boolean threaded through the code that gates every side "
                "effect: the computation still happens, the decisions are still made, but the write, the delete and "
                "the send are replaced by a line of narration. That lets you rehearse a dangerous job on real data "
                "before trusting it, and it lets a reviewer see exactly which actions a run would take. The subtlety "
                "is that the dry run must exercise the same code path as the live run, or it teaches you nothing; a "
                "separate preview function that drifts from the real one is worse than none. Today you write one "
                "process function that takes a dry_run flag and reports either what it would write or what it actually "
                "wrote, counting the writes so the difference is visible. The count is the proof: zero in dry mode, "
                "the real number in live mode, and the same decisions in both. A dry run is not a substitute for testing on a "
                "copy, but it is the fastest way to see a whole run's intentions before any of them happen."
            ),
            code=(
                'def process(rows, dry_run):\n'
                '    log = []\n'
                '    written = 0\n'
                '    for row in rows:\n'
                '        if dry_run:\n'
                '            log.append("would write " + row)\n'
                '        else:\n'
                '            written += 1\n'
                '            log.append("wrote " + row)\n'
                '    return log, written\n'
                '\n'
                'log, written = process(["alpha", "beta"], dry_run=True)\n'
                'print("\\n".join(log))\n'
                'print("rows written:", written)\n'
                '\n'
                'assert written == 0\n'
                'print("dry run rehearses the same path without side effects")'
            ),
            variant_b='run the same rows with `dry_run=False` and confirm the log wording and count change',
            variant_c='return the count of rows that *would* be written and assert it matches the live run',
            mistakes=[
                "Maintaining a separate preview path that quietly diverges from the code that really writes.",
                "Making the dry run skip the computation, so it never validates the logic that matters.",
                "Forgetting to gate one side effect, so a dry run sends one real email anyway.",
            ],
            q1=(
                "Why must the dry run share the code path with the live run?",
                "Otherwise the rehearsal validates a different program and hides the mistake you were trying to catch.",
            ),
            homework=(
                "Write `process(rows, dry_run)` that returns a log of strings and a count of writes, doing nothing "
                "except noting the action when dry_run is true. Call it in dry mode over three rows, print the log "
                "and count, and comment which line gates the side effect."
            ),
            patterns=["def process", "dry_run", "print("],
            mapping=(
                "Terraform plan, rsync dry-run and database migration previews are the same idea: show the actions, "
                "apply none, and let a human approve the real run."
            ),
        ),
        138: dict(
            topic="Logging a run",
            idea=(
                "A log is the only evidence a scheduled job leaves behind. When something goes wrong at six in the "
                "morning and nobody was watching, the log is what tells you which step ran, what it saw and where it "
                "stopped. Good logging is boring: one line per meaningful event, a stable order, a level, and enough "
                "context to identify the input. Today you build a run log as a plain list of strings — start, each "
                "step, the end, and any problem — and you print it. Keeping the log in memory first is deliberate: it "
                "is data you can assert on, count, and later write to a file or a monitoring system without changing "
                "how it was produced. Two habits make logs useful rather than noisy. Log boundaries, not just "
                "failures, so you can tell the difference between finished with nothing to do and never started. And "
                "keep the same shape every run, so a reader scanning a hundred lines can find the problem by its "
                "position. The run id that usually opens a real log line is a parameter here, not a call to the clock, "
                "which keeps the example deterministic and testable. The log is also the first thing you will read "
                "after an alert, so decide its shape before the day you need it."
            ),
            code=(
                'def run_log(run_id, steps):\n'
                '    log = ["START run " + run_id]\n'
                '    for i, step in enumerate(steps, 1):\n'
                '        log.append("STEP %02d %s" % (i, step))\n'
                '    log.append("END run " + run_id + " complete")\n'
                '    return log\n'
                '\n'
                'lines = run_log("R001", ["open config", "read input", "write report"])\n'
                'print("\\n".join(lines))\n'
                'print("log lines:", len(lines))\n'
                '\n'
                'assert lines[0].startswith("START") and lines[-1].endswith("complete")\n'
                'print("one line per event, same shape every run")'
            ),
            variant_b='add a level marker such as INFO or WARN to each line and print the log again',
            variant_c='have a step record a failure and append an ERROR line without stopping the log',
            mistakes=[
                "Logging only failures, so a job that never started looks the same as one that finished cleanly.",
                "Printing vague messages with no run id or step number, so the log cannot be tied to an input.",
                "Writing the last thing first by buffering wrongly, so the log reads in the wrong order.",
            ],
            q1=(
                "Why log the start and end of a run, not just its errors?",
                "The boundaries distinguish a clean run from one that never happened, which is the first question after an alert.",
            ),
            homework=(
                "Write `run_log(run_id, steps)` that returns a list of log strings with a START line, a numbered line "
                "per step, and an END line. Call it with three steps, print each line, and comment which line fixes "
                "the shape of every run."
            ),
            patterns=["def run_log", "append", "print("],
            mapping=(
                "Structured logging to files or a log service is how cron jobs and CI builds become debuggable after "
                "the fact, especially when the run happened hours ago on another machine."
            ),
        ),
        139: dict(
            topic="Handling errors per row",
            idea=(
                "One bad row should never sink a whole run, but silently ignoring bad rows is just as bad. The "
                "reliable pattern is per-row error handling: process each record inside a try block, collect the ones "
                "that fail with a note about which row and why, and carry on. That turns a single fatal exception into "
                "a reported list of problems, and it means a report covering ninety-nine good rows still gets produced "
                "while pointing at the one that needs attention. The important details are the identifiers — a row "
                "number and the offending value — so the failure is actionable, and the honesty of the summary: the "
                "report should state how many rows were skipped rather than pretend the input was clean. This is the "
                "same decision you made when cleaning data, now made while running. Be careful not to swallow errors "
                "too broadly: catch the exception you expect, like a value that cannot convert, and let genuinely "
                "unexpected failures stop the run, because a try that catches everything hides bugs. Today you split "
                "a list of values into converted numbers and error strings, and assert both counts. The run should end with a "
                "summary — how many succeeded, how many were skipped — so the outcome is visible without reading every line."
            ),
            code=(
                'def convert(values):\n'
                '    good = []\n'
                '    errors = []\n'
                '    for i, value in enumerate(values, 1):\n'
                '        try:\n'
                '            good.append(float(value))\n'
                '        except ValueError:\n'
                '            errors.append("row %d: bad value %r" % (i, value))\n'
                '    return good, errors\n'
                '\n'
                'numbers, problems = convert(["1.5", "oops", "3"])\n'
                'print("converted:", numbers)\n'
                'print("errors:   ", problems)\n'
                '\n'
                'assert len(numbers) == 2 and len(problems) == 1\n'
                'print("one bad row is reported, not fatal")'
            ),
            variant_b='catch a second exception type, such as a None value, and print both classes of error',
            variant_c='continue past the bad row but append its value to a quarantine list and print that list',
            mistakes=[
                "Letting one unparseable cell raise and abort the whole run, losing the good rows.",
                "Catching every exception, so a genuine bug is filed as a data problem and ignored.",
                "Dropping bad rows without counting or identifying them, so the report lies by omission.",
            ],
            q1=(
                "Why catch only the specific exception you expect in a per-row loop?",
                "A catch-all hides real bugs in the logic and files them as harmless data problems.",
            ),
            homework=(
                "Write `convert(values)` that returns a list of floats and a list of error strings naming each bad "
                "value with its row number. Run it over four values including two bad ones, print both lists, and "
                "comment which line keeps one bad row from stopping the rest."
            ),
            patterns=["def convert", "except", "print("],
            mapping=(
                "Data pipelines routinely quarantine bad records and report counts; the pattern is the same whether "
                "the input is a spreadsheet export or an API feed."
            ),
        ),
        140: dict(
            topic="Retrying locked or missing files",
            idea=(
                "Locked files and missing shares are the ordinary weather of scheduled automation: something else is "
                "holding the workbook, or the file has not landed yet. The answer is a bounded retry, not an immediate "
                "crash and not a loop that runs forever. A retry is a small policy: how many attempts, how long "
                "between them, and what counts as a failure worth retrying. Today you model that policy as a "
                "deterministic list of outcomes and a function that walks it, logging each attempt and stopping at the "
                "first success. Because the attempts are a list rather than a call to sleep, the example is instant "
                "and repeatable, but the shape is exactly what real code does. Two rules keep retries from making "
                "things worse. Cap the attempts and give up loudly, because an unbounded retry turns a transient "
                "glitch into a stuck job and a queue of duplicates. And retry only the failures that are plausibly "
                "temporary; retrying a wrong password or a schema change just wastes time and buries the real error. "
                "When the retries are exhausted, the honest outcome is a clear failure the runbook can act on. A retry that "
                "eventually succeeds should still leave a trace, so a flaky dependency stays visible instead of being "
                "quietly papered over."
            ),
            code=(
                'def attempt_file(attempts):\n'
                '    log = []\n'
                '    for i, outcome in enumerate(attempts, 1):\n'
                '        if outcome == "locked":\n'
                '            log.append("attempt %d: locked, will retry" % i)\n'
                '        else:\n'
                '            log.append("attempt %d: %s" % (i, outcome))\n'
                '            return log, True\n'
                '    return log, False\n'
                '\n'
                'log, ok = attempt_file(["locked", "locked", "ok"])\n'
                'print("\\n".join(log))\n'
                'print("succeeded:", ok)\n'
                '\n'
                'assert ok is True\n'
                'print("bounded retry, then stop")'
            ),
            variant_b='give the list fewer attempts and a final miss, and print the clear failure result',
            variant_c='add a permanent error such as "denied" that returns immediately without retrying',
            mistakes=[
                "Retrying forever, so a stuck file becomes a job that never ends and never alerts.",
                "Retrying errors that can never succeed, such as a wrong password or a schema mismatch.",
                "Sleeping between attempts with no cap, so the job blocks a scheduler worker for hours.",
            ],
            q1=(
                "Why should retries be bounded and only cover plausibly temporary failures?",
                "Unbounded retries hide the failure and waste time, while retrying permanent errors just delays the real alert.",
            ),
            homework=(
                "Write `attempt_file(attempts)` that walks a list of outcome strings, logs each attempt, returns a log "
                "and a success flag, and stops at the first success. Call it with two locked attempts then an ok, "
                "print the log, and comment which line enforces the bound."
            ),
            patterns=["def attempt_file", "return", "print("],
            mapping=(
                "File shares, network drives and cloud storage all produce transient lock errors; a capped retry is "
                "the standard defence in scheduled scripts and ETL tools."
            ),
        ),
        141: dict(
            topic="Configuration files",
            idea=(
                "Configuration is everything that differs between one run and the next: where the input lives, where "
                "the output goes, how many retries, who to alert. Hard-coding those in the script means every change "
                "is a code change, every environment needs its own copy, and the same logic silently diverges between "
                "machines. The fix is to read settings from data — a dict, a file, or environment variables — and "
                "merge them over sensible defaults, so the script states what it needs and the operator states what it "
                "wants. Today you write a load_config that copies a defaults dict and overlays overrides, and you "
                "print the resolved settings in sorted order. That overlay is the whole idea: defaults make the script "
                "runnable with no configuration, overrides make it adaptable, and neither silences the other. Two "
                "habits keep configuration trustworthy. Validate it early — a missing key or an unknown format should "
                "fail at startup with a clear message, not halfway through writing a report. And keep secrets out of "
                "the config file, reading them from the environment instead, so the file can be shared and "
                "version-controlled safely. Configuration is the seam between the code and the world it runs in. Making settings explicit also documents "
                "what the script depends on, which is a gift to whoever has to operate it next."
            ),
            code=(
                'DEFAULTS = {"path": "reports", "format": "csv", "retries": 3}\n'
                '\n'
                'def load_config(overrides):\n'
                '    config = dict(DEFAULTS)\n'
                '    config.update(overrides)\n'
                '    return config\n'
                '\n'
                'config = load_config({"format": "xlsx"})\n'
                'for key in sorted(config):\n'
                '    print(key, "=", config[key])\n'
                '\n'
                'assert config["format"] == "xlsx" and config["retries"] == 3\n'
                'print("overrides win, defaults fill the gaps")'
            ),
            variant_b='add a required key missing from defaults and raise a clear error when it is absent',
            variant_c='load the overrides from a small text string instead of a dict and print the merge',
            mistakes=[
                "Hard-coding paths and thresholds, so every environment needs a different copy of the script.",
                "Letting a config value be used before it is validated, causing a failure deep inside a run.",
                "Committing secrets such as passwords or tokens into the configuration file.",
            ],
            q1=(
                "Why merge overrides over defaults instead of just reading the config file directly?",
                "Defaults keep the script runnable out of the box while overrides adapt it, without one replacing the other.",
            ),
            homework=(
                "Write `load_config(overrides)` that copies a defaults dict, updates it with the overrides, and "
                "returns the merged settings. Print them sorted by key, change one value, and comment which line "
                "makes the override take precedence."
            ),
            patterns=["def load_config", "update", "print("],
            mapping=(
                "Environment variables and config files are how a script moves from a developer laptop to a scheduler "
                "without hand-editing, and how the same code serves test and production."
            ),
        ),
        142: dict(
            topic="Parameterising paths and dates",
            idea=(
                "Paths and dates are where a script stops being general and becomes tied to one day. Hard-coding "
                "report_2026-10-19.csv guarantees that tomorrow's run writes last week's file, and hard-coding a "
                "directory means the job only works on one machine. The remedy is parameterisation: build the path "
                "from a pattern and the run's inputs, so the same script produces the right name for any day, region "
                "or version. Today you write a small function that fills a path template with a day and a region, and "
                "you check the exact strings it returns. The date is passed in as a value rather than read from the "
                "clock, which is what makes the example deterministic and, more importantly, what makes the real "
                "script testable: when the date is an argument, you can run the job as if it were any day you like. "
                "Parameterising also exposes the things you were assuming. The pattern makes the layout explicit, so "
                "a change from one folder tree to another is one line in one place. And because the same parameters "
                "feed the reader and the writer, input and output stay in step. Keep naming a single decision made in "
                "one function, not sprinkled through the script."
            ),
            code=(
                'PATTERN = "reports/{day}/{region}.csv"\n'
                '\n'
                'def report_path(day, region):\n'
                '    return PATTERN.format(day=day, region=region)\n'
                '\n'
                'print(report_path("2026-10-19", "north"))\n'
                'print(report_path("2026-10-19", "south"))\n'
                '\n'
                'assert report_path("2026-10-19", "north") == "reports/2026-10-19/north.csv"\n'
                'print("paths are built from parameters, never typed by hand")'
            ),
            variant_b='add a version segment to the pattern and print the path for version 2',
            variant_c='pass a different day and confirm only the day segment of the path changes',
            mistakes=[
                "Typing a literal dated filename, so the job overwrites or reuses the wrong day's output.",
                "Reading the current date from the clock inside the path builder, making runs hard to reproduce.",
                "Scattering path construction across the script so the layout exists in several inconsistent places.",
            ],
            q1=(
                "Why pass the date into the path builder instead of reading the clock there?",
                "It keeps the function deterministic and lets you test or replay the job for any date you choose.",
            ),
            homework=(
                "Write `report_path(day, region)` that fills a pattern template and returns a full path string. Print "
                "paths for two regions on the same day, change the day, and comment which line turns inputs into a "
                "path and nothing else."
            ),
            patterns=["def report_path", "format", "print("],
            mapping=(
                "Dated folder trees are standard for scheduled reports and backups; generating them from a pattern "
                "keeps the reader and writer using exactly the same names."
            ),
        ),
        143: dict(
            topic="Scheduling concepts",
            idea=(
                "Scheduling is a vocabulary, and learning it stops you reinventing it badly. A job fires at a time or "
                "an interval; a trigger is the event that starts a run; the run has a window in which it is expected "
                "to finish; a missed run is one that was due but did not happen. Today you model a small cron-like "
                "rule as a dict — minute, hour, weekday — and a due function that answers whether a given moment "
                "matches. The moment is a dict supplied by the caller, not read from a clock, so you can test Monday "
                "at 06:00 and Monday at 06:05 without waiting a week. That separation is the practical point: the "
                "schedule is a predicate over time, and a scheduler is just something that calls the predicate often "
                "and fires when it is true. Knowing this lets you reason about the failure modes people hit — a job "
                "that never fires because the weekday spelling is wrong, two jobs that collide at the same minute, a "
                "job whose window overlaps the one after it. It also frames the difference between a trigger and a "
                "lock: the first decides when to start, the second stops a second copy from starting while the first "
                "is still running."
            ),
            code=(
                'SPEC = {"minute": 0, "hour": 6, "weekdays": ["mon", "tue", "wed", "thu", "fri"]}\n'
                '\n'
                'def due(spec, when):\n'
                '    return (when["minute"] == spec["minute"]\n'
                '            and when["hour"] == spec["hour"]\n'
                '            and when["weekday"] in spec["weekdays"])\n'
                '\n'
                'print("06:00 mon due:", due(SPEC, {"minute": 0, "hour": 6, "weekday": "mon"}))\n'
                'print("06:05 mon due:", due(SPEC, {"minute": 5, "hour": 6, "weekday": "mon"}))\n'
                'print("06:00 sun due:", due(SPEC, {"minute": 0, "hour": 6, "weekday": "sun"}))\n'
                '\n'
                'assert due(SPEC, {"minute": 0, "hour": 6, "weekday": "mon"})\n'
                'assert not due(SPEC, {"minute": 0, "hour": 6, "weekday": "sun"})\n'
                'print("a schedule is a predicate over time")'
            ),
            variant_b='switch the rule to weekends only and print the three due results again',
            variant_c='add a second allowed hour and show that the rule now matches two times a day',
            mistakes=[
                "Mixing up the trigger that starts a run with the lock that prevents overlapping copies.",
                "Writing weekday names inconsistently, so a job silently never matches its intended day.",
                "Assuming a job that is due also ran, when a missed run is a separate thing to detect.",
            ],
            q1=(
                "What is the difference between a trigger and a lock in scheduling?",
                "The trigger decides when a run may start; the lock stops a second copy starting while the first is still running.",
            ),
            homework=(
                "Write `due(spec, when)` that returns True when a moment dict matches a rule dict of minute, hour and "
                "allowed weekdays. Test a matching and a non-matching moment, print both, and comment which line "
                "encodes the weekday condition."
            ),
            patterns=["def due", "return", "print("],
            mapping=(
                "Cron, systemd timers, Windows Task Scheduler and Airflow all provide triggers and locks; knowing the "
                "concepts lets you read their configurations instead of guessing."
            ),
        ),
        144: dict(
            topic="Monitoring outputs",
            idea=(
                "A job that runs is not the same as a job that worked. Monitoring is how you tell the difference when "
                "nobody is watching: you check the output against what a healthy run should look like and raise an "
                "alert when it does not. The simplest useful checks are on the result itself — did the report get "
                "written, does it have rows, is the count within the range we expect, are the totals non-zero when "
                "they should be. Today you write a check_health that inspects a report description and returns a list "
                "of alerts, empty when everything is fine. Returning a list rather than printing or raising keeps the "
                "check as data, so the same logic can feed a log, an email or a dashboard. Two properties make checks "
                "worth having. They must be able to fail: a check that no plausible bad run could trip is decoration. "
                "And they should describe the problem in plain terms — row count below threshold beats assertion "
                "failed — because the person reading the alert at seven in the morning is often not the person who "
                "wrote it. Monitoring closes the loop from the cron fired to the numbers are right. A check that never fires is still "
                "worth reviewing now and then, because thresholds drift as the business changes around them."
            ),
            code=(
                'def check_health(report):\n'
                '    alerts = []\n'
                '    if report["rows"] == 0:\n'
                '        alerts.append("report is empty")\n'
                '    if report["rows"] < report["min_rows"]:\n'
                '        alerts.append("row count below threshold")\n'
                '    return alerts\n'
                '\n'
                'healthy = {"rows": 120, "min_rows": 100}\n'
                'empty = {"rows": 0, "min_rows": 100}\n'
                'print("healthy alerts:", check_health(healthy))\n'
                'print("empty alerts:  ", check_health(empty))\n'
                '\n'
                'assert check_health(healthy) == [] and len(check_health(empty)) == 2\n'
                'print("monitor the result, not just the exit code")'
            ),
            variant_b='add a check that the total is non-zero and print how the empty report scores',
            variant_c='return the alerts joined into one sentence for an email subject and print it',
            mistakes=[
                "Monitoring only whether the process exited, so an empty report passes as healthy.",
                "Writing checks that can never fail, which give false comfort without catching real problems.",
                "Making alert messages technical, so the on-call reader cannot tell what is actually wrong.",
            ],
            q1=(
                "Why return alerts as a list instead of printing or raising inside the check?",
                "A list is data a caller can log, email or count, so one check serves many destinations unchanged.",
            ),
            homework=(
                "Write `check_health(report)` that returns a list of alert strings for an empty report or a row count "
                "below a minimum. Run it on a healthy and an empty report, print both lists, and comment which line "
                "detects the empty output."
            ),
            patterns=["def check_health", "append", "print("],
            mapping=(
                "Freshness and volume checks are the backbone of data-quality monitoring, whether they run in a "
                "dashboard, a monitoring service or a cron job that emails a summary."
            ),
        ),
        145: dict(
            topic="Reconciliation alerts",
            idea=(
                "Reconciliation is the check that the numbers at the end match the numbers at the start. A pipeline "
                "that reads a hundred rows and writes ninety-eight has lost two somewhere, and without reconciliation "
                "nobody notices until someone questions a total. The core comparison is a count, or a sum, between "
                "source and destination, with a tolerance that says how much drift is acceptable before it is a "
                "problem. Today you write a reconcile that compares two counts and returns either a matched message "
                "or a mismatch naming both sides and the difference. Returning a sentence rather than raising an "
                "exception keeps the result inspectable and lets a caller decide whether a small difference is a "
                "warning and a large one is a page. Three details make reconciliation honest. Compare on a key you "
                "trust, not on a total that can hide offsetting errors. Record the tolerance explicitly so close "
                "enough is a decision, not an accident. And reconcile every run, not only the ones that looked "
                "suspicious, because the run that looks fine is exactly the one you stopped checking. This is the "
                "control that turns a script you hope works into one you can vouch for. Tolerance is a judgement "
                "about the data, so it should be written down and revisited, never buried silently in a constant."
            ),
            code=(
                'def reconcile(source_rows, target_rows, tolerance=0):\n'
                '    diff = source_rows - target_rows\n'
                '    if abs(diff) <= tolerance:\n'
                '        return "matched: %d rows" % source_rows\n'
                '    return "mismatch: source %d, target %d, diff %d" % (\n'
                '        source_rows, target_rows, diff)\n'
                '\n'
                'print(reconcile(100, 100))\n'
                'print(reconcile(100, 98))\n'
                'print(reconcile(100, 99, tolerance=1))\n'
                '\n'
                'assert reconcile(100, 100).startswith("matched")\n'
                'assert "diff 2" in reconcile(100, 98)\n'
                'print("compare the ends of the pipeline every run")'
            ),
            variant_b='compare sums instead of counts and print the mismatch when a value is dropped',
            variant_c='allow a small percentage tolerance and show a one-row drift passing as matched',
            mistakes=[
                "Comparing a total that can hide compensating errors, instead of a trusted row count or key set.",
                "Leaving the tolerance implicit, so nobody agrees what counts as an acceptable difference.",
                "Reconciling only when a run looks wrong, which skips exactly the silent failures you need to catch.",
            ],
            q1=(
                "Why reconcile every run rather than only the suspicious ones?",
                "A run that looks fine can still lose rows silently, and routine reconciliation is what surfaces it early.",
            ),
            homework=(
                "Write `reconcile(source_rows, target_rows, tolerance=0)` that returns a matched or mismatch sentence "
                "naming both counts and the difference. Run it on an equal pair and a drifted pair, print both, and "
                "comment which line decides when a difference is acceptable."
            ),
            patterns=["def reconcile", "diff", "print("],
            mapping=(
                "Financial and operational pipelines run row-count and control-total checks after every load; "
                "reconciliation is how an accountant or analyst gains confidence in an automated report."
            ),
        ),
        146: dict(
            topic="Versioning reports",
            idea=(
                "Reports are evidence, and evidence should be dated and kept. Versioning means each run writes a new, "
                "clearly numbered output rather than overwriting the last one, so a question about last Tuesday's "
                "numbers can still be answered. Today you write a small next_version that derives the version from "
                "the history of filenames so far, and you append the new name to that history. The version is "
                "computed, never typed, which is what stops two runs from claiming to be version two. This pattern "
                "shows up everywhere: dated exports in a folder, numbered snapshots, build numbers. It also changes "
                "how you think about the output file: it is not a single living document that gets rewritten, but a "
                "series of immutable artifacts, one per run. That makes recovery easy, because the previous good "
                "version is still there, and it makes the run's product auditable, because you can see what each run "
                "actually produced. Two cautions. Keep enough history to be useful but prune it on a policy, or the "
                "folder grows without bound. And put the version in the name deterministically, so a person or a "
                "script can find the latest without guessing. A version derived from the folder is also "
                "self-describing, so a reader needs no separate index to know what exists."
            ),
            code=(
                'def next_version(history):\n'
                '    return "v" + str(len(history) + 1)\n'
                '\n'
                'history = ["report_v1.csv"]\n'
                'version = next_version(history)\n'
                'history.append("report_" + version + ".csv")\n'
                '\n'
                'print("latest: ", history[-1])\n'
                'print("history:", history)\n'
                '\n'
                'assert history == ["report_v1.csv", "report_v2.csv"]\n'
                'print("each run writes a new version, older ones stay")'
            ),
            variant_b='base the version on the number of existing files and print v3 after adding one more',
            variant_c='include the run id in the filename and print a name that names both run and version',
            mistakes=[
                "Overwriting the same report each run, so yesterday's numbers are gone when you need evidence.",
                "Typing the version number by hand, so two runs can both claim to be version two.",
                "Keeping every version forever with no retention policy, until the folder is unmanageable.",
            ],
            q1=(
                "Why keep each run's report as a separate version rather than overwriting one file?",
                "It preserves evidence of each run for auditing and recovery, and makes the latest version findable by name.",
            ),
            homework=(
                "Write `next_version(history)` that returns the next version string derived from the length of a "
                "filename list. Add two versions in turn, print the history, and comment which line computes the "
                "version instead of hard-coding it."
            ),
            patterns=["def next_version", "len(", "print("],
            mapping=(
                "Dated or numbered artifacts are standard for reports and backups; a retention policy keeps the "
                "history useful without letting it grow forever."
            ),
        ),
        147: dict(
            topic="Runbooks and recovery",
            idea=(
                "A runbook is the instructions you follow when the automation stops, written while you are calm so you "
                "do not have to improvise while you are not. It maps a symptom to a diagnosis and an action: file "
                "locked, wait and retry; input missing, restore from backup; report empty, page the owner. Today you "
                "model that mapping as a dict and a recover function that returns the prescribed step for a given "
                "failure, with a sensible answer for a failure the book has never seen. Keeping the runbook as data "
                "means it can be reviewed, tested and improved, and the same entries can later become automatic "
                "recovery where it is safe to automate. The deeper point is that a runbook and the code should agree. "
                "Every failure the script can raise should have a line in the book, and every line in the book should "
                "name a failure the script can actually produce; when they drift apart, the on-call engineer follows a "
                "script that no longer matches reality. Recovery is easier when the run was built to be recoverable: "
                "idempotent, logged and versioned means the remedy is usually fix the input and run it again rather "
                "than a manual repair."
            ),
            code=(
                'RUNBOOK = {\n'
                '    "locked": "wait and retry",\n'
                '    "missing": "restore from backup",\n'
                '    "empty": "page the owner",\n'
                '}\n'
                '\n'
                'def recover(failure):\n'
                '    step = RUNBOOK.get(failure, "no known recovery, escalate")\n'
                '    return "%s -> %s" % (failure, step)\n'
                '\n'
                'print(recover("locked"))\n'
                'print(recover("missing"))\n'
                'print(recover("corrupt"))\n'
                '\n'
                'assert recover("locked") == "locked -> wait and retry"\n'
                'assert "escalate" in recover("corrupt")\n'
                'print("a runbook maps a symptom to a calm action")'
            ),
            variant_b='add a "denied" entry that says to check credentials, and print the recovery step',
            variant_c='have recover fall back to a default page when the failure is not in the runbook',
            mistakes=[
                "Leaving the recovery procedure in someone's head, so a holiday turns a small failure into an outage.",
                "Letting the runbook drift from the failures the code actually raises, so it leads the reader astray.",
                "Writing steps that assume a manual repair the run was never designed to survive.",
            ],
            q1=(
                "Why keep the runbook in sync with the failures the script can actually raise?",
                "Otherwise the on-call engineer follows instructions that no longer match reality and wastes the incident window.",
            ),
            homework=(
                "Write `recover(failure)` that looks a failure up in a runbook dict and returns the prescribed step, "
                "falling back to a default escalation for unknown failures. Print three lookups including one unknown, "
                "and comment which line supplies the safe default."
            ),
            patterns=["def recover", "get(", "print("],
            mapping=(
                "Operations teams keep runbooks next to their alerts so anyone on call can act; automation can even "
                "execute the safe steps itself when the recovery is deterministic."
            ),
        ),
        148: dict(
            topic="Turning incidents into checks",
            idea=(
                "An incident is expensive, and its one lasting value is the check it leaves behind. Every time a run "
                "fails in a new way, the response is not just to fix it but to ask what would have caught it sooner, "
                "and to add that check so the same class of failure is automatic next time. Today you take a list of "
                "past incidents, each with what happened, and derive the checks they should have become — a minimum "
                "row count, a maximum file age, a required column. This is the loop that makes automation improve "
                "over time rather than merely persist: the system accumulates knowledge, encoded as tests, instead of "
                "relying on the same person to remember. Two habits make it work. Make each check small and specific, "
                "so a failure points at one cause, and cheap enough to run on every job. And keep the reasoning with "
                "the check — a short note of what incident it came from — so a future reader does not delete it as "
                "mysterious. The goal is that yesterday's surprise becomes today's alert and tomorrow's non-event. "
                "Reliability is not the absence of failures; it is the slow accumulation of checks that catch them "
                "early."
            ),
            code=(
                'INCIDENTS = [\n'
                '    {"what": "empty report", "check": "min_rows"},\n'
                '    {"what": "stale input", "check": "max_age_days"},\n'
                '    {"what": "missing column", "check": "required_columns"},\n'
                ']\n'
                '\n'
                'def checks_from(incidents):\n'
                '    return [incident["check"] for incident in incidents]\n'
                '\n'
                'checks = checks_from(INCIDENTS)\n'
                'for check in checks:\n'
                '    print("added check:", check)\n'
                '\n'
                'assert "min_rows" in checks and len(checks) == 3\n'
                'print("every incident becomes a permanent check")'
            ),
            variant_b='attach the incident reason to each check and print the reason beside it',
            variant_c='filter to only the checks that have not been implemented yet and print those',
            mistakes=[
                "Fixing an incident without adding the check that would catch the next one automatically.",
                "Writing a check so broad it fires on healthy runs, so people learn to ignore the alerts.",
                "Losing the reason a check exists, so a later reader deletes it as unexplained noise.",
            ],
            q1=(
                "What should happen to every new incident after it is fixed?",
                "It should turn into a small, specific check so the same class of failure is caught automatically next time.",
            ),
            homework=(
                "Write `checks_from(incidents)` that takes a list of incident dicts and returns the name of the check "
                "each one should become. Print the checks from three incidents, and comment which line turns history "
                "into a permanent test."
            ),
            patterns=["def checks_from", "for ", "print("],
            mapping=(
                "Post-incident reviews in operations end with action items that become alerts or tests; the durable "
                "output of an incident is the check that prevents a repeat."
            ),
        ),
        149: dict(
            topic="Review: automation and reliability checklist",
            idea=(
                "Today is the review, and it is deliberately a checklist rather than new ground: can this run be "
                "repeated, rehearsed, observed, retried, configured, parameterised, scheduled, monitored, reconciled, "
                "versioned and recovered? Each of those is a property you built in the preceding fortnight, and "
                "together they are what separates a script that happens to work on your machine from an automation "
                "someone can trust at six in the morning. The exercise today is to hold a state — a set of booleans, "
                "one per property — and have an audit list the ones that are missing. The empty list is the goal, and "
                "anything on it is the next thing to fix, which is a more useful answer than a vague sense of unease. "
                "Two things are worth noting about a checklist of this kind. It is honest only if each item is backed "
                "by something concrete; ticking logging without a log a stranger could read is self-deception. And it "
                "is a floor, not a ceiling: a run that passes every box is safe to schedule, but the checks inside it "
                "will keep growing as incidents teach you what else to look for. Readiness is a state you can "
                "measure, and today you measure it."
            ),
            code=(
                'CHECKLIST = ["idempotent", "dry_run", "logging", "error_per_row",\n'
                '             "retry", "config", "alerts", "reconcile", "versioned"]\n'
                '\n'
                'def audit(state):\n'
                '    return [item for item in CHECKLIST if not state.get(item)]\n'
                '\n'
                'state = {item: True for item in CHECKLIST}\n'
                'state["dry_run"] = False\n'
                'missing = audit(state)\n'
                '\n'
                'print("checklist size:", len(CHECKLIST))\n'
                'print("missing:", missing)\n'
                '\n'
                'assert missing == ["dry_run"]\n'
                'print("automation is ready when nothing is missing")'
            ),
            variant_b='mark three properties false and print the missing list in checklist order',
            variant_c='count how many checks pass and print a percentage of readiness',
            mistakes=[
                "Ticking a checklist item without the concrete artifact that makes it true.",
                "Treating the checklist as a finish line rather than a floor that grows with each incident.",
                "Reviewing readiness once at handover instead of after every change to the job.",
            ],
            q1=(
                "Why is an audit that lists missing properties more useful than a general sense of unease?",
                "It names the next concrete thing to fix and lets you measure readiness rather than guess at it.",
            ),
            homework=(
                "Write `audit(state)` that takes a dict of readiness flags and returns the checklist items that are "
                "still missing. Start from an all-true state, set two flags false, print the missing list, and "
                "comment which line defines what ready means."
            ),
            patterns=["def audit", "for ", "print("],
            mapping=(
                "Handover documents and production-readiness reviews use exactly this kind of checklist to decide "
                "whether a job may run unattended."
            ),
        ),
    },
)
