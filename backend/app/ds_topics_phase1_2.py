"""Data Science topics — Phases 1–2 (Data Workflow, Statistics)."""

PHASE_1_2: dict[str, dict] = {}

def _t(topic, theory, code, questions, answers, homework):
    PHASE_1_2[topic] = {
        "theory": theory, "code": code,
        "questions": questions, "answers": answers, "homework": homework,
    }

# ============================ PHASE 1: DATA WORKFLOW ========================
_t("CSV datasets",
    "**What it is**\nA CSV stores tabular data as plain text: one header row, then comma-separated values per row. It is the most common exchange format between spreadsheets, databases and analysis tools.\n\n"
    "**Why it matters**\nAlmost every real dataset you will download starts life as CSV. Reading it correctly is step zero of every analysis.\n\n"
    "**Watch out**\nValues containing commas get quoted — never parse CSV by splitting on ',' yourself; use the csv module or pandas.",
    "# Inspect a CSV's structure before analysing it\nimport csv, io\n\ntext = 'name,score\\nriya,85\\naarav,92\\nkabir,'\nreader = csv.DictReader(io.StringIO(text))\nrows = list(reader)\nprint('columns:', reader.fieldnames)\nprint('row count:', len(rows))\nprint(rows[0])",
    ["What does DictReader give you that plain splitting doesn't?", "Why is the header row special?", "What danger hides in a value like '\"Patel, R\"'?"],
    ["It maps each row to a dict keyed by column names instead of returning raw lists", "It defines the column names used to interpret every following row", "Naive comma-splitting breaks it — proper CSV parsing respects quotes"],
    "Build a three-row CSV string about study hours, read it with csv.DictReader, print the columns, row count and first row.")

_t("Pandas DataFrames",
    "**What it is**\nThe DataFrame is pandas' core object: a labelled 2-D table where every column is a Series sharing an index.\n\n"
    "**Why it matters**\nDataFrame operations are vectorised — filtering, aggregating and joining happen at C speed without writing loops.\n\n"
    "**Watch out**\npandas must be installed (pip install pandas). Under the hood a DataFrame is a bundle of NumPy arrays plus index labels.",
    "import pandas as pd\n\ndata = {'name': ['riya', 'aarav', 'kabir'],\n        'hours': [3, 5, 2],\n        'score': [85, 92, 78]}\ndf = pd.DataFrame(data)\nprint(df)\nprint('shape:', df.shape)\nprint('average score:', df['score'].mean())",
    ["What three things make up a DataFrame?", "Why prefer df['score'].mean() over a manual loop?", "What does df.shape return?"],
    ["Column data (NumPy arrays), column labels, and a row index", "Vectorised operations are faster, shorter and less error-prone than Python loops", "A tuple (rows, columns)"],
    "Create a DataFrame with 4 rows of (subject, minutes_studied), print it, its shape, and the total minutes using .sum().")

_t("Selecting columns",
    "**What it is**\ndf['col'] returns one column as a Series; df[['a', 'b']] returns multiple columns as a new DataFrame (note the double brackets).\n\n"
    "**Why it matters**\nSelection is how you narrow a wide table down to what your question needs.\n\n"
    "**Watch out**\nSingle brackets give a Series, double brackets give a DataFrame — they behave differently when you chain methods.",
    "import pandas as pd\n\ndf = pd.DataFrame({'name': ['riya', 'aarav'], 'hours': [3, 5], 'score': [85, 92]})\nscores = df['score']                 # Series\nsubset = df[['name', 'score']]       # DataFrame\nprint(type(scores).__name__, type(subset).__name__)\nprint(subset)",
    ["Difference between df['a'] and df[['a']]?", "What type is a single selected column?", "How do you select three specific columns?"],
    ["Single brackets → Series; double brackets → DataFrame", "pandas.Series", "df[['col1', 'col2', 'col3']]"],
    "From a 4-column DataFrame, select just two columns into a new variable, print both the selection and its type.")

_t("Filtering rows",
    "**What it is**\nBoolean masking filters rows: df[df['score'] >= 80] keeps only rows where the condition is True.\n\n"
    "**Why it matters**\nEvery 'show me only…' question in analysis is a filter. Combine conditions with & (and), | (or) and parentheses.\n\n"
    "**Watch out**\nUse & and |, NOT 'and'/'or' — and use parentheses around each condition because & binds tighter than comparisons.",
    "import pandas as pd\n\ndf = pd.DataFrame({'name': ['riya', 'aarav', 'kabir'], 'hours': [3, 5, 2], 'score': [85, 92, 58]})\nhard_workers = df[df['hours'] >= 3]\nstrong = df[(df['hours'] >= 3) & (df['score'] >= 80)]\nprint(hard_workers)\nprint(strong)",
    ["What does df[mask] do?", "Why parentheses around each condition?", "Why & instead of and?"],
    ["Keeps only rows where the boolean mask is True", "& has higher precedence than comparison operators, so without them the expression parses wrongly", "numpy/pandas overload bitwise operators for element-wise logic; Python's 'and' cannot be vectorised"],
    "From a marks DataFrame, filter students who scored above 70 AND studied more than 2 hours; print how many rows survived.")

