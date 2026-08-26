"""Data Science topics — Phases 3–7 (Visualization, Predictive Modelling,
Evaluation & Deployment, Applied Projects, Capstone). Merged into
DS_TOPIC_LIBRARY by ds_topic_library.py."""

PHASE_3_TO_7: dict[str, dict] = {}

def _t(topic, theory, code, questions, answers, homework):
    PHASE_3_TO_7[topic] = {
        "theory": theory, "code": code,
        "questions": questions, "answers": answers, "homework": homework,
    }

# ============================ PHASE 3: VISUALIZATION ========================
_t("Chart selection",
    "**What it is**\nMatch chart to question: trend over time → line; compare categories → bar; distribution → histogram; relationship → scatter; part-of-whole (few slices) → pie/stacked bar.\n\n"
    "**Why it matters**\nThe wrong chart hides the answer. Pie charts with 12 slices and line charts of unordered categories are classic failures.\n\n"
    "**Watch out**\nTime belongs on the x-axis of line charts; bar charts need a zero baseline or they lie.",
    "def recommend_chart(question):\n    rules = [\n        ('trend over time', 'line chart'),\n        ('compare categories', 'bar chart'),\n        ('distribution of one variable', 'histogram'),\n        ('relationship between two variables', 'scatter plot'),\n        ('parts of a whole', 'stacked bar (or pie if <=5 slices)'),\n    ]\n    for key, chart in rules:\n        if key in question.lower():\n            return chart\n    return 'start with a histogram - see the shape first'\n\nfor q in ['trend over time of scores', 'relationship between hours and score']:\n    print(q, '->', recommend_chart(q))",
    ["Best chart for monthly revenue across a year?", "Why must bar charts start at zero?", "First chart for an unknown dataset?"],
    ["Line chart", "Bar length encodes value; a non-zero baseline distorts ratios", "A histogram — shape guides everything else"],
    "Write your own recommend_chart function with at least four rules, test it on three questions, and print each recommendation.")

_t("Matplotlib basics",
    "**What it is**\nmatplotlib's mental model: a Figure (canvas) containing Axes (one plot). plt.plot/plt.bar draw onto current axes; plt.show() renders.\n\n"
    "**Why it matters**\nEvery Python visualisation library builds on this model. Master figure/axes and Seaborn/Plotly become trivial.\n\n"
    "**Watch out**\nIn scripts you must call plt.show(); in notebooks plots often auto-render, hiding the model from you.",
    "# Real usage (pip install matplotlib):\n# import matplotlib.pyplot as plt\n# fig, ax = plt.subplots()\n# ax.plot([1, 2, 3], [52, 65, 78], marker='o')\n# ax.set_title('Score by study day')\n# plt.show()\ndays = [1, 2, 3]\nscores = [52, 65, 78]\nwidth = max(scores)\nfor d, s in zip(days, scores):\n    print(f'day {d} | ' + '#' * (s * 40 // width) + f' {s}')\nprint('(ASCII preview of what ax.plot draws: scores rising over days)')",
    ["Figure vs Axes — which contains which?", "What does plt.subplots() return?", "Why might your plot not appear in a script?"],
    ["A Figure contains one or more Axes", "A (fig, ax) pair — one fresh canvas with one axes", "You forgot plt.show()"],
    "Write the real matplotlib code as comments AND run an ASCII version for a bar chart of three subjects; both must show the same data.")

_t("Line charts",
    "**What it is**\nLine charts connect ordered points — ideal when x is time or another continuous order. Markers show actual observations.\n\n"
    "**Why it matters**\nTrends, seasonality and turning points are only visible when order is preserved.\n\n"
    "**Watch out**\nNever sort away the time axis to 'make the line pretty'; uneven gaps in time should ideally use datetime x-values.",
    "weeks = [1, 2, 3, 4]\nstreak = [2, 4, 3, 6]\npeak = streak.index(max(streak))\nfor w, s in zip(weeks, streak):\n    print(f'week {w} | ' + '#' * s + f' {s}')\nprint(f'trend: rising overall, dip at week {weeks[2]}, peak at week {weeks[peak]}')",
    ["When is a line chart wrong?", "Why add markers?", "What does a sudden slope change reveal?"],
    ["For unordered categories — use bars instead", "They distinguish observed data points from interpolated segments", "A regime change: something altered the underlying process"],
    "Plot a 6-week ASCII line of any metric, then print two sentences describing its trend and sharpest change.")

