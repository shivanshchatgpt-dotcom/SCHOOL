"""Features and matching, days 105-119: keypoints, descriptors and matching by hand.

Every example is stdlib-only, offline and deterministic: an image is a nested
list of pixel values and every operation is a loop over that list. Corner
scores, patch descriptors, Euclidean distance, nearest-neighbour matching, the
ratio test and template matching are implemented directly, so a matching
pipeline can be run and asserted on without OpenCV, a camera or a file on disk.
"""

PHASE = (
    "Features and Matching",
    "Find distinctive image points, describe their neighbourhoods and match them across views without any image library.",
    {
        105: dict(
            topic="Orientation: interesting points",
            idea=(
                "Feature work starts from a change of viewpoint. A pixel is just a number, but a small patch around "
                "the right place stays recognisable as the camera moves, turns or zooms. Those places are called "
                "interesting points, or keypoints, and this whole phase is about finding them, describing them and "
                "pairing them across two images. An interesting point is one whose neighbourhood is distinctive: if "
                "you slide a small window in any direction the contents change. A flat region is boring because "
                "every shift looks the same; a straight edge is only locally unique along its own direction; a "
                "corner or a blob is distinctive in several directions at once. Today you do not measure corners "
                "yet. You only look at local contrast, the difference between the brightest and darkest value in a "
                "small window, and treat a high value as a sign that something is happening there. That single "
                "number already separates smooth background from an object's corner. Remember this is a heuristic, "
                "not ground truth: texture, noise and lighting all change the contrast, so a threshold is a tuning "
                "knob rather than a law. Print the scores, sort them and see which places win; the following days "
                "replace this crude measure with proper corner scores."
            ),
            code="""\
IMAGE = [
    [10, 10, 10, 10, 10],
    [10, 10, 10, 10, 10],
    [10, 10, 250, 10, 10],
    [10, 10, 10, 10, 10],
    [10, 10, 10, 10, 10],
]

def contrast(image, r, c):
    window = [image[rr][cc] for rr in range(r - 1, r + 2) for cc in range(c - 1, c + 2)]
    return max(window) - min(window)

points = []
for r in range(1, 4):
    for c in range(1, 4):
        points.append((contrast(IMAGE, r, c), r, c))
points.sort(reverse=True)
for score, r, c in points[:3]:
    print("point", (r, c), "contrast", score)

assert points[0][0] == 240
assert len(points) == 9
print("interesting points are where the local window changes")
""",
            variant_b="lower the bright pixel to 60 and explain why the top score drops",
            variant_c="use a 5x5 window instead of 3x3 and compare which points rank highest",
            mistakes=[
                "Reading a 3x3 window at the image border, so the loop indexes outside the grid.",
                "Treating local contrast as a true corner measure instead of a rough first filter.",
                "Forgetting that a single bright pixel also scores high, which is a blob not a corner.",
            ],
            q1=(
                "Why does a flat region make a poor keypoint?",
                "Sliding the window in any direction leaves the contents almost unchanged, so the location is not distinctive.",
            ),
            homework=(
                "Write `interesting_points(image, threshold)` that scans the interior pixels, computes the local "
                "contrast of each 3x3 window and returns the positions whose score is at least the threshold. Run "
                "it on a 5x5 image with one bright pixel, print the survivors in descending score order, and comment "
                "which line decides whether a point is kept."
            ),
            patterns=["def ", "max(", "print("],
            mapping=(
                "OpenCV's `goodFeaturesToTrack` and ORB both begin by finding locations whose neighbourhood is "
                "distinctive before any descriptor is computed."
            ),
        ),
        106: dict(
            topic="Corners by intuition",
            idea=(
                "The previous day ranked places by contrast, but contrast alone confuses a bright edge with a true "
                "corner. The classic intuition is motion: cover a tiny window and try to move it. Over a flat area, "
                "any shift leaves the window looking identical, so the sum of squared differences stays near zero. "
                "On an edge, a shift along the edge still matches, and only a shift across the edge changes the "
                "window, so one direction is informative and the other is not. At a corner, a shift in any "
                "direction changes the window, so the differences are large both horizontally and vertically. That "
                "asymmetry is the whole idea, and it is worth testing on two hand-drawn images: a horizontal edge "
                "and an L-shaped corner. Measure the total absolute difference when the image is compared with "
                "itself shifted one pixel right and one pixel down. The edge gives a large vertical response and "
                "almost none horizontally; the corner gives a large response in both. This directional gap is what "
                "a corner detector exploits. It also explains why corners are rare and valuable: most of an image "
                "is flat or edgy, and only the junctions respond in every direction. Today you build that "
                "measurement by hand and print the two responses."
            ),
            code="""\
EDGE = [
    [20, 20, 20, 20, 20],
    [20, 20, 20, 20, 20],
    [200, 200, 200, 200, 200],
    [200, 200, 200, 200, 200],
    [200, 200, 200, 200, 200],
]
CORNER = [
    [20, 20, 200, 200, 200],
    [20, 20, 200, 200, 200],
    [200, 200, 200, 200, 200],
    [200, 200, 200, 200, 200],
    [200, 200, 200, 200, 200],
]

def shift_diff(image, dr, dc):
    total = 0
    h, w = len(image), len(image[0])
    for r in range(h):
        for c in range(w):
            nr, nc = r + dr, c + dc
            if 0 <= nr < h and 0 <= nc < w:
                total += abs(image[r][c] - image[nr][nc])
    return total

for name, img in (("edge", EDGE), ("corner", CORNER)):
    print(name, "horizontal", shift_diff(img, 0, 1), "vertical", shift_diff(img, 1, 0))

assert shift_diff(EDGE, 0, 1) == 0
assert shift_diff(CORNER, 0, 1) > 0 and shift_diff(CORNER, 1, 0) > 0
print("a corner changes in both directions, an edge in one")
""",
            variant_b="reverse the corner image so the bright block sits top-right and re-run the two shifts",
            variant_c="use squared differences instead of absolute differences and compare the same two images",
            mistakes=[
                "Comparing the shifted image without checking bounds, so border pixels raise an error.",
                "Assuming a large response in one direction is enough, which describes an edge not a corner.",
                "Forgetting that shifting changes the number of overlapping pixels, so totals are not comparable.",
            ],
            q1=(
                "What distinguishes a corner from an edge in the shift test?",
                "A corner responds strongly to shifts in both directions, while an edge responds mainly to the shift across it.",
            ),
            homework=(
                "Write `shift_difference(image, dr, dc)` that returns the total absolute difference after shifting "
                "the image. Build a small edge image and a small corner image, print both directional responses, "
                "and comment which line skips pixels that fall outside the grid."
            ),
            patterns=["def ", "for ", "print("],
            mapping=(
                "This self-similarity view is the intuition behind the Harris and Shi-Tomasi detectors, and ORB's "
                "FAST test applies the same idea to a ring of neighbourhood pixels."
            ),
        ),
        107: dict(
            topic="A simple corner score",
            idea=(
                "Now turn the intuition into a number. Take the horizontal and vertical brightness gradients at "
                "every pixel, then sum three products over a small window: the sum of squared horizontal gradients, "
                "the sum of squared vertical gradients, and the sum of their products. Write them as a 2x2 matrix "
                "often called the structure tensor. Its determinant minus a fraction of its trace squared gives a "
                "score that is large at corners, small on edges and near zero on flat regions. That is the Harris "
                "corner score in its essential form. The matrix works because its two eigenvalues describe how "
                "strongly the window changes in the two principal directions; both large means a corner, one large "
                "means an edge. You do not need the eigenvalues to get a usable score, because the determinant and "
                "trace are cheap combinations that rank candidates the same way. Choose the constant, usually "
                "around 0.04 to 0.06, as a sensitivity knob: larger values suppress edges more aggressively. Today "
                "you implement gradients, accumulate the matrix over a 3x3 window and print scores for a few "
                "positions so the corner outranks its neighbours. This single function is the ancestor of the "
                "detectors used in real systems."
            ),
            code="""\
IMAGE = [
    [10, 10, 10, 10, 10, 10],
    [10, 10, 10, 10, 10, 10],
    [10, 10, 10, 10, 10, 10],
    [10, 10, 10, 200, 200, 200],
    [10, 10, 10, 200, 200, 200],
    [10, 10, 10, 200, 200, 200],
]

def grad(image, r, c):
    return image[r][c + 1] - image[r][c - 1], image[r + 1][c] - image[r - 1][c]

def corner_score(image, r, c):
    sx2 = sy2 = sxy = 0
    for rr in range(r - 1, r + 2):
        for cc in range(c - 1, c + 2):
            gx, gy = grad(image, rr, cc)
            sx2 += gx * gx
            sy2 += gy * gy
            sxy += gx * gy
    return round(sx2 * sy2 - sxy * sxy - 0.05 * (sx2 + sy2) ** 2, 2)

for r, c in ((2, 2), (2, 3), (3, 3)):
    print("score", (r, c), corner_score(IMAGE, r, c))

best = max((corner_score(IMAGE, r, c), r, c) for r in range(2, 4) for c in range(2, 4))
print("best corner", best[1:], "score", best[0])
assert best[1:] == (3, 3)
assert corner_score(IMAGE, 2, 3) < corner_score(IMAGE, 3, 3)
print("a corner scores high on both gradients")
""",
            variant_b="raise the constant to 0.10 and show whether the same pixel still wins",
            variant_c="accumulate over a 5x5 window and compare the scores with the 3x3 version",
            mistakes=[
                "Computing gradients at the very border, so the neighbour index falls off the image.",
                "Confusing the sign of the score with its magnitude; only the ranking matters.",
                "Choosing a huge constant, which subtracts so much that even true corners go negative.",
            ],
            q1=(
                "Why can the determinant and trace replace the eigenvalues?",
                "They are cheap combinations of the same matrix whose ranking agrees with the eigenvalue test for corners and edges.",
            ),
            homework=(
                "Write `corner_score(image, r, c)` that builds the structure tensor over a 3x3 window and returns "
                "the Harris-style score. Run it on a 6x6 image containing one bright square, print the scores for "
                "three positions, and comment which term punishes edges."
            ),
            patterns=["def ", "for ", "print("],
            mapping=(
                "`cv2.cornerHarris` computes exactly this response; Shi-Tomasi uses the smaller eigenvalue of the "
                "same matrix, and ORB relies on a FAST corner score instead."
            ),
        ),
        108: dict(
            topic="Descriptors as patches",
            idea=(
                "Detecting a keypoint tells you where something interesting is, but not what it looks like. To "
                "match across images you need a description of the local neighbourhood, and the simplest "
                "description is the raw patch: the small grid of pixel values around the keypoint, read out in a "
                "fixed order. That ordered list of numbers is the descriptor. Matching then becomes comparing "
                "lists. One detail matters immediately: raw brightness changes with exposure, so subtracting the "
                "patch mean removes the common offset and makes the descriptor far more stable. This is the first "
                "hint of a recurring theme, that a good descriptor is invariant to transformations that do not "
                "change identity. A patch descriptor of radius one holds nine values; radius two holds "
                "twenty-five. Larger patches carry more context but blur together nearby structure and cost more "
                "to compare. Reading the patch in row-major order is a choice, and as long as both images use the "
                "same order the comparison is consistent. Today you write a patch extractor and a descriptor that "
                "centres the values, then print both for one keypoint. Notice that the descriptor no longer "
                "contains the keypoint position; position is stored separately. Later descriptors are cleverer "
                "summaries of the same neighbourhood."
            ),
            code="""\
IMAGE = [
    [10, 10, 10, 10, 10, 10],
    [10, 40, 40, 40, 10, 10],
    [10, 40, 90, 40, 10, 10],
    [10, 40, 40, 40, 10, 10],
    [10, 10, 10, 10, 10, 10],
    [10, 10, 10, 10, 10, 10],
]

def patch(image, r, c, radius=1):
    values = []
    for rr in range(r - radius, r + radius + 1):
        for cc in range(c - radius, c + radius + 1):
            values.append(image[rr][cc])
    return values

def descriptor(image, r, c):
    values = patch(image, r, c)
    mean = sum(values) / len(values)
    return [round(v - mean, 2) for v in values]

d = descriptor(IMAGE, 2, 2)
print("keypoint", (2, 2), "patch", patch(IMAGE, 2, 2))
print("descriptor", d)
print("length", len(d))
assert len(d) == 9
assert abs(sum(d)) < 0.1
print("a descriptor is a small patch, centred on its keypoint")
""",
            variant_b="extract a radius-2 patch and compare the descriptor length and contents",
            variant_c="divide each value by the patch mean instead of subtracting it and print the result",
            mistakes=[
                "Reading the patch with the radius reversed, so the descriptor has the wrong length.",
                "Comparing uncentred patches, so a brightness change alone ruins the match.",
                "Mixing row-major and column-major order between two images, which breaks every comparison.",
            ],
            q1=(
                "Why subtract the patch mean before using the raw values as a descriptor?",
                "It removes the common brightness offset, so a change in exposure does not change the descriptor much.",
            ),
            homework=(
                "Write `descriptor(image, r, c, radius)` that extracts a square patch, subtracts its mean and "
                "returns the centred values. Print the descriptor for two keypoints of a small image and comment "
                "which line makes the descriptor robust to a brightness shift."
            ),
            patterns=["def ", "sum(", "print("],
            mapping=(
                "SIFT and ORB both summarise a local neighbourhood, but they do it with gradient histograms and "
                "intensity comparisons rather than the raw centred patch used here."
            ),
        ),
        109: dict(
            topic="Distance between descriptors",
            idea=(
                "Two descriptors are just two lists of numbers, so comparing them means measuring how far apart "
                "those lists are. The standard choice is Euclidean distance: subtract corresponding values, square, "
                "sum and take the square root. Smaller distance means more similar. The square root is monotonic, "
                "so for ranking you can skip it and compare sums of squares, which is faster; keep it when you want "
                "a value in the same units as the pixels. Several properties are worth knowing. Distance from a "
                "descriptor to itself is zero. Distance is symmetric, so it does not matter which one you call "
                "first. And distance grows with the number of elements, so descriptors of different lengths cannot "
                "be compared directly; always fix the length. Comparing raw brightness values is fragile, which is "
                "why yesterday's mean-centring helps here. A useful sanity check is that a descriptor is always "
                "closer to itself than to any unrelated one; if that fails, the descriptor or the distance is "
                "broken. Today you implement the squared and the Euclidean forms, check that self-distance is zero "
                "and print a few pairwise values. This tiny function is reused every time a matcher scores a "
                "candidate pair. A good distance is also cheap, because matching compares every query against every candidate."
            ),
            code="""\
A = [10, 20, 30, 40]
B = [12, 18, 33, 36]

def distance(a, b):
    total = 0
    for x, y in zip(a, b):
        total += (x - y) ** 2
    return round(total ** 0.5, 2)

print("A", A)
print("B", B)
print("distance A-B", distance(A, B))
print("distance A-A", distance(A, A))
print("distance A-zero", distance(A, [0, 0, 0, 0]))

assert distance(A, A) == 0.0
assert distance(A, B) < distance(A, [0, 0, 0, 0])
assert distance(A, B) == distance(B, A)
print("distance measures how far apart two descriptors are")
""",
            variant_b="compare the squared distance with the Euclidean distance and explain which is cheaper",
            variant_c="add a third descriptor and print all three pairwise distances in a small table",
            mistakes=[
                "Comparing descriptors of different lengths, so the zip silently drops the tail values.",
                "Forgetting the square root and reporting squared sums as if they were pixel distances.",
                "Subtracting in one direction only, which hides that distance should be symmetric.",
            ],
            q1=(
                "Why is the squared distance enough when you only need to rank candidates?",
                "The square root is monotonic, so it never changes the ordering, only the scale of the numbers.",
            ),
            homework=(
                "Write `distance(a, b)` returning the Euclidean distance between two equal-length descriptors. "
                "Test it with a descriptor and itself, with a shifted copy, and with a zero list, print each value "
                "and comment which line guarantees the lists are paired correctly."
            ),
            patterns=["def ", "zip(", "print("],
            mapping=(
                "OpenCV's BFMatcher reports exactly this distance for each pair, and the ratio test later relies "
                "on sorting those distances."
            ),
        ),
        110: dict(
            topic="Matching keypoints",
            idea=(
                "With descriptors in hand, matching is a search. For each descriptor in the first image, compare "
                "it against every descriptor in the second and keep the closest one: the nearest neighbour. That "
                "is brute-force matching, and for small sets it is exactly what real libraries do before any "
                "acceleration. The result is a list of pairs, one per query, but not all of them are correct. A "
                "repeated texture or a missing partner produces a confident wrong pair. Two habits keep this "
                "usable. First, always keep the distance alongside the pair so you can sort and filter later; a "
                "match without a score cannot be judged. Second, decide a policy for unmatched queries rather than "
                "silently accepting the best of a bad set. Notice that matching is not symmetric: the nearest "
                "neighbour of a descriptor in one image need not agree with the nearest neighbour in the other "
                "direction, a property called mutual consistency that later becomes a cheap filter. Today you "
                "implement the double loop that scores every pair, pick the minimum per query, and print the chosen "
                "partner and its distance. The same structure scales to thousands of descriptors once you index "
                "them. Keep the descriptor length fixed across both sets so distances stay comparable."
            ),
            code="""\
A = [[10, 0, 10], [0, 10, 0], [5, 5, 5]]
B = [[0, 10, 0], [9, 0, 9], [5, 5, 5]]

def distance(a, b):
    return round(sum((x - y) ** 2 for x, y in zip(a, b)) ** 0.5, 2)

for i, da in enumerate(A):
    best = min(range(len(B)), key=lambda j: distance(da, B[j]))
    print("A", i, "-> B", best, "distance", distance(da, B[best]))

first = min(range(len(B)), key=lambda j: distance(A[0], B[j]))
assert first == 1
assert distance(A[2], B[2]) == 0.0
print("matching is a nearest-neighbour search over descriptors")
""",
            variant_b="swap the two sets and show that the nearest neighbour in reverse can differ",
            variant_c="print the full distance of every query to every candidate as a small table",
            mistakes=[
                "Keeping only the partner and discarding the distance, so a bad match cannot be filtered later.",
                "Calling min on distances without tracking the index, so the matched keypoint is unknown.",
                "Assuming the reverse match is identical, which is false when the sets are different sizes.",
            ],
            q1=(
                "What does brute-force matching actually return for each query descriptor?",
                "The single candidate in the other set with the smallest descriptor distance, together with that distance.",
            ),
            homework=(
                "Write `match(query, candidates)` returning the index of the nearest candidate and its distance. "
                "Run it on two short lists of descriptors, print each chosen partner and distance, and comment "
                "which line picks the smallest distance."
            ),
            patterns=["def ", "min(", "print("],
            mapping=(
                "`cv2.BFMatcher.match` implements this double loop; `knnMatch` returns several neighbours so the "
                "ratio test has a second distance to compare."
            ),
        ),
        111: dict(
            topic="The ratio test",
            idea=(
                "Nearest-neighbour matching always returns something, even when the correct partner is missing, so "
                "the real problem is knowing when to trust a match. Lowe's ratio test handles this elegantly. "
                "Instead of comparing the best distance to a fixed threshold, compare it to the second-best "
                "distance. If the best match is genuinely correct, it should be clearly closer than the next-best "
                "candidate, which is likely a random mismatch. If both candidates are about equally close, the "
                "query is ambiguous and the match is probably wrong. The ratio of best to second-best is therefore "
                "a confidence measure that adapts to the image, because it normalises out how close distances "
                "happen to be. A common cut-off is around 0.75 to 0.8: keep the match only if the ratio is below "
                "it. Lower values keep fewer but cleaner matches. This is why good libraries return not just a "
                "match but its two nearest neighbours; the second one exists purely to be compared. Today you rank "
                "candidates by distance, compute the ratio and print whether the match survives. The test is "
                "cheap, needs no training, and removes most false matches. Notice that the test only works when the second-best candidate is a genuine alternative rather than a duplicate."
            ),
            code="""\
QUERY = [10, 0, 10]
CANDIDATES = [[9, 1, 9], [0, 10, 0], [5, 5, 5]]

def distance(a, b):
    return round(sum((x - y) ** 2 for x, y in zip(a, b)) ** 0.5, 2)

ranked = sorted(CANDIDATES, key=lambda c: distance(QUERY, c))
best = distance(QUERY, ranked[0])
second = distance(QUERY, ranked[1])
ratio = round(best / second, 2)
print("best", ranked[0], "distance", best)
print("second", ranked[1], "distance", second)
print("ratio", ratio, "keep", ratio < 0.8)

assert ranked[0] == [9, 1, 9]
assert ratio < 0.8
print("the ratio test rejects ambiguous matches")
""",
            variant_b="tighten the cut-off to 0.5 and check whether the same match still survives",
            variant_c="add a fourth candidate almost as close as the best and show the ratio rise",
            mistakes=[
                "Dividing by the best distance instead of the second, which inverts the test.",
                "Keeping a match with a ratio just below one, which is essentially a random pick.",
                "Forgetting to sort first, so the best and second distances are not the two smallest.",
            ],
            q1=(
                "What makes the ratio test adapt better than a fixed distance threshold?",
                "It compares the best distance to the second-best, normalising for how close distances are in that image.",
            ),
            homework=(
                "Write `ratio_test(query, candidates, threshold)` that ranks candidates by distance and returns "
                "the best candidate only if best divided by second is below the threshold. Print the best, second "
                "and ratio for one example and comment which line computes the confidence."
            ),
            patterns=["def ", "sorted(", "print("],
            mapping=(
                "Lowe's original SIFT paper introduced this test, and OpenCV's `knnMatch` plus a ratio check is "
                "still the standard first filter in ORB and SIFT pipelines."
            ),
        ),
        112: dict(
            topic="Template matching",
            idea=(
                "Sometimes you know exactly what you are looking for and only need to find where it is in a larger "
                "image. That is template matching, and it is the simplest form of correspondence. Slide the "
                "template over every valid position of the image, compare the overlapped region with the template, "
                "and record a score. The score is usually the sum of squared differences: add up the squared pixel "
                "differences and take the smallest value as the best position. Unlike feature matching, template "
                "matching has no descriptors, no keypoints and no learning; it assumes the object appears at the "
                "same size and orientation. That assumption is the weakness. A small rotation, a scale change or a "
                "brightness shift can ruin a raw difference, which is why real systems either normalise the "
                "comparison, for example by subtracting the mean, or abandon templates for keypoints. Still, the "
                "mechanics are worth writing by hand because everything that follows is a refinement of the same "
                "slide-and-score idea. Today you write a double loop that places the template at each top-left "
                "corner, compute the total difference and print the winning position. The example is tiny so you "
                "can verify the match by eye. Its output is a location, not a correspondence list, which is a useful distinction."
            ),
            code="""\
IMAGE = [
    [0, 0, 0, 0, 0],
    [0, 9, 9, 0, 0],
    [0, 9, 1, 9, 0],
    [0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0],
]
TEMPLATE = [
    [9, 9, 0],
    [9, 1, 9],
    [0, 0, 0],
]

def ssd(image, template, r, c):
    total = 0
    for tr in range(len(template)):
        for tc in range(len(template[0])):
            diff = image[r + tr][c + tc] - template[tr][tc]
            total += diff * diff
    return total

best = None
for r in range(len(IMAGE) - len(TEMPLATE) + 1):
    for c in range(len(IMAGE[0]) - len(TEMPLATE[0]) + 1):
        score = ssd(IMAGE, TEMPLATE, r, c)
        if best is None or score < best[0]:
            best = (score, r, c)
print("best position", (best[1], best[2]), "ssd", best[0])
assert best[1:] == (1, 1)
print("template matching slides a patch and keeps the lowest difference")
""",
            variant_b="pad the template with an extra column and show the best position shift",
            variant_c="subtract the template mean before comparing and explain why the score changes",
            mistakes=[
                "Allowing the window to run off the edge, so the overlap is smaller than the template.",
                "Taking the largest score as the match when squared differences are minimised.",
                "Assuming the match survives rotation or scale, which raw template matching cannot handle.",
            ],
            q1=(
                "Why is template matching more fragile than descriptor matching?",
                "It compares raw pixels directly, so any rotation, scale or brightness change breaks the similarity, and it has no invariance built in.",
            ),
            homework=(
                "Write `template_match(image, template)` returning the top-left position with the lowest sum of "
                "squared differences. Run it on a 5x5 image with an embedded 3x3 template, print the position and "
                "score, and comment which line bounds the slide so the template stays inside."
            ),
            patterns=["def ", "range(", "print("],
            mapping=(
                "`cv2.matchTemplate` offers the same sliding search with several score formulas; template matching "
                "is the base case that feature matching generalises."
            ),
        ),
        113: dict(
            topic="Rotation and scale effects",
            idea=(
                "A descriptor is useful only if it survives the transformations a real camera produces. Two of the "
                "most common are rotation and scale. Take a small patch, rotate it a quarter turn, and compare the "
                "rotated version with the original using the raw descriptor distance. The distance jumps, even "
                "though a human sees the same pattern. That is the key failure of the raw patch descriptor: it is "
                "tied to the pixel grid and the image's orientation, so the same physical corner produces a "
                "different list of numbers. Scale is just as damaging, because a patch that covers one feature at "
                "one distance may cover three features at another. The fix in modern descriptors is to estimate a "
                "dominant orientation from local gradients and to pick a patch size proportional to a detected "
                "scale, then sample in a rotation-aligned, scale-relative frame. That is exactly what SIFT does "
                "with its orientation histogram and its difference-of-Gaussians scale search, and what ORB "
                "approximates with a fast orientation measure. Today you rotate a patch with a transpose-and-"
                "reverse operation and print the distances before and after. Seeing the number rise motivates the "
                "rotation-aware machinery in the next days. The lesson generalises: any descriptor built on a fixed pixel grid inherits that grid's weaknesses."
            ),
            code="""\
PATCH = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9],
]

def distance(a, b):
    flat_a = [v for row in a for v in row]
    flat_b = [v for row in b for v in row]
    return round(sum((x - y) ** 2 for x, y in zip(flat_a, flat_b)) ** 0.5, 2)

def rotate90(patch):
    return [list(row) for row in zip(*patch[::-1])]

rotated = rotate90(PATCH)
print("original", PATCH)
print("rotated", rotated)
print("distance same", distance(PATCH, PATCH))
print("distance rotated", distance(PATCH, rotated))

assert distance(PATCH, PATCH) == 0.0
assert distance(PATCH, rotated) > 0
print("a raw patch descriptor changes under rotation")
""",
            variant_b="rotate the patch twice more and show the distance climbing toward the full turn",
            variant_c="scale the patch by dropping the last row and column and compare the distances",
            mistakes=[
                "Rotating the patch but forgetting to re-read it in the same fixed order before comparing.",
                "Assuming a small rotation leaves the raw descriptor almost unchanged.",
                "Comparing patches of different sizes after scaling, which the distance cannot handle.",
            ],
            q1=(
                "Why does a raw patch descriptor change when the image rotates?",
                "The list of values is tied to the pixel grid, so turning the pattern reshuffles which values the descriptor compares.",
            ),
            homework=(
                "Write `rotate90(patch)` returning a clockwise quarter-turn of a square patch, and use `distance` "
                "to compare the original with itself and with the rotated version. Print both distances and comment "
                "which property of the descriptor breaks."
            ),
            patterns=["def ", "zip(", "print("],
            mapping=(
                "SIFT adds an orientation from gradient histograms and a scale from a Gaussian pyramid; ORB uses "
                "an intensity centroid for orientation, both to fix exactly this failure."
            ),
        ),
        114: dict(
            topic="Deduplicating keypoints",
            idea=(
                "Corner detection rarely fires once. Around a single strong corner, many neighbouring pixels all "
                "pass the threshold, so the raw output is a cluster of near-identical keypoints. These duplicates "
                "waste time, inflate counts and bias any statistic computed per keypoint. The standard remedy is "
                "non-maximum suppression. Sort all candidates by score, then walk down the list keeping a "
                "candidate only if it is at least some radius away from every candidate already kept. Strong "
                "points suppress weaker neighbours, and the result is a sparse, well-spread set. Two parameters "
                "control the behaviour: the score threshold decides which candidates enter at all, and the "
                "suppression radius decides how close two surviving points may be. Set the radius too small and "
                "clusters remain; too large and genuinely distinct nearby corners are merged. The comparison is "
                "done in image coordinates, so a simple squared-distance check avoids a square root in the inner "
                "loop. Today you sort the keypoints, apply suppression with a modest radius and print the "
                "survivors. The same idea appears far beyond features, in bounding-box filtering and edge thinning, "
                "wherever a peaked response must reduce to one point. Suppression is really a clustering problem in disguise, and the radius sets its resolution."
            ),
            code="""\
KEYPOINTS = [
    (0.9, 10, 10),
    (0.8, 11, 10),
    (0.7, 40, 40),
    (0.6, 41, 41),
    (0.5, 25, 25),
]

def dedupe(points, radius):
    kept = []
    for score, r, c in sorted(points, reverse=True):
        if all((r - kr) ** 2 + (c - kc) ** 2 > radius * radius for _, kr, kc in kept):
            kept.append((score, r, c))
    return kept

kept = dedupe(KEYPOINTS, 5)
for score, r, c in kept:
    print("kept", (r, c), "score", score)

assert len(kept) == 3
assert (0.8, 11, 10) not in kept
print("non-max suppression keeps the strongest point in each neighbourhood")
""",
            variant_b="shrink the radius to 2 and show that fewer keypoints are suppressed",
            variant_c="use an eight-pixel radius and explain which weaker points now disappear",
            mistakes=[
                "Suppressing before sorting by score, so a weak point can evict a strong one.",
                "Comparing only row or only column difference, which keeps diagonal duplicates.",
                "Using a radius smaller than the density of the cluster, leaving several near-identical points.",
            ],
            q1=(
                "Why must the candidates be sorted by score before suppression?",
                "So the strongest point in a neighbourhood is kept and weaker neighbours are the ones removed.",
            ),
            homework=(
                "Write `dedupe(points, radius)` that sorts keypoints by score and keeps a point only if it is "
                "further than the radius from every kept point, using squared distance. Run it on five clustered "
                "keypoints, print the survivors and comment which line does the neighbourhood check."
            ),
            patterns=["def ", "sorted(", "print("],
            mapping=(
                "ORB and FAST both apply non-maximum suppression over a grid to bound and spread the keypoints "
                "they return."
            ),
        ),
        115: dict(
            topic="Homography concept",
            idea=(
                "The ultimate goal of matching is to know how one view maps onto another. When a scene is roughly "
                "planar, or the camera rotates about its optical centre, the relationship between two views is a "
                "homography, a single 3x3 matrix acting on homogeneous coordinates. Apply the matrix to a point, "
                "divide by the third output coordinate, and you land on the corresponding point in the other "
                "image. Four point correspondences are enough to solve the eight unknowns, which is why robust "
                "matching pipelines sample small sets of matches, fit a homography and count how many others "
                "agree. That agreeing count is the inlier set, and the procedure is RANSAC. The payoff is "
                "practical: once you have the homography you can warp images, stitch panoramas, or reject every "
                "match that violates the geometry. The matrix is projective, not affine, because the bottom row "
                "allows perspective foreshortening. Two cautions matter. Dividing by a coordinate near zero means "
                "the point maps to infinity, so guard the arithmetic. And a homography assumes a plane or a pure "
                "rotation; for general three-dimensional scenes it is only an approximation. Today you apply a "
                "hand-written matrix to several points. Mapping a point is matrix multiplication followed by "
                "normalisation, a pattern shared by all projective transforms."
            ),
            code="""\
H = [
    [1.0, 0.2, 5.0],
    [0.0, 1.0, 3.0],
    [0.0, 0.001, 1.0],
]

def apply_h(H, x, y):
    w = H[2][0] * x + H[2][1] * y + H[2][2]
    nx = (H[0][0] * x + H[0][1] * y + H[0][2]) / w
    ny = (H[1][0] * x + H[1][1] * y + H[1][2]) / w
    return round(nx, 2), round(ny, 2)

for point in ((0, 0), (10, 0), (0, 10), (10, 10)):
    print(point, "->", apply_h(H, *point))

assert apply_h(H, 0, 0) == (5.0, 3.0)
assert apply_h(H, 10, 0)[0] == 15.0
print("a homography maps any point through one 3x3 matrix")
""",
            variant_b="set the bottom-left entry to 0.002 and see the square deform more strongly",
            variant_c="change the translation terms and check that every mapped point shifts equally",
            mistakes=[
                "Forgetting the division by the homogeneous coordinate, so perspective is lost.",
                "Using fewer than four correspondences and expecting a unique homography.",
                "Treating the matrix as affine and ignoring the bottom row that creates foreshortening.",
            ],
            q1=(
                "Why is four correspondences the minimum for a homography?",
                "The 3x3 matrix has eight independent numbers after fixing scale, and each correspondence supplies two constraints.",
            ),
            homework=(
                "Write `apply_h(H, x, y)` that multiplies a homogeneous point by a 3x3 matrix and normalises by "
                "the third coordinate. Apply it to the four corners of a small square, print the results and "
                "comment which line performs the perspective division."
            ),
            patterns=["def ", "round(", "print("],
            mapping=(
                "`cv2.findHomography` with RANSAC fits this matrix from matches; panorama stitching and "
                "ORB-SLAM both use it to warp and verify views."
            ),
        ),
        116: dict(
            topic="Optical flow concept",
            idea=(
                "Feature matching pairs sparse points between two images, but sometimes you want to know how every "
                "pixel moved. That is optical flow, and its founding assumption is brightness constancy: a moving "
                "point keeps roughly the same brightness from one frame to the next, so its displacement is what "
                "best aligns a small window. The simplest implementation is exactly that idea, spelled out. Take a "
                "small window around a point in the first frame, slide it over a search region in the second frame "
                "and keep the shift with the lowest sum of squared differences. That brute-force search gives a "
                "displacement vector for the point. Lucas and Kanade made this efficient by linearising brightness "
                "as a linear function of the displacement and solving a tiny least-squares system per window, but "
                "the intuition and the failure modes are the same. Flow struggles where the window contains an "
                "edge, because motion along the edge is unobservable; this is the aperture problem, the "
                "optical-flow twin of the edge-versus-corner distinction. It also needs small motion between "
                "frames, since the linearisation breaks down for large shifts. Today you search a couple of "
                "integer shifts over a tiny pair of frames. A pyramid of scales handles larger motion in practice."
            ),
            code="""\
FRAME_A = [
    [0, 0, 0, 0, 0],
    [0, 9, 9, 0, 0],
    [0, 9, 9, 0, 0],
    [0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0],
]
FRAME_B = [
    [0, 0, 0, 0, 0],
    [0, 0, 9, 9, 0],
    [0, 0, 9, 9, 0],
    [0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0],
]

def patch_ssd(a, b, dx, dy):
    total = 0
    for rr in range(1, 3):
        for cc in range(1, 3):
            total += (a[rr][cc] - b[rr + dy][cc + dx]) ** 2
    return total

best = None
for dy in (0, 1):
    for dx in (0, 1):
        score = patch_ssd(FRAME_A, FRAME_B, dx, dy)
        if best is None or score < best[0]:
            best = (score, dx, dy)
print("best shift", (best[1], best[2]), "ssd", best[0])

assert best[1:] == (1, 0)
print("optical flow finds the shift that best matches the next frame")
""",
            variant_b="shift the second frame down instead of right and re-run the search",
            variant_c="expand the search to two pixels and show the true shift still wins",
            mistakes=[
                "Assuming brightness constancy holds across a large motion, where the linearisation fails.",
                "Ignoring the aperture problem, so flow along an edge is reported as zero.",
                "Comparing windows that run off the frame, which mixes in out-of-range pixels.",
            ],
            q1=(
                "What assumption lets a window search recover motion between frames?",
                "Brightness constancy: a moving point keeps roughly the same brightness, so the displacement that best aligns the window is the motion.",
            ),
            homework=(
                "Write `patch_ssd(a, b, dx, dy)` returning the sum of squared differences between a small patch "
                "in frame A and the shifted patch in frame B. Search a few integer shifts, print the best one, and "
                "comment which line keeps the current minimum."
            ),
            patterns=["def ", "for ", "print("],
            mapping=(
                "`cv2.calcOpticalFlowPyrLK` implements the Lucas-Kanade window search with pyramids, and it is "
                "routinely run on the keypoints that feature matching already found."
            ),
        ),
        117: dict(
            topic="Feature quality and thresholds",
            idea=(
                "Every feature detector ends with a threshold, and that threshold is a trade-off you have to make "
                "deliberately. Raise it and only strong responses survive: fewer keypoints, more of them genuine, "
                "but a risk of finding nothing in a low-contrast image. Lower it and you get many keypoints, "
                "including noise and repeated texture, so matching slows down and false pairs increase. There is "
                "no universally correct value, because the right cut depends on the image content, the sensor "
                "noise and the later task. The practical discipline is to treat the threshold as a parameter, "
                "sweep it, and look at the counts rather than guessing. A useful diagnostic is the distribution of "
                "scores, not just the passing set; a single strong peak is easy, while a long flat tail means no "
                "obvious cut and you should fall back on a relative rule, such as keeping a fixed fraction of the "
                "best responses. This relative approach is what ORB does when it bounds the number of keypoints "
                "per image, and what adaptive methods do when they normalise by local contrast. Today you apply "
                "several thresholds to the same list of scores and print how many survive at each, so the curve "
                "becomes concrete."
            ),
            code="""\
SCORES = [0.9, 0.7, 0.65, 0.3, 0.2, 0.1]

for threshold in (0.2, 0.5, 0.8):
    kept = [s for s in SCORES if s >= threshold]
    print("threshold", threshold, "kept", len(kept), kept)

assert len([s for s in SCORES if s >= 0.5]) == 3
assert len([s for s in SCORES if s >= 0.2]) == 5
print("a higher threshold keeps fewer, stronger keypoints")
""",
            variant_b="keep only the top three scores by rank and compare that with a fixed threshold",
            variant_c="add a score of 0.5 and show which thresholds change their count",
            mistakes=[
                "Tuning the threshold on one image and assuming it transfers to different lighting.",
                "Lowering the threshold to get more matches without checking that false matches rise too.",
                "Reading the number of keypoints alone and ignoring the distribution of scores behind it.",
            ],
            q1=(
                "What is the trade-off when you raise the corner threshold?",
                "Fewer and stronger keypoints are kept, which improves match quality but risks finding nothing in a flat or low-contrast image.",
            ),
            homework=(
                "Write `count_above(scores, threshold)` returning how many scores meet the threshold, then call "
                "it for several thresholds and print the counts. Comment which line expresses the comparison that "
                "defines a keypoint as strong enough."
            ),
            patterns=["def ", "for ", "print("],
            mapping=(
                "ORB caps the number of keypoints per image and applies its own FAST threshold, exactly the "
                "quantity-versus-quality trade handled here."
            ),
        ),
        118: dict(
            topic="Evaluating a matcher",
            idea=(
                "A matcher that returns pairs is not automatically a good matcher, and the only way to know is to "
                "measure it. If you have ground-truth correspondences, two numbers tell most of the story. "
                "Precision is the fraction of returned matches that are actually correct: it answers how often you "
                "can trust a match. Recall is the fraction of true correspondences you managed to find: it answers "
                "how many you missed. The two trade off. A strict ratio test raises precision and lowers recall; a "
                "loose one does the opposite. Reporting a single accuracy figure hides this, which is why vision "
                "papers list both and plot one against the other. Counting also needs care about direction, "
                "because matches are usually one-to-one, and an unmatched query is not the same as a false match. "
                "For a quick check on small data, precision and recall computed by hand over a short list are "
                "enough to see the machinery work. Today you compare a predicted match list against a truth set, "
                "count the intersection and print both fractions. Building this habit early makes every later "
                "improvement, from the ratio test to RANSAC, measurable rather than a matter of opinion, and it "
                "forces you to define what a correct match even means."
            ),
            code="""\
MATCHES = [(0, 1), (1, 0), (2, 2), (3, 3)]
TRUTH = {(0, 1), (1, 0), (2, 2)}

correct = [m for m in MATCHES if m in TRUTH]
precision = round(len(correct) / len(MATCHES), 2)
recall = round(len(correct) / len(TRUTH), 2)
print("predicted", MATCHES)
print("correct", correct)
print("precision", precision, "recall", recall)

assert correct == [(0, 1), (1, 0), (2, 2)]
assert precision == 0.75
assert recall == 1.0
print("precision and recall describe different failure modes")
""",
            variant_b="add a wrong match to the list and show precision drop while recall stays put",
            variant_c="remove a correct match and show recall fall while precision holds",
            mistakes=[
                "Reporting accuracy alone, which hides whether errors are false matches or missed ones.",
                "Counting pairs in only one direction, so the truth set and the matches are misaligned.",
                "Treating an unmatched query as a wrong match, which inflates the error count.",
            ],
            q1=(
                "What do precision and recall each measure for a matcher?",
                "Precision is the fraction of returned matches that are correct; recall is the fraction of true correspondences that were found.",
            ),
            homework=(
                "Write `evaluate(matches, truth)` returning the precision and recall as a pair of rounded "
                "fractions. Run it on a short match list with one wrong entry, print both numbers, and comment "
                "which line computes the hits shared with the truth set."
            ),
            patterns=["def ", "for ", "print("],
            mapping=(
                "Feature benchmarks report precision and recall curves over the ratio threshold, and RANSAC "
                "inlier counts are the same idea applied to geometry."
            ),
        ),
        119: dict(
            topic="Review: features and matching checklist",
            idea=(
                "Today you assemble the phase into a checklist and run the parts together on one tiny image. The "
                "pipeline has five questions. Where are the interesting places? Find keypoints with a corner score "
                "and suppress the duplicates. What does each one look like? Build a descriptor from its "
                "neighbourhood. What is the distance between descriptors? Use Euclidean distance on equal-length "
                "lists. Which descriptor is the best partner? Take the nearest neighbour, and measure how clearly "
                "it wins with the ratio test. How do you know it worked? Count matches and, when truth is "
                "available, compute precision and recall. Each stage has a knob. The corner threshold controls the "
                "number of keypoints, the suppression radius controls their spacing, the patch size controls the "
                "descriptor, and the ratio controls match quality. This phase deliberately uses raw patches so the "
                "mechanics are visible; the next phase replaces them with rotation-invariant and scale-invariant "
                "descriptors, and adds geometry to reject outliers. Keep the five stages as separate functions, "
                "print the intermediate values, and remember that almost every real system is this same list with "
                "better parts. Write the checklist down and use it as a review sheet whenever a match result looks "
                "wrong or a count is surprising."
            ),
            code="""\
IMAGE = [
    [10, 10, 10, 10, 10],
    [10, 10, 10, 10, 10],
    [10, 10, 240, 240, 10],
    [10, 10, 240, 240, 10],
    [10, 10, 10, 10, 10],
]

def contrast(image, r, c):
    window = [image[rr][cc] for rr in range(r - 1, r + 2) for cc in range(c - 1, c + 2)]
    return max(window) - min(window)

keypoints = []
for r in range(1, 4):
    for c in range(1, 4):
        score = contrast(IMAGE, r, c)
        if score >= 200:
            keypoints.append((score, r, c))
keypoints.sort(reverse=True)
print("keypoints", keypoints)
print("count", len(keypoints))
assert keypoints[0][0] == 230
print("features: find, describe, match, verify")
""",
            variant_b="raise the contrast threshold to 235 and show the keypoint list empty out",
            variant_c="add a suppression radius so only the top keypoint in each cluster survives",
            mistakes=[
                "Merging all stages into one function, so a wrong count cannot be traced to a stage.",
                "Skipping the ratio test and accepting the nearest neighbour with no confidence measure.",
                "Comparing descriptors of different patch sizes after changing the radius mid-pipeline.",
            ],
            q1=(
                "Which stage of the checklist removes duplicates before matching?",
                "Deduplication with non-maximum suppression, which keeps the strongest keypoint in each neighbourhood and drops the rest.",
            ),
            homework=(
                "Write `find_keypoints(image, threshold)` returning scored keypoints above the threshold, then a "
                "`pipeline(image)` that finds keypoints, builds a centred patch descriptor for each, matches them "
                "and reports the pair count. Print the intermediate stages and comment which line filters by "
                "threshold."
            ),
            patterns=["def ", "for ", "print("],
            mapping=(
                "ORB-SLAM and panorama stitchers run exactly this find-describe-match-verify chain, swapping the "
                "raw patch for ORB or SIFT and adding RANSAC to reject geometric outliers."
            ),
        ),
    },
)
