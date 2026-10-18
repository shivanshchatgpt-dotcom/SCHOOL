"""Canonical topic batch: NumPy reshaping, joining and splitting (PDSH ch 5)."""
from canonical_topics import topic

PDSH_CH5_SHAPE = {
    "book": "python-data-science-handbook",
    "chapter": 5,
    "pages": [70, 80],
    "sections": ["Reshaping of Arrays", "Array Concatenation and Splitting"],
}


topic(
    "canonical:array-reshaping-and-concatenation",
    "Reshaping changes how axes divide the same elements, joining stacks arrays along a chosen axis, and both are views until a copy is forced",
    sources=[dict(PDSH_CH5_SHAPE)],
    concept=(
        "Reshaping answers a question about the same data seen differently: the number of "
        "elements is fixed, and only how they are divided among axes changes, so any pair "
        "of shapes whose sizes multiply to the same total is a valid reshape of one "
        "another. The most common use is flattening a multi-dimensional array into a "
        "vector, and the second most common is folding a flat sequence into rows and "
        "columns so a computation that expects a batch can accept it. Reshaping is usually "
        "a view, so the reshaped array and its source share memory, and that is what makes "
        "it cheap and also what makes writes through a reshaped view reach the original. "
        "Inserting a length-one axis is a special case worth its own name, because it "
        "changes dimensionality without changing any data and is how a single sample is "
        "presented as a batch. Joining arrays is the complementary operation, and it takes "
        "an axis argument because two arrays can be stacked side by side or one after the "
        "other, with results of different shapes. Concatenate appends along an existing "
        "axis while stacking along a new axis adds one, and choosing between them is a "
        "matter of deciding whether the parts are more samples or a new kind of "
        "subdivision. Splitting undoes both, cutting an array along an axis at chosen "
        "positions, and the inverse relationship is what makes a pipeline that reshapes, "
        "joins and splits comprehensible."
    ),
    prerequisites=["canonical:ndarray-attributes-and-shape"],
    pitfalls=[
        "Reshaping to a shape whose sizes do not multiply to the original total, which "
        "raises rather than silently choosing a different shape.",
        "Writing through a reshaped array and expecting the source to be untouched, when a "
        "reshape is a view sharing the same elements.",
        "Concatenating along the wrong axis and getting an error or, worse, a result that "
        "stacks samples where features were expected because the axis lengths happened to "
        "agree.",
    ],
    adapters={
        "deep-learning": {
            "framing": (
                "A dataloader yields batches of one and the network expects a batch axis, "
                "so inserting a length-one axis is the everyday bridge."
            ),
            "application": (
                "Walk the example as a single sample being prepared for a network. The "
                "sample is a flat vector and the network's contract is batch by features, "
                "so a new axis is inserted and the shape becomes one by n without any "
                "element moving, which is the cheapest way to satisfy the contract. "
                "Flattening a convolutional feature map before a linear layer is the "
                "mirror operation, and it too is a view, so the reshape cost nothing while "
                "the weights still receive a two-dimensional input. Concatenation appears "
                "in multi-branch networks: two branches producing batch by features arrays "
                "are joined along the feature axis, and choosing axis 1 rather than axis 0 "
                "is what makes the result batch by combined features instead of a longer "
                "batch. Getting the axis right is the distinction between a wider layer "
                "and twice as many samples, and only one of them is what the architecture "
                "meant."
            ),
            "example_hint": "insert a batch axis, flatten a feature map, concatenate branches on the feature axis",
            "assessment_angle": "what inserting an axis costs and what the concatenate axis decides",
            "day": 3,
            "title": "Add the Batch Axis, Flatten, Join Branches on the Right Axis",
            "code": """import numpy as np

sample = np.arange(6, dtype=np.float32)
batch = sample[np.newaxis, :]
print("sample shape:", sample.shape, "-> batch shape:", batch.shape)

feature_map = np.arange(12, dtype=np.float32).reshape(2, 2, 3)
flat = feature_map.reshape(2, -1)
print("flattened shape:", flat.shape, "is view:", flat.base is feature_map)

flat[0, 0] = -1.0
print("reshape edit reached source:", feature_map[0, 0, 0])

branch_a = np.ones((2, 3), dtype=np.float32)
branch_b = np.zeros((2, 2), dtype=np.float32)
joined = np.concatenate([branch_a, branch_b], axis=1)
print("joined shape:", joined.shape)
print(joined)
""",
            "questions": [
                "What does inserting a new axis change about the array's data, and what does it change about its shape?",
                "After an element of the flattened array is edited, the feature map shows the change. Why?",
                "The two branches are joined with axis=1. What would axis=0 have produced, and why is that not what a wider layer needs?",
            ],
            "answers": [
                "Nothing about the data, since no element moves or is copied, but it adds a length-one axis so the shape gains a dimension and the array reads as a batch of one.",
                "Because the reshape is a view sharing the feature map's memory, so the write through the flattened array lands in the source's storage.",
                "A longer batch of five rows by three columns, since axis 0 is the batch axis, and that would mean more samples rather than the wider feature vector a concatenated layer is meant to receive.",
            ],
            "homework": (
                "Write batch_axis.py with a flat float vector of at least six values that inserts a new "
                "leading axis and prints both shapes. Build a three-axis feature map, flatten it with "
                "reshape using a minus one for the last dimension, print the flattened shape and "
                "whether it shares the source's memory, edit the flattened array and print the "
                "source to show the change. Concatenate two arrays with matching batch sizes but "
                "different feature counts along the feature axis and print the shape and contents. "
                "Observable output: six lines or blocks."
            ),
            "required_patterns": ["np.newaxis", ".reshape(", "np.concatenate", "axis=1", "print("],
        },
        "computer-vision": {
            "framing": (
                "An image batch is N by H by W by C, and reshaping between channel "
                "conventions is the plumbing every vision pipeline does once."
            ),
            "application": (
                "Walk the example as a batch of images being converted between conventions. "
                "The images arrive as batch by height by width by channel and a layer "
                "expects channels first, so the axes are reordered by reshape of a "
                "transposed view, and the total element count is what proves no data was "
                "lost, only rearranged. Flattening an image into a vector is the classic "
                "bridge from a convolutional backbone to a classifier head, and it is a "
                "view, so the flatten costs no memory at all. Stacking is how a set of "
                "single images becomes a batch, and it adds an axis where concatenate "
                "would have lengthened an existing one, so the choice between stack and "
                "concatenate is the choice between a new batch axis and more of an old "
                "one. Splitting is how a tiled inference result is cut back into per-image "
                "outputs, and the positions have to match the tiling or the crops are "
                "misaligned."
            ),
            "example_hint": "reorder a batch from channels-last to channels-first, flatten, stack, split",
            "assessment_angle": "what reshape guarantees about element count and how stack differs from concatenate",
            "day": 3,
            "title": "Reshape Is Rearrangement: Same Elements, Different Axes",
            "code": """import numpy as np

batch = np.arange(2 * 3 * 4, dtype=np.float32).reshape(2, 3, 4)
print("batch shape (N,H,W):", batch.shape)

flat = batch.reshape(2, -1)
print("flattened shape:", flat.shape, "elements kept:", flat.size == batch.size)

a = np.zeros((3, 4), dtype=np.float32)
b = np.ones((3, 4), dtype=np.float32)
stacked = np.stack([a, b], axis=0)
concat = np.concatenate([a, b], axis=0)
print("stack shape:", stacked.shape, "concat shape:", concat.shape)

tiles = np.arange(8, dtype=np.float32).reshape(4, 2)
parts = np.split(tiles, 2, axis=0)
print("split shapes:", [p.shape for p in parts])

channels_last = np.arange(2 * 2 * 3, dtype=np.float32).reshape(2, 2, 3)
channels_first = channels_last.transpose(2, 0, 1).reshape(3, 2, 2)
print("channels first shape:", channels_first.shape)
""",
            "questions": [
                "What does flat.size == batch.size demonstrate about the reshape, and why is that the first thing to check?",
                "stack and concatenate are given the same two arrays. Why do they produce shapes that differ in dimensionality?",
                "What does the transpose in the last step do that a plain reshape would not?",
            ],
            "answers": [
                "That the number of elements is unchanged, so the operation only rearranged how they are divided among axes, and it is the first check because any reshape that changes the total has discarded or invented data.",
                "Because stack inserts a new axis along which the inputs become slices, adding a dimension, while concatenate joins along an existing axis, keeping the dimensionality and lengthening that axis.",
                "It reorders the existing axes so the channel axis moves to the front, which changes which index selects what, whereas a plain reshape only relabels the same axis order.",
            ],
            "homework": (
                "Write rearrange_batch.py with a batch array of shape two by three by four and "
                "print its shape. Flatten it to two rows using a minus one for the last dimension "
                "and print the shape plus whether the element count is preserved. Stack two arrays "
                "of identical shape with np.stack and concatenate the same two with "
                "np.concatenate, printing both shapes, then split a four by two array into two "
                "parts along the first axis and print each part's shape. Finally transpose a "
                "channels-last array to channels-first and print the resulting shape. Observable "
                "output: six lines."
            ),
            "required_patterns": [".reshape(", "np.stack", "np.concatenate", "np.split", "print("],
        },
        "nlp": {
            "framing": (
                "Token ids come shaped as one thing and attention needs them shaped as "
                "another, so reshaping is the step between every stage of a text pipeline."
            ),
            "application": (
                "Walk the example as a tokenised corpus being reshaped for batching. A flat "
                "list of identifiers is folded into rows whose length is the sequence "
                "length, and the total element count is what guarantees the fold lost "
                "nothing, which matters because a fold that drops the final partial row "
                "would silently discard sentences. Padding to a common length is the case "
                "where elements are added rather than just rearranged, so it is a join of "
                "the content with a pad array along the sequence axis. Stacking is how "
                "individual sequences become a batch, adding a new axis instead of "
                "lengthening the sequence one, and the choice between the two is what "
                "decides whether you have more samples or longer samples. Splitting along "
                "the sequence axis is how a model is given a prefix and a suffix separately, "
                "for example when a prompt and a completion are processed as one tensor and "
                "then separated for scoring."
            ),
            "example_hint": "fold a flat token list into a batch, pad to a fixed length, stack and split",
            "assessment_angle": "what element count proves about a fold and how stack and concatenate differ",
            "day": 3,
            "title": "Fold the Corpus, Pad the Short Rows, Stack the Batch",
            "code": """import numpy as np

ids = np.arange(12, dtype=np.int32)
batch = ids.reshape(3, -1)
print("flat:", ids.shape, "folded:", batch.shape, "count kept:", batch.size == ids.size)

short = np.array([1, 2, 3], dtype=np.int32)
pad = np.zeros(2, dtype=np.int32)
padded = np.concatenate([short, pad], axis=0)
print("padded row:", padded)

seq_a = np.array([1, 2, 3], dtype=np.int32)
seq_b = np.array([4, 5, 6], dtype=np.int32)
print("stacked batch:", np.stack([seq_a, seq_b], axis=0).shape)
print("concatenated:", np.concatenate([seq_a, seq_b], axis=0).shape)

prompt_and_completion = np.arange(8, dtype=np.int32).reshape(2, 4)
prompt, completion = np.split(prompt_and_completion, 2, axis=1)
print("prompt shape:", prompt.shape, "completion shape:", completion.shape)
""",
            "questions": [
                "What does the element-count check on the folded batch prove, and why is it necessary after folding?",
                "The short sequence is padded by concatenating with a pad array. Why is that a join rather than a reshape?",
                "Stacking the two sequences and concatenating them give different shapes. What does each one represent?",
            ],
            "answers": [
                "That the fold divided the same identifiers into rows without dropping or duplicating any, which is necessary because a fold that does not divide evenly would silently discard a partial final row.",
                "Because padding adds elements that were not in the original sequence, so the total changes and the operation has to join new values, while a reshape only rearranges a fixed number of elements.",
                "Stacking gives shape (2, 3), a batch of two sequences, while concatenating gives shape (6,), one longer sequence, so the first is more samples and the second is a longer one.",
            ],
            "homework": (
                "Write fold_corpus.py with a flat array of at least twelve integer token ids that "
                "folds into rows with reshape and prints both shapes and whether the element count "
                "is preserved. Pad a short sequence by concatenating a pad array along the sequence "
                "axis and print it. Stack two equal-length sequences and concatenate the same two, "
                "printing both shapes, and split a two by four array of prompt and completion "
                "columns into two parts printing both shapes. Observable output: six lines."
            ),
            "required_patterns": [".reshape(", "np.concatenate", "np.stack", "np.split", "print("],
        },
        "time-series": {
            "framing": (
                "Turning a long series into windowed samples is a reshape, and doing it "
                "with a stride makes windowing cheap enough for years of data."
            ),
            "application": (
                "Walk the example as a long series being converted into supervised "
                "samples. Each sample is a window of consecutive values followed by the "
                "next value as its target, and reshaping the series into rows is the "
                "fastest way to produce them, with the element count confirming that no "
                "observation was lost in the fold. The subtlety is that a plain reshape "
                "produces non-overlapping windows, while a forecaster usually wants "
                "overlapping ones, and the difference is exactly what a stride controls, "
                "so the sliding-window construction is a reshape with an offset rather "
                "than a reshape of the whole array. Stacking a set of univariate series "
                "into a multivariate array is the join case that matters here, because it "
                "adds a channel axis rather than lengthening the time axis, and the choice "
                "decides whether the model sees several signals at each time step or one "
                "signal over more time. Splitting along the time axis is how a train and "
                "test portion are separated chronologically."
            ),
            "example_hint": "fold a series into windows, build overlapping samples, stack channels, split chronologically",
            "assessment_angle": "why non-overlapping reshape is not enough and what stacking adds",
            "day": 3,
            "title": "Fold the Series, Slide the Window, Stack the Channels",
            "code": """import numpy as np
from numpy.lib.stride_tricks import sliding_window_view

series = np.arange(12, dtype=np.float64)

non_overlapping = series.reshape(3, 4)
print("non-overlapping windows:", non_overlapping.shape)

windows = sliding_window_view(series, 4)
print("sliding windows:", windows.shape)
print("first two samples:\\n", windows[:2])

a = np.arange(5, dtype=np.float64)
b = np.arange(5, dtype=np.float64) * 2
multivariate = np.stack([a, b], axis=1)
print("multivariate shape:", multivariate.shape)

train, test = np.split(series[:10], [8])
print("train shape:", train.shape, "test shape:", test.shape)
""",
            "questions": [
                "Why does a forecaster need sliding_window_view rather than a plain reshape of the series?",
                "What does stacking the two univariate series with axis=1 produce, and what does that axis represent?",
                "What does np.split with the list [8] do, and why is the split position a chronological decision?",
            ],
            "answers": [
                "Because a plain reshape produces non-overlapping windows, using each value once, while a forecaster needs every consecutive group as a sample, which sliding_window_view produces by offsetting each window by one position.",
                "A five by two array, where the new second axis is the channel axis, so each time step carries both signals instead of the series being concatenated into a longer single signal.",
                "It cuts the array at index eight, giving a train portion of the first eight values and a test portion of the rest, and the position is chronological because it decides how much history trains the model and how much is held out.",
            ],
            "homework": (
                "Write window_reshape.py with a float series of at least twelve values. Reshape it "
                "into non-overlapping windows and print the shape, then use "
                "sliding_window_view to produce overlapping windows, print the shape and the first "
                "two samples. Stack two univariate series of equal length into a multivariate array "
                "with a channel axis and print its shape, and split the first ten values at index "
                "eight into train and test parts printing both shapes. Observable output: five "
                "lines or blocks."
            ),
            "required_patterns": ["sliding_window_view", ".reshape(", "np.stack", "np.split", "print("],
        },
        "recommendation-systems": {
            "framing": (
                "Interaction data arrives as one long list of triples and a model needs a "
                "matrix, so reshaping and splitting are the ETL of recommendation."
            ),
            "application": (
                "Walk the example as a list of interactions being shaped into a matrix. "
                "The triple form is compact and sparse while the matrix form is what a "
                "factorisation reads, and the reshape has to preserve the element count "
                "because a dropped interaction is a lost training signal. The more "
                "characteristic operation here is a join: user features and item features "
                "are concatenated along the feature axis to form one wide input vector per "
                "pair, and the axis choice is what makes it a wider sample rather than more "
                "samples. Stacking is how a per-user summary array becomes a batch, adding "
                "a batch axis. Splitting is how a scored matrix is cut into per-user "
                "recommendation lists, and the positions come from the group sizes, so a "
                "mismatch makes the lists contain another user's items. Reasoning about "
                "which axis a join lengthens is the skill that keeps a recommender's "
                "inputs aligned with its weight matrix."
            ),
            "example_hint": "reshape a triple list into a matrix, join user and item features, split scores per user",
            "assessment_angle": "what the element count proves and which axis the feature join lengthens",
            "day": 3,
            "title": "Triples to Matrix, Features to One Wide Vector",
            "code": """import numpy as np

triples = np.arange(12, dtype=np.float64)
matrix = triples.reshape(4, 3)
print("triples:", triples.shape, "matrix:", matrix.shape, "count kept:", matrix.size == triples.size)

user_features = np.ones((2, 3), dtype=np.float64)
item_features = np.zeros((2, 2), dtype=np.float64)
wide = np.concatenate([user_features, item_features], axis=1)
print("wide input shape:", wide.shape)

per_user = np.array([0.9, 0.4], dtype=np.float64)
batch = np.stack([per_user, per_user], axis=0)
print("batch shape:", batch.shape)

scores = np.arange(6, dtype=np.float64).reshape(2, 3)
per_user_lists = np.split(scores, 2, axis=0)
print("per-user lists:", [list(p[0]) for p in per_user_lists])
""",
            "questions": [
                "What does the element-count check after the reshape prove, and why does it matter for training data?",
                "The user and item features are joined with axis=1. What would axis=0 have produced, and why is it wrong here?",
                "What does np.split(scores, 2, axis=0) produce, and what assumption does it make?",
            ],
            "answers": [
                "That every interaction survived the reshape, so no training signal was discarded, which matters because a reshape that loses elements loses data silently.",
                "A four by three array, which would mean more samples with only one feature group each, and it is wrong because a model wants each user-item pair described by one wide vector.",
                "Two arrays of one row each, one per user, and it assumes the two halves of the matrix divide evenly into the users rather than splitting within a user's scores.",
            ],
            "homework": (
                "Write triples_to_matrix.py with a flat array of at least twelve values reshaped into a "
                "matrix whose shape you choose, printing both shapes and whether the element count "
                "is preserved. Concatenate two feature arrays with matching row counts and different "
                "column counts along the feature axis and print the shape, stack two identical "
                "summary arrays into a batch and print the shape, and split a two by three score "
                "matrix into per-user parts printing each one's contents. Observable output: five "
                "lines."
            ),
            "required_patterns": [".reshape(", "np.concatenate", "np.stack", "np.split", "print("],
        },
        "reinforcement-learning": {
            "framing": (
                "A rollout is a flat sequence of steps until it is reshaped into fields, "
                "and a replay buffer joins batches along the step axis."
            ),
            "application": (
                "Walk the example as a rollout being converted into training data. The "
                "collected steps are folded into rows, one per transition, and the element "
                "count is what confirms no step was lost, which matters because a dropped "
                "step is a learning signal that disappears without an error. Joining is how "
                "the buffer is built: a new batch of transitions is concatenated along the "
                "step axis to the stored ones, lengthening an existing axis rather than "
                "adding one, and that is what keeps the field axes aligned, whereas "
                "stacking would have introduced a new axis the consumer does not expect. "
                "Splitting is how a sample is drawn from the buffer and cut into the fields "
                "a loss function consumes, and the split positions are the field "
                "boundaries, so a wrong index there gives the network actions where it "
                "expects states."
            ),
            "example_hint": "fold a rollout into transitions, concatenate batches, split a sample into fields",
            "assessment_angle": "what the element count proves and which axis the buffer concatenation lengthens",
            "day": 3,
            "title": "Fold the Rollout, Append Along the Step Axis, Split the Fields",
            "code": """import numpy as np

rollout = np.arange(16, dtype=np.float32)
transitions = rollout.reshape(4, 4)
print("rollout:", rollout.shape, "transitions:", transitions.shape)
print("steps kept:", transitions.size == rollout.size)

stored = np.ones((2, 4), dtype=np.float32)
new_batch = np.zeros((3, 4), dtype=np.float32)
buffer = np.concatenate([stored, new_batch], axis=0)
print("buffer shape:", buffer.shape)

sample = np.arange(8, dtype=np.float32).reshape(2, 4)
states, actions, rewards = np.split(sample, [2, 3], axis=1)
print("states:", states.tolist(), "actions:", actions.tolist(), "rewards:", rewards.tolist())

per_episode = np.stack([sample, sample], axis=0)
print("episode batch shape:", per_episode.shape)
""",
            "questions": [
                "What does the element-count check on the folded rollout prove, and why is it worth checking explicitly?",
                "The buffer is built by concatenating along axis 0. What would np.stack have produced instead, and why is it wrong?",
                "What do the split indices [2, 3] say about the layout of each transition?",
            ],
            "answers": [
                "That every collected step survived the fold into rows, which is worth checking because a reshape that loses elements discards transitions without raising an error.",
                "A new axis, giving shape (2, 2, 4), which is wrong because the consumer expects one longer table of transitions, not an extra dimension grouping them.",
                "That each transition row has two state entries, then one action entry, then one reward entry, so the cuts fall at the field boundaries.",
            ],
            "homework": (
                "Write rollout_fold.py with a flat float array of at least sixteen values folded into "
                "a transition matrix of four columns, printing both shapes and whether every step "
                "survived. Concatenate a stored batch and a new batch along the step axis and print "
                "the buffer shape. Split a two by four sample at indices two and three along the "
                "field axis and print the states, actions and rewards, and stack two samples into an "
                "episode batch printing its shape. Observable output: five lines."
            ),
            "required_patterns": [".reshape(", "np.concatenate", "np.split", "np.stack", "print("],
        },
        "gpu-programming": {
            "framing": (
                "A kernel grid is defined by block and grid shapes, and reshaping the "
                "same buffer between them is how a launch matches the data's layout."
            ),
            "application": (
                "Walk the example as a buffer being reshaped to match a kernel's "
                "execution grid. The same elements are divided into blocks and blocks into "
                "threads, and the reshape is a view, so the reshaped grid and the host "
                "buffer are the same memory, which is what lets a host-side check read the "
                "results without a transfer. The element count is the invariant that makes "
                "the reshape trustworthy, because a grid whose size does not match the "
                "buffer would either leave elements unprocessed or read past the end, and "
                "checking the product of the shapes first is the cheapest guard. Joining "
                "is how tiles are assembled back into a full buffer, and the axis choice "
                "decides whether the tiles become more rows or more columns, which has to "
                "match how the next kernel divides the grid. Splitting is the inverse, "
                "cutting a buffer into tiles at the block boundaries."
            ),
            "example_hint": "reshape a buffer to a kernel grid, verify the element invariant, join tiles back",
            "assessment_angle": "what the element-count invariant protects and what the tile-join axis must match",
            "day": 3,
            "title": "Reshape to the Grid: Same Elements, Matching Block Sizes",
            "code": """import numpy as np

buffer = np.arange(16, dtype=np.float32)

BLOCK = 4
if buffer.size % BLOCK != 0:
    raise ValueError("buffer is not divisible by the block size")

grid = buffer.reshape(-1, BLOCK)
print("buffer:", buffer.shape, "grid:", grid.shape)
print("is view:", grid.base is buffer)

grid[0, 0] = -1.0
print("buffer head after grid edit:", buffer[:BLOCK])

tiles = [np.full((2, 2), i, dtype=np.float32) for i in (1, 2)]
joined_rows = np.concatenate(tiles, axis=0)
joined_cols = np.concatenate(tiles, axis=1)
print("rows join:", joined_rows.shape, "cols join:", joined_cols.shape)

whole = np.arange(8, dtype=np.float32).reshape(4, 2)
parts = np.split(whole, 2, axis=0)
print("tile shapes:", [p.shape for p in parts])
""",
            "questions": [
                "Why does the code check that the buffer size is divisible by the block size before reshaping?",
                "After an element of the grid is edited, the buffer shows the change. What property of reshape makes that happen?",
                "The two tiles are joined along axis 0 and along axis 1. What decides which is correct?",
            ],
            "answers": [
                "Because the reshape has to divide the buffer into equal blocks for the grid, and a size that does not divide evenly would leave elements outside every block, so the check prevents a silently incomplete launch.",
                "That the reshape is a view sharing the buffer's memory, so a write through the grid lands in the buffer's storage.",
                "How the next kernel divides its grid, since joining along axis 0 stacks tiles as more rows and along axis 1 as more columns, and only one of those matches the layout the next launch expects.",
            ],
            "homework": (
                "Write grid_reshape.py with a float32 buffer of sixteen values that checks divisibility "
                "by a block size of four and raises a clear error otherwise, then reshapes to blocks "
                "and prints both shapes and whether the result is a view. Edit one element of the "
                "grid and print the affected part of the buffer. Concatenate two two by two tiles "
                "along both axes and print both shapes, and split a four by two array into two "
                "row-parts printing each shape. Observable output: five lines."
            ),
            "required_patterns": [".reshape(", "buffer.size %", "np.concatenate", "np.split", "print("],
        },
        "own-ml-framework": {
            "framing": (
                "Reshape in a framework must be recorded in the graph, because the "
                "backward pass has to reverse the shape change exactly."
            ),
            "application": (
                "Walk the example as a framework wrapping reshape as a differentiable "
                "operation. The node stores the input's original shape so the backward pass "
                "can restore it, since a gradient arriving in the reshaped shape has to be "
                "reshaped back before it reaches the source, and that bookkeeping is what "
                "makes flatten and unflatten a lossless pair in the graph. The view "
                "relationship is recorded too, because a reshape that shares memory has to "
                "scatter its gradient into the source's gradient rather than create a "
                "separate one. Joining along a chosen axis is the operation where the "
                "framework has to remember the axis, since the backward pass splits along "
                "the same axis at the same positions, and storing the split sizes with the "
                "node is what makes the reverse exact rather than approximate. The "
                "invariant that the element count never changes is worth asserting inside "
                "the framework, because it catches a class of shape bugs at the operation "
                "boundary instead of at some distant consumer."
            ),
            "example_hint": "record reshape with its source shape and axis with its split sizes",
            "assessment_angle": "why the backward pass needs the original shape and the axis",
            "day": 3,
            "title": "Reshape Is Reversible Only If the Graph Remembers the Shape",
            "code": """import numpy as np


class Tensor:
    def __init__(self, data):
        self.data = np.asarray(data)
        self.producer = None

    def reshaped(self, shape):
        if int(np.prod(shape)) != self.data.size:
            raise ValueError("element count must not change")
        out = Tensor(self.data.reshape(shape))
        out.producer = ("reshape", self.data.shape)
        return out

    def joined(self, other, axis=0):
        if self.data.shape[1 - axis] != other.data.shape[1 - axis]:
            raise ValueError("only the join axis may differ")
        out = Tensor(np.concatenate([self.data, other.data], axis=axis))
        out.producer = ("concat", axis, self.data.shape[axis])
        return out


t = Tensor(np.arange(6, dtype=np.float64))
r = t.reshaped((2, 3))
print("reshaped:", r.data.shape, "from", r.producer[1])

a = Tensor(np.ones((2, 3), dtype=np.float64))
b = Tensor(np.zeros((2, 3), dtype=np.float64))
j = a.joined(b, axis=1)
print("joined:", j.data.shape, "axis", j.producer[1], "first part width", j.producer[2])

try:
    t.reshaped((4, 4))
except ValueError as exc:
    print("rejected:", exc)
""",
            "questions": [
                "Why does the reshape method refuse a shape whose element count differs, and why check it inside the framework?",
                "What does the producer tuple store for a reshape, and how would the backward pass use it?",
                "The join stores the axis and the first part's width. Why are both needed to reverse the operation?",
            ],
            "answers": [
                "Because a reshape must preserve the number of elements, and checking it inside the framework catches a shape bug at the operation boundary instead of letting it surface far away in an unrelated computation.",
                "The source's original shape, which the backward pass uses to reshape the incoming gradient back to what the source's gradient requires.",
                "The axis says which direction to cut and the width says where, so the backward pass can split the gradient along that axis at exactly the original boundary rather than at a guessed midpoint.",
            ],
            "homework": (
                "Write reshape_graph.py with a small tensor class whose reshaped method asserts that "
                "the product of the new shape equals the element count, records the source shape on "
                "the result, and whose joined method checks that only the join axis differs, records "
                "the axis and the first part's width, and concatenates. Reshape a six-element tensor "
                "to two by three and print the shape and the recorded source shape, join two "
                "matching tensors along the feature axis printing the shape and the recorded axis and "
                "width, and demonstrate that a reshape to four by four is rejected with a clear "
                "message. Observable output: three lines plus the rejection."
            ),
            "required_patterns": ["np.prod", "np.concatenate", "self.data.shape", "ValueError", "print("],
        },
    },
)
