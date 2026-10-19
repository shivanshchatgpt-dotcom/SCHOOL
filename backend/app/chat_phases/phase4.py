PHASE = (
    "Context and Memory",
    "Separate the bounded context sent with each request from the durable facts an assistant chooses to remember.",
    {
        120: dict(
            topic="Orientation: context versus memory",
            idea=(
                "Context and memory are different resources and mixing them is the first design mistake in "
                "assistant work. Context is everything the model can see on this request: the system prompt, "
                "the recent turns, retrieved snippets and any tool results you injected. It is temporary, "
                "expensive and bounded by a token window. Memory is what your program decided to persist "
                "outside that window: a name, a preference, a fact from last week. The model does not remember "
                "anything by itself; your code writes facts down and later chooses which ones to put back into "
                "context. Once you separate the two, hard questions become concrete. How many turns fit? Which "
                "facts are worth storing? What happens when a remembered fact contradicts a fresh statement? "
                "Today you build both sides in miniature: a fixed transcript, a function that keeps only a "
                "recent window, and a small dictionary of durable facts. Print the window and the memory side by "
                "side and notice that the final user question can be answered because memory survives while the "
                "early turns do not. This distinction runs through every later lesson on summarising, retrieval, "
                "expiry and conflict resolution, and it is the vocabulary you need to reason about production "
                "assistant failures."
            ),
            code='''def window(history, limit):
    system = [m for m in history if m["role"] == "system"]
    turns = [m for m in history if m["role"] != "system"]
    return system + turns[-limit:]

def memory_facts(memory):
    return {k: v for k, v in sorted(memory.items())}

history = [
    {"role": "system", "content": "Be brief."},
    {"role": "user", "content": "My name is Ada."},
    {"role": "assistant", "content": "Noted."},
    {"role": "user", "content": "I prefer tea."},
    {"role": "assistant", "content": "Okay."},
    {"role": "user", "content": "What should I order?"},
]
memory = {"name": "Ada", "drink": "tea"}
print("context window:")
for m in window(history, 3):
    print(" ", m["role"], m["content"])
print("durable memory:", memory_facts(memory))
assert "My name is Ada." not in [m["content"] for m in window(history, 3)]
print("recent turns answer style; memory carries facts")''',
            variant_b="raise the window limit to five and explain which early turn now reappears",
            variant_c="add a second remembered fact and print context and memory again after the same transcript",
            mistakes=[
                "Treating everything in the transcript as permanent memory.",
                "Assuming the model remembers a fact that was never written to storage.",
                "Building memory without deciding which parts belong in the current context.",
            ],
            q1=(
                "What is the difference between context and memory in a chatbot?",
                "Context is the bounded input visible on this request, while memory is durable data your program stores and later chooses to inject into context.",
            ),
            homework=(
                "Write `window(history, limit)` that keeps every system message and only the last `limit` "
                "dialogue messages. Build a six-message transcript with one fact stated early, print the "
                "trimmed history, and comment which line shows the fact is outside the window but still in memory."
            ),
            patterns=["def ", "window(", "print("],
            mapping=(
                "Assistant products expose this split as a context window plus a persistent memory or profile "
                "store; retrieval systems decide which stored facts earn a place in the next prompt."
            ),
        ),
        121: dict(
            topic="Short-term conversation history",
            idea=(
                "A conversation history is the bot's working context, but it cannot grow without limit. Every "
                "turn costs tokens, long histories slow the request and eventually overflow the window, and "
                "older small talk usually adds more noise than signal. The usual first fix is a sliding window: "
                "keep the system prompt and the most recent N turns, drop everything older. It is crude, cheap "
                "and predictable, which makes it a good baseline. Two details matter. The system prompt must "
                "survive trimming, because losing instructions mid-conversation changes behaviour in ways that "
                "are hard to debug. And trimming should happen at turn boundaries, not in the middle of an "
                "exchange, so the model never sees a dangling assistant reply without its user question. Today "
                "you implement `trim_history`, which separates the system messages from the dialogue, keeps the "
                "last few dialogue messages and returns both the kept history and the dropped ones. Printing the "
                "dropped list is deliberate: silent truncation hides bugs, while an explicit list lets you log "
                "what the model stopped seeing. This is exactly what production clients do when they cap "
                "context, and it is the foundation for the next idea, where instead of dropping old turns we "
                "compress them into a summary."
            ),
            code='''def trim_history(history, max_turns):
    system = [m for m in history if m["role"] == "system"]
    dialog = [m for m in history if m["role"] != "system"]
    dropped = dialog[:-max_turns] if max_turns else dialog
    return system + dialog[-max_turns:], dropped

history = [{"role": "system", "content": "Short answers."}]
for i in range(1, 6):
    history.append({"role": "user", "content": f"question {i}"})
    history.append({"role": "assistant", "content": f"answer {i}"})

kept, dropped = trim_history(history, 4)
print("dropped:", [m["content"] for m in dropped])
print("kept:")
for m in kept:
    print(f"  {m['role']:9} {m['content']}")
assert kept[0]["role"] == "system"
assert len(kept) == 5
print("system prompt survives trimming")''',
            variant_b="try max_turns values of two and ten and compare how many messages are dropped",
            variant_c="keep complete user/assistant pairs instead of counting messages individually",
            mistakes=[
                "Trimming the system prompt along with old user messages.",
                "Dropping messages in the middle of a user/assistant exchange.",
                "Truncating silently so nobody knows what the model stopped seeing.",
            ],
            q1=(
                "Why must the system prompt be protected from history trimming?",
                "It carries the standing instructions for the whole conversation, and losing it changes behaviour while leaving no obvious error in the transcript.",
            ),
            homework=(
                "Write `trim_history(history, limit)` that returns kept and dropped lists while always keeping "
                "system messages. Test it with eight dialogue messages and a limit of four, print both lists, "
                "and comment which line guarantees the system prompt is never dropped."
            ),
            patterns=["def ", "trim_history(", "return"],
            mapping=(
                "Chat clients and agent frameworks cap conversation history this way before every model call, "
                "often keeping a system prompt plus a fixed number of recent turns."
            ),
        ),
        122: dict(
            topic="Summarising old turns",
            idea=(
                "Throwing old turns away loses information that may still matter. Summarising is the middle "
                "path: replace a block of older turns with a short, deterministic description, then keep recent "
                "turns verbatim. In production this summary is usually written by a model, but the contract is "
                "the same one you can practise offline: the summary must be shorter than the input, must state "
                "what the user asked about, and must be placed where the old turns were. A hand-written "
                "extractive summary is a useful exercise because it forces you to decide what deserves to "
                "survive. Names, decisions, constraints and open questions matter; greetings and "
                "acknowledgements do not. Today you write `summarise`, which splits the transcript into an old "
                "section and a recent section, collects the user text from the old part, normalises it and "
                "produces a compact line, then returns that line with the untouched recent turns. The output is "
                "deterministic, so you can assert on it. Notice the trade-off: a summary can lose a detail that "
                "later turns depend on, and it can also misstate something. That risk is why summaries should be "
                "visible, stored separately from raw history, and refreshed rather than edited in place. Later "
                "retrieval will partially recover the detail that compression drops."
            ),
            code='''def summarise(turns, keep=2):
    old, recent = turns[:-keep], turns[-keep:]
    user_lines = [m["content"] for m in old if m["role"] == "user"]
    words = []
    for line in user_lines:
        words.extend(line.split())
    summary = "Earlier the user asked about: " + ", ".join(sorted(set(words))[:8])
    return summary, recent

turns = [
    {"role": "user", "content": "How do I reset my password"},
    {"role": "assistant", "content": "Use the settings page."},
    {"role": "user", "content": "Where are the password rules"},
    {"role": "assistant", "content": "In the security guide."},
    {"role": "user", "content": "Show my open tickets"},
]
summary, recent = summarise(turns)
print(summary)
print("recent turns:")
for m in recent:
    print(f"  {m['role']:9} {m['content']}")
assert len(recent) == 2
print("summary replaced 3 old turns")''',
            variant_b="change keep to four and observe which turns move into the summary",
            variant_c="summarise only user requests and mention how many assistant replies were folded away",
            mistakes=[
                "Summarising before deciding which details later turns rely on.",
                "Storing the summary as if it were a verbatim user quote.",
                "Letting the summary grow until it is as long as the history it replaced.",
            ],
            q1=(
                "What must a summary of old turns preserve to be useful?",
                "The stable facts, decisions, constraints and open questions that later turns may depend on, while dropping greetings and acknowledgements.",
            ),
            homework=(
                "Write `summarise(turns, keep)` that folds older user turns into one deterministic summary "
                "string and returns it with the recent turns. Print the summary and the kept turns for a "
                "six-message transcript, and comment which line decides what gets compressed."
            ),
            patterns=["def ", "summarise(", "return"],
            mapping=(
                "Memory systems such as conversation buffers with summary compression use this pattern to bound "
                "context while retaining earlier intent, and RAG pipelines index the summary for later retrieval."
            ),
        ),
        123: dict(
            topic="Long-term facts and preferences",
            idea=(
                "Short-term history disappears when the session ends, so a useful assistant also keeps "
                "long-term facts and preferences. The important word is curated: not every sentence deserves "
                "permanent storage. Good candidates are stable, reusable and user-specific, such as a preferred "
                "name, a timezone, a dietary restriction or a communication style. Bad candidates are one-off "
                "requests, sensitive data and anything you cannot explain later. A simple and honest extractor "
                "looks for explicit markers in user turns, pulls the value, and records where it came from. "
                "Recording the source turn matters, because it lets you audit a fact, expire it, or resolve a "
                "conflict when the user changes their mind. Today you build `learn`, a small rule-based "
                "extractor that recognises three kinds of statement and stores each value with the turn number "
                "that produced it. The parser is intentionally naive: it is a stand-in for a model-based "
                "extractor, not a replacement. What you should take away is the shape of the data, a key, a "
                "value and provenance, plus the rule that extraction only runs on user-authored text. Print the "
                "facts and check that a statement from turn one is still available after later turns. That "
                "persistence is the whole point of long-term memory."
            ),
            code='''def learn(text, facts, turn):
    patterns = {
        "name": "my name is ",
        "drink": "i prefer ",
        "city": "i live in ",
    }
    lowered = text.lower()
    for key, marker in patterns.items():
        if marker in lowered:
            value = text[lowered.index(marker) + len(marker):].strip(" .")
            facts[key] = {"value": value, "turn": turn}
    return facts

turns = [
    "Hi, my name is Ada.",
    "I prefer green tea.",
    "I live in Pune.",
]
facts = {}
for number, text in enumerate(turns, start=1):
    learn(text, facts, number)
for key in sorted(facts):
    print(f"{key:6} = {facts[key]['value']!r} (turn {facts[key]['turn']})")
assert facts["city"]["value"] == "Pune"
print("preferences persist beyond the current turn")''',
            variant_b="add a preference marker for communication style and learn it from a fourth turn",
            variant_c="ignore a statement unless it comes from a user role, and explain why assistant text is unsafe to learn from",
            mistakes=[
                "Storing every sentence as a permanent fact instead of curating candidates.",
                "Losing the source turn, so a remembered value cannot be audited or expired.",
                "Extracting facts from assistant text and then treating them as user preferences.",
            ],
            q1=(
                "Why should a stored fact record the turn that produced it?",
                "Provenance supports auditing, expiry and conflict resolution when a later statement contradicts the original fact.",
            ),
            homework=(
                "Write `learn(text, facts, turn)` that extracts a name, a preference and a city using explicit "
                "markers, storing each value with its source turn. Feed three user turns, print the facts, and "
                "comment which line records provenance for later conflict resolution."
            ),
            patterns=["def ", "learn(", "facts"],
            mapping=(
                "Production assistants extract durable preferences into a user profile and cite the source when "
                "resolving conflicting memories, much like an entity store in a RAG system."
            ),
        ),
        124: dict(
            topic="A key-value profile store",
            idea=(
                "A key-value profile store is the simplest durable memory that is still genuinely useful in practice. Each "
                "fact gets a key such as name, timezone or drink, and a small record holds the value plus "
                "metadata like a version and the turn that wrote it. Reading a profile is one lookup; writing "
                "one is a decision about overwriting. Last-write-wins is the usual default, but it should be "
                "explicit rather than an accident of dictionary assignment. Keeping a version counter makes "
                "updates visible and gives you something to log or compare when two sessions race. A default "
                "value on read prevents callers from scattering `None` checks everywhere, while still keeping "
                "missing facts distinguishable from facts that are present. Today you implement `put` and `get` "
                "over a plain dictionary, write the same key twice, and print every entry with its version and "
                "source turn. The second write to name should visibly win. This store is deliberately not clever: "
                "no schema validator, no transactions, no database. Those are real concerns later, but the core "
                "contract is small and testable now. Once facts live in a key-value shape, retrieval, "
                "deduplication, expiry and prompt injection all become operations on the same structure instead "
                "of special cases."
            ),
            code='''def put(store, key, value, turn):
    old = store.get(key)
    store[key] = {
        "value": value,
        "version": (old["version"] + 1) if old else 1,
        "turn": turn,
    }
    return store

def get(store, key, default=None):
    entry = store.get(key)
    return default if entry is None else entry["value"]

profile = {}
put(profile, "name", "Ada", 1)
put(profile, "timezone", "IST", 2)
put(profile, "name", "Ada Lovelace", 3)
for key in sorted(profile):
    entry = profile[key]
    print(f"{key:9} {entry['value']!r:16} v{entry['version']} turn {entry['turn']}")
print("lookup city:", get(profile, "city", "unknown"))
assert get(profile, "name") == "Ada Lovelace"
print("last write wins with a version counter")''',
            variant_b="add a delete operation and show that reading a deleted key returns the default",
            variant_c="store a confidence value with each write and print it beside the version",
            mistakes=[
                "Overwriting silently with no version or source information.",
                "Conflating a missing key with a stored None value.",
                "Letting every caller invent its own ad-hoc dictionary shape.",
            ],
            q1=(
                "Why keep a version counter in a key-value profile store?",
                "It makes overwrites visible, supports auditing and debugging, and gives competing writers a value to compare.",
            ),
            homework=(
                "Write `put(store, key, value, turn)` and `get(store, key, default)` over a plain dict, with a "
                "version counter on every write. Write one key twice, read a missing key, print the profile, "
                "and comment which line makes the overwrite explicit."
            ),
            patterns=["def ", "put(", "get("],
            mapping=(
                "User profile services and assistant memory APIs expose exactly this get/set shape, adding "
                "versioning so retrieved facts can be traced and refreshed."
            ),
        ),
        125: dict(
            topic="Retrieval with a keyword index",
            idea=(
                "Long-term facts are only useful if you can find the right ones at the right moment. A keyword "
                "index is the cheapest retrieval mechanism that works: scan every stored memory once, map each "
                "word to the memories that contain it, and answer a query by looking up its words. Building an "
                "inverted index turns a linear search into a dictionary lookup plus a small merge. The trade-offs "
                "are worth seeing clearly. Keyword matching is exact, so it misses synonyms, typos and "
                "paraphrases, and common words create noisy hits. Normalising case and punctuation helps a "
                "little, but there is no stemming in this lesson. Still, for a small memory of user preferences, "
                "an index is fast, transparent and easy to debug. Today you build `index_memories` and `search` "
                "over a handful of facts. The index maps words to sorted memory ids, and search unions the hits "
                "for each query word, then sorts them so output never depends on set ordering. Notice that a "
                "query with several words behaves like a soft AND only if you intersect, and a soft OR if you "
                "union; this example unions, which favours recall. Print the hits for three queries, including "
                "one that misses. That miss is informative: retrieval quality, not storage, is usually the "
                "limiting factor in memory systems."
            ),
            code='''def index_memories(memories):
    index = {}
    for key in sorted(memories):
        for word in memories[key].lower().split():
            index.setdefault(word, []).append(key)
    return index

def search(index, query):
    hits = set()
    for word in query.lower().split():
        hits.update(index.get(word, []))
    return sorted(hits)

memories = {
    "m1": "Ada drinks green tea",
    "m2": "Ada lives in Pune",
    "m3": "green tea is preferred in the morning",
}
index = index_memories(memories)
for query in ["green tea", "pune", "coffee"]:
    print(f"{query!r:12} -> {search(index, query)}")
print("index size:", len(index))
assert search(index, "green") == ["m1", "m3"]
print("keyword index trades precision for cheap lookup")''',
            variant_b="normalise punctuation before indexing and add a query that only matches after normalisation",
            variant_c="intersect query words instead of unioning them and describe which queries change",
            mistakes=[
                "Returning set objects so output order varies between runs.",
                "Forgetting to normalise case before building the index.",
                "Treating keyword hits as proof of relevance instead of candidates for ranking.",
            ],
            q1=(
                "What does an inverted keyword index buy you over scanning every memory?",
                "It replaces a full scan with dictionary lookups per query word, making retrieval cheaper and its behaviour easy to inspect.",
            ),
            homework=(
                "Write `index_memories(memories)` and `search(index, query)` using words as keys and sorted "
                "memory ids as values. Index four memories, run three queries including one miss, print each "
                "result, and comment which line keeps the output order deterministic."
            ),
            patterns=["def ", "index", "sorted("],
            mapping=(
                "This is the lexical half of RAG retrieval; production systems pair keyword indexes with "
                "embeddings so exact names and semantic paraphrases both retrieve useful memory."
            ),
        ),
        126: dict(
            topic="Ranking by recency and frequency",
            idea=(
                "Retrieval returns candidates, but the prompt can only take a few of them, so they need a "
                "ranking. Two signals are available without any model: how often a memory has been used and how "
                "recently it was updated. Frequency rewards facts that keep proving useful; recency rewards "
                "facts that reflect the current situation. Combining them as a weighted score is a classic "
                "design, and the weights are a product decision, not a mathematical truth. A large recency "
                "weight makes the assistant forget old but stable preferences, while a large frequency weight "
                "can keep resurrecting an outdated fact. Two engineering details keep this honest. Store the "
                "counters explicitly, with recency supplied as data rather than read from the clock, so tests "
                "are reproducible. And break ties deterministically, usually by a stable key, because dictionary "
                "order is not a ranking policy. Today you implement `rank`, compute `visits * frequency_weight "
                "+ recency * recency_weight`, sort by descending score and then by name, and print the ordered "
                "result. Two entries deliberately tie, so you can see the tie-break working. This is the same "
                "shape as production memory scoring, where embeddings or learned weights may replace the "
                "hand-tuned formula but the need for an explicit, debuggable policy remains."
            ),
            code='''def rank(entries, weights):
    scored = []
    for item in entries:
        score = item["visits"] * weights["frequency"] + item["recency"] * weights["recency"]
        scored.append((-score, item["name"], item))
    scored.sort()
    return [(name, -score) for score, name, _ in scored]

weights = {"frequency": 2, "recency": 1}
entries = [
    {"name": "tea", "visits": 3, "recency": 5},
    {"name": "pune", "visits": 1, "recency": 1},
    {"name": "ada", "visits": 3, "recency": 5},
]
for name, score in rank(entries, weights):
    print(f"{name:6} score={score}")
assert [n for n, _ in rank(entries, weights)] == ["ada", "tea", "pune"]
print("ties break on name, not on dict order")''',
            variant_b="increase the recency weight and predict which entries move ahead",
            variant_c="add a decayed score that subtracts a fixed penalty per stale tick and compare both rankings",
            mistakes=[
                "Reading the clock inside the scoring function and making tests non-reproducible.",
                "Leaving ties dependent on dictionary insertion order.",
                "Choosing weights without recording why they were chosen.",
            ],
            q1=(
                "Why break ranking ties with a stable key such as the memory name?",
                "Without a deterministic secondary key, equal scores could reorder between runs and make retrieval and tests unpredictable.",
            ),
            homework=(
                "Write `rank(entries, weights)` that scores each entry by frequency and recency, sorts by "
                "descending score then by name, and returns names with scores. Include a deliberate tie, print "
                "the ranking, and comment which line makes the order reproducible."
            ),
            patterns=["def ", "rank(", "sort"],
            mapping=(
                "Memory and RAG rerankers combine retrieval scores with usage or freshness signals; deterministic "
                "tie-breaking keeps assistant context stable across identical requests."
            ),
        ),
        127: dict(
            topic="Deduplicating remembered facts",
            idea=(
                "Deduplication is what keeps memory from turning into a pile of near-identical sentences. The "
                "same preference arrives phrased slightly differently, in a different case, with punctuation or "
                "extra whitespace, and a naive append stores all of it. That wastes context, distorts frequency "
                "counts and makes conflict resolution harder. The first step is normalisation: lowercase, strip "
                "surrounding punctuation, collapse whitespace. Normalisation is lossy on purpose, and you must "
                "know what it loses, because `US` and `us` may not be the same thing. The second step is a keyed "
                "store instead of a list, so a repeated fact updates an existing entry rather than adding a new "
                "one. You also need a policy for which version wins. Keeping the newest occurrence is a "
                "reasonable default, and recording a last-seen counter makes the choice visible. Today you write "
                "`normalise` and `dedupe`, feed in five raw statements including three spellings of the same "
                "preference, and print the surviving entries with their last-seen positions. The output should "
                "be stable because the result is sorted by recency and then by text. The lesson is that "
                "duplicate handling is a data-modelling decision, not string cleanup bolted on at the end, and "
                "that the policy must be written down and tested."
            ),
            code='''def normalise(text):
    return " ".join(text.lower().strip(" .").split())

def dedupe(facts):
    latest = {}
    for order, fact in enumerate(facts):
        key = normalise(fact)
        latest[key] = {"text": key, "last_seen": order}
    return [latest[key] for key in sorted(latest, key=lambda k: (-latest[k]["last_seen"], k))]

raw = ["Likes tea", "likes tea.", "LIKES tea", "Likes tea", "Lives in Pune"]
unique = dedupe(raw)
for item in unique:
    print(f"{item['text']:14} last_seen={item['last_seen']}")
assert len(unique) == 2
print("duplicates collapsed, newest occurrence kept")''',
            variant_b="normalise punctuation inside sentences as well and show which raw statements collapse",
            variant_c="count how many times each fact appeared instead of keeping only last_seen",
            mistakes=[
                "Appending every statement and calling the list a memory.",
                "Normalising so aggressively that distinct facts collapse together.",
                "Keeping duplicates but hiding them behind a retrieval filter.",
            ],
            q1=(
                "Why store normalised facts as keys instead of appending every statement?",
                "A keyed store collapses repeats on write, keeps context small and makes frequency and conflict policies explicit.",
            ),
            homework=(
                "Write `normalise(text)` and `dedupe(facts)` that collapse case, punctuation and whitespace "
                "variants while keeping the newest occurrence. Feed five raw facts containing duplicates, print "
                "the survivors, and comment which line makes the output order stable."
            ),
            patterns=["def ", "normalise(", "dedupe("],
            mapping=(
                "Memory services deduplicate extracted facts before indexing so one repeated preference does not "
                "dominate retrieval or inflate confidence."
            ),
        ),
        128: dict(
            topic="Forgetting and expiry",
            idea=(
                "Memory that never expires becomes wrong in a quiet, expensive way. A trial deadline, a delivery "
                "address or a temporary preference is true for a while and misleading afterwards. Expiry is the "
                "policy that says how long a fact may live. The clean implementation stores an explicit creation "
                "tick and a time-to-live with each entry, then compares both against a `now` value supplied by "
                "the caller. Reading the real clock inside the function would make tests flaky and behaviour "
                "hard to reproduce, so time is data here, exactly as it is in many production systems that pass "
                "a request timestamp through. Deciding the TTL is a product judgement: identity facts can live "
                "for a long time, session context should be short, and anything with a deadline should expire at "
                "that deadline. The deletion strategy also matters. Filtering expired entries at read time is "
                "simple and always correct; a background sweep saves space but adds scheduling concerns. Today "
                "you implement `active`, which keeps entries whose age is within their TTL, and print both the "
                "survivors and the expired facts for a fixed `now`. Pay attention to the boundary comparison: "
                "whether an entry exactly at its TTL survives is a decision, and it should be stated rather "
                "than discovered by accident."
            ),
            code='''def active(entries, now):
    kept = []
    for entry in entries:
        age = now - entry["created"]
        if age <= entry["ttl"]:
            kept.append((entry, age))
    return kept

entries = [
    {"fact": "name is Ada", "created": 1, "ttl": 100},
    {"fact": "likes tea", "created": 8, "ttl": 3},
    {"fact": "trial ends", "created": 2, "ttl": 4},
]
now = 10
for entry, age in active(entries, now):
    print(f"{entry['fact']:14} age={age} ttl={entry['ttl']}")
expired = [e["fact"] for e in entries if (now - e["created"]) > e["ttl"]]
print("expired:", expired)
assert expired == ["trial ends"]
print("expiry uses explicit timestamps, not the clock")''',
            variant_b="give the name fact a short TTL and observe it disappear at the same now value",
            variant_c="sweep expired entries into a separate archive list instead of dropping them",
            mistakes=[
                "Calling datetime.now or time.time inside an expiry check, making tests flaky.",
                "Giving every fact the same TTL regardless of how it is used.",
                "Deleting expired facts with no policy for audit or recovery.",
            ],
            q1=(
                "Why pass `now` into an expiry function instead of reading the clock inside it?",
                "Supplied time makes behaviour deterministic, testable and consistent across a request, while the real clock stays at the boundary.",
            ),
            homework=(
                "Write `active(entries, now)` that keeps entries whose age is within their TTL and returns them "
                "with ages. Use explicit `created` and `ttl` fields, one entry at the boundary, print survivors "
                "and expired facts, and comment which comparison implements the policy."
            ),
            patterns=["def ", "active(", "ttl"],
            mapping=(
                "Assistant memory stores expire session facts and stale preferences; request-scoped timestamps "
                "keep the decision reproducible and auditable."
            ),
        ),
        129: dict(
            topic="Redacting private data",
            idea=(
                "Long-term memory creates a privacy obligation before it creates a convenience. Users type email "
                "addresses, phone numbers, card digits and addresses into chats, and a store that keeps raw "
                "turns will keep all of it forever. Redaction should happen on the way in, not on the way out, "
                "because data you never stored cannot leak. The practical approach is a short ordered list of "
                "patterns and replacements, applied before any fact is persisted or logged. Order matters: "
                "match structured identifiers such as email and long digit groups before looser patterns like "
                "phone numbers, otherwise a broad rule can consume part of a narrower one. Redaction is not "
                "anonymisation. A pattern can miss an unusual format, and replacing an email with a label still "
                "reveals that an email existed. Say that plainly in your design notes. Today you compile three "
                "regular expressions, apply them with `re.sub`, and print redacted versions of three sample "
                "messages. Notice that the card pattern allows spaces or dashes, and that the phone pattern is "
                "intentionally broad. The output is deterministic. The habit to build is a single redaction "
                "function that every write path calls, plus a test with realistic samples, because one "
                "forgotten path is exactly where private data survives."
            ),
            code='''import re

RULES = [
    (re.compile(r"[\\w.+-]+@[\\w-]+\\.[\\w.]+"), "[email]"),
    (re.compile(r"\\b\\d{4}[- ]?\\d{4}[- ]?\\d{4}[- ]?\\d{4}\\b"), "[card]"),
    (re.compile(r"\\+?\\d[\\d -]{7,}\\d"), "[phone]"),
]

def redact(text):
    for pattern, replacement in RULES:
        text = pattern.sub(replacement, text)
    return text

samples = [
    "Email ada@example.com for the invoice",
    "Card 4111 1111 1111 1111 expires soon",
    "Call +91 98765 43210 tomorrow",
]
for sample in samples:
    print(redact(sample))
assert "ada@example.com" not in " ".join(redact(s) for s in samples)
print("private spans are replaced before storage")''',
            variant_b="add a rule for postal codes and check that it does not damage ordinary numbers",
            variant_c="replace matches with stable labels that keep the kind but drop the value",
            mistakes=[
                "Redacting only when displaying data that was already stored raw.",
                "Applying a broad pattern before a structured one and corrupting the match.",
                "Treating redaction as complete anonymisation and promising more than it delivers.",
            ],
            q1=(
                "Why apply redaction before persistence rather than before display?",
                "Data that was never stored cannot leak later, while display-time redaction leaves the private value exposed in storage and logs.",
            ),
            homework=(
                "Write `redact(text)` that replaces emails, card numbers and phone numbers with labelled tokens "
                "using ordered patterns. Run it on three realistic samples, print each result, and comment which "
                "line guarantees every stored fact passes through the filter."
            ),
            patterns=["def ", "redact(", "sub("],
            mapping=(
                "Privacy filters sit before assistant memory writes and log emission; RAG ingestion pipelines "
                "apply the same redaction before indexing documents."
            ),
        ),
        130: dict(
            topic="Resolving conflicting memories",
            idea=(
                "Two memories can disagree, and the system needs a policy instead of whichever value happened "
                "to load last. Conflicts appear when a user corrects a fact, when a form and a chat provide "
                "different values, or when an old session is imported after a new one. Resolving them requires "
                "metadata: where the claim came from, how confident the extractor was, and when it was "
                "observed. A deterministic resolver sorts claims by a stated priority and picks the winner. A "
                "common order is confidence first, then recency, then source name as a final stable tie-break. "
                "That order is a product choice; a verified profile field may deserve to beat a casual chat "
                "statement even if the chat is newer. The losing claims should not be deleted silently. Keeping "
                "them, or at least logging the override, lets you explain why the assistant believes something "
                "and lets a later correction win. Today you implement `resolve` over three claims with explicit "
                "confidence and update ticks, print the winner and the overridden values, and assert the "
                "expected result. The sort is total, so equal inputs always produce the same output. This is the "
                "same problem as reconciling records in any data system, and the lesson transfers directly to "
                "assistant memory, where an unexplained contradiction is far worse than a slightly stale fact."
            ),
            code='''def resolve(claims):
    ordered = sorted(
        claims,
        key=lambda c: (-c["confidence"], -c["updated"], c["source"]),
    )
    return ordered[0], ordered[1:]

claims = [
    {"source": "profile", "value": "Pune", "confidence": 2, "updated": 4},
    {"source": "chat", "value": "Mumbai", "confidence": 3, "updated": 2},
    {"source": "form", "value": "Delhi", "confidence": 2, "updated": 5},
]
winner, losers = resolve(claims)
print("winner:", winner["source"], winner["value"])
for claim in losers:
    print("overridden:", claim["source"], claim["value"])
assert winner["value"] == "Mumbai"
print("confidence beats staleness; source name breaks full ties")''',
            variant_b="make recency outrank confidence and explain which value wins now",
            variant_c="add a verified flag that outranks both signals and test the same three claims",
            mistakes=[
                "Letting load order decide the winner without recording the policy.",
                "Deleting losing claims so a later correction has nothing to compare against.",
                "Using a partial sort key that leaves some ties non-deterministic.",
            ],
            q1=(
                "Why should losing claims be kept or logged rather than silently deleted?",
                "They explain the override, preserve audit history and allow a later correction to revisit the decision.",
            ),
            homework=(
                "Write `resolve(claims)` that sorts claims by confidence, then update tick, then source name, "
                "returning the winner and the rest. Create three conflicting claims, print the decision, and "
                "comment which line makes the result total and reproducible."
            ),
            patterns=["def ", "resolve(", "sorted("],
            mapping=(
                "Knowledge bases and assistant memory layers reconcile duplicate or contradictory facts with "
                "source trust, freshness and confidence before retrieval exposes them."
            ),
        ),
        131: dict(
            topic="Session boundaries",
            idea=(
                "A session is a boundary, and boundaries are what stop memory from leaking between contexts. "
                "One user may return on a new device, a shared kiosk may serve several people, and a support "
                "conversation may concern one order while the next concerns another. If all turns go into one "
                "global history, facts from the previous session silently become context for the next one. The "
                "fix is an explicit session id on every message and a store keyed by that id. Reads and writes "
                "should always name a session, and any cross-session summary should be deliberate rather than "
                "incidental. Even with sessions, you need a policy for what may be promoted to long-term "
                "memory: a preference the user confirms can cross sessions, while an order number probably "
                "should not. Today you build `split_sessions` from a flat message list and a tiny `memory_for` "
                "that summarises each session independently. Printing both sessions shows that the second "
                "session cannot see the first session's content. The assertion makes that isolation a test "
                "rather than a hope. Session boundaries also give you natural points to summarise, expire "
                "short-term context, and start a fresh token budget. Treating them as first-class data is much "
                "safer than inferring a boundary from timestamps or from a gap in the transcript."
            ),
            code='''def split_sessions(messages):
    sessions = {}
    for message in messages:
        sessions.setdefault(message["session"], []).append(message["content"])
    return sessions

def memory_for(turns):
    return {"turns": len(turns), "first": turns[0], "last": turns[-1]}

messages = [
    {"session": "s1", "content": "my name is Ada"},
    {"session": "s1", "content": "I like tea"},
    {"session": "s2", "content": "where is my order"},
    {"session": "s2", "content": "order 42"},
]
sessions = split_sessions(messages)
for sid in sorted(sessions):
    print(sid, memory_for(sessions[sid]))
assert "Ada" not in " ".join(sessions["s2"])
print("session ids stop private facts leaking into a new conversation")''',
            variant_b="add a third session and show that its memory starts empty",
            variant_c="promote one confirmed preference across sessions and leave the order number isolated",
            mistakes=[
                "Using one global history for every user and every visit.",
                "Inferring a session boundary from timestamps instead of explicit ids.",
                "Promoting every session fact to long-term memory without a policy.",
            ],
            q1=(
                "How does an explicit session id prevent memory leakage?",
                "Every read and write names a session, so another conversation's turns are never mixed into the current context by accident.",
            ),
            homework=(
                "Write `split_sessions(messages)` that groups turns by explicit session id, and "
                "`memory_for(turns)` summarising one session. Build two sessions, print each summary, and "
                "comment which line keeps the second session isolated."
            ),
            patterns=["def ", "session", "print("],
            mapping=(
                "Assistant platforms scope conversation memory per session or thread, and only promoted profile "
                "facts cross into later conversations."
            ),
        ),
        132: dict(
            topic="Injecting memory into the prompt",
            idea=(
                "Memory is only useful when it reaches the model, and that means prompt assembly. The prompt is "
                "a budget: a system instruction, a compact block of relevant facts, recent turns and the "
                "current question all compete for the same window. Injection order affects behaviour. Put "
                "stable instructions first, then a clearly labelled memory block, then the chronological "
                "dialogue, so the model can distinguish a remembered fact from something just said. Label the "
                "block explicitly, because an unlabelled fact looks like an assistant claim and the model may "
                "treat it as authoritative. Keep the block small and ranked, using the retrieval and scoring "
                "ideas from earlier days, and omit facts that are irrelevant to the current turn. Today you "
                "write `build_prompt`, which sorts memory keys, joins them into one labelled line, appends the "
                "last few turns verbatim and returns a single string. Printing the prompt lets you see the "
                "final shape the model would receive. The assertion checks that one remembered fact is present. "
                "This is also where mistakes become visible: duplicated facts, stale facts and private data all "
                "show up in the prompt. In a real assistant this function is the join point between storage and "
                "generation, so it deserves tests of its own."
            ),
            code='''def build_prompt(system, memory, turns, limit=3):
    facts = "; ".join(f"{k}={v}" for k, v in sorted(memory.items()))
    lines = [system, f"Known user facts: {facts}"]
    for turn in turns[-limit:]:
        lines.append(f"{turn['role']}: {turn['content']}")
    return "\\n".join(lines)

prompt = build_prompt(
    "You are a concise assistant.",
    {"name": "Ada", "drink": "tea"},
    [
        {"role": "user", "content": "What should I order?"},
        {"role": "assistant", "content": "Tea, as usual?"},
        {"role": "user", "content": "Yes please."},
    ],
)
print(prompt)
assert "name=Ada" in prompt
print("memory is injected once, recent turns stay verbatim")''',
            variant_b="limit the memory block to two ranked facts and explain what you would drop first",
            variant_c="add a token estimate based on whitespace words and show the budget used",
            mistakes=[
                "Dumping every stored fact into the prompt on every turn.",
                "Leaving memory unlabelled so it reads like assistant prose.",
                "Duplicating a fact in memory and again in the recent turns.",
            ],
            q1=(
                "Why label the memory block separately from the recent dialogue?",
                "A label tells the model these are stored facts rather than something just said, which reduces confusion and makes the prompt auditable.",
            ),
            homework=(
                "Write `build_prompt(system, memory, turns, limit)` that injects a sorted, labelled memory "
                "block before the most recent turns. Print the assembled prompt for a small transcript, and "
                "comment which line keeps memory distinct from dialogue."
            ),
            patterns=["def ", "build_prompt(", "join("],
            mapping=(
                "RAG systems assemble retrieved context and profile facts into a labelled prompt block before "
                "generation; the same budget decisions control assistant quality and cost."
            ),
        ),
        133: dict(
            topic="Testing memory behaviour",
            idea=(
                "Memory code fails in ways that are easy to miss during a demo: a duplicate slips in, an expired "
                "fact survives, a fact from one session appears in another, or a redaction rule stops matching "
                "after a format change. The answer is small, boring tests written before the bug reaches "
                "production. You do not need a framework to get most of the value. Plain functions plus `assert` "
                "statements give you fast, deterministic checks, and a single script that exits non-zero on "
                "failure is enough for a first suite. Good tests target behaviour, not internals: after "
                "remembering the same fact twice it appears once; after its TTL it disappears; a new session "
                "starts empty. Keep time and data explicit so the tests never depend on the machine. Today you "
                "write `remember`, `is_active` and three assertions covering deduplication, expiry and session "
                "isolation, then print one line confirming the checks passed. The point is not the tiny example "
                "but the habit. Every memory feature you add later, retrieval, ranking, conflict resolution, "
                "prompt injection, should arrive with at least one check that would fail if the logic broke. "
                "Those checks also document the intended policy, which is invaluable when someone changes a "
                "weight or a TTL months later."
            ),
            code='''def normalise(text):
    return " ".join(text.lower().split())

def remember(store, fact):
    key = normalise(fact)
    store[key] = store.get(key, 0) + 1
    return store

def is_active(entry, now):
    return now - entry["created"] <= entry["ttl"]

store = {}
remember(store, "Likes tea")
remember(store, "likes tea")
assert store == {"likes tea": 2}

assert is_active({"created": 2, "ttl": 3}, 5)
assert not is_active({"created": 2, "ttl": 3}, 6)

s1, s2 = {"name": "Ada"}, {}
assert "name" not in s2
print("dedupe, expiry and isolation checks passed")''',
            variant_b="add a failing assertion for an unredacted email and read the failure message it produces",
            variant_c="test a ranking tie by asserting the exact output order for two equal scores",
            mistakes=[
                "Testing with the real clock and making results change from run to run.",
                "Checking private helper internals instead of observable memory behaviour.",
                "Adding memory features without a check that would fail when the policy breaks.",
            ],
            q1=(
                "What makes a good test for memory behaviour?",
                "It targets an observable policy such as deduplication, expiry or session isolation, uses explicit inputs and time, and fails clearly when that policy breaks.",
            ),
            homework=(
                "Write `remember(store, fact)` and `is_active(entry, now)` plus assertions covering "
                "deduplication, expiry and session isolation. Print one success line, and comment which "
                "assertion would fail if the TTL comparison were off by one."
            ),
            patterns=["def ", "assert", "print("],
            mapping=(
                "Evaluation suites for assistant memory assert deduplication, freshness and per-session "
                "isolation before retrieval quality is measured end to end."
            ),
        ),
        134: dict(
            topic="Review: context and memory checklist",
            idea=(
                "The end of a phase is a good time to turn everything you have learned into a checklist, because "
                "memory bugs usually come from a missing policy rather than a missing line of code. This is especially true once storage, retrieval and prompt assembly interact. A review "
                "should confirm that context and durable memory are stored separately, that history trimming "
                "preserves the system prompt, that old turns are summarised rather than silently dropped, and "
                "that long-term facts carry provenance. It should also check retrieval, ranking and "
                "deduplication, because a memory you cannot find or trust is not useful. Expiry needs an "
                "explicit clock source, redaction needs to run before storage, and conflicts need a documented "
                "winner. Sessions need isolation, prompt injection needs a clear label and a size limit, and "
                "every one of these behaviours needs at least one test. Today you encode a short checklist as "
                "data, evaluate each item with a boolean, print pass or fail per item and collect the failures. "
                "The deliberately failing item shows the value of the exercise: a checklist that can never fail "
                "is decoration. Use this list when you review your own assistant, and extend it whenever a real "
                "incident teaches you a new failure mode."
            ),
            code='''def check(items):
    results = {}
    for name, passed in items:
        results[name] = bool(passed)
    failed = [name for name in sorted(results) if not results[name]]
    return results, failed

memory = {"name": "Ada"}
history = [{"role": "user", "content": "hi"}]
store = ["likes tea", "likes tea"]
items = [
    ("system prompt present", True),
    ("history trimmed", len(history) <= 8),
    ("named fact stored", "name" in memory),
    ("private span redacted", "ada@example.com" not in "[email]"),
    ("duplicates removed", len(set(store)) == len(store)),
]
results, failed = check(items)
for name in sorted(results):
    print(f"{name:20} {'pass' if results[name] else 'fail'}")
print("failed:", failed)
assert failed == ["duplicates removed"]
print("a checklist turns memory design into testable gates")''',
            variant_b="add checklist items for expiry and session isolation and mark the ones your current code passes",
            variant_c="split the checklist into must-pass and advisory items and print two failure lists",
            mistakes=[
                "Treating the checklist as documentation rather than executable checks.",
                "Reviewing retrieval while ignoring redaction and session isolation.",
                "Accepting a checklist where every item always passes by construction.",
            ],
            q1=(
                "Why turn a memory review into a checklist with executable checks?",
                "It makes each policy explicit and testable, so a missing boundary, expiry rule or redaction step fails visibly instead of becoming a production incident.",
            ),
            homework=(
                "Write `check(items)` that evaluates named checks and returns a results dict plus a sorted "
                "failure list. Include at least six memory and context items, print each result, and comment "
                "which item you would add after your next real failure."
            ),
            patterns=["def ", "check(", "failed"],
            mapping=(
                "Production assistant reviews cover context limits, memory provenance, expiry, privacy and "
                "retrieval quality, with each policy backed by an automated check or evaluation case."
            ),
        ),
    },
)