_t("Bar charts",
    "**What it is**\nBars encode values as lengths for comparing categories. Horizontal bars fit long labels; sorting bars by value adds instant insight.\n\n"
    "**Why it matters**\nLength perception is accurate — humans judge bar comparisons better than angles or areas.\n\n"
    "**Watch out**\nAlways start at zero; unsorted bars waste the reader's attention hunting for the max.",
    "subjects = {'maths': 85, 'code': 92, 'art': 71}\nfor name, mark in sorted(subjects.items(), key=lambda kv: -kv[1]):\n    print(f'{name:>6} | ' + '#' * (mark // 5) + f' {mark}')\nbest = max(subjects, key=subjects.get)\nprint('sorted descending -> best subject jumps out:', best)",
    ["Horizontal vs vertical bars — when prefer horizontal?", "Why sort bars?", "Grouped vs stacked bars?"],
    ["Long category labels; horizontal leaves room for text", "Sorted bars let readers rank instantly without scanning", "Grouped compares series side-by-side; stacked shows composition per category"],
    "Draw a sorted horizontal ASCII bar chart of at least four categories and print one sentence naming the top and bottom entries.")

_t("Histograms",
    "**What it is**\nHistograms bin a numeric variable and count per bin — revealing centre, spread, skew and multimodality.\n\n"
    "**Why it matters**\nThe distribution's SHAPE decides your statistics (mean vs median) and models later.\n\n"
    "**Watch out**\nBin width changes the story: too few bins hide peaks, too many amplify noise. Try several.",
    "import random\nrandom.seed(9)\nvalues = [random.gauss(70, 8) for _ in range(300)]\nbins = {}\nfor v in values:\n    b = int(v // 10) * 10       # 10-wide bins\n    bins[b] = bins.get(b, 0) + 1\nfor start in sorted(bins):\n    print(f'{start:>3}-{start+9:<3}| ' + '#' * (bins[start] // 2))\nprint('shape: single bell centred near 70')",
    ["Histogram vs bar chart — core difference?", "Effect of too few bins?", "What does a second peak suggest?"],
    ["Histograms bin continuous ranges; bars compare discrete categories", "Distinct peaks merge into one blob — structure disappears", "A mixture of two populations (e.g. two different user types)"],
    "Histogram 400 simulated values twice — once with wide bins, once narrow — print both, and comment which reveals more.")

_t("Scatter plots",
    "**What it is**\nEach point is one observation's (x, y) pair — the direct view of relationships between two numeric variables.\n\n"
    "**Why it matters**\nScatters reveal linear trends, curves, clusters and outliers that correlation numbers compress away.\n\n"
    "**Watch out**\nOverplotting (thousands of points) hides density — use transparency or sample down.",
    "hours =   [1, 2, 2, 3, 4, 4, 5, 6]\nscores =  [50, 55, 62, 60, 70, 74, 75, 88]\nfor h, s in zip(hours, scores):\n    row = ['.'] * 10\n    col = min(int((s - 45) / 5), 9)\n    row[col] = 'o'\n    print(f'{h}h |' + ''.join(row))\nprint('points climb left-to-right: positive association visible')",
    ["What can a scatter show that r cannot?", "How do you fight overplotting?", "What do clusters in a scatter hint at?"],
    ["Curvature, clusters, outliers — the functional form of the relation", "Alpha transparency, smaller markers, or random sampling", "Latent subgroups worth segmenting before analysis"],
    "ASCII-scatter eight (x, y) pairs including one obvious outlier, print it, and write one sentence on the trend plus one on the outlier.")

