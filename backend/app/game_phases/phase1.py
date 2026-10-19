"""Game State and Loops, days 75-89: the mutable world and the scheduler around it.

Every example is stdlib-only, offline and deterministic (fixed seeds, supplied
timings, no clock), so the applier executes it and gets the same output on every
run. One idea, one runnable fixture, and one named homework function per day.
"""

PHASE = (
    "Game State and Loops",
    "Build one explicit world state that a deterministic loop can update, render, save, inspect and replay.",
    {
        75: dict(
            topic="Orientation: what a game loop owns",
            idea=(
                "A game loop looks like three lines of plumbing and is actually the contract that keeps a game "
                "honest. It owns time: deciding how much simulated time passes before the world changes. It owns "
                "the order of work: read input, update state, then present the result. It owns termination: "
                "knowing when a session is over instead of running until a window closes. Everything else — "
                "physics, AI, scoring, art — is a guest inside that schedule. When people say a game feels tight, "
                "they are often describing a loop with a steady tick and cheap presentation. When a prototype "
                "becomes unmaintainable, the loop usually grew extra responsibilities, such as saving, networking "
                "or menu logic, until nobody could say what runs in which order. Today's example is deliberately "
                "tiny: a turn-based skirmish that runs a fixed number of ticks and prints state and a rendering "
                "line each tick. The point is not the combat but the ownership boundary. If you can point at the "
                "loop and say it decides time and order and nothing else, later lessons about fixed timesteps, "
                "systems and replays will slot in without a rewrite. Keep that boundary and the rest of the phase "
                "is adding citizens to a city that already has a clear government."
            ),
            code=(
                'def read_input(tick):\n'
                '    return "attack" if tick % 2 == 0 else "wait"\n'
                '\n'
                'def update(state, action):\n'
                '    hp = state["hp"]\n'
                '    if action == "attack":\n'
                '        hp = max(0, hp - 3)\n'
                '    return {"tick": state["tick"] + 1, "hp": hp}\n'
                '\n'
                'def render(state):\n'
                '    return "tick=" + str(state["tick"]) + " hp=" + str(state["hp"])\n'
                '\n'
                'state = {"tick": 0, "hp": 10}\n'
                'for _ in range(4):\n'
                '    state = update(state, read_input(state["tick"]))\n'
                '    print(render(state))\n'
                '\n'
                'assert state["hp"] == 4\n'
                'print("the loop owned time, order and termination")'
            ),
            variant_b="run six ticks instead of four and predict the hp before running",
            variant_c="make wait restore one hp and print a different action sequence",
            mistakes=[
                "Letting the loop contain game rules instead of only scheduling them.",
                "Saving, loading or menu logic growing inside the per-frame loop.",
                "Looping without a tick budget or termination condition.",
            ],
            q1=(
                "What three responsibilities does a minimal game loop own?",
                "It owns simulated time, the order of input/update/render work, and the termination condition.",
            ),
            homework=(
                "Write `advance` with the signature `def advance(state, ticks):`. It should run the update "
                "function exactly the requested number of ticks, print each rendered state, and return the final "
                "state together with the number of ticks actually run. Comment which line keeps the loop bounded."
            ),
            patterns=["def advance", "return", "print("],
            mapping=(
                "Every engine from pygame to Unity wraps this schedule; the loop is the one place that decides "
                "tick order, so keeping it boring is a feature."
            ),
        ),
        76: dict(
            topic="Entities and components as data",
            idea=(
                "An entity is an identifier, and its components are plain data attached to that identifier. That "
                "sentence is the whole idea behind data-oriented design. Instead of a deep class hierarchy where "
                "a Goblin extends Monster extends Actor, you store a table of entities and a table per component: "
                "position, health, sprite, ai. A goblin is simply entity seven with a position row and a health "
                "row. The benefit is composition without inheritance: want a trap that is also damageable and "
                "visible? Give it those components rather than hunting for a common ancestor. The second benefit "
                "is tooling. Plain data serialises, diffs and inspects easily, so a save file is a few "
                "dictionaries and a debug panel can show any component without special cases. The third benefit "
                "is that systems can process one component table at a time, which is cache friendly in large "
                "games and, more importantly here, easy to reason about in small ones. Today you build a "
                "roguelike entity store with separate dictionaries for positions and health, add a couple of "
                "monsters, and print the joined view. Notice that nothing in the data knows how to draw or how to "
                "move. Behaviour lives elsewhere and reads these tables, and that separation is what the next "
                "lessons depend on."
            ),
            code=(
                'entities = ["goblin", "rat"]\n'
                'positions = {"goblin": (3, 2), "rat": (5, 5)}\n'
                'health = {"goblin": 6, "rat": 2}\n'
                '\n'
                'def living(ids, health):\n'
                '    return [name for name in ids if health.get(name, 0) > 0]\n'
                '\n'
                'def describe(name, positions, health):\n'
                '    x, y = positions[name]\n'
                '    return name + " at (" + str(x) + "," + str(y) + ") hp=" + str(health[name])\n'
                '\n'
                'health["rat"] = max(0, health["rat"] - 5)\n'
                'for name in living(entities, health):\n'
                '    print(describe(name, positions, health))\n'
                '\n'
                'print("alive:", living(entities, health))\n'
                'assert living(entities, health) == ["goblin"]\n'
                'print("components are data, not behaviour")'
            ),
            variant_b="add a third entity with a speed component and print its description",
            variant_c="store components as one dictionary of rows per entity and explain the trade-off",
            mistakes=[
                "Building a class hierarchy for every monster variant instead of composing components.",
                "Putting movement or drawing methods on the component data itself.",
                "Duplicating an entity's id inside every component row inconsistently.",
            ],
            q1=(
                "Why is an entity usually an identifier rather than a big object?",
                "The identifier lets independent component tables join cheaply, so behaviour can be added by attaching data instead of changing a class.",
            ),
            homework=(
                "Write `def spawn(entities, positions, health, name, x, y, hp):` that adds one entity to all "
                "three tables and returns them. Spawn two entities, print the joined rows, damage one to zero, and "
                "comment which check filters the dead entity out of the listing."
            ),
            patterns=["def spawn", "return", "print("],
            mapping=(
                "Entity-component systems in Godot, Unity's DOTS and Bevy all separate stable ids from component "
                "tables; the same idea scales from two monsters to tens of thousands."
            ),
        ),
        77: dict(
            topic="The world state container",
            idea=(
                "The world state container is the single place a running game can be inspected. It gathers the "
                "clock, the entity tables, the current scene name, the random seed and any session counters into "
                "one addressable structure. That sounds bureaucratic until you need to save, replay or debug: "
                "each of those operations is just taking the container and doing something with it. A container "
                "also makes ownership explicit. If something is not in the world, it is configuration or an "
                "asset, and it should not change during play. Keeping resources out of the state prevents the "
                "classic bug where a level's static tile table is mutated and the next restart inherits the "
                "damage. Today's example is a small puzzle board with a player, crates, a score and a tick "
                "counter, all stored under named keys. The code reads and writes only through the container, "
                "prints a compact summary, and copies it before an edit to prove the original survives. The habit "
                "to take away is to define the container's shape early, in one place, and to resist adding "
                "globals later. A world that fits in one dictionary can be copied, compared and serialised, which "
                "is exactly what saves and replays require."
            ),
            code=(
                'def make_world():\n'
                '    return {"tick": 0, "scene": "board", "player": (1, 1),\n'
                '            "crates": [(2, 2)], "score": 0}\n'
                '\n'
                'world = make_world()\n'
                'world["tick"] += 1\n'
                'world["player"] = (2, 1)\n'
                'world["score"] += 10\n'
                '\n'
                'clone = dict(world)\n'
                'clone["crates"] = list(world["crates"])\n'
                'clone["crates"].append((0, 0))\n'
                '\n'
                'print("tick", world["tick"], "scene", world["scene"], "score", world["score"])\n'
                'print("original crates:", world["crates"])\n'
                'print("clone crates:", clone["crates"])\n'
                '\n'
                'assert world["crates"] == [(2, 2)] and world["tick"] == 1\n'
                'print("one container holds the mutable world")'
            ),
            variant_b="add a seed key and print it alongside the tick and scene",
            variant_c="nested-copy the crate list through a helper and explain shallow versus deep claims",
            mistakes=[
                "Keeping half the mutable world in module globals outside the container.",
                "Storing static level data inside the container and mutating it during play.",
                "Copying the container shallowly and assuming the nested lists are independent.",
            ],
            q1=(
                "Why should the mutable world live in one container?",
                "A single container can be copied, compared, saved, replayed and inspected, and it makes ownership of every changing value explicit.",
            ),
            homework=(
                "Write `def reset_world(world):` that returns a fresh copy of the world with the tick and score "
                "at zero but the same scene and player start. Build a world, advance it, reset it, print both "
                "worlds, and comment which line proves the old container was not edited."
            ),
            patterns=["def reset_world", "return", "print("],
            mapping=(
                "Engines expose a scene tree or world object for exactly this reason; save systems and debuggers "
                "attach to that one root rather than chasing loose variables."
            ),
        ),
        78: dict(
            topic="Update versus render",
            idea=(
                "Update and render are two different questions. Update asks what is true now: where things moved, "
                "what died, which score changed. Render asks what the player sees: which characters, colours and "
                "text represent that truth. Mixing them creates a loop that can only run with a screen attached, "
                "and it hides bugs because drawing code starts making decisions. The separation has a practical "
                "test: update must be callable with no output device and produce the same state. If it cannot, "
                "some rule has leaked into presentation. A second test is that render must not mutate the world. "
                "If drawing changes anything, then pausing, resizing or running headless changes the game. "
                "Today's platformer example keeps a player position and a goal, runs a pure update for several "
                "ticks, and renders each state into a text row. Rendering is a function from state to strings; it "
                "has no side effects beyond returning them. The same state always yields the same row, which "
                "makes the output easy to assert on in tests. This discipline also sets up interpolation later: "
                "once render is a pure view of state, you can draw between two updates without touching the "
                "simulation. Treat render as a projection and update as the projector's subject."
            ),
            code=(
                'def update(state):\n'
                '    x, y = state["player"]\n'
                '    return {"player": (x + 1, y), "goal": state["goal"], "tick": state["tick"] + 1}\n'
                '\n'
                'def render(state):\n'
                '    width = 6\n'
                '    x, y = state["player"]\n'
                '    row = ["." for _ in range(width)]\n'
                '    row[x] = "P"\n'
                '    return "".join(row)\n'
                '\n'
                'state = {"player": (0, 0), "goal": 5, "tick": 0}\n'
                'for _ in range(3):\n'
                '    state = update(state)\n'
                '    print(render(state))\n'
                '\n'
                'before = render(state)\n'
                'assert render(state) == before and state["player"] == (3, 0)\n'
                'print("render is a pure view of state")'
            ),
            variant_b="move the player two cells per update and print the four rendered rows",
            variant_c="render the goal as a G and explain why render must not change the player position",
            mistakes=[
                "Mutating the world inside the render function so drawing changes the game.",
                "Calling render from inside update, which makes headless tests impossible.",
                "Storing the rendered text in the world instead of deriving it from state.",
            ],
            q1=(
                "What is the practical test that update and render are really separated?",
                "Update can run headless and produce the same state, while render can run repeatedly without changing that state.",
            ),
            homework=(
                "Write `def draw_board(state):` that returns a list of strings for a grid with the player, a "
                "goal and walls. Then write `def tick(state):` that advances the player without drawing. Print "
                "three frames and comment which function would still work with no screen attached."
            ),
            patterns=["def draw_board", "def tick", "print("],
            mapping=(
                "Engine render pipelines submit a description of the scene each frame; the simulation never calls "
                "the GPU directly, which is why dedicated servers can run the same update code."
            ),
        ),
        79: dict(
            topic="Input as a value",
            idea=(
                "Input should enter the game as a value, not as a callback that reaches into the world. A frame's "
                "input is a small record: which directions are held, which buttons were pressed this tick, maybe a "
                "pointer position. The loop reads the device once, builds that record, and passes it to update. "
                "Rules then consume a value they can inspect, which means a test can supply a scripted input "
                "without a keyboard and a replay can store a list of records. Edge detection belongs in this layer "
                "too. Held and pressed-this-frame are different facts, and conflating them produces double jumps "
                "and repeated menu activations. Today's example is a platformer step that takes a state and an "
                "input dictionary, applies horizontal movement and a jump only when the jump key is present, then "
                "prints the resulting positions. Two different input records produce visibly different trajectories from the "
                "same starting state. Notice that the step never asks the operating system anything. That purity "
                "is what lets the later replay lesson work: an input log plus the initial state is enough to "
                "reconstruct the run. Keep the input record small and explicit, and resist adding a global "
                "keyboard object that every rule can read."
            ),
            code=(
                'def step(state, inp):\n'
                '    x, y, vy = state["x"], state["y"], state["vy"]\n'
                '    if inp["left"]:\n'
                '        x -= 1\n'
                '    if inp["right"]:\n'
                '        x += 1\n'
                '    if inp["jump"] and y == 0:\n'
                '        vy = 2\n'
                '    y = max(0, y + vy)\n'
                '    vy = max(0, vy - 1) if y > 0 else 0\n'
                '    return {"x": x, "y": y, "vy": vy}\n'
                '\n'
                'inputs = [\n'
                '    {"left": False, "right": True, "jump": True},\n'
                '    {"left": False, "right": True, "jump": False},\n'
                '    {"left": True, "right": False, "jump": False},\n'
                ']\n'
                '\n'
                'state = {"x": 0, "y": 0, "vy": 0}\n'
                'for inp in inputs:\n'
                '    state = step(state, inp)\n'
                '    print("x", state["x"], "y", state["y"])\n'
                '\n'
                'assert state["x"] == 1 and state["y"] == 3\n'
                'print("input entered the simulation as a value")'
            ),
            variant_b="add a run modifier that doubles horizontal movement while held",
            variant_c="record the three input records and replay them from the start, printing both runs",
            mistakes=[
                "Having rules poll the keyboard directly instead of accepting an input record.",
                "Treating a held key as a fresh press every tick and triggering repeated jumps.",
                "Forgetting to clear one-frame press flags after the update.",
            ],
            q1=(
                "Why should input be captured once per frame and passed as data?",
                "A value can be scripted in tests, logged for replays and consumed by the same rule on any device.",
            ),
            homework=(
                "Write `def apply_inputs(state, inputs):` that applies a list of input dictionaries in order and "
                "returns the final state plus the list of positions visited. Run it with two different scripts, "
                "print both paths, and comment which line keeps the function independent of a real keyboard."
            ),
            patterns=["def apply_inputs", "return", "print("],
            mapping=(
                "Console and network input are both normalised into per-frame command records before gameplay "
                "code sees them; that is what makes remapping and replays possible."
            ),
        ),
        80: dict(
            topic="Events and message queues",
            idea=(
                "Events are facts that already happened, queued so that the system which caused them does not "
                "need to know who cares. A single rule might kill an enemy, and three unrelated systems might "
                "need that fact: score, audio, achievements. Calling all three from the damage rule couples "
                "combat to presentation and turns one change into many. A message queue inverts that: the rule "
                "appends a small record, and a drain step dispatches records to handlers. The queue also gives "
                "you ordering and a natural place to defer effects. If a handler spawns another event while the "
                "queue is being drained, you can decide whether it is processed this tick or the next, and that "
                "decision becomes explicit instead of accidental. Today's roguelike example drains a queue of "
                "pickups and traps, updates health and score, and prints both the dispatched events and the "
                "resulting state. Notice that the event description is data, not a callback: it can be printed, "
                "logged, serialised into a replay or sent over a network. The trade-off is indirection. A direct "
                "call is easier to follow for two systems, so start with calls and introduce a queue when the "
                "fan-out grows. Events are a tool for decoupling, not a law of nature."
            ),
            code=(
                'from collections import deque\n'
                '\n'
                'def drain(state, queue):\n'
                '    events = []\n'
                '    while queue:\n'
                '        event = queue.popleft()\n'
                '        events.append(event)\n'
                '        if event["kind"] == "pickup":\n'
                '            state["score"] += event["value"]\n'
                '        elif event["kind"] == "trap":\n'
                '            state["hp"] = max(0, state["hp"] - event["value"])\n'
                '    return state, events\n'
                '\n'
                'queue = deque([\n'
                '    {"kind": "pickup", "value": 5},\n'
                '    {"kind": "trap", "value": 3},\n'
                '    {"kind": "pickup", "value": 2},\n'
                '])\n'
                'state = {"score": 0, "hp": 10}\n'
                'state, events = drain(state, queue)\n'
                '\n'
                'for event in events:\n'
                '    print("handled", event["kind"], event["value"])\n'
                'print("score", state["score"], "hp", state["hp"])\n'
                '\n'
                'assert state["score"] == 7 and state["hp"] == 7 and not queue\n'
                'print("producers and consumers are decoupled")'
            ),
            variant_b="add a heal event kind and drain a queue that mixes all three kinds",
            variant_c="make a handler append a follow-up event and explain when it should be drained",
            mistakes=[
                "Calling every interested system directly from the rule that caused the event.",
                "Mutating the queue while iterating over it with a plain for loop.",
                "Putting callbacks or live objects in events instead of serialisable data.",
            ],
            q1=(
                "What does an event queue decouple?",
                "The producer of a fact from the consumers that react to it, so new listeners do not change the producing rule.",
            ),
            homework=(
                "Write `def drain_events(state, events):` that processes a list of dictionaries for move, damage "
                "and score events, returning the new state and a log of handled kinds. Feed it several events, "
                "print the log and final state, and comment which line preserves processing order."
            ),
            patterns=["def drain_events", "while ", "print("],
            mapping=(
                "Engines ship publish/subscribe or signal systems for the same reason; a queue also makes it "
                "trivial to record events into a replay or a telemetry stream."
            ),
        ),
        81: dict(
            topic="Scenes and transitions",
            idea=(
                "Scenes are named chunks of a game with their own state and rules: a title screen, a dungeon "
                "floor, a shop, a game-over summary. A transition is a request to leave one scene and enter "
                "another, often carrying a small payload such as which level to load or the final score. The "
                "healthy pattern is to make transitions data, not direct calls. A scene sets a pending request "
                "like enter the shop with forty gold and returns; the loop notices the request between updates "
                "and swaps the active scene. That avoids re-entrant updates where the old scene continues running "
                "after the new one started, and it gives one place to fade, save or validate. Scene state should "
                "be disposable. Shared facts such as the player's inventory belong to the session container, not "
                "to whichever scene happened to create them. Today's example drives a puzzle game through title, "
                "play and results scenes using a dictionary from scene name to a small handler. Transitions carry "
                "the score forward, and the code prints each scene visited. The important assertion is that after "
                "a transition the previous scene no longer updates. Scene switching looks trivial until it "
                "happens mid-frame; making the request a value is what keeps it predictable."
            ),
            code=(
                'def title(state):\n'
                '    return ("play", {"score": state["score"], "board": [1, 2, 3]})\n'
                '\n'
                'def play(state):\n'
                '    return ("results", {"score": state["score"] + sum(state["board"])})\n'
                '\n'
                'def results(state):\n'
                '    return (None, {"score": state["score"]})\n'
                '\n'
                'handlers = {"title": title, "play": play, "results": results}\n'
                'state = {"scene": "title", "score": 0}\n'
                'visited = []\n'
                'for _ in range(5):\n'
                '    visited.append(state["scene"])\n'
                '    name, payload = handlers[state["scene"]](state)\n'
                '    if name is None:\n'
                '        break\n'
                '    state = {"scene": name}\n'
                '    state.update(payload)\n'
                '\n'
                'print("visited:", visited)\n'
                'print("final score:", state["score"])\n'
                '\n'
                'assert visited == ["title", "play", "results"] and state["score"] == 6\n'
                'print("transitions are requests handled between updates")'
            ),
            variant_b="add a game-over scene reached when the score is below three",
            variant_c="carry a level number through two play scenes and print the scene trail",
            mistakes=[
                "Calling the next scene's update directly from inside the current scene.",
                "Keeping the player's inventory inside whichever scene created it.",
                "Switching scenes without deciding what state is carried across.",
            ],
            q1=(
                "Why should a scene transition be a request processed by the loop?",
                "The loop can swap scenes between updates, so the old scene never keeps running after the new one starts.",
            ),
            homework=(
                "Write `def change_scene(state, name, payload):` that stores a pending transition in the state "
                "instead of switching immediately, plus `def commit_scene(state):` that applies it. Print the "
                "state before and after the commit and comment which line delays the switch."
            ),
            patterns=["def change_scene", "def commit_scene", "print("],
            mapping=(
                "Scene managers in Godot and Unity queue load requests for the same reason: a switch mid-update "
                "would leave half the frame running old code."
            ),
        ),
        82: dict(
            topic="Fixed timestep in practice",
            idea=(
                "A fixed timestep means the simulation always advances by the same slice, typically a sixtieth or "
                "a fiftieth of a second. Real frames are uneven, so the loop keeps an accumulator of elapsed "
                "time, adds each frame's duration, and runs one fixed update for every full slice. Leftover time "
                "is carried into the next frame. The catch-up loop must be bounded: if a frame takes a second, "
                "running sixty updates at once turns a hiccup into a freeze, so engines cap the number of steps "
                "and discard the excess. This lesson simulates that with a list of frame durations rather than a "
                "clock, which makes the behaviour visible and testable. You will feed in fast frames, one slow "
                "frame and a pathological half-second frame, then print how many steps each produced and what "
                "remained in the accumulator. The leftovers are the interesting part, because they carry into the next "
                "frame. The interesting assertions are that the step count stays bounded "
                "and that the same frame durations always produce the same sequence of steps. Determinism comes "
                "from the fixed slice: identical inputs give identical states. That property is what makes "
                "physics, replays and automated balance tests trustworthy, and it is why the accumulator pattern "
                "outlives any particular engine."
            ),
            code=(
                'STEP_MS = 50\n'
                'MAX_STEPS = 3\n'
                '\n'
                'def run(frames):\n'
                '    accumulator = 0\n'
                '    report = []\n'
                '    for ms in frames:\n'
                '        accumulator += ms\n'
                '        steps = 0\n'
                '        while accumulator >= STEP_MS and steps < MAX_STEPS:\n'
                '            accumulator -= STEP_MS\n'
                '            steps += 1\n'
                '        report.append((ms, steps, accumulator))\n'
                '    return report\n'
                '\n'
                'frames = [16, 16, 120, 16, 500]\n'
                'for ms, steps, leftover in run(frames):\n'
                '    print("frame", ms, "steps", steps, "leftover", leftover)\n'
                '\n'
                'print("simulated ms:", sum(s * STEP_MS for _, s, _ in run(frames)))\n'
                'assert run(frames) == run(frames)\n'
                'assert all(s <= MAX_STEPS for _, s, _ in run(frames))\n'
                'print("same frames, same fixed steps")'
            ),
            variant_b="raise the step size to 100 ms and print the new step counts",
            variant_c="remove the step cap and explain what a half-second frame now costs",
            mistakes=[
                "Letting the catch-up loop run unbounded after a long frame.",
                "Dropping leftover time instead of carrying it into the next frame.",
                "Using wall-clock time inside rules instead of only in the accumulator.",
            ],
            q1=(
                "Why must the catch-up loop be capped?",
                "An unbounded catch-up turns one slow frame into a long burst of updates, which feels like a freeze and can spiral.",
            ),
            homework=(
                "Write `def simulate_frames(frames, step_ms, max_steps):` that returns a per-frame report of step "
                "count and leftover time. Run it on a fast sequence and on one containing a 400 ms frame, print "
                "both reports, and comment which line bounds the catch-up."
            ),
            patterns=["def simulate_frames", "while ", "print("],
            mapping=(
                "Unity's FixedUpdate and Godot's physics ticks are fixed-step accumulators; the cap is usually "
                "called a maximum allowed timestep or maximum substeps."
            ),
        ),
        83: dict(
            topic="Delta time and frame budget",
            idea=(
                "Delta time is how much real time passed since the previous frame, and a frame budget is how much "
                "time you have before the next one. Used carelessly, delta time multiplies every movement and "
                "makes behaviour depend on hardware. Used well, it belongs at the boundary: the loop converts "
                "wall-clock time into a fixed number of simulation steps, and only presentation, such as camera "
                "smoothing or a progress bar, consumes raw delta. The budget question is separate: a "
                "sixteen-millisecond budget at sixty frames per second means all update, render, audio and "
                "bookkeeping must fit inside it. Measuring is the first step, and you measure in the loop, not by "
                "guessing. Today's example takes a list of frame durations in milliseconds, computes the average, "
                "the worst case and how many frames exceeded a budget, and prints a small report. Because the "
                "durations are supplied, the result is deterministic and can be asserted. The lesson to carry "
                "forward is that optimisation without a measurement is superstition. Once you can see the worst "
                "frame and its cause, you can decide whether to reduce work, spread it across frames or lower the "
                "simulation rate. Delta time informs the loop; it should not silently leak into every rule."
            ),
            code=(
                'BUDGET_MS = 16\n'
                '\n'
                'def report(frames):\n'
                '    total = sum(frames)\n'
                '    over = [ms for ms in frames if ms > BUDGET_MS]\n'
                '    return {\n'
                '        "frames": len(frames),\n'
                '        "average": total / len(frames),\n'
                '        "worst": max(frames),\n'
                '        "over": len(over),\n'
                '    }\n'
                '\n'
                'data = [8, 12, 15, 40, 9, 11, 22]\n'
                'summary = report(data)\n'
                'print("frames", summary["frames"])\n'
                'print("average ms", round(summary["average"], 2))\n'
                'print("worst ms", summary["worst"], "over budget", summary["over"])\n'
                '\n'
                'assert summary["worst"] == 40 and summary["over"] == 2\n'
                'print("delta informs the loop, it does not leak into every rule")'
            ),
            variant_b="raise the budget to 24 ms and print the new over-budget count",
            variant_c="add a median calculation and explain why the average hides a spike",
            mistakes=[
                "Multiplying every rule by raw delta time, so behaviour changes with frame rate.",
                "Optimising without measuring which frame actually blew the budget.",
                "Reporting only the average and hiding a single long stall.",
            ],
            q1=(
                "Where should raw delta time be consumed, and where should it not?",
                "It belongs at the loop and presentation boundary; simulation rules should run on a fixed step instead.",
            ),
            homework=(
                "Write `def budget_report(frames, budget_ms):` returning frame count, worst frame, average and "
                "the indices of frames over budget. Run it on one smooth list and one with a spike, print both "
                "reports, and comment which value would have hidden the spike."
            ),
            patterns=["def budget_report", "return", "print("],
            mapping=(
                "Profilers in Unity, Godot and Unreal report per-frame milliseconds against a target budget, and "
                "the fix is chosen from that data rather than from intuition."
            ),
        ),
        84: dict(
            topic="Systems that run in order",
            idea=(
                "Systems are small functions that each own one concern: movement, collision, spawning, cleanup, "
                "scoring. A frame is a list of systems run in a defined order, and most gameplay bugs come from "
                "that order being implicit. Movement before collision means entities are tested where they are "
                "now. Collision before movement means they are tested where they were. Cleanup before scoring "
                "means dead enemies never award points. None of these is universally right, but each must be "
                "chosen and written down. A system should read and write only the parts of the state it owns, "
                "and it should be easy to disable for a test. Today's example is a tiny collection turn with two "
                "systems: movement and pickup collection. You will run them in the intended order, print the "
                "state, then run the same systems in the opposite order and show how the result differs. The "
                "comparison is the lesson. When systems are values in a list, order becomes data you can inspect, "
                "swap and test, rather than a fact buried in a long function. That is what makes a small codebase "
                "stay understandable as it grows, and it is why engine update order is documented rather than "
                "left to chance."
            ),
            code=(
                'def move(state):\n'
                '    state["entities"] = [\n'
                '        {"name": e["name"], "x": e["x"] + e["speed"], "hp": e["hp"]}\n'
                '        for e in state["entities"]\n'
                '    ]\n'
                '    return state\n'
                '\n'
                'def collect(state):\n'
                '    reached = [e for e in state["entities"] if e["x"] >= state["goal"]]\n'
                '    state["score"] += len(reached)\n'
                '    state["entities"] = [e for e in state["entities"] if e["x"] < state["goal"]]\n'
                '    return state\n'
                '\n'
                'def run(order, start):\n'
                '    state = {"entities": [dict(e) for e in start], "score": 0, "goal": 5}\n'
                '    for system in order:\n'
                '        state = system(state)\n'
                '    return state\n'
                '\n'
                'start = [{"name": "coin", "x": 3, "speed": 3, "hp": 1}]\n'
                'print("move then collect:", run([move, collect], start)["score"])\n'
                'print("collect then move:", run([collect, move], start)["score"])\n'
                '\n'
                'assert run([move, collect], start)["score"] == 1\n'
                'assert run([collect, move], start)["score"] == 0\n'
                'print("system order changes the result")'
            ),
            variant_b="add a cleanup system and place it before and after collect",
            variant_c="make the entity move twice per move system and compare both orders again",
            mistakes=[
                "Leaving system order undocumented so behaviour depends on list construction.",
                "Letting one system edit state owned by another system.",
                "Relying on dictionary iteration order for anything gameplay-relevant.",
            ],
            q1=(
                "Why does the order of systems belong in data rather than in a long function body?",
                "A list makes order explicit, swappable and testable, and comparing two orders shows its effect immediately.",
            ),
            homework=(
                "Write `def run_systems(state, systems):` that applies each system function in order and returns "
                "the state plus a per-system snapshot. Build three systems, run them in two different orders, "
                "print both snapshot lists, and comment which line makes the order explicit."
            ),
            patterns=["def run_systems", "for system in systems", "print("],
            mapping=(
                "Engines publish a fixed update order for scripts and physics; knowing it is often the difference "
                "between a consistent jump and a random one."
            ),
        ),
        85: dict(
            topic="Saving and loading state",
            idea=(
                "Saving is serialising the world state container; loading is rebuilding it. That is only clean if "
                "the state is plain data and the container's shape is explicit. A save file should hold facts, not "
                "objects with hidden behaviour: entity tables, the tick, the seed, the scene name, the inventory. "
                "Derived values such as is alive or a rendered string should be recomputed on load rather than "
                "stored, because duplicated truth drifts. Versioning matters from the first save. A small version "
                "number lets you migrate old files instead of crashing or silently misreading them. Today's "
                "example builds a small dungeon state, saves it with json.dumps into a string, loads it back with "
                "json.loads, and checks that the reloaded world equals the original. It then mutates the reloaded "
                "copy and proves the original is untouched, which catches the classic aliasing bug. It also prints the "
                "serialised text so the schema is visible. json is "
                "standard library and human readable, which makes it good for small saves and debugging, though "
                "it cannot represent sets or custom objects without conversion. The habit to take away is to keep "
                "the save schema beside the state schema, and to test a round trip every time the state changes."
            ),
            code=(
                'import json\n'
                '\n'
                'def make_world():\n'
                '    return {\n'
                '        "version": 1,\n'
                '        "tick": 4,\n'
                '        "seed": 42,\n'
                '        "scene": "crypt",\n'
                '        "player": {"hp": 7, "gold": 12},\n'
                '        "items": ["torch", "key"],\n'
                '    }\n'
                '\n'
                'def save(state):\n'
                '    return json.dumps(state, sort_keys=True)\n'
                '\n'
                'def load(text):\n'
                '    return json.loads(text)\n'
                '\n'
                'original = make_world()\n'
                'text = save(original)\n'
                'restored = load(text)\n'
                '\n'
                'print("saved characters:", len(text))\n'
                'print("restored scene:", restored["scene"], "gold:", restored["player"]["gold"])\n'
                'assert restored == original\n'
                '\n'
                'restored["player"]["gold"] = 1\n'
                'print("original gold after editing the copy:", original["player"]["gold"])\n'
                'assert original["player"]["gold"] == 12\n'
                'print("round trip produced an independent state")'
            ),
            variant_b="add a version 2 field and write a small migration from version 1",
            variant_c="save a set of visited rooms by converting it to a sorted list",
            mistakes=[
                "Storing derived values such as is_alive in the save and letting them drift from hp.",
                "Saving live objects with behaviour instead of plain data.",
                "Skipping a version field, so old saves break silently after a schema change.",
            ],
            q1=(
                "Why should a save contain facts rather than a rendered view or derived flags?",
                "Facts round-trip exactly and let derived values be recomputed, so duplicated truth cannot drift.",
            ),
            homework=(
                "Write `def save_load(state):` that serialises the state with json, deserialises it, and returns "
                "the restored copy and whether it equals the input. Add a version field, print the restored state, "
                "and comment which line proves the round trip is faithful."
            ),
            patterns=["def save_load", "json.dumps", "print("],
            mapping=(
                "Real save systems use the same shape with binary or compressed formats, plus a version and "
                "migration step so old players keep their progress."
            ),
        ),
        86: dict(
            topic="Debug overlays and inspection",
            idea=(
                "An overlay is a view of state that is always available and never authoritative. It shows the "
                "facts you would otherwise add print statements for: frame count, entity count, current scene, "
                "pending events, the last few inputs. The rule that keeps it useful is that the overlay only "
                "reads. Once overlay code mutates state or consumes events, it changes the game while you observe "
                "it, and the bug you were chasing disappears or moves. A good overlay is built from small "
                "formatter functions that take the state and return strings, so the same code can be printed to a "
                "console, shown in a corner of the screen or dumped into a test failure message. Today's example "
                "is a puzzle game state with a player, crates and a score, plus an inspect function that returns "
                "labelled lines and flags suspicious values such as a negative score or a player outside the "
                "board. The output is deterministic, which means a failing test can print the same overlay you saw "
                "while playing. This is cheap observability and it pays for itself the first time a value is not "
                "what you assumed. Build the overlay before you need it, not after a bug becomes mysterious."
            ),
            code=(
                'def overlay(state):\n'
                '    lines = [\n'
                '        "tick=" + str(state["tick"]),\n'
                '        "player=" + str(state["player"]),\n'
                '        "crates=" + str(len(state["crates"])),\n'
                '        "score=" + str(state["score"]),\n'
                '    ]\n'
                '    if state["score"] < 0:\n'
                '        lines.append("WARN negative score")\n'
                '    if not (0 <= state["player"][0] < 5):\n'
                '        lines.append("WARN player off board")\n'
                '    return lines\n'
                '\n'
                'healthy = {"tick": 3, "player": (2, 1), "crates": [(2, 2)], "score": 10}\n'
                'broken = {"tick": 3, "player": (9, 9), "crates": [], "score": -5}\n'
                '\n'
                'for line in overlay(healthy):\n'
                '    print("ok", line)\n'
                'for line in overlay(broken):\n'
                '    print("check", line)\n'
                '\n'
                'assert overlay(healthy)[-1] == "score=10"\n'
                'assert len(overlay(broken)) == 6\n'
                'print("the overlay reads state and never writes it")'
            ),
            variant_b="add a warning when the crate count is zero before the board is solved",
            variant_c="format the overlay as one compact line and print it for three states",
            mistakes=[
                "Letting the overlay consume events or tick the world while it displays.",
                "Printing from deep inside game rules instead of formatting from one state snapshot.",
                "Showing only happy values and hiding anomalies the overlay exists to catch.",
            ],
            q1=(
                "What is the one rule that keeps a debug overlay trustworthy?",
                "It must only read state; any mutation or event consumption changes the game while you observe it.",
            ),
            homework=(
                "Write `def inspect_world(state):` returning a list of labelled lines plus warnings for an empty "
                "entity list or a negative tick. Run it on one healthy and one broken state, print both, and "
                "comment which line proves the function does not modify its input."
            ),
            patterns=["def inspect_world", "return", "print("],
            mapping=(
                "Engine consoles and remote inspectors show live component values for the same reason; the best "
                "ones are read-only views over the same state the simulation uses."
            ),
        ),
        87: dict(
            topic="Deterministic replays",
            idea=(
                "A deterministic replay is a recording of inputs, not of the world. If the simulation is a pure "
                "function of state and input, then storing the initial state, the seed and the ordered input "
                "records is enough to reconstruct every frame. The requirements are strict: no wall-clock time "
                "inside rules, no unseeded randomness, no iteration over an unordered collection where order "
                "affects results, and no hidden global state. Replays are the cheapest possible test harness for a "
                "game. They catch regressions when a rule changes, they let a bug report travel as data, and they "
                "make balance changes measurable. Today's example records a seeded roguelike run: a short list of "
                "moves applied tick by tick, with a snapshot of position and gold after each. The code then "
                "replays the same input list from the same seed and asserts that every snapshot matches. It also "
                "perturbs one input and shows the run diverging, which proves the comparison is meaningful rather "
                "than trivially true. The practical habit is to record inputs at the loop boundary in one place, "
                "and to keep a few short golden replays in the test suite. They are small, fast to run, and they fail "
                "loudly when behaviour changes."
            ),
            code=(
                'import random\n'
                '\n'
                'def step(state, move, rng):\n'
                '    x = state["x"] + move[0]\n'
                '    y = state["y"] + move[1]\n'
                '    gold = state["gold"] + rng.randint(0, 2)\n'
                '    return {"x": x, "y": y, "gold": gold, "tick": state["tick"] + 1}\n'
                '\n'
                'def run(seed, moves):\n'
                '    rng = random.Random(seed)\n'
                '    state = {"x": 0, "y": 0, "gold": 0, "tick": 0}\n'
                '    snaps = []\n'
                '    for move in moves:\n'
                '        state = step(state, move, rng)\n'
                '        snaps.append((state["x"], state["y"], state["gold"]))\n'
                '    return snaps\n'
                '\n'
                'moves = [(1, 0), (0, 1), (-1, 0), (0, -1)]\n'
                'first = run(7, moves)\n'
                'second = run(7, moves)\n'
                'perturbed = run(7, [(2, 0), (0, 1), (-1, 0), (0, -1)])\n'
                '\n'
                'print("first:", first)\n'
                'print("replay matches:", first == second)\n'
                'print("perturbed differs:", first != perturbed)\n'
                '\n'
                'assert first == second and first != perturbed\n'
                'print("seed plus inputs reconstructs the run")'
            ),
            variant_b="change only the seed and print the two snapshot lists side by side",
            variant_c="record one move twice and explain which part of the state diverges first",
            mistakes=[
                "Calling the global random module so the sequence depends on unrelated code.",
                "Reading wall-clock time inside a rule that a replay must reproduce.",
                "Recording world snapshots instead of the inputs that generated them.",
            ],
            q1=(
                "What must a replay store for a deterministic simulation?",
                "The initial state, the random seed and the ordered input records; the world itself is recomputed.",
            ),
            homework=(
                "Write `def replay(seed, moves):` that returns one snapshot per move, then write "
                "`def check_replay(seed, moves):` that runs it twice and returns whether the snapshots match. "
                "Print the result for a good run and for one with a changed move, and comment which line fixes the "
                "random sequence."
            ),
            patterns=["def replay", "random.Random", "print("],
            mapping=(
                "Speedrun verification and fighting-game replays work on recorded inputs plus a deterministic "
                "engine; the same technique powers regression tests for physics."
            ),
        ),
        88: dict(
            topic="Playtesting a build",
            idea=(
                "A playtest is a measurement, not a demo. Before watching anyone play, decide what question the "
                "build answers: can a new player finish the first room, does the jump feel usable, is the third "
                "puzzle understandable without text. Then instrument the build so the session produces facts: "
                "attempts, time to completion, deaths by cause, where players stopped. In a small offline "
                "prototype the instrument is a log of structured events, not a video. Today's example runs a "
                "scripted playtest session through a tiny level using a fixed list of inputs, counts attempts, "
                "moves and deaths, and prints a summary. It is a stand-in for a human session, but the shape is "
                "real: the build emits events, and a report turns them into decisions. The discipline is to avoid "
                "asking whether it was fun as the only question, because the answer is neither actionable nor "
                "reproducible. Ask what players did and where the build failed them. Keep the instrumentation "
                "behind a flag so normal play is unaffected, and compare two builds using the same scripted "
                "inputs. That comparison is what turns an opinion into a change you can verify, and it is why "
                "playtest notes should point at recorded events rather than remembered impressions."
            ),
            code=(
                'def playtest(level, inputs):\n'
                '    player = level["start"]\n'
                '    moves = 0\n'
                '    deaths = 0\n'
                '    for step in inputs:\n'
                '        moves += 1\n'
                '        player = (player[0] + step[0], player[1] + step[1])\n'
                '        if player in level["hazards"]:\n'
                '            deaths += 1\n'
                '            player = level["start"]\n'
                '        if player == level["exit"]:\n'
                '            break\n'
                '    return {"moves": moves, "deaths": deaths, "finished": player == level["exit"]}\n'
                '\n'
                'level = {"start": (0, 0), "hazards": [(1, 0)], "exit": (2, 1)}\n'
                'script = [(1, 0), (0, 1), (1, 0), (1, 0)]\n'
                'result = playtest(level, script)\n'
                '\n'
                'print("moves", result["moves"], "deaths", result["deaths"])\n'
                'print("finished", result["finished"])\n'
                '\n'
                'assert result["deaths"] == 1 and result["finished"]\n'
                'print("an instrumented session produced facts, not opinions")'
            ),
            variant_b="make the first move safe and print a session with zero deaths",
            variant_c="count how many moves happened after the first death and explain why that matters",
            mistakes=[
                "Asking only whether the build was fun, which gives no actionable signal.",
                "Instrumenting only successes, so the places players fail stay invisible.",
                "Changing two things between builds and attributing the difference to one.",
            ],
            q1=(
                "Why should a playtest instrument events instead of relying on impressions?",
                "Events give reproducible facts about attempts, failures and progress, which can be compared across builds.",
            ),
            homework=(
                "Write `def session_report(level, inputs):` returning moves, deaths, finished and the move index "
                "of the first death. Run it on a failing script and a succeeding script, print both reports, and "
                "comment which metric points at the level's difficulty."
            ),
            patterns=["def session_report", "return", "print("],
            mapping=(
                "Studios instrument builds with telemetry events for deaths, retries and drop-off, then compare "
                "cohorts or builds; the questions are decided before the session starts."
            ),
        ),
        89: dict(
            topic="Review: state and loop checklist",
            idea=(
                "A review is a checklist applied to a real build, and today's checklist is the one this phase has "
                "been building toward. Does one container own the mutable world, and is it plain data? Is update "
                "separate from render, and can update run headless? Does input enter as a value at one boundary? "
                "Are events queued rather than called directly where fan-out exists? Are scene transitions "
                "requests processed between updates? Is the timestep fixed with a bounded catch-up? Is delta time "
                "confined to presentation? Do systems have a written order? Does a save round-trip reproduce the "
                "state, and is it versioned? Can a replay reproduce a run from its seed and inputs? Does a debug "
                "overlay expose the numbers you would otherwise print? Is a playtest instrumented with structured "
                "events? Today's example encodes a compact version of this checklist as functions that inspect a "
                "state dictionary and return a list of problems, then runs it against a healthy state and a "
                "deliberately broken one. The output is the review you would write for a teammate. The point is "
                "not to pass every box on a small prototype but to know which boxes you skipped and why, because "
                "an unexamined shortcut is the one that becomes permanent."
            ),
            code=(
                'def review(state):\n'
                '    issues = []\n'
                '    world = state.get("world")\n'
                '    if not isinstance(world, dict):\n'
                '        issues.append("no single world container")\n'
                '    elif "render" in world:\n'
                '        issues.append("render data stored in the world")\n'
                '    if state.get("timestep") != "fixed":\n'
                '        issues.append("timestep is not fixed")\n'
                '    if not state.get("record_inputs"):\n'
                '        issues.append("inputs are not recorded for replay")\n'
                '    if state.get("save_version", 0) < 1:\n'
                '        issues.append("save has no version")\n'
                '    return issues\n'
                '\n'
                'good = {"world": {"player": (1, 1)}, "timestep": "fixed",\n'
                '        "record_inputs": True, "save_version": 1}\n'
                'bad = {"world": {"player": (1, 1), "render": "cached"},\n'
                '       "timestep": "variable", "record_inputs": False, "save_version": 0}\n'
                '\n'
                'print("good build issues:", review(good))\n'
                'print("bad build issues:", review(bad))\n'
                '\n'
                'assert review(good) == [] and len(review(bad)) == 4\n'
                'print("review turns state into actionable checks")'
            ),
            variant_b="add a check for a bounded catch-up flag and rerun both builds",
            variant_c="return a list of (check, passed) pairs and print a pass count",
            mistakes=[
                "Treating the checklist as a score instead of a list of consciously accepted risks.",
                "Reviewing only the code and never inspecting the actual runtime state.",
                "Fixing symptoms in the renderer when the loop ordering is the real cause.",
            ],
            q1=(
                "What is the purpose of the state and loop checklist?",
                "To make each structural decision explicit, so skipped shortcuts are known and can be revisited rather than silently becoming permanent.",
            ),
            homework=(
                "Write `def audit(state):` that returns a list of failed check names for a world container, fixed "
                "timestep, recorded inputs and a versioned save. Run it on one healthy and one broken state, print "
                "both lists, and comment which check you would fix first and why."
            ),
            patterns=["def audit", "return", "print("],
            mapping=(
                "Engine teams ship review checklists for update order, save compatibility and replay determinism; "
                "the list exists so a rushed decision is at least a recorded one."
            ),
        ),
    },
)
