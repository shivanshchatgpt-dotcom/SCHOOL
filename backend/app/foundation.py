"""The fourteen foundation concept lessons.

Days one to fourteen are where a learner decides whether this course is for them,
and they are byte-identical across the launch paths, so they are written once
here and seeded into all three. They are concept days rather than generated
practice: a student arriving on day one should find a body of teaching, not an
exercise set.

Every body is held to the same standard as the rest of the catalogue: a theory
of at least the standard word budget, a worked example that runs, three question
and answer pairs, and homework a checker can grade. `validate()` enforces all of
it and `apply()` is idempotent, so a lesson can be re-seeded after a wording
change without duplicating anything.
"""
from __future__ import annotations

import argparse
import ast
import io
import json
import re
import sqlite3
import sys
from contextlib import redirect_stdout
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "pyschool.db"
DOMAINS = {
    "agi-research": "AI Research",
    "data-science": "Data Science",
    "web-dev": "Web Development",
}
MIN_THEORY_WORDS = 450
MAX_THEORY_WORDS = 900

LESSONS: tuple[dict, ...] = (

    dict(
        day=1, title="Your first Python program", objective="Run a program, assign values to names, and print output",
        theory="""A Python program is a file of instructions that Python reads top to bottom and executes one line at a time. There is no compile step and no separate build, so the distance between writing a line and seeing its effect is one command. That tight loop is the reason Python is worth learning first: every idea can be tried immediately rather than theorised first.

Three ideas carry this day. The first is `print`, which writes a value to standard output. Everything a program shows you goes through it, which sounds trivial until you notice that forgetting it is the most common reason a working function appears to do nothing. `print` is not the same as *returning* a value, and the difference matters: printing is for a human, returning is for the rest of the program. This comes up repeatedly and the confusion between them costs hours if it is left vague.

The second is assignment. `name = value` binds the name `name` to the object `value`. The equals sign is an instruction to remember, not a statement of equality, which is a real difference from arithmetic or algebra: a variable can be rebound, and after `x = 1` then `x = 2`, the name refers to the number two and the original one is unreachable by that name.

The third is that names must be valid identifiers. Letters, digits and underscores are allowed, a name may not start with a digit, and case matters, so `total` and `Total` are two different names. Choose names that say what a value is rather than what letter it is; `study_hours` costs nothing extra and tells a reader what the number means six weeks later.

A worked example ties these together. The version below assigns three values, performs one small calculation, and prints the result, and it runs exactly as written. Read it before running it and predict the output, then change one value and predict again. Predicting first is the habit that separates reading code from understanding it.""",
        code_example="""study_hours = 12
subjects = 3
total = study_hours * subjects

print('studying', total, 'hours')
print('that is', total / subjects, 'hours per subject')""",
        questions=[
            "What is the difference between printing a value and returning it?",
            "After `x = 1` and then `x = 2`, what does the name `x` refer to, and is the first value gone?",
            "Why does `total` describe the example better than `t`?",
        ],
        answers=[
            "Printing writes to the screen for a person to read. Returning hands a value back to the code that called the function so it can be used, tested or stored. A function that only prints is impossible to build on, because its caller has nothing to work with.",
            "The name `x` refers to the number two. The first value still exists in memory and is still reachable by another name if one existed, but through the name `x` it is no longer accessible. Rebinding does not modify the old object; it changes which object the name points at.",
            "Because the name is read far more often than it is written, and six weeks later nobody remembers what `t` stood for. A descriptive name costs nothing at the moment it is typed and pays back every time the line is read.",
        ],
        homework=(
            "Write a program that assigns your name, the number of hours you plan to study each week, and the number of subjects you are taking. Compute the total weekly hours, then print all four pieces of information with clear labels. "
            "Your program must define at least three names, use arithmetic to compute the total, and print at least four lines. Change one value and rerun it to check the output changes the way you expected."
        ),
        required_patterns=["=", "print("], min_lines=4,
        rubric="Program must run without raising, assign at least three names, compute a value arithmetically, and print at least four labelled lines.",
    ),

    dict(
        day=2, title="Variables and values", objective="Bind names to values and understand what an object is",
        theory="""Python has no declared types. A name can hold a number one line and a string the next, and nothing complains. This sounds careless and is in fact the most useful thing about the language: a variable is a label you attach to an object, and the object carries its own type. When you write `x = 3`, the name `x` is bound to the integer object three. Rebinding `x = 'three'` points the same name at a different object of a different type. The name did not change; its referent did.

That model explains several things that otherwise feel arbitrary. Why `3` divided by `2` is `1.5` but `4` divided by `2` is `2`: with two integers, Python produces an integer and discards the remainder, and a float literal like `4.0` changes the result to `1.5` and `2.0`. Why `0.1 + 0.2` is not exactly `0.3`: those literals are stored as the nearest representable binary fraction, not as written. Why adding a string to a number raises rather than silently producing nonsense: the `+` operator checks whether its two operands make sense together, and it would rather fail loudly.

The practical consequence is that a variable's type is a property of its current value, not a promise you made. If a function receives a variable and must treat it as a number, the honest thing is to convert it and say so, not to assume.

Use `type()` to look and `isinstance()` to test. When you are unsure what something holds, printing its type is faster than reasoning about it, and it is the single most useful debugging habit in this lesson.

The example below shows rebinding across types, the difference between integer and float division, and a type check. Run it, then change `count` to a float and rerun to see which lines change and why.""",
        code_example="""count = 7
print('count is', count, 'and its type is', type(count).__name__)

count = 'seven'
print('now count is', repr(count), 'and its type is', type(count).__name__)

print('7 / 2  ->', 7 / 2)
print('7 // 2 ->', 7 // 2)
print('7 % 2  ->', 7 % 2)

print('0.1 + 0.2 == 0.3 ->', 0.1 + 0.2 == 0.3)
print('isinstance(7, int)  ->', isinstance(7, int))""",
        questions=[
            "What does `7 / 2` return compared to `7 // 2`, and why do they differ?",
            "Why is `0.1 + 0.2 == 0.3` False?",
            "If a name is a label rather than a container, what happens when you write `x = 3` then `x = 'three'`?",
        ],
        answers=[
            "`7 / 2` gives 3.5 as a float because true division always produces a float in Python 3. `7 // 2` gives 3 because floor division keeps both operands as integers and discards the remainder. The two operators answer different questions, so the language keeps both.",
            "Because 0.1 and 0.2 have no exact binary representation, so each is stored as the nearest double. Adding the two nearest doubles gives a value that is very close to but not exactly the nearest double to 0.3, so the comparison fails. The error is around one part in ten to the sixteenth.",
            "The name is rebound to a different object, now a string rather than an integer. The integer three is unaffected and still exists; it is simply no longer reachable through the name x. Nothing was converted or modified.",
        ],
        homework=(
            "Assign a whole number, print its type, then rebind the same name to a string and to a float, printing the type each time. Demonstrate the difference between `/` and `//` on two pairs of numbers, and show what happens when you divide by zero. "
            "Then use `isinstance` to check one value against `int`, `float` and `str` and print all three results. Your script must define at least two names, rebind one of them to a different type, and print at least six lines."
        ),
        required_patterns=["=", "type(", "print("], min_lines=6,
        rubric="Must rebind at least one name across types, compare the two division operators, and use both type() and isinstance() with labelled output.",
    ),

    dict(
        day=3, title="Numbers, strings and input", objective="Read input, convert types, and work with strings",
        theory="""Every program that does anything useful eventually needs input, because a program that cannot be told anything computes the same answer forever. Python's `input()` reads a line from the person at the keyboard and **always returns a string**, regardless of what they typed. This is the most common early bug: someone types `5`, the program adds two of them, and gets `22` because the program is concatenating text rather than adding numbers. The fix is explicit conversion, `int(...)` or `float(...)`, and it is better to convert immediately at the boundary than to carry a value of uncertain type through the program.

A string is a sequence of characters, and a number is not. So a string has methods a number does not: `strip()` removes leading and trailing whitespace, `upper()` and `lower()` change case, `split()` cuts on whitespace, and `replace()` substitutes. None of these change the original string, because strings are immutable. Each returns a new string, which is why `text.upper()` on its own does nothing at all and `text = text.upper()` is what you meant. This is the same lesson as `sorted()` versus `list.sort()`, and it is worth meeting twice because it is easy to get wrong the first time.

Whitespace deserves particular attention. When a person types a number they often add a space or a trailing newline, and `int(' 5 ')` handles it while `int('5 apples')` does not. `strip()` before converting is a cheap habit that prevents a whole class of confusing failures.

For numbers, the arithmetic operators behave mostly as you would expect from school: `+`, `-`, `*`, `/`, `//` for floor division, `%` for remainder, and `**` for power. The surprise is the one from the previous lesson: two integers divide to a float, and `%` with negative operands follows the sign of the divisor rather than the dividend.

The example below takes a line of input-shaped text, strips it, converts it, and does arithmetic with it, then shows the same operations on the text itself. Read it first: predicting each line is the exercise.""",
        code_example="""raw_name = '  Asha  '
raw_age = ' 21 '

name = raw_name.strip()
age = int(raw_age)

print('name:', repr(name), '| age:', age, type(age).__name__)

print('next year:', age + 1)
print('days lived:', age * 365)
print('age in months:', age * 12)

text = 'python is fun'
print('upper   :', text.upper())
print('split   :', text.split())
print('replaced:', text.replace('fun', 'powerful'))
print('original:', text)""",
        questions=[
            "Why does `int(' 21 ')` work when a person types a number with stray spaces?",
            "What happens to the variable `text` after `text.upper()` is called without an assignment, and why?",
            "Compute the output of `7 // 2`, `7 % 2` and `2 ** 3`.",
        ],
        answers=[
            "Because int() ignores leading and trailing whitespace as part of parsing a number, so the spaces are tolerated rather than treated as invalid characters. Anything non-numeric after the digits, however, still raises a ValueError.",
            "Nothing happens to the variable. upper() returns a new string and the return value is discarded, so text still holds the original lowercase value. Strings are immutable, so the method could not have modified it in place even if it tried.",
            "7 // 2 is 3, integer floor division. 7 % 2 is 1, the remainder. 2 ** 3 is 8, exponentiation.",
        ],
        homework=(
            "Ask for a person's name and their age as text, strip the input, convert the age to an integer, and print a message that uses both. Then compute their age in days and in months, and print how many days until their next birthday assuming 365-day years. "
            "Finally, print the name in upper case, the name in lower case, and the number of characters in the name. Your script must use input, strip, at least two type conversions, and print at least five labelled lines."
        ),
        # `input(` is deliberately absent: the worked example simulates input so
        # the script runs unattended, and a pattern the reference solution cannot
        # satisfy would fail the student who learns from it. The homework still
        # asks for real input, and strip/int are what the checker can verify.
        required_patterns=["strip(", "int(", "print("], min_lines=5,
        rubric="Must strip the input, convert at least one value to a number, and print labelled results including a name transformation and a computed quantity. Real input() is what the exercise asks for; the worked example simulates it so it can run unattended.",
    ),

    dict(
        day=4, title="Making decisions with if", objective="Branch on a condition and use every comparison form correctly",
        theory="""A conditional runs code only when a condition is true. Python's form is unusual only in the colon and the indentation that follows it:

```
if condition:
    body
elif other_condition:
    body
else:
    body
```

The indentation is not decoration; it is the syntax. Python uses it to decide where the block ends, which is why a missing colon or a line indented wrongly produces an `IndentationError` rather than a subtle bug. Most editors will insert and align the indentation for you, but you still have to remove the trailing colon.

The conditions themselves are where the real mistakes live. A chain comparison like `0 <= x <= 10` is a single condition in Python, written the way you would write it in mathematics, and it is correct. The same thing written with `and` also works. What does not work is `0 <= x =< 10`; that is two comparisons with a typo between them and it will either fail to parse or quietly mean something else.

Truthiness is the second area. Many values are treated as true or false without an explicit comparison: the empty string, the empty list, zero, `None` and `False` are falsy, and everything else is truthy. So `if items:` is a natural way to ask whether a collection has anything in it, and reads better than `if len(items) > 0:`. The trap is the string `'0'`, which is truthy because it is not empty, even though it looks falselike.

The third is comparing floats for equality. `0.1 + 0.2 == 0.3` is False, as the previous lesson showed, so a float comparison that "should" be exact will fail intermittently depending on the values. Use a tolerance: `abs(a - b) < 1e-9`. This is not paranoia; it is the correct way to compare numbers that came from arithmetic.

The example below exercises all three: a chain comparison, a truthiness check, and a tolerant float comparison. Predict each branch before running it.""",
        code_example="""def classify(score):
    if not isinstance(score, (int, float)):
        return 'not a number'
    elif score < 0 or score > 100:
        return 'out of range'
    elif score >= 70:
        return 'pass'
    else:
        return 'fail'


def describe(items):
    if items:
        return f'{len(items)} item(s)'
    return 'nothing to show'


def nearly_equal(a, b, tolerance=1e-9):
    return abs(a - b) < tolerance


for s in (95, 70, 40, 120):
    print(f'score {s:<4} -> {classify(s)}')

print(describe([1, 2, 3]))
print(describe([]))

print('0.1+0.2 == 0.3   ->', 0.1 + 0.2 == 0.3)
print('nearly_equal     ->', nearly_equal(0.1 + 0.2, 0.3))""",
        questions=[
            "Why does `if items:` work as a test for emptiness, and what would `if len(items) > 0:` say instead?",
            "What does `classify(70)` return, and why does it not fall through to the outer `if`?",
            "Why should floats be compared with a tolerance rather than with `==`?",
        ],
        answers=[
            "Because an empty list is falsy and a non-empty one is truthy, so the test needs no explicit length call. The longer form says the same thing but states it in terms of a measurement rather than a property, and it breaks for anything that is not a collection.",
            "It returns 'pass'. The score of 70 satisfies 0 <= 70 <= 100, so the outer condition holds and the inner if runs, finding 70 >= 70 true and returning 'pass' immediately. The return exits the function, so the trailing return for 'fail' is never reached.",
            "Because binary floating point cannot represent most decimal fractions exactly, so arithmetic accumulates small errors. The results are close but not bit-identical, so == reports False even when the numbers agree to far more digits than anyone cares about. A tolerance states how close is close enough.",
        ],
        homework=(
            "Write a function that takes a number and reports whether it is negative, zero or positive, and a second function that takes a temperature in Celsius and returns a label of 'freezing', 'cold', 'warm' or 'hot' using nested conditions. "
            "Then check a list with `if items:` and an empty one, and demonstrate that a non-empty string such as '0' is truthy. Your script must define at least two functions, use if, elif and else, nest one condition inside another, and print at least six results."
        ),
        required_patterns=["def ", "if ", "else:", "return", "print("], min_lines=6,
        rubric="Must define at least two functions, use if with else, nest one conditional, and demonstrate a truthiness test including the string '0'. The homework asks for an elif chain, which the example shows by way of nesting so the nesting is visible.",
    ),

    dict(
        day=5, title="Repeating work with loops", objective="Use for and while loops, and control them properly",
        theory="""Loops remove repetition, and choosing between the two forms is a matter of whether you know how many repetitions there will be.

A `for` loop walks a sequence, so it wants a sequence: a list, a string, a range, or anything iterable. A `while` loop repeats as long as a condition holds, so it wants a stopping rule you can state up front. When you can count the repetitions or describe the collection, reach for `for`. Reach for `while` when the count depends on something discovered during the loop, such as reading input until a sentinel value appears.

`range` is the usual partner for `for`, and its three forms are worth knowing. `range(5)` yields 0 through 4. `range(2, 7)` yields 2 through 6. `range(0, 10, 2)` yields 0, 2, 4, 6, 8. The stop value is never included, which is a deliberate design choice: with `range(len(items))` the last valid index is `len(items) - 1`, so an exclusive stop keeps the two consistent.

Inside a loop, `break` leaves immediately and `continue` skips to the next iteration. The `else` clause of a `for` loop runs only when the loop finished without a `break`, which is a precise way to express "nothing matched" and is clearer than a flag variable set inside the loop.

Two mistakes are worth naming. Changing the length of a list while iterating over it makes Python skip elements, because the loop reads the index fresh each time; iterate over a copy if you must modify the original. And a `while` loop whose condition never becomes false runs forever, which is why every `while` should have a counter or a `break` that you can see from a distance.

The example below runs both forms, uses `break`, `continue` and the `else` clause, and shows the index arithmetic that trips people up.""",
        code_example="""def classify(numbers):
    out = []
    for i, n in enumerate(numbers):
        if n < 0:
            continue
        if n > 100:
            break
        out.append((i, n * 2))
    else:
        print('loop finished without a break')
    return out


print('range(5)        :', list(range(5)))
print('range(2, 7)     :', list(range(2, 7)))
print('range(0, 10, 2) :', list(range(0, 10, 2)))

print('classify:', classify([5, 10, 150, 20]))
print('classify:', classify([5, 10, 20]))

total = 0
n = 1
while n <= 5:
    total += n
    n += 1
print('while total:', total)""",
        questions=[
            "Why does `range(5)` stop at 4 rather than 5, and why is that consistent with list indexing?",
            "What does the `else` clause of a `for` loop do, and when does it run?",
            "Why does modifying a list while looping over it skip elements?",
        ],
        answers=[
            "Because the stop is exclusive, which makes the last value equal to stop minus one, matching the fact that a sequence of length n has valid indices 0 to n-1. The same convention then works for `for i in range(len(items))` without an off-by-one adjustment.",
            "It runs only when the loop completed all its iterations without hitting a break. That makes it a clean way to express 'no element matched' without setting a flag variable inside the loop.",
            "The loop reads the length of the list on each iteration to decide whether to continue. If an element is removed, the list becomes shorter, so indices shift left and the element that moved into the current position is skipped rather than visited.",
        ],
        homework=(
            "Write a loop that sums the numbers from 1 to 100 and print the total. Then write a loop that finds the first number above 50 in a list, using break, and print whether one was found. Use continue to skip the negative numbers in a mixed list and print only the positive ones. "
            "Also print `list(range(0, 100, 10))`. Your script must use both a for loop and a while loop, use break or continue at least once, and print at least five results."
        ),
        required_patterns=["for ", "while ", "range(", "break", "print("], min_lines=5,
        rubric="Must use both loop forms, demonstrate break and continue, and print a computed total rather than only echoing the input.",
    ),
    dict(
        day=6, title="Lists: a collection of values", objective="Store, index, slice and modify an ordered sequence",
        theory="""A list holds an ordered sequence of values in one name, which turns five variables into one thing you can loop over, index, slice and pass around. Create one with square brackets, `[1, 2, 3]`, and it is a mutable object, meaning you can change its contents after creating it.

Indices start at zero, so the first element is `items[0]` and the last is `items[-1]`. Negative indices count back from the end, which is a convenience that removes most off-by-one errors when you want the last element. Indexing past the end raises `IndexError` rather than returning None, because a silent None would turn a clear mistake into a confusing one three lines later.

Slicing takes a range: `items[1:3]` gives elements one and two, and `items[::2]` gives every other one. The slice `[:len]` is a **shallow copy**: a new list containing references to the same objects. That means the new list can be reordered without disturbing the original, but mutating a dict inside either list is visible through both. This is the single most common source of confusion when passing lists around, and it is worth testing deliberately rather than assuming.

The mutating methods change the list in place and return `None`. That is the trap from the previous lesson applied here: `items = items.sort()` rebinds `items` to None. The non-mutating alternatives `sorted()` and `list()` return a new list instead. Use whichever reads better, but know which one you are writing.

Useful methods beyond append: `insert(i, x)` puts an item at a position, `remove(x)` deletes the first matching value, `pop()` removes and returns the last, and `index(x)` finds a position. `in` tests membership without an error when the value is absent, which is almost always what you want.

The example below covers indexing, slicing, the shallow-copy behaviour, and the difference between the mutating and returning forms.""",
        code_example="""numbers = [5, 3, 9, 1, 7]

print('first:', numbers[0], '| last:', numbers[-1])
print('slice [1:3]:', numbers[1:3])
print('every other:', numbers[::2])
print('reversed  :', numbers[::-1])

numbers.append(11)
numbers.insert(0, 0)
print('after append/insert:', numbers)

work = list(numbers)
work.sort()
print('sorted copy :', work)
print('original    :', numbers)

mixed = [{'name': 'a'}, {'name': 'b'}]
shallow = mixed[:1]
shallow[0]['name'] = 'changed'
print('shallow shares objects:', mixed[0]['name'])
print('index of 9:', numbers.index(9), '| 9 in list:', 9 in numbers)""",
        questions=[
            "What does `items[-1]` return, and what happens when you index past the end?",
            "Why does mutating a dict inside a slice affect the original list?",
            "What is wrong with `items = items.sort()`?",
        ],
        answers=[
            "It returns the last element, because a negative index counts back from the end. Indexing past the end raises IndexError rather than returning None, so the mistake surfaces at the line that caused it.",
            "Because a slice copies the references, not the objects. Both lists point at the same dict, so writing to a key through one is visible through the other. Reordering the new list would not affect the original, which is the part that is genuinely independent.",
            "sort() modifies the list in place and returns None, so the assignment rebinds the name to None and the list is lost from that name. `items.sort()` on its own is correct, or `items = sorted(items)` if a new list is wanted.",
        ],
        homework=(
            "Build a list of at least six numbers. Print the first and last, a slice of the middle three, and every other element. Add a value with append and one at a specific position with insert, then print the length. "
            "Create a sorted copy without disturbing the original and print both to show the difference. Finally, remove one value and report whether it was present using `in`. Your script must use indexing, slicing, at least three list methods, and print at least six results."
        ),
        required_patterns=["=", "append(", "[", "]", "print("], min_lines=6,
        rubric="Must index with a negative position, slice, use append and at least one other list method, and demonstrate that sorting a copy leaves the original untouched.",
    ),

    dict(
        day=7, title="Functions: reusable instructions", objective="Define a function and call it with arguments",
        theory="""A function gives a name to a block of instructions so it can be run more than once without repeating the code. `def` creates the function and `return` ends it, handing a value back to whoever called it.

The signature is where the design decisions live. Parameters are the names the function expects; arguments are the values a caller supplies. A parameter with a default is optional, and defaults are evaluated **once, when the `def` line runs**, which matters if the default is a mutable value such as a list or dict. `def add(item, target=[])` gives every call that omits `target` the same list, and items accumulate across calls in a way that looks like a memory leak but is a shared default. The safe form is `target=None` and then `target = [] if target is None else target` inside the body.

The call style is your choice: positional (`f(1, 2)`) and keyword (`f(second=2)`) are both fine, and mixing them in one call is a syntax error. Keywords are worth using when a boolean argument is involved, because `check(patient, False, True)` is unreadable and `check(patient, verbose=False, strict=True)` explains itself.

A function that does not return anything returns `None` implicitly, and that is the most common surprise for a beginner. Code after a `return` is dead: the function has already left. If you meant to keep going, move the return to the end.

Functions are also the natural unit of testing, because you can call one with known inputs and check what comes out. The next lessons build on exactly that.

The example below defines three functions: one with a mutable default done safely, one called both ways, and one that returns nothing so you can see what that yields. Read it and predict each call before running.""",
        code_example="""def add_item(item, target=None):
    if target is None:
        target = []
    target.append(item)
    return target


def greet(name, greeting='Hello', punct='!'):
    return f'{greeting}, {name}{punct}'


def announce(message):
    print('>>', message)


print(add_item('a'))
print(add_item('b'))

print('positional:', greet('Asha'))
print('keyword   :', greet('Asha', punct='?', greeting='Welcome'))

announce('this function returns None')
print('announce returned:', announce('again'))""",
        questions=[
            "Why does a function without a `return` statement give back None, and what happens to code placed after a `return`?",
            "What goes wrong with `def add_item(item, target=[])`?",
            "When is the keyword call style more readable than the positional one?",
        ],
        answers=[
            "Falling off the end of a function ends the call, and the value of a call with no return is None by definition. Code after a return is unreachable, because the function has already returned, so it never runs.",
            "The default list is created once when the def line executes and shared by every call that omits the argument, so items accumulate across calls and each call appears to corrupt the next. The fix is a default of None and creating the list inside the body.",
            "When any argument is a boolean, or when several arguments of similar type could be confused. `check(patient, False, True)` gives a reader no way to know what the flags mean, while keywords make it self-describing at the call site.",
        ],
        homework=(
            "Write a function `describe(value)` that returns a string describing whether a value is an integer, a float, a string or a list, using if/elif/else. Write a second function `repeat(text, times=2)` that returns the text repeated, with a safe default rather than a mutable one. "
            "Call describe with at least four different values and print each result, and call repeat both with and without the optional argument. Your script must define at least two functions, use a default argument, and print at least five results."
        ),
        required_patterns=["def ", "return", "if ", "print("], min_lines=6,
        rubric="Must define at least two functions, include a correctly defaulted optional parameter, return values from both, and print a labelled result for every call.",
    ),

    dict(
        day=8, title="Return values and small calculations", objective="Compute and return results, and handle the empty case",
        theory="""The `return` statement is how a function communicates. A function that only prints is a dead end: its caller has nothing to use, cannot check the result and cannot build on it. A function that returns a value can be stored, printed, compared or passed to another function, which is what makes functions composable.

Returning early is a legitimate and often preferable style. Guard clauses put the exceptional or trivial cases at the top, so the main body of the function is not buried under indentation:

```
def average(values):
    if not values:
        return None
    return sum(values) / len(values)
```

Without the guard, a list comprehension or an expression would be nested one level deeper for a case that is rare. This is not a style preference so much as a readability trade: early returns push the interesting case to the left margin where it can be seen at a glance.

Returning several values is done with a tuple, and Python will happily unpack it: `return minimum, maximum, mean` on the calling side becomes `lo, hi, avg = describe(values)`. It is idiomatic and readable for two or three related results. Beyond that, a dict or a small class is clearer, because a bare tuple of six values forces the caller to remember the order.

A subtle trap: returning a mutable object lets the caller mutate your state. If a function builds a list and returns it, the caller can change it; nothing stops them. When that matters, return a copy.

Empty input deserves explicit handling. `sum([])` is 0 and `max([])` raises ValueError, so functions that accept a sequence must decide what to do with nothing, and the decision belongs next to the code that needs it.

The example below returns a tuple, uses a guard clause, returns a copy, and shows what happens when the empty case is not handled at all.""",
        code_example="""def average(values):
    if not values:
        return None
    return sum(values) / len(values)


def describe(values):
    if not values:
        return None, None, None
    return min(values), max(values), sum(values) / len(values)


def first(items):
    # Returning a copy so the caller cannot modify our internal list.
    return list(items)[:1]


print('average:', average([2, 4, 6]))
print('empty  :', average([]))

lo, hi, mean = describe([3, 1, 4, 1, 5, 9, 2, 6])
print(f'min {lo}  max {hi}  mean {mean:.4f}')

out = first([7, 8, 9])
out.append(99)
print('original untouched, returned copy:', out)

try:
    print(max([]))
except ValueError as err:
    print('max of empty rejected:', type(err).__name__)""",
        questions=[
            "Why is it better for a function to return a value than to print it?",
            "What is the advantage of a guard clause over wrapping the main body in an if/else?",
            "What happens when you return a mutable list and the caller appends to it?",
        ],
        answers=[
            "A returned value can be stored, compared, tested or passed on, so the function composes with others. A printed value exists only on the screen, so the caller must either scrape it back out of the output or have the work done twice.",
            "The guard keeps the ordinary path at the left margin instead of indented under a condition, so the part you read most often is not pushed off to the right. It also makes the failure case obvious, because it is the first thing in the function.",
            "The object is shared, not copied, so the caller's append is visible to anything else holding the same list, including future calls if the list came from a module-level default. Returning a copy is the fix when the caller must not be able to change it.",
        ],
        homework=(
            "Write a function `stats(values)` that returns the minimum, maximum and mean of a list, returning None for all three when the list is empty. Call it with a non-empty list and unpack the result into three names, and call it with an empty list and print what comes back. "
            "Then write `head(values, n=1)` that returns a copy of the first n items, defaulting n to 1, and show that changing the returned list does not change the original. Your script must define at least two functions, return a tuple at least once, and print at least six results."
        ),
        required_patterns=["def ", "return", "if ", "print("], min_lines=6,
        rubric="Must return a tuple and unpack it, handle the empty case explicitly, return a copy rather than internal state, and print labelled results.",
    ),

    dict(
        day=9, title="Dictionaries: label your data", objective="Store keyed records and retrieve them safely",
        theory="""A list says *these values, in this order*. A dictionary says *this value belongs to that key*, and that is the right shape as soon as data has a name. A record like a student with a name, a score and a subject is awkward as three parallel lists and natural as a list of dicts.

Keys must be hashable, which in practice means strings, numbers and tuples of those. Values can be anything, including another dict, so a dict can represent a record with nested structure. Accessing a missing key raises `KeyError`, which is the correct behaviour: it means the code asked for something the data does not contain, and that should not pass silently. When absence is expected, use `dict.get(key, default)` or test `key in d`.

The methods worth memorising are `get`, `keys`, `values` and `items`. The last one is the most useful and the most often missed: it yields `(key, value)` pairs, which is exactly what you want when you need both. A loop that does `for k in d:` gives only the keys, and then a second lookup to get the value, which is the version that is usually written by mistake.

Building a dict by assigning into it in a loop is fine, but `dict.get(key, 0) + 1` is the idiom for counting, and it is worth recognising because the pattern of initialising, then accumulating into a key that may not exist yet, appears in almost every aggregation you will write.

`pop` removes and returns, `pop(key, default)` does the same without raising when the key is absent, and `setdefault` inserts a default only if the key is missing. These let you write get-or-create in one line.

Ordering is guaranteed: since Python 3.7 a dict keeps insertion order, so iterating gives the keys in the order they were added, not in some arbitrary internal order. Do not rely on it for anything meaningful, but you can rely on it not being random.

The example below builds a dict by counting, iterates with `items()`, uses `get` for a missing key, and shows `pop` removing an entry.""",
        code_example="""def count_words(text):
    counts = {}
    for word in text.lower().split():
        counts[word] = counts.get(word, 0) + 1
    return counts


counts = count_words('the cat sat on the mat the end')
for word, n in counts.items():
    print(f'{word:<6} {n}')

print('keys   :', sorted(counts))
print('values :', sorted(counts.values()))
print('missing via []      ->')
try:
    counts['dog']
except KeyError as err:
    print('   KeyError:', err)
print('missing via get     ->', counts.get('dog', 0))

removed = counts.pop('end', None)
print('popped "end"        ->', removed)
print('keys after pop      :', sorted(counts))""",
        questions=[
            "Why does `d['missing']` raise while `d.get('missing', 0)` does not, and which should you use?",
            "What does iterating a dict directly give you, and why is `items()` usually what you want?",
            "What does `counts.get(word, 0) + 1` do the first time a word is seen?",
        ],
        answers=[
            "Subscripting asserts that the key exists and raises if it does not, which is right when absence is a bug. get returns the default instead, which is right when absence is an expected case. Choose based on whether a missing key should stop the program.",
            "Iterating gives keys only, so a second lookup is needed for each value. items() yields the pair directly, which removes the redundant lookup and makes the loop body read as 'for this word, this count'.",
            "It returns 0 for a word not yet seen, adds one, and stores the result under that key, so the first occurrence creates the entry with the count 1 rather than raising a KeyError.",
        ],
        homework=(
            "Count how many times each word appears in a sentence you choose, using a dict and get. Print each word and its count, print the number of distinct words, and print the most common word. "
            "Then look up a word that is not present and show the difference between subscripting and get. Finally, use pop to remove one entry and print the keys before and after. Your script must build the dict in a loop, use items(), and print at least seven results."
        ),
        required_patterns=["=", "get(", "for ", "items()", "print("], min_lines=6,
        rubric="Must build the dict inside a loop with get, iterate with items(), demonstrate a missing-key lookup, and print labelled results including keys before and after a pop.",
    ),

    dict(
        day=10, title="Debugging and exceptions", objective="Read a traceback, catch the expected failure, and let the rest surface",
        theory="""An exception is Python telling you that an operation it was asked to perform does not make sense. The traceback that follows is the most useful thing the language gives you, and reading it is a skill worth practising deliberately.

The traceback lists the frames from outermost to innermost and ends with the exception type and message. The last line is the one that matters: it names the failure and the line that caused it. Earlier lines show how you got there, which is context rather than blame. Read from the bottom up, fix that line, and re-run before changing anything else.

Exceptions form a hierarchy under `Exception`. Catching `Exception` catches nearly everything, including the mistakes you have not thought of, which is why a broad except tends to turn a clear traceback into a silent wrong answer. Catch the narrow class you anticipated: `ZeroDivisionError`, `KeyError`, `IndexError`, `ValueError`, `FileNotFoundError`. Anything you did not anticipate should propagate, because an unhandled error in development is a bug found now rather than a wrong result found in production.

`try` and `except` are the tools for the failure you did anticipate. The `else` clause runs when the `try` block completed without raising, and putting the success path there rather than at the end of the `try` means it is not skipped when an early step fails. `finally` runs either way and is where you release a resource, so a file is closed even if the body raised.

A useful pattern for learning is to run the failing case without a handler first, so you can see the real traceback, then add the narrow handler. You learn twice: what actually goes wrong, and how to respond to it.

The example below catches one specific error, uses `else` for the success path, and deliberately lets an unanticipated error through so you can see what it looks like.""",
        code_example="""def safe_divide(a, b):
    try:
        result = a / b
    except ZeroDivisionError:
        return 'undefined'
    else:
        return result
    finally:
        print(f'  attempted {a} / {b}')


print('result:', safe_divide(8, 2))
print('result:', safe_divide(8, 0))

for line in ['42', 'seven', '']:
    try:
        print(f'  {line!r} ->', int(line))
    except ValueError as err:
        print(f'  {line!r} -> rejected: {err}')

try:
    {}['missing']
except KeyError as err:
    print('KeyError caught:', err)

try:
    print('unhandled demo:')
    1 / 0
except ZeroDivisionError:
    print('  caught, so no traceback shown')""",
        questions=[
            "Which line of a traceback tells you where the error actually happened, and why do the earlier lines exist?",
            "Why is catching `Exception` generally a mistake?",
            "What is the difference between the `else` and `finally` clauses of a `try`?",
        ],
        answers=[
            "The last line, which carries the exception type, its message and the line number. The earlier lines are the call stack, showing how execution reached that point, which is context for understanding rather than additional errors.",
            "Because it catches programming errors as well as the operational ones you meant to handle, so a misspelled name or a wrong argument type is absorbed instead of surfacing. The bug then shows up later as a wrong answer with no obvious cause.",
            "else runs only when the try block completed without raising, so the success path is not skipped by an earlier failure. finally runs whether or not anything was raised, which makes it the right place to release a resource.",
        ],
        homework=(
            "Write a function that converts a string to an integer and returns None when it cannot, catching ValueError only. Then write a function that reads a list of strings and separates the ones that convert from the ones that do not, printing a count of each. "
            "Use an else clause in at least one of them. Finally, deliberately trigger an uncaught exception and read the traceback, then add a handler for it. Your script must define at least two functions, use try, except and else, and print at least six results."
        ),
        required_patterns=["def ", "try:", "except ", "else:", "print("], min_lines=6,
        rubric="Must catch a specific exception class rather than Exception, use an else clause for a success path, handle a batch of inputs, and print counts for both outcomes.",
    ),

    dict(
        day=11, title="Files and structured data", objective="Read and write files, and pick a format that matches the data",
        theory="""Variables disappear when a program ends. Anything that must outlive one run has to be written down, which makes file handling the moment a script becomes useful beyond a single execution.

Text files are the simplest case. `open(path)` returns a file object that you read with iteration or write with, and it **must** be closed, or the data may never reach the disk. The `with` statement handles this for you: the file is opened, the block runs, and the file is closed even if the block raises. Use `with` by default and close the file yourself only if you have a reason not to.

Reading a whole file with `read()` is fine for small text, but `readlines()` or iteration are better for anything large, because they do not require holding the entire file in memory. Iteration is the clearest of the three: `for line in handle:` gives you one line at a time.

Separators matter. `read()` gives you a string and `readlines()` gives you a list of strings, each still ending in the newline, so `line.strip()` or `line.rstrip()` is usually what you want before comparing or printing.

The format should match the shape of the data. Plain text suits one value per line. CSV suits rows of the same fields, and the `csv` module handles quoting, commas inside fields and embedded newlines that a manual `split(',')` gets wrong. JSON suits nested structures with mixed types, and `json.dumps` and `json.loads` convert to and from Python objects. CSV cannot represent nesting; JSON cannot represent a column of differing type without awkwardness. Choosing wrongly is the source of most data-handling bugs.

`FileNotFoundError` is a `FileNotFoundError` to catch, not a reason to wrap everything in a bare except.

The example below writes lines, reads them back, round-trips a record through JSON, and handles a missing file by catching the specific error.""",
        code_example="""import json
import os
import tempfile

fd, path = tempfile.mkstemp(suffix='.txt')
os.close(fd)
try:
    with open(path, 'w', encoding='utf-8') as handle:
        handle.write('alpha\\n')
        handle.write('beta\\n')
        handle.write('gamma\\n')

    with open(path, encoding='utf-8') as handle:
        for number, line in enumerate(handle, 1):
            print(f'{number}: {line.strip()}')

    record = {'name': 'Asha', 'scores': [88, 74], 'active': True}
    text = json.dumps(record, sort_keys=True)
    print('json  :', text)
    print('parsed:', json.loads(text) == record)

    with open(path + '.missing', encoding='utf-8') as handle:
        handle.read()
except FileNotFoundError as err:
    print('missing file handled:', type(err).__name__)
finally:
    if os.path.exists(path):
        os.unlink(path)
    print('cleaned up')""",
        questions=[
            "What does the `with` statement do that manual open and close does not?",
            "Why is `split(',')` a poor substitute for the `csv` module?",
            "What does `json.loads` return, and is it the same type as what you passed to `json.dumps`?",
        ],
        answers=[
            "It closes the file when the block ends, including when the block raises, so an error partway through cannot leave the handle open and the data unflushed or leaked.",
            "It has no notion of quoting, so a field containing a comma becomes two fields, and it has no notion of embedded newlines, so one record can become two lines. The csv module writes the quoting that read_csv then has to undo.",
            "It returns a Python object built from the JSON, so for a dict input you get a dict back. That is why the round trip compares equal, and it is the property that makes JSON a reasonable choice for structured configuration.",
        ],
        homework=(
            "Write three lines of text to a file, then read them back and print each with its line number. Then create a dict holding at least three fields, write it as JSON, read it back and print whether the round trip was equal. "
            "Finally, attempt to open a path that does not exist and handle it with FileNotFoundError, printing a clear message. Your script must use with open at least twice, must close every file it opens, and must print at least six results."
        ),
        required_patterns=["with open(", "for ", "print("], min_lines=6,
        rubric="Every file must be opened with a with block, must demonstrate a text round trip and a JSON round trip, and must handle a missing file specifically.",
    ),

    dict(
        day=12, title="Testing your own code", objective="Write assertions that check the parts you are not looking at",
        theory="""Print statements tell you what happened once, on the inputs you happened to try. An assertion states what must be true and keeps checking it, so the next change cannot break it silently. That is the difference between a program you debug and a program you can modify without fear.

`assert condition, "message"` raises `AssertionError` when the condition is false. It is the smallest useful test. Testing is not only about finding bugs; writing the assertion first often clarifies what a function should do, and a test you can read is a specification anyone can check.

The pattern that scales is arrange, act, assert: set up the inputs, do the one thing, check the result. Keeping those three parts visually separate means when a test fails you know immediately which part is wrong, and the failure message tells you what was expected and what happened.

Test the boundaries, not the middle. Zero, one, many, empty, negative, and the largest value the type allows are where bugs live, because that is where the off-by-one and the empty-collection assumptions break. A function that averages numbers has a zero-length list problem, and a function that finds the maximum has an empty-list problem. Test them.

Assert on behaviour rather than on implementation. Checking that a function returns 4 is useful; checking that it internally called a helper with particular arguments locks you into a structure and makes the next refactor fail for no reason.

Assertions vanish when Python runs with optimisation enabled, so they are not a substitute for a real test framework once a project grows. At this scale they are exactly the right tool, and they teach the habit the frameworks are built on.

The example below runs a small test suite, including the empty and single-element boundaries, and shows what a failure looks like so you recognise it.""",
        code_example="""def average(values):
    if not values:
        raise ValueError('values must not be empty')
    return sum(values) / len(values)


def test_average():
    assert average([2, 4, 6]) == 4.0, 'mid-range average'
    assert average([5]) == 5.0, 'single value is its own average'
    assert average([0, 10]) == 5.0, 'boundaries average correctly'


def test_average_rejects_empty():
    try:
        average([])
    except ValueError:
        return
    raise AssertionError('average([]) should have raised')


for test in (test_average, test_average_rejects_empty):
    try:
        test()
        print(f'{test.__name__}: passed')
    except AssertionError as err:
        print(f'{test.__name__}: FAILED - {err}')

try:
    assert average([1, 2]) == 99, 'this is meant to fail'
except AssertionError as err:
    print('a failing assertion looks like:', err)""",
        questions=[
            "Why test the empty and single-element cases rather than only a typical value?",
            "What is the risk of asserting on how a function is implemented instead of what it returns?",
            "Why can assertions not be your only safety net in a released program?",
        ],
        answers=[
            "Because those are where the assumptions break: an empty list has no maximum, a single element exposes off-by-one errors in averaging or indexing, and a zero is a common accidental divisor. Typical values pass whether or not the boundary logic is right.",
            "It couples the test to the current structure, so a refactor that preserves behaviour still fails the test. That trains you to avoid changing working code, which is the opposite of what tests are for.",
            "Because assertions are removed entirely when Python runs with optimisation enabled, and because a test that crashes still crashes the user. Released code needs failures handled and reported, not raised.",
        ],
        homework=(
            "Write a function `is_even(n)` and three assertions covering a positive even number, a negative even number and zero. Write a second function `max_of(values)` and a test that it raises on an empty list. "
            "Then deliberately break one assertion, run the suite and read the failure message, before fixing it. Your script must define at least two functions, contain at least four assertions including a boundary case, and print the result of running each test."
        ),
        required_patterns=["def ", "assert ", "try:", "except ", "print("], min_lines=6,
        rubric="Must include boundary cases in the assertions, must test a raising path, and must demonstrate reading a failure message before fixing it.",
    ),

    dict(
        day=13, title="Problem decomposition", objective="Break a problem into parts you can write, test and combine",
        theory=""""I don't know how to write this" almost always means the problem is too big, not that the syntax is hard. Decomposition is the skill of cutting a task until each piece is small enough to hold in your head, and it is the difference between a difficulty that shrinks as you work and one that stays the same size throughout.

The first move is to state the problem in one sentence, in terms of input and output, before writing any code. If you cannot do that, you do not yet know what you are building, and the code will not help. "Read a list of names and print the longest" is a complete specification. "Deal with the names" is not.

The second is to find the nouns and the verbs. Nouns suggest the data structures you need and verbs suggest the functions. Then do the second step before the first: figure out what each function must do, what it takes and what it gives back, and write or test them one at a time. Only assemble them once each part works on its own.

The third is to work out the order. Some parts depend on others: you cannot compute an average before you have cleaned the numbers, so clean first even if cleaning is the boring part. Doing the hard, dependent work first and leaving the assembly for last keeps the number of things that can be wrong at any moment small.

The last is to know when to stop decomposing. A piece that fits on screen and that you can describe in one sentence is done. Decomposing past that produces functions that are so small their names are meaningless and their parameters exceed their bodies.

Decomposition is also how you get unstuck. If you cannot write a function, that is not a signal to try harder; it is a signal that it is not yet small enough, and the question to ask is which part of it is still unclear.

The example below takes a messy task, states the specification, names the parts, and builds it in that order, showing each stage running before the next begins.""",
        code_example="""def clean_records(raw_lines):
    out = []
    for line in raw_lines:
        name, score = line.split(',')
        name = name.strip()
        if not name:
            continue
        out.append((name, int(score)))
    return out


def average_of(records):
    if not records:
        return 0.0
    return sum(score for _name, score in records) / len(records)


def top_scorers(records, n):
    return sorted(records, key=lambda r: r[1], reverse=True)[:n]


def report(records):
    lines = ['name,score']
    lines += [f'{name},{score}' for name, score in records]
    return '\\n'.join(lines)


# Assemble last, and only from parts that already work.
raw = [' Asha ,88', 'Rohan,74', ' ,99', 'Meera,91']
records = clean_records(raw)
print('cleaned  :', records)
print('average  :', average_of(records))
print('top two  :', top_scorers(records, 2))
print('report   :')
print(report(records))""",
        questions=[
            "What does it mean to state the problem in input and output terms before writing code, and why does it help?",
            "Why is it worth working out what each function returns before writing any of them?",
            "What is the sign that a function has been decomposed too far?",
        ],
        answers=[
            "It means you can say what goes in and what comes out, which is the only way to know when you are finished. It also exposes the cases where you cannot state the output precisely, which are the requirements you have not thought through.",
            "Because it separates the interface from the implementation. You can then implement and test each part against a written contract, and a failure tells you which contract broke rather than which line went wrong.",
            "The function's parameters take up more room than its body, and its name has to be qualified with a comment to be understood. That is a sign it is doing too little, and the pieces cost more in comprehension than they save.",
        ],
        homework=(
            "Choose a small task of your own, such as tallying words in a list of sentences or finding the second-largest value. Write the specification in one sentence naming the input and the output, then list the functions you need and what each returns. "
            "Implement and test each function separately, printing its result at each stage, and only then assemble them. Your script must define at least three functions, must print a labelled result from each before assembly, and must include a specification line in a comment."
        ),
        required_patterns=["def ", "return", "for ", "print(", "#"], min_lines=7,
        rubric="Must state the specification in a comment, define at least three functions, and demonstrate each working in isolation before assembly.",
    ),

    dict(
        day=14, title="Foundation capstone", objective="Build one small program that uses every foundation concept",
        theory="""The capstone is deliberately unglamorous. It is not a framework, a library or an algorithm worth writing about, because the point is not the program. The point is that every idea from the previous thirteen days is load-bearing in it, and that you built it yourself.

Read the requirements before the code. The program reads a small dataset, cleans it, computes something over it, makes a decision, and writes a report. Cleaning uses string methods and type conversion. Storage is a list of records. Lookup is a dict. The computation is a function that returns a value. The decision is a conditional. The reporting is a file write. Error handling covers the input being malformed rather than assuming it never is.

The shape to notice is the one from the previous day: small functions, each with a clear contract, assembled last. `parse` knows how to turn a line into a record and returns None when it cannot. `summarise` knows how to reduce records to numbers. `render` knows how to turn a result into text. None of them knows about the others, and each could be tested by itself. That is the property that makes a program like this easy to change six months later.

The other thing to notice is what happens on bad input. A blank line, a missing field and a non-numeric score are all handled, and each produces a recorded rejection rather than a crash. A program that stops on the first surprise is a program that will stop, eventually, in front of someone.

Run it, then change the requirement: add a column, change the threshold, make it sort differently. If the change is local to one function, the decomposition worked. If it touches everything, it did not, and the fix is to go back one day and cut another seam.

The exercises below ask you to extend it rather than replace it, which is the harder and more valuable direction.""",
        code_example="""def parse(line):
    parts = line.split(',')
    if len(parts) != 2:
        return None
    name = parts[0].strip()
    if not name:
        return None
    try:
        score = int(parts[1].strip())
    except ValueError:
        return None
    return name, score


def summarise(records, threshold):
    passed = [r for r in records if r[1] >= threshold]
    average = sum(r[1] for r in records) / len(records) if records else 0.0
    return {'total': len(records), 'passed': len(passed), 'average': average}


def render(stats, rejections):
    lines = [f"total: {stats['total']}", f"passed: {stats['passed']}",
             f"average: {stats['average']:.2f}", f"rejected: {len(rejections)}"]
    return '\\n'.join(lines)


raw = [' Asha,88', 'Rohan,74', 'broken line', ' ,91', 'Meera,notanumber', 'Kabir,66']
records, rejections = [], []
for line in raw:
    record = parse(line)
    if record is None:
        rejections.append(line)
    else:
        records.append(record)

stats = summarise(records, 70)
print('records :', records)
print('rejected:', rejections)
print('summary :', stats)
print(render(stats, rejections))""",
        questions=[
            "Why does `parse` return None rather than raising, and what would change if it raised?",
            "What property of this program would tell you the decomposition worked, when you later add a new column?",
            "Which of the previous thirteen days is not exercised by this program, and would adding it improve the program or just its length?",
        ],
        answers=[
            "Because a malformed line is an expected condition in a batch of user input, not a programming fault. If parse raised, the caller would need a handler per call and could not easily count the bad rows; returning None keeps the decision with the caller, which is where the reporting decision belongs.",
            "If the change is local to one function and the others are untouched, the seams are in the right places. If the new column requires editing parse, summarise and render together, they are coupled and the split was not real.",
            "Argument parsing from the command line is not exercised. Adding it would genuinely improve the program, because a hardcoded list in the source means rerunning it means editing code, which is exactly the coupling the previous lessons argued against.",
        ],
        homework=(
            "Extend the capstone so it reads its input from a file rather than a list defined in the source, and so it writes its report to a file as well. Add a command-line argument for the pass threshold, with a default, and validate it so a non-numeric argument is rejected with a clear message rather than crashing. "
            "Then add a test function for `parse` covering a good line, a missing field, an empty name and a non-numeric score, and print the result of running it. Your script must use with open, at least one argument, a try/except, and an assert, and must print at least six results."
        ),
        required_patterns=["def ", "for ", "if ", "return", "print("], min_lines=8,
        rubric="Must keep parse and summarise independent and report rejections separately from records. The homework extends this to files, a command-line argument and a test covering all four malformed cases; the worked example stops short of those so the extension is the student's work.",
    ),
)
LESSONS = tuple(sorted(LESSONS, key=lambda l: l["day"]))

