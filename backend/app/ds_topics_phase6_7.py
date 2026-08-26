"""Data Science topics — Phases 6–7 (Applied Projects, Capstone)."""

PHASE_6_7: dict[str, dict] = {}

def _t(topic, theory, code, questions, answers, homework):
    PHASE_6_7[topic] = {
        "theory": theory, "code": code,
        "questions": questions, "answers": answers, "homework": homework,
    }

# ====================== PHASE 6: APPLIED DATA PROJECTS ======================
_t("Question framing",
    "**What it is**\nA good analysis question is specific, answerable with available data, and tied to a decision: not 'improve learning' but 'does weekly quiz frequency raise day-30 retention scores?'\n\n"
    "**Why it matters**\nThe question determines the data, method and deliverable. Vague questions produce impressive-looking, useless analyses.\n\n"
    "**Watch out**\nTest framing: can you state the null hypothesis and the action if significant? If not, keep sharpening.",
    "questions = [\n    ('vague', 'How do we make students learn better?', False),\n    ('better', 'Does daily quiz practice raise week-4 test scores vs weekly quizzes?', True),\n]\nfor quality, text, decidable in questions:\n    print(f'{quality:>6}: {text}')\n    if decidable:\n        print('        -> null: no difference; if significant: adopt daily quizzes')",
    ["Three properties of a well-framed question?", "Convert 'are users happy?' into an analysable question", "What does decidability require?"],
    ["Specific, answerable with available data, decision-linked", "'Did NPS rise after the onboarding redesign, comparing matched cohorts?'", "A statable null hypothesis and a pre-agreed action for each outcome"],
    "Write one vague and one framed version of three questions of your own, print both versions, and mark which are decidable and why.")

_t("Dataset sourcing",
    "**What it is**\nFinding usable data: public sources (govt portals, Kaggle, UCI), APIs, your own logs. Evaluate each source on licence, freshness, coverage, and collection methodology.\n\n"
    "**Why it matters**\nAnalysis credibility inherits from data provenance — 'where did this come from?' is the first reviewer question.\n\n"
    "**Watch out**\nCheck the licence BEFORE building on a dataset; also check how missing values are encoded (−999? empty?).",
    "sources = [\n    {'name': 'open-gov portal', 'licence': 'open', 'updated': 'monthly', 'usable': True},\n    {'name': 'random blog csv', 'licence': 'unknown', 'updated': 'unknown', 'usable': False},\n    {'name': 'product API', 'licence': 'proprietary-ok', 'updated': 'live', 'usable': True},\n]\nfor s in sources:\n    verdict = 'USE' if s['usable'] else 'SKIP - unclear licence/freshness'\n    print(f\"{s['name']:>18}: {verdict}\")",
    ["Four criteria for judging a data source?", "Why check licences first?", "What is sentinel-encoded missingness?"],
    ["Licence, freshness/update cadence, coverage, collection methodology", "Legal risk invalidates everything built afterwards", "Missing values stored as special codes like −999 that pollute numeric stats"],
    "Score three candidate sources (real or invented) on four criteria in dicts, print USE/SKIP verdicts, and justify one skip.")

_t("Cleaning plan",
    "**What it is**\nBefore touching rows, write the cleaning plan: expected schema, allowed ranges, missing-value policy per column, deduplication key, transformation order. Then execute mechanically.\n\n"
    "**Why it matters**\nAd-hoc cleaning is unrepeatable and hides mistakes; a written plan is auditable and rerunnable.\n\n"
    "**Watch out**\nOrder matters: fix types before range-checks; deduplicate before imputing.",
    "cleaning_plan = {\n    'schema': {'name': 'str', 'score': '0-100 int', 'joined': 'ISO date'},\n    'missing_policy': {'score': 'drop row', 'name': 'fill as Unknown'},\n    'dedup_key': ['name', 'joined'],\n    'order': ['parse types', 'deduplicate', 'range-filter', 'impute'],\n}\nfor section, detail in cleaning_plan.items():\n    print(f'{section:>15}: {detail}')\nassert cleaning_plan['order'].index('parse types') < cleaning_plan['order'].index('range-filter')\nprint('ordering constraint verified: types before filters')",
    ["Four sections of a cleaning plan?", "Why parse types before filtering ranges?", "What makes a dedup key right?"],
    ["Expected schema, missing policy per column, dedup key, ordered steps", "Range comparisons need real numbers/dates, not strings", "It matches what genuinely makes a record unique in the domain"],
    "Write a four-section cleaning plan dict for any dataset idea, assert the ordering constraint programmatically, and print the plan.")

_t("Exploration",
    "**What it is**\nProject-phase EDA: profile every column (dtype, nulls, cardinality), inspect distributions and pairwise relations, log anomalies — producing findings that shape features and models.\n\n"
    "**Why it matters**\nEvery downstream choice (transforms, features, model class) should cite an exploration finding, not habit.\n\n"
    "**Watch out**\nWrite findings down during exploration; memory fades before the modelling decisions that need them.",
    "from collections import Counter\ncolumn = [85, 92, None, 78, 85, 300, 88]\nnulls = sum(v is None for v in column)\nvalues = [v for v in column if v is not None]\nprint(f'nulls: {nulls}/{len(column)}')\nprint(f'min/max: {min(values)}/{max(values)} -> 300 is suspicious')\nprint('top values:', Counter(values).most_common(2))\nfindings = ['one impossible value needs range filter', '85 repeats -> check duplicates']\nfor i, f in enumerate(findings, 1):\n    print(f'finding {i}: {f}')",
    ["Profile which three things per column?", "Why log findings immediately?", "What flags a suspicious max?"],
    ["Dtype/type, null count, cardinality or distribution summary", "Findings must survive into feature/model decisions made days later", "Distance from bulk of data relative to spread (IQR rule)"],
    "Profile a mixed column (with nulls and an outlier), print nulls/range/top-values, and write two logged findings that would change a modelling choice.")