_t("Missing data",
    "**What it is**\nReal datasets have holes: NaN marks missing numeric values. Detect with .isna(), drop with .dropna(), fill with .fillna(value).\n\n"
    "**Why it matters**\nOne NaN silently poisons sums, means and models. Handling missingness is a decision, not an accident.\n\n"
    "**Watch out**\nNaN != NaN — comparing won't find it. Also ask WHY data is missing before choosing drop vs fill.",
    "import pandas as pd\n\ndf = pd.DataFrame({'name': ['riya', 'aarav', 'kabir'], 'score': [85, None, 78]})\nprint(df['score'].isna().sum(), 'missing')\nfilled = df['score'].fillna(df['score'].mean())\nprint(filled.tolist())\nprint('mean works after filling:', filled.mean())",
    ["How do you count missing values per column?", "Drop vs fill — what decides?", "Why can't you find NaN with =="],
    ["df.isna().sum()", "If missingness is random and few → drop; if dropping loses signal → fill with mean/median/mode", "NaN compares unequal to everything, including itself"],
    "Create a DataFrame with two missing scores, print the missing count, then produce BOTH a dropped version and a mean-filled version and print both.")

_t("Duplicates",
    "**What it is**\nDuplicate rows arise from double imports or repeated logging. .duplicated() flags them; .drop_duplicates() removes them.\n\n"
    "**Why it matters**\nDuplicates inflate counts and bias averages — a student counted twice changes your conclusions.\n\n"
    "**Watch out**\nDecide what makes a row unique: subset=['name'] deduplicates by name even if other columns differ.",
    "import pandas as pd\n\ndf = pd.DataFrame({'name': ['riya', 'riya', 'aarav'], 'score': [85, 85, 92]})\nprint('duplicates found:', df.duplicated().sum())\nclean = df.drop_duplicates()\nprint('before:', len(df), 'after:', len(clean))",
    ["Which method flags duplicate rows?", "How would you deduplicate by name only?", "Why do duplicates matter for averages?"],
    [".duplicated() (True for each repeat beyond the first)", "df.drop_duplicates(subset=['name'])", "Repeated rows over-weight some observations, skewing means and counts"],
    "Build a list with one repeated student entry, convert to a DataFrame, show the duplicate count, then drop duplicates and compare lengths.")

_t("Data types",
    "**What it is**\nEach column has a dtype: int64, float64, object (text), datetime64, bool. Check with df.dtypes; convert with .astype() or pd.to_numeric().\n\n"
    "**Why it matters**\nA 'score' column stored as text can't be averaged. Wrong dtypes are the #1 hidden bug in beginner analyses.\n\n"
    "**Watch out**\nAny column containing even one string becomes object dtype — numbers imported from messy CSVs often arrive as text.",
    "import pandas as pd\n\ndf = pd.DataFrame({'raw_score': ['85', '92', '78']})\nprint('before:', df.dtypes.iloc[0])\ndf['score'] = pd.to_numeric(df['raw_score'])\nprint('after:', df.dtypes['score'])\nprint('mean now possible:', df['score'].mean())",
    ["Why might numbers import as text?", "Which conversion fixes numeric-as-text?", "What dtype does a text column get?"],
    ["One stray non-numeric value (or formatting) forces the whole column to object/string", "pd.to_numeric(column) (or .astype(int) when clean)", "object"],
    "Create a DataFrame where scores are strings, verify the dtype, convert with pd.to_numeric, then compute and print the mean.")

_t("Grouping",
    "**What it is**\ndf.groupby('col')['metric'].agg(['mean', 'count']) splits rows into groups, aggregates each, and combines results — split-apply-combine.\n\n"
    "**Why it matters**\n'Average score per subject' or 'total hours per student' are groupby questions. It replaces dozens of manual filter-and-sum steps.\n\n"
    "**Watch out**\nAfter groupby the grouping column becomes the INDEX — use .reset_index() if you want it back as a normal column.",
    "import pandas as pd\n\ndf = pd.DataFrame({'subject': ['maths', 'maths', 'code', 'code'],\n                   'score': [85, 91, 78, 88]})\nsummary = df.groupby('subject')['score'].agg(['mean', 'count'])\nprint(summary.reset_index())",
    ["Describe split-apply-combine in one line", "What does .agg(['mean','count']) give?", "Why call reset_index() afterwards?"],
    ["Split rows by key, apply an aggregation per group, combine into one result table", "Both statistics per group in one DataFrame", "groupby turns the key into the index; reset_index restores it as a regular column"],
    "Group a study-log DataFrame by subject and print average minutes plus session count per subject.")