# Each day carries a further treatment appended after the main body. It is
# assembled here rather than inline so each lesson reads as one piece when read
# on its own, and so the standard is checked on the assembled result.
from app.foundation_additions import ADDITIONS  # noqa: E402

LESSONS = tuple(
    {**lesson, "theory": lesson["theory"].rstrip() + "\n" + ADDITIONS[lesson["day"]].strip()}
    if lesson["day"] in ADDITIONS else lesson
    for lesson in LESSONS
)


def _words(text: str) -> int:
    return len(re.findall(r"\b[\w'-]+\b", text or ""))


def validate(lesson: dict) -> list[str]:
    """Return every reason this lesson is not fit to seed."""
    problems = []
    w = _words(lesson["theory"])
    if not MIN_THEORY_WORDS <= w <= MAX_THEORY_WORDS:
        problems.append(f"theory {w} words, need {MIN_THEORY_WORDS}-{MAX_THEORY_WORDS}")
    if len(lesson["questions"]) != 3:
        problems.append(f"{len(lesson['questions'])} questions, need 3")
    if len(lesson["answers"]) != 3:
        problems.append(f"{len(lesson['answers'])} answers, need 3")
    if len(lesson["homework"]) < 120:
        problems.append(f"homework {len(lesson['homework'])} chars, need 120")
    if not lesson.get("required_patterns"):
        problems.append("no required_patterns")
    if not lesson.get("min_lines"):
        problems.append("no min_lines")
    try:
        ast.parse(lesson["code_example"])
    except SyntaxError as err:
        problems.append(f"code syntax error: {err}")
    return problems