_t("Feature plan",
    "**What it is**\nDesigning features deliberately: list candidates from domain reasoning, check availability at prediction time, decide transforms (log, bin, encode), and rank by expected signal.\n\n"
    "**Why it matters**\nFeatures beat algorithms on tabular problems; a planned feature set also exposes leakage before it hurts.\n\n"
    "**Watch out**\nEvery feature needs a leak-check AND a fallback for missing values at serving time.",
    "feature_plan = [\n    {'name': 'hours_per_week', 'source': 'study log', 'leak_safe': True, 'transform': 'log1p'},\n    {'name': 'consistency_sd', 'source': 'session gaps', 'leak_safe': True, 'transform': 'none'},\n    {'name': 'final_grade', 'source': 'registrar', 'leak_safe': False, 'transform': 'REJECTED'},\n]\napproved = [f['name'] for f in feature_plan if f['leak_safe']]\nrejected = [f['name'] for f in feature_plan if not f['leak_safe']]\nprint('approved:', approved)\nprint('rejected (leakage):', rejected)",
    ["Two mandatory checks per feature?", "Why log-transform skewed counts?", "Rank features by what?"],
    ["Leak-safety (exists at prediction time) and missing-value strategy", "Linear models see more symmetric, better-behaved relations", "Domain-expected signal strength — build the strongest first"],
    "Draft a five-row feature plan with leak flags and transforms, separate approved/rejected lists, print both, and justify one transform.")

_t("Baseline",
    "**What it is**\nThe baseline is the simplest defensible predictor — majority class, mean prediction, or a one-rule heuristic — scored with the SAME metric and folds as later models.\n\n"
    "**Why it matters**\nBaselines calibrate success: a complex model must demonstrably beat this floor or complexity is unjustified.\n\n"
    "**Watch out**\nFor imbalanced targets, the majority-class accuracy baseline is deceptively high — use recall/F1 floors too.",
    "truth = ['pass', 'fail', 'pass', 'pass', 'fail', 'pass', 'pass', 'fail']\nmajority = max(set(truth), key=truth.count)\nbaseline_preds = [majority] * len(truth)\nbaseline_acc = sum(p == t for p, t in zip(baseline_preds, truth)) / len(truth)\npasses = truth.count('pass')\nrecall_of_pass = sum(p == 'pass' and t == 'pass' for p, t in zip(baseline_preds, truth)) / passes\nprint(f'baseline: always predict {majority!r} -> acc {baseline_acc:.2f}, pass-recall {recall_of_pass:.2f}')\nprint('any real model must clear BOTH numbers')",
    ["What makes a baseline 'defensible'?", "Why does majority-class baseline mislead on imbalance?", "When may you skip a baseline?"],
    ["Same data, folds and metric as candidate models — nothing cherry-picked", "High accuracy while never detecting the minority class", "Never — even trivial baselines anchor interpretation"],
    "Compute majority-class baseline accuracy AND minority recall on a labelled list, print both floors, and state the bar your model must clear.")

_t("Iteration",
    "**What it is**\nDisciplined improvement loop: change ONE thing (a feature, a hyperparameter, a model), re-run identical CV, record the delta, keep or revert. One variable at a time keeps attribution honest.\n\n"
    "**Why it matters**\nSimultaneous changes make wins unattributable; single-variable iteration builds compounding, documented gains.\n\n"
    "**Watch out**\nSmall deltas within fold noise aren't wins — compare against CV spread before celebrating.",
    "iterations = [\n    {'change': 'add consistency_sd feature', 'cv_before': 0.78, 'cv_after': 0.81, 'spread': 0.02},\n    {'change': 'max_depth 5 -> 10',          'cv_before': 0.81, 'cv_after': 0.815, 'spread': 0.02},\n]\nfor it in iterations:\n    gain = it['cv_after'] - it['cv_before']\n    verdict = 'KEEP' if gain > it['spread'] else 'REVERT (within noise)'\n    print(f\"{it['change']:>28}: {gain:+.3f} -> {verdict}\")",
    ["Why change one variable per iteration?", "When is a +0.005 gain not a win?", "What must every iteration record?"],
    ["So score changes attribute cleanly to that single change", "When it's smaller than the CV fold spread", "The change, before/after CV score, and the keep/revert verdict"],
    "Log three iterations with before/after CV and spread, apply the noise-aware KEEP/REVERT rule, print verdicts, and total the kept gains.")

_t("Visualization review",
    "**What it is**\nPeer-reviewing project charts against a checklist: message in title, units on axes, zero baselines, colour accessibility, chart-type fit, no distortion.\n\n"
    "**Why it matters**\nAuthors go blind to their own charts; structured review catches misleading defaults before publication.\n\n"
    "**Watch out**\nReview the MESSAGE first ('what claim does this make?'), then mechanics — pretty-but-pointless charts pass mechanical checks.",
    "review_checklist = {\n    'message_in_title': True,\n    'axis_units_present': True,\n    'bar_zero_baseline': False,   # caught!\n    'colourblind_safe': True,\n    'chart_type_fits_question': True,\n}\nissues = [name for name, ok in review_checklist.items() if not ok]\nfor name, ok in review_checklist.items():\n    mark = 'PASS' if ok else 'FAIL'\n    print(f'{name:>26}: {mark}')\nprint('verdict:', 'publishable' if not issues else f'revise: {issues}')",
    ["First question a viz review asks?", "Five checklist items?", "Verdict rule?"],
    ["What single claim does this chart make?", "Message title, axis units, zero baseline, colour safety, type fit", "Any FAIL → revise before publishing"],
    "Run the five-item checklist over two chart specs (one with planted flaws), print PASS/FAIL lines, and output publishable/revise verdicts.")

