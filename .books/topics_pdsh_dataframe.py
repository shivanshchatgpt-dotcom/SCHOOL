"""Canonical topic batch: Series and DataFrame as indexed structures (PDSH ch 13)."""
from canonical_topics import topic

PDSH_CH13 = {
    "book": "python-data-science-handbook",
    "chapter": 13,
    "pages": [147, 157],
    "sections": ["Series as Generalized NumPy Array", "Series as Specialized Dictionary",
                 "DataFrame as Generalized NumPy Array", "DataFrame as Specialized Dictionary",
                 "Constructing DataFrame Objects"],
}


topic(
    "canonical:dataframe-as-indexed-table",
    "A Series is a one-dimensional array with an index and a DataFrame is a table whose columns are Series, so the index is what makes tabular data addressable by name",
    sources=[dict(PDSH_CH13)],
    concept=(
        "A pandas Series is a numpy array with an attached index, which means every value "
        "is reachable by a label as well as by position, and that single addition is what "
        "changes how the object is used. Alignment follows from the index: when two Series "
        "are combined, their values are matched by label rather than by position, so a "
        "missing label becomes a nan instead of a silently misaligned number. A DataFrame "
        "extends this to two dimensions: its columns are named Series sharing one row index, "
        "so a column is selected by name and a row by label, and the whole structure is best "
        "thought of as a dictionary of Series rather than as an array of rows. Constructing "
        "one from a dictionary of lists is the most common route, and the column order then "
        "comes from the dictionary while the row index comes from the lists. The index is a "
        "real object with its own dtype, and it is what distinguishes a row from its "
        "position, a distinction that matters the moment rows are filtered or sorted, "
        "because the labels travel with the data. The practical payoff is that operations "
        "are expressed in terms of what the data is rather than where it sits, and the "
        "practical cost is that forgetting the index is present leads to surprises when "
        "positions and labels disagree."
    ),
    prerequisites=["canonical:ndarray-attributes-and-shape"],
    pitfalls=[
        "Selecting a single column with bracket notation and expecting a DataFrame, when a "
        "single column returns a Series.",
        "Combining two Series and expecting positional alignment, when the values are "
        "matched by index label and a missing label yields nan.",
        "Filtering or sorting rows and then indexing by position as if the original row "
        "numbers still applied, when the labels travel with the rows.",
    ],
    adapters={
        "deep-learning": {
            "framing": (
                "Experiment logs are tables, and a DataFrame is what makes them queryable "
                "after the run instead of during it."
            ),
            "application": (
                "Walk the example as experiment results being collected into a table. Each "
                "run becomes a row with a model name, a learning rate and a score, and the "
                "DataFrame makes it possible to select the score column by name and compare "
                "across runs without bookkeeping. The column-versus-Series detail appears "
                "immediately: selecting one column gives a Series whose index is the run "
                "names, and that object is what a ranking is computed from, while selecting "
                "a list of one column gives a DataFrame, and the difference is a pair of "
                "extra brackets rather than anything semantic. Sorting the score column "
                "reorders the rows while the labels travel with them, which is what makes "
                "the best model identifiable by name. The alignment property matters when "
                "two runs' metrics are combined, because matching by index rather than by "
                "position means a run present in one table and absent in the other produces "
                "a nan rather than a wrong number."
            ),
            "example_hint": "collect runs into a DataFrame, select a column, sort by it and align two tables",
            "assessment_angle": "what selecting a column returns and what index alignment prevents",
            "day": 8,
            "title": "Experiment Logs Are a Table: Select by Name, Sort, Align",
            "code": """import pandas as pd

runs = pd.DataFrame({
    "model": ["baseline", "tuned", "wide", "deep"],
    "lr": [0.01, 0.01, 0.001, 0.01],
    "score": [0.841, 0.873, 0.812, 0.866],
})
runs = runs.set_index("model")

scores = runs["score"]
print("scores is a:", type(scores).__name__)
print(scores)

print("best:", scores.idxmax(), scores.max())

print(runs.sort_values("score", ascending=False))

extra = pd.Series({"tuned": 0.88, "wide": 0.83, "unseen": 0.70}, name="tuned_again")
combined = scores.align(extra)
print("aligned:\\n", combined[0])
print(combined[1])
""",
            "questions": [
                "runs['score'] returns a Series rather than a DataFrame. What would return a DataFrame with one column, and why does the distinction matter?",
                "After sorting by score, how is the best model identified, and why does the model name stay attached to its score?",
                "What does align produce for a run present in one Series and absent from the other?",
            ],
            "answers": [
                "Passing a list of one name, runs[['score']], because the bracket form with a list selects columns and keeps the DataFrame shape, while a single string selects one column and collapses it to a Series.",
                "By calling idxmax on the score column, and the name stays attached because the index labels travel with the values when the rows are sorted rather than being replaced by positions.",
                "A nan in the Series where the label is missing, because alignment matches labels rather than positions, so an absent run has no value to contribute instead of borrowing its neighbour's.",
            ],
            "homework": (
                "Write experiment_table.py that builds a DataFrame from a dictionary of lists for at "
                "least five model runs with a learning rate and a score, sets the model column as the "
                "index, and prints the type and contents of one selected column. Print the best "
                "model's name and score with idxmax and max, print the DataFrame sorted by score "
                "descending, and align the score column with another Series that shares two labels "
                "and adds one new one, printing both aligned results. Observable output: five lines "
                "or blocks."
            ),
            "required_patterns": ["pd.DataFrame", "set_index(", "sort_values(", "idxmax()", "print("],
        },
        "computer-vision": {
            "framing": (
                "Image annotation files are tables: one row per image with its path, labels "
                "and split."
            ),
            "application": (
                "Walk the example as an annotation table being built and inspected. Each "
                "image is a row with a filename, a width, a height and a label, and the "
                "DataFrame makes it possible to ask for the label column by name and count "
                "its values, which is how a class imbalance is discovered before training "
                "begins. The split between position and label appears when the table is "
                "filtered to one class: the resulting rows keep their original labels, so "
                "indexing them by position afterwards is a trap, and the remedy is to "
                "address rows by name or to reset the index deliberately. Selecting a "
                "column as a Series versus a list of one column is the daily question, "
                "since a histogram wants a Series and a display routine wants a DataFrame. "
                "Computing a derived column such as aspect ratio is an expression over two "
                "named columns, and the index alignment is automatic, which is the "
                "convenience that makes tabular preprocessing readable."
            ),
            "example_hint": "build an annotation table, count classes, filter and derive an aspect ratio column",
            "assessment_angle": "what filtering does to row labels and what a derived column costs",
            "day": 8,
            "title": "Annotations Are a Table: Count Classes, Filter, Derive",
            "code": """import pandas as pd

annotations = pd.DataFrame({
    "file": ["a.jpg", "b.jpg", "c.jpg", "d.jpg", "e.jpg"],
    "width": [640, 1920, 800, 640, 1920],
    "height": [480, 1080, 600, 480, 1080],
    "label": ["cat", "dog", "cat", "bird", "cat"],
})

print(annotations["label"].value_counts())

annotations["aspect"] = annotations["width"] / annotations["height"]
print(annotations[["file", "aspect"]])

cats = annotations[annotations["label"] == "cat"]
print("cat rows:")
print(cats)
print("position 0 is:", cats.iloc[0]["file"], "not the first original row")

wide = annotations[annotations["aspect"] > 1.5]
print("wide images:", wide["file"].tolist())
""",
            "questions": [
                "After filtering to cats, why does the first row of the result not correspond to the first row of the original table?",
                "The aspect column is computed from two named columns in one expression. What makes that work without any explicit loop or index arithmetic?",
                "What do value_counts and the filtered wide list each report about the dataset?",
            ],
            "answers": [
                "Because filtering keeps the original index labels, so the filtered table's first row is the first surviving row, whose label is whatever its position in the original table was, not zero.",
                "The two Series share the same row index, so the division aligns them label by label automatically and produces a new Series with the same index.",
                "Value counts reports how many images each class has, and the filtered list reports which filenames satisfy the aspect condition.",
            ],
            "homework": (
                "Write annotation_table.py that builds a DataFrame of at least six images with file, "
                "width, height and label columns and prints the label value counts. Derive an aspect "
                "column from width and height and print the file and aspect columns, then filter to "
                "one class and print the rows with their original labels, and print the filename at "
                "position zero of the filtered frame noting it is not the original first row. Finally "
                "filter by a condition on the derived column and print the matching filenames as a "
                "list. Observable output: five lines or blocks."
            ),
            "required_patterns": ["pd.DataFrame", "value_counts()", ".iloc[0]", "annotations[", "print("],
        },
        "nlp": {
            "framing": (
                "A corpus is a table of documents with metadata, and a DataFrame is what "
                "makes corpus-level statistics a one-liner."
            ),
            "application": (
                "Walk the example as a corpus being loaded into a table. Each document is a "
                "row with an identifier, its text, a language and a length, and the "
                "DataFrame makes it possible to group by language and compare lengths, "
                "which is how a corpus's composition is understood before modelling. The "
                "index-as-identity point appears concretely: setting the document "
                "identifier as the index makes a selected document reachable by name, and "
                "after filtering the identifiers travel with the rows, so a lookup by "
                "label is stable while a positional lookup is not. Deriving a length "
                "column from the text column is an expression over named columns, and the "
                "value is that the pipeline reads as a description of the data rather than "
                "as index arithmetic. Selecting one column gives a Series whose values can "
                "be described statistically, while a list of columns keeps the table shape "
                "for export, and choosing between them is a constant practical decision."
            ),
            "example_hint": "load a corpus into a DataFrame, index it by document id, derive lengths and group",
            "assessment_angle": "what indexing by identifier makes stable and what a grouped statistic reports",
            "day": 8,
            "title": "A Corpus Is a Table: Index by Id, Derive, Group",
            "code": """import pandas as pd

corpus = pd.DataFrame({
    "doc": ["d1", "d2", "d3", "d4", "d5"],
    "text": ["the quick fox", "le renard vite", "a slow turtle", "the lazy dog", "un chien"],
    "lang": ["en", "fr", "en", "en", "fr"],
})
corpus["length"] = corpus["text"].str.split().str.len()
corpus = corpus.set_index("doc")

print(corpus)
print("languages:", corpus["lang"].value_counts().to_dict())

print("d3 by label:", corpus.loc["d3"]["length"])

short = corpus[corpus["length"] <= 3]
print("short docs:", short.index.tolist())
print("first short by position:", short.iloc[0]["length"], "label:", short.index[0])

print(corpus.groupby("lang")["length"].mean().round(2))
""",
            "questions": [
                "What does setting the document identifier as the index make possible that positional access does not?",
                "After filtering to short documents, how are the first row's label and position related to the original table?",
                "What does the grouped mean report, and why is grouping by a column rather than by position the natural operation?",
            ],
            "answers": [
                "It makes a document reachable by its name with loc, so a lookup is stable regardless of how the table was filtered or sorted, whereas a positional lookup refers to whatever row happens to be there.",
                "The filtered frame keeps the original labels, so the first row by position is the first surviving document, whose label is its original identifier rather than zero.",
                "The average document length within each language, and grouping by a column is natural because the question is about a category of documents rather than about a range of positions.",
            ],
            "homework": (
                "Write corpus_table.py that builds a DataFrame of at least six documents with an id, "
                "text and language, derives a word-count column from the text, sets the id as the "
                "index and prints the table. Print the language distribution as a dictionary, look "
                "up one document by label with loc, filter by a condition on the derived column and "
                "print the surviving labels plus the first row's length and label accessed by "
                "position, and print the mean length grouped by language. Observable output: six "
                "lines or blocks."
            ),
            "required_patterns": ["pd.DataFrame", "set_index(", ".loc[", "groupby(", "print("],
        },
        "time-series": {
            "framing": (
                "A series loaded from a file becomes a DataFrame, and a timestamp index is "
                "what makes time the address rather than a column."
            ),
            "application": (
                "Walk the example as a series being loaded and given a timestamp index. "
                "Setting the timestamps as the index is the step that changes the object "
                "from a table with a time column into a time series, because a slice then "
                "reads as a date range rather than as row numbers, and that is the "
                "operation every forecaster's pipeline is built on. The label-versus-"
                "position distinction is sharper in time series than anywhere else: "
                "selecting a range by label includes both endpoints, which is not how "
                "positional slicing behaves, and the difference is a real source of "
                "off-by-one errors in train-test splits. Deriving a rolling mean over a "
                "column is an operation that only makes sense once the index is time, "
                "because the window is defined in periods of the index, and resampling is "
                "expressed as a groupby over the index. The column-versus-Series choice "
                "appears when a plotting routine expects a Series and a reporting routine "
                "expects a table."
            ),
            "example_hint": "give a series a timestamp index, slice by label, compute a rolling mean",
            "assessment_angle": "what a timestamp index makes sliceable and how label slicing differs from positional",
            "day": 8,
            "title": "Make Time the Index: Slice by Date, Window by Period",
            "code": """import pandas as pd

index = pd.date_range("2026-01-01", periods=10, freq="D")
series = pd.DataFrame({
    "reads": [12, 15, 9, 22, 30, 18, 25, 31, 27, 35],
}, index=index)
series.index.name = "date"

print(series.head())
print("slice by label:")
print(series.loc["2026-01-03":"2026-01-05"])

print("positional slice:")
print(series.iloc[2:5])

series["rolling"] = series["reads"].rolling(3).mean()
print(series.tail(4))

print("resampled mean:", series["reads"].resample("3D").mean().to_dict())
""",
            "questions": [
                "What does setting a timestamp index change about how the data is addressed?",
                "The label slice and the positional slice look similar. How do their endpoints differ?",
                "Why does the rolling window make sense only after the index is in place?",
            ],
            "answers": [
                "It makes a range of dates a valid slice, so a subset is selected by the time it covers rather than by counting rows, and it lets resampling and rolling group by the index.",
                "The label slice includes both endpoints, so the third and the fifth dates are both present, while the positional slice is exclusive at the end and drops the fifth date.",
                "Because the window is defined in consecutive periods of the index, so the mean is taken over neighbouring points in time rather than over an arbitrary run of rows.",
            ],
            "homework": (
                "Write time_index.py that builds a DataFrame of at least ten daily values with a "
                "date_range index named date and prints its head. Print a slice selected by date "
                "labels with both endpoints, and print a positional slice of the same width showing "
                "the endpoint difference. Add a rolling mean column over a window of three and print "
                "the tail, and print a resampled mean over a three-day period as a dictionary. "
                "Observable output: five lines or blocks."
            ),
            "required_patterns": ["pd.date_range", ".loc[", ".iloc[", ".rolling(", "print("],
        },
        "recommendation-systems": {
            "framing": (
                "Interaction logs are tables, and a DataFrame is what makes them "
                "transformable into the matrix a recommender consumes."
            ),
            "application": (
                "Walk the example as an event log being shaped into a user-item matrix. "
                "Each row of the log is one event with a user, an item and a rating, and "
                "the DataFrame is the structure that can be grouped by user to get totals, "
                "grouped by item to get popularity, and pivoted into the matrix form the "
                "model reads. The index-as-identity point matters because users and items "
                "have names, and setting one of them as the index makes a user's history a "
                "single loc lookup, while a positional lookup would change every time the "
                "table was filtered. The derived-column case is computing an average per "
                "user, which is a groupby returning a Series indexed by user name, and "
                "that object is the input to a normalisation step. Selecting a single "
                "column gives a Series that a ranking uses, while a list of columns keeps "
                "the table shape for export to the next stage, and the choice recurs at "
                "every stage of the pipeline."
            ),
            "example_hint": "turn an event log into per-user and per-item statistics and pivot to a matrix",
            "assessment_angle": "what grouping by name gives and what the pivot produces",
            "day": 8,
            "title": "An Event Log Becomes a Matrix: Group, Pivot, Rank",
            "code": """import pandas as pd

events = pd.DataFrame({
    "user": ["u1", "u1", "u2", "u2", "u3", "u3", "u1"],
    "item": ["A", "B", "A", "C", "B", "C", "C"],
    "rating": [5, 3, 4, 2, 5, 1, 4],
})

per_user = events.groupby("user")["rating"].mean()
print("mean per user:", per_user.to_dict())
print("best user:", per_user.idxmax())

per_item = events.groupby("item")["rating"].sum()
print("popularity:", per_item.sort_values(ascending=False).to_dict())

matrix = events.pivot_table(index="user", columns="item", values="rating")
print(matrix)

print("u2's row by label:", matrix.loc["u2"].to_dict())
print("column A is a:", type(matrix["A"]).__name__)
""",
            "questions": [
                "Why is idxmax on the per-user mean a stable way to name the best user?",
                "What does the pivot produce, and what appears in the cells where a user never rated an item?",
                "Selecting matrix['A'] returns a Series. What is its index, and why is that useful?",
            ],
            "answers": [
                "Because the groupby result is indexed by user name, so the maximum carries its label with it and the answer is a name rather than a position that could shift.",
                "A table of one row per user and one column per item with the rating at each crossing, and nan appears where a user and an item never interacted.",
                "Its index is the user names, so the Series reads as each user's rating of item A and can be aligned or compared with another item's column directly.",
            ],
            "homework": (
                "Write event_matrix.py with an event log of at least eight rows of user, item and "
                "rating. Print the mean rating per user as a dictionary and the best user's name, "
                "the total rating per item sorted descending as a dictionary, and a pivot table with "
                "users as rows and items as columns. Look up one user's row by label and print it as "
                "a dictionary, and print the type of one selected column. Observable output: five "
                "lines or blocks."
            ),
            "required_patterns": ["groupby(", "pivot_table(", ".idxmax()", ".loc[", "print("],
        },
        "reinforcement-learning": {
            "framing": (
                "Rollout logs are tables, and a DataFrame is what turns them into the "
                "curves a training report is built from."
            ),
            "application": (
                "Walk the example as rollout data being summarised for a report. Each row "
                "is an episode with its number, its return, its length and the policy "
                "version that produced it, and the DataFrame makes it possible to group by "
                "policy version and compare mean returns, which is exactly the comparison "
                "a training report states. The index point appears because episode numbers "
                "are a natural identity: after filtering to one policy version the episode "
                "numbers travel with the rows, so a positional access and a label access "
                "give different things, and knowing which to reach for is what keeps a "
                "report's numbers attributable to the right episodes. Deriving a per-step "
                "return by dividing two named columns is an expression that aligns by "
                "index automatically, and selecting the return column as a Series is what "
                "a plotting routine consumes while a table of several columns is what an "
                "export routine wants."
            ),
            "example_hint": "collect episodes into a table, group by policy version and derive per-step returns",
            "assessment_angle": "what grouping by policy version reports and what index travel costs",
            "day": 8,
            "title": "Rollouts Become Curves: Group by Version, Derive per Step",
            "code": """import pandas as pd

episodes = pd.DataFrame({
    "episode": [10, 11, 12, 13, 14, 15, 16],
    "return": [2.1, 3.4, 1.8, 5.0, 4.6, 6.2, 5.8],
    "steps": [40, 55, 30, 70, 65, 80, 75],
    "policy": ["v1", "v1", "v1", "v2", "v2", "v2", "v2"],
})
episodes["per_step"] = episodes["return"] / episodes["steps"]

print(episodes)

by_policy = episodes.groupby("policy")["return"].agg(["mean", "max", "count"])
print(by_policy)

print("best episode overall:", episodes["return"].idxmax(), episodes["return"].max())

v1 = episodes[episodes["policy"] == "v1"]
print("v1 by position:", v1.iloc[0]["episode"], "by label:", v1.loc[v1.index[0], "episode"])

print(episodes.sort_values("return", ascending=False).head(3))
""",
            "questions": [
                "What does grouping by policy version with several aggregations report, and why is it the natural summary for a training report?",
                "After filtering to one policy version, what does the comparison of positional and label access demonstrate?",
                "What does dividing the return by the steps column produce, and what makes the two columns align correctly?",
            ],
            "answers": [
                "The mean, maximum and count of returns within each version, and it is natural because the report's question is whether one version of the policy improved on the previous one, which is a comparison by category.",
                "That the positional access gives the first surviving row while the label access names the episode identifier, so the two are different facts and only the label access is stable across filters.",
                "A per-step return measuring how much reward each step earned, and the columns align because they share the same row index, so the division is label by label.",
            ],
            "homework": (
                "Write rollout_table.py with a DataFrame of at least seven episodes with episode "
                "number, return, steps and policy version, plus a derived per-step column printed "
                "with the table. Group by policy version with mean, max and count and print the "
                "result, print the best episode's label and value, and after filtering to one policy "
                "version print the first row's episode number accessed both positionally and by "
                "label. Print the top three episodes sorted by return. Observable output: six lines "
                "or blocks."
            ),
            "required_patterns": ["groupby(", ".agg([", ".idxmax()", ".iloc[0]", "print("],
        },
        "gpu-programming": {
            "framing": (
                "The host side of a device pipeline is usually a DataFrame, because that is "
                "how data arrives before it becomes arrays."
            ),
            "application": (
                "Walk the example as host data being inspected before a device transfer. "
                "The data sits in a DataFrame, and the question is which columns are "
                "numeric and how large they are, because those facts decide the buffer "
                "sizes and the dtype of the device arrays. Selecting the numeric columns "
                "by name and converting them to arrays is the bridge from tabular form to "
                "the contiguous buffers a kernel consumes, and the dtypes of the columns "
                "become the dtypes of the buffers, so an integer column loaded as an "
                "object dtype would silently become a much more expensive device array. "
                "The index point appears because rows have identifiers, and after a filter "
                "the identifiers travel with the rows, so a report that names which rows "
                "were transferred has to use the labels rather than the positions. This "
                "is the practical reason a device pipeline still needs pandas: the data "
                "does not arrive as arrays, and the inspection step that decides the "
                "layout is tabular."
            ),
            "example_hint": "inspect a host DataFrame's dtypes and sizes and convert columns to a device-ready buffer",
            "assessment_angle": "what column dtypes decide for a device buffer and why the index travels",
            "day": 8,
            "title": "Host Side Is a Table: Inspect Before You Transfer",
            "code": """import pandas as pd
import numpy as np

host = pd.DataFrame({
    "id": [101, 102, 103, 104],
    "x": [1.0, 2.5, 3.0, 4.5],
    "y": [0.5, 1.5, 2.5, 3.5],
    "label": ["a", "b", "a", "c"],
})

print(host.dtypes)

numeric = host[["x", "y"]]
buffer = numeric.to_numpy(dtype=np.float32)
print("buffer shape:", buffer.shape, "dtype:", buffer.dtype)
print("bytes:", buffer.nbytes)

selected = host[host["label"] == "a"]
print("selected labels:", selected.index.tolist())
print("first selected id by position:", selected.iloc[0]["id"])

print(host[["x", "y"]].describe().loc[["min", "max"]])
""",
            "questions": [
                "What do the DataFrame's column dtypes determine for the device buffer that follows?",
                "Why does the buffer conversion specify float32 rather than relying on the columns' own dtype?",
                "After filtering to one label, what does the printed index list demonstrate about the rows that survived?",
            ],
            "answers": [
                "The dtype and therefore the width of the device array, because the buffer is built from the columns, so a wider column dtype becomes a wider and more expensive buffer.",
                "Because the columns' own dtype may be float64 from the load, which would double the transfer cost and the device memory, so the explicit narrower dtype keeps the buffer the size the kernel expects.",
                "That the surviving rows kept their original index labels, so the selection is identifiable by those labels rather than being renumbered from zero.",
            ],
            "homework": (
                "Write host_table.py with a DataFrame of at least five rows containing an integer id, "
                "two float coordinate columns and a text label, and print the column dtypes. Select "
                "the two numeric columns, convert them to a float32 numpy array with to_numpy and "
                "print its shape, dtype and byte size. Filter to one label and print the surviving "
                "index labels plus the first selected id accessed by position, and print the min and "
                "max rows of a describe of the numeric columns. Observable output: five lines or "
                "blocks."
            ),
            "required_patterns": [".dtypes", "to_numpy(", "float32", ".iloc[0]", "print("],
        },
        "own-ml-framework": {
            "framing": (
                "A framework still has to load data, and a DataFrame is the shape most data "
                "arrives in before the framework's own tensors take over."
            ),
            "application": (
                "Walk the example as a data-loading boundary inside a framework. The "
                "training data arrives as a DataFrame, and the framework's loader has to "
                "turn chosen columns into tensors, which is where the tabular world meets "
                "the array world. The decision that has to be made deliberately is which "
                "columns are features and which is the target, and that choice is "
                "expressed by name rather than by position, which is what makes a loader "
                "configurable and readable. The dtype of each column becomes the dtype of "
                "the resulting tensor unless it is stated, and stating it is what prevents "
                "an integer label column from becoming an expensive float tensor. The "
                "index point appears because a shuffle or a filter keeps the original "
                "labels, so a debug routine that names which samples were mispredicted has "
                "to use the index rather than positions, and a framework that exposes the "
                "labels alongside the tensors makes that possible. Recognising this "
                "boundary as a design decision is what separates a framework whose data "
                "path is inspectable from one whose tensors arrive opaquely."
            ),
            "example_hint": "build a loader that turns named columns into tensors with stated dtypes",
            "assessment_angle": "what the loader decides by name and what the column dtype would cost",
            "day": 8,
            "title": "The Loader Boundary: Columns by Name, Tensors with a Stated Dtype",
            "code": """import pandas as pd
import numpy as np

training = pd.DataFrame({
    "sample_id": ["s1", "s2", "s3", "s4"],
    "f1": [0.1, 0.5, 0.3, 0.9],
    "f2": [0.2, 0.4, 0.6, 0.8],
    "target": [0, 1, 0, 1],
})


def load(df, features, target, dtype=np.float32):
    x = df[features].to_numpy(dtype=dtype)
    y = df[target].to_numpy(dtype=np.int64)
    return x, y, df.index


x, y, labels = load(training, ["f1", "f2"], "target")
print("x:", x.shape, x.dtype, "bytes:", x.nbytes)
print("y:", y.shape, y.dtype)
print("labels:", labels.tolist())

untyped = training[["f1", "f2"]].to_numpy()
print("untyped dtype:", untyped.dtype, "bytes:", untyped.nbytes)

mask = y == 1
print("positive labels:", [labels[i] for i in np.where(mask)[0]])

print("column means:", training[["f1", "f2"]].mean().round(3).to_dict())
""",
            "questions": [
                "Why does the loader take feature names as an argument rather than fixed positions?",
                "What would the untyped conversion cost compared with the stated float32 one?",
                "How are the labels used to report which samples were positive, and why is that better than using positions?",
            ],
            "answers": [
                "Because it makes the loader configurable for any dataset whose column names are known, so the same code serves many inputs, and reading names states what the features are instead of hiding them behind numbers.",
                "It would use float64, doubling the memory of the feature matrix for no benefit, since the stated float32 holds the same values in half the space.",
                "The positions where the target is one are mapped through the index to the sample identifiers, so the report names samples rather than counts, and it stays correct after any filter or shuffle because the labels travel with the rows.",
            ],
            "homework": (
                "Write loader_boundary.py with a training DataFrame of at least five rows, an "
                "identifier column, two float feature columns and an integer target. Write a load "
                "function that selects the named feature columns, converts them to float32 and the "
                "target to int64 with to_numpy, and returns the arrays plus the index, and print "
                "both arrays' shapes, dtypes and byte sizes with the label list. Print the dtype and "
                "byte size of an untyped conversion for comparison, and use the index to report the "
                "identifiers of the positive samples plus the feature column means. Observable "
                "output: five lines or blocks."
            ),
            "required_patterns": ["to_numpy(", "np.float32", "np.int64", "df.index", "print("],
        },
    },
)
