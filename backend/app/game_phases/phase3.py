"""Game logic, days 105-119: rules, turns, maths and machine opponents.

Every example is stdlib-only, offline and deterministic (fixed seeds, no clock),
so the applier can execute it and compare outputs across runs. Rules stay pure
functions over plain dicts and ints; printing is only the presentation layer.
"""

PHASE = ("Rules, Turns and Game Logic", "Turn rules, numbers and opponents into small pure functions that any loop or test can drive.", {
    105: dict(
        topic="Orientation: rules as functions",
        idea=(
            "A game rule is a promise about how state changes, and the cleanest way to keep that promise is a "
            "pure function: state in, new state out, no drawing and no hidden globals. Once a rule has that "
            "shape you can call it from the turn loop, from a test, from a replay viewer or from an AI planner "
            "without changing a line. The example separates three small rules: is a unit alive, can it act, and "
            "what happens when it takes damage. Each one reads only its parameters and returns a value, so the "
            "order in which you call them is explicit in the caller rather than buried in shared variables. "
            "Notice that damage clamps at zero: a rule should encode the domain constraint, not leave negative "
            "health for later code to trip over. Notice also that the stunned flag is queried, not mutated, "
            "because acting and being able to act are different questions. When rules are this small, the game "
            "loop becomes ordinary code that sequences them and checks endings. The habit to build today is to "
            "ask of every new mechanic: what is its input state, what is its output state, and what does it "
            "deliberately not know about? If the answer mentions the screen or the keyboard, the rule is doing "
            "too much and belongs in two pieces."
        ),
        code=(
            'def is_alive(unit):\n'
            '    return unit["hp"] > 0\n'
            '\n'
            'def can_act(state, name):\n'
            '    unit = state[name]\n'
            '    return is_alive(unit) and not unit.get("stunned", False)\n'
            '\n'
            'def apply_damage(state, target, amount):\n'
            '    updated = {name: dict(unit) for name, unit in state.items()}\n'
            '    updated[target]["hp"] = max(0, updated[target]["hp"] - amount)\n'
            '    return updated\n'
            '\n'
            'world = {"hero": {"hp": 10}, "slime": {"hp": 3, "stunned": True}}\n'
            'print("slime can act:", can_act(world, "slime"))\n'
            'world = apply_damage(world, "slime", 5)\n'
            'print("slime hp:", world["slime"]["hp"])\n'
            'print("slime can act:", can_act(world, "slime"))\n'
            'assert can_act(world, "hero") and not can_act(world, "slime")\n'
            'print("rules are pure state -> state functions")'
        ),
        variant_b='add a "shield" field that absorbs the first three points of damage before hp changes',
        variant_c='write a rule that returns whether a unit may move, and call it from a two-unit state',
        mistakes=[
            "Printing inside a rule, so the same rule cannot run headless in a test.",
            "Reading a global player object instead of taking the state as a parameter.",
            "Letting hp go negative and expecting every later rule to remember to clamp it.",
        ],
        q1=(
            "What makes a game rule a pure function?",
            "It takes all the state it needs as parameters, returns a new value, and changes nothing outside itself.",
        ),
        homework=(
            "Write `can_act(state, name)` that returns False for a dead or stunned unit and True otherwise. Build "
            "a state with one healthy and one stunned unit, print the result for both, and comment which part of "
            "the expression enforces each condition."
        ),
        patterns=["def can_act", "return", "print("],
        mapping=(
            "Engine scripts usually become reusable when the rule lives in a system or helper that reads and "
            "returns data, while the scene layer only presents the result."
        ),
    ),
    106: dict(
        topic="Turn order and initiative",
        idea=(
            "Turn order looks trivial until two units roll the same initiative. The rule you want is a total "
            "order, not a partial one: compare initiative first, then a stable tie-breaker such as name, so the "
            "same roster always produces the same sequence. That determinism matters for replays, for tests and "
            "for debugging a battle that went wrong. The natural implementation is a sort key of negative "
            "initiative plus the tie-breaker, because Python sorts ascending and you want the highest initiative "
            "first. Resist the urge to sort a list of mutable unit dictionaries in place and then read their "
            "order later; return a fresh list of names instead, so the roster and the schedule stay separate "
            "values. Round rotation is a second, simpler rule: drop the first name and append it to the end. "
            "Keeping that as a function means a fast unit with two actions per round, or a stun that skips a "
            "turn, can be added later without rewriting the loop. Today you print the order for a mixed party, "
            "rotate one round, and assert the tie-break, which is the case most likely to be wrong in a real "
            "implementation. A total order is a small contract that saves a lot of confusing behaviour."
        ),
        code=(
            'def turn_order(units):\n'
            '    ranked = sorted(units.items(), key=lambda item: (-item[1]["initiative"], item[0]))\n'
            '    return [name for name, _unit in ranked]\n'
            '\n'
            'def rotate(order):\n'
            '    return order[1:] + order[:1]\n'
            '\n'
            'units = {\n'
            '    "hero": {"initiative": 12},\n'
            '    "rogue": {"initiative": 15},\n'
            '    "slime": {"initiative": 12},\n'
            '    "boss": {"initiative": 8},\n'
            '}\n'
            'order = turn_order(units)\n'
            'print("this round:", order)\n'
            'print("next round:", rotate(order))\n'
            'assert order == ["rogue", "hero", "slime", "boss"]\n'
            'assert turn_order(units) == order\n'
            'print("ties break by name, so the order is repeatable")'
        ),
        variant_b='give the slime initiative 15 and print the new order, noting which name breaks the tie',
        variant_c='add a "stunned" flag and filter stunned units out before building the order',
        mistakes=[
            "Sorting only by initiative, so equal values fall back to dictionary insertion order.",
            "Mutating the roster list while sorting and losing the original party order.",
            "Forgetting that Python sorts ascending and putting the slowest unit first.",
        ],
        q1=(
            "Why add a name tie-breaker to an initiative sort?",
            "It turns a partial order into a total one, so equal initiative values still produce the same repeatable sequence.",
        ),
        homework=(
            "Write `turn_order(units)` that returns names sorted by highest initiative and breaks ties "
            "alphabetically. Call it on a roster with two equal initiatives, print the order twice, and comment "
            "which part of the key makes the result stable."
        ),
        patterns=["def turn_order", "sorted(", "print("],
        mapping=(
            "Tabletop engines and tactics games expose initiative as a sortable stat, and replay tools depend on "
            "the tie-break being deterministic."
        ),
    ),
    107: dict(
        topic="Actions as small commands",
        idea=(
            "When every action is a branch in the turn loop, the loop grows without bound and every new ability "
            "edits the same function. The command pattern fixes this by making an action a small data value: a "
            "kind plus its parameters. Input, AI and replay all produce the same command dictionaries, and one "
            "dispatcher decides what each kind means. The loop then only sequences commands and checks endings. "
            "This separation has three practical benefits. First, a command can be logged, serialised or sent "
            "over a network because it is plain data. Second, an AI can search over candidate commands without "
            "calling any game code. Third, validation lives in one place: an unknown kind raises immediately "
            "instead of silently doing nothing. In the example the dispatcher copies the state before editing "
            "it, so the caller keeps the previous world for undo or replay. The dispatcher is still a chain of "
            "if statements, and that is fine at this scale; a dictionary of handlers is the next step when the "
            "list grows. The important boundary is that commands describe intent, while rules decide effects. "
            "A command says attack the slime; the dispatcher and the damage rule decide what that costs and "
            "whether it lands. Keep that boundary and new actions become additive."
        ),
        code=(
            'def make_action(kind, **payload):\n'
            '    return {"kind": kind, **payload}\n'
            '\n'
            'def apply_action(state, action):\n'
            '    updated = {name: dict(unit) for name, unit in state.items()}\n'
            '    kind = action["kind"]\n'
            '    if kind == "move":\n'
            '        updated["hero"]["x"] += action["dx"]\n'
            '    elif kind == "attack":\n'
            '        target = action["target"]\n'
            '        updated[target]["hp"] = max(0, updated[target]["hp"] - 3)\n'
            '    else:\n'
            '        raise ValueError("unknown action: " + kind)\n'
            '    return updated\n'
            '\n'
            'world = {"hero": {"hp": 10, "x": 0}, "slime": {"hp": 6}}\n'
            'commands = [make_action("move", dx=2), make_action("attack", target="slime")]\n'
            'for command in commands:\n'
            '    world = apply_action(world, command)\n'
            '    print(command["kind"], "-> x", world["hero"]["x"], "slime hp", world["slime"]["hp"])\n'
            'assert world["slime"]["hp"] == 3\n'
            'print("commands are data; the dispatcher owns the effects")'
        ),
        variant_b='add a "wait" command that changes nothing and print the state before and after it',
        variant_c='replace the if chain with a dictionary mapping kind to a handler function',
        mistakes=[
            "Putting the effect of every action directly in the turn loop instead of a dispatcher.",
            "Passing a live state object into the dispatcher and editing it in place.",
            "Ignoring unknown action kinds, so a typo silently consumes a turn.",
        ],
        q1=(
            "Why represent an action as a dictionary instead of calling a function immediately?",
            "A data value can be logged, validated, replayed or scored by an AI before anything is applied.",
        ),
        homework=(
            "Write `apply_action(state, action)` supporting move and attack commands over a state dictionary. "
            "Build a list of two commands, apply them in order, print the state after each, and comment which "
            "line rejects an unknown command kind."
        ),
        patterns=["def apply_action", "raise", "print("],
        mapping=(
            "Networked games and replay systems send input as commands for exactly this reason: the same message "
            "can drive a local session, a server tick or a recorded match."
        ),
    ),
    108: dict(
        topic="Inventory and item models",
        idea=(
            "An inventory is two different things that are easy to confuse: the static definition of an item and "
            "the dynamic count a player owns. The catalog holds weight, value and stack rules; the inventory is "
            "just a mapping from item name to count. Splitting them means a balance change edits the catalog and "
            "does not touch save data, and a save file stores counts rather than copies of every item definition. "
            "With that split, the useful operations are small: add a count, remove a count without going "
            "negative, and compute total weight from the catalog. Removal needs a real decision when the count "
            "would drop below zero: clamp at zero, or refuse the operation. Clamping is friendlier for a quick "
            "prototype, but refusing is safer for trade and crafting, where a duplicated item is an exploit. "
            "Total weight should be derived, never stored alongside the counts, because the two will drift the "
            "moment one path forgets to update the other. The example adds a stack of potions and a sword, prints "
            "the derived weight, then drops one sword and shows the count reaching zero. Stacking is just "
            "counting, and capacity is just a comparison against the derived weight. Keep those as functions and "
            "the UI can preview a pickup without mutating the real bag."
        ),
        code=(
            'def add_item(inventory, item, count=1):\n'
            '    bag = dict(inventory)\n'
            '    bag[item] = bag.get(item, 0) + count\n'
            '    return bag\n'
            '\n'
            'def total_weight(inventory, catalog):\n'
            '    return sum(catalog[name]["weight"] * count for name, count in inventory.items())\n'
            '\n'
            'catalog = {\n'
            '    "potion": {"weight": 1, "value": 5},\n'
            '    "sword": {"weight": 4, "value": 30},\n'
            '    "rope": {"weight": 2, "value": 8},\n'
            '}\n'
            'bag = {}\n'
            'for item in ["potion", "potion", "sword"]:\n'
            '    bag = add_item(bag, item)\n'
            'print("bag:", sorted(bag.items()))\n'
            'print("weight:", total_weight(bag, catalog), "/ 8")\n'
            'bag = add_item(bag, "sword", -1)\n'
            'print("swords left:", bag["sword"])\n'
            'assert total_weight(bag, catalog) == 2\n'
            'print("inventory counts live apart from the item catalog")'
        ),
        variant_b='add a rope and print whether the total weight still fits a capacity of eight',
        variant_c='make add_item refuse to go below zero and return a success flag alongside the bag',
        mistakes=[
            "Storing weight inside each inventory entry instead of deriving it from the catalog.",
            "Letting a count go negative, which turns a drop into a silent duplication.",
            "Copying whole item definitions into save data so balance edits no longer apply.",
        ],
        q1=(
            "Why keep item definitions in a catalog instead of inside the inventory?",
            "The inventory only needs counts, while the catalog owns stats, so balance changes and save files stay independent.",
        ),
        homework=(
            "Write `total_weight(inventory, catalog)` that sums weight times count and returns an int. Test it on "
            "an empty bag, a stacked potion bag and a bag with one heavy sword, print all three weights, and "
            "comment which line derives the value instead of storing it."
        ),
        patterns=["def total_weight", "sum(", "print("],
        mapping=(
            "Most engines split item assets from per-character inventories for the same reason: assets are "
            "shared content, counts are save state."
        ),
    ),
    109: dict(
        topic="Combat resolution maths",
        idea=(
            "Combat maths is where a game's feel is decided, and the temptation is to hide the numbers inside a "
            "long expression. Instead, split the calculation into named steps: hit chance, the roll, the damage "
            "formula and the floor. Each step is a function or a clearly named value, so a designer can ask what "
            "happens at extreme accuracy without reading the whole attack. Hit chance is usually accuracy minus "
            "evasion added to a base, then clamped: below five percent nothing ever lands and above ninety-five "
            "nothing ever misses, which makes fights feel broken at the edges. The roll is compared to that "
            "chance, and the random generator is passed in rather than created inside, so a seed still controls "
            "the whole battle. Damage is power minus half armour, floored at one so a hit always matters, and a "
            "critical multiplies the result. Order matters here: flooring after the critical gives different "
            "numbers from flooring before it, and you must pick one and write it down. The example prints the "
            "roll, the chance and the damage for three turns, which is enough to see the formula working without "
            "a spreadsheet. Later, when balance feels wrong, these named pieces are the dials you turn."
        ),
        code=(
            'import random\n'
            '\n'
            'def hit_chance(attacker, defender):\n'
            '    raw = 60 + attacker["accuracy"] - defender["evasion"]\n'
            '    return max(5, min(95, raw))\n'
            '\n'
            'def resolve(attacker, defender, rng):\n'
            '    chance = hit_chance(attacker, defender)\n'
            '    roll = rng.randint(1, 100)\n'
            '    if roll > chance:\n'
            '        return 0, roll, chance\n'
            '    critical = rng.randint(1, 100) <= attacker["crit"]\n'
            '    damage = attacker["power"] - defender["armor"] // 2\n'
            '    if critical:\n'
            '        damage *= 2\n'
            '    return max(1, damage), roll, chance\n'
            '\n'
            'hero = {"power": 12, "accuracy": 20, "crit": 25}\n'
            'goblin = {"evasion": 10, "armor": 6}\n'
            'rng = random.Random(7)\n'
            'for turn in range(3):\n'
            '    damage, roll, chance = resolve(hero, goblin, rng)\n'
            '    print(f"turn {turn}: roll {roll} vs {chance} -> {damage} damage")\n'
            'assert hit_chance(hero, goblin) == 70\n'
            'print("chance is clamped and damage is floored at one")'
        ),
        variant_b='raise armour to 30 and print the damage, then explain why the floor at one matters',
        variant_c='roll the critical check before the hit check and describe how the distribution changes',
        mistakes=[
            "Creating a new RNG inside the attack function, so one seed no longer controls the battle.",
            "Leaving hit chance unclamped, so some units can never hit or never miss.",
            "Choosing floor-before-critical and floor-after-critical in different abilities.",
        ],
        q1=(
            "Why pass the random generator into the combat function?",
            "One seeded generator keeps the whole battle reproducible and prevents unrelated callers from changing the sequence.",
        ),
        homework=(
            "Write `expected_damage(attacker, defender)` that returns hit chance as a fraction times average "
            "damage, ignoring criticals. Compare two defenders with different armour, print both values, and "
            "comment which term makes armour matter."
        ),
        patterns=["def expected_damage", "return", "print("],
        mapping=(
            "Combat designers usually keep hit chance and damage in tunable data tables, with the code only "
            "applying the named steps in a fixed order."
        ),
    ),
    110: dict(
        topic="Stats, modifiers and leveling",
        idea=(
            "A stat system has three layers and mixing them causes most of the bugs. The base stat is what the "
            "character is. Modifiers are temporary or external changes: a buff, a curse, a piece of gear. The "
            "effective stat is what the rules actually use, recomputed from the other two. If you write the "
            "effective value back into the base, a buff that expires leaves a permanent change, and stacking two "
            "buffs can double-apply. Keep base and modifiers separate, and make the total a pure function with a "
            "floor of one. Leveling is a separate loop over experience thresholds: while xp exceeds the cost of "
            "the current level, subtract that cost, raise the level and raise the base stats. The while loop, not "
            "an if, is what lets a single large reward grant several levels at once; an if silently swallows the "
            "overflow. Thresholds should grow with level, usually linearly or quadratically, so early levels "
            "arrive quickly and later ones take longer. The example grants one big reward, prints the resulting "
            "level and leftover xp, then computes power from base plus a positive and a negative modifier. "
            "Notice that the modifier is passed at read time and never stored on the hero. That is the habit "
            "that keeps equipment, buffs and level-ups from fighting each other."
        ),
        code=(
            'def total_stat(base, modifiers):\n'
            '    return max(1, base + sum(modifiers))\n'
            '\n'
            'def xp_for_level(level):\n'
            '    return 100 * level\n'
            '\n'
            'def grant_xp(hero, amount):\n'
            '    hero = dict(hero)\n'
            '    hero["xp"] += amount\n'
            '    while hero["xp"] >= xp_for_level(hero["level"]):\n'
            '        hero["xp"] -= xp_for_level(hero["level"])\n'
            '        hero["level"] += 1\n'
            '        hero["base_power"] += 2\n'
            '    return hero\n'
            '\n'
            'hero = {"level": 1, "xp": 0, "base_power": 8}\n'
            'hero = grant_xp(hero, 350)\n'
            'power = total_stat(hero["base_power"], [3, -1])\n'
            'print("level:", hero["level"], "xp left:", hero["xp"])\n'
            'print("base power:", hero["base_power"], "with modifiers:", power)\n'
            'assert hero["level"] == 3 and hero["xp"] == 50 and power == 14\n'
            'print("leveling loops over thresholds; modifiers stay outside the base")'
        ),
        variant_b='grant 90 xp instead and print the level, showing that no threshold was crossed',
        variant_c='add a multiplier modifier and explain why recomputing the total is safer than caching it',
        mistakes=[
            "Writing buffed stats back into the base, so expired buffs leave permanent boosts.",
            "Using an if instead of a while for leveling, which drops overflow experience.",
            "Caching the effective stat and forgetting to invalidate it when gear changes.",
        ],
        q1=(
            "Why should effective stats be derived from base plus modifiers rather than stored?",
            "Deriving avoids stale values and double application when buffs, gear or levels change.",
        ),
        homework=(
            "Write `grant_xp(hero, amount)` that levels the hero while xp crosses each threshold and returns a "
            "new dictionary. Grant one large and one tiny reward, print level and leftover xp for both, and "
            "comment why the loop must be a while."
        ),
        patterns=["def grant_xp", "while ", "print("],
        mapping=(
            "RPGs commonly separate base attributes, equipment modifiers and computed stats; tooltips show the "
            "computed value while saves keep the base."
        ),
    ),
    111: dict(
        topic="Resource and economy loops",
        idea=(
            "An economy is a loop with bookkeeping: every turn, production adds to stockpiles and upkeep "
            "subtracts from them. The two rules that prevent most economy bugs are clamping and all-or-nothing "
            "spending. Clamping keeps a resource between zero and a cap, so a negative food count never leaks "
            "into the rest of the game and a runaway stockpile does not overflow the interface. All-or-nothing "
            "spending checks every cost before subtracting any of it, because a partial purchase that takes the "
            "wood but not the food leaves the player with a broken blueprint and a confusing message. Keeping "
            "production and spending as separate functions also makes the loop easy to read: produce for n "
            "turns, then attempt a purchase. Rates can be negative, which is how upkeep is expressed, and the "
            "same clamp handles both directions. The example runs a village for three turns with positive wood "
            "and negative food, prints the stockpile, then tries to build a barracks whose cost is affordable. "
            "It asserts the exact remainder, which is the sort of check that catches an off-by-one in the number "
            "of turns. A real economy adds more resources and recipes, but the shape stays this: pure functions "
            "over a stockpile dictionary, with the loop only deciding how many times to call them."
        ),
        code=(
            'def produce(stock, rates, turns):\n'
            '    stock = dict(stock)\n'
            '    for _ in range(turns):\n'
            '        for resource, rate in rates.items():\n'
            '            stock[resource] = max(0, min(100, stock[resource] + rate))\n'
            '    return stock\n'
            '\n'
            'def affordable(stock, cost):\n'
            '    return all(stock.get(item, 0) >= amount for item, amount in cost.items())\n'
            '\n'
            'def spend(stock, cost):\n'
            '    if not affordable(stock, cost):\n'
            '        return stock, False\n'
            '    stock = dict(stock)\n'
            '    for item, amount in cost.items():\n'
            '        stock[item] -= amount\n'
            '    return stock, True\n'
            '\n'
            'village = {"wood": 10, "food": 8}\n'
            'village = produce(village, {"wood": 15, "food": -1}, 3)\n'
            'print("after 3 turns:", village)\n'
            'village, built = spend(village, {"wood": 40, "food": 5})\n'
            'print("built barracks:", built, "left:", village)\n'
            'assert built and village == {"wood": 15, "food": 0}\n'
            'print("rates are clamped and costs are all-or-nothing")'
        ),
        variant_b='set the food rate to minus four and print the stockpile, showing the clamp at zero',
        variant_c='attempt a cost the village cannot afford and show that nothing is deducted',
        mistakes=[
            "Subtracting costs one resource at a time before checking the whole cost is affordable.",
            "Storing a negative resource and letting later rules assume it is non-negative.",
            "Forgetting the cap, so a long idle period creates an absurd stockpile.",
        ],
        q1=(
            "Why check affordability for the whole cost before subtracting anything?",
            "A partial payment leaves the player without resources and without the building, which is a state the rest of the game does not expect.",
        ),
        homework=(
            "Write `spend(stock, cost)` that returns the new stock and a success flag, deducting nothing when "
            "any resource is short. Test one affordable and one unaffordable cost, print both results, and "
            "comment which line makes the operation atomic."
        ),
        patterns=["def spend", "return", "print("],
        mapping=(
            "Strategy games run a resource tick between turns; clamping and atomic purchases are standard "
            "guards so the simulation never enters an impossible state."
        ),
    ),
    112: dict(
        topic="Win and lose conditions",
        idea=(
            "Ending conditions are a priority list, not a pile of independent checks. When the hero dies on the "
            "same turn the boss dies, the game needs one answer, and that answer should be written down rather "
            "than emerge from whichever check happened to run first. The clean shape is a single evaluate "
            "function over the state that returns a small string: win, lose or ongoing. Inside, the checks run "
            "in a fixed order, and the first match returns. The example puts hero death first, so a mutual kill "
            "is a loss; you might prefer a win, but the important thing is that the choice is explicit and "
            "tested. A time limit is another losing condition, and it belongs in the same list so all endings "
            "live in one place. Callers then have a simple contract: after every action, ask evaluate and stop "
            "when the answer is not ongoing. This is easier to test than boolean flags scattered across the "
            "code, and it is easy to extend with a third ending such as a peace treaty. The function should not "
            "print, award score or change the state; those are consequences of the ending, handled by the loop. "
            "Keeping evaluation pure means a UI can preview an ending, and a test can assert every branch "
            "without playing a whole game."
        ),
        code=(
            'def evaluate(state):\n'
            '    if state["hero_hp"] <= 0:\n'
            '        return "lose"\n'
            '    if state["boss_hp"] <= 0:\n'
            '        return "win"\n'
            '    if state["turns_left"] <= 0:\n'
            '        return "lose"\n'
            '    return "ongoing"\n'
            '\n'
            'cases = [\n'
            '    {"hero_hp": 5, "boss_hp": 0, "turns_left": 2},\n'
            '    {"hero_hp": 0, "boss_hp": 0, "turns_left": 2},\n'
            '    {"hero_hp": 5, "boss_hp": 3, "turns_left": 0},\n'
            '    {"hero_hp": 5, "boss_hp": 3, "turns_left": 4},\n'
            ']\n'
            'for case in cases:\n'
            '    print("hero", case["hero_hp"], "boss", case["boss_hp"],\n'
            '          "turns", case["turns_left"], "->", evaluate(case))\n'
            'assert evaluate(cases[0]) == "win"\n'
            'assert evaluate(cases[1]) == "lose"\n'
            'print("priority order decides simultaneous endings")'
        ),
        variant_b='add a "rescued" flag that wins before boss death and decide where it belongs in the order',
        variant_c='return a tuple of the result and the reason, then print both for each case',
        mistakes=[
            "Checking conditions in different places, so mutual kills depend on call order.",
            "Letting the ending function award score or change state instead of only reporting.",
            "Treating ongoing as an error case rather than the normal result for most turns.",
        ],
        q1=(
            "Why should win and lose checks live in one function with a fixed order?",
            "Simultaneous endings then have one documented answer instead of depending on which check ran first.",
        ),
        homework=(
            "Write `evaluate(state)` returning win, lose or ongoing for a boss fight with hero hp, boss hp and a "
            "turn limit. Test at least four states including a mutual kill, print each result, and comment which "
            "condition is checked first."
        ),
        patterns=["def evaluate", "return", "print("],
        mapping=(
            "Match and level scripts usually funnel endings through one state check so cutscenes, scoring and "
            "saves all agree on why the game stopped."
        ),
    ),
    113: dict(
        topic="Scoring and high scores",
        idea=(
            "A score is a formula, and a high-score table is a sorted view of runs. Keeping them separate means "
            "you can change the formula without rewriting the table, and you can change how many entries the "
            "table keeps without touching scoring. The formula itself should use named stats rather than "
            "mystery numbers inline, so players and designers can reason about it: kills are worth more than "
            "coins, and damage taken is a penalty that rewards clean play. Weights are design choices, not "
            "physics, so expect to tune them; the structure is what matters today. Sorting needs a deterministic "
            "tie-breaker, otherwise two equal scores can swap places between runs and a replay looks different. "
            "Name is a reasonable tie-breaker, or earliest run, as long as it is stated. The table should also "
            "be bounded: sorting every run ever played is wasteful, and displaying a thousand rows is not a high "
            "score table. The example scores three runs, prints the top three with positions, and asserts the "
            "winner. Notice that score_run is called again inside the sort key rather than cached, which is fine "
            "for three runs and a useful reminder that scoring is cheap and pure. When runs become expensive to "
            "score, cache the value in the run record."
        ),
        code=(
            'def score_run(stats):\n'
            '    return stats["kills"] * 100 + stats["coins"] * 5 - stats["damage_taken"] * 2\n'
            '\n'
            'def top_scores(runs, limit=3):\n'
            '    ranked = sorted(runs, key=lambda run: (-score_run(run), run["name"]))\n'
            '    return [(run["name"], score_run(run)) for run in ranked[:limit]]\n'
            '\n'
            'runs = [\n'
            '    {"name": "ada", "kills": 5, "coins": 20, "damage_taken": 10},\n'
            '    {"name": "bo", "kills": 7, "coins": 0, "damage_taken": 40},\n'
            '    {"name": "cy", "kills": 3, "coins": 90, "damage_taken": 5},\n'
            ']\n'
            'for run in runs:\n'
            '    print(run["name"], "scores", score_run(run))\n'
            'for position, entry in enumerate(top_scores(runs), start=1):\n'
            '    print(position, entry[0], entry[1])\n'
            'assert top_scores(runs)[0] == ("cy", 740)\n'
            'print("score is a pure formula; ties break by name")'
        ),
        variant_b='increase the damage penalty to five and print the new ranking',
        variant_c='add a time bonus in seconds and explain whether a faster or slower run should score more',
        mistakes=[
            "Mixing the formula and the table sort into one function that also prints.",
            "Sorting without a tie-breaker, so equal scores reorder between runs.",
            "Keeping every run forever instead of limiting the table to a display size.",
        ],
        q1=(
            "Why does a high-score sort need a tie-breaker?",
            "Equal scores would otherwise be ordered by unstable input order, so the table could differ between identical runs.",
        ),
        homework=(
            "Write `top_scores(runs, limit)` that ranks runs by a points formula and returns name-score pairs. "
            "Include two runs with equal scores, print the table, and comment which part of the key makes the "
            "order repeatable."
        ),
        patterns=["def top_scores", "sorted(", "print("],
        mapping=(
            "Arcade and mobile games keep scoring in data or a small rules module, then persist a bounded leaderboard "
            "rather than recomputing it on every launch."
        ),
    ),
    114: dict(
        topic="Difficulty and adaptive tuning",
        idea=(
            "Adaptive difficulty is a feedback loop, and feedback loops need a window and a dead band. Reacting "
            "to every single result makes the game oscillate: one lucky win raises difficulty, the next loss "
            "drops it, and the player feels the floor moving under them. Looking at a sliding window of the last "
            "few results smooths that out. A dead band, meaning you only change when several results agree, "
            "prevents constant small adjustments. The example raises the level after three wins in the window "
            "and lowers it after three losses, leaving it alone otherwise. Notice that the function takes the "
            "current level and the recent results and returns a new level; it does not read a global difficulty "
            "or write to one. That makes it trivial to test at the boundaries: three wins at the maximum level "
            "must stay at the maximum. Clamping matters for the same reason it mattered in combat maths, because "
            "an unbounded level eventually produces absurd values. There is also an ethical and design question "
            "buried here: should the player know? Hidden rubber-banding is common in racing games, while explicit "
            "difficulty settings are expected in strategy games. Whatever you choose, the mechanism should be "
            "observable in a debug print and measurable in a test. A loop you cannot inspect is a loop you cannot "
            "balance, and a player will feel unfairness long before they can name it."
        ),
        code=(
            'def next_difficulty(level, recent_results):\n'
            '    wins = sum(1 for result in recent_results if result == "win")\n'
            '    losses = len(recent_results) - wins\n'
            '    if wins >= 3:\n'
            '        return min(5, level + 1)\n'
            '    if losses >= 3:\n'
            '        return max(1, level - 1)\n'
            '    return level\n'
            '\n'
            'history = ["win", "win", "win", "loss", "win"]\n'
            'level = 2\n'
            'for index in range(len(history)):\n'
            '    window = history[max(0, index - 2): index + 1]\n'
            '    level = next_difficulty(level, window)\n'
            '    print("after", index + 1, "results -> level", level)\n'
            'assert next_difficulty(5, ["win", "win", "win"]) == 5\n'
            'assert level == 3\n'
            'print("a sliding window and a clamp keep the feedback calm")'
        ),
        variant_b='start at level five and feed three wins, showing that the clamp refuses to go higher',
        variant_c='react to two wins instead of three and explain why the game may start oscillating',
        mistakes=[
            "Adjusting difficulty after every single result, which makes the game feel unstable.",
            "Forgetting to clamp the level, so a long win streak produces impossible enemies.",
            "Hiding the mechanism so thoroughly that nobody can debug or test it.",
        ],
        q1=(
            "Why use a sliding window instead of only the last result?",
            "A window smooths out single lucky or unlucky outcomes, so difficulty changes reflect a trend rather than noise.",
        ),
        homework=(
            "Write `next_difficulty(level, results)` that raises, lowers or keeps difficulty using a three-result "
            "window and clamps to one through five. Feed a mixed history, print the level after each step, and "
            "comment which line prevents runaway difficulty."
        ),
        patterns=["def next_difficulty", "min(", "print("],
        mapping=(
            "Racing games and action titles often tune rubber-banding from a rolling performance window, while "
            "strategy games tend to expose difficulty as an explicit setting."
        ),
    ),
    115: dict(
        topic="Fair randomness and pity timers",
        idea=(
            "Pure randomness feels unfair to players because long dry streaks are common and memorable. A pity "
            "timer is a small counter that guarantees a success after enough failures, turning a geometric "
            "distribution into one with a hard ceiling. The design questions are the ceiling and the reset rule: "
            "how many failures before the guarantee, and does one success reset the counter to zero. The example "
            "uses a guarantee on the fourth attempt, which means no window of four rolls can be all misses. That "
            "is a testable property, and testing properties rather than exact sequences is the right habit for "
            "random systems. Notice that the counter lives inside the roll function for the duration of the run, "
            "but the random generator is passed in. When a save file is involved, the counter must be saved too; "
            "otherwise reloading resets pity and players can farm it. Pity interacts with probability in ways "
            "that are easy to misstate: the advertised chance is no longer the final chance, so if you display a "
            "percentage you should display the effective one or explain the guarantee. The example prints hits "
            "and misses and asserts that every four-roll window contains a hit. It also reruns with the same "
            "seed to show that the pity state stays deterministic, which is what makes the whole system testable."
        ),
        code=(
            'import random\n'
            '\n'
            'def roll_with_pity(rng, rolls, pity_after=4, chance=0.25):\n'
            '    failures = 0\n'
            '    results = []\n'
            '    for _ in range(rolls):\n'
            '        success = rng.random() < chance\n'
            '        if not success and failures + 1 >= pity_after:\n'
            '            success = True\n'
            '        failures = 0 if success else failures + 1\n'
            '        results.append(success)\n'
            '    return results\n'
            '\n'
            'results = roll_with_pity(random.Random(3), 20)\n'
            'print("rolls:", ["hit" if r else "miss" for r in results])\n'
            'streaks = "".join("m" if not r else " " for r in results).split()\n'
            'print("longest miss streak:", max((len(run) for run in streaks), default=0))\n'
            'assert all(any(results[i:i + 4]) for i in range(len(results) - 3))\n'
            'assert results == roll_with_pity(random.Random(3), 20)\n'
            'print("pity caps the dry streak and stays seeded")'
        ),
        variant_b='raise the pity threshold to six and print the new longest miss streak',
        variant_c='reset the pity counter only on a natural success and decide whether that is fairer',
        mistakes=[
            "Forgetting to save the pity counter, so reloading the game resets the guarantee.",
            "Advertising the base chance without mentioning the guarantee, which misleads players.",
            "Testing one exact sequence instead of the property that no long dry streak occurs.",
        ],
        q1=(
            "What property does a pity timer guarantee that raw randomness does not?",
            "It bounds the maximum number of consecutive failures, so no player can hit an arbitrarily long dry streak.",
        ),
        homework=(
            "Write `roll_with_pity(rng, rolls, pity_after)` that forces a success after the given number of "
            "failures and returns a list of booleans. Print the list, assert that no window of pity_after rolls "
            "is all failures, and comment which line enforces the guarantee."
        ),
        patterns=["def roll_with_pity", "assert", "print("],
        mapping=(
            "Gacha and loot systems ship pity counters as part of save state, and documentation usually states "
            "both the base rate and the guarantee."
        ),
    ),
    116: dict(
        topic="Greedy opponent AI",
        idea=(
            "A greedy opponent is the cheapest believable AI: score every legal action by its immediate effect, "
            "then take the best one. It is not smart over time, but it is understandable, fast and a good "
            "baseline before anything more elaborate. The important design choice is the scoring function, "
            "because that is where the opponent's personality lives. Attacking a low-health, high-threat enemy "
            "scores well; healing scores by how much health is missing; waiting scores zero. Keeping the score "
            "as a pure function over the state and one action means you can print the table and see exactly why "
            "the AI chose what it chose, which is invaluable when it does something stupid. Ties need a rule, or "
            "the choice depends on list order and stops being reproducible. The example uses kind as a "
            "tie-breaker and then selects with max, but a real implementation should make the tie-break explicit "
            "and documented. Greedy has a known failure mode: it will take a big immediate hit over a setup "
            "that wins next turn, and it will never retreat to heal if attacking scores higher right now. That "
            "is acceptable for trash mobs and unacceptable for a boss. Knowing where the ceiling is tells you "
            "when to move to search-based AI, which is the next lesson."
        ),
        code=(
            'def score_action(state, action):\n'
            '    if action["kind"] == "attack":\n'
            '        target = state["enemies"][action["target"]]\n'
            '        return target["threat"] - target["hp"]\n'
            '    if action["kind"] == "heal":\n'
            '        return state["hero_max_hp"] - state["hero_hp"]\n'
            '    return 0\n'
            '\n'
            'def choose(state, actions):\n'
            '    return max(actions, key=lambda action: (score_action(state, action), action["kind"]))\n'
            '\n'
            'state = {\n'
            '    "hero_hp": 6,\n'
            '    "hero_max_hp": 10,\n'
            '    "enemies": {"slime": {"hp": 2, "threat": 3}, "ogre": {"hp": 9, "threat": 10}},\n'
            '}\n'
            'actions = [\n'
            '    {"kind": "attack", "target": "slime"},\n'
            '    {"kind": "attack", "target": "ogre"},\n'
            '    {"kind": "heal"},\n'
            ']\n'
            'for action in actions:\n'
            '    print(action, "scores", score_action(state, action))\n'
            'print("chosen:", choose(state, actions))\n'
            'assert choose(state, actions) == {"kind": "heal"}\n'
            'print("greedy takes the best immediate score")'
        ),
        variant_b='lower hero hp to two and print the choice, showing how the same scoring reacts',
        variant_c='add a "defend" action worth the incoming threat and explain when defending becomes correct',
        mistakes=[
            "Scoring actions inside the choose loop with hidden state, so the printed table and the choice disagree.",
            "Leaving ties to list order, which makes the AI non-reproducible after a refactor.",
            "Expecting greedy play to set up multi-turn combos it cannot see.",
        ],
        q1=(
            "What is the main limitation of a greedy opponent?",
            "It only values immediate effects, so it cannot sacrifice now for a stronger position or plan several turns ahead.",
        ),
        homework=(
            "Write `choose(state, actions)` that scores attack and heal actions and returns the best one, with a "
            "documented tie-break. Print the score for every action, print the choice, and comment which action "
            "the AI ignores and why."
        ),
        patterns=["def choose", "max(", "print("],
        mapping=(
            "Greedy utility scoring drives many mobile and roguelike enemies, while bosses usually add scripts or "
            "search on top of the same scoring function."
        ),
    ),
    117: dict(
        topic="Minimax for perfect information",
        idea=(
            "Minimax is the idea that a rational opponent picks the move that is worst for you, so you should "
            "pick the move whose worst reply is least bad. The recursion has three parts: a terminal test, a "
            "depth limit and a turn that maximises or minimises depending on who is to move. The terminal score "
            "must be from one consistent point of view, or the signs cancel and the search confidently chooses "
            "the losing move. The example uses a tiny take-away game: one heap, take one or two stones, and the "
            "player who takes the last stone wins. The search explores only two plies beyond the opening, which "
            "is enough to demonstrate the idea without a large tree. Depth matters because a full search on a "
            "real game is enormous; a depth-limited search needs an evaluation for non-terminal nodes, and here "
            "that evaluation is a neutral zero. Even this small version shows the characteristic behaviour: it "
            "prefers a line where the opponent has no good reply and avoids lines where every reply loses. The "
            "function returns a score, not a move, so a separate wrapper picks the best opening. Keeping those "
            "two jobs apart makes it easy to print the value of every candidate move, which is exactly how you "
            "debug a search that is choosing something surprising."
        ),
        code=(
            'def moves(state):\n'
            '    return [take for take in (1, 2) if take <= state["stones"]]\n'
            '\n'
            'def result(state, take, player):\n'
            '    return {"stones": state["stones"] - take, "player": 3 - player}\n'
            '\n'
            'def minimax(state, depth, player):\n'
            '    if state["stones"] == 0:\n'
            '        return 10 - depth if player == 2 else depth - 10\n'
            '    if depth == 0:\n'
            '        return 0\n'
            '    scores = [minimax(result(state, take, player), depth - 1, 3 - player)\n'
            '              for take in moves(state)]\n'
            '    return max(scores) if player == 1 else min(scores)\n'
            '\n'
            'start = {"stones": 5, "player": 1}\n'
            'for take in moves(start):\n'
            '    value = minimax(result(start, take, 1), 2, 2)\n'
            '    print("take", take, "-> value", value)\n'
            'best = max(moves(start), key=lambda take: minimax(result(start, take, 1), 2, 2))\n'
            'print("best opening take:", best)\n'
            'assert best == 2\n'
            'print("minimax assumes a perfect opponent and avoids losing lines")'
        ),
        variant_b='start with seven stones and print the value of each opening move',
        variant_c='change the win condition to taking the last stone loses and describe how the scores flip',
        mistakes=[
            "Scoring terminal states from different points of view, so one side maximises the wrong number.",
            "Searching without a depth limit on a game whose tree is too large to finish.",
            "Returning a move from the recursive function and then forgetting whose turn it is.",
        ],
        q1=(
            "Why must terminal scores use one consistent point of view?",
            "Max and min compare the same number, so mixed perspectives make the search prefer lines that are good for the opponent.",
        ),
        homework=(
            "Write `minimax(state, depth, player)` for a one-heap take-away game where taking the last stone wins. "
            "Print the value of every opening move from five stones, choose the best take, and comment which "
            "line flips between maximising and minimising."
        ),
        patterns=["def minimax", "max(", "print("],
        mapping=(
            "Chess and checkers engines run minimax or negamax with alpha-beta pruning; the toy version here is "
            "the same recursion with a much smaller tree."
        ),
    ),
    118: dict(
        topic="State machines for behaviour",
        idea=(
            "Enemy behaviour is easier to read as a state machine than as a nest of timers and booleans. The "
            "machine has a current state, a set of events, and a table mapping state plus event to the next "
            "state. Anything not in the table leaves the state unchanged, which is a useful default: an enemy "
            "that hears a noise while attacking does not need a special case unless you decide it does. Keeping "
            "the transition table as data means you can print it, test it exhaustively and let a designer edit "
            "it without touching the update loop. The states in the example are patrol, chase and attack, with "
            "events for seeing the player, getting in range, losing the player and the target going down. The "
            "trail shows a full cycle and a return to patrol. Notice that the machine only decides which state "
            "the enemy is in; what the enemy does while chasing, such as pathfinding, is a separate concern "
            "owned by that state's behaviour. Separating transition logic from per-state behaviour is what keeps "
            "both small. A real implementation often adds entry and exit actions, such as playing a sound on "
            "entering attack, but the core remains this table. When the table grows, invalid transitions become "
            "the main source of bugs, so a test that walks every state-event pair is worth more than a long "
            "manual playtest."
        ),
        code=(
            'def next_state(state, event):\n'
            '    table = {\n'
            '        ("patrol", "sees_player"): "chase",\n'
            '        ("chase", "in_range"): "attack",\n'
            '        ("chase", "lost_player"): "patrol",\n'
            '        ("attack", "target_down"): "patrol",\n'
            '    }\n'
            '    return table.get((state, event), state)\n'
            '\n'
            'def run(events):\n'
            '    state = "patrol"\n'
            '    trail = [state]\n'
            '    for event in events:\n'
            '        state = next_state(state, event)\n'
            '        trail.append(state)\n'
            '    return trail\n'
            '\n'
            'events = ["sees_player", "in_range", "target_down", "sees_player", "lost_player"]\n'
            'trail = run(events)\n'
            'print(" -> ".join(trail))\n'
            'for before, event in zip(trail, events):\n'
            '    print(before, "+", event, "->", next_state(before, event))\n'
            'assert trail == ["patrol", "chase", "attack", "patrol", "chase", "patrol"]\n'
            'print("an unknown event leaves the state unchanged")'
        ),
        variant_b='add a "flees" state entered when health is low and print the new trail',
        variant_c='return an (state, action) pair from each transition and explain where entry actions belong',
        mistakes=[
            "Encoding states as several booleans, so impossible combinations such as chasing and patrolling can occur.",
            "Throwing on unknown events instead of documenting the default behaviour.",
            "Mixing pathfinding code into the transition table instead of the state's own behaviour.",
        ],
        q1=(
            "Why keep the transition table as data rather than a chain of if statements?",
            "It can be printed, tested pair by pair and edited by a designer without changing control flow.",
        ),
        homework=(
            "Write `next_state(state, event)` using a dictionary of transitions for patrol, chase and attack. Walk "
            "a list of events, print the state after each one, and comment which line implements the stay-put "
            "default."
        ),
        patterns=["def next_state", "table.get", "print("],
        mapping=(
            "Enemy AI in engines is commonly a state machine or behaviour tree; the table version is the smallest "
            "form and the easiest to inspect in a debug overlay."
        ),
    ),
    119: dict(
        topic="Review: game logic checklist",
        idea=(
            "A review checklist is worth more when it runs. Instead of reading code and hoping to remember every "
            "invariant, encode the invariants as a function that takes a game state and returns a list of "
            "problems. The list is empty when the state is healthy, which makes it trivial to assert in a test "
            "and trivial to print in a debug overlay. Good checks are about impossible states rather than style: "
            "negative health, a turn counter that starts below one, no reachable ending, and an empty action "
            "list. Each of those means the game can enter a situation the rest of the code does not expect, or "
            "cannot progress at all. Notice that the checklist does not fix anything. Reporting and repairing "
            "are separate jobs, and a checker that silently repairs problems hides the bug that produced them. "
            "The example builds one deliberately broken state and one healthy state, prints both reports, and "
            "asserts the counts. That is the shape of a smoke test you can run after every rule change. As the "
            "game grows, the checklist grows with it: resource bounds, inventory non-negative counts, unique ids, "
            "and a reachable ending for every level. The point is not to enumerate every bug, but to catch the "
            "class of bug that makes a game unwinnable or a save unloadable."
        ),
        code=(
            'def check_game(state):\n'
            '    issues = []\n'
            '    if state["hero_hp"] < 0:\n'
            '        issues.append("negative hp breaks the clamp")\n'
            '    if state["turn"] < 1:\n'
            '        issues.append("turn counter must start at one")\n'
            '    if not state["victory"] and not state["defeat"]:\n'
            '        issues.append("no ending condition can be reached")\n'
            '    if not state["actions"]:\n'
            '        issues.append("empty action list blocks progress")\n'
            '    return issues\n'
            '\n'
            'bad = {"hero_hp": -1, "turn": 0, "victory": False, "defeat": False, "actions": []}\n'
            'good = {"hero_hp": 5, "turn": 3, "victory": True, "defeat": False, "actions": ["attack"]}\n'
            'print("bad:", check_game(bad))\n'
            'print("good:", check_game(good))\n'
            'assert len(check_game(bad)) == 4 and check_game(good) == []\n'
            'print("a checklist turns review into a runnable test")'
        ),
        variant_b='add a check that inventory counts are never negative and give the bad state a negative count',
        variant_c='return issue codes instead of prose and map the codes to messages in the presentation layer',
        mistakes=[
            "Making the checker repair state, which hides the bug that created the bad state.",
            "Only checking for crashes and not for unwinnable or unloadable states.",
            "Writing prose checks that cannot be asserted in a test.",
        ],
        q1=(
            "Why should the checklist return problems instead of fixing them?",
            "Reporting keeps the checker pure and makes the original bug visible; silent repair hides how the invalid state arose.",
        ),
        homework=(
            "Write `check_game(state)` returning a list of invariant violations for hp, turn, ending reachability "
            "and actions. Run it on a broken and a healthy state, print both lists, and comment which check "
            "guards against an unwinnable game."
        ),
        patterns=["def check_game", "issues.append", "print("],
        mapping=(
            "Studios run smoke tests and debug overlays against invariants like these; automated checks catch the "
            "unwinnable states that manual playtesting misses."
        ),
    ),
})
