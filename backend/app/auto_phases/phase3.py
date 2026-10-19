"""Automation / Scripting phase 3, days 105-119: scheduling and recurring jobs.

Every worked example is stdlib-only, offline and deterministic: time is
represented as plain integer minutes or epoch-like integers supplied as data,
and no example reads a real clock, sleeps, touches the network or uses
unseeded randomness. Next runs and windows are computed arithmetically, so the
output is stable while the behaviour is exactly what a scheduler does.
"""

PHASE = (
    "Scheduling and Recurring Jobs",
    "Take recurring work from a hand-waved cron line to a tested, overlap-safe "
    "schedule by treating time as data you can compute on.",
    {
        105: dict(
            topic="Orientation: recurring work",
            idea=(
                "Most automation is not a script you run once; it is work that happens again and again on a "
                "rhythm, and the moment you accept that, a new set of questions appears. When should it run? "
                "What happens if a run is slow, or fails, or overlaps the next one? Where do you record that it "
                "succeeded? Recurring work is best understood as three separate concerns: a trigger that decides "
                "when, a unit of work that does the thing, and a record that remembers what happened. Keeping them "
                "separate is what lets you test the schedule without touching the work, and test the work without "
                "waiting for a clock. Today you model that shape with plain integers. A minute-of-day counter is "
                "enough to represent a cursor moving forward through time, and stepping it by a period produces "
                "the run times of a simple job. No real clock is involved, so the example is fast, deterministic "
                "and easy to reason about. That habit of treating time as data and advancing it arithmetically "
                "carries through the whole phase, and it is exactly how schedulers reason internally about when "
                "the next run is due. Keeping that three-part boundary clear from day one is what stops a "
                "scheduler from slowly turning into a pile of special cases."
            ),
            code=(
                "DAY = 24 * 60\n"
                "\n"
                "def run_times(start, period, horizon):\n"
                "    times = []\n"
                "    t = start\n"
                "    while t < horizon:\n"
                "        times.append(t)\n"
                "        t += period\n"
                "    return times\n"
                "\n"
                "for t in run_times(9 * 60, DAY, 3 * DAY):\n"
                "    print(\"run at\", f\"{t // 60:02d}:{t % 60:02d}\")\n"
                "print(\"count:\", len(run_times(9 * 60, DAY, 3 * DAY)))\n"
                "\n"
                "assert run_times(0, 60, 180) == [0, 60, 120]\n"
                "print(\"a recurring job is just a cursor moving forward\")"
            ),
            variant_b="change the period to 90 minutes and predict how many runs appear over three days",
            variant_c="start the job at 08:30 instead of 09:00 and print the shifted schedule",
            mistakes=[
                "Treating a recurring job as a one-off script, so no thought is given to overlaps or reruns.",
                "Burying the trigger timing inside the work function, so neither can be tested alone.",
                "Forgetting to record outcomes, so nobody can tell whether the last run actually succeeded.",
            ],
            q1=(
                "Why keep the trigger, the work and the run record separate?",
                "Each can be tested and changed independently, so schedule bugs and work bugs do not hide behind each other.",
            ),
            homework=(
                "Write `run_times(start, period, horizon)` that returns the list of run times before the horizon, "
                "plus code that prints each one as HH:MM and prints the total count. Try two different periods and "
                "comment which line advances the cursor."
            ),
            patterns=["def run_times", "return", "print("],
            mapping=(
                "Cron, systemd timers and Airflow DAGs all separate the trigger from the task and keep a record "
                "of runs; this three-part shape is what lets those tools retry and alert."
            ),
        ),
        106: dict(
            topic="A schedule as data",
            idea=(
                "Schedules are easier to reason about when they are data rather than code. Instead of scattering "
                "constants like 'every thirty minutes' through a script, you write one dictionary describing the "
                "cadence and the window, and every part of the system reads that single description. The payoff "
                "is uniformity: the runner, the next-run calculator, the documentation and the tests all agree "
                "because they consult the same value. It also makes schedules inspectable and storable, so you "
                "can print one, diff two, keep a library of them, or load one from a file without changing any "
                "logic. A good schedule record answers a few questions explicitly: what kind of cadence is it, "
                "how often, and when is it allowed to run? Validation belongs right next to the data, so a "
                "malformed schedule is rejected the moment it is created rather than three hours later when the "
                "runner trips over it. Today you represent a schedule as a plain dictionary and write a validator "
                "and a human-readable formatter over it. Everything stays in memory, so you can test the whole "
                "thing with a couple of assertions and no scheduler at all. The dictionary is also the natural "
                "unit to review, because a reviewer can read one line and see the intended cadence."
            ),
            code=(
                "schedule = {\"kind\": \"interval\", \"every_minutes\": 30, \"window\": (9 * 60, 17 * 60)}\n"
                "\n"
                "def validate(schedule):\n"
                "    problems = []\n"
                "    if schedule.get(\"kind\") != \"interval\":\n"
                "        problems.append(\"unknown kind\")\n"
                "    if schedule.get(\"every_minutes\", 0) <= 0:\n"
                "        problems.append(\"period must be positive\")\n"
                "    lo, hi = schedule.get(\"window\", (0, 1440))\n"
                "    if not 0 <= lo < hi <= 1440:\n"
                "        problems.append(\"bad window\")\n"
                "    return problems\n"
                "\n"
                "def describe(schedule):\n"
                "    lo, hi = schedule[\"window\"]\n"
                "    return (f\"{schedule['kind']} every {schedule['every_minutes']}m \"\n"
                "            f\"from {lo // 60:02d}:{lo % 60:02d} to {hi // 60:02d}:{hi % 60:02d}\")\n"
                "\n"
                "print(describe(schedule))\n"
                "print(\"problems:\", validate(schedule))\n"
                "print(\"bad:\", validate({\"kind\": \"cron\", \"every_minutes\": 0, \"window\": (10, 0)}))\n"
                "\n"
                "assert validate(schedule) == []\n"
                "assert validate({\"kind\": \"cron\", \"every_minutes\": 0, \"window\": (10, 0)})"
            ),
            variant_b="add a timezone field and make validate reject a missing or empty one",
            variant_c="load two different schedule dictionaries and print both descriptions side by side",
            mistakes=[
                "Hard-coding cadence constants in several places instead of one schedule record.",
                "Validating the schedule deep inside the runner instead of where it is created.",
                "Using a sentinel like zero to mean 'no window', which hides a genuinely bad value.",
            ],
            q1=(
                "Why keep a schedule as a dictionary rather than as constants in code?",
                "One described value is shared by the runner, the calculator and the tests, so they cannot silently disagree.",
            ),
            homework=(
                "Write `validate(schedule)` that returns a list of problems for a schedule dictionary and "
                "`describe(schedule)` that returns a readable one-line summary. Test a good schedule and a "
                "deliberately broken one, print both, and comment which line catches the bad period."
            ),
            patterns=["def validate", "return", "print("],
            mapping=(
                "Airflow stores schedules as data on the DAG and Kubernetes CronJobs as a YAML spec; the "
                "principle is that cadence is configuration, not scattered code."
            ),
        ),
        107: dict(
            topic="Cron-style expressions",
            idea=(
                "Cron expressions are the lingua franca of recurring schedules, and they look cryptic until you "
                "see that each field is just a set of allowed values. A classic five-field expression names "
                "minute, hour, day of month, month and day of week, and every field accepts the same small "
                "vocabulary: a star for any, a number, a list joined by commas, a range written with a hyphen, "
                "and a step written as a slash. Once you can evaluate one field against a value, evaluating a "
                "whole timestamp is just linking the fields with and. Writing a matcher teaches this far better "
                "than memorising syntax, because it removes the mystery from every tool that uses cron. It also "
                "surfaces the subtle traps early: the day-of-month and day-of-week fields combine inclusively in "
                "real cron, a step like */15 means 'every fifteen starting at zero', and a range such as 9-17 "
                "includes both ends. Today you implement a field matcher and use it to test a few fixed "
                "timestamps, so the output is stable and you can see precisely which times the expression "
                "selects. All times are ordinary integers, so nothing depends on the machine clock. A few "
                "minutes spent reading a matcher repay themselves the first time a production job fires at the "
                "wrong time."
            ),
            code=(
                "def field_matches(spec, value):\n"
                "    for part in spec.split(\",\"):\n"
                "        if part == \"*\":\n"
                "            return True\n"
                "        if part.startswith(\"*/\"):\n"
                "            if value % int(part[2:]) == 0:\n"
                "                return True\n"
                "        elif \"-\" in part:\n"
                "            lo, hi = part.split(\"-\")\n"
                "            if int(lo) <= value <= int(hi):\n"
                "                return True\n"
                "        elif int(part) == value:\n"
                "            return True\n"
                "    return False\n"
                "\n"
                "def cron_matches(expr, minute, hour):\n"
                "    m, h = expr.split()[:2]\n"
                "    return field_matches(m, minute) and field_matches(h, hour)\n"
                "\n"
                "expr = \"*/15 9-17\"\n"
                "for minute, hour in ((30, 8), (30, 9), (45, 17), (5, 9)):\n"
                "    print(f\"{hour:02d}:{minute:02d}\", cron_matches(expr, minute, hour))\n"
                "\n"
                "assert cron_matches(expr, 45, 17) and not cron_matches(expr, 30, 8)"
            ),
            variant_b="add the day-of-week field and test that '*/15 9-17 * * 1-5' excludes Saturday",
            variant_c="support a list such as '0,30' in the minute field and print which times it matches",
            mistakes=[
                "Assuming a range like 9-17 excludes 17, when cron includes both ends.",
                "Writing */15 and expecting it to start at the current minute rather than at zero.",
                "Evaluating the fields in the wrong order, so hour values are compared as minutes.",
            ],
            q1=(
                "What does the step syntax */15 in a cron field mean?",
                "Every value divisible by fifteen within the field's range, starting at zero, so 0, 15, 30 and 45.",
            ),
            homework=(
                "Write `field_matches(spec, value)` and `cron_matches(expr, minute, hour)` that evaluate a "
                "two-field cron expression, then test at least four fixed timestamps and print each result. "
                "Comment which line handles the range syntax."
            ),
            patterns=["def field_matches", "def cron_matches", "print("],
            mapping=(
                "Linux cron, systemd OnCalendar and many CI systems accept near-identical expressions; a matcher "
                "you can read is the key to debugging why a job did or did not fire."
            ),
        ),
        108: dict(
            topic="Intervals and windows",
            idea=(
                "An interval says how often a job runs; a window says when it is allowed to. Separating the two "
                "is what keeps a schedule realistic. A report may be due every thirty minutes, but you only want "
                "it during business hours, so the window trims the interval's output without changing its rhythm. "
                "The clean way to model this is to start at the window's opening time and step by the period "
                "until the window closes, which makes the run count obvious. Watch the boundaries. A half-open "
                "window, written as start inclusive and end exclusive, avoids the double-run at the edge and "
                "matches how most schedulers think about slots. Windows can also wrap past midnight, which is "
                "common for maintenance or evening jobs, and that case needs its own branch rather than a "
                "straight comparison. Keeping the interval and the window as two separate pieces of data also "
                "means you can change the business hours without touching the cadence, which is a real concern "
                "in every operations team. Today you generate the slots of a job inside a fixed window and print "
                "each one, using only integer minutes, so the result is fully deterministic. The boundary rule "
                "you choose here is the one every later phase will assume."
            ),
            code=(
                "def window_runs(start, end, period, horizon):\n"
                "    slots = []\n"
                "    t = start\n"
                "    while t < horizon and t < end:\n"
                "        slots.append(t)\n"
                "        t += period\n"
                "    return slots\n"
                "\n"
                "slots = window_runs(9 * 60, 12 * 60, 45, 24 * 60)\n"
                "for t in slots:\n"
                "    print(\"slot\", f\"{t // 60:02d}:{t % 60:02d}\")\n"
                "print(\"count:\", len(slots))\n"
                "\n"
                "assert slots == [540, 585, 630, 675]\n"
                "print(\"the window trims the interval without changing it\")"
            ),
            variant_b="make the window wrap past midnight and generate slots for an evening maintenance job",
            variant_c="change the period so the last slot lands exactly on the window end and explain the boundary rule",
            mistakes=[
                "Mixing interval and window into one number, so business-hours logic leaks into the cadence.",
                "Treating the window end as inclusive, which fires one run too many at the boundary.",
                "Ignoring windows that wrap past midnight, so evening jobs never run.",
            ],
            q1=(
                "Why treat the window end as exclusive?",
                "So a run exactly at the closing time is not counted twice and the slot count matches the interval maths.",
            ),
            homework=(
                "Write `window_runs(start, end, period, horizon)` returning the run times inside a half-open "
                "window, print each slot as HH:MM and print the count. Then call it with a different period and "
                "comment which line enforces the window's closing time."
            ),
            patterns=["def window_runs", "return", "print("],
            mapping=(
                "Cron cannot express a window directly, so teams wrap the job in a guard; systemd timers express "
                "windows natively, and both are doing what this function makes explicit."
            ),
        ),
        109: dict(
            topic="Computing the next run",
            idea=(
                "The single most useful function in any scheduler is 'given that the last run happened and that "
                "time is now, when is the next run?'. It sounds trivial until you handle the cases properly. The "
                "job may never have run, so the next run is simply now, or the start of the window. The last run "
                "may be far in the past, so the next time may already be overdue and you either fire immediately "
                "or skip ahead. And the arithmetic must be strictly greater than now, never equal, or a job can "
                "fire twice in the same instant. The clean formulation takes a last-run time, a period and a "
                "current time and returns the first period boundary strictly after now. Because it is pure "
                "arithmetic over integers it is easy to test exhaustively, and it never reads a clock, which is "
                "why it belongs in its own small function that the runner calls. Once you can compute the next "
                "run, a great deal of scheduling becomes bookkeeping: advance the cursor, record the outcome, and "
                "ask again. Today you implement that function on fixed values, including the awkward cases where "
                "the last run equals now and where many periods have been missed."
            ),
            code=(
                "def next_run(last, period, now):\n"
                "    if last is None:\n"
                "        return now\n"
                "    nxt = last + period\n"
                "    while nxt <= now:\n"
                "        nxt += period\n"
                "    return nxt\n"
                "\n"
                "print(\"never run:\", next_run(None, 60, 900))\n"
                "print(\"due now:\", next_run(600, 60, 660))\n"
                "print(\"equal to now:\", next_run(540, 60, 600))\n"
                "print(\"far behind:\", next_run(0, 60, 300))\n"
                "\n"
                "assert next_run(540, 60, 600) == 660\n"
                "assert next_run(0, 60, 300) == 360"
            ),
            variant_b="make a job that is far behind return the overdue time so the runner can catch up",
            variant_c="add an optional start time used only when the job has never run before",
            mistakes=[
                "Returning a next run equal to now, so the job fires twice in the same instant.",
                "Advancing by one period from now instead of from the last run, which drifts.",
                "Handling the never-run case with a crash instead of a defined start time.",
            ],
            q1=(
                "Why must the next run be strictly greater than the current time?",
                "Otherwise a run equal to now satisfies the condition again immediately and the job fires repeatedly.",
            ),
            homework=(
                "Write `next_run(last, period, now)` returning the first period boundary strictly after now, "
                "handling a missing last run. Test it on at least four fixed inputs including a far-behind case, "
                "print each result, and comment which line skips over missed periods."
            ),
            patterns=["def next_run", "while ", "print("],
            mapping=(
                "APScheduler and Airflow both expose a next-run calculation; keeping it pure and clock-free is "
                "what makes a scheduler testable instead of mysterious."
            ),
        ),
        110: dict(
            topic="Calendar and business days",
            idea=(
                "Interval maths assumes every day is the same, but real schedules live on a calendar. Some jobs "
                "run only on weekdays, some skip public holidays, some fire on the first business day of the "
                "month. The foundation for all of that is being able to convert a date into a weekday and to "
                "find the next day that qualifies. If you number days consecutively and fix an arbitrary origin, "
                "the weekday is just the day number taken modulo seven, and a weekend test is a membership check "
                "against the weekend numbers. From there, 'the next business day' is a loop that advances until "
                "the predicate passes. Holidays are the harder half: they are not a formula but a list, and the "
                "honest approach is to keep that list as data and treat a holiday exactly like a weekend, so the "
                "same advancing loop uses it without change. This separation, a weekday rule plus a weekend rule "
                "plus a holiday list, keeps the calendar logic transparent and testable. Today you build a "
                "weekday function, a business-day predicate and a next-business-day search over small integer "
                "day numbers with a fixed holiday set. Weekday, weekend and holiday each stay a separate, "
                "replaceable piece, which is what lets a test swap in a different calendar."
            ),
            code=(
                "WEEKEND = (5, 6)\n"
                "HOLIDAYS = {10, 17}\n"
                "\n"
                "def weekday(day):\n"
                "    return day % 7\n"
                "\n"
                "def is_business_day(day):\n"
                "    return weekday(day) not in WEEKEND and day not in HOLIDAYS\n"
                "\n"
                "def next_business(day):\n"
                "    d = day + 1\n"
                "    while not is_business_day(d):\n"
                "        d += 1\n"
                "    return d\n"
                "\n"
                "for d in range(3, 9):\n"
                "    print(d, \"weekday\", weekday(d), \"business\", is_business_day(d))\n"
                "print(\"next from Friday:\", next_business(4))\n"
                "\n"
                "assert next_business(4) == 7"
            ),
            variant_b="add a holiday and confirm the next-business-day search skips it as well",
            variant_c="find the first business day of a month by starting from its first day number",
            mistakes=[
                "Hard-coding weekend days as names instead of deriving a weekday from the day number.",
                "Scattering holiday checks through the code instead of keeping one holiday set as data.",
                "An off-by-one in the advancing loop, so a day that is itself a weekend is returned.",
            ],
            q1=(
                "How do you derive the weekday of a day number?",
                "Take the day number modulo seven, once the origin's weekday is fixed as day zero.",
            ),
            homework=(
                "Write `weekday(day)`, `is_business_day(day)` and `next_business(day)` that skip weekends and a "
                "small fixed holiday set, print a short range of days with their status, and comment which line "
                "advances past a non-business day."
            ),
            patterns=["def next_business", "while ", "print("],
            mapping=(
                "Airflow's schedule intervals and cron's day-of-week field both encode calendar rules; "
                "business-day libraries wrap exactly this weekday-plus-holiday-list idea."
            ),
        ),
        111: dict(
            topic="Timezones conceptually",
            idea=(
                "Timezones are where scheduling quietly gets hard. A schedule is usually stored in one reference, "
                "often UTC, but the wall-clock time people care about is local, so every job needs a well-defined "
                "conversion between the two. The simplest honest model is an offset in minutes: UTC plus the "
                "offset gives local time, and subtracting gives UTC back. That model is already enough to catch "
                "the classic bug of a job that fires an hour early twice a year, because daylight saving is "
                "exactly an offset that changes. The key conceptual points are few. Store instants in UTC and "
                "convert only for display or for human-entered rules. Carry the timezone name alongside the "
                "value, because a bare number cannot be reinterpreted later. And beware of arithmetic across a "
                "daylight-saving boundary, where a local time may not exist or may occur twice. Today you convert "
                "a fixed UTC instant to several local times using integer offsets and print them, which makes the "
                "arithmetic visible without depending on the host machine's zone database. That last point "
                "matters: a script whose output changes with the server's timezone is not testable. Fixing the "
                "offset as data is what keeps the example honest, portable and reproducible on any machine."
            ),
            code=(
                "def fmt(minute):\n"
                "    minute %= 1440\n"
                "    return f\"{minute // 60:02d}:{minute % 60:02d}\"\n"
                "\n"
                "def to_local(utc_minute, offset_minutes):\n"
                "    return utc_minute + offset_minutes\n"
                "\n"
                "utc = 9 * 60\n"
                "for name, offset in ((\"UTC\", 0), (\"CET\", 60), (\"IST\", 330), (\"EST\", -300)):\n"
                "    print(name, f\"{offset:+04d}\", fmt(to_local(utc, offset)))\n"
                "\n"
                "assert fmt(to_local(utc, 330)) == \"14:30\"\n"
                "print(\"store UTC, convert for people\")"
            ),
            variant_b="add a daylight-saving offset change and show the same UTC instant mapping to a new local time",
            variant_c="convert a local input time back to UTC by subtracting the offset and print both",
            mistakes=[
                "Storing wall-clock local times as if they were absolute instants.",
                "Dropping the timezone name, so a bare number cannot be interpreted later.",
                "Assuming an offset is fixed across the year and ignoring daylight saving.",
            ],
            q1=(
                "Why store scheduled instants in UTC and convert only for display?",
                "UTC is unambiguous and monotonic, so daylight-saving changes cannot move the underlying instant.",
            ),
            homework=(
                "Write `to_local(utc_minute, offset_minutes)` and `fmt(minute)` that convert and format integer "
                "minutes for at least three offsets, print each local time, and comment which line carries the "
                "offset and why it must travel with the value."
            ),
            patterns=["def to_local", "def fmt", "print("],
            mapping=(
                "Cron runs in the host timezone unless told otherwise, systemd supports a timezone suffix, and "
                "Airflow attaches a timezone to each DAG; explicit offsets are what prevent silent drift."
            ),
        ),
        112: dict(
            topic="Missed runs and catch-up",
            idea=(
                "Schedulers miss runs more often than people expect: the machine was off, a previous run was slow, "
                "an outage delayed the timer. What matters is that the system has a deliberate policy for the "
                "gap. The two extremes are both wrong. Firing every missed run the moment the system returns can "
                "stampede a queue, and skipping everything silently can leave a report missing for a whole day. "
                "The common middle ground is catch-up with a cap: run the most recent few missed occurrences and "
                "coalesce the older ones into a single note or a single run. To implement it, you compute every "
                "occurrence due between the last success and now, take the first few, and count the remainder so "
                "the record and the logs can explain what was dropped. The cap is doing real work, because it "
                "bounds the load while preserving useful recency. Catching up also makes idempotency mandatory, "
                "since a run may be repeated after a partial failure. Today you compute the due runs and split "
                "them into those you will execute and those you will coalesce, using fixed integer times so the "
                "split is completely deterministic. The same function then feeds the run record, so the log can "
                "state what was caught up and what was coalesced."
            ),
            code=(
                "def due_runs(last, period, now):\n"
                "    runs = []\n"
                "    t = last + period\n"
                "    while t <= now:\n"
                "        runs.append(t)\n"
                "        t += period\n"
                "    return runs\n"
                "\n"
                "def catch_up(last, period, now, cap=3):\n"
                "    runs = due_runs(last, period, now)\n"
                "    return runs[:cap], len(runs) - cap\n"
                "\n"
                "missed, dropped = catch_up(540, 60, 540 + 6 * 60)\n"
                "print(\"last run: 09:00\")\n"
                "print(\"catch up:\", missed)\n"
                "print(\"coalesced:\", dropped)\n"
                "\n"
                "assert missed == [600, 660, 720] and dropped == 3"
            ),
            variant_b="set the cap to one so only the most recent missed run executes and the rest coalesce",
            variant_c="make catch_up also return the coalesced run times rather than just a count",
            mistakes=[
                "Firing every missed occurrence at once, so the system stampedes after downtime.",
                "Dropping missed runs silently, so a report is missing with no explanation.",
                "Forgetting that a caught-up run may repeat, which requires idempotent work.",
            ],
            q1=(
                "Why cap catch-up instead of running every missed occurrence?",
                "A cap bounds the sudden load while still bringing the schedule back up to date.",
            ),
            homework=(
                "Write `due_runs(last, period, now)` and `catch_up(last, period, now, cap)` that return the runs "
                "to execute and the number coalesced. Run it on a long gap with a small cap, print both values, "
                "and comment which line bounds the work."
            ),
            patterns=["def catch_up", "return", "print("],
            mapping=(
                "systemd's Persistent=true and Airflow's catchup flag are exactly this decision; choosing a cap "
                "is what keeps a backlog from turning into an outage."
            ),
        ),
        113: dict(
            topic="Single-instance locks",
            idea=(
                "A scheduled job can overlap itself. If a run takes longer than its period, the next trigger "
                "arrives while the previous one is still working, and two copies fight over the same output. The "
                "standard defence is a single-instance lock: before doing anything, a run tries to claim a named "
                "lock, and a run that cannot claim it exits quietly. The interesting design questions are about "
                "ownership and recovery. A lock must name its owner so it can be released by the right process, "
                "and it must carry an expiry so that a crashed run does not block the schedule forever. With an "
                "expiry, claiming is a simple rule: succeed if the lock is absent or already expired, otherwise "
                "fail. That gives at-most-one-run behaviour without any coordination service, which is usually "
                "enough. It also means the lock is only as reliable as the expiry you choose; too short and two "
                "runs overlap, too long and a crash stalls the job. Today you model a lock as a plain dictionary "
                "with an owner and an expiry, and test claiming before, during and after the expiry window, all "
                "with fixed integer times. Reading the lock as data also makes the whole overlap question a "
                "matter of arithmetic rather than trust."
            ),
            code=(
                "def acquire(lock, owner, now, ttl):\n"
                "    holder = lock.get(\"owner\")\n"
                "    if holder is not None and lock[\"expires\"] > now:\n"
                "        return lock, False\n"
                "    return {\"owner\": owner, \"expires\": now + ttl}, True\n"
                "\n"
                "lock = {}\n"
                "lock, first = acquire(lock, \"run-1\", 100, 30)\n"
                "lock, second = acquire(lock, \"run-2\", 110, 30)\n"
                "lock, third = acquire(lock, \"run-3\", 135, 30)\n"
                "print(\"run-1 claimed:\", first)\n"
                "print(\"run-2 refused:\", not second)\n"
                "print(\"run-3 after expiry:\", third)\n"
                "\n"
                "assert first and not second and third"
            ),
            variant_b="add an owner check so only the process holding the lock may release it",
            variant_c="show what happens with a very short ttl when two runs start close together",
            mistakes=[
                "Using a lock with no expiry, so a crashed run blocks the schedule forever.",
                "Releasing a lock without checking the owner, so one run frees another's claim.",
                "Treating the lock as a guarantee, when clock skew and lost records can still allow overlap.",
            ],
            q1=(
                "Why must a single-instance lock carry an expiry?",
                "So a crashed holder does not block every future run; the lock can be reclaimed once it expires.",
            ),
            homework=(
                "Write `acquire(lock, owner, now, ttl)` and `release(lock, owner)` that implement a single-instance "
                "lock over a dictionary with an expiry, test claiming twice and reclaiming after expiry, print "
                "each outcome, and comment which line enforces the expiry."
            ),
            patterns=["def acquire", "def release", "print("],
            mapping=(
                "Cron users reach for flock, systemd relies on the service manager, and Airflow uses "
                "max_active_runs; all of them are expressing at-most-one-run."
            ),
        ),
        114: dict(
            topic="Retries for a scheduled job",
            idea=(
                "Scheduled jobs fail for transient reasons all the time: a database is briefly unavailable, a "
                "network call times out, a file is not there yet. Retrying is the standard remedy, but a naive "
                "retry loop makes things worse by hammering a struggling service. The usual policy pairs a "
                "limited number of attempts with exponential backoff, so each wait is longer than the last, and "
                "sometimes with jitter, so many jobs do not all retry at the same instant. Three parameters "
                "define the policy and each needs a sane value: the maximum number of attempts, the base delay, "
                "and a cap on the delay. The distinction that matters most is between retryable and permanent "
                "failures; retrying a validation error forever just wastes a worker, while treating a timeout as "
                "permanent loses recoverable work. A retry policy is therefore part of the job's contract, not an "
                "afterthought, and it should be visible in the schedule and in the logs. Today you build a small "
                "retry planner that, given a fixed pattern of failures, prints when each attempt happens and how "
                "the wait grows. Because the failure pattern is data, the example is fully deterministic. "
                "Keeping the policy as parameters rather than constants makes it easy to tune per job."
            ),
            code=(
                "def run_with_retries(fail_until, max_attempts=4, base=1):\n"
                "    log = []\n"
                "    for attempt in range(1, max_attempts + 1):\n"
                "        ok = attempt >= fail_until\n"
                "        wait = 0 if ok else base * 2 ** (attempt - 1)\n"
                "        log.append((attempt, ok, wait))\n"
                "    return log\n"
                "\n"
                "for attempt, ok, wait in run_with_retries(3):\n"
                "    print(\"attempt\", attempt, \"succeeded\" if ok else f\"retry in {wait}m\")\n"
                "\n"
                "waits = [w for _, ok, w in run_with_retries(3) if not ok]\n"
                "assert waits == [1, 2]\n"
                "print(\"backoff waits:\", waits)"
            ),
            variant_b="add a maximum delay cap so the backoff stops doubling after a few attempts",
            variant_c="mark one error as permanent and show the loop stopping without exhausting attempts",
            mistakes=[
                "Retrying without a limit, so a permanently broken job retries forever.",
                "Waiting the same short time between every attempt, so a struggling service is hammered.",
                "Retrying permanent failures such as validation errors, which only wastes workers.",
            ],
            q1=(
                "Why grow the delay between retries instead of using a fixed short wait?",
                "Growing delays give a struggling dependency time to recover instead of being hit at full rate.",
            ),
            homework=(
                "Write `run_with_retries(fail_until, max_attempts, base)` that returns a list of attempts with a "
                "success flag and the wait before the next try, print each attempt, and comment which line "
                "doubles the delay."
            ),
            patterns=["def run_with_retries", "return", "print("],
            mapping=(
                "Airflow's retries and retry_delay, and systemd's RestartSec with StartLimitBurst, are exactly "
                "this planner; the schedule should state the policy rather than hide it."
            ),
        ),
        115: dict(
            topic="Jitter and load smoothing",
            idea=(
                "A schedule that fires thousands of jobs on the hour, or every minute at second zero, creates a "
                "spike that is entirely self-inflicted. The fix is jitter: instead of running at a fixed offset "
                "from the period boundary, each job starts at the boundary plus a small delay, which spreads the "
                "load across the interval. Jitter is different from a longer period, because it does not change "
                "how often the job runs, only when within each interval it starts, and it does not change the "
                "total amount of work. There are a few flavours. A job can jitter from a fixed base, or from its "
                "own last run, or be given a stable per-job offset derived from its identity so its timing is "
                "reproducible. The last is especially useful because a reproducible offset keeps logs and tests "
                "stable while still separating jobs. The trap is not to jitter a job that must run exactly on the "
                "boundary, such as a settlement or a deadline. Today you spread a set of jobs with an explicit "
                "per-job offset, print each start time, and measure the spread, all with integer minutes and no "
                "randomness. An offset that is chosen once and written down is still jitter, and it keeps a test "
                "suite honest."
            ),
            code=(
                "def stagger(base, period, count, span):\n"
                "    starts = []\n"
                "    for i in range(count):\n"
                "        offset = (i * 7) % span\n"
                "        starts.append(base + i * period + offset)\n"
                "    return starts\n"
                "\n"
                "starts = stagger(0, 60, 5, 20)\n"
                "for i, t in enumerate(starts):\n"
                "    print(\"job\", i, \"start\", t)\n"
                "print(\"spread:\", max(starts) - min(starts))\n"
                "\n"
                "assert starts == [0, 67, 134, 181, 248]\n"
                "print(\"offsets spread the load without changing the period\")"
            ),
            variant_b="derive the offset from a job index so the same job always lands in the same slot",
            variant_c="use a larger span and compare how evenly the start times are distributed",
            mistakes=[
                "Running every job exactly on the boundary, which creates a load spike on purpose.",
                "Using jitter on a job that must complete by a deadline, so it occasionally misses.",
                "Confusing jitter with a longer period, which changes how often the job runs.",
            ],
            q1=(
                "How is jitter different from making the period longer?",
                "Jitter only shifts when within each interval a job starts; the period and the total work are unchanged.",
            ),
            homework=(
                "Write `stagger(base, period, count, span)` returning start times with a deterministic per-job "
                "offset, print each start and the spread between earliest and latest, and comment which line "
                "computes the offset."
            ),
            patterns=["def stagger", "enumerate", "print("],
            mapping=(
                "Kubernetes provides pod spreading, Airflow users add jitter to a schedule, and cron users pick "
                "odd minutes; all of it smooths the same thundering herd."
            ),
        ),
        116: dict(
            topic="Idempotency windows",
            idea=(
                "A run may be repeated for reasons outside your control: a retry after a timeout that actually "
                "succeeded, a catch-up after downtime, someone triggering it manually. Idempotency windows make "
                "those repeats harmless by defining the unit of work as a time bucket rather than a single event. "
                "The window is named by dividing the current time by the bucket size, so every event inside the "
                "same bucket maps to the same key; if the key has already been processed, the run is skipped. "
                "That single rule collapses duplicates with no coordination, because the key is derived from the "
                "data rather than stored in advance. The size of the bucket is the important choice. Too small "
                "and a job that straddles a boundary runs twice; too large and genuinely separate events are "
                "merged into one. A window also needs to be bounded in practice, or the set of processed keys "
                "grows forever, which is why real systems expire keys older than a few window lengths. Today you "
                "implement bucketing and a processed-key skip over a short list of integer times, printing what "
                "ran and what was skipped. The whole thing is in-memory data, so the logic is testable in "
                "isolation. Once you trust the bucket, retries and catch-up become safe by construction."
            ),
            code=(
                "def bucket(t, size):\n"
                "    return t // size\n"
                "\n"
                "seen = set()\n"
                "\n"
                "def run(t, size):\n"
                "    key = bucket(t, size)\n"
                "    if key in seen:\n"
                "        return \"skipped\"\n"
                "    seen.add(key)\n"
                "    return \"ran\"\n"
                "\n"
                "for t in (0, 5, 12, 20, 22):\n"
                "    print(\"t=\", t, run(t, 10))\n"
                "\n"
                "assert run(35, 10) == \"ran\"\n"
                "print(\"a window collapses duplicates into one run\")"
            ),
            variant_b="expire keys older than two windows so the processed set stays bounded",
            variant_c="use a larger window size and show two events collapsing into a single run",
            mistakes=[
                "Using an unbounded processed set, so the key store grows without limit.",
                "Choosing a window so small that a job straddling a boundary runs twice.",
                "Keying on the exact timestamp, which defeats the purpose and lets duplicates through.",
            ],
            q1=(
                "Why key idempotency on a time bucket rather than the exact timestamp?",
                "Every event inside one window maps to the same key, so natural duplicates are collapsed instead of re-run.",
            ),
            homework=(
                "Write `bucket(t, size)` and `run(t, size)` that skip a time bucket already recorded in a set, "
                "call it on a list with duplicates inside a window, print each outcome, and comment which line "
                "collapses the duplicate."
            ),
            patterns=["def bucket", "def run", "print("],
            mapping=(
                "Airflow's execution_date and DagRun idempotency, and event-driven systems' dedup keys, all "
                "express the same bucketed-key idea."
            ),
        ),
        117: dict(
            topic="Recording last-successful run",
            idea=(
                "The most important field in any scheduler's state is the time of the last successful run. It is "
                "what next-run calculation starts from, what catch-up measures the gap against, and what an "
                "operator checks first when they suspect a job has quietly stopped. The discipline is that this "
                "record is updated only on success, never on failure or start, which sounds obvious but is the "
                "single most common way a schedule silently breaks: a job that records a start time as if it were "
                "a success will report healthy while producing nothing. A good record holds more than the time. "
                "It names the run that succeeded, so a completion can be matched to a trigger, and it may carry a "
                "short status or a count, so partial progress is visible. Because the record is a value, it can "
                "be written as JSON to a file or a row, and the whole scheduler can be reasoned about without a "
                "database. The failure mode to design against is a crash between doing the work and writing the "
                "record, which is why an idempotent job can safely repeat after such a crash. Today you update a "
                "state dictionary only when a run reports success, over a fixed sequence of runs, and print the "
                "recorded time."
            ),
            code=(
                "def record_success(state, run_id, minute, ok):\n"
                "    if not ok:\n"
                "        return state, \"unchanged\"\n"
                "    return {**state, \"last_success\": minute, \"last_run_id\": run_id}, \"updated\"\n"
                "\n"
                "state = {}\n"
                "for run_id, minute, ok in ((1, 540, True), (2, 600, False), (3, 660, True)):\n"
                "    state, status = record_success(state, run_id, minute, ok)\n"
                "    print(\"run\", run_id, status, \"last_success=\", state.get(\"last_success\"))\n"
                "\n"
                "assert state[\"last_success\"] == 660 and state[\"last_run_id\"] == 3\n"
                "print(\"only success moves the cursor forward\")"
            ),
            variant_b="add a failure counter to the state that resets on success and increments on failure",
            variant_c="serialise the state to a JSON string and load it back before the next run",
            mistakes=[
                "Recording a start time as a success, so a broken job still looks healthy.",
                "Updating the record before the work completes, so a crash leaves a false success.",
                "Starting the next run from the trigger time instead of the last success, which drifts.",
            ],
            q1=(
                "Why update the last-successful record only after the work completes?",
                "A crash before completion would otherwise be recorded as success, and the schedule would skip needed work.",
            ),
            homework=(
                "Write `record_success(state, run_id, minute, ok)` returning an updated state dict and a status "
                "string, feed it a mixed sequence of successes and failures, print the recorded time after each, "
                "and comment which line protects the last success."
            ),
            patterns=["def record_success", "return", "print("],
            mapping=(
                "Airflow stores the last DagRun per DAG, systemd tracks a timestamp in its state, and a plain "
                "JSON file works for a script; all serve the same next-run calculation."
            ),
        ),
        118: dict(
            topic="Testing a schedule",
            idea=(
                "A schedule you cannot test is a schedule you cannot trust, and the way to make one testable is "
                "to keep time as an input rather than reading a clock. Once the next-run function takes the "
                "current time as an argument, a test is just a small table of inputs and expected outputs, and "
                "the whole schedule can be checked in milliseconds with no waiting and no flakiness. The table "
                "should be chosen deliberately around the boundaries, because boundaries are where schedules "
                "break: exactly on a period, one moment before, one moment after, the first run ever, and a long "
                "gap. Each entry is a claim about behaviour, and a failing entry points straight at the rule that "
                "is wrong. This is also how you can safely change a schedule: the tests freeze the old behaviour, "
                "so an accidental change to the cadence shows up immediately rather than the following night when "
                "a report does not arrive. The habit worth building is that the schedule functions stay pure and "
                "the tests are data. Today you write a small assertion table over the next-run function and count "
                "the passing cases, using literal integers so the example is completely deterministic. A "
                "schedule with a table like this is safe to refactor."
            ),
            code=(
                "def next_run(last, period, now):\n"
                "    if last is None:\n"
                "        return now\n"
                "    nxt = last + period\n"
                "    while nxt <= now:\n"
                "        nxt += period\n"
                "    return nxt\n"
                "\n"
                "cases = [\n"
                "    ((None, 60, 900), 900),\n"
                "    ((0, 60, 59), 60),\n"
                "    ((0, 60, 60), 120),\n"
                "    ((540, 60, 600), 660),\n"
                "]\n"
                "failures = 0\n"
                "for args, expected in cases:\n"
                "    got = next_run(*args)\n"
                "    if got != expected:\n"
                "        failures += 1\n"
                "        print(\"FAIL\", args, \"got\", got, \"want\", expected)\n"
                "print(\"passed\", len(cases) - failures, \"of\", len(cases))\n"
                "\n"
                "assert failures == 0"
            ),
            variant_b="add a boundary case one minute before the period and predict whether it passes",
            variant_c="test the catch-up function with the same table style and print the count",
            mistakes=[
                "Testing only the happy path, so boundary behaviour is never checked.",
                "Reading the real clock inside the function, which makes tests flaky and slow.",
                "Asserting on log text instead of the returned value, so the test is brittle.",
            ],
            q1=(
                "Why take the current time as an argument instead of reading the clock inside?",
                "With time as data the function is pure, so tests are deterministic and need no waiting.",
            ),
            homework=(
                "Write `next_run(last, period, now)` and a list of (input, expected) cases including the exact "
                "boundary, run each case, count pass and fail, print the total, and comment which case checks the "
                "boundary."
            ),
            patterns=["def next_run", "for ", "print("],
            mapping=(
                "Airflow ships schedule tests using a mock clock, and CI commonly freezes time; passing time as "
                "data is the portable version of the same trick."
            ),
        ),
        119: dict(
            topic="Review: scheduling checklist",
            idea=(
                "Today you assemble the phase into one checklist, because scheduling bugs are rarely about a "
                "single function and usually about a missing decision. The list runs from trigger to recovery. Is "
                "the cadence described as data, in one place? Does the next-run calculation take time as an input "
                "and pick a boundary strictly after now? Are windows and calendars explicit, with weekends and "
                "holidays kept as data? Is the timezone carried with the value and the reference instant kept in "
                "UTC? If a run is missed, is there a bounded catch-up rather than a stampede or a silent gap? Can "
                "two runs overlap, and if not, is there a lock with an expiry and an owner? Do transient failures "
                "retry with a growing delay, and are permanent ones not retried at all? Is the work idempotent "
                "within a window, and is the last success recorded only after completion? Finally, is the "
                "schedule covered by a small table of boundary tests? A job that answers every question is one "
                "you can leave running unattended, which is the whole point. Today you encode the checklist as "
                "small predicates and run them against a schedule description. Turn each answer into a check and "
                "the review runs itself on every change."
            ),
            code=(
                "schedule = {\n"
                "    \"every_minutes\": 30,\n"
                "    \"window\": (540, 1020),\n"
                "    \"timezone\": \"UTC\",\n"
                "    \"catch_up_cap\": 3,\n"
                "    \"lock_ttl\": 60,\n"
                "    \"max_attempts\": 4,\n"
                "}\n"
                "\n"
                "CHECKS = {\n"
                "    \"cadence is data\": lambda s: s.get(\"every_minutes\", 0) > 0,\n"
                "    \"window is bounded\": lambda s: s[\"window\"][0] < s[\"window\"][1],\n"
                "    \"timezone is set\": lambda s: bool(s.get(\"timezone\")),\n"
                "    \"catch-up is capped\": lambda s: 0 < s.get(\"catch_up_cap\", 0) <= 10,\n"
                "    \"lock has expiry\": lambda s: s.get(\"lock_ttl\", 0) > 0,\n"
                "    \"retries are limited\": lambda s: 1 < s.get(\"max_attempts\", 1) <= 10,\n"
                "}\n"
                "\n"
                "passed = 0\n"
                "for name, check in CHECKS.items():\n"
                "    ok = check(schedule)\n"
                "    passed += ok\n"
                "    print(\"OK\" if ok else \"MISSING\", name)\n"
                "print(\"passed\", passed, \"of\", len(CHECKS))\n"
                "\n"
                "assert passed == len(CHECKS)"
            ),
            variant_b="add a check for idempotency and one for a recorded last success",
            variant_c="run the checklist against a deliberately incomplete schedule and print which items fail",
            mistakes=[
                "Treating scheduling as only the trigger and forgetting locks, retries and the run record.",
                "Answering the checklist once at design time instead of encoding it as checks that run.",
                "Fixing a scheduling bug locally without asking which checklist item was missing.",
            ],
            q1=(
                "Which checklist item most often prevents a schedule from running unattended?",
                "Bounded catch-up together with idempotent work, which make missed and repeated runs harmless.",
            ),
            homework=(
                "Write `checklist(schedule)` that returns the names of the failed checks for a schedule "
                "dictionary, run it on a complete schedule and an incomplete one, print both lists, and comment "
                "which check catches the missing catch-up cap."
            ),
            patterns=["def checklist", "return", "print("],
            mapping=(
                "This is the review an on-call engineer performs on a flaky cron job; the same questions appear "
                "as Airflow DAG reviews and as Kubernetes CronJob checklists."
            ),
        ),
    },
)