_t("Model evaluation",
    "**What it is**\nThe formal evaluation step: locked test set scored ONCE with pre-declared metrics, alongside CV means, baseline comparison, subgroup breakdowns and uncertainty.\n\n"
    "**Why it matters**\nThis number goes in the report and drives the ship/no-ship call — it must be untainted by peeking.\n\n"
    "**Watch out**\nIf the test score disappoints, the honest options are accept-or-restart-with-new-data, not re-tune-and-rescore.",
    "evaluation = {\n    'protocol': 'test set untouched until now; metrics declared in advance',\n    'cv_mean_recall': 0.84,\n    'test_recall': 0.82,\n    'baseline_recall': 0.60,\n    'subgroup_gap': 0.05,\n    'verdict': '',\n}\ngap_cv_test = abs(evaluation['cv_mean_recall'] - evaluation['test_recall'])\nevaluation['verdict'] = ('SHIP' if evaluation['test_recall'] > evaluation['baseline_recall'] and gap_cv_test < 0.05 else 'HOLD - investigate')\nfor k, v in evaluation.items():\n    print(f'{k:>17}: {v}')",
    ["Why score the test set exactly once?", "CV≫test gap signals what?", "Ship criterion beyond beating baseline?"],
    ["Repeated scoring turns it into another tuning set — estimates inflate", "Overfitting to validation via repeated tuning", "Test performance consistent with CV (no big gap) and acceptable subgroup behaviour"],
    "Fill a six-field evaluation dict, compute the CV-test gap programmatically, derive SHIP/HOLD from stated rules, and print the full evaluation.")

_t("Recommendation writing",
    "**What it is**\nThe analysis ends in a recommendation: the decision, the evidence line, confidence level, conditions/risks, and the review date. Written for the decision-maker, not the modeller.\n\n"
    "**Why it matters**\nInsight without recommendation changes nothing; conditional recommendations handle uncertainty honestly.\n\n"
    "**Watch out**\nConfidence must match evidence: 'pilot' language for observational findings, stronger only for experimental ones.",
    "recommendation = {\n    'decision': 'Adopt weekly quiz intervention for flagged students',\n    'evidence': '+9 points vs control, permutation p≈0.01, CI (4, 14)',\n    'confidence': 'moderate - single-cohort experiment',\n    'conditions': 're-run flagger monthly; stop if lift < 3 points',\n    'review_date': '2026-11-26',\n}\nfor k, v in recommendation.items():\n    print(f'{k:>12}: {v}')",
    ["Five fields of a complete recommendation?", "Why attach conditions?", "Match confidence language to what?"],
    ["Decision, evidence, confidence, conditions, review date", "They pre-commit to stopping rules, preventing zombie projects", "The study design — experiments earn stronger claims than observations"],
    "Write all five recommendation fields for any earlier finding, print them, and verify the confidence wording matches an observational design.")

_t("Peer review",
    "**What it is**\nStructured review of another analyst's work: reproduce the headline number, check pipeline order (leakage!), probe one alternative interpretation, and give actionable feedback.\n\n"
    "**Why it matters**\nReproducibility errors and silent leaks are near-invisible to authors; fresh eyes catch them cheaply.\n\n"
    "**Watch out**\nReview the pipeline, not just results — a beautiful report can sit on a leaking split.",
    "review_report = {\n    'reproduced_headline': True,\n    'pipeline_order_ok': False,   # scaler fitted before split!\n    'alternative_explained': True,\n    'feedback': 'Refit scaler inside CV folds; rerun and resend results.',\n}\nblocking = [k for k in ('reproduced_headline', 'pipeline_order_ok') if not review_report[k]]\nfor k, v in review_report.items():\n    print(f'{k:>22}: {v}')\nprint('decision:', 'approve' if not blocking else f'changes requested: {blocking}')",
    ["First act of a peer review?", "Which flaw outranks a wrong number?", "Feedback format?"],
    ["Attempt to reproduce the headline result independently", "Pipeline leakage — it invalidates every number downstream", "Specific and actionable: name the fix, not just the fault"],
    "Complete a four-field review dict with one planted blocker, compute the approve/changes decision programmatically, and print the feedback.")

_t("Reproducibility check",
    "**What it is**\nThe final technical gate: fresh environment, pinned dependencies, seeded randomness, data hash verified — then run top-to-bottom and confirm identical outputs.\n\n"
    "**Why it matters**\nUnreplicable analysis can't be trusted, extended, or debugged later. This check is the difference between a demo and a result.\n\n"
    "**Watch out**\nHidden state lives in cells run out of order and unstated package versions — flush both.",
    "import hashlib, json, random\nrun_manifest = {'seed': 42, 'data_hash': None, 'result': None}\nrandom.seed(run_manifest['seed'])\ndata = sorted([random.random() for _ in range(5)])\nrun_manifest['data_hash'] = hashlib.sha256(json.dumps(data).encode()).hexdigest()[:10]\nrun_manifest['result'] = round(sum(data)/5, 6)\n# simulate second run\nrandom.seed(run_manifest['seed'])\ndata2 = sorted([random.random() for _ in range(5)])\nh2 = hashlib.sha256(json.dumps(data2).encode()).hexdigest()[:10]\nr2 = round(sum(data2)/5, 6)\nsame = (h2 == run_manifest['data_hash'] and r2 == run_manifest['result'])\nprint('runs identical:', same, '| hash:', run_manifest['data_hash'], '| mean:', run_manifest['result'])",
    ["Four ingredients of a reproducible run?", "What does hashing the input data add?", "Pass condition?"],
    ["Pinned dependencies, fixed seeds, hashed inputs, linear top-to-bottom execution", "Proves the exact data — not just the code — was identical", "Second run reproduces hash AND result bit-for-bit"],
    "Execute a seeded computation twice under a manifest (seed, hash, result), assert both runs match, and print the reproducibility verdict.")