_t("Merging tables",
    "**What it is**\npd.merge(left, right, on='key') joins two tables on a shared column — like SQL JOIN. how='inner' keeps matches only; 'left' keeps all left rows.\n\n"
    "**Why it matters**\nReal insights live across tables: scores in one file, students in another. Merging reunites them.\n\n"
    "**Watch out**\nCheck row counts after merging — unexpected growth means duplicate keys; shrinkage means unmatched rows were dropped.",
    "import pandas as pd\n\nstudents = pd.DataFrame({'id': [1, 2], 'name': ['riya', 'aarav']})\nscores = pd.DataFrame({'id': [1, 1, 2], 'score': [85, 90, 92]})\nmerged = pd.merge(students, scores, on='id')\nprint(merged)\nprint('rows:', len(merged), '(one-to-many join)')",
    ["What role does the 'on' column play?", "inner vs left join difference?", "Why inspect row counts after a merge?"],
    ["It is the shared key matched between the two tables", "inner keeps only matching keys; left keeps every left row, filling misses with NaN", "Row-count surprises reveal duplicate keys or failed matches"],
    "Merge a students table with a multi-row scores table on id, print the result, and comment whether the join was one-to-one or one-to-many.")

_t("Datetime data",
    "**What it is**\nDates often arrive as text. pd.to_datetime() converts them to datetime64, unlocking .dt.year, .dt.month, .dt.day_name() and date arithmetic.\n\n"
    "**Why it matters**\nTrends live in time: monthly totals, weekday patterns, gaps between events. Text dates can't be sorted or grouped properly.\n\n"
    "**Watch out**\nDay-first vs month-first formats differ by region — pass dayfirst=True when needed.",
    "import pandas as pd\n\ndf = pd.DataFrame({'logged': ['2026-08-01', '2026-08-05', '2026-08-09'],\n                   'minutes': [45, 60, 30]})\ndf['logged'] = pd.to_datetime(df['logged'])\ndf['weekday'] = df['logged'].dt.day_name()\nspan = (df['logged'].max() - df['logged'].min()).days\nprint(df[['weekday', 'minutes']].to_string())\nprint('days covered:', span)",
    ["Why convert dates from text?", "Name two things .dt gives you", "What does subtracting two datetimes give?"],
    ["Text can't be ordered, grouped by month, or used in arithmetic", "Components like .dt.month/.dt.year and helpers like .dt.day_name()", "A Timedelta — e.g. .days gives the gap"],
    "Convert a text-date study log to datetime, add a weekday column, and print the number of days between first and last entry.")

_t("Data validation",
    "**What it is**\nValidation asserts your data obeys expectations BEFORE analysis: ranges (0–100), allowed categories, no negative ages, correct dtypes.\n\n"
    "**Why it matters**\nA typo like score=850 silently skews every downstream statistic. Validate early, fail loudly.\n\n"
    "**Watch out**\nValidate AFTER cleaning too — cleaning steps themselves can corrupt data.",
    "import pandas as pd\n\ndf = pd.DataFrame({'score': [85, 92, 850, 78]})\nout_of_range = df[~df['score'].between(0, 100)]\nassert len(out_of_range) > 0, 'expected to catch the bad row'\nprint('invalid rows:')\nprint(out_of_range.to_string())",
    ["Give three things worth validating", "When should validation run?", "Why assert instead of print?"],
    ["Value ranges, category membership, dtypes/nulls in key columns", "Immediately after loading, and again after every transformation", "Assertions crash loudly on violation instead of letting bad data flow on silently"],
    "Load a small scores DataFrame containing one impossible value, write validation checks (range + nulls), and print every violating row.")

_t("Reproducible notebooks",
    "**What it is**\nA reproducible notebook runs top-to-bottom and produces identical results: fixed random seeds, no hidden state, data loaded from files not memory edits.\n\n"
    "**Why it matters**\nAnalysis others can't rerun isn't verifiable — including future you. Reproducibility is the scientific baseline.\n\n"
    "**Watch out**\nRunning cells out of order creates invisible state; Restart & Run All is the honesty test.",
    "import random\nrandom.seed(42)                    # same shuffle every run\nsample = random.sample(range(100), 5)\nprint('deterministic sample:', sample)\nprint('rerun this cell - identical output proves reproducibility')",
    ["What is the 'Restart & Run All' test?", "Why set random seeds?", "Name two sources of hidden notebook state"],
    ["Restarting the kernel and running every cell in order must reproduce the exact results", "Seeded randomness produces the same sequence on every machine/run", "Variables left from edited/deleted cells; unseeded random draws"],
    "Write a cell that seeds random, samples 5 numbers twice, and asserts both samples are equal — proving determinism.")

