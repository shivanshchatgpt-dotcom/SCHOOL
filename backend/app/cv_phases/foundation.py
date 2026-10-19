"""Computer Vision foundations, days 9-14: images as data, no image libraries.

Every example is stdlib-only, offline and deterministic: an image is a nested
list of pixel values, and every operation is a loop over that list. The domain
phases keep the same discipline, so a pipeline can be run and asserted on
without OpenCV, a camera or a file on disk.
"""

FOUNDATION = {
    9: dict(
        topic="An image is a grid of numbers",
        idea=(
            "A digital image is a rectangular grid of numbers, and every vision operation is arithmetic on that "
            "grid. Understanding this removes the sense that images are magical objects. The grid has a height "
            "and a width, and each cell holds a value — a brightness for a grayscale image, or three values for "
            "colour. In Python the natural representation is a list of rows, where each row is a list of pixel "
            "values. That is exactly the shape a framework calls an array, minus the fast maths. The two facts "
            "worth fixing early are that indexing is `[row][column]` and that sizes are given as height times "
            "width, not the other way round. Most beginner bugs are a transposed shape or an off-by-one at the "
            "border. Today you build a small grid, print it as rows, and write functions to read a pixel and "
            "report the image's dimensions. Printing the grid, rather than an image viewer, makes the data "
            "visible and is the fastest way to debug a preprocessing step. Every later topic — colour, filters, "
            "thresholds, components — operates on this same structure."
        ),
        code=(
            'IMAGE = [\n'
            '    [0, 50, 100],\n'
            '    [150, 200, 250],\n'
            ']\n'
            '\n'
            'def size(image):\n'
            '    return len(image), len(image[0])\n'
            '\n'
            'def pixel(image, row, col):\n'
            '    return image[row][col]\n'
            '\n'
            'height, width = size(IMAGE)\n'
            'print("size:", height, "x", width)\n'
            'for row in IMAGE:\n'
            '    print(row)\n'
            'print("pixel (1, 2):", pixel(IMAGE, 1, 2))\n'
            '\n'
            'assert size(IMAGE) == (2, 3)\n'
            'assert pixel(IMAGE, 1, 2) == 250\n'
            'print("images are row-major grids of numbers")'
        ),
        variant_b='build a 3x4 image of zeros and set one pixel to 255, then print the rows',
        variant_c='write `column(image, c)` returning one column and use it to check the indexing order',
        mistakes=[
            "Swapping height and width, so loops read past the end of a row.",
            "Indexing as [column][row] while the data is stored as rows.",
            "Assuming every row has the same length instead of validating the grid.",
        ],
        q1=(
            "In a list-of-rows image, what does `image[r][c]` address?",
            "The pixel at row r and column c, because the outer list holds rows and each inner list holds that row's values.",
        ),
        homework=(
            "Write `size(image)` and `pixel(image, row, col)`. Build a 3x3 image with distinct values, print "
            "its size and the centre pixel, and comment which index selects the row."
        ),
        patterns=["def ", "len(", "print("],
        mapping=(
            "OpenCV and torchvision expose images as arrays with a height-width-channel convention; the "
            "row-major indexing here is the same rule."
        ),
    ),
    10: dict(
        topic="Channels and colour maths",
        idea=(
            "A colour image has three channels per pixel, usually red, green and blue, so the grid becomes a "
            "grid of triples. Two operations dominate early vision work: converting to grayscale, and adjusting "
            "brightness or contrast. Grayscale is a weighted sum of the channels, not a plain average, because "
            "human vision is more sensitive to green than to blue. A common weighting is 0.299 red, 0.587 green "
            "and 0.114 blue, and using it makes a conversion look right rather than washed out. The second "
            "lesson is that pixel values have a range, typically zero to 255, and arithmetic must respect it. "
            "Brightening by adding a constant can push values past the maximum, and clipping keeps the result "
            "valid; without clipping the numbers drift outside the expected range and later thresholds behave "
            "strangely. Today you convert a small colour image to grayscale with the weighted formula and "
            "brighten it with clipping. Notice that both operations are per-pixel and independent of "
            "neighbours, which is why they are the easy half of image processing. The harder half, filtering, "
            "looks at neighbourhoods and comes next."
        ),
        code=(
            'def to_gray(pixel):\n'
            '    r, g, b = pixel\n'
            '    return round(0.299 * r + 0.587 * g + 0.114 * b)\n'
            '\n'
            'def brighten(pixel, amount, maximum=255):\n'
            '    return [min(maximum, value + amount) for value in pixel]\n'
            '\n'
            'colour = [[255, 0, 0], [0, 255, 0], [0, 0, 255]]\n'
            'for p in colour:\n'
            '    print(p, "-> gray", to_gray(p))\n'
            '\n'
            'print("brightened:", brighten([250, 10, 0], 20))\n'
            '\n'
            'assert to_gray([255, 0, 0]) == 76\n'
            'assert to_gray([0, 255, 0]) == 150\n'
            'assert brighten([250, 10, 0], 20) == [255, 30, 20]\n'
            'print("colour maths is per-pixel and range-aware")'
        ),
        variant_b='use a plain average instead of the weighted formula and compare the grayscale values',
        variant_c='add a contrast function that scales around 128 and clips the result',
        mistakes=[
            "Averaging channels equally, which produces grayscale that looks wrong to human eyes.",
            "Letting brightness arithmetic exceed the maximum without clipping.",
            "Treating a pixel as one number when the image is actually three channels.",
        ],
        q1=(
            "Why is grayscale a weighted sum rather than a plain average of RGB?",
            "Human vision is more sensitive to green, and the weights approximate perceived brightness so the result looks natural.",
        ),
        homework=(
            "Write `to_gray(image)` that converts a list of RGB rows into one grayscale value per pixel, plus "
            "`brighten(image, amount)`. Run both on a 2x2 colour image, print the results, and comment which "
            "line clips the values to the valid range."
        ),
        patterns=["def ", "round", "print("],
        mapping=(
            "`cv2.cvtColor(..., cv2.COLOR_BGR2GRAY)` uses a similar luminance weighting; understanding the "
            "weights explains why OpenCV's BGR order matters."
        ),
    ),
    11: dict(
        topic="Thresholding and masks",
        idea=(
            "Thresholding turns a grayscale image into a binary mask, and masks are how vision code decides what "
            "to look at. The rule is simple: if a pixel is above a threshold it becomes foreground, otherwise "
            "background. What makes it useful is that the output is a small, inspectable structure rather than "
            "a picture; you can count foreground pixels, find their bounding box, or use the mask to select "
            "colours from the original. Two practical points save a lot of confusion. First, threshold "
            "direction matters: bright objects on a dark background need the opposite comparison from dark "
            "objects on a bright background, so make it a parameter rather than a hard-coded choice. Second, a "
            "raw threshold is sensitive to lighting, so real pipelines usually normalise or blur first. Today "
            "you write a threshold function that returns a mask of zeros and ones, then count the foreground and "
            "compute a bounding box over the mask. Those two derived values are the start of segmentation, and "
            "they are much easier to test than the image itself. Keep the example tiny so the mask can be read "
            "directly as a grid."
        ),
        code=(
            'def threshold(image, value, above=True):\n'
            '    return [[1 if (px >= value) == above else 0 for px in row] for row in image]\n'
            '\n'
            'def foreground(mask):\n'
            '    return sum(sum(row) for row in mask)\n'
            '\n'
            'def bbox(mask):\n'
            '    rows = [r for r, row in enumerate(mask) if any(row)]\n'
            '    cols = [c for c, row in enumerate(zip(*mask)) for v in row if v]\n'
            '    return (min(rows), min(cols), max(rows), max(cols))\n'
            '\n'
            'gray = [[10, 200, 30], [220, 240, 5]]\n'
            'mask = threshold(gray, 100)\n'
            'for row in mask:\n'
            '    print(row)\n'
            'print("foreground:", foreground(mask), "bbox:", bbox(mask))\n'
            '\n'
            'assert mask == [[0, 1, 0], [1, 1, 0]]\n'
            'assert foreground(mask) == 3\n'
            'assert bbox(mask) == (0, 0, 1, 1)\n'
            'print("a mask is data you can count and bound")'
        ),
        variant_b='flip the comparison (above=False) and show the mask selects the dark pixels instead',
        variant_c='return two masks, one for bright and one for dark pixels, and count each',
        mistakes=[
            "Hard-coding the comparison direction, so the mask inverts when the lighting changes.",
            "Computing a bounding box before checking that the mask has any foreground pixels.",
            "Confusing the threshold value's scale (0-255) with a normalised 0-1 range.",
        ],
        q1=(
            "Why keep the threshold direction as a parameter?",
            "Bright objects on dark backgrounds and dark objects on bright backgrounds need opposite comparisons, and the choice should be explicit.",
        ),
        homework=(
            "Write `threshold(image, value)` returning a 0/1 mask, plus `foreground(mask)` and `bbox(mask)`. "
            "Test them on a 3x3 grid with four bright pixels, print the mask, count and box, and comment which "
            "line decides what counts as foreground."
        ),
        patterns=["def ", "if ", "print("],
        mapping=(
            "`cv2.threshold` returns exactly this mask plus the value used; bounding boxes and pixel counts "
            "are the first features most segmentation code computes."
        ),
    ),
    12: dict(
        topic="Filters are convolution",
        idea=(
            "A filter replaces each pixel with a combination of its neighbours, and convolution is the general "
            "form: slide a small kernel over the image, multiply each kernel weight by the pixel underneath, and "
            "sum. A box blur with equal weights averages the neighbourhood and smooths noise; a kernel with a "
            "positive centre and negative neighbours sharpens or detects edges. The concept to internalise is "
            "that the kernel is the whole specification of the operation — change the numbers and you change "
            "the effect. Three details matter in practice. Border handling is a choice: skip the border, pad "
            "with zeros, or replicate edge pixels, and the choice changes the output size. Normalising the "
            "kernel keeps brightness roughly constant for averaging filters. And integer arithmetic with a "
            "division at the end is easier to reason about than premature floating point. Today you implement a "
            "3x3 convolution that skips a one-pixel border, using a box blur, and print both images so the "
            "smoothing is visible as numbers. This one function is the ancestor of blur, sharpening, edge "
            "detection and, conceptually, the convolution layers in a CNN."
        ),
        code=(
            'def convolve(image, kernel):\n'
            '    size = len(kernel)\n'
            '    offset = size // 2\n'
            '    divisor = sum(sum(row) for row in kernel) or 1\n'
            '    height, width = len(image), len(image[0])\n'
            '    out = [[0] * (width - 2 * offset) for _ in range(height - 2 * offset)]\n'
            '    for r in range(offset, height - offset):\n'
            '        for c in range(offset, width - offset):\n'
            '            total = 0\n'
            '            for kr in range(size):\n'
            '                for kc in range(size):\n'
            '                    total += kernel[kr][kc] * image[r + kr - offset][c + kc - offset]\n'
            '            out[r - offset][c - offset] = round(total / divisor, 2)\n'
            '    return out\n'
            '\n'
            'image = [\n'
            '    [0, 0, 0, 0],\n'
            '    [0, 90, 90, 0],\n'
            '    [0, 90, 90, 0],\n'
            '    [0, 0, 0, 0],\n'
            ']\n'
            'blur = [[1, 1, 1], [1, 1, 1], [1, 1, 1]]\n'
            'result = convolve(image, blur)\n'
            'for row in result:\n'
            '    print(row)\n'
            '\n'
            'assert result[0][0] == 40.0\n'
            'assert result[1][1] == 40.0\n'
            'print("a kernel is a tiny program applied at every pixel")'
        ),
        variant_b='use a sharpening kernel [[0,-1,0],[-1,5,-1],[0,-1,0]] and explain why it is not normalised',
        variant_c='use a sobel-x kernel and print the values to see vertical edges amplified',
        mistakes=[
            "Forgetting to skip or pad the border, so the output is misaligned by one pixel.",
            "Using an unnormalised averaging kernel, which makes the image brighter at every step.",
            "Convolving with the kernel flipped when the definition expects a specific orientation.",
        ],
        q1=(
            "What does the kernel's numbers actually specify?",
            "The weights applied to each neighbourhood position; changing them changes the operation, from blur to sharpen to edge detection.",
        ),
        homework=(
            "Write `convolve(image, kernel)` for 3x3 kernels, skipping the border. Apply a box blur to a small "
            "image, print the original and result, and comment which line normalises the weights."
        ),
        patterns=["def ", "for ", "print("],
        mapping=(
            "OpenCV's `filter2D` and a CNN's convolutional layer both apply learned or hand-written kernels "
            "with padding and stride choices."
        ),
    ),
    13: dict(
        topic="Connected components",
        idea=(
            "A binary mask often contains several separate blobs, and the first question is how many and where. "
            "Connected components answers it: pixels belong to the same blob if they are adjacent and both "
            "foreground. Four-connectivity considers up, down, left and right; eight-connectivity also includes "
            "diagonals. The standard implementation is a flood fill, either with a stack or a queue, that walks "
            "from an unvisited foreground pixel and marks every reachable neighbour. The output is a set of "
            "groups, and from each group you can compute area, centroid and bounding box. This is segmentation "
            "in miniature: no model, just connectivity and a traversal. Two practical notes. Decide connectivity "
            "deliberately, because diagonal-only touches are a common source of surprising counts. And keep a "
            "visited set so the traversal is linear in the number of pixels rather than exponential. Today you "
            "run a flood fill over a small mask and print each component's pixels and area. The same traversal "
            "underlies region growing, flood-fill tools and object counting before deep learning."
        ),
        code=(
            'def components(mask):\n'
            '    height, width = len(mask), len(mask[0])\n'
            '    seen = set()\n'
            '    groups = []\n'
            '    for r in range(height):\n'
            '        for c in range(width):\n'
            '            if mask[r][c] and (r, c) not in seen:\n'
            '                stack = [(r, c)]\n'
            '                group = []\n'
            '                while stack:\n'
            '                    cr, cc = stack.pop()\n'
            '                    if (cr, cc) in seen or not mask[cr][cc]:\n'
            '                        continue\n'
            '                    seen.add((cr, cc))\n'
            '                    group.append((cr, cc))\n'
            '                    for nr, nc in ((cr-1, cc), (cr+1, cc), (cr, cc-1), (cr, cc+1)):\n'
            '                        if 0 <= nr < height and 0 <= nc < width and mask[nr][nc]:\n'
            '                            stack.append((nr, nc))\n'
            '                groups.append(group)\n'
            '    return groups\n'
            '\n'
            'mask = [\n'
            '    [1, 1, 0, 0],\n'
            '    [1, 0, 0, 1],\n'
            '    [0, 0, 1, 1],\n'
            ']\n'
            'groups = components(mask)\n'
            'print("count:", len(groups))\n'
            'for group in groups:\n'
            '    print("pixels:", sorted(group), "area:", len(group))\n'
            '\n'
            'assert len(groups) == 2\n'
            'assert [len(g) for g in groups] == [3, 3]\n'
            'print("connectivity turns a mask into objects")'
        ),
        variant_b='switch to eight-connectivity and check whether the two groups merge',
        variant_c='return each component\'s centroid and bounding box instead of the pixel list',
        mistakes=[
            "Forgetting the visited set, so the flood fill revisits pixels and never terminates on loops.",
            "Checking bounds after indexing, so border pixels raise an IndexError.",
            "Assuming diagonal touching counts as connected without choosing eight-connectivity explicitly.",
        ],
        q1=(
            "Why is a visited set essential in flood fill?",
            "Without it neighbouring pixels push each other back onto the stack repeatedly, so the traversal can loop forever.",
        ),
        homework=(
            "Write `components(mask)` using an explicit stack and four-connectivity, returning a list of pixel "
            "lists. Run it on a mask with two separate blobs, print each blob's area, and comment which line "
            "marks a pixel as visited."
        ),
        patterns=["def ", "stack", "print("],
        mapping=(
            "`cv2.connectedComponents` and scikit-image's `label` do this at scale; the traversal and the "
            "connectivity choice are identical."
        ),
    ),
    14: dict(
        topic="A tiny vision pipeline, end to end",
        idea=(
            "Today you connect the week: take a small colour image, convert it to grayscale, threshold it into a "
            "mask, find connected components, and report each object's bounding box and area. It is a complete "
            "vision pipeline with no model and no library, and it demonstrates the shape every later pipeline "
            "takes: preprocess, transform, extract structure, measure. Because each stage returns a value, you "
            "can inspect the intermediate results and localise a failure precisely: a wrong count is either a "
            "bad mask or a bad component step, and printing the mask tells you which. That is far more useful "
            "than staring at a final picture. The example also makes an honest trade-off: a fixed threshold "
            "works on this synthetic image and would need adaptation under real lighting, which is exactly why "
            "the later phases cover normalisation, learned features and evaluation. Keep the stages as separate "
            "functions rather than one long script, because the seams are what you will test and replace. Build "
            "the skeleton here and the domain phases simply deepen each box."
        ),
        code=(
            'def to_gray(image):\n'
            '    return [[round(0.299*r + 0.587*g + 0.114*b) for r, g, b in row] for row in image]\n'
            '\n'
            'def threshold(image, value):\n'
            '    return [[1 if px >= value else 0 for px in row] for row in image]\n'
            '\n'
            'def components(mask):\n'
            '    h, w = len(mask), len(mask[0])\n'
            '    seen, groups = set(), []\n'
            '    for r in range(h):\n'
            '        for c in range(w):\n'
            '            if mask[r][c] and (r, c) not in seen:\n'
            '                stack, group = [(r, c)], []\n'
            '                while stack:\n'
            '                    cr, cc = stack.pop()\n'
            '                    if (cr, cc) in seen or not mask[cr][cc]:\n'
            '                        continue\n'
            '                    seen.add((cr, cc)); group.append((cr, cc))\n'
            '                    for nr, nc in ((cr-1,cc),(cr+1,cc),(cr,cc-1),(cr,cc+1)):\n'
            '                        if 0 <= nr < h and 0 <= nc < w and mask[nr][nc]:\n'
            '                            stack.append((nr, nc))\n'
            '                groups.append(group)\n'
            '    return groups\n'
            '\n'
            'def bbox(group):\n'
            '    rows = [r for r, _ in group]; cols = [c for _, c in group]\n'
            '    return (min(rows), min(cols), max(rows), max(cols))\n'
            '\n'
            'image = [\n'
            '    [[255,255,255],[255,255,255],[0,0,0],[0,0,0]],\n'
            '    [[255,255,255],[255,255,255],[0,0,0],[0,0,0]],\n'
            '    [[0,0,0],[0,0,0],[255,255,255],[255,255,255]],\n'
            ']\n'
            'gray = to_gray(image)\n'
            'mask = threshold(gray, 128)\n'
            'groups = components(mask)\n'
            'print("gray:", gray)\n'
            'print("mask:", mask)\n'
            'print("objects:", [(bbox(g), len(g)) for g in groups])\n'
            '\n'
            'assert len(groups) == 2\n'
            'assert [len(g) for g in groups] == [4, 2]\n'
            'print("preprocess, threshold, segment, measure")'
        ),
        variant_b='lower the threshold to 100 and explain why the mask and object count change',
        variant_c='add a minimum-area filter so tiny blobs are discarded before reporting',
        mistakes=[
            "Combining all stages in one function, so a wrong object count cannot be traced to a stage.",
            "Reporting objects before checking that the mask is non-empty.",
            "Using a threshold tuned to one image and assuming it transfers to different lighting.",
        ],
        q1=(
            "Why keep each pipeline stage as a separate function?",
            "Each intermediate result can be printed and asserted on, so a failure is localised to a stage instead of the whole pipeline.",
        ),
        homework=(
            "Write `pipeline(image, threshold_value)` that grayscales, thresholds, finds components and returns "
            "each object's bounding box and area. Run it on a small image with two blobs, print the stages and "
            "final objects, and comment which call is the preprocessing step."
        ),
        patterns=["def ", "print(", "return"],
        mapping=(
            "This is the classic preprocess-segment-measure pipeline; modern detectors replace the middle "
            "stages but keep the same interfaces and evaluation questions."
        ),
    ),
}
