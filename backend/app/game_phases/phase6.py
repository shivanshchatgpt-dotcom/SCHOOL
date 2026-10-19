"""Domain phase 6, days 150-164: engines, performance and porting.

Every example is stdlib-only, offline and deterministic: work is measured by
counting operations, never by reading a clock, so the applier captures the same
output on every machine. One idea, a runnable fixture, and a homework function
the learner adapts, in the same shape as the foundation arc.
"""

PHASE = (
    "Engines, Performance and Porting",
    "Turn a working game into one that runs fast, tests headless, and ships on more than one platform.",
    {
        150: dict(
            topic="Orientation: shipping and performance",
            idea=(
                "Until now the goal was a game that works; from here the goal is a game that ships. Shipping "
                "changes the questions you ask. Does it run on the machine the player owns, not just yours? Does "
                "it hold a stable frame rate when the world gets busy, or does it stutter exactly when it "
                "matters? Can you build and test it without a window or a graphics card? Performance stops "
                "being an afterthought and becomes a feature with a budget, because a frame is a fixed slice "
                "of time and every system competes for it. The mental shift is from correctness to constraints: "
                "a correct system that misses the frame budget is still a broken game. The second shift is from "
                "one machine to many, which forces you to separate what is truly required from what merely "
                "happens to work on your setup. This phase is a tour of both disciplines. You will learn to "
                "measure work in operations rather than seconds, to reuse objects, to index space, to test "
                "logic headless, and to package and port the result. The unifying habit is to make the machine "
                "state explicit and the hot path obvious. Today you size a naive all-pairs update and see how "
                "quickly the count explodes, which motivates every optimisation that follows."
            ),
            code=(
                'def pair_checks(n):\n'
                '    checks = 0\n'
                '    for a in range(n):\n'
                '        for b in range(n):\n'
                '            if a != b:\n'
                '                checks += 1\n'
                '    return checks\n'
                '\n'
                'for n in (10, 100, 1000):\n'
                '    print(n, "entities ->", pair_checks(n), "pair checks")\n'
                '\n'
                'assert pair_checks(10) == 90\n'
                'print("naive work grows with the square of entity count")'
            ),
            variant_b='add a row for 5000 entities and compare it to 1000 — how much bigger is the count?',
            variant_c='count only the pairs that actually overlap and explain why the naive loop still visits all of them',
            mistakes=[
                "Treating performance as something to fix at the end rather than a budget from the start.",
                "Optimising by guesswork without first counting where the work actually goes.",
                "Assuming the code that runs fast on your machine will run fast on a player's machine.",
            ],
            q1=(
                "Why is an all-pairs update fine for ten entities but hopeless for ten thousand?",
                "The work grows with the square of the count, so ten thousand entities need about a hundred million checks per frame.",
            ),
            homework=(
                "Write `pair_checks(n)` that counts the ordered pairs of distinct indices for n entities, then "
                "print the result for three sizes of your choosing and comment which line makes the count grow "
                "quadratically."
            ),
            patterns=["def ", "return", "print("],
            mapping=(
                "Every engine profiler exists because this quadratic blow-up is invisible until a level ships; "
                "the fix is always to stop touching every entity every frame."
            ),
        ),
        151: dict(
            topic="Frame budget and profiling",
            idea=(
                "A frame budget is the time one frame may take: about sixteen milliseconds at sixty frames per "
                "second. Profiling is the act of spending that budget knowingly. Without profiling, optimisation "
                "is superstition; with it, the decision is arithmetic. You divide the frame among subsystems, "
                "measure what each one costs, and fix the one that overruns rather than the one that looks "
                "suspicious. Two rules make this honest. First, measure before you change anything, because the "
                "bottleneck is almost never where intuition says. Second, measure the same way every time, so "
                "that a change can be attributed to one edit. For this course we never read a clock, because a "
                "clock makes output depend on the machine and breaks reproducibility; instead we count "
                "operations, which is a stable proxy for work. A profiler that counts is still a profiler: it "
                "tells you which subsystem dominates and whether an edit moved the needle. The companion idea "
                "is the budget itself. If audio costs forty operations, physics twelve hundred and rendering "
                "nine hundred, then physics is the target, and shaving audio is a rounding error. Today you "
                "account for a toy frame in counted operations, find the heaviest subsystem, and print it. That "
                "habit of attributing cost to a system is what keeps a game inside its frame when the content "
                "grows."
            ),
            code=(
                'budget_ms = 16.67\n'
                'subsystems = {"physics": 1200, "ai": 350, "render": 900, "audio": 40}\n'
                '\n'
                'print("frame budget ms:", budget_ms)\n'
                'total = 0\n'
                'for name, ops in subsystems.items():\n'
                '    total += ops\n'
                '    print(f"{name:8s} {ops:5d} ops")\n'
                'print("total ops:", total)\n'
                '\n'
                'heaviest = max(subsystems, key=subsystems.get)\n'
                'print("heaviest subsystem:", heaviest)\n'
                'assert heaviest == "physics"\n'
                'print("profile first, then optimise the subsystem that dominates")'
            ),
            variant_b='move half the physics budget into ai and rerun — which subsystem becomes the target?',
            variant_c='add a frame_ms field per subsystem and print the share of the budget each one consumes',
            mistakes=[
                "Optimising the code that is easiest to change instead of the subsystem that costs the most.",
                "Comparing timings taken on a busy machine, so the numbers move for reasons unrelated to the code.",
                "Measuring once and trusting the result, rather than repeating after every single change.",
            ],
            q1=(
                "Why count operations instead of seconds when comparing two versions of a system?",
                "Operation counts are stable across machines and runs, so a difference is caused by the change rather than by the hardware or load.",
            ),
            homework=(
                "Write `heaviest_subsystem(costs)` that takes a dictionary of subsystem names to operation counts "
                "and returns the name of the most expensive one. Call it on two different cost tables, print both "
                "answers, and comment which line selects the maximum."
            ),
            patterns=["def ", "return", "max("],
            mapping=(
                "Engines ship profilers that attribute a frame to systems; Godot's monitor panel and Unity's "
                "profiler are the same idea of spending a fixed frame budget knowingly."
            ),
        ),
        152: dict(
            topic="Object pooling",
            idea=(
                "Games create and destroy objects constantly: bullets, particles, damage numbers, enemies. Each "
                "creation asks the memory system for space and each destruction eventually returns it, and the "
                "cost is not only the allocation itself but the fragmentation and garbage collection that follow "
                "in languages that manage memory. A pool trades that churn for reuse. You allocate a fixed set of "
                "slots up front, hand them out while the game runs, and take them back when an object is done. "
                "The number of live objects is usually small and bounded; if a hundred bullets can exist at once, "
                "a pool of a hundred is enough for the whole session. The pattern has three responsibilities to "
                "keep straight. Acquiring a slot must be constant time, so a free list of available indices is "
                "the usual structure. Releasing a slot must put it back exactly once, because a double release "
                "hands the same slot to two owners and corrupts state. Running out must have a defined policy, "
                "usually reusing the oldest slot or skipping the spawn. None of this is complicated, but all of "
                "it must be deliberate, because pool bugs surface as objects that vanish or teleport. Today you "
                "build a tiny pool, exhaust it, and prove the free list refills."
            ),
            code=(
                'class Pool:\n'
                '    def __init__(self, size):\n'
                '        self.free = list(range(size))\n'
                '        self.allocations = 0\n'
                '        self.reuses = 0\n'
                '    def acquire(self):\n'
                '        if self.free:\n'
                '            self.reuses += 1\n'
                '            return self.free.pop()\n'
                '        self.allocations += 1\n'
                '        return -1\n'
                '    def release(self, slot):\n'
                '        self.free.append(slot)\n'
                '\n'
                'pool = Pool(2)\n'
                'held = [pool.acquire() for _ in range(4)]\n'
                'print("slots:", held)\n'
                'print("allocations:", pool.allocations, "reuses:", pool.reuses)\n'
                'for slot in held:\n'
                '    if slot != -1:\n'
                '        pool.release(slot)\n'
                'print("free after release:", sorted(pool.free))\n'
                'assert pool.allocations == 2 and pool.reuses == 2\n'
                'assert sorted(pool.free) == [0, 1]\n'
                'print("a pool reuses slots and bounds allocation")'
            ),
            variant_b='create the pool with size three and acquire five slots — how do the two counters change?',
            variant_c='add a generation counter to each slot so a stale handle can detect it was released',
            mistakes=[
                "Releasing a slot twice, so two live objects end up sharing one index.",
                "Growing the pool without a policy for exhaustion, which allocates during the hot path anyway.",
                "Forgetting to reset a slot's data on acquire, so a reused bullet carries the old one's state.",
            ],
            q1=(
                "Why does a pool allocate up front instead of allocating on each spawn?",
                "It removes per-spawn allocation and the fragmentation or collection that follows, keeping the hot path constant time and predictable.",
            ),
            homework=(
                "Write `acquire_two(pool)` that takes a pool object and returns the slots for two acquires, and "
                "`give_back(pool, slots)` that releases them. Acquire two, release them, print the free list "
                "before and after, and comment which line returns a slot to the pool."
            ),
            patterns=["def ", "return", "print("],
            mapping=(
                "Particle systems and bullet managers in every commercial engine are pools; recycling projectiles "
                "is the classic reason a shooter can fire thousands of bullets without a hitch."
            ),
        ),
        153: dict(
            topic="Spatial indexes at scale",
            idea=(
                "Checking every pair of objects for proximity is the quadratic cost you met on day one hundred and "
                "fifty, and a spatial index is the standard way to beat it. The idea is to divide the world into "
                "cells and only compare objects that share or neighbour a cell, because two objects far apart can "
                "never collide. A uniform grid is the simplest index and the one most games start with: pick a "
                "cell size near the typical object size, hash each object's position to a cell, and keep a list "
                "per cell. A query then visits a handful of cells instead of the whole world. The trade-offs are "
                "real and worth naming. A cell too small scatters objects across many cells and the bookkeeping "
                "dominates; a cell too large packs everything together and you are back to pairwise checks. "
                "Objects that span cells need to be inserted into each cell they touch, or found by checking "
                "neighbours. A grid also assumes objects are spread out; if the whole world clusters in one "
                "corner, a tree or a sorted axis list adapts better. None of that changes the core win, which is "
                "turning a global all-pairs scan into a local one. Today you bucket points on a grid and count "
                "how many pairs the grid still compares, then compare that to the brute-force number."
            ),
            code=(
                'def brute_pairs(points):\n'
                '    n = len(points)\n'
                '    return n * (n - 1) // 2\n'
                '\n'
                'def grid_buckets(points, cell):\n'
                '    buckets = {}\n'
                '    for i, (x, y) in enumerate(points):\n'
                '        buckets.setdefault((x // cell, y // cell), []).append(i)\n'
                '    return buckets\n'
                '\n'
                'points = [(x, y) for x in range(0, 12, 3) for y in range(0, 12, 3)]\n'
                'grid = grid_buckets(points, 6)\n'
                'inside = sum(len(v) * (len(v) - 1) // 2 for v in grid.values())\n'
                '\n'
                'print("points:", len(points))\n'
                'print("buckets:", len(grid))\n'
                'print("brute pairs:", brute_pairs(points))\n'
                'print("same-cell pairs:", inside)\n'
                'assert inside < brute_pairs(points)\n'
                'print("grid localises the pair checks")'
            ),
            variant_b='halve the cell size to three and print the bucket count and same-cell pairs again',
            variant_c='insert each point into its cell and all neighbouring cells, then count the larger candidate set',
            mistakes=[
                "Choosing a cell size in isolation instead of relative to the typical object size.",
                "Storing an object in only one cell when it spans several, so overlaps across borders are missed.",
                "Rebuilding the whole grid every frame when nothing moved, wasting the very budget the index saved.",
            ],
            q1=(
                "Why does a spatial grid reduce the number of pair checks?",
                "Objects far apart never share a cell, so the index only compares objects that are close enough to possibly interact.",
            ),
            homework=(
                "Write `cell_of(point, cell)` that returns the integer (column, row) for one point, and "
                "`bucket_count(points, cell)` that counts how many distinct cells the points occupy. Print both "
                "for two cell sizes and comment which line performs the integer division."
            ),
            patterns=["def ", "//", "print("],
            mapping=(
                "Broad-phase collision in engines uses exactly this grid or a quadtree; the choice is a "
                "cell-size tuning problem whenever object sizes vary a lot."
            ),
        ),
        154: dict(
            topic="Entity component systems",
            idea=(
                "Inheritance looks natural for game objects and turns into a tangle. A Player is an Actor, an "
                "Actor is an Entity; then a flying enemy needs both movement and flight, and the hierarchy "
                "cracks. An entity component system replaces the hierarchy with composition. An entity is just "
                "an identifier, a number with no behaviour. Components are plain data attached to entities: a "
                "position, a health, a sprite name. Systems are functions that query the entities which have a "
                "particular set of components and act on them. Because data and behaviour are separate, a new "
                "feature is usually a new component plus a small system, not a new branch in a base class. The "
                "selection mechanism is the heart of it. A system declares the components it reads, and the "
                "world returns every entity that has all of them; an entity simply stops matching when you remove "
                "a component. That is the flexibility inheritance cannot give you cheaply. The cost is "
                "indirection: state is now spread across component stores, so straightforward code becomes "
                "queries, and debugging means asking which systems touched an entity. The trade-off is worth it "
                "once the number of behaviours grows. Today you build a tiny world with component dictionaries, "
                "spawn three entities, and query by component set to show composition in action."
            ),
            code=(
                'class World:\n'
                '    def __init__(self):\n'
                '        self.components = {}\n'
                '        self.next_id = 0\n'
                '    def spawn(self, **comps):\n'
                '        eid = self.next_id\n'
                '        self.next_id += 1\n'
                '        for name, value in comps.items():\n'
                '            self.components.setdefault(name, {})[eid] = value\n'
                '        return eid\n'
                '    def query(self, *names):\n'
                '        sets = [set(self.components[n]) for n in names]\n'
                '        return sorted(set.intersection(*sets))\n'
                '\n'
                'world = World()\n'
                'hero = world.spawn(position=(0, 0), health=10, sprite="hero")\n'
                'slime = world.spawn(position=(5, 2), health=4)\n'
                'world.spawn(position=(1, 1))\n'
                '\n'
                'print("position+health:", world.query("position", "health"))\n'
                'print("sprites:", world.query("sprite"))\n'
                'assert world.query("position", "health") == [hero, slime]\n'
                'print("systems query components, not class hierarchies")'
            ),
            variant_b='add a velocity component to the hero only and print which entities a movement system would read',
            variant_c='remove the health component from the slime and show it drops out of the position+health query',
            mistakes=[
                "Putting behaviour inside components, which just rebuilds the class hierarchy as data.",
                "Letting a system mutate components it did not declare it reads, hiding the dependency.",
                "Assuming query order is stable when it comes from unordered storage, so results vary between runs.",
            ],
            q1=(
                "Why is composition preferred over deep inheritance for game objects?",
                "An entity gets exactly the components it needs, so adding one behaviour never forces a change to unrelated types the way a base class does.",
            ),
            homework=(
                "Write `find_with(world, *names)` that returns the sorted ids of every entity holding all the "
                "named components. Spawn a few entities with overlapping components, print the result for two "
                "component sets, and comment which line intersects the sets."
            ),
            patterns=["def ", "set.", "print("],
            mapping=(
                "Unity, Godot and Bevy all expose a component model; the query-by-components idea is the same "
                "whether it is called GameObject or ECS."
            ),
        ),
        155: dict(
            topic="Physics libraries and when to use them",
            idea=(
                "A physics library is an enormous amount of careful work, and knowing when to buy it instead of "
                "building it is a real engineering skill. Hand-rolled motion is perfect for the simple cases: a "
                "top-down shooter where circles bounce, a platformer with axis-aligned ground, a turn-based game "
                "with no continuous motion at all. You integrate position from velocity, clamp against the world "
                "bounds, and stop. The moment you need stacking boxes, rotating bodies, joints, friction or "
                "sleeping, a library earns its weight, because stable contact resolution is the hardest part of "
                "physics and the part beginners most often get wrong. There are good reasons to take the library "
                "early. It handles tunnelling, the case where a fast object passes through a thin wall in one "
                "step, through continuous collision detection. It provides deterministic options for replays. It "
                "is tested against thousands of scenarios you will never write. The reasons to avoid it are "
                "equally real: it is a large dependency, it wants to own the timestep, and it can be hard to make "
                "behave custom. The decision rule is to match the library to the simulation you actually need, "
                "not the most impressive one. Today you integrate a toy projectile by hand to see what a library "
                "would replace, and note where the hand version stops being adequate."
            ),
            code=(
                'def integrate(pos, vel, accel, dt, steps):\n'
                '    for _ in range(steps):\n'
                '        vel = (vel[0] + accel[0] * dt, vel[1] + accel[1] * dt)\n'
                '        pos = (pos[0] + vel[0] * dt, pos[1] + vel[1] * dt)\n'
                '    return pos, vel\n'
                '\n'
                'pos, vel = integrate((0.0, 0.0), (1.0, 0.0), (0.0, -2.0), 0.5, 4)\n'
                'print("pos:", tuple(round(v, 2) for v in pos))\n'
                'print("vel:", tuple(round(v, 2) for v in vel))\n'
                'assert tuple(round(v, 2) for v in pos) == (2.0, -5.0)\n'
                'print("hand integration is fine until contacts and stacking appear")'
            ),
            variant_b='drop the timestep to 0.25 with eight steps and compare the final position to the coarse run',
            variant_c='add a floor at y=0 and clamp the position when it goes below, then print the bounce behaviour',
            mistakes=[
                "Using a variable timestep with a physics library, which makes the simulation depend on frame rate.",
                "Adding a heavy engine for motion that a few lines of integration would cover exactly.",
                "Letting game logic read physics bodies mid-step, so rules see a world that is half updated.",
            ],
            q1=(
                "When does hand-rolled physics stop being the right choice?",
                "Once stable contacts, stacking, rotation or joints matter, because a tested library resolves those far more reliably than a small integrator.",
            ),
            homework=(
                "Write `projectile(vx, vy, steps, dt)` that returns the final position after fixed-step "
                "integration with a constant downward acceleration. Run it with two launch velocities, print both "
                "landing positions, and comment which line advances the position."
            ),
            patterns=["def ", "for ", "return"],
            mapping=(
                "Box2D, Bullet, PhysX and Godot's physics servers all exist because robust contact resolution is "
                "years of work; teams adopt them exactly when simple motion stops being enough."
            ),
        ),
        156: dict(
            topic="Rendering concepts without a GPU",
            idea=(
                "You do not need a graphics card to understand rendering; you need the ideas, and they fit in a "
                "list sort. A frame is a sequence of draw operations, and the order of those operations decides "
                "what covers what. The painter's algorithm is the oldest and clearest: draw the things furthest "
                "away first, then nearer things on top, exactly as a painter layers a canvas. In a flat "
                "two-dimensional game this is a sort by a depth value, and everything else is bookkeeping. With "
                "that model you can reason about the parts of a renderer that matter for design and performance. "
                "Overdraw is how many times a pixel is written before the frame ends, and drawing a full-screen "
                "background under a full-screen sky is wasted work. Batching is drawing many sprites that share a "
                "texture in one call, which matters because each draw has fixed overhead. Culling is deciding not "
                "to draw what is off-screen at all. None of these require pixels to demonstrate; they are "
                "decisions about a queue of draw commands, and a list is enough to model the queue. Today you "
                "sort a toy scene from far to near and print the draw order, which is the painter's algorithm in "
                "its entirety, then note where a real renderer would add batching and culling."
            ),
            code=(
                'def draw_order(sprites):\n'
                '    return sorted(sprites, key=lambda s: s["z"])\n'
                '\n'
                'scene = [\n'
                '    {"name": "sky", "z": 0},\n'
                '    {"name": "hero", "z": 5},\n'
                '    {"name": "tree", "z": 3},\n'
                '    {"name": "hud", "z": 10},\n'
                ']\n'
                '\n'
                'for sprite in draw_order(scene):\n'
                '    print("draw", sprite["name"], "z", sprite["z"])\n'
                '\n'
                'names = [s["name"] for s in draw_order(scene)]\n'
                'assert names == ["sky", "tree", "hero", "hud"]\n'
                'print("painter algorithm: back to front by depth")'
            ),
            variant_b='give the hud a negative z and rerun — what draws underneath the world?',
            variant_c='add a "visible" flag and filter hidden sprites before sorting, then print a culled draw list',
            mistakes=[
                "Sorting by creation order instead of depth, so distant objects draw over near ones.",
                "Redrawing a full-screen background beneath another full-screen layer, wasting overdraw.",
                "Interleaving draws that share a texture, breaking batching that a single grouped pass would allow.",
            ],
            q1=(
                "What does the painter's algorithm guarantee about the final image?",
                "Nearer sprites are drawn after farther ones, so they correctly cover the ones behind them.",
            ),
            homework=(
                "Write `render_list(sprites)` that returns the names of the visible sprites sorted from farthest "
                "to nearest. Build a scene with at least four sprites, print the list, and comment which line "
                "performs the depth sort."
            ),
            patterns=["def ", "sorted(", "print("],
            mapping=(
                "Two-dimensional engines sort sprites by depth every frame; the same ordering logic feeds a real "
                "renderer's command buffer once a GPU is present."
            ),
        ),
        157: dict(
            topic="Testing game logic headless",
            idea=(
                "A game that can only be tested by playing it is a game that will be tested rarely and badly. The "
                "answer is to run the logic with no window at all. This works only if the earlier separation was "
                "respected: update mutates state and render draws it, and they never call each other. If the "
                "update step is a pure function from state to state, a test can start from a fixture, run it a "
                "fixed number of times, and assert on the result. No window opens, no clock is read, no graphics "
                "driver is touched, and the whole test runs in milliseconds. That speed changes behaviour: tests "
                "you can run in a fraction of a second get run on every edit, while tests that need a person to "
                "click through a level get run before a release, if that. Headless testing also makes failures "
                "reproducible. Because there is no timing and no input device, a failing assertion points at a "
                "state and a step number rather than at a feeling that something looked wrong. The discipline "
                "asks one thing of you, that the loop be drivable from outside. You pass in the state and the "
                "number of ticks, you get the final state back, and nothing about a screen is involved. Today you "
                "write that runner and prove a fixture does not move when a copy is advanced."
            ),
            code=(
                'def tick(state):\n'
                '    new = dict(state)\n'
                '    new["x"] += state["vx"]\n'
                '    new["ticks"] += 1\n'
                '    return new\n'
                '\n'
                'def run(start, n):\n'
                '    state = start\n'
                '    for _ in range(n):\n'
                '        state = tick(state)\n'
                '    return state\n'
                '\n'
                'start = {"x": 0, "vx": 2, "ticks": 0}\n'
                'final = run(start, 5)\n'
                'print("final x:", final["x"], "ticks:", final["ticks"])\n'
                'print("original x still:", start["x"])\n'
                'assert final["x"] == 10 and final["ticks"] == 5\n'
                'assert start["x"] == 0\n'
                'print("logic runs headless, no window and no clock")'
            ),
            variant_b='run the same fixture for twelve ticks and predict the final x before you print it',
            variant_c='make tick mutate the dictionary in place and explain why the original x assertion then fails',
            mistakes=[
                "Calling the renderer inside update, so the test needs a window and a graphics context.",
                "Reading real time inside the logic, so the same fixture produces different results on different runs.",
                "Writing tests that assert on printed text instead of on the returned state.",
            ],
            q1=(
                "What makes game logic testable without a display?",
                "The update step is a pure function from state to state, so a test can advance a fixture and assert on the result directly.",
            ),
            homework=(
                "Write `run_for(start, n)` that advances a state dictionary by n fixed ticks and returns the final "
                "state. Run it on two different starts, print both results, and comment which line keeps the "
                "original fixture unchanged."
            ),
            patterns=["def ", "for ", "return"],
            mapping=(
                "Continuous integration for games runs exactly these headless simulations; the renderer is stubbed "
                "out so thousands of logic tests can run on a build server with no display."
            ),
        ),
        158: dict(
            topic="Property based checks for rules",
            idea=(
                "A unit test checks one example; a property test checks a claim over a whole range of inputs. For "
                "game rules that is often the more honest question. You do not want to know that damage equals "
                "four for one roll; you want to know that damage is never negative, never exceeds the die, and "
                "that more armour never deals more damage. Those are properties, and they can be checked against "
                "hundreds of generated cases in a loop. The payoff is that properties catch the inputs you would "
                "never think to write by hand, especially combined edge cases. The discipline is to state the "
                "invariant as code: choose a range, generate inputs, apply the rule, and assert the claim holds "
                "for every one. When a property fails, the seed and the input are the counterexample, and fixing "
                "the rule is then a matter of arithmetic rather than guesswork. A property can also be about "
                "relationships rather than values: healing then damaging cannot leave more health than healing "
                "alone, and a stronger attacker never does less than a weaker one given the same roll. Ordinary "
                "range checks and monotonicity checks cover a surprising amount of balance logic. Because this "
                "course is deterministic, generated cases come from a seeded generator, so a failing run repeats "
                "exactly. Today you assert a bound over a thousand seeded rolls and print the violation count."
            ),
            code=(
                'import random\n'
                '\n'
                'def damage(rng, armor):\n'
                '    raw = rng.randint(1, 12)\n'
                '    return max(0, raw - armor)\n'
                '\n'
                'rng = random.Random(7)\n'
                'violations = 0\n'
                'for _ in range(1000):\n'
                '    dealt = damage(rng, 3)\n'
                '    if dealt < 0 or dealt > 12:\n'
                '        violations += 1\n'
                '\n'
                'print("checked 1000 seeded rolls")\n'
                'print("invariant violations:", violations)\n'
                'assert violations == 0\n'
                'print("damage stays between zero and the die size")'
            ),
            variant_b='assert instead that a higher armour value never yields more damage, still over many rolls',
            variant_c='widen the die to a hundred sides and check the new upper bound property still holds',
            mistakes=[
                "Testing a single hand-picked input and calling the rule verified.",
                "Stating a property that is subtly false, such as assuming damage can never be zero.",
                "Using unseeded randomness in a property check, so a failure cannot be reproduced.",
            ],
            q1=(
                "What is the difference between a unit test and a property check?",
                "A unit test asserts one expected output; a property check asserts an invariant holds across many generated inputs.",
            ),
            homework=(
                "Write `never_negative(seed, armor, trials)` that draws many damage values from one seeded "
                "generator and returns whether every result stayed non-negative. Call it with two armour values, "
                "print both booleans, and comment which line states the invariant."
            ),
            patterns=["def ", "random.Random", "return"],
            mapping=(
                "Balance teams run property and fuzz checks against combat formulas precisely because the "
                "pathological input is the one a player will eventually find."
            ),
        ),
        159: dict(
            topic="Deterministic netcode basics",
            idea=(
                "Networking a game begins with a deceptively simple requirement: two machines that received the "
                "same inputs in the same order must compute the same state. That is determinism, and it is the "
                "foundation of lockstep, of replays, and of the regression tests from the previous day. The "
                "pattern is to send inputs rather than positions, then let each side simulate forward. Sending "
                "positions is simple but huge and lets the two sides disagree; sending inputs is tiny and, if the "
                "simulation is deterministic, keeps the sides in agreement by construction. The catch is that "
                "determinism is fragile and the usual culprits are mundane. Floating-point arithmetic that "
                "rounds differently across platforms, unordered collections iterated in a different order, a "
                "random generator seeded from a clock, and integration that depends on elapsed real time rather "
                "than a fixed step. Each one breaks the promise silently. When both peers share the same code, "
                "the same fixed step and the same seed and apply the same inputs, the state matches to the bit. "
                "This is why the course insisted on fixed timesteps and seeded randomness long before networking "
                "appeared. Today you run the same input list through two seeded simulations and prove they agree, "
                "then show a different seed diverges, which is exactly the failure a desync would produce."
            ),
            code=(
                'import random\n'
                '\n'
                'def simulate(seed, inputs):\n'
                '    rng = random.Random(seed)\n'
                '    x = 0\n'
                '    for move in inputs:\n'
                '        x += move\n'
                '        x += rng.randint(0, 1)\n'
                '    return x\n'
                '\n'
                'inputs = [1, 1, -1, 2, 0]\n'
                'a = simulate(99, inputs)\n'
                'b = simulate(99, list(inputs))\n'
                'c = simulate(100, inputs)\n'
                'print("client A:", a)\n'
                'print("client B:", b)\n'
                'print("other seed:", c)\n'
                'assert a == b\n'
                'print("same seed and inputs rebuild the same state")'
            ),
            variant_b='append two more moves to the input list and check the two clients still agree',
            variant_c='replace the seeded generator with a clock-seeded one and explain why the clients now desync',
            mistakes=[
                "Sending positions over the network instead of the inputs that produced them.",
                "Seeding the random generator from the clock, so peers start from different sequences.",
                "Iterating an unordered collection when applying inputs, so order differs between machines.",
            ],
            q1=(
                "Why does lockstep send inputs rather than positions?",
                "Inputs are tiny and, with a deterministic simulation, each peer recomputes the identical state, so there is nothing to reconcile.",
            ),
            homework=(
                "Write `agree(seed, inputs)` that runs the same input list through two generators seeded identically "
                "and returns whether the two final states match. Test it with a matching seed and a mismatched one, "
                "print both booleans, and comment which line guarantees the shared starting point."
            ),
            patterns=["def ", "random.Random", "return"],
            mapping=(
                "Real-time strategy games are built on lockstep for exactly this reason, and desyncs are almost "
                "always a hidden source of nondeterminism rather than the network itself."
            ),
        ),
        160: dict(
            topic="Data oriented design tradeoffs",
            idea=(
                "Object-oriented design groups the fields of one thing together: an entity holds its position, "
                "velocity and health in one object. Data oriented design asks what the hot loop actually reads and "
                "lays data out to serve that access pattern instead. The classic contrast is an array of structs "
                "against a struct of arrays. In the first, iterating over positions also drags velocity, health "
                "and sprite data through memory even when the loop only moves x. In the second, each field lives "
                "in its own list, so a movement system streams a contiguous run of x values and y values and never "
                "touches the rest. The benefit is locality: modern processors fetch memory in blocks, so reading "
                "only the needed field wastes less bandwidth and fits more useful data in cache. The trade-off is "
                "ergonomics. Splitting fields makes one logical entity into several parallel arrays, so adding a "
                "component and deleting an entity are now operations across many lists, and simple code becomes "
                "index bookkeeping. It is rarely worth it for a few hundred entities and often decisive for a few "
                "hundred thousand. The honest framing is not which is better but which access pattern dominates. "
                "Today you move every entity on only one axis and count the values each layout touches."
            ),
            code=(
                'positions = [(0, 0), (1, 0), (2, 0), (3, 0)]\n'
                'xs = [0, 1, 2, 3]\n'
                '\n'
                'aos_touched = 0\n'
                'for i, (x, y) in enumerate(positions):\n'
                '    positions[i] = (x + 1, y)\n'
                '    aos_touched += 2\n'
                '\n'
                'soa_touched = 0\n'
                'for i in range(len(xs)):\n'
                '    xs[i] += 1\n'
                '    soa_touched += 1\n'
                '\n'
                'print("array-of-structs values touched:", aos_touched)\n'
                'print("struct-of-arrays values touched:", soa_touched)\n'
                'assert soa_touched < aos_touched\n'
                'print("moving only x touches half the values in column layout")'
            ),
            variant_b='add a speed list beside xs and integrate both, then compare the two touched counts again',
            variant_c='keep the array of structs but add a third unused field and show the movement loop still drags it',
            mistakes=[
                "Adopting column layout for a small entity count, paying the bookkeeping for no measurable win.",
                "Scattering a hot field across many lists, so the loop jumps between allocations instead of streaming.",
                "Rewriting simple readable code into parallel arrays before a profiler has shown it matters.",
            ],
            q1=(
                "What access pattern makes a struct of arrays faster than an array of structs?",
                "When a system reads one field of many entities, the column layout keeps that field contiguous in memory instead of dragging the unused fields along.",
            ),
            homework=(
                "Write `move_x(columns, delta)` that adds delta to every value of a single x column in place and "
                "returns how many values it touched. Run it on a small column list, print the count and the result, "
                "and comment which line performs the in-place update."
            ),
            patterns=["def ", "return", "print("],
            mapping=(
                "High-performance engines store components in contiguous arrays for exactly this reason; it is the "
                "same cache locality idea behind a database choosing a column store."
            ),
        ),
        161: dict(
            topic="Build and packaging concepts",
            idea=(
                "A game is not finished when it runs from your editor; it is finished when a stranger can install "
                "and launch it. Between those two points sits packaging, and packaging is mostly about making the "
                "build reproducible. A manifest is the small document that names the product, its version, the "
                "entry point that starts it, the dependencies it needs, and the platforms it targets. Having that "
                "in one place lets a script build the same artifact from the same source every time. Version "
                "numbers deserve a moment because they are compared, not just displayed. A version like one point "
                "two point zero is really three integers, and comparing strings would put ten before nine; parsing "
                "them to a tuple fixes the ordering and makes it trivial to ask whether an update is available. "
                "Dependencies are the other half. Every one you add is code you ship, must license, and must keep "
                "working; listing them explicitly turns an implicit assumption into something a build can check. A "
                "good release also names its targets, because the same source must be assembled differently for "
                "each platform, and forgetting one is how a game ships for one set of players and not another. "
                "Today you define a tiny manifest, parse its version into a tuple, and enumerate its targets, which "
                "is the whole idea in miniature."
            ),
            code=(
                'manifest = {\n'
                '    "name": "skyward",\n'
                '    "version": "1.2.0",\n'
                '    "entry": "main.py",\n'
                '    "deps": ["requests"],\n'
                '    "targets": ["windows", "linux"],\n'
                '}\n'
                '\n'
                'def parse_version(text):\n'
                '    return tuple(int(part) for part in text.split("."))\n'
                '\n'
                'print("packaging", manifest["name"], parse_version(manifest["version"]))\n'
                'for target in sorted(manifest["targets"]):\n'
                '    print("build for", target)\n'
                'print("dependencies:", len(manifest["deps"]))\n'
                'assert parse_version("1.2.0") > parse_version("1.1.9")\n'
                'print("a manifest names version, entry, deps and targets")'
            ),
            variant_b='add a third target and a second dependency, then print the updated counts',
            variant_c='bump the version to 2.0.0, parse it, and explain why string comparison would give the wrong answer',
            mistakes=[
                "Comparing version strings directly, so version ten sorts before version nine.",
                "Shipping undeclared dependencies, so the game works on your machine and fails on a fresh one.",
                "Building for one platform and discovering the others were never listed in the target set.",
            ],
            q1=(
                "Why parse a version string into a tuple of integers?",
                "Tuple comparison orders numeric components correctly, so a later version always compares greater, unlike lexicographic string comparison.",
            ),
            homework=(
                "Write `parse_version(text)` that splits a dotted version string and returns a tuple of integers, "
                "and `is_newer(candidate, current)` that returns whether the candidate is greater. Print two "
                "comparisons, and comment which line handles the numeric conversion."
            ),
            patterns=["def ", "split(", "return"],
            mapping=(
                "Steam, itch.io and console stores all consume a manifest and a versioned build; a reproducible "
                "packaging step is the difference between a demo and a product."
            ),
        ),
        162: dict(
            topic="Porting across platforms",
            idea=(
                "Porting is the work of making one codebase behave correctly on machines that differ in small, "
                "infuriating ways. The failures are rarely dramatic. One platform treats file names as "
                "case-insensitive, so code that loads Sprite dot P N G works there and fails on another. One "
                "platform uses a backslash as the path separator and another a forward slash. One treats an "
                "integer as thirty-two bits and another as sixty-four. One offers fewer hardware threads. The "
                "mature response is not to sprinkle special cases through the code but to probe capabilities once "
                "at startup and branch on the result, so platform knowledge lives in exactly one place. A "
                "capability probe answers questions: are paths case sensitive, how many threads are available, "
                "which byte order is native. The rest of the game then asks about the capability, never about the "
                "platform name, which keeps the special cases few and testable. This also makes a new platform "
                "cheap to add, because it is a new entry in the probe rather than edits scattered across the "
                "codebase. The same principle covers data: store paths in a canonical form and normalise at the "
                "boundary, and keep save files free of anything platform-specific. Today you probe two toy "
                "platforms for case sensitivity and thread count and adapt a file name accordingly, printing both "
                "outcomes from one code path."
            ),
            code=(
                'def capabilities(platform):\n'
                '    table = {\n'
                '        "windows": {"case_insensitive": True, "threads": 4},\n'
                '        "linux": {"case_insensitive": False, "threads": 8},\n'
                '    }\n'
                '    return table.get(platform, {"case_insensitive": False, "threads": 1})\n'
                '\n'
                'def safe_name(name, caps):\n'
                '    return name.lower() if caps["case_insensitive"] else name\n'
                '\n'
                'for platform in ("windows", "linux"):\n'
                '    caps = capabilities(platform)\n'
                '    print(platform, "->", safe_name("Sprite.PNG", caps), "threads", caps["threads"])\n'
                '\n'
                'assert safe_name("Sprite.PNG", capabilities("windows")) == "sprite.png"\n'
                'assert safe_name("Sprite.PNG", capabilities("linux")) == "Sprite.PNG"\n'
                'print("probe capabilities once, branch on the capability not the platform")'
            ),
            variant_b='add a third platform with two threads and case-insensitive paths, then print its line',
            variant_c='add a native byte order field to each probe and print which platforms agree',
            mistakes=[
                "Testing the platform name throughout the code instead of a probed capability.",
                "Hard-coding a path separator, so the game cannot find its own data on another platform.",
                "Assuming an integer is a fixed width when the platform may define it differently.",
            ],
            q1=(
                "Why branch on a probed capability instead of on the platform name?",
                "Capabilities describe the behaviour the code actually depends on, so the special case stays in one probe and a new platform needs no new branches.",
            ),
            homework=(
                "Write `normalise_name(name, case_insensitive)` that returns a lowercased name when the flag is "
                "true and the original otherwise, plus a `probe(platform)` that returns that flag for two named "
                "platforms. Print the result for both, and comment which line branches on the capability."
            ),
            patterns=["def ", "return", "print("],
            mapping=(
                "Porting a title to consoles means exactly this kind of capability probing; studios centralise "
                "the differences so the gameplay code stays one shared, testable body."
            ),
        ),
        163: dict(
            topic="Regression tests for balance",
            idea=(
                "Balance changes are the most common edit a live game receives and the easiest way to break "
                "something silently. A regression test for balance works like a regression test for code: you "
                "lock in the numbers you are happy with as a baseline, then check that a later change does not "
                "move them by more than you intended. The tricky part is that balance is inherently approximate, "
                "so the assertion is not equality. A test compares the measured outcome against the baseline "
                "within a tolerance, and a change that pushes a matchup outside that tolerance fails, which is "
                "the signal you want: this edit changed the game more than it claimed to. The measurement itself "
                "must be reproducible, and that is why seeded simulation and fixed steps matter. If the same "
                "version produces a different win rate each run, the baseline is meaningless and every test "
                "flakes. With a seeded generator the measurement is stable, so a real difference is a real "
                "regression rather than noise. Good baselines also record why they were chosen, so a future "
                "designer can tell whether a drift is a bug or a deliberate change that should update the "
                "baseline. Today you measure a toy duel over many seeded trials and compare the result to a "
                "locked baseline, printing the drift."
            ),
            code=(
                'import random\n'
                '\n'
                'baseline = {"knight": 0.62, "archer": 0.51, "mage": 0.47}\n'
                '\n'
                'def win_rate(power, enemy, trials, seed):\n'
                '    rng = random.Random(seed)\n'
                '    wins = 0\n'
                '    for _ in range(trials):\n'
                '        if rng.randint(1, 20) + power > rng.randint(1, 20) + enemy:\n'
                '            wins += 1\n'
                '    return wins / trials\n'
                '\n'
                'measured = {name: round(win_rate(p, 6, 2000, 1), 2)\n'
                '            for name, p in {"knight": 8, "archer": 4, "mage": 2}.items()}\n'
                'drift = {k: round(abs(measured[k] - baseline[k]), 2) for k in measured}\n'
                '\n'
                'print("measured:", measured)\n'
                'print("drift:", drift)\n'
                'assert measured["knight"] == max(measured.values())\n'
                'assert drift["mage"] > 0.1\n'
                'print("a locked baseline turns a balance shift into a failing test")'
            ),
            variant_b='raise the archer power by two and rerun — does its drift shrink toward the baseline?',
            variant_c='loosen the tolerance to a quarter and explain why too wide a band hides real regressions',
            mistakes=[
                "Measuring balance with unseeded randomness, so the baseline moves every run and tests flake.",
                "Asserting exact equality for an approximate quantity, so any harmless jitter fails the build.",
                "Updating the baseline without recording why, so a real regression is silently blessed.",
            ],
            q1=(
                "Why does a balance regression test compare against a tolerance rather than an exact value?",
                "Balance outcomes are approximate, so a tolerance catches meaningful shifts while ignoring harmless measurement jitter.",
            ),
            homework=(
                "Write `measure(power, enemy, seed)` that returns a win rate over a fixed number of seeded trials, "
                "and `drift(measured, baseline)` that returns the absolute difference. Print the drift for two "
                "matchups, and comment which line makes the measurement reproducible."
            ),
            patterns=["def ", "random.Random", "return"],
            mapping=(
                "Live-service teams keep golden balance numbers and flag any patch that moves a character outside "
                "its expected win rate, which is this test running at scale."
            ),
        ),
        164: dict(
            topic="Review: performance and porting checklist",
            idea=(
                "This phase covered a lot of ground, and the thread running through it is discipline: measure "
                "before you optimise, keep behaviour reproducible, and make platform assumptions explicit. A "
                "checklist turns that thread into something you can actually run before declaring a build ready. "
                "The items are not arbitrary. A fixed timestep keeps physics and replays stable. A pool in the hot "
                "path removes per-frame allocation. Profiling before optimising keeps effort pointed at the real "
                "bottleneck. A stored seed makes replays and balance tests reproducible. A headless test suite "
                "means logic can be checked without a window. Portable path handling means the game finds its data "
                "on more than your own machine. None of these is glamorous, and each one, skipped, becomes a bug "
                "report later. The value of the checklist is that it makes a missed item visible as a named "
                "failure rather than a vague worry. You compute which items pass, print the failures, and the "
                "build either is or is not ready. Today's example is that checklist in code: a small dictionary "
                "of checks, a filter for the failures, and a printed verdict. The list is deliberately short, "
                "because a checklist nobody finishes is worse than a short one everybody runs."
            ),
            code=(
                'checklist = {\n'
                '    "fixed timestep": True,\n'
                '    "pooled hot-path objects": True,\n'
                '    "profiled before optimising": True,\n'
                '    "seed stored for replay": False,\n'
                '    "tested headless": True,\n'
                '    "portable paths": True,\n'
                '}\n'
                '\n'
                'failed = [name for name, ok in checklist.items() if not ok]\n'
                'print("checks:", len(checklist))\n'
                'for name in failed:\n'
                '    print("FAIL:", name)\n'
                'print("passed:", len(checklist) - len(failed))\n'
                'assert failed == ["seed stored for replay"]\n'
                'print("a shipping checklist names what still blocks the build")'
            ),
            variant_b='mark two more items as false and print the larger failure list as the release blocker set',
            variant_c='split the checklist into performance and porting groups and print a count for each group',
            mistakes=[
                "Keeping a checklist so long that nobody runs it before a release.",
                "Treating a failed check as a warning instead of a blocker the build must clear.",
                "Fixing the checklist items without a test that keeps them fixed on the next change.",
            ],
            q1=(
                "What is the point of a short release checklist for performance and porting?",
                "It makes each known risk a named pass or fail, so a gap is a visible blocker instead of a vague worry discovered after shipping.",
            ),
            homework=(
                "Write `blockers(checklist)` that takes a name-to-boolean dictionary and returns the sorted names "
                "of the checks that failed. Run it on one passing and one failing checklist, print the blockers "
                "each time, and comment which line filters the failures."
            ),
            patterns=["def ", "return", "print("],
            mapping=(
                "Studios run exactly this kind of pre-release gate; the checks are the lessons of the whole phase "
                "turned into a pass or fail a producer can read."
            ),
        ),
    },
)
