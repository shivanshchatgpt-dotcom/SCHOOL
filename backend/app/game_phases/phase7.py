"""Game Development capstone, days 165-179, built around one toy dungeon crawler.

Every worked example is stdlib-only, offline and deterministic, so the applier
can run it and the learner sees the same output on every machine. The arc moves
from scoping and design through the loop, entities, rules and content to
simulation, tests, packaging, performance and a retrospective, so each day is a
real slice of the same small game rather than advice about working on one.
"""

PHASE = (
    "Game Development Capstone",
    "Scope, build, test, balance and ship one small turn-based dungeon crawler end to end.",
    {
        165: dict(
            topic="Capstone: choose the scope",
            idea=(
                "Scope is the first and hardest capstone decision, because projects fail far more often from too "
                "much ambition than from too little. The practical technique is the vertical slice: the smallest "
                "build that contains every kind of work the finished game needs, such as one level, one enemy, "
                "one rule and one win condition, rather than a horizontal layer of many half-finished systems. A "
                "cheap way to force the cut is to list candidate features with an effort cost and a mandatory "
                "flag, then keep every mandatory feature and add optional ones only while the budget lasts. That "
                "budget is often time, but it can be lines of code or a count of systems. Writing the list down "
                "turns a vague feeling of too much to do into a concrete set you can finish and demo. The exercise "
                "also exposes dependencies, because combat is worthless without movement and loot is worthless "
                "without combat, so build order falls out of the graph. Today you encode the decision as data and "
                "print the resulting minimum scope. The habit outlives the capstone: every studio milestone is a "
                "scope cut, and finishing a small complete game teaches more than abandoning a large unfinished one."
            ),
            code="""def in_scope(features, budget):
    kept = []
    spent = 0
    for name, cost, must in features:
        if must or spent + cost <= budget:
            kept.append(name)
            spent += cost
    return kept, spent

features = [
    ("move", 1, True),
    ("combat", 3, True),
    ("loot", 2, False),
    ("boss", 2, False),
    ("crafting", 5, False),
]
kept, spent = in_scope(features, 6)
print("MVP scope:", kept)
print("effort spent:", spent, "of budget 6")
assert "move" in kept and "crafting" not in kept
print("optional work cut once the budget ran out")
""",
            variant_b="give crafting a cost of 3 instead of 5 and see whether it now fits the budget",
            variant_c="add a risk column and drop any optional feature that duplicates combat",
            mistakes=[
                "Listing twenty features and starting all of them, so nothing reaches a playable state.",
                "Calling a horizontal layer (all the art, all the menus) a vertical slice when no full loop exists.",
                "Treating the budget as fixed when the real constraint is the number of unfinished systems.",
            ],
            q1=(
                "What is a vertical slice and why does it beat a horizontal one for a capstone?",
                "It builds one complete path through every system, so the game is playable and testable early instead of many half-finished layers.",
            ),
            homework=(
                "Write `choose_scope(features, budget)` that takes (name, cost, must) tuples and returns the kept "
                "names and the total cost. Run it with two budgets on the same list, print both results, and "
                "comment which line admits the mandatory features regardless of cost."
            ),
            patterns=["def ", "return", "print("],
            mapping=(
                "Studios cut milestones exactly this way: a playable vertical slice first, then breadth. Engines "
                "such as Godot even keep a prototype scene separate from the shipping one."
            ),
        ),
        166: dict(
            topic="Write the design doc",
            idea=(
                "A design doc is not prose for its own sake; it is the shortest text that lets someone else build "
                "the same game and lets you tell when it is done. A useful template is four sections: pitch, the "
                "one sentence that says what the game is; loop, the repeating action the player performs; systems, "
                "the list of mechanics the loop needs; and done, a testable condition for the capstone being "
                "complete. The done section is the one people skip and the one that matters most, because it "
                "converts scope into a check you can run rather than a feeling. Write each section as short bullets, "
                "keep the whole thing under a page, and treat it as a living document you edit when the design "
                "changes, not a contract carved in stone. The discipline of filling every section reveals gaps "
                "early: if you cannot write the loop in one sentence, you do not yet know what the player does. "
                "Today you store the doc as a dictionary and write a small checker that reports missing sections. "
                "That checker is itself a test, which is the theme that returns on the testing day."
            ),
            code="""REQUIRED = ("pitch", "loop", "systems", "done")

doc = {
    "pitch": "a turn-based dungeon crawl in one room",
    "loop": "explore, fight, descend",
    "systems": ["grid movement", "melee combat", "loot"],
    "done": "one level that can be won or lost",
}

def missing_sections(doc, required):
    return [name for name in required if not doc.get(name)]

print("design doc sections:", len(doc))
print("missing:", missing_sections(doc, REQUIRED))
assert missing_sections({"pitch": "x"}, REQUIRED) == ["loop", "systems", "done"]
print("the done section is what makes scope testable")
""",
            variant_b="add a 'risks' section to the doc and make the checker require it",
            variant_c="store each section as a list of bullet strings and print them one per line",
            mistakes=[
                "Writing prose that never states a single, testable done condition.",
                "Letting the design doc grow past what a one-week prototype can build.",
                "Writing the doc once and never updating it when the design changes.",
            ],
            q1=(
                "Why does a design doc need a 'done' section?",
                "A testable done condition turns scope into something you can check, instead of a feeling about whether the game is finished.",
            ),
            homework=(
                "Write `audit_doc(doc, required)` that returns the missing required sections, then `render_doc(doc)` "
                "that prints each section heading and its value. Call audit_doc on a complete and an incomplete doc, "
                "print both, and comment which line defines completeness."
            ),
            patterns=["def ", "return", "print("],
            mapping=(
                "Real teams keep a one-page design doc as a living spec; the stable parts become tickets and the "
                "rest is edited as the game teaches you what it wants to be."
            ),
        ),
        167: dict(
            topic="Build the core loop",
            idea=(
                "The core loop is the heartbeat of the game, and the clean way to build one is a state machine: a "
                "small set of named states and a table saying which state follows which. Menu goes to play, play "
                "goes to combat, combat goes to win or lose, and both endings go to over. Making the transitions "
                "explicit as data, rather than as scattered if-statements, gives you three things at once. The "
                "loop provably terminates if the graph has a terminal state, every screen is a value you can test "
                "in isolation, and a designer can read the whole progression from one dictionary. The update step "
                "should only decide the next state; drawing and input belong outside it, exactly as with any other "
                "rule. The classic failure is an unbounded loop with no terminal state, which hangs the game "
                "instead of ending it. Today you walk a transition table from a start state, collecting the path, "
                "and print it until a terminal state is reached. Notice that the loop never inspects what a screen "
                "looks like, only which state comes next, which is what keeps it testable headless."
            ),
            code="""TRANSITIONS = {
    "menu": "play",
    "play": "combat",
    "combat": "win",
    "win": "over",
}

def run(limit):
    state = "menu"
    seen = [state]
    while state != "over" and len(seen) < limit:
        state = TRANSITIONS[state]
        seen.append(state)
    return seen

path = run(10)
print("screens visited:", " -> ".join(path))
assert path == ["menu", "play", "combat", "win", "over"]
print("the core loop is a state machine with one terminal state")
""",
            variant_b="add a 'lose' terminal state reachable from combat and print the new path",
            variant_c="store transitions that carry an action name and print the action taken at each step",
            mistakes=[
                "Writing an unbounded while loop with no terminal state, so the game never ends.",
                "Scattering screen logic across if-statements instead of one table of transitions.",
                "Letting a transition carry side effects such as saving the game.",
            ],
            q1=(
                "Why model the core loop as a state machine?",
                "It makes every screen and transition explicit and finite, so the loop always terminates and each state can be tested on its own.",
            ),
            homework=(
                "Write `reach(transitions, start, limit)` that walks the transition table from a start state and "
                "returns the list of states seen, stopping at the limit. Run it on two different start states, "
                "print both paths, and comment which line guarantees termination."
            ),
            patterns=["def ", "while ", "print("],
            mapping=(
                "Engine scene managers are this table plus a renderer; Godot's scene tree and a Unity state "
                "machine both encode transitions explicitly."
            ),
        ),
        168: dict(
            topic="Model the entities",
            idea=(
                "Entities are the nouns of the game, and the design question is whether a goblin and a boss "
                "deserve separate classes or one record that differs only in numbers. Splitting behaviour per "
                "monster type multiplies code and multiplies bugs; sharing one rule set and describing monsters "
                "as data keeps the code small and makes new content a table edit. A frozen dataclass with name, "
                "health, attack and position is enough for a crawler, and spawning becomes a function that reads a "
                "stats table and returns a fresh entity at a given tile. That single spawn function is the only "
                "place that knows how stats become an object, so changing the schema touches one spot. Keep "
                "presentation fields such as colour out of the entity record, because they are rendering concerns "
                "and would otherwise leak into the rules. There is a real trade-off: data-driven monsters cannot "
                "have wildly different behaviour without a behaviour tag the rules check, and for a capstone a "
                "small tag field covers that need. Today you spawn two monsters from a bestiary dictionary and "
                "print them, proving the stats table stays the only source of truth."
            ),
            code="""from dataclasses import dataclass

@dataclass(frozen=True)
class Entity:
    name: str
    hp: int
    atk: int
    x: int
    y: int

BESTIARY = {"goblin": {"hp": 5, "atk": 2}, "rat": {"hp": 2, "atk": 1}}

def spawn(kind, x, y):
    stats = BESTIARY[kind]
    return Entity(kind, stats["hp"], stats["atk"], x, y)

goblin = spawn("goblin", 3, 1)
rat = spawn("rat", 4, 2)
print("spawned:", goblin)
print("second:", rat.name, rat.hp, "hp at", (rat.x, rat.y))
assert (goblin.hp, rat.hp) == (5, 2)
print("entities are data built from stats, not hard-coded objects")
""",
            variant_b="add a boss entry with 20 hp and 4 attack and spawn it in the far corner",
            variant_c="add a unique id field so two goblins can be told apart in the log",
            mistakes=[
                "Hard-coding each monster as its own class when they differ only in stats.",
                "Building entities and mutating them later instead of spawning fresh from data.",
                "Mixing presentation fields such as colour into the entity record.",
            ],
            q1=(
                "Why spawn entities from a stats table instead of one class per monster?",
                "Behaviour lives in the shared rules, so monsters differ only by data and a new monster is a table entry rather than new code.",
            ),
            homework=(
                "Write `spawn_all(kinds, table)` that returns a list of entity objects built from a stats table, "
                "one per kind, each with a distinct position. Print the list, and comment which line keeps the "
                "stats as the only source of truth."
            ),
            patterns=["def ", "return", "print("],
            mapping=(
                "This is data-driven design: engines load entity archetypes from files, and the spawn code does "
                "not change when content is added."
            ),
        ),
        169: dict(
            topic="Implement the rules",
            idea=(
                "Rules are the verbs of the game, and each should be a pure function that reads the world and "
                "returns a new world. Move takes a position and a direction; attack takes an attacker and a target "
                "and reduces the target's health; heal caps at a maximum. None of them draw, read the keyboard or "
                "decide whose turn it is. That narrow contract is what lets you test a rule with a hand-built "
                "world, replay it from a log, and reuse it for a computer-controlled enemy without change. A rule "
                "should never mutate shared state in place and return nothing, because then the caller cannot tell "
                "what changed and previous states cannot be kept for undo or replay. The caller, usually the loop, "
                "decides the order in which rules run, and the win condition is checked there rather than inside "
                "any rule. Watch for functions that quietly mix movement, damage and presentation, which is the "
                "most common way a small rule set becomes untestable. Today you write move and attack, chain them, "
                "and print the world after each step, with an assertion proving damage was applied exactly once."
            ),
            code="""def move(entities, name, dx, dy):
    updated = dict(entities)
    e = dict(updated[name])
    e["x"] += dx
    e["y"] += dy
    updated[name] = e
    return updated

def attack(entities, attacker, target):
    updated = dict(entities)
    t = dict(updated[target])
    t["hp"] = max(0, t["hp"] - updated[attacker]["atk"])
    updated[target] = t
    return updated

world = {"hero": {"hp": 8, "atk": 3, "x": 1, "y": 1},
         "goblin": {"hp": 5, "atk": 2, "x": 2, "y": 1}}
world = move(world, "hero", 1, 0)
world = attack(world, "hero", "goblin")
print("hero at", (world["hero"]["x"], world["hero"]["y"]))
print("goblin hp:", world["goblin"]["hp"])
assert world["goblin"]["hp"] == 2
print("rules transform state and know nothing about drawing")
""",
            variant_b="add a heal rule capped at a max_hp stored on the entity",
            variant_c="make move reject a step into a wall using the level grid from the next day",
            mistakes=[
                "Mixing movement, damage and rendering in one function so no rule can be tested alone.",
                "Mutating the shared world in place and returning None instead of new state.",
                "Reading the keyboard directly inside a rule function.",
            ],
            q1=(
                "Why should each rule take the world as an argument and return a new world?",
                "The rule becomes a pure transformation you can test and replay, and the caller decides when and in what order rules run.",
            ),
            homework=(
                "Write `heal(world, name, amount, max_hp)` that returns new world state with the target healed but "
                "never above max_hp. Apply it to a full-health and a wounded entity, print both results, and "
                "comment which line clamps the value."
            ),
            patterns=["def ", "max(", "print("],
            mapping=(
                "In an engine these are the systems that run each tick; keeping them pure is what lets you "
                "unit-test combat without launching the game."
            ),
        ),
        170: dict(
            topic="Create the first level",
            idea=(
                "A level is data, and the cheapest authoring format is text: rows of characters where a hash is a "
                "wall, a dot is floor, an at sign is the player, a letter is a monster and a greater-than sign is "
                "the exit. Storing the map as a list of strings means you can edit it in any text editor and read "
                "it at a glance, which is worth more during a capstone than any editor tooling. A tiny parser "
                "turns those rows into two things the rest of the game needs: a grid you can index by coordinates "
                "and a dictionary of marks giving each symbol its position. Always check that a required mark "
                "exists before trusting it, because a map missing a player start should fail loudly rather than "
                "place the hero at the origin. This is also the day to fix your coordinate convention, whether y "
                "grows downward, and to write it down so half the code never disagrees with the other half. Today "
                "you parse a five-row level, print its dimensions and the positions of the player, monster and "
                "stairs, and assert the walls and the player start. Movement and line of sight later read this "
                "same grid, so getting the parser right pays off immediately."
            ),
            code="""LEVEL = [
    "#####",
    "#@..#",
    "#.g.#",
    "#..>#",
    "#####",
]

def parse(rows):
    grid = [list(row) for row in rows]
    marks = {}
    for y, row in enumerate(rows):
        for x, cell in enumerate(row):
            if cell in "@g>":
                marks[cell] = (x, y)
    return grid, marks

grid, marks = parse(LEVEL)
print("level size:", len(grid[0]), "x", len(grid))
print("player at", marks["@"], "| goblin at", marks["g"], "| stairs at", marks[">"])
assert grid[0][0] == "#" and marks["@"] == (1, 1)
print("the level is text data the parser turns into a grid")
""",
            variant_b="add a second level string and parse both, printing each player start",
            variant_c="treat 'T' as a treasure tile and return its coordinates alongside the monsters",
            mistakes=[
                "Editing maps by hand in code instead of loading them as text rows.",
                "Trusting a map to contain a player start without checking.",
                "Mixing tile coordinates with pixel coordinates from the start.",
            ],
            q1=(
                "Why store levels as text rows rather than literal grid objects?",
                "Text maps are easy to author and read, and a tiny parser turns them into the grid and spawn points the rules need.",
            ),
            homework=(
                "Write `find_marks(rows, symbols)` that returns a dictionary mapping each symbol it finds to its "
                "(x, y) position. Run it on a map with two marks, print the dictionary, and comment which line "
                "scans row and column."
            ),
            patterns=["for ", "enumerate", "print("],
            mapping=(
                "Level editors and formats such as Tiled, and the classic ASCII roguelike maps, all reduce to "
                "rows of symbols parsed into a grid."
            ),
        ),
        171: dict(
            topic="Add content data",
            idea=(
                "Content is the numbers and names that designers tweak, and it should live in tables rather than "
                "inside the code that uses it. A monster table maps an id to health, attack and a spawn weight; an "
                "item table maps an id to its effect. The rules then look a monster up by id and never mention a "
                "specific creature, so adding a dragon is a new row and nothing else. Weights turn a table into a "
                "spawn distribution: sum the weights, draw a number in that range, and walk the entries until the "
                "running total passes the draw. That is one small function, and it lets you make rare creatures "
                "rare without special cases. The other habit is the safe lookup, using a default when a key is "
                "missing so a mistyped id produces a weak placeholder rather than a crash, at least during "
                "prototyping. Keep the tables in one module so the balance pass has a single file to edit. Today "
                "you define a weighted bestiary, draw several spawns from a fixed seed, and print both the results "
                "and a lookup that falls back to a default."
            ),
            code="""import random

MONSTERS = {
    "rat": {"hp": 2, "atk": 1, "weight": 3},
    "goblin": {"hp": 5, "atk": 2, "weight": 2},
    "slime": {"hp": 7, "atk": 1, "weight": 1},
}

def pick(rng, table):
    total = sum(v["weight"] for v in table.values())
    roll = rng.randrange(total)
    for name in table:
        roll -= table[name]["weight"]
        if roll < 0:
            return name
    return name

rng = random.Random(7)
spawns = [pick(rng, MONSTERS) for _ in range(6)]
print("spawned:", spawns)
print("stats for goblin:", MONSTERS.get("goblin", {}))
print("stats for dragon:", MONSTERS.get("dragon", {"hp": 0}))
assert all(name in MONSTERS for name in spawns)
print("content lives in tables, code only reads them")
""",
            variant_b="add an elite monster with weight 1 and draw twenty spawns to see how rare it is",
            variant_c="move the weights into a separate table and compute the total once before drawing",
            mistakes=[
                "Scattering monster stats through the combat code instead of one table.",
                "Assuming a key exists and crashing on an unknown monster id.",
                "Using unweighted choice when rarity is meant to differ.",
            ],
            q1=(
                "Why separate content tables from the code that reads them?",
                "Designers can retune numbers without touching logic, and the code stays small enough to test with fake tables.",
            ),
            homework=(
                "Write `weighted_pick(rng, table)` that draws one key using each entry's weight and never crashes "
                "on an empty table. Draw ten picks from a fixed seed, print them, and comment which line converts "
                "the roll into a choice."
            ),
            patterns=["def ", "return", "print("],
            mapping=(
                "This is a data asset or spreadsheet pipeline: content lives in files, the code reads it, and the "
                "balance team edits it without a programmer."
            ),
        ),
        172: dict(
            topic="Polish the presentation",
            idea=(
                "Presentation is everything the player sees, and the discipline is to make it a pure function of "
                "state so it can change freely without touching the rules. A health bar is a ratio clamped to a "
                "width; a heads-up display is a formatted line combining name, bar and numbers; a combat log is a "
                "list of strings. Because these are pure functions, you can test a bar at zero, half and full, and "
                "you can restyle the whole game without fear of changing balance. Fixed field widths and alignment "
                "matter more than they sound, because columns that jump as numbers change make a turn-based game "
                "feel broken. Keep the rendering separate from the simulation for the same reason you kept rules "
                "pure: a headless test must never need to look at the screen. If the same formatting rules are "
                "duplicated in three places they will drift, so centralise them. Today you write a bar renderer and "
                "an aligned HUD line, print a full and a nearly empty bar, and assert the two extremes fill and "
                "empty exactly. This is the layer a real engine replaces with widgets, and nothing below it should "
                "need to change."
            ),
            code="""def bar(value, maximum, width=10):
    filled = round(width * value / maximum)
    return "[" + "#" * filled + "." * (width - filled) + "]"

def hud(name, hp, maximum, gold):
    return f"{name:<6} {bar(hp, maximum)} {hp:>2}/{maximum:<2} gold {gold:>3}"

print(hud("hero", 7, 12, 15))
print(hud("rat", 1, 2, 0))
assert bar(12, 12) == "[" + "#" * 10 + "]"
assert bar(0, 12) == "[" + "." * 10 + "]"
print("presentation is pure formatting over state")
""",
            variant_b="add a percentage suffix and right-align the numbers in a fixed column",
            variant_c="render the bar with block characters scaled to a width passed in",
            mistakes=[
                "Building UI strings from raw numbers without fixed widths, so the columns jump.",
                "Computing the bar width from hp without clamping, so it overflows.",
                "Coupling formatting to game rules so balance changes alter the HUD output.",
            ],
            q1=(
                "Why separate formatting from game state?",
                "Formatting is a pure function of state, so you can change the look without touching the rules and test the rules without reading text.",
            ),
            homework=(
                "Write `xp_bar(xp, needed, width)` that returns a bar string filling proportionally and clamped to "
                "the given width. Print bars for zero, half and full, and comment which line prevents overflow past "
                "the width."
            ),
            patterns=["def ", "return", "print("],
            mapping=(
                "This is the HUD layer; engines keep widgets reading state each frame, so a restyle never changes "
                "combat numbers."
            ),
        ),
        173: dict(
            topic="Balance with simulation",
            idea=(
                "Balance is a measurement, not a guess, and the tool for measuring it is a headless simulation "
                "harness. The idea is to wrap the real rules in an autoplay loop that makes both sides act without "
                "any input, run it across hundreds of fixed seeds, and look at aggregate numbers such as win rate "
                "and average length. Because the rules are pure and the randomness is seeded, the numbers are "
                "reproducible: the same build gives the same win rate, so a change that moves it moved the balance "
                "and not the noise. Judging balance from one playthrough is the classic error, because a single run "
                "is dominated by luck. Change one value at a time, or you cannot tell which change did the work. "
                "The harness should call exactly the functions the real game calls, or the simulation lies about "
                "the thing you shipped. A win rate near an extreme usually means the fight is decided by the "
                "opening dice rather than by choices, which is itself a design signal. Today you autoplay two "
                "hundred seeded fights, print the hero win rate, and show that a fixed seed still gives a fixed "
                "outcome."
            ),
            code="""import random

def autoplay(seed, hero_hp=8, foe_hp=5):
    rng = random.Random(seed)
    hero, foe = hero_hp, foe_hp
    while hero > 0 and foe > 0:
        foe = max(0, foe - rng.randint(1, 3))
        if foe == 0:
            break
        hero = max(0, hero - rng.randint(1, 3))
    return "hero" if foe == 0 else "foe"

def win_rate(runs):
    wins = sum(1 for seed in range(runs) if autoplay(seed) == "hero")
    return wins / runs

rate = win_rate(200)
print("runs: 200, hero win rate:", round(rate, 3))
print("seed 0 outcome:", autoplay(0), "| seed 1:", autoplay(1))
assert 0.0 <= rate <= 1.0
print("balance is measured by simulating many seeded games")
""",
            variant_b="raise the hero attack range and rerun two hundred seeds to see the new win rate",
            variant_c="return the average number of turns alongside the win rate",
            mistakes=[
                "Judging balance from one lucky playthrough instead of many seeds.",
                "Making the simulated rules differ from the real ones, so the numbers lie.",
                "Changing two values at once, so you cannot tell which fixed the balance.",
            ],
            q1=(
                "Why run hundreds of seeded games to judge balance?",
                "A single run is noise; many deterministic runs give a stable win rate that shows whether a change helped.",
            ),
            homework=(
                "Write `average_turns(runs, seed_start)` that autoplays one game per seed and returns the mean "
                "number of turns. Print the mean for two different starting hp values, and comment which line "
                "accumulates the total."
            ),
            patterns=["def ", "for ", "print("],
            mapping=(
                "Studios build exactly this harness, often called a headless soak test, to tune difficulty before "
                "a human ever plays."
            ),
        ),
        174: dict(
            topic="Write headless tests",
            idea=(
                "A headless test runs game logic with no window, no input and no clock, so it can run on every "
                "save and every commit. The pattern is small: a rule function, one test function per behaviour, "
                "and a runner that executes each test and reports passes and failures. Test the contract, not the "
                "printed output, by asserting on returned values such as health after damage or a position after a "
                "blocked move. The payoff is regression safety on a capstone where you are still changing the "
                "rules daily: if a balance tweak breaks the damage cap, a test tells you in a second instead of "
                "after a confusing playtest. Avoid one giant test that checks everything at once, because a "
                "failure then hides which rule broke. Avoid tests that depend on wall-clock time or on the order "
                "other tests ran, since those pass today and fail in a different environment. The runner you write "
                "here is a few lines, and it is enough for a capstone; a framework only matters when the suite "
                "grows. Today you write three rule tests, run them, and print the pass and fail counts."
            ),
            code="""def damage(hp, amount):
    return max(0, hp - amount)

def test_damage_reduces():
    assert damage(10, 3) == 7

def test_damage_never_negative():
    assert damage(2, 5) == 0

def test_damage_zero_amount():
    assert damage(4, 0) == 4

def run_tests():
    passed = failed = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_"):
            try:
                fn()
                passed += 1
            except AssertionError:
                failed += 1
    return passed, failed

passed, failed = run_tests()
print("tests passed:", passed, "failed:", failed)
assert (passed, failed) == (3, 0)
print("headless tests pin the rules without a window")
""",
            variant_b="add a test for healing past max hp and check it fails before you fix the rule",
            variant_c="make run_tests return the names of failing tests instead of just the counts",
            mistakes=[
                "Testing by reading printed output instead of asserting on returned values.",
                "Writing one giant test that checks everything, so a failure hides its cause.",
                "Leaving a test that depends on the clock or on run order.",
            ],
            q1=(
                "What makes a test headless?",
                "It exercises rules with no window, input or clock, so it runs anywhere and returns the same result every time.",
            ),
            homework=(
                "Write `run_tests(tests)` taking a list of (name, function) pairs, running each and returning the "
                "passing and failing names. Register three rules tests, print the summary, and comment which line "
                "catches the assertion failure."
            ),
            patterns=["def ", "assert", "print("],
            mapping=(
                "CI runs these same headless tests on every commit; engines make gameplay logic testable "
                "precisely so this is possible."
            ),
        ),
        175: dict(
            topic="Playtest and fix",
            idea=(
                "A playtest is only useful if the bugs it finds can be reproduced, and the way to make that "
                "reliable is a command log. Record the exact sequence of player actions with the seed, and you "
                "have a deterministic recipe that turns a one-time glitch into a repeatable failure. The workflow "
                "is to replay that log against the current code, watch the wrong state appear, and then find the "
                "shared function responsible rather than patching the single command path that happened to be "
                "reported. Boundary bugs are the common case, such as a move that walks off the map because the "
                "guard is missing, and the lazy correct fix is one check in the move function that every "
                "direction and every caller already routes through. Changing behaviour without the log is worse "
                "than not fixing the bug, because the next tester cannot reproduce either the fault or the fix. "
                "Once fixed, the same log becomes a regression test that guards the boundary forever. Today you "
                "replay a small command log against a buggy move and a guarded move, print both final positions, "
                "and assert the guarded version stays on the map."
            ),
            code="""def try_move(pos, cmd, width, height):
    x, y = pos
    if cmd == "e":
        x += 1
    elif cmd == "w":
        x -= 1
    return (x, y)

LOG = ["e", "e", "e"]
pos = (1, 1)
for cmd in LOG:
    pos = try_move(pos, cmd, width=3, height=3)
print("buggy end position:", pos)
assert pos == (4, 1)

def fixed_move(pos, cmd, width, height):
    x, y = pos
    if cmd == "e":
        x += 1
    elif cmd == "w":
        x -= 1
    return (x, y) if 0 <= x < width and 0 <= y < height else pos

pos = (1, 1)
for cmd in LOG:
    pos = fixed_move(pos, cmd, width=3, height=3)
print("fixed end position:", pos)
assert pos == (2, 1)
print("replay the command log to reproduce, then guard the boundary")
""",
            variant_b="add a north command to both versions and replay a log that walks into the top wall",
            variant_c="have fixed_move also reject a step onto an occupied tile",
            mistakes=[
                "Fixing the symptom on one command path instead of the shared move function.",
                "Changing behaviour without a saved command log, so the bug cannot be reproduced.",
                "Adding a clamp that silently changes the position instead of rejecting the move.",
            ],
            q1=(
                "Why replay a saved command log instead of clicking around?",
                "The log reproduces the exact state that triggered the bug, so the fix can be verified deterministically.",
            ),
            homework=(
                "Write `replay(start, commands, width, height)` that applies fixed_move for each command and "
                "returns the final position. Replay the buggy log and a short log, print both positions, and "
                "comment which line rejects an out-of-bounds step."
            ),
            patterns=["def ", "return", "print("],
            mapping=(
                "Player bug reports ship as replays and seeds; the same command log drives the fix and the "
                "regression test."
            ),
        ),
        176: dict(
            topic="Package and present",
            idea=(
                "Packaging is how a playable prototype becomes something another person can run, and the core "
                "artifact is a manifest: the project name, a version, the list of files, and a fingerprint of "
                "their contents. The fingerprint is a hash over the files in a fixed order, so two builds are "
                "identical exactly when their digests match and any edit changes the digest. That property is what "
                "lets a build system, a download page or a teammate tell whether they have the same thing you do, "
                "and it is the same idea behind package checksums. The other packaging discipline is to ship only "
                "files that are listed, so the build is self-contained and traceable rather than a folder full of "
                "unknown leftovers. Version numbers should live in one place and be read from there, not "
                "hand-typed into three files that then disagree. For a capstone this is deliberately small: an "
                "in-memory manifest built by a function, printed with a short digest. If the game writes a save "
                "file, that format is part of the package too and deserves its own version. Today you build and "
                "print a manifest, then show the digest changing when a file is added."
            ),
            code="""import hashlib

FILES = {
    "main.py": ("print('run the game')",),
    "level.txt": ("#####", "#@..#", "#####"),
    "README.md": ("a tiny dungeon crawler",),
}

def fingerprint(files):
    blob = "|".join(f"{name}:{'/'.join(files[name])}" for name in sorted(files))
    return hashlib.sha256(blob.encode()).hexdigest()

digest = fingerprint(FILES)
manifest = {"name": "dungeon", "version": "1.0", "files": len(FILES),
            "digest": digest[:12]}
print("manifest:", manifest)
assert fingerprint(FILES) == digest
assert fingerprint({**FILES, "extra.py": ("x",)}) != digest
print("the digest changes when any packaged file changes")
""",
            variant_b="add the python version and a sorted file list to the manifest and print them",
            variant_c="fingerprint the files in reverse order and show the digest still matches",
            mistakes=[
                "Shipping files that are not in the manifest, so the package is untraceable.",
                "Hand-writing the version in three places and letting them disagree.",
                "Depending on a system library that is not declared anywhere.",
            ],
            q1=(
                "Why fingerprint the packaged files?",
                "A digest proves the exact contents of a build, so you can tell whether two packages differ and verify a download.",
            ),
            homework=(
                "Write `manifest(files, version)` that returns a dictionary with the file count, the version and "
                "a sha256 digest of the sorted contents. Build it for two file sets, print both manifests, and "
                "comment which line makes the digest order independent."
            ),
            patterns=["def ", "hashlib", "print("],
            mapping=(
                "Every real build system produces a manifest with versions and hashes; package managers verify "
                "exactly this digest."
            ),
        ),
        177: dict(
            topic="Build day: performance pass",
            idea=(
                "A performance pass is measurement before action, because intuition about what is slow is wrong "
                "more often than right. The tool is a profile: a count of how often each function runs, or where "
                "the time goes, so you optimise the hot spot instead of the code that merely looks complicated. A "
                "classic result is that a small recursive function is called exponentially many times, and the "
                "fix is memoisation, caching each input's result so repeated calls are free. In the standard "
                "library that is functools.lru_cache, one decorator on a pure function. The trade is memory: the "
                "cache grows with the number of distinct inputs, so an unbounded cache on a large input set can "
                "exhaust memory, and a cache on a function whose result depends on mutable state returns stale "
                "answers. Measure again after the change, because a cache on a cold function only adds overhead. "
                "Today you count the real computations behind a recursive call with and without the cache, print "
                "both counts, and show that the second identical call does no new work. This is the same pattern "
                "behind cached pathfinding and AI lookups."
            ),
            code="""from functools import lru_cache

CALLS = {"n": 0}

@lru_cache(maxsize=None)
def fib(n):
    CALLS["n"] += 1
    return n if n < 2 else fib(n - 1) + fib(n - 2)

CALLS["n"] = 0
first = fib(20)
first_calls = CALLS["n"]
CALLS["n"] = 0
again = fib(20)
again_calls = CALLS["n"]
print("fib(20):", first, "computed in", first_calls, "calls")
print("second call used", again_calls, "new calls (cached)")
assert first == again == 6765 and again_calls == 0
print("memoisation trades memory for repeated work")
""",
            variant_b="measure a grid path counter with and without lru_cache and compare call counts",
            variant_c="lower the maxsize so the cache thrashes and explain the change in call count",
            mistakes=[
                "Optimising before measuring, so effort lands on code that was never slow.",
                "Caching a function whose result depends on mutable state, so answers go stale.",
                "Assuming a cache is free when memory can matter more than time.",
            ],
            q1=(
                "What does memoisation trade away to save time?",
                "Memory: it stores every distinct result, so a large or unbounded input set can grow without limit.",
            ),
            homework=(
                "Write `counted(n)` that uses functools.lru_cache to compute a recursive value while counting real "
                "computations in a dictionary, then call it twice. Print both call counts, and comment which line "
                "makes the second call free."
            ),
            patterns=["lru_cache", "def ", "print("],
            mapping=(
                "Profiling with cProfile then caching hot pure functions is standard practice on shipped games, "
                "especially for pathfinding and AI."
            ),
        ),
        178: dict(
            topic="Build day: final review",
            idea=(
                "A final review is a rerunnable checklist, not a feeling. The technique is to turn each release "
                "condition into a named check that returns pass or fail, collect them, and print the failures as a "
                "blocking list. Typical checks for a capstone are that a level loads, a fight resolves to a "
                "winner, the game runs offline with no missing assets, and a save round-trips. Group checks by "
                "severity so a cosmetic item does not block the release while a crash does, and run the same "
                "checklist on every candidate build so the standard never drifts. The value of writing them as a "
                "function is repeatability: a mental checklist misses something at midnight, while a script checks "
                "the same things every time. Keep each check small and independent, because one check that tests "
                "everything tells you little when it fails. This is the same discipline as the headless tests, "
                "applied at the level of the whole build rather than one rule. Today you write an audit function "
                "over a checklist, print the pass and fail counts with the blocking item, and assert which checks "
                "stop a release."
            ),
            code="""CHECKS = [
    ("one level loads", True),
    ("combat resolves", True),
    ("save/load round-trips", False),
    ("runs offline", True),
]

def audit(checks):
    passed = [name for name, ok in checks if ok]
    failed = [name for name, ok in checks if not ok]
    return passed, failed

passed, failed = audit(CHECKS)
print("passed:", len(passed), "failed:", len(failed))
for name in failed:
    print("blocking:", name)
assert failed == ["save/load round-trips"]
print("a review is a checklist you can rerun")
""",
            variant_b="add a check that runs one seeded game and fails if it raises",
            variant_c="make audit return the checks grouped by severity instead of pass and fail",
            mistakes=[
                "Reviewing only the happy path and never running the failing branch.",
                "Keeping a mental checklist instead of a rerunnable one.",
                "Blocking the release on a cosmetic item while a crash stays open.",
            ],
            q1=(
                "Why turn a review into a checklist function?",
                "A checklist that runs the checks is repeatable and objective, so the same standard applies to every candidate build.",
            ),
            homework=(
                "Write `release_ready(checks)` that takes (name, passed) pairs and returns the list of blocking "
                "failures. Feed it one build with a failing check and one clean build, print both verdicts, and "
                "comment which line decides blocking."
            ),
            patterns=["def ", "return", "print("],
            mapping=(
                "This is a ship gate or a QA checklist; studios automate it as smoke tests that must pass before "
                "a build is published."
            ),
        ),
        179: dict(
            topic="Ship: retrospective and next steps",
            idea=(
                "Shipping a capstone ends with a retrospective, and its job is to convert what actually happened "
                "into a smaller, sharper plan for the next project. The input is a few honest numbers: features "
                "planned, features finished, hours spent and open bugs. From those you compute a completion ratio, "
                "the ratio of finished to planned work, and a short ranked list of next steps that puts open bugs "
                "ahead of unfinished scope, because a shipped thing with a known crash is worth less than a "
                "smaller thing that runs. The technique is to make this a function of the stats dictionary rather "
                "than a paragraph, so the same summary can be regenerated as numbers change and so the ordering "
                "rule is explicit and reviewable. A retrospective that only lists what went well teaches nothing; "
                "the useful output is the process change, such as scoping the next milestone smaller or writing "
                "the done condition earlier. Resist counting features started, which flatters a stalled project, "
                "and count only what shipped. Today you summarise a stats dictionary, print the completion ratio "
                "and the ordered next steps, and assert the first step targets the open bug."
            ),
            code="""STATS = {
    "planned": 6,
    "shipped": 5,
    "open_bugs": 1,
    "hours": 40,
}

def retro(stats):
    rate = stats["shipped"] / stats["planned"]
    next_steps = []
    if stats["open_bugs"]:
        next_steps.append("fix open bugs before new features")
    if rate < 1.0:
        next_steps.append("scope the next milestone smaller")
    return round(rate, 2), next_steps

rate, steps = retro(STATS)
print("completion:", rate)
for step in steps:
    print("next:", step)
assert rate == 0.83 and steps[0].startswith("fix")
print("a retrospective turns numbers into the next milestone")
""",
            variant_b="add cycle time in days per shipped feature and print it beside completion",
            variant_c="rank open bugs by severity and list the top one as the first next step",
            mistakes=[
                "Counting features started rather than features finished.",
                "Listing next steps without naming who does them or when.",
                "Skipping the retrospective and repeating the same scope mistake.",
            ],
            q1=(
                "What is the point of a retrospective if the project shipped?",
                "It converts what happened into a smaller, sharper plan for the next milestone, so the same mistakes are not repeated.",
            ),
            homework=(
                "Write `summarise(stats)` that returns the completion ratio and a list of next steps ordered by "
                "open bugs then unfinished scope. Run it on two stat dictionaries, print both summaries, and "
                "comment which line chooses the first next step."
            ),
            patterns=["def ", "return", "print("],
            mapping=(
                "Studios run a post-mortem after every milestone; the output is a short list of process changes "
                "that feed the next sprint."
            ),
        ),
    },
)