_t("Data ethics",
    "**What it is**\nEthical data work means consent for collection, privacy protection (anonymise identifiers), fairness checks (does the metric treat groups equally?) and honest reporting.\n\n"
    "**Why it matters**\nData about people affects people. A biased dataset produces decisions that quietly discriminate.\n\n"
    "**Watch out**\n'Removed names' ≠ anonymous — postcode + birthdate can re-identify individuals.",
    "import pandas as pd\n\ndf = pd.DataFrame({'name': ['riya', 'aarav'], 'email': ['r@x.com', 'a@x.com'], 'score': [85, 92]})\nanonymised = df.drop(columns=['name', 'email']).copy()\nanonymised['student_hash'] = [hash(i) % 10000 for i in range(len(df))]\nprint(anonymised.to_string())   # identifiers gone, analysis still possible",
    ["Why is removing names not enough for anonymity?", "Name two ethical duties of a data scientist", "What is a fairness check?"],
    ["Combinations of indirect fields (location, birthdate) can re-identify people", "Informed consent and honest, bias-checked reporting", "Verifying metrics/outcomes don't systematically disadvantage a group"],
    "Take a small table with personal fields, anonymise it (drop direct identifiers, add a pseudo-id), and print before/after with comments on residual risks.")

_t("Exploratory analysis",
    "**What it is**\nEDA (exploratory data analysis) is the open-minded first look: shape, dtypes, summary stats (.describe()), distributions, correlations, oddities.\n\n"
    "**Why it matters**\nEDA generates the hypotheses and catches the landmines (outliers, leaks, wrong types) before modelling begins.\n\n"
    "**Watch out**\nDon't jump to models first — models trained on unexplored data encode its garbage.",
    "import pandas as pd\n\ndf = pd.DataFrame({'hours': [1, 2, 3, 4, 20], 'score': [52, 58, 65, 72, 95]})\nprint(df.describe().to_string())\nprint('correlation:', round(df['hours'].corr(df['score']), 3))\nprint('max hours looks like an outlier:', round(df['hours'].max() / df['hours'].median(), 2), 'x median')",
    ["List four things EDA examines", "Why EDA before modelling?", "What does .describe() summarise?"],
    ["Size/dtypes, summary statistics, distributions, relationships/correlations, anomalies", "It reveals data problems and patterns that would otherwise be baked into the model", "Count, mean, std, min, quartiles, max per numeric column"],
    "Run a mini-EDA on a 6-row dataset: describe(), one correlation, and one outlier ratio; print all three with a one-line finding each.")

_t("Data cleaning project",
    "**What it is**\nThe phase capstone: take a deliberately messy table (missing values, duplicates, wrong types, invalid ranges) through a documented cleaning pipeline to an analysis-ready result.\n\n"
    "**Why it matters**\nCleaning is 60–80% of real data work. A repeatable pipeline beats one-off fixes.\n\n"
    "**Watch out**\nDocument EVERY transformation — undocumented cleaning is unverifiable cleaning.",
    "import pandas as pd\n\nmessy = pd.DataFrame({'name': ['riya', 'riya', 'aarav', 'kabir'],\n                      'score': ['85', '85', None, '250']})\nmessy['score'] = pd.to_numeric(messy['score'], errors='coerce')\nmessy = messy.drop_duplicates()\nmessy = messy[messy['score'].between(0, 100)]\nmessy['score'] = messy['score'].fillna(messy['score'].mean())\nprint(messy.to_string())\nprint('clean rows:', len(messy))",
    ["Order these steps: fillna, to_numeric, drop_duplicates, range-filter — and justify", "Why document each cleaning step?", "What defines 'analysis-ready'?"],
    ["Convert types first (so comparisons work), then deduplicate, then filter ranges, then fill remaining nulls", "So the pipeline is auditable and rerunnable by anyone", "Correct dtypes, no duplicates, valid ranges, explicit missing-value policy"],
    "Clean a 5-row messy table end-to-end (types → duplicates → ranges → nulls), printing the table after EACH step with a comment explaining it.")

# ============================ PHASE 2: STATISTICS ===========================
_t("Mean median mode",
    "**What it is**\nThree centres: mean = sum/n (sensitive to outliers), median = middle value (robust), mode = most frequent value (works on categories).\n\n"
    "**Why it matters**\nChoosing the wrong centre misleads: average income hides inequality; median house price is the industry standard for exactly this reason.\n\n"
    "**Watch out**\nWith even counts the median is the mean of the two middle values — sort first!",
    "scores = [55, 60, 65, 70, 300]\nmean = sum(scores) / len(scores)\nordered = sorted(scores)\nn = len(ordered)\nmedian = ordered[n//2] if n % 2 else (ordered[n//2 - 1] + ordered[n//2]) / 2\nfrom collections import Counter\nmode = Counter([82, 85, 85, 90]).most_common(1)[0][0]\nprint(mean, median, mode)   # outlier drags mean far above median",
    ["Which centre survives outliers best?", "Median of [1, 3, 5, 7]?", "When is mode the only option?"],
    ["Median", "4 — mean of the two middle values (3+5)/2", "For categorical data (most common category), where mean/median are undefined"],
    "Compute all three centres by hand (no statistics module) for a list containing one extreme outlier; print each and state which you'd report.")

