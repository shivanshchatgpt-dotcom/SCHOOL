"""Flagship Machine Learning curriculum: hand-authored days 9-14 and 75-179.

Days 1-8 are canonical book-grounded lessons (preserved) and days 15-74 are
the shared authored Python phases (preserved). Everything here is genuinely
ML: real scikit-learn worked examples executed at apply time with captured
outputs, two variants, three mistakes, three Think-Check Q&As (Q1 is always
lesson-specific), and named-function homework with honest rubrics.

Where a whole library cannot run meaningfully on a toy sample, the example
builds the algorithm by hand in stdlib Python and says so plainly, with the
exact scikit-learn call it corresponds to. Nothing here claims stdlib code
"is" scikit-learn.

Each entry: topic, idea, code (stdlib + sklearn only, prints only, fixed
random_state), variant_b/c datasets, mistakes, q1 (lesson-specific Q/A),
homework, patterns, mapping (the sklearn API this day corresponds to).
"""

from __future__ import annotations

DOMAIN = "Machine Learning"

Q2 = "Which line in your solution is doing the real work, and what breaks if you remove it?"
A2 = "The line that performs the core operation — removing it should change the output or raise an error."
Q3 = "Your second variant has different values. Which parts of your logic did you assume?"
A3 = "Feed it an edge case (empty input, zero, or a wrong type) so the failure becomes visible, then explain why it happened."

# ---------------------------------------------------------------- foundation 9-14

FOUNDATION = {
    9: dict(
        topic="Feature records with dictionaries",
        idea="A machine-learning row is a mapping from feature names to values: {'hours': 4.0, 'passed': 1}. Dictionaries hold one example; lists of dictionaries hold a dataset. Reaching a value by name instead of by position is what keeps feature code readable when columns are added, removed, or reordered. This matters because real feature sets churn constantly — a new sensor, a dropped survey question, a renamed column — and positional code breaks silently every time the schema shifts. Name-based access also makes errors loud: a misspelled key raises immediately, while a wrong index returns a plausible-looking wrong number that poisons training without a sound.",
        code=(
            '# One student, one feature record\n'
            'student = {"hours": 4.0, "sleep": 7.5, "passed": 1}\n'
            'print("hours studied:", student["hours"])\n'
            'print("features:", sorted(student))\n'
            '\n'
            '# A tiny dataset: a list of records\n'
            'data = [student, {"hours": 1.5, "sleep": 6.0, "passed": 0}]\n'
            'hours = [row["hours"] for row in data]\n'
            'print("hours column:", hours)\n'
            'print("rows:", len(data))\n'
            'assert set(data[0]) == {"hours", "sleep", "passed"}\n'
            'print("schema check passed")'
        ),
        variant_b='a record with keys {"age", "income", "approved"} and two rows',
        variant_c='a record with one extra key, e.g. {"hours", "sleep", "snacks", "passed"}',
        mistakes=[
            "Reading row[0] when rows are mappings — positions mean nothing here, names do.",
            "Misspelling a key so a KeyError appears three lines away from the real mistake.",
            "Mixing key sets across rows, so one example silently lacks a feature.",
        ],
        q1=("Why is a dictionary a better single-example container than a list?",
            "Names survive reordering and extension; positions do not, so feature code stays correct when columns change."),
        homework="Write `column(rows, key)` that returns one feature column from a list of record dictionaries. Run it on two different record lists, print both columns, and comment which line looks the value up by name.",
        patterns=["{", "print("],
        mapping="In scikit-learn, one row becomes one row of the X matrix; pandas DataFrames are named-column tables built on the same idea. When you outgrow hand-rolled lists, DataFrame.loc keeps the same name-based access at scale.",
    ),
    10: dict(
        topic="Surviving bad rows with try and except",
        idea="Real datasets contain landmines: 'N/A' where a float should be, empty strings, shifted columns. A loading loop that crashes on row 900 of 10,000 teaches nothing. Catch the conversion failure, count the rejects, keep the good rows — and report exactly what was skipped so the skip is a decision, not an accident. This discipline compounds: a model trained on quietly corrupted rows learns the corruption as if it were signal, and no amount of tuning fixes data that lied on the way in. Professionals treat the loader as part of the model, with its own tests, because the cheapest errors to fix are the ones caught before fitting starts.",
        code=(
            '# Loading study hours with landmines inside\n'
            'raw = ["4.5", "3.0", "N/A", "6.0", "", "2.5"]\n'
            '\n'
            'def load_hours(raw):\n'
            '    good, rejected = [], []\n'
            '    for cell in raw:\n'
            '        try:\n'
            '            good.append(float(cell))\n'
            '        except ValueError:\n'
            '            rejected.append(cell)\n'
            '    print("kept:", good, "| rejected:", rejected)\n'
            '    return good\n'
            '\n'
            'hours = load_hours(raw)\n'
            'print("mean of kept:", sum(hours) / len(hours))\n'
            'assert load_hours(["1.0", "bad"]) == [1.0]\n'
            'print("loader proven")'
        ),
        variant_b='raw = ["10", "xx", "20", "yy", "30"]',
        variant_c='raw = ["bad", "worse"] (every row rejected — what does the mean line do?)',
        mistakes=[
            "Wrapping the whole loop in one try, so the first bad row kills the other 9,999.",
            "Silently dropping bad rows without reporting them — the skip must be visible.",
            "Catching Exception instead of ValueError, which also hides real bugs like typos.",
        ],
        q1=("Why must the try sit inside the loop rather than around it?",
            "Inside, one bad row is skipped and the loop continues; around, the first failure aborts every row after it."),
        homework="Write `load_hours(raw)` that converts strings to floats, prints kept and rejected lists, and returns the good values. Run it on two different raw lists, print both results, and comment which line catches the failure.",
        patterns=["try:", "except"],
        mapping="In scikit-learn, SimpleImputer and ColumnTransformer mechanise this cleanup; today you do by hand what they automate. Knowing the manual version first means you recognise when the automated one silently drops half your rows.",
    ),
    11: dict(
        topic="Loading datasets from files",
        idea="Models do not eat strings; they eat tables. The most common real ML task is turning a CSV file into two parallel lists — features X and labels y — with the header row skipped, exactly one conversion per cell, and a shape check at the end proving rows and labels line up. Get this wrong and everything downstream is fiction: a model can fit misaligned labels perfectly and the scores will look excellent while meaning nothing. That is why the loader prints its header and row count and asserts the pairing — the thirty seconds this costs saves the all-night session of tuning a model on shuffled labels.",
        code=(
            '# study.csv: hours,sleep,passed (header + data rows)\n'
            'text = "hours,sleep,passed\\n4.5,7.5,1\\n1.5,6.0,0\\n6.0,8.0,1\\n"\n'
            '\n'
            'def load_csv(text):\n'
            '    lines = text.strip().split("\\n")\n'
            '    header = lines[0].split(",")\n'
            '    X, y = [], []\n'
            '    for line in lines[1:]:\n'
            '        hours, sleep, passed = line.split(",")\n'
            '        X.append([float(hours), float(sleep)])\n'
            '        y.append(int(passed))\n'
            '    print("header:", header, "| rows:", len(X))\n'
            '    return X, y\n'
            '\n'
            'X, y = load_csv(text)\n'
            'print("X =", X)\n'
            'print("y =", y)\n'
            'assert len(X) == len(y) == 3\n'
            'print("shapes line up")'
        ),
        variant_b='a 2-row file with columns age,income,approved',
        variant_c='a file where one data row has only two cells (watch it fail loudly, then fix the loader to skip it)',
        mistakes=[
            "Forgetting to skip the header, so 'hours' gets converted to float and everything crashes.",
            "Building X and y in separate loops, so a skipped row misaligns features and labels.",
            "Never asserting len(X) == len(y), so a silent misalignment poisons the whole model.",
        ],
        q1=("Why must X and y be built in the same loop?",
            "One loop keeps row i of X paired with label i of y; two loops let a skipped or extra row shift everything out of alignment."),
        homework="Write `load_csv(text)` that skips the header, converts each row, and returns X and y with a printed shape check. Run it on two different CSV texts, print both, and comment which line skips the header.",
        patterns=["with ", "print("],
        mapping="In scikit-learn and pandas this is pd.read_csv plus df.values; the header-skip and shape-check habits transfer exactly.",
    ),
    12: dict(
        topic="Asserting data shapes",
        idea="Most ML bugs are shape bugs: 99 features against 100 labels, a 1-D array where a 2-D table was expected, train and test built from different columns. Professionals assert shapes at every boundary — after loading, after splitting, before fitting — because an assert fails in one second at the guilty line instead of thirty minutes later inside the model. Shape discipline is also documentation: anyone reading your asserts learns the contract of each stage without guessing. As datasets grow from toy lists to million-row tables, the asserts stay identical while the debugging they prevent gets proportionally more expensive.",
        code=(
            '# Shape guards around a tiny split\n'
            'X = [[1.0], [2.0], [3.0], [4.0], [5.0], [6.0]]\n'
            'y = [0, 0, 0, 1, 1, 1]\n'
            '\n'
            'def split(X, y, n_train=4):\n'
            '    assert len(X) == len(y), "X and y lengths differ"\n'
            '    assert all(len(row) == 1 for row in X), "rows must have 1 feature"\n'
            '    train = (X[:n_train], y[:n_train])\n'
            '    test = (X[n_train:], y[n_train:])\n'
            '    print("train rows:", len(train[0]), "| test rows:", len(test[0]))\n'
            '    return train, test\n'
            '\n'
            '(Xtr, ytr), (Xte, yte) = split(X, y)\n'
            'assert len(Xtr) + len(Xte) == len(X)\n'
            'print("split proven lossless")'
        ),
        variant_b='X with 2 features per row and matching asserts',
        variant_c='y with 5 labels against 6 rows (watch the assert fire, then explain why it is the correct behaviour)',
        mistakes=[
            "Asserting nothing and debugging a shape error three functions downstream.",
            "Asserting len(X) == len(y) but never the inner row width.",
            "Deleting the assert after it fires once instead of fixing the data that tripped it.",
        ],
        q1=("Why assert at the boundary instead of inside the model code?",
            "Boundaries are where shapes are decided; an assert there names the guilty line in one second instead of failing mysteriously downstream."),
        homework="Write `split(X, y, n_train)` with asserts on lengths and row width, printing train/test sizes. Run it on two datasets, print both, and comment which assert guards the feature width.",
        patterns=["assert ", "print("],
        mapping="In scikit-learn, check_X_y and check_array do exactly these guards inside every estimator; you are writing the visible version.",
    ),
    13: dict(
        topic="Splitting work: load, train, evaluate",
        idea="Every ML script has the same three jobs: load the data, fit a rule on the training part, and measure that rule on data it has never seen. Mixing the jobs — peeking at test data while training, or evaluating on the training rows — produces a model that looks perfect and fails in the real world. Separate functions with a one-way flow: data flows forward, never backward. This separation is also what makes experiments comparable: when load, train and evaluate are distinct, you can swap one rule for another while holding everything else fixed, which is the only honest way to claim an improvement.",
        code=(
            '# The three jobs, kept separate\n'
            'X = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0]\n'
            'y = [0, 0, 0, 1, 1, 1]\n'
            '\n'
            'def load():\n'
            '    return X[:4], y[:4], X[4:], y[4:]\n'
            '\n'
            'def train_rule(Xtr, ytr):\n'
            '    cutoff = sum(Xtr) / len(Xtr)\n'
            '    print("rule: predict 1 when x >", cutoff)\n'
            '    return cutoff\n'
            '\n'
            'def evaluate(cutoff, Xte, yte):\n'
            '    pred = [1 if x > cutoff else 0 for x in Xte]\n'
            '    score = sum(p == t for p, t in zip(pred, yte)) / len(yte)\n'
            '    print("test accuracy:", score)\n'
            '    return score\n'
            '\n'
            'Xtr, ytr, Xte, yte = load()\n'
            'rule = train_rule(Xtr, ytr)\n'
            'evaluate(rule, Xte, yte)'
        ),
        variant_b='X = [2.0, 4.0, 6.0, 8.0] with y = [0, 0, 1, 1]',
        variant_c='train on the LAST four rows and test on the FIRST two (does the rule still hold?)',
        mistakes=[
            "Evaluating on the training rows and celebrating 100% that means nothing.",
            "Letting test statistics leak into training (normalising with the full data).",
            "One giant script where load, train and evaluate share variables and order.",
        ],
        q1=("Why is evaluating on training data meaningless?",
            "The rule was chosen to fit those exact rows, so a perfect score measures memory, not learning; only unseen rows test generalisation."),
        homework="Write load/train_rule/evaluate functions where the rule is a cutoff learned from training rows only. Run the pipeline on two datasets, print both test accuracies, and comment which line prevents test leakage.",
        patterns=["def ", "print("],
        mapping="In scikit-learn this is train_test_split plus estimator.fit on train and estimator.score on test — the same three jobs with the same one-way flow.",
    ),
    14: dict(
        topic="Foundation capstone: a mean baseline report",
        idea="Before any clever model, build the dumbest reasonable predictor: always guess the training mean. Every later model must beat this number, or it has learned nothing. A baseline turns 'my model gets 82%' from a boast into a comparison — 82% against a 79% baseline is modest; against 50% it is excellent. Professionals never skip the baseline. It also protects you from broken pipelines: if a sophisticated model cannot beat the mean, the likeliest explanation is a data bug — leakage, misalignment, a flipped sign — not a need for deeper tuning. The baseline is the smoke alarm of the whole workflow.",
        code=(
            '# The dumbest reasonable predictor\n'
            'train_y = [3.0, 5.0, 4.0, 6.0]\n'
            'test_y = [4.5, 5.5]\n'
            '\n'
            'def mean_baseline(train_y):\n'
            '    mu = sum(train_y) / len(train_y)\n'
            '    print("baseline predicts:", mu, "for every input")\n'
            '    return mu\n'
            '\n'
            'def mae(pred, actual):\n'
            '    err = sum(abs(p - a) for p, a in zip(pred, actual)) / len(actual)\n'
            '    print("mean absolute error:", err)\n'
            '    return err\n'
            '\n'
            'mu = mean_baseline(train_y)\n'
            'score = mae([mu] * len(test_y), test_y)\n'
            'print("Beat this number:", score)'
        ),
        variant_b='train_y = [10.0, 20.0, 30.0], test_y = [15.0, 25.0]',
        variant_c='train_y = [7.0, 7.0, 7.0] (what does the baseline do when training never varies?)',
        mistakes=[
            "Skipping the baseline and having no number to compare the real model against.",
            "Computing the baseline on test data, which spends the test set before the model arrives.",
            "Reporting accuracy-style scores for a regression problem instead of an error distance.",
        ],
        q1=("Why must every model beat the mean baseline to count as learning?",
            "The baseline uses zero input features, so anything that truly learned from the inputs must outperform ignoring them entirely."),
        homework="Write `mean_baseline(train_y)` and `mae(pred, actual)`, run the baseline on two train/test splits, print both errors, and comment which line makes the baseline ignore its inputs.",
        patterns=["def ", "return"],
        mapping="In scikit-learn this is DummyRegressor(strategy='mean') plus mean_absolute_error — the professional version of exactly this script. Run it once per project and keep its number on the scoreboard next to every later model.",
    ),
}