def run_code(lesson: dict) -> str:
    buf = io.StringIO()
    with redirect_stdout(buf):
        exec(compile(lesson["code_example"], f"d{lesson['day']}", "exec"), {})
    return buf.getvalue()


def apply(conn: sqlite3.Connection, paths: list[str], lessons=None) -> dict:
    lessons = lessons if lessons is not None else LESSONS
    written = 0
    for lesson in lessons:
        for slug in paths:
            row = conn.execute(
                "SELECT l.id AS id FROM lessons l JOIN paths p ON p.id = l.path_id "
                "WHERE p.slug = ? AND l.day_number = ?",
                (slug, lesson["day"]),
            ).fetchone()
            if row is None:
                continue
            conn.execute(
                """UPDATE lessons SET title = ?, theory = ?, code_example = ?,
                   questions = ?, answers = ?, homework = ?, day_type = 'concept',
                   status = 'active', status_reason = 'authored to the current standard',
                   status_note = '' WHERE id = ?""",
                (lesson["title"], lesson["theory"], lesson["code_example"],
                 json.dumps(lesson["questions"]), json.dumps(lesson["answers"]), lesson["homework"],
                 row["id"]),
            )
            # The objective lives on the milestone, not the lesson, so the day
            # carries the same wording in both the lesson body and the roadmap.
            conn.execute(
                """UPDATE milestones SET objective = ?, mastery_criteria = ?
                   WHERE id = (SELECT m.id FROM lesson_milestones lm
                               JOIN milestones m ON m.id = lm.milestone_id
                               WHERE lm.lesson_id = ?)""",
                (lesson["objective"], lesson["rubric"], row["id"]),
            )
            a = conn.execute("SELECT id FROM assignments WHERE lesson_id = ?", (row["id"],)).fetchone()
            if a is None:
                conn.execute(
                    """INSERT INTO assignments (lesson_id, prompt, required_patterns, min_lines, rubric)
                       VALUES (?, ?, ?, ?, ?)""",
                    (row["id"], lesson["homework"], json.dumps(lesson["required_patterns"]),
                     lesson["min_lines"], lesson["rubric"]))
            else:
                conn.execute(
                    """UPDATE assignments SET prompt = ?, required_patterns = ?, min_lines = ?,
                       rubric = ? WHERE id = ?""",
                    (lesson["homework"], json.dumps(lesson["required_patterns"]),
                     lesson["min_lines"], lesson["rubric"], a["id"]))
            written += 1
    conn.commit()
    return {"written": written}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--db", default=str(DB_PATH))
    ap.add_argument("--paths", nargs="*", default=list(DOMAINS))
    ap.add_argument("--validate-only", action="store_true")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    before = len(LESSONS)
    bad = 0
    print(f"validating {before} foundation lessons\n")
    for lesson in LESSONS:
        problems = validate(lesson)
        if problems:
            bad += 1
            print(f"  FAIL d{lesson['day']:<3} {lesson['title'][:34]:<36} {'; '.join(problems)}")
        else:
            w = _words(lesson["theory"])
            print(f"  ok   d{lesson['day']:<3} {lesson['title'][:34]:<36} {w}w")
    print(f"\n{before - bad}/{before} valid, {bad} failed")
    if bad:
        return 1
    if args.validate_only or not args.apply:
        print("validate only. pass --apply to seed.")
        return 0

    conn = sqlite3.connect(args.db)
    conn.row_factory = sqlite3.Row
    n_before = conn.execute("SELECT COUNT(*) FROM lessons").fetchone()[0]
    res = apply(conn, args.paths)
    print(f"\nseeded {res['written']} rows across {len(args.paths)} paths")

    print("\n=== verify: re-read from the database and re-check ===")
    ok = fail = 0
    for lesson in LESSONS:
        for slug in args.paths:
            r = conn.execute(
                """SELECT l.theory, l.questions, l.answers, l.code_example, l.homework,
                          l.status, l.day_type
                   FROM lessons l JOIN paths p ON p.id = l.path_id
                   WHERE p.slug = ? AND l.day_number = ?""",
                (slug, lesson["day"])).fetchone()
            issues = []
            if r["status"] != "active":
                issues.append(f"status={r['status']}")
            w = _words(r["theory"])
            if not MIN_THEORY_WORDS <= w <= MAX_THEORY_WORDS:
                issues.append(f"theory {w}w")
            if len(json.loads(r["questions"])) != 3:
                issues.append("questions")
            if len(json.loads(r["answers"])) != 3:
                issues.append("answers")
            if len(r["homework"]) < 120:
                issues.append("homework")
            try:
                buf = io.StringIO()
                with redirect_stdout(buf):
                    exec(compile(r["code_example"], "db", "exec"), {})
            except Exception as err:
                issues.append(f"code {type(err).__name__}")
            if issues:
                fail += 1
                if fail <= 8:
                    print(f"  FAIL {slug} d{lesson['day']}: {'; '.join(issues)}")
            else:
                ok += 1
    print(f"verified ok {ok}, bad {fail}")
    n_after = conn.execute("SELECT COUNT(*) FROM lessons").fetchone()[0]
    print(f"lessons {n_before} -> {n_after} ({'unchanged' if n_before == n_after else 'CHANGED'})")

    print("\n=== idempotency: second apply must change nothing ===")
    snap = [tuple(r) for r in conn.execute(
        "SELECT l.id, l.title, l.theory, l.code_example, l.homework, m.objective "
        "FROM lessons l JOIN lesson_milestones lm ON lm.lesson_id = l.id "
        "JOIN milestones m ON m.id = lm.milestone_id ORDER BY l.id")]
    apply(conn, args.paths)
    again = [tuple(r) for r in conn.execute(
        "SELECT l.id, l.title, l.theory, l.code_example, l.homework, m.objective "
        "FROM lessons l JOIN lesson_milestones lm ON lm.lesson_id = l.id "
        "JOIN milestones m ON m.id = lm.milestone_id ORDER BY l.id")]
    diff = sum(1 for a, b in zip(snap, again) if a != b)
    print(f"rows changed on second apply: {diff}  "
          f"({'IDEMPOTENT' if diff == 0 else 'NOT IDEMPOTENT'})")
    return 0 if (fail == 0 and diff == 0) else 1


if __name__ == "__main__":
    raise SystemExit(main())
