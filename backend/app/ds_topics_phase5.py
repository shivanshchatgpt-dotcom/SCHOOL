"""Data Science topics — Phase 5 (Evaluation and Deployment)."""

PHASE_5: dict[str, dict] = {}

def _t(topic, theory, code, questions, answers, homework):
    PHASE_5[topic] = {
        "theory": theory, "code": code,
        "questions": questions, "answers": answers, "homework": homework,
    }

_t("Regression metrics",
    "**What it is**\nScoring numeric predictions: MAE (mean |error|, robust, in units), MSE/RMSE (squared — punishes big misses), R² (variance explained vs predicting the mean).\n\n"
    "**Why it matters**\nDifferent metrics rank models differently; the metric must match the business cost of errors.\n\n"
    "**Watch out**\nRMSE is in target units but outlier-sensitive; R² can be negative on test data — meaning worse than predicting the mean.",
    "truth   = [70, 80, 90]\npredicted = [72, 78, 97]\nerrors = [p - t for p, t in zip(predicted, truth)]\nmae = sum(abs(e) for e in errors) / len(errors)\nmse = sum(e*e for e in errors) / len(errors)\nrmse = mse ** 0.5\nmean_t = sum(truth)/len(truth)\nss_res = sum(e*e for e in errors)\nss_tot = sum((t - mean_t)**2 for t in truth)\nr2 = 1 - ss_res/ss_tot\nprint(f'MAE={mae:.2f} RMSE={rmse:.2f} R2={r2:.3f}')",
    ["MAE vs RMSE — when prefer MAE?", "What does negative R² signal?", "Which metric matches 'big mistakes cost double'?"],
    ["Outlier-heavy targets or when errors are linear in size", "Test predictions worse than always predicting the mean", "MSE/RMSE — squaring penalises large errors disproportionately"],
    "Compute MAE, MSE, RMSE and R² by hand for three predictions, print all four, and state which model change each metric would motivate.")

_t("Classification metrics",
    "**What it is**\nFrom the confusion matrix: accuracy (all correct), precision (TP/(TP+FP) — trusted alarms), recall (TP/(TP+FN) — caught cases), F1 (their harmonic mean).\n\n"
    "**Why it matters**\nAccuracy lies on imbalanced data: 99% negatives → a do-nothing model scores 99%.\n\n"
    "**Watch out**\nPick the metric from error costs: spam filtering wants precision; cancer screening wants recall.",
    "truth     = [1, 0, 1, 1, 0, 0, 1]\npredicted = [1, 0, 0, 1, 0, 1, 1]\ntp = sum(p == 1 and t == 1 for p, t in zip(predicted, truth))\nfp = sum(p == 1 and t == 0 for p, t in zip(predicted, truth))\nfn = sum(p == 0 and t == 1 for p, t in zip(predicted, truth))\ntn = sum(p == 0 and t == 0 for p, t in zip(predicted, truth))\naccuracy = (tp + tn) / len(truth)\nprecision = tp / (tp + fp)\nrecall = tp / (tp + fn)\nf1 = 2 * precision * recall / (precision + recall)\nprint(f'tp={tp} fp={fp} fn={fn} tn={tn}')\nprint(f'acc={accuracy:.2f} prec={precision:.2f} rec={recall:.2f} f1={f1:.2f}')",
    ["Why does accuracy fail on imbalanced data?", "Precision vs recall in one line?", "When is F1 the right summary?"],
    ["Predicting the majority class alone scores high while catching nothing useful", "Precision: of predicted positives, how many were right; recall: of real positives, how many were found", "You need one balanced number and both error types matter"],
    "Build a full confusion matrix by hand from two lists, derive all four metrics, print them, and name which metric a fraud team would prioritise.")

_t("Precision recall tradeoff",
    "**What it is**\nThe classification threshold slides along a tradeoff: lower threshold → higher recall but more false positives (lower precision); raise it and precision climbs as recall drops.\n\n"
    "**Why it matters**\nThe default 0.5 threshold is rarely optimal — the operating point is a business decision about error costs.\n\n"
    "**Watch out**\nOn heavy imbalance, PR curves are more informative than ROC curves.",
    "probs = [0.93, 0.81, 0.64, 0.45, 0.30, 0.12]\ntruth = [1,     1,    0,    1,    0,    0]\nfor threshold in [0.3, 0.5, 0.8]:\n    preds = [1 if p >= threshold else 0 for p in probs]\n    tp = sum(p == 1 and t == 1 for p, t in zip(preds, truth))\n    fp = sum(p == 1 and t == 0 for p, t in zip(preds, truth))\n    fn = sum(p == 0 and t == 1 for p, t in zip(preds, truth))\n    prec = tp / (tp + fp) if tp + fp else 1.0\n    rec = tp / (tp + fn)\n    print(f'threshold {threshold}: precision {prec:.2f}, recall {rec:.2f}')",
    ["Lowering the threshold moves precision/recall which ways?", "Who chooses the operating point?", "PR vs ROC — when prefer PR?"],
    ["Recall up, precision down", "The product owner, based on the relative cost of FP vs FN", "With imbalanced classes"],
    "Score six probabilities at three thresholds, print precision/recall per threshold, and recommend an operating point with one-sentence justification.")

