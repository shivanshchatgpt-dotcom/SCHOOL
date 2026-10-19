PHASE = (
    "Video, Geometry and Deployment",
    "Treat video as indexed frames, reason about camera geometry, and keep a vision pipeline inside its latency and memory budgets.",
    {
        150: dict(
            topic="Orientation: beyond one frame",
            idea=(
                "Most computer vision lessons stop at a single still image, but deployed systems see a stream. A "
                "video is just an ordered sequence of frames, and the ordering carries information a single "
                "picture lacks. Once frames are indexed, questions that were impossible become simple: what "
                "moved, how far, and did anything appear or disappear? The mental shift is to treat the stream "
                "as data with one extra axis, the frame index, rather than as a movie. A frame is still a grid "
                "of numbers, and a clip is a list of those grids. This phase builds the deployment side of "
                "vision on that idea: temporal change, tracking, camera geometry, and the budgets that decide "
                "whether a model can run at all. The examples stay deliberately small so the arithmetic is "
                "visible, using nested lists and integer indices rather than a library. Today you compare "
                "consecutive frames and count pixels whose value changed. That single number is the ancestor of "
                "motion detection, and it shows the central rule of the phase: a video pipeline is a loop over "
                "frames with state carried between iterations. Keep that state explicit, because hidden state "
                "is what makes temporal code hard to test. The same loop shape will hold tracking, background "
                "models and monitoring, so the rest of the phase is depth on this skeleton."
            ),
            code=(
                'FRAMES = [\n'
                '    [[0, 0, 0], [0, 0, 0]],\n'
                '    [[0, 90, 0], [0, 0, 0]],\n'
                '    [[0, 90, 90], [0, 0, 0]],\n'
                ']\n'
                '\n'
                'def changed(a, b, threshold=30):\n'
                '    count = 0\n'
                '    for r in range(len(a)):\n'
                '        for c in range(len(a[0])):\n'
                '            if abs(a[r][c] - b[r][c]) >= threshold:\n'
                '                count += 1\n'
                '    return count\n'
                '\n'
                'for i in range(len(FRAMES) - 1):\n'
                '    print("frame", i, "->", i + 1, "changed:", changed(FRAMES[i], FRAMES[i + 1]))\n'
                '\n'
                'assert changed(FRAMES[0], FRAMES[1]) == 1\n'
                'assert changed(FRAMES[1], FRAMES[2]) == 1\n'
                'print("video is a sequence of frames, not one picture")'
            ),
            variant_b="count changed pixels with a threshold of 100 instead of 30 and explain the difference",
            variant_c="compare frame 0 with frame 2 directly to show that adjacent-frame motion misses slow objects",
            mistakes=[
                "Treating a clip as a single image and ignoring the frame axis entirely.",
                "Comparing frames with an exact inequality, so sensor noise registers as motion everywhere.",
                "Forgetting that frame order matters, which makes a reversed clip look identical.",
            ],
            q1=(
                "Why is the frame index the essential extra piece of data in video?",
                "It defines order and adjacency, so change, speed and appearance can be computed across time rather than from one still image.",
            ),
            homework=(
                "Write `frame_change(frames, threshold)` that compares each consecutive pair in a list of frames "
                "and returns a list of changed-pixel counts. Run it on four small frames, print the counts, and "
                "comment which pair contains the most motion."
            ),
            patterns=["def ", "for ", "print("],
            mapping=(
                "Video analytics pipelines are loops over frames with state; motion counting here is the same "
                "loop a deployed service runs, just without decoding or a model."
            ),
        ),
        151: dict(
            topic="Frames and timestamps",
            idea=(
                "A frame rate is not a promise. Cameras drop frames, encoders reorder them and networks deliver "
                "them late, so the only reliable way to reason about video time is to attach an integer index "
                "to every frame. Using frame indices instead of wall-clock time keeps experiments deterministic "
                "and reproducible: a test that says the gap is three frames fails the same way on every "
                "machine. The basic measurements are the gap between consecutive stamps, the total span, and "
                "the number of missing frames implied by the gaps. A gap of one is normal; a gap of three means "
                "two frames never arrived. These counts matter because downstream logic assumes a rate: a "
                "tracker's velocity is per frame, and a queue's capacity is frames per second times seconds of "
                "buffer. If the stream silently drops half its frames, distances per frame double and the "
                "system looks wrong for a reason no model can explain. Today you write gap and drop counters "
                "over a short timestamp list. The habit is to validate the stream before trusting any temporal "
                "result, and to make the expected step explicit rather than assumed. Timestamps are data, and "
                "the first thing to check is whether they are what you think they are."
            ),
            code=(
                'TIMESTAMPS = [0, 1, 2, 4, 5, 8]\n'
                '\n'
                'def gaps(stamps):\n'
                '    return [b - a for a, b in zip(stamps, stamps[1:])]\n'
                '\n'
                'def dropped(stamps, expected=1):\n'
                '    return sum(g - expected for g in gaps(stamps) if g > expected)\n'
                '\n'
                'print("gaps:", gaps(TIMESTAMPS))\n'
                'print("missing frames:", dropped(TIMESTAMPS))\n'
                'print("span in frames:", TIMESTAMPS[-1] - TIMESTAMPS[0])\n'
                '\n'
                'assert gaps(TIMESTAMPS) == [1, 1, 2, 1, 3]\n'
                'assert dropped(TIMESTAMPS) == 3\n'
                'assert TIMESTAMPS[-1] - TIMESTAMPS[0] == 8\n'
                'print("timestamps are frame indices; gaps are missing data")'
            ),
            variant_b="set the expected step to 2 and recompute how many frames are missing",
            variant_c="add a function that returns the indices of all gaps larger than one frame",
            mistakes=[
                "Using wall-clock time inside tests, which makes the result depend on the machine's load.",
                "Assuming every gap is one frame and silently dividing by the wrong rate.",
                "Sorting frames by content instead of by their timestamp before measuring gaps.",
            ],
            q1=(
                "What does a timestamp gap of three mean when the expected step is one?",
                "Two frames are missing between the two observed frames, so any per-frame rate must be corrected before use.",
            ),
            homework=(
                "Write `gaps(stamps)` and `dropped(stamps, expected)` over a list of integer frame stamps. Run "
                "them on a stream with two gaps, print the gap list and the missing count, and comment which "
                "line counts the missing frames."
            ),
            patterns=["def ", "zip(", "print("],
            mapping=(
                "Frame drops are a common production incident; counting gaps from indices is the cheapest "
                "first check before blaming a model for wrong speeds or missed events."
            ),
        ),
        152: dict(
            topic="Background subtraction",
            idea=(
                "A camera that never moves sees the same scene most of the time, so the cheapest way to find "
                "activity is to model what is normally there and subtract it. The model can be a running "
                "average per pixel: each new frame nudges the stored value, and any pixel far from the model is "
                "foreground. This is background subtraction, and it is the workhorse behind motion masks, "
                "occupancy counts and simple intrusion alerts. Three choices drive behaviour. The learning rate "
                "controls how quickly the model forgets, so a fast rate adapts to light changes but also absorbs "
                "slow-moving objects. The difference threshold decides what counts as foreground, trading "
                "sensitivity against noise. And the model needs a warm-up period, because a mean built from one "
                "frame is just that frame. The output is a mask, exactly like thresholding, so the tools from "
                "earlier phases apply: count foreground pixels, find components, measure boxes. Today you build "
                "a mean background from several frames and subtract a new frame from it. The example uses "
                "integers and a fixed history so the arithmetic is inspectable. Note the limitation honestly: a "
                "plain average has no notion of how variable a pixel usually is, which is why real systems track "
                "variance too."
            ),
            code=(
                'HISTORY = [\n'
                '    [[10, 10], [10, 10]],\n'
                '    [[12, 10], [10, 12]],\n'
                '    [[8, 10], [10, 8]],\n'
                ']\n'
                'CURRENT = [[10, 200], [10, 10]]\n'
                '\n'
                'def background(history):\n'
                '    h, w = len(history[0]), len(history[0][0])\n'
                '    return [[round(sum(f[r][c] for f in history) / len(history)) for c in range(w)] for r in range(h)]\n'
                '\n'
                'def foreground(frame, model, threshold=40):\n'
                '    return [[1 if abs(frame[r][c] - model[r][c]) >= threshold else 0\n'
                '             for c in range(len(frame[0]))] for r in range(len(frame))]\n'
                '\n'
                'model = background(HISTORY)\n'
                'mask = foreground(CURRENT, model)\n'
                'print("background model:", model)\n'
                'for row in mask:\n'
                '    print("mask row:", row)\n'
                '\n'
                'assert model == [[10, 10], [10, 10]]\n'
                'assert sum(map(sum, mask)) == 1\n'
                'print("background is a running average; foreground is a difference")'
            ),
            variant_b="raise the foreground threshold to 150 and explain why only the bright pixel survives",
            variant_c="add a learning rate so the model becomes `old + (new - old) // 4` and print the updated model",
            mistakes=[
                "Building a background model from a single frame and treating it as stable.",
                "Using the same threshold for a noisy sensor and a clean one without checking false positives.",
                "Letting slow objects or gradual light changes get absorbed into the background model.",
            ],
            q1=(
                "What does the learning rate trade off in background subtraction?",
                "Fast adaptation follows light changes but absorbs slow objects; slow adaptation keeps objects but is fooled by lighting drift.",
            ),
            homework=(
                "Write `background(frames)` returning the per-pixel mean and `foreground(frame, model, threshold)` "
                "returning a 0/1 mask. Run both on three history frames and one new frame, print the model and "
                "mask, and comment which line decides foreground."
            ),
            patterns=["def ", "abs(", "print("],
            mapping=(
                "`cv2.createBackgroundSubtractorMOG2` adds variance and history windows, but the contract is the "
                "same mean-versus-difference idea you implement here."
            ),
        ),
        153: dict(
            topic="Tracking by centroid",
            idea=(
                "Detection gives you objects in one frame; tracking gives them identity across frames. The "
                "simplest tracker keeps each object's centroid, predicts that it stays roughly where it was, and "
                "matches each new detection to the nearest previous centroid within a distance gate. The gate "
                "matters as much as the distance: without it, every detection is forced onto some existing "
                "track, and unrelated objects swap identities. Matching also needs a rule for competition, "
                "because two detections may prefer the same track; the usual lazy approach is greedy nearest "
                "with a used set, which is good enough when objects are well separated. Unmatched tracks are "
                "coasted or dropped, and unmatched detections start new tracks. Those three outcomes are the "
                "whole lifecycle. Today you implement greedy nearest-centroid matching and print the assignment "
                "plus the number of distance comparisons. Counting comparisons rather than timing makes the cost "
                "visible and deterministic: naive matching is the number of tracks times the number of "
                "detections. That cost is why large deployments use motion models, appearance features or "
                "assignment algorithms. Start with the simple version and know what it assumes. Identity is a "
                "decision made over time, not a property that a single detection carries on its own."
            ),
            code=(
                'PREVIOUS = [(2, 2), (8, 8)]\n'
                'DETECTIONS = [(3, 2), (7, 9), (2, 2)]\n'
                '\n'
                'def distance(a, b):\n'
                '    return abs(a[0] - b[0]) + abs(a[1] - b[1])\n'
                '\n'
                'def match(previous, detections, gate=3):\n'
                '    used, pairs, comparisons = set(), [], 0\n'
                '    for i, track in enumerate(previous):\n'
                '        best, best_distance = None, gate + 1\n'
                '        for j, detection in enumerate(detections):\n'
                '            if j in used:\n'
                '                continue\n'
                '            comparisons += 1\n'
                '            gap = distance(track, detection)\n'
                '            if gap < best_distance:\n'
                '                best, best_distance = j, gap\n'
                '        if best is not None:\n'
                '            used.add(best)\n'
                '            pairs.append((i, best, best_distance))\n'
                '    return pairs, comparisons\n'
                '\n'
                'pairs, comparisons = match(PREVIOUS, DETECTIONS)\n'
                'print("matches (track, detection, distance):", pairs)\n'
                'print("distance comparisons:", comparisons)\n'
                '\n'
                'assert pairs == [(0, 2, 0), (1, 1, 2)]\n'
                'assert comparisons == 5\n'
                'print("tracking is nearest-centroid matching under a gate")'
            ),
            variant_b="lower the gate to 0 and show that only the exact centroid match survives",
            variant_c="add a third previous centroid far from every detection and show it stays unmatched",
            mistakes=[
                "Matching without a distance gate, so unrelated objects steal each other's identity.",
                "Comparing tracks to detections that were already assigned earlier in the loop.",
                "Assuming centroid distance is meaningful when objects move fast or cross each other.",
            ],
            q1=(
                "Why include a distance gate as well as nearest-neighbour matching?",
                "The gate refuses implausible matches instead of forcing every detection onto a track, which prevents identity swaps across unrelated objects.",
            ),
            homework=(
                "Write `match(previous, detections, gate)` returning assigned pairs and a comparison count. Test "
                "it on two tracks and three detections, print the pairs, and comment which line applies the "
                "distance gate."
            ),
            patterns=["def ", "for ", "print("],
            mapping=(
                "SORT and ByteTrack add motion and appearance to this rule; the gate-and-assign structure is "
                "still the core of production multi-object tracking."
            ),
        ),
        154: dict(
            topic="Kalman filter concept",
            idea=(
                "A measurement is noisy, and a prediction is often better than any single reading. The Kalman "
                "filter formalises the blend: keep an estimate and its uncertainty, predict the estimate "
                "forward with a motion model, then correct it toward the measurement in proportion to how much "
                "you trust each. In one dimension this reduces to a scalar gain between zero and one. A gain of "
                "zero ignores measurements and trusts the prediction; a gain of one ignores the prediction and "
                "copies the measurement. Values between the two smooth noise while still following real "
                "changes. The important idea is not the matrix algebra but the structure: predict, measure, "
                "correct, and carry uncertainty. That structure explains why a filter recovers quickly from a "
                "spike without chasing every noisy value, and why it lags when the gain is too low. Today you run "
                "a scalar filter over a short measurement list with a suspicious spike in the middle and print "
                "the estimates. Counting the arithmetic per step shows the cost is tiny compared with the "
                "detector that produced the measurements. The realism is in choosing the gain and admitting "
                "that a constant-velocity assumption fails when motion changes abruptly. Tuning the gain from "
                "data is part of the model, not an afterthought."
            ),
            code=(
                'MEASUREMENTS = [10, 12, 11, 30, 13]\n'
                '\n'
                'def filter_scalar(values, gain=0.5):\n'
                '    estimate = values[0]\n'
                '    history = [estimate]\n'
                '    for measurement in values[1:]:\n'
                '        prediction = estimate\n'
                '        estimate = prediction + gain * (measurement - prediction)\n'
                '        history.append(round(estimate, 1))\n'
                '    return history\n'
                '\n'
                'history = filter_scalar(MEASUREMENTS)\n'
                'print("measurements:", MEASUREMENTS)\n'
                'print("estimates:", history)\n'
                'print("response to spike:", round(history[3] - history[2], 1))\n'
                '\n'
                'assert history[1] == 11.0\n'
                'assert history[3] == 20.5\n'
                'assert history[4] < 20.5\n'
                'print("a Kalman step blends prediction with measurement using a gain")'
            ),
            variant_b="set the gain to 1.0 and show that the filter simply copies every noisy measurement",
            variant_c="set the gain to 0.1 and show that the spike is smoothed but the estimate lags",
            mistakes=[
                "Using a gain above one, which overshoots and makes the estimate oscillate.",
                "Filtering without a motion model, then expecting it to follow fast turns.",
                "Treating the gain as a tuning-free constant rather than a trust trade-off.",
            ],
            q1=(
                "What do the two extremes of the scalar Kalman gain mean?",
                "A gain of zero trusts the prediction and ignores measurements; a gain of one trusts the measurement and ignores the prediction.",
            ),
            homework=(
                "Write `filter_scalar(values, gain)` returning the estimate history. Run it with gains 1.0 and "
                "0.1 on the spike data, print both histories, and comment which line performs the correction "
                "step."
            ),
            patterns=["def ", "for ", "print("],
            mapping=(
                "Trackers use a Kalman filter to smooth boxes and predict through missed detections; the scalar "
                "gain is the same trust decision the matrix version encodes."
            ),
        ),
        155: dict(
            topic="The pinhole camera model",
            idea=(
                "A camera maps a three-dimensional scene onto a two-dimensional sensor, and the pinhole model is "
                "the smallest description of that mapping. A point at position x, y and depth z projects to "
                "image coordinates given by the focal length times x divided by z, plus the principal point. The "
                "division by depth is the whole story: far objects are small, near objects are large, and a "
                "point exactly on the optical axis lands at the principal point regardless of depth. The "
                "principal point represents where the optical axis meets the sensor, usually near the centre "
                "but rarely exactly there. Focal length is expressed in pixels after calibration. Two practical "
                "consequences follow. First, a detector that reports a box in pixels says nothing about physical "
                "size until depth is known. Second, distance can be estimated from apparent size only if the "
                "object's real size is known and stable. Today you project a few points with scalar arithmetic "
                "and print the results. Notice that the model has no distortion and no skew, which is why real "
                "calibration estimates extra terms. The value of starting here is that every later geometry "
                "formula, including stereo and homography, is a variation on this projection. The model is an "
                "approximation of a real lens, but a useful one because it exposes the quantities to calibrate."
            ),
            code=(
                'FOCAL = 50\n'
                'PRINCIPAL = (320, 240)\n'
                'POINTS = [(0, 0, 100), (100, 0, 200), (50, 50, 50)]\n'
                '\n'
                'def project(point, focal=FOCAL, principal=PRINCIPAL):\n'
                '    x, y, z = point\n'
                '    u = principal[0] + focal * x / z\n'
                '    v = principal[1] + focal * y / z\n'
                '    return (round(u, 1), round(v, 1))\n'
                '\n'
                'for point in POINTS:\n'
                '    print(point, "->", project(point))\n'
                '\n'
                'assert project((0, 0, 100)) == (320.0, 240.0)\n'
                'assert project((100, 0, 200)) == (345.0, 240.0)\n'
                'print("pinhole projection divides by depth, so far points shrink")'
            ),
            variant_b="double the focal length and show that every off-axis point moves further from the centre",
            variant_c="move the principal point to (0, 0) and explain what changes without moving the camera",
            mistakes=[
                "Multiplying by depth instead of dividing, which makes far points larger.",
                "Ignoring the principal point and assuming the optical axis is exactly at pixel zero.",
                "Reporting physical size from pixel size without knowing depth.",
            ],
            q1=(
                "Why does a point on the optical axis project to the principal point at any depth?",
                "Its x and y offsets are zero, so the focal-length times offset divided by depth term vanishes for every z.",
            ),
            homework=(
                "Write `project(point, focal, principal)` for integer pixel output and run it on three points at "
                "different depths. Print the coordinates and comment which division makes distant points move "
                "toward the centre."
            ),
            patterns=["def ", "round", "print("],
            mapping=(
                "Boxes from a detector are pixel measurements; the pinhole model is what lets a deployment turn "
                "them into bearing or size once calibration and depth are available."
            ),
        ),
        156: dict(
            topic="Calibration concept",
            idea=(
                "Calibration is the process of measuring the numbers the pinhole model leaves free, principally "
                "the focal length and the principal point, plus distortion terms in a real lens. The practical "
                "route is to observe something with known dimensions at a known depth and solve for what must be "
                "true for the projection to match. If an object of real width W at depth Z appears w pixels "
                "wide, then the focal length in pixels is w times Z divided by W. Repeating over several "
                "observations and averaging guards against measurement noise. The residuals are as important as "
                "the estimate: if observations disagree wildly, the depth or size assumption is wrong, and "
                "averaging produces a confident wrong number. Real calibration uses a printed pattern with many "
                "points, fits a model, and reports reprojection error. But the concept is the same one-line "
                "relation, and it is testable without a camera. Today you estimate focal length from three "
                "synthetic observations and use it to predict apparent width at a new depth. The lesson is that "
                "calibration converts pixels into geometry, and that a calibration is only valid for the "
                "resolution and lens it was measured at. Change either and the numbers stop applying."
            ),
            code=(
                'SAMPLES = [(100, 200), (50, 400), (200, 100)]\n'
                'REAL_WIDTH_MM = 50\n'
                '\n'
                'def focal(pixel_width, depth):\n'
                '    return pixel_width * depth / REAL_WIDTH_MM\n'
                '\n'
                'def predict_width(depth, focal_length):\n'
                '    return focal_length * REAL_WIDTH_MM / depth\n'
                '\n'
                'estimates = [focal(w, z) for w, z in SAMPLES]\n'
                'mean_focal = sum(estimates) / len(estimates)\n'
                'print("focal estimates:", estimates)\n'
                'print("mean focal:", mean_focal)\n'
                'print("predicted widths:", [predict_width(z, mean_focal) for _, z in SAMPLES])\n'
                '\n'
                'assert estimates == [400.0, 400.0, 400.0]\n'
                'assert predict_width(200, mean_focal) == 100.0\n'
                'print("calibration turns a known size into focal length in pixels")'
            ),
            variant_b="change one sample's depth to 300 and show how it pulls the mean focal length away",
            variant_c="add a residual check that reports the spread of the focal estimates",
            mistakes=[
                "Averaging estimates without checking their spread, so a bad depth is hidden by the mean.",
                "Calibrating at one resolution and using the focal length at another.",
                "Confusing millimetres of real width with pixels of apparent width in the formula.",
            ],
            q1=(
                "Given an object of known width at a known depth, how do you estimate focal length?",
                "Multiply its apparent pixel width by the depth and divide by its real width.",
            ),
            homework=(
                "Write `focal(pixel_width, depth, real_width)` and `predict_width(depth, focal_length, "
                "real_width)`. Use them on three consistent samples, print the estimates and predictions, and "
                "comment which line averages the observations."
            ),
            patterns=["def ", "sum(", "print("],
            mapping=(
                "Camera calibration is a prerequisite for measured analytics such as distance, speed and real "
                "object size; the formula here is the one-line core of a calibration report."
            ),
        ),
        157: dict(
            topic="Stereo and disparity",
            idea=(
                "Two cameras a fixed distance apart see the same point at slightly different horizontal "
                "positions, and that difference is enough to recover depth. The offset in pixels is called "
                "disparity, and for a calibrated pair depth equals focal length times baseline divided by "
                "disparity. This is triangulation in its simplest form. The geometry has two immediate "
                "consequences. First, depth error grows with the square of distance, so stereo is precise up "
                "close and vague far away. Second, a larger baseline improves precision at range but makes "
                "matching harder because the two views differ more. Matching is the hard part in practice: for "
                "every pixel in one image you must find its counterpart in the other, and textureless surfaces "
                "give no reliable match. The formula also shows failure modes clearly. A disparity of zero means "
                "the point is at infinity along that ray, and negative disparity means the match violates the "
                "expected left-right order. Today you compute disparity from matched horizontal coordinates and "
                "convert it to depth with scalar arithmetic. Working in integers keeps the example exact. The "
                "same equation underlies stereo rigs, structured light and, in spirit, any two-view depth "
                "system. Depth from stereo is a measurement with a range-dependent error bar, not an exact "
                "coordinate."
            ),
            code=(
                'FOCAL = 400\n'
                'BASELINE = 60\n'
                'MATCHES = [(220, 200), (260, 200), (200, 180)]\n'
                '\n'
                'def disparity(left_u, right_u):\n'
                '    return left_u - right_u\n'
                '\n'
                'def depth(disp, focal=FOCAL, baseline=BASELINE):\n'
                '    return focal * baseline / disp\n'
                '\n'
                'for left_u, right_u in MATCHES:\n'
                '    disp = disparity(left_u, right_u)\n'
                '    print("pair", (left_u, right_u), "disparity", disp, "depth", round(depth(disp), 1))\n'
                '\n'
                'assert disparity(220, 200) == 20\n'
                'assert round(depth(20), 1) == 1200.0\n'
                'assert depth(40) < depth(20)\n'
                'print("stereo depth is focal times baseline divided by disparity")'
            ),
            variant_b="double the baseline and show that every depth halves for the same disparity",
            variant_c="add a zero-disparity case and explain why the formula cannot produce a finite depth",
            mistakes=[
                "Swapping left and right images, which flips the sign of disparity and breaks the depth formula.",
                "Using pixel disparity with a baseline measured in metres without a consistent unit for focal length.",
                "Assuming disparity is reliable on textureless walls where matching has no evidence.",
            ],
            q1=(
                "Why does stereo depth become less precise at long range?",
                "Depth is inversely proportional to disparity, and disparity is a small pixel difference there, so a one-pixel error causes a large depth error.",
            ),
            homework=(
                "Write `disparity(left_u, right_u)` and `depth(disp, focal, baseline)`. Run them on three "
                "matched pairs, print disparity and depth, and comment which line divides by disparity to get "
                "distance."
            ),
            patterns=["def ", "round", "print("],
            mapping=(
                "Stereo rigs, depth cameras and multi-view reconstruction all convert matched pixel offsets "
                "into depth; the baseline and focal length are the calibration constants that make it metric."
            ),
        ),
        158: dict(
            topic="Inference batching",
            idea=(
                "A model call has fixed overhead, so feeding one frame at a time wastes most of the available "
                "compute. Batching groups several frames into one call, amortising that overhead across the "
                "group. The arithmetic is simple: with n items and batch size b, the number of calls is n "
                "divided by b rounded up, and the last batch is padded or left short. Padding makes the work "
                "uniform, which is what hardware likes, but it also does work on slots that contain no real "
                "frame. That waste is the central trade-off: bigger batches improve throughput and device "
                "utilisation while increasing latency, because a frame must wait for the rest of its batch. "
                "For live video this is a real decision, not a micro-optimisation: a batch of sixteen may halve "
                "the cost per frame yet add a visible delay. Today you compute batch composition, padded slots "
                "and total work units for a small stream at a fixed batch size. Counting work rather than timing "
                "keeps the result deterministic and makes the padding overhead obvious. The same accounting "
                "generalises to batching across cameras, where a shared inference server mixes requests from "
                "several streams and latency depends on the queue. Throughput and latency must be reported "
                "separately, because a batch can improve one while worsening the other."
            ),
            code=(
                'FRAMES = 10\n'
                'BATCH_SIZE = 4\n'
                'COST_PER_SLOT = 5\n'
                '\n'
                'def batch_counts(count, size):\n'
                '    return [min(size, count - start) for start in range(0, count, size)]\n'
                '\n'
                'def padded_slots(count, size):\n'
                '    counts = batch_counts(count, size)\n'
                '    return len(counts) * size\n'
                '\n'
                'counts = batch_counts(FRAMES, BATCH_SIZE)\n'
                'slots = padded_slots(FRAMES, BATCH_SIZE)\n'
                'print("frames per batch:", counts)\n'
                'print("calls:", len(counts))\n'
                'print("padded slots:", slots, "real frames:", FRAMES)\n'
                'print("work units:", slots * COST_PER_SLOT)\n'
                '\n'
                'assert counts == [4, 4, 2]\n'
                'assert slots == 12\n'
                'assert slots - FRAMES == 2\n'
                'print("batching reduces calls but pads the last batch")'
            ),
            variant_b="use a batch size of six and compare the number of calls and padded slots",
            variant_c="add a function that reports the padding waste as a fraction of total slots",
            mistakes=[
                "Forgetting to round up, so the final partial batch is never scheduled.",
                "Counting real frames as work while ignoring padded slots, which understates compute.",
                "Using the largest possible batch without checking the added latency against the live budget.",
            ],
            q1=(
                "What is the trade-off of increasing batch size in a live pipeline?",
                "Throughput and device utilisation improve, but each frame waits longer for its batch, so latency grows.",
            ),
            homework=(
                "Write `batch_counts(count, size)` and `padded_slots(count, size)` for a stream of frames. Print "
                "the batch composition, call count and waste for two batch sizes, and comment which line rounds "
                "the stream up to whole batches."
            ),
            patterns=["def ", "range(", "print("],
            mapping=(
                "Inference servers batch requests from many cameras to raise GPU utilisation; knowing the padding "
                "and latency cost is how you choose a batch size instead of guessing."
            ),
        ),
        159: dict(
            topic="Latency and memory budgets",
            idea=(
                "A vision service has two hard budgets: how long a frame may take and how much memory it may "
                "hold. Both are arithmetic, and both are easier to enforce before deployment than after. Latency "
                "budgets are built by summing the cost of every stage in the path, from decode to resize to "
                "model to post-processing, then comparing the total with the frame interval. If the sum exceeds "
                "the interval, the queue grows without bound and the system falls further behind with every "
                "second. Memory budgets follow the same shape: bytes per frame times the number of buffered "
                "frames, plus the model's own weights and workspace. A single 640 by 480 colour frame is almost "
                "a megabyte before any copy, so a queue of a few dozen frames is a serious allocation. Today you "
                "sum stage costs in abstract operation units and compute a frame buffer size. Operation counts "
                "are deterministic, unlike wall-clock timing, so they make the comparison testable. The habit to "
                "build is to put every stage's cost in one table and check the total against the budget, because "
                "a pipeline is only as fast as its slowest required stage and only as small as its largest "
                "simultaneous buffer."
            ),
            code=(
                'STAGES = [("decode", 3), ("resize", 2), ("model", 20), ("post", 2)]\n'
                'FRAME_BYTES = 640 * 480 * 3\n'
                'QUEUE_FRAMES = 4\n'
                'BUDGET_OPS = 30\n'
                '\n'
                'total = 0\n'
                'for name, cost in STAGES:\n'
                '    total += cost\n'
                '    print(name, "cumulative ops:", total)\n'
                '\n'
                'buffer_bytes = FRAME_BYTES * QUEUE_FRAMES\n'
                'print("total ops:", total, "budget:", BUDGET_OPS, "headroom:", BUDGET_OPS - total)\n'
                'print("frame buffer bytes:", buffer_bytes)\n'
                '\n'
                'assert total == 27\n'
                'assert total <= BUDGET_OPS\n'
                'assert buffer_bytes == 3686400\n'
                'print("budgets are arithmetic, not guesswork")'
            ),
            variant_b="add a second model pass costing 8 operations and show that the budget is now exceeded",
            variant_c="raise the queue to twelve frames and compare the buffer with the original",
            mistakes=[
                "Measuring only the model and ignoring decode, resize and post-processing costs.",
                "Forgetting that each queued frame multiplies the per-frame memory by the queue length.",
                "Treating a fast average latency as proof that no frame ever misses its deadline.",
            ],
            q1=(
                "Why must the sum of stage costs stay below the frame interval?",
                "Otherwise each frame takes longer than the next arrives, so the queue grows and latency accumulates without limit.",
            ),
            homework=(
                "Write `stage_budget(stages, budget)` returning the total cost and headroom, plus "
                "`buffer_bytes(width, height, channels, queued)`. Run them on four stages and a small queue, and "
                "comment which line detects an over-budget pipeline."
            ),
            patterns=["def ", "sum(", "print("],
            mapping=(
                "Deployment reviews compare measured stage latency and memory against the frame interval and the "
                "device limit; this table is the same review in miniature."
            ),
        ),
        160: dict(
            topic="Model export and quantisation",
            idea=(
                "A trained model is one thing; a deployable model is another. Export converts the training "
                "framework's graph into a runtime format, and quantisation reduces the numeric precision of its "
                "weights and activations so it runs faster and fits in less memory. The simplest form maps "
                "floating-point weights onto signed eight-bit integers using a scale, then clamps to the "
                "representable range. Reconstructing a value multiplies the integer by the scale, so the error "
                "is bounded by half a scale step for values inside the range. Values outside the range saturate, "
                "which is why the scale must be chosen from the observed weight distribution rather than "
                "guessed. Two ideas matter for deployment. First, quantisation is lossy, and the loss must be "
                "measured on representative data rather than assumed harmless. Second, an exported model is only "
                "equivalent if preprocessing, colour order, normalisation and output decoding match what "
                "training used; most export bugs are interface mismatches, not arithmetic. Today you quantise a "
                "small weight list, dequantise it and measure the mean absolute error. Counting the error makes "
                "the trade-off visible and testable. The same check on real tensors is a standard pre-release "
                "gate, and it should run on frames that resemble production, not only tidy examples."
            ),
            code=(
                'WEIGHTS = [0.0, 0.5, 1.0, -1.0, 2.5]\n'
                'SCALE = 0.02\n'
                '\n'
                'def quantise(weights, scale):\n'
                '    return [max(-128, min(127, round(w / scale))) for w in weights]\n'
                '\n'
                'def dequantise(values, scale):\n'
                '    return [round(v * scale, 2) for v in values]\n'
                '\n'
                'stored = quantise(WEIGHTS, SCALE)\n'
                'restored = dequantise(stored, SCALE)\n'
                'error = sum(abs(a - b) for a, b in zip(WEIGHTS, restored)) / len(WEIGHTS)\n'
                'print("int8 values:", stored)\n'
                'print("restored:", restored)\n'
                'print("mean absolute error:", round(error, 4))\n'
                '\n'
                'assert stored == [0, 25, 50, -50, 125]\n'
                'assert error < 0.01\n'
                'print("quantisation is a scale, a clamp and a rounding error")'
            ),
            variant_b="use a scale of 0.05 and show which weights saturate at the int8 limit",
            variant_c="add a report of the maximum absolute error alongside the mean",
            mistakes=[
                "Choosing a scale that saturates many weights instead of covering the observed range.",
                "Comparing quantised and original outputs without checking preprocessing is identical.",
                "Assuming an export succeeded because the file loads, without a numerical parity test.",
            ],
            q1=(
                "What bounds the error of a quantised weight that stays inside the representable range?",
                "Half of one scale step, because the value is rounded to the nearest integer multiple of the scale.",
            ),
            homework=(
                "Write `quantise(weights, scale)` and `dequantise(values, scale)`, then report the mean absolute "
                "error. Run them on a short weight list at two scales, print the errors, and comment which line "
                "clamps values to the int8 range."
            ),
            patterns=["def ", "round", "print("],
            mapping=(
                "ONNX or TFLite export plus int8 quantisation is standard for edge vision; parity and error "
                "checks on representative frames are the release gate."
            ),
        ),
        161: dict(
            topic="Drift in visual data",
            idea=(
                "A model validated last month can quietly degrade without any code change, because the data "
                "arriving at it has changed. That is drift: a shift in the input distribution, the label "
                "distribution, or the relationship between them. In vision, common causes are a new camera, a "
                "moved light, seasonal colour, a lens cleaned or dirtied, or a scene that is simply busier at a "
                "new time of day. Drift is dangerous because every unit test still passes; only monitoring the "
                "live distribution catches it. The cheap signals are summary statistics per window: mean "
                "brightness, contrast, foreground fraction, detection count, and box size. Comparing a window "
                "with a reference window and flagging a large delta turns drift into a number rather than a "
                "feeling. The subtlety is that drift detection needs a baseline and a tolerance, and both must "
                "be chosen deliberately; too tight produces alert fatigue, too loose misses real degradation. "
                "Today you compute per-window means over chunked frame summaries and report the delta between "
                "windows. The example is small enough to read, but the shape scales: chunk by time, aggregate, "
                "compare, alert. The next step in a real system is to attach labels to a sample and check "
                "accuracy, not just the input statistics."
            ),
            code=(
                'WINDOWS = [\n'
                '    [100, 102, 98, 101],\n'
                '    [101, 99, 100, 100],\n'
                '    [140, 138, 142, 139],\n'
                ']\n'
                '\n'
                'def window_mean(values):\n'
                '    return round(sum(values) / len(values), 1)\n'
                '\n'
                'means = [window_mean(window) for window in WINDOWS]\n'
                'deltas = [round(means[i + 1] - means[i], 1) for i in range(len(means) - 1)]\n'
                'print("window means:", means)\n'
                'print("deltas:", deltas)\n'
                'print("drifted:", abs(deltas[-1]) > 20)\n'
                '\n'
                'assert means == [100.2, 100.0, 139.8]\n'
                'assert abs(deltas[-1]) > 20\n'
                'print("drift is a shift in the input distribution, not a bug in one frame")'
            ),
            variant_b="add a window with mean 101 and show that the drift flag clears after recovery",
            variant_c="compare the maximum value in each window instead of the mean and discuss which is noisier",
            mistakes=[
                "Watching only model outputs and never the input statistics.",
                "Alerting on a single frame instead of a window, which confuses noise with drift.",
                "Changing the reference baseline after an incident so the drift becomes invisible.",
            ],
            q1=(
                "Why is drift invisible to ordinary unit tests?",
                "The code and model are unchanged, so fixed test inputs still pass; only the live input distribution has moved.",
            ),
            homework=(
                "Write `window_mean(values)` and `drift_report(windows, tolerance)` returning means and deltas. "
                "Run them on three windows with one clear shift, print the report, and comment which line raises "
                "the drift flag."
            ),
            patterns=["def ", "sum(", "print("],
            mapping=(
                "Production vision teams monitor per-camera brightness, detection counts and confidence "
                "distributions to catch camera or scene drift before accuracy complaints arrive."
            ),
        ),
        162: dict(
            topic="Monitoring a vision service",
            idea=(
                "A deployed vision service needs a small set of numbers that answer whether it is working. The "
                "useful ones are ratios and percentiles, not single readings: error rate, empty-result rate, "
                "median and tail latency, and throughput. Averages hide the tail, and the tail is what users "
                "notice; a service that is fast on average but loses one frame in twenty has a queue problem. "
                "Empty results deserve their own counter because they are ambiguous. An empty frame can be a "
                "correct answer, a threshold that is too high, or a camera that has gone dark, and the code "
                "cannot tell the difference without history. Monitoring should therefore record status per "
                "inference call and aggregate over a window, with thresholds that trigger a review rather than "
                "an automatic restart. The same accounting makes the service testable: given a list of "
                "outcomes, the summary is a pure function, so the alert logic can be asserted on without a "
                "network or a clock. Today you summarise a short run list into error rate, empty rate and a tail "
                "cost, then print whether an alert should fire. Counting outcomes is the whole job; dashboards "
                "and log pipelines are transport for these same few numbers."
            ),
            code=(
                'RUNS = [("ok", 10), ("ok", 12), ("empty", 9), ("ok", 11), ("error", 0), ("empty", 10)]\n'
                '\n'
                'def summarize(runs):\n'
                '    total = len(runs)\n'
                '    errors = sum(1 for status, _ in runs if status == "error")\n'
                '    empties = sum(1 for status, _ in runs if status == "empty")\n'
                '    costs = sorted(cost for _, cost in runs)\n'
                '    tail = costs[min(total - 1, int(0.95 * total))]\n'
                '    return errors / total, empties / total, tail\n'
                '\n'
                'error_rate, empty_rate, tail = summarize(RUNS)\n'
                'print("error rate:", round(error_rate, 3))\n'
                'print("empty rate:", round(empty_rate, 3))\n'
                'print("tail cost:", tail)\n'
                'print("alert:", error_rate > 0.1 or empty_rate > 0.25)\n'
                '\n'
                'assert round(error_rate, 3) == 0.167\n'
                'assert tail == 12\n'
                'print("monitoring is a few rates and a percentile")'
            ),
            variant_b="add an all-empty run list and show that the empty rate becomes one and the alert fires",
            variant_c="report the median cost as well and explain when it is more useful than the tail",
            mistakes=[
                "Reporting only the mean latency, which hides the slow tail users actually experience.",
                "Treating every empty result as success when it may indicate a dark or disconnected camera.",
                "Setting alert thresholds so tight that routine noise pages the team every hour.",
            ],
            q1=(
                "Why track an empty-result rate separately from the error rate?",
                "Empty outputs are ambiguous between correct no-object frames, over-strict thresholds and camera failures, so their rate is a distinct signal.",
            ),
            homework=(
                "Write `summarize(runs)` returning error rate, empty rate and a tail cost from a list of status "
                "tuples. Run it on mixed outcomes, print the summary and alert flag, and comment which line "
                "computes the tail value."
            ),
            patterns=["def ", "sum(", "print("],
            mapping=(
                "Service dashboards track request errors, no-detection rates and p95 latency per camera; these "
                "same aggregates feed both alerting and post-incident review."
            ),
        ),
        163: dict(
            topic="Turning failures into tests",
            idea=(
                "Every production failure is a specification you did not write down. The productive response is "
                "to turn it into a test before fixing it: reproduce the input, assert the behaviour you "
                "actually want, and watch the test fail for the stated reason. That sequence proves the test "
                "is meaningful, which a test written after the fix never does. For vision code the inputs are "
                "often odd frames: all dark, all bright, one pixel, wrong shape, or a scene with no texture. "
                "These edge cases are cheap to construct as nested lists and they catch the failures that "
                "photogenic samples never touch. The test should assert on the smallest stable fact, such as "
                "the foreground count or whether a mask is empty, rather than an entire image, so it survives "
                "refactoring. Today you take a plausible failure, a detector returning nothing on a dark frame, "
                "and encode several cases as a table of input, expected count and reason. Running the table is "
                "the regression suite. The habit scales directly: a bug report becomes a named case, the case "
                "stays after the fix, and the suite grows in the shape of real operational pain rather than "
                "imagined scenarios. A test that cannot fail for the reported reason is just documentation."
            ),
            code=(
                'def detect(frame, threshold=100):\n'
                '    return [[1 if px >= threshold else 0 for px in row] for row in frame]\n'
                '\n'
                'def foreground(mask):\n'
                '    return sum(sum(row) for row in mask)\n'
                '\n'
                'CASES = [\n'
                '    ("bright object", [[0, 200], [0, 0]], 1),\n'
                '    ("dark frame", [[0, 0], [0, 0]], 0),\n'
                '    ("low contrast", [[40, 40], [40, 40]], 0),\n'
                ']\n'
                '\n'
                'for name, frame, expected in CASES:\n'
                '    got = foreground(detect(frame))\n'
                '    print(name, "foreground:", got, "expected:", expected)\n'
                '    assert got == expected\n'
                '\n'
                'print("every fixed failure becomes a permanent regression case")'
            ),
            variant_b="add a case for a one-pixel frame and confirm the detector still returns one value",
            variant_c="raise the threshold to 210 and show which existing cases change their expected count",
            mistakes=[
                "Writing the test after the fix, so it is never observed failing for the right reason.",
                "Asserting on a whole image dump, which breaks on any harmless refactor.",
                "Only testing happy-path frames and never the dark, empty or malformed ones.",
            ],
            q1=(
                "Why run the new test before fixing the failure?",
                "Seeing it fail for the stated reason proves the test actually reproduces the bug rather than passing for an unrelated cause.",
            ),
            homework=(
                "Write `regression_cases()` returning a table of `(name, frame, expected_count)` and a loop that "
                "asserts each one. Include a dark frame and a one-pixel frame, print every result, and comment "
                "which assertion captures the original failure."
            ),
            patterns=["def ", "assert", "print("],
            mapping=(
                "Incident reviews in vision deployments produce exactly these regression cases; keeping them "
                "cheap and deterministic is what makes the suite run in CI."
            ),
        ),
        164: dict(
            topic="Review: video, geometry and deployment checklist",
            idea=(
                "This phase moved from a single image to a running system. The checklist is short and each item "
                "is a question you can answer with a test. Is the stream a validated sequence with explicit "
                "frame indices, so gaps and ordering are known? Is there an explicit background or state model, "
                "and does it have a warm-up and a learning rate? Are detections matched to tracks with a gate, "
                "and are unmatched tracks and detections handled rather than dropped silently? Does the "
                "geometry use calibration constants with units, and does it fail loudly when disparity or depth "
                "is invalid? Is inference batched with the padding and latency cost accounted for? Does the "
                "total stage cost fit inside the frame interval and the memory budget? Is the exported model "
                "checked for numerical parity and quantisation error? Is there monitoring for error rate, "
                "empty results and tail latency, plus a drift baseline? Finally, does every field failure have a "
                "regression case? Today you run a compact checklist that exercises one representative "
                "computation from each area and prints a pass or fail line. It is not a substitute for the "
                "individual lessons; it is the integration test that tells you the pieces still agree with each "
                "other."
            ),
            code=(
                'def changed(a, b):\n'
                '    return sum(1 for ra, rb in zip(a, b) for x, y in zip(ra, rb) if x != y)\n'
                '\n'
                'def background(frames):\n'
                '    h, w = len(frames[0]), len(frames[0][0])\n'
                '    return [[round(sum(f[r][c] for f in frames) / len(frames)) for c in range(w)] for r in range(h)]\n'
                '\n'
                'def project(x, z, focal=50, cx=320):\n'
                '    return round(cx + focal * x / z, 1)\n'
                '\n'
                'FRAMES = [[[0, 0]], [[0, 90]], [[0, 90]]]\n'
                'checks = {\n'
                '    "motion counted": changed(FRAMES[0], FRAMES[1]) == 1,\n'
                '    "background averaged": background(FRAMES) == [[0, 60]],\n'
                '    "projection scaled": project(100, 200) == 345.0,\n'
                '    "budget respected": 3 + 2 + 20 <= 30,\n'
                '}\n'
                'for name, ok in checks.items():\n'
                '    print(name + ":", "PASS" if ok else "FAIL")\n'
                '\n'
                'assert all(checks.values())\n'
                'print("checklist complete:", len(checks), "checks")'
            ),
            variant_b="add a stereo check computing depth from a disparity of twenty and a baseline of sixty",
            variant_c="add a drift check comparing two window means and confirm the checklist still passes",
            mistakes=[
                "Treating the checklist as a substitute for the individual lessons it integrates.",
                "Checking only outputs while ignoring the units and calibration constants behind them.",
                "Declaring deployment ready without a regression case for the last production failure.",
            ],
            q1=(
                "What does this integration checklist verify that the individual lessons do not?",
                "That the pieces still agree with each other: frame state, geometry, budgets and monitoring are all exercised together with one set of data.",
            ),
            homework=(
                "Write `checklist(frames, stages, budget)` returning a dict of named boolean checks covering "
                "motion, background, projection and cost. Print each result, assert all pass, and comment which "
                "check would fail first if the frame indices were wrong."
            ),
            patterns=["def ", "assert", "print("],
            mapping=(
                "A deployment readiness review for vision services covers exactly these seams: stream integrity, "
                "state, geometry units, latency, memory, export parity and monitoring."
            ),
        ),
    },
)
