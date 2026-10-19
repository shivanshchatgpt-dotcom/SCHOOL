"""Widgets and Layout, days 75-89: the desktop UI data model, headless and runnable.

Each day keeps the same discipline as the foundation arc: no toolkit import, no
window, no clock and no network. Windows, widgets, geometry managers, dialogs
and scroll offsets are plain dicts and arithmetic, and every example prints the
computed layout as text so the numbers can be checked in a test. What a real
toolkit draws is the last step; the layout it draws is the part modelled here.
"""

PHASE = ("Widgets and Layout", "Model a desktop interface as widgets and arithmetic, then compute a layout you can print, audit and test.", {
    75: dict(
        topic="Orientation: what a GUI toolkit gives you",
        idea=(
            "A GUI toolkit is a loan, and like any loan you should know what it covers before you sign. It gives "
            "you a window, a widget vocabulary, a geometry manager, an event loop, focus handling, redraw, "
            "clipboard and theming, and in exchange your program gives up direct control of pixels and becomes a "
            "set of callbacks. Beginners often fight the toolkit because they expect it to be a drawing library: "
            "they compute coordinates by hand while the geometry manager recomputes them, or they block the event "
            "loop with work and wonder why nothing repaints. Knowing the division of labour fixes most of that. "
            "The toolkit owns presentation and delivery; your code owns state and rules. In this phase every "
            "example keeps that split, modelling windows, widgets and layout as dictionaries so you can print the "
            "result without a display. That is not a trick to avoid the real thing. It is a way to see the "
            "contract clearly, because the numbers a toolkit computes are the same numbers you compute here. When "
            "you later call pack or grid, you will recognise the arithmetic underneath. Today you inventory what "
            "a toolkit supplies and note which parts you would otherwise have to build yourself."
        ),
        code=(
            """\
TOOLKIT = {
    "widgets": ["window", "label", "entry", "button", "menu"],
    "layout": ["pack", "grid", "place"],
    "services": ["event loop", "redraw", "focus", "clipboard"],
}

def provided(toolkit):
    return sum(len(parts) for parts in toolkit.values())

print("what the toolkit hands you")
for category, parts in TOOLKIT.items():
    print(f"{category:9} {len(parts)}: {', '.join(parts)}")
print("total parts:", provided(TOOLKIT))

assert provided(TOOLKIT) == 12
print("your app supplies the data; the toolkit supplies the machinery")
"""
        ),
        variant_b="add a \"drawing\" category with two entries and check the new total",
        variant_c="write `missing(toolkit, needed)` that reports which needed services the toolkit does not list",
        mistakes=[
            "Treating the toolkit as a drawing library and fighting the geometry manager with hand-placed coordinates.",
            "Doing long work inside a handler, which starves the event loop the toolkit runs for you.",
            "Assuming every feature is portable, then discovering menus or clipboard behaviour differs per platform.",
        ],
        q1=(
            "Which responsibilities belong to the toolkit and which to your code?",
            "The toolkit handles windows, widgets, layout, events, focus and redraw; your code owns state, rules and what each action means.",
        ),
        homework=(
            "Write `inventory(toolkit)` that walks a dict of categories and returns the total number of supplied "
            "parts plus a sorted list of category names. Print the inventory for a toolkit of your own, then add "
            "one category and print it again, and comment which line proves the count is derived rather than hard-coded."
        ),
        patterns=["def ", "return", "print("],
        mapping=(
            "Tkinter's `Tk` root, widget classes, `mainloop` and geometry managers are exactly this inventory; Qt "
            "splits the same duties across `QApplication`, widgets, layouts and the event loop."
        ),
    ),
    76: dict(
        topic="Widgets as a tree",
        idea=(
            "The moment you stop thinking of widgets as painted shapes and start thinking of them as a tree, layout "
            "and teardown become obvious. A window has children, a frame has children, and every child knows one "
            "parent. That single rule gives you a way to walk the interface: count nodes, find all buttons, "
            "restyle a container, or destroy a branch and everything under it. It also explains a class of leaks: "
            "a widget whose parent was destroyed but whose reference survives in a list is now an orphan holding "
            "memory and callbacks. Modelling the form as nested dictionaries makes the tree explicit, and a "
            "recursive walk prints it with indentation, which is exactly how you would inspect a real widget "
            "hierarchy in a debugger. The exercise also teaches you to separate structure from presentation. The "
            "tree does not care where a widget sits; the geometry manager does. Today you build a login form as a "
            "tree, count its nodes and print it with depth. Keep the parent link in the data rather than inferring "
            "it from position, because position is a layout decision and structure is a fact about ownership. "
            "That distinction pays off when you rebuild a form from a schema."
        ),
        code=(
            """\
TREE = {
    "kind": "window", "text": "Login",
    "children": [
        {"kind": "label", "text": "Email", "children": []},
        {"kind": "entry", "text": "email", "children": []},
        {"kind": "frame", "text": "actions", "children": [
            {"kind": "button", "text": "Cancel", "children": []},
            {"kind": "button", "text": "Sign in", "children": []},
        ]},
    ],
}

def walk(node, depth=0):
    label = node.get("text", "")
    print("  " * depth + f"{node['kind']} {label}".rstrip())
    for child in node["children"]:
        walk(child, depth + 1)

def count(node):
    return 1 + sum(count(child) for child in node["children"])

walk(TREE)
print("nodes:", count(TREE))
assert count(TREE) == 6
print("the frame owns two buttons; the window owns everything")
"""
        ),
        variant_b="add a password entry and a hint label under the window, then recount the nodes",
        variant_c="write `find(node, kind)` returning every widget of one kind, and list the form's buttons",
        mistakes=[
            "Keeping only a flat list of widgets, so parent-child ownership has to be guessed from order.",
            "Forgetting to destroy or release a subtree, leaving callbacks pointing at dead widgets.",
            "Treating a frame as decoration rather than as the owner of a group of widgets.",
        ],
        q1=(
            "Why keep the parent link in the widget data instead of inferring it from position?",
            "Position is a layout decision that changes, while the parent link is stable ownership that teardown, styling and traversal depend on.",
        ),
        homework=(
            "Write `walk_tree(node, depth=0)` that prints each widget indented by depth and returns the total "
            "node count. Build a tree with a window, a frame and two buttons, print it, then remove one button "
            "and print again, and comment which line makes the recursion visit nested children."
        ),
        patterns=["def ", "children", "print("],
        mapping=(
            "Tkinter `Widget.master` and `winfo_children()` expose this tree, and Qt's `QObject.parent()` and "
            "`findChildren()` do the same; destroying a parent takes its subtree with it."
        ),
    ),
    77: dict(
        topic="Geometry managers: pack",
        idea=(
            "Pack is the geometry manager people use first and understand last. It places widgets in a single "
            "line, top to bottom by default, and the interesting part is what happens to leftover space. Each "
            "widget asks for its natural size, pack allocates it plus padding and spacing, and the rest is either "
            "ignored or given to widgets marked to expand. If you only ever test at one window size, you never see "
            "the difference. Modelling pack as a running cursor makes the rule concrete: start at the top margin, "
            "give each widget its requested height, add the gap, and move down. The number left at the bottom is "
            "the space available for expansion, and a single expanding widget will claim all of it. This is why a "
            "footer sometimes floats in the middle and sometimes sticks to the bottom depending on which widget "
            "expands. Order matters too: pack consumes space in the order children were added, so adding a status "
            "bar last does not place it last if an earlier child expanded. Today you simulate a vertical pack of a "
            "header, a body and a footer, print each y coordinate and the final bottom edge, then check the "
            "arithmetic adds up. The same trace tells you where to put the expand flag."
        ),
        code=(
            """\
def pack(children, start=10, gap=6):
    placed, y = [], start
    for name, height in children:
        placed.append((name, y, height))
        y += height + gap
    return placed, y - gap

children = [("header", 40), ("body", 160), ("footer", 24)]
placed, bottom = pack(children)
for name, y, height in placed:
    print(f"{name:7} y={y:3} h={height:3}")
print("bottom edge:", bottom)
print("leftover below footer:", 300 - bottom)

assert bottom == 10 + 40 + 6 + 160 + 6 + 24
assert placed[1][1] == placed[0][1] + placed[0][2] + 6
print("each widget starts after the previous one plus the gap")
"""
        ),
        variant_b="insert a 32-pixel toolbar before the header and print the new y positions",
        variant_c="mark the body as expanding and show that it receives all leftover height at a 500-pixel window",
        mistakes=[
            "Adding widgets in a different order than you expect them to appear, because pack consumes space in insertion order.",
            "Forgetting that padding and gaps accumulate, so the last widget is pushed past the window edge.",
            "Marking several siblings to expand and then being surprised that the leftover space is split between them.",
        ],
        q1=(
            "What determines the order in which pack places siblings?",
            "The order they were added to the parent, not their visual importance or the order they are configured.",
        ),
        homework=(
            "Write `pack_rows(rows, start, gap)` that returns a list of (name, y, height) tuples and the final "
            "bottom edge. Feed it four rows at two different window heights, print both traces, and comment which "
            "line advances the cursor by the widget height plus the gap."
        ),
        patterns=["def ", "return", "print("],
        mapping=(
            "Tkinter's `pack(side='top', fill='x', expand=True)` is this cursor with expansion added; Qt's "
            "`QVBoxLayout` is the same idea under a different name."
        ),
    ),
    78: dict(
        topic="Geometry managers: grid",
        idea=(
            "Grid asks two questions per widget: which row and column, and how many cells does it span. Everything "
            "else, including column widths, is derived. That is why grid is the right manager for forms and "
            "dashboards and a poor fit for a single row of buttons. The key insight is that a grid is not a table "
            "of fixed pixels; it is a set of columns whose width is the largest requested width in that column, "
            "unless a weight says to share extra space. If you compute positions as origin plus index times cell "
            "size plus gaps, you have the whole model. The traps are easy to name: forgetting the gap in the "
            "multiply, mixing zero-based and one-based indexes between toolkits, and spanning a widget across "
            "cells without telling the content how to align. Today you lay out a settings dialog in a three-by-two "
            "grid, print each cell's rectangle and label, and verify the right edge of the last column from the "
            "arithmetic. Notice that changing one label's width would change the whole column, which is the "
            "behaviour you want in a form and the behaviour that surprises people in a toolbar. That difference is "
            "the practical reason to know both grid and pack rather than picking a favourite."
        ),
        code=(
            """\
def cells(rows, cols, w, h, gap=8, left=12, top=12):
    out = {}
    for r in range(rows):
        for c in range(cols):
            out[(r, c)] = (left + c * (w + gap), top + r * (h + gap), w, h)
    return out

layout = cells(3, 2, 140, 30)
labels = ["Name", "Ada", "Email", "ada@example.com", "Plan", "Pro"]
for (r, c), (x, y, w, h) in layout.items():
    print(f"row {r} col {c}: x={x:3} y={y:3} {w}x{h}  {labels[r * 2 + c]}")
right = max(x + w for x, y, w, h in layout.values())
print("grid right edge:", right)
print("grid width with gaps:", 12 + 2 * 140 + 8)

assert right == 12 + 140 + 8 + 140
assert layout[(2, 1)][0] == 12 + 148
print("column one starts one cell plus one gap after column zero")
"""
        ),
        variant_b="add a third column for a default value and recompute every x coordinate",
        variant_c="span the plan field across both columns and print the width it should receive",
        mistakes=[
            "Computing a column position as index times width and forgetting the gaps between columns.",
            "Mixing Tkinter's one-based rows and columns with a zero-based Python list of cells.",
            "Spanning a widget but leaving its content request at one cell, so it looks cramped or overflows.",
        ],
        q1=(
            "Why is grid usually a better fit for a form than for a row of toolbar buttons?",
            "A form needs aligned label and field columns whose widths derive from content, while a toolbar wants one flexible row rather than a column structure.",
        ),
        homework=(
            "Write `grid_cells(rows, cols, cell_w, cell_h, gap)` returning a dict from (row, col) to an "
            "(x, y, w, h) rectangle. Print a two-by-three layout, compute its right edge with `max`, and comment "
            "which line adds the gap between columns."
        ),
        patterns=["def ", "range(", "print("],
        mapping=(
            "Tkinter's `grid(row=, column=, sticky=, columnspan=)` and Qt's `QGridLayout` both derive cell "
            "geometry from content requests plus stretch rules."
        ),
    ),
    79: dict(
        topic="Geometry managers: place",
        idea=(
            "Place is the escape hatch: you give a widget an absolute or relative position and it goes there, with "
            "no negotiation. That makes it perfect for overlays, canvas annotations, splash elements and anything "
            "that must sit at a mathematically exact spot. It is a poor default for forms because it does not "
            "respond to font changes, translations or window resizing. The model is small: a position can be a "
            "fraction of the parent, an offset in pixels, or both, and an anchor decides which corner of the "
            "widget is being positioned. Convert the fractions to pixels, add the offsets, and you have a "
            "rectangle. Two checks catch almost every place bug: is the rectangle inside the parent, and does it "
            "stay inside when the parent shrinks. Today you position a status label and a close button at the "
            "bottom of a four-hundred by three-hundred window, print both boxes and their margins, and assert the "
            "right and bottom edges land where intended. The exercise is also a lesson in when not to use the "
            "tool: because nothing reflows, you must decide the behaviour at every size yourself. Use place "
            "deliberately, for a few elements, and let a geometry manager handle the rest of the interface."
        ),
        code=(
            """\
def place(relx, rely, x=0, y=0, width=100, height=24, parent=(400, 300)):
    px = int(parent[0] * relx) + x
    py = int(parent[1] * rely) + y
    return {"x": px, "y": py, "w": width, "h": height,
            "right": px + width, "bottom": py + height}

status = place(1.0, 1.0, x=-168, y=-28, width=156, height=20)
close = place(1.0, 0.0, x=-32, y=8, width=24, height=24)

for name, box in [("status", status), ("close", close)]:
    print(f"{name:6} x={box['x']:3} y={box['y']:3} right={box['right']:3} bottom={box['bottom']:3}")
print("status margin right/bottom:", 400 - status["right"], 300 - status["bottom"])

assert status["right"] == 388 and status["bottom"] == 292
assert close["right"] == 392
print("relative anchor plus pixel offset gives an exact rectangle")
"""
        ),
        variant_b="anchor a badge at the top-right with a twelve-pixel inset and print its box",
        variant_c="resize the parent to 320 by 240 and show which hand-placed rectangles now fall outside",
        mistakes=[
            "Hand-placing a whole form, so the layout breaks on any font or window-size change.",
            "Forgetting the anchor corner, then wondering why a bottom-right button is offset by its own size.",
            "Mixing relative fractions with absolute pixels without printing the resolved rectangle.",
        ],
        q1=(
            "When is place the right geometry manager?",
            "For a small number of elements that must land at an exact spot or track a parent fraction, such as overlays, badges or canvas annotations.",
        ),
        homework=(
            "Write `place_box(parent_w, parent_h, relx, rely, x, y, width, height)` returning a resolved "
            "rectangle dict. Place two elements at different anchors, print both, and comment which line converts "
            "the relative position into pixels."
        ),
        patterns=["def ", "int(", "print("],
        mapping=(
            "Tkinter's `place(relx=, rely=, anchor=)` and Qt's absolute `setGeometry` are the same escape hatch; "
            "both are best reserved for overlays rather than forms."
        ),
    ),
    80: dict(
        topic="Sizing, weights and stretch",
        idea=(
            "Sizing is where a layout stops being a list of widgets and becomes a negotiation. Each widget has a "
            "requested size, a minimum below which it becomes useless, and a willingness to grow. A weight "
            "expresses that willingness as a share of the leftover space, not a share of the total. That "
            "distinction is the source of most confusion: with weights two, one and one, the panes do not get "
            "fifty, twenty-five and twenty-five percent of the window; they get their natural sizes plus half, a "
            "quarter and a quarter of whatever remains. If you want true proportions you set the requested sizes "
            "small and let the weights dominate. That is a common source of surprise when a pane refuses to "
            "reach the ratio you planned. Rounding is the other trap. Integer division loses pixels, so a "
            "consistent rule, such as giving the remainder to the last pane, keeps the total exact and "
            "reproducible. Today you stretch three dashboard panes across a nine-hundred-pixel window with a gap, "
            "print the widths and the sum, then repeat at six hundred and forty pixels. The identity widths plus "
            "gaps equals the window width is the assertion to keep. Once you trust that identity, resizing stops "
            "being a visual guess and becomes a calculation you can test."
        ),
        code=(
            """\
def stretch(total, weights, gap=0):
    usable = total - gap * (len(weights) - 1)
    share = usable // sum(weights)
    widths = [weight * share for weight in weights]
    widths[-1] += usable - sum(widths)
    return widths

for total in (900, 640):
    widths = stretch(total, [2, 1, 1], gap=10)
    print(f"window {total}: panes {widths} sum={sum(widths)}")
    assert sum(widths) + 10 * 2 == total

print("ratio at 900:", stretch(900, [2, 1, 1], 10))
print("remainder always lands in the last pane")
assert stretch(900, [2, 1, 1], 10)[0] == 2 * stretch(900, [2, 1, 1], 10)[1]
"""
        ),
        variant_b="change the gaps to 16 and confirm the pane widths shrink while the total identity holds",
        variant_c="add a minimum width per pane and report when a small window can no longer satisfy all minimums",
        mistakes=[
            "Reading a weight as a percentage of the window instead of a share of the leftover space.",
            "Dropping the rounding remainder, so the panes are a few pixels narrower than the window.",
            "Giving every pane the same weight and expecting a designed hierarchy to appear anyway.",
        ],
        q1=(
            "What does a weight of 2 mean when it sits beside weights of 1 and 1?",
            "That pane gets twice the share of leftover space given to each neighbour, after natural sizes and gaps are removed.",
        ),
        homework=(
            "Write `stretch(total, weights, gap)` returning pane widths whose sum plus gaps equals the total, "
            "with the rounding remainder added to the last pane. Print the result for two weights and two window "
            "widths, and comment which line places the remainder."
        ),
        patterns=["def ", "sum(", "print("],
        mapping=(
            "Tkinter's `weight` in `grid_columnconfigure`, Qt's stretch factors and CSS `flex-grow` all describe "
            "the same leftover-space share."
        ),
    ),
    81: dict(
        topic="Padding, margins and spacing",
        idea=(
            "Padding, margins and spacing look like synonyms until a layout is off by eight pixels and nobody can "
            "say why. They belong to different owners. Padding is space inside a container around its content. A "
            "border sits outside the padding and is drawn. A margin is space outside the widget that separates it "
            "from its neighbours. Spacing is the gap a layout manager inserts between siblings. Tkinter exposes "
            "padding through padx and pady, Qt through contents margins and spacing, and CSS names all four "
            "explicitly, which is why web developers often find box models easier to reason about. The reliable "
            "approach is to model the box from the inside out: content size, add border, add padding, add margin, "
            "and print each stage. Then the total is not a mystery; it is a sum. Two practical rules follow. Never "
            "mix padding and margin to achieve the same visual gap in one container, because the next change will "
            "double it. And keep one spacing value per container rather than hand-tuning each child. Today you "
            "compute the outer size of a labelled field at each stage and check the total. The numbers are small, "
            "but the habit scales to every dialog you will build."
        ),
        code=(
            """\
def box(content, pad, border, margin):
    after_border = content + 2 * border
    after_pad = after_border + 2 * pad
    total = after_pad + 2 * margin
    return {"content": content, "border_box": after_border,
            "pad_box": after_pad, "margin_box": total}

field = box(content=120, pad=8, border=1, margin=6)
for stage in ("content", "border_box", "pad_box", "margin_box"):
    print(f"{stage:11} {field[stage]}")

print("horizontal space outside the label:", field["margin_box"] - field["content"])
assert field["margin_box"] == 150
assert field["pad_box"] == 138

spacing = 8
row = field["margin_box"] + spacing + field["margin_box"]
print("two fields and the spacing between:", row)
"""
        ),
        variant_b="set border to 2 and padding to 4, then confirm the outer size is unchanged",
        variant_c="model vertical spacing separately and compute the height of a three-row field group",
        mistakes=[
            "Using padding and margin interchangeably, so gaps double when the two are combined.",
            "Forgetting that padding applies on both sides, then undercounting the outer size by half.",
            "Mixing a per-widget margin with a container spacing value and losing track of the total gap.",
        ],
        q1=(
            "Which of padding, border, margin and spacing is owned by the layout manager rather than the widget?",
            "Spacing between siblings is inserted by the layout manager; padding, border and margin describe the widget's own box.",
        ),
        homework=(
            "Write `outer_size(content, pad, border, margin)` returning the final box width and height for a "
            "square content area. Print the size for two settings, then place two boxes in a row with `spacing`, "
            "and comment which line adds the margin on both sides."
        ),
        patterns=["def ", "return", "print("],
        mapping=(
            "Tkinter's `padx`/`pady` and Qt's contents margins map to padding, while layout `spacing` and CSS "
            "`gap` map to the manager-owned gap."
        ),
    ),
    82: dict(
        topic="Frames and containers",
        idea=(
            "A frame is a container with no visible purpose except to own a region and its rules. That sounds "
            "modest, but it is the main tool for keeping a layout comprehensible. Instead of one window with "
            "twelve children and a pile of exceptions, you get a header frame, a sidebar frame, a content frame "
            "and a footer frame, each with its own padding and geometry manager. The outer layout then only has to "
            "place four things. This decomposition is why experienced developers can change a toolbar without "
            "touching the form. It also localises bugs: if the sidebar is wrong, you look at the sidebar frame, "
            "not the whole window. The arithmetic is simple subtraction. Take the window width, remove the outer "
            "padding, remove the sidebar and the gap, and the content frame gets the rest. Do the same vertically "
            "for header and footer, and you have a layout grid of regions before any widget is placed. Today you "
            "split a six-hundred-and-forty-pixel window into a sidebar and content area, print the regions and "
            "assert they add back to the inner width. Keep frames shallow; deep nesting hides the very clarity you "
            "built it for, and each level costs padding you must account for."
        ),
        code=(
            """\
def split(window_w, sidebar_w, gap, pad):
    inner = window_w - 2 * pad
    content = inner - sidebar_w - gap
    return {"padding": pad, "inner": inner, "sidebar": sidebar_w,
            "gap": gap, "content": content}

parts = split(window_w=640, sidebar_w=200, gap=8, pad=12)
for name, value in parts.items():
    print(f"{name:8} {value}")

assert parts["sidebar"] + parts["gap"] + parts["content"] == parts["inner"]
print("regions fill the inner width exactly")

nested = split(parts["content"], 160, 8, 0)
print("content frame split again:", nested)
assert nested["content"] == 408 - 160 - 8
print("a frame is just another parent with its own arithmetic")
"""
        ),
        variant_b="add a 48-pixel header above the split and recompute the content height",
        variant_c="nest two frames and show how each level of padding reduces the available width",
        mistakes=[
            "Putting every widget directly in the window, so one change disturbs unrelated regions.",
            "Nesting frames so deeply that padding at each level consumes the space the content needs.",
            "Mixing pack in one part of a parent and grid in another, which the toolkit cannot reconcile.",
        ],
        q1=(
            "What does a frame contribute to a layout besides grouping widgets visually?",
            "It owns its region's padding, geometry manager and children, so changes inside it do not disturb the outer layout.",
        ),
        homework=(
            "Write `split_regions(window_w, sidebar_w, gap, pad)` returning inner, sidebar, gap and content "
            "widths. Print the split for two window sizes, assert the regions add back to the inner width, and "
            "comment which line subtracts both the sidebar and the gap."
        ),
        patterns=["def ", "return", "print("],
        mapping=(
            "Tkinter's `ttk.Frame` and Qt's `QWidget` containers exist for exactly this decomposition; a nested "
            "frame with its own layout is the standard way to isolate a region."
        ),
    ),
    83: dict(
        topic="Menus and toolbars",
        idea=(
            "A menu bar is a small tree with accelerators attached. Each top-level entry owns a list of items, "
            "items can be separators, and some carry a shortcut, a check state or a submenu. Toolbars are the same "
            "commands with icons and a much smaller budget for space. The important design point is that the "
            "command should exist once and be referenced from both places. If the menu handler and the toolbar "
            "handler are separate functions, they will drift, and one day Save from the toolbar will do something "
            "slightly different from Save in the menu. Model commands by name, then let the menu and toolbar "
            "render references to those names. Accelerators are not decoration either: they are the difference "
            "between a usable app and a mouse-only one, and they must be unique within a window or the first match "
            "wins silently. Today you model a two-menu application, count its commands, list the shortcuts and "
            "print each entry with its index. Notice that separators do not count as commands and that disabled "
            "items still occupy a slot. That indexing detail matters later when you generate menus from a list of "
            "available actions rather than writing them by hand. A menu that cannot be reached by keyboard is a "
            "menu half the users cannot use."
        ),
        code=(
            """\
MENUS = [
    ("File", [("New", "Ctrl+N"), ("Open", "Ctrl+O"), None, ("Quit", "Ctrl+Q")]),
    ("Edit", [("Undo", "Ctrl+Z"), ("Redo", "Ctrl+Y")]),
]

def commands(menu):
    return [entry for _, items in menu for entry in items if entry]

def shortcuts(menu):
    return [entry[1] for entry in commands(menu)]

for title, items in MENUS:
    print(title)
    for index, entry in enumerate(items):
        if entry is None:
            print(f"  {index}: --- separator")
        else:
            print(f"  {index}: {entry[0]:9} {entry[1]}")

print("commands:", len(commands(MENUS)))
assert len(commands(MENUS)) == 5
assert len(shortcuts(MENUS)) == len(set(shortcuts(MENUS)))
print("separators are not commands and shortcuts stay unique")
"""
        ),
        variant_b="add a View menu with a checkable item and a unique accelerator",
        variant_c="derive a toolbar from the command names and skip separators and disabled items",
        mistakes=[
            "Wiring menu and toolbar to separate callbacks, so the same command behaves differently in two places.",
            "Assigning the same accelerator twice, which silently makes one of the bindings unreachable.",
            "Counting separators as commands when writing tests or generating a toolbar from the menu.",
        ],
        q1=(
            "Why should menu and toolbar entries reference one command definition?",
            "So the action and its enabled state cannot drift apart; both surfaces stay in sync when the command changes.",
        ),
        homework=(
            "Write `flatten_menu(menu)` returning a list of labels and accelerators while skipping separators, "
            "plus a separate `shortcuts(menu)` built on it. Print both for a two-menu structure, add a third "
            "menu, print again, and comment which line filters the separators."
        ),
        patterns=["def ", "return", "print("],
        mapping=(
            "Tkinter's `Menu` with `add_command` and `add_separator`, and Qt's `QMenu`/`QAction`, both expect a "
            "single action object shared with the toolbar."
        ),
    ),
    84: dict(
        topic="Dialogs and modal flow",
        idea=(
            "A dialog is a small window with a job and a return value. A modal dialog additionally blocks its "
            "parent until it closes, and that blocking is the whole reason modal flow needs care. If you open a "
            "settings dialog, then open a confirmation from inside it, the stack is two deep; cancelling the "
            "confirmation must return to settings, not to the main window. Model that as a stack and the rules "
            "become testable: open pushes, accept and cancel pop, and any attempt to interact with a blocked "
            "parent is refused. The classic bugs are a dialog that never pops because an error path returned "
            "early, and a parent that stays disabled after the child closes. Keeping the stack explicit makes "
            "both visible in a printed trace. The return value matters too. A settings dialog should not apply "
            "changes until it is accepted, or Cancel becomes a lie. The parent is disabled while the child runs, "
            "so the user cannot start a second flow. Today you script a flow that opens settings, "
            "opens a confirmation, declines it, then accepts settings, printing each transition and the stack "
            "depth. At the end the stack must be empty. That assertion is worth more than any amount of clicking, "
            "because it proves every path unwinds."
        ),
        code=(
            """\
def run_flow(actions):
    stack, log = [], []
    for action in actions:
        if action.startswith("open:"):
            name = action.split(":", 1)[1]
            stack.append(name)
            log.append(f"open {name:9} depth={len(stack)}")
        elif action == "accept" and stack:
            log.append(f"accept {stack.pop():7} depth={len(stack)}")
        elif action == "cancel" and stack:
            log.append(f"cancel {stack.pop():7} depth={len(stack)}")
        else:
            blocked = stack[-1] if stack else "nothing"
            log.append(f"blocked {action:7} by {blocked}")
    return log, stack

actions = ["open:settings", "open:confirm", "cancel", "accept", "click:main"]
log, stack = run_flow(actions)
for line in log:
    print(line)
print("remaining dialogs:", stack)
assert stack == [] and log[-1].startswith("blocked")
print("every dialog path unwound; the parent was blocked while modal")
"""
        ),
        variant_b="add an `open:error` path that is dismissed with OK and confirm the stack still empties",
        variant_c="record a result per dialog and show that settings apply only after the outer accept",
        mistakes=[
            "Leaving a dialog on the stack when an error path returns early, so the parent stays disabled forever.",
            "Applying settings before the dialog is accepted, which makes Cancel unable to undo anything.",
            "Allowing interaction with the parent while a modal child is open, creating a second source of truth.",
        ],
        q1=(
            "What does a modal stack protect against?",
            "It keeps the flow nested and reversible, so a child closes back into its parent and no blocked window receives input.",
        ),
        homework=(
            "Write `run_dialog_stack(actions)` returning a log and the final stack after processing open, "
            "accept, cancel and blocked actions. Include a nested confirmation, print the log, and comment which "
            "line refuses input while a dialog is modal."
        ),
        patterns=["def ", "append", "print("],
        mapping=(
            "Tkinter's `grab_set()` plus `wait_window()` and Qt's `exec()` implement this stack; the return code "
            "tells the caller whether changes should be applied."
        ),
    ),
    85: dict(
        topic="Scrollable areas",
        idea=(
            "Scrolling is a window onto content larger than the viewport, and almost every scroll bug is "
            "off-by-one arithmetic. Three numbers matter: the content height, the viewport height and the current "
            "offset. The offset is clamped between zero and content minus viewport, otherwise the user can scroll "
            "into blank space. From the offset you derive which rows are visible: the first row is the offset "
            "divided by the row height, and the count is the viewport divided by the row height, capped by what "
            "remains. Wheel events then change the offset by a fixed step, and the scrollbar thumb's size and "
            "position are ratios of those same numbers. Model it this way and you can test the boundaries without "
            "a display: at the top, the first visible row is zero; at the bottom, the last visible row is the "
            "final item; and a huge wheel delta must not push the view past the end. Wheel deltas differ by "
            "platform, so normalise the step before applying it. Today you page through a "
            "forty-row file list in a two-hundred-and-twenty-pixel viewport, printing the visible range for a "
            "small, middle and oversized offset. The clamp is the line that keeps the last page full instead of "
            "half empty."
        ),
        code=(
            """\
def clamp(offset, content_h, viewport_h):
    return max(0, min(offset, content_h - viewport_h))

def visible(offset, total_rows, row_h, viewport_h):
    first = offset // row_h
    shown = min(total_rows - first, viewport_h // row_h)
    return first, first + shown - 1

rows, row_h, viewport = 40, 22, 220
content = rows * row_h
for raw in (0, 495, 5000):
    offset = clamp(raw, content, viewport)
    first, last = visible(offset, rows, row_h, viewport)
    print(f"raw={raw:4} offset={offset:3} rows {first}-{last}")

first, last = visible(clamp(495, content, viewport), rows, row_h, viewport)
assert (first, last) == (22, 31)
assert clamp(5000, content, viewport) == content - viewport
print("last page ends at row 39 with a full viewport")
"""
        ),
        variant_b="change the row height to 30 and show how many rows fit in the same viewport",
        variant_c="reverse one wheel step and clamp it at zero, then print the visible range from the top",
        mistakes=[
            "Letting the offset exceed content minus viewport, so the list scrolls past its last item into blank space.",
            "Computing visible rows without capping by the number of remaining items, producing a phantom last row.",
            "Updating the scrollbar thumb from a different number than the offset actually applied.",
        ],
        q1=(
            "What is the valid range for a scroll offset, and why?",
            "From zero to content height minus viewport height, so the viewport always covers real content and never shows empty space.",
        ),
        homework=(
            "Write `scroll_window(offset, total_rows, row_h, viewport_h)` returning the clamped offset and the "
            "first and last visible row indexes. Print the range for a top, middle and oversized offset, and "
            "comment which line clamps the viewport."
        ),
        patterns=["def ", "min(", "print("],
        mapping=(
            "Tkinter's `Canvas` with `yview`/`scrollregion` and Qt's `QScrollArea` use the same offset clamp and "
            "derive the scrollbar thumb from content and viewport ratios."
        ),
    ),
    86: dict(
        topic="DPI and scaling",
        idea=(
            "DPI scaling is the reason a dialog that looks right on your monitor looks tiny on a laptop or "
            "enormous on a projector. The toolkit reports a scale factor, usually relative to ninety-six dots per "
            "inch, and you are expected to express sizes in logical units while the system maps them to physical "
            "pixels. Mixing the two is the classic error: a font specified in points, a button sized in raw "
            "pixels and an image loaded at its native resolution will disagree about how big everything is. The "
            "safe habit is to pick one unit per concern. Use points or logical pixels for text, scale images "
            "explicitly from their pixel size, and multiply any hand-computed pixel constant by the scale factor "
            "before comparing it to a measured size. Watch the rounding too: scaling a hundred-and-twenty-pixel "
            "button by one and a half gives a clean one hundred and eighty, but scaling a one-pixel border gives "
            "one or two pixels depending on the rule, and asymmetry is immediately visible. Today you convert a "
            "button and a font size at three common scale factors, print the results and assert the expected "
            "physical sizes. The point is not the exact numbers but the discipline of never letting logical and "
            "physical units meet without a conversion."
        ),
        code=(
            """\
def logical_to_physical(value, dpi, baseline=96):
    return (value * dpi + baseline // 2) // baseline

def points_to_pixels(points, dpi, baseline=96):
    return (points * dpi + 36) // 72

button = (120, 32)
font_pt = 11
for dpi in (96, 144, 192):
    w = logical_to_physical(button[0], dpi)
    h = logical_to_physical(button[1], dpi)
    text = points_to_pixels(font_pt, dpi)
    print(f"dpi={dpi:3} button={w}x{h} text={text}px")

assert logical_to_physical(120, 96) == 120
assert logical_to_physical(120, 192) == 240
assert points_to_pixels(11, 96) == 15
print("pixels scale with dpi; points resolve through 72 per inch")
"""
        ),
        variant_b="add a 1-pixel border and show where rounding produces an uneven two-pixel edge",
        variant_c="write the inverse conversion and check that logical sizes round-trip at 144 dpi",
        mistakes=[
            "Setting widths in raw pixels while font sizes are in points, so text and boxes scale differently.",
            "Scaling already-scaled values, which compounds the factor and produces double-size widgets.",
            "Ignoring rounding on thin borders and spacing, where one pixel is immediately visible.",
        ],
        q1=(
            "Why do a pixel-sized button and a point-sized font disagree at high DPI?",
            "Pixels are physical while points are logical units resolved through DPI, so without conversion each scales by a different rule.",
        ),
        homework=(
            "Write `scale_size(width, height, dpi, baseline=96)` returning rounded physical pixels, and test it "
            "at three DPI values. Print the results, assert the ninety-six case is unchanged, and comment which "
            "line performs the rounding."
        ),
        patterns=["def ", "return", "print("],
        mapping=(
            "Qt's device pixel ratio and Tk's `tk scaling` expose this factor; both expect text in points and "
            "images sized with an explicit scale step."
        ),
    ),
    87: dict(
        topic="Debugging a layout",
        idea=(
            "Debugging a layout is mostly refusing to guess. When something is in the wrong place, the useful "
            "question is not why it looks wrong but which rectangle is wrong: the widget's, its container's, or "
            "the space the manager allocated. Print the boxes. A layout audit is a small function that takes "
            "rectangles and reports overlaps, overflow past the parent and zero or negative sizes. Those three "
            "checks catch the majority of real defects, and they run without a display, which means they can live "
            "in a test. Overlap is the easiest to detect: two rectangles intersect when each starts before the "
            "other ends on both axes. Overflow is a comparison against the parent's inner rectangle, not its "
            "outer one, which is a common source of false alarms once padding exists. Zero sizes usually mean a "
            "weight or a natural size was never set, and negative sizes mean a subtraction that assumed a wider "
            "parent. Print the container's inner rectangle too, because most overflow bugs are measured against "
            "the wrong boundary. Today you audit a deliberately broken dialog, print each finding with the offending widget, "
            "then correct the numbers and show a clean report. The lesson to keep is that a printed coordinate is "
            "evidence, and squinting at a screenshot is not."
        ),
        code=(
            """\
WINDOW = (400, 300)

def overlaps(a, b):
    return (a["x"] < b["x"] + b["w"] and b["x"] < a["x"] + a["w"]
            and a["y"] < b["y"] + b["h"] and b["y"] < a["y"] + a["h"])

def audit(boxes, parent):
    issues = []
    for i, box in enumerate(boxes):
        if box["w"] <= 0 or box["h"] <= 0:
            issues.append(f"{box['name']}: non-positive size")
        if box["x"] + box["w"] > parent[0]:
            issues.append(f"{box['name']}: overflows right by {box['x'] + box['w'] - parent[0]}")
        for other in boxes[i + 1:]:
            if overlaps(box, other):
                issues.append(f"{box['name']} overlaps {other['name']}")
    return issues

broken = [
    {"name": "email", "x": 20, "y": 20, "w": 380, "h": 28},
    {"name": "submit", "x": 330, "y": 20, "w": 90, "h": 28},
    {"name": "hint", "x": 20, "y": 54, "w": 0, "h": 18},
]
for issue in audit(broken, WINDOW):
    print("issue:", issue)

fixed = [dict(box) for box in broken]
fixed[0]["w"] = 290
fixed[1]["x"] = 310
fixed[1]["w"] = 70
fixed[2]["w"] = 290
print("issues after fix:", audit(fixed, WINDOW))
assert audit(fixed, WINDOW) == []
print("every reported rectangle is now inside and disjoint")
"""
        ),
        variant_b="add an overlap and an overflow to the fixed layout and confirm the audit names both",
        variant_c="audit against the parent's inner rectangle after subtracting padding, not the outer window",
        mistakes=[
            "Fixing positions by eye in a screenshot instead of printing the rectangles the manager allocated.",
            "Checking overflow against the window instead of the padded inner area, so real overflow is missed.",
            "Treating a zero-width widget as harmless when it usually means a size or weight was never applied.",
        ],
        q1=(
            "Which three rectangle checks catch most layout defects?",
            "Non-positive sizes, overflow past the parent's inner area, and pairwise overlap between siblings.",
        ),
        homework=(
            "Write `audit(boxes, parent)` returning a list of overlap, overflow and size findings. Run it on a "
            "layout with one of each, print the findings, then correct the boxes and print an empty list, "
            "commenting which condition detects overlap."
        ),
        patterns=["def ", "append", "print("],
        mapping=(
            "This is the headless half of `winfo_geometry` debugging in Tkinter or `geometry()` in Qt; printing "
            "resolved rectangles is faster and more reliable than reading pixels off a screen."
        ),
    ),
    88: dict(
        topic="Rebuilding a form from data",
        idea=(
            "Forms are repetitive, so they should be generated. Once you have a list of fields with a label, a "
            "kind, a required flag and maybe a default, the widget tree is a mechanical transformation. This is "
            "the same reason web frameworks render forms from a schema and why a hand-built settings page rots as "
            "soon as a field is added. The generator needs only a few rules: a consistent label column, a field "
            "column, a row height, and a marker for required fields. From those you compute a y coordinate per row "
            "and emit a label and an input for each field. Validation messages then belong to the schema, not "
            "scattered through the layout code. The payoff is that adding a field is a one-line data change and "
            "the layout cannot forget to include it. Two cautions are worth stating. Keep the field order "
            "explicit rather than relying on dictionary order, and keep presentation hints such as width out of "
            "the domain data. Today you rebuild a four-field account form from a list, print the generated widgets "
            "with their positions and assert the count and total height. The same loop in Tkinter creates real "
            "entries; here it creates dictionaries that prove the positions are right."
        ),
        code=(
            """\
FIELDS = [
    ("Email", "entry", True),
    ("Password", "entry", True),
    ("Plan", "choice", False),
    ("Newsletter", "check", False),
]

def build(fields, top=16, row_h=36, label_w=90, field_w=220):
    widgets, y = [], top
    for label, kind, required in fields:
        text = label + (" *" if required else "")
        widgets.append({"kind": "label", "text": text, "x": 16, "y": y, "w": label_w})
        widgets.append({"kind": kind, "name": label.lower(), "x": 16 + label_w,
                        "y": y, "w": field_w})
        y += row_h
    return widgets, y

widgets, bottom = build(FIELDS)
for widget in widgets:
    print(f"{widget['kind']:5} {widget.get('text', widget.get('name')):12} "
          f"x={widget['x']:3} y={widget['y']:3} w={widget['w']}")

print("widgets:", len(widgets), "bottom:", bottom)
assert len(widgets) == 2 * len(FIELDS)
assert bottom == 16 + 4 * 36
print("one data row produces one label and one input")
"""
        ),
        variant_b="add a required Confirm password field at the end and rebuild the layout",
        variant_c="allow a field to span both columns and print the width and position it receives",
        mistakes=[
            "Hand-building each row, so a new field requires edits in three places and the columns drift.",
            "Relying on dictionary iteration order for field order instead of using an explicit list.",
            "Burying width and colour hints in the field data, mixing domain rules with presentation.",
        ],
        q1=(
            "Why should a form be generated from a field list rather than written row by row?",
            "The list is the single source of field order and rules, so adding a field changes one entry and the layout follows mechanically.",
        ),
        homework=(
            "Write `build_form(fields, top, row_h)` returning a list of widget dicts with label and input pairs "
            "and the final bottom coordinate. Add a fifth field, print the rebuilt widgets, and comment which "
            "line advances the row position."
        ),
        patterns=["def ", "for ", "print("],
        mapping=(
            "Qt's `QFormLayout` and Django-style form rendering are schema-driven in the same way; the toolkit "
            "loop simply creates real widgets from the generated rows."
        ),
    ),
    89: dict(
        topic="Review: widgets and layout checklist",
        idea=(
            "A checklist is not bureaucracy; it is the compressed memory of every layout bug you have already "
            "met. The useful list for this phase is short. Does every widget have a parent and a sensible "
            "container? Does each container use one geometry manager rather than mixing pack and grid in the same "
            "parent? Does the layout still add up when the window shrinks? Are all sizes derived from the "
            "container rather than hard-coded? Is spacing consistent, and are padding and margin doing different "
            "jobs? Is there exactly one expanding region, so the interface has an obvious anchor? Does the dialog "
            "stack always unwind, and is the scroll offset clamped? Are menu commands defined once and referenced "
            "everywhere? Are units consistent across text, images and hand-computed pixels? And can the whole "
            "layout be printed and audited in a test? Running such a list over a model is mechanical, which is "
            "the point: each item becomes a predicate, and a failing predicate names the bug. Today you encode "
            "five of these checks as functions, run them against a dashboard layout, print pass or fail for each "
            "and assert the score. Keep the checklist in the repository and extend it whenever a new class of bug "
            "appears."
        ),
        code=(
            """\
def overlaps(a, b):
    return (a["x"] < b["x"] + b["w"] and b["x"] < a["x"] + a["w"]
            and a["y"] < b["y"] + b["h"] and b["y"] < a["y"] + a["h"])

LAYOUT = {
    "window": (800, 600),
    "regions": [
        {"name": "sidebar", "x": 0, "y": 0, "w": 240, "h": 600, "manager": "grid"},
        {"name": "content", "x": 240, "y": 0, "w": 560, "h": 600, "manager": "grid"},
    ],
}

def no_overlaps(layout):
    regions = layout["regions"]
    return not any(overlaps(regions[i], regions[j])
                   for i in range(len(regions))
                   for j in range(i + 1, len(regions)))

CHECKS = [
    ("positive sizes", lambda l: all(r["w"] > 0 and r["h"] > 0 for r in l["regions"])),
    ("inside window", lambda l: all(r["x"] + r["w"] <= l["window"][0]
                                    and r["y"] + r["h"] <= l["window"][1] for r in l["regions"])),
    ("no overlap", no_overlaps),
    ("one manager", lambda l: len({r["manager"] for r in l["regions"]}) == 1),
    ("widths conserved", lambda l: sum(r["w"] for r in l["regions"]) == l["window"][0]),
]

score = 0
for name, check in CHECKS:
    passed = check(LAYOUT)
    score += passed
    print(f"{name:18} {'pass' if passed else 'fail'}")

print(f"score {score}/{len(CHECKS)}")
assert score == len(CHECKS)
print("the checklist is executable: every rule is a predicate")
"""
        ),
        variant_b="add an overlapping footer and confirm exactly one checklist item fails",
        variant_c="add a check that every region height is derived from the window rather than hard-coded",
        mistakes=[
            "Mixing pack and grid under one parent, which the toolkit cannot lay out consistently.",
            "Hard-coding positions that pass one window size and fail the moment it is resized.",
            "Keeping checklist rules in prose only, so the same bug returns without a failing test.",
        ],
        q1=(
            "What makes a layout checklist useful in code rather than as a document?",
            "Each rule becomes a predicate that runs on the layout data, so a regression fails a test instead of relying on someone remembering to look.",
        ),
        homework=(
            "Write `audit_layout(layout)` returning a list of (rule_name, passed) pairs for at least five "
            "checks, plus a score. Run it against a valid dashboard and one broken variant, print both reports, "
            "and comment which loop turns each rule into a pass or fail."
        ),
        patterns=["def ", "for ", "print("],
        mapping=(
            "This is the review lane for real desktop work: the same checks appear in UI tests using "
            "`winfo_geometry` or Qt's geometry API, run before anyone opens the window."
        ),
    ),
})
