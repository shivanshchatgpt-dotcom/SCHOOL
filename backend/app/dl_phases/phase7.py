"""Deep Learning capstone, days 165-179: one project, built one idea at a time.

Each day is a working slice of the same toy capstone, a linear regressor over two
features on a fixed six-row dataset, written in pure stdlib Python and run offline
and deterministically. The slices build in order: a scope contract, a model spec,
data preparation, the forward pass, the training loop, a tuning sweep, held-out
evaluation, assert-based tests, interpretation, edge-case guards, an experiment
log, a report, a reproducibility pass, a ship checklist and a retrospective. No
third-party numerical framework is imported anywhere, because the point of the
capstone is to show the whole experiment end to end in code you can read and rerun.
"""

PHASE = (
    "Deep Learning Capstone",
    "Take one narrowly scoped deep learning question from a written scope contract to a tested, reproducible result.",
    {
        165: dict(
            topic="Capstone: choose the scope",
            idea=(
                "A capstone succeeds or fails before any code is written, in how narrowly its scope is drawn, so today "
                "you write a one-page scope contract instead of starting a model. A useful contract has six fields: the "
                "single question the project answers, the exact dataset and its size, the one metric that decides "
                "success, the baseline that metric must beat, the time or compute budget, and the non-goals you refuse "
                "to attempt. Writing the non-goals matters most, because unfinished capstones almost always tried to "
                "answer three questions at once. Keep the question falsifiable: can two features predict this target can "
                "succeed or fail, whereas explore the data cannot. Fix the metric and baseline now, for example mean "
                "squared error against a mean predictor, so you cannot quietly redefine success after seeing the "
                "numbers. Name the dataset and freeze it, including how many rows are reserved for testing, because a "
                "dataset that grows mid-project invalidates every earlier comparison. Freeze both the rows and the metric before the first experiment. Today you write your own contract "
                "in a small dictionary and print it, then assert that it names a metric and a baseline. Everything that "
                "follows, the spec, training, tests and report, is judged against this one page."
            ),
            code=(
                'SPEC = {\n'
                '    "question": "can two features predict the target",\n'
                '    "dataset": "6 fixed rows",\n'
                '    "metric": "mse",\n'
                '    "baseline": "mean predictor",\n'
                '    "budget": "300 steps",\n'
                '    "non_goals": "no hidden layers",\n'
                '}\n'
                'for key in sorted(SPEC):\n'
                '    print(key, "=", SPEC[key])\n'
                '\n'
                'assert SPEC["metric"] == "mse"\n'
                'assert SPEC["baseline"] == "mean predictor"\n'
                'print("scope fixed: one question, one metric, one baseline")'
            ),
            variant_b='add a second metric and a second baseline, then print which one you trust and why',
            variant_c='write a deliberately vague question and show that no baseline or metric can be fixed for it',
            mistakes=[
                "Writing a question that cannot fail, so no result ever settles it.",
                "Choosing the metric after seeing results, which turns a test into a story.",
                "Listing no non-goals, so the project quietly expands until it stalls.",
            ],
            q1=(
                "Why should the baseline be fixed in the scope contract rather than after training?",
                "A baseline chosen in advance makes the result falsifiable; chosen later, it can always be made weak enough to beat.",
            ),
            homework=(
                "Write `scope(question, dataset, metric, baseline, budget, non_goals)` that returns a dictionary of the "
                "six fields and prints them sorted by key. Fill it for your own capstone, assert that metric and "
                "baseline are short strings, and comment why the non_goal field matters."
            ),
            patterns=["def ", "sorted", "print("],
            mapping=(
                "Real projects live or die on scope: production models start from a written problem statement, a fixed "
                "evaluation metric and an explicit baseline, exactly as this contract does."
            ),
        ),
        166: dict(
            topic="Write the model spec",
            idea=(
                "With the scope fixed, the next artefact is a model specification short enough to fit on a screen and "
                "precise enough to implement without a decision left open. A good spec names the inputs and their "
                "shapes, every parameter and its initial value, the forward computation, the loss, and the update rule, "
                "in that order. Naming the parameter count up front is a surprisingly effective check: for a linear "
                "model over two features it must be three, one per feature plus the bias, and any mismatch means the "
                "design drifted. State the initial values explicitly, usually zeros for a linear model, because a hidden "
                "random initialisation is one more thing a reader cannot reproduce. Write the forward pass as a formula, "
                "not as code, and only then translate it; the translation should be mechanical. The loss must be the "
                "metric's training twin, so mean squared error for both. The update rule says plainly that each "
                "parameter moves against its own gradient scaled by a learning rate. Today you encode this spec in a "
                "dictionary, implement the forward pass from it, and confirm the parameter count and one hand-computed "
                "prediction, so spec and code are tested against each other before training exists."
            ),
            code=(
                'MODEL = {\n'
                '    "inputs": 2,\n'
                '    "params": ["w1", "w2", "b"],\n'
                '    "init": 0.0,\n'
                '    "loss": "mse",\n'
                '    "update": "gradient descent",\n'
                '}\n'
                '\n'
                'def predict(x, p):\n'
                '    return p["w1"] * x[0] + p["w2"] * x[1] + p["b"]\n'
                '\n'
                'p = {"w1": 0.0, "w2": 0.0, "b": 0.0}\n'
                'print("params:", MODEL["params"])\n'
                'print("count:", len(MODEL["params"]))\n'
                'print("init prediction:", predict([2.0, 3.0], p))\n'
                '\n'
                'assert len(MODEL["params"]) == MODEL["inputs"] + 1\n'
                'assert predict([1.0, 1.0], {"w1": 2.0, "w2": -1.0, "b": 1.0}) == 2.0\n'
                'print("the spec names every parameter before any training")'
            ),
            variant_b='add a second output so the spec has two biases and print the new parameter count',
            variant_c='change the loss in the spec to mae and note that the gradients would need rewriting too',
            mistakes=[
                "Leaving the initialisation implicit, so two runs can never be compared.",
                "Letting the parameter count drift from the feature count without noticing.",
                "Writing the spec after the code, so it documents guesses instead of decisions.",
            ],
            q1=(
                "Why write the forward pass as a formula in the spec before translating it to code?",
                "The formula exposes shapes, parameter count and sign mistakes cheaply, before code makes the same errors harder to see.",
            ),
            homework=(
                "Write `spec(inputs)` returning a dictionary with parameter names, initial value, loss and update rule, "
                "and `predict(x, p)` that consumes it. Print the parameter count and one prediction, assert the count "
                "equals inputs plus one, and comment where the bias appears in the formula."
            ),
            patterns=["def ", "assert", "print("],
            mapping=(
                "A model spec is the contract between research and engineering: shape tables and initialisation schemes "
                "in real repositories exist precisely so a run can be reconstructed."
            ),
        ),
        167: dict(
            topic="Prepare the data",
            idea=(
                "Data preparation is where most quiet capstone bugs live, so today you write a small, testable prepare "
                "function rather than loading rows by hand. The function takes the frozen rows and the expected feature "
                "count, checks every row's shape, and splits the data deterministically into a training portion and a "
                "held-out test portion. Checking the feature count first turns a confusing shape error deep inside "
                "training into a clear message at the boundary, which is exactly where a trust boundary belongs. Split "
                "by position or by a fixed seed, never by a fresh shuffle, because the split must be identical on every "
                "run or the metric is not comparable across experiments. Fit nothing on the test rows: no scaling, no "
                "imputation, no selection. A mean or standard deviation computed over all rows leaks test information "
                "into training and inflates the final score, quietly. Keep the test rows small but untouched; two rows "
                "are enough for this toy project and remain honest. Today you implement the prepare function, print the "
                "sizes and the first training row, and assert that the two portions add up to the whole dataset. That "
                "single assertion catches dropped or duplicated rows, the most common data bug of all."
            ),
            code=(
                'DATA = [\n'
                '    ([1.0, 0.0], 3.0),\n'
                '    ([0.0, 1.0], 0.0),\n'
                '    ([1.0, 1.0], 2.0),\n'
                '    ([2.0, 1.0], 4.0),\n'
                '    ([1.0, 2.0], 1.0),\n'
                '    ([2.0, 3.0], 2.0),\n'
                ']\n'
                'FEATURES = 2\n'
                '\n'
                'def prepare(rows, features):\n'
                '    for x, y in rows:\n'
                '        if len(x) != features:\n'
                '            raise ValueError("expected " + str(features) + " features")\n'
                '    split = len(rows) * 3 // 4\n'
                '    return rows[:split], rows[split:]\n'
                '\n'
                'train, test = prepare(DATA, FEATURES)\n'
                'print("train rows:", len(train))\n'
                'print("test rows:", len(test))\n'
                'print("first train row:", train[0])\n'
                '\n'
                'assert len(train) + len(test) == len(DATA)\n'
                'assert all(len(x) == FEATURES for x, _ in DATA)\n'
                'print("prepare checks, splits and never touches the test rows")'
            ),
            variant_b='split 50/50 instead and print the two sizes, then argue which split this six-row set deserves',
            variant_c='pass a row with one feature and show the ValueError naming the expected count',
            mistakes=[
                "Shuffling on every run, so the split and therefore the metric change between experiments.",
                "Computing normalisation statistics over all rows, leaking test information into training.",
                "Forgetting to check row shapes, so a short row surfaces later as a cryptic maths error.",
            ],
            q1=(
                "Why must the train/test split be deterministic rather than freshly shuffled each run?",
                "A changing split changes the metric, so results from different runs can no longer be compared or reproduced.",
            ),
            homework=(
                "Write `prepare(rows, features, split)` that validates every row's feature count, splits at the given "
                "fraction, and returns the training and test lists. Print both sizes, assert they sum to the input, and "
                "comment which line protects against a silent shape error."
            ),
            patterns=["def ", "raise", "print("],
            mapping=(
                "This is a miniature of a real data loader: validate at the edge, split deterministically, and fit all "
                "preprocessing on the training portion only."
            ),
        ),
        168: dict(
            topic="Build the forward pass",
            idea=(
                "The forward pass is the part of a model you can fully verify, so today you build the predictor and its "
                "loss as pure functions over the frozen dataset. For a linear model the forward pass is a weighted sum "
                "plus a bias: multiply the first feature by its weight, the second by its weight, add the intercept, "
                "return the number. Writing it once and calling it everywhere means training, evaluation and tests all "
                "share the same definition, so they cannot disagree. The loss goes beside it: mean squared error over "
                "the batch, which is the number training will reduce. With both functions in place, check a "
                "hand-computed case before any learning happens, because at this point the arithmetic is still small "
                "enough to do in your head. Then evaluate the loss at zero weights, which is the natural baseline model, "
                "and note the value; every later improvement is measured against it. Rounding the printed outputs keeps "
                "the idea visible instead of burying it in floating-point tails. Today you write predict and mse, print "
                "a few predictions against their targets, assert one exact hand-computed prediction and the zero-weight "
                "loss, and confirm the forward pass is just two multiplies and an add."
            ),
            code=(
                'TRAIN = [\n'
                '    ([1.0, 0.0], 3.0),\n'
                '    ([0.0, 1.0], 0.0),\n'
                '    ([1.0, 1.0], 2.0),\n'
                '    ([2.0, 1.0], 4.0),\n'
                ']\n'
                '\n'
                'def predict(x, weights):\n'
                '    w1, w2, b = weights\n'
                '    return w1 * x[0] + w2 * x[1] + b\n'
                '\n'
                'def mse(rows, weights):\n'
                '    return sum((predict(x, weights) - y) ** 2 for x, y in rows) / len(rows)\n'
                '\n'
                'weights = [0.0, 0.0, 0.0]\n'
                'for x, y in TRAIN[:3]:\n'
                '    print(x, "->", round(predict(x, weights), 4), "target", y)\n'
                'print("mse at zero weights:", round(mse(TRAIN, weights), 4))\n'
                '\n'
                'assert predict([1.0, 1.0], [2.0, -1.0, 1.0]) == 2.0\n'
                'assert mse(TRAIN, [0.0, 0.0, 0.0]) > 0.0\n'
                'print("the forward pass is two multiplies and an add")'
            ),
            variant_b='print the prediction for every training row and eyeball how far each is from its target',
            variant_c='set the weights to the true values and show the loss drops to exactly zero',
            mistakes=[
                "Reimplementing the prediction inside the loss, so the two definitions can drift apart.",
                "Forgetting the bias term, which shifts every prediction by a constant.",
                "Taking the residual the wrong way round, flipping the sign of the loss gradient.",
            ],
            q1=(
                "Why define predict once and have mse call it instead of recomputing the weighted sum?",
                "One definition means training, evaluation and tests cannot disagree about what the model computes.",
            ),
            homework=(
                "Write `predict(x, weights)` for a two-feature linear model and `mse(rows, weights)`. Print three "
                "predictions beside their targets, assert a hand-computed prediction equals its exact value, and "
                "comment which line performs the weighted sum plus bias."
            ),
            patterns=["def ", "sum(", "print("],
            mapping=(
                "A framework layer's forward method is this function generalised; keeping the forward pure is what makes "
                "gradient checks and unit tests possible later."
            ),
        ),
        169: dict(
            topic="Implement training",
            idea=(
                "Training is the loop that turns the forward pass into a learner, and today you write it in full: "
                "forward, loss, gradient, update, repeat. The gradient of mean squared error for a linear model has a "
                "closed form. For each row the residual is prediction minus target; each weight's gradient is twice the "
                "average of residual times that weight's feature, and the bias gradient is twice the average residual. "
                "Computing all three over the whole batch before touching the parameters is essential, because updating "
                "a weight before the others are measured mixes two different models into one step. Then subtract "
                "learning rate times gradient from each parameter. Track the loss at the start and end, and assert it "
                "fell; a loss that does not fall means a wrong sign or an oversized step, not a mystery. With a modest "
                "learning rate this toy model reaches the true weights quickly, and the printed history shows the loss "
                "dropping by orders of magnitude. Today you implement gradients and a train function that returns the "
                "final weights and a short loss history, print them, and assert improvement. This is the identical loop "
                "every framework runs, minus the automatic differentiation. That single assertion is your first defence against a silent sign error."
            ),
            code=(
                'TRAIN = [\n'
                '    ([1.0, 0.0], 3.0),\n'
                '    ([0.0, 1.0], 0.0),\n'
                '    ([1.0, 1.0], 2.0),\n'
                '    ([2.0, 1.0], 4.0),\n'
                ']\n'
                '\n'
                'def predict(x, weights):\n'
                '    return weights[0] * x[0] + weights[1] * x[1] + weights[2]\n'
                '\n'
                'def mse(rows, weights):\n'
                '    return sum((predict(x, weights) - y) ** 2 for x, y in rows) / len(rows)\n'
                '\n'
                'def gradients(rows, weights):\n'
                '    n = len(rows)\n'
                '    g1 = g2 = gb = 0.0\n'
                '    for x, y in rows:\n'
                '        error = predict(x, weights) - y\n'
                '        g1 += 2 * error * x[0] / n\n'
                '        g2 += 2 * error * x[1] / n\n'
                '        gb += 2 * error / n\n'
                '    return [g1, g2, gb]\n'
                '\n'
                'def train(rows, lr, steps):\n'
                '    weights = [0.0, 0.0, 0.0]\n'
                '    history = []\n'
                '    for step in range(steps):\n'
                '        g = gradients(rows, weights)\n'
                '        weights = [w - lr * gi for w, gi in zip(weights, g)]\n'
                '        if step % 100 == 0:\n'
                '            history.append(round(mse(rows, weights), 4))\n'
                '    return weights, history\n'
                '\n'
                'weights, history = train(TRAIN, 0.1, 300)\n'
                'print("loss every 100 steps:", history)\n'
                'print("final weights:", [round(w, 4) for w in weights])\n'
                '\n'
                'assert history[0] > history[-1]\n'
                'print("forward, gradient, update: repeat and the loss falls")'
            ),
            variant_b='set the learning rate to 0.5 and show the loss exploding instead of falling',
            variant_c='update each weight immediately after computing its gradient and compare the messy history',
            mistakes=[
                "Updating weights inside the gradient loop, so later gradients use half-updated parameters.",
                "Leaving the two-over-n factor out, making the effective learning rate depend on batch size.",
                "Trusting a loss history without asserting that the final value is lower than the first.",
            ],
            q1=(
                "Why must all gradients be computed before any parameter is updated?",
                "All gradients must describe the same parameter values; updating early makes later gradients inconsistent with the model.",
            ),
            homework=(
                "Write `gradients(rows, weights)` for mean squared error and `train(rows, lr, steps)` returning the "
                "final weights and loss history. Train this dataset, print the history and weights, and comment which "
                "line performs the parameter update."
            ),
            patterns=["def ", "for ", "print("],
            mapping=(
                "This is exactly what `loss.backward()` computes and `optimizer.step()` applies; the framework only "
                "automates the derivative and batches the arithmetic."
            ),
        ),
        170: dict(
            topic="Tune the optimisation",
            idea=(
                "Optimisation has very few knobs, and the learning rate dominates all of them, so today you tune it "
                "deliberately rather than guessing. The method is a sweep: pick a small set of candidate rates, run the "
                "same training loop with the same fixed budget for each, and record the final training loss. Print the "
                "table and read it. A rate that is too small leaves the loss high because the run has not converged; a "
                "rate that is too large overshoots and can diverge to enormous values, which is why the sweep includes "
                "an obviously bad candidate on purpose. Choose the best candidate and expect a broad basin, not a "
                "single magic number: several nearby rates should work almost as well, and that robustness is more "
                "valuable than a precisely tuned optimum. One rule matters more than the search itself: tune on training "
                "or validation rows, never on the held-out test rows, or the final test metric stops being an honest "
                "estimate. Also hold the step budget and initialisation fixed across candidates, so the only thing "
                "changing is the rate. Today you write a fit helper and a loop that prints the loss for several rates, "
                "assert your chosen rate is the best of the set, and note which candidate diverged."
            ),
            code=(
                'TRAIN = [\n'
                '    ([1.0, 0.0], 3.0),\n'
                '    ([0.0, 1.0], 0.0),\n'
                '    ([1.0, 1.0], 2.0),\n'
                '    ([2.0, 1.0], 4.0),\n'
                ']\n'
                '\n'
                'def predict(x, weights):\n'
                '    return weights[0] * x[0] + weights[1] * x[1] + weights[2]\n'
                '\n'
                'def mse(rows, weights):\n'
                '    return sum((predict(x, weights) - y) ** 2 for x, y in rows) / len(rows)\n'
                '\n'
                'def fit(rows, lr, steps):\n'
                '    weights = [0.0, 0.0, 0.0]\n'
                '    for _ in range(steps):\n'
                '        n = len(rows)\n'
                '        g = [0.0, 0.0, 0.0]\n'
                '        for x, y in rows:\n'
                '            error = predict(x, weights) - y\n'
                '            g[0] += 2 * error * x[0] / n\n'
                '            g[1] += 2 * error * x[1] / n\n'
                '            g[2] += 2 * error / n\n'
                '        weights = [w - lr * gi for w, gi in zip(weights, g)]\n'
                '    return weights\n'
                '\n'
                'candidates = [0.001, 0.01, 0.1, 0.5]\n'
                'for lr in candidates:\n'
                '    loss = mse(TRAIN, fit(TRAIN, lr, 300))\n'
                '    print("lr", lr, "train mse", round(loss, 6))\n'
                '\n'
                'best = min(candidates, key=lambda lr: mse(TRAIN, fit(TRAIN, lr, 300)))\n'
                'print("chosen lr:", best)\n'
                '\n'
                'assert best == 0.1\n'
                'print("sweep the rate and pick by loss, never by test rows")'
            ),
            variant_b='add 0.2 to the candidates and show it reaches zero loss just as the table predicts',
            variant_c='fix a tiny budget of 20 steps and show that the ranking of rates can change',
            mistakes=[
                "Selecting the learning rate using the test rows, which silently overfits the evaluation.",
                "Changing the budget between candidates, so the comparison measures the budget as well.",
                "Reporting a single best rate without checking that neighbours behave similarly.",
            ],
            q1=(
                "Why include a deliberately too-large learning rate in the sweep?",
                "Seeing the loss diverge marks the upper edge of the useful range, which frames where the good rates lie.",
            ),
            homework=(
                "Write `sweep(rows, rates, steps)` that trains once per rate and returns a list of (rate, loss) pairs. "
                "Print the table, pick the best pair, assert the chosen rate is the minimum-loss one, and comment which "
                "row of the sweep diverged."
            ),
            patterns=["def ", "min(", "print("],
            mapping=(
                "Hyperparameter sweeps and learning-rate finders in real training do the same thing at scale: fix all "
                "else, vary one factor, and select on validation loss."
            ),
        ),
        171: dict(
            topic="Evaluate properly",
            idea=(
                "A number is not an evaluation, so today you report metrics properly: on the held-out rows, against a "
                "baseline, with more than one measure. Start with the baseline the scope contract named, usually "
                "predicting the training mean everywhere, and compute its test error. A model that cannot beat that has "
                "learned nothing worth reporting, however low its training loss looks. Then compute the model's test "
                "mean squared error and mean absolute error. Squared error punishes large misses and is the training "
                "loss's twin; absolute error is easier to read in the target's own units, so the pair together tells a "
                "fuller story. Report training and test error side by side. A large gap means overfitting, a small gap "
                "with both high means underfitting, and both low on this tiny exact dataset is the expected outcome. "
                "Never adjust anything after seeing test numbers; if you do, they are validation numbers and you need a "
                "fresh holdout. Today you write the baseline, the two metrics and a short report of test versus "
                "baseline, and assert that the model beats the baseline on the rows it has never seen. Print the table, not just the winning number, so the gap between them stays visible."
            ),
            code=(
                'TRAIN = [\n'
                '    ([1.0, 0.0], 3.0),\n'
                '    ([0.0, 1.0], 0.0),\n'
                '    ([1.0, 1.0], 2.0),\n'
                '    ([2.0, 1.0], 4.0),\n'
                ']\n'
                'TEST = [\n'
                '    ([1.0, 2.0], 1.0),\n'
                '    ([2.0, 3.0], 2.0),\n'
                ']\n'
                '\n'
                'def predict(x, weights):\n'
                '    return weights[0] * x[0] + weights[1] * x[1] + weights[2]\n'
                '\n'
                'def mse(rows, weights):\n'
                '    return sum((predict(x, weights) - y) ** 2 for x, y in rows) / len(rows)\n'
                '\n'
                'def mae(rows, weights):\n'
                '    return sum(abs(predict(x, weights) - y) for x, y in rows) / len(rows)\n'
                '\n'
                'weights = [2.0, -1.0, 1.0]\n'
                'mean_y = sum(y for _, y in TRAIN) / len(TRAIN)\n'
                'baseline = [0.0, 0.0, mean_y]\n'
                '\n'
                'print("train mse:", round(mse(TRAIN, weights), 4))\n'
                'print("test mse:", round(mse(TEST, weights), 4))\n'
                'print("test mae:", round(mae(TEST, weights), 4))\n'
                'print("baseline test mse:", round(mse(TEST, baseline), 4))\n'
                '\n'
                'assert mse(TEST, weights) < mse(TEST, baseline)\n'
                'print("report held-out error beside a baseline, never alone")'
            ),
            variant_b='print the baseline prediction mean and check that it does not need the test rows',
            variant_c='evaluate on the training rows instead and show how the comparison flatters the model',
            mistakes=[
                "Reporting training error as if it were the result, when the model has seen those rows.",
                "Quoting a metric without a baseline, so the reader cannot judge whether it is good.",
                "Tuning anything after reading the test numbers, which quietly turns them into validation.",
            ],
            q1=(
                "Why report mean absolute error as well as mean squared error?",
                "Squared error is dominated by large misses while absolute error stays in the target's units, so together they describe different failure modes.",
            ),
            homework=(
                "Write `mae(rows, weights)` and `evaluate(train, test, weights)` that prints train and test mean squared "
                "error plus the mean-predictor baseline. Assert the model beats the baseline on test, and comment which "
                "line computes the mean predictor."
            ),
            patterns=["def ", "abs(", "print("],
            mapping=(
                "Model cards and benchmark tables always pair a metric with a baseline; reporting a held-out score in "
                "isolation is how results get overstated."
            ),
        ),
        172: dict(
            topic="Write the tests",
            idea=(
                "A capstone without tests is a claim you cannot re-check, so today you write a tiny assert-based test "
                "suite for the model's core functions. Good tests here are small, named and independent: one checks the "
                "forward pass against a hand-computed value, one checks that the true weights give exactly zero loss on "
                "the exact data, one checks that a training run actually reduces the loss, and one checks that the same "
                "seed produces the same result. Each test states what it is checking, runs one operation, and asserts "
                "one condition, the arrange-act-assert shape used everywhere. A small helper that prints a passing "
                "test's name and raises on failure keeps the suite readable and needs no framework. The point is not "
                "coverage percentage; it is that a change to the forward pass or the gradient should break a test "
                "loudly rather than silently change a number in a report. Write the tests against the tiny "
                "hand-checkable case first, because if the test itself is wrong the whole exercise is theatre. Today you "
                "write four checks over predict, mse and train, run them, and print that they passed. Keep each test deliberately independent so that one failure cannot mask the next one."
            ),
            code=(
                'DATA = [\n'
                '    ([1.0, 0.0], 3.0),\n'
                '    ([0.0, 1.0], 0.0),\n'
                '    ([1.0, 1.0], 2.0),\n'
                '    ([2.0, 1.0], 4.0),\n'
                ']\n'
                '\n'
                'def predict(x, weights):\n'
                '    return weights[0] * x[0] + weights[1] * x[1] + weights[2]\n'
                '\n'
                'def mse(rows, weights):\n'
                '    return sum((predict(x, weights) - y) ** 2 for x, y in rows) / len(rows)\n'
                '\n'
                'def check(name, condition):\n'
                '    assert condition, name\n'
                '    print("pass:", name)\n'
                '\n'
                'def fit(rows, lr, steps):\n'
                '    weights = [0.0, 0.0, 0.0]\n'
                '    for _ in range(steps):\n'
                '        n = len(rows)\n'
                '        g = [0.0, 0.0, 0.0]\n'
                '        for x, y in rows:\n'
                '            error = predict(x, weights) - y\n'
                '            g[0] += 2 * error * x[0] / n\n'
                '            g[1] += 2 * error * x[1] / n\n'
                '            g[2] += 2 * error / n\n'
                '        weights = [w - lr * gi for w, gi in zip(weights, g)]\n'
                '    return weights\n'
                '\n'
                'check("hand example", predict([1.0, 1.0], [2.0, -1.0, 1.0]) == 2.0)\n'
                'check("true weights zero loss", mse(DATA, [2.0, -1.0, 1.0]) == 0.0)\n'
                'check("training reduces loss", mse(DATA, fit(DATA, 0.1, 300)) < mse(DATA, [0.0, 0.0, 0.0]))\n'
                'check("same seed same result", fit(DATA, 0.1, 300) == fit(DATA, 0.1, 300))\n'
                'print("4 checks passed")'
            ),
            variant_b='add a failing check on purpose and show the assertion stops the suite with a clear name',
            variant_c='turn the tests into a function returning (passed, failed) counts and print a summary line',
            mistakes=[
                "Testing the training output instead of the small hand-computable function, so the test is as opaque as the model.",
                "Writing one giant test, so a failure does not localise to a single behaviour.",
                "Asserting on floating point equality without a hand-exact case first.",
            ],
            q1=(
                "What is the value of an assert-based test suite with no testing framework?",
                "It re-checks core behaviour cheaply and fails loudly on regressions, using only the standard language.",
            ),
            homework=(
                "Write `check(name, condition)` that prints passing tests and raises on failure, then add four checks: a "
                "hand-computed prediction, zero loss at true weights, a training run reducing loss, and seed-stable "
                "training. Run the suite and comment which check guards the gradient."
            ),
            patterns=["def ", "assert", "print("],
            mapping=(
                "Real projects use pytest or unittest for this, but the shape is identical: small named tests that "
                "localise a regression instead of hiding it in a metric."
            ),
        ),
        173: dict(
            topic="Interpret the results",
            idea=(
                "Interpretation asks what the fitted numbers mean, and for a linear model that is unusually direct, so "
                "today you read the coefficients instead of only the score. Each weight is the change in the prediction "
                "for a one-unit increase in that feature, holding the others fixed, and its sign says direction while "
                "its magnitude says strength. Compare the learned weights with the values that generated the data: "
                "close agreement is evidence the model recovered the real relationship, and a large disagreement with a "
                "low loss is a warning that the data does not pin the parameters down. Decompose one prediction into "
                "its per-feature contributions, weight times feature plus the bias, and check that they sum to the "
                "output; this makes the arithmetic of a prediction explicit and exposes whether one feature dominates. "
                "Look at the residuals on the test rows as well, remembering that with an exact linear dataset tiny "
                "residuals mean little, while on real noisy data a pattern in residuals signals a missing term. Resist "
                "the temptation to call a correlation a cause, especially with six rows. Today you print the "
                "coefficients, one row's contributions and the test residuals, and assert the contributions reconstruct "
                "the prediction. That is a cheap correctness check on the interpretation itself."
            ),
            code=(
                'TEST = [\n'
                '    ([1.0, 2.0], 1.0),\n'
                '    ([2.0, 3.0], 2.0),\n'
                ']\n'
                '\n'
                'def predict(x, weights):\n'
                '    return weights[0] * x[0] + weights[1] * x[1] + weights[2]\n'
                '\n'
                'weights = [2.0, -1.0, 1.0]\n'
                'print("w1:", weights[0], "w2:", weights[1], "bias:", weights[2])\n'
                '\n'
                'x, y = TEST[0]\n'
                'parts = [weights[0] * x[0], weights[1] * x[1], weights[2]]\n'
                'print("contributions:", parts)\n'
                'print("prediction:", round(sum(parts), 4), "target:", y)\n'
                '\n'
                'for row, target in TEST:\n'
                '    print("residual:", round(target - predict(row, weights), 4))\n'
                '\n'
                'assert round(sum(parts), 4) == round(predict(x, weights), 4)\n'
                'print("read the coefficients and residuals, not just the score")'
            ),
            variant_b='flip the sign of w2 and show how the second feature now pushes predictions the other way',
            variant_c='print the contribution of each feature as a fraction of the prediction to see which dominates',
            mistakes=[
                "Reading a coefficient as causal when the data is only observational.",
                "Interpreting weights when features are on wildly different scales, making magnitudes incomparable.",
                "Ignoring residuals entirely, so a systematic pattern goes unnoticed.",
            ],
            q1=(
                "What does a linear weight mean, stated in words?",
                "It is the predicted change in the output for a one-unit increase in that feature while the other features are held fixed.",
            ),
            homework=(
                "Write `explain(x, y, weights)` that returns the per-feature contributions, the prediction and the "
                "residual for one row. Print the coefficients and one row's decomposition, assert the contributions sum "
                "to the prediction, and comment which weight dominates."
            ),
            patterns=["def ", "sum(", "print("],
            mapping=(
                "Feature attribution in production models is a harder version of this: decompose a prediction into "
                "evidence a human can check, and distrust causal claims the data cannot support."
            ),
        ),
        174: dict(
            topic="Handle the edge cases",
            idea=(
                "Edge cases decide whether a capstone is a demo or a component, so today you add guards at the "
                "boundaries and prove they fire. A data function should reject an empty dataset rather than dividing by "
                "zero later, and reject any row whose feature count differs from the expected count, with an error "
                "message naming the actual and expected sizes. A prediction function should reject a feature vector of "
                "the wrong length and any non-finite number, because a NaN silently poisons every subsequent gradient. "
                "A training function should reject a non-positive step budget and a learning rate that is not positive, "
                "and you should decide explicitly what a learning rate of zero means, since it is legal but learns "
                "nothing. Validate once, at the entry point, where the message is close to the mistake; scattering "
                "checks through the maths makes them unmaintainable and easy to skip. The lazy but complete pattern is a "
                "short validate function that raises ValueError with a useful message, plus one check per guard. Today "
                "you write validate and a small table of bad inputs, catch each rejection and print it, so a reviewer "
                "sees the failure modes handled rather than assumed away. Each guard also documents an assumption the model cannot repair."
            ),
            code=(
                'import math\n'
                '\n'
                'def validate(rows, features):\n'
                '    if not rows:\n'
                '        raise ValueError("empty dataset")\n'
                '    for x, y in rows:\n'
                '        if len(x) != features:\n'
                '            raise ValueError("expected " + str(features) + " features, got " + str(len(x)))\n'
                '        if not all(math.isfinite(v) for v in x):\n'
                '            raise ValueError("non-finite feature value")\n'
                '    return len(rows)\n'
                '\n'
                'cases = [\n'
                '    ([], 2),\n'
                '    ([([1.0], 1.0)], 2),\n'
                '    ([([1.0, float("nan")], 0.0)], 2),\n'
                ']\n'
                'for rows, features in cases:\n'
                '    try:\n'
                '        validate(rows, features)\n'
                '    except ValueError as err:\n'
                '        print("rejected:", err)\n'
                '\n'
                'assert validate([([1.0, 2.0], 3.0)], 2) == 1\n'
                'print("guards run at the boundary, before the maths")'
            ),
            variant_b='add a guard rejecting a non-positive learning rate and show the message it prints',
            variant_c='remove one guard and show how a NaN quietly makes every later loss non-finite',
            mistakes=[
                "Validating deep inside the maths, so the error message no longer points at the bad input.",
                "Allowing NaN through, which spreads silently and turns every later number into NaN.",
                "Treating an empty dataset as a valid input, so a later average divides by zero.",
            ],
            q1=(
                "Why validate inputs at the entry point rather than scattered through the computation?",
                "One check at the boundary gives a clear message close to the mistake and cannot be skipped by a later code path.",
            ),
            homework=(
                "Write `validate(rows, features)` that raises ValueError for an empty dataset, a wrong feature count or "
                "a non-finite value. Call it on three bad inputs inside try/except, print each message, and comment "
                "which guard protects against silent NaN propagation."
            ),
            patterns=["def ", "raise", "except"],
            mapping=(
                "Production data pipelines fail fast at ingestion with descriptive errors; catching NaN and shape "
                "problems at the boundary is far cheaper than debugging them after a long training run."
            ),
        ),
        175: dict(
            topic="Polish the experiment log",
            idea=(
                "An experiment log is what lets you answer, weeks later, why a run produced the number it did, so today "
                "you make logging a first-class step rather than an afterthought. Each record captures the "
                "configuration, the seed, the budget, the dataset version, the metric and a one-line note; everything "
                "that could change the result must appear, because an unrecorded parameter is a result you cannot "
                "reproduce. Keep records append-only and machine-readable, a dictionary serialised with sorted keys is "
                "enough, so comparing two runs is mechanical instead of archaeological. When you compare runs, compare "
                "like with like: same dataset, same metric, same number of steps, with only the factor under study "
                "changing. The best run is not the highest score in isolation but the one you can explain and repeat. "
                "This habit directly serves the final report, which should cite configurations rather than vague "
                "claims. Today you build a couple of run records, write a log function that serialises each with sorted "
                "keys, print them, and assert which configuration wins by metric. Notice how the log turns a vague "
                "memory into an auditable line. Do this well before the final report, because that report should cite the log rather than memory."
            ),
            code=(
                'import json\n'
                '\n'
                'RUNS = [\n'
                '    {"id": "r1", "lr": 0.1, "steps": 300, "seed": 0, "mse": 0.0},\n'
                '    {"id": "r2", "lr": 0.01, "steps": 300, "seed": 0, "mse": 0.0478},\n'
                ']\n'
                '\n'
                'def log(run):\n'
                '    return json.dumps(run, sort_keys=True)\n'
                '\n'
                'for run in RUNS:\n'
                '    print(log(run))\n'
                '\n'
                'best = min(RUNS, key=lambda r: r["mse"])\n'
                'print("best:", best["id"], "lr", best["lr"], "steps", best["steps"])\n'
                '\n'
                'assert best["id"] == "r1"\n'
                'print("log config, seed and metric for every single run")'
            ),
            variant_b='add a notes field and show how a sorted-key log keeps records comparable',
            variant_c='add a run with a different dataset version and show why it cannot be ranked against the others',
            mistakes=[
                "Record only the final metric, so the run cannot be reproduced or compared.",
                "Use free-form prose, so two records cannot be diffed mechanically.",
                "Compare runs that differ in several factors, crediting all the change to one of them.",
            ],
            q1=(
                "Why record the seed and step budget alongside the metric?",
                "Without them the run cannot be reproduced, so the metric is an unexplained observation rather than evidence.",
            ),
            homework=(
                "Write `log(run)` that serialises one run dictionary with sorted keys, and `best(runs)` that returns the "
                "lowest-error run. Print both records, print the winner, assert its id, and comment which fields make a "
                "run reproducible."
            ),
            patterns=["def ", "json.dumps", "print("],
            mapping=(
                "Experiment trackers like Weights & Biases and MLflow exist to capture exactly this record automatically; "
                "a local JSON line is the same idea at capstone scale."
            ),
        ),
        176: dict(
            topic="Present the model",
            idea=(
                "Presenting a model is a writing task with a fixed skeleton, so today you assemble the report from the "
                "artefacts you already have. Open with the question and the dataset in one sentence each, because a "
                "reader must know what was asked before hearing the answer. State the method in plain language: model "
                "form, loss, optimiser, budget, then the result with its metric and the baseline side by side, so the "
                "improvement is visible in one line. Include the held-out numbers, not the training ones, and quote the "
                "configuration from the experiment log so the run is identifiable. Then write the limitations honestly, "
                "and there are always some: six rows, an exact linear relationship, no noise, one metric. Honesty here "
                "is not modesty, it is precision that lets a reader judge how far the result extends. Close with the "
                "next step the limitations imply, ordered by value. A table or a couple of printed lines is enough; "
                "polish is clarity, not decoration. Today you write a report function that returns a short structured "
                "text from the metrics you computed, print it, and assert the headline result beats the baseline. Print it and read it once as if you were a stranger."
            ),
            code=(
                'METRICS = {"train_mse": 0.0, "test_mse": 0.0, "baseline_mse": 0.8125}\n'
                'WEIGHTS = [2.0, -1.0, 1.0]\n'
                '\n'
                'def report(metrics, weights):\n'
                '    lines = [\n'
                '        "Question: can two features predict the target",\n'
                '        "Method: linear model, squared error, gradient descent",\n'
                '        "Result: test mse " + str(metrics["test_mse"]) + " vs baseline " + str(metrics["baseline_mse"]),\n'
                '        "Weights: " + str(weights),\n'
                '        "Limitation: six rows, no noise, linear only",\n'
                '        "Next: collect more rows and add a non-linear feature",\n'
                '    ]\n'
                '    return "\\n".join(lines)\n'
                '\n'
                'print(report(METRICS, WEIGHTS))\n'
                '\n'
                'assert METRICS["test_mse"] < METRICS["baseline_mse"]\n'
                'print("state the result, the baseline and the limitation")'
            ),
            variant_b='add a headline sentence summarising the result in under fifteen words',
            variant_c='swap in a weaker result and rewrite the limitation paragraph to stay honest',
            mistakes=[
                "Leading with the method and burying the result, so the reader has to hunt for the answer.",
                "Quoting the best cherry-picked run and omitting the configuration that produced it.",
                "Leaving out limitations, which makes the report sound confident beyond what six rows support.",
            ],
            q1=(
                "Why must the report quote held-out metrics and the run configuration together?",
                "The held-out metric gives an honest estimate and the configuration identifies the exact run, so the claim can be checked.",
            ),
            homework=(
                "Write `report(metrics, weights)` returning a short structured report with question, method, result "
                "versus baseline, limitation and next step. Print it, assert the test metric beats the baseline, and "
                "comment which line states the limitation."
            ),
            patterns=["def ", "return", "print("],
            mapping=(
                "Model cards and research abstracts follow this skeleton; stating a baseline, a holdout score and a "
                "limitation is the minimum for a result to be credible."
            ),
        ),
        177: dict(
            topic="Build day: reproducibility pass",
            idea=(
                "Reproducibility is a property you test, not a hope, so today you run a reproducibility pass over the "
                "whole pipeline. Fix every source of nondeterminism: initialise parameters to stated constants, seed "
                "any shuffle with a recorded integer, use a stable sort so ties break the same way, and avoid anything "
                "that depends on the clock, the filesystem order or the network. Then run the pipeline twice from empty "
                "state and compare a digest of the results, weights and metrics, not the eye. If the digests differ, the "
                "cause is almost always an unseeded shuffle, set iteration order or an unfixed initial value, and the "
                "fix belongs at the source rather than in the comparison. Snapshot the configuration alongside the "
                "digest so a later reader knows exactly which settings produced it. This is the same discipline a "
                "shared experiment needs, where a colleague must be able to rerun your reported number unchanged. Today "
                "you write a seed-shuffle helper and a digest helper, shuffle the data twice with the same seed, print "
                "both digests, and assert they match; a mismatch is a genuine bug you must chase before shipping. A pass that is not tested is only a hope, and hope does not survive a reviewer."
            ),
            code=(
                'import hashlib\n'
                'import random\n'
                '\n'
                'DATA = [\n'
                '    ([1.0, 0.0], 3.0),\n'
                '    ([0.0, 1.0], 0.0),\n'
                '    ([1.0, 1.0], 2.0),\n'
                '    ([2.0, 1.0], 4.0),\n'
                ']\n'
                '\n'
                'def shuffled(rows, seed):\n'
                '    copy = list(rows)\n'
                '    random.Random(seed).shuffle(copy)\n'
                '    return copy\n'
                '\n'
                'def digest(value):\n'
                '    return hashlib.sha256(str(value).encode()).hexdigest()[:8]\n'
                '\n'
                'a = shuffled(DATA, 7)\n'
                'b = shuffled(DATA, 7)\n'
                'print("first order:", [x for x, _ in a][:3])\n'
                'print("digest a:", digest(a))\n'
                'print("digest b:", digest(b))\n'
                '\n'
                'assert a == b\n'
                'assert digest(a) == digest(b)\n'
                'print("same seed, same order, same result")'
            ),
            variant_b='shuffle with a different seed and show the digest changes, proving the seed is the only lever',
            variant_c='digest the final trained weights instead of the data and compare two identical training runs',
            mistakes=[
                "Using the global random module without seeding, so results shift between runs.",
                "Comparing outputs by eyeballing floats instead of hashing a deterministic representation.",
                "Fixing a reproducibility symptom in the comparison while leaving the unseeded source in place.",
            ],
            q1=(
                "What is usually the first cause of a reproducibility mismatch in a small ML pipeline?",
                "An unseeded shuffle or iteration over an unordered collection, so the order of examples changes between runs.",
            ),
            homework=(
                "Write `seeded_order(rows, seed)` returning a deterministically shuffled copy, and `fingerprint(value)` "
                "returning a short hash. Shuffle twice with the same seed, print both fingerprints, assert they match, "
                "and comment which line removes the randomness."
            ),
            patterns=["def ", "hashlib", "assert"],
            mapping=(
                "Reproducible runs are a prerequisite for debugging and publication; teams pin seeds and version data "
                "precisely so a reported number can be regenerated later."
            ),
        ),
        178: dict(
            topic="Build day: final review",
            idea=(
                "The final review is a checklist you execute, not a feeling, so today you write the pre-ship checks and "
                "run them as code. A capstone is ready when the data split is deterministic and the test rows were "
                "never touched during development, when the reported metric beats the baseline the scope named, when "
                "the core functions have passing assertions, when the training run is reproducible from a recorded "
                "configuration, and when the known edge cases are guarded. Each check is a boolean you can evaluate, "
                "and a small review function prints PASS or FAIL per line and counts the passes, so the result is a "
                "number rather than an opinion. Any failing check blocks the ship, and the lazy correct response is to "
                "fix the check rather than lower the bar. Re-run the whole suite from a clean interpreter as the actual "
                "final action, because a passing suite in a warm session can hide import-order and state bugs. Today "
                "you write the checklist as a dictionary of booleans, print each line, assert that all five pass, and "
                "treat any failure as the next task rather than a footnote. Then stop: a shipped capstone is better than a perfect unfinished one."
            ),
            code=(
                'CHECKS = {\n'
                '    "split is deterministic": True,\n'
                '    "test rows never touched": True,\n'
                '    "seed is recorded": True,\n'
                '    "metric beats baseline": True,\n'
                '    "edge cases guarded": True,\n'
                '}\n'
                '\n'
                'def review(checks):\n'
                '    passed = 0\n'
                '    for name in sorted(checks):\n'
                '        print(("PASS" if checks[name] else "FAIL"), name)\n'
                '        passed += 1 if checks[name] else 0\n'
                '    return passed\n'
                '\n'
                'score = review(CHECKS)\n'
                'print("passed", score, "of", len(CHECKS))\n'
                '\n'
                'assert score == len(CHECKS)\n'
                'print("do not ship until every check passes")'
            ),
            variant_b='flip one check to false and show the count dropping and the assertion firing',
            variant_c='add checks for a logged run id and a written limitation, then re-run the review',
            mistakes=[
                "Treating the review as a mood rather than a list of booleans that can fail.",
                "Skipping the clean-interpreter rerun, so stale state hides a real failure.",
                "Lowering a check to pass instead of fixing the underlying problem.",
            ],
            q1=(
                "Why evaluate the ship checklist as booleans in code rather than as a written list?",
                "Booleans can fail loudly and be counted, so the decision to ship is reproducible instead of a judgement call.",
            ),
            homework=(
                "Write `review(checks)` that prints PASS or FAIL per check, counts the passes and returns the score. Run "
                "it on a five-item checklist for your capstone, assert every check passes, and comment which check "
                "would catch a leaked test split."
            ),
            patterns=["def ", "assert", "print("],
            mapping=(
                "Release checklists in machine learning engineering gate deployment on exactly these properties: "
                "reproducibility, leakage, baseline comparison and input validation."
            ),
        ),
        179: dict(
            topic="Ship: retrospective and next steps",
            idea=(
                "A retrospective closes the project by turning experience into reusable rules, and it works best as a "
                "short structured template rather than a diary. Name what worked, with the evidence that shows it: the "
                "run that recovered the true weights, the held-out error below baseline. Name what failed or surprised "
                "you, also with evidence: the learning rate that diverged, the metric that looked good only because the "
                "split leaked. Then state what you will do differently next time, as concrete actions rather than "
                "resolutions, for example collect more rows, add a non-linear feature, keep a validation split. Finish "
                "with the next step this project most obviously enables, so the capstone feeds a larger goal instead of "
                "ending cold. The retrospective is only honest if each claim points at a logged number or a reproduced "
                "run, which is why it comes after the log and the reproducibility pass, not before. Today you encode a "
                "retro as a dictionary with worked, failed and next sections, print it as a labelled list, and assert "
                "it names at least one next step. This is the habit that compounds across every later project. Every later project inherits these rules instead of rediscovering them the hard way."
            ),
            code=(
                'RETRO = {\n'
                '    "worked": ["exact linear fit after 300 steps", "held-out error below baseline"],\n'
                '    "failed": ["a 0.5 learning rate diverged to huge values"],\n'
                '    "next": ["more rows", "a non-linear feature", "a validation split"],\n'
                '}\n'
                '\n'
                'def summarise(retro):\n'
                '    for section in ("worked", "failed", "next"):\n'
                '        print(section + ":")\n'
                '        for item in retro[section]:\n'
                '            print("  -", item)\n'
                '\n'
                'summarise(RETRO)\n'
                '\n'
                'assert RETRO["next"]\n'
                'assert len(RETRO["worked"]) >= 1\n'
                'print("a retrospective names evidence, not vibes")'
            ),
            variant_b='add a numbers section quoting the final test metric and reprint the retro',
            variant_c='move one failed item into worked after fixing it and note what evidence changed',
            mistakes=[
                "Writing a diary of feelings rather than claims backed by logged numbers.",
                "Listing next steps that are vague resolutions such as do better with data.",
                "Ending with no next step, so the project does not feed anything larger.",
            ],
            q1=(
                "Why must each retrospective claim point at a logged number or a reproduced run?",
                "Evidence makes the lesson checkable and reusable; without it the retrospective is opinion and cannot guide the next project.",
            ),
            homework=(
                "Write `summarise(retro)` that prints worked, failed and next sections as labelled lists, and "
                "`next_steps(retro)` returning the next list. Print your own retro, assert it names at least one next "
                "step, and comment which evidence supports the worked section."
            ),
            patterns=["def ", "for ", "print("],
            mapping=(
                "Teams hold post-mortems after launches for the same reason: capture what the evidence showed, then "
                "convert it into changes that make the next project cheaper."
            ),
        ),
    },
)