_t("Subplots",
    "**What it is**\nplt.subplots(rows, cols) creates a grid of axes; draw each view into its own ax — small multiples of related views share one figure.\n\n"
    "**Why it matters**\nSide-by-side panels make comparisons honest (same scales!) without flipping between images.\n\n"
    "**Watch out**\nShare y-axes when comparing magnitudes; independent scales silently mislead.",
    "groups = {'morning': [60, 65, 70], 'evening': [72, 75, 90]}\nfor name, values in groups.items():\n    scale = max(values)          # shared scale = honest comparison\n    print(f'--- {name} ---')\n    for i, v in enumerate(values):\n        print(f'  p{i+1} | ' + '#' * (v * 20 // scale) + f' {v}')\nprint('same 0-max scale on both panels keeps the comparison fair')",
    ["Why use subplots instead of separate figures?", "What does sharey=True enforce?", "Name a good small-multiples use case"],
    ["Eyes compare panels within one view far better than across scrolled images", "Identical y-scales across all panels", "One histogram per category, stacked in a grid"],
    "Render two ASCII panels (two groups) with a SHARED scale, then re-render with independent scales and comment how the impression changes.")

_t("Labels and legends",
    "**What it is**\nEvery chart needs: axis labels WITH units, a title stating the takeaway, legends distinguishing multiple series, and source notes where relevant.\n\n"
    "**Why it matters**\nAn unlabelled chart transfers nothing — the reader guesses units, series and meaning.\n\n"
    "**Watch out**\nTitles should state findings ('Scores rise ~7 pts/hour') not just topics ('Hours vs Score').",
    "chart_meta = {\n    'title': 'Study hours predict mock-exam scores (n=8)',\n    'x_label': 'Self-study hours per week',\n    'y_label': 'Mock exam score (0-100)',\n    'legend': ['observed students'],\n}\nfor key, value in chart_meta.items():\n    print(f'{key}: {value}')\nassert 'score' in chart_meta['y_label'].lower() and '(0-100)' in chart_meta['y_label']\nprint('units present: label checklist passed')",
    ["Three mandatory elements of any published chart", "Good title vs bad title?", "When is a legend required?"],
    ["Labelled axes with units, informative title, legend when >1 series", "'Scores rise ~7 pts per study hour' beats 'Hours vs Score'", "Whenever two or more series share the same axes"],
    "Build a metadata dict for any earlier chart ensuring the title states a finding and both axis labels carry units; assert-check it and print it.")

_t("Color and accessibility",
    "**What it is**\nAccessible colour: sufficient contrast, colour-blind-safe palettes (avoid pure red+green), never encoding meaning in hue alone — add shapes/labels/patterns.\n\n"
    "**Why it matters**\n~8% of men have colour-vision deficiency. Inaccessible charts exclude them and often print badly in grayscale.\n\n"
    "**Watch out**\nSequential data wants sequential palettes (light→dark); categorical data wants distinct hues — don't mix them up.",
    "palette = {'up': 'blue + triangle marker', 'down': 'orange + X marker'}\nfor meaning, encoding in palette.items():\n    print(f'{meaning}: encoded by {encoding}')\nassert all('marker' in e for e in palette.values()), 'never hue alone'\nprint('dual encoding: readable in grayscale and for colour-blind readers')",
    ["Why avoid red/green pairs?", "Two ways to encode beyond hue?", "Which palette type fits ordinal data?"],
    ["Red-green deficiency is the most common colour-vision issue", "Marker shapes, line styles, direct labels, patterns", "A sequential gradient (light→dark)"],
    "Define encodings for a 3-category chart using colour PLUS shape plus label, assert no category relies on hue alone, and print the legend spec.")

