"""Data Science topics — Phase 4 (Predictive Modelling)."""

PHASE_4: dict[str, dict] = {}

def _t(topic, theory, code, questions, answers, homework):
    PHASE_4[topic] = {
        "theory": theory, "code": code,
        "questions": questions, "answers": answers, "homework": homework,
    }

_t("Features and labels",
    "**What it is**\nFeatures (X) are the inputs a model learns from; the label (y) is the answer to predict. Tabular ML = matrix X (n_samples × n_features) and vector y.\n\n"
    "**Why it matters**\nFeature quality caps model quality — garbage features, garbage predictions, no algorithm escapes it.\n\n"
    "**Watch out**\nLabel leakage: any feature that wouldn't exist at prediction time (e.g. 'final_grade' when predicting pass/fail) inflates results fraudulently.",
    "X = [[2, 55], [4, 70], [6, 85]]   # [study_hours, mock_score] -> features\ny = ['fail', 'pass', 'pass']       # target -> label\nfeature_names = ['hours', 'mock_score']\nfor row, label in zip(X, y):\n    print(dict(zip(feature_names, row)), '->', label)\nprint('leakage check: neither feature IS the answer -> clean')",
    ["Define feature vs label with an example", "What is label leakage?", "Shapes of X and y for 100 rows, 3 features?"],
    ["Inputs the model uses to predict; the label is the target answer", "Including information unavailable at prediction time that encodes the answer", "X: 100×3 matrix; y: length-100 vector"],
    "Build X and y for a tiny prediction problem of your own (4 rows), print each sample as a dict, and comment why no feature leaks.")

_t("Train-test split",
    "**What it is**\nHold out part of the data (typically 20%) before training. Train on the rest; score on the untouched test set to estimate real-world performance.\n\n"
    "**Why it matters**\nScoring on training data measures memorisation, not learning. The test set is your only honest preview.\n\n"
    "**Watch out**\nSplit BEFORE fitting anything (including scalers!) and set random_state for reproducibility.",
    "import random\nrandom.seed(42)\ndata = list(zip([[1], [2], [3], [4], [5], [6], [7], [8]], ['a','b','c','d','e','f','g','h']))\nrandom.shuffle(data)\ncut = int(len(data) * 0.75)\ntrain, test = data[:cut], data[cut:]\nprint('train size:', len(train), '| test size:', len(test))\ntrain_keys = [tuple(x) for x, _ in train]\ntest_keys = [tuple(x) for x, _ in test]\nassert not set(train_keys) & set(test_keys)\nprint('disjoint split verified')",
    ["Why must the test set stay unseen until final scoring?", "Typical split ratio?", "Why shuffle before splitting?"],
    ["Any peeking turns it into a second training set — estimates become optimistic lies", "80/20 or 75/25 train/test", "Ordered data would put similar rows on one side, biasing both sets"],
    "Shuffle-and-split eight samples 75/25 in pure Python, print both sets, assert disjointness, and explain what leakage would look like.")

_t("Linear regression",
    "**What it is**\nFits y = slope·x + intercept by least squares: choose the line minimising squared errors. Slope = change in y per unit x.\n\n"
    "**Why it matters**\nThe workhorse baseline: interpretable, fast, and the reference every fancier model must beat.\n\n"
    "**Watch out**\nIt only captures linear relations and is sensitive to outliers — one wild point drags the whole line.",
    "hours = [1, 2, 3, 4]\nscores = [52, 58, 65, 72]\nn = len(hours)\nmx, my = sum(hours)/n, sum(scores)/n\nslope = sum((x-mx)*(y-my) for x, y in zip(hours, scores)) / sum((x-mx)**2 for x in hours)\nintercept = my - slope * mx\npred = lambda h: slope * h + intercept\nerrors = [(y - pred(x))**2 for x, y in zip(hours, scores)]\nprint(f'score = {slope:.2f}*hours + {intercept:.2f}')\nprint('MSE:', round(sum(errors)/n, 2), '| predict 5h:', round(pred(5), 1))",
    ["Interpret slope=7.2 in a hours→score model", "What does least squares minimise?", "Is the intercept always meaningful?"],
    ["Each extra study hour associates with +7.2 points on average", "The sum of squared prediction errors", "No — zero may lie outside observed data; extrapolation warnings apply"],
    "Fit a line by hand on five points, print slope/intercept/MSE, predict one new value, and state in words what your slope means.")

