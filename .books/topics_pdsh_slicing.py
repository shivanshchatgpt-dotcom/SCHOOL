"""Canonical topic batch: NumPy indexing, slicing and views (PDSH ch 5)."""
from canonical_topics import topic

PDSH_CH5_INDEX = {
    "book": "python-data-science-handbook",
    "chapter": 5,
    "pages": [70, 80],
    "sections": ["Array Indexing: Accessing Single Elements",
                 "Array Slicing: Accessing Subarrays",
                 "Subarrays as No-Copy Views", "Creating Copies of Arrays"],
}


topic(
    "canonical:array-indexing-and-slicing",
    "Indexing picks one element and slicing picks a subarray, and a slice is a view whose writes reach the original array",
    sources=[dict(PDSH_CH5_INDEX)],
    concept=(
        "Indexing and slicing are how a rectangular array is reduced to the part a "
        "computation actually needs. A single index on each axis selects one element, and "
        "negative indices count from the end of an axis, so the last row and the last "
        "column are reachable without knowing the shape in advance. A slice on an axis "
        "selects a run of positions, and giving a slice on one axis and an index on another "
        "reduces dimensionality, which is how a row, a column or a plane is extracted from "
        "a multi-dimensional array. The behaviour that most often surprises people is that "
        "a slice is a view. It shares memory with the source array, so assigning through "
        "the view writes into the original, and this is the same sharing that assignment "
        "creates for lists, only with an extra trap: a view's shape can differ from the "
        "original's, so the write lands in a position the reader was not looking at. An "
        "explicit copy is the remedy whenever a subarray has to be modified independently, "
        "and it costs memory in exchange for safety. Slices can also take a step, which "
        "selects every k-th element and is how a series is downsampled or a matrix "
        "transposed-ish view is taken, and a step of minus one reverses an axis. The "
        "discipline worth building is to ask, before every write to a subarray, whether the "
        "source is still needed."
    ),
    prerequisites=["canonical:ndarray-attributes-and-shape"],
    pitfalls=[
        "Writing through a slice to modify a subarray and not realising the original array "
        "changed too, because the slice is a view sharing memory.",
        "Mixing a slice and an index and expecting the result to keep the same number of "
        "dimensions, when an index drops an axis.",
        "Using a negative step to reverse an axis and then assuming the elements are still "
        "at their original indices, which reverses the meaning of every index on that axis.",
    ],
    adapters={
        "deep-learning": {
            "framing": (
                "A residual connection stores an earlier activation and adds it back later, "
                "and if either side is a view of a tensor being mutated, the addition sees "
                "data the network never computed."
            ),
            "application": (
                "Walk the example as a residual connection implemented with slices. The "
                "input's first half is kept as a view, the second half is transformed, and "
                "the two are concatenated, so a write into the kept view would change the "
                "input tensor that the layer is still reading. The remedy shown is a copy "
                "at the point the subarray is stored, which is exactly the boundary at which "
                "ownership changes hands. Indexing versus slicing is the other distinction "
                "that matters in a network: selecting one sample with an integer drops the "
                "batch axis and gives a vector, while slicing with a range keeps the axis "
                "and gives a batch of one, and a loss function that expects a batch will "
                "behave differently for the two. Getting that distinction right is what "
                "makes a training loop's shapes stable across a forward pass."
            ),
            "example_hint": "split an activation into halves, transform one, copy the other, rejoin",
            "assessment_angle": "why the stored half needs a copy and what an index drops that a slice keeps",
            "day": 2,
            "title": "Residual Connections: Copy the Branch You Are Keeping",
            "code": """import numpy as np

x = np.arange(8, dtype=np.float64) * 0.5

first = x[:4].copy()        # stored branch: owned, not a view
second = x[4:]
transformed = second * 2.0 + 1.0

x[0] = 999.0                # late change to the input
print("stored branch:", first)

out = np.concatenate([first, transformed])
print("output:", out)

one_sample = x[0]           # index: axis dropped
batch_of_one = x[0:1]       # slice: axis kept
print("index ndim:", one_sample.ndim, "slice ndim:", batch_of_one.ndim)

print("reversed view:", x[::-1])
""",
            "questions": [
                "Why is the stored branch taken with copy rather than as a plain slice?",
                "one_sample comes from x[0] and batch_of_one from x[0:1]. Why do they have different numbers of dimensions?",
                "What does x[::-1] produce, and what happens to the meaning of index 0 on that view?",
            ],
            "answers": [
                "Because a plain slice is a view sharing the input's memory, so a later change to the input would retroactively change the stored branch, while a copy owns independent memory.",
                "Because an integer index selects one position and drops that axis, giving a zero-dimensional value, while a slice selects a run and keeps the axis, giving an array of length one.",
                "The same values in reverse order along the axis, so index 0 of the view is the last element of the original rather than the first.",
            ],
            "homework": (
                "Write residual_branch.py that builds a float vector of at least eight elements, "
                "stores its first half as a copy, transforms its second half in place, then "
                "mutates the original vector and prints the stored branch to show it is "
                "unaffected. Concatenate the stored branch with the transformed half and print "
                "the result. Also select one element by index and one by slice and print both "
                "shapes or dimension counts, and print a reversed view of the vector. Observable "
                "output: five lines."
            ),
            "required_patterns": [".copy()", "np.concatenate", "[::-1]", "[0:1]", "print("],
        },
        "computer-vision": {
            "framing": (
                "Cropping, flipping and patch extraction are all slicing, and because they "
                "are views, augmenting a crop in place corrupts the frame it came from."
            ),
            "application": (
                "Walk the example as augmentation pipeline reading crops from a frame. A "
                "crop is a slice, so it shares the frame's memory and brightening it in "
                "place would also brighten the region of every later crop taken from the "
                "same frame, which is how an augmentation loop silently leaks into the "
                "dataset. The copy at augmentation time is what keeps each crop an "
                "independent sample. Flipping with a negative step is the other common "
                "operation, and it is worth noticing that a flip is a view too, so writing "
                "into a flipped crop reaches the frame through reversed indices. Extracting "
                "a single channel with an index drops an axis while a slice over channels "
                "keeps it, and the distinction decides whether a filter written for a "
                "grayscale plane can accept the result."
            ),
            "example_hint": "crop a frame as a view and as a copy, flip with a negative step, extract a channel",
            "assessment_angle": "why augmentation must copy and what an index drops that a slice keeps",
            "day": 2,
            "title": "Augment a Copy of the Crop, Never the Frame",
            "code": """import numpy as np

frame = np.arange(16, dtype=np.uint8).reshape(4, 4)

crop_view = frame[:2, :2]
crop_copy = frame[:2, :2].copy()
crop_view[0, 0] = 255
print("view reached frame:", frame[0, 0], "copy safe:", crop_copy[0, 0])

augmented = frame[2:, 2:].copy()
augmented = augmented + 40
print("augmented corner:\\n", augmented)
print("frame corner:\\n", frame[2:, 2:])

flipped = frame[::-1]
print("last row first:", flipped[0])

channel_img = np.zeros((2, 2, 3), dtype=np.uint8)
plane = channel_img[:, :, 0]       # index drops the channel axis
kept = channel_img[:, :, 0:1]      # slice keeps it
print("plane shape:", plane.shape, "kept shape:", kept.shape)
""",
            "questions": [
                "After the crop taken as a view is modified, why has the frame changed too?",
                "The augmented copy has 40 added to it, but the frame's corner is unchanged. What would the frame have shown if the copy had been omitted?",
                "plane comes from an index and kept from a slice on the same axis. What does the shape comparison show, and why does it matter to a filter?",
            ],
            "answers": [
                "Because the slice is a view sharing the frame's memory, so the write through it lands in the frame's own storage.",
                "It would have shown the same brightened values, because the addition would have been applied to a view of the frame rather than to an independent array.",
                "Plane has two axes, because the index drops the channel axis, while kept has three, because the slice keeps it, so a filter that expects a grayscale plane can accept the first but not the second.",
            ],
            "homework": (
                "Write augment_crop.py that builds a four by four unsigned eight-bit frame, takes a "
                "two by two crop as a view and as a copy, modifies the view and prints both to show "
                "the frame changed. Take another crop as a copy, add a constant to it and print it "
                "beside the corresponding region of the unchanged frame. Print a flipped view's "
                "first row, then build a two by two by three image and extract one channel with an "
                "index and with a slice, printing both shapes. Observable output: six lines or "
                "blocks."
            ),
            "required_patterns": [".copy()", "[::-1]", ".shape", "[:, :, 0:1]", "print("],
        },
        "nlp": {
            "framing": (
                "Attention reads subsequences of a token matrix, and whether those reads are "
                "views decides whether caching them is safe."
            ),
            "application": (
                "Walk the example as an attention layer slicing a prefix of the sequence. "
                "The prefix is a view sharing the batch's memory, so storing it directly and "
                "then padding the batch would corrupt the cached keys, which is why a copy "
                "is taken when the prefix has to outlive the step. Selecting one sequence "
                "with an integer index gives a vector while slicing a range gives a batch "
                "of one, and the distinction is what an attention mask's shape depends on. "
                "Reversing an axis with a negative step is a useful diagnostic rather than a "
                "useful transform in NLP, since it destroys the time ordering the model is "
                "built on, and noticing that a reversed view still shares memory is the "
                "kind of detail that prevents a debugging step from becoming a bug."
            ),
            "example_hint": "slice a token prefix, copy it into a cache, and compare index against slice selection",
            "assessment_angle": "why a cached prefix needs a copy and what an index drops",
            "day": 2,
            "title": "Cache the Prefix as a Copy, Not a View",
            "code": """import numpy as np

tokens = np.array([[1, 2, 3, 4, 5],
                   [6, 7, 8, 9, 10]], dtype=np.int32)

prefix = tokens[:, :3].copy()
tokens[0, 0] = 999
print("cached prefix:", prefix[0])

kept_axis = tokens[0:1]
dropped_axis = tokens[0]
print("slice shape:", kept_axis.shape, "index shape:", dropped_axis.shape)

positions = np.arange(5)
print("reversed positions:", positions[::-1])

tail = tokens[:, 3:]               # a view of the last two positions
tail_view_copy = tokens[:, 3:].copy()
tail[0, 0] = -1
print("tail edit reached batch:", tokens[0, 3], "copy safe:", tail_view_copy[0, 0])
""",
            "questions": [
                "Why is the cached prefix a copy rather than the plain slice tokens[:, :3]?",
                "kept_axis comes from tokens[0:1] and dropped_axis from tokens[0]. Why do their shapes differ?",
                "The tail is taken as a view and as a copy. What does the final comparison show, and why?",
            ],
            "answers": [
                "Because the slice is a view sharing the batch's memory, so a later change to the batch would change the cached prefix as well, while a copy is independent and survives the edit.",
                "Because the slice keeps the batch axis, giving an array of shape (1, 5), while the integer index selects one sequence and drops that axis, giving shape (5,).",
                "That the view's edit reached the batch while the copy was unaffected, because the view shares the batch's memory and the copy does not.",
            ],
            "homework": (
                "Write prefix_cache.py with a token matrix of at least three sequences of six "
                "integers. Store the first three positions as a copy, mutate the original matrix "
                "and print the cached prefix to show it is unchanged. Select one sequence by index "
                "and one by slice and print both shapes, print a reversed view of a positions "
                "array, and take the last two positions both as a view and as a copy, editing the "
                "view and printing both to show the batch changed. Observable output: five lines."
            ),
            "required_patterns": [".copy()", "[::-1]", ".shape", "[0:1]", "print("],
        },
        "time-series": {
            "framing": (
                "Windowing a series is slicing, and because a window is a view, an entire "
                "windowed dataset can be presented without copying the series."
            ),
            "application": (
                "Walk the example as a series being windowed for a forecaster. Each window "
                "is a slice of the underlying array, so all the windows together cost "
                "almost no memory, and that is what makes windowed training feasible over "
                "years of data. The price is the same as any view: modifying a window "
                "changes the series, so a normalisation step has to be applied to a copy "
                "or the raw history is destroyed. Stepped slicing is the other building "
                "block, because a slice with a step selects every k-th point and that is "
                "downsampling, which is how a minute-level series is reduced to hourly "
                "without resampling. Selecting the last value with index minus one is the "
                "idiom for the most recent observation, and it works without knowing the "
                "length, which is why it appears in every serving path that reports the "
                "current value."
            ),
            "example_hint": "window a series as views, downsample with a step, take the last value by negative index",
            "assessment_angle": "when a window is free, what a step does, and why index -1 is idiomatic",
            "day": 2,
            "title": "Window for Free, Downsample with a Step, Read the Last by Index",
            "code": """import numpy as np

series = np.arange(20, dtype=np.float64)

windows = [series[i:i + 4] for i in range(0, 16, 4)]
print("window shapes:", [w.shape[0] for w in windows])
print("window shares memory:", windows[0].base is series)

windows[0][0] = -1.0
print("series head after window edit:", series[:4])

normalised = (series - series.mean()) / series.std()
print("normalised is a new array:", normalised.base is None)

hourly = series[::4]
print("downsampled:", hourly)

print("most recent:", series[-1], "first:", series[-20])
""",
            "questions": [
                "The windows are built as plain slices. What does the memory check show, and what does that imply about the cost of windowing?",
                "Why does editing windows[0] change the series, and what would have prevented it?",
                "What does series[::4] do, and why is index -1 the right way to read the most recent value?",
            ],
            "answers": [
                "That each window's base attribute points at the series, so the windows are views sharing its memory, which implies windowing costs almost nothing beyond the slice objects.",
                "Because the window is a view of the series' storage, so the write lands in the series itself, and taking a copy at windowing time would have prevented it.",
                "It selects every fourth element, downsampling the series, and index -1 reads the final position without needing to know the series length, which is why it is used in serving paths.",
            ],
            "homework": (
                "Write window_views.py with a float series of at least twenty values. Build windows of "
                "four consecutive values as plain slices, print their lengths and whether each one "
                "shares the series' memory, edit one window and print the affected part of the "
                "series. Compute a normalised copy and print whether it is a new array. Downsample "
                "the series with a step of four and print the result, and print the most recent and "
                "the twentieth-from-last value using negative indices. Observable output: five lines."
            ),
            "required_patterns": ["[::", ".base is", ".mean()", "[-1]", "print("],
        },
        "recommendation-systems": {
            "framing": (
                "A recommender repeatedly needs one user's history or one item's audience, "
                "and those are rows and columns obtained by slicing."
            ),
            "application": (
                "Walk the example as a user-item matrix being sliced. One user's history is "
                "a row and one item's audience is a column, and both are views, so a "
                "normalisation applied to a user's row in place would change the matrix "
                "every later computation reads. The copy at the point of modification is "
                "what keeps the raw matrix intact, which matters because a held-out "
                "evaluation has to score the original interactions rather than a "
                "normalised version of them. Selecting a subset of users by slicing keeps "
                "the axis and gives a matrix, while selecting one user by index drops it "
                "and gives a vector, and that distinction is what a similarity function's "
                "signature depends on. A negative step to reverse an item axis has a real "
                "use here: reversing into chronological order when the matrix is stored "
                "newest-last, so a recency-weighted score can be computed without copying."
            ),
            "example_hint": "slice a user's row and an item's column, copy before normalising, reverse for recency",
            "assessment_angle": "why in-place row normalisation is unsafe and what an index drops that a slice keeps",
            "day": 2,
            "title": "A Row Is a User, a Column Is an Item: Copy Before You Normalise",
            "code": """import numpy as np

matrix = np.array([[1, 0, 3, 0],
                   [0, 2, 0, 1],
                   [4, 0, 0, 2]], dtype=np.float64)

user_row = matrix[0]
user_copy = matrix[0].copy()
user_row[0] = 0.0
print("row edit reached matrix:", matrix[0, 0], "copy safe:", user_copy[0])

item_col = matrix[:, 2]
print("item column:", item_col, "shape:", item_col.shape)

subset = matrix[0:2]
print("subset shape:", subset.shape, "single shape:", matrix[0].shape)

chronological = matrix[:, ::-1]
print("reversed item order:", chronological[0])
print("shares memory:", chronological.base is matrix)
""",
            "questions": [
                "Why does zeroing an entry in the user's row change the matrix, and what would have prevented it?",
                "The item column and the user subset are both slices. Why does the column have shape (3,) while the subset has two axes?",
                "What does matrix[:, ::-1] produce, and why is it cheap?",
            ],
            "answers": [
                "Because the row is a view sharing the matrix's memory, so the write lands in the matrix itself, and a copy of the row before modifying it would have kept the original intact.",
                "Because the column slices one axis fully and indexes the other, dropping the row axis, while the subset slices both axes and keeps both, so it remains a two-dimensional matrix.",
                "A view of the same rows with each row's item order reversed, and it is cheap because no data is copied, only the axis direction changes.",
            ],
            "homework": (
                "Write row_column.py with a float user-item matrix of at least four users and five "
                "items. Take one user's row as a view and as a copy, modify the view and print both "
                "to show the matrix changed. Slice one item's column and print it with its shape, "
                "and slice a subset of users printing its shape beside the shape of one user taken "
                "by index. Reverse the item axis with a negative step, print one reversed row and "
                "whether the result shares the matrix's memory. Observable output: five lines."
            ),
            "required_patterns": ["[0]", ".copy()", ".shape", "[::-1]", "print("],
        },
        "reinforcement-learning": {
            "framing": (
                "An environment's observation often arrives as a stacked frame buffer, and "
                "slicing is how the most recent frames are pulled out of it."
            ),
            "application": (
                "Walk the example as a frame stack being consumed by a policy. The "
                "observation the network sees is a slice of the stack, and because it is a "
                "view, storing it in a transition without a copy makes the replay buffer a "
                "set of windows into a buffer that keeps changing, so the stored "
                "transitions would all show the latest frames. That is the sharpest form "
                "of the view trap, because the buffer would look correct in shape and be "
                "entirely wrong in content. Taking the last n frames with a negative-index "
                "slice is the idiom, and it works because negative indices address the end "
                "of the axis without knowing its length. Selecting one frame by index drops "
                "the stack axis and gives a single image, which is what a network expecting "
                "one channel needs, while slicing keeps the stack."
            ),
            "example_hint": "take the latest frames by negative-index slice and copy them into a transition",
            "assessment_angle": "why a stored observation must be copied and what a negative-index slice reads",
            "day": 2,
            "title": "The Latest Frames by Slice, Stored Once as a Copy",
            "code": """import numpy as np

stack = np.arange(12, dtype=np.float32).reshape(4, 3)

observation = stack[-2:]            # the last two frames
stored = stack[-2:].copy()
stack[-1, 0] = 77.0                 # environment advances
print("stored observation:", stored[1, 0])

one_frame = stack[-1]
frames = stack[-2:]
print("index shape:", one_frame.shape, "slice shape:", frames.shape)

buffer = []
buffer.append(stored)
stack[-2:] = 0.0
print("buffer after reset:", buffer[0])
print("stack now:\\n", stack)
""",
            "questions": [
                "Why is the observation stored as a copy of the slice rather than the slice itself?",
                "What does stack[-2:] select, and why does it work without knowing the stack's length?",
                "The final assignment writes zeros into a slice of the stack. What does that demonstrate about slices?",
            ],
            "answers": [
                "Because the slice is a view of the stack, so when the environment advances and the stack changes, the stored observation would change with it, while a copy keeps the transition the policy actually acted on.",
                "The last two rows, because negative indices count from the end of the axis, so the most recent frames are addressed without needing the stack length.",
                "That a slice is writable as well as readable, so assigning to it writes through the view into the source array, which is how a frame buffer is updated in place.",
            ],
            "homework": (
                "Write frame_stack.py with a float stack of at least six rows of three columns "
                "representing stacked frames. Take the last three frames with a negative-index "
                "slice, store a copy in a buffer list, advance the stack by mutating its last row "
                "and print the stored observation to show it is unchanged. Select one frame by "
                "index and three by slice and print both shapes, then assign zeros to a slice of "
                "the stack and print it to show the write reached the source. Observable output: "
                "five lines or blocks."
            ),
            "required_patterns": ["[-2:]", ".copy()", ".shape", "stack", "print("],
        },
        "gpu-programming": {
            "framing": (
                "A device kernel is launched on a sub-buffer, and a sub-buffer that is a "
                "view means the kernel's writes are visible to the host without a copy back."
            ),
            "application": (
                "Walk the example as a host array being sliced for a kernel. The slice is "
                "a view, so a kernel that writes into it produces results the host can read "
                "from the original array, and that is the cheapest form of device "
                "communication, with no explicit copy in either direction. The cost is "
                "aliasing: two overlapping views handed to the same kernel give "
                "non-deterministic results, so view offsets have to be chosen deliberately, "
                "and recognising which slices are views is what makes that choice possible. "
                "The step in a slice has a GPU meaning too, because a strided view "
                "corresponds to a memory access pattern, and a pattern that strides through "
                "memory can be dramatically slower than a contiguous one even when it reads "
                "the same number of elements. Copying a sub-buffer before a launch is the "
                "remedy whenever independence is required."
            ),
            "example_hint": "launch on a view, read the result from the host, and compare strided access",
            "assessment_angle": "what a view-based launch saves, when it is unsafe, and what a stride costs",
            "day": 2,
            "title": "Launch on a View, Mind the Stride, Copy When Independent",
            "code": """import numpy as np

host = np.zeros(8, dtype=np.float32)

def kernel(x, value):
    x[:] = value

tile = host[2:6]
kernel(tile, 7.0)
print("host after kernel on a view:", host)

strided = host[::2]
print("strided shape:", strided.shape, "contiguous:", strided.flags["C_CONTIGUOUS"])
print("contiguous tile contiguous:", tile.flags["C_CONTIGUOUS"])

independent = host[4:].copy()
kernel(independent, 1.0)
print("independent after kernel:", independent)
print("host tail unchanged:", host[4:])
""",
            "questions": [
                "The kernel writes into a slice of the host array and the result is read back from the host array. What makes that work without an explicit copy?",
                "Why can two overlapping views handed to the same kernel be unsafe?",
                "The strided view is not contiguous while the tile is. What does that difference mean on a device?",
            ],
            "answers": [
                "Because the slice is a view sharing the host array's memory, so the kernel's writes land in that memory and the host reads them through the original array.",
                "Because both views address some of the same memory, so the kernel's writes to one would race with its reads of the other, giving results that depend on the execution order.",
                "A strided view skips elements between accesses, which scatters memory reads and is far slower than a contiguous run, even when the number of elements touched is the same.",
            ],
            "homework": (
                "Write launch_view.py with a float32 host array of at least eight zeros, a fake kernel "
                "function that assigns a constant to a slice of its argument, and a call on a "
                "contiguous slice of the host array followed by a print of the whole array. Build a "
                "strided view and print its shape and whether it is contiguous, then take a "
                "sub-array as a copy, run the kernel on it and print both the copy and the "
                "unchanged host tail. Observable output: five lines."
            ),
            "required_patterns": ["[2:6]", "[::2]", ".copy()", ".flags[", "print("],
        },
        "own-ml-framework": {
            "framing": (
                "Slicing in a framework has to preserve enough information to reconstruct "
                "the gradient, which means tracking that a slice is a view of some other "
                "tensor."
            ),
            "application": (
                "Walk the example as a framework recording slice operations. A slice node "
                "in the computation graph stores whether it shares the source's memory, "
                "because the backward pass has to scatter the gradient into the right "
                "positions of the source's gradient rather than into a fresh tensor, and "
                "that is what makes slicing differentiable. The framework also has to "
                "decide which slices return views and which return copies, and exposing "
                "that choice explicitly is what lets a user reason about aliasing, because "
                "a framework that hides it produces gradients that silently leak between "
                "tensors that share memory. Reducing an axis with an integer index is the "
                "case where the shape bookkeeping matters most, since the gradient has to "
                "be expanded back along the dropped axis, and the forward shape is all the "
                "information needed to do it correctly."
            ),
            "example_hint": "record slice operations with a view flag and route the gradient accordingly",
            "assessment_angle": "why a framework must track views and what an index drop costs the backward pass",
            "day": 2,
            "title": "A Slice Is a Graph Node: Track the View, Route the Gradient",
            "code": """import numpy as np


class Tensor:
    def __init__(self, data, base=None):
        self.data = np.asarray(data)
        self.base = base

    def slice(self, spec):
        out = self.data[spec]
        return Tensor(out, base=self.data if out.base is self.data else None)

    def slice_copy(self, spec):
        return Tensor(self.data[spec].copy(), base=None)

    @property
    def is_view(self):
        return self.base is not None


t = Tensor(np.arange(6, dtype=np.float64))

view = t.slice(slice(0, 3))
copy = t.slice_copy(slice(0, 3))
print("slice is view:", view.is_view, "copy is view:", copy.is_view)

view.data[0] = 99.0
print("source after view edit:", t.data[:3])

indexed = t.slice(0)
sliced = t.slice(slice(0, 1))
print("index shape:", indexed.data.shape, "slice shape:", sliced.data.shape)
""",
            "questions": [
                "How does the framework decide whether a sliced tensor is a view, and why does the backward pass care?",
                "What does the slice_copy method give up that the plain slice does not?",
                "indexed comes from an integer index and sliced from a slice. Why will their backward passes differ in shape?",
            ],
            "answers": [
                "By comparing the sliced array's base attribute with the source's data, and the backward pass cares because a view's gradient has to be scattered into the source's gradient rather than stored in a standalone tensor.",
                "Independence of memory, since the copy cannot affect the source, but it also gives up the memory saving and the aliasing that let in-place kernels communicate results.",
                "Because the index drops an axis, so its gradient has to be expanded back along that axis, while the slice keeps the axis and its gradient already has the right shape.",
            ],
            "homework": (
                "Write slice_node.py with a small tensor class that stores its data and an optional "
                "base, whose slice method returns a tensor flagged as a view only when the result "
                "actually shares the source's memory, and whose slice_copy method always returns an "
                "independent tensor. Build a tensor of six values, take both kinds of slice from it "
                "and print which is a view, edit the view and print the source to show the "
                "connection, then take one element by integer index and one by slice and print both "
                "shapes. Observable output: five lines."
            ),
            "required_patterns": [".base", ".copy()", "slice(", ".is_view", "print("],
        },
    },
)
