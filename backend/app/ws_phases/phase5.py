"""Phase 5: dynamic and authenticated sources, days 135-149.

Every example is stdlib-only and offline. Sessions, tokens, paginated JSON and
rendered HTML are simulated with in-memory strings and dictionaries so the
lesson logic can be exercised without touching a live site.
"""

PHASE = (
    "Dynamic and Authenticated Sites",
    "Recognise JavaScript-built pages and protected sources, then choose between the data API and a browser while respecting access rules.",
    {
        135: dict(
            topic="Why the HTML is empty",
            idea=(
                "View source and the page looks finished: headings, a table container, a price placeholder. The data is not "
                "there. What arrived over the wire was a shell: HTML, CSS, a script tag, and an empty mount point such as a div "
                "with id app. The browser then executed the JavaScript, called one or more APIs, and built the table in memory. "
                "This is why copying the URL into a script that only fetches bytes returns a page that looks broken or empty: "
                "you captured the recipe, not the meal. The distinction matters because every later decision depends on it. If "
                "the values exist in the first response, parse HTML and be done. If they do not, the page is a program, and you "
                "must either run it with browser automation or find the request it makes for data. Diagnosing which case you "
                "face is a two-minute check: fetch or view the raw response, search for a known value such as a product name, "
                "and see whether the bytes contain it. If the value is missing while the rendered page shows it, stop writing "
                "selectors. No amount of CSS selector cleverness can extract text that was never sent. Record the evidence, "
                "because the same site may serve data directly on one route and render it on another."
            ),
            code=(
                'raw = \'<div id="app"></div><script src="/app.js"></script>\'\n'
                'rendered = (\'<div id="app"><table><tr><td>Dune</td>\'\n'
                '            \'<td>9.99</td></tr></table></div>\')\n'
                '\n'
                'def probe(html, needle):\n'
                '    found = needle in html\n'
                '    print("payload:", len(html), "chars | contains", needle + ":", found)\n'
                '    return found\n'
                '\n'
                'print("raw response")\n'
                'probe(raw, "Dune")\n'
                'print("after JavaScript ran")\n'
                'probe(rendered, "9.99")\n'
                'assert not probe(raw, "9.99") and probe(rendered, "Dune")\n'
                'print("diagnosis: fetch the data source, not the shell")'
            ),
            variant_b="a raw shell that contains the price in a JSON script tag rather than in the table",
            variant_c="a no-JavaScript fallback page where the marker is present in the raw bytes",
            mistakes=[
                "Writing CSS selectors for a table that only exists after JavaScript runs.",
                "Concluding the site is down because the raw response has no rows.",
                "Assuming every route of one site behaves the same way.",
            ],
            q1=(
                "What does an empty table container in the raw response prove?",
                "The bytes you fetched contain no row data, so the values must arrive later from a script or API call; selectors cannot recover them.",
            ),
            homework=(
                "Write `missing_in_raw(raw, rendered, marker)` that prints whether the marker appears in each payload and returns "
                "True only when it is absent from raw and present after rendering. Run it on two fixture pairs, print both "
                "verdicts, and comment which line distinguishes a shell from a rendered page."
            ),
            patterns=["def ", "in html", "print("],
            mapping=(
                "In DevTools, compare View Source with the Elements panel; the gap is the rendered data. Playwright and Selenium "
                "exist to close that gap, but first check whether a JSON script tag or Network request already carries the values."
            ),
        ),
        136: dict(
            topic="Find the API behind the page",
            idea=(
                "When a page fetches its own data, the browser's Network panel is the map. Open it, filter to Fetch/XHR, reload, "
                "and watch which request returns the rows you can see. The response is usually JSON, often cleaner than the HTML "
                "because it is designed for a client rather than for people. Before automating a browser, spend five minutes "
                "looking for that request: a URL, a query string with a limit or page parameter, and a JSON body with a stable "
                "shape. Inline configuration is another clue. Many single-page apps embed a state object in a script tag, "
                "including the API base path, a store identifier, or a page size. Extracting that object with string slicing and "
                "parsing it with the json module gives you the endpoint and its parameters without running any JavaScript. The "
                "payoff is large: JSON endpoints are faster, cheaper, and far more stable than pixel-level clicking, and their "
                "fields keep their names when the visual design changes. Treat the discovery as evidence, not a licence. Note "
                "the request method, required headers, authentication, and paging behaviour, then confirm that the endpoint "
                "returns the same records the page displays. If the JSON is public and permitted, parse it; if it needs a "
                "session, capture that session properly in the next lessons rather than guessing."
            ),
            code=(
                'import json\n'
                'from urllib.parse import urlencode\n'
                '\n'
                'page = (\'<script>window.__STATE__ = \'\n'
                '        \'{"api":"/api/v2/books","pageSize":2,"store":"west"}</script>\')\n'
                'state = json.loads(page.split("window.__STATE__ = ", 1)[1].split("</script>")[0])\n'
                'print("endpoint:", state["api"])\n'
                'params = {"store": state["store"], "limit": state["pageSize"]}\n'
                'url = state["api"] + "?" + urlencode(params)\n'
                'print("request:", url)\n'
                'print("parameter names:", sorted(params))\n'
                'assert "limit=2" in url and state["store"] == "west"\n'
                'print("found the data endpoint without a browser")'
            ),
            variant_b="inline state with api /api/v1/orders, pageSize 50 and region north",
            variant_c="a state object that stores the API path under the key dataUrl instead of api",
            mistakes=[
                "Automating clicks before checking whether an XHR already returns the same rows.",
                "Copying the endpoint but dropping required query parameters such as store or limit.",
                "Hard-coding a signed or expiring URL instead of reading how it is built.",
            ],
            q1=(
                "Why inspect Fetch/XHR requests before building a browser script?",
                "If a request already returns the visible data as JSON, parsing it is faster and more stable than driving the interface.",
            ),
            homework=(
                "Write `api_from_state(page)` that extracts the embedded state object, builds a URL with urlencode, and prints the "
                "endpoint plus parameter names. Run it on two different state objects, print both URLs, and comment which line "
                "turns configuration into a request."
            ),
            patterns=["json.loads(", "urlencode(", "print("],
            mapping=(
                "The DevTools Network panel, filtered to Fetch/XHR, is the standard discovery tool. Playwright's request "
                "interception and Selenium's performance logs expose the same traffic when the page only loads after interaction."
            ),
        ),
        137: dict(
            topic="Browser automation concepts",
            idea=(
                "A browser automation tool is not a smarter HTTP client. It starts a real browser process, gives you a remote "
                "control channel, and lets you act on the live document: navigate, find an element, click, type, read text, and "
                "wait. The unit you manipulate is the DOM after scripts have run, not the source text the server sent. That is "
                "the whole value and the whole cost. Every action has a state precondition. You cannot click a button that is "
                "not yet attached, not visible, or covered by a cookie banner, and you cannot read a cell before its row has "
                "been rendered. Good automation therefore thinks in terms of locators, actions, and expected states rather than "
                "fixed sleeps. A locator should describe the element the way a careful tester would: by role and accessible "
                "name first, then by stable attributes, and only last by brittle structural position. The browser also holds "
                "state across steps: cookies, local storage, and the current page. That is what makes login flows possible, and "
                "also what makes tests order-dependent when you forget to reset it. Keep the control layer thin. Your scraper "
                "should still receive plain records, so the parsing and validation code remains testable without launching a "
                "browser at all."
            ),
            code=(
                'class Browser:\n'
                '    def __init__(self):\n'
                '        self.dom = {"#load": "Load", "#status": ""}\n'
                '        self.clicks = 0\n'
                '\n'
                '    def click(self, selector):\n'
                '        self.clicks += 1\n'
                '        if selector == "#load":\n'
                '            self.dom["#status"] = "3 rows" if self.clicks == 1 else "3 rows (cached)"\n'
                '\n'
                '    def text(self, selector):\n'
                '        return self.dom.get(selector, "")\n'
                '\n'
                'browser = Browser()\n'
                'print("before:", repr(browser.text("#status")))\n'
                'browser.click("#load")\n'
                'print("after click:", browser.text("#status"))\n'
                'print("actions taken:", browser.clicks)\n'
                'assert browser.text("#status") == "3 rows"\n'
                'print("state lives in the browser, not in the source")'
            ),
            variant_b="click the load button twice and read whether the status changes",
            variant_c="request a selector that does not exist and decide whether to return empty text or raise",
            mistakes=[
                "Treating the browser as an HTTP client and expecting the first DOM read to contain data.",
                "Sleeping instead of waiting for a concrete state such as visible text or a row count.",
                "Letting browser state leak between runs, so the second run starts logged in or on the wrong page.",
            ],
            q1=(
                "What state does a browser hold that a plain fetch does not?",
                "The live DOM after scripts, plus cookies, storage and navigation history; that state is what login flows and rendered reads depend on.",
            ),
            homework=(
                "Write a tiny `FakeBrowser` class with `click(selector)` and `text(selector)` methods that change an in-memory DOM. "
                "Drive it through two action sequences, print the text after each, and comment which line proves the data came "
                "from browser state rather than the initial source."
            ),
            patterns=["class ", "def ", "print("],
            mapping=(
                "Playwright and Selenium provide this process, locator and action model in real browsers. Keep the same thin "
                "boundary: automation fetches and acts, your parser turns the resulting text into records."
            ),
        ),
        138: dict(
            topic="Waiting for content",
            idea=(
                "Dynamic pages race your scraper. The document may be ready while the table is still a skeleton, and a fixed "
                "sleep is a bet that the network, the server, and the client script all finish within an arbitrary number of "
                "seconds. On a fast day the bet wastes time; on a slow day it loses, and your parser sees an empty container "
                "that is indistinguishable from a changed layout. The robust pattern is an explicit wait: poll a concrete "
                "condition until it becomes true or a deadline expires, then fail with the condition named. The condition "
                "should be something the data itself guarantees, such as a row with a known class, a status cell containing "
                "text, or a spinner disappearing. Waiting for the whole page load event is usually too early because data "
                "requests continue afterwards. Two details separate a reliable wait from a hopeful one. First, poll at a "
                "sensible interval and measure elapsed time, so the timeout is real rather than a loop count that changes "
                "meaning when the machine is loaded. Second, report what was expected and what was seen when the deadline "
                "passes; an empty table and a login redirect require different fixes. Waits belong in one helper that every "
                "read uses, not scattered through the parser. That helper is also where you add a screenshot or DOM dump on "
                "failure, turning an intermittent scrape into evidence you can inspect later."
            ),
            code=(
                'import time\n'
                '\n'
                'class Clock:\n'
                '    def __init__(self):\n'
                '        self.now = 0.0\n'
                '    def sleep(self, seconds):\n'
                '        self.now += seconds\n'
                '\n'
                'def wait_for(clock, read, ready, timeout=5.0, interval=0.5):\n'
                '    deadline = clock.now + timeout\n'
                '    while clock.now < deadline:\n'
                '        value = read()\n'
                '        print("at", round(clock.now, 1), "s saw", repr(value))\n'
                '        if ready(value):\n'
                '            return value\n'
                '        clock.sleep(interval)\n'
                '    raise TimeoutError("condition not met before deadline: " + repr(read()))\n'
                '\n'
                'clock = Clock()\n'
                'frames = iter(["", "", "3 rows", "3 rows"])\n'
                'result = wait_for(clock, lambda: next(frames), lambda v: "rows" in v)\n'
                'print("ready after", round(clock.now, 1), "s:", result)\n'
                'assert result == "3 rows" and clock.now <= 5.0\n'
                'print("wait ended on the data, not on a guess")'
            ),
            variant_b="a payload that becomes ready on the first poll (how much time was wasted?)",
            variant_c="a payload that never becomes ready (watch the timeout message and deadline)",
            mistakes=[
                "Using sleep(5) as a substitute for checking whether the data exists.",
                "Waiting for page load instead of for the specific element that holds rows.",
                "Polling forever with no deadline, so a broken page hangs the whole run.",
            ],
            q1=(
                "Why is polling for a concrete condition better than a fixed sleep?",
                "It proceeds as soon as the data is ready and fails with a named condition when it is not, instead of guessing a duration.",
            ),
            homework=(
                "Write `wait_for(clock, read, ready, timeout)` that polls a fake clock, prints each observation, and raises "
                "TimeoutError at the deadline. Run it on a reader that succeeds on the third poll and one that never succeeds, "
                "print both, and comment which line enforces the deadline."
            ),
            patterns=["def ", "while ", "print("],
            mapping=(
                "Playwright has `expect(locator).to_be_visible()` and `wait_for_selector`; Selenium has WebDriverWait with "
                "expected conditions. Both are the same poll-until-ready loop with a timeout."
            ),
        ),
        139: dict(
            topic="User agents and request headers",
            idea=(
                "Every HTTP request carries headers that describe the client, what it accepts, and where it came from. The "
                "User-Agent names the software; Accept says which media types are welcome; Accept-Language asks for a language; "
                "Referer says which page linked here; and a few caching or encoding headers shape the response. Scrapers care "
                "because servers use these values for routing, content negotiation, and access decisions. The same URL can "
                "return a different layout, currency, or even a block page depending on what you send. A missing or generic "
                "User-Agent is a common reason an otherwise correct request is refused. The lazy fix is not to impersonate a "
                "browser in order to evade controls; it is to identify your client honestly and send only the headers the "
                "endpoint needs. Some APIs want an explicit Accept: application/json. Some sites vary by Accept-Language, so "
                "asking for the wrong language makes your parser look broken. A Referer may be required for a form or a "
                "download. Build a request description as data, inspect it before sending, and keep it identical between runs "
                "so a change in output can be traced to the site rather than to drifting headers. If a policy restricts "
                "automated clients, changing the header string to hide is a policy problem, not a technical one."
            ),
            code=(
                'base = {"Accept": "application/json", "Accept-Language": "en"}\n'
                '\n'
                'def build_headers(role, referer=None):\n'
                '    headers = dict(base)\n'
                '    headers["User-Agent"] = "SchoolResearchBot/1.0 (" + role + ")"\n'
                '    if referer:\n'
                '        headers["Referer"] = referer\n'
                '    return headers\n'
                '\n'
                'def respond(headers):\n'
                '    if "User-Agent" not in headers:\n'
                '        return 403, "identify your client"\n'
                '    if headers.get("Accept-Language") != "en":\n'
                '        return 200, "contenu francais"\n'
                '    return 200, "english content"\n'
                '\n'
                'good = build_headers("catalog", "https://shop.example/books")\n'
                'print("headers:", good)\n'
                'print("response:", respond(good))\n'
                'print("anonymous:", respond({}))\n'
                'assert respond(good)[0] == 200\n'
                'print("headers are part of the request contract")'
            ),
            variant_b="Accept-Language 'fr' and observe which body the simulated server returns",
            variant_c="remove the User-Agent entirely and route the 403 to a policy decision, not a retry",
            mistakes=[
                "Sending a browser User-Agent to disguise a bot instead of following the site's policy.",
                "Dropping Accept-Language and then blaming the parser for a translated layout.",
                "Building headers in several places so two requests to one endpoint disagree.",
            ],
            q1=(
                "Why can the same URL return different content to two clients?",
                "Servers negotiate on headers such as Accept, Accept-Language and User-Agent, and may also block clients they do not recognise.",
            ),
            homework=(
                "Write `build_headers(role, referer)` that returns a complete header dictionary and `respond(headers)` that "
                "returns a status and body based on its contents. Run both on two header sets, print the responses, and comment "
                "which header causes the refusal."
            ),
            patterns=["def ", "headers", "print("],
            mapping=(
                "DevTools shows the exact request headers and lets you copy them as a starting point. Session libraries keep "
                "them consistent; Playwright and Selenium send whatever the browser sends, which is not automatically desirable."
            ),
        ),
        140: dict(
            topic="Cookies and login sessions",
            idea=(
                "HTTP forgets. A login is the server's way of remembering you anyway. You send credentials to a login endpoint, "
                "the server answers with a Set-Cookie header, and the browser stores that cookie and sends it on later requests. "
                "The cookie is usually a session identifier, not your password; losing it logs you out, and sharing it hands "
                "someone your account. A scraper therefore needs a cookie store that behaves like a browser's: capture cookies "
                "from responses, respect domain and path rules, and attach them to every request that targets the same site. "
                "The naive version keeps one dictionary of name to value, which works until the site sets two cookies with the "
                "same name on different paths, or expires one at logout. Expiry matters: a long crawl can outlive a session, "
                "and the first symptom is a redirect to the login page in the middle of your data. That redirect must be "
                "detected and handled explicitly, never parsed as if it were a table. Security hygiene is part of the lesson. "
                "Credentials belong in environment variables or a local secret store, never in source or logs. Print cookie "
                "names, not values, when debugging. A session captured from your own account is not permission to scrape other "
                "people's data, and automated login may itself be restricted by the site's terms."
            ),
            code=(
                'class Session:\n'
                '    def __init__(self):\n'
                '        self.cookies = {}\n'
                '        self.user = None\n'
                '\n'
                '    def login(self, user, password):\n'
                '        if password != "correct-horse":\n'
                '            return 401, {}\n'
                '        self.user = user\n'
                '        return 200, {"Set-Cookie": "sid=abc123; Path=/; HttpOnly"}\n'
                '\n'
                '    def store(self, headers):\n'
                '        raw = headers.get("Set-Cookie", "")\n'
                '        if raw:\n'
                '            name, value = raw.split(";")[0].split("=", 1)\n'
                '            self.cookies[name] = value\n'
                '\n'
                '    def request(self, path):\n'
                '        if "sid" not in self.cookies:\n'
                '            return 302, "/login"\n'
                '        return 200, "data for " + path + " as " + str(self.user)\n'
                '\n'
                's = Session()\n'
                'status, headers = s.login("student", "correct-horse")\n'
                's.store(headers)\n'
                'print("cookie names:", sorted(s.cookies))\n'
                'print("orders:", s.request("/orders"))\n'
                'assert s.request("/orders")[0] == 200\n'
                'print("session established and reused")'
            ),
            variant_b="log in with the wrong password and follow what the later request returns",
            variant_c="clear the cookie jar before the second request and classify the redirect",
            mistakes=[
                "Putting credentials in the script and committing them to version control.",
                "Sending cookies to every domain instead of matching domain and path.",
                "Treating a login redirect as a parse failure instead of an expired session.",
            ],
            q1=(
                "What does the Set-Cookie header actually give the scraper?",
                "A session identifier to store and send on later requests; it represents the logged-in state without repeating the password.",
            ),
            homework=(
                "Write `Session` with `login`, `store` and `request` methods that keep a cookie dictionary and return 302 when "
                "the session is missing. Run a successful and an unauthenticated case, print both results, and comment which line "
                "attaches the stored session to later work."
            ),
            patterns=["class ", "cookies", "print("],
            mapping=(
                "Requests' `Session` and `http.cookiejar` handle this automatically; Playwright keeps a browser context with "
                "cookies and storage. Always detect the login redirect explicitly during long authenticated runs."
            ),
        ),
        141: dict(
            topic="Tokens and CSRF",
            idea=(
                "Cookies alone are not enough for state-changing requests. If a browser automatically attaches a session cookie, "
                "another site can trick it into submitting a form on your behalf, which is cross-site request forgery. The "
                "standard defence is a token: the server embeds a random value in the form, also binds it to your session or a "
                "cookie, and rejects any submission that does not echo it. For a scraper this means a POST is a two-step "
                "conversation. First fetch the form, parse the hidden input, and keep the token alongside the cookies from the "
                "same response. Then submit the data with that token, and expect it to be single-use or time-limited. Reusing a "
                "token from an old page is one of the most common causes of a mysterious 403 on an otherwise correct request. "
                "Modern APIs use a related idea with a different name: a bearer token or an API key in a header. The mechanics "
                "differ, but the discipline is identical. Never invent the value, never hard-code one captured yesterday, and "
                "never log it. Read where the page or the auth response puts it, refresh it when it expires, and keep the "
                "token tied to the session that requested it. A token is a capability, so treat it like a password."
            ),
            code=(
                'def issue_form(session_id):\n'
                '    token = "a1b2c3d4"  # fixed fixture; a real server generates this\n'
                '    return {"token": token, "session": session_id, "form": \'<input name="csrf" value="\' + token + \'">\'}\n'
                '\n'
                'def submit(form_page, session_id, token, used):\n'
                '    if token in used:\n'
                '        return 403, "token already used"\n'
                '    if token not in form_page or session_id != "s-42":\n'
                '        return 403, "token does not match session"\n'
                '    used.add(token)\n'
                '    return 200, "saved"\n'
                '\n'
                'issued = issue_form("s-42")\n'
                'seen = set()\n'
                'print("form:", issued["form"])\n'
                'print("first submit:", submit(issued["form"], "s-42", issued["token"], seen))\n'
                'print("replay:", submit(issued["form"], "s-42", issued["token"], seen))\n'
                'print("wrong session:", submit(issued["form"], "s-99", issued["token"], set()))\n'
                'assert submit(issued["form"], "s-42", issued["token"], set())[0] == 200\n'
                'print("tokens are fetched, bound and single-use")'
            ),
            variant_b="generate a fresh token for each form and submit it once with the matching session",
            variant_c="reuse the token after a simulated five-minute expiry and read the rejection",
            mistakes=[
                "Submitting a POST without first fetching the form that carries the token.",
                "Reusing one token across several submissions or several sessions.",
                "Logging the token value while debugging authentication failures.",
            ],
            q1=(
                "Why must the token be fetched with the form rather than invented?",
                "The server binds it to the session and expects the exact issued value; a made-up token fails the check even when the cookies are valid.",
            ),
            homework=(
                "Write `issue_form(session_id)` and `submit(form_page, session_id, token, used)` that enforce a session match and "
                "single use. Run a valid submission and a replayed one, print both responses, and comment which line prevents the "
                "second use."
            ),
            patterns=["def ", "token", "print("],
            mapping=(
                "DevTools shows the hidden csrf input and the matching cookie; requests needs the token parsed and posted back. "
                "API clients instead carry a bearer token in the Authorization header, refreshed on expiry."
            ),
        ),
        142: dict(
            topic="Authenticated API pagination",
            idea=(
                "An authenticated endpoint rarely returns everything at once. It returns a page and a way to ask for the next one. "
                "Two schemes dominate: page numbers with a total count, and cursors where the response includes an opaque "
                "next value and null or absent means stop. Cursors are safer for changing datasets because they point at a "
                "position rather than an offset that shifts when rows are inserted. The loop must therefore follow the signal "
                "the API gives, not a guessed number of pages. Stop when the cursor is empty, when an empty item list arrives, "
                "or when you see a cursor you have already consumed; that last guard prevents an infinite loop caused by a "
                "buggy or ignored parameter. Authentication adds two failure modes. The token may expire mid-crawl, producing "
                "a 401 that should trigger a refresh and a retry of the same page, not a silent end. A page may return fewer "
                "items than the requested limit while still having more data, so do not infer completion from a short page "
                "unless the documentation says so. Deduplicate by a stable identifier as you go: retries and overlapping "
                "cursors can repeat records, and a count inflated by duplicates is worse than a small one. Finally, log pages, "
                "items, retries and the stop reason. That log is the difference between a defensible dataset and a number "
                "nobody can explain."
            ),
            code=(
                'pages = {\n'
                '    None: {"items": [{"id": 1}, {"id": 2}], "next": "c1"},\n'
                '    "c1": {"items": [{"id": 3}], "next": "c2"},\n'
                '    "c2": {"items": [{"id": 4}, {"id": 5}], "next": None},\n'
                '}\n'
                '\n'
                'def crawl(token, pages):\n'
                '    cursor, seen_ids, seen_cursors, order = None, set(), set(), []\n'
                '    while True:\n'
                '        if token != "live":\n'
                '            raise PermissionError("token expired")\n'
                '        if cursor in seen_cursors:\n'
                '            raise RuntimeError("cursor loop at " + repr(cursor))\n'
                '        seen_cursors.add(cursor)\n'
                '        page = pages[cursor]\n'
                '        for item in page["items"]:\n'
                '            if item["id"] not in seen_ids:\n'
                '                seen_ids.add(item["id"])\n'
                '                order.append(item["id"])\n'
                '        print("cursor", cursor, "-> items", len(page["items"]), "next", page["next"])\n'
                '        cursor = page["next"]\n'
                '        if cursor is None:\n'
                '            break\n'
                '    return order\n'
                '\n'
                'ids = crawl("live", pages)\n'
                'print("unique ids:", ids)\n'
                'assert ids == [1, 2, 3, 4, 5]\n'
                'print("stopped on the API end signal")'
            ),
            variant_b="a page that repeats id 3 and verify deduplication keeps the count correct",
            variant_c="a cursor chain c1 -> c2 -> c1 and watch the loop guard fire",
            mistakes=[
                "Assuming a short page means the end when the cursor is still non-null.",
                "Restarting from page one after a token refresh and duplicating every record.",
                "Following a cursor without a visited set, so a server bug loops forever.",
            ],
            q1=(
                "What is the authoritative signal that an authenticated crawl is finished?",
                "The API's own end condition, such as a null cursor or empty item list, not a guessed page count or a short page.",
            ),
            homework=(
                "Write `crawl(token, pages)` that follows a next cursor, deduplicates by id, guards against repeated cursors, and "
                "prints each page. Run it on a normal chain and a looping chain, print the results, and comment which line stops "
                "the normal case."
            ),
            patterns=["while ", "next", "print("],
            mapping=(
                "Most JSON APIs return `next_cursor` or a `next` link; Requests users loop on that field and refresh OAuth "
                "tokens on 401. The same loop works in a browser context when the page's own client calls the API."
            ),
        ),
        143: dict(
            topic="Reading JavaScript-rendered tables",
            idea=(
                "Once a table has been rendered, it is ordinary HTML again, but it carries the fingerprints of a UI framework: "
                "wrapper divs, spans around values, data attributes, and rows that are not siblings where you expect. The "
                "lesson is to parse the rendered document by meaning rather than by depth. Locate the table, read the header "
                "row to establish column order, then map each body row's cells to those names. That header-driven mapping is "
                "what keeps the parser alive when the site adds a column; a positional index quietly returns the wrong field "
                "while the row count still looks healthy. Values may need cleanup: a currency symbol inside a span, a "
                "non-breaking space, a badge word such as sale, or a dash for missing data. Normalise per field, and decide "
                "explicitly whether a missing value becomes None or causes the row to be rejected. Row counts and column "
                "counts are your first quality check: a row with fewer cells than the header is a parse bug or a legitimately "
                "merged cell, and both deserve a decision rather than an index error. Keep the parser pure: it receives HTML "
                "text and returns dictionaries, with no browser or network call inside. That makes it testable against saved "
                "rendered fixtures, which is the only reliable way to notice a markup change before it corrupts a whole run. "
                "When the structure is genuinely irregular, prefer a small explicit map of column names over a clever "
                "generic table library."
            ),
            code=(
                'from html.parser import HTMLParser\n'
                '\n'
                'html = (\'<table><thead><tr><th>Title</th><th>Price</th></tr></thead>\'\n'
                '        \'<tbody><tr><td><span>Dune</span></td><td>$9.99</td></tr>\'\n'
                '        \'<tr><td>Foundation</td><td>$12.50</td></tr></tbody></table>\')\n'
                '\n'
                'class Table(HTMLParser):\n'
                '    def __init__(self):\n'
                '        super().__init__()\n'
                '        self.cell, self.row, self.rows, self.header = "", [], [], []\n'
                '    def handle_starttag(self, tag, attrs):\n'
                '        if tag in ("td", "th"):\n'
                '            self.cell = ""\n'
                '        if tag == "tr":\n'
                '            self.row = []\n'
                '    def handle_data(self, data):\n'
                '        self.cell += data\n'
                '    def handle_endtag(self, tag):\n'
                '        if tag in ("td", "th"):\n'
                '            self.row.append(self.cell.strip())\n'
                '        if tag == "tr" and self.row:\n'
                '            if not self.header:\n'
                '                self.header = self.row\n'
                '            else:\n'
                '                self.rows.append(dict(zip(self.header, self.row)))\n'
                '\n'
                't = Table()\n'
                't.feed(html)\n'
                'print("header:", t.header)\n'
                'for row in t.rows:\n'
                '    row["Price"] = float(row["Price"].replace("$", ""))\n'
                '    print(row)\n'
                'assert t.rows[1]["Title"] == "Foundation" and t.rows[1]["Price"] == 12.5\n'
                'print("columns mapped by header, not by position")'
            ),
            variant_b="a third column called Stock is added between Title and Price",
            variant_c="one body row has a colspan cell rather than two cells",
            mistakes=[
                "Indexing cells by position after the site inserts a new column.",
                "Parsing the raw response instead of the rendered DOM when the table is client-built.",
                "Letting a stray badge or currency symbol reach storage as part of a numeric field.",
            ],
            q1=(
                "Why map cells by header name instead of by numeric index?",
                "A new or reordered column changes indices silently but leaves the header names correct, so name-based mapping keeps fields aligned.",
            ),
            homework=(
                "Write `parse_table(html)` that feeds a rendered table into HTMLParser, reads the header row, and returns rows as "
                "dictionaries with prices converted to floats. Run it on two rendered fixtures, print both row lists, and comment "
                "which line makes the mapping independent of column order."
            ),
            patterns=["HTMLParser", "dict(zip(", "print("],
            mapping=(
                "After Playwright or Selenium renders the page, `page.content()` or `driver.page_source` gives this HTML. Parse "
                "the saved rendered fixture offline first; browser time is expensive and hard to reproduce."
            ),
        ),
        144: dict(
            topic="Capturing network responses",
            idea=(
                "The most useful artifact from a dynamic session is not a screenshot; it is the set of responses the page "
                "received while rendering. Capture them deliberately. Record the request URL and method, the status, the "
                "content type, and the body, then filter to the handful that carry data rather than fonts and analytics. A "
                "capture turns a one-off browser visit into a replayable fixture: you can write and test the parser offline, "
                "compare today's shape with last week's, and prove which request produced which record. The discipline is to "
                "capture before parsing. If you click through the page and only print the final table, you have lost the "
                "evidence of how it was built and will repeat the slow path next time. Save bodies exactly as received, "
                "including headers that identify the request, and keep a small manifest describing the scenario. Do not stuff "
                "large captures into source control without a retention plan; personal data and tokens may be present, so "
                "redact before sharing and delete when the fixture has served its purpose. A captured response is also a "
                "contract test: if the JSON still parses and the expected keys exist, a parser failure is your bug; if the "
                "keys moved, the source changed. That distinction saves hours of guessing during an outage."
            ),
            code=(
                'import json\n'
                'from urllib.parse import urlsplit\n'
                '\n'
                'capture = [\n'
                '    {"url": "https://shop.example/app.js", "type": "script", "status": 200, "body": "..."},\n'
                '    {"url": "https://shop.example/api/books?page=1", "type": "xhr", "status": 200,\n'
                '     "body": \'{"items":[{"id":7,"title":"Dune"}]}\'},\n'
                '    {"url": "https://shop.example/api/books?page=2", "type": "fetch", "status": 200,\n'
                '     "body": \'{"items":[]}\'},\n'
                ']\n'
                '\n'
                'def data_responses(capture):\n'
                '    found = []\n'
                '    for entry in capture:\n'
                '        if entry["type"] not in ("xhr", "fetch") or entry["status"] != 200:\n'
                '            continue\n'
                '        try:\n'
                '            payload = json.loads(entry["body"])\n'
                '        except json.JSONDecodeError:\n'
                '            continue\n'
                '        path = urlsplit(entry["url"]).path\n'
                '        found.append({"path": path, "items": payload.get("items", [])})\n'
                '    return found\n'
                '\n'
                'for hit in data_responses(capture):\n'
                '    print(hit["path"], "->", len(hit["items"]), "items")\n'
                'total = sum(len(h["items"]) for h in data_responses(capture))\n'
                'print("total records captured:", total)\n'
                'assert total == 1\n'
                'print("filtered the data traffic and kept it replayable")'
            ),
            variant_b="a capture where the data response uses type document instead of xhr",
            variant_c="a response with status 200 but an HTML challenge body that fails JSON parsing",
            mistakes=[
                "Saving every response, including images and analytics, until the capture is unusable.",
                "Capturing the final table instead of the underlying data response.",
                "Committing captured cookies or tokens to a shared fixture directory.",
            ],
            q1=(
                "Why capture the raw network body instead of only the rendered table?",
                "The raw body can be replayed and diffed offline, shows the real data contract, and preserves evidence when the parser breaks.",
            ),
            homework=(
                "Write `data_responses(capture)` that keeps successful XHR or fetch entries, parses their JSON, and returns path "
                "and item counts. Run it on two capture lists, print both summaries, and comment which line separates data "
                "traffic from assets."
            ),
            patterns=["json.loads(", "for ", "print("],
            mapping=(
                "DevTools can save a HAR file; Playwright's `page.on('response')` and Selenium's performance logs let you record "
                "the same bodies programmatically. Redact cookies and personal data before archiving."
            ),
        ),
        145: dict(
            topic="Terms, privacy and permission",
            idea=(
                "Technical access is not the same as permission. Before scraping a source, read the terms that apply to it, "
                "check the robots rules for the paths you intend to use, and decide whether the data is personal or merely "
                "public content. These are separate questions. A page can be visible to your browser and still be off-limits "
                "to automated collection under its terms; robots.txt can allow a path while the terms forbid the use you have "
                "in mind. The practical discipline is to write the decision down before writing the loop: who owns the data, "
                "what you will collect, why you need each field, how long you will keep it, and who can see it. Data "
                "minimisation is not a bureaucratic ritual. If your analysis needs a title and a price, do not store email "
                "addresses found in the same table. Redact or hash identifiers that are not necessary, restrict access to the "
                "raw layer, and set a deletion date for anything you do not need indefinitely. Also check the collection's "
                "rate and scope: a permission for a catalogue is not permission to mirror a whole platform. When the terms "
                "are silent or ambiguous, ask the operator rather than assuming silence means yes. A short written request "
                "often produces a documented allowance, and it protects you when someone later asks why your traffic looked "
                "the way it did."
            ),
            code=(
                'from urllib.robotparser import RobotFileParser\n'
                '\n'
                'rules = RobotFileParser()\n'
                'rules.parse([\n'
                '    "User-agent: *",\n'
                '    "Disallow: /account",\n'
                '    "Allow: /books",\n'
                '    "Crawl-delay: 2",\n'
                '])\n'
                '\n'
                'fields = ["title", "price", "seller_email"]\n'
                'needed = {"title", "price"}\n'
                'kept = [f for f in fields if f in needed]\n'
                '\n'
                'for path in ["/books/1", "/account/settings"]:\n'
                '    print(path, "robots allows:", rules.can_fetch("BookBot", path))\n'
                'print("collected fields:", kept)\n'
                'print("dropped fields:", sorted(set(fields) - set(kept)))\n'
                'assert not rules.can_fetch("BookBot", "/account/settings")\n'
                'assert "seller_email" not in kept\n'
                'print("scope and minimisation decided before collection")'
            ),
            variant_b="a robots file that disallows /books/search but allows /books/detail",
            variant_c="a field list where the only needed values are an id and a public title",
            mistakes=[
                "Treating a successful HTTP 200 as permission to collect and reuse the data.",
                "Keeping every scraped column because deleting fields feels like losing information.",
                "Assuming robots.txt settles the terms of service question by itself.",
            ],
            q1=(
                "Why is robots.txt not the whole permission decision?",
                "It states crawler access preferences, while terms, privacy law and the purpose of collection can impose stricter limits that robots does not cover.",
            ),
            homework=(
                "Write `plan_collection(fields, needed, paths, rules)` that filters fields to the minimum, checks each path "
                "with `can_fetch`, and returns a printed decision. Run it on two different field and path sets, print both, "
                "and comment which line enforces data minimisation."
            ),
            patterns=["can_fetch(", "for ", "print("],
            mapping=(
                "Check robots.txt and the site's terms before scheduling a crawler, and log the decision with the date. "
                "In real projects this note is reviewed alongside the code, not after a complaint arrives."
            ),
        ),
        146: dict(
            topic="Anti-bot realities and ethics",
            idea=(
                "Sites defend themselves for reasons that deserve respect: bandwidth costs, scraping that bypasses paid access, "
                "credential stuffing, and privacy. The defences are recognisable. A 403 with a challenge page, a CAPTCHA, a "
                "JavaScript check that sets a cookie, a sudden redirect to a verification route, or a sharp change in response "
                "time all say the same thing: this client is not welcome as configured. The ethical response is to stop, "
                "diagnose, and change the request to comply, not to escalate until the block disappears. Rotating proxies, "
                "spoofing fingerprints and solving challenges to evade a stated control turn a technical exercise into "
                "circumvention. It is also poor engineering. Defences change constantly, so evasion code has a short life and "
                "leaves you maintaining a cat-and-mouse game with no stable contract. The durable alternatives are unglamorous: "
                "use an official API, request permission, reduce volume, slow down, use a documented export, or pay for access. "
                "When a block appears mid-run, record the URL, status, timestamp and a small body sample, then halt that "
                "segment rather than hammering. Distinguish a temporary rate limit from a deliberate refusal: a 429 with "
                "Retry-After invites patience, while a persistent 403 with a challenge invites a conversation. A scraper that "
                "knows when to stop is more valuable than one that never does."
            ),
            code=(
                'responses = [\n'
                '    {"status": 200, "body": "catalog rows"},\n'
                '    {"status": 429, "body": "slow down", "retry_after": 30},\n'
                '    {"status": 403, "body": "verify you are human: captcha"},\n'
                '    {"status": 200, "body": "enable javascript and cookies to continue"},\n'
                ']\n'
                '\n'
                'def decide(response):\n'
                '    body = response["body"].lower()\n'
                '    if response["status"] == 429:\n'
                '        return "wait " + str(response.get("retry_after", 60)) + "s then resume"\n'
                '    if "captcha" in body or "verify you are human" in body:\n'
                '        return "stop: access control, seek permission"\n'
                '    if response["status"] == 403:\n'
                '        return "stop: refused, do not evade"\n'
                '    if "enable javascript" in body and "rows" not in body:\n'
                '        return "stop: challenge page, not data"\n'
                '    return "store"\n'
                '\n'
                'for response in responses:\n'
                '    print(response["status"], "->", decide(response))\n'
                'assert decide(responses[2]).startswith("stop")\n'
                'assert decide(responses[1]).startswith("wait")\n'
                'print("blocked is a decision, not an obstacle to defeat")'
            ),
            variant_b="a 403 whose body is an ordinary permission error rather than a challenge",
            variant_c="a 200 response that contains a CAPTCHA marker alongside no data rows",
            mistakes=[
                "Rotating proxies or user agents to get past a deliberate refusal.",
                "Retrying a CAPTCHA page as if it were a transient server error.",
                "Ignoring a 429 and increasing concurrency to finish the crawl faster.",
            ],
            q1=(
                "What is the difference between a 429 and a persistent 403 challenge?",
                "A 429 asks you to slow down and retry later; a persistent 403 challenge is a refusal that calls for permission, not evasion.",
            ),
            homework=(
                "Write `decide(response)` that returns store, wait, or stop for success, rate limiting, CAPTCHA and JavaScript "
                "challenge responses. Run it on two response lists, print every decision, and comment which line distinguishes "
                "patience from a refusal."
            ),
            patterns=["def ", "in body", "print("],
            mapping=(
                "Playwright and Selenium can detect a challenge page but should not be used to defeat it. Record the evidence, "
                "pause the job, and move to an official API or a permission request."
            ),
        ),
        147: dict(
            topic="Rate limiting authenticated requests",
            idea=(
                "Authentication changes the cost of going too fast. An anonymous crawler that trips a limit may be blocked; an "
                "authenticated one can exhaust a per-account quota, disrupt a real user, or trigger a security response against "
                "the account whose credentials you are using. Rate limiting is therefore part of correctness, not politeness. "
                "The simplest useful model is a token bucket: capacity sets the burst, refill rate sets the sustained pace, and "
                "each request consumes one token. A token bucket lets a short burst through while enforcing an average, which "
                "matches how many APIs meter traffic. Spacing requests evenly is an alternative and is easier to reason about "
                "for small jobs. Either way the clock must be explicit and testable, not hidden in sleep calls scattered through "
                "the code, so you can simulate a long crawl in milliseconds. Honour Retry-After when the server sends it, and "
                "treat it as a floor, not a suggestion. Keep concurrency low and per-account; two workers sharing one quota are "
                "twice as likely to collide. Log waits, retries and remaining budget so a slow run is explainable. Also "
                "separate read endpoints from write endpoints: a login POST or a state-changing action deserves a stricter "
                "limit than listing records. The aim is to finish without being the reason the service had a bad afternoon, "
                "and to leave enough quota for the next legitimate run."
            ),
            code=(
                'class Bucket:\n'
                '    def __init__(self, capacity, refill_per_second):\n'
                '        self.capacity = capacity\n'
                '        self.tokens = float(capacity)\n'
                '        self.rate = refill_per_second\n'
                '        self.now = 0.0\n'
                '\n'
                '    def advance(self, seconds):\n'
                '        self.now += seconds\n'
                '        self.tokens = min(self.capacity, self.tokens + seconds * self.rate)\n'
                '\n'
                '    def take(self):\n'
                '        if self.tokens >= 1:\n'
                '            self.tokens -= 1\n'
                '            return True\n'
                '        return False\n'
                '\n'
                'bucket = Bucket(capacity=2, refill_per_second=0.5)\n'
                'for i in range(4):\n'
                '    ok = bucket.take()\n'
                '    print("request", i + 1, "at", bucket.now, "s allowed:", ok, "tokens:", round(bucket.tokens, 2))\n'
                'bucket.advance(4)\n'
                'print("after waiting: allowed:", bucket.take())\n'
                'print("tokens left:", round(bucket.tokens, 2))\n'
                'assert bucket.tokens == 1.0\n'
                'print("burst capped, average pace enforced")'
            ),
            variant_b="capacity 5 and refill 1 token per second with six immediate requests",
            variant_c="a server Retry-After of 30 seconds that must delay the next attempt",
            mistakes=[
                "Sleeping after every request but still running many workers against one account quota.",
                "Ignoring Retry-After and retrying as soon as the local timer allows.",
                "Treating a write endpoint with the same loose limit as a read endpoint.",
            ],
            q1=(
                "Why does authenticated scraping need a stricter limit than anonymous reading?",
                "It spends a real account's quota and can affect that user; going too fast risks a lockout or a security response, not just a block.",
            ),
            homework=(
                "Write `Bucket(capacity, refill_per_second)` with `advance(seconds)` and `take()` methods, then run a burst and "
                "a refill scenario. Print each decision, and comment which line enforces the sustained rate rather than the burst."
            ),
            patterns=["class ", "def take", "print("],
            mapping=(
                "APIs publish quotas and send Retry-After headers; Requests clients wrap a token bucket around calls, and "
                "Playwright runs should use one browser context per account with concurrency one when quotas are tight."
            ),
        ),
        148: dict(
            topic="Testing dynamic scrapers",
            idea=(
                "A dynamic scraper fails for reasons that are hard to reproduce: a slow render, an expired session, a response "
                "that changed shape, a wait that fired one second too early. Testing has to make those conditions cheap to "
                "recreate. Start with fixtures captured from real runs: rendered HTML, JSON bodies, and headers with secrets "
                "removed. Then test the pure parts first. The parser should turn a fixture into an exact expected list, and the "
                "comparison should name the first differing record rather than dumping a wall of text. The session and paging "
                "loops should run against fake clients that can return 401, an empty page, a repeated cursor, or a malformed "
                "body on demand. Time must be injectable, so a wait test advances a fake clock instead of sleeping. The most "
                "valuable tests encode failure conditions, not happy paths: missing column, challenge page, token expiry, and a "
                "short page with a non-null cursor. Also keep one golden fixture per source revision and refresh it deliberately, "
                "with a note describing what changed. A scraper that only works on today's live site is untested by definition. "
                "The test suite is how you find out that a site change altered a field before a scheduled run writes a "
                "thousand wrong rows. Treat every production parse failure as a missing test, then add the smallest fixture that "
                "would have caught it."
            ),
            code=(
                'def parse_rows(payload):\n'
                '    if "items" not in payload:\n'
                '        raise ValueError("missing items key")\n'
                '    return [{"id": i["id"], "price": float(i["price"])} for i in payload["items"]]\n'
                '\n'
                'fixtures = {\n'
                '    "normal": {"items": [{"id": 1, "price": "9.99"}]},\n'
                '    "renamed": {"results": [{"id": 1, "price": "9.99"}]},\n'
                '}\n'
                '\n'
                'def check(name, payload, expected):\n'
                '    try:\n'
                '        got = parse_rows(payload)\n'
                '    except ValueError as error:\n'
                '        print(name, "-> rejected:", error)\n'
                '        return "rejected"\n'
                '    print(name, "->", got)\n'
                '    return "ok" if got == expected else "mismatch"\n'
                '\n'
                'a = check("normal", fixtures["normal"], [{"id": 1, "price": 9.99}])\n'
                'b = check("renamed", fixtures["renamed"], [{"id": 1, "price": 9.99}])\n'
                'print("outcomes:", a, b)\n'
                'assert a == "ok" and b == "rejected"\n'
                'print("the renamed fixture fails before a live run does")'
            ),
            variant_b="a fixture with a price of 'sold out' that should be rejected or mapped to None",
            variant_c="a fixture with two identical ids that should expose a deduplication bug",
            mistakes=[
                "Testing only the happy path, so a renamed field reaches production unnoticed.",
                "Using real sleeps in tests, which makes the suite slow and flaky.",
                "Pretending a captured fixture is still current without dating or refreshing it.",
            ],
            q1=(
                "Why must a dynamic scraper have failure fixtures as well as normal ones?",
                "The dangerous changes are missing keys, challenge pages and expired sessions; only a fixture of the failure proves the code handles it.",
            ),
            homework=(
                "Write `check(name, payload, expected)` and a `parse_rows(payload)` parser, then run both on a normal fixture and "
                "a renamed-key fixture. Print the outcomes, and comment which line makes the failure visible before a live run."
            ),
            patterns=["def ", "assert", "print("],
            mapping=(
                "Playwright can record HAR and DOM snapshots for fixtures; pytest runs the pure parser against them without a "
                "browser. Keep one dated fixture per source revision and refresh it when the live shape changes."
            ),
        ),
        149: dict(
            topic="Review: API vs browser",
            idea=(
                "By now you have two ways to reach the same data, and the professional question is which one is justified. The "
                "API path wins when the data arrives as JSON, the request is documented or discoverable, the volume is "
                "moderate, and the response shape is stable. It is faster, cheaper, easier to test, and leaves less "
                "infrastructure to maintain. The browser path wins when the data only exists after client-side interaction: a "
                "canvas chart, a multi-step form, a login flow with device checks, or content assembled from many requests. "
                "Browser automation is heavier, slower, more fragile, and consumes memory, so it should be a considered choice "
                "rather than the default. Make the decision explicit with a small set of questions. Is the data in the initial "
                "or a discoverable JSON response? Does access require a human step or a challenge? Is the site's policy "
                "compatible with automated collection? How much data, how often, and how stable is the markup? If two answers "
                "point at the API, try the API first and keep the browser as a fallback for the routes that genuinely need it. "
                "Hybrid is normal: use a browser to establish a session, then call the API with that session. Whatever the "
                "choice, the output contract stays the same — plain records, validated and counted — so storage and analysis "
                "never need to know how the bytes arrived."
            ),
            code=(
                'def choose(source):\n'
                '    if source["challenge"]:\n'
                '        return "stop: needs permission, not a workaround"\n'
                '    score = 0\n'
                '    score += 2 if source["json"] else 0\n'
                '    score += 1 if source["documented"] else 0\n'
                '    score += 1 if source["volume"] < 10000 else 0\n'
                '    score -= 2 if source["human_step"] else 0\n'
                '    if score >= 3:\n'
                '        return "api"\n'
                '    if source["human_step"] or not source["json"]:\n'
                '        return "browser"\n'
                '    return "api first, browser fallback"\n'
                '\n'
                'cases = {\n'
                '    "catalogue": {"json": True, "documented": True, "volume": 500, "human_step": False, "challenge": False},\n'
                '    "canvas": {"json": False, "documented": False, "volume": 200, "human_step": True, "challenge": False},\n'
                '    "blocked": {"json": True, "documented": False, "volume": 50, "human_step": False, "challenge": True},\n'
                '}\n'
                'for name, source in cases.items():\n'
                '    print(name, "->", choose(source))\n'
                'assert choose(cases["catalogue"]) == "api"\n'
                'assert choose(cases["canvas"]) == "browser"\n'
                'assert choose(cases["blocked"]).startswith("stop")\n'
                'print("route chosen by evidence, not habit")'
            ),
            variant_b="a documented JSON API with a required human consent step",
            variant_c="a large documented source that also exposes a canvas-only detail view",
            mistakes=[
                "Defaulting to browser automation because it feels more like using the site.",
                "Choosing an API without checking its quota, policy and authentication requirements.",
                "Mixing API and browser records without a shared schema and deduplication key.",
            ],
            q1=(
                "When is the browser path the honest choice?",
                "When the data exists only after client-side interaction or a human step, and the API route is absent, insufficient or not permitted.",
            ),
            homework=(
                "Write `choose(source)` that scores JSON availability, documentation, volume and human steps, and returns api, "
                "browser or stop. Run it on two different source descriptions, print both decisions, and comment which condition "
                "overrides the score."
            ),
            patterns=["def ", "return", "print("],
            mapping=(
                "Open DevTools Network first; if a clean JSON endpoint exists, use Requests. Reach for Playwright or Selenium "
                "only for interaction-heavy routes, and stop when a challenge signals that permission is the real answer."
            ),
        ),
    },
)