_t("Logistic regression",
    "**What it is**\nDespite the name, a CLASSIFIER: it outputs P(y=1) by squashing a linear score through the sigmoid σ(z)=1/(1+e^(−z)), then thresholds (default 0.5).\n\n"
    "**Why it matters**\nThe default first classifier: calibrated probabilities, interpretable coefficients, cheap to train.\n\n"
    "**Watch out**\nThe 0.5 threshold is a business decision — move it toward recall or precision depending on error costs.",
    "import math\nw, b = 0.8, -3.0   # learned coefficients\nsigmoid = lambda z: 1 / (1 + math.exp(-z))\nfor hours in [1, 3, 5, 7]:\n    z = w * hours + b\n    p = sigmoid(z)\n    label = 'pass' if p >= 0.5 else 'fail'\n    print(f'{hours}h -> z={z:.1f}, P(pass)={p:.2f}, predicted: {label}')",
    ["Why 'regression' in the name if it classifies?", "What does the sigmoid output?", "When raise the threshold above 0.5?"],
    ["It regresses the log-odds of the outcome — the name is historical", "A probability between 0 and 1", "When false positives are costlier than false negatives"],
    "Implement sigmoid scoring for five inputs with fixed weights, print probability AND thresholded class for each, then re-threshold at 0.7 and compare.")

_t("K-nearest neighbours",
    "**What it is**\nKNN stores the training set; to predict, find the k closest points (Euclidean distance) and take their majority vote (classification) or average (regression). No real 'training'.\n\n"
    "**Why it matters**\nThe most intuitive learner and a strong sanity baseline for small data.\n\n"
    "**Watch out**\nScale your features (big ranges dominate distance); large k smooths decisions, k=1 memorises noise.",
    "train = [(2, 'fail'), (4, 'pass'), (5, 'pass'), (8, 'pass'), (1, 'fail')]\ndef knn(point, k):\n    nearest = sorted(train, key=lambda row: abs(row[0] - point))[:k]\n    votes = [label for _, label in nearest]\n    return max(set(votes), key=votes.count), nearest\nresult, used = knn(3, 3)\nprint('predict 3h:', result, '| neighbours used:', used)",
    ["What does KNN do at 'training' time?", "Why does feature scaling matter here?", "k=1 vs k=n — behaviour?"],
    ["Nothing but store data — all work happens at prediction", "Distances are dominated by the largest-range feature otherwise", "k=1 overfits noise; k=n predicts the global majority everywhere"],
    "Implement KNN with adjustable k on six points, predict two queries with k=1 and k=3, print all four outcomes, and note where they disagree.")

_t("Decision trees",
    "**What it is**\nA tree splits data by asking feature questions ('hours > 3?'), each branch narrowing rows until leaves vote/average. Splits chosen to maximise purity (e.g. Gini drop).\n\n"
    "**Why it matters**\nFully interpretable — you can read the model as rules — and handles mixed feature types natively.\n\n"
    "**Watch out**\nUnlimited depth memorises training data; cap max_depth or prune.",
    "tree = {'question': 'hours > 3?',\n        'yes': {'question': 'mock > 65?', 'yes': 'pass', 'no': 'review'},\n        'no': 'fail'}\ndef predict(node, hours, mock):\n    while isinstance(node, dict):\n        go = 'yes' if (hours > 3 if node['question'] == 'hours > 3?' else mock > 65) else 'no'\n        node = node[go]\n    return node\nprint(predict(tree, 5, 70), predict(tree, 2, 90), predict(tree, 4, 50))",
    ["How does a tree choose split questions?", "Why do deep trees overfit?", "Two selling points of trees?"],
    ["By maximising child-node purity (e.g. Gini impurity decrease)", "Deep paths isolate individual training rows instead of patterns", "Human-readable rules; no scaling needed"],
    "Build a two-level nested-dict tree for your own rule set, write a predict-walker, run three cases, and print which leaf each reaches.")

