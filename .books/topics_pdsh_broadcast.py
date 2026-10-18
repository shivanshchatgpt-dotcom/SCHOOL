"""Canonical topic batch: broadcasting rules and rank expansion (PDSH ch 8)."""
from canonical_topics import topic

PDSH_CH8 = {
    "book": "python-data-science-handbook",
    "chapter": 8,
    "pages": [100, 108],
    "sections": ["Introducing Broadcasting", "Rules of Broadcasting",
                 "Centering an Array", "Plotting a Two-Dimensional Function"],
}


topic(
    "canonical:broadcasting",
    "Broadcasting lets a binary operation combine arrays of different shapes by virtually expanding the smaller one, so no copy is made and no loop is needed",
    sources=[dict(PDSH_CH8)],
    concept=(
        "Broadcasting is the rule that lets two arrays of different shapes participate in "
        "one element-wise operation. It works by comparing the shapes from the trailing "
        "axis backwards, and two axes are compatible when they are equal or when one of them "
        "is one, in which case that axis is virtually stretched to match the other. If any "
        "pair of axes is neither equal nor one, the operation raises, and the error message "
        "names the offending shapes, which is what makes the rule checkable by hand. The "
        "stretched array is not copied: the operation reads the same elements repeatedly, so "
        "a broadcast of a small array against a large one costs the memory of the small one. "
        "The practical uses are everywhere once recognised. Adding a vector to every row of a "
        "matrix is a broadcast, normalising each row by its own norm is a broadcast with "
        "keepdims, and centreing an array by subtracting its column means is a broadcast. "
        "The discipline this topic trains is to predict a broadcast's result before running "
        "it, because a shape that aligns by accident can produce a result that is the wrong "
        "shape and still runs, and a keepdims argument that is omitted is the single most "
        "common cause. Writing shapes down and comparing them from the right is the "
        "technique that resolves these cases in seconds."
    ),
    prerequisites=["canonical:vectorized-ufuncs"],
    pitfalls=[
        "Forgetting keepdims on a reduction whose result is meant to broadcast back against "
        "the original array, so the trailing axes no longer align.",
        "Assuming two shapes will broadcast because they have the same number of elements, "
        "when alignment is from the trailing axis and leading axes must match or be one.",
        "Relying on broadcasting to catch a shape error, when most shape errors raise but a "
        "few align accidentally and silently produce a result of the wrong shape.",
    ],
    adapters={
        "deep-learning": {
            "framing": (
                "Adding a bias vector to every row of an activation is a broadcast, and "
                "batch normalisation is a broadcast with carefully kept dimensions."
            ),
            "application": (
                "Walk the example as a linear layer's bias being added to a batch. The "
                "activation is batch by features and the bias is features, so the bias is "
                "stretched across the batch axis and no loop is needed, which is the "
                "simplest and most common broadcast in the whole field. The subtle case is "
                "normalisation: subtracting each row's mean requires the mean to keep its "
                "axis, because a reduced array of shape batch would not align against batch "
                "by features, while with keepdims it aligns exactly, and that one argument "
                "is the difference between a correct layer and a shape error. Predicting "
                "these results by comparing shapes from the trailing axis is what keeps a "
                "network's shape contracts verifiable while writing them rather than at "
                "runtime, and it is the habit that scales to complicated architectures."
            ),
            "example_hint": "add a bias across a batch and normalise rows with keepdims",
            "assessment_angle": "why the bias aligns without a loop and what keepdims preserves",
            "day": 6,
            "title": "Bias Broadcasts, Normalisation Keeps Its Dims",
            "code": """import numpy as np

activations = np.array([[1.0, 2.0, 3.0],
                        [4.0, 5.0, 6.0]])
bias = np.array([0.1, 0.2, 0.3])

biased = activations + bias
print("biased:\\n", biased)

row_mean = activations.mean(axis=1)
print("reduced shape:", row_mean.shape)
try:
    print(activations - row_mean)
except ValueError as exc:
    print("rejected:", exc)

kept = activations.mean(axis=1, keepdims=True)
centred = activations - kept
print("centred shape:", centred.shape, "row means now:", centred.mean(axis=1))

print("column-centred:\\n", activations - activations.mean(axis=0))

weights = np.array([2.0, 1.0, 0.5])
print("weighted:\\n", activations * weights)
""",
            "questions": [
                "Why can the bias vector be added to every row of the activation without a loop or a copy?",
                "The plain row mean fails to broadcast but the one with keepdims succeeds. What does keepdims change?",
                "What is the difference between centring by rows and centring by columns in this example?",
            ],
            "answers": [
                "Because the bias's feature axis matches the activation's feature axis and its missing batch axis is treated as one, so it is virtually stretched across the batch and read repeatedly rather than copied.",
                "It keeps the reduced axis as a length-one axis, so the result has shape batch by one and aligns with the activation's batch by features, whereas the collapsed shape would not align from the trailing axis.",
                "Row centring subtracts each row's own mean so every row averages to zero, while column centring subtracts each feature's mean across the batch so every feature averages to zero.",
            ],
            "homework": (
                "Write bias_broadcast.py with an activation array of at least three rows and three "
                "columns and a bias vector matching the feature count. Print the biased result, then "
                "attempt to subtract a plain axis-1 mean and print the rejection message, and do it "
                "again with keepdims=True printing the centred shape and each row's resulting mean. "
                "Print the column-centred array and a weighted array produced by multiplying with a "
                "per-feature vector. Observable output: six lines or blocks."
            ),
            "required_patterns": ["axis=1", "keepdims=True", "axis=0", "ValueError", "print("],
        },
        "computer-vision": {
            "framing": (
                "Per-channel normalisation and per-pixel brightness correction are both "
                "broadcasts, and mixing up the axes gives a garbled image rather than an "
                "error."
            ),
            "application": (
                "Walk the example as an image being corrected. A per-channel gain array of "
                "three values multiplies a height by width by channel image by stretching "
                "along the channel axis, and the alignment works because that axis is last "
                "and matches, which is why channel-last layout is so convenient for these "
                "operations. A per-column correction is a broadcast of a width-length array "
                "against the image, and here the axis is not last, so the correction has to "
                "be shaped to align, and that reshaping is where the trailing-axis rule "
                "becomes practical. The failure mode worth naming is that a wrongly shaped "
                "correction can still broadcast against a square image and silently produce "
                "the wrong adjustment, because every axis is equal and no error is raised, "
                "which is why the shapes have to be reasoned about rather than trusted. "
                "Normalising a batch of images by per-image statistics with keepdims is the "
                "case where a missing argument changes a correct pipeline into a broken one."
            ),
            "example_hint": "apply per-channel gain and per-column correction to an image by broadcasting",
            "assessment_angle": "why the trailing axis makes channel-last convenient and what a square image hides",
            "day": 6,
            "title": "Channel-Last Means a Gain Array Just Broadcasts",
            "code": """import numpy as np

image = np.arange(12, dtype=np.float32).reshape(2, 2, 3)
gain = np.array([1.0, 2.0, 0.5], dtype=np.float32)

adjusted = image * gain
print("per-channel adjusted:\\n", adjusted)

columns = np.array([10.0, 20.0], dtype=np.float32)
column_fix = image + columns.reshape(1, 2, 1)
print("per-column correction:\\n", column_fix)

per_image_mean = image.mean(axis=(0, 1), keepdims=True)
print("normalised shape:", (image / per_image_mean).shape)

square = np.arange(4, dtype=np.float32).reshape(2, 2)
wrong = square + np.array([1.0, 2.0])
print("silent shape alignment:\\n", wrong)

per_row = image.mean(axis=(1, 2), keepdims=True)
print("per-image mean shape:", per_image_mean.shape, per_image_mean.ravel())
""",
            "questions": [
                "Why does a three-element gain array align with a height by width by three image without any reshaping?",
                "The per-column correction reshapes the correction to (1, 2, 1). What would happen without that reshape?",
                "The final example adds a two-element array to a two by two square and succeeds. Why is that a warning rather than a convenience?",
            ],
            "answers": [
                "Because the channel axis is the trailing axis and its length matches, so broadcasting stretches the gain along the two spatial axes without any explicit reshaping.",
                "The two-element array would align against the trailing axis of length three and fail, because the widths would be compared as two against three and neither is one.",
                "Because the operation runs and produces a result whose shape is right by coincidence, so a correction meant for one axis gets applied to another and the error is visible only in the image, never in a message.",
            ],
            "homework": (
                "Write channel_broadcast.py with a two by two by three float image and a "
                "three-element gain array, printing the per-channel adjusted image. Build a "
                "per-column correction array and reshape it to align with the width axis, printing "
                "the corrected image, then print the shape of an image normalised by per-image "
                "statistics computed with keepdims. Demonstrate a silent alignment by adding a "
                "two-element array to a two by two square and printing the result, and print the "
                "per-image means with keepdims and their shape. Observable output: five lines or "
                "blocks."
            ),
            "required_patterns": ["axis=(0, 1)", "keepdims=True", ".reshape(", "image * gain", "print("],
        },
        "nlp": {
            "framing": (
                "Padding masks are broadcasts, and applying an attention mask is a "
                "broadcast between a batch of sequences and a batch of masks."
            ),
            "application": (
                "Walk the example as padding being masked out of a score matrix. The scores "
                "are batch by heads by queries by keys, and the mask is batch by keys, so "
                "the alignment depends entirely on which axis is last, and getting it right "
                "is the difference between masking the padding and masking the queries. The "
                "keepdims detail appears in layer normalisation, where statistics are "
                "computed over the feature axis with the dimension kept so the result "
                "broadcasts back, and omitting it is the classic cause of a shape error "
                "late in a build. Broadcasting a mask of additive negative infinities is the "
                "idiomatic way to hide padding from a softmax without changing its shape, "
                "because the mask aligns and the arithmetic is one expression. Reasoning "
                "about which axis a mask aligns against is the core skill this trains, and "
                "it is usually done by writing the two shapes down."
            ),
            "example_hint": "apply a padding mask by broadcasting and normalise over the feature axis with keepdims",
            "assessment_angle": "what a mask aligns against and why additive masking preserves the shape",
            "day": 6,
            "title": "Mask by Broadcasting, Hide Padding by Adding Infinity",
            "code": """import numpy as np

scores = np.array([[1.0, 2.0, 3.0],
                   [4.0, 5.0, 6.0]])
mask = np.array([0.0, 0.0, -np.inf])

masked = scores + mask
print("masked:\\n", masked)

probs = np.exp(masked - masked.max(axis=1, keepdims=True))
probs = probs / probs.sum(axis=1, keepdims=True)
print("probs:\\n", probs)

features = np.array([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]])
mean = features.mean(axis=1, keepdims=True)
std = features.std(axis=1, keepdims=True)
print("layer-norm style:\\n", np.round((features - mean) / std, 3))

pad_lengths = np.array([3, 2])
length_mask = np.arange(3)[None, :] < pad_lengths[:, None]
print("length mask:\\n", length_mask)
""",
            "questions": [
                "Why does adding a mask of zeros and negative infinity hide positions from the softmax without changing the shape?",
                "The layer-norm style computation uses keepdims=True on both statistics. What would the subtraction do without it?",
                "How does the length mask build its boolean array, and what does each row represent?",
            ],
            "answers": [
                "Because the mask aligns with the key axis and the infinities become zeros after the exponential, so those positions get no probability while the array keeps its shape throughout.",
                "The mean would collapse to shape (2,) and fail to align with the (2, 3) features from the trailing axis, so the subtraction would raise instead of normalising each row.",
                "It compares a broadcast position index against each sequence's padding length, so each row is a true where the position is a real token and a false where it is padding.",
            ],
            "homework": (
                "Write mask_broadcast.py with a scores matrix of at least two rows and three columns "
                "and a mask containing zeros and a negative infinity. Print the masked scores, then "
                "compute a stable softmax with the row maxima kept and print the probabilities. "
                "Compute a layer-norm style normalisation over the feature axis using keepdims for "
                "both the mean and the standard deviation and print the rounded result, and build a "
                "boolean length mask by comparing a broadcast position index against per-sequence "
                "lengths and print it. Observable output: four lines or blocks."
            ),
            "required_patterns": ["keepdims=True", "axis=1", "-np.inf", "[:, None]", "print("],
        },
        "time-series": {
            "framing": (
                "Normalising a multivariate series, removing a baseline and applying a "
                "per-channel calibration are all broadcasts."
            ),
            "application": (
                "Walk the example as a multivariate series being calibrated. Each channel "
                "has its own offset and scale, and applying them is a broadcast of a "
                "channel-shaped array against a time by channel series, which works because "
                "the channel axis is trailing. Removing a baseline measured over a "
                "reference period is a broadcast of one value per channel, and here the "
                "reduction that produced the baseline needs keepdims so it aligns with the "
                "series' two axes, which is the same detail as everywhere else but appears "
                "constantly in forecasting code. The instructive failure is a per-timestep "
                "correction applied to a square series, where a wrongly shaped array aligns "
                "accidentally and the correction lands along the wrong axis with no error, "
                "and in time series that specifically means a correction meant per channel "
                "being applied per time step. Writing the shapes down resolves it."
            ),
            "example_hint": "calibrate channels by broadcasting offsets and scales against a series",
            "assessment_angle": "which axis a channel array aligns against and what a square series hides",
            "day": 6,
            "title": "Calibrate Each Channel: One Broadcast, No Loop",
            "code": """import numpy as np

series = np.arange(10, dtype=np.float64).reshape(5, 2)
offset = np.array([1.0, -1.0])
scale = np.array([2.0, 0.5])

calibrated = (series + offset) * scale
print("calibrated:\\n", calibrated)

baseline = series[:3].mean(axis=0, keepdims=True)
print("baseline shape:", baseline.shape, "values:", baseline.ravel())
detrended = series - baseline
print("detrended:\\n", detrended)

mean = series.mean(axis=0, keepdims=True)
std = series.std(axis=0, keepdims=True)
print("per-channel normalised:\\n", np.round((series - mean) / std, 3))

square = np.arange(9, dtype=np.float64).reshape(3, 3)
print("accidental alignment:\\n", square + np.array([1.0, 2.0, 3.0]))
""",
            "questions": [
                "Why does a two-element offset array align with a five by two series?",
                "The baseline is computed with keepdims=True. What would the subtraction do without it?",
                "The final example adds a three-element array to a three by three square. Why does that succeed, and why is it not reassuring?",
            ],
            "answers": [
                "Because the channel axis is the trailing one and its length matches, so the offset is stretched along the time axis and applied to every time step of its channel.",
                "The mean would collapse to shape (2,), which has no leading time axis, and since the series is five by two the subtraction would raise rather than subtracting a baseline from every row.",
                "It succeeds because every axis is equal so broadcasting needs no stretching, and it is not reassuring because a correction meant for channels aligns equally well against time steps, so the mistake produces no error.",
            ],
            "homework": (
                "Write channel_calibrate.py with a series of at least five time steps and two channels, "
                "an offset array and a scale array, and print the calibrated series. Compute a "
                "baseline as the mean of the first three rows with keepdims and print its shape and "
                "values and the detrended series. Normalise per channel with keepdims on both the mean "
                "and standard deviation and print the rounded result, and demonstrate an accidental "
                "alignment by adding a three-element array to a three by three square. Observable "
                "output: five lines or blocks."
            ),
            "required_patterns": ["axis=0", "keepdims=True", "axis=1", ".reshape(", "print("],
        },
        "recommendation-systems": {
            "framing": (
                "Adding a user bias, an item bias and a global mean is the classic "
                "decomposition, and every term is a broadcast."
            ),
            "application": (
                "Walk the example as a matrix-factorisation score being assembled. The dot "
                "product gives one value per user-item pair, the user bias is a "
                "user-shaped array that broadcasts across all items, the item bias is an "
                "item-shaped array that broadcasts across all users, and the global mean is "
                "a scalar that broadcasts against everything, so the whole prediction is "
                "one expression with four terms of four different ranks. That structure is "
                "why biases are added after the dot product rather than folded into it, "
                "because broadcasting is what makes each term independently meaningful and "
                "independently learnable. The axis discipline appears in the outer product "
                "that builds the score matrix from two vectors: a user vector of shape "
                "(users, 1) and an item vector of shape (1, items) multiply into a users by "
                "items matrix, and the length-one axes are what broadcasting stretches. "
                "Reasoning about which axis each term aligns against is how a recommender's "
                "parameters stay attributable to users, items or the platform."
            ),
            "example_hint": "assemble a score from a dot product, a user bias, an item bias and a global mean",
            "assessment_angle": "how each term of a different rank contributes and why biases broadcast",
            "day": 6,
            "title": "User Bias, Item Bias, Global Mean: Four Ranks, One Expression",
            "code": """import numpy as np

users = np.array([[1.0, 0.0], [0.5, 0.5], [0.0, 1.0]])
items = np.array([[1.0, 0.5], [0.0, 1.0]])

dot = users @ items.T
print("dot product shape:", dot.shape)
print(dot)

user_bias = np.array([0.2, -0.1, 0.4])
item_bias = np.array([0.3, -0.2])
global_mean = 3.5

predicted = dot + user_bias[:, None] + item_bias[None, :] + global_mean
print("predicted:\\n", np.round(predicted, 2))

outer = user_bias[:, None] * item_bias[None, :]
print("bias interaction shape:", outer.shape)

centred = predicted - predicted.mean(axis=1, keepdims=True)
print("row-centred:\\n", np.round(centred, 2))
""",
            "questions": [
                "Why do the four terms of the prediction have different numbers of axes yet combine in one expression?",
                "What do the two None indexings in user_bias[:, None] and item_bias[None, :] achieve?",
                "Why is the global mean able to broadcast against a two-dimensional result at all?",
            ],
            "answers": [
                "Because broadcasting stretches each term's length-one or missing axes to match the result, so the scalar, the two vectors and the matrix all align to the users by items shape.",
                "They insert a length-one axis, turning the user bias into a column and the item bias into a row, so the two align against opposite axes of the score matrix instead of against each other.",
                "Because a scalar has no axes, so every axis of the result is stretched to accommodate it and the value is added to every position.",
            ],
            "homework": (
                "Write score_terms.py with a users matrix of at least three rows and two factors and an "
                "items matrix of at least two rows and two factors. Print the dot product of users "
                "with the transposed items matrix, then assemble a prediction as that dot product plus "
                "a user bias with an inserted axis, an item bias with an inserted axis and a scalar "
                "global mean, and print the rounded result. Print the shape of the bias interaction "
                "built by an outer product, and print the row-centred predictions using keepdims. "
                "Observable output: four lines or blocks."
            ),
            "required_patterns": ["[:, None]", "[None, :]", "keepdims=True", "@", "print("],
        },
        "reinforcement-learning": {
            "framing": (
                "Advantage normalisation, discount factors applied per step and batch "
                "statistics are all broadcasts, and the axis decides which is scaled."
            ),
            "application": (
                "Walk the example as a batch of advantages being normalised. The per-batch "
                "mean and standard deviation are scalars that broadcast against every "
                "element, and a per-episode normalisation would need keepdims and a "
                "different axis, so the choice of what is normalised is expressed entirely "
                "in the reduction's axes. Applying a per-agent or per-environment scale "
                "factor is a broadcast where the factor's axis has to align with the batch "
                "axis, and inserting a length-one axis is what makes it align rather than "
                "clash. The instructive failure is a discount applied to a square batch of "
                "rewards where a per-step factor and a per-episode factor have the same "
                "length, so the wrong one broadcasts silently and the returns are computed "
                "with the wrong weighting. Recognising that ambiguity is the practical "
                "skill, and the remedy is to write the shapes and to prefer an explicit "
                "axis insertion over relying on coincidence."
            ),
            "example_hint": "normalise advantages by broadcast and scale a batch with an inserted axis",
            "assessment_angle": "what a scalar broadcast normalises versus a kept-dims reduction and what a square batch hides",
            "day": 6,
            "title": "Normalise by Broadcast, Insert the Axis You Mean",
            "code": """import numpy as np

advantages = np.array([[1.0, 2.0], [3.0, 4.0]])

batch_mean = advantages.mean()
batch_std = advantages.std()
print("batch-normalised:\\n", np.round((advantages - batch_mean) / batch_std, 3))

per_row = advantages.mean(axis=1, keepdims=True)
print("per-episode centred:\\n", advantages - per_row)

scale = np.array([2.0, 0.5])
print("scaled batch:\\n", advantages * scale[:, None])

print("wrongly aligned:\\n", advantages * scale)

GAMMA = 0.9
discount = np.array([[GAMMA ** 0, GAMMA ** 1], [GAMMA ** 2, GAMMA ** 3]])
print("discounted:\\n", advantages * discount)
""",
            "questions": [
                "What do the batch mean and standard deviation broadcast against, and what does that normalisation produce?",
                "The scale array is used both with an inserted axis and without. What does each multiplication do, and why does the second run?",
                "Why is the discount example a case to be careful about?",
            ],
            "answers": [
                "Every element of the array, because they are scalars with no axes, so the result is the advantages rescaled to mean zero and standard deviation one across the whole batch.",
                "With the inserted axis the scale aligns with the batch axis and scales each row differently, and without it the array aligns with the trailing axis and scales each column instead, which runs because the array is square.",
                "Because the per-position discount weights and a per-episode scale have the same length on a square batch, so applying the wrong one broadcasts without error and silently misweights the returns.",
            ],
            "homework": (
                "Write advantage_normalise.py with an advantage array of at least three rows and two "
                "columns. Print the batch-normalised values using scalar mean and standard deviation, "
                "and print the per-episode centred values using an axis-one reduction with keepdims. "
                "Multiply the array by a per-row scale with an inserted axis and print it, then "
                "multiply by the same scale without an inserted axis and print that to show the "
                "different alignment, and print the array discounted by powers of a factor arranged "
                "per position. Observable output: five lines or blocks."
            ),
            "required_patterns": [".mean()", "keepdims=True", "[:, None]", "axis=1", "print("],
        },
        "gpu-programming": {
            "framing": (
                "Broadcasting on a device means reading a small array many times instead of "
                "materialising the expanded one, which is exactly the memory trade a kernel "
                "has to exploit."
            ),
            "application": (
                "Walk the example as broadcasts expressed as memory plans. A bias added to "
                "every row is a small array read repeatedly, so a kernel loads it once into "
                "fast memory and reuses it, and that is the device-level meaning of "
                "broadcasting: no expansion, only reuse. The shape rule is what tells a "
                "programmer whether a broadcast is possible at all, and comparing axes from "
                "the trailing one is the same exercise in numpy and in a launch's grid "
                "design. The failure mode that matters on a device is an accidental "
                "alignment: a square matrix accepts a mis-shaped vector without complaint, "
                "so a kernel written for the wrong axis produces correct-looking results "
                "that are computed from the wrong data, and the only defence is reasoning "
                "about the shapes beforehand. The scalar case is the cheapest of all, since "
                "a scalar broadcast is a register constant, and noticing that a term is "
                "scalar is worth doing before launching a kernel that would otherwise read "
                "it from global memory."
            ),
            "example_hint": "express bias reuse and accidental alignment and note what a scalar broadcast costs",
            "assessment_angle": "what broadcasting means for device memory and what a square matrix hides",
            "day": 6,
            "title": "Broadcasting Is Reuse: Load the Small Array Once",
            "code": """import numpy as np

matrix = np.arange(6, dtype=np.float32).reshape(2, 3)
bias = np.array([0.1, 0.2, 0.3], dtype=np.float32)

biased = matrix + bias
print("bias broadcast shape:", biased.shape, "bias bytes:", bias.nbytes)
print("no expansion: expanded would cost", matrix.size * bias.itemsize)

scalar = 2.0
print("scalar broadcast:", matrix * scalar)

column_bias = np.array([10.0, 20.0], dtype=np.float32)
print("column-aligned:\\n", matrix + column_bias[:, None])

square = np.arange(4, dtype=np.float32).reshape(2, 2)
row_vec = np.array([1.0, 2.0], dtype=np.float32)
col_vec = np.array([1.0, 10.0], dtype=np.float32)
print("row add:\\n", square + row_vec)
print("col add:\\n", square + col_vec[:, None])
""",
            "questions": [
                "Why does a broadcast not expand the small array in memory, and what is the device-level consequence?",
                "The scalar multiplication and the bias addition produce results of the same shape. How do their memory costs differ?",
                "The square matrix accepts two different additions that look almost identical in code. What distinguishes them, and why is that a hazard?",
            ],
            "answers": [
                "Because broadcasting reads the existing elements repeatedly rather than materialising a stretched copy, so on a device the small array can be loaded once into fast memory and reused across the whole grid.",
                "The scalar is a register constant with no memory traffic at all, while the bias is an array that has to be loaded, so the bias costs bandwidth and the scalar costs none.",
                "The row vector aligns with the trailing axis and the column vector with an inserted axis, so they scale different dimensions of the matrix, and the hazard is that both run on a square matrix and produce different results with no error.",
            ],
            "homework": (
                "Write broadcast_reuse.py with a float32 matrix of at least two rows and three columns "
                "and a bias vector matching the trailing axis. Print the broadcast result's shape and "
                "the bias's byte cost, and print what an expanded copy would have cost computed from "
                "the matrix size and element width. Multiply the matrix by a scalar and print it, add "
                "a column-aligned bias with an inserted axis and print it, and on a two by two square "
                "print both a trailing-axis addition and an inserted-axis addition to show they "
                "differ. Observable output: five lines or blocks."
            ),
            "required_patterns": [".nbytes", "[:, None]", ".itemsize", "matrix * scalar", "print("],
        },
        "own-ml-framework": {
            "framing": (
                "A framework has to implement broadcasting on purpose and reverse it in the "
                "backward pass, because the gradient of a broadcast is a reduction."
            ),
            "application": (
                "Walk the example as a framework adding two tensors of different shapes. "
                "The forward call aligns the shapes by the broadcasting rule and stores "
                "them, and the backward pass has to do the opposite: sum the incoming "
                "gradient back to each input's original shape along the axes that were "
                "stretched, because one output position contributed to several input "
                "gradients when it was broadcast. That duality, broadcast forward and "
                "reduce backward, is one of the few rules that govern every "
                "shape-changing operation in a framework, and implementing it once makes "
                "bias additions, normalisation layers and per-channel scaling all "
                "differentiable. The practical check is to verify that a gradient's shape "
                "matches the input's shape after the reduction, because a shape mismatch "
                "there is the signature of a missing reduction, and asserting it catches "
                "the defect at the operation instead of far away in training."
            ),
            "example_hint": "implement broadcast forward and the matching reduction backward",
            "assessment_angle": "why the backward pass reduces along stretched axes and what assertion catches a mistake",
            "day": 6,
            "title": "Broadcast Forward, Reduce Backward: One Rule for Every Shape Op",
            "code": """import numpy as np


def align(a, b):
    to_b = (1,) * (b.ndim - a.ndim) + a.shape
    return to_b


def backward_broadcast(grad, shape):
    while grad.ndim > len(shape):
        grad = grad.sum(axis=0)
    for axis, size in enumerate(shape):
        if size == 1 and grad.shape[axis] != 1:
            grad = grad.sum(axis=axis, keepdims=True)
    return grad


a = np.array([[1.0, 2.0]])              # (1, 2)
b = np.array([[3.0], [4.0]])            # (2, 1)
out = a + b
print("forward shape:", out.shape)

grad = np.ones((2, 2))
ga = backward_broadcast(grad, a.shape)
gb = backward_broadcast(grad, b.shape)
print("grad to a:", ga.shape, ga)
print("grad to b:", gb.shape, gb)

assert ga.shape == a.shape and gb.shape == b.shape
print("shape assertion held")
""",
            "questions": [
                "Why is the backward pass of a broadcast a reduction rather than another broadcast?",
                "What does align compute, and why does it pad with leading ones?",
                "What does the final assertion check, and what defect would it catch?",
            ],
            "answers": [
                "Because the forward stretch made one element contribute to several output positions, so the incoming gradient has to be summed back along the stretched axes to give each input a single gradient per element.",
                "The shape the smaller array would need to align with the larger, padded with leading ones because broadcasting compares axes from the trailing end and treats missing leading axes as length one.",
                "That each gradient's shape matches its input's shape, which catches a missing reduction that would otherwise leave a gradient with the broadcast shape and silently corrupt the update.",
            ],
            "homework": (
                "Write broadcast_backward.py with a backward_broadcast helper that sums away added "
                "axes and length-one axes until a gradient matches a target shape. Add a (1, 2) array "
                "to a (2, 1) array, print the forward shape, pass a gradient of ones through the "
                "helper for each input and print both resulting gradients with their shapes, and "
                "assert each shape equals its input's shape with a printed confirmation. Observable "
                "output: four lines."
            ),
            "required_patterns": [".sum(axis=0)", "keepdims=True", "assert", ".ndim", "print("],
        },
    },
)
