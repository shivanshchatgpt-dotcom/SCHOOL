"""Phase 1, days 75-89: messages and conversations as data you can test.

Every example is stdlib-only, offline and deterministic (no network, no model
call, no clock), so the applier can execute it and produce the same output every
run. A conversation is a list of role/content dicts; windows, budgets, state
machines, reference resolution, logging and replay are all plain functions over
that list, which is what makes a whole session reproducible and assertable
without an API key.
"""

PHASE = (
    "Messages and Conversations",
    "Model a chatbot conversation as an ordered list of typed messages, then read, bound, replay and test it with plain Python.",
    {
        75: dict(
            topic="Orientation: what a chatbot is",
            idea=(
                "A chatbot is a loop. It takes text from a person, decides what to do with it, produces text back, "
                "and remembers enough to do it again on the next turn. Everything else — models, tools, memory, "
                "personality — hangs off that loop. Before reaching for any framework, it helps to build the "
                "smallest honest version: a function from user text to a reply, called once per turn, with the "
                "turns collected in a list. That version is not impressive, but it is complete, and it makes the "
                "real questions visible. Where does the reply come from? What does the bot remember? What happens "
                "when it does not understand? You can answer those questions in twenty lines of standard library "
                "Python, and the answers stay true when a language model replaces the keyword rules later. Today "
                "the bot is a support desk that matches a few keywords to canned answers. The point is not the "
                "answers but the shape: input in, decision, output out, history kept. Keep that shape in mind for "
                "the rest of the phase, because every later topic — schemas, roles, windows, budgets, state "
                "machines — is a refinement of this one small loop. Keep the loop small, because the shape is "
                "what transfers to every bot you build after this one."
            ),
            code="""\
def reply(text):
    lowered = text.lower()
    if "refund" in lowered:
        return "I can help with a refund."
    if "hours" in lowered:
        return "We are open 9 to 5."
    return "Let me connect you to support."

for user in ["Hi", "What are your hours?", "I want a refund", "Weather?"]:
    print(f"user: {user}")
    print(f"bot : {reply(user)}")

assert reply("refund please").startswith("I can help")
assert reply("hmm") == "Let me connect you to support."
print("a chatbot is a loop mapping user text to a reply")
""",
            variant_b="add an 'order status' branch that echoes the order number found in the text",
            variant_c="return a tuple of (reply, intent) and print the intent alongside every reply",
            mistakes=[
                "Treating the bot as one big function instead of a loop over turns with history.",
                "Making the reply depend on global state, so two conversations interfere.",
                "Leaving some inputs to fall through and produce no reply at all.",
            ],
            q1=(
                "What is the smallest complete model of a chatbot?",
                "A function from user text to a reply, called once per turn, with the turns kept in an ordered history.",
            ),
            homework=(
                "Write `reply(text)` for a support bot that recognises three topics and always falls back to a "
                "handoff message. Drive five user strings through it in a loop, print each user line and each "
                "reply, and comment which line guarantees the bot never stays silent."
            ),
            patterns=["def ", "for ", "print("],
            mapping=(
                "Framework chatbots such as Rasa and Dialogflow all run this same turn loop; the difference is "
                "that a model or a policy chooses the reply instead of hand-written keyword rules."
            ),
        ),
        76: dict(
            topic="The message schema",
            idea=(
                "A message is the atom of every conversation, so it deserves a fixed shape. The widely used shape "
                "has exactly two required fields: a role that says who is speaking and content that holds the "
                "text. The four roles that matter are system, user, assistant and tool. Keeping the schema this "
                "small is a deliberate choice: every extra field is something each layer must understand, "
                "serialise and preserve. Write a constructor that rejects unknown roles early, because a typo "
                "like 'assistent' that travels silently into storage is far more expensive to find later than an "
                "exception thrown at the source. Write a validator that checks the keys and the type of the "
                "content, so malformed messages fail fast rather than surfacing as strange behaviour three turns "
                "later. Today you build both and feed them a good message and a bad one. The bad one should "
                "raise, because a schema is only useful if it actually rejects things. Notice that this schema is "
                "not tied to any vendor; provider formats are translations of this idea into JSON with their own "
                "field names. Get the atom right and every conversation built from it stays inspectable. A "
                "validator is only worth having if it rejects something, so always test it with a bad input as "
                "well as a good one."
            ),
            code="""\
def make_message(role, content):
    if role not in {"system", "user", "assistant", "tool"}:
        raise ValueError(f"unknown role: {role}")
    return {"role": role, "content": content}

def is_valid(message):
    return set(message) == {"role", "content"} and isinstance(message["content"], str)

good = make_message("user", "Where is my order?")
print("message:", good)
print("valid:", is_valid(good))

try:
    make_message("robot", "beep")
except ValueError as error:
    print("rejected:", error)

assert is_valid(good)
assert not is_valid({"role": "user"})
print("the schema is a role plus text content")
""",
            variant_b="allow an optional 'name' field but keep role and content required",
            variant_c="write `validate_all(messages)` that raises on the first malformed message in a list",
            mistakes=[
                "Letting unknown roles through, so a typo survives until it breaks a later layer.",
                "Using different key names for the speaker in different parts of the code.",
                "Skipping the schema check on messages read back from storage.",
            ],
            q1=(
                "Why validate a message at construction instead of when it is used?",
                "Failing at the source points at the bad input immediately, while deferred failures surface as confusing behaviour far from the cause.",
            ),
            homework=(
                "Write `make_message(role, content)` and `is_valid(message)` against a fixed set of roles. Build "
                "one valid message and one invalid one, print both validation results, raise on the invalid role, "
                "and comment which line enforces the allowed roles."
            ),
            patterns=["def ", "raise", "print("],
            mapping=(
                "OpenAI, Anthropic and Gemini all accept role/content message lists; each just renames the fields "
                "and adds provider-specific ones for tools and images."
            ),
        ),
        77: dict(
            topic="Roles and system prompts",
            idea=(
                "Each role does a different job in the transcript. The system message sets the rules for the "
                "whole conversation: tone, length, what the bot may and may not do. The user message carries the "
                "request. The assistant message carries the reply. The tool message carries a result. The system "
                "prompt is special because it comes first and applies to everything after it, which is why it is "
                "written once, kept at the front of the history, and never mistaken for something the user said. A "
                "good system prompt is short and testable: 'answer in at most three words' is a rule you can "
                "check, while 'be helpful' is not. Today you keep a system message at the head of a history and "
                "append turns behind it, then assert that every assistant reply obeys the stated limit. The "
                "exercise shows the practical difference between the roles: the same words would change meaning "
                "if spoken by the user instead of the system. Treat the system prompt as configuration you can "
                "inspect and diff, not as hidden magic, and it becomes something you can review, version and test "
                "like any other part of the program. Test the prompt by asserting on the replies it produces, "
                "not by reading it and hoping it has the intended effect."
            ),
            code="""\
SYSTEM = {"role": "system", "content": "Answer in at most three words."}

def add_turn(history, text):
    history.append({"role": "user", "content": text})
    short = " ".join(text.replace("?", "").split()[:3])
    history.append({"role": "assistant", "content": short})

history = [dict(SYSTEM)]
add_turn(history, "What is your return policy?")
add_turn(history, "Do you ship abroad?")

for m in history:
    print(f"{m['role']:9}: {m['content']}")

assert history[0]["content"] == SYSTEM["content"]
assert all(len(m["content"].split()) <= 3 for m in history if m["role"] == "assistant")
print("the system prompt steers every later reply")
""",
            variant_b="give the system prompt a persona word and prepend it to each assistant reply",
            variant_c="compare a history with and without the system message and print both first replies",
            mistakes=[
                "Appending new system messages in the middle of a conversation instead of setting one at the start.",
                "Writing vague system prompts that no test can check.",
                "Letting user text overwrite or impersonate the system rules.",
            ],
            q1=(
                "Why does the system prompt live at the front of the history?",
                "It applies to every following turn and is written once, so keeping it pinned at the start makes it clear it is configuration rather than conversation.",
            ),
            homework=(
                "Write `start_conversation(system_text)` that returns a history with one system message, plus "
                "`add_turn(history, text)` that appends a user and an assistant message. Drive two turns, print "
                "the transcript, and comment which line keeps the system prompt at the head."
            ),
            patterns=["def ", "system", "print("],
            mapping=(
                "Every major provider exposes a system or developer role that behaves this way, and prompt "
                "management tools output exactly this leading message."
            ),
        ),
        78: dict(
            topic="Turns and the transcript",
            idea=(
                "A turn is one exchange: something the user says and something the bot says back. The transcript "
                "is the ordered list of every message, and its order is meaning, not decoration. If you sort the "
                "transcript, deduplicate it, or store it in a dictionary keyed by text, you destroy the one "
                "property that makes it a conversation. The transcript is also your primary debugging tool: when "
                "a bot behaves strangely, the first question is always what the history actually contained at the "
                "moment it answered. Today you append turns to a history list and render the whole thing as a "
                "readable transcript with one line per message. Rendering matters more than it looks: a stable "
                "plain-text view is what you paste into a bug report or compare between two runs. Keep the "
                "representation simple — a list of role and content — and write one function that turns it into "
                "text. Because the transcript is a value, you can print it, store it, diff it and replay it. Those "
                "four abilities, all consequences of treating the conversation as data, are what this phase is "
                "really about. Render it the same way every time, so two runs can be compared with a plain diff."
            ),
            code="""\
def turn(role, content):
    return {"role": role, "content": content}

def transcript(history):
    return "\\n".join(f"{m['role']}: {m['content']}" for m in history)

history = []
history.append(turn("user", "Book a table"))
history.append(turn("assistant", "For how many?"))
history.append(turn("user", "Four"))

print(transcript(history))
print("turns:", len(history))

assert history[-1] == turn("user", "Four")
assert transcript(history).startswith("user: Book a table")
print("the transcript is the ordered record of turns")
""",
            variant_b="add a timestamp string field to each turn and print it in the rendered transcript",
            variant_c="write `turn_count(history, role)` and print how many user and assistant turns there are",
            mistakes=[
                "Storing the transcript in a set or dict and losing the order of turns.",
                "Rendering the transcript inconsistently in different places, so diffs are noisy.",
                "Mixing metadata into the content string instead of adding a field.",
            ],
            q1=(
                "Why is a dictionary keyed by message text the wrong store for a transcript?",
                "It loses order and collapses repeated identical turns, and order is the meaning of a conversation.",
            ),
            homework=(
                "Write `turn(role, content)` and `transcript(history)` that renders one line per message. Build a "
                "four-turn conversation, print the transcript and the turn count, and comment which line preserves "
                "the order of the messages."
            ),
            patterns=["def ", "return", "print("],
            mapping=(
                "Conversation stores in frameworks like LangChain persist turns in order, and every provider's "
                "message list is exactly this ordered transcript."
            ),
        ),
        79: dict(
            topic="Reading a conversation in order",
            idea=(
                "Reading a conversation means walking the transcript from start to finish and answering questions "
                "about what you find. How many turns did the user take? What was the most recent request? Did the "
                "bot ever ask a question it never got an answer to? These are simple folds over a list, and "
                "writing them by hand first is the fastest way to understand what a memory or summarisation layer "
                "will later need to provide. The most important skill is finding the last user message, because in "
                "most bots that is the request currently being answered; everything before it is context. A "
                "common mistake is to scan from the front and return the first match, which answers an old request "
                "and creates confusing replies in long conversations. Today you count messages per role and "
                "extract the last user turn, then assert both. Notice that order carries the answer: the same "
                "three messages reordered would tell a different story. Once you can answer questions about a "
                "transcript with a loop, you can answer them about any conversation you can capture, and those "
                "answers become the tests for everything downstream. Write these readers before you write memory, "
                "so you know exactly what memory must remember."
            ),
            code="""\
conversation = [
    {"role": "user", "content": "Hi"},
    {"role": "assistant", "content": "Hello"},
    {"role": "user", "content": "I need a tutor"},
    {"role": "assistant", "content": "Which subject?"},
    {"role": "user", "content": "Math"},
]

counts = {}
for m in conversation:
    counts[m["role"]] = counts.get(m["role"], 0) + 1
print("counts:", counts)

last_user = [m["content"] for m in conversation if m["role"] == "user"][-1]
print("last user said:", last_user)

assert counts == {"user": 3, "assistant": 2}
assert last_user == "Math"
print("order matters: the last user turn defines the request")
""",
            variant_b="also report the first user message and print whether it differs from the last",
            variant_c="write `last_by_role(history, role)` and use it to print the last assistant reply",
            mistakes=[
                "Returning the first matching message instead of the most recent one.",
                "Assuming roles strictly alternate, which breaks after tool calls or corrections.",
                "Counting turns by length without excluding the system message.",
            ],
            q1=(
                "Why is the last user message usually the request being answered?",
                "Each new user turn drives the next reply, so the newest one is the live request and the earlier turns are context.",
            ),
            homework=(
                "Write `scan(history)` that returns a dict of message counts per role plus the last user message. "
                "Run it on a five-message conversation, print both results, and comment which line selects the "
                "most recent user turn rather than the first."
            ),
            patterns=["def ", "for ", "return"],
            mapping=(
                "Memory and summarisation layers in production assistants are built by folding over the "
                "transcript this way; retrieval decides what to keep and what to compress."
            ),
        ),
        80: dict(
            topic="The context window",
            idea=(
                "A language model cannot read an unbounded conversation. It sees a fixed number of tokens at a "
                "time, called the context window, and anything older than that is simply invisible. This has a "
                "direct consequence for your code: the history you keep is usually longer than the history you "
                "send, so you need a function that selects the part to include. The simplest policy keeps the most "
                "recent messages and drops the oldest, on the reasoning that the newest turns are most relevant to "
                "what the user just asked. That reasoning is often right and sometimes wrong, which is exactly the "
                "kind of trade-off worth making explicit in a named function rather than burying in a loop. Today "
                "you write a window function that returns the last few messages and print what it keeps and what "
                "it drops. Two details matter later: the system prompt should usually survive trimming, and the "
                "newest message must always be included, because answering without the current question is worse "
                "than answering with stale context. A window is a policy, so name it, test it and change it "
                "deliberately. Because it is a policy, a larger context size should change one constant rather "
                "than the whole design."
            ),
            code="""\
WINDOW = 4

def window(history, size=WINDOW):
    return history[-size:]

history = [{"role": "user", "content": f"turn {i}"} for i in range(1, 8)]
print("full history:", len(history))

kept = window(history)
print("window size:", len(kept))
for m in kept:
    print("kept:", m["content"])

assert len(kept) == WINDOW
assert kept[0]["content"] == "turn 4"
assert kept[-1]["content"] == "turn 7"
print("a context window keeps only the most recent messages")
""",
            variant_b="take an explicit size argument and print the window for sizes 2 and 5",
            variant_c="write `dropped(history, size)` that returns the messages left out of the window",
            mistakes=[
                "Sending the entire history and hoping the provider silently trims it.",
                "Dropping the newest message, so the bot answers the wrong question.",
                "Hard-coding the window size in several places instead of one constant.",
            ],
            q1=(
                "Why must the newest message always survive the window?",
                "It is the current request; answering without it means the bot replies to stale context rather than the user's live question.",
            ),
            homework=(
                "Write `window(history, size)` that returns the last `size` messages, plus `dropped(history, size)` "
                "for the rest. Build a seven-message history, print what each function returns, and comment which "
                "line guarantees the newest message is included."
            ),
            patterns=["def ", "return", "print("],
            mapping=(
                "Providers cap context windows by model, and frameworks expose a sliding-window memory that is "
                "exactly this function with persistence attached."
            ),
        ),
        81: dict(
            topic="Truncating history safely",
            idea=(
                "Truncation is what you do when the history is too long and something must go. The naive version "
                "keeps the last few messages, which is fine until it silently throws away the system prompt, and "
                "then the bot forgets its rules mid-conversation. Safe truncation treats the system message as "
                "pinned: it is never dropped, because it is configuration rather than conversation. Everything "
                "else is fair game, and the usual rule is to remove the oldest turns first, since they are least "
                "likely to matter to the current request. A second subtlety is that removing a turn can orphan its "
                "pair: dropping a user message while keeping the assistant reply to it leaves a transcript that "
                "starts with an answer to nothing. Today you write a truncation function that pins the system "
                "prompt, keeps the newest messages up to a limit, and prints the result. Assert that the system "
                "message survives and that the newest message is still present. Truncation is where correctness is "
                "easiest to lose quietly, so it is exactly the function to cover with a couple of assertions "
                "before you trust it. Assert both that the system prompt survived and that the newest message is "
                "still there, every time you trim."
            ),
            code="""\
def truncate(history, limit):
    if len(history) <= limit:
        return list(history)
    system = [m for m in history if m["role"] == "system"]
    rest = [m for m in history if m["role"] != "system"]
    keep = rest[-(limit - len(system)):]
    return system + keep

history = [{"role": "system", "content": "Be brief."}]
for i in range(1, 6):
    history.append({"role": "user", "content": f"msg {i}"})

trimmed = truncate(history, 3)
for m in trimmed:
    print(f"{m['role']:9}: {m['content']}")

assert trimmed[0]["role"] == "system"
assert len(trimmed) == 3 and trimmed[-1]["content"] == "msg 5"
print("truncation keeps the system prompt and the newest turn")
""",
            variant_b="also pin the first user message, treating it as the original request",
            variant_c="raise a clear error when the limit is smaller than the pinned messages",
            mistakes=[
                "Dropping the system prompt along with the oldest messages.",
                "Leaving an assistant reply without the user message it answered.",
                "Truncating by message count when the real limit is tokens.",
            ],
            q1=(
                "Why is the system prompt pinned rather than treated as the oldest message?",
                "It is configuration that governs every turn, so dropping it silently changes the bot's behaviour even though the conversation looks fine.",
            ),
            homework=(
                "Write `truncate(history, limit)` that keeps the system prompt and the newest messages up to the "
                "limit. Build a long history, print the trimmed transcript, and comment which line pins the system "
                "message so it can never be dropped."
            ),
            patterns=["def ", "system", "print("],
            mapping=(
                "Frameworks call this trimming or pruning; the same trick of pinning the system prompt appears in "
                "memory modules and provider-side conversation summaries."
            ),
        ),
        82: dict(
            topic="A token budget model",
            idea=(
                "Truncation is easier to reason about if you give it a budget measured in the same unit the model "
                "uses: tokens. You do not need a real tokeniser to practise the idea; approximating one token per "
                "word is close enough to build the logic and to see where it breaks. The function walks the "
                "history from newest to oldest, adds the cost of each message, and stops before the budget is "
                "exceeded, so the result is the largest suffix that fits. This is a knapsack-flavoured decision "
                "with a simple greedy answer, and the greedy answer is usually what you want, because recent "
                "turns matter most. Two details to keep in mind. First, the system prompt needs its own reserved "
                "share, or a long conversation will crowd it out. Second, the approximation is deliberately crude, "
                "and that is fine: the goal is a budget you can test offline, not a byte-accurate count. Today you "
                "approximate tokens with words, cap the total, and print what fit and how much was used. When you "
                "later swap in a real tokeniser, only the cost function changes; the budget logic stays the same. "
                "Keep the budget a parameter, so a bigger model is a bigger number and not a rewrite."
            ),
            code="""\
def tokens(text):
    return len(text.split())

def fit(history, budget):
    kept = []
    used = 0
    for m in reversed(history):
        cost = tokens(m["content"])
        if used + cost > budget:
            break
        kept.append(m)
        used += cost
    return list(reversed(kept)), used

history = [
    {"role": "user", "content": "one two three"},
    {"role": "assistant", "content": "four five"},
    {"role": "user", "content": "six seven eight nine"},
]

kept, used = fit(history, 6)
print("used:", used, "of 6")
for m in kept:
    print("kept:", m["content"])

assert used <= 6 and kept[-1]["content"] == "six seven eight nine"
print("a budget caps how much history you send")
""",
            variant_b="reserve two tokens for the system prompt and show it fits only when the budget allows",
            variant_c="count characters instead of words and print how the chosen window changes",
            mistakes=[
                "Never bounding the prompt, so a long conversation eventually overflows the window.",
                "Letting one huge message blow the budget instead of stopping before it.",
                "Treating the word count as a real token count and trusting it exactly.",
            ],
            q1=(
                "Why keep a token budget in the conversation layer rather than at the API call?",
                "The layer that builds the message list knows what can be dropped, so it can spend the budget deliberately instead of failing at send time.",
            ),
            homework=(
                "Write `fit(history, budget)` that keeps the newest messages whose total cost stays within the "
                "budget and returns them with the amount used. Estimate cost with `len(text.split())`, print the "
                "result for a small history, and comment which line stops before the budget is exceeded."
            ),
            patterns=["def ", "return", "print("],
            mapping=(
                "Real systems use a tokeniser such as tiktoken to price messages, then apply exactly this greedy "
                "trim; the budget is the model's context size minus the room reserved for the reply."
            ),
        ),
        83: dict(
            topic="Conversation state machines",
            idea=(
                "A scripted bot can get away with a pile of if-statements, but the moment a bot must collect "
                "several pieces of information in order — a booking date, then a time, then a confirmation — those "
                "conditionals become a knot. A state machine untangles it. You name a small set of states, "
                "describe which input moves you from one state to another, and keep the current state in the "
                "session. The whole behaviour fits in a table: a dictionary from a state and an intent to the next "
                "state. When input does not match a transition, the machine stays put and the bot asks again, "
                "which is usually the right recovery. This model makes conversations reviewable, because you can "
                "read the table instead of tracing control flow, and testable, because each edge is one "
                "assertion. Today you build a three-state machine for a booking bot and step it through several "
                "intents, including one that does not apply. Notice the difference between no transition and a "
                "transition to an error state: staying put is often friendlier. Keep the state in the session, "
                "never in a global, so two conversations cannot interfere with each other. Print the state after "
                "each step, because a state machine is easiest to debug when its path is visible."
            ),
            code="""\
TRANSITIONS = {
    ("start", "hi"): "greeting",
    ("greeting", "book"): "collecting",
    ("collecting", "done"): "confirmed",
}

def step(state, intent):
    return TRANSITIONS.get((state, intent), state)

state = "start"
for intent in ["hi", "book", "done", "cancel"]:
    previous = state
    state = step(state, intent)
    print(f"{previous:11} --{intent:6}--> {state}")

assert state == "confirmed"
assert step("start", "book") == "start"
print("the state machine only moves on valid transitions")
""",
            variant_b="add a 'cancel' transition from collecting back to start and step through it",
            variant_c="record the visited states in a list and print the full path taken",
            mistakes=[
                "Storing the current state in a global that every conversation shares.",
                "Scattering transitions across if-statements instead of one readable table.",
                "Crashing on an unexpected intent instead of staying in the current state.",
            ],
            q1=(
                "Why is a table better than if-statements for collecting several slots in order?",
                "The table states every allowed transition in one place, so the conversation is reviewable and each edge is a single assertion.",
            ),
            homework=(
                "Write `step(state, intent)` driven by a transition table for a booking bot with three states. "
                "Step through four intents including one that has no transition, print the state after each, and "
                "comment which line makes an unknown intent leave the state unchanged."
            ),
            patterns=["def ", "get(", "print("],
            mapping=(
                "Design tools such as Rasa forms and Amazon Lex follow explicit state transitions; even "
                "model-driven agents usually keep a small state machine around the conversation."
            ),
        ),
        84: dict(
            topic="Multi-turn references",
            idea=(
                "People do not repeat themselves. After asking for the science plan, they say 'show me that again' "
                "or 'make it longer', and a bot that treats every message in isolation will fail on both. "
                "Resolving a reference means looking back through the transcript for the thing being referred to — "
                "usually the most recent matching entity — and substituting it before deciding what to do. This is "
                "a small piece of anaphora resolution, and a crude last-mention rule covers a surprising amount of "
                "real conversation. The important design point is that resolution is a separate step from acting: "
                "first turn 'it' into a concrete noun phrase using the history, then route the resolved text in the "
                "normal way. Keeping them separate means your intent rules never need to know about pronouns, and "
                "you can test resolution on its own. Today you write a resolver that replaces a pronoun with the "
                "last user-mentioned subject and print the result. Watch for the failure cases: two candidate "
                "entities, or a pronoun with nothing to refer to. In those situations the honest answer is to ask, "
                "not to guess. When there is no candidate to attach to, returning the text unchanged is safer "
                "than inventing a referent."
            ),
            code="""\
def resolve(history, text):
    if text.strip().lower() in {"it", "that", "them"}:
        for m in reversed(history):
            if m["role"] == "user":
                return m["content"]
    return text

history = [
    {"role": "user", "content": "Show me the science plan"},
    {"role": "assistant", "content": "Here it is."},
]

print("resolved:", resolve(history, "it"))
print("resolved:", resolve(history, "the math plan"))

assert resolve(history, "that") == "Show me the science plan"
assert resolve(history, "something else") == "something else"
print("a pronoun points at the most recent user reference")
""",
            variant_b="return a flag when the pronoun has no earlier user turn to attach to",
            variant_c="resolve 'them' only when the last user message mentions a plural noun",
            mistakes=[
                "Routing pronouns before resolving them, so intent rules misfire on 'it'.",
                "Resolving against the assistant reply instead of the user's own words.",
                "Guessing when there is no candidate reference instead of asking for clarification.",
            ],
            q1=(
                "Why resolve references before routing the intent?",
                "Routing decides what to do from concrete text, so converting 'it' into the referenced phrase first keeps the intent rules simple and pronoun-free.",
            ),
            homework=(
                "Write `resolve(history, text)` that replaces a pronoun with the most recent user-mentioned "
                "subject. Test it with a history of two turns for a pronoun and a plain phrase, print both "
                "results, and comment which line scans the history backwards for the reference."
            ),
            patterns=["def ", "reversed", "return"],
            mapping=(
                "This is the anaphora step that real assistants perform before intent detection; frameworks "
                "sometimes expose it as coreference resolution."
            ),
        ),
        85: dict(
            topic="Ambiguity and clarification",
            idea=(
                "Ambiguity is the normal condition of conversation, not an edge case. A user says 'the plan' and "
                "there are three plans; a bot that picks one silently is wrong twice — it gives an unwanted answer "
                "and it hides the uncertainty that should have driven a question. Good chatbots detect ambiguity "
                "and ask. The detection is often simple: match the request against your known options and count "
                "how many fit. Zero matches means the bot needs more information or a different phrasing; one "
                "match means proceed; more than one means present the candidates and let the user choose. This "
                "small three-way decision is more valuable than a clever guess, because it keeps the user in "
                "control and makes the bot's confusion visible. Today you write an interpreter that classifies a "
                "request as resolved, ambiguous or unknown and prints the reply for each case. Notice that the "
                "clarification reply should name the options concretely; 'which one?' without listing them helps "
                "nobody. Listing the options also turns a vague failure into a useful next turn that the user can "
                "actually answer, which is why clarification is a feature and not a fallback. Asking a sharp "
                "question is one of the easiest ways to make a small bot feel competent."
            ),
            code="""\
PLANS = ["science plan", "math plan", "sports plan"]

def interpret(text):
    lowered = text.lower()
    matches = [p for p in PLANS if p.split()[0] in lowered]
    if len(matches) == 1:
        return f"Selected {matches[0]}."
    if len(matches) > 1:
        return "Which one: " + ", ".join(matches) + "?"
    return "Which plan do you mean?"

for text in ["I want the math plan", "science or sports?", "hello"]:
    print(f"{text!r} -> {interpret(text)}")

assert interpret("sports plan").startswith("Selected")
assert interpret("science or sports").endswith("?")
assert interpret("hello") == "Which plan do you mean?"
print("several matches should trigger a clarifying question")
""",
            variant_b="ask a numbered question and accept a follow-up number as the choice",
            variant_c="rank matches by how many words they share with the text before deciding",
            mistakes=[
                "Choosing arbitrarily when several options match instead of asking.",
                "Asking 'which one?' without naming the candidates.",
                "Treating zero matches as an error rather than a request for more detail.",
            ],
            q1=(
                "Why ask instead of picking the best-scoring match when two options fit?",
                "A silent guess gives an answer the user did not want and hides the uncertainty; naming the options keeps the user in control.",
            ),
            homework=(
                "Write `interpret(text)` that classifies a request against three named options as resolved, "
                "ambiguous or unknown and returns the reply. Print the reply for one of each case, and comment "
                "which line turns several matches into a clarifying question."
            ),
            patterns=["def ", "if ", "print("],
            mapping=(
                "Clarifying questions are standard in slot-filling assistants; frameworks expose disambiguation "
                "as a step after intent scoring when confidence is split."
            ),
        ),
        86: dict(
            topic="Logging conversations",
            idea=(
                "A bot you cannot observe is a bot you cannot improve. Logging is how you find out what users "
                "actually asked, where the bot got stuck and how long conversations ran, but logging a full "
                "transcript carelessly is its own hazard: conversations contain personal data, and dumping raw "
                "text everywhere is both a privacy problem and a noisy one. The useful middle ground is structured "
                "metadata. Log one record per turn with a turn index, the role, the length of the content, and any "
                "decision the bot made, such as the chosen intent. That is enough to measure behaviour without "
                "copying everything a user typed into long-lived storage. Structured records also mean the log is "
                "queryable: you can count how often the fallback fired without reading prose. Today you turn a "
                "history into a list of small JSON records and print them. Note that the same discipline applies "
                "to the transcript you keep in a session: store what the bot needs to continue, and redact or "
                "summarise anything it does not, so retention stays a deliberate choice rather than an accident. "
                "Choose the logged fields before you write the logger, so privacy and retention are deliberate "
                "design decisions rather than conveniences."
            ),
            code="""\
import json

def log_lines(history):
    lines = []
    for index, m in enumerate(history):
        entry = {"i": index, "role": m["role"], "chars": len(m["content"])}
        lines.append(json.dumps(entry, sort_keys=True))
    return lines

history = [
    {"role": "user", "content": "Hi"},
    {"role": "assistant", "content": "Hello there"},
]

for line in log_lines(history):
    print(line)

assert json.loads(log_lines(history)[1])["chars"] == 11
print("logging turns records metadata, not the raw text")
""",
            variant_b="add a 'fallback' boolean to each record and print the log for a missed intent",
            variant_c="write `summary(log)` that totals characters per role from the records",
            mistakes=[
                "Dumping full transcripts into logs that outlive the session.",
                "Logging free text with no index or role, so the records cannot be queried.",
                "Keeping user data longer than the bot needs it to continue a conversation.",
            ],
            q1=(
                "Why log metadata instead of the full message text?",
                "Index, role and length answer behavioural questions while exposing far less user data, and the records stay queryable.",
            ),
            homework=(
                "Write `log_lines(history)` that returns one JSON record per turn with an index, role and content "
                "length. Build a two-message history, print each record, and comment which line keeps the logged "
                "text to a length rather than the message itself."
            ),
            patterns=["def ", "len(", "print("],
            mapping=(
                "Observability tools such as LangSmith and provider dashboards store structured per-turn traces; "
                "the same design keeps user data minimised."
            ),
        ),
        87: dict(
            topic="Replaying a session",
            idea=(
                "Replay is the ability to take a saved conversation and run it again. It is the foundation of "
                "debugging, evaluation and regression testing, and it only works if the bot is a pure function of "
                "the turns it is given. If a response depends on the clock, a random choice or a global counter, "
                "the same conversation produces a different result on the second run and you cannot compare "
                "anything. Making the bot replayable is largely a matter of discipline: pass the turns and any "
                "state in, return the new state and messages out, and keep everything else out of reach. Once that "
                "holds, you can store a session, reload it, run it through the current code, and diff the new "
                "transcript against the old one to see exactly what changed. That diff is your regression test. "
                "Today you run one fixed list of user turns through a responder twice and assert the two sessions "
                "are identical. The determinism you build here is the same property the worked examples in this "
                "course rely on to run offline and produce the same output every time, and it is what lets you "
                "trust a test failure as a real change. A session that replays identically is a session you can "
                "safely change, test and ship."
            ),
            code="""\
def respond(text):
    if "refund" in text:
        return "Refunds take 3 days."
    return "Sorry, I did not get that."

def session(turns):
    history = []
    for t in turns:
        history.append({"role": "user", "content": t})
        history.append({"role": "assistant", "content": respond(t)})
    return history

saved = ["I want a refund", "ok"]
first = session(saved)
second = session(saved)
print("first :", first[1]["content"])
print("second:", second[1]["content"])

assert first == second
print("replaying the same turns rebuilds the same session")
""",
            variant_b="store a session as a list of user turns and rebuild the transcript from it",
            variant_c="introduce a counter in the responder and show the replay then differs, then remove it",
            mistakes=[
                "Depending on the clock or random values, so replay is never identical.",
                "Mutating a shared history so the second run starts from dirty state.",
                "Comparing only the last reply instead of the whole transcript when checking a replay.",
            ],
            q1=(
                "What property must a bot have for replay to be meaningful?",
                "It must be deterministic and a pure function of its turns and state, so the same input always rebuilds the same transcript.",
            ),
            homework=(
                "Write `session(turns)` that runs user turns through a responder and returns the full history. Run "
                "it twice on the same turns, print both transcripts, assert they are equal, and comment which line "
                "removes the dependence on any outside state."
            ),
            patterns=["def ", "for ", "assert "],
            mapping=(
                "Evaluation harnesses replay recorded conversations through an updated bot to catch regressions; "
                "the same idea powers golden-transcript tests in CI."
            ),
        ),
        88: dict(
            topic="Scripted conversations in tests",
            idea=(
                "A conversation is a value, so it can be tested like any other value. Instead of clicking through a "
                "chat window and hoping, you write the user turns as a fixed list, run them through the bot, and "
                "assert on the replies. This is the cheapest high-value habit in chatbot development, because "
                "conversation bugs are usually order-dependent and only appear after several turns. A good "
                "scripted test names the scenario, drives a few turns, and checks the properties that matter: the "
                "last reply is non-empty, the bot asked for the missing slot, the tool was called once. It is not a "
                "snapshot of every character; brittle tests that pin exact wording break on every harmless edit. "
                "Today you write a tiny test function that drives three turns through a booking bot and asserts "
                "each reply. Because nothing touches a network or a clock, it runs in milliseconds and never "
                "flakes. When you later add a real model, keep these tests as guardrails around the parts that "
                "must remain deterministic, and let them define what 'still working' means for the bot. Run them "
                "often, because they cost almost nothing and catch the order-dependent bugs that manual clicking "
                "through a chat window rarely finds."
            ),
            code="""\
def bot(text):
    if text == "hi":
        return "hello"
    if "book" in text:
        return "what day?"
    return "please rephrase"

def test_conversation():
    turns = ["hi", "book a room", "blah"]
    replies = [bot(t) for t in turns]
    assert replies == ["hello", "what day?", "please rephrase"]
    return replies

print("replies:", test_conversation())
print("all assertions passed")

assert test_conversation()[-1] == "please rephrase"
print("scripted turns make a conversation a unit test")
""",
            variant_b="assert that every reply is a non-empty string instead of pinning exact wording",
            variant_c="add a turn that must trigger a fallback and assert the fallback text appears",
            mistakes=[
                "Snapshotting exact wording, so harmless copy edits break the test.",
                "Testing only single turns, missing bugs that need conversation context.",
                "Depending on a live model, so the test is slow and non-deterministic.",
            ],
            q1=(
                "Why test properties of a conversation rather than exact reply wording?",
                "Exact snapshots break on harmless copy changes, while properties such as a non-empty reply or a fresh question catch real regressions without freezing the text.",
            ),
            homework=(
                "Write `test_conversation()` that drives a list of user turns through a booking bot and asserts the "
                "replies. Include a greeting, a booking request and a fallback, print the replies, and comment "
                "which line keeps the scenario fixed and order-dependent."
            ),
            patterns=["def ", "assert ", "print("],
            mapping=(
                "Framework test suites and evaluation tools scripted conversations this way; pytest-style tests "
                "around the deterministic parts are standard before a model is wired in."
            ),
        ),
        89: dict(
            topic="Review: messages and conversations checklist",
            idea=(
                "This phase built one idea in fifteen steps: a conversation is a list of typed messages, and every "
                "interesting behaviour — roles, ordering, windows, budgets, states, references, logging, replay — "
                "is a function over that list. A useful way to consolidate is a checklist you can run against any "
                "bot, small or large. Does every message have a role and content? Does the history start with a "
                "system prompt and end with an assistant reply? Is there a window or budget that bounds what gets "
                "sent? Can the same turns be replayed to the same result? Does the bot ask when it is unsure "
                "instead of guessing? Are turns logged as structured records rather than raw dumps? None of these "
                "are about models; they are about the plumbing around them, and they are where most production "
                "bugs live. Today you build a small history and assert a handful of these properties at once, "
                "printing each check. Treat the checklist as a portable review script: run it whenever you change "
                "how conversations are stored or trimmed. If a later change breaks one of these checks, the "
                "checklist tells you which invariant you just gave up, before the break reaches a user. "
                "Everything later in the course assumes these invariants hold."
            ),
            code="""\
def build(system, user_turns):
    history = [{"role": "system", "content": system}]
    for t in user_turns:
        history.append({"role": "user", "content": t})
        history.append({"role": "assistant", "content": t[::-1]})
    return history

history = build("Be brief.", ["one", "two"])

checks = {
    "has system": history[0]["role"] == "system",
    "ends with assistant": history[-1]["role"] == "assistant",
    "every turn typed": all(m["role"] in {"system", "user", "assistant"} for m in history),
}
for name, ok in checks.items():
    print(f"{name}: {ok}")

assert all(checks.values())
print("a conversation checklist is assertions over the transcript")
""",
            variant_b="add a check that the history can be replayed to an identical transcript",
            variant_c="turn the checks into a `review(history)` function that returns the failing names",
            mistakes=[
                "Reviewing only the newest reply instead of the whole transcript.",
                "Treating the checklist as one-off rather than rerunning it after each change.",
                "Storing conversations in forms that break the invariants the checklist encodes.",
            ],
            q1=(
                "Why turn the phase's lessons into an executable checklist?",
                "An executable list of properties runs on every change, so the invariants stay true instead of being remembered and gradually broken.",
            ),
            homework=(
                "Write `review(history)` that runs at least three checks over a conversation and returns the names "
                "of the ones that fail. Build a small history, print the result, and comment which line makes the "
                "checklist reusable on any transcript."
            ),
            patterns=["def ", "assert ", "return"],
            mapping=(
                "Production teams keep such checks as schema validation and invariant tests around their "
                "conversation stores, exactly as shown here."
            ),
        ),
    },
)
