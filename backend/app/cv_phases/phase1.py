PHASE = ("Images as Arrays", "Build a precise mental model of images as nested lists of numbers and the small operations that reshape them.", {
    75: dict(
        topic="Orientation: how computers see images",
        idea=(
            "An image, to a computer, is a rectangular arrangement of numbers, and every operation in this phase is "
            "arithmetic on that arrangement. There is no picture inside the machine, only rows and columns of values "
            "that a display later turns into light. The useful mental model is a table: the height counts rows, the "
            "width counts columns, and the position of a value is read as row first and column second. That order "
            "matters more than it looks, because swapping it is the most common early bug. A grayscale image stores one "
            "number per cell, and a colour image stores a small list of channel values per cell, but the outer "
            "structure is the same. Python's natural representation is a list of rows, each row a list of numbers. "
            "Indexing a pixel is therefore two brackets, and iterating the outer list walks down the image while "
            "iterating an inner list walks across it. Today you print a tiny grid and read it as data, so the "
            "connection between the loops and the picture is explicit. Once that is solid, resizing, colour conversion "
            "and filtering are all just careful loops over the same structure. Read the printed rows aloud and point "
            "at each value until the indexing feels ordinary."
        ),
        code=(
            'grid = [\n'
            '    [10, 20, 30],\n'
            '    [40, 50, 60],\n'
            '    [70, 80, 90],\n'
            ']\n'
            '\n'
            'print("height:", len(grid), "width:", len(grid[0]))\n'
            'for row in grid:\n'
            '    print(row)\n'
            'print("pixel at row 1, column 2:", grid[1][2])\n'
            'print("top-left pixel:", grid[0][0])\n'
            '\n'
            'assert grid[1][2] == 60\n'
            'assert len(grid) == 3 and len(grid[0]) == 3\n'
            'print("row index first, column index second")'
        ),
        variant_b="build a 2x4 grid of zeros, set two pixels to 255, and print it as rows",
        variant_c="write `pixel(image, row, col)` and a bounds check that rejects negative indices",
        mistakes=[
            "Swapping row and column, so code reads the transpose of the intended pixel.",
            "Treating height and width as interchangeable when printing or iterating.",
            "Assuming an image is square and indexing past the end of a shorter row.",
        ],
        q1=(
            "In a list-of-rows image, what does `image[r][c]` address?",
            "The pixel at row r and column c, because the outer list holds rows and each inner list holds that row's values.",
        ),
        homework=(
            "Write `orient(image)` that returns the height and width, then prints the grid row by row and the "
            "four corner pixels. Build a 3x3 image with distinct values, call `orient`, and comment which bracket "
            "selects the row and which selects the column."
        ),
        patterns=["def ", "len(", "print("],
        mapping=(
            "OpenCV and torchvision expose images as arrays ordered height, width, channel; the row-first indexing "
            "you use here is the same rule."
        ),
    ),
    76: dict(
        topic="Pixels, rows and channels",
        idea=(
            "A grayscale pixel is one number, while a colour pixel is a small sequence of channel values, usually red, "
            "green and blue in that order for hand-written code. The image as a whole is a grid of those pixels, so a "
            "colour image is a list of rows, each row a list of pixels, and each pixel a list of three integers. That "
            "is three nested levels, and most confusion comes from losing track of which level a loop is on. Reading "
            "`image[r][c]` gives one pixel; adding `[1]` gives that pixel's green value. Printing the dimensions of "
            "each level separately is a quick sanity check: height, width, and channels should be three known numbers. "
            "Keep the order fixed. Libraries differ, and OpenCV stores channels as blue, green, red by default, so "
            "hand-written examples that assume red first will disagree with library output unless the order is "
            "converted deliberately. For now stick to red, green, blue and state it in comments. The point of today is "
            "not colour theory but the nesting: an image is a grid of pixels, a pixel is a vector of channels, and "
            "every later operation either walks the grid, reads a channel, or replaces a pixel with a new triple."
        ),
        code=(
            'colour = [\n'
            '    [[255, 0, 0], [0, 255, 0]],\n'
            '    [[0, 0, 255], [255, 255, 255]],\n'
            ']\n'
            '\n'
            'print("height:", len(colour), "width:", len(colour[0]))\n'
            'print("channels:", len(colour[0][0]))\n'
            'for row in colour:\n'
            '    print([tuple(px) for px in row])\n'
            'print("bottom-right pixel:", colour[1][1])\n'
            'print("red channel of top-left:", colour[0][0][0])\n'
            '\n'
            'assert len(colour[0][0]) == 3\n'
            'assert colour[1][0][2] == 255\n'
            'print("a pixel is a short row of channel values")'
        ),
        variant_b="swap to blue, green, red order and adjust the printed labels to match",
        variant_c="write `channel(image, index)` returning one channel as a grayscale grid",
        mistakes=[
            "Losing track of nesting and applying a channel operation to a whole row.",
            "Mixing red-first and blue-first data in the same function without converting.",
            "Treating a colour pixel as a single number when indexing.",
        ],
        q1=(
            "What does `image[r][c][1]` select in a red-green-blue colour image?",
            "The green channel value of the pixel at row r and column c, because the third index selects within the channel triple.",
        ),
        homework=(
            "Write `channels(image)` that prints the height, width and channel count, then prints every pixel as a "
            "tuple. Run it on a 2x2 colour image and comment which index chooses the channel. Assert that `channels` "
            "reports three channels and print the grid."
        ),
        patterns=["def ", "len(", "print("],
        mapping=(
            "OpenCV channels arrive as blue, green, red, while torchvision tensors use channel-first layout; the "
            "nesting is the same even when the order and axis position change."
        ),
    ),
    77: dict(
        topic="Shapes and axes",
        idea=(
            "Shapes and axes describe where you are in the nested structure. For a list of rows the shape is a pair, "
            "rows then columns, and rows are the vertical axis while columns are the horizontal axis. A grayscale "
            "image has shape height by width; a colour image adds a third axis for channels. When code sums over an "
            "axis, the axis number selects which nesting level is collapsed. Summing over rows produces one value per "
            "column, while summing over columns produces one value per row. Getting this wrong usually produces a "
            "result of the right type but the wrong orientation, which is hard to spot on a tiny example and "
            "expensive later. Two habits prevent it. First, print the shape before operating and again after, and "
            "check that only the intended dimension changed. Second, name variables `height`, `width` and `channels` "
            "rather than `x`, `y` and `z`, so a loop reads as what it means. Transposing an image swaps rows and "
            "columns, and it is a good test of whether you understand the axes because the shape reverses and every "
            "pixel moves. Today you compute row sums, column sums and the overall total, then assert the shape. Those "
            "tiny aggregates confirm the orientation of the data before you build anything more ambitious on top."
        ),
        code=(
            'image = [\n'
            '    [1, 2, 3],\n'
            '    [4, 5, 6],\n'
            ']\n'
            '\n'
            'shape = (len(image), len(image[0]))\n'
            'print("shape (rows, cols):", shape)\n'
            'print("row sums:", [sum(row) for row in image])\n'
            'print("column sums:", [sum(col) for col in zip(*image)])\n'
            'print("total:", sum(sum(row) for row in image))\n'
            'print("transpose:", [list(col) for col in zip(*image)])\n'
            '\n'
            'assert shape == (2, 3)\n'
            'assert [sum(col) for col in zip(*image)] == [5, 7, 9]\n'
            'print("axis 0 walks rows, axis 1 walks columns")'
        ),
        variant_b="add a third row and predict the new shape and column sums before running",
        variant_c="write `shape(image)` and `transpose(image)` and assert the shape swaps",
        mistakes=[
            "Confusing the row count with the column count when reporting a shape.",
            "Summing the wrong axis and getting a result with the wrong orientation.",
            "Assuming a rectangular grid instead of checking every row length.",
        ],
        q1=(
            "What shape does a list of three rows of four values report?",
            "Three by four, as rows first and columns second, so the pair is (3, 4).",
        ),
        homework=(
            "Write `shape(image)` returning the row and column counts, plus `row_sums(image)` and `column_sums(image)`. "
            "Run all three on a 3x3 grid, print the results, and comment which loop collapses the row axis."
        ),
        patterns=["def ", "zip(", "print("],
        mapping=(
            "NumPy and torch report colour shapes as height-width-channel or channel-height-width; knowing which "
            "axis you are collapsing is the same skill in both."
        ),
    ),
    78: dict(
        topic="Colour spaces",
        idea=(
            "Colour spaces are different coordinate systems for the same pixel. Red, green and blue is convenient for "
            "displays and cameras, but it mixes brightness with colour, so a change in lighting moves all three "
            "numbers at once. Hue, saturation and value separates them: hue is the colour family, saturation is how "
            "pure it is, and value is how bright. Converting between the two is pure arithmetic, and doing it by hand "
            "on a few pixels makes the meaning concrete. Hue is an angle from zero to 360 degrees, saturation and "
            "value run from zero to one. A pure red has hue zero and full saturation, a grey has zero saturation, and "
            "black has zero value. Two cautions. Conversion formulas assume values scaled to zero to one, so divide "
            "the byte values first. And hue wraps around, so red appears at both ends of the range. In practice you "
            "choose a space based on the question: RGB for display, HSV for colour thresholding under uneven light, "
            "and later spaces for perceptual distance. Today you convert a handful of tiny pixels from RGB to HSV and "
            "print both representations. The important outcome is that a colour space is a choice of coordinates, not "
            "a different image."
        ),
        code=(
            'import colorsys\n'
            '\n'
            'rgb = [\n'
            '    [[255, 0, 0], [0, 255, 0]],\n'
            '    [[0, 0, 255], [128, 128, 128]],\n'
            ']\n'
            '\n'
            'for row in rgb:\n'
            '    for r, g, b in row:\n'
            '        h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)\n'
            '        print((r, g, b), "-> hsv", (round(h * 360), round(s * 100), round(v * 100)))\n'
            '\n'
            'h, s, v = colorsys.rgb_to_hsv(1.0, 1.0, 1.0)\n'
            'assert (round(s), round(v)) == (0, 1)\n'
            'print("grey has zero saturation; hue is an angle")'
        ),
        variant_b="convert the same pixels from HSV back to RGB and compare with the originals",
        variant_c="print only the hue for each pixel and explain why grey has no meaningful hue",
        mistakes=[
            "Passing byte values directly into a formula that expects zero to one.",
            "Treating hue as a linear number when it wraps around at 360 degrees.",
            "Assuming every colour space separates brightness and colour the same way.",
        ],
        q1=(
            "What do the three HSV components describe?",
            "Hue is the colour family as an angle, saturation is purity, and value is brightness, so lighting changes mostly move value.",
        ),
        homework=(
            "Write `rgb_to_hsv(pixel)` that takes a red-green-blue triple of bytes and returns rounded hue, saturation "
            "and value. Apply it to a 2x2 colour image, print every result, and comment why the byte values are "
            "divided by 255 before conversion."
        ),
        patterns=["def ", "round(", "print("],
        mapping=(
            "`cv2.cvtColor` converts between RGB, HSV, LAB and other spaces; choosing HSV is how classical colour "
            "thresholding survives uneven lighting."
        ),
    ),
    79: dict(
        topic="Grayscale conversion",
        idea=(
            "Grayscale conversion collapses three channels into one number that represents perceived brightness. The "
            "naive approach averages red, green and blue equally, but human vision is much more sensitive to green, so "
            "an equal average makes green and blue look similarly bright when they are not. A standard weighting is "
            "0.299 red, 0.587 green and 0.114 blue. These are the classic luminance coefficients, and they produce a "
            "conversion that looks natural rather than washed out. The operation is per pixel and independent of "
            "neighbours, which makes it one of the easiest transformations to implement and test. Two details matter. "
            "Round the weighted sum to an integer, because fractional pixel values are awkward to print and compare, "
            "and clip if your inputs can exceed the byte range. Keep the weights together rather than scattering magic "
            "numbers through the code. Also record the formula you used, because a different weighting gives different "
            "downstream thresholds. Today you convert a tiny colour grid to grayscale with a double loop and print "
            "both. Compare a saturated colour with its grayscale value and notice that green maps much brighter than "
            "blue at equal input intensity. That single observation explains why grayscale is not a simple average."
        ),
        code=(
            'image = [\n'
            '    [[255, 0, 0], [0, 255, 0]],\n'
            '    [[0, 0, 255], [255, 255, 255]],\n'
            ']\n'
            '\n'
            'def to_gray(image):\n'
            '    out = []\n'
            '    for row in image:\n'
            '        gray_row = []\n'
            '        for r, g, b in row:\n'
            '            gray_row.append(round(0.299 * r + 0.587 * g + 0.114 * b))\n'
            '        out.append(gray_row)\n'
            '    return out\n'
            '\n'
            'gray = to_gray(image)\n'
            'for row in gray:\n'
            '    print(row)\n'
            '\n'
            'assert gray[0][0] == 76\n'
            'assert gray[0][1] == 150\n'
            'print("green is weighted far above blue")'
        ),
        variant_b="use an equal average and compare the green and blue values with the weighted result",
        variant_c="write `to_gray_pixel(pixel)` and apply it with a list comprehension instead of nested loops",
        mistakes=[
            "Averaging channels equally, which makes green and blue look equally bright.",
            "Forgetting to round, so printed values carry long floating point tails.",
            "Applying weights in the wrong channel order after converting to blue-green-red.",
        ],
        q1=(
            "Why is grayscale a weighted sum rather than a plain average?",
            "Human vision is more sensitive to green, so the weights approximate perceived brightness and the result looks natural.",
        ),
        homework=(
            "Write `to_gray(image)` that converts a 2x2 colour grid into integer grayscale values with the luminance "
            "weights. Print the result and comment which term dominates for a green pixel. Assert that pure green maps "
            "to 150 and pure red to 76."
        ),
        patterns=["def ", "for ", "round("],
        mapping=(
            "`cv2.cvtColor(..., cv2.COLOR_BGR2GRAY)` applies a similar luminance weighting, which is why channel order "
            "must be known before conversion."
        ),
    ),
    80: dict(
        topic="Nearest-neighbour resizing",
        idea=(
            "Nearest-neighbour resizing is the simplest way to change an image's dimensions: map each output pixel "
            "back to the nearest input pixel and copy its value. There is no interpolation and no blending, so edges "
            "stay hard and the result looks blocky when enlarged. That is a feature for some tasks, because it "
            "preserves exact values and never invents colours. The mapping is a scale factor. For each output row and "
            "column, divide by the factor and take the integer part; that indexes the source. The integer division is "
            "doing the real work, and it is worth checking the last row and column carefully, since a factor that does "
            "not divide evenly can leave the final output pixel pointing at the edge. Nearest-neighbour also works for "
            "shrinking, though it discards pixels and can alias fine patterns. Two habits help. Compute the output "
            "size first and assert it matches what you expect. Then print both grids and trace one output pixel back "
            "to its source by hand. Today you enlarge a two-by-two image to four-by-four and print each row. The "
            "result should look like each source pixel repeated in a two-by-two block. That repetition is the whole "
            "algorithm, and it makes the difference between resizing and interpolating obvious."
        ),
        code=(
            'image = [\n'
            '    [0, 100],\n'
            '    [200, 255],\n'
            ']\n'
            '\n'
            'def resize_nearest(image, factor):\n'
            '    height, width = len(image), len(image[0])\n'
            '    out = []\n'
            '    for r in range(height * factor):\n'
            '        row = []\n'
            '        for c in range(width * factor):\n'
            '            row.append(image[r // factor][c // factor])\n'
            '        out.append(row)\n'
            '    return out\n'
            '\n'
            'big = resize_nearest(image, 2)\n'
            'print("shape:", (len(big), len(big[0])))\n'
            'for row in big:\n'
            '    print(row)\n'
            '\n'
            'assert len(big) == 4 and len(big[0]) == 4\n'
            'assert big[1][3] == 100\n'
            'print("each source pixel becomes a block")'
        ),
        variant_b="shrink the same image by a factor of two and explain which pixels are discarded",
        variant_c="use a non-integer scale such as 1.5 and handle the output size with rounding",
        mistakes=[
            "Indexing the source with the output index instead of dividing by the scale.",
            "Letting the final row or column index run one past the source edge.",
            "Expecting smooth edges from a method that only copies existing values.",
        ],
        q1=(
            "Where does the output pixel at row 3 get its value when enlarging by two?",
            "From source row 3 // 2, which is row 1, because integer division maps output coordinates back to input.",
        ),
        homework=(
            "Write `resize_nearest(image, factor)` that returns an enlarged list of rows. Run it on a 2x2 image with "
            "factor 2, print the 4x4 result, and comment which expression performs the coordinate mapping. Assert the "
            "output shape."
        ),
        patterns=["def ", "//", "print("],
        mapping=(
            "OpenCV's `resize` with `INTER_NEAREST` does the same coordinate mapping; the other interpolation modes "
            "replace the copy with a weighted combination."
        ),
    ),
    81: dict(
        topic="Cropping and padding",
        idea=(
            "Cropping selects a rectangular region, while padding adds a border around the image. Both are index "
            "arithmetic, and both change the shape, so check the shape after each. A crop takes a starting row and "
            "column plus a height and width, then copies those pixels into a new grid. The usual slicing notation is "
            "half-open, so the end index is not included. Off-by-one errors here are easy because it is tempting to "
            "treat the end coordinate as inclusive. Padding is the reverse: allocate a larger grid, usually filled "
            "with zeros, then copy the original into an offset position. The offset is the border width. Padding "
            "matters because filters read neighbours, and pixels at the edge have no neighbours unless you provide "
            "some. Zero padding is simple but darkens edges; replicating the edge pixel is often more faithful. Today "
            "you crop a three-by-three grid to two-by-two and pad that crop back to four-by-four with a one-pixel zero "
            "border. Print both results and confirm the shape at each step. The exercise is deliberately small so "
            "every coordinate is visible. When a crop or pad looks wrong, the fastest diagnosis is to print the "
            "indices you used rather than the values, because the bug is almost always in the bounds, not in the data."
        ),
        code=(
            'image = [\n'
            '    [1, 2, 3],\n'
            '    [4, 5, 6],\n'
            '    [7, 8, 9],\n'
            ']\n'
            '\n'
            'def crop(image, top, left, height, width):\n'
            '    return [row[left:left + width] for row in image[top:top + height]]\n'
            '\n'
            'def pad(image, border):\n'
            '    width = len(image[0]) + 2 * border\n'
            '    out = [[0] * width for _ in range(border)]\n'
            '    for row in image:\n'
            '        out.append([0] * border + row + [0] * border)\n'
            '    out.extend([[0] * width for _ in range(border)])\n'
            '    return out\n'
            '\n'
            'small = crop(image, 0, 0, 2, 2)\n'
            'print("crop shape:", (len(small), len(small[0])))\n'
            'for row in small:\n'
            '    print(row)\n'
            'padded = pad(small, 1)\n'
            'print("padded shape:", (len(padded), len(padded[0])))\n'
            'for row in padded:\n'
            '    print(row)\n'
            '\n'
            'assert small == [[1, 2], [4, 5]]\n'
            'assert len(padded) == 4 and len(padded[0]) == 4\n'
            'print("crop slices, pad allocates and offsets")'
        ),
        variant_b="crop the centre pixel only and pad it with a two-pixel border",
        variant_c="replace zero padding with edge replication and compare the border values",
        mistakes=[
            "Treating the crop end coordinate as inclusive, which adds an extra row.",
            "Padding only the left and top edges so the output is not rectangular.",
            "Forgetting to offset the original when copying it into the padded grid.",
        ],
        q1=(
            "What is the difference between cropping and padding in terms of shape?",
            "Cropping makes the grid smaller by selecting a region, while padding makes it larger by adding a border around the data.",
        ),
        homework=(
            "Write `crop(image, top, left, height, width)` and `pad(image, border)`. Crop a 3x3 grid to 2x2, pad it "
            "back to 4x4 with zeros, print both and comment which slice excludes the end index. Assert both shapes."
        ),
        patterns=["def ", "len(", "print("],
        mapping=(
            "OpenCV crops with NumPy slicing and pads with `copyMakeBorder`, where border type chooses zeros, "
            "replication or reflection."
        ),
    ),
    82: dict(
        topic="Flipping and rotating",
        idea=(
            "Flipping and rotating are index remappings, not new pixel values. A horizontal flip reverses each row, so "
            "the left edge becomes the right edge and the shape is unchanged. A vertical flip reverses the order of "
            "the rows. A ninety-degree rotation is a transpose followed by a flip, and the shape swaps, so a wide "
            "image becomes tall. That shape change is the detail that catches people: they rotate the values but "
            "forget that the outer length and the inner length must exchange. Rotation by ninety degrees clockwise "
            "maps the first row to the last column, which is easier to reason about if you trace one corner "
            "explicitly. Flipping is its own inverse, while rotating four times returns the original. Two practical "
            "notes. Do not modify the input in place unless you intend to, because debugging is harder when the "
            "original disappears. And test with an asymmetric grid, since a symmetric one hides mistakes in the "
            "remapping. Today you flip a three-by-three image horizontally and rotate it clockwise, printing both. "
            "Pick a corner value, follow it through each operation, and confirm it lands where you predicted. That "
            "trace is a more reliable check than eyeballing the printed grid. Predict each move before you print."
        ),
        code=(
            'image = [\n'
            '    [1, 2, 3],\n'
            '    [4, 5, 6],\n'
            '    [7, 8, 9],\n'
            ']\n'
            '\n'
            'flipped = [row[::-1] for row in image]\n'
            'rotated = [list(col) for col in zip(*image[::-1])]\n'
            '\n'
            'print("horizontal flip:")\n'
            'for row in flipped:\n'
            '    print(row)\n'
            'print("clockwise rotation:")\n'
            'for row in rotated:\n'
            '    print(row)\n'
            '\n'
            'assert flipped[0] == [3, 2, 1]\n'
            'assert rotated == [[7, 4, 1], [8, 5, 2], [9, 6, 3]]\n'
            'print("a rotation swaps the shape; a flip does not")'
        ),
        variant_b="rotate counter-clockwise by reversing the transpose order and compare the corner values",
        variant_c="write `rotate_180(image)` and check it equals a horizontal flip plus a vertical flip",
        mistakes=[
            "Rotating values without swapping the output dimensions.",
            "Editing rows in place and then trying to reuse the original image.",
            "Testing on a symmetric grid, which hides incorrect index remapping.",
        ],
        q1=(
            "Why does a ninety-degree rotation change the image shape while a flip does not?",
            "Rows become columns, so the height and width exchange; a flip only reverses order along an existing axis.",
        ),
        homework=(
            "Write `flip_horizontal(image)` and `rotate_clockwise(image)`. Apply both to a 3x3 asymmetric grid, print "
            "each result, and comment which expression transposes the rows. Assert that rotation maps the top-left "
            "pixel to the top-right corner."
        ),
        patterns=["def ", "zip(", "print("],
        mapping=(
            "`cv2.flip` takes an axis code for horizontal, vertical or both, and `cv2.rotate` offers the same "
            "ninety-degree remappings with explicit output shapes."
        ),
    ),
    83: dict(
        topic="Brightness and contrast",
        idea=(
            "Brightness and contrast are the two simplest point operations. Brightness adds a constant to every pixel; "
            "contrast scales values around a midpoint, usually 128 for byte images. Both are applied per pixel, so "
            "they are easy to implement and easy to get wrong at the boundary. The midpoint matters: scaling around "
            "zero would darken everything, while scaling around 128 keeps mid-grey fixed and pushes values away from "
            "it. A contrast factor above one spreads values apart, and below one pulls them toward grey. After either "
            "operation the result can leave the valid range. Adding 40 to 250 gives 290, which is not a byte value, "
            "and scaling can produce negatives. Clip to zero and 255 after the arithmetic, not before, or the result "
            "will not match the intended formula. Round intermediate floats so printed values are stable. Today you "
            "apply a combined adjustment to a tiny grid and print the original and the result side by side. Include at "
            "least one pixel that would exceed the range so the clipping is visible. That pixel is the whole lesson: "
            "arithmetic on images is ordinary arithmetic, and validity is something you enforce explicitly rather than "
            "something the language guarantees. Check that every output is a legal byte."
        ),
        code=(
            'image = [\n'
            '    [40, 120, 200],\n'
            '    [250, 10, 128],\n'
            ']\n'
            '\n'
            'def adjust(value, brightness, contrast):\n'
            '    result = round((value - 128) * contrast + 128 + brightness)\n'
            '    return max(0, min(255, result))\n'
            '\n'
            'def transform(image, brightness, contrast):\n'
            '    return [[adjust(v, brightness, contrast) for v in row] for row in image]\n'
            '\n'
            'print("original:")\n'
            'for row in image:\n'
            '    print(row)\n'
            'print("brightness 20, contrast 1.5:")\n'
            'for row in transform(image, 20, 1.5):\n'
            '    print(row)\n'
            '\n'
            'assert transform(image, 20, 1.5)[0][2] == 255\n'
            'print("contrast pivots around 128; clipping keeps values valid")'
        ),
        variant_b="lower the contrast to 0.5 and explain why values move toward mid-grey",
        variant_c="apply brightness only and find the pixel that saturates at 255",
        mistakes=[
            "Scaling contrast around zero instead of around the mid-grey value.",
            "Clipping before the arithmetic, which discards the intended offset.",
            "Forgetting that a brightness increase can saturate highlights.",
        ],
        q1=(
            "Why is contrast scaled around 128 rather than around zero?",
            "Scaling around zero shifts overall brightness; 128 keeps mid-grey fixed and spreads values away from it symmetrically.",
        ),
        homework=(
            "Write `adjust(value, brightness, contrast)` and `transform(image, brightness, contrast)`. Apply a "
            "brightness of 20 and contrast of 1.5 to a 2x3 grid, print both versions, and comment which line clamps "
            "the result. Assert that the brightest pixel becomes 255."
        ),
        patterns=["def ", "min(", "print("],
        mapping=(
            "OpenCV's `convertScaleAbs` expresses alpha as contrast and beta as brightness with saturation, which is "
            "the same formula with clipping built in."
        ),
    ),
    84: dict(
        topic="Histograms",
        idea=(
            "A histogram counts how many pixels have each value. For a byte grayscale image it has 256 buckets, and "
            "for a small example you only print the buckets that occur. The histogram is a compact summary of "
            "exposure: a cluster near zero means a dark image, a cluster near 255 means a bright one, and a narrow "
            "spike means low contrast. It throws away all spatial information, which is both its strength and its "
            "limitation. Two images with completely different content can share a histogram. Building one is a loop "
            "and a dictionary, or a list of fixed length if the range is known. The fixed list is usually better "
            "because indexing is direct and missing values read as zero. Use the same bucket width consistently, and "
            "state whether values are zero to 255 or zero to one. For colour images you either build three histograms "
            "or convert to grayscale first; do not mix channels in one count without saying so. Today you count values "
            "in a tiny grid, print each value with its frequency, and identify the most common one. Check that the "
            "frequencies sum to the number of pixels. That sum is a cheap invariant that catches lost or double-counted "
            "pixels immediately."
        ),
        code=(
            'image = [\n'
            '    [0, 50, 50],\n'
            '    [100, 100, 100],\n'
            '    [200, 255, 255],\n'
            ']\n'
            '\n'
            'def histogram(image):\n'
            '    counts = {}\n'
            '    for row in image:\n'
            '        for value in row:\n'
            '            counts[value] = counts.get(value, 0) + 1\n'
            '    return counts\n'
            '\n'
            'hist = histogram(image)\n'
            'for value in sorted(hist):\n'
            '    print(value, "->", hist[value])\n'
            'print("pixels counted:", sum(hist.values()))\n'
            'print("most common:", max(hist, key=hist.get))\n'
            '\n'
            'assert sum(hist.values()) == 9\n'
            'assert hist[100] == 3\n'
            'print("frequencies must sum to the pixel count")'
        ),
        variant_b="use a 256-element list instead of a dictionary and print only non-zero buckets",
        variant_c="build three histograms for a colour image and compare their totals",
        mistakes=[
            "Letting the counts sum to more or fewer pixels than the image contains.",
            "Mixing colour channels into one histogram without recording the order.",
            "Comparing histograms built with different bucket widths or ranges.",
        ],
        q1=(
            "What invariant should always hold for a grayscale histogram's counts?",
            "Their total must equal the number of pixels, because every pixel contributes to exactly one bucket.",
        ),
        homework=(
            "Write `histogram(image)` returning a dictionary from value to count. Run it on a 3x3 grid, print each "
            "non-zero bucket in sorted order, and comment which line increments a count. Assert that the frequencies "
            "sum to nine."
        ),
        patterns=["def ", "get(", "print("],
        mapping=(
            "`cv2.calcHist` and `numpy.histogram` build the same counts, and histogram equalisation uses them to "
            "remap intensities for contrast."
        ),
    ),
    85: dict(
        topic="Normalisation and ranges",
        idea=(
            "Normalisation rescales values into a chosen range, usually zero to 255 for display or zero to one for "
            "arithmetic. Min-max normalisation subtracts the minimum and divides by the spread, so the darkest pixel "
            "becomes zero and the brightest becomes the maximum. If every pixel has the same value the spread is zero, "
            "so that case needs an explicit guard. Normalisation changes contrast but not the relative ordering of "
            "pixels, and it is not the same as standardisation, which subtracts the mean and divides by the standard "
            "deviation. Keep the original minimum and maximum if you need to invert the transform, because information "
            "is lost when the range is clipped. Two details matter in practice. Work in floats during the calculation "
            "and round only when printing or when converting back to bytes. And decide whether the target range is "
            "inclusive, since dividing by 255 and by 254 give slightly different results. Today you normalise a tiny "
            "grid whose values occupy a narrow band and print both versions. Notice that the ordering is unchanged "
            "while the spread is larger. That is exactly what normalisation is for: making a low-contrast sample "
            "easier to threshold without pretending it contains more detail than it does."
        ),
        code=(
            'image = [\n'
            '    [10, 20],\n'
            '    [30, 40],\n'
            ']\n'
            '\n'
            'def normalise(image, high=255):\n'
            '    values = [v for row in image for v in row]\n'
            '    low, top = min(values), max(values)\n'
            '    if top == low:\n'
            '        return [[0 for _ in row] for row in image]\n'
            '    return [[round((v - low) * high / (top - low)) for v in row] for row in image]\n'
            '\n'
            'scaled = normalise(image)\n'
            'print("original:")\n'
            'for row in image:\n'
            '    print(row)\n'
            'print("normalised to 0-255:")\n'
            'for row in scaled:\n'
            '    print(row)\n'
            '\n'
            'assert scaled == [[0, 85], [170, 255]]\n'
            'print("min becomes 0, max becomes 255, order is preserved")'
        ),
        variant_b="normalise to the range zero to one and print rounded floats",
        variant_c="pass a constant image and confirm the zero-spread guard returns zeros",
        mistakes=[
            "Dividing by the maximum instead of by the spread between minimum and maximum.",
            "Ignoring the constant-image case and dividing by zero.",
            "Rounding before the final scaling step, which loses precision.",
        ],
        q1=(
            "What happens to relative pixel ordering under min-max normalisation?",
            "It is preserved; only the scale and offset change, so darker stays darker and brighter stays brighter.",
        ),
        homework=(
            "Write `normalise(image, high=255)` that rescales a grid by its minimum and maximum, with a guard for a "
            "constant image. Run it on a 2x2 low-contrast grid, print both versions, and comment which line computes "
            "the spread. Assert the smallest becomes zero."
        ),
        patterns=["def ", "min(", "print("],
        mapping=(
            "Deep-learning pipelines normalise to zero to one or to a dataset mean and deviation; the same spread "
            "calculation appears in torchvision transforms."
        ),
    ),
    86: dict(
        topic="Pixel data types",
        idea=(
            "Pixel data types determine what arithmetic means. The usual storage type for an image is an unsigned "
            "eight-bit integer, which holds zero to 255 and wraps around on overflow. That wrapping is the source of "
            "many strange results: brightening a value of 250 by 10 can produce 4 rather than 255, because the type "
            "does not saturate. Python integers do not wrap, so a hand-written example behaves differently from a "
            "library unless you simulate the range yourself. Floating point has the opposite issue: it represents "
            "fractions and can grow beyond the byte range, but it cannot represent every decimal exactly, so "
            "comparisons need tolerance. When you convert a float back to an integer, decide between truncation and "
            "rounding, because they differ by one and that difference propagates. Two habits pay off. Keep the data "
            "type explicit in variable names or comments, and check the range at the boundaries of every stage. Today "
            "you take a few values, show integer and float division, and demonstrate wrap versus clip for a value "
            "above 255. The lesson is that the same numbers mean different things under different types, and vision "
            "code is full of silent conversions that deserve a deliberate choice. Name the type, then choose the range."
        ),
        code=(
            'values = [250, 255, 260]\n'
            '\n'
            'print("values:", values)\n'
            'print("types:", [type(v).__name__ for v in values])\n'
            'print("scaled floats:", [round(v / 255, 3) for v in values])\n'
            'print("uint8-style wrap:", [v % 256 for v in values])\n'
            'print("clipped:", [min(255, max(0, v)) for v in values])\n'
            'print("integer division 7 // 2:", 7 // 2)\n'
            'print("float division 7 / 2:", 7 / 2)\n'
            '\n'
            'assert [v % 256 for v in values] == [250, 255, 4]\n'
            'assert [min(255, v) for v in values] == [250, 255, 255]\n'
            'print("byte range must be enforced explicitly")'
        ),
        variant_b="compare truncation and rounding when converting 127.6 back to an integer",
        variant_c="simulate an eight-bit clip after every step of a short brightness calculation",
        mistakes=[
            "Assuming Python integer arithmetic wraps like an eight-bit image buffer.",
            "Comparing floats for exact equality after repeated arithmetic.",
            "Truncating when rounding was intended, shifting values by one.",
        ],
        q1=(
            "Why can brightening 250 by 10 produce 4 in a real image buffer?",
            "An unsigned eight-bit type wraps on overflow, so 260 modulo 256 is 4 unless the value is clipped first.",
        ),
        homework=(
            "Write `wrap_byte(value)` and `clip_byte(value)` to model eight-bit overflow and saturation. Run both on "
            "values 250, 255 and 260, print every result, and comment which function matches a display buffer. Assert "
            "that wrapping 260 gives 4."
        ),
        patterns=["def ", "%", "print("],
        mapping=(
            "NumPy arrays default to uint8 for images, so `img + 10` wraps while `cv2.add` saturates; knowing the "
            "type explains the difference."
        ),
    ),
    87: dict(
        topic="Clipping and saturation",
        idea=(
            "Clipping and saturation are what keep arithmetic inside the valid range. Clipping replaces any value "
            "below the minimum with the minimum and any value above the maximum with the maximum. Saturation is the "
            "same idea described from the other side: a sensor or a display has saturated when it can no longer "
            "represent a brighter value, so detail is lost in the highlights. In code, clipping is two comparisons per "
            "value, and it should happen after the full calculation rather than between steps unless the intermediate "
            "range matters. There is a real difference between clipping and wrapping, and confusing them produces "
            "dramatic artefacts. Clipping preserves ordering; wrapping turns the brightest values into dark ones. For "
            "colour images clip each channel independently, which can shift hue when one channel clips earlier than "
            "the others; that shift is a genuine effect, not a bug. Two practical notes. Keep the limits as named "
            "parameters so a different bit depth can reuse the function. And test with values on both sides of the "
            "range, including exactly the boundary. Today you clip a list containing negative and oversized values and "
            "print the result. Then apply a strong brightness increase to a tiny image and observe which pixels "
            "flatten at 255. That flattening is saturation made visible."
        ),
        code=(
            'def clip(value, low=0, high=255):\n'
            '    return max(low, min(high, value))\n'
            '\n'
            'values = [-20, 0, 100, 280]\n'
            'print("input:", values)\n'
            'print("clipped:", [clip(v) for v in values])\n'
            '\n'
            'image = [\n'
            '    [200, 240],\n'
            '    [250, 300],\n'
            ']\n'
            'brightened = [[clip(v + 40) for v in row] for row in image]\n'
            'print("brightened by 40:")\n'
            'for row in brightened:\n'
            '    print(row)\n'
            '\n'
            'assert clip(-20) == 0 and clip(280) == 255\n'
            'assert brightened[0][1] == 255\n'
            'print("clipped pixels flatten instead of wrapping")'
        ),
        variant_b="remove the clip and print the raw sums to see values outside zero to 255",
        variant_c="clip a colour pixel channel by channel and check whether the hue shifts",
        mistakes=[
            "Wrapping instead of clipping, which turns highlights into dark values.",
            "Clipping before adding brightness, so the offset is thrown away.",
            "Sharing one channel's limit across channels with different ranges.",
        ],
        q1=(
            "What is the visible difference between clipping and wrapping an oversized pixel?",
            "Clipping holds the value at the maximum so highlights flatten, while wrapping sends it back near zero and creates dark artefacts.",
        ),
        homework=(
            "Write `clip(value, low=0, high=255)` and `brighten(image, amount)` that clips after adding. Apply a "
            "40-level increase to a 2x2 image containing an oversized value, print the result, and comment which "
            "pixels saturate. Assert that no output exceeds 255."
        ),
        patterns=["def ", "min(", "max("],
        mapping=(
            "OpenCV saturating arithmetic and PyTorch's `clamp` express clipping directly; knowing where it happens "
            "prevents highlight artefacts."
        ),
    ),
    88: dict(
        topic="Synthetic images versus real ones",
        idea=(
            "Synthetic images are generated by a rule, so they are exact, repeatable and cheap to reason about. A "
            "gradient sets each pixel from its column index, a checkerboard sets it from the parity of row plus "
            "column, and a constant image sets every pixel to the same value. Because you know the rule, you can "
            "assert the exact expected output, which makes synthetic images excellent tests for resizing, filtering "
            "and thresholding. Real images are different in ways that matter: they contain noise, uneven "
            "illumination, compression artefacts and content you did not choose. A pipeline that works on a clean "
            "gradient may fail on a photograph for reasons that have nothing to do with the algorithm. The honest "
            "approach is to develop on synthetic data where the expected result is provable, then test on real data "
            "where the result is merely plausible. Two cautions. Do not let a synthetic example become the only test, "
            "and do not tune parameters to one real image either. Today you build a checkerboard and a gradient with "
            "loops, print them, and count how many distinct values each contains. The count confirms the rule. Notice "
            "that the checkerboard has two values and the gradient has many, and think about which one is a better "
            "test for an edge detector."
        ),
        code=(
            'def checkerboard(size, low=0, high=255):\n'
            '    return [[high if (r + c) % 2 == 0 else low for c in range(size)] for r in range(size)]\n'
            '\n'
            'def gradient(height, width):\n'
            '    return [[round(c * 255 / (width - 1)) for c in range(width)] for _ in range(height)]\n'
            '\n'
            'board = checkerboard(4)\n'
            'ramp = gradient(2, 4)\n'
            '\n'
            'print("checkerboard:")\n'
            'for row in board:\n'
            '    print(row)\n'
            'print("gradient:")\n'
            'for row in ramp:\n'
            '    print(row)\n'
            'print("distinct board values:", len({v for row in board for v in row}))\n'
            'print("distinct ramp values:", len({v for row in ramp for v in row}))\n'
            '\n'
            'assert board[0][0] == 255 and board[0][1] == 0\n'
            'assert ramp[0] == [0, 85, 170, 255]\n'
            'print("synthetic images make exact assertions possible")'
        ),
        variant_b="generate a vertical gradient and check that every row is identical",
        variant_c="make a checkerboard with three intensities and explain why it is still deterministic",
        mistakes=[
            "Testing only on synthetic data and assuming the pipeline transfers to photographs.",
            "Hard-coding sizes that do not match the generated rule, causing index errors.",
            "Tuning a threshold to one real image and calling it general.",
        ],
        q1=(
            "Why are synthetic images useful tests even though they are not photographs?",
            "Their generating rule gives an exact expected output, so assertions prove the code rather than a visual impression.",
        ),
        homework=(
            "Write `checkerboard(size, low, high)` and `gradient(height, width)`. Print both grids, count their "
            "distinct values, and comment which line encodes the parity rule. Assert one known corner of the board "
            "and the first ramp row."
        ),
        patterns=["def ", "for ", "print("],
        mapping=(
            "Test suites for vision code generate synthetic arrays to assert exact behaviour, then reserve real "
            "datasets for evaluating robustness."
        ),
    ),
    89: dict(
        topic="Review: images as arrays checklist",
        idea=(
            "Today is a checklist day: run through the core ideas and confirm each one with a tiny assertion. Can you "
            "state the shape of a list-of-rows image and index a pixel without hesitating? Can you convert a colour "
            "pixel to grayscale, and explain why the weights are not equal? Can you crop, pad, flip and rotate while "
            "keeping the shape correct? Can you adjust brightness and contrast and then clip to the valid range? Can "
            "you build a histogram and check that its counts sum to the pixel count? Can you normalise a narrow range "
            "and explain what is preserved? Can you describe what an eight-bit type does on overflow, and why clipping "
            "differs from wrapping? Can you generate a synthetic image from a rule and predict its values? These "
            "questions cover the vocabulary the rest of the course assumes. The review is deliberately practical: for "
            "each item, write a few lines and an assertion rather than rereading notes. If an item takes more than a "
            "minute, that is the one to revisit. Today's example runs a small end-to-end check over a colour image, "
            "printing shape, grayscale values, the value range and a histogram total. Treat the printed summary as a "
            "template for your own sanity checks before any larger experiment."
        ),
        code=(
            'image = [\n'
            '    [[255, 0, 0], [0, 255, 0]],\n'
            '    [[0, 0, 255], [255, 255, 255]],\n'
            ']\n'
            '\n'
            'gray = [[round(0.299*r + 0.587*g + 0.114*b) for r, g, b in row] for row in image]\n'
            'values = [v for row in gray for v in row]\n'
            'low, high = min(values), max(values)\n'
            'scaled = [[round((v - low) * 255 / (high - low)) for v in row] for row in gray]\n'
            'counts = {}\n'
            'for row in scaled:\n'
            '    for v in row:\n'
            '        counts[v] = counts.get(v, 0) + 1\n'
            '\n'
            'print("shape:", (len(image), len(image[0]), len(image[0][0])))\n'
            'print("gray:", gray)\n'
            'print("range:", (low, high), "scaled range:", (min(v for r in scaled for v in r), 255))\n'
            'print("histogram total:", sum(counts.values()))\n'
            'print("checklist: shape, gray, range, histogram")\n'
            '\n'
            'assert sum(counts.values()) == 4\n'
            'assert scaled[1][0] == 0 and scaled[1][1] == 255\n'
            'print("all invariants hold")'
        ),
        variant_b="add a flip and a crop to the checklist and assert their shapes",
        variant_c="run the same summary on a 3x3 image and confirm the histogram total changes",
        mistakes=[
            "Rereading notes instead of writing assertions that prove each idea.",
            "Skipping the histogram total check, which catches lost pixels.",
            "Treating a pass on one tiny grid as proof for non-square images.",
        ],
        q1=(
            "What should you check after any image transformation?",
            "The output shape and value range, plus an invariant such as histogram total or a known pixel value.",
        ),
        homework=(
            "Write `summary(image)` that prints shape, grayscale values, the value range and the histogram total, then "
            "asserts the total equals the pixel count. Run it on a 2x2 colour image, print the summary, and comment "
            "which assertion catches a lost pixel."
        ),
        patterns=["def ", "assert", "print("],
        mapping=(
            "The checklist mirrors the sanity checks used before feeding arrays to OpenCV or a torchvision model: "
            "shape, range, channel order and counts."
        ),
    ),
})