_t("Portfolio writing",
    "**What it is**\nTurning the finished project into public artifacts: README with the five-section story, clean repo structure, requirements file, and a short results summary a stranger understands in two minutes.\n\n"
    "**Why it matters**\nWork that isn't communicable doesn't count — portfolios convert projects into opportunities.\n\n"
    "**Watch out**\nReviewers skim: put the result and one chart at the TOP of the README, setup instructions after.",
    "readme_outline = {\n    'hook': 'Predicts student risk 2 weeks early at 84% recall',\n    'problem': 'Tutors discover struggling students after finals',\n    'method': 'Logistic regression, 5-fold CV, leak-checked features',\n    'quickstart': 'pip install -r requirements.txt; python predict.py',\n    'structure': ['data/', 'src/', 'notebooks/', 'README.md'],\n}\nfor section, content in readme_outline.items():\n    print(f'{section:>10}: {content}')\nassert '84%' in readme_outline['hook']\nprint('hook leads with a quantified result: approved')",
    ["What belongs at the very top of a README?", "Minimum repo artifacts?", "Two-minute test?"],
    ["The hook: headline result with a number", "README, requirements.txt, organised src/, data note", "A stranger grasps problem+result in two minutes of skimming"],
    "Assemble a five-section README outline with a quantified hook, assert the hook contains a number, print it, and list the repo tree.")

_t("Presentation rehearsal",
    "**What it is**\nRehearsing delivery: time-boxed sections (problem 1 min, method 2, results 3, recommendation 2), one slide-one point, anticipated Q&A including limitations questions.\n\n"
    "**Why it matters**\nGood work dies in bad delivery; rehearsal exposes rambling, timing overruns and weak answers while they're still fixable.\n\n"
    "**Watch out**\nPractise the limitation answers hardest — 'what are the weaknesses?' is the guaranteed question.",
    "rehearsal = {\n    'sections': [('problem', 1), ('method', 2), ('results', 3), ('recommendation', 2)],\n    'qa_drills': ['data quality?', 'why logistic not deep learning?', 'bias risks?'],\n}\ntotal = sum(minutes for _, minutes in rehearsal['sections'])\nfor name, minutes in rehearsal['sections']:\n    print(f'{name:>15}: {minutes} min')\ntiming = 'fits 10-min slot' if total <= 8 else '(OVER TIME - cut)'\nprint('total:', total, 'minutes', timing)\nfor q in rehearsal['qa_drills']:\n    print('drill:', q)",
    ["Standard section timing for a 10-min slot?", "Which QA answers need most rehearsal?", "Slide rule?"],
    ["Problem 1, method 2–3, results 3–4, recommendation 2 — leave buffer", "Limitations and 'why not fancier methods?' questions", "One point per slide"],
    "Plan a timed presentation with four sections totalling ≤8 minutes plus three QA drills, validate the timing programmatically, and print the plan.")

_t("Applied project",
    "**What it is**\nPhase capstone: run one complete applied study — framed question → sourced data → cleaned → explored → modelled → evaluated → recommended — with every stage leaving an artifact.\n\n"
    "**Why it matters**\nThis is the portfolio centrepiece proving end-to-end capability, integrating all five previous phases.\n\n"
    "**Watch out**\nManage scope ruthlessly: a small complete study beats an ambitious incomplete one.",
    "applied_project = {\n    'question': 'Does consistency outperform cramming on retention?',\n    'artifacts': {\n        'framing': 'hypothesis + null recorded',\n        'data': '200 simulated learners, hash-pinned',\n        'model': 'logistic regression, CV 0.81 vs baseline 0.58',\n        'evaluation': 'test recall 0.80, subgroup gap 0.04',\n        'recommendation': 'pilot consistency nudges, review in 90 days',\n    },\n}\ncomplete = all(applied_project['artifacts'].values())\nfor stage, artifact in applied_project['artifacts'].items():\n    print(f'{stage:>15}: {artifact}')\nstatus = 'COMPLETE' if complete else 'GAPS REMAIN'\nprint('project completeness:', status)",
    ["Five stages that must each leave an artifact?", "Scope rule for applied projects?", "Completeness check?"],
    ["Framing, data, model, evaluation, recommendation", "Small and fully finished beats large and partial", "Every stage has a non-empty, verifiable artifact"],
    "Define a five-stage applied-project manifest with concrete artifacts, assert completeness programmatically, and print the full manifest.")

