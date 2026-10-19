"""Classification and detection models, days 135-149: training loops and metrics.

Every example is stdlib-only, offline and deterministic. Feature vectors are
plain lists, weights are hand-sized, and randomness comes from `random.Random`
with a fixed integer seed, so each lesson runs identically on any machine
without numpy, torch, torchvision, scikit-learn, PIL or an image file.
"""

PHASE = (
    "Classification and Detection Models",
    "Build a softmax classifier, evaluate it honestly, and reason about detection scores and anchors.",
    {
        135: dict(
            topic="Orientation: learned vision",
            idea=(
                "Vision models do not begin with edges or objects; they begin with numbers and a score. A learned "
                "classifier is a function with adjustable weights that maps a small feature vector to a class score, "
                "and learning means changing those weights when the score is wrong. The orientation matters because "
                "it reframes computer vision from a bag of tricks into parameter fitting. Start with a feature "
                "vector, say two measurements per image, and a linear score w1*x1 + w2*x2 + b. A decision rule turns "
                "the score into a label. Training repeats: predict, compare with the label, and nudge each weight in "
                "the direction that reduces the error. This is the perceptron update, and although modern networks "
                "use gradient descent over millions of parameters, the shape of the loop is identical. Two "
                "consequences follow. First, the features still matter: a linear model cannot see what the features "
                "did not measure. Second, the loop needs a stopping rule, because perfect training accuracy can mean "
                "memorisation. Today you run this loop by hand on four points, print the weights, and check that "
                "predictions improve. The point is not the toy accuracy; it is recognising the predict-compare-update "
                "cycle that every later training script wraps in a library."
            ),
            code="""def train(samples, epochs=4, lr=0.5):
    w = [0.0, 0.0]
    b = 0.0
    for _ in range(epochs):
        for x, y in samples:
            score = w[0] * x[0] + w[1] * x[1] + b
            pred = 1 if score >= 0 else 0
            err = y - pred
            w[0] += lr * err * x[0]
            w[1] += lr * err * x[1]
            b += lr * err
    return [round(v, 2) for v in w], round(b, 2)

samples = [((1, 1), 1), ((2, 1), 1), ((-1, -1), 0), ((-2, -1), 0)]
w, b = train(samples)
print("learned weights:", w, "bias:", b)
correct = 0
for x, y in samples:
    score = w[0] * x[0] + w[1] * x[1] + b
    pred = 1 if score >= 0 else 0
    correct += pred == y
    print("x", x, "score", round(score, 2), "pred", pred, "true", y)
print("training accuracy:", correct, "/", len(samples))
assert correct == len(samples)
print("the loop is predict, compare, update")
""",
            variant_b="initialise the weights at [1.0, -1.0] and count how many epochs are needed to separate the points",
            variant_c="add a third feature that is constant one and treat it as the bias, removing the separate b variable",
            mistakes=[
                "Forgetting to update the bias, so the boundary is forced through the origin.",
                "Using the raw score as a probability instead of thresholding or applying softmax.",
                "Training for many epochs and reporting training accuracy as if it were test accuracy.",
            ],
            q1=(
                "What are the three recurring steps inside a learned vision training loop?",
                "Predict with the current weights, compare the prediction with the label to get an error, then update the weights to reduce that error.",
            ),
            homework=(
                "Write `def train_perceptron(samples, epochs, lr)` that starts from zero weights, prints the weights "
                "after each epoch, and reports training accuracy. Run it on four two-feature samples and comment "
                "which update moves the decision boundary."
            ),
            patterns=["def train_perceptron", "epochs", "print("],
            mapping=(
                "A CNN training loop is the same predict-compare-update cycle with millions of weights, and the same "
                "stopping-rule question decides when training becomes memorisation."
            ),
        ),
        136: dict(
            topic="Datasets and labels",
            idea=(
                "Supervised vision starts with a dataset: a list of examples, each pairing an input with a label. The "
                "input might be a feature vector, an image path, or a nested grid of pixels; the label is the answer "
                "the model should produce. Before any model, inspect the list as data. How many examples are there? "
                "Which labels occur, and how often? Are the label strings consistent, or does 'cat', 'Cat' and "
                "'cats' create three classes out of one? Are feature lengths constant? A dataset is code, and it has "
                "bugs. A label taxonomy is a design decision, not a fact of nature. Two labels may overlap, one "
                "label may be too broad to learn, and rare labels may be impossible to evaluate. Writing a small "
                "validator early catches these problems while they are cheap. Today you build six labelled feature "
                "vectors, count per-class examples, list the label set, and assert the feature width. No files and "
                "no image library are needed; the structure is the lesson. The habit to take forward is that "
                "dataset inspection precedes model training. When a CNN performs badly, the first question is "
                "whether the labels and the sample counts are what you believe, and that question is answered by "
                "code like this."
            ),
            code="""SAMPLES = [
    ([0.2, 0.1], "cat"),
    ([0.9, 0.8], "dog"),
    ([0.1, 0.3], "cat"),
    ([0.8, 0.6], "dog"),
    ([0.4, 0.4], "bird"),
    ([0.5, 0.2], "cat"),
]

def class_counts(samples):
    counts = {}
    for _, label in samples:
        counts[label] = counts.get(label, 0) + 1
    return counts

def feature_width(samples):
    widths = {len(x) for x, _ in samples}
    if len(widths) != 1:
        raise ValueError("inconsistent feature width")
    return widths.pop()

counts = class_counts(SAMPLES)
print("examples:", len(SAMPLES))
print("labels:", sorted(counts))
print("counts:", counts)
print("feature width:", feature_width(SAMPLES))
print("rarest:", min(counts, key=counts.get))
assert sum(counts.values()) == len(SAMPLES)
assert feature_width(SAMPLES) == 2
print("dataset inspected before training")
""",
            variant_b="add two 'Cat' examples with a capital letter and show how the label count changes",
            variant_c="add a sample with three features and print the error raised by the width check",
            mistakes=[
                "Counting rows without checking that every label string is spelled consistently.",
                "Assuming class balance instead of printing per-class support before splitting.",
                "Mixing feature widths and only noticing when matrix multiplication fails later.",
            ],
            q1=(
                "Why inspect label counts and feature widths before training?",
                "Because inconsistent labels silently create extra classes and inconsistent widths break the model, and both are cheapest to fix before any training run.",
            ),
            homework=(
                "Write `def summarise_dataset(samples)` that returns the number of examples, sorted labels, "
                "per-class counts and feature width. Run it on the six samples above, raise a clear error for "
                "inconsistent widths, and print the rarest class."
            ),
            patterns=["def summarise_dataset", "counts", "print("],
            mapping=(
                "CNN datasets carry the same obligations: consistent class names, known support per class, and a "
                "fixed input shape that the network expects."
            ),
        ),
        137: dict(
            topic="Train, validation and test splits",
            idea=(
                "A model evaluated on the data it trained on is taking an open-book exam. Splitting separates three "
                "jobs: training adjusts parameters, validation chooses settings such as learning rate or "
                "augmentation strength, and test estimates performance on unseen data. The test set is touched "
                "once, at the end; every peek turns it into another validation set and makes the final number "
                "optimistic. Splits must be random but reproducible, which means a seeded shuffle rather than a "
                "fresh shuffle each run. The proportions depend on dataset size: a large dataset might use "
                "ninety-eight percent for training, while a small one needs a larger validation and test share to "
                "produce stable estimates. Stratification keeps class proportions similar across splits; without "
                "it a rare class can vanish from validation entirely. There is also a temporal split for video or "
                "street scenes, where random frames leak near-identical neighbours across sets. Today you shuffle "
                "ten numbered samples with a fixed seed, cut them into six, two and two, and assert that the index "
                "sets are disjoint and cover everything. The numbers are arbitrary; the invariants are the point. "
                "Once the split is trustworthy, every later accuracy number means something, and comparisons "
                "between experiments become legitimate. Treat it as frozen afterwards."
            ),
            code="""import random

DATA = list(range(10))

def split(items, seed):
    order = list(items)
    random.Random(seed).shuffle(order)
    n = len(order)
    train_end = int(n * 0.6)
    val_end = train_end + int(n * 0.2)
    return order[:train_end], order[train_end:val_end], order[val_end:]

train, val, test = split(DATA, 7)
print("train:", train)
print("val:  ", val)
print("test: ", test)
everything = train + val + test
assert len(train) == 6 and len(val) == 2 and len(test) == 2
assert sorted(everything) == DATA
assert not (set(train) & set(test))
again = split(DATA, 7)
assert again == (train, val, test)
print("disjoint, complete, reproducible")
""",
            variant_b="change the split to 50/25/25 and verify the same three invariants still hold",
            variant_c="add a `stratified_split(labels, seed)` helper that keeps class counts balanced across the cuts",
            mistakes=[
                "Tuning hyperparameters on the test set and then reporting that same score.",
                "Shuffling without a seed, so the split and the metric change on every run.",
                "Using a random split on video frames, which puts near-identical frames in train and test.",
            ],
            q1=(
                "What is the job of the validation set compared with the test set?",
                "Validation guides choices such as hyperparameters during development, while test is held back for one final, unbiased estimate.",
            ),
            homework=(
                "Write `def make_split(items, seed)` returning train, validation and test lists in a 60/20/20 cut. "
                "Assert that the three sets are disjoint and cover every item, run it twice with seed 7, and print "
                "both results."
            ),
            patterns=["def make_split", "random.Random", "assert"],
            mapping=(
                "CNN training uses the same split discipline, with the added rule that frames from one video or "
                "photos of one object must stay within a single split."
            ),
        ),
        138: dict(
            topic="A softmax classifier",
            idea=(
                "A classifier must turn arbitrary scores into probabilities, and softmax is the standard bridge. "
                "Given a vector of logits, one per class, softmax exponentiates each and divides by the sum. "
                "Exponentiation makes every value positive and exaggerates differences: a logit one unit larger "
                "than another yields about 2.7 times the probability before normalisation. The output sums to one, "
                "so it can be read as a distribution. Two practical details matter. First, subtract the maximum "
                "logit before exponentiating; this leaves the result mathematically unchanged and prevents "
                "overflow for large scores. Second, softmax preserves order, so the predicted class is simply the "
                "index of the largest logit, and the probability only says how confident the model is. Confidence "
                "is not correctness: a badly calibrated network can be confidently wrong, which is why loss and "
                "calibration are studied separately. Today you implement softmax over three logits with plain "
                "loops, round the probabilities for display, and verify they sum to one. You also compare two logit "
                "vectors with the same ranking but different gaps, and see how the gaps change confidence. That "
                "distinction — ranking versus confidence — returns when detection scores are thresholded. In code, keep the logits unrounded until the final print statement."
            ),
            code="""import math

CLASSES = ["cat", "dog", "bird"]

def softmax(logits):
    top = max(logits)
    exps = [math.exp(v - top) for v in logits]
    total = sum(exps)
    return [round(e / total, 3) for e in exps]

for logits in ([2.0, 1.0, 0.1], [2.0, 1.9, 1.8]):
    probs = softmax(logits)
    print("logits:", logits)
    print("probs: ", probs, "sum:", round(sum(probs), 3))
    print("predicted:", CLASSES[probs.index(max(probs))])
assert abs(sum(softmax([5.0, 5.0, 5.0])) - 1.0) < 0.01
assert softmax([0.0, 9.0, 0.0])[1] > 0.99
print("softmax turns scores into a distribution")
""",
            variant_b="compare logits [4.0, 2.0, 0.0] with [40.0, 20.0, 0.0] and explain why confidence grows",
            variant_c="write `argmax(values)` by hand and use it instead of `index(max(...))` to pick the class",
            mistakes=[
                "Exponentiating without subtracting the maximum, which overflows on large logits.",
                "Reading the largest probability as certainty rather than as a relative score.",
                "Rounding each probability before normalising, so the outputs no longer sum to one.",
            ],
            q1=(
                "Why subtract the maximum logit before calling `exp` in softmax?",
                "Subtracting the maximum leaves the ratios unchanged but keeps every exponent at or below zero, which prevents overflow.",
            ),
            homework=(
                "Write `def softmax(logits)` with max-subtraction and rounding, then classify three logit vectors. "
                "Print each probability list, its sum and the predicted class, and assert that equal logits give "
                "equal probabilities."
            ),
            patterns=["def softmax", "math.exp", "print("],
            mapping=(
                "CNN classifiers end in a softmax layer over classes, and detection models attach class scores to "
                "thousands of boxes that are later thresholded."
            ),
        ),
        139: dict(
            topic="Cross-entropy loss",
            idea=(
                "Cross-entropy measures how surprised a classifier is by the true label. With softmax output p and "
                "true class y, the loss is -log(p[y]). If the model assigns probability one to the correct class "
                "the loss is zero; if it assigns a tiny probability the loss grows without bound. This is why the "
                "loss punishes confident mistakes far more than uncertain ones, and why it pairs naturally with "
                "softmax: the gradient with respect to the logits is simply predicted minus one-hot target, a clean "
                "and cheap expression. Two failure modes deserve attention. Averaging losses over a batch is "
                "standard, but the average hides which examples dominate; a single impossible sample can swamp the "
                "rest. And a hard zero probability, produced by clipping or an overflow bug, sends the loss to "
                "infinity, so implementations clamp the probability before taking the logarithm. Today you compute "
                "cross-entropy for a good prediction, a bad prediction and a confidently wrong one, then compare "
                "their values. The ordering is the lesson: good below bad below confident error. You also see how "
                "one confident error contributes more total loss than several mild ones, which motivates label "
                "smoothing and careful annotation in real datasets. Clamping avoids infinite loss values."
            ),
            code="""import math

def cross_entropy(probs, target):
    return -math.log(max(probs[target], 1e-12))

cases = [
    ("good", [0.80, 0.15, 0.05], 0),
    ("bad", [0.10, 0.30, 0.60], 0),
    ("confident error", [0.01, 0.01, 0.98], 0),
]
losses = {}
for name, probs, target in cases:
    loss = round(cross_entropy(probs, target), 3)
    losses[name] = loss
    print(name, "p(true)=", probs[target], "loss=", loss)
print("ordering ok:", losses["good"] < losses["bad"] < losses["confident error"])
assert losses["good"] < losses["bad"] < losses["confident error"]
print("cross-entropy punishes confident mistakes")
""",
            variant_b="use a uniform prediction [1/3, 1/3, 1/3] and compare its loss with the confident error",
            variant_c="average the losses over the three cases and comment on why one confident error dominates the mean",
            mistakes=[
                "Taking the log of zero because the probability was never clamped.",
                "Applying cross-entropy to raw logits instead of softmax probabilities.",
                "Reporting mean loss without checking whether a few impossible samples dominate it.",
            ],
            q1=(
                "What happens to cross-entropy loss when the true-class probability approaches zero?",
                "The loss -log(p) grows toward infinity, so a confidently wrong prediction is penalised far more than an uncertain one.",
            ),
            homework=(
                "Write `def cross_entropy(probs, target)` clamped at a tiny probability, then compare a good, a bad "
                "and a confidently wrong prediction. Print the three losses and assert the confident error is "
                "largest."
            ),
            patterns=["def cross_entropy", "math.log", "assert"],
            mapping=(
                "Classification CNNs minimise the same cross-entropy over class scores, while detectors sum a "
                "classification loss with a box-regression loss."
            ),
        ),
        140: dict(
            topic="Augmentation pipelines",
            idea=(
                "Augmentation creates plausible variations of training images so the model sees more than the "
                "original sample. Horizontal flips, small crops, brightness changes and rotations are common, and "
                "they encode an assumption: the label survives the transformation. A flipped cat is still a cat, "
                "but a flipped traffic sign may not be, and a crop that removes the object destroys the label "
                "entirely. Augmentation is therefore domain knowledge expressed as code, not a generic switch. "
                "Determinism matters for experiments. A pipeline that samples fresh randomness each run makes two "
                "identical configurations produce different results, so seeds must be fixed and the same seed must "
                "reproduce the same transform. It also helps to keep augmentation in training only; applying random "
                "crops at evaluation makes metrics noisy and hard to compare. Today you implement a horizontal flip "
                "and a fixed-size crop on a small grid, drive the crop offset from a seeded random generator, and "
                "verify that the same seed produces the same augmented image. The code is deliberately tiny, but it "
                "demonstrates the contract every framework pipeline must satisfy: a labelled example in, a "
                "transformed labelled example out, reproducibly. Keep the original label attached to every transformed copy, and drop transforms that would invalidate it."
            ),
            code="""import random

IMAGE = [
    [10, 20, 30, 40],
    [50, 60, 70, 80],
    [90, 100, 110, 120],
    [130, 140, 150, 160],
]

def augment(image, seed):
    rng = random.Random(seed)
    out = [row[::-1] for row in image] if rng.random() < 0.5 else [row[:] for row in image]
    top = rng.randrange(0, len(image) - 2)
    left = rng.randrange(0, len(image[0]) - 2)
    return [row[left:left + 3] for row in out[top:top + 3]]

first = augment(IMAGE, 5)
second = augment(IMAGE, 5)
for label, grid in (("original", IMAGE), ("seed 5", first), ("seed 5 again", second)):
    print(label)
    for row in grid:
        print(" ", row)
assert first == second
assert first != IMAGE
print("same seed, same augmented crop")
""",
            variant_b="apply the augmentation only when a seeded coin flip says so, and print both branches for two seeds",
            variant_c="add a brightness offset that clips to 0-255, then check that no pixel leaves the valid range",
            mistakes=[
                "Applying random crops during evaluation, which makes the test metric noisy.",
                "Forgetting to fix the seed, so identical runs see different augmentations.",
                "Flipping a class where left-right orientation carries the label, such as a traffic sign.",
            ],
            q1=(
                "Why should augmentation randomness be seeded?",
                "So the same configuration reproduces the same images and any change in results comes from the model, not from a different random draw.",
            ),
            homework=(
                "Write `def augment(image, seed)` that applies a seeded horizontal flip and a three-by-three crop. "
                "Call it twice with the same seed, assert the outputs match, and print the original and both "
                "augmented grids."
            ),
            patterns=["def augment", "random.Random", "assert"],
            mapping=(
                "CNN training pipelines apply identical flips and crops per batch, and augmentation choices often "
                "matter more than a small architecture change."
            ),
        ),
        141: dict(
            topic="Transfer learning concept",
            idea=(
                "Transfer learning reuses features learned on a large dataset for a smaller target task. A network "
                "trained on millions of images has already learned filters for edges, textures and object parts; "
                "those early layers transfer well because they are general. The usual recipe freezes the "
                "convolutional backbone and trains a new classification head on the target labels. Freezing means "
                "the backbone weights are constants during optimisation, so only the head's parameters change. This "
                "is cheaper, needs less data, and reduces overfitting, but it also imposes a ceiling: if the target "
                "domain is very different, frozen features may be the wrong ones. Practitioners often unfreeze the "
                "last block and fine-tune with a small learning rate after the head has stabilised. Two mistakes "
                "recur. Recomputing normalisation statistics on the new data without matching the backbone's "
                "expected input harms accuracy. And evaluating on images that were part of pretraining inflates "
                "results, a subtle leakage. Today you simulate the idea with a hand-set extractor that maps an input "
                "to two features, snapshot its parameters, train a tiny head on three examples, and verify the "
                "extractor did not move. The separation between frozen representation and trainable head is the "
                "concept that matters. Check the input range too."
            ),
            code="""EXTRACTOR = [0.6, 0.4]

def extract(x):
    return [round(EXTRACTOR[0] * x[0], 2), round(EXTRACTOR[1] * x[1], 2)]

def train_head(samples, epochs=6, lr=0.2):
    w = [0.0, 0.0]
    for _ in range(epochs):
        for x, y in samples:
            feats = extract(x)
            pred = 1 if w[0] * feats[0] + w[1] * feats[1] >= 0 else 0
            err = y - pred
            w = [w[0] + lr * err * feats[0], w[1] + lr * err * feats[1]]
    return [round(v, 2) for v in w]

before = list(EXTRACTOR)
samples = [((1.0, 1.0), 1), ((2.0, 1.0), 1), ((0.2, 0.1), 0)]
head = train_head(samples)
print("frozen extractor before:", before)
print("frozen extractor after: ", EXTRACTOR)
print("trained head weights:  ", head)
print("extractor unchanged:", before == EXTRACTOR)
print("head adapted:", head != [0.0, 0.0])
assert before == EXTRACTOR
assert head != [0.0, 0.0]
print("features frozen, head learned")
""",
            variant_b="start the head at [0.5, 0.5] instead of zeros and compare the final head weights",
            variant_c="unfreeze the extractor for one extra epoch and show that both the head and features change",
            mistakes=[
                "Fine-tuning the whole backbone with a large learning rate and destroying the pretrained features.",
                "Preprocessing target images differently from the data the backbone was trained on.",
                "Evaluating on images that belong to the pretraining set and reporting the inflated score.",
            ],
            q1=(
                "What does freezing a backbone mean during transfer learning?",
                "Its weights are held constant and receive no updates, so only the new head is trained on the target labels.",
            ),
            homework=(
                "Write `def train_head(samples)` that keeps the extractor weights frozen and updates only the head. "
                "Print the extractor before and after, assert it is unchanged, and report whether the head moved "
                "away from zero."
            ),
            patterns=["def train_head", "extract", "assert"],
            mapping=(
                "Most practical CNN projects start from an ImageNet-pretrained backbone, then fine-tune the head or "
                "the last block instead of training millions of parameters from scratch."
            ),
        ),
        142: dict(
            topic="Confusion matrix for vision",
            idea=(
                "A confusion matrix is the first honest view of a classifier beyond accuracy. Rows are true "
                "classes, columns are predictions, and the diagonal holds correct answers. Off-diagonal cells say "
                "which classes are being mixed up, which is far more actionable than a single percentage. From the "
                "matrix you derive per-class precision and recall: recall is the fraction of true instances found, "
                "precision is the fraction of predicted instances that were right. A class with high precision but "
                "low recall is conservative; the opposite is over-eager. Accuracy alone hides both, especially with "
                "imbalanced data where predicting the majority class scores well while ignoring everything else. "
                "Two conventions exist for row and column order, so label the axes in code and in reports. Also "
                "decide what to do with low-support classes: a recall of 1.0 from one example is not evidence. "
                "Today you build a three-class matrix from six predictions with plain nested loops, print the rows, "
                "and compute accuracy plus per-class recall. The arithmetic is trivial; the habit of looking at the "
                "structure is what transfers to detection, where the same cells reappear per class at a fixed "
                "confidence threshold. Normalising each row into proportions can make small classes easier to compare."
            ),
            code="""LABELS = ["cat", "dog", "bird"]
TRUTH = ["cat", "dog", "cat", "bird", "dog", "bird"]
PRED = ["cat", "cat", "cat", "bird", "dog", "dog"]

matrix = [[0] * len(LABELS) for _ in LABELS]
for truth, pred in zip(TRUTH, PRED):
    matrix[LABELS.index(truth)][LABELS.index(pred)] += 1

print("rows=true, cols=pred", LABELS)
for name, row in zip(LABELS, matrix):
    print(name, row)
correct = sum(matrix[i][i] for i in range(len(LABELS)))
print("accuracy:", round(correct / len(TRUTH), 3))

def recall(cls):
    i = LABELS.index(cls)
    actual = sum(matrix[i])
    return round(matrix[i][i] / actual, 3) if actual else 0.0

for cls in LABELS:
    print("recall", cls, recall(cls))
assert correct == 4
assert recall("dog") == 0.5
print("confusion matrix exposes class confusions")
""",
            variant_b="add one more dog predicted as bird and recompute accuracy and the dog and bird recalls",
            variant_c="extend the code with per-class precision as the diagonal divided by the column sum",
            mistakes=[
                "Confusing row and column meaning, so precision and recall are computed from the wrong axis.",
                "Reporting accuracy on imbalanced data where the majority class dominates the diagonal.",
                "Treating a perfect recall from a single example as strong evidence about that class.",
            ],
            q1=(
                "What does one off-diagonal cell in a confusion matrix tell you?",
                "How many examples of the row's true class were predicted as the column's class, which names a specific confusion to investigate.",
            ),
            homework=(
                "Write `def confusion_matrix(truth, pred, labels)` returning a nested list. Print the rows, "
                "accuracy and per-class recall, then assert one known off-diagonal count from the six predictions "
                "above."
            ),
            patterns=["def confusion_matrix", "recall", "assert"],
            mapping=(
                "Detection evaluation produces one confusion matrix per class at a confidence threshold, and its "
                "off-diagonal errors separate classification mistakes from localisation failures."
            ),
        ),
        143: dict(
            topic="mAP concept",
            idea=(
                "Mean average precision summarises detection quality across classes and confidence thresholds. "
                "Unlike classification accuracy, a detector produces ranked boxes with scores, so evaluation must "
                "decide which boxes are true positives, false positives, or missed. A prediction counts as a true "
                "positive only if it overlaps a ground-truth box above an IoU threshold and that ground truth has "
                "not already been claimed. Sorting all predictions by confidence and walking down the list yields "
                "precision and recall at every rank. Average precision is the area under that precision-recall "
                "curve; mean average precision averages it over classes. The details matter: matching order, "
                "duplicate suppression, and whether unmatched ground truths count as missed affect the number. AP "
                "rewards ranking correct detections above wrong ones, not just finding them eventually. This is why "
                "a detector that returns many low-confidence guesses can look fine at high recall but score poorly "
                "overall. Today you compute an eleven-point interpolated AP for two tiny ranked lists with plain "
                "loops, then average the two values. The dataset is absurdly small, but the mechanics are exactly "
                "those of a real evaluator; only the arrays are longer. Per-class AP also exposes a class that is rare but easy, which can pull the mean in a misleading direction."
            ),
            code="""def average_precision(ranked):
    total = sum(hit for _, hit in ranked)
    points = []
    for step in range(11):
        recall_target = step / 10
        hits = 0
        best = 0.0
        for rank, (score, hit) in enumerate(ranked, start=1):
            hits += hit
            if hits / total >= recall_target:
                best = max(best, hits / rank)
        points.append(best)
    return round(sum(points) / len(points), 3)

car = [(0.95, 1), (0.80, 0), (0.70, 1), (0.40, 1)]
person = [(0.90, 0), (0.60, 1), (0.30, 0)]
ap_car = average_precision(car)
ap_person = average_precision(person)
print("AP car:   ", ap_car)
print("AP person:", ap_person)
print("mAP:      ", round((ap_car + ap_person) / 2, 3))
assert ap_car > ap_person
assert 0.0 <= ap_car <= 1.0
print("mAP averages ranked precision-recall curves")
""",
            variant_b="move the true-positive detection from rank three to rank one and recompute AP for cars",
            variant_c="add a third class with two false positives and show how the mean changes",
            mistakes=[
                "Matching several detections to the same ground-truth box, creating duplicate true positives.",
                "Computing precision and recall without sorting predictions by confidence first.",
                "Comparing mAP numbers produced with different IoU thresholds as if they were the same metric.",
            ],
            q1=(
                "Why must detections be sorted by confidence before computing average precision?",
                "AP measures the quality of the ranking as well as the detections, so precision is accumulated as the confidence threshold falls.",
            ),
            homework=(
                "Write `def average_precision(ranked)` implementing eleven-point interpolation, then compute AP for "
                "the car and person lists and their mean. Print each value and assert that AP stays between zero "
                "and one."
            ),
            patterns=["def average_precision", "recall", "assert"],
            mapping=(
                "COCO-style detector evaluation reports mAP at several IoU thresholds, and the ranking behaviour it "
                "measures is what separates a usable detector from a lucky one."
            ),
        ),
        144: dict(
            topic="Anchor boxes",
            idea=(
                "Detectors do not regress boxes from nothing; they start from anchor boxes, a fixed set of reference "
                "rectangles at several scales and aspect ratios. Each anchor is compared with the ground-truth "
                "boxes using intersection over union, and anchors above a positive threshold are trained to predict "
                "the nearby object; anchors below a negative threshold become background examples. The ones in "
                "between are usually ignored, because forcing a decision there adds noise. IoU is the area of "
                "overlap divided by the area of union, and it is the same metric used at evaluation time, which is "
                "why anchor design and evaluation thresholds must be chosen together. Hand-set anchors are a prior "
                "about object size: if every anchor is small, large objects will never match well. Modern detectors "
                "learn anchors or predict boxes densely, but the matching problem is unchanged. Today you implement "
                "IoU from coordinates, score one ground-truth box against three hand-set anchors, and label each "
                "anchor positive, negative or ignored by threshold. Watch the edge cases: boxes that merely touch "
                "have zero overlap, and box coordinates must be converted consistently from corner or centre plus "
                "size. Anchor matching is a design choice, and reviewing a few matches by hand catches broken coordinate conventions quickly."
            ),
            code="""def iou(box_a, box_b):
    ax, ay, aw, ah = box_a
    bx, by, bw, bh = box_b
    left = max(ax, bx)
    top = max(ay, by)
    right = min(ax + aw, bx + bw)
    bottom = min(ay + ah, by + bh)
    overlap = max(0, right - left) * max(0, bottom - top)
    union = aw * ah + bw * bh - overlap
    return overlap / union if union else 0.0

GT = (2, 2, 4, 4)
ANCHORS = [(2, 2, 4, 4), (0, 0, 4, 4), (6, 6, 2, 2)]
for index, anchor in enumerate(ANCHORS):
    score = round(iou(anchor, GT), 3)
    if score >= 0.5:
        label = "positive"
    elif score >= 0.3:
        label = "ignored"
    else:
        label = "negative"
    print("anchor", index, "iou", score, label)
best = max(range(len(ANCHORS)), key=lambda i: iou(ANCHORS[i], GT))
print("best anchor:", best, "iou:", round(iou(ANCHORS[best], GT), 3))
assert iou(GT, GT) == 1.0
assert iou(GT, ANCHORS[2]) == 0.0
print("anchors matched by IoU thresholds")
""",
            variant_b="add an anchor of size 8x8 at the same origin and compare its IoU with the 4x4 anchor",
            variant_c="shift the ground truth by two pixels and reprint which anchors are positive, ignored or negative",
            mistakes=[
                "Mixing corner coordinates with centre-plus-size coordinates when computing overlap.",
                "Letting one ground-truth box produce several positive anchors during evaluation matching.",
                "Setting anchors all at one scale, so objects much larger or smaller never match above threshold.",
            ],
            q1=(
                "What does an IoU of 0.5 between an anchor and a ground-truth box mean?",
                "The overlap area is half the area of their union, which is why 0.5 is a common positive-matching threshold.",
            ),
            homework=(
                "Write `def iou(box_a, box_b)` and `def match_anchor(anchor, gt)` returning positive, ignored or "
                "negative. Run them over the three anchors, print each score and label, and assert that a box "
                "matched with itself scores 1.0."
            ),
            patterns=["def iou", "def match_anchor", "assert"],
            mapping=(
                "Single-shot CNN detectors assign anchors to ground truth by IoU, then train class and box offsets "
                "on the positive matches."
            ),
        ),
        145: dict(
            topic="Data leakage in vision",
            idea=(
                "Data leakage is any information in training that would not be available at prediction time, and "
                "vision datasets leak easily. The classic case is near-duplicate images: consecutive video frames, "
                "burst photos, or augmentations of the same source appearing in different splits. A model can then "
                "memorise a scene and score well on the test set without generalising. Leakage also enters through "
                "preprocessing fitted on the full dataset, such as computing normalisation statistics before "
                "splitting, or through labels derived from metadata that will not exist in deployment. The symptom "
                "is a large gap between impressive test results and disappointing real-world performance. The fix "
                "is to split by source, not by image: group frames from one video, keep all photos of one object "
                "together, and deduplicate near-identical inputs before splitting. Today you build a train set and "
                "a test set that share exact duplicates, measure a nearest-neighbour classifier's accuracy, then "
                "remove duplicates and measure again. The drop is the point. Exact matching is a simplification; "
                "real deduplication uses perceptual hashes or embedding distance, but the diagnostic habit is the "
                "same. Before trusting a benchmark number, ask honestly how its splits were built and whether any preprocessing saw the test images at all."
            ),
            code="""def nearest(features, train):
    best = None
    best_distance = None
    for x, label in train:
        d = sum((a - b) ** 2 for a, b in zip(features, x))
        if best_distance is None or d < best_distance:
            best_distance = d
            best = label
    return best

train = [([0.0, 0.0], "cat"), ([1.0, 1.0], "dog"), ([0.0, 1.0], "cat")]
leaky_test = [([0.0, 0.0], "cat"), ([1.0, 1.0], "dog")]
clean_test = [([0.7, 0.7], "cat")]

def accuracy(test, train):
    hits = sum(nearest(x, train) == label for x, label in test)
    return round(hits / len(test), 3)

leaky = accuracy(leaky_test, train)
clean = accuracy(clean_test, train)
print("test with duplicates:", leaky)
print("test after dedupe:   ", clean)
print("inflation:", round(leaky - clean, 3))
assert leaky > clean
assert leaky == 1.0
print("duplicate images leak answers into the test set")
""",
            variant_b="add one near-duplicate with a small offset and show that exact matching no longer detects it",
            variant_c="split by source id instead of by image and explain how that removes the duplicate overlap",
            mistakes=[
                "Splitting video frames randomly, so almost identical neighbours land on both sides.",
                "Fitting normalisation statistics on all images before creating the splits.",
                "Deduplicating only exact pixels and missing resized or recompressed copies of the same photo.",
            ],
            q1=(
                "Why do random image splits leak in video datasets?",
                "Because consecutive frames are nearly identical, so a test frame usually has a near-copy of itself in training.",
            ),
            homework=(
                "Write `def find_duplicates(train, test)` that returns test examples exactly matching a training "
                "feature vector. Print the duplicate count, remove those rows, and assert that the cleaned test set "
                "has no overlap."
            ),
            patterns=["def find_duplicates", "assert", "print("],
            mapping=(
                "CNN benchmarks split by scene, video or photographer to prevent memorisation, and preprocessing "
                "statistics are computed on the training split only."
            ),
        ),
        146: dict(
            topic="Error analysis on images",
            idea=(
                "Error analysis turns a metric into a plan. Sort the failures, inspect them, and count causes; a "
                "classifier at eighty percent accuracy may fail mostly on blurry images, or mostly on one confused "
                "class pair, or mostly because labels are wrong. These imply different fixes. Blur suggests better "
                "augmentation or a sharper input pipeline. A specific class pair suggests more discriminative data "
                "or a targeted feature. Bad labels suggest a relabelling pass before any model change. A useful "
                "routine is to bucket every false positive and false negative by an observable tag — lighting, "
                "occlusion, size, source — and report counts rather than anecdotes. The tags are hypotheses, so keep "
                "them simple and honest. It also helps to look at the confidence distribution: errors with very high "
                "confidence often mean label noise, while errors near the decision threshold may be unavoidable "
                "ambiguity. Today you take six labelled predictions with tags, separate false positives from false "
                "negatives with loops, and count failures per tag. The dataset is tiny; the discipline scales. In "
                "detection the same step separates localisation errors from classification errors and background "
                "confusion. Write the counts down before changing anything, so the next run can show whether the fix actually worked."
            ),
            code="""RECORDS = [
    ("a", "cat", "cat", "sharp"),
    ("b", "dog", "cat", "blur"),
    ("c", "dog", "dog", "sharp"),
    ("d", "bird", "dog", "blur"),
    ("e", "cat", "dog", "low_light"),
    ("f", "bird", "bird", "low_light"),
]

false_negatives = []
false_positives = []
tag_counts = {}
for name, truth, pred, tag in RECORDS:
    if truth == pred:
        continue
    false_negatives.append((name, truth, tag))
    false_positives.append((name, pred, tag))
    tag_counts[tag] = tag_counts.get(tag, 0) + 1

print("false negatives:", len(false_negatives))
for name, truth, tag in false_negatives:
    print("  missed", truth, "on", name, "tag", tag)
print("false positives:", len(false_positives))
for name, pred, tag in false_positives:
    print("  predicted", pred, "on", name, "tag", tag)
print("failures by tag:", tag_counts)
assert len(false_negatives) == 3
assert tag_counts["blur"] == 2
print("error analysis groups failures by cause")
""",
            variant_b="add a confidence field and list only high-confidence errors, which often indicate label noise",
            variant_c="add a size tag and test whether failures cluster among small objects",
            mistakes=[
                "Listing a few memorable failures instead of counting every error by category.",
                "Changing the model before checking whether the failing labels are actually correct.",
                "Treating a tag as a proven cause when it is only a hypothesis about the failure.",
            ],
            q1=(
                "What is the difference between a false positive and a false negative here?",
                "A false positive is a wrong predicted class on a real example, while a false negative is a true class the model failed to predict.",
            ),
            homework=(
                "Write `def analyse_errors(records)` returning false negatives, false positives and a per-tag "
                "failure count. Print each group, assert the totals agree, and name the tag you would fix first."
            ),
            patterns=["def analyse_errors", "tag", "assert"],
            mapping=(
                "Detector error analysis separates classification errors, localisation errors and missed objects, "
                "which point to different changes in training data or anchors."
            ),
        ),
        147: dict(
            topic="Balancing classes",
            idea=(
                "Class imbalance is normal in vision: background dominates detection images, rare species dominate "
                "conservation datasets, and defects are rare in manufacturing. A model trained on raw counts learns "
                "to predict the majority class and can still report high accuracy. Three responses are common. "
                "Resampling oversamples rare classes or undersamples common ones, changing what the model sees per "
                "epoch. Class weighting keeps the data but scales each example's loss by inverse frequency, so rare "
                "mistakes cost more. Threshold tuning leaves training alone and chooses a decision point that "
                "matches the operating cost. Each has trade-offs: oversampling can duplicate the same few images "
                "and overfit, undersampling throws away data, and weighting can destabilise training if weights are "
                "extreme. Evaluate with per-class recall and precision, not accuracy, and report support for every "
                "class. Today you count three classes, compute inverse-frequency weights, and compare the weighted "
                "contribution of each class under raw and balanced loss. The arithmetic shows why weighting works: "
                "after multiplication, each class contributes equally in expectation. That is a deliberate choice, "
                "not a universal truth; costs should follow the application. Report support next to every per-class metric, because a recall of one from only two labelled examples is always mostly noise."
            ),
            code="""COUNTS = {"cat": 6, "dog": 2, "bird": 2}
total = sum(COUNTS.values())
classes = len(COUNTS)
weights = {
    name: round(total / (classes * count), 3)
    for name, count in COUNTS.items()
}
print("counts: ", COUNTS)
print("weights:", weights)
raw_total = 0.0
balanced_total = 0.0
for name, count in COUNTS.items():
    raw = count * 1.0
    balanced = count * weights[name]
    raw_total += raw
    balanced_total += balanced
    print(name, "raw", round(raw, 2), "weighted", round(balanced, 2))
print("raw total:", round(raw_total, 2))
print("balanced total:", round(balanced_total, 2))
assert weights["cat"] < weights["dog"]
assert abs((COUNTS["cat"] * weights["cat"]) - (COUNTS["dog"] * weights["dog"])) < 0.01
print("class weights equalise rare and common classes")
""",
            variant_b="use weights proportional to one over the square root of the count and compare the totals",
            variant_c="build an oversampled index list that repeats rare-class examples until counts match",
            mistakes=[
                "Reporting accuracy on an imbalanced dataset and declaring the majority-class model good.",
                "Oversampling the same few rare images until the model memorises them.",
                "Using extreme class weights that make gradients unstable instead of tuning them.",
            ],
            q1=(
                "How do inverse-frequency class weights change training?",
                "They scale each example's loss so rare-class mistakes cost more, making each class contribute more equally.",
            ),
            homework=(
                "Write `def class_weights(counts)` returning inverse-frequency weights. Print raw and weighted "
                "totals, assert each class contributes equally, and comment which class gets the largest weight."
            ),
            patterns=["def class_weights", "weights", "assert"],
            mapping=(
                "Detection training weights foreground and background samples, and hard-example mining plays the "
                "same role as balancing for classification."
            ),
        ),
        148: dict(
            topic="Reproducible vision experiments",
            idea=(
                "An experiment is reproducible when a second person, or the same person next week, can rerun it and "
                "obtain the same result. Vision pipelines have many randomness sources: weight initialisation, data "
                "shuffling, augmentation sampling, dropout and non-deterministic GPU kernels. Fixing a seed is "
                "necessary but not sufficient; the seed must control every source, and library versions must be "
                "recorded because defaults change. A useful habit is to make the seed an explicit parameter, derive "
                "independent generators for splitting and augmentation, and log the configuration next to the "
                "metrics. Determinism also has a cost: identical seeds can hide sensitivity, so report a few seeds "
                "when the conclusion is close. If results move more between seeds than between two architectures, "
                "the comparison is not yet meaningful. Today you write a small seeded pipeline that shuffles "
                "indices and samples scale factors, run it twice with the same seed and once with a different seed, "
                "and assert the first two match while the third differs. No files or timestamps are involved, so the "
                "demonstration is exact. The lesson generalises to full training runs, where the same discipline "
                "separates a real improvement from noise. Write the seed and versions into the run log rather than remembering them."
            ),
            code="""import random

def run_experiment(seed):
    rng = random.Random(seed)
    order = list(range(8))
    rng.shuffle(order)
    scales = [round(rng.uniform(0.8, 1.2), 2) for _ in order]
    return order, scales

first = run_experiment(11)
second = run_experiment(11)
other = run_experiment(12)
print("same seed equal:", first == second)
print("order:", first[0])
print("scales:", first[1])
print("different seed equal:", first == other)
assert first == second
assert first != other
print("fixed seeds reproduce the whole pipeline")
""",
            variant_b="return a tuple of split indices, augmentation scales and initial weights from one seeded generator",
            variant_c="run three seeds and print the spread of a summary value to show seed sensitivity",
            mistakes=[
                "Seeding only the shuffle but leaving augmentation on an unseeded generator.",
                "Recording the seed but not the library versions, which can change default behaviour.",
                "Comparing two models from single runs when the seed-to-seed variation is larger than the gap.",
            ],
            q1=(
                "Why is one fixed seed not enough to make a vision experiment reproducible?",
                "Every randomness source needs control, and unseeded augmentation, initialisation or non-deterministic kernels can still change the result.",
            ),
            homework=(
                "Write `def run_experiment(seed)` that shuffles eight indices and samples eight scale factors. Call "
                "it twice with seed 11 and once with seed 12, assert the first two match, and print all three "
                "results."
            ),
            patterns=["def run_experiment", "random.Random", "assert"],
            mapping=(
                "CNN training scripts expose a seed flag for splitting, augmentation and initialisation, and serious "
                "comparisons report variation across several seeds."
            ),
        ),
        149: dict(
            topic="Review: classification and detection checklist",
            idea=(
                "A checklist is not bureaucracy; it is the compressed memory of mistakes already made. For "
                "classification, confirm the split has no duplicates, labels are consistent, class support is "
                "reported, and the metric is chosen for the operating cost. Confirm preprocessing is fitted on "
                "training data only and that augmentation is applied only during training. For training, record the "
                "seed, learning rate, input size and class weights, and keep a baseline that the new model must "
                "beat. For evaluation, report per-class precision and recall, a confusion matrix, and confidence "
                "calibration where it matters. For detection, state the IoU threshold, the matching rule and whether "
                "mAP is computed per class before averaging. Check that low-confidence detections are not silently "
                "counted as true positives, and that duplicate predictions are suppressed. Finally, inspect a "
                "sample of successes and failures with your own eyes; metrics compress reality and can hide a "
                "systematic problem. Today you run a compact end-to-end check on a toy dataset: split, fit a "
                "one-step classifier, build the confusion matrix, score an anchor by IoU, and print boolean "
                "checklist items. The asserts make the review executable, which is the only kind of checklist that "
                "stays honest. A failing check is a finding, not an inconvenience."
            ),
            code="""import random

DATA = [
    ([0.1, 0.2], 0), ([0.8, 0.9], 1), ([0.2, 0.3], 0),
    ([0.7, 0.8], 1), ([0.4, 0.2], 0), ([0.6, 0.7], 1),
]
order = list(DATA)
random.Random(3).shuffle(order)
train, test = order[:4], order[4:]

w = [0.0, 0.0]
for _ in range(5):
    for x, y in train:
        score = w[0] * x[0] + w[1] * x[1]
        pred = 1 if score >= 0.5 else 0
        err = y - pred
        w = [w[0] + 0.5 * err * x[0], w[1] + 0.5 * err * x[1]]

preds = [1 if w[0] * x[0] + w[1] * x[1] >= 0.5 else 0 for x, _ in test]
truths = [y for _, y in test]
matrix = [[0, 0], [0, 0]]
for truth, pred in zip(truths, preds):
    matrix[truth][pred] += 1
train_keys = {tuple(x) for x, _ in train}
test_keys = {tuple(x) for x, _ in test}

def iou(a, b):
    left, top = max(a[0], b[0]), max(a[1], b[1])
    right = min(a[0] + a[2], b[0] + b[2])
    bottom = min(a[1] + a[3], b[1] + b[3])
    overlap = max(0, right - left) * max(0, bottom - top)
    union = a[2] * a[3] + b[2] * b[3] - overlap
    return overlap / union if union else 0.0

anchor_score = round(iou((1, 1, 3, 3), (2, 2, 3, 3)), 3)
checks = [not (train_keys & test_keys), len(matrix[0]) == 2, anchor_score > 0]
print("train/test sizes:", len(train), len(test))
print("weights:", [round(v, 2) for v in w])
print("confusion matrix:", matrix)
print("anchor iou:", anchor_score)
print("checklist:", checks)
assert all(checks)
print("review checklist is executable and passing")
""",
            variant_b="add a per-class support check and a seed-recording check to the boolean list",
            variant_c="raise the anchor IoU threshold to 0.6 and show the checklist failing honestly",
            mistakes=[
                "Running the checklist once at the start instead of before every reported result.",
                "Checking accuracy but skipping per-class recall and the confusion matrix.",
                "Forgetting to state the IoU threshold when comparing detection mAP numbers.",
            ],
            q1=(
                "Why should a review checklist be executable code rather than a prose list?",
                "Because asserts fail loudly when a condition is violated, while a prose list is easy to skim and skip.",
            ),
            homework=(
                "Write `def review(checklist)` that asserts every named check is true and prints the checklist. "
                "Include a duplicate-free split check, a per-class support check and an IoU threshold check in your "
                "own run."
            ),
            patterns=["def review", "assert", "print("],
            mapping=(
                "Before trusting a CNN result, the same review covers split hygiene, per-class metrics, seeding and "
                "the IoU rule used for detection evaluation."
            ),
        ),
    },
)