_t("Variance and standard deviation",
    "**What it is**\nVariance = average squared distance from the mean. Std-dev = its square root, back in original units.\n\n"
    "**Why it matters**\nTwo classes can share a mean of 70 with wildly different consistency. Spread tells you about reliability and risk.\n\n"
    "**Watch out**\nPopulation variance divides by n; sample variance divides by n−1 (Bessel's correction). Know which one your formula uses.",
    "scores = [60, 65, 70, 75]\nmean = sum(scores) / len(scores)\npop_var = sum((s - mean)**2 for s in scores) / len(scores)\nsample_var = sum((s - mean)**2 for s in scores) / (len(scores) - 1)\nprint('population sd:', round(pop_var ** 0.5, 2))\nprint('sample sd:   ', round(sample_var ** 0.5, 2))",
    ["Why square deviations instead of averaging them raw?", "Why does std-dev beat variance for reporting?", "n vs n−1 divisor — which is sample variance?"],
    ["Raw deviations cancel to zero; squaring makes them all positive and weights big misses more", "Variance is in squared units (marks²); std-dev returns to interpretable units", "Dividing by n−1"],
    "Compute population AND sample std-dev for five study-hour values without importing statistics; print both and comment on the difference.")

_t("Distributions",
    "**What it is**\nA distribution describes which values occur how often. The normal (bell) curve appears everywhere via averaging; skewed distributions drag their tail one way.\n\n"
    "**Why it matters**\nThe distribution decides which statistics are honest: mean±sd fits symmetric data; median+quartiles fit skewed data.\n\n"
    "**Watch out**\nIncome, response times and file sizes are famously right-skewed — means overstate the 'typical' case.",
    "import random\nrandom.seed(1)\n# Summing dice approximates a normal curve (central limit theorem in action)\nrolls = [sum(random.randint(1, 6) for _ in range(3)) for _ in range(2000)]\nmean = sum(rolls) / len(rolls)\nbins = {}\nfor r in rolls:\n    bins[r] = bins.get(r, 0) + 1\nfor value in sorted(bins):\n    bar = '#' * (bins[value] // 10)\n    print(f'{value:>2} | {bar}')\nprint('mean:', round(mean, 2), '- bell-shaped around it')",
    ["What shape do sums of many random draws tend toward?", "Which summary suits right-skewed data?", "How would you eyeball a distribution without charts?"],
    ["Approximately normal (Central Limit Theorem)", "Median with quartiles — the long tail inflates the mean", "A frequency table / ASCII histogram like this one"],
    "Simulate 1000 sums of two dice, build a frequency table, print an ASCII histogram, and state whether it looks normal or skewed.")

_t("Sampling",
    "**What it is**\nSampling studies a subset to learn about the whole. Random sampling gives every member equal chance, so the sample estimates the population unbiasedly.\n\n"
    "**Why it matters**\nYou almost never get all the data. Polls, A/B tests and quality checks are all sampling arguments.\n\n"
    "**Watch out**\nConvenience samples (your friends, voluntary surveys) carry selection bias no formula can fix.",
    "import random\nrandom.seed(7)\npopulation = [f'student_{i}' for i in range(100)]\nsample = random.sample(population, 10)\nprint('sampled:', sample[:3], '...')\nprint('sample size:', len(sample), 'of', len(population))\nprint('every student had an equal chance -> unbiased estimate')",
    ["Why does randomness make samples trustworthy?", "What bias does a voluntary survey have?", "Sample vs census — when must you sample?"],
    ["Equal chance means no systematic group is over- or under-represented on average", "Selection bias: only motivated/opinionated people respond", "When measuring everyone is impossible or too costly"],
    "Simulate a population of 50 with known average score, draw random samples of 10 five times, and print how close each sample mean lands to the true mean.")

