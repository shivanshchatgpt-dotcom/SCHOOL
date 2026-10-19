PHASE = (
    "Robustness, Errors and Logging",
    "Make unattended scripts fail safely by classifying errors, bounding retries, "
    "logging structured outcomes, alerting on summaries and reconciling what a run "
    "claims against what actually exists.",
    {
        135: dict(
            topic="Orientation: things go wrong",
            idea=(
                "Automation is written to run unattended, so the interesting question is not whether things will "
                "go wrong but what the script does when they do. A file is missing, an API returns a 500, one "
                "record has a malformed date, the disk fills halfway through a write: each is normal, and each can "
                "be handled if it is detected at the right level. The first habit is to stop treating failure as "
                "an exception to the happy path and start treating it as a value the script can inspect, count and "
                "report. That means a run should be able to answer three questions: what failed, what did we do "
                "about it, and what is still safe to retry. The second habit is to keep a boundary around each unit "
                "of work so one bad item does not destroy the evidence for the other ninety-nine. The third is to "
                "leave a trail that another person or program can read without rerunning the job. Today you map the "
                "failure modes of a tiny pipeline and print a structured outcome for each run, without touching a "
                "real disk, clock or network. The shapes you build here — status, failing step, completed work — "
                "are the vocabulary for the rest of the phase."
            ),
            code=(
                'def run_job(steps):\n'
                '    completed = []\n'
                '    for name, ok in steps:\n'
                '        if not ok:\n'
                '            return {"status": "failed", "completed": completed, "failed_at": name}\n'
                '        completed.append(name)\n'
                '    return {"status": "ok", "completed": completed, "failed_at": None}\n'
                '\n'
                'jobs = {\n'
                '    "broken": [("load", True), ("clean", True), ("write", False)],\n'
                '    "healthy": [("load", True), ("clean", True), ("write", True)],\n'
                '}\n'
                'for name in sorted(jobs):\n'
                '    result = run_job(jobs[name])\n'
                '    print(name, "->", result["status"], "failed_at:", result["failed_at"])\n'
                '\n'
                'assert run_job(jobs["broken"])["failed_at"] == "write"\n'
                'assert run_job(jobs["healthy"])["completed"] == ["load", "clean", "write"]\n'
                'print("a failure is data, not a crash")'
            ),
            variant_b="add a third job that fails on its first step and confirm the completed list is empty",
            variant_c="return the number of completed steps and print it next to the status for all three jobs",
            mistakes=[
                "Assuming the happy path is the only path and discovering the rest during an incident.",
                "Recording only a boolean instead of which step failed and what had already completed.",
                "Letting one bad run destroy the evidence needed to understand the other runs.",
            ],
            q1=(
                "Why treat a failure as data rather than as an exceptional crash?",
                "A recorded failure can be counted, reported and retried deliberately, while a crash loses the information about what was already completed.",
            ),
            homework=(
                "Write `def run_job(steps)` that takes a list of `(name, ok)` pairs, stops at the first failure "
                "and returns a dict with status, completed steps and the failing step. Run it on one failing and "
                "one successful plan, print both results, and comment which return value tells a scheduler where "
                "the run stopped."
            ),
            patterns=["def run_job", "failed_at", "print("],
            mapping=(
                "Cron, systemd timers and CI runners all need a status and a failing step; production job "
                "records store exactly these fields so an operator can see where a run stopped."
            ),
        ),
        136: dict(
            topic="An exception taxonomy",
            idea=(
                "Errors are not interchangeable, and the first useful act after catching one is to decide which "
                "family it belongs to. A transient error, such as a timeout or a refused connection, may succeed on "
                "a later attempt. A data error, such as a malformed integer or a missing key, will fail identically "
                "forever until the input or the code changes. An environment error, such as a missing directory or "
                "denied permission, needs an operator to change the machine. A programming error, such as a type "
                "mistake or an index bug, needs a developer and should never be retried. The classification changes "
                "the response: retry transients with a limit, quarantine data errors with the offending payload, "
                "fail fast on environment errors with a clear message, and let programming errors crash loudly in "
                "development. Mixing the families is how scripts end up retrying a typo ten times or hiding a bug "
                "behind a cheerful warning. Today you write a classifier over error names and count each family, an "
                "in-memory exercise that mirrors the branches of a production handler. The point is not the exact "
                "mapping but the discipline of asking what kind of failure this is before choosing what to do. Use "
                "it as a small decision table for every handler you write."
            ),
            code=(
                'def classify(error):\n'
                '    if error in {"TimeoutError", "ConnectionError"}:\n'
                '        return "transient"\n'
                '    if error in {"ValueError", "KeyError"}:\n'
                '        return "data"\n'
                '    if error in {"PermissionError", "FileNotFoundError"}:\n'
                '        return "environment"\n'
                '    return "programming"\n'
                '\n'
                'errors = ["TimeoutError", "ValueError", "PermissionError", "TypeError", "TimeoutError"]\n'
                'counts = {}\n'
                'for error in errors:\n'
                '    kind = classify(error)\n'
                '    counts[kind] = counts.get(kind, 0) + 1\n'
                '    print(f"{error:18} -> {kind}")\n'
                'print("counts:", dict(sorted(counts.items())))\n'
                '\n'
                'assert counts == {"transient": 2, "data": 1, "environment": 1, "programming": 1}\n'
                'print("classify before deciding how to respond")'
            ),
            variant_b="add a fourth family for authentication errors and decide whether it should be retried",
            variant_c="make the classifier return a suggested action such as retry, quarantine or fail fast",
            mistakes=[
                "Retrying every exception, which turns permanent data errors into wasted attempts.",
                "Catching a broad base class and losing the distinction between data and programming faults.",
                "Treating a permission failure as transient when only an operator can change it.",
            ],
            q1=(
                "Why should a programming error never be retried?",
                "The same code path will fail identically every time, so retries only delay the crash and hide the bug behind noise.",
            ),
            homework=(
                "Write `def classify(error_name)` that maps at least six error names to the families transient, "
                "data, environment and programming, then `def count_families(names)` that returns a count per "
                "family. Run it on a mixed list, print the classification and the counts, and comment why a "
                "programming error should not be retried."
            ),
            patterns=["def classify", "def count_families", "print("],
            mapping=(
                "Libraries such as urllib3 expose retry policies by error class, and HTTP clients distinguish "
                "retryable status codes from permanent ones; the taxonomy is the same decision at a lower level."
            ),
        ),
        137: dict(
            topic="Isolating failures per item",
            idea=(
                "A batch job has a natural boundary around each item, and that boundary is the cheapest place to "
                "contain damage. If one row of a CSV cannot be parsed, the correct outcome is usually that row "
                "failed and the other rows succeeded, not that the whole run aborts. Isolating failures means "
                "wrapping the per-item work in a narrow handler, recording the item identity and the reason, and "
                "continuing with the next item. Two cautions keep this from becoming a way to hide problems. The "
                "handler should catch the errors you expect from bad input, not every exception, because a "
                "programming bug inside the item function must still surface. And the run must end with a summary "
                "that makes failures impossible to miss: counts of ok, failed and skipped, plus enough log context "
                "to reproduce each failure. A summary that says only \"done\" after ninety-nine failures is worse "
                "than a crash, because it looks successful to a scheduler. Today you build that per-item boundary "
                "and print both the log records and the totals. The same shape scales from fifteen rows to fifteen "
                "million; only the storage of the log changes. The goal is containment without concealment: "
                "continue the batch, but make every failure visible and attributable."
            ),
            code=(
                'def run_items(items):\n'
                '    log = []\n'
                '    summary = {"ok": 0, "failed": 0}\n'
                '    for item in items:\n'
                '        try:\n'
                '            value = int(item)\n'
                '        except ValueError as error:\n'
                '            summary["failed"] += 1\n'
                '            log.append({"item": item, "outcome": "failed", "error": str(error)})\n'
                '            continue\n'
                '        summary["ok"] += 1\n'
                '        log.append({"item": item, "outcome": "ok", "value": value})\n'
                '    return summary, log\n'
                '\n'
                'summary, log = run_items(["4", "oops", "9"])\n'
                'for record in log:\n'
                '    print(record)\n'
                'print("summary:", summary)\n'
                '\n'
                'assert summary == {"ok": 2, "failed": 1}\n'
                'assert [r["outcome"] for r in log] == ["ok", "failed", "ok"]\n'
                'print("one bad item does not stop the batch")'
            ),
            variant_b="add an empty-string item that is skipped rather than failed and count it separately",
            variant_c="catch both ValueError and KeyError and record the error type in each log record",
            mistakes=[
                "Aborting the whole batch on the first malformed item instead of isolating it.",
                "Catching every exception, so a real bug in the item function looks like bad input.",
                "Finishing with a bare \"done\" message that hides how many items failed.",
            ],
            q1=(
                "What belongs in the per-item log record besides the error text?",
                "The item identity, the outcome and enough context to reproduce the failure, so the bad item can be inspected or replayed.",
            ),
            homework=(
                "Write `def run_items(items)` that converts each item to an integer inside its own try block, "
                "records ok and failed counts, and returns the summary plus a list of log dictionaries with item, "
                "outcome and error. Run it on two good items and one bad item, print every record and the "
                "summary, and comment which line keeps the batch alive."
            ),
            patterns=["def run_items", "except ValueError", "print("],
            mapping=(
                "Batch ETL tools and queue consumers isolate failures per message and emit a summary at the end; "
                "the per-item boundary is what keeps one poison message from stalling a queue."
            ),
        ),
        138: dict(
            topic="Retry with backoff",
            idea=(
                "Retries are a bet that a failure was temporary, and like any bet they need a limit. The naive loop "
                "that tries again immediately, forever, turns a brief outage into a self-inflicted denial of "
                "service and hides a permanent error behind a spinning process. The standard pattern is a bounded "
                "number of attempts with exponential backoff: wait one second, then two, then four, and stop at a "
                "maximum. The delay gives the dependency time to recover and spreads pressure from many clients. "
                "Jitter, a small random offset, prevents synchronized clients from retrying in lockstep, though here "
                "you will model delays as plain integers so the lesson stays deterministic. Just as important is "
                "deciding what may be retried: a timeout is a candidate, a validation error is not, and a write "
                "that is not idempotent must not be repeated blindly. The retry policy belongs in one place, "
                "visible and testable, not scattered through the call stack. Today you represent a run as a list of "
                "attempt outcomes and derive the delay schedule from it, then print the delays and the total wait. "
                "That list is exactly what a scheduler or a test harness would record in real life. A policy that "
                "cannot explain its own limits is not a policy."
            ),
            code=(
                'def attempt_plan(outcomes, base=1, limit=5):\n'
                '    delays = []\n'
                '    for attempt, ok in enumerate(outcomes[:limit], start=1):\n'
                '        if ok:\n'
                '            break\n'
                '        delays.append(base * (2 ** (attempt - 1)))\n'
                '    return delays\n'
                '\n'
                'outcomes = [False, False, True]\n'
                'delays = attempt_plan(outcomes)\n'
                'print("outcomes:", outcomes)\n'
                'print("delays:", delays)\n'
                'print("total wait:", sum(delays))\n'
                'print("capped plan:", attempt_plan([False] * 8))\n'
                '\n'
                'assert delays == [1, 2]\n'
                'assert attempt_plan([False] * 8) == [1, 2, 4, 8, 16]\n'
                'print("retries stop at success or at the attempt limit")'
            ),
            variant_b="change the base delay to two seconds and print how the total wait changes",
            variant_c="stop after three attempts even when the outcomes list is longer and print the cap",
            mistakes=[
                "Retrying forever with no attempt limit, which turns an outage into a traffic flood.",
                "Using a constant delay so every client retries in lockstep and re-creates the spike.",
                "Retrying a validation error or a non-idempotent write that should fail once and stay failed.",
            ],
            q1=(
                "Why does exponential backoff include a maximum attempt count?",
                "The limit bounds the time and load a run can spend on a permanent failure, leaving room to report and escalate instead of spinning.",
            ),
            homework=(
                "Write `def attempt_plan(outcomes, base=1)` that takes a list of booleans and returns the integer "
                "delays before each retry, stopping at the first success and capping at five attempts. Print the "
                "outcomes, the delays and the total wait, then comment which line makes the policy bounded."
            ),
            patterns=["def attempt_plan", "delays", "print("],
            mapping=(
                "HTTP clients such as urllib3 and cloud SDKs ship exponential backoff with jitter; the same "
                "policy should be visible in the job code rather than hidden in every call site."
            ),
        ),
        139: dict(
            topic="A circuit breaker",
            idea=(
                "Retrying every call to a service that is already down makes an outage worse. A circuit breaker "
                "adds a small state machine in front of the dependency: while calls succeed it stays closed and "
                "traffic flows; after a threshold of consecutive failures it opens and rejects calls immediately, "
                "giving the dependency room to recover; after a cooldown it moves to half-open, lets a probe "
                "through, and closes again if the probe succeeds. The value is not only speed. Fast rejection "
                "protects your own workers from piling up timeouts, makes the failure visible in metrics, and gives "
                "the run a clear reason to stop instead of burning its whole time budget. The breaker needs a "
                "threshold, a cooldown and a single probe policy, and it must be shared by the callers that hit the "
                "same dependency, otherwise each worker learns the outage separately. There is a real trade-off "
                "between opening too eagerly and waiting too long; the right numbers come from measuring the "
                "dependency, not from taste. Today you model the breaker with counters and a status string, run a "
                "fixed sequence of outcomes through it, and print each transition. No real service, no clock, just "
                "the state machine that decides whether a call is attempted."
            ),
            code=(
                'class Breaker:\n'
                '    def __init__(self, threshold=3):\n'
                '        self.threshold = threshold\n'
                '        self.failures = 0\n'
                '        self.status = "closed"\n'
                '\n'
                '    def call(self, ok):\n'
                '        if self.status == "open":\n'
                '            return "rejected"\n'
                '        if ok:\n'
                '            self.failures = 0\n'
                '            self.status = "closed"\n'
                '            return "ok"\n'
                '        self.failures += 1\n'
                '        if self.failures >= self.threshold:\n'
                '            self.status = "open"\n'
                '        return "failed"\n'
                '\n'
                'breaker = Breaker()\n'
                'for ok in [False, False, False, True, False]:\n'
                '    before = breaker.status\n'
                '    decision = breaker.call(ok)\n'
                '    print(before, "->", decision, "->", breaker.status)\n'
                '\n'
                'assert breaker.status == "open"\n'
                'assert breaker.call(True) == "rejected"\n'
                'print("the breaker fails fast while the dependency is down")'
            ),
            variant_b="raise the threshold to four and print how many calls fit before the circuit opens",
            variant_c="add a half-open status that allows exactly one probe call after the open state",
            mistakes=[
                "Keeping a separate breaker per worker, so the whole fleet has to learn the outage independently.",
                "Opening and closing on a single failure, which makes the breaker flap instead of protecting anything.",
                "Rejecting calls forever with no probe path, so recovery is never detected.",
            ],
            q1=(
                "What does an open circuit breaker return, and why is that better than another retry?",
                "It rejects the call immediately, which protects the dependency and stops the caller from spending its budget on requests that cannot succeed.",
            ),
            homework=(
                "Write `def breaker_calls(outcomes, threshold=3)` that simulates a circuit breaker over a list of "
                "booleans and returns a list of `(status_before, decision)` pairs. Run it with three failures "
                "followed by a success, print the transitions, and comment which line opens the circuit."
            ),
            patterns=["def breaker_calls", "open", "print("],
            mapping=(
                "Resilience libraries such as pybreaker and the circuit breaking features of service proxies use "
                "this exact closed, open and half-open model in front of remote dependencies."
            ),
        ),
        140: dict(
            topic="Log levels",
            idea=(
                "Logs exist for the person who has to understand a run they did not watch, and log levels are the "
                "contract about how much detail that person gets. DEBUG explains internal decisions and is usually "
                "off in production; INFO records normal milestones such as a run starting or an item completing; "
                "WARNING says something is degraded but the run continues; ERROR says a unit of work failed. The "
                "level is not a measure of how upset the author feels, it is a filter that lets the same code serve "
                "a developer tracing a bug and an operator watching a dashboard. The threshold should be "
                "configurable, with INFO in normal operation and DEBUG enabled for a specific investigation. Two "
                "failure modes dominate. Logging everything at INFO creates noise that hides the one line that "
                "matters, and logging nothing at the point of failure leaves an alert with no context. A good rule "
                "is to log decisions and outcomes rather than every variable, and to include the identifiers needed "
                "to find the affected item. Today you filter an in-memory list of level-tagged records through a "
                "threshold and print what survives. The mechanics are trivial; choosing the level is the skill. "
                "Choose the threshold for the reader, not for the author."
            ),
            code=(
                'LEVELS = {"DEBUG": 10, "INFO": 20, "WARNING": 30, "ERROR": 40}\n'
                'records = [\n'
                '    ("DEBUG", "cache hit"),\n'
                '    ("INFO", "run started"),\n'
                '    ("WARNING", "item was slow"),\n'
                '    ("ERROR", "write failed"),\n'
                '    ("INFO", "run finished"),\n'
                ']\n'
                '\n'
                'def emit(records, threshold):\n'
                '    return [(level, message) for level, message in records if LEVELS[level] >= threshold]\n'
                '\n'
                'for threshold in (LEVELS["INFO"], LEVELS["WARNING"]):\n'
                '    kept = emit(records, threshold)\n'
                '    print("threshold:", threshold, "kept:", len(kept))\n'
                '    for level, message in kept:\n'
                '        print(" ", level, message)\n'
                '\n'
                'assert [level for level, _ in emit(records, LEVELS["WARNING"])] == ["WARNING", "ERROR"]\n'
                'print("the threshold decides what a reader sees")'
            ),
            variant_b="request DEBUG for the run and confirm all five records are printed",
            variant_c="count records per level before filtering and print the counts",
            mistakes=[
                "Logging everything at INFO, so the signal is buried in routine noise.",
                "Logging a failure at DEBUG, so the normal production threshold hides it completely.",
                "Using levels as emotional labels instead of a consistent filter contract.",
            ],
            q1=(
                "What should WARNING mean compared with ERROR?",
                "WARNING means the run is degraded but can continue; ERROR means a unit of work failed and someone may need to act.",
            ),
            homework=(
                "Write `def emit(records, threshold)` that filters `(level, message)` records at or above a "
                "numeric threshold and returns the kept records. Use DEBUG=10, INFO=20, WARNING=30 and ERROR=40, "
                "run it twice with different thresholds, print what survives each time, and comment which line "
                "makes the threshold configurable."
            ),
            patterns=["def emit", "DEBUG", "print("],
            mapping=(
                "The standard library logging module, systemd journal priorities and cloud log levels all share "
                "the same ordered scale, so a threshold chosen here maps directly to production configuration."
            ),
        ),
        141: dict(
            topic="Structured logs",
            idea=(
                "Plain log strings are comfortable for humans and painful for programs. When every line has a "
                "different shape, a dashboard cannot count failures by item without a pile of brittle regular "
                "expressions. Structured logs fix that by emitting records with stable keys: an event name, the "
                "item identifier, the attempt number, the outcome, the duration and the error kind. The message "
                "becomes a field rather than the whole record, so one query can find every failed attempt for a "
                "given item across a whole day. The schema should be small and documented, and it should use "
                "consistent names and types; a field that is sometimes an integer and sometimes the string "
                "\"unknown\" will break the query that matters. Correlation identifiers tie the records of one run "
                "together, which is essential when several runs overlap. Structured logging also forces a decision "
                "about sensitive data: never log passwords, tokens or full customer records, and prefer identifiers "
                "over payloads. Today you build log dictionaries for two attempts and print them as sorted JSON, "
                "the same shape a log pipeline would ingest. The output is deliberately boring and stable, because "
                "boring and stable is exactly what makes it queryable. Treat the schema as an interface with "
                "consumers you cannot see."
            ),
            code=(
                'import json\n'
                '\n'
                'def log_record(item, attempt, outcome, **fields):\n'
                '    record = {"event": "item.processed", "item": item, "attempt": attempt, "outcome": outcome}\n'
                '    record.update(fields)\n'
                '    return record\n'
                '\n'
                'records = [\n'
                '    log_record("a.csv", 1, "ok", duration_ms=12),\n'
                '    log_record("b.csv", 2, "failed", error="timeout"),\n'
                ']\n'
                'for record in records:\n'
                '    print(json.dumps(record, sort_keys=True))\n'
                '\n'
                'failures = [r for r in records if r["outcome"] == "failed"]\n'
                'assert len(failures) == 1 and failures[0]["item"] == "b.csv"\n'
                'assert records[1]["error"] == "timeout"\n'
                'print("stable keys let a query find every failure")'
            ),
            variant_b="add a run identifier to every record and show that both records share the same value",
            variant_c="add a duration field to both records and print the record with the larger duration",
            mistakes=[
                "Building log lines by string concatenation, so every field needs a custom parser later.",
                "Changing a field type between records, which breaks the query that groups by it.",
                "Logging full payloads or credentials instead of identifiers and redacted summaries.",
            ],
            q1=(
                "Why is sorted JSON output useful for a structured log example?",
                "Sorting keys makes the record stable across runs, so output can be compared and assertions can target exact fields without depending on insertion order.",
            ),
            homework=(
                "Write `def log_record(item, attempt, outcome, **fields)` that returns a dictionary with event, "
                "item, attempt and outcome plus any extra fields, and `def dump(records)` that prints each record "
                "as sorted JSON. Build one success and one failure, print both lines, and comment which key a "
                "query would use to find failures."
            ),
            patterns=["def log_record", "json.dumps", "print("],
            mapping=(
                "Log aggregators index JSON fields, so structured records support filters such as outcome=failed "
                "and group-by item; this is the schema contract between an automation and its dashboards."
            ),
        ),
        142: dict(
            topic="Alerts from a summary",
            idea=(
                "An alert is a promise that someone will act, so it should be derived from the run summary rather "
                "than from every log line. The summary holds the numbers that matter: how many items succeeded, "
                "failed or were skipped, how long the run took, how many retries happened. Alert rules compare "
                "those numbers with thresholds and produce a small set of messages with a severity and an owner. "
                "The usual failure is alerting on symptoms nobody can fix, or firing so often that the channel is "
                "muted; both destroy trust faster than a missing alert. Good rules are specific, actionable and "
                "tied to a runbook: \"more than zero items failed\" is a page, \"a run took longer than sixty "
                "seconds\" may be a warning, \"one retry occurred\" is probably just a log line. Deduplication and "
                "grouping keep a single incident from producing a hundred identical pages, and a resolution notice "
                "closes the loop. Alerts should also carry the identifiers needed to find the run, not just a vague "
                "description. Today you evaluate a fixed summary against a short rule list and print the resulting "
                "alerts. The exercise is deterministic, but the design question is the real one: which numbers "
                "deserve to wake someone up?"
            ),
            code=(
                'def alerts_from(summary, rules):\n'
                '    alerts = []\n'
                '    for rule in rules:\n'
                '        actual = summary.get(rule["metric"], 0)\n'
                '        if rule["op"] == ">" and actual > rule["limit"]:\n'
                '            alerts.append({\n'
                '                "severity": rule["severity"],\n'
                '                "message": rule["message"],\n'
                '                "runbook": rule["runbook"],\n'
                '            })\n'
                '    return alerts\n'
                '\n'
                'summary = {"ok": 48, "failed": 2, "duration_s": 95}\n'
                'rules = [\n'
                '    {"metric": "failed", "op": ">", "limit": 0, "severity": "page", "message": "items failed", "runbook": "failed-items"},\n'
                '    {"metric": "duration_s", "op": ">", "limit": 60, "severity": "warn", "message": "run is slow", "runbook": "slow-run"},\n'
                '    {"metric": "failed", "op": ">", "limit": 10, "severity": "page", "message": "mass failure", "runbook": "outage"},\n'
                ']\n'
                'alerts = alerts_from(summary, rules)\n'
                'for alert in alerts:\n'
                '    print(alert["severity"], "-", alert["message"], "-", alert["runbook"])\n'
                '\n'
                'assert [a["severity"] for a in alerts] == ["page", "warn"]\n'
                'print("alerts are rules over the run summary")'
            ),
            variant_b="add a rule for skipped items and show that it stays quiet when the count is zero",
            variant_c="raise the failure limit to ten and confirm the mass-failure alert disappears",
            mistakes=[
                "Alerting on every log line instead of on the summary numbers that indicate impact.",
                "Firing repeatedly without deduplication, so one incident floods the channel.",
                "Sending an alert without a runbook or run identifier, leaving the responder with no next step.",
            ],
            q1=(
                "Why should an alert be derived from the run summary?",
                "The summary holds impact-level counts that are stable and actionable, while raw log lines are noisy and often describe harmless detail.",
            ),
            homework=(
                "Write `def alerts_from(summary, rules)` that evaluates a list of rule dictionaries with a metric, "
                "an operator, a limit and a severity, and returns the matching alert dictionaries. Test it on a "
                "summary with two failures and a slow duration, print each alert, and comment why an alert should "
                "include a runbook link."
            ),
            patterns=["def alerts_from", "severity", "print("],
            mapping=(
                "Monitoring systems such as Prometheus Alertmanager evaluate rules over metrics and route them by "
                "severity; the run summary is the smallest version of that same pipeline."
            ),
        ),
        143: dict(
            topic="Reconciliation checks",
            idea=(
                "Automation changes state, and reconciliation is the habit of checking that the state you intended "
                "is the state that exists. After copying files you can compare the source and destination counts; "
                "after loading rows you can compare the expected keys with the keys the database reports; after a "
                "migration you can compare old and new totals. The comparison is usually expressed as three sets: "
                "missing (expected but absent), extra (present but unexpected) and mismatched (present in both but "
                "with different values). Those three words are more useful than a single \"failed\" flag because "
                "they point at different repairs: missing means the work did not finish, extra means something "
                "wrote more than it should, and mismatched means the two sides disagree about content. "
                "Reconciliation should run as part of the job, not as a manual afterthought, and its output should "
                "be small enough to read. It also needs a tolerance for legitimate differences such as timestamps "
                "or formatting, which must be explicit rather than silently ignored. Today you compare two plain "
                "dictionaries and print the differences and their deltas. No database, no disk, but the exact logic "
                "a production check would use. A run that cannot reconcile cannot honestly claim success or "
                "explain a failure."
            ),
            code=(
                'expected = {"a.csv": 10, "b.csv": 5, "c.csv": 2}\n'
                'actual = {"a.csv": 10, "b.csv": 4, "d.csv": 1}\n'
                '\n'
                'def reconcile(expected, actual):\n'
                '    missing = sorted(set(expected) - set(actual))\n'
                '    extra = sorted(set(actual) - set(expected))\n'
                '    shared = set(expected) & set(actual)\n'
                '    mismatched = {k: actual[k] - expected[k] for k in sorted(shared) if expected[k] != actual[k]}\n'
                '    return {"missing": missing, "extra": extra, "mismatched": mismatched}\n'
                '\n'
                'result = reconcile(expected, actual)\n'
                'for section in ("missing", "extra", "mismatched"):\n'
                '    print(section + ":", result[section])\n'
                '\n'
                'assert result["missing"] == ["c.csv"]\n'
                'assert result["extra"] == ["d.csv"]\n'
                'assert result["mismatched"] == {"b.csv": -1}\n'
                'print("reconcile before trusting the run")'
            ),
            variant_b="add a matching key to both maps and confirm it appears in none of the three sections",
            variant_c="treat a difference of one as within tolerance and report only larger mismatches",
            mistakes=[
                "Reporting a single failed flag instead of distinguishing missing, extra and mismatched state.",
                "Ignoring legitimate formatting differences, so every run reports a false mismatch.",
                "Running reconciliation only after an incident instead of as part of every job.",
            ],
            q1=(
                "Why separate missing, extra and mismatched instead of reporting one difference count?",
                "Each category points to a different repair: unfinished work, unexpected writes, or content disagreement between the two sides.",
            ),
            homework=(
                "Write `def reconcile(expected, actual)` that returns dictionaries for missing keys, extra keys "
                "and mismatched values with their deltas. Run it on two count maps that differ in all three ways, "
                "print each section, and comment which section tells you the job did not finish."
            ),
            patterns=["def reconcile", "missing", "print("],
            mapping=(
                "Data pipelines and migrations run row-count and checksum reconciliation after every load; "
                "missing, extra and mismatched are the standard triage buckets."
            ),
        ),
        144: dict(
            topic="Dead-letter queues",
            idea=(
                "Some work fails permanently, and the worst response is to keep retrying it or silently drop it. A "
                "dead-letter queue is a quarantine: the failed item is stored with its payload, the reason it "
                "failed, the number of attempts and the time of the last try, so a person can inspect it later "
                "without rerunning the whole batch. The queue turns an invisible loss into a visible backlog with "
                "a count and an owner. A good dead-letter record is replayable, which means the original input must "
                "be preserved and the replay path must be idempotent, otherwise the second attempt duplicates side "
                "effects. The queue also needs a policy: a retention window, a maximum size, and an alert when it "
                "grows. Replaying is an operation in its own right, with its own log and reconciliation, not a "
                "quiet loop someone runs from a laptop. Poison messages that crash the consumer need special care; "
                "they should be isolated before they take down the queue. Today you process a list of items, move "
                "the invalid ones into an in-memory dead-letter list with reasons, and replay the survivors after a "
                "fix. The data structure is simple; the discipline is refusing to lose failed work."
            ),
            code=(
                'def route(items, failing):\n'
                '    done = []\n'
                '    dead = []\n'
                '    for item in items:\n'
                '        if item in failing:\n'
                '            dead.append({"item": item, "reason": "invalid", "attempts": 3})\n'
                '        else:\n'
                '            done.append(item)\n'
                '    return done, dead\n'
                '\n'
                'def replay(dead):\n'
                '    return [entry["item"] for entry in dead]\n'
                '\n'
                'items = ["a", "bad-1", "b", "bad-2"]\n'
                'done, dead = route(items, {"bad-1", "bad-2"})\n'
                'print("done:", done)\n'
                'for entry in dead:\n'
                '    print("dead:", entry)\n'
                'print("replayed:", replay(dead))\n'
                '\n'
                'assert done == ["a", "b"]\n'
                'assert [entry["item"] for entry in dead] == ["bad-1", "bad-2"]\n'
                'print("failed work is quarantined, not dropped")'
            ),
            variant_b="add an attempt count per item and send only items with three attempts to the dead-letter list",
            variant_c="simulate a fix and assert that replaying the dead letters completes every item",
            mistakes=[
                "Silently dropping failed items, so the loss only appears when someone misses the output.",
                "Storing only the error text and not the original input, which makes replay impossible.",
                "Replaying non-idempotent work and duplicating the side effects the first attempt already produced.",
            ],
            q1=(
                "What makes a dead-letter record replayable?",
                "The original input plus the failure reason and attempt count, so the item can be retried unchanged after the cause is fixed.",
            ),
            homework=(
                "Write `def route(items, failing)` that returns completed items and dead-letter records containing "
                "item, reason and attempts, then `def replay(dead)` that retries the quarantined items after a fix. "
                "Run one failing pass and one replay, print both results, and comment which field makes a dead "
                "letter replayable."
            ),
            patterns=["def route", "def replay", "print("],
            mapping=(
                "SQS, RabbitMQ and Kafka all provide dead-letter queues with retention limits and redrive tools; "
                "the record shape here mirrors what those systems preserve."
            ),
        ),
        145: dict(
            topic="Reporting partial success",
            idea=(
                "Most real runs do not end in clean success or total failure; they end somewhere in between, and "
                "the report must say so honestly. If ninety-nine items succeeded and one failed, calling the run a "
                "success hides the failure, while calling it a failure hides the ninety-nine. Partial success is a "
                "distinct outcome with its own exit code, its own summary and its own follow-up: the successful "
                "work should be recorded as done, the failed work should be visible and retryable, and the next run "
                "should not redo what already succeeded. The report should lead with the counts and the status, "
                "then name the failures with enough context to act, and avoid adjectives that obscure the numbers. "
                "Exit codes are the machine-readable version: zero for complete success, a dedicated non-zero value "
                "for partial success, and another for total failure, documented so schedulers and humans agree on "
                "what they mean. The same status should drive alerts, so a partial run pages only when its failure "
                "count crosses the agreed threshold. Today you classify three count dictionaries into success, "
                "partial and failure and print the status with its code. The exercise is small because the hard "
                "part is the convention, not the code."
            ),
            code=(
                'def report(counts):\n'
                '    if counts["failed"] == 0:\n'
                '        status = "success"\n'
                '    elif counts["ok"] == 0:\n'
                '        status = "failure"\n'
                '    else:\n'
                '        status = "partial"\n'
                '    code = {"success": 0, "partial": 2, "failure": 1}[status]\n'
                '    return {"status": status, "exit_code": code, "ok": counts["ok"], "failed": counts["failed"]}\n'
                '\n'
                'runs = [\n'
                '    {"ok": 5, "failed": 0},\n'
                '    {"ok": 3, "failed": 2},\n'
                '    {"ok": 0, "failed": 4},\n'
                ']\n'
                'for counts in runs:\n'
                '    print(report(counts))\n'
                '\n'
                'assert report({"ok": 3, "failed": 2})["exit_code"] == 2\n'
                'assert report({"ok": 0, "failed": 4})["status"] == "failure"\n'
                'print("partial success is a distinct outcome")'
            ),
            variant_b="add a skipped count to the report and show that skipped items do not change the status",
            variant_c="route partial runs to a warning channel while total failures page immediately",
            mistakes=[
                "Reporting partial success as a plain success, so the failed items are never followed up.",
                "Reporting partial success as total failure, which hides the work that did complete.",
                "Leaving the partial exit code undocumented, so a scheduler treats it as an unknown error.",
            ],
            q1=(
                "Why does partial success need its own exit code?",
                "A scheduler must distinguish completed-with-failures from total failure and from success, so it can retry only the failed work and alert at the right severity.",
            ),
            homework=(
                "Write `def report(counts)` that returns a status of success, partial or failure plus a distinct "
                "exit code for each. Run it on three count dictionaries, print every report, and comment which line "
                "distinguishes partial success from total failure."
            ),
            patterns=["def report", "partial", "print("],
            mapping=(
                "Batch schedulers and CI systems rely on documented exit codes to decide whether to retry, alert "
                "or mark a build green; partial outcomes are where that convention earns its keep."
            ),
        ),
        146: dict(
            topic="Cleaning up resources",
            idea=(
                "Every resource you open must be closed, even when the work in between raises, and the reliable "
                "way to guarantee that is a cleanup path that always runs. Files, database connections, locks and "
                "temporary directories all have this shape: acquire, use, release. In Python the idiomatic tool is a "
                "context manager, which runs its exit code whether the block succeeded, failed or returned early. "
                "When several resources are nested, release order is the reverse of acquisition order, so a lock "
                "taken before a connection is released after it; getting that order wrong can deadlock or leave a "
                "half-closed state. Cleanup code itself must be defensive: closing a resource may fail, and that "
                "failure should not replace the original error that sent you there. It is also worth separating "
                "\"release\" from \"commit\": rolling back an uncommitted transaction is different from closing the "
                "connection, and the cleanup path should be explicit about which one it is doing. Resource leaks "
                "are quiet; they show up as exhaustion hours later, far from the code that caused them. Today you "
                "model handles that record when they open and close, run a block that raises, and print the release "
                "order. The real lesson is that cleanup is part of the control flow, not an afterthought."
            ),
            code=(
                'closed = []\n'
                '\n'
                'class Handle:\n'
                '    def __init__(self, name):\n'
                '        self.name = name\n'
                '    def __enter__(self):\n'
                '        print("open", self.name)\n'
                '        return self\n'
                '    def __exit__(self, kind, value, traceback):\n'
                '        closed.append(self.name)\n'
                '        print("close", self.name)\n'
                '        return False\n'
                '\n'
                'try:\n'
                '    with Handle("db"), Handle("temp"):\n'
                '        print("working")\n'
                '        raise RuntimeError("boom")\n'
                'except RuntimeError as error:\n'
                '    print("handled:", error)\n'
                '\n'
                'print("release order:", closed)\n'
                'assert closed == ["temp", "db"]\n'
                'print("cleanup runs on the error path")'
            ),
            variant_b="remove the exception and confirm the release order stays the reverse of acquisition",
            variant_c="add a second try block that acquires only one handle and show that it still closes",
            mistakes=[
                "Closing resources only on the success path, so an exception leaks the handle.",
                "Releasing in acquisition order, which can leave a dependent resource used after its parent closes.",
                "Letting a cleanup error replace the original exception, which hides the real cause.",
            ],
            q1=(
                "Why should nested resources be released in reverse acquisition order?",
                "Dependent resources were acquired after their parent, so they must be released before it to avoid using or closing something that is already gone.",
            ),
            homework=(
                "Write `def with_resources(names)` that models acquiring handles in order, runs a block that "
                "raises, releases them in reverse order in a finally block, and returns the release log. Print the "
                "log and comment which line guarantees cleanup on the error path."
            ),
            patterns=["def with_resources", "finally", "print("],
            mapping=(
                "Context managers, connection pools and transaction blocks all encode this acquire-use-release "
                "contract; leaked connections are one of the most common production exhaustion failures."
            ),
        ),
        147: dict(
            topic="Atomic writes",
            idea=(
                "Readers of an output file should never see a half-written version, and the way to guarantee that "
                "is to build the new content somewhere else and swap it in with a single rename. Write to a "
                "temporary file in the same directory, flush and close it, optionally validate it, then rename it "
                "over the destination. Rename within one filesystem is atomic, so a reader sees either the old file "
                "or the new one, never a truncated mixture. The temporary file must live in the same directory, not "
                "in a system temp folder on another mount, or the rename becomes a copy and loses the guarantee. If "
                "the process crashes before the rename, the destination is untouched and the leftover temporary "
                "file can be cleaned up safely. The pattern also applies to in-memory state: build a new dictionary "
                "or list, validate it, then replace the reference rather than mutating the live one. Idempotence "
                "matters here too, because a retry after a failed rename must be able to tell whether the new "
                "content already landed. Today you model a filesystem as a dictionary, write through a temporary "
                "key, and show that a simulated crash leaves the old value intact. No disk is touched, but the "
                "order of operations is exactly the one production writers use."
            ),
            code=(
                'files = {"report.csv": "old"}\n'
                '\n'
                'def atomic_write(files, path, data, crash=False):\n'
                '    tmp = path + ".tmp"\n'
                '    files[tmp] = data\n'
                '    if crash:\n'
                '        return False\n'
                '    files[path] = files.pop(tmp)\n'
                '    return True\n'
                '\n'
                'print("start:", files)\n'
                'print("first write ok:", atomic_write(files, "report.csv", "new"))\n'
                'print("after ok:", files)\n'
                'print("second write ok:", atomic_write(files, "report.csv", "half", crash=True))\n'
                'print("after crash:", files)\n'
                '\n'
                'assert files["report.csv"] == "new"\n'
                'assert files["report.csv.tmp"] == "half"\n'
                'print("the destination never holds a partial write")'
            ),
            variant_b="validate the new content before the swap and refuse to rename when the value is empty",
            variant_c="clean up the leftover temporary key after a crash and show the destination is still old",
            mistakes=[
                "Writing directly into the destination, so a crash leaves a truncated file for readers.",
                "Putting the temporary file on a different filesystem, which turns the rename into a copy.",
                "Swapping before validating the new content, so a bad build replaces a good file.",
            ],
            q1=(
                "Why must the temporary file live in the same directory as the destination?",
                "Rename is only atomic within one filesystem; across filesystems it becomes a copy and readers can see a partial state.",
            ),
            homework=(
                "Write `def atomic_write(files, path, data, crash=False)` that stores data under a temporary key, "
                "optionally simulates a crash, and otherwise replaces the destination in one step. Run one "
                "successful write and one crash, print the dictionary after each, and comment which line protects "
                "the old value."
            ),
            patterns=["def atomic_write", ".tmp", "print("],
            mapping=(
                "Databases use write-ahead logs and rename-based writers use temp-plus-rename; the guarantee is "
                "the same, and it is what lets a reader trust a file at any instant."
            ),
        ),
        148: dict(
            topic="Runbooks for failures",
            idea=(
                "A runbook is the answer to the question the alert did not answer: what do I do now? It should "
                "start from the symptom an operator can actually see, for example \"write failed with no space "
                "left\", then give a verification step that confirms the diagnosis, a mitigation that restores "
                "service, and an escalation path with an owner for when the mitigation does not work. Good "
                "runbooks are short, ordered and concrete: exact commands or checks, expected output, and a clear "
                "stop condition. They also name the blast radius and any irreversible step, so nobody deletes the "
                "wrong directory while following instructions at three in the morning. The runbook should be linked "
                "from the alert itself and stored next to the code, so it changes in the same review as the "
                "behaviour it describes. A runbook that has never been exercised is a guess; a periodic game day or "
                "a replay against a staging failure is how you find the missing step. Today you model runbooks as "
                "dictionaries with symptom, verify, mitigate and escalate fields, then print the ordered steps for "
                "one symptom. The code is deliberately plain because the value is in the content and its review, "
                "not in the container."
            ),
            code=(
                'RUNBOOK = {\n'
                '    "disk_full": {\n'
                '        "verify": "check free space on the output volume",\n'
                '        "mitigate": "move old exports and rerun the failed step",\n'
                '        "escalate": "storage owner if space does not recover",\n'
                '    },\n'
                '}\n'
                '\n'
                'def runbook_steps(runbook, symptom):\n'
                '    entry = runbook.get(symptom)\n'
                '    if entry is None:\n'
                '        return ["no runbook: escalate to the on-call owner"]\n'
                '    return [entry[key] for key in ("verify", "mitigate", "escalate")]\n'
                '\n'
                'for number, step in enumerate(runbook_steps(RUNBOOK, "disk_full"), start=1):\n'
                '    print(number, step)\n'
                'print("unknown:", runbook_steps(RUNBOOK, "clock_skew"))\n'
                '\n'
                'assert runbook_steps(RUNBOOK, "disk_full")[0].startswith("check")\n'
                'assert len(runbook_steps(RUNBOOK, "disk_full")) == 3\n'
                'print("every alert should link to a runbook")'
            ),
            variant_b="add a symptom that has no runbook and confirm the fallback tells the responder to escalate",
            variant_c="add an irreversible step field and print it before the mitigation so it cannot be missed",
            mistakes=[
                "Writing a runbook that starts with a cause instead of the symptom an operator can see.",
                "Leaving out the escalation owner, so a failed mitigation has nowhere to go.",
                "Storing the runbook far from the code so it drifts out of date without anyone noticing.",
            ],
            q1=(
                "Why should a runbook begin with the observable symptom?",
                "The responder starts from what the alert or dashboard shows, so matching on the symptom gets them to the right procedure fastest.",
            ),
            homework=(
                "Write `def runbook_steps(runbook, symptom)` that returns verify, mitigate and escalate steps in "
                "order, or a clear 'no runbook' message. Run it for a known symptom and an unknown one, print both, "
                "and comment which line makes the escalation path explicit."
            ),
            patterns=["def runbook_steps", "escalate", "print("],
            mapping=(
                "Incident tooling links alerts to runbooks, and teams review them after every incident; an "
                "unreviewed runbook is the documentation equivalent of an untested backup."
            ),
        ),
        149: dict(
            topic="Review: robustness and logging checklist",
            idea=(
                "Today you assemble the phase into a checklist, which is how robustness stops being a set of good "
                "intentions and becomes something a reviewer can verify. The list should cover the whole failure "
                "path: errors are classified rather than lumped together, bad items are isolated so the batch "
                "continues, retries are bounded and only applied to transient faults, a breaker stops hammering a "
                "dead dependency, logs are structured with stable keys, alerts are derived from a summary and "
                "linked to a runbook, reconciliation compares expected and actual state, failures land in a "
                "dead-letter queue instead of disappearing, partial success has its own status and exit code, "
                "resources are released on every path, and writes are atomic. A checklist is not a score to "
                "maximise; it is a way to ask which items genuinely apply to this job and which would be ceremony. "
                "The output of the review should be a short list of gaps with owners, not a pass mark. Each gap is a "
                "hypothesis about how the next incident will start. Today you audit an in-memory policy dictionary "
                "against the checklist and print the count and the missing items. That is the same review a "
                "production team would run before calling an automation dependable."
            ),
            code=(
                'CHECKS = {\n'
                '    "classify_errors": True,\n'
                '    "isolate_items": True,\n'
                '    "bounded_retries": True,\n'
                '    "circuit_breaker": False,\n'
                '    "structured_logs": True,\n'
                '    "alerts_with_runbook": True,\n'
                '    "reconcile_state": False,\n'
                '    "dead_letter_queue": True,\n'
                '    "partial_status": True,\n'
                '    "cleanup_resources": True,\n'
                '    "atomic_writes": True,\n'
                '    "runbook_reviewed": False,\n'
                '}\n'
                '\n'
                'def audit(checks):\n'
                '    failed = sorted(name for name, ok in checks.items() if not ok)\n'
                '    return {"passed": len(checks) - len(failed), "gaps": failed}\n'
                '\n'
                'result = audit(CHECKS)\n'
                'print("passed:", result["passed"], "of", len(CHECKS))\n'
                'for name in result["gaps"]:\n'
                '    print("gap:", name)\n'
                '\n'
                'assert result["passed"] == 9\n'
                'assert result["gaps"] == ["circuit_breaker", "reconcile_state", "runbook_reviewed"]\n'
                'print("a checklist turns robustness into a review")'
            ),
            variant_b="add a checklist item for idempotent replay and show how the pass count changes",
            variant_c="group the gaps by owner and print one line per owner instead of one line per gap",
            mistakes=[
                "Treating the checklist as a score to maximise instead of a review of what applies.",
                "Listing gaps with no owner, so the review produces awareness rather than action.",
                "Copying the checklist without adapting it to the job, which adds ceremony instead of safety.",
            ],
            q1=(
                "What should the output of a robustness review be?",
                "A short list of applicable gaps with owners, not a pass mark, so each finding turns into an action.",
            ),
            homework=(
                "Write `def audit(checks)` that returns the number of passed checks and a sorted list of gaps, "
                "then run it over a dictionary of at least eight checklist items. Print the count and each gap, and "
                "comment which gap you would fix first and why."
            ),
            patterns=["def audit", "sorted", "print("],
            mapping=(
                "Production readiness reviews and SRE checklists use the same shape: a small set of verifiable "
                "properties, each with an owner, reviewed before a service is trusted unattended."
            ),
        ),
    },
)
