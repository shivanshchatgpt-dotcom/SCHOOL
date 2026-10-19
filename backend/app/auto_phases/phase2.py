"""Automation / Scripting phase 2, days 90-104: commands, arguments and config.

Every example is stdlib-only, offline and deterministic. Argument lists and
environment variables are passed to functions as plain data, configuration is
parsed from in-memory strings, and nothing reads `sys.argv`, the real
environment, the clock or the filesystem.
"""

PHASE = (
    "Commands, Arguments and Config",
    "Turn a script into a command people can run by treating arguments, environment and config as data with clear precedence and honest validation.",
    {
        90: dict(
            topic="Orientation: scripts people can run",
            idea=(
                "A script people can run is not the same thing as a file of Python that happens to work on your machine. "
                "The difference is an entry point: one obvious function that receives the arguments, decides what to do, "
                "and returns an exit code instead of printing a traceback. A useful convention is `main(argv)` where "
                "`argv` is a plain list of strings, plus a small guard at the bottom that only calls it when the file is "
                "executed directly. Keeping `argv` as a parameter is the habit that matters most, because it means every "
                "decision the script makes is a function of data you can hand it in a test. The exit code is the second "
                "habit: zero means success, non-zero means something needs attention, and a scheduler reads that number "
                "rather than your log. Finally, a script people can run says what it expects. When it is called with no "
                "arguments it should print a short usage line rather than fail with an index error. Today you build that "
                "shape: a `main` function, an explicit argument list, a usage message and an exit code. The code is tiny "
                "on purpose. Everything in this phase is about where values come from and how they are checked, and that "
                "begins with an entry point you can call from a test."
            ),
            code=(
                'def main(argv):\n'
                '    if not argv:\n'
                '        print("usage: report.py <source> [--limit N]")\n'
                '        return 2\n'
                '    source = argv[0]\n'
                '    print("script: report.py")\n'
                '    print("source:", source)\n'
                '    print("arguments:", len(argv))\n'
                '    return 0\n'
                '\n'
                'code = main(["inbox"])\n'
                'print("exit code:", code)\n'
                'assert code == 0\n'
                'assert main([]) == 2\n'
                'print("the entry point is a function of a list")'
            ),
            variant_b='show what happens if main indexes argv without checking for an empty list',
            variant_c='return 2 for a missing argument and 0 otherwise, then print both codes in order',
            mistakes=[
                "Reading the real command line deep inside helper functions instead of one entry point.",
                "Returning None on failure, so a scheduler cannot tell success from an error.",
                "Letting an empty argument list crash with an index error instead of printing usage.",
            ],
            q1=(
                "Why should the entry point take an argument list instead of reading the real one?",
                "A list is ordinary data, so tests can call the function with any input without launching a subprocess.",
            ),
            homework=(
                "Write `main(argv)` that prints a usage line when the list is empty, otherwise prints the first "
                "argument and returns 0. Call it with one realistic argument list and with an empty one, print both "
                "exit codes, and comment which line makes the entry point testable."
            ),
            patterns=["def main", "return ", "print("],
            mapping=(
                "`argparse`, `click` and `typer` all build on this same entry point idea: one function receives the "
                "parsed values and returns an exit code that the shell can read."
            ),
        ),
        91: dict(
            topic="argv as data",
            idea=(
                "`sys.argv` is a list of strings: the program name first, then whatever the user typed, split on spaces "
                "by the shell. That is the whole model. The moment you stop reading it directly and start passing a list "
                "around, argument handling becomes ordinary data processing, which is why this day is called argv as "
                "data. A function can take the list, split off the program name, and return the remaining values; a test "
                "can call it with any list it likes without launching a subprocess. Notice what argv does not tell you. "
                "It does not say which values are required, which are flags or what type they should become, and it does "
                "not remember the quotes the user typed. It is only text. That is exactly why the next days add a schema "
                "on top: the raw list is the input, parsed settings are the output. Two details are worth internalising "
                "now. The first element is the program name, so slicing from index one is the normal move, and an "
                "argument that looks like `--limit` is still just a string until a parser gives it meaning. Today you "
                "split a list, describe it and assert on it. Nothing reads the real command line, and that is the point: "
                "the argument layer is testable because it is only a list."
            ),
            code=(
                'def split_argv(argv):\n'
                '    return argv[0], argv[1:]\n'
                '\n'
                'def describe(argv):\n'
                '    program, args = split_argv(argv)\n'
                '    return {"program": program, "count": len(args), "args": args}\n'
                '\n'
                'first = describe(["copy.py", "a.txt", "b.txt"])\n'
                'second = describe(["copy.py"])\n'
                'print("first:", first)\n'
                'print("second:", second)\n'
                '\n'
                'assert first["args"] == ["a.txt", "b.txt"]\n'
                'assert second["count"] == 0\n'
                'print("the rest of argv is just a list of strings")'
            ),
            variant_b='pass a list with the program name in the middle and explain why index zero is special',
            variant_c='return a copy of the argument slice and show that changing it leaves the original list intact',
            mistakes=[
                "Treating the program name as a normal argument, so every positional value shifts by one.",
                "Indexing into argv before checking its length, which crashes on an empty invocation.",
                "Mutating the list in place while parsing, so later checks see values that never reached the user.",
            ],
            q1=(
                "What does argv contain before any parsing happens?",
                "A list of plain strings: the program name first, followed by the tokens the shell split apart.",
            ),
            homework=(
                "Write `split_argv(argv)` that returns the program name and the remaining tokens as separate values. "
                "Call it with two different lists, including one where the program is the only element, print both "
                "results, and comment why the function never needs to read the real command line."
            ),
            patterns=["def ", "return", "print("],
            mapping=(
                "`argparse` accepts any list of strings through its `args` parameter, and that is why a parser can be "
                "tested directly; `click` and `typer` expose the same seam."
            ),
        ),
        92: dict(
            topic="Parsing flags",
            idea=(
                "A flag is a token that starts with a dash and carries a name, and parsing flags is the small act of "
                "turning those tokens into a dictionary. Two shapes dominate. `--name=value` puts the name and value in "
                "one token, so a single split on the first equals sign separates them. `--verbose` has no value at all, "
                "and the honest representation is a boolean, not the empty string. Mixing the two in one pass is fine as "
                "long as the rule is explicit: split on the first `=` when it exists, otherwise treat the token as a "
                "switch. The first-equals rule matters more than it looks. Values can contain equals signs, and using "
                "`split(\"=\")` without a limit silently drops everything after the second one, which is a classic bug in "
                "scripts that handle URLs or query strings. You should also decide early what happens to unknown flags. "
                "Ignoring them feels friendly and hides typos; rejecting them catches `--ouput` before it writes to the "
                "wrong folder. Today you write a parser over a list of tokens and inspect the result. The values will "
                "still be strings, because argv has no types. Everything is text until you choose to convert it, and "
                "that choice belongs in the next layer, not in the tokenizer."
            ),
            code=(
                'def parse_flags(args):\n'
                '    flags = {}\n'
                '    for token in args:\n'
                '        if token.startswith("--") and "=" in token:\n'
                '            name, value = token[2:].split("=", 1)\n'
                '            flags[name] = value\n'
                '        elif token.startswith("--"):\n'
                '            flags[token[2:]] = True\n'
                '    return flags\n'
                '\n'
                'parsed = parse_flags(["--limit=5", "--verbose", "--name=a=b"])\n'
                'print("parsed:", parsed)\n'
                'print("limit type:", type(parsed["limit"]).__name__)\n'
                'assert parsed["verbose"] is True\n'
                'assert parsed["name"] == "a=b"\n'
                'print("flags arrive as text; conversion is a separate step")'
            ),
            variant_b='add an "--output=" flag and parse a value that contains two equals signs',
            variant_c='make a repeated flag keep the last value and print which occurrence won',
            mistakes=[
                "Splitting on every equals sign, which cuts off values such as a URL query string.",
                "Storing a bare switch as an empty string, so a presence check looks falsy.",
                "Silently ignoring unknown flags, so a typo becomes a silently wrong default.",
            ],
            q1=(
                "Why split a flag token on the first equals sign only?",
                "Values may themselves contain equals signs, and a full split would discard everything after the second one.",
            ),
            homework=(
                "Write `parse_flags(args)` that turns `--name=value` tokens into string values and bare `--name` "
                "tokens into `True`. Parse a list containing both forms plus a value with an equals sign, print the "
                "dict, and comment which line keeps that value intact."
            ),
            patterns=["def ", 'split("=", 1)', "print("],
            mapping=(
                "`argparse` distinguishes `store_true` switches from `--name=value` options, and `click` mirrors this "
                "with `is_flag`; the underlying token rules are the ones you wrote today."
            ),
        ),
        93: dict(
            topic="Positional versus optional",
            idea=(
                "Positional and optional arguments fail in different ways, so it helps to treat them as two separate "
                "channels. A positional value is identified by where it appears: the first token is the source, the "
                "second is the destination, the third is something else. An optional value is identified by its name, so "
                "its position does not matter and it can be omitted. Most real commands have both, which is why the order "
                "of the two on the command line should be flexible even if the positional order is not. The practical "
                "rule is to collect named tokens into a dictionary and everything else into a list, then decide whether "
                "the list has the right length. Doing that in one pass keeps the code short and makes the failure message "
                "easy to write: the number of positional values is the only thing the user got wrong. It also exposes a "
                "mistake people make when they hand-roll parsing: a flag placed before a positional value should not "
                "shift the positional order. Because they live in separate channels, it does not. Today you classify a "
                "token list into positionals and options and assert on both. Notice that classification is not "
                "validation yet; it only says what kind of token you saw, not whether the values make sense."
            ),
            code=(
                'def classify(args):\n'
                '    positional = []\n'
                '    optional = {}\n'
                '    for token in args:\n'
                '        if token.startswith("--"):\n'
                '            name, _, value = token[2:].partition("=")\n'
                '            optional[name] = value or True\n'
                '        else:\n'
                '            positional.append(token)\n'
                '    return positional, optional\n'
                '\n'
                'pos, opt = classify(["--force", "inbox", "outbox", "--limit=3"])\n'
                'print("positional:", pos)\n'
                'print("optional:", opt)\n'
                'assert pos == ["inbox", "outbox"]\n'
                'assert opt == {"force": True, "limit": "3"}\n'
                'print("a flag before a value does not shift the positional order")'
            ),
            variant_b='place both flags after the positional values and confirm the same two channels come out',
            variant_c='return a third list of unknown dash tokens so a caller can report them instead of dropping them',
            mistakes=[
                "Mixing named and positional values in one list, then guessing which is which by position.",
                "Letting a flag consume the next token as its value when the user wrote it without an equals sign.",
                "Validating positional count before classification, so a flag is counted as a missing argument.",
            ],
            q1=(
                "Why keep positional values and named options in separate channels?",
                "They are identified differently, by order versus by name, so separating them makes both checks simple and independent.",
            ),
            homework=(
                "Write `classify(args)` that returns two values: a list of positional tokens and a dict of named "
                "options. Test it with flags before and after positional values, print both channels, and comment why "
                "a flag does not shift the positional order."
            ),
            patterns=["def ", "partition", "print("],
            mapping=(
                "`argparse` calls these positionals and optionals, and its parser handles interplay such as `--` to "
                "end option parsing; `click` and `typer` make the distinction visible in the function signature."
            ),
        ),
        94: dict(
            topic="Defaults and required values",
            idea=(
                "Defaults and required values are a schema question, not a parsing question. Once tokens are in a "
                "dictionary, you still have to fill gaps from defaults and refuse to continue when something essential "
                "is missing. A small table is the clearest way to express this: every setting gets a name, a default and "
                "a required flag. Then the same table drives three things at once: filling values, checking what is "
                "missing and later phrasing the help text. That is the advantage of data-driven settings over a chain of "
                "if statements. The order is important. Apply defaults first, then check required values on the merged "
                "result, so a required field that received a default never reports as missing. Keep `None` distinct from "
                "an empty string, because they mean different things: one is absent, the other is present but blank, and "
                "the user needs different advice for each. Also resist the temptation to invent defaults for required "
                "values just to make the program continue. A missing input folder is not a case for a sensible guess; it "
                "is a case for a clear message and a non-zero exit code. Today you build the schema table, merge values, "
                "and return the list of missing required names, all without any real parser."
            ),
            code=(
                'SCHEMA = {\n'
                '    "input": {"required": True},\n'
                '    "output": {"default": "out"},\n'
                '    "limit": {"default": "10"},\n'
                '}\n'
                '\n'
                'def parse(args):\n'
                '    values = {}\n'
                '    for token in args:\n'
                '        if token.startswith("--") and "=" in token:\n'
                '            name, value = token[2:].split("=", 1)\n'
                '            values[name] = value\n'
                '    return {name: values.get(name, rule.get("default")) for name, rule in SCHEMA.items()}\n'
                '\n'
                'def missing(settings):\n'
                '    return [n for n, r in SCHEMA.items() if r.get("required") and settings.get(n) is None]\n'
                '\n'
                'a = parse(["--input=inbox"])\n'
                'b = parse([])\n'
                'print("a:", a)\n'
                'print("b:", b)\n'
                'print("b missing:", missing(b))\n'
                'assert a["output"] == "out" and missing(a) == []\n'
                'assert missing(b) == ["input"]'
            ),
            variant_b='add a required "--output" and show that a default value no longer satisfies it',
            variant_c='distinguish an empty string from an absent value and report the empty one separately',
            mistakes=[
                "Checking for required values before defaults are applied, so defaulted fields report as missing.",
                "Inventing a fallback for a required value, which hides a genuine configuration error.",
                "Conflating `None` with an empty string, so the message tells the user the wrong thing.",
            ],
            q1=(
                "Why apply defaults before checking required values?",
                "A field that legitimately has a default is never actually missing, so checking first would produce false problems.",
            ),
            homework=(
                "Write `parse(args)` that fills `input`, `output` and `limit` from a schema with one required field "
                "and two defaults, plus `missing(settings)` returning the names still absent. Run it with and without "
                "the required flag, print both settings, and comment which step applies defaults before checking."
            ),
            patterns=["def ", "get(", "print("],
            mapping=(
                "`argparse` expresses defaults with `default=` and required options with `required=True`; `click` uses "
                "`default` and `required` on each option, and both then share the same validation shape."
            ),
        ),
        95: dict(
            topic="Config files as dicts",
            idea=(
                "Configuration files look special until you parse one; after that they are dicts, and the dict is what "
                "the rest of the program should see. That is the useful mental model. A file is a storage format, a "
                "dict is the value, and a loader is the short function that converts one into the other. Keeping the "
                "loader separate means the rest of the code never cares whether settings came from JSON, TOML or a test "
                "fixture. It also means you can check that the file contains what you expect before you use it. A common "
                "mistake is trusting the file completely and then failing with a `KeyError` deep in the work. A better "
                "pattern is to read only the keys you recognise, ignore unknown ones deliberately, and report missing "
                "required ones through the same validation path that handles flags. Types matter here too: JSON gives you "
                "numbers and booleans properly, while environment variables and argv will not. That difference is the "
                "main reason the merge step needs a coercion pass later. Today you load a JSON document from an "
                "in-memory string, keep the keys you know, and confirm that the result is an ordinary dictionary you can "
                "merge and test like any other. No file is opened."
            ),
            code=(
                'import json\n'
                '\n'
                'CONFIG_TEXT = \'{"input": "inbox", "output": "out", "limit": 5, "owner": "ops"}\'\n'
                '\n'
                'def load_config(text):\n'
                '    data = json.loads(text)\n'
                '    return {key: data[key] for key in ("input", "output", "limit") if key in data}\n'
                '\n'
                'config = load_config(CONFIG_TEXT)\n'
                'print("config:", config)\n'
                'print("limit plus one:", config["limit"] + 1)\n'
                'print("ignored keys:", sorted(set(json.loads(CONFIG_TEXT)) - set(config)))\n'
                'assert config == {"input": "inbox", "output": "out", "limit": 5}\n'
                'print("the loaded config is just a dict")'
            ),
            variant_b='load a document missing the limit key and confirm the loader simply omits it',
            variant_c='add a nested section for output options and flatten the one key the program needs',
            mistakes=[
                "Passing the whole parsed document around instead of the recognised settings dict.",
                "Assuming every key exists and crashing with a KeyError halfway through the work.",
                "Forgetting that JSON numbers and booleans already have types, unlike argv values.",
            ],
            q1=(
                "What should the program work with after a config file is loaded?",
                "A plain dict of recognised settings, so nothing downstream needs to know the file format.",
            ),
            homework=(
                "Write `load_config(text)` that parses an in-memory JSON string and returns only the keys `input`, "
                "`output` and `limit`. Call it on a document with an extra unknown key, print the resulting dict and "
                "the ignored key, and comment why the rest of the program never needs to know it came from JSON."
            ),
            patterns=["def ", "json.loads", "print("],
            mapping=(
                "`tomllib` produces the same kind of dict from TOML, and `configparser` from INI; the loader is the only "
                "place that knows the format, while the settings dict is shared."
            ),
        ),
        96: dict(
            topic="Environment variables",
            idea=(
                "Environment variables are a dictionary of strings that the operating system hands to the process, and "
                "treating them as a dict is the whole trick. The name comes from convention: an app prefix such as "
                "`APP_` separates your settings from the hundreds of unrelated variables that are always present. A "
                "loader filters by that prefix, lowercases the remainder, and returns a plain dict of settings. Two "
                "habits keep this sane. First, never scan the whole environment for values that happen to look "
                "interesting; the prefix is the contract. Second, remember that the values are strings, so `\"0\"` is "
                "truthy and `\"false\"` is too; truthiness has to be parsed explicitly rather than assumed. Secrets are "
                "another reason to treat environment values carefully: they should not be printed in logs or echoed in "
                "error messages, even during debugging. In this course the environment is passed in as a dict, which is "
                "not a workaround but good design, because a function that receives its environment can be tested with "
                "any values you like. Today you write that loader and an ignore list, and print the result. Notice the "
                "same shape from the config day: one small function converts an external format into the settings dict "
                "the rest of the program already understands."
            ),
            code=(
                'def env_settings(env, prefix="APP_"):\n'
                '    settings = {}\n'
                '    for key, value in env.items():\n'
                '        if key.startswith(prefix):\n'
                '            settings[key[len(prefix):].lower()] = value\n'
                '    return settings\n'
                '\n'
                'env = {"APP_INPUT": "inbox", "APP_DRY_RUN": "1", "PATH": "/usr/bin"}\n'
                'settings = env_settings(env)\n'
                'print("settings:", settings)\n'
                'print("ignored:", sorted(k for k in env if not k.startswith("APP_")))\n'
                'print("dry_run is a string:", type(settings["dry_run"]).__name__)\n'
                'assert settings["input"] == "inbox"\n'
                'assert "path" not in settings\n'
                'print("environment variables are strings from a dict")'
            ),
            variant_b='use a different prefix for a second loader and show that the two settings never mix',
            variant_c='convert "1" and "0" to booleans and print both results next to the raw strings',
            mistakes=[
                "Reading every variable and guessing which ones are settings instead of filtering by prefix.",
                "Treating the string `\"false\"` as false, when any non-empty string is truthy.",
                "Printing secret values while debugging, which puts them in logs and console history.",
            ],
            q1=(
                "Why is `\"0\"` a dangerous value for a boolean environment setting?",
                "It is a non-empty string, so it is truthy; the value must be parsed explicitly into a boolean.",
            ),
            homework=(
                "Write `env_settings(env, prefix=\"APP_\")` that returns only prefixed variables as lowercase setting "
                "names. Pass a dict containing two app values and one unrelated variable, print the settings and the "
                "ignored names, and comment why the function takes the environment as an argument."
            ),
            patterns=["def ", "startswith", "print("],
            mapping=(
                "`os.environ` is the real source, and tools such as `python-dotenv` load `.env` files into it; "
                "`pydantic-settings` maps prefixed variables onto typed fields."
            ),
        ),
        97: dict(
            topic="Precedence order",
            idea=(
                "Precedence is the rule that decides which value wins when the same setting arrives from several "
                "places. The convention that works is defaults, then config file, then environment, then command-line "
                "flags, with later layers overriding earlier ones. It matches what people expect: a shared default, a "
                "project config, a machine-specific environment and finally a one-off choice typed at the terminal. "
                "Implement it as repeated dictionary updates on a copy, in that order, and the whole rule becomes four "
                "lines that cannot drift apart. Two details prevent surprises. Never mutate the defaults dict, or the "
                "next run in the same process starts from polluted values; copy first. And be explicit about `None`: an "
                "absent flag is not the same as a flag set to an empty string, so decide whether empty values override "
                "or are ignored, and apply that decision in one place. The value of writing the merge as a function is "
                "that precedence stops being folklore spread across the codebase and becomes testable data. You can pass "
                "four small dicts and assert on the winner. Today you do exactly that, with one setting that comes from "
                "each layer, so the output shows the whole chain rather than a single lucky value."
            ),
            code=(
                'def resolve(flags, env, config, defaults):\n'
                '    merged = dict(defaults)\n'
                '    merged.update(config)\n'
                '    merged.update(env)\n'
                '    merged.update(flags)\n'
                '    return merged\n'
                '\n'
                'defaults = {"input": ".", "output": "out", "limit": "10"}\n'
                'config = {"input": "reports", "limit": "5"}\n'
                'env = {"output": "env-out"}\n'
                'flags = {"limit": "20"}\n'
                'final = resolve(flags, env, config, defaults)\n'
                'print("final:", final)\n'
                'print("input from config:", final["input"])\n'
                'print("output from env:", final["output"])\n'
                'print("limit from flag:", final["limit"])\n'
                'assert final == {"input": "reports", "output": "env-out", "limit": "20"}\n'
                'assert defaults["input"] == "."\n'
                'print("later layers win and the defaults stay untouched")'
            ),
            variant_b='pass an empty flags dict and confirm the environment value wins over the config value',
            variant_c='make an empty-string flag value override the lower layers and comment whether that is desirable',
            mistakes=[
                "Updating the defaults dict in place, so a later run silently inherits earlier overrides.",
                "Applying the layers in the wrong order, letting a config file beat an explicit flag.",
                "Spreading precedence logic across several functions, where the order is easy to get inconsistent.",
            ],
            q1=(
                "Why should command-line flags be merged last?",
                "The most explicit, local choice should win, so a one-off override works without editing shared configuration.",
            ),
            homework=(
                "Write `resolve(flags, env, config, defaults)` that merges the four layers in precedence order without "
                "mutating any of them. Give each layer one value, print the final dict, and comment which line proves a "
                "flag beats an environment value."
            ),
            patterns=["def ", "update", "print("],
            mapping=(
                "`argparse` defaults are the last layer, `click` supports `envvar=` for the environment layer and "
                "`default_map` for config, and `typer` exposes the same precedence to the caller."
            ),
        ),
        98: dict(
            topic="Validating settings",
            idea=(
                "Validation is the part of the argument layer that turns user input into trustworthy settings. It has "
                "two duties: convert text into the type the program needs, and report every problem it can find before "
                "any work starts. Coercion and checking are easier to reason about as separate steps. Coerce first, and "
                "record a clear failure when conversion is impossible instead of letting a `ValueError` escape from deep "
                "inside the run. Then validate the coerced values against the rules: required fields are present, "
                "numbers are in range, choices are among the allowed ones. Collect problems in a list rather than raising "
                "on the first one, because a user who mistyped two flags deserves to see both. The list is also easy to "
                "assert on in a test, which is the practical reason this style is worth adopting. Finally, validation "
                "should not silently repair values it dislikes. Clamping a negative limit to one, or inventing an input "
                "folder, hides the mistake and makes the eventual wrong result look correct. Report, then exit with a "
                "non-zero code and let the caller decide. Today you coerce a limit, collect problems for two bad "
                "settings, and confirm a good settings dict produces an empty list."
            ),
            code=(
                'def coerce(settings):\n'
                '    out = dict(settings)\n'
                '    try:\n'
                '        out["limit"] = int(out.get("limit", "10"))\n'
                '    except (TypeError, ValueError):\n'
                '        out["limit"] = None\n'
                '    return out\n'
                '\n'
                'def validate(settings):\n'
                '    problems = []\n'
                '    if not settings.get("input"):\n'
                '        problems.append("input is required")\n'
                '    if settings.get("limit") is None:\n'
                '        problems.append("limit must be an integer")\n'
                '    elif settings["limit"] < 1:\n'
                '        problems.append("limit must be positive")\n'
                '    return problems\n'
                '\n'
                'good = coerce({"input": "inbox", "limit": "3"})\n'
                'bad = coerce({"input": "", "limit": "many"})\n'
                'print("good:", good, validate(good))\n'
                'print("bad:", bad, validate(bad))\n'
                'assert validate(good) == []\n'
                'assert len(validate(bad)) == 2\n'
                'print("bad input is reported, not repaired")'
            ),
            variant_b='add an allowed-levels check that reports a value outside a small set of names',
            variant_c='coerce a boolean-like env string and report the value that could not be understood',
            mistakes=[
                "Letting conversion errors escape from deep inside the run instead of reporting them up front.",
                "Raising on the first problem, so the user fixes one flag and immediately hits the next.",
                "Silently clamping or defaulting bad values, which makes a wrong run look successful.",
            ],
            q1=(
                "Why collect validation problems in a list instead of raising on the first one?",
                "The user sees every mistake in one pass, and the list is trivial to assert on in a test.",
            ),
            homework=(
                "Write `validate(settings)` that returns a list of problems for a missing input, a non-positive limit "
                "and an invalid level. Call it on one good and one bad dict, print both lists, and comment why "
                "validation should collect every problem instead of raising on the first one."
            ),
            patterns=["def ", "append", "print("],
            mapping=(
                "`argparse` uses `type=` and `choices=` for coercion and constraints, while `click` calls it a callback "
                "or a custom type; both still produce a message rather than a traceback."
            ),
        ),
        99: dict(
            topic="Help text as data",
            idea=(
                "Help text is data before it is prose. A list of option records, each with a name and a sentence, is "
                "enough to generate a usage line, a padded option table and later a manual page. Treating it that way "
                "has three benefits. The help stays in sync with the options because they come from the same table, the "
                "formatting is a small function rather than hand-aligned spaces, and a test can assert on the generated "
                "lines without capturing a terminal. The alignment rule is simple: find the longest option name, pad "
                "every name to that width, then add two spaces and the description. Every line starts to line up, and "
                "adding a longer option does not break the rest. Content matters as much as layout. A useful help line "
                "says what the option does and what the default is, in the user's vocabulary rather than the variable "
                "name. It should also show the program name in the usage line, because people copy that line. What help "
                "text should not be is a wall of text written once and never updated; generated help is cheap to keep "
                "accurate. Today you build the table and the formatter, print the result, and assert on the first and "
                "last lines. No terminal width detection, no locale, no clever wrapping."
            ),
            code=(
                'OPTIONS = [\n'
                '    ("-i, --input", "folder to read"),\n'
                '    ("-o, --output", "folder to write (default: out)"),\n'
                '    ("--dry-run", "print the plan without doing work"),\n'
                ']\n'
                '\n'
                'def help_lines(program, options):\n'
                '    width = max(len(name) for name, _ in options)\n'
                '    lines = ["usage: " + program + " [options]"]\n'
                '    for name, text in options:\n'
                '        lines.append("  " + name.ljust(width) + "  " + text)\n'
                '    return lines\n'
                '\n'
                'lines = help_lines("report.py", OPTIONS)\n'
                'for line in lines:\n'
                '    print(line)\n'
                'assert lines[0] == "usage: report.py [options]"\n'
                'assert len(lines) == 4\n'
                'print("help is generated from the same table as the options")'
            ),
            variant_b='add a longer "--output-format" option and confirm every description still starts in one column',
            variant_c='generate the table from a dict of options and assert that the insertion order is preserved',
            mistakes=[
                "Hand-aligning spaces in a string literal, which breaks as soon as a longer option is added.",
                "Writing help text separately from the options, so the two drift out of sync.",
                "Omitting the default value, so users have to guess what happens when they omit the flag.",
            ],
            q1=(
                "Why generate help lines from an options table instead of writing them by hand?",
                "The generated lines cannot drift out of sync with the options, and alignment updates automatically when names change.",
            ),
            homework=(
                "Write `help_lines(program, options)` that builds a usage line and a padded table from a list of "
                "`(name, description)` pairs. Call it with three options, print each line, and comment which expression "
                "keeps the descriptions aligned when a longer option is added."
            ),
            patterns=["def ", "ljust", "print("],
            mapping=(
                "`argparse` generates `--help` from each option's `help=` and `metavar`, and `click` does the same from "
                "decorator arguments; both are data-driven formatters."
            ),
        ),
        100: dict(
            topic="Subcommands",
            idea=(
                "Subcommands turn one script into a family of verbs: `add`, `list`, `remove`, each with its own "
                "arguments and its own work. The structure that keeps this clean is a dispatch table mapping a command "
                "name to a function, plus one routing step that looks up the first token and calls the matching "
                "function with the rest. That is the same idea as a dictionary of callables from an earlier phase, "
                "applied to the entry point. Two rules make the dispatch honest. An unknown or missing command should "
                "return a clear error listing the valid choices, not raise a `KeyError` that leaks the implementation. "
                "And each handler should receive only its own arguments, so a parser for one command cannot accidentally "
                "depend on another's flags. Keeping the handlers small also means each one can be tested directly, "
                "without going through the router. As the family grows, the table grows by one line per command, which "
                "is the sign that the design is still working. Today you build two handlers, a router and an error path, "
                "then print the result of each call. Notice that nothing here parses flags yet; command routing and flag "
                "parsing are separate layers that compose, and separating them now will keep the follow-on phases "
                "readable."
            ),
            code=(
                'def cmd_add(args):\n'
                '    return {"command": "add", "total": sum(int(a) for a in args)}\n'
                '\n'
                'def cmd_list(args):\n'
                '    return {"command": "list", "count": len(args)}\n'
                '\n'
                'COMMANDS = {"add": cmd_add, "list": cmd_list}\n'
                '\n'
                'def dispatch(args):\n'
                '    if not args or args[0] not in COMMANDS:\n'
                '        return {"error": "unknown command", "choices": sorted(COMMANDS)}\n'
                '    return COMMANDS[args[0]](args[1:])\n'
                '\n'
                'print(dispatch(["add", "1", "2", "3"]))\n'
                'print(dispatch(["list", "a", "b"]))\n'
                'print(dispatch(["remove"]))\n'
                'assert dispatch(["add", "2", "3"])["total"] == 5\n'
                'assert "error" in dispatch([])\n'
                'print("routing is a table lookup, not a pile of if statements")'
            ),
            variant_b='add a third "count" command that shares the list handler and confirm the table stays readable',
            variant_c='return an error for an empty argument list and print the valid choices in sorted order',
            mistakes=[
                "Writing one long if/elif chain instead of a table, so adding a command means editing the router.",
                "Letting an unknown command raise a KeyError instead of returning a useful error.",
                "Passing the whole argument list to every handler, so handlers silently depend on each other's flags.",
            ],
            q1=(
                "Why route subcommands through a dictionary of functions?",
                "Adding a command becomes one table entry, and the router stays a small, uniform lookup instead of a growing if chain.",
            ),
            homework=(
                "Write `dispatch(args, commands)` that calls the handler named by the first token with the remaining "
                "tokens, and returns an error dict for an unknown or missing command. Register two handlers, call it "
                "three times including a bad command, print the results, and comment why the router stays separate from "
                "flag parsing."
            ),
            patterns=["def ", "return", "print("],
            mapping=(
                "`argparse` supports subparsers, and `click` and `typer` build command groups from the same dispatch "
                "idea; the table behind them is exactly what you wrote."
            ),
        ),
        101: dict(
            topic="Dry-run and verbose flags",
            idea=(
                "Dry-run and verbose are small flags with outsized value, because they change how a script behaves "
                "without changing what it is supposed to do. A dry run replaces the action with a description of the "
                "action: the same plan, the same order, no side effects. That requires the code to separate planning "
                "from execution, which is a good structure regardless of the flag. If the actions are computed first as "
                "a list of strings or records, then the dry run is just a different loop over the same list, and the "
                "output is exactly what a real run would do. Verbose is the other axis: it adds detail to the report "
                "without changing the work, so an operator can see what happened and why. Keeping the two independent is "
                "worth the effort; a common bug is making verbose imply dry-run or letting a print statement sit inside "
                "the work loop where it cannot be suppressed. A useful convention is that the plan is always available, "
                "the run reports one line per action, and verbose adds a summary. Today you implement both flags over an "
                "in-memory action list and assert that the dry run produces no `did` lines. No files, no shell, just the "
                "shape of the behaviour."
            ),
            code=(
                'def execute(actions, dry_run=False, verbose=False):\n'
                '    log = []\n'
                '    for action in actions:\n'
                '        if dry_run:\n'
                '            log.append("would " + action)\n'
                '        else:\n'
                '            log.append("did " + action)\n'
                '    if verbose:\n'
                '        log.append("total actions: " + str(len(actions)))\n'
                '    return log\n'
                '\n'
                'print("dry run:")\n'
                'for line in execute(["copy a", "copy b"], dry_run=True):\n'
                '    print(" ", line)\n'
                'print("verbose run:")\n'
                'for line in execute(["copy a"], verbose=True):\n'
                '    print(" ", line)\n'
                '\n'
                'assert execute(["x"], dry_run=True) == ["would x"]\n'
                'assert execute(["x"], verbose=True) == ["did x", "total actions: 1"]\n'
                'print("the plan and the report are separate from the work")'
            ),
            variant_b='combine both flags in one call and confirm the dry run still adds the verbose count',
            variant_c='return the planned actions separately so a caller can print them even on a real run',
            mistakes=[
                "Printing inside the work loop, where the output cannot be silenced on a dry run.",
                "Making verbose imply dry-run, so asking for detail accidentally prevents the real work.",
                "Building actions lazily during execution, so there is no plan to preview before side effects.",
            ],
            q1=(
                "What structure makes a trustworthy dry run possible?",
                "Compute the full list of actions first, then either describe them or perform them in a separate loop.",
            ),
            homework=(
                "Write `run(actions, dry_run=False, verbose=False)` that returns one line per action, prefixes them "
                "with `would` on a dry run, and appends a count only when verbose. Call it three ways on the same "
                "list, print each result, and comment which line keeps planning separate from execution."
            ),
            patterns=["def ", "dry_run", "print("],
            mapping=(
                "`argparse` adds these as `store_true` flags, and `click` as `is_flag=True`; production tools such as "
                "`rsync --dry-run` and `apt-get -s` follow the same plan-then-act split."
            ),
        ),
        102: dict(
            topic="Logging options",
            idea=(
                "Logging flags look trivial until a script has to run unattended, at which point the level decides "
                "whether anyone can diagnose a failure later. The useful model is a small table mapping level names to "
                "numbers, and a filter that keeps messages at or above the chosen floor. Debug is the noisiest, warning "
                "the quietest, and choosing a level should never change the order of messages. Two principles keep logs "
                "useful. Every line should carry its level, so a reader can scan for warnings, and every line should say "
                "what happened with enough context to act, rather than just `error` or a bare exception string. The "
                "other principle is that logs go to the right stream in a real program: normal output to stdout, "
                "diagnostics to stderr. Here the lines are collected in a list so the lesson stays deterministic, but "
                "the shape is the same one the standard `logging` module produces. Also watch the default. A script that "
                "defaults to debug floods a scheduler's mailbox, while one that defaults to warning hides the "
                "information you need when something goes wrong; info is usually the sane middle. Today you filter "
                "messages by level, format each line and count how many a stricter level would hide."
            ),
            code=(
                'LEVELS = {"debug": 10, "info": 20, "warning": 30}\n'
                'MESSAGES = [\n'
                '    ("debug", "loaded 3 rows"),\n'
                '    ("info", "starting"),\n'
                '    ("warning", "output exists"),\n'
                ']\n'
                '\n'
                'def log_lines(messages, level):\n'
                '    floor = LEVELS[level]\n'
                '    return [name.upper().ljust(7) + text for name, text in messages if LEVELS[name] >= floor]\n'
                '\n'
                'for line in log_lines(MESSAGES, "info"):\n'
                '    print(line)\n'
                'print("debug count:", len(log_lines(MESSAGES, "debug")))\n'
                'print("warning count:", len(log_lines(MESSAGES, "warning")))\n'
                '\n'
                'assert len(log_lines(MESSAGES, "warning")) == 1\n'
                'assert log_lines(MESSAGES, "info")[0].endswith("starting")\n'
                'print("the level filters lines without reordering them")'
            ),
            variant_b='add an "error" level above warning and confirm a warning is hidden when the floor is error',
            variant_c='let the caller pass a custom level table and check that unknown level names raise a clear error',
            mistakes=[
                "Using bare print calls with no level, so a reader cannot tell a warning from routine output.",
                "Writing log text that names no item or value, leaving nothing to act on later.",
                "Defaulting to the noisiest level in a scheduled job, so real warnings disappear in the volume.",
            ],
            q1=(
                "Why should the chosen log level filter messages without changing their order?",
                "Order carries meaning in a run; filtering should only hide detail, never reorder the sequence of events.",
            ),
            homework=(
                "Write `log_lines(messages, level)` that filters `(level_name, text)` pairs at or above a numeric "
                "floor and formats each line with a padded level. Call it at info and warning on the same list, print "
                "both outputs, and comment which default level you would choose for a scheduled job."
            ),
            patterns=["def ", "LEVELS", "print("],
            mapping=(
                "The standard `logging` module uses the same numeric levels and handlers, and `--verbose`/`--quiet` "
                "flags in `click` and `typer` usually map onto them."
            ),
        ),
        103: dict(
            topic="Testing the argument layer",
            idea=(
                "The argument layer is code, so it deserves tests like any other code, and the good news is that it is "
                "the easiest part of a script to test. Every case is a list of tokens plus the expected settings, which "
                "makes a table the natural format: one row per behaviour, one loop, a pass and fail count. No "
                "subprocess, no temporary directory, no patching of `sys.argv`. Cover the cases that actually break: "
                "the empty list, a flag with a value, a flag with an empty value, an unknown flag, a value containing an "
                "equals sign, and a repeated flag where the last one should win. Decide the expected outcome for each "
                "before running, because a test written after seeing the output only confirms what the code already "
                "does. Keep the table small enough to read; a dozen rows usually beats a hundred generated ones for a "
                "layer this size. When a case fails, print the input, the expected value and the actual value together, "
                "which is all a future reader needs. Today you build that table, run it, and assert that every case "
                "passes. This habit pays off immediately in the next phases, where argument mistakes otherwise show up "
                "as confusing runtime errors far from their cause."
            ),
            code=(
                'def parse(args):\n'
                '    settings = {"input": "inbox"}\n'
                '    for token in args:\n'
                '        if token.startswith("--input="):\n'
                '            settings["input"] = token.split("=", 1)[1]\n'
                '    return settings\n'
                '\n'
                'CASES = [\n'
                '    ([], "inbox"),\n'
                '    (["--input=reports"], "reports"),\n'
                '    (["--input="], ""),\n'
                ']\n'
                '\n'
                'passed = 0\n'
                'failed = 0\n'
                'for args, expected in CASES:\n'
                '    got = parse(args)["input"]\n'
                '    if got == expected:\n'
                '        passed += 1\n'
                '    else:\n'
                '        failed += 1\n'
                '        print("FAIL", args, "expected", repr(expected), "got", repr(got))\n'
                'print("passed:", passed, "failed:", failed)\n'
                'assert passed == 3 and failed == 0'
            ),
            variant_b='add a case where the flag appears twice and define the expected winner before running',
            variant_c='add an unknown flag to the table and show the parser ignoring it, then decide if that is correct',
            mistakes=[
                "Testing only the happy path, so the empty and malformed cases stay unexercised.",
                "Launching a subprocess for each case, which makes the suite slow and environment-dependent.",
                "Writing the expected value after seeing the output, which turns the test into a rubber stamp.",
            ],
            q1=(
                "What makes the argument layer especially easy to test?",
                "It is a pure function from a token list to settings, so each case is a list plus one expected value.",
            ),
            homework=(
                "Write `check_cases(cases)` that runs a table of `(args, expected)` rows through your parser, counts "
                "passes and failures, and prints each failure with input, expected and actual. Include an empty list "
                "and an empty flag value, print the totals, and comment why the table has no subprocess calls."
            ),
            patterns=["def ", "for ", "print("],
            mapping=(
                "`argparse`, `click` and `typer` parsers all accept an explicit list of arguments, and the `CliRunner` "
                "in `click` exists for the cases that genuinely need the full app."
            ),
        ),
        104: dict(
            topic="Review: commands, arguments and config checklist",
            idea=(
                "Today is a review, and the checklist is the lesson. A command line layer is in good shape when parsing "
                "is a pure function over a token list, defaults are applied before required values are checked, "
                "precedence runs defaults then config then environment then flags, and validation returns a list of "
                "problems instead of crashing. Add to that a help table generated from the same option data, "
                "subcommands routed through a table, and flags such as dry-run, verbose and log level that change "
                "reporting rather than the core work. It also matters that none of these functions read global state: "
                "no `sys.argv`, no `os.environ`, no file open inside the logic. That one constraint makes the whole "
                "layer testable with plain values, and it is the difference between a script you can trust in a "
                "scheduler and one you can only run by hand. A practical way to close the phase is to take one function "
                "at a time and ask what its input is, what its output is, and which test would fail if the rule broke. "
                "If you can answer all three quickly, the design is sound. Today you run a small checklist over a "
                "parsed settings dict and confirm each rule holds, then carry that list into the next phase."
            ),
            code=(
                'def parse(args, defaults):\n'
                '    settings = dict(defaults)\n'
                '    for token in args:\n'
                '        if token.startswith("--") and "=" in token:\n'
                '            name, value = token[2:].split("=", 1)\n'
                '            settings[name] = value\n'
                '        elif token.startswith("--"):\n'
                '            settings[token[2:]] = True\n'
                '    return settings\n'
                '\n'
                'def validate(settings):\n'
                '    problems = []\n'
                '    for name in ("input", "output"):\n'
                '        if not settings.get(name):\n'
                '            problems.append(name + " is required")\n'
                '    return problems\n'
                '\n'
                'CHECKLIST = [\n'
                '    ("defaults applied", lambda s: s.get("output") == "out"),\n'
                '    ("flag overrides default", lambda s: s.get("input") == "inbox"),\n'
                '    ("missing settings reported", lambda s: bool(validate(s))),\n'
                ']\n'
                '\n'
                'settings = parse(["--input=inbox"], {"input": None, "output": "out"})\n'
                'for label, check in CHECKLIST:\n'
                '    print(label, "->", bool(check(settings)))\n'
                'problems = validate(parse([], {"input": None, "output": ""}))\n'
                'print("problems:", problems)\n'
                'assert len(problems) == 2\n'
                'print("checklist complete")'
            ),
            variant_b='add a precedence check to the checklist and run it against four small layer dicts',
            variant_c='add a help-generation check and confirm it fails when an option is missing its description',
            mistakes=[
                "Reading `sys.argv` directly, which breaks the purity the whole checklist depends on.",
                "Checking required values before defaults, so fields that are never missing appear as problems.",
                "Treating dry-run or verbose as part of the core work rather than as a reporting choice.",
            ],
            q1=(
                "What single constraint makes the whole argument layer easy to test?",
                "No function reads global state such as argv, environment or files; every input arrives as a plain value.",
            ),
            homework=(
                "Write `audit(settings)` that returns a dict of checklist results: defaults present, required values "
                "reported, and precedence respected. Run it on a parsed settings dict, print each check with a "
                "boolean, and comment which check would catch a function that reads `sys.argv` directly."
            ),
            patterns=["def ", "return", "print("],
            mapping=(
                "This checklist is what separates a script from a tool: `argparse`, `click`, `typer` and a config "
                "library such as `pydantic-settings` each cover part of it, but the structure is yours to keep."
            ),
        ),
    },
)