_t("Probability",
    "**What it is**\nP(event) = favourable outcomes / total equally-likely outcomes, from 0 (impossible) to 1 (certain). Independent events multiply: P(A and B) = P(A)·P(B).\n\n"
    "**Why it matters**\nProbability underpins A/B tests, risk estimates and every model that outputs 'likelihood'.\n\n"
    "**Watch out**\nP(A or B) = P(A)+P(B)−P(A and B); forgetting the subtraction double-counts overlaps.",
    "# P(sum=7 with two dice): 6 favourable of 36 outcomes\nfavourable = [(a, b) for a in range(1, 7) for b in range(1, 7) if a + b == 7]\np_seven = len(favourable) / 36\np_two_independent = p_seven * p_seven   # two independent rounds both hitting 7\nprint(round(p_seven, 4), round(p_two_independent, 5))",
    ["State the basic probability formula", "P(heads then heads) with a fair coin?", "Why subtract P(A and B) in P(A or B)?"],
    ["Favourable outcomes ÷ total equally likely outcomes", "0.25 — independence multiplies: 0.5 × 0.5", "Outcomes satisfying BOTH get counted twice otherwise"],
    "Count favourable outcomes for P(doubles with two dice), compute it exactly, simulate 10,000 rolls, and print theory vs simulation side by side.")

_t("Correlation",
    "**What it is**\nCorrelation (−1 to +1) measures linear association: +1 perfect upward line, 0 no linear relation, −1 perfect downward.\n\n"
    "**Why it matters**\nIt's the first question of bivariate analysis: do hours studied and scores move together?\n\n"
    "**Watch out**\nCorrelation ≠ causation, it only captures LINEAR relations (plot U-shaped data and r≈0 despite strong dependence), and outliers can manufacture it.",
    "hours =  [1, 2, 3, 4, 5]\nscores = [52, 58, 65, 72, 78]\nn = len(hours)\nmx, my = sum(hours)/n, sum(scores)/n\ncov = sum((x-mx)*(y-my) for x, y in zip(hours, scores))\nr = cov / ((sum((x-mx)**2 for x in hours) * sum((y-my)**2 for y in scores)) ** 0.5)\nprint('r =', round(r, 3))   # near +1: strong positive linear relation",
    ["What does r = −0.9 describe?", "Give one dataset pair with high correlation but no causation", "Why can U-shaped data show r ≈ 0?"],
    ["A strong negative linear relation — as one rises the other falls", "Ice-cream sales vs drowning deaths (both driven by summer heat)", "Pearson r only measures straight-line fit; symmetric curves cancel out"],
    "Compute Pearson r BY HAND for two small variables, then deliberately inject one huge outlier and print how much r moved.")

_t("Confounding",
    "**What it is**\nA confounder is a hidden variable driving both X and Y, faking or masking their apparent relationship.\n\n"
    "**Why it matters**\n'Coffee drinkers have more heart disease' may really be 'smokers drink more coffee'. Acting on confounded findings causes real harm.\n\n"
    "**Watch out**\nThe fix is design (control groups, stratification), not cleverer statistics after the fact.",
    "# Stratify by the suspected confounder: exercise level\nlow_ex  = {'coffee': True,  'heart_rate': 80}\nhigh_ex = {'coffee': False, 'heart_rate': 62}\ngroups = {'exercises-little': low_ex, 'exercises-a-lot': high_ex}\nfor label, g in groups.items():\n    print(label, '-> resting heart rate', g['heart_rate'])\nprint('within each stratum the coffee effect shrinks: exercise was the driver')",
    ["Define a confounder in one sentence", "How does stratification expose confounding?", "Give a famous confounded correlation"],
    ["A third variable influencing both the supposed cause and effect", "Compare X–Y within each level of the confounder; a real effect persists, a confounded one collapses", "Shoe size ↔ reading skill in children (age confounds both)"],
    "Build a tiny example where X–Y look related overall but within-stratum comparison kills the link; print both views and explain in comments.")

_t("Hypothesis tests",
    "**What it is**\nA test asks: could this difference be luck? State H₀ (no effect), compute a statistic from data, get a p-value = probability of seeing data this extreme IF H₀ were true.\n\n"
    "**Why it matters**\n'A/B went up 3%' is meaningless until luck is excluded. Tests quantify the doubt.\n\n"
    "**Watch out**\np-value is NOT the probability H₀ is true, and non-significant ≠ proven-equal.",
    "import random\nrandom.seed(3)\na = [random.gauss(70, 8) for _ in range(30)]\nb = [random.gauss(73, 8) for _ in range(30)]\ndiff = sum(b)/len(b) - sum(a)/len(a)\n# Permutation test: shuffle labels, see how often chance beats the observed gap\ncombined = a + b\nextreme = 0\nfor _ in range(2000):\n    random.shuffle(combined)\n    pa, pb = combined[:30], combined[30:]\n    if abs(sum(pb)/30 - sum(pa)/30) >= abs(diff):\n        extreme += 1\np_value = extreme / 2000\nprint(f'observed diff {diff:.2f}, permutation p ~= {p_value:.3f}')",
    ["What exactly is a p-value?", "State H₀ for an A/B test", "Two common misreadings of p-values?"],
    ["The probability of data at least this extreme, assuming H₀ is true", "'Both variants have the same true average'", "Reading it as P(H₀ true); treating p>0.05 as proof of no effect"],
    "Run a permutation test comparing two score lists, print the observed gap and p-value, and write a comment stating your conclusion in plain words.")