_t("Data leakage",
    "**What it is**\nLeakage = training information that won't exist at prediction time: target-encoding features, fitting scalers before splitting, duplicating rows across train/test, using future data.\n\n"
    "**Why it matters**\nLeaked models score brilliantly offline and collapse in production — the most expensive silent failure in ML.\n\n"
    "**Watch out**\nGroup leakage too: same user's rows on both sides of the split.",
    "features = ['hours_studied', 'mock_score', 'final_exam_score']\ntarget = 'pass_fail'\ndef leaks(feature):\n    return 'final' in feature or feature == target\nreport = {f: leaks(f) for f in features}\nfor f, bad in report.items():\n    verdict = 'LEAK - remove' if bad else 'ok'\n    print(f'{f}: {verdict}')\nassert any(report.values()), 'detector must catch final_exam_score'",
    ["Three classic leakage channels?", "Why fit transforms on train only?", "How does group leakage happen?"],
    ["Future information in features; pre-split transform fitting; duplicated/split entities across sets", "Fitting on all data smuggles test-set statistics into training", "Related rows (same student/user/event) landing in both train and test"],
    "Write a leak-checker over a five-feature plan that flags at least two leaking names, print the verdict table, and fix the plan in comments.")

_t("Bias checks",
    "**What it is**\nSystematically comparing model behaviour across subgroups: per-group error rates, selection rates, calibration. A globally-good model may badly serve a minority slice.\n\n"
    "**Why it matters**\nUnfair models harm people and expose organisations legally. Aggregate metrics hide subgroup failures.\n\n"
    "**Watch out**\nFairness definitions conflict (equal accuracy vs equal selection rate) — choose deliberately and document.",
    "data = [\n    ('group-a', 1, 1), ('group-a', 0, 0), ('group-b', 1, 0), ('group-b', 0, 0), ('group-b', 1, 0),\n]  # (group, truth, predicted)\nfrom collections import defaultdict\nstats = defaultdict(lambda: [0, 0])   # correct, total\nfor group, t, p in data:\n    stats[group][0] += int(t == p)\n    stats[group][1] += 1\nrates = {}\nfor group, (correct, total) in stats.items():\n    rates[group] = correct / total\n    print(f'{group}: accuracy {rates[group]:.2f} on n={total}')\nprint('max group gap:', round(max(rates.values()) - min(rates.values()), 2), '(investigate if large)')",
    ["Why check subgroup metrics at all?", "Name two fairness criteria that can conflict", "First action on finding a big gap?"],
    ["Aggregate averages conceal failure concentrated in minority groups", "Equalised odds vs demographic parity", "Audit the group's data volume/quality before touching the model"],
    "Compute per-group accuracy from mixed records, print each group plus the max gap, and write what threshold would trigger investigation.")

_t("Error analysis",
    "**What it is**\nStudying the model's actual mistakes: collect misclassified rows, look for patterns (which slices? which features? hard cases or label noise?), then target fixes.\n\n"
    "**Why it matters**\nAggregate scores say how much you're wrong; error analysis says WHERE and WHY — the only path to targeted improvement.\n\n"
    "**Watch out**\nAnalyse errors on VALIDATION data, never tune against the test set.",
    "rows = [\n    {'hours': 6, 'score': 55, 'truth': 'pass', 'pred': 'fail'},\n    {'hours': 1, 'score': 90, 'truth': 'fail', 'pred': 'fail'},\n    {'hours': 7, 'score': 58, 'truth': 'pass', 'pred': 'fail'},\n]\nerrors = [r for r in rows if r['truth'] != r['pred']]\nfalse_negatives = [r for r in errors if r['truth'] == 'pass']\navg_hours_fn = sum(r['hours'] for r in false_negatives) / len(false_negatives)\nprint('all errors:', len(errors), '| false negatives:', len(false_negatives))\nprint(f'FN students average {avg_hours_fn:.1f}h yet low scores -> mock-score weight too high')",
    ["Why analyse errors instead of just retraining?", "Validation vs test for error analysis?", "What pattern justifies a new feature?"],
    ["Patterns in mistakes reveal targeted fixes; blind retraining is guesswork", "Validation — the test set stays sealed until the end", "A consistent slice of errors sharing a measurable property"],
    "Filter errors from prediction records, split into FN/FP, compute one aggregate trait of the dominant error type, and print a recommended fix.")

