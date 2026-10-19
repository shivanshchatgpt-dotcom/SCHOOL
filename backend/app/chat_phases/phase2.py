"""Intents and responses, days 90-104: rules you can read, score and test.

Every example is stdlib-only, offline and deterministic (no network, no model
call, no clock), so the applier can execute it and produce the same output every
run. A message is a string, an intent table is a dict, scoring is a pure
function of the text, and decisions are printed in a stable order.
"""

PHASE = (
    "Intents and Responses",
    "Turn user text into a scored, testable intent decision with a helpful reply.",
    {
        90: dict(
            topic="Orientation: rules before models",
            idea=(
                "Before reaching for a classifier or a language model, it helps to build the simplest thing that "
                "could possibly work: a bot whose behaviour you can read top to bottom. A rules-first orientation "
                "means you write down what the user might say, what the bot should do, and how you will tell "
                "whether the decision was right, all before any model enters the picture. The value is not that "
                "rules are always enough. The value is that rules make the whole pipeline visible: input, "
                "decision, response. You can point at the exact line that chose an answer, which is nearly "
                "impossible once a statistical model is making the choice. A rule bot also gives you a baseline to "
                "beat. If a model cannot outscore a table of a dozen hand-written patterns on your own traffic, "
                "the model is not buying you anything yet. Today you build the smallest such bot: a list of "
                "candidate messages, a tiny table of trigger words, and a loop that prints the decision for each "
                "message in a fixed order. Resist the urge to add cleverness early. The goal is a skeleton you "
                "fully understand, so that every later idea — intents, entities, scoring, confidence — can be "
                "bolted onto something you trust. Rules first, models later."
            ),
            code=(
                'RULES = [\n'
                '    ("greeting", "hello"),\n'
                '    ("farewell", "bye"),\n'
                '    ("help", "help"),\n'
                ']\n'
                '\n'
                'def reply(text):\n'
                '    lowered = text.lower()\n'
                '    for name, trigger in RULES:\n'
                '        if trigger in lowered:\n'
                '            return name\n'
                '    return "fallback"\n'
                '\n'
                'for text in ["Hello there", "I need help", "Goodbye", "thanks"]:\n'
                '    print(f"{text!r:16} -> {reply(text)}")\n'
                '\n'
                'assert reply("bye now") == "farewell"\n'
                'print("rules first: every decision is a readable lookup")'
            ),
            variant_b='add an "hours" rule matching "open" and place it above the greeting rule, then rerun',
            variant_c='return the matched trigger as well as the name and print both for each message',
            mistakes=[
                "Jumping to a model before writing down the cases the bot must handle.",
                "Hiding the decision inside nested if-statements with no single place to inspect it.",
                "Building no baseline, so nobody can tell whether a model improved anything.",
            ],
            q1=(
                "Why build a rule-based bot before trying a model?",
                "It is fully inspectable and gives a cheap baseline; if a model cannot beat it, the model is not helping.",
            ),
            homework=(
                "Write `reply_from_rules(text, rules)` that returns the intent name whose trigger appears in the "
                "lowered text, or \"fallback\". Build a three-rule table, run it on four messages covering each "
                "rule and one miss, print the decisions in order, and comment which line makes the fallback "
                "explicit."
            ),
            patterns=["def reply_from_rules", "for ", "return"],
            mapping=(
                "Dialogflow, Rasa and Amazon Lex all begin with intents triggered by example utterances; a rules "
                "bot is the same idea with the matching written by hand."
            ),
        ),
        91: dict(
            topic="An intent table",
            idea=(
                "An intent table is a plain mapping from an intent name to the utterances that should trigger it. "
                "Writing it as data rather than as nested if-statements changes what the code can do. Data can be "
                "counted, edited by non-programmers, loaded from a file, and tested in bulk. When intents live in "
                "a dict, adding a new one is a one-line change and cannot accidentally reorder another rule. The "
                "table is also the natural place to keep example utterances, because those examples double as "
                "documentation for humans and as fixtures for the matcher. Two design habits pay off immediately. "
                "Give every intent a stable name in one naming convention, because those names travel into logs, "
                "metrics and training sets. And keep the utterances lowercase and punctuation-free at rest, doing "
                "normalisation once at the edges, so the table has a single canonical form. Today you build a "
                "table for three intents, write a lookup that iterates it in sorted order for reproducibility, and "
                "print the match for a handful of messages. The table is boring on purpose. Boring here means no "
                "hidden control flow, which is exactly what you want when the bot later misclassifies something "
                "and you have to explain why."
            ),
            code=(
                'INTENTS = {\n'
                '    "greet": ["hi", "hello", "hey"],\n'
                '    "balance": ["check my balance", "account balance"],\n'
                '    "cancel": ["cancel my order", "cancel order"],\n'
                '}\n'
                '\n'
                'def match(text):\n'
                '    lowered = text.lower().strip()\n'
                '    for name in sorted(INTENTS):\n'
                '        for phrase in INTENTS[name]:\n'
                '            if phrase in lowered:\n'
                '                return name, phrase\n'
                '    return "fallback", None\n'
                '\n'
                'for text in ["hey there", "cancel order 12", "check my balance", "who are you"]:\n'
                '    name, phrase = match(text)\n'
                '    print(f"{text!r:20} -> {name:8} ({phrase})")'
            ),
            variant_b='add a "refund" intent with two utterances and print the match for two new messages',
            variant_c='return every matching intent instead of the first, and explain when that is more useful',
            mistakes=[
                "Writing each intent as a separate branch so the set cannot be counted or iterated.",
                "Inconsistent intent names across the table, which break logs and metrics later.",
                "Storing utterances with mixed case and punctuation, forcing every matcher to re-clean them.",
            ],
            q1=(
                "Why store intents as a dict of utterance lists rather than as if-statements?",
                "Data can be counted, edited and tested in bulk, and new intents never silently reorder existing rules.",
            ),
            homework=(
                "Write `match_intent(text, intents)` that returns the first intent name and phrase found by "
                "scanning the table in sorted order, or (\"fallback\", None). Add three intents with two utterances "
                "each, test four messages, print each decision, and comment which line keeps the scan order stable."
            ),
            patterns=["def match_intent", "sorted", "return"],
            mapping=(
                "This table is what Dialogflow calls training phrases grouped under an intent, and what Rasa stores "
                "in its NLU training data."
            ),
        ),
        92: dict(
            topic="Keyword and phrase matching",
            idea=(
                "Two bots that both look for words can behave very differently depending on whether they match "
                "single keywords or whole phrases. A keyword match splits the text into tokens and asks whether a "
                "trigger token is present. A phrase match asks whether a multiword expression appears in order. "
                "Keywords are cheap and forgiving, but they fire on noise: matching the token \"hi\" will trigger a "
                "greeting inside unrelated words if you use naive substring search, and splitting on whitespace "
                "avoids that by comparing whole tokens. Phrases are more precise but brittle: \"reset my password\" "
                "will not match \"reset the password\" because the middle word changed. Good matchers often use both, "
                "letting a strong phrase outrank a weak keyword. The practical rules are to normalise case once, to "
                "match phrases against a space-padded string so a phrase cannot match inside a longer word, and to "
                "iterate in a fixed order so results never shuffle between runs. Today you write both matchers, run "
                "them over the same messages, and print the keywords found and the phrases hit side by side. Seeing "
                "the two columns next to each other is the fastest way to feel why precision and recall pull in "
                "opposite directions."
            ),
            code=(
                'def keywords(text):\n'
                '    return set(text.lower().split())\n'
                '\n'
                'def phrase_hits(text):\n'
                '    padded = " " + text.lower().strip() + " "\n'
                '    phrases = {"reset my password": "reset_password", "my password": "password"}\n'
                '    return [name for phrase, name in phrases.items() if " " + phrase + " " in padded]\n'
                '\n'
                'for text in ["how do I reset my password", "i forgot my password", "hello"]:\n'
                '    print(f"{text!r:30} keywords={sorted(keywords(text))} phrases={phrase_hits(text)}")'
            ),
            variant_b='add a keyword matcher that ignores stop words like "the" and "my", then rerun',
            variant_c='match phrases against a token tuple so word order matters but extra words are allowed',
            mistakes=[
                "Substring-matching short keywords so they fire inside unrelated longer words.",
                "Matching phrases without padding, so a phrase also triggers inside a bigger word.",
                "Iterating an unordered structure, so the printed matches change between runs.",
            ],
            q1=(
                "Why pad the text with spaces before matching a phrase?",
                "It ensures the phrase matches as whole words and cannot trigger from inside a longer word.",
            ),
            homework=(
                "Write `phrase_match(text, phrases)` that returns a list of intent names whose multiword phrase "
                "appears as a whole phrase in the text. Register three phrases including one that overlaps a "
                "shorter phrase, test messages that trigger both, print each result, and comment which line "
                "prevents a substring from matching by accident."
            ),
            patterns=["def phrase_match", "return", "print("],
            mapping=(
                "Lex and Dialogflow treat example phrases as literal training utterances; hand-written phrase "
                "matching is the transparent version of that idea."
            ),
        ),
        93: dict(
            topic="Regular expressions for intents",
            idea=(
                "Keywords and phrases handle fixed wording, but real users pad sentences with optional words, "
                "numbers and punctuation. Regular expressions describe those shapes. A pattern can say \"the word "
                "cancel, then optional whitespace, then an order number\" in one line, and it can match many "
                "phrasings you would otherwise have to list by hand. Three habits keep regex intents maintainable. "
                "Compile each pattern once at module level rather than rebuilding it on every message, because "
                "compilation is the expensive part. Anchor with word boundaries so a pattern for \"order\" does not "
                "fire inside \"border\". And test regexes with a small table of inputs, because a regex that looks "
                "right often fails on a trailing period or a missing space. A regex is also a natural place to "
                "capture a value: wrapping the digits in a group lets you pull the order number straight out of the "
                "match instead of parsing it again later. Today you write three compiled patterns, search them over "
                "several messages, and print the list of intents that matched. Notice that a single message can "
                "legitimately match more than one pattern, which is why the next lessons are about scoring and "
                "priority rather than first-match-wins. A pattern that is hard to read is a pattern that will be "
                "wrong later, so write the regex and then write a test beside it, using inputs that look like the "
                "real messages your bot will receive."
            ),
            code=(
                'import re\n'
                '\n'
                'PATTERNS = [\n'
                '    ("cancel", re.compile(r"\\bcancel\\b")),\n'
                '    ("order_id", re.compile(r"\\border\\s*#?(\\d+)\\b")),\n'
                '    ("greet", re.compile(r"\\b(hi|hello|hey)\\b")),\n'
                ']\n'
                '\n'
                'def route(text):\n'
                '    lowered = text.lower()\n'
                '    return [name for name, pattern in PATTERNS if pattern.search(lowered)]\n'
                '\n'
                'for text in ["hello", "cancel order 42", "cancel #7 please", "nothing here"]:\n'
                '    print(f"{text!r:20} -> {route(text)}")\n'
                '\n'
                'assert route("cancel order 42") == ["cancel", "order_id"]\n'
                'print("compiled patterns find every intent that matches")'
            ),
            variant_b='add a "refund" pattern requiring the words refund or money back, then rerun the routing',
            variant_c='use a capturing group to pull the order number out and print it beside the matched intents',
            mistakes=[
                "Recompiling the same pattern on every message instead of compiling once.",
                "Omitting word boundaries, so a pattern fires inside a larger unrelated word.",
                "Assuming a regex is correct without testing trailing punctuation and spacing.",
            ],
            q1=(
                "Why compile a regular expression once at module level?",
                "Compilation is the expensive step; reusing the compiled pattern avoids repeating that work on every message.",
            ),
            homework=(
                "Write `compile_intents(pairs)` that compiles a list of (name, pattern) pairs with `re.compile`, "
                "and `route(text, compiled)` returning the names of every pattern that searches the lowered text. "
                "Test three utterances, print the matches, and comment which line uses word boundaries to avoid "
                "partial matches."
            ),
            patterns=["def route", "re.compile", "return"],
            mapping=(
                "Rasa supports regex-based intent features and entity rules; the same compiled patterns power "
                "custom slot extractors in Dialogflow and Lex."
            ),
        ),
        94: dict(
            topic="Scoring candidate intents",
            idea=(
                "When more than one intent could apply, first-match-wins is too blunt. Scoring gives every "
                "candidate a number and lets the highest win, which turns routing into a small ranking problem. "
                "The simplest useful score is overlap: count how many of an intent's example words actually appear "
                "in the message, optionally weighting rarer words higher. Overlap alone is crude, so most systems "
                "normalise it, dividing by the number of example words or by the length of the message, so a long "
                "intent is not penalised simply for having more keywords. Two engineering details matter more than "
                "the formula. First, scoring must be a pure function of the text and the table, so the same input "
                "always yields the same ranking; never let dict ordering or a clock leak in. Second, break ties "
                "deterministically, usually by the intent name, so results are stable and testable. Today you score "
                "three intents by token overlap, sort the scored pairs by descending score and then name, and print "
                "the ranked list for several messages. Because the output is sorted and the score is arithmetic, "
                "you can assert on it directly, which is exactly the property you want before adding thresholds or "
                "confidence cut-offs on top."
            ),
            code=(
                'INTENTS = {\n'
                '    "weather": "what is the weather forecast today".split(),\n'
                '    "news": "latest news headlines today".split(),\n'
                '    "joke": "tell me a joke".split(),\n'
                '}\n'
                '\n'
                'def score(text, words):\n'
                '    tokens = set(text.lower().split())\n'
                '    return sum(1 for word in words if word in tokens)\n'
                '\n'
                'def rank(text):\n'
                '    scored = [(score(text, words), name) for name, words in INTENTS.items()]\n'
                '    return sorted(scored, key=lambda pair: (-pair[0], pair[1]))\n'
                '\n'
                'for text in ["weather today", "tell me a joke", "news headlines"]:\n'
                '    print(f"{text!r:18} -> {rank(text)}")\n'
                '\n'
                'assert rank("weather today")[0][1] == "weather"\n'
                'print("candidates are ranked by a pure, sortable score")'
            ),
            variant_b='normalise each score by the number of example words and rerun the ranking',
            variant_c='weight each example word by one over its frequency across intents, then rerank',
            mistakes=[
                "Letting dict order decide ties, so results drift between runs and cannot be asserted.",
                "Comparing raw overlap without normalising, so longer intents always win.",
                "Scoring with side effects such as logging, making the ranking unpredictable.",
            ],
            q1=(
                "Why sort scored intents by score and then by name?",
                "The name tie-break makes the ranking deterministic, so equal scores never change the output between runs.",
            ),
            homework=(
                "Write `rank_intents(text, intents)` that scores each intent by the number of its example words "
                "present as whole tokens and returns pairs sorted by descending score then name. Test three "
                "utterances, print the ranked list, and comment which line makes ties deterministic."
            ),
            patterns=["def rank_intents", "sorted", "return"],
            mapping=(
                "This overlap score is a skeletal version of the confidence Rasa and Dialogflow report for an "
                "intent, both of which rank candidates rather than stopping at the first hit."
            ),
        ),
        95: dict(
            topic="Fallbacks that help",
            idea=(
                "A fallback is the reply a bot gives when no intent is confident enough, and it is the single "
                "biggest driver of whether users trust the bot. A bad fallback says \"I did not understand\" and "
                "stops. A good fallback admits the miss, keeps the conversation alive, and tells the user what the "
                "bot can actually do. The design rule is that every turn ends with a message, even a miss, because "
                "silence looks like a crash. It also helps to make the fallback specific: instead of one generic "
                "line, offer the two or three intents the bot supports, so the user can rephrase into something "
                "recognisable. Since the next lessons add confidence thresholds, today you keep the decision simple "
                "— a fixed set of triggers plus one fallback — but you shape the fallback text carefully. You also "
                "log which messages fell through, because those are your best source of new examples for the intent "
                "table. Today you respond to a handful of messages, returning both the intent and the reply, and "
                "print a fallback that names the supported topics. The habit to keep is that the fallback is a "
                "first-class response, not an afterthought. Treat the fallback as part of the product, review its "
                "wording as carefully as any other reply, and it will carry a surprising amount of the user "
                "experience on its own."
            ),
            code=(
                'RESPONSES = {"greet": "Hello!", "weather": "It is sunny.", "help": "I can answer weather."}\n'
                '\n'
                'def respond(text):\n'
                '    lowered = text.lower()\n'
                '    if "hi" in lowered:\n'
                '        return "greet", RESPONSES["greet"]\n'
                '    if "weather" in lowered:\n'
                '        return "weather", RESPONSES["weather"]\n'
                '    if "help" in lowered:\n'
                '        return "help", RESPONSES["help"]\n'
                '    return "fallback", "I am not sure. You can ask about the weather or type help."\n'
                '\n'
                'for text in ["hi", "weather?", "book a flight"]:\n'
                '    intent, reply = respond(text)\n'
                '    print(f"{text!r:16} {intent:9} {reply}")'
            ),
            variant_b='offer two suggestions in the fallback and count how often each intent fires',
            variant_c='return a list of supported intents from the fallback so the caller can render them',
            mistakes=[
                "Replying with silence or an empty string when nothing matches.",
                "Using one vague fallback that never tells the user what the bot can do.",
                "Throwing away missed messages instead of logging them as future examples.",
            ],
            q1=(
                "What makes a fallback helpful rather than merely polite?",
                "It admits the miss, keeps the turn alive with a visible reply, and tells the user which intents the bot supports.",
            ),
            homework=(
                "Write `respond(text)` that returns an (intent, reply) tuple, using a fallback reply that names "
                "what the bot can do when nothing matches. Cover three intents plus the fallback, test four "
                "messages, print each tuple, and comment which line guarantees a non-empty reply."
            ),
            patterns=["def respond", "return", "fallback"],
            mapping=(
                "Dialogflow has a dedicated fallback intent and Rasa ships a default fallback; both exist precisely "
                "so the bot never answers with silence."
            ),
        ),
        96: dict(
            topic="Response templates",
            idea=(
                "Once routing knows the intent, the reply is often the same sentence with one or two values "
                "swapped in. Writing that sentence as a template keeps wording in one place and logic in another, "
                "so you can fix a typo without touching code and add a language without rewriting the handler. A "
                "template is a string with named placeholders, filled from a dict of slot values. Python's "
                "`str.format` does this directly, and it fails loudly when a required slot is missing, which is far "
                "better than silently printing a placeholder. The discipline is to name placeholders after the slot "
                "schema, not after the sentence, so the template and the extractor agree. Keep templates free of "
                "logic: no conditionals, no method calls, just text and names. When a reply genuinely branches, use "
                "two templates and choose between them in code rather than embedding an if-statement in the string. "
                "Today you build two templates, render them with slot dicts, and print the results. Notice that "
                "rendering is a pure function of the template and the slots, so every reply is reproducible and can "
                "be checked against an expected string in a test. When a reply later needs to vary by tone or "
                "language, you change the template, not the handler, and the routing logic stays exactly as it "
                "was."
            ),
            code=(
                'TEMPLATES = {\n'
                '    "greet": "Hello, {name}!",\n'
                '    "order": "Order {order_id} is {status}.",\n'
                '}\n'
                '\n'
                'def render(intent, slots):\n'
                '    return TEMPLATES[intent].format(**slots)\n'
                '\n'
                'print(render("greet", {"name": "Ada"}))\n'
                'print(render("order", {"order_id": "42", "status": "shipped"}))\n'
                '\n'
                'assert render("order", {"order_id": "7", "status": "pending"}) == "Order 7 is pending."\n'
                'print("templates keep wording separate from logic")'
            ),
            variant_b='add a "weather" template with a {city} placeholder and render it for two cities',
            variant_c='render a template with a missing slot inside try/except and print the KeyError message',
            mistakes=[
                "Embedding conditionals and method calls inside the template string.",
                "Naming placeholders after sentence words instead of the slot schema, so they drift apart.",
                "Silently substituting an empty string for a missing slot instead of failing loudly.",
            ],
            q1=(
                "Why name template placeholders after the slot schema?",
                "It keeps the template and the extractor in agreement, so a renamed slot breaks visibly rather than silently.",
            ),
            homework=(
                "Write `render(template, slots)` that fills a `str.format` template from a dict of slot values and "
                "raises a clear error when a slot is missing. Register two templates, render one complete and one "
                "partial case inside try/except, print both, and comment which line catches the missing slot."
            ),
            patterns=["def render", "format", "except"],
            mapping=(
                "Dialogflow response sections and Rasa response templates both separate the wording from the "
                "handler, so the same intent can speak in several tones or languages."
            ),
        ),
        97: dict(
            topic="Extracting entities",
            idea=(
                "An intent says what the user wants; an entity says which thing they want it about. \"Cancel "
                "order 42\" carries the intent cancel and the entity order_id 42, and the handler cannot act "
                "without that number. Entities are usually pulled out with a pattern — a regular expression that "
                "matches a shape such as digits after the word order, or a quantity after for. The important "
                "discipline is to extract into named fields and to leave a field out entirely when the text does "
                "not contain it, rather than inserting a placeholder that later code mistakes for a real value. A "
                "missing entity is meaningful information: it tells the bot to ask a follow-up question. Keep the "
                "extractors independent, one per entity type, so a change to how order numbers are matched cannot "
                "break how quantities are matched. And always test the negative case, a message with none of the "
                "entities, because that is where extractors most often misbehave by capturing something accidental. "
                "Today you write a small extractor that finds an order id and a quantity, run it on messages that "
                "carry each combination, and print the dict of entities found. Absent keys, not null values, are "
                "the clearest signal that the bot still needs to ask."
            ),
            code=(
                'import re\n'
                '\n'
                'def extract(text):\n'
                '    lowered = text.lower()\n'
                '    found = {}\n'
                '    order = re.search(r"\\border\\s*#?(\\d+)\\b", lowered)\n'
                '    if order:\n'
                '        found["order_id"] = order.group(1)\n'
                '    quantity = re.search(r"\\b(?:for|qty)\\s+(\\d+)\\b", lowered)\n'
                '    if quantity:\n'
                '        found["quantity"] = quantity.group(1)\n'
                '    return found\n'
                '\n'
                'for text in ["cancel order 42", "order 7 for 3 people", "nothing here"]:\n'
                '    print(f"{text!r:26} -> {extract(text)}")\n'
                '\n'
                'assert extract("nothing here") == {}\n'
                'print("missing entities stay absent instead of null")'
            ),
            variant_b='add an "email" entity matched with a simple pattern and print it for two messages',
            variant_c='return which required entities are missing alongside the ones extracted',
            mistakes=[
                "Inserting null or empty placeholders for entities that were not found.",
                "Mixing all extraction into one tangled pattern so one change breaks every entity.",
                "Never testing the message that contains no entities at all.",
            ],
            q1=(
                "Why leave a field out of the result instead of setting it to None?",
                "An absent key clearly signals the entity was never found, which tells the bot to ask a follow-up question.",
            ),
            homework=(
                "Write `extract_entities(text)` that finds an order id and a quantity with `re.search` and returns "
                "a dict of the entities present. Test a message with both, one with only the id, and one with "
                "neither, print each dict, and comment which line keeps a missing entity out of the result."
            ),
            patterns=["def extract_entities", "re.search", "return"],
            mapping=(
                "These named fields are what Dialogflow calls parameters and Rasa calls entities; the same values "
                "become the arguments of a tool call in later lessons."
            ),
        ),
        98: dict(
            topic="Synonyms and normalisation",
            idea=(
                "Users do not share one vocabulary. One says buy, another purchase, a third acquire; one types "
                "how much, another asks for the price. If your matcher only knows the word you happened to write "
                "in the table, it will miss perfectly clear requests. Normalisation fixes this by mapping many "
                "surface forms onto one canonical form before matching, so the intent table only ever sees the "
                "canonical words. A synonym map plus case folding and whitespace cleanup is a small amount of code "
                "that buys a large amount of recall. Two practical warnings. Replace longer phrases before shorter "
                "ones, or \"how much\" may be partly rewritten before the phrase rule sees it. And apply "
                "normalisation in exactly one place, at the boundary where text enters the matcher, so you never "
                "have to guess whether a string has already been cleaned. Keep the map honest by starting only with "
                "synonyms you can defend; an over-eager map can collapse words that users mean differently. Today "
                "you build a small synonym map, normalise a few phrasings of the same request, and print the "
                "canonical text each becomes. Watching three different sentences converge on one output is the "
                "clearest demonstration of why normalisation belongs before matching."
            ),
            code=(
                'SYNONYMS = {"purchase": "buy", "acquire": "buy", "cost": "price", "how much": "price"}\n'
                '\n'
                'def normalise(text):\n'
                '    lowered = text.lower()\n'
                '    for word in sorted(SYNONYMS, key=len, reverse=True):\n'
                '        lowered = lowered.replace(word, SYNONYMS[word])\n'
                '    return " ".join(lowered.split())\n'
                '\n'
                'for text in ["I want to purchase this", "Acquire it", "How much is it?"]:\n'
                '    print(f"{text!r:26} -> {normalise(text)!r}")\n'
                '\n'
                'assert "buy" in normalise("purchase now")\n'
                'print("normalisation maps surface forms onto canonical words")'
            ),
            variant_b='add "cant" -> "cannot" and "dont" -> "do not" and normalise two more messages',
            variant_c='strip punctuation before replacing and show how the canonical form changes',
            mistakes=[
                "Replacing short synonyms before long ones, so a phrase is only partly rewritten.",
                "Normalising in several places, so no one knows whether a string is already clean.",
                "Adding synonyms that collapse words users actually mean differently.",
            ],
            q1=(
                "Why replace longer synonyms before shorter ones?",
                "A shorter word can be a substring of the phrase, so replacing it first would leave the phrase partly rewritten.",
            ),
            homework=(
                "Write `normalise(text, synonyms)` that lowers the text and replaces each synonym with its "
                "canonical word before matching. Build a small synonym map, normalise three phrasings of one "
                "request, print the results, and comment which line makes \"how much\" collapse onto the price intent."
            ),
            patterns=["def normalise", "replace", "return"],
            mapping=(
                "Rasa synonym mappings and Dialogflow entity synonyms do exactly this, mapping many surface forms "
                "onto one canonical value before intent matching."
            ),
        ),
        99: dict(
            topic="Multiple matches and priority",
            idea=(
                "Real messages often match several rules at once. \"Hi, I need to reset my account\" contains a "
                "greeting and two possible tasks, and first-match-wins would decide the outcome purely by the "
                "order someone happened to write the rules. Priority replaces accident with intent. Give every "
                "rule a number that expresses how specific or important it is, collect all the rules that match, "
                "and return the highest-priority one, breaking ties by name so the result stays deterministic. "
                "Specific rules outrank general ones: a rule about resetting a password should beat a rule about "
                "greetings, because the greeting is almost always incidental when a real request follows. This is "
                "also where the shape of the data matters. If priority lives beside each rule in the table, "
                "changing which rule wins is a visible one-line edit rather than a cut-and-paste that can break "
                "other rules. Today you register three rules with overlapping keywords and explicit priorities, "
                "match two messages, and print the sorted list of matches so you can see both who won and who was "
                "outranked. Seeing the losers is what lets you later explain a surprising answer to a colleague "
                "instead of shrugging. Priority is a promise about intent that you can read, change and test like "
                "any other value."
            ),
            code=(
                'RULES = [\n'
                '    ("reset_password", 50, "reset"),\n'
                '    ("account_help", 20, "account"),\n'
                '    ("greet", 10, "hi"),\n'
                ']\n'
                '\n'
                'def matches(text, rules):\n'
                '    lowered = text.lower()\n'
                '    hits = [(priority, name) for name, priority, keyword in rules if keyword in lowered]\n'
                '    return sorted(hits, reverse=True)\n'
                '\n'
                'for text in ["hi, I need to reset my account", "hi there"]:\n'
                '    print(f"{text!r:34} -> {matches(text, RULES)}")\n'
                '\n'
                'assert matches("hi, reset my account", RULES)[0][1] == "reset_password"\n'
                'print("priority decides when several rules match")'
            ),
            variant_b='add a low-priority "smalltalk" rule matching "how are you" and rerun both messages',
            variant_c='return the top intent and the list of outranked intents separately',
            mistakes=[
                "Letting the hand-written order of rules decide the outcome instead of explicit priority.",
                "Returning only the winner, hiding which other rules also matched.",
                "Choosing a priority scheme with ties that are never broken deterministically.",
            ],
            q1=(
                "Why give specific rules a higher priority than general ones?",
                "A specific request is usually the real purpose of the message, while a greeting is incidental when it appears alongside a task.",
            ),
            homework=(
                "Write `top_intent(text, rules)` that returns the highest-priority matching intent name where each "
                "rule carries a numeric priority, or None. Register three rules with overlapping keywords, test two "
                "messages, print the winners, and comment which line makes priority decide the tie."
            ),
            patterns=["def top_intent", "sorted", "return"],
            mapping=(
                "Rasa policies and Dialogflow intent ordering both resolve competing matches by priority or "
                "confidence rather than by the order rules were created."
            ),
        ),
        100: dict(
            topic="Confidence thresholds",
            idea=(
                "A score is not a decision. Knowing that the weather intent scored 0.4 is useless until you "
                "choose a line above which the bot answers and below which it falls back. That line is the "
                "confidence threshold, and picking it is a trade-off. Set it too low and the bot guesses, "
                "confidently answering questions it only half recognised. Set it too high and it falls back on "
                "requests it actually understood, which feels obtuse. There is no universal right value; the "
                "threshold depends entirely on how costly a wrong answer is versus a fallback. What matters is that the "
                "threshold is explicit, in one named constant, so it can be tuned against labelled examples "
                "instead of being hidden in a comparison somewhere. Confidence itself needs a definition; the "
                "simplest is the share of the message's tokens that were matched by the intent, which naturally "
                "penalises short, thin evidence. Guard the empty message, because dividing by zero tokens is the "
                "classic crash. Today you compute a per-message confidence, compare it to a named threshold, and "
                "print the intent, its confidence and the final decision. Printing all three makes it obvious when "
                "the threshold, not the matcher, is causing a fallback."
            ),
            code=(
                'THRESHOLD = 0.5\n'
                'KEYWORDS = {"weather", "forecast"}\n'
                '\n'
                'def confidence(text):\n'
                '    tokens = text.lower().split()\n'
                '    if not tokens:\n'
                '        return 0.0\n'
                '    hits = sum(1 for token in tokens if token in KEYWORDS)\n'
                '    return round(hits / len(tokens), 2)\n'
                '\n'
                'for text in ["weather forecast", "weather please", "sing a song"]:\n'
                '    score = confidence(text)\n'
                '    decision = "answer" if score >= THRESHOLD else "fallback"\n'
                '    print(f"{text!r:18} confidence={score:.2f} -> {decision}")\n'
                '\n'
                'assert confidence("") == 0.0\n'
                'print("a threshold turns a score into a decision")'
            ),
            variant_b='raise the threshold to 0.75 and rerun, then discuss which message changed decision',
            variant_c='normalise confidence by the number of keywords instead of message length and compare',
            mistakes=[
                "Leaving the threshold as a bare magic number buried in a comparison.",
                "Dividing by the token count without guarding the empty message.",
                "Answering confidently on a thin score instead of falling back.",
            ],
            q1=(
                "What is the risk of setting the confidence threshold too low?",
                "The bot confidently answers questions it only half recognised, which is harder for users to forgive than an honest fallback.",
            ),
            homework=(
                "Write `decide(text, keywords, threshold)` returning (intent, confidence, decision) where the "
                "decision is \"answer\" at or above the threshold and \"fallback\" below. Test a clear message, a "
                "weak one and an empty one, print all three, and comment which line stops the empty input from "
                "dividing by zero."
            ),
            patterns=["def decide", "threshold", "return"],
            mapping=(
                "Dialogflow and Rasa both expose a confidence value and a configurable threshold, and both ship "
                "a fallback that fires whenever the top intent falls below it."
            ),
        ),
        101: dict(
            topic="Disambiguation questions",
            idea=(
                "Sometimes the honest answer is that the bot does not know which of two intents the user meant, "
                "and the best reply is a short question rather than a guess. When the top two candidate scores are "
                "close, guessing is a coin flip that users experience as the bot not listening; asking \"did you "
                "mean this or that?\" converts an ambiguous input into a clean, unambiguous one. The trigger is a "
                "gap rule: if the winner beats the runner-up by more than some margin, answer directly, otherwise "
                "ask. Like the confidence threshold, that margin should be a named, tunable value rather than a "
                "stray number. A good disambiguation question offers the actual alternatives, phrased the way a "
                "person would, and never more than two or three options, because a long menu is worse than a "
                "fallback. It also records which intents were in contention, so you can later see which pairs of "
                "intents your table confuses most and fix the examples. Today you implement the margin rule over "
                "score dicts, print a question when the top two are close, and a direct choice otherwise. This is "
                "the first place the bot admits uncertainty out loud, and it usually reads as competence rather "
                "than weakness."
            ),
            code=(
                'MARGIN = 1\n'
                '\n'
                'def clarify(scores):\n'
                '    ranked = sorted(scores.items(), key=lambda pair: (-pair[1], pair[0]))\n'
                '    best, runner_up = ranked[0], ranked[1]\n'
                '    if best[1] - runner_up[1] <= MARGIN:\n'
                '        return f"Did you mean {best[0]} or {runner_up[0]}?"\n'
                '    return f"Using {best[0]}."\n'
                '\n'
                'CASES = [\n'
                '    {"reset_password": 3, "track_order": 3},\n'
                '    {"reset_password": 5, "track_order": 1},\n'
                ']\n'
                'for scores in CASES:\n'
                '    print(clarify(scores))\n'
                '\n'
                'assert clarify({"a": 4, "b": 4}).startswith("Did you mean")\n'
                'print("close scores become a question instead of a guess")'
            ),
            variant_b='raise the margin to 2 and rerun, then discuss which case now asks a question',
            variant_c='offer three alternatives when the top three scores are all within the margin',
            mistakes=[
                "Guessing between two near-equal intents instead of asking a short question.",
                "Listing every intent as an option, turning a question into an unusable menu.",
                "Hard-coding the margin as a magic number that no one can tune.",
            ],
            q1=(
                "When should a bot ask a disambiguation question instead of answering?",
                "When the top two intents score within a small margin, because a guess at that point is effectively a coin flip.",
            ),
            homework=(
                "Write `clarify(scores)` that returns a disambiguation question when the top two scores are within "
                "one point, otherwise a single chosen intent. Feed two score dicts, print both replies, and comment "
                "which line turns a near tie into a question."
            ),
            patterns=["def clarify", "sorted", "return"],
            mapping=(
                "Dialogflow's disambiguation and Rasa's two-stage fallback both ask the user to choose when "
                "candidate intents are too close to call."
            ),
        ),
        102: dict(
            topic="Small talk versus tasks",
            idea=(
                "Not every message is a request to do something. Users greet, thank, apologise and chat, and a bot "
                "that treats \"how are you?\" as a task it cannot perform feels cold, distant and broken. Separating small "
                "talk from tasks is a classification problem in miniature: a short list of social phrases handled "
                "with a fixed friendly reply, and everything else routed to the task intents. Keeping the two "
                "layers apart has real benefits. Small talk needs no entities, no tools and no state, so handling "
                "it early keeps the task pipeline clean and fast. It also lets you write better replies for the "
                "social cases without inventing intents for them, because their whole job is to acknowledge the "
                "user. The tricky part is the boundary. \"Hi, cancel my order\" is small talk plus a task, and a "
                "naive check for a greeting word would swallow the task. The fix is to treat an exact social phrase "
                "differently from a keyword buried inside a longer request, and to let task keywords win when both "
                "appear. Today you classify messages into small talk, task and unclear, and print the label for "
                "each. Getting the ambiguous middle case right is the whole exercise."
            ),
            code=(
                'SMALL_TALK = {"hi", "hello", "how are you", "thanks", "bye"}\n'
                'TASK_WORDS = {"order", "refund", "cancel", "balance"}\n'
                '\n'
                'def classify(text):\n'
                '    lowered = text.lower().strip()\n'
                '    if any(word in lowered for word in sorted(TASK_WORDS)):\n'
                '        return "task"\n'
                '    if lowered in SMALL_TALK:\n'
                '        return "small_talk"\n'
                '    return "unclear"\n'
                '\n'
                'for text in ["hello", "cancel my order", "hi, cancel my order", "tell me a story"]:\n'
                '    print(f"{text!r:24} -> {classify(text)}")\n'
                '\n'
                'assert classify("hi, cancel my order") == "task"\n'
                'print("task keywords win when small talk and a request mix")'
            ),
            variant_b='add "good morning" and "thanks a lot" to the small-talk set and rerun the messages',
            variant_c='return both labels when a message is small talk followed by a task, and print the pair',
            mistakes=[
                "Treating social phrases as tasks the bot cannot perform, so it refuses to say hello.",
                "Letting a greeting keyword swallow a task in a mixed message.",
                "Matching small talk with substring search so it fires inside unrelated words.",
            ],
            q1=(
                "Why route small talk before the task layer?",
                "Small talk needs no entities, tools or state, so handling it early keeps the task pipeline clean and gives social messages better replies.",
            ),
            homework=(
                "Write `classify(text)` returning \"small_talk\", \"task\" or \"unclear\" using a small-talk set "
                "and a task-keyword set. Test five messages covering all three labels, print each label, and "
                "comment which line keeps small talk from being mistaken for a task."
            ),
            patterns=["def classify", "return", "print("],
            mapping=(
                "Assistant platforms route chit-chat to a separate small-talk agent so greetings and thanks never "
                "pollute the task intents or consume a tool call."
            ),
        ),
        103: dict(
            topic="Evaluating intent accuracy",
            idea=(
                "A routing table is only as good as the evidence that it works, and the only honest evidence is a "
                "set of labelled messages with the intent each should produce. Evaluation is nothing more than "
                "running the matcher over that set and counting how often the prediction matches the label. The "
                "value is that it turns opinion into a number you can watch as you edit rules; adding a synonym "
                "that raises accuracy on your examples is progress, while adding one that lowers it is a warning. "
                "A single accuracy figure hides a lot, so keep the list of misclassified examples too, because "
                "those specific failures tell you which rule to fix next. Build the labelled set carefully: a "
                "handful of cases per intent, including phrasing you did not write the rules for, and a few "
                "genuine fallback cases. Keep it fixed while you tune, or you will be moving the target. Never "
                "tune against the exact examples you will report on without saying so, because that inflates the "
                "number. Today you run a tiny labelled set through a predictor, print the accuracy and the missed "
                "cases, and assert the count. This is the loop that every later model will also be judged by."
            ),
            code=(
                'LABELLED = [\n'
                '    ("hi there", "greet"),\n'
                '    ("hello", "greet"),\n'
                '    ("cancel order", "cancel"),\n'
                '    ("track my parcel", "track"),\n'
                ']\n'
                '\n'
                'def predict(text):\n'
                '    lowered = text.lower()\n'
                '    if lowered.startswith(("hi", "hello")):\n'
                '        return "greet"\n'
                '    if "cancel" in lowered:\n'
                '        return "cancel"\n'
                '    return "fallback"\n'
                '\n'
                'correct = sum(1 for text, gold in LABELLED if predict(text) == gold)\n'
                'print(f"accuracy: {correct}/{len(LABELLED)}")\n'
                'for text, gold in LABELLED:\n'
                '    if predict(text) != gold:\n'
                '        print(f"missed {text!r}: wanted {gold}, got {predict(text)}")\n'
                '\n'
                'assert correct == 3\n'
                'print("accuracy plus the misses is the feedback loop")'
            ),
            variant_b='add a labelled "refund" example and show how accuracy changes when the rule is missing',
            variant_c='split the set into two halves and report accuracy on each to expose unstable rules',
            mistakes=[
                "Reporting accuracy without keeping the misclassified examples to learn from.",
                "Changing the labelled set while tuning, so numbers from two runs are not comparable.",
                "Tuning on the same examples you report, which inflates the measured accuracy.",
            ],
            q1=(
                "Why keep the list of misclassified examples as well as the accuracy number?",
                "The specific failures name the rule that needs fixing, while the single accuracy figure only says something is wrong.",
            ),
            homework=(
                "Write `evaluate(labelled, predict)` returning accuracy as a fraction and the list of mislabelled "
                "examples. Run it on four labelled utterances, print the accuracy and the mistakes, and comment "
                "which line makes the score reproducible."
            ),
            patterns=["def evaluate", "return", "print("],
            mapping=(
                "Rasa's NLU test runner and Dialogflow's evaluation both report intent accuracy over a held-out "
                "labelled set, exactly this loop with more data."
            ),
        ),
        104: dict(
            topic="Review: intents and responses checklist",
            idea=(
                "The intent pipeline you built over these days has a small number of moving parts, and a checklist "
                "makes them visible before the bot ships. Does the intent table exist as data, with stable names "
                "and canonical utterances? Is there a matcher that normalises case and punctuation once, compiles "
                "its patterns up front, and does not fire inside unrelated words? Is there a scoring or priority "
                "rule that ranks competing intents deterministically? Is there a named confidence threshold, and "
                "a fallback that names what the bot can do rather than going silent? Are entities extracted into "
                "named fields, with missing ones left absent? And is there a labelled evaluation set that produces "
                "an accuracy figure plus the specific misses? A checklist is not bureaucracy; each item maps to a "
                "failure mode you have already seen. Reviewing against it is how a demo becomes something you are "
                "willing to put in front of users, and it is how you decide what to improve next. Today you write "
                "an audit function that checks whether each piece is present and prints every missing box. The "
                "output should point straight at the weakest part of a bot rather than reassuring you that it runs."
            ),
            code=(
                'CHECKS = ["table", "matcher", "score", "fallback", "threshold"]\n'
                '\n'
                'def audit(bot):\n'
                '    return {name: bool(bot.get(name)) for name in CHECKS}\n'
                '\n'
                'bot = {"table": True, "matcher": True, "score": True, "fallback": True, "threshold": False}\n'
                'report = audit(bot)\n'
                'for name, present in report.items():\n'
                '    print(f"{name:10} {\'ok\' if present else \'missing\'}")\n'
                '\n'
                'missing = [name for name, present in report.items() if not present]\n'
                'assert missing == ["threshold"]\n'
                'print("review:", missing, "still to do")'
            ),
            variant_b='add "entities" and "evaluation" to the checklist and rerun the audit on the same bot',
            variant_c='make audit return a readiness score as a fraction of present items and print it',
            mistakes=[
                "Shipping once the bot merely runs, without checking the pieces it is missing.",
                "Treating the checklist as a formality rather than a map of real failure modes.",
                "Adding features before the fallback and threshold are in place.",
            ],
            q1=(
                "What is the point of auditing a bot against a fixed checklist?",
                "Each box maps to a known failure mode, so the audit points at the weakest part instead of merely confirming the bot runs.",
            ),
            homework=(
                "Write `audit(bot)` that returns a dict from each checklist item to a boolean, and `main()` that "
                "prints every unchecked item. Build a bot missing two items, print the audit, and comment which "
                "line makes the missing pieces visible before launch."
            ),
            patterns=["def audit", "def main", "return"],
            mapping=(
                "Production bot reviews ask the same questions — intents, thresholds, fallbacks, entities and "
                "evaluation — before any platform, Dialogflow, Rasa or Lex, is allowed near real users."
            ),
        ),
    },
)