_t("Seaborn",
    "**What it is**\nSeaborn sits on matplotlib and binds DataFrames to statistical graphics: sns.histplot(df, x=...), sns.boxplot, sns.scatterplot with hue= for instant grouping.\n\n"
    "**Why it matters**\nOne line replaces ten: aggregation, styling and legends come free because seaborn understands pandas columns.\n\n"
    "**Watch out**\nIt's still matplotlib underneath — customising means mixing both APIs (sns draws, ax formats).",
    "# Real usage (requires pip install seaborn):\n# import seaborn as sns\n# sns.boxplot(data=df, x='subject', y='score')\n# sns.lmplot(data=df, x='hours', y='score', hue='group')\nimport statistics\ngroups = {'a': [60, 62, 91, 63], 'b': [70, 72, 73, 74]}\nfor name, vals in groups.items():\n    print(f'boxplot({name}): median={statistics.median(vals)}')\nprint('seaborn draws exactly this summary, straight from DataFrame columns')",
    ["What does hue= add to a seaborn plot?", "Why does seaborn need less code than raw matplotlib?", "Which seaborn call shows distributions per group?"],
    ["Automatic colour-splitting by a categorical column, with legend", "It maps DataFrame column names directly to plot roles", "sns.boxplot(data=df, x='group', y='value')"],
    "Compute boxplot-style medians for two groups in pure Python, print them, and write the equivalent one-line seaborn calls as comments.")

_t("Distribution plots",
    "**What it is**\nBeyond histograms: KDE (smooth density curve), boxplots (median/quartiles/outliers), violin plots (boxplot + mirrored density).\n\n"
    "**Why it matters**\nDifferent displays expose different features — KDE shows smooth shape, boxplots nail medians and outliers for comparison.\n\n"
    "**Watch out**\nKDE bandwidth can invent bumps that aren't there; always sanity-check against a plain histogram.",
    "import statistics\nscores_a = [55, 60, 62, 65, 68, 95]\ndef five_number(vals):\n    ordered = sorted(vals)\n    n = len(ordered)\n    return ordered[0], ordered[n//4], statistics.median(ordered), ordered[3*n//4], ordered[-1]\nlo, q1, med, q3, hi = five_number(scores_a)\niqr = q3 - q1\noutliers = [v for v in scores_a if v < q1 - 1.5*iqr or v > q3 + 1.5*iqr]\nprint(f'min={lo} Q1={q1} median={med} Q3={q3} max={hi} outliers={outliers}')",
    ["What extra info does a violin give over a boxplot?", "Which plot best compares medians across many groups?", "KDE danger?"],
    ["The full density shape (multimodality) around the box summary", "Boxplots — one compact row per group", "Smoothing can fabricate peaks; verify with a histogram"],
    "Compute a five-number summary plus IQR outliers for two datasets, print both, and state which display (box/violin/KDE) you'd publish and why.")

_t("Categorical plots",
    "**What it is**\nPlots for category-vs-number questions: bar plots of aggregated values, count plots of frequencies, grouped splits by a second category (hue).\n\n"
    "**Why it matters**\n'Marks per subject, split by gender' style questions dominate stakeholder requests.\n\n"
    "**Watch out**\nAggregating first (groupby) then plotting plain bars is clearer — and faster — than statistical bar plots with hidden bootstraps.",
    "from collections import defaultdict\nrows = [('maths', 'girl', 85), ('maths', 'boy', 78), ('code', 'girl', 92), ('code', 'boy', 88)]\ntotals, counts = defaultdict(int), defaultdict(int)\nfor subject, gender, mark in rows:\n    totals[(subject, gender)] += mark\n    counts[(subject, gender)] += 1\nfor key in sorted(totals):\n    avg = totals[key] / counts[key]\n    print(f'{key[0]:>5} {key[1]}: avg {avg:.0f} | ' + '#' * int(avg // 5))",
    ["Count plot vs bar plot?", "Why aggregate with groupby before plotting?", "What does hue= encode in categorical plots?"],
    ["Count plot tallies raw occurrences; bar plot shows an aggregated statistic like mean", "Explicit aggregation is transparent about what's plotted and avoids surprise resampling", "A second categorical dimension"],
    "Aggregate a mixed list of records into per-(category, subgroup) averages, print sorted ASCII bars, and name the highest cell.")

