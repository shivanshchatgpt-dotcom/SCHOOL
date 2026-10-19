"""Game Development phase 4, days 120-134: content, levels and data.

Fifteen hand-authored days on treating everything the engine reads as data:
level layouts, tilemap layers, procedural generation, spawn and loot tables,
schemas, balancing, dialogue, JSON serialisation, save migration, localisation
and content testing. Every worked example is stdlib-only, offline and
deterministic (fixed seeds, no clock, no disk writes), so the applier can
execute it and produce the same output on every run.
"""

class _Day(dict):
    def __lt__(self, other):
        return self["topic"] < other["topic"]


PHASE = (
    "Content, Levels and Data",
    "Model game content as plain, validatable data so levels, spawns and text can grow without touching engine code.",
    {
        120: _Day(
            topic="Orientation: content is data",
            idea=(
                "Content is everything the engine reads but does not contain: level layouts, enemy stats, item "
                "lists, dialogue and spawn tables. Hard-coding content into functions makes every new level a code "
                "change and every designer a programmer. Moving it into plain data, dictionaries and lists at "
                "first and JSON or a database later, lets the engine stay small and lets content grow without "
                "touching logic. The mental switch is to ask, every time you write a literal such as a monster's "
                "health or a room's size, whether that value is engine behaviour or game content. Behaviour "
                "belongs in code, content belongs in data. This split is what makes tooling possible: once levels "
                "are data, you can write an editor, validate a batch of them, translate the text and balance "
                "numbers without recompiling. It also makes testing easier, because a level becomes a value you "
                "can construct in a test rather than a scene you must load. Today you describe one level as a "
                "dictionary and write a tiny function that reads it, proving the engine needs no knowledge of "
                "this particular level. Keep the shape boring and explicit, because a content format people can "
                "read is a content format people can fix."
            ),
            code=r'''import json


LEVEL = {
    "name": "green_hills",
    "tiles": ["grass", "grass", "water"],
    "spawn": {"x": 2, "y": 5},
    "enemies": [{"kind": "slime", "count": 3}],
}


def summarise(level):
    total = sum(e["count"] for e in level["enemies"])
    return f"{level['name']}: {len(level['tiles'])} tiles, {total} enemies"


print(summarise(LEVEL))
print(json.dumps(LEVEL["spawn"], sort_keys=True))
assert summarise(LEVEL) == "green_hills: 3 tiles, 3 enemies"
print("the level is data the engine reads")
''',
            variant_b="add a second enemy entry and check the summary total updates without touching the function",
            variant_c="store the level as a JSON string, parse it with json.loads, and pass the result to summarise",
            mistakes=[
                "Writing enemy stats as literals inside update functions that only this level can use.",
                "Mixing engine behaviour and level content so one file must change for every new scene.",
                "Duplicating a value in several places instead of giving it one name in the data.",
            ],
            q1=(
                "Why does keeping content out of code make tools like editors possible?",
                "A tool can read and write the same data format the engine loads, without recompiling or understanding the engine's code.",
            ),
            homework=(
                "Write `summarise_level(level)` that takes a level dictionary with a name, a tiles list and an "
                "enemies list, and returns a one-line summary. Call it on two different levels, print both "
                "summaries, and comment which line reads the content as data instead of assuming it."
            ),
            patterns=["def ", "return", "print("],
            mapping=(
                "Unity's ScriptableObjects and Godot's custom .tres resources exist for exactly this reason: "
                "designers author data while programmers own the engine that reads it."
            ),
        ),
        121: _Day(
            topic="Level definitions in data",
            idea=(
                "A level definition is a contract between a designer and the engine. It says how big the level "
                "is, where the player starts, where the goal is, and what obstacles exist, using only values. "
                "Because it is data, the engine can render it, validate it and test it with the same code for "
                "every level. The most common shape is a size plus a collection of coordinates for special tiles, "
                "rather than a full grid, because sparse features like walls and chests do not need a value per "
                "cell. This keeps the file small and the intent readable: a list of walls is easier to eyeball "
                "than a wall of characters. The engine function that turns those coordinates into something "
                "visible should be pure, taking the level and returning rows of text or a grid, so the same "
                "definition can later feed a real renderer. Naming the fields now pays off later: every validator, "
                "migration and editor will use those names. Today you define one cave as a dictionary and write a "
                "function that renders it, checking a specific row so the layout is pinned down. Notice that "
                "changing the level means changing the data, and the rendering function never changes at all."
            ),
            code=r'''LEVEL = {
    "id": "cave_01",
    "size": (8, 4),
    "goal": {"x": 7, "y": 3},
    "walls": [(0, 0), (1, 0), (2, 0)],
    "start": {"x": 0, "y": 3},
}


def is_wall(level, x, y):
    return (x, y) in set(level["walls"])


def describe(level):
    w, h = level["size"]
    rows = []
    for y in range(h):
        rows.append("".join("#" if is_wall(level, x, y) else "." for x in range(w)))
    return rows


for row in describe(LEVEL):
    print(row)
assert describe(LEVEL)[0] == "###....."
print("level definition rendered from data, not code")
''',
            variant_b="add two wall coordinates and predict which rendered rows change before running it",
            variant_c="render the goal tile as 'G' and the start tile as 'S', deciding which takes priority",
            mistakes=[
                "Storing a full grid when only a few cells are special, so the file is mostly filler.",
                "Hard-coding the level size inside the render function instead of reading it from the data.",
                "Letting the same coordinate mean different things in different levels without saying so.",
            ],
            q1=(
                "Why store walls as a list of coordinates instead of a dense grid of characters?",
                "Sparse features stay small and readable, and the engine can still build a dense grid when it needs one.",
            ),
            homework=(
                "Write `render_level(level)` that takes a level dictionary with a size, a start and a goal, and "
                "returns a list of text rows marking start and goal. Render two different levels, print every row, "
                "and comment which line reads the size from the data."
            ),
            patterns=["def ", "for ", "print("],
            mapping=(
                "Tiled and LDtk both export a small header plus a list of objects; engines read that structure "
                "rather than assuming a fixed layout per scene."
            ),
        ),
        122: _Day(
            topic="Tilemaps and layers",
            idea=(
                "A tilemap is a grid of tile ids, and layers stack several grids on top of one another: ground, "
                "decoration, collision, lighting. The engine draws them in order, so the last non-empty layer at a "
                "cell wins. Layers matter because they separate concerns that would otherwise fight. The ground "
                "layer says what the floor is, the decoration layer says what sits on the floor, and the collision "
                "layer says what blocks movement. Keeping them separate means you can change the visuals without "
                "changing physics, or hide a layer without touching its data. The classic implementation is a list "
                "of equal-sized grids plus a legend mapping tile ids to characters or sprites. Rendering walks "
                "cells then layers, and collision reads only the collision layer. The subtle rule is compositing "
                "order: decide once whether the top layer overrides or blends, and keep it consistent, because "
                "overlapping decorations are exactly where sloppy order shows. Today you build two small layers "
                "and a legend, then render them together and assert a specific row. Notice the data is just "
                "numbers, and every decision about appearance lives in the legend and the draw order, not in the "
                "grid itself. The compositing rule is the whole lesson, and it belongs in the render function where "
                "it can be tested on its own."
            ),
            code=r'''GROUND = [
    [1, 1, 1, 1],
    [1, 0, 0, 1],
    [1, 1, 1, 1],
]
DECOR = [
    [0, 0, 0, 0],
    [0, 9, 0, 0],
    [0, 0, 0, 0],
]
LEGEND = {0: ".", 1: "#", 9: "*"}


def render(layers):
    height = len(layers[0])
    width = len(layers[0][0])
    rows = []
    for y in range(height):
        row = ""
        for x in range(width):
            tile = 0
            for layer in layers:
                if layer[y][x]:
                    tile = layer[y][x]
            row += LEGEND[tile]
        rows.append(row)
    return rows


for line in render([GROUND, DECOR]):
    print(line)
assert render([GROUND, DECOR])[1] == "#*.#"
print("top layer wins where it is non-zero")
''',
            variant_b="swap the layer order and predict how the decorated row changes before running it",
            variant_c="add a third collision layer drawn as 'X' and decide whether it should hide decoration",
            mistakes=[
                "Flattening all layers into one grid, so decoration and collision cannot change independently.",
                "Rendering cells in a different order than the data is authored, flipping the picture.",
                "Forgetting that a zero tile id means empty and drawing it as a real tile.",
            ],
            q1=(
                "Why keep collision on its own layer instead of sharing the ground grid?",
                "Physics then reads one clean grid and visual changes never accidentally alter what blocks movement.",
            ),
            homework=(
                "Write `stack_layers(layers)` that takes a list of equal grids and returns one grid where the last "
                "non-zero value per cell wins. Render two stacked tilemaps, print each row, and comment which loop "
                "decides the winning layer."
            ),
            patterns=["def ", "for ", "print("],
            mapping=(
                "Every 2D engine exposes tilemap layers with a draw order; the layer list is the same data, only "
                "the compositor is faster."
            ),
        ),
        123: _Day(
            topic="Procedural generation with constraints",
            idea=(
                "Procedural generation fills content from an algorithm instead of a hand-authored file, but the "
                "useful version is never pure randomness. Constraints are what make a generated level playable: a "
                "solid border so the player cannot fall out, a guaranteed path from start to goal, a minimum "
                "distance between hazards, a cap on how many enemies spawn. The generator is a function from a "
                "seed and a set of parameters to content, and the constraints are checks applied while or after "
                "building. Because the seed drives everything, a generated level is reproducible: ship the seed "
                "and the same level appears on every machine, which is why procedural games store seeds rather "
                "than layouts. The important design choice is where constraints live. If they are baked into the "
                "generator, every rule change edits the generator; if they are separate post-checks, you can test "
                "and reuse them. A practical pattern is generate first, then repair: carve the border, connect "
                "isolated rooms, then validate. Today you generate a small grid from a fixed seed, force a solid "
                "border, and prove that regenerating from the same seed reproduces the identical layout. "
                "Constraints, not randomness alone, are what make generated content usable enough to ship at scale."
            ),
            code=r'''import random


def generate(seed, width, height, fill):
    rng = random.Random(seed)
    grid = [[0] * width for _ in range(height)]
    for y in range(1, height - 1):
        for x in range(1, width - 1):
            if rng.random() < fill:
                grid[y][x] = 1
    for x in range(width):
        grid[0][x] = 1
        grid[height - 1][x] = 1
    return grid


def count_walls(grid):
    return sum(sum(row) for row in grid)


grid = generate(7, 6, 4, 0.3)
for row in grid:
    print("".join("#" if c else "." for c in row))
inner = (len(grid) - 2) * (len(grid[0]) - 2)
print("inner walls:", count_walls(grid), "of", inner, "cells")
same = generate(7, 6, 4, 0.3)
assert same == grid
print("border always solid, interior seeded")
''',
            variant_b="raise the fill probability and check whether the border stays solid whatever the seed",
            variant_c="generate three levels from three seeds and print which one has the most interior walls",
            mistakes=[
                "Generating without constraints, so some seeds produce unreachable or empty levels.",
                "Burying every rule inside the generator, so constraints cannot be tested on their own.",
                "Using an unseeded generator, so the same level cannot be reproduced for a bug report.",
            ],
            q1=(
                "Why is a procedural level stored as a seed rather than as the finished grid?",
                "The seed plus the generator reproduces the identical grid on any machine, so the save stays tiny.",
            ),
            homework=(
                "Write `generate_grid(seed, width, height)` that fills an interior from a seeded generator and "
                "always leaves a solid border. Generate two different seeds, print both grids, and comment which "
                "loop enforces the border."
            ),
            patterns=["random.Random", "def ", "print("],
            mapping=(
                "Roguelikes and Minecraft-style worlds are generated from a seed plus rules; the constraints are "
                "the difference between a level and noise."
            ),
        ),
        124: _Day(
            topic="Spawn tables and weighted picks",
            idea=(
                "A spawn table describes what can appear and how often, as a list of entries each with a weight. "
                "Picking with weights is different from picking uniformly: a weight of six against a weight of one "
                "means the first is six times as likely, which is how designers tune difficulty without touching "
                "code. The standard technique is a cumulative sum. Add the weights, draw a number from one to the "
                "total, then walk the entries subtracting until the running total covers the draw. This is exactly "
                "how a loaded die works, and it costs one pass over a short list. The subtle trap is order "
                "dependence: the same weights in a different order can change a run's outcome once rounding and "
                "fixed seeds enter the picture, so keep the table stable and test it. Because the pick consumes a "
                "seeded generator, the same seed produces the same sequence of spawns, which is what makes a wave "
                "replayable. Today you build a small weighted table, draw a hundred spawns from a fixed seed, and "
                "show that the heavy entry lands more often. Notice the numbers come from data, and the picking "
                "function is the same whatever the table contains, ready for balance passes."
            ),
            code=r'''import random

SPAWN_TABLE = [("slime", 6), ("bat", 3), ("golem", 1)]


def total_weight(table):
    return sum(weight for _, weight in table)


def pick(table, rng):
    roll = rng.randint(1, total_weight(table))
    upto = 0
    for name, weight in table:
        upto += weight
        if roll <= upto:
            return name
    raise AssertionError("unreachable")


rng = random.Random(11)
counts = {}
for _ in range(100):
    name = pick(SPAWN_TABLE, rng)
    counts[name] = counts.get(name, 0) + 1
print("spawns over 100 draws:", counts)
print("weights:", SPAWN_TABLE)
assert set(counts) <= {"slime", "bat", "golem"}
assert counts["slime"] > counts["golem"]
print("weighted picks respect the table")
''',
            variant_b="make golem twice as common and check whether the counts move toward it over 100 draws",
            variant_c="give every entry the same weight and explain why pick then becomes a uniform choice",
            mistakes=[
                "Picking uniformly when the design clearly asks for rare and common enemies.",
                "Recomputing the total weight inside the loop, which changes the distribution subtly.",
                "Letting the table order drift between runs, so a fixed seed no longer reproduces the wave.",
            ],
            q1=(
                "How does the cumulative-sum technique give each entry its intended probability?",
                "Drawing uniformly from one to the total and stopping at the entry whose running sum covers the draw gives each weight its share of outcomes.",
            ),
            homework=(
                "Write `weighted_pick(table, rng)` that takes entries of name and weight and one seeded generator, "
                "and returns a picked name. Draw fifty spawns from two seeds, print the counts, and comment which "
                "line turns the roll into a choice."
            ),
            patterns=["def ", "for ", "print("],
            mapping=(
                "Loot and spawn systems in real engines are weighted tables; the same cumulative draw sits behind "
                "a designer's rarity percentages."
            ),
        ),
        125: _Day(
            topic="Content schemas and validation",
            idea=(
                "A schema is a description of what valid content looks like: which fields must exist, what type "
                "each holds, and which values are allowed. Validation checks a piece of content against the schema "
                "and reports every problem it finds, ideally all at once rather than stopping at the first. This "
                "matters because content is authored by hand and hand-authored data has typos, missing fields and "
                "stray keys. Catching them at load time, with a clear message naming the field, is far cheaper "
                "than debugging a crash three scenes later. The first useful schema is tiny: a mapping from field "
                "name to expected type, plus a rule for missing and unknown fields. Returning a list of errors "
                "instead of raising keeps the validator composable and testable, and lets a tool show a report. "
                "The design principle is that a schema is data too, so the same validator can check enemies, "
                "items and levels if they share shapes, and a new field is a one-line change. Today you write a "
                "small schema and a validator that returns every error for a good and a bad record. Notice that "
                "one validator, driven by data, replaces a pile of ad-hoc if-statements scattered through the "
                "loader."
            ),
            code=r'''SCHEMA = {"name": str, "hp": int, "speed": float}


def validate_record(record, schema):
    errors = []
    for field, kind in schema.items():
        if field not in record:
            errors.append(f"missing {field}")
        elif not isinstance(record[field], kind):
            errors.append(f"{field} should be {kind.__name__}")
    for field in sorted(set(record) - set(schema)):
        errors.append(f"unknown {field}")
    return errors


good = {"name": "slime", "hp": 4, "speed": 1.0}
bad = {"name": "slime", "hp": "four", "colour": "green"}
print("good:", validate_record(good, SCHEMA))
print("bad:", validate_record(bad, SCHEMA))
assert validate_record(good, SCHEMA) == []
assert len(validate_record(bad, SCHEMA)) == 3
print("validation reports every problem at once")
''',
            variant_b="add an optional field to the schema and check that a record missing it is not an error",
            variant_c="validate a list of records and print how many are valid, deciding what to do with the rest",
            mistakes=[
                "Raising on the first error so the author fixes fields one run at a time.",
                "Treating booleans as ints because bool is a subclass of int without meaning to.",
                "Ignoring unknown fields, so typos like 'hpp' pass silently and read as zero.",
            ],
            q1=(
                "Why return a list of errors instead of raising an exception on the first one?",
                "The author sees every problem in one pass, and the validator stays a pure, testable function.",
            ),
            homework=(
                "Write `validate_record(record, schema)` that takes a record and a field-to-type schema and "
                "returns a list of error strings. Check one valid and two invalid records, print each error list, "
                "and comment which line reports an unknown field."
            ),
            patterns=["def ", "return", "print("],
            mapping=(
                "JSON Schema and protobuf do this in production; a schema is data, and validation is a function "
                "over data."
            ),
        ),
        126: _Day(
            topic="Balancing tables",
            idea=(
                "A balancing table stores the numbers that make a game feel fair: base stats, growth per level, "
                "damage curves, costs. The goal is not one perfect value but a formula whose shape you can reason "
                "about. Store base values and growth separately so a design change is a number edit, then derive "
                "everything else. This is where data beats code: a designer tweaks a coefficient and the whole "
                "progression shifts without a programmer in the loop. The technique to reach for is a small "
                "derived-stat function, base plus growth times levels gained, and a combat function that turns two "
                "stat blocks into a result such as turns to kill. Keeping those as pure functions means you can "
                "sweep levels in a loop and print a table, which is how balance work is actually done. The trap is "
                "hard-coding an interaction instead of the underlying numbers, so every new character needs new "
                "logic. Notice the whole exercise is arithmetic over a dictionary: no engine, no rendering, just "
                "the model. Today you derive stats from base and growth, compute a simple time-to-kill, and check "
                "that a higher-level attacker finishes the same defender faster. The formula, not any single number, "
                "is the real design decision."
            ),
            code=r'''BASE = {"hp": 20, "attack": 5, "defence": 2}
GROWTH = {"hp": 8, "attack": 2, "defence": 1}


def stats_at(level):
    return {key: BASE[key] + GROWTH[key] * (level - 1) for key in BASE}


def turns_to_kill(attacker_level, defender_level):
    attack = stats_at(attacker_level)["attack"]
    defence = stats_at(defender_level)["defence"]
    hp = stats_at(defender_level)["hp"]
    per_hit = max(1, attack - defence)
    return (hp + per_hit - 1) // per_hit


for level in (1, 3, 5):
    print("level", level, stats_at(level))
print("L1 vs L1 turns:", turns_to_kill(1, 1))
print("L5 vs L1 turns:", turns_to_kill(5, 1))
assert turns_to_kill(5, 1) < turns_to_kill(1, 1)
print("derived stats keep the table balanced")
''',
            variant_b="change the attack growth and check which levels move the time-to-kill the most",
            variant_c="add a cost field that grows quadratically and print the level where cost outruns hp",
            mistakes=[
                "Hard-coding combat outcomes instead of deriving them from base stats and growth.",
                "Editing derived numbers directly so the table and the values drift apart.",
                "Leaving a divide or subtraction unprotected when defence can exceed attack.",
            ],
            q1=(
                "Why store base stats and growth separately instead of a table of final values per level?",
                "A formula with base and growth is a few numbers you can tune, while a full table must be edited at every level.",
            ),
            homework=(
                "Write `stats_at(level, base, growth)` that returns a stat dictionary for a level. Print the stats "
                "for three levels on two different base and growth pairs, and comment which line applies the "
                "growth."
            ),
            patterns=["def ", "return", "print("],
            mapping=(
                "Production balance lives in spreadsheets or data assets that feed formulas; designers tune "
                "coefficients, and the same function runs in the game."
            ),
        ),
        127: _Day(
            topic="Dialogue and quest data",
            idea=(
                "Dialogue is a graph: nodes hold text and a list of choices, and each choice names the next node. "
                "Quests are a small state machine on top: not started, active, complete, and conditions that move "
                "between them. Storing both as data separates writing from logic. A writer edits nodes and "
                "conditions, and the engine just follows the graph and evaluates the conditions. The key modelling "
                "decision is that choices are data, not code, so a new branch is a new node rather than a new "
                "function. Conditions should be data too, ideally referencing flags the player carries, such as "
                "has_key, rather than calling arbitrary logic, so dialogue can be validated and translated. The "
                "engine walks from a start node following choices, printing text at each step, and stops at a node "
                "with no choices. Because the graph is finite and every choice names an existing node, you can "
                "validate that it cannot loop forever or point at a missing node, which is exactly the kind of "
                "check a content pipeline runs. Today you encode a tiny conversation as a dictionary and walk it "
                "to the end. Notice the walker knows nothing about the story at all; it only follows the data."
            ),
            code=r'''DIALOGUE = {
    "start": {"text": "The gate is locked.", "choices": [("Ask about the key", "ask"), ("Leave", "end")]},
    "ask": {"text": "The keeper has it.", "choices": [("Leave", "end")]},
    "end": {"text": "You walk away.", "choices": []},
}


def play(node_id):
    seen = []
    while node_id != "end":
        seen.append(node_id)
        node = DIALOGUE[node_id]
        node_id = node["choices"][0][1]
    seen.append("end")
    return seen


print(play("start"))
assert play("start") == ["start", "ask", "end"]
assert DIALOGUE["end"]["choices"] == []
print("dialogue is a graph of data nodes")
''',
            variant_b="flip the first node's choice so the conversation ends immediately and check the path",
            variant_c="add a node with two choices and walk the second branch by indexing choice one",
            mistakes=[
                "Writing each conversation branch as its own function, so writers cannot add a line.",
                "Letting a choice point at a node that does not exist, so the walk crashes mid-scene.",
                "Embedding story logic in the walker instead of reading conditions from the data.",
            ],
            q1=(
                "Why model dialogue as a graph of data nodes instead of nested if-statements?",
                "Nodes and choices can be authored, validated and translated as data, while the engine only needs one walker.",
            ),
            homework=(
                "Write `walk_dialogue(dialogue, start, choice)` that follows the numbered choice at each node until "
                "a node with no choices, returning the visited ids. Walk two branches, print both paths, and "
                "comment which line stops the walk."
            ),
            patterns=["def ", "while ", "print("],
            mapping=(
                "Ink and Yarn compile authored dialogue graphs into data a runtime walks; the graph is content, the "
                "walker is code."
            ),
        ),
        128: _Day(
            topic="Items, drops and loot tables",
            idea=(
                "A loot table lists what a defeated enemy or opened chest can yield, with a probability and a "
                "quantity range per entry. Rolls are independent: guaranteed entries have a chance of one, and "
                "rare entries have a small chance, so a roll is one random draw per entry compared against its "
                "chance. Because entries carry everything, adding a new drop is a data edit, and the rolling "
                "function never changes. The design subtlety is that independent rolls and a single weighted pick "
                "are different systems: independent rolls can drop several things at once, while a weighted pick "
                "drops exactly one. Many games combine both, rolling guaranteed currency and then a weighted "
                "chance for a rare item. Quantity ranges are their own data so a chest can hold one to five coins "
                "without special code. As always the generator is seeded, so the same kill yields the same drops "
                "and a bug report can be replayed. Today you define a small loot table, roll it a few times from a "
                "fixed seed, and show that the guaranteed entry always appears while the rare one appears rarely. "
                "Keeping every number in the table means balance changes never touch the rolling code at all."
            ),
            code=r'''import random

LOOT = [
    {"item": "gold", "chance": 1.0, "min": 1, "max": 5},
    {"item": "potion", "chance": 0.5, "min": 1, "max": 1},
    {"item": "sword", "chance": 0.1, "min": 1, "max": 1},
]


def roll_drops(table, rng):
    drops = []
    for entry in table:
        if rng.random() < entry["chance"]:
            drops.append((entry["item"], rng.randint(entry["min"], entry["max"])))
    return drops


for run in range(3):
    print("drop", run, roll_drops(LOOT, random.Random(run)))
assert roll_drops(LOOT, random.Random(3))[0][0] == "gold"
print("gold is guaranteed, rare items are chance-based")
''',
            variant_b="set the sword chance to 1.0 and check it appears on every roll of the table",
            variant_c="add a second guaranteed entry and explain whether order of rolls should matter",
            mistakes=[
                "Rolling a single weighted pick when the design wants several independent drops.",
                "Comparing against a raw integer chance without normalising it to a fraction between zero and one.",
                "Forgetting to seed the generator, so a reported drop cannot be reproduced.",
            ],
            q1=(
                "What is the difference between independent rolls and one weighted pick?",
                "Independent rolls can yield several items in one pass, while a weighted pick always yields exactly one entry.",
            ),
            homework=(
                "Write `roll_loot(table, rng)` that takes entries with item, chance, min and max and a seeded "
                "generator, and returns the list of drops. Roll one table with two seeds, print each result, and "
                "comment which line decides whether an entry drops."
            ),
            patterns=["random.Random", "def ", "print("],
            mapping=(
                "ARPGs and MMOs run loot tables with guaranteed and rare entries; the same independent-roll model "
                "scales to hundreds of items."
            ),
        ),
        129: _Day(
            topic="Serialising content to JSON",
            idea=(
                "JSON is the lingua franca of content because it is text, human-readable and supported everywhere. "
                "Serialising content means turning your in-memory dictionaries into a JSON string, and "
                "deserialising means parsing it back. The round trip is the test that matters: load the string and "
                "check it equals the original data. Two habits make JSON usable in a pipeline. First, sort keys so "
                "the serialised form is stable: the same content produces the same bytes, which makes diffs and "
                "checksums meaningful. Second, keep the format tight and explicit rather than pretty, and add the "
                "pretty form only for debugging. JSON has limits worth knowing: keys are strings, tuples become "
                "lists, and types like sets and objects do not survive without a custom encoder, so keep content "
                "to dictionaries, lists and scalars. This is why content formats are usually flat records with "
                "string ids rather than clever Python objects. Never write files in examples, because output must "
                "be reproducible and side-effect free: serialise to a string and parse it back. Today you "
                "round-trip a small content bundle and assert that the parsed result equals the original, proving "
                "the format is lossless for this data. Text in, text out, and the same result on every machine."
            ),
            code=r'''import json


CONTENT = {
    "level": "cave_01",
    "tiles": ["grass", "stone"],
    "spawns": [{"kind": "slime", "x": 1, "y": 2}],
}


def to_json(content):
    return json.dumps(content, sort_keys=True, separators=(",", ":"))


text = to_json(CONTENT)
print(text)
reloaded = json.loads(text)
print("round trip equal:", reloaded == CONTENT)
assert reloaded == CONTENT
assert to_json({"b": 1, "a": 2}) == '{"a":2,"b":1}'
print("content survives a JSON round trip")
''',
            variant_b="add a nested list of coordinates and check the round trip still compares equal",
            variant_c="serialise a tuple and show it comes back as a list, then decide how to handle that",
            mistakes=[
                "Writing to a file during a lesson example, so reruns are no longer pure or reproducible.",
                "Relying on dictionary order instead of sorting keys, so output differs run to run.",
                "Putting sets or custom objects into content that JSON cannot represent without an encoder.",
            ],
            q1=(
                "Why sort keys when serialising content to JSON?",
                "A stable key order makes identical content produce identical text, so diffs and checksums are meaningful and output is reproducible.",
            ),
            homework=(
                "Write `round_trip(content)` that serialises a content dictionary to JSON with sorted keys and "
                "returns the parsed result. Round-trip two different bundles, print both parsed values, and "
                "comment which line proves the data is lossless."
            ),
            patterns=["json.dumps", "json.loads", "print("],
            mapping=(
                "Level editors and asset pipelines read and write JSON or a binary twin of it; stable key order is "
                "what keeps version-control diffs readable."
            ),
        ),
        130: _Day(
            topic="Save file versioning and migration",
            idea=(
                "A save file is content that outlives the code that wrote it. Players expect old saves to keep "
                "working after an update, which means every save needs a version number and every format change is "
                "a migration. The pattern is straightforward: read the version, and if it is older than current, "
                "apply the migration steps in order until the data reaches the current shape. Keeping migrations "
                "as small pure functions, one per version bump, makes them easy to test and safe to chain, and it "
                "means you never rewrite history: a version-one save passes through every step to reach today. "
                "Reads should also guard the future: a save from a newer build than the game understands should "
                "refuse politely rather than corrupt. Migrations must be idempotent in effect: loading an "
                "already-current save returns it unchanged, because the version field short-circuits the old steps. "
                "This is the same discipline as content schemas, applied to time: validate shape, respect the "
                "version, and never mutate the caller's data in place. Today you define a version-one save, write "
                "a migration to version two, and prove that loading a current save is a no-op. In this way history "
                "is preserved and every old save remains loadable."
            ),
            code=r'''SAVE_V1 = {"version": 1, "coins": 30, "level": "cave_01"}


def migrate(save):
    save = dict(save)
    if save["version"] == 1:
        save["xp"] = save["coins"] // 3
        save["version"] = 2
    return save


def load(save):
    if save["version"] > 2:
        raise ValueError("save from a newer build")
    return migrate(save)


old = dict(SAVE_V1)
new = load(old)
print("v1:", old)
print("v2:", new)
assert new["version"] == 2 and new["xp"] == 10
assert load(new) == new
print("migration is idempotent for the current version")
''',
            variant_b="add a version-three step that renames a field and load a version-one save through both",
            variant_c="pass a save from version nine and check the guard refuses it instead of guessing",
            mistakes=[
                "Storing no version, so an old save and a new one cannot be told apart.",
                "Editing saved data in place, so the caller's original structure is silently changed.",
                "Rewriting all older save files at once instead of chaining small migrations.",
            ],
            q1=(
                "Why should loading an already-current save return it unchanged?",
                "The version field short-circuits every older migration, so a current save is not re-transformed and repeated loads stay stable.",
            ),
            homework=(
                "Write `migrate_save(save)` that upgrades a save dictionary from version one to version two by "
                "adding a derived field and bumping version. Migrate an old save and a current one, print both "
                "results, and comment which check makes the second a no-op."
            ),
            patterns=["def ", "if ", "print("],
            mapping=(
                "Games ship migration code alongside save formats; each new patch adds one step so years-old saves "
                "still load."
            ),
        ),
        131: _Day(
            topic="Localisation and text keys",
            idea=(
                "Localisation replaces hard-coded strings with keys, and stores each key's text per language in a "
                "table. Code asks for the key, not the sentence, and a lookup decides which language to return. "
                "The reason is that a sentence in code cannot be translated, reused or reviewed, while a key can. "
                "The lookup should have a fallback: if a language is missing a key, use the default language "
                "rather than showing a key or crashing, because translations lag behind development and partial "
                "coverage is normal. Interpolation is the other half: a message like a greeting inserts a "
                "placeholder such as a name, and the same template is translated as a whole so word order can "
                "change per language. The discipline is that code never sees a user-facing literal, only a key, "
                "and text is data like everything else in this phase. A validator can then check that every key "
                "used exists in every shipped language, which catches the classic missing-translation bug before "
                "release. Today you build a two-language table with a fallback and interpolation, and show that a "
                "missing French string still renders in English, keeping the screen readable while the translation "
                "is finished. Text is just one more kind of content."
            ),
            code=r'''STRINGS = {
    "en": {"greet": "Hello, {name}!", "bye": "Goodbye"},
    "fr": {"greet": "Bonjour, {name}!"},
}


def text(locale, key, **values):
    table = STRINGS.get(locale, {})
    template = table.get(key) or STRINGS["en"].get(key, key)
    return template.format(**values)


print(text("en", "greet", name="Ada"))
print(text("fr", "greet", name="Ada"))
print(text("fr", "bye"))
assert text("fr", "greet", name="Ada") == "Bonjour, Ada!"
assert text("de", "greet", name="Ada") == "Hello, Ada!"
print("missing strings fall back to the default locale")
''',
            variant_b="add a German table with one key and show the rest still fall back to English",
            variant_c="add a key used in code but missing everywhere and decide what the fallback should return",
            mistakes=[
                "Writing user-facing sentences directly in code, so nothing can be translated or reviewed.",
                "Concatenating translated fragments, which breaks languages with different word order.",
                "Crashing on a missing translation instead of falling back to the default language.",
            ],
            q1=(
                "Why should code reference a text key rather than the final sentence?",
                "A key can be translated, reused and validated across languages, while a literal sentence can only exist in one language.",
            ),
            homework=(
                "Write `text(locale, key, strings, **values)` that looks up a localised template, falls back to "
                "the default locale when missing, and formats it with the values. Look up one present and one "
                "missing key, print both, and comment which line applies the fallback."
            ),
            patterns=["def ", "return", "print("],
            mapping=(
                "Engines ship string tables per locale and a lookup with fallback; a build step validates that "
                "every key has a translation."
            ),
        ),
        132: _Day(
            topic="Content pipelines and tooling",
            idea=(
                "A content pipeline is the path from authoring to a loadable game: collect raw records, validate "
                "them, report every problem, and emit a clean bundle. Treating it as a pipeline rather than "
                "loading files ad hoc is what makes content scalable and reproducible. The key behaviour is to "
                "report all errors and still produce the valid subset, so an author sees every problem in one run "
                "and the build can decide whether to fail. Raw records are hand-authored and unreliable: ids can "
                "be missing, duplicated or blank, references can dangle. A good builder separates these into "
                "valid content and an error list, sorts the output for stability, and never crashes partway so the "
                "rest of the records are still checked. This is the same validator idea from earlier, applied at "
                "scale, and it is where tooling pays off: one script can check a thousand records in a second, "
                "something no human reviewer can. Because the pipeline is deterministic, the same input always "
                "produces the same bundle, which makes it testable. Today you write a builder that splits records "
                "into valid and error lists, prints the ids it kept, and reports duplicates and missing ids "
                "without stopping at the first one."
            ),
            code=r'''def build(records):
    valid, errors = [], []
    for record in records:
        if not record.get("id"):
            errors.append(f"record without id: {record}")
        elif record["id"] in {r["id"] for r in valid}:
            errors.append(f"duplicate id: {record['id']}")
        else:
            valid.append(record)
    return sorted(valid, key=lambda r: r["id"]), errors


raw = [{"id": "slime", "hp": 4}, {"id": ""}, {"id": "slime", "hp": 6}, {"id": "bat", "hp": 2}]
content, errors = build(raw)
print("built:", [r["id"] for r in content])
for error in errors:
    print("error:", error)
assert [r["id"] for r in content] == ["bat", "slime"]
assert len(errors) == 2
print("pipeline reports every bad record instead of crashing")
''',
            variant_b="add a record with a duplicate blank id and decide whether it counts as one error or two",
            variant_c="make the builder reject records with hp below one and print the new error list",
            mistakes=[
                "Stopping at the first bad record, so authors fix problems one build at a time.",
                "Emitting records in authoring order, so the bundle is not stable across edits.",
                "Silently dropping bad records with no error list, so mistakes vanish instead of being fixed.",
            ],
            q1=(
                "Why should a content builder report all errors but still emit the valid records?",
                "The author fixes everything in one pass, and the build can choose to warn or fail while still giving a complete picture.",
            ),
            homework=(
                "Write `build_content(records)` that validates records with ids, drops blanks, reports duplicates "
                "as errors, and returns the sorted valid list plus the error list. Run it on a mixed list, print "
                "both results, and comment which line detects a duplicate."
            ),
            patterns=["def ", "return", "print("],
            mapping=(
                "Asset pipelines in shipping engines validate, transform and package content in one deterministic "
                "pass, failing the build on errors."
            ),
        ),
        133: _Day(
            topic="Testing content data",
            idea=(
                "Content bugs are data bugs: a goal outside the map, an enemy with no sprite, a duplicate id, a "
                "loot table whose chances never sum sensibly. Because content is data, all of these can be checked "
                "by functions that take the data and return problems, which run in a test or a pre-build step. "
                "This is different from testing engine logic: you are not checking that a collision resolves, you "
                "are checking an invariant that must hold for every level, such as the goal being inside the "
                "bounds, every referenced id existing, and every enemy having positive health. The powerful shape "
                "is a list of invariant checks over a list of records, collecting all failures rather than "
                "asserting on the first. That gives a report naming each offending record, which is exactly what a "
                "designer needs. Testing content this way catches the whole class of mistakes a play-test might "
                "miss for hours, and it runs instantly. The invariants are content too, so as the schema grows the "
                "checks grow with it. Today you write a bounds check over two levels, one good and one broken, and "
                "print the exact problem the broken level has, proving the test names the offender rather than "
                "just failing."
            ),
            code=r'''LEVELS = [
    {"id": "cave_01", "goal": {"x": 7, "y": 3}, "size": (8, 4)},
    {"id": "cave_02", "goal": {"x": 9, "y": 0}, "size": (8, 4)},
]


def check_levels(levels):
    problems = []
    seen = set()
    for level in levels:
        if level["id"] in seen:
            problems.append(f"duplicate id {level['id']}")
        seen.add(level["id"])
        w, h = level["size"]
        gx, gy = level["goal"]["x"], level["goal"]["y"]
        if not (0 <= gx < w and 0 <= gy < h):
            problems.append(f"goal out of bounds in {level['id']}")
    return problems


problems = check_levels(LEVELS)
print("problems:", problems)
assert problems == ["goal out of bounds in cave_02"]
print("content tests assert invariants, not exact output")
''',
            variant_b="add a duplicate id and a second out-of-bounds goal and check both appear in the problems",
            variant_c="add an invariant that every level has a non-empty id and test a level with a blank one",
            mistakes=[
                "Asserting on the first bad level with a plain assert, so the report stops at one problem.",
                "Skipping content tests because the data looks fine, so a typo ships to players.",
                "Writing checks that name no record, so a failure does not say which level broke.",
            ],
            q1=(
                "Why collect all content problems instead of asserting on the first one?",
                "A designer gets one report naming every broken record, so all fixes happen in a single pass.",
            ),
            homework=(
                "Write `check_levels(levels)` that returns a list of problems for a list of level dictionaries, "
                "checking goal bounds and duplicate ids. Run it on a list with one broken level, print the "
                "problems, and comment which line names the offending level."
            ),
            patterns=["def ", "return", "print("],
            mapping=(
                "Studios run content validation in CI; a data error fails the build the same way a code bug does, "
                "before a tester ever sees it."
            ),
        ),
        134: _Day(
            topic="Review: content and levels checklist",
            idea=(
                "This review ties the phase together into one checklist you can run against a content bundle: are "
                "there levels, do enemies have positive health, are ids unique, is the loot table non-empty, does "
                "every referenced id exist. A checklist of small named checks is more useful than one giant "
                "validator because the report says which check failed and why, and each check can be reasoned "
                "about on its own. The pattern is a list of tuples, a name, a predicate over the content and a "
                "description, then a runner that evaluates each and prints a pass or fail line. Keeping checks as "
                "data means adding a rule is adding a row, not editing a function, which is the same lesson as "
                "content is data applied to testing itself. A healthy bundle passes every check, and a failing one "
                "names the exact rule that broke, so the fix is obvious. This is the shape of a pre-build gate: "
                "cheap, deterministic, and complete enough to catch the mistakes that cost the most time. Today you "
                "assemble the phase's ideas into a small checklist, run it against a healthy content bundle, and "
                "confirm every check passes. Change a value and you can watch a specific check fail."
            ),
            code=r'''CONTENT = {
    "levels": ["cave_01", "cave_02"],
    "enemies": {"slime": {"hp": 4}, "bat": {"hp": 2}},
    "loot": ["gold", "potion"],
}


CHECKS = [
    ("levels", lambda c: len(c["levels"]) > 0, "at least one level"),
    ("enemies", lambda c: all(v["hp"] > 0 for v in c["enemies"].values()), "enemies have hp"),
    ("loot", lambda c: len(c["loot"]) > 0, "loot table is not empty"),
]


def run_checks(content, checks):
    return [(name, bool(test(content)), description) for name, test, description in checks]


for name, ok, description in run_checks(CONTENT, CHECKS):
    print(("PASS" if ok else "FAIL"), name, "-", description)
assert all(ok for _, ok, _ in run_checks(CONTENT, CHECKS))
print("checklist passes on a healthy bundle")
''',
            variant_b="set one enemy's hp to zero and predict which checklist line turns to FAIL",
            variant_c="add a check that every level id is unique and run it on a bundle with a duplicate",
            mistakes=[
                "Bundling every rule into one function, so a failure does not say which rule broke.",
                "Treating a failed check as a warning that never blocks the build, so broken content ships.",
                "Writing checks that read data the content does not define, crashing before the report prints.",
            ],
            q1=(
                "Why store checklist rules as data instead of writing one large validation function?",
                "Each rule can be named, added or removed as a row, and a failure reports exactly which rule broke.",
            ),
            homework=(
                "Write `run_checks(content, checks)` that takes a content bundle and a list of named predicate "
                "tuples and returns name, ok and description for each. Run it on one healthy and one broken "
                "bundle, print the report, and comment which line evaluates a check."
            ),
            patterns=["def ", "return", "print("],
            mapping=(
                "Pre-build gates in game and web pipelines are checklists like this; a named failing check is far "
                "faster to fix than a stack trace."
            ),
        ),
    },
)

del _Day