# ====================== PHASE 7: DATA SCIENCE CAPSTONE ======================
_t("Capstone question",
    "**What it is**\nThe capstone opens by locking ONE question: specific, decision-linked, answerable with data you can actually get — plus a written success criterion (what result changes what decision?).\n\n"
    "**Why it matters**\nEverything downstream inherits the question's quality. A locked question also prevents mid-project scope drift.\n\n"
    "**Watch out**\nWrite the success criterion BEFORE seeing results — post-hoc success definitions are self-deception.",
    "capstone_charter = {\n    'question': 'Which study habit best predicts week-4 retention scores?',\n    'decision': 'Choose which habit the app nudges daily',\n    'data_available': '90-day simulated learner logs',\n    'success_criterion': 'Identify a habit with CV recall >= 0.75, else recommend dashboard redesign',\n}\nfor field, text in capstone_charter.items():\n    print(f'{field:>18}: {text}')\nassert all(capstone_charter.values()), 'charter incomplete'\nprint('charter locked - no scope drift allowed')",
    ["Four fields of a capstone charter?", "Why lock the success criterion first?", "What does the charter prevent?"],
    ["Question, linked decision, available data, pre-written success criterion", "Post-hoc criteria let any result look like success", "Mid-project scope drift and moving goalposts"],
    "Write your own four-field charter with a falsifiable success criterion, assert completeness, print it, and declare it locked in a comment.")

_t("Data dictionary",
    "**What it is**\nA data dictionary documents every column: name, type, units, allowed range, meaning, missing-value encoding, and source. It is the contract between the data and everyone who uses it.\n\n"
    "**Why it matters**\nSix months later 'score' could mean mock, final or normalised — the dictionary settles it. Reviewers and teammates depend on it too.\n\n"
    "**Watch out**\nDocument UNITS explicitly (hours vs minutes, 0–1 vs 0–100) — unit confusion is a classic silent bug.",
    "data_dictionary = [\n    {'column': 'study_hours', 'type': 'float', 'units': 'hours/week', 'range': '0-80', 'missing': 'NaN'},\n    {'column': 'quiz_freq',   'type': 'int',   'units': 'quizzes/week', 'range': '0-7', 'missing': '-1'},\n    {'column': 'retention',   'type': 'int',   'units': 'score 0-100', 'range': '0-100', 'missing': 'NaN'},\n]\nfor col in data_dictionary:\n    assert col.get('units'), f\"{col['column']} missing units\"\n    print(f\"{col['column']:>12}: {col['type']:<6} {col['units']:<14} range {col['range']} missing={col['missing']}\")\nprint('every column documents units: dictionary valid')",
    ["Six attributes per documented column?", "Why are units mandatory?", "Who consumes a data dictionary?"],
    ["Name, type, units, range, meaning, missing encoding (+source)", "Unit mix-ups silently corrupt every statistic built on them", "Future you, teammates, reviewers, and anyone reusing the dataset"],
    "Document three columns with full attributes including units, assert each has units, print the table, and add one sentence on who will read it.")

_t("Analysis plan",
    "**What it is**\nThe pre-analysis contract: which features, which model candidates, which metric(s), which validation scheme, and what result triggers which action — all fixed BEFORE touching the test data.\n\n"
    "**Why it matters**\nIt converts exploration from fishing into testing, blocks p-hacking and cherry-picking, and makes the final claim defensible.\n\n"
    "**Watch out**\nIf you change the plan mid-way, log it as an amendment with reasons — silent deviations destroy credibility.",
    "analysis_plan = {\n    'features': ['study_hours', 'consistency_sd'],\n    'candidates': ['majority-baseline', 'logistic-regression', 'random-forest'],\n    'primary_metric': 'recall (missing at-risk students is costly)',\n    'validation': '5-fold stratified CV; test set scored once at end',\n    'actions': {'recall>=0.75': 'ship flagger', 'else': 'redesign dashboard'},\n}\nfor k, v in analysis_plan.items():\n    print(f'{k:>10}: {v}')\nassert 'baseline' in analysis_plan['candidates'][0]\nprint('plan includes baseline and dual actions: valid')",
    ["Five sections of an analysis plan?", "Why must a baseline appear among candidates?", "How to handle legitimate plan changes?"],
    ["Features, candidate models, primary metric, validation scheme, action mapping", "Results only mean something relative to a floor", "Logged amendments with reasons — never silent edits"],
    "Write a five-section analysis plan including a baseline candidate and both-branch actions, validate programmatically, and print it.")

_t("Data preparation",
    "**What it is**\nExecuting the cleaning + feature plan: parse types, deduplicate, enforce ranges, apply the missing policy, build features per the leak-checked plan — each step logged with before/after row counts.\n\n"
    "**Why it matters**\nPreparation determines ceiling quality; logged steps make the pipeline auditable and rerunnable.\n\n"
    "**Watch out**\nTrack row counts through EVERY step — unexplained drops hide broken filters.",
    "rows = [\n    {'name': 'riya', 'score': '85'}, {'name': 'riya', 'score': '85'},\n    {'name': 'aarav', 'score': None}, {'name': 'kabir', 'score': '250'},\n]\nlog = []\nn0 = len(rows)\nrows = [dict(r, score=int(r['score'])) for r in rows if r['score'] is not None]\nlog.append(f'parse+drop-null: {n0} -> {len(rows)} rows')\nn1 = len(rows)\nseen, deduped = set(), []\nfor r in rows:\n    key = (r['name'], r['score'])\n    if key not in seen:\n        seen.add(key)\n        deduped.append(r)\nrows = [r for r in deduped if 0 <= r['score'] <= 100]\nlog.append(f'dedupe+range: {n1} -> {len(rows)} rows')\nfor entry in log:\n    print(entry)\nprint('final:', rows)",
    ["What must accompany every preparation step?", "Order these: dedupe, range-filter, parse types", "Why track row counts?"],
    ["A log line with before/after row counts", "Parse types → deduplicate → range-filter", "Unexplained drops reveal broken filters or over-aggressive rules"],
    "Clean a four-row messy list through three logged steps, print each log line with counts, and show the final clean records.")

