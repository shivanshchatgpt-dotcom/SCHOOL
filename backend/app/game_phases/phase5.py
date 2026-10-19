"""Player Experience and Polish, days 135-149.

A game that works is not yet a game that feels good. This phase treats the
player's experience as data — input maps, camera maths, HUD rectangles, tweens,
state machines, event buses — and computes measured values from plain dicts, so
every example stays stdlib-only, offline and deterministic. No audio device, no
window, no GPU: feedback, cues and layout are modelled as values and arithmetic.

Each day entry is ``(topic, idea, code, variants, mistakes, q1, homework,
patterns, mapping)`` and is consumed by ``apply_game_dev.build_day``.
"""

PHASE = (
    "Player Experience and Polish",
    "Turn a working game into one that feels responsive, readable and welcoming by measuring the player's experience and removing friction.",
    {
        135: dict(
            topic="Orientation: the player's experience",
            idea=(
                "The player's experience is the only output that actually reaches anyone, so it deserves the "
                "same measurement discipline as frame rate or memory. Before tweaking feel, record what players "
                "do: how long until the first meaningful input, how many times they die, how often they retry, "
                "where they stop. Those signals turn vague complaints into numbers you can move and then "
                "re-measure. Keep a session as plain data, a small dictionary of observations, and derive the "
                "interesting quantities with pure functions, so the same summary runs on a playtest log, a "
                "replay or a synthetic fixture. This is the habit the whole phase builds on: observe, quantify, "
                "change one thing, observe again. Crucially, never let one expert session hide three struggling "
                "beginners; report per session and aggregate only when you mean to. The metrics are not the "
                "goal, they are a compass: a high friction score tells you where to look, not what to change, "
                "because the change still comes from watching the player. Today you summarise two contrasting "
                "sessions and print a friction score for each, giving the rest of the phase a baseline to "
                "improve against. A shared definition of each metric keeps a team arguing about the game "
                "instead of about the numbers, and it makes week-to-week progress legible to everyone, not "
                "only to the person who happened to watch the session."
            ),
            code=(
                'def summarise(session):\n'
                '    first = session["time_to_first_input"]\n'
                '    deaths = session["deaths"]\n'
                '    retries = session["retries"]\n'
                '    return {\n'
                '        "friction": round(first + deaths * 2.0, 1),\n'
                '        "clean": deaths == 0 and retries <= 1,\n'
                '    }\n'
                '\n'
                'sessions = {\n'
                '    "new": {"time_to_first_input": 12.0, "deaths": 4, "retries": 3},\n'
                '    "veteran": {"time_to_first_input": 1.5, "deaths": 0, "retries": 0},\n'
                '}\n'
                'for name, session in sessions.items():\n'
                '    report = summarise(session)\n'
                '    print(name, "friction", report["friction"], "clean", report["clean"])\n'
                '\n'
                'assert summarise(sessions["veteran"])["clean"]\n'
                'print("experience is measured before it is polished")'
            ),
            variant_b='add a "false_starts" field and fold it into the friction score',
            variant_c='average friction across all sessions and print the worst offender by name',
            mistakes=[
                "Tweaking feel before recording what players actually do.",
                "Averaging every session so one expert hides three beginners' friction.",
                "Treating a single metric as if it were the whole experience.",
            ],
            q1=(
                "Why measure the player experience instead of relying on the designer's intuition?",
                "Measurements from real sessions expose friction the designer has stopped noticing, and they give a before and after number for every polish change.",
            ),
            homework=(
                "Write `friction_score(session)` that turns a session dict with first_input, deaths and retries "
                "into one number, weighting deaths highest, and returns it. Print the score for three different "
                "sessions and comment which weight dominates the result."
            ),
            patterns=["friction_score", "def ", "return"],
            mapping=(
                "Studios log time-to-first-input, death heatmaps and retry counts; those signals drive the "
                "polish backlog in exactly the way this summary does."
            ),
        ),
        136: dict(
            topic="Input mapping and rebinding",
            idea=(
                "Input should be indirected through an action map so gameplay never hard-codes a key. The map is "
                "small data: a dictionary from action name to the list of keys that trigger it, such as jump to "
                "space, left to a and the left arrow. Gameplay asks only whether an action is active, which "
                "means a controller, a keyboard or an accessibility preset all reach the same rule without a "
                "single edit. Rebinding is then just replacing an action's key list, and the interesting problem "
                "is conflict: if two actions share a key, pressing it fires both and the player is confused. "
                "Detecting that clash early, before it ships, is a small loop over the map. It is also useful to "
                "invert the map for a settings screen, turning action to keys into key to action for display. "
                "The discipline worth keeping is that the map is built and owned by the input layer, not rebuilt "
                "each frame and not consulted by gameplay. Today you look up the action for a pressed key, "
                "rebind jump, and print the conflict report for a deliberately clashing pair. Notice how much "
                "behaviour is changed by editing data rather than code. A controller button and a keyboard key "
                "then differ only in what the map says they mean, which is exactly the separation the whole "
                "input layer exists to provide."
            ),
            code=(
                'def action_for(bindings, key):\n'
                '    for action, keys in bindings.items():\n'
                '        if key in keys:\n'
                '            return action\n'
                '    return None\n'
                '\n'
                'def conflicts(bindings):\n'
                '    seen, clashes = {}, []\n'
                '    for action, keys in bindings.items():\n'
                '        for key in keys:\n'
                '            if key in seen:\n'
                '                clashes.append((seen[key], action, key))\n'
                '            seen[key] = action\n'
                '    return clashes\n'
                '\n'
                'bindings = {"jump": ["space"], "left": ["a", "left"], "right": ["d", "right"]}\n'
                'print("pressed d ->", action_for(bindings, "d"))\n'
                'print("pressed space ->", action_for(bindings, "space"))\n'
                '\n'
                'bindings["jump"] = ["w"]\n'
                'print("after rebind, w ->", action_for(bindings, "w"), "space ->", action_for(bindings, "space"))\n'
                'print("conflicts:", conflicts({"jump": ["w"], "up": ["w"]}))\n'
                '\n'
                'assert action_for(bindings, "space") is None\n'
                'print("gameplay asks for actions, never for keys")'
            ),
            variant_b='add a "dash" action on shift and print the full inverted key-to-action map',
            variant_c="detect a rebind that steals another action's only key and print the clash",
            mistakes=[
                "Reading raw keys in gameplay code so a rebind silently misses a path.",
                "Allowing two actions to share a key without warning the player.",
                "Rebuilding the binding map every frame instead of once at load.",
            ],
            q1=(
                "Why route input through an action map instead of checking keys directly?",
                "Gameplay depends on actions, so rebinding, gamepads and accessibility presets all work without touching a single rule.",
            ),
            homework=(
                "Write `rebind(bindings, action, key)` that returns a new map giving the action exactly this one "
                "key, leaving the original map untouched, and print the conflicts it creates. Test it on two "
                "actions and comment the line that detects the clash."
            ),
            patterns=["rebind", "def ", "return"],
            mapping=(
                "Unity's Input Actions, Godot's InputMap and Unreal's Enhanced Input all store this action-to-key "
                "table so controllers and accessibility rebinds share one code path."
            ),
        ),
        137: dict(
            topic="Camera and viewport maths",
            idea=(
                "A camera is a window onto a larger world: it defines which slice of the level fills the screen. "
                "The core transform is simple subtraction, screen equals world minus camera, and every sprite, "
                "HUD world marker and mouse pick uses it. The interesting part is placement. If the camera just "
                "centres on the player, the viewport slides past the edge of the level and shows empty space, so "
                "you clamp the offset to the range that keeps the window inside the level. Level smaller than "
                "the viewport is a real case and must clamp to zero rather than a negative range. A deadzone lets "
                "the camera stay still while the player moves a little, which reduces nausea and makes motion "
                "readable; smoothing then eases the camera toward its target instead of snapping. Keeping the "
                "transform in one function matters because a rounding difference between the camera and the "
                "sprites shows up as visible jitter. Today you compute a clamped camera offset, map a world point "
                "to screen space, and verify the camera stops at both edges. The lesson generalises to zoom and "
                "split screen by adding a scale factor before the subtraction. Doing the arithmetic in whole "
                "pixels keeps the camera and the sprites in agreement, so nothing shimmers or seams by a "
                "single pixel as the view slides."
            ),
            code=(
                'def clamp(value, lo, hi):\n'
                '    return max(lo, min(value, hi))\n'
                '\n'
                'def camera_offset(target, view, level):\n'
                '    vw, vh = view\n'
                '    lw, lh = level\n'
                '    x = clamp(target[0] - vw // 2, 0, max(0, lw - vw))\n'
                '    y = clamp(target[1] - vh // 2, 0, max(0, lh - vh))\n'
                '    return (x, y)\n'
                '\n'
                'def to_screen(cam, point):\n'
                '    return (point[0] - cam[0], point[1] - cam[1])\n'
                '\n'
                'level, view = (200, 120), (80, 60)\n'
                'cam = camera_offset((10, 50), view, level)\n'
                'print("camera clamped near left edge:", cam)\n'
                'print("hero on screen:", to_screen(cam, (10, 50)))\n'
                'cam2 = camera_offset((199, 119), view, level)\n'
                'print("camera at right edge:", cam2)\n'
                '\n'
                'assert cam == (0, 20) and cam2 == (120, 60)\n'
                'print("the camera stays inside the level")'
            ),
            variant_b='add a deadzone so the camera only moves once the target leaves a centre box',
            variant_c='support a zoom factor by dividing world coordinates before subtracting the camera',
            mistakes=[
                "Letting the camera show past the level edge and reveal the void.",
                "Applying the camera transform in world space so collision runs against screen pixels.",
                "Rounding the camera offset differently for the camera and the sprites, causing jitter.",
            ],
            q1=(
                "Why clamp the camera to the level bounds?",
                "Without clamping the viewport slides past the level and shows empty space, which breaks the illusion and exposes missing art.",
            ),
            homework=(
                "Write `camera_lerp(cam, target_cam, alpha)` that moves a camera position a fraction alpha "
                "toward the target and returns the new tuple, so the camera eases instead of snapping. Print a "
                "few steps and comment the line that smooths the motion."
            ),
            patterns=["camera_lerp", "def ", "return"],
            mapping=(
                "Every 2D engine has a camera with bounds and smoothing; this maths is what Unity's Cinemachine "
                "and Godot's Camera2D limit settings expose to the designer."
            ),
        ),
        138: dict(
            topic="HUD and UI layout",
            idea=(
                "The HUD is the layer the player reads without looking away, so its layout must survive every "
                "resolution. The robust approach is to place elements relative to the screen edges rather than "
                "at absolute pixels: health in the top left, a timer in the top right, a hotbar bottom centre. "
                "Each element becomes a rectangle of x, y, width and height, and placement is a function from an "
                "anchor, a size and a margin to a rectangle. Once everything is a rectangle, the same overlap "
                "test from collision tells you whether the timer is hidden behind the health bar. This matters "
                "because HUD overlap is invisible to the developer's monitor and obvious on a phone. Anchoring "
                "also gives you a UI scale for high-DPI screens: multiply sizes and margins before placing. The "
                "discipline is to never position HUD elements in world coordinates, where they would drift with "
                "the camera, and never to hard-code offsets for one resolution. Today you anchor three elements "
                "on a virtual screen and prove they do not collide. The same rectangle algebra underlies every "
                "retained-mode UI toolkit. Because every element is described the same way, a layout test can "
                "assert relationships between rectangles rather than a person squinting at a screenshot on one "
                "particular monitor."
            ),
            code=(
                'def place(anchor, size, margin, screen):\n'
                '    sw, sh = screen\n'
                '    w, h = size\n'
                '    spots = {\n'
                '        "top_left": (margin, margin),\n'
                '        "top_right": (sw - w - margin, margin),\n'
                '        "bottom_left": (margin, sh - h - margin),\n'
                '        "bottom_right": (sw - w - margin, sh - h - margin),\n'
                '    }\n'
                '    x, y = spots[anchor]\n'
                '    return {"x": x, "y": y, "w": w, "h": h}\n'
                '\n'
                'def overlaps(a, b):\n'
                '    return (a["x"] < b["x"] + b["w"] and b["x"] < a["x"] + a["w"]\n'
                '            and a["y"] < b["y"] + b["h"] and b["y"] < a["y"] + a["h"])\n'
                '\n'
                'screen = (320, 180)\n'
                'health = place("top_left", (60, 12), 6, screen)\n'
                'timer = place("top_right", (48, 12), 6, screen)\n'
                'print("health:", health)\n'
                'print("timer:", timer)\n'
                'print("overlap:", overlaps(health, timer))\n'
                '\n'
                'assert not overlaps(health, timer)\n'
                'print("HUD anchored to the screen, not to world pixels")'
            ),
            variant_b='add a bottom-centre hotbar and print its rect and whether it hits the timer',
            variant_c='scale every element by a ui_scale factor before placing, for high-DPI screens',
            mistakes=[
                "Positioning HUD elements in world coordinates so they drift with the camera.",
                "Hard-coding pixel offsets for one resolution instead of anchoring to edges.",
                "Letting two elements overlap so the timer hides behind the health bar.",
            ],
            q1=(
                "Why anchor HUD elements to screen edges rather than absolute pixels?",
                "Edge anchoring keeps the layout correct across resolutions and aspect ratios, where fixed pixels would drift off screen.",
            ),
            homework=(
                "Write `layout(screen, elements)` that takes a screen size and a list of (anchor, size) pairs "
                "and returns the list of rectangles, all inset by a margin. Print the rectangles for three "
                "elements and comment which line anchors them to the edge."
            ),
            patterns=["layout", "def ", "return"],
            mapping=(
                "Godot Control anchors, Unity RectTransform anchors and CSS flexbox are all edge-relative "
                "layout; the same corner arithmetic runs underneath."
            ),
        ),
        139: dict(
            topic="Feedback and game feel",
            idea=(
                "Game feel is mostly feedback: the world must visibly answer every input within a frame. The "
                "trick is that feel is not damage, it is presentation layered on top of the same numbers. Hit "
                "stop freezes the simulation for a few milliseconds so the eye registers the impact; knockback "
                "adds a shove; a flash and a scale pop sell the same event. Model each of these as timed "
                "parameters in a dictionary and compute the effect envelope rather than drawing it, because the "
                "timing is the design decision. The failure mode is overdoing it: stacking every effect on every "
                "hit turns the screen into noise, and giving a light tap the same feedback as a critical hit "
                "flattens the response. Good feel is contrast: a small hit whispers, a big hit shouts. Feedback "
                "also must be scaled by duration rather than a raw frame count, so it survives a different frame "
                "rate. Today you build two hit effects, one with a freeze and one without, and print their "
                "envelopes. The important habit is to make feedback data a function of the hit's strength, so "
                "tuning is editing values. Tuning then happens in one place, and a designer can feel the "
                "difference a parameter makes without waiting for a programmer to rebuild anything."
            ),
            code=(
                'def impact(base_speed, freeze_ms, knockback):\n'
                '    return {\n'
                '        "frozen": freeze_ms > 0,\n'
                '        "speed_after": round(base_speed * (0.3 if freeze_ms > 0 else 1.0), 1),\n'
                '        "knockback": knockback,\n'
                '    }\n'
                '\n'
                'effects = {\n'
                '    "sword": impact(10, 80, 3),\n'
                '    "spike": impact(10, 0, 0),\n'
                '}\n'
                'for name, effect in effects.items():\n'
                '    print(name, "frozen", effect["frozen"], "speed", effect["speed_after"],\n'
                '          "knockback", effect["knockback"])\n'
                '\n'
                'assert effects["sword"]["frozen"] and not effects["spike"]["frozen"]\n'
                'print("a hit reads as heavy only when feedback interrupts the world")'
            ),
            variant_b='add a flash duration to each effect dict and print the two side by side',
            variant_c='build a decay curve so knockback falls off over n frames and print each frame',
            mistakes=[
                "Piling on every effect at once so the screen becomes noise.",
                "Giving the same feedback to a light tap and a critical hit.",
                "Tying feedback timing to a raw frame count instead of a scaled duration.",
            ],
            q1=(
                "What is hit stop and why does it improve game feel?",
                "A brief pause on impact makes the collision register in the eye and adds a sense of weight without changing the actual damage.",
            ),
            homework=(
                "Write `feedback(hit)` that takes a hit dict with strength and returns freeze_ms, knockback and "
                "shake amplitude scaled by that strength, then print the feedback for a weak and a heavy hit and "
                "comment which scaling line matters most."
            ),
            patterns=["feedback", "def ", "return"],
            mapping=(
                "Fighting-game and action studios tune hit stop per frame; engines expose it as a brief global "
                "time-scale dip, which is exactly this freeze flag."
            ),
        ),
        140: dict(
            topic="Screenshake, tweens and easing",
            idea=(
                "Motion feels good when it accelerates and settles, which is why tweens and easing are the "
                "workhorses of polish. A tween interpolates a scalar from a start to an end over a normalised "
                "time t between zero and one, and an easing function reshapes that t so the value moves like a "
                "physical object: fast then slow for a settle, slow then fast for a shove. The same three-line "
                "pattern drives a menu fade, a door, a health bar and a camera. Screenshake is a different kind "
                "of motion: a short, decaying jitter, usually on the camera, that must not continue forever and "
                "must not use the global random generator, or two shakes will differ every frame and the effect "
                "becomes unreproducible. Seed a local generator with the shake's id and it is deterministic while "
                "still looking chaotic. Two details matter: clamp t so overshoot easing does not fly past the "
                "target, and decay amplitude over the shake's life so it stops cleanly. Today you tween a value "
                "with an ease-out curve and generate a short seeded shake, then assert both behave. Polish is "
                "these small curves applied consistently. Applied to fires, doors, UI and cameras alike, a "
                "handful of well-chosen curves is most of what players actually describe as juice."
            ),
            code=(
                'import random\n'
                '\n'
                'def ease_out_cubic(t):\n'
                '    return 1 - (1 - t) ** 3\n'
                '\n'
                'def tween(start, end, t, ease=ease_out_cubic):\n'
                '    t = max(0.0, min(1.0, t))\n'
                '    return start + (end - start) * ease(t)\n'
                '\n'
                'def shake(seed, samples, amplitude):\n'
                '    rng = random.Random(seed)\n'
                '    return [round(rng.uniform(-amplitude, amplitude), 2) for _ in range(samples)]\n'
                '\n'
                'print("tween at 0.0/0.5/1.0:", [round(tween(0, 100, t), 1) for t in (0.0, 0.5, 1.0)])\n'
                'offsets = shake(7, 5, 3.0)\n'
                'print("shake offsets:", offsets)\n'
                '\n'
                'assert tween(0, 100, 0.0) == 0 and tween(0, 100, 1.0) == 100\n'
                'assert all(-3.0 <= offset <= 3.0 for offset in offsets)\n'
                'print("easing shapes motion; a seeded shake is still deterministic")'
            ),
            variant_b='add ease_in_out_quad and print both curves at the same five sample points',
            variant_c='multiply shake amplitude by (1 - t) so the shake fades as the tween completes',
            mistakes=[
                "Using linear tweens everywhere, so motion looks mechanical.",
                "Letting the shake draw from the global RNG so it differs every frame.",
                "Forgetting to clamp t to 0..1 so overshoot easing flies past the target.",
            ],
            q1=(
                "Why do easing functions make motion feel better than linear interpolation?",
                "Real objects accelerate and settle, and easing shapes that acceleration so a door, a jump and a menu all move the way the player expects.",
            ),
            homework=(
                "Write `tween_steps(start, end, frames)` that returns a list of eased positions across a fixed "
                "number of frames, then print the first few and the last. Comment which line applies the easing "
                "and which line clamps the progress."
            ),
            patterns=["tween_steps", "def ", "return"],
            mapping=(
                "Tween libraries such as DOTween, Godot's Tween and Unity animator curves, plus Robert Penner's "
                "easing collection, are exactly this family of functions."
            ),
        ),
        141: dict(
            topic="Animation state machines",
            idea=(
                "An animation state machine is a small graph: states are clips, edges are the events that are "
                "allowed to leave one clip for another. Encoding it as data, a dictionary from state to the "
                "events it accepts and the state each event leads to, keeps the logic inspectable and testable. "
                "The machine's one job is to answer, given the current state and an event, what the state is "
                "next. Everything else, which sprite to draw and which frame to show, hangs off that answer. The "
                "value of the machine is that illegal transitions are impossible by construction: while jumping "
                "you simply have no edge for walk, so the request is ignored rather than interrupting the clip. "
                "A queue of clips, by contrast, lets any animation interrupt any other and the result looks like "
                "a glitch. When an unknown event arrives, the machine should keep the current state and, at most, "
                "log it, never crash and never corrupt the state. Today you walk a three-state machine through a "
                "sequence of events including a stopped one and print each transition. This pattern scales to "
                "characters, UI and even menu flow. It scales from one character to a whole cast, and the same "
                "graph can describe UI states, dialogue and menu flow without a new mechanism for each."
            ),
            code=(
                'MACHINE = {\n'
                '    "idle": {"walk": "walk", "jump": "jump"},\n'
                '    "walk": {"stop": "idle", "jump": "jump"},\n'
                '    "jump": {"land": "idle"},\n'
                '}\n'
                '\n'
                'def advance(state, event):\n'
                '    return MACHINE.get(state, {}).get(event, state)\n'
                '\n'
                'state = "idle"\n'
                'for event in ["walk", "jump", "land", "stop"]:\n'
                '    state = advance(state, event)\n'
                '    print("event", event, "->", state)\n'
                '\n'
                'assert advance("jump", "walk") == "jump"\n'
                'print("an unknown event leaves the state intact")'
            ),
            variant_b='add an attack state that returns to idle on finish and print the new transitions',
            variant_c='count how many events are spent in each state and print the totals',
            mistakes=[
                "Scattering animation flags across the entity so no single machine owns the state.",
                "Allowing every transition from every state so animations interrupt unpredictably.",
                "Letting an unknown event raise instead of being ignored or logged.",
            ],
            q1=(
                "Why model animation as a state machine instead of a queue of clips?",
                "A state machine names the legal transitions, so interrupting or repeating an animation becomes a deliberate decision rather than an accident.",
            ),
            homework=(
                "Write `run_machine(machine, start, events)` that walks a transitions dict through a list of "
                "events and returns the list of states visited. Feed it at least four events including one "
                "illegal one, print the states, and comment the fallback line."
            ),
            patterns=["run_machine", "def ", "return"],
            mapping=(
                "Unity's Animator, Godot's AnimationTree and Unreal's state machines all encode transitions as "
                "data in exactly this shape."
            ),
        ),
        142: dict(
            topic="Audio cues and event bus",
            idea=(
                "Audio should react to the game, not be called by it. The clean seam is an event bus: gameplay "
                "publishes named events with a small payload, and any number of handlers subscribe to react. A "
                "coin event can drive a sound effect, a score popup and a haptic pulse without the coin rule "
                "knowing that any of them exist. This decoupling is what makes muting, subtitles, volume mixing "
                "and automated tests possible: you detach the sound handler and the game still runs. The bus "
                "itself is tiny, a dictionary from event name to a list of handlers, with publish looping over "
                "the subscribers and collecting their results. Two rules keep it healthy. First, one handler "
                "raising an error must not abort the other subscribers, so a bad cue cannot silence the HUD. "
                "Second, one-shot events should be published once, not every frame, or the mixer is flooded. "
                "Today you build a bus, attach two handlers to a coin event, publish a couple of events and "
                "print the resulting cue list. Every real audio middleware is a richer version of this bus. "
                "Because the handlers are plain callables, a test can subscribe a recorder and assert the exact "
                "cue sequence without a sound device attached."
            ),
            code=(
                'def make_bus():\n'
                '    return {"subs": {}}\n'
                '\n'
                'def subscribe(bus, event, handler):\n'
                '    bus["subs"].setdefault(event, []).append(handler)\n'
                '\n'
                'def publish(bus, event, payload):\n'
                '    return [handler(payload) for handler in bus["subs"].get(event, [])]\n'
                '\n'
                'bus = make_bus()\n'
                'subscribe(bus, "coin", lambda amount: "sfx_coin_%d" % amount)\n'
                'subscribe(bus, "coin", lambda amount: "hud_score")\n'
                'subscribe(bus, "hurt", lambda damage: "sfx_hurt")\n'
                '\n'
                'cues = publish(bus, "coin", 1) + publish(bus, "hurt", 3)\n'
                'print("cues:", cues)\n'
                'print("unknown event ->", publish(bus, "land", None))\n'
                '\n'
                'assert cues == ["sfx_coin_1", "hud_score", "sfx_hurt"]\n'
                'print("events announce; the bus decides who listens")'
            ),
            variant_b='subscribe a debug logger to every event and print the order handlers fire',
            variant_c='add a mute flag that drops sound cues while keeping the HUD handlers attached',
            mistakes=[
                "Calling play_sound directly from gameplay so muting and subtitles are impossible.",
                "Letting one handler raise and abort the rest of the subscribers.",
                "Publishing a one-shot event every frame and flooding the mixer.",
            ],
            q1=(
                "Why publish events instead of calling sound functions directly?",
                "Gameplay stays unaware of audio, so muting, subtitles, haptics and tests can subscribe without touching a single rule.",
            ),
            homework=(
                "Write `wire_audio(bus)` that subscribes at least two handlers to a hit event and returns the "
                "bus, then publish a test hit and print the cues. Comment which line decouples gameplay from "
                "sound."
            ),
            patterns=["wire_audio", "def ", "return"],
            mapping=(
                "FMOD and Wwise integration, Godot signals and a global Unity event bus all exist so gameplay "
                "emits intent and the audio layer reacts on its own terms."
            ),
        ),
        143: dict(
            topic="Accessibility and remapping",
            idea=(
                "Accessibility is a shipping requirement, not a nice extra. Remapping is the clearest case: "
                "players with different hands, controllers or assistive switches need controls they can actually "
                "press, so a single fixed scheme excludes them. Model a preset as just another binding map, then "
                "check the property that matters: every required action is reachable in every preset. A second "
                "preset such as one-handed keeps the first key of each action, and switch access collapses each "
                "action to a single press, and the same reachability check validates it. Accessibility also "
                "reaches beyond input: text that scales, subtitles for audio cues, and never encoding state by "
                "colour alone, because colour-blind players will miss it. The reason to formalise it as data and "
                "checks is that accessibility features are the first to be cut under deadline pressure, so they "
                "need a test that fails loudly when broken. Today you build two presets and prove every action "
                "survives, printing any preset that fails. The same check runs in a build pipeline to stop a "
                "regression from shipping. Two more checks belong in the same place as data: a minimum text "
                "scale and a guarantee that every audio cue has a subtitle, both of which are easy to verify "
                "and easy to lose."
            ),
            code=(
                'DEFAULT = {"jump": ["space"], "left": ["a"], "right": ["d"], "pause": ["esc"]}\n'
                'LEFT_HANDED = {"jump": ["enter"], "left": ["j"], "right": ["l"], "pause": ["p"]}\n'
                '\n'
                'def reachable(bindings, actions):\n'
                '    return all(action in bindings and bindings[action] for action in actions)\n'
                '\n'
                'def one_handed(bindings):\n'
                '    return {action: keys[:1] for action, keys in bindings.items()}\n'
                '\n'
                'needed = ["jump", "left", "right", "pause"]\n'
                'presets = {"default": DEFAULT, "left_handed": LEFT_HANDED, "one_handed": one_handed(DEFAULT)}\n'
                'for name, bindings in presets.items():\n'
                '    print(name, "reachable:", reachable(bindings, needed))\n'
                '\n'
                'assert all(reachable(bindings, needed) for bindings in presets.values())\n'
                'print("every action survives every remap preset")'
            ),
            variant_b='add a switch-access preset where every action is reachable by one press',
            variant_c='check that no preset leaves an action unbound and print the offenders',
            mistakes=[
                "Shipping one fixed control scheme with no remap screen.",
                "Mapping a critical action only to a key some players cannot reach.",
                "Encoding state by colour alone with no shape or text backup.",
            ],
            q1=(
                "Why is remapping an accessibility feature and not just a preference?",
                "Players with different hands, controllers or assistive devices need controls they can press, and a fixed scheme excludes them entirely.",
            ),
            homework=(
                "Write `check_presets(presets, actions)` that returns the names of presets missing any required "
                "action, then print the failures. Comment which line defines what reachable means."
            ),
            patterns=["check_presets", "def ", "return"],
            mapping=(
                "The Xbox Accessibility Guidelines and the Game Accessibility Guidelines require remapping, "
                "scalable text and colour-independent cues as shippable features."
            ),
        ),
        144: dict(
            topic="Checkpoints and save UX",
            idea=(
                "A checkpoint exists so the player's time is not wasted, and a save is nothing more than "
                "serialised state. Once the game state is plain data, saving is encoding it to a string and "
                "loading is decoding it back, which is why the earlier discipline of keeping state as values "
                "pays off here. A good save system answers a few questions: when to autosave, which slots exist, "
                "and what to strip. Autosaving every frame thrashes the disk, so saves fire on milestones, a "
                "timer or an explicit checkpoint, and a frame counter modulo an interval is the standard test. "
                "Not everything belongs in a save: transient values such as velocity or an active tween should "
                "be reset on load, or the player resumes mid-air. Slots are a dictionary keyed by name, and "
                "overwriting an existing slot is a merge, not an append. The UX side is equally important: make "
                "the save visible, make loading predictable, and never lose a slot silently. Today you snapshot "
                "a state, restore it, and print which frames trigger an autosave. This is the same "
                "snapshot-and-restore pair a full save system builds on. Versioning the payload, so a field can "
                "be added later without breaking an old save, is the one upgrade almost every project ends up "
                "needing."
            ),
            code=(
                'import json\n'
                '\n'
                'def snapshot(state):\n'
                '    return json.dumps(state, sort_keys=True)\n'
                '\n'
                'def restore(blob):\n'
                '    return json.loads(blob)\n'
                '\n'
                'def should_autosave(frame, interval):\n'
                '    return frame > 0 and frame % interval == 0\n'
                '\n'
                'state = {"level": 3, "hp": 7, "checkpoint": "bridge"}\n'
                'blob = snapshot(state)\n'
                'print("saved:", blob)\n'
                'loaded = restore(blob)\n'
                'print("loaded hp:", loaded["hp"])\n'
                'for frame in range(1, 7):\n'
                '    if should_autosave(frame, 3):\n'
                '        print("autosave at frame", frame)\n'
                '\n'
                'assert loaded == state\n'
                'print("a save is serialised state, restored without surprises")'
            ),
            variant_b='store three save slots in a dict and print the newest slot by frame number',
            variant_c='strip volatile fields such as velocity before saving and print the cleaned state',
            mistakes=[
                "Serialising objects that cannot be reconstructed, so the save will not load.",
                "Saving every frame and thrashing the disk instead of on milestones.",
                "Loading a checkpoint without resetting volatile state, leaving stale velocity.",
            ],
            q1=(
                "Why should a checkpoint store state rather than replay every action?",
                "Storing the state is small and instant, while replaying actions is fragile if the rules changed between builds.",
            ),
            homework=(
                "Write `save_slot(slots, name, state)` that stores a serialised state under a slot name, "
                "overwriting an existing slot, and returns the slot count. Print the count after two saves and "
                "comment the line that performs the overwrite."
            ),
            patterns=["save_slot", "def ", "return"],
            mapping=(
                "Save systems in Souls-likes and roguelikes autosave at checkpoints; the payload is the same "
                "snapshot-and-restore pair, versioned so old saves still migrate."
            ),
        ),
        145: dict(
            topic="Tutorials and onboarding",
            idea=(
                "A tutorial works best when it teaches by doing and unlocks one thing at a time. Model it as a "
                "list of steps, each with an id and an optional prerequisite, and a function that returns the "
                "next teachable step given what the player has already done. A step is teachable when its "
                "prerequisite is complete, so move comes before jump which comes before attack, and the player "
                "is never asked to perform something they have not been shown. When no step is left, the "
                "tutorial is complete. This small gating rule replaces the wall of text that players skip, "
                "because each prompt appears exactly when the action is useful and nowhere else. Two design "
                "rules keep it humane: never hard-gate progress behind a step the player cannot perform, and "
                "always allow skipping, which simply marks the remaining steps done and unlocks their actions. "
                "Optional hints can sit in the same list flagged as never gating, so they teach without "
                "blocking. Today you step through a three-stage sequence and print each prompt until it "
                "completes. The same prerequisite logic drives quest chains and ability unlocks. Measuring "
                "where players quit a tutorial turns the sequence into something you can debug rather than "
                "guess about."
            ),
            code=(
                'STEPS = [\n'
                '    {"id": "move", "requires": None},\n'
                '    {"id": "jump", "requires": "move"},\n'
                '    {"id": "attack", "requires": "jump"},\n'
                ']\n'
                '\n'
                'def next_step(steps, done):\n'
                '    for step in steps:\n'
                '        if step["id"] not in done:\n'
                '            if step["requires"] is None or step["requires"] in done:\n'
                '                return step["id"]\n'
                '    return None\n'
                '\n'
                'done = set()\n'
                'for _ in range(4):\n'
                '    step = next_step(STEPS, done)\n'
                '    if step is None:\n'
                '        print("tutorial complete")\n'
                '        break\n'
                '    print("teach:", step)\n'
                '    done.add(step)\n'
                '\n'
                'assert next_step(STEPS, {"move", "jump", "attack"}) is None\n'
                'print("onboarding unlocks one action at a time")'
            ),
            variant_b='allow the player to skip the tutorial and print the gated actions it unlocks',
            variant_c='add an optional hint step that never gates progress and print whether it is required',
            mistakes=[
                "Teaching every mechanic up front instead of when it is first needed.",
                "Hard-gating the player behind a step they cannot perform.",
                "Showing a wall of text where a single prompted action would teach faster.",
            ],
            q1=(
                "Why unlock tutorial steps one at a time?",
                "Each step is taught at the moment it matters, so the player learns by doing instead of memorising a manual.",
            ),
            homework=(
                "Write `tutorial_progress(steps, done)` that returns the next teachable step id or None given a "
                "steps list and a set of completed ids. Print progress after each of three completions and "
                "comment the line that checks the gate."
            ),
            patterns=["tutorial_progress", "def ", "return"],
            mapping=(
                "Valve's in-game tutorials and Nintendo's opening levels teach through gated prompts; the same "
                "prerequisite check runs behind the scenes."
            ),
        ),
        146: dict(
            topic="Difficulty curves",
            idea=(
                "Difficulty is a curve, and a badly shaped one ruins an otherwise good game. The usual model is "
                "a value that grows with progression, often exponentially, then flattens near a ceiling. "
                "Exponential growth ramps quickly, which feels exciting early, but without a cap it eventually "
                "outpaces any player and the game becomes unwinnable, a cliff rather than a curve. The cap turns "
                "the ramp into a plateau where skilled play still matters but the numbers stop exploding. "
                "Difficulty should also breathe: alternating harder levels with a rest keeps tension from "
                "becoming fatigue, and scaling only enemy health while the player stays fixed makes fights "
                "merely longer rather than harder. Modelling the curve as a pure function of the level number "
                "lets you print it, compare shapes and see the cliff before a playtester does. Keep base, growth "
                "and cap as parameters so the whole curve is tuned by editing three values. Today you print the "
                "difficulty and enemy health for six levels and confirm the cap holds at the top. The same "
                "formula underlies XP and loot scaling. Printing the curve also reveals dead zones where several "
                "levels feel identical, which quietly wastes the middle of the game and the player's interest "
                "along with it."
            ),
            code=(
                'def difficulty(level, base=1.0, growth=1.25, cap=6.0):\n'
                '    value = base * (growth ** (level - 1))\n'
                '    return round(min(value, cap), 2)\n'
                '\n'
                'def health_for(level, base_hp=10):\n'
                '    return int(base_hp * difficulty(level))\n'
                '\n'
                'for level in range(1, 7):\n'
                '    print("level", level, "difficulty", difficulty(level), "enemy hp", health_for(level))\n'
                '\n'
                'assert difficulty(1) == 1.0 and difficulty(20) == 6.0\n'
                'print("a capped ramp climbs fast, then flattens to avoid a cliff")'
            ),
            variant_b='add a rest level after every third that resets difficulty to 1.0',
            variant_c='make difficulty step-based instead of exponential and compare the two curves',
            mistakes=[
                "Ramping difficulty exponentially with no cap, creating a wall.",
                "Making every level harder instead of alternating tension and rest.",
                "Scaling only enemy health without scaling the player, so fights drag.",
            ],
            q1=(
                "Why cap a difficulty curve instead of letting it grow forever?",
                "An uncapped curve eventually outpaces any player's skill and the game stops being winnable, so difficulty plateaus near a ceiling.",
            ),
            homework=(
                "Write `difficulty_for(level, base, growth, cap)` that returns a capped scalar, plus a helper "
                "named `curve` that prints each value across a range. Print levels 1 to 8 and comment the line "
                "that applies the cap."
            ),
            patterns=["difficulty_for", "def ", "return"],
            mapping=(
                "Designers sketch curves like this in spreadsheets; RPG and loot games scale stats with exactly "
                "a capped growth formula."
            ),
        ),
        147: dict(
            topic="Pause, menus and flow",
            idea=(
                "Menus are a stack, and treating them as one solves a whole class of flow bugs. Opening a screen "
                "pushes it; closing pops it; the visible screen is whatever is on top. A settings screen opened "
                "from pause, for example, sits above pause, so closing it returns to pause rather than dropping "
                "the player straight into the game. A single current-menu variable cannot express that path, "
                "which is why so many games resume unexpectedly after a settings round trip. The stack also "
                "gives you the right place to freeze the simulation: while the stack is deeper than gameplay, "
                "the world stops updating, so nothing moves behind a modal dialog. Commands become a tiny "
                "reducer, open pushes, close pops, quit clears, and the underflow case of popping an empty or "
                "last screen must be guarded rather than crashing. This is the same state-machine discipline as "
                "animation, applied to flow. Today you push pause, push settings, then pop twice and confirm you "
                "land back in gameplay. The reducer shape means the entire flow can be tested by feeding it "
                "commands. Because the reducer is pure, a test can replay a whole session of menu commands and "
                "assert the stack after each one, which catches the resume-into-the-wrong-screen bug that "
                "screenshots never show."
            ),
            code=(
                'def push(stack, state):\n'
                '    return stack + [state]\n'
                '\n'
                'def pop(stack):\n'
                '    return stack[:-1] if len(stack) > 1 else stack\n'
                '\n'
                'def top(stack):\n'
                '    return stack[-1] if stack else None\n'
                '\n'
                'stack = push(push([], "gameplay"), "pause")\n'
                'print("after pause:", top(stack), stack)\n'
                'stack = push(stack, "settings")\n'
                'print("in settings:", top(stack))\n'
                'stack = pop(stack)\n'
                'stack = pop(stack)\n'
                'print("resumed:", top(stack), stack)\n'
                '\n'
                'assert top(stack) == "gameplay" and len(stack) == 1\n'
                'print("menus are a stack: opening pushes, closing pops")'
            ),
            variant_b='push a confirm-quit dialog on top of pause and print the full stack order',
            variant_c='freeze the game while the stack is deeper than gameplay and print a paused flag',
            mistakes=[
                "Resuming from a menu without restoring the exact previous state.",
                "Clearing the whole stack on pause so a settings detour loses the pause screen.",
                "Updating gameplay underneath a modal menu so the world moves behind it.",
            ],
            q1=(
                "Why is a menu stack better than a single current-menu variable?",
                "A stack remembers the path back, so a settings screen opened from pause returns to pause rather than to the game.",
            ),
            homework=(
                "Write `flow(stack, command)` that handles open, close and quit commands against a menu stack "
                "and returns the new stack. Print the stack after each command and comment the guard that "
                "prevents popping the last screen."
            ),
            patterns=["flow", "def ", "return"],
            mapping=(
                "Godot's menu stack, Unity UI panels and every pause screen in a AAA title are a stack that "
                "preserves the caller."
            ),
        ),
        148: dict(
            topic="Playtest notes into fixes",
            idea=(
                "Playtest notes are raw material that must be triaged, not obeyed one by one. The first job is "
                "to tag each note with a short category such as camera, audio or ui, then count how often each "
                "category appears. Frequency is a cheap and surprisingly good proxy for how many players hit the "
                "same friction, so ranking categories by count gives an ordered fix list. The single loudest "
                "complaint is not necessarily the most important; one dramatic comment can hide a hundred quiet "
                "ones about the same problem. Tagging also separates symptoms from causes: several different "
                "camera notes may share one root, and grouping them reveals it. Severity can weight the ranking, "
                "so a rare crash outranks a common cosmetic nit, but the base sort stays frequency first. The "
                "output is a priority order, and each top item should be closed with the smallest change that "
                "removes the friction, then re-tested. Notes that cannot be reproduced should be recorded, not "
                "quietly dropped, because they often return. Today you tally tagged notes and print the ranked "
                "list. A bug tracker is this same triage at a larger scale. Keeping the raw notes beside the "
                "tally preserves the context a bare count throws away, which matters when a fix is reopened "
                "weeks later."
            ),
            code=(
                'def tally(notes):\n'
                '    counts = {}\n'
                '    for note in notes:\n'
                '        tag = note.split(":")[0].strip().lower()\n'
                '        counts[tag] = counts.get(tag, 0) + 1\n'
                '    return counts\n'
                '\n'
                'def ranked(counts):\n'
                '    return sorted(counts.items(), key=lambda item: (-item[1], item[0]))\n'
                '\n'
                'notes = [\n'
                '    "camera: too close",\n'
                '    "camera: jitters near walls",\n'
                '    "audio: footsteps too loud",\n'
                '    "camera: too close",\n'
                '    "ui: font too small",\n'
                ']\n'
                'counts = tally(notes)\n'
                'print("counts:", counts)\n'
                'print("ranked:", ranked(counts))\n'
                '\n'
                'assert ranked(counts)[0] == ("camera", 3)\n'
                'print("the most repeated note is the next fix")'
            ),
            variant_b='weight critical notes double before ranking and print the new priority order',
            variant_c='group notes by severity as well as tag and print a two-key ranking',
            mistakes=[
                "Fixing the loudest single complaint instead of the most repeated one.",
                "Ignoring notes that are hard to reproduce and hoping they vanish.",
                "Rewriting a whole feature instead of the smallest change that removes the friction.",
            ],
            q1=(
                "Why count repeated playtest notes instead of acting on the first one?",
                "Frequency is a cheap proxy for how many players hit the same friction, so it orders the fix list by shared pain.",
            ),
            homework=(
                "Write `triage(notes)` that returns a list of (tag, count) pairs sorted by count descending, "
                "then print the top three. Comment the line that orders the result and the line that builds the "
                "counts."
            ),
            patterns=["triage", "def ", "return"],
            mapping=(
                "Playtest tools and bug trackers sort by frequency and severity; a designer triages that list "
                "into the next sprint exactly like this."
            ),
        ),
        149: dict(
            topic="Review: polish checklist",
            idea=(
                "Polish is the set of things that must be true for the game to ship, which is why it belongs in "
                "an explicit checklist rather than a vague intention to make it feel good. The checklist covers "
                "input remap, pause and menus, save and load, subtitles, colour-blind safety and a stable frame "
                "rate, each a yes or no fact about the build. Turning polish into data means you can score it: "
                "count the completed items, list the unfinished ones as blockers, and argue about the list "
                "instead of about feelings. A percentage is useful, but the blockers matter more, because a "
                "single missing save system sinks a release regardless of how complete everything else is. "
                "Weighting items by player impact can sharpen the score, but it must never let accessibility "
                "items be diluted to zero, since they are requirements, not extras. The checklist also makes "
                "regressions visible: a feature that drops from done to not done is a blocker that reappears. "
                "Today you score a sample checklist and print its blockers, which is the phase's closing ritual. "
                "Every studio runs a ship-readiness list like this before a release candidate. Run it after "
                "every milestone, because polish regresses quietly and a checklist is often the only thing that "
                "notices it slipped."
            ),
            code=(
                'CHECKLIST = {\n'
                '    "input_remap": True,\n'
                '    "pause_menu": True,\n'
                '    "save_load": True,\n'
                '    "subtitles": False,\n'
                '    "colour_blind_safe": False,\n'
                '    "stable_framerate": True,\n'
                '}\n'
                '\n'
                'def score(checklist):\n'
                '    done = sum(1 for ok in checklist.values() if ok)\n'
                '    return done, len(checklist)\n'
                '\n'
                'def blockers(checklist):\n'
                '    return sorted(name for name, ok in checklist.items() if not ok)\n'
                '\n'
                'done, total = score(CHECKLIST)\n'
                'print("polish score: %d/%d" % (done, total))\n'
                'print("blockers:", blockers(CHECKLIST))\n'
                '\n'
                'assert done == 4 and blockers(CHECKLIST) == ["colour_blind_safe", "subtitles"]\n'
                'print("polish is a checklist you can argue against")'
            ),
            variant_b='mark every blocker fixed and print the new score and an empty blockers list',
            variant_c='weight each checklist item by player impact and print a weighted polish score',
            mistakes=[
                "Treating polish as decoration instead of a shippable checklist.",
                "Skipping accessibility items because they are not on the critical path.",
                "Calling a build done because it runs, not because the flow is complete.",
            ],
            q1=(
                "Why keep polish as an explicit checklist rather than a vague goal?",
                "A checklist turns feel-good into testable items, so progress is visible and nothing silently ships unfinished.",
            ),
            homework=(
                "Write `polish_score(checklist, weights)` that returns a weighted percentage of completed items "
                "plus a `blockers` list of unfinished names. Print the score and blockers for the sample and "
                "comment the line that computes the weighted total."
            ),
            patterns=["polish_score", "def ", "return"],
            mapping=(
                "Studios run ship-readiness checklists covering input, saves, accessibility, pacing and "
                "stability; the score gates the release candidate."
            ),
        ),
    },
)
