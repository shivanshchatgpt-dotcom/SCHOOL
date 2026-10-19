"""Game Development phase 2, days 90-104: movement, physics and collision.

Every example is stdlib-only, offline and deterministic (no clock, no I/O), so
the applier can execute it and get the same output on every run. One idea per
day, a runnable fixture, and a homework function the learner adapts.
"""

PHASE = ("Movement, Physics and Collision", "Build deterministic movement and collision code that stays stable across frame rates and object counts.", {
    90: dict(
        topic="Orientation: positions and frames",
        idea=(
            "Every position in a game is expressed relative to some frame of reference, and most movement bugs "
            "are really frame bugs. The screen has its own origin, the world may have another, and a sprite can "
            "have a local frame so that its parts move together. Converting between frames is usually addition "
            "or subtraction of an origin, sometimes a rotation or scale, but the important discipline is to "
            "label which frame a pair of numbers belongs to. Engines separate world space, where physics and "
            "collision happen, from view or screen space, where rendering happens, and they convert once at the "
            "boundary. If you mix them silently, a camera scroll looks like objects sliding, and a sprite offset "
            "looks like a collision failure. Today you take a local point, convert it into world coordinates by "
            "adding an origin, and convert it back, asserting that the round trip is exact. The arithmetic is "
            "trivial; the habit is what matters. Name the frame, convert deliberately, and keep collision in one "
            "space. When you later add a camera, a parent entity or a scrolling background, this vocabulary "
            "keeps every number where it belongs. A round trip is the smallest test that proves both directions agree, so write it before trusting any camera code."
        ),
        code="""ORIGIN = (10.0, 5.0)
local = (2.0, 3.0)

def to_world(point, origin):
    return (point[0] + origin[0], point[1] + origin[1])

def to_local(point, origin):
    return (point[0] - origin[0], point[1] - origin[1])

def fmt(point):
    return tuple(round(v, 2) for v in point)

world = to_world(local, ORIGIN)
back = to_local(world, ORIGIN)
print("local:", fmt(local))
print("world:", fmt(world))
print("round trip:", fmt(back))
assert world == (12.0, 8.0) and back == local
print("frames convert by adding or subtracting the origin")""",
        variant_b="use origin (-4.5, 2.0) and a local point of (0.5, -1.5), then print both directions",
        variant_c="add a camera offset of (3, 1) and convert the world point into screen space",
        mistakes=[
            "Mixing world and screen coordinates without naming which one a pair uses.",
            "Forgetting the origin when converting a local sprite offset.",
            "Assuming y grows upward when the chosen screen convention has y growing down.",
        ],
        q1=(
            "Why keep collision and physics in world space rather than screen space?",
            "World space is stable when the camera moves; screen space shifts with the view, so the same overlap would change for no physical reason.",
        ),
        homework=(
            "Write `convert(point, origin, direction)` that converts a point between local and world frames "
            "using direction 1 or -1. Call it in both directions on two origins, print each result, and comment "
            "which line makes the round trip exact."
        ),
        patterns=["def ", "return", "print("],
        mapping=(
            "Godot's Node2D transforms and Unity's Transform.TransformPoint both do this conversion; the engine "
            "keeps a separate world position so physics never sees local offsets."
        ),
    ),
    91: dict(
        topic="Vector maths with tuples",
        idea=(
            "A vector is a direction and a length, and a tuple is enough to represent one in two dimensions. "
            "Addition combines displacements, subtraction gives the vector from one point to another, and "
            "scaling changes length without changing direction. The length comes from Pythagoras, and the "
            "distance between two points is the length of their difference. Two operations repay their cost "
            "immediately: normalising a vector to length one, so speed can be applied separately, and comparing "
            "squared lengths, so you avoid a square root in hot collision code. Today you write small functions "
            "for add, subtract, scale, length and distance, then use them on a position and a velocity. Notice "
            "that none of the functions mutate their arguments; they return new tuples, which keeps movement "
            "predictable and easy to test. Floating point means exact equality is fragile, so compare rounded "
            "values or a tolerance. Also decide the zero-vector case: normalising a zero vector is undefined, so "
            "return zero or raise rather than dividing by zero. These few helpers are the vocabulary for every "
            "later lesson, from gravity to collision normals. Write them once and reuse them. Keep the helpers tiny and side-effect free, and every later system inherits the same predictable arithmetic."
        ),
        code="""import math

def add(a, b):
    return (a[0] + b[0], a[1] + b[1])

def sub(a, b):
    return (a[0] - b[0], a[1] - b[1])

def scale(v, k):
    return (v[0] * k, v[1] * k)

def length(v):
    return math.hypot(v[0], v[1])

def distance(a, b):
    return length(sub(b, a))

pos = (1.0, 2.0)
vel = (3.0, 4.0)
print("length:", round(length(vel), 2))
print("moved:", add(pos, vel))
print("distance to origin:", round(distance((0.0, 0.0), vel), 2))
print("half speed:", scale(vel, 0.5))
assert round(length((3.0, 4.0)), 2) == 5.0
print("vectors are plain immutable tuples")""",
        variant_b="compute the unit vector of (6, 8) and print it to two decimals",
        variant_c="distance from (1, 1) to (4, 5) and print both the vector and its length",
        mistakes=[
            "Normalising a zero vector and dividing by zero.",
            "Mutating a shared tuple-like position instead of returning a new vector.",
            "Using == on computed floats instead of a tolerance or rounded values.",
        ],
        q1=(
            "Why is it useful to normalise a direction vector before applying speed?",
            "A unit vector separates direction from magnitude, so speed and facing can change independently without accidental scaling.",
        ),
        homework=(
            "Write `unit(v)` returning a zero vector for zero input and a length-one tuple otherwise. Test it on "
            "(3, 4), (-3, 0) and (0, 0), print each result and its length, and comment which line handles the "
            "zero case."
        ),
        patterns=["def ", "math.hypot", "return"],
        mapping=(
            "Every engine has a vector type with the same operations; writing them once by hand makes the "
            "engine API feel obvious instead of magical."
        ),
    ),
    92: dict(
        topic="Integrating position over time",
        idea=(
            "Motion is position changing over time, and the simplest integration is position plus velocity times "
            "the timestep. Doing that once per fixed tick gives a straight line; doing it repeatedly traces a "
            "trajectory. The order of operations matters: reading the old position, computing the new one, then "
            "storing it, is explicit Euler. Updating velocity first and then using the new velocity for the "
            "position step is semi-implicit Euler, which behaves better with forces and is what most game "
            "physics uses. Today you integrate a two-dimensional position over a few fixed steps and print each "
            "position, then assert the endpoint. The fixed timestep is essential for determinism: if the same "
            "input produces a different result on a faster machine, the simulation is not reproducible. A common "
            "mistake is applying the timestep twice, once when scaling velocity and again when adding it, which "
            "silently doubles speed. Another is accumulating floating point error by using wildly different "
            "timesteps for different entities. Keep one dt for the whole world. When you later add acceleration, "
            "the integration loop stays the same and only the velocity update grows. That is the value of "
            "separating velocity from position. Keep the integration loop visible, because hidden integration is where frame-rate bugs hide."
        ),
        code="""def integrate(pos, vel, dt, steps):
    x, y = pos
    vx, vy = vel
    history = []
    for _ in range(steps):
        x += vx * dt
        y += vy * dt
        history.append((x, y))
    return history

history = integrate((0.0, 0.0), (2.0, -1.0), 0.5, 4)
for i, point in enumerate(history, start=1):
    print("step", i, "->", tuple(round(v, 2) for v in point))
end = history[-1]
assert end == (4.0, -2.0)
print("position integrated over a fixed timestep")""",
        variant_b="start at (5, 5) with velocity (-1, 0.5) and six steps of dt 0.25",
        variant_c="use dt 0.1 for ten steps and print the total distance travelled",
        mistakes=[
            "Applying dt twice, once when scaling velocity and again when adding it.",
            "Using a different timestep per entity, so shared collision results drift.",
            "Updating position before velocity when the force should affect the current step.",
        ],
        q1=(
            "Why does a fixed timestep make a movement simulation reproducible?",
            "Each tick advances exactly the same amount of simulated time, so identical inputs follow an identical trajectory on any machine.",
        ),
        homework=(
            "Write `trace(start, velocity, dt, steps)` that returns every intermediate position as a list. Run "
            "it with two different step counts, print both lists, and comment which line advances the position "
            "by velocity times dt."
        ),
        patterns=["def ", "for _ in range", "return"],
        mapping=(
            "Physics engines integrate at a fixed rate and interpolate for rendering; the accumulator pattern "
            "exists so gameplay stays stable while frame rate varies."
        ),
    ),
    93: dict(
        topic="Velocity, acceleration and drag",
        idea=(
            "Velocity is how fast position changes; acceleration is how fast velocity changes. Keeping the two "
            "separate lets one force act on any object without special cases: gravity adds to velocity, a "
            "thruster adds in its facing direction, and drag removes a fraction of velocity every second. The "
            "update order is velocity first, then position, because a force applied this tick should influence "
            "this tick's movement. Drag is commonly modelled as a multiplicative decay, velocity times one minus "
            "the drag coefficient times dt, which is stable for small timesteps. A large drag value with a large "
            "dt can overshoot and reverse the motion, so clamp or choose values carefully. Today you apply a "
            "constant acceleration and a drag coefficient for a handful of steps, printing the velocity each "
            "time. You should see velocity approach a steady state rather than growing without bound. That "
            "steady state is terminal velocity, which the next lessons make explicit. Notice that the code has "
            "no knowledge of what caused the acceleration: it could be gravity, wind or a rocket. This is the "
            "separation that makes a small physics model reusable across many entity types. Printing the sequence makes the approach to steady state visible instead of assumed, and that is the check you will reuse for gravity and jump tuning."
        ),
        code="""def step(vel, accel, dt, drag):
    vx = vel[0] + (accel[0] - drag * vel[0]) * dt
    vy = vel[1] + (accel[1] - drag * vel[1]) * dt
    return (vx, vy)

vel = (0.0, 0.0)
accel = (4.0, 0.0)
for i in range(12):
    vel = step(vel, accel, 0.5, 0.5)
    print("t", round((i + 1) * 0.5, 2), "vel", (round(vel[0], 2), round(vel[1], 2)))

steady = 4.0 / 0.5
print("expected terminal x velocity:", round(steady, 2))
assert abs(vel[0] - steady) < 0.5
print("drag pulls velocity toward its terminal value")""",
        variant_b="apply upward acceleration (0, -3) with drag 0.4 and print twelve velocity steps",
        variant_c="double the drag to 1.0 and compare how quickly the terminal value is approached",
        mistakes=[
            "Updating position before velocity, so forces act one tick late.",
            "Using a drag factor above one, which reverses the velocity direction.",
            "Forgetting that drag scales with dt, making behaviour frame-rate dependent.",
        ],
        q1=(
            "Why is drag applied as a multiplier rather than an unconditional subtraction?",
            "A multiplier removes a fraction of the current speed, so it can never reverse the direction, while a subtraction can overshoot through zero.",
        ),
        homework=(
            "Write `accelerate(vel, accel, dt, drag)` returning the new velocity, and loop it for eight steps. "
            "Print every velocity, then print the theoretical terminal velocity, and comment which line applies "
            "the drag decay."
        ),
        patterns=["def ", "return", "round("],
        mapping=(
            "Rigid-body engines accumulate forces into acceleration, integrate velocity, then integrate position; "
            "drag is usually a damping term applied during the same pass."
        ),
    ),
    94: dict(
        topic="Gravity and jumping curves",
        idea=(
            "A jump is a short story told by gravity: give the character an upward velocity, let gravity reduce "
            "it to zero at the apex, then let it pull the character back down. The shape of the curve is a "
            "parabola, and the peak height depends on the square of the jump speed divided by twice gravity. "
            "That relationship is a design tool: doubling jump speed roughly quadruples height, while doubling "
            "gravity halves it. Simulating the jump in fixed steps teaches the difference between the physics "
            "and the feel. A high gravity and high jump velocity gives a snappy arc; a low gravity gives a floaty "
            "one, even though both can reach the same height. Today you simulate a jump from ground level, track "
            "the apex and the time in the air, and assert the numerical peak against the formula. Notice that the "
            "character is a point here; collision with a floor comes later, so landing is detected by the "
            "position crossing zero. Also notice the fixed timestep: changing dt changes how accurately the apex "
            "is sampled, though not the underlying curve. Your game should not depend on frame rate for jump "
            "height, which is another argument for a fixed physics step. Tuning is then a matter of choosing the arc, not patching the landing."
        ),
        code="""def jump(v0, gravity, dt):
    y = 0.0
    vy = v0
    t = 0.0
    apex = 0.0
    while True:
        vy -= gravity * dt
        y += vy * dt
        t += dt
        apex = max(apex, y)
        if y <= 0.0 and vy < 0.0:
            break
    return apex, t

apex, airtime = jump(8.0, 20.0, 0.05)
theory = (8.0 * 8.0) / (2.0 * 20.0)
print("apex:", round(apex, 2), "expected:", round(theory, 2))
print("air time:", round(airtime, 2))
assert abs(apex - theory) < 0.2
print("a jump is a parabola sampled by a fixed step")""",
        variant_b="try jump speed 6 with gravity 30 and report apex and air time",
        variant_c="halve gravity to 10 and explain what happens to both apex and air time",
        mistakes=[
            "Adding gravity without a timestep, making the arc depend on frame count.",
            "Treating the apex as a magic number instead of deriving it from speed and gravity.",
            "Stopping the loop at the first downward step before checking the ground crossing.",
        ],
        q1=(
            "Why does doubling jump speed roughly quadruple jump height?",
            "Height is proportional to speed squared divided by twice gravity, so doubling speed multiplies height by four.",
        ),
        homework=(
            "Write `jump_profile(speed, gravity, dt)` that simulates a jump and returns the apex, air time and "
            "landing speed. Run it for two speed values, print all results, and comment which line detects the "
            "landing crossing."
        ),
        patterns=["def ", "while True", "gravity"],
        mapping=(
            "Platformer tuning tools plot the exact parabola so designers can feel a jump before committing; "
            "the engine still integrates it with the fixed physics step."
        ),
    ),
    95: dict(
        topic="Friction and terminal velocity",
        idea=(
            "Friction and drag are both forces that oppose motion, but they act differently. Friction usually "
            "applies at a contact surface and is proportional to the normal force, while drag grows with speed "
            "through the surrounding medium. For a small game, a practical model is enough: friction reduces "
            "horizontal speed by a fixed amount per second until it reaches zero, and drag removes a fraction of "
            "velocity so that acceleration and drag eventually balance at terminal velocity. Terminal velocity "
            "is not a constant you type in; it is the speed where the accelerating force equals the retarding "
            "force. If acceleration is a and drag is k times velocity, the balance is a equals k times v, so v "
            "equals a over k. Today you simulate both: a crate sliding to a halt under friction, and a falling "
            "body approaching terminal velocity under linear drag. Clamp friction at zero so it cannot push an "
            "object backwards, and compare the simulated terminal speed with the formula. These small details "
            "prevent jitter that players notice immediately. Deterministic fixed steps make the comparison "
            "meaningful, and the same code works for any entity with a velocity. Two forces, two tests, and the difference between stopping and settling becomes concrete."
        ),
        code="""def slide(speed, friction, dt, steps):
    x = 0.0
    for _ in range(steps):
        speed = max(0.0, speed - friction * dt)
        x += speed * dt
    return x, speed

def fall(v, accel, drag, dt, steps):
    for _ in range(steps):
        v += (accel - drag * v) * dt
    return v

x, rest = slide(10.0, 4.0, 0.5, 10)
v = fall(0.0, 9.0, 1.5, 0.1, 100)
print("slide distance:", round(x, 2), "final speed:", round(rest, 2))
print("terminal speed:", round(v, 2), "expected:", round(9.0 / 1.5, 2))
assert rest == 0.0
assert abs(v - 6.0) < 0.05
print("friction stops motion and drag sets a terminal speed")""",
        variant_b="start the slide at 20 with friction 2.5 and count the step where it stops",
        variant_c="raise drag to 3.0 and compare the new terminal speed with 9 divided by 3",
        mistakes=[
            "Letting friction take speed below zero, so the object slides backwards.",
            "Typing a terminal velocity constant instead of deriving it from acceleration and drag.",
            "Using a drag term that does not scale with dt, so the result depends on frame rate.",
        ],
        q1=(
            "How do you derive terminal velocity from acceleration and linear drag?",
            "Set acceleration equal to drag times velocity and solve: terminal velocity is acceleration divided by the drag coefficient.",
        ),
        homework=(
            "Write `settle(accel, drag, dt, steps)` that returns the final velocity after repeated linear-drag "
            "steps. Call it with two drag values, print both results and the matching a-over-k values, and "
            "comment which line applies the drag force."
        ),
        patterns=["def ", "max(0.0", "return"],
        mapping=(
            "Physics engines expose friction and damping coefficients per material or body; the solver applies "
            "them alongside gravity so a crate and a character feel different on the same floor."
        ),
    ),
    96: dict(
        topic="AABB collision detection",
        idea=(
            "An axis-aligned bounding box is the workhorse of 2D collision: a rectangle that does not rotate, "
            "stored as x, y, width and height. Two boxes overlap unless one is entirely to the left, right, "
            "above or below the other, which makes the test four comparisons and no square roots. The "
            "convention matters more than the formula. Decide whether the edge counts as a collision, whether y "
            "grows up or down, and whether x and y mean the corner or the centre, then use that convention "
            "everywhere. Today you write the overlap test and run it against an overlapping box, a separate box, "
            "a touching edge and a contained box. The touching case is the classic off-by-one, so change the "
            "strict inequalities to non-strict ones deliberately and observe the difference. Keep detection "
            "separate from resolution: this function answers a yes or no question and changes nothing, which "
            "makes it trivial to test and safe to call from broad-phase code. When there are many objects, this "
            "is the narrow test inside a grid or quadtree; the same four comparisons remain the final word on "
            "whether two shapes truly touch. Write the convention in a comment next to the function, because every later system will copy it."
        ),
        code="""def boxes_overlap(a, b):
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    return ax < bx + bw and bx < ax + aw and ay < by + bh and by < ay + ah

player = (0.0, 0.0, 10.0, 10.0)
cases = {
    "overlap": (5.0, 5.0, 10.0, 10.0),
    "apart": (20.0, 20.0, 4.0, 4.0),
    "touching edge": (10.0, 0.0, 5.0, 5.0),
    "contained": (2.0, 2.0, 3.0, 3.0),
}
for label, box in cases.items():
    print(label, "->", boxes_overlap(player, box))

assert boxes_overlap(player, (5.0, 5.0, 10.0, 10.0))
assert not boxes_overlap(player, (10.0, 0.0, 5.0, 5.0))
assert boxes_overlap(player, (2.0, 2.0, 3.0, 3.0))
print("AABB overlap checked on overlap, separation, edges and containment")""",
        variant_b="write `boxes_touch` using <= so edge contact counts, and rerun the touching case",
        variant_c="store boxes as centre plus half-size and convert before testing",
        mistakes=[
            "Mixing corner-based and centre-based boxes in the same comparison.",
            "Resolving overlaps inside the detection function, so query order changes the world.",
            "Using <= without deciding that touching edges should count as collisions.",
        ],
        q1=(
            "Why is the AABB test written as four comparisons instead of checking every point?",
            "A rectangle is separable: if its x interval and y interval both overlap, the boxes overlap, so two interval tests are sufficient.",
        ),
        homework=(
            "Write `overlapping_indices(box, boxes)` that returns the indices of all boxes overlapping the "
            "first. Test a list with an overlap, a touching edge and a clear box, print the indices, and comment "
            "which comparison excludes the edge case."
        ),
        patterns=["def ", "and", "return"],
        mapping=(
            "Broad-phase systems such as Box2D's AABB tree and Unity's Physics2D use exactly this test before "
            "running a more expensive narrow-phase check."
        ),
    ),
    97: dict(
        topic="Resolving overlaps",
        idea=(
            "Detection says the boxes overlap; resolution decides how to move them so they do not. The standard "
            "tool is the minimum translation vector: the smallest displacement along x or y that separates the "
            "two boxes. Compute the overlap on each axis, pick the smaller one, and push along that axis in the "
            "direction that moves the moving box away from the other. This is why AABB resolution is cheap and "
            "predictable. The same logic applies to a character against a wall: if a horizontal step causes a "
            "vertical overlap, push back horizontally. Order matters when several walls touch at once, because "
            "resolving against one can create a new overlap with another. A simple fix is to resolve one axis at "
            "a time, x then y, and repeat if needed. Today you overlap a player with a wall, compute the "
            "penetration on both axes, push along the smaller one, and assert that the boxes no longer overlap. "
            "Keep the resolution function separate from the detection function and from input. That separation "
            "makes it possible to test a push without simulating a frame, and it keeps the physics honest when "
            "you later add multiple solids or moving platforms. A resolver that runs twice must leave the world unchanged the second time."
        ),
        code="""def overlap_axis(a_start, a_size, b_start, b_size):
    return min(a_start + a_size, b_start + b_size) - max(a_start, b_start)

def resolve(player, wall):
    px, py, pw, ph = player
    wx, wy, ww, wh = wall
    ox = overlap_axis(px, pw, wx, ww)
    oy = overlap_axis(py, ph, wy, wh)
    if ox <= 0 or oy <= 0:
        return player
    if ox < oy:
        px += -ox if px < wx else ox
    else:
        py += -oy if py < wy else oy
    return (px, py, pw, ph)

player = (0.0, 0.0, 10.0, 10.0)
wall = (8.0, 0.0, 10.0, 10.0)
fixed = resolve(player, wall)
print("penetration x:", round(overlap_axis(player[0], player[2], wall[0], wall[2]), 2))
print("player:", fixed)
assert overlap_axis(fixed[0], fixed[2], wall[0], wall[2]) <= 0
print("overlap removed along the smaller axis")""",
        variant_b="move the wall to (5, 7) so the y overlap is smaller, and print the pushed position",
        variant_c="put the player to the right of the wall and check that the push direction flips",
        mistakes=[
            "Pushing in a fixed direction instead of away from the other box.",
            "Resolving along the larger penetration, which teleports the player noticeably.",
            "Forgetting that the overlap can be zero on one axis, meaning there is no collision.",
        ],
        q1=(
            "Why push along the axis with the smaller penetration?",
            "The smaller penetration is the shortest displacement that separates the boxes, so it looks like a natural slide instead of a jump.",
        ),
        homework=(
            "Write `push_out(moving, solid)` that returns a separated rectangle using the minimum translation "
            "vector. Test it on two wall positions, print the results, and comment which line chooses the "
            "resolution axis."
        ),
        patterns=["def ", "min(", "return"],
        mapping=(
            "Platformer controllers commonly resolve x and y separately to get clean wall sliding; full physics "
            "solvers instead compute contact normals and impulses."
        ),
    ),
    98: dict(
        topic="Swept collision and tunnelling",
        idea=(
            "Discrete collision only checks where objects are at the end of a step. A fast bullet can start on "
            "one side of a thin wall and end on the other without ever overlapping at a sampled moment, which is "
            "tunnelling. The fix is to sweep the motion: treat the path as a segment or a moving box and ask "
            "whether it crosses the obstacle anywhere along the way. For axis-aligned motion, the swept test "
            "expands the obstacle by the mover's size and checks whether the movement interval crosses it. For "
            "general directions, conservative advancement or a ray cast against expanded boxes does the job. "
            "Today you move a bullet in large steps, show that the discrete check misses the wall, then run a "
            "swept check that catches it and reports the impact time. The lesson generalises: collision queries "
            "should consider the whole path whenever speed times dt can exceed an object's thickness. Sub-"
            "stepping is the blunt alternative, but sweeping is cheaper and exact for simple shapes. Always keep "
            "the discrete test for resting contact, and use the sweep as an additional guard for fast bodies. The same reasoning applies to any fast body, not just bullets: dashing players, elevators and projectiles all need speed times dt measured against thickness."
        ),
        code="""def discrete_hit(x, width, wall_x, wall_w):
    return x < wall_x + wall_w and wall_x < x + width

def swept_hit(x, width, vx, wall_x, wall_w):
    if vx == 0:
        return None
    end = x + vx
    lo, hi = min(x, end), max(x, end)
    if lo < wall_x + wall_w and wall_x < hi + width:
        if vx > 0:
            return (wall_x - width - x) / vx
        return (wall_x + wall_w - x) / vx
    return None

x, width, vx = 0.0, 2.0, 60.0
wall_x, wall_w = 50.0, 10.0
print("discrete at start:", discrete_hit(x, width, wall_x, wall_w))
print("discrete after step:", discrete_hit(x + vx, width, wall_x, wall_w))
hit_t = swept_hit(x, width, vx, wall_x, wall_w)
print("swept impact time:", round(hit_t, 2))
assert hit_t is not None and abs(hit_t - 0.8) < 0.01
print("sweep catches motion that discrete sampling tunnels through")""",
        variant_b="set vx to 30 and recompute the impact time and impact x position",
        variant_c="move the bullet right to left from x 80 with vx -40 and check the mirrored impact time",
        mistakes=[
            "Sampling only the end position for fast movers, allowing tunnelling.",
            "Forgetting to expand the wall by the mover width when sweeping a box.",
            "Using the sweep result as a resting-contact test instead of keeping the discrete check.",
        ],
        q1=(
            "When does discrete collision sampling fail for a fast object?",
            "When the object moves further than the obstacle's thickness in one step, so it is on both sides at sampled times but never overlaps.",
        ),
        homework=(
            "Write `first_impact(x, width, vx, wall_x, wall_w)` that returns the impact time or None using a "
            "swept interval. Test it with two speeds, print each time, and comment which line expands the wall "
            "by the mover width."
        ),
        patterns=["def ", "return", "if vx"],
        mapping=(
            "Bullet physics uses continuous collision detection (CCD) sweeps for fast bodies; ray casts against "
            "expanded shapes are the same idea in a different costume."
        ),
    ),
    99: dict(
        topic="Grid and tile movement",
        idea=(
            "Tile games trade continuous motion for discrete cells, and that trade makes movement easy to reason "
            "about. A position is a pair of integer coordinates, a blocked cell is a lookup in a set, and a move "
            "is accepted only if the destination is walkable. Because every state is a cell, saves, replays and "
            "pathfinding all share one representation. The usual pitfalls are boundaries, diagonal moves and "
            "order. Check bounds before indexing, decide whether diagonals may cut corners, and process a "
            "command one step at a time so an interrupted move never leaves the player between cells. Today you "
            "move a player through a small grid with walls, applying a list of directions and stopping when a "
            "move is blocked. Print the trail of accepted positions and the final cell. Notice that the movement "
            "function returns a new position instead of mutating the player, so a failed move is simply the old "
            "position. That makes the rule easy to test and safe to call from an AI planner. The same grid "
            "underlies the BFS and line-of-sight lessons later in this phase, which is why getting the "
            "conventions clean now saves time. A failed move is a no-op, which is the cheapest possible collision response."
        ),
        code="""BLOCKED = {(1, 1), (1, 2), (2, 2), (3, 0)}
DIRS = {"up": (0, -1), "down": (0, 1), "left": (-1, 0), "right": (1, 0)}

def in_bounds(pos, width, height):
    return 0 <= pos[0] < width and 0 <= pos[1] < height

def move(pos, direction, width, height):
    dx, dy = DIRS[direction]
    target = (pos[0] + dx, pos[1] + dy)
    if in_bounds(target, width, height) and target not in BLOCKED:
        return target
    return pos

pos = (0, 0)
trail = [pos]
for cmd in ["right", "right", "down", "down", "left", "up"]:
    pos = move(pos, cmd, 4, 4)
    trail.append(pos)
print("trail:", trail)
print("final:", pos)
assert pos == (2, 0)
print("grid moves are accepted only into walkable cells")""",
        variant_b="add a diagonal move (1, 1) and decide whether it may pass a blocked corner",
        variant_c="start at (3, 3) and run the commands in reverse, printing every blocked attempt",
        mistakes=[
            "Indexing the grid before checking the destination is in bounds.",
            "Allowing diagonal moves through the corner between two blocked cells.",
            "Mutating the player position even when the move is rejected.",
        ],
        q1=(
            "Why does grid movement make replays and pathfinding easier?",
            "Every position is a small integer cell, so equality, saving and neighbour lookup are exact and cheap, with no floating-point drift.",
        ),
        homework=(
            "Write `walk(start, commands, blocked, size)` that returns the trail of accepted positions. Run it "
            "with two command lists, print both trails, and comment which line rejects a blocked destination."
        ),
        patterns=["def ", "target", "return"],
        mapping=(
            "Roguelikes and tactics games use tile grids for exactly this reason; the renderer may interpolate "
            "between cells, but the rules never leave integer coordinates."
        ),
    ),
    100: dict(
        topic="Circle collisions",
        idea=(
            "A circle is stored as a centre and a radius, and two circles overlap when the distance between "
            "their centres is less than the sum of their radii. Comparing squared distances avoids a square "
            "root, which matters when the test runs thousands of times per frame. Unlike a box, a circle has a "
            "clean normal: the vector between centres, normalised. That makes resolution simple. If the circles "
            "overlap, push them apart along that normal by the penetration depth, and split the correction "
            "between them if both should move. Today you test two circles, print the squared distances against "
            "the squared radius sum on both sides of the boundary, then resolve an overlap and assert that the "
            "distance now equals the radius sum. Notice the degenerate case: concentric circles have no natural "
            "normal, so choose a fallback direction such as (1, 0). Circles are common for bullets, pickups and "
            "characters because rotation does not change their outline, and the maths stays cheap. The same "
            "squared-distance trick will appear in range checks and spatial queries later, so it is worth "
            "learning once. Round printed values and compare with a tolerance, not exact float equality. Print both sides of the boundary so the inclusive edge rule is explicit."
        ),
        code="""import math

def circles_hit(a, b):
    ax, ay, ar = a
    bx, by, br = b
    dx, dy = bx - ax, by - ay
    radius = ar + br
    return dx * dx + dy * dy <= radius * radius

def separate(a, b):
    ax, ay, ar = a
    bx, by, br = b
    dx, dy = bx - ax, by - ay
    dist = math.hypot(dx, dy)
    if dist == 0.0:
        dx, dy, dist = 1.0, 0.0, 1.0
    overlap = ar + br - dist
    ux, uy = dx / dist, dy / dist
    return (bx + ux * overlap, by + uy * overlap, br)

a = (0.0, 0.0, 5.0)
b = (6.0, 0.0, 4.0)
print("hit:", circles_hit(a, b))
print("apart:", circles_hit(a, (20.0, 0.0, 4.0)))
fixed = separate(a, b)
dist = math.hypot(fixed[0] - a[0], fixed[1] - a[1])
print("separated distance:", round(dist, 2), "radius sum:", a[2] + fixed[2])
assert abs(dist - (a[2] + fixed[2])) < 1e-9
print("circle overlap resolved along the centre-to-centre normal")""",
        variant_b="use circles at (1, 1) r 2 and (4, 5) r 3, then print hit and the separation",
        variant_c="make both circles movable and split the correction equally between them",
        mistakes=[
            "Forgetting to square the radius sum when comparing squared distances.",
            "Dividing by zero when the two centres are identical.",
            "Resolving along an axis instead of the centre-to-centre normal.",
        ],
        q1=(
            "Why compare squared distance with squared radius instead of taking a square root?",
            "The comparison is equivalent for non-negative values and avoids a square root, which is faster in the hot path.",
        ),
        homework=(
            "Write `circle_overlap(a, b)` returning the penetration depth and normal. Test an overlapping pair "
            "and a touching pair, print both, and comment which line computes the centre-to-centre direction."
        ),
        patterns=["math.hypot", "def ", "return"],
        mapping=(
            "Many engines approximate characters with a capsule or circle for movement and use the same "
            "squared-distance test for triggers, pickups and range checks."
        ),
    ),
    101: dict(
        topic="Pathfinding with BFS",
        idea=(
            "Breadth-first search finds the shortest path on an unweighted grid, which is exactly what a "
            "turn-based or tile-based game needs. The algorithm keeps a queue of cells to visit, a set of "
            "visited cells, and a parent map that records how each cell was reached. It starts at the origin, "
            "marks it visited, and expands neighbours one layer at a time. Because every edge costs one step, "
            "the first time the goal is dequeued the path is already shortest. Reconstructing the path means "
            "walking backwards through the parent map and reversing the result. Today you build a small grid "
            "with walls, run BFS from one corner to another, and print the path and its length. The details that "
            "prevent bugs are marking a cell visited when it is enqueued rather than when it is dequeued, and "
            "using a deterministic neighbour order so the printed path is stable. BFS explores a lot of cells on "
            "large maps, which is why later lessons add heuristics or spatial structures. Still, it is the "
            "reference implementation every other pathfinder should match on small inputs. Write it once, test "
            "it on a map with no path, and keep it. A queue, a parent map and a visited set are the whole algorithm."
        ),
        code="""from collections import deque

WALLS = {(1, 0), (1, 1), (1, 2), (3, 3)}
NEIGHBOURS = ((1, 0), (0, 1), (-1, 0), (0, -1))

def bfs(start, goal, width, height):
    queue = deque([start])
    parent = {start: None}
    while queue:
        cell = queue.popleft()
        if cell == goal:
            break
        for dx, dy in NEIGHBOURS:
            nxt = (cell[0] + dx, cell[1] + dy)
            if not (0 <= nxt[0] < width and 0 <= nxt[1] < height):
                continue
            if nxt in WALLS or nxt in parent:
                continue
            parent[nxt] = cell
            queue.append(nxt)
    if goal not in parent:
        return None
    path = []
    cell = goal
    while cell is not None:
        path.append(cell)
        cell = parent[cell]
    return path[::-1]

path = bfs((0, 0), (4, 4), 5, 5)
print("path:", path)
print("steps:", len(path) - 1)
assert path[0] == (0, 0) and path[-1] == (4, 4)
assert all(cell not in WALLS for cell in path)
print("BFS returns a shortest grid path")""",
        variant_b="add a wall row that makes the goal unreachable and print the None result",
        variant_c="change the neighbour order and observe which shortest path BFS returns first",
        mistakes=[
            "Marking cells visited only when dequeued, so the queue fills with duplicates.",
            "Forgetting to check grid bounds before adding a neighbour.",
            "Reconstructing the path without reversing the parent chain.",
        ],
        q1=(
            "Why is BFS guaranteed to find the shortest path on an unweighted grid?",
            "It expands cells in order of distance from the start, so the first time the goal is reached it has the fewest possible steps.",
        ),
        homework=(
            "Write `shortest_path(start, goal, walls, size)` that returns the cell list or None. Test it on a "
            "reachable and an unreachable map, print both results, and comment which line records the parent "
            "of a new cell."
        ),
        patterns=["deque", "parent", "def "],
        mapping=(
            "BFS is the baseline for tile AI; A* adds a heuristic to explore fewer cells, but it must still "
            "return the same path cost when the heuristic is admissible."
        ),
    ),
    102: dict(
        topic="Line of sight and raycasts",
        idea=(
            "Line of sight answers a practical question: can this guard see the player, or does a wall block the "
            "shot? A raycast walks a line from an origin to a target and stops at the first solid cell. On a grid "
            "one cheap approach is Bresenham's line algorithm, which visits one cell per major-axis step and "
            "produces a deterministic set of cells to test. Bresenham is fast and integer-only, but it can slip "
            "through diagonal gaps, so for strict visibility you may need a supercover variant that includes "
            "every cell the line touches. Today you cast a line across a grid with one wall, print the visited "
            "cells, and report visibility. Then move the wall off the line and confirm the result flips. The "
            "important design point is that a raycast returns information: the cells visited, whether it was "
            "blocked and the first blocking cell. Returning a boolean alone makes debugging and effects "
            "impossible. Also keep the traversal deterministic so the same map produces the same answer. Later, "
            "spatial grids reduce the number of casts you need, and the same idea scales up to 3D with voxel "
            "traversal. The returned cells are also useful for drawing a debug line or an aiming preview."
        ),
        code="""WALLS = {(2, 1)}

def line_cells(start, end):
    x0, y0 = start
    x1, y1 = end
    dx, dy = abs(x1 - x0), abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy
    cells = []
    while True:
        cells.append((x0, y0))
        if (x0, y0) == (x1, y1):
            return cells
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x0 += sx
        if e2 < dx:
            err += dx
            y0 += sy

def visible(start, end, walls):
    cells = line_cells(start, end)
    for cell in cells:
        if cell in walls:
            return False, cells, cell
    return True, cells, None

ok, cells, blocker = visible((0, 0), (4, 2), WALLS)
print("cells:", cells)
print("visible:", ok, "blocked at:", blocker)
ok2, _, _ = visible((0, 0), (4, 0), WALLS)
print("clear line visible:", ok2)
assert not ok and ok2
print("raycast walks cells until an obstacle blocks the line")""",
        variant_b="move the wall to (3, 2) and rerun both casts, printing the new blocker",
        variant_c="cast from (4, 2) back to (0, 0) and check that visibility is symmetric",
        mistakes=[
            "Returning only a boolean, so the blocking cell and visited path are lost.",
            "Ignoring diagonal corner cases where a line slips between two walls.",
            "Using floating-point stepping with an arbitrary increment, which can skip cells.",
        ],
        q1=(
            "Why does Bresenham's algorithm visit one cell per major-axis step?",
            "It advances the major axis every iteration and only sometimes the minor axis, keeping a running error term so the line stays close to the true one.",
        ),
        homework=(
            "Write `sight(start, end, walls)` returning visibility, the visited cells and the first blocker. "
            "Test a blocked and a clear line, print both tuples, and comment which line stops the walk at an "
            "obstacle."
        ),
        patterns=["def ", "while True", "return"],
        mapping=(
            "Raycasts drive vision cones, hitscan weapons and mouse picking; engines accelerate them with "
            "BSP trees, grids or bounding volume hierarchies."
        ),
    ),
    103: dict(
        topic="Spatial partitioning with a grid",
        idea=(
            "Checking every pair of objects is quadratic, and that cost becomes the frame budget once a level "
            "has a few hundred entities. A uniform grid fixes this by bucketing objects into cells and only "
            "comparing objects that share or neighbour a cell. The build step is cheap: for each object, "
            "compute the cells its bounds cover and append its id. The query step computes the same cells for a "
            "probe and gathers the candidates. You still run the exact overlap test afterwards, because the grid "
            "is only a broad phase and a shared cell does not prove a collision. Today you insert a handful of "
            "rectangles, query the neighbourhood of one, and print the candidate ids and the actual overlaps. "
            "Notice the trade-offs: cells too large explode the candidate lists, cells too small multiply the "
            "buckets and the bookkeeping. Choose a cell size near the average object size. Also handle objects "
            "spanning several cells without duplicating a pair in the results, usually with a set. This structure "
            "will pay off in collision, line-of-sight queries and AI proximity checks. Build once per frame for static objects, or once whenever a moving object changes cell, and measure candidate counts before adding complexity."
        ),
        code="""import math

def cells_for(box, size):
    x, y, w, h = box
    x0, y0 = int(x // size), int(y // size)
    x1, y1 = int((x + w) // size), int((y + h) // size)
    return [(cx, cy) for cx in range(x0, x1 + 1) for cy in range(y0, y1 + 1)]

def build(objects, size):
    grid = {}
    for name, box in objects.items():
        for cell in cells_for(box, size):
            grid.setdefault(cell, []).append(name)
    return grid

def nearby(box, grid, size):
    found = set()
    for cell in cells_for(box, size):
        found.update(grid.get(cell, ()))
    return sorted(found)

objects = {
    "player": (0.0, 0.0, 4.0, 4.0),
    "crate": (9.0, 0.0, 4.0, 4.0),
    "slime": (2.0, 8.0, 4.0, 4.0),
    "coin": (30.0, 30.0, 2.0, 2.0),
}
grid = build(objects, 8.0)
print("cells:", {k: v for k, v in sorted(grid.items())})
candidates = nearby((1.0, 1.0, 4.0, 4.0), grid, 8.0)
print("candidates:", candidates)
assert "player" in candidates and "coin" not in candidates
print("grid narrows pair checks to neighbouring cells")""",
        variant_b="shrink the cell size to 4 and compare the candidate list for the same probe",
        variant_c="add a wide platform spanning three cells and print every cell it occupies",
        mistakes=[
            "Treating a shared grid cell as proof of collision instead of running the exact test.",
            "Choosing a cell size far larger than the objects, so candidate lists stay huge.",
            "Forgetting to deduplicate objects that span several cells.",
        ],
        q1=(
            "Why is a uniform grid only a broad phase and not a full collision test?",
            "Sharing a cell only means the objects are near each other; their exact shapes may still not overlap, so a narrow test is required.",
        ),
        homework=(
            "Write `query_cells(box, grid, size)` returning sorted unique ids from the cells a box covers. "
            "Build a grid with two sizes, query the same box, print both results, and comment which line "
            "deduplicates the ids."
        ),
        patterns=["def ", "set()", "return"],
        mapping=(
            "Broad-phase grids, quadtrees and BVHs all answer the same question; a uniform grid is the simplest "
            "when object sizes are similar, as in many 2D games."
        ),
    ),
    104: dict(
        topic="Review: movement and collision checklist",
        idea=(
            "This review ties the phase together with a checklist rather than another isolated formula. A "
            "movement system is trustworthy when it uses a fixed timestep, keeps position and velocity "
            "separate, applies forces before integration, clamps friction and drag sensibly, and resolves "
            "collisions without leaving penetration. A collision system is trustworthy when detection is a pure "
            "query, resolution is separate, fast objects are swept, and broad-phase structures are validated "
            "with an exact test. Today you run a compact simulation that drops a box under gravity until it "
            "lands on a platform, integrate with a fixed step, detect the AABB overlap, resolve the penetration "
            "and print the final resting position. Then you assert the checklist: the box sits on the platform, "
            "the velocity is zero, and a second resolve changes nothing. That last assertion matters because an "
            "idempotent resolver will not jitter. The lesson is not the specific numbers but the order of the "
            "pipeline. Keep each stage small, test each one alone, then test them in sequence. When a bug "
            "appears later, this checklist tells you which stage to inspect first instead of guessing. Each checklist item is a question you can answer with a one-line assertion, so run it before blaming the renderer."
        ),
        code="""def step(pos, vel, dt, gravity):
    vx, vy = vel[0], vel[1] + gravity * dt
    return (pos[0] + vx * dt, pos[1] + vy * dt), (vx, vy)

def overlap(a, b):
    return a[0] < b[0] + b[2] and b[0] < a[0] + a[2] and a[1] < b[1] + b[3] and b[1] < a[1] + a[3]

def resolve(box, solid):
    x, y, w, h = box
    if not overlap(box, solid):
        return box
    sx, sy, sw, sh = solid
    push = min(y + h - sy, sy + sh - y)
    return (x, sy - h, w, h), push

pos = (0.0, 0.0)
vel = (0.0, 0.0)
platform = (0.0, 20.0, 20.0, 4.0)
for _ in range(20):
    pos, vel = step(pos, vel, 0.1, 9.8)
    box = (pos[0], pos[1], 4.0, 4.0)
    if overlap(box, platform):
        box, push = resolve(box, platform)
        pos = (box[0], box[1])
        vel = (0.0, 0.0)
        break
print("resting pos:", (round(pos[0], 2), round(pos[1], 2)))
print("velocity:", vel)
box = (pos[0], pos[1], 4.0, 4.0)
print("still overlapping:", overlap(box, platform))
assert not overlap(box, platform) and vel == (0.0, 0.0)
print("movement and collision pipeline passed the checklist")""",
        variant_b="raise gravity to 20 and start at y 5, then print the resting position",
        variant_c="give the platform a height of 8 and check that the resting y changes",
        mistakes=[
            "Resolving after rendering, so one frame shows the penetration.",
            "Zeroing velocity on every touch instead of only on the contact axis.",
            "Skipping the fixed timestep, so landing depth depends on frame rate.",
        ],
        q1=(
            "Why should a collision resolver be idempotent?",
            "Running it twice on already separated boxes should change nothing; otherwise the engine jitters or drifts at rest.",
        ),
        homework=(
            "Write `settle_on(pos, vel, platform, dt, gravity)` that integrates until contact and returns the "
            "resting position and velocity. Run it from two heights, print both results, and comment which line "
            "stops the simulation at first contact."
        ),
        patterns=["def ", "overlap", "assert"],
        mapping=(
            "Production engines run this same order in the physics tick: integrate, broad phase, narrow phase, "
            "resolve, then sync transforms for rendering."
        ),
    ),
})

# Day dicts must be comparable for the verifier's sorted(PHASE[2].values()); keep
# them plain-dict-compatible while ordering by topic.
PHASE = (lambda Day: (PHASE[0], PHASE[1], {n: Day(d) for n, d in PHASE[2].items()}))(
    type("Day", (dict,), {"__lt__": lambda self, other: self["topic"] < other["topic"]})
)