_t("Exploration report",
    "**What it is**\nThe written output of project EDA: per-column profiles, distribution notes, correlation highlights, anomaly list — each finding phrased so it implies a modelling decision.\n\n"
    "**Why it matters**\nIt converts raw looking into decisions: transforms chosen, features justified, anomalies handled. Also evidence of diligence for reviewers.\n\n"
    "**Watch out**\nFindings without implications ('mean is 70.2') are filler; every line should end in 'therefore…'.",
    "exploration_report = [\n    {'finding': 'retention is right-skewed (mean 74 > median 70)', 'implication': 'report median; consider log target'},\n    {'finding': 'study_hours correlates 0.62 with retention',      'implication': 'keep as lead feature'},\n    {'finding': '3 rows have quiz_freq = -1 (sentinel)',           'implication': 'recode to NaN, apply missing policy'},\n]\nfor i, item in enumerate(exploration_report, 1):\n    print(f\"{i}. {item['finding']}\")\n    print(f\"   -> therefore: {item['implication']}\")",
    ["Structure of each report line?", "What separates findings from filler?", "Which three profiles belong in it?"],
    ["Finding + the modelling decision it implies", "An actionable implication attached to each observation", "Column profiles, distributions/correlations, anomaly list"],
    "Write three finding→implication pairs from invented EDA, print them numbered, and verify each implication names a concrete decision.")

_t("Model baseline",
    "**What it is**\nThe capstone's floor: naive predictors (majority class / global mean) AND one simple heuristic rule, scored under the exact protocol later models face.\n\n"
    "**Why it matters**\nEvery improvement claim needs a reference point; baselines also expose class imbalance traps early.\n\n"
    "**Watch out**\nScore baselines with the SAME folds and metric — a differently-measured baseline is decoration, not calibration.",
    "truth =   ['at-risk', 'ok', 'at-risk', 'ok', 'ok', 'at-risk', 'ok', 'ok']\nhours =    [1.5,        6,     2,       7,    5,      1,      8,    6]\nmajority = max(set(truth), key=truth.count)\nnaive_acc = sum(majority == t for t in truth) / len(truth)\nheuristic_preds = ['at-risk' if h < 3 else 'ok' for h in hours]\nheur_acc = sum(p == t for p, t in zip(heuristic_preds, truth)) / len(truth)\nat_risk_count = truth.count('at-risk')\nheur_recall = sum(p == 'at-risk' and t == 'at-risk' for p, t in zip(heuristic_preds, truth)) / at_risk_count\nprint(f'majority baseline acc: {naive_acc:.2f}')\nprint(f'hours<3 heuristic: acc {heur_acc:.2f}, at-risk recall {heur_recall:.2f}')\nprint('models must beat BOTH floors')",
    ["Two kinds of baseline?", "Same-protocol requirement?", "What do baselines expose early?"],
    ["Naive statistical (majority/mean) and simple domain heuristics", "Identical folds, data and metric as challenger models", "Class imbalance and whether any signal exists at all"],
    "Compute majority-class accuracy plus a one-rule heuristic's accuracy and recall on labelled data, print all floors, and state the double bar.")

_t("Improvement experiment",
    "**What it is**\nOne controlled upgrade cycle beyond the baseline: hypothesise (feature/model/param), change exactly one thing, rerun identical CV, decide keep/revert against fold noise, log everything.\n\n"
    "**Why it matters**\nStructured single-variable experiments compound into real gains while keeping attribution clean.\n\n"
    "**Watch out**\nGains smaller than CV spread are noise — reverting them is progress, not failure.",
    "experiment_log = {\n    'hypothesis': 'Adding consistency_sd improves at-risk recall',\n    'change': 'one feature added; nothing else touched',\n    'cv_before': [0.72, 0.70, 0.74, 0.71, 0.73],\n    'cv_after':  [0.78, 0.76, 0.79, 0.77, 0.78],\n}\nbefore = sum(experiment_log['cv_before'])/5\nafter = sum(experiment_log['cv_after'])/5\nspread = max(experiment_log['cv_after']) - min(experiment_log['cv_after'])\ngain = after - before\nverdict = 'KEEP' if gain > spread else 'REVERT'\nprint(experiment_log['hypothesis'])\nprint(f'CV {before:.3f} -> {after:.3f} (gain {gain:+.3f}, spread {spread:.3f}) -> {verdict}')",
    ["The experiment loop's five steps?", "Keep condition?", "Why is reverting a valid outcome?"],
    ["Hypothesise, change one thing, rerun identical CV, compare vs noise, log verdict", "Gain exceeds CV fold spread", "Noise-level gains add complexity without value — discipline compounds trust"],
    "Run one logged experiment with five-fold arrays, compute gain vs spread programmatically, print KEEP/REVERT, and write the next hypothesis.")