_t("Random forests",
    "**What it is**\nAn ensemble of many decision trees, each trained on a bootstrap sample with random feature subsets; predictions are majority-averaged (bagging).\n\n"
    "**Why it matters**\nIndividual trees overfit; averaging decorrelated trees cancels their noise — usually the strongest tabular baseline.\n\n"
    "**Watch out**\nLess interpretable than one tree (mitigate with feature importances) and slower to predict.",
    "trees = [\n    lambda h, m: 'pass' if h > 3 else 'fail',\n    lambda h, m: 'pass' if m > 60 else 'fail',\n    lambda h, m: 'pass' if h + m/10 > 9 else 'fail',\n]\ndef forest_predict(h, m):\n    votes = [t(h, m) for t in trees]\n    return max(set(votes), key=votes.count), votes\nprint(forest_predict(4, 55))\nprint(forest_predict(2, 90))",
    ["Name the two randomness sources in a forest", "Why does averaging help?", "How to regain interpretability?"],
    ["Bootstrap-sampled rows and random feature subsets per split", "Decorrelated errors cancel; variance shrinks without bias growth", "Inspect feature importances or single trees as approximations"],
    "Hand-build three diverse rule-trees, implement majority voting, test four cases, and print each case's individual votes plus the verdict.")

_t("Feature scaling",
    "**What it is**\nStandardising features to comparable ranges: standardisation (mean 0, sd 1) or min-max (0–1). Needed by distance- and gradient-based models (KNN, regression, neural nets); trees don't care.\n\n"
    "**Why it matters**\nUnscaled, income (100000s) drowns age (10s) in any distance computation regardless of true importance.\n\n"
    "**Watch out**\nFit the scaler on TRAINING data only, then apply the same transform to test data — fitting on everything leaks.",
    "def standardise(values):\n    mean = sum(values) / len(values)\n    sd = (sum((v - mean)**2 for v in values) / len(values)) ** 0.5\n    return [(v - mean) / sd for v in values]\n\nincome = [30000, 45000, 60000]\nage =    [22, 35, 48]\ninc_z, age_z = standardise(income), standardise(age)\nprint('raw ranges dominate:', max(income) - min(income), 'vs', max(age) - min(age))\nprint('after scaling both vary around zero:', [round(z, 2) for z in inc_z], [round(z, 2) for z in age_z])",
    ["Which model families need scaling?", "Standardisation vs min-max?", "Where must the scaler be fitted?"],
    ["Distance-based (KNN) and gradient-based (linear/logistic, NN); not trees", "Standardise → z-scores; min-max → squeeze into [0,1]", "On training data only; transform test with those saved parameters"],
    "Write standardise(), scale two wildly different-range features, print raw vs scaled spreads, and comment which algorithms would care.")

_t("Pipelines",
    "**What it is**\nA pipeline chains preprocessing + model into one object: fit/transform steps run automatically in order, so test data flows through identical transforms.\n\n"
    "**Why it matters**\nPipelines eliminate the #1 leakage bug (fitting transforms on full data) and make cross-validation honest by construction.\n\n"
    "**Watch out**\nEverything inside the pipeline must be deterministic or seeded, or CV scores wobble.",
    "class Pipeline:\n    def __init__(self, *steps):\n        self.steps = steps\n    def _flow(self, X):\n        for transform, _ in self.steps[:-1]:\n            X = transform(X)\n        return X\n    def fit(self, X):\n        self._flow(X)\n        self.model = self.steps[-1][1]\n        return self\n    def predict(self, X):\n        return self.model(self._flow(X))\n\nscale = lambda rows: [[v / 10 for v in r] for r in rows]\nmodel = lambda rows: ['pass' if r[0] >= 0.5 else 'fail' for r in rows]\npipe = Pipeline(('scale', scale), ('model', model))\nprint(pipe.predict([[7, 90], [2, 40]]))",
    ["What problem do pipelines solve beyond convenience?", "Order of operations inside a pipeline?", "Pipeline + CV combination benefit?"],
    ["Guaranteeing test data receives train-fitted transforms — no leakage", "Transform steps sequentially, fit the estimator last", "CV refits the WHOLE pipeline per fold, keeping every fold leak-free"],
    "Build a mini Pipeline class with two transforms and a rule-model, run two batches through it, and print how transforms chained.")