_t("Confidence intervals",
    "**What it is**\nA 95% CI is a range built so that the same procedure captures the true value 95% of the time: estimate ± margin (margin ∝ spread/√n).\n\n"
    "**Why it matters**\nPoint estimates lie by omission — 'average 72' hides whether that's 72±1 or 72±15. CIs show precision honestly.\n\n"
    "**Watch out**\nQuadrupling data only halves the margin (√n law) — precision is expensive.",
    "import random, math\nrandom.seed(11)\nsample = [random.gauss(70, 10) for _ in range(40)]\nmean = sum(sample)/len(sample)\nsd = (sum((x-mean)**2 for x in sample)/(len(sample)-1)) ** 0.5\nmargin = 1.96 * sd / math.sqrt(len(sample))\nprint(f'mean = {mean:.1f}, 95% CI = ({mean-margin:.1f}, {mean+margin:.1f})')",
    ["Interpret '95% CI' correctly", "What happens to the margin when n quadruples?", "What two ingredients set CI width?"],
    ["The procedure covers the true value in ~95% of repeated samples — not a 95% probability for THIS interval", "It halves (margin scales with 1/√n)", "Data spread (sd) and sample size (n)"],
    "Compute a 95% CI by hand for a simulated sample, then recompute for n=160 and print both margins to demonstrate the √n effect.")

_t("A/B tests",
    "**What it is**\nRandomly split users into variants (A control, B change), measure one pre-declared metric, and test whether the difference exceeds noise.\n\n"
    "**Why it matters**\nA/B testing is causal inference in production: randomisation neutralises confounders by construction.\n\n"
    "**Watch out**\nPeeking early and stopping at the first significant reading inflates false positives; decide duration in advance.",
    "import random\nrandom.seed(5)\ndef variant(cr):\n    return [1 if random.random() < cr else 0 for _ in range(500)]\na, b = variant(0.10), variant(0.13)\nrate_a, rate_b = sum(a)/len(a), sum(b)/len(b)\nlift = rate_b - rate_a\nprint(f'A: {rate_a:.3f}  B: {rate_b:.3f}  lift: {lift:+.3f}')\nprint('decision needs a significance test on this lift, not the raw number alone')",
    ["Why does randomisation enable causal claims?", "Name two A/B testing sins", "What should be fixed BEFORE starting?"],
    ["It balances known and unknown confounders across groups on average", "Peek-and-stop early; running many metrics and cherry-picking", "One primary metric, sample size, and run duration"],
    "Simulate an A/B test with a small true lift, print both conversion rates and the lift, and comment what extra evidence you'd need before shipping B.")

_t("Outliers",
    "**What it is**\nOutliers are points far from the bulk of data. Detect with IQR rule (outside Q1−1.5·IQR, Q3+1.5·IQR) or z-scores (>3 sd).\n\n"
    "**Why it matters**\nThey wreck means, correlations and fitted lines — sometimes they're errors, sometimes they're the story (fraud, breakout students).\n\n"
    "**Watch out**\nNever delete silently: investigate, document, and justify each removal.",
    "def iqr_bounds(values):\n    ordered = sorted(values)\n    def q(p):\n        idx = int(p * (len(ordered) - 1))\n        return ordered[idx]\n    q1, q3 = q(0.25), q(0.75)\n    iqr = q3 - q1\n    return q1 - 1.5*iqr, q3 + 1.5*iqr\n\nscores = [55, 60, 62, 65, 68, 70, 900]\nlo, hi = iqr_bounds(scores)\noutliers = [v for v in scores if v < lo or v > hi]\nprint('bounds:', lo, hi, '| outliers:', outliers)",
    ["State the IQR outlier rule", "When might an outlier be kept?", "Effect of one outlier on mean vs median?"],
    ["Flag values outside [Q1−1.5·IQR, Q3+1.5·IQR]", "When it's genuine and important — fraud detection exists because of outliers", "Mean moves a lot; median barely at all"],
    "Detect outliers in a list using the IQR rule, print them, then print mean and median before/after removing the outlier and compare.")

_t("Skewness",
    "**What it is**\nSkew measures asymmetry: right-skew = long tail of large values (income, load times), left-skew = long tail of small values (easy exam scores).\n\n"
    "**Why it matters**\nSkewed data breaks the mean±sd mental model and many test assumptions; transformations (log) often restore symmetry.\n\n"
    "**Watch out**\nIn right-skewed data: mean > median. That ordering is a quick skew detector.",
    "import random, math\nrandom.seed(2)\nright_skewed = [min(100, random.expovariate(1/20)) for _ in range(500)]  # exponential-ish\nmean = sum(right_skewed)/len(right_skewed)\nmedian = sorted(right_skewed)[250]\nprint(f'mean {mean:.1f} vs median {median:.1f} -> mean > median means right skew')\nlogged = [round(math.log1p(v), 2) for v in right_skewed[:5]]\nprint('log-transform tames the tail:', logged)",
    ["Tail on the right — which skew?", "Quick mean/median skew heuristic?", "Common fix for right-skewed positive data?"],
    ["Right (positive) skew", "mean > median → right skew; mean < median → left skew", "Log transform (log1p handles zeros)"],
    "Generate right-skewed data, print mean vs median to diagnose direction, apply log1p, and print how much closer the transformed mean sits to its median.")

