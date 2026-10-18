"""Canonical topic batch: NumPy array attributes, shape and views (PDSH ch 5).

Adapted paths are all zero-lesson data/ML paths; each day number starts a new
path at day 1 so a path taking every topic in dependency order gets a
contiguous run.
"""
from canonical_topics import topic

PDSH_CH5 = {
    "book": "python-data-science-handbook",
    "chapter": 5,
    "pages": [70, 80],
    "sections": ["NumPy Array Attributes", "Array Slicing: Accessing Subarrays",
                 "Subarrays as No-Copy Views", "Creating Copies of Arrays",
                 "Reshaping of Arrays"],
}


topic(
    "canonical:ndarray-attributes-and-shape",
    "An ndarray has one fixed dtype and a shape that names every axis, so reading the attributes is how you confirm what a computation actually received",
    sources=[dict(PDSH_CH5)],
    concept=(
        "A NumPy array differs from a list in three ways that follow from one decision: it "
        "holds elements of a single type, it lays them out in a rectangular block of "
        "memory, and it carries a shape that names the length of every axis. The attributes "
        "that describe this are the first thing to read when any array computation misbehaves. "
        "ndim counts the axes, shape gives each axis's length as a tuple, size is the total "
        "number of elements, dtype names the one type every element shares, and nbytes "
        "multiplies size by element width to give the memory cost. Because the dtype is "
        "fixed, assigning a float into an integer array silently truncates rather than "
        "changing the array's type, and that is the detail behind a large class of "
        "unexpected results. Because the shape names the axes in order, two arrays can hold "
        "the same numbers and still be incompatible, and the shape is what reveals it. The "
        "other defining property is that a slice of an array is a view, not a copy: it "
        "shares the same memory, so changing the slice changes the original, exactly as a "
        "shared reference does for a list, and an explicit copy is required whenever a "
        "subarray has to be independent. Reshaping is the natural companion, and it too "
        "returns a view when it can, so a reshaped array and its source remain connected "
        "until one of them is copied."
    ),
    prerequisites=["canonical:object-type-categories"],
    pitfalls=[
        "Reading values out of an array without checking shape first, so a batch that was "
        "supposed to be many samples turns out to be one sample of many features.",
        "Assigning a float into an integer array and expecting the array to widen, when the "
        "value is truncated to fit the existing dtype instead.",
        "Slicing an array to extract a sub-block and then modifying it, which changes the "
        "original array too because the slice is a view sharing memory.",
    ],
    adapters={
        "deep-learning": {
            "framing": (
                "Every layer contract in a network is a shape contract, and the difference "
                "between a batch of samples and a single sample of features is visible only "
                "in the attributes."
            ),
            "application": (
                "Walk the example as a forward pass receiving a batch and having its "
                "assumptions checked before any computation. The array's ndim, shape and "
                "dtype are printed first, and that is what reveals whether the input is one "
                "sample or many, and whether the values are floats or have been silently "
                "stored as integers. The truncation case is worth seeing directly, because "
                "an integer weight matrix that receives float updates would discard the "
                "fractional part of every gradient and the training loss would never improve, "
                "with no error raised. The view behaviour matters when a layer stores a "
                "slice of its input for a residual connection: mutating that slice would "
                "change the input tensor, so a copy is taken deliberately. Reading the "
                "attributes is the cheapest debug step in deep learning, and the one that "
                "settles most shape errors before any math is done."
            ),
            "example_hint": "print ndim shape dtype size of a batch before the forward pass and expose truncation",
            "assessment_angle": "what each attribute reveals and what integer truncation costs a training loop",
            "day": 1,
            "title": "Read the Batch Attributes Before You Touch the Math",
            "code": """import numpy as np

batch = np.array([[0.10, 0.25, -0.40],
                  [0.55, 0.00,  0.90],
                  [0.30, 0.70, -0.15],
                  [0.85, 0.45,  0.02]])

print("ndim :", batch.ndim)
print("shape:", batch.shape)
print("size :", batch.size)
print("dtype:", batch.dtype)
print("bytes:", batch.nbytes)

interpretation = "samples x features" if batch.ndim == 2 else "check axes"
print("reading:", interpretation)

weights = np.zeros((3, 2), dtype=np.int64)
weights[0, 0] = 0.9
print("stored float into int array:", weights[0, 0])

first = batch[0]            # a view, not a copy
copy = batch[0].copy()
first[0] = 99.0
print("view mutated original:", batch[0, 0], "copy safe:", copy[0])
""",
            "questions": [
                "What do ndim and shape together tell you that size alone does not?",
                "After a float is stored into the integer weight matrix, why is the printed value 0 rather than 0.9?",
                "The first row is taken twice, once by slicing and once with copy. Why does only one of them survive the mutation?",
            ],
            "answers": [
                "They give the number of axes and the length of each one in order, so the roles of the axes are known, whereas size only counts elements and would be identical for a batch of samples and a single sample of many features.",
                "Because the array's dtype is fixed as integer, so the value is converted to fit it and the fractional part is discarded, rather than the array widening to accept a float.",
                "Because the slice is a view sharing memory with the original, so mutating it reaches the source array, while copy duplicates the data so the copy is independent.",
            ],
            "homework": (
                "Write batch_attributes.py that builds a float array of at least five rows and four "
                "columns and prints its ndim, shape, size, dtype and nbytes, followed by a line "
                "interpreting the axes. Then build an integer array, store a float into one element "
                "and print the result, and take one row both as a plain slice and as a copy, mutate "
                "the slice, and print both to show only the copy is unaffected. Observable output: "
                "five attribute lines, an interpretation line, a truncation line and a comparison "
                "line."
            ),
            "required_patterns": [".ndim", ".shape", ".dtype", ".copy()", "print("],
        },
        "computer-vision": {
            "framing": (
                "An image is a height by width array, and colour adds a third axis. Getting "
                "that axis order wrong is the classic source of a rotated or striped result."
            ),
            "application": (
                "Walk the example as an image being loaded and inspected before any filter "
                "is applied. The array's ndim distinguishes a grayscale image from a colour "
                "one, and shape names the axis order the library used, which is the fact "
                "that decides whether the first index selects a row or a channel. The "
                "nbytes attribute is what tells you a camera frame is far larger than the "
                "model input it has to become, and that arithmetic is the basis of every "
                "downsampling decision in a vision pipeline. The view behaviour appears in "
                "cropping: a crop shares memory with the frame, so drawing on the crop also "
                "draws on the frame, and a copy is required when the crop has to be kept as "
                "evidence. The truncation case is visibly destructive here, because "
                "storing a float pixel into an unsigned eight-bit array wraps or clips "
                "without warning, which is how a normalised image becomes garbage when it "
                "is written back into the wrong buffer."
            ),
            "example_hint": "inspect an image array's axes, crop it as a view and as a copy, expose the pixel buffer's dtype",
            "assessment_angle": "how the axes are interpreted and why an integer pixel buffer silently corrupts float values",
            "day": 1,
            "title": "An Image Is Shaped: Inspect the Axes Before You Filter",
            "code": """import numpy as np

gray = np.arange(12, dtype=np.uint8).reshape(3, 4)
colour = np.zeros((3, 4, 3), dtype=np.uint8)

print("gray  ndim", gray.ndim, "shape", gray.shape)
print("colour ndim", colour.ndim, "shape", colour.shape)
print("bytes:", gray.nbytes, colour.nbytes)

crop_view = gray[:2, :2]
crop_copy = gray[:2, :2].copy()
crop_view[0, 0] = 255
print("view changed frame:", gray[0, 0], "copy safe:", crop_copy[0, 0])

frame = np.zeros((2, 2), dtype=np.uint8)
frame[0, 0] = np.uint8(300.0 % 256)
print("float 300 into uint8:", frame[0, 0])

print("interpretation:", "rows x columns" if gray.ndim == 2 else "unknown")
""",
            "questions": [
                "How does the shape of the colour image differ from the grayscale one, and what does the extra axis represent?",
                "Why does storing 300.0 into the unsigned eight-bit frame print 44 rather than raising an error?",
                "Why does the crop taken as a view change the original frame when the crop taken with copy does not?",
            ],
            "answers": [
                "The colour image has three axes, so its shape ends in a channel axis of length three, while the grayscale image has two axes, rows and columns, with no channel dimension.",
                "Because the dtype is fixed and narrower than the value, so the value is stored modulo the type's range and the overflow is silent rather than an error.",
                "Because the plain slice is a view that shares the frame's memory, so a write through it reaches the source, whereas copy duplicates the pixels into independent memory.",
            ],
            "homework": (
                "Write image_axes.py that builds a grayscale image array of at least four rows and "
                "five columns and a colour image array of matching height and width with three "
                "channels, both unsigned eight-bit, and prints each one's ndim, shape and nbytes. "
                "Take a two by two crop both as a plain slice and as a copy, mutate the slice and "
                "print both to show only the copy is unaffected. Store a value larger than 255 "
                "into the frame by first reducing it modulo 256, print the result, and print a "
                "line interpreting the grayscale axes. Observable output: two attribute blocks, a "
                "comparison line, a truncation line and an interpretation line."
            ),
            "required_patterns": ["np.", ".reshape(", ".ndim", ".copy()", "print("],
        },
        "nlp": {
            "framing": (
                "Text becomes numbers as a matrix of token identifiers, and whether the "
                "second axis is sequence length or vocabulary size decides what every "
                "downstream layer sees."
            ),
            "application": (
                "Walk the example as a tokenised batch being validated before it reaches a "
                "model. The array's shape distinguishes a batch of padded sequences, a "
                "single sequence, and a one-hot or embedding matrix, and reading it is what "
                "prevents a vocabulary-sized axis being treated as a time axis. The dtype "
                "matters more than usual here because token identifiers are integers and "
                " embeddings are floats, and an accidental integer dtype on an embedding "
                "matrix would truncate every learned vector to whole numbers without an "
                "error. The view behaviour appears in attention: slicing a subsequence to "
                "attend to gives a view, so writing into it would corrupt the original "
                "batch, and a copy is taken when the subsequence has to be cached. "
                "Reasoning about axis order is the core NLP engineering skill this topic "
                "trains, since a transformer's contracts are entirely expressed in shapes."
            ),
            "example_hint": "inspect a token batch's shape and dtype and slice a subsequence as a view and a copy",
            "assessment_angle": "what the axes mean and why an integer dtype would destroy embeddings",
            "day": 1,
            "title": "Tokens to Tensor: Shape Decides What the Model Reads",
            "code": """import numpy as np

batch = np.array([[5, 12, 7, 0, 0],
                  [3, 9, 14, 2, 0],
                  [11, 6, 8, 1, 4]])

print("shape:", batch.shape, "| ndim:", batch.ndim)
print("dtype:", batch.dtype, "| size:", batch.size)

axis_meaning = ("batch x sequence length" if batch.ndim == 2 else "unknown")
print("axes:", axis_meaning)

embeddings = np.zeros((3, 2), dtype=np.int64)
embeddings[0, 0] = 0.87
print("embedding stored as int:", embeddings[0, 0])

sub = batch[:, :3]              # view of the first three positions
sub_copy = batch[:, :3].copy()
sub[0, 0] = 999
print("view changed batch:", batch[0, 0], "copy safe:", sub_copy[0, 0])
""",
            "questions": [
                "The batch has shape (3, 5). What does each axis represent, and why does that interpretation matter to a model?",
                "An embedding value of 0.87 is stored into an integer array. What is retrieved, and what would the effect be on training?",
                "The first three positions are taken both as a view and as a copy. Why does mutating the view reach the original batch?",
            ],
            "answers": [
                "The first axis is the number of sequences in the batch and the second is the padded sequence length, which matters because a model reads one position per time step along the second axis and would misread the data if the axes were swapped.",
                "Zero, because the integer dtype discards the fractional part, so every learned embedding would be rounded away and the model could not represent continuous meaning.",
                "Because the slice shares the batch's memory rather than duplicating it, so a write through the view writes into the original, while the copy is a separate array.",
            ],
            "homework": (
                "Write token_tensor.py that builds a batch of at least four token-id sequences of "
                "equal length with padding zeros and prints its shape, ndim, dtype and size with a "
                "line naming the two axes. Build an integer array, store a float embedding value "
                "into it and print the result, then slice the first few positions of the batch "
                "both as a view and as a copy, mutate the view and print both to show the batch "
                "changed. Observable output: an attribute block, an axis line, a truncation line "
                "and a comparison line."
            ),
            "required_patterns": [".shape", ".ndim", ".dtype", ".copy()", "print("],
        },
        "time-series": {
            "framing": (
                "A series is an ordered array whose axis is time, and the shape tells you "
                "whether you hold one long series or many windows."
            ),
            "application": (
                "Walk the example as a series being shaped for a forecasting model. The "
                "array's ndim and shape distinguish a single continuous series, a stack of "
                "windows, and a multivariate series with several channels per time step, "
                "and that distinction is the first thing a forecaster's input contract "
                "checks. The dtype matters because a series of integer counts stored as "
                "floats costs twice the memory, and nbytes makes that cost explicit, which "
                "is a real concern when years of minute-level data are involved. The view "
                "behaviour is especially valuable here, because a sliding window can be "
                "presented as a view rather than a copy, so a large series can be windowed "
                "without duplicating its memory, and that is the trick that makes windowed "
                "training feasible on long histories. Recognising when a slice is free is "
                "the transferable skill."
            ),
            "example_hint": "inspect a series, reshape windows as views, and compare the copy cost",
            "assessment_angle": "what the axes mean for a forecaster and when a window is free",
            "day": 1,
            "title": "Windows Are Views: Shape a Series Without Copying It",
            "code": """import numpy as np

series = np.arange(12, dtype=np.float64)
print("series shape:", series.shape, "dtype:", series.dtype, "bytes:", series.nbytes)

windows = series[:8].reshape(2, 4)     # reshape of a slice: still a view
print("windows shape:", windows.shape)
windows[0, 0] = -1.0
print("series after window edit:", series[:4])

copy_windows = series[:8].reshape(2, 4).copy()
copy_windows[1, 0] = -5.0
print("series after copy edit:", series[4:8])

counts = np.arange(6, dtype=np.int32)
as_float = counts.astype(np.float64)
print("bytes int32 vs float64:", counts.nbytes, as_float.nbytes)
""",
            "questions": [
                "The eight-element slice is reshaped into two rows of four. Why does editing that reshaped array change the original series?",
                "The copy of the same reshaped array is edited too, but the series is unaffected. What does that contrast demonstrate?",
                "What does the final byte comparison tell you about storing integer counts as floats?",
            ],
            "answers": [
                "Because the slice is a view sharing the series' memory and reshape of a view is again a view, so the two-by-four array is another way of looking at the same numbers.",
                "That copy duplicates the data into an independent array, so its edits never reach the series, which is the property required when a window has to be kept as evidence.",
                "That the float version uses twice the memory of the int32 one, so storing counts as floats doubles the cost of a long history for no gain in information.",
            ],
            "homework": (
                "Write series_views.py that builds a float series of at least twelve values and prints "
                "its shape, dtype and nbytes. Slice and reshape it into windows without copying, print "
                "the window shape, edit one window element and print the affected part of the series to "
                "show the connection. Make a reshaped copy, edit it and print the series again to show "
                "no change. Finally build an int32 array and its float64 counterpart and print both "
                "nbytes values. Observable output: an attribute line, a window shape line, two series "
                "comparisons and a byte comparison."
            ),
            "required_patterns": [".reshape(", ".copy()", ".astype(", ".shape", "print("],
        },
        "recommendation-systems": {
            "framing": (
                "A recommender's core object is a matrix of users by items, and its shape "
                "and dtype decide whether the data is interactions, ratings or embeddings."
            ),
            "application": (
                "Walk the example as an interaction matrix being inspected before a model "
                "is fit. The shape names the two axes as users and items, and the dtype "
                "reveals whether the matrix holds counts, ratings or a dense float factor "
                "representation, which is what tells you whether a similarity computation "
                "is even meaningful on it. The size and nbytes attributes are how you "
                "decide whether a dense user-item matrix is affordable at all, since a "
                "million users against a hundred thousand items is a memory question "
                "before it is an algorithmic one, and that judgement starts with reading "
                "the attributes. The view behaviour matters for train-test splits: a slice "
                "of held-out users shares memory with the full matrix, so normalising the "
                "training portion in place would also change the held-out data, and a copy "
                "is required to keep the split honest."
            ),
            "example_hint": "inspect a user-item matrix's shape, dtype and cost, and copy before a split",
            "assessment_angle": "what dtype reveals about the matrix's meaning and why a split needs a copy",
            "day": 1,
            "title": "Users by Items: Read the Matrix Before You Score It",
            "code": """import numpy as np

interactions = np.array([[1, 0, 3, 0],
                         [0, 2, 0, 1],
                         [4, 0, 0, 2]], dtype=np.int32)

print("shape:", interactions.shape, "| users x items")
print("dtype:", interactions.dtype, "| size:", interactions.size, "| bytes:", interactions.nbytes)

held_out = interactions[:1]            # view of the first user
held_out_copy = interactions[:1].copy()
held_out[0, 0] = 0
print("view changed matrix:", interactions[0, 0], "copy safe:", held_out_copy[0, 0])

ratings = interactions.astype(np.float64)
print("as ratings dtype:", ratings.dtype, "bytes:", ratings.nbytes)

print("density:", (interactions > 0).sum(), "of", interactions.size)
""",
            "questions": [
                "What does the shape of the interaction matrix name, and why is that interpretation part of the data rather than the algorithm?",
                "The held-out user is taken as a view and as a copy. Why does zeroing the view change the matrix while the copy is unaffected?",
                "What do size and nbytes together tell you about whether a dense user-item matrix is affordable?",
            ],
            "answers": [
                "The number of users and the number of items, in that order, which is part of the data because the axis order is what makes a row a user's history and a column an item's audience.",
                "Because the view shares the matrix's memory, so the write reaches the source and would corrupt the held-out split, while the copy is independent and keeps the split honest.",
                "How many entries the matrix has and how many bytes each one costs, so their product gives the memory footprint that decides whether a dense representation is feasible.",
            ],
            "homework": (
                "Write matrix_inspect.py that builds an integer user-item interaction matrix of at "
                "least four users and five items with many zeros and prints its shape, dtype, size "
                "and nbytes with a line naming the axes. Take the first user both as a view and as a "
                "copy, zero an entry in the view and print both to show the matrix changed. Convert "
                "the matrix to float64 and print the new dtype and nbytes, and print how many "
                "entries are non-zero out of the total. Observable output: an attribute block, an "
                "axis line, a comparison line, a dtype and byte pair, and a density line."
            ),
            "required_patterns": [".shape", ".dtype", ".copy()", ".astype(", "print("],
        },
        "reinforcement-learning": {
            "framing": (
                "A reinforcement learning loop moves arrays between an environment and an "
                "agent, and their shape and dtype are the contract both sides negotiate."
            ),
            "application": (
                "Walk the example as a transition batch being inspected. The array's shape "
                "tells you whether you hold one observation or a batch of them, and whether "
                "the reward is packed into the same structure or kept separate, which is "
                "the kind of mismatch that produces a silently mis-averaged loss. The dtype "
                "on the observation matters because environments often return unsigned "
                "pixel bytes while a network needs floats, and the conversion has to be "
                "explicit rather than relied upon, since an accidental integer dtype would "
                "truncate normalised inputs to zero or one. The view behaviour appears in "
                "experience replay: storing a slice of the environment's observation means "
                "storing a reference, so a later in-place change to the environment's "
                "buffer would corrupt the stored transition, and a copy is what makes the "
                "replay buffer trustworthy."
            ),
            "example_hint": "inspect an observation and reward batch, and copy transitions into a replay buffer",
            "assessment_angle": "what the shape contract is between environment and agent and why the buffer copies",
            "day": 1,
            "title": "The Transition Contract: Shape In, Shape Out, Copied Once",
            "code": """import numpy as np

observations = np.array([[0.1, 0.0, 0.9],
                         [0.4, 0.2, 0.1],
                         [0.0, 0.8, 0.3]])
rewards = np.array([1.0, -0.5, 0.0])

print("observations:", observations.shape, observations.dtype)
print("rewards:", rewards.shape, rewards.dtype)

if observations.shape[0] != rewards.shape[0]:
    raise ValueError("batch sizes disagree")

buffer = []
buffer.append(observations[0].copy())       # not a view of the environment
observations[0, 0] = 99.0
print("stored transition:", buffer[0])

pixels = np.zeros((2, 2), dtype=np.uint8)
pixels[0, 0] = 250
normalised = pixels.astype(np.float64) / 255.0
print("pixel dtype:", pixels.dtype, "normalised dtype:", normalised.dtype)
""",
            "questions": [
                "Why does the code compare observations.shape[0] with rewards.shape[0] before doing anything else?",
                "The stored transition is a copy of the observation. What would a replay buffer contain instead if a view had been stored?",
                "Why is the pixel array converted to float64 before dividing by 255?",
            ],
            "answers": [
                "Because the two arrays have to describe the same number of steps, so the check catches a batch mismatch before rewards are averaged into a loss that would be silently wrong.",
                "It would contain a view of the environment's buffer, so a later in-place change of that buffer would retroactively change the stored transition and corrupt the training data.",
                "Because an integer division would truncate the result to zero for every pixel below 255, while converting to float first keeps the fractional normalised values.",
            ],
            "homework": (
                "Write transition_contract.py with an observations array of at least five rows of "
                "three floats and a rewards array whose length you choose deliberately, printing "
                "both shapes and dtypes and raising a clear error if the batch sizes disagree. Copy "
                "one observation into a replay buffer list, mutate the original array and print the "
                "stored transition to show it is unaffected. Build a small unsigned eight-bit pixel "
                "array, normalise it by converting to float64 before dividing by 255 and print both "
                "dtypes. Observable output: two attribute lines, a stored transition line and two "
                "dtype lines."
            ),
            "required_patterns": [".shape", ".dtype", ".copy()", ".astype(", "print("],
        },
        "gpu-programming": {
            "framing": (
                "An array's shape and dtype are the layout, and the layout is exactly what "
                "has to travel with the data when it moves between host and device."
            ),
            "application": (
                "Walk the example as a host buffer being prepared for a device kernel. The "
                "shape names how the kernel must index the data and the dtype names how "
                "many bytes each element occupies, so together they are the whole "
                "description a kernel needs, and the reason both are checked before any "
                "transfer is that a mismatched layout produces silently wrong results "
                "rather than an error. The nbytes attribute is what makes the transfer "
                "cost explicit, since a device copy is priced in bytes, and that is the "
                "arithmetic behind every decision about how much data to move per kernel "
                "launch. The view behaviour has a sharp GPU consequence: overlapping "
                "transfers and computation rely on slices that do not copy, so "
                "recognising which slices are views is what lets a pipeline overlap work "
                "without duplicating a large buffer, and it is also what makes a "
                "double-buffered scheme correct."
            ),
            "example_hint": "describe a buffer's layout and cost and slice it without copying",
            "assessment_angle": "why shape and dtype together are the layout, and what nbytes prices",
            "day": 1,
            "title": "Shape and Dtype Are the Layout That Travels to the Device",
            "code": """import numpy as np

buffer = np.arange(24, dtype=np.float32).reshape(4, 6)

print("shape:", buffer.shape, "| dtype:", buffer.dtype, "| bytes:", buffer.nbytes)
print("element width:", buffer.dtype.itemsize, "bytes")

if not buffer.flags["C_CONTIGUOUS"]:
    raise ValueError("kernel expects row-major layout")

half = buffer[:, :3]                    # a view: no device-side duplication
print("half shape:", half.shape, "is view:", half.base is not None)
print("half bytes if copied:", half.nbytes)

copy = buffer[:, :3].copy()
print("copy is view:", copy.base is not None)
""",
            "questions": [
                "Why are shape and dtype together sufficient to describe a buffer for a kernel, and what is missing from shape alone?",
                "What does nbytes let you compute, and why is that the first question when moving data to a device?",
                "The half-buffer is taken as a view and as a copy. How does the code demonstrate which is which, and what does that distinction buy?",
            ],
            "answers": [
                "Shape gives the length of every axis so the kernel can index correctly, and dtype gives the element width and representation so the kernel reads the right number of bytes per element, which shape alone omits.",
                "The transfer cost, since a device copy is priced in bytes, so nbytes is what decides how much data can move per kernel launch.",
                "By checking whether the array's base attribute is set, which is true for a view and false for a copy, and the distinction buys transfer-free sub-buffer access for overlapping work instead of duplicating a large buffer.",
            ],
            "homework": (
                "Write buffer_layout.py that builds a float32 array of at least four rows and six "
                "columns and prints its shape, dtype, nbytes and element width in bytes, then "
                "raises a clear error if the array is not row-major contiguous. Take a column slice "
                "as a view and as a copy, print each one's shape and whether its base attribute is "
                "set, and print how many bytes the view would cost if it were copied. Observable "
                "output: a layout block, a contiguity guard, two comparison lines and a byte count."
            ),
            "required_patterns": [".shape", ".dtype", ".itemsize", ".copy()", "print("],
        },
        "own-ml-framework": {
            "framing": (
                "When you build the array library yourself, shape and dtype stop being "
                "metadata and become the type system your framework is built on."
            ),
            "application": (
                "Walk the example as a minimal array wrapper reporting the attributes a "
                "framework depends on. ndim, shape, dtype, size and nbytes are exposed as "
                "properties because every operation in the framework will consult them "
                "before doing anything, and that is what makes shape checking a library "
                "responsibility rather than a caller's burden. The design decision worth "
                "naming is that a single fixed dtype is what allows contiguous storage and "
                "therefore the speed the framework exists to provide, and it is also what "
                "imposes the truncation semantics that a good wrapper should surface "
                "loudly instead of silently. Implementing copy separately from a view is "
                "the other foundational choice, because autograd needs to know which "
                "arrays share memory in order to build a correct computation graph, and a "
                "framework that cannot tell views from copies produces gradients that "
                "silently leak between tensors."
            ),
            "example_hint": "wrap an array, expose the attributes, and track which results share memory",
            "assessment_angle": "why shape and dtype form a type system and why view tracking matters for autograd",
            "day": 1,
            "title": "Shape and Dtype Are the Type System You Are Building",
            "code": """import numpy as np


class Tensor:
    def __init__(self, data):
        self.data = np.asarray(data)

    @property
    def shape(self):
        return self.data.shape

    @property
    def dtype(self):
        return self.data.dtype

    @property
    def size(self):
        return self.data.size

    def slice(self, spec):
        view = Tensor(self.data[spec])       # shares memory: a view
        view.base = self.data
        return view

    def detached(self):
        return Tensor(self.data.copy())      # independent: a copy


t = Tensor([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]])
print("shape:", t.shape, "dtype:", t.dtype, "size:", t.size)

view = t.slice((slice(None), slice(2)))
print("view shape:", view.shape, "shares base:", getattr(view, "base", None) is t.data)

independent = t.detached()
print("copy shape:", independent.shape, "shares base:", getattr(independent, "base", None) is t.data)

view.data[0, 0] = 99.0
print("owner after view edit:", t.data[0, 0])
""",
            "questions": [
                "Why does the wrapper expose shape and dtype as properties rather than reading them once at construction?",
                "How does the code distinguish a slice from a detached copy, and why would an autograd implementation care?",
                "Editing the view changes the original tensor's data. What would the framework need to do to prevent that when it is not wanted?",
            ],
            "answers": [
                "Because the underlying array's layout can change through reshape or transpose operations, so the properties report the current truth on every access instead of a stale value captured at construction.",
                "By recording whether the result shares the source's memory, which autograd needs because a view's gradient must flow to the tensor it shares memory with, while a copy's gradient should not.",
                "Take an explicit copy at the point the slice is created, so the result owns independent memory and writes through it cannot reach the original tensor.",
            ],
            "homework": (
                "Write tensor_wrapper.py with a small wrapper class around an ndarray exposing shape, "
                "dtype, size and nbytes as properties, plus a slice method that records that its "
                "result shares the source's memory and a detached method that returns a copy. Build "
                "a two-dimensional float tensor, print its attributes, take one slice and one "
                "detached copy, print each result's shape and whether it shares the source, then "
                "edit the slice and print the original to show the connection. Observable output: an "
                "attribute block, two comparison lines and a final ownership line."
            ),
            "required_patterns": ["np.asarray", "@property", ".copy()", ".shape", "print("],
        },
    },
)