_t("Cross-validation",
    "**What it is**\nk-fold CV splits data into k parts, trains k times (each fold held out once), and averages scores — every row gets tested exactly once.\n\n"
    "**Why it matters**\nOne train-test split can land lucky or unlucky; CV averages away that luck for reliable model comparison.\n\n"
    "**Watch out**\nCostly (k× training time); use stratified folds for imbalanced classes.",
    "fold_scores = [[0.82, 0.79], [0.85, 0.77], [0.80, 0.81], [0.83, 0.84], [0.81, 0.78]]\nfold_means = [sum(pair)/len(pair) for pair in fold_scores]\ncv_mean = sum(fold_means) / len(fold_means)\nspread = max(fold_means) - min(fold_means)\nprint('fold means:', [round(m, 3) for m in fold_means])\nprint(f'CV score: {cv_mean:.3f} ± spread {spread:.3f}')",
    ["Describe 5-fold CV mechanics", "Why prefer CV to a single split?", "What does high fold-to-fold spread warn about?"],
    ["Split into 5 folds; train on 4, test on the remaining one; rotate 5×; average", "Single splits have high variance; CV averages over every row being tested", "Unstable model or heterogeneous data — investigate before trusting the mean"],
    "Compute fold means, overall CV score and spread from five fake fold pairs, print all, and write a verdict sentence using both numbers.")

_t("Hyperparameters",
    "**What it is**\nHyperparameters are settings chosen BEFORE training (k in KNN, max_depth, learning rate) — unlike parameters, which training learns. Tuning searches hyperparameter space, typically via grid search + CV.\n\n"
    "**Why it matters**\nDefault settings leave performance on the table; systematic search beats guesswork.\n\n"
    "**Watch out**\nTune on the TEST set and you've leaked — search via CV, touch test once at the very end.",
    "import itertools\nparam_grid = {'k': [1, 3, 5], 'metric': ['euclidean', 'manhattan']}\ncombos = list(itertools.product(param_grid['k'], param_grid['metric']))\ncv_scores = {combo: round(0.70 + 0.02*combo[0] - 0.01*(combo[1]=='manhattan'), 3) for combo in combos}\nbest = max(cv_scores, key=cv_scores.get)\nfor combo, score in sorted(cv_scores.items()):\n    print(combo, '->', score)\nprint('best:', best, cv_scores[best])",
    ["Parameter vs hyperparameter?", "What does grid search do?", "Why never tune on test data?"],
    ["Parameters are learned from data during training; hyperparameters are pre-set by the practitioner", "Tries every combination in the grid, scoring each with CV", "Test performance would feed back into choices — the estimate becomes optimistically biased"],
    "Define a 2×3 grid for any model, enumerate combos with itertools, assign fake CV scores, and print the winner plus the runner-up.")

_t("Overfitting",
    "**What it is**\nOverfitting = memorising training noise: train score keeps climbing while test score falls. Underfitting = too simple to even learn the training pattern.\n\n"
    "**Why it matters**\nThe central failure mode of ML. A model is only useful if train↔test gap stays small.\n\n"
    "**Watch out**\nDiagnose by comparing curves: big train-test gap → overfit; both low → underfit.",
    "depths = [1, 2, 3, 5, 8]\ntrain_acc = [0.62, 0.74, 0.85, 0.95, 0.99]\ntest_acc  = [0.60, 0.72, 0.80, 0.76, 0.68]\nbest_i = max(range(len(depths)), key=lambda i: test_acc[i])\nfor i, d in enumerate(depths):\n    gap = train_acc[i] - test_acc[i]\n    flag = ' <-- sweet spot' if i == best_i else (' overfitting!' if gap > 0.12 else '')\n    print(f'depth {d}: train {train_acc[i]} test {test_acc[i]} gap {gap:+.2f}{flag}')",
    ["Define overfitting via the train-test gap", "Three remedies for overfitting?", "Symptom of underfitting?"],
    ["Training accuracy rises while test accuracy falls — the model memorised noise", "More data, simpler model/regularisation, early stopping or pruning", "Both train AND test scores stay low"],
    "Print a depth-vs-accuracy table showing the overfitting turn, mark the best test depth, and write one sentence diagnosing each region.")

