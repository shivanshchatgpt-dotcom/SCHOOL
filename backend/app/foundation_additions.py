"""Extra theory sections for the foundation lessons, keyed by day.

Kept apart from `foundation.py` so the lesson bodies stay readable on their own.
Each addition is a further treatment of the same day rather than filler, and the
standard is enforced when the module is validated.
"""

ADDITIONS: dict[int, str] = {
    1: """
There is more than one way to run a Python file, and knowing which is which saves confusion later. The interactive prompt, which starts with three chevrons, executes each line as you type it and is the fastest way to try something. A script runs a whole file top to bottom. `python -c "print(1)"` runs a single expression without a file at all, which is genuinely useful for testing a one-liner on a machine where you cannot create files.

The prompt has a subtlety worth knowing early: if a line ends with an open bracket, string or triple quote, it waits for the rest rather than complaining, so a `SyntaxError` about an unclosed bracket usually means an earlier line left something open.

Finally, a convention you will meet before you need it. Code meant to be imported rather than run is wrapped in a guard, `if __name__ == '__main__':`, so the top-level part executes only when the file is run directly. Nothing here needs it yet, but every file from here on will, because importing a module should not launch it.
""",
    2: """
Three details about values explain behaviour that otherwise seems arbitrary.

Booleans are integers in Python: `True` is 1 and `False` is 0, which is why `True + True` is 2 and why `if flag:` accepts any non-zero number. Useful occasionally, a bug source regularly, and the reason a function expecting a boolean will happily take a count without complaining.

`None` is not zero and not the empty string. It is the absence of a value, which is what a function with no return gives back. Test for it with `is None` rather than `== None`, because the latter also matches anything that merely compares equal, and `is` is the correct way to ask about identity.

Small integers and short strings are interned, meaning Python reuses one object for every equal value in a small range. So two names bound to 5 refer to the same object and `is` returns True. That is an implementation detail you should not rely on, but it explains why identity comparisons behave differently for small and for computed values.
""",
    3: """
Two details about `input()` matter before you rely on it. It strips the trailing newline for you, so you never need to strip again for that reason, but it does not strip leading or trailing spaces, so someone typing `  5  ` produces `'  5  '`. And when there is no line to read, such as when input is redirected from nothing, it raises `EOFError` rather than returning an empty string, which is what shows up in a pipeline.

Conversion is stricter than people expect. `int('5')` works and `int(' 5 ')` works, but `int('5.0')` raises ValueError and so does `int('five')`. If decimals are acceptable, convert to `float` instead, and be aware that `float('nan')` and `float('inf')` are both valid, which quietly poisons every calculation downstream when they arrive from untrusted input.

A practical habit: convert once, immediately, at the boundary, and never again. A program where every value is converted where it enters is one where the type is never genuinely in doubt, and it removes the whole category of bug where a string reaches somewhere it should not have.
""",
    4: """
Two things extend the plain if/elif/else.

A conditional expression assigns as it chooses: `label = 'pass' if score >= 70 else 'fail'`. This is worth using for a short choice where both branches are single expressions, and worth avoiding as soon as either needs a statement, because a conditional expression cannot contain one and the attempt turns unreadable fast.

Conditions short-circuit. In `if items and items[0] == 'x':` the right-hand side is not evaluated when the list is empty, which is exactly what makes the idiom safe. The same applies to `or` when choosing a default. Relying on this is fine and is one reason conditions read the way they do, but it also means a side effect placed inside a condition may not run at all, which is a good reason not to put side effects in conditions.

Finally, when several branches test the same value against different fixed values, Python 3.10 added a `match` statement that expresses precisely that and can be clearer than a long elif chain. Worth knowing about, though if/elif is not wrong and remains the right choice whenever the branches contain conditions of their own.
""",
    5: """
Two things about loops are worth adding.

Loops nest, and the nesting is where interesting problems live. A loop over rows and a loop over columns is the standard way to walk a grid, and counting the total work is how you notice that a nested loop over ten thousand items is a hundred million operations. This is the direct link to the growth-rate material later in the course, and forming the habit of estimating before running is worth more than any optimisation you will do later.

The `else` clause is available on `while` as well as `for`, and it runs when the loop ends because the condition became false rather than because of a `break`. That is even more useful in the while case, because running until the condition failed is the normal outcome and the `else` is what distinguishes it from an early exit.

A practical warning about mutating during iteration: adding to a list while looping over it does not raise, it silently continues into the new items, which can produce an infinite loop or an overwhelming result depending on what is being appended. If you need a new collection, build a separate list and assign it afterwards.
""",
    6: """
A few list behaviours come up constantly.

Multiplying a list repeats it, and the items inside are shared rather than copied: `rows = [[0]] * 3` creates three references to the *same* inner list, so writing `rows[0][0] = 1` changes all three. A comprehension, `rows = [[0] for _ in range(3)]`, builds each one separately. This is the most common list bug and it produces output that looks self-contradictory.

`sort` takes a key function, which is how you sort by something other than natural order: `pairs.sort(key=lambda p: p[1])` sorts by the second element, and `key=lambda p: -p[1]` sorts by it descending. The key runs once per element and the elements themselves are never compared, so values of mixed type are fine.

Deleting by position is `del items[i]` and by value is `items.remove(x)`, and they differ when the target is absent: `del` raises IndexError, `remove` raises ValueError. Test with `in` first when absence is possible.

One more: `list.copy()` is a shallow copy, exactly like a slice, so nested lists are still shared between the original and the copy.
""",
    7: """
Three aspects of function definitions go beyond the basics.

Arguments can be made keyword-only with a bare `*`, as in `def connect(host, *, timeout=5)`. A caller must then name `timeout`, so a later parameter can be inserted or reordered without silently changing what a positional call means. For anything other than a two-line helper, keyword-only arguments are worth the small inconvenience.

A docstring is the first statement and documents what the function does, what it takes and what it returns. It is the one piece of documentation that cannot drift out of date relative to the code, because it travels with the code, and `help(func)` reads it.

The call stack is worth naming now. Every call pushes a frame holding its parameters and locals, and the return pops it. That is why a local variable cannot be seen by the function it called, and why a function which forgets to return gives the caller None rather than an error. A traceback is this stack printed from the inside out.

Naming matters more than anything else: `def calculate_total(items, tax_rate)` documents itself, while `def c(i, r)` makes the reader inspect the body to learn what the parameters mean.
""",
    8: """
Two things about return values are worth adding.

Python unpacks a sequence on assignment, so `a, b = pair` and `for a, b in pairs:` work whenever the right-hand side has the right number of elements. If it does not, the error appears at the assignment rather than at the point of construction, so when a tuple comes back with the wrong length the message names the line that tried to take it apart. That is usually quick to diagnose, but it means a function returning a tuple is making an assumption about how it will be used.

Returning nothing and returning None are the same thing, and that occasionally hides a bug. A function that accumulates into a list and returns nothing is fine; a function meant to compute a number and missing the return gives the caller None, and the error appears later as a TypeError somewhere unrelated. When the job is to produce a value, ending the function with the value in a return rather than a bare print is the safer habit.

A function that both mutates an argument and returns a value is doing two jobs, and the second caller to use it gets a surprise. Prefer a function that takes something, returns something new, and mutates nothing.
""",
    9: """
Three more dict behaviours are worth having.

A dict comprehension builds one in a single expression: `counts = {word: len(word) for word in words}`. It is the same as the initialise-then-accumulate loop, and reading it is easier precisely because the result is right there.

`update` merges another dict in, overwriting existing keys, and `setdefault(key, default)` inserts the default only when the key is absent and returns the value either way. Together they cover the get-or-create cases that otherwise need a membership test followed by an assignment.

`keys()`, `values()` and `items()` return view objects, not lists. A view reflects later changes to the dict, which is occasionally what you want and usually a surprise if you were expecting a snapshot. They also support set-like operations on `keys()`: `a.keys() & b.keys()` gives the keys present in both, which is a neat way to compare two dicts' fields.

One thing a dict will not do is accept a non-hashable key, so a list cannot be a key. When you need that, `tuple(values)` works if the values are themselves hashable, and it is a common way to key by a pair of fields.
""",
    10: """
Three things about exceptions go beyond what is here.

Raising your own exception is how a function reports a failure the caller can distinguish from anyone else's. Define a subclass of `Exception` that carries the relevant detail as an attribute, raise it on the specific condition, and the caller can catch that one class and know exactly what went wrong without parsing a message string.

Chaining preserves context. Raising a new exception while handling another attaches the original as the cause and the traceback shows both, which is how you see that a `KeyError` became a `ValueError` inside a lookup. `raise NewError(...) from err` makes that relationship explicit rather than incidental.

The `finally` clause runs even while an exception is propagating, but it does not swallow it: if the body raised, the exception continues after the block. To suppress it you would have to return from inside `finally`, which is almost always a mistake because it discards the original failure. If you need to recover, catch and handle rather than returning from finally.

Catching `BaseException` is almost always wrong, because it includes KeyboardInterrupt and SystemExit, and swallowing those makes a program impossible to stop.
""",
    11: """
Four details about files are worth knowing.

Opening in `'a'` appends rather than overwriting, which is what you want for a log and a data-loss bug if you wanted to rewrite. `'r+'` allows reading and writing but does not truncate, and the position rules are easy to get wrong. The three modes you need most are `'r'`, `'w'` and `'a'`.

Output to a file is buffered, so a crash can lose the last few kilobytes. `handle.flush()` forces it out, and it is worth knowing why a script that is killed can appear to have written nothing at all.

`os.path.join` rather than string concatenation, because a separator is not the only thing that differs between platforms, and a hard-coded slash is a bug that appears only on the other one.

And `csv.DictReader` against `csv.reader`: with a header row, `DictReader` gives each row as a dict keyed by the header names, which survives a column being reordered or added. `reader` gives positional lists, which silently misassign every field if the order changes. For anything with a header, `DictReader` is the safer default.
""",
    12: """
A few refinements to the assertion habit are worth adding.

An assert is removed when Python runs with `-O`, so treat it as documentation and a development tool rather than as validation in released code. Where a check must always run, raise explicitly.

When you give an assertion a message, it should say what was expected and what happened, not merely which line failed. `assert len(rows) == expected, f'expected {expected} rows, got {len(rows)}'` tells you the problem; `assert False, 'failed'` does not.

Tests for the same function belong together, and naming them after the behaviour rather than the function keeps them readable when the function is renamed. `test_average_rejects_empty` says what must hold; `test_2` does not.

Finally, a test that checks one value proves very little. For a function that transforms a list, check the empty case, a single element, a typical case and an unsorted input, and check the result rather than the steps. Those four cover most of what a function can get wrong, and they are cheap to write.
""",
    13: """
The vocabulary for this skill is worth learning, because the concepts are easier to remember by name.

Coupling is how much one part depends on another. Cohesion is how much the parts of a single unit belong together. You want low coupling and high cohesion: modules that can be understood and changed one at a time, each with one clear responsibility.

A pure function is one whose output depends only on its inputs, with no side effects and no hidden state. `def average(values): return sum(values) / len(values)` is pure. A function that reads a global, prints as it goes, or appends to a module-level list is not. Pure functions are trivially testable, which is why pushing towards them is the most effective response when a program becomes hard to work with.

Two decomposition directions are worth naming. Top-down starts from the whole and cuts it into pieces, which suits a specification you already understand. Bottom-up starts from a capability you know how to build and assembles upward, which suits a situation where the shape of the whole is not yet clear. Real work alternates between them, and switching is not a sign of failure.
""",
    14: """
Two things about building a program that others will run are worth adding.

Error messages are part of the interface. A message that says what was expected, what arrived, and what the person can do about it costs four lines and saves a support conversation. The capstone rejects a malformed line; a real tool would name the line and the field that failed, and a command-line tool would exit with a non-zero status so a shell script could react.

Logging is print with the volume controlled. `print` goes to the screen and is always seen; logging has levels, a timestamp and a destination you choose, and levels below the configured threshold are discarded before formatting. A program that prints unconditionally cannot be run quietly, which is exactly what you want when something else is driving it.

A third habit, and the most valuable: after it works, change one thing and check that only one thing changed. If a small change breaks something in a distant part of the code, the boundaries are in the wrong place, and now is the cheapest moment to discover it.
""",
}