_t("Final visuals",
    "**What it is**\nThe capstone's presentation layer: 3–4 publication-grade charts — headline result, key relationship, error/subgroup view, recommendation support — each passing the viz review checklist.\n\n"
    "**Why it matters**\nDecision-makers meet your work through these charts; they carry the argument when you're not in the room.\n\n"
    "**Watch out**\nEvery chart states its takeaway in the title; unlabelled axes fail review automatically.",
    "final_charts = [\n    {'title': 'Consistent studiers retain +11 points (p<0.01)', 'type': 'bar', 'checks': {'units': True, 'baseline_zero': True, 'colour_safe': True}},\n    {'title': 'Error concentration: low-hours students',        'type': 'scatter', 'checks': {'units': True, 'baseline_zero': True, 'colour_safe': False}},\n]\nfor chart in final_charts:\n    failed = [k for k, ok in chart['checks'].items() if not ok]\n    status = 'READY' if not failed else f'REVISE ({failed})'\n    print(f\"[{chart['type']:>7}] {chart['title']} -> {status}\")",
    ["Four canonical capstone charts?", "Automatic-fail conditions?", "Where does the takeaway live?"],
    ["Headline result, key relationship, errors/subgroups, recommendation support", "Missing units, non-zero bar baselines, inaccessible colour", "In the title, stated as a finding"],
    "Spec two final charts with three-point checklists (plant one failure), evaluate programmatically, and print READY/REVISE per chart.")

_t("Evaluation report",
    "**What it is**\nThe formal results document: protocol declaration, baseline vs model numbers with uncertainty, subgroup breakdown, limitations, and the ship/hold verdict mapped from the pre-set analysis plan.\n\n"
    "**Why it matters**\nThis document justifies the decision; its credibility rests on declared protocol and honest uncertainty.\n\n"
    "**Watch out**\nReport the pre-declared primary metric FIRST — secondary metrics inform but never rescue a failed primary.",
    "evaluation_report = {\n    'protocol': 'test set sealed until final scoring; primary metric declared in plan',\n    'primary_metric': 'at-risk recall',\n    'results': {'baseline_heuristic': 0.55, 'model_cv': 0.81, 'model_test': 0.79},\n    'uncertainty': 'CV fold spread ±0.02',\n    'subgroups': 'max group gap 0.04 - acceptable',\n    'limitations': 'simulated data; short horizon',\n    'verdict': '',\n}\nr = evaluation_report['results']\nevaluation_report['verdict'] = 'SHIP' if r['model_test'] > r['baseline_heuristic'] + 0.15 else 'HOLD'\nfor k, v in evaluation_report.items():\n    print(f'{k:>16}: {v}')",
    ["Seven sections of the evaluation report?", "Primary metric rule?", "Verdict derived from what?"],
    ["Protocol, primary metric, results incl. baseline, uncertainty, subgroups, limitations, verdict", "Declared in advance, reported first, never swapped post-hoc", "Pre-set thresholds in the analysis plan applied to locked test results"],
    "Assemble the seven-section report, derive SHIP/HOLD from a margin rule programmatically, print everything, and confirm primary-metric primacy.")

_t("Limitations",
    "**What it is**\nHonest constraints: data provenance and coverage gaps, simulation vs reality, short horizons, confounders not controlled, generalisation boundaries. Stated proactively, specifically, with impact estimates.\n\n"
    "**Why it matters**\nUndisclosed limitations get discovered by critics; disclosed ones become scoped trust. They also define future work.\n\n"
    "**Watch out**\nVague humility ('more data would help') is worthless — say WHICH limitation biases WHAT direction.",
    "limitations = [\n    {'issue': 'simulated learner data', 'impact': 'effect sizes likely optimistic vs real classrooms', 'mitigation': 'pilot on one real cohort before scaling'},\n    {'issue': '8-week observation window', 'impact': 'long-term retention effects unknown', 'mitigation': 'schedule 6-month follow-up'},\n]\nfor lim in limitations:\n    assert lim['impact'] and lim['mitigation'], 'each limitation needs impact + mitigation'\n    print(f\"- {lim['issue']}: {lim['impact']} -> {lim['mitigation']}\")",
    ["Three parts per limitation?", "Why proactive disclosure beats discovery?", "What does each limitation feed?"],
    ["Issue, directional impact, mitigation/next step", "Discovered limitations destroy credibility; disclosed ones scope it", "The future-work section"],
    "Write two fully-specified limitations (issue, impact, mitigation), assert completeness, print them, and note which future work each suggests.")

_t("Documentation",
    "**What it is**\nCapstone documentation: README (problem→result hook), setup instructions, pipeline description, artifact inventory (data hash, model version), and how to reproduce end-to-end.\n\n"
    "**Why it matters**\nDocumentation is the interface for every future reader — reviewers, teammates, and you in six months.\n\n"
    "**Watch out**\nWrite docs for the reader in a hurry: reproduction commands up top, narrative after.",
    "docs_inventory = {\n    'README.md': 'hook + problem + result + quickstart',\n    'requirements.txt': 'pinned dependency versions',\n    'pipeline.md': 'stage-by-stage description with row counts',\n    'manifest.json': 'data hash, seed, model version, metrics',\n    'reproduce.sh': 'single command rebuilding every number',\n}\nrequired = ['README.md', 'requirements.txt', 'reproduce.sh']\nmissing = [r for r in required if r not in docs_inventory]\nfor name, purpose in docs_inventory.items():\n    print(f'{name:>18}: {purpose}')\ndoc_status = 'COMPLETE' if not missing else f'missing {missing}'\nprint('doc set:', doc_status)",
    ["Five core documentation artifacts?", "Reader-first ordering rule?", "What does manifest.json pin?"],
    ["README, requirements, pipeline description, manifest, reproduce script", "Reproduction commands before narrative", "Data hash, seeds, model version, final metrics"],
    "Build a five-entry documentation inventory, assert the three required files exist, print purposes, and draft the one-line reproduce command.")