_t("Model comparison",
    "**What it is**\nComparing candidates fairly: same folds, same metrics, same data — score each with CV and pick by mean (± spread), not a single lucky number.\n\n"
    "**Why it matters**\nDifferent models win on different problems; only disciplined comparison reveals yours.\n\n"
    "**Watch out**\nCompare on the SAME folds (paired comparison) or differences may be sampling noise.",
    "models = {\n    'baseline-mean':      [0.61, 0.59, 0.63, 0.60],\n    'logistic-regression':[0.78, 0.74, 0.80, 0.76],\n    'random-forest':      [0.82, 0.77, 0.84, 0.79],\n}\nsummary = {}\nfor name, folds in models.items():\n    mean = sum(folds)/len(folds)\n    spread = max(folds) - min(folds)\n    summary[name] = (round(mean, 3), round(spread, 3))\nwinner = max(summary, key=lambda m: summary[m][0])\nfor name, (mean, spread) in summary.items():\n    tag = '<-- winner' if name == winner else ''\n    print(f'{name:>22}: {mean} ±{spread} {tag}')",
    ["Fair comparison requires holding what constant?", "Why report spread beside the mean?", "Should the simplest model be a candidate?"],
    ["Identical data, folds, and evaluation metric across all candidates", "A 0.80±0.01 beats a noisy 0.81±0.08 despite the lower point estimate", "Always — a dumb baseline calibrates whether complexity pays"],
    "Score three models on four shared fake folds, compute mean±spread for each, crown a winner, and check it beat the naive baseline.")

_t("Model explainability",
    "**What it is**\nExplaining WHY a model predicts: global views (feature importances, coefficient signs/sizes) and local ones (which features pushed THIS prediction up/down).\n\n"
    "**Why it matters**\nStakeholders trust and correctly use models they understand; explanations also expose spurious shortcuts.\n\n"
    "**Watch out**\nImportance ≠ causation, and correlated features split importance confusingly.",
    "coefficients = {'hours_studied': 0.42, 'absences': -0.30, 'mock_score': 0.15}\nprediction_input = {'hours_studied': 5, 'absences': 2, 'mock_score': 70}\ncontributions = {f: round(coefficients[f] * prediction_input[f], 2) for f in coefficients}\nfor f, c in sorted(contributions.items(), key=lambda kv: -abs(kv[1])):\n    direction = 'pushes UP' if c > 0 else 'pushes DOWN'\n    print(f'{f}: {c:+.2f} ({direction})')\nprint('top driver:', max(contributions, key=lambda f: abs(contributions[f])))",
    ["Global vs local explanation?", "Negative coefficient meaning?", "Two caveats of feature importance?"],
    ["Global describes the model overall; local justifies one prediction", "Increasing that feature lowers the predicted outcome", "Not causal; correlated features share/split credit"],
    "Given coefficients and one input, compute per-feature contributions, sort by absolute impact, print each with direction, and name the top driver.")

_t("Prediction project",
    "**What it is**\nPhase capstone: end-to-end modelling — frame question, engineer features, split, baseline, tune one competitor, evaluate honestly, explain top drivers.\n\n"
    "**Why it matters**\nIntegrates every phase skill into one defensible artifact — exactly the shape of junior analyst work.\n\n"
    "**Watch out**\nLock the test set away until every decision is made; report its score ONCE.",
    "project_log = [\n    ('frame',   'predict pass/fail from study habits'),\n    ('features','hours, consistency, mock_score (leak-checked)'),\n    ('split',   '75/25 shuffled, seed fixed'),\n    ('baseline','majority class -> 0.58 CV'),\n    ('model',   'logistic regression, tuned -> 0.81 CV'),\n    ('explain', 'top driver: hours_studied (+)'),\n]\nfor stage, detail in project_log:\n    print(f'{stage:>9} | {detail}')\nbase = float(project_log[3][1].split('->')[1].strip()[:4])\nmodel = float(project_log[4][1].split('->')[1].strip()[:4])\nassert model > base\nprint('model beats baseline: verified')",
    ["Which stage must come last and happen once?", "Why record a naive baseline?", "What makes the project 'defensible'?"],
    ["Final test-set evaluation — after all tuning decisions", "Complexity must earn its keep against something dumb", "Leak-free features, tuned via CV, explained drivers, honest single test score"],
    "Assemble a six-stage project-log like the example for your own problem, print it, and programmatically verify the model stage beats the baseline stage.")
