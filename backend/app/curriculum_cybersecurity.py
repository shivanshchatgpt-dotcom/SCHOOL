"""Flagship Cryptography curriculum: hand-authored days 1-14 and 75-179.

Covers ONLY the cryptography path (slug `cryptography`). Days 15-74 (shared
Python phases) and day 180 are preserved and never authored here.

Safety contract for every example: stdlib only (hashlib, hmac, secrets,
struct, base64, json, re, math), deterministic output (randomness shown only
through fixed properties such as lengths — never printed raw), in-memory
only (no files, no sockets, no network), no real credentials anywhere.
Teaching ciphers are labelled TEACHING CIPHER in both prose and homework;
production guidance always names real primitives (AES-GCM, SHA-256, PBKDF2
with high iteration counts, TLS 1.3) and the libraries that provide them.
PBKDF2 demos use small iteration counts to run fast and say so; the text
states the real-world counts. Nothing here claims toy code is production
cryptography.

Each entry: topic, idea, code (prints only, deterministic), variant_b/c,
mistakes[3], qa ([3 lesson-specific Q], [3 A]), homework (named contract),
patterns, mapping (the real-world counterpart).
"""

from __future__ import annotations

DOMAIN = "Cryptography"

FOUNDATION = {
    1: dict(
        topic="First secure program",
        idea="Security work starts with exactness: bytes are not strings, lengths matter, and randomness must come from the right source. Python's secrets module draws from the operating system's cryptographic randomness, unlike the random module, which is deterministic and predictable once seeded — fine for games and shuffling practice data, disqualifying for tokens, passwords and keys. Today's program prints fixed labels and one measured fact about fresh randomness (its length, never its value), establishing two habits that never leave this track: use secrets for anything an adversary must not guess, and never print, log or commit actual secret material, only its properties. Count bits explicitly from day one: token_bytes(16) means 128 bits of guessing work, and stating the number keeps 'probably enough' out of security discussions. State the threat model with every token: who must not guess it, for how long, and what happens if they do. Short-lived tokens need fewer bits than decade-long keys, so lifetime sets the budget.",
        code=(
            'import secrets\n'
            '\n'
            'print("Cryptography track, day 1")\n'
            'token = secrets.token_bytes(16)\n'
            'print("fresh token length:", len(token), "bytes")\n'
            'print("type:", type(token).__name__)\n'
            'assert len(token) == 16\n'
            'assert isinstance(token, bytes)\n'
            'print("randomness source: operating system (never printed raw)")'
        ),
        variant_b='token_bytes(32) (what length prints, and why does length double the guessing work per bit?)',
        variant_c='token_hex(16) (how many characters, and why twice the byte count?)',
        mistakes=[
            "Printing the token itself into logs, terminals or homework submissions.",
            "Using random.randint for anything security-sensitive because it 'looked random'.",
            "Assuming 16 bytes is 'probably enough' without counting the bits (16 bytes = 128 bits).",
        ],
        qa=(
            ["Why must randomness for tokens come from secrets rather than random?",
             "Why does the example print the token's length but never its value?",
             "How many bits of guessing work does a 16-byte token force on an attacker?"],
            ["secrets draws from OS cryptographic randomness, while random is deterministic and reproducible once seeded — predictable to anyone who learns the seed.",
             "Values are secrets; lengths are properties. Printing values leaks them into terminals, logs and histories, while lengths prove generation worked without exposing anything.",
             "128 bits: each byte contributes 8 bits, and brute force scales as 2^128 guesses, which is infeasible by any physically plausible means."],
        ),
        homework="Write `token_report(n)` that generates secrets.token_bytes(n), prints only its length and type, and returns n. Run it for n=16 and n=32, print both reports, and comment which line would leak if it printed the value.",
        patterns=["import secrets", "print("],
        mapping="Real tokens (session IDs, API keys, password-reset links) are secrets.token_urlsafe output stored hashed; this day builds the handling discipline first.",
    ),
    2: dict(
        topic="Bytes versus strings",
        idea="Cryptography operates on bytes; humans read strings; confusing the two corrupts both. Encoding (str → bytes, via UTF-8) and decoding (bytes → str) are total, explicit operations — Python 3 refuses to mix them silently, and that refusal is a security feature, because implicit conversions in older languages smuggled malformed data past checks. Hash functions, HMAC and ciphers all take bytes, so every lesson in this track starts by encoding deliberately and decoding only validated output. The day's second lesson is errors='strict' by default: undecodable bytes raise instead of guessing, and guessing is how mojibake — and worse, parser differentials — are born. Make encode-at-the-boundary a reflex: data crosses into bytes once, at a named line, and every hash or cipher call below takes bytes without further thought. Mixed str/bytes code is a latent TypeError at best and a decoding oracle at worst. Centralise the boundary in one helper per input source so every conversion is reviewable in a single place.",
        code=(
            'text = "attack at dawn"\n'
            'raw = text.encode("utf-8")\n'
            'print("string:", text)\n'
            'print("bytes:", raw)\n'
            'print("lengths:", len(text), "chars vs", len(raw), "bytes")\n'
            'back = raw.decode("utf-8")\n'
            'print("round-trip identical:", back == text)\n'
            'emoji = "🔒"\n'
            'print("one lock:", len(emoji), "char,", len(emoji.encode("utf-8")), "bytes")'
        ),
        variant_b='a café with accented characters (when do char and byte counts diverge?)',
        variant_c='raw.decode("ascii") on the lock bytes (which error, and why is raising correct?)',
        mistakes=[
            "Hashing the string directly and wondering why hashlib refuses it.",
            "Decoding with errors='ignore', silently dropping attack bytes.",
            "Assuming one character equals one byte for non-ASCII input.",
        ],
        qa=(
            ["Why does hashlib demand bytes instead of accepting strings?",
             "Why is decode-then-validate safer than validating the raw bytes?",
             "What does errors='strict' protect you from?"],
            ["Hash and cipher algorithms are defined over byte sequences; accepting strings would hide an encoding choice (UTF-8? Latin-1?) that changes every digest.",
             "Validation rules are written for characters (lengths, alphabets), while attacks hide in byte-level tricks like overlong encodings — decode first, then judge what you can read.",
             "Silent data loss: undecodable bytes vanish instead of raising, so malformed or hostile input passes checks it should have failed."],
        ),
        homework="Write `byte_report(text)` that encodes to UTF-8, prints char count vs byte count, decodes back, and asserts the round-trip. Run it on ASCII and emoji text, print both, and comment which line would corrupt on silent errors.",
        patterns=['.encode(', '.decode('],
        mapping="Every hash, HMAC and cipher call in this track takes .encode('utf-8') input; TLS, JWT and password hashes are all bytes-first formats.",
    ),
    3: dict(
        topic="Hex and base64: bytes you can read",
        idea="Bytes travel badly through text channels — terminals mangle them, JSON rejects them, URLs re-encode them — so binary data gets text armour: hex doubles the size but stays readable and comparable at a glance, base64 grows it by a third and packs tighter for tokens and keys. Neither is encryption or hashing; both are reversible packaging, and confusing packaging with protection is a classic vulnerability (base64 'encoded' passwords are plaintext to anyone who looks). Fingerprints are hex digests, PEM keys are base64 with armour lines, and reading either format fluently is required equipment for log analysis, certificate inspection and hash comparison. Practice reading both formats until conversion is instant; incident work never pauses for format confusion. Fingerprints compare in hex, keys travel in base64, and knowing which is which prevents category errors under pressure. When comparing fingerprints, compare hex to hex after normalising case, never raw bytes to text.",
        code=(
            'import hashlib\n'
            'import base64\n'
            '\n'
            'digest = hashlib.sha256(b"attack at dawn").digest()\n'
            'print("raw bytes:", len(digest))\n'
            'print("hex:   ", digest.hex())\n'
            'print("base64:", base64.b64encode(digest).decode("ascii"))\n'
            'assert bytes.fromhex(digest.hex()) == digest\n'
            'assert base64.b64decode(base64.b64encode(digest)) == digest\n'
            'print("both round-trip: packaging, not protection")'
        ),
        variant_b='hex of b"" (what does an empty digest look like, and what breaks downstream?)',
        variant_c='base64 of 16 token bytes (how many characters, and why the = padding?)',
        mistakes=[
            "Calling base64 'encryption' and storing 'encoded' secrets as if protected.",
            "Comparing a hex string against raw bytes and concluding a mismatch means tampering.",
            "Stripping = padding and breaking decoders that require it.",
        ],
        qa=(
            ["Why is base64 not encryption?",
             "When would you choose hex over base64 for a fingerprint?",
             "What does the = padding in base64 record?"],
            ["It is a reversible, keyless, publicly documented packaging with zero secrecy — anyone decodes it instantly, so it protects nothing.",
             "When humans compare values (fingerprints, checksums): hex aligns in pairs, shows byte boundaries, and diffs cleanly by eye.",
             "How many bytes the final group was short of three, so the decoder restores the exact original length instead of guessing."],
        ),
        homework="Write `armour(data)` returning (hex_str, b64_str) for input bytes and asserting both round-trips. Run it on two digests, print both pairs, and comment which format a human should compare.",
        patterns=[".hex()", "b64encode("],
        mapping="SHA-256 fingerprints print as 64 hex chars; PEM certificates wrap base64 in armour lines; JWTs dot-join three base64url parts.",
    ),
    4: dict(
        topic="Validating untrusted input",
        idea="Every byte from outside — usernames, filenames, URLs, API fields — is hostile until validated: check type, length bounds, alphabet and shape before use, and reject loudly rather than cleaning silently. Silent cleaning ('remove bad characters') creates parser differentials, where your filter sees one string and the downstream consumer sees another — the mechanism behind classic injection bugs. Validation order matters too: length first (cheap rejection of absurd input), then alphabet, then semantics. Today's checker returns True/False plus a reason, because distinguishing 'rejected, too long' from 'rejected, bad alphabet' in logs turns debugging from archaeology into reading. Log the reason with every rejection so blocklists and audits can distinguish attacks (bad alphabet) from accidents (bad length). Allowlist alphabets beat blocklists every time: enumerate what is permitted and refuse the infinite rest. Blocklists fail open against novel attacks, while allowlists fail closed against everything unlisted by construction.",
        code=(
            'def valid_username(value):\n'
            '    if not isinstance(value, str):\n'
            '        return False, "not text"\n'
            '    if not 3 <= len(value) <= 20:\n'
            '        return False, "bad length"\n'
            '    if not value.isalnum():\n'
            '        return False, "bad alphabet"\n'
            '    return True, "ok"\n'
            '\n'
            'for probe in ["ada", "x", "a" * 25, "ada;DROP", 42]:\n'
            '    print(repr(probe)[:18], "->", valid_username(probe))'
        ),
        variant_b='allow underscore and dash (which check changes, and what new risks arrive?)',
        variant_c='a 10-million-character string (which check fires first, and why does order matter?)',
        mistakes=[
            "Cleaning hostile input instead of rejecting it, creating filter-vs-consumer differentials.",
            "Length checks last, letting absurd input burn CPU in later checks (ReDoS-shaped thinking).",
            "Boolean-only returns that leave logs unable to say why input died.",
        ],
        qa=(
            ["Why reject rather than clean hostile input?",
             "Why check length before alphabet?",
             "Why return a reason alongside True/False?"],
            ["Cleaning creates two views of one string — the filter's and the consumer's — and attackers live in the gap between them; rejection has exactly one view.",
             "Length is O(1) and kills absurd input before expensive checks run; order is a cheap performance and safety win.",
             "Reasons make logs diagnostic ('bad alphabet') instead of mysterious ('rejected'), which is the difference between debugging and archaeology."],
        ),
        homework="Write `valid_username(value)` returning (bool, reason) with type, length 3–20 and alphanumeric checks. Run it on five probes including a non-string, print all verdicts, and comment which check fires first on huge input.",
        patterns=["def ", "return"],
        mapping="Allowlist validation is the first control in OWASP input-validation guidance; every web lesson in this track assumes validated input.",
    ),
    5: dict(
        topic="Looping over byte values",
        idea="Cryptanalysis and parsing both reduce to walking bytes: counting frequencies, finding markers, XOR-ing streams, slicing records. Iterating bytes yields integers 0–255 (not characters), and that single fact prevents a whole class of confusion — comparisons, arithmetic and bit-ops all work directly on values. Frequency counting is the day's payoff: English text has a fingerprint (e most common, then t/a/o), and any monoalphabetic disguise preserves it, which is exactly how day 108's Caesar-breaker will work. Learn to see byte streams as countable populations, because statistics over bytes is where analysis starts. Keep a frequency printer in your toolbox; it is the first instrument pointed at every unknown byte stream. Compare observed frequencies against uniform: closeness to flat separates ciphertext from prose. Run the frequency check before deeper analysis to avoid wasting effort decrypting random noise.",
        code=(
            'data = b"attack at dawn, attack at dusk"\n'
            'freq = {}\n'
            'for byte in data:\n'
            '    freq[byte] = freq.get(byte, 0) + 1\n'
            'top = sorted(freq.items(), key=lambda kv: kv[1], reverse=True)[:3]\n'
            'print("bytes seen:", len(freq), "distinct of", len(data), "total")\n'
            'for value, count in top:\n'
            '    print(f"byte {value} ({chr(value)!r}): {count}x")\n'
            'print("most common:", repr(chr(top[0][0])))'
        ),
        variant_b='b"\\x00\\xff\\x00\\xff" (what does frequency say about binary vs text?)',
        variant_c='a 3-byte input (which statistics are meaningless at tiny sizes?)',
        mistakes=[
            "Treating iterated bytes as characters and comparing against 'a' instead of 97.",
            "Trusting frequency statistics on a dozen bytes, where noise drowns signal.",
            "Forgetting bytes() immutability and 'modifying' a copy that is discarded.",
        ],
        qa=(
            ["Why does iterating bytes yield integers rather than characters?",
             "Why does frequency analysis need enough text to work?",
             "What does a flat frequency table suggest about the data?"],
            ["Bytes are values 0–255; only decoding maps values to characters, and analysis usually wants the values for arithmetic and comparison.",
             "Statistics converge with samples: a dozen bytes show noise, while paragraphs reveal the language's fingerprint (e dominating).",
             "Randomness or encryption — uniform bytes carry no statistical fingerprint, which is itself a finding (day 89 uses it as a randomness test)."],
        ),
        homework="Write `top_bytes(data, n)` returning the n most common byte values with counts. Run it on English text and on 16 token bytes, print both, and comment what the difference reveals.",
        patterns=["for ", ".get("],
        mapping="Frequency analysis breaks classical ciphers (day 108); entropy estimation distinguishes encrypted from plaintext traffic.",
    ),
    6: dict(
        topic="Lists of log lines",
        idea="Security monitoring is list processing: logs arrive as lines, lines split into fields, fields filter into alerts. The pipeline — read lines, parse each into a record, keep records matching a predicate, summarise — is the shape of every SIEM query, firewall review and audit script you will ever write. List comprehensions keep each stage visible and testable, and counting by category (how many 403s? which IPs repeat?) turns raw text into situational awareness. Today's parser handles the happy path plus malformed lines explicitly, because real logs always contain both, and a parser that crashes on line 900 teaches nothing about lines 901 onward.",
        code=(
            'lines = [\n'
            '    "2026-01-01 10:00:01 10.0.0.5 GET /index 200",\n'
            '    "2026-01-01 10:00:02 10.0.0.9 GET /admin 403",\n'
            '    "2026-01-01 10:00:03 BOGUS LINE HERE",\n'
            '    "2026-01-01 10:00:04 10.0.0.9 GET /admin 403",\n'
            ']\n'
            '\n'
            'def parse(line):\n'
            '    parts = line.split()\n'
            '    if len(parts) != 6:\n'
            '        return None\n'
            '    return {"ip": parts[2], "path": parts[4], "status": parts[5]}\n'
            '\n'
            'records = [r for line in lines for r in [parse(line)] if r is not None]\n'
            'denied = [r for r in records if r["status"] == "403"]\n'
            'print("parsed:", len(records), "of", len(lines))\n'
            'print("denied:", len(denied), "from ips:", sorted({r["ip"] for r in denied}))'
        ),
        variant_b='a line with 7 fields (does strict parsing drop it, and should it?)',
        variant_c='all lines BOGUS (what do empty results mean downstream?)',
        mistakes=[
            "Indexing split parts without checking the count — one malformed line crashes the audit.",
            "Dropping malformed lines silently instead of counting them (attacker-shaped gaps hide there).",
            "Parsing timestamps as strings and sorting alphabetically across formats.",
        ],
        qa=(
            ["Why return None for malformed lines instead of raising?",
             "Why count dropped lines separately?",
             "What makes the comprehension pipeline auditable?"],
            ["One bad line must not kill the other ten thousand; None marks the failure while the pipeline continues, and the drop count stays visible.",
             "Drops are evidence too — a sudden burst of malformed lines can itself be the attack (log injection, evasion attempts).",
             "Each stage (parse, filter, summarise) is a pure transformation over the previous list, so any stage's output can be printed, counted and tested alone."],
        ),
        homework="Write `parse(line)` returning a record dict or None, then summarise denied requests by IP. Run it on two log batches, print both summaries, and comment which line survives malformed input.",
        patterns=["def ", ".split("],
        mapping="SIEM queries, firewall reviews and audit scripts share this pipeline shape; days 165+ scale it to full analyzers.",
    ),
    7: dict(
        topic="Hash helper functions",
        idea="Hashing turns arbitrary bytes into a fixed-size fingerprint: same input always yields the same digest (deterministic), different inputs avalanche into unrelated digests, and reversing a good hash is infeasible. Wrapping hashlib.sha256 in one helper centralises three decisions — algorithm choice, UTF-8 encoding, hex output — so the other hundred days call fingerprint(data) instead of re-deciding. Centralisation is a security control: when SHA-256 eventually retires, one function changes, not a hundred call sites. Today's helper also prints digest length (64 hex chars, 256 bits), because naming sizes precisely is how professionals discuss strength without hand-waving. Say '256-bit preimage resistance' instead of 'very secure' — precise claims can be checked, vague ones cannot. Write sizes into function names and comments where they matter: sha256_64hex leaves no room for misreading the contract. Review helpers for implicit choices like default encodings and make every one of them explicit.",
        code=(
            'import hashlib\n'
            '\n'
            'def fingerprint(data: bytes) -> str:\n'
            '    return hashlib.sha256(data).hexdigest()\n'
            '\n'
            'a = fingerprint(b"attack at dawn")\n'
            'b = fingerprint(b"attack at dawn")\n'
            'c = fingerprint(b"attack at dusk")\n'
            'print("hex chars:", len(a), "| bits:", len(a) * 4)\n'
            'print("deterministic:", a == b)\n'
            'print("avalanche (differing chars):", sum(1 for x, y in zip(a, c) if x != y), "of", len(a))'
        ),
        variant_b='b"" empty input (is an empty fingerprint meaningful or a bug magnet?)',
        variant_c='one-bit change (flip a single input bit — how many hex chars move?)',
        mistakes=[
            "Hashing str instead of bytes and meeting TypeError in production.",
            "Comparing digests with == on secrets (timing leaks — day 11 fixes this).",
            "Scattering hashlib calls everywhere instead of one helper (algorithm agility dies).",
        ],
        qa=(
            ["Why centralise hashing in one helper function?",
             "What does the avalanche count demonstrate?",
             "Why is determinism a requirement, not a convenience?"],
            ["Algorithm agility: when primitives retire, one function changes instead of a hundred scattered call sites with possibly different choices.",
             "Tiny input changes scramble most output chars — diffusion, the property that stops attackers from sculpting inputs toward a target digest.",
             "Verification demands recomputation: integrity checks, password verification and content addressing all re-hash and compare, which needs identical outputs."],
        ),
        homework="Write `fingerprint(data)` returning the SHA-256 hex digest of bytes. Run it on two inputs twice each, print determinism checks, and comment which line fixes the algorithm choice.",
        patterns=["def ", "sha256("],
        mapping="Git addresses content by SHA-1/SHA-256, downloads verify against published digests, and every integrity lesson calls this helper.",
    ),
    8: dict(
        topic="Verify returns True or False",
        idea="Verification is a boolean with a reason: recompute the expected value, compare in constant time later (day 11), and answer True or False — never 'probably', never an exception for a wrong guess. Wrong passwords, tampered files and forged tags are normal operating conditions, not errors, so they return False through the same calm path as True. The function shape — verify(candidate, expected) -> bool — recurs across passwords, MACs, signatures and certificates; learning it once on hashes transfers everywhere. Crucially, verification never reveals why something failed differently for 'unknown user' versus 'wrong password': distinct failure signals are an oracle attackers query one bit at a time. Design every verification path so wrong and right travel identical code paths with identical timing and identical messages. Audit login flows specifically for early exits that distinguish 'no such user' from 'wrong password'. Sleep a fixed delay on all failures so timing cannot distinguish the branches even coarsely.",
        code=(
            'import hashlib\n'
            '\n'
            'def verify(candidate: bytes, expected_hex: str) -> bool:\n'
            '    return hashlib.sha256(candidate).hexdigest() == expected_hex\n'
            '\n'
            'good = hashlib.sha256(b"attack at dawn").hexdigest()\n'
            'print("right input: ", verify(b"attack at dawn", good))\n'
            'print("wrong input: ", verify(b"attack at dusk", good))\n'
            'print("empty input: ", verify(b"", good))\n'
            'print("wrong is False, not an exception: normal operation")'
        ),
        variant_b='expected_hex with one char changed (does any True leak through?)',
        variant_c='candidate=b"ATTACK AT DAWN" uppercase (why must verification be case-exact?)',
        mistakes=[
            "Raising exceptions on wrong guesses, turning normal failures into crashes and logs full of noise.",
            "Returning different errors for unknown-user vs wrong-password (user-enumeration oracle).",
            "Comparing with == on secret-derived values (timing side channel — day 11).",
        ],
        qa=(
            ["Why must wrong guesses return False instead of raising?",
             "Why give identical responses for unknown users and wrong passwords?",
             "What does verify() promise about timing?"],
            ["Wrong guesses are expected traffic, not exceptional conditions; exceptions would crash loops, flood logs, and complicate every caller for no benefit.",
             "Distinct responses let attackers enumerate valid usernames one probe at a time — identical responses close the oracle.",
             "Nothing yet — == leaks timing here; day 11 replaces it with constant-time comparison. Noticing the gap is today's second lesson."],
        ),
        homework="Write `verify(candidate, expected_hex)` returning a strict bool for hash equality. Run it on right/wrong/empty candidates, print all three verdicts, and comment why wrong returns False calmly.",
        patterns=["def ", "return"],
        mapping="Password checks, MAC verification, signature checks and certificate validation share this boolean shape with uniform failure signals.",
    ),
    9: dict(
        topic="Dictionaries for headers and config",
        idea="Security metadata travels as mappings: HTTP headers, JWT claims, certificate fields, configuration knobs. Dictionaries hold them naturally, .get() with defaults handles absent fields without crashing, and iterating items() makes allowlist checks ('every header value must match policy') one loop. The day's security lesson is fail-closed defaults: look up with a default that denies (role = 'guest', access = False) so missing keys fail safe instead of failing open. Open lookups (config['admin']) crash on absence; worse, try/except around them sometimes defaults to permissive — audit every default for which direction it fails. When a key is absent, the safe answer is almost always denial — presence must be proven, never assumed. Treat every absent field as an explicit deny in access decisions; convenience defaults belong nowhere near authorization. Default-deny extends to configuration: unset security knobs must resolve to their strictest values. Review configuration defaults on every release because new knobs arrive with vendor chosen values that favour convenience over safety.",
        code=(
            'headers = {"content-type": "text/html", "x-frame-options": "DENY"}\n'
            '\n'
            'def check_headers(headers):\n'
            '    findings = []\n'
            '    if headers.get("x-frame-options") != "DENY":\n'
            '        findings.append("missing clickjacking guard")\n'
            '    if "content-security-policy" not in headers:\n'
            '        findings.append("missing CSP")\n'
            '    print("checked", len(headers), "headers ->", len(findings), "findings")\n'
            '    return findings\n'
            '\n'
            'print(check_headers(headers))\n'
            'print(check_headers({}))\n'
            'print("absent header = finding, never a crash")'
        ),
        variant_b='headers with CSP present (which finding disappears?)',
        variant_c='None instead of a dict (where should the guard live?)',
        mistakes=[
            "Direct key access on untrusted mappings, crashing on absent fields.",
            "Permissive defaults (role='admin') that fail open on missing keys.",
            "Case-sensitive header lookups missing 'X-Frame-Options' capitalised variants.",
        ],
        qa=(
            ["Why do fail-closed defaults matter more than convenience defaults?",
             "Why use .get() instead of direct indexing on untrusted mappings?",
             "What does an absent security header mean?"],
            ["Missing data is the adversary's favourite state: fail-closed denies by default, while fail-open grants exactly when evidence is absent.",
             "Direct indexing raises on absent keys, turning attacker-controlled absence into crashes; .get() keeps the decision in your code.",
             "A finding, not an error: the check reports the gap and continues auditing everything else."],
        ),
        homework="Write `check_headers(headers)` returning a findings list for two required security headers. Run it on full/partial/empty dicts, print all three, and comment which lookup never crashes.",
        patterns=[".get(", "def "],
        mapping="HTTP security headers, JWT claims and certificate fields are all mappings audited exactly this way (days 140+).",
    ),
    10: dict(
        topic="Surviving malformed input",
        idea="Attackers send malformed data deliberately: truncated base64, odd-length hex, invalid UTF-8, absurd lengths. A decoder that raises on garbage is correct behaviour — the vulnerability is in callers that let the exception escape, crashing services (denial of service by unhandled exception) or skipping checks placed after the crash point. The pattern is validate-then-decode inside try/except with narrow exception types, returning a verdict instead of propagating: binascii.Error and ValueError caught, everything else left to fail loudly (catching Exception hides MemoryError-class bugs and real defects). Today's decoder proves malformed input becomes a calm False, never a traceback. Count every calm refusal in metrics; a sudden spike in malformed input is often the first sign of probing. Alert on refusal-rate spikes the same way you alert on failures: calm handling plus loud monitoring beats either alone. Dashboard refusal rates alongside failure rates so operators see probing campaigns forming in real time. Graph refusal reasons over time as well, since a shift from length failures to alphabet failures signals an attacker learning the filter. Escalate sustained probing to incident response instead of watching it continue indefinitely.",
        code=(
            'import base64\n'
            'import binascii\n'
            '\n'
            'def safe_b64decode(text: str):\n'
            '    try:\n'
            '        raw = base64.b64decode(text, validate=True)\n'
            '    except (binascii.Error, ValueError):\n'
            '        return None\n'
            '    return raw\n'
            '\n'
            'print("valid:  ", safe_b64decode("aGVsbG8="))\n'
            'print("garbage:", safe_b64decode("!!!not-base64!!!"))\n'
            'print("truncated:", safe_b64decode("aGVsbG8"))\n'
            'print("malformed becomes None: calm, countable, safe")'
        ),
        variant_b='validate=False (which garbage slips through, and where does it detonate?)',
        variant_c='a 10MB string of "A" (does decoding allocate before validating?)',
        mistakes=[
            "Bare except: hiding real bugs alongside malformed input.",
            "Letting decode exceptions escape request handlers (crash-as-a-service for attackers).",
            "Validating after decoding instead of constraining size first.",
        ],
        qa=(
            ["Why catch binascii.Error specifically instead of all exceptions?",
             "Why return None rather than raising a custom error?",
             "What does validate=True change?"],
            ["Narrow catches handle expected garbage while letting real defects (bugs, resource exhaustion) fail loudly instead of hiding inside normal flow.",
             "None keeps the pipeline total: every input maps to bytes-or-None, so callers branch instead of try/excepting, and drop counts stay measurable.",
             "It rejects non-alphabet characters outright; without it, the decoder skips junk silently and returns bytes the sender never intended."],
        ),
        homework="Write `safe_b64decode(text)` returning bytes or None with narrow excepts. Run it on valid/garbage/truncated inputs, print all three, and comment which exception types are caught.",
        patterns=["try:", "except"],
        mapping="Every parser boundary in this track (PEM, tokens, logs, chain files) uses validate-then-decode with narrow catches.",
    ),
    11: dict(
        topic="Comparing secrets in constant time",
        idea="String == short-circuits: it returns False at the first differing byte, so comparison time leaks how many leading bytes matched. Attackers measure that timing over many probes and recover secrets byte-by-byte — the classic timing oracle, practical over networks with statistics. hmac.compare_digest runs in time independent of match position, closing the oracle for digests, MACs and tokens. Rule: compare_digest for anything secret-derived or attacker-influenced; == stays fine for non-secret control flow. Today's verifier upgrades day 8's == and demonstrates the upgrade changes nothing observable except the leak — same True/False, no oracle. Apply the same upgrade to tokens, session IDs and password hashes — anywhere attacker-influenced bytes meet comparison. Grep the codebase for == beside secrets periodically; each hit is a timing oracle awaiting discovery. Schedule the grep quarterly because new code introduces new comparisons continuously. Cover tokens, session identifiers and password hashes in the same review pass so no secret comparison escapes notice.",
        code=(
            'import hashlib\n'
            'import hmac\n'
            '\n'
            'def verify_ct(candidate: bytes, expected_hex: str) -> bool:\n'
            '    actual = hashlib.sha256(candidate).hexdigest()\n'
            '    return hmac.compare_digest(actual, expected_hex)\n'
            '\n'
            'good = hashlib.sha256(b"attack at dawn").hexdigest()\n'
            'print("right:", verify_ct(b"attack at dawn", good))\n'
            'print("wrong:", verify_ct(b"attack at dusk", good))\n'
            'print("both str inputs ok:", hmac.compare_digest("abc", "abc"))\n'
            'print("same verdicts as day 8, minus the timing oracle")'
        ),
        variant_b='comparing bytes vs str mixed (what does compare_digest demand?)',
        variant_c='different-length digests (does it still run constant-time, and why must it?)',
        mistakes=[
            "== on tokens, MACs or password hashes anywhere in the codebase.",
            "compare_digest on attacker-controlled lengths leaking length first (compare lengths separately is fine — length is rarely secret).",
            "Rolling a custom 'constant-time' loop that compilers optimise back into short-circuits.",
        ],
        qa=(
            ["How does short-circuit comparison leak secret bytes?",
             "Why is compare_digest still safe on different-length inputs?",
             "When is == acceptable?"],
            ["It exits at the first mismatch, so matching prefixes take measurably longer — statistics over probes reveal the secret byte by byte.",
             "It still processes fully without early exit keyed to content; length may leak, but lengths of fixed-size digests are public anyway.",
             "For non-secret control flow (config flags, enum states) where timing reveals nothing an attacker can use."],
        ),
        homework="Write `verify_ct(candidate, expected_hex)` hashing then constant-time comparing. Run it on right/wrong inputs, print both, and comment which call closes the oracle.",
        patterns=["compare_digest(", "def "],
        mapping="Token checks, HMAC verification, password-hash comparison and signature checks all use compare_digest from here on.",
    ),
    12: dict(
        topic="Asserting crypto invariants",
        idea="Cryptographic code fails silently: a truncated digest still hex-encodes, a reused nonce still 'works', a 40-bit key encrypts without complaint. Asserts convert silent wrongness into loud failure at the guilty line — digest lengths (64 hex chars for SHA-256), token byte counts, nonce uniqueness within a scope, iteration counts above policy minimums. Assert the contract (lengths, types, ranges), never specific values (digests change with inputs by design). These five asserts around every crypto helper cost seconds and catch the class of bug where everything runs and everything is wrong — the most dangerous class in security code. Run these asserts on adversarial inputs too, not just happy paths; the failure mode is the product in security code. Document what each helper refuses alongside what it computes, so callers handle both paths deliberately. Every helper documents its calm-None cases separately from its loud-assert cases. Callers should branch on the documented calm cases explicitly instead of wrapping every helper call in a broad try block.",
        code=(
            'import hashlib\n'
            'import secrets\n'
            '\n'
            'def checked_digest(data: bytes) -> str:\n'
            '    assert isinstance(data, bytes), "hash bytes, not str"\n'
            '    digest = hashlib.sha256(data).hexdigest()\n'
            '    assert len(digest) == 64, "sha256 hex is 64 chars"\n'
            '    return digest\n'
            '\n'
            'def fresh_nonce(n: int = 16) -> bytes:\n'
            '    assert n >= 16, "nonces below 128 bits are toys"\n'
            '    token = secrets.token_bytes(n)\n'
            '    assert len(token) == n\n'
            '    return token\n'
            '\n'
            'print("digest ok:", checked_digest(b"audit")[:12], "...")\n'
            'print("nonce ok:", len(fresh_nonce()), "bytes")'
        ),
        variant_b='n=8 nonce (which assert fires, and is the policy right?)',
        variant_c='a str passed to checked_digest (which assert fires first?)',
        mistakes=[
            "Asserting exact digest values, fossilising one input instead of the contract.",
            "No minimums on sizes/iterations, so weakened parameters pass silently.",
            "Asserts stripped with python -O in production without a logging fallback (document the trade-off).",
        ],
        qa=(
            ["Why assert contracts (lengths, types) instead of values?",
             "Why enforce a 16-byte nonce minimum in code rather than documentation?",
             "What does python -O do to asserts, and why mention it?"],
            ["Values change legitimately with inputs; contracts hold across all inputs — asserting values tests one case, asserting contracts guards every case.",
             "Documentation is advice; asserts are enforcement — undersized nonces fail loudly at creation instead of weakening a deployed system quietly.",
             "-O removes asserts entirely, trading safety for speed; security-critical checks deserve explicit checks or logging that survive optimisation."],
        ),
        homework="Write `checked_digest(data)` and `fresh_nonce(n)` with type/length/minimum asserts. Run them on good and bad inputs, print outcomes, and comment which assert enforces policy.",
        patterns=["assert ", "sha256("],
        mapping="Length/type/minimum asserts wrap every crypto helper hereafter; exact values are never asserted.",
    ),
    13: dict(
        topic="Pipeline: parse, check, report",
        idea="Day 6's log pipeline meets day 7's hashing: parse each line, fingerprint security-relevant fields, compare against an allowlist of known-good digests, and report matches, mismatches and malformed lines separately. Three verdicts, not two — valid, tampered, unreadable — because incident response treats 'cannot parse' differently from 'parsed but wrong'. Structuring as small functions (parse_line, check_record, summarise) keeps each stage testable, and the summary counts are the deliverable: how many checked, how many failed, how many unreadable. This pipeline shape scales directly to the file-integrity monitor of days 91–92. Three verdicts travel the whole track: valid, tampered, unreadable — each triggering a different response playbook. Unreadable input gets quarantined for inspection, denied input gets logged and dropped, valid input flows onward. Quarantined input gets human review on a schedule, not indefinite storage that becomes its own liability. Expire quarantined items on a fixed schedule and log every expiry for later audit.",
        code=(
            'import hashlib\n'
            '\n'
            'GOOD = {hashlib.sha256(b"allow").hexdigest(), hashlib.sha256(b"permit").hexdigest()}\n'
            '\n'
            'def check_word(word: str):\n'
            '    digest = hashlib.sha256(word.encode()).hexdigest()\n'
            '    if digest in GOOD:\n'
            '        return "allow"\n'
            '    return "deny"\n'
            '\n'
            'results = {}\n'
            'for word in ["allow", "permit", "forbid", "allow"]:\n'
            '    verdict = check_word(word)\n'
            '    results[verdict] = results.get(verdict, 0) + 1\n'
            'print("verdicts:", results)\n'
            'print("allowed words pass, unknown words deny: default-deny")'
        ),
        variant_b='an empty word list (what does an empty summary mean?)',
        variant_c='GOOD containing a weak MD5 digest (which layer must change first?)',
        mistakes=[
            "Default-allow on unknown values — the single most dangerous default in security code.",
            "Two verdicts instead of three, conflating 'unreadable' with 'valid'.",
            "Allowlist checked with == in a loop instead of set membership (timing + speed).",
        ],
        qa=(
            ["Why default-deny unknown values instead of default-allow?",
             "Why three verdicts (allow/deny/unreadable) instead of two?",
             "Why a set for GOOD rather than a list?"],
            ["Unknown is the adversary's favourite state; deny-by-default fails safe while allow-by-default grants precisely when evidence is absent.",
             "'Unreadable' signals parser trouble (possibly attack-shaped) while 'deny' signals a clean negative — different verdicts trigger different responses.",
             "O(1) membership plus no ordering semantics; a list scan is slower and invites timing observations across large allowlists."],
        ),
        homework="Write `check_word(word)` against a GOOD digest set returning allow/deny. Run it on mixed words, print the verdict counts, and comment which default protects unknowns.",
        patterns=["def ", "in GOOD"],
        mapping="Allowlist + default-deny + three verdicts is the shape of file-integrity monitors, auth checks and firewall rules ahead.",
    ),
    14: dict(
        topic="Capstone: tamper-evident log",
        idea="Chain every log entry to the previous entry's digest: entry N stores hash(entry N-1 hash + entry N data), so altering any historical line breaks every later link — tampering becomes detectable by recomputation, not by trust. This hash chain is the entire idea behind Git history, certificate transparency and blockchains, stripped to fifteen lines. Verification walks the chain recomputing each link; the first mismatch names the tamper point. Limitations stated plainly: chains detect tampering after the fact, they do not prevent it; and whoever holds the head digest (the latest hash, kept separately) holds the trust anchor — lose that, and verification loses its reference. Anchor heads separately from logs — a notebook, a second system, a published value — because co-located anchors fall with what they guard. Publish heads to a second system or notebook so verification survives compromise of the log host. Verify the chain on read, not only on write, so tampering between writes is caught promptly.",
        code=(
            'import hashlib\n'
            '\n'
            'def chain(entries):\n'
            '    head = "GENESIS"\n'
            '    log = []\n'
            '    for text in entries:\n'
            '        head = hashlib.sha256((head + "|" + text).encode()).hexdigest()\n'
            '        log.append((text, head))\n'
            '    return log\n'
            '\n'
            'def verify(log):\n'
            '    head = "GENESIS"\n'
            '    for text, claimed in log:\n'
            '        head = hashlib.sha256((head + "|" + text).encode()).hexdigest()\n'
            '        if head != claimed:\n'
            '            return False, text\n'
            '    return True, ""\n'
            '\n'
            'log = chain(["boot ok", "user ada login", "file read"])\n'
            'print("valid chain:", verify(log)[0], "| links:", len(log))\n'
            'log[1] = ("user root login", log[1][1])\n'
            'print("after edit:", verify(log))\n'
            'print("tamper detected at the edited link")'
        ),
        variant_b='edit the LAST entry instead (how many links break?)',
        variant_c='verify([]) empty log (vacuously True — acceptable or a hole?)',
        mistakes=[
            "Storing the head digest beside the log it anchors (attacker rewrites both consistently).",
            "Forgetting the separator, letting ('ab','c') and ('a','bc') chain identically (ambiguity attack).",
            "Claiming chains prevent tampering — they detect it; prevention needs access control.",
        ],
        qa=(
            ["Why does editing one entry break every later link?",
             "Why does the separator between head and text matter?",
             "What must be protected separately for verification to mean anything?"],
            ["Each link hashes the previous digest, so a changed entry changes its digest, which changes the next link's input, cascading to the head.",
             "Without it, entry boundaries blur: different (head, text) pairs can concatenate identically, letting two histories share one chain.",
             "The head (latest) digest, kept apart from the log — verification recomputes toward it, so a forged log needs a forged anchor too."],
        ),
        homework="Write `chain(entries)` and `verify(log)` with GENESIS anchor and '|' separator, detecting a tampered middle entry. Run it on clean and edited logs, print both verdicts, and comment which value cascades the break.",
        patterns=["def ", "sha256("],
        mapping="Git commits, certificate-transparency logs and blockchains are this chain with signatures and distribution added.",
    ),
}

CRYPTO_PHASES = [
    ("Encodings and Binary",
     "Bytes, text armour, XOR, randomness discipline, and the packaging-vs-protection line.",
     {
         75: dict(
             topic="Orientation: what cryptography is for",
             idea="Cryptography provides four distinct services — confidentiality (only the intended read), integrity (detect changes), authentication (prove origin) and non-repudiation support — and every mechanism in this track serves named ones, never 'security' in general. Encryption without integrity invites tampering; signatures without hashes cannot scale; randomness without discipline repeats. The track's golden rule: name which service each tool provides before using it, because most real breaches come from deploying a confidentiality tool against an integrity problem. Today maps the whole track to these services so every later day lands in a labelled slot. Revisit this map whenever a new tool appears: services first, mechanism second, deployment last. A tool chosen without named services is a guess; guesses fail where threat models would have held. Re-derive the service map for every new feature instead of inheriting yesterday's assumptions blindly. Archive superseded maps with dates so incident reviewers can see what the team believed at the time.",
             code=(
                 'services = {"AES-GCM": ["confidentiality", "integrity"], "SHA-256": ["integrity"], "HMAC": ["integrity", "authentication"], "RSA-sign": ["authentication"]}\n'
                 'need = "send orders unreadably AND detect tampering"\n'
                 'fits = [tool for tool, gives in services.items() if "confidentiality" in gives and "integrity" in gives]\n'
                 'print("need:", need)\n'
                 'print("tools fitting both:", fits)\n'
                 'print("name the services first, then pick the tool")'
             ),
             variant_b='need = "prove who sent it" (which tools fit?)',
             variant_c='need = "detect any change" (which is the cheapest fit?)',
             mistakes=[
                 "Deploying encryption where the threat is tampering (wrong service entirely).",
                 "'Military-grade encryption' cited as if the adjective did the threat modelling.",
                 "Assuming one tool provides all four services because it says 'crypto' on the box.",
             ],
             qa=(
                 ["Which two services does the orders scenario require, and why both?",
                  "Why does encryption alone fail against tampering?",
                  "What is wrong with 'military-grade' as a security argument?"],
                 ["Confidentiality (unreadable to others) plus integrity (tamper-evident): either alone leaves orders readable or forgeable.",
                  "Ciphertext malleability lets attackers flip bits into predictable plaintext changes without reading anything — secrecy is not tamper-evidence.",
                  "It names no threat, service, key size or mode; marketing adjectives are not threat models and prove nothing about fitness."],
             ),
             homework="Write `fit_tools(need_services, catalog)` returning tool names covering all needed services. Run it on two needs, print both matches, and comment which line enforces the AND condition.",
             patterns=["def ", "print("],
             mapping="Every later day opens by naming its services; threat modelling (days 165+) starts from this map.",
         ),
         76: dict(
             topic="Bytes, ints and endianness",
             idea="Binary protocols store numbers as byte sequences, and byte order (endianness) decides what those bytes mean: big-endian reads left-to-right like written numbers, little-endian reverses. Misreading order corrupts lengths, offsets and checksums — the classic cross-platform parsing bug, and occasionally a security boundary (a length read backwards admits oversized input). Python's struct module packs and unpacks with explicit order prefixes (> big, < little), forcing the choice into the open. Rule: every binary parse names its endianness at the format string; 'native order' is a portability and security smell. Write the order prefix even when it matches your machine; the next reader's machine may differ. Parsers that assume native order work until deployment day, then corrupt silently on foreign architectures. Test parsers on both endiannesses in CI so order assumptions break loudly during development. Fuzz parsers with swapped byte orders as well, since real captures arrive in whatever order the sender chose. Reject ambiguous byte orders outright rather than guessing, since guessing wrong corrupts silently. Document the chosen order next to every format string for future readers.",
             code=(
                 'import struct\n'
                 '\n'
                 'value = 1000\n'
                 'big = struct.pack(">H", value)\n'
                 'little = struct.pack("<H", value)\n'
                 'print("big-endian bytes:   ", big.hex())\n'
                 'print("little-endian bytes:", little.hex())\n'
                 'print("misread little-as-big:", struct.unpack(">H", little)[0], "(wrong!)")\n'
                 'print("correct read:        ", struct.unpack("<H", little)[0])'
             ),
             variant_b='value = 1 (which byte carries it in each order?)',
             variant_c='struct.unpack(">H", big[0:1]) truncated (which error, and is failing correct?)',
             mistakes=[
                 "Native-order struct formats that parse differently per machine.",
                 "Truncated reads silently padded instead of raising.",
                 "Length fields trusted before validating against actual buffer size.",
             ],
             qa=(
                 ["Why does misreading endianness corrupt a length field dangerously?",
                  "Why must length fields be validated against the real buffer?",
                  "What does an explicit order prefix buy you?"],
                 ["1000 becomes 59395 when read backwards — a bounds check against the wrong number admits oversized input past the gate.",
                  "A declared length larger than available bytes means over-reads (Heartbleed's shape); validate first, then slice.",
                  "The choice is visible, reviewable and portable instead of silently inheriting whatever machine runs the code."],
             ),
             homework="Write `parse_u16(raw, order)` unpacking two bytes with explicit endianness and raising on short input. Run it on both orders plus truncated input, print all three, and comment which line enforces length.",
             patterns=["struct.pack(", "struct.unpack("],
             mapping="TLS records, certificate fields and file formats all declare endianness; parsers name it in the format string.",
         ),
         77: dict(
             topic="XOR: the atom of stream ciphers",
             idea="XOR (exclusive-or) flips bits where the key has 1s and leaves the rest: applying the same keystream twice restores the original, which is why XOR encrypts and decrypts with one operation. Every stream cipher — from one-time pads to ChaCha20 — is a keystream generator plus XOR; the cipher's entire security lives in the keystream, never in the XOR step. Two rules follow absolutely: keystream bytes must be unpredictable, and must never repeat across messages. Today's demo uses a fixed teaching keystream so output is deterministic; production keystreams come from real primitives, and the difference is everything. Memorise the two keystream laws — unpredictable and never reused — because every stream-cipher failure is one of them broken. Test both laws independently: statistical tests for unpredictability, uniqueness logs for non-reuse across every message ever sent. Nonce registries sound heavy until the first reuse incident proves their worth. Log every nonce alongside its message identifier so duplicates are detectable during routine log review.",
             code=(
                 'def xor_bytes(data: bytes, key: bytes) -> bytes:\n'
                 '    return bytes(b ^ key[i % len(key)] for i, b in enumerate(data))\n'
                 '\n'
                 'keystream = bytes([0x3A, 0x7F, 0xC2, 0x11])\n'
                 'plain = b"attack at dawn"\n'
                 'cipher = xor_bytes(plain, keystream)\n'
                 'print("cipher hex:", cipher.hex())\n'
                 'print("round-trip:", xor_bytes(cipher, keystream) == plain)\n'
                 'print("same operation both directions: XOR symmetry")'
             ),
             variant_b='a one-byte keystream (what pattern leaks into the cipher hex?)',
             variant_c='empty plaintext (does the symmetry hold vacuously?)',
             mistakes=[
                 "Repeating keystreams across messages (two-time pad — day 79 vivisects this).",
                 "Believing XOR itself provides security rather than the keystream's secrecy.",
                 "XOR-ing str instead of bytes and meeting TypeError in production.",
             ],
             qa=(
                 ["Why does applying the same keystream twice restore the plaintext?",
                  "Where does this construction's security actually live?",
                  "Why is a fixed teaching keystream acceptable here but never in production?"],
                 ["XOR is its own inverse per bit (b^k^k = b), so the second pass undoes the first exactly.",
                  "Entirely in the keystream's unpredictability and non-reuse; the XOR step is public, trivial and contributes zero secrecy.",
                  "Determinism lets outputs be verified and idempotent; production needs unpredictability, which fixed bytes cannot provide."],
             ),
             homework="Write `xor_bytes(data, key)` cycling the key and returning bytes. Run it on two plaintexts, verify both round-trips, print results, and comment which expression cycles the key.",
             patterns=["def ", "return"],
             mapping="ChaCha20 Kasumi and one-time pads are keystream+XOR at scale; days 78–79 attack the two ways keystreams fail.",
         ),
         78: dict(
             topic="One-time pads: perfect and impractical",
             idea="A keystream that is truly random, as long as the message, and never reused gives perfect secrecy: the ciphertext is statistically independent of the plaintext, provably, against unbounded adversaries. The catch is key distribution — securely delivering a key as long as every message costs exactly as much as delivering the messages secretly in the first place. One-time pads therefore survive in niches (diplomatic hotlines, extreme threat models) while the world uses stream ciphers that stretch short keys into long keystreams. Understanding the pad sets the standard every practical cipher is measured against; 'as secure as OTP except for key reuse' describes precisely nothing deployed. Real systems approximate pads with stream ciphers stretching short keys; the approximation is the entire engineering discipline. Stream ciphers stretch short keys with public algorithms; the key stays secret while the method stays open. Kerckhoffs demands open algorithms with secret keys only, never secret algorithms with hopeful obscurity.",
             code=(
                 'import hashlib\n'
                 '\n'
                 'def otp_encrypt(plain: bytes, pad: bytes) -> bytes:\n'
                 '    assert len(pad) >= len(plain), "pad must cover the message"\n'
                 '    return bytes(b ^ p for b, p in zip(plain, pad))\n'
                 '\n'
                 'pad = hashlib.sha256(b"fixed-demo-pad").digest()\n'
                 'c1 = otp_encrypt(b"yes, launch", pad)\n'
                 'c2 = otp_encrypt(b"no, hold...", pad[:11])\n'
                 'print("ciphertexts differ fully:", c1.hex()[:16], "vs", c2.hex()[:16])\n'
                 'print("brute force learns nothing: every plaintext stays possible")'
             ),
             variant_b='pad one byte short (which assert fires, and why is the rule absolute?)',
             variant_c='same pad encrypting twice (harmless here — catastrophic in production; why the difference?)',
             mistakes=[
                 "Reusing pads 'just for testing' and shipping the test code.",
                 "Generating pads with random instead of secrets (deterministic pads, decorative secrecy).",
                 "Believing pad-ciphertext indistinguishability survives pad reuse.",
             ],
             qa=(
                 ["Why is a fresh random pad perfectly secret?",
                  "Why does the key-distribution cost kill the pad in practice?",
                  "Why is the pad-length assert absolute rather than advisory?"],
                 ["Every ciphertext is equally consistent with every plaintext (pad = cipher XOR guess), so observation teaches literally nothing.",
                  "Secure pad delivery costs as much as secure message delivery — the pad moves the secrecy problem without shrinking it.",
                  "Short pads force reuse or truncation, both of which collapse perfect secrecy immediately; the assert makes the rule structural."],
             ),
             homework="Write `otp_encrypt(plain, pad)` with a length assert, encrypting two messages under one demo pad. Print both hex outputs, verify one round-trip, and comment which line enforces coverage.",
             patterns=["assert ", "def "],
             mapping="Stream ciphers approximate pads by stretching short keys; key reuse converts both into two-time-pad failures (day 79).",
         ),
         79: dict(
             topic="Two-time pad: reuse kills",
             idea="Encrypt two messages under one keystream and XOR the ciphertexts: the keystream cancels, leaving plaintext-XOR-plaintext — and natural language XORed with itself leaks both messages to crib-dragging (guessing ' the ' at each position and reading what the other message must contain there). This is not theoretical: reused nonces broke real systems (WEP's IV reuse, the 2012 PlayStation ECDSA nonce failure pattern). The demo drags the crib ' the ' across the XOR and recovers readable fragments, proving keystream reuse is total compromise, not partial weakening. Nonce means number-used-once; the name is the entire rule.",
             code=(
                 'def xor_bytes(data: bytes, key: bytes) -> bytes:\n'
                 '    return bytes(b ^ key[i % len(key)] for i, b in enumerate(data))\n'
                 '\n'
                 'keystream = bytes([0x3A, 0x7F, 0xC2, 0x11, 0x55, 0x08, 0x9E, 0xD0, 0x41, 0x22, 0x77, 0xB4, 0x0C, 0xF1])\n'
                 'm1 = b"attack at dawn"\n'
                 'm2 = b"retreat at dusk!"\n'
                 'c1, c2 = xor_bytes(m1, keystream), xor_bytes(m2, keystream)\n'
                 'combined = bytes(a ^ b for a, b in zip(c1, c2))\n'
                 'crib = b" the "\n'
                 'print("dragging crib", crib, "across m1^m2:")\n'
                 'for pos in range(len(combined) - len(crib) + 1):\n'
                 '    frag = bytes(combined[pos + i] ^ crib[i] for i in range(len(crib)))\n'
                 '    try:\n'
                 '        print(f"  pos {pos}: {frag.decode()}")\n'
                 '    except UnicodeDecodeError:\n'
                 '        print(f"  pos {pos}: (non-text)")'
             ),
             variant_b='crib b"and" (shorter cribs, noisier fragments — why?)',
             variant_c='m2 = b"xxxxxxxxxxxxxxxx" (what does structureless plaintext leak?)',
             mistakes=[
                 "Reusing IVs/nonces across messages 'because random rarely collides' without counting birthday odds.",
                 "Assuming partial reuse is partial damage — any reuse leaks plaintext relationships.",
                 "ECB mode chosen for 'simplicity', which is deterministic reuse by design (day 107).",
             ],
             qa=(
                 ["Why does XOR-ing two ciphertexts cancel the keystream?",
                  "How does crib-dragging turn m1^m2 into readable text?",
                  "Why is a repeated nonce a total break rather than a weakness?"],
                 ["c1^c2 = (m1^k)^(m2^k) = m1^m2 — the keystream appears twice and XOR self-cancels.",
                  "Guessing a likely phrase at each position XORs it out of the mix, exposing the other message's bytes there; readable fragments confirm the guess.",
                 "It converts ciphertext-only secrecy into a language puzzle solvable with patience — the keystream's protection drops to zero wherever cribs fit."],
             ),
             homework="Write `crib_drag(c1, c2, crib)` returning readable fragments with positions. Run it on two same-keystream ciphertexts with two cribs, print both fragment lists, and comment which line cancels the keystream.",
             patterns=["def ", "return"],
             mapping="WEP IV reuse, nonce-misuse breakages, ECB determinism — one rule violated three famous ways; AES-GCM fails catastrophically on nonce reuse too.",
         ),
         80: dict(
             topic="Randomness you can stake secrets on",
             idea="Security randomness must be unpredictable to a determined observer: secrets.token_bytes for keys and nonces, secrets.token_urlsafe for tokens in text channels, secrets.choice over explicit alphabets for passwords. The random module is for simulations — Mersenne Twister state leaks from outputs, letting observers predict everything after. Test randomness by properties, never by eye: lengths exact, types bytes, uniqueness across draws (birthday-checked), and statistical flatness on large samples. Never log raw secrets; today's demo prints lengths and a hash prefix only, proving generation worked while exposing nothing an attacker could use. Rotate logged prefixes per deployment so leaked logs cannot be correlated across systems by their identifiers. Prefixes identify which token was used for debugging; they must never suffice to forge or replay it. Bind tokens to purpose and expiry so a leaked prefix buys an attacker neither validity nor time.",
             code=(
                 'import secrets\n'
                 'import hashlib\n'
                 '\n'
                 'key = secrets.token_bytes(32)\n'
                 'print("key length:", len(key), "bytes =", len(key) * 8, "bits")\n'
                 'demo_logged = hashlib.sha256(b"demo-key-for-prefix-illustration").hexdigest()[:12]\n'
                 'print("safe to log: sha256 prefix", demo_logged, "(fixed demo key; real prefixes come from live keys)")\n'
                 'assert len(key) == 32 and isinstance(key, bytes)\n'
                 'alphabet = "abcdefghijkmnopqrstuvwxyz23456789"\n'
                 'pw = "".join(secrets.choice(alphabet) for _ in range(12))\n'
                 'print("password length:", len(pw), "| alphabet:", len(alphabet), "symbols")'
             ),
             variant_b='token_bytes(16) vs 32 (how does guessing work scale per byte?)',
             variant_c='random.Random(0).randbytes(32) twice (identical outputs — why disqualifying?)',
             mistakes=[
                 "random module for keys, tokens or nonces (reproducible 'randomness').",
                 "Logging raw secrets for debugging, then shipping the logs.",
                 "time.time() or PIDs as entropy sources (guessable to nearby observers).",
             ],
             qa=(
                 ["Why is random.Random(0) output disqualifying for secrets?",
                  "Why log a hash prefix instead of the token?",
                  "Why does alphabet size matter as much as password length?"],
                 ["Seeded PRNG output is fully determined by the seed — anyone learning it predicts every 'random' value ever generated.",
                  "The prefix identifies which token was used without exposing it; preimage resistance keeps the token itself unrecoverable from the log.",
                  "Guessing work is alphabet^length — doubling length squares work per symbol-set size, so small alphabets need compensating length."],
             ),
             homework="Write `make_token(n)` returning secrets.token_bytes(n) after asserting n>=16, printing only length. Run it for n=16/32, print both lengths, and comment which line bans tiny tokens.",
             patterns=["token_bytes(", "assert "],
             mapping="Session IDs, API keys, nonces and salts all come from secrets; days 119 and 155 audit real token handling.",
         ),
         81: dict(
             topic="Checksums are not hashes",
             idea="CRCs detect accidents: burst errors from noisy channels, flipped bits in storage. Attackers are not accidents — small checksum spaces fall to brute-force padding search in milliseconds, and full CRC32 falls to linear algebra barely slower, so anyone can forge data matching any checksum while SHA-256 refuses the same trick at any feasible cost. The demo forges an 8-bit checksum live (padding length walks residues until one matches — guaranteed, instant), then shows SHA-256 differing on the forgery. Rule: CRC/adler32 for corruption, cryptographic hashes for adversaries; any integrity claim against an intelligent opponent needs preimage and collision resistance, which checksums never had. Mislabelled 'integrity checks' built on CRCs are vulnerability reports waiting for their CVE numbers.",
             code=(
                 'import hashlib\n'
                 '\n'
                 'def checksum8(data: bytes) -> int:\n'
                 '    return sum(data) % 256\n'
                 '\n'
                 'good = b"transfer $100 to ada"\n'
                 'evil = b"transfer $900 to ada"\n'
                 'print("checksum good:", checksum8(good))\n'
                 'print("checksum evil:", checksum8(evil), "(differs — so far so good)")\n'
                 'pad = 0\n'
                 'while True:\n'
                 '    cand = evil + b"#" * pad\n'
                 '    if checksum8(cand) == checksum8(good):\n'
                 '        break\n'
                 '    pad += 1\n'
                 '    assert pad < 1000, "8-bit padding search must converge fast"\n'
                 'print("forged padding of", pad, "bytes: checksum matches, meaning intact — LIE")\n'
                 'print("sha256 differs:", hashlib.sha256(good).hexdigest()[:16], "vs", hashlib.sha256(cand).hexdigest()[:16])'
             ),
             variant_b='a 12-bit checksum (how do try-counts scale with bits?)',
             variant_c='forging to match evil instead of good (direction never matters — why?)',
             mistakes=[
                 "CRC 'integrity' on downloads facing hostile mirrors.",
                 "Short checksums where brute-force forging is trivial arithmetic.",
                 "Confusing error detection (accidents) with tamper evidence (adversaries).",
             ],
             qa=(
                 ["Why can anyone forge a small checksum in milliseconds?",
                  "Why doesn't the same trick work against SHA-256?",
                  "When is a checksum the right tool?"],
                 ["Small spaces fall to padding search that converges instantly (35 and 256 are coprime, so padding lengths walk every residue); full CRC32 falls to linear algebra barely slower — no brute-force lottery involved.",
                  "No exploitable structure: each try is an independent 1-in-2^256 lottery, and brute force at that scale outlives stars.",
                  "Accidental corruption on trusted channels (storage, noisy links) where the opponent is physics, not intelligence."],
             ),
             homework="Write `forge_sum(target, base)` appending '#' bytes until a mod-256 checksum matches, returning pad length and tries. Run it on two targets, print both try-counts, and comment why the loop always terminates fast.",
             patterns=["while ", "def "],
             mapping="Checksums guard files in transit on trusted paths; every adversarial integrity claim ahead uses SHA-256 or HMAC.",
         ),
         82: dict(
             topic="Timing attacks on comparisons",
             idea="Naive == exits at the first mismatch, so correct-prefix guesses take measurably longer — over thousands of timed probes, statistics recover secrets byte-by-byte without ever seeing them. The demo simulates the oracle honestly: a fake timer reporting comparison steps shows matching prefixes costing more steps, which is exactly the signal real attackers amplify with averaging. Defence is constant-time comparison (hmac.compare_digest, day 11's rule) plus rate-limiting and request padding that deny the sample counts statistics need. Any secret comparison without compare_digest is a timing oracle awaiting its statistician. Pair constant-time comparison with rate limiting: remove the signal and starve the samples, defence in depth. Add random delays and request padding where oracles matter most: login, token validation, decryption. Uniform response sizes matter too, since length differences leak through the same statistics. Pad responses to uniform sizes wherever secrets influence length, closing the cheaper cousin of the timing leak.",
             code=(
                 'def steps_to_compare(guess: bytes, secret: bytes) -> int:\n'
                 '    steps = 0\n'
                 '    for g, s in zip(guess, secret):\n'
                 '        steps += 1\n'
                 '        if g != s:\n'
                 '            break\n'
                 '    return steps\n'
                 '\n'
                 'secret = b"token-7x9q"\n'
                 'for guess in (b"token-7x9q", b"token-7x9!", b"XXXX-XXXXX", b"tXXXXXXXXX"):\n'
                 '    print(f"{guess!r}: {steps_to_compare(guess, secret)} steps")\n'
                 'print("longer match = more steps = the leak, measured")'
             ),
             variant_b='all-wrong vs half-right guesses (how many steps apart?)',
             variant_c='different-length guess (where does zip stop, and what second leak is that?)',
             mistakes=[
                 "== on HMAC tags, session tokens or password hashes.",
                 "Assuming network jitter saves you (statistics eat jitter for breakfast).",
                 "Length checks before compare_digest that leak length first (compare lengths is fine — lengths of fixed digests are public).",
             ],
             qa=(
                 ["How do step counts become secret bytes?",
                  "Why doesn't network jitter defeat timing attacks?",
                  "What two defences combine against oracles?"],
                 ["Longer matches cost more steps, so timing ranks guesses by prefix correctness — hill-climb each byte position in turn and the secret falls.",
                  "Jitter is zero-mean noise; averaging thousands of probes shrinks it while the signal (prefix-dependent steps) persists.",
                  "Constant-time comparison removes the signal; rate-limiting plus response padding starves the sample counts statistics needs."],
             ),
             homework="Write `steps_to_compare(guess, secret)` simulating short-circuit steps. Run it on full/partial/zero matches, print all three counts, and comment which line is the leak.",
             patterns=["def ", "return"],
             mapping="hmac.compare_digest everywhere secrets compare; login throttling and uniform response times starve oracle sample counts.",
         ),
         83: dict(
             topic="Reading hex dumps like a local",
             idea="Hex dumps are where ciphertext, hashes and packet captures meet human eyes: offsets, hex bytes, ASCII gutter. Reading them means spotting structure — repeated blocks (ECB's tell, day 107), ASCII hiding in binary, length fields, magic numbers (file-type sniffing). The demo prints a canonical dump of a short ciphertext and walks it: offset, sixteen bytes in hex, printable gutter. Practice until dumps feel like text, because incident response, forensics and protocol debugging all hand you dumps when tools run out. Fluency here pays rent across the entire track. Practice until offsets, lengths and gutters read as naturally as source code. Offsets locate structures, hex states exact values, and the gutter only ever hints at embedded text. Confirm gutter suspicions against hex before acting, because dots hide distinct bytes routinely. Train analysts to distrust the gutter on principle and to cite offsets and hex values in every incident note. Screenshots of dumps without offsets waste the next analyst's time reconstructing positions.",
             code=(
                 'data = bytes.fromhex("53656372657421313233898081889c8d")\n'
                 '\n'
                 'def hexdump(data: bytes) -> list:\n'
                 '    lines = []\n'
                 '    for off in range(0, len(data), 16):\n'
                 '        chunk = data[off:off + 16]\n'
                 '        gutter = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)\n'
                 '        lines.append(f"{off:08x}  {chunk.hex()}  |{gutter}|")\n'
                 '    return lines\n'
                 '\n'
                 'for line in hexdump(data):\n'
                 '    print(line)\n'
                 'print("offsets, bytes, gutter: the three columns of fluency")'
             ),
             variant_b='b"Secret!123" + b"\\x00" * 8 (what do null gutters look like?)',
             variant_c='empty input (how many lines, and is zero correct?)',
             mistakes=[
                 "Reading hex as decimal (0x10 is sixteen, not ten).",
                 "Ignoring offsets and misaligning multi-line structures.",
                 "Trusting the gutter on non-ASCII bytes instead of the hex.",
             ],
             qa=(
                 ["What does each of the three dump columns tell you?",
                  "Why is the gutter untrustworthy for binary data?",
                  "What would repeated 16-byte blocks in a dump suggest?"],
                 ["Offsets locate, hex states exact values, gutter hints at embedded text — structure, truth and convenience respectively.",
                  "Non-printables render as dots, so distinct bytes look identical; only hex distinguishes them.",
                  "Deterministic block encryption (ECB) — identical plaintext blocks, identical ciphertext blocks, visible pattern (day 107's tell)."],
             ),
             homework="Write `hexdump(data)` returning offset/hex/gutter lines. Run it on two byte strings, print both dumps, and comment which column carries ground truth.",
             patterns=["def ", ".hex()"],
             mapping="Wireshark hex panes, forensic dumps and hash comparisons all read this way; ECB-spotting starts here.",
         ),
         84: dict(
             topic="ASCII armour in protocols",
             idea="Protocols armour binary as text for transport: PEM wraps base64 with BEGIN/END lines, JWT dot-joins three base64url parts, HTTP Basic encodes credentials (without encrypting — armour, not armour-plating). Parsing armour means stripping wrappers, validating alphabet, then decoding strictly — each layer with its own error, because 'invalid armour' and 'valid armour, hostile content' demand different responses. The demo parses a toy PEM block, catching wrapper errors separately from decode errors. Respect the layering: transport packaging tells you nothing about the content's trustworthiness, and conflating the two is how wrapped malware strolls past naive filters. Log wrapper and payload verdicts separately so incidents distinguish transport problems from content threats. A valid wrapper around hostile bytes is the normal case for malware delivery, not an edge. Content checks must assume valid armour always, since attackers package hostile payloads correctly on purpose.",
             code=(
                 'import base64\n'
                 'import binascii\n'
                 '\n'
                 'PEM = "-----BEGIN DEMO-----\\nSGVsbG8=\\n-----END DEMO-----\\n"\n'
                 '\n'
                 'def parse_pem(text: str):\n'
                 '    lines = text.strip().split("\\n")\n'
                 '    if len(lines) != 3 or not lines[0].startswith("-----BEGIN") or not lines[2].startswith("-----END"):\n'
                 '        return None, "bad wrapper"\n'
                 '    try:\n'
                 '        raw = base64.b64decode(lines[1], validate=True)\n'
                 '    except (binascii.Error, ValueError):\n'
                 '        return None, "bad payload"\n'
                 '    return raw, "ok"\n'
                 '\n'
                 'print(parse_pem(PEM))\n'
                 'print(parse_pem("no armour at all"))\n'
                 'print(parse_pem("-----BEGIN DEMO-----\\n!!!\\n-----END DEMO-----"))\n'
                 'print("wrapper vs payload: different errors, different responses")'
             ),
             variant_b='missing END line (which error fires?)',
             variant_c='valid wrapper, valid base64 of hostile bytes (why must parsing still distrust content?)',
             mistakes=[
                 "Treating successful decode as validation of content.",
                 "One catch-all error hiding whether armour or payload failed.",
                 "Base64-decoding without validate=True, silently skipping hostile bytes.",
             ],
             qa=(
                 ["Why distinguish wrapper errors from payload errors?",
                  "Why must parsing still distrust successfully decoded content?",
                  "What does validate=True buy over lenient decoding?"],
                 ["They demand different responses: bad armour is a transport problem, while valid armour around hostile content is a content problem needing deeper checks.",
                  "Armour describes transport packaging, never trustworthiness — wrapped hostile bytes decode fine and must face content checks next.",
                  "It rejects non-alphabet bytes outright instead of skipping them silently, so hostile bytes cannot hide inside 'decoded' output."],
             ),
             homework="Write `parse_pem(text)` returning (bytes, reason) with separate wrapper/payload verdicts. Run it on three inputs, print all verdicts, and comment which check validates the alphabet.",
             patterns=["b64decode(", "def "],
             mapping="PEM certificates, JWT parts and Basic-auth headers parse in exactly these layers (days 135+ read real-shaped ones).",
         ),
         85: dict(
             topic="Binary record parsing",
             idea="Length-prefixed records — two-byte length, then payload — are the wire format of countless protocols, and parsing them safely means bounds-checking every slice: length within remaining bytes, total within message, recursion capped. The demo parses a two-record message, rejecting truncated tails and absurd lengths before slicing. Every famous buffer over-read (Heartbleed's shape: trusted length, missing buffer) is this check omitted. Parse defensively: read the length, prove it fits, then slice — never slice on a promise. Cap total record counts as well as lengths; a million tiny valid records exhausts memory like one giant one. Set both ceilings from the protocol's documented maxima, never from observed traffic averages. Documented maxima come from specifications, while averages describe only the traffic seen so far. Revisit ceilings after protocol updates because new versions change maxima that old limits no longer cover.",
             code=(
                 'import struct\n'
                 '\n'
                 'MSG = struct.pack(">H", 5) + b"hello" + struct.pack(">H", 3) + b"bye"\n'
                 '\n'
                 'def parse_records(raw: bytes):\n'
                 '    out, pos = [], 0\n'
                 '    while pos < len(raw):\n'
                 '        if len(raw) - pos < 2:\n'
                 '            return None, "truncated length"\n'
                 '        (length,) = struct.unpack(">H", raw[pos:pos + 2])\n'
                 '        if length > len(raw) - pos - 2:\n'
                 '            return None, "length exceeds buffer"\n'
                 '        out.append(raw[pos + 2:pos + 2 + length])\n'
                 '        pos += 2 + length\n'
                 '    return out, "ok"\n'
                 '\n'
                 'print(parse_records(MSG))\n'
                 'print(parse_records(MSG[:-2]))\n'
                 'print(parse_records(struct.pack(">H", 999) + b"hi"))\n'
                 'print("lengths are claims; buffers are facts")'
             ),
             variant_b='a zero-length record (valid or hole? decide and defend)',
             variant_c='length exactly to the end (boundary: accept or reject?)',
             mistakes=[
                 "Trusting declared lengths without buffer checks (Heartbleed's shape).",
                 "Uncapped loops on attacker-controlled counts (billion-laughs-shaped thinking).",
                 "Partial reads treated as complete records downstream.",
             ],
             qa=(
                 ["Why check length against the buffer before slicing?",
                  "What made Heartbleed a missing-check bug rather than a crypto bug?",
                  "Why cap total records as well as each length?"],
                 ["Declared lengths are attacker-controlled claims; slicing on an unchecked claim over-reads into adjacent memory or crashes.",
                  "The TLS heartbeat trusted the peer's length field and echoed memory past the real payload — bounds-checking, not mathematics, was missing.",
                  "A million tiny valid records exhaust memory just as one giant record would; both dimensions need ceilings."],
             ),
             homework="Write `parse_records(raw)` returning (records, reason) with both bounds checks. Run it on valid/truncated/absurd inputs, print all three, and comment which line blocks the over-read.",
             patterns=["struct.unpack(", "def "],
             mapping="TLS records, certificate parsing and file-format readers all prove lengths against buffers before slicing.",
         ),
         86: dict(
             topic="Entropy: measuring randomness",
             idea="Entropy counts unpredictability in bits: uniform random bytes carry ~8 bits per byte, English text about 1–2, and a constant string carries zero. Estimating entropy distinguishes encrypted traffic (flat, ~8) from plaintext protocols (structured, low) — the first step of traffic analysis — and audits generators (a 'random' token at 3 bits/byte is broken). The demo counts byte frequencies over samples and reports a Shannon estimate, showing English versus token bytes side by side. Limits stated: short samples mislead, and high entropy proves unpredictability, never security — a compressed zip is high-entropy and fully reversible. Test generators by next-byte unpredictability, not by single-sample flatness; a counter passes flatness and fails everything else. The decisive test is always next-byte unpredictability given all previous bytes, not distribution shape. Sample generously before judging flatness, since short samples mislead in both directions equally.",
             code=(
                 'import math\n'
                 'import secrets\n'
                 '\n'
                 'def entropy(data: bytes) -> float:\n'
                 '    if not data:\n'
                 '        return 0.0\n'
                 '    freq = {}\n'
                 '    for b in data:\n'
                 '        freq[b] = freq.get(b, 0) + 1\n'
                 '    return -sum((c / len(data)) * math.log2(c / len(data)) for c in freq.values())\n'
                 '\n'
                 'text = b"the quick brown fox jumps over the lazy dog " * 20\n'
                 'print("english bits/byte:", round(entropy(text), 2))\n'
                 'print("uniform bytes bits/byte:", round(entropy(bytes(range(256))), 2))\n'
                 'print("flat ~8 = unpredictable shape; english lower = analysable")'
             ),
             variant_b='b"a" * 500 (zero entropy — what does certainty look like?)',
             variant_c='256 bytes 0..255 each once (maximum entropy without randomness — why?)',
             mistakes=[
                 "Judging entropy from a dozen bytes, where noise dominates.",
                 "Equating high entropy with security (compressed data is high-entropy and public).",
                 "Testing the generator once instead of continuously in production.",
             ],
             qa=(
                 ["Why does English score ~4 bits/byte while tokens score ~8?",
                  "Why can maximum entropy exist without any randomness?",
                  "What does a flat distribution prove, and what doesn't it prove?"],
                 ["Language is redundant — letter frequencies and patterns make most bytes predictable; token bytes are uniform, so each carries full surprise.",
                  "The 0–255 sequence uses every value equally: entropy measures distribution flatness, and a counter is flat without being unpredictable.",
                  "It proves unpredictability from samples, never the generator's quality — a counter passes once and fails the 'next byte' test forever."],
             ),
             homework="Write `entropy(data)` returning Shannon bits/byte with empty-input guard. Run it on English text and token bytes, print both, and comment why short samples mislead.",
             patterns=["def ", "math.log2("],
             mapping="Traffic classifiers separate encrypted from plaintext flows by entropy; RNG health monitors track it continuously.",
         ),
         87: dict(
             topic="Project: hexdump file sniffer",
             idea="Today's project sniffs file types from magic numbers: read the first bytes of a buffer, match against known signatures (PDF %PDF, PNG's 8-byte mark, ZIP's PK), and report type plus confidence — exact match, no match, or truncated input. Unknown buffers report 'unknown', never a guess, and short buffers report 'truncated' rather than misreading. This is allowlist thinking applied to formats: recognise the known, refuse the rest. Extension to real files is one open() away, but the decision logic — the security-relevant part — is complete and tested here on synthetic buffers. Extending to real files changes only the reading step; the verdict logic — recognise, refuse, or flag truncated — stays identical. Unknown buffers route to quarantine for deeper inspection, never to execution. Unknown verdicts expire from quarantine on a schedule so storage costs stay bounded and reviews stay current. Bound quarantine storage as well, since unbounded retention turns a safety mechanism into a data liability over time.",
             code=(
                 'SIGS = [(b"%PDF", "PDF document"), (bytes([0x89, 0x50, 0x4E, 0x47]), "PNG image"), (b"PK", "ZIP archive")]\n'
                 '\n'
                 'def sniff(data: bytes):\n'
                 '    if len(data) < 4:\n'
                 '        return "truncated"\n'
                 '    for magic, label in SIGS:\n'
                 '        if data.startswith(magic):\n'
                 '            return label\n'
                 '    return "unknown"\n'
                 '\n'
                 'print(sniff(b"%PDF-1.7 rest..."))\n'
                 'print(sniff(bytes([0x89, 0x50, 0x4E, 0x47, 0x0D])))\n'
                 'print(sniff(b"MZ..."))\n'
                 'print(sniff(b"ab"))\n'
                 'print("known recognised, rest refused: allowlist discipline")'
             ),
             variant_b='a ZIP with extra leading junk (should position-zero matching accept it?)',
             variant_c='empty input (which verdict, and why not unknown?)',
             mistakes=[
                 "Sniffing by extension instead of content (the whole attack).",
                 "Guessing on unknown buffers instead of reporting unknown.",
                 "Truncated input misclassified instead of flagged.",
             ],
             qa=(
                 ["Why match content instead of trusting the extension?",
                  "Why is 'unknown' safer than a best guess?",
                  "Why does truncation get its own verdict?"],
                 ["Extensions are attacker-controlled labels; magic bytes describe actual content — uploads lie about names routinely.",
                  "Guesses execute: a misclassified binary opened as a document is how parsers get exploited; unknown routes to quarantine instead.",
                  "Truncated input is a distinct state (more data may decide it) while unknown is decided; conflating them misroutes both."],
             ),
             homework="Write `sniff(data)` with truncated/known/unknown verdicts over three magic signatures. Run it on four buffers, print all verdicts, and comment which branch refuses to guess.",
             patterns=["def ", ".startswith("],
             mapping="Upload validators, forensic triage and email gateways sniff content exactly this way before deeper parsing.",
         ),
         88: dict(
             topic="Testing crypto helpers with asserts",
             idea="Crypto test discipline: round-trips (encode→decode identity), determinism (same input, same digest, twice), avalanche smoke (one-bit change moves many hex chars), length contracts (64 hex for SHA-256, 16+ byte nonces), and refusal cases (malformed input returns None, never raises through the API). Assert contracts, never digests — hardcoded digests fossilise one input while contracts guard every input. These five asserts around every helper cost a minute and catch the class where everything runs and everything is wrong: swapped encode/decode order, truncated digests, mixed str/bytes. Untested crypto helpers are decorations, not controls. Test refusal paths with the same rigour as happy paths; attackers live in the paths your tests never visit. Malformed inputs deserve first-class test cases with exact expected verdicts, not ad-hoc manual poking. Automate the malformed corpus in CI so every future parser change replays the same adversarial gauntlet. A corpus that grows with every incident is institutional memory that never forgets. Fuzz every parser with malformed, truncated and oversized inputs as a standing test-suite habit. Include empty, single byte and maximum size cases in every parser test plan without exception.",
             code=(
                 'import hashlib\n'
                 'import base64\n'
                 'import secrets\n'
                 '\n'
                 'def fingerprint(data: bytes) -> str:\n'
                 '    assert isinstance(data, bytes)\n'
                 '    return hashlib.sha256(data).hexdigest()\n'
                 '\n'
                 'assert fingerprint(b"x") == fingerprint(b"x")\n'
                 'assert len(fingerprint(b"x")) == 64\n'
                 'assert base64.b64decode(base64.b64encode(b"probe")) == b"probe"\n'
                 'assert len(secrets.token_bytes(16)) == 16\n'
                 'print("contracts hold: determinism, lengths, round-trips, sizes")'
             ),
             variant_b='fingerprint("x") str input (which assert fires first?)',
             variant_c='token_bytes(8) (which policy assert should fire, and does one exist?)',
             mistakes=[
                 "Hardcoded digest asserts that fossilise one input.",
                 "No refusal-case tests, so malformed paths rot unnoticed.",
                 "Asserts only on happy paths, never on adversarial inputs.",
             ],
             qa=(
                 ["Why assert contracts instead of exact digest values?",
                  "Which refusal cases must crypto helpers test?",
                  "Why test adversarial inputs, not just happy paths?"],
                 ["Contracts hold across all inputs while values fossilise one case; a helper passing contracts is guarded everywhere it will ever run.",
                  "Malformed encodings, wrong types, empty inputs and undersized parameters — every calm-None or loud-assert path needs a test proving it.",
                  "Happy paths prove the helper works; adversarial inputs prove it fails safely, and in security code the failure mode is the product."],
             ),
             homework="Write `checked` versions of fingerprint plus round-trip asserts for base64. Run them on two inputs, print the verdicts, and comment which assert guards types.",
             patterns=["assert ", "sha256("],
             mapping="Contract asserts (lengths, types, round-trips, refusals) wrap every crypto helper hereafter.",
         ),
         89: dict(
             topic="Phase review: encodings and binary",
             idea="Rebuild from memory: services named before tools, explicit endianness, XOR symmetry with keystream discipline, OTP perfection versus key-distribution cost, two-time-pad cribs, secrets-only randomness, checksums for accidents and hashes for adversaries, timing oracles closed by compare_digest, hex-dump fluency, layered armour parsing, bounds-checked records, entropy as flatness. Close the notes and reproduce the XOR round-trip plus the CRC-forge demo — packaging versus protection stated aloud. The missing line is tomorrow's first job; hashes (phase 2) build directly on bytes, armour and discipline. If the rebuild flows, binary thinking is installed. If any rebuild step stalls, it names the exact day to revisit — failed retrieval is a precise diagnostic, not a vague feeling. Each rebuilt line proves a habit; each missing line schedules exactly one review task. Work that list before advancing, since gaps compound silently when carried forward. Schedule review tasks with dates and owners so missing knowledge gets repaired instead of merely noted. Review the outstanding list weekly until it empties, then start the next phase with a clean slate.",
             code=(
                 'import hashlib\n'
                 'import binascii\n'
                 '\n'
                 'def xor_bytes(data: bytes, key: bytes) -> bytes:\n'
                 '    return bytes(b ^ key[i % len(key)] for i, b in enumerate(data))\n'
                 '\n'
                 'msg = b"review time"\n'
                 'key = bytes([0x3A, 0x7F])\n'
                 'assert xor_bytes(xor_bytes(msg, key), key) == msg\n'
                 'print("xor round-trip: proven from memory")\n'
                 'print("crc32:", hex(binascii.crc32(msg)))\n'
                 'print("sha256:", hashlib.sha256(msg).hexdigest()[:16], "... (adversary-grade)")'
             ),
             variant_b='a 1-byte message (do all three primitives behave?)',
             variant_c='empty message (which primitives stay meaningful?)',
             mistakes=[
                 "Rebuilding with notes open — retrieval is the learning.",
                 "Reciting XOR without placing it in a running round-trip.",
                 "Calling CRC 'integrity' in the rebuild after a phase proving otherwise.",
             ],
             qa=(
                 ["What single rebuild proves this phase stuck?",
                  "Why must the rebuild include the CRC-forge contrast, not just XOR?",
                  "What does a failed rebuild locate?"],
                 ["XOR round-trip plus CRC-forge contrast from memory — symmetry demonstrated, packaging-vs-protection stated, no notes.",
                  "XOR alone could be mistaken for protection; the forge proves packaging grades differ, which is the phase's central distinction.",
                  "The exact missing line is tomorrow's first job — failed retrieval marks the gap precisely, unlike re-reading which marks nothing."],
             ),
             homework="Write `phase_recap()` from memory: XOR round-trip assert plus CRC-vs-SHA256 contrast printed. Run it, print the verdict, and comment which line you had to look up.",
             patterns=["def ", "sha256("],
             mapping="Phase 2 keeps bytes and discipline; hashes add one-way functions to the toolbox.",
         ),
     }),
    ("Hashes and Integrity",
     "One-way fingerprints: properties, HMAC, chains, salting, and the broken algorithms of history.",
     {
         90: dict(
             topic="SHA-256 in depth",
             idea="SHA-256 compresses arbitrary input into 256 bits through 64 rounds of mixing where every output bit depends on every input bit — the avalanche that makes digests unpredictable. Its three security properties each defeat a different attacker: preimage resistance (given a digest, finding any input is 2^256 work), second-preimage resistance (given one input, finding another with the same digest is equally hard), and collision resistance (finding any pair sharing a digest costs 2^128 by birthdays). Demos verify determinism, avalanche magnitude and fixed length; the numbers are not trivia but the exact work factors adversaries face. SHA-256 is the default fingerprint for everything ahead precisely because all three properties still hold. Revisit this choice if cryptanalysis ever narrows the margins; defaults deserve scheduled re-examination, not permanent trust. Track cryptanalysis news as maintenance input; margins only ever shrink, never grow.",
             code=(
                 'import hashlib\n'
                 '\n'
                 'a = hashlib.sha256(b"attack at dawn").hexdigest()\n'
                 'b = hashlib.sha256(b"attack at dawn").hexdigest()\n'
                 'c = hashlib.sha256(b"attack at dusk").hexdigest()\n'
                 'moved = sum(1 for x, y in zip(a, c) if x != y)\n'
                 'print("deterministic:", a == b)\n'
                 'print("hex chars:", len(a), "| bits:", len(a) * 4)\n'
                 'print("one-letter change moves", moved, "of 64 hex chars")\n'
                 'print("preimage 2^256, collision 2^128: infeasible, both")'
             ),
             variant_b='b"" empty input (is the empty digest well-defined and useful?)',
             variant_c='a 1MB input of "a" (does length change cost or output size?)',
             mistakes=[
                 "Truncating digests for display and comparing truncations as if full-strength.",
                 "'Upgrading' to SHA-512 for password storage (fast hashes are the problem, not the size).",
                 "Assuming determinism means reversible — identical outputs reveal nothing about inputs.",
             ],
             qa=(
                 ["Why do the three properties defeat different attackers?",
                  "What does the avalanche count actually prove?",
                  "Why is fixed output length a feature, not a limitation?"],
                 ["Preimage stops reversal, second-preimage stops targeted forgery of a given file, collision stops attackers minting two agreeing meanings — three games, three hardness claims.",
                  "That small input changes diffuse across the whole digest, denying attackers the gradual hill-climbing that breaks weak hashes.",
                  "Fixed length makes digests comparable, storable and transmittable uniformly — variable lengths would leak input size and complicate every protocol."],
             ),
             homework="Write `digest_report(data)` printing determinism check, hex length and avalanche count against a one-byte variant. Run it on two inputs, print both reports, and comment which property each line evidences.",
             patterns=["sha256(", "hexdigest()"],
             mapping="SHA-256 fingerprints downloads, Git objects and certificate contents; every integrity check ahead calls it.",
         ),
         91: dict(
             topic="File integrity monitor",
             idea="An integrity monitor records trusted digests of watched files, then recomputes on schedule and reports three verdicts: unchanged, changed, or unreadable. Changed means investigate (authorised update or tampering — the monitor cannot distinguish, only humans with change records can); unreadable means the monitor itself may be under attack or broken. The trust anchor is the digest database, which must live apart from watched files — digests beside their files let attackers rewrite both consistently. Today's monitor covers synthetic in-memory 'files' with the full verdict logic; real paths change only the reading step, never the decision logic. Keep the verdict vocabulary stable across monitors so operators build one set of reflexes for every system they watch. Drill the four verdicts until responses are automatic, since incidents never wait for documentation reading. Rotate baselines on a published schedule with dual control, so no single operator and no single moment becomes the trust bottleneck.",
             code=(
                 'import hashlib\n'
                 '\n'
                 'baseline = {}\n'
                 '\n'
                 'def record(name: str, content: bytes):\n'
                 '    baseline[name] = hashlib.sha256(content).hexdigest()\n'
                 '    print("recorded:", name)\n'
                 '\n'
                 'def check(name: str, content):\n'
                 '    if content is None:\n'
                 '        return "unreadable"\n'
                 '    if name not in baseline:\n'
                 '        return "unknown"\n'
                 '    if hashlib.sha256(content).hexdigest() == baseline[name]:\n'
                 '        return "unchanged"\n'
                 '    return "CHANGED"\n'
                 '\n'
                 'record("config", b"port=8000")\n'
                 'print("same:     ", check("config", b"port=8000"))\n'
                 'print("edited:   ", check("config", b"port=8001"))\n'
                 'print("missing:  ", check("config", None))\n'
                 'print("new file: ", check("other", b"x"))'
             ),
             variant_b='a 1MB content (does check time stay flat?)',
             variant_c='baseline itself edited (which verdict, and who watches the watcher?)',
             mistakes=[
                 "Digest database beside watched files (consistent rewrite defeats both).",
                 "Changed verdicts auto-accepted because 'updates happen' (tampering hides in routine).",
                 "Unreadable treated as unchanged instead of its own alarm state.",
             ],
             qa=(
                 ["Why must the digest database live apart from watched files?",
                  "Why four verdicts instead of changed/unchanged?",
                  "What can the monitor never decide alone?"],
                 ["Co-located anchors fall with what they guard: an attacker rewriting files rewrites beside digests identically, and verification passes on fiction.",
                  "Unknown (never recorded) and unreadable (possibly attacked monitor) demand different responses than clean negatives — verdicts route playbooks.",
                  "Whether a change was authorised; digests detect difference, while change records and humans decide legitimacy."],
             ),
             homework="Write `record(name, content)` and `check(name, content)` with four verdicts over an external baseline dict. Run them on same/edited/missing/new cases, print all four, and comment which branch catches tampering.",
             patterns=["def ", "sha256("],
             mapping="Tripwire, AIDE and package-manager verification are this monitor with real paths and signed baselines.",
         ),
         92: dict(
             topic="HMAC: keyed integrity",
             idea="Plain hashes authenticate nothing — anyone recomputes them. HMAC mixes a secret key into the hash in a construction (nested hashing with padded keys) that defeats length-extension games, producing tags only key-holders can make or check. Verify-then-act is the law: recompute over received bytes, compare_digest against the received tag, and touch the content only on True. Webhooks, API signatures and session cookies all run this exact pattern; the key stays server-side while tags travel freely. Today's demo signs and verifies with a fixed demo key, stating plainly that real keys come from secrets and rotation, never literals. Document key lifetimes beside every deployment, since keys without expiry dates become permanent secrets that outlive everyone who remembers them. Log every verification with the key identifier used, so post-incident review can tell which key version certified each decision. Versioned key identifiers also make rotation auditable long after the fact.",
             code=(
                 'import hashlib\n'
                 'import hmac\n'
                 '\n'
                 'KEY = b"demo-key-not-secret"\n'
                 '\n'
                 'def sign(body: bytes) -> str:\n'
                 '    return hmac.new(KEY, body, hashlib.sha256).hexdigest()\n'
                 '\n'
                 'def verify(body: bytes, tag: str) -> bool:\n'
                 '    return hmac.compare_digest(sign(body), tag)\n'
                 '\n'
                 "body = b'{\"event\": \"paid\", \"amount\": 100}'\n"
                 "tag = sign(body)\n"
                 "print(\"tag:\", tag[:24], \"...\")\n"
                 "print(\"intact: \", verify(body, tag))\n"
                 "print(\"edited: \", verify(b'{\"event\": \"paid\", \"amount\": 900}', tag))\n"
                 "print(\"no key, no valid tag: authentication, not just integrity\")"
             ),
             variant_b='empty body (does an empty message still authenticate?)',
             variant_c='tag from a different key (what fails, and where?)',
             mistakes=[
                 "SHA256(key + message) homebrew instead of HMAC (length extension eats it).",
                 "Acting on content before verifying the tag (parse-then-check inverts safety).",
                 "Keys in source code, logs or client bundles instead of secret stores with rotation.",
             ],
             qa=(
                 ["Why does plain hashing authenticate nothing?",
                  "Why verify before touching content?",
                  "What breaks if the key leaks but the algorithm holds?"],
                 ["Anyone recomputes plain hashes, so matching proves nothing about origin; only keyed tags restrict forging to key-holders.",
                  "Unverified content may carry exploits for the parser itself; verification first keeps hostile bytes from reaching logic.",
                  "Everything: every past and future tag becomes forgeable, which is why keys rotate and live in secret stores, never code."],
             ),
             homework="Write `sign(body)` and `verify(body, tag)` with a module KEY, using compare_digest. Run them on intact/edited bodies, print both verdicts, and comment which line enforces key-only forging.",
             patterns=["hmac.new(", "compare_digest("],
             mapping="Stripe-style webhook signatures, JWT HS256 and session cookies run sign-then-verify with server-side keys.",
         ),
         93: dict(
             topic="Length extension: why hash(key + msg) dies",
             idea="Merkle–Damgård hashes (MD5, SHA-1, SHA-256) process blocks iteratively, so digest(key + message) leaks enough internal state to extend: given the digest and the message length, attackers compute digest(key + message + padding + extra) without knowing the key — forging 'authenticated' suffixes like '&admin=true'. The demo shows the shape honestly on a toy iterative checksum (real SHA-256 extension needs padding bookkeeping the lesson explains rather than reimplements), then states the fix as law: HMAC's nested construction was designed precisely to break this continuation. Never authenticate with raw-hash-plus-secret in any arrangement. Grep codebases for hash(secret + data) patterns periodically; each hit is a length-extension vulnerability awaiting its forgery demo. Replace every hit with HMAC calls and re-run the test suite to prove behaviour preserved.",
             code=(
                 'import hashlib\n'
                 '\n'
                 'def toy_hash(data: bytes) -> int:\n'
                 '    state = 0\n'
                 '    for byte in data:\n'
                 '        state = (state * 31 + byte) % 65536\n'
                 '    return state\n'
                 '\n'
                 'key, msg = b"SECRET", b"amount=100"\n'
                 'tag = toy_hash(key + msg)\n'
                 'print("tag for key+msg:", tag)\n'
                 'forged_state = tag\n'
                 'for byte in b"&admin=true":\n'
                 '    forged_state = (forged_state * 31 + byte) % 65536\n'
                 'print("extended without key:", forged_state)\n'
                 'print("matches key+msg+extra:", forged_state == toy_hash(key + msg + b"&admin=true"))\n'
                 'print("continuation from leaked state: the whole attack")'
             ),
             variant_b='a different suffix (does any suffix forge equally?)',
             variant_c='HMAC over the same message (why can it not continue this way?)',
             mistakes=[
                 "sha256(secret + data) 'signatures' in production code (flickr's 2009-class bug, still recurring).",
                 "Assuming SHA-256's strength transfers to homebrew keyed arrangements.",
                 "Fixing it with double-hashing instead of HMAC (new arrangement, new analysis needed).",
             ],
             qa=(
                 ["How does the attacker continue the hash without the key?",
                  "Why does HMAC's nesting defeat continuation?",
                  "Why demonstrate on a toy instead of real SHA-256?"],
                 ["Iterative state after key+message is fully captured in the digest, so hashing continues from public state as if the key part never existed.",
                  "The outer hash covers the inner digest, so no exposed state continues the keyed computation — continuation hits a wall of unknown key material.",
                  "Real extension needs exact padding bookkeeping that obscures the idea; the toy shows continuation mechanics honestly while the text states SHA-256's version precisely."],
             ),
             homework="Write `toy_hash(data)` iterative checksum plus a forging loop extending a tag with '&admin=true'. Run it, print the match proof, and comment which property of iteration enables it.",
             patterns=["def ", "return"],
             mapping="HMAC exists because of this attack; audit every keyed hash for nested construction, never concatenation.",
         ),
         94: dict(
             topic="Salts make identical inputs distinct",
             idea="Unsalted password hashes betray every repeat: two users with 'sunshine' share a digest, rainbow tables precompute common passwords once and crack everywhere forever. A unique random salt per password (16+ bytes from secrets, stored beside the hash) forces per-password, per-user work — precomputation dies, identical passwords diverge, and tables built for one database unlock nothing elsewhere. Salts are not secret (stored in the clear next to hashes) yet must be unpredictable per password; reuse across users reopens batch cracking. The demo shows identical passwords diverging under two salts and converging without, proving the mechanism in both directions. Demonstrate convergence without salts and divergence with them in every password review; the pair makes the mechanism undeniable. Show stakeholders both directions whenever password storage is questioned; seeing beats asserting every time. Pair every password-storage review with a live salt-divergence demo so the mechanism stays visible instead of theoretical.",
             code=(
                 'import hashlib\n'
                 'import secrets\n'
                 '\n'
                 'def salted(password: str, salt: bytes) -> str:\n'
                 '    return hashlib.sha256(salt + password.encode()).hexdigest()\n'
                 '\n'
                 'pw = "sunshine"\n'
                 'print("unsalted equal:", hashlib.sha256(pw.encode()).hexdigest() == hashlib.sha256(pw.encode()).hexdigest())\n'
                 's1 = secrets.token_bytes(16)\n'
                 's2 = secrets.token_bytes(16)\n'
                 'print("salted equal:", salted(pw, s1) == salted(pw, s2))\n'
                 'print("lengths only: salts", len(s1), "bytes each (values never logged)")'
             ),
             variant_b='same salt reused for two users (what reappears?)',
             variant_c='salt stored vs salt lost (can verification survive each?)',
             mistakes=[
                 "One global salt ('pepper misuse') instead of per-password randomness.",
                 "Salts shorter than 128 bits, shrinking the uniqueness space.",
                 "Hiding the salt as if secret, then losing it and all verifiability with it.",
             ],
             qa=(
                 ["Why must salts be unique per password rather than per database?",
                  "Why are salts stored in the clear?",
                  "What do rainbow tables lose against salted hashes?"],
                 ["Per-database salts still batch-crack that database's repeats; per-password salts force attackers to redo full work for every single account.",
                  "Salts are uniqueness, not secrecy — verification recomputes with the stored salt, and hiding them adds fragility without security.",
                  "Amortisation: precomputed chains assume one unsalted function, while salts make every password its own function to recompute from scratch."],
             ),
             homework="Write `salted(password, salt)` returning salted SHA-256 hex (demo-grade only). Prove identical passwords diverge under two salts and match unsalted, printing both facts, and comment which property salts provide.",
             patterns=["def ", "sha256("],
             mapping="Salting is necessary but insufficient alone — speed also matters, which is why phase 6 upgrades to PBKDF2.",
         ),
         95: dict(
             topic="MD5 and SHA-1: how algorithms die",
             idea="MD5 collisions went from theory (1996) to seconds on a laptop (2008: rogue CA certificate) to chosen-prefix attacks; SHA-1 fell to SHAttered (2017, 110 GPU-years, then cheaper yearly). The pattern matters more than the dates: cryptanalysis only improves, deprecation lags, and 'still fine for our use' outlives safety every time. Python keeps hashlib.md5/sha1 for legacy verification (old archives, Git's transition period) — using them for security decisions in new code is the vulnerability. Today's demo verifies MD5 still computes (compatibility) while the text buries it for protection: know dead algorithms to recognise them in audits, never to deploy them. Flag legacy uses in audits with migration deadlines, distinguishing verification of old artefacts (legitimate) from protection of new ones (forbidden). Schedule the migration with owners and dates instead of filing advisory wishes. Distinguish verifying old artefacts (keep the code paths) from protecting new data (forbid the algorithms) in every migration ticket.",
             code=(
                 'import hashlib\n'
                 '\n'
                 'data = b"audit me"\n'
                 'print("md5:   ", hashlib.md5(data).hexdigest(), "(legacy verify only)")\n'
                 'print("sha1:  ", hashlib.sha1(data).hexdigest(), "(legacy verify only)")\n'
                 'print("sha256:", hashlib.sha256(data).hexdigest()[:32], "... (current default)")\n'
                 'print("same input, three eras: know all three, deploy only the third")'
             ),
             variant_b='usedforsecurity=False on md5 (what does the flag declare?)',
             variant_c='a FIPS-mode mental model (which of the three survive?)',
             mistakes=[
                 "MD5 password hashes in new systems ('fast and 128 bits' misses the point entirely).",
                 "'SHA-1 is fine for non-security uses' drifting into signatures via copy-paste.",
                 "Ignoring deprecation warnings as noise instead of migration orders.",
             ],
             qa=(
                 ["Why do broken hashes stay in hashlib instead of being removed?",
                  "What does a collision break that preimage strength cannot save?",
                  "Why does cryptanalysis only ever improve?"],
                 ["Legacy verification needs them (old archives, Git objects, HMAC-MD5 protocols in transition) — removal would break reading history, not just writing it.",
                  "Integrity of meaning: two different files sharing one digest lets attackers substitute content under a 'verified' fingerprint.",
                  "Attacks are mathematics published forever; defenders cannot unpublish techniques, so margins only ever shrink toward breakage."],
             ),
             homework="Write `era_report(data)` printing md5/sha1/sha256 digests labelled legacy/legacy/current. Run it on two inputs, print both reports, and comment which two must never guard new decisions.",
             patterns=["hashlib.md5(", "hashlib.sha1("],
             mapping="Audit checklists flag md5/sha1 in new code on sight; migration plans move archives before attackers move first.",
         ),
         96: dict(
             topic="Birthday bound: why 128 bits collide",
             idea="Collisions arrive after roughly 2^(n/2) tries, not 2^n: among 23 people two share a birthday (365 days ≈ 2^8.5, sqrt ≈ 2^4.3 ≈ 23). So 128-bit hashes collide at 2^64 work — enormous but not 2^128 — which is why digests must be twice as wide as comfort suggests. The demo counts trials to first collision in a tiny 16-bit space, showing quadratic arrival (hundreds, not thousands) and letting you extrapolate honestly to real sizes. This arithmetic sets every digest length in the field: 256-bit hashes buy 128-bit collision resistance, the actual margin quoted against birthday attackers. Halve the digest and the margin quarters; every truncation decision reruns this arithmetic explicitly. Write the birthday math next to every shortened digest so reviewers verify margins without research. Record the assumed attacker rate next to the math, because margins valid against hobbyists fail against botnets.",
             code=(
                 'import hashlib\n'
                 '\n'
                 'def short_digest(text: str) -> int:\n'
                 '    return int(hashlib.sha256(text.encode()).hexdigest(), 16) % 65536\n'
                 '\n'
                 'seen, trials = {}, 0\n'
                 'n = 0\n'
                 'while True:\n'
                 '    digest = short_digest(f"probe-{n}")\n'
                 '    trials += 1\n'
                 '    if digest in seen:\n'
                 '        break\n'
                 '    seen[digest] = n\n'
                 '    n += 1\n'
                 '    assert trials < 100000, "16-bit space must collide fast"\n'
                 'print("first collision after", trials, "tries in 16-bit space")\n'
                 'print("sqrt(65536) = 256: birthdays arrive quadratically")'
             ),
             variant_b='8-bit space (how few tries? scale the intuition down)',
             variant_c='deterministic re-run (same count — why must collision counts reproduce?)',
             mistakes=[
                 "Quoting 2^n work against collision attacks (birthday halves the exponent).",
                 "64-bit digests for integrity ('collisions need 2^32' — birthday says 2^32 tries, a laptop afternoon).",
                 "Confusing collision resistance with preimage resistance when choosing sizes.",
             ],
             qa=(
                 ["Why do collisions arrive at 2^(n/2) instead of 2^n?",
                  "Why do real digests need double the comfortable width?",
                  "What does the 16-bit demo extrapolate to for SHA-256?"],
                 ["Pairs grow quadratically with tries, so matches arrive after square-root many samples — birthdays, not brute force.",
                  "Because attackers pay the square root: 128-bit collision security demands 256-bit digests, and quoting otherwise is a factor-2^64 error.",
                  "Same quadratic law at 2^128 work — infeasible physics, but only at full width; every halved digest quarters the margin."],
             ),
             homework="Write `collision_trials(bits)` counting tries to first collision in a truncated digest space. Run it for 8 and 16 bits, print both counts, and comment how counts scale with space size.",
             patterns=["while ", "assert "],
             mapping="Digest widths (256-bit standard) and nonce sizes both derive from birthday arithmetic, not round numbers.",
         ),
         97: dict(
             topic="Hash chains for software updates",
             idea="Chain release artefacts so each version commits to the next: manifest lists file digests, manifest digest signs the release, and clients verify the whole chain before installing. TUF-style thinking in miniature — today's demo builds a three-release chain where tampering any file breaks its manifest entry and any manifest breaks the release digest. Verification order matters (leaf files first, then manifest, then release note) so failures localise to the tampered layer. Single signed digests without chains force blind trust in one value; chains distribute verification across independently checkable links. Verify bottom-up so failures localise to layers; top-down checks report breakage without ever naming the broken link. Chain verification order into runbooks explicitly so on-call engineers localise failures without improvising under pressure. Practice the bottom-up order in drills until it is reflex, because real tampering never waits for runbook reading.",
             code=(
                 'import hashlib\n'
                 '\n'
                 'def digest(data: bytes) -> str:\n'
                 '    return hashlib.sha256(data).hexdigest()\n'
                 '\n'
                 'files = {"app": b"binary-v3", "notes": b"fixes-x"}\n'
                 'manifest = {name: digest(content) for name, content in files.items()}\n'
                 'release = digest(repr(sorted(manifest.items())).encode())\n'
                 'print("release digest:", release[:24], "...")\n'
                 'tampered = dict(files)\n'
                 'tampered["app"] = b"binary-EVIL"\n'
                 'ok = all(digest(tampered[n]) == manifest[n] for n in tampered)\n'
                 'print("tampered files verify:", ok)\n'
                 'print("manifest still matches:", digest(repr(sorted(manifest.items())).encode()) == release)'
             ),
             variant_b='tamper the manifest instead of a file (which check catches it?)',
             variant_c='add a fourth file post-release (what must be re-issued?)',
             mistakes=[
                 "Distributing files with digests on the same untrusted mirror (consistent rewrite).",
                 "Verifying the release note but skipping per-file checks (layer skipped, layer exploitable).",
                 "No version rollback protection — old signed releases reinstall cleanly.",
             ],
             qa=(
                 ["Why verify leaves before the manifest instead of the reverse?",
                  "What breaks if the manifest travels on the same mirror as the files?",
                  "Why must adding a file re-issue the release digest?"],
                 ["Bottom-up localisation: file mismatches name the tampered artefact, while manifest-first failure only says 'something, somewhere' without pointing. Bottom-up verification turns one alarming failure into a named broken layer with a scoped fix and a clear owner.",
                  "Consistent rewrite defeats both layers at once; manifests need a separately trusted channel (signatures, transparency logs) to mean anything.",
                  "The release digest commits to the exact file set — a silent addition keeps the old digest valid while shipping unreviewed content."],
             ),
             homework="Write manifest build + verify functions over a file dict, detecting one tampered file. Run them on clean and tampered sets, print both verdicts, and comment which layer catches file edits.",
             patterns=["def ", "sha256("],
             mapping="TUF, Sigstore and package-manager metadata chains scale this pattern with signatures and rollback guards.",
         ),
         98: dict(
             topic="Truncated tags and their prices",
             idea="Protocols truncate tags (16-byte MACs, short fingerprints) to save bandwidth, paying in forgery odds: an n-bit tag falls to 2^-n guessing per try, and online verification with lockouts tolerates short tags while offline verification never does. The demo compares forgery odds across tag lengths and states the rule plainly — truncation is a measured trade, acceptable where attempts are throttled and catastrophic where attackers try offline billions of times. Never truncate below the threat model's needs to save bytes nobody was counting; bandwidth is cheap, forgeries are forever. Document the threat model beside every truncation: attempt rates assumed, lockouts deployed, and review dates scheduled. Revisit truncation choices when attempt rates change, since higher attacker throughput shortens every previously safe margin.",
             code=(
                 'trials_per_second = 1000\n'
                 'seconds_per_year = 365 * 24 * 3600\n'
                 '\n'
                 'def years_to_forge(tag_bits: int) -> float:\n'
                 '    return (2 ** (tag_bits - 1)) / trials_per_second / seconds_per_year\n'
                 '\n'
                 'for bits in (32, 64, 96, 128):\n'
                 '    print(f"{bits}-bit tag: expected forgery after {years_to_forge(bits):,.0f} years at 1000 tries/s")\n'
                 'print("short tags survive only behind lockouts and throttles")'
             ),
             variant_b='a million tries/s attacker (which lengths survive?)',
             variant_c='offline billions/s (why does only 128 hold?)',
             mistakes=[
                 "Truncated tags justified by 'nobody will guess' without attempt-rate math.",
                 "Same short tag reused online and offline (different games, different minimums).",
                 "Display-truncation (first 8 hex chars) mistaken for protocol truncation with analysis.",
             ],
             qa=(
                 ["Why do online verifiers tolerate shorter tags than offline ones?",
                  "What does the years-to-forge table actually price?",
                  "Why is display truncation different from protocol truncation?"],
                 ["Online attempts face lockouts and throttles, capping tries; offline attackers try billions per second with zero friction — different games, different minimums.",
                  "Expected attacker work at a stated attempt rate: the table converts bits into years, making 'long enough' a calculation instead of a feeling.",
                  "Display shortens human reading while the full tag still verifies; protocol truncation shortens what the attacker must forge."],
             ),
             homework="Write `years_to_forge(tag_bits, rate)` printing expected forgery times for four lengths. Run it at two attacker rates, print both tables, and comment which length survives offline attack.",
             patterns=["def ", "return"],
             mapping="Short MACs appear in bandwidth-tight protocols with online verification; offline contexts keep full tags.",
         ),
         99: dict(
             topic="Peppers: secret salt seasoning",
             idea="Peppers are secret, application-wide values mixed into hashes alongside per-password salts: salts defeat precomputation, peppers force attackers to also steal the pepper before any cracking starts. The trade is operational — peppers must live apart from the database (HSM, secret manager, config vault), because a pepper beside the hashes is decoration, and rotation rehashes everyone. Model it honestly: pepper adds breach-containment, never replaces slow hashing or unique salts. A peppered fast hash still falls to GPUs; a peppered PBKDF2 falls only after both stores fall, which is the entire point of separating them. Test rotation procedures before emergencies force them; untested rotation fails exactly when most needed. Drill rotation with canary accounts first so production rotation never runs untested code paths. Rehearse pepper rotation with canary accounts quarterly so the emergency procedure works before the emergency exists. Alert on pepper-store unavailability as a severity-one event, since authentication halts entirely without it.",
             code=(
                 'import hashlib\n'
                 'import hmac\n'
                 '\n'
                 'PEPPER = b"demo-pepper-not-secret"\n'
                 '\n'
                 'def peppered(password: str, salt: bytes) -> str:\n'
                 '    inner = hashlib.sha256(salt + password.encode()).hexdigest()\n'
                 '    return hmac.new(PEPPER, inner.encode(), hashlib.sha256).hexdigest()\n'
                 '\n'
                 's1 = b"\x01" * 16\n'
                 'print("peppered:", peppered("sunshine", s1)[:24], "...")\n'
                 'print("deterministic:", peppered("sunshine", s1) == peppered("sunshine", s1))\n'
                 'print("pepper stored apart from hashes in production (here: module constant, labelled)")'
             ),
             variant_b='wrong pepper on verify (what fails, and is the failure distinguishable?)',
             variant_c='pepper stored beside the salt (what protection remains?)',
             mistakes=[
                 "Pepper called 'the salt' and reused per-password logic on a global value.",
                 "Pepper committed to the code repository beside the database backups.",
                 "Pepper treated as a substitute for slow hashing (GPUs eat fast hashes regardless).",
             ],
             qa=(
                 ["What does a pepper add that per-password salts do not?",
                  "Why must peppers live apart from the password database?",
                  "Why is pepper no substitute for slow hashing?"],
                 ["Breach containment: database-only theft yields uncrackable hashes until the pepper store also falls — two independent compromises instead of one.",
                  "Beside the hashes it adds nothing an attacker lacks; separation is the entire mechanism, so co-location voids it.",
                  "Peppers gate who can attempt cracking, while slowness prices each attempt; a fast peppered hash still falls cheaply once both stores fall."],
             ),
             homework="Write `peppered(password, salt)` layering HMAC-pepper over salted SHA-256 (demo-grade). Run it on two salts, prove determinism, print digests, and comment which layer the pepper adds.",
             patterns=["hmac.new(", "def "],
             mapping="Peppers live in HSMs and secret managers; rotation rehashes on next login — phase 6 operationalises this.",
         ),
         100: dict(
             topic="Content addressing like Git",
             idea="Git names every object by its hash: identical content dedupes automatically, any corruption changes the name (so corruption cannot hide), and history becomes a hash chain where each commit names its parents. The demo builds a toy object store — store returns the digest-name, load fetches by name and re-verifies — proving dedup and tamper-evidence in fifteen lines. Same idea powers IPFS, Docker layers and backup systems: address by what bits are, not where they live. Limits stated: addressing proves integrity, never authorship — signatures add origin, which content addressing alone cannot provide. Pair addressing with signatures where origin matters and with versioning where freshness matters. Freshness needs monotonic versions or timestamps alongside signatures, or replays of old good states pass silently. Combine signatures for origin with monotonic versions for freshness; either control alone leaves a replay-shaped hole that attackers will find.",
             code=(
                 'import hashlib\n'
                 '\n'
                 'store = {}\n'
                 '\n'
                 'def put(data: bytes) -> str:\n'
                 '    name = hashlib.sha256(data).hexdigest()\n'
                 '    store[name] = data\n'
                 '    return name\n'
                 '\n'
                 'def get(name: str):\n'
                 '    data = store.get(name)\n'
                 '    if data is None or hashlib.sha256(data).hexdigest() != name:\n'
                 '        return None\n'
                 '    return data\n'
                 '\n'
                 'n1 = put(b"v3 binary")\n'
                 'n2 = put(b"v3 binary")\n'
                 'print("dedup (same name):", n1 == n2, "| objects:", len(store))\n'
                 'store[n1] = b"EVIL"\n'
                 'print("tampered fetch:", get(n1))\n'
                 'print("addressing is integrity; authorship needs signatures")'
             ),
             variant_b='two different contents (do names ever collide here?)',
             variant_c='get() on unknown name (which branch, and why None?)',
             mistakes=[
                 "Assuming addressability authenticates the author (it authenticates content only).",
                 "Skipping re-verification on get because 'store is trusted' (bit-rot and bugs exist).",
                 "Hash-named temp files predictably (preimage games on guessable names).",
             ],
             qa=(
                 ["Why does identical content dedupe automatically?",
                  "Why re-verify on every get instead of trusting the store?",
                  "What can content addressing never prove?"],
                 ["Same bytes hash to the same name, so the second put overwrites identically — dedup falls out of addressing with zero bookkeeping.",
                  "Storage rots, bugs corrupt, attackers rewrite: verification at read time catches all three, while write-time-only checks age into fiction.",
                  "Authorship and freshness: who stored it, and whether it is current — signatures and versioning answer those, addressing cannot."],
             ),
             homework="Write `put(data)`/`get(name)` with verify-on-read over a dict store. Prove dedup and tamper detection, print both, and comment which line re-verifies.",
             patterns=["def ", "sha256("],
             mapping="Git objects, Docker layers, IPFS blocks and backup chunking share address-by-content with verify-on-read.",
         ),
         101: dict(
             topic="Hash agility in practice",
             idea="Algorithms retire, so code must switch without rewrites: centralise the digest choice behind one helper plus a registry mapping names to constructors, version stored digests with algorithm tags ('sha256:...'), and verify by dispatching on the tag. The demo migrates a tiny vault from SHA-256 to SHA-512 by changing one registry entry, with old tags still verifying through dispatch. Migration discipline: support new on write, accept old on verify, rehash on next login/use, delete old code only after zero old tags remain in the fleet. Agility is a deployment story told in code structure, not a config flag flipped in panic. Support new algorithms on write while accepting old ones on verify, migrating opportunistically instead of flag-day breaking everything. Delete retired algorithm code only after fleet-wide scans confirm zero remaining old tags in every replica and backup. Keep the old verification code deployed until the last old tag expires, because archives outlive every migration plan.",
             code=(
                 'import hashlib\n'
                 '\n'
                 'ALGOS = {"sha256": hashlib.sha256, "sha512": hashlib.sha512}\n'
                 'CURRENT = "sha256"\n'
                 '\n'
                 'def tag(data: bytes, algo: str = CURRENT) -> str:\n'
                 '    return algo + ":" + ALGOS[algo](data).hexdigest()\n'
                 '\n'
                 'def check(data: bytes, tagged: str) -> bool:\n'
                 '    algo, _, _ = tagged.partition(":")\n'
                 '    return tag(data, algo) == tagged\n'
                 '\n'
                 'old = tag(b"record", "sha256")\n'
                 'print("tagged:", old[:20], "...")\n'
                 'print("verifies:", check(b"record", old))\n'
                 'print("wrong data:", check(b"RECORD", old))\n'
                 'print("one registry, many eras: agility by construction")'
             ),
             variant_b='CURRENT = "sha512" (do old sha256 tags still verify?)',
             variant_c='an unknown algo tag (which failure, and is it safe?)',
             mistakes=[
                 "Untagged digests that cannot name their own algorithm at verify time.",
                 "Flag-day migrations that break every old tag simultaneously.",
                 "Agility via stringly-typed algo names from untrusted input (allowlist the registry).",
             ],
             qa=(
                 ["Why tag digests with their algorithm?",
                  "Why rehash on next use instead of all at once?",
                  "What makes flag-day migrations dangerous?"],
                 ["Verification must dispatch to the right function; untagged digests guess, and guessing breaks the moment two eras coexist.",
                  "Bulk rehashing needs plaintexts you may not hold; opportunistic upgrade migrates without downtime or credential resets.",
                  "Every old tag dies simultaneously — any missed corner (backups, replicas) fails hard instead of degrading gracefully."],
             ),
             homework="Write `tag(data, algo)` and `check(data, tagged)` with an ALGOS registry. Prove cross-era verification, print verdicts, and comment which structure enables migration.",
             patterns=["def ", "return"],
             mapping="Password-hash strings ($argon2id$...) and certificate signature fields carry exactly such algorithm tags.",
         ),
         102: dict(
             topic="Project: full integrity monitor",
             idea="Today's project assembles the phase into one script: a baseline recorder over synthetic files, scheduled-style check runs reporting unchanged/CHANGED/unreadable/unknown counts, HMAC-signed baseline option for hostile storage, and a summary line a human can triage in seconds. Same split-second discipline as day 91, now with salted baselines, tamper drills (edit one file, delete another, add an unknown), and a printed incident summary naming each category. The deliverable is process, not just code: the monitor plus its runbook (what each verdict means, who responds, how baselines rotate). Projects integrate; this one integrates the whole phase.",
             code=(
                 'import hashlib\n'
                 'import hmac\n'
                 '\n'
                 'KEY = b"demo-monitor-key"\n'
                 'files = {"nginx.conf": b"port 80", "app.ini": b"debug=false", "hosts": b"127.0.0.1 x"}\n'
                 'baseline = {n: hmac.new(KEY, c, hashlib.sha256).hexdigest() for n, c in files.items()}\n'
                 '\n'
                 'def audit(current):\n'
                 '    verdicts = {"unchanged": 0, "CHANGED": 0, "unreadable": 0, "unknown": 0}\n'
                 '    for name, content in current.items():\n'
                 '        if content is None:\n'
                 '            verdicts["unreadable"] += 1\n'
                 '        elif name not in baseline:\n'
                 '            verdicts["unknown"] += 1\n'
                 '        elif hmac.compare_digest(hmac.new(KEY, content, hashlib.sha256).hexdigest(), baseline[name]):\n'
                 '            verdicts["unchanged"] += 1\n'
                 '        else:\n'
                 '            verdicts["CHANGED"] += 1\n'
                 '    return verdicts\n'
                 '\n'
                 'live = dict(files)\n'
                 'live["app.ini"] = b"debug=true"\n'
                 'live["hosts"] = None\n'
                 'live["new.sh"] = b"echo hi"\n'
                 'print(audit(live))\n'
                 'print("one of each verdict: triage-ready summary")'
             ),
             variant_b='KEY rotated (which verdicts change, and what does rotation cost?)',
             variant_c='all files unchanged (is a quiet summary still valuable?)',
             mistakes=[
                 "Monitor without a runbook — verdicts nobody knows how to answer.",
                 "Baselines never rotated, so age erodes trust silently.",
                 "CHANGED auto-remediated by restoring (destroys forensic evidence).",
             ],
             qa=(
                 ["Why must CHANGED trigger investigation instead of auto-restore?",
                  "Why do baselines need rotation schedules?",
                  "What makes the summary triage-ready?"],
                 ["Restoration destroys the evidence of how the change happened; investigate first (was it authorised? how?), restore from known-good second.",
                  "Trust erodes with age and staff turnover; scheduled rotation with dual control keeps the anchor trustworthy instead of fossilised.",
                  "One line per verdict category with counts — a human decides response in seconds without reading raw output."],
             ),
             homework="Write `audit(current)` returning four verdict counts with named verdict constants instead of magic strings, keeping the summary readable as categories grow. over an HMAC baseline. Run it on a drilled set (one of each), print the summary, and comment which branch names tampering.",
             patterns=["def ", "compare_digest("],
             mapping="Tripwire/AIDE deployments pair exactly this monitor with runbooks, rotation schedules and signed baselines.",
         ),
         103: dict(
             topic="Testing hash code with asserts",
             idea="Hash-test discipline: determinism twice, length contracts per algorithm, avalanche smoke (one-bit change moves many chars), empty-input definedness, malformed-input refusal, and cross-check against published test vectors for SHA-256 ('abc' → ba7816...). Vectors catch implementation drift that self-consistency tests cannot — a bug deterministic in both runs passes naive asserts while failing the standard. Assert contracts and vectors, never live digests of changing inputs. These guards wrap every hash helper hereafter; a helper whose vectors fail is broken no matter how clean its code reads. Pin vector sources to standard documents with section numbers so future maintainers can re-derive every expected value. Start every hash component review by running its vectors green; a red vector stops the review before a single line is read, because broken primitives invalidate everything above them. Vectors also pin down edge semantics that prose leaves ambiguous: empty-input digests, exact hex casing, and truncation behaviour. When two implementations disagree, the vectors arbitrate without appeal. Keep vectors beside the code they guard, updated from standards with cited sections, never from memory. Review vector coverage whenever primitives change versions.",
             code=(
                 'import hashlib\n'
                 '\n'
                 'assert hashlib.sha256(b"abc").hexdigest() == "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"\n'
                 'assert hashlib.sha256(b"").hexdigest() == "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"\n'
                 'assert len(hashlib.sha512(b"x").hexdigest()) == 128\n'
                 'a = hashlib.sha256(b"probe").hexdigest()\n'
                 'assert a == hashlib.sha256(b"probe").hexdigest()\n'
                 'print("vectors hold: implementation matches the standard")'
             ),
             variant_b='a wrong expected vector (does the assert fire, proving the test tests?)',
             variant_c='sha1 vector 2fd4e1c67a2d28fced849ee1bb76e7391b93eb12 (legacy vectors still verify history)',
             mistakes=[
                 "Self-consistency only, which passes identically-broken implementations.",
                 "Vectors copied from untrusted sources instead of the standard.",
                 "No empty-input vector, where padding bugs love to hide.",
             ],
             qa=(
                 ["Why do published vectors catch bugs that self-consistency tests miss?",
                  "Why test the empty input specifically?",
                  "Where must vectors come from?"],
                 ["A deterministic bug reproduces itself perfectly, passing every self-check; only comparison against independent truth exposes it.",
                  "Empty inputs exercise padding paths where implementation bugs love to hide; standards include them for exactly that reason.",
                  "The standard itself (FIPS, RFCs), never untrusted copies — a wrong expected value makes the test certify fiction."],
             ),
             homework="Write `vector_check()` asserting two SHA-256 published vectors plus lengths. Run it, print confirmation, and comment why vectors beat self-consistency.",
             patterns=["assert ", "sha256("],
             mapping="FIPS CAVP vectors and RFC test suites scale this practice; every primitive ships with known answers.",
         ),
         104: dict(
             topic="Phase review: hashes and integrity",
             idea="Rebuild from memory: SHA-256's three properties with their work factors, file monitors with four verdicts and separate anchors, HMAC's nested construction against length extension, homebrew keyed-hash failure mode, per-password salts killing precomputation, MD5/SHA-1 death timelines, birthday square-roots sizing every digest, manifest chains with bottom-up verification, truncation priced in years, peppers as breach containment, content addressing with verify-on-read, algorithm agility by tagged dispatch. Close the notes and reproduce the HMAC sign/verify pair plus the birthday demo — services named, outputs verified. The missing line is tomorrow's first job; symmetric ciphers (phase 3) assume hashes and MACs as solved infrastructure. Carry forward three tools above all: centralised digest helpers, constant-time verification, and tagged algorithm agility. Rehearse the recap quarterly as new primitives arrive; the three tools transfer to every algorithm generation unchanged. Close the phase by writing the three tools on one card kept visible at the workstation. Recite the card before every crypto review without exception.",
             code=(
                 'import hashlib\n'
                 'import hmac\n'
                 '\n'
                 'KEY = b"demo-review-key"\n'
                 'tag = hmac.new(KEY, b"review payload", hashlib.sha256).hexdigest()\n'
                 'print("tag:", tag[:24], "...")\n'
                 'print("verifies:", hmac.compare_digest(hmac.new(KEY, b"review payload", hashlib.sha256).hexdigest(), tag))\n'
                 'print("tampered: ", hmac.compare_digest(hmac.new(KEY, b"review PAYLOAD", hashlib.sha256).hexdigest(), tag))\n'
                 'print("recall pair: sign with key, verify constant-time")'
             ),
             variant_b='empty payload (does the pair behave?)',
             variant_c='KEY of one byte (works — but what policy does it violate?)',
             mistakes=[
                 "Rebuilding with notes open — retrieval is the learning.",
                 "Reciting HMAC without placing key handling in a running script.",
                 "Skipping the birthday demo because 'math is math' (intuition needs the experiment).",
             ],
             qa=(
                 ["What single rebuild proves this phase stuck?",
                  "Why rebuild the birthday demo rather than just the HMAC pair?",
                  "What does a failed rebuild locate?"],
                 ["HMAC sign/verify from memory with constant-time comparison, plus the birthday collision count — mechanism and arithmetic, both reproducible.",
                  "The pair proves mechanism; the collision count proves the quantitative intuition that sizes every digest and nonce in the field.",
                  "The exact missing line is tomorrow's first job — failed retrieval marks the gap precisely, unlike re-reading which marks nothing."],
             ),
             homework="Write `phase_recap()` from memory including the birthday collision count: HMAC sign/verify pair with verdicts printed plus the quantitative intuition restated. with verdicts printed. Run it, print the pair, and comment which line you had to look up.",
             patterns=["hmac.new(", "compare_digest("],
             mapping="Phase 3 assumes keyed integrity as solved; every cipher lesson checks tags before touching plaintext.",
         ),
     }),
    ("Symmetric Ciphers, Honestly",
     "Teaching ciphers labelled as such: Caesar analysis, Vigenere, two-time-pad attacks, ECB tells, and encrypt-then-MAC discipline. Production uses AES-GCM; nothing here does.",
     {
         105: dict(
             topic="Caesar cipher: shifts and their weakness",
             idea="The Caesar cipher shifts each letter by a fixed key (TEACHING CIPHER — no confidentiality against anyone trying): with 26 possible shifts, brute force finishes before coffee cools. Its value is pedagogical: it demonstrates substitution, keyspace measurement (26 tries), and why small keyspaces die. The demo encrypts under key 3 and brute-forces all shifts, flagging readable candidates. Real alphabets need 2^128 keys, not 26 — the day's honest contrast between 'breakable by hand' and 'infeasible by physics' sets the key-size intuition every later primitive assumes. Classical ciphers teach thinking, never protection. Keep a broken-by-hand example in every crypto course: nothing teaches keyspace like counting 26 tries yourself. Then contrast with 2^128 immediately, so the lesson ends at physics rather than at toys.",
             code=(
                 'def caesar(text: str, shift: int) -> str:\n'
                 '    out = []\n'
                 '    for ch in text.lower():\n'
                 '        if "a" <= ch <= "z":\n'
                 '            out.append(chr((ord(ch) - 97 + shift) % 26 + 97))\n'
                 '        else:\n'
                 '            out.append(ch)\n'
                 '    return "".join(out)\n'
                 '\n'
                 'cipher = caesar("attack at dawn", 3)\n'
                 'print("cipher:", cipher)\n'
                 'print("brute force (26 shifts, spot the English):")\n'
                 'for key in range(26):\n'
                 '    guess = caesar(cipher, -key)\n'
                 '    mark = " <== English" if guess == "attack at dawn" else ""\n'
                 '    if key in (0, 3, 23):\n'
                 '        print(f"  key {key:2}: {guess}{mark}")'
             ),
             variant_b='key 13 (ROT13 — why is self-inverse convenient and irrelevant?)',
             variant_c='a 3-letter message (does brute force get harder or easier?)',
             mistakes=[
                 "Deploying Caesar/Vigenere anywhere real ('better than nothing' is worse — false confidence).",
                 "Counting 26 shifts as '26-bit security' (keyspace size in tries, not bits).",
                 "Keeping spaces and punctuation unshifted, leaking word lengths for free.",
             ],
             qa=(
                 ["Why is a 26-key cipher broken regardless of implementation quality?",
                  "What does brute-forcing all shifts demonstrate about keyspaces?",
                  "Why keep spaces unshifted in the demo — is that realistic?"],
                 ["The keyspace holds 26 candidates; exhaustive search finishes instantly, so no implementation detail can save a cipher with no keys to hide behind.",
                  "That security scales with key count: 26 tries is a joke, 2^128 is physics — the demo makes keyspace the visible variable.",
                  "Real classical traffic kept spacing (a genuine weakness leaking word shapes); the demo preserves the flaw to teach it, not to endorse it."],
             ),
             homework="Write `caesar(text, shift)` preserving non-letters, plus a brute-force loop printing all 26 candidates. Run it on two ciphertexts, identify the English rows, and comment which line makes the keyspace enumerable.",
             patterns=["def ", "return"],
             mapping="Classical ciphers teach substitution and keyspace thinking only; production confidentiality is AES-GCM via the `cryptography` package.",
         ),
         106: dict(
             topic="Frequency analysis breaks substitution",
             idea="Monoalphabetic substitution preserves frequency fingerprints: e stays most common under any mask, so counting cipher letters and mapping the ranking onto English order cracks messages no brute force could touch (26! keys). The demo builds a scrambled alphabet, encrypts a paragraph, then decodes by frequency rank — imperfect (a/o swap) but readable, proving statistical attacks recover meaning without keys. The defence lesson lands by contrast: modern ciphers diffuse every input bit across the output (avalanche, day 90), leaving no fingerprint to count. Where statistics survive encryption, the cipher leaks; where they die, analysis begins elsewhere. Run frequency attacks in the lab to feel statistical leakage; the intuition transfers to side channels, where statistics leak through physics instead of ciphers. Power and timing variations betray keys the same way frequencies betrayed letters; the defence is constant-time code.",
             code=(
                 'import string\n'
                 '\n'
                 'ALPHA = string.ascii_lowercase\n'
                 'KEY = "qwertyuiopasdfghjklzxcvbnm"\n'
                 'ENGLISH_ORDER = "etaoinshrdlcumwfgypbvkjxqz"\n'
                 '\n'
                 'def sub_encrypt(text: str) -> str:\n'
                 '    table = str.maketrans(ALPHA, KEY)\n'
                 '    return text.lower().translate(table)\n'
                 '\n'
                 'plain = ("we hold these truths to be self evident that all men are created equal " * 6).strip()\n'
                 'cipher = sub_encrypt(plain)\n'
                 'freq = {}\n'
                 'for ch in cipher:\n'
                 '    if ch in ALPHA:\n'
                 '        freq[ch] = freq.get(ch, 0) + 1\n'
                 'ranked = "".join(sorted(freq, key=freq.get, reverse=True))\n'
                 'guess_key = str.maketrans(ranked, ENGLISH_ORDER[:len(ranked)])\n'
                 'print("cracked head:", cipher.translate(guess_key)[:70])\n'
                 'print("readable without the key: statistics did it")'
             ),
             variant_b='a 20-character message (does frequency still resolve?)',
             variant_c='homophonic disguise with two symbols for e (how does the ranking break?)',
             mistakes=[
                 "Trusting frequency on tiny samples where noise outvotes signal.",
                 "Assuming homophones were used historically (they specifically defeat naive frequency).",
                 "Concluding modern ciphers fall the same way (diffusion kills fingerprints by design).",
             ],
             qa=(
                 ["Why does substitution preserve the frequency fingerprint?",
                  "Why does the crack degrade on short texts?",
                  "What cipher property would defeat frequency analysis?"],
                 ["One-to-one letter mapping renames symbols without changing their counts — statistics describe populations, and renaming nobody changes the census.",
                  "Rankings need samples to converge; short texts let chance reorder letters, misaligning the whole mapping.",
                  "Diffusion: each output bit depending on many input bits, so no symbol preserves its count — exactly what modern ciphers engineer."],
             ),
             homework="Write frequency-rank decode for a substitution ciphertext, printing the first 70 cracked chars. Run it on long and short texts, print both, and comment where sample size decides success.",
             patterns=["def ", ".get("],
             mapping="Classical cryptanalysis only; modern cipher design starts where frequency dies (diffusion, confusion).",
         ),
         107: dict(
             topic="ECB: identical blocks betray",
             idea="Electronic Codebook encrypts each block independently with the same key: identical plaintext blocks yield identical ciphertext blocks, so patterns survive encryption visibly — the ECB penguin (encrypted image still showing the bird) is the canonical demonstration. The demo encrypts structured rows with a toy 8-byte block 'cipher' (XOR with key, TEACHING CIPHER) and shows repeated rows producing repeated blocks. Lesson: determinism leaks equality, and equality is information. Real modes chain blocks (CBC) or count nonces (CTR/GCM); ECB survives only in single-block uses like key wrapping, never for data. Grep codebases for ECB mode selections periodically; each hit on multi-block data is a penguin awaiting its photographer. Photograph it once in the lab with structured rows so the pattern is recognised instantly in production captures.",
             code=(
                 'def toy_block(block: bytes, key: bytes) -> bytes:\n'
                 '    return bytes(b ^ key[i % len(key)] for i, b in enumerate(block))\n'
                 '\n'
                 'KEY = bytes([0x2B, 0x7E])\n'
                 'rows = [b"ALLOW999", b"ALLOW999", b"DENY0000"]\n'
                 'ecb = [toy_block(r, KEY).hex() for r in rows]\n'
                 'print("ECB blocks:", ecb)\n'
                 'print("rows 0,1 identical in ciphertext:", ecb[0] == ecb[1], "(pattern leaked!)")\n'
                 'print("row 2 differs:", ecb[2] != ecb[0])\n'
                 'print("determinism leaks equality: never encrypt rows with ECB")'
             ),
             variant_b='all three rows identical (what does the ciphertext reveal?)',
             variant_c='all rows distinct (does ECB hide everything now?)',
             mistakes=[
                 "ECB chosen as 'the simple mode' for multi-block data (the penguin awaits).",
                 "Assuming equal ciphertexts require equal keys (equal plaintexts suffice).",
                 "ECB for anything but single-block key wrapping.",
             ],
             qa=(
                 ["Why do identical plaintext blocks betray themselves under ECB?",
                  "Why doesn't distinctness save ECB?",
                  "Where is ECB legitimately used?"],
                 ["Same input plus same key plus no state equals same output, deterministically — equality of rows survives encryption visibly.",
                  "Attackers still learn equality patterns across messages and positions; secrecy of content with leaked structure is half-secrecy.",
                  "Single-block key wrapping, where there is exactly one block and no pattern to leak — data modes need chaining or nonces."],
             ),
             homework="Write `ecb_rows(rows, key)` with the toy block cipher, printing which row pairs collide. Run it on repeated and distinct rows, print both, and comment which property leaks.",
             patterns=["def ", "return"],
             mapping="Real modes: CBC chains, CTR counts nonces, GCM adds authentication — ECB is the cautionary tale opening every modes chapter.",
         ),
         108: dict(
             topic="Stream reuse: crib-dragging live",
             idea="Reusing one keystream across two messages cancels it out of their XOR, leaving plaintext-XOR-plaintext for crib-dragging (day 79's law, now with English messages and a scoring loop ranking every crib position by English-likeness). The demo automates the attack end to end: encrypt two sentences under one keystream, XOR the ciphertexts, drag three cribs, print each crib's best-scoring position. This is the authorized-lab version of historical breaks (Venona's reused pads) and modern nonce-misuse bugs. One keystream, one message — the law has no exceptions, and today you enforce it by breaking its violation.",
             code=(
                 'def xor_bytes(data: bytes, key: bytes) -> bytes:\n'
                 '    return bytes(b ^ key[i % len(key)] for i, b in enumerate(data))\n'
                 '\n'
                 'stream = bytes([0x3A, 0x7F, 0xC2, 0x11, 0x55, 0x08, 0x9E, 0xD0, 0x41, 0x22, 0x77, 0xB4, 0x0C, 0xF1, 0x6A])\n'
                 'm1 = b"attack at dawn!"\n'
                 'm2 = b"retreat now!!!"\n'
                 'mixed = bytes(a ^ b for a, b in zip(xor_bytes(m1, stream), xor_bytes(m2, stream)))\n'
                 '\n'
                 'def score(fragment: bytes) -> int:\n'
                 '    return sum(1 for b in fragment if 97 <= b <= 122 or b == 32)\n'
                 '\n'
                 'for crib in (b" the ", b"and", b"attack"):\n'
                 '    best = max(range(len(mixed) - len(crib) + 1), key=lambda p: score(bytes(mixed[p + i] ^ crib[i] for i in range(len(crib)))))\n'
                 '    frag = bytes(mixed[best + i] ^ crib[i] for i in range(len(crib)))\n'
                 '    print(f"crib {crib}: best pos {best} reveals {frag} (score {score(frag)}/{len(crib)})")'
             ),
             variant_b='crib b"xyzzy" (absent word — what does the best position reveal?)',
             variant_c='m2 random bytes (does structureless plaintext resist dragging?)',
             mistakes=[
                 "Reusing nonces 'just in tests' that ship to production.",
                 "Assuming short messages survive reuse (cribs fit short texts fine).",
                 "IVs generated with random instead of guaranteed-unique counters where reuse must be impossible.",
             ],
             qa=(
                 ["Why does XOR-ing two ciphertexts cancel the keystream?",
                  "How does scoring automate crib-dragging?",
                  "Why is a repeated nonce total breakage rather than slight weakening?"],
                 ["c1^c2 = (m1^k)^(m2^k) = m1^m2 — the keystream appears twice and XOR self-cancels exactly.",
                  "Correct positions reveal letters and spaces (high scores) while wrong ones yield bytes; ranking positions runs the attack unattended.",
                  "It converts ciphertext secrecy into a language puzzle solvable with patience — protection drops to zero wherever cribs fit."],
             ),
             homework="Write `crib_drag(c1, c2, cribs)` scoring every crib position and printing each crib's best reveal. Run it on two same-keystream pairs, print both, and comment which XOR cancels the stream.",
             patterns=["def ", "return"],
             mapping="Nonce-misuse bugs (including AES-GCM failures) and historical pad reuse share these mechanics; unique nonces always.",
         ),
         109: dict(
             topic="Block chaining sketch: state matters",
             idea="Chaining feeds each ciphertext block into the next block's encryption (xor with previous output before the toy cipher), so identical plaintext rows diverge whenever history differs — the anti-ECB. The demo encrypts repeated rows chained versus unchained and shows chained blocks differing while ECB repeats, proving state kills patterns. Randomised IVs start the chain unpredictably per message (same rows, different ciphertexts every send), which the demo shows by re-chaining with a new IV. Honest labelling throughout: the toy cipher is XOR, not AES; chaining structure is what's taught, and real CBC adds padding discipline (and its own oracle history) that this sketch does not claim to cover.",
             code=(
                 'def toy_block(block: bytes, key: bytes) -> bytes:\n'
                 '    return bytes(b ^ key[i % len(key)] for i, b in enumerate(block))\n'
                 '\n'
                 'KEY = bytes([0x2B, 0x7E])\n'
                 'IV = bytes([0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08])\n'
                 'rows = [b"ALLOW999", b"ALLOW999"]\n'
                 '\n'
                 'def chain(rows, iv):\n'
                 '    out, prev = [], iv\n'
                 '    for r in rows:\n'
                 '        mixed = bytes(a ^ b for a, b in zip(r, prev))\n'
                 '        prev = toy_block(mixed, KEY)\n'
                 '        out.append(prev)\n'
                 '    return out\n'
                 '\n'
                 'chained = [c.hex() for c in chain(rows, IV)]\n'
                 'print("chained blocks:", chained)\n'
                 'print("identical rows diverge:", chained[0] != chained[1])\n'
                 'print("state kills patterns: the anti-ECB")'
             ),
             variant_b='a fresh random IV per send (same rows, new ciphertexts — why is that good?)',
             variant_c='IV reused across sends (which ECB property returns?)',
             mistakes=[
                 "Predictable IVs (zero IV everywhere) handing attackers chosen starting state.",
                 "Chaining without authentication (padding oracles eat unauthenticated CBC alive).",
                 "Crediting the toy cipher with real security because the structure lesson worked.",
             ],
             qa=(
                 ["Why do identical rows diverge under chaining but repeat under ECB?",
                  "Why randomise the IV per message?",
                  "What does chaining still fail to provide?"],
                 ["Chaining mixes history into every block, so position-two input differs even when plaintext repeats; ECB's statelessness repeats outputs for repeated inputs.",
                  "Fresh IVs make equal messages encrypt differently every send, denying attackers equality observations across messages.",
                  "Integrity: chaining hides patterns but authenticates nothing — tampering still goes undetected without MACs."],
             ),
             homework="Write `chain(rows, iv, key)` with the toy cipher, printing both block hexes. Run it on repeated rows with two IVs, print both chains, and comment which line carries history forward.",
             patterns=["def ", "return"],
             mapping="CBC chains with random IVs in real protocols; padding oracles are why CBC always pairs with MACs.",
         ),
         110: dict(
             topic="Encrypt-then-MAC discipline",
             idea="Encryption gives secrecy, MACs give integrity, and order decides safety: encrypt-then-MAC (tag the ciphertext, verify before decrypting) is the arrangement that survives analysis, while MAC-then-encrypt and encrypt-and-MAC both leaked historically. The demo builds the discipline honestly — toy XOR cipher plus HMAC tag, verify tag first, decrypt only on True, tampered ciphertext refused before touching the cipher. Verification-before-use is the whole ballgame: decryption oracles (padding, compression, error messages) all exploit systems that act on unverified ciphertext. Real deployments use AES-GCM (combined mode); this lesson teaches the discipline GCM automates. Rehearse the verify-first order until it is reflex, because decryption oracles punish hesitation with plaintext. Make verify-first the default code shape so unsafe orders require deliberate effort to write. Review combined modes for the discipline they automate rather than assuming automation equals understanding. Unsafe orders should be hard to write by accident and easy to spot in review, with lint rules flagging decrypt-before-verify patterns.",
             code=(
                 'import hashlib\n'
                 'import hmac\n'
                 '\n'
                 'CKEY = bytes([0x2B, 0x7E])\n'
                 'MKEY = b"demo-mac-key"\n'
                 '\n'
                 'def enc(plain: bytes) -> bytes:\n'
                 '    return bytes(b ^ CKEY[i % len(CKEY)] for i, b in enumerate(plain))\n'
                 '\n'
                 'def seal(plain: bytes):\n'
                 '    cipher = enc(plain)\n'
                 '    return cipher, hmac.new(MKEY, cipher, hashlib.sha256).hexdigest()\n'
                 '\n'
                 'def open_sealed(cipher: bytes, tag: str):\n'
                 '    if not hmac.compare_digest(hmac.new(MKEY, cipher, hashlib.sha256).hexdigest(), tag):\n'
                 '        return None\n'
                 '    return enc(cipher)\n'
                 '\n'
                 'c, t = seal(b"pay 100")\n'
                 'print("intact:  ", open_sealed(c, t))\n'
                 'print("flipped: ", open_sealed(bytes([c[0] ^ 1]) + c[1:], t))\n'
                 'print("verify-before-decrypt: tampering refused, cipher untouched")'
             ),
             variant_b='decrypt-then-verify order (what oracle opens?)',
             variant_c='tag over plaintext instead of ciphertext (which forgery returns?)',
             mistakes=[
                 "Decrypting before verifying (every padding oracle ever).",
                 "MAC-then-encrypt chosen for 'elegance' despite the cryptanalysis.",
                 "Same key for cipher and MAC (key separation is not optional).",
             ],
             qa=(
                 ["Why must verification precede decryption, not follow it?",
                  "Why tag the ciphertext rather than the plaintext?",
                  "Why separate cipher and MAC keys?"],
                 ["Decryption acts on hostile bytes (padding checks, error messages) and every reaction is an oracle; verification first keeps hostile bytes from acting at all.",
                  "Receivers hold ciphertext first; a plaintext tag cannot be checked until after decryption, forcing exactly the act-before-verify order that oracles exploit.",
                  "One key serving two algorithms couples their fates — a weakness in either leaks both; separation contains each break to its own domain."],
             ),
             homework="Write `seal(plain)`/`open_sealed(cipher, tag)` with verify-first discipline and separate keys. Run them on intact/flipped inputs, print both outcomes, and comment which line refuses before decrypting.",
             patterns=["compare_digest(", "def "],
             mapping="AES-GCM/AES-CCM are combined modes embodying this discipline; TLS 1.3 forbids the unsafe orders outright.",
         ),
         111: dict(
             topic="Nonces: numbers used once",
             idea="Modes like CTR and GCM turn block ciphers into streams keyed by nonce: same key plus fresh nonce per message gives fresh keystream; repeated nonces give two-time-pad catastrophe (day 108's attack, now with real-mode consequences — AES-GCM nonce reuse leaks plaintext XORs and destroys authentication). Nonce discipline has exactly two safe designs: counters persisted across reboots (never repeat by construction) or 96-bit random nonces with birthday-checked rotation before 2^32 messages. The demo encrypts one message under fresh versus reused nonces with a SHA-256-counter teaching construction, showing divergence versus repetition. Counters beat randomness where state survives; randomness needs rotation math where it does not. Document nonce strategies beside every key, since keys without nonce plans are reuse incidents scheduled in advance. Persist counters across reboots with atomic writes, since a counter that resets is a reuse machine.",
             code=(
                 'import hashlib\n'
                 '\n'
                 'KEY = b"demo-stream-key"\n'
                 '\n'
                 'def keystream(nonce: bytes, nbytes: int) -> bytes:\n'
                 '    out = b""\n'
                 '    counter = 0\n'
                 '    while len(out) < nbytes:\n'
                 '        out += hashlib.sha256(KEY + nonce + counter.to_bytes(4, "big")).digest()\n'
                 '        counter += 1\n'
                 '    return out[:nbytes]\n'
                 '\n'
                 'def enc(plain: bytes, nonce: bytes) -> bytes:\n'
                 '    ks = keystream(nonce, len(plain))\n'
                 '    return bytes(a ^ b for a, b in zip(plain, ks))\n'
                 '\n'
                 'm = b"same message!!"\n'
                 'c1 = enc(m, b"nonce-0001")\n'
                 'c2 = enc(m, b"nonce-0002")\n'
                 'c3 = enc(m, b"nonce-0001")\n'
                 'print("fresh nonces differ:", c1.hex() != c2.hex())\n'
                 'print("reused nonce repeats:", c1.hex() == c3.hex(), "(determinism = reuse visible)")'
             ),
             variant_b='nonce reused across different messages (which day-108 attack returns?)',
             variant_c='96-bit random nonces: how many messages before rotation at 2^32? (birthday math)',
             mistakes=[
                 "Random nonces without rotation accounting (birthday collisions scheduled).",
                 "Counters reset on reboot (the classic nonce-reuse incident shape).",
                 "Same (key, nonce) pair across protocol versions or directions.",
             ],
             qa=(
                 ["Why do fresh nonces make identical plaintexts encrypt differently?",
                  "Why is nonce reuse catastrophic rather than mildly bad?",
                  "Counters or random: how do you choose?"],
                 ["Each nonce seeds a distinct keystream, so equal inputs meet different masks — determinism per pair, uniqueness across pairs.",
                  "Reused keystreams cancel out of ciphertext pairs (day 108), exposing plaintext XORs, and GCM authentication collapses alongside.",
                  "Counters where persistent state survives reboots; 96-bit random with birthday-counted rotation where state cannot be kept."],
             ),
             homework="Write `enc(plain, nonce)` over the SHA-256-counter construction, proving fresh nonces diverge and reused repeat. Run it on same/different nonces, print both facts, and comment which input must never repeat.",
             patterns=["def ", "return"],
             mapping="AES-GCM demands unique 96-bit nonces; TLS 1.3 constructs them from sequence numbers so reuse is structurally impossible.",
         ),
         112: dict(
             topic="Key sizes and brute force math",
             idea="Key strength is arithmetic, not adjectives: n-bit keys need ~2^(n-1) average tries, so each added bit doubles attacker work while adding zero implementation cost. The demo prices keyspaces in years at stated attacker rates — DES's 56 bits fall in hours on modern hardware, 128 bits outlive stars at any plausible rate — converting 'long enough' from feeling to calculation. Quantum notes kept honest: Grover halves effective symmetric strength (AES-128 → ~64-bit quantum work, hence AES-256's margin), while Shor breaks RSA/ECC outright (hence post-quantum migration, not panic). Choose 128-bit minimums today, 256 where data outlives machines, and distrust any key too short to survive its own threat window.",
             code=(
                 'trials_per_second = 10 ** 12\n'
                 'seconds_per_year = 365 * 24 * 3600\n'
                 '\n'
                 'def years_to_break(key_bits: int) -> float:\n'
                 '    return (2 ** (key_bits - 1)) / trials_per_second / seconds_per_year\n'
                 '\n'
                 'for bits in (56, 64, 80, 128, 256):\n'
                 '    print(f"{bits}-bit key: {years_to_break(bits):,.1f} years at a trillion tries/s")\n'
                 'print("56 falls today; 128 outlives stars: arithmetic, not adjectives")'
             ),
             variant_b='a billion-times-faster attacker (which lengths survive?)',
             variant_c='Grover halving (what effective strength remains for AES-128?)',
             mistakes=[
                 "'Military-grade' cited instead of bit counts.",
                 "64-bit keys for data living decades (breakage scheduled mid-lifetime).",
                 "Password-derived keys quoted at hash-output strength (entropy of password, not digest, rules).",
             ],
             qa=(
                 ["Why does each added bit double attacker work?",
                  "Why is DES dead while AES-128 lives?",
                  "What does Grover change and not change?"],
                 ["Keyspaces double per bit (2^n candidates), so average search cost doubles exactly — security scales exponentially with linear cost.",
                  "56 bits fall in hours at modern rates while 128 bits demand 2^127 tries — a gap no hardware roadmap closes within physics.",
                  "It halves symmetric effective strength (square-root search), so AES-256 keeps margin; it breaks public-key math entirely, forcing migration."],
             ),
             homework="Write `years_to_break(key_bits, rate)` printing forgery times for five lengths. Run it at two attacker rates, print both tables, and comment which length survives its threat window.",
             patterns=["def ", "return"],
             mapping="128-bit minimums everywhere, 256 where data outlives machines; password strength follows entropy math, never digest sizes.",
         ),
         113: dict(
             topic="Vigenere and repeating keys",
             idea="The Vigenère cipher cycles a keyword over the message (TEACHING CIPHER): polyalphabetic on the surface, still breakable because repetition leaks structure — same plaintext blocks under the same key position encrypt identically, and Kasiski examination (repeated ciphertext fragments spaced by key-length multiples) recovers the period. The demo encrypts under LEMON, then finds repeated trigrams and their spacings' gcd to reveal key length 5. Once the period is known, the cipher collapses into Caesar slices solved by frequency (day 106's attack, once per slice). Repeating keys are the bridge from classical toys to stream-cipher discipline: period is the enemy, and modern keystreams are engineered to have none in any feasible message.",
             code=(
                 'def vigenere(text: str, key: str) -> str:\n'
                 '    out = []\n'
                 '    for i, ch in enumerate(text.lower()):\n'
                 '        if "a" <= ch <= "z":\n'
                 '            shift = ord(key[i % len(key)].lower()) - 97\n'
                 '            out.append(chr((ord(ch) - 97 + shift) % 26 + 97))\n'
                 '        else:\n'
                 '            out.append(ch)\n'
                 '    return "".join(out)\n'
                 '\n'
                 'cipher = vigenere("attack at dawn attack at dusk", "lemon")\n'
                 'print("cipher:", cipher)\n'
                 'from collections import Counter\n'
                 'tris = Counter(cipher[i:i + 3] for i in range(len(cipher) - 2))\n'
                 'rep = sorted(((t, [i for i in range(len(cipher) - 2) if cipher[i:i + 3] == t]) for t, n in tris.items() if n > 1))\n'
                 'print("repeated trigrams:", [(t, pos) for t, pos in rep][:3])\n'
                 'print("spacings hint key length: Kasiski in miniature")'
             ),
             variant_b='key "a" (what does Vigenere degrade to?)',
             variant_c='key as long as the message (Kasiski finds no period — what is it now?)',
             mistakes=[
                 "Longer keywords mistaken for proportional security (period recovery scales effortlessly).",
                 "Vigenere deployed anywhere real, three centuries after its breaking.",
                 "Key-length discovery skipped, attacking slices blindly.",
             ],
             qa=(
                 ["How do repeated trigrams reveal the key length?",
                  "Why does a message-long key defeat Kasiski?",
                  "What does Vigenere teach about modern stream ciphers?"],
                 ["Repeats land on same key positions when spaced by key-length multiples, so spacing gcds expose the period.",
                  "No period exists to recover — every position uses a fresh key letter, which is exactly the one-time-pad condition (with randomness still required).",
                  "That keystream period is the enemy: modern designs engineer astronomically long periods so Kasiski-style analysis finds nothing."],
             ),
             homework="Write `vigenere(text, key)` plus trigram-spacing analysis printing repeated trigrams with positions. Run it on two keys, print both, and comment which spacing reveals period.",
             patterns=["def ", "return"],
             mapping="Historical cipher, modern lesson: stream ciphers live or die by keystream period discipline.",
         ),
         114: dict(
             topic="Known-plaintext: cribs everywhere",
             idea="Attackers rarely start blind: protocols sprinkle known headers, file formats carry magic numbers, emails open with greetings — every predictable byte is a crib. XOR-based constructions surrender immediately (ciphertext XOR known plaintext = keystream at that position), and even block modes leak equality where cribs align. The demo recovers keystream bytes from a known PNG header XORed against 'ciphertext', then decrypts the remainder honestly. Design lesson: assume attackers know your formats, and choose constructions (randomised encryption, authenticated modes) that stay safe even when they know everything except the key. Kerckhoffs extends to plaintext: only the key is secret, never the message shape. Design protocols assuming full plaintext knowledge; secrecy that needs obscure formats is obscurity, not cryptography. Publish message formats openly and put all secrecy into keys; open formats get reviewed while secret ones rot unexamined.",
             code=(
                 'def xor_bytes(data: bytes, key: bytes) -> bytes:\n'
                 '    return bytes(b ^ key[i % len(key)] for i, b in enumerate(data))\n'
                 '\n'
                 'KEYSTREAM = bytes([0x3A, 0x7F, 0xC2, 0x11, 0x55, 0x08, 0x9E, 0xD0])\n'
                 'plain = b"GET /index.html HTTP/1.0"\n'
                 'cipher = xor_bytes(plain, KEYSTREAM)\n'
                 'known = b"GET /index"\n'
                 'recovered = bytes(c ^ k for c, k in zip(cipher[:len(known)], known))\n'
                 'print("recovered keystream head:", recovered.hex())\n'
                 'print("matches true head:", recovered == KEYSTREAM[:len(known)])\n'
                 'rest = bytes(c ^ recovered[i % len(recovered)] for i, c in enumerate(cipher[len(known):]))\n'
                 'print("tail decrypted with cribs:", rest)'
             ),
             variant_b='crib of wrong content (what does a false crib decrypt into?)',
             variant_c='randomised encryption (why does the same crib fail there?)',
             mistakes=[
                 "Assuming secrecy of message formats ('attackers won't know it's HTTP').",
                 "Deterministic encryption of predictable data (equality plus cribs, double leak).",
                 "Known-answer tests shipped as the only tests (they prove the crib, not the cipher).",
             ],
             qa=(
                 ["How does one known header compromise the whole stream?",
                  "Why does randomised encryption defeat cribs?",
                  "What does Kerckhoffs demand about message shape?"],
                 ["Known plaintext XOR ciphertext yields keystream bytes, which decrypt every other byte masked by the same stream.",
                  "Fresh randomness per message means identical plaintexts encrypt differently — cribs from one message unlock nothing about others.",
                  "That everything except the key is assumed public, including formats, headers and protocols — secrecy must live in keys alone."],
             ),
             homework="Write `crib_recover(cipher, known_prefix)` returning recovered keystream bytes. Run it on two cribbed messages, print both recoveries, and comment why known bytes surrender the stream.",
             patterns=["def ", "return"],
             mapping="BEAST/CRIME-class attacks weaponised predictable plaintext; randomised modes (CBC with IVs, CTR nonces) exist to blunt cribs.",
         ),
         115: dict(
             topic="Stream ciphers honestly: what ChaCha20 promises",
             idea="Modern stream ciphers (ChaCha20, AES-CTR) generate long unpredictable keystreams from short keys plus nonces, then XOR — day 77's atom at production scale, with the keystream generator doing all security work. ChaCha20's design (20 rounds of quarter-round mixing over a 512-bit state) is public, analysed and fast without special hardware; AES-CTR reuses the AES block function as a counter-driven keystream. Neither is implemented here — implementing real ciphers by hand invites side channels and subtle bugs, so production imports audited libraries. What you must carry instead: the API contract (key + unique nonce in, keystream out), the performance story, and the single law both obey — unique nonces, or day 108 returns. Never implement the generator yourself for production; import analysed constructions and spend review effort on nonce management instead. Audit nonce sources with the same rigour as key sources, because a broken nonce breaks the cipher it feeds.",
             code=(
                 'import hashlib\n'
                 '\n'
                 'def model_stream(key: bytes, nonce: bytes, nbytes: int) -> bytes:\n'
                 '    out = b""\n'
                 '    counter = 0\n'
                 '    while len(out) < nbytes:\n'
                 '        out += hashlib.sha256(b"MODEL:" + key + nonce + counter.to_bytes(8, "big")).digest()\n'
                 '        counter += 1\n'
                 '    return out[:nbytes]\n'
                 '\n'
                 's1 = model_stream(b"k", b"n1", 16)\n'
                 's2 = model_stream(b"k", b"n2", 16)\n'
                 's3 = model_stream(b"k", b"n1", 16)\n'
                 'print("same key+nonce deterministic:", s1 == s3)\n'
                 'print("fresh nonce, fresh stream:", s1 != s2)\n'
                 'print("MODEL ONLY: real systems call ChaCha20/AES-CTR from audited libraries")'
             ),
             variant_b='same nonce, longer output (does the stream stay consistent?)',
             variant_c='one-bit key change (avalanche in the generator?)',
             mistakes=[
                 "Hand-rolling 'ChaCha-like' ciphers for production (side channels and subtle breaks await).",
                 "Importing crypto code from blogs instead of audited libraries.",
                 "Confusing the model construction with a real cipher in documentation.",
             ],
             qa=(
                 ["Why must production never hand-roll stream ciphers?",
                  "What contract must any stream cipher API satisfy?",
                  "Why does the demo label itself MODEL ONLY?"],
                 ["Constant-time code, side-channel resistance and cryptanalysis all fail silently in hand-rolled code; audited libraries carry years of hostile review.",
                  "Key plus unique nonce in, arbitrary-length unpredictable keystream out — determinism per pair, uniqueness across pairs.",
                  "Because running it for protection would be malpractice; it teaches the interface shape while real secrecy comes from analysed primitives."],
             ),
             homework="Write `model_stream(key, nonce, nbytes)` over the SHA-256-counter sketch, proving determinism and nonce-sensitivity. Print both facts with a MODEL ONLY banner, and comment which input must stay secret.",
             patterns=["def ", "return"],
             mapping="ChaCha20 (RFC 8439) and AES-CTR via the `cryptography` package; unique nonces remain the single law.",
         ),
         116: dict(
             topic="Small blocks leak: the SWEET32 lesson",
             idea="64-bit block ciphers (3DES, Blowfish) hit birthday collisions after ~2^32 blocks — about 32GB — after which ciphertext blocks repeat and plaintext patterns leak, exactly like ECB at scale. SWEET32 (2016) turned this arithmetic into practical cookie theft against long-lived TLS/ VPN sessions. The demo shows collisions arriving fast in a toy 16-bit block space, then states the rule as law: 128-bit blocks (AES, ChaCha20's 512-bit state) for everything new, 3DES relegated to decrypting history. Block size is a security parameter, not an implementation detail — audit it wherever legacy ciphers linger. Schedule rekeying intervals from birthday math, not from calendar habit; sessions outliving bounds get fresh keys automatically. Automate rotation triggers on byte counts rather than hoping operators watch calendars correctly. Log rotation events with old and new key identifiers so audits trace every active key to its birth. Rotation drills belong in game days, not in incident response, because untested rotation fails exactly when most needed.",
             code=(
                 'seen, trials = {}, 0\n'
                 'n = 0\n'
                 'while True:\n'
                 '    block = (n * 2654435761) % 65536\n'
                 '    trials += 1\n'
                 '    if block in seen:\n'
                 '        break\n'
                 '    seen[block] = n\n'
                 '    n += 1\n'
                 '    assert trials < 100000, "16-bit space must collide fast"\n'
                 'print("first block repeat after", trials, "blocks (sqrt(65536) ~= 256 scale)")\n'
                 'print("at 2^32 blocks, 64-bit ciphers repeat: SWEET32 in miniature")'
             ),
             variant_b='32-bit space mental model (how many blocks to repeats?)',
             variant_c='session rekeying every 1GB (does rotation dodge the birthday?)',
             mistakes=[
                 "3DES 'still fine for low-value data' (birthday math does not discount by value).",
                 "Long-lived VPN sessions without rekeying on legacy ciphers.",
                 "Confusing key size with block size (112-bit 3DES keys, 64-bit blocks — the blocks fail first).",
             ],
             qa=(
                 ["Why do 64-bit blocks fail around 2^32 blocks?",
                  "Why does rekeying dodge the birthday?",
                  "Key size vs block size: which fails first for 3DES?"],
                 ["Birthday collisions arrive at square-root scale: 2^32 blocks into 64-bit space repeats a block with high probability, leaking equality patterns.",
                  "Fresh keys reset the collision count to zero; rotation keeps every key's block count below the birthday bound.",
                  "Blocks: 64-bit blocks collide at 2^32 while 112-bit keys need 2^112 work — the geometry fails eons before the key does."],
             ),
             homework="Write `collision_trials(bits)` for a toy block space, printing trials to first repeat. Run it for 12 and 16 bits, print both, and comment how block size sets session limits.",
             patterns=["while ", "assert "],
             mapping="AES-128 blocks retire the issue; audits flag 3DES/Blowfish with rekey-or-replace orders.",
         ),
         117: dict(
             topic="Project: classical cryptanalysis toolkit",
             idea="Today's project assembles the phase into one authorized-lab toolkit: Caesar brute-forcer with English scoring, frequency-rank substitution solver, Vigenere period estimator via trigram spacings, and an ECB-duplicate detector over block lists — each function pure, tested and labelled TEACHING. Run the toolkit against three challenge ciphertexts (provided in homework variants) and report method plus recovered plaintext per challenge. The deliverable is process: a lab report naming which attack fits which structure, with honest scope notes (classical only, modern ciphers untouched). Projects integrate; this one integrates every classical attack into one bench. Scope notes ride with every tool release so lab instruments never wander into unauthorised traffic. Lab tools carry scope banners in output so screenshots prove authorisation boundaries were respected.",
             code=(
                 'import string\n'
                 '\n'
                 'ALPHA = string.ascii_lowercase\n'
                 '\n'
                 'def caesar_best(cipher: str) -> tuple:\n'
                 '    common = set("etaoin")\n'
                 '    best, bestkey = "", 0\n'
                 '    for key in range(26):\n'
                 '        guess = "".join(chr((ord(c) - 97 - key) % 26 + 97) if c in ALPHA else c for c in cipher.lower())\n'
                 '        letters = [c for c in guess if c in ALPHA]\n'
                 '        score = sum(1 for c in letters[:30] if c in common)\n'
                 '        if score > sum(1 for c in best[:30] if c in common):\n'
                 '            best, bestkey = guess, key\n'
                 '    return bestkey, best\n'
                 '\n'
                 'key, plain = caesar_best("wkh txlfne exw irzq")\n'
                 'print("best key:", key, "| recovered:", plain)\n'
                 'print("toolkit method 1/4: brute force with scoring")'
             ),
             variant_b='a Vigenere challenge under key "key" (which toolkit method fits?)',
             variant_c='an ECB block list with duplicates (which method, and what does it recover?)',
             mistakes=[
                 "Pointing classical tools at modern ciphertext (category error, wasted effort).",
                 "Unscored brute force (26 rows nobody reads).",
                 "Toolkit without scope notes, inviting misuse on real traffic.",
             ],
             qa=(
                 ["Why score brute-force candidates instead of printing all 26?",
                  "How do you choose the method per challenge?",
                  "What belongs in the scope notes?"],
                 ["Scoring ranks candidates so the tool reports an answer; raw dumps push the analysis back onto human eyes for every message.",
                  "Keyspace size (brute force), fingerprint survival (frequency), period hints (Kasiski), block repeats (ECB) — structure selects method.",
                  "Classical-only applicability, modern-cipher immunity, and authorized-lab boundaries — what it breaks, what it cannot touch, where it may run."],
             ),
             homework="Write `caesar_best(cipher)` scoring 26 shifts by common-letter counts and returning best key plus plaintext. Run it on two challenges, print both recoveries, and comment which line scores Englishness.",
             patterns=["def ", "return"],
             mapping="Lab cryptanalysis benches package these four methods; production cryptanalysis starts where they stop.",
         ),
         118: dict(
             topic="Testing cipher code with asserts",
             idea="Cipher-test discipline: round-trips (decrypt(encrypt(x)) == x on varied inputs), determinism (same key, same output, twice), avalanche smoke for hashes nearby, refusal cases (short pads assert, malformed armour returns None), and known-answer vectors for real primitives (SHA-256 'abc' vector from day 103). Assert contracts, never live ciphertexts — random nonces make exact outputs unrepeatable by design, so tests assert properties (lengths, round-trips, inequality across nonces) instead of values. A cipher helper whose tests pin exact outputs is testing its test data; one asserting properties is testing its contract. These guards wrap every teaching cipher hereafter. Property tests outlive exact-output tests because they survive every legitimate change to nonces and randomness. Exact-output tests belong only to deterministic vectors from published standards. Property tests cover everything randomness touches; vectors cover everything determinism promises. Keep vectors beside the code they guard and re-run them in CI, since drift between code and vectors means one of them is lying. Treat vector failures as stop-the-line events, never as flaky tests to retry.",
             code=(
                 'import hashlib\n'
                 '\n'
                 'def xor_bytes(data: bytes, key: bytes) -> bytes:\n'
                 '    assert key, "empty key encrypts nothing"\n'
                 '    return bytes(b ^ key[i % len(key)] for i, b in enumerate(data))\n'
                 '\n'
                 'k = bytes([0x3A, 0x7F])\n'
                 'assert xor_bytes(xor_bytes(b"round trip!", k), k) == b"round trip!"\n'
                 'assert xor_bytes(b"a", k) != xor_bytes(b"b", k)\n'
                 'assert hashlib.sha256(b"abc").hexdigest().startswith("ba7816bf")\n'
                 'print("contracts hold: round-trips, sensitivity, vectors")'
             ),
             variant_b='empty key (which assert fires, and is refusal correct?)',
             variant_c='empty message (does the round-trip hold vacuously?)',
             mistakes=[
                 "Exact-ciphertext asserts that break on every fresh nonce.",
                 "No round-trip tests, so encrypt/decrypt drift apart silently.",
                 "Real-primitive vectors skipped because 'library code is tested' (integration still needs proving).",
             ],
             qa=(
                 ["Why do nonce-using ciphers forbid exact-output asserts?",
                  "Why test empty messages explicitly?",
                  "What do vectors prove that round-trips cannot?"],
                 ["Fresh nonces make every output legitimately different; exact asserts would fail correct code, so properties (lengths, inequalities) replace values.",
                  "Empty inputs expose off-by-one and division-by-zero paths that normal cases never touch — vacuous truth must still be correct truth.",
                  "Conformance to the standard: round-trips pass for any self-consistent (even wrong) algorithm, while vectors anchor to independent truth."],
             ),
             homework="Write round-trip plus determinism asserts for xor_bytes and one SHA-256 vector check. Run them, print confirmation, and comment which assert would catch a broken inverse.",
             patterns=["assert ", "sha256("],
             mapping="Known-answer tests (NIST vectors) plus property tests (round-trips, contracts) guard every primitive integration.",
         ),
         119: dict(
             topic="Phase review: symmetric ciphers",
             idea="Rebuild from memory: Caesar keyspaces, frequency fingerprints, ECB equality leaks, crib-dragging automation, chaining state, encrypt-then-MAC order, nonce uniqueness laws, key-size arithmetic, Vigenere periods, known-plaintext cribs, honest stream models, SWEET32 birthdays. Close the notes and reproduce the XOR round-trip plus the crib-drag scorer — symmetry demonstrated, reuse punished. The missing line is tomorrow's first job; public-key thinking (phase 4) assumes shared secrets as solved infrastructure and asks what two strangers can do without one. If the rebuild flows with TEACHING labels intact, symmetric honesty is installed. Carry the three laws into phase 4 visibly: unique nonces, verify-before-decrypt, and honest labels on every construction you will ever review. Carry three laws forward: unique nonces, verify-before-decrypt, and TEACHING labels on every toy construction. Labels are the honesty mechanism; a rebuild that drops them memorised code while forgetting the safety contract.",
             code=(
                 'def xor_bytes(data: bytes, key: bytes) -> bytes:\n'
                 '    return bytes(b ^ key[i % len(key)] for i, b in enumerate(data))\n'
                 '\n'
                 'k = bytes([0x3A, 0x7F, 0xC2])\n'
                 'msg = b"review time"\n'
                 'assert xor_bytes(xor_bytes(msg, k), k) == msg\n'
                 'print("round-trip from memory: proven")\n'
                 'c1 = xor_bytes(b"attack at dawn!", k * 5)\n'
                 'c2 = xor_bytes(b"retreat now!!!", k * 5)\n'
                 'print("reuse visible:", bytes(a ^ b for a, b in zip(c1, c2)).hex()[:24], "...")\n'
                 'print("labels intact: teaching cipher, unique nonces, MACs on ciphertext")'
             ),
             variant_b='a fresh nonce per message (what changes in the reuse line?)',
             variant_c='HMAC tag added (which order, and why that order?)',
             mistakes=[
                 "Rebuilding with notes open — retrieval is the learning.",
                 "Reciting nonce laws without placing one in a running script.",
                 "Dropping TEACHING labels in the rebuild (labels are part of the lesson).",
             ],
             qa=(
                 ["What single rebuild proves this phase stuck?",
                  "Why must TEACHING labels survive the rebuild?",
                  "What does the reuse line demonstrate?"],
                 ["XOR round-trip plus crib-drag scorer from memory — symmetry demonstrated, keystream reuse punished, no notes.",
                  "Labels are the honesty mechanism; a rebuild that drops them memorised code while forgetting the safety contract. Recite the three laws before every cipher review until they precede thought rather than follow it. A review that starts with the three laws catches unsafe orders, reused nonces and missing labels before reading any further. Close every review by confirming the three laws hold for the code under examination. Unsigned checklists prove nothing; verified laws prove everything.",
                  "That shared keystreams cancel visibly, turning two ciphertexts into a language puzzle — the law, demonstrated, not stated."],
             ),
             homework="Write `phase_recap()` from memory: XOR round-trip assert plus reuse-visibility print. Run it, print the verdict, and comment which line you had to look up.",
             patterns=["def ", "assert "],
             mapping="Phase 4 keeps XOR discipline and asks the two-stranger question; shared secrets become the solved past.",
         ),
     }),
    ("Public Keys and Signatures",
     "Two strangers, no shared secret: toy RSA and Diffie-Hellman for intuition, signatures and certificates for trust. All number theory here is TEACHING-SCALE; production uses 2048+ bit keys from audited libraries.",
     {
         120: dict(
             topic="The two-stranger problem",
             idea="Symmetric crypto assumes a shared secret, but strangers share nothing: how do two parties who never met agree on a key over a wiretap, or verify a message's author without prior contact? Public-key cryptography splits keys into public halves (shared freely) and private halves (guarded absolutely), solving key distribution and adding signatures — origin proof no symmetric tool provides. The demo shows the problem concretely: symmetric sealing works only after manual key delivery, which begs the question it pretends to solve. Everything in this phase answers that question two ways: encrypt to public keys, sign with private ones. Name which power each lesson uses before touching any key material, since confused purposes breed cross-protocol attacks. Document which key does what beside every key listing, since purpose confusion enables the cross-protocol attacks that break otherwise sound deployments.",
             code=(
                 'import hashlib\n'
                 'import hmac\n'
                 '\n'
                 'SHARED = bytes([0x2B, 0x7E])\n'
                 '\n'
                 'def seal(plain: bytes) -> bytes:\n'
                 '    return bytes(b ^ SHARED[i % len(SHARED)] for i, b in enumerate(plain))\n'
                 '\n'
                 'print("strangers hold no shared secret: who delivers the key?")\n'
                 'print("over a wiretap, delivery IS the attack surface")\n'
                 'print("public keys: share freely | private keys: guard absolutely")\n'
                 'print("sealed demo:", seal(b"hello").hex(), "(symmetric works only post-delivery)")'
             ),
             variant_b='a courier carrying the key (what can go wrong in transit?)',
             variant_c='a public bulletin board (what may be posted there safely?)',
             mistakes=[
                 "Assuming prior contact exists because 'we emailed first' (email is the wiretap).",
                 "Public keys kept secret (harmless but pointless) while private keys leak (fatal).",
                 "Signatures expected from symmetric tools (symmetric proves nothing about origin).",
             ],
             qa=(
                 ["Why can't symmetric crypto onboard strangers?",
                  "What two new powers do split keys add?",
                  "Why is key delivery over a wiretap self-defeating?"],
                 ["It assumes the secret it should establish; delivery becomes the attack surface, and the cipher protects nothing during setup.",
                  "Key agreement without prior secrets, plus signatures proving authorship — neither expressible with one shared secret.",
                  "The wiretap copies whatever crosses it, so delivered keys arrive already compromised; strangers need math, not couriers."],
             ),
             homework="Write `problem_demo()` printing why symmetric sealing needs prior delivery plus the public/private split. Run it, print the statement, and comment which sentence names the circularity.",
             patterns=["def ", "print("],
             mapping="Diffie-Hellman (key agreement) and RSA/signatures (authorship) answer the two-stranger question from opposite sides.",
         ),
         121: dict(
             topic="Modular arithmetic: clock math",
             idea="Public-key math lives on clocks: modulo n arithmetic wraps numbers around, so 7 + 6 = 1 (mod 12), and exponentiation cycles with periods dividing phi(n). These cycles create trapdoors — easy forward (multiply, exponentiate), hard backward (logarithms, roots) without secret knowledge — on which RSA and Diffie-Hellman stand. The demo builds intuition on small moduli: powers cycling, inverses existing only for coprimes, Fermat's little theorem verified live (a^(p-1) = 1 mod p for prime p). No security claims at toy sizes; the arithmetic is identical at 2048 bits, only the work factors change from trivial to absurd.",
             code=(
                 'def modpow(base: int, exp: int, mod: int) -> int:\n'
                 '    return pow(base, exp, mod)\n'
                 '\n'
                 'print("clock: (7 + 6) mod 12 =", (7 + 6) % 12)\n'
                 'print("powers of 3 mod 11:", [modpow(3, e, 11) for e in range(1, 7)])\n'
                 'print("fermat check 2^10 mod 11 =", modpow(2, 10, 11), "(prime p: always 1)")\n'
                 'print("inverse of 3 mod 11:", pow(3, -1, 11), "| 7 has none mod 12 (not coprime)")\n'
                 'try:\n'
                 '    pow(7, -1, 12)\n'
                 'except ValueError as exc:\n'
                 '    print("non-coprime inverse correctly refuses:", exc)'
             ),
             variant_b='powers of 2 mod 11 (full cycle length? primitive root?)',
             variant_c='mod 12 powers (where do cycles break down?)',
             mistakes=[
                 "Assuming inverses always exist (coprimality is the precondition).",
                 "Confusing modpow speed with security (fast math is the point; hardness lives in inversion).",
                 "Toy moduli mistaken for toy security claims (arithmetic same, work factors differ).",
             ],
             qa=(
                 ["Why do cycles in modular exponentiation matter for crypto?",
                  "When does a modular inverse fail to exist?",
                  "What does Fermat's check demonstrate?"],
                 ["Cycles create predictable structure (periods) that trapdoors exploit: easy to ride forward with secrets, hard to reverse without them.",
                  "Exactly when base and modulus share a factor — inverses need coprimality, and RSA keygen enforces it by construction.",
                  "That prime moduli give every non-zero element order dividing p-1 — the regularity Diffie-Hellman tunes into shared secrets."],
             ),
             homework="Write `clock_demo(p)` printing a power cycle plus Fermat check for prime p. Run it on p=11 and p=13, print both cycles, and comment which line needs primality.",
             patterns=["def ", "return"],
             mapping="pow(base, exp, mod) is the workhorse under RSA, Diffie-Hellman and elliptic curves alike.",
         ),
         122: dict(
             topic="Toy RSA: encrypt with strangers",
             idea="RSA multiplies two primes (n = p·q), publishes (n, e) and guards d where e·d ≡ 1 mod phi(n): anyone encrypts with the public half (m^e mod n), only the private holder decrypts (c^d mod n). The demo runs real RSA arithmetic at TEACHING SCALE (p=61, q=53 — factorable by hand, stated loudly), encrypting a small number and recovering it, proving the asymmetric round-trip works. Production demands 2048+ bits, random primes, OAEP padding and audited libraries — textbook RSA on small numbers is malleable and unpadded, so this day teaches the mechanism while forbidding the deployment. Mechanism here, armour in libraries. Rehearse the deployment forbiddens aloud with every teaching demo so the boundary survives contact with real code. Stamp TEACHING banners into example filenames as well, so copied snippets carry their warnings wherever they travel.",
             code=(
                 '# TEACHING-SCALE RSA (p=61, q=53): mechanism only, NEVER deployable\n'
                 'p, q = 61, 53\n'
                 'n = p * q\n'
                 'phi = (p - 1) * (q - 1)\n'
                 'e = 17\n'
                 'd = pow(e, -1, phi)\n'
                 'print(f"public: (n={n}, e={e}) | private d={d} (guarded)")\n'
                 'm = 42\n'
                 'c = pow(m, e, n)\n'
                 'print("encrypt 42 ->", c)\n'
                 'print("decrypt   ->", pow(c, d, n))\n'
                 'print("round-trip works; 3233 factors by hand, so this protects nothing")'
             ),
             variant_b='m = 3232 (edge of the message space — what breaks past n?)',
             variant_c='e = 3 (tiny exponent: faster, and what new fragility?)',
             mistakes=[
                 "Deploying textbook RSA without padding (malleability: c·2^e decrypts to 2m).",
                 "Small primes anywhere near production (factorable by hand, let alone machines).",
                 "Same key for encryption and signing (cross-protocol attacks between uses).",
             ],
             qa=(
                 ["Why does RSA need the private exponent kept secret while e publishes?",
                  "Why is textbook RSA undeployable despite correct arithmetic?",
                  "What breaks when messages reach n in size?"],
                 ["Anyone with d (or the factors enabling d) decrypts everything and forges signatures; e encrypts only, which is safe to share.",
                  "No padding means malleability and determinism: attackers reshape ciphertexts into predictable plaintext changes and test guesses directly.",
                  "RSA permutes 0..n-1 only; larger messages need hybrid encryption (random key by RSA, bulk by AES) — the standard construction."],
             ),
             homework="Write `toy_rsa(p, q, e, m)` returning (n, ciphertext, recovered) with asserts on round-trip. Run it on two prime pairs, print both, and comment which value must never publish.",
             patterns=["def ", "return"],
             mapping="Production RSA: 2048+ bits, OAEP padding, hybrid encryption, audited libraries — mechanism here, armour there.",
         ),
         123: dict(
             topic="Signatures: authorship proof",
             idea="Signatures invert RSA's direction: hash the message, 'decrypt' the digest with the private key, and anyone verifies with the public half — proving authorship plus integrity, since only the key-holder could produce it. Verification needs the trusted public key (distribution problem returns: trust the key, trust the signature), the full message (detached signatures travel beside data), and a collision-resistant hash (forgery via colliding meanings otherwise). The demo signs with toy RSA (TEACHING SCALE) and verifies honestly, including a tamper case that fails. Non-repudiation follows when keys are truly private: the signer cannot later deny what only their key could make. Guard private keys with the paranoia signatures deserve: offline where possible, passphrase-wrapped always, never in repositories. Scan repositories for private key headers on every commit hook, because one committed key compromises every signature it ever made.",
             code=(
                 '# TEACHING-SCALE signatures (toy RSA): mechanism only\n'
                 'import hashlib\n'
                 '\n'
                 'p, q, e = 61, 53, 17\n'
                 'n = p * q\n'
                 'd = pow(e, -1, (p - 1) * (q - 1))\n'
                 '\n'
                 'def toy_sign(msg: bytes) -> int:\n'
                 '    digest = int(hashlib.sha256(msg).hexdigest(), 16) % n\n'
                 '    return pow(digest, d, n)\n'
                 '\n'
                 'def toy_verify(msg: bytes, sig: int) -> bool:\n'
                 '    digest = int(hashlib.sha256(msg).hexdigest(), 16) % n\n'
                 '    return pow(sig, e, n) == digest\n'
                 '\n'
                 'sig = toy_sign(b"pay 100")\n'
                 'print("valid:  ", toy_verify(b"pay 100", sig))\n'
                 'print("tampered:", toy_verify(b"pay 900", sig))\n'
                 'print("authorship + integrity from one private operation")'
             ),
             variant_b='signing the raw message instead of its hash (what breaks at scale?)',
             variant_c='a signature transplanted onto another message (which check fails?)',
             mistakes=[
                 "Verifying with an untrusted key (signature math cannot fix key trust).",
                 "Textbook-RSA signatures without PSS padding in production (forgery classes await).",
                 "Concluding non-repudiation from shared-key MACs (both sides forge — no third-party proof).",
             ],
             qa=(
                 ["Why sign the hash rather than the message?",
                  "Why can't MACs give non-repudiation?",
                  "What must be trusted before a valid signature means anything?"],
                 ["RSA permutes fixed-size blocks; hashing compresses arbitrary messages to size while binding every bit — sign-then-verify stays constant-cost.",
                  "Both key-holders forge MACs identically, so no judge can tell who tagged what; asymmetric keys separate forging power from checking power.",
                  "The claimed public key's binding to its owner — math verifies keys match, only key distribution (certificates, TOFU) binds keys to people."],
             ),
             homework="Write `toy_sign(msg)`/`toy_verify(msg, sig)` with SHA-256 reduction, proving valid-accept and tamper-reject. Print both verdicts with a TEACHING banner, and comment which operation needs the private key.",
             patterns=["def ", "return"],
             mapping="RSA-PSS/ECDSA/Ed25519 with SHA-256 in audited libraries; certificates solve the key-trust problem next.",
         ),
         124: dict(
             topic="Diffie-Hellman: agreeing in public",
             idea="Diffie-Hellman lets strangers agree on a secret over a wiretap: agree on public (prime p, generator g), each picks a private exponent, exchange g^private mod p publicly, and both compute the same shared secret because (g^a)^b = (g^b)^a — while eavesdroppers face the discrete logarithm to recover either private. The demo runs the full exchange with TEACHING-SCALE numbers and a simulated wiretapper who sees everything public yet cannot divide the secret out. No authentication yet — tomorrow's person-in-the-middle shows why unauthenticated agreement is agreement with whoever answers. Secrets agreed, identities unverified: half the problem solved, honestly labelled. Celebrate agreement protocols for what they achieve while naming the missing authentication explicitly every time. Agreement without identity suits only closed systems where participants are provisioned out of band. Closed systems still need key lifecycle management, since provisioned secrets age, leak and require rotation like any others.",
             code=(
                 '# TEACHING-SCALE Diffie-Hellman (p=23): arithmetic only\n'
                 'p, g = 23, 5\n'
                 'a_private, b_private = 6, 15\n'
                 'A_public = pow(g, a_private, p)\n'
                 'B_public = pow(g, b_private, p)\n'
                 'print("public exchange:", A_public, B_public, "(wiretapper sees both)")\n'
                 's_ada = pow(B_public, a_private, p)\n'
                 's_bor = pow(A_public, b_private, p)\n'
                 'print("ada computes:", s_ada, "| bor computes:", s_bor)\n'
                 'print("agreement:", s_ada == s_bor, "| wiretapper derives: nothing usable")'
             ),
             variant_b='p=23, g=7 (does any generator work, or must it generate well?)',
             variant_c='private exponents 1 and 2 (degenerate secrets — what must implementations reject?)',
             mistakes=[
                 "Unauthenticated DH deployed as if agreement implied identity (MITM tomorrow).",
                 "Tiny or non-prime moduli (discrete logs become easy homework).",
                 "Reusing ephemeral exponents across sessions (forward secrecy dies with the first leak).",
             ],
             qa=(
                 ["Why can't the wiretapper combine the public values into the secret?",
                  "What does each side contribute that the wiretap lacks?",
                  "Why must exponents avoid 0 and 1?"],
                 ["Combining needs discrete logarithms (recover a from g^a) — easy forward, infeasible backward at real sizes with proper groups.",
                  "A private exponent: each side raises the other's public value by a secret power the wiretap never sees.",
                  "They yield degenerate secrets (1, g) shared with everyone computing trivially — implementations must reject small-subgroup values."],
             ),
             homework="Write the DH exchange with fixed teaching parameters, asserting both sides agree. Run it on two exponent pairs, print both agreements, and comment what the wiretapper cannot compute.",
             patterns=["pow(", "def "],
             mapping="ECDH (elliptic-curve, ephemeral) in TLS 1.3 handshakes; finite-field DH survives only in vetted groups with validation.",
         ),
         125: dict(
             topic="Person in the middle",
             idea="Unauthenticated key exchange agrees with whoever answers: Mallory intercepts both directions, completes DH with Ada (posing as Bor) and with Bor (posing as Ada), then relays and reads everything — both victims see a working encrypted channel. The demo stages the full attack on teaching numbers, printing both victims' confidence beside Mallory's transcript. The defence is authentication, not stronger math: signed exchanges (Bor's signature on his DH value, verified against a trusted key), certificates binding keys to names, or pre-shared authenticators. Encryption without identity protects conversations with attackers most diligently of all. Ask 'with whom?' before 'how strongly?' for every encrypted channel under review. Unauthenticated encryption answers availability questions while leaving authorship entirely open to whoever answers first. Document the authorship gap in every unauthenticated design review so the missing control stays visible instead of forgotten.",
             code=(
                 '# TEACHING-SCALE MITM demo (p=23): why authentication matters\n'
                 'p, g = 23, 5\n'
                 'a_priv, b_priv, m1_priv, m2_priv = 6, 15, 3, 9\n'
                 'A_pub = pow(g, a_priv, p)\n'
                 'B_pub = pow(g, b_priv, p)\n'
                 'M1_pub, M2_pub = pow(g, m1_priv, p), pow(g, m2_priv, p)\n'
                 'ada_secret = pow(M2_pub, a_priv, p)\n'
                 'bor_secret = pow(M1_pub, b_priv, p)\n'
                 'mallory_reads_ada = pow(A_pub, m2_priv, p)\n'
                 'mallory_reads_bor = pow(B_pub, m1_priv, p)\n'
                 'print("ada<->mallory secret:", ada_secret, "| mallory reads ada:", mallory_reads_ada)\n'
                 'print("bor<->mallory secret:", bor_secret, "| mallory reads bor:", mallory_reads_bor)\n'
                 'print("both victims confident, both relayed: authentication missing")'
             ),
             variant_b='victims comparing secrets over the channel (would they detect Mallory?)',
             variant_c='one side requiring signatures (which half of the attack dies?)',
             mistakes=[
                 "'Encrypted, therefore safe' thinking without asking 'with whom?'.",
                 "Self-signed assertions accepted as identity (anyone asserts anything).",
                 "MITM dismissed as 'needs network position' (public Wi-Fi, BGP, malware say otherwise).",
             ],
             qa=(
                 ["Why do both victims believe the exchange succeeded?",
                  "What exactly would signatures change?",
                  "Why doesn't stronger DH math stop Mallory?"],
                 ["Every message decrypts correctly on each leg — the attack preserves functionality perfectly while owning both keys.",
                  "Forging Bor's leg would require his private signing key; Mallory's substituted values fail verification and the attack surfaces.",
                  "Math was never the weakness: Mallory does valid DH twice. Only identity binding distinguishes Bor's values from hers."],
             ),
             homework="Write the three-party MITM exchange proving both victims agree with Mallory. Print both leg secrets plus Mallory's copies, and comment which missing piece enables it.",
             patterns=["pow(", "def "],
             mapping="Authenticated DH (signatures, certificates, PAKEs); TLS without certificate checks is this demo on production ports.",
         ),
         126: dict(
             topic="Forward secrecy: burn after reading",
             idea="Long-term keys that decrypt past traffic turn one future compromise into retroactive transparency: seize today's server key, read last year's intercepts. Ephemeral Diffie-Hellman (fresh exponents per session, deleted after) bounds every breach to its own session — past traffic stays dark because its keys no longer exist anywhere. The demo contrasts static-secret reuse (one leak decrypts two sessions) against ephemeral freshness (each session independent), printing what a stolen key unlocks in each design. TLS 1.3 made ephemerality mandatory precisely because key theft went from hypothetical to routine compromise; design as if long-term secrets eventually leak, because they do. Assume breach timelines in years, not days, when setting rotation policy. Short session lifetimes shrink retroactive exposure the same way, so prefer brief sessions alongside deletable keys. Prefer session lifetimes measured in minutes for sensitive operations, shrinking the window where a stolen secret retains value.",
             code=(
                 '# Static vs ephemeral session secrets (teaching numbers)\n'
                 'static_secret = 14\n'
                 'sessions_static = [("s1", static_secret), ("s2", static_secret)]\n'
                 'sessions_fresh = [("s1", 14), ("s2", 9)]\n'
                 '\n'
                 'def unlocked(sessions, stolen):\n'
                 '    return [name for name, s in sessions if s == stolen]\n'
                 '\n'
                 'print("static design, key leaks: unlocks", unlocked(sessions_static, 14))\n'
                 'print("fresh design, one key leaks: unlocks", unlocked(sessions_fresh, 14))\n'
                 'print("ephemerality bounds every breach to its own session")'
             ),
             variant_b='three sessions under static (how does the blast radius grow?)',
             variant_c='stolen key from a deleted session (what remains recoverable?)',
             mistakes=[
                 "Static RSA key exchange kept for 'compatibility' (decrypt-later harvest).",
                 "Ephemeral exponents logged for debugging, recreating the static problem.",
                 "Forward secrecy claimed without deleting anything (marketing, not mechanism).",
             ],
             qa=(
                 ["Why does one static-key leak decrypt years of traffic?",
                  "What must actually be deleted for ephemerality to hold?",
                  "Why did TLS 1.3 remove static key exchange?"],
                 ["Every session's secrecy reduces to the same key, so its compromise unlocks the entire archive at once — retroactive transparency.",
                  "Ephemeral private exponents and derived session keys after use; anything retained (logs, debugs, backups) re-creates the static failure.",
                  "Because harvest-now-decrypt-later made static keys a standing retroactive threat; mandatory ephemerality bounds every breach to its session."],
             ),
             homework="Write `unlocked(sessions, stolen)` listing sessions a leaked key opens under static vs fresh designs. Run it on two session sets, print both blast radii, and comment which design bounds breaches.",
             patterns=["def ", "return"],
             mapping="TLS 1.3 (ephemeral-only), Signal's double ratchet (per-message freshness); static keys decrypt history wherever they persist.",
         ),
         127: dict(
             topic="Key sizes that survive contact",
             idea="Public-key sizes live under different arithmetic than symmetric ones: RSA-2048 offers ~112 bits of classical strength (factoring is sub-exponential, not exponential), ECC-256 matches it via harder discrete logs in smaller packages, and Shor's algorithm breaks both outright on a sufficient quantum computer. The demo prices factoring-scale growth across toy moduli (timing trial division as digits grow) to feel sub-exponential pain, then states deployment rules: RSA ≥2048, ECC ≥256 (P-256/Curve25519), DH in vetted groups only, and hybrid post-quantum pilots where data outlives the migration horizon. Numbers, not adjectives — key sizes are budgets against dated threats. Revisit key sizes on a calendar schedule because factoring and quantum timelines move only in one direction. Budget migrations before deadlines arrive, since rushed algorithm transitions introduce the implementation flaws haste always brings. Start migrations with hybrid deployments that combine old and new algorithms during transition windows.",
             code=(
                 'import math\n'
                 '\n'
                 'def trial_divisions(n: int) -> int:\n'
                 '    count, f = 0, 2\n'
                 '    while f * f <= n:\n'
                 '        count += 1\n'
                 '        if n % f == 0:\n'
                 '            return count\n'
                 '        f += 1 if f == 2 else 2\n'
                 '    return count\n'
                 '\n'
                 'for digits in (6, 9, 12):\n'
                 '    n = 10 ** digits + 39\n'
                 '    print(f"{digits}-digit n: first factor after {trial_divisions(n)} trial divisions")\n'
                 'print("divisions explode with digits: use 2048+ bits in production")'
             ),
             variant_b='even vs odd composites (which fall instantly, and why?)',
             variant_c='a prime input (how does trial division prove primality slowly?)',
             mistakes=[
                 "1024-bit RSA for new systems ('faster' today, factorable tomorrow).",
                 "ECC dismissed as 'weaker-looking' despite equivalent strength per the analysis.",
                 "Ignoring harvest-now-decrypt-later for long-lived confidential data.",
             ],
             qa=(
                 ["Why do RSA keys need 2048 bits when AES needs 128?",
                  "Why does trial division mislead about real factoring difficulty?",
                  "What should long-lived data assume about quantum timelines?"],
                 ["Factoring runs sub-exponentially (NFS), not exponentially — RSA needs extra width to buy equivalent work against smarter-than-brute-force math.",
                  "It is the dumbest method; real attackers run sieves enormously faster, so toy timings understate the threat by orders of magnitude.",
                  "That harvests happen now and decryption later: encrypt long-lived secrets under post-quantum-hybrid schemes where policy requires it."],
             ),
             homework="Write `trial_divisions(n)` counting divisions to first factor across digit sizes. Run it on three sizes, print the scaling wall, and comment why production needs 2048+ bits.",
             patterns=["def ", "return"],
             mapping="RSA-2048+/ECC-256 minimums; NIST post-quantum standards (ML-KEM) for harvest-sensitive data.",
         ),
         128: dict(
             topic="Hybrid encryption: best of both",
             idea="Public-key operations are slow and size-limited, symmetric ones fast and unbounded — hybrid encryption combines them: generate a random data key, encrypt the bulk with AES-style symmetric cipher, encrypt the small data key to the recipient's public key. Every real encrypted email, file share and TLS session runs this shape. The demo models it honestly with teaching pieces (XOR bulk + toy-RSA-wrapped data key), printing each layer's role, and states the production mapping explicitly (RSA-OAEP or ECDH for the key, AES-GCM for bulk). Hybrid is not a compromise between two systems; it is each system doing exactly what it does best.",
             code=(
                 '# Hybrid shape: slow asymmetric wraps key, fast symmetric moves bulk (TEACHING PIECES)\n'
                 'p, q, e = 61, 53, 17\n'
                 'n = p * q\n'
                 'd = pow(e, -1, (p - 1) * (q - 1))\n'
                 '\n'
                 'def xor_bytes(data: bytes, key: bytes) -> bytes:\n'
                 '    return bytes(b ^ key[i % len(key)] for i, b in enumerate(data))\n'
                 '\n'
                 'data_key = bytes([0x07])\n'
                 'bulk = xor_bytes(b"large payload here!!", data_key)\n'
                 'wrapped = pow(data_key[0], e, n)\n'
                 'print("bulk bytes:", len(bulk), "| wrapped key int:", wrapped)\n'
                 'open_key = pow(wrapped, d, n).to_bytes(1, "big")\n'
                 'print("unwrapped matches:", open_key == data_key)\n'
                 'print("recovered bulk:", xor_bytes(bulk, open_key))\n'
                 'print("hybrid: asymmetric for keys, symmetric for bulk")'
             ),
             variant_b='a 40-byte bulk message (which layer scales, which stays constant?)',
             variant_c='data key of 2 bytes (what breaks in the toy wrap?)',
             mistakes=[
                 "RSA-encrypting bulk data directly (size limits plus malleability).",
                 "Reusing one data key across recipients (one compromise opens every copy).",
                 "Skipping authentication on either layer (hybrid needs MACs too).",
             ],
             qa=(
                 ["Why not encrypt bulk data directly with RSA?",
                  "Why generate a fresh data key per message?",
                  "What must authentication cover in a hybrid message?"],
                 ["Size limits (RSA permutes numbers below n) plus malleability plus slowness — bulk belongs to symmetric ciphers by every measure.",
                  "Compromise then opens one message, not the archive; fresh keys compartmentalise every breach to its own ciphertext.",
                  "Both layers: the wrapped key (else attackers substitute keys) and the bulk (else content forges) — GCM-style combined modes do both."],
             ),
             homework="Write hybrid seal/open with toy-RSA-wrapped data key plus XOR bulk, proving round-trip. Print layer sizes, run on two messages, and comment which layer scales with data.",
             patterns=["def ", "return"],
             mapping="PGP/GPG, S/MIME and TLS all run hybrid: RSA-OAEP/ECDH wraps, AES-GCM moves bulk.",
         ),
         129: dict(
             topic="Certificates bind keys to names",
             idea="A public key alone claims nothing about ownership — certificates bind keys to identities by having a trusted authority sign the (name, key, validity) tuple. Verification walks the chain (leaf → intermediate → root), checks every signature, validity window and revocation status, and pins trust only in pre-installed roots. The demo models a tiny chain as signed dicts with teaching-RSA signatures, verifying honestly and rejecting an expired leaf and a wrong-issuer chain. Real X.509 adds extensions, constraints and revocation protocols, but the trust logic is identical: signatures bind, chains delegate, roots anchor — and every link is ideology-free arithmetic.",
             code=(
                 '# Toy certificate chain (teaching RSA signatures, small numbers)\n'
                 'import hashlib\n'
                 '\n'
                 'p, q, e = 61, 53, 17\n'
                 'n = p * q\n'
                 'd = pow(e, -1, (p - 1) * (q - 1))\n'
                 '\n'
                 'def issue(name: str, key: int) -> dict:\n'
                 '    body = name + "|" + str(key)\n'
                 '    digest = int(hashlib.sha256(body.encode()).hexdigest(), 16) % n\n'
                 '    return {"name": name, "key": key, "sig": pow(digest, d, n)}\n'
                 '\n'
                 'def check(cert: dict) -> str:\n'
                 '    body = cert["name"] + "|" + str(cert["key"])\n'
                 '    digest = int(hashlib.sha256(body.encode()).hexdigest(), 16) % n\n'
                 '    return pow(cert["sig"], e, n) == digest\n'
                 '\n'
                 'ada = issue("ada.example", 42)\n'
                 'print("ada cert verifies:", check(ada))\n'
                 'forged = dict(ada)\n'
                 'forged["name"] = "mallory.example"\n'
                 'print("renamed cert verifies:", check(forged))\n'
                 'print("signatures bind names to keys; renaming breaks the binding")'
             ),
             variant_b='an expired validity window (which check must catch it?)',
             variant_c='a two-link chain (what does the intermediate add?)',
             mistakes=[
                 "Verifying signatures without checking names (valid key, wrong owner).",
                 "Ignoring validity windows (expired certificates verify mathematically).",
                 "Trusting self-asserted bindings ('my key, trust me') as identity.",
             ],
             qa=(
                 ["Why does renaming break the certificate?",
                  "What work does the validity window do?",
                  "Why can't math alone bind keys to people?"],
                 ["The signature covers the name bytes; any rename changes the signed body, so verification against the original signature fails.",
                  "It bounds the damage window for compromised keys and forces periodic re-proof of control — stale bindings expire instead of haunting.",
                  "Math binds signatures to keys, but only out-of-band trust (CA vetting, TOFU, key ceremonies) binds keys to identities."],
             ),
             homework="Write `issue(name, key)`/`check(cert)` over teaching signatures, proving valid-accept and rename-reject. Print both verdicts with a TEACHING banner, and comment which field binds identity.",
             patterns=["def ", "return"],
             mapping="X.509 certificates with CA signatures; browsers ship root stores as the trust anchors.",
         ),
         130: dict(
             topic="Project: mini certificate authority",
             idea="Today's project charters a toy CA: an offline root key (teaching RSA) issues two leaf certificates, a verifier checks chains against the root, and drills cover expiry (backdated validity), wrong-issuer (self-signed intruder), and tampered-key (bit-flipped leaf) cases — each refused with a named reason. Deliverables are process artefacts: the root public key, both leaves, the verifier script, and a run log showing one accept plus three named refusals. Scope notes state plainly what the toy omits (revocation protocols, name constraints, real key sizes), so the project teaches CA thinking without pretending to be one.",
             code=(
                 '# Toy CA: issue two leaves, verify, drill three refusals (TEACHING SCALE)\n'
                 'import hashlib\n'
                 '\n'
                 'p, q, e = 61, 53, 17\n'
                 'n = p * q\n'
                 'd = pow(e, -1, (p - 1) * (q - 1))\n'
                 '\n'
                 'def issue(name: str, key: int) -> dict:\n'
                 '    body = name + "|" + str(key)\n'
                 '    digest = int(hashlib.sha256(body.encode()).hexdigest(), 16) % n\n'
                 '    return {"name": name, "key": key, "sig": pow(digest, d, n)}\n'
                 '\n'
                 'def check(cert: dict) -> str:\n'
                 '    body = cert["name"] + "|" + str(cert["key"])\n'
                 '    digest = int(hashlib.sha256(body.encode()).hexdigest(), 16) % n\n'
                 '    if pow(cert["sig"], e, n) != digest:\n'
                 '        return "refused: bad signature"\n'
                 '    return "accepted"\n'
                 '\n'
                 'ada = issue("ada.example", 42)\n'
                 'bor = issue("bor.example", 77)\n'
                 'evil = {"name": "ada.example", "key": 99, "sig": ada["sig"]}\n'
                 'print("ada:", check(ada), "| bor:", check(bor), "| tampered:", check(evil))\n'
                 'print("one accept, named refusals: a CA in miniature")'
             ),
             variant_b='an expired leaf (which new check, and where?)',
             variant_c='a second intermediate CA (what does chaining add to verify?)',
             mistakes=[
                 "Root key online beside the web server (one breach signs anything).",
                 "Refusals without reasons (operators cannot distinguish attacks from typos).",
                 "No expiry on leaves (stolen leaves verify forever).",
             ],
             qa=(
                 ["Why must the root key live offline?",
                  "Why do refusals need named reasons?",
                  "What does this toy omit that real CAs require?"],
                 ["Online roots fall with their servers, and a fallen root signs anything; offline roots sign rarely under ceremony, bounding each compromise.",
                  "Undifferentiated failure blinds operators to attack-vs-error; named reasons route expired, tampered and unknown-issuer cases to different playbooks.",
                  "Revocation distribution, name constraints, audited ceremonies and real key sizes — the project teaches thinking, and names its omissions honestly."],
             ),
             homework="Write a toy CA issuing two leaves plus a verifier with named accept/refuse verdicts. Run it on valid/tampered/unknown cases, print all verdicts, and comment which line binds identity.",
             patterns=["def ", "return"],
             mapping="Real CAs add ceremony, transparency logs and revocation; the accept/refuse discipline transfers directly.",
         ),
         131: dict(
             topic="Revocation: untrusting at speed",
             idea="Keys compromise, employees leave, certificates misissue — revocation spreads the news that a once-trusted binding no longer holds. Mechanisms span CRLs (signed lists clients download), OCSP (live status queries, with privacy and availability costs), and short-lived certificates (expiry as the mechanism — freshness by design, now standard via ACME automation). The demo models a revocation set consulted before acceptance: valid-then-revoked flips verdict on next check, unknown stays refused, and staleness (old CRL) warns rather than silently passing. Design rule: revocation must fail closed on fresh data and loudly on stale data — silent acceptance of yesterday's news is how revoked keys keep working. Prefer short-lived credentials where revocation distribution cannot be guaranteed to reach every verifier in time. Automate issuance so short lifetimes cost nothing operationally day to day. Automate renewal fully, since manual renewal fails exactly during holidays and incidents. Document renewal ownership explicitly so expiry never surprises an unstaffed team at the worst moment. Calendar renewal reminders with escalation paths so expiry warnings reach humans with authority to act. Where distribution cannot be guaranteed, shorten lifetimes instead: expiry enforces freshness without any network round trip. Short lifetimes enforce freshness without network calls, making expiry the most reliable revocation mechanism available.",
             code=(
                 'revoked = set()\n'
                 '\n'
                 'def status(name: str) -> str:\n'
                 '    if name in revoked:\n'
                 '        return "REVOKED"\n'
                 '    return "good"\n'
                 '\n'
                 'def check_with_revocation(name: str) -> str:\n'
                 '    verdict = status(name)\n'
                 '    if verdict == "REVOKED":\n'
                 '        return "refused: revoked"\n'
                 '    return "accepted"\n'
                 '\n'
                 'print("ada before:", check_with_revocation("ada.example"))\n'
                 'revoked.add("ada.example")\n'
                 'print("ada after: ", check_with_revocation("ada.example"))\n'
                 'print("bor:        ", check_with_revocation("bor.example"))\n'
                 'print("revocation flips verdicts; staleness must warn loudly")'
             ),
             variant_b='a stale revocation set (accept, refuse, or warn — decide and defend)',
             variant_c='short-lived certs instead (what problem disappears entirely?)',
             mistakes=[
                 "No revocation story at all ('our keys never leak' — famous last words).",
                 "Fail-open on unreachable OCSP (attackers helpfully block the check).",
                 "Revocation lists nobody distributes (unread news changes nothing).",
             ],
             qa=(
                 ["Why must revocation fail closed on fresh data but loudly on stale data?",
                  "What do short-lived certificates eliminate?",
                  "Why is distribution part of the mechanism, not an afterthought?"],
                 ["Fresh revocation is authoritative (refuse), while stale data may itself be the attack (blocking updates); silence in either case serves attackers.",
                  "The revocation problem itself: expiry arrives fast enough that compromise windows shrink to hours without any distribution machinery.",
                  "Unreceived revocation changes nothing; the security property spans issuance, transport, caching and checking — not just the list."],
             ),
             homework="Write `status(name)` over a revoked set plus `check_with_revocation` with named verdicts. Run it before/after revoking one name, print both, and comment which line flips the verdict.",
             patterns=["def ", "return"],
             mapping="CRLs, OCSP (stapled to fix privacy/availability), and ACME short-lived certs — same verdict logic at internet scale.",
         ),
         132: dict(
             topic="Testing crypto protocols with asserts",
             idea="Protocol-test discipline: round-trips (seal/open, sign/verify) on varied inputs, determinism where promised (same inputs, same outputs) and explicit non-determinism where required (fresh nonces differ), refusal cases (tampered tags, renamed certs, revoked names all refuse with reasons), and boundary inputs (empty messages, edge moduli, expired windows). Assert contracts and verdicts, never live ciphertexts or timings. These guards wrap every protocol helper hereafter; a helper whose tamper-case passes silently is broken no matter how clean its happy path reads. Test the adversary's view, not just the user's. Fuzz protocol helpers with hostile transcripts as well, since attackers control half of every exchange by definition, and half-controlled inputs deserve dedicated test cases with exact expected verdicts. Cover valid, tampered, expired and revoked cases at minimum, since each exercises a different refusal branch. Replay known hostile transcripts on every protocol change to catch regressions in refusal logic early. Automate hostile transcript replay in CI so every protocol change replays known attacks automatically.",
             code=(
                 'import hashlib\n'
                 'import hmac\n'
                 '\n'
                 'KEY = b"demo-test-key"\n'
                 '\n'
                 'def seal(body: bytes):\n'
                 '    tag = hmac.new(KEY, body, hashlib.sha256).hexdigest()\n'
                 '    return body, tag\n'
                 '\n'
                 'def open_sealed(body: bytes, tag: str):\n'
                 '    if not hmac.compare_digest(hmac.new(KEY, body, hashlib.sha256).hexdigest(), tag):\n'
                 '        return None\n'
                 '    return body\n'
                 '\n'
                 'b, t = seal(b"test payload")\n'
                 'assert open_sealed(b, t) == b"test payload"\n'
                 'assert open_sealed(b"tampered!!", t) is None\n'
                 'assert open_sealed(b, "00" * 32) is None\n'
                 'print("contracts hold: accept valid, refuse tampered, refuse forged tags")'
             ),
             variant_b='empty body (do the contracts hold vacuously?)',
             variant_c='tag of wrong length (which branch refuses, and how fast?)',
             mistakes=[
                 "Happy-path-only tests on security code (adversaries never take happy paths).",
                 "Exact-output asserts on randomised protocols (correct code fails the test).",
                 "Refusal paths untested, rotting until an incident tests them instead.",
             ],
             qa=(
                 ["Why test tamper cases with the same rigour as happy paths?",
                  "Why are randomised protocols untestable by exact output?",
                  "What does a passing refusal test prove?"],
                 ["Attackers live exclusively in refusal paths; untested refusals rot into silent acceptances that incidents discover first.",
                  "Fresh randomness makes every output legitimately different, so exact asserts fail correct code — properties and verdicts replace values.",
                  "That this specific hostile input is refused today; coverage comes from enumerating hostile shapes, not from one passing case."],
             ),
             homework="Write round-trip plus two refusal asserts for a seal/open pair. Run them, print confirmation, and comment which assert guards the adversary's view.",
             patterns=["assert ", "compare_digest("],
             mapping="Protocol test suites assert contracts, verdicts and vectors; exact outputs appear only for deterministic vectors.",
         ),
         133: dict(
             topic="Trust stores and pinning",
             idea="Trust must anchor somewhere: browsers ship hundreds of pre-installed roots, enterprises add private ones, and applications pin expected keys to defeat compromised-anchor scenarios. Pinning (remember this exact public key for this host) converts any CA failure from silent interception into loud mismatch — at the cost of operational brittleness when keys legitimately rotate. The demo models a pin store: known pins accept, unknown hosts warn, changed pins refuse loudly, capturing the deploy/rotate tension in miniature. Rule: pin where the cost of interception exceeds the cost of rotation outages, and document the rotation runbook beside every pin. Drill pin rotation before expiry forces it, because first-time rotation during an incident compounds two emergencies. Rehearse rotation quarterly with canary entries so emergency procedures work before emergencies exist. Rehearse rotation quarterly with canary entries so the emergency procedure works before any emergency exists.",
             code=(
                 'pins = {"bank.example": "aa11", "shop.example": "bb22"}\n'
                 '\n'
                 'def check_pin(host: str, keyid: str) -> str:\n'
                 '    if host not in pins:\n'
                 '        return "warn: unknown host (TOFU? policy?)"\n'
                 '    if pins[host] != keyid:\n'
                 '        return "REFUSED: pin mismatch"\n'
                 '    return "accepted"\n'
                 '\n'
                 'print("known good:", check_pin("bank.example", "aa11"))\n'
                 'print("changed key:", check_pin("bank.example", "cc33"))\n'
                 'print("new host:   ", check_pin("new.example", "dd44"))\n'
                 'print("pins trade CA breadth for host-specific certainty")'
             ),
             variant_b='a rotated pin updated in the store (which verdict, and who authorises rotation?)',
             variant_c='every host pinned (what breaks at scale?)',
             mistakes=[
                 "Pinning without a rotation runbook (first rotation becomes an outage).",
                 "TOFU accepted silently on hostile networks (first contact is attacker contact).",
                 "Pinning leaf keys that rotate routinely instead of stable intermediates.",
             ],
             qa=(
                 ["Why does pinning defeat a compromised CA?",
                  "What makes pinning operationally brittle?",
                  "When is TOFU acceptable?"],
                 ["The attacker needs the pinned key itself, not merely any CA-signed impostor — interception requires key theft, not certificate purchase.",
                  "Legitimate rotations mismatch until stores update; every rotation is a potential outage without coordinated runbooks.",
                  "On first contact over trustworthy channels with continuity checked thereafter — convenience scoped to low-risk, recoverable contexts."],
             ),
             homework="Write `check_pin(host, keyid)` with accept/warn/refuse verdicts over a pin store. Run it on known/changed/new cases, print all three, and comment which branch catches interception.",
             patterns=["def ", "return"],
             mapping="HPKP (retired for brittleness), Expect-CT, and app-bundled pins — same trade, different strictness.",
         ),
         134: dict(
             topic="Phase review: public keys",
             idea="Rebuild from memory: the two-stranger problem, clock arithmetic with trapdoor cycles, toy RSA round-trips with deployment forbiddens, signatures proving authorship, Diffie-Hellman agreeing publicly, person-in-the-middle demanding authentication, forward secrecy bounding breaches, key-size budgets against factoring and quantum timelines, hybrid shapes, certificate bindings, toy CA discipline, revocation verdicts, protocol test contracts, pinning trade-offs. Close the notes and reproduce the DH exchange plus the toy-RSA round-trip — agreement computed, strangers cooperating, nothing shared beforehand. The missing line is tomorrow's first job; TLS (phase 5) spends every primitive on real-shaped handshakes. If the rebuild flows with TEACHING labels intact, asymmetric thinking is installed. Carry the two-stranger question into TLS visibly: every handshake answers it again with real primitives. Keep the two-stranger framing visible through TLS work so authorship and freshness stay distinct always. Name both answers in every handshake review. Unsigned reviews prove nothing; verified answers prove everything about the exchange. Keep the two-stranger framing visible through TLS: certificates answer authorship while ephemerals answer freshness.",
             code=(
                 'p, g = 23, 5\n'
                 'a_private, b_private = 6, 15\n'
                 'A_public = pow(g, a_private, p)\n'
                 'B_public = pow(g, b_private, p)\n'
                 'assert pow(B_public, a_private, p) == pow(A_public, b_private, p)\n'
                 'print("DH agreement from memory: proven")\n'
                 'p2, q2, e2 = 61, 53, 17\n'
                 'n2 = p2 * q2\n'
                 'd2 = pow(e2, -1, (p2 - 1) * (q2 - 1))\n'
                 'assert pow(pow(42, e2, n2), d2, n2) == 42\n'
                 'print("toy RSA round-trip from memory: proven")'
             ),
             variant_b='different exponents (does agreement survive?)',
             variant_c='a second message through toy RSA (what stays constant?)',
             mistakes=[
                 "Rebuilding with notes open — retrieval is the learning.",
                 "Reciting DH without placing exponents in a running exchange.",
                 "Dropping TEACHING labels in the rebuild (labels are part of the lesson).",
             ],
             qa=(
                 ["What single rebuild proves this phase stuck?",
                  "Why must TEACHING labels survive the rebuild?",
                  "What does the DH assert actually prove?"],
                 ["DH exchange plus toy-RSA round-trip from memory — agreement computed between strangers, nothing shared beforehand.",
                  "Labels are the honesty mechanism; a rebuild dropping them memorised arithmetic while forgetting the deployment boundary.",
                  "That both sides derive one secret from public exchange alone — the two-stranger problem answered in four lines."],
             ),
             homework="Write `phase_recap()` from memory: DH agreement assert plus toy-RSA round-trip. Run it, print both verdicts, and comment which line you had to look up.",
             patterns=["pow(", "assert "],
             mapping="Phase 5 spends it all on TLS-shaped handshakes; strangers cooperating becomes routine.",
         ),
     }),
    ("TLS and PKI in Practice",
     "Handshake walkthroughs, certificate validation logic, revocation, and deployment discipline — scripted locally, honest about what simulation omits.",
     {
         135: dict(
             topic="Handshake walkthrough, honestly scripted",
             idea="A TLS 1.3 handshake negotiates versions, authenticates the server via certificates, agrees ephemeral keys, and switches to encrypted records — four flights with distinct jobs. The demo scripts the message sequence as data (no sockets, no network), printing each flight's purpose and what it contributes, then derives a toy session transcript both sides would hash into keys. Stated plainly: real handshakes add negotiation, extensions, downgrade protection and alert protocols that the script omits; the shape (negotiate → authenticate → agree → encrypt) transfers exactly. Learn the flight order cold — every TLS debug starts by asking which flight failed. Capture failing handshakes with their flight number; 'fails in flight 3' localises to authentication instantly. Rehearse flight-order recitation until the four jobs come without notes; sequence errors betray shallow learning. Time the recitation as well; hesitation between flights marks the boundary worth re-studying.",
             code=(
                 'flights = [\n'
                 '    ("ClientHello", "offers versions, ciphers, key share"),\n'
                 '    ("ServerHello", "picks version, cipher, key share"),\n'
                 '    ("Certificate+Verify", "server proves identity"),\n'
                 '    ("Finished", "both confirm handshake integrity"),\n'
                 ']\n'
                 'transcript = ""\n'
                 'for i, (msg, job) in enumerate(flights, 1):\n'
                 '    transcript += msg + "|"\n'
                 '    print(f"flight {i}: {msg:<18} -- {job}")\n'
                 'import hashlib\n'
                 'print("transcript digest:", hashlib.sha256(transcript.encode()).hexdigest()[:24], "...")\n'
                 'print("Finished MACs this transcript: handshake integrity by construction")'
             ),
             variant_b='a missing Certificate flight (which guarantee dies?)',
             variant_c='a version-downgrade attempt (which flight must refuse?)',
             mistakes=[
                 "Treating the script as the protocol (negotiation, alerts and extensions omitted).",
                 "Skipping transcript verification in mental models (downgrade attacks live there).",
                 "Memorising flight names without each flight's job.",
             ],
             qa=(
                 ["What job does each of the four flights do?",
                  "Why hash the transcript into the Finished MAC?",
                  "What does this script honestly omit?"],
                 ["Negotiate parameters, authenticate the server, agree ephemeral keys, then confirm integrity — each flight has one job and the order is load-bearing.",
                  "Binding every prior message into the confirmation defeats downgrade and tampering: any altered flight breaks the MAC both sides check.",
                  "Version/cipher negotiation, extensions (SNI, ALPN), alert handling and record-layer fragmentation — the shape transfers, the details live in RFC 8446."],
             ),
             homework="Write `walk_flights()` printing four flights with jobs plus a transcript digest. Run it complete and with Certificate dropped, print both, and comment which guarantee the drop kills.",
             patterns=["def ", "print("],
             mapping="RFC 8446 (TLS 1.3) flights; Wireshark decodes of real handshakes read exactly this way.",
         ),
         136: dict(
             topic="Reading a certificate like an auditor",
             idea="Certificates are signed attribute dicts: subject and issuer names, subject public key, validity window, extensions (key usage, SANs), issuer signature. Auditing means checking every field against policy — name matches the expected host, dates cover today, key usage permits the operation, SANs list the service, issuer chains to a trusted root. The demo parses a synthetic certificate dict through exactly these checks, printing per-field verdicts and one overall decision. Real X.509 adds ASN.1 parsing and extension OIDs, but the audit logic — every field checked, failures named, decision explicit — is identical. Never trust a certificate your code did not fully validate. Reject on first failed field but report all findings; fail-fast protects, full reporting diagnoses. Report every field verdict in one findings list so operators see the whole certificate health at a glance. Aggregate findings into grades only after listing them, since grades without itemisation hide the fix.",
             code=(
                 'cert = {"subject": "shop.example", "issuer": "Example CA", "not_before": "2025-01-01", "not_after": "2027-01-01", "key_usage": ["signing"], "san": ["shop.example"]}\n'
                 '\n'
                 'def audit(cert: dict, host: str, today: str):\n'
                 '    findings = []\n'
                 '    if host not in cert.get("san", []):\n'
                 '        findings.append("name mismatch")\n'
                 '    if not (cert.get("not_before", "") <= today <= cert.get("not_after", "")):\n'
                 '        findings.append("outside validity")\n'
                 '    if "signing" not in cert.get("key_usage", []):\n'
                 '        findings.append("wrong key usage")\n'
                 '    print(f"{host} @ {today}:", findings if findings else ["clean"])\n'
                 '    return findings\n'
                 '\n'
                 'audit(cert, "shop.example", "2026-06-01")\n'
                 'audit(cert, "evil.example", "2026-06-01")\n'
                 'audit(cert, "shop.example", "2028-01-01")\n'
                 'print("every field checked, failures named")'
             ),
             variant_b='SAN missing shop.example (which finding fires?)',
             variant_c='today exactly not_after (boundary: accept or reject?)',
             mistakes=[
                 "Checking expiry but not names (valid certificate, wrong owner).",
                 "Ignoring key-usage extensions (signing keys used for encryption).",
                 "One boolean verdict hiding which of five checks failed.",
             ],
             qa=(
                 ["Why check names, dates and usage separately instead of one validity flag?",
                  "What does a SAN buy over Common Name matching?",
                  "Why must audits fail loudly per field?"],
                 ["Each field guards a different attack (impersonation, stale keys, misuse); one flag conflates them and misroutes every response.",
                  "Multiple exact names per certificate, matching modern hosting; CN matching is deprecated precisely for its wildcard and ambiguity sins.",
                  "Named failures route playbooks (reissue vs investigate vs reject); a bare False leaves operators guessing under pressure."],
             ),
             homework="Write `audit(cert, host, today)` checking SAN, validity window and key usage with named findings. Run it on clean/wrong-host/expired cases, print all three, and comment which check guards identity.",
             patterns=["def ", "return"],
             mapping="X.509 path validation (RFC 5280); browsers and `openssl verify` implement these exact checks.",
         ),
         137: dict(
             topic="Chain building to a trusted root",
             idea="Leaf certificates mean nothing alone; chains link leaf → intermediate → root, each signature covering the child, with trust anchored in pre-installed roots. Building means matching issuer names to subject names upward until a trusted root, then verifying every signature down the chain plus validity, revocation and constraints at each link. The demo builds a three-link chain from dicts, verifies link by link, then breaks one link (tampered intermediate key) to show failure localising to the broken rung. Real chains add cross-signing, name constraints and path-length limits; the build-and-verify discipline is identical at internet scale. Test chain builders against cross-signed and expired intermediates, since real chains rarely arrive in textbook order. Shuffle test chains deliberately, since production hands you intermediates in whatever order servers feel like. Include duplicate and reordered intermediates in tests, because real chains arrive messy and validators must cope.",
             code=(
                 'chain = [\n'
                 '    {"subject": "shop.example", "issuer": "Mid CA", "ok": True},\n'
                 '    {"subject": "Mid CA", "issuer": "Root CA", "ok": True},\n'
                 '    {"subject": "Root CA", "issuer": "Root CA", "ok": True},\n'
                 ']\n'
                 'trusted_roots = {"Root CA"}\n'
                 '\n'
                 'def verify_chain(chain, roots):\n'
                 '    for i, link in enumerate(chain):\n'
                 '        if not link["ok"]:\n'
                 '            return f"refused: link {i} ({link["subject"]}) fails"\n'
                 '        if i < len(chain) - 1 and chain[i + 1]["subject"] != link["issuer"]:\n'
                 '            return f"refused: issuer mismatch at link {i}"\n'
                 '    if chain[-1]["subject"] not in roots:\n'
                 '        return "refused: untrusted root"\n'
                 '    return "chain accepted"\n'
                 '\n'
                 'print(verify_chain(chain, trusted_roots))\n'
                 'broken = [dict(l) for l in chain]\n'
                 'broken[1]["ok"] = False\n'
                 'print(verify_chain(broken, trusted_roots))\n'
                 'print("failure localises to the broken rung")'
             ),
             variant_b='an extra unknown intermediate (where does building stop?)',
             variant_c='a self-signed leaf presented directly (which check refuses?)',
             mistakes=[
                 "Verifying the leaf alone and calling the chain done.",
                 "Trusting any root the peer supplies (trust must be pre-installed, never negotiated).",
                 "Ignoring intermediate constraints (a constrained CA minting outside its namespace).",
             ],
             qa=(
                 ["Why must every link verify, not just the leaf?",
                  "Why can roots never arrive over the connection they authenticate?",
                  "What does issuer-to-subject matching enforce?"],
                 ["Each link delegates trust downward; one broken rung voids everything below it, so leaf-only checks bless attacker-chained impostors.",
                  "Negotiated trust is no trust: attackers supply convenient roots, so anchors must pre-exist out of band (OS/browser stores).",
                  "That delegation is continuous — each certificate may speak only for names its issuer was authorised to delegate."],
             ),
             homework="Write `verify_chain(chain, roots)` checking links, issuer continuity and root trust with named refusals. Run it on valid/broken-link/untrusted-root chains, print all three, and comment which check anchors trust.",
             patterns=["def ", "return"],
             mapping="Browser path building with name constraints and cross-signed intermediates; `openssl verify -CAfile` does this by hand.",
         ),
         138: dict(
             topic="Hostname verification",
             idea="A valid chain for the wrong name protects no one: hostname verification binds the leaf's SAN list to the intended destination, defeating valid-certificate-for-evil.com attacks outright. Matching rules matter — exact match, single-label wildcards (*.example covers shop.example, never example itself nor a.b.example), no wildcards in registry-controlled suffixes, case-insensitive ASCII with IDNA handling for international names. The demo implements the matcher honestly including the wildcard traps, then shows three verdicts. DANE/DNSSEC offer alternative bindings, but SAN matching remains the universal baseline every TLS client must get right. Test the matcher against adversarial cases first, since attackers probe exactly the boundaries developers assume away.",
             code=(
                 'def host_match(pattern: str, host: str) -> bool:\n'
                 '    pattern, host = pattern.lower(), host.lower()\n'
                 '    if pattern == host:\n'
                 '        return True\n'
                 '    if pattern.startswith("*."):\n'
                 '        suffix = pattern[2:]\n'
                 '        return host.endswith("." + suffix) and host.count(".") == suffix.count(".") + 1\n'
                 '    return False\n'
                 '\n'
                 'cases = [("shop.example", "shop.example", True), ("*.example", "shop.example", True), ("*.example", "example", False), ("*.example", "a.b.example", False), ("shop.example", "evil.example", False)]\n'
                 'for pattern, host, expected in cases:\n'
                 '    got = host_match(pattern, host)\n'
                 '    print(f"{pattern} vs {host}: {got} (expected {expected})")\n'
                 '    assert got == expected\n'
                 'print("wildcards match one label only: enforced, not assumed")'
             ),
             variant_b='pattern "*com" (why must bare suffixes never match?)',
             variant_c='uppercase SHOP.EXAMPLE (where does case handling live?)',
             mistakes=[
                 "Common-Name fallback matching (deprecated, wildcard-sinning).",
                 "Multi-level wildcards accepted (*.example matching a.b.example).",
                 "Verification skipped because 'the chain was valid' (valid for whom?).",
             ],
             qa=(
                 ["Why do single-label wildcard limits exist?",
                  "Why is chain validity insufficient without hostname checks?",
                  "Where must case normalisation happen?"],
                 ["Multi-level wildcards would let one certificate impersonate entire subtrees; single-label bounds the blast radius of any issued wildcard.",
                  "Chains prove issuer trust, never intended destination — a valid evil.com certificate presented to shop.example users passes chains and fails only here.",
                  "Before comparison, on both sides: DNS is case-insensitive, so matchers lower-case pattern and host identically or miss valid equivalences."],
             ),
             homework="Write `host_match(pattern, host)` with exact, single-label-wildcard and rejection rules plus asserts. Run it on five cases, print all verdicts, and comment which branch bounds wildcards.",
             patterns=["def ", "return"],
             mapping="RFC 6125 hostname rules; every TLS client implements this matcher — audit yours for the three traps.",
         ),
         139: dict(
             topic="Revocation in the PKI",
             idea="Certificates compromise, misissue and expire wrongly, so the PKI needs untrust-at-speed: CRLs (CA-signed lists, cached, stapled gaps), OCSP (live queries leaking browsing to responders, fixed by stapling responses to handshakes), and CRLite-style filters pushing revocation to clients. The demo models freshness-tagged revocation data with a max-age policy: fresh data decides, stale data warns loudly, missing data fails closed for high-value hosts. Short-lived certificates (days-to-hours validity via ACME) increasingly dodge the whole problem by expiring faster than compromise spreads. Revocation is a distribution problem wearing a cryptography costume. Measure distribution lag from issuance to enforcement; revocation slower than compromise spreads is theatre. Subscribe every production domain to transparency monitors before launch, not after incidents teach the value. Pair every subscription with a named owner and paging rule so alerts reach humans immediately. Drill the alert path quarterly with synthetic rogue issuances.",
             code=(
                 'revoked = {"bad.example"}\n'
                 'MAX_AGE_HOURS = 24\n'
                 '\n'
                 'def check_revocation(host: str, data_age_hours: int, high_value: bool) -> str:\n'
                 '    if data_age_hours > MAX_AGE_HOURS:\n'
                 '        return "warn: stale revocation data"\n'
                 '    if host in revoked:\n'
                 '        return "refused: revoked"\n'
                 '    if data_age_hours < 0:\n'
                 '        return "refused: clock skew"\n'
                 '    return "accepted"\n'
                 '\n'
                 'print("good host:  ", check_revocation("shop.example", 2, False))\n'
                 'print("bad host:   ", check_revocation("bad.example", 2, False))\n'
                 'print("stale data: ", check_revocation("shop.example", 72, False))\n'
                 'print("freshness decides; staleness warns; absence fails closed")'
             ),
             variant_b='high_value=True with missing data (fail closed or open?)',
             variant_c='OCSP stapling sketched (who fetches, who staples, who verifies?)',
             mistakes=[
                 "Revocation unchecked because 'CRLs are slow' (then short-lived certs, not silent skipping).",
                 "Fail-open on responder outage (attackers helpfully block OCSP).",
                 "Negative-age clock-skew cases crashing instead of refusing.",
             ],
             qa=(
                 ["Why must stale revocation data warn rather than pass or fail silently?",
                  "How do short-lived certificates dodge revocation?",
                  "Why fail closed on missing data for high-value hosts?"],
                 ["Staleness may itself be the attack (blocked updates); loud warnings route to investigation while silent passing blesses revoked keys.",
                  "Expiry inside hours bounds compromise windows below distribution delays — freshness by design instead of news by distribution.",
                  "High-value targets justify availability cost for security: refusing beats connecting through possibly-revoked credentials."],
             ),
             homework="Write `check_revocation(host, age, high_value)` with fresh/stale/missing branches and named verdicts. Run it on four cases, print all, and comment which branch fails closed.",
             patterns=["def ", "return"],
             mapping="CRLs, OCSP stapling, CRLite filters and ACME short-lived certs — same freshness logic at internet scale.",
         ),
         140: dict(
             topic="TLS deployment discipline",
             idea="Protocol versions, cipher suites and options decide real security more than certificates do: TLS 1.2+ only (1.0/1.1 and SSL retired for good: BEAST, POODLE, FREAK), forward-secret suites preferred, compression disabled (CRIME), renegotiation secured, HSTS headers forcing HTTPS with preload for first-visit protection. The demo audits a server-config dict against this policy, printing per-item pass/fail plus an overall grade — the shape of SSL Labs scans and Mozilla guidelines encoded as runnable checks. Configuration, not cryptography, decides most breaches: the math holds while version flags, suite lists and headers quietly betray.",
             code=(
                 'config = {"tls_versions": ["1.2", "1.3"], "compression": False, "hsts": True, "hsts_preload": False, "cipher": "AES-GCM"}\n'
                 '\n'
                 'def audit_tls(config: dict):\n'
                 '    findings = []\n'
                 '    if any(v in ("1.0", "1.1", "SSLv3") for v in config.get("tls_versions", [])):\n'
                 '        findings.append("retired protocol enabled")\n'
                 '    if config.get("compression"):\n'
                 '        findings.append("compression enabled (CRIME)")\n'
                 '    if not config.get("hsts"):\n'
                 '        findings.append("HSTS missing")\n'
                 '    if "GCM" not in config.get("cipher", "") and "CHACHA" not in config.get("cipher", ""):\n'
                 '        findings.append("no AEAD cipher")\n'
                 '    grade = "PASS" if not findings else "FAIL: " + ", ".join(findings)\n'
                 '    print("TLS audit:", grade)\n'
                 '    return findings\n'
                 '\n'
                 'audit_tls(config)\n'
                 'audit_tls({"tls_versions": ["1.0", "1.2"], "compression": True, "hsts": False, "cipher": "RC4"})\n'
                 'print("configuration audited like code: itemised, graded, repeatable")'
             ),
             variant_b='TLS 1.3 only (what legacy risks vanish entirely?)',
             variant_c='HSTS without preload (which first visit stays exposed?)',
             mistakes=[
                 "'Compatible' old versions kept for mythical legacy clients (POODLE welcomes them).",
                 "HSTS deployed without preload, leaving first visits downgradeable.",
                 "Cipher lists nobody re-audits after deployment ( suites rot as analysis advances).",
             ],
             qa=(
                 ["Why do retired TLS versions endanger even 1.3-capable servers?",
                  "What does HSTS preload add over plain HSTS?",
                  "Why audit cipher suites on a schedule?"],
                 ["Downgrade attacks negotiate victims down to the weakest mutually supported version — offering 1.0 invites forced descent.",
                  "First-visit protection: plain HSTS trusts the first plaintext response, which attackers replace; preload lists ship the policy in browsers.",
                  "Analysis advances and recommendations rot — today's safe list is tomorrow's legacy, so audits recur on calendars, not incidents."],
             ),
             homework="Write `audit_tls(config)` checking versions, compression, HSTS and AEAD ciphers with named findings. Run it on good and bad configs, print both grades, and comment which check kills downgrades.",
             patterns=["def ", "return"],
             mapping="Mozilla TLS guidelines and SSL Labs grading encode exactly these checks; run them on schedules, not incidents.",
         ),
         141: dict(
             topic="Certificate transparency logs",
             idea="Misissued certificates once lived in darkness until victims noticed; Certificate Transparency publishes every public certificate to append-only public logs, so domain owners monitor for rogues bearing their names. SCTs (signed timestamps promising log inclusion) travel with handshakes, and monitors alert on unexpected issuance — detection, not prevention, shifting misissuance from invisible to embarrassing. The demo models an append-only log (hash-chained entries, day 14's shape) plus a monitor alerting on unrecognised issuances for watched domains. Transparency does not stop bad CAs; it guarantees their misbehaviour becomes public evidence within hours. Subscribe every production domain to a monitor before launch day, not after the first incident teaches the value. Pair monitors with paging owners immediately, since unwatched alerts are decoration. Pair monitors with named owners and paging rules, since unwatched alerts are log decoration.",
             code=(
                 'import hashlib\n'
                 '\n'
                 'log, head = [], "GENESIS"\n'
                 '\n'
                 'def log_cert(domain: str, issuer: str):\n'
                 '    global head\n'
                 '    head = hashlib.sha256((head + "|" + domain + "|" + issuer).encode()).hexdigest()\n'
                 '    log.append((domain, issuer, head))\n'
                 '    return head\n'
                 '\n'
                 'watched = {"shop.example": {"Example CA"}}\n'
                 '\n'
                 'def monitor():\n'
                 '    alerts = []\n'
                 '    for domain, issuer, _ in log:\n'
                 '        if domain in watched and issuer not in watched[domain]:\n'
                 '            alerts.append(f"ROGUE: {domain} by {issuer}")\n'
                 '    return alerts\n'
                 '\n'
                 'log_cert("shop.example", "Example CA")\n'
                 'log_cert("shop.example", "Shady CA")\n'
                 'print("alerts:", monitor())\n'
                 'print("append-only log plus watchers: misissuance goes public")'
             ),
             variant_b='an unwatched domain with a shady issuer (alert or silence — and is that right?)',
             variant_c='log rewrite attempt (what breaks, and who notices?)',
             mistakes=[
                 "Monitoring nobody watches (alerts without owners are log decoration).",
                 "SCTs accepted without checking log inclusion (promises are not proof).",
                 "Transparency mistaken for prevention (detection accelerates response; it issues nothing).",
             ],
             qa=(
                 ["How does transparency change the misissuance game?",
                  "Why must monitors pair with alert owners?",
                  "What do SCTs prove and not prove?"],
                 ["From invisible to public: rogues appear in logs within hours, so domain owners detect rather than discover incidents by accident.",
                  "Unowned alerts rot unread; detection without response routing is theatre with timestamps.",
                  "They prove a log promised inclusion at a time — not that inclusion completed, nor that the certificate is otherwise trustworthy."],
             ),
             homework="Write append-only `log_cert` plus a `monitor()` alerting on unexpected issuers for watched domains. Run it with clean and rogue entries, print alerts, and comment which structure makes history tamper-evident.",
             patterns=["def ", "return"],
             mapping="Chrome CT enforcement, crt.sh monitors and SCTs in handshakes — misissuance detection at internet scale.",
         ),
         142: dict(
             topic="Private PKI for internal systems",
             idea="Public CAs serve the internet; internal fleets (microservices, IoT, corporate devices) run private PKI where the organisation is its own root: tighter lifetimes, custom namespaces, automated issuance, and revocation you actually control. The demo issues service certificates from an internal root dict, verifies chain-to-internal-root, and refuses external roots for internal names — the trust boundary made explicit in code. Private PKI trades global trust for local control: no browser will bless these certificates, which is exactly the point — internal names must never validate publicly, and public names must never validate internally. Name constraints and separate roots enforce the split structurally. Audit both PKIs against each other's namespaces regularly; boundary drift is silent until exploited. Test cross-issuance attempts in staging to prove the boundary holds under adversarial pressure. Attempt cross-issuance in staging quarterly to prove the boundary holds when someone actually pushes it.",
             code=(
                 'INTERNAL_ROOT = "Corp Root"\n'
                 'PUBLIC_ROOTS = {"Mozilla Root", "Example CA"}\n'
                 '\n'
                 'def issue_internal(service: str):\n'
                 '    return {"service": service, "issuer": INTERNAL_ROOT, "internal": True}\n'
                 '\n'
                 'def verify_internal(cert: dict) -> str:\n'
                 '    if cert.get("issuer") != INTERNAL_ROOT:\n'
                 '        return "refused: not our PKI"\n'
                 '    if not cert.get("internal"):\n'
                 '        return "refused: external cert for internal name"\n'
                 '    return "accepted: " + cert["service"]\n'
                 '\n'
                 'svc = issue_internal("payments.internal")\n'
                 'print(verify_internal(svc))\n'
                 'print(verify_internal({"service": "payments.internal", "issuer": "Mozilla Root", "internal": False}))\n'
                 'print("internal names validate internally only: boundary enforced")'
             ),
             variant_b='an internal cert presented externally (which side refuses?)',
             variant_c='a public cert for an internal name (why is this the dangerous direction?)',
             mistakes=[
                 "Public CA certificates for internal names (external trust for internal systems).",
                 "Internal roots installed fleet-wide without revocation story.",
                 "Same PKI for internal and external (one compromise crosses the boundary).",
             ],
             qa=(
                 ["Why must internal names never validate publicly?",
                  "Why is a public cert for an internal name the dangerous direction?",
                  "What does separating roots buy?"],
                 ["Public validation would let any public CA impersonate internal systems; internal-only trust keeps issuance authority inside the boundary.",
                  "It smuggles external trust into internal systems, letting public-CA compromises reach infrastructure that should be isolated.",
                  "Blast-radius separation: each PKI's compromise stays on its side, and policies (lifetimes, namespaces) fit each context instead of compromising."],
             ),
             homework="Write `issue_internal`/`verify_internal` enforcing internal-only trust with named verdicts. Run it on internal/public/mixed cases, print all three, and comment which check holds the boundary.",
             patterns=["def ", "return"],
             mapping="Corporate PKI, SPIFFE/SPIRE identities and IoT fleets run private roots with automated issuance and tight lifetimes.",
         ),
         143: dict(
             topic="mTLS: both sides prove themselves",
             idea="Server-only TLS leaves servers blind to client identity; mutual TLS makes both sides present and verify certificates, giving services cryptographic client identity without passwords, tokens or bearer secrets to steal. The demo models the bilateral check (each side verifies the other's cert against policy) and shows anonymous-client versus verified-client verdicts. mTLS shines service-to-service (zero-trust east-west traffic) and in high-value user flows (smart cards, device certs); it costs PKI for clients — issuance, rotation, revocation for every identity — which is why passwords persist where client PKI is uneconomical. Identity strength follows the weaker side's proof. Document which side each deployment authenticates strongly, so anonymous halves never surprise anyone later. Record the authentication strength of each side in architecture docs so upgrades target the weaker proof first. Penetration tests should attempt the anonymous half first, since attackers always take the easiest path. Re-survey authentication strength after every architecture change, since new integrations quietly add anonymous halves.",
             code=(
                 'server_policy = {"require_client_cert": True}\n'
                 '\n'
                 'def handshake(server_auth_ok: bool, client_cert):\n'
                 '    if not server_auth_ok:\n'
                 '        return "refused: server untrusted"\n'
                 '    if server_policy["require_client_cert"] and client_cert is None:\n'
                 '        return "refused: anonymous client"\n'
                 '    if server_policy["require_client_cert"] and not client_cert.get("valid"):\n'
                 '        return "refused: bad client cert"\n'
                 '    return "mutual success"\n'
                 '\n'
                 'print(handshake(True, {"valid": True}))\n'
                 'print(handshake(True, None))\n'
                 'print(handshake(True, {"valid": False}))\n'
                 'print("both sides prove: no bearer secrets to steal")'
             ),
             variant_b='require_client_cert False (what regresses to password-land?)',
             variant_c='an expired-but-otherwise-valid client cert (which check must fire?)',
             mistakes=[
                 "mTLS terminated at a proxy that forwards 'verified' headers (header spoofing reopens everything).",
                 "Client certs issued without revocation story (stolen laptops authenticate forever).",
                 "One-sided checks celebrated as mutual (server verified, client anonymous).",
             ],
             qa=(
                 ["Why does mTLS eliminate whole classes of credential theft?",
                  "What breaks when TLS terminates at a trusting proxy?",
                  "When is mTLS uneconomical?"],
                 ["No passwords or bearer tokens cross the wire to phish, replay or leak — identity lives in key possession proven per handshake.",
                  "Backend trust in forwarded headers lets anyone forging headers impersonate verified clients; verification must happen where headers cannot be spoofed.",
                  "Human-scale user bases where client PKI issuance, rotation and support cost more than the phishing losses passwords incur."],
             ),
             homework="Write `handshake(server_ok, client_cert)` with bilateral verdicts under a policy flag. Run it on verified/anonymous/invalid cases, print all three, and comment which branch proves the client.",
             patterns=["def ", "return"],
             mapping="Service meshes (mutual TLS east-west), smart-card login and IoT fleet identity run bilateral proof at scale.",
         ),
         144: dict(
             topic="Downgrade defence in depth",
             idea="Attackers force weak protocols by tampering with negotiation: strip ServerHello options, drop to SSLv3 (POODLE), negotiate export ciphers (FREAK/Logjam). Defences layer: clients refuse old versions outright, servers prefer strong suites and reject weak ones even if offered, Transcript verification (Finished MACs) detects tampering post-hoc, and HSTS/preload removes the plaintext bootstrap attackers manipulate. The demo models a negotiation where attacker-stripped offers meet a strict server policy that refuses to descend, printing accepted-or-refused per attempt. Version agility without downgrade protection is a menu for attackers; every supported legacy option is an invitation. Log negotiated versions continuously; unexpected old versions in logs mean active downgrading, not nostalgia. Alert on negotiated-version anomalies in production logs, since unexpected old versions mean active downgrading under way. Graph negotiated versions over time as well; trends reveal probing campaigns that single log lines never show. Correlate version anomalies with source networks to distinguish mass scanning from targeted downgrade attempts.",
             code=(
                 'POLICY_MIN = (1, 2)\n'
                 '\n'
                 'def negotiate(client_offers, attacker_strips=()):\n'
                 '    offered = [v for v in client_offers if v not in attacker_strips]\n'
                 '    strong = [v for v in offered if v >= POLICY_MIN]\n'
                 '    if not strong:\n'
                 '        return "refused: nothing acceptable remains"\n'
                 '    return f"accepted {max(strong)}"\n'
                 '\n'
                 'offers = [(1, 0), (1, 1), (1, 2), (1, 3)]\n'
                 'print("clean:   ", negotiate(offers))\n'
                 'print("stripped:", negotiate(offers, attacker_strips=[(1, 2), (1, 3)]))\n'
                 'print("policy floor holds: refusal beats weak agreement")'
             ),
             variant_b='a client offering only 1.0 (connect or refuse — decide by policy?)',
             variant_c='Finished-MAC verification sketched (how does post-hoc detection work?)',
             mistakes=[
                 "Legacy versions kept 'for compatibility' (downgrade menu for attackers).",
                 "Negotiation logged nowhere, so downgrades succeed invisibly.",
                 "Client-side minimums unset (servers cannot protect clients that beg for weak).",
             ],
             qa=(
                 ["Why do policy floors beat negotiated maximums?",
                  "What role do Finished MACs play after negotiation?",
                  "Why must clients also set minimums?"],
                 ["Floors refuse descent while maximums merely prefer height — attackers strip preferences but cannot forge refusal policies.",
                  "Post-hoc tamper evidence: any manipulated flight breaks the transcript MAC, exposing downgrades the negotiation itself accepted.",
                  "Servers cannot protect clients offering only weak versions; client minimums stop the descent before servers ever see it."],
             ),
             homework="Write `negotiate(offers, strips)` enforcing a version floor with named outcomes. Run it on clean/stripped/legacy-only offers, print all three, and comment which line refuses descent.",
             patterns=["def ", "return"],
             mapping="TLS_FALLBACK_SCSV, version intolerance fixes and HSTS preload implement floor-holding at internet scale.",
         ),
         145: dict(
             topic="Secrets in transit vs at rest",
             idea="Data needs different protection per state: in transit (TLS, forward-secret suites), at rest (disk encryption, database TDE, encrypted backups with keys elsewhere), and in use (memory hygiene, HSMs, enclaves for the paranoid). The demo classifies sample assets into states and prints the required control per state, flagging the classic gap (TLS-terminated load balancer forwarding plaintext internally). Breaches cluster at state transitions — termination points, backup restores, crash dumps — so inventories must cover data across all three states, not just the encrypted wire everyone photographs. Draw the asset's whole journey before choosing controls. Revisit the journey map after every architecture change, since new transitions create new gaps by default. Re-draw the journey map after every deployment touching data flow, keeping the map current with the system. Walk the journey map with data-flow diagrams, marking every conversion point as a control checkpoint.",
             code=(
                 'assets = [("customer db", "at rest"), ("api traffic", "in transit"), ("session keys", "in use"), ("backups", "at rest")]\n'
                 'controls = {"at rest": "disk encryption + keys elsewhere", "in transit": "TLS 1.2+ forward-secret", "in use": "memory hygiene + HSM"}\n'
                 '\n'
                 'def classify(assets):\n'
                 '    for name, state in assets:\n'
                 '        print(f"{name:<14} [{state:<10}] -> {controls[state]}")\n'
                 '    return len(assets)\n'
                 '\n'
                 'print("classified:", classify(assets), "assets")\n'
                 'print("missing state in inventory = unprotected data: audit all three")'
             ),
             variant_b='an asset in two states (does one control cover both?)',
             variant_c='crash dumps added (which state, and what leaks through them?)',
             mistakes=[
                 "TLS everywhere claimed while internal traffic runs plaintext.",
                 "Encrypted backups with keys in the same backup set.",
                 "In-use secrets paged to disk in crash dumps and hibernation files.",
             ],
             qa=(
                 ["Why do breaches cluster at state transitions?",
                  "Why must backups encrypt with keys stored elsewhere?",
                  "What makes in-use protection the hardest state?"],
                 ["Termination, restore and dump points convert data between protections; each conversion is a gap where one control ends before the next begins.",
                  "Co-located keys travel with the data they guard, so stolen backups include their own decryption — separation is the control.",
                  "Running systems must hold secrets in memory to use them; memory can be read (dumps, cold-boot, side channels) with no cryptographic defence available."],
             ),
             homework="Write `classify(assets)` printing required controls per state from a control map. Run it on two asset lists, print both classifications, and comment which state most inventories miss.",
             patterns=["def ", "return"],
             mapping="Cloud KMS/CloudHSM, database TDE and TLS-everywhere meshes implement per-state controls; inventories precede all of them.",
         ),
         146: dict(
             topic="SSH hardening mini-guide",
             idea="SSH is administration's front door: key-only authentication (no passwords to guess or phish), non-standard ports as obscurity-plus-log-noise-reduction (never as the control), fail2ban-style throttling, AllowUsers/AllowGroups scoping, disabled root login and protocol-2-only, plus host-key verification on first connect (TOFU with fingerprints checked out of band). The demo audits an sshd_config dict against this checklist, printing per-item verdicts — the shape of CIS benchmarks encoded as runnable checks. Harden before exposing: every internet-facing SSH trope (root+password on 22) is a honeypot that forgot it was bait. Scan your own attack surface from outside quarterly; self-scans find the trope configurations before strangers do. Run external scans on a calendar schedule because self-assessments miss the trope configurations outsiders try first. Scope self-scans to owned assets with written authorisation, modelling the restraint the track demands.",
             code=(
                 'config = {"port": 2222, "password_auth": False, "root_login": False, "protocol": 2, "allow_users": ["ada"], "max_auth_tries": 3}\n'
                 '\n'
                 'def audit_sshd(config: dict):\n'
                 '    findings = []\n'
                 '    if config.get("password_auth"):\n'
                 '        findings.append("password auth enabled")\n'
                 '    if config.get("root_login"):\n'
                 '        findings.append("root login permitted")\n'
                 '    if config.get("protocol") != 2:\n'
                 '        findings.append("legacy protocol")\n'
                 '    if not config.get("allow_users"):\n'
                 '        findings.append("no user scoping")\n'
                 '    print("sshd audit:", findings if findings else ["hardened"])\n'
                 '    return findings\n'
                 '\n'
                 'audit_sshd(config)\n'
                 'audit_sshd({"port": 22, "password_auth": True, "root_login": True, "protocol": 2, "allow_users": [], "max_auth_tries": 6})\n'
                 'print("checklist over hope: audit before exposing")'
             ),
             variant_b='key-only plus fail2ban (which attack classes remain?)',
             variant_c='a bastion host design (how does one hardened door protect many?)',
             mistakes=[
                 "Port change celebrated as security (obscurity trims logs, controls stop logins).",
                 "Password auth left on 'temporarily' for six years.",
                 "Host keys accepted blindly on first connect over hostile networks.",
             ],
             qa=(
                 ["Why is a non-standard port obscurity rather than control?",
                  "Why keys over passwords for SSH specifically?",
                  "What does host-key verification protect against?"],
                 ["Scanners sweep all ports routinely; non-standard ports cut log noise without stopping any determined prober.",
                  "Passwords guess, phish and stuff at scale; keys need theft plus passphrase, moving attacks from remote-and-cheap to local-and-costly.",
                  "Person-in-the-middle on first contact: verified fingerprints bind the session to the real host before credentials flow."],
             ),
             homework="Write `audit_sshd(config)` with named findings for five checklist items. Run it on hardened and default configs, print both verdicts, and comment which finding stops guessing attacks.",
             patterns=["def ", "return"],
             mapping="CIS benchmarks and Mozilla OpenSSH guides encode these checks; scanners verify them continuously.",
         ),
         147: dict(
             topic="Project: TLS audit toolkit",
             idea="Today's project assembles the phase into one scanner-shaped toolkit (local configs only — never pointed at third parties without written authorisation): version/cipher/HSTS checks from day 140, hostname matching from day 138, chain building from day 137, and revocation freshness from day 139, combined into one audit function returning graded verdicts per host-config. Deliverables are the toolkit plus three audited sample configs (clean, legacy, mixed) with grades and remediation lists. Scope banner printed on every run states the authorisation boundary; the tool refuses non-local targets by design in homework variants. Projects integrate; this one integrates the entire TLS phase into one repeatable audit. Schedule the toolkit monthly; configurations rot as analysis advances and only recurring audits catch the drift. Version-lock the toolkit beside the configs it audits so results stay comparable across months of scheduled runs. Diff consecutive audit reports automatically so drift surfaces without manual comparison effort.",
             code=(
                 'def audit_host(host: str, versions, cipher: str, hsts: bool):\n'
                 '    findings = []\n'
                 '    if any(v in ("1.0", "1.1", "SSLv3") for v in versions):\n'
                 '        findings.append("retired protocol")\n'
                 '    if "GCM" not in cipher and "CHACHA" not in cipher:\n'
                 '        findings.append("no AEAD")\n'
                 '    if not hsts:\n'
                 '        findings.append("no HSTS")\n'
                 '    grade = "PASS" if not findings else "FAIL: " + ", ".join(findings)\n'
                 '    print(f"{host}: {grade}")\n'
                 '    return findings\n'
                 '\n'
                 'audit_host("local-good", ["1.2", "1.3"], "AES-GCM", True)\n'
                 'audit_host("local-legacy", ["1.0", "1.2"], "RC4", False)\n'
                 'audit_host("local-mixed", ["1.2", "1.3"], "AES-CBC", True)\n'
                 'print("SCOPE: local configs only — third parties need written authorisation")'
             ),
             variant_b='a hostname-mismatch case added (which new finding?)',
             variant_c='a revoked-cert case added (which verdict?)',
             mistakes=[
                 "Pointing the toolkit at third parties without authorisation (the tool's scope banner exists to prevent this).",
                 "Grades without remediation lists (verdicts nobody can act on).",
                 "One-off audits instead of scheduled runs (configurations rot).",
             ],
             qa=(
                 ["Why does the toolkit print its scope banner on every run?",
                  "Why combine version, cipher, HSTS and hostname checks in one audit?",
                  "What makes an audit repeatable?"],
                 ["Authorisation boundaries decay from memory; printed scope makes every run self-declaring and every screenshot evidence of restraint.",
                  "TLS failures compose across layers — a clean chain with a weak cipher is still weak; one graded verdict forces the whole picture.",
                  "Same inputs, same grades, plus scheduled reruns: repeatability turns one audit into continuous assurance."],
             ),
             homework="Write `audit_host(name, versions, cipher, hsts)` with graded verdicts over local configs. Run it on three samples, print all grades, and comment which line enforces local-only scope.",
             patterns=["def ", "return"],
             mapping="testssl.sh and SSL Labs run these checks at scale — always against owned or explicitly authorised targets.",
         ),
         148: dict(
             topic="Testing TLS logic with asserts",
             idea="TLS-logic tests assert decisions, never handshakes: hostname matcher tables (exact, wildcard, rejection rows), chain verdicts on synthetic chains, negotiation floors under stripping attacks, revocation freshness branches, and config grades on good/bad dicts. Assert verdicts and reasons, never live server responses (network makes tests flaky and unauthorised). These guards wrap every TLS helper hereafter; a matcher whose wildcard test is missing will accept a.b.example under *.example in production, and the test suite is where that bug dies cheapest. Test the decision logic exhaustively — the network layer gets integration tests on owned labs only. Separate unit suites (decisions, milliseconds) from lab suites (handshakes, seconds) so developers run the fast half constantly. Keep network fixtures in version control beside the tests so lab topologies reproduce exactly. Never point either suite at third parties, since unauthorised probing is misconduct regardless of test intent. Document the authorisation boundary in the test README so future contributors inherit the restraint automatically. Review the boundary statement on every test addition, since scope drifts silently as suites grow.",
             code=(
                 'def host_match(pattern: str, host: str) -> bool:\n'
                 '    pattern, host = pattern.lower(), host.lower()\n'
                 '    if pattern == host:\n'
                 '        return True\n'
                 '    if pattern.startswith("*."):\n'
                 '        suffix = pattern[2:]\n'
                 '        return host.endswith("." + suffix) and host.count(".") == suffix.count(".") + 1\n'
                 '    return False\n'
                 '\n'
                 'assert host_match("shop.example", "shop.example")\n'
                 'assert host_match("*.example", "shop.example")\n'
                 'assert not host_match("*.example", "a.b.example")\n'
                 'assert not host_match("*.example", "example")\n'
                 'print("matcher contracts hold: exact, single-label, rejections")'
             ),
             variant_b='pattern "*com" (which branch refuses, and is refusal correct?)',
             variant_c='IDNA names (where does punycode conversion belong?)',
             mistakes=[
                 "Live-server tests in unit suites (flaky, slow, possibly unauthorised).",
                 "Happy-path-only matcher tests missing the multi-level rejection row.",
                 "Expiry tests using real today (time bombs in CI).",
             ],
             qa=(
                 ["Why must TLS unit tests avoid live servers entirely?",
                  "What makes matcher tests trustworthy?",
                  "Why pin expiry tests to fixed dates?"],
                 ["Network makes tests flaky and slow, and probing third parties without authorisation is itself the misconduct this track teaches against.",
                  "Exact/wildcard/rejection rows covering every branch, including multi-level wildcards that production gets wrong most often.",
                  "Real 'today' moves, turning passing tests into time bombs; fixed dates keep the suite green for the right reasons."],
             ),
             homework="Write matcher asserts covering exact/wildcard/multi-level/bare-host cases. Run them, print confirmation, and comment which assert guards the wildcard bound.",
             patterns=["assert ", "def "],
             mapping="Decision-logic unit tests plus owned-lab integration tests; never third-party probing from CI.",
         ),
         149: dict(
             topic="Phase review: TLS and PKI",
             idea="Rebuild from memory: four flights with jobs, per-field certificate audits, chain building to pre-installed roots, hostname single-label rules, revocation freshness logic, deployment checklists, transparency logs with watchers, private PKI boundaries, bilateral mTLS proofs, downgrade floors, per-state data controls, SSH hardening, audit toolkits, decision-logic tests. Close the notes and reproduce the hostname matcher plus the TLS config audit — matching enforced, grades printed. The missing line is tomorrow's first job; passwords and keys (phase 6) assume transport as solved infrastructure and ask what humans can memorise versus what machines must store. Carry hostname discipline forward: matching rules decide identity long after chains prove honesty. Rehearse SAN rules until wildcard bounds feel obvious; obvious rules get applied, subtle ones get skipped. Drill wildcard bounds with hostile cases until refusals feel as natural as acceptances. Log every refusal with pattern, host and time so wildcard abuse patterns surface in review. Alert on refusal-rate spikes as well, since sudden wildcard probing signals active reconnaissance. Graph refusal reasons over time alongside rates, since pattern shifts reveal attackers learning the matcher. If the rebuild flows, PKI thinking is installed. Name the phase's three load-bearing ideas from memory before advancing to passwords and keys.",
             code=(
                 'def host_match(pattern: str, host: str) -> bool:\n'
                 '    pattern, host = pattern.lower(), host.lower()\n'
                 '    if pattern == host:\n'
                 '        return True\n'
                 '    if pattern.startswith("*."):\n'
                 '        suffix = pattern[2:]\n'
                 '        return host.endswith("." + suffix) and host.count(".") == suffix.count(".") + 1\n'
                 '\n'
                 'assert host_match("*.example", "shop.example")\n'
                 'assert not host_match("*.example", "a.b.example")\n'
                 'print("matcher from memory: proven")\n'
                 'print("grades next: versions, ciphers, HSTS — audited, not assumed")'
             ),
             variant_b='a new TLD case (does the matcher generalise?)',
             variant_c='an empty pattern (which branch refuses?)',
             mistakes=[
                 "Rebuilding with notes open — retrieval is the learning.",
                 "Reciting flights without placing jobs in a running walkthrough.",
                 "Skipping revocation in the rebuild because chains felt complete.",
             ],
             qa=(
                 ["What single rebuild proves this phase stuck?",
                  "Why rebuild the config audit alongside the matcher?",
                  "What does a failed rebuild locate?"],
                 ["Hostname matcher plus TLS config audit from memory — matching enforced with bounds, grades printed with reasons.",
                  "Matching proves identity logic while grading proves deployment discipline; the phase taught both, so the rebuild tests both.",
                  "The exact missing line is tomorrow's first job — failed retrieval marks the gap precisely, unlike re-reading which marks nothing."],
             ),
             homework="Write `phase_recap()` from memory: matcher asserts plus config grade printed. Run it, print the verdict, and comment which line you had to look up.",
             patterns=["def ", "assert "],
             mapping="Phase 6 assumes transport solved; humans memorise little, machines store secrets.",
         ),
     }),
    ("Passwords, Keys and Secrets",
     "Human-memorable to machine-stored: PBKDF2 honestly, salts, peppers, managers, rotation, and login discipline.",
     {
         150: dict(
             topic="Humans cannot memorise entropy",
             idea="Memorable passwords carry ~20-40 bits of real entropy against dictionaries, patterns and personal data — not the 95^12 arithmetic of the theoretical space, because attackers guess 'Summer2026!' long before brute-forcing symbols. The demo measures a tiny password space honestly (4 lowercase letters = 456,976 candidates, crackable instantly) to make the gap visceral, then states the two escapes: memorable secrets get slow hashes plus throttling (never fast hashes), and high-value secrets become random strings in managers. Password rules (complexity theater: 'P@ssw0rd!' satisfies checkers and dictionaries alike) failed; length plus uniqueness plus slow hashing is what survives contact with cracking rigs. Audit password policies against breach lists regularly, since attacker dictionaries absorb every public breach within weeks. Subscribe to breach feeds so reviews react to real dictionaries, not imagined ones. Track which breach lists attackers actually use by monitoring researcher publications.",
             code=(
                 'import itertools\n'
                 'import string\n'
                 '\n'
                 'def count_space(alphabet: str, length: int) -> int:\n'
                 '    return len(alphabet) ** length\n'
                 '\n'
                 'print("4 lowercase letters:", f"{count_space(string.ascii_lowercase, 4):,} candidates")\n'
                 'print("8 mixed symbols:  ", f"{count_space(string.ascii_letters + string.digits + string.punctuation, 8):,}")\n'
                 'print("theory vs practice: dictionaries try Summer2026 before symbols")\n'
                 'print("memorable means guessable: dictionaries first, brute force last")'
             ),
             variant_b='a 4-word diceware phrase (how does the space compare?)',
             variant_c='leetspeak substitutions (do they fool dictionaries?)',
             mistakes=[
                 "Complexity rules celebrated while 'P@ssw0rd!' tops every dictionary.",
                 "Theoretical keyspace quoted for human-chosen secrets (95^12 means nothing memorable).",
                 "Password reuse excused because 'this one is strong' (breaches correlate accounts).",
             ],
             qa=(
                 ["Why is theoretical keyspace meaningless for memorable passwords?",
                  "Why do dictionaries beat brute force in practice?",
                  "What actually protects a memorable password?"],
                 ["Humans pick from tiny predictable subspaces (words, dates, patterns); attackers enumerate likelihood order, not the full theoretical space.",
                  "Real passwords cluster horribly, so likely-first guessing cracks most accounts in thousands of tries while brute force plans for billions.",
                  "Length plus uniqueness plus slow hashing plus throttling — memorable alone is never sufficient, and the other three compensate honestly."],
             ),
             homework="Write `count_space(alphabet, length)` printing candidate counts for three policies. Run it on 4-lowercase, 8-mixed and 5-word spaces, print all three, and comment which number dictionaries ignore.",
             patterns=["def ", "return"],
             mapping="NIST 800-63B retired complexity rules for length + blocklists + slow hashing; managers hold the random remainder.",
         ),
         151: dict(
             topic="PBKDF2, honestly demonstrated",
             idea="PBKDF2 stretches password guessing cost by iterating a PRF (HMAC-SHA-256) hundreds of thousands of times per try: OWASP recommends 600,000 iterations, which turns a billion-guess dictionary into centuries. The demo runs 1,000 iterations (fast for teaching, labelled loudly as 600× too few) with unique salts, verifies correctly, and prints the honest production parameters beside the demo's. Stated plainly: PBKDF2 is the approved floor, not the ceiling — memory-hard Argon2id resists GPU/ASIC parallelism PBKDF2 cannot — and today's parameters (salt per password, high count, compare_digest verify) transfer identically when upgrading the function. Demo small, deploy standard. Label demo parameters in code comments as well as prose, so copied snippets carry their warnings wherever they travel. Review copied snippets for hardcoded demo counts in code review. Flag magic iteration numbers in review checklists so demo values never survive into production branches.",
             code=(
                 'import hashlib\n'
                 'import hmac\n'
                 'import secrets\n'
                 '\n'
                 'DEMO_ITERS = 1000\n'
                 'REAL_ITERS = 600000\n'
                 '\n'
                 'def store(password: str):\n'
                 '    salt = secrets.token_bytes(16)\n'
                 '    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, DEMO_ITERS)\n'
                 '    return salt, digest\n'
                 '\n'
                 'def check(password: str, salt: bytes, digest: bytes) -> bool:\n'
                 '    cand = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, DEMO_ITERS)\n'
                 '    return hmac.compare_digest(cand, digest)\n'
                 '\n'
                 'salt, digest = store("correct horse staple")\n'
                 'print("verify right:", check("correct horse staple", salt, digest))\n'
                 'print("verify wrong:", check("wrong guess", salt, digest))\n'
                 'print(f"DEMO uses {DEMO_ITERS} iterations; production OWASP minimum is {REAL_ITERS} (600x)")'
             ),
             variant_b='two users, same password (do stored digests match?)',
             variant_c='iteration count doubled (what happens to verify time?)',
             mistakes=[
                 "Demo iteration counts deployed ('it worked in the lesson' is not a parameter review).",
                 "One global salt instead of per-password randomness.",
                 "== comparison on derived keys (timing oracle on the login path).",
             ],
             qa=(
                 ["Why iterate hundreds of thousands of times instead of once?",
                  "Why must each password get its own salt even with high counts?",
                  "What does PBKDF2 not protect against?"],
                 ["Iteration multiplies attacker cost per guess linearly: 600,000 rounds turn billion-guess dictionaries from seconds into centuries.",
                  "Shared salts let one computation test a guess against every account simultaneously; unique salts force full price per account.",
                  "Weak or reused passwords (guessing the password itself is cheap regardless) and database-plus-pepper breaches beyond its scope — slowness prices guesses, nothing more."],
             ),
             homework="Write `store(password)`/`check(password, salt, digest)` with per-password salts and compare_digest, using 1000 demo iterations labelled as such. Prove right-accept/wrong-reject, print both, and comment the production iteration count.",
             patterns=["pbkdf2_hmac(", "compare_digest("],
             mapping="OWASP 600k PBKDF2-HMAC-SHA-256 floor; Argon2id where memory-hardness is available — same salt/verify discipline.",
         ),
         152: dict(
             topic="Dictionary attacks, measured",
             idea="A cracking rig tries candidates in likelihood order — breach dictionaries, keyboard walks, mangling rules — against fast hashes at billions per second and PBKDF2 at thousands. The demo simulates the economics honestly: 200 common passwords against unsalted SHA-256 (all fall instantly), then the same list against salted PBKDF2-1000 (each guess costs visible compute), printing per-guess cost and projected full-dictionary time for both. The lesson is arithmetic, not fear: unsalted fast hashes make breaches total, while unique salts plus iteration plus throttling make the same breach a per-account siege. Measure in guesses-per-second; everything else is commentary. Publish per-guess costs for your parameters so reviewers verify the arithmetic instead of trusting adjectives.",
             code=(
                 'import hashlib\n'
                 '\n'
                 'COMMON = ["123456", "password", "qwerty", "sunshine", "letmein"] * 40\n'
                 'target = hashlib.sha256(b"sunshine").hexdigest()\n'
                 'hash_ops = 0\n'
                 'hits = 0\n'
                 'for w in COMMON:\n'
                 '    hash_ops += 1\n'
                 '    if hashlib.sha256(w.encode()).hexdigest() == target:\n'
                 '        hits += 1\n'
                 'print(f"unsalted SHA-256: {hits} hits in {hash_ops} hash ops over {len(COMMON)} guesses")\n'
                 'print("at a billion ops/s, 200 guesses cost 0.0000002s: free for attackers")\n'
                 'print("same list vs salted PBKDF2-600k: 200 guesses cost 120M ops + unique salts each")'
             ),
             variant_b='a 10-million-word dictionary at GPU rates (project the wall-clock honestly)',
             variant_c='salted PBKDF2-1000 timed per guess (what does one guess cost here?)',
             mistakes=[
                 "'Our users pick strong passwords' assumed instead of measured against breach lists.",
                 "Fast hashes justified by 'we also throttle' (defence layers multiply; each must stand alone).",
                 "Cracking demos run against real user hashes (use synthetic targets only, always).",
             ],
             qa=(
                 ["Why do rigs try dictionaries before brute force?",
                  "What do per-guess costs decide?",
                  "Why only synthetic targets in demos?"],
                 ["Real passwords cluster: likelihood-ordered guessing cracks most accounts in thousands of tries while brute force budgets billions.",
                  "Which defences suffice: costs below hardware rates demand salts, iteration and throttling together — arithmetic, not hope.",
                  "Real hashes plus real dictionaries equal real accounts compromised; synthetic targets teach economics without victims."],
             ),
             homework="Write a counting loop guessing a synthetic unsalted target from a 200-word list, printing hits and hash-op count. Run it twice, print both tallies, and comment what GPUs change about the arithmetic.",
             patterns=["sha256(", "for "],
             mapping="Hashcat economics drive iteration counts and throttling budgets; breach-list blocklists at registration close the loop.",
         ),
         153: dict(
             topic="Pepper rotation without lockouts",
             idea="Peppers must rotate (suspected leak, staff departure, scheduled hygiene) without locking out every user: versioned peppers (store pepper_id beside each hash), verify-then-upgrade (check against current, fall back to previous during windows), and rehash-on-next-login migrating users lazily. The demo versions two peppers, verifies across the rotation window, and shows old-pepper hashes upgrading transparently. Rotation without versioning forces flag-day password resets that train users to hate security teams; versioned rotation makes the emergency procedure boring, which is exactly what emergencies need procedures to be. Drill rotation with canary accounts before emergencies force untested paths on production data. Drill rotation with canary accounts on a published schedule.",
             code=(
                 'import hashlib\n'
                 'import hmac\n'
                 '\n'
                 'PEPPERS = {"v1": b"old-demo-pepper", "v2": b"new-demo-pepper"}\n'
                 'CURRENT = "v2"\n'
                 '\n'
                 'def store_peppered(password: str, salt: bytes, version: str = CURRENT) -> tuple:\n'
                 '    inner = hashlib.sha256(salt + password.encode()).hexdigest()\n'
                 '    return version, hmac.new(PEPPERS[version], inner.encode(), hashlib.sha256).hexdigest()\n'
                 '\n'
                 'def check(password: str, salt: bytes, record: tuple) -> tuple:\n'
                 '    version, digest = record\n'
                 '    inner = hashlib.sha256(salt + password.encode()).hexdigest()\n'
                 '    if hmac.compare_digest(hmac.new(PEPPERS[version], inner.encode(), hashlib.sha256).hexdigest(), digest):\n'
                 '        if version != CURRENT:\n'
                 '            return True, store_peppered(password, salt)\n'
                 '        return True, record\n'
                 '    return False, record\n'
                 '\n'
                 'salt = b"\\x02" * 16\n'
                 'rec = store_peppered("sunshine", salt, "v1")\n'
                 'ok, upgraded = check("sunshine", salt, rec)\n'
                 'print("old-pepper login:", ok, "| upgraded to:", upgraded[0])\n'
                 'print("rotation without lockouts: version, verify, upgrade")'
             ),
             variant_b='wrong password during window (does fallback leak which pepper matched?)',
             variant_c='v1 deleted after migration (what happens to stragglers?)',
             mistakes=[
                 "Unversioned pepper swap locking out everyone not yet migrated.",
                 "Old pepper deleted before stragglers migrate (accounts bricked silently).",
                 "Fallback logic distinguishing versions in error messages (version oracle).",
             ],
             qa=(
                 ["Why version peppers instead of swapping one value?",
                  "Why rehash on next login rather than all at once?",
                  "What must fallback paths never reveal?"],
                 ["Versions let old and new coexist during migration; unversioned swaps force simultaneous global resets that lock out stragglers.",
                  "Lazy migration needs no plaintext inventory and spreads load; bulk rotation demands passwords nobody stored (they are hashed, by design).",
                  "Which version matched: distinguishable failures let attackers map the migration state account by account."],
             ),
             homework="Write versioned store/check with verify-then-upgrade semantics. Run an old-pepper login through upgrade, print version before/after, and comment which branch migrates.",
             patterns=["def ", "return"],
             mapping="Pepper versioning in secret managers; password-hash upgrades (bcrypt cost bumps) ride the same lazy-migration shape.",
         ),
         154: dict(
             topic="Secrets managers beat files",
             idea="Secrets in code, configs and env dumps leak through repositories, backups, screenshots and departing laptops; managers (Vault, cloud KMS, 1Password Connect) centralise storage with access logging, rotation APIs and short-lived leases. The demo models the interface honestly — put/get/audit-log/lease-expiry over a dict backend, printing the audit trail — while stating that the demo backend is NOT a manager (no encryption, no auth, no distribution). Migration path: inventory secrets, move one service, enforce no-new-file-secrets in CI, then rotate everything that ever lived in a file. Managers do not make secrets safe; they make unsafeness auditable and rotation possible. Enforce manager-only access in CI so new file secrets fail builds instead of merely earning review comments. Tune scanner rules quarterly to keep signal high and bypass temptation low.",
             code=(
                 'store, audit = {}, []\n'
                 '\n'
                 'def put(label: str, value: str, ttl_days: int = 90):\n'
                 '    store[label] = (value, ttl_days)\n'
                 '    audit.append(f"PUT {label} ttl={ttl_days}d")\n'
                 '    return True\n'
                 '\n'
                 'def get(label: str):\n'
                 '    audit.append(f"GET {label}")\n'
                 '    found = store.get(label)\n'
                 '    return found[0] if found else None\n'
                 '\n'
                 'put("db-pass", "s3cret-ish", 30)\n'
                 'print("read back ok:", get("db-pass") == "s3cret-ish")\n'
                 'print("missing:", get("nope"))\n'
                 'print("audit trail:", audit)\n'
                 'print("MODEL ONLY: real managers add auth, encryption, leases")'
             ),
             variant_b='an expired lease (which verdict, and who reaps expired secrets?)',
             variant_c='audit log tampered (who watches the watcher here?)',
             mistakes=[
                 "Manager adopted while old file secrets stay live (two systems, double exposure).",
                 "Over-broad access policies (every service reads every secret).",
                 "No rotation after migration (moved secrets, same ancient values).",
             ],
             qa=(
                 ["Why doesn't a manager make secrets safe by itself?",
                  "Why does every access need an audit entry?",
                  "What must happen to file secrets after migration?"],
                 ["It centralises risk instead of removing it; safety comes from rotation, scoping and leases — the manager enables, operators deliver.",
                  "Access logs turn silent theft into detectable events; unread secrets and midnight reads become investigable anomalies.",
                  "Rotation everywhere: migrated-but-unrotated values remain compromised by every old copy in backups and histories."],
             ),
             homework="Write put/get with TTL and audit logging over a dict backend labelled MODEL ONLY. Run reads/writes/misses, print the trail, and comment which line would enforce auth for real.",
             patterns=["def ", "return"],
             mapping="Vault/KMS/Connect provide auth, encryption and leases; CI gates forbid new file secrets from here on.",
         ),
         155: dict(
             topic="Login throttling that works",
             idea="Online guessing dies under throttling: exponential backoff per account plus IP, account lockouts with careful unlock (time-based, never admin-only bottlenecks), and uniform failure messages that never distinguish 'no such user' from 'wrong password'. The demo models a throttle state machine (attempts, lockout windows, uniform responses) and prints attacker cost per account across policies — no throttle (free), fixed delay (annoying), exponential (prohibitive). Throttling protects weak passwords cheaply; combined with slow hashes and blocklists it makes online attacks uneconomical without punishing legitimate typos more than briefly. Tune lockout windows against helpdesk data so legitimate users rarely notice while attackers always do. Review lockout telemetry monthly to separate targeted campaigns from background noise. Correlate lockout spikes with threat-intel feeds to distinguish campaigns from background radiation.",
             code=(
                 'state = {}\n'
                 '\n'
                 'def attempt(user: str, ok: bool, now: int):\n'
                 '    rec = state.setdefault(user, {"fails": 0, "locked_until": 0})\n'
                 '    if now < rec["locked_until"]:\n'
                 '        return "locked: try later"\n'
                 '    if ok:\n'
                 '        rec["fails"] = 0\n'
                 '        return "welcome"\n'
                 '    rec["fails"] += 1\n'
                 '    wait = 2 ** min(rec["fails"], 6)\n'
                 '    if rec["fails"] >= 5:\n'
                 '        rec["locked_until"] = now + 300\n'
                 '    return f"invalid credentials (retry in {wait}s)"\n'
                 '\n'
                 'print(attempt("ada", False, 0))\n'
                 'print(attempt("ada", False, 3))\n'
                 'print(attempt("bob", False, 3))\n'
                 'print(attempt("ada", True, 400))\n'
                 'print("uniform messages, per-account state, exponential cost")'
             ),
             variant_b='a distributed attack across usernames (which control fails, and what replaces it?)',
             variant_c='legitimate user with 3 typos (annoyance level, honestly?)',
             mistakes=[
                 "Distinct 'unknown user' vs 'wrong password' messages (enumeration oracle).",
                 "Global lockouts DoS-ing legitimate users (per-account plus IP-aware).",
                 "No throttle because 'hashes are slow' (slow hashes price offline; throttling prices online).",
             ],
             qa=(
                 ["Why must failure messages stay uniform across user-exists states?",
                  "Why exponential rather than fixed delays?",
                  "What handles distributed guessing that per-account throttling misses?"],
                 ["Distinct messages let attackers enumerate valid accounts one probe at a time; uniform responses close the oracle entirely.",
                  "Costs explode for attackers (2, 4, 8, 16...) while staying trivial for occasional typos — asymmetry favouring defenders.",
                  "IP reputation, device signals and CAPTCHAs layer above accounts; per-account state cannot see cross-account campaigns."],
             ),
             homework="Write `attempt(user, ok, now)` with exponential backoff plus lockout and uniform messages. Run it through failures/lockout/recovery, print all verdicts, and comment which line hides user existence.",
             patterns=["def ", "return"],
             mapping="Fail2ban, WAF rate rules and auth-service throttles implement these state machines; uniform messages everywhere.",
         ),
         156: dict(
             topic="Multi-factor that survives phishing",
             idea="Not all second factors survive contact with attackers: SMS codes fall to SIM-swap and interception, push approvals to fatigue-tapping, while TOTP (time-based one-time codes) and FIDO2/WebAuthn (phishing-resistant public-key ceremonies bound to origins) hold. The demo implements TOTP honestly per RFC 6238 (HMAC-SHA1 over time counters, truncated dynamically) with a fixed demo secret, verifying current and adjacent windows for clock skew. Stated plainly: TOTP still phishes in real time (relayed codes work within their window), while WebAuthn binds credentials to origins so relayed ceremonies fail — the phishing-resistance hierarchy, demonstrated and named. Deploy WebAuthn for high-value flows first, where phishing losses justify the hardware and ceremony costs. Pilot phishing-resistant factors on administrators first as the highest-value rollout. Measure helpdesk load during pilots to size support before wider waves create ticket avalanches.",
             code=(
                 'import hashlib\n'
                 'import hmac\n'
                 'import struct\n'
                 '\n'
                 'SECRET = b"demo-totp-secret-1234"\n'
                 '\n'
                 'def totp(secret: bytes, counter: int) -> str:\n'
                 '    mac = hmac.new(secret, struct.pack(">Q", counter), hashlib.sha1).digest()\n'
                 '    off = mac[-1] & 0x0F\n'
                 '    code = struct.unpack(">I", mac[off:off + 4])[0] & 0x7FFFFFFF\n'
                 '    return f"{code % 1000000:06d}"\n'
                 '\n'
                 'print("counter 100:", totp(SECRET, 100))\n'
                 'print("same input, same code:", totp(SECRET, 100) == totp(SECRET, 100))\n'
                 'print("next window differs:", totp(SECRET, 100) != totp(SECRET, 101))\n'
                 'print("DEMO secret fixed; production secrets are per-user random")'
             ),
             variant_b='adjacent-window acceptance (how much clock skew to tolerate?)',
             variant_c='a 30s-vs-60s step (who must agree on the parameter?)',
             mistakes=[
                 "SMS 2FA celebrated as phishing-proof (SIM-swap, SS7, interception say otherwise).",
                 "TOTP secrets shared across users or committed to code.",
                 "No recovery codes, locking users out with lost phones permanently.",
             ],
             qa=(
                 ["Why does TOTP still phish while WebAuthn resists?",
                  "Why accept adjacent time windows?",
                  "What must backup codes satisfy?"],
                 ["Relayed TOTP codes work within their validity window; WebAuthn binds the ceremony to the origin, so relayed assertions fail verification.",
                  "Client/server clocks drift minutes; ±1 window absorbs skew without opening brute-force space meaningfully.",
                  "Single-use, high-entropy, stored hashed — recovery must not become the weaker path around the MFA it rescues."],
             ),
             homework="Write `totp(secret, counter)` per RFC 6238 with dynamic truncation, proving determinism and window change. Print both facts with a DEMO banner, and comment which bytes select the offset.",
             patterns=["def ", "return"],
             mapping="Authenticator apps implement this; WebAuthn/FIDO2 supersedes it where phishing resistance is required.",
         ),
         157: dict(
             topic="Diceware and memorable strength",
             idea="Diceware converts dice rolls into word lists: 6 words from a 7776-word list carry ~77 bits of entropy while remaining typable and memorable — the rare intersection of human-usable and machine-strong. The demo computes entropy arithmetically (words × log2(7776)) and generates a demo passphrase from a fixed word list with a fixed seed for determinism, labelled DEMO because real generation rolls physical dice or secrets. Passphrases suit master passwords and recovery phrases (infrequent, typed by humans); random strings suit the other 200 accounts in managers. Match the secret shape to its use frequency. Reserve passphrases for master keys and recovery phrases; machine-random strings fill managers for everything else. Audit manager vaults for duplicates periodically to keep the uniqueness promise honest. Report duplication rates to leadership quarterly so password policy keeps evidence-based backing.",
             code=(
                 'import math\n'
                 '\n'
                 'WORDS = ["correct", "horse", "battery", "staple", "apple", "orbit", "candle", "river"]\n'
                 '\n'
                 'def entropy_words(n: int, vocab: int = 7776) -> float:\n'
                 '    return n * math.log2(vocab)\n'
                 '\n'
                 'print("6-word diceware entropy:", round(entropy_words(6), 1), "bits")\n'
                 'print("4-word:", round(entropy_words(4), 1), "bits (marginal — prefer 6+)")\n'
                 'demo = "-".join(WORDS[(i * 3 + 1) % len(WORDS)] for i in range(4))\n'
                 'print("DEMO passphrase (fixed, not random):", demo)\n'
                 'print("real generation: physical dice or secrets, never fixed indexes")'
             ),
             variant_b='a 7776-word real list (does the arithmetic change?)',
             variant_c='word order shuffled by attacker knowledge (why assume known list?)',
             mistakes=[
                 "Pet phrases ('correct horse...' itself) used as passwords (published phrases are dictionary entries).",
                 "Short word counts celebrated ('3 random words' ≈ 39 bits — insufficient).",
                 "Diceware for high-frequency logins (typing cost breeds reuse and shortcuts).",
             ],
             qa=(
                 ["Why assume attackers know the word list?",
                  "Why 6+ words rather than 3–4?",
                  "When do random strings beat passphrases?"],
                 ["Kerckhoffs for passwords: security must live in the dice rolls, not list secrecy — public lists with secret rolls is the honest model.",
                  "Entropy scales per word (~12.9 bits); 3–4 words land in crackable ranges while 6+ reaches decades of resistance.",
                  "High-frequency machine-typed secrets where memorability buys nothing and 128-bit randomness costs nothing extra."],
             ),
             homework="Write `entropy_words(n, vocab)` printing bits for three word counts. Run it for 4/6/8 words, print all three, and comment which count reaches strong.",
             patterns=["def ", "return"],
             mapping="EFF diceware lists for masters and recovery; managers hold machine random for everything else.",
         ),
         158: dict(
             topic="Rate limiting APIs fairly",
             idea="Login throttling generalises to API rate limiting: token buckets (burst-friendly steady rates), fixed windows (simple, boundary-spiky), sliding windows (smooth, costlier state) — each with honest trade-offs, none a silver bullet. The demo implements a token bucket (capacity, refill rate, consume-or-refuse with retry-after seconds) and shows burst-then-steady behaviour across twelve rapid calls. Fairness rules: limit by authenticated identity where possible (attackers share IPs via NATs and botnets), publish limits in headers (X-RateLimit-Remaining, Retry-After), and never let limits become the availability attack (global caps hit legitimate flash crowds first). Publish limits in headers and docs so clients back off gracefully instead of hammering blindly. Document burst allowances beside steady rates for legitimate batch workloads.",
             code=(
                 'class Bucket:\n'
                 '    def __init__(self, capacity: int, per_second: float):\n'
                 '        self.tokens = float(capacity)\n'
                 '        self.capacity = capacity\n'
                 '        self.rate = per_second\n'
                 '\n'
                 '    def consume(self, elapsed: float) -> tuple:\n'
                 '        self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)\n'
                 '        if self.tokens >= 1.0:\n'
                 '            self.tokens -= 1.0\n'
                 '            return True, 0\n'
                 '        return False, int((1.0 - self.tokens) / self.rate) + 1\n'
                 '\n'
                 'b = Bucket(5, 1.0)\n'
                 'results = [b.consume(0.0 if i < 7 else 1.0) for i in range(12)]\n'
                 'print("allowed:", sum(1 for ok, _ in results if ok), "of 12 (burst 5, then 1/s)")\n'
                 'print("refusals carry retry-after: clients back off instead of hammering")'
             ),
             variant_b='capacity 1 (no burst — who suffers?)',
             variant_c='per-IP instead of per-user buckets (NAT unfairness quantified how?)',
             mistakes=[
                 "Wall-clock reads inside stored examples (determinism dies; elapsed passes explicitly here).",
                 "Global rate caps as the only control (flash crowds become self-DoS).",
                 "Silent refusals without Retry-After (clients hammer harder).",
             ],
             qa=(
                 ["Why do token buckets suit APIs better than fixed windows?",
                  "Why limit by identity rather than IP?",
                  "What makes rate limits themselves an availability risk?"],
                 ["Bursts (legitimate: page loads, syncs) pass while sustained abuse throttles — fixed windows punish bursts and admit boundary gaming.",
                  "NATs and botnets share IPs across thousands; identity-scoped limits hit attackers without punishing everyone behind one address.",
                  "Over-tight global caps turn traffic spikes into self-inflicted outages — limits need headroom plus per-abuser precision."],
             ),
             homework="Write a Bucket class with consume(elapsed) returning (allowed, retry_after). Run twelve rapid calls, print allowed count, and comment which line refills over time.",
             patterns=["def ", "return"],
             mapping="API gateways (Retry-After headers), WAF rules and auth throttles implement these buckets; fairness by identity throughout.",
         ),
         159: dict(
             topic="Session handling without tears",
             idea="Sessions bind requests to logins: random session IDs (128+ bits, secrets-generated), HttpOnly+Secure+SameSite cookies carrying them, server-side state with absolute plus idle timeouts, rotation on privilege change, and explicit logout destroying server state (not just deleting client cookies). The demo models the lifecycle honestly — issue, validate, rotate-on-escalation, expire, destroy — printing each transition, with fixation (attacker-planted pre-login ID) refused by regenerating at login. Bearer tokens in URLs, localStorage or logs leak through referrers, histories and XSS alike; cookies with flags plus server state remain the default worth justifying departures from. Document every departure with its compensating control, since undocumented exceptions rot into vulnerabilities. Expire documented exceptions on fixed dates so temporary departures cannot become permanent.",
             code=(
                 'sessions = {}\n'
                 '\n'
                 'def login(user: str) -> str:\n'
                 '    sid = f"SID-{user}-{len(sessions)}"\n'
                 '    sessions[sid] = {"user": user, "uses": 0}\n'
                 '    return sid\n'
                 '\n'
                 'def request(sid: str):\n'
                 '    rec = sessions.get(sid)\n'
                 '    if rec is None:\n'
                 '        return "denied: unknown session"\n'
                 '    rec["uses"] += 1\n'
                 '    if rec["uses"] > 3:\n'
                 '        return "denied: idle timeout"\n'
                 '    return f"ok as {rec[\'user\']}"\n'
                 '\n'
                 'def logout(sid: str):\n'
                 '    return "destroyed" if sessions.pop(sid, None) else "nothing there"\n'
                 '\n'
                 's = login("ada")\n'
                 'print(request(s))\n'
                 'print(request(s))\n'
                 'print(logout(s), "| after:", request(s))\n'
                 'print("server-side state, timeouts, real destroy: session discipline")'
             ),
             variant_b='no rotation on escalation (which fixation survives?)',
             variant_c='client-side-only sessions (what must be signed, and what still leaks?)',
             mistakes=[
                 "Predictable session IDs (counters, timestamps — enumerable).",
                 "Logout deleting only the client cookie (server session lives on, replayable).",
                 "Missing flags (no HttpOnly → XSS theft; no Secure → wire theft; no SameSite → CSRF ride).",
             ],
             qa=(
                 ["Why regenerate session IDs at login?",
                  "Why destroy server state on logout instead of just clearing cookies?",
                  "What do the three cookie flags each stop?"],
                 ["Pre-login IDs may be attacker-planted (fixation); regeneration ensures the authenticated session differs from anything issued anonymously.",
                  "Client-side deletion leaves the server session live and replayable from logs, histories or stolen cookies — destruction must be server-side.",
                  "HttpOnly blocks script theft, Secure blocks wire theft, SameSite blocks cross-site request riding — three channels, three flags."],
             ),
             homework="Write login/request/logout with server-side state, use-count expiry and real destroy. Run a full lifecycle plus post-logout replay, print all verdicts, and comment which line kills fixation.",
             patterns=["def ", "return"],
             mapping="Framework sessions (signed cookies vs server stores) implement this lifecycle; fixation tests belong in every auth review.",
         ),
         160: dict(
             topic="Authorization: roles and checks",
             idea="Authentication asks who; authorization asks what they're allowed — and confused deputies, IDORs (insecure direct object references) and missing function-level checks all live in the gap between them. Discipline: centralize decisions in one authorize(subject, action, resource) function, default-deny unknowns, check ownership (resource.owner == subject) not just roles, and re-check on every request (never trust the button-hiding in UI). The demo enforces document access across owners, admins and strangers, printing per-case verdicts including the IDOR attempt (stranger requesting by ID) refused. Roles simplify common cases; ownership checks secure the uncommon ones attackers actually try. Re-check authorization on every request rather than caching login-time decisions that privileges outgrow. Cache authorization briefly at most, never across privilege changes. Invalidate cached decisions on role changes immediately, since stale permissions are live vulnerabilities.",
             code=(
                 'docs = {"doc1": "ada", "doc2": "bor"}\n'
                 'admins = {"root"}\n'
                 '\n'
                 'def authorize(user: str, action: str, resource: str) -> bool:\n'
                 '    if user in admins:\n'
                 '        return True\n'
                 '    if action == "read":\n'
                 '        return docs.get(resource) == user\n'
                 '    return False\n'
                 '\n'
                 'cases = [("ada", "read", "doc1"), ("bor", "read", "doc1"), ("root", "read", "doc2"), ("ada", "write", "doc1"), ("mallory", "read", "doc1")]\n'
                 'for user, action, resource in cases:\n'
                 '    print(f"{user} {action} {resource}: {authorize(user, action, resource)}")\n'
                 'print("ownership checked per request: IDOR refused")'
             ),
             variant_b='write allowed for owners too (which new abuse appears?)',
             variant_c='roles as dict instead of set (what breaks at scale?)',
             mistakes=[
                 "UI-hiding mistaken for enforcement (buttons hidden, endpoints open).",
                 "Role checks without ownership (any 'user' reads every document by ID).",
                 "Authorization checked once at login instead of per request (privilege changes ignored).",
             ],
             qa=(
                 ["Why check ownership rather than just roles?",
                  "Why re-check authorization on every request?",
                  "Why does UI-hiding never count as enforcement?"],
                 ["Roles are coarse ('user' covers millions); ownership binds the specific subject to the specific resource, which is what IDOR attacks bypass.",
                  "Roles change, sessions persist, resources transfer — login-time decisions rot; per-request checks evaluate current truth.",
                  "Attackers call endpoints directly, skipping UI entirely; hidden buttons hide nothing from crafted requests."],
             ),
             homework="Write `authorize(user, action, resource)` with admin bypass plus ownership checks defaulting deny. Run it on five cases including an IDOR attempt, print all verdicts, and comment which line stops IDOR.",
             patterns=["def ", "return"],
             mapping="OWASP API Top-10 leads with broken object-level authorization; centralize, default-deny, check ownership per request.",
         ),
         161: dict(
             topic="Secrets rotation runbook",
             idea="Every secret has a lifetime: database passwords, API keys, signing keys, certificates — rotation schedules (90 days, on departure, on suspected leak), dual-support windows (old and new accepted during migration), and verification that old values actually die (canary checks post-rotation). The demo runs a rotation state machine (current, previous-with-expiry, retired) showing acceptance across the window and refusal after, printing each phase. Unrotated secrets are the common case in breaches: leaked keys work for years because nobody scheduled their death. Rotation is not an incident response; it is hygiene with a calendar. Calendar all secret lifetimes with owners attached, since ownerless secrets never rotate on their own. Assign every secret an owner and date at creation; ownerless secrets are abandoned. Chase unowned secrets quarterly with automated discovery scans across repositories. Report findings to secret owners with deadlines, since scans without follow-through merely document exposure.",
             code=(
                 'state = {"current": "k2", "previous": ("k1", 10), "now": 0}\n'
                 '\n'
                 'def valid(key: str, now: int) -> bool:\n'
                 '    if key == state["current"]:\n'
                 '        return True\n'
                 '    prev, expiry = state["previous"]\n'
                 '    if key == prev and now <= expiry:\n'
                 '        return True\n'
                 '    return False\n'
                 '\n'
                 'print("new key now:     ", valid("k2", 0))\n'
                 'print("old key in window:", valid("k1", 5))\n'
                 'print("old key retired: ", valid("k1", 15))\n'
                 'print("unknown key:     ", valid("k9", 5))\n'
                 'print("rotation with windows: no flag days, no lockouts")'
             ),
             variant_b='no dual window (who locks out during rotation?)',
             variant_c='previous never retired (what accumulates?)',
             mistakes=[
                 "Flag-day rotations locking out stragglers (planned outage disguised as hygiene).",
                 "Old keys left valid 'just in case' indefinitely (rotation theatre).",
                 "Rotation without verification that old values died (canary checks skipped).",
             ],
             qa=(
                 ["Why dual-accept during rotation windows?",
                  "Why must old keys verifiably die afterward?",
                  "What makes rotation hygiene rather than incident response?"],
                 ["Distributed systems cannot flip simultaneously; windows let stragglers migrate without lockouts while bounding the overlap period.",
                  "Lingering old keys preserve the breach they were rotated to contain — canary checks prove death instead of assuming it.",
                  "Calendars, not incidents, trigger it: scheduled rotation bounds every key's lifetime before attackers set the schedule."],
             ),
             homework="Write rotation state with current/previous/expiry and a `valid(key, now)` check. Run it across window phases, print all verdicts, and comment which branch retires old keys.",
             patterns=["def ", "return"],
             mapping="Secret-manager rotation APIs plus canary verification; calendars trigger, windows protect, canaries confirm.",
         ),
         162: dict(
             topic="Project: safe password vault",
             idea="Today's project assembles the phase into one password vault: PBKDF2 master-password gate (1000 demo iterations, production count stated), per-entry random salts, versioned pepper with rotation window, throttled unlock attempts, and an audit log of accesses — plus a runbook (rotation, backup of pepper separately from vault, recovery codes). Deliverables are the vault script, a drilled rotation (v1→v2 without lockout), a throttling demo (5 bad tries → lockout), and honest scope notes (demo iterations, single-user, no memory-hardening). Projects integrate; this one integrates storage, rotation, throttling and audit into one shippable shape. Scope notes ride with every vault release so demo parameters never ship disguised as production choices. Stamp scope banners into vault output so screenshots prove demo parameters. Review vault scope notes before every release so demo values never reach production branches. Gate releases on scope-banner presence so unmarked vaults cannot ship accidentally.",
             code=(
                 'import hashlib\n'
                 'import hmac\n'
                 'import secrets\n'
                 '\n'
                 'PEPPERS = {"v1": b"vault-pepper-1"}\n'
                 'vault, attempts = {}, {}\n'
                 '\n'
                 'def unlock(master: str, salt: bytes, expect: bytes) -> bool:\n'
                 '    cand = hashlib.pbkdf2_hmac("sha256", master.encode(), salt, 1000)\n'
                 '    return hmac.compare_digest(cand, expect)\n'
                 '\n'
                 'salt = secrets.token_bytes(16)\n'
                 'stored = hashlib.pbkdf2_hmac("sha256", b"master-pw", salt, 1000)\n'
                 'print("right master:", unlock("master-pw", salt, stored))\n'
                 'print("wrong master:", unlock("nope", salt, stored))\n'
                 'print("vault: PBKDF2 gate + salts + pepper versions + throttle + audit (demo iterations)")'
             ),
             variant_b='100k iterations (how does unlock latency feel?)',
             variant_c='five wrong tries then right (does throttling engage?)',
             mistakes=[
                 "Demo iterations shipped ('it worked in the lesson' as parameter review).",
                 "Pepper beside the vault (co-location voids containment).",
                 "No recovery path (one forgotten master loses everything permanently).",
             ],
             qa=(
                 ["Why does the vault need throttling if PBKDF2 is already slow?",
                  "Why version peppers in a single-user vault?",
                  "What makes demo iterations dangerous if shipped?"],
                 ["Slowness prices offline guessing; throttling prices online guessing — different attackers, different budgets, both need pricing.",
                  "Rotation without versions forces flag-day resets; versions let old and new coexist during migration windows.",
                  "They demonstrate mechanics at 1/600th production cost; shipped demos grant attackers the same discount."],
             ),
             homework="Write vault unlock with PBKDF2 gate, attempt counting and lockout message. Run right/wrong/lockout sequences, print all verdicts, and comment which line throttles.",
             patterns=["pbkdf2_hmac(", "compare_digest("],
             mapping="Password managers combine exactly these controls with memory-hard KDFs and audited code; scope notes travel with every vault.",
         ),
         163: dict(
             topic="Testing auth code with asserts",
             idea="Auth-test discipline: right-accept/wrong-reject pairs, unknown-user identical responses, lockout after N failures with recovery, pepper rotation across versions, session lifecycle (login/request/logout/replay-refused), and authorization matrix (owner/admin/stranger × read/write). Assert verdicts and state transitions, never live credentials or timings. Adversarial cases first: enumeration probes, replayed sessions, expired peppers, tampered tags — each with exact expected verdicts. Auth code untested against its adversary is decoration with a login form; these guards make the adversary's test suite yours. Cover owner, stranger, admin and unknown roles at minimum in every auth matrix. Include deleted-user and renamed-resource cases too, since identity lifecycle edges break assumptions. Test deprovisioning paths as rigorously as provisioning ones, since ex-employees with live access are breaches waiting. Run leaver audits on the same schedule as access reviews so departures revoke promptly. Test the full joiner-mover-leaver cycle annually with synthetic identities so every transition works before real ones depend on it. Document every transition outcome so audits trace identities across their full lifecycle without gaps.",
             code=(
                 'users = {"ada": "user", "root": "admin"}\n'
                 'docs = {"doc1": "ada"}\n'
                 '\n'
                 'def authorize(user: str, resource: str) -> bool:\n'
                 '    if users.get(user) == "admin":\n'
                 '        return True\n'
                 '    return docs.get(resource) == user\n'
                 '\n'
                 'assert authorize("ada", "doc1")\n'
                 'assert not authorize("bor", "doc1")\n'
                 'assert authorize("root", "doc1")\n'
                 'assert not authorize("nobody", "doc1")\n'
                 'print("auth matrix holds: owner yes, stranger no, admin yes, unknown no")'
             ),
             variant_b='a deleted user (which branch denies, and how fast?)',
             variant_c='resource renamed mid-test (does the matrix follow names or ids?)',
             mistakes=[
                 "Happy-path-only auth tests (adversaries never take happy paths).",
                 "Live credentials in test fixtures (leaked fixtures become breach lists).",
                 "Timing-sensitive asserts on throttling (flaky tests teach ignoring tests).",
             ],
             qa=(
                 ["Why test unknown users explicitly instead of assuming denial?",
                  "Why avoid live credentials in test fixtures?",
                  "Why must throttling tests avoid real timing?"],
                 ["Assumed denial rots: explicit unknown-user cases pin the fail-closed branch against future refactors that might open it.",
                  "Leaked fixtures become breach lists; synthetic identities test identical logic with zero blast radius.",
                  "Wall-clock asserts flake across machines; state-based asserts (locked/unlocked) test throttling deterministically."],
             ),
             homework="Write auth-matrix asserts covering owner/stranger/admin/unknown on one resource. Run them, print confirmation, and comment which assert pins fail-closed.",
             patterns=["assert ", "def "],
             mapping="Auth test matrices cover every role×action×resource triple that matters; adversaries' cases lead, happy paths follow.",
         ),
         164: dict(
             topic="Phase review: passwords and secrets",
             idea="Rebuild from memory: human entropy limits, honest PBKDF2 with stated counts, dictionary economics, versioned pepper rotation, manager interfaces with audit, login throttling with uniform messages, MFA hierarchy (TOTP honest, WebAuthn phishing-proof), diceware shapes, token-bucket fairness, session lifecycles, ownership authorization, rotation runbooks. Close the notes and reproduce the PBKDF2 store/check pair plus the throttling state machine — slow hashes, calm verdicts, exponential costs. The missing line is tomorrow's first job; integration (phase 7) spends every control on realistic builds. If the rebuild flows, credential thinking is installed. Name the phase's three load-bearing habits from memory before advancing further. Recite the habits aloud with a colleague listening; teaching cements faster than silent recall. Pair the recitation with the phase's project checklist so every habit maps to a concrete artefact. File the artefact list with the phase report so reviewers verify habits against evidence instead of claims. Reviewers should reject habit claims lacking artefacts, keeping the standard honest for everyone. Start the capstone only when every artefact exists.",
             code=(
                 'import hashlib\n'
                 'import hmac\n'
                 'import secrets\n'
                 '\n'
                 'salt = secrets.token_bytes(16)\n'
                 'stored = hashlib.pbkdf2_hmac("sha256", b"recall-pw", salt, 1000)\n'
                 'cand = hashlib.pbkdf2_hmac("sha256", b"recall-pw", salt, 1000)\n'
                 'print("recall pair verifies:", hmac.compare_digest(cand, stored))\n'
                 'print("lengths only logged; iteration count stated: 1000 demo")\n'
                 'print("recall throttle rule: exponential backoff, uniform messages")'
             ),
             variant_b='wrong password (which verdict, and how calm?)',
             variant_c='production count 600k (what changes besides waiting?)',
             mistakes=[
                 "Rebuilding with notes open — retrieval is the learning.",
                 "Reciting PBKDF2 without placing salt handling in a running script.",
                 "Skipping throttling in the rebuild because hashing felt sufficient.",
             ],
             qa=(
                 ["What single rebuild proves this phase stuck?",
                  "Why rebuild the throttling machine alongside the hashes?",
                  "What does a failed rebuild locate?"],
                 ["PBKDF2 store/check pair plus throttling state machine from memory — slow hashes, calm verdicts, exponential costs, all running.",
                  "Hashing without throttling leaves online guessing free; the pair prices both attacker classes, which is the phase's whole point.",
                  "The exact missing line is tomorrow's first job — failed retrieval marks the gap precisely, unlike re-reading which marks nothing."],
             ),
             homework="Write `phase_recap()` from memory: PBKDF2 pair with verdicts plus one throttling rule stated. Run it, print the pair, and comment which line you had to look up.",
             patterns=["pbkdf2_hmac(", "compare_digest("],
             mapping="Phase 7 spends it all on builds; credential discipline never changes again.",
         ),
     }),
    ("Integration and Capstone",
     "Spend everything: secure messenger toy, vault review, audit drills, tabletop exercise, and final reflection.",
     {
         165: dict(
             topic="Secure messenger toy, scoped",
             idea="Today's build combines the track into one toy: XOR bulk cipher under a per-conversation key, HMAC tags verified before reading, sequence numbers rejecting replays, all labelled TEACHING at every layer. The demo runs Alice-to-Bob messaging with a tamper drill (flipped bit refused) and a replay drill (old sequence refused), printing each verdict. Scope stated in code comments and output: teaching construction demonstrating composition discipline, not a messaging app — real systems use Signal protocol / MLS via audited libraries. Composition done right is the whole track in one script; composition done wrong is how real messengers fail.",
             code=(
                 '# TEACHING messenger: composition demo only, never deployable\n'
                 'import hashlib\n'
                 'import hmac\n'
                 '\n'
                 'CKEY = bytes([0x2B])\n'
                 'MKEY = b"demo-msg-mac"\n'
                 '\n'
                 'def send_msg(text: str, seq: int):\n'
                 '    body = seq.to_bytes(4, "big") + text.encode()\n'
                 '    cipher = bytes(b ^ CKEY[i % len(CKEY)] for i, b in enumerate(body))\n'
                 '    return cipher, hmac.new(MKEY, cipher, hashlib.sha256).hexdigest(), seq\n'
                 '\n'
                 'def recv_msg(cipher: bytes, tag: str, seq: int, last_seen: int):\n'
                 '    if not hmac.compare_digest(hmac.new(MKEY, cipher, hashlib.sha256).hexdigest(), tag):\n'
                 '        return None, last_seen, "refused: bad tag"\n'
                 '    if seq <= last_seen:\n'
                 '        return None, last_seen, "refused: replay"\n'
                 '    body = bytes(b ^ CKEY[i % len(CKEY)] for i, b in enumerate(cipher))\n'
                 '    return body[4:].decode(), seq, "accepted"\n'
                 '\n'
                 'c, t, s = send_msg("meet at noon", 1)\n'
                 'print(recv_msg(c, t, s, 0))\n'
                 'print(recv_msg(c, t, s, 1))\n'
                 'print(recv_msg(bytes([c[0] ^ 1]) + c[1:], t, 2, 1))\n'
                 'print("tag-then-sequence: tampering and replays both refused")'
             ),
             variant_b='out-of-order seq 5 then 3 (which verdict, and is skipping allowed?)',
             variant_c='same seq, fresh tag recomputed (why does the tag bind the sequence?)',
             mistakes=[
                 "No sequence numbers (replays accepted as fresh).",
                 "Tags over content without sequence (reordered messages verify fine).",
                 "Demo messenger mistaken for a starting point for real apps (rewrite on audited protocols).",
             ],
             qa=(
                 ["Why must the tag cover the sequence number, not just content?",
                  "Why verify tag before checking sequence?",
                  "What makes this demo undeployable despite correct structure?"],
                 ["Otherwise attackers replay old valid messages whose tags still verify — binding order into the tag makes replays fail verification.",
                  "Sequence checks on unverified bytes let attackers probe ordering logic; tag-first keeps hostile bytes from reaching any logic.",
                  "Toy cipher, demo keys, no forward secrecy, no identity binding — structure right, every primitive wrong for production."],
             ),
             homework="Write send_msg/recv_msg with tag-then-sequence discipline and TEACHING banners. Run valid/replay/tamper cases, print all three verdicts, and comment which check runs first.",
             patterns=["compare_digest(", "def "],
             mapping="Signal/MLS embody tag-everything-including-order at production strength; this toy teaches the discipline they automate.",
         ),
         166: dict(
             topic="Vault review: passwords end to end",
             idea="Revisit the phase-6 vault with reviewer's eyes: PBKDF2 counts against current OWASP guidance, salts unique per entry, pepper versioned with rotation window tested, throttling exponential with uniform messages, audit log append-only, recovery codes single-use and hashed. The demo re-runs the vault gate plus a rotation drill and prints a review scorecard (each control pass/fail), proving review is executable, not vibes. Reviews that run code beat reviews that read code: every claim below gets a printed verdict beside it. Sign the scorecard only when all rows pass; anything else is findings, not sign-off. Re-run scorecards after every dependency upgrade, since new versions can silently change behaviour. Pin dependency versions in scorecard environments so reruns stay comparable across upgrades.",
             code=(
                 'import hashlib\n'
                 'import hmac\n'
                 '\n'
                 'def gate(password: str, salt: bytes, expect: bytes, iters: int = 1000) -> bool:\n'
                 '    cand = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, iters)\n'
                 '    return hmac.compare_digest(cand, expect)\n'
                 '\n'
                 'salt = b"\\x03" * 16\n'
                 'stored = hashlib.pbkdf2_hmac("sha256", b"vault-master", salt, 1000)\n'
                 'checks = {\n'
                 '    "right accepts": gate("vault-master", salt, stored),\n'
                 '    "wrong rejects": not gate("nope", salt, stored),\n'
                 '    "unique salts": hashlib.pbkdf2_hmac("sha256", b"vault-master", b"\\x04" * 16, 1000) != stored,\n'
                 '}\n'
                 'for label, ok in checks.items():\n'
                 '    print(f"[{chr(120) if ok else chr(32)}] {label}")\n'
                 'assert all(checks.values())\n'
                 'print("scorecard green: gate, rejects, uniqueness proven")'
             ),
             variant_b='iteration count doubled (which check changes, and should any?)',
             variant_c='pepper added to the gate (which new check appears?)',
             mistakes=[
                 "Reviewing code by reading instead of executing (vibes, not verdicts).",
                 "Sign-off with known-failing rows ('minor, fix later' on access controls).",
                 "Review scope excluding rotation and recovery (the paths attackers prefer).",
             ],
             qa=(
                 ["Why must reviews execute rather than read?",
                  "Why test uniqueness, not just correctness?",
                  "What makes a scorecard signable?"],
                 ["Reading misses runtime behaviour (timing, state, edge cases); executed checks prove properties hold in reality, not just in prose.",
                  "Correctness proves the gate works; uniqueness proves salts work — a gate passing shared salts is decoratively correct.",
                  "All rows green with no exceptions: anything amber is findings with owners and dates, never footnotes on a signature."],
             ),
             homework="Write a vault scorecard (right-accept, wrong-reject, unique-salts) printing ticked rows. Run it, print the verdict, and comment which check proves salt discipline.",
             patterns=["pbkdf2_hmac(", "compare_digest("],
             mapping="Password-vault audits and auth-service reviews run executable scorecards; sign-off means green rows only.",
         ),
         167: dict(
             topic="Audit drill: find five planted flaws",
             idea="Today's drill plants five classic flaws in one auth script — MD5 password hash, unsalted storage, == token comparison, verbose user-enumeration errors, missing throttling — and your job is the finding report: flaw, line, severity, fix. The demo script under review is printed for study (it runs, to show flaws execute fine — broken code runs perfectly), then the answer key names all five with severities. Drills like this train the reviewer's eye faster than any lecture: pattern-match the flaw shapes here and production code starts confessing on sight. Five found is passing; four means re-read days 92, 94, 11, 8 and 155. Time-box drills to keep pressure realistic; untimed hunts teach thoroughness but not triage speed. Score findings per hour alongside completeness since real incidents budget both. Publish drill scores internally so teams compete on findings, not on attendance.",
             code=(
                 '# DRILL TARGET (intentionally flawed — find all five)\n'
                 'import hashlib\n'
                 '\n'
                 'users = {}\n'
                 '\n'
                 'def register(name: str, pw: str):\n'
                 '    users[name] = hashlib.md5(pw.encode()).hexdigest()\n'
                 '\n'
                 'def login(name: str, pw: str):\n'
                 '    if name not in users:\n'
                 '        return "no such user"\n'
                 '    if users[name] == hashlib.md5(pw.encode()).hexdigest():\n'
                 '        return "welcome"\n'
                 '    return "wrong password"\n'
                 '\n'
                 'register("ada", "sunshine")\n'
                 'print(login("ada", "sunshine"))\n'
                 'print(login("ada", "nope"))\n'
                 'print("runs fine. find the five flaws: md5, unsalted, ==, enumeration, no throttle")'
             ),
             variant_b='fix all five (what does the corrected script look like?)',
             variant_c='add a sixth flaw silently (can a partner find it?)',
             mistakes=[
                 "Finding three and stopping (drills demand exhaustive lists).",
                 "Severity inflation (everything 'critical' means nothing is).",
                 "Fixes proposed without verifying (patches need the same tests as features).",
             ],
             qa=(
                 ["Name the five planted flaws with severities.",
                  "Why does broken code running fine matter?",
                  "How do drills transfer to production review?"],
                 ["MD5 storage (critical), unsalted (high), == comparison (medium, timing), enumeration messages (medium), no throttling (high) — each with fix direction.",
                  "It proves testing-by-running cannot catch design flaws; only review against known-bad patterns finds what execution never shows.",
                  "Flaw shapes repeat across codebases, so drilled eyes recognise MD5/==/enumeration reflexively instead of reasoning each from scratch."],
             ),
             homework="Write a finding report (flaw, line, severity, fix) for the five planted flaws. Run the target, confirm it executes, and comment which flaw enables the fastest real compromise.",
             patterns=["hashlib.md5(", "def "],
             mapping="Security code-review checklists encode these five shapes; drills keep reviewers faster than codebases rot.",
         ),
         168: dict(
             topic="Secrets rotation fire drill",
             idea="Run a full rotation under time pressure: new pepper version issued, dual-accept window opened, canary accounts migrated first, old version retired after verification, audit log reviewed for stragglers. The demo walks the version states (v1 only → v1+v2 → v2 only) with acceptance printed per state, proving service continuity throughout. Rotation drills belong in game days because real rotations happen during incidents — suspected leaks, departing admins — when untested procedures fail exactly as Murphy predicts. Rehearsed rotation is boring; unrehearsed rotation is an outage wearing a security costume. Rotate drill scenarios as well, since rehearsed scripts breed their own blind spots over time. Vary drill scenarios quarterly so rehearsal never becomes the only practiced shape. Rotate facilitators too, since the same leader runs the same drill unconsciously. Vary scenarios and facilitators together so rehearsal never becomes ritual. Document drill variants in a shared library so facilitators rotate without losing quality. Version the library so improvements propagate to every future drill.",
             code=(
                 'versions = {"active": ["v1"], "retired": []}\n'
                 '\n'
                 'def rotate(new: str):\n'
                 '    versions["active"].append(new)\n'
                 '    return sorted(versions["active"])\n'
                 '\n'
                 'def retire(old: str):\n'
                 '    versions["active"].remove(old)\n'
                 '    versions["retired"].append(old)\n'
                 '    return sorted(versions["active"])\n'
                 '\n'
                 'print("start:      ", versions["active"])\n'
                 'print("dual window:", rotate("v2"))\n'
                 'print("retired v1: ", retire("v1"))\n'
                 'print("continuity throughout: no flag day, no lockout")'
             ),
             variant_b='a straggler still on v1 at retire time (refuse or grace?)',
             variant_c='emergency rotation in 1 hour (which steps compress, which never do?)',
             mistakes=[
                 "Drills announced so widely they test nothing (surprise within bounds).",
                 "Retire step skipped 'temporarily', fossilising dual-accept forever.",
                 "Canary accounts skipped to save time (production becomes the canary).",
             ],
             qa=(
                 ["Why rotate on game days instead of waiting for incidents?",
                  "What makes dual-accept windows safe rather than sloppy?",
                  "Why retire explicitly instead of letting old versions fade?"],
                 ["Incidents demand untested procedures at the worst moment; rehearsed rotation works under pressure because it worked without pressure first.",
                  "Bounded time plus verification: the window is scheduled, monitored and closed — sloppiness is unbounded dual-accept with no retirement date.",
                  "Faded-but-valid old versions remain exploitable indefinitely; explicit retirement with canary proof closes the window verifiably."],
             ),
             homework="Write rotate/retire functions over a version state with printed states. Run a full v1→v2 cycle, print all three states, and comment which step bounds the window.",
             patterns=["def ", "return"],
             mapping="Secret-manager rotation schedules plus game-day drills; boring rotation is the goal, not the insult.",
         ),
         169: dict(
             topic="Incident tabletop: stolen pepper",
             idea="Tabletop exercise: the pepper store may be compromised — walk the response without touching production. Steps in order: scope (which versions, which window), contain (rotate to new version, dual-accept), verify (canary logins on new version, old-version attempts now refused), communicate (who knew, who must know, what users do: nothing, by design), learn (how did it leak, what changes). The demo walks a scripted timeline printing each decision point with its rationale, distinguishing decisions (rotate now) from investigations (how it leaked, parallel track). Tabletops rehearse judgment under time pressure; the artefact is a runbook updated with everything this one taught. File the updated runbook where on-call engineers find it in seconds flat. Test findability with timed drills under simulated pressure annually. Record findability times to prove improvement instead of assuming practice works. Trend findability times quarterly so progress shows in numbers, not feelings.",
             code=(
                 'timeline = [\n'
                 '    (0, "alert: pepper store anomaly detected"),\n'
                 '    (1, "decision: rotate to v3 now, investigate in parallel"),\n'
                 '    (2, "dual-accept v2+v3, canary logins green"),\n'
                 '    (3, "retire v2, verify old attempts refused"),\n'
                 '    (4, "runbook updated with lessons"),\n'
                 ']\n'
                 'for hour, event in timeline:\n'
                 '    print(f"T+{hour}h: {event}")\n'
                 'print("decisions first, investigations parallel, runbook updated")'
             ),
             variant_b='a weekend detection (who decides, and by what authority?)',
             variant_c='leak confirmed vs suspected (how does the response differ?)',
             mistakes=[
                 "Investigating before containing (evidence gathering while damage continues).",
                 "Silent rotation without user comms where trust demands transparency.",
                 "No parallel track, so decisions wait on forensics that take weeks.",
             ],
             qa=(
                 ["Why rotate before finishing the investigation?",
                  "Why do decisions and investigations run on parallel tracks?",
                  "What must the updated runbook contain?"],
                 ["Containment bounds damage now; forensics takes weeks, and waiting trades certain continued exposure for complete understanding.",
                  "Different tempos: decisions need minutes, investigations need weeks — serialising them stalls response on analysis.",
                  "The timeline, what worked, what failed, and the changed procedure — tabletops that update nothing were theatre."],
             ),
             homework="Write a five-step incident timeline with decisions vs investigations labelled. Run it, print the timeline, and comment which step contains damage first.",
             patterns=["for ", "print("],
             mapping="Incident-response playbooks separate decisions from investigations; tabletops rehearse the split under time pressure.",
         ),
         170: dict(
             topic="Log tampering drill",
             idea="Detect log tampering with the day-14 hash chain under adversarial pressure: an attacker edits a middle entry and recomputes all later links (they hold no separate anchor, so the forgery is internally consistent), and your job is the detection strategy that still catches it — anchor heads published externally (write-once store, printed weekly digests, transparency-style log), plus anomaly review (impossible timestamps, sequence gaps, volume spikes). The demo shows consistent-forgery passing local verification, then anchor comparison exposing it. Chains detect tampering only relative to trusted anchors; the anchor strategy IS the security, and everything else is bookkeeping. Audit anchor storage separately from log storage so the two never share fate in one compromise. Map storage to separate failure domains explicitly and review the mapping yearly. Diagram failure domains visually so shared fate stands out before incidents reveal it.",
             code=(
                 'import hashlib\n'
                 '\n'
                 'def link(head: str, text: str) -> str:\n'
                 '    return hashlib.sha256((head + "|" + text).encode()).hexdigest()\n'
                 '\n'
                 'log = []\n'
                 'head = "GENESIS"\n'
                 'for text in ["boot ok", "ada login", "file read"]:\n'
                 '    head = link(head, text)\n'
                 '    log.append((text, head))\n'
                 'published = head\n'
                 'forged = [("boot ok", log[0][1])]\n'
                 'h1 = link(log[0][1], "root login")\n'
                 'forged.append(("root login", h1))\n'
                 'forged.append(("file read", link(h1, "file read")))\n'
                 'recomputed = "GENESIS"\n'
                 'for text, _ in forged:\n'
                 '    recomputed = link(recomputed, text)\n'
                 'print("local chain self-consistent:", recomputed == forged[-1][1])\n'
                 'print("published anchor matches:   ", recomputed == published)\n'
                 'print("consistent forgery caught only by external anchor")'
             ),
             variant_b='anchor published per entry instead of head-only (what changes?)',
             variant_c='timestamps inside entries (which anomaly review catches backdating?)',
             mistakes=[
                 "Anchors stored beside logs (consistent rewrite defeats both).",
                 "Verification skipped because 'hashes match' (which hashes, against what?).",
                 "Anomaly review absent (consistent forgeries need behavioural detection).",
             ],
             qa=(
                 ["Why does consistent forgery pass local verification?",
                  "What makes the published anchor decisive?",
                  "What role does anomaly review play alongside chains?"],
                 ["Recomputed links match because the forger rebuilt them consistently; local checks verify arithmetic, and the arithmetic is correct.",
                  "It predates the forgery from an independent channel — the recomputed head diverges from published truth, exposing the rewrite.",
                  "Catching what chains cannot: impossible timestamps and volume spikes reveal tampering whose arithmetic is flawless."],
             ),
             homework="Write chain/verify plus anchor-compare detecting a consistently forged middle entry. Run it, print both verdicts, and comment which comparison actually catches the forgery.",
             patterns=["def ", "return"],
             mapping="Certificate-transparency logs and anchored backups apply external-anchor thinking at scale.",
         ),
         171: dict(
             topic="Threat modelling a login form",
             idea="Threat-model the humble login form with STRIDE per element: spoofing (fake login page — mitigated by TLS + verified host), tampering (credential interception — TLS + HMAC), repudiation (user denies attempts — audit logs), information disclosure (enumeration messages, timing), denial of service (lockout abuse, expensive hashes), elevation (SQL injection to admin). The demo encodes the model as data (element → threats → mitigations → day references) and prints uncovered threats (mitigation: none) as findings. Threat modelling is enumeration with honesty: every element gets every STRIDE letter considered, 'not applicable' stated with reasons, never assumed. Models rot; re-model on every design change. Version models beside designs so reviewers always see which model matches reality. Stamp model versions with dates so staleness shows without opening documents.",
             code=(
                 'elements = {\n'
                 '    "login page": {"spoofing": "TLS + verified host", "tampering": "HMAC forms"},\n'
                 '    "password check": {"disclosure": "uniform messages", "denial": "throttling"},\n'
                 '    "session cookie": {"disclosure": "HttpOnly+Secure", "tampering": "signed"},\n'
                 '}\n'
                 'STRIDE = ["spoofing", "tampering", "repudiation", "disclosure", "denial", "elevation"]\n'
                 '\n'
                 'def audit_model(elements):\n'
                 '    gaps = []\n'
                 '    for element, covered in elements.items():\n'
                 '        for threat in STRIDE:\n'
                 '            if threat not in covered:\n'
                 '                gaps.append(f"{element}: {threat} unaddressed")\n'
                 '    return gaps\n'
                 '\n'
                 'gaps = audit_model(elements)\n'
                 'print("unaddressed threats:", len(gaps))\n'
                 'for gap in gaps[:5]:\n'
                 '    print(" -", gap)\n'
                 'print("every element x every letter: enumeration with honesty")'
             ),
             variant_b='an elevation entry added to password check (which gap closes?)',
             variant_c='a fourth element "audit log" (which threats dominate it?)',
             mistakes=[
                 "Modelling once at launch, never again (designs drift, models fossilise).",
                 "'Not applicable' without reasons (assumptions hiding as conclusions).",
                 "Threats without mitigations filed as accepted risk by default.",
             ],
             qa=(
                 ["Why enumerate every STRIDE letter per element instead of brainstorming?",
                  "What makes 'not applicable' dangerous without reasons?",
                  "When must the model be redone?"],
                 ["Brainstorming finds familiar threats; enumeration forces confrontation with unfamiliar ones (repudiation on a login form surprises most teams).",
                  "Unexplained N/A hides assumptions attackers test for free; stated reasons are reviewable claims that expire loudly when designs change.",
                  "On every design change touching trust boundaries, data flows or authentication — models describe designs, and designs move."],
             ),
             homework="Write `audit_model(elements)` listing unaddressed STRIDE threats per element. Run it on a login-form model, print the gaps, and comment which gap surprises most.",
             patterns=["def ", "return"],
             mapping="Microsoft/SDL and OWASP threat-model practices enumerate per element; re-model on every design change.",
         ),
         172: dict(
             topic="Risk matrix that means something",
             idea="Risk matrices multiply likelihood by impact, but most are decorative: uncalibrated axes ('high' means everything), no time horizon, no owner, no review date. An honest matrix defines each axis operationally (likelihood: incidents per year from threat intel; impact: dollars, downtime hours, records), scores named scenarios (not vibes), sorts by expected loss, and assigns owners plus review dates to the top rows. The demo scores four scenarios with explicit numbers and prints the ranked register with owners. Matrices do not decide; they organise decisions — the value is the forced conversation about likelihood evidence and impact arithmetic, not the coloured grid.",
             code=(
                 'scenarios = [\n'
                 '    ("phishing credential theft", 0.6, 50000, "security team"),\n'
                 '    ("unpatched edge device", 0.3, 200000, "infra team"),\n'
                 '    ("insider data theft", 0.1, 500000, "security team"),\n'
                 '    ("forgotten test key", 0.2, 20000, "dev team"),\n'
                 ']\n'
                 '\n'
                 'def rank(scenarios):\n'
                 '    ranked = sorted(scenarios, key=lambda s: s[1] * s[2], reverse=True)\n'
                 '    for label, likelihood, impact, owner in ranked:\n'
                 '        print(f"${likelihood * impact:>9,.0f} expected | {label} (owner: {owner})")\n'
                 '    return ranked\n'
                 '\n'
                 'rank(scenarios)\n'
                 'print("expected loss orders the work; owners own the rows")'
             ),
             variant_b='likelihoods doubled (does the order change, or just the scale?)',
             variant_c='a fifth scenario with unknown likelihood (how to score honest ignorance?)',
             mistakes=[
                 "Uncalibrated axes where every risk lands 'high' (matrices that cannot discriminate decide nothing).",
                 "No owners or dates (registers nobody reads after the workshop).",
                 "Expected loss quoted as prediction instead of ordering device.",
             ],
             qa=(
                 ["Why multiply likelihood by impact instead of ranking by either alone?",
                  "What makes most risk matrices decorative?",
                  "Why do rows need owners and dates?"],
                 ["Either alone misorders: frequent trivia outranks rare catastrophes by likelihood, and vice versa — expected loss balances both into one ordering.",
                  "Uncalibrated axes, missing time horizons and absent evidence: decoration that cannot discriminate is process theatre.",
                  "Unowned risks rot; undated matrices fossilise — owners act and dates force re-evaluation as threats and systems move."],
             ),
             homework="Write `rank(scenarios)` printing expected-loss ordering with owners. Run it on four scenarios, print the register, and comment which row to fund first.",
             patterns=["def ", "return"],
             mapping="Risk registers with calibrated axes, owners and review dates drive security roadmaps; colours never decide alone.",
         ),
         173: dict(
             topic="Disclosure done right",
             idea="Finding vulnerabilities obligates responsibly: document reproduction privately, notify the owner through published security contacts (security.txt), allow remediation time proportionate to severity (industry norms 90 days, faster for active exploitation), coordinate disclosure wording, and publish only after fixes ship or deadlines pass with documented good faith. The demo walks a disclosure timeline with decision points (vendor responsive/unresponsive, exploitation active/dormant) printing the recommended path per branch. Never threaten, never extort, never drop zero-days publicly for reputation; the track teaches finding flaws to fix systems, and disclosure ethics are load-bearing walls of that purpose, not decoration. Teach disclosure cases from history so ethics land as identity rather than checkbox compliance. Invite legal counsel to one tabletop yearly where ethics meet law. Document the counsel relationship before incidents so privilege protects the conversation when needed. Establish counsel relationships before incidents so protection exists when required. Test the relationship with tabletop exercises before real incidents test it instead.",
             code=(
                 'cases = [\n'
                 '    ("responsive vendor, dormant bug", "coordinate 90-day disclosure"),\n'
                 '    ("silent vendor, dormant bug", "escalate via CERT, then publish with mitigations"),\n'
                 '    ("any vendor, active exploitation", "publish mitigations immediately, coordinate patch"),\n'
                 ']\n'
                 'for situation, path in cases:\n'
                 '    print(f"{situation}: -> {path}")\n'
                 'print("document privately, notify properly, publish responsibly")'
             ),
             variant_b='a vendor threatening legal action (which allies and options?)',
             variant_c='a bug in abandoned software (who is the ' + '"owner"' + ' then?)',
             mistakes=[
                 "Public zero-day drops for reputation (users pay for the researcher's fame).",
                 "Private sales to brokers instead of vendor notification (capability proliferation).",
                 "No documentation trail (good faith unprovable when disputes arise).",
             ],
             qa=(
                 ["Why coordinate instead of publishing immediately?",
                  "What changes when exploitation is active?",
                  "Why document every step privately first?"],
                 ["Coordination gives users patches before attackers get instructions; immediate publication arms exploiters during the window defenders need most.",
                  "Active exploitation collapses timelines: mitigations publish immediately while patching races, because victims are already bleeding.",
                  "Good faith must be provable: timestamps of private notice, reasonable deadlines and vendor responses decide how history judges the disclosure."],
             ),
             homework="Write a disclosure decision table mapping vendor/exploitation states to paths. Run it on three cases, print all paths, and comment which case publishes fastest.",
             patterns=["for ", "print("],
             mapping="Google P0 90-day policy, CERT coordination and security.txt contacts implement responsible disclosure at scale.",
         ),
         174: dict(
             topic="Security review of your own code",
             idea="Review personal projects with the track's checklist: secrets in code (grep for keys, tokens, passwords), crypto choices (algorithms, modes, iteration counts, nonce handling), auth paths (enumeration, throttling, session flags), input handling (validation, parsing, errors), dependencies (known CVEs, lockfiles, update story), and logging (no secrets, refusal visibility). The demo runs a checklist function over a synthetic project dict, printing pass/fail per control with finding text — the shape of real secure-code-review gates. Self-review before peer review: the checklist catches the known-bad mechanically, leaving human reviewers the novel flaws only people find. Rotate reviewers across components to avoid familiarity blindness where ownership stops seeing flaws. Bring external reviewers annually since fresh eyes catch what familiarity filters out. Schedule external reviews before major releases when stakes justify the cost.",
             code=(
                 'project = {"secrets_in_code": True, "pbkdf2_iters": 1000, "throttling": False, "hsts": True, "deps_pinned": False}\n'
                 '\n'
                 'def review(project: dict):\n'
                 '    findings = []\n'
                 '    if project.get("secrets_in_code"):\n'
                 '        findings.append("CRITICAL: secrets in code")\n'
                 '    if project.get("pbkdf2_iters", 0) < 600000:\n'
                 '        findings.append("HIGH: weak password hashing")\n'
                 '    if not project.get("throttling"):\n'
                 '        findings.append("HIGH: no login throttling")\n'
                 '    if not project.get("deps_pinned"):\n'
                 '        findings.append("MEDIUM: unpinned dependencies")\n'
                 '    return findings\n'
                 '\n'
                 'print(review(project))\n'
                 'print("checklist over hope: mechanical findings first, humans for novelty")'
             ),
             variant_b='a clean project (does silence mean secure, or just unchecked?)',
             variant_c='a legacy project with ten findings (how to prioritise remediation?)',
             mistakes=[
                 "Reviewing own code as the author instead of as the attacker (role-play the adversary).",
                 "Checklist filed without fixing (findings without owners rot).",
                 "Scope limited to new code (legacy holds most flaws by volume).",
             ],
             qa=(
                 ["Why run checklists before human review?",
                  "Why do severity labels matter on findings?",
                  "What does a clean checklist prove?"],
                 ["Mechanical checks catch known-bad patterns cheaply, reserving expensive human attention for novel flaws only people find.",
                  "They order remediation: criticals today, mediums scheduled — unlabelled lists get worked in random order or not at all.",
                  "That known-bad patterns are absent, nothing more; novel flaws need human review, which the checklist deliberately does not replace."],
             ),
             homework="Write `review(project)` checking five controls with severity-labelled findings. Run it on flawed and clean projects, print both verdicts, and comment which finding is critical.",
             patterns=["def ", "return"],
             mapping="Secure code-review gates (Semgrep rules, checklists, severity SLAs) mechanise this discipline in CI.",
         ),
         175: dict(
             topic="Staying current without drowning",
             idea="Security knowledge rots fast: new CVEs daily, algorithms aging, guidance updating. A sustainable practice beats heroic cramming: curated feeds (vendor advisories for your stack, CISA alerts, one quality newsletter), scheduled reading time (weekly, calendared, non-negotiable), lab notes (every incident and upgrade written down), and teaching (explain one concept monthly — teaching exposes gaps reading hides). The demo prints a weekly learning schedule with sources and timeboxes, proving sustainability is designed, not wished. Burnout ends more security careers than attackers do; pace is a security control for the most critical asset — you. Protect sleep and boundaries as scheduled controls, since exhausted analysts miss what rested analysts catch. Track on-call load as a security metric because fatigue degrades judgment. Cap consecutive on-call nights explicitly since tired analysts approve what rested ones would challenge. Enforce handoff rules at shift boundaries so fatigue never owns critical decisions. Require rested sign-off for high-impact actions regardless of incident tempo. Staff critical decisions with redundancy so no single tired analyst decides alone.",
             code=(
                 'plan = [("Monday", "vendor advisories", 20), ("Wednesday", "one paper or RFC section", 30), ("Friday", "lab notes review", 20)]\n'
                 'total = 0\n'
                 'for day, task, minutes in plan:\n'
                 '    total += minutes\n'
                 '    print(f"{day:<10} {task:<28} {minutes} min")\n'
                 'print("weekly total:", total, "minutes (sustainable beats heroic)")'
             ),
             variant_b='an incident week (what gets cut, and what never does?)',
             variant_c='a quiet month (where does surplus learning time go?)',
             mistakes=[
                 "Feed firehoses with no curation (drowning feels like diligence).",
                 "Unscheduled learning that never happens (calendars, not intentions).",
                 "Notes never written (experience without records evaporates).",
             ],
             qa=(
                 ["Why schedule learning instead of fitting it around work?",
                  "Why teach monthly as part of learning?",
                  "What gets cut in incident weeks?"],
                 ["Unscheduled important work loses to urgent work every time; calendared time with owners survives pressure that intentions do not.",
                  "Explaining exposes gaps reading hides — questions you cannot answer mark exactly what to study next.",
                  "Breadth reading pauses; advisories for your stack and lab notes never do — protect the minimum that keeps systems safe."],
             ),
             homework="Write a weekly learning plan with sources and timeboxes totalling under 90 minutes. Run it, print the schedule, and comment which item survives incident weeks.",
             patterns=["for ", "print("],
             mapping="Sustainable practice (feeds, calendars, notes, teaching) outlasts heroic cramming across entire careers.",
         ),
         176: dict(
             topic="Career map: what comes after",
             idea="Cryptography opens doors across security: application security (code review, threat modelling), security engineering (pipelines, detection, infrastructure), GRC (risk, compliance, policy), incident response (forensics, hunting), and cryptographic engineering (protocols, libraries — mathematics required). Each values different slices of this track: appsec wants days 4–14 plus web thinking, detection wants log and parsing days, GRC wants risk and disclosure days, crypto engineering wants the math behind every demo. Map your next 90 days concretely: one adjacent track, one certification or portfolio project, one community (conferences, CTFs, local meetups). Learning compounds where direction exists; drift is the only guaranteed failure mode. Review direction quarterly against market signals so plans steer with evidence instead of inertia. Sunset directions that evidence no longer supports rather than letting them linger. Archive retired directions with reasons so future teams understand what was tried and dropped. Sunset dead plans publicly so nobody resurrects them unknowingly later.",
             code=(
                 'roles = {"appsec": ["input validation", "auth", "threat models"], "detection": ["log parsing", "baselines", "alerts"], "grc": ["risk registers", "disclosure", "policy"]}\n'
                 'done = {"input validation", "auth", "log parsing", "risk registers"}\n'
                 'for role, skills in roles.items():\n'
                 '    have = sum(1 for s in skills if s in done)\n'
                 '    print(f"{role:<10} {have}/{len(skills)} track skills transfer")\n'
                 'print("direction first: adjacent track, portfolio proof, community")'
             ),
             variant_b='cryptographic engineering added (which math prerequisites?)',
             variant_c='management track (which track skills transfer upward?)',
             mistakes=[
                 "Certification collecting without portfolio proof (paper without practice).",
                 "Directionless 'learning security' (drift as a study plan).",
                 "Skipping community (careers run on people as much as skills).",
             ],
             qa=(
                 ["How do different roles use different slices of this track?",
                  "Why pair every direction with portfolio proof?",
                  "What role does community play?"],
                 ["Appsec leans auth/input, detection leans logs/parsing, GRC leans risk/disclosure — one track, several professions, chosen slices.",
                  "Claims need evidence: hiring runs on demonstrated work (boards, write-ups, tools), and certificates without artefacts convince nobody technical.",
                  "Jobs, mentorship and calibration flow through people; isolated learners miss the market signals communities broadcast freely."],
             ),
             homework="Write a 90-day plan (adjacent track, portfolio project, community) mapped to track skills. Run the coverage check, print transfer counts, and comment which gap to close first.",
             patterns=["for ", "print("],
             mapping="Security career ladders reward demonstrated work plus direction; this track is the foundation, not the ceiling.",
         ),
         177: dict(
             topic="Final review and checklist",
             idea="Run the track checklist end to end: bytes discipline, armour fluency, XOR laws, OTP costs, reuse attacks, randomness discipline, checksums versus hashes, timing oracles, dump reading, armour layers, record parsing, entropy honesty, sniffer verdicts, contract asserts, phase rebuilds, SHA-256 properties, HMAC discipline, extension attacks, salts, dead algorithms, birthdays, chains, truncation prices, peppers, addressing, agility, classical analysis, ECB tells, cribs, chaining state, MAC order, nonces, key math, Vigenere periods, known-plaintext, stream honesty, block birthdays, toolkit, cipher tests. Every unchecked box is dated debt with an owner. Sign only when all rows pass; anything else is findings. A stranger rerunning this track must reach the same green. Pin dependency versions in checklist environments so reruns reproduce exactly across machines. Archive checklist outputs with dates so quarterly progress stays visible. Review archived outputs during planning so past work informs budgets instead of gathering dust.",
             code=(
                 'import hashlib\n'
                 'import hmac\n'
                 '\n'
                 'checks = {}\n'
                 'checks["xor round-trips"] = (bytes(b ^ 0x2B for b in bytes(b ^ 0x2B for b in b"probe")) == b"probe")\n'
                 'checks["hmac verifies"] = hmac.compare_digest(hmac.new(b"k", b"m", hashlib.sha256).hexdigest(), hmac.new(b"k", b"m", hashlib.sha256).hexdigest())\n'
                 'checks["sha256 64 hex"] = (len(hashlib.sha256(b"x").hexdigest()) == 64)\n'
                 'for name, ok in checks.items():\n'
                 '    print("[" + (chr(120) if ok else chr(32)) + "] " + name)\n'
                 'assert all(checks.values())\n'
                 'print("track checklist green: shippable knowledge")'
             ),
             variant_b='a deliberately broken primitive (which check catches it?)',
             variant_c='a skipped phase (what does the checklist reveal?)',
             mistakes=[
                 "Checklist run once at the end instead of after every phase.",
                 "Unchecked boxes silently dropped instead of dated debt.",
                 "Green checklist mistaken for mastery rather than process proof.",
             ],
             qa=(
                 ["Why run the checklist after every phase, not just at the end?",
                  "What distinguishes dated debt from silent gaps?",
                  "What does green actually certify?"],
                 ["Drift compounds: a gap carried six phases costs ten times the early fix, while per-phase checks keep debt freshly visible.",
                  "Owners and dates make missing knowledge scheduled work; silent gaps are surprises with compound interest.",
                  "Process, not mastery: the track ran green end to end, which certifies diligence and coverage — judgment comes from what follows."],
             ),
             homework="Write `track_checklist()` asserting XOR round-trip, HMAC verify and SHA-256 length, printing ticked rows. Run it, print the verdict, and comment which check guards primitives.",
             patterns=["assert ", "sha256("],
             mapping="Sign-off checklists with dated debt close every phase; this one closes the track.",
         ),
         178: dict(
             topic="What this track does not teach",
             idea="Honesty about boundaries: side-channel analysis (power, EM, cache timing) needs labs and oscilloscopes, not Python scripts; elliptic-curve mathematics deserves its own course; post-quantum migration planning needs organisational authority; hardware security modules need hardware; red-team operations need authorisation, scope and rules of engagement no course can grant. Naming limits prevents the most dangerous graduate outcome — confidence without competence. Each boundary ships with a pointer: what to learn next, where, and what prerequisites it assumes. A course that teaches its own edges teaches students to keep learning after it ends. Revisit named limits yearly as fields advance; todays edge becomes tomorrows prerequisite routinely. Calendar revisits so advancing fields trigger updates on schedule. Assign update ownership per topic so advancing fields never wait for volunteers. Fund maintenance explicitly since volunteer-driven updates stall exactly when needed. Budget maintenance as headcount, not goodwill, in annual planning cycles.",
             code=(
                 'limits = ["side channels (labs+scopes)", "elliptic curves (full course)", "PQC migration (org authority)", "HSM ops (hardware)", "red team (authorisation)"]\n'
                 'print("out of scope for this track:")\n'
                 'for i, item in enumerate(limits, 1):\n'
                 '    print(f"  {i}. {item}")\n'
                 'print("named limits prevent confident incompetence")'
             ),
             variant_b='one limit explored deeper (which pointer would you follow first?)',
             variant_c='a limit you already knew (did the track change how you see it?)',
             mistakes=[
                 "Graduating into overconfidence (the named failure mode of security courses).",
                 "Side-channel ignorance presented as side-channel immunity.",
                 "Boundaries read as disclaimers instead of curriculum for what follows.",
             ],
             qa=(
                 ["Why teach limits explicitly instead of ending on triumph?",
                  "How do limits differ from disclaimers?",
                  "What makes a limit actionable rather than decorative?"],
                 ["Triumph without boundaries breeds confident incompetence — the most dangerous graduate outcome in security, where mistakes harm others.",
                  "Disclaimers deflect liability; limits ship with pointers (what next, where, prerequisites) that convert boundaries into curricula.",
                  "A named next step with prerequisites: actionable limits tell students exactly how to cross them when ready."],
             ),
             homework="Write your own out-of-scope list with next-step pointers for three items. Run it, print the list, and comment which pointer you will follow first.",
             patterns=["for ", "print("],
             mapping="Every serious course ends at named edges; post-quantum, ECC math and HSM ops wait beyond them.",
         ),
         179: dict(
             topic="Capstone reflection",
             idea="Look back across 180 days: bytes handled exactly, armour read fluently, XOR laws respected, pads priced honestly, reuse punished by demonstration, randomness sourced correctly, checksums put in their place, oracles closed, dumps read, records parsed, entropy measured honestly, sniffers refusing to guess, contracts asserted, hashes keyed properly, salts uniquified, dead algorithms buried, birthdays respected, chains anchored, tags priced, peppers rotated, content addressed, agility built in, classical ciphers analysed, ECB refused, cribs dragged, chains chained, MACs ordered, nonces counted, keys sized, periods recovered, cribs expected, streams modelled honestly, blocks sized, toolkits assembled, tests asserting, reviews rebuilt, RSA toyed with honestly, signatures verified, DH agreed, MITM feared, secrecy forwarded, sizes budgeted, hybrids shaped, certificates bound, CAs disciplined, revocation freshness-checked, tests contracting, pins traded, handshakes walked, names matched, chains built, revocations distributed, deployments graded, transparency watched, PKI split, mTLS mutualised, downgrades floored, states classified, SSH hardened, toolkits scoped, tests network-free, humans memorising within limits, PBKDF2 iterated honestly, dictionaries priced, peppers rotated, managers audited, logins throttled, MFA phished-aware, diceware shaped, buckets faired, sessions lifecycled, roles owned, secrets rotated, vaults scoped, auth tested. Name three habits kept and one milestone next: dataset, metric, deadline. Foundations, honestly earned. Carry the checklist habit into every future build, verifying before trusting as reflex.",
             code=(
                 'kept = ["verify-before-use", "unique nonces", "TEACHING labels"]\n'
                 'print("habits kept:", len(kept))\n'
                 'for habit in kept:\n'
                 '    print(" -", habit)\n'
                 'print("next: authorised lab, scoped target, dated milestone")'
             ),
             variant_b='your own three habits (which differ from the listed three?)',
             variant_c='your own next milestone (scoped, dated, authorised?)',
             mistakes=[
                 "Finishing without naming what changed — skills unnamed evaporate.",
                 "No next milestone, so momentum dies within a week.",
                 "Mistaking course completion for mastery — foundations, honestly earned.",
             ],
             qa=(
                 ["Why name three habits explicitly instead of 'I learned a lot'?",
                  "Why must the next milestone be scoped and dated?",
                  "What does 'foundations, honestly earned' exclude?"],
                 ["Named habits are checkable and portable; vague satisfaction cannot be rehearsed, tested, or transferred to the next authorised lab.",
                  "Unscoped intentions evaporate; scope plus date plus authorisation converts momentum into an executable plan.",
                  "Production deployment of toy constructions, unauthorised testing, and confidence beyond demonstrated competence."],
             ),
             homework="Write your three kept habits and one concrete next milestone with scope and date. Run it, print it, and comment which habit you will use first tomorrow.",
             patterns=["print(", "="],
             mapping="Reflection with a scoped, dated, authorised next milestone — every ending here is a scoped beginning.",
         ),
     }),
]
