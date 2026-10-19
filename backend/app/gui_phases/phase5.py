"""GUI Applications phase 5, days 135-149: packaging, theming and polish.

Same discipline as the foundations: stdlib-only, offline, deterministic and
headless. Nothing here opens a window, runs a build tool or touches the disk.
Themes are token dicts, shortcuts are key-to-action maps, translations are
dictionaries keyed by strings, and a release is a manifest you can print and
check before a single installer is produced.
"""

PHASE = (
    "Packaging, Theming and Polish",
    "Turn a working desktop script into a themed, accessible, packaged app with a calm first run and honest error states.",
    {
        135: dict(
            topic="Orientation: shipping a desktop app",
            idea=(
                "Shipping is a separate skill from building, and it starts with an honest inventory. A program "
                "that only runs on your machine because a path happens to exist or a package happens to be "
                "installed is not yet an app; it is a rehearsal. The mature move is to describe the release as "
                "data before you touch a build tool: a name, a version, an entry point, the assets that travel "
                "with it, and the licence you promise. Once that list is a dictionary, you can check it, print "
                "it and diff two releases without opening a terminal in the right directory. This framing also "
                "exposes the gaps early. The field you left blank is the reason the installer fails on a clean "
                "machine, and a missing asset is the reason the icon vanishes on someone else's desktop. Today "
                "you build that manifest and report which required fields do not resolve. The checklist is "
                "deliberately plain, but it is the same shape every packaging tool consumes: a declared set of "
                "inputs and outputs. Carry it forward, and each later day in this phase fills in one part of "
                "the list with real behaviour rather than a guess. A manifest is the contract you can hold yourself to."
            ),
            code=(
                'REQUIRED = ["name", "version", "entry", "icons", "license"]\n'
                '\n'
                'def manifest(**fields):\n'
                '    return {key: fields.get(key, "") for key in REQUIRED}\n'
                '\n'
                'release = manifest(name="Notes", version="1.2.0",\n'
                '                   entry="notes/__main__.py", icons="icons/")\n'
                'missing = [key for key, value in release.items() if not value]\n'
                'print("release:", release["name"], release["version"])\n'
                'print("entry:", release["entry"])\n'
                'print("missing fields:", missing)\n'
                'assert missing == ["license"]\n'
                'print("a release is complete only when every required field resolves")'
            ),
            variant_b='fill in a licence value and re-check that the missing list becomes empty',
            variant_c='print each required field on its own line as "field = value" and flag the empty ones',
            mistakes=[
                "Treating a successful run on your own machine as proof the app is shippable.",
                "Forgetting the entry point, so the packaged build has nothing to launch.",
                "Leaving required fields blank and discovering the gap only on a clean install.",
            ],
            q1=(
                "Why describe the release as a manifest before running any build tool?",
                "So the inputs and outputs are inspectable data you can check and diff, and gaps surface before the build rather than after.",
            ),
            homework=(
                "Write `check_release(fields)` that takes a dictionary, fills missing required keys with empty "
                "strings, prints each field and whether it resolves, and returns the list of blank field names. "
                "Run it on one complete and one incomplete release, print both lists, and comment which line "
                "detects the blanks."
            ),
            patterns=["def ", "for ", "print("],
            mapping=(
                "PyInstaller specs, setuptools metadata and Debian control files are all this manifest in "
                "different syntaxes; the required-field idea is identical."
            ),
        ),
        136: dict(
            topic="Themes and style tokens",
            idea=(
                "A theme is not a list of colours sprinkled through the code; it is a dictionary of named tokens "
                "that widgets ask for by role. The moment a button says `bg=accent` instead of `bg=#3366cc`, "
                "switching to a dark theme is a data change rather than a hunt. This is the same idea as CSS "
                "custom properties or a design system's palette, and it pays off twice: consistency, because "
                "every control draws from one source, and testability, because you can assert that a token "
                "exists without rendering anything. The trap is letting a widget keep a private override that no "
                "theme can reach, which is how an app ends up mostly dark with one stubborn white panel. The "
                "discipline is to resolve styles through a single function that merges layered token dicts in a "
                "defined order: base theme, then user preference, then a local override. Order is the whole "
                "contract. Today you build two themes and a resolver, print the resolved style for a few widget "
                "kinds, and confirm that an override wins only where it is meant to. That single resolver is what "
                "makes high-contrast and light modes cheap later. A single resolver is the only place a theme rule is allowed to live."
            ),
            code=(
                'LIGHT = {"bg": "#ffffff", "fg": "#111111", "accent": "#3366cc", "pad": 8}\n'
                'DARK = {"bg": "#111111", "fg": "#eeeeee", "accent": "#6699ff", "pad": 8}\n'
                '\n'
                'def resolve(theme, overrides):\n'
                '    return {**theme, **overrides}\n'
                '\n'
                'def style_for(theme, kind, **overrides):\n'
                '    tokens = resolve(theme, overrides)\n'
                '    return f"{kind}: bg={tokens[\'bg\']} fg={tokens[\'fg\']} pad={tokens[\'pad\']}"\n'
                '\n'
                'print(style_for(LIGHT, "button"))\n'
                'print(style_for(DARK, "button"))\n'
                'print(style_for(DARK, "label", pad=4))\n'
                'assert resolve(LIGHT, {"pad": 12})["pad"] == 12\n'
                'print("themes are token dicts; widgets never hard-code colours")'
            ),
            variant_b='add a HIGH_CONTRAST theme with black and yellow tokens and resolve a button from it',
            variant_c='make resolve raise on an unknown token key and show it refusing a typo like "colour"',
            mistakes=[
                "Hard-coding colour values inside widgets so a theme change misses some of them.",
                "Layering overrides in an undefined order, so the last merge silently wins.",
                "Letting a widget hold a private style that no theme can ever reach.",
            ],
            q1=(
                "Why do widgets ask for tokens like accent rather than literal colour values?",
                "So a theme change is a data edit rather than a code hunt, and every control stays consistent from one source.",
            ),
            homework=(
                "Write `theme_style(theme, kind, **overrides)` that merges the theme dict with the overrides and "
                "returns a formatted string of the resolved tokens. Define two themes, resolve the same widget "
                "kind under each, print both, and comment which line makes the override win."
            ),
            patterns=["def ", "**", "print("],
            mapping=(
                "Tkinter's `ttk.Style`, Qt stylesheets and QPalette all resolve named tokens per widget role; "
                "the merge order is what makes theming predictable."
            ),
        ),
        137: dict(
            topic="Reusable widget components",
            idea=(
                "A reusable component is a small function that produces a configured widget with sensible "
                "defaults, so the rest of the app asks for a labelled field rather than assembling one from "
                "scratch each time. The value is not brevity alone; it is that the default lives in exactly one "
                "place, so changing the padding or the validation hint updates every instance. Think of it as the "
                "difference between copy-pasting a form field and calling a constructor. Building components as "
                "functions over plain data also keeps them testable: you can inspect the produced dictionary "
                "without a display and assert that a required field carries its flag. The common failure is a "
                "component with too many parameters, which is really two components wearing one name; when a "
                "factory grows a mode switch, split it. The other failure is the opposite: no defaults, so every "
                "call site repeats the same six arguments and drifts. Today you write a component factory and "
                "compose a short form from it, then pull the required fields back out. You are practising the "
                "move that turns a one-off screen into a library of parts you can reuse in the next view without "
                "retyping the rules. Reuse is the point, and defaults are how reuse stays honest."
            ),
            code=(
                'def component(kind, **props):\n'
                '    base = {"kind": kind, "enabled": True, "visible": True}\n'
                '    base.update(props)\n'
                '    return base\n'
                '\n'
                'def field(label, name, required=False):\n'
                '    return component("entry", label=label, name=name, required=required)\n'
                '\n'
                'form = [field("Email", "email", required=True), field("Nickname", "nick")]\n'
                'for widget in form:\n'
                '    flag = "required" if widget["required"] else "optional"\n'
                '    print(widget["label"], "->", widget["name"], f"({flag})")\n'
                'required = [w["name"] for w in form if w["required"]]\n'
                'print("required fields:", required)\n'
                'assert "email" in required and "nick" not in required\n'
                'print("a component is a function that fills in sensible defaults")'
            ),
            variant_b='add a password field variant that sets a "mask" property and print the form again',
            variant_c='give component a "disabled" flag and list only the widgets that are enabled',
            mistakes=[
                "Copy-pasting a widget definition so the shared default drifts between screens.",
                "Growing one factory a mode switch until it is really two components in a trench coat.",
                "Giving no defaults, so every call site repeats the same arguments and diverges.",
            ],
            q1=(
                "What is the main benefit of building a widget through a component function?",
                "Its defaults live in one place, so behaviour changes and reuse happen by editing a single definition.",
            ),
            homework=(
                "Write `make_field(label, name, required=False, mask=None)` that returns a configured widget "
                "dictionary, then build a form of three fields from it. Print each field, collect the required "
                "names, and comment which line keeps the default in one place."
            ),
            patterns=["def ", "return", "print("],
            mapping=(
                "Qt custom widgets, Tkinter subclasses and React components are all this factory idea with more "
                "machinery for lifetimes and events."
            ),
        ),
        138: dict(
            topic="Icons and assets",
            idea=(
                "Assets are the files a program needs at runtime that are not code: icons, fonts, images, cursor "
                "sets and sounds. In development they often sit next to the source and load by a relative path, "
                "which is exactly why they disappear after packaging. The disciplined approach is a registry: one "
                "place that names each asset, records its size, and answers lookups by name. Then a missing icon "
                "becomes a defined fallback rather than a crash, and a scaling decision is arithmetic instead of "
                "guesswork. Two habits follow. First, never build a path from string concatenation at the call "
                "site; ask the registry, because that is the one function you update when the layout changes. "
                "Second, treat a missing asset as a visible state, not a silent one, so a placeholder appears "
                "where the real art should be and someone notices. Today you model a registry, resolve icons at "
                "one and two times scale, and print what happens for a name that was never registered. The point "
                "is that asset handling is data plus a lookup, and the packaging lesson later simply ships that "
                "lookup's inputs alongside the code. A registry also shows, at a glance, everything the build must carry."
            ),
            code=(
                'ASSETS = {\n'
                '    "save": {"file": "save.png", "size": (16, 16)},\n'
                '    "open": {"file": "open.png", "size": (16, 16)},\n'
                '    "logo": {"file": "logo.png", "size": (64, 64)},\n'
                '}\n'
                '\n'
                'def icon(name, scale=1):\n'
                '    asset = ASSETS.get(name)\n'
                '    if asset is None:\n'
                '        return f"{name}: missing (using placeholder)"\n'
                '    width, height = asset["size"]\n'
                '    return f"{name}: {asset[\'file\']} at {width * scale}x{height * scale}"\n'
                '\n'
                'for name in ["save", "logo", "print"]:\n'
                '    print(icon(name, scale=2))\n'
                'print("registered assets:", sorted(ASSETS))\n'
                'assert icon("print").startswith("print: missing")\n'
                'print("name every asset once so missing art is a lookup, not a crash")'
            ),
            variant_b='add a "retina" scale of 3 and show the logo resolving at that size',
            variant_c='return a dict of resolved files from a list of requests and report the missing ones',
            mistakes=[
                "Building asset paths by concatenation at each call site instead of asking one registry.",
                "Assuming an icon file is present, so a missing image crashes the window at startup.",
                "Ignoring display scale, so icons are blurry on high-resolution screens.",
            ],
            q1=(
                "Why route every asset request through a single registry?",
                "So lookups, fallbacks and scaling are defined once, and a missing file becomes a known state rather than a crash.",
            ),
            homework=(
                "Write `resolve_icons(requests)` that takes a list of asset names and returns a mapping from name "
                "to either its file and scaled size or a placeholder string. Include one unregistered name, print "
                "the mapping, and comment which line produces the fallback."
            ),
            patterns=["def ", "get(", "print("],
            mapping=(
                "Qt resource files, PyInstaller `--add-data` and Tkinter `PhotoImage` all solve the same problem: "
                "finding named files after the code has moved into a bundle."
            ),
        ),
        139: dict(
            topic="Keyboard shortcuts and accelerators",
            idea=(
                "Keyboard shortcuts are a mapping from a normalised key combination to an action name, and almost "
                "every shortcut bug comes from skipping the normalisation. On one platform the same chord reports "
                "as Control, on another as Ctrl; a user may hold shift or not; the case of a letter is irrelevant "
                "to intent. If you collapse each combination into one canonical form before looking it up, the "
                "table has a single key per action and cannot silently shadow itself. The action name, not the "
                "callback, belongs in the table: it keeps the map data and lets a menu item, a toolbar button and "
                "a key event all dispatch to the same handler. It also makes conflicts visible, because two "
                "different combos mapping to one action, or one combo mapped twice, is exactly the kind of thing "
                "you can assert in a test. Today you build the map, normalise a few ways a user might press the "
                "same chord, and report which presses are unbound. Good shortcut hygiene is boring: a canonical "
                "form, a single owner per action, and a clear report when nothing matches. That same table drives "
                "the menus and the help screen, so it is worth getting right once."
            ),
            code=(
                'SHORTCUTS = {"ctrl+s": "save", "ctrl+z": "undo", "f1": "help"}\n'
                '\n'
                'def normalize(combo):\n'
                '    parts = [part.strip().lower() for part in combo.split("+")]\n'
                '    return "+".join(sorted(parts))\n'
                '\n'
                'LOOKUP = {normalize(key): action for key, action in SHORTCUTS.items()}\n'
                '\n'
                'def action_for(combo):\n'
                '    return LOOKUP.get(normalize(combo), "unbound")\n'
                '\n'
                'for pressed in ["Ctrl+S", "ctrl+z", "Shift+Ctrl+S", "F1"]:\n'
                '    print(pressed, "->", action_for(pressed))\n'
                'print("unbound presses:", [p for p in ["Ctrl+S", "Ctrl+P"] if action_for(p) == "unbound"])\n'
                'assert action_for("CTRL+S") == "save"\n'
                'print("shortcuts are a key-to-action map with one normal form")'
            ),
            variant_b='add a "Ctrl+Shift+S" entry for save-as and show it resolving separately from save',
            variant_c='list two combos mapped to the same action and print them as a duplicate report',
            mistakes=[
                "Comparing raw key strings, so Ctrl+S and ctrl+s are treated as different shortcuts.",
                "Storing callbacks in the map instead of action names, so no menu can reuse the binding.",
                "Binding the same combination twice and letting the later registration silently shadow the first.",
            ],
            q1=(
                "Why normalise a key combination before looking it up?",
                "Different platforms and modifier orders spell the same chord differently, so one canonical form keeps the map unambiguous.",
            ),
            homework=(
                "Write `bindings(pairs)` that takes a list of (combo, action) pairs, normalises each combo, and "
                "returns a mapping plus a list of any action bound more than once. Print the map and the duplicate "
                "list, and comment which line folds the combos to one form."
            ),
            patterns=["def ", "lower(", "print("],
            mapping=(
                "Qt `QKeySequence`, Tkinter `bind` on `<Control-s>` and GTK accelerators all normalise and route "
                "keys to named commands this way."
            ),
        ),
        140: dict(
            topic="Accessibility basics",
            idea=(
                "Accessibility is not a feature you add at the end; it is a property of every control from the "
                "start, and the cheapest part of it is naming. A screen reader announces a control by its "
                "accessible name, which comes from a visible label, a title, or a fallback derived from an icon. "
                "If that name is empty, the control is invisible to anyone not looking at the pixels, no matter "
                "how well it is drawn. Getting the basics right means three habits: give every interactive widget "
                "a name, keep the keyboard focus order equal to the visual order, and never encode meaning in "
                "colour alone, because a red outline means nothing to a colour-blind user. The good news is that "
                "these are checkable properties of your widget data, so you can test them headlessly. You can walk "
                "a list of controls and report the ones with no name before anyone opens the app. That is exactly "
                "the audit a reviewer would run by hand, except it is instant and repeatable. Today you compute an "
                "accessible name from a few fallbacks and list the controls that still come up empty. The habit to "
                "keep is that an unlabelled control is a bug, as real as a crash but quieter."
            ),
            code=(
                'def accessible_name(widget):\n'
                '    name = widget.get("label") or widget.get("title") or ""\n'
                '    if not name and widget.get("icon"):\n'
                '        name = widget["icon"] + " button"\n'
                '    return name.strip()\n'
                '\n'
                'widgets = [\n'
                '    {"kind": "button", "label": "Save"},\n'
                '    {"kind": "button", "icon": "trash"},\n'
                '    {"kind": "entry", "label": ""},\n'
                ']\n'
                'for widget in widgets:\n'
                '    name = accessible_name(widget)\n'
                '    status = "ok" if name else "NO NAME"\n'
                '    print(widget["kind"], "->", repr(name), status)\n'
                'unlabelled = [w for w in widgets if not accessible_name(w)]\n'
                'print("unlabelled controls:", len(unlabelled))\n'
                'assert len(unlabelled) == 1\n'
                'print("every control needs a name a screen reader can read")'
            ),
            variant_b='add a "title" fallback for windows and a "tooltip" field and show both being used',
            variant_c='write `audit(widgets)` returning all unlabelled controls and assert the count by kind',
            mistakes=[
                "Leaving an icon-only button with no accessible name, so a screen reader calls it empty.",
                "Setting the keyboard focus order by pixel position, which rarely matches the visual reading order.",
                "Conveying state with colour alone, which vanishes for colour-blind users.",
            ],
            q1=(
                "Why is an icon-only button without a label an accessibility bug?",
                "Its accessible name is empty, so a screen reader announces nothing useful and the control is unusable without sight.",
            ),
            homework=(
                "Write `audit(widgets)` that returns a list of controls whose accessible name is empty, deriving "
                "the name from label, title or icon. Feed it at least three controls including one unlabelled, "
                "print the offenders, and comment which fallback saves the icon-only button."
            ),
            patterns=["def ", "for ", "print("],
            mapping=(
                "Qt's `setAccessibleName`, Tkinter's label association and platform screen readers all depend on "
                "this one computed name being present."
            ),
        ),
        141: dict(
            topic="Internationalisation and text keys",
            idea=(
                "Internationalisation begins the day you stop writing user-visible sentences directly into the "
                "code. A string literal in a label is a message with exactly one language, and translating it "
                "later means hunting every literal across the project. The alternative is a message catalogue: a "
                "dictionary per language, keyed by a stable identifier, with placeholders for the values that "
                "change. Then a label asks for the key `greeting` and receives whatever the active language "
                "provides. Two details make this survive contact with reality. First, every lookup needs a "
                "fallback, because a catalogue will always lag the code, and a missing key must show the English "
                "default rather than the raw key or a crash. Second, text that changes length should flow through "
                "placeholders, since word order differs between languages and concatenation bakes in one grammar. "
                "Today you build two small catalogues, resolve the same key in each, and deliberately ask for a "
                "key that only exists in one language to watch the fallback work. The thinking transfers far "
                "beyond desktop apps: any interface with text in it needs a keyed catalogue and a defined "
                "fallback before the second language arrives. Keys also survive copy edits, because the message text can change without touching code."
            ),
            code=(
                'CATALOGUE = {\n'
                '    "en": {"greeting": "Hello, {name}", "items": "{count} items"},\n'
                '    "fr": {"greeting": "Bonjour, {name}", "items": "{count} elements"},\n'
                '}\n'
                '\n'
                'def tr(lang, key, **params):\n'
                '    table = CATALOGUE.get(lang, CATALOGUE["en"])\n'
                '    template = table.get(key, CATALOGUE["en"].get(key, key))\n'
                '    return template.format(**params)\n'
                '\n'
                'print(tr("en", "greeting", name="Ada"))\n'
                'print(tr("fr", "greeting", name="Ada"))\n'
                'print(tr("de", "items", count=3))\n'
                'print(tr("fr", "unknown_key"))\n'
                'assert tr("fr", "items", count=0).startswith("0")\n'
                'print("translation is a lookup by key with a safe fallback")'
            ),
            variant_b='add a Spanish catalogue for the greeting and show it resolving alongside English',
            variant_c='make tr list which keys each language is missing from the English baseline',
            mistakes=[
                "Writing user-visible sentences as literals, so translating means editing code everywhere.",
                "Concatenating fragments to build a sentence, which bakes in the word order of one language.",
                "Crashing or showing a raw key when a catalogue is missing an entry instead of falling back.",
            ],
            q1=(
                "Why does every translation lookup need a fallback?",
                "Catalogues lag the code, so a missing key must show a sensible default rather than a raw identifier or an error.",
            ),
            homework=(
                "Write `translate(catalogue, lang, key, **params)` that falls back to the English entry and then "
                "to the key itself, and `missing_keys(catalogue)` listing keys a language lacks. Build a small "
                "catalogue, print several lookups, and comment which line provides the fallback."
            ),
            patterns=["def ", "get(", "print("],
            mapping=(
                "Qt's `tr()` and `.ts` files, GNU gettext and Fluent all implement this keyed catalogue with a "
                "neutral fallback language."
            ),
        ),
        142: dict(
            topic="Packaging with PyInstaller",
            idea=(
                "A packaging tool is not magic; it reads a description of your app and produces a bundle. "
                "PyInstaller in particular consumes a set of flags, an entry script and a list of data files, "
                "and its output is only as good as those inputs. The reliable way to work with any such tool is "
                "to build the argument list as data first, inspect it, and only then run it. That single habit "
                "saves hours, because the flag you mistyped is visible in the printed list rather than buried in "
                "a shell history. It also clarifies the two decisions that dominate packaging. One-file versus "
                "one-directory trades startup time against tidiness: a single file is easy to hand around but "
                "unpacks itself on every launch, while a directory starts faster and looks messier. Windowed "
                "versus console decides whether a terminal flashes behind the app. Both are just booleans in your "
                "spec, so the choice is explicit instead of accidental. Today you write a function that turns a "
                "small specification dictionary into the exact command list, including the data files that must "
                "travel with the code. You never run the tool; you produce the arguments a real run would use and "
                "assert they say what you meant, which is the testable half of packaging."
            ),
            code=(
                'def pyinstaller_args(spec):\n'
                '    args = ["pyinstaller", "--name", spec["name"]]\n'
                '    args.append("--onefile" if spec["onefile"] else "--onedir")\n'
                '    if spec["windowed"]:\n'
                '        args.append("--windowed")\n'
                '    for data in spec.get("datas", []):\n'
                '        args += ["--add-data", data]\n'
                '    args.append(spec["entry"])\n'
                '    return args\n'
                '\n'
                'spec = {"name": "Notes", "entry": "notes/__main__.py",\n'
                '        "onefile": True, "windowed": True, "datas": ["icons:icons"]}\n'
                'cmd = pyinstaller_args(spec)\n'
                'print(" ".join(cmd))\n'
                'print("data files:", len(spec["datas"]))\n'
                'assert "--onefile" in cmd and cmd[-1] == spec["entry"]\n'
                'print("a build is a list of arguments you can inspect before running")'
            ),
            variant_b='switch the spec to onedir and console mode and print the changed command',
            variant_c='validate the spec first and report a missing entry or name before building the args',
            mistakes=[
                "Forgetting to include data files, so icons and fonts are absent from the bundle.",
                "Shipping a windowed build that still needs console output for errors the user never sees.",
                "Editing build flags by hand each release instead of generating them from one spec.",
            ],
            q1=(
                "Why build the packaging command as a data list before running the tool?",
                "The arguments become inspectable and testable, so a wrong flag is caught before anything is bundled.",
            ),
            homework=(
                "Write `build_args(spec)` that returns the full argument list for a spec with name, entry, mode "
                "and data files, and `check_spec(spec)` that returns missing required keys. Print the command for "
                "one spec, print the check result, and comment which line adds a data file."
            ),
            patterns=["def ", "append", "print("],
            mapping=(
                "PyInstaller, cx_Freeze and Briefcase all take a declared spec; generating that spec as data is "
                "what makes releases reproducible by machine."
            ),
        ),
        143: dict(
            topic="Installers and updates",
            idea=(
                "An installer does two jobs: it puts the files somewhere durable and it tells the operating "
                "system how to launch and uninstall the app. An updater is a different animal, and it is mostly a "
                "version comparison with a download attached. Separating the two is what keeps release logic "
                "honest, because the update question reduces to one operation: is the latest version greater than "
                "the one installed? That comparison is not string equality. `1.10.0` is newer than `1.9.0`, yet as "
                "plain text it sorts earlier, which is the classic bug where an update never appears. The "
                "defensible approach is to parse versions into tuples of integers and compare those, so ordering "
                "is numeric per component. Everything else around an updater, the download, the checksum, the "
                "prompt, the restart, is machinery you can add once the comparison is correct. Today you write "
                "that comparer and run it over a few pairs, including the one that fools string sorting, and "
                "report how many updates are pending. The lesson is steady: the risky part of an update system is "
                "usually an unnoticed comparison, not the network code. Install and update are separate journeys, and only one of them compares versions."
            ),
            code=(
                'def parse(version):\n'
                '    return tuple(int(part) for part in version.split("."))\n'
                '\n'
                'def needs_update(current, latest):\n'
                '    return parse(latest) > parse(current)\n'
                '\n'
                'pairs = [("1.2.0", "1.2.1"), ("1.9.0", "1.10.0"), ("2.0.0", "1.9.9"), ("1.0.0", "1.0.0")]\n'
                'for current, latest in pairs:\n'
                '    print(current, "->", latest, "update:", needs_update(current, latest))\n'
                'pending = [pair for pair in pairs if needs_update(*pair)]\n'
                'print("updates available:", len(pending))\n'
                'assert needs_update("1.9.0", "1.10.0") and not needs_update("2.0.0", "1.9.9")\n'
                'print("an update check is a numeric version comparison, not text")'
            ),
            variant_b='add a "channel" field (stable, beta) and only update stable installs from stable releases',
            variant_c='return which component changed between two versions instead of a single boolean',
            mistakes=[
                "Comparing versions as strings, so 1.10.0 is judged older than 1.9.0.",
                "Bundling install and update logic together so neither can be tested in isolation.",
                "Updating without checking the installed version, so an older release overwrites a newer one.",
            ],
            q1=(
                "Why is plain string comparison wrong for version numbers?",
                "Text ordering compares character by character, so 1.10.0 sorts before 1.9.0 even though it is the newer release.",
            ),
            homework=(
                "Write `compare_versions(current, latest)` that parses dotted versions into integer tuples and "
                "returns -1, 0 or 1, plus `needs_update` built on it. Test several pairs including 1.9.0 against "
                "1.10.0, print the results, and comment which line performs the numeric comparison."
            ),
            patterns=["def ", "int(", "print("],
            mapping=(
                "Sparkle on macOS, WinSparkle and MSIX updaters are all a version comparison plus a signed "
                "download; the comparison is the part that silently breaks."
            ),
        ),
        144: dict(
            topic="Logging and crash reports",
            idea=(
                "Logging exists so you can reconstruct what happened without a debugger attached, and a crash "
                "report is just the tail of a log plus the state that surrounded the failure. The mistake is "
                "treating logging as scattered print statements. A useful log has a level, a stable message and "
                "structured fields, so it can be filtered and grepped months later. Levels are the contract: "
                "debug for development detail, info for milestones a user might report, warning for something "
                "recoverable, error for a failure that needs attention. The filter, not the call site, decides "
                "what ships, which is why you write debug lines freely and raise the threshold for releases. "
                "Structured fields matter because a message that reads `save failed` is nearly useless, while "
                "`save failed (path=notes.txt)` tells you what to reproduce. The second habit is not to log "
                "secrets or whole documents; a crash report can accidentally carry a password if you dump raw "
                "state. Today you format log records with levels and ordered fields, print only those at or above "
                "info, and count the errors. Good logging is quiet in success and precise in failure. A log you would not want to read at 3am is a log that will not help you then."
            ),
            code=(
                'LEVELS = {"debug": 10, "info": 20, "warning": 30, "error": 40}\n'
                '\n'
                'def log_line(level, message, **fields):\n'
                '    extra = " ".join(f"{key}={value}" for key, value in sorted(fields.items()))\n'
                '    return f"[{level.upper()}] {message}" + (f" ({extra})" if extra else "")\n'
                '\n'
                'records = [\n'
                '    ("info", "app started", {"version": "1.2.0"}),\n'
                '    ("warning", "asset missing", {"name": "logo.png"}),\n'
                '    ("error", "save failed", {"path": "notes.txt"}),\n'
                '    ("debug", "cache warm", {}),\n'
                ']\n'
                'for level, message, fields in records:\n'
                '    if LEVELS[level] >= LEVELS["info"]:\n'
                '        print(log_line(level, message, **fields))\n'
                'errors = [r for r in records if LEVELS[r[0]] >= LEVELS["error"]]\n'
                'print("errors logged:", len(errors))\n'
                'assert len(errors) == 1\n'
                'print("levels filter what ships; the record format stays constant")'
            ),
            variant_b='raise the threshold to warning and print which records survive the filter',
            variant_c='write a crash report that appends the last two log lines and the current state summary',
            mistakes=[
                "Using print instead of levels, so there is no way to silence detail in a release build.",
                "Logging free text with no fields, making a failure impossible to grep or reproduce later.",
                "Dumping full application state into a crash report and leaking passwords or private data.",
            ],
            q1=(
                "Why separate log levels from the call sites that emit them?",
                "The filter decides what ships, so you can log freely in development and raise the threshold for a release without editing every line.",
            ),
            homework=(
                "Write `emit(records, threshold)` that formats records with levels and sorted fields and returns "
                "only those at or above the threshold, plus `dangerous(record)` flagging a suspected secret key. "
                "Print the filtered log, and comment which line applies the threshold."
            ),
            patterns=["def ", "sorted(", "print("],
            mapping=(
                "Python's `logging` module, Sentry and platform crash reporters all build on levelled, structured "
                "records; the level names here are the same contract."
            ),
        ),
        145: dict(
            topic="First-run experience",
            idea=(
                "The first run of an app is a special case, and the honest way to handle it is a single flag that "
                "remembers the ceremony is done. On first launch you might show a welcome, ask for a theme and "
                "pick a folder; on every later launch you skip all of it. Modelling that as a settings dictionary "
                "with a `seen_welcome` boolean keeps the special case from leaking into the rest of the code. The "
                "alternative, scattered checks against whether a config file exists, spreads first-run logic "
                "everywhere and makes restart behaviour hard to predict. A second principle is to make first run "
                "skippable and reversible: the user should be able to dismiss the tour and change every choice "
                "later in preferences. A third is to do as little as possible on the very first launch, because "
                "that is when the app is least understood and most likely to be judged. Today you apply a "
                "first-run routine to fresh settings and then to the already-seen settings, printing the steps "
                "each time. The second call does nothing, which is exactly the point: the ceremony runs once, "
                "records that it ran, and the code afterwards is the same as any other launch."
            ),
            code=(
                'DEFAULT_SETTINGS = {"theme": "light", "autosave": True, "seen_welcome": False}\n'
                '\n'
                'def apply_first_run(settings):\n'
                '    if settings["seen_welcome"]:\n'
                '        return settings, []\n'
                '    steps = ["welcome", "pick theme", "choose folder"]\n'
                '    return {**settings, "seen_welcome": True}, steps\n'
                '\n'
                'fresh, steps = apply_first_run(dict(DEFAULT_SETTINGS))\n'
                'print("first run steps:", steps)\n'
                'print("flag now:", fresh["seen_welcome"])\n'
                'again, steps_again = apply_first_run(fresh)\n'
                'print("second run steps:", steps_again)\n'
                'assert steps and not steps_again\n'
                'print("first-run work happens once, then a flag retires it")'
            ),
            variant_b='add a "skipped_welcome" flag so a user can dismiss the tour but still import settings later',
            variant_c='make apply_first_run also print each step as it would appear on screen with a number',
            mistakes=[
                "Checking whether a config file exists on every launch instead of reading one explicit flag.",
                "Forcing the tour on every run, so the app cannot be used until it is dismissed.",
                "Making first-run choices permanent, with no route to change them in preferences later.",
            ],
            q1=(
                "Why gate the first-run ceremony behind a single explicit flag?",
                "It confines the special case to one place and one launch, so every later run follows the ordinary path.",
            ),
            homework=(
                "Write `first_run(settings, steps)` that returns the settings with the flag set and the steps to "
                "show, or an empty list when the flag is already true. Call it twice on the same settings, print "
                "both step lists, and comment which line skips the ceremony on the second run."
            ),
            patterns=["def ", "if ", "print("],
            mapping=(
                "Qt's `QSettings`, Tkinter config files and installer wizards all record a one-time flag; the "
                "welcome tour is just the visible half of that flag."
            ),
        ),
        146: dict(
            topic="Preferences and defaults",
            idea=(
                "Preferences are where user data and application defaults meet, and the meeting needs rules. The "
                "clean model is a dictionary of defaults, and a loader that copies those defaults and then lets a "
                "saved dictionary override only the keys it knows. Unknown keys are ignored with a note rather "
                "than merged blindly, because a preference file from a newer version can carry settings this "
                "build does not understand, and silently importing them is how an app acquires phantom options. "
                "This layering also gives you a place to validate. A font size of 900 or a theme name that does "
                "not exist should be clamped to a sane range rather than trusted. The reason to be strict is "
                "simple: preferences are user input read from a file, and files get edited, truncated and copied "
                "between machines. Treating them as trusted is the same mistake as trusting a form field without "
                "validation. Today you merge a saved dictionary over defaults, ignore an unknown key, clamp a "
                "numeric range, and print the resolved preferences. The pattern is the same one every settings "
                "screen needs: defaults define the shape, saved values fill known slots, and validation guards the "
                "edges. Strictness here is cheap and prevents a whole class of confusing bug reports."
            ),
            code=(
                'DEFAULTS = {"theme": "light", "font_size": 12, "autosave": True}\n'
                'KNOWN = set(DEFAULTS)\n'
                '\n'
                'def load_prefs(saved):\n'
                '    prefs = dict(DEFAULTS)\n'
                '    for key, value in saved.items():\n'
                '        if key in KNOWN:\n'
                '            prefs[key] = value\n'
                '        else:\n'
                '            print("ignoring unknown preference:", key)\n'
                '    prefs["font_size"] = max(8, min(72, prefs["font_size"]))\n'
                '    return prefs\n'
                '\n'
                'prefs = load_prefs({"theme": "dark", "font_size": 900, "telemetry": True})\n'
                'print("resolved:", prefs)\n'
                'assert prefs["theme"] == "dark" and prefs["font_size"] == 72\n'
                'print("defaults fill the gaps; unknown keys are ignored and values clamped")'
            ),
            variant_b='add a "language" preference with a list of allowed values and fall back on an unknown one',
            variant_c='collect every ignored or clamped key into a warnings list and print it at the end',
            mistakes=[
                "Merging every saved key blindly, so preferences from a future version create phantom options.",
                "Trusting a saved font size or colour without clamping it to a valid range.",
                "Replacing the defaults dictionary in place, so the defaults are lost for the next launch.",
            ],
            q1=(
                "Why ignore unknown preference keys instead of merging them all in?",
                "A file from another version can carry settings this build does not understand, and importing them creates options that do nothing.",
            ),
            homework=(
                "Write `load_settings(defaults, saved)` that copies the defaults, overrides known keys, ignores "
                "unknown ones and clamps a numeric range, returning both the resolved settings and any warnings. "
                "Run it on a saved dict with a bad value, print the result, and comment which line clamps."
            ),
            patterns=["def ", "dict(", "print("],
            mapping=(
                "Qt's `QSettings`, Tkinter config files and macOS defaults are all this merge of defaults with "
                "saved values, plus validation the app owns."
            ),
        ),
        147: dict(
            topic="Empty, loading and error states",
            idea=(
                "Every screen has at least four states, and beginners build only the happy one. There is the "
                "loading state, before data has arrived; the empty state, when the answer is genuinely nothing "
                "rather than an error; the error state, when something failed and the user needs a way out; and "
                "the loaded state with real content. A view function that branches on these states turns each into "
                "a deliberate screen with words, instead of a blank panel that makes the user wonder whether the "
                "app is broken. The empty state is the one people forget, and it matters most on first run, "
                "because that is when there is nothing yet and the app must invite an action rather than look "
                "dead. The error state must offer a next step, usually a retry, because an error with no exit is "
                "just a wall. Order matters too: an error outranks loading, and loading outranks empty, or an "
                "in-flight request will briefly flash the empty message. Today you write that precedence "
                "explicitly, printing the screen for each condition. The habit to keep is that no condition is "
                "left undesigned, so the interface is honest about what is actually happening. Designing all four states costs little and prevents the blank-screen panic."
            ),
            code=(
                'def view(state, data=None, error=None):\n'
                '    if error:\n'
                '        return f"Error: {error} (retry)"\n'
                '    if state == "loading":\n'
                '        return "Loading..."\n'
                '    if not data:\n'
                '        return "Nothing here yet - add your first note"\n'
                '    return f"{len(data)} items"\n'
                '\n'
                'print(view("loading"))\n'
                'print(view("ready", data=[]))\n'
                'print(view("ready", data=["a", "b", "c"]))\n'
                'print(view("loading", error="disk full"))\n'
                'assert "retry" in view("ready", error="disk full")\n'
                'print("a screen is never blank: every state has words")'
            ),
            variant_b='make the empty state vary by context, so a search with no matches says "no results"',
            variant_c='return a (title, detail, action) tuple per state so a real dialog can render it',
            mistakes=[
                "Rendering a blank panel for empty data, so the user cannot tell it apart from a hang.",
                "Showing an error with no retry or escape, which leaves the user stuck.",
                "Checking loading before error, so a failed request flickers through the loading screen.",
            ],
            q1=(
                "Why must the error state take precedence over the loading state?",
                "A failed request is not still loading, and showing loading first misleads the user about what is happening.",
            ),
            homework=(
                "Write `render_state(state, data=None, error=None)` that returns a labelled message for loading, "
                "empty, error and loaded states with error checked first. Print all four outcomes, and comment "
                "which line enforces the precedence order."
            ),
            patterns=["def ", "if ", "print("],
            mapping=(
                "Any list, table or dashboard view in a desktop app needs these four branches; returning them "
                "from one pure function is what keeps the UI honest."
            ),
        ),
        148: dict(
            topic="Polish pass checklist",
            idea=(
                "Polish is not a mood; it is a checklist you can run before every release. The reason to write "
                "the checks down is that they are easy to skip under deadline and each one is cheap to verify in "
                "isolation: does the window have a title, does every button have a label, is a theme actually "
                "applied, does any shortcut point at nothing. Turning those questions into functions over the "
                "app's own data means the polish pass becomes a command rather than an afternoon of clicking. "
                "This is the same argument as a test suite: a check that has never been written is a check that "
                "will be forgotten, and the tenth release is when the untitled window ships. The discipline also "
                "forces the app to be describable as data, which is itself a design pressure toward a clean "
                "model. Today you define a small checklist of named predicates and run them all against one app "
                "description, printing pass or fail for each and collecting the failures. It will not catch "
                "everything, but it catches the boring regressions that make an otherwise finished app feel "
                "unfinished. When a new polish rule appears, it becomes one more predicate in the list."
            ),
            code=(
                'CHECKLIST = [\n'
                '    ("window has a title", lambda app: bool(app["title"])),\n'
                '    ("all buttons labelled", lambda app: all(w["label"] for w in app["widgets"] if w["kind"] == "button")),\n'
                '    ("theme applied", lambda app: bool(app["theme"])),\n'
                '    ("no unbound shortcuts", lambda app: all(app["shortcuts"].values())),\n'
                ']\n'
                '\n'
                'app = {"title": "Notes", "theme": "dark",\n'
                '       "widgets": [{"kind": "button", "label": "Save"}, {"kind": "entry", "label": ""}],\n'
                '       "shortcuts": {"Ctrl+S": "save", "Ctrl+P": None}}\n'
                '\n'
                'for name, check in CHECKLIST:\n'
                '    print("PASS" if check(app) else "FAIL", name)\n'
                'failures = [name for name, check in CHECKLIST if not check(app)]\n'
                'print("failures:", failures)\n'
                'assert "no unbound shortcuts" in failures\n'
                'print("polish is a checklist you can run, not a feeling")'
            ),
            variant_b='add a check that every window has at least one way to close and rerun the pass',
            variant_c='score the app as passed over total checks and print a percentage at the end',
            mistakes=[
                "Relying on memory to check polish, so the same small defect ships release after release.",
                "Writing checks that inspect pixels instead of the widget data, which cannot run headlessly.",
                "Adding a polish rule but never wiring it into the list that actually runs before a release.",
            ],
            q1=(
                "Why express the polish pass as functions over the app's data?",
                "Then the pass is runnable and repeatable like a test, catching boring regressions instead of depending on someone remembering.",
            ),
            homework=(
                "Write `run_checklist(app, checks)` that takes the app dictionary and a list of (name, predicate) "
                "pairs and returns the failing names. Define at least four checks, run them on one app, print each "
                "result, and comment which line collects the failures."
            ),
            patterns=["def ", "lambda", "print("],
            mapping=(
                "Pre-release audits in Qt and Tkinter projects are often literal checklists; encoding them as "
                "predicates over widget data makes them repeatable in CI."
            ),
        ),
        149: dict(
            topic="Review: packaging and polish checklist",
            idea=(
                "The last day of the phase gathers the threads: packaging, polish and the support work around "
                "them. Readiness is not one boolean; it is a checklist across sections, each with its own items, "
                "and the useful output is both a per-section score and the specific things still missing. That "
                "shape lets you answer the only question that matters at release time: what, exactly, is left. A "
                "single percentage hides the answer, so you print the missing items alongside the count. This is "
                "the same discipline as the whole phase, turned on itself. You have a manifest, themes, "
                "components, assets, shortcuts, accessible names, a catalogue, a build spec, an update check, "
                "logging, a first-run flag and states, and now you verify they are all present and wired. The "
                "review is also where you decide honestly what is out of scope, because a checklist that is never "
                "finished is not a plan. Today you model readiness as nested dictionaries, score each section and "
                "print the gaps. The habit worth keeping is that shipping is a series of small, checkable claims, "
                "and the release is simply the day they are all true. Each claim is small enough to verify, and together they mean you are done."
            ),
            code=(
                'RELEASE = {\n'
                '    "packaging": {"manifest": True, "icons": True, "installer": False},\n'
                '    "polish": {"themes": True, "shortcuts": True, "accessibility": False},\n'
                '    "support": {"logging": True, "updates": True, "first_run": True},\n'
                '}\n'
                '\n'
                'def readiness(release):\n'
                '    done = sum(1 for section in release.values() for ok in section.values() if ok)\n'
                '    total = sum(len(section) for section in release.values())\n'
                '    return done, total\n'
                '\n'
                'for section, checks in RELEASE.items():\n'
                '    missing = [key for key, ok in checks.items() if not ok]\n'
                '    print(section, f"{len(checks) - len(missing)}/{len(checks)}", "missing:", missing)\n'
                'done, total = readiness(RELEASE)\n'
                'print(f"overall {done}/{total} = {round(100 * done / total)}%")\n'
                'assert done == 7 and total == 9\n'
                'print("shipping is a checklist across packaging, polish and support")'
            ),
            variant_b='add a section with an explicit out-of-scope item and show it excluded from the score',
            variant_c='return the missing items grouped by section and print only the sections with gaps',
            mistakes=[
                "Reporting one pass or fail for the whole release, hiding which section is actually unfinished.",
                "Counting an item as done because it exists on a plan rather than because it is wired up.",
                "Treating the checklist as infinite, so no release is ever declared ready.",
            ],
            q1=(
                "Why report readiness per section with the missing items named?",
                "A single score hides the answer; naming the gaps tells you exactly what is left to finish before shipping.",
            ),
            homework=(
                "Write `readiness(release)` that returns a per-section mapping of passed, total and missing items, "
                "plus an overall fraction. Build a release with at least three sections and one gap, print the "
                "report, and comment which line groups the missing items by section."
            ),
            patterns=["def ", "for ", "print("],
            mapping=(
                "Release checklists in desktop tooling, from app-store review guides to in-house ship lists, all "
                "have this per-area scoring with named gaps."
            ),
        ),
    },
)
