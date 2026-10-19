"""Deep Learning phase 6, days 150-164: evaluation, debugging and deployment.

Every example stays stdlib-only, offline and deterministic: metrics are counters
over fixed predictions, artefacts are dictionaries, and nothing touches the
network, the clock or the filesystem. The phase is about evidence, so each
lesson ends with a number that a release decision could actually use.
"""

PHASE = (
    "Evaluation, Debugging and Deployment",
    "Turn a trained model into a measured, monitored artefact that can be released, rolled back and trusted in production.",
    {
        150: dict(
            topic="Orientation: shipping a model",
            idea=(
                "Shipping a model is a decision about evidence, not a celebration of a training run. A model that "
                "scores well on one held-out file can still be too slow, too large, or too sensitive to be useful, "
                "so the orientation for this phase is to treat deployment as a sequence of explicit gates. The "
                "first gate is offline quality: a metric computed on data the model never trained on, compared "
                "against a baseline you would otherwise ship. The second is robustness: behaviour on empty inputs, "
                "unusual values and the rare classes that aggregate accuracy hides. The third is operational: "
                "latency, memory, artifact size and a rollback path when the first two turn out to be optimistic. "
                "Writing these gates as a dictionary of named checks makes the release argument inspectable, and "
                "the same dictionary becomes the checklist at the end of the phase. Today you evaluate a fixed set "
                "of predictions against three such gates and print pass or fail for each. The numbers are small on "
                "purpose, because the habit matters more than the score: no single number should authorise a "
                "release on its own. A gate that nobody can rerun is an anecdote, so every check below is a pure "
                "function over fixed inputs."
            ),
            code=(
                'def accuracy(preds, labels):\n'
                '    correct = sum(1 for p, y in zip(preds, labels) if p == y)\n'
                '    return round(correct / len(labels), 3)\n'
                '\n'
                'preds = [1, 1, 0, 1, 0, 1, 0, 0, 1, 1]\n'
                'labels = [1, 0, 0, 1, 0, 1, 1, 0, 1, 0]\n'
                'acc = accuracy(preds, labels)\n'
                'gates = {"quality": acc >= 0.7, "robustness": True, "operational": True}\n'
                'print("accuracy:", acc)\n'
                'for name in sorted(gates):\n'
                '    print(name, "->", "pass" if gates[name] else "fail")\n'
                '\n'
                'assert acc == 0.7\n'
                'print("a model ships only when every gate passes")'
            ),
            variant_b="add a p95 latency gate and require two consecutive passes before deployment",
            variant_c="flip one prediction and show which single gate changes while accuracy barely moves",
            mistakes=[
                "Treating one held-out accuracy number as sufficient evidence for a release.",
                "Evaluating on data that was used for tuning, so the gate measures memory rather than generalisation.",
                "Forgetting the rollback path until the first bad deployment makes it urgent.",
            ],
            q1=(
                "What are the three gates a model must pass before deployment?",
                "Offline quality on held-out data, robustness on edge cases and rare classes, and operational limits such as latency, memory and size.",
            ),
            homework=(
                "Write `release_gates(preds, labels)` returning a dictionary with accuracy and a pass flag per "
                "gate. Evaluate it on the fixed predictions, print each gate, and comment which line decides that a "
                "failed gate blocks release."
            ),
            patterns=["def ", "print(", "if "],
            mapping=(
                "Model registries and CI pipelines encode the same idea: promotion is gated by recorded checks, "
                "not by a person remembering the last notebook result."
            ),
        ),
        151: dict(
            topic="Metrics beyond accuracy",
            idea=(
                "Accuracy answers one question — how often the top prediction was right — and that question is "
                "often the wrong one. When one class dominates, a model that always predicts the majority can look "
                "excellent while being useless: on a fraud feed where one percent of rows are fraud, ninety-nine "
                "percent accuracy is what a constant predictor already achieves. Metrics beyond accuracy make the "
                "cost of that failure visible. Balanced accuracy averages per-class recall, so ignoring a rare "
                "class cannot be hidden by the majority. Macro averaging gives each class equal weight regardless "
                "of size; micro averaging lets frequent classes dominate, which is closer to accuracy. Per-class "
                "recall tells you which labels the model abandons, and a majority-class baseline makes every number "
                "interpretable by comparison. The lesson is to report a small panel, not a single scalar: overall "
                "accuracy beside balanced accuracy and per-class recall, with the baseline stated. Today you compute "
                "those three numbers from fixed predictions on an imbalanced toy set and confirm that a model with "
                "high accuracy has collapsed on the positive class. If a dashboard shows only accuracy, assume it "
                "is hiding something and ask for the confusion matrix. A panel of two or three metrics is cheap to compute "
                "and much harder to game unintentionally."
            ),
            code=(
                'def metric_panel(preds, labels):\n'
                '    n = len(labels)\n'
                '    tp = sum(1 for p, y in zip(preds, labels) if p == 1 and y == 1)\n'
                '    tn = sum(1 for p, y in zip(preds, labels) if p == 0 and y == 0)\n'
                '    fp = sum(1 for p, y in zip(preds, labels) if p == 1 and y == 0)\n'
                '    fn = sum(1 for p, y in zip(preds, labels) if p == 0 and y == 1)\n'
                '    accuracy = (tp + tn) / n\n'
                '    recall_pos = tp / (tp + fn) if tp + fn else 0.0\n'
                '    recall_neg = tn / (tn + fp) if tn + fp else 0.0\n'
                '    balanced = (recall_pos + recall_neg) / 2\n'
                '    return round(accuracy, 3), round(balanced, 3), round(recall_pos, 3)\n'
                '\n'
                'labels = [0] * 10 + [1] * 2\n'
                'preds = [0] * 12\n'
                'acc, balanced, recall = metric_panel(preds, labels)\n'
                'print("accuracy:", acc)\n'
                'print("balanced accuracy:", balanced)\n'
                'print("positive recall:", recall)\n'
                '\n'
                'assert acc == 0.833 and balanced == 0.5 and recall == 0.0\n'
                'print("high accuracy can hide a collapsed minority class")'
            ),
            variant_b="reduce the positive class to one example and show balanced accuracy collapse",
            variant_c="compare macro and micro recall on the same fixed predictions",
            mistakes=[
                "Reporting accuracy alone on a dataset where one class dominates the counts.",
                "Averaging per-class scores without checking that every class has enough examples.",
                "Forgetting the majority-class baseline, which makes a weak model look strong.",
            ],
            q1=(
                "Why can accuracy be misleading on an imbalanced dataset?",
                "A model that always predicts the majority class can score high accuracy while missing every minority case, so per-class and balanced metrics are needed.",
            ),
            homework=(
                "Write `metric_panel(preds, labels)` that returns accuracy, balanced accuracy and positive-class "
                "recall. Run it on an imbalanced fixed list, print all three rounded to three places, and comment "
                "why the majority baseline makes the accuracy misleading."
            ),
            patterns=["def ", "print(", "round"],
            mapping=(
                "Monitoring dashboards usually carry a metric panel rather than one score; balanced and per-class "
                "recall are the fastest way to see a rare-class regression after a release."
            ),
        ),
        152: dict(
            topic="Confusion matrices",
            idea=(
                "A confusion matrix is the table every classification metric is derived from, and reading it "
                "directly is faster than trusting a summary. Rows are the true labels and columns are the "
                "predictions, so the diagonal counts correct decisions while the off-diagonal cells name the two "
                "ways the model can be wrong: false positives, where a negative is called positive, and false "
                "negatives, where a positive is missed. Those errors have different costs in different products, "
                "which is why the matrix is more informative than one accuracy number. The four counts also make "
                "the arithmetic of precision and recall obvious, and they expose class collapse immediately: if one "
                "column is empty, the model never predicts that label; if a row is empty, that class is absent from "
                "the evaluation set. Build the matrix with plain counters over paired lists rather than a library, "
                "because the indexing is the concept. Print it with labels on both axes and verify the cells sum to "
                "the number of examples, which catches misaligned or dropped rows. Today you construct a two-by-two "
                "matrix by hand from ten fixed predictions and read the counts aloud. Once this table is natural, "
                "every metric in the next lesson is a one-line ratio over four integers."
            ),
            code=(
                'def confusion(true, pred):\n'
                '    matrix = [[0, 0], [0, 0]]\n'
                '    for t, p in zip(true, pred):\n'
                '        matrix[t][p] += 1\n'
                '    return matrix\n'
                '\n'
                'true = [1, 0, 1, 1, 0, 0, 1, 0, 0, 1]\n'
                'pred = [1, 0, 1, 0, 0, 1, 1, 0, 1, 0]\n'
                'm = confusion(true, pred)\n'
                'print("rows=true, cols=pred")\n'
                'print("       0  1")\n'
                'for label in (0, 1):\n'
                '    print(label, m[label])\n'
                '\n'
                'assert sum(sum(row) for row in m) == len(true)\n'
                'assert m[1][1] == 3\n'
                'print("every error lands in exactly one cell")'
            ),
            variant_b="add a third class and print the three-by-three matrix",
            variant_c="swap true and predicted to see the matrix transpose and its errors change places",
            mistakes=[
                "Reading the matrix with rows as predictions and columns as truth, inverting every error interpretation.",
                "Losing examples to misaligned lists, so the cells sum to less than the dataset size.",
                "Treating all off-diagonal errors as equally costly when false positives and false negatives differ.",
            ],
            q1=(
                "What do the off-diagonal cells of a confusion matrix represent?",
                "False positives, where a negative is predicted positive, and false negatives, where a positive is predicted negative.",
            ),
            homework=(
                "Write `confusion(true, pred)` returning a two-by-two list of lists. Build it from ten fixed pairs, "
                "print it with row and column labels, and assert that the four cells sum to the number of examples."
            ),
            patterns=["def ", "print(", "assert"],
            mapping=(
                "Serving dashboards log the confusion matrix per release and per slice; it is the artefact that "
                "lets an on-call engineer see whether a regression is a miss problem or a false-alarm problem."
            ),
        ),
        153: dict(
            topic="Precision, recall and F1",
            idea=(
                "Precision, recall and F1 are three views of the same confusion matrix, and the useful skill is "
                "knowing which one a situation rewards. Precision asks, of everything the model flagged, how many "
                "were real; it falls when false positives pile up. Recall asks, of everything real, how many were "
                "found; it falls when positives are missed. They trade against each other through the decision "
                "threshold, so quoting one without the other is incomplete. F1 is their harmonic mean, which stays "
                "low unless both are decent and therefore summarises the trade-off in a single number — convenient "
                "for ranking, dangerous as a target, because it treats a miss and a false alarm as equally costly. "
                "The right habit is to compute all three, state the threshold, and choose the emphasis from the "
                "product: a screening test wants recall, a spam filter that deletes mail wants precision. Today you "
                "derive the three from a fixed set of predictions, print them rounded, and check the degenerate "
                "cases: no predicted positives makes precision undefined and should be reported as zero or "
                "explicitly skipped rather than crashing. Keep the denominators visible in the code, since most "
                "metric bugs are a wrong divisor rather than wrong arithmetic."
            ),
            code=(
                'def prf(tp, fp, fn):\n'
                '    precision = tp / (tp + fp) if tp + fp else 0.0\n'
                '    recall = tp / (tp + fn) if tp + fn else 0.0\n'
                '    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0\n'
                '    return round(precision, 3), round(recall, 3), round(f1, 3)\n'
                '\n'
                'true = [1, 0, 1, 1, 0, 0, 1, 0, 0, 1]\n'
                'pred = [1, 0, 1, 0, 0, 1, 1, 0, 1, 0]\n'
                'tp = sum(1 for t, p in zip(true, pred) if t == 1 and p == 1)\n'
                'fp = sum(1 for t, p in zip(true, pred) if t == 0 and p == 1)\n'
                'fn = sum(1 for t, p in zip(true, pred) if t == 1 and p == 0)\n'
                'precision, recall, f1 = prf(tp, fp, fn)\n'
                'print("tp, fp, fn:", tp, fp, fn)\n'
                'print("precision:", precision)\n'
                'print("recall:", recall)\n'
                'print("f1:", f1)\n'
                '\n'
                'assert (precision, recall, f1) == (0.6, 0.6, 0.6)\n'
                'assert prf(0, 3, 0) == (0.0, 0.0, 0.0)\n'
                'print("each metric isolates a different kind of mistake")'
            ),
            variant_b="raise the threshold so precision climbs while recall falls",
            variant_c="set predicted positives to zero and show the safe handling of an undefined precision",
            mistakes=[
                "Quoting precision without recall, which hides how many real positives the model misses.",
                "Crashing on a zero denominator instead of handling the undefined case explicitly.",
                "Optimising F1 when a miss and a false alarm have very different real-world costs.",
            ],
            q1=(
                "When would you prefer recall over precision?",
                "When missing a positive is more costly than a false alarm, such as screening or fraud review where recall should be high.",
            ),
            homework=(
                "Write `prf(tp, fp, fn)` that returns precision, recall and F1 with safe handling for a zero "
                "denominator. Compute the counts from fixed predictions, print all three, and comment which "
                "denominator drives recall."
            ),
            patterns=["def ", "print(", "if "],
            mapping=(
                "Alerting systems expose precision and recall at a chosen threshold; tuning that threshold is a "
                "product decision about the relative cost of misses and false alarms."
            ),
        ),
        154: dict(
            topic="Calibration",
            idea=(
                "Calibration asks a different question from discrimination: when the model says seventy percent, "
                "is it right about seventy percent of the time? A model can rank examples perfectly and still be "
                "badly calibrated, and ranking is what accuracy and AUC mostly measure. Calibration matters "
                "whenever the score drives a decision with a cost, such as a threshold, a price, or a human review "
                "queue, because an overconfident model hides its own uncertainty. The standard diagnostic groups "
                "predictions into confidence bins and compares mean confidence with observed accuracy in each bin. "
                "The gap, weighted by bin size, is expected calibration error. A reliability table exposes the "
                "shape of the failure: overconfidence at the high end, underconfidence in the middle, or a single "
                "bin doing all the damage. Temperature scaling and isotonic regression are the usual fixes, but "
                "neither is trustworthy before the table exists. Today you build the bins from fixed confidences "
                "and labels with plain counters, print each bin's mean confidence and accuracy, then compute "
                "expected calibration error. Notice how few examples are needed to make the estimate noisy, which "
                "is why production monitors use larger samples and report the bin counts beside the scores. Report those "
                "counts next to the error so a reader can judge how much of the gap is real."
            ),
            code=(
                'def reliability(confidences, labels):\n'
                '    buckets = {}\n'
                '    for c, y in zip(confidences, labels):\n'
                '        idx = min(int(c / 0.25), 3)\n'
                '        count, hits = buckets.get(idx, (0, 0))\n'
                '        buckets[idx] = (count + 1, hits + y)\n'
                '    rows = []\n'
                '    for idx in sorted(buckets):\n'
                '        count, hits = buckets[idx]\n'
                '        conf = sum(c for c, _ in zip(confidences, labels)\n'
                '                   if min(int(c / 0.25), 3) == idx) / count\n'
                '        rows.append((idx * 0.25, (idx + 1) * 0.25, count, conf, hits / count))\n'
                '    ece = sum(count / len(labels) * abs(acc - conf)\n'
                '              for _, _, count, conf, acc in rows)\n'
                '    return rows, ece\n'
                '\n'
                'confidences = [0.95, 0.85, 0.65, 0.55, 0.7, 0.3, 0.4, 0.6, 0.8, 0.9]\n'
                'labels = [1, 1, 1, 0, 0, 1, 0, 0, 1, 1]\n'
                'rows, ece = reliability(confidences, labels)\n'
                'for low, high, count, conf, acc in rows:\n'
                '    print(f"[{low:.2f},{high:.2f}) n={count} conf={conf:.3f} acc={acc:.3f}")\n'
                'print("expected calibration error:", round(ece, 3))\n'
                '\n'
                'assert round(ece, 3) == 0.23\n'
                'print("confidence is only useful when it matches observed frequency")'
            ),
            variant_b="shift every confidence up by 0.1 and watch calibration error grow",
            variant_c="use fewer examples per bin and show how noisy the reliability table becomes",
            mistakes=[
                "Confusing calibration with accuracy, so a well-ranking but overconfident score passes review.",
                "Using bins with too few examples and treating noisy gaps as real miscalibration.",
                "Fitting a calibration fix on the test set instead of a separate validation split.",
            ],
            q1=(
                "What does calibration measure that accuracy does not?",
                "Whether predicted confidence matches observed frequency, so a 0.7 score should be correct about seventy percent of the time.",
            ),
            homework=(
                "Write `reliability(confidences, labels)` returning per-bin rows and expected calibration error. "
                "Use fixed inputs, print each bin count, mean confidence and accuracy, and assert that the weighted "
                "error is below one."
            ),
            patterns=["def ", "for ", "print("],
            mapping=(
                "Risk scores and review queues need calibrated probabilities; monitoring the reliability table "
                "after deployment catches overconfidence that accuracy alone never shows."
            ),
        ),
        155: dict(
            topic="Error analysis",
            idea=(
                "Error analysis is the part of evaluation that produces the next experiment instead of another "
                "number. Aggregate metrics tell you that something is wrong; slicing the errors tells you what, "
                "where and for whom. The method is deliberately manual at first: collect the failures, read them, "
                "group them by a property you can act on — input length, class, source, language, time of day — and "
                "compute the error rate per group. A slice with few examples and a high rate is often more "
                "informative than a large slice that matches the average. This is also how you discover label "
                "noise, duplicated rows and leakage, because all three look like model errors until you inspect the "
                "examples. The discipline is to write down the slice definitions before looking at the results, so "
                "the analysis does not become a hunt for a flattering subgroup. Today you tabulate error rates "
                "across three fixed slices and identify the worst one. The output is not a score to report but a "
                "ranked list of hypotheses: the worst slice becomes a test, a data fix or a targeted augmentation. "
                "That conversion from observation to a concrete next step is what separates debugging from "
                "dashboard watching. Write the slice name and count beside every rate, because a percentage "
                "without a denominator is not evidence."
            ),
            code=(
                'def error_by_slice(rows):\n'
                '    totals = {}\n'
                '    wrong = {}\n'
                '    for name, true, pred in rows:\n'
                '        totals[name] = totals.get(name, 0) + 1\n'
                '        wrong[name] = wrong.get(name, 0) + (true != pred)\n'
                '    return {k: round(wrong[k] / totals[k], 3) for k in totals}\n'
                '\n'
                'rows = [\n'
                '    ("short", 1, 1), ("short", 0, 0), ("short", 1, 0),\n'
                '    ("medium", 1, 1), ("medium", 0, 1), ("medium", 0, 0), ("medium", 1, 1),\n'
                '    ("long", 1, 0), ("long", 0, 1), ("long", 0, 0), ("long", 1, 1), ("long", 1, 1),\n'
                ']\n'
                'rates = error_by_slice(rows)\n'
                'for name in sorted(rates, key=rates.get, reverse=True):\n'
                '    print(f"{name:<8} error rate {rates[name]}")\n'
                '\n'
                'assert rates["long"] == 0.4\n'
                'print("investigate the long slice first, then write the fix")'
            ),
            variant_b="add a slice with three examples and a single error, and discuss its wide interval",
            variant_c="split the long slice by label and compare the two error rates",
            mistakes=[
                "Scanning for a slice that flatters the model instead of defining slices before looking.",
                "Treating a tiny slice's error rate as precise without showing its count.",
                "Stopping at a slice name instead of reading the actual failing examples.",
            ],
            q1=(
                "What is the output of a good error analysis?",
                "A ranked set of hypotheses and concrete next steps such as tests, data fixes or targeted training, not just a number.",
            ),
            homework=(
                "Write `error_by_slice(rows)` taking (slice, true, pred) tuples and returning error rate per slice. "
                "Print the slices sorted from worst to best, and comment which slice you would investigate first "
                "and why."
            ),
            patterns=["def ", "print(", "sorted"],
            mapping=(
                "Production triage starts from failing examples grouped by customer segment or input source; that "
                "ranking decides whether the next fix is data, model or a guardrail."
            ),
        ),
        156: dict(
            topic="Ablations",
            idea=(
                "An ablation removes one component and measures what happens, which is the cheapest way to find "
                "out whether a design choice is earning its keep. The components can be features, preprocessing "
                "steps, architectural blocks, loss terms or augmentation policies, and the measurement should be "
                "the same held-out metric used for the release decision. A common mistake is to ablate on training "
                "data, where every component looks helpful because the model has memorised the set; another is to "
                "change several things at once and attribute the difference to one of them. Ablations are also not "
                "significance tests. A small drop may be noise, so keep the seeds fixed, report the spread when you "
                "have several runs, and treat the direction as a hypothesis rather than proof. The useful output is "
                "a table of full performance, performance without each component, and the drop, sorted by cost. "
                "Today you compute that table from fixed prediction lists for three ablations and print the drops. "
                "The habit generalises to production: removing a feature is also a latency, cost and maintenance "
                "experiment, and the same table answers whether the complexity pays for itself. A drop of one example in a "
                "small evaluation set is not a reason to keep a feature."
            ),
            code=(
                'def evaluate(preds, labels):\n'
                '    hits = sum(1 for p, y in zip(preds, labels) if p == y)\n'
                '    return round(hits / len(labels), 3)\n'
                '\n'
                'labels = [1, 0, 1, 1, 0, 0, 1, 1, 0, 0]\n'
                'full = [1, 0, 1, 1, 0, 0, 1, 1, 1, 0]\n'
                'no_metadata = [1, 0, 1, 0, 0, 0, 1, 0, 0, 0]\n'
                'no_text = [0, 0, 1, 1, 0, 1, 1, 1, 1, 0]\n'
                'base = evaluate(full, labels)\n'
                'print("full accuracy:", base)\n'
                'for name, preds in (("without metadata", no_metadata), ("without text", no_text)):\n'
                '    score = evaluate(preds, labels)\n'
                '    print(f"{name:<18} acc={score} drop={round(base - score, 3)}")\n'
                '\n'
                'assert base == 0.9 and evaluate(no_text, labels) == 0.7\n'
                'print("keep a component only if its removal costs something real")'
            ),
            variant_b="ablate two components together and compare the joint drop with the sum of singles",
            variant_c="evaluate the same ablations on training data and explain the flattering result",
            mistakes=[
                "Ablating on training data, where memorisation makes every component look useful.",
                "Changing several components at once and attributing the whole difference to one of them.",
                "Calling a small single-seed drop a real effect without checking the run-to-run spread.",
            ],
            q1=(
                "Why should ablations use the same held-out metric as the release decision?",
                "Otherwise a component can look useful on training data while not improving the metric that actually governs deployment.",
            ),
            homework=(
                "Write `ablation_table(labels, candidates)` where candidates maps a name to predictions and returns "
                "each name's accuracy and drop from the full model. Print the table sorted by drop and comment which "
                "component you would remove first."
            ),
            patterns=["def ", "print(", "for "],
            mapping=(
                "Feature stores and serving stacks use ablation cost tables to justify deleting a feature; the "
                "same evidence supports latency and maintenance reductions."
            ),
        ),
        157: dict(
            topic="Experiment logs as tables",
            idea=(
                "An experiment log is only useful if two runs can be compared without opening a notebook and "
                "guessing which cell was executed. The minimum record is a row per run with an immutable "
                "identifier, a config fingerprint, the seed, the data version, the metric values and the code or "
                "image version. Logging results as a table rather than prose forces every run to have the same "
                "columns, which is what makes sorting, filtering and regression checks possible. The table should "
                "live outside the training script, generated at the end of a run, because hand-edited logs drift "
                "from the artefacts they claim to describe. For a small project a plain list of dictionaries "
                "printed or appended to a text file is enough; the structure matters more than the tool. Two "
                "habits make the log trustworthy: record failed and aborted runs, not just the good ones, and "
                "never overwrite a row, since deletion destroys the evidence you need when a metric later looks "
                "unreproducible. Today you sort fixed run records by validation accuracy and print an aligned "
                "table with the seed and run name, which is the same shape a tracker shows. The table is your "
                "memory: if it cannot answer what changed between two numbers, it is incomplete."
            ),
            code=(
                'runs = [\n'
                '    {"name": "baseline", "seed": 0, "val_acc": 0.812},\n'
                '    {"name": "lr-3e-4", "seed": 0, "val_acc": 0.834},\n'
                '    {"name": "augment", "seed": 1, "val_acc": 0.841},\n'
                ']\n'
                'print(f"{"run":<10}{"seed":>5}{"val_acc":>9}")\n'
                'for run in sorted(runs, key=lambda r: -r["val_acc"]):\n'
                '    name = run["name"]\n'
                '    seed = run["seed"]\n'
                '    acc = run["val_acc"]\n'
                '    print(f"{name:<10}{seed:>5}{acc:>9.3f}")\n'
                '\n'
                'best = max(runs, key=lambda r: r["val_acc"])\n'
                'assert best["name"] == "augment"\n'
                'print("best run:", best["name"], "seed", best["seed"])'
            ),
            variant_b="add a duration column and sort by validation accuracy per second",
            variant_c="include a failed run in the table and mark it rather than deleting it",
            mistakes=[
                "Logging only the best run, so the comparison that explains the result is lost.",
                "Overwriting an old row after a rerun, destroying the original measurement.",
                "Storing results without the seed or config, making a number impossible to reproduce.",
            ],
            q1=(
                "What belongs in a minimal experiment log row?",
                "A run identifier, config and seed, data and code version, and the metric values, so two runs can be compared without guesswork.",
            ),
            homework=(
                "Write `log_table(runs)` taking a list of dictionaries with name, seed and val_acc, and returning "
                "an aligned text table sorted by val_acc descending. Print it and comment which column makes two "
                "runs comparable."
            ),
            patterns=["def ", "sorted", "print("],
            mapping=(
                "Experiment trackers persist the same rows as a queryable store; the schema is what allows a team "
                "to diff releases and audit why a metric moved."
            ),
        ),
        158: dict(
            topic="Checkpointing",
            idea=(
                "A checkpoint is the serialised state needed to resume or serve a model: parameters, optimiser "
                "state, the epoch or step, and the configuration and data version that produced it. Saving only "
                "the weights is a common and expensive shortcut, because the optimiser state determines whether "
                "training resumes smoothly and the configuration determines whether the weights mean anything. "
                "Checkpointing is also a safety mechanism: long jobs fail, and a checkpoint converts a lost week "
                "into a lost hour. The serialisation format should be boring and explicit. Plain JSON or a "
                "dictionary of tensors is enough for a toy model, and the same principles apply when a framework "
                "writes its own binary format: version the schema, record the shape of each array, and verify that "
                "a round trip is exact before trusting the file. A checkpoint that cannot be loaded by a fresh "
                "process is not a checkpoint; it is a file. Today you encode a tiny parameter dictionary as JSON, "
                "decode it, and assert that the reloaded state is identical. That round-trip test is the smallest "
                "version of the load check every serving pipeline should run before declaring an artefact deployable. Name "
                "checkpoints by run identifier and step, never by the best score, which invites silent overwrites."
            ),
            code=(
                'import json\n'
                '\n'
                'state = {"step": 1200, "w1": 0.25, "w2": -0.5, "b": 0.125}\n'
                'blob = json.dumps(state, sort_keys=True)\n'
                'restored = json.loads(blob)\n'
                'print("blob:", blob)\n'
                'print("restored keys:", sorted(restored))\n'
                'print("identical:", restored == state)\n'
                '\n'
                'changed = dict(state)\n'
                'changed["w1"] = 0.251\n'
                'assert restored == state\n'
                'assert json.loads(json.dumps(changed)) != state\n'
                'print("a checkpoint is data, and it must survive a round trip")'
            ),
            variant_b="add a step counter to the state and confirm it survives the round trip",
            variant_c="compare a shallow copy with a decoded copy and show why the decoded one is safer",
            mistakes=[
                "Saving weights without optimiser state, so resumed training behaves differently.",
                "Assuming a written file loads correctly instead of testing the round trip.",
                "Changing the checkpoint schema without versioning it, breaking older artefacts.",
            ],
            q1=(
                "Why save optimiser state alongside model weights?",
                "It lets training resume with the same momentum and update history, so the resumed run behaves like the uninterrupted one.",
            ),
            homework=(
                "Write `round_trip(state)` that encodes a parameter dictionary with json, decodes it, and returns "
                "both the blob and whether the state survived exactly. Print the blob and the check, and assert "
                "that a modified state does not match."
            ),
            patterns=["def ", "json", "print("],
            mapping=(
                "Model registries and training launchers rely on versioned checkpoints; the load round trip is the "
                "first smoke test before any artefact is promoted."
            ),
        ),
        159: dict(
            topic="Quantisation concepts",
            idea=(
                "Quantisation stores weights and sometimes activations in fewer bits, trading a little numerical "
                "precision for a large reduction in memory and often in latency. The simplest scheme is symmetric "
                "integer quantisation: choose a scale equal to the maximum absolute weight divided by the largest "
                "representable integer, round each weight to that grid, and store the integers plus the scale. "
                "Dequantisation multiplies back, so the error per weight is bounded by half a scale step. The "
                "practical consequences follow from that bound: small weights suffer proportionally more, outliers "
                "stretch the scale and coarsen everything else, and per-channel scales reduce that damage. In real "
                "deployment the payoff is eight-bit weights instead of thirty-two, roughly a fourfold size "
                "reduction, plus faster integer kernels on suitable hardware. The risk is a silent accuracy drop "
                "that only appears on rare inputs, which is why quantised models are evaluated against the float "
                "baseline on the same slices, not just on the average. Today you quantise five fixed weights to "
                "eight bits, dequantise them, and print the maximum reconstruction error and the size ratio. The "
                "exercise is arithmetic, but it builds the reflex to measure the error instead of assuming small "
                "weight changes are harmless. Calibration and error slices still decide whether the quantised "
                "artefact is acceptable, since average accuracy can barely move."
            ),
            code=(
                'weights = [-0.74, 0.12, 0.98, -0.35, 0.51]\n'
                'scale = max(abs(w) for w in weights) / 127\n'
                'codes = [round(w / scale) for w in weights]\n'
                'restored = [round(c * scale, 3) for c in codes]\n'
                'error = max(abs(a - b) for a, b in zip(weights, restored))\n'
                'print("scale:", round(scale, 5))\n'
                'print("int8 codes:", codes)\n'
                'print("restored:", restored)\n'
                'print("max error:", round(error, 4))\n'
                'print("bytes fp32:", 4 * len(weights), "int8:", len(weights))\n'
                '\n'
                'assert error < scale\n'
                'assert 4 * len(weights) == 4 * len(weights)\n'
                'print("quantisation trades precision for size and speed")'
            ),
            variant_b="add one large outlier weight and show the scale stretching and error rising",
            variant_c="quantise to four bits and compare the reconstruction error with eight bits",
            mistakes=[
                "Forgetting to store the scale, so the integer codes cannot be interpreted.",
                "Ignoring one large outlier that stretches the scale and coarsens all other weights.",
                "Shipping a quantised model without comparing it to the float baseline on the same slices.",
            ],
            q1=(
                "What bounds the error introduced by symmetric quantisation?",
                "Half a scale step per weight, where the scale is the maximum absolute weight divided by the largest representable integer.",
            ),
            homework=(
                "Write `quantise(weights, bits=8)` returning the scale, integer codes and dequantised weights. "
                "Print the maximum error and the byte ratio against float32, and comment why an outlier stretches "
                "the scale."
            ),
            patterns=["def ", "print(", "round"],
            mapping=(
                "Edge and mobile serving routinely uses quantised artefacts; the evaluation gate compares the "
                "quantised model with the float baseline on the same slices before release."
            ),
        ),
        160: dict(
            topic="Inference batching",
            idea=(
                "Inference batching is the practice of running several requests through the model at once, and its "
                "economics are dominated by fixed overhead. Each call pays for setup, kernel launches, memory "
                "transfer and scheduling whether it processes one example or thirty-two, while the marginal cost "
                "per example is comparatively small. The result is that per-example latency falls sharply as batch "
                "size grows, until the batch no longer fits in memory or the latency of waiting to fill it becomes "
                "the dominant cost. That second limit is what separates offline scoring, where large batches are "
                "free throughput, from interactive serving, where a request cannot wait for a full batch. The "
                "trade-off is therefore not simply bigger is better; it is a schedule that balances queueing delay "
                "against throughput. Measuring it with a simple cost model makes the shape visible: total time "
                "equals overhead plus per-item work. Today you evaluate that model across four batch sizes and "
                "print total and per-item milliseconds. In production you would replace the constants with measured "
                "numbers and add the tail latency, because averages hide the users who wait longest. The lesson is "
                "to reason about batches as a scheduling decision rather than a model property. Measure the curve on the "
                "real server, because launch overhead and memory bandwidth change the constants."
            ),
            code=(
                'def batch_cost(batch, overhead=2.0, per_item=0.05):\n'
                '    return overhead + per_item * batch\n'
                '\n'
                'for size in (1, 8, 32, 128):\n'
                '    total = batch_cost(size)\n'
                '    print(f"batch {size:>3}: total {total:6.2f} ms, per item {total / size:5.3f} ms")\n'
                '\n'
                'assert batch_cost(128) / 128 < batch_cost(1)\n'
                'print("batching amortises fixed overhead across requests")'
            ),
            variant_b="increase the fixed overhead and show the throughput gain from batching growing",
            variant_c="add a queue delay that grows with batch size and find the point where it dominates",
            mistakes=[
                "Assuming the largest batch always wins, ignoring the queueing delay to fill it.",
                "Reporting average latency while users experience the slow tail.",
                "Batching requests that have incompatible shapes without padding or bucketing.",
            ],
            q1=(
                "Why does batching reduce per-example latency?",
                "Fixed per-call overhead is shared across more examples, so total time grows slowly while the per-item share falls.",
            ),
            homework=(
                "Write `batch_profile(sizes, overhead, per_item)` returning total and per-item milliseconds per "
                "batch size. Print the table, and comment why the smallest per-item cost is not automatically the "
                "best serving choice."
            ),
            patterns=["def ", "for ", "print("],
            mapping=(
                "Serving systems choose maximum batch size and timeout together; the profile explains why a larger "
                "batch improves throughput while a timeout protects interactive latency."
            ),
        ),
        161: dict(
            topic="Deployment constraints",
            idea=(
                "Deployment constraints are the non-negotiable numbers that decide whether a technically accurate "
                "model can run where it is needed. Four constraints cover most cases: artifact size, which affects "
                "download and cold start; memory, which caps concurrency; latency at a stated percentile, because "
                "averages hide the slow tail; and cost per thousand requests, which follows from all three. Each "
                "constraint is a budget, and a model that misses one is not deployable regardless of its accuracy. "
                "The right order is to write the budget first, measure the candidate against it second, and only "
                "then discuss optimisation. Measuring means measuring the packaged artifact on target hardware "
                "with realistic inputs, not the training script on a laptop. It also means recording headroom, "
                "since a model that uses ninety-nine percent of the memory budget will fail under a traffic spike. "
                "When a constraint fails, the response is a concrete option: quantise, distil, cache, shard, or "
                "relax the requirement after an explicit conversation with the product owner. Today you compare a "
                "fixed model profile against a fixed budget and print pass or fail per constraint, then a single "
                "deployable verdict. That verdict is deliberately conservative: one failed gate blocks the release. Write "
                "the budget down before training, otherwise the target quietly moves to fit whatever the model costs."
            ),
            code=(
                'budget = {"size_mb": 50.0, "p95_ms": 40.0, "ram_mb": 256.0}\n'
                'model = {"size_mb": 42.5, "p95_ms": 37.0, "ram_mb": 300.0}\n'
                'deployable = True\n'
                'for key in sorted(budget):\n'
                '    passed = model[key] <= budget[key]\n'
                '    deployable = deployable and passed\n'
                '    print(f"{key:<8} model {model[key]:>6.1f} budget {budget[key]:>6.1f} "\n'
                '          f"{"pass" if passed else "fail"}")\n'
                '\n'
                'print("deployable:", deployable)\n'
                'assert deployable is False\n'
                'print("one failed constraint blocks the release")'
            ),
            variant_b="tighten the memory budget until one constraint fails and flip the verdict",
            variant_c="add a cost-per-request constraint and express it in terms of the other three",
            mistakes=[
                "Measuring on a laptop with the training script instead of the packaged artifact on target hardware.",
                "Reporting average latency and ignoring the tail that users actually feel.",
                "Treating a missed constraint as a warning rather than a blocked release.",
            ],
            q1=(
                "What should you do when a model misses one deployment constraint?",
                "Treat it as not deployable and choose an explicit response such as quantising, distilling, caching or renegotiating the budget.",
            ),
            homework=(
                "Write `check_budget(model, budget)` returning a per-constraint pass map and an overall verdict. "
                "Print each row, assert that one failing constraint flips the verdict, and comment which constraint "
                "blocks this model."
            ),
            patterns=["def ", "print(", "assert"],
            mapping=(
                "Release pipelines make budgets explicit and fail closed; the same numbers feed capacity planning "
                "and incident reviews when a model starts timing out."
            ),
        ),
        162: dict(
            topic="Detecting data drift",
            idea=(
                "Data drift is the change in the distribution of inputs or outcomes after a model is deployed, and "
                "it is the most common reason a model that passed evaluation quietly degrades. Covariate drift "
                "changes the features, label drift changes the relationship between features and target, and "
                "concept drift changes both. Monitoring usually starts with cheap univariate checks: compare the "
                "live mean or rate of each feature against a frozen baseline from training or the last accepted "
                "window, and flag relative or absolute differences beyond a threshold. These checks catch pipeline "
                "breaks, a new client population or a seasonal shift without needing labels, which is their main "
                "advantage, since labels often arrive late or never. They also produce false alarms, so the "
                "threshold must be paired with a minimum sample size and an owner who knows what to do. A drift "
                "alert is a prompt to investigate, not proof of model failure; the model may be correctly handling "
                "a new but benign population. Today you compare fixed baseline and live means for three features, "
                "print the relative deltas, and list the drifted ones. The exercise is small, but the production "
                "pattern is identical: define the baseline, version it, monitor the delta, and keep the raw slices "
                "for the next error analysis."
            ),
            code=(
                'baseline = {"age": 34.0, "spend": 51.0, "clicks": 3.0}\n'
                'live = {"age": 35.7, "spend": 74.0, "clicks": 3.1}\n'
                'threshold = 0.2\n'
                'drifted = []\n'
                'for key in sorted(baseline):\n'
                '    delta = abs(live[key] - baseline[key]) / baseline[key]\n'
                '    flag = delta > threshold\n'
                '    if flag:\n'
                '        drifted.append(key)\n'
                '    print(f"{key:<7} delta {delta:5.2f} {"DRIFT" if flag else "ok"}")\n'
                '\n'
                'print("drifted features:", drifted)\n'
                'assert drifted == ["spend"]\n'
                'print("drift checks compare live slices with a frozen baseline")'
            ),
            variant_b="lower the threshold and show a benign feature being flagged",
            variant_c="compare two live windows against the same baseline and show drift appearing over time",
            mistakes=[
                "Monitoring drift without versioning the baseline, so the comparison target changes silently.",
                "Alerting on tiny samples where a harmless difference looks large.",
                "Treating a drift alert as proof of model failure instead of a prompt to investigate.",
            ],
            q1=(
                "Why monitor feature drift before labels arrive?",
                "Input distribution changes are observable immediately, so they can warn of degradation while waiting for delayed ground truth.",
            ),
            homework=(
                "Write `drift_report(baseline, live, threshold)` returning relative deltas and the drifted feature "
                "names. Print each feature with its delta, assert the expected drifted list, and comment why the "
                "baseline must be versioned."
            ),
            patterns=["def ", "print(", "if "],
            mapping=(
                "Production monitors run drift checks on a schedule and attach the raw slices; an alert routes to "
                "an owner who decides between retraining, a data fix or no action."
            ),
        ),
        163: dict(
            topic="Turning failures into tests",
            idea=(
                "Every production failure should leave behind a test, otherwise the same bug returns with a "
                "different ticket number. The conversion is mechanical once the failing input is known: capture "
                "the smallest input that reproduces the problem, state the expected behaviour, and assert it in the "
                "suite that runs before deployment. The test does not need to reproduce the whole model; it needs "
                "to pin the contract that broke, whether that is an empty input, a missing field, a threshold "
                "boundary or a class the preprocessing used to drop. This is also how ambiguous requirements become "
                "precise: writing the expected output forces someone to decide what correct means. Regression tests "
                "are most valuable at the boundaries, because that is where the original failure usually lived. "
                "Keep them fast, deterministic and independent of network access, and name them after the incident "
                "so the history is searchable. Today you turn three fixed failure cases into assertions over a "
                "small function, run them, and print pass or fail for each. The pattern scales directly: a bug "
                "report becomes a failing test, the fix makes it pass, and the test stays as the guard against the "
                "next refactor. A failure without a test is a promise to repeat it."
            ),
            code=(
                'def total_positive(values):\n'
                '    return sum(v for v in values if v > 0)\n'
                '\n'
                'cases = [\n'
                '    ("empty", [], 0),\n'
                '    ("single", [2], 2),\n'
                '    ("mixed", [-3, 4, -1], 4),\n'
                ']\n'
                'all_passed = True\n'
                'for name, values, expected in cases:\n'
                '    got = total_positive(values)\n'
                '    passed = got == expected\n'
                '    all_passed = all_passed and passed\n'
                '    print(name, "got", got, "expected", expected, "pass" if passed else "fail")\n'
                '\n'
                'assert all_passed\n'
                'print("every fixed failure becomes one regression test")'
            ),
            variant_b="add the boundary case where the input is exactly zero",
            variant_c="deliberately break the function and confirm the regression suite fails loudly",
            mistakes=[
                "Fixing the bug without adding the reproducing input to the test suite.",
                "Writing a test that depends on the network or a random seed, so it fails intermittently.",
                "Testing only the happy path and leaving the failing boundary unguarded.",
            ],
            q1=(
                "How does a production failure become a regression test?",
                "Capture the smallest reproducing input, state the expected behaviour, and assert it in the suite that guards deployment.",
            ),
            homework=(
                "Write `run_regressions(cases)` where cases are (name, input, expected) and the function returns "
                "pass flags. Print each result, assert that all pass, and comment how a bug report becomes a "
                "permanent test."
            ),
            patterns=["def ", "print(", "assert"],
            mapping=(
                "CI suites grow from incident postmortems; a regression test named after the incident is the "
                "cheapest insurance against the same outage recurring after a refactor."
            ),
        ),
        164: dict(
            topic="Review: evaluation and deployment checklist",
            idea=(
                "A release checklist is the moment the phase turns from techniques into a decision. The checklist "
                "should be short enough to run every time and specific enough that each item can fail. A workable "
                "set covers the evaluation protocol, the metric panel, calibration, error slices, the ablation "
                "table, drift monitoring, rollback and ownership. Each item answers a question a reviewer would "
                "otherwise have to ask: was the holdout touched once, are rare classes reported, does the "
                "confidence mean anything, which slice is worst, did every component earn its place, who is paged "
                "when drift fires, and how do we go back. The checklist is not bureaucracy if it prevents a "
                "category of mistake; it is bureaucracy when nobody can say what failure it blocks. Keep it in "
                "version control beside the deployment script and update it after every incident, because the "
                "postmortem is where the next item comes from. Today you score a fixed checklist and print the "
                "blocked items with a conservative verdict. The output is deliberately not a percentage that hides "
                "a failure: any unchecked required item means not ready. That single rule is the difference "
                "between a checklist and a formality. Review the list after every release, because the gaps that "
                "matter are the ones just exposed."
            ),
            code=(
                'checks = {\n'
                '    "metrics on holdout": True,\n'
                '    "calibration reported": True,\n'
                '    "ablation run": False,\n'
                '    "drift monitor": True,\n'
                '    "rollback ready": True,\n'
                '}\n'
                'passed = sum(1 for value in checks.values() if value)\n'
                'blockers = [name for name in sorted(checks) if not checks[name]]\n'
                'print("passed:", passed, "of", len(checks))\n'
                'for name in blockers:\n'
                '    print("blocked:", name)\n'
                'ready = not blockers\n'
                'print("ready to ship:", ready)\n'
                '\n'
                'assert passed == 4 and ready is False\n'
                'print("any unchecked required item blocks the release")'
            ),
            variant_b="add a required owner field and show an unowned check blocking release",
            variant_c="remove a passing item and show the verdict is unchanged until a required one fails",
            mistakes=[
                "Turning the checklist into a percentage that lets a serious failure average out.",
                "Adding items nobody can explain, so the list becomes a formality skipped under time pressure.",
                "Leaving rollback and ownership off the list until an incident makes them urgent.",
            ],
            q1=(
                "What makes a release checklist useful rather than bureaucratic?",
                "Every item blocks a specific, known failure and can be checked quickly; unexplained items should be removed or rewritten.",
            ),
            homework=(
                "Write `release_ready(checks)` returning the passed count, the blocked item names and the boolean "
                "verdict. Print the score and every blocker, then assert that any unchecked required item makes "
                "the verdict false."
            ),
            patterns=["def ", "print(", "assert"],
            mapping=(
                "Mature deployment practice pairs a short checklist with automated gates and a named owner; the "
                "checklist is the human-readable layer over the same recorded evidence."
            ),
        ),
    },
)
