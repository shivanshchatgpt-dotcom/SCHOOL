"""Canonical topic batch: reductions and aggregation over axes (PDSH ch 7)."""
from canonical_topics import topic

PDSH_CH7 = {
    "book": "python-data-science-handbook",
    "chapter": 7,
    "pages": [93, 99],
    "sections": ["Summing the Values in an Array", "Minimum and Maximum",
                 "Aggregations and Min, Max, and Everything in Between"],
}


topic(
    "canonical:array-aggregation",
    "A reduction collapses an array along chosen axes, so the axis argument is what decides whether you get one number, one per row or one per column",
    sources=[dict(PDSH_CH7)],
    concept=(
        "Aggregation turns an array into something smaller by applying one operation across "
        "many elements. Sum, product, mean, standard deviation, minimum and maximum are all "
        "reductions, and each takes an axis argument that decides what is collapsed. With no "
        "axis, the whole array becomes a single number. With an axis, that axis is consumed "
        "and every other axis survives, so a mean along rows of a two-dimensional array "
        "gives one value per column and a mean along columns gives one value per row. The "
        "practical consequence is that reading a reduction correctly is a matter of asking "
        "which axis disappeared, and that habit resolves most aggregation confusion "
        "immediately. Reductions also behave predictably with missing data: a nan in the "
        "input makes a plain sum return nan, and the nan-prefixed variants skip those "
        "positions, which is why a dataset with gaps has both variants available and a "
        "choice to make. Aggregating over multiple axes at once is a third shape worth "
        "knowing, because a tuple of axes collapses several in one call instead of chaining "
        "two reductions. The performance note is that these operations run in compiled code, "
        "so a hand-rolled loop that totals an array is both slower and more error-prone than "
        "the built-in reduction, and the built-in is also what a later optimisation, such as "
        "parallel reduction, would replace."
    ),
    prerequisites=["canonical:vectorized-ufuncs"],
    pitfalls=[
        "Reading a reduction's result without asking which axis was collapsed, so a "
        "per-column mean is mistaken for a per-row one.",
        "Summing an array containing a nan and treating the resulting nan as a bug in the "
        "computation rather than as data the sum refused to ignore.",
        "Aggregating an already-aggregated result and expecting the same answer as "
        "aggregating the original, when the two weight the data differently.",
    ],
    adapters={
        "deep-learning": {
            "framing": (
                "A loss is a reduction of per-sample values, and a metric is a reduction "
                "over a batch, so the axis argument separates training signal from reporting."
            ),
            "application": (
                "Walk the example as a validation pass computing both. The per-sample losses "
                "are reduced along the batch axis to give the reported number, while "
                "reductions along the class axis give per-sample diagnostics, and the "
                "difference between the two is exactly the axis argument. The multi-axis case "
                "appears when a batch of predictions has three dimensions, samples by classes "
                "by folds, and a single call with a tuple collapses two of them to give one "
                "number per sample. The nan behaviour matters in a real run, because an "
                "evaluation with a padded or absent class can produce nan losses, and the "
                "nanmean variant reports the average over the real folds instead of "
                "propagating the gap. Getting this right is the difference between a metric "
                "that reports nothing and one that reports the right thing under imperfect "
                "data."
            ),
            "example_hint": "reduce losses along the batch axis and metrics along the class axis",
            "assessment_angle": "what each axis choice produces and why nanmean exists",
            "day": 5,
            "title": "Loss Reduces the Batch, Accuracy Reduces the Classes",
            "code": """import numpy as np

losses = np.array([[0.4, 0.7], [0.1, 0.2], [0.9, 0.3]])

print("batch mean:", losses.mean(axis=0))
print("per-sample:", losses.mean(axis=1))
print("overall:", losses.mean())

multi = np.arange(24, dtype=np.float64).reshape(2, 3, 4)
print("collapse two axes:", multi.sum(axis=(1, 2)).shape)

gappy = np.array([0.5, np.nan, 0.7])
print("plain mean:", gappy.mean(), "nanmean:", np.nanmean(gappy))

pred = np.array([[0.7, 0.2, 0.1], [0.1, 0.8, 0.1]])
labels = np.array([0, 1])
correct = pred.argmax(axis=1) == labels
print("accuracy:", correct.mean())
""",
            "questions": [
                "losses.mean(axis=0) and losses.mean(axis=1) produce arrays of the same length. Why are they different quantities?",
                "What does summing with a tuple of axes do that two chained sums would also do, and why prefer the tuple?",
                "Why does the plain mean of the gappy array print nan while nanmean prints a number?",
            ],
            "answers": [
                "Because axis 0 is the batch axis, so collapsing it gives one mean per class, while axis 1 is the class axis, so collapsing it gives one mean per sample, and the two answer different questions even though the results have the same length here.",
                "It collapses several axes in one reduction, which is shorter to write and avoids materialising an intermediate array, whereas chained sums build and reduce a partial result.",
                "Because the plain reduction propagates the missing value through the total, while nanmean skips the nan positions and averages only the values that are present.",
            ],
            "homework": (
                "Write loss_metric.py with a losses array of at least three samples and two classes "
                "and print its mean along the batch axis, along the class axis and over the whole "
                "array. Build a three-dimensional array of at least two by three by four and print "
                "the shape produced by summing over a tuple of two axes. Add a nan to a small "
                "array and print its plain mean and its nanmean, and compute an accuracy by "
                "comparing argmax along the class axis to labels and printing the mean of the "
                "boolean result. Observable output: five lines."
            ),
            "required_patterns": ["axis=0", "axis=1", "axis=(", "np.nanmean", "print("],
        },
        "computer-vision": {
            "framing": (
                "Image statistics are reductions: brightness is a mean over pixels, and a "
                "histogram is a reduction over intensities."
            ),
            "application": (
                "Walk the example as image statistics being computed. A mean with no axis "
                "gives the overall brightness, a mean along a row axis gives one brightness "
                "per column, which is exactly what a vignette correction needs, and a mean "
                "along the column axis gives one per row, which is how a document scanner "
                "finds text bands. The distinction is purely the axis argument, and "
                "misreading it is how a per-column correction gets applied as a per-row one. "
                "The multi-axis case is pooling: an average over both spatial axes of each "
                "block gives one value per block, and doing it with a tuple or by reshaping "
                "is what turns a full image into a feature map. The nan behaviour is less "
                "common in images but appears with masked regions, where a region outside "
                "the valid area is set to nan so a reduction over the valid pixels ignores "
                "it, and that is a deliberate use of the missing-value semantics rather than "
                "an accident."
            ),
            "example_hint": "compute global, per-row and per-column image statistics and pool blocks",
            "assessment_angle": "which axis gives a per-row versus per-column statistic and what pooling does",
            "day": 5,
            "title": "Brightness Is a Mean, a Band Is a Mean Along an Axis",
            "code": """import numpy as np

image = np.arange(16, dtype=np.float64).reshape(4, 4)
print("global brightness:", image.mean())
print("per-row brightness:", image.mean(axis=1))
print("per-column brightness:", image.mean(axis=0))

blocks = np.arange(16, dtype=np.float64).reshape(2, 2, 2, 2)
pooled = blocks.mean(axis=(2, 3))
print("pooled shape:", pooled.shape)
print(pooled)

print("min, max, std:", image.min(), image.max(), image.std().round(3))

valid = np.full((2, 2), np.nan)
valid[0, 0] = 100.0
print("valid-pixel mean:", np.nanmean(valid))
""",
            "questions": [
                "The per-row and per-column brightnesses are both arrays of length four. What distinguishes them?",
                "What does pooling with mean(axis=(2, 3)) produce, and what did the reshape have to do to make it possible?",
                "Why does nanmean report a value for the valid array while a plain mean would report nan?",
            ],
            "answers": [
                "The axis that was collapsed, so the per-row result collapses each row into its mean and describes horizontal bands, while the per-column result collapses each column and describes vertical bands.",
                "A smaller array holding one average per block, and the reshape grouped the image into blocks first, so the last two axes became the within-block positions that the reduction collapses.",
                "Because nanmean skips the nan positions and averages only the real pixel, whereas a plain mean propagates the missing value and returns nan for the whole array.",
            ],
            "homework": (
                "Write image_stats.py with a four by four float image. Print its global mean, its "
                "per-row means and its per-column means. Reshape a sixteen-element array into a "
                "two by two by two by two block structure and print the shape and contents of a "
                "mean pooled over the last two axes. Print the image's min, max and standard "
                "deviation, and print the nanmean of an array containing one real value and three "
                "nans. Observable output: five lines or blocks."
            ),
            "required_patterns": ["axis=1", "axis=0", "axis=(", ".reshape(", "print("],
        },
        "nlp": {
            "framing": (
                "Corpus statistics are reductions: document lengths, token frequencies and "
                "embedding norms all collapse an axis."
            ),
            "application": (
                "Walk the example as corpus statistics being computed over a token matrix. "
                "Counting non-pad tokens is a reduction along the sequence axis, giving one "
                "length per document, and that number is what drives a batching decision "
                "about padding. The mean sequence length is a further reduction over the "
                "document axis, collapsing the corpus to a single number, and the "
                "distinction between the two reductions is the axis argument alone. Norms of "
                "embedding vectors are reductions along the feature axis, and they are what "
                "a normalisation or a cosine similarity needs. The nan case appears with "
                "padded positions marked nan rather than zero, because zero is a real "
                "embedding value while nan can be excluded from a mean, which is a genuine "
                "design choice a pipeline has to make consciously."
            ),
            "example_hint": "reduce token counts per document and norms per embedding",
            "assessment_angle": "what each reduction axis gives and why pad positions as nan beat zeros",
            "day": 5,
            "title": "Length Reduces the Sequence Axis, Norm Reduces the Feature Axis",
            "code": """import numpy as np

docs = np.array([[5, 12, 7, 0, 0],
                 [3, 9, 14, 2, 0],
                 [11, 6, 8, 1, 4]])

lengths = (docs > 0).sum(axis=1)
print("lengths:", lengths, "mean length:", lengths.mean())

mask = docs > 0
print("total tokens:", mask.sum(), "positions:", mask.size)

embeddings = np.array([[3.0, 4.0], [1.0, 0.0]])
norms = np.linalg.norm(embeddings, axis=1)
print("norms:", norms)

padded = docs.astype(np.float64)
padded[padded == 0] = np.nan
print("mean real token id per doc:", np.nanmean(padded, axis=1))

print("max token id:", docs.max(), "min real token:", docs[docs > 0].min())
""",
            "questions": [
                "How is the per-document length computed, and what does the further mean over those lengths collapse?",
                "Why is the norm computed with axis=1 rather than with no axis argument?",
                "What is the advantage of marking pad positions as nan before taking a mean?",
            ],
            "answers": [
                "By comparing each position to zero and summing the resulting boolean array along the sequence axis, and the mean over those lengths collapses the document axis to give one average for the whole corpus.",
                "Because no axis argument would reduce the entire embedding matrix to a single number, while axis 1 collapses the feature axis and gives one norm per embedding vector.",
                "Because nan positions are skipped by nanmean, so the average reflects only the real tokens, whereas zeros would be counted as real token identifiers and drag the mean down.",
            ],
            "homework": (
                "Write corpus_stats.py with a token matrix of at least three documents of five "
                "positions containing pad zeros. Print the per-document lengths as a sum of a "
                "boolean mask along the sequence axis and the mean length, and print the total "
                "token count and the number of positions. Compute the norms of at least two "
                "embedding vectors along the feature axis and print them, then convert pad zeros "
                "to nan and print the per-document nanmean token id. Print the maximum token id and "
                "the minimum real token id. Observable output: five lines."
            ),
            "required_patterns": ["axis=1", ".sum()", "np.linalg.norm", "np.nanmean", "print("],
        },
        "time-series": {
            "framing": (
                "Series summaries are reductions, and the axis argument is what separates a "
                "number describing the whole history from one series per channel."
            ),
            "application": (
                "Walk the example as a multivariate series being summarised. A mean with no "
                "axis gives one number for the entire history, a mean along the time axis "
                "gives one series per channel describing each signal's level, and the "
                "difference is the axis argument and nothing else. Rolling statistics are the "
                "same reductions applied to windowed views, so a rolling mean is a reduction "
                "along the within-window axis, and composing windowing with reduction is the "
                "pattern behind every smoothing operation. The nan behaviour is especially "
                "important in time series because gaps are common, and reporting nan for a "
                "whole metric because one day is missing is a classic failure, while "
                "nanmean reports the average over the days that exist. Multi-axis reduction "
                "appears when a series is stored as windows by channels by positions and one "
                "call collapses the last two."
            ),
            "example_hint": "summarise whole history, per channel, and per window with the right axes",
            "assessment_angle": "what each axis choice produces and why gaps need nanmean",
            "day": 5,
            "title": "One Number, One Series, One Window: It Is All the Axis",
            "code": """import numpy as np
from numpy.lib.stride_tricks import sliding_window_view

series = np.arange(20, dtype=np.float64).reshape(10, 2)
print("whole-history mean:", series.mean())
print("per-channel mean:", series.mean(axis=0))
print("per-step mean:", series.mean(axis=1)[:3])

windows = sliding_window_view(series[:, 0], 4)
print("rolling mean shape:", windows.mean(axis=1).shape)

with_gap = np.array([1.0, np.nan, 3.0, 4.0])
print("plain mean:", with_gap.mean(), "nanmean:", np.nanmean(with_gap))

cube = np.arange(24, dtype=np.float64).reshape(2, 3, 4)
print("collapse two axes shape:", cube.sum(axis=(1, 2)).shape)
print("min, max:", cube.min(), cube.max())
""",
            "questions": [
                "The whole-history mean and the per-channel mean are both single values here. Why is one a scalar and the other an array?",
                "What does windows.mean(axis=1) compute, and why is that axis the one to collapse?",
                "Why would a report that prints nan for a series with one missing day be wrong, and what fixes it?",
            ],
            "answers": [
                "Because the whole-history mean collapses every axis and returns one scalar, while the per-channel mean collapses only the time axis and leaves the channel axis, returning one value per channel.",
                "The mean within each window, because axis 1 is the positions inside a window, so collapsing it gives one smoothed value per window.",
                "Because the single missing day propagates through the sum and makes the whole metric unreadable, and nanmean skips the missing position and reports the average over the days that are present.",
            ],
            "homework": (
                "Write series_summary.py with a series of at least ten time steps and two channels "
                "and print the mean over the whole array, the per-channel mean and the first three "
                "per-step means. Window one channel with sliding_window_view and print the shape of "
                "the rolling mean. Add a nan to a four-value array and print its plain mean and "
                "nanmean, and reshape a twenty-four-element array to two by three by four and print "
                "the shape produced by summing over a tuple of two axes plus the array's min and "
                "max. Observable output: six lines."
            ),
            "required_patterns": ["axis=0", "axis=1", "axis=(", "np.nanmean", "print("],
        },
        "recommendation-systems": {
            "framing": (
                "Engagement metrics are reductions over an interaction matrix, and the axis "
                "decides whether you report per user, per item or overall."
            ),
            "application": (
                "Walk the example as an interaction matrix being summarised. A sum along the "
                "item axis gives each user's total activity, a sum along the user axis gives "
                "each item's popularity, and a sum with no axis gives the platform's total, "
                "and these are the same operation with different axes. The popularity ranking "
                "comes from ordering one of those reductions, and the choice of axis decides "
                "whether the ranking is of users or items, which is a report-level "
                "distinction rather than a computational one. Averages interact with sparsity "
                "in a way worth naming: the mean of a row including zeros measures engagement "
                "per item offered, while a mean over non-zero entries measures engagement "
                "given interaction, and the two answer different business questions. The nan "
                "case appears when unrated positions are marked nan rather than zero, which "
                "is the honest representation for implicit versus explicit feedback."
            ),
            "example_hint": "reduce interactions per user and per item and distinguish mean-including-zeros from mean-given-interaction",
            "assessment_angle": "what each axis reports and why the two user averages differ",
            "day": 5,
            "title": "Per User, Per Item, Overall: Three Reductions of One Matrix",
            "code": """import numpy as np

matrix = np.array([[1, 0, 3, 0],
                   [0, 2, 0, 1],
                   [4, 0, 0, 2]], dtype=np.float64)

print("total:", matrix.sum())
print("per user:", matrix.sum(axis=1))
print("per item:", matrix.sum(axis=0))

top_item = matrix.sum(axis=0).argmax()
print("most popular item:", top_item, "with", matrix.sum(axis=0).max())

user = matrix[0]
print("mean per item offered:", user.mean())
print("mean given interaction:", user[user > 0].mean())

ratings = matrix.copy()
ratings[ratings == 0] = np.nan
print("nan-aware item mean:", np.nanmean(ratings, axis=0))

print("density:", (matrix > 0).mean())
""",
            "questions": [
                "How do the per-user and per-item reductions differ in which axis they collapse?",
                "The first user's mean over all entries and the mean over only positive entries differ. What does each measure?",
                "Why is the nan-aware item mean a different quantity from the plain per-item sum?",
            ],
            "answers": [
                "The per-user reduction collapses the item axis, leaving one total per user, while the per-item reduction collapses the user axis, leaving one total per item.",
                "The first measures engagement across every item the user was offered, counting the ignored ones as zero, while the second measures how strongly the user engaged on the items they engaged with at all.",
                "Because the nan-aware mean skips positions never rated and averages only recorded ratings, while the plain sum counts every interaction including zeros that may mean no data rather than no engagement.",
            ],
            "homework": (
                "Write engagement_metrics.py with a float interaction matrix of at least four users "
                "and five items containing many zeros. Print the total, the per-user sums and the "
                "per-item sums, and print the most popular item with its total found by ordering a "
                "reduction. For one user, print the mean over all entries and the mean over only "
                "the positive entries. Convert zeros to nan and print a nan-aware per-item mean, "
                "and print the matrix's density as the mean of a boolean mask. Observable output: "
                "six lines."
            ),
            "required_patterns": ["axis=1", "axis=0", ".argmax()", "np.nanmean", "print("],
        },
        "reinforcement-learning": {
            "framing": (
                "Episode returns and success rates are reductions over a trajectory, and the "
                "axis separates per-episode reporting from per-step learning signal."
            ),
            "application": (
                "Walk the example as trajectories being summarised. A sum of rewards along "
                "the time axis gives one return per episode, and a mean over the episode axis "
                "gives the single number a report calls average return, so the two reductions "
                "compose to produce the headline metric. Success rate is a mean over a "
                "boolean reduction, which is a reduction of a reduction, and reading it "
                "correctly means seeing both. The axis distinction matters in a sharper way "
                "during learning: a per-step reduction gives the signal a value function is "
                "fit to, while a per-episode reduction gives the number a report tracks, and "
                "feeding the second into the first is how a training loop accidentally "
                "optimises a lagging indicator. The nan case appears with truncated episodes "
                "marked nan, so an average over completed episodes can be reported without "
                "the unfinished ones either contributing or being silently dropped."
            ),
            "example_hint": "reduce rewards to per-episode returns then to an average return",
            "assessment_angle": "how two composed reductions build the headline metric and what a boolean mean gives",
            "day": 5,
            "title": "Return Reduces the Episode, Average Return Reduces the Runs",
            "code": """import numpy as np

episodes = np.array([[1.0, 0.5, -0.5, 2.0],
                     [0.0, 1.0, 1.0, 1.0],
                     [-1.0, 0.5, 0.5, 0.5]])

returns = episodes.sum(axis=1)
print("returns:", returns)
print("average return:", returns.mean())

lengths = (episodes != 0).sum(axis=1)
print("lengths:", lengths, "mean length:", lengths.mean())

success = np.array([1.0, 0.0, 1.0, 1.0, 0.0])
print("success rate:", success.mean())

steps = episodes.mean(axis=1)
print("per-step mean reward:", np.round(steps, 3))

partial = np.array([2.0, np.nan, 4.0])
print("completed-episode mean:", np.nanmean(partial))

print("best episode:", returns.argmax(), "return:", returns.max())
""",
            "questions": [
                "How do the two composed reductions build the average return?",
                "The success rate is the mean of an array of ones and zeros. What does that mean compute, and why is it a reduction of a boolean quantity?",
                "What does nanmean report for the partial array, and why is that the right metric for truncated episodes?",
            ],
            "answers": [
                "The first sums rewards along the time axis to give one return per episode, and the second averages those returns along the episode axis to give a single headline number.",
                "The fraction of runs that succeeded, because each one counts as true and each zero as false, so the mean of the indicator is the success proportion.",
                "The average return over the episodes that completed, because nanmean skips the truncated episode rather than letting its missing return propagate to the whole metric.",
            ],
            "homework": (
                "Write episode_returns.py with a rewards array of at least three episodes of four "
                "steps. Print the per-episode returns, the average return and the per-episode step "
                "counts with their mean. Build a success indicator array and print the success "
                "rate, print the per-step mean reward per episode, and print the nanmean of an "
                "array containing one nan among completed episodes. Print the index and value of "
                "the best episode's return. Observable output: seven lines."
            ),
            "required_patterns": ["axis=1", ".mean()", "np.nanmean", ".argmax()", "print("],
        },
        "gpu-programming": {
            "framing": (
                "A reduction is a parallel algorithm on a device, and numpy's axis argument "
                "expresses exactly the tree a device reduction has to build."
            ),
            "application": (
                "Walk the example as reductions expressed at array level and compared with "
                "their device equivalents. A sum over one axis is a reduction tree along that "
                "dimension, and the axis argument is what decides the tree's direction, "
                "which determines both the result shape and the memory access pattern, "
                "because collapsing rows reads contiguously while collapsing columns strides "
                "through memory. Multi-axis reduction with a tuple is the case where a "
                "device kernel can fuse two trees into one pass, and that is a real "
                "optimisation rather than a notational convenience. The nan behaviour is a "
                "device concern too, because a reduction that propagates nan has to "
                "short-circuit, and some fast device reductions skip that check for speed, "
                "which is a trade-off a programmer has to know they are making. Timing a "
                "numpy reduction against a hand-rolled loop is the practical way to see why "
                "the compiled reduction is the baseline a device version has to beat."
            ),
            "example_hint": "reduce along both axes of a grid and time the reduction against a loop",
            "assessment_angle": "what the axis decides about memory access and what fusing axes saves",
            "day": 5,
            "title": "A Reduction Is a Tree: The Axis Picks Its Direction",
            "code": """import numpy as np

grid = np.arange(12, dtype=np.float32).reshape(3, 4)
print("row totals:", grid.sum(axis=1))
print("column totals:", grid.sum(axis=0))
print("contiguous check rows:", grid.sum(axis=1).flags["C_CONTIGUOUS"])

cube = np.arange(24, dtype=np.float32).reshape(2, 3, 4)
print("fused axes shape:", cube.sum(axis=(1, 2)).shape)
print("chained shape:", cube.sum(axis=2).sum(axis=1).shape)

gappy = np.array([1.0, np.nan, 3.0], dtype=np.float32)
print("nan-aware:", np.nansum(gappy))

big = np.arange(1_000_000, dtype=np.float32)
total = 0.0
for value in big:
    total += value
print("loop total close to numpy:", np.isclose(total, big.sum()))
""",
            "questions": [
                "Why does reducing along axis 1 have a different memory access pattern from reducing along axis 0?",
                "The fused and chained reductions produce the same shape. What does fusing save?",
                "What does the loop-total comparison demonstrate about the built-in reduction?",
            ],
            "answers": [
                "Because axis 1 runs along each row, so the reduction reads consecutive elements, while axis 0 runs down the columns, so it strides between rows and touches memory less contiguously.",
                "It avoids materialising the intermediate array and can be done in one pass over the data, while chaining builds a partial result and reduces it again.",
                "That the built-in reduction produces the same total as an explicit loop, so the loop is not more correct, only slower.",
            ],
            "homework": (
                "Write reduction_tree.py with a three by four float32 grid and print its row totals "
                "and column totals, plus whether the row-total result is contiguous. Build a two by "
                "three by four cube and print the shapes produced by summing over a tuple of two "
                "axes and by chaining two single-axis sums. Print the nansum of an array containing "
                "a nan, and print whether a hand-rolled loop total over a large float array is "
                "close to numpy's sum. Observable output: five lines."
            ),
            "required_patterns": ["axis=1", "axis=0", "axis=(", "np.isclose", "print("],
        },
        "own-ml-framework": {
            "framing": (
                "A framework's reduce operation has to carry its axis into the backward pass, "
                "because the gradient of a sum is a broadcast of ones."
            ),
            "application": (
                "Walk the example as a reduce operation recorded for autograd. The forward "
                "call collapses an axis, so the backward pass has to expand the incoming "
                "gradient back along that axis, and the recorded shape is what makes the "
                "expansion exact rather than guessed. The rule is simple and worth stating "
                "plainly: the gradient of a sum with respect to its input is an array of ones "
                "in the input's shape, so the backward pass broadcasts rather than "
                "computing. For mean the ones are scaled by the count, and getting that "
                "scaling wrong is a silent error that shows up only as a learning rate that "
                "seems off. Averaging over multiple axes has to record all of them, because "
                "the backward pass restores each one, and the order does not matter for the "
                "shape but the recorded set does."
            ),
            "example_hint": "record a reduce with its collapsed axis and expand the gradient back",
            "assessment_angle": "why the backward pass of a sum broadcasts and what mean changes",
            "day": 5,
            "title": "The Gradient of a Sum Is Ones: Reduce Forward, Broadcast Back",
            "code": """import numpy as np


class Tensor:
    def __init__(self, data):
        self.data = np.asarray(data, dtype=np.float64)
        self.shape = self.data.shape

    def reduce_sum(self, axis=None):
        out = Tensor(self.data.sum(axis=axis))
        out.axis = axis
        out.input_shape = self.shape
        return out

    def reduce_mean(self, axis=None):
        total = self.data.sum(axis=axis)
        count = self.data.size // total.size
        out = Tensor(total / count)
        out.axis = axis
        out.input_shape = self.shape
        out.scale = 1.0 / count
        return out


def backward_reduce(node, grad):
    if node.axis is None:
        return np.full(node.input_shape, grad, dtype=np.float64)
    return np.expand_dims(grad, node.axis) * np.ones(node.input_shape)


x = Tensor(np.array([[1.0, 2.0], [3.0, 4.0]]))
row_sum = x.reduce_sum(axis=1)
print("row sums:", row_sum.data)
print("grad to input:\\n", backward_reduce(row_sum, np.array([9.0, 7.0])))

row_mean = x.reduce_mean(axis=1)
print("row means:", row_mean.data, "scale:", row_mean.scale)

total = x.reduce_sum()
print("total:", total.data, "grad shape:", backward_reduce(total, 1.0).shape)
""",
            "questions": [
                "Why is the backward pass of a sum a broadcast of ones rather than a computation?",
                "What does the mean's scale factor record, and why does getting it wrong matter?",
                "Why does the reduce operation store the input shape on its result?",
            ],
            "answers": [
                "Because a sum's derivative with respect to every input element is one, so the incoming gradient simply has to be expanded back to the input's shape with no further arithmetic.",
                "The reciprocal of the number of elements averaged, because the mean is a sum divided by that count, so the gradient is scaled by the same factor, and using it incorrectly makes the effective learning rate silently wrong.",
                "Because the backward pass has to restore the collapsed axis to its original length, and the input shape is the only record of what that length was.",
            ],
            "homework": (
                "Write reduce_backward.py with a small tensor class whose reduce_sum and reduce_mean "
                "methods record the collapsed axis, the input shape and, for the mean, the scale "
                "factor. Reduce a two by two float array along axis 1, print the sums and the "
                "gradient expanded back to the input shape, then reduce along the same axis with "
                "mean and print the means with the recorded scale. Reduce the whole array and print "
                "the total with the shape of the gradient produced for a scalar input. Observable "
                "output: four lines or blocks."
            ),
            "required_patterns": ["axis=1", "np.expand_dims", "np.ones(", "self.shape", "print("],
        },
    },
)
