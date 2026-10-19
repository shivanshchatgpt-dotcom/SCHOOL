"""Segmentation and detection, days 120-134: masks, components and boxes by hand.

Every example is stdlib-only, offline and deterministic. Masks are tiny nested
lists, every traversal is an explicit loop, and every printed number is rounded
and asserted so the lesson can be checked without OpenCV or an image file.
"""

PHASE = ("Segmentation and Detection", "Turn pixels into counted, boxed and scored objects using only loops over tiny masks.", {
    120: dict(
        topic="Orientation: pixels to objects",
        idea=(
            "Detection begins with a shift in representation: the input is a grid of pixel values, and the output "
            "is a short list of objects with locations. Nothing in between is mysterious if you keep every stage "
            "inspectable. Start with a grayscale image, choose a threshold, and turn it into a binary mask. The "
            "mask is still a grid, but its values mean foreground and background rather than brightness. From the "
            "mask you can count foreground pixels, which gives area, and find the extreme row and column indices, "
            "which give a bounding box. Those two numbers already answer where and how big. The orientation day is "
            "deliberately small: one bright square on a dark background, a handful of lines of output. The point is "
            "to fix the vocabulary and the direction of the pipeline before adding machinery. Notice that no step "
            "needs a library, a file, or a random number. Notice also that each function accepts the previous "
            "stage's output, so a wrong result can be traced to one call. This testability is the habit that "
            "carries through the rest of the phase. Detection systems differ in how they propose and classify "
            "regions, not in the basic contract: an image goes in, and boxes with scores come out. Keep that "
            "contract in mind as the examples grow."
        ),
        code=(
            'IMAGE = [\n'
            '    [10, 10, 10, 10],\n'
            '    [10, 200, 200, 10],\n'
            '    [10, 200, 200, 10],\n'
            '    [10, 10, 10, 10],\n'
            ']\n'
            '\n'
            'def threshold(image, level):\n'
            '    return [[1 if px >= level else 0 for px in row] for row in image]\n'
            '\n'
            'def area(mask):\n'
            '    return sum(sum(row) for row in mask)\n'
            '\n'
            'def bbox(mask):\n'
            '    points = [(r, c) for r, row in enumerate(mask) for c, v in enumerate(row) if v]\n'
            '    rows = [r for r, _ in points]\n'
            '    cols = [c for _, c in points]\n'
            '    return (min(rows), min(cols), max(rows), max(cols))\n'
            '\n'
            'mask = threshold(IMAGE, 100)\n'
            'for row in mask:\n'
            '    print(row)\n'
            'print("foreground:", area(mask))\n'
            'print("bbox:", bbox(mask))\n'
            'print("object count:", 1)\n'
            '\n'
            'assert area(mask) == 4\n'
            'assert bbox(mask) == (1, 1, 2, 2)\n'
            'print("pixels -> mask -> object")'
        ),
        variant_b='change the square to a 1x3 bar and predict the new area and bbox before running',
        variant_c='add a second bright square and explain why the simple bbox no longer describes one object',
        mistakes=[
            "Jumping straight to boxes without printing the intermediate mask.",
            "Reporting objects before checking that the mask has foreground.",
            "Treating the bbox as the object when the blob may be L-shaped.",
        ],
        q1=(
            "What two mask-derived numbers already describe an object's size and location?",
            "The foreground pixel count gives its area, and the minimum and maximum row and column give its bounding box.",
        ),
        homework=(
            "Write `threshold(image, level)` and `bbox(mask)`. Build a 4x4 grayscale grid with one bright rectangle, "
            "print the mask, area and box, and comment which call converts pixels into an object-level summary."
        ),
        patterns=["def ", "print(", "assert"],
        mapping=(
            "This mask-then-measure contract matches `cv2.threshold` followed by `cv2.boundingRect`; open-vocabulary "
            "detectors keep the same interface but replace the threshold with a learned proposal stage."
        ),
    ),
    121: dict(
        topic="Threshold segmentation",
        idea=(
            "Thresholding is the simplest segmenter: pick a value and declare every pixel on one side foreground. "
            "The useful version is a range, not a single cutoff, because objects often occupy a band of intensities "
            "and both very dark and very bright pixels may be irrelevant. A band threshold takes a low and a high "
            "value and keeps pixels inside the interval. Two design choices matter. The interval is inclusive on "
            "both ends, so a pixel exactly equal to a bound is foreground; an off-by-one here changes counts in a "
            "way that is easy to miss. And the bounds should be parameters, because a value tuned for one image "
            "will not transfer to different lighting. Today's example applies a high-pass threshold and a band "
            "threshold to the same small grid, prints both masks, and counts foreground pixels. Comparing the two "
            "counts shows how the choice of rule changes the segmentation without changing the image. This is also "
            "a reminder that a mask is data: you can print it, count it, and assert on it. Later methods such as "
            "adaptive thresholds, Otsu, or learned segmentation replace the rule for choosing the cutoff, but they "
            "still produce a mask, and the inspection habit stays the same. Keep the rule explicit and the counts "
            "visible."
        ),
        code=(
            'GRAY = [\n'
            '    [10, 60, 120, 200],\n'
            '    [30, 90, 150, 240],\n'
            '    [5, 45, 100, 255],\n'
            ']\n'
            '\n'
            'def threshold(image, low, high=255):\n'
            '    return [[1 if low <= px <= high else 0 for px in row] for row in image]\n'
            '\n'
            'bright = threshold(GRAY, 128)\n'
            'band = threshold(GRAY, 50, 150)\n'
            'print("bright:")\n'
            'for row in bright:\n'
            '    print(row)\n'
            'print("band:")\n'
            'for row in band:\n'
            '    print(row)\n'
            'print("bright count:", sum(map(sum, bright)))\n'
            'print("band count:", sum(map(sum, band)))\n'
            '\n'
            'assert sum(map(sum, bright)) == 4\n'
            'assert sum(map(sum, band)) == 5\n'
            'print("threshold direction and range are explicit")'
        ),
        variant_b='make the interval exclusive at the upper bound and recount the band mask',
        variant_c='swap the comparison to select dark pixels and explain why the counts are complements',
        mistakes=[
            "Hard-coding the comparison direction so the mask inverts with lighting.",
            "Forgetting the inclusive bound and losing pixels exactly on the threshold.",
            "Reusing a threshold tuned on one image without checking the new histogram.",
        ],
        q1=(
            "Why use a low and high bound instead of one cutoff?",
            "Objects often occupy a band of intensities, so a range excludes both very dark and very bright pixels that a single cutoff would keep.",
        ),
        homework=(
            "Write `threshold(image, low, high)` returning a 0/1 mask. Run it twice on a 3x4 grid with different "
            "bounds, print both masks and foreground counts, and comment which comparison decides membership."
        ),
        patterns=["def ", "print(", "if "],
        mapping=(
            "`cv2.threshold` covers the single-cutoff case and `cv2.inRange` the band case; both return the same kind "
            "of mask that later connected-components code consumes."
        ),
    ),
    122: dict(
        topic="Connected components at scale",
        idea=(
            "A mask can contain many blobs, and connected components turns it into a list of objects. Two foreground "
            "pixels belong to the same component if a path of foreground pixels connects them. Four-connectivity "
            "allows only up, down, left and right moves; eight-connectivity adds diagonals. The choice is not "
            "cosmetic: a diagonal touch that merges two blobs under eight-connectivity keeps them separate under "
            "four. The implementation is a flood fill. Scan the grid, and when you find an unvisited foreground "
            "pixel, push it on a stack and repeatedly pop, mark and push its in-bounds foreground neighbours. Every "
            "pixel is visited once, so the cost is linear in the number of cells. Without a visited set the "
            "traversal can push the same pixel many times and, on larger masks, appear to hang. The output is a list "
            "of groups; each group's length is its area, and its extreme coordinates give a bounding box. Today's "
            "mask is six by six with four blobs so the labels and areas can be checked by eye. This is segmentation "
            "without a model, and it is the same traversal used by region growing and by object counting before "
            "learned detectors. When a later method returns masks, this step still runs to turn pixels into "
            "countable objects."
        ),
        code=(
            'MASK = [\n'
            '    [1, 1, 0, 0, 0, 1],\n'
            '    [0, 1, 0, 0, 0, 1],\n'
            '    [0, 0, 0, 1, 1, 0],\n'
            '    [0, 0, 0, 1, 0, 0],\n'
            '    [1, 0, 0, 0, 0, 0],\n'
            '    [0, 0, 0, 0, 0, 0],\n'
            ']\n'
            '\n'
            'def components(mask):\n'
            '    height, width = len(mask), len(mask[0])\n'
            '    seen = set()\n'
            '    groups = []\n'
            '    for r in range(height):\n'
            '        for c in range(width):\n'
            '            if not mask[r][c] or (r, c) in seen:\n'
            '                continue\n'
            '            stack = [(r, c)]\n'
            '            group = []\n'
            '            while stack:\n'
            '                cr, cc = stack.pop()\n'
            '                if (cr, cc) in seen or not mask[cr][cc]:\n'
            '                    continue\n'
            '                seen.add((cr, cc))\n'
            '                group.append((cr, cc))\n'
            '                for nr, nc in ((cr-1, cc), (cr+1, cc), (cr, cc-1), (cr, cc+1)):\n'
            '                    if 0 <= nr < height and 0 <= nc < width:\n'
            '                        stack.append((nr, nc))\n'
            '            groups.append(group)\n'
            '    return groups\n'
            '\n'
            'groups = components(MASK)\n'
            'print("components:", len(groups))\n'
            'for i, group in enumerate(groups):\n'
            '    rows = [r for r, _ in group]\n'
            '    cols = [c for _, c in group]\n'
            '    print("label", i + 1, "area", len(group), "bbox", (min(rows), min(cols), max(rows), max(cols)))\n'
            '\n'
            'assert len(groups) == 4\n'
            'assert sorted(len(g) for g in groups) == [1, 2, 3, 3]\n'
            'print("one pass labels every blob")'
        ),
        variant_b='switch to eight-connectivity and check whether any two blobs merge',
        variant_c='add a minimum-area filter and drop components smaller than two pixels',
        mistakes=[
            "Omitting the visited set, so pixels are pushed repeatedly.",
            "Checking bounds after indexing instead of before.",
            "Mixing four- and eight-connectivity between training and evaluation.",
        ],
        q1=(
            "Why does the flood fill need a visited set?",
            "Neighbouring pixels push each other back onto the stack, so without marking visited pixels the traversal can loop indefinitely.",
        ),
        homework=(
            "Write `components(mask)` with an explicit stack and four-connectivity. Run it on a 6x6 mask with four "
            "blobs, print each component's area and bbox, and comment which line marks a pixel as visited."
        ),
        patterns=["def ", "stack", "print("],
        mapping=(
            "`cv2.connectedComponentsWithStats` returns labels plus area and bbox per label; the stack traversal and "
            "connectivity choice here are the same, just slower."
        ),
    ),
    123: dict(
        topic="Region properties",
        idea=(
            "Once a blob is isolated, region properties summarise it with a few numbers. Area is the count of "
            "foreground pixels. The centroid is the mean row and mean column of those pixels; it is not necessarily "
            "a foreground pixel, which matters for concave shapes. The bounding box is the smallest rectangle "
            "aligned with the axes that contains the blob, expressed as minimum and maximum row and column, or as an "
            "origin plus width and height. Width and height follow from the extremes with an inclusive count, so a "
            "blob spanning columns three to five is three wide, not two. Today's example computes all of these from a "
            "single component and prints them with floats rounded. Two habits are worth forming. First, derive "
            "properties from the pixel list rather than from the whole image, so the numbers describe one object. "
            "Second, decide whether your coordinates are inclusive corners or half-open extents, and stay "
            "consistent; mixing the two produces boxes that are one pixel too large or too small. These summaries "
            "are what detection metrics compare, what tracking code associates between frames, and what a "
            "classifier uses as region proposals. The arithmetic is trivial, but the coordinate conventions are "
            "where most bugs live."
        ),
        code=(
            'MASK = [\n'
            '    [0, 0, 0, 0, 0],\n'
            '    [0, 1, 1, 1, 0],\n'
            '    [0, 1, 1, 1, 0],\n'
            '    [0, 1, 1, 0, 0],\n'
            '    [0, 0, 0, 0, 0],\n'
            ']\n'
            '\n'
            'def props(mask):\n'
            '    points = [(r, c) for r, row in enumerate(mask) for c, v in enumerate(row) if v]\n'
            '    count = len(points)\n'
            '    rows = [r for r, _ in points]\n'
            '    cols = [c for _, c in points]\n'
            '    return {\n'
            '        "area": count,\n'
            '        "centroid": (round(sum(rows) / count, 2), round(sum(cols) / count, 2)),\n'
            '        "bbox": (min(rows), min(cols), max(rows), max(cols)),\n'
            '        "width": max(cols) - min(cols) + 1,\n'
            '        "height": max(rows) - min(rows) + 1,\n'
            '    }\n'
            '\n'
            'info = props(MASK)\n'
            'for key in ("area", "centroid", "bbox", "width", "height"):\n'
            '    print(key + ":", info[key])\n'
            '\n'
            'assert info["area"] == 8\n'
            'assert info["centroid"] == (1.88, 1.88)\n'
            'assert info["bbox"] == (1, 1, 3, 3)\n'
            'assert info["width"] == 3 and info["height"] == 3\n'
            'print("region properties summarise one blob")'
        ),
        variant_b='add the topmost and leftmost foreground pixel and compare them with the bbox corners',
        variant_c='compute the centroid for an L shape and explain why it falls outside the foreground',
        mistakes=[
            "Dividing by the image area instead of the component's pixel count.",
            "Using max minus min without the plus one for inclusive widths.",
            "Assuming the centroid is always a foreground pixel.",
        ],
        q1=(
            "What is the centroid of a component?",
            "The mean row and mean column of its foreground pixels, which may lie outside the blob for concave shapes.",
        ),
        homework=(
            "Write `region_props(mask)` returning area, centroid, bbox, width and height for one blob. Run it on a "
            "5x5 mask, print every property rounded, and comment which line counts the pixels."
        ),
        patterns=["def ", "round", "print("],
        mapping=(
            "`cv2.connectedComponentsWithStats` and `skimage.measure.regionprops` expose the same area, centroid and "
            "bbox quantities; the conventions matter when boxes move into detection code."
        ),
    ),
    124: dict(
        topic="Bounding boxes",
        idea=(
            "Bounding boxes are the common currency between segmentation and detection, and there are two "
            "conventions in everyday use. One stores the minimum and maximum row and column, inclusive on both "
            "ends. The other stores an origin, usually x and y, plus a width and a height. The first is natural when "
            "you scan a mask; the second is natural for drawing and for libraries that treat boxes as half-open "
            "rectangles. Converting between them is simple but easy to get wrong at the boundary. With inclusive "
            "corners, width is max minus min plus one; drop the plus one and every box shrinks by a pixel. Today's "
            "example builds a box from four corner points, converts it to x, y, width, height, converts back, and "
            "checks that the round trip returns the original. It also prints the box area. The important lesson is "
            "not the formulas but the discipline of naming the convention in the code and testing the round trip. A "
            "detection pipeline may receive boxes from a model in one convention and compare them with ground truth "
            "in the other, so a silent mismatch inflates or deflates every overlap score. Once the convention is "
            "explicit, intersection, union and cropping all become straightforward arithmetic."
        ),
        code=(
            'POINTS = [(2, 3), (2, 5), (4, 3), (4, 5)]\n'
            '\n'
            'def corners(points):\n'
            '    rows = [r for r, _ in points]\n'
            '    cols = [c for _, c in points]\n'
            '    return (min(rows), min(cols), max(rows), max(cols))\n'
            '\n'
            'def to_xywh(box):\n'
            '    r0, c0, r1, c1 = box\n'
            '    return (c0, r0, c1 - c0 + 1, r1 - r0 + 1)\n'
            '\n'
            'def from_xywh(box):\n'
            '    x, y, w, h = box\n'
            '    return (y, x, y + h - 1, x + w - 1)\n'
            '\n'
            'box = corners(POINTS)\n'
            'print("row/col corners:", box)\n'
            'print("x/y/width/height:", to_xywh(box))\n'
            'print("round trip:", from_xywh(to_xywh(box)))\n'
            'print("box area:", (box[2] - box[0] + 1) * (box[3] - box[1] + 1))\n'
            '\n'
            'assert to_xywh(box) == (3, 2, 3, 3)\n'
            'assert from_xywh((3, 2, 3, 3)) == (2, 3, 4, 5)\n'
            'print("inclusive corners versus width and height")'
        ),
        variant_b='convert a box at the image border and check that the round trip still holds',
        variant_c='write the reverse conversion with half-open corners and compare both conventions',
        mistakes=[
            "Dropping the plus one when converting inclusive corners to width.",
            "Swapping rows and columns between the two conventions.",
            "Mixing x/y and row/column order in the same function.",
        ],
        q1=(
            "How do inclusive row/column corners convert to width and height?",
            "Width is max column minus min column plus one, and height is max row minus min row plus one.",
        ),
        homework=(
            "Write `to_xywh(box)` and `from_xywh(box)` for inclusive row/column boxes. Convert a box twice, print "
            "both forms, assert the round trip, and comment which plus one keeps the widths correct."
        ),
        patterns=["def ", "assert", "print("],
        mapping=(
            "OpenCV rectangles are usually x, y, width, height while masks naturally produce inclusive corners; "
            "converting explicitly prevents one-pixel errors in IoU and cropping."
        ),
    ),
    125: dict(
        topic="Intersection over union",
        idea=(
            "Intersection over union is the standard way to ask whether two boxes describe the same object. Compute "
            "the area of their overlap, divide by the area covered by either box, and you get a number between zero "
            "and one. Zero means disjoint; one means identical. The overlap rectangle is found by taking the larger "
            "of the two left edges and the smaller of the two right edges, and likewise for the top and bottom, "
            "clamping each extent at zero so disjoint boxes do not produce a negative area. Union is the sum of the "
            "two areas minus the overlap, because the overlap is counted twice otherwise. Today's example computes "
            "IoU for identical, partially overlapping, contained and disjoint boxes. The partial case is the "
            "instructive one: a box shifted by one pixel in both directions overlaps in one unit of area but has a "
            "union of seven, giving about 0.14. That number looks small, and that is the point, because IoU punishes "
            "shifts quickly on small objects. Thresholds such as 0.5 are conventions, not laws. IoU is used to match "
            "predictions to ground truth, to decide whether a detection is a true positive, and inside non-maximum "
            "suppression. Implement it once, test the edge cases, and reuse it."
        ),
        code=(
            'def iou(a, b):\n'
            '    ax0, ay0, aw, ah = a\n'
            '    bx0, by0, bw, bh = b\n'
            '    ix = max(0, min(ax0 + aw, bx0 + bw) - max(ax0, bx0))\n'
            '    iy = max(0, min(ay0 + ah, by0 + bh) - max(ay0, by0))\n'
            '    inter = ix * iy\n'
            '    union = aw * ah + bw * bh - inter\n'
            '    return round(inter / union, 2) if union else 0.0\n'
            '\n'
            'A = (0, 0, 2, 2)\n'
            'B = (1, 1, 2, 2)\n'
            'C = (5, 5, 2, 2)\n'
            'print("identical:", iou(A, A))\n'
            'print("shifted:", iou(A, B))\n'
            'print("disjoint:", iou(A, C))\n'
            'print("contained:", iou(A, (0, 0, 1, 1)))\n'
            '\n'
            'assert iou(A, A) == 1.0\n'
            'assert iou(A, B) == 0.14\n'
            'assert iou(A, C) == 0.0\n'
            'assert iou(A, (0, 0, 1, 1)) == 0.25\n'
            'print("shared area over combined area")'
        ),
        variant_b='shift B by two pixels instead of one and predict the new IoU',
        variant_c='use inclusive corner boxes and adapt the intersection arithmetic',
        mistakes=[
            "Computing union as the sum of areas without subtracting the overlap.",
            "Allowing negative intersection extents for disjoint boxes.",
            "Comparing a box in x/y/w/h with one in row/column corners.",
        ],
        q1=(
            "Why subtract the intersection from the sum of areas in the union?",
            "The overlap is included in both box areas, so subtracting it once avoids counting it twice.",
        ),
        homework=(
            "Write `iou(a, b)` for x/y/width/height boxes. Test identical, shifted, contained and disjoint pairs, "
            "print each rounded value, and comment which line clamps the overlap at zero."
        ),
        patterns=["def ", "max(", "print("],
        mapping=(
            "IoU is the matching rule behind true-positive counts, mAP evaluation and greedy NMS; OpenCV and "
            "torchvision both ship versions with the same clamping logic."
        ),
    ),
    126: dict(
        topic="Non-maximum suppression",
        idea=(
            "Non-maximum suppression removes duplicate detections. A detector often fires several boxes around one "
            "object, each with a confidence score. Sorting by score and keeping a box only if it does not overlap an "
            "already kept box above a threshold is the greedy version, and it is what most pipelines use. The "
            "threshold controls the trade-off: too high and duplicates survive, too low and distinct nearby objects "
            "suppress each other. Today's example has four boxes with scores, including one clear duplicate near the "
            "best box and a second duplicate pair elsewhere. It sorts, compares each candidate with the kept list "
            "using IoU, and prints the survivors. Two details matter. The comparison is against kept boxes only, not "
            "against every box, because a suppressed box should not suppress anything. And the result depends on the "
            "score ordering, so ties need a deterministic rule; sorting by score alone is usually enough with stable "
            "input. Keeping the accepted list separate also makes the suppression order explicit. NMS assumes one "
            "object per cluster of overlapping boxes, which is why crowded scenes need softer "
            "variants or class-aware suppression. For now, implement the greedy loop, assert the survivors, and "
            "remember that the threshold is a tuning knob, not a universal constant."
        ),
        code=(
            'BOXES = [\n'
            '    (0, 0, 4, 4, 0.9),\n'
            '    (1, 1, 4, 4, 0.8),\n'
            '    (10, 10, 2, 2, 0.7),\n'
            '    (10, 10, 2, 2, 0.6),\n'
            ']\n'
            '\n'
            'def iou(a, b):\n'
            '    ax, ay, aw, ah = a[:4]\n'
            '    bx, by, bw, bh = b[:4]\n'
            '    ix = max(0, min(ax + aw, bx + bw) - max(ax, bx))\n'
            '    iy = max(0, min(ay + ah, by + bh) - max(ay, by))\n'
            '    inter = ix * iy\n'
            '    union = aw * ah + bw * bh - inter\n'
            '    return inter / union if union else 0.0\n'
            '\n'
            'def nms(boxes, threshold):\n'
            '    kept = []\n'
            '    for box in sorted(boxes, key=lambda b: b[4], reverse=True):\n'
            '        if all(iou(box, other) <= threshold for other in kept):\n'
            '            kept.append(box)\n'
            '    return kept\n'
            '\n'
            'kept = nms(BOXES, 0.3)\n'
            'print("kept:", [(box[:4], box[4]) for box in kept])\n'
            'print("count:", len(kept))\n'
            '\n'
            'assert [box[4] for box in kept] == [0.9, 0.7]\n'
            'assert len(kept) == 2\n'
            'print("greedy suppression removes duplicates")'
        ),
        variant_b='raise the threshold to 0.5 and explain which low-scoring duplicate survives',
        variant_c='make suppression class-aware by comparing only boxes with the same label',
        mistakes=[
            "Comparing against all boxes instead of only the kept ones.",
            "Forgetting to sort by score before the greedy loop.",
            "Using IoU without clamping, so disjoint boxes compare oddly.",
        ],
        q1=(
            "Why compare each candidate only with the boxes already kept?",
            "A suppressed box is no longer an accepted detection, so it must not be allowed to suppress later candidates.",
        ),
        homework=(
            "Write `nms(boxes, threshold)` using IoU and a score sort. Run it on four boxes with two duplicates, "
            "print the survivors and scores, and comment which line skips an overlapping candidate."
        ),
        patterns=["def ", "sorted", "print("],
        mapping=(
            "OpenCV's `dnn.NMSBoxes` and torchvision's `nms` implement the same greedy rule; class-aware suppression "
            "is why instance detectors run NMS per class."
        ),
    ),
    127: dict(
        topic="Sliding window detection",
        idea=(
            "Sliding window detection applies a fixed-size classifier or score function at every position of an "
            "image. The window moves one step at a time, and at each position you extract the patch, score it, and "
            "keep the score. The output is a score map: one value per top-left position. The best position is the "
            "maximum, and thresholding the map gives candidate detections. Today's example slides a two-by-two "
            "window over a six-by-six mask and sums the foreground inside it. That score is a stand-in for a "
            "classifier: it prefers windows that cover object pixels. The example prints the number of windows, the "
            "best window and its score. Two practical facts follow from the arithmetic. The number of positions is "
            "height minus window height plus one, times the analogous width, so windows shrink the usable search "
            "area at the borders. And a window score is not a probability unless the scorer is calibrated. Real "
            "detectors use image pyramids or region proposals to avoid scoring every position at every scale, but "
            "the idea is the same. Sliding windows also explain why detection is expensive: cost grows with "
            "positions times window work. Keep the window small in the example and verify the count before trusting "
            "the best location."
        ),
        code=(
            'MASK = [\n'
            '    [0, 0, 0, 0, 0, 0],\n'
            '    [0, 1, 1, 0, 0, 0],\n'
            '    [0, 1, 1, 0, 1, 0],\n'
            '    [0, 0, 0, 0, 1, 0],\n'
            '    [0, 0, 0, 0, 0, 0],\n'
            '    [0, 0, 0, 0, 0, 0],\n'
            ']\n'
            '\n'
            'def window_sum(mask, top, left, size):\n'
            '    total = 0\n'
            '    for r in range(top, top + size):\n'
            '        for c in range(left, left + size):\n'
            '            total += mask[r][c]\n'
            '    return total\n'
            '\n'
            'size = 2\n'
            'scores = []\n'
            'for top in range(len(MASK) - size + 1):\n'
            '    for left in range(len(MASK[0]) - size + 1):\n'
            '        scores.append((window_sum(MASK, top, left, size), top, left))\n'
            '\n'
            'best = max(scores)\n'
            'print("windows:", len(scores))\n'
            'print("best score and origin:", best)\n'
            'print("unique scores:", sorted({score for score, _, _ in scores}))\n'
            '\n'
            'assert len(scores) == 25\n'
            'assert best == (4, 1, 1)\n'
            'print("a sliding window turns detection into repeated scoring")'
        ),
        variant_b='change the window to 3x3 and recompute the number of positions and the best score',
        variant_c='add a score threshold and print only the window origins that pass',
        mistakes=[
            "Iterating to the image edge without subtracting the window size.",
            "Treating the raw window score as a calibrated probability.",
            "Reusing a window size that does not match the object scale.",
        ],
        q1=(
            "How many window positions are there for a 6x6 image and a 2x2 window?",
            "Five positions per axis, so 25 in total, because each axis has size minus window size plus one starts.",
        ),
        homework=(
            "Write `slide(mask, size)` that scores every window by its foreground sum. Run it on a 6x6 mask, print "
            "the number of windows and the best origin, and comment which subtraction keeps the loop in bounds."
        ),
        patterns=["def ", "for ", "print("],
        mapping=(
            "Classical detectors such as Viola-Jones scan windows over an image pyramid; modern region proposals "
            "replace exhaustive scanning but still produce scored boxes."
        ),
    ),
    128: dict(
        topic="Detection metrics",
        idea=(
            "Detection metrics reduce a set of predictions and a set of ground-truth objects to numbers you can "
            "compare. Match each prediction to a ground-truth object, usually by IoU, and count true positives, "
            "false positives and false negatives. Precision is true positives divided by all predictions; it "
            "answers how many of your detections were right. Recall is true positives divided by all ground-truth "
            "objects; it answers how many real objects you found. F1 is their harmonic mean, which punishes a system "
            "that is good at only one. Today's example uses sets of integer ids instead of boxes so the matching is "
            "trivial and the arithmetic is visible. It prints the three counts and the three ratios, rounded to two "
            "places. The lesson is to compute counts first and ratios second, because ratios hide the sample size. A "
            "precision of one from one prediction means little; the counts make that visible. Also notice that "
            "precision and recall trade off: lowering a confidence threshold usually raises recall and lowers "
            "precision. F1 compresses that curve into one number and therefore hides the operating point, so report "
            "the counts alongside it. In detection practice, average precision summarises the curve over thresholds "
            "and is the metric you will meet next."
        ),
        code=(
            'TRUTH = {1, 2, 3, 4, 6}\n'
            'PRED = {1, 2, 3, 5}\n'
            '\n'
            'def metrics(truth, pred):\n'
            '    tp = len(truth & pred)\n'
            '    fp = len(pred - truth)\n'
            '    fn = len(truth - pred)\n'
            '    precision = tp / (tp + fp) if tp + fp else 0.0\n'
            '    recall = tp / (tp + fn) if tp + fn else 0.0\n'
            '    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0\n'
            '    return tp, fp, fn, round(precision, 2), round(recall, 2), round(f1, 2)\n'
            '\n'
            'tp, fp, fn, precision, recall, f1 = metrics(TRUTH, PRED)\n'
            'print("tp fp fn:", tp, fp, fn)\n'
            'print("precision:", precision)\n'
            'print("recall:", recall)\n'
            'print("f1:", f1)\n'
            '\n'
            'assert (tp, fp, fn) == (3, 1, 2)\n'
            'assert precision == 0.75\n'
            'assert recall == 0.6\n'
            'assert f1 == 0.67\n'
            'print("counts first, ratios second")'
        ),
        variant_b='add a second predicted id and recompute precision and recall',
        variant_c='empty the prediction set and check how the zero-division branches behave',
        mistakes=[
            "Reporting precision without the true and false positive counts.",
            "Calling every unmatched prediction a false negative.",
            "Using F1 alone when the precision-recall operating point matters.",
        ],
        q1=(
            "What do precision and recall each divide by?",
            "Precision divides true positives by all predictions; recall divides true positives by all ground-truth objects.",
        ),
        homework=(
            "Write `metrics(truth, pred)` returning tp, fp, fn, precision, recall and f1. Run it on two id sets, "
            "print the counts and rounded ratios, and comment which denominator differs between precision and recall."
        ),
        patterns=["def ", "round", "print("],
        mapping=(
            "Detection evaluation turns IoU matches into the same counts and then sweeps a score threshold to build "
            "the precision-recall curve behind average precision."
        ),
    ),
    129: dict(
        topic="Semantic versus instance",
        idea=(
            "Semantic segmentation labels every pixel with a class: road, person, sky. Instance segmentation goes "
            "further and separates individual objects of the same class: person one, person two. The distinction is "
            "easy to state and easy to blur in code, because both outputs look like label images. The difference is "
            "what the labels mean. In a semantic label map, two adjacent people share the class value and are "
            "indistinguishable. In an instance map, each person gets a unique id even though they share the class. "
            "Today's example starts with a small class map and counts the classes present. It then builds one binary "
            "mask per class and runs connected components on each mask, which recovers instances within that class. "
            "The printed counts show that class one has two separate objects while class two has one. This two-level "
            "structure, class plus component, is the simplest instance segmenter and a useful baseline. It fails "
            "when objects of one class touch, because connectivity merges them, which is exactly why the phase later "
            "covers splitting and watershed. Keep the class map and the instance map separate in your head: one "
            "answers what is present, the other answers which object it is, and neither replaces the other."
        ),
        code=(
            'CLASSES = [\n'
            '    [0, 1, 1, 0, 2],\n'
            '    [0, 1, 0, 0, 2],\n'
            '    [0, 0, 0, 1, 1],\n'
            '    [0, 0, 0, 1, 1],\n'
            '    [0, 0, 0, 0, 0],\n'
            ']\n'
            '\n'
            'def components(mask):\n'
            '    height, width = len(mask), len(mask[0])\n'
            '    seen, groups = set(), []\n'
            '    for r in range(height):\n'
            '        for c in range(width):\n'
            '            if not mask[r][c] or (r, c) in seen:\n'
            '                continue\n'
            '            stack, group = [(r, c)], []\n'
            '            while stack:\n'
            '                cr, cc = stack.pop()\n'
            '                if (cr, cc) in seen or not mask[cr][cc]:\n'
            '                    continue\n'
            '                seen.add((cr, cc))\n'
            '                group.append((cr, cc))\n'
            '                for nr, nc in ((cr-1, cc), (cr+1, cc), (cr, cc-1), (cr, cc+1)):\n'
            '                    if 0 <= nr < height and 0 <= nc < width:\n'
            '                        stack.append((nr, nc))\n'
            '            groups.append(group)\n'
            '    return groups\n'
            '\n'
            'classes = sorted({value for row in CLASSES for value in row if value})\n'
            '\n'
            'print("semantic classes:", classes)\n'
            'for label in classes:\n'
            '    mask = [[1 if value == label else 0 for value in row] for row in CLASSES]\n'
            '    groups = components(mask)\n'
            '    print("class", label, "instances:", len(groups), "areas:", [len(g) for g in groups])\n'
            '\n'
            'assert classes == [1, 2]\n'
            'assert len(components([[1 if v == 1 else 0 for v in row] for row in CLASSES])) == 2\n'
            'print("semantic labels classes; instances label objects")'
        ),
        variant_b='make the two class-one blobs touch diagonally and recount under four-connectivity',
        variant_c='add a third class and check that the per-class loop still recovers each instance count',
        mistakes=[
            "Calling a class map an instance map because the values differ.",
            "Running components once across all classes and merging different objects.",
            "Assuming four-connectivity when the data was labelled with eight.",
        ],
        q1=(
            "What does an instance map add over a semantic map?",
            "It gives each object a distinct id, so two people of the same class remain separate instead of sharing one class label.",
        ),
        homework=(
            "Write `instances(class_map, label)` that builds a binary mask for one class and returns its components. "
            "Run it for every class, print instance counts and areas, and comment which line recovers objects."
        ),
        patterns=["def ", "components", "print("],
        mapping=(
            "Mask R-CNN and torchvision's Mask R-CNN return semantic class ids plus per-instance masks; connected "
            "components on a class mask is the hand-written baseline for the same output."
        ),
    ),
    130: dict(
        topic="Masks and contours",
        idea=(
            "Masks describe regions; contours describe their boundaries. A contour is an ordered sequence of "
            "boundary points, and it is what you draw, simplify, or use to measure perimeter and shape. The simplest "
            "boundary extraction marks every foreground pixel that has at least one background or out-of-bounds "
            "four-neighbour. That gives the set of boundary pixels, not necessarily a single ordered loop; a real "
            "contour tracer walks the edge and returns points in order. Today's example uses the set version on a "
            "three-by-three square. Eight pixels are boundary and the centre is interior. The printed boundary row "
            "shows the expected run of three. This is enough to see the relationship between area, perimeter and "
            "shape, and to understand why a mask and its contour are not the same object. Two cautions. A "
            "one-pixel-wide object has no interior, so every pixel is boundary. And diagonal connectivity changes "
            "which pixels count as boundary, just as it changes components. Contours are convenient for "
            "visualisation and for polygon approximations, but most metrics operate directly on masks. Boundary "
            "pixels are also where raster masks meet vector polygons, and that conversion loses detail at corners. "
            "The set is cheap to compute, but it does not preserve order. Keep both representations and know which "
            "one your next function expects."
        ),
        code=(
            'MASK = [\n'
            '    [0, 0, 0, 0, 0, 0],\n'
            '    [0, 1, 1, 1, 0, 0],\n'
            '    [0, 1, 1, 1, 0, 0],\n'
            '    [0, 1, 1, 1, 0, 0],\n'
            '    [0, 0, 0, 0, 0, 0],\n'
            '    [0, 0, 0, 0, 0, 0],\n'
            ']\n'
            '\n'
            'def boundary(mask):\n'
            '    height, width = len(mask), len(mask[0])\n'
            '    edge = []\n'
            '    for r in range(height):\n'
            '        for c in range(width):\n'
            '            if not mask[r][c]:\n'
            '                continue\n'
            '            for nr, nc in ((r-1, c), (r+1, c), (r, c-1), (r, c+1)):\n'
            '                if not (0 <= nr < height and 0 <= nc < width) or not mask[nr][nc]:\n'
            '                    edge.append((r, c))\n'
            '                    break\n'
            '    return edge\n'
            '\n'
            'edge = boundary(MASK)\n'
            'print("boundary pixels:", len(edge))\n'
            'print("row 1 boundary:", [p for p in edge if p[0] == 1])\n'
            'print("mask area:", sum(map(sum, MASK)))\n'
            'print("interior pixels:", sum(map(sum, MASK)) - len(edge))\n'
            '\n'
            'assert len(edge) == 8\n'
            'assert (2, 2) not in edge\n'
            'print("contours are foreground pixels touching background")'
        ),
        variant_b='use a one-pixel-wide line and confirm that every foreground pixel is boundary',
        variant_c='return boundary coordinates grouped by side instead of one flat list',
        mistakes=[
            "Treating the boundary set as an ordered contour suitable for drawing.",
            "Forgetting out-of-bounds neighbours when the object touches the border.",
            "Comparing contour length directly with area as if both measured the same thing.",
        ],
        q1=(
            "Why is the centre of a solid 3x3 blob not a boundary pixel?",
            "All four of its four-neighbours are foreground, so it never touches background or the image border.",
        ),
        homework=(
            "Write `boundary(mask)` returning foreground pixels with a background four-neighbour. Run it on a 3x3 "
            "block, print the count and boundary rows, and comment which condition detects an edge pixel."
        ),
        patterns=["def ", "if ", "print("],
        mapping=(
            "`cv2.findContours` returns ordered boundary polylines from a mask, while the set-based boundary here is "
            "the direct check behind contour tracing and mask editing."
        ),
    ),
    131: dict(
        topic="Watershed concept",
        idea=(
            "Watershed segmentation treats a grayscale image as a terrain, with dark pixels as valleys and bright "
            "pixels as ridges. If you flood the terrain from its lowest points, basins grow and meet at ridge lines; "
            "those lines become the boundaries between regions. The key input is the set of seeds, one per basin, "
            "usually local minima of the image or of a gradient. Good seeds give good regions, and this is where "
            "watershed is fragile: too many minima produce oversegmentation, too few merge objects. Today's example "
            "builds a tiny height grid with two minima separated by a ridge. It finds the seeds, then assigns each "
            "cell to the nearest seed in grid distance. Cells equidistant from two seeds are marked as boundary. The "
            "printed label map shows two basins and a clean ridge column. The ridge itself is left unlabelled rather "
            "than assigned arbitrarily. This is a simplification of true flooding, "
            "which respects the terrain height along the path, but it captures the essential idea of seeds plus "
            "catchment regions. In practice, watershed usually runs on a distance transform or an edge map, and "
            "markers are supplied explicitly to control the result. When objects touch, that marker control is what "
            "makes watershed useful."
        ),
        code=(
            'HEIGHTS = [\n'
            '    [3, 3, 5, 3, 3],\n'
            '    [3, 1, 5, 1, 3],\n'
            '    [3, 3, 5, 3, 3],\n'
            ']\n'
            '\n'
            'def minima(grid):\n'
            '    height, width = len(grid), len(grid[0])\n'
            '    seeds = []\n'
            '    for r in range(height):\n'
            '        for c in range(width):\n'
            '            neighbours = []\n'
            '            for nr, nc in ((r-1, c), (r+1, c), (r, c-1), (r, c+1)):\n'
            '                if 0 <= nr < height and 0 <= nc < width:\n'
            '                    neighbours.append(grid[nr][nc])\n'
            '            if all(grid[r][c] < value for value in neighbours):\n'
            '                seeds.append((r, c))\n'
            '    return seeds\n'
            '\n'
            'def watershed(grid, seeds):\n'
            '    labels = []\n'
            '    for r in range(len(grid)):\n'
            '        row = []\n'
            '        for c in range(len(grid[0])):\n'
            '            distances = [abs(r - sr) + abs(c - sc) for sr, sc in seeds]\n'
            '            best = min(distances)\n'
            '            owners = [i for i, d in enumerate(distances) if d == best]\n'
            '            row.append(owners[0] + 1 if len(owners) == 1 else 0)\n'
            '        labels.append(row)\n'
            '    return labels\n'
            '\n'
            'seeds = minima(HEIGHTS)\n'
            'print("seeds:", seeds)\n'
            'for row in watershed(HEIGHTS, seeds):\n'
            '    print(row)\n'
            '\n'
            'assert seeds == [(1, 1), (1, 3)]\n'
            'assert watershed(HEIGHTS, seeds)[0] == [1, 1, 0, 2, 2]\n'
            'print("seeds flood outward until basins meet at a ridge")'
        ),
        variant_b='move the seeds one column closer and watch the ridge shift',
        variant_c='add a third minimum and check how many basins the label map now contains',
        mistakes=[
            "Choosing seeds by threshold rather than by actual minima.",
            "Allowing every plateau pixel to become a separate seed.",
            "Treating the watershed line as foreground belonging to one object.",
        ],
        q1=(
            "What decides the regions in a watershed segmentation?",
            "The seeds and the terrain: basins grow from the seeds and meet at ridges, so seed choice controls the result.",
        ),
        homework=(
            "Write `seeds(grid)` for strict local minima and `flood(grid, seeds)` assigning cells to the nearest seed. "
            "Run both on a 3x5 height grid, print the label map, and comment which case marks a ridge pixel."
        ),
        patterns=["def ", "min(", "print("],
        mapping=(
            "`cv2.watershed` takes explicit marker labels and a gradient image; the marker psychology is identical, "
            "which is why seed placement is the hard part."
        ),
    ),
    132: dict(
        topic="Handling touching objects",
        idea=(
            "Touching objects defeat plain connected components: the bridge between two blobs makes them one "
            "component. A practical fix is to find a narrow place and cut it. One cheap signal is the column "
            "projection, the count of foreground pixels in each column. Two blobs joined by a thin neck produce a "
            "valley at the neck, because the bridge contributes fewer pixels than the bodies on either side. Today's "
            "example builds two two-by-two blocks joined by a single-pixel bridge, computes column sums, finds the "
            "interior column with the smallest sum, and removes it. It then counts components before and after, "
            "printing one and two. The method is deliberately simple and has a clear failure mode: if the objects "
            "overlap broadly, or if the projection has no clear valley, cutting a column will slice an object rather "
            "than separate it. More robust approaches use the distance transform, watershed markers, or learned "
            "instance segmentation. Still, the projection trick is a good first diagnostic, and it teaches the "
            "general pattern: measure a one-dimensional summary, find a minimum, and test whether the cut changes "
            "the object count. A cut is a hypothesis, not a proof. Always compare counts before and after, and never "
            "assume the cut is correct without checking."
        ),
        code=(
            'MASK = [\n'
            '    [0, 0, 0, 0, 0, 0],\n'
            '    [0, 1, 1, 1, 1, 0],\n'
            '    [0, 1, 1, 0, 1, 1],\n'
            '    [0, 0, 0, 0, 0, 0],\n'
            '    [0, 0, 0, 0, 0, 0],\n'
            '    [0, 0, 0, 0, 0, 0],\n'
            ']\n'
            '\n'
            'def components(mask):\n'
            '    height, width = len(mask), len(mask[0])\n'
            '    seen, groups = set(), []\n'
            '    for r in range(height):\n'
            '        for c in range(width):\n'
            '            if not mask[r][c] or (r, c) in seen:\n'
            '                continue\n'
            '            stack, group = [(r, c)], []\n'
            '            while stack:\n'
            '                cr, cc = stack.pop()\n'
            '                if (cr, cc) in seen or not mask[cr][cc]:\n'
            '                    continue\n'
            '                seen.add((cr, cc))\n'
            '                group.append((cr, cc))\n'
            '                for nr, nc in ((cr-1, cc), (cr+1, cc), (cr, cc-1), (cr, cc+1)):\n'
            '                    if 0 <= nr < height and 0 <= nc < width:\n'
            '                        stack.append((nr, nc))\n'
            '            groups.append(group)\n'
            '    return groups\n'
            '\n'
            'def column_sums(mask):\n'
            '    return [sum(row[c] for row in mask) for c in range(len(mask[0]))]\n'
            '\n'
            'sums = column_sums(MASK)\n'
            'cut = min(range(1, len(sums) - 1), key=lambda c: (sums[c], c))\n'
            'split = [[0 if c == cut else value for c, value in enumerate(row)] for row in MASK]\n'
            'print("column sums:", sums)\n'
            'print("cut column:", cut)\n'
            'print("objects before:", len(components(MASK)))\n'
            'print("objects after:", len(components(split)))\n'
            'for row in split:\n'
            '    print(row)\n'
            '\n'
            'assert len(components(MASK)) == 1\n'
            'assert len(components(split)) == 2\n'
            'assert cut == 3\n'
            'print("a narrow projection valley can separate touching blobs")'
        ),
        variant_b='use a row projection instead and explain when rows are the better cut direction',
        variant_c='cut two columns around the minimum and check the object count stays two',
        mistakes=[
            "Cutting at the global minimum when it lies on the border.",
            "Assuming a valley always separates objects rather than slicing one.",
            "Comparing counts without verifying the split visually or by area.",
        ],
        q1=(
            "What signal does the column projection give for two blobs joined by a thin bridge?",
            "The bridge column has a lower foreground count than the surrounding body columns, so it shows up as a valley.",
        ),
        homework=(
            "Write `split_touching(mask)` that uses column sums to find an interior minimum and remove that column. "
            "Run it on two blocks joined by a bridge, print the before and after component counts, and comment which "
            "line chooses the cut."
        ),
        patterns=["def ", "min(", "print("],
        mapping=(
            "OpenCV watershed is the usual production answer for touching objects, while distance transforms supply "
            "the markers; the projection valley is the quick diagnostic before reaching for either."
        ),
    ),
    133: dict(
        topic="Evaluating a segmenter",
        idea=(
            "Evaluating a segmenter means comparing predicted masks with ground-truth masks, and there are several "
            "metrics because they answer different questions. Pixel accuracy is the fraction of all pixels "
            "classified correctly. It looks reassuring on images where background dominates, which is why it is "
            "often misleading. Intersection over union treats the foreground as a set, dividing the overlap of "
            "prediction and truth by their union. Dice is similar but weights the overlap more heavily; it is twice "
            "the intersection divided by the sum of foreground areas. Precision and recall describe the same counts "
            "from the prediction and truth sides. Today's example runs all of these on a four-by-four pair of masks "
            "and prints the counts and ratios. The prediction has no false positives but misses two pixels, so "
            "precision is one while recall and IoU are about 0.71. That gap is the lesson: a conservative segmenter "
            "can look perfect on precision and still miss objects. Report counts, at least one overlap metric, and "
            "the operating point. For detection, the same counts feed precision-recall curves and average "
            "precision. Always inspect the masks alongside the numbers, because one bad region can dominate a "
            "ratio. The arithmetic is small; the interpretation is what makes the evaluation useful."
        ),
        code=(
            'TRUTH = [\n'
            '    [0, 0, 1, 1],\n'
            '    [0, 1, 1, 0],\n'
            '    [0, 1, 1, 0],\n'
            '    [0, 0, 1, 0],\n'
            ']\n'
            'PRED = [\n'
            '    [0, 0, 1, 0],\n'
            '    [0, 1, 1, 0],\n'
            '    [0, 1, 0, 0],\n'
            '    [0, 0, 1, 0],\n'
            ']\n'
            '\n'
            'def evaluate(truth, pred):\n'
            '    tp = sum(1 for tr, pr in zip(truth, pred) for t, p in zip(tr, pr) if t and p)\n'
            '    fp = sum(1 for tr, pr in zip(truth, pred) for t, p in zip(tr, pr) if p and not t)\n'
            '    fn = sum(1 for tr, pr in zip(truth, pred) for t, p in zip(tr, pr) if t and not p)\n'
            '    tn = sum(1 for tr, pr in zip(truth, pred) for t, p in zip(tr, pr) if not t and not p)\n'
            '    precision = tp / (tp + fp) if tp + fp else 0.0\n'
            '    recall = tp / (tp + fn) if tp + fn else 0.0\n'
            '    iou = tp / (tp + fp + fn) if tp + fp + fn else 0.0\n'
            '    dice = 2 * tp / (2 * tp + fp + fn) if 2 * tp + fp + fn else 0.0\n'
            '    accuracy = (tp + tn) / (tp + tn + fp + fn)\n'
            '    return (tp, fp, fn, tn, round(precision, 2), round(recall, 2),\n'
            '            round(iou, 2), round(dice, 2), round(accuracy, 2))\n'
            '\n'
            'tp, fp, fn, tn, precision, recall, iou, dice, accuracy = evaluate(TRUTH, PRED)\n'
            'print("tp fp fn tn:", tp, fp, fn, tn)\n'
            'print("precision:", precision, "recall:", recall)\n'
            'print("iou:", iou, "dice:", dice)\n'
            'print("pixel accuracy:", accuracy)\n'
            '\n'
            'assert (tp, fp, fn, tn) == (5, 0, 2, 9)\n'
            'assert (precision, recall, iou, dice, accuracy) == (1.0, 0.71, 0.71, 0.83, 0.88)\n'
            'print("overlap metrics disagree with pixel accuracy")'
        ),
        variant_b='add one false positive and check which metrics drop and which stay high',
        variant_c='evaluate a prediction that marks every pixel foreground and explain the accuracy trap',
        mistakes=[
            "Reporting pixel accuracy when background dominates the image.",
            "Confusing Dice with IoU and using them interchangeably.",
            "Computing ratios without reporting the underlying counts.",
        ],
        q1=(
            "Why can pixel accuracy mislead on segmentation tasks?",
            "Background usually dominates, so predicting all background can score high accuracy while finding no objects.",
        ),
        homework=(
            "Write `evaluate_masks(truth, pred)` returning tp, fp, fn, tn, precision, recall, IoU and Dice. Run it "
            "on two 4x4 masks, print the counts and ratios, and comment which denominator IoU uses."
        ),
        patterns=["def ", "round", "print("],
        mapping=(
            "The same overlap counts underpin mask mAP in instance segmentation and pixel IoU in semantic "
            "segmentation benchmarks such as Cityscapes."
        ),
    ),
    134: dict(
        topic="Review: segmentation and detection checklist",
        idea=(
            "The review day is a checklist, not a new algorithm. Given a mask, can you confirm that it is non-empty, "
            "count its components, compute each bounding box, and compare a box with a reference using IoU? Each "
            "check is a small assertion, and together they cover the phase's core operations. Today's example runs "
            "exactly that sequence on a six-by-six mask with two objects of different sizes. It prints PASS or FAIL "
            "for each check and asserts that all pass. The value of the checklist is diagnostic order: if the mask "
            "check fails, later checks are meaningless; if the component count is wrong, the boxes will be wrong "
            "too. Each stage returns a value that the next stage consumes, so order matters. Running checks in "
            "dependency order localises the failure. This is also the habit to carry into "
            "larger pipelines, where a silent empty mask can propagate through metrics and produce a plausible-"
            "looking zero. Before leaving the phase, be able to explain the difference between a mask, a component, "
            "a box and a contour, and when each representation is appropriate. Detection adds scoring and "
            "suppression, but it still rests on these primitives. A short checklist run on every new dataset catches "
            "most integration bugs early."
        ),
        code=(
            'MASK = [\n'
            '    [0, 0, 0, 0, 0, 0],\n'
            '    [0, 1, 1, 0, 1, 0],\n'
            '    [0, 1, 1, 0, 1, 0],\n'
            '    [0, 0, 0, 0, 0, 0],\n'
            '    [0, 0, 0, 0, 0, 0],\n'
            '    [0, 0, 0, 0, 0, 0],\n'
            ']\n'
            '\n'
            'def components(mask):\n'
            '    height, width = len(mask), len(mask[0])\n'
            '    seen, groups = set(), []\n'
            '    for r in range(height):\n'
            '        for c in range(width):\n'
            '            if not mask[r][c] or (r, c) in seen:\n'
            '                continue\n'
            '            stack, group = [(r, c)], []\n'
            '            while stack:\n'
            '                cr, cc = stack.pop()\n'
            '                if (cr, cc) in seen or not mask[cr][cc]:\n'
            '                    continue\n'
            '                seen.add((cr, cc))\n'
            '                group.append((cr, cc))\n'
            '                for nr, nc in ((cr-1, cc), (cr+1, cc), (cr, cc-1), (cr, cc+1)):\n'
            '                    if 0 <= nr < height and 0 <= nc < width:\n'
            '                        stack.append((nr, nc))\n'
            '            groups.append(group)\n'
            '    return groups\n'
            '\n'
            'def bbox(group):\n'
            '    rows = [r for r, _ in group]\n'
            '    cols = [c for _, c in group]\n'
            '    return (min(rows), min(cols), max(rows), max(cols))\n'
            '\n'
            'def iou(a, b):\n'
            '    ar0, ac0, ar1, ac1 = a\n'
            '    br0, bc0, br1, bc1 = b\n'
            '    ih = max(0, min(ar1, br1) - max(ar0, br0) + 1)\n'
            '    iw = max(0, min(ac1, bc1) - max(ac0, bc0) + 1)\n'
            '    inter = ih * iw\n'
            '    area_a = (ar1 - ar0 + 1) * (ac1 - ac0 + 1)\n'
            '    area_b = (br1 - br0 + 1) * (bc1 - bc0 + 1)\n'
            '    return round(inter / (area_a + area_b - inter), 2)\n'
            '\n'
            'groups = components(MASK)\n'
            'boxes = [bbox(group) for group in groups]\n'
            'reference = (1, 1, 2, 2)\n'
            'checks = {\n'
            '    "mask non-empty": sum(map(sum, MASK)) > 0,\n'
            '    "two objects": len(groups) == 2,\n'
            '    "areas correct": sorted(len(g) for g in groups) == [2, 4],\n'
            '    "iou with reference": iou(boxes[0], reference) == 1.0,\n'
            '}\n'
            'for name, passed in checks.items():\n'
            '    print(name + ":", "PASS" if passed else "FAIL")\n'
            '\n'
            'assert all(checks.values())\n'
            'print("checklist passed")'
        ),
        variant_b='add a check for a minimum object area and watch one blob fail it',
        variant_c='compare two predicted boxes with the reference and choose the higher IoU',
        mistakes=[
            "Running expensive checks before confirming the mask is non-empty.",
            "Using a bbox comparison without agreeing on coordinate conventions.",
            "Treating a passing checklist as proof that the segmenter generalises.",
        ],
        q1=(
            "Why run the checklist in dependency order?",
            "An empty or wrong mask makes later box and metric checks meaningless, so validating earlier stages first localises the failure.",
        ),
        homework=(
            "Write `check_mask(mask, reference)` that verifies foreground, counts components, boxes each one and "
            "compares the first box with a reference using IoU. Print PASS or FAIL per check and comment the order."
        ),
        patterns=["def ", "assert", "print("],
        mapping=(
            "The checklist maps onto a production smoke test: assert the mask is non-empty, compare component "
            "counts, and verify IoU against a known reference before trusting detection metrics."
        ),
    ),
})
