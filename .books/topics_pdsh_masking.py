"""Canonical topic batch: comparisons, masks and boolean arrays (PDSH ch 9)."""
from canonical_topics import topic

PDSH_CH9 = {
    "book": "python-data-science-handbook",
    "chapter": 9,
    "pages": [109, 119],
    "sections": ["Comparison Operators as Ufuncs", "Working with Boolean Arrays",
                 "Boolean Arrays as Masks"],
}


topic(
    "canonical:boolean-masking",
    "A comparison produces a boolean array, and using it as a mask selects the elements that satisfied the condition without a loop or an index list",
    sources=[dict(PDSH_CH9)],
    concept=(
        "Comparisons in numpy are themselves vectorised operations, so an expression "
        "comparing an array to a value returns a boolean array of the same shape rather than "
        "a single boolean. That boolean array is useful in three distinct ways and the three "
        "are worth separating. It can be counted, so summing a mask gives the number of "
        "positions satisfying the condition and taking its mean gives a proportion. It can "
        "be combined with the logical operators, so two masks can be and-ed or or-ed to "
        "express a compound condition. And it can be used as a mask, so indexing an array "
        "with a boolean array of the same shape returns a flat array of the elements that "
        "were true, which is the cleanest way to select the values that matter. Masking has "
        "one shape consequence that surprises people: the result is one-dimensional, "
        "because the selected elements have no reason to form a rectangle, so a mask is not "
        "a way to take a sub-block. Boolean masks can also be assigned to, which replaces "
        "every selected element in place, and that is the idiom for clipping, thresholding "
        "and cleaning data. The counting behaviour is what makes a mask a statistical tool, "
        "since a proportion of true values is a rate, a density or an error fraction, and "
        "nothing has to be counted in a loop."
    ),
    prerequisites=["canonical:vectorized-ufuncs"],
    pitfalls=[
        "Expecting a masked result to keep the array's shape, when masking returns a flat "
        "array of the selected elements.",
        "Combining masks with the bitwise operators on Python booleans instead of the "
        "element-wise operators, which raises rather than applying to every element.",
        "Using a mask built from a comparison of floats with equality and getting an empty "
        "selection because of representation residuals.",
    ],
    adapters={
        "deep-learning": {
            "framing": (
                "Accuracy is a count of a boolean mask, and a confidence threshold is a mask "
                "used to filter predictions."
            ),
            "application": (
                "Walk the example as a validation pass scoring predictions. The predicted and "
                "true labels are compared once and the result is a boolean array, which is "
                "then counted for accuracy and used as a mask to pull out the wrong "
                "predictions for inspection, so one comparison feeds both a metric and a "
                "diagnostic. That duality is the transferable point: a mask is simultaneously "
                "a statistic and a selection, and choosing to use it both ways is what makes "
                "an evaluation loop short. A confidence threshold is a second mask over the "
                "probabilities, and the two masks are combined to find the confident errors, "
                "which is the case that demonstrates element-wise logical composition. The "
                "float-equality caution appears in comparing losses or probabilities: an "
                "exact comparison of two floats gives an empty selection, so a tolerance "
                "mask is the correct tool and the equality mask is the bug."
            ),
            "example_hint": "compute accuracy from one comparison and mask out the confident errors",
            "assessment_angle": "how one mask serves both counting and selection and what composition expresses",
            "day": 7,
            "title": "Accuracy Counts the Mask, Errors Are the Mask's Selection",
            "code": """import numpy as np

pred = np.array([0, 1, 1, 0, 2, 2, 1])
true = np.array([0, 1, 0, 0, 2, 1, 1])

correct = pred == true
print("correct mask:", correct)
print("accuracy:", correct.mean())
print("errors:", pred[~correct])

probs = np.array([0.9, 0.8, 0.55, 0.95, 0.7, 0.6, 0.85])
confident = probs > 0.75
confident_errors = confident & ~correct
print("confident errors:", pred[confident_errors], "at", np.where(confident_errors)[0])

scores = np.array([0.3, 0.3000000001])
print("exact equality mask:", scores == scores.mean())
print("tolerance mask:", np.abs(scores - scores.mean()) < 1e-6)
""",
            "questions": [
                "How does one comparison serve both the accuracy metric and the error list?",
                "What does the expression confident & ~correct select, and why is the operator element-wise?",
                "Why does the exact equality mask select nothing while the tolerance mask selects both values?",
            ],
            "answers": [
                "Because the comparison produces one boolean array whose mean is the accuracy and whose complement masks the array to give the wrong predictions, so the mask is counted and used as a selection in the same pass.",
                "The predictions that are both above the confidence threshold and wrong, and the operator is element-wise because it combines two boolean arrays position by position rather than collapsing them to a single truth value.",
                "Because the two floats differ by a tiny representation residual, so an exact comparison is never satisfied, while the tolerance mask accepts any value within a small distance of the mean.",
            ],
            "homework": (
                "Write accuracy_mask.py with predicted and true label arrays of at least seven "
                "elements. Build one correct mask, print it, print the accuracy as its mean and the "
                "errors as the masked selection of the predictions. Build a confidence mask over a "
                "probabilities array and combine it with the complement of the correct mask to print "
                "the confident errors and their positions, and print both an exact equality mask and "
                "a tolerance mask over two floats that differ only in a tiny residual. Observable "
                "output: seven lines."
            ),
            "required_patterns": ["== correct", ".mean()", "~correct", "np.where", "print("],
        },
        "computer-vision": {
            "framing": (
                "Thresholding is a mask, the foreground fraction is the mask's mean, and "
                "morphological cleanup is masks combined logically."
            ),
            "application": (
                "Walk the example as a segmentation being turned into measurements. The "
                "threshold comparison produces a boolean mask over the image, its mean is the "
                "foreground fraction, and indexing the original image with the mask gives the "
                "foreground intensities as a flat array whose mean is a useful statistic, so "
                "three measurements come from one comparison. The shape consequence is worth "
                "stating explicitly: the masked selection is flat, so it cannot be displayed "
                "as an image, whereas the mask itself can, and knowing which result to use is "
                "what keeps a display routine from receiving a vector. Combining masks "
                "logically is how connected regions are cleaned: a size threshold over "
                "labelled components keeps the large ones and removes the small ones, and "
                "that composition is the morphological part of a pipeline. The assignment "
                "form appears too, since setting background pixels to zero through a mask is "
                "a one-line operation that changes the image in place."
            ),
            "example_hint": "threshold an image, measure the foreground fraction, combine masks for cleanup",
            "assessment_angle": "what a mask's mean measures and why the masked selection is flat",
            "day": 7,
            "title": "Threshold Once: Fraction, Foreground Values, Cleanup",
            "code": """import numpy as np

image = np.array([[10, 40, 80], [120, 200, 250]], dtype=np.uint8)

foreground = image > 100
print("mask:\\n", foreground)
print("foreground fraction:", foreground.mean())
print("foreground values:", image[foreground])
print("mean foreground intensity:", image[foreground].mean())

background = ~foreground
clean = image.copy()
clean[background] = 0
print("cleaned:\\n", clean)

small = np.array([True, False, True, False])
large = np.array([True, True, False, False])
kept = small | large
print("union of masks:", kept, "count:", kept.sum())

print("masked shape:", image[foreground].shape, "mask shape:", foreground.shape)
""",
            "questions": [
                "What does the mean of the threshold mask measure, and why is it a proportion?",
                "Why is image[foreground] one-dimensional while the mask itself is two-dimensional?",
                "What do the two ways of using a mask shown here, selection and assignment, each achieve?",
            ],
            "answers": [
                "The fraction of pixels above the threshold, and it is a proportion because the mean averages a boolean array whose values are one and zero.",
                "Because masking selects the elements that were true and they have no reason to form a rectangle, so the result is flattened, while the mask is a full array covering every pixel.",
                "Selection pulls the foreground values out as a flat list to be measured, while assignment writes through the mask to change the selected pixels in place, which is how the background is zeroed.",
            ],
            "homework": (
                "Write threshold_mask.py with an integer image of at least two rows and three columns "
                "spanning a wide range. Build a threshold mask, print it and its mean as the foreground "
                "fraction, print the masked selection of values and their mean, and build a copy of the "
                "image with the background set to zero by assigning through the complement mask, "
                "printing the result. Combine two small boolean masks with both the element-wise union "
                "and intersection and print each with its count, and print the shape of the masked "
                "selection beside the mask's shape. Observable output: seven lines or blocks."
            ),
            "required_patterns": ["> 100", ".mean()", "image[foreground]", "~foreground", "print("],
        },
        "nlp": {
            "framing": (
                "A padding mask, an out-of-vocabulary mask and a length mask are all boolean "
                "arrays built by comparison."
            ),
            "application": (
                "Walk the example as a token matrix being filtered. A comparison against the "
                "pad id produces a mask whose mean is the padding fraction, which is the "
                "number a batching routine uses to choose a sequence length, and the "
                "complement masks the matrix to give the real tokens as a flat array. The "
                "composition case is genuinely important in NLP: a token is out of "
                "vocabulary if it exceeds the vocabulary size, and a mask over that "
                "condition is combined with a mask over padding to report how many real "
                "tokens were unknown, which is a single metric built from two comparisons. "
                "The assignment form is how unknown ids are replaced with a dedicated "
                "unknown token, written through the mask in place. The float caution "
                "appears in comparing attention weights or probabilities, where an exact "
                "comparison selects nothing and a tolerance or a greater-than does the "
                "intended job."
            ),
            "example_hint": "build padding and out-of-vocabulary masks and combine them into one metric",
            "assessment_angle": "what a mask's mean reports and how two masks compose into one metric",
            "day": 7,
            "title": "Pad Mask, OOV Mask, One Metric from Two Comparisons",
            "code": """import numpy as np

PAD = 0
VOCAB = 10
tokens = np.array([[5, 7, 0, 0], [12, 3, 8, 0], [2, 4, 6, 9]])

pad = tokens == PAD
print("padding fraction:", pad.mean())
real = ~pad
print("real tokens:", tokens[real])

oov = tokens > VOCAB
real_oov = oov & real
print("real and out of vocab:", real_oov.sum(), "positions:", np.where(real_oov))

cleaned = tokens.copy()
cleaned[oov] = 1
print("unknowns replaced:\\n", cleaned)

lengths = real.sum(axis=1)
print("lengths:", lengths)
print("any fully padded:", (~real.any(axis=1)).any())
""",
            "questions": [
                "What does the padding mask's mean report, and why is that number useful to a batching routine?",
                "What does combining the out-of-vocabulary mask with the real-token mask produce, and why is the combination necessary?",
                "How does the assignment form replace unknown tokens, and what would go wrong if the mask were applied to the original array instead of a copy?",
            ],
            "answers": [
                "The fraction of positions that are padding, which tells a batching routine how much of the batch is wasted on padding and informs the choice of sequence length.",
                "The count of real tokens that fall outside the vocabulary, and the combination is necessary because an out-of-vocabulary hit on a padding position is not a real unknown token, so padding has to be excluded.",
                "It writes the unknown id through the mask into the copy, replacing every selected position in place, and applying it to the original would permanently alter the source matrix that other computations still read.",
            ],
            "homework": (
                "Write token_masks.py with a token matrix of at least three sequences of four positions, "
                "a pad id and a vocabulary size. Build a padding mask, print its mean and the flat "
                "selection of real tokens, then build an out-of-vocabulary mask and combine it with "
                "the real-token mask to print the count of real unknown tokens and their positions. "
                "Copy the matrix, replace unknown ids through the mask and print the result, and "
                "print the per-sequence lengths plus whether any sequence is fully padding. "
                "Observable output: six lines or blocks."
            ),
            "required_patterns": ["== PAD", ".mean()", "~pad", "np.where", "print("],
        },
        "time-series": {
            "framing": (
                "Anomalies are a mask, missing periods are a mask, and the rate above a "
                "threshold is the mask's mean."
            ),
            "application": (
                "Walk the example as a series being screened for anomalies. A comparison "
                "against a threshold produces a mask whose mean is the anomaly rate, which "
                "is the headline number, and the mask selects the anomalous values "
                "themselves for a report. Combining masks is how a more precise definition "
                "of an anomaly is expressed: a value is anomalous if it exceeds the "
                "threshold and its neighbours are normal, which is two masks and-ed, and "
                "that refinement is what distinguishes a spike from a regime change. The "
                "assignment form is how anomalies are capped or replaced with an "
                "interpolation, written through the mask. The missing-data case is the "
                "opposite use of the same tool: a mask over the nan positions identifies "
                "gaps so a report can state the coverage, and the two masks, anomalies and "
                "gaps, are complementary rather than competing. The tolerance caution "
                "appears in detecting a value near a reference, where an exact equality "
                "mask would be empty and a distance mask is correct."
            ),
            "example_hint": "flag anomalies with a threshold mask and refine it with a neighbour mask",
            "assessment_angle": "what the mask's mean reports and what composing two masks expresses",
            "day": 7,
            "title": "Anomaly Rate Is a Mean, Anomalies Are the Selection",
            "code": """import numpy as np

series = np.array([1.0, 1.1, 9.5, 1.2, 0.9, 8.0, 1.0], dtype=np.float64)
THRESHOLD = 5.0

anomaly = series > THRESHOLD
print("anomaly rate:", anomaly.mean())
print("anomalies:", series[anomaly], "at", np.where(anomaly)[0])

shifted = np.roll(series, 1)
neighbour_normal = shifted <= THRESHOLD
spike = anomaly & neighbour_normal
print("spikes only:", series[spike])

capped = series.copy()
capped[anomaly] = THRESHOLD
print("capped:", capped)

with_gap = np.array([1.0, np.nan, 1.2])
print("coverage:", (~np.isnan(with_gap)).mean())
print("near reference:", np.abs(series - 1.0) < 0.15)
""",
            "questions": [
                "What does the anomaly mask's mean report, and how is it computed without a loop?",
                "What does combining the anomaly mask with a neighbour mask express, and why is that a better definition than the threshold alone?",
                "Why does the capping assign through the mask into a copy rather than computing a new array by a formula?",
            ],
            "answers": [
                "The fraction of points above the threshold, computed as the mean of a boolean array whose ones and zeros average to the rate, so no counting loop is needed.",
                "That a value is only a spike if it exceeds the threshold while its predecessor does not, which separates an isolated spike from a sustained shift to a new level.",
                "Because capping replaces only the selected positions with a constant, leaving every other point exactly as it was, which a formula over the whole array could not do without recomputing every value.",
            ],
            "homework": (
                "Write anomaly_mask.py with a float series of at least seven values containing two "
                "large spikes and a threshold. Build an anomaly mask, print its mean as the anomaly "
                "rate and the selected values with their positions. Build a neighbour mask with "
                "np.roll, combine it with the anomaly mask and print the spikes only. Copy the "
                "series, cap the anomalies by assigning through the mask and print it, and print the "
                "coverage of a small array containing a nan plus a tolerance mask for values near a "
                "reference. Observable output: six lines."
            ),
            "required_patterns": ["> THRESHOLD", ".mean()", "series[anomaly]", "np.roll", "print("],
        },
        "recommendation-systems": {
            "framing": (
                "A cold-start report is built from masks: users with no history, items with "
                "no audience, and the overlap between them."
            ),
            "application": (
                "Walk the example as an interaction matrix being profiled. A mask over a row "
                "sum identifies users with no history, a mask over a column sum identifies "
                "items with no audience, and counting each gives the two numbers a "
                "cold-start report states. Combining the two masks is not meaningful "
                "directly since they live on different axes, which is itself a useful "
                "lesson: masks can only be combined when they share a shape, and a shape "
                "mismatch in a logical expression is a sign the two masks describe different "
                "things. The density of the matrix is the mean of an interaction mask, and "
                "selecting through a per-user mask gives that user's items as a flat list, "
                "which is what a recommendation explanation displays. The assignment form "
                "appears when suspicious interactions, say a count above a plausible "
                "ceiling, are zeroed through a mask as a cleaning step before scoring."
            ),
            "example_hint": "profile cold users and cold items from row and column masks",
            "assessment_angle": "what each mask counts and why masks on different axes cannot combine",
            "day": 7,
            "title": "Cold Users and Cold Items: Two Masks on Two Axes",
            "code": """import numpy as np

matrix = np.array([[1, 0, 3, 0],
                   [0, 0, 0, 0],
                   [4, 0, 0, 2],
                   [0, 0, 0, 0]], dtype=np.int32)

user_totals = matrix.sum(axis=1)
cold_users = user_totals == 0
print("cold users:", cold_users.sum(), "of", cold_users.size)

item_totals = matrix.sum(axis=0)
cold_items = item_totals == 0
print("cold items:", cold_items.sum(), "of", cold_items.size)

interacted = matrix > 0
print("density:", interacted.mean())

active = matrix[0]
print("user 0's items:", np.where(active > 0)[0], "values:", active[active > 0])

suspicious = matrix > 3
cleaned = matrix.copy()
cleaned[suspicious] = 3
print("capped:\\n", cleaned)

print("same-shape masks combine:", (matrix > 0) & (matrix < 4))
""",
            "questions": [
                "How are the cold-user and cold-item masks built, and why do they live on different axes?",
                "What does the density of the interaction matrix measure as a mask mean?",
                "Why can the two cold masks not be combined with a logical operator, and what does the final example show instead?",
            ],
            "answers": [
                "By comparing a row-wise sum to zero for users and a column-wise sum to zero for items, and they live on different axes because one has a length per user and the other a length per item.",
                "The fraction of user-item pairs with any interaction, computed as the mean of a boolean mask over the whole matrix.",
                "Because their shapes differ, so a logical operator has no position-by-position correspondence, whereas the final example combines two masks over the same matrix, which aligns and produces a per-entry result.",
            ],
            "homework": (
                "Write cold_start.py with an integer interaction matrix of at least four users and "
                "four items where some rows and some columns are entirely zero. Print the count of "
                "cold users and cold items from row-sum and column-sum masks and print the matrix "
                "density as the mean of an interaction mask. For one active user, print the positions "
                "and values of their items selected through a mask. Copy the matrix, cap values "
                "above a threshold by assigning through a mask and print it, and print the result of "
                "combining two same-shape masks with a logical operator. Observable output: six lines "
                "or blocks."
            ),
            "required_patterns": ["axis=1", "axis=0", "matrix > 0", ".sum()", "print("],
        },
        "reinforcement-learning": {
            "framing": (
                "Episode termination, invalid actions and success flags are all masks, and "
                "a policy's illegal-action rate is a mask mean."
            ),
            "application": (
                "Walk the example as a batch of transitions being screened. A mask over the "
                "done flags identifies the terminal steps, whose count is the number of "
                "complete episodes, and selecting the rewards through that mask gives the "
                "final rewards, which are the outcomes worth reporting. Invalid actions are "
                "the composition case: an action is legal if it is in the allowed set and "
                "the state permits it, which is two masks and-ed over an action axis, and "
                "the mean of the resulting mask is the legality rate that a mask-and-retrain "
                "loop monitors. The assignment form appears in masking a policy's logits "
                "before a softmax, where illegal positions are set to negative infinity "
                "through a mask so they receive no probability, and that is how a constraint "
                "is enforced without changing the network. The float caution matters in "
                "checking whether a value estimate has converged, where an exact equality "
                "mask is empty and a distance mask is the correct test."
            ),
            "example_hint": "screen terminal steps and illegal actions with masks and mask the policy logits",
            "assessment_angle": "what each mask counts and what masking logits before a softmax achieves",
            "day": 7,
            "title": "Done Flags and Illegal Actions: Masks Count and Constrain",
            "code": """import numpy as np

rewards = np.array([0.1, 1.0, -0.2, 2.0, 0.0])
dones = np.array([False, True, False, True, False])

print("episodes:", dones.sum())
print("final rewards:", rewards[dones])

legal = np.array([[True, True, False], [False, True, True]])
safe = np.array([[True, False, False], [True, True, False]])
allowed = legal & safe
print("allowed rate:", allowed.mean())

logits = np.array([1.0, 2.0, 0.5, 3.0])
action_mask = np.array([True, True, False, True])
masked = logits.copy()
masked[~action_mask] = -np.inf
probs = np.exp(masked - masked.max())
probs = probs / probs.sum()
print("policy probs:", np.round(probs, 3))

values = np.array([1.0000001, 1.0, 0.9999999])
print("converged by tolerance:", (np.abs(values - values.mean()) < 1e-6).mean())
""",
            "questions": [
                "How does the done mask serve both a count and a selection?",
                "What does the composition of the legal and safe masks express, and what does its mean report?",
                "Why are illegal logits set to negative infinity rather than to zero before the softmax?",
            ],
            "answers": [
                "Its sum is the number of completed episodes and it also selects the rewards at exactly those steps, so the mask is both a count of terminal steps and the selector of the final outcomes.",
                "The actions that are legal in the state and also safe, so it is the intersection of two constraints, and its mean is the fraction of action positions that satisfy both, which is the legality rate.",
                "Because negative infinity becomes zero after the exponential, so the illegal position receives no probability, whereas zero would still receive probability weight and keep the action selectable.",
            ],
            "homework": (
                "Write done_mask.py with a rewards array and a dones array of at least five steps "
                "and print the count of completed episodes and the final rewards selected through the "
                "mask. Build two boolean masks over an action axis, combine them and print the "
                "allowed rate as the mean. Build logits with a boolean action mask, set the illegal "
                "positions to negative infinity in a copy, compute a softmax and print the "
                "probabilities, and print the fraction of a small value array within a tolerance of "
                "its mean. Observable output: five lines."
            ),
            "required_patterns": ["dones.sum()", "rewards[dones]", "-np.inf", "&", "print("],
        },
        "gpu-programming": {
            "framing": (
                "A mask is the array-level expression of a branchless kernel, and the mask's "
                "mean is the occupancy a launch is judged on."
            ),
            "application": (
                "Walk the example as a computation expressed without branches. Selecting "
                "the elements above a threshold is a mask, and on a device that is a "
                "branchless pattern because the comparison produces a boolean array rather "
                "than a divergence-inducing if, which is exactly why vectorised code "
                "translates well to a wide device. The mean of a mask is the occupancy or "
                "hit rate, and it is the number a kernel's efficiency is reported against, "
                "because a mask that is rarely true means most threads did the work to "
                "evaluate a condition they failed. Combining masks is the way a compound "
                "predicate is expressed without nested branches, and the element-wise "
                "operators keep the whole thing vectorised. The assignment form is how a "
                "device-side clean-up is expressed: writing a sentinel through a mask sets "
                "the failing positions in place, and it is the pattern a validation kernel "
                "uses to mark results that failed a check."
            ),
            "example_hint": "express a threshold filter as a mask and report its occupancy and compound predicate",
            "assessment_angle": "why a mask is branchless and what its mean reports about efficiency",
            "day": 7,
            "title": "A Mask Is a Branchless Kernel: Measure Its Occupancy",
            "code": """import numpy as np

values = np.array([0.1, 5.0, 0.2, 9.0, 0.3], dtype=np.float32)
hit = values > 1.0

print("occupancy:", hit.mean(), "hits:", hit.sum())
print("selected:", values[hit])

within = (values > 0.05) & (values < 1.0)
print("compound predicate:", within, "count:", within.sum())

results = np.array([1.0, -1.0, 2.0, -3.0], dtype=np.float32)
validated = results.copy()
validated[results < 0] = 0.0
print("validated:", validated)

labels = (values > 1.0).astype(np.int32)
print("as indices:", labels)

left = values > 0.15
right = values < 8.0
print("either:", left | right)
""",
            "questions": [
                "Why is a mask described as branchless, and why does that matter on a wide device?",
                "What does the occupancy number report about the efficiency of the operation?",
                "What do the two ways of using the mask shown here, selection and assignment, correspond to in a kernel?",
            ],
            "answers": [
                "Because the comparison evaluates every element and produces a boolean array rather than a conditional that only some threads take, which matters because branches make threads on one device lane wait for the other path.",
                "The fraction of elements that satisfied the condition, so a low occupancy means most threads computed a comparison they failed, which is the efficiency figure a kernel is judged on.",
                "Selection corresponds to a compaction kernel that writes the surviving elements to a compact output, and assignment corresponds to a kernel that writes a sentinel to the failing positions in place.",
            ],
            "homework": (
                "Write mask_kernel.py with a float32 array of at least six values and build a "
                "threshold mask. Print its occupancy as the mean and the hit count as the sum, and "
                "print the selected values. Build a compound predicate from two comparisons with an "
                "element-wise operator and print it with its count, copy the array and zero the "
                "failing positions by assigning through the negative of a mask, and print the mask "
                "converted to integer indices plus a mask built by or-ing two conditions. Observable "
                "output: six lines."
            ),
            "required_patterns": ["> 1.0", ".mean()", "values[hit]", ".astype(", "print("],
        },
        "own-ml-framework": {
            "framing": (
                "Masking in a framework has to be differentiable, and the gradient through a "
                "mask is a multiplication by zero and one."
            ),
            "application": (
                "Walk the example as a masked operation recorded for autograd. The forward "
                "pass selects elements through a boolean mask, and the backward pass has to "
                "route the incoming gradient to exactly those positions, which it does by "
                "multiplying the gradient by the mask, so the masked-out positions receive "
                "zero and the selected positions receive their share. That is why masking is "
                "differentiable in practice: the mask is a factor in the backward pass "
                "rather than an operation that loses information silently. The composition "
                "of masks is what expresses a compound condition in a framework, and since "
                "the logical operators act element-wise, the backward pass for the "
                "composition is just the composed product. The subtlety worth naming is "
                "that a comparison producing a mask is not itself differentiable, because a "
                "boolean has no gradient, so a framework has to treat masks as constants in "
                "the graph and only make their application differentiable, which is a "
                "distinction that explains why one can mask a loss but not backpropagate "
                "through a threshold."
            ),
            "example_hint": "apply a mask forward and route the gradient back through it by multiplication",
            "assessment_angle": "why the backward pass multiplies by the mask and why the comparison itself has no gradient",
            "day": 7,
            "title": "Mask Forward, Multiply Backward: Zeros and Ones",
            "code": """import numpy as np


def masked_sum(values, mask):
    return values[mask].sum()


def masked_backward(values, mask, grad):
    out = np.zeros_like(values, dtype=np.float64)
    out[mask] = grad
    return out


values = np.array([1.0, 2.0, 3.0, 4.0])
mask = np.array([False, True, False, True])

forward = masked_sum(values, mask)
print("masked sum:", forward)
print("selected:", values[mask])

grad = masked_backward(values, mask, 1.0)
print("gradient:", grad)

compound = (values > 1.0) & (values < 4.0)
print("compound mask:", compound)
print("compound gradient:", masked_backward(values, compound, 1.0))

print("sum over mask mean:", mask.mean(), "count:", mask.sum())
""",
            "questions": [
                "Why does the backward pass place the incoming gradient only at the selected positions?",
                "What does the composed mask express, and how does its backward pass differ from the single mask's?",
                "Why is the comparison that produces a mask treated as a constant in the graph?",
            ],
            "answers": [
                "Because the forward sum only added the selected elements, so only they contributed to the output, and the gradient has to mirror that by carrying the incoming value to exactly those positions and nowhere else.",
                "The values that satisfy both conditions at once, and its backward pass is the same operation with the composed mask, so it routes the gradient to the intersection rather than to either set alone.",
                "Because a comparison's output is boolean and a boolean has no derivative, so the framework can differentiate applying a mask but not the threshold that created it.",
            ],
            "homework": (
                "Write masked_backward.py with a masked_sum function and a masked_backward function "
                "that places the incoming gradient at the selected positions and zero elsewhere. "
                "Print the masked sum and the selected values for a four-element array and a mask "
                "with two true positions, print the gradient for a scalar incoming value, then build "
                "a compound mask from two comparisons and print it with its gradient, and print the "
                "mask's mean and count. Observable output: five lines."
            ),
            "required_patterns": ["values[mask]", "np.zeros_like", "out[mask]", "&", "print("],
        },
    },
)