_t("Saving models",
    "**What it is**\nPersist trained artifacts to disk so training and serving decouple: joblib/pickle for sklearn objects, JSON elsewhere. Save the WHOLE pipeline (preprocessing + model), not just the estimator.\n\n"
    "**Why it matters**\nRetraining on every request is wasteful and non-reproducible; persistence enables versioned, reviewable deployments.\n\n"
    "**Watch out**\nPickle loads arbitrary code — only load artifacts you trust; keep library versions pinned.",
    "import json\npipeline_artifact = {\n    'version': '1.0.0',\n    'scaler': {'mean': 3.5, 'sd': 1.2},\n    'model': {'type': 'threshold-rule', 'params': {'cut': 0.5}},\n    'trained_at': '2026-08-26',\n}\nwith open('/tmp/model.json', 'w') as f:\n    json.dump(pipeline_artifact, f)\nwith open('/tmp/model.json') as f:\n    loaded = json.load(f)\nassert loaded == pipeline_artifact\nprint('saved & reloaded:', loaded['version'], loaded['model']['params'])",
    ["Save the model or the pipeline — why?", "Security risk of pickle.load?", "What metadata belongs beside every artifact?"],
    ["The pipeline — serving must reproduce preprocessing exactly", "Pickle executes embedded code; untrusted files are remote-code-execution vectors", "Version, training date, library versions, evaluation score"],
    "Serialise a mini pipeline dict (scaler params + model params) to JSON, reload it, assert equality, and print a version-stamped confirmation.")

_t("Loading models",
    "**What it is**\nThe serving side: load the artifact once at startup, rebuild the exact preprocessing, apply it to incoming requests, return predictions. Loading code must match saving code version-for-version.\n\n"
    "**Why it matters**\nTrain/serve skew — subtly different preprocessing at load time — silently degrades production quality.\n\n"
    "**Watch out**\nValidate the artifact on load (schema/version checks) so mismatches crash loudly at boot, not quietly per request.",
    "import json\nwith open('/tmp/model.json') as f:\n    artifact = json.load(f)\nassert artifact['version'].startswith('1.'), 'unsupported artifact version'\nmean, sd = artifact['scaler']['mean'], artifact['scaler']['sd']\ncut = artifact['model']['params']['cut']\ndef predict(raw_value):\n    z = (raw_value - mean) / sd\n    return 'positive' if z >= cut else 'negative'\nfor value in [2.0, 3.5, 6.0]:\n    print(value, '->', predict(value))",
    ["What is train/serve skew?", "Why validate artifacts at load time?", "When should the model load — per request or startup?"],
    ["Preprocessing differing between training and serving environments, degrading predictions", "Bad/mismatched artifacts should fail fast at boot rather than corrupt live traffic", "At startup — loading is expensive; requests should only infer"],
    "Load your saved /tmp/model.json, assert its version, reimplement predict() from its parameters, run three inputs, and print results.")

_t("Simple API",
    "**What it is**\nWrap a loaded model behind HTTP: POST features → JSON prediction. FastAPI gives validation (Pydantic) and docs free.\n\n"
    "**Why it matters**\nThe API contract decouples model internals from every consumer — you can swap models without touching clients.\n\n"
    "**Watch out**\nValidate input schemas strictly; garbage features should 422, not produce confident nonsense.",
    "# Real endpoint (requires pip install fastapi uvicorn):\n# from fastapi import FastAPI\n# from pydantic import BaseModel\n# class Features(BaseModel):\n#     hours: float\n# app = FastAPI()\n# @app.post('/predict')\n# def predict(f: Features):\n#     return {'prediction': model.predict([[f.hours]])[0]}\n\ndef api_sim(body):\n    assert isinstance(body.get('hours'), (int, float)), '422: hours must be numeric'\n    return {'status': 200, 'body': {'prediction': 'pass' if body['hours'] >= 4 else 'fail'}}\nprint(api_sim({'hours': 5}))\ntry:\n    api_sim({'hours': 'five'})\nexcept AssertionError as e:\n    print('rejected:', e)",
    ["Why serve models through an API at all?", "What should invalid input trigger?", "Two things FastAPI adds beyond routing?"],
    ["Decouples consumers from implementation; centralises validation/logging/scaling", "A 422 validation error — never a silent bad prediction", "Pydantic request validation and auto-generated OpenAPI docs"],
    "Write an api_sim() enforcing a typed field, exercise one valid and one invalid call, print both outcomes, and add the real FastAPI code as comments.")