_t("Dashboard thinking",
    "**What it is**\nDashboards arrange 3–6 purposeful views answering standing questions at a glance: one headline number, one trend, one breakdown, one detail table.\n\n"
    "**Why it matters**\nDashboards are read repeatedly by decision-makers — layout and focus matter as much as each chart.\n\n"
    "**Watch out**\nMore tiles ≠ better. Every tile must answer a named recurring question or it's noise.",
    "dashboard = {\n    'headline': {'tile': 'avg score this week', 'value': 76},\n    'trend':    {'tile': 'weekly avg, 6 weeks', 'spark': [64, 66, 70, 69, 73, 76]},\n    'breakdown':{'tile': 'avg by subject', 'values': {'maths': 74, 'code': 81}},\n}\nprint('HEADLINE:', dashboard['headline']['value'])\nprint('TREND:   ', ' '.join(str(v) for v in dashboard['trend']['spark']))\nfor subject, avg in dashboard['breakdown']['values'].items():\n    print(f'BREAKDOWN {subject}: {avg}')",
    ["Four canonical dashboard tiles?", "Test for whether a tile deserves space?", "Why lead with a headline number?"],
    ["Headline KPI, trend over time, breakdown by category, detail table", "Can you name the recurring question it answers? If not, cut it", "Gives immediate status before details demand attention"],
    "Design a 3-tile dashboard dict for learner progress (headline, sparkline trend, one breakdown), print it rendered, and justify each tile in comments.")

_t("Narrative visuals",
    "**What it is**\nA narrative visual makes ONE point: annotated key events, highlighted focal series while greying context, callouts on the decisive number.\n\n"
    "**Why it matters**\nReports persuade through focus. Annotation directs attention to exactly the evidence supporting your claim.\n\n"
    "**Watch out**\nHighlighting must not distort: greyed context stays visible so the audience can check your reading.",
    "series = [58, 61, 59, 72, 74, 73]\nevent_day = 4   # new study method introduced\nfor day, value in enumerate(series, start=1):\n    marker = ' <-- method changed' if day == event_day else ''\n    emphasis = '###' if day >= event_day else '   '\n    print(f'day {day} | {emphasis}' + '#' * (value // 5) + f' {value}{marker}')\nprint('annotation pins the causal moment; pre/post shading carries the argument')",
    ["Three annotation techniques?", "Why keep context visible when highlighting?", "Where should the annotation point?"],
    ["Event markers, focal-series highlighting, numeric callouts", "Readers must be able to verify the highlighted pattern isn't cherry-picked", "At the exact data point/event your claim depends on"],
    "Render an ASCII series with a marked intervention point and post-event emphasis, then print a one-line claim the visual supports.")

_t("Visualization project",
    "**What it is**\nPhase capstone: take one dataset through chart selection → draft → critique (labels, accessibility, honesty) → final annotated visual with a stated message.\n\n"
    "**Why it matters**\nCharts are edited, not just generated. The critique loop is what separates analysts from plot-callers.\n\n"
    "**Watch out**\nShip the message, not the chart: if a viewer can't repeat your finding after seeing it, revise.",
    "project = {\n    'question': 'Does study consistency beat total hours?',\n    'chart_choice': 'scatter of consistency-score vs test-score',\n    'draft_issues': ['missing units', 'red-green colours', 'no annotation'],\n    'fixes': ['add axis units', 'blue/orange + markers', 'callout on steepest cluster'],\n    'message': 'consistent studiers outperform equal-hour crammers',\n}\nfor stage, content in project.items():\n    print(f'{stage.upper()}: {content}')",
    ["Order the project stages", "Give two critique checks", "What defines project success?"],
    ["Question → chart selection → draft → critique → fixes → final message", "Units present? Colour-safe? Zero baselines? Message stated in title?", "A viewer can restate your finding accurately after one look"],
    "Document a mini viz-project dict (question, chosen chart, two draft flaws, two fixes, final message), print it, and assert the message field is non-empty.")
