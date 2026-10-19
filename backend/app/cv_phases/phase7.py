"""Computer Vision capstone, days 165-179: ship one small pipeline end to end.

Every example is stdlib-only, offline and deterministic. The whole phase builds
one toy capstone — classifying 4x4 binary grids into four shapes — so the spec,
data contract, loader, preprocessing, classifier, metrics, tests, error
analysis, speed measurement and packaging are all slices of the same program.
"""

PHASE = (
    "Computer Vision Capstone",
    "Ship one small, reproducible vision pipeline end to end, from scope and data contract to evaluated, tested, packaged results.",
    {
        165: dict(
            topic="Capstone: choose the scope",
            idea=(
                "Every capstone begins by refusing work, because an unbounded vision project never ships. The "
                "technique today is a one-page scope document written as a Python dict: task, classes, in-scope "
                "inputs, explicit out-of-scope cases, the single metric, and the success threshold. Writing it as "
                "data forces each decision to be concrete, so 'classify shapes' becomes 'classify fixed 4x4 binary "
                "grids into h, v, d or x'. The out-of-scope list matters most, because it is where scope creep is "
                "stopped: colour, rotation, multiple objects and real photographs are named and deferred. Fixing "
                "one metric before any code prevents the usual drift where accuracy is quoted when it looks good "
                "and recall when it does not. The success threshold, ideally tied to a trivial baseline such as the "
                "majority class, tells you when to stop. Keep the scope small enough that the whole pipeline runs "
                "offline in under a second, which makes every later experiment cheap and repeatable. The dict is "
                "not documentation that rots; it is imported by the tests, so an out-of-scope case can be asserted "
                "against rather than merely promised. Today you write the spec for the toy capstone you will build "
                "all week: four shapes, 4x4 grids, accuracy on a held-out sample. Everything after this is filling "
                "in boxes the spec already named."
            ),
            code=(
                'SPEC = {\n'
                '    "task": "classify 4x4 binary grids as h, v, d, x",\n'
                '    "classes": ["h", "v", "d", "x"],\n'
                '    "in_scope": ["fixed 4x4 grid", "one shape per image", "binary pixels"],\n'
                '    "out_of_scope": ["colour", "rotation", "multiple objects"],\n'
                '    "metric": "accuracy",\n'
                '    "success": 0.9,\n'
                '}\n'
                '\n'
                'for key in ("task", "classes", "in_scope", "out_of_scope", "metric", "success"):\n'
                '    print(key, ":", SPEC[key])\n'
                '\n'
                'assert set(SPEC["classes"]) == {"h", "v", "d", "x"}\n'
                'assert SPEC["metric"] == "accuracy" and SPEC["success"] == 0.9\n'
                'print("scope fixed:", len(SPEC["classes"]), "classes, one metric")\n'
            ),
            variant_b="add a 'deferred' key listing rotation and noise, and explain why each is not in scope",
            variant_c="lower the success threshold to 0.8 and note what that buys in build time",
            mistakes=[
                "Naming a task so broadly that no single metric can decide success.",
                "Leaving out-of-scope cases implicit, so they reappear as surprise requirements midway.",
                "Choosing several metrics before any data exists, then reporting whichever looks best.",
            ],
            q1=(
                "Why write the scope as a dict rather than a paragraph?",
                "Because a dict can be imported and asserted on, making the scope an executable boundary instead of prose that drifts.",
            ),
            homework=(
                "Write `choose_scope()` returning a scope dict with task, classes, in_scope, out_of_scope, metric "
                "and success keys for your own capstone idea. Print each key and value, and comment which "
                "out_of_scope entry stops the most tempting scope creep."
            ),
            patterns=["def ", "choose_scope", "print("],
            mapping=(
                "Every real vision project opens with a scoping document that fixes one metric and one baseline; "
                "product teams call it an evaluation plan, and it is the same artefact."
            ),
        ),
        166: dict(
            topic="Write the vision spec",
            idea=(
                "Yesterday's scope dict answered what to build; today it becomes a template with fixed sections "
                "so no project silently omits one. The technique is a `make_spec` function that takes keyword "
                "sections and refuses to return unless every required key — task, inputs, outputs, metric, baseline "
                "and success — is present. Writing the refusal is the point: a missing section raises immediately "
                "at construction time rather than surfacing as a vague failure late in evaluation. Each section "
                "has a job. Inputs state the exact shape and value range, in this capstone a 4x4 grid of 0 or 255. "
                "Outputs name the label set and its order, because an unordered class list makes confusion "
                "matrices unreadable. Metric and baseline pair up: you cannot judge accuracy without knowing what a "
                "trivial answer scores. Success is a number, not an adjective, so 'good enough' becomes 0.9. The "
                "template also keeps a written record that survives the week, and its keys drive the later report "
                "and tests, so the spec is executable rather than decorative. Keep the keys ordered so two specs "
                "compare with a plain equality check. Today you build the validator, fill it for the toy capstone, "
                "and confirm that an incomplete call is rejected with a message naming the missing section."
            ),
            code=(
                'TEMPLATE = ("task", "inputs", "outputs", "metric", "baseline", "success")\n'
                '\n'
                'def make_spec(**sections):\n'
                '    missing = [k for k in TEMPLATE if k not in sections]\n'
                '    if missing:\n'
                '        raise ValueError("missing sections: " + ", ".join(missing))\n'
                '    return {k: sections[k] for k in TEMPLATE}\n'
                '\n'
                'spec = make_spec(\n'
                '    task="classify 4x4 shapes",\n'
                '    inputs="4x4 grid of 0/255",\n'
                '    outputs="h, v, d or x",\n'
                '    metric="accuracy",\n'
                '    baseline="majority class",\n'
                '    success=0.9,\n'
                ')\n'
                'print("sections:", len(spec))\n'
                'print("metric:", spec["metric"], "baseline:", spec["baseline"])\n'
                'try:\n'
                '    make_spec(task="incomplete")\n'
                'except ValueError as err:\n'
                '    print("rejected:", err)\n'
                '\n'
                'assert tuple(spec) == TEMPLATE\n'
                'print("a spec names every section before any code")\n'
            ),
            variant_b="remove the baseline key from a spec and show the validator refusing it",
            variant_c="add a notes key outside the template and have make_spec drop unknown keys",
            mistakes=[
                "Letting sections be optional, so a spec can be built without a metric.",
                "Storing success as a word like 'good' instead of a number to compare against.",
                "Omitting the baseline, so accuracy is read as an absolute rather than a gain.",
            ],
            q1=(
                "Why should a missing spec section raise at construction time?",
                "Because a spec built without a metric or baseline is invalid immediately, and failing at build time localises the mistake to one call.",
            ),
            homework=(
                "Write `make_spec(**sections)` that raises when a required section is missing and returns an "
                "ordered spec otherwise. Build one complete spec, trigger one ValueError, print the error message, "
                "and comment which line enforces completeness."
            ),
            patterns=["def ", "make_spec", "ValueError"],
            mapping=(
                "Model cards and evaluation plans are the same guardrail: required sections, one metric, one "
                "baseline, checked before training starts."
            ),
        ),
        167: dict(
            topic="Define the data contract",
            idea=(
                "A data contract is the boundary where bugs are cheapest to catch, and today's technique is a "
                "`check_sample` function that asserts the shape of one sample before it enters the pipeline. The "
                "contract for this capstone has four clauses: the label is one of the known classes, the grid is "
                "exactly four rows of four values, every value is either 0 or 255, and the image is not empty. Each "
                "clause is an `assert` with a message, so a violation names the broken rule. Checking at the "
                "boundary means every function downstream can assume a valid grid, which removes defensive checks "
                "from the classifier and keeps it short. The contract also documents the data for a reader: shape, "
                "range and label set in one place. Two decisions are worth making explicit. Ragged rows must be "
                "rejected, because a row of three values silently shifts every column feature. And an "
                "all-background image must be rejected, because no shape is present to classify and the honest "
                "answer is not a label. Notice the contract is about structure, not semantics: it cannot know a "
                "grid is mislabelled, only that it is well formed. Today you write the checker, feed it one valid "
                "and one ragged sample, and watch the assertion message identify the fault."
            ),
            code=(
                'LABELS = ("h", "v", "d", "x")\n'
                'H = W = 4\n'
                '\n'
                'def check_sample(sample):\n'
                '    label, grid = sample\n'
                '    assert label in LABELS, "unknown label"\n'
                '    assert len(grid) == H, "wrong height"\n'
                '    assert all(len(row) == W for row in grid), "ragged row"\n'
                '    assert all(v in (0, 255) for row in grid for v in row), "values must be 0 or 255"\n'
                '    assert any(v for row in grid for v in row), "empty image"\n'
                '    return True\n'
                '\n'
                'good = ("h", [[255, 255, 255, 255], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]])\n'
                'print("valid:", check_sample(good))\n'
                '\n'
                'bad = ("h", [[255, 255, 255, 255], [0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]])\n'
                'try:\n'
                '    check_sample(bad)\n'
                'except AssertionError as err:\n'
                '    print("rejected:", err)\n'
                '\n'
                'assert check_sample(good)\n'
                'print("the contract is asserted once, at the boundary")\n'
            ),
            variant_b="add a clause rejecting grids with more than twelve foreground pixels as too dense",
            variant_c="check two samples in a loop and print which clause fails for the malformed one",
            mistakes=[
                "Validating inside the classifier instead of once when a sample is loaded.",
                "Allowing ragged rows so column features silently read the wrong cell.",
                "Accepting an all-background image and forcing the classifier to guess a shape.",
            ],
            q1=(
                "What does the data contract guarantee to the rest of the pipeline?",
                "That every grid downstream is well formed — correct shape, valid values, non-empty — so later stages can skip defensive checks.",
            ),
            homework=(
                "Write `check_sample(sample)` asserting label membership, grid shape, allowed values and a "
                "non-empty image. Run it on one valid and one ragged sample, print the assertion message, and "
                "comment which clause detects the ragged row."
            ),
            patterns=["def ", "check_sample", "assert "],
            mapping=(
                "Schema checks with pydantic or tf.data validation are data contracts at scale; catching a bad "
                "shape at ingest is far cheaper than debugging it inside a model."
            ),
        ),
        168: dict(
            topic="Load images as arrays",
            idea=(
                "Features only exist after text becomes arrays, and today's technique is a small loader that turns "
                "a labelled block of text into a label and a grid of integers. The format is deliberately boring: "
                "the first line is the label, and each following line is one row of whitespace-separated pixel "
                "values. Parsing is three stdlib moves — strip, then splitlines, then split — followed by `int` on "
                "each token. Two details separate a loader that survives from one that does not. Blank lines must "
                "be handled, because hand-written samples accumulate them; stripping the whole block before "
                "splitting removes leading and trailing blanks. And the loader should not silently accept a ragged "
                "grid: build the rows, then a quick shape check confirms all rows have equal length, since a typo "
                "in one row is the most common data bug. Keeping the loader separate from preprocessing matters "
                "because the loader is where file formats and encodings live, while preprocessing is where pixels "
                "are transformed; mixing them makes both hard to test. In a real project this function would read "
                "PNG files with a decoder, but the interface — source in, label and numeric grid out — is "
                "identical. Today you write `load`, run it on a literal sample, print the shape and rows, and "
                "assert the total pixel count."
            ),
            code=(
                'def load(text):\n'
                '    label, *rows = text.strip().splitlines()\n'
                '    grid = [[int(v) for v in row.split()] for row in rows]\n'
                '    widths = {len(row) for row in grid}\n'
                '    assert len(widths) == 1, "ragged grid"\n'
                '    return label.strip(), grid\n'
                '\n'
                'RAW = """\n'
                'h\n'
                '255 255 255 255\n'
                '0 0 0 0\n'
                '0 0 0 0\n'
                '0 0 0 0\n'
                '"""\n'
                '\n'
                'label, grid = load(RAW)\n'
                'print("label:", label)\n'
                'print("shape:", len(grid), "x", len(grid[0]))\n'
                'for row in grid:\n'
                '    print(row)\n'
                '\n'
                'assert len(grid) == 4 and len(grid[0]) == 4\n'
                'assert sum(sum(row) for row in grid) == 4 * 255\n'
                'print("text becomes a labelled grid")\n'
            ),
            variant_b="load two samples separated by a blank line and return a list of labelled grids",
            variant_c="feed a ragged block and print the assertion that rejects it",
            mistakes=[
                "Forgetting to strip the block, so a leading blank line is parsed as the label.",
                "Parsing pixel values as strings, which makes every later sum concatenate text.",
                "Assuming all rows are equal length instead of checking the grid is rectangular.",
            ],
            q1=(
                "Why keep loading separate from preprocessing?",
                "The loader owns formats and parsing, preprocessing owns pixel transforms; separating them means each can be tested and replaced alone.",
            ),
            homework=(
                "Write `load_grid(text)` returning a label and a rectangular grid of ints, rejecting ragged "
                "rows. Run it on a literal four-row sample, print the label, shape and rows, and comment which "
                "line guarantees the grid is rectangular."
            ),
            patterns=["def ", "load_grid", "splitlines"],
            mapping=(
                "This is the ingest stage of any vision service: `cv2.imread` or a PIL decode returns an array, "
                "and the label-plus-array interface is what the rest of the pipeline consumes."
            ),
        ),
        169: dict(
            topic="Build preprocessing",
            idea=(
                "Preprocessing is the stage that makes the classifier's assumptions true, and today's technique is "
                "a `to_binary` function that maps a raw 0-255 grid onto zeros and ones using a threshold. The "
                "classifier counts foreground pixels per row and column, so it needs a grid where every value is "
                "either zero or one; without this step the counts are in units of 255 and every comparison is off "
                "by two orders of magnitude. The function is a comprehension with one comparison, and making the "
                "threshold a parameter rather than a constant is what lets it adapt when the data gets noisier. A "
                "second, smaller helper, `foreground`, sums the whole grid and gives the cheapest possible sanity "
                "check: a useful image has some but not all pixels set, so an all-zero or all-one result flags a "
                "broken threshold before any model sees it. The rule to internalise is that preprocessing must be a "
                "named, separately callable function, not lines buried in the pipeline, because it is the stage "
                "most likely to need replacing and the stage whose output you print when debugging. Keep "
                "transformations deterministic and free of hidden state so the same input always yields the same "
                "grid. Today you binarise a small mixed grid, print the result, and assert both the first row and "
                "the total foreground count."
            ),
            code=(
                'def to_binary(grid, value=128):\n'
                '    return [[1 if px >= value else 0 for px in row] for row in grid]\n'
                '\n'
                'def foreground(binary):\n'
                '    return sum(sum(row) for row in binary)\n'
                '\n'
                'gray = [\n'
                '    [255, 0, 0, 255],\n'
                '    [0, 255, 255, 0],\n'
                '    [0, 0, 0, 0],\n'
                '    [0, 0, 0, 0],\n'
                ']\n'
                'binary = to_binary(gray)\n'
                'for row in binary:\n'
                '    print(row)\n'
                'print("foreground:", foreground(binary))\n'
                '\n'
                'assert binary[0] == [1, 0, 0, 1]\n'
                'assert foreground(binary) == 4\n'
                'print("preprocessing is a named, testable step")\n'
            ),
            variant_b="raise the threshold to 200 and explain why fewer pixels survive as foreground",
            variant_c="add a `normalise` step dividing by 255 so the grid holds floats in 0..1",
            mistakes=[
                "Skipping binarisation and counting raw 0-255 values, so every row sum looks large.",
                "Hard-coding the threshold so the step cannot adapt to a noisier image.",
                "Burying the transform inside the pipeline instead of a named function that can be tested alone.",
            ],
            q1=(
                "Why does the classifier need a binary grid rather than the raw one?",
                "Because it counts foreground pixels per row and column, and those counts are only meaningful when each pixel contributes exactly one, not 255.",
            ),
            homework=(
                "Write `preprocess_grid(grid, value=128)` returning a 0/1 grid, plus `foreground(binary)`. Run "
                "both on a 4x4 mixed sample, print the binary rows and count, and comment which line performs the "
                "thresholding."
            ),
            patterns=["def ", "preprocess_grid", "print("],
            mapping=(
                "Resize, normalise and threshold steps are the standard preprocessing block in every vision "
                "pipeline; keeping them named and deterministic is what makes a model reproducible."
            ),
        ),
        170: dict(
            topic="Build the classifier or detector",
            idea=(
                "With clean binary grids, today's technique is a hand-written classifier built from interpretable "
                "features: per-row sums, per-column sums, and the two diagonal sums. These features are enough to "
                "separate four shapes on a 4x4 grid. A horizontal bar makes one row sum to four; a vertical bar "
                "makes one column sum to four; a main diagonal makes the main diagonal sum to four; and a cross "
                "makes both diagonals sum to four. The classifier is therefore an ordered decision list, testing "
                "the most specific case first — both diagonals, then main diagonal, then a full row, then a full "
                "column — and returning `unknown` when none match. Order matters: checking a full row before the "
                "diagonals would label a cross as a bar when one of its forms has a full row. This rule-based "
                "approach has real advantages for a small fixed task: no training data, no parameters, and every "
                "decision can be explained in one sentence. Its weakness is exactly that the thresholds are "
                "hand-chosen, so it does not transfer to rotated or noisy shapes. That trade-off is the honest "
                "lesson — features plus a rule get a working baseline cheaply, and everything later is about "
                "replacing the rule with something learned. Today you write the feature extractors and the ordered "
                "`classify` function, then check all four shapes."
            ),
            code=(
                'def row_sums(grid):\n'
                '    return [sum(row) for row in grid]\n'
                '\n'
                'def col_sums(grid):\n'
                '    return [sum(row[c] for row in grid) for c in range(len(grid[0]))]\n'
                '\n'
                'def diag_sums(grid):\n'
                '    n = len(grid)\n'
                '    main = sum(grid[i][i] for i in range(n))\n'
                '    anti = sum(grid[i][n - 1 - i] for i in range(n))\n'
                '    return main, anti\n'
                '\n'
                'def classify(grid):\n'
                '    main, anti = diag_sums(grid)\n'
                '    if main == 4 and anti == 4:\n'
                '        return "x"\n'
                '    if main == 4:\n'
                '        return "d"\n'
                '    if max(row_sums(grid)) == 4:\n'
                '        return "h"\n'
                '    if max(col_sums(grid)) == 4:\n'
                '        return "v"\n'
                '    return "unknown"\n'
                '\n'
                'samples = {\n'
                '    "h": [[1, 1, 1, 1], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]],\n'
                '    "v": [[1, 0, 0, 0], [1, 0, 0, 0], [1, 0, 0, 0], [1, 0, 0, 0]],\n'
                '    "d": [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]],\n'
                '    "x": [[1, 0, 0, 1], [0, 1, 1, 0], [0, 1, 1, 0], [1, 0, 0, 1]],\n'
                '}\n'
                'for label, grid in samples.items():\n'
                '    print(label, "->", classify(grid))\n'
                '\n'
                'assert classify(samples["x"]) == "x"\n'
                'assert classify(samples["h"]) == "h"\n'
                'print("features plus an ordered rule beat a lookup table")\n'
            ),
            variant_b="test a described but unsupported shape and confirm classify returns 'unknown'",
            variant_c="move the full-row test before the diagonal test and show the cross is now mislabelled",
            mistakes=[
                "Testing the general case before the specific one, so a cross is read as a bar.",
                "Using raw 0-255 values, so no sum ever equals four and every label is 'unknown'.",
                "Returning a guess instead of 'unknown' when no feature matches a known shape.",
            ],
            q1=(
                "Why must the diagonal cases be tested before the full-row case?",
                "Because a cross satisfies the full-row test too, so the specific two-diagonal test must fire first or the cross is mislabelled as a bar.",
            ),
            homework=(
                "Write `classify_grid(grid)` using row sums, column sums and diagonal sums as an ordered "
                "decision list, returning 'unknown' when nothing matches. Run it on all four shape grids, print "
                "each label, and comment which test must come first and why."
            ),
            patterns=["def ", "classify_grid", "unknown"],
            mapping=(
                "Feature plus rule classifiers were the standard before learned models; they remain the sane "
                "baseline against which any detector or CNN must show a real gain."
            ),
        ),
        171: dict(
            topic="Evaluate properly",
            idea=(
                "Evaluation is where a model stops being a demo, and today's technique is a confusion matrix built "
                "as a nested dictionary of true label by predicted label. The matrix is the raw material for every "
                "metric: accuracy is the trace divided by the total, per-class recall is the diagonal cell over "
                "that row's sum, and precision is the diagonal over that column's sum. Building the counts first "
                "and deriving metrics from them is the discipline, because accuracy alone hides which class fails; "
                "a classifier that ignores one rare class can still look good overall. Two habits make the numbers "
                "trustworthy. First, always report the baseline — here the majority class — beside the accuracy, "
                "so a score is read as a gain rather than an absolute. Second, compute recall per class and print "
                "it, because the matrix already contains it and a single aggregate number throws away the most "
                "diagnostic information. Keep the evaluation code separate from the classifier so it can be "
                "pointed at any prediction list, and never tune on the test set: the samples used to choose a "
                "threshold are not the samples used to report a score. Today you write `confusion` and `accuracy`, "
                "run them on a small prediction list, print recall per class, and assert the counts for one known "
                "misclassification."
            ),
            code=(
                'LABELS = ("d", "h", "v", "x")\n'
                '\n'
                'def confusion(preds, truths):\n'
                '    counts = {t: {p: 0 for p in LABELS} for t in LABELS}\n'
                '    for truth, pred in zip(truths, preds):\n'
                '        counts[truth][pred] += 1\n'
                '    return counts\n'
                '\n'
                'def accuracy(preds, truths):\n'
                '    return sum(p == t for p, t in zip(preds, truths)) / len(truths)\n'
                '\n'
                'def recall(counts, label):\n'
                '    total = sum(counts[label].values())\n'
                '    return counts[label][label] / total if total else 0.0\n'
                '\n'
                'truths = ["h", "v", "d", "x", "h", "v"]\n'
                'preds = ["h", "v", "d", "h", "h", "v"]\n'
                'counts = confusion(preds, truths)\n'
                'for label in LABELS:\n'
                '    print(label, "recall", round(recall(counts, label), 2))\n'
                'print("accuracy:", round(accuracy(preds, truths), 2))\n'
                '\n'
                'assert round(accuracy(preds, truths), 2) == 0.83\n'
                'assert counts["x"]["h"] == 1\n'
                'print("metrics are computed, not eyeballed")\n'
            ),
            variant_b="add precision per class and print it beside recall to show the asymmetry",
            variant_c="append a majority-class baseline prediction list and compare its accuracy",
            mistakes=[
                "Reporting accuracy alone, which hides a class the classifier never gets right.",
                "Tuning the threshold on the same samples used to report the score.",
                "Quoting a metric without the size of the set it was measured on.",
            ],
            q1=(
                "Why build the confusion matrix before computing accuracy?",
                "Every metric is derived from the counts, and the matrix shows which class fails, which a single accuracy number hides.",
            ),
            homework=(
                "Write `confusion_matrix(preds, truths)` returning counts, plus `accuracy` and `recall`. Run "
                "them on a small prediction list with one error, print recall per class and accuracy, and comment "
                "which cell records the misclassification."
            ),
            patterns=["def ", "confusion_matrix", "accuracy"],
            mapping=(
                "scikit-learn's `confusion_matrix` and `classification_report` produce exactly these counts and "
                "per-class metrics; the derivation is unchanged at any scale."
            ),
        ),
        172: dict(
            topic="Write the tests",
            idea=(
                "Tests are the difference between code you believe and code you have checked, and today's "
                "technique is a single assert-based test function with no framework. The function holds a table of "
                "cases, each a pair of an expected label and a grid designed to produce it, and loops over them "
                "asserting the classifier's answer matches. When a case fails, the assertion message names the "
                "expected and actual labels, which is enough to find the bug without a debugger. The design "
                "choices matter more than the asserts. Build one case per class, so a class the classifier never "
                "gets right is caught rather than hidden behind the classes that dominate. Keep the grids literal "
                "and tiny, so a reader can verify by eye that the expected label is correct. Use the returned "
                "count of cases as evidence the test actually ran, since a test that silently skips is worse than "
                "no test. And test the edges deliberately: an empty grid, a full grid and a random pattern should "
                "all return `unknown`, because 'no shape present' is a legitimate and important answer. This "
                "mirrors exactly what a pytest file would do, minus the runner. Today you write `test_classify`, "
                "run it over the four shapes plus an ambiguous case, print how many cases passed, and see the "
                "message a deliberate failure produces."
            ),
            code=(
                'def classify(grid):\n'
                '    rows = [sum(r) for r in grid]\n'
                '    cols = [sum(r[c] for r in grid) for c in range(4)]\n'
                '    main = sum(grid[i][i] for i in range(4))\n'
                '    anti = sum(grid[i][3 - i] for i in range(4))\n'
                '    if main == 4 and anti == 4:\n'
                '        return "x"\n'
                '    if main == 4:\n'
                '        return "d"\n'
                '    if max(rows) == 4:\n'
                '        return "h"\n'
                '    if max(cols) == 4:\n'
                '        return "v"\n'
                '    return "unknown"\n'
                '\n'
                'def test_classify():\n'
                '    cases = [\n'
                '        ("h", [[1, 1, 1, 1]] + [[0] * 4] * 3),\n'
                '        ("v", [[1, 0, 0, 0]] * 4),\n'
                '        ("d", [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]),\n'
                '        ("x", [[1, 0, 0, 1], [0, 1, 1, 0], [0, 1, 1, 0], [1, 0, 0, 1]]),\n'
                '        ("unknown", [[0] * 4] * 4),\n'
                '    ]\n'
                '    for expected, grid in cases:\n'
                '        got = classify(grid)\n'
                '        assert got == expected, expected + " misread as " + got\n'
                '    return len(cases)\n'
                '\n'
                'print("cases passed:", test_classify())\n'
                'assert test_classify() == 5\n'
                'print("each shape gets its own asserted case")\n'
            ),
            variant_b="add a grid with two full rows and show the test failing on the ambiguous case",
            variant_c="check a full all-ones grid and decide whether 'unknown' is the right expected label",
            mistakes=[
                "Testing only the shapes the classifier already gets right.",
                "Using hidden or generated grids, so a failure cannot be reproduced by eye.",
                "Letting a failing assert pass silently instead of naming expected and actual labels.",
            ],
            q1=(
                "Why include a case that expects 'unknown'?",
                "Because refusing to label an ambiguous input is a real behaviour, and a test locks it in just like the four shape cases.",
            ),
            homework=(
                "Write `test_classifier()` holding a table of expected-label and grid pairs, looping and "
                "asserting the classifier's answer. Include one 'unknown' case, print the number of cases that "
                "passed, and comment which line makes a failure name both labels."
            ),
            patterns=["def ", "test_classifier", "assert "],
            mapping=(
                "This is the assertion set a pytest file would hold; testing each class plus the no-match case is "
                "standard practice for any classifier before it is trusted."
            ),
        ),
        173: dict(
            topic="Analyse the errors",
            idea=(
                "A model improves fastest when you read its mistakes, and today's technique is an error analysis "
                "that pairs each wrong prediction with the feature vector that caused it. The procedure is "
                "mechanical: run every sample, collect the ones where the predicted label differs from the true "
                "label, and for each print the true label, the predicted label, and the extracted features. "
                "Printing features next to the failure is what turns a list of errors into a diagnosis — you can "
                "see whether the diagonal sum was missed, whether a full row was absent, or whether two shapes "
                "genuinely share a feature signature. Two patterns recur. Some errors are feature collisions, where "
                "two different shapes produce the same values and no rule can separate them; the fix is a richer "
                "feature, not a threshold tweak. Others are data faults, where the sample itself was malformed, "
                "which is why the data contract runs first. Counting errors per class also reveals imbalance: a "
                "class with many errors may simply have fewer confident examples. The output of this step is a "
                "ranked list of causes, each with a proposed change, not a single blame-worthy number. That list is "
                "what the next day's work acts on. Today you write `error_report`, run it on a set containing one "
                "deliberately broken cross, print the offending feature vector, and assert exactly one error was "
                "found."
            ),
            code=(
                'def classify(grid):\n'
                '    main = sum(grid[i][i] for i in range(4))\n'
                '    anti = sum(grid[i][3 - i] for i in range(4))\n'
                '    if main == 4 and anti == 4:\n'
                '        return "x"\n'
                '    if main == 4:\n'
                '        return "d"\n'
                '    if max(sum(r) for r in grid) == 4:\n'
                '        return "h"\n'
                '    if max(sum(r[c] for r in grid) for c in range(4)) == 4:\n'
                '        return "v"\n'
                '    return "unknown"\n'
                '\n'
                'def features(grid):\n'
                '    main = sum(grid[i][i] for i in range(4))\n'
                '    anti = sum(grid[i][3 - i] for i in range(4))\n'
                '    return {"main": main, "anti": anti,\n'
                '            "row": max(sum(r) for r in grid),\n'
                '            "col": max(sum(r[c] for r in grid) for c in range(4))}\n'
                '\n'
                'data = [\n'
                '    ("h", [[1, 1, 1, 1], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]),\n'
                '    ("d", [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]),\n'
                '    ("x", [[1, 0, 0, 1], [0, 1, 1, 0], [1, 0, 0, 1], [0, 1, 1, 0]]),\n'
                ']\n'
                'errors = [(t, classify(g), g) for t, g in data if classify(g) != t]\n'
                'print("error count:", len(errors))\n'
                'for truth, pred, grid in errors:\n'
                '    print("true", truth, "pred", pred, "features", features(grid))\n'
                '\n'
                'assert len(errors) == 1\n'
                'assert errors[0][1] == "unknown"\n'
                'print("inspect the feature vector, not just the label")\n'
            ),
            variant_b="add a second broken diagonal and check both are reported as errors",
            variant_c="group errors by class and print the count per class to spot an imbalanced failure",
            mistakes=[
                "Reporting only an accuracy number and never looking at which samples failed.",
                "Fixing a feature collision by tweaking a threshold instead of adding a feature.",
                "Ignoring malformed samples that the data contract should have rejected earlier.",
            ],
            q1=(
                "Why print the feature vector alongside each wrong prediction?",
                "Because the features show why the rule fired, turning a bare error list into a diagnosis of a collision or a data fault.",
            ),
            homework=(
                "Write `error_report(data, classify)` returning the samples whose prediction differs from the "
                "true label, each with its feature dict. Run it on a set with one broken shape, print the features "
                "of the error, and comment what the feature values reveal about the cause."
            ),
            patterns=["def ", "error_report", "print("],
            mapping=(
                "Error analysis by slicing the failures is core practice in applied ML; the same 'pair each "
                "mistake with its inputs' habit drives every dataset and model improvement."
            ),
        ),
        174: dict(
            topic="Optimise the speed",
            idea=(
                "Speed work starts with a measurement, and today's technique is to count the operations a "
                "classifier performs rather than to time it with a stopwatch, which is noisy and machine-dependent. "
                "Counting is deterministic and portable: you estimate the number of additions and comparisons each "
                "approach needs and compare the totals. Comparing a query grid against stored prototype grids "
                "costs one comparison per pixel per class, so sixteen times the number of classes. The feature "
                "approach pays a fixed cost once — summing rows, summing columns and reading the diagonal — then "
                "compares only a handful of feature values per class. The interesting result is the crossover: with "
                "one class the feature extractor is more expensive, because it does work the pixel comparison does "
                "not, but as classes grow the comparison cost dominates and features win. That is the argument for "
                "features on any real problem with many classes, and it is an argument you can make with arithmetic "
                "instead of a benchmark. The habit to keep is stating the unit of measurement and the workload when "
                "claiming a speed-up, since 'faster' without those is meaningless. Today you write `naive_ops` and "
                "`feature_ops`, print both for one, four and sixteen classes, and assert the crossover exists."
            ),
            code=(
                'def naive_ops(classes):\n'
                '    return classes * 16\n'
                '\n'
                'def feature_ops(classes):\n'
                '    extract = 4 * 4 + 4 * 4 + 4\n'
                '    return extract + classes * 3\n'
                '\n'
                'for classes in (1, 4, 16):\n'
                '    print(classes, "classes -> naive", naive_ops(classes),\n'
                '          "features", feature_ops(classes))\n'
                '\n'
                'assert feature_ops(1) > naive_ops(1)\n'
                'assert feature_ops(16) < naive_ops(16)\n'
                'print("features win once there are several classes")\n'
            ),
            variant_b="count operations for an 8x8 grid instead of 4x4 and show the crossover moves",
            variant_c="add a cache that reuses extracted features and recount the operations for a whole batch",
            mistakes=[
                "Timing with a stopwatch and reporting a number that changes on every machine.",
                "Claiming 'faster' without stating the workload and the unit being counted.",
                "Optimising before a measurement shows the comparison loop is actually the cost.",
            ],
            q1=(
                "Why count operations instead of timing the code?",
                "Operation counts are deterministic and portable, so they compare algorithms rather than the machine and background load at the moment of timing.",
            ),
            homework=(
                "Write `count_ops(classes, grid_size)` returning the operation counts for a naive pixel compare "
                "and a feature approach. Print both for one, four and sixteen classes, assert the crossover, and "
                "comment which cost dominates as classes grow."
            ),
            patterns=["def ", "count_ops", "print("],
            mapping=(
                "Complexity analysis and FLOP counting are how real teams choose between pixel comparison and "
                "feature or embedding comparison before spending on hardware."
            ),
        ),
        175: dict(
            topic="Package the pipeline",
            idea=(
                "A pipeline is only reusable when it has one entry point, and today's technique is packaging the "
                "stages behind a single `pipeline` function that takes raw text and returns a structured result. "
                "The stages already exist as separate functions — `load`, `preprocess`, `classify` — and the "
                "packaging adds nothing but a contract: it calls them in order and returns a dictionary with the "
                "true label, the shape and the predicted label. Returning a dict rather than printing inside the "
                "function is the key decision, because it makes the pipeline callable from a test, a report or a "
                "loop, and it keeps side effects at the edge of the program. Naming the stage tuple as a constant "
                "documents the order in one place, so inserting a normalisation step later is a visible edit "
                "rather than a hidden one. The wrapper should be thin: if it contains real logic, that logic "
                "belongs in a stage where it can be tested alone. Error handling belongs at this boundary too — a "
                "load failure or a malformed sample is caught here and reported with context, not swallowed deep "
                "inside a feature calculation. This is the shape every production vision service exposes: one "
                "function, typed input, structured output, stages hidden but individually replaceable. Today you "
                "write `pipeline`, run it on one sample, print the result dictionary, and assert the predicted "
                "label and shape."
            ),
            code=(
                'STAGES = ("load", "preprocess", "classify")\n'
                '\n'
                'def load(text):\n'
                '    label, *rows = text.strip().splitlines()\n'
                '    return label.strip(), [[int(v) for v in row.split()] for row in rows]\n'
                '\n'
                'def preprocess(grid):\n'
                '    return [[1 if px >= 128 else 0 for px in row] for row in grid]\n'
                '\n'
                'def classify(grid):\n'
                '    main = sum(grid[i][i] for i in range(4))\n'
                '    anti = sum(grid[i][3 - i] for i in range(4))\n'
                '    if main == 4 and anti == 4:\n'
                '        return "x"\n'
                '    if main == 4:\n'
                '        return "d"\n'
                '    if max(sum(r) for r in grid) == 4:\n'
                '        return "h"\n'
                '    if max(sum(r[c] for r in grid) for c in range(4)) == 4:\n'
                '        return "v"\n'
                '    return "unknown"\n'
                '\n'
                'def pipeline(text):\n'
                '    label, grid = load(text)\n'
                '    binary = preprocess(grid)\n'
                '    return {"label": label, "shape": (len(binary), len(binary[0])),\n'
                '            "predicted": classify(binary)}\n'
                '\n'
                'RAW = "h\\n255 255 255 255\\n0 0 0 0\\n0 0 0 0\\n0 0 0 0"\n'
                'result = pipeline(RAW)\n'
                'print(result)\n'
                'print("stages:", " -> ".join(STAGES))\n'
                '\n'
                'assert result["predicted"] == "h"\n'
                'assert result["shape"] == (4, 4)\n'
                'print("one function hides the stages, not the seams")\n'
            ),
            variant_b="return the probability-free feature dict alongside the label for richer callers",
            variant_c="wrap the load call in try/except and return an error field instead of raising",
            mistakes=[
                "Printing inside the pipeline, so it cannot be called from a test or a loop.",
                "Putting real logic in the wrapper instead of a stage that can be tested alone.",
                "Losing the true label, so the caller cannot score the result it just received.",
            ],
            q1=(
                "Why return a dictionary instead of printing the prediction?",
                "A returned value can be tested, scored and reused by any caller, while printed output can only be read by a human.",
            ),
            homework=(
                "Write `run_pipeline(text)` that loads, preprocesses and classifies, returning a dict with "
                "label, shape and predicted fields. Run it on one literal sample, print the dict, and comment "
                "which line makes the stages composable."
            ),
            patterns=["def ", "run_pipeline", "return"],
            mapping=(
                "Inference services expose exactly this: one predict function, structured input and output, "
                "stages composed underneath and individually replaceable."
            ),
        ),
        176: dict(
            topic="Present the results",
            idea=(
                "Communicating results is part of the work, and today's technique is turning a metrics dictionary "
                "into a formatted report with `str` formatting rather than screenshotting a notebook. The function "
                "takes a dictionary and renders aligned key-value lines, sorting the keys so two runs produce "
                "identical text that a diff can check. Alignment comes from format specifiers, which is stdlib and "
                "adds no dependency. Two content rules make the report useful to someone who was not in the room: "
                "always show the baseline next to the accuracy, and always state the sample count, because a metric "
                "without the size of the set it was measured on cannot be judged. The report is generated from the "
                "same dict the tests use, so the numbers presented are the numbers verified, with no manual "
                "transcription step where a figure can drift. Keeping the renderer separate from the computation "
                "also means the report can be regenerated for any metric set, including a comparison against the "
                "baseline model. When this becomes a slide, the dict is the source and the formatting is "
                "disposable. Today you write `report`, print it for a four-key metrics dictionary, and assert that "
                "the output contains the metric name and has the expected number of lines."
            ),
            code=(
                'def report(metrics):\n'
                '    lines = ["Capstone report", "-" * 16]\n'
                '    for key in sorted(metrics):\n'
                '        lines.append(str(key).rjust(10) + ": " + str(metrics[key]))\n'
                '    return "\\n".join(lines)\n'
                '\n'
                'metrics = {"accuracy": 0.9, "baseline": 0.25, "classes": 4, "samples": 20}\n'
                'text = report(metrics)\n'
                'print(text)\n'
                '\n'
                'assert "accuracy" in text\n'
                'assert text.count("\\n") == 5\n'
                'print("a report is a formatted dict, not a screenshot")\n'
            ),
            variant_b="add a title argument and place it in the header line of the report",
            variant_c="render the metrics as percentages and show the accuracy line changing format",
            mistakes=[
                "Screenshotting a notebook cell so the numbers cannot be reproduced or diffed.",
                "Reporting accuracy without the baseline, so a gain is impossible to judge.",
                "Hand-copying numbers into the report, which lets a figure drift from the verified value.",
            ],
            q1=(
                "Why sort the keys when rendering the report?",
                "So two runs of the same metrics produce identical, diffable text and a hand-fed figure cannot quietly differ from the computed one.",
            ),
            homework=(
                "Write `format_report(metrics)` returning aligned key-value lines sorted by key. Run it on a "
                "metrics dict containing accuracy and baseline, print the report, and comment which line keeps "
                "the output stable between runs."
            ),
            patterns=["def ", "format_report", "join("],
            mapping=(
                "Experiment trackers and model cards render the same structured metrics; a report generated from "
                "the verified dict is the reproducible-documentation version of a slide."
            ),
        ),
        177: dict(
            topic="Build day: reproducibility pass",
            idea=(
                "Reproducibility is a property you can test, and today's technique is a determinism pass that runs "
                "the feature extractor and classifier twice and asserts the two results are identical. For code "
                "with no randomness this sounds trivial, but the assertion catches a class of real bugs: iteration "
                "over an unordered set, reliance on a clock or a hash seed, and dictionaries whose insertion order "
                "changed between runs. The fix is to sort wherever order is arbitrary and to never depend on `id` "
                "or `hash` for logic. In this capstone determinism is built in — pure functions, literal data, no "
                "I/O — and the pass documents that guarantee so a later edit that introduces a cache or a random "
                "sampling is caught immediately. The technique generalises: in a real pipeline you pin the random "
                "seed, sort file listings before batching, and record library versions, so a result can be "
                "reproduced on another machine. Storing the inputs alongside the outputs, even as literals, is the "
                "cheapest form of a reproducible experiment. The check itself is a few lines and worth keeping as a "
                "test. Today you write `features` and `classify` as pure functions, compute the result twice, print "
                "both, and assert they are equal and that the known cross is labelled `x`."
            ),
            code=(
                'GRID = [[1, 0, 0, 1], [0, 1, 1, 0], [0, 1, 1, 0], [1, 0, 0, 1]]\n'
                '\n'
                'def features(grid):\n'
                '    n = len(grid)\n'
                '    rows = tuple(sum(r) for r in grid)\n'
                '    cols = tuple(sum(r[c] for r in grid) for c in range(n))\n'
                '    main = sum(grid[i][i] for i in range(n))\n'
                '    anti = sum(grid[i][n - 1 - i] for i in range(n))\n'
                '    return rows + cols + (main, anti)\n'
                '\n'
                'def classify(grid):\n'
                '    f = features(grid)\n'
                '    if f[8] == 4 and f[9] == 4:\n'
                '        return "x"\n'
                '    if f[8] == 4:\n'
                '        return "d"\n'
                '    if max(f[:4]) == 4:\n'
                '        return "h"\n'
                '    return "v"\n'
                '\n'
                'first = (features(GRID), classify(GRID))\n'
                'second = (features(GRID), classify(GRID))\n'
                'print("run 1:", first)\n'
                'print("run 2:", second)\n'
                '\n'
                'assert first == second\n'
                'assert classify(GRID) == "x"\n'
                'print("no randomness, no clock, same answer twice")\n'
            ),
            variant_b="sort a set of labels inside a feature function and note why unsorted iteration breaks determinism",
            variant_c="run the pass over two different grids and confirm the outputs stay independent",
            mistakes=[
                "Iterating a set where order matters, so the result changes between runs.",
                "Depending on a hash or timestamp, which varies across machines and sessions.",
                "Assuming determinism without asserting it, so a later cache edit silently breaks it.",
            ],
            q1=(
                "What does running the pipeline twice and comparing outputs catch?",
                "Non-determinism from unordered iteration, clock or hash dependence, or hidden state, which would make results irreproducible on another machine.",
            ),
            homework=(
                "Write `reproducibility_check(grid)` that computes features and classifies twice, returns whether "
                "the two results match. Run it on a known cross grid, print both runs, and comment which "
                "guarantee makes the equality hold."
            ),
            patterns=["def ", "reproducibility_check", "assert "],
            mapping=(
                "Pinning seeds and recording versions is how real experiments stay reproducible; the two-run "
                "equality check is the smallest test that guards that property."
            ),
        ),
        178: dict(
            topic="Build day: final review",
            idea=(
                "The final review is not a reread, it is a checklist executed as code, and today's technique is a "
                "`review` function that runs the pipeline's invariants against a sample and returns a dictionary "
                "of pass or fail. The checks cover the concerns built across the week: the preprocessed grid keeps "
                "the required shape, every value is binary, the classifier returns a real label rather than "
                "`unknown`, and the sample is non-empty. Expressing the review as a function means it can be "
                "pointed at fresh samples instead of one hand-checked example, which is how a review catches "
                "regressions the author has stopped seeing. Each check is a small boolean, and the whole dictionary "
                "is asserted to be uniformly true, so a single false value fails loudly and names the broken "
                "concern. A useful review distinguishes blocking failures from warnings — a wrong shape is fatal, "
                "while a tiny foreground count might merely be suspicious — but the first version can treat "
                "everything as blocking and relax later. Keeping the review separate from the tests means the "
                "tests check the classifier on designed cases while the review checks that a real sample travels "
                "the pipeline intact. That division is how mature codebases separate unit checks from integration "
                "checks. Today you write `review`, run it on a four-pixel cross, print each named check, and assert "
                "they all pass."
            ),
            code=(
                'def preprocess(grid):\n'
                '    return [[1 if px >= 128 else 0 for px in row] for row in grid]\n'
                '\n'
                'def classify(grid):\n'
                '    main = sum(grid[i][i] for i in range(len(grid)))\n'
                '    anti = sum(grid[i][len(grid) - 1 - i] for i in range(len(grid)))\n'
                '    if main == 4 and anti == 4:\n'
                '        return "x"\n'
                '    if main == 4:\n'
                '        return "d"\n'
                '    if max(sum(r) for r in grid) == 4:\n'
                '        return "h"\n'
                '    if max(sum(r[c] for r in grid) for c in range(len(grid))) == 4:\n'
                '        return "v"\n'
                '    return "unknown"\n'
                '\n'
                'def review(grid):\n'
                '    binary = preprocess(grid)\n'
                '    return {\n'
                '        "shape": len(binary) == 4 and all(len(r) == 4 for r in binary),\n'
                '        "binary": all(v in (0, 1) for r in binary for v in r),\n'
                '        "labelled": classify(binary) != "unknown",\n'
                '    }\n'
                '\n'
                'grid = [[255, 0, 0, 255], [0, 255, 255, 0], [0, 255, 255, 0], [255, 0, 0, 255]]\n'
                'checks = review(grid)\n'
                'for key in sorted(checks):\n'
                '    print(key, checks[key])\n'
                '\n'
                'assert all(checks.values())\n'
                'print("the review is the test suite summary")\n'
            ),
            variant_b="point review at a blank grid and show the 'labelled' check failing",
            variant_c="add a check that foreground count is between one and twelve and print the tally",
            mistakes=[
                "Reviewing by rereading the code instead of running named checks over a real sample.",
                "Treating every check as a warning, so a fatal shape error passes unnoticed.",
                "Merging the review into the classifier, which hides which invariant broke.",
            ],
            q1=(
                "How does the review differ from the unit tests?",
                "The tests check the classifier on designed cases, while the review checks that a real sample travels the whole pipeline and still satisfies each invariant.",
            ),
            homework=(
                "Write `final_review(grid)` returning a dict of named boolean checks for shape, binary values "
                "and a real label. Run it on a cross sample, print each check, and comment which check would fail "
                "first on a malformed input."
            ),
            patterns=["def ", "final_review", "all("],
            mapping=(
                "Integration checks run before a model ships are exactly this: named invariants over a real "
                "sample that fail loudly long before a user sees a wrong answer."
            ),
        ),
        179: dict(
            topic="Ship: retrospective and next steps",
            idea=(
                "Shipping ends with a retrospective, and today's technique is to write it as a dictionary with "
                "fixed sections so it captures learning rather than a story. Four sections cover the ground: what "
                "worked, what was learned, what comes next, and what to keep. Writing it as data keeps each item "
                "short and reviewable, and it can be diffed against next week's version to show what actually "
                "changed. The most valuable section is next steps, because a capstone that ends without a named "
                "successor becomes a dead folder; naming three concrete extensions — rotation invariance, learned "
                "features and more classes — turns the project into a queue. The learned section should record "
                "decisions, not events: 'lock the metric before tuning' is useful later, while 'fixed a bug' is "
                "not. The keep section preserves the habits that paid off — asserting at boundaries and one metric "
                "per run — so they carry into the next project. The retrospective should also state honestly what "
                "was out of scope and why, which is the same scoping skill from day one applied in hindsight. "
                "Finally, every artefact from the week should run from a single command so the project is "
                "reproducible by a stranger. Today you write the retrospective dict, print each section, and assert "
                "the next-steps list is non-empty."
            ),
            code=(
                'RETRO = {\n'
                '    "worked": ["clean data contract", "fast feature classifier"],\n'
                '    "learned": ["lock the metric before tuning", "count operations to prove speed"],\n'
                '    "next": ["rotation invariance", "learned features", "more classes"],\n'
                '    "keep": ["assert at boundaries", "one metric per run"],\n'
                '}\n'
                '\n'
                'for section in ("worked", "learned", "next", "keep"):\n'
                '    print(section + ":")\n'
                '    for item in RETRO[section]:\n'
                '        print("  -", item)\n'
                '\n'
                'assert len(RETRO["next"]) >= 1\n'
                'assert "metric" in RETRO["learned"][0]\n'
                'print("a retrospective names what is next, not just what happened")\n'
            ),
            variant_b="add an 'out_of_scope' section and record colour and rotation as deferred with a reason",
            variant_c="reduce next steps to one and note how a single item changes planning",
            mistakes=[
                "Writing a story with no named next steps, so the project quietly dies.",
                "Recording events instead of decisions, which teaches nothing for the next project.",
                "Forgetting what was out of scope, so the same work is re-scoped from scratch later.",
            ],
            q1=(
                "Why is the next-steps section the most valuable part of the retrospective?",
                "Because naming concrete successors turns a finished project into a queue, which is what keeps progress going instead of stopping at ship.",
            ),
            homework=(
                "Write `write_retro()` returning a dict with worked, learned, next and keep lists. Print each "
                "section and its items, assert the next list is non-empty, and comment which entry you will start "
                "on next."
            ),
            patterns=["def ", "write_retro", "print("],
            mapping=(
                "Postmortems and project retros in real teams use the same worked/learned/next shape; writing it "
                "as data makes it diffable against the next cycle."
            ),
        ),
    },
)