_t("Reporting results",
    "**What it is**\nCommunicating model performance honestly: metric(s) matched to costs, baseline comparison, uncertainty (CV spread/CI), subgroup breakdown, known limitations.\n\n"
    "**Why it matters**\nDecisions ride on reports. A bare '87% accuracy' invites misuse; context prevents it.\n\n"
    "**Watch out**\nNever report test metrics selected after peeking — report the single locked-in number.",
    "report = {\n    'metric_rationale': 'recall primary (missing passers is costly)',\n    'baseline': 'majority-class accuracy 0.58',\n    'result': 'recall 0.84, precision 0.79 (CV mean of 5 folds)',\n    'uncertainty': 'fold spread ±0.03',\n    'subgroups': 'group-a recall 0.86, group-b recall 0.80 — monitored',\n    'limitations': 'self-reported hours; observational data',\n}\nfor section, text in report.items():\n    print(f'{section:>18}: {text}')",
    ["Six sections of an honest model report?", "Why justify the metric choice?", "Where do limitations belong?"],
    ["Metric rationale, baseline, result, uncertainty, subgroups, limitations", "Readers must see WHY this metric reflects the decision's costs", "In the main report — not buried in an appendix"],
    "Write a six-section report dict for any earlier lesson's numbers, print it formatted, and assert the baseline section exists.")

_t("Versioning data",
    "**What it is**\nDatasets change: rows added, cleaning rules revised. Data versioning records WHICH data produced WHICH model — via snapshots, hashes, or tools like DVC.\n\n"
    "**Why it matters**\n'Model v3 dropped 2%' is undiagnosable without knowing the data also changed. Reproducibility requires pinning both.\n\n"
    "**Watch out**\nHash the file contents, not filenames — names lie, hashes don't.",
    "import hashlib, json\n\ndef data_fingerprint(rows):\n    blob = json.dumps(rows, sort_keys=True).encode()\n    return hashlib.sha256(blob).hexdigest()[:12]\n\ndataset_v1 = [{'id': 1, 'score': 85}]\ndataset_v2 = dataset_v1 + [{'id': 2, 'score': 92}]\nh1, h2 = data_fingerprint(dataset_v1), data_fingerprint(dataset_v2)\nprint('v1:', h1, '| v2:', h2, '| changed:', h1 != h2)\nregistry = {'model-a': {'data_hash': h2}}\nprint('model-a trained on:', registry['model-a']['data_hash'])",
    ["Why hash content instead of filename?", "What must a model registry record?", "Same filename, changed rows — detected?"],
    ["Content identifies the actual data; names get reused and lie", "The data hash/fingerprint it was trained on, plus code version", "Yes — the hash changes even though the name didn't"],
    "Fingerprint two dataset versions with hashlib, register a model against one hash, mutate a row, and show the fingerprint catches it.")

_t("Monitoring ideas",
    "**What it is**\nProduction models decay: data drift (inputs shift), concept drift (the X→y relation shifts). Monitor input distributions, prediction distributions, outcome rates, latency and error rates.\n\n"
    "**Why it matters**\nSilent decay erodes trust invisibly; alerts turn drift into scheduled retraining instead of surprise failures.\n\n"
    "**Watch out**\nAlert thresholds need baselines and hysteresis — naive daily comparisons page everyone for noise.",
    "baseline_mean, baseline_sd = 3.5, 1.0\nthis_week = [4.9, 5.2, 4.7, 5.0, 5.1]\nweek_mean = sum(this_week)/len(this_week)\nz_shift = abs(week_mean - baseline_mean) / (baseline_sd / len(this_week) ** 0.5)\nalert = z_shift > 3\nstatus = 'ALERT: retrain review' if alert else 'healthy'\nprint(f'input drift z={z_shift:.1f} -> {status}')\npred_rate, base_rate = 0.34, 0.25\nprint('positive-rate shift:', f'{pred_rate - base_rate:+.2f}', '(second signal)')",
    ["Data drift vs concept drift?", "Four monitorable signals?", "Why avoid naive alert thresholds?"],
    ["Inputs change vs the input-output relationship itself changes", "Input distribution stats, prediction distribution, outcome rates, system health (latency/errors)", "Without baselines/hysteresis they fire constantly on normal variation"],
    "Compute a drift z-score for a simulated week versus a stored baseline, print alert status, add a second signal check, and write the escalation rule in comments.")

