"""Game Development foundations, days 9-14: the vocabulary the domain phases build on.

Every example is stdlib-only, offline and deterministic (fixed seeds, no clock),
so the applier can execute it and produce the same output on every run. The
domain phases keep the same discipline: one idea, a runnable fixture, and a
homework function the learner adapts.
"""

FOUNDATION = {
    9: dict(
        topic="Game state is data",
        idea=(
            "A game is a program that keeps changing a world model, and the first design decision is what that "
            "world model looks like. If the state lives in scattered variables and closures, every new feature "
            "touches every corner of the code. If it lives in one explicit structure — a dictionary or a small "
            "class — then update, render, save and test all read from the same source of truth. The classic "
            "split is between static data (level layout, item tables) and dynamic state (positions, health, "
            "score), with the dynamic part being what the loop rewrites each tick. Naming that split early pays "
            "off because save files are just serialised state, replays are recorded inputs against "
            "deterministic state, and bugs are usually a mismatch between what the code thinks the state is "
            "and what it actually is. Today you build one player as a dataclass and print it, then mutate a "
            "copy. The important habit is to treat state as a value you can inspect, copy and compare, not as "
            "an invisible context that functions reach into. Once state is data, you can write a test that "
            "sets up a world, runs one tick, and asserts the result."
        ),
        code=(
            'from dataclasses import dataclass, replace\n'
            '\n'
            '@dataclass(frozen=True)\n'
            'class Player:\n'
            '    name: str\n'
            '    hp: int\n'
            '    x: int\n'
            '    y: int\n'
            '\n'
            'hero = Player("Ada", hp=10, x=3, y=4)\n'
            'print("start:", hero)\n'
            '\n'
            'hurt = replace(hero, hp=hero.hp - 3)\n'
            'print("after hit:", hurt.hp, "at", (hurt.x, hurt.y))\n'
            'print("original unchanged:", hero.hp)\n'
            '\n'
            'assert hero.hp == 10 and hurt.hp == 7\n'
            'assert hurt == Player("Ada", 7, 3, 4)\n'
            'print("state is a value you can copy and compare")'
        ),
        variant_b='add a "coins: int = 0" field and print two players that differ only in coins',
        variant_c='mutate a non-frozen dataclass in place and explain when mutation is the better choice',
        mistakes=[
            "Spreading player state across loose variables so no single object can be saved or compared.",
            "Mutating shared state in place when the caller expected a copy.",
            "Storing derived values such as is_alive instead of computing them from hp.",
        ],
        q1=(
            "Why is a frozen dataclass a good default for game state?",
            "An immutable value can be copied, compared and serialised without hidden aliases, and every change becomes an explicit new state.",
        ),
        homework=(
            "Write `damage(player, amount)` that returns a new player with reduced hp, never below zero. Call "
            "it on two different players, print both before and after, and comment which line keeps the "
            "original state untouched."
        ),
        patterns=["@dataclass", "return", "print("],
        mapping=(
            "Engines from pygame to Godot all expose an entity object you read and write; keeping that object "
            "plain data is what lets you snapshot, replay and debug a run."
        ),
    ),
    10: dict(
        topic="One function per rule",
        idea=(
            "Game rules should be functions with a narrow contract: state in, new state out. A rule such as "
            "`apply_damage(state, target, amount)` does not draw, does not read the keyboard and does not know "
            "which scene is active. Keeping rules pure makes them testable with a fixture state, reusable from "
            "an AI controller and a network replay, and replaceable when the design changes. The alternative — "
            "rules tangled into the input handler and the renderer — is the single most common reason small "
            "games become impossible to change. Separating update from render matters for the same reason. "
            "Update decides what the world is now; render decides how it looks. If update writes directly to "
            "the screen, you cannot run it headless in a test, and you cannot speed it up without changing "
            "behaviour. Today you write two pure rule functions and call them in sequence, printing the state "
            "after each step. Notice that the functions return a new state rather than editing a global. That "
            "choice is what makes the turn loop in later lessons straightforward: each action is a function, "
            "and the loop is only about ordering."
        ),
        code=(
            'def apply_damage(state, target, amount):\n'
            '    new_hp = max(0, state[target]["hp"] - amount)\n'
            '    updated = {name: dict(body) for name, body in state.items()}\n'
            '    updated[target]["hp"] = new_hp\n'
            '    return updated\n'
            '\n'
            'def is_alive(state, name):\n'
            '    return state[name]["hp"] > 0\n'
            '\n'
            'world = {"hero": {"hp": 10}, "slime": {"hp": 4}}\n'
            'world = apply_damage(world, "slime", 5)\n'
            'print("slime hp:", world["slime"]["hp"], "| alive:", is_alive(world, "slime"))\n'
            'world = apply_damage(world, "hero", 3)\n'
            'print("hero hp:", world["hero"]["hp"], "| alive:", is_alive(world, "hero"))\n'
            'assert not is_alive(world, "slime") and is_alive(world, "hero")\n'
            'print("rules are pure functions over state")'
        ),
        variant_b='add a heal rule that never exceeds a max_hp field stored in the state',
        variant_c='make apply_damage mutate the dictionary in place and explain what breaks in replay',
        mistakes=[
            "Printing or drawing inside a rule, so it cannot run headless in a test.",
            "Reaching for a global player instead of taking the state as a parameter.",
            "Letting a rule return None and editing state through a side effect.",
        ],
        q1=(
            "Why should a game rule return new state instead of editing state in place?",
            "Returning state makes the rule a testable value transformation and lets you keep the previous state for replays or undo.",
        ),
        homework=(
            "Write `heal(state, target, amount, max_hp)` that returns new state with hp capped at max_hp. Apply "
            "it to two different starting values, print the resulting hp for each, and comment which line "
            "enforces the cap."
        ),
        patterns=["def ", "return", "print("],
        mapping=(
            "An AI controller and a human controller should both call the same rule functions; only the source "
            "of the chosen action differs."
        ),
    ),
    11: dict(
        topic="The fixed-step game loop",
        idea=(
            "A game loop is a small scheduler: read input, update the world by one fixed step, render, repeat. "
            "Choosing a fixed step matters because variable timesteps make physics depend on frame rate and "
            "make runs hard to reproduce. With a fixed step, a tick always means the same amount of simulated "
            "time, so a replay of the same inputs produces the same result regardless of how fast the machine "
            "is. Real engines accumulate elapsed real time and run zero or more fixed steps per frame to catch "
            "up, which is why a laggy frame can advance the world twice. Today you simulate the loop without a "
            "clock: run exactly three ticks, print the state after each, and stop on a condition such as the "
            "hero dying. This is the shape every later lesson builds on, from collision to pathfinding. Notice "
            "that update never draws, and the loop never contains game rules; it only decides how many times "
            "the update runs. That separation is what lets you run the same simulation headless, faster than "
            "real time, to test balance or train an AI."
        ),
        code=(
            'def step(state):\n'
            '    state = dict(state)\n'
            '    state["tick"] = state["tick"] + 1\n'
            '    state["energy"] = max(0, state["energy"] - 2)\n'
            '    return state\n'
            '\n'
            'def finished(state):\n'
            '    return state["energy"] == 0\n'
            '\n'
            'world = {"tick": 0, "energy": 5}\n'
            'while not finished(world) and world["tick"] < 3:\n'
            '    world = step(world)\n'
            '    print("tick", world["tick"], "energy", world["energy"])\n'
            '\n'
            'assert world["tick"] == 3 and world["energy"] == 0\n'
            'print("loop ran a fixed number of steps")'
        ),
        variant_b='raise energy to 9 and count how many ticks run before it reaches zero',
        variant_c='add a "paused" flag that skips stepping while still incrementing a frame counter',
        mistakes=[
            "Putting rendering or input handling inside the update step.",
            "Using a variable timestep, so behaviour changes with machine speed.",
            "Looping forever without a termination or tick-budget condition.",
        ],
        q1=(
            "Why is a fixed timestep easier to reproduce than a variable one?",
            "Each tick simulates the same amount of time, so the same inputs yield the same state trajectory regardless of frame rate.",
        ),
        homework=(
            "Write `run_ticks(state, n)` that steps a state dictionary n times and returns the final state plus "
            "the list of states seen. Run it with two tick counts on the same start, print both histories, and "
            "comment which line bounds the loop."
        ),
        patterns=["while ", "def ", "print("],
        mapping=(
            "pygame's clock.tick(fps) and Godot's _process/_physics_process split are both this loop; the "
            "fixed physics step is what keeps replays and tests stable."
        ),
    ),
    12: dict(
        topic="Randomness with a seed",
        idea=(
            "Games need randomness — damage rolls, loot, spawn positions — but a game that cannot reproduce a "
            "bug is a game that cannot be balanced. The standard answer is a seeded pseudo-random generator: "
            "create one generator with a known seed, and every draw from it is a deterministic sequence. Two "
            "runs with the same seed produce the same results, so a replay can be stored as a seed plus the "
            "player's inputs rather than a recording of the whole world. A critical rule follows: never call a "
            "global random function from deep inside game rules, because then the outcome depends on every "
            "other caller and cannot be replayed in isolation. Pass the generator explicitly, or keep the seed "
            "in the save file. Seeds also make tests honest: a test can pin a seed and assert the exact loot "
            "table, while a balance test can run a thousand seeds and look at the distribution. Today you "
            "create one seeded generator, draw a few numbers, and prove that a second generator with the same "
            "seed reproduces them exactly. This determinism is what later makes replays, AI training and "
            "regression tests possible."
        ),
        code=(
            'import random\n'
            '\n'
            'def roll_damage(rng, count):\n'
            '    return [rng.randint(1, 6) for _ in range(count)]\n'
            '\n'
            'first = roll_damage(random.Random(42), 5)\n'
            'second = roll_damage(random.Random(42), 5)\n'
            'different = roll_damage(random.Random(7), 5)\n'
            '\n'
            'print("seed 42:", first)\n'
            'print("seed 42 again:", second)\n'
            'print("seed 7:", different)\n'
            '\n'
            'assert first == second\n'
            'assert first != different\n'
            'print("same seed, same sequence")'
        ),
        variant_b='draw ten rolls from seed 42 and print how many are sixes',
        variant_c='use one shared generator for two rolls in a row and explain why order matters',
        mistakes=[
            "Calling module-level random functions, so the sequence depends on unrelated callers.",
            "Forgetting to store the seed in the save file, making a run impossible to reproduce.",
            "Assuming a seeded generator is random enough for security; it is for games, not secrets.",
        ],
        q1=(
            "Why store the seed instead of the whole random sequence in a save file?",
            "The seed regenerates the entire sequence deterministically, so the save stays small and the run replays identically.",
        ),
        homework=(
            "Write `loot_table(seed, rolls)` that creates one generator, draws the given number of items from a "
            "fixed list, and returns the list. Call it twice with the same seed and once with a different one, "
            "print all three, and comment which line makes the run reproducible."
        ),
        patterns=["random.Random", "def ", "print("],
        mapping=(
            "Most engines let you seed their RNG; storing that seed alongside recorded inputs is how speedrun "
            "replays and automated tests stay deterministic."
        ),
    ),
    13: dict(
        topic="Collision and coordinates",
        idea=(
            "Collision detection is geometry with a performance budget. For rectangles, the test is four "
            "comparisons: two boxes overlap unless one is entirely left, right, above or below the other. For "
            "circles, it is a distance comparison, and comparing squared distances avoids a square root. The "
            "concept worth internalising is that collision is a query over positions, and the answer should be "
            "a boolean or a description, not a side effect. Detect and resolve are separate steps: detection "
            "answers whether the boxes touch, resolution decides how to push them apart. Mixing the two makes "
            "physics unpredictable, because the order in which objects are processed changes the outcome. "
            "Coordinates also need a convention: is y down or up, and what is the origin? Pick one, write it "
            "down, and never mix it. Today you write an axis-aligned bounding-box overlap test and check it "
            "against a few cases, including touching edges and containment. Touching edges are the classic "
            "off-by-one: decide whether contact counts as a collision and stay consistent, because the same "
            "choice will matter again when you resolve overlaps."
        ),
        code=(
            'def boxes_overlap(a, b):\n'
            '    ax, ay, aw, ah = a\n'
            '    bx, by, bw, bh = b\n'
            '    return ax < bx + bw and bx < ax + aw and ay < by + bh and by < ay + ah\n'
            '\n'
            'player = (0, 0, 10, 10)\n'
            'cases = {\n'
            '    "overlap": (5, 5, 10, 10),\n'
            '    "apart": (20, 20, 4, 4),\n'
            '    "touching edge": (10, 0, 5, 5),\n'
            '    "inside": (2, 2, 3, 3),\n'
            '}\n'
            'for label, box in cases.items():\n'
            '    print(label, "->", boxes_overlap(player, box))\n'
            '\n'
            'assert boxes_overlap(player, (5, 5, 10, 10))\n'
            'assert not boxes_overlap(player, (10, 0, 5, 5))\n'
            'print("AABB overlap tested on edges and containment")'
        ),
        variant_b='write `boxes_touch` that counts edge contact as a collision, using <= instead of <',
        variant_c='represent a circle as (x, y, r) and compare squared distances to a box centre',
        mistakes=[
            "Using <= so touching edges count as overlap without deciding that it should.",
            "Resolving the collision inside the detection function, making order of processing matter.",
            "Mixing coordinate systems, so the y axis points the wrong way in half the code.",
        ],
        q1=(
            "Why compare squared distances for circle collisions instead of distances?",
            "It avoids a square root, and the comparison result is identical because squaring is monotonic for non-negative distances.",
        ),
        homework=(
            "Write `overlaps_any(box, boxes)` that returns the indices of every box overlapping the first. Test "
            "it on a list with one overlap, one touching edge and one clear box, print the indices, and comment "
            "which comparison decides the edge case."
        ),
        patterns=["def ", "return", "print("],
        mapping=(
            "Engines call this broad-phase collision; the same rectangles feed later spatial partitioning such "
            "as a grid or quadtree when the object count grows."
        ),
    ),
    14: dict(
        topic="A tiny game, end to end",
        idea=(
            "Today you connect the pieces into a turn-based fight: state as data, rules as pure functions, a "
            "loop that alternates turns, seeded randomness for damage, and a clear win condition. It is small, "
            "but it has the full skeleton of a game. The hero attacks, the slime retaliates, the loop checks "
            "for a winner and prints a readable log. Because every part is deterministic, the same seed and the "
            "same starting state always produce the same battle, which means the whole thing can be tested by "
            "asserting on the outcome rather than on the text. Notice the responsibilities: the rules decide "
            "damage, the loop decides order, and printing is a thin presentation layer that could be replaced "
            "by a different renderer without touching the logic. That separation is exactly what you will keep "
            "when the presentation becomes a real window. The win condition is checked after every action, "
            "never inside a rule, so the rules stay reusable. If the battle ever fails to end, that is a bug in "
            "the loop's termination condition, not in the damage rules. Build the skeleton here and the rest of "
            "the track is adding systems to it."
        ),
        code=(
            'import random\n'
            '\n'
            'def attack(attacker, defender, rng):\n'
            '    damage = rng.randint(1, 6)\n'
            '    defender = dict(defender)\n'
            '    defender["hp"] = max(0, defender["hp"] - damage)\n'
            '    return defender, damage\n'
            '\n'
            'def battle(seed):\n'
            '    rng = random.Random(seed)\n'
            '    hero = {"name": "hero", "hp": 12}\n'
            '    slime = {"name": "slime", "hp": 8}\n'
            '    turn = 0\n'
            '    log = []\n'
            '    while hero["hp"] > 0 and slime["hp"] > 0:\n'
            '        attacker, defender = (hero, slime) if turn % 2 == 0 else (slime, hero)\n'
            '        defender, damage = attack(attacker, defender, rng)\n'
            '        if attacker is hero:\n'
            '            slime = defender\n'
            '        else:\n'
            '            hero = defender\n'
            '        log.append(f"t{turn} {attacker[\'name\']} hits for {damage} -> {hero[\'hp\']}/{slime[\'hp\']}")\n'
            '        turn += 1\n'
            '    return ("hero" if slime["hp"] == 0 else "slime"), turn, log\n'
            '\n'
            'winner, turns, log = battle(42)\n'
            'for line in log:\n'
            '    print(line)\n'
            'print("winner:", winner, "in", turns, "turns")\n'
            'assert winner == battle(42)[0]\n'
            'print("same seed, same battle")'
        ),
        variant_b='give the hero 20 hp and rerun seed 42 — does the winner change?',
        variant_c='add a heal action every third turn and explain which function should own it',
        mistakes=[
            "Checking the win condition inside the damage rule instead of the loop.",
            "Rebuilding the RNG every turn, so damage is no longer part of one reproducible sequence.",
            "Letting the log decide game state instead of observing it.",
        ],
        q1=(
            "Why can this battle be asserted on without checking its printed text?",
            "The result is a value returned by a deterministic function of the seed, so tests compare outcomes rather than log strings.",
        ),
        homework=(
            "Write `simulate(seed, hero_hp, slime_hp)` that runs the fight and returns the winner and turn "
            "count. Run it on two seeds and two hp pairs, print every result, and comment which line makes the "
            "loop terminate."
        ),
        patterns=["def ", "while ", "random.Random"],
        mapping=(
            "This is the same loop and rule split a real engine runs; replacing print with a renderer and "
            "rng.randint with input is the entire difference."
        ),
    ),
}
