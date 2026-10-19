"""API Building phase 4, days 120-134: auth, security and reliability.

Every example is stdlib-only, offline and deterministic: fixed tokens, fixed
salts, fixed timestamps and fixed iteration counts. Nothing here starts a
server or calls a network, so the applier can execute each snippet and capture
its output exactly as a learner would see it.
"""

PHASE = (
    "Auth, Security and Reliability",
    "Authenticate callers, authorise actions, and keep credentials, input, traffic and failures under control.",
    {
        120: dict(
            topic="Authentication vs authorisation",
            idea=(
                "Authentication answers who is calling; authorisation answers what that caller may do. They are "
                "different decisions, and collapsing them is the classic API bug where any valid token is treated "
                "as permission for every endpoint. Start by resolving a credential into an identity: look up the "
                "token, confirm it is genuine, and attach a subject and its roles. Only then evaluate the requested "
                "action against a policy. Keep the policy in one table so the answer to “may a viewer delete an "
                "order?” is decided once rather than being re-guessed inside handlers. The HTTP status must reflect "
                "which step failed: 401 when identity is missing or invalid, 403 when identity is known but the "
                "action is forbidden. Returning 404 instead of 403 can be a deliberate way to hide resources, but it "
                "must be a decision, not an accident. Log both outcomes with the subject, because a burst of 403s is "
                "an authorisation bug or an attack, and a burst of 401s is usually a broken client. Finally, test "
                "the negative cases first: no token, expired token, wrong role, and the same role on a different "
                "resource. A system that only tests the happy path has not tested authorisation at all."
            ),
            code=(
                'USERS = {\n'
                '    "Bearer tok-alice": {"subject": "alice", "role": "editor"},\n'
                '    "Bearer tok-bob": {"subject": "bob", "role": "viewer"},\n'
                '}\n'
                'POLICY = {"viewer": {"read"}, "editor": {"read", "write"}}\n'
                '\n'
                'def authenticate(headers):\n'
                '    return USERS.get(headers.get("Authorization", ""))\n'
                '\n'
                'def authorise(user, action):\n'
                '    return user is not None and action in POLICY.get(user["role"], set())\n'
                '\n'
                'def handle(headers, action):\n'
                '    user = authenticate(headers)\n'
                '    if user is None:\n'
                '        return 401, {"error": "missing_or_invalid_token"}\n'
                '    if not authorise(user, action):\n'
                '        return 403, {"error": "forbidden", "action": action}\n'
                '    return 200, {"subject": user["subject"], "action": action}\n'
                '\n'
                'print("editor writes:", handle({"Authorization": "Bearer tok-alice"}, "write"))\n'
                'print("viewer writes:", handle({"Authorization": "Bearer tok-bob"}, "write"))\n'
                'print("anonymous reads:", handle({}, "read"))\n'
                'assert handle({}, "read")[0] == 401\n'
                'print("authn and authz are separate gates")'
            ),
            variant_b='give bob the editor role and re-run the viewer-write case',
            variant_c='add a "billing" role that may read invoices but not books, and test both actions',
            mistakes=[
                "Returning 403 for a missing token instead of 401, so clients cannot tell login from permission.",
                "Checking that a token exists but never checking which action the role allows.",
                "Scattering role checks through handlers instead of keeping one policy table.",
            ],
            q1=(
                "Why must authentication be resolved before authorisation is evaluated?",
                "Authorisation needs a known subject and its roles; without a verified identity there is nothing to evaluate a policy against.",
            ),
            homework=(
                "Write `authorise_request(headers, action, policy)` that authenticates a token, looks up its role, "
                "and returns 401, 403 or 200 with the subject. Run it on two different users and three actions, "
                "print every result, and comment which line keeps identity separate from permission."
            ),
            patterns=["def authenticate", "def authorise", "return 403"],
            mapping=(
                "OAuth2 separates authentication at the identity provider from scopes and roles checked by the "
                "resource server. The 401-before-403 ordering is the same contract in every framework."
            ),
        ),
        121: dict(
            topic="API keys",
            idea=(
                "An API key identifies a calling service rather than a human, which makes it perfect for "
                "server-to-server integrations and dangerous when pasted into a browser. The key is a bearer "
                "secret: whoever holds it is the account, so treat it like a password. Store only a hash, never the "
                "key itself, because a leaked database should not become a leaked set of live credentials. Keep a "
                "short public prefix so support can identify a key without seeing the secret, and compare digests "
                "in constant time to avoid timing leaks. Scope every key to the smallest set of actions it needs, and "
                "give each one an owner, a creation date and a revocation switch. Keys should be rotatable without "
                "downtime: accept old and new during a short overlap, then disable the old one. Never put keys in "
                "URLs, because URLs end up in access logs, browser history and referrer headers; use an "
                "Authorization header. Never ship a key in a mobile app or front-end bundle, where any user can "
                "extract it. Today you verify a presented key against stored digests and reject wrong, truncated "
                "and revoked values. The mapping is direct: API gateways, cloud SDKs and payment providers all "
                "build on this exact discipline."
            ),
            code=(
                'import hashlib\n'
                'import hmac\n'
                '\n'
                'def digest(key):\n'
                '    return hashlib.sha256(key.encode()).hexdigest()\n'
                '\n'
                'RECORDS = [\n'
                '    {"prefix": "sk_live_acme", "digest": digest("sk_live_acme_7f3a"), "account": "acme", "revoked": False},\n'
                '    {"prefix": "sk_live_old1", "digest": digest("sk_live_old1_991b"), "account": "oldco", "revoked": True},\n'
                ']\n'
                '\n'
                'def verify(presented):\n'
                '    if len(presented) < 12:\n'
                '        return None\n'
                '    prefix = presented[:12]\n'
                '    for record in RECORDS:\n'
                '        if record["prefix"] == prefix and not record["revoked"]:\n'
                '            if hmac.compare_digest(record["digest"], digest(presented)):\n'
                '                return record["account"]\n'
                '    return None\n'
                '\n'
                'print("live key ->", verify("sk_live_acme_7f3a"))\n'
                'print("wrong key ->", verify("sk_live_acme_0000"))\n'
                'print("revoked key ->", verify("sk_live_old1_991b"))\n'
                'print("truncated key ->", verify("short"))\n'
                'assert verify("sk_live_acme_7f3a") == "acme"\n'
                'print("only hashed, active keys authenticate")'
            ),
            variant_b='add a second active key for acme with a different prefix and confirm both verify',
            variant_c='un-revoke oldco and show that verification depends on the revocation flag, not the prefix',
            mistakes=[
                "Storing the raw key in the database, so one dump exposes every integration.",
                "Comparing keys with ordinary equality, which can leak length and prefix through timing.",
                "Accepting a key with no scopes, giving a read-only integration write access by default.",
            ],
            q1=(
                "Why store a hash of an API key instead of the key itself?",
                "Login-style verification only needs to recompute the digest; a stolen database then yields no usable live credentials.",
            ),
            homework=(
                "Write `verify_key(presented, records)` that matches a public prefix and compares SHA-256 digests "
                "in constant time, rejecting revoked records. Run it with one valid and two invalid keys, print all "
                "three results, and comment which line prevents a plaintext key database."
            ),
            patterns=["compare_digest", "sha256", "return None"],
            mapping=(
                "API gateway key plans, Stripe-style restricted keys and cloud service accounts all hash or scope "
                "their credentials at rest. Rotation with an overlap window is the standard operational practice."
            ),
        ),
        122: dict(
            topic="Bearer tokens",
            idea=(
                "A bearer token is a credential the server accepts without further proof, so possession is the whole "
                "security model. OAuth2 access tokens and JWTs are the common shapes: a signed payload carrying a "
                "subject, scopes and an expiry. The signature proves the issuer created the claims; it does not "
                "encrypt them, so never put secrets in the payload. Verification has three separate jobs, and "
                "skipping any one is a real vulnerability. First check the signature with the issuer’s key, using a "
                "constant-time comparison. Second check the expiry against the server’s clock, not the client’s, and "
                "allow only a small clock skew. Third check the audience and scopes for the specific endpoint, because "
                "a token minted for the billing service should not open the admin API. Rotate the signing key on a "
                "schedule, and let the token carry a key identifier so the server knows which key to trust. Reject unsigned tokens "
                "outright rather than accepting the common “alg: none” trick, and never trust a token just because it "
                "decodes. Short lifetimes limit the damage of theft; refresh tokens let clients renew without sending "
                "passwords repeatedly. Today you build and verify a compact signed token with a fixed secret and a "
                "fixed clock so the result is reproducible, then tamper with the subject to watch verification fail."
            ),
            code=(
                'import base64\n'
                'import hashlib\n'
                'import hmac\n'
                'import json\n'
                '\n'
                'SECRET = b"fixed-demo-signing-key"\n'
                '\n'
                'def b64(data):\n'
                '    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()\n'
                '\n'
                'def unb64(text):\n'
                '    return base64.urlsafe_b64decode(text + "=" * (-len(text) % 4))\n'
                '\n'
                'def sign(raw):\n'
                '    return b64(hmac.new(SECRET, raw, hashlib.sha256).digest())\n'
                '\n'
                'def issue(claims):\n'
                '    raw = json.dumps(claims, sort_keys=True, separators=(",", ":")).encode()\n'
                '    return b64(raw) + "." + sign(raw)\n'
                '\n'
                'def verify(token, now):\n'
                '    try:\n'
                '        encoded, signature = token.split(".")\n'
                '    except ValueError:\n'
                '        return None\n'
                '    raw = unb64(encoded)\n'
                '    if not hmac.compare_digest(sign(raw), signature):\n'
                '        return None\n'
                '    claims = json.loads(raw)\n'
                '    if claims.get("exp", 0) <= now:\n'
                '        return None\n'
                '    return claims\n'
                '\n'
                'token = issue({"sub": "alice", "scope": "orders:read", "exp": 1700000600})\n'
                'print("valid ->", verify(token, 1700000000))\n'
                'print("expired ->", verify(token, 1700000700))\n'
                'encoded, signature = token.split(".")\n'
                'first = "A" if encoded[0] != "A" else "B"\n'
                'tampered = first + encoded[1:] + "." + signature\n'
                'print("tampered ->", verify(tampered, 1700000000))\n'
                'assert verify(tampered, 1700000000) is None\n'
                'print("signature covers the claims")'
            ),
            variant_b='change exp to 1700000000 and verify at the same instant (boundary case)',
            variant_c='change scope to orders:write and note that the token is still valid until authorisation checks it',
            mistakes=[
                "Reading the payload without verifying the signature, then trusting the subject it claims.",
                "Ignoring expiry, so a stolen token works forever.",
                "Using the token for an endpoint whose audience or scope it was never issued for.",
            ],
            q1=(
                "Why is a bearer token dangerous if it leaks?",
                "Possession alone authenticates the caller, so anyone holding it can act as the subject until the token expires or is revoked.",
            ),
            homework=(
                "Write `verify_token(token, secret, now)` that checks an HMAC signature with compare_digest, "
                "rejects malformed tokens, and enforces expiry. Run it on a valid token and one tampered token, "
                "print both results, and comment which line proves the claims were not altered."
            ),
            patterns=["hmac.new", "compare_digest", "exp"],
            mapping=(
                "JWT access tokens carry the same header-payload-signature shape, usually verified with RS256 or "
                "ES256. OAuth2 adds issuer, audience and scope checks around this exact primitive."
            ),
        ),
        123: dict(
            topic="Password hashing",
            idea=(
                "Passwords are the credential users reuse everywhere, so a password database is a liability unless it "
                "is hashed properly. Hashing is one-way: the server stores a digest, and login re-computes the "
                "digest from the submitted password and compares. A fast hash such as plain SHA-256 is the wrong "
                "tool, because attackers try billions of guesses per second on stolen data. Password hashing must "
                "be deliberately slow and salted. A salt is a unique random value stored beside each digest; it "
                "makes precomputed tables useless and ensures two users with the same password get different "
                "digests. An iteration count raises the cost of each guess, and it must be stored with the hash so it "
                "can be raised later. Verify with a constant-time comparison, never with ordinary equality on "
                "secrets. Never email a password, never log it, and never cap it at a short length that encourages "
                "weak choices. Modern systems use bcrypt, scrypt or argon2, which also resist GPU cracking; today you "
                "use PBKDF2-HMAC-SHA256 with a fixed salt and a fixed iteration count so the output is deterministic "
                "for study. Store the salt and iteration count beside each digest so the cost can be raised, and "
                "re-hash on the next successful login. The discipline is what transfers: unique salt, high cost, "
                "constant-time check, and an upgrade path."
            ),
            code=(
                'import hashlib\n'
                'import hmac\n'
                '\n'
                'ITERATIONS = 120000\n'
                '\n'
                'def hash_password(password, salt):\n'
                '    return hashlib.pbkdf2_hmac(\n'
                '        "sha256", password.encode(), salt.encode(), ITERATIONS\n'
                '    ).hex()\n'
                '\n'
                'def verify(password, salt, expected):\n'
                '    candidate = hash_password(password, salt)\n'
                '    return hmac.compare_digest(candidate, expected)\n'
                '\n'
                'salt_a = "demo-salt-user-a"\n'
                'salt_b = "demo-salt-user-b"\n'
                'stored = hash_password("correct horse battery", salt_a)\n'
                'print("stored digest:", stored[:32], "...")\n'
                'print("correct password:", verify("correct horse battery", salt_a, stored))\n'
                'print("wrong password:", verify("correct horse batterY", salt_a, stored))\n'
                '\n'
                'same_password_other_salt = hash_password("correct horse battery", salt_b)\n'
                'print("same password, new salt is different:", stored != same_password_other_salt)\n'
                'print("iterations:", ITERATIONS)\n'
                'assert stored != same_password_other_salt\n'
                'print("unique salt defeats precomputation")'
            ),
            variant_b='raise ITERATIONS to 200000 and note the digest changes without changing the password',
            variant_c='hash the same password with salt_b and compare both stored digests for equality',
            mistakes=[
                "Storing plain SHA-256, which is fast enough to brute-force at enormous scale.",
                "Using one global salt, so identical passwords share a digest and one crack opens many accounts.",
                "Comparing digests with == instead of hmac.compare_digest, leaking timing information.",
            ],
            q1=(
                "Why does a per-user salt make precomputed password tables useless?",
                "The attacker must rebuild the table for every salt, so the same guess costs full work for each account instead of once.",
            ),
            homework=(
                "Write `hash_password(password, salt, iterations)` and `verify_password(password, salt, digest)` "
                "using PBKDF2 and compare_digest. Run it with the correct password, a wrong one, and a different "
                "salt, print all three results, and comment which value makes identical passwords diverge."
            ),
            patterns=["pbkdf2_hmac", "compare_digest", "salt"],
            mapping=(
                "bcrypt, scrypt and argon2 are the production choices because they are memory-hard as well as slow. "
                "PBKDF2-HMAC is the same discipline with a simpler cost model, and its stored parameters enable "
                "upgrades at login."
            ),
        ),
        124: dict(
            topic="HMAC request signing",
            idea=(
                "An HMAC signature proves that a request came from someone who holds a shared secret, and that the "
                "request was not altered in transit. The client builds a canonical string from the parts that "
                "matter — method, path, timestamp and a hash of the body — signs it with HMAC-SHA256, and sends the "
                "signature in a header. The server rebuilds the same string and compares signatures in constant "
                "time. Every field you omit from the canonical string is a field an attacker can change for free, "
                "which is why method and path must be included, not just the body. Include a timestamp to limit "
                "replay: a signature from an hour ago should be rejected even if it is mathematically valid, and the "
                "server should remember recently seen nonces if the window is wide. The secret never travels with "
                "the request, unlike a bearer token, so interception of one request does not hand over the key. That "
                "is why payment providers, webhooks and internal service calls use this pattern. The hard part is "
                "canonicalisation: both sides must agree on whitespace, encoding, header order and clock skew, or "
                "valid requests fail mysteriously. Today you sign a fixed request, verify it, then change the body "
                "and watch verification fail."
            ),
            code=(
                'import hashlib\n'
                'import hmac\n'
                '\n'
                'SECRET = b"shared-webhook-secret-v1"\n'
                'MAX_SKEW = 300\n'
                '\n'
                'def canonical(method, path, timestamp, body):\n'
                '    return f"{method}\\n{path}\\n{timestamp}\\n{body}".encode()\n'
                '\n'
                'def sign(method, path, timestamp, body):\n'
                '    return hmac.new(\n'
                '        SECRET, canonical(method, path, timestamp, body), hashlib.sha256\n'
                '    ).hexdigest()\n'
                '\n'
                'def verify(method, path, timestamp, body, signature, now):\n'
                '    if abs(now - int(timestamp)) > MAX_SKEW:\n'
                '        return "stale_timestamp"\n'
                '    expected = sign(method, path, timestamp, body)\n'
                '    if not hmac.compare_digest(expected, signature):\n'
                '        return "bad_signature"\n'
                '    return "accepted"\n'
                '\n'
                'body = \'{"amount": 100, "currency": "EUR"}\'\n'
                'ts = "1700000000"\n'
                'signature = sign("POST", "/payments", ts, body)\n'
                'print("signature:", signature[:24], "...")\n'
                'print("original:", verify("POST", "/payments", ts, body, signature, 1700000100))\n'
                'print("tampered:", verify("POST", "/payments", ts, \'{"amount": 9000}\', signature, 1700000100))\n'
                'print("stale:", verify("POST", "/payments", ts, body, signature, 1700000900))\n'
                'assert verify("POST", "/payments", ts, \'{"amount": 9000}\', signature, 1700000100) == "bad_signature"\n'
                'print("body, method and time are all covered")'
            ),
            variant_b='sign the path /refunds instead and verify against /payments to see the mismatch',
            variant_c='use a timestamp 301 seconds old and confirm the skew check wins before the signature check',
            mistakes=[
                "Signing only the body, leaving the method and path free for an attacker to change.",
                "Comparing signatures with == rather than hmac.compare_digest.",
                "Accepting any timestamp, which makes a captured request replayable forever.",
            ],
            q1=(
                "Why include the method, path and timestamp in the signed string, not just the body?",
                "Otherwise a valid body signature could be replayed against a different endpoint or at any later time, since those fields were never covered.",
            ),
            homework=(
                "Write `sign_request(secret, method, path, timestamp, body)` and `verify_request(...)` that checks "
                "skew and uses compare_digest. Run it on an intact request and a tampered body, print both verdicts, "
                "and comment which component stops replay."
            ),
            patterns=["hmac.new", "canonical", "compare_digest"],
            mapping=(
                "Stripe webhooks, AWS SigV4 and GitHub webhooks all sign a canonical request and enforce a "
                "timestamp window. The shared secret stays server-side; only the signature crosses the wire."
            ),
        ),
        125: dict(
            topic="Input validation and injection",
            idea=(
                "Every value that crosses the API boundary is hostile until proven otherwise. Input validation means "
                "checking type, shape, length, range and allowed values before the value reaches business logic or a "
                "database. It is not a courtesy to clients; it is the line between a 400 and a corrupted table. "
                "Injection happens when input is treated as code: SQL, shell commands, template expressions or log "
                "formats. The defences are boring and effective. Use parameterised queries so the database parses "
                "the query and the data separately, never string concatenation. Allowlist formats rather than "
                "blocklisting characters, because blocklists always miss an encoding. Reject unexpected fields "
                "instead of silently ignoring them. Bound every string and collection by length, and return "
                "field-level errors so clients can fix the request. Validation belongs in one place at the edge, not "
                "repeated inconsistently in each handler. Today you create an in-memory SQLite table, query it with a "
                "parameter, and pass a classic injection string to show it is treated as a literal value. Then you "
                "validate a payload and collect errors for a missing field and an oversized value. The mapping is "
                "direct: ORMs, schema validators and API gateways automate this, but only if you know what they are "
                "protecting."
            ),
            code=(
                'import sqlite3\n'
                '\n'
                'conn = sqlite3.connect(":memory:")\n'
                'conn.execute("CREATE TABLE users (name TEXT, role TEXT)")\n'
                'conn.execute("INSERT INTO users VALUES (?, ?)", ("alice", "admin"))\n'
                '\n'
                'def find_user(name):\n'
                '    query = "SELECT name, role FROM users WHERE name = ?"\n'
                '    return conn.execute(query, (name,)).fetchall()\n'
                '\n'
                'injection = "alice\' OR \'1\'=\'1"\n'
                'print("normal lookup:", find_user("alice"))\n'
                'print("injection string:", find_user(injection))\n'
                '\n'
                'def validate(payload):\n'
                '    errors = []\n'
                '    if not isinstance(payload.get("name"), str):\n'
                '        errors.append("name must be a string")\n'
                '    elif not 1 <= len(payload["name"]) <= 40:\n'
                '        errors.append("name length must be 1..40")\n'
                '    if payload.get("role") not in {"viewer", "editor"}:\n'
                '        errors.append("role must be viewer or editor")\n'
                '    return errors\n'
                '\n'
                'print("valid payload:", validate({"name": "bob", "role": "viewer"}))\n'
                'print("bad payload:", validate({"name": "", "role": "root"}))\n'
                'print("oversized:", validate({"name": "x" * 41, "role": "viewer"}))\n'
                'assert find_user(injection) == []\n'
                'print("parameter binding keeps data out of the query")'
            ),
            variant_b='query with f-string interpolation and print the SQL text to see the injection',
            variant_c='send a role of "viewer " with trailing whitespace and decide whether to normalise or reject',
            mistakes=[
                "Building SQL with f-strings, so a quote in a name changes the query structure.",
                "Validating only in the browser, which an attacker bypasses with a direct request.",
                "Accepting unknown fields silently, then forwarding them to a database or template.",
            ],
            q1=(
                "Why does a parameterised query stop the classic OR injection string?",
                "The database treats the bound value as data, so quotes inside it never become query syntax.",
            ),
            homework=(
                "Write `validate_user(payload)` that returns a list of field errors for type, length and allowed "
                "role, then query SQLite with a bound parameter. Run it on one valid and two invalid payloads, print "
                "all results, and comment which line keeps input out of the SQL text."
            ),
            patterns=["execute(", "?", "validate"],
            mapping=(
                "ORMs parameterise by default, and schema libraries such as Pydantic enforce type and range at the "
                "edge. Neither replaces knowing why a bound parameter is different from string interpolation."
            ),
        ),
        126: dict(
            topic="Rate limiting",
            idea=(
                "Rate limiting protects capacity, fairness and security at the same time. Without it, one client can "
                "exhaust the database, scrape the catalogue, or brute-force a login by trying passwords quickly. A "
                "simple fixed-window counter stores a key, a window start and a count; each request increments the "
                "count if the window is still open, and resets it otherwise. When the count exceeds the limit, "
                "return 429 with a Retry-After header so well-behaved clients back off. Choose the key deliberately: "
                "per API key for fairness, per IP for anonymous traffic, and per account for login attempts, where "
                "IP alone is defeated by botnets. Fixed windows are cheap but allow a burst at the boundary, "
                "because a client can spend the quota at the end of one window and again at the start of the next. "
                "Sliding windows and token buckets smooth that out at the cost of more state. In a distributed "
                "system the counter must live in a shared store such as Redis, or each server will enforce its own "
                "private limit. Always exempt health checks and internal jobs, and never let a limiter failure take "
                "down the API. Today you implement a deterministic fixed-window limiter with a fixed clock and show "
                "the request that finally gets 429."
            ),
            code=(
                'def allow(state, key, now, limit=3, window=60):\n'
                '    entry = state.get(key)\n'
                '    if entry is None or now - entry[0] >= window:\n'
                '        state[key] = [now, 1]\n'
                '        return True, limit - 1\n'
                '    if entry[1] >= limit:\n'
                '        return False, 0\n'
                '    entry[1] += 1\n'
                '    return True, limit - entry[1]\n'
                '\n'
                'state = {}\n'
                'for now in (100, 101, 102, 103, 104):\n'
                '    allowed, remaining = allow(state, "key-acme", now)\n'
                '    print("t=100..104 request ->", allowed, "| remaining:", remaining)\n'
                '\n'
                'print("at t=161 ->", allow(state, "key-acme", 161))\n'
                'print("other key ->", allow(state, "key-other", 161))\n'
                'assert allow(state, "key-fresh", 100)[1] == 2\n'
                'print("quota is per key and resets after the window")'
            ),
            variant_b='set limit=1 and show that the second request in the same window is rejected',
            variant_c='start a request at t=159 and another at t=161 with limit=3 to see the boundary burst',
            mistakes=[
                "Limiting per IP only, so one botnet or shared office proxy controls the outcome for everyone.",
                "Returning 500 when the limiter trips, instead of 429 with a clear retry hint.",
                "Keeping counters in process memory on several servers, so each enforces its own private limit.",
            ],
            q1=(
                "Why can a fixed window allow twice the intended limit around a boundary?",
                "A client can spend the full quota at the end of one window and the full quota again at the start of the next, since the counters reset independently.",
            ),
            homework=(
                "Write `allow(state, key, now, limit, window)` implementing a fixed-window counter and returning "
                "allowed plus remaining. Run it on two keys and a window reset, print every decision, and comment "
                "which line makes the limit per key rather than global."
            ),
            patterns=["state.get", "return True", "return False"],
            mapping=(
                "API gateways expose per-key quotas, and login flows add per-account and per-IP limits together. "
                "Distributed limiters use Redis counters or token buckets so all replicas share one view."
            ),
        ),
        127: dict(
            topic="Idempotency keys",
            idea=(
                "Networks retry. A client times out, a load balancer resends, a user double-clicks, and a payment is "
                "charged twice. An idempotency key makes a write safe to repeat: the client generates a unique key "
                "per logical operation and sends it with the request. The server records the key and the response "
                "it produced; if the same key arrives again, the server returns the stored response instead of "
                "performing the side effect a second time. The key belongs to the operation, not the HTTP "
                "connection, and it should be scoped to the authenticated account so one customer cannot replay "
                "another’s key. Store the record in the same transaction as the effect when possible, or use a "
                "unique constraint to make the race safe. The record needs a retention window, because keys cannot "
                "grow forever. If the same key arrives with a different payload, return 409 rather than silently "
                "replaying a response for different input. Idempotency does not replace retries; it makes them safe. "
                "It also does not make GET idempotent — GET already is. Today you store a key, create a record once, "
                "replay the same key twice, and print the side-effect count to prove the second call did not create "
                "a second resource. The pattern is standard at payment providers and anywhere a duplicate charge is "
                "unacceptable."
            ),
            code=(
                'def create_payment(store, key, amount):\n'
                '    if key in store:\n'
                '        return 200, store[key], "replayed"\n'
                '    payment = {"id": f"pay-{len(store) + 1}", "amount": amount}\n'
                '    store[key] = payment\n'
                '    return 201, payment, "created"\n'
                '\n'
                'store = {}\n'
                'print("first  ->", create_payment(store, "idem-abc", 100))\n'
                'print("retry  ->", create_payment(store, "idem-abc", 100))\n'
                'print("second ->", create_payment(store, "idem-xyz", 50))\n'
                'print("payments in store:", list(store.values()))\n'
                'print("side effects:", len(store))\n'
                'assert len(store) == 2\n'
                'print("one key, one effect")'
            ),
            variant_b='replay idem-abc with amount 999 and decide whether the server should replay or return 409',
            variant_c='use a fresh key idem-def for the same amount and confirm it creates a new payment',
            mistakes=[
                "Letting the server generate the key, so a client retry creates a different key and a duplicate charge.",
                "Storing the key without the response, so a replay cannot return the original result.",
                "Ignoring a changed payload under the same key instead of rejecting it as a conflict.",
            ],
            q1=(
                "Why must the client generate the idempotency key rather than the server?",
                "Only the client knows that two attempts are the same logical operation; a server-generated key would differ on every retry.",
            ),
            homework=(
                "Write `create_payment(store, key, amount)` that stores the first response and replays it for a "
                "repeated key. Run it with one key twice and a second key once, print all three responses, and "
                "comment which line prevents the duplicate side effect."
            ),
            patterns=["if key in", "return 200", "return 201"],
            mapping=(
                "Payment providers accept an Idempotency-Key header and retain the result for a stated window. "
                "The same pattern protects webhook processing and any retried POST that creates money or state."
            ),
        ),
        128: dict(
            topic="Timeouts and retries",
            idea=(
                "Timeouts and retries are how a client survives a network that is slower and less reliable than the "
                "test suite. A timeout is a promise to stop waiting: without one, a single stalled dependency can "
                "exhaust every worker and take down the whole service. Set timeouts at every hop — connection, read "
                "and total request — and make the total budget smaller than the caller’s budget so failures surface "
                "before the user gives up. Retries are only safe for transient failures and only for operations that "
                "can be repeated. Retrying a timeout on a non-idempotent POST can duplicate a charge, which is why "
                "retries belong with idempotency keys or on reads. Use a small maximum, exponential backoff and "
                "jitter so a recovering service is not stampeded by every client at once. Do not retry validation "
                "errors or 4xx responses; they will fail identically forever. Circuit breakers stop retrying a "
                "dependency that is clearly down, and bulkheads isolate one slow dependency from the rest. Today you "
                "simulate a flaky call with a fixed sequence of outcomes, apply a bounded retry loop with computed "
                "backoff, and print each attempt and the final result. No sleeping is needed: the arithmetic of the "
                "delay is the lesson. The mapping is every HTTP client and service mesh you will meet."
            ),
            code=(
                'def call_service(outcomes, attempt):\n'
                '    return outcomes[attempt - 1]\n'
                '\n'
                'def with_retries(outcomes, max_attempts=3):\n'
                '    for attempt in range(1, max_attempts + 1):\n'
                '        result = call_service(outcomes, attempt)\n'
                '        print("attempt", attempt, "->", result)\n'
                '        if result == "ok":\n'
                '            return True, attempt\n'
                '        if result == "invalid_request":\n'
                '            return False, attempt\n'
                '        backoff = 2 ** (attempt - 1)\n'
                '        print("  transient failure, next delay", backoff, "s")\n'
                '    return False, max_attempts\n'
                '\n'
                'print("flaky service:", with_retries(["timeout", "timeout", "ok"]))\n'
                'print("permanent 4xx:", with_retries(["invalid_request", "ok"]))\n'
                'print("out of budget:", with_retries(["timeout", "timeout", "timeout"]))\n'
                'assert with_retries(["timeout", "ok"]) == (True, 2)\n'
                'print("retries are bounded and skip permanent failures")'
            ),
            variant_b='give the flaky service four timeouts and a max_attempts of three to reach exhaustion',
            variant_c='put "ok" on the first attempt and confirm no backoff line is printed',
            mistakes=[
                "Retrying a non-idempotent write without a key, turning one timeout into two charges.",
                "Retrying 400 and 422 responses, which will never succeed no matter how often they are sent.",
                "Setting no timeout at all, so a stalled dependency holds workers until the service collapses.",
            ],
            q1=(
                "Why should a 422 response never be retried?",
                "It means the request itself is invalid, so repeating the same payload produces the same rejection and only adds load.",
            ),
            homework=(
                "Write `retry_call(outcomes, max_attempts)` returning success plus attempts, with exponential "
                "backoff printed and permanent failures returned immediately. Run it on two outcome sequences, "
                "print both traces, and comment which branch prevents a pointless retry."
            ),
            patterns=["for attempt", "backoff", "return False"],
            mapping=(
                "HTTP clients expose connect and read timeouts; retry middleware adds backoff and jitter. "
                "Kubernetes and service meshes add circuit breakers and deadlines on top of the same policy."
            ),
        ),
        129: dict(
            topic="TLS and transport security",
            idea=(
                "TLS protects credentials and data in transit, and “we use HTTPS” is only true if it is enforced "
                "everywhere. Plain HTTP sends headers and bodies in clear text, so a bearer token or password on an "
                "http:// URL is readable by anyone on the path. Switching the scheme on the login form is not "
                "enough: a single image, redirect or legacy endpoint over HTTP lets an attacker downgrade or steal "
                "the session. Enforce HTTPS at the edge, redirect safely, and send HSTS so browsers refuse plaintext "
                "for the future. Inside the connection, verify the certificate chain and the hostname; a client that "
                "accepts any certificate defeats the entire protocol. Certificate pinning adds a second check by "
                "comparing a hash of the server’s public key or certificate against a known value, which limits "
                "damage from a compromised certificate authority, but pins must have a rotation plan or they become "
                "an outage. Never roll your own encryption, and never treat base64 as protection. Today you "
                "demonstrate that a token in an HTTP request is visible, then enforce an https-only transport check "
                "and verify a fixed certificate fingerprint with a constant-time comparison. The mapping is direct: "
                "TLS 1.3, HSTS, certificate pinning and mTLS are the production versions of these checks."
            ),
            code=(
                'import hashlib\n'
                'import hmac\n'
                '\n'
                'CERT_DER = b"demo-certificate-bytes"\n'
                'PIN = hashlib.sha256(CERT_DER).hexdigest()\n'
                '\n'
                'def transport(scheme, cert_der, token):\n'
                '    if scheme != "https":\n'
                '        return 400, {"error": "https_required", "exposed": token}\n'
                '    fingerprint = hashlib.sha256(cert_der).hexdigest()\n'
                '    if not hmac.compare_digest(fingerprint, PIN):\n'
                '        return 495, {"error": "certificate_pin_mismatch"}\n'
                '    return 200, {"delivered": True}\n'
                '\n'
                'token = "Bearer tok-alice"\n'
                'print("plain http ->", transport("http", CERT_DER, token))\n'
                'print("wrong pin ->", transport("https", b"other-certificate", token))\n'
                'print("verified tls ->", transport("https", CERT_DER, token))\n'
                'print("response header: Strict-Transport-Security: max-age=31536000; includeSubDomains")\n'
                'assert transport("http", CERT_DER, token)[0] == 400\n'
                'print("transport is checked before the credential is trusted")'
            ),
            variant_b='pass a certificate signed by another authority and confirm the pin check rejects it',
            variant_c='keep the right certificate but send the scheme as "http" and note the token appears in the error',
            mistakes=[
                "Disabling certificate verification in an HTTP client to “make it work”.",
                "Using base64 or a custom XOR scheme and calling it encryption.",
                "Serving one legacy endpoint over HTTP, which opens a downgrade path for the whole session.",
            ],
            q1=(
                "Why does a correct certificate chain still need a hostname check?",
                "A valid certificate for a different host proves that host’s identity, not the one the client intended to reach.",
            ),
            homework=(
                "Write `secure_transport(scheme, cert_der, expected_pin)` that rejects non-HTTPS and verifies a "
                "SHA-256 fingerprint with compare_digest. Run it on plain HTTP, a wrong certificate and the right "
                "one, print all three results, and comment which check blocks the downgrade."
            ),
            patterns=["sha256", "compare_digest", "https"],
            mapping=(
                "TLS 1.3 protects the channel, HSTS prevents future plaintext, and public-key pinning constrains "
                "which certificates clients accept. mTLS extends the same verification to the client identity."
            ),
        ),
        130: dict(
            topic="CORS done safely",
            idea=(
                "CORS is a browser rule, not a server security boundary. A browser blocks JavaScript on one origin "
                "from reading responses from another unless the server explicitly allows it. The server expresses "
                "that permission with Access-Control-Allow-Origin and related headers, and the browser enforces "
                "them. The danger is the shortcut: reflecting any Origin back, or allowing * together with "
                "credentials, silently turns every website into an authorised client. A safe policy keeps an "
                "explicit allowlist of trusted origins, echoes only an exact match, and adds Vary: Origin so caches "
                "do not serve one site’s allowed response to another. Preflight requests for non-simple methods and "
                "custom headers must be answered deliberately, with the smallest allowed method and header set. Do "
                "not confuse CORS with authentication: a request can be sent cross-origin even when the response is "
                "blocked, so state-changing endpoints still need CSRF protection when cookies are used. Never put "
                "secrets in JavaScript; CORS cannot protect data from a user who owns the browser. Today you compute "
                "headers for an allowed origin, an evil origin and a wildcard-plus-credentials case, and print what "
                "the browser would permit. The mapping is the same header set every framework emits, and the same "
                "mistakes appear in production."
            ),
            code=(
                'ALLOWED = {"https://app.example.com", "https://admin.example.com"}\n'
                '\n'
                'def cors_headers(origin, credentials=False):\n'
                '    headers = {}\n'
                '    if origin in ALLOWED:\n'
                '        headers["Access-Control-Allow-Origin"] = origin\n'
                '        headers["Vary"] = "Origin"\n'
                '    elif origin == "*" and not credentials:\n'
                '        headers["Access-Control-Allow-Origin"] = "*"\n'
                '    if credentials and headers:\n'
                '        headers["Access-Control-Allow-Credentials"] = "true"\n'
                '    return headers\n'
                '\n'
                'print("trusted:", cors_headers("https://app.example.com", credentials=True))\n'
                'print("evil:", cors_headers("https://evil.example", credentials=True))\n'
                'print("wildcard with cookies:", cors_headers("*", credentials=True))\n'
                'print("public read:", cors_headers("*", credentials=False))\n'
                'assert "Access-Control-Allow-Origin" not in cors_headers("https://evil.example")\n'
                'print("only the exact allowlist is echoed")'
            ),
            variant_b='add "https://preview.example.com" to the allowlist and re-run the evil-origin case',
            variant_c='reflect the request origin blindly for every site and explain what that breaks',
            mistakes=[
                "Reflecting any Origin header, which authorises every website that calls the API.",
                "Combining Access-Control-Allow-Origin: * with credentials, a combination browsers reject.",
                "Assuming CORS prevents cross-site state changes, when it only controls response reading.",
            ],
            q1=(
                "Why is reflecting the request Origin back to the caller unsafe?",
                "It approves whoever asks, so any malicious site can read authenticated responses instead of being limited to a trusted allowlist.",
            ),
            homework=(
                "Write `cors_headers(origin, allowed, credentials)` that echoes only an exact allowlist match and "
                "adds Vary: Origin. Run it for a trusted origin, an untrusted one and a wildcard request, print all "
                "results, and comment which line refuses the untrusted site."
            ),
            patterns=["ALLOWED", "Vary", "Allow-Origin"],
            mapping=(
                "Frameworks expose CORS middleware with an origins list, but the safe policy is yours: exact "
                "matches, Vary: Origin, and never wildcard with credentials. CSRF protection remains a separate "
                "control for cookie-based sessions."
            ),
        ),
        131: dict(
            topic="Secrets and configuration",
            idea=(
                "Secrets are the credentials your service uses to talk to databases, payment providers and other "
                "services, and configuration is everything that changes between environments. The rule is simple: "
                "secrets live in the environment or a secret manager, never in code, never in a repository, never in "
                "a container image and never in a log. Configuration should be validated at startup, not discovered "
                "at the first request. Fail fast if a required value is missing or obviously weak, because a service "
                "that boots with an empty signing key is worse than one that refuses to start. Give each environment "
                "its own credentials so a staging leak cannot touch production, and rotate secrets on a schedule "
                "with a documented overlap. Redact sensitive fields before logging or returning configuration to an "
                "admin UI. Avoid defaults for secrets: a default password is a published password. Keep a single "
                "typed config object rather than reading environment variables all over the codebase, so the "
                "complete set of dependencies is visible in one place. Today you load a fixed configuration "
                "dictionary, validate required keys and a minimum secret length, then print a redacted view that "
                "hides the secret. The mapping is twelve-factor configuration, vaults and managed identity; the "
                "principle is the same at every scale."
            ),
            code=(
                'REQUIRED = ("DATABASE_URL", "API_SECRET")\n'
                '\n'
                'def load_config(env):\n'
                '    missing = [name for name in REQUIRED if not env.get(name)]\n'
                '    if missing:\n'
                '        raise ValueError(f"missing config: {missing}")\n'
                '    secret = env["API_SECRET"]\n'
                '    if len(secret) < 16:\n'
                '        raise ValueError("API_SECRET must be at least 16 characters")\n'
                '    return {"database_url": env["DATABASE_URL"], "api_secret": secret}\n'
                '\n'
                'def redact(config):\n'
                '    clean = {}\n'
                '    for key, value in config.items():\n'
                '        if "secret" in key or "password" in key or "token" in key:\n'
                '            clean[key] = "***redacted***"\n'
                '        else:\n'
                '            clean[key] = value\n'
                '    return clean\n'
                '\n'
                'env = {\n'
                '    "DATABASE_URL": "postgres://app@db.internal/school",\n'
                '    "API_SECRET": "a-fixed-demo-secret-value",\n'
                '}\n'
                'config = load_config(env)\n'
                'print("redacted config:", redact(config))\n'
                '\n'
                'try:\n'
                '    load_config({"DATABASE_URL": "postgres://app@db.internal/school", "API_SECRET": "short"})\n'
                'except ValueError as exc:\n'
                '    print("startup refused:", exc)\n'
                'assert redact(config)["api_secret"] == "***redacted***"\n'
                'print("config is validated early and never logged raw")'
            ),
            variant_b='remove DATABASE_URL from the environment and show the missing-config failure',
            variant_c='add a STRIPE_TOKEN key and confirm redact hides it by name',
            mistakes=[
                "Committing a .env file or a hardcoded fallback secret to the repository.",
                "Logging the whole config object on startup, which copies secrets into log storage.",
                "Booting with an empty secret because no check ran until the first signed request.",
            ],
            q1=(
                "Why validate configuration at startup instead of on first use?",
                "A missing or weak secret discovered at boot is an immediate, obvious failure; discovered later it becomes a production incident.",
            ),
            homework=(
                "Write `load_config(env)` that enforces required keys and a minimum secret length, plus "
                "`redact(config)` that masks names containing secret, token or password. Run it on two environments, "
                "print both redacted views, and comment which line keeps secrets out of logs."
            ),
            patterns=["load_config", "redact", "raise ValueError"],
            mapping=(
                "Twelve-factor apps read configuration from the environment; production systems add a secret "
                "manager, per-environment credentials and rotation. Managed identity removes long-lived secrets "
                "entirely where the platform supports it."
            ),
        ),
        132: dict(
            topic="Audit logging",
            idea=(
                "An audit log answers who did what, when, to which resource, and whether it succeeded. It is not the "
                "same as application logs: application logs help you debug, while audit records support "
                "investigations, compliance and incident response. Each record should be structured, append-only "
                "and written even when the request fails, because a failed authorisation attempt is exactly what you "
                "want to see. Include an actor identifier, an action, a resource identifier, the outcome, a "
                "correlation or request id, and a trusted timestamp. Do not include passwords, tokens, full request "
                "bodies or unnecessary personal data; an audit log that leaks secrets is a second incident. Protect "
                "the log from the application that writes it: separate storage, restricted read access, and "
                "retention rules that satisfy policy. Make entries tamper-evident with hash chaining if the threat "
                "model requires it. Log decisions, not just successes: “denied because role viewer” is far more "
                "useful than “403”. Today you build a small recorder that emits deterministic JSON lines for a login, "
                "a denied write and a successful read, then print the records and confirm they carry a request id "
                "and no secret. The mapping is SIEM ingestion, cloud audit trails and compliance evidence, all built "
                "from this shape."
            ),
            code=(
                'import json\n'
                '\n'
                'def audit_line(actor, action, outcome, request_id):\n'
                '    record = {\n'
                '        "actor": actor,\n'
                '        "action": action,\n'
                '        "outcome": outcome,\n'
                '        "request_id": request_id,\n'
                '    }\n'
                '    return json.dumps(record, sort_keys=True, separators=(",", ":"))\n'
                '\n'
                'log = []\n'
                'events = [\n'
                '    ("alice", "login", "success", "req-1001"),\n'
                '    ("bob", "book:write", "denied_role_viewer", "req-1002"),\n'
                '    ("alice", "book:read", "success", "req-1003"),\n'
                ']\n'
                'for actor, action, outcome, request_id in events:\n'
                '    line = audit_line(actor, action, outcome, request_id)\n'
                '    log.append(line)\n'
                '    print(line)\n'
                '\n'
                'print("records:", len(log))\n'
                'print("all have request ids:", all(\'"request_id"\' in line for line in log))\n'
                'print("no credential fields:", not any("password" in line or "token" in line for line in log))\n'
                'assert len(log) == 3\n'
                'print("audit entries are structured and minimal")'
            ),
            variant_b='add a failed login for an unknown user and confirm the outcome is still recorded',
            variant_c='add a password field to the record and see the credential check fail',
            mistakes=[
                "Logging only successful actions, so brute-force attempts and denied writes leave no trace.",
                "Putting tokens, passwords or full request bodies into the audit record.",
                "Writing audit data in the same mutable store and with the same permissions as debug logs.",
            ],
            q1=(
                "Why must a denied action still produce an audit record?",
                "Repeated denials are evidence of an attack or a broken permission model; logging only successes hides the pattern.",
            ),
            homework=(
                "Write `audit_line(actor, action, outcome, request_id)` returning deterministic JSON, and run it on "
                "a success, a denial and a failure. Print all three lines, then assert that none contains a password "
                "or token, and comment which field supports investigation."
            ),
            patterns=["json.dumps", "request_id", "outcome"],
            mapping=(
                "Cloud audit trails and SIEM pipelines consume exactly this structured event shape. Hash-chained "
                "logs add tamper evidence, and retention policies decide how long the record survives."
            ),
        ),
        133: dict(
            topic="Abuse and privacy",
            idea=(
                "Abuse and privacy are two sides of the same design question: what should this endpoint reveal, and "
                "to whom, at what rate? Enumeration attacks exploit differences in responses. If login says “no such "
                "user” for one email and “wrong password” for another, an attacker learns which accounts exist; "
                "return one generic error for both. If a lookup endpoint returns full records, it becomes a scraping "
                "API; return only the fields the client needs and cap page sizes. Sequential ids make enumeration "
                "trivial, so use opaque identifiers or accept that ids are public and enforce authorisation on every "
                "read. Collect the minimum personal data you need, keep it only as long as necessary, and give users "
                "a way to see and delete it. Log security events without logging the sensitive payload. Rate limits, "
                "pagination caps and generic errors are not cosmetic: they remove the cheap signals and cheap bulk "
                "access that most automated abuse depends on. Privacy also means not shipping data to analytics or "
                "third parties by default. Today you compare two login responses to show they are identical, strip "
                "email and phone from a public profile, and clamp a requested page size to a maximum. The mapping is "
                "OWASP API Security, GDPR-style minimisation and the defences every public API eventually needs."
            ),
            code=(
                'def login_response(user_exists, password_ok):\n'
                '    if not user_exists or not password_ok:\n'
                '        return 401, {"error": "invalid_credentials"}\n'
                '    return 200, {"token": "issued"}\n'
                '\n'
                'def public_user(user):\n'
                '    return {"id": user["id"], "display_name": user["display_name"]}\n'
                '\n'
                'def page_size(requested, maximum=50):\n'
                '    return max(1, min(requested, maximum))\n'
                '\n'
                'user = {\n'
                '    "id": "usr_8f2c",\n'
                '    "display_name": "A. Reader",\n'
                '    "email": "reader@example.com",\n'
                '    "phone": "+10000000000",\n'
                '}\n'
                'print("unknown user:", login_response(False, False))\n'
                'print("wrong password:", login_response(True, False))\n'
                'print("public profile:", public_user(user))\n'
                'print("requested 5000 -> page size:", page_size(5000))\n'
                'assert login_response(False, False) == login_response(True, False)\n'
                'assert "email" not in public_user(user)\n'
                'print("responses do not confirm accounts or expose contact data")'
            ),
            variant_b='request page size 0 and decide whether clamping to 1 or rejecting with 422 is better',
            variant_c='add a "created_at" field to the public profile and justify whether it belongs there',
            mistakes=[
                "Returning distinct errors for an unknown user and a wrong password, enabling account enumeration.",
                "Exposing the internal user object directly, which leaks email, phone and password hashes.",
                "Accepting an unlimited page size, which turns a list endpoint into a bulk export tool.",
            ],
            q1=(
                "Why should an unknown user and a wrong password return the same login error?",
                "Different messages tell an attacker which accounts exist, turning login into an account-enumeration oracle.",
            ),
            homework=(
                "Write `safe_profile(user)` that returns only id and display_name, and `clamp_limit(n, maximum)` "
                "that bounds pagination. Run both on two inputs each, print the results, and comment which line "
                "removes the enumeration signal."
            ),
            patterns=["invalid_credentials", "public_user", "min("],
            mapping=(
                "OWASP API Security names broken object property level authorisation and unrestricted resource "
                "consumption as top risks. Data minimisation and generic authentication errors are the same "
                "controls described in privacy regulation."
            ),
        ),
        134: dict(
            topic="Review: a defensible API",
            idea=(
                "A defensible API is one you can explain to a reviewer, an auditor and an attacker. The explanation "
                "is a chain of decisions: transport is HTTPS with verified certificates; identity is established by a "
                "token or key that is verified, not merely present; authorisation is checked per action and "
                "resource; input is validated and queries are parameterised; writes are idempotent where duplicates "
                "are harmful; expensive or sensitive endpoints are rate limited; secrets come from the environment; "
                "and security-relevant events are logged without leaking credentials. Each decision fails closed. If "
                "the token verifier errors, deny. If the rate-limit store is unavailable, prefer a conservative "
                "limit over no limit. If the audit write fails, decide explicitly whether the action may proceed. A "
                "defensible API also has negative tests for every one of those controls, because a control nobody "
                "tested is a hope. Today you assemble a small request pipeline that applies the checks in order and "
                "returns 401, 403, 429, 422 or 200 with a reason, then run four requests through it. The order "
                "matters: authenticate before revealing validation detail, limit before doing expensive work, and "
                "never let a failure path skip the audit record. This is the review you should be able to give for "
                "any service you ship."
            ),
            code=(
                'TOKENS = {"Bearer tok-alice": {"subject": "alice", "role": "editor"}}\n'
                'ALLOWED = {"editor": {"read", "write"}}\n'
                '\n'
                'def handle(request, buckets, now):\n'
                '    if request["scheme"] != "https":\n'
                '        return 400, "https_required"\n'
                '    user = TOKENS.get(request["headers"].get("Authorization", ""))\n'
                '    if user is None:\n'
                '        return 401, "unauthenticated"\n'
                '    key = user["subject"]\n'
                '    count = buckets.get(key, 0)\n'
                '    if count >= 2:\n'
                '        return 429, "rate_limited"\n'
                '    buckets[key] = count + 1\n'
                '    if request["action"] not in ALLOWED.get(user["role"], set()):\n'
                '        return 403, "forbidden"\n'
                '    if not request["body"].get("title"):\n'
                '        return 422, "title_required"\n'
                '    return 200, "accepted"\n'
                '\n'
                'buckets = {}\n'
                'base = {"scheme": "https", "headers": {"Authorization": "Bearer tok-alice"}, "action": "write"}\n'
                'requests = [\n'
                '    dict(base, body={"title": "Dune"}),\n'
                '    dict(base, body={"title": ""}),\n'
                '    dict(base, scheme="http", body={"title": "Dune"}),\n'
                '    {"scheme": "https", "headers": {}, "action": "read", "body": {}},\n'
                ']\n'
                'for request in requests:\n'
                '    print(handle(request, buckets, 1000))\n'
                'assert handle(requests[0], buckets, 1000)[0] == 429\n'
                'print("every control fails closed in order")'
            ),
            variant_b='raise the per-user limit to three and confirm the fourth request changes from 429 to 422',
            variant_c='give alice the viewer role and watch the write path return 403 after authentication',
            mistakes=[
                "Checking validation before authentication, which leaks field details to anonymous callers.",
                "Treating a rate-limit store failure as unlimited traffic instead of failing conservatively.",
                "Skipping the audit record on an early return, so denied requests vanish from the log.",
            ],
            q1=(
                "Why should authentication run before detailed input validation?",
                "Unauthenticated callers should not learn which field names, limits or rules the endpoint accepts; identity comes first and opaque errors follow.",
            ),
            homework=(
                "Write `handle(request, buckets, now)` that enforces HTTPS, authentication, a per-user rate limit, "
                "role permission and a required title, returning a specific status for each failure. Run four "
                "requests through it, print every result, and comment which check must come first and why."
            ),
            patterns=["def handle", "return 401", "return 429"],
            mapping=(
                "This is the review behind API gateway policies, OAuth2 scopes, WAF rules and audit trails. The "
                "controls differ by product; the ordering and the fail-closed default do not."
            ),
        ),
    },
)