_t("Stakeholder communication",
    "**What it is**\nTranslating analysis for non-technical audiences: lead with the decision, quantify in their units (money, hours, students), visualise simply, pre-answer 'so what?'.\n\n"
    "**Why it matters**\nModels create value only when acted on; the handoff lives or dies on communication.\n\n"
    "**Watch out**\nJargon ('AUC 0.83') excludes; translate to consequences ('catches 8 of 10 at-risk students').",
    "briefing = {\n    'decision': 'Offer tutoring to predicted-failing students',\n    'evidence': 'Model flags 8 of 10 true strugglers two weeks early',\n    'cost_of_error': 'Extra tutoring for ~2 false alarms per 10 flags',\n    'next_step': 'Pilot with one cohort next month; review weekly',\n}\nfor section, text in briefing.items():\n    print(f'{section.upper()}: {text}')\nassert all(len(text.split()) < 15 for text in briefing.values()), 'keep lines executive-short'\nprint('executive-length check passed')",
    ["Lead a stakeholder brief with decision or method — why?", "Translate 'recall 0.8' for a principal", "Why cap sentence length?"],
    ["Decision-first respects their time; method is supporting detail", "'Catches 8 of every 10 students who will struggle'", "Executive attention: short lines survive forwarding and meetings"],
    "Draft a four-section executive briefing dict with a length assertion, print it, and rewrite one jargon sentence into consequence language.")

_t("Portfolio case study",
    "**What it is**\nA portfolio case study packages one project for reviewers: problem, data, approach, results with honest caveats, repo link. It demonstrates judgment, not just code.\n\n"
    "**Why it matters**\nHiring managers read case studies to see how you THINK — framing and honesty differentiate stronger candidates.\n\n"
    "**Watch out**\nInclude failures and iterations; flawless narratives read as fiction.",
    "case_study = {\n    'title': 'Predicting student pass/fail from study habits',\n    'problem': 'Tutors need early warning, not post-exam surprises',\n    'data': 'simulated 200-student log; leak-checked features',\n    'approach': 'logistic regression vs majority baseline, 5-fold CV',\n    'results': 'recall 0.84; precision 0.79',\n    'caveats': 'simulated data; self-reported hours',\n    'repo': 'github.com/you/student-pass-predictor',\n}\nfor section, text in case_study.items():\n    print(f'{section:>9}: {text}')\nassert case_study.get('caveats'), 'honesty section mandatory'\nprint('case study passes honesty check')",
    ["Five core sections of a case study?", "Why include caveats deliberately?", "What does a case study prove beyond skill?"],
    ["Problem, data, approach, results, caveats (+ repo link)", "They demonstrate judgment and credibility — reviewers distrust perfect stories", "Communication and professional maturity"],
    "Assemble a seven-field case study dict including mandatory caveats and a repo placeholder, print it, and assert the honesty section is non-empty.")

_t("Data product project",
    "**What it is**\nPhase capstone: ship a small end-to-end data product — data → model → saved artifact → API simulation → monitoring hook → stakeholder brief — documented as one coherent unit.\n\n"
    "**Why it matters**\nProducts integrate modelling with engineering and communication; this is the day-to-day shape of applied data science work.\n\n"
    "**Watch out**\nScope tiny and finish: one working vertical slice beats three half-built components.",
    "product = {\n    'artifact': {'version': '1.0.0', 'hash': 'a1b2c3'},\n    'api_contract': 'POST /predict {hours: float} -> {prediction: str}',\n    'monitor': {'signal': 'input mean z-score', 'alert_if': '> 3'},\n    'brief': 'Flags at-risk students 2 weeks early; pilot next cohort',\n}\nchecks = [\n    bool(product['artifact']['hash']),\n    'POST' in product['api_contract'],\n    product['monitor']['alert_if'] == '> 3',\n    len(product['brief'].split()) < 20,\n]\nprint('ship checklist:', dict(zip(['artifact', 'api', 'monitor', 'brief'], checks)))\nassert all(checks), 'not shippable yet'\nprint('VERDICT: ready to demo')",
    ["What defines the minimum shippable slice?", "Why wire monitoring before launch?", "Order the six product components"],
    ["One complete path: data → model → served prediction → monitored → communicated", "Day-one traffic is when drift starts; retrofitting monitors gets skipped", "Data, model/artifact, API, monitoring, documentation/brief"],
    "Build a four-component product manifest (artifact, API contract, monitor rule, brief), run a four-point ship checklist with asserts, and print the verdict.")
