"""Automation / Scripting phase 1, days 75-89: files, paths and folders.

Every example is stdlib-only, offline and deterministic. Paths are
`PurePosixPath` values and folders are plain dictionaries or lists, so the
lessons model file work without touching a real disk. The planning habit built
here is what the later phases extend to scheduling, backups and packaging.
"""

PHASE = ("Files, Paths and Folders", "Plan, inspect and verify file operations as data before any of them touch a real disk.", {
    75: dict(
        topic="Orientation: what automation scripts do",
        idea=(
            "An automation script is a program that performs a small, repeatable job without a person watching it. "
            "The job is usually described in three parts: read some inputs, decide what should change, then make "
            "the change. Most of the danger lives in the third part, because moving or overwriting a file is hard "
            "to undo. The professional habit is therefore to separate decision from action: first build a plain "
            "description of the work, print it, check it, and only then execute it. That description is data — "
            "names, paths, sizes, counts — and data can be tested without a disk, which keeps feedback fast and "
            "makes failures reproducible on any machine. In this phase every example "
            "models a folder as a dictionary of names to contents, so the logic is visible and runs anywhere. A "
            "script that reports what it found before changing anything is already more trustworthy than one that "
            "acts immediately. Today you map a small folder, count files by type, and print a short report. Notice "
            "that the report is produced by ordinary Python functions over plain values. That is the whole shape of "
            "file automation; the remaining days add precision to the paths, richer matching, and safe execution."
        ),
        code=(
            'folders = {\n'
            '    "inbox": ["note.txt", "data.csv", "photo.jpg"],\n'
            '    "archive": ["old.csv"],\n'
            '}\n'
            '\n'
            'def summarise(folders):\n'
            '    total = sum(len(names) for names in folders.values())\n'
            '    kinds = {}\n'
            '    for names in folders.values():\n'
            '        for name in names:\n'
            '            kind = name.rsplit(".", 1)[-1]\n'
            '            kinds[kind] = kinds.get(kind, 0) + 1\n'
            '    return total, kinds\n'
            '\n'
            'total, kinds = summarise(folders)\n'
            'print("folders:", len(folders))\n'
            'print("files:", total)\n'
            'for kind in sorted(kinds):\n'
            '    print(f"  {kind}: {kinds[kind]}")\n'
            '\n'
            'assert total == 4 and kinds["csv"] == 2\n'
            'print("report first, change later")'
        ),
        variant_b='add a folder "trash" with one file and confirm both the total and the csv count change',
        variant_c='report the largest folder by file count instead of only the total',
        mistakes=[
            "Acting on files immediately instead of printing a report of intended work first.",
            "Hard-coding folder names inside loops so the script only works on one machine.",
            "Counting by splitting on every dot, which miscounts names such as archive.tar.gz.",
        ],
        q1=(
            "Why should a file script report before it changes anything?",
            "The report exposes wrong paths and wrong counts while the cost of a mistake is still zero.",
        ),
        homework=(
            "Write `summarise(folders)` that takes a dict mapping folder names to lists of filenames and returns "
            "the total file count plus a dict of counts per extension. Print the report sorted by extension, call "
            "it on two folders, and comment which line makes the report inspectable before any change."
        ),
        patterns=["def ", ".get(", "print("],
        mapping=(
            "Real scripts usually read this report with `os.scandir` or `pathlib.Path.iterdir`; keeping the "
            "counting function separate means it can be tested on data with no files present."
        ),
    ),
    76: dict(
        topic="Paths as values with PurePath",
        idea=(
            "A path is not a string, even though it is often stored as one. Strings have no idea what a separator "
            "is, what a parent means, or how to replace an extension, so scripts that treat paths as text tend to "
            "break on a missing slash or a dot inside a filename. `pathlib` makes a path a value with methods, and "
            "`PurePosixPath` gives you those methods without asking the operating system anything. You can join "
            "with the `/` operator, ask for `.name`, `.parent`, `.parts` or `.is_absolute()`, and compare two "
            "paths as values. This matters most of all during planning, because the paths you intend to use can be built, "
            "printed and asserted on before a single file is touched. A useful discipline is to build every target "
            "path from a small, trusted set of roots plus relative parts, rather than gluing fragments together at the "
            "call site. When the shape is wrong, the printed plan shows it immediately. Today you compose paths, "
            "inspect their parts, and check absolute versus relative forms. All of it is pure computation with no "
            "I/O wait, so results are deterministic and safe. Later days reuse exactly this composition when they plan renames, "
            "archives and atomic writes."
        ),
        code=(
            'from pathlib import PurePosixPath\n'
            '\n'
            'root = PurePosixPath("/srv/reports")\n'
            'source = root / "2026" / "q1" / "sales.csv"\n'
            'target = source.parent / "archive" / source.name\n'
            '\n'
            'print("source:", source)\n'
            'print("parts:", source.parts)\n'
            'print("parent:", source.parent)\n'
            'print("target:", target)\n'
            'print("absolute:", source.is_absolute())\n'
            '\n'
            'relative = PurePosixPath("inbox") / "note.txt"\n'
            'print("relative:", relative, relative.is_absolute())\n'
            '\n'
            'assert source.name == "sales.csv"\n'
            'assert target == PurePosixPath("/srv/reports/2026/q1/archive/sales.csv")\n'
            'assert not relative.is_absolute()\n'
            'print("paths compose without string concatenation")'
        ),
        variant_b='start from a relative root such as "reports" and print the parts of the composed path',
        variant_c='build a sibling path for "summary.csv" and assert it shares the source parent',
        mistakes=[
            "Joining path fragments with `+` and forgetting the separator on some inputs.",
            "Using `os.path` string functions on values that should be pathlib paths.",
            "Assuming a path is absolute because it starts with a familiar folder name.",
        ],
        q1=(
            "Why is `PurePosixPath` useful in a lesson or test that has no disk?",
            "It provides real path arithmetic and inspection while making no filesystem calls, so results are deterministic.",
        ),
        homework=(
            "Write `build_targets(root, names)` that accepts a root as a string and a list of relative names, "
            "returns `PurePosixPath` targets, and prints each one with its parent. Assert that every target starts "
            "with the root, and comment which line keeps composition in one place."
        ),
        patterns=["from pathlib", "def ", "PurePosixPath"],
        mapping=(
            "`pathlib.Path` adds filesystem methods to the same API; code that only needs composition can use "
            "`PurePosixPath` and remain testable, then switch to `Path` at the edge where real work begins."
        ),
    ),
    77: dict(
        topic="Names, stems and suffixes",
        idea=(
            "Filenames carry structure, and most file automation is really a conversation about that structure. "
            "A path exposes `.name` for the last component, `.stem` for the name without its final suffix, "
            "`.suffix` for that suffix including the dot, and `.suffixes` for all of them. The distinction "
            "between stem and suffix is where many bugs hide. `report.tar.gz` has three suffixes in total but "
            "only `.gz` is the final suffix, so `with_suffix` would replace just that part. A name beginning "
            "with a dot, such as `.env`, is treated as having no suffix, which is usually what you want but "
            "surprises people who split on dots. Building a new name is safest when you combine the stem, your "
            "own marker, and the original suffix in that order, rather than editing the name with `replace`. "
            "That keeps dots inside the stem untouched and makes the transformation obvious in review. Today you "
            "dissect a handful of names and derive clean output names from them. Print every part, because seeing "
            "the parts is how the rules become intuitive, and printing both old and new forms side by side catches "
            "most surprises early. Rename planning later depends on getting these boundaries exactly right, "
            "especially for multi-dot and hidden names."
        ),
        code=(
            'from pathlib import PurePosixPath\n'
            '\n'
            'names = ["report.tar.gz", "sales.csv", "notes", ".env", "archive.v2.zip"]\n'
            'for name in names:\n'
            '    path = PurePosixPath(name)\n'
            '    print(f"{name:15} stem={path.stem!r:12} suffix={path.suffix!r:7} all={path.suffixes}")\n'
            '\n'
            'source = PurePosixPath("exports/sales.csv")\n'
            'renamed = source.with_name(source.stem + "_2026" + source.suffix)\n'
            'print("renamed:", renamed)\n'
            '\n'
            'assert PurePosixPath("report.tar.gz").suffix == ".gz"\n'
            'assert PurePosixPath(".env").suffix == ""\n'
            'assert renamed.name == "sales_2026.csv"\n'
            'print("derive names from parts, never by blind replacement")'
        ),
        variant_b='try "backup.2026.01.tar.gz" and print its stem, final suffix and full suffix list',
        variant_c='add the marker before the first suffix of "sales.csv" and assert the folder survives',
        mistakes=[
            "Using `replace` on the whole name, which also rewrites matching text inside the stem.",
            "Assuming `.suffix` returns every suffix when it only returns the last one.",
            "Forgetting that a dotfile such as `.env` has an empty suffix.",
        ],
        q1=(
            "What is the difference between `.stem` and `.name`?",
            "`.name` includes the final suffix while `.stem` is the name with that last suffix removed.",
        ),
        homework=(
            "Write `tagged(source, tag)` that takes a path-like string and a tag, and returns a `PurePosixPath` "
            "with the tag inserted before the final suffix. Run it on a simple name, a multi-dot name and a "
            "dotfile, print all three, and comment which part keeps the original suffix."
        ),
        patterns=["def ", ".stem", ".suffix"],
        mapping=(
            "Rename scripts in the wild routinely corrupt multi-dot names; `Path.stem`, `Path.suffix` and "
            "`Path.with_name` are the safe vocabulary that avoids those incidents."
        ),
    ),
    78: dict(
        topic="Listing a folder as data",
        idea=(
            "A folder listing is just a collection of names, and treating it as data is the difference between a "
            "script you can reason about and one that surprises you. The important realisation is that listing, "
            "filtering, sorting and grouping are pure operations once the names are in memory. Only the first "
            "step, reading the directory, needs the disk. That first step is also the one that can fail, so it "
            "belongs behind a small function with a clear contract: given a folder, return its entries. After "
            "that, everything is ordinary Python. Sorting matters because directory order is not guaranteed, and "
            "an unstable order makes reports and tests flaky. Grouping by suffix or by size turns a flat list into "
            "something a person can scan. Keep in mind that a listing usually contains both files and folders, "
            "and that names are not paths until you join them to their parent. Today you model a folder as a list "
            "of names, sort it, group it, and print a small inventory. Every assertion runs on the in-memory data, "
            "so the lesson behaves identically on every machine. Real scans replace the literal list with "
            "`iterdir` or `scandir`, and the rest of the code stays the same."
        ),
        code=(
            'from pathlib import PurePosixPath\n'
            '\n'
            'def inventory(names):\n'
            '    paths = sorted(PurePosixPath(name) for name in names)\n'
            '    groups = {}\n'
            '    for path in paths:\n'
            '        key = path.suffix or "(none)"\n'
            '        groups.setdefault(key, []).append(path.name)\n'
            '    return paths, groups\n'
            '\n'
            'paths, groups = inventory(["zeta.csv", "alpha.txt", "beta.csv", "README"])\n'
            'print("sorted:", [p.name for p in paths])\n'
            'for key in sorted(groups):\n'
            '    print(key, "->", groups[key])\n'
            '\n'
            'assert [p.name for p in paths][0] == "README"\n'
            'assert groups[".csv"] == ["beta.csv", "zeta.csv"]\n'
            'assert groups["(none)"] == ["README"]\n'
            'print("listing is data once it is in memory")'
        ),
        variant_b='add a "notes.md" file and print the group sizes instead of the names',
        variant_c='group by first letter of the stem and compare the shape with suffix grouping',
        mistakes=[
            "Relying on `os.listdir` order, which is arbitrary and makes output flaky.",
            "Mixing bare names with full paths so later joins target the wrong folder.",
            "Forgetting that a listing contains folders too, then treating every entry as a file.",
        ],
        q1=(
            "Why sort a folder listing explicitly instead of trusting the order it arrives in?",
            "Directory order is not guaranteed, so sorting makes reports stable and assertions reliable across systems.",
        ),
        homework=(
            "Write `inventory(names)` that sorts a list of names, groups them by suffix and returns both the "
            "sorted paths and the groups. Print the groups in sorted key order, run it on five names including "
            "one without a suffix, and comment which line makes the order deterministic."
        ),
        patterns=["def ", "sorted(", "print("],
        mapping=(
            "`Path.iterdir()` and `os.scandir()` supply the raw listing; sorting and grouping afterwards is "
            "normal Python and makes the scan easy to test with fixed data."
        ),
    ),
    79: dict(
        topic="Matching files with globs",
        idea=(
            "Globs are the shorthand everyone knows from a shell: `*.csv` means every name ending in `.csv`, and "
            "`report-?.txt` means one character in that position. Python exposes the same rules through `fnmatch`, "
            "which is pure string matching and therefore ideal for planning. The first thing to understand is that "
            "globs match a whole name, not a path, unless you use a recursive pattern; a pattern with a slash "
            "depends on how you split the parts yourself. The second is that matching is case-sensitive on "
            "`fnmatchcase` but may follow platform rules with `fnmatch`, so tests should use the explicit version. "
            "The third is that a broad pattern is a liability: `*` will match files you did not mean to touch, and "
            "a rename script built on `*` is how folders get scrambled, so broad patterns deserve extra suspicion. "
            "A good habit is to keep patterns in a list "
            "near the top, print which names matched, and assert the count before acting. Today you filter a list "
            "of names with several patterns and report the matches. Nothing here reads a directory; the names are "
            "the input. Later you will apply the same filters to a real listing while keeping the matching logic "
            "separate and testable."
        ),
        code=(
            'from fnmatch import fnmatchcase\n'
            '\n'
            'names = [\n'
            '    "sales_2026.csv", "sales_2025.csv", "notes.txt",\n'
            '    "report-1.txt", "report-12.txt", "IMAGE.JPG",\n'
            ']\n'
            'patterns = ["*.csv", "report-?.txt"]\n'
            '\n'
            'matches = {}\n'
            'for pattern in patterns:\n'
            '    found = [name for name in names if fnmatchcase(name, pattern)]\n'
            '    matches[pattern] = found\n'
            '    print(pattern, "->", found)\n'
            '\n'
            'assert matches["*.csv"] == ["sales_2026.csv", "sales_2025.csv"]\n'
            'assert matches["report-?.txt"] == ["report-1.txt"]\n'
            'assert "IMAGE.JPG" not in matches["*.csv"]\n'
            'print("patterns match whole names, and case matters")'
        ),
        variant_b='add the pattern "*.txt" and predict which of the report files it catches',
        variant_c='match the uppercase image with "*.jpg" and explain why the result is empty',
        mistakes=[
            "Assuming `*` crosses folder separators, so a name filter silently matches too much.",
            "Using `fnmatch` where platform case folding makes tests behave differently.",
            "Acting on a broad pattern before printing and checking the match count.",
        ],
        q1=(
            "Why prefer `fnmatchcase` over `fnmatch` when writing tests?",
            "It applies one fixed case rule on every platform, so a test does not pass or fail depending on the operating system.",
        ),
        homework=(
            "Write `select(names, patterns)` that returns a dict mapping each pattern to the names matching it "
            "with `fnmatchcase`. Include one pattern with a question mark, print every match list, and comment "
            "which line prevents case from changing the result."
        ),
        patterns=["def ", "fnmatchcase", "print("],
        mapping=(
            "`glob.glob` and `Path.glob` extend these rules to real directory scans; keeping the matcher pure "
            "means the expensive or risky part of the script stays small."
        ),
    ),
    80: dict(
        topic="Walking a tree",
        idea=(
            "A folder tree is a nested structure, and walking it means visiting every node exactly once in a "
            "predictable order. The classic bug is recursion without a base case or a loop that revisits shared "
            "state, so it helps to write the walk as a function over plain data first. Represent the tree as "
            "nested dictionaries: a value that is a dict is a folder, and a value that is a string is a file. Then "
            "the walk is a recursive function carrying the current path down and collecting file paths as it "
            "returns. Depth matters in practice: a walk can be expensive on a large tree, and a script that "
            "prints every path can produce more output than anyone will read. Summaries, filters and a maximum "
            "depth are the usual answers. It also matters that the order is deterministic; sorting keys before "
            "recursing gives the same result on every run. Today you flatten a small tree into a list of "
            "`PurePosixPath` values and print it. The same recursion underlies `os.walk`, but writing it once "
            "yourself makes the behaviour obvious and debuggable. That matters when a real walk returns a path you "
            "did not expect. After that, using the standard walker is a convenience rather than a mystery."
        ),
        code=(
            'from pathlib import PurePosixPath\n'
            '\n'
            'tree = {\n'
            '    "inbox": {"a.txt": "a", "b.csv": "b"},\n'
            '    "archive": {"2025": {"old.csv": "c"}},\n'
            '}\n'
            '\n'
            'def walk(node, prefix=PurePosixPath(".")):\n'
            '    found = []\n'
            '    for name in sorted(node):\n'
            '        path = prefix / name\n'
            '        value = node[name]\n'
            '        if isinstance(value, dict):\n'
            '            found.extend(walk(value, path))\n'
            '        else:\n'
            '            found.append(path)\n'
            '    return found\n'
            '\n'
            'files = walk(tree)\n'
            'for path in files:\n'
            '    print(path)\n'
            '\n'
            'assert len(files) == 3\n'
            'assert str(files[0]) == "archive/2025/old.csv"\n'
            'assert str(files[2]) == "inbox/b.csv"\n'
            'print("depth-first, sorted, and easy to test")'
        ),
        variant_b='add a "tmp" folder under archive and print the new flattened list in order',
        variant_c='return only files ending in .csv and assert the non-csv file is absent',
        mistakes=[
            "Mutating a shared list from recursive calls instead of returning each subtree's results.",
            "Walking in directory order, which makes the output differ between machines.",
            "Forgetting that folders and files are different node kinds and treating both as strings.",
        ],
        q1=(
            "Why sort the keys before recursing into a tree?",
            "It makes the visit order deterministic, so printed plans and assertions do not depend on insertion or directory order.",
        ),
        homework=(
            "Write `walk(node, prefix)` that recursively collects `PurePosixPath` values from nested dicts, "
            "treating dict values as folders and strings as files. Print the flattened result for a tree with two "
            "levels, assert the count, and comment which line makes the traversal deterministic."
        ),
        patterns=["def ", "isinstance(", "PurePosixPath"],
        mapping=(
            "`os.walk` yields a root plus directory and file lists; the recursive version here shows the same "
            "three pieces of state, which helps when a real walk needs filtering or depth limits."
        ),
    ),
    81: dict(
        topic="Planning renames before doing them",
        idea=(
            "A rename is a one-line operation with a two-line failure mode: the new name already exists, or two "
            "sources map to the same target. Both failures are cheap to catch in a plan and expensive to discover "
            "after half the folder has moved. The planning habit is to build pairs of old and new names in "
            "memory, then check the whole set before applying anything. Three checks cover most accidents. First, "
            "the source must exist. Second, the targets must be unique. Third, a target must not collide with an "
            "existing name that is not itself being renamed. A fourth, subtler check is that the transformation "
            "is stable: running it on an already renamed file should not rename it again, or at least should be "
            "detected. Printing the pairs makes the intent reviewable by someone who does not read Python, which "
            "is exactly the point of writing a reviewable plan in the first place. The actual rename should happen only after the plan passes, and on a "
            "real system it should copy-then-"
            "replace or use an atomic move when possible. Today you plan a folder of names, detect a collision, "
            "and print what would happen. No file is touched, so the mistake costs nothing."
        ),
        code=(
            'from pathlib import PurePosixPath\n'
            '\n'
            'names = ["IMG_001.jpg", "IMG_002.jpg", "IMG_001.jpeg"]\n'
            '\n'
            'def plan(names):\n'
            '    pairs = []\n'
            '    for name in names:\n'
            '        path = PurePosixPath(name)\n'
            '        new = path.with_name(path.stem.lower() + path.suffix.lower())\n'
            '        pairs.append((path, new))\n'
            '    return pairs\n'
            '\n'
            'pairs = plan(names)\n'
            'for old, new in pairs:\n'
            '    print(f"{old} -> {new}")\n'
            '\n'
            'targets = [new for _, new in pairs]\n'
            'collisions = sorted({str(t) for t in targets if targets.count(t) > 1})\n'
            'print("collisions:", collisions)\n'
            '\n'
            'assert not collisions\n'
            'assert pairs[0][1].name == "img_001.jpg"\n'
            'print("plan is safe, so no rename runs yet")'
        ),
        variant_b='add "IMG_002.JPG" so two sources collide, and print the collision list',
        variant_c='skip names that are already lowercase and report how many were skipped',
        mistakes=[
            "Renaming inside the loop before checking whether later targets collide.",
            "Comparing names case-sensitively when the target filesystem is case-insensitive.",
            "Building the new name by replacing text instead of recombining stem and suffix.",
        ],
        q1=(
            "Which collision must a rename plan detect even when all sources exist?",
            "Two different sources mapping to the same target, plus a target that already exists and is not being renamed.",
        ),
        homework=(
            "Write `plan_renames(names)` that lowercases every name and returns a list of old-new pairs, plus "
            "`collisions(pairs)` that returns duplicated targets. Print the pairs and the collisions for a list "
            "with one clash, and comment which line refuses to act on an unsafe plan."
        ),
        patterns=["def ", "collisions", "print("],
        mapping=(
            "`Path.rename` and `shutil.move` perform the operation; production scripts keep the pair-building "
            "and collision check separate so the dangerous call happens only after review."
        ),
    ),
    82: dict(
        topic="Moving and archiving plans",
        idea=(
            "Moving a file is a rename with a different destination folder, and archiving is moving a batch into a "
            "dated or categorised tree. The planning problem is to decide the destination for every source without "
            "touching anything. A good destination rule is a pure function of the source: the year and month from "
            "the name, a category from the suffix, or a fixed archive root. Keeping that rule pure means you can "
            "print the whole move plan and check it before running. There are two distinct operations to keep "
            "apart. A move within one filesystem is usually cheap and atomic. A move across filesystems is a copy "
            "followed by a delete, which can fail halfway and leave two copies. Archive plans should therefore say "
            "whether they assume a same-filesystem move, and a careful script verifies the copy before removing "
            "the source. Another practical detail is creating destination folders as part of the plan rather than "
            "ad hoc inside the loop, so the plan lists them explicitly. Today you derive destinations, print the "
            "move list and the folders that would be created. This is the same information a real script would "
            "log, and it is enough to catch a wrong archive root before anything moves."
        ),
        code=(
            'from pathlib import PurePosixPath\n'
            '\n'
            'sources = [\n'
            '    PurePosixPath("inbox/2026-01-sales.csv"),\n'
            '    PurePosixPath("inbox/2026-02-sales.csv"),\n'
            '    PurePosixPath("inbox/notes.txt"),\n'
            ']\n'
            'archive_root = PurePosixPath("archive")\n'
            '\n'
            'def destination(path, root):\n'
            '    parts = path.stem.split("-")\n'
            '    if len(parts) >= 2 and parts[0].isdigit():\n'
            '        return root / parts[0] / parts[1] / path.name\n'
            '    return root / "misc" / path.name\n'
            '\n'
            'plan = [(path, destination(path, archive_root)) for path in sources]\n'
            'for old, new in plan:\n'
            '    print(f"{old} -> {new}")\n'
            '\n'
            'folders = sorted({new.parent for _, new in plan})\n'
            'for folder in folders:\n'
            '    print("ensure folder:", folder)\n'
            '\n'
            'assert str(plan[0][1]) == "archive/2026/01/2026-01-sales.csv"\n'
            'assert str(plan[2][1]) == "archive/misc/notes.txt"\n'
            'print("destinations are a pure function of the source")'
        ),
        variant_b='archive by suffix instead of date and print the resulting folder set',
        variant_c='add a file with a date but no month and route it to a "partial" folder',
        mistakes=[
            "Creating destination folders inside the move loop so the plan cannot list them up front.",
            "Assuming a cross-device move is atomic when it is really copy-then-delete.",
            "Deriving the archive root from the current working directory instead of an explicit setting.",
        ],
        q1=(
            "Why should the destination rule be a pure function of the source path?",
            "The whole move plan can then be computed, printed and checked before any file is moved.",
        ),
        homework=(
            "Write `archive_plan(sources, root)` that returns old-new path pairs using year and month taken from "
            "the filename, plus a sorted list of destination folders. Print both, run it on three names including "
            "one undated file, and comment which line keeps the archive root configurable."
        ),
        patterns=["def ", "PurePosixPath", "print("],
        mapping=(
            "`shutil.move` and `Path.rename` execute the plan; real archive scripts log the same pairs and folder "
            "list so an operator can review a move before it happens."
        ),
    ),
    83: dict(
        topic="Safe overwrite and backups",
        idea=(
            "Overwriting is the most dangerous ordinary file operation, because the previous content is gone and "
            "nothing in the filename warns you. The safe pattern is to refuse to overwrite by default, and when a "
            "replacement is intended, move the old file to a backup name first. A backup name must be unique, "
            "otherwise the second backup silently destroys the first. The usual approach is to try `name.bak`, "
            "then `name.bak1`, `name.bak2` and so on until a free name is found, while holding the chosen name in "
            "the plan so a concurrent process cannot take it. That last point matters in real scripts even though "
            "it is hard to demonstrate without a filesystem; checking and then acting is a race. On a single "
            "machine with one automation it is acceptable, but the limitation should be stated rather than "
            "forgotten. A second safeguard is to compare sizes or checksums after writing, so a failed copy is not "
            "mistaken for a successful overwrite. Today you build a backup-name chooser over a set of names, print "
            "the chosen names and assert that none collide. You also print the intended write order: back up, "
            "write the new file, then confirm. That order is the part worth memorising."
        ),
        code=(
            'from pathlib import PurePosixPath\n'
            '\n'
            'existing = {"report.csv", "report.csv.bak", "report.csv.bak1"}\n'
            '\n'
            'def backup_name(path, taken):\n'
            '    candidate = PurePosixPath(path.name + ".bak")\n'
            '    counter = 1\n'
            '    while str(candidate) in taken:\n'
            '        candidate = PurePosixPath(f"{path.name}.bak{counter}")\n'
            '        counter += 1\n'
            '    return candidate\n'
            '\n'
            'target = PurePosixPath("report.csv")\n'
            'chosen = backup_name(target, existing)\n'
            'print("target:", target)\n'
            'print("backup:", chosen)\n'
            'print("order: back up, write, verify")\n'
            '\n'
            'assert str(chosen) == "report.csv.bak2"\n'
            'assert str(chosen) not in existing\n'
            'existing.add(str(chosen))\n'
            'assert str(backup_name(target, existing)) == "report.csv.bak3"\n'
            'print("backup names stay unique")'
        ),
        variant_b='start with no backup names taken and confirm the first choice is "report.csv.bak"',
        variant_c='change the target to "data.tar.gz" and print the backup name it produces',
        mistakes=[
            "Writing directly over the target with no backup, so a failed write loses the old data.",
            "Using a fixed `.bak` name, which destroys the previous backup on the next run.",
            "Checking that a backup name is free and then writing much later without rechecking.",
        ],
        q1=(
            "Why does a fixed `.bak` name fail as a backup strategy?",
            "The second run overwrites the first backup, so the oldest and often most valuable version is lost.",
        ),
        homework=(
            "Write `backup_name(path, taken)` that returns the first free `.bak`, `.bak1`, `.bak2` name as a "
            "`PurePosixPath`, and print the chosen name for two targets against a set of taken names. Assert the "
            "result is not in the set, and comment which line makes repeated runs safe."
        ),
        patterns=["def ", "while ", ".bak"],
        mapping=(
            "`os.replace` is atomic within a filesystem, and `shutil.copy2` preserves metadata; pairing either with "
            "a unique backup name is what keeps an overwrite recoverable."
        ),
    ),
    84: dict(
        topic="Reading text safely",
        idea=(
            "Reading text sounds trivial until a file is missing, empty, enormous or not actually text. Safe "
            "reading means deciding up front what should happen in each of those cases, and keeping the parsing "
            "separate from the retrieval. A small helper can return a result that distinguishes three outcomes: "
            "the content, an empty file, and a missing file. Using a mapping with `.get` and a sentinel makes the "
            "missing case explicit instead of hiding it behind a default that looks like real content. Once the "
            "text is in hand, normalise it before parsing: strip a trailing newline, split on lines, and skip "
            "blank lines if they carry no meaning. Be careful with `splitlines`, which handles several line-ending "
            "conventions and is usually what you want for text. Another practical concern is size. Reading a "
            "multi-gigabyte log into memory will fail, so a real script should check the size or stream the file. "
            "Today you read from an in-memory mapping of names to contents, handle a missing key, and parse a small "
            "CSV-like text. The lesson is that the caller gets a clear outcome and never has to guess whether an "
            "empty string meant an empty file, a missing file or a genuine failure, which is a distinction real "
            "batch scripts depend on."
        ),
        code=(
            'files = {\n'
            '    "sales.csv": "region,amount\\nnorth,10\\nsouth,20\\n",\n'
            '    "empty.txt": "",\n'
            '}\n'
            '\n'
            'MISSING = object()\n'
            '\n'
            'def read_text(files, name):\n'
            '    raw = files.get(name, MISSING)\n'
            '    if raw is MISSING:\n'
            '        return "missing", []\n'
            '    lines = [line for line in raw.splitlines() if line.strip()]\n'
            '    if not lines:\n'
            '        return "empty", []\n'
            '    return "ok", lines\n'
            '\n'
            'for name in ["sales.csv", "empty.txt", "nope.csv"]:\n'
            '    status, lines = read_text(files, name)\n'
            '    print(f"{name:10} {status:8} lines={len(lines)}")\n'
            '\n'
            'status, lines = read_text(files, "sales.csv")\n'
            'rows = [line.split(",") for line in lines[1:]]\n'
            'print("rows:", rows)\n'
            '\n'
            'assert status == "ok" and rows[0] == ["north", "10"]\n'
            'assert read_text(files, "nope.csv")[0] == "missing"\n'
            'print("missing, empty and present are distinct outcomes")'
        ),
        variant_b='add a file containing only blank lines and confirm it is reported as empty',
        variant_c='parse a text whose last line lacks a newline and confirm it still appears',
        mistakes=[
            "Returning an empty string for both a missing file and an empty one.",
            "Leaving the trailing newline on the last line, which pollutes the final field.",
            "Reading an unbounded file into memory without checking its size first.",
        ],
        q1=(
            "Why distinguish a missing file from an empty file?",
            "They call for different handling: a missing file may be an error, while an empty file may be a valid but quiet input.",
        ),
        homework=(
            "Write `read_text(files, name)` that returns a status plus a list of non-blank lines, using a "
            "sentinel to detect a missing key. Print the outcome for a normal file, an empty one and an absent "
            "one, and comment which line keeps missing distinct from empty."
        ),
        patterns=["def ", "splitlines", "print("],
        mapping=(
            "`Path.read_text` is the real retrieval step; wrapping it in a helper that reports missing and empty "
            "separately keeps parsing code free of exception handling."
        ),
    ),
    85: dict(
        topic="Writing text atomically",
        idea=(
            "A direct write truncates the target before the new content is complete, so a crash or a full disk "
            "leaves a half-written file and destroys the old version. The standard fix is to write a temporary "
            "file in the same folder, flush and close it, then replace the target in one atomic step. Same folder "
            "matters because an atomic replace only works within one filesystem. On POSIX, `os.replace` gives that "
            "guarantee; a rename across devices does not. A careful implementation also cleans up the temporary "
            "file when the write fails, and checks the result before declaring success. The mental model is a "
            "two-phase commit: prepare the complete new value, then publish it with a single name change. Tests "
            "usually model this with a dictionary of names to contents and a `replace` helper, which makes the "
            "order visible and lets a deliberately failing write show that the old content survives. Today you "
            "simulate that store, write to a temporary name, swap it in, and demonstrate a failed write leaving "
            "the original untouched. The example prints the store after each stage so the two phases are obvious. "
            "This is the pattern to use for reports, state files and anything a later run depends on."
        ),
        code=(
            'store = {"report.txt": "old content"}\n'
            '\n'
            'def write_atomic(store, name, text, fail=False):\n'
            '    temp = name + ".tmp"\n'
            '    store[temp] = text\n'
            '    if fail:\n'
            '        del store[temp]\n'
            '        return "aborted"\n'
            '    store[name] = store.pop(temp)\n'
            '    return "written"\n'
            '\n'
            'print("before:", store)\n'
            'print(write_atomic(store, "report.txt", "first draft", fail=True))\n'
            'print("after failure:", store)\n'
            'print(write_atomic(store, "report.txt", "final content"))\n'
            'print("after success:", store)\n'
            '\n'
            'assert "report.txt.tmp" not in store\n'
            'assert store["report.txt"] == "final content"\n'
            'print("publish with one replace, never a partial write")'
        ),
        variant_b='write to "notes.txt" with a failing first attempt and confirm the old notes stay',
        variant_c='add a second successful write and print how the temp key disappears each time',
        mistakes=[
            "Writing the temporary file in a different folder, so the final replace is not atomic.",
            "Deleting the old target before the new file is complete.",
            "Leaving the temporary file behind when the write fails.",
        ],
        q1=(
            "Why must the temporary file live in the same folder as the target?",
            "An atomic replace only works within one filesystem, and the same folder guarantees that.",
        ),
        homework=(
            "Write `write_atomic(store, name, text, fail=False)` that stages content under a `.tmp` key and then "
            "publishes it, returning a status. Demonstrate one failed and one successful write on a dict, print "
            "the store each time, and comment which line performs the publish."
        ),
        patterns=["def ", ".tmp", "print("],
        mapping=(
            "`tempfile.NamedTemporaryFile` plus `os.replace` is the production version; the invariant is the "
            "same, complete the new content before changing the old name."
        ),
    ),
    86: dict(
        topic="Encoding and newlines",
        idea=(
            "Text is bytes plus an encoding, and the moment a script ignores that distinction it becomes "
            "fragile. UTF-8 is the sane default, but files arrive in other encodings, and a decode error can stop "
            "a batch halfway through. The safe habit is to name the encoding explicitly at every boundary rather "
            "than relying on the platform default, which differs between systems. Newlines are the other invisible "
            "variable: Windows uses carriage return plus line feed, Unix uses line feed, and Python's text mode "
            "normalises them unless told otherwise. If a script compares file contents byte for byte, newline "
            "normalisation can make two different files look equal or two equivalent files look different. The "
            "defensive approach is to normalise newlines to a single form as soon as text is read, and to write a "
            "single form explicitly. Another common trap is counting characters when the real constraint is bytes, "
            "which matters for database columns and message limits. Today you encode and decode a small string, "
            "normalise mixed line endings, and print the byte length alongside the character length. Seeing both "
            "numbers side by side makes the difference concrete. Later, when a report looks corrupted, you will "
            "know to ask which encoding and which newline convention produced it."
        ),
        code=(
            'text = "caf\\u00e9\\r\\nsecond line\\r\\n"\n'
            'data = text.encode("utf-8")\n'
            'decoded = data.decode("utf-8")\n'
            '\n'
            'normalised = decoded.replace("\\r\\n", "\\n").replace("\\r", "\\n")\n'
            'print("chars:", len(normalised))\n'
            'print("bytes:", len(normalised.encode("utf-8")))\n'
            'print("repr:", repr(normalised))\n'
            '\n'
            'lines = normalised.splitlines()\n'
            'print("lines:", lines)\n'
            '\n'
            'latin = "caf\\u00e9".encode("latin-1")\n'
            'print("latin bytes:", latin)\n'
            'assert latin.decode("utf-8", errors="replace") != "caf\\u00e9"\n'
            'assert data.decode("utf-8").replace("\\r\\n", "\\n") == normalised\n'
            'print("encoding and newlines are explicit choices")'
        ),
        variant_b='normalise a text that already uses only "\\n" and confirm nothing changes',
        variant_c='print the byte length of an emoji string and compare it with its character count',
        mistakes=[
            "Relying on the platform default encoding instead of naming UTF-8 explicitly.",
            "Comparing decoded text without normalising carriage returns from other systems.",
            "Assuming one character is one byte when checking a size limit.",
        ],
        q1=(
            "Why normalise newlines before comparing two text files?",
            "The same logical lines can use different line endings, so normalising avoids false differences and false matches.",
        ),
        homework=(
            "Write `normalise(text)` that converts carriage-return line endings to `\\n`, and `byte_report(text)` "
            "that returns character and UTF-8 byte counts. Run both on a string containing `\\r\\n`, print the "
            "repr and counts, and comment which line names the encoding explicitly."
        ),
        patterns=["def ", "encode", "\\r\\n"],
        mapping=(
            "`open(path, encoding=\"utf-8\")` and `Path.read_text(encoding=\"utf-8\")` are where real scripts "
            "state this choice; newline handling then stays predictable across platforms."
        ),
    ),
    87: dict(
        topic="Comparing before and after",
        idea=(
            "After a batch of file work, the useful question is not 'did the script run' but 'what actually "
            "changed'. A before-and-after comparison answers that precisely, and it is cheap when both states are "
            "plain mappings of names to contents. Comparing three things covers the useful cases: names that "
            "appeared, names that disappeared, and names whose content changed. A name that is present in both "
            "with identical content is unchanged and usually does not need to be printed, unless the report is an "
            "audit and completeness matters. The comparison should be explicit about what counts as equality. For "
            "text, normalising line endings first avoids reporting a change that is only a platform difference. "
            "For large files, hashing is cheaper than holding both contents, though it trades a little certainty "
            "for speed. In tests a snapshot comparison is the simplest regression check: run the operation on a "
            "fixed input, then assert the exact diff. Today you compare two dictionaries of file contents and "
            "print added, removed and changed names. The output is sorted so it is stable, and a stable report can "
            "be stored and compared between runs. This is the same evidence a reviewer wants after an automation "
            "touches a folder."
        ),
        code=(
            'before = {\n'
            '    "a.txt": "one",\n'
            '    "b.txt": "two",\n'
            '    "c.txt": "three",\n'
            '}\n'
            'after = {\n'
            '    "a.txt": "one",\n'
            '    "b.txt": "TWO",\n'
            '    "d.txt": "four",\n'
            '}\n'
            '\n'
            'def compare(before, after):\n'
            '    added = sorted(set(after) - set(before))\n'
            '    removed = sorted(set(before) - set(after))\n'
            '    changed = sorted(k for k in before if k in after and before[k] != after[k])\n'
            '    return {"added": added, "removed": removed, "changed": changed}\n'
            '\n'
            'diff = compare(before, after)\n'
            'for kind in ("added", "removed", "changed"):\n'
            '    print(kind + ":", diff[kind])\n'
            '\n'
            'assert diff == {"added": ["d.txt"], "removed": ["c.txt"], "changed": ["b.txt"]}\n'
            'assert compare(before, before) == {"added": [], "removed": [], "changed": []}\n'
            'print("the diff is the evidence that the batch worked")'
        ),
        variant_b='make "d.txt" identical to "a.txt" and confirm no additions are reported for it',
        variant_c='add a changed file whose content differs only by "\\r\\n" and discuss normalising first',
        mistakes=[
            "Comparing only file names, so a changed content is reported as unchanged.",
            "Printing differences in set order, which makes the report unstable between runs.",
            "Counting temporary files created during the write as real additions.",
        ],
        q1=(
            "Which three categories are enough to describe a before-and-after folder diff?",
            "Added names, removed names and names present in both whose content changed.",
        ),
        homework=(
            "Write `compare(before, after)` that returns sorted added, removed and changed names from two dicts "
            "of file contents. Run it on a small before and after, print all three lists, and comment which line "
            "keeps the report deterministic."
        ),
        patterns=["def ", "sorted(", "set("],
        mapping=(
            "`filecmp` and `hashlib` support the same comparison on real files; reporting the diff is what turns "
            "a script run into auditable evidence."
        ),
    ),
    88: dict(
        topic="Dry runs for file work",
        idea=(
            "A dry run executes everything except the operation that changes the world, and prints what would "
            "have happened. It is the single most valuable feature of a file automation, because it turns a risky "
            "batch into a reviewable plan. The clean way to implement it is a single flag that gates the commit "
            "step, not a scattered set of `if dry_run` checks around every line. Build the plan, run all the "
            "checks, and route the final mutation through one function that either applies it or records it. When "
            "the flag is on, the output should be identical in shape to a real run, so the two can be compared. "
            "That is what makes a dry run trustworthy: the code path is the same up to the last moment. A second "
            "habit is to keep a counter of planned, applied and skipped actions and print it at the end. If the "
            "numbers do not match your expectation, stop. Finally, a dry run should not create folders, lock "
            "files or write logs that imply work happened. Today you build a small executor that takes a list of "
            "actions and a flag, prints each decision, and reports the counts. The action itself is just a string, "
            "so the whole thing is deterministic and easy to assert."
        ),
        code=(
            'actions = ["mkdir archive/2026", "move inbox/a.csv", "move inbox/b.csv"]\n'
            '\n'
            'def execute(actions, dry_run):\n'
            '    applied = []\n'
            '    planned = []\n'
            '    for action in actions:\n'
            '        planned.append(action)\n'
            '        if dry_run:\n'
            '            print("would:", action)\n'
            '            continue\n'
            '        applied.append(action)\n'
            '        print("did:", action)\n'
            '    return planned, applied\n'
            '\n'
            'planned, applied = execute(actions, dry_run=True)\n'
            'print("planned:", len(planned), "applied:", len(applied))\n'
            'planned, applied = execute(actions, dry_run=False)\n'
            'print("planned:", len(planned), "applied:", len(applied))\n'
            '\n'
            'assert len(planned) == 3 and len(applied) == 3\n'
            'assert execute(actions, True)[1] == []\n'
            'print("one flag gates the commit step")'
        ),
        variant_b='pass a single action with the dry-run flag on and confirm the applied list stays empty',
        variant_c='skip actions that start with "move" in a real run and report them as skipped',
        mistakes=[
            "Scattering dry-run checks through the logic instead of gating one commit step.",
            "Creating destination folders during a dry run, so the run is not actually dry.",
            "Printing different messages in dry and real mode, which makes comparison hard.",
        ],
        q1=(
            "What should a dry run change, and what should it leave identical?",
            "It changes only the final commit, while planning, checks and output shape stay the same as a real run.",
        ),
        homework=(
            "Write `execute(actions, dry_run)` that prints each action as planned or applied and returns both "
            "lists. Call it once with the flag on and once off over three actions, print both counts, and comment "
            "which line is the single gate on real work."
        ),
        patterns=["def ", "dry_run", "print("],
        mapping=(
            "`rsync --dry-run` and `git clean -n` are mature examples; the same idea scales to any script that "
            "separates planning from a single commit step."
        ),
    ),
    89: dict(
        topic="Review: files, paths and folders checklist",
        idea=(
            "The end of a phase is a good moment to turn habits into a checklist, because checklists survive when "
            "memory does not. For file work the list is short but each item has earned its place. Are paths built "
            "with pathlib rather than string concatenation? Is every intended target printed before it is "
            "touched? Are rename targets unique and non-colliding? Does an overwrite create a unique backup first? "
            "Is text read and written with an explicit encoding? Is a new file published with an atomic replace? "
            "Does the script report a before-and-after diff? Can the whole thing run as a dry run? A checklist is "
            "not bureaucracy if it maps to real incidents; each of these items corresponds to a way data gets "
            "lost. The useful exercise is to apply the checklist to a concrete plan and see which items pass. "
            "Today you run a small plan through four checks and print a pass line for each. The checks are plain "
            "functions over the plan, so they are testable and can be reused. Treat the output as a template: a "
            "real script can log the same lines, and a reviewer can see at a glance whether the risky parts were "
            "handled. The next phase builds on this base with scheduling and larger jobs."
        ),
        code=(
            'from pathlib import PurePosixPath\n'
            '\n'
            'plan = {\n'
            '    "sources": [PurePosixPath("inbox/a.csv"), PurePosixPath("inbox/b.csv")],\n'
            '    "targets": [PurePosixPath("archive/a.csv"), PurePosixPath("archive/b.csv")],\n'
            '    "encoding": "utf-8",\n'
            '    "atomic": True,\n'
            '    "dry_run": True,\n'
            '}\n'
            '\n'
            'def check(plan):\n'
            '    results = []\n'
            '    results.append(("paths are path objects", all(isinstance(p, PurePosixPath) for p in plan["sources"] + plan["targets"])))\n'
            '    results.append(("targets are unique", len(set(plan["targets"])) == len(plan["targets"])))\n'
            '    results.append(("encoding is explicit", plan["encoding"] == "utf-8"))\n'
            '    results.append(("publish is atomic", plan["atomic"] is True))\n'
            '    results.append(("dry run available", plan["dry_run"] is True))\n'
            '    return results\n'
            '\n'
            'for label, passed in check(plan):\n'
            '    print(("PASS" if passed else "FAIL"), label)\n'
            '\n'
            'assert all(passed for _, passed in check(plan))\n'
            'print("checklist complete: safe to run for real")'
        ),
        variant_b='add a duplicated target and confirm exactly one checklist line fails',
        variant_c='set dry_run to False and explain why the checklist still passes but review matters',
        mistakes=[
            "Treating the checklist as paperwork instead of gating the run on it.",
            "Checking only happy paths and never testing a collision or missing file.",
            "Letting a failed check print FAIL and still proceeding to the commit step.",
        ],
        q1=(
            "What should happen when one checklist item fails?",
            "The run should stop before the commit step, because a failed safety check means the plan is not ready to apply.",
        ),
        homework=(
            "Write `check(plan)` returning labelled boolean results for path types, unique targets, explicit "
            "encoding and atomic publishing. Print PASS or FAIL for each label, run it on a good plan and a plan "
            "with duplicate targets, and comment which line stops an unsafe run."
        ),
        patterns=["def ", "PASS", "print("],
        mapping=(
            "Production runbooks use the same checks around `pathlib`, `shutil` and `os.replace` calls; logging "
            "each result is what makes an unattended job reviewable."
        ),
    ),
})