_t("Statistical storytelling",
    "**What it is**\nTurning analysis into narrative: context → finding → evidence → caveat → recommendation. One chart, one message.\n\n"
    "**Why it matters**\nStakeholders act on stories, not tables. Same numbers, framed honestly, drive good decisions.\n\n"
    "**Watch out**\nTruncated axes and cherry-picked windows are storytelling lies — persuasion must survive scrutiny.",
    "report = {\n    'context': 'Study-hours pilot, 40 students, 4 weeks',\n    'finding': 'Students studying 3h+ scored 12 points higher on average',\n    'evidence': 'difference 12.1 pts, permutation p ~= 0.02, CI (3, 21)',\n    'caveat': 'self-reported hours; observational, not causal',\n    'recommendation': 'run a randomised trial before mandating study hours',\n}\nfor section, text in report.items():\n    print(f'{section.upper()}: {text}')",
    ["List the five story sections in order", "Why include caveats in a persuasive report?", "Give one example of misleading chartcraft"],
    ["Context, finding, evidence, caveat, recommendation", "Honest limitations protect credibility and prevent misuse of the result", "Y-axis truncated so a tiny difference looks dramatic"],
    "Write a five-section mini-report dict for any finding from earlier lessons and print it formatted; ensure the caveat names one real limitation.")

_t("Study design",
    "**What it is**\nDesign happens BEFORE data collection: define the question, population, sampling method, variables, metric and analysis plan up front.\n\n"
    "**Why it matters**\nNo analysis rescues bad collection. A pre-registered plan also stops post-hoc cherry-picking.\n\n"
    "**Watch out**\nAmbiguous metrics ('engagement') doom projects — operationalise everything numerically.",
    "design = {\n    'question': 'Does spaced practice beat massed practice?',\n    'population': 'first-year PySchool learners',\n    'sampling': 'random assignment to two arms',\n    'variables': {'arm': 'spaced|massed', 'outcome': 'day-14 test score'},\n    'metric': 'mean score difference',\n    'analysis_plan': 'permutation test, alpha 0.05, n=100',\n}\nfor key, value in design.items():\n    print(f'{key}: {value}')",
    ["Why fix the analysis plan before collecting data?", "Operationalise 'engagement'", "Random assignment fixes what problem?"],
    ["To prevent post-hoc cherry-picking and guarantee a valid test exists", "E.g. 'distinct active days per week' — a countable definition", "Confounding between treatment and participant characteristics"],
    "Write a complete six-field study-design dict for a question you invent, print it, and mark which field guards against cherry-picking.")

_t("Statistics project",
    "**What it is**\nPhase capstone: take one question through the full statistical pipeline — design, sample/simulate, describe, test, interval, conclude honestly.\n\n"
    "**Why it matters**\nIsolated techniques don't answer questions; pipelines do. This mirrors real analyst work end-to-end.\n\n"
    "**Watch out**\nThe conclusion must match the evidence strength — 'suggests' vs 'proves' matter.",
    "import random, math\nrandom.seed(42)\ncontrol  = [random.gauss(64, 9) for _ in range(50)]\ntreated  = [random.gauss(67, 9) for _ in range(50)]\nm = lambda xs: sum(xs)/len(xs)\nsd = lambda xs: (sum((x - m(xs))**2 for x in xs)/(len(xs)-1)) ** 0.5\ndiff = m(treated) - m(control)\nse = (sd(treated)**2/50 + sd(control)**2/50) ** 0.5\nci = (diff - 1.96*se, diff + 1.96*se)\nprint(f'mean diff = {diff:.2f}, 95% CI = ({ci[0]:.2f}, {ci[1]:.2f})')\nverdict = 'likely real improvement' if ci[0] > 0 else 'cannot rule out no effect'\nprint('conclusion:', verdict)",
    ["Order the pipeline stages used here", "Why report a CI alongside the difference?", "When may you say 'proves'?"],
    ["Design → simulate/sample → summarise → estimate with uncertainty → conclude", "The point estimate alone hides the uncertainty; the CI shows plausible range", "Almost never outside mathematics — experiments give 'strong evidence', not proof"],
    "Run the full pipeline on your own two-group question: simulate, compute means, pooled SE, 95% CI, and print a one-line honest conclusion.")