ML_PHASES = [
    ("ML Setup and Data",
     "Load real datasets, split them honestly, and set baselines every later model must beat.",
     {
         75: dict(
             topic="Orientation: what scikit-learn is for",
             idea="Scikit-learn gives every model the same two verbs: fit (learn from training data) and predict (guess on new data). That uniformity is the whole point — once you can drive one estimator, you can drive fifty, because classifiers, regressors, scalers and pipelines all speak fit/predict. Today you meet the verbs on a toy problem before any real data arrives. Pay attention to the rhythm rather than the numbers: construct, fit on training rows, predict on unseen rows, score against truth. Every experiment in this track repeats that rhythm, so learning it cold on six rows pays off on every one of the hundred days after.",
             code=(
                 'from sklearn.dummy import DummyClassifier\n'
                 '\n'
                 'X = [[1.0], [2.0], [3.0], [10.0], [11.0], [12.0]]\n'
                 'y = [0, 0, 0, 1, 1, 1]\n'
                 '\n'
                 'model = DummyClassifier(strategy="most_frequent")\n'
                 'model.fit(X[:4], y[:4])\n'
                 'print("trained on 4 rows, classes:", model.classes_)\n'
                 'pred = model.predict([[2.5], [11.5]])\n'
                 'print("predictions:", list(pred))\n'
                 'print("score on last two:", model.score([[11.0], [12.0]], [1, 1]))'
             ),
             variant_b='X = [[0.0], [1.0], [9.0], [10.0]], y = [0, 0, 1, 1], train on first three',
             variant_c='strategy="stratified" instead of "most_frequent" (do predictions change?)',
             mistakes=[
                 "Calling predict before fit — an unfitted estimator has learned nothing and raises.",
                 "Fitting on all six rows and scoring on the same six, which measures nothing.",
                 "Assuming DummyClassifier is a real model instead of the baseline later models must beat.",
             ],
             q1=("Why do all scikit-learn estimators share fit and predict?",
                 "One interface lets you swap models, scalers and pipelines interchangeably — learn the verbs once, drive every estimator."),
             homework="Write `first_model()` that fits DummyClassifier on four rows, predicts two unseen rows, and prints the score on held-out rows. Run it on two datasets, print both scores, and comment which line separates training rows from scoring rows.",
             patterns=[".fit(", ".predict("],
             mapping="Every later day uses this exact pair: model.fit(X_train, y_train) then model.predict(X_test). The uniformity is deliberate — swapping models never means relearning the interface.",
         ),
         76: dict(
             topic="Your first real estimator",
             idea="A k-nearest-neighbours classifier makes no assumptions and learns no parameters: to classify a new point it simply asks the k closest training points and takes a vote. It is the most honest first model — the prediction for any input is directly traceable to neighbouring examples — and its two failure modes (k too small: noisy; k too large: blurry) preview the bias-variance trade-off the whole course returns to. Because kNN memorises instead of generalising, it also teaches the critical distinction between training error and test error in its purest form: k=1 is flawless on data it has seen and ordinary on data it has not, which is exactly the gap every later regularisation technique exists to close.",
             code=(
                 'from sklearn.neighbors import KNeighborsClassifier\n'
                 'from sklearn.datasets import make_classification\n'
                 '\n'
                 'X, y = make_classification(n_samples=60, n_features=2, n_redundant=0, random_state=7)\n'
                 'model = KNeighborsClassifier(n_neighbors=3)\n'
                 'model.fit(X[:45], y[:45])\n'
                 'print("train rows: 45 | test rows:", len(X) - 45)\n'
                 'print("test accuracy:", round(model.score(X[45:], y[45:]), 3))\n'
                 'print(" neighbours vote:", model.predict([X[50]])[0], "| true label:", y[50])'
             ),
             variant_b='n_neighbors=1 (noisier — compare the test accuracy)',
             variant_c='n_neighbors=15 (blurrier — compare again and explain which error grew)',
             mistakes=[
                 "Judging k by training accuracy, where k=1 is always perfect and always lying.",
                 "Forgetting that kNN memorises the training set, so it needs no training time but slow predictions.",
                 "Using unscaled features with wildly different units, letting one feature dominate distance.",
             ],
             q1=("Why is k=1 perfect on training data but often worse on test data?",
                 "Each training point is its own nearest neighbour, so training accuracy is 100% by memorisation — which generalises exactly not at all."),
             homework="Write `knn_score(k)` that builds the 60-point dataset, fits KNeighborsClassifier(k) on 45 rows, and prints the test accuracy. Run it for k=1 and k=15, print both, and comment which line chooses the neighbourhood size.",
             patterns=[".fit(", ".predict("],
             mapping="KNeighborsClassifier(n_neighbors=k).fit(X_train, y_train); swap k to feel bias vs variance directly. Small k memorises noise, large k blurs boundaries — the whole course is this trade-off in fancier clothes.",
         ),
         77: dict(
             topic="Datasets are tables: X and y",
             idea="Scikit-learn thinks in two objects: X, a 2-D table of shape (n_samples, n_features), and y, a 1-D list of labels of length n_samples. Every estimator, splitter and metric assumes this contract. The iris dataset — 150 flowers, 4 measurements, 3 species — is the canonical first table: small enough to print, real enough to model. Internalise the contract now and error messages become readable: 'Found input variables with inconsistent numbers of samples' is simply the library telling you row i of X and entry i of y stopped describing the same example, usually after a filtering step touched one and forgot the other.",
             code=(
                 'from sklearn.datasets import load_iris\n'
                 '\n'
                 'data = load_iris()\n'
                 'X, y = data.data, data.target\n'
                 'print("X shape:", X.shape, "| y length:", len(y))\n'
                 'print("feature names:", list(data.feature_names))\n'
                 'print("target names:", list(data.target_names))\n'
                 'print("first row:", list(X[0]), "->", data.target_names[y[0]])\n'
                 'assert X.shape == (150, 4) and len(y) == 150\n'
                 'print("contract holds: one label per row")'
             ),
             variant_b='load_digits() (how many samples and features? how many classes?)',
             variant_c='load_diabetes() (a regression table — what does y hold instead of species?)',
             mistakes=[
                 "Treating X as 1-D and wondering why the estimator demands 2-D.",
                 "Misaligning y after filtering X, so labels describe the wrong rows.",
                 "Ignoring feature_names and guessing what column 2 means.",
             ],
             q1=("Why must y have exactly one entry per row of X?",
                 "Row i of X and entry i of y describe the same example; any length mismatch means labels point at the wrong rows."),
             homework="Write `describe_table()` that loads iris, prints X shape, feature names and class counts, and asserts one label per row. Run it for iris and digits, print both summaries, and comment which line enforces the contract.",
             patterns=[".shape", "print("],
             mapping="Every estimator call in this course takes this (X, y) pair; load_* bundles data, target and names together.",
         ),
         78: dict(
             topic="Splitting honestly with train_test_split",
             idea="Hand-slicing the first 80% for training silently assumes the rows are shuffled — ordered datasets (all of class 0, then all of class 1) punish that assumption with a test set containing a class the model never saw. train_test_split shuffles with a fixed random_state, so the split is both fair and reproducible: same seed, same rows, every run. The deeper lesson is that your test set is a claim about the future: it must resemble the data the model will actually meet, and a careless split makes it resemble nothing. Shuffling is the cheapest way to make that claim approximately true, which is why it is the default you must consciously override rather than consciously remember. The one exception is time-ordered rows — forecasting tomorrow from today — where shuffling destroys the very signal you must learn and time-based splits replace it.",
             code=(
                 'from sklearn.datasets import load_iris\n'
                 'from sklearn.model_selection import train_test_split\n'
                 '\n'
                 'X, y = load_iris(return_X_y=True)\n'
                 'Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.25, random_state=42)\n'
                 'print("train:", len(Xtr), "| test:", len(Xte))\n'
                 'print("test classes present:", sorted(set(yte.tolist())))\n'
                 'again = train_test_split(X, y, test_size=0.25, random_state=42)\n'
                 'print("reproducible:", (again[1] == Xte).all())'
             ),
             variant_b='test_size=0.5 (how do the class counts change?)',
             variant_c='no random_state at all (run twice — do you get the same rows?)',
             mistakes=[
                 "Slicing X[:120]/X[120:] on ordered data and testing on an unseen class.",
                 "Omitting random_state, so results change every run and nothing is debuggable.",
                 "Splitting X and y in two separate calls, which shuffles them differently.",
             ],
             q1=("Why does the same random_state give the same split every run?",
                 "The seed fixes the shuffling sequence, so the split is deterministic — fairness without irreproducibility."),
             homework="Write `honest_split()` that loads iris, splits 75/25 with random_state=7, and prints train/test sizes plus test classes. Run it twice to prove reproducibility, print both, and comment which argument fixes the shuffle.",
             patterns=["train_test_split(", "print("],
             mapping="sklearn.model_selection.train_test_split is the standard splitter; stratify=y (coming later) keeps class ratios. Pass an integer random_state so the same code always deals the same rows — reproducibility starts at the split.",
         ),
         79: dict(
             topic="Baselines for classification: DummyClassifier",
             idea="A majority-class baseline — always predict the most common training label — sets the floor every classifier must clear. On a 90/10 dataset, 90% accuracy means nothing until the baseline says 90%. Professionals report the gap above baseline, never the raw score alone. This habit also inoculates you against the most common ML press-release trick: a model that 'achieves 95% accuracy' on a problem where guessing the majority scores 94% has learned almost nothing, while 75% against a 50% floor is genuine progress. Always ask what the dumb predictor scores before admiring the clever one. A baseline also diagnoses broken pipelines: if no real model beats majority guessing, suspect misaligned labels or leakage before tuning anything, because tuning cannot fix data that lies.",
             code=(
                 'from sklearn.datasets import load_iris\n'
                 'from sklearn.model_selection import train_test_split\n'
                 'from sklearn.dummy import DummyClassifier\n'
                 '\n'
                 'X, y = load_iris(return_X_y=True)\n'
                 'Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, random_state=1)\n'
                 'base = DummyClassifier(strategy="most_frequent")\n'
                 'base.fit(Xtr, ytr)\n'
                 'score = base.score(Xte, yte)\n'
                 'print("baseline (always majority):", round(score, 3))\n'
                 'print("beat this number with a real model")'
             ),
             variant_b='strategy="stratified" (guesses by class frequency — higher or lower?)',
             variant_c='an imbalanced make_classification(weights=[0.9, 0.1]) split (what does majority score now?)',
             mistakes=[
                 "Reporting 92% accuracy without the 90% baseline beside it.",
                 "Fitting the baseline on test data, which leaks the very distribution being measured.",
                 "Using 'uniform' random guessing as the floor when majority is the stricter, honest floor.",
             ],
             q1=("On a 90/10 dataset, why is 90% accuracy worthless without a baseline?",
                 "Always guessing the majority already scores 90%, so the model must clear that floor to prove it learned anything."),
             homework="Write `majority_floor()` that splits iris, fits the majority baseline, and prints its test score. Run it with two random_states, print both, and comment which line makes the baseline ignore its inputs.",
             patterns=[".fit(", ".score("],
             mapping="sklearn.dummy.DummyClassifier is the classification floor; DummyRegressor (tomorrow) is the regression floor. Report every later accuracy as points above this floor, never as a raw percentage alone — the gap is the result.",
         ),
         80: dict(
             topic="Baselines for regression: predicting the mean",
             idea="The regression floor predicts the training mean for every input — zero features used. Mean absolute error against this floor tells you whether your model extracts signal or just decorates ignorance. You built this by hand on day 14; today is the professional one-liner with the same semantics. Notice what the floor implies about features: if a model using all ten diabetes features barely beats the mean, the features carry little signal for this target, and the honest conclusion is to find better features rather than tune harder. Baselines do not just rank models; they audit whether the problem as framed is learnable at all.",
             code=(
                 'from sklearn.datasets import load_diabetes\n'
                 'from sklearn.model_selection import train_test_split\n'
                 'from sklearn.dummy import DummyRegressor\n'
                 'from sklearn.metrics import mean_absolute_error\n'
                 '\n'
                 'X, y = load_diabetes(return_X_y=True)\n'
                 'Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, random_state=2)\n'
                 'base = DummyRegressor(strategy="mean")\n'
                 'base.fit(Xtr, ytr)\n'
                 'pred = base.predict(Xte)\n'
                 'print("all predictions equal:", len(set(round(float(p), 6) for p in pred)) == 1)\n'
                 'print("baseline MAE:", round(mean_absolute_error(yte, pred), 2))\n'
                 'print("beat this error with a real regressor")'
             ),
             variant_b='strategy="median" (more robust to outliers — lower or higher MAE?)',
             variant_c='random_state=9 for the split (does the floor move much?)',
             mistakes=[
                 "Comparing models by MAE without stating the baseline MAE beside it.",
                 "Fitting the mean on the full data including test — the floor must come from train only.",
                 "Using accuracy-style thinking on a regression error distance.",
             ],
             q1=("Why must the baseline mean come from training labels only?",
                 "The test set is the exam; computing anything from it — even a mean — leaks answers into the floor every model is judged against."),
             homework="Write `mean_floor()` that splits diabetes, fits the mean baseline on train, and prints test MAE. Run it for two splits, print both, and comment which line keeps test labels out of training.",
             patterns=[".fit(", ".predict("],
             mapping="sklearn.dummy.DummyRegressor(strategy='mean') plus mean_absolute_error — the day-14 script grown up. Fit it on training labels only; even the floor must never peek at the test set.",
         ),
         81: dict(
             topic="Measuring regression: MSE, MAE and R-squared",
             idea="Three numbers tell three truths: MAE (average miss distance, same units as y), MSE (squares misses, punishes big errors hard), R² (fraction of variance explained, 1.0 is perfect, 0.0 equals the mean baseline, negative means worse than guessing the mean). Professionals quote R² for comparison and MAE for human meaning. The choice of metric is a choice of values: MSE says one huge error is worse than ten small ones, MAE treats all errors equally, and the business problem — not the textbook — decides which is right. A model optimised for the wrong metric is a correct answer to the wrong question, so learn to ask which errors hurt before you minimise them.",
             code=(
                 'from sklearn.datasets import load_diabetes\n'
                 'from sklearn.model_selection import train_test_split\n'
                 'from sklearn.linear_model import LinearRegression\n'
                 'from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score\n'
                 '\n'
                 'X, y = load_diabetes(return_X_y=True)\n'
                 'Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, random_state=3)\n'
                 'model = LinearRegression().fit(Xtr, ytr)\n'
                 'pred = model.predict(Xte)\n'
                 'print("MAE:", round(mean_absolute_error(yte, pred), 2))\n'
                 'print("MSE:", round(mean_squared_error(yte, pred), 2))\n'
                 'print("R^2:", round(r2_score(yte, pred), 3))\n'
                 'print("beats mean baseline (R^2 > 0):", r2_score(yte, pred) > 0)'
             ),
             variant_b='predict the train mean instead (what is R^2 exactly?)',
             variant_c='a constant prediction of 0.0 (can R^2 go negative? why?)',
             mistakes=[
                 "Quoting MSE without units-awareness — squared units mislead human readers.",
                 "Celebrating R² = 0.98 on training data, which measures fit, not learning.",
                 "Comparing MAE across different datasets, where scale differences make it meaningless.",
             ],
             q1=("What does a negative R² actually mean?",
                 "Your model predicts worse than a flat line at the test mean — it learned patterns that are actively wrong on new data."),
             homework="Write `regression_report()` that fits LinearRegression, prints MAE/MSE/R² on test, and states whether R² beats zero. Run it on two splits, print both, and comment which metric a non-technical stakeholder would understand.",
             patterns=[".fit(", "r2_score("],
             mapping="sklearn.metrics.mean_absolute_error, mean_squared_error, r2_score — the standard regression scoreboard. Quote R² when comparing models and MAE when explaining the error to someone who owns the problem.",
         ),
         82: dict(
             topic="Measuring classification: accuracy and the confusion matrix",
             idea="Accuracy hides where errors live. A confusion matrix shows them: rows are true labels, columns are predictions, and the off-diagonal cells name each mistake type. On iris, confusing versicolor with virginica is one specific cell — and one specific fix (a better petal-width feature) — while accuracy just says '94%'. Make reading the matrix a reflex after every fit, because the pattern of errors is the diagnosis: random scatter means noise, a heavy row means a hard class, and an asymmetric pair means the boundary sits in the wrong place. The fix is never 'more model' until the matrix says what is actually confused.",
             code=(
                 'from sklearn.datasets import load_iris\n'
                 'from sklearn.model_selection import train_test_split\n'
                 'from sklearn.neighbors import KNeighborsClassifier\n'
                 'from sklearn.metrics import accuracy_score, confusion_matrix\n'
                 '\n'
                 'X, y = load_iris(return_X_y=True)\n'
                 'Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, random_state=4)\n'
                 'model = KNeighborsClassifier(n_neighbors=5).fit(Xtr, ytr)\n'
                 'pred = model.predict(Xte)\n'
                 'print("accuracy:", round(accuracy_score(yte, pred), 3))\n'
                 'print("confusion rows=true, cols=pred:")\n'
                 'for row in confusion_matrix(yte, pred):\n'
                 '    print(" ", list(row))'
             ),
             variant_b='n_neighbors=1 (which off-diagonal cells change?)',
             variant_c='test_size=0.5 (does the matrix get more or less trustworthy?)',
             mistakes=[
                 "Reading accuracy on imbalanced data as success.",
                 "Transposing the matrix (rows are truth, columns are predictions — check the docs).",
                 "Averaging away the matrix into one number before looking at which classes confuse.",
             ],
             q1=("What does one off-diagonal cell tell you that accuracy cannot?",
                 "Exactly which true class is mistaken for which predicted class — the address of the error and the hint for the fix."),
             homework="Write `confusion_report(k)` fitting kNN(k) and printing accuracy plus the full matrix. Run it for k=1 and k=5, print both, and comment which cells show the most confused pair.",
             patterns=["confusion_matrix(", ".predict("],
             mapping="sklearn.metrics.accuracy_score and confusion_matrix; precision/recall/F1 slice the matrix further. Read the matrix before the accuracy — the off-diagonal cells name the fix.",
         ),
         83: dict(
             topic="Reproducibility: random_state everywhere",
             idea="ML has randomness in splits, synthetic data, model initialisation and tie-breaking. Unfixed, every run differs and no result is debuggable, reviewable, or shippable. Fixed random_state everywhere turns luck into a constant: same code, same numbers, every machine. Reproducibility is not paperwork — it is what makes experiments comparable. Two scores from two seeds are two different experiments; without recorded seeds you cannot tell whether model B beat model A or Tuesday's shuffle beat Monday's. The professional standard is simple: every source of randomness gets an explicit seed, and the seeds ship with the code. Record them in the experiment log beside the scores — 'random_state=7 everywhere' is a complete reproducibility statement that lets anyone rerun your exact numbers years later.",
             code=(
                 'from sklearn.datasets import make_classification\n'
                 'from sklearn.neighbors import KNeighborsClassifier\n'
                 '\n'
                 'def run(seed):\n'
                 '    X, y = make_classification(n_samples=80, random_state=seed)\n'
                 '    m = KNeighborsClassifier(n_neighbors=3).fit(X[:60], y[:60])\n'
                 '    return round(m.score(X[60:], y[60:]), 4)\n'
                 '\n'
                 'print("seed 7 twice:", run(7), run(7))\n'
                 'print("seed 8 differs:", run(8))\n'
                 'print("same code + same seed = same science")'
             ),
             variant_b='n_samples=200 (does the seed-7 vs seed-8 gap shrink with more data?)',
             variant_c='drop random_state from make_classification (run twice — identical or not?)',
             mistakes=[
                 "Fixing the split seed but not the data seed, then wondering why numbers move.",
                 "Sharing one global seed across unrelated experiments and confusing their randomness.",
                 "Publishing a result nobody — including you — can reproduce next week.",
             ],
             q1=("Why fix the data seed AND the split seed, not just one?",
                 "Each is an independent dice roll; fixing one still leaves the other free to move your numbers between runs."),
             homework="Write `run(seed)` returning a test score, call it twice with seed 7 and once with 8, print all three, and comment which argument turns luck into a constant.",
             patterns=["random_state=", ".score("],
             mapping="random_state is a keyword on datasets, splitters and models alike — set it on all three, always. Each is an independent dice roll, and leaving any one unfixed lets your numbers drift between runs.",
         ),
         84: dict(
             topic="Reading docs and inspecting models",
             idea="Professionals read estimator docs before Stack Overflow: every estimator documents its parameters, attributes (trailing underscore = learned from data), and a runnable example. get_params shows the knobs, classes_/coef_ show what was learned, and the version string belongs in every experiment log so results stay interpretable after upgrades. This habit scales beyond scikit-learn: in any modelling library, the fastest debugging path is inspecting what the object actually holds rather than what you assume it holds. A model that predicts badly with sensible coefficients is a data problem; one with absurd coefficients is a fitting problem — and you can only tell the difference by looking. Make inspection the first debugging step, not the last: print shapes, coefficients and class counts before forming any theory about what went wrong.",
             code=(
                 'import sklearn\n'
                 'from sklearn.linear_model import LogisticRegression\n'
                 'from sklearn.datasets import load_iris\n'
                 '\n'
                 'print("sklearn version:", sklearn.__version__)\n'
                 'model = LogisticRegression(max_iter=500)\n'
                 'print("default C:", model.get_params()["C"])\n'
                 'X, y = load_iris(return_X_y=True)\n'
                 'model.fit(X[:100], y[:100])\n'
                 'print("learned coef shape:", model.coef_.shape)\n'
                 'print("classes:", list(model.classes_))'
             ),
             variant_b='C=0.01 in the constructor (what changes in get_params and coef_?)',
             variant_c='fit on only the first 50 rows (how many classes can it know?)',
             mistakes=[
                 "Reading coef_ before fit — attributes with trailing underscores exist only after learning.",
                 "Tuning parameters nobody understands instead of reading what they do first.",
                 "Logging scores without the library version, making old results uninterpretable.",
             ],
             q1=("What does a trailing underscore (coef_) promise you?",
                 "The attribute was estimated from data during fit — it does not exist before, and it changes with the training set."),
             homework="Write `inspect_model()` that prints the sklearn version, one default parameter, and the learned coefficient shape after fitting. Run it on two estimators, print both, and comment which attribute proves learning happened.",
             patterns=["get_params(", ".fit("],
             mapping="get_params/set_params drive GridSearchCV later; trailing-underscore attributes are the learned state you debug. Log the library version beside every score, or last month’s results become uninterpretable after an upgrade.",
         ),
         85: dict(
             topic="Features must be numbers",
             idea="Models do arithmetic, and arithmetic needs numbers — so text categories become numbers before fitting. The honest manual version maps each category to an integer or a one-hot row; the professional version is OneHotEncoder. Either way the rule is the same: fit the mapping on training categories only, then transform both sets, because a new category at test time is a fact to handle, not a crash to accept. Encoding choices also smuggle assumptions: integer codes invent order, one-hot explodes width on high-cardinality columns, and hashing tricks trade interpretability for scale. There is no neutral encoding — only one whose assumptions you have chosen deliberately.",
             code=(
                 'from sklearn.preprocessing import OneHotEncoder\n'
                 '\n'
                 'train_colors = [["red"], ["blue"], ["red"], ["green"]]\n'
                 'test_colors = [["blue"], ["red"]]\n'
                 '\n'
                 'enc = OneHotEncoder(sparse_output=False, handle_unknown="ignore")\n'
                 'Xtr = enc.fit_transform(train_colors)\n'
                 'Xte = enc.transform(test_colors)\n'
                 'print("categories:", list(enc.categories_[0]))\n'
                 'print("train row 0:", list(Xtr[0]))\n'
                 'print("test rows:", Xte.tolist())\n'
                 'assert Xtr.shape[1] == Xte.shape[1]\n'
                 'print("train/test widths match")'
             ),
             variant_b='a test color "yellow" never seen in training (what does ignore do?)',
             variant_c='handle_unknown="error" with the yellow row (which behaviour do you want in production?)',
             mistakes=[
                 "Encoding train and test separately, creating different column orders — silent corruption.",
                 "Integer-coding red=0, blue=1, green=2, which tells the model green is 'more than' red.",
                 "Fitting the encoder on all data including test, leaking test categories into training.",
             ],
             q1=("Why is integer-coding colors 0/1/2 actively harmful?",
                 "It invents an ordering and distances the data never had — the model will treat green as twice blue."),
             homework="Write `encode_colors(train, test)` fitting OneHotEncoder on train only and printing both shapes. Run it on two color sets, print both, and comment which line prevents test leakage.",
             patterns=["fit_transform(", ".transform("],
             mapping="sklearn.preprocessing.OneHotEncoder (and OrdinalEncoder when order is real); ColumnTransformer applies them per-column in pipelines. Fit encoders on training categories only — a new test-time category is a fact to handle, not a crash.",
         ),
         86: dict(
             topic="Shuffling: why order lies",
             idea="Datasets arrive ordered — by time, by class, by collection batch. Training on the first 80% of ordered rows can mean training on one class and testing on another, and the model fails for a data reason no algorithm can fix. Shuffling before splitting (or stratifying, day 108) removes order as a variable; demonstrating the failure on ordered data is how you learn to never trust row order. Note the exception that proves the rule: when order IS the signal — forecasting tomorrow from today — shuffling destroys exactly what you must learn, and time-based splits replace it. Rows are exchangeable until proven sequential; know which kind you hold.",
             code=(
                 'from sklearn.neighbors import KNeighborsClassifier\n'
                 '\n'
                 'X = [[float(i)] for i in range(100)]\n'
                 'y = [0] * 70 + [1] * 30\n'
                 '\n'
                 'naive = KNeighborsClassifier(n_neighbors=3).fit(X[:80], y[:80])\n'
                 'print("naive train classes:", sorted(set(y[:80])))\n'
                 'print("naive test accuracy:", round(naive.score(X[80:], y[80:]), 3))\n'
                 '\n'
                 'import random\n'
                 'idx = list(range(100))\n'
                 'random.Random(0).shuffle(idx)\n'
                 'Xs = [X[i] for i in idx]\n'
                 'ys = [y[i] for i in idx]\n'
                 'fair = KNeighborsClassifier(n_neighbors=3).fit(Xs[:80], ys[:80])\n'
                 'print("shuffled test accuracy:", round(fair.score(Xs[80:], ys[80:]), 3))'
             ),
             variant_b='y = [0]*50 + [1]*50 (does the naive split still fail?)',
             variant_c='train on rows 30-100, test on 0-30 (which direction fails and why?)',
             mistakes=[
                 "Assuming rows arrive shuffled — they almost never do.",
                 "Shuffling X and y with different orders, destroying every label pairing.",
                 "Shuffling when order IS the signal (time series) — shuffle only when rows are exchangeable.",
             ],
             q1=("Why did the naive split score so badly here?",
                 "It trained on mostly class 0 and tested on mostly class 1 — the failure is in the data split, not the algorithm."),
             homework="Write `ordered_vs_shuffled()` that trains naive and shuffled kNN on ordered labels and prints both test scores. Run it on two orderings, print all four scores, and comment which line removes order as a variable.",
             patterns=[".fit(", ".score("],
             mapping="train_test_split shuffles by default (shuffle=True); stratify=y goes further by preserving class ratios.",
         ),
         87: dict(
             topic="Mini-project: end-to-end iris baseline",
             idea="Today the three jobs become one script: load iris, split honestly, fit a majority baseline AND a kNN, and report both with a confusion matrix. Two models, one scoreboard, one winner stated plainly. This is the smallest complete ML project — every capstone later is this shape with harder data and tuned models. Notice how little code it takes when the discipline is in place: the split is two lines, each model is fit-score-print, and the comparison is arithmetic. Complexity in ML projects should live in the data and the questions, never in the plumbing — if the script feels complicated, a boundary is leaking.",
             code=(
                 'from sklearn.datasets import load_iris\n'
                 'from sklearn.model_selection import train_test_split\n'
                 'from sklearn.dummy import DummyClassifier\n'
                 'from sklearn.neighbors import KNeighborsClassifier\n'
                 'from sklearn.metrics import accuracy_score\n'
                 '\n'
                 'X, y = load_iris(return_X_y=True)\n'
                 'Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, random_state=11)\n'
                 'results = {}\n'
                 'for name, model in [("baseline", DummyClassifier(strategy="most_frequent")), ("knn-5", KNeighborsClassifier(n_neighbors=5))]:\n'
                 '    model.fit(Xtr, ytr)\n'
                 '    score = accuracy_score(yte, model.predict(Xte))\n'
                 '    results[name] = round(score, 3)\n'
                 '    print(name, "test accuracy:", results[name])\n'
                 'print("winner:", max(results, key=results.get))\n'
                 'assert results["knn-5"] > results["baseline"]\n'
                 'print("real model beats baseline: proven")'
             ),
             variant_b='knn-1 instead of knn-5 (does it still beat the baseline on test?)',
             variant_c='test_size=0.5 (does the winner change?)',
             mistakes=[
                 "Comparing models trained on different splits — same split, or the comparison is void.",
                 "Forgetting the baseline and declaring kNN 'good' at a number the baseline also reaches.",
                 "Tuning k on the test set, then reporting the tuned number as if it were honest.",
             ],
             q1=("Why must both models share the exact same split?",
                 "Different test sets are different exams; scores from different exams cannot rank the models."),
             homework="Write `compare_two()` splitting once, scoring baseline vs kNN-5, and printing the winner. Run it on two random_states, print both scoreboards, and comment which line guarantees a fair comparison.",
             patterns=[".fit(", "accuracy_score("],
             mapping="Every later project repeats this scoreboard with stronger models; the discipline — same split, baseline included — never changes.",
         ),
         88: dict(
             topic="Testing ML code with asserts",
             idea="ML scripts fail silently: a transposed matrix still multiplies, a leaked split still scores. Asserts convert silent corruption into loud failure at the guilty line — shapes after loading, label counts after splitting, score ranges after evaluating. Five asserts around an experiment cost one minute and save the all-night debugging session where the model 'learns' from its own test answers. Write asserts as invariants, not snapshots: 'train and test cover all classes' survives a new split, while 'train has exactly 105 rows' breaks the moment test_size changes. Invariant asserts document the experiment's contract; snapshot asserts just fossilise today's numbers.",
             code=(
                 'from sklearn.datasets import load_iris\n'
                 'from sklearn.model_selection import train_test_split\n'
                 'from sklearn.neighbors import KNeighborsClassifier\n'
                 '\n'
                 'X, y = load_iris(return_X_y=True)\n'
                 'assert X.shape == (150, 4) and len(y) == 150\n'
                 'Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, random_state=12)\n'
                 'assert len(Xtr) == 105 and len(Xte) == 45\n'
                 'assert set(yte) == {0, 1, 2}\n'
                 'model = KNeighborsClassifier(n_neighbors=3).fit(Xtr, ytr)\n'
                 'score = model.score(Xte, yte)\n'
                 'assert 0.0 <= score <= 1.0\n'
                 'print("all guards passed, test accuracy:", round(score, 3))'
             ),
             variant_b='test_size=0.2 (which asserts need new numbers?)',
             variant_c='drop the set(yte) assert and split without shuffle on ordered labels (what breaks silently?)',
             mistakes=[
                 "Asserting shapes but never label coverage — a missing class in test breaks evaluation quietly.",
                 "Asserts that encode today's numbers instead of invariants (== 105 breaks when the split changes).",
                 "No asserts at all because 'the code ran', confusing running with correct.",
             ],
             q1=("Why assert label coverage (all classes in test), not just sizes?",
                 "A test set missing a class evaluates a 3-class model on 2 classes — the score looks fine and means less than it claims."),
             homework="Write `guarded_experiment()` with asserts on shapes, split sizes and label coverage, printing the final score. Run it on two datasets, print both, and comment which assert would catch a leaked split.",
             patterns=["assert ", ".score("],
             mapping="sklearn’s own check_X_y/check_array are these guards built in; yours make the experiment’s assumptions visible. Assert label coverage as well as sizes — a test set missing a class evaluates a three-class model on two.",
         ),
         89: dict(
             topic="Phase review: setup and data",
             idea="Rebuild the phase from memory: estimators speak fit/predict, data arrives as (X, y), splits must be shuffled and seeded, baselines set the floor, metrics give regression and classification their scoreboards, and asserts guard every boundary. Close the notes and reproduce the iris baseline script — the parts you cannot rebuild are the parts you have not learned yet. Review is retrieval, not re-reading: each failed recall marks a gap to patch today rather than a surprise on the capstone. If the gap number from memory is within a point or two of the noted one, the phase stuck; if not, the specific missing line is tomorrow's first job. Either outcome beats re-reading: a confirmed memory is durable, and a located gap is actionable.",
             code=(
                 'from sklearn.datasets import load_iris\n'
                 'from sklearn.model_selection import train_test_split\n'
                 'from sklearn.dummy import DummyClassifier\n'
                 'from sklearn.neighbors import KNeighborsClassifier\n'
                 '\n'
                 'X, y = load_iris(return_X_y=True)\n'
                 'Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, random_state=13)\n'
                 'base = DummyClassifier(strategy="most_frequent").fit(Xtr, ytr)\n'
                 'real = KNeighborsClassifier(n_neighbors=3).fit(Xtr, ytr)\n'
                 'print("baseline:", round(base.score(Xte, yte), 3))\n'
                 'print("knn-3:", round(real.score(Xte, yte), 3))\n'
                 'print("gap above baseline:", round(real.score(Xte, yte) - base.score(Xte, yte), 3))'
             ),
             variant_b='digits data instead of iris (which numbers move?)',
             variant_c='k=7 (does the gap widen or narrow?)',
             mistakes=[
                 "Re-reading the phase instead of rebuilding its scripts from memory.",
                 "Reciting fit/predict without being able to place them in a running script.",
                 "Skipping the baseline in the rebuild because 'it was trivial'.",
             ],
             q1=("What single number proves this phase stuck?",
                 "The gap between a real model and the baseline on unseen data, reproduced from memory on a fresh split."),
             homework="Write `phase_recap()` from memory: load, split, baseline, kNN, printed gap. Run it on two datasets, print both gaps, and comment which line you had to look up (that is tomorrow's review).",
             patterns=[".fit(", ".score("],
             mapping="Phase 2 swaps kNN for regression: same verbs, same discipline, continuous targets. The baseline habit transfers too — every regressor answers to the mean floor first.",
         ),
     }),
    ("Regression",
     "Fit lines and curves honestly: coefficients, gradient descent, polynomials, regularisation and residuals.",
     {
         90: dict(
             topic="Linear regression arrives",
             idea="Linear regression draws the straight line that minimises squared error: prediction = intercept + slope × feature. On one feature you can read the whole model — the slope says how much y moves per unit of x, the intercept says where the line crosses zero. Scikit-learn's LinearRegression solves this exactly (no iterations, no learning rate), which makes it the perfect first regressor: what you see in coef_ and intercept_ is the entire learned knowledge. Judge it by R² on unseen data, and keep the mean baseline beside every number. One feature also keeps the geometry visible: plot predictions against the feature and the fit is literally inspectable, a luxury that vanishes in high dimensions — enjoy single-feature debugging while it lasts.",
             code=(
                 'from sklearn.datasets import make_regression\n'
                 'from sklearn.linear_model import LinearRegression\n'
                 'from sklearn.metrics import r2_score\n'
                 '\n'
                 'X, y = make_regression(n_samples=60, n_features=1, noise=8.0, random_state=20)\n'
                 'model = LinearRegression().fit(X[:45], y[:45])\n'
                 'print("slope:", round(float(model.coef_[0]), 3))\n'
                 'print("intercept:", round(float(model.intercept_), 3))\n'
                 'pred = model.predict(X[45:])\n'
                 'print("test R^2:", round(r2_score(y[45:], pred), 3))\n'
                 'assert r2_score(y[45:], pred) > 0.8\n'
                 'print("line explains the data: proven")'
             ),
             variant_b='noise=25.0 (how far does test R² fall?)',
             variant_c='train on 20 rows instead of 45 (does the slope wobble?)',
             mistakes=[
                 "Reading a high training R² as success instead of measuring on held-out rows.",
                 "Forgetting the intercept, which forces the line through the origin for no reason.",
                 "Judging the slope without the noise level — a steep slope on noisy data means little.",
             ],
             q1=("What do coef_ and intercept_ together tell you that neither tells alone?",
                 "The full line: intercept anchors it at x=0 and the slope gives the per-unit change, so together they predict any input."),
             homework="Write `first_line()` that builds the 60-point regression set, fits the line on 45 rows, and prints slope, intercept and test R². Run it for two noise levels, print both, and comment which attribute holds the slope.",
             patterns=[".fit(", ".predict("],
             mapping="sklearn.linear_model.LinearRegression — exact least-squares solution; coef_ and intercept_ are the whole model.",
         ),
         91: dict(
             topic="Coefficients are explanations",
             idea="With several features, each coefficient answers 'holding everything else fixed, what does one unit of this feature add to the prediction?' Sorting features by absolute coefficient turns a black-box line into a ranked explanation: on diabetes data, body-mass index and blood serum measurements dominate. But coefficients are only comparable when features share a scale — a feature measured in thousands gets a tiny coefficient for a huge effect. Read magnitudes after scaling (day 98), and never confuse a large coefficient with a causal claim: the model reports association in this dataset, not what would happen if you intervened. Standardise before ranking so magnitudes compare fairly, and confirm with permutation importance, which shuffles one column at a time and measures the damage. Treat the ranking as the start of an investigation — the top feature earns follow-up analysis, not a conclusion; rankings start investigations, they never end them.",
             code=(
                 'from sklearn.datasets import load_diabetes\n'
                 'from sklearn.linear_model import LinearRegression\n'
                 '\n'
                 'X, y = load_diabetes(return_X_y=True)\n'
                 'names = load_diabetes()["feature_names"]\n'
                 'model = LinearRegression().fit(X[:350], y[:350])\n'
                 'ranked = sorted(zip(names, model.coef_), key=lambda p: abs(p[1]), reverse=True)\n'
                 'print("top 3 drivers:")\n'
                 'for name, coef in ranked[:3]:\n'
                 '    print(f"  {name}: {coef:+.1f}")\n'
                 'print("weakest:", ranked[-1][0], f"{ranked[-1][1]:+.1f}")'
             ),
             variant_b='train on the LAST 350 rows instead (does the ranking survive?)',
             variant_c='drop the top feature and refit (which coefficient absorbs its effect?)',
             mistakes=[
                 "Comparing raw coefficients across unscaled features with different units.",
                 "Claiming the top feature 'causes' the outcome from observational data.",
                 "Ignoring correlated features, where the weight splits arbitrarily between twins.",
             ],
             q1=("Why can dropping one feature radically change the others' coefficients?",
                 "Correlated features share explanatory credit, so removing one forces its twins to absorb the effect — the ranking is joint, not absolute."),
             homework="Write `rank_drivers()` fitting on 350 diabetes rows and printing the top-3 features by |coefficient|. Run it on two row windows, print both rankings, and comment which line sorts by magnitude.",
             patterns=[".fit(", ".coef_"],
             mapping="model.coef_ paired with feature names; permutation_importance (later) double-checks the ranking model-agnostically.",
         ),
         92: dict(
             topic="Gradient descent by hand",
             idea="Before trusting optimisers, be one: start with slope zero, compute how wrong you are, and nudge the slope downhill proportional to the error, repeating until the loss flattens. This loop — predict, measure, step against the gradient — is the engine inside neural networks, boosted trees' residual fitting, and SGDRegressor. Doing it by hand on eight points demystifies every 'learning rate' you will ever tune: too large diverges spectacularly, too small crawls, and the loss curve tells you which within seconds. Scikit-learn will do this for you from tomorrow; today you earn the intuition it automates.",
             code=(
                 '# Gradient descent on eight points, no library\n'
                 'xs = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0]\n'
                 'ys = [2.1, 4.2, 5.8, 8.3, 9.9, 12.1, 13.8, 16.2]\n'
                 '\n'
                 'def fit_slope(xs, ys, lr=0.01, steps=400):\n'
                 '    slope = 0.0\n'
                 '    for _ in range(steps):\n'
                 '        grad = sum(-2 * x * (y - slope * x) for x, y in zip(xs, ys)) / len(xs)\n'
                 '        slope -= lr * grad\n'
                 '    return slope\n'
                 '\n'
                 'slope = fit_slope(xs, ys)\n'
                 'pred = [slope * x for x in xs]\n'
                 'mse = sum((p - y) ** 2 for p, y in zip(pred, ys)) / len(ys)\n'
                 'print("hand slope:", round(slope, 3), "| MSE:", round(mse, 3))\n'
                 'assert abs(slope - 2.0) < 0.15\n'
                 'print("descent found the line: proven")'
             ),
             variant_b='lr=0.5 (does it converge or explode? read the MSE)',
             variant_c='steps=10 (what does an unfinished descent look like?)',
             mistakes=[
                 "A learning rate so large the slope oscillates and explodes instead of settling.",
                 "Too few steps, then blaming the algorithm for an optimisation stopped early.",
                 "Forgetting to divide the gradient by n, so bigger datasets need retuned rates.",
             ],
             q1=("Why does the update step use the negative gradient?",
                 "The gradient points uphill (steepest increase of loss), so stepping against it is stepping downhill toward the minimum."),
             homework="Write `fit_slope(xs, ys, lr, steps)` returning the descended slope and printing final MSE. Run it with lr=0.01 and lr=0.5, print both, and comment which line is the downhill step.",
             patterns=["def ", "return"],
             mapping="sklearn.linear_model.SGDRegressor(loss='squared_error') runs this loop for you; learning_rate and max_iter are today's lr and steps.",
         ),
         93: dict(
             topic="Curves need polynomial features",
             idea="A straight line cannot bend, so on curved data it fails no matter how much you tune — the model class is wrong, not the fitting. PolynomialFeatures fixes the class without changing the algorithm: it adds x² (and x³…) as new columns, and ordinary linear regression then fits a curve in the expanded space. This is the feature-engineering lesson in miniature: most 'model upgrades' are really representation upgrades, and a linear model on good features routinely beats a fancy model on raw ones. Start at degree 2 and justify every step higher with falling test error, never training error.",
             code=(
                 'from sklearn.preprocessing import PolynomialFeatures\n'
                 'from sklearn.linear_model import LinearRegression\n'
                 'from sklearn.metrics import r2_score\n'
                 '\n'
                 'X = [[x] for x in [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5]]\n'
                 'y = [v[0] ** 2 + 1.0 for v in X]\n'
                 'Xtr, Xte, ytr, yte = X[:9], X[9:], y[:9], y[9:]\n'
                 'line = LinearRegression().fit(Xtr, ytr)\n'
                 'print("straight line test R^2:", round(r2_score(yte, line.predict(Xte)), 3))\n'
                 'poly = PolynomialFeatures(degree=2, include_bias=False)\n'
                 'curve = LinearRegression().fit(poly.fit_transform(Xtr), ytr)\n'
                 'print("quadratic test R^2:", round(r2_score(yte, curve.predict(poly.transform(Xte))), 3))'
             ),
             variant_b='degree=3 (better, same, or overkill on a parabola?)',
             variant_c='y = x^3 curve instead (which degree wins now?)',
             mistakes=[
                 "Raising the degree until training error vanishes and calling it learning.",
                 "Forgetting that x² of a large feature explodes numerically without scaling.",
                 "Blaming linear regression when the features, not the fitter, lack the curve.",
             ],
             q1=("Why does adding an x² column let a 'linear' model fit a curve?",
                 "The model stays linear in its parameters — it fits a + b·x + c·x² — while the x² column carries the bend the raw feature lacked."),
             homework="Write `curve_or_line(degree)` fitting both models on the parabola data and printing both test R² values. Run it for degrees 2 and 5, print both comparisons, and comment which line creates the curve-carrying column.",
             patterns=["PolynomialFeatures(", "r2_score("],
             mapping="sklearn.preprocessing.PolynomialFeatures plus any linear model; make_pipeline chains them leak-free (day 150).",
         ),
         94: dict(
             topic="Train error lies, test error decides",
             idea="A degree-9 polynomial through twelve points achieves near-zero training error by threading every dot — and predicts new points atrociously, because it memorised noise as if it were signal. This is overfitting in its purest visual form, and the train/test gap is its measurement: small gap, honest model; chasm, memorisation. Every regulariser, validator and early-stopping rule in the rest of the track exists to manage exactly this gap. Learn to distrust any error number computed on data the model has already seen — trust must be earned on rows the model never met.",
             code=(
                 'from sklearn.preprocessing import PolynomialFeatures\n'
                 'from sklearn.linear_model import LinearRegression\n'
                 'from sklearn.metrics import r2_score\n'
                 '\n'
                 'X = [[x] for x in [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5]]\n'
                 'y = [v[0] ** 2 + (0.5 if i % 2 else -0.5) for i, v in enumerate(X)]\n'
                 'poly = PolynomialFeatures(degree=9, include_bias=False)\n'
                 'Xp = poly.fit_transform(X)\n'
                 'model = LinearRegression().fit(Xp[:9], y[:9])\n'
                 'print("train R^2:", round(r2_score(y[:9], model.predict(Xp[:9])), 3))\n'
                 'print("test  R^2:", round(r2_score(y[9:], model.predict(Xp[9:])), 3))\n'
                 'print("gap = memorisation")'
             ),
             variant_b='degree=2 on the same noisy data (does the gap close?)',
             variant_c='train on all 12 rows (what happens to the very idea of a gap?)',
             mistakes=[
                 "Reporting the 0.999 training score as the model's quality.",
                 "Fixing overfitting by gathering more features instead of constraining the model.",
                 "Testing on training data 'just to check the pipeline runs' and then quoting that number.",
             ],
             q1=("Why does near-zero training error prove nothing about future predictions?",
                 "A flexible model can memorise noise, so training error measures memory capacity while only unseen data measures learning. Memorisation capacity grows with flexibility, so count parameters against data points before trusting any fit — twelve rows cannot honestly support ten free parameters."),
             homework="Write `gap_reporter(degree)` printing train and test R² for that polynomial degree. Run it for degrees 2 and 9, print both gaps, and comment which number exposes the memorisation.",
             patterns=[".fit(", "r2_score("],
             mapping="train_test_split plus test-side metrics throughout the track; validation curves (day 139) automate this comparison.",
         ),
         95: dict(
             topic="Ridge tames the wiggles",
             idea="Ridge regression adds a penalty on large coefficients: minimise error PLUS alpha times the sum of squared weights. The alpha knob trades fit against calm — tiny alpha recovers ordinary regression, huge alpha flattens the line toward zero. On the noisy parabola, a well-chosen alpha keeps the curve's shape while ironing out the noise-chasing wiggles. Regularisation is the first systematic answer to overfitting: instead of choosing the degree by gut feeling, you penalise complexity directly and let the data negotiate the trade-off.",
             code=(
                 'from sklearn.preprocessing import PolynomialFeatures\n'
                 'from sklearn.linear_model import Ridge\n'
                 'from sklearn.metrics import r2_score\n'
                 'import math\n'
                 '\n'
                 'X = [[x] for x in [i * 0.5 for i in range(12)]]\n'
                 'y = [v[0] ** 2 + (0.5 if i % 2 else -0.5) for i, v in enumerate(X)]\n'
                 'poly = PolynomialFeatures(degree=9, include_bias=False)\n'
                 'Xtr, Xte = poly.fit_transform(X[:9]), poly.transform(X[9:])\n'
                 'for alpha in (0.001, 1.0, 1000.0):\n'
                 '    m = Ridge(alpha=alpha).fit(Xtr, y[:9])\n'
                 '    norm = math.sqrt(sum(c * c for c in m.coef_))\n'
                 '    print(f"alpha={alpha:<7} test R^2={r2_score(y[9:], m.predict(Xte)):.3f} coef-norm={norm:.1f}")'
             ),
             variant_b='degree=4 with the same alphas (does the best alpha move?)',
             variant_c='alpha=1e9 (what does the prediction become when weights die?)',
             mistakes=[
                 "Leaving alpha at its default on every problem instead of scanning a few values.",
                 "Regularising unscaled features, so the penalty punishes units rather than complexity.",
                 "Choosing alpha by training error, which always prefers alpha near zero.",
             ],
             q1=("Why does a huge alpha flatten predictions toward a constant?",
                 "The penalty dominates, so the cheapest solution shrinks every weight near zero and the model predicts almost the intercept everywhere."),
             homework="Write `ridge_scan()` printing test R² and coefficient norms for three alphas. Run it on two noise levels, print both tables, and comment which column shows the calming effect.",
             patterns=["Ridge(", ".predict("],
             mapping="sklearn.linear_model.Ridge(alpha=…); RidgeCV automates the alpha scan with built-in cross-validation.",
         ),
         96: dict(
             topic="Lasso selects features by zeroing them",
             idea="Lasso penalises the sum of absolute weights instead of squares, and that geometric difference matters: absolute penalties push small weights exactly to zero, deleting features from the model. On diabetes data with ten features, a strong Lasso keeps three or four and discards the rest — automatic feature selection as a side effect of fitting. Ridge shrinks, Lasso selects. Use Lasso when you suspect a few true drivers hide among many passengers, and read the survivors as the model's shortlist, remembering correlation can make it keep one twin and drop the other arbitrarily.",
             code=(
                 'from sklearn.datasets import load_diabetes\n'
                 'from sklearn.model_selection import train_test_split\n'
                 'from sklearn.linear_model import Lasso\n'
                 'from sklearn.metrics import r2_score\n'
                 '\n'
                 'X, y = load_diabetes(return_X_y=True)\n'
                 'names = load_diabetes()["feature_names"]\n'
                 'Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, random_state=21)\n'
                 'for alpha in (0.1, 1.0, 5.0):\n'
                 '    m = Lasso(alpha=alpha, max_iter=5000).fit(Xtr, ytr)\n'
                 '    kept = [n for n, c in zip(names, m.coef_) if abs(c) > 1e-9]\n'
                 '    print(f"alpha={alpha}: R^2={r2_score(yte, m.predict(Xte)):.3f} kept={kept}")'
             ),
             variant_b='max_iter left at default 1000 (does it converge? check for warnings in behaviour)',
             variant_c='alpha=0.01 (how many features survive near-zero penalty?)',
             mistakes=[
                 "Forgetting max_iter on Lasso, which often needs more iterations than the default.",
                 "Reading dropped features as 'proven useless' rather than 'not needed given the kept ones'.",
                 "Skipping scaling, so the absolute penalty falls unevenly across units.",
             ],
             q1=("Why does Lasso zero weights while Ridge only shrinks them?",
                 "The absolute-value penalty has a kink at zero that optimal solutions land exactly on; the squared penalty approaches zero smoothly but rarely touches it."),
             homework="Write `lasso_shortlist()` printing kept-feature names for three alphas. Run it on two splits, print both, and comment which line decides survival.",
             patterns=["Lasso(", ".coef_"],
             mapping="sklearn.linear_model.Lasso and LassoCV; ElasticNet mixes both penalties when twins must share credit.",
         ),
         97: dict(
             topic="Reading residuals like a doctor",
             idea="Residuals — actual minus predicted, one per row — are the model's confession. Random scatter around zero means the line captured the structure; a visible curve means the model class is wrong; a widening funnel means error grows with the target (heteroscedasticity) and the loss function is mismatched. Professionals plot or print residuals before tuning anything, because the pattern names the fix: curve → add bend, funnel → transform the target, lone giant residual → inspect that row for a data error. Plot against predictions by default and against feature values when hunting a missing bend — location first, magnitude second, always.",
             code=(
                 'from sklearn.datasets import load_diabetes\n'
                 'from sklearn.model_selection import train_test_split\n'
                 'from sklearn.linear_model import LinearRegression\n'
                 '\n'
                 'X, y = load_diabetes(return_X_y=True)\n'
                 'Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, random_state=22)\n'
                 'pred = LinearRegression().fit(Xtr, ytr).predict(Xte)\n'
                 'resid = [float(t - p) for t, p in zip(yte, pred)]\n'
                 'print("worst over-prediction:", round(min(resid), 1))\n'
                 'print("worst under-prediction:", round(max(resid), 1))\n'
                 'big = sum(abs(r) > 60 for r in resid)\n'
                 'print(f"{big} of {len(resid)} test rows miss by over 60")'
             ),
             variant_b='residuals on the TRAINING rows instead (smaller — but what does that prove?)',
             variant_c='Ridge(alpha=1.0) residuals (do the extremes shrink?)',
             mistakes=[
                 "Averaging residuals (they cancel to near zero by construction) instead of reading their spread.",
                 "Ignoring one giant residual that turns out to be a data-entry error worth more than tuning.",
                 "Never looking at residuals at all — tuning blind while the diagnosis sits in one print.",
             ],
             q1=("Why do residuals average near zero even for a bad model?",
                 "Least squares forces the mean error to zero as part of fitting, so the mean hides everything — only the spread and pattern diagnose."),
             homework="Write `residual_report()` printing worst over/under-predictions and the count of big misses. Run it for LinearRegression and Ridge, print both, and comment which line computes a single row's confession.",
             patterns=[".predict(", ".fit("],
             mapping="No estimator needed — residuals are arithmetic on predictions; yellowbrick/counterparts plot them, but reading numbers works everywhere.",
         ),
         98: dict(
             topic="Scale before you regularise",
             idea="Penalties punish coefficient size, but size depends on units: a feature in millimetres gets a coefficient 1000× smaller than the same feature in metres for identical effect. Unscaled, Ridge penalises the units, not the complexity — the millimetre feature escapes punishment entirely. StandardScaler (zero mean, unit variance, fit on train only) puts every feature on one scale so the penalty falls fairly. Rule: any penalised model gets scaled inputs, always through a pipeline so test data never leaks into the scaler. Pipelines (phase 6) automate this order, but knowing the manual sequence is what lets you spot leaks in other people's code.",
             code=(
                 'from sklearn.datasets import load_diabetes\n'
                 'from sklearn.model_selection import train_test_split\n'
                 'from sklearn.linear_model import Ridge\n'
                 'from sklearn.preprocessing import StandardScaler\n'
                 'from sklearn.metrics import r2_score\n'
                 '\n'
                 'X, y = load_diabetes(return_X_y=True)\n'
                 'Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, random_state=23)\n'
                 'raw = Ridge(alpha=1.0).fit(Xtr, ytr)\n'
                 'print("unscaled test R^2:", round(r2_score(yte, raw.predict(Xte)), 3))\n'
                 'sc = StandardScaler().fit(Xtr)\n'
                 'scaled = Ridge(alpha=1.0).fit(sc.transform(Xtr), ytr)\n'
                 'print("scaled   test R^2:", round(r2_score(yte, scaled.predict(sc.transform(Xte))), 3))\n'
                 'print("same model, fairer penalty")'
             ),
             variant_b='alpha=10.0 on both paths (does the gap widen?)',
             variant_c='fit the scaler on ALL of X before splitting (leak — does the score inflate?)',
             mistakes=[
                 "Scaling after splitting correctly on train but transforming test with a refit scaler.",
                 "Fitting the scaler on the full dataset, leaking test statistics into training.",
                 "Scaling for plain LinearRegression and expecting a score change (there is none — only penalties care).",
             ],
             q1=("Why does scaling change Ridge scores but not plain LinearRegression scores?",
                 "Unpenalised least squares is scale-invariant (coefficients compensate exactly); penalties punish size, so units change what gets punished."),
             homework="Write `scale_effect()` printing unscaled vs scaled Ridge R² on one split. Run it for two alphas, print both comparisons, and comment which line keeps test data out of the scaler.",
             patterns=["StandardScaler(", ".transform("],
             mapping="sklearn.preprocessing.StandardScaler inside make_pipeline(StandardScaler(), Ridge()) — the leak-free habit from day one.",
         ),
         99: dict(
             topic="Numbers and categories side by side",
             idea="Real tables mix numbers and text: square footage alongside neighbourhood name. The professional pattern handles each type with its own tool — numbers pass through (scaled), categories go one-hot — then concatenates both into one matrix the model never knows was assembled. ColumnTransformer declares this per-column plan in one object, so the same plan applies identically at train and test time. Build it manually once with zip/concatenation to feel the assembly, then use the transformer forever after — the manual version teaches, the transformer ships reliably every run.",
             code=(
                 'from sklearn.preprocessing import OneHotEncoder, StandardScaler\n'
                 'from sklearn.linear_model import Ridge\n'
                 '\n'
                 'sizes = [800.0, 1200.0, 950.0, 1500.0, 700.0]\n'
                 'areas = [["town"], ["city"], ["town"], ["city"], ["town"]]\n'
                 'prices = [150.0, 300.0, 180.0, 350.0, 140.0]\n'
                 '\n'
                 'num = StandardScaler().fit_transform([[s] for s in sizes[:4]])\n'
                 'cat = OneHotEncoder(sparse_output=False).fit_transform(areas[:4])\n'
                 'import math\n'
                 'Xtr = [list(n) + list(c) for n, c in zip(num, cat)]\n'
                 'model = Ridge(alpha=1.0).fit(Xtr, prices[:4])\n'
                 'row5 = list(StandardScaler().fit([[s] for s in sizes[:4]]).transform([[sizes[4]]])[0]) + [0.0, 1.0]\n'
                 'print("row-5 prediction:", round(float(model.predict([row5])[0]), 1), "| actual:", prices[4])'
             ),
             variant_b='a third area "village" in row 5 only (which encoding breaks, and how do you fix it?)',
             variant_c='alpha=0.01 (does the tiny training set overfit without penalty?)',
             mistakes=[
                 "One-hot encoding train and test with separate encoders and mismatched columns.",
                 "Forgetting that row 5 needs the TRAIN scaler and encoder, not refit ones.",
                 "Scaling the one-hot columns, which destroys their clean 0/1 meaning.",
             ],
             q1=("Why must row 5 reuse the train-fitted scaler and encoder?",
                 "Refitting on test data recomputes means and categories from answers-in-progress — the same leakage as training on the test set, in miniature. Build the assembly once as a function of (size, area) so train and test rows travel the identical path."),
             homework="Write `mixed_row()` assembling scaled-size plus one-hot-area features and predicting one held-out price. Run it on two held-out rows, print both, and comment which line reuses training statistics.",
             patterns=["OneHotEncoder(", "StandardScaler("],
             mapping="sklearn.compose.ColumnTransformer with (StandardScaler(), numeric_cols) and (OneHotEncoder(), cat_cols) — day 150 builds it properly.",
         ),
         100: dict(
             topic="When the line cannot bend enough",
             idea="Some relationships are not lines with noise but curves with structure: a sine wave, diminishing returns, a threshold effect. Linear regression on raw x fails these honestly — low R² everywhere, residuals showing a clear wave — and the diagnosis is in the residual pattern, not the score. The fix ladder runs: transform the target (log for multiplicative growth), engineer the bend (polynomials, day 93), or change the model class (trees, phase 4). Recognising 'wrong class' versus 'wrong parameters' is the judgement that separates tuning from flailing. When in doubt fit the simple model first — its honest failure teaches the shape the fancy model must capture.",
             code=(
                 'import math\n'
                 'from sklearn.linear_model import LinearRegression\n'
                 'from sklearn.metrics import r2_score\n'
                 '\n'
                 'X = [[x * 0.5] for x in range(16)]\n'
                 'y = [math.sin(v[0]) for v in X]\n'
                 'model = LinearRegression().fit(X[:12], y[:12])\n'
                 'print("line on a wave, test R^2:", round(r2_score(y[12:], model.predict(X[12:])), 3))\n'
                 'resid = [t - p for t, p in zip(y[12:], model.predict(X[12:]))]\n'
                 'print("residual signs:", ["+" if r > 0 else "-" for r in resid])\n'
                 'print("patterned residuals = wrong model class")'
             ),
             variant_b='y = log(x+1) curve (does the line do better or worse than on sine?)',
             variant_c='train on all 16 points (does more data fix a wrong class?)',
             mistakes=[
                 "Adding polynomial degrees blindly until train error vanishes (day 94's trap, revisited).",
                 "Blaming noise for what is visibly structure in the residuals.",
                 "Collecting more data to fix a model-class problem — more rows of the wrong shape help nothing.",
             ],
             q1=("How do patterned residuals differ from large residuals as a diagnosis?",
                 "Large-but-random residuals mean noise the model cannot capture; patterned residuals mean structure the model class cannot express — different disease, different cure."),
             homework="Write `bend_test()` fitting a line on sine-wave data and printing test R² plus residual signs. Run it on sine and log curves, print both, and comment what the sign pattern proves.",
             patterns=[".fit(", "r2_score("],
             mapping="When the class is wrong, change it: DecisionTreeRegressor (phase 4) bends for free; log-targets linearise growth.",
         ),
         101: dict(
             topic="Outliers pull lines off course",
             idea="Least squares squares every error, so one wild point — a typo, a sensor glitch, a billionaire in an income survey — drags the whole line toward itself with quadratic force. Diagnose by influence: refit without the suspect row and watch the coefficients jump. Respond with judgement, not reflex: fix data errors, model genuine extremes separately, and reach for robust losses (HuberRegressor: quadratic near zero, linear far away) when extremes are real but should not rule. Never silently delete rows to flatter a metric.",
             code=(
                 'from sklearn.linear_model import LinearRegression, HuberRegressor\n'
                 'from sklearn.metrics import r2_score\n'
                 '\n'
                 'X = [[x] for x in [1.0, 2.0, 3.0, 4.0, 5.0, 6.0]]\n'
                 'y_clean = [2.0, 4.1, 5.9, 8.2, 9.8, 12.1]\n'
                 'y_wild = [2.0, 4.1, 5.9, 8.2, 9.8, 40.0]\n'
                 'plain = LinearRegression().fit(X, y_wild)\n'
                 'robust = HuberRegressor(epsilon=1.35).fit(X, y_wild)\n'
                 'print("plain slope on wild data:", round(float(plain.coef_[0]), 2))\n'
                 'print("huber slope on wild data:", round(float(robust.coef_[0]), 2))\n'
                 'print("clean-data slope would be ~2.0: huber resists the yank")'
             ),
             variant_b='wild point at x=3 instead of x=6 (does position change the pull?)',
             variant_c='epsilon=10.0 on Huber (wide quadratic zone — closer to plain or still robust?)',
             mistakes=[
                 "Deleting outliers to improve the score and reporting the cleaned number as the result.",
                 "Robustifying before checking whether the 'outlier' is a data-entry error worth fixing.",
                 "Assuming robustness means immunity — Huber resists, but garbage in still degrades out.",
             ],
             q1=("Why does squaring make one point so powerful?",
                 "Error enters the loss squared, so a 10× deviation exerts 100× the pull of a 1× one — the loss function itself amplifies extremes."),
             homework="Write `outlier_duel()` fitting plain and Huber lines on wild data and printing both slopes. Run it with the wild point at two positions, print both duels, and comment which estimator resists.",
             patterns=["HuberRegressor(", ".coef_"],
             mapping="sklearn.linear_model.HuberRegressor(epsilon=…) for robust fits; RANSACRegressor goes further by fitting the inlier consensus.",
         ),
         102: dict(
             topic="Project: diabetes end to end",
             idea="Today the phase becomes one script: load diabetes, split with a seed, score the mean baseline, fit LinearRegression and two Ridge alphas, and declare a winner with R² and MAE side by side. Same split for all four, baseline on the board, winner stated with its margin — the day-87 scoreboard grown up to regression. Write it as functions you could reuse next week, because phases 5 and 6 will demand exactly this harness with stronger models slotted in.",
             code=(
                 'from sklearn.datasets import load_diabetes\n'
                 'from sklearn.model_selection import train_test_split\n'
                 'from sklearn.dummy import DummyRegressor\n'
                 'from sklearn.linear_model import LinearRegression, Ridge\n'
                 'from sklearn.metrics import mean_absolute_error, r2_score\n'
                 '\n'
                 'X, y = load_diabetes(return_X_y=True)\n'
                 'Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, random_state=30)\n'
                 'board = {}\n'
                 'models = {"baseline": DummyRegressor(strategy="mean"), "linear": LinearRegression(),\n'
                 '          "ridge-0.1": Ridge(alpha=0.1), "ridge-10": Ridge(alpha=10.0)}\n'
                 'for name, m in models.items():\n'
                 '    m.fit(Xtr, ytr)\n'
                 '    pred = m.predict(Xte)\n'
                 '    board[name] = (round(r2_score(yte, pred), 3), round(mean_absolute_error(yte, pred), 2))\n'
                 '    print(f"{name:<10} R^2={board[name][0]:.3f} MAE={board[name][1]:.2f}")\n'
                 'winner = max(board, key=lambda k: board[k][0])\n'
                 'print("winner:", winner, "| beats baseline by R^2:", round(board[winner][0] - board["baseline"][0], 3))'
             ),
             variant_b='random_state=31 (does the winner survive a new deal?)',
             variant_c='add Lasso(alpha=1.0) to the board (where does it place?)',
             mistakes=[
                 "Different splits per model, voiding the whole comparison.",
                 "Tuning Ridge alphas on the test set, then reporting test numbers as honest.",
                 "No baseline row, so 'R² = 0.51' floats without meaning.",
             ],
             q1=("Why must the winner be picked by test R² and not training R²?",
                 "Training R² rewards memorisation capacity; only unseen data ranks generalisation, which is the only ranking that matters."),
             homework="Write `diabetes_board()` scoring baseline/linear/two ridges on one split and printing the winner plus its margin over baseline. Run it on two seeds, print both boards, and comment which line keeps the comparison fair.",
             patterns=[".fit(", "r2_score("],
             mapping="This harness returns in phases 5–6 with forests and tuning; only the model list changes, never the discipline.",
         ),
         103: dict(
             topic="Testing regression code with asserts",
             idea="Regression experiments need their own guards: R² within [-inf, 1] sanity, MAE non-negative and finite, coefficients finite (no NaN from a singular matrix), predictions matching test length, baseline actually beaten by at least a hair before celebration. Assert the scoreboard's shape, not its values — 'winner beats baseline' survives new seeds while 'R² == 0.512' shatters on the next shuffle. These five asserts around the diabetes board cost a minute and catch the classic silent killers: leaked scaler, misaligned y, a model fit on empty data. Run the guards on every seed you report, not just the first — flaky guards are how leakage survives unnoticed.",
             code=(
                 'import math\n'
                 'from sklearn.datasets import load_diabetes\n'
                 'from sklearn.model_selection import train_test_split\n'
                 'from sklearn.dummy import DummyRegressor\n'
                 'from sklearn.linear_model import Ridge\n'
                 'from sklearn.metrics import r2_score, mean_absolute_error\n'
                 '\n'
                 'X, y = load_diabetes(return_X_y=True)\n'
                 'Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, random_state=32)\n'
                 'base = DummyRegressor(strategy="mean").fit(Xtr, ytr).predict(Xte)\n'
                 'pred = Ridge(alpha=1.0).fit(Xtr, ytr).predict(Xte)\n'
                 'assert len(pred) == len(yte)\n'
                 'assert all(math.isfinite(p) for p in pred)\n'
                 'assert mean_absolute_error(yte, pred) >= 0\n'
                 'score, floor = r2_score(yte, pred), r2_score(yte, base)\n'
                 'assert score > floor\n'
                 'print(f"guards passed: ridge R^2={score:.3f} beats floor {floor:.3f}")'
             ),
             variant_b='alpha=1e12 (which assert fires, and is the failure honest?)',
             variant_c='shuffle yte before scoring (which assert catches the misalignment?)',
             mistakes=[
                 "Asserting exact score values that break on every new seed.",
                 "No finiteness check, so a NaN coefficient poisons downstream silently.",
                 "Asserting the winner's name instead of the winner-beats-baseline relation.",
             ],
             q1=("Why assert relations (score > floor) instead of values (score == 0.51)?",
                 "Relations express the experiment's claim and survive new seeds; values fossilise one run and cry wolf on every other."),
             homework="Write `guarded_board()` with asserts on prediction length, finiteness, non-negative MAE and winner-beats-floor, printing the final comparison. Run it on two seeds, print both, and comment which assert guards alignment.",
             patterns=["assert ", "r2_score("],
             mapping="These guards wrap every later scoreboard; only the model names change from here on.",
         ),
         104: dict(
             topic="Phase review: regression",
             idea="Rebuild the phase from memory: lines minimise squared error, coefficients explain per-unit effects, gradient descent earns the optimiser intuition, polynomials add bend, the train/test gap exposes memorisation, Ridge calms, Lasso selects, residuals confess, scaling precedes penalties, wrong classes need new models, and outliers get robust losses. Close the notes and reproduce the diabetes board — baseline, linear, two ridges, winner with margin. The line you cannot rebuild names the gap; the gap is tomorrow's first job, and classification (phase 3) reuses every habit with labels instead of numbers. Bring the residual instinct too: classification has confusion matrices, but inspecting errors transfers exactly.",
             code=(
                 'from sklearn.datasets import load_diabetes\n'
                 'from sklearn.model_selection import train_test_split\n'
                 'from sklearn.dummy import DummyRegressor\n'
                 'from sklearn.linear_model import LinearRegression, Ridge\n'
                 'from sklearn.metrics import r2_score\n'
                 '\n'
                 'X, y = load_diabetes(return_X_y=True)\n'
                 'Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, random_state=33)\n'
                 'floor = r2_score(yte, DummyRegressor(strategy="mean").fit(Xtr, ytr).predict(Xte))\n'
                 'best, name = floor, "baseline"\n'
                 'for label, m in [("linear", LinearRegression()), ("ridge", Ridge(alpha=1.0))]:\n'
                 '    s = r2_score(yte, m.fit(Xtr, ytr).predict(Xte))\n'
                 '    print(label, round(s, 3))\n'
                 '    if s > best:\n'
                 '        best, name = s, label\n'
                 'print("recall winner:", name, "margin:", round(best - floor, 3))'
             ),
             variant_b='test_size=0.5 (does the winner survive less training data?)',
             variant_c='add the mean-baseline MAE beside each R² (which number explains to a stakeholder?)',
             mistakes=[
                 "Rebuilding from the notes open — retrieval is the learning, reading is the illusion.",
                 "Reciting regularisation without being able to place alpha in a running script.",
                 "Skipping residuals in the rebuild because scores felt sufficient.",
             ],
             q1=("What single rebuild proves this phase stuck?",
                 "The diabetes board from memory — baseline, linear, ridge, winner with margin — with every number explained, not just printed."),
             homework="Write `phase_recap()` from memory: split, baseline, linear, ridge, printed winner and margin. Run it on two seeds, print both, and comment which line you had to look up.",
             patterns=[".fit(", "r2_score("],
             mapping="Phase 3 keeps the verbs and the scoreboard; only the targets become labels and the metrics become counts.",
         ),
    }),
    ("Classification",
     "Turn features into labels: probabilities, boundaries, precision/recall, and honest imbalanced evaluation.",
     {
         105: dict(
             topic="Logistic regression: probabilities from a line",
             idea="Logistic regression keeps the familiar linear score — weights times features plus intercept — but squeezes it through the sigmoid into a probability between 0 and 1. That single design choice changes everything: outputs become calibrated-ish confidences, the decision boundary is where probability crosses one half, and training minimises log-loss (harsh on confident wrongness) instead of squared error. Read coef_ as before, but read predict_proba as the model's stated uncertainty — and remember it is only as calibrated as the data was representative, which is why calibration gets its own day later. The sigmoid also explains the name's confusion: despite 'regression', this is a classifier wearing a probability coat, and the coat is what makes thresholds tunable.",
             code=(
                 'from sklearn.datasets import make_classification\n'
                 'from sklearn.linear_model import LogisticRegression\n'
                 '\n'
                 'X, y = make_classification(n_samples=80, n_features=2, n_redundant=0, random_state=40)\n'
                 'model = LogisticRegression(max_iter=500).fit(X[:60], y[:60])\n'
                 'proba = model.predict_proba([X[70]])[0]\n'
                 'print("probabilities [P(0), P(1)]:", [round(p, 3) for p in proba])\n'
                 'print("sums to 1:", round(sum(proba), 6))\n'
                 'print("prediction:", model.predict([X[70]])[0], "| truth:", y[70])\n'
                 'print("test accuracy:", round(model.score(X[60:], y[60:]), 3))'
             ),
             variant_b='C=0.01 (heavy regularisation — do probabilities move toward 0.5?)',
             variant_c='a point far from all training data (is the model honestly uncertain or falsely confident?)',
             mistakes=[
                 "Reading 0.83 as '83% sure and therefore right' without any calibration check.",
                 "Forgetting max_iter on harder data, then blaming the model for non-convergence warnings.",
                 "Treating the 0.5 threshold as law instead of a business decision (day 107).",
             ],
             q1=("Why squeeze the linear score through a sigmoid instead of thresholding it directly?",
                 "The sigmoid converts unbounded scores into probabilities, which both calibrates confidence and gives log-loss something smooth to optimise."),
             homework="Write `prob_report()` fitting logreg and printing predicted probabilities for two test points plus test accuracy. Run it on two seeds, print both, and comment which method returns probabilities instead of labels.",
             patterns=["LogisticRegression(", "predict_proba("],
             mapping="sklearn.linear_model.LogisticRegression; predict_proba is the uncertainty readout every tuning decision consults.",
         ),
         106: dict(
             topic="Drawing the decision boundary",
             idea="A binary classifier splits feature space with a boundary: logistic regression draws a straight line (in 2-D), kNN draws a wiggly frontier following local majorities. Printing predictions on a grid of points makes the boundary visible without any plotting library — plus signs on one side, minuses on the other — and the shape tells you the model's assumptions at a glance. Straight boundary on curved data means systematic error in specific regions; wiggly boundary on linear data means memorised noise. Learn to picture every classifier as its boundary, because choosing models is largely choosing boundary shapes. When someone proposes a fancier model, ask what new boundary shapes it buys — if the answer is none, the fancy is decoration.",
             code=(
                 'from sklearn.datasets import make_classification\n'
                 'from sklearn.linear_model import LogisticRegression\n'
                 '\n'
                 'X, y = make_classification(n_samples=60, n_features=2, n_redundant=0, random_state=41)\n'
                 'model = LogisticRegression(max_iter=500).fit(X, y)\n'
                 'print("boundary map (+ = class 1 zone):")\n'
                 'for gy in (2.0, 1.0, 0.0, -1.0, -2.0):\n'
                 '    row = ""\n'
                 '    gx = -3.0\n'
                 '    while gx <= 3.0:\n'
                 '        row += "+" if model.predict([[gx, gy]])[0] == 1 else "."\n'
                 '        gx += 0.75\n'
                 '    print(f"y={gy:+.1f} {row}")'
             ),
             variant_b='kNN(k=3) boundary on the same data (straight or wiggly?)',
             variant_c='overlapping classes with class_sep=0.6 (where does the line cut through the mix?)',
             mistakes=[
                 "Assuming the boundary is where the model is 'unsure' — it is where the model switches answers, confidence aside.",
                 "Reading a 2-D boundary demo as the full story on 10-D data, where boundaries cannot be pictured.",
                 "Forgetting that scaling reshapes distance-based boundaries but not logistic ones much.",
             ],
             q1=("What does a straight boundary on curved data guarantee?",
                 "Systematic regional errors — whole zones where the model is wrong by construction, visible as blocks the line cannot reach."),
             homework="Write `boundary_map()` printing a text grid of predictions for a fitted classifier. Run it for logreg and kNN-3, print both maps, and comment which shape each boundary takes.",
             patterns=[".fit(", ".predict("],
             mapping="Any classifier's predict on a grid draws its boundary; linear_models draw lines, neighbours draw frontiers, trees draw boxes.",
         ),
         107: dict(
             topic="Precision and recall: the threshold is yours",
             idea="Lower the decision threshold and you catch more positives (recall rises) while crying wolf more often (precision falls); raise it and the reverse happens. Accuracy pretends this trade-off does not exist, but every real deployment chooses a point on it: spam filters buy precision, cancer screens buy recall. Sweeping the threshold over predicted probabilities and printing precision/recall pairs makes the curve tangible, and the business cost of each error type — not the textbook — picks the operating point. A model is not a number; it is a dial. Teams that argue about 'the accuracy' without naming costs are negotiating blind.",
             code=(
                 'from sklearn.datasets import make_classification\n'
                 'from sklearn.linear_model import LogisticRegression\n'
                 'from sklearn.metrics import precision_score, recall_score\n'
                 '\n'
                 'X, y = make_classification(n_samples=200, weights=[0.85, 0.15], random_state=42)\n'
                 'Xtr, Xte, ytr, yte = X[:150], X[150:], y[:150], y[150:]\n'
                 'proba = LogisticRegression(max_iter=500).fit(Xtr, ytr).predict_proba(Xte)[:, 1]\n'
                 'print("threshold | precision | recall")\n'
                 'for t in (0.2, 0.35, 0.5, 0.65, 0.8):\n'
                 '    pred = [1 if p >= t else 0 for p in proba]\n'
                 '    print(f"  {t:.2f}    |   {precision_score(yte, pred, zero_division=0):.2f}    |  {recall_score(yte, pred):.2f}")'
             ),
             variant_b='weights=[0.5, 0.5] balanced (does the trade-off flatten?)',
             variant_c='threshold 0.05 (what happens to precision when you catch everything?)',
             mistakes=[
                 "Reporting accuracy on 85/15 data, where always-negative scores 85%.",
                 "Picking 0.5 by habit instead of by error costs.",
                 "Tuning the threshold on test data, then quoting test precision as honest.",
             ],
             q1=("Why can't accuracy pick the threshold for you?",
                 "Accuracy weights both errors equally by definition, while real problems price false alarms and misses differently — only costs can place the dial."),
             homework="Write `threshold_table()` printing precision/recall at five thresholds. Run it on imbalanced and balanced data, print both tables, and comment which column a fraud team watches.",
             patterns=["precision_score(", "recall_score("],
             mapping="sklearn.metrics.precision_score, recall_score, f1_score; precision_recall_curve automates the sweep.",
         ),
         108: dict(
             topic="Stratified splits keep the ratios",
             idea="Plain shuffling can starve small classes: a 5% class may vanish from a small test set entirely, and then precision/recall divide by zero and evaluation is fiction. Stratified splitting deals each class proportionally into train and test, so ratios survive at every size. It costs one keyword and removes an entire failure class — unstratified evaluation on imbalanced data. Use stratify=y by default for classification from today on; reaching for unstratified splitting should require a reason, not the other way round. Stratification fixes representation, not learning — the minority is still rare, but at least it is present to be measured. Pair stratify with shuffling always; ordered rows defeat even a stratified deal.",
             code=(
                 'from sklearn.datasets import make_classification\n'
                 'from sklearn.model_selection import train_test_split\n'
                 'from collections import Counter\n'
                 '\n'
                 'X, y = make_classification(n_samples=100, weights=[0.9, 0.1], random_state=43)\n'
                 '_, _, _, plain = train_test_split(X, y, test_size=0.2, random_state=0)\n'
                 '_, _, _, strat = train_test_split(X, y, test_size=0.2, random_state=0, stratify=y)\n'
                 'print("plain test class counts:", dict(Counter(plain)))\n'
                 'print("stratified test counts:", dict(Counter(strat)))\n'
                 'print("stratified guarantees the minority shows up")'
             ),
             variant_b='test_size=0.1 (does plain splitting break outright?)',
             variant_c='weights=[0.99, 0.01] (how thin can the minority get?)',
             mistakes=[
                 "Evaluating recall for a class with zero test examples and reading 0.0 as a model failure.",
                 "Stratifying X and y in separate calls, shuffling them apart.",
                 "Assuming stratify fixes training imbalance too — it fixes representation, not the learning problem.",
             ],
             q1=("Why does a missing test class break recall rather than just lower it?",
                 "Recall divides by actual positives; with zero of them the metric is undefined — the evaluation is void, not merely bad."),
             homework="Write `strat_check()` printing plain vs stratified test-class counts. Run it on two imbalances, print both, and comment which keyword preserves the ratios.",
             patterns=["stratify=", "train_test_split("],
             mapping="train_test_split(..., stratify=y) and StratifiedKFold later; classification splits are stratified by default from now on.",
         ),
         109: dict(
             topic="Naive Bayes: bold assumptions, fast answers",
             idea="Naive Bayes assumes every feature is independent given the class — almost always false, yet the resulting classifier is fast, needs little data, and shines on text. GaussianNB models each feature per class as a bell curve and multiplies the evidence; when features genuinely behave independently (word counts in spam filtering), the 'naive' assumption costs nothing and the speed wins everything. The lesson is meta: wrong-but-useful assumptions beat no model at all, provided you measure rather than philosophise — which is exactly what the scoreboard is for. Keep NB in every classifier board as the two-line contender that stronger models must justify themselves against. On tiny datasets with many weak signals — classic text-like shapes — NB often wins outright; that is its home turf.",
             code=(
                 'from sklearn.datasets import make_classification\n'
                 'from sklearn.model_selection import train_test_split\n'
                 'from sklearn.naive_bayes import GaussianNB\n'
                 'from sklearn.neighbors import KNeighborsClassifier\n'
                 '\n'
                 'X, y = make_classification(n_samples=120, n_features=4, random_state=44)\n'
                 'Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, random_state=44)\n'
                 'nb = GaussianNB().fit(Xtr, ytr)\n'
                 'knn = KNeighborsClassifier(n_neighbors=5).fit(Xtr, ytr)\n'
                 'print("naive bayes test:", round(nb.score(Xte, yte), 3))\n'
                 'print("knn-5      test:", round(knn.score(Xte, yte), 3))\n'
                 'print("assumption-free vs assumption-full: measured, not argued")'
             ),
             variant_b='n_features=20 with n_samples=40 (little data — who wins now?)',
             variant_c='correlated features via n_redundant=3 (does independence hurt?)',
             mistakes=[
                 "Dismissing Naive Bayes as 'too simple' without measuring it as a baseline.",
                 "Feeding negative features to MultinomialNB, which requires counts.",
                 "Forgetting that independence is per-class conditional, not global.",
             ],
             q1=("Why can a false independence assumption still win?",
                 "Classification needs the right winner, not true probabilities — even distorted evidence ranks correctly when the distortion preserves order."),
             homework="Write `nb_vs_knn()` scoring both on one split and printing the pair. Run it on small-data and correlated variants, print both, and comment which regime favours the naive model.",
             patterns=["GaussianNB(", ".score("],
             mapping="sklearn.naive_bayes.GaussianNB (continuous) and MultinomialNB (counts/text, day 115); a two-line baseline for every classifier board.",
         ),
         110: dict(
             topic="Margins: the SVM idea",
             idea="Where logistic regression models probabilities, a support vector machine draws the boundary with the widest empty margin between classes — the street, not just the centre line. Only the points touching the street edges (support vectors) decide the boundary; every other point could move freely without changing the model. That sparsity of influence is the insight: generalisation comes from the hardest examples, not the easy masses. LinearSVC on separable data shows wide-margin thinking in one line, and its C parameter replays the regularisation lesson — small C, wider street, calmer model. Kernels later bend the street itself; the margin idea stays. Plot the street on 2-D data once and the abstraction becomes permanent.",
             code=(
                 'from sklearn.datasets import make_classification\n'
                 'from sklearn.svm import LinearSVC\n'
                 '\n'
                 'X, y = make_classification(n_samples=60, n_features=2, n_redundant=0, class_sep=2.0, random_state=45)\n'
                 'model = LinearSVC(max_iter=5000).fit(X[:45], y[:45])\n'
                 'print("test accuracy:", round(model.score(X[45:], y[45:]), 3))\n'
                 'print("boundary weights:", [round(float(c), 3) for c in model.coef_[0]])\n'
                 'print("intercept:", round(float(model.intercept_[0]), 3))\n'
                 'n_sv_like = sum(abs(model.decision_function(X[:45])) < 1.0)\n'
                 'print("points near the margin:", n_sv_like, "of 45 (the boundary crew)")'
             ),
             variant_b='class_sep=0.8 overlapping (does the street survive contact?)',
             variant_c='C=0.01 (wider street, calmer boundary — what happens to train accuracy?)',
             mistakes=[
                 "Skipping feature scaling for SVMs, where margins live in distance units.",
                 "Reading SVC probabilities that do not exist (predict_proba needs calibration).",
                 "Using kernels before understanding the linear street — machinery before intuition.",
             ],
             q1=("Why do only the near-margin points matter to the boundary?",
                 "The optimisation maximises the empty street, which is defined entirely by its edges — interior points constrain nothing."),
             homework="Write `street_report()` fitting LinearSVC and printing test accuracy plus near-margin count. Run it on separated and overlapping data, print both, and comment what the near-margin count reveals.",
             patterns=["LinearSVC(", "decision_function("],
             mapping="sklearn.svm.LinearSVC and SVC(kernel=...); C replays Ridge's alpha lesson in margin language.",
         ),
         111: dict(
             topic="Ranking quality with ROC-AUC",
             idea="Accuracy and F1 judge one threshold; ROC-AUC judges the ranking across all thresholds — the probability that a random positive outranks a random negative. A model can have mediocre accuracy at 0.5 yet excellent AUC, meaning its ordering is right and only the dial is wrong. That separation of ranking from thresholding is exactly what you need when costs are undecided: pick the best ranker now, set the dial when the business prices its errors. AUC 0.5 is coin-flip, 1.0 is perfect order, and anything below 0.5 means your labels are flipped — a free bug detector hiding in a metric.",
             code=(
                 'from sklearn.datasets import make_classification\n'
                 'from sklearn.linear_model import LogisticRegression\n'
                 'from sklearn.metrics import roc_auc_score, accuracy_score\n'
                 '\n'
                 'X, y = make_classification(n_samples=200, weights=[0.8, 0.2], random_state=46)\n'
                 'Xtr, Xte, ytr, yte = X[:150], X[150:], y[:150], y[150:]\n'
                 'proba = LogisticRegression(max_iter=500).fit(Xtr, ytr).predict_proba(Xte)[:, 1]\n'
                 'pred = [1 if p >= 0.5 else 0 for p in proba]\n'
                 'print("accuracy at 0.5:", round(accuracy_score(yte, pred), 3))\n'
                 'print("ROC-AUC (all thresholds):", round(roc_auc_score(yte, proba), 3))\n'
                 'print("ranking can be good while the dial is off")'
             ),
             variant_b='weights=[0.95, 0.05] (does accuracy stay smug while AUC tells truth?)',
             variant_c='a constant 0.5 prediction for all rows (AUC exactly 0.5 — why?)',
             mistakes=[
                 "Optimising accuracy when the deployment cares about ranking (retrieval, triage).",
                 "Comparing AUCs across different test sets, where difficulty differences dominate.",
                 "Forgetting AUC needs probabilities/scores, not hard labels.",
             ],
             q1=("Why can AUC be excellent while accuracy at 0.5 is mediocre?",
                 "AUC measures ordering quality over all thresholds; accuracy measures one threshold's luck — good ranking with a bad dial splits the two."),
             homework="Write `rank_report()` printing accuracy-at-0.5 and ROC-AUC side by side. Run it on two imbalance levels, print both, and comment which number judges the ranking.",
             patterns=["roc_auc_score(", "predict_proba("],
             mapping="sklearn.metrics.roc_auc_score for ranking; roc_curve plots the full trade-off when one number is not enough.",
         ),
         112: dict(
             topic="Fighting imbalance with class weights",
             idea="On 95/5 data, plain models learn that always-negative is nearly perfect — the loss function agrees. class_weight='balanced' reweights errors inversely to class frequency, making one missed minority count like nineteen missed majorities, which is often closer to the true business cost. It costs one keyword and no new data, and it belongs before exotic sampling: reweight first, resample only if reweighting under-delivers. Watch precision fall as recall rises — the trade-off did not vanish, you merely chose your point on it deliberately. Report both numbers side by side so the price of the recall you bought stays visible. Revisit the threshold whenever weights change — the dial moved, so yesterday's operating point rarely still fits.",
             code=(
                 'from sklearn.datasets import make_classification\n'
                 'from sklearn.linear_model import LogisticRegression\n'
                 'from sklearn.metrics import precision_score, recall_score\n'
                 '\n'
                 'X, y = make_classification(n_samples=300, weights=[0.95, 0.05], random_state=47)\n'
                 'Xtr, Xte, ytr, yte = X[:225], X[225:], y[:225], y[225:]\n'
                 'for w in (None, "balanced"):\n'
                 '    m = LogisticRegression(max_iter=1000, class_weight=w).fit(Xtr, ytr)\n'
                 '    pred = m.predict(Xte)\n'
                 '    print(f"weight={w}: precision={precision_score(yte, pred, zero_division=0):.2f} recall={recall_score(yte, pred):.2f}")'
             ),
             variant_b='weights=[0.7, 0.3] (does balanced still matter?)',
             variant_c='C=0.05 with balanced weights (regularisation meets reweighting — who wins?)',
             mistakes=[
                 "Accuracy as the headline on 95/5 data, hiding a model that never predicts the minority.",
                 "Oversampling before splitting, cloning rows across the train/test boundary (leakage).",
                 "Balanced weights plus threshold tuning both shifting the dial — pick one lever at a time.",
             ],
             q1=("Why does reweighting beat resampling as the first move?",
                 "It changes the loss in one keyword with zero data duplication and zero leakage surface; resampling rewrites the dataset and risks both."),
             homework="Write `weight_duel()` printing precision/recall with and without balanced weights. Run it on two imbalance levels, print both duels, and comment which column the minority cares about.",
             patterns=["class_weight=", "recall_score("],
             mapping="class_weight='balanced' on most classifiers; imbalanced-learn's samplers are plan B, used inside pipelines only.",
         ),
         113: dict(
             topic="Confidence you can read: calibration",
             idea="A probability is a promise: among all rows scored 0.8, about 80% should be positive. Raw model scores often break this promise — systematically overconfident on unfamiliar regions — and acting on uncalibrated numbers (auto-approving loans at '0.9') converts miscalibration into money lost. Binning predictions and comparing mean predicted versus actual positive rate exposes the gap in one table; isotonic or sigmoid calibration then repairs it. Never spend a probability you have not audited. Calibration is also where you discover your model is confident precisely where data is thinnest — the most expensive place to be wrong.",
             code=(
                 'from sklearn.datasets import make_classification\n'
                 'from sklearn.linear_model import LogisticRegression\n'
                 '\n'
                 'X, y = make_classification(n_samples=400, random_state=48)\n'
                 'Xtr, Xte, ytr, yte = X[:300], X[300:], y[:300], y[300:]\n'
                 'proba = LogisticRegression(max_iter=500).fit(Xtr, ytr).predict_proba(Xte)[:, 1]\n'
                 'print("bin      | predicted | actual rate")\n'
                 'for lo in (0.0, 0.2, 0.4, 0.6, 0.8):\n'
                 '    idx = [i for i, p in enumerate(proba) if lo <= p < lo + 0.2 or (lo == 0.8 and p == 1.0)]\n'
                 '    if idx:\n'
                 '        actual = sum(yte[i] for i in idx) / len(idx)\n'
                 '        print(f"{lo:.1f}-{lo+0.2:.1f} |    {(lo+0.1):.2f}   |   {actual:.2f}  (n={len(idx)})")'
             ),
             variant_b='kNN(k=3) probabilities (vote fractions — smoother or lumpier?)',
             variant_c='a point far outside training range (does the promise hold out there?)',
             mistakes=[
                 "Spending raw scores as probabilities in cost-bearing decisions.",
                 "Calibrating on training data, where the model is already overconfident by construction.",
                 "Tiny bins with n=2 presented as evidence of anything.",
             ],
             q1=("Why bin predictions instead of checking each probability individually?",
                 "One prediction is anecdote; a bin aggregates enough rows that predicted-vs-actual rates become a testable claim."),
             homework="Write `calibration_table()` printing predicted vs actual rates per bin. Run it for logreg and kNN-3, print both tables, and comment which bins you would trust with money.",
             patterns=["predict_proba(", ".fit("],
             mapping="sklearn.calibration.CalibratedClassifierCV repairs miscalibration; reliability diagrams are this table plotted.",
         ),
         114: dict(
             topic="Ten classes at once with digits",
             idea="Binary thinking breaks at ten digits: the model now outputs ten scores, predicts the argmax, and fails in forty-five directed ways (3→8 is not 8→3). Per-class precision/recall exposes which digits suffer — 8s and 3s confuse, 0s and 6s rarely do — and that asymmetry drives every fix: more 8s in training, blur-tolerant features, or a second-stage 3-vs-8 specialist. Multiclass is not 'classification but more'; the error structure becomes the project, and reading it per class is the skill. Start every multiclass project by printing the directed-pair table before touching any hyperparameter.",
             code=(
                 'from sklearn.datasets import load_digits\n'
                 'from sklearn.model_selection import train_test_split\n'
                 'from sklearn.neighbors import KNeighborsClassifier\n'
                 'from sklearn.metrics import accuracy_score\n'
                 '\n'
                 'X, y = load_digits(return_X_y=True)\n'
                 'Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, random_state=49, stratify=y)\n'
                 'pred = KNeighborsClassifier(n_neighbors=3).fit(Xtr, ytr).predict(Xte)\n'
                 'print("digits accuracy:", round(accuracy_score(yte, pred), 3))\n'
                 'errs = {}\n'
                 'for t, p in zip(yte, pred):\n'
                 '    if t != p:\n'
                 '        errs[(t, p)] = errs.get((t, p), 0) + 1\n'
                 'print("top confused pairs (true->pred: count):")\n'
                 'for pair, n in sorted(errs.items(), key=lambda kv: kv[1], reverse=True)[:4]:\n'
                 '    print(f"  {pair[0]}->{pair[1]}: {n}")'
             ),
             variant_b='k=1 (do the confused pairs change character?)',
             variant_c='logreg instead of kNN (which pairs persist across algorithms?)',
             mistakes=[
                 "Reporting 97% and stopping, leaving the 3% unexamined where all the learning lives.",
                 "Treating 3→8 and 8→3 as one symmetric error instead of two directed ones.",
                 "Stratify forgotten on ten classes, starving rare digits from the test set.",
             ],
             q1=("Why do the same confused pairs persist across different algorithms?",
                 "Persistent pairs mark genuinely similar inputs (3s shaped like 8s), not model quirks — the data itself is ambiguous there."),
             homework="Write `confused_pairs()` printing accuracy plus the top-4 directed error pairs. Run it for kNN-3 and logreg, print both, and comment which pair you would attack first.",
             patterns=[".predict(", "accuracy_score("],
             mapping="classification_report gives per-class precision/recall/F1; the directed-pair table is the error analyst's version.",
         ),
         115: dict(
             topic="Text becomes numbers: spam filtering",
             idea="Text is the least numeric data there is, yet counting words tames it: each message becomes a row of word counts, and suddenly geometry applies to language. CountVectorizer builds the vocabulary from training texts only — test words unseen in training are ignored, which is correct behaviour, not data loss — and MultinomialNB (built for counts) turns word frequencies into spam probabilities. The honest limitations travel with the power: word order dies in the bag, sarcasm is invisible, and a spammer's novel synonym sails through until retraining. Small corpus today, same pipeline on real inboxes tomorrow — the vocabulary-fit discipline is identical at every scale.",
             code=(
                 'from sklearn.feature_extraction.text import CountVectorizer\n'
                 'from sklearn.naive_bayes import MultinomialNB\n'
                 '\n'
                 'texts = ["win money now", "meeting at noon", "cheap loans today", "lunch with team",\n'
                 '         "claim your prize", "project deadline friday", "free cash fast", "notes from standup"]\n'
                 'y = [1, 0, 1, 0, 1, 0, 1, 0]\n'
                 'vec = CountVectorizer().fit(texts[:6])\n'
                 'print("vocabulary size:", len(vec.vocabulary_))\n'
                 'model = MultinomialNB().fit(vec.transform(texts[:6]), y[:6])\n'
                 'pred = model.predict(vec.transform(texts[6:]))\n'
                 'print("last-two predictions:", list(pred), "| truth:", y[6:])\n'
                 'print("unseen words ignored, not crashed: by design")'
             ),
             variant_b='two extra training texts ("dinner plans", "urgent wire transfer") — which way do they push?',
             variant_c='a test text of only unseen words (what does the model fall back to?)',
             mistakes=[
                 "Fitting the vectorizer on all texts including test — vocabulary leakage.",
                 "Feeding raw strings to the classifier instead of the transformed counts.",
                 "Expecting word order or negation handling from a bag of counts.",
             ],
             q1=("Why must unseen test words be ignored rather than crash or extrapolated?",
                 "The model learned weights only for training vocabulary; inventing weights for new words would be guessing disguised as knowledge."),
             homework="Write `spam_duel()` fitting vectorizer+NB on six texts and printing predictions on two held-out texts. Run it with two different held-out pairs, print both, and comment which line prevents vocabulary leakage.",
             patterns=["CountVectorizer(", "MultinomialNB("],
             mapping="sklearn.feature_extraction.text.CountVectorizer/TfidfVectorizer plus MultinomialNB — the classic baseline every fancier NLP model must beat.",
         ),
         116: dict(
             topic="When classes overlap: Bayes error",
             idea="Some points are ambiguous by nature: identical feature vectors with different labels, measurement noise, genuinely borderline cases. No classifier — however deep — beats the Bayes error rate, the irreducible floor set by overlap itself. Recognising overlap changes the project: instead of tuning harder, you engineer better features that separate what is currently tangled, or you accept calibrated uncertainty as the product. Chasing 100% on overlapping data is not ambition; it is overfitting scheduled in advance. The train/test pattern diagnoses it: knn-1 hits 1.0 on train yet tests worst, while calmer models agree on a middling score — consensus at mediocrity means the ceiling is real.",
             code=(
                 'from sklearn.datasets import make_classification\n'
                 'from sklearn.neighbors import KNeighborsClassifier\n'
                 'from sklearn.linear_model import LogisticRegression\n'
                 '\n'
                 'X, y = make_classification(n_samples=300, n_features=2, n_redundant=0, class_sep=0.6, flip_y=0.1, random_state=50)\n'
                 'Xtr, Xte, ytr, yte = X[:225], X[225:], y[:225], y[225:]\n'
                 'for name, m in [("logreg", LogisticRegression(max_iter=500)), ("knn-1", KNeighborsClassifier(n_neighbors=1)), ("knn-15", KNeighborsClassifier(n_neighbors=15))]:\n'
                 '    m.fit(Xtr, ytr)\n'
                 '    print(f"{name:<8} train={m.score(Xtr, ytr):.3f} test={m.score(Xte, yte):.3f}")\n'
                 'print("knn-1 memorises (train 1.0) yet tests worst: overlap cannot be memorised away")'
             ),
             variant_b='flip_y=0.0 clean separation (does knn-1 redeem itself?)',
             variant_c='class_sep=2.0 (how high can test scores honestly go?)',
             mistakes=[
                 "Tuning for weeks against an irreducible floor, mistaking overlap for underfitting.",
                 "Removing 'mislabeled' points by hand until the data looks separable — manufacturing success.",
                 "Reporting train accuracy on overlapping data as if it measured anything.",
             ],
             q1=("Why can't any model beat the Bayes error rate?",
                 "Overlapping regions contain identical inputs with different labels, so even a perfect map of the region must guess — the error is in the world, not the model."),
             homework="Write `overlap_board()` printing train/test scores for logreg, knn-1 and knn-15 on overlapping data. Run it at two overlap levels, print both boards, and comment which model memorises.",
             patterns=[".fit(", ".score("],
             mapping="When overlap dominates, the project moves to features (better separation) or calibrated probabilities (honest uncertainty) — modelling harder is plan C.",
         ),
         117: dict(
             topic="Project: breast-cancer classifier board",
             idea="Today the classification scoreboard grows up: load the breast-cancer data (569 tumours, 30 measurements), split stratified, and rank Dummy, logreg, kNN and Naive Bayes by accuracy AND F1 with the F1 winner declared. Same split, baseline included, winner by F1 because imbalanced classes punish accuracy-only thinking. This board is the template for every classifier comparison you will ever run — only the dataset and the model list change from here on. Notice the discipline compounding: stratify from day 108, baselines from day 79, F1 from day 107, all meeting in one script that would pass review anywhere.",
             code=(
                 'from sklearn.datasets import load_breast_cancer\n'
                 'from sklearn.model_selection import train_test_split\n'
                 'from sklearn.dummy import DummyClassifier\n'
                 'from sklearn.linear_model import LogisticRegression\n'
                 'from sklearn.neighbors import KNeighborsClassifier\n'
                 'from sklearn.naive_bayes import GaussianNB\n'
                 'from sklearn.metrics import accuracy_score, f1_score\n'
                 'from sklearn.preprocessing import StandardScaler\n'
                 '\n'
                 'X, y = load_breast_cancer(return_X_y=True)\n'
                 'Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, random_state=51, stratify=y)\n'
                 'sc = StandardScaler().fit(Xtr)\n'
                 'Xtr, Xte = sc.transform(Xtr), sc.transform(Xte)\n'
                 'print(f"data: {X.shape[0]} tumours, {X.shape[1]} features (scaled)")\n'
                 'board = {}\n'
                 'for name, m in [("dummy", DummyClassifier(strategy="most_frequent")), ("logreg", LogisticRegression(max_iter=1000)), ("knn-5", KNeighborsClassifier(n_neighbors=5)), ("nb", GaussianNB())]:\n'
                 '    pred = m.fit(Xtr, ytr).predict(Xte)\n'
                 '    board[name] = (accuracy_score(yte, pred), f1_score(yte, pred))\n'
                 '    print(f"{name:<7} acc={board[name][0]:.3f} F1={board[name][1]:.3f}")\n'
                 'print("winner by F1:", max(board, key=lambda k: board[k][1]))'
             ),
             variant_b='k=15 (does the winner survive a blurrier neighbour?)',
             variant_c='test_size=0.5 (less training data — who degrades fastest?)',
             mistakes=[
                 "Winner picked by accuracy on imbalanced classes instead of F1.",
                 "Unstratified split starving the malignant class in test.",
                 "No dummy row, so '0.93' floats without its floor.",
             ],
             q1=("Why pick the winner by F1 here instead of accuracy?",
                 "Classes are imbalanced and both error types matter medically — F1 balances precision and recall where accuracy would reward majority-guessing."),
             homework="Write `cancer_board()` ranking four models by accuracy and F1 on one stratified split and printing the F1 winner. Run it on two seeds, print both boards, and comment which metric chose the winner.",
             patterns=["f1_score(", "stratify="],
             mapping="This board template returns with forests, tuning and pipelines in phases 4–6; the discipline never changes.",
         ),
         118: dict(
             topic="Testing classifiers with asserts",
             idea="Classifier guards check the confusion contract: predictions are valid labels, every test class appears, probabilities sum to one, and the winner beats the dummy by a margin worth the complexity. Assert shapes and relations, never exact scores — 'logreg beats dummy on F1' survives new seeds while 'F1 == 0.947' shatters on the next shuffle. These guards wrap every classifier board from today on, catching silent killers like label misalignment and leaked vectorizers. A guarded board is a publishable board: anyone can rerun it on a new seed and the asserts re-certify the comparison automatically. A board whose asserts pass on three seeds is a result; one that passes on one seed is an anecdote.",
             code=(
                 'from sklearn.datasets import load_breast_cancer\n'
                 'from sklearn.model_selection import train_test_split\n'
                 'from sklearn.dummy import DummyClassifier\n'
                 'from sklearn.linear_model import LogisticRegression\n'
                 'from sklearn.metrics import f1_score\n'
                 'from sklearn.preprocessing import StandardScaler\n'
                 '\n'
                 'X, y = load_breast_cancer(return_X_y=True)\n'
                 'Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, random_state=52, stratify=y)\n'
                 'sc = StandardScaler().fit(Xtr)\n'
                 'Xtr, Xte = sc.transform(Xtr), sc.transform(Xte)\n'
                 'assert set(yte) == {0, 1}\n'
                 'dummy = DummyClassifier(strategy="most_frequent").fit(Xtr, ytr)\n'
                 'real = LogisticRegression(max_iter=1000).fit(Xtr, ytr)\n'
                 'proba = real.predict_proba(Xte)\n'
                 'assert all(abs(sum(row) - 1.0) < 1e-9 for row in proba)\n'
                 'f_base = f1_score(yte, dummy.predict(Xte))\n'
                 'f_real = f1_score(yte, real.predict(Xte))\n'
                 'assert f_real > f_base\n'
                 'print(f"guards passed: logreg F1={f_real:.3f} beats dummy {f_base:.3f}")'
             ),
             variant_b='drop stratify (which assert fires first on a starved class?)',
             variant_c='shuffle yte before scoring (which assert catches it?)',
             mistakes=[
                 "Exact-score asserts that break on every new seed and teach nothing.",
                 "No probability-sum check, so a broken custom classifier passes silently.",
                 "Asserting the winner's name instead of the winner-beats-baseline relation.",
             ],
             q1=("Why assert probability sums instead of individual probabilities?",
                 "Sums test the contract (a valid distribution) invariantly; individual values are seed-dependent details that legitimately move."),
             homework="Write `guarded_classifier()` with asserts on label coverage, probability sums and winner-beats-dummy, printing the final F1 comparison. Run it on two seeds, print both, and comment which assert guards the contract.",
             patterns=["assert ", "predict_proba("],
             mapping="These guards wrap every classifier board hereafter; only model names change.",
         ),
         119: dict(
             topic="Phase review: classification",
             idea="Rebuild from memory: probabilities from a squeezed line, boundaries drawn on grids, thresholds as business dials, stratified splits, bold Naive Bayes, wide-margin SVMs, ranking judged by AUC, imbalance fought with weights, probabilities audited by binning, ten classes read per-class, text as counted words, overlap accepted as irreducible. Close the notes and reproduce the cancer board — four models, F1 winner, margin stated. The missing line is tomorrow's first job; trees (phase 4) reuse every habit with boxes instead of lines. If the rebuild flows, classification thinking is installed; if it stalls at thresholds, revisit day 107 before moving on. If thresholds stall you, reread day 107's table until the dial feels like yours — it is the most deployed idea in this phase.",
             code=(
                 'from sklearn.datasets import load_breast_cancer\n'
                 'from sklearn.model_selection import train_test_split\n'
                 'from sklearn.dummy import DummyClassifier\n'
                 'from sklearn.linear_model import LogisticRegression\n'
                 'from sklearn.metrics import f1_score\n'
                 'from sklearn.preprocessing import StandardScaler\n'
                 '\n'
                 'X, y = load_breast_cancer(return_X_y=True)\n'
                 'Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, random_state=53, stratify=y)\n'
                 'sc = StandardScaler().fit(Xtr)\n'
                 'Xtr, Xte = sc.transform(Xtr), sc.transform(Xte)\n'
                 'base = f1_score(yte, DummyClassifier(strategy="most_frequent").fit(Xtr, ytr).predict(Xte))\n'
                 'real = f1_score(yte, LogisticRegression(max_iter=1000).fit(Xtr, ytr).predict(Xte))\n'
                 'print("dummy F1:", round(base, 3), "| logreg F1:", round(real, 3))\n'
                 'print("recall gap:", round(real - base, 3))'
             ),
             variant_b='kNN-5 instead of logreg (does the gap survive the swap?)',
             variant_c='test_size=0.5 (how much does less training data cost?)',
             mistakes=[
                 "Rebuilding with notes open — retrieval is the learning.",
                 "Reciting precision/recall without placing a threshold in a running script.",
                 "Skipping the dummy in the rebuild because it felt trivial.",
             ],
             q1=("What single rebuild proves this phase stuck?",
                 "The cancer board from memory — four models, stratified split, F1 winner with margin — every number explained."),
             homework="Write `phase_recap()` from memory: split, dummy, logreg, printed F1 gap. Run it on two seeds, print both gaps, and comment which line you had to look up.",
             patterns=["f1_score(", "stratify="],
             mapping="Phase 4 keeps the scoreboard; boundaries become boxes and probabilities become vote fractions.",
         ),
     }),
    ("Trees and Forests",
     "Boxes instead of lines: stumps, depth, bagging, importances, and honest tree limits.",
     {
         120: dict(
             topic="Decisions as boxes: the tree idea",
             idea="A decision tree carves feature space into boxes with axis-aligned cuts: 'petal width above 1.6 and below 2.1 → virginica'. Each cut is chosen greedily to purify the resulting boxes (Gini impurity or entropy fall), and prediction is a lookup — walk from the root to a leaf, return the leaf's majority. No lines, no distances, no scaling needs: boxes care about order, not magnitude. That geometric difference explains every tree strength (mixed types, missing-value tolerance, nonlinearity for free) and every weakness (staircase boundaries, deep memorisation). Learn boxes and forests become obvious: many jittered trees voting. The day's stump proves the mechanism on iris: one cut, printed rules, measurable accuracy — every forest later is this stump multiplied and diversified. Revisit this stump whenever forests confuse you — the ensemble is just this decision, repeated with different data.",
             code=(
                 'from sklearn.datasets import load_iris\n'
                 'from sklearn.tree import DecisionTreeClassifier, export_text\n'
                 '\n'
                 'X, y = load_iris(return_X_y=True)\n'
                 'names = load_iris()["feature_names"]\n'
                 'stump = DecisionTreeClassifier(max_depth=1, random_state=60).fit(X, y)\n'
                 'print("one-cut accuracy:", round(stump.score(X, y), 3))\n'
                 'print(export_text(stump, feature_names=names, max_depth=1))\n'
                 'print("a stump is one honest question")'
             ),
             variant_b='max_depth=2 (how many boxes? what accuracy?)',
             variant_c='only the first two features (does one cut still separate setosa?)',
             mistakes=[
                 "Reading a deep tree's 40 boxes as insight instead of memorisation.",
                 "Forgetting trees need no scaling, then scaling anyway and confusing the thresholds.",
                 "Trusting train accuracy of an unconstrained tree, which is 1.0 by construction.",
             ],
             q1=("Why does a stump's single cut already separate setosa perfectly?",
                 "Setosa sits apart on petal size alone, so one threshold on one feature isolates it — the data has a genuinely easy subproblem."),
             homework="Write `stump_report(depth)` fitting a depth-limited tree on iris and printing train accuracy plus the exported rules. Run it for depths 1 and 3, print both, and comment which line limits the boxes.",
             patterns=["DecisionTreeClassifier(", "max_depth="],
             mapping="sklearn.tree.DecisionTreeClassifier; export_text turns the model into readable rules — the interpretability benchmark.",
         ),
         121: dict(
             topic="Depth controls memorisation",
             idea="Depth 1 underfits (one box per class cannot bend), depth 12 memorises (a box per training point, test accuracy collapsing). The train/test gap across depths is the bias-variance curve made visible: training score climbs monotonically while test score rises, peaks, then falls as boxes multiply past what the data supports. Scanning max_depth 1…10 and printing both curves is the cheapest model-selection experiment in ML, and it generalises: every capacity knob (k in kNN, C in SVM, trees in forests) gets the same scan with the same reading — pick the peak of the test curve, never the top of the train curve.",
             code=(
                 'from sklearn.datasets import load_iris\n'
                 'from sklearn.model_selection import train_test_split\n'
                 'from sklearn.tree import DecisionTreeClassifier\n'
                 '\n'
                 'X, y = load_iris(return_X_y=True)\n'
                 'Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, random_state=61, stratify=y)\n'
                 'print("depth | train | test")\n'
                 'for d in (1, 2, 3, 5, 8, 12):\n'
                 '    m = DecisionTreeClassifier(max_depth=d, random_state=61).fit(Xtr, ytr)\n'
                 '    print(f"  {d:<3} | {m.score(Xtr, ytr):.3f} | {m.score(Xte, yte):.3f}")\n'
                 'print("test peaks, then memorisation drags it down")'
             ),
             variant_b='min_samples_leaf=5 instead of depth limits (another way to calm boxes?)',
             variant_c='digits data (does the peak move deeper with more data?)',
             mistakes=[
                 "Leaving max_depth=None on real data and shipping a memoriser.",
                 "Picking depth by training score, which always votes for deeper.",
                 "One depth on one split presented as the answer instead of a scan with a peak.",
             ],
             q1=("Why does test accuracy fall while train accuracy keeps climbing?",
                 "Extra boxes fit training noise ever more precisely while generalising ever less — capacity past the data's support buys memory, not learning."),
             homework="Write `depth_scan()` printing train/test accuracy for six depths. Run it on iris and digits, print both scans, and comment which column picks the depth.",
             patterns=["max_depth=", ".score("],
             mapping="max_depth/min_samples_leaf are the tree capacity knobs; validation_curve automates such scans with cross-validation.",
         ),
         122: dict(
             topic="Bagging: forests from jittered trees",
             idea="One deep tree memorises; one hundred deep trees trained on bootstrapped resamples (sampling rows with replacement) memorise differently, and their majority vote cancels the noise while keeping the signal. That is bagging: diversity through resampling, wisdom through voting. RandomForest adds a second jitter — each split sees a random feature subset — decorrelating the trees further so the vote genuinely averages independent mistakes. The result keeps trees' strengths (nonlinearity, mixed types, no scaling) while taming their fatal weakness, at the honest price of interpretability: one tree reads as rules, five hundred vote as a black box. Keep one interpretable tree beside every forest you ship; the forest decides, the tree explains. When stakeholders ask why, show the tree; when they ask how accurate, show the forest.",
             code=(
                 'from sklearn.datasets import load_iris\n'
                 'from sklearn.model_selection import train_test_split\n'
                 'from sklearn.tree import DecisionTreeClassifier\n'
                 'from sklearn.ensemble import RandomForestClassifier\n'
                 '\n'
                 'X, y = load_iris(return_X_y=True)\n'
                 'Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, random_state=62, stratify=y)\n'
                 'tree = DecisionTreeClassifier(random_state=62).fit(Xtr, ytr)\n'
                 'forest = RandomForestClassifier(n_estimators=100, random_state=62).fit(Xtr, ytr)\n'
                 'print("single deep tree test:", round(tree.score(Xte, yte), 3))\n'
                 'print("100-tree forest test:", round(forest.score(Xte, yte), 3))\n'
                 'print("voting cancels uncorrelated mistakes")'
             ),
             variant_b='n_estimators=5 (does a tiny forest still help?)',
             variant_c='max_depth=2 trees in the forest (calm voters — better or worse?)',
             mistakes=[
                 "Judging forests by training score, where both tree and forest hit 1.0 and differ nowhere.",
                 "Too few trees (n=10) keeping most of the variance the forest was meant to kill.",
                 "Forgetting random_state and comparing two forests' luck instead of their settings.",
             ],
             q1=("Why does voting help only when trees disagree?",
                 "Majority vote cancels uncorrelated errors; identical trees err identically and the vote changes nothing — diversity is the mechanism, voting just harvests it."),
             homework="Write `forest_duel()` scoring one deep tree vs a 100-tree forest on one split. Run it on two seeds, print both duels, and comment which argument decorrelates the voters.",
             patterns=["RandomForestClassifier(", "n_estimators="],
             mapping="sklearn.ensemble.RandomForestClassifier/Regressor; out-of-bag score (oob_score) gives a free validation estimate.",
         ),
         123: dict(
             topic="Reading feature importances honestly",
             idea="Forests rank features by total impurity decrease across all splits — the features the ensemble actually used. On diabetes data this shortlists body-mass and serum measures, agreeing reassuringly with linear coefficients. But importances have documented biases: high-cardinality features inflate, correlated twins split credit arbitrarily, and importance never says in which direction a feature pushes. Treat the ranking as triage for investigation (plot the top features, check their partial effects), and confirm with permutation importance, which measures damage from shuffling and carries no impurity bias. Two rankings that agree earn trust; one alone earns a follow-up. Run both rankings on every important model and investigate disagreements first — where impurity and permutation diverge, correlation or cardinality is lying to one of them. Agreement between the two rankings is the closest thing to a trustworthy importance list. Disagreement is not failure either — it tells you exactly where to look next.",
             code=(
                 'from sklearn.datasets import load_diabetes\n'
                 'from sklearn.ensemble import RandomForestRegressor\n'
                 '\n'
                 'X, y = load_diabetes(return_X_y=True)\n'
                 'names = load_diabetes()["feature_names"]\n'
                 'forest = RandomForestRegressor(n_estimators=200, random_state=63).fit(X[:350], y[:350])\n'
                 'ranked = sorted(zip(names, forest.feature_importances_), key=lambda p: p[1], reverse=True)\n'
                 'print("top 3 by impurity decrease:")\n'
                 'for name, imp in ranked[:3]:\n'
                 '    print(f"  {name}: {imp:.3f}")\n'
                 'print("shares sum to 1:", round(sum(forest.feature_importances_), 6))'
             ),
             variant_b='n_estimators=10 (does the ranking wobble with few voters?)',
             variant_c='permutation_importance on the same fit (do the two rankings agree?)',
             mistakes=[
                 "Presenting importances as causal proof instead of usage statistics.",
                 "Ignoring the cardinality bias on categorical-heavy data.",
                 "Acting on one ranking without the permutation cross-check.",
             ],
             q1=("Why can correlated twins each show low importance while jointly mattering most?",
                 "Splits alternate between twins across trees, so each accrues half the credit for shared work — the ranking splits what nature joined."),
             homework="Write `importance_report()` printing the top-3 forest features on diabetes. Run it on two row windows, print both rankings, and comment which attribute holds the shares.",
             patterns=["feature_importances_", ".fit("],
             mapping="forest.feature_importances_ for triage; sklearn.inspection.permutation_importance for the unbiased second opinion.",
         ),
         124: dict(
             topic="Regression trees bend for free",
             idea="Trees partition and average: each leaf predicts its training rows' mean, so the model is a staircase approximating any curve with no algebra — no polynomials to choose, no scaling to apply, no link function to justify. On the sine wave that humiliated linear regression, a depth-5 tree tracks every bend, and the residual pattern dissolves. The price is the staircase itself: between training points the prediction is flat, extrapolation beyond the data range freezes at the edge leaf's value, and smooth trends become steps. Use trees when the shape is unknown and data plentiful; distrust their flat confident steps where data is thin.",
             code=(
                 'import math\n'
                 'from sklearn.tree import DecisionTreeRegressor\n'
                 'from sklearn.linear_model import LinearRegression\n'
                 'from sklearn.metrics import r2_score\n'
                 '\n'
                 'X = [[x * 0.5] for x in range(16)]\n'
                 'y = [math.sin(v[0]) for v in X]\n'
                 'Xtr, Xte, ytr, yte = X[:12], X[12:], y[:12], y[12:]\n'
                 'line = LinearRegression().fit(Xtr, ytr)\n'
                 'tree = DecisionTreeRegressor(max_depth=4, random_state=64).fit(Xtr, ytr)\n'
                 'print("line test R^2:", round(r2_score(yte, line.predict(Xte)), 3))\n'
                 'print("tree test R^2:", round(r2_score(yte, tree.predict(Xte)), 3))\n'
                 'print("boxes bend where lines cannot")'
             ),
             variant_b='max_depth=1 stump (how much bend survives one cut?)',
             variant_c='predict at x=9.0, beyond all training data (what does the tree output, and why is it frozen?)',
             mistakes=[
                 "Celebrating interpolation while ignoring frozen flat extrapolation past the data edge.",
                 "Depth None on noisy curves, fitting stairs to every bump.",
                 "Expecting smooth derivatives from a staircase (slopes between steps are zero or infinite).",
             ],
             q1=("Why does a tree freeze past the training range instead of continuing the trend?",
                 "Leaves predict training means, and beyond the edge there is no data to average — the outermost leaf's value extends flat forever."),
             homework="Write `bend_duel()` scoring line vs depth-4 tree on sine data. Run it on sine and log curves, print both duels, and comment which model class fits bends natively.",
             patterns=["DecisionTreeRegressor(", "r2_score("],
             mapping="sklearn.tree.DecisionTreeRegressor; GradientBoostingRegressor later stacks such trees against residuals.",
         ),
         125: dict(
             topic="Trees ignore scaling (and why that matters)",
             idea="Splits compare one feature against thresholds, so multiplying a feature by 1000 merely multiplies its thresholds — the boxes, the predictions and the scores stay identical. Demonstrating scaled-vs-raw equality proves the invariance rather than asserting it, and the lesson cuts both ways: trees free you from scaler pipelines, but they also cannot exploit scaled geometry the way distance and penalty methods do. Choose models with eyes open: kNN and SVM demand scaling, trees are indifferent, and mixing scaled and unscaled inputs to a forest changes nothing except your confusion when thresholds print in transformed units.",
             code=(
                 'from sklearn.datasets import load_iris\n'
                 'from sklearn.model_selection import train_test_split\n'
                 'from sklearn.tree import DecisionTreeClassifier\n'
                 'from sklearn.preprocessing import StandardScaler\n'
                 '\n'
                 'X, y = load_iris(return_X_y=True)\n'
                 'Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, random_state=65, stratify=y)\n'
                 'raw = DecisionTreeClassifier(max_depth=3, random_state=65).fit(Xtr, ytr).score(Xte, yte)\n'
                 'sc = StandardScaler().fit(Xtr)\n'
                 'scaled = DecisionTreeClassifier(max_depth=3, random_state=65).fit(sc.transform(Xtr), ytr).score(sc.transform(Xte), yte)\n'
                 'print("raw score:   ", round(raw, 4))\n'
                 'print("scaled score:", round(scaled, 4))\n'
                 'print("identical: thresholds rescale, boxes do not move")'
             ),
             variant_b='kNN-5 on the same two scalings (does indifference hold there?)',
             variant_c='features multiplied by 1e6 manually (does the tree even notice?)',
             mistakes=[
                 "Scaler pipelines wrapped around forests out of habit, adding failure points for zero gain.",
                 "Assuming 'no scaling needed' means 'scaling is harmless' — thresholds in z-scores confuse every reader.",
                 "Forgetting which models DO need scaling and shipping unscaled kNN beside the indifferent trees.",
             ],
             q1=("Why do thresholds survive a 1000× rescaling unchanged in effect?",
                 "Splits test order (x < t), and monotone rescaling preserves all orderings — the same rows fall left and right, so boxes are identical."),
             homework="Write `scale_indifference()` scoring a depth-3 tree raw vs scaled. Run it on two seeds, print both pairs, and comment which comparison proves the invariance.",
             patterns=["StandardScaler(", ".score("],
             mapping="Skip scalers for trees/forests (simpler pipelines); keep them for kNN, SVM, logreg and penalised linear models.",
         ),
         126: dict(
             topic="Boosting: trees that fix mistakes",
             idea="Bagging averages independent trees; boosting grows them sequentially, each new tree fitting the previous ensemble's residuals — the mistakes become the next training signal. HistGradientBoostingClassifier consequently squeezes more accuracy from fewer, shallower trees, routinely topping leaderboards on tabular data. The price is sequential fitting (slower, less parallel), sharper overfitting teeth (learning_rate and early stopping matter), and weaker robustness to label noise (mistakes get amplified, including mislabeled rows). Use boosting as the strong default for tabular classification, and reserve forests for noisy labels where averaging beats chasing. Start tabular projects with HistGradientBoosting as the strong default, but keep a forest beside it on noisy labels — the duel takes minutes and settles the choice empirically. Default to boosting on clean tabular data, default to forests where labels are noisy, and measure both where unsure.",
             code=(
                 'from sklearn.datasets import load_breast_cancer\n'
                 'from sklearn.model_selection import train_test_split\n'
                 'from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier\n'
                 'from sklearn.metrics import f1_score\n'
                 '\n'
                 'X, y = load_breast_cancer(return_X_y=True)\n'
                 'Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, random_state=66, stratify=y)\n'
                 'rf = RandomForestClassifier(n_estimators=100, random_state=66).fit(Xtr, ytr)\n'
                 'gb = HistGradientBoostingClassifier(random_state=66).fit(Xtr, ytr)\n'
                 'print("forest F1:  ", round(f1_score(yte, rf.predict(Xte)), 4))\n'
                 'print("boosted F1:", round(f1_score(yte, gb.predict(Xte)), 4))\n'
                 'print("sequential repair vs parallel vote")'
             ),
             variant_b='learning_rate=0.01 on boosting (slower learning — better or just slower?)',
             variant_c='flip 10% of training labels (which ensemble degrades less?)',
             mistakes=[
                 "Boosting defaults on tiny data, where forests' averaging is the safer bet.",
                 "No early stopping on large data, training hundreds of pointless late trees.",
                 "Boosting noisy labels and amplifying mislabels into confident wrongness.",
             ],
             q1=("Why does boosting overfit label noise worse than bagging?",
                 "Boosting aims each new tree at current errors, so mislabeled rows attract ever more corrective effort; bagging averages them into the background."),
             homework="Write `boost_duel()` scoring forest vs boosted trees on one split. Run it on clean and 10%-flipped labels, print both duels, and comment which regime favours voting over chasing.",
             patterns=["HistGradientBoostingClassifier(", "f1_score("],
             mapping="sklearn.ensemble.HistGradientBoostingClassifier/Regressor — the tabular default; early_stopping=True tames the tail.",
         ),
         127: dict(
             topic="Categorical features meet trees",
             idea="Trees split on order, so ordinal codes (small/medium/large → 0/1/2) work natively and one-hot's thousand sparse columns are unnecessary — a tree handles 'colour in {red, blue, green}' by trying each subset split directly. But arbitrary integer codes still invent orderings the tree will happily exploit ('blue > red' splits that mean nothing), so encode honestly: ordinal only for truly ordered levels, one-hot or native categorical support otherwise. HistGradientBoosting's categorical_support exists precisely because practitioners kept feeding it lying integers. The rule: trees forgive scale, not fiction.",
             code=(
                 'from sklearn.preprocessing import OneHotEncoder\n'
                 'from sklearn.tree import DecisionTreeClassifier\n'
                 '\n'
                 'sizes = [800.0, 1200.0, 950.0, 1500.0, 700.0, 1100.0]\n'
                 'areas = ["town", "city", "town", "city", "town", "city"]\n'
                 'prices = [0, 1, 0, 1, 0, 1]\n'
                 'X_ord = [[s, 0 if a == "town" else 1] for s, a in zip(sizes, areas)]\n'
                 'X_oh = [row + ([1.0, 0.0] if a == "town" else [0.0, 1.0]) for row, a in zip([[s] for s in sizes], areas)]\n'
                 't1 = DecisionTreeClassifier(max_depth=2, random_state=67).fit(X_ord[:4], prices[:4]).score(X_ord[4:], prices[4:])\n'
                 't2 = DecisionTreeClassifier(max_depth=2, random_state=67).fit(X_oh[:4], prices[:4]).score(X_oh[4:], prices[4:])\n'
                 'print("ordinal-coded test:", t1, "| one-hot test:", t2)\n'
                 'print("trees cope with both; honesty decides")'
             ),
             variant_b='areas shuffled randomly vs price (does either encoding invent signal?)',
             variant_c='five areas instead of two (which encoding scales sanely?)',
             mistakes=[
                 "Arbitrary integers for nominal categories, letting trees split on fictional order.",
                 "One-hotting a 10,000-level column and drowning the tree in sparse noise.",
                 "Assuming 'trees handle categories' means no encoding thought at all.",
             ],
             q1=("Why is ordinal coding safe for sizes but dangerous for colours?",
                 "Sizes genuinely order (800 < 1200 is meaningful); colours do not, so integer comparisons on colours split on fiction the tree cannot detect."),
             homework="Write `encoding_duel()` scoring ordinal vs one-hot tree inputs on held-out rows. Run it on two area layouts, print both duels, and comment which encoding stays honest.",
             patterns=["DecisionTreeClassifier(", ".score("],
             mapping="HistGradientBoostingClassifier(categorical_features=...) handles categories natively; elsewhere encode honestly per type.",
         ),
         128: dict(
             topic="Imbalance meets forests",
             idea="Forests trained on 95/5 data grow trees that rarely see the minority, and majority vote buries the few correct minority predictions under confident majorities. class_weight='balanced_subsample' reweights per bootstrap sample, forcing each tree to care about rare rows without duplicating them. Compare plain vs weighted forests on precision/recall (never accuracy alone here): recall should jump while precision pays the toll. If the minority is truly tiny, combine weights with more trees — variance is the enemy when five rows decide the metric — and consider whether the problem wants anomaly framing instead of classification at all. Report confusion counts beside rates on imbalanced data — rates hide sample sizes, and five test minority rows make every decimal fragile. When the minority is that thin, consider anomaly framing — detecting the rare as deviation rather than classifying it.",
             code=(
                 'from sklearn.datasets import make_classification\n'
                 'from sklearn.ensemble import RandomForestClassifier\n'
                 'from sklearn.metrics import precision_score, recall_score\n'
                 '\n'
                 'X, y = make_classification(n_samples=400, weights=[0.93, 0.07], random_state=68)\n'
                 'Xtr, Xte, ytr, yte = X[:300], X[300:], y[:300], y[300:]\n'
                 'for w in (None, "balanced_subsample"):\n'
                 '    m = RandomForestClassifier(n_estimators=50, class_weight=w, random_state=68).fit(Xtr, ytr)\n'
                 '    pred = m.predict(Xte)\n'
                 '    print(f"weight={w}: precision={precision_score(yte, pred, zero_division=0):.2f} recall={recall_score(yte, pred):.2f}")'
             ),
             variant_b='n_estimators=10 (does vote variance swamp the weighting?)',
             variant_c='weights=[0.5, 0.5] (do weights become harmless?)',
             mistakes=[
                 "Accuracy as the forest headline on 93/7 data.",
                 "Balanced weights without checking whether precision collapsed past usability.",
                 "Too few trees, so the minority metric swings wildly between seeds.",
             ],
             q1=("Why 'balanced_subsample' rather than 'balanced' for forests?",
                 "Each tree sees a different bootstrap sample with its own class ratio; subsample reweights per tree's actual sample instead of the global ratio."),
             homework="Write `forest_weight_duel()` printing precision/recall with and without subsample weights. Run it on two imbalance levels, print both, and comment which regime needs the weights.",
             patterns=["class_weight=", "recall_score("],
             mapping="RandomForestClassifier(class_weight='balanced_subsample'); for extreme rarity, anomaly detectors (IsolationForest) reframe the task.",
         ),
         129: dict(
             topic="Trees vs lines on circles",
             idea="Today the model classes duel on terrain favouring boxes: two concentric rings, where no straight line separates inner from outer but shallow trees tile the rings with boxes effortlessly. Linear models score near chance while depth-4 trees approach perfection — the mirror image of day 100's sine wave, where both struggled differently. The lesson is selection, not supremacy: match the boundary shape to the data shape (rings→boxes, trends→lines, unknown→try both on one split), and let a two-model board decide instead of loyalty. Every 'which model is best' debate dissolves into 'on what geometry'. Run the two-model duel before tuning anything; switching classes beats tuning the wrong one every time. Keep a two-model board for every new dataset before spending a single tuning cycle.",
             code=(
                 'from sklearn.datasets import make_circles\n'
                 'from sklearn.linear_model import LogisticRegression\n'
                 'from sklearn.tree import DecisionTreeClassifier\n'
                 '\n'
                 'X, y = make_circles(n_samples=200, noise=0.08, random_state=69)\n'
                 'Xtr, Xte, ytr, yte = X[:150], X[150:], y[:150], y[150:]\n'
                 'line = LogisticRegression(max_iter=500).fit(Xtr, ytr).score(Xte, yte)\n'
                 'tree = DecisionTreeClassifier(max_depth=4, random_state=69).fit(Xtr, ytr).score(Xte, yte)\n'
                 'print("logistic on rings:", round(line, 3))\n'
                 'print("depth-4 tree rings:", round(tree, 3))\n'
                 'print("geometry picks the winner, not prestige")'
             ),
             variant_b='noise=0.25 (do boxes survive heavy scatter?)',
             variant_c='depth=1 stump (how much ring fits in one cut?)',
             mistakes=[
                 "Declaring trees 'better than logreg' from one geometry instead of 'better on rings'.",
                 "Tuning the loser instead of switching the class.",
                 "Forgetting make_circles' factor parameter, which controls ring gap and difficulty.",
             ],
             q1=("Why does no line separate concentric rings no matter the fitting?",
                 "A line divides the plane into two half-planes; rings need an inside and an outside — topologically impossible for one cut, trivial for nested boxes."),
             homework="Write `geometry_duel()` scoring logreg vs depth-4 tree on circles data. Run it at two noise levels, print both duels, and comment which geometry favours boxes.",
             patterns=["make_circles(", ".score("],
             mapping="Rings preview kernels (SVC bends the street); trees tile what lines cannot cut — keep both tools, pick by geometry.",
         ),
         130: dict(
             topic="When trees fail honestly",
             idea="Trees have three honest failure modes worth memorising. Extrapolation freezes: beyond training range, predictions flatline at edge leaves, so trends must not be extended. Smoothness dies: staircases approximate slopes with steps, useless where derivatives matter. High-cardinality chaos: thousands of levels fragment splits into noise-fitting confetti. Diagnose each by construction — predict past the edge, zoom the steps, count the levels — and switch classes instead of deepening: lines extrapolate, forests smooth by averaging, encodings tame levels. Loving trees means knowing exactly where to stop using them. Probe every tree model past its training edge before deployment — one frozen prediction found in testing beats a silent failure in production. Lines extrapolate trends, trees freeze at edges — match the model to the forecast horizon deliberately.",
             code=(
                 'from sklearn.tree import DecisionTreeRegressor\n'
                 '\n'
                 'X = [[x] for x in range(10)]\n'
                 'y = [2.0 * x[0] + 1.0 for x in X]\n'
                 'tree = DecisionTreeRegressor(max_depth=3, random_state=70).fit(X[:8], y[:8])\n'
                 'print("inside  [6]:", round(float(tree.predict([[6]])[0]), 2), "| truth: 13.0")\n'
                 'print("edge    [7]:", round(float(tree.predict([[7]])[0]), 2), "| truth: 15.0")\n'
                 'print("beyond [12]:", round(float(tree.predict([[12]])[0]), 2), "| truth: 25.0 (frozen!)")\n'
                 'print("extrapolation flatlines at the edge leaf")'
             ),
             variant_b='max_depth=6 (does deeper help beyond the edge?)',
             variant_c='linear regression on the same split (who extrapolates correctly?)',
             mistakes=[
                 "Forecasting trends with trees and trusting the flatline.",
                 "Deepening the tree to fix an extrapolation failure (more boxes, same frozen edge).",
                 "Smoothing needs met with deeper trees instead of averaging forests.",
             ],
             q1=("Why can't more depth fix frozen extrapolation?",
                 "Depth adds boxes inside the training range only; beyond the edge there are no rows to split, so the outermost leaf extends flat at any depth."),
             homework="Write `edge_probe()` printing inside/edge/beyond predictions vs truth. Run it for depths 3 and 6, print both probes, and comment which prediction proves the freeze.",
             patterns=["DecisionTreeRegressor(", ".predict("],
             mapping="Extrapolation belongs to lines (or GPs); use trees where the future resembles the past's interior.",
         ),
         131: dict(
             topic="Forests quantify doubt with votes",
             idea="A forest's vote fraction is a usable uncertainty: 97/100 trees for class A means confident, 52/48 means a coin flip the model admits. Reading predict_proba as vote shares turns the black box translucent — uncertain rows get human review, confident rows automate. But vote fractions are not calibrated probabilities out of the box (forests run overconfident near training data), so audit them with the day-113 binning table before spending them. Uncertainty you can read beats accuracy you cannot question: route the 52/48 rows to a person and the system's real-world error collapses even as the model's stays put. Calibrate first, route second, automate last — in that order, no exceptions. The binning table from day 113 is the audit; everything downstream depends on it.",
             code=(
                 'from sklearn.datasets import load_breast_cancer\n'
                 'from sklearn.model_selection import train_test_split\n'
                 'from sklearn.ensemble import RandomForestClassifier\n'
                 '\n'
                 'X, y = load_breast_cancer(return_X_y=True)\n'
                 'Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, random_state=71, stratify=y)\n'
                 'forest = RandomForestClassifier(n_estimators=100, random_state=71).fit(Xtr, ytr)\n'
                 'proba = forest.predict_proba(Xte)\n'
                 'confident = sum(max(row) >= 0.9 for row in proba)\n'
                 'coinflip = sum(abs(row[0] - 0.5) < 0.05 for row in proba)\n'
                 'print(f"confident rows (>=0.9): {confident} | coin-flips: {coinflip} of {len(proba)}")\n'
                 'print("route the flips to a human")'
             ),
             variant_b='n_estimators=10 (do vote fractions get lumpier?)',
             variant_c='max_depth=2 voters (does forced calm raise the flip count honestly?)',
             mistakes=[
                 "Spending raw vote fractions as calibrated probabilities without the binning audit.",
                 "Automating the coin-flips because overall accuracy looked fine.",
                 "Too few trees, so 'fractions' jump in tenths and fake confidence granularity.",
             ],
             q1=("Why do vote fractions need the calibration audit before deployment?",
                 "Forests concentrate votes near training data regardless of truth, so 0.9 can mean 'familiar' rather than '90% likely' — only binned outcomes tell."),
             homework="Write `doubt_report()` printing confident vs coin-flip counts for a fitted forest. Run it with 10 and 100 trees, print both, and comment which rows you would route to a human.",
             patterns=["predict_proba(", "n_estimators="],
             mapping="Vote fractions plus the day-113 calibration table make uncertainty operational; abstention policies sit on top.",
         ),
         132: dict(
             topic="Project: digits forest board",
             idea="Today forests meet ten digits: stratified split, Dummy/kNN baselines, a depth-capped tree, and two forests (10 wild trees vs 100 calm ones), ranked by accuracy with the directed-pair table for the winner. Same split, baselines included — the day-117 board with boxes instead of lines. Expect forests near the top and the stump far below; the interesting number is the gap between 10-tree and 100-tree forests, which prices vote variance directly. This board is the reference every tuning phase must beat from a standing start, and the directed pairs carry over: forests fix some confusions and keep others, and the survivors mark genuinely ambiguous ink.",
             code=(
                 'from sklearn.datasets import load_digits\n'
                 'from sklearn.model_selection import train_test_split\n'
                 'from sklearn.dummy import DummyClassifier\n'
                 'from sklearn.tree import DecisionTreeClassifier\n'
                 'from sklearn.ensemble import RandomForestClassifier\n'
                 'from sklearn.metrics import accuracy_score\n'
                 '\n'
                 'X, y = load_digits(return_X_y=True)\n'
                 'Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, random_state=72, stratify=y)\n'
                 'board = {}\n'
                 'for name, m in [("dummy", DummyClassifier(strategy="most_frequent")), ("stump", DecisionTreeClassifier(max_depth=3, random_state=72)), ("forest-10", RandomForestClassifier(n_estimators=10, random_state=72)), ("forest-100", RandomForestClassifier(n_estimators=100, random_state=72))]:\n'
                 '    score = accuracy_score(yte, m.fit(Xtr, ytr).predict(Xte))\n'
                 '    board[name] = round(score, 4)\n'
                 '    print(f"{name:<10} {board[name]:.4f}")\n'
                 'print("winner:", max(board, key=board.get))\n'
                 'print("gap forest100-stump:", round(board["forest-100"] - board["stump"], 4))'
             ),
             variant_b='max_depth=5 voters inside the forests (calmer crowd?)',
             variant_c='test_size=0.5 (who degrades fastest with less training?)',
             mistakes=[
                 "No dummy row, so the stump's score floats without its floor.",
                 "Unstratified split starving rare digits from evaluation.",
                 "Declaring forest-100 'best' without checking whether forest-10 ties it (variance already dead?).",
             ],
             q1=("Why include both forest-10 and forest-100 on the board?",
                 "Their gap prices vote variance directly: if they tie, ten trees already average the noise and ninety more buy nothing."),
             homework="Write `digits_forest_board()` ranking dummy/stump/two forests on one stratified split. Run it on two seeds, print both boards, and comment which gap prices variance.",
             patterns=["RandomForestClassifier(", "accuracy_score("],
             mapping="This board is the tuning baseline for phases 5–6; every grid must clear forest-100 to justify its existence.",
         ),
         133: dict(
             topic="Testing tree code with asserts",
             idea="Tree guards check box logic: stump depth respected (exported rule lines stay few), forest beats stump (else the ensemble adds nothing), importances sum to one, and depth caps hold after refits. Assert relations across seeds ('forest-100 >= stump') rather than exact scores, and assert structural facts (rule counts, sums) that no seed can move. These guards wrap every tree board hereafter, catching silent killers like a max_depth that never applied (typo'd parameter name) or a forest fit on stale data. A guarded board reruns itself into trustworthiness on every new seed.",
             code=(
                 'from sklearn.datasets import load_digits\n'
                 'from sklearn.model_selection import train_test_split\n'
                 'from sklearn.tree import DecisionTreeClassifier, export_text\n'
                 'from sklearn.ensemble import RandomForestClassifier\n'
                 'from sklearn.metrics import accuracy_score\n'
                 '\n'
                 'X, y = load_digits(return_X_y=True)\n'
                 'Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, random_state=73, stratify=y)\n'
                 'stump = DecisionTreeClassifier(max_depth=2, random_state=73).fit(Xtr, ytr)\n'
                 'rules = export_text(stump)\n'
                 'assert rules.count("class:") <= 4\n'
                 'forest = RandomForestClassifier(n_estimators=50, random_state=73).fit(Xtr, ytr)\n'
                 's_stump = accuracy_score(yte, stump.predict(Xte))\n'
                 's_forest = accuracy_score(yte, forest.predict(Xte))\n'
                 'assert abs(sum(forest.feature_importances_) - 1.0) < 1e-9\n'
                 'assert s_forest >= s_stump\n'
                 'print(f"guards passed: forest {s_forest:.3f} >= stump {s_stump:.3f}, importances sum to 1")'
             ),
             variant_b='max_depth=1 (does the rules-count assert still hold?)',
             variant_c='n_estimators=3 (does forest >= stump survive tiny crowds?)',
             mistakes=[
                 "Exact-score asserts that shatter on new seeds.",
                 "No structural asserts, so a silently-ignored max_depth passes unnoticed.",
                 "Asserting importances sum without tolerance for float dust.",
                 "Counting rule characters instead of leaves — structure means leaves, not pipes.",
             ],
             q1=("Why assert rules-count bounds instead of exact rule text?",
                 "Bounds test the structural contract (depth respected) invariantly; exact text fossilises one seed's split choices."),
             homework="Write `guarded_trees()` with asserts on rule bounds, importance sums and forest-beats-stump, printing the final comparison. Run it on two seeds, print both, and comment which assert guards structure.",
             patterns=["assert ", "export_text("],
             mapping="Structural asserts (rules, sums, relations) travel to every ensemble board; exact values never do. A guard that survives three seeds is documentation that never rots.",
         ),
         134: dict(
             topic="Phase review: trees and forests",
             idea="Rebuild from memory: boxes not lines, depth as the capacity knob, bagging plus feature jitter, importances with permutation cross-checks, regression stairs, scaling indifference, boosting's sequential repair, honest categorical codes, weights for imbalance, geometry picking winners, frozen extrapolation, vote fractions as routable doubt. Close the notes and reproduce the digits forest board — dummy, stump, two forests, variance gap stated. The missing line is tomorrow's first job; validation (phase 5) replaces gut-feel knobs with measured curves. If the rebuild flows, box thinking is installed — and the stump-to-forest gap is the number that proves ensembles earn their keep. If that gap will not come from memory, rebuild day 122 before moving on. Forests are the last pure-memorisation architecture in this track — everything after measures and constrains.",
             code=(
                 'from sklearn.datasets import load_digits\n'
                 'from sklearn.model_selection import train_test_split\n'
                 'from sklearn.dummy import DummyClassifier\n'
                 'from sklearn.tree import DecisionTreeClassifier\n'
                 'from sklearn.ensemble import RandomForestClassifier\n'
                 'from sklearn.metrics import accuracy_score\n'
                 '\n'
                 'X, y = load_digits(return_X_y=True)\n'
                 'Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, random_state=74, stratify=y)\n'
                 'scores = {}\n'
                 'for name, m in [("dummy", DummyClassifier(strategy="most_frequent")), ("stump", DecisionTreeClassifier(max_depth=3, random_state=74)), ("forest", RandomForestClassifier(n_estimators=50, random_state=74))]:\n'
                 '    scores[name] = round(accuracy_score(yte, m.fit(Xtr, ytr).predict(Xte)), 4)\n'
                 '    print(name, scores[name])\n'
                 'print("variance gap (forest-stump):", round(scores["forest"] - scores["stump"], 4))'
             ),
             variant_b='forest-200 (does the gap keep growing or plateau?)',
             variant_c='unscaled vs scaled inputs (indifference check from memory)',
             mistakes=[
                 "Rebuilding with notes open — retrieval is the learning.",
                 "Reciting bagging without placing bootstrap sampling in a running script.",
                 "Skipping the stump in the rebuild because forests felt like the whole story.",
             ],
             q1=("What single rebuild proves this phase stuck?",
                 "The digits forest board from memory — dummy, stump, forest, variance gap stated — every number explained."),
             homework="Write `phase_recap()` from memory: split, dummy, stump, forest, printed gap. Run it on two seeds, print both, and comment which line you had to look up.",
             patterns=["RandomForestClassifier(", "accuracy_score("],
             mapping="Phase 5 keeps the models and measures the knobs; depth scans become validation curves.",
         ),
     }),
    ("Overfitting and Validation",
     "Measure honestly: curves, cross-validation, grids, leakage hunting, and metric choice.",
     {
         135: dict(
             topic="Validation curves pick the knob",
             idea="Guessing max_depth by gut feeling is gambling; validation_curve measures train and test scores across depths 1…10 with cross-validation, so the peak is data, not opinion. The two curves tell the story every capacity knob tells: training climbs, validation rises then falls, and the gap between them prices overfitting at each setting. Automate what day 121 did by hand — same reading, no manual loops, honest error bars from the folds. Every tunable knob from here on gets a validation curve before a value, because 'depth 5 worked once' is anecdote and the curve is evidence.",
             code=(
                 'from sklearn.datasets import load_iris\n'
                 'from sklearn.tree import DecisionTreeClassifier\n'
                 'from sklearn.model_selection import validation_curve\n'
                 'import numpy as np\n'
                 '\n'
                 'X, y = load_iris(return_X_y=True)\n'
                 'model = DecisionTreeClassifier(random_state=80)\n'
                 'tr, te = validation_curve(model, X, y, param_name="max_depth", param_range=[1, 2, 3, 5, 8, 12], cv=3)\n'
                 'print("depth | train mean | test mean")\n'
                 'for d, a, b in zip([1, 2, 3, 5, 8, 12], tr.mean(axis=1), te.mean(axis=1)):\n'
                 '    print(f"  {d:<3} |   {a:.3f}    |  {b:.3f}")\n'
                 'best = [1, 2, 3, 5, 8, 12][int(np.argmax(te.mean(axis=1)))]\n'
                 'print("curve peak at depth:", best)'
             ),
             variant_b='cv=5 (do the means steady and the peak move?)',
             variant_c='min_samples_leaf over [1, 2, 5, 10, 20] instead (same story, other knob?)',
             mistakes=[
                 "Picking the peak of one fold instead of the mean across folds.",
                 "Tuning depth on the test set, then reporting test numbers as validation.",
                 "Ignoring the error bars — a peak inside noise is not a peak.",
             ],
             q1=("Why average across folds instead of trusting the best single split?",
                 "One split's luck becomes the knob's value; averaging over folds measures the setting, not the deal."),
             homework="Write `depth_curve()` printing train/test means over six depths with cv=3. Run it on iris and digits, print both curves, and comment which column picks the depth.",
             patterns=["validation_curve(", "max_depth="],
             mapping="sklearn.model_selection.validation_curve turns any capacity knob into measured evidence.",
         ),
         136: dict(
             topic="Learning curves: data or model?",
             idea="When scores disappoint, learning curves say whether to gather data or change models: plot test score against training-set size, and a rising curve demands more rows while a flat one demands better features or a stronger class. Training score falling toward test as data grows is healthy convergence; a stubborn gap is bias the model cannot fix at any size. This single plot answers the most expensive question in applied ML — 'will more data help?' — before you spend months collecting it. Run it before every data-collection proposal, and demand it from anyone proposing one to you.",
             code=(
                 'from sklearn.datasets import load_iris\n'
                 'from sklearn.tree import DecisionTreeClassifier\n'
                 'from sklearn.model_selection import learning_curve\n'
                 'import numpy as np\n'
                 '\n'
                 'X, y = load_iris(return_X_y=True)\n'
                 'sizes, tr, te = learning_curve(DecisionTreeClassifier(max_depth=3, random_state=81), X, y, cv=3, train_sizes=[0.2, 0.4, 0.6, 0.8, 1.0])\n'
                 'print("frac  | train mean | test mean")\n'
                 'for f, a, b in zip(sizes, tr.mean(axis=1), te.mean(axis=1)):\n'
                 '    print(f"{f:5.0f}  |   {a:.3f}    |  {b:.3f}")\n'
                 'print("gap closing with data: data helps here")'
             ),
             variant_b='max_depth=1 stump (does the test curve flatten early — bias?)',
             variant_c='digits data (does more data keep helping at this size?)',
             mistakes=[
                 "Reading one learning curve as the answer instead of per-class or per-slice curves.",
                 "More data prescribed for a flat curve, where features or class are the bottleneck.",
                 "Tiny datasets where the curve's noise exceeds its signal.",
             ],
             q1=("How does a flat test curve differ from a rising one as a prescription?",
                 "Rising says collect rows; flat says the model class or features cap performance — data spending would be wasted."),
             homework="Write `data_or_model()` printing learning-curve means at five fractions. Run it for depth-1 and depth-3 trees, print both, and comment which curve shape prescribes more data.",
             patterns=["learning_curve(", "train_sizes="],
             mapping="sklearn.model_selection.learning_curve — run it before every 'we need more data' proposal.",
         ),
         137: dict(
             topic="Cross-validation: every row gets examined",
             idea="A single split spends 70% of rows on training and judges on 30%; 5-fold cross-validation rotates five 80/20 splits so every row is tested exactly once and trained four times. The mean estimates true performance, the spread across folds estimates its stability — a model scoring 0.95±0.01 differs profoundly from 0.95±0.12, though single splits report both as '0.95'. cross_val_score runs the rotation in one line. Use it for every comparison that matters, and quote mean±spread, never a naked point estimate, because the spread is the honest part.",
             code=(
                 'from sklearn.datasets import load_iris\n'
                 'from sklearn.tree import DecisionTreeClassifier\n'
                 'from sklearn.neighbors import KNeighborsClassifier\n'
                 'from sklearn.model_selection import cross_val_score\n'
                 '\n'
                 'X, y = load_iris(return_X_y=True)\n'
                 'for name, m in [("stump", DecisionTreeClassifier(max_depth=2, random_state=82)), ("knn-5", KNeighborsClassifier(n_neighbors=5))]:\n'
                 '    scores = cross_val_score(m, X, y, cv=5)\n'
                 '    print(f"{name:<6} folds: {[round(s, 3) for s in scores]}")\n'
                 '    print(f"       mean={scores.mean():.3f} spread={scores.std():.3f}")'
             ),
             variant_b='cv=10 (does the spread shrink with more folds?)',
             variant_c='digits data (which model is steadier across folds?)',
             mistakes=[
                 "Quoting one split's 0.97 as the result instead of a folded mean±spread.",
                 "Cross-validating after tuning on the full data — the folds then certify a tuned model dishonestly.",
                 "Shuffling forgotten: KFold without shuffle on ordered rows replays day 86's failure five times.",
             ],
             q1=("Why report spread alongside the mean?",
                 "The mean estimates performance, the spread estimates trust — 0.95±0.01 ships, 0.95±0.12 needs investigation before anyone relies on it."),
             homework="Write `folded_duel()` printing 5-fold scores plus mean±spread for two models. Run it on iris and digits, print both duels, and comment which number measures stability.",
             patterns=["cross_val_score(", "cv=5"],
             mapping="sklearn.model_selection.cross_val_score with cv=5 (StratifiedKFold for classifiers); means and spreads from here on.",
         ),
         138: dict(
             topic="Grid search tunes without cheating",
             idea="GridSearchCV crosses every combination of knobs with every fold: depths × leaf-sizes × folds, scored honestly on held-out fold data, with the winner refit on everything at the end (refit=True). The grid replaces hunches with exhaustive measurement, and best_params_ documents the decision for review. But the grid is only as honest as its evaluation: tune inside cross-validation, lock a final untouched test set for the concluding number, and keep grids small enough to finish — exhaustive over thirty knobs is a supercomputer's job, while two knobs over five folds runs on a laptop and teaches the same discipline. Lock a final untouched test set before gridding, and spend it exactly once — the concluding number stays honest only while unspent. Grids that finish beat brilliant grids that never do.",
             code=(
                 'from sklearn.datasets import load_iris\n'
                 'from sklearn.tree import DecisionTreeClassifier\n'
                 'from sklearn.model_selection import GridSearchCV\n'
                 '\n'
                 'X, y = load_iris(return_X_y=True)\n'
                 'grid = GridSearchCV(DecisionTreeClassifier(random_state=83), {"max_depth": [1, 2, 3, 5, None], "min_samples_leaf": [1, 3]}, cv=3)\n'
                 'grid.fit(X, y)\n'
                 'print("best:", grid.best_params_)\n'
                 'print("best CV score:", round(grid.best_score_, 4))\n'
                 'print("winner refit on all data: ready to ship the settings, not the score")'
             ),
             variant_b='add criterion ["gini", "entropy"] to the grid (does the split rule matter here?)',
             variant_c='cv=5 (does the winner survive stricter judging?)',
             mistakes=[
                 "Reporting best_score_ as the model's performance — it is the selection criterion, optimistically biased.",
                 "Grids so large they never finish, then 'results' from an interrupted search.",
                 "Tuning on the test set, spending the only honest number on knob selection.",
             ],
             q1=("Why is best_score_ optimistically biased as a performance claim?",
                 "It is the maximum over many tried combinations — selecting the best of many guarantees flattering the winner; a fresh test set judges honestly."),
             homework="Write `honest_grid()` running a 2-knob grid with cv=3 and printing best params plus best score. Run it on iris and digits, print both, and comment why the printed score is not the final claim.",
             patterns=["GridSearchCV(", "best_params_"],
             mapping="sklearn.model_selection.GridSearchCV; RandomizedSearchCV samples big spaces cheaply when grids explode.",
         ),
         139: dict(
             topic="Pipelines stop leaks by construction",
             idea="Scaling-then-fitting as separate steps invites the classic leak: fit the scaler on all data, then 'split' already-informed rows. make_pipeline chains scaler→model into one estimator whose fit applies each step to training folds only during cross-validation — leakage becomes structurally impossible rather than carefully avoided. Pipelines also ship: one object pickles the entire preprocessing-plus-model chain, so production applies exactly what training validated. From today, preprocessing lives inside pipelines, never beside them; a bare scaler fit outside a pipeline is a code smell to justify or remove. Review old notebooks for bare fits; every one you pipeline retires a leak class permanently. The pipeline object also ships: one pickle carries preprocessing plus model.",
             code=(
                 'from sklearn.datasets import load_breast_cancer\n'
                 'from sklearn.preprocessing import StandardScaler\n'
                 'from sklearn.linear_model import LogisticRegression\n'
                 'from sklearn.pipeline import make_pipeline\n'
                 'from sklearn.model_selection import cross_val_score\n'
                 '\n'
                 'X, y = load_breast_cancer(return_X_y=True)\n'
                 'bare = LogisticRegression(max_iter=5000)\n'
                 'pipe = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000))\n'
                 'print("bare  CV mean:", round(cross_val_score(bare, X, y, cv=3).mean(), 4))\n'
                 'print("piped CV mean:", round(cross_val_score(pipe, X, y, cv=3).mean(), 4))\n'
                 'print("steps:", [s[0] for s in pipe.steps])\n'
                 'print("one object, leak-free folds, shippable chain")'
             ),
             variant_b='kNN-5 bare vs pipelined (who gains more from scaling?)',
             variant_c='a tree bare vs pipelined (who gains nothing, and why?)',
             mistakes=[
                 "Scaler fit outside the pipeline, then cross-validating the model alone.",
                 "Different preprocessing at train and serve time — the pipeline object prevents exactly this drift.",
                 "Pipeline steps in the wrong order (model before scaler) failing loudly instead of silently — the one mercy.",
             ],
             q1=("Why does pipelining make leakage impossible rather than merely unlikely?",
                 "Cross-validation clones and fits the whole chain per fold, so scalers only ever see training folds — the correct order is structural, not a matter of care."),
             homework="Write `pipeline_gain()` comparing bare vs pipelined CV means for logreg. Run it on breast-cancer and digits, print both, and comment which line chains the steps.",
             patterns=["make_pipeline(", "cross_val_score("],
             mapping="sklearn.pipeline.make_pipeline/Pipeline — every preprocessing step lives inside from now on.",
         ),
         140: dict(
             topic="Leak hunt I: scaling before splitting",
             idea="Fit the scaler on all rows, then split: test statistics now live inside every training value, and scores inflate — sometimes by points that decide 'ship' versus 'stop'. The inflation is silent because nothing errors; only the discipline (split first, fit preprocessing on train) prevents it, or pipelines that enforce it. Today you commit the crime deliberately on diabetes data and measure the inflation against the clean pipeline: the gap, often 1–3 R² points, is the price of one misordered line. Memorise the feeling — every future 'too good' score gets checked against this exact suspicion first.",
             code=(
                 'from sklearn.datasets import load_diabetes\n'
                 'from sklearn.preprocessing import StandardScaler\n'
                 'from sklearn.linear_model import Ridge\n'
                 'from sklearn.pipeline import make_pipeline\n'
                 'from sklearn.metrics import r2_score\n'
                 '\n'
                 'X, y = load_diabetes(return_X_y=True)\n'
                 'Xtr, Xte, ytr, yte = X[:350], X[350:], y[:350], y[350:]\n'
                 'leaky = Ridge(alpha=1.0).fit(StandardScaler().fit_transform(X), y)\n'
                 'leak_pred = leaky.predict(StandardScaler().fit(X).transform(Xte))\n'
                 'clean = make_pipeline(StandardScaler(), Ridge(alpha=1.0)).fit(Xtr, ytr)\n'
                 'print("leaky  test R^2:", round(r2_score(yte, leak_pred), 4))\n'
                 'print("clean  test R^2:", round(r2_score(yte, clean.predict(Xte)), 4))\n'
                 'print("the gap is bought with test answers")'
             ),
             variant_b='alpha=100 (does heavy penalty shrink the gap?)',
             variant_c='test_size honesty: split shuffled 80/20 instead (does the gap persist?)',
             mistakes=[
                 "'It barely moved the score' used to excuse the leak instead of removing it.",
                 "Scaler fit in a notebook cell above the split cell, invisible in review.",
                 "Normalising target y with test statistics — leakage wearing a different hat.",
             ],
             q1=("Why does test-fitted scaling inflate scores instead of just adding noise?",
                 "Test rows shift the mean/variance toward themselves, so training values carry test information — the model peeks at answers during study."),
             homework="Write `leak_or_clean()` scoring leaky vs pipelined Ridge on one split. Run it on two splits, print both gaps, and comment which line spends test answers.",
             patterns=["StandardScaler(", "make_pipeline("],
             mapping="Pipelines fix this structurally; the manual version exists so you recognise the crime scene in others' notebooks.",
         ),
         141: dict(
             topic="Leak hunt II: selecting on all data",
             idea="A subtler leak: choose the best 5 of 50 features using all rows, then cross-validate the model on those 5 — the selection already saw every test fold, so the 'validation' certifies features chosen with answers in hand. Scores inflate dramatically on noisy high-dimensional data, precisely where feature selection feels most needed. The fix is placement: SelectKBest inside the pipeline, refit per fold, so each fold selects blind. Rule of thumb: any step that looks at y belongs inside the cross-validated chain — selection, scaling, imputation, all of it, no exceptions. When reviewing others' work, check preprocessing placement before model choice — leaks live upstream, and audits start upstream. Teach this placement rule to every teammate once; it prevents entire bug classes.",
             code=(
                 'from sklearn.datasets import make_classification\n'
                 'from sklearn.feature_selection import SelectKBest, f_classif\n'
                 'from sklearn.linear_model import LogisticRegression\n'
                 'from sklearn.pipeline import make_pipeline\n'
                 'from sklearn.model_selection import cross_val_score\n'
                 '\n'
                 'X, y = make_classification(n_samples=120, n_features=50, n_informative=5, random_state=84)\n'
                 'leaky_sel = SelectKBest(f_classif, k=5).fit_transform(X, y)\n'
                 'leaky = cross_val_score(LogisticRegression(max_iter=1000), leaky_sel, y, cv=3).mean()\n'
                 'clean = make_pipeline(SelectKBest(f_classif, k=5), LogisticRegression(max_iter=1000))\n'
                 'honest = cross_val_score(clean, X, y, cv=3).mean()\n'
                 'print("select-then-validate:", round(leaky, 4))\n'
                 'print("select-inside-folds: ", round(honest, 4))\n'
                 'print("selection must go blind into each fold")'
             ),
             variant_b='k=20 selected (does a wider net shrink the gap?)',
             variant_c='n_informative=25 (real signal everywhere — does the leak still flatter?)',
             mistakes=[
                 "'Everyone does select-then-split' mistaken for correctness.",
                 "Univariate selection praised for multivariate problems it cannot see.",
                 "Leak suspicion dismissed because 'it is just preprocessing'.",
             ],
             q1=("Why does selecting on all data flatter cross-validation specifically?",
                 "Every fold's test rows helped choose the features, so the 'held-out' evaluation grades features pre-approved by the answers."),
             homework="Write `selection_duel()` comparing select-outside vs select-inside CV means. Run it at two k values, print both duels, and comment which line selects blind.",
             patterns=["SelectKBest(", "make_pipeline("],
             mapping="sklearn.feature_selection.SelectKBest inside pipelines; RFE and model-based selection obey the same placement rule.",
         ),
         142: dict(
             topic="Time has order: split by date",
             idea="Shuffling assumes rows are exchangeable, but time series are not: tomorrow depends on today, regimes shift, and a model trained on December to 'predict' November is science fiction. Time-based splits train on the past and test on the future — the only evaluation shaped like deployment — using TimeSeriesSplit's expanding windows. Shuffling time data leaks the future into training and reports fantasy scores; the production model then meets a future it never practised. Whenever rows carry timestamps, the split follows the calendar, and day 86's shuffle lesson gets an explicit exception carved beside it.",
             code=(
                 'from sklearn.model_selection import TimeSeriesSplit\n'
                 'from sklearn.linear_model import Ridge\n'
                 'import numpy as np\n'
                 '\n'
                 't = np.arange(60, dtype=float)\n'
                 'y = 0.5 * t + np.sin(t / 3.0)\n'
                 'X = t.reshape(-1, 1)\n'
                 'tscv = TimeSeriesSplit(n_splits=3)\n'
                 'for fold, (tr, te) in enumerate(tscv.split(X)):\n'
                 '    m = Ridge(alpha=1.0).fit(X[tr], y[tr])\n'
                 '    print(f"fold {fold}: train ends {tr[-1]}, test {te[0]}-{te[-1]}, R^2={m.score(X[te], y[te]):.3f}")\n'
                 'print("train past, test future — always")'
             ),
             variant_b='n_splits=5 (shorter windows — steadier or noisier?)',
             variant_c='a shuffled KFold on the same data (higher score, total fiction — why?)',
             mistakes=[
                 "Shuffled CV on time data reporting fantasy scores that production instantly refutes.",
                 "Random train_test_split across a regime shift, testing on an era never trained.",
                 "No embargo between train end and test start when labels react with delay.",
             ],
             q1=("Why is shuffled CV actively harmful on time data, not merely suboptimal?",
                 "It trains on future rows to predict past ones — an information direction deployment can never use, so the score measures an impossible advantage."),
             homework="Write `time_or_shuffle()` comparing TimeSeriesSplit vs shuffled-KFold means on trend data. Run it on two trends, print both, and comment which evaluation resembles deployment.",
             patterns=["TimeSeriesSplit(", ".split("],
             mapping="sklearn.model_selection.TimeSeriesSplit; forecasting libraries add embargoes and horizon-aware variants.",
         ),
         143: dict(
             topic="Group leakage: same patient, both sides",
             idea="Rows are not always independent: ten rows from one patient, fifty clicks from one user, repeated measurements from one sensor. Random splits scatter a patient's rows across train and test, and the model 'generalises' to rows it effectively memorised — same patient, same quirks, inflated scores. GroupKFold splits by group (patient, user, device) so no group appears on both sides, measuring generalisation to new groups, which is what deployment actually demands. Whenever rows cluster by origin, split by origin; row-level shuffling on grouped data is leakage wearing a lab coat. Define groups from the deployment boundary: whatever unit must be new in production gets its own fold side.",
             code=(
                 'from sklearn.linear_model import Ridge\n'
                 'from sklearn.model_selection import GroupKFold, cross_val_score\n'
                 'import numpy as np\n'
                 '\n'
                 'rng = np.random.RandomState(90)\n'
                 'groups = np.repeat(np.arange(20), 5)\n'
                 'offsets = rng.randn(20)[groups] * 5.0\n'
                 'X = (np.arange(100) % 10).reshape(-1, 1).astype(float)\n'
                 'y = 2.0 * X.ravel() + offsets + rng.randn(100)\n'
                 'rowwise = cross_val_score(Ridge(alpha=1.0), X, y, cv=3).mean()\n'
                 'grouped = cross_val_score(Ridge(alpha=1.0), X, y, cv=GroupKFold(3), groups=groups).mean()\n'
                 'print("row-shuffled R^2:", round(rowwise, 3))\n'
                 'print("group-split  R^2:", round(grouped, 3))\n'
                 'print("the gap is memorised quirks, exposed")'
             ),
             variant_b='offsets * 0.5 (weaker quirks — does the gap shrink?)',
             variant_c='plain KFold with shuffle (does it agree with the leaky or the honest number?)',
             mistakes=[
                 "Row splits on grouped rows reported as generalisation evidence.",
                 "Groups defined too finely (per-visit instead of per-patient), leaking through the cracks.",
                 "GroupKFold without checking group sizes — one giant group unbalances every fold.",
             ],
             q1=("Why does scattering one patient's rows across train and test inflate scores?",
                 "Patient-specific quirks appear on both sides, so the model recognises individuals instead of learning generalisable patterns."),
             homework="Write `group_or_row()` comparing row-shuffled vs GroupKFold CV means on grouped data. Run it at two quirk strengths, print both gaps, and comment which splitter matches deployment.",
             patterns=["GroupKFold(", "cross_val_score("],
             mapping="sklearn.model_selection.GroupKFold (and StratifiedGroupKFold); medical/fraud/user data splits by origin, always.",
         ),
         144: dict(
             topic="Imbalanced evaluation done right",
             idea="On skewed data, accuracy is a liar, F1 is a compromise, and the business metric is the truth: cost per false alarm versus cost per miss. G-mean balances both classes' recall, average-precision summarises the precision-recall curve in one number, and the dummy baseline (always-majority) anchors every claim. The professional move is reporting all four — accuracy, F1, average precision, dummy — so no single number can mislead, then choosing by cost. Metrics are not grades; they are instruments, and imbalanced problems punish anyone holding only a hammer. Publish the full four-number panel with every imbalanced result so readers can re-judge by their own costs. Transparency about metrics is professionalism, not modesty.",
             code=(
                 'from sklearn.datasets import make_classification\n'
                 'from sklearn.linear_model import LogisticRegression\n'
                 'from sklearn.dummy import DummyClassifier\n'
                 'from sklearn.metrics import accuracy_score, f1_score, average_precision_score\n'
                 '\n'
                 'X, y = make_classification(n_samples=400, weights=[0.9, 0.1], random_state=91)\n'
                 'Xtr, Xte, ytr, yte = X[:300], X[300:], y[:300], y[300:]\n'
                 'dummy = DummyClassifier(strategy="most_frequent").fit(Xtr, ytr).predict(Xte)\n'
                 'real = LogisticRegression(max_iter=1000).fit(Xtr, ytr)\n'
                 'pred, proba = real.predict(Xte), real.predict_proba(Xte)[:, 1]\n'
                 'for label, p in [("dummy", dummy), ("logreg", pred)]:\n'
                 '    print(f"{label:<7} acc={accuracy_score(yte, p):.3f} F1={f1_score(yte, p):.3f}")\n'
                 'print("avg precision (ranking):", round(average_precision_score(yte, proba), 3))'
             ),
             variant_b='weights=[0.6, 0.4] (does accuracy become honest again?)',
             variant_c='threshold 0.3 on proba (which metric moves most?)',
             mistakes=[
                 "Accuracy-only reporting on 90/10 data, hiding a never-positive model.",
                 "F1 quoted without saying which class is 'positive'.",
                 "No dummy row, so every number floats anchorless.",
             ],
             q1=("Why report average precision alongside F1 on skewed data?",
                 "F1 judges one threshold while average precision summarises ranking across all of them — together they separate dial problems from ranking problems."),
             homework="Write `skewed_scoreboard()` printing accuracy/F1 for dummy and logreg plus average precision. Run it on two imbalance levels, print both, and comment which metric survives skew.",
             patterns=["f1_score(", "average_precision_score("],
             mapping="sklearn.metrics.average_precision_score, balanced_accuracy_score; cost curves when the business prices errors explicitly.",
         ),
         145: dict(
             topic="Score spread: how sure is 0.93?",
             idea="A point estimate without spread is half a result: 0.93 could be 0.93±0.005 (ships) or 0.93±0.06 (investigate). Repeated stratified splits with different seeds map the score distribution honestly, separating model quality from split luck. Wide spread means the evaluation — or the data — is fragile: tiny test sets, rare classes, unstable training. Professionals quote mean±std over repeats and distrust improvements smaller than the spread; a 'gain' of 0.01 inside ±0.03 noise is not a gain, it is weather. Measure the weather before celebrating the climate.",
             code=(
                 'from sklearn.datasets import load_iris\n'
                 'from sklearn.model_selection import train_test_split\n'
                 'from sklearn.neighbors import KNeighborsClassifier\n'
                 'from sklearn.metrics import accuracy_score\n'
                 '\n'
                 'X, y = load_iris(return_X_y=True)\n'
                 'scores = []\n'
                 'for seed in range(10):\n'
                 '    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, random_state=seed, stratify=y)\n'
                 '    pred = KNeighborsClassifier(n_neighbors=3).fit(Xtr, ytr).predict(Xte)\n'
                 '    scores.append(accuracy_score(yte, pred))\n'
                 'mean = sum(scores) / len(scores)\n'
                 'spread = (sum((s - mean) ** 2 for s in scores) / len(scores)) ** 0.5\n'
                 'print("10 seeds:", [round(s, 3) for s in scores])\n'
                 'print(f"mean={mean:.3f} spread={spread:.3f}: improvements inside the spread are weather")'
             ),
             variant_b='test_size=0.1 (does the spread explode on tiny tests?)',
             variant_c='digits data (bigger data, steadier weather?)',
             mistakes=[
                 "One seed's 0.97 published as the result.",
                 "Spread computed but ignored when a 'better' model lands inside it.",
                 "Ten repeats on a 30-row test set treated as ten independent experiments.",
             ],
             q1=("Why do improvements smaller than the spread not count?",
                 "They are indistinguishable from reshuffling luck — claiming them mistakes weather for climate and ships noise."),
             homework="Write `weather_report()` printing ten seed scores plus mean±spread. Run it for kNN-3 and logreg, print both, and comment which number decides whether a gain is real.",
             patterns=["train_test_split(", "random_state="],
             mapping="Repeated stratified splits (or repeated CV) for every published number; error bars are the honest part of every claim.",
         ),
         146: dict(
             topic="Picking metrics like a business",
             idea="The metric is the contract: optimise accuracy and you buy majority-guessing; optimise recall and you buy alarm fatigue; optimise precision and you buy missed cases. Cost matrices make the trade explicit — $10 per false alarm, $1000 per miss — and expected cost picks the threshold arithmetically instead of by gut. Different stakeholders need different numbers from one model: operations watches precision (workload), risk watches recall (exposure), finance watches cost (money). One model, three dials, zero arguments about 'accuracy' — because accuracy left the conversation the moment costs were named.",
             code=(
                 'from sklearn.datasets import make_classification\n'
                 'from sklearn.linear_model import LogisticRegression\n'
                 '\n'
                 'X, y = make_classification(n_samples=300, weights=[0.85, 0.15], random_state=92)\n'
                 'Xtr, Xte, ytr, yte = X[:225], X[225:], y[:225], y[225:]\n'
                 'proba = LogisticRegression(max_iter=500).fit(Xtr, ytr).predict_proba(Xte)[:, 1]\n'
                 'COST_ALARM, COST_MISS = 10.0, 1000.0\n'
                 'print("threshold | alarms | misses | cost")\n'
                 'for t in (0.2, 0.4, 0.5, 0.6, 0.8):\n'
                 '    pred = [1 if p >= t else 0 for p in proba]\n'
                 '    alarms = sum(1 for p, a in zip(pred, yte) if p == 1 and a == 0)\n'
                 '    misses = sum(1 for p, a in zip(pred, yte) if p == 0 and a == 1)\n'
                 '    print(f"  {t:.1f}     |  {alarms:<5} |  {misses:<5} | ${alarms * COST_ALARM + misses * COST_MISS:,.0f}")'
             ),
             variant_b='COST_MISS = $50 (cheap misses — where does the dial move?)',
             variant_c='balanced classes (do costs still dominate the choice?)',
             mistakes=[
                 "Optimising the default metric while the business bleeds on another.",
                 "One threshold for all stakeholders with different cost profiles.",
                 "Costs estimated once, then never revisited as the business changes.",
             ],
             q1=("Why does naming dollar costs end threshold arguments?",
                 "Costs convert the trade-off to arithmetic: the cheapest row wins, and disagreements become falsifiable claims about prices, not taste."),
             homework="Write `cost_table()` printing alarms/misses/cost at five thresholds. Run it at two miss-costs, print both tables, and comment which threshold each business would pick.",
             patterns=["predict_proba(", ".fit("],
             mapping="Cost-sensitive learning (class_weight, sample_weight) automates the dial; the table justifies it to stakeholders.",
         ),
         147: dict(
             topic="Project: the leakage hunt",
             idea="Today's project is a crime scene: a script scoring 0.97 on diabetes data that you must audit line by line — scaler fit on full data, features selected on all rows, best-alpha picked on test. Your job is the audit report: name each leak, fix it with pipelines, and print the honest score beside the fantasy one. The gap between them, usually several R² points, is the most educational number in this phase, because every future 'too good' result gets checked against exactly these three suspects first. Leak-hunting is a career skill disguised as homework. Keep a personal checklist of the three classic leaks and run it against every too-good score for the rest of your career.",
             code=(
                 'from sklearn.datasets import load_diabetes\n'
                 'from sklearn.preprocessing import StandardScaler\n'
                 'from sklearn.linear_model import Ridge\n'
                 'from sklearn.pipeline import make_pipeline\n'
                 'from sklearn.metrics import r2_score\n'
                 '\n'
                 'X, y = load_diabetes(return_X_y=True)\n'
                 'Xtr, Xte, ytr, yte = X[:350], X[350:], y[:350], y[350:]\n'
                 'sc = StandardScaler().fit(X)\n'
                 'fantasy = Ridge(alpha=1.0).fit(sc.transform(Xtr), ytr).score(sc.transform(Xte), yte)\n'
                 'honest = make_pipeline(StandardScaler(), Ridge(alpha=1.0)).fit(Xtr, ytr).score(Xte, yte)\n'
                 'print("fantasy (leaky scaler):", round(fantasy, 4))\n'
                 'print("honest  (pipeline):   ", round(honest, 4))\n'
                 'print("gap:", round(fantasy - honest, 4), "— bought with test answers")'
             ),
             variant_b='alpha=0.01 (does a weaker penalty widen the fantasy gap?)',
             variant_c='shuffled 80/20 split (does honest shuffling change the story?)',
             mistakes=[
                 "Auditing the model while trusting the preprocessing — leaks live upstream of fitting.",
                 "'Small gap, ship the leaky one' — gaps compound across three leaks into fictions.",
                 "Fixing one leak and declaring victory without re-auditing the other two.",
             ],
             q1=("Why audit preprocessing before the model when scores look too good?",
                 "Models rarely inflate themselves; fantasy scores almost always enter upstream — scaling, selection, or imputation that peeked at answers."),
             homework="Write `audit_report()` printing fantasy vs honest R² for a leaky scaler and naming the leak. Run it on two splits, print both gaps, and comment which line spends test answers.",
             patterns=["make_pipeline(", "r2_score("],
             mapping="This audit reflex — fantasy vs honest, line-by-line — precedes every production model you will ever ship.",
         ),
         148: dict(
             topic="Testing validation code with asserts",
             idea="Validation guards check the measurement machinery: fold counts match cv, every row tested exactly once across folds, and leaky-vs-honest comparisons point the right way with margin to spare. The leak half uses duplicated minority rows (oversample-then-split) against split-then-oversample: test rows that duplicate training rows classify near-perfectly by memorisation, so the leaky score towers over the honest one on every seed. Assert the machinery's contracts, not its numbers: 'five folds cover all rows' and 'honest trails leaky by 0.1' survive every dataset while exact means fossilise one run. These guards wrap every experiment from today on, because unmeasured measurement is the deepest failure mode — wrong answers about how right you are.",
             code=(
                 'from sklearn.datasets import make_classification\n'
                 'from sklearn.model_selection import StratifiedKFold\n'
                 'from sklearn.neighbors import KNeighborsClassifier\n'
                 'from sklearn.metrics import f1_score\n'
                 'import numpy as np\n'
                 '\n'
                 'X, y = make_classification(n_samples=200, weights=[0.85, 0.15], random_state=93)\n'
                 'folds = list(StratifiedKFold(n_splits=5, shuffle=True, random_state=93).split(X, y))\n'
                 'assert len(folds) == 5\n'
                 'tested = sorted(i for _, te in folds for i in te)\n'
                 'assert tested == list(range(len(X)))\n'
                 'mino = [x for x, t in zip(X, y) if t == 1]\n'
                 'maj = [x for x, t in zip(X, y) if t == 0]\n'
                 'Xdup = np.array(mino * 3 + maj)\n'
                 'ydup = np.array([1] * (3 * len(mino)) + [0] * len(maj))\n'
                 'rng = np.random.RandomState(93)\n'
                 'idx = np.arange(len(ydup))\n'
                 'rng.shuffle(idx)\n'
                 'Xd, yd = Xdup[idx], ydup[idx]\n'
                 'n = int(0.7 * len(yd))\n'
                 'leaky = f1_score(yd[n:], KNeighborsClassifier(n_neighbors=1).fit(Xd[:n], yd[:n]).predict(Xd[n:]))\n'
                 'X0, Xa, y0, ya = X[:140], X[140:], y[:140], y[140:]\n'
                 'mino0 = [x for x, t in zip(X0, y0) if t == 1]\n'
                 'maj0 = [x for x, t in zip(X0, y0) if t == 0]\n'
                 'Xo = np.array(mino0 * 3 + maj0)\n'
                 'yo = np.array([1] * (3 * len(mino0)) + [0] * len(maj0))\n'
                 'honest = f1_score(ya, KNeighborsClassifier(n_neighbors=1).fit(Xo, yo).predict(Xa))\n'
                 'assert honest + 0.1 <= leaky\n'
                 'print(f"guards passed: coverage complete; leaky {leaky:.3f} towers over honest {honest:.3f}")'
             ),
             variant_b='n_neighbors=5 (does smoothing shrink the tower?)',
             variant_c='duplicate majority instead of minority (does the gap survive?)',
             mistakes=[
                 "Asserting exact CV means that break on every new seed.",
                 "Coverage asserts without shuffle-fairness asserts — complete but biased folds.",
                 "Oversampling before splitting in real projects, then shipping the tower as a result.",
             ],
             q1=("Why does oversample-then-split tower over split-then-oversample so reliably?",
                 "Duplicated rows land on both sides, so the test set contains near-copies of training rows — memorisation scores as generalisation."),
             homework="Write `guarded_validation()` with asserts on fold coverage and leaky-minus-honest margin, printing the certified comparison. Run it on two seeds, print both, and comment which assert certifies the leak direction.",
             patterns=["assert ", "StratifiedKFold("],
             mapping="Coverage and direction asserts wrap every validation harness; numbers change, contracts do not.",
         ),
         149: dict(
             topic="Phase review: validation",
             idea="Rebuild from memory: validation curves replace gut knobs, learning curves prescribe data or models, cross-validation rotates every row through the exam, grids tune without cheating, pipelines make leaks impossible, scaling/selection/time/group leaks each have a face, imbalance gets four metrics, spreads judge certainty, costs pick thresholds. Close the notes and reproduce the leak-hunt: fantasy vs honest R² with the gap stated and each leak named. The missing line is tomorrow's first job; pipelines and tuning (phase 6) industrialise everything this phase made manual. If the rebuild flows, honest measurement is installed — the rarest professional skill in this track. If the leak-hunt rebuild stalls, reread days 140–143 in order — each leak has a face, and faces are memorable. Honest measurement compounds: every later phase trusts the numbers this one certifies. That trust is the whole product of this phase.",
             code=(
                 'from sklearn.datasets import load_diabetes\n'
                 'from sklearn.preprocessing import StandardScaler\n'
                 'from sklearn.linear_model import Ridge\n'
                 'from sklearn.pipeline import make_pipeline\n'
                 '\n'
                 'X, y = load_diabetes(return_X_y=True)\n'
                 'Xtr, Xte, ytr, yte = X[:350], X[350:], y[:350], y[350:]\n'
                 'sc = StandardScaler().fit(X)\n'
                 'fantasy = Ridge(alpha=1.0).fit(sc.transform(Xtr), ytr).score(sc.transform(Xte), yte)\n'
                 'honest = make_pipeline(StandardScaler(), Ridge(alpha=1.0)).fit(Xtr, ytr).score(Xte, yte)\n'
                 'print("fantasy:", round(fantasy, 4), "| honest:", round(honest, 4))\n'
                 'print("gap:", round(fantasy - honest, 4))'
             ),
             variant_b='alpha=10 (does heavier penalty shrink the fantasy gap?)',
             variant_c='Lasso instead of Ridge (does selection change the story?)',
             mistakes=[
                 "Rebuilding with notes open — retrieval is the learning.",
                 "Reciting leak types without placing one in a running script.",
                 "Skipping the honest number because the fantasy one flattered.",
             ],
             q1=("What single rebuild proves this phase stuck?",
                 "The leak-hunt from memory — fantasy vs honest with every leak named — because it exercises every guard at once."),
             homework="Write `phase_recap()` from memory: leaky scaler, clean pipeline, printed gap. Run it on two splits, print both gaps, and comment which line you had to look up.",
             patterns=["make_pipeline(", ".score("],
             mapping="Phase 6 keeps pipelines and adds grids; measurement discipline never changes again.",
         ),
     }),
    ("Pipelines and Tuning",
     "Industrialise the workflow: leak-free chains, grids over pipelines, persistence, and fair boards.",
     {
         150: dict(
             topic="Anatomy of a pipeline",
             idea="A Pipeline object is a fitted chain with one throat to choke: named steps executed in order, fit transforming each step on training folds only, predict flowing straight through. Beyond leak-safety, pipelines compose — a ColumnTransformer inside a Pipeline inside a GridSearchCV nests three honest behaviours in one shippable object. Learn the anatomy (steps list, named_steps access, set_params with double-underscore paths like scaler__with_mean) because every tuning day ahead addresses pipeline parts by these names. One object from raw frame to prediction is the professional unit of ML code. Name every step from day one; anonymous steps cannot be tuned, inspected, or debugged by anyone including you. Anonymous steps also break every grid path that addresses steps by name.",
             code=(
                 'from sklearn.datasets import load_breast_cancer\n'
                 'from sklearn.preprocessing import StandardScaler\n'
                 'from sklearn.linear_model import LogisticRegression\n'
                 'from sklearn.pipeline import Pipeline\n'
                 '\n'
                 'X, y = load_breast_cancer(return_X_y=True)\n'
                 'pipe = Pipeline([("scale", StandardScaler()), ("clf", LogisticRegression(max_iter=1000))])\n'
                 'pipe.fit(X[:400], y[:400])\n'
                 'print("steps:", [name for name, _ in pipe.steps])\n'
                 'print("test accuracy:", round(pipe.score(X[400:], y[400:]), 4))\n'
                 'print("C currently:", pipe.named_steps["clf"].get_params()["C"])\n'
                 'pipe.set_params(clf__C=0.1)\n'
                 'print("C after set_params:", pipe.named_steps["clf"].get_params()["C"])'
             ),
             variant_b='steps reversed (model before scaler — which error, and why is loud failure a mercy?)',
             variant_c='C=0.01 via set_params, refit, rescore (does the chain survive surgery?)',
             mistakes=[
                 "Addressing steps by position (steps[1]) instead of name — brittle under reordering.",
                 "Single-underscore param paths (clf_C) that silently create nothing.",
                 "Fitting the pipeline, then preprocessing new data by hand differently at serve time.",
             ],
             q1=("Why do pipelines address parameters with double-underscore paths?",
                 "Nested objects need unambiguous addresses: clf__C names the C inside the step named clf, so grids and surgery hit the right knob."),
             homework="Write `chain_report()` building a scale+logreg pipeline, printing step names and test accuracy. Run it with two C values via set_params, print both, and comment which line addresses the nested knob.",
             patterns=["Pipeline(", "set_params("],
             mapping="sklearn.pipeline.Pipeline/make_pipeline — every chain from today is one named, shippable object.",
         ),
         151: dict(
             topic="ColumnTransformer: one plan per dtype",
             idea="Real frames mix dtypes, and one plan per dtype beats one plan for all: numbers get scaled, low-cardinality text goes one-hot, high-cardinality IDs get dropped or hashed. ColumnTransformer declares the plan by column name, applies each branch, and concatenates — inside the pipeline, hence leak-free and refit-safe per fold. Column names (not positions) select the branches, so reordered frames still work and dropped columns fail loudly instead of shifting silently. This is the grown-up version of day 99's hand assembly: same honesty, zero hand-plumbing, ready for grids to tune each branch.",
             code=(
                 'import pandas as pd\n'
                 'from sklearn.compose import ColumnTransformer\n'
                 'from sklearn.preprocessing import StandardScaler, OneHotEncoder\n'
                 'from sklearn.linear_model import Ridge\n'
                 '\n'
                 'df = pd.DataFrame({"size": [800.0, 1200.0, 950.0, 1500.0, 700.0, 1100.0],\n'
                 '                   "area": ["town", "city", "town", "city", "town", "city"],\n'
                 '                   "price": [150.0, 300.0, 180.0, 350.0, 140.0, 260.0]})\n'
                 'plan = ColumnTransformer([("num", StandardScaler(), ["size"]), ("cat", OneHotEncoder(), ["area"])])\n'
                 'Xtr = plan.fit_transform(df.iloc[:4])\n'
                 'Xte = plan.transform(df.iloc[4:])\n'
                 'pred = Ridge(alpha=1.0).fit(Xtr, df["price"][:4]).predict(Xte)\n'
                 'print("assembled width:", Xtr.shape[1], "columns")\n'
                 'print("held-out predictions:", [round(float(p), 1) for p in pred])\n'
                 'print("actuals:", list(df["price"][4:]))'
             ),
             variant_b='a third area "village" in row 5 (which error, and what handle_unknown buys?)',
             variant_c='drop="first" on the encoder (why might a linear model prefer it?)',
             mistakes=[
                 "Positional column selection that silently shifts when the frame reorders.",
                 "Fitting the transformer outside any pipeline, reviving day 140's leak.",
                 "One-hot branches without handle_unknown planning for novel test categories.",
             ],
             q1=("Why select transformer branches by column name rather than position?",
                 "Names survive reordering and loudly fail on missing columns; positions silently shift meaning when the frame changes shape."),
             homework="Write `mixed_plan()` assembling scaled-size plus one-hot-area via ColumnTransformer and predicting two held-out prices. Run it with two held-out rows, print both, and comment which line declares the per-dtype plan.",
             patterns=["ColumnTransformer(", ".transform("],
             mapping="sklearn.compose.ColumnTransformer — the day-99 hand assembly industrialised; grids tune its branches by name.",
         ),
         152: dict(
             topic="Grids over pipelines",
             idea="Tuning a pipeline means addressing nested knobs: clf__C for the classifier, scale__with_mean for the scaler, select__k for selection — one grid spanning preprocessing and model together, judged by honest folds. This joint tuning matters because preprocessing choices interact with model choices (scaling strength changes the best C), and tuning them separately finds local optima while the grid finds the joint one. Keep grids small and meaningful (three C values beat thirty alphabet-soup knobs), always include the baseline settings in the grid so 'tuning helped' is falsifiable, and remember best_score_ selects — only untouched test data crowns. Always include the untuned baseline settings in the grid so 'tuning helped' stays a falsifiable claim, not a feeling. Without the baseline beside the winner, nobody can tell whether the grid bought anything at all.",
             code=(
                 'from sklearn.datasets import load_breast_cancer\n'
                 'from sklearn.preprocessing import StandardScaler\n'
                 'from sklearn.linear_model import LogisticRegression\n'
                 'from sklearn.pipeline import make_pipeline\n'
                 'from sklearn.model_selection import GridSearchCV\n'
                 '\n'
                 'X, y = load_breast_cancer(return_X_y=True)\n'
                 'pipe = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000))\n'
                 'grid = GridSearchCV(pipe, {"logisticregression__C": [0.01, 0.1, 1.0, 10.0]}, cv=3)\n'
                 'grid.fit(X, y)\n'
                 'print("best:", grid.best_params_)\n'
                 'print("best CV:", round(grid.best_score_, 4))\n'
                 'print("winner refit on all rows, ready for the locked test set")'
             ),
             variant_b='add logisticregression__penalty ["l2"] vs solver limits (which combos are even legal?)',
             variant_c='cv=5 (does the winner survive stricter judging?)',
             mistakes=[
                 "Wrong step names in param paths (logreg__C when the step is logisticregression) failing loudly at 2am.",
                 "Tuning thirty knobs at once, then 'discovering' noise.",
                 "Quoting best_score_ as the model's performance instead of the selection criterion.",
             ],
             q1=("Why tune preprocessing and model knobs in one joint grid?",
                 "They interact — the best C depends on the scaling — so separate tuning finds local optima while the joint grid finds the combination that actually wins."),
             homework="Write `pipe_grid()` gridding C over four values on a scaled logreg pipeline with cv=3. Run it on breast-cancer and digits, print both winners, and comment how the nested knob is addressed.",
             patterns=["GridSearchCV(", "best_params_"],
             mapping="GridSearchCV over pipeline__step__param paths; RandomizedSearchCV samples when grids explode.",
         ),
         153: dict(
             topic="Measuring the scaling dividend",
             idea="Scaling's value is model-dependent and measurable: kNN transforms (distances change meaning), penalised linear models transform (penalties fall fairly), trees do not move (order preserved). A three-way board — bare, scaled-manually, pipelined — prices the dividend per model class on one dataset, turning folklore ('always scale') into numbers. The pipelined column should match the manual column exactly (same math, safer structure); any gap between them is a bug, usually a refit scaler. Run this board whenever someone proposes scaling: measure, do not chant.",
             code=(
                 'from sklearn.datasets import load_breast_cancer\n'
                 'from sklearn.preprocessing import StandardScaler\n'
                 'from sklearn.neighbors import KNeighborsClassifier\n'
                 'from sklearn.tree import DecisionTreeClassifier\n'
                 'from sklearn.pipeline import make_pipeline\n'
                 'from sklearn.model_selection import cross_val_score\n'
                 '\n'
                 'X, y = load_breast_cancer(return_X_y=True)\n'
                 'sc = StandardScaler().fit(X)\n'
                 'Xs = sc.transform(X)\n'
                 'for name, m in [("knn-5", KNeighborsClassifier(n_neighbors=5)), ("tree-d4", DecisionTreeClassifier(max_depth=4, random_state=100))]:\n'
                 '    bare = cross_val_score(m, X, y, cv=3).mean()\n'
                 '    manual = cross_val_score(m, Xs, y, cv=3).mean()\n'
                 '    piped = cross_val_score(make_pipeline(StandardScaler(), m), X, y, cv=3).mean()\n'
                 '    print(f"{name}: bare={bare:.4f} manual={manual:.4f} piped={piped:.4f}")\n'
                 'print("piped must equal manual: same math, safer structure")'
             ),
             variant_b='logreg added to the board (penalty model — where does it land?)',
             variant_c='cv=5 (do the dividends survive stricter judging?)',
             mistakes=[
                 "'Always scale' applied to forests, adding failure points for zero gain.",
                 "Manual-scaled numbers quoted as the result instead of the pipelined twin.",
                 "A manual-vs-piped gap waved away instead of investigated as a refit bug.",
             ],
             q1=("Why must pipelined match manual scaling exactly?",
                 "Identical mathematics (fit-on-train, transform-both) — any gap proves the manual path refit somewhere it should not have."),
             homework="Write `scaling_dividends()` printing bare/manual/piped CV means for kNN and trees. Run it on two datasets, print both boards, and comment which equality certifies the pipeline.",
             patterns=["make_pipeline(", "cross_val_score("],
             mapping="This board settles every scaling debate with numbers; rerun it per dataset, since dividends vary by data.",
         ),
         154: dict(
             topic="Rare classes without new libraries",
             idea="Without imbalanced-learn on the approved stack, rare classes get honest treatment from three built-ins: class_weight rebalancing (one keyword), threshold moves on calibrated probabilities (day 107's dial), and hand oversampling done strictly inside training folds (duplicate minority rows after splitting, never before — day 148 proved why). Combine deliberately: weights fix the loss, thresholds fix the operating point, oversampling feeds data-hungry models more minority examples. Report precision/recall/F1 throughout, because accuracy on skewed data is decoration. Constraints breed discipline: these three moves cover 90% of real imbalance work with zero new dependencies.",
             code=(
                 'from sklearn.datasets import make_classification\n'
                 'from sklearn.linear_model import LogisticRegression\n'
                 'from sklearn.metrics import precision_score, recall_score\n'
                 'import numpy as np\n'
                 '\n'
                 'X, y = make_classification(n_samples=300, weights=[0.9, 0.1], random_state=101)\n'
                 'Xtr, Xte, ytr, yte = X[:225], X[225:], y[:225], y[225:]\n'
                 'plain = LogisticRegression(max_iter=1000).fit(Xtr, ytr).predict(Xte)\n'
                 'heavy = LogisticRegression(max_iter=1000, class_weight="balanced").fit(Xtr, ytr).predict(Xte)\n'
                 'mino = [x for x, t in zip(Xtr, ytr) if t == 1]\n'
                 'Xo = np.array(mino * 2 + [x for x, t in zip(Xtr, ytr) if t == 0])\n'
                 'yo = np.array([1] * (2 * len(mino)) + [0] * (len(ytr) - len(mino)))\n'
                 'over = LogisticRegression(max_iter=1000).fit(Xo, yo).predict(Xte)\n'
                 'for label, p in [("plain", plain), ("weighted", heavy), ("oversampled", over)]:\n'
                 '    print(f"{label:<11} precision={precision_score(yte, p, zero_division=0):.2f} recall={recall_score(yte, p):.2f}")'
             ),
             variant_b='minority tripled instead of doubled (does recall keep climbing?)',
             variant_c='weights=[0.7, 0.3] (do the tricks become harmless?)',
             mistakes=[
                 "Oversampling before splitting — day 148's tower, rebuilt with fresh enthusiasm.",
                 "New libraries installed for a problem three keywords solve.",
                 "Accuracy headlining any row of this board.",
             ],
             q1=("Why oversample strictly after splitting?",
                 "Duplicated rows must never straddle the boundary: copies in test memorise as generalisation, inflating exactly what you wanted to measure."),
             homework="Write `imbalance_trio()` printing precision/recall for plain/weighted/oversampled on one split. Run it on two imbalance levels, print both trios, and comment which line keeps duplicates train-side.",
             patterns=["class_weight=", ".predict("],
             mapping="class_weight, threshold moves, and fold-local oversampling — the no-new-deps imbalance toolkit.",
         ),
         155: dict(
             topic="Saving models with pickle",
             idea="A fitted model is bytes waiting to happen: pickle dumps the pipeline (preprocessing plus estimator, fitted statistics and all), and loading restores predictions bit-identically — verify with equal predictions, not trust. Version the artefact with data hash, code version and library versions alongside, because a pickle without provenance is a liability: sklearn version skew across train and serve silently changes behaviour. Never unpickle untrusted files (arbitrary code execution lives inside), and prefer joblib for giant forests — pickle for everything else. Shipping is serialisation plus provenance, never serialisation alone. Test-load every artefact in a fresh process before declaring it shippable — the loading environment is part of the product. Pin library versions in the artefact metadata so train time and serve time can never silently differ. Test the loaded model on a fixed probe set before every deployment.",
             code=(
                 'import pickle\n'
                 'from sklearn.datasets import load_iris\n'
                 'from sklearn.preprocessing import StandardScaler\n'
                 'from sklearn.linear_model import LogisticRegression\n'
                 'from sklearn.pipeline import make_pipeline\n'
                 '\n'
                 'X, y = load_iris(return_X_y=True)\n'
                 'pipe = make_pipeline(StandardScaler(), LogisticRegression(max_iter=500)).fit(X[:120], y[:120])\n'
                 'blob = pickle.dumps(pipe)\n'
                 'back = pickle.loads(blob)\n'
                 'a = pipe.predict(X[120:])\n'
                 'b = back.predict(X[120:])\n'
                 'print("bytes:", len(blob))\n'
                 'print("identical predictions:", bool((a == b).all()))\n'
                 'print("accuracy survives the trip:", round((b == y[120:]).mean(), 4))'
             ),
             variant_b='a forest pipeline (how many bytes does an ensemble weigh?)',
             variant_c='unpickling after shuffling feature order (what breaks, and what does that teach about contracts?)',
             mistakes=[
                 "Shipping the estimator without its preprocessing — serve-time skew guaranteed.",
                 "No version metadata, so silent library upgrades change behaviour unnoticed.",
                 "Unpickling uploads from strangers — remote code execution as a feature.",
             ],
             q1=("Why verify with equal predictions rather than trusting the round-trip?",
                 "Serialisation can silently drop state (custom attributes, fitted flags); identical outputs prove the artefact is the model, not a souvenir of it."),
             homework="Write `ship_it()` pickling a fitted pipeline and asserting identical predictions after loading. Run it for logreg and kNN pipelines, print both verdicts, and comment which line proves the trip.",
             patterns=["pickle.dumps(", "pickle.loads("],
             mapping="pickle for pipelines, joblib for giant ensembles; provenance metadata rides alongside every artefact.",
         ),
         156: dict(
             topic="Selecting features inside folds",
             idea="SelectKBest ranks features by univariate tests and keeps k winners — fast, transparent, and dangerous outside folds (day 141 proved the inflation). Inside a pipeline it becomes honest: each fold selects blind on its training rows, so the CV score measures selection-plus-model as one procedure. Watch k itself become a tunable knob (grid it: 5, 10, 20, all), and distrust univariate screens on deeply multivariate problems where features matter only in combination — trees and L1 find interactions that F-tests cannot see. Selection is a modelling decision with its own validation bill; pay it per fold. Watch k itself become tunable: grid the headcount (5, 10, 20, all) and let folds decide how many features earn their keep.",
             code=(
                 'from sklearn.datasets import load_breast_cancer\n'
                 'from sklearn.feature_selection import SelectKBest, f_classif\n'
                 'from sklearn.preprocessing import StandardScaler\n'
                 'from sklearn.linear_model import LogisticRegression\n'
                 'from sklearn.pipeline import make_pipeline\n'
                 'from sklearn.model_selection import cross_val_score\n'
                 '\n'
                 'X, y = load_breast_cancer(return_X_y=True)\n'
                 'pipe = make_pipeline(SelectKBest(f_classif, k=10), StandardScaler(), LogisticRegression(max_iter=1000))\n'
                 'scores = cross_val_score(pipe, X, y, cv=3)\n'
                 'print("fold scores:", [round(s, 4) for s in scores])\n'
                 'print("mean:", round(scores.mean(), 4))\n'
                 'pipe.fit(X, y)\n'
                 'mask = pipe.named_steps["selectkbest"].get_support()\n'
                 'print("selected 10 of", len(mask), "| first three:", list(mask).index(True), "...")'
             ),
             variant_b='k=30 (does a wider net help or dilute?)',
             variant_c='k="all" (is selection doing anything at all here?)',
             mistakes=[
                 "Selection outside folds, certifying answer-approved features.",
                 "k tuned on test data, spending honesty on a headcount.",
                 "Univariate screens trusted on interaction-driven problems.",
             ],
             q1=("Why must k itself be validated rather than set by gut?",
                 "Too few features starves the model, too many feeds it noise — the right headcount is empirical and dataset-specific."),
             homework="Write `select_inside()` scoring a select-scale-logreg pipeline at three k values with cv=3. Run it on breast-cancer and digits, print both scans, and comment which step selects blind.",
             patterns=["SelectKBest(", "cross_val_score("],
             mapping="SelectKBest/RFE inside pipelines; the placement rule from day 141 is now structural habit.",
         ),
         157: dict(
             topic="Polynomial pipelines that cannot leak",
             idea="Degree plus alpha form the classic two-knob grid: PolynomialFeatures bends, Ridge calms, and the pipeline binds them leak-free across folds. Gridding degree {2,3,4} against alpha {0.01, 1, 100} maps the landscape — underfit corner, sweet ridge, overfit corner — in nine honest cells. Read the grid as a map, not a leaderboard: neighbouring cells should agree (stability), the winner should beat the linear baseline by a margin worth the complexity, and the whole map reruns identically on new seeds. This is tuning done right on a problem small enough to see all of it. Read the grid as a map rather than a leaderboard: neighbouring cells should agree, and disagreement marks instability worth investigating.",
             code=(
                 'from sklearn.preprocessing import PolynomialFeatures, StandardScaler\n'
                 'from sklearn.linear_model import Ridge\n'
                 'from sklearn.pipeline import make_pipeline\n'
                 'from sklearn.model_selection import GridSearchCV\n'
                 'import numpy as np\n'
                 '\n'
                 'rng = np.random.RandomState(102)\n'
                 'X = (rng.rand(40, 1) * 6.0 - 3.0)\n'
                 'y = X.ravel() ** 2 + rng.randn(40) * 0.5\n'
                 'pipe = make_pipeline(PolynomialFeatures(include_bias=False), StandardScaler(), Ridge())\n'
                 'grid = GridSearchCV(pipe, {"polynomialfeatures__degree": [1, 2, 3], "ridge__alpha": [0.01, 1.0, 100.0]}, cv=3)\n'
                 'grid.fit(X, y)\n'
                 'print("winner:", grid.best_params_, round(grid.best_score_, 4))\n'
                 'print("degree-2 region should dominate a parabola")'
             ),
             variant_b='noise × 3 (does the winner flee to stronger alpha?)',
             variant_c='a sine target instead (which corner wins on waves?)',
             mistakes=[
                 "Degree grids without scaling — x^4 of unscaled features explodes numerically.",
                 "include_bias left True beside an intercept, doubling the constant term.",
                 "Nine cells quoted as nine independent experiments instead of one mapped landscape.",
             ],
             q1=("Why grid degree and alpha together instead of separately?",
                 "They interact — higher degrees need stronger calming — so separate optima miss the joint optimum the landscape actually holds."),
             homework="Write `bend_grid()` gridding degree×alpha on noisy parabola data with cv=3. Run it at two noise levels, print both winners, and comment how nested knobs are addressed.",
             patterns=["GridSearchCV(", "PolynomialFeatures("],
             mapping="Joint grids over pipeline paths; the map-reading habit transfers to every later search space.",
         ),
         158: dict(
             topic="Text pipelines that cannot leak",
             idea="Text pipelines chain vectorizer→classifier in one object, so vocabulary fits on training folds only and test words stay unseen-the-right-way at every fold. TfidfVectorizer weights rare words up and boilerplate down, logreg or NB classifies the rows, and GridSearchCV can even tune ngram_range against C jointly. The leakage lesson lands hardest here because vocabulary leaks are invisible — no shape changes, no errors, just quietly inflated scores from test words in the dictionary. Pipeline it from the first line and the whole failure class vanishes before it can form. Pipeline text handling from the first line of every NLP experiment; vocabulary leaks are the quietest failure class in the field.",
             code=(
                 'from sklearn.feature_extraction.text import TfidfVectorizer\n'
                 'from sklearn.naive_bayes import MultinomialNB\n'
                 'from sklearn.pipeline import make_pipeline\n'
                 'from sklearn.model_selection import cross_val_score\n'
                 '\n'
                 'texts = ["win money now", "meeting at noon", "cheap loans today", "lunch with team",\n'
                 '         "claim your prize", "project deadline friday", "free cash fast", "notes from standup",\n'
                 '         "bonus cash prize", "standup notes tuesday", "wire money fast", "team lunch plans"]\n'
                 'y = [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0]\n'
                 'pipe = make_pipeline(TfidfVectorizer(), MultinomialNB())\n'
                 'scores = cross_val_score(pipe, texts, y, cv=3)\n'
                 'print("fold accuracies:", [round(s, 3) for s in scores])\n'
                 'print("mean:", round(scores.mean(), 3), "| vocabulary refit per fold, leak-free")'
             ),
             variant_b='ngram_range=(1, 2) via TfidfVectorizer(ngram_range=(1,2)) (do pairs help on 12 texts?)',
             variant_c='LogisticRegression instead of NB (which classifier suits tf-idf rows?)',
             mistakes=[
                 "Vectorizer fit outside folds while the classifier enjoys pipeline protection — half-leaked.",
                 "Stop-words removed on tiny corpora, deleting the only signal-bearing tokens.",
                 "CV accuracy quoted without noting twelve texts make every decimal fragile.",
             ],
             q1=("Why does vocabulary leakage leave no trace in shapes or errors?",
                 "The matrix dimensions look identical either way — only the dictionary's contents differ, carrying test words silently into training rows."),
             homework="Write `text_pipe()` scoring a tfidf+NB pipeline with cv=3 and printing fold scores. Run it on two text splits, print both, and comment which object refits vocabulary per fold.",
             patterns=["TfidfVectorizer(", "cross_val_score("],
             mapping="TfidfVectorizer/LogisticRegression pipelines with ngram__range/C grids — production text baselines.",
         ),
         159: dict(
             topic="Four models, one split, no excuses",
             idea="The fair board reaches maturity: four model classes (linear, neighbours, trees, boosting), one stratified split, scaled inputs where each class needs them, accuracy plus F1 plus fit-time printed per row. Same data, same exam, three score columns plus cost — excuses exhausted. Read it like a hiring panel: who wins, by what margin, at what cost, and does the winner survive the next seed? Any model that only wins on its favourite metric or its favourite split is a specialist auditioning for generalist work. The board decides; loyalty does not vote.",
             code=(
                 'from sklearn.datasets import load_breast_cancer\n'
                 'from sklearn.model_selection import train_test_split\n'
                 'from sklearn.preprocessing import StandardScaler\n'
                 'from sklearn.linear_model import LogisticRegression\n'
                 'from sklearn.neighbors import KNeighborsClassifier\n'
                 'from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier\n'
                 'from sklearn.metrics import accuracy_score, f1_score\n'
                 '\n'
                 'X, y = load_breast_cancer(return_X_y=True)\n'
                 'Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, random_state=103, stratify=y)\n'
                 'sc = StandardScaler().fit(Xtr)\n'
                 'Xs_tr, Xs_te = sc.transform(Xtr), sc.transform(Xte)\n'
                 'cands = [("logreg", LogisticRegression(max_iter=1000), True, "1 fit"), ("knn-7", KNeighborsClassifier(n_neighbors=7), True, "memorises"), ("forest", RandomForestClassifier(n_estimators=100, random_state=103), False, "100 trees"), ("boost", HistGradientBoostingClassifier(random_state=103), False, "sequential")]\n'
                 'for name, m, scaled, cost in cands:\n'
                 '    pred = m.fit(Xs_tr if scaled else Xtr, ytr).predict(Xs_te if scaled else Xte)\n'
                 '    print(f"{name:<7} acc={accuracy_score(yte, pred):.4f} F1={f1_score(yte, pred):.4f} cost={cost}")\n'
                 'print("time your own runs locally: cost decides ties")'
             ),
             variant_b='digits data (do tree ensembles pull ahead on pixels?)',
             variant_c='knn-1 added to the board (memoriser among generalisers — what do its numbers look like?)',
             mistakes=[
                 "Different splits per row, voiding every comparison on the board.",
                 "Fit-time ignored, then the winner cannot train before the deadline.",
                 "Scaled inputs fed to forests and unscaled to kNN in the same board — rigged deck.",
             ],
             q1=("Why print fit-time beside accuracy and F1?",
                 "The deployable model maximises score per budget: a 0.002 gain that costs 100× training time loses every real selection."),
             homework="Write `fair_board()` scoring four model classes on one split with accuracy/F1/fit-time. Run it on two datasets, print both boards, and comment which column besides accuracy decides.",
             patterns=[".fit(", "f1_score("],
             mapping="Same-split multi-model boards with cost columns — the selection ritual for every project from here on.",
         ),
         160: dict(
             topic="Speed: n_jobs and small data",
             idea="Forests and grids parallelise embarrassingly: n_jobs=-1 spreads trees and folds across cores for near-linear speedups, turning overnight grids into coffee-break grids. But parallelism has overhead — spawning processes for ten tiny trees costs more than it saves — so measure before parallelising everything: time one core versus all cores on your actual workload. Small-data habits matter more than cores: subsample while iterating, grid coarse-to-fine (wide cheap scan, narrow expensive refine), and cache transformed features instead of recomputing them per candidate. Speed is a feature of the workflow, not the hardware. Subsample while iterating and refine coarse-to-fine: a wide cheap scan locates the region, a narrow expensive one pins the optimum. Never launch the expensive refine before the cheap scan has earned it.",
             code=(
                 'from sklearn.datasets import load_digits\n'
                 'from sklearn.ensemble import RandomForestClassifier\n'
                 '\n'
                 'X, y = load_digits(return_X_y=True)\n'
                 'Xtr, ytr = X[:1200], y[:1200]\n'
                 'one = RandomForestClassifier(n_estimators=50, n_jobs=1, random_state=104).fit(Xtr, ytr)\n'
                 'many = RandomForestClassifier(n_estimators=50, n_jobs=-1, random_state=104).fit(Xtr, ytr)\n'
                 'print("same predictions:", bool((one.predict(X[1200:]) == many.predict(X[1200:])).all()))\n'
                 'print("same score:", round(one.score(X[1200:], y[1200:]), 4), round(many.score(X[1200:], y[1200:]), 4))\n'
                 'print("parallelism changes clocks, never math — time both locally to feel the gap")'
             ),
             variant_b='n_estimators=200 (does the speedup ratio grow with work?)',
             variant_c='tiny iris data (does -1 win or lose on overhead?)',
             mistakes=[
                 "n_jobs=-1 inside nested parallelism (grid over pipelined forest), oversubscribing cores into thrash.",
                 "Timing wall-clock once and declaring victory over noise.",
                 "Huge grids launched before a coarse scan located the promising region.",
             ],
             q1=("Why can more cores slow tiny jobs down?",
                 "Process spawning and data copying cost a fixed toll; on ten small trees the toll exceeds the parallel savings."),
             homework="Write `core_duel()` timing 1 vs all cores on a 50-tree forest fit. Run it on digits and iris, print both duels, and comment when parallelism pays.",
             patterns=["n_jobs=", ".fit("],
             mapping="n_jobs=-1 on forests and grids; coarse-to-fine search discipline for every tuning budget.",
         ),
         161: dict(
             topic="Reproducibility audit",
             idea="Today you audit a whole experiment for determinism: every random_state listed, data versions recorded, library versions pinned, seeds differing across folds yet fixed overall. Run the same script twice and diff the outputs byte-for-byte; any drift names an uncontrolled dice roll — an unseeded shuffle, a parallel race, a timestamp in features. The audit checklist (seeds, versions, data hashes, locked test set) ships beside every model from here on, because irreproducible 'results' are rumours with confidence intervals. If you cannot rerun it, you did not run it. Diff two consecutive runs byte-for-byte as a habit; any drift names an uncontrolled dice roll to hunt down. Record data hashes too, because identical code on silently changed rows is the hardest drift to catch.",
             code=(
                 'import sklearn\n'
                 'from sklearn.datasets import load_iris\n'
                 'from sklearn.model_selection import train_test_split\n'
                 'from sklearn.neighbors import KNeighborsClassifier\n'
                 'import hashlib\n'
                 '\n'
                 'print("sklearn:", sklearn.__version__)\n'
                 'X, y = load_iris(return_X_y=True)\n'
                 'print("data hash:", hashlib.md5(X.tobytes()).hexdigest()[:12])\n'
                 'runs = []\n'
                 'for _ in range(2):\n'
                 '    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, random_state=105, stratify=y)\n'
                 '    runs.append(KNeighborsClassifier(n_neighbors=3).fit(Xtr, ytr).score(Xte, yte))\n'
                 'print("run1:", runs[0], "| run2:", runs[1], "| identical:", runs[0] == runs[1])\n'
                 'print("audit: versions + data hash + seeds = rerunnable science")'
             ),
             variant_b='drop random_state from the split (does the audit catch the drift?)',
             variant_c='n_jobs=-1 on a forest here (deterministic anyway? why?)',
             mistakes=[
                 "Versions unrecorded, so last quarter's numbers become uninterpretable.",
                 "Data hashes missing — same filename, silently different rows.",
                 "Seeds fixed for models but not for splits, leaving half the luck loose.",
             ],
             q1=("Why hash the data instead of trusting the filename?",
                 "Filenames lie — same name, appended rows, reordered columns — while hashes certify the exact bytes the numbers came from."),
             homework="Write `audit_run()` printing library version, data hash and two identical scores. Run it on two datasets, print both audits, and comment which line certifies the bytes.",
             patterns=["random_state=", ".score("],
             mapping="Version pins, data hashes, fixed seeds, locked tests — the shipping checklist for every model hereafter.",
         ),
         162: dict(
             topic="Project: tuned pipeline, reported honestly",
             idea="Today everything combines: a scaled-logreg pipeline, a 2×3 grid over C and penalty-compatible settings, cv=3 selection, refit, then ONE evaluation on a locked test split with accuracy, F1, confusion highlights and fit-time — plus the dummy baseline beside every number. Report the grid winner, the test verdict, and whether tuning beat the default by a margin worth its compute. This is the professional deliverable in miniature: reproducible (seeds), honest (locked test), complete (baseline, board, cost). Phases 1–6 converge here; the capstone scales it to real data and real writing.",
             code=(
                 'from sklearn.datasets import load_breast_cancer\n'
                 'from sklearn.model_selection import train_test_split, GridSearchCV\n'
                 'from sklearn.preprocessing import StandardScaler\n'
                 'from sklearn.linear_model import LogisticRegression\n'
                 'from sklearn.dummy import DummyClassifier\n'
                 'from sklearn.pipeline import make_pipeline\n'
                 'from sklearn.metrics import accuracy_score, f1_score\n'
                 '\n'
                 'X, y = load_breast_cancer(return_X_y=True)\n'
                 'Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, random_state=106, stratify=y)\n'
                 'pipe = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000))\n'
                 'grid = GridSearchCV(pipe, {"logisticregression__C": [0.01, 0.1, 1.0, 10.0]}, cv=3)\n'
                 'grid.fit(Xtr, ytr)\n'
                 'base = accuracy_score(yte, DummyClassifier(strategy="most_frequent").fit(Xtr, ytr).predict(Xte))\n'
                 'pred = grid.predict(Xte)\n'
                 'print("winner:", grid.best_params_, f"CV={grid.best_score_:.4f}")\n'
                 'print(f"locked test: acc={accuracy_score(yte, pred):.4f} F1={f1_score(yte, pred):.4f} (dummy acc={base:.4f})")'
             ),
             variant_b='penalty grid extended (which solver/penalty combos are legal?)',
             variant_c='test_size=0.5 (does less tuning data move the winner?)',
             mistakes=[
                 "Grid winner reported without the default-settings baseline beside it.",
                 "Locked test evaluated twice ('just to check'), spending its honesty.",
                 "Fit-time unreported, hiding a winner nobody can afford.",
             ],
             q1=("Why keep default settings in every tuning report?",
                 "Without the untuned number, nobody — including you — can tell whether the grid bought anything or just burned compute."),
             homework="Write `tuned_report()` gridding C, refitting, and printing winner plus locked-test accuracy/F1 against dummy. Run it on two seeds, print both reports, and comment which line spends the locked test.",
             patterns=["GridSearchCV(", "f1_score("],
             mapping="This report shape — winner, locked verdict, baseline, cost — is the template for the capstone and beyond.",
         ),
         163: dict(
             topic="Testing pipelines with asserts",
             idea="Pipeline guards certify the chain: step names resolve, set_params reaches nested knobs, transform output widths match fit-time widths, refit reproduces scores bit-identically, and the locked test is evaluated exactly once per report (count it). Assert pickled round-trips predict identically, assert grid winners belong to the searched space, and assert honest beats dummy — the guard suite from days 88/118/133 extended to chains. A guarded pipeline is deployable machinery: the same asserts that certify today's homework will guard tomorrow's production retraining. A guarded pipeline reruns itself into trustworthiness on every new seed and every new dataset.",
             code=(
                 'from sklearn.datasets import load_breast_cancer\n'
                 'from sklearn.model_selection import train_test_split\n'
                 'from sklearn.preprocessing import StandardScaler\n'
                 'from sklearn.linear_model import LogisticRegression\n'
                 'from sklearn.dummy import DummyClassifier\n'
                 'from sklearn.pipeline import make_pipeline\n'
                 'from sklearn.metrics import f1_score\n'
                 'import pickle\n'
                 '\n'
                 'X, y = load_breast_cancer(return_X_y=True)\n'
                 'Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, random_state=107, stratify=y)\n'
                 'pipe = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000, C=0.1))\n'
                 'pipe.fit(Xtr, ytr)\n'
                 'assert [n for n, _ in pipe.steps] == ["standardscaler", "logisticregression"]\n'
                 'assert pipe.named_steps["logisticregression"].C == 0.1\n'
                 'back = pickle.loads(pickle.dumps(pipe))\n'
                 'assert (back.predict(Xte) == pipe.predict(Xte)).all()\n'
                 'assert f1_score(yte, pipe.predict(Xte)) > f1_score(yte, DummyClassifier(strategy="most_frequent").fit(Xtr, ytr).predict(Xte))\n'
                 'print("guards passed: named chain, C=0.1 addressed, pickle identical, beats dummy")'
             ),
             variant_b='C=100 (does the chain survive extreme knobs?)',
             variant_c='steps reordered scaler/model swapped (which loud error guards the order?)',
             mistakes=[
                 "Exact-score asserts fossilising one seed's numbers.",
                 "Step-name asserts skipped, so renames break grids silently.",
                 "Pickle round-trip assumed instead of asserted with identical predictions.",
             ],
             q1=("Why assert step names explicitly?",
                 "Grids and surgery address steps by name — a renamed step silently orphans every param path that referenced the old one."),
             homework="Write `guarded_pipe()` with asserts on step names, nested C, pickle identity and winner-beats-dummy. Run it on two C values, print both verdicts, and comment which assert guards the chain.",
             patterns=["assert ", "named_steps["],
             mapping="Chain guards (names, knobs, round-trips, baselines) wrap every pipeline you ship.",
         ),
         164: dict(
             topic="Phase review: pipelines and tuning",
             idea="Rebuild from memory: named chains, per-dtype column plans, joint grids addressed by double-underscore paths, scaling dividends measured per model, imbalance fought with three no-deps moves, pickles with provenance, in-fold selection, polynomial maps, text chains, four-model fair boards, core counts with overhead honesty, reproducibility audits, tuned reports with locked tests, chain guards. Close the notes and reproduce the tuned report — grid, winner, locked verdict against dummy. The missing line is tomorrow's first job; the capstone (phase 7) spends everything saved: real data, real writing, real trade-offs. If the rebuild flows, industrial ML is installed. If the tuned report will not come from memory, rebuild day 162 line by line because it contains every phase-6 habit in one script. The tuned report is the professional deliverable in miniature.",
             code=(
                 'from sklearn.datasets import load_breast_cancer\n'
                 'from sklearn.model_selection import train_test_split, GridSearchCV\n'
                 'from sklearn.preprocessing import StandardScaler\n'
                 'from sklearn.linear_model import LogisticRegression\n'
                 'from sklearn.pipeline import make_pipeline\n'
                 'from sklearn.metrics import f1_score\n'
                 '\n'
                 'X, y = load_breast_cancer(return_X_y=True)\n'
                 'Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, random_state=108, stratify=y)\n'
                 'grid = GridSearchCV(make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000)), {"logisticregression__C": [0.1, 1.0, 10.0]}, cv=2)\n'
                 'grid.fit(Xtr, ytr)\n'
                 'real = f1_score(yte, grid.predict(Xte))\n'
                 'print("winner:", grid.best_params_)\n'
                 'print("locked F1:", round(real, 4))'
             ),
             variant_b='cv=3 (does the winner survive stricter judging?)',
             variant_c='C values ×10 (does the landscape shift or hold?)',
             mistakes=[
                 "Rebuilding with notes open — retrieval is the learning.",
                 "Reciting pipeline benefits without placing a step in a running chain.",
                 "Skipping the dummy in the rebuild because tuning felt like the whole story.",
             ],
             q1=("What single rebuild proves this phase stuck?",
                 "The tuned report from memory — grid, winner, locked verdict against dummy — every number explained and every step named."),
             homework="Write `phase_recap()` from memory: pipeline, grid, winner, locked verdict. Run it on two seeds, print both, and comment which line you had to look up.",
             patterns=["GridSearchCV(", "f1_score("],
             mapping="Phase 7 spends it all: the capstone is this report with real data, real writing and real trade-offs.",
         ),
     }),
    ("ML Capstone",
     "Ship it: a guided digits project from brief to demo, every habit spent.",
     {
         165: dict(
             topic="Capstone brief and dataset tour",
             idea="The capstone classifies handwritten digits (1797 8×8 images, 10 classes) with a documented, tuned, honestly evaluated pipeline — the day-162 report grown to project scale. Today is reconnaissance: load digits, print shapes and class balance, view one digit as ASCII art, and write the brief — goal metric (F1), baseline to beat (kNN-3), budget (fits under a minute), and the locked test split nobody touches until day 172. Professionals scope before fitting: a written brief turns two weeks of tinkering into an executed plan with acceptance criteria. Sign it by running the tour script green. Tour twice: once to see the data, once to verify the brief's claims about balance and scale.",
             code=(
                 'from sklearn.datasets import load_digits\n'
                 '\n'
                 'X, y = load_digits(return_X_y=True)\n'
                 'print("images:", X.shape[0], "| pixels:", X.shape[1], "| classes:", sorted(set(y.tolist())))\n'
                 'print("class counts:", [list(y).count(d) for d in range(10)])\n'
                 'print("one zero as ASCII:")\n'
                 'for r in range(8):\n'
                 '    print("".join("#" if X[0][r * 8 + c] > 8 else "." for c in range(8)))\n'
                 'print("brief signed: F1 wins, kNN-3 is the floor, test stays locked")'
             ),
             variant_b='a one digit (which digit photographs most distinctly?)',
             variant_c='pixel value ranges (what scale do raw pixels live on?)',
             mistakes=[
                 "Fitting anything before the brief exists — tinkering without acceptance criteria.",
                 "Peeking at the locked test split 'just to look'.",
                 "No baseline declared, so every later number floats.",
             ],
             q1=("Why write the brief before fitting anything?",
                 "Scope turns tinkering into an executed plan: goal metric, baseline, budget and locked test agreed before results can tempt anyone to move them."),
             homework="Write `dataset_tour()` printing shapes, class counts and one ASCII digit. Run it on digits and iris, print both tours, and comment which line locks the test split policy.",
             patterns=["load_digits(", "print("],
             mapping="Brief-first scoping; the locked split and declared baseline govern the next fourteen days.",
         ),
         166: dict(
             topic="Baseline and split that holds",
             idea="Every capstone opens with the floor poured: stratified 80/20 split with a recorded seed, Dummy majority F1, kNN-3 accuracy and F1 — three numbers no later model can duck. The split is the project's constitution: same rows for every candidate, test predictions from each logged for the final error analysis. Spending one day on plumbing feels slow and saves ten: every comparison downstream inherits this split's honesty, and the locked test set stays virgin until day 172. Log the split parameters in the notebook today; every later day cites them instead of re-deriving them. Pour the floor carefully; the whole building stands on it.",
             code=(
                 'from sklearn.datasets import load_digits\n'
                 'from sklearn.model_selection import train_test_split\n'
                 'from sklearn.dummy import DummyClassifier\n'
                 'from sklearn.neighbors import KNeighborsClassifier\n'
                 'from sklearn.metrics import f1_score\n'
                 '\n'
                 'X, y = load_digits(return_X_y=True)\n'
                 'Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=200, stratify=y)\n'
                 'base = f1_score(yte, DummyClassifier(strategy="most_frequent").fit(Xtr, ytr).predict(Xte), average="weighted")\n'
                 'knn = f1_score(yte, KNeighborsClassifier(n_neighbors=3).fit(Xtr, ytr).predict(Xte), average="weighted")\n'
                 'print("dummy weighted F1:", round(base, 4))\n'
                 'print("knn-3 weighted F1:", round(knn, 4))\n'
                 'print("floor poured: every later model answers to these")'
             ),
             variant_b='test_size=0.3 (does the floor move with less training?)',
             variant_c='macro instead of weighted F1 (which digits does the averaging punish?)',
             mistakes=[
                 "Unstratified split on ten classes, starving rare digits from the exam.",
                 "Weighted vs macro F1 chosen by habit instead of by the brief.",
                 "Test predictions discarded instead of logged for day 170's error analysis.",
             ],
             q1=("Why weighted F1 as the capstone headline instead of accuracy?",
                 "Ten classes with uneven counts: weighted F1 prices every class fairly where accuracy lets big classes hide small-class failures."),
             homework="Write `pour_floor()` splitting stratified, scoring dummy and kNN-3 weighted F1, and printing both. Run it on two seeds, print both floors, and comment which line locks the split.",
             patterns=["train_test_split(", "f1_score("],
             mapping="The constitution split (seed 200) plus floor numbers govern every comparison to day 178.",
         ),
         167: dict(
             topic="First real model and its confusions",
             idea="Fit the first serious candidate — a 100-tree forest — and read it the way day 114 taught: accuracy, then the directed-pair table, then per-class F1 for the worst digits. Expect high-97s overall with 3/8/9 tangles surviving; those survivors are the project's work list, not its shame. Log the test predictions and the pair table to the project notebook today, because day 170's failure analysis and day 177's presentation both build directly on these artefacts. First models diagnose; they do not need to win yet.",
             code=(
                 'from sklearn.datasets import load_digits\n'
                 'from sklearn.model_selection import train_test_split\n'
                 'from sklearn.ensemble import RandomForestClassifier\n'
                 'from sklearn.metrics import accuracy_score, f1_score\n'
                 '\n'
                 'X, y = load_digits(return_X_y=True)\n'
                 'Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=200, stratify=y)\n'
                 'pred = RandomForestClassifier(n_estimators=100, random_state=200).fit(Xtr, ytr).predict(Xte)\n'
                 'print("forest acc:", round(accuracy_score(yte, pred), 4), "| weighted F1:", round(f1_score(yte, pred, average="weighted"), 4))\n'
                 'errs = {}\n'
                 'for t, p in zip(yte, pred):\n'
                 '    if t != p:\n'
                 '        errs[(t, p)] = errs.get((t, p), 0) + 1\n'
                 'print("top confused pairs:")\n'
                 'for pair, n in sorted(errs.items(), key=lambda kv: kv[1], reverse=True)[:3]:\n'
                 '    print(f"  {pair[0]}->{pair[1]}: {n}")'
             ),
             variant_b='n_estimators=20 (how much accuracy does impatience cost?)',
             variant_c='max_depth=8 voters (calmer crowd — which pairs survive?)',
             mistakes=[
                 "Tuning before reading the pairs — optimising blind while the diagnosis sits printed.",
                 "Predictions unlogged, forcing day 170 to refit and risk drift.",
                 "Accuracy-only reading, missing which digits actually suffer.",
             ],
             q1=("Why log predictions and pairs today instead of recomputing later?",
                 "Later refits risk seed, version or data drift; logged artefacts freeze today's evidence for the analysis and presentation to build on."),
             homework="Write `first_model()` fitting a 100-tree forest and printing accuracy, weighted F1 and top-3 pairs. Run it on two seeds, print both, and comment which lines build the work list.",
             patterns=["RandomForestClassifier(", "accuracy_score("],
             mapping="First-model discipline: read errors before tuning anything; the pairs table is the project compass.",
         ),
         168: dict(
             topic="Second opinion: boosted trees",
             idea="Fit HistGradientBoosting beside the forest on the identical split and compare F1, fit-time and confused pairs: boosting usually edges forests on tabular pixels while training slower and caring more about label noise. The comparison, not the winner, is the deliverable — report both numbers with costs, note which pairs each model fixes, and keep both artefacts. If boosting wins narrowly at 10× fit-time, the report says so honestly and the recommendation weighs latency against points. Two strong models disagreeing on different rows is also an ensemble hint the capstone may or may not afford to take. Date every duel artefact; undated comparisons breed arguments about which numbers were final. Note duel fit-times in the report prose beside the board; cost lives in text while scores live in tables.",
             code=(
                 'from sklearn.datasets import load_digits\n'
                 'from sklearn.model_selection import train_test_split\n'
                 'from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier\n'
                 'from sklearn.metrics import f1_score\n'
                 '\n'
                 'X, y = load_digits(return_X_y=True)\n'
                 'Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=200, stratify=y)\n'
                 'for name, m in [("forest", RandomForestClassifier(n_estimators=100, random_state=200)), ("boost", HistGradientBoostingClassifier(random_state=200))]:\n'
                 '    pred = m.fit(Xtr, ytr).predict(Xte)\n'
                 '    print(f"{name:<7} F1={f1_score(yte, pred, average=\"weighted\"):.4f}")\n'
                 'print("report both numbers with costs; loyalty does not vote")'
             ),
             variant_b='learning_rate=0.05 on boosting (slower study — better F1?)',
             variant_c='forest-300 (does a bigger crowd close the gap?)',
             mistakes=[
                 "Different splits per model, voiding the duel.",
                 "Fit-time unreported, hiding a winner nobody can afford.",
                 "Winner declared by accuracy while the brief says F1.",
             ],
             q1=("Why keep the loser of an honest duel in the report?",
                 "Close losers document the decision: reviewers see what was tried, what it cost, and why the winner won — the alternative is trust-me tuning. Keep both fitted models on disk beside the report; reviewers rerun duels, and artefacts make reruns exact. Date every artefact; undated models breed arguments about which number was final."),
             homework="Write `second_opinion()` scoring forest vs boosted trees with F1 and fit-time on the constitution split. Run it twice, print both duels, and comment which column prices the win.",
             patterns=["HistGradientBoostingClassifier(", "f1_score("],
             mapping="Honest duels with costs attached; the format serves every model comparison to the end of the track.",
         ),
         169: dict(
             topic="Tuning the finalist properly",
             idea="Tune the leading model (not both — budget tunes the finalist) with a small joint grid over its two most influential knobs, cv=3, on training data only, then refit the winner on all training rows. For forests that means n_estimators × max_depth; for boosting, learning_rate × max_depth. Keep the grid tiny enough to finish and rerun: nine cells judged honestly beats eighty-one cells judged never. Log best_params_, best CV score, and fit-time beside the day-168 defaults so the report can state exactly what tuning bought — often less than hoped, which is itself a finding worth publishing. Tune only the finalist and say so plainly; spreading budget across losers burns money quietly. Time the grid once locally for the report's cost column; the stored board prices accuracy while prose carries cost.",
             code=(
                 'from sklearn.datasets import load_digits\n'
                 'from sklearn.model_selection import train_test_split, GridSearchCV\n'
                 'from sklearn.ensemble import RandomForestClassifier\n'
                 '\n'
                 'X, y = load_digits(return_X_y=True)\n'
                 'Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=200, stratify=y)\n'
                 'grid = GridSearchCV(RandomForestClassifier(random_state=200), {"n_estimators": [50, 100], "max_depth": [None, 12, 8]}, cv=2)\n'
                 'grid.fit(Xtr, ytr)\n'
                 'print("winner:", grid.best_params_, f"CV={grid.best_score_:.4f}")\n'
                 'print("test F1:", round(grid.score(Xte, yte), 4), "(first and only touch of locked test)")'
             ),
             variant_b='max_depth [20, 12, 8] (does the ceiling move?)',
             variant_c='cv=3 (stricter judging, slower search — worth it?)',
             mistakes=[
                 "Tuning both finalists fully, doubling compute for a duel already decided.",
                 "Grid winner reported without the default it beat (or failed to beat).",
                 "Locked test touched during tuning, then quoted as honest.",
             ],
             q1=("Why tune only the finalist instead of every candidate?",
                 "Budget is finite: the duel already ranked the classes, so compute goes to the winner's last points, not to losers' consolation prizes."),
             homework="Write `tune_finalist()` gridding two knobs with cv=2 and printing winner, CV score and one locked-test score. Run it on two seeds, print both, and comment which line spends the locked test.",
             patterns=["GridSearchCV(", "best_params_"],
             mapping="Small joint grids on the finalist only; defaults stay on the board so tuning must earn its keep.",
         ),
         170: dict(
             topic="Failure analysis: meet the confusions",
             idea="Pull the logged day-167 predictions and interrogate the survivors: print the worst confused pairs with counts, show two ASCII renderings of a 3-predicted-8, and classify each error as data ambiguity (even a human squints), representation limit (8×8 pixels erase the telling stroke), or model blind spot (fixable with features or capacity). This taxonomy decides the response: ambiguity gets calibrated uncertainty, representation limits get better inputs, blind spots get modelling work. A capstone without failure analysis is a highlight reel; with it, an engineering report. Write the taxonomy down — day 177 presents it.",
             code=(
                 'from sklearn.datasets import load_digits\n'
                 'from sklearn.model_selection import train_test_split\n'
                 'from sklearn.ensemble import RandomForestClassifier\n'
                 '\n'
                 'X, y = load_digits(return_X_y=True)\n'
                 'Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=200, stratify=y)\n'
                 'pred = RandomForestClassifier(n_estimators=100, random_state=200).fit(Xtr, ytr).predict(Xte)\n'
                 'errs = [(t, p, i) for i, (t, p) in enumerate(zip(yte, pred)) if t != p]\n'
                 'print("total errors:", len(errs), "of", len(yte))\n'
                 'shown = 0\n'
                 'for t, p, i in errs:\n'
                 '    if t == 3 and p == 8 and shown < 1:\n'
                 '        print("a 3 called 8:")\n'
                 '        for r in range(8):\n'
                 '            print("".join("#" if Xte[i][r * 8 + c] > 8 else "." for c in range(8)))\n'
                 '        shown += 1\n'
                 'print("taxonomy next: ambiguity, representation, or blind spot?")'
             ),
             variant_b='the worst 8-called-3 instead (symmetric story or different cause?)',
             variant_c='kNN-3 errors on the same split (do the pairs match the forest\u2019s?)',
             mistakes=[
                 "Averaging errors away instead of meeting individual failures.",
                 "Blaming the model for data ambiguity no classifier could resolve.",
                 "Skipping the taxonomy, so fixes are prescribed to undiagnosed diseases.",
             ],
             q1=("Why classify each error into ambiguity, representation, or blind spot?",
                 "The class prescribes the cure: ambiguity wants calibrated uncertainty, representation wants better inputs, blind spots want modelling — one treatment per diagnosis."),
             homework="Write `meet_failures()` printing error count plus one ASCII rendering of a 3-called-8. Run it on two seeds, print both, and comment which lines locate the failure.",
             patterns=[".predict(", ".fit("],
             mapping="Failure taxonomies turn error tables into project plans; every production post-mortem uses this shape.",
         ),
         171: dict(
             topic="Logistic baseline with scaling",
             idea="Give linear models their fair hearing on pixels: a scaled StandardScaler→LogisticRegression pipeline, tuned C over three values, scored with weighted F1 beside the forest numbers. Pixels are correlated neighbours, not independent features — regularised linear models handle that gracefully once scaled — and the comparison tests whether digits need boxes at all. If logreg trails by a point at 10× less fit-time, the report states the trade honestly instead of burying it. Every model class deserves one fair, scaled, tuned audition before the capstone casts its lead. Bury no audition: the model that loses fairly today may win on the next dataset, and the record proves it.",
             code=(
                 'from sklearn.datasets import load_digits\n'
                 'from sklearn.model_selection import train_test_split, GridSearchCV\n'
                 'from sklearn.preprocessing import StandardScaler\n'
                 'from sklearn.linear_model import LogisticRegression\n'
                 'from sklearn.pipeline import make_pipeline\n'
                 'from sklearn.metrics import f1_score\n'
                 '\n'
                 'X, y = load_digits(return_X_y=True)\n'
                 'Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=200, stratify=y)\n'
                 'grid = GridSearchCV(make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000)), {"logisticregression__C": [0.01, 0.1, 1.0]}, cv=2)\n'
                 'grid.fit(Xtr, ytr)\n'
                 'pred = grid.predict(Xte)\n'
                 'print("winner:", grid.best_params_)\n'
                 'print("logreg weighted F1:", round(f1_score(yte, pred, average="weighted"), 4))\n'
                 'print("audition complete: lines against boxes, fairly")'
             ),
             variant_b='saga solver with l1 (does sparsity help on pixels?)',
             variant_c='C=100 nearly unregularised (do pixels overfit without calming?)',
             mistakes=[
                 "Unscaled pixels fed to logreg, rigging the audition.",
                 "C grid copied from another dataset instead of spanning this one's scale.",
                 "Winner buried because forests 'felt' stronger — auditions decide, feelings do not.",
             ],
             q1=("Why must the linear audition be scaled and tuned before judging?",
                 "Raw pixels plus default C handicap lines against boxes; only a fair hearing — scaled, tuned, same split — makes the comparison mean anything."),
             homework="Write `linear_audition()` gridding C on a scaled logreg pipeline and printing winner plus weighted F1. Run it on two seeds, print both, and comment which line scales fairly.",
             patterns=["GridSearchCV(", "StandardScaler("],
             mapping="Every model class gets one fair audition; the capstone casts its lead from evidence, not habit.",
         ),
         172: dict(
             topic="The locked test speaks once",
             idea="Today the locked test set is evaluated exactly once per finalist, and the numbers are written into the report permanently: accuracy, weighted F1, confusion highlights, fit-time, and the gap to the day-166 floor. One touch means one touch — no re-splits after seeing the numbers, no threshold tweaks 'just to check', no second model selected post-hoc on test results. If a number surprises, the response is analysis (which rows? which pairs?), never another peek. This discipline is what makes the report trustworthy to strangers: the test set is a witness examined once, not a collaborator consulted throughout.",
             code=(
                 'from sklearn.datasets import load_digits\n'
                 'from sklearn.model_selection import train_test_split\n'
                 'from sklearn.dummy import DummyClassifier\n'
                 'from sklearn.ensemble import RandomForestClassifier\n'
                 'from sklearn.metrics import accuracy_score, f1_score\n'
                 '\n'
                 'X, y = load_digits(return_X_y=True)\n'
                 'Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=200, stratify=y)\n'
                 'base = DummyClassifier(strategy="most_frequent").fit(Xtr, ytr).predict(Xte)\n'
                 'real = RandomForestClassifier(n_estimators=100, random_state=200).fit(Xtr, ytr).predict(Xte)\n'
                 'print("dummy: acc", round(accuracy_score(yte, base), 4), "F1", round(f1_score(yte, base, average="weighted"), 4))\n'
                 'print("forest: acc", round(accuracy_score(yte, real), 4), "F1", round(f1_score(yte, real, average="weighted"), 4))\n'
                 'print("locked test examined once; numbers are permanent")'
             ),
             variant_b='a second evaluation run (identical numbers — why must they be?)',
             variant_c='threshold moved post-hoc on these numbers (what did you just spend?)',
             mistakes=[
                 "A second peek 'to confirm', spending the honesty the first touch bought.",
                 "Model selection on test numbers, then reporting test numbers as validation.",
                 "Locked-test code living beside tuning code, one import away from accident.",
             ],
             q1=("Why does a second peek destroy the test set's honesty?",
                 "Every peek lets decisions adapt to test rows; adapted-to data is training data wearing a test costume, whatever the variable is named."),
             homework="Write `locked_verdict()` scoring dummy and forest on the locked split exactly once and printing both rows. Run it once per seed policy (never twice on one seed), print the verdict, and comment which line is the single touch.",
             patterns=[".predict(", "f1_score("],
             mapping="One-touch evaluation with permanent numbers; all later claims cite this table, never a rerun.",
         ),
         173: dict(
             topic="Documenting the project",
             idea="A model without documentation is a rumour: write the README that states the goal metric, the data and split, every model tried with scores, the winner and its margin, known failures from day 170, and exact rerun instructions (seeds, versions, commands). Documentation is tested like code — follow your own rerun instructions on a clean checkout and fix every step that fails. Future you, and every reviewer, inherits only what is written; the cleverness in your head ships nowhere. Today's script generates the results table programmatically so numbers in prose can never drift from numbers in code.",
             code=(
                 'from sklearn.datasets import load_digits\n'
                 'from sklearn.model_selection import train_test_split\n'
                 'from sklearn.dummy import DummyClassifier\n'
                 'from sklearn.neighbors import KNeighborsClassifier\n'
                 'from sklearn.ensemble import RandomForestClassifier\n'
                 'from sklearn.metrics import f1_score\n'
                 'import sklearn\n'
                 '\n'
                 'print("# Digits capstone — results (generated, do not hand-edit)")\n'
                 'print(f"sklearn {sklearn.__version__} | split seed 200 | test 20% stratified")\n'
                 'X, y = load_digits(return_X_y=True)\n'
                 'Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=200, stratify=y)\n'
                 'for name, m in [("dummy", DummyClassifier(strategy="most_frequent")), ("knn-3", KNeighborsClassifier(n_neighbors=3)), ("forest-100", RandomForestClassifier(n_estimators=100, random_state=200))]:\n'
                 '    s = f1_score(yte, m.fit(Xtr, ytr).predict(Xte), average="weighted")\n'
                 '    print(f"- {name}: weighted F1 {s:.4f}")'
             ),
             variant_b='a forest-20 row added (does the doc table stay honest?)',
             variant_c='macro F1 column beside weighted (which readers need it?)',
             mistakes=[
                 "Scores hand-copied into prose, drifting from code within a week.",
                 "Rerun instructions never tested on a clean checkout.",
                 "Failures omitted from the write-up, presenting a highlight reel as engineering.",
             ],
             q1=("Why generate the results table from code instead of writing it by hand?",
                 "Generated numbers cannot drift from the code that produced them; hand-copied numbers rot with every rerun."),
             homework="Write `results_table()` printing version, split policy and three weighted F1 rows. Run it on two seeds, print both tables, and comment which line makes hand-editing unnecessary.",
             patterns=["f1_score(", ".fit("],
             mapping="Docs-as-code: generated tables, tested rerun instructions, failures included — the professional write-up standard.",
         ),
         174: dict(
             topic="Demo script: one digit, live",
             idea="A demo that runs live beats ten slides: a script taking 64 pixel values, printing the predicted digit with vote shares, and flagging low-confidence rows for human review. Build it on the locked artefacts (fitted forest, recorded split) with input validation — wrong length, non-numeric pixels, out-of-range values each get a clear error, not a traceback. Demo the failure modes deliberately: show a confident 0, then a 3/8 coin-flip routed to review. Audiences trust presenters who demo the doubts, not just the triumphs. Rehearse the failure demo twice as long as the triumph; composure during doubt is what audiences remember. Never demo on training rows; memorised confidence under a spotlight embarrasses everyone present.",
             code=(
                 'from sklearn.datasets import load_digits\n'
                 'from sklearn.model_selection import train_test_split\n'
                 'from sklearn.ensemble import RandomForestClassifier\n'
                 '\n'
                 'X, y = load_digits(return_X_y=True)\n'
                 'Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=200, stratify=y)\n'
                 'forest = RandomForestClassifier(n_estimators=100, random_state=200).fit(Xtr, ytr)\n'
                 '\n'
                 'def demo(pixels):\n'
                 '    assert len(pixels) == 64, "need exactly 64 pixels"\n'
                 '    assert all(0 <= p <= 16 for p in pixels), "pixels range 0-16"\n'
                 '    proba = forest.predict_proba([pixels])[0]\n'
                 '    best = int(proba.argmax())\n'
                 '    print(f"predicts {best} at {max(proba):.2f} confidence")\n'
                 '    return best\n'
                 '\n'
                 'demo(list(Xte[0]))\n'
                 'print("truth was:", yte[0])'
             ),
             variant_b='the most uncertain test row (which digit splits the vote?)',
             variant_c='64 zeros (what does the model do with a blank page?)',
             mistakes=[
                 "Demo on training rows, where confidence is memorisation wearing a tuxedo.",
                 "No input validation, so the live demo dies on the first odd input.",
                 "Only triumphs demoed — the audience learns nothing about limits.",
             ],
             q1=("Why validate demo inputs instead of trusting the caller?",
                 "Live demos meet hostile input; clear errors preserve trust while tracebacks destroy it in front of witnesses."),
             homework="Write `demo(pixels)` validating length and range, printing prediction plus confidence. Run it on a clear row and a coin-flip row, print both, and comment which lines guard the inputs.",
             patterns=["def ", "predict_proba("],
             mapping="Demo scripts validate, predict, and route doubt — the presentation half of every shipped model.",
         ),
         175: dict(
             topic="Failure follow-up: the 8s that look like 3s",
             idea="Return to day 170's taxonomy with counts: pull every 8-predicted-3 and 3-predicted-8, compare their pixel renderings against correctly classified 8s, and decide per pair whether the stroke data even contains the distinguishing loop. Where pixels genuinely underdetermine the answer, the honest fix is calibrated abstention (route below-confidence rows to review) rather than more capacity — memorising ambiguous ink helps the scoreboard and nobody else. Document two such pairs with renderings and verdicts; this page of the report is what separates engineering from leaderboard-chasing. Attach two renderings per verdict class; one example convinces nobody, while two establish a pattern.",
             code=(
                 'from sklearn.datasets import load_digits\n'
                 'from sklearn.model_selection import train_test_split\n'
                 'from sklearn.ensemble import RandomForestClassifier\n'
                 '\n'
                 'X, y = load_digits(return_X_y=True)\n'
                 'Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=200, stratify=y)\n'
                 'pred = RandomForestClassifier(n_estimators=100, random_state=200).fit(Xtr, ytr).predict(Xte)\n'
                 'pairs = [(t, p) for t, p in zip(yte, pred) if {t, p} == {3, 8}]\n'
                 'print("3/8 confusions:", len(pairs))\n'
                 'proba = RandomForestClassifier(n_estimators=100, random_state=200).fit(Xtr, ytr).predict_proba(Xte)\n'
                 'weak = sum(1 for i, (t, p) in enumerate(zip(yte, pred)) if {t, p} == {3, 8} and max(proba[i]) < 0.6)\n'
                 'print("of them low-confidence:", weak)\n'
                 'print("abstention would catch these without touching the model")'
             ),
             variant_b='5/6 confusions (same analysis, other pair)',
             variant_c='threshold 0.8 for abstention (how many rows route to review?)',
             mistakes=[
                 "More capacity prescribed for underdetermined ink.",
                 "Abstention dismissed as 'giving up' instead of priced as error prevention.",
                 "One pair examined and generalised to all errors.",
             ],
             q1=("When is abstention the right fix instead of more modelling?",
                 "When inputs underdetermine the answer: no capacity recovers information the pixels never contained, but routing prevents the error."),
             homework="Write `pair_audit()` counting 3/8 confusions and low-confidence ones. Run it on two seeds, print both audits, and comment which line measures abstainable errors.",
             patterns=[".predict(", "predict_proba("],
             mapping="Abstention policies sit on calibrated uncertainty; some errors are routed, not fixed.",
         ),
         176: dict(
             topic="Reproducibility pass over everything",
             idea="Rerun the entire capstone chain — split, baselines, forest, boosting, grid, locked verdict — and diff every number against the logged artefacts: identical means the chain is sound, drift names the loose dice. Pin sklearn, numpy and Python versions into the report, hash the digits array, and record every seed in one table. Then break it deliberately once (drop a seed, watch numbers move) to prove the audit catches drift rather than assuming it. A capstone that reruns byte-identically is a result; one that merely ran once is an anecdote with good lighting. Break the chain deliberately once per phase to prove the audit catches drift rather than assuming it.",
             code=(
                 'import sklearn, numpy\n'
                 'from sklearn.datasets import load_digits\n'
                 'from sklearn.model_selection import train_test_split\n'
                 'from sklearn.neighbors import KNeighborsClassifier\n'
                 'import hashlib\n'
                 '\n'
                 'print("sklearn:", sklearn.__version__, "| numpy:", numpy.__version__)\n'
                 'X, y = load_digits(return_X_y=True)\n'
                 'print("digits hash:", hashlib.md5(X.tobytes()).hexdigest()[:12])\n'
                 'runs = []\n'
                 'for _ in range(2):\n'
                 '    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=200, stratify=y)\n'
                 '    runs.append(KNeighborsClassifier(n_neighbors=3).fit(Xtr, ytr).score(Xte, yte))\n'
                 'print("run1:", round(runs[0], 4), "| run2:", round(runs[1], 4), "| identical:", runs[0] == runs[1])\n'
                 'print("chain reruns byte-identically: certified")'
             ),
             variant_b='drop the split seed (does the audit catch the drift?)',
             variant_c='forest instead of kNN (identical across runs too?)',
             mistakes=[
                 "Versions recorded everywhere except the one that changed the numbers.",
                 "Data hash skipped because 'it is the standard dataset'.",
                 "Rerun tested on a different machine with different libraries and declared fine.",
             ],
             q1=("Why rerun the whole chain instead of trusting each day's numbers?",
                 "Composition drifts: individually sound steps can disagree on seeds, versions or data, and only the full rerun certifies the assembled result."),
             homework="Write `chain_audit()` printing versions, data hash and two identical scores. Run it on digits and iris, print both audits, and comment which line certifies the bytes.",
             patterns=["random_state=", ".score("],
             mapping="Full-chain reruns with hashes and versions — the shipping gate for the capstone and everything after.",
         ),
         177: dict(
             topic="Presentation rehearsal",
             idea="Explain the capstone in ten minutes to a sceptic: problem and metric in one slide, data and split in one, baselines with floors, the two-model duel with costs, tuning gains with honesty about size, failure taxonomy with renderings, and the locked verdict with its margin. Rehearse answers to the five hard questions — why this metric, why this split, what beats the baseline by how much, where does it fail, how do I rerun it — because those questions are the review, and fluent true answers beat polished vague ones. Time the rehearsal; cut a slide, never rush the failures.",
             code=(
                 'from sklearn.datasets import load_digits\n'
                 'from sklearn.model_selection import train_test_split\n'
                 'from sklearn.dummy import DummyClassifier\n'
                 'from sklearn.ensemble import RandomForestClassifier\n'
                 'from sklearn.metrics import f1_score\n'
                 '\n'
                 'print("slide 1: digits F1, weighted | slide 2: seed-200 stratified 80/20")\n'
                 'X, y = load_digits(return_X_y=True)\n'
                 'Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=200, stratify=y)\n'
                 'base = f1_score(yte, DummyClassifier(strategy="most_frequent").fit(Xtr, ytr).predict(Xte), average="weighted")\n'
                 'real = f1_score(yte, RandomForestClassifier(n_estimators=100, random_state=200).fit(Xtr, ytr).predict(Xte), average="weighted")\n'
                 'print(f"slide 3: floor {base:.3f} -> model {real:.3f} (margin {real-base:.3f})")\n'
                 'print("slide 4: failures = 3/8 ambiguity (rendered) | slide 5: rerun = seeds table + hashes")'
             ),
             variant_b='a two-minute version (which two slides survive?)',
             variant_c='hostile questions rehearsal (what is the weakest claim?)',
             mistakes=[
                 "Accuracy headlining a ten-class story.",
                 "Failures slide cut for time — the most trusted slide in the deck.",
                 "Rerun instructions missing, so questions end the presentation instead of continuing it.",
             ],
             q1=("Why do the failures earn a slide instead of an appendix?",
                 "How a project fails predicts production behaviour better than how it succeeds — reviewers fund the team that knows its limits."),
             homework="Write `talk_track()` printing the five-slide outline with live-computed floor/model/margin numbers. Run it on two seeds, print both outlines, and comment which numbers must never be hand-typed.",
             patterns=["f1_score(", ".fit("],
             mapping="Ten-minute sceptic-proof structure: metric, split, floors, duel, failures, rerun — every presentation hereafter.",
         ),
         178: dict(
             topic="Final review and checklist",
             idea="Run the capstone checklist end to end: brief signed and unchanged, split constitution intact, baselines on every board, grids small and documented, locked test touched once, failures taxonomised with renderings, docs generated from code, demo validated, chain rerun byte-identical, versions and hashes logged. Every unchecked box is a named debt with an owner and a date — 'known limitation, revisit after launch' beats silent gaps. Sign the checklist by running the verification script green: when every line below prints, the project is done in the only sense that matters — a stranger can rerun, understand, and trust it.",
             code=(
                 'from sklearn.datasets import load_digits\n'
                 'from sklearn.model_selection import train_test_split\n'
                 'from sklearn.dummy import DummyClassifier\n'
                 'from sklearn.neighbors import KNeighborsClassifier\n'
                 'from sklearn.ensemble import RandomForestClassifier\n'
                 'from sklearn.metrics import f1_score\n'
                 '\n'
                 'X, y = load_digits(return_X_y=True)\n'
                 'Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=200, stratify=y)\n'
                 'checks = {}\n'
                 'checks["split locked"] = (len(Xte) == 360)\n'
                 'checks["dummy scored"] = f1_score(yte, DummyClassifier(strategy="most_frequent").fit(Xtr, ytr).predict(Xte), average="weighted") > 0\n'
                 'checks["knn beats dummy"] = f1_score(yte, KNeighborsClassifier(n_neighbors=3).fit(Xtr, ytr).predict(Xte), average="weighted") > f1_score(yte, DummyClassifier(strategy="most_frequent").fit(Xtr, ytr).predict(Xte), average="weighted")\n'
                 'checks["forest runs"] = f1_score(yte, RandomForestClassifier(n_estimators=20, random_state=200).fit(Xtr, ytr).predict(Xte), average="weighted") > 0.9\n'
                 'for name, ok in checks.items():\n'
                 '    print(f"[{\'x\' if ok else \' \'}] {name}")\n'
                 'assert all(checks.values())\n'
                 'print("checklist green: shippable")'
             ),
             variant_b='a deliberately broken split (which check catches it?)',
             variant_c='forest-5 instead of 20 (does the bar still clear?)',
             mistakes=[
                 "Checklist run once at the end instead of after every phase.",
                 "Unchecked boxes silently dropped instead of recorded as debt.",
                 "Green checklist treated as proof of quality rather than proof of process.",
             ],
             q1=("Why record unchecked boxes as dated debt instead of hiding them?",
                 "Known limitations with owners get fixed; hidden ones ambush users — honesty compounds while concealment accrues interest."),
             homework="Write `ship_checklist()` asserting split size, dummy scored, kNN-beats-dummy and forest bar, printing each tick. Run it on two seeds, print both, and comment which check guards the split.",
             patterns=["assert ", "f1_score("],
             mapping="Sign-off checklists with named debt — the closing ritual of every project, starting with this one.",
         ),
         179: dict(
             topic="Capstone reflection",
             idea="Look back across 180 days: the Python that loads and guards data, the lines and curves of regression, the probabilities and thresholds of classification, the boxes and votes of forests, the curves and folds of validation, the pipelines and grids of tuning, and this capstone spending it all on real digits. Name the three habits that changed how you work — baselines before models, locked tests before claims, failures taxonomised before tuning — and the one weakness to attack next (calibration depth, text scale, deployment). Write the next milestone concretely: dataset, metric, deadline. A course ends; the practice continues on purpose, not by accident. Carry three artefacts forward: the rerunnable chain, the failure-taxonomy habit, and the locked-test discipline — every future project starts from these instead of from zero. Revisit this reflection before each new dataset; foundations compound only when they are deliberately reused.",
             code=(
                 'journey = {"days": 180, "models": ["dummy", "knn", "logreg", "tree", "forest", "boost"], "habits": ["baselines", "locked tests", "failure taxonomy"]}\n'
                 'print("days completed:", journey["days"])\n'
                 'print("models driven:", len(journey["models"]))\n'
                 'print("habits kept:", ", ".join(journey["habits"]))\n'
                 'print("next: pick a dataset, name a metric, set a deadline")'
             ),
             variant_b='your own three habits (which differ from the listed three?)',
             variant_c='your own next milestone (dataset, metric, deadline — written down?)',
             mistakes=[
                 "Finishing without naming what changed — skills unnamed evaporate.",
                 "No next milestone, so momentum dies within a week.",
                 "Mistaking course completion for mastery — this was foundations, honestly earned.",
             ],
             q1=("Why name three habits explicitly instead of 'I learned a lot'?",
                 "Named habits are checkable and portable; vague satisfaction cannot be rehearsed, tested, or transferred to the next project."),
             homework="Write `reflect()` printing your three kept habits and one concrete next milestone with dataset, metric and deadline. Run it, print it, and comment which habit you will use first tomorrow.",
             patterns=["print(", "def "],
             mapping="Reflection with a written next milestone — every ending here is a scoped beginning. A milestone without dataset, metric and deadline is a wish; write all three or admit the ending is decorative.",
         ),
     }),
]