_t("Demo notebook",
    "**What it is**\nA linear demo notebook walking a stranger through the project in ~10 cells: load → prepare → model → evaluate → explain → conclude, each cell runnable top-to-bottom with narrative between.\n\n"
    "**Why it matters**\nIt's the fastest way for reviewers to trust and grasp the work — executable proof beats prose claims.\n\n"
    "**Watch out**\nThe Restart-and-Run-All test is pass/fail: any hidden cell order dependence fails the demo.",
    "demo_cells = [\n    ('1. Load pinned data', 'df = load(hash=manifest.data_hash)'),\n    ('2. Prepare per pipeline.md', 'clean = prepare(df)'),\n    ('3. Baseline floors', 'print(baseline_scores)'),\n    ('4. Model + CV', 'scores = cross_validate(model, clean)'),\n    ('5. Locked test score', 'print(test_score)  # scored once'),\n    ('6. Explain drivers', 'show(contributions)'),\n    ('7. Conclusion', 'print(verdict)'),\n]\nfor title, code in demo_cells:\n    print(f'{title:<28} | {code}')\nprint('restart & run all: deterministic (seeded, hash-pinned) -> PASS')",
    ["Target length and shape of a demo notebook?", "The pass/fail acceptance test?", "Cell 5 discipline?"],
    ["~7–10 linear cells, narrative between, no dead ends", "Restart kernel + Run All reproduces every output", "Locked test score shown exactly once, clearly labelled"],
    "Outline a seven-cell demo notebook with titles and one-line code sketches, verify linearity, and print the restart-test verdict.")

_t("Presentation",
    "**What it is**\nThe live capstone defence: timed sections, one message per slide, results visual-first, limitations owned confidently, ending on the recommendation and ask.\n\n"
    "**Why it matters**\nThe presentation moment decides how the work is remembered and funded; structure beats improvisation under pressure.\n\n"
    "**Watch out**\nNever present a metric without its baseline beside it — naked numbers invite distrust.",
    "presentation = {\n    'slides': [\n        ('problem', 'Tutors learn of struggling students too late'),\n        ('method', 'Logistic regression on leak-checked habits, 5-fold CV'),\n        ('result', 'Recall 0.81 vs 0.55 heuristic baseline'),\n        ('limits', 'Simulated data; real-cohort pilot planned'),\n        ('ask', 'Approve one-cohort pilot starting October'),\n    ],\n}\nfor section, message in presentation['slides']:\n    print(f'{section:>8} | {message}')\nassert any('baseline' in m.lower() for _, m in presentation['slides']), 'always show baseline beside results'\nprint('baseline-shown rule satisfied')",
    ["Five-slide skeleton?", "The baseline-beside-results rule?", "How should limitations be delivered?"],
    ["Problem, method, result, limits, ask", "No metric appears without its comparison point on the same slide", "Confidently and specifically — owned limits build trust"],
    "Script a five-slide deck with one message each, assert the baseline rule holds, print the outline, and time-box it to eight minutes.")

_t("Final review",
    "**What it is**\nThe last gate before submission: run the reproducibility check fresh, verify every report number traces to code, confirm documentation completeness, and re-read the charter against delivery.\n\n"
    "**Why it matters**\nFinal reviews catch integration drift — numbers that changed after late edits, docs that lagged code, charter promises quietly dropped.\n\n"
    "**Watch out**\nCheck traceability NUMBER BY NUMBER: one orphan stat undermines the whole document.",
    "final_review = {\n    'fresh_repro_run_passed': True,\n    'all_numbers_traced_to_code': True,\n    'documentation_complete': True,\n    'charter_success_criterion_met': True,\n}\ngates = list(final_review.values())\nfor gate, passed in final_review.items():\n    mark = 'PASS' if passed else 'FAIL'\n    print(f'{gate:>32}: {mark}')\nverdict = 'SUBMIT' if all(gates) else 'FIX GATES FIRST'\nprint('FINAL VERDICT:', verdict)",
    ["Four final gates?", "Traceability means what exactly?", "Who runs the final review?"],
    ["Fresh repro run, number traceability, doc completeness, charter fulfilment", "Every published figure regenerates from current code deterministically", "You — ideally after a night's sleep, with a checklist"],
    "Run a four-gate final review dict, compute SUBMIT/FIX programmatically, print each gate, and simulate one failing gate to see the verdict flip.")

_t("Data science capstone",
    "**What it is**\nThe finish line: assemble charter, dictionary, plan, prepared data, exploration report, baselines, experiments, visuals, evaluation, limitations, docs, demo and presentation into one coherent, defensible body of work.\n\n"
    "**Why it matters**\nIntegration is the skill: thirteen artifacts that individually pass but must also agree with each other.\n\n"
    "**Watch out**\nCross-check consistency: the README's numbers, notebook outputs and slides must match EXACTLY.",
    "capstone_package = {\n    'charter': 'question + success criterion locked',\n    'data': 'dictionary + hash-pinned dataset',\n    'analysis': 'plan + exploration report + prepared data',\n    'modelling': 'baselines + 3 logged experiments',\n    'communication': 'evaluation report + visuals + docs + demo + slides',\n    'integrity': 'all numbers traced; repro run green',\n}\ncomplete = all(capstone_package.values())\nfor component, summary in capstone_package.items():\n    print(f'{component:>13}: {summary}')\nfinal = 'COMPLETE - defend it proudly' if complete else 'INCOMPLETE'\nprint('CAPSTONE:', final)",
    ["Six components of the finished package?", "Final consistency check?", "What does completion certify?"],
    ["Charter, data, analysis, modelling, communication, integrity checks", "Every number identical across README, notebook and slides", "End-to-end capability: frame, build, evaluate, communicate, defend"],
    "Assemble your six-component capstone package summary, assert completeness, print it, and write one sentence on what you can now defend.")
