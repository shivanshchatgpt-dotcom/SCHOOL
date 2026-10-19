"""Computer Vision filtering and edges, days 90-104: convolution, gradients and morphology.

Every example is stdlib-only, offline and deterministic: an image is a nested
list of pixel values and every operation is an explicit loop over that list.
The kernels, gradient magnitudes, suppression rule and morphology counts are all
asserted on tiny grids, so the phase runs without OpenCV, a camera or a file.
"""

PHASE = (
    "Filtering and Edges",
    "Read, build and reason about convolution kernels, gradients and morphology on tiny image grids.",
    {
        90: dict(
            topic="Orientation: local operations",
            idea=(
                "Every operation so far acted on one pixel at a time: brightening, grayscale conversion and "
                "thresholding all decided each output from the same input pixel and nothing else. This phase "
                "changes that. A local operation computes each output pixel from a small neighbourhood around "
                "the corresponding input pixel, so the result depends on position and context rather than one "
                "value. The neighbourhood is usually a square of odd size, three by three being the workhorse, "
                "centred on the pixel being produced. Two concepts follow immediately. The first is the radius: "
                "a three-by-three neighbourhood reaches one pixel in every direction, a five-by-five reaches "
                "two, and the cost of an operation grows with the square of the radius. The second is the "
                "border, where the neighbourhood falls off the image and you must decide whether to shrink the "
                "output, pad with zeros or replicate edge pixels; each choice changes the result and must be "
                "deliberate. Local operations are where vision stops being arithmetic and starts being useful, "
                "because texture, edges and denoising are all properties of neighbourhoods, not pixels. Today "
                "you extract a three-by-three neighbourhood from the centre of a small image, print it and "
                "compute its mean, then compare that local mean with the global mean over the whole grid."
            ),
            code=(
                'IMAGE = [\n'
                '    [10, 20, 30, 40, 50],\n'
                '    [60, 70, 80, 90, 100],\n'
                '    [110, 120, 130, 140, 150],\n'
                '    [160, 170, 180, 190, 200],\n'
                '    [210, 220, 230, 240, 250],\n'
                ']\n'
                '\n'
                'def neighbourhood(image, row, col):\n'
                '    return [[image[r][c] for c in range(col - 1, col + 2)]\n'
                '            for r in range(row - 1, row + 2)]\n'
                '\n'
                'def local_mean(image, row, col):\n'
                '    block = neighbourhood(image, row, col)\n'
                '    return round(sum(sum(r) for r in block) / 9, 2)\n'
                '\n'
                'print("centre pixel:", IMAGE[2][2])\n'
                'for row in neighbourhood(IMAGE, 2, 2):\n'
                '    print(row)\n'
                'print("local mean at (2,2):", local_mean(IMAGE, 2, 2))\n'
                'print("global mean:", round(sum(sum(r) for r in IMAGE) / 25, 2))\n'
                '\n'
                'assert local_mean(IMAGE, 2, 2) == 130.0\n'
                'assert local_mean(IMAGE, 1, 1) == 70.0\n'
                'print("local operations read a neighbourhood, not one pixel")\n'
            ),
            variant_b="use a five-by-five neighbourhood and compare its mean with the three-by-three mean",
            variant_c="print the neighbourhood at a corner and explain why its mean is undefined without padding",
            mistakes=[
                "Treating a local operation as per-pixel and forgetting the neighbourhood entirely.",
                "Computing a neighbourhood that runs off the image instead of choosing a border rule.",
                "Mixing up the row and column offsets, so the window is not centred on the pixel.",
            ],
            q1=(
                "What makes an operation local rather than per-pixel?",
                "A local operation reads a neighbourhood around the input pixel, so its output depends on nearby values, not just the one pixel under it.",
            ),
            homework=(
                "Write `neighbourhood(image, row, col)` returning the three-by-three block around a pixel, and "
                "`local_mean(image, row, col)` returning its rounded mean. Run them on a five-by-five image, "
                "print one block and the local and global means, and comment which line picks the window."
            ),
            patterns=["def ", "range(", "print("],
            mapping=(
                "OpenCV's `filter2D`, `blur` and `GaussianBlur` all take a kernel or window size and apply it "
                "locally; the border mode is exactly the padding choice here."
            ),
        ),
        91: dict(
            topic="The convolution kernel",
            idea=(
                "A convolution kernel is a small grid of weights that defines a filter completely. To compute "
                "one output pixel, place the kernel over the input so its centre sits on the pixel, multiply "
                "every weight by the input value underneath it, and add the products. Sliding that same kernel "
                "across the image produces the whole filtered result. The kernel's size is its reach: a "
                "three-by-three kernel sees nine input pixels, a five-by-five sees twenty-five, and the "
                "arithmetic grows accordingly. Two properties deserve attention. First, the sum of the weights "
                "sets the brightness behaviour. An averaging kernel whose weights sum to one preserves overall "
                "brightness, while a kernel summing to zero responds only to change and produces dark output on "
                "flat regions, which is why edge kernels look the way they do. Second, the sign and arrangement "
                "of the weights encode direction and purpose: swapping rows for columns turns a horizontal "
                "detector into a vertical one. Convolution also has to define its centre, since an even-sized "
                "kernel has no middle element, which is why practical kernels use odd sizes. Today you implement "
                "a general three-by-three convolution that skips the border, then apply an identity kernel, "
                "which returns the input unchanged, and a cross kernel that sums the four neighbours. Comparing "
                "the two outputs shows that the numbers alone decide the operation."
            ),
            code=(
                'IMAGE = [\n'
                '    [0, 0, 10, 10],\n'
                '    [0, 0, 10, 10],\n'
                '    [20, 20, 30, 30],\n'
                '    [20, 20, 30, 30],\n'
                ']\n'
                '\n'
                'def convolve(image, kernel):\n'
                '    offset = len(kernel) // 2\n'
                '    h, w = len(image), len(image[0])\n'
                '    out = [[0] * (w - 2 * offset) for _ in range(h - 2 * offset)]\n'
                '    for r in range(offset, h - offset):\n'
                '        for c in range(offset, w - offset):\n'
                '            total = 0\n'
                '            for kr, krow in enumerate(kernel):\n'
                '                for kc, weight in enumerate(krow):\n'
                '                    total += weight * image[r + kr - offset][c + kc - offset]\n'
                '            out[r - offset][c - offset] = total\n'
                '    return out\n'
                '\n'
                'identity = [[0, 0, 0], [0, 1, 0], [0, 0, 0]]\n'
                'cross = [[0, 1, 0], [1, 0, 1], [0, 1, 0]]\n'
                'print("identity:", convolve(IMAGE, identity))\n'
                'print("cross sums:", convolve(IMAGE, cross))\n'
                '\n'
                'assert convolve(IMAGE, identity) == [[0, 10], [20, 30]]\n'
                'assert convolve(IMAGE, cross) == [[30, 50], [70, 90]]\n'
                'print("the kernel weights decide the operation")\n'
            ),
            variant_b="rotate the cross kernel ninety degrees and check whether the output changes",
            variant_c="scale a kernel by two and explain why the output values double without any code change",
            mistakes=[
                "Reading the kernel upside down, so the result is mirrored in the wrong direction.",
                "Forgetting to skip the border, so the output is offset by one pixel from the input.",
                "Confusing the kernel size with the number of multiplications per pixel.",
            ],
            q1=(
                "What do the numbers in a convolution kernel actually specify?",
                "The weight applied at each neighbourhood position; changing them changes the operation, from blur to sharpen to edge detection.",
            ),
            homework=(
                "Write `convolve(image, kernel)` for three-by-three kernels, skipping the border. Apply an "
                "identity kernel and a cross kernel to a four-by-four image, print both results, and comment "
                "which line performs the multiply and accumulate."
            ),
            patterns=["def ", "for ", "print("],
            mapping=(
                "OpenCV's `filter2D` applies an arbitrary kernel exactly like this, and a CNN's convolutional "
                "layer is the same multiply-and-accumulate with learned weights."
            ),
        ),
        92: dict(
            topic="Box blur",
            idea=(
                "A box blur replaces each pixel with the average of its neighbourhood, and because every "
                "neighbour gets equal weight it is the simplest real filter. The kernel is a grid of ones, and "
                "dividing the weighted sum by the number of cells keeps the result in the original range. Two "
                "effects follow from averaging. Noise is reduced, because independent random deviations in a "
                "neighbourhood partly cancel, and detail is softened, because an edge is spread across the "
                "whole window. The trade-off is the whole story of blurring: the larger the window, the more "
                "noise is suppressed and the more genuine structure is destroyed. Borders need a decision, and "
                "the file skips the outermost ring so every output pixel has a complete neighbourhood; that "
                "shrinks the image by one pixel on each side, which must be remembered when coordinates are "
                "reused later. The box blur is also cheap: with a fixed window each output is a constant number "
                "of additions, and the sum can be computed from the previous one by subtracting the outgoing "
                "column and adding the incoming one, an optimisation called a running sum. Today you average a "
                "five-by-five test image that contains a bright square, print the three-by-three result, and "
                "observe that the sharp boundary has become a gentle ramp of values. That smoothing is exactly "
                "what makes blur a preprocessing step for edge detection."
            ),
            code=(
                'IMAGE = [\n'
                '    [10, 10, 10, 10, 10],\n'
                '    [10, 90, 90, 90, 10],\n'
                '    [10, 90, 90, 90, 10],\n'
                '    [10, 90, 90, 90, 10],\n'
                '    [10, 10, 10, 10, 10],\n'
                ']\n'
                '\n'
                'def box_blur(image):\n'
                '    h, w = len(image), len(image[0])\n'
                '    out = [[0] * (w - 2) for _ in range(h - 2)]\n'
                '    for r in range(1, h - 1):\n'
                '        for c in range(1, w - 1):\n'
                '            total = 0\n'
                '            for dr in (-1, 0, 1):\n'
                '                for dc in (-1, 0, 1):\n'
                '                    total += image[r + dr][c + dc]\n'
                '            out[r - 1][c - 1] = round(total / 9, 2)\n'
                '    return out\n'
                '\n'
                'result = box_blur(IMAGE)\n'
                'for row in result:\n'
                '    print(row)\n'
                'print("centre before:", IMAGE[2][2], "after:", result[1][1])\n'
                '\n'
                'assert result[1][1] == 90.0\n'
                'assert result[0][0] == 45.56\n'
                'assert result[0][1] == 63.33\n'
                'print("a box blur averages each 3x3 neighbourhood")\n'
            ),
            variant_b="use a five-by-five box kernel and observe how much wider the ramp becomes",
            variant_c="divide by eight instead of nine and explain why the image gets brighter",
            mistakes=[
                "Forgetting to divide by the number of weights, so the image brightens at every position.",
                "Averaging a neighbourhood that runs off the image instead of skipping the border.",
                "Assuming a bigger window is always better, when it also erases real detail.",
            ],
            q1=(
                "Why does a box blur soften an edge as well as reduce noise?",
                "Averaging spreads each value across the whole window, so a sharp step becomes a gradual ramp while random noise partly cancels.",
            ),
            homework=(
                "Write `box_blur(image)` averaging each three-by-three neighbourhood and rounding to two "
                "places. Run it on a five-by-five image with a bright square, print the blurred grid, and "
                "comment which line divides by the number of weights."
            ),
            patterns=["def ", "round", "print("],
            mapping=(
                "`cv2.blur` is exactly this uniform average; comparing it with `cv2.GaussianBlur` shows why "
                "the weighted kernel usually looks better on real images."
            ),
        ),
        93: dict(
            topic="Gaussian weighting",
            idea=(
                "A gaussian blur is a weighted average in which the centre pixel counts most and distant "
                "neighbours count least, with weights following the bell curve. The standard three-by-three "
                "approximation is one, two, one across and down, whose outer product gives a kernel with four "
                "in the centre, two on the edges and one in the corners, summing to sixteen. Comparing it with "
                "the box blur on the same image shows the practical difference: a box averages a whole square, "
                "so an isolated bright pixel contaminates every neighbour equally, while a gaussian keeps the "
                "disruption local and concentrated near the source. That locality is why gaussian blur is the "
                "default smoothing filter before edge detection and why it looks natural on photographs. Two "
                "properties make it convenient. Separability means the two-dimensional kernel is the outer "
                "product of a one-dimensional one, so the expensive square of neighbours collapses into two "
                "cheap passes, which matters as the window grows. Normalisation, dividing by the weight sum, "
                "keeps brightness constant. The bell shape also introduces a parameter, the standard deviation, "
                "controlling width. Today you apply the one, two, one kernel to a small image containing a "
                "bright square and print the result, noting that the blurred edge is smoother and the centre "
                "stays closer to the original value than in the box blur."
            ),
            code=(
                'IMAGE = [\n'
                '    [10, 10, 10, 10, 10],\n'
                '    [10, 90, 90, 90, 10],\n'
                '    [10, 90, 90, 90, 10],\n'
                '    [10, 90, 90, 90, 10],\n'
                '    [10, 10, 10, 10, 10],\n'
                ']\n'
                'GAUSS = [[1, 2, 1], [2, 4, 2], [1, 2, 1]]\n'
                '\n'
                'def gaussian_blur(image):\n'
                '    h, w = len(image), len(image[0])\n'
                '    out = [[0] * (w - 2) for _ in range(h - 2)]\n'
                '    for r in range(1, h - 1):\n'
                '        for c in range(1, w - 1):\n'
                '            total = 0\n'
                '            for kr in range(3):\n'
                '                for kc in range(3):\n'
                '                    total += GAUSS[kr][kc] * image[r + kr - 1][c + kc - 1]\n'
                '            out[r - 1][c - 1] = round(total / 16, 2)\n'
                '    return out\n'
                '\n'
                'result = gaussian_blur(IMAGE)\n'
                'for row in result:\n'
                '    print(row)\n'
                'print("kernel weight sum:", sum(sum(row) for row in GAUSS))\n'
                '\n'
                'assert sum(sum(row) for row in GAUSS) == 16\n'
                'assert result[0][0] == 55.0\n'
                'assert result[0][1] == 70.0\n'
                'assert result[1][1] == 90.0\n'
                'print("a gaussian kernel weights the centre more than the corners")\n'
            ),
            variant_b="use [[1,1,1],[1,1,1],[1,1,1]] and compare the blurred values with the gaussian",
            variant_c="swap the kernel for [[1,0,1],[0,4,0],[1,0,1]] and describe how the weighting changed",
            mistakes=[
                "Forgetting to divide by the weight sum, so the blurred image is much too bright.",
                "Using an even-sized gaussian kernel that has no single centre pixel.",
                "Assuming a gaussian is just a box blur, when its locality is the point.",
            ],
            q1=(
                "Why is a gaussian kernel preferred over a box kernel before edge detection?",
                "It concentrates the blur near the source and follows the bell curve, so noise is reduced with less spreading of genuine edges.",
            ),
            homework=(
                "Write `gaussian_blur(image)` using the one, two, one weights and dividing by sixteen. Run it "
                "on a five-by-five image with a bright square, print the grid and the weight sum, and comment "
                "which line normalises the kernel."
            ),
            patterns=["def ", "for ", "print("],
            mapping=(
                "`cv2.GaussianBlur` takes a kernel size and a standard deviation, and its separable inner "
                "passes are the same two one-dimensional convolutions you build here."
            ),
        ),
        94: dict(
            topic="Sharpening",
            idea=(
                "Sharpening does the opposite of blurring: it increases the contrast between a pixel and its "
                "neighbours, emphasising edges and fine detail. The common kernel has a positive centre of five "
                "and negative weights of minus one in the four orthogonal neighbours, summing to one so average "
                "brightness is preserved. For a flat region the negatives cancel the centre and the output "
                "equals the input; near an edge the weighted sum overshoots, making the bright side brighter and "
                "the dark side darker. Overshoot is the point, but it also means the arithmetic can leave the "
                "valid range. A dark-to-bright step can produce a negative value and a bright-to-dark step a "
                "value above the maximum, so clipping back to zero-to-two-hundred-fifty-five is not optional. "
                "That clipping creates a subtle artefact called a halo, and pushing the centre weight higher "
                "exaggerates it, which is why sharpening is usually applied gently and after denoising rather "
                "than before: sharpening noise just makes the noise crisp. A more controllable alternative is "
                "unsharp masking, where a blurred copy is subtracted from the original and the difference is "
                "added back, scaled by an amount. Today you apply the five, minus-one kernel to a small image "
                "with a bright block, print both the raw and clipped results, and see the overshoot appear as "
                "the extremes of the valid range."
            ),
            code=(
                'IMAGE = [\n'
                '    [10, 10, 10, 10],\n'
                '    [10, 10, 10, 10],\n'
                '    [10, 200, 200, 10],\n'
                '    [10, 200, 200, 10],\n'
                ']\n'
                'SHARPEN = [[0, -1, 0], [-1, 5, -1], [0, -1, 0]]\n'
                '\n'
                'def convolve(image, kernel):\n'
                '    h, w = len(image), len(image[0])\n'
                '    out = [[0] * (w - 2) for _ in range(h - 2)]\n'
                '    for r in range(1, h - 1):\n'
                '        for c in range(1, w - 1):\n'
                '            total = 0\n'
                '            for kr in range(3):\n'
                '                for kc in range(3):\n'
                '                    total += kernel[kr][kc] * image[r + kr - 1][c + kc - 1]\n'
                '            out[r - 1][c - 1] = total\n'
                '    return out\n'
                '\n'
                'def clip(value):\n'
                '    return max(0, min(255, value))\n'
                '\n'
                'raw = convolve(IMAGE, SHARPEN)\n'
                'sharp = [[clip(v) for v in row] for row in raw]\n'
                'print("raw:", raw)\n'
                'print("clipped:", sharp)\n'
                'print("kernel sum:", sum(sum(row) for row in SHARPEN))\n'
                '\n'
                'assert sum(sum(row) for row in SHARPEN) == 1\n'
                'assert raw[0][0] == -180 and raw[1][0] == 580\n'
                'assert sharp == [[0, 0], [255, 255]]\n'
                'print("sharpening amplifies difference and must be clipped")\n'
            ),
            variant_b="use a centre weight of nine and describe where the halo would appear",
            variant_c="skip the clip function and explain what negative pixel values would do downstream",
            mistakes=[
                "Forgetting to clip, so sharpened values leave the zero-to-255 range.",
                "Sharpening before denoising, which amplifies the noise instead of the detail.",
                "Using a kernel whose weights do not sum to one, which shifts overall brightness.",
            ],
            q1=(
                "Why does a sharpening kernel need clipping after the convolution?",
                "Near an edge the weighted sum overshoots below zero or above 255, and the valid pixel range must be restored or later stages misbehave.",
            ),
            homework=(
                "Write `sharpen(image)` applying the five, minus-one kernel and `clip(value)` limiting it to "
                "zero-to-255. Run both on a four-by-four image with a bright block, print the raw and clipped "
                "grids, and comment which line restores the range."
            ),
            patterns=["def ", "max(", "print("],
            mapping=(
                "OpenCV's `filter2D` with a sharpen kernel or its `detailEnhance` works this way, and the "
                "unsharp-mask variant exists as `addWeighted(original, 1+a, blurred, -a, 0)`."
            ),
        ),
        95: dict(
            topic="Sobel edges",
            idea=(
                "Sobel edge detection uses two kernels that respond to intensity change in the horizontal and "
                "vertical directions. The horizontal kernel has negative weights on the left column and "
                "positive on the right, with a stronger pair in the middle row, so it returns a large value "
                "where brightness changes from left to right. The vertical kernel is its transpose. Applied to "
                "a flat region both return zero; applied across an edge the matching kernel returns a large "
                "magnitude whose sign encodes the direction of the change. The doubled middle weights are not "
                "arbitrary: they approximate a smoothing along the edge direction, which reduces the "
                "sensitivity to single-pixel noise that a bare difference would have. Two kernels together mean "
                "every pixel gets a pair of numbers, usually written gx and gy, and those numbers behave like "
                "components of a vector pointing in the direction of greatest change. The magnitude of that "
                "vector is the edge strength and its angle is the edge orientation. Working with integer "
                "kernels keeps the arithmetic exact, and the border is again skipped to avoid incomplete "
                "neighbourhoods. Today you convolve a small image with both kernels and print the two integer "
                "grids, seeing that a vertical edge lights up the horizontal kernel and leaves the vertical one "
                "silent. That pairing is the foundation of the next topic."
            ),
            code=(
                'IMAGE = [\n'
                '    [10, 10, 100, 100, 100],\n'
                '    [10, 10, 100, 100, 100],\n'
                '    [10, 10, 100, 100, 100],\n'
                '    [10, 10, 100, 100, 100],\n'
                '    [10, 10, 100, 100, 100],\n'
                ']\n'
                'SOBEL_X = [[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]]\n'
                'SOBEL_Y = [[-1, -2, -1], [0, 0, 0], [1, 2, 1]]\n'
                '\n'
                'def convolve(image, kernel):\n'
                '    h, w = len(image), len(image[0])\n'
                '    out = [[0] * (w - 2) for _ in range(h - 2)]\n'
                '    for r in range(1, h - 1):\n'
                '        for c in range(1, w - 1):\n'
                '            total = 0\n'
                '            for kr in range(3):\n'
                '                for kc in range(3):\n'
                '                    total += kernel[kr][kc] * image[r + kr - 1][c + kc - 1]\n'
                '            out[r - 1][c - 1] = total\n'
                '    return out\n'
                '\n'
                'gx = convolve(IMAGE, SOBEL_X)\n'
                'gy = convolve(IMAGE, SOBEL_Y)\n'
                'print("horizontal kernel:")\n'
                'for row in gx:\n'
                '    print(row)\n'
                'print("vertical kernel:")\n'
                'for row in gy:\n'
                '    print(row)\n'
                '\n'
                'assert gx[0] == [360, 360, 0]\n'
                'assert all(value == 0 for row in gy for value in row)\n'
                'print("sobel x responds to a vertical edge, y to a horizontal one")\n'
            ),
            variant_b="transpose the image so the edge is horizontal and watch which kernel responds",
            variant_c="use a diagonal edge and predict the signs of the two responses before running it",
            mistakes=[
                "Using only one kernel and missing edges that run in the other direction.",
                "Swapping the two kernels, so the reported direction is rotated by ninety degrees.",
                "Forgetting that the response is signed, so opposite edges can cancel if added directly.",
            ],
            q1=(
                "Why does Sobel use two kernels rather than one?",
                "One detects horizontal change and one vertical change, so together they give the full gradient direction instead of only axis-aligned edges.",
            ),
            homework=(
                "Write `sobel(image)` returning the horizontal and vertical response grids for three-by-three "
                "kernels. Run it on a five-by-five image with a vertical edge, print both grids, and comment "
                "which kernel responds to the edge."
            ),
            patterns=["def ", "for ", "print("],
            mapping=(
                "`cv2.Sobel(src, cv2.CV_64F, 1, 0)` computes exactly this horizontal response at a higher "
                "precision, and the pair of calls is the standard OpenCV edge setup."
            ),
        ),
        96: dict(
            topic="Gradient magnitude",
            idea=(
                "The two Sobel responses at a pixel form a vector, and the gradient magnitude is its length: "
                "the square root of gx squared plus gy squared. The magnitude answers how strong the change is "
                "without regard to its direction, which is exactly what an edge map needs. Because the "
                "components are signed, adding them would cancel changes of opposite direction; squaring removes "
                "the sign, and the square root returns the numbers to the original scale. Two practical notes "
                "apply. First, the square root is expensive on large images, so a common approximation is the "
                "sum of the absolute components, which is cheaper and monotonic with the true magnitude, so "
                "thresholding behaves almost the same. Second, the values can be much larger than the input "
                "range, because a strong edge in a kernel with weights summing to eight can multiply the "
                "contrast several times; the magnitude is a strength score, not a pixel, so it is compared "
                "against thresholds rather than displayed directly. The magnitude is also rotation-independent: "
                "a diagonal edge produces a similar response to an axis-aligned one of the same contrast, which "
                "is why Sobel detects edges in every direction. Today you compute gx and gy over a small "
                "corner-shaped image, combine them into a magnitude grid, and print the rounded values, checking "
                "that flat regions give near zero and the corner gives the largest response."
            ),
            code=(
                'IMAGE = [\n'
                '    [10, 10, 10, 10, 10],\n'
                '    [10, 10, 10, 10, 10],\n'
                '    [10, 10, 100, 100, 100],\n'
                '    [10, 10, 100, 100, 100],\n'
                '    [10, 10, 100, 100, 100],\n'
                ']\n'
                'SOBEL_X = [[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]]\n'
                'SOBEL_Y = [[-1, -2, -1], [0, 0, 0], [1, 2, 1]]\n'
                '\n'
                'def convolve(image, kernel):\n'
                '    h, w = len(image), len(image[0])\n'
                '    out = [[0] * (w - 2) for _ in range(h - 2)]\n'
                '    for r in range(1, h - 1):\n'
                '        for c in range(1, w - 1):\n'
                '            total = 0\n'
                '            for kr in range(3):\n'
                '                for kc in range(3):\n'
                '                    total += kernel[kr][kc] * image[r + kr - 1][c + kc - 1]\n'
                '            out[r - 1][c - 1] = total\n'
                '    return out\n'
                '\n'
                'def magnitude(gx, gy):\n'
                '    h, w = len(gx), len(gx[0])\n'
                '    return [[round((gx[r][c] ** 2 + gy[r][c] ** 2) ** 0.5, 2) for c in range(w)]\n'
                '            for r in range(h)]\n'
                '\n'
                'gx = convolve(IMAGE, SOBEL_X)\n'
                'gy = convolve(IMAGE, SOBEL_Y)\n'
                'mag = magnitude(gx, gy)\n'
                'for row in mag:\n'
                '    print(row)\n'
                '\n'
                'assert mag[0][0] == 127.28\n'
                'assert mag[0][2] == 360.0\n'
                'assert mag[1][1] == 381.84\n'
                'print("gradient magnitude is the length of the (gx, gy) vector")\n'
            ),
            variant_b="use the absolute-sum approximation and compare it with the true magnitude",
            variant_c="scale one Sobel kernel by two and explain how the magnitude map changes",
            mistakes=[
                "Adding the signed components instead of combining their squares, so opposing edges cancel.",
                "Treating the magnitude as a pixel value and clipping it to 255 for no reason.",
                "Forgetting the square root, which leaves the values on a squared scale that misleads thresholds.",
            ],
            q1=(
                "Why combine gx and gy by squaring rather than adding them?",
                "Both responses are signed, so adding would cancel changes of opposite direction; the Euclidean length keeps every edge positive and direction-free.",
            ),
            homework=(
                "Write `magnitude(gx, gy)` returning the square root of the summed squares, rounded to two "
                "places. Run it on the Sobel responses of a five-by-five corner image, print the magnitude "
                "grid, and comment which line removes the sign of the components."
            ),
            patterns=["def ", "** 0.5", "print("],
            mapping=(
                "OpenCV's `cv2.magnitude(gx, gy)` computes exactly this, and Canny internally builds the same "
                "magnitude from two Sobel responses."
            ),
        ),
        97: dict(
            topic="Thresholding edges",
            idea=(
                "Thresholding converts gradient magnitudes into a binary edge map, discarding the strength and "
                "keeping only whether a pixel is an edge. The rule is the same as the mask thresholding from "
                "the foundations: a magnitude above the value becomes one, everything else becomes zero. The "
                "choice of threshold is the whole difficulty. Too low and noise, texture and compression "
                "artefacts all register as edges; too high and genuine edges break into fragments. A single "
                "global value therefore rarely works on a real image with uneven lighting, which motivates "
                "adaptive and hysteresis methods later. Two refinements are worth knowing now. Hysteresis keeps "
                "weak edges only when they connect to strong ones, which fills gaps without admitting isolated "
                "noise. And smoothing before computing the gradient shifts the trade-off: a gaussian blur lowers "
                "the magnitude of noise more than that of a real edge, so a higher threshold becomes safe. The "
                "edge map is also the input to the next step, non-maximum suppression, because thresholding "
                "produces thick bands of edge pixels rather than the thin one-pixel lines that later stages "
                "want. Today you compute a magnitude grid from Sobel responses, threshold it at two hundred, "
                "print the resulting binary map and count its foreground pixels, then note how raising or "
                "lowering the value changes that count."
            ),
            code=(
                'IMAGE = [\n'
                '    [10, 10, 10, 10, 10],\n'
                '    [10, 10, 10, 10, 10],\n'
                '    [10, 10, 100, 100, 100],\n'
                '    [10, 10, 100, 100, 100],\n'
                '    [10, 10, 100, 100, 100],\n'
                ']\n'
                'SOBEL_X = [[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]]\n'
                'SOBEL_Y = [[-1, -2, -1], [0, 0, 0], [1, 2, 1]]\n'
                'EDGE_THRESHOLD = 200\n'
                '\n'
                'def convolve(image, kernel):\n'
                '    h, w = len(image), len(image[0])\n'
                '    out = [[0] * (w - 2) for _ in range(h - 2)]\n'
                '    for r in range(1, h - 1):\n'
                '        for c in range(1, w - 1):\n'
                '            total = 0\n'
                '            for kr in range(3):\n'
                '                for kc in range(3):\n'
                '                    total += kernel[kr][kc] * image[r + kr - 1][c + kc - 1]\n'
                '            out[r - 1][c - 1] = total\n'
                '    return out\n'
                '\n'
                'def magnitude(gx, gy):\n'
                '    h, w = len(gx), len(gx[0])\n'
                '    return [[round((gx[r][c] ** 2 + gy[r][c] ** 2) ** 0.5, 2) for c in range(w)]\n'
                '            for r in range(h)]\n'
                '\n'
                'gx = convolve(IMAGE, SOBEL_X)\n'
                'gy = convolve(IMAGE, SOBEL_Y)\n'
                'mag = magnitude(gx, gy)\n'
                'mask = [[1 if value >= EDGE_THRESHOLD else 0 for value in row] for row in mag]\n'
                'for row in mask:\n'
                '    print(row)\n'
                'print("edge pixels:", sum(sum(row) for row in mask))\n'
                '\n'
                'assert mask == [[0, 1, 1], [1, 1, 1], [1, 1, 0]]\n'
                'assert sum(sum(row) for row in mask) == 7\n'
                'print("thresholding turns magnitudes into an edge map")\n'
            ),
            variant_b="raise the threshold to 300 and recount, explaining which edge pixels disappear",
            variant_c="lower the threshold to 100 and explain why the corner band grows wider",
            mistakes=[
                "Thresholding the raw signed responses instead of the magnitude, so half the edges vanish.",
                "Choosing a threshold on one image and assuming it transfers to different lighting.",
                "Expecting one-pixel edges, when thresholding alone leaves thick bands.",
            ],
            q1=(
                "Why is a single threshold rarely enough for a real image?",
                "Noise, texture and uneven lighting change the magnitude scale across the frame, so one value lets noise through in some regions and breaks edges in others.",
            ),
            homework=(
                "Write `edge_mask(image, threshold)` computing Sobel responses, their magnitude and a 0/1 mask. "
                "Run it on a five-by-five corner image at threshold 200, print the mask and the edge count, and "
                "comment which line compares magnitude with the threshold."
            ),
            patterns=["def ", "if ", "print("],
            mapping=(
                "`cv2.threshold` on a Canny or Sobel magnitude produces this mask; the two-value hysteresis "
                "threshold is what `cv2.Canny` uses to link weak edges to strong ones."
            ),
        ),
        98: dict(
            topic="Non-maximum suppression",
            idea=(
                "Thresholding an edge map leaves ridges several pixels wide, because the magnitude stays high "
                "across a band around the true edge. Non-maximum suppression thins each ridge to a single pixel "
                "by keeping only local maxima. The full Canny version uses the gradient direction to compare "
                "each pixel with two neighbours interpolated along that direction, but the idea is visible in "
                "one dimension: scan the magnitudes, and keep a value only if it is at least as large as its "
                "neighbour on one side and strictly larger than the neighbour on the other, otherwise set it to "
                "zero. The asymmetric comparison handles plateaus without erasing every pixel of a flat-topped "
                "ridge. The result is a thin set of candidates, which is what makes later edge linking and "
                "contour extraction tractable. Two details matter. The test is a local maximum along the "
                "gradient direction, not along a row or column, so using the wrong direction merges distinct "
                "edges or drops corners. And suppression does not create edges or set thresholds; it only thins "
                "what is already there, so it must follow the gradient and precede the final threshold in a "
                "Canny pipeline. Today you apply a horizontal suppression rule to a small magnitude grid, print "
                "the before and after values, and count how many pixels survived, noticing that plateaus lose "
                "all but one representative."
            ),
            code=(
                'MAG = [\n'
                '    [10, 40, 40, 10],\n'
                '    [20, 80, 60, 20],\n'
                '    [10, 90, 50, 10],\n'
                '    [5, 30, 20, 5],\n'
                ']\n'
                '\n'
                'def suppress_horizontal(mag):\n'
                '    h, w = len(mag), len(mag[0])\n'
                '    out = [[0] * w for _ in range(h)]\n'
                '    for r in range(h):\n'
                '        for c in range(1, w - 1):\n'
                '            value = mag[r][c]\n'
                '            if value >= mag[r][c - 1] and value > mag[r][c + 1]:\n'
                '                out[r][c] = value\n'
                '    return out\n'
                '\n'
                'kept = suppress_horizontal(MAG)\n'
                'print("before:", MAG)\n'
                'print("after:", kept)\n'
                'survivors = sum(1 for row in kept for value in row if value)\n'
                'print("surviving pixels:", survivors)\n'
                '\n'
                'assert kept == [[0, 0, 40, 0], [0, 80, 0, 0], [0, 90, 0, 0], [0, 30, 0, 0]]\n'
                'assert survivors == 4\n'
                'print("non-maximum suppression keeps only ridge peaks")\n'
            ),
            variant_b="make the comparison strict on the left instead and check which pixels survive",
            variant_c="reverse each row before comparing and describe how the chosen side moves",
            mistakes=[
                "Suppressing along a row or column when the gradient direction is different.",
                "Using strict comparisons on both sides, which deletes every pixel of a plateau.",
                "Doing suppression after thresholding, where the weakest of a ridge may already be gone.",
            ],
            q1=(
                "Why does suppression compare with neighbours on both sides of a pixel?",
                "A ridge is only thinned if a pixel is kept when it is at least the local maximum along the gradient, so both neighbours must be checked.",
            ),
            homework=(
                "Write `suppress_horizontal(mag)` keeping a pixel only when it beats its left and right "
                "neighbours. Run it on a four-by-four magnitude grid, print the grid and the survivor count, "
                "and comment which line performs the local-maximum test."
            ),
            patterns=["def ", "if ", "print("],
            mapping=(
                "`cv2.Canny` performs non-maximum suppression internally along the gradient direction; "
                "implementing the one-dimensional version makes the thinning step concrete."
            ),
        ),
        99: dict(
            topic="Dilation and erosion",
            idea=(
                "Morphology operates on binary masks using a small structuring element, usually a three-by-three "
                "square, and two primitives. Dilation sets an output pixel to one if any pixel under the "
                "structuring element is foreground, so objects grow by one pixel in every direction and small "
                "gaps close. Erosion sets it to one only if every pixel under the element is foreground, so "
                "objects shrink and thin protrusions vanish. Borders need a convention, and the honest one is "
                "zero padding: outside the image counts as background, which is why dilation near the edge "
                "still works but erosion there fails. Both operations are local, deterministic and cheap, and "
                "they are the geometry of masks in the same way convolution is the geometry of grayscale "
                "images. The structuring element is the whole specification: a square grows in all directions, "
                "a plus grows only orthogonally, and a larger element reaches further, so the shape and size "
                "must be chosen deliberately. Dilation and erosion are not inverses; dilating then eroding "
                "removes small objects, while eroding then dilating fills small holes, and those two composites "
                "are opening and closing. Today you write one function parameterised by mode and apply it to a "
                "mask holding a solid four-by-four block, printing the dilated and eroded counts and confirming "
                "that dilation grows the pixel count while erosion shrinks it."
            ),
            code=(
                'MASK = [\n'
                '    [0, 0, 0, 0, 0, 0],\n'
                '    [0, 1, 1, 1, 1, 0],\n'
                '    [0, 1, 1, 1, 1, 0],\n'
                '    [0, 1, 1, 1, 1, 0],\n'
                '    [0, 1, 1, 1, 1, 0],\n'
                '    [0, 0, 0, 0, 0, 0],\n'
                ']\n'
                '\n'
                'def morphology(mask, mode):\n'
                '    h, w = len(mask), len(mask[0])\n'
                '    out = [[0] * w for _ in range(h)]\n'
                '    for r in range(h):\n'
                '        for c in range(w):\n'
                '            neighbours = []\n'
                '            for dr in (-1, 0, 1):\n'
                '                for dc in (-1, 0, 1):\n'
                '                    rr, cc = r + dr, c + dc\n'
                '                    inside = 0 <= rr < h and 0 <= cc < w\n'
                '                    neighbours.append(mask[rr][cc] if inside else 0)\n'
                '            if mode == "erode":\n'
                '                out[r][c] = 1 if all(neighbours) else 0\n'
                '            else:\n'
                '                out[r][c] = 1 if any(neighbours) else 0\n'
                '    return out\n'
                '\n'
                'dilated = morphology(MASK, "dilate")\n'
                'eroded = morphology(MASK, "erode")\n'
                'print("dilated rows:")\n'
                'for row in dilated:\n'
                '    print(row)\n'
                'print("eroded rows:")\n'
                'for row in eroded:\n'
                '    print(row)\n'
                'print("pixels:", sum(map(sum, MASK)), sum(map(sum, dilated)), sum(map(sum, eroded)))\n'
                '\n'
                'assert sum(map(sum, dilated)) == 36\n'
                'assert sum(map(sum, eroded)) == 4\n'
                'print("dilation grows foreground, erosion shrinks it")\n'
            ),
            variant_b="use a plus-shaped element instead of a square and compare the dilated counts",
            variant_c="treat outside pixels as foreground for erosion and describe how the border survives",
            mistakes=[
                "Treating out-of-bounds neighbourhood values as absent, which makes border erosion too lenient.",
                "Assuming erosion undoes dilation, when the pair is not invertible.",
                "Using a structuring element larger than the objects, which erases them completely.",
            ],
            q1=(
                "What does the structuring element control in dilation and erosion?",
                "Its shape and size define which neighbours are examined, so a square grows in all directions while a plus grows only orthogonally.",
            ),
            homework=(
                "Write `morphology(mask, mode)` applying a three-by-three square with zero padding, where mode "
                "is dilate or erode. Run it on a six-by-six mask with a four-by-four block, print both grids, "
                "and comment which branch handles erosion."
            ),
            patterns=["def ", "if ", "print("],
            mapping=(
                "`cv2.dilate` and `cv2.erode` take a structuring element from `cv2.getStructuringElement`; a "
                "three-by-three rectangular element matches this square."
            ),
        ),
        100: dict(
            topic="Opening and closing",
            idea=(
                "Opening and closing combine erosion and dilation in the two possible orders, and the order "
                "turns out to be the whole point. Opening erodes first, which deletes anything too small to "
                "contain the structuring element, then dilates, which restores the survivors to roughly their "
                "original size. The net effect is that isolated specks and thin bridges disappear while solid "
                "objects are preserved. Closing dilates first, which fills holes and narrows gaps smaller than "
                "the element, then erodes, which returns objects to roughly their original size. The net effect "
                "is that pinholes disappear while the outer boundary is left essentially unchanged. Because "
                "each composite removes a different kind of defect, opening and closing are the standard "
                "cleanup operations in a segmentation pipeline: threshold, open to drop noise, close to "
                "solidify objects, then measure. Neither operation is lossless, and both depend entirely on the "
                "structuring element, so a mask cleaned with one element may lose detail that a smaller one "
                "would keep. A useful way to remember the pair is that opening removes small foreground, "
                "closing removes small background. Today you build a mask with an isolated speck and a separate "
                "mask with a one-pixel hole, apply opening and closing respectively, and print the counts and "
                "the fate of the speck and the hole."
            ),
            code=(
                'SPECKED = [\n'
                '    [0, 0, 0, 0, 0, 1],\n'
                '    [0, 1, 1, 1, 0, 0],\n'
                '    [0, 1, 1, 1, 0, 0],\n'
                '    [0, 1, 1, 1, 0, 0],\n'
                '    [0, 0, 0, 0, 0, 0],\n'
                '    [0, 0, 0, 0, 0, 0],\n'
                ']\n'
                'HOLED = [\n'
                '    [0, 0, 0, 0, 0, 0],\n'
                '    [0, 1, 1, 1, 0, 0],\n'
                '    [0, 1, 0, 1, 0, 0],\n'
                '    [0, 1, 1, 1, 0, 0],\n'
                '    [0, 0, 0, 0, 0, 0],\n'
                '    [0, 0, 0, 0, 0, 0],\n'
                ']\n'
                '\n'
                'def morphology(mask, mode):\n'
                '    h, w = len(mask), len(mask[0])\n'
                '    out = [[0] * w for _ in range(h)]\n'
                '    for r in range(h):\n'
                '        for c in range(w):\n'
                '            neighbours = []\n'
                '            for dr in (-1, 0, 1):\n'
                '                for dc in (-1, 0, 1):\n'
                '                    rr, cc = r + dr, c + dc\n'
                '                    inside = 0 <= rr < h and 0 <= cc < w\n'
                '                    neighbours.append(mask[rr][cc] if inside else 0)\n'
                '            if mode == "erode":\n'
                '                out[r][c] = 1 if all(neighbours) else 0\n'
                '            else:\n'
                '                out[r][c] = 1 if any(neighbours) else 0\n'
                '    return out\n'
                '\n'
                'def count(mask):\n'
                '    return sum(map(sum, mask))\n'
                '\n'
                'opened = morphology(morphology(SPECKED, "erode"), "dilate")\n'
                'closed = morphology(morphology(HOLED, "dilate"), "erode")\n'
                'print("speck", SPECKED[0][5], "->", opened[0][5], "opened pixels:", count(opened))\n'
                'print("hole", HOLED[2][2], "->", closed[2][2], "closed pixels:", count(closed))\n'
                '\n'
                'assert count(opened) == 9 and opened[0][5] == 0\n'
                'assert count(closed) == 9 and closed[2][2] == 1\n'
                'print("opening removes specks, closing fills pinholes")\n'
            ),
            variant_b="open the holed mask and explain why the solid block survives but the hole returns",
            variant_c="close the specked mask and describe whether the isolated pixel is kept",
            mistakes=[
                "Swapping the order, so opening becomes closing and the wrong defect is removed.",
                "Using opening to fill holes, when holes are small background and need closing.",
                "Expecting the object shape to stay identical after opening or closing.",
            ],
            q1=(
                "Why does opening remove specks while closing fills holes?",
                "Opening erodes first, deleting anything smaller than the element, then dilates; closing dilates first, filling small background, then erodes.",
            ),
            homework=(
                "Write `opening(mask)` and `closing(mask)` from an erode and dilate helper, plus `count(mask)`. "
                "Apply opening to a mask with a speck and closing to a mask with a hole, print both counts, and "
                "comment which composite fills background."
            ),
            patterns=["def ", "return", "print("],
            mapping=(
                "`cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)` and `cv2.MORPH_CLOSE` are the direct "
                "equivalents, and they are the usual cleanup pair after thresholding."
            ),
        ),
        101: dict(
            topic="Denoising small images",
            idea=(
                "Denoising is the first job of filtering, and the choice of filter depends on the noise. "
                "Averaging filters such as box and gaussian blur suit smooth, spread-out noise, because "
                "averaging many independent errors reduces their contribution. They are the wrong tool for "
                "salt-and-pepper noise, the isolated black and white pixels caused by transmission errors, "
                "because a single bad value drags the average of its whole neighbourhood with it. A median "
                "filter handles that case: it sorts the neighbourhood and takes the middle value, so as long as "
                "fewer than half the pixels are corrupted the median is one of the clean values and the outlier "
                "simply vanishes. The median also preserves edges better than a blur of the same size, because a "
                "step edge passes through the median while averaging rounds it off. The cost is that sorting is "
                "slower than a sum, which is why median filtering is used on small windows and often only on "
                "the noisy channels. Measuring the effect honestly means comparing against the clean image and "
                "reporting the mean absolute error rather than eyeballing the result. Today you add "
                "deterministic salt-and-pepper pixels to a small step image, apply both a box average and a "
                "median, and print the mean absolute error against the clean reference, confirming that the "
                "median wins on this kind of noise."
            ),
            code=(
                'CLEAN = [\n'
                '    [40, 40, 80, 80, 80],\n'
                '    [40, 40, 80, 80, 80],\n'
                '    [40, 40, 80, 80, 80],\n'
                '    [40, 40, 80, 80, 80],\n'
                '    [40, 40, 80, 80, 80],\n'
                ']\n'
                'NOISY = [row[:] for row in CLEAN]\n'
                'NOISY[0][2] = 0\n'
                'NOISY[1][1] = 255\n'
                'NOISY[2][4] = 0\n'
                'NOISY[3][3] = 255\n'
                '\n'
                'def box_filter(image):\n'
                '    h, w = len(image), len(image[0])\n'
                '    out = [[0] * (w - 2) for _ in range(h - 2)]\n'
                '    for r in range(1, h - 1):\n'
                '        for c in range(1, w - 1):\n'
                '            total = sum(image[r + dr][c + dc]\n'
                '                        for dr in (-1, 0, 1) for dc in (-1, 0, 1))\n'
                '            out[r - 1][c - 1] = round(total / 9, 2)\n'
                '    return out\n'
                '\n'
                'def median_filter(image):\n'
                '    h, w = len(image), len(image[0])\n'
                '    out = [[0] * (w - 2) for _ in range(h - 2)]\n'
                '    for r in range(1, h - 1):\n'
                '        for c in range(1, w - 1):\n'
                '            values = sorted(image[r + dr][c + dc]\n'
                '                            for dr in (-1, 0, 1) for dc in (-1, 0, 1))\n'
                '            out[r - 1][c - 1] = values[4]\n'
                '    return out\n'
                '\n'
                'def mean_abs_error(a, b):\n'
                '    total = sum(abs(a[r][c] - b[r][c]) for r in range(len(a)) for c in range(len(a[0])))\n'
                '    return round(total / (len(a) * len(a[0])), 2)\n'
                '\n'
                'reference = [row[1:4] for row in CLEAN[1:4]]\n'
                'boxed = box_filter(NOISY)\n'
                'med = median_filter(NOISY)\n'
                'print("box error:", mean_abs_error(boxed, reference))\n'
                'print("median error:", mean_abs_error(med, reference))\n'
                'print("median row:", med[0])\n'
                '\n'
                'assert mean_abs_error(boxed, reference) == 17.28\n'
                'assert mean_abs_error(med, reference) == 0.0\n'
                'assert med[0] == [40, 80, 80]\n'
                'print("median removes salt and pepper, a box average spreads it")\n'
            ),
            variant_b="corrupt a smooth patch instead of a step edge and compare the two filters again",
            variant_c="add more salt pixels than clean ones and explain why the median then fails too",
            mistakes=[
                "Using an averaging filter on salt-and-pepper noise, which smears the outliers.",
                "Judging the denoiser by eye instead of measuring error against the clean image.",
                "Corrupting more than half the neighbourhood, where the median stops being robust.",
            ],
            q1=(
                "Why does a median filter beat a box filter on salt-and-pepper noise?",
                "The median ignores the extreme values as long as they are a minority, while an average lets one corrupted pixel drag the whole neighbourhood.",
            ),
            homework=(
                "Write `median_filter(image)` returning the sorted middle of each three-by-three window, plus "
                "`mean_abs_error(a, b)`. Run it and a box filter on a noisy step image, print both errors "
                "against the clean reference, and comment which line chooses the middle value."
            ),
            patterns=["def ", "sorted(", "print("],
            mapping=(
                "`cv2.medianBlur` takes a window size and is the standard first response to impulse noise; "
                "comparing it with `cv2.blur` on the same frame shows the difference immediately."
            ),
        ),
        102: dict(
            topic="Separable filters",
            idea=(
                "Separable filters exploit a property of certain two-dimensional kernels: they can be written "
                "as the outer product of two one-dimensional kernels, one vertical and one horizontal. "
                "Convolution with such a kernel is exactly equivalent to a horizontal pass followed by a "
                "vertical pass, but the arithmetic is cheaper. A three-by-three pass costs nine multiplications "
                "per pixel; the separated version costs three horizontally plus three vertically, six in total, "
                "and the saving grows with the window, so a fifteen-by-fifteen kernel costs fifteen plus fifteen "
                "instead of two hundred and twenty-five. The gaussian kernel built from one, two, one is the "
                "canonical example, and so is the box kernel of uniform weights. The two passes are not "
                "commutative in implementation details such as border handling, but for interior pixels the "
                "order does not change the result. Recognising separability is a standard performance idea: "
                "check whether the kernel has rank one, and if it does, run two passes. It also clarifies the "
                "filter's behaviour, since the effective spread is the combination of the horizontal and "
                "vertical widths. Not every kernel is separable; an edge-detection kernel generally is not, "
                "which is why it is applied in two dimensions. Today you build the three-by-three gaussian from "
                "the one-dimensional one, run the direct convolution and the two-pass version on the same image, "
                "print both results, and check that they agree."
            ),
            code=(
                'IMAGE = [\n'
                '    [10, 10, 10, 10, 10],\n'
                '    [10, 90, 90, 90, 10],\n'
                '    [10, 90, 90, 90, 10],\n'
                '    [10, 90, 90, 90, 10],\n'
                '    [10, 10, 10, 10, 10],\n'
                ']\n'
                'ONE_D = [1, 2, 1]\n'
                'GAUSS = [[a * b for b in ONE_D] for a in ONE_D]\n'
                '\n'
                'def convolve2d(image, kernel):\n'
                '    h, w = len(image), len(image[0])\n'
                '    out = [[0] * (w - 2) for _ in range(h - 2)]\n'
                '    for r in range(1, h - 1):\n'
                '        for c in range(1, w - 1):\n'
                '            total = 0\n'
                '            for kr in range(3):\n'
                '                for kc in range(3):\n'
                '                    total += kernel[kr][kc] * image[r + kr - 1][c + kc - 1]\n'
                '            out[r - 1][c - 1] = round(total / 16, 2)\n'
                '    return out\n'
                '\n'
                'def separable(image, kernel):\n'
                '    h, w = len(image), len(image[0])\n'
                '    rows = [[sum(kernel[i] * image[r][c + i - 1] for i in range(3))\n'
                '             for c in range(1, w - 1)] for r in range(h)]\n'
                '    out = [[round(sum(kernel[i] * rows[r + i - 1][c] for i in range(3)) / 16, 2)\n'
                '            for c in range(w - 2)] for r in range(1, h - 1)]\n'
                '    return out\n'
                '\n'
                'two_d = convolve2d(IMAGE, GAUSS)\n'
                'two_pass = separable(IMAGE, ONE_D)\n'
                'print("2d:", two_d)\n'
                'print("separated:", two_pass)\n'
                'print("multiplications per pixel: 9 vs 6")\n'
                '\n'
                'assert two_d == two_pass\n'
                'assert two_d[0][0] == 55.0\n'
                'print("a rank-one kernel factors into two 1d passes")\n'
            ),
            variant_b="use a five-tap one-dimensional kernel and compare the cost with its 2d equivalent",
            variant_c="try the Sobel kernel and show that the two passes do not match",
            mistakes=[
                "Assuming every kernel is separable and two passes will match the direct result.",
                "Forgetting to normalise the separated passes, so the output is too large.",
                "Applying the vertical pass before the horizontal one and changing the border convention.",
            ],
            q1=(
                "How much does separability save for a three-by-three kernel?",
                "It replaces nine multiplications per pixel with three plus three, six in total, and the saving grows with the window size.",
            ),
            homework=(
                "Write `separable(image, kernel)` running a horizontal then a vertical one-dimensional pass, and "
                "`convolve2d(image, kernel)` for comparison. Run both with the one, two, one kernel on a "
                "five-by-five image, print the grids, and comment which line does the first pass."
            ),
            patterns=["def ", "for ", "print("],
            mapping=(
                "OpenCV's `GaussianBlur` and `blur` are separable internally, which is why large kernel sizes "
                "stay fast; `sepFilter2D` exposes the two one-dimensional kernels directly."
            ),
        ),
        103: dict(
            topic="Choosing a filter",
            idea=(
                "Choosing a filter is a decision about what the image contains and what the next stage needs. "
                "The first question is the noise: salt-and-pepper or other impulsive corruption calls for a "
                "median filter, while smooth sensor noise is better handled by a gaussian or box average, "
                "because averaging is exactly what reduces spread-out error. The second question is detail: "
                "every averaging filter trades noise reduction against edge preservation, and a larger window "
                "trades more of the latter for more of the former, so pick the smallest window that removes the "
                "noise. The third is purpose: if the goal is edges, smooth lightly first and then apply a "
                "gradient operator, because differentiation amplifies noise; if the goal is a clean mask, "
                "threshold and use morphology to tidy it. Sharpening belongs after denoising, never before, and "
                "only when the detail is genuine rather than noise. A useful discipline is to measure rather "
                "than guess: compute a roughness score such as the sum of absolute neighbour differences, and "
                "observe how each candidate filter changes it, remembering that lowering roughness is not "
                "automatically good because a constant image is perfectly smooth and useless. Today you compute "
                "the roughness of a small noisy image, compare it after a box filter and after a median, and "
                "print a short decision rule that maps noise type and intent to a filter name."
            ),
            code=(
                'IMAGE = [\n'
                '    [40, 40, 80, 80, 80],\n'
                '    [40, 40, 80, 80, 80],\n'
                '    [40, 40, 80, 80, 80],\n'
                '    [40, 40, 80, 80, 80],\n'
                '    [40, 40, 80, 80, 80],\n'
                ']\n'
                'IMAGE[1][1] = 255\n'
                'IMAGE[3][3] = 0\n'
                '\n'
                'def box_filter(image):\n'
                '    h, w = len(image), len(image[0])\n'
                '    out = [[0] * (w - 2) for _ in range(h - 2)]\n'
                '    for r in range(1, h - 1):\n'
                '        for c in range(1, w - 1):\n'
                '            total = sum(image[r + dr][c + dc]\n'
                '                        for dr in (-1, 0, 1) for dc in (-1, 0, 1))\n'
                '            out[r - 1][c - 1] = round(total / 9, 2)\n'
                '    return out\n'
                '\n'
                'def median_filter(image):\n'
                '    h, w = len(image), len(image[0])\n'
                '    out = [[0] * (w - 2) for _ in range(h - 2)]\n'
                '    for r in range(1, h - 1):\n'
                '        for c in range(1, w - 1):\n'
                '            values = sorted(image[r + dr][c + dc]\n'
                '                            for dr in (-1, 0, 1) for dc in (-1, 0, 1))\n'
                '            out[r - 1][c - 1] = values[4]\n'
                '    return out\n'
                '\n'
                'def roughness(image):\n'
                '    h, w = len(image), len(image[0])\n'
                '    across = sum(abs(image[r][c] - image[r][c + 1])\n'
                '                 for r in range(h) for c in range(w - 1))\n'
                '    down = sum(abs(image[r][c] - image[r + 1][c])\n'
                '               for r in range(h - 1) for c in range(w))\n'
                '    return across + down\n'
                '\n'
                'def choose(noise, edges_wanted):\n'
                '    if noise == "salt-pepper":\n'
                '        return "median filter"\n'
                '    if noise == "smooth":\n'
                '        return "gaussian blur"\n'
                '    if edges_wanted:\n'
                '        return "sobel then threshold"\n'
                '    return "box blur"\n'
                '\n'
                'print("roughness before:", roughness(IMAGE))\n'
                'print("roughness box:", round(roughness(box_filter(IMAGE)), 2))\n'
                'print("roughness median:", roughness(median_filter(IMAGE)))\n'
                'print("salt-pepper ->", choose("salt-pepper", False))\n'
                'print("find edges ->", choose("none", True))\n'
                '\n'
                'assert roughness(median_filter(IMAGE)) < round(roughness(box_filter(IMAGE)), 2)\n'
                'assert choose("salt-pepper", False) == "median filter"\n'
                'print("pick the filter that matches the noise, then measure it")\n'
            ),
            variant_b="blur the image twice and explain why roughness keeps falling but the image degrades",
            variant_c="sharpen before denoising and describe how the roughness score reacts",
            mistakes=[
                "Choosing a filter by habit rather than by the type of noise present.",
                "Minimising roughness alone, since a constant image scores perfectly and carries nothing.",
                "Sharpening before denoising, which amplifies the noise instead of the detail.",
            ],
            q1=(
                "Why is a roughness score not enough on its own to choose a filter?",
                "A constant image has zero roughness but no content, so the score must be paired with error against a reference or the intended task.",
            ),
            homework=(
                "Write `roughness(image)` summing absolute neighbour differences and `choose(noise, "
                "edges_wanted)` returning a filter name. Apply box and median filters to a noisy image, print "
                "the roughness before and after, and comment which branch chooses the median."
            ),
            patterns=["def ", "return", "print("],
            mapping=(
                "This mirrors the OpenCV decision between `medianBlur`, `GaussianBlur`, `Sobel` and "
                "`morphologyEx`; the same noise and intent questions drive the choice."
            ),
        ),
        104: dict(
            topic="Review: filtering and edges checklist",
            idea=(
                "Today consolidates the phase into a checklist that you can apply to any new filter or "
                "morphology problem. Start with the kernel: what are its weights, do they sum to one, and what "
                "does that sum imply for brightness? Then the border: does the implementation skip the edge, "
                "pad with zeros, or replicate, and does the output size shrink accordingly? For smoothing, "
                "decide box or gaussian, choose the smallest window that controls the noise, and remember that "
                "separable kernels should run as two passes. For edges, take Sobel responses in both "
                "directions, combine them into a magnitude, suppress non-maxima along the gradient, and "
                "threshold last. For masks, remember that dilation grows, erosion shrinks, opening removes "
                "small foreground and closing removes small background. Keep every stage a separate function "
                "and print its intermediate result, because a wrong final answer is always traceable to one "
                "stage. Measure wherever possible: mean absolute error against a reference for denoising, edge "
                "counts for thresholds, component counts for morphology. The worked example runs the gradient "
                "half of the chain on a small corner image, prints the magnitude grid and the number of "
                "thresholded edge pixels, and so exercises kernel, gradient, magnitude and threshold in one "
                "deterministic script. From here the next phase builds on this vocabulary to describe shapes "
                "and features rather than pixels."
            ),
            code=(
                'IMAGE = [\n'
                '    [10, 10, 10, 10, 10],\n'
                '    [10, 10, 10, 10, 10],\n'
                '    [10, 10, 100, 100, 100],\n'
                '    [10, 10, 100, 100, 100],\n'
                '    [10, 10, 100, 100, 100],\n'
                ']\n'
                'SOBEL_X = [[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]]\n'
                'SOBEL_Y = [[-1, -2, -1], [0, 0, 0], [1, 2, 1]]\n'
                '\n'
                'def convolve(image, kernel):\n'
                '    h, w = len(image), len(image[0])\n'
                '    out = [[0] * (w - 2) for _ in range(h - 2)]\n'
                '    for r in range(1, h - 1):\n'
                '        for c in range(1, w - 1):\n'
                '            total = 0\n'
                '            for kr in range(3):\n'
                '                for kc in range(3):\n'
                '                    total += kernel[kr][kc] * image[r + kr - 1][c + kc - 1]\n'
                '            out[r - 1][c - 1] = total\n'
                '    return out\n'
                '\n'
                'def magnitude(gx, gy):\n'
                '    h, w = len(gx), len(gx[0])\n'
                '    return [[round((gx[r][c] ** 2 + gy[r][c] ** 2) ** 0.5, 2) for c in range(w)]\n'
                '            for r in range(h)]\n'
                '\n'
                'gx = convolve(IMAGE, SOBEL_X)\n'
                'gy = convolve(IMAGE, SOBEL_Y)\n'
                'mag = magnitude(gx, gy)\n'
                'mask = [[1 if value >= 250 else 0 for value in row] for row in mag]\n'
                'for row in mag:\n'
                '    print(row)\n'
                'print("kernel sum check:", sum(sum(row) for row in SOBEL_X))\n'
                'print("edge pixels:", sum(sum(row) for row in mask))\n'
                '\n'
                'assert sum(sum(row) for row in SOBEL_X) == 0\n'
                'assert mag[0][0] == 127.28\n'
                'assert sum(sum(row) for row in mask) == 7\n'
                'print("checklist: kernel, border, gradient, magnitude, threshold")\n'
            ),
            variant_b="add the horizontal suppression step and count how many edge pixels remain",
            variant_c="dilate the edge mask once and describe how the count and thickness change",
            mistakes=[
                "Combining every stage in one function, so a failure cannot be traced to one step.",
                "Forgetting the border rule, so the magnitude grid no longer lines up with the image.",
                "Thresholding before combining gx and gy, which throws away half the edge evidence.",
            ],
            q1=(
                "Why does the checklist insist on keeping each stage a separate function?",
                "Each intermediate result can be printed and asserted on, so a wrong final answer is localised to a single stage instead of the whole chain.",
            ),
            homework=(
                "Write `edge_pipeline(image, threshold)` combining Sobel, magnitude and threshold, and print "
                "the magnitude grid plus the edge count. Run it on a five-by-five corner image, check the count, "
                "and comment which call computes the gradient magnitude."
            ),
            patterns=["def ", "return", "print("],
            mapping=(
                "This is the OpenCV sequence `Sobel` then `magnitude` then `threshold`; the checklist maps "
                "directly onto the filter and morphology functions used in practice."
            ),
        ),
    },
)
