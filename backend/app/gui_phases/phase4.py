"""GUI Applications phase 4, days 120-134: threads, files and responsiveness.

Every example is stdlib-only, offline and deterministic (fixed data, no clock,
no sleeping, no real threads, no network), so the applier can execute it and
produce the same output on every run. Workers, queues, timers and cancellation
tokens are modelled as plain data structures; the UI thread is a loop with a
budget, and operations are counted rather than timed. That keeps the contract of
a responsive desktop application visible before Tkinter or Qt supplies the real
threading primitives.
"""

PHASE = (
    "Threads, Files and Responsiveness",
    "Keep the UI thread free by moving work to workers, handing results back through queues, and proving it with deterministic tests.",
    {
        120: dict(
            topic="Orientation: the UI thread",
            idea=(
                "A GUI framework gives you exactly one thread that is allowed to touch widgets, and everything else in "
                "this phase is a consequence of that rule. That thread runs the event loop: it waits for input, "
                "dispatches a handler, lets the handler update the screen, and returns so the next event can be "
                "delivered. When people say an application is responsive, they mean this thread keeps coming back for "
                "more work quickly. It does not mean the program is doing nothing; a well-behaved app can be "
                "computing heavily in the background while the interface still scrolls, resizes and repaints. The "
                "mental model to install today is a loop with a budget. Each turn should do a small bounded amount of "
                "work, then yield, so redraws and input are never stuck behind one enormous operation. Think of the UI "
                "thread as a scarce resource shared by every widget on screen, not as a place to put your algorithm. "
                "Once you accept the budget, threads stop looking like a clever trick and start looking like the "
                "obvious way to move work off that budget without breaking the single-owner rule. The code models one "
                "pass of that loop over a fixed list of jobs and marks which ones were small enough to run inline."
            ),
            code=(
                'def run_ui(jobs, budget):\n'
                '    done, deferred, turns = [], [], 0\n'
                '    for job in jobs:\n'
                '        turns += 1\n'
                '        if job["cost"] > budget:\n'
                '            deferred.append(job["name"])\n'
                '        else:\n'
                '            done.append(job["name"])\n'
                '    return done, deferred, turns\n'
                '\n'
                'jobs = [\n'
                '    {"name": "load settings", "cost": 2},\n'
                '    {"name": "parse report", "cost": 9},\n'
                '    {"name": "redraw", "cost": 1},\n'
                ']\n'
                'done, deferred, turns = run_ui(jobs, budget=4)\n'
                'print("ui turns:", turns)\n'
                'print("inline:", done)\n'
                'print("deferred:", deferred)\n'
                'assert "parse report" in deferred\n'
                'print("the ui thread finishes its turn")'
            ),
            variant_b='lower the budget to 1 and print which jobs are still handled inline',
            variant_c='let each turn carry several jobs up to the budget and print the number of turns used',
            mistakes=[
                "Drawing or updating widgets from the worker instead of from the thread that owns them.",
                "Starting threads first when the real fix is to keep each turn of the event loop short.",
                "Treating the event loop as free, so a long handler is written without any thought about yields.",
            ],
            q1=(
                "What exactly does it mean for the UI thread to be busy?",
                "It is inside a handler and cannot pop the next event, so input and redraw wait until that handler returns.",
            ),
            homework=(
                "Write `run_ui(jobs, budget)` that returns `(done, deferred, turns)`, classifying each job by "
                "whether its cost fits the per-turn budget. Run it on five jobs where two exceed the budget, print "
                "the two lists and the turn count, and comment which line enforces the budget."
            ),
            patterns=["def run_ui", "budget", "print("],
            mapping=(
                "Tkinter and Qt both funnel widget calls through one thread; `mainloop` and `exec` are that thread's "
                "turn-taking, and every responsiveness rule in this phase protects it."
            ),
        ),
        121: dict(
            topic="Long tasks and the freeze test",
            idea=(
                "The freeze test turns a vague complaint, the window felt stuck, into a number: how long did the event "
                "loop go without completing a turn? You do not need a profiler to answer it. Write down the work the "
                "handler performs as a timeline, cut it into spans, and find the longest span during which no event "
                "could be processed. If that span is longer than a few dozen milliseconds, users notice; if it is "
                "seconds, the operating system may paint a not-responding ghost over your window. The useful part of "
                "this exercise is that it separates two questions people constantly confuse: how much total work is "
                "there, and what is the longest uninterrupted stretch of it. Splitting a twelve-unit task into four "
                "three-unit chunks does not reduce the total work at all, but it lowers the worst stall from twelve to "
                "three, which is exactly what responsiveness measures. That is why progress bars move and buttons "
                "still highlight during a large import. Today you build a tiny stall calculator over fixed integer "
                "spans. No clock is involved, because the ratio is what matters, and a deterministic model of the "
                "spans lets you test the reasoning without waiting on a real machine."
            ),
            code=(
                'def longest_stall(spans):\n'
                '    worst = 0\n'
                '    for start, end in spans:\n'
                '        worst = max(worst, end - start)\n'
                '    return worst\n'
                '\n'
                'def schedule(chunks):\n'
                '    spans, clock = [], 0\n'
                '    for chunk in chunks:\n'
                '        spans.append((clock, clock + chunk))\n'
                '        clock += chunk\n'
                '    return spans\n'
                '\n'
                'big = schedule([12])\n'
                'chunked = schedule([3, 3, 3, 3])\n'
                'print("one big call stall:", longest_stall(big))\n'
                'print("four chunks stall:", longest_stall(chunked))\n'
                'print("redraws between chunks:", len(chunked) - 1)\n'
                'assert longest_stall(big) == 12\n'
                'assert longest_stall(chunked) == 3\n'
                'print("the freeze test measures the longest stall")'
            ),
            variant_b='split the work into six chunks of two and compare the worst stall with the four-chunk plan',
            variant_c='add a fixed one-unit gap between chunks and show what it does to the total elapsed time',
            mistakes=[
                "Measuring total work and calling it responsiveness, though chunking changes the stall and not the total.",
                "Assuming a fast development machine proves the interface will stay smooth on slower hardware.",
                "Chunking so finely that scheduling overhead between the pieces costs more than the original stall.",
            ],
            q1=(
                "Why can splitting a long task leave total work unchanged yet make the app responsive?",
                "The longest uninterrupted stretch shrinks, so the event loop gets to process input and redraws between chunks.",
            ),
            homework=(
                "Write `longest_stall(spans)` that takes a list of `(start, end)` integer spans and returns the "
                "longest single span. Feed it the one-call and four-chunk schedules, print both results plus the "
                "difference, and comment why splitting work lowers the worst stall without lowering total work."
            ),
            patterns=["def longest_stall", "max(", "print("],
            mapping=(
                "This is what `after` in Tkinter and `QTimer` slices in Qt are for: break a long job into pieces and "
                "return to the loop between them so repaints can happen."
            ),
        ),
        122: dict(
            topic="Worker threads with results",
            idea=(
                "Once work moves off the UI thread, the one thing the interface actually needs is the result, "
                "delivered at a moment when it is safe to draw. A worker that computes correctly but hands its value "
                "back by poking a widget has solved the calculation and broken the application. The safe pattern is a "
                "handoff: the worker writes its result somewhere the UI thread controls, and the UI thread picks it up "
                "on a later turn of its loop. In this model a worker is a small object with a pending list and a step "
                "function. The UI calls step once per turn, and each call retires one job and appends a result. "
                "Nothing runs concurrently; the sequence is completely deterministic, which is the point. You are "
                "learning the contract, not the scheduler. The contract has three clauses: submit only data, never "
                "widget references; keep results separate from pending work; and let the UI decide when to read them. "
                "Real thread pools add locking, but a lock does not change those clauses, it only makes them "
                "enforceable across cores. Today you implement that handoff and watch results appear one UI tick at "
                "a time, which is exactly the rhythm a signals and slots connection gives you."
            ),
            code=(
                'class Worker:\n'
                '    def __init__(self):\n'
                '        self.pending = []\n'
                '        self.results = []\n'
                '\n'
                '    def submit(self, job):\n'
                '        self.pending.append(job)\n'
                '\n'
                '    def step(self):\n'
                '        if self.pending:\n'
                '            job = self.pending.pop(0)\n'
                '            self.results.append((job["id"], job["value"] * 2))\n'
                '\n'
                '    def drain(self):\n'
                '        for _ in range(len(self.pending)):\n'
                '            self.step()\n'
                '        return list(self.results)\n'
                '\n'
                'w = Worker()\n'
                'for i, value in enumerate([3, 4, 5]):\n'
                '    w.submit({"id": i, "value": value})\n'
                'print("before polls:", w.results)\n'
                'for tick in range(2):\n'
                '    w.step()\n'
                '    print("ui tick", tick, "results", w.results)\n'
                'print("after drain:", w.drain())\n'
                'assert w.results == [(0, 6), (1, 8), (2, 10)]'
            ),
            variant_b='submit a job that returns a string instead of a number and print the drained results',
            variant_c='make step return the result it produced and let the caller decide where to store it',
            mistakes=[
                "Returning values by touching widgets from the worker instead of handing them to the UI thread.",
                "Reading the worker's pending list directly from the UI and assuming it is complete.",
                "Submitting a widget reference as part of a job, so the worker captures UI state it may not own.",
            ],
            q1=(
                "Why should a worker hand back plain data rather than a widget or a callback that draws?",
                "Plain data crosses the boundary safely; drawing must happen on the UI thread at a moment the UI controls.",
            ),
            homework=(
                "Write `class Worker` with `submit(job)`, `step()` and `drain()` where each `step` retires one "
                "pending job into a results list. Submit three jobs, call `step` twice while printing results after "
                "each call, then call `drain`, and assert all three results exist exactly once."
            ),
            patterns=["class Worker", "def step", "drain"],
            mapping=(
                "Qt's `QThread` with signals, and Tkinter's pattern of a worker posting to a `queue.Queue` checked by "
                "`after`, are both this handoff with real thread primitives underneath."
            ),
        ),
        123: dict(
            topic="Queues between workers and UI",
            idea=(
                "A queue is the seam between a worker and the interface, and its shape teaches you what is safe to "
                "send across that seam. Widgets cannot cross it: a widget belongs to the UI thread and carries "
                "toolkit state that is not safe to mutate elsewhere. Plain values can cross it: strings, numbers, "
                "tuples, small dictionaries describing what happened. That is why real applications post messages "
                "like progress at forty percent or finished with two hundred rows, and let the UI thread decide "
                "which label to touch. Modelling the queue explicitly also shows you the failure modes. A worker that "
                "posts faster than the UI polls builds an unbounded backlog; a UI that polls in a tight loop wastes "
                "turns and starves input; a message consumer that assumes a fixed order can be surprised when two "
                "workers interleave. Today you run a worker that fills an inbox and a UI that drains it in bounded "
                "polls, printing the screen after each poll. The fixed list of messages keeps it deterministic. Notice "
                "that the UI never reads the worker's internal list; the only shared object is the queue, and that is "
                "what makes the design reviewable and safe to extend. A queue also gives you one obvious place to measure backlog."
            ),
            code=(
                'def worker(jobs, out):\n'
                '    for job in jobs:\n'
                '        out.append({"job": job, "value": len(job)})\n'
                '    return len(jobs)\n'
                '\n'
                'def ui_poll(inbox, screen):\n'
                '    while inbox:\n'
                '        msg = inbox.pop(0)\n'
                '        screen.append(msg["job"] + ":" + str(msg["value"]))\n'
                '    return len(screen)\n'
                '\n'
                'inbox, screen = [], []\n'
                'sent = worker(["alpha", "beta", "gamma"], inbox)\n'
                'print("worker posted:", sent, "in queue:", len(inbox))\n'
                'print("screen before poll:", screen)\n'
                'for polls in range(2):\n'
                '    ui_poll(inbox, screen)\n'
                '    print("poll", polls + 1, "screen:", screen)\n'
                'assert screen == ["alpha:5", "beta:4", "gamma:5"]\n'
                'assert inbox == []\n'
                'print("the queue is the only shared object")'
            ),
            variant_b='post a duplicate message and let the UI skip it by comparing with the last rendered value',
            variant_c='cap the inbox and have the worker block instead of appending when it is full',
            mistakes=[
                "Putting widget objects into the queue so the UI thread is bypassed entirely.",
                "Letting the worker append without bound while the UI polls rarely, growing the queue forever.",
                "Draining the queue in a tight loop with no limit, so input events never get a turn.",
            ],
            q1=(
                "Why can a queue carry messages but not widgets?",
                "A widget belongs to the UI thread and its state is not safe to touch elsewhere, while a message is a plain value the UI can apply itself.",
            ),
            homework=(
                "Write `drain_inbox(inbox, screen, limit)` that pops at most `limit` messages, formats each as "
                "`name:value`, appends to the screen list and returns the number consumed. Fill an inbox with four "
                "messages, poll in two rounds, print the screen after each round, and comment why widgets never go "
                "into the queue."
            ),
            patterns=["def drain_inbox", "limit", "print("],
            mapping=(
                "The standard Tkinter pattern is a `queue.Queue` written by the worker and drained in an `after` "
                "callback; Qt replaces the queue with queued signal connections, but the seam is identical."
            ),
        ),
        124: dict(
            topic="Cancellation and timeouts",
            idea=(
                "A task that cannot be cancelled owns your application, because the user cannot get their window back "
                "until it finishes. Cancellation and timeouts are therefore interface features, not worker features: "
                "the UI must be able to say stop, and the worker must check that request often enough for stopping to "
                "feel immediate. The mechanism is deliberately boring. A cancellation flag and a budget counter are "
                "read at safe points in the work loop; when either fires, the worker returns a status instead of a "
                "result. Good work loops are written so those checks happen between natural units, a row, a page, a "
                "file, never in the middle of a half-applied update. The same structure gives you timeouts for free: "
                "a deadline is a budget that expires whether or not anyone pressed a button. Distinguish three "
                "endings, because the UI treats them differently: finished, cancelled by the user, and timed out by "
                "policy. Only the first should update the success path. Today you run the same job under a small "
                "budget, a sufficient budget, and an early cancellation, and compare the returned status and the "
                "amount of work committed. Counters stand in for the clock so the results are reproducible, and the same statuses appear regardless of machine speed."
            ),
            code=(
                'class Job:\n'
                '    def __init__(self, steps):\n'
                '        self.steps = steps\n'
                '        self.done = 0\n'
                '\n'
                'def run(job, budget, cancelled=False):\n'
                '    while job.done < job.steps:\n'
                '        if cancelled:\n'
                '            return "cancelled", job.done\n'
                '        if job.done >= budget:\n'
                '            return "timed out", job.done\n'
                '        job.done += 1\n'
                '    return "finished", job.done\n'
                '\n'
                'status, done = run(Job(10), budget=4)\n'
                'print("tight budget:", status, done)\n'
                'status2, done2 = run(Job(3), budget=4)\n'
                'print("enough budget:", status2, done2)\n'
                'status3, done3 = run(Job(10), budget=10, cancelled=True)\n'
                'print("cancelled:", status3, done3)\n'
                'assert (status, done) == ("timed out", 4)\n'
                'assert (status2, done2) == ("finished", 3)\n'
                'assert (status3, done3) == ("cancelled", 0)\n'
                'print("three endings, three ui outcomes")'
            ),
            variant_b='check cancellation only every three steps and observe how much work is committed before it stops',
            variant_c='start the budget at zero and confirm the job times out without doing any work',
            mistakes=[
                "Killing a worker thread abruptly instead of asking it to stop at a safe point.",
                "Reporting cancellation as success, so the UI shows partial data as if it were complete.",
                "Never checking the flag inside a long inner loop, so cancel takes effect minutes later.",
            ],
            q1=(
                "Why is a timeout just a cancellation budget that expires on its own?",
                "Both stop the work loop at a safe point and return a non-success status; the only difference is who triggered the stop.",
            ),
            homework=(
                "Write `run_job(steps, budget, cancelled=False)` returning `(status, committed)` where status is "
                "one of finished, cancelled or timed out. Call it with a generous budget, an insufficient budget and "
                "an early cancellation, print all three outcomes, and assert that a cancelled job commits nothing."
            ),
            patterns=["def run_job", "cancelled", "assert"],
            mapping=(
                "Real code uses a `threading.Event` or an atomic flag checked in the work loop; in Qt, "
                "`QThread.requestInterruption` and `isInterruptionRequested` play the same role."
            ),
        ),
        125: dict(
            topic="Progress reporting",
            idea=(
                "Progress reporting is a promise about the future, so it has to be honest in both directions. A bar "
                "that jumps from ten percent to ninety and then hangs for a minute is worse than no bar, because the "
                "user has been told a story that turns out to be false. The two hard parts are measuring and "
                "translating. Measuring means knowing how much work there is in units the worker actually completes, "
                "such as rows read or files copied, not in wall-clock guesses. Translating means mapping completed "
                "units onto a percentage without dividing by zero and without claiming one hundred before the last "
                "unit is committed. A third part is often forgotten: the UI does not need every update. Emitting at "
                "every row can flood the queue and cost more than the work itself, so workers report at thresholds, "
                "every few percent or every fixed number of units. Today you compute progress from a fixed list of "
                "job sizes, emit an update only when the percentage has advanced by a chosen step, and assert the "
                "series is increasing and ends at one hundred. The threshold is a parameter, which is exactly where "
                "a real application would tune it, and the tuning shows up as a changed message count rather than changed correctness."
            ),
            code=(
                'def progress_updates(sizes, step):\n'
                '    total = sum(sizes)\n'
                '    done, updates, last = 0, [], 0\n'
                '    for size in sizes:\n'
                '        done += size\n'
                '        pct = done * 100 // total\n'
                '        if not updates or pct - last >= step:\n'
                '            updates.append(pct)\n'
                '            last = pct\n'
                '    return total, updates\n'
                '\n'
                'total, updates = progress_updates([5, 10, 25, 60], step=20)\n'
                'print("total work:", total)\n'
                'print("updates:", updates)\n'
                'assert updates == sorted(updates)\n'
                'assert updates[-1] == 100\n'
                'print("progress is computed from completed units")\n'
                '\n'
                '_, coarse = progress_updates([5, 10, 25, 60], step=50)\n'
                'print("coarse updates:", coarse)\n'
                'assert coarse[-1] == 100'
            ),
            variant_b='raise the step to 50 and print the coarser series while keeping the final hundred',
            variant_c='emit progress after every job and print how many more messages the queue must carry',
            mistakes=[
                "Dividing by a total that can be zero before any work has been counted.",
                "Emitting an update per row so the queue costs more than the actual work.",
                "Dropping the final update because it did not pass the threshold, leaving the bar incomplete.",
            ],
            q1=(
                "Why should progress be derived from completed units rather than elapsed time?",
                "Units are known and monotonic, so the bar reflects real work instead of a guess that can stall or run backwards.",
            ),
            homework=(
                "Write `progress_updates(sizes, step)` that turns a list of work sizes into percentages and emits a "
                "value only when it has advanced by at least `step` from the last emitted one. Test with sizes 4, 12, "
                "30, 54 and step 15, print the series, and assert it is increasing and ends at 100."
            ),
            patterns=["def progress_updates", "step", "assert"],
            mapping=(
                "Tkinter's `ttk.Progressbar` and Qt's `QProgressBar` only render a number; workers post the number to "
                "the UI thread, usually rate limited, and never touch the bar directly."
            ),
        ),
        126: dict(
            topic="File I/O off the main loop",
            idea=(
                "File work is the classic reason a desktop window freezes: the developer wrote a tidy loop that reads "
                "a file and fills a list, and it was fast on a small test file. On a real file the call blocks the "
                "only thread allowed to paint. The fix is not magic; it is the same handoff as any other long job, "
                "with one addition: the worker must read in bounded chunks so cancellation and progress have "
                "somewhere to happen. Chunking also keeps memory predictable on large inputs. In this headless model "
                "the file is an `io.StringIO`, so nothing touches the disk, but the shape of the code is the real "
                "shape: open, read a chunk, process it, publish a count, repeat until empty. Two details matter in "
                "production. Encoding and newline handling should be explicit rather than left to the platform "
                "default, and errors must be captured and reported as values instead of escaping the worker. Today "
                "you read a fixed in-memory document two lines at a time, count the read calls, and print the "
                "accumulated batches. The counts are the lesson: a chunked reader has a visible, testable rhythm that "
                "a single blocking call never had, and it makes the difference between a frozen window and a moving progress line testable."
            ),
            code=(
                'import io\n'
                '\n'
                'def read_chunks(stream, per_chunk):\n'
                '    batches, calls = [], 0\n'
                '    while True:\n'
                '        lines = stream.readlines(per_chunk)\n'
                '        if not lines:\n'
                '            break\n'
                '        calls += 1\n'
                '        batches.append([line.strip() for line in lines])\n'
                '    return batches, calls\n'
                '\n'
                'data = io.StringIO("id,name\\n1,ada\\n2,grace\\n3,alan\\n4,edsger\\n")\n'
                'batches, calls = read_chunks(data, per_chunk=2)\n'
                'for index, batch in enumerate(batches):\n'
                '    print("batch", index, batch)\n'
                'print("read calls:", calls)\n'
                'assert calls == len(batches)\n'
                'assert ["1,ada"] in batches\n'
                'print("bounded reads keep the loop responsive")'
            ),
            variant_b='read the whole stream in one call and print how many read calls the same data takes',
            variant_c='skip blank lines while reading and assert no empty string ends up in any batch',
            mistakes=[
                "Reading a whole large file into memory on the UI thread before doing any processing.",
                "Leaving encoding to the platform default so the same file breaks on another machine.",
                "Letting an I/O exception escape the worker, where nobody catches it and the UI stays busy forever.",
            ],
            q1=(
                "Why does chunked reading help responsiveness even when the total file is the same?",
                "Each read returns quickly, so the worker can check cancellation, report progress, and publish counts between chunks.",
            ),
            homework=(
                "Write `read_chunks(stream, per_chunk)` that uses `io.StringIO` and `readlines(per_chunk)` to return "
                "a list of stripped line batches plus the number of read calls. Run it on five lines with a chunk of "
                "two, print each batch and the call count, and comment why bounded reads let cancellation happen."
            ),
            patterns=["def read_chunks", "io.StringIO", "readlines"],
            mapping=(
                "In Tkinter the read runs in a worker thread and posts counts back through a queue; Qt's "
                "`QFile`/`QTextStream` code lives in a `QThread` or a `QtConcurrent` task for the same reason."
            ),
        ),
        127: dict(
            topic="Network calls without blocking",
            idea=(
                "Network calls are file I/O with much worse manners: the server can be slow, the connection can "
                "stall, and the failure can arrive long after the user stopped caring. The single rule that keeps an "
                "interface alive is that no request is ever awaited on the UI thread. You send the request, keep a "
                "handle, and check back later, exactly as with a worker result. That checkback can be a timer, a "
                "completion callback, or a poll, but it must be something the event loop controls. The second rule is "
                "that the UI must have a state for in flight, and it must render it, because a spinner is the user's "
                "evidence that the application heard them. The third is that responses must be matched to their "
                "request, since two calls can return out of order; an identifier is enough. Today a fake transport "
                "holds canned responses and decrements a countdown on each poll, so the sequence is fully "
                "deterministic and no socket exists. You will see requests stay in flight for two polls while the "
                "loop keeps turning. Real libraries hide the transport, but they cannot hide these three rules, and "
                "code that ignores them will block or cross wires no matter which client it uses."
            ),
            code=(
                'class FakeTransport:\n'
                '    def __init__(self):\n'
                '        self.inflight = []\n'
                '        self.cache = {"users": "[ada, grace]", "health": "ok"}\n'
                '\n'
                '    def send(self, name):\n'
                '        if name in self.cache:\n'
                '            self.inflight.append({"name": name, "after": 2})\n'
                '\n'
                '    def poll(self):\n'
                '        ready = []\n'
                '        for req in list(self.inflight):\n'
                '            req["after"] -= 1\n'
                '            if req["after"] <= 0:\n'
                '                ready.append(req["name"])\n'
                '                self.inflight.remove(req)\n'
                '        return [(name, self.cache[name]) for name in ready]\n'
                '\n'
                'net = FakeTransport()\n'
                'net.send("users")\n'
                'net.send("health")\n'
                'for tick in range(3):\n'
                '    print("tick", tick, "inflight", len(net.inflight), "ready", net.poll())\n'
                'assert net.inflight == []\n'
                'print("ui kept turning while requests were in flight")'
            ),
            variant_b='send an unknown name and confirm no request is created for a missing cached reply',
            variant_c='make one request finish after three polls and print the order responses are matched',
            mistakes=[
                "Calling a blocking HTTP client directly from a button handler and waiting for the response.",
                "Assuming responses return in the order the requests were sent.",
                "Forgetting to clear the busy state when a request fails, so the spinner runs forever.",
            ],
            q1=(
                "Why must a network response carry a request identifier?",
                "Two requests can complete out of order, so the UI needs the identifier to match a reply to the work that asked for it.",
            ),
            homework=(
                "Write `class FakeTransport` with `send(name)` and `poll()` where each request finishes after two "
                "polls and returns its cached payload. Send two names, poll three times printing the ready list each "
                "time, and assert nothing remains in flight while the loop kept running."
            ),
            patterns=["class FakeTransport", "def poll", "assert"],
            mapping=(
                "Qt's `QNetworkAccessManager` signals completion asynchronously; Tkinter callers typically run "
                "`urllib` in a worker and post the parsed result back through a queue."
            ),
        ),
        128: dict(
            topic="Errors from workers",
            idea=(
                "An error inside a worker cannot be allowed to vanish, and it cannot be allowed to escape the way an "
                "exception in a normal function would. The UI thread is not on the worker's call stack, so there is "
                "nobody to catch it there; an uncaught exception in a real thread usually prints to a log the user "
                "never sees and leaves the interface waiting forever. The reliable pattern is to make failure a "
                "value. Every job returns either a success carrying its data or a failure carrying a category and a "
                "human-readable message, and the UI branch that consumes results has an explicit failure path that "
                "updates the screen and clears the busy state. That branch is where you decide policy: retry, offer "
                "a file picker, or show a toast. Returning exception types rather than raw exception objects also "
                "keeps the boundary clean and serialisable. Today you run three division jobs, one of which divides "
                "by zero, and collect the outcomes without letting the loop crash. The assertion checks that exactly "
                "one failure was reported. The habit to keep is simple: at every thread or process boundary, convert "
                "exceptions into data before they cross, because a log line the user never opens is not error handling."
            ),
            code=(
                'def worker_result(a, b):\n'
                '    try:\n'
                '        return {"ok": True, "value": a / b}\n'
                '    except ZeroDivisionError as exc:\n'
                '        return {"ok": False, "error": type(exc).__name__}\n'
                '\n'
                'pairs = [(10, 2), (3, 0), (9, 3), (5, 0)]\n'
                'results, failures = [], 0\n'
                'for a, b in pairs:\n'
                '    result = worker_result(a, b)\n'
                '    results.append(result)\n'
                '    if not result["ok"]:\n'
                '        failures += 1\n'
                '        print("worker error:", result["error"], "for", (a, b))\n'
                '\n'
                'values = [r["value"] for r in results if r["ok"]]\n'
                'print("ok values:", values)\n'
                'print("processed:", len(results), "failures:", failures)\n'
                'assert len(results) == 4 and failures == 2\n'
                'print("the ui thread survived every result")'
            ),
            variant_b='treat a negative divisor as a custom invalid input failure and count it separately',
            variant_c='return a message string alongside the error type and print it in the ui branch',
            mistakes=[
                "Letting the exception propagate in a thread where nothing catches it, leaving the UI waiting.",
                "Re-raising on the UI thread without clearing the busy state first.",
                "Reporting a failure as an empty success, so the screen shows nothing and claims it worked.",
            ],
            q1=(
                "Why return failures as values instead of letting worker exceptions propagate?",
                "The UI is not on the worker's stack, so a returned value is the only reliable way for the failure to reach a handler that can react.",
            ),
            homework=(
                "Write `worker_result(a, b)` returning `{'ok': True, 'value': ...}` or `{'ok': False, 'error': "
                "...}` for division. Run it over four pairs including a zero divisor, collect the outcomes, print "
                "the values and error labels, and assert the loop processed every pair without raising."
            ),
            patterns=["def worker_result", "ZeroDivisionError", "assert"],
            mapping=(
                "Qt reports queued-connection errors through signals, and `concurrent.futures` stores exceptions on "
                "the future until the UI calls `result()`; both keep failure as data at the boundary."
            ),
        ),
        129: dict(
            topic="Polling with timers",
            idea=(
                "Polling has a bad reputation, and most of it comes from polling badly: a loop that spins as fast as "
                "it can, burning a core to ask whether anything changed. Scheduled polling is a different animal. The "
                "toolkit gives you a timer, `after` in Tkinter or `QTimer` in Qt, and you ask it to call a function "
                "later; when that function runs, it does one bounded check and schedules the next one. The interface "
                "stays free between checks, and the cost is proportional to the interval you chose rather than to the "
                "speed of the machine. The design questions are the interval, the stop condition, and the interaction "
                "with shutdown. Too fast wastes work and floods the queue; too slow feels laggy; and a timer that "
                "keeps firing after the window closes is a classic leak. Choosing the interval is a product decision "
                "as much as a technical one. Today you model ticks as a list of fixed millisecond offsets and poll a "
                "pending list once per tick, stopping as soon as the list is empty. It is a fake clock, but it lets "
                "you assert the exact poll times, which is how you would test scheduling in a real app without "
                "sleeping in a test suite."
            ),
            code=(
                'def timer_ticks(interval_ms, count):\n'
                '    return [index * interval_ms for index in range(count)]\n'
                '\n'
                'def poll_until_idle(pending, ticks):\n'
                '    seen = []\n'
                '    for tick in ticks:\n'
                '        if not pending:\n'
                '            break\n'
                '        seen.append((tick, pending.pop(0)))\n'
                '    return seen, len(pending)\n'
                '\n'
                'pending = ["job-a", "job-b", "job-c"]\n'
                'seen, left = poll_until_idle(pending, timer_ticks(250, 5))\n'
                'print("poll times:", [tick for tick, _ in seen])\n'
                'print("jobs seen:", [job for _, job in seen])\n'
                'print("left:", left)\n'
                'assert [tick for tick, _ in seen] == [0, 250, 500]\n'
                'assert left == 0\n'
                'print("a timer turns polling into scheduled work")'
            ),
            variant_b='use a 100 ms interval and print how many ticks pass before the queue is empty',
            variant_c='leave one job pending and confirm polling stops without processing a phantom result',
            mistakes=[
                "Scheduling the next tick inside the poll before checking whether work is finished, so it never stops.",
                "Polling in a `while` loop with no delay and freezing the UI with busy work.",
                "Forgetting to cancel the timer when the window closes, so it fires into a destroyed widget.",
            ],
            q1=(
                "What makes scheduled polling different from a busy loop?",
                "The timer returns control to the event loop between checks, so the cost follows the chosen interval instead of the CPU speed.",
            ),
            homework=(
                "Write `poll_on_ticks(pending, interval, count)` that builds tick offsets from `interval` and consumes "
                "one pending item per tick until the list is empty. Print the tick times actually used and the "
                "remaining count, and assert that no tick fires after the work is done."
            ),
            patterns=["def poll_on_ticks", "range(", "assert"],
            mapping=(
                "Tkinter's `widget.after(ms, callback)` and Qt's `QTimer` with `setInterval` are the real versions of "
                "this schedule; reschedule from inside the callback and cancel on close."
            ),
        ),
        130: dict(
            topic="Rate limiting updates",
            idea=(
                "Every widget update costs a layout, a repaint and a wake-up of the UI thread, so a worker that emits "
                "progress for every row can make the application slower than doing the work quietly. Rate limiting is "
                "the discipline of deciding how often the interface is allowed to hear from a producer, independent "
                "of how often the producer has news. There are two common shapes. Throttling keeps at most one "
                "update per interval and drops the ones in between. Coalescing keeps the latest value and sheds "
                "duplicates, which is usually what progress wants, since only the newest percentage matters. Both "
                "need a policy for the final update, because dropping the last message leaves a bar stuck at "
                "ninety-eight percent. Today you walk a fixed event list with timestamps and keep an event only when "
                "it is at least a chosen gap after the last kept one. The dropped count is printed alongside the kept "
                "percentages, and the assertions pin the exact result. Notice that the policy is data, not a hidden "
                "constant, so you can test two gaps and compare. In a real app the same logic sits in a small "
                "publisher and keeps the queue from becoming the bottleneck."
            ),
            code=(
                'def throttle(events, min_gap):\n'
                '    kept, dropped, last = [], 0, None\n'
                '    for event in events:\n'
                '        if last is None or event["t"] - last >= min_gap:\n'
                '            kept.append(event)\n'
                '            last = event["t"]\n'
                '        else:\n'
                '            dropped += 1\n'
                '    return kept, dropped\n'
                '\n'
                'events = [\n'
                '    {"t": 0, "pct": 1},\n'
                '    {"t": 10, "pct": 2},\n'
                '    {"t": 20, "pct": 3},\n'
                '    {"t": 120, "pct": 4},\n'
                '    {"t": 130, "pct": 5},\n'
                '    {"t": 240, "pct": 6},\n'
                ']\n'
                'kept, dropped = throttle(events, min_gap=100)\n'
                'print("kept times:", [e["t"] for e in kept])\n'
                'print("kept pct:", [e["pct"] for e in kept])\n'
                'print("dropped:", dropped)\n'
                'assert [e["t"] for e in kept] == [0, 120, 240]\n'
                'assert dropped == 3\n'
                'print("the ui hears only what it can use")'
            ),
            variant_b='lower the gap to 50 and print which events survive and how many are dropped',
            variant_c='always keep the final event even if it falls inside the gap, and assert the last percentage appears',
            mistakes=[
                "Updating a label for every row read, so repaint cost dominates the actual work.",
                "Dropping the final update and leaving the progress bar short of the end.",
                "Using a fixed gap for every screen without measuring whether the widget can keep up.",
            ],
            q1=(
                "Why must the final event be kept even when it falls inside the minimum gap?",
                "Otherwise the last state never reaches the screen and the UI looks unfinished though the work completed.",
            ),
            homework=(
                "Write `throttle(events, min_gap)` returning `(kept, dropped)` for events carrying an integer `t`. "
                "Run it twice with gaps of 50 and 100 on the same six events, print both kept timestamp lists and "
                "the drop counts, and comment why the final event must always be kept."
            ),
            patterns=["def throttle", "min_gap", "print("],
            mapping=(
                "Qt has `QElapsedTimer` guards around `setValue`, and Tkinter apps commonly coalesce queue messages "
                "before touching a `ttk.Progressbar`; the policy belongs above the toolkit call."
            ),
        ),
        131: dict(
            topic="Graceful shutdown",
            idea=(
                "Shutdown is the part of a threaded application that everyone writes last and debugs at three in the "
                "morning. A clean shutdown has an order, and the order is the whole design. First stop accepting new "
                "work, so nothing arrives while you are tearing down. Then tell workers to stop, letting them reach a "
                "safe point rather than killing them mid-write. Then drain what is already queued, because those "
                "results belong to work the user already started. Finally release resources and only then let the "
                "window go away. Skip the first step and a late message crashes a half-dead object; skip the drain "
                "and users lose the last few rows they watched being processed; kill workers instead of asking and "
                "you get truncated files. The UI also needs a visible state for shutting down, so the user is not "
                "clicking a dead button that appears alive. Today you model an application object with a running "
                "flag, a queue, and a shutdown method that closes the gate and drains in a defined order. A "
                "submission after shutdown is refused and printed. The assertion checks the exact number of drained "
                "jobs, which is the part most implementations get wrong. Shutdown is a sequence, so make that sequence explicit in code."
            ),
            code=(
                'class App:\n'
                '    def __init__(self):\n'
                '        self.running = True\n'
                '        self.queue = ["save", "flush"]\n'
                '        self.closed = []\n'
                '\n'
                '    def submit(self, job):\n'
                '        if not self.running:\n'
                '            print("refused after shutdown:", job)\n'
                '            return False\n'
                '        self.queue.append(job)\n'
                '        return True\n'
                '\n'
                '    def shutdown(self):\n'
                '        self.running = False\n'
                '        while self.queue:\n'
                '            self.closed.append(self.queue.pop(0))\n'
                '        return len(self.closed)\n'
                '\n'
                'app = App()\n'
                'app.submit("backup")\n'
                'print("queued:", len(app.queue))\n'
                'drained = app.shutdown()\n'
                'app.submit("late")\n'
                'print("drained:", drained, app.closed)\n'
                'assert drained == 3\n'
                'assert not app.running\n'
                'print("close the gate, then drain, then refuse")'
            ),
            variant_b='shutdown twice in a row and confirm the second call drains nothing and does not raise',
            variant_c='keep a separate stop event per worker and print which workers acknowledged the stop request',
            mistakes=[
                "Destroying the window while workers are still writing, so callbacks hit dead objects.",
                "Closing the queue before draining it, losing results for work the user already started.",
                "Leaving the running flag set, so a stray submission restarts work during teardown.",
            ],
            q1=(
                "Why is refusing new work the first step of shutdown rather than the last?",
                "Once the gate is closed nothing can arrive mid-teardown, so draining and stopping happen against a fixed set of pending work.",
            ),
            homework=(
                "Write `class App` with `submit(job)` and `shutdown()`, where shutdown flips a running flag, drains "
                "the queue in order and refuses later submissions with a printed message. Queue three jobs, shut "
                "down, submit one more, print the drained list, and assert the refused job never entered the queue."
            ),
            patterns=["class App", "def shutdown", "assert"],
            mapping=(
                "Qt's `closeEvent` and `QThread.quit` plus `wait`, and Tkinter's `WM_DELETE_WINDOW` protocol, are the "
                "hooks where this ordering has to be implemented for real."
            ),
        ),
        132: dict(
            topic="Concurrency without races",
            idea=(
                "A race is not really about two things happening at the same instant; it is about two operations "
                "whose result depends on the order they interleave, combined with state that one of them can observe "
                "half-changed. The canonical example is read, modify, write: two workers each read a counter holding "
                "zero, each add one, each write their own answer, and the final value is one. No hardware failure "
                "occurred. The updates were simply not atomic. The defence is to make the unit that must not "
                "interleave explicit, and then protect it: a lock around the read-modify-write, or a queue that "
                "funnels mutations through one owner, or immutable data passed by message. The best concurrency "
                "design usually avoids sharing altogether, and a lock is the fallback when sharing is unavoidable. "
                "Today you implement the same increment twice, once with two stale reads interleaved to show the "
                "lost update, and once serialised to show the correct count. The assertions pin both numbers, one and "
                "two, so the bug is demonstrated rather than described. In a GUI, the single UI thread already gives "
                "you one safe owner; the races you must watch are on shared caches, counters and connection pools. A lock held across a UI call is its own kind of freeze."
            ),
            code=(
                'def unlocked_increment():\n'
                '    cell = {"value": 0}\n'
                '    first = cell["value"]\n'
                '    second = cell["value"]\n'
                '    cell["value"] = first + 1\n'
                '    cell["value"] = second + 1\n'
                '    return cell["value"]\n'
                '\n'
                'def locked_increment():\n'
                '    cell = {"value": 0}\n'
                '    for _ in range(2):\n'
                '        current = cell["value"]\n'
                '        cell["value"] = current + 1\n'
                '    return cell["value"]\n'
                '\n'
                'print("unlocked final count:", unlocked_increment())\n'
                'print("locked final count:", locked_increment())\n'
                'assert unlocked_increment() == 1\n'
                'assert locked_increment() == 2\n'
                'assert locked_increment() - unlocked_increment() == 1\n'
                'print("atomic read-modify-write prevents the lost update")'
            ),
            variant_b='add a third stale writer to the unlocked version and print the final count it loses',
            variant_c='route both increments through a single owner function and show the count is always two',
            mistakes=[
                "Assuming two increments are safe because each one looks like a single statement.",
                "Holding a lock while calling back into the UI, which invites deadlock or a frozen window.",
                "Sharing a mutable cache between workers and the UI without a single defined owner.",
            ],
            q1=(
                "How can two increments produce one instead of two with no hardware fault?",
                "Both read the old value before either write, so the second write overwrites the first and one update is lost.",
            ),
            homework=(
                "Write `unlocked_increment()` and `locked_increment()` that each model two read-modify-write "
                "operations, the first with two reads before either write and the second serialised. Print both final "
                "counts and assert they differ by exactly one, then comment which line makes the update atomic."
            ),
            patterns=["def unlocked_increment", "def locked_increment", "assert"],
            mapping=(
                "Qt's queued connections and Tkinter's queue pattern avoid shared mutable widgets entirely; when "
                "sharing is unavoidable, a `threading.Lock` or a single-owner actor keeps the invariant."
            ),
        ),
        133: dict(
            topic="Testing asynchronous flows",
            idea=(
                "Asynchronous code is hard to test when the test waits on real time, because a suite that sleeps for "
                "two seconds per case is slow and flaky at the same time. The fix is to remove the clock from the "
                "logic. If the flow is driven by polls, ticks or messages, then the test can supply those events "
                "directly: run two polls and assert what happened, run ten and assert the final state. Nothing has to "
                "be fast, because nothing is waiting. This is why mature applications keep the scheduling policy "
                "outside the pure logic and pass in a clock or a tick source rather than calling sleep in the middle "
                "of a function. The same tests should also cover the boring edges that real users hit: zero polls, "
                "completion before the first poll, duplicate results, and shutdown while work is pending. Today you "
                "run one tiny poll loop with three different budgets and print the done and pending lists for each, "
                "then assert the extremes. The point is not the loop, it is the control: the test owns the schedule, "
                "so the result is deterministic and a failure means a logic bug rather than a slow machine. Write the edge cases first; they are cheap and they catch ordering mistakes."
            ),
            code=(
                'def run_polls(jobs, polls):\n'
                '    done, pending = [], list(jobs)\n'
                '    for _ in range(polls):\n'
                '        if pending:\n'
                '            done.append(pending.pop(0))\n'
                '    return done, pending\n'
                '\n'
                'jobs = ["a", "b", "c"]\n'
                'for polls in (0, 2, 9):\n'
                '    done, pending = run_polls(jobs, polls)\n'
                '    print("polls", polls, "done", done, "pending", pending)\n'
                '\n'
                'done, pending = run_polls(jobs, 9)\n'
                'assert done == ["a", "b", "c"] and pending == []\n'
                'assert run_polls(jobs, 0) == ([], ["a", "b", "c"])\n'
                'assert run_polls(jobs, 9)[0] == run_polls(jobs, 20)[0]\n'
                'print("extra polls add nothing; the test owns the schedule")'
            ),
            variant_b='start with an empty job list and assert every poll count returns nothing without raising',
            variant_c='run the same flow twice and assert both runs produce identical output lists',
            mistakes=[
                "Using real sleeps in tests, making the suite slow and timing dependent.",
                "Testing only the happy path where every poll completes one job and nothing is ever pending.",
                "Checking output once at the end instead of asserting intermediate pending and done states.",
            ],
            q1=(
                "Why does injecting the poll or tick count make asynchronous code testable?",
                "The test controls exactly how much the loop runs, so the outcome is deterministic and needs no waiting or wall-clock timing.",
            ),
            homework=(
                "Write `run_polls(jobs, polls)` returning `(done, pending)` without sleeping, then test it with zero "
                "polls, enough polls and extra polls. Print all three results, assert that extra polls add nothing, "
                "and comment why injecting the poll count makes the flow testable."
            ),
            patterns=["def run_polls", "assert", "print("],
            mapping=(
                "A fake clock or a manual event pump is the standard way to test `after` callbacks and Qt timers; "
                "production code takes the scheduler as a dependency so tests never wait."
            ),
        ),
        134: dict(
            topic="Review: responsiveness checklist",
            idea=(
                "A responsiveness review is a checklist applied before release, not a feeling you get while clicking "
                "around on a fast laptop. The checklist exists because the same six or seven mistakes recur in every "
                "desktop codebase: long work on the UI thread, results delivered by touching widgets from a worker, no "
                "cancellation path, progress emitted faster than the screen can use it, a queue with no bound, "
                "shutdown that abandons pending work, and shared mutable state with no owner. Each item can be checked "
                "by reading code and asking one question, which is why it survives deadlines and staff changes. A "
                "checklist also gives a review meeting something concrete to argue about, and it turns a vague bug "
                "report into a named defect with a fix. Today you encode the list as a dictionary of booleans and "
                "write an audit function that separates passes from failures. The sample design fails exactly one "
                "item, and the output names it. That is the shape of a real review tool: small, explicit, and honest "
                "about what it does not cover, such as visual polish or accessibility, which deserve their own lists. Run the audit during code review and add an item for every new kind of freeze."
            ),
            code=(
                'CHECKLIST = {\n'
                '    "long_work_off_ui_thread": True,\n'
                '    "worker_results_via_queue": True,\n'
                '    "cancel_supported": False,\n'
                '    "progress_rate_limited": True,\n'
                '    "shutdown_drains_queue": True,\n'
                '}\n'
                '\n'
                'def audit(design):\n'
                '    passed = [name for name, ok in design.items() if ok]\n'
                '    failed = [name for name, ok in design.items() if not ok]\n'
                '    return passed, failed\n'
                '\n'
                'passed, failed = audit(CHECKLIST)\n'
                'print("passed:", len(passed), "failed:", len(failed))\n'
                'for name in failed:\n'
                '    print("fix:", name)\n'
                'assert failed == ["cancel_supported"]\n'
                'print("responsiveness is a checklist, not a feeling")'
            ),
            variant_b='add a checklist item for bounded queues, fail it, and print both failing names',
            variant_c='make audit return a score as a percentage and print it alongside the failing items',
            mistakes=[
                "Reviewing responsiveness by clicking around on a fast development machine.",
                "Checking only the happy path and never asking what cancels, fails or shuts the work down.",
                "Treating the checklist as a substitute for visual and accessibility review instead of a complement.",
            ],
            q1=(
                "Why is a checklist more reliable than a subjective impression of speed?",
                "It names specific defects that can be checked in code, so the review does not depend on the reviewer's machine or mood.",
            ),
            homework=(
                "Write `audit(design)` that splits a checklist dictionary into passed and failed names, and "
                "`summary(design)` returning a single sentence naming the failures. Run both on a design with one "
                "failing item, print the output, and assert the failed list has exactly one entry."
            ),
            patterns=["def audit", "def summary", "assert"],
            mapping=(
                "Apply the checklist to real Tkinter `after`/queue code or Qt `QThread` code before shipping; it maps "
                "one-to-one onto the thread-safety warnings in both toolkits."
            ),
        ),
    },
)
