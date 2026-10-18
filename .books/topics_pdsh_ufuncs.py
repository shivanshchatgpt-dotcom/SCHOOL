"""Canonical topic batch: vectorised computation with ufuncs (PDSH ch 6)."""
from canonical_topics import topic

PDSH_CH6 = {
    "book": "python-data-science-handbook",
    "chapter": 6,
    "pages": [81, 92],
    "sections": ["Introducing Ufuncs", "Exploring NumPy's Ufuncs"],
}


topic(
    "canonical:vectorized-ufuncs",
    "A ufunc applies one operation to every element of an array in compiled code, so a loop written in Python is replaced by a single call",
    sources=[dict(PDSH_CH6)],
    concept=(
        "A universal function is the mechanism NumPy uses to apply an operation to every "
        "element of an array without an explicit Python loop. Writing an arithmetic "
        "expression between arrays dispatches to a compiled routine that walks the data, so "
        "the same code that looks like element-wise mathematics is executed without "
        "interpreter overhead, and the speed difference over a large array is orders of "
        "magnitude rather than a constant factor. The second property is dtype handling: a "
        "ufunc promotes its inputs to a common type and returns a new array, so an "
        "operation on integers can produce floats and the result's dtype is what tells you "
        "what happened. Reductions are ufuncs too, so sum, min, max, mean and their "
        "relatives collapse an array along chosen axes and are the way a whole array "
        "becomes a few numbers. Two kinds of composition are worth knowing. Arithmetic "
        "ufuncs chain into expressions, so a formula written once applies everywhere, and "
        "an outer product builds a two-dimensional result from two one-dimensional inputs, "
        "which is how a distance or interaction matrix is computed without a nested loop. "
        "The failure mode that this topic corrects is writing an explicit loop over array "
        "elements, which is correct but slow by a factor that grows with the data, and "
        "recognising a loop as a candidate for a ufunc is the transferable skill."
    ),
    prerequisites=["canonical:ndarray-attributes-and-shape"],
    pitfalls=[
        "Writing an explicit Python loop over array elements when a single ufunc expression "
        "would do the same work in compiled code.",
        "Expecting an operation on an integer array to stay integer, when division promotes "
        "the result to float without warning.",
        "Applying a binary ufunc to arrays of incompatible shapes and treating the resulting "
        "error as a data problem rather than a shape problem.",
    ],
    adapters={
        "deep-learning": {
            "framing": (
                "Every activation function and every loss is a ufunc expression, and writing "
                "them as loops would make a training step take minutes instead of "
                "milliseconds."
            ),
            "application": (
                "Walk the example as a loss being computed for a batch. The predicted and "
                "target arrays are combined in one expression, and the subtraction, "
                "squaring and mean are each a ufunc applied to the whole array, so the loss "
                "of every sample is computed by compiled code in a single line. The "
                "reduction is what turns a per-sample array into the scalar the training "
                "loop actually minimises, and choosing the axis decides whether you get one "
                "loss per batch or one per feature. The outer product case appears in "
                "attention-style computations, where every query has to meet every key, and "
                "the ufunc builds that matrix without a nested loop. Noticing that an "
                "activation such as a sigmoid or a rectifier is a ufunc expression is what "
                "lets a network be written in the shape its framework expects, and the "
                "dtype promotion matters because a loss computed in integer arithmetic would "
                "be truncated to zero and never train."
            ),
            "example_hint": "compute a batch loss in one ufunc expression and reduce along the right axis",
            "assessment_angle": "what a single expression replaces and what the reduction axis decides",
            "day": 4,
            "title": "The Loss Is One Expression: Write It Without a Loop",
            "code": """import numpy as np

pred = np.array([[0.2, 0.5, 0.3], [0.7, 0.1, 0.2], [0.4, 0.4, 0.2]])
target = np.array([[0.0, 1.0, 0.0], [1.0, 0.0, 0.0], [0.0, 0.0, 1.0]])

per_sample = ((pred - target) ** 2).sum(axis=1)
print("per-sample loss:", per_sample)

batch_loss = per_sample.mean()
print("batch loss:", batch_loss)

def relu(x):
    return np.maximum(x, 0.0)

activations = np.array([-1.0, 2.0, -0.5, 3.0])
print("relu:", relu(activations))

logits = np.array([1.0, 2.0, 3.0])
print("sigmoid:", 1.0 / (1.0 + np.exp(-logits)))

ints = np.array([1, 2, 3])
print("integer division dtype:", (ints / 2).dtype)
""",
            "questions": [
                "Why can the loss be written as one expression rather than a loop over the batch?",
                "per_sample reduces with axis=1 and the batch loss reduces the result further. What does each reduction collapse?",
                "Why does dividing an integer array by two produce a float array?",
            ],
            "answers": [
                "Because each arithmetic operation is a ufunc that applies to the whole array in compiled code, so the subtraction, squaring and sum are each one vectorised step rather than per-element Python work.",
                "The first sums along the feature axis, collapsing each sample's errors into one number, and the second averages those numbers into a single scalar for the whole batch.",
                "Because true division is defined on real numbers, so the ufunc promotes the integer array to float to represent the fractional results rather than truncating them.",
            ],
            "homework": (
                "Write batch_loss.py with a predicted and a target array of at least four rows and "
                "three columns of probabilities. Compute the squared error as one ufunc expression, "
                "sum along the feature axis and print the per-sample losses, then average them and "
                "print the batch loss. Write a relu function using np.maximum and apply it to an "
                "array containing negative and positive values, and print the sigmoid of a small "
                "logit array. Finally show that dividing an integer array by two yields a float "
                "dtype and print it. Observable output: six lines."
            ),
            "required_patterns": ["** 2", "axis=1", ".mean()", "np.maximum", "print("],
        },
        "computer-vision": {
            "framing": (
                "Brightness, contrast and thresholding are per-pixel operations, and a ufunc "
                "does them to a whole image in one call."
            ),
            "application": (
                "Walk the example as an image being adjusted. Adding a constant brightens "
                "every pixel through one ufunc call, multiplying scales the contrast, and "
                "clipping with a minimum and maximum keeps the result inside the pixel "
                "range, all without a loop over rows and columns. The dtype behaviour is "
                "the detail that bites here: an unsigned eight-bit image plus a constant "
                "wraps around on overflow, so a brightening step can make bright pixels "
                "dark, and converting to a wider type before the arithmetic is the "
                "standard remedy. A threshold is a comparison ufunc that yields a boolean "
                "mask, and that mask is itself an array that can be counted and summed, "
                "which is how a vision pipeline reports the fraction of a frame above a "
                "value. The reduction case is computing per-row means to find the "
                "brightest band of the image, and the axis choice decides whether the "
                "result is one number per row or one per column."
            ),
            "example_hint": "brighten and clip an image with ufuncs and threshold it to a countable mask",
            "assessment_angle": "why per-pixel arithmetic needs a wider type and what a comparison ufunc returns",
            "day": 4,
            "title": "Brighten, Clip, Threshold: Per-Pixel Math Without a Loop",
            "code": """import numpy as np

image = np.arange(0, 256, 64, dtype=np.uint8).reshape(2, 2)
print("image:\\n", image)

wide = image.astype(np.int16)
brightened = np.clip(wide + 100, 0, 255).astype(np.uint8)
print("brightened:\\n", brightened)

overflow = image + 100
print("wrapped overflow:\\n", overflow)

mask = image > 128
print("mask:", mask, "count above:", mask.sum(), "of", mask.size)

row_means = image.mean(axis=1)
print("row means:", row_means)

contrast = (wide - wide.mean()) * 1.5 + 128
print("contrast dtype:", contrast.dtype)
""",
            "questions": [
                "Why does the brightening convert to a wider integer type first and clip the result?",
                "The mask is produced by a comparison and then summed. What does that sum count, and what does the comparison return?",
                "row_means uses axis=1. What would axis=0 have produced instead?",
            ],
            "answers": [
                "Because adding a constant to an unsigned eight-bit array overflows and wraps around, making bright pixels dark, so a wider type holds the intermediate values and clipping keeps them inside the pixel range before they are stored back.",
                "It counts the pixels above 128, and the comparison returns a boolean array of the same shape, which is itself an array whose true values can be summed.",
                "One mean per column instead of one per row, since the axis names the direction collapsed by the reduction.",
            ],
            "homework": (
                "Write pixel_math.py with a two by two or larger unsigned eight-bit image spanning a "
                "wide range of values. Convert it to a wider integer type, add a constant, clip to "
                "the pixel range with np.clip and print the result, then print the same addition "
                "done directly on the unsigned array to show the wraparound. Build a boolean mask "
                "with a comparison and print it with the count of true values and the total size. "
                "Compute the mean along both axes and print both results, and print the dtype of a "
                "contrast computation that subtracts the image's own mean. Observable output: six "
                "lines or blocks."
            ),
            "required_patterns": [".astype(", "np.clip", "axis=1", ".mean()", "print("],
        },
        "nlp": {
            "framing": (
                "Softmax, token-frequency counting and embedding normalisation are all ufunc "
                "expressions over arrays of numbers."
            ),
            "application": (
                "Walk the example as logits being turned into probabilities. The softmax "
                "subtracts the maximum for numerical stability, exponentiates, and divides "
                "by the sum, and each step is a ufunc over the whole array, so a "
                "vocabulary of any size is handled by one expression. The stability trick "
                "is worth understanding on its own: exponentiating large logits overflows "
                "to infinity, and shifting by the maximum keeps every exponent non-positive "
                "without changing the resulting distribution, which is a case where the "
                "vectorised form is not only faster but also the numerically sensible one. "
                "The reduction axis is the other decision, because a softmax over a batch "
                "must sum along the vocabulary axis rather than the batch axis, and the "
                "wrong axis produces rows that do not sum to one. Counting tokens with a "
                "comparison ufunc gives frequencies, and summing a mask is how a corpus's "
                "vocabulary coverage is measured."
            ),
            "example_hint": "compute a numerically stable softmax along the vocabulary axis and count tokens",
            "assessment_angle": "why the maximum is subtracted before exponentiating and what the sum axis decides",
            "day": 4,
            "title": "Softmax in One Expression: Stable, Vectorised, Right Axis",
            "code": """import numpy as np

logits = np.array([[2.0, 1.0, 0.5],
                   [0.1, 3.0, 0.2]])

shifted = logits - logits.max(axis=1, keepdims=True)
exp = np.exp(shifted)
probs = exp / exp.sum(axis=1, keepdims=True)

print("probs:\\n", probs)
print("row sums:", probs.sum(axis=1))

with np.errstate(over="ignore"):
    unstable = np.exp(np.array([1000.0, 1001.0, 1002.0]))
print("unstable has inf:", np.isinf(unstable).any())

ids = np.array([5, 5, 2, 9, 5, 2, 7])
print("count of token 5:", (ids == 5).sum(), "distinct:", len(np.unique(ids)))

embedding = np.array([[3.0, 4.0]])
print("normalised:", embedding / np.linalg.norm(embedding, axis=1, keepdims=True))
""",
            "questions": [
                "Why does the softmax subtract the row maximum before exponentiating?",
                "probs is divided by a sum along axis 1. What would rows look like if the sum used axis 0?",
                "How does counting a token with a comparison ufunc differ from iterating and incrementing a dictionary?",
            ],
            "answers": [
                "Because exponentiating a large logit overflows to infinity, and shifting by the maximum keeps every exponent at or below zero, so the exponentials stay finite while the resulting distribution is unchanged.",
                "They would not sum to one, because dividing by a column sum mixes the batch's rows instead of normalising each row over its own vocabulary.",
                "The comparison builds a boolean array in compiled code and sums it, so the count comes from one vectorised expression rather than a Python loop that updates a dictionary entry at a time.",
            ],
            "homework": (
                "Write softmax_stable.py with a logits array of at least three rows and four columns "
                "whose values differ by large amounts. Compute a stable softmax by subtracting the "
                "row maxima with keepdims, exponentiating and dividing by the row sums, and print "
                "the probabilities and each row's sum to show they are one. Print an unstable "
                "exponential of large values with a check for infinity. Count one token in an id "
                "array with a comparison ufunc and print the count and the number of distinct ids, "
                "and normalise a small embedding by its norm printing the result. Observable "
                "output: five lines or blocks."
            ),
            "required_patterns": ["axis=1", "keepdims=True", "np.exp", "np.unique", "print("],
        },
        "time-series": {
            "framing": (
                "Rolling statistics are reductions over windows, and ufuncs are what make "
                "them fast enough to compute over years of history."
            ),
            "application": (
                "Walk the example as a series being summarised. A mean over the whole array "
                "is one reduction, and a rolling mean over windows is the same reduction "
                "applied along a new axis created by windowing, so the two share the "
                "underlying ufunc. The reduction axis is the decision that matters: "
                "collapsing the time axis gives one number for the whole series while "
                "collapsing a channel axis gives one series per channel, and confusing them "
                "produces a single number where a per-series statistic was wanted. An "
                "outer product case appears in computing a distance matrix between every "
                "window and every other window, which is how anomaly detection finds the "
                "most unusual window without a nested loop. The overflow caution appears "
                "when a series of large integer counts is summed into a total that exceeds "
                "the element type, and a wider accumulator is the remedy."
            ),
            "example_hint": "compute whole-series and rolling reductions and a window distance matrix",
            "assessment_angle": "what the reduction axis decides and what an outer product builds",
            "day": 4,
            "title": "Mean the Whole Series, Mean the Windows: Pick the Axis",
            "code": """import numpy as np
from numpy.lib.stride_tricks import sliding_window_view

series = np.arange(20, dtype=np.float64)
print("whole-series mean:", series.mean())
print("min, max, std:", series.min(), series.max(), series.std().round(3))

windows = sliding_window_view(series, 5)
rolling = windows.mean(axis=1)
print("rolling mean length:", rolling.shape, "first two:", rolling[:2])

two_channel = np.stack([series, series * 2], axis=1)
print("per-channel means:", two_channel.mean(axis=0))

w = windows[:4]
distances = np.abs(w[:, None, :] - w[None, :, :]).sum(axis=2)
print("distance matrix shape:", distances.shape)
print(distances)

counts = np.full(1000, 2 ** 20, dtype=np.int32)
print("narrow sum dtype:", counts.sum().dtype, "overflowed:", counts.sum() < 0)
""",
            "questions": [
                "The rolling mean reduces with axis=1 on the windowed array. Why axis 1 rather than axis 0?",
                "What does the distance matrix computation build, and which ufunc arrangement replaces the nested loop?",
                "Why might summing many large int32 values need a wider accumulator?",
            ],
            "answers": [
                "Because axis 0 is the window axis and axis 1 is the positions within each window, so reducing axis 1 gives one mean per window while reducing axis 0 would average the windows together position by position.",
                "A matrix holding the distance between every pair of windows, built by subtracting every window from every other through broadcasting and summing along the position axis, which replaces an explicit loop over pairs.",
                "Because the running total can exceed the range of a 32-bit integer and wrap negative, so a wider accumulator keeps the sum correct.",
            ],
            "homework": (
                "Write rolling_stats.py with a float series of at least twenty values. Print the "
                "whole-series mean and its min, max and standard deviation. Window it with "
                "sliding_window_view, reduce along axis 1 and print the rolling mean's length and "
                "its first two values. Stack two channels and print the per-channel means by "
                "reducing along the time axis. Build a distance matrix between the first four "
                "windows using broadcasting and absolute values and print its shape and contents, "
                "and print the dtype of a sum over a thousand large int32 values noting whether it "
                "overflowed. Observable output: six lines or blocks."
            ),
            "required_patterns": ["sliding_window_view", "axis=1", ".mean()", "np.abs", "print("],
        },
        "recommendation-systems": {
            "framing": (
                "Similarity between a user and every item is one ufunc expression, and that "
                "is what makes scoring a whole catalogue affordable."
            ),
            "application": (
                "Walk the example as scores being computed for every item. The user's vector "
                "and the item matrix are combined with arithmetic ufuncs and a reduction "
                "along the feature axis, and the result is one score per item produced "
                "without a loop over the catalogue, which is the difference between a "
                "recommender that responds in milliseconds and one that does not respond "
                "at all. The reduction axis is the decision that makes it correct: "
                "collapsing the feature axis gives a score per item, while collapsing the "
                "item axis would give one number per feature, which is a summary of the "
                "catalogue rather than a ranking of it. Normalising vectors before a dot "
                "product turns it into a cosine similarity, and that normalisation is "
                "itself a ufunc expression over norms computed by reduction. The outer "
                "product case is how a user-item score matrix is built from a user axis and "
                "an item axis when there is no feature dimension to contract."
            ),
            "example_hint": "score every item with one reduction along the feature axis and rank them",
            "assessment_angle": "what the reduction axis produces and why normalisation turns a dot product into cosine",
            "day": 4,
            "title": "Score the Whole Catalogue in One Expression",
            "code": """import numpy as np

user = np.array([1.0, 0.5, 0.0, 0.8])
items = np.array([[1.0, 0.2, 0.0, 0.9],
                  [0.0, 1.0, 0.5, 0.0],
                  [0.4, 0.4, 0.4, 0.4]])

scores = (user * items).sum(axis=1)
print("scores:", scores)
print("best item:", items[scores.argmax()], "score:", scores.max())

wrong_axis = (user * items).sum(axis=0)
print("wrong-axis result:", wrong_axis)

norm = np.linalg.norm(user)
item_norms = np.linalg.norm(items, axis=1)
cosine = (user * items).sum(axis=1) / (norm * item_norms)
print("cosine similarity:", np.round(cosine, 3))

bias = np.outer(user, np.array([1.0, 0.5]))
print("outer shape:", bias.shape)
""",
            "questions": [
                "Why does the scoring reduce along axis 1 rather than axis 0?",
                "The wrong-axis result has the same number of values as the user's features. What does it represent instead of a ranking?",
                "What does dividing by the two norms do to the dot product?",
            ],
            "answers": [
                "Because axis 1 is the feature axis, so collapsing it gives one score per item, while axis 0 is the item axis and collapsing it would mix the items together.",
                "A per-feature total across the catalogue, which describes which features the items emphasise overall rather than how well each item matches the user.",
                "It divides out both vectors' lengths, so the result measures the angle between them and becomes a cosine similarity that is comparable across items of different magnitudes.",
            ],
            "homework": (
                "Write score_catalogue.py with a user vector of at least four features and an item "
                "matrix of at least four rows. Compute scores as an element-wise product reduced "
                "along the feature axis, print them and the best-scoring item with its score. "
                "Print the same product reduced along the item axis and note it is not a ranking. "
                "Compute cosine similarity by dividing the dot products by the product of the two "
                "norms and print the rounded values, and build an outer product of the user with a "
                "two-element vector printing its shape. Observable output: five lines."
            ),
            "required_patterns": ["axis=1", ".argmax()", "np.linalg.norm", "np.outer", "print("],
        },
        "reinforcement-learning": {
            "framing": (
                "Advantage estimation and target computation are ufunc expressions over "
                "transition batches, and the right reduction axis decides whether you get "
                "one number per step or one per field."
            ),
            "application": (
                "Walk the example as a return being computed for a batch of transitions. "
                "The immediate rewards are an array, the values estimated for the next "
                "states are another array, and the target combines them with arithmetic "
                "ufuncs into one array of targets, so the whole batch is updated by a "
                "single expression. The reduction decision appears in discounting: "
                "multiplying by a constant is a ufunc, and accumulating along the time axis "
                "with a reduction is how a discounted return is computed, while reducing "
                "along the field axis would collapse the trajectory's structure. The "
                "advantage is the difference between the target and the current value "
                "estimate, and it too is one expression, which matters because it is the "
                "signal the policy gradient uses. The clipping caution applies to a "
                "cumulative reward over many steps, where a naive dtype can overflow or "
                "lose precision, and an explicit wider accumulator or a normalisation keeps "
                "the signal usable."
            ),
            "example_hint": "compute discounted targets and advantages over a transition batch in one expression",
            "assessment_angle": "what each reduction axis produces and why advantage is a ufunc expression",
            "day": 4,
            "title": "Targets and Advantages: One Expression Per Batch",
            "code": """import numpy as np

rewards = np.array([1.0, 0.0, -0.5, 2.0])
next_values = np.array([0.5, 0.8, 0.6, 0.0])
current_values = np.array([0.4, 0.7, 0.9, 0.1])
GAMMA = 0.9

targets = rewards + GAMMA * next_values
print("targets:", targets)

advantages = targets - current_values
print("advantages:", advantages)
print("mean advantage:", advantages.mean())
print("normalised:", np.round((advantages - advantages.mean()) / advantages.std(), 3))

discounted = np.array([GAMMA ** i for i in range(4)]) * rewards
returns = np.cumsum(discounted[::-1])[::-1]
print("discounted returns:", returns)

mask = rewards > 0
print("positive steps:", mask.sum(), "of", mask.size)
""",
            "questions": [
                "Why can the target array be written as rewards + GAMMA * next_values rather than computed in a loop?",
                "What does the advantage expression compute, and why is its mean a useful number to print?",
                "The discounted return reverses, cumulatively sums and reverses again. What does that sequence produce?",
            ],
            "answers": [
                "Because the addition and multiplication are ufuncs applied element-wise to the whole arrays in compiled code, so one expression covers the entire batch without per-step interpreter work.",
                "The difference between the estimated target and the current value for each transition, and the mean shows whether the value function is on average over- or under-estimating the returns.",
                "The discounted return at each step, because reversing puts the future first, the cumulative sum then accumulates rewards from the end backwards, and reversing again restores the original time order.",
            ],
            "homework": (
                "Write targets_advantages.py with reward, next-value and current-value arrays of at "
                "least five steps and a discount factor. Compute targets in one expression and "
                "print them, compute and print the advantages with their mean and a normalised "
                "version, and compute discounted returns by weighting the rewards by powers of the "
                "discount, reversing, cumulatively summing and reversing back, printing the "
                "result. Build a boolean mask for positive rewards and print the count and total. "
                "Observable output: six lines."
            ),
            "required_patterns": ["GAMMA *", ".mean()", "np.cumsum", "[::-1]", "print("],
        },
        "gpu-programming": {
            "framing": (
                "A ufunc is a vectorised kernel, and writing one at array level is the "
                "bridge between numpy prototyping and device code."
            ),
            "application": (
                "Walk the example as a numerical kernel being expressed at array level. "
                "The element-wise function is written once and applied to the whole array, "
                "and that is the same shape a device kernel takes, so a ufunc prototype is "
                "the natural starting point for a GPU implementation. The reduction case "
                "matters because a sum over an axis is what a device reduction kernel has "
                "to reproduce, and choosing the axis decides whether the kernel collapses "
                "rows or columns, which changes both the output shape and the memory access "
                "pattern. The dtype behaviour is a device concern too, because a kernel "
                "compiled for float32 that receives float64 data either fails or silently "
                "loses precision, and the ufunc's promotion rules are the numpy-side "
                "expression of the same constraint. An outer product is the pattern for a "
                "matrix from two vectors, and on a device it is a two-dimensional grid, so "
                "recognising the shape in numpy is a step toward writing the launch."
            ),
            "example_hint": "express an element-wise kernel and an axis reduction at array level",
            "assessment_angle": "what a ufunc prototype shares with a device kernel and what the axis changes",
            "day": 4,
            "title": "A Ufunc Is a Kernel: Prototype at Array Level",
            "code": """import numpy as np

x = np.linspace(0.0, 1.0, 5, dtype=np.float32)

def kernel(x):
    return np.sin(x) * np.exp(-x) + 0.5

print("kernel output:", kernel(x))
print("output dtype:", kernel(x).dtype)

grid = np.arange(6, dtype=np.float32).reshape(2, 3)
print("row sums:", grid.sum(axis=1))
print("column sums:", grid.sum(axis=0))

a = np.array([0.0, 1.0, 2.0], dtype=np.float32)
b = np.array([1.0, 2.0], dtype=np.float32)
product = np.subtract.outer(a, b)
print("outer shape:", product.shape)
print(product)

mixed = np.float32(1) / np.float64(3)
print("promotion dtype:", mixed.dtype)
""",
            "questions": [
                "In what sense is the element-wise function a prototype for a device kernel?",
                "The grid is reduced along axis 1 and along axis 0. How do the two results differ in shape and meaning?",
                "What does np.subtract.outer build, and what device structure does it correspond to?",
            ],
            "answers": [
                "It applies one operation to every element without an explicit loop, which is exactly what a kernel does over its threads, so the array-level expression states the computation a launch has to implement.",
                "Axis 1 collapses each row into one number, giving a result of shape (2,), while axis 0 collapses each column, giving shape (3,), so they are per-row and per-column totals respectively.",
                "A two-dimensional array holding the difference of every element of the first vector from every element of the second, which corresponds to a two-dimensional kernel grid indexing both vectors.",
            ],
            "homework": (
                "Write kernel_prototype.py that builds a float32 array with np.linspace and applies an "
                "element-wise function of at least two ufuncs to it, printing the output and its "
                "dtype. Reshape an array to two by three and print its row sums and column sums, "
                "then build an outer product of a three-element and a two-element vector with "
                "np.subtract.outer and print its shape and contents. Finally print the dtype "
                "resulting from mixing a float32 and a float64 value in one operation. Observable "
                "output: six lines or blocks."
            ),
            "required_patterns": ["np.linspace", "axis=1", "axis=0", "np.subtract.outer", "print("],
        },
        "own-ml-framework": {
            "framing": (
                "A framework's operations are ufunc expressions with gradients attached, and "
                "the backward pass is itself a chain of ufuncs."
            ),
            "application": (
                "Walk the example as an operation recording its forward computation so the "
                "backward pass can be defined. A binary op stores which ufunc it used and "
                "the shapes of its inputs, because the backward pass has to produce a "
                "gradient for each input, and for element-wise operations those gradients "
                "come from the same kind of vectorised expression as the forward pass. The "
                "broadcasting question is central here: when the forward op broadcasts its "
                "inputs to a common shape, the backward pass has to sum the gradient back "
                "down to each input's original shape, and that reduction is what keeps a "
                "gradient on a broadcast axis from having the wrong number of dimensions. "
                "Recording the operation also lets a framework expose the composed "
                "expression, which is how a user inspects what actually ran, and it is the "
                "same information a tracing compiler would need to fuse those ufuncs into "
                "one kernel."
            ),
            "example_hint": "record a binary op with its inputs so the backward pass can reduce gradients back",
            "assessment_angle": "why the backward pass needs the input shapes and what broadcasting costs",
            "day": 4,
            "title": "Every Op Records Its Inputs: The Backward Pass Is Ufuncs Too",
            "code": """import numpy as np


class Tensor:
    def __init__(self, data, op=None):
        self.data = np.asarray(data, dtype=np.float64)
        self.op = op

    def add(self, other):
        out = Tensor(self.data + other.data, op=("add", self.data.shape, other.data.shape))
        return out

    def backward_add(self, grad):
        first, second = self.op[1], self.op[2]
        return _reduce_to(grad, first), _reduce_to(grad, second)


def _reduce_to(grad, shape):
    while grad.ndim > len(shape):
        grad = grad.sum(axis=0)
    for axis, size in enumerate(shape):
        if size == 1 and grad.shape[axis] != 1:
            grad = grad.sum(axis=axis, keepdims=True)
    return grad


a = Tensor(np.array([[1.0, 2.0]]))          # shape (1, 2)
b = Tensor(np.array([[3.0], [4.0]]))        # shape (2, 1)
c = a.add(b)
print("broadcast shape:", c.data.shape, "op:", c.op[0])

grad = np.ones((2, 2))
ga, gb = c.backward_add(grad)
print("grad to a:", ga, "shape", ga.shape)
print("grad to b:", gb, "shape", gb.shape)
""",
            "questions": [
                "Why does the op record the shapes of both inputs rather than only the output's shape?",
                "What problem does _reduce_to solve in the backward pass?",
                "The two inputs have shapes (1, 2) and (2, 1) but the output is (2, 2). What does that imply about the forward operation?",
            ],
            "answers": [
                "Because the backward pass has to produce one gradient per input, and each has to match that input's original shape, so both shapes are needed to reduce the upstream gradient correctly.",
                "It shrinks a gradient that was computed at the broadcast shape back to the input's shape, summing over the axes that broadcasting added so no gradient is lost.",
                "That the addition broadcast both inputs to a common shape, expanding each along the axis where it had length one, so the forward result has two rows and two columns.",
            ],
            "homework": (
                "Write op_record.py with a small tensor class whose add method records the operation "
                "name and both input shapes, and a _reduce_to helper that reduces a gradient to a "
                "target shape by summing added axes and length-one axes. Add a (1, 2) tensor to a "
                "(2, 1) tensor, print the broadcast shape and the recorded op, then pass a "
                "gradient of ones at the output shape through the backward helper and print both "
                "resulting gradients with their shapes. Observable output: three lines."
            ),
            "required_patterns": ["axis=0", "keepdims=True", "self.data + other.data", "while ", "print("],
        },
    },
)
