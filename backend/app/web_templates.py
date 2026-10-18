"""Canonical exercise templates for the web-development domain blocks.

Five blocks of fifteen days cover what a web path actually teaches: how the web
works, building an API, storing data, wiring a frontend to a backend, and
quality and security. Unlike the shared Python blocks these are not identical
across paths, so they are authored for one path and applied to one path.

The exercises model their subjects in the standard library rather than importing
a framework. `sqlite3`, `http.server`, `urllib`, `hashlib`, `secrets` and
`unittest` are all standard, so every template runs unattended with nothing
installed, and the idea being taught stays visible instead of disappearing into a
framework's plumbing.
"""
from __future__ import annotations

from app.exercise_gen import ExerciseTemplate

R = (
    "Code must run without raising, define at least one function, and print the stated output.",
    "The required constructs must appear so the idea is practised, not bypassed.",
    "Changing one input value must change the output in the way the prompt predicts.",
)


def _t(**kw) -> ExerciseTemplate:
    return ExerciseTemplate(rubric=R, **kw)


WEB_FOUNDATIONS: tuple[ExerciseTemplate, ...] = (

    _t(id="wf-75-request", block="Web Foundations", day=75, skill="The request and response cycle",
       prompt=(
           "A web server is a function from a request to a response. Write `handle(request)` taking a "
           "request dict with `method` and `path`, and returning a response dict with `status` and "
           "`body`. Serve <<routes>>. Print each request and the status it produced, so the cycle is "
           "visible as data rather than as a diagram."),
       solution='''ROUTES = <<routes>>


def handle(request):
    key = (request['method'], request['path'])
    handler = ROUTES.get(key)
    if handler is None:
        return {'status': 404, 'body': 'not found'}
    return {'status': 200, 'body': handler(request)}


def main(routes=ROUTES):
    for request in ({'method': 'GET', 'path': '/'},
                    {'method': 'GET', 'path': '/about'},
                    {'method': 'GET', 'path': '/nope'}):
        response = handle(request)
        print(f"{request['method']} {request['path']:<8} -> {response['status']} {response['body']}")


main()''',
       required_patterns=("def ", "get(", "return", "for ", "print("),
       params={"routes": ("""{'/': lambda r: 'home', '/about': lambda r: 'about'}""",
                          """{'/': lambda r: 'welcome', '/api': lambda r: '{}', '/x': lambda r: 'x'}""",
                          """{'/': lambda r: 'root', '/help': lambda r: 'help text'}""")},
       expect=("-> 404",),
       n_variants=3),

    _t(id="wf-76-html-structure", block="Web Foundations", day=76, skill="Nesting and closing tags",
       prompt=(
           "Write `nest(tags)` that builds correctly nested HTML from a list of tag names, with the "
           "inner ones inside the outer one, and `well_formed(html)` that returns True when every "
           "opening tag has a matching closing tag in the right order. Use <<tags>> and print the HTML "
           "and whether it is well formed, so the two functions check each other."),
       solution='''TAGS = <<tags>>


def nest(tags):
    if not tags:
        return ''
    outer = tags[0]
    inner = nest(tags[1:])
    return f'<{outer}>{inner}</{outer}>'


def well_formed(html):
    import re
    stack = []
    for match in re.finditer(r'<(/?)(\\w+)>', html):
        closing, name = match.group(1), match.group(2)
        if not closing:
            stack.append(name)
        elif not stack or stack.pop() != name:
            return False
    return not stack


def main(tags=TAGS):
    html = nest(tags)
    print('html    :', html)
    print('balanced:', well_formed(html))
    print('broken  :', well_formed('<div><span></div>'))


main()''',
       required_patterns=("def ", "return", "for ", "print("),
       params={"tags": ("""['html', 'body', 'main', 'p']""", """['div', 'section', 'span']""",
                         """['main', 'article', 'header', 'h1', 'text']""")},
       expect=("balanced: True",),
       n_variants=3),

    _t(id="wf-77-semantic", block="Web Foundations", day=77, skill="Choosing elements for meaning",
       prompt=(
           "A page is a list of blocks given as plain text descriptions. Write `to_html(blocks)` that "
           "chooses a semantic element per kind of block: `nav` for navigation, `h1` for the heading, "
           "`main` for the body, `footer` for the footer, and `p` for anything else. Use <<blocks>> and "
           "print the tags chosen, so the mapping is visible."),
       solution='''BLOCKS = <<blocks>>


def to_html(blocks):
    mapping = {
        'navigation': 'nav',
        'heading': 'h1',
        'body': 'main',
        'footer': 'footer',
    }
    out = []
    for kind, text in blocks:
        tag = mapping.get(kind, 'p')
        out.append(f'<{tag}>{text}</{tag}>')
    return out


def main(blocks=BLOCKS):
    for line in to_html(blocks):
        print(line)


main()''',
       required_patterns=("def ", "get(", "for ", "append(", "print("),
       params={"blocks": ("""[('heading', 'Site'), ('navigation', 'Home'), ('body', 'Welcome'), ('footer', 'Copyright')]""",
                           """[('heading', 'Menu'), ('text', 'Just some words'), ('footer', 'End')]""",
                           """[('heading', 'Docs'), ('body', 'Intro'), ('text', 'More'), ('footer', 'F')]""")},
       expect=("<h1>",),
       n_variants=3),

    _t(id="wf-78-forms", block="Web Foundations", day=78, skill="Form encoding and parsing",
       prompt=(
           "A form posts key and value pairs. Write `encode(fields)` producing the percent-encoded "
           "body and `decode(body)` reading it back, including repeated keys. Use <<fields>> and print "
           "the body, the parsed dict, and the list of values for a key that appears twice, so the "
           "round trip and the repetition are both visible."),
       solution='''FIELDS = <<fields>>


def encode(fields):
    from urllib.parse import quote
    return '&'.join(f'{quote(k)}={quote(v)}' for k, v in fields)


def decode(body):
    from urllib.parse import unquote_plus
    out = {}
    for pair in body.split('&'):
        if not pair:
            continue
        key, _, value = pair.partition('=')
        out.setdefault(unquote_plus(key), []).append(unquote_plus(value))
    return out


def main(fields=FIELDS):
    body = encode(fields)
    print('body   :', body)
    parsed = decode(body)
    print('parsed :', parsed)
    for key, values in parsed.items():
        if len(values) > 1:
            print(f'repeated {key}: {values}')


main()''',
       required_patterns=("def ", "split(", "append(", "print("),
       params={"fields": ("""[('name', 'Asha Rao'), ('tag', 'python'), ('tag', 'data')]""",
                           """[('q', 'search terms'), ('q', 'other terms'), ('page', '2')]""",
                           """[('a', '1'), ('b', '2'), ('a', '3'), ('b', '4')]""")},
       expect=("repeated",),
       n_variants=3),

    _t(id="wf-79-css", block="Web Foundations", day=79, skill="Specificity and the cascade",
       prompt=(
           "Given rules for <<selectors>> and a list of properties, work out which declaration wins by "
           "specificity, breaking a tie by source order. Print the winner for each selector, and print "
           "the total specificity as (ids, classes, elements) so the rule is explicit rather than "
           "folklore."),
       solution='''SELECTORS = <<selectors>>
DECLARATIONS = [('color', 'red'), ('color', 'blue'), ('font-size', '14px')]


def specificity(selector):
    return (selector.count('#'), selector.count('.') + selector.count('['), 0)


def winner(selector, declarations):
    best = None
    for prop, value in declarations:
        if prop != selector:
            continue
        if best is None or specificity(selector) >= best[0]:
            best = (specificity(selector), value)
    return best[1] if best else 'unset'


def main(selectors=SELECTORS):
    for selector in selectors:
        print(f'{selector:<14} {specificity(selector)} -> {winner(selector, DECLARATIONS)}')


main()''',
       required_patterns=("def ", "for ", "if ", "print("),
       params={"selectors": ("['#main', '.note', 'p']", "['.a.b', '#x', 'div']",
                             "['header', '.nav a', '#site .link']")},
       expect=("-> "),
       n_variants=3),

    _t(id="wf-80-responsive", block="Web Foundations", day=80, skill="Breakpoints and fluid sizing",
       prompt=(
           "Write `columns(width, breakpoints)` choosing a column count for each named breakpoint and "
           "a percentage width per column, and `fluid(base, max_width, viewport)` clamping a fluid width "
           "between two limits. Use viewport <<viewport>> and breakpoints <<breakpoints>> and print the "
           "result, so the arithmetic behind a fluid layout is visible rather than magical."),
       solution='''BREAKPOINTS = <<breakpoints>>


def columns(width, breakpoints):
    out = []
    for name, minimum in breakpoints:
        count = max(1, width // minimum)
        out.append((name, count, round(100 / count, 1)))
    return out


def fluid(base, max_width, viewport):
    return round(min(max_width, max(base, viewport * base / 100)), 1)


def main(breakpoints=BREAKPOINTS, viewport=<<viewport>>):
    for name, count, percent in columns(1200, breakpoints):
        print(f'{name:<10} {count} column(s) at {percent}%')
    print('fluid width:', fluid(90, 1200, viewport))


main()''',
       required_patterns=("def ", "max(", "for ", "print("),
       params={"breakpoints": ("[('sm', 480), ('md', 768), ('lg', 1024)]",
                               "[('xs', 360), ('sm', 600), ('xl', 1200)]",
                               "[('mobile', 400), ('tablet', 800)]"),
               "viewport": ("360", "1024", "768")},
       expect=("column(s) at",),
       n_variants=3),

    _t(id="wf-81-javascript", block="Web Foundations", day=81, skill="The shape of client-side code",
       prompt=(
           "Model a browser update without a browser: `render(state)` producing the text a component "
           "would show, and `set_state(state, key, value)` returning a new state rather than mutating. "
           "Use <<initial>> and apply two updates, printing the rendered text after each, so the "
           "immutable-update habit is visible."),
       solution='''INITIAL = <<initial>>


def set_state(state, key, value):
    # Returning a new object rather than mutating is what makes re-rendering
    # predictable, and it is the habit worth forming.
    return {**state, key: value}


def render(state):
    if state['count'] == 0:
        return 'Cart is empty'
    label = 'item' if state['count'] == 1 else 'items'
    return f"Cart has {state['count']} {label}"


def main(initial=INITIAL):
    state = initial
    print('start :', render(state))
    for key, value in (('count', 1), ('count', 3)):
        state = set_state(state, key, value)
        print(f'after {key}={value}:', render(state))


main()''',
       required_patterns=("def ", "return", "for ", "print("),
       params={"initial": ("{'count': 0, 'name': 'Asha'}", "{'count': 0}",
                           "{'count': 0, 'name': 'Rohan', 'total': 0}")},
       expect=("Cart is empty",),
       n_variants=3),

    _t(id="wf-82-devtools", block="Web Foundations", day=82, skill="Reading a network response",
       prompt=(
           "A response has a status, headers and a body. Write `summarise(response)` validating that "
           "each part is present and reporting the first problem found, and `timing(entries)` "
           "computing the total and slowest request. Use <<response>> and <<entries>> and print both "
           "results, so a missing field is caught rather than assumed absent."),
       solution='''RESPONSE = <<response>>
ENTRIES = <<entries>>


def summarise(response):
    for field in ('status', 'headers', 'body'):
        if field not in response:
            return f'missing field: {field}'
    size = len(response['body'])
    return f"status {response['status']}, {len(response['headers'])} headers, {size} bytes"


def timing(entries):
    total = sum(e['ms'] for e in entries)
    slowest = max(entries, key=lambda e: e['ms'])
    return total, slowest


def main(response=RESPONSE, entries=ENTRIES):
    print('summary :', summarise(response))
    print('broken  :', summarise({'status': 200}))
    total, slowest = timing(entries)
    print(f'total {total}ms, slowest {slowest["name"]} at {slowest["ms"]}ms')


main()''',
       required_patterns=("def ", "for ", "max(", "print("),
       params={"response": ("{'status': 200, 'headers': {'content-type': 'text/html'}, 'body': 'hello'}",
                            "{'status': 500, 'headers': {}, 'body': 'oops'}",
                            "{'status': 404, 'headers': {'x': '1'}, 'body': ''}"),
               "entries": ("[{'name': 'doc', 'ms': 40}, {'name': 'app.js', 'ms': 180}, {'name': 'api', 'ms': 90}]",
                           "[{'name': 'a', 'ms': 10}, {'name': 'b', 'ms': 250}]",
                           "[{'name': 'x', 'ms': 5}, {'name': 'y', 'ms': 5}, {'name': 'z', 'ms': 120}]")},
       expect=("total",),
       n_variants=3),

    _t(id="wf-83-methods", block="Web Foundations", day=83, skill="HTTP methods and their meaning",
       prompt=(
           "Write `allowed(method)` reporting whether a method is safe, and `idempotent(method)`. "
           "Check the methods <<methods>> and print a table of the three properties, so the distinction "
           "between safe and idempotent is visible rather than remembered."),
       solution='''METHODS = <<methods>>
SAFE = {'GET', 'HEAD', 'OPTIONS'}
IDEMPOTENT = {'GET', 'HEAD', 'PUT', 'DELETE', 'OPTIONS'}


def allowed(method):
    return method in {'GET', 'HEAD', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS'}


def is_safe(method):
    return method in SAFE


def is_idempotent(method):
    return method in IDEMPOTENT


def main(methods=METHODS):
    for method in methods:
        print(f'{method:<8} allowed={str(allowed(method)):<5} '
              f'safe={str(is_safe(method)):<5} idempotent={is_idempotent(method)}')


main()''',
       required_patterns=("def ", "return", "for ", "print("),
       params={"methods": ("['GET', 'POST', 'PUT', 'DELETE']", "['HEAD', 'PATCH', 'OPTIONS']",
                          "['GET', 'PUT', 'POST', 'PATCH', 'DELETE']")},
       expect=("allowed=",),
       n_variants=3),

    _t(id="wf-84-status", block="Web Foundations", day=84, skill="Choosing a status code",
       prompt=(
           "Write `status_for(outcome)` mapping an outcome to a status, and `describe(status)` giving "
           "a short reason. Handle the outcomes <<outcomes>> and print each status with its reason, "
           "so the code chosen is justified rather than guessed."),
       solution='''OUTCOMES = <<outcomes>>


def status_for(outcome):
    mapping = {
        'created': 201,
        'ok': 200,
        'missing': 404,
        'denied': 403,
        'invalid': 422,
        'crashed': 500,
    }
    return mapping.get(outcome, 400)


def describe(status):
    reasons = {
        200: 'request succeeded',
        201: 'a new resource was created',
        403: 'refused, and retrying will not help',
        404: 'no such resource',
        422: 'well-formed but semantically wrong',
        500: "our fault, not the caller's",
        400: 'could not understand the request',
    }
    return reasons.get(status, 'unknown')


def main(outcomes=OUTCOMES):
    for outcome in outcomes:
        status = status_for(outcome)
        print(f'{outcome:<10} {status}  {describe(status)}')


main()''',
       required_patterns=("def ", "get(", "for ", "print("),
       params={"outcomes": ("['ok', 'created', 'missing', 'invalid']",
                            "['ok', 'denied', 'crashed', 'missing']",
                            "['created', 'missing', 'denied', 'invalid', 'crashed']")},
       expect=("missing",),
       n_variants=3),

    _t(id="wf-85-urls", block="Web Foundations", day=85, skill="Query strings and parameters",
       prompt=(
           "Write `parse_qs(query)` producing a dict of key to list of values and `build_qs(params)` "
           "the inverse. Round-trip <<params>> and print the body, the parsed values, and which keys "
           "were repeated, so the encoding and the reading agree."),
       solution='''PARAMS = <<params>>


def parse_qs(query):
    from urllib.parse import unquote_plus
    out = {}
    for pair in query.split('&'):
        if not pair:
            continue
        key, _, value = pair.partition('=')
        out.setdefault(unquote_plus(key), []).append(unquote_plus(value))
    return out


def build_qs(params):
    from urllib.parse import quote
    parts = []
    for key, values in params.items():
        for value in values:
            parts.append(f'{quote(key)}={quote(value)}')
    return '&'.join(parts)


def main(params=PARAMS):
    query = build_qs(params)
    print('query  :', query)
    parsed = parse_qs(query)
    print('parsed :', parsed)
    print('repeated:', sorted(k for k, v in parsed.items() if len(v) > 1))
    print('round trip:', parsed == params)


main()''',
       required_patterns=("def ", "split(", "for ", "print("),
       params={"params": ("""{'tag': ['a', 'b'], 'page': ['2']}""",
                          "{'q': ['search'], 'sort': ['asc']}",
                          "{'x': ['1', '2'], 'y': ['3', '4']}")},
       expect=("round trip: True",),
       n_variants=3),

    _t(id="wf-86-json-http", block="Web Foundations", day=86, skill="JSON over HTTP",
       prompt=(
           "Write `respond(payload, status)` producing a JSON body with a content type, and "
           "`read_json(body)` parsing one, raising ValueError on malformed input rather than returning "
           "something falsy. Use <<payload>> and print the body, the parsed round trip, and the error "
           "for a malformed body."),
       solution='''PAYLOAD = <<payload>>


def respond(payload, status=200):
    import json
    return {'status': status,
            'headers': {'content-type': 'application/json'},
            'body': json.dumps(payload, sort_keys=True)}


def read_json(body):
    import json
    return json.loads(body)


def main(payload=PAYLOAD):
    response = respond(payload)
    print('status :', response['status'])
    print('body   :', response['body'])
    parsed = read_json(response['body'])
    print('round trip:', parsed == payload)
    try:
        read_json('{"broken": }')
    except ValueError as err:
        print('malformed rejected:', type(err).__name__)


main()''',
       required_patterns=("import json", "dumps", "loads", "print("),
       params={"payload": ("{'name': 'Asha', 'tags': ['a', 'b'], 'ok': True}",
                           "{'id': 1, 'items': []}",
                           "{'error': 'nope', 'code': 404}")},
       expect=("round trip: True",),
       n_variants=3),

    _t(id="wf-87-a11y", block="Web Foundations", day=87, skill="Auditing a page for accessibility",
       prompt=(
           "Write `audit(html)` checking for an image without alternative text, an input without a "
           "label and a heading level skipped. Given the fragments <<fragments>>, print each finding "
           "and a total, so the check is a list rather than an opinion."),
       solution='''FRAGMENTS = <<fragments>>


def audit(html):
    import re
    problems = []
    for tag in re.findall(r'<img[^>]*>', html):
        if 'alt=' not in tag:
            problems.append('image without alt text')
    for tag in re.findall(r'<(input|select|textarea)[^>]*>', html):
        if 'aria-label' not in tag and 'id=' not in tag:
            problems.append(f'{tag} without a label')
    levels = [int(h) for h in re.findall(r'<h([1-6])', html)]
    for first, second in zip(levels, levels[1:]):
        if second > first + 1:
            problems.append(f'heading level jumps from h{first} to h{second}')
    return problems


def main(fragments=FRAGMENTS):
    total = 0
    for fragment in fragments:
        problems = audit(fragment)
        total += len(problems)
        print(f'{fragment[:44]:<46} {len(problems)} issue(s): {problems}')
    print('total issues:', total)


main()''',
       required_patterns=("def ", "findall(", "for ", "append(", "print("),
       params={"fragments": ("""['<h1>Title</h1><img src="a.png">', '<h1>T</h1><h3>Sub</h3>', '<input type=text>']""",
                             """['<img src=x>', '<h2>Only h2</h2>', '<input id=name>']""",
                             """['<h1>A</h1><h2>B</h2><h2>C</h2><img src=1 alt=ok>']""")},
       expect=("total issues:",),
       n_variants=3),

    _t(id="wf-88-websec", block="Web Foundations", day=88, skill="Escaping output and rejecting bad input",
       prompt=(
           "Write `escape(text)` escaping the characters that matter in HTML, and `safe_render(user)` "
           "using it. Then write `reject(value)` refusing input that is empty, absurdly long, or "
           "carrying a script tag. Use <<input>> and print the escaped output, the refused cases and "
           "their reasons, and the value that got through."),
       solution='''INPUT = <<input>>


def escape(text):
    replacements = {'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#x27;'}
    out = []
    for char in text:
        out.append(replacements.get(char, char))
    return ''.join(out)


def reject(value):
    if not value.strip():
        return 'empty'
    if len(value) > 100:
        return 'too long'
    if 'script' in value.lower():
        return 'contains a script tag'
    return None


def main(value=INPUT):
    print('escaped:', escape(value))
    for candidate in ('', 'x' * 200, '<script>alert(1)</script>', 'Asha'):
        print(f'{candidate[:24]!r:<28} -> {reject(candidate)}')


main()''',
       required_patterns=("def ", "return", "for ", "print("),
       params={"input": ("'<b>bold</b> & \"quotes\"'", "'Tom & Jerry'", "'<script>alert(1)</script>'")},
       expect=("escaped:",),
       n_variants=3),

    _t(id="wf-89-project", block="Web Foundations", day=89, skill="Assembling a static site",
       prompt=(
           "Build a small site from a list of pages: `build(pages)` returning a dict of path to HTML "
           "using a shared template, and `nav(paths)` returning the navigation links for a path. Use "
           "<<pages>> and print the generated paths, one page's HTML, and the links it contains, so "
           "the template is visibly shared."),
       solution='''PAGES = <<pages>>


def render(title, body, links):
    items = ''.join(f'<a href="{href}">{text}</a>' for href, text in links)
    return f'<html><head><title>{title}</title></head><body>{items}<main>{body}</main></body></html>'


def build(pages):
    out = {}
    for path, (title, body) in pages.items():
        links = [(p, t) for p, (t, _b) in pages.items() if p != path]
        out[path] = render(title, body, links)
    return out


def nav(html):
    import re
    return re.findall(r'href="([^"]+)"', html)


def main(pages=PAGES):
    built = build(pages)
    print('built:', sorted(built))
    first = sorted(built)[0]
    print(f'{first} ->', built[first])
    print('links :', nav(built[first]))


main()''',
       required_patterns=("def ", "for ", "return", "print("),
       params={"pages": ("""{'/': ('Home', 'Welcome'), '/about': ('About', 'Who we are')}""",
                          """{'/': ('Home', 'Hi'), '/docs': ('Docs', 'Reference')}""",
                          """{'/': ('A', 'x'), '/b': ('B', 'y'), '/c': ('C', 'z')}""")},
       expect=("links :",),
       n_variants=3),
)


FASTAPI_APIS: tuple[ExerciseTemplate, ...] = (

    _t(id="fa-90-setup", block="FastAPI APIs", day=90, skill="An application object and registration",
       prompt=(
           "Model a minimal application: `App()` collects routes, `route(method, path)` is a "
           "decorator that registers a function under that method and path, and `dispatch(method, "
           "path)` returns the handler's response. Register the routes <<routes>> and print the route "
           "table, so registration and lookup are visibly separate steps."),
       solution='''ROUTES = <<routes>>


class App:
    def __init__(self):
        self.routes = {}

    def route(self, method, path):
        def decorate(func):
            self.routes[(method, path)] = func
            return func
        return decorate

    def dispatch(self, method, path, **params):
        handler = self.routes.get((method, path))
        if handler is None:
            return 404, {'error': 'not found'}
        return 200, handler(**params)


def main(routes=ROUTES):
    app = App()

    @app.route('GET', '/items')
    def list_items():
        return {'items': [1, 2, 3]}

    @app.route('GET', '/items/{item_id}')
    def get_item(item_id):
        return {'id': item_id}


    @app.route('POST', '/items')
    def create_item():
        return {'created': True}

    for method, path in sorted(app.routes):
        print(f'{method:<5} {path}')
    print('---')
    print(app.dispatch('GET', '/items'))
    print(app.dispatch('GET', '/items/{item_id}', item_id=7))
    print(app.dispatch('POST', '/items'))


main()''',
       required_patterns=("class ", "def ", "get(", "return", "print("),
       params={"routes": ("""['GET /items', 'GET /items/{id}']""",
                          """['GET /health', 'GET /users', 'GET /users/{id}']""",
                          """['GET /', 'POST /', 'GET /status']""")},
       expect=("---",),
       n_variants=3),

    _t(id="fa-91-routing", block="FastAPI APIs", day=91, skill="Matching a path pattern",
       prompt=(
           "Write `match(pattern, path)` matching a pattern with `{name}` placeholders against a path "
           "and returning either a dict of captured values or None, and `resolve(routes, path)` "
           "finding the first match. Use the routes <<routes>> and the path <<path>>, and print the "
           "captured parameters or the failure, so matching is a function you can test."),
       solution='''ROUTES = <<routes>>
PATH = <<path>>


def match(pattern, path):
    p_parts = pattern.strip('/').split('/')
    a_parts = path.strip('/').split('/')
    if len(p_parts) != len(a_parts):
        return None
    captured = {}
    for expected, actual in zip(p_parts, a_parts):
        if expected.startswith('{') and expected.endswith('}'):
            captured[expected[1:-1]] = actual
        elif expected != actual:
            return None
    return captured


def resolve(routes, path):
    for pattern in routes:
        captured = match(pattern, path)
        if captured is not None:
            return pattern, captured
    return None, None


def main(routes=ROUTES, path=PATH):
    for pattern in routes:
        print(f'{pattern:<24} -> {match(pattern, path)}')
    pattern, captured = resolve(routes, path)
    print('resolved:', pattern, captured)


main()''',
       required_patterns=("def ", "return", "for ", "if ", "print("),
       params={"routes": ("""['/items', '/items/{id}', '/items/{id}/tags']""",
                          """['/users', '/users/{uid}', '/users/{uid}/posts/{pid}']""",
                          """['/', '/about', '/teams/{team}']"""),
               "path": ("""'"/items/42'""", """'"/users/7/posts/9'""", """'"/teams/core'""")},
       expect=("resolved:",),
       n_variants=3),

    _t(id="fa-92-pathparams", block="FastAPI APIs", day=92, skill="Typed path parameters and coercion",
       prompt=(
           "Write `coerce(value, target)` converting a captured string to `int`, `float` or `str` and "
           "raising ValueError on a bad value, and `endpoint(params)` validating a request against "
           "<<fields>>. Print the result for a good request and for a bad one, so validation failure "
           "is visible as a failure rather than as a surprise."),
       solution='''FIELDS = <<fields>>


def coerce(value, target):
    if target is str:
        return value
    try:
        return target(value)
    except (TypeError, ValueError) as err:
        raise ValueError(f'cannot read {value!r} as {target.__name__}') from err


def validate(params, fields):
    out = {}
    for key, target in fields.items():
        if key not in params:
            raise ValueError(f'missing parameter: {key}')
        out[key] = coerce(params[key], target)
    return out


SAMPLES = {'int': '42', 'float': '4.5', 'str': 'text'}


def main(fields=FIELDS):
    good = {key: SAMPLES[target.__name__] for key, target in fields.items()}
    print('good:', validate(good, fields))
    broken = dict(good)
    first = next(iter(fields))
    broken[first] = 'not-a-number'
    for bad in (broken, {k: v for k, v in list(fields.items())[1:]}):
        try:
            validate(bad, fields)
        except ValueError as err:
            print('rejected:', bad, '->', err)


main()''',
       required_patterns=("def ", "raise ", "try:", "except ", "print("),
       params={"fields": ("{'item_id': int, 'limit': int}", "{'uid': int, 'score': float}",
                          "{'team': str, 'year': int}")},
       expect=("rejected:",),
       n_variants=3),

    _t(id="fa-93-queryparams", block="FastAPI APIs", day=93, skill="Optional query parameters and defaults",
       prompt=(
           "Write `query(request)` reading a dict of query values, applying a default where a key is "
           "absent and raising ValueError where a value is present but unusable. Apply it to "
           "<<params>> and print the resolved parameters, so absent and invalid are two different "
           "outcomes rather than one."),
       solution='''PARAMS = <<params>>


def query(values, defaults):
    resolved = dict(defaults)
    for key, raw in values.items():
        if key not in defaults:
            raise ValueError(f'unknown parameter: {key}')
        target = type(defaults[key])
        try:
            resolved[key] = target(raw)
        except (TypeError, ValueError):
            raise ValueError(f'bad value for {key}: {raw!r}') from None
    return resolved


def main(params=PARAMS):
    defaults = {'limit': 10, 'offset': 0, 'search': ''}
    print('resolved:', query(params, defaults))
    for bad in ({'limit': 'lots'}, {'unknown': '1'}):
        try:
            query(bad, defaults)
        except ValueError as err:
            print('rejected:', err)


main()''',
       required_patterns=("def ", "raise ", "try:", "except ", "print("),
       params={"params": ("{'limit': '25', 'search': 'python'}", "{'offset': '5'}",
                          "{'limit': '10', 'offset': '20', 'search': 'x'}")},
       expect=("rejected:",),
       n_variants=3),

    _t(id="fa-94-bodies", block="FastAPI APIs", day=94, skill="Request bodies and required fields",
       prompt=(
           "Write `body(payload, required)` returning the payload when every required key is present "
           "and non-empty, and raising ValueError naming the first missing field. Use "
           "<<payload>> and <<required>> and print the accepted body and the rejection with its "
           "reason, so a client error names the field rather than just failing."),
       solution='''PAYLOAD = <<payload>>
REQUIRED = <<required>>


def body(payload, required):
    if not isinstance(payload, dict):
        raise ValueError('body must be an object')
    for field in required:
        if field not in payload or payload[field] in (None, ''):
            raise ValueError(f'missing or empty field: {field}')
    return payload


def main(payload=PAYLOAD, required=REQUIRED):
    try:
        accepted = body(payload, required)
        print('accepted:', accepted)
    except ValueError as err:
        print('rejected:', err)
    for bad in ({'name': 'Asha'}, 'not an object'):
        try:
            body(bad, required)
        except ValueError as err:
            print('rejected:', err)


main()''',
       required_patterns=("def ", "raise ", "try:", "except ", "print("),
       params={"payload": ("{'name': 'Asha', 'email': 'a@b.co', 'score': 88}",
                           "{'title': 'Notes', 'body': 'text', 'tags': ['a']}",
                           "{'id': 1, 'status': 'new'}"),
               "required": ("('name', 'email')", "('title', 'body')", "('id', 'status')")},
       expect=("rejected:",),
       n_variants=3),

    _t(id="fa-95-models", block="FastAPI APIs", day=95, skill="A model that validates itself",
       prompt=(
           "Define a `Model` base class carrying fields and required names, and two subclasses, then "
           "`parse(cls, data)` validating against the required list and filling defaults. Use "
           "<<data>> and print a valid instance, a rejected one, and the error naming the field."),
       solution='''DATA = <<data>>


class Model:
    required = ()
    defaults = {}


def parse(cls, data):
    if not isinstance(data, dict):
        raise ValueError('expected an object')
    for field in cls.required:
        if field not in data or data[field] in (None, ''):
            raise ValueError(f'{cls.__name__}: missing {field}')
    merged = dict(cls.defaults)
    merged.update(data)
    known = set(cls.required) | set(cls.defaults)
    return {k: v for k, v in merged.items() if k in known}


class User(Model):
    required = ('name', 'email')
    defaults = {'role': 'member'}


class Item(Model):
    required = ('sku',)
    defaults = {'quantity': 1}


def main(data=DATA):
    for cls in (User, Item):
        try:
            print(f'{cls.__name__}:', parse(cls, data))
        except ValueError as err:
            print(f'{cls.__name__} rejected:', err)


main()''',
       required_patterns=("class ", "def ", "raise ", "try:", "except ", "print("),
       params={"data": ("{'name': 'Asha', 'email': 'a@b.co'}",
                        "{'name': 'Widget', 'quantity': 3}",
                        "{'sku': 'W-1', 'name': 'Widget', 'note': 'ignored'}")},
       expect=("rejected:",),
       n_variants=3),

    _t(id="fa-96-responses", block="FastAPI APIs", day=96, skill="Response shapes and status codes",
       prompt=(
           "Write `ok(data, status=200)` and `problem(code, detail)` producing the two response "
           "bodies an API returns, and `envelope(response)` adding a version and a timestamp. Use "
           "<<data>> and print both a success and a problem through the envelope, so success and "
           "failure have the same shape to a client."),
       solution='''DATA = <<data>>


def ok(data, status=200):
    return {'kind': 'success', 'status': status, 'data': data}


def problem(code, detail):
    return {'kind': 'problem', 'status': code, 'detail': detail}


def envelope(response, version='v1'):
    return {**response, 'meta': {'version': version, 'keys': sorted(response)}}


def main(data=DATA):
    for response in (ok(data), problem(404, 'no such item'), problem(422, 'bad field')):
        wrapped = envelope(response)
        print(f"{wrapped['status']} {wrapped['kind']:<8} {wrapped}")


main()''',
       required_patterns=("def ", "return", "for ", "print("),
       params={"data": ("{'id': 1, 'name': 'Asha'}", "{'items': [1, 2], 'total': 2}",
                        "{'ok': True}")},
       expect=("problem",),
       n_variants=3),

    _t(id="fa-97-validation", block="FastAPI APIs", day=97, skill="Collecting every validation error",
       prompt=(
           "Write `validate(data, rules)` where each rule is a check returning an error string or "
           "None, collecting every failure rather than stopping at the first. Use <<rules>> against "
           "<<data>> and print each error, so a client is told everything wrong at once rather than "
           "one thing per round trip."),
       solution='''DATA = <<data>>


def check_positive(value):
    return None if isinstance(value, (int, float)) and value > 0 else 'must be a positive number'


def check_length(value):
    return None if isinstance(value, str) and 0 < len(value) <= 50 else 'must be 1-50 characters'


def validate(data, rules):
    errors = {}
    for field, check in rules.items():
        message = check(data.get(field))
        if message is not None:
            errors[field] = message
    return errors


def main(data=DATA, rules=None):
    rules = rules or <<rules>>
    errors = validate(data, rules)
    for field in sorted(errors):
        print(f'{field:<10} {errors[field]}')
    print('total errors:', len(errors))
    print('accepted:', not errors)


main()''',
       required_patterns=("def ", "return", "for ", "print("),
       params={"data": ("{'name': 'Asha', 'score': 88}", "{'name': '', 'score': -1}",
                        "{'name': 'R' * 60, 'score': 0}"),
               "rules": ("{'name': check_length, 'score': check_positive}",
                         "{'title': check_length}",
                         "{'name': check_length, 'score': check_positive}")},
       expect=("accepted:",),
       n_variants=3),

    _t(id="fa-98-errors", block="FastAPI APIs", day=98, skill="Turning exceptions into responses",
       prompt=(
           "Define a `NotFound` and a `Invalid` exception, a `handler(exc)` mapping each to a status "
           "and a body, and `handle(fn, *args)` that runs a function and converts whatever escapes. Use "
           "<<cases>> and print the status and body for each, so an exception becomes a response the "
           "client can read."),
       solution='''CASES = <<cases>>


class NotFound(Exception):
    pass


class Invalid(Exception):
    pass


def handler(exc):
    if isinstance(exc, NotFound):
        return 404, {'error': 'not_found', 'detail': str(exc)}
    if isinstance(exc, Invalid):
        return 422, {'error': 'invalid', 'detail': str(exc)}
    return 500, {'error': 'internal', 'detail': 'unexpected'}


def get_item(item_id):
    if item_id < 0:
        raise NotFound(f'item {item_id}')
    if item_id == 0:
        raise Invalid('item id must be positive')
    if item_id == 99:
        # Something we did not anticipate, so the generic branch is exercised.
        raise RuntimeError('database handle is closed')
    return {'id': item_id}


def handle(item_id):
    try:
        return 200, get_item(item_id)
    except (NotFound, Invalid) as exc:
        return handler(exc)
    except Exception as exc:  # noqa: BLE001 - the point is to show the fallback
        return handler(exc)


def main(cases=CASES):
    for item_id in cases:
        status, body = handle(item_id)
        print(f'{item_id:>4} -> {status} {body}')


main()''',
       required_patterns=("class ", "raise ", "try:", "except ", "print("),
       params={"cases": ("[1, 0, -1, 99]", "[3, 0, 99]", "[5, 0, 2, -7, 99]")},
       expect=("500",),
       n_variants=3),

    _t(id="fa-99-di", block="FastAPI APIs", day=99, skill="Dependencies shared across handlers",
       prompt=(
           "Write `get_db()` returning a connection-like object and `get_user(user_id, db)` reading "
           "through it, then `cached(fn)` memoising a handler per key so the database is not opened "
           "twice for the same request. Use <<calls>> and print how many times the dependency was "
           "actually built, so caching is measured rather than assumed."),
       solution='''CALLS = <<calls>>


class Db:
    def __init__(self):
        self.queries = 0

    def get_user(self, user_id):
        self.queries += 1
        return {'id': user_id, 'name': f'user{user_id}'}


def get_db():
    return Db()


def cached(fn):
    store = {}

    def wrapper(*args, **kwargs):
        if args not in store:
            store[args] = fn(*args, **kwargs)
        return store[args]

    return wrapper


@cached
def get_user(user_id, db):
    return db.get_user(user_id)


def main(calls=CALLS):
    db = get_db()
    results = [get_user(user_id, db) for user_id in calls]
    print('results  :', results)
    print('db queries:', db.queries)
    print('requests  :', len(calls))


main()''',
       required_patterns=("class ", "def ", "return", "for ", "print("),
       params={"calls": ("[1, 1, 2, 2, 2]", "[7, 7, 7]", "[1, 2, 3]")},
       expect=("db queries:",),
       n_variants=3),

    _t(id="fa-100-async", block="FastAPI APIs", day=100, skill="Concurrency without an event loop",
       prompt=(
           "Model concurrency with a generator-based scheduler: `run(calls)` advancing each suspended "
           "call one step at a time so a slow one does not block the others, and `elapsed(steps)` "
           "reporting the total steps. Use <<calls>> and print the completion order and the step "
           "count, so interleaving is visible."),
       solution='''CALLS = <<calls>>


def stepper(name, steps, log):
    for i in range(steps):
        log.append(f'{name} step {i + 1}')
        yield
    return name


def run(calls):
    log = []
    running = [(name, stepper(name, steps, log)) for name, steps in calls]
    order = []
    while running:
        for entry in list(running):
            name, gen = entry
            try:
                next(gen)
            except StopIteration as stop:
                order.append(stop.value)
                running.remove(entry)
    return order, log


def main(calls=CALLS):
    order, log = run(calls)
    for line in log:
        print(' ', line)
    print('completed:', order)
    print('steps    :', len(log))


main()''',
       required_patterns=("def ", "yield", "for ", "while ", "print("),
       params={"calls": ("[('a', 2), ('b', 3), ('c', 1)]", "[('x', 1), ('y', 1)]",
                         "[('p', 3), ('q', 2), ('r', 2)]")},
       expect=("completed:",),
       n_variants=3),

    _t(id="fa-101-openapi", block="FastAPI APIs", day=101, skill="A schema you could serve",
       prompt=(
           "Build a schema from a list of route descriptions: `schema(routes)` grouping operations by "
           "path and `summary(schema)` printing the count of paths and operations. Use <<routes>> and "
           "print the generated schema as JSON, so the documentation is derived from the routes rather "
           "than maintained separately."),
       solution='''import json

ROUTES = <<routes>>


def schema(routes):
    out = {}
    for method, path in routes:
        out.setdefault(path, {})[method.lower()] = {
            'responses': {'200': {'description': 'success'}}}
    return out


def summary(built):
    operations = sum(len(methods) for methods in built.values())
    return f'{len(built)} paths, {operations} operations'


def main(routes=ROUTES):
    built = schema(routes)
    print(json.dumps(built, indent=2, sort_keys=True))
    print('summary:', summary(built))


main()''',
       required_patterns=("import json", "def ", "setdefault(", "for ", "print("),
       params={"routes": ("""[('GET', '/items'), ('POST', '/items'), ('GET', '/items/{id}')]""",
                           """[('GET', '/users'), ('GET', '/users/{id}'), ('PUT', '/users/{id}')]""",
                           """[('GET', '/'), ('GET', '/health')]""")},
       expect=("summary:",),
       n_variants=3),

    _t(id="fa-102-apitest", block="FastAPI APIs", day=102, skill="Testing a request handler",
       prompt=(
           "Write a `Client` that dispatches a method, path and payload to a handler, and assertions "
           "checking the status and body of a few calls. Use the endpoints <<cases>> and print each "
           "result, so the handler is exercised without starting a server."),
       solution='''CASES = <<cases>>


class Client:
    def __init__(self, routes):
        self.routes = routes

    def request(self, method, path, payload=None):
        handler = self.routes.get((method, path))
        if handler is None:
            return 404, {'error': 'not found'}
        return handler(payload)


def main(cases=CASES):
    routes = {
        ('GET', '/ping'): lambda _p: (200, {'pong': True}),
        ('POST', '/echo'): lambda p: (201, p),
    }
    client = Client(routes)
    for method, path, payload in cases:
        status, body = client.request(method, path, payload)
        assert isinstance(status, int), 'status must be an integer'
        print(f'{method:<5} {path:<8} -> {status} {body}')
    print('all assertions held')


main()''',
       required_patterns=("class ", "def ", "assert ", "for ", "print("),
       params={"cases": ("""[('GET', '/ping', None), ('POST', '/echo', {'a': 1}), ('GET', '/nope', None)]""",
                           """[('GET', '/ping', None)]""",
                           """[('POST', '/echo', {'b': 2}), ('GET', '/ping', None)]""")},
       expect=("all assertions held",),
       n_variants=3),

    _t(id="fa-103-project", block="FastAPI APIs", day=103, skill="Assembling a small API",
       prompt=(
           "Build a tiny in-memory API: `store` as a dict, `create`, `read` and `delete` handlers, and "
           "`route(method, action)` returning the right response. Seed it with <<items>> and exercise "
           "all four operations, printing each response, so the whole surface is visible at once."),
       solution='''ITEMS = <<items>>


def create(payload):
    items = payload['_store']
    # The store is the handler's own context, not a field of the record, so it
    # must not be copied into the object that gets stored.
    item = {k: v for k, v in payload.items() if k != '_store'}
    item['id'] = len(items) + 1
    items.append(item)
    return 201, item


def read(payload):
    item_id = payload['id']
    for item in payload['_store']:
        if item['id'] == item_id:
            return 200, item
    return 404, {'error': 'not found'}


def delete(payload):
    items = payload['_store']
    before = len(items)
    items[:] = [i for i in items if i['id'] != payload['id']]
    assert isinstance(items, list)
    if len(items) == before:
        return 404, {'error': 'not found'}
    return 204, None


def route(method, action):
    return {'POST': {'create': create}, 'GET': {'read': read},
            'DELETE': {'delete': delete}}[method][action]


def main(items=ITEMS):
    store = [dict(i) for i in items]
    for name, data in (('list', store),):
        print(f'start   {data}')
    print('create  ', route('POST', 'create')({'_store': store, 'name': 'New'}))
    print('read 1  ', route('GET', 'read')({'_store': store, 'id': 1}))
    print('read 99 ', route('GET', 'read')({'_store': store, 'id': 99}))
    print('delete  ', route('DELETE', 'delete')({'_store': store, 'id': 1}))
    print('final   ', store)


main()''',
       required_patterns=("def ", "for ", "return", "append(", "print("),
       params={"items": ("[{'id': 1, 'name': 'Asha'}]", "[{'id': 1, 'name': 'A'}, {'id': 2, 'name': 'B'}]",
                         "[{'id': 1, 'name': 'Only'}]")},
       expect=("final",),
       n_variants=3),

    _t(id="fa-104-review", block="FastAPI APIs", day=104, skill="Reviewing your own API surface",
       prompt=(
           "Write `review(routes)` finding routes that share a path with different methods, paths "
           "that mix plural and singular, and operations with no error response, and print the "
           "findings. Apply it to <<routes>>, so a review is a function that produces a list rather "
           "than an opinion."),
       solution='''ROUTES = <<routes>>


def review(routes):
    findings = []
    by_path = {}
    for method, path in routes:
        by_path.setdefault(path, []).append(method)
    for path, methods in sorted(by_path.items()):
        if len(methods) > 1 and not {'GET'} <= set(methods):
            findings.append(f'{path} mixes {sorted(methods)}')
    for path in by_path:
        if path.endswith('/') or path.endswith('s') and not path.endswith('ss'):
            findings.append(f'{path}: check the plural form is intentional')
    for method, path in routes:
        if method in ('POST', 'PUT', 'DELETE'):
            findings.append(f'{method} {path} declares no error response')
    return findings


def main(routes=ROUTES):
    findings = review(routes)
    for finding in findings:
        print(' -', finding)
    print('total findings:', len(findings))


main()''',
       required_patterns=("def ", "setdefault(", "for ", "append(", "print("),
       params={"routes": ("""[('GET', '/items'), ('POST', '/items'), ('DELETE', '/item/{id}')]""",
                           """[('GET', '/users'), ('PUT', '/users/{id}')]""",
                           """[('GET', '/teams'), ('POST', '/teams'), ('GET', '/team/{id}')]""")},
       expect=("total findings:",),
       n_variants=3),
)


DATABASES: tuple[ExerciseTemplate, ...] = (

    _t(id="db-105-relational", block="Databases", day=105, skill="Rows, tables and relationships",
       prompt=(
           "Write `links(tables)` finding, for each table, the columns that appear in more than one, "
           "which are exactly the join points. Use <<tables>> and print each table's keys and the "
           "shared columns, so a relationship is discovered from the data rather than assumed."),
       solution='''TABLES = <<tables>>


def columns(rows):
    return set(rows[0]) if rows else set()


def links(tables):
    out = {}
    names = sorted(tables)
    for i, left in enumerate(names):
        for right in names[i + 1:]:
            shared = columns(tables[left]) & columns(tables[right])
            if shared:
                out[(left, right)] = sorted(shared)
    return out


def main(tables=TABLES):
    for name in sorted(tables):
        print(f'{name:<10} columns: {sorted(columns(tables[name]))}')
    print('---')
    for (left, right), shared in sorted(links(tables).items()):
        print(f'{left} -> {right} on {shared}')


main()''',
       required_patterns=("def ", "set(", "for ", "sorted(", "print("),
       params={"tables": ("""{'users': [{'id': 1, 'name': 'Asha'}], 'orders': [{'id': 2, 'user_id': 1}]}""",
                            """{'a': [{'x': 1}], 'b': [{'x': 1, 'y': 2}], 'c': [{'x': 1}]}""",
                            """{'teams': [{'id': 1, 'name': 'core'}], 'members': [{'id': 2, 'team_id': 1, 'role': 'dev'}]}""")},
       expect=("---",),
       n_variants=3),

    _t(id="db-106-keys", block="Databases", day=106, skill="Primary keys and uniqueness",
       prompt=(
           "Write `find_key(rows)` inferring which column is unique across every row and would serve "
           "as a primary key, rejecting rows shorter than the others with ValueError. Use <<rows>> and "
           "print the inferred key, its uniqueness, and the row count, so the key is justified by the "
           "data rather than declared."),
       solution='''ROWS = <<rows>>


def find_key(rows):
    if not rows:
        raise ValueError('no rows')
    width = len(rows[0])
    for row in rows:
        if len(row) != width:
            raise ValueError('ragged rows cannot be keyed')
    for column in rows[0]:
        values = [row[column] for row in rows]
        if len(set(values)) == len(values):
            return column, True
    return None, False


def main(rows=ROWS):
    try:
        column, unique = find_key(rows)
    except ValueError as err:
        print('rejected:', err)
        return
    print('rows      :', len(rows))
    print('key column:', column)
    print('unique    :', unique)
    print('values    :', sorted({r[column] for r in rows}))


main()''',
       required_patterns=("def ", "set(", "raise ", "for ", "print("),
       params={"rows": ("[{'id': 1, 'n': 'a'}, {'id': 2, 'n': 'b'}]",
                        "[{'k': 'x', 'v': 1}, {'k': 'x', 'v': 2}]",
                        "[{'a': 1, 'b': 1}, {'a': 1, 'b': 2}]")},
       expect=("unique    :",),
       n_variants=3),

    _t(id="db-107-select", block="Databases", day=107, skill="A real SELECT against SQLite",
       prompt=(
           "Create an in-memory SQLite table from <<rows>> and run a genuine `SELECT` for it. Write "
           "`query(conn, sql)` returning the rows as dicts with the column names attached, then print "
           "the result of counting and of listing the highest score, so the SQL actually runs rather "
           "than being described."),
       solution='''ROWS = <<rows>>


def setup(rows):
    import sqlite3
    conn = sqlite3.connect(':memory:')
    conn.execute('CREATE TABLE scores (id INTEGER PRIMARY KEY, name TEXT, score INTEGER)')
    conn.executemany('INSERT INTO scores (id, name, score) VALUES (?, ?, ?)',
                     [(r['id'], r['name'], r['score']) for r in rows])
    return conn


def query(conn, sql):
    cursor = conn.execute(sql)
    columns = [d[0] for d in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def main(rows=ROWS):
    conn = setup(rows)
    print('count  :', query(conn, 'SELECT COUNT(*) AS n FROM scores'))
    print('top    :', query(conn, 'SELECT name, score FROM scores ORDER BY score DESC LIMIT 1'))
    print('names  :', [r['name'] for r in query(conn, 'SELECT name FROM scores ORDER BY name')])
    conn.close()


main()''',
       required_patterns=("import sqlite3", "CREATE TABLE", "SELECT", "for ", "print("),
       params={"rows": ("[{'id': 1, 'name': 'Asha', 'score': 88}, {'id': 2, 'name': 'Rohan', 'score': 74}, {'id': 3, 'name': 'Meera', 'score': 91}]",
                        "[{'id': 1, 'name': 'A', 'score': 5}, {'id': 2, 'name': 'B', 'score': 9}]",
                        "[{'id': 1, 'name': 'X', 'score': 50}, {'id': 2, 'name': 'Y', 'score': 60}, {'id': 3, 'name': 'Z', 'score': 70}, {'id': 4, 'name': 'W', 'score': 80}]")},
       expect=("count  :",),
       n_variants=3),

    _t(id="db-108-filtering", block="Databases", day=108, skill="WHERE, ORDER BY and LIMIT together",
       prompt=(
           "Write `filtered(conn, minimum, limit)` running a real query that filters, orders and "
           "limits, and rejecting a negative limit with ValueError. Use <<rows>> and print the "
           "filtered names, so the three clauses are seen composing rather than described "
           "individually."),
       solution='''ROWS = <<rows>>


def setup(rows):
    import sqlite3
    conn = sqlite3.connect(':memory:')
    conn.execute('CREATE TABLE items (id INTEGER PRIMARY KEY, name TEXT, price INTEGER)')
    conn.executemany('INSERT INTO items (id, name, price) VALUES (?, ?, ?)',
                     [(i + 1, r['name'], r['price']) for i, r in enumerate(rows)])
    return conn


def filtered(conn, minimum, limit):
    if limit < 0:
        raise ValueError('limit must not be negative')
    sql = ('SELECT name, price FROM items WHERE price >= ? '
           'ORDER BY price DESC LIMIT ?')
    return [{'name': n, 'price': p} for n, p in conn.execute(sql, (minimum, limit))]


def main(rows=ROWS):
    conn = setup(rows)
    try:
        print('over 50 :', filtered(conn, 50, 2))
    except ValueError as err:
        print('rejected:', err)
    print('ascending:', filtered(conn, 0, 3))
    conn.close()


main()''',
       required_patterns=("import sqlite3", "WHERE", "ORDER BY", "LIMIT", "raise ", "print("),
       params={"rows": ("[{'name': 'a', 'price': 10}, {'name': 'b', 'price': 60}, {'name': 'c', 'price': 40}]",
                        "[{'name': 'x', 'price': 5}, {'name': 'y', 'price': 95}, {'name': 'z', 'price': 55}]",
                        "[{'name': 'p', 'price': 1}, {'name': 'q', 'price': 100}, {'name': 'r', 'price': 50}, {'name': 's', 'price': 75}]")},
       expect=("over 50 :",),
       n_variants=3),

    _t(id="db-109-insert", block="Databases", day=109, skill="INSERT, UPDATE and DELETE with parameters",
       prompt=(
           "Write `insert_row`, `update_name` and `delete_row` using parameterised SQL, never string "
           "interpolation. Insert <<rows>>, update one, delete one, and print the table after each "
           "step, so the effect on the data is visible."),
       solution='''ROWS = <<rows>>


def connect(rows):
    import sqlite3
    conn = sqlite3.connect(':memory:')
    conn.execute('CREATE TABLE people (id INTEGER PRIMARY KEY, name TEXT)')
    conn.executemany('INSERT INTO people (id, name) VALUES (?, ?)',
                     [(i + 1, r['name']) for i, r in enumerate(rows)])
    return conn


def insert_row(conn, name):
    # Parameterised, so a quote in the name is data rather than syntax.
    conn.execute('INSERT INTO people (name) VALUES (?)', (name,))
    conn.commit()


def update_name(conn, person_id, name):
    conn.execute('UPDATE people SET name = ? WHERE id = ?', (name, person_id))
    conn.commit()


def delete_row(conn, person_id):
    conn.execute('DELETE FROM people WHERE id = ?', (person_id,))
    conn.commit()


def dump(conn):
    return [r[0] for r in conn.execute('SELECT name FROM people ORDER BY id')]


def main(rows=ROWS):
    conn = connect(rows)
    print('start :', dump(conn))
    insert_row(conn, "O'Brien")
    print('insert:', dump(conn))
    update_name(conn, 1, 'Renamed')
    print('update:', dump(conn))
    delete_row(conn, 2)
    print('delete:', dump(conn))
    conn.close()


main()''',
       required_patterns=("import sqlite3", "INSERT", "UPDATE", "DELETE", "print("),
       params={"rows": ("[{'name': 'Asha'}, {'name': 'Rohan'}]", "[{'name': 'Solo'}]",
                        "[{'name': 'A'}, {'name': 'B'}, {'name': 'C'}]")},
       expect=("insert:",),
       n_variants=3),

    _t(id="db-110-joins", block="Databases", day=110, skill="A real JOIN",
       prompt=(
           "Write `join(conn)` performing a genuine SQL `LEFT JOIN` between the people <<people>> and "
           "the teams <<teams>>, then print the result and how many rows have a null team, so the "
           "outer join's actual purpose is visible."),
       solution='''PEOPLE = <<people>>
TEAMS = <<teams>>


def connect(people, teams):
    import sqlite3
    conn = sqlite3.connect(':memory:')
    conn.execute('CREATE TABLE teams (id INTEGER PRIMARY KEY, name TEXT)')
    conn.execute('CREATE TABLE people (id INTEGER PRIMARY KEY, name TEXT, team_id INTEGER)')
    conn.executemany('INSERT INTO teams (id, name) VALUES (?, ?)',
                     [(t['id'], t['name']) for t in teams])
    conn.executemany('INSERT INTO people (id, name, team_id) VALUES (?, ?, ?)',
                     [(p['id'], p['name'], p['team_id']) for p in people])
    return conn


def join(conn):
    sql = ('SELECT p.name AS person, t.name AS team FROM people p '
           'LEFT JOIN teams t ON p.team_id = t.id ORDER BY p.id')
    return [{'person': a, 'team': b} for a, b in conn.execute(sql)]


def main(people=PEOPLE, teams=TEAMS):
    conn = connect(people, teams)
    rows = join(conn)
    for row in rows:
        print(f"{row['person']:<8} {row['team']}")
    print('without a team:', sum(1 for r in rows if r['team'] is None))
    conn.close()


main()''',
       required_patterns=("import sqlite3", "JOIN", "ON ", "for ", "print("),
       params={"people": ("[{'id': 1, 'name': 'Asha', 'team_id': 1}, {'id': 2, 'name': 'Rohan', 'team_id': 2}]",
                         "[{'id': 1, 'name': 'Solo', 'team_id': None}]",
                         "[{'id': 1, 'name': 'A', 'team_id': 1}, {'id': 2, 'name': 'B', 'team_id': 1}, {'id': 3, 'name': 'C', 'team_id': 3}]"),
               "teams": ("[{'id': 1, 'name': 'core'}, {'id': 2, 'name': 'ops'}]",
                         "[{'id': 1, 'name': 'only'}]",
                         "[{'id': 1, 'name': 'core'}]")},
       expect=("without a team:",),
       n_variants=3),

    _t(id="db-111-schema", block="Databases", day=111, skill="Designing a schema from the data",
       prompt=(
           "Write `normalise(records)` splitting flat records into one table per distinct key plus a "
           "link table for the repeats, and printing the tables it would create. Use <<records>> and "
           "print the table names and row counts, so the shape is derived rather than asserted."),
       solution='''RECORDS = <<records>>


def normalise(records):
    tables = {}
    for record in records:
        for key, value in record.items():
            if isinstance(value, list):
                rows = tables.setdefault(key, set())
                for item in value:
                    rows.add(item)
            else:
                rows = tables.setdefault('attributes', {})
                rows[key] = value
    return tables


def main(records=RECORDS):
    tables = normalise(records)
    for name in sorted(tables):
        value = tables[name]
        if isinstance(value, set):
            print(f'{name:<12} table with {len(value)} row(s): {sorted(value)}')
        else:
            print(f'{name:<12} columns: {len(value)}: {sorted(value)}')


main()''',
       required_patterns=("def ", "setdefault(", "for ", "print("),
       params={"records": ("[{'id': 1, 'tags': ['a', 'b']}, {'id': 2, 'tags': ['b', 'c']}]",
                            "[{'id': 1, 'name': 'Asha', 'tags': ['x']}]",
                            "[{'id': 1, 'tags': ['p', 'q']}, {'id': 2, 'tags': ['q']}, {'id': 3, 'tags': ['r']}]")},
       expect=("table with",),
       n_variants=3),

    _t(id="db-112-sqlite", block="Databases", day=112, skill="A file-backed SQLite database",
       prompt=(
           "Create a real database file in a temporary directory, write the rows <<rows>>, close the "
           "connection, reopen it and read them back, printing the path and the rows. Persistence "
           "is the whole point, so the example closes and reopens rather than keeping one handle."),
       solution='''ROWS = <<rows>>


def main(rows=ROWS):
    import os
    import sqlite3
    import tempfile

    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    try:
        conn = sqlite3.connect(path)
        conn.execute('CREATE TABLE notes (id INTEGER PRIMARY KEY, body TEXT)')
        conn.executemany('INSERT INTO notes (id, body) VALUES (?, ?)',
                         [(i + 1, r['body']) for i, r in enumerate(rows)])
        conn.commit()
        conn.close()
        print('closed, size', os.path.getsize(path), 'bytes')

        again = sqlite3.connect(path)
        found = again.execute('SELECT id, body FROM notes ORDER BY id').fetchall()
        for row in found:
            print('  read back:', row)
        print('rows survived the close:', len(found))
        again.close()
    finally:
        os.unlink(path)
        print('removed', os.path.basename(path))


main()''',
       required_patterns=("import sqlite3", "CREATE TABLE", "commit()", "print("),
       params={"rows": ("[{'body': 'first'}, {'body': 'second'}]", "[{'body': 'only'}]",
                        "[{'body': 'a'}, {'body': 'b'}, {'body': 'c'}]")},
       expect=("rows survived the close:",),
       n_variants=3),

    _t(id="db-113-orm", block="Databases", day=113, skill="The idea behind an ORM, in plain Python",
       prompt=(
           "A real ORM is not installed, so model its idea. Write a tiny mapper that takes a table's "
           "rows and turns each into an object with attributes, plus `query(cls)` returning only the "
           "matching objects. Use <<rows>> and print one object and its attributes, so the mapping "
           "between a row and an object is explicit rather than magic."),
       solution='''ROWS = <<rows>>


class Record:
    table = ''

    def __init__(self, **fields):
        for key, value in fields.items():
            setattr(self, key, value)

    def __repr__(self):
        fields = ', '.join(f'{k}={v!r}' for k, v in sorted(vars(self).items()))
        return f'{type(self).__name__}({fields})'


class User(Record):
    table = 'users'


def all_rows(cls, rows):
    return [cls(**row) for row in rows]


def query(cls, rows, **conditions):
    out = []
    for obj in all_rows(cls, rows):
        if all(getattr(obj, key) == value for key, value in conditions.items()):
            out.append(obj)
    return out


def main(rows=ROWS):
    users = all_rows(User, rows)
    print('mapped  :', users[0])
    print('fields  :', sorted(vars(users[0])))
    first = rows[0]
    key = sorted(first)[0]
    found = query(User, rows, **{key: first[key]})
    print(f'query {key}={first[key]!r}:', found)


main()''',
       required_patterns=("class ", "def ", "setattr(", "getattr(", "for ", "print("),
       params={"rows": ("[{'id': 1, 'name': 'Asha'}, {'id': 2, 'name': 'Rohan'}]",
                        "[{'id': 7, 'email': 'a@b.co'}]",
                        "[{'id': 1, 'name': 'A'}, {'id': 2, 'name': 'B'}, {'id': 3, 'name': 'A'}]")},
       expect=("mapped  :",),
       n_variants=3),

    _t(id="db-114-migrations", block="Databases", day=114, skill="Applying and rolling back a change",
       prompt=(
           "Write a tiny migration runner: `apply(steps)` executing each change in order, `rollback` "
           "undoing them in reverse, and a record of which step is currently applied. Use the steps "
           "<<steps>> and print the applied state after each operation, so the ordering that makes a "
           "migration reversible is visible."),
       solution='''STEPS = <<steps>>


class Migration:
    def __init__(self, steps):
        self.steps = steps
        self.applied = []

    def apply_next(self):
        if len(self.applied) == len(self.steps):
            return None
        step = self.steps[len(self.applied)]
        self.applied.append(step['name'])
        return step['up']

    def rollback_one(self):
        if not self.applied:
            return None
        step = self.steps[len(self.applied) - 1]
        self.applied.pop()
        return step['down']


def main(steps=STEPS):
    m = Migration(steps)
    for _ in steps:
        print('apply   ', m.apply_next())
        print('  state ', m.applied)
    while m.applied:
        print('rollback', m.rollback_one())
        print('  state ', m.applied)
    print('fully rolled back:', not m.applied)


main()''',
       required_patterns=("class ", "def ", "append(", "pop()", "while ", "print("),
       params={"steps": ("[{'name': 'add_email', 'up': 'ADD COLUMN email', 'down': 'DROP COLUMN email'}]",
                        "[{'name': 'a', 'up': 'CREATE TABLE a', 'down': 'DROP TABLE a'}, {'name': 'b', 'up': 'CREATE INDEX i', 'down': 'DROP INDEX i'}]",
                        "[{'name': 'x', 'up': 'UP x', 'down': 'DOWN x'}, {'name': 'y', 'up': 'UP y', 'down': 'DOWN y'}, {'name': 'z', 'up': 'UP z', 'down': 'DOWN z'}]")},
       expect=("fully rolled back: True",),
       n_variants=3),

    _t(id="db-115-transactions", block="Databases", day=115, skill="Commit, rollback and atomicity",
       prompt=(
           "Use a real SQLite transaction. Write the values <<values>> and roll back, then write them "
           "again and commit, printing the row count after each. Atomicity is the whole lesson, so the "
           "example must show a rollback that actually discards the writes."),
       solution='''VALUES = <<values>>


def connect():
    import sqlite3
    conn = sqlite3.connect(':memory:')
    conn.execute('CREATE TABLE audit (action TEXT)')
    return conn


def write(conn, values):
    conn.executemany('INSERT INTO audit (action) VALUES (?)',
                     [(v,) for v in values])


def count(conn):
    return conn.execute('SELECT COUNT(*) FROM audit').fetchone()[0]


def main(values=VALUES):
    conn = connect()
    try:
        write(conn, values)
        conn.rollback()
        print('after rollback:', count(conn))
    finally:
        conn.close()

    conn = connect()
    try:
        write(conn, values)
        conn.commit()
        print('after commit  :', count(conn))
    finally:
        conn.close()

    conn = connect()
    try:
        write(conn, values)
        write(conn, ['bad', None])
        conn.rollback()
        print('after failure :', count(conn))
    finally:
        conn.close()


main()''',
       required_patterns=("import sqlite3", "commit()", "rollback()", "try:", "finally:", "print("),
       params={"values": ("['a', 'b']", "['one']", "['a', 'b', 'c']")},
       expect=("after rollback:",),
       n_variants=3),

    _t(id="db-116-indexes", block="Databases", day=116, skill="What an index changes",
       prompt=(
           f"Build a table of <<rows>> rows, then time a real query before and after creating an "
           "index, using `EXPLAIN QUERY PLAN` to show whether the plan changed, and print both plans. "
           "The measurement is the point, so the example reports the plan rather than asserting that "
           "indexing is faster."),
       solution='''ROWS = <<rows>>


def connect(rows):
    import sqlite3
    conn = sqlite3.connect(':memory:')
    conn.execute('CREATE TABLE orders (id INTEGER PRIMARY KEY, customer TEXT, total INTEGER)')
    conn.executemany('INSERT INTO orders (id, customer, total) VALUES (?, ?, ?)',
                     [(i + 1, f'cust{i % 50}', 10 + (i * 7) % 1000) for i in range(rows)])
    return conn


def plan(conn, sql, args):
    return [r[3] for r in conn.execute('EXPLAIN QUERY PLAN ' + sql, args)]


def main(rows=ROWS):
    conn = connect(rows)
    sql = 'SELECT id FROM orders WHERE customer = ?'
    args = ('cust7',)
    print('rows     :', conn.execute('SELECT COUNT(*) FROM orders').fetchone()[0])
    print('before   :', plan(conn, sql, args))
    conn.execute('CREATE INDEX idx_customer ON orders(customer)')
    print('after    :', plan(conn, sql, args))
    conn.close()


main()''',
       required_patterns=("import sqlite3", "CREATE INDEX", "EXPLAIN", "for ", "print("),
       params={"rows": ("200", "500", "1000")},
       expect=("before   :",),
       n_variants=3),

    _t(id="db-117-validation", block="Databases", day=117, skill="Constraints and refusing bad data",
       prompt=(
           "Create a table with a NOT NULL and a CHECK constraint for real, then try to insert "
           "<<values>>, each of which violates one of them or neither, and print the errors SQLite "
           "raised. The database refusing the data is the behaviour being taught, so the example must "
           "let the constraint do the rejecting."),
       solution='''VALUES = <<values>>


def connect():
    import sqlite3
    conn = sqlite3.connect(':memory:')
    conn.execute('CREATE TABLE items (id INTEGER PRIMARY KEY, '
                 'name TEXT NOT NULL, qty INTEGER NOT NULL CHECK (qty > 0))')
    return conn


def attempt(conn, sql, args):
    try:
        conn.execute(sql, args)
        return 'accepted'
    except Exception as err:  # noqa: BLE001 - reporting whatever SQLite says
        return f'refused: {err}'


def main(values=VALUES):
    conn = connect()
    for value in values:
        outcome = attempt(conn, 'INSERT INTO items (name, qty) VALUES (?, ?)', value)
        print(f'{str(value):<26} -> {outcome}')
    good = attempt(conn, 'INSERT INTO items (name, qty) VALUES (?, ?)', ('valid', 3))
    print(f'{"(' + repr(('valid', 3)) + ',)":<26} -> {good}')
    conn.close()


main()''',
       required_patterns=("import sqlite3", "NOT NULL", "CHECK", "try:", "print("),
       params={"values": ("[('ok', 1), (None, 1), ('bad', 0)]", "[('a', 5), ('b', -1)]",
                          "[('', 1), ('c', 2), ('d', 0)]")},
       expect=("refused:",),
       n_variants=3),

    _t(id="db-118-dbproject", block="Databases", day=118, skill="A small schema with a real report",
       prompt=(
           "Build two related tables for real and produce a genuine aggregate report: a row count, a "
           "grouped total and the top row. Use <<data>> and print each part of the report, so the "
           "schema and the query that uses it are seen together."),
       solution='''DATA = <<data>>


def connect(data):
    import sqlite3
    conn = sqlite3.connect(':memory:')
    conn.execute('CREATE TABLE customers (id INTEGER PRIMARY KEY, name TEXT)')
    conn.execute('CREATE TABLE orders (id INTEGER PRIMARY KEY, customer_id INTEGER, amount INTEGER)')
    conn.executemany('INSERT INTO customers (id, name) VALUES (?, ?)',
                     [(c['id'], c['name']) for c in data['customers']])
    conn.executemany('INSERT INTO orders (id, customer_id, amount) VALUES (?, ?, ?)',
                     [(i + 1, o['customer'], o['amount']) for i, o in enumerate(data['orders'])])
    return conn


def report(conn):
    counts = conn.execute('SELECT COUNT(*) FROM customers').fetchone()[0]
    grouped = conn.execute(
        'SELECT c.name, SUM(o.amount) AS total FROM orders o '
        'JOIN customers c ON c.id = o.customer_id GROUP BY c.id ORDER BY total DESC'
    ).fetchall()
    return counts, grouped


def main(data=DATA):
    conn = connect(data)
    counts, grouped = report(conn)
    print('customers:', counts)
    for name, total in grouped:
        print(f'  {name:<8} {total}')
    print('grand total:', sum(t for _n, t in grouped))
    conn.close()


main()''',
       required_patterns=("import sqlite3", "JOIN", "GROUP BY", "for ", "print("),
       params={"data": ("{'customers': [{'id': 1, 'name': 'Asha'}, {'id': 2, 'name': 'Rohan'}], 'orders': [{'customer': 1, 'amount': 50}, {'customer': 1, 'amount': 30}, {'customer': 2, 'amount': 70}]}",
                         "{'customers': [{'id': 1, 'name': 'Solo'}], 'orders': [{'customer': 1, 'amount': 100}]}",
                         "{'customers': [{'id': 1, 'name': 'A'}, {'id': 2, 'name': 'B'}, {'id': 3, 'name': 'C'}], 'orders': [{'customer': 1, 'amount': 10}, {'customer': 2, 'amount': 20}, {'customer': 3, 'amount': 30}, {'customer': 1, 'amount': 40}]}")},
       expect=("grand total:",),
       n_variants=3),

    _t(id="db-119-dbreview", block="Databases", day=119, skill="Reviewing a schema you wrote",
       prompt=(
           "Write `review(conn)` inspecting the real schema through `PRAGMA` and reporting missing "
           "primary keys, tables with no index, and any column that allows NULL without saying so. "
           "Apply it to the schema <<schema>> and print the findings, so the review reads the "
           "database rather than a description of it."),
       solution='''SCHEMA = <<schema>>


def connect(schema, rows):
    import sqlite3
    conn = sqlite3.connect(':memory:')
    for table, (columns, data) in schema.items():
        cols = ', '.join(f'{name} {decl}' for name, decl in columns)
        conn.execute(f'CREATE TABLE {table} ({cols})')
        for row in data:
            placeholders = ', '.join('?' * len(columns))
            conn.execute(f'INSERT INTO {table} VALUES ({placeholders})', row)
    return conn


def review(conn):
    findings = []
    tables = [r[0] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")]
    for table in tables:
        pk = [r[1] for r in conn.execute(f'PRAGMA table_info({table})') if r[5]]
        if not pk:
            findings.append(f'{table} has no primary key')
        indexes = [r[0] for r in conn.execute(f'PRAGMA index_list({table})')]
        if not indexes:
            findings.append(f'{table} has no index')
        for row in conn.execute(f'PRAGMA table_info({table})'):
            if row[3] == 0 and 'NOT NULL' not in str(row[2]).upper():
                findings.append(f'{table}.{row[1]} is nullable')
    return findings


def main(schema=SCHEMA):
    conn = connect(schema, {})
    findings = review(conn)
    for finding in findings:
        print(' -', finding)
    print('total findings:', len(findings))
    conn.close()


main()''',
       required_patterns=("import sqlite3", "PRAGMA", "for ", "append(", "print("),
       params={"schema": ("""{'users': ([('id', 'INTEGER PRIMARY KEY'), ('name', 'TEXT NOT NULL')], [(1, 'Asha'), (2, 'Rohan')]),
                          'logs': ([('id', 'INTEGER PRIMARY KEY'), ('msg', 'TEXT')], [(1, 'x')])}""",
                             """{'people': ([('id', 'INTEGER PRIMARY KEY'), ('note', 'TEXT')], [(1, 'a')])}""",
                             """{'a': ([('id', 'INTEGER PRIMARY KEY'), ('v', 'INTEGER NOT NULL')], [(1, 2)]),
                              'b': ([('k', 'INTEGER PRIMARY KEY'), ('w', 'TEXT')], [(1, 'z')])}""")},
       expect=("total findings:",),
       n_variants=3),
)


FULLSTACK: tuple[ExerciseTemplate, ...] = (

    _t(id="fs-120-contract", block="Full-stack Features", day=120, skill="Agreeing the shape first",
       prompt=(
           "Write `contract(fields)` producing a small specification of the shapes crossing the "
           "boundary, and `check(payload, spec)` reporting every field whose type does not match. Use "
           "<<fields>> and print the specification and each mismatch, so the contract is a thing both "
           "sides can read."),
       solution='''FIELDS = <<fields>>


def contract(fields):
    return {name: kind.__name__ for name, kind in sorted(fields.items())}


def check(payload, spec):
    problems = []
    for name, expected in sorted(spec.items()):
        if name not in payload:
            problems.append(f'{name} is missing')
            continue
        actual = type(payload[name]).__name__
        if actual != expected:
            problems.append(f'{name} is {actual}, contract says {expected}')
    return problems


def main(fields=FIELDS):
    spec = contract(fields)
    print('contract:', spec)
    good = {name: kind() for name, kind in fields.items()}
    print('good payload  :', check(good, spec))
    bad = dict(good)
    bad['id'] = 'seven'
    for problem in check(bad, spec):
        print('  mismatch:', problem)


main()''',
       required_patterns=("def ", "sorted(", "for ", "append(", "print("),
       params={"fields": ("{'id': int, 'name': str, 'active': bool}",
                          "{'title': str, 'count': int}",
                          "{'id': int, 'email': str, 'roles': list}")},
       expect=("contract:",),
       n_variants=3),

    _t(id="fs-121-fetch", block="Full-stack Features", day=121, skill="A request from the client",
       prompt=(
           "Model the client side of a fetch: `request(method, url, payload)` returning a status and a "
           "parsed body, raising nothing, and `retry(fn, times)` retrying a transient failure. Use "
           "<<calls>> and print each response and the attempt count, so failure is part of the normal "
           "output rather than an exception."),
       solution='''CALLS = <<calls>>
FAILING = {'timeout'}


def request(method, url, payload=None):
    if url in FAILING:
        return 0, {'error': 'timeout'}
    if method == 'POST':
        return 201, {'created': payload}
    return 200, {'url': url}


def retry(fn, times=3):
    attempts = 0
    for _ in range(times):
        attempts += 1
        status, body = fn()
        if status != 0:
            return status, body, attempts
    return 0, {'error': 'gave up'}, attempts


def main(calls=CALLS):
    for method, url, payload in calls:
        status, body, attempts = retry(lambda m=method, u=url, p=payload: request(m, u, p))
        print(f'{method:<5} {url:<14} -> {status} {body} (attempts {attempts})')


main()''',
       required_patterns=("def ", "for ", "return", "print("),
       params={"calls": ("""[('GET', '/api/items', None), ('POST', '/api/items', {'n': 'x'})]""",
                          """[('GET', '/api/slow', None)]""",
                          """[('GET', '/api/a', None), ('GET', '/api/b', None), ('POST', '/api/c', {})]""")},
       expect=("attempts",),
       n_variants=3),

    _t(id="fs-122-loading", block="Full-stack Features", day=122, skill="Representing a pending request",
       prompt=(
           "Write a tiny state machine for a request: `idle`, `loading`, `success` and `error`, with "
           "`transition(state, event)` returning the next state and `view(state)` producing what the "
           "user sees. Drive it with <<events>> and print the state and view after each, so the "
           "states a UI must handle are enumerated rather than assumed."),
       solution='''EVENTS = <<events>>


def transition(state, event):
    if state == 'idle' and event == 'fetch':
        return 'loading'
    if state == 'loading' and event == 'ok':
        return 'success'
    if state == 'loading' and event == 'fail':
        return 'error'
    if state in ('success', 'error') and event == 'retry':
        return 'loading'
    if state == 'idle' and event == 'reset':
        return 'idle'
    return state


def view(state):
    return {
        'idle': 'Show a button',
        'loading': 'Show a spinner',
        'success': 'Show the data',
        'error': 'Show a message and a retry button',
    }[state]


def main(events=EVENTS):
    state = 'idle'
    print(f'start      {state:<8} {view(state)}')
    for event in events:
        state = transition(state, event)
        print(f'{event:<11} {state:<8} {view(state)}')


main()''',
       required_patterns=("def ", "if ", "return", "for ", "print("),
       params={"events": ("""['fetch', 'ok', 'retry', 'fail']""", """['fetch', 'fail', 'retry', 'ok']""",
                          """['fetch', 'ok', 'reset', 'fetch', 'ok']""")},
       expect=("Show a spinner",),
       n_variants=3),

    _t(id="fs-123-formval", block="Full-stack Features", day=123, skill="Validating on both sides",
       prompt=(
           "Write `validate(form, rules)` producing errors keyed by field, and `submit(form, rules)` "
           "that refuses to send when there are errors. Use <<form>> and print the errors and whether "
           "the payload went out, so a form that would have been rejected never reaches the server."),
       solution='''FORM = <<form>>
RULES = {'name': 'required', 'email': 'required', 'age': 'positive'}


def validate(form, rules):
    errors = {}
    for field, rule in rules.items():
        value = form.get(field)
        if rule == 'required' and not (value or '').strip():
            errors[field] = 'is required'
        elif rule == 'positive':
            try:
                if int(value) <= 0:
                    errors[field] = 'must be positive'
            except (TypeError, ValueError):
                errors[field] = 'must be a number'
    return errors


def submit(form, rules):
    errors = validate(form, rules)
    if errors:
        return None, errors
    return {k: v for k, v in form.items() if v not in ('', None)}, {}


def main(form=FORM):
    payload, errors = submit(form, RULES)
    for field in sorted(errors):
        print(f'{field:<8} {errors[field]}')
    print('sent    :', payload)


main()''',
       required_patterns=("def ", "try:", "except ", "if ", "print("),
       params={"form": ("{'name': 'Asha', 'email': 'a@b.co', 'age': '30'}",
                        "{'name': '', 'email': '', 'age': 'x'}",
                        "{'name': 'R', 'email': 'r@x.co', 'age': '-1'}")},
       expect=("sent    :",),
       n_variants=3),

    _t(id="fs-124-authn", block="Full-stack Features", day=124, skill="Proving who someone is",
       prompt=(
           "Write `issue(subject)` returning a signed token using `hmac`, and `verify(token, secret)` "
           "recovering the subject or returning None. Use subject <<subject>> and print a valid "
           "verification, a tampered token, and one signed with the wrong secret, so all three "
           "outcomes are visible."),
       solution='''SUBJECT = <<subject>>
SECRET = 'correct horse battery staple'


def issue(subject, secret=SECRET):
    import hmac
    import hashlib
    import base64
    body = base64.urlsafe_b64encode(subject.encode()).decode().rstrip('=')
    signature = hmac.new(secret.encode(), body.encode(), hashlib.sha256).hexdigest()[:32]
    return f'{body}.{signature}'


def verify(token, secret=SECRET):
    import hmac
    import hashlib
    import base64
    if '.' not in token:
        return None
    body, signature = token.rsplit('.', 1)
    expected = hmac.new(secret.encode(), body.encode(), hashlib.sha256).hexdigest()[:32]
    # Compared in constant time so a mismatch does not leak where it differed.
    if not hmac.compare_digest(expected, signature):
        return None
    return base64.urlsafe_b64decode(body + '=' * (-len(body) % 4)).decode()


def main(subject=SUBJECT):
    token = issue(subject)
    print('token  :', token)
    print('valid  :', verify(token))
    print('tampered:', verify(token[:-1] + ('0' if token[-1] != '0' else '1')))
    print('wrong secret:', verify(token, 'other secret'))


main()''',
       required_patterns=("import hmac", "def ", "compare_digest", "print("),
       params={"subject": ("'user-42'", "'admin'", "'student:7'")},
       expect=("tampered: None",),
       n_variants=3),

    _t(id="fs-125-sessions", block="Full-stack Features", day=125, skill="A session that expires",
       prompt=(
           "Write a session store with `start(subject, ttl)` and `read(token, now)` that returns None "
           "once the session has expired, and `sweep(now)` removing what has lapsed. Start <<sessions>> "
           "and read them back at two different times, printing which have expired, so expiry is a "
           "behaviour rather than a timeout setting."),
       solution='''SESSIONS = <<sessions>>


def start(subject, ttl, store):
    import secrets
    token = secrets.token_urlsafe(8)
    store[token] = {'subject': subject, 'expires': store['_now'] + ttl}
    return token


def read(token, store):
    session = store.get(token)
    if session is None:
        return None
    if store['_now'] >= session['expires']:
        return None
    return session['subject']


def sweep(store):
    alive, dropped = {}, 0
    for token, session in store.items():
        if token == '_now':
            alive['_now'] = session
        elif store['_now'] >= session['expires']:
            dropped += 1
        else:
            alive[token] = session
    return alive, dropped


def main(sessions=SESSIONS):
    store = {'_now': 0}
    tokens = [(s['subject'], start(s['subject'], s['ttl'], store)) for s in sessions]
    store['_now'] = sessions[0]['ttl'] + 1
    for subject, token in tokens:
        print(f'{subject:<10} -> {read(token, store)}')
    store, dropped = sweep(store)
    print('swept    :', dropped, 'expired;', len(store) - 1, 'alive')


main()''',
       required_patterns=("import secrets", "def ", "for ", "return", "print("),
       params={"sessions": ("[{'subject': 'a', 'ttl': 10}, {'subject': 'b', 'ttl': 100}]",
                           "[{'subject': 'only', 'ttl': 5}]",
                           "[{'subject': 'x', 'ttl': 10}, {'subject': 'y', 'ttl': 50}, {'subject': 'z', 'ttl': 500}]")},
       expect=("swept    :",),
       n_variants=3),

    _t(id="fs-126-authz", block="Full-stack Features", day=126, skill="Deciding what an identity may do",
       prompt=(
           "Write `allowed(roles, action)` returning a decision with a reason, using a permissions "
           "table. Use roles <<roles>> against the action list, and print each decision, so a refusal "
           "carries a reason a user can act on."),
       solution='''ROLES = <<roles>>
ACTIONS = ['read', 'create', 'update', 'delete', 'admin']
PERMISSIONS = {
    'read': {'viewer', 'editor', 'admin'},
    'create': {'editor', 'admin'},
    'update': {'editor', 'admin'},
    'delete': {'admin'},
    'admin': {'admin'},
}


def allowed(roles, action):
    if action not in PERMISSIONS:
        return False, f'no such action: {action}'
    permitted = PERMISSIONS[action]
    for role in roles:
        if role in permitted:
            return True, f'{role} may {action}'
    return False, f'needs one of {sorted(permitted)}'


def main(roles=ROLES, actions=ACTIONS):
    for action in actions:
        granted, reason = allowed(roles, action)
        mark = 'allow' if granted else 'deny '
        print(f'{mark} {action:<8} {reason}')


main()''',
       required_patterns=("def ", "for ", "return", "in ", "print("),
       params={"roles": ("['viewer']", "['editor']", "['viewer', 'admin']")},
       expect=("allow",),
       n_variants=3),

    _t(id="fs-127-passwords", block="Full-stack Features", day=127, skill="Hashing a password safely",
       prompt=(
           "Write `hash_password(password, salt)` using `hashlib.pbkdf2_hmac` with a real iteration "
           "count, and `verify_password` comparing digests without leaking which part failed. Hash "
           "the passwords <<passwords>> and print how many verify, so the comparison is exercised "
           "without printing any digest."),
       solution='''PASSWORDS = <<passwords>>
ITERATIONS = 120000


def make_salt():
    import secrets
    return secrets.token_hex(16)


def hash_password(password, salt, iterations=ITERATIONS):
    import hashlib
    return hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), iterations).hex()


def verify_password(password, salt, expected, iterations=ITERATIONS):
    import hmac
    return hmac.compare_digest(hash_password(password, salt, iterations), expected)


def main(passwords=PASSWORDS):
    stored = {}
    for password in passwords:
        salt = make_salt()
        stored[password] = (salt, hash_password(password, salt))
        print(f'len {len(password):<3} hashed with a fresh salt')
    for password, (salt, digest) in stored.items():
        print(f'verifies correctly: {verify_password(password, salt, digest)}')
    sample = passwords[0]
    salt, digest = stored[sample]
    print('wrong password  :', verify_password(sample + '!', salt, digest))


main()''',
       required_patterns=("import hashlib", "import hmac", "compare_digest", "for ", "print("),
       params={"passwords": ("['correct horse', 'short', 'a much longer passphrase here']",
                             "['hunter2']",
                             "['abc', 'defg', 'hijkl', 'mnopqrst']")},
       expect=("wrong password  : False",),
       n_variants=3),

    _t(id="fs-128-uploads", block="Full-stack Features", day=128, skill="Validating an upload",
       prompt=(
           "Write `check_upload(name, size, allowed_types, max_bytes)` returning a decision and a "
           "reason, and `accept(reports)` counting the good ones. Use <<uploads>> and print every "
           "decision, so each rejection rule is exercised at least once."),
       solution='''UPLOADS = <<uploads>>
ALLOWED = {'.png', '.txt', '.csv'}
MAX_BYTES = 1000


def check_upload(name, size, allowed_types=ALLOWED, max_bytes=MAX_BYTES):
    suffix = '.' + name.rsplit('.', 1)[-1].lower() if '.' in name else ''
    if '.' not in name:
        return False, 'no extension'
    if suffix not in allowed_types:
        return False, f'{suffix} is not allowed'
    if size == 0:
        return False, 'file is empty'
    if size > max_bytes:
        return False, f'{size} bytes exceeds {max_bytes}'
    return True, 'accepted'


def accept(reports):
    good = [r for r in reports if r[0]]
    return good, len(reports) - len(good)


def main(uploads=UPLOADS):
    reports = [check_upload(name, size) for name, size in uploads]
    for (name, _size), (ok, reason) in zip(uploads, reports):
        print(f'{name:<16} {"accept" if ok else "reject"}  {reason}')
    good, bad = accept(reports)
    print(f'accepted {len(good)}, rejected {bad}')


main()''',
       required_patterns=("def ", "return", "for ", "in ", "print("),
       params={"uploads": ("[('photo.png', 500), ('script.exe', 100), ('empty.png', 0)]",
                            "[('big.txt', 5000), ('ok.txt', 10)]",
                            "[('noext', 10), ('data.csv', 200), ('tool.png', 4000)]")},
       expect=("accepted",),
       n_variants=3),

    _t(id="fs-129-pagination", block="Full-stack Features", day=129, skill="Paging through a result set",
       prompt=(
           "Write `paginate(items, page, per_page)` returning the slice plus whether there is a next "
           "or previous page, rejecting a page below one with ValueError. Page through <<items>> with "
           "<<per_page>> per page and print every page's contents, so offset arithmetic is visible."),
       solution='''ITEMS = <<items>>


def paginate(items, page, per_page):
    if page < 1:
        raise ValueError('page numbers start at 1')
    if per_page < 1:
        raise ValueError('per_page must be positive')
    start = (page - 1) * per_page
    window = items[start:start + per_page]
    return {
        'items': window,
        'page': page,
        'has_next': start + per_page < len(items),
        'has_previous': page > 1,
        'total': len(items),
    }


def main(items=ITEMS, per_page=<<per_page>>):
    page = 1
    while True:
        try:
            result = paginate(items, page, per_page)
        except ValueError as err:
            print('rejected:', err)
            break
        print(f"page {result['page']} of - {result['items']} "
              f"prev={result['has_previous']} next={result['has_next']}")
        if not result['has_next']:
            break
        page += 1


main()''',
       required_patterns=("def ", "raise ", "while ", "if ", "print("),
       params={"items": ("[1, 2, 3, 4, 5]", "list(range(10))", "[1, 2, 3, 4, 5, 6, 7]"),
               "per_page": ("2", "3", "5")},
       expect=("page 1",),
       n_variants=3),

    _t(id="fs-130-search", block="Full-stack Features", day=130, skill="Searching and ranking results",
       prompt=(
           "Write `search(records, term, key)` returning records whose field contains the term, "
           "case-insensitively, ranked by whether the match is at the start. Search <<records>> for "
           "the term <<term>> and print the ranking, so the ranking rule is stated rather than "
           "assumed."),
       solution='''RECORDS = <<records>>


def search(records, term, key):
    needle = term.lower()
    hits = []
    for record in records:
        value = str(record.get(key, '')).lower()
        if needle in value:
            hits.append((value.startswith(needle), value.count(needle), record))
    hits.sort(key=lambda hit: (not hit[0], -hit[1], str(hit[2])))
    return [hit[2] for hit in hits]


def main(records=RECORDS, term=<<term>>):
    found = search(records, term, 'name')
    print(f'term   : {term!r}')
    for position, record in enumerate(found, 1):
        print(f'{position}. {record["name"]}')
    print('matches:', len(found), 'of', len(records))
    if found:
        first = str(found[0]['name']).lower()
        print('first matched at the start:', first.startswith(term.lower()))


main()''',
       required_patterns=("def ", "lower()", "in ", "sort(", "for ", "print("),
       params={"records": ("[{'name': 'Asha'}, {'name': 'Rohan'}, {'name': 'Kiran'}]",
                            "[{'name': 'alpha'}, {'name': 'beta'}, {'name': 'alphabet'}]",
                            "[{'name': 'test'}, {'name': 'testing'}, {'name': 'contest'}]"),
               "term": ("'a'", "'test'", "'ro'")},
       expect=("matches:",),
       n_variants=3),

    _t(id="fs-131-notify", block="Full-stack Features", day=131, skill="Telling the user what happened",
       prompt=(
           "Write `notify(event)` producing a message and a severity for an event, and `render(events)` "
           "returning only the ones the user should see. Use <<events>> and print each message with its "
           "severity, so what is suppressed is as visible as what is shown."),
       solution='''EVENTS = <<events>>
LEVELS = {'error': 3, 'warning': 2, 'info': 1, 'debug': 0}


def notify(event):
    kind = event.get('kind', 'info')
    return f"{event.get('text', '')}", kind, LEVELS.get(kind, 1)


def render(events, minimum=2):
    out = []
    for event in events:
        message, kind, weight = notify(event)
        if weight >= minimum:
            out.append((kind, message))
    return out


def main(events=EVENTS):
    for kind, message in render(events):
        print(f'[{kind:<7}] {message}')
    print(f'showed {len(render(events))} of {len(events)} events')


main()''',
       required_patterns=("def ", "get(", "for ", "if ", "append(", "print("),
       params={"events": ("[{'kind': 'error', 'text': 'Save failed'}, {'kind': 'debug', 'text': 'render start'}]",
                           "[{'kind': 'info', 'text': 'Saved'}]",
                           "[{'kind': 'warning', 'text': 'Unsaved changes'}, {'kind': 'debug', 'text': 'tick'}, {'kind': 'error', 'text': 'Offline'}]")},
       expect=("showed",),
       n_variants=3),

    _t(id="fs-132-errorux", block="Full-stack Features", day=132, skill="An error a user can act on",
       prompt=(
           "Write `explain(error)` producing a message that says what happened and what to do, never "
           "leaking an internal name, and `fallback()` for the case with nothing useful. Use "
           "<<errors>> and print each message, so the difference between a useful and a useless error "
           "message is visible."),
       solution='''ERRORS = <<errors>>


def explain(error):
    code = error.get('code')
    hints = {
        'validation': 'Check the highlighted fields and submit again.',
        'conflict': 'Someone else changed this. Reload to see their version.',
        'rate_limited': 'Wait a few seconds before trying again.',
        'server': 'We are having trouble. Your work was not saved.',
    }
    if code in hints:
        return hints[code]
    return 'Something went wrong and we could not record why. Please try again.'


def fallback():
    return 'The request could not be completed. Please try again.'


def main(errors=ERRORS):
    for error in errors:
        print(f"{error.get('code', '?'):<14} {explain(error)}")
    print('unknown code:', explain({'code': 'wat'}))


main()''',
       required_patterns=("def ", "get(", "for ", "return", "print("),
       params={"errors": ("[{'code': 'validation'}, {'code': 'nonsense'}]",
                          "[{'code': 'rate_limited'}]",
                          "[{'code': 'conflict'}, {'code': 'server'}, {'code': 'other'}]")},
       expect=("unknown code:",),
       n_variants=3),

    _t(id="fs-133-feature", block="Full-stack Features", day=133, skill="One feature across both sides",
       prompt=(
           "Build the same feature end to end: a `store`, `create` on the server, a `submit` on the "
           "client that reports the server's decision, and `refresh` that re-reads. Add the items "
           "<<items>> and print the state after each step, so the round trip is visible as one "
           "connected feature."),
       solution='''ITEMS = <<items>>


def create(store, item):
    if not item.get('name'):
        return 422, {'error': 'name is required'}
    item = {**item, 'id': len(store) + 1}
    store.append(item)
    return 201, item


def submit(store, item):
    status, body = create(store, item)
    return {'status': status, 'body': body, 'sent': True}


def refresh(store):
    return {'status': 200, 'items': list(store), 'count': len(store)}


def main(items=ITEMS):
    store = []
    for item in items:
        result = submit(store, item)
        print(f"sent {item} -> {result['status']} {result['body']}")
    print('submit a bad one:', submit(store, {}))
    final = refresh(store)
    print('after refresh:', final['count'], final['items'])


main()''',
       required_patterns=("def ", "for ", "append(", "return", "print("),
       params={"items": ("[{'name': 'a'}, {'name': 'b'}]", "[{'name': 'only'}]",
                         "[{'name': 'x'}, {'name': 'y'}, {'name': 'z'}]")},
       expect=("after refresh:",),
       n_variants=3),

    _t(id="fs-134-featurereview", block="Full-stack Features", day=134, skill="Reviewing a feature you built",
       prompt=(
           "Write `review(handlers)` finding a handler with no client, a client call to no handler, "
           "and a handler that cannot fail. Apply it to <<handlers>> and print the findings, so the "
           "review is a list produced by a function rather than a judgement."),
       solution='''HANDLERS = <<handlers>>


def review(handlers):
    findings = []
    server = set()
    called = set()
    failing = set()
    for name, spec in handlers.items():
        if spec['side'] == 'server':
            server.add(name)
            if not spec.get('can_fail', True):
                failing.add(name)
        else:
            called.add(spec['calls'])
    for name in sorted(server - called):
        findings.append(f'{name} is never called by the client')
    for name in sorted(called - server):
        findings.append(f'client calls {name}, which has no handler')
    for name in sorted(failing):
        findings.append(f'{name} cannot fail, so its error path is untested')
    return findings


def main(handlers=HANDLERS):
    findings = review(handlers)
    for finding in findings:
        print(' -', finding)
    print('total findings:', len(findings))


main()''',
       required_patterns=("def ", "set(", "for ", "sorted(", "print("),
       params={"handlers": ("{'list': {'side': 'client', 'calls': 'list'}, 'get': {'side': 'server', 'calls': 'get'}}",
                            "{'save': {'side': 'client', 'calls': 'save'}, 'save_handler': {'side': 'server', 'calls': 'save'}}",
                            "{'a': {'side': 'server', 'calls': 'a'}, 'b': {'side': 'server', 'calls': 'b', 'can_fail': False}}")},
       expect=("total findings:",),
       n_variants=3),
)


QUALITY: tuple[ExerciseTemplate, ...] = (

    _t(id="qs-135-unit", block="Quality and Security", day=135, skill="Unit tests with unittest",
       prompt=(
           "Write a real `unittest.TestCase` covering a function's ordinary case, its boundary and its "
           "failure, run it, and print the result. Use the function <<target>> and report the runner's "
           "verdict, so the framework is used rather than reimplemented."),
       solution='''TARGET = <<target>>


def add(a, b):
    return a + b


def divide(a, b):
    if b == 0:
        raise ValueError('division by zero')
    return a / b


import unittest


class TestArithmetic(unittest.TestCase):
    def test_add_ordinary(self):
        self.assertEqual(add(2, 3), 5)

    def test_add_boundary(self):
        self.assertEqual(add(0, 0), 0)

    def test_add_negative(self):
        self.assertEqual(add(-2, 3), 1)

    def test_divide_ordinary(self):
        self.assertEqual(divide(6, 3), 2.0)

    def test_divide_by_zero_raises(self):
        with self.assertRaises(ValueError):
            divide(1, 0)


import io
from contextlib import redirect_stderr, redirect_stdout

buf = io.StringIO()
suite = unittest.TestLoader().loadTestsFromTestCase(TestArithmetic)
result = unittest.TextTestRunner(stream=buf, verbosity=0).run(suite)
print('ran   :', result.testsRun)
print('failures:', len(result.failures), '| errors:', len(result.errors))
print('verdict:', 'PASSED' if result.wasSuccessful() else 'FAILED')''',
       required_patterns=("import unittest", "TestCase", "assertEqual", "assertRaises", "print("),
       params={"target": ("'add'", "'divide'", "'add and divide'")},
       expect=("verdict: PASSED",),
       n_variants=3),

    _t(id="qs-136-apitest", block="Quality and Security", day=136, skill="Testing a handler end to end",
       prompt=(
           "Build a handler and a `unittest` case that calls it for a success, a validation failure "
           "and a not-found, asserting the status each time. Run the suite and print the verdict, so a "
           "handler's whole surface is checked rather than one path."),
       solution='''import unittest


def handler(request):
    if not request.get('name'):
        return 422, {'error': 'name is required'}
    if request['name'] == 'missing':
        return 404, {'error': 'not found'}
    return 200, {'name': request['name'], 'length': len(request['name'])}


class TestHandler(unittest.TestCase):
    def test_success(self):
        status, body = handler({'name': 'Asha'})
        self.assertEqual(status, 200)
        self.assertEqual(body['length'], 4)

    def test_validation_failure(self):
        self.assertEqual(handler({})[0], 422)

    def test_not_found(self):
        self.assertEqual(handler({'name': 'missing'})[0], 404)


import io

buf = io.StringIO()
suite = unittest.TestLoader().loadTestsFromTestCase(TestHandler)
result = unittest.TextTestRunner(stream=buf, verbosity=0).run(suite)
print('ran    :', result.testsRun)
print('verdict:', 'PASSED' if result.wasSuccessful() else 'FAILED')
print('length of "Asha":', handler({'name': 'Asha'})[1]['length'])''',
       required_patterns=("import unittest", "TestCase", "assertEqual", "print("),
       params={},
       expect=("verdict: PASSED",),
       n_variants=1),

    _t(id="qs-137-integration", block="Quality and Security", day=137, skill="Testing parts against each other",
       prompt=(
           "Write two units that genuinely interact, a real database and a function that reads it, and "
           "a `unittest` case that exercises both together against a temporary file. Run it and print "
           "the verdict, so the test would catch a break in either half."),
       solution='''import os
import sqlite3
import tempfile
import unittest


def connect(path):
    conn = sqlite3.connect(path)
    conn.execute('CREATE TABLE IF NOT EXISTS items (id INTEGER PRIMARY KEY, name TEXT)')
    return conn


def add_item(conn, name):
    conn.execute('INSERT INTO items (name) VALUES (?)', (name,))
    conn.commit()


def count_items(conn):
    return conn.execute('SELECT COUNT(*) FROM items').fetchone()[0]


class TestStore(unittest.TestCase):
    def setUp(self):
        fd, self.path = tempfile.mkstemp(suffix='.db')
        os.close(fd)
        self.conn = connect(self.path)

    def tearDown(self):
        self.conn.close()
        os.unlink(self.path)

    def test_add_then_count(self):
        self.assertEqual(count_items(self.conn), 0)
        add_item(self.conn, 'first')
        self.assertEqual(count_items(self.conn), 1)

    def test_count_reflects_every_write(self):
        for name in ('a', 'b', 'c'):
            add_item(self.conn, name)
        self.assertEqual(count_items(self.conn), 3)


import io

buf = io.StringIO()
suite = unittest.TestLoader().loadTestsFromTestCase(TestStore)
result = unittest.TextTestRunner(stream=buf, verbosity=0).run(suite)
print('ran    :', result.testsRun)
print('verdict:', 'PASSED' if result.wasSuccessful() else 'FAILED')''',
       required_patterns=("import sqlite3", "import unittest", "setUp", "tearDown", "print("),
       params={},
       expect=("verdict: PASSED",),
       n_variants=1),

    _t(id="qs-138-testdb", block="Quality and Security", day=138, skill="A test database that is thrown away",
       prompt=(
           "Write a fixture that builds a fresh temporary database per test and removes it "
           "afterwards, and a `unittest` case that inserts rows in one test and confirms the next test "
           "starts empty. Run it and print both counts, so isolation is demonstrated rather than "
           "assumed."),
       solution='''import os
import sqlite3
import tempfile
import unittest


def fresh_db():
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    conn = sqlite3.connect(path)
    conn.execute('CREATE TABLE rows_t (id INTEGER PRIMARY KEY, v TEXT)')
    return conn, path


class TestIsolation(unittest.TestCase):
    def setUp(self):
        self.conn, self.path = fresh_db()

    def tearDown(self):
        self.conn.close()
        os.unlink(self.path)

    def count(self):
        return self.conn.execute('SELECT COUNT(*) FROM rows_t').fetchone()[0]

    def test_first_writes(self):
        self.conn.execute("INSERT INTO rows_t (v) VALUES ('x')")
        self.conn.commit()
        self.assertEqual(self.count(), 1)

    def test_second_starts_empty(self):
        # A leak from the previous test would make this fail.
        self.assertEqual(self.count(), 0)


import io

buf = io.StringIO()
suite = unittest.TestLoader().loadTestsFromTestCase(TestIsolation)
result = unittest.TextTestRunner(stream=buf, verbosity=0).run(suite)
print('ran    :', result.testsRun)
print('verdict:', 'PASSED' if result.wasSuccessful() else 'FAILED')
print('isolation held:', result.wasSuccessful())''',
       required_patterns=("import sqlite3", "import unittest", "setUp", "tearDown", "assertEqual"),
       params={},
       expect=("isolation held: True",),
       n_variants=1),

    _t(id="qs-139-envvars", block="Quality and Security", day=139, skill="Reading configuration",
       prompt=(
           "Write `setting(name, default, env)` reading an environment variable and converting it, "
           "raising KeyError when it is absent and no default is given. Set the variables in "
           "<<env>> and print each setting and the error for the missing one, so required and optional "
           "configuration are visibly different."),
       solution='''import os

ENV = <<env>>


def setting(name, default=None, env=None):
    env = os.environ if env is None else env
    if name in env:
        raw = env[name]
        if isinstance(default, int) and raw.isdigit():
            return int(raw)
        if isinstance(default, bool):
            return raw.lower() in ('1', 'true', 'yes')
        return raw
    if default is None:
        raise KeyError(f'required setting not set: {name}')
    return default


def main(env=ENV):
    merged = {**env}
    for name, default in (('PORT', 8000), ('DEBUG', False), ('SECRET', None)):
        try:
            value = setting(name, default, merged)
            print(f'{name:<7} = {value!r}')
        except KeyError as err:
            print(f'{name:<7} -> {err}')


main()''',
       required_patterns=("import os", "def ", "raise ", "try:", "except ", "print("),
       params={"env": ("{'PORT': '9000', 'DEBUG': 'true'}", "{'PORT': '8080'}",
                        "{'PORT': '3000', 'DEBUG': 'false', 'SECRET': 's3cret'}")},
       expect=("SECRET",),
       n_variants=3),

    _t(id="qs-140-secrets", block="Quality and Security", day=140, skill="Generating and comparing secrets",
       prompt=(
           "Write `make_secret(length)` returning a URL-safe random secret from `secrets`, and "
           "`matches(a, b)` comparing without an early exit. Generate <<count>> secrets, print their "
           "lengths and that they differ, and show the comparison refusing a near-miss, so a secret is "
           "generated correctly rather than invented."),
       solution='''import secrets
import string

ALPHABET = string.ascii_letters + string.digits


def make_secret(length=32):
    return ''.join(secrets.choice(ALPHABET) for _ in range(length))


def matches(a, b):
    import hmac
    if len(a) != len(b):
        return False
    return hmac.compare_digest(a, b)


def main(count=<<count>>):
    made = [make_secret(32) for _ in range(count)]
    for index, value in enumerate(made, 1):
        print(f'{index}. len {len(value)} {value[:6]}...')
    print('all distinct:', len(set(made)) == count)
    print('exact match :', matches(made[0], made[0]))
    print('near miss   :', matches(made[0], made[0][:-1] + ('a' if made[0][-1] != 'a' else 'b')))
    print('short       :', matches(made[0], made[0][:10]))


main()''',
       required_patterns=("import secrets", "compare_digest", "for ", "print("),
       params={"count": ("3", "5", "2")},
       expect=("all distinct: True",),
       n_variants=3),

    _t(id="qs-141-sanitize", block="Quality and Security", day=141, skill="Validating input against an allowlist",
       prompt=(
           "Write `clean(value, allowed_types, max_len)` refusing anything of the wrong type or over "
           "the limit, and `safe_query(field, value)` refusing a field that is not an allowlist of "
           "identifiers. Use <<cases>> and print each decision, so a refusal names the rule it broke."),
       solution='''CASES = <<cases>>
SAFE_FIELDS = {'name', 'email', 'age'}


def clean(value, allowed_types=(str, int), max_len=100):
    if not isinstance(value, allowed_types):
        return None, f'type {type(value).__name__} is not allowed'
    if isinstance(value, str) and len(value) > max_len:
        return None, f'string exceeds {max_len} characters'
    return value, 'accepted'


def safe_query(field, value, allowed=SAFE_FIELDS):
    if field not in allowed:
        return None, f'unknown field {field!r}'
    cleaned, reason = clean(value)
    if cleaned is None:
        return None, reason
    return (field, cleaned), 'accepted'


def main(cases=CASES):
    for field, value in cases:
        result, reason = safe_query(field, value)
        print(f'{field!r:<10} {str(value)[:16]!r:<20} {reason}')
        if result is not None:
            print('   usable as', result)


main()''',
       required_patterns=("def ", "isinstance(", "if ", "return", "for ", "print("),
       params={"cases": ("[('name', 'Asha'), ('age', 30), ('name', 'x' * 200), ('evil', 1)]",
                          "[('email', 'a@b.co')]",
                          "[('name', 123), ('age', 'thirty')]")},
       expect=("usable as",),
       n_variants=3),

    _t(id="qs-142-csrf", block="Quality and Security", day=142, skill="Why a token travels with the request",
       prompt=(
           "Model the check: `make_token(session, secret)` and `check(request, secret)` accepting only "
           "when the session cookie and the submitted token agree. Use session <<session>> and print "
           "an accepted request, one with a wrong token, and one with no token, so the three outcomes "
           "are distinct."),
       solution='''import hmac
import hashlib

SESSION = <<session>>
SECRET = 'shared secret between the two sides'


def make_token(session, secret=SECRET):
    return hmac.new(secret.encode(), session.encode(), hashlib.sha256).hexdigest()[:24]


def check(request, secret=SECRET):
    session = request.get('cookie')
    token = request.get('token')
    if not session or not token:
        return False, 'missing cookie or token'
    if not hmac.compare_digest(make_token(session, secret), token):
        return False, 'token does not match the session'
    return True, 'accepted'


def main(session=SESSION):
    token = make_token(session)
    good = {'cookie': session, 'token': token}
    for label, request in (('good     ', good),
                           ('bad token', {'cookie': session, 'token': 'x' * 24}),
                           ('no token ', {'cookie': session})):
        allowed, reason = check(request)
        print(f'{label} -> {"allow" if allowed else "deny "}  {reason}')


main()''',
       required_patterns=("import hmac", "compare_digest", "def ", "if ", "print("),
       params={"session": ("'session-abc'", "'sid-1-2-3'", "'longer-session-value'")},
       expect=("no token  -> deny",),
       n_variants=3),

    _t(id="qs-143-cors", block="Quality and Security", day=143, skill="Deciding which origins are allowed",
       prompt=(
           "Write `allowed_origin(origin, allowed, credentials)` allowing a listed origin, refusing "
           "`null`, and treating a wildcard as incompatible with credentials. Use <<origins>> and print "
           "each decision with its reason, so the preflight question has a stated answer."),
       solution='''ORIGINS = <<origins>>
ALLOWED = ['https://app.example.com', 'https://admin.example.com']


def allowed_origin(origin, allowed=ALLOWED, credentials=True):
    if origin == 'null':
        return None, 'refused: a null origin is a sandboxed or file page'
    if origin == '*':
        if credentials:
            return None, 'refused: a wildcard cannot be combined with credentials'
        return '*', 'allowed: public read only'
    if origin in allowed:
        return origin, 'allowed: listed origin'
    return None, f'refused: {origin} is not listed'


def main(origins=ORIGINS):
    for origin in origins:
        value, reason = allowed_origin(origin)
        print(f'{origin:<32} {reason}')
    print('sent header:', allowed_origin('https://app.example.com')[0])


main()''',
       required_patterns=("def ", "if ", "in ", "return", "for ", "print("),
       params={"origins": ("['https://app.example.com', 'https://evil.test', 'null']",
                            "['*', 'https://app.example.com']",
                            "['null', 'https://admin.example.com', 'https://other.test']")},
       expect=("sent header:",),
       n_variants=3),

    _t(id="qs-144-ratelimit", block="Quality and Security", day=144, skill="Limiting how often something happens",
       prompt=(
           "Write a sliding-window limiter: `allow(key, now)` returning whether a request is within "
           "the limit, using a per-key window. Use <<requests>> at <<window>> seconds per <<limit>> "
           "allowed, and print each decision, so the window's effect is visible rather than asserted."),
       solution='''REQUESTS = <<requests>>
WINDOW = <<window>>
LIMIT = <<limit>>


def allow(history, key, now, window=WINDOW, limit=LIMIT):
    recent = [t for t in history.get(key, []) if now - t < window]
    if len(recent) >= limit:
        history[key] = recent
        return False, len(recent)
    recent.append(now)
    history[key] = recent
    return True, len(recent)


def main(requests=REQUESTS, window=WINDOW, limit=LIMIT):
    history = {}
    allowed_count = 0
    for key, now in requests:
        granted, count = allow(history, key, now, window, limit)
        allowed_count += 1 if granted else 0
        print(f'{now:>3}s {key:<6} {"allow" if granted else "BLOCK"}  ({count} in window)')
    print(f'allowed {allowed_count} of {len(requests)}')


main()''',
       required_patterns=("def ", "for ", "get(", "if ", "return", "print("),
       params={"requests": ("[('a', 0), ('a', 1), ('a', 2), ('a', 10)]",
                            "[('x', 0), ('y', 0), ('x', 1)]",
                            "[('a', 0), ('a', 0), ('a', 0), ('b', 0), ('a', 20)]"),
               "window": ("3", "5", "10"), "limit": ("2", "3", "1")},
       expect=("allowed",),
       n_variants=3),

    _t(id="qs-145-logging2", block="Quality and Security", day=145, skill="Logging a request through its life",
       prompt=(
           "Configure `logging` to a real temporary file, log a request through middleware-like hooks at "
           "entry and exit, then read the file back and print the lines. Use <<path>> and log one "
           "DEBUG line that must be filtered, so the level threshold is demonstrated."),
       solution='''import logging
import os
import tempfile

PATH = <<path>>


def setup(path):
    logging.basicConfig(filename=path, level=logging.INFO, force=True,
                        format='%(levelname)s %(message)s')
    return logging.getLogger('app')


def middleware(logger, request):
    logger.debug('entering %s', request)
    logger.info('handling %s %s', request['method'], request['path'])
    result = {'status': 200}
    logger.info('finished %s with %s', request['path'], result['status'])
    return result


def main(path=PATH):
    fd, target = tempfile.mkstemp(suffix=path)
    os.close(fd)
    try:
        logger = setup(target)
        logger.debug('this line is below the threshold')
        middleware(logger, {'method': 'GET', 'path': '/items'})
        logging.shutdown()
        with open(target, encoding='utf-8') as handle:
            lines = [line.rstrip() for line in handle if line.strip()]
        for line in lines:
            print(line)
        print('debug line suppressed:', not any('below the threshold' in l for l in lines))
    finally:
        os.unlink(target)


main()''',
       required_patterns=("import logging", "basicConfig", "INFO", "print("),
       params={"path": ("'app.log'", "'request.log'", "'access.log'")},
       expect=("debug line suppressed: True",),
       n_variants=3),

    _t(id="qs-146-monitoring", block="Quality and Security", day=146, skill="Measuring what the service did",
       prompt=(
           "Write `record(entries)` accumulating counts, mean latency, worst latency and an error rate "
           "from a list of request records, and `report()` printing them. Use <<entries>> and print the "
           "full report, so a monitoring summary is derived from the data rather than guessed."),
       solution='''ENTRIES = <<entries>>


def record(entries):
    total = len(entries)
    latencies = sorted(e['ms'] for e in entries)
    errors = sum(1 for e in entries if e['status'] >= 500)
    return {
        'requests': total,
        'mean_ms': sum(latencies) / total,
        'p95_ms': latencies[max(0, int(0.95 * total) - 1)],
        'worst_ms': latencies[-1],
        'errors': errors,
        'error_rate': errors / total,
    }


def main(entries=ENTRIES):
    summary = record(entries)
    for key in ('requests', 'errors'):
        print(f'{key:<12} {summary[key]}')
    print(f'{"mean_ms":<12} {summary["mean_ms"]:.2f}')
    print(f'{"p95_ms":<12} {summary["p95_ms"]}')
    print(f'{"worst_ms":<12} {summary["worst_ms"]}')
    print(f'{"error_rate":<12} {summary["error_rate"]:.1%}')


main()''',
       required_patterns=("def ", "sorted(", "sum(", "for ", "print("),
       params={"entries": ("[{'ms': 20, 'status': 200}, {'ms': 300, 'status': 500}, {'ms': 45, 'status': 200}]",
                            "[{'ms': 10, 'status': 200}]",
                            "[{'ms': 5, 'status': 200}, {'ms': 400, 'status': 503}, {'ms': 90, 'status': 200}, {'ms': 60, 'status': 500}]")},
       expect=("error_rate",),
       n_variants=3),

    _t(id="qs-147-a11y", block="Quality and Security", day=147, skill="An accessibility audit you can run",
       prompt=(
           "Write `audit(fragments)` checking for images without alt text, inputs with no label, "
           "buttons with no accessible name, and heading levels skipped. Use <<fragments>> and print "
           "each finding by rule, so the audit is a count per rule rather than one verdict."),
       solution='''FRAGMENTS = <<fragments>>


def audit(fragments):
    import re
    findings = {}
    for fragment in fragments:
        for tag in re.findall(r'<img[^>]*>', fragment):
            if 'alt=' not in tag:
                findings['image without alt'] = findings.get('image without alt', 0) + 1
        for tag in re.findall(r'<(input|select)[^>]*>', fragment):
            if 'aria-label' not in tag and 'id=' not in tag:
                findings['control without a label'] = findings.get('control without a label', 0) + 1
        for tag in re.findall(r'<button[^>]*>(.*?)</button>', fragment, re.S):
            if not tag.strip():
                findings['button with no name'] = findings.get('button with no name', 0) + 1
        levels = [int(h) for h in re.findall(r'<h([1-6])', fragment)]
        for first, second in zip(levels, levels[1:]):
            if second > first + 1:
                findings['skipped heading level'] = findings.get('skipped heading level', 0) + 1
    return findings


def main(fragments=FRAGMENTS):
    findings = audit(fragments)
    for rule in sorted(findings):
        print(f'{rule:<26} {findings[rule]}')
    print('total findings:', sum(findings.values()))


main()''',
       required_patterns=("def ", "findall(", "get(", "for ", "print("),
       params={"fragments": ("['<img src=a><input><h1>T</h1><h3>S</h3><button></button>']",
                             "['<h2>Only h2</h2>']",
                             "['<img src=x alt=ok><input id=q><h1>A</h1><h2>B</h2><h4>D</h4>']")},
       expect=("total findings:",),
       n_variants=3),

    _t(id="qs-148-secreview", block="Quality and Security", day=148, skill="Reviewing your own security decisions",
       prompt=(
           "Write `review(findings)` ranking each risk by how severe it is and how hard it is to fix, "
           "and returning the order. Use <<findings>> and print the ranked list, so the review "
           "produces an order of work rather than a list of worries."),
       solution='''FINDINGS = <<findings>>


SEVERITY = {'critical': 4, 'high': 3, 'medium': 2, 'low': 1}


def review(findings):
    scored = []
    for finding in findings:
        weight = SEVERITY.get(finding['severity'], 0)
        effort = finding.get('effort_days', 1)
        score = weight / effort
        scored.append((score, finding))
    scored.sort(key=lambda pair: -pair[0])
    return [(finding['severity'], round(score, 2), finding['title']) for score, finding in scored]


def main(findings=FINDINGS):
    for position, (severity, score, title) in enumerate(review(findings), 1):
        print(f'{position}. [{severity:<8}] score {score:<6} {title}')


main()''',
       required_patterns=("def ", "get(", "sort(", "for ", "print("),
       params={"findings": ("[{'severity': 'high', 'effort_days': 1, 'title': 'No rate limit'}]",
                            "[{'severity': 'low', 'effort_days': 5, 'title': 'Noisy log line'}, {'severity': 'critical', 'effort_days': 2, 'title': 'Secret in repository'}]",
                            "[{'severity': 'medium', 'effort_days': 1, 'title': 'Missing timeout'}, {'severity': 'high', 'effort_days': 1, 'title': 'Unvalidated input'}]")},
       expect=("score",),
       n_variants=3),

    _t(id="qs-149-qproject", block="Quality and Security", day=149, skill="A whole quality pass in one program",
       prompt=(
           "Bring the block together: a handler, a validator, a rate limiter and a test for each, run "
           "the suite and print a quality report. Use the requests <<requests>> and print the report, "
           "so the day exercises everything the block taught rather than summarising it."),
       solution='''import unittest
import io

REQUESTS = <<requests>>


def validate(request):
    if not request.get('token'):
        return 'missing token'
    return None


def rate_limit(history, key, now, limit=2, window=5):
    recent = [t for t in history.get(key, []) if now - t < window]
    if len(recent) >= limit:
        return False
    recent.append(now)
    history[key] = recent
    return True


def handle(request, history, now):
    problem = validate(request)
    if problem:
        return 401, problem
    if not rate_limit(history, request.get('key', 'anon'), now):
        return 429, 'slow down'
    return 200, {'ok': True}


class TestQuality(unittest.TestCase):
    def test_rejects_missing_token(self):
        self.assertEqual(handle({}, {}, 0)[0], 401)

    def test_allows_a_good_request(self):
        self.assertEqual(handle({'token': 't', 'key': 'k'}, {}, 0)[0], 200)

    def test_blocks_the_third(self):
        history = {}
        handle({'token': 't', 'key': 'k'}, history, 0)
        handle({'token': 't', 'key': 'k'}, history, 1)
        self.assertEqual(handle({'token': 't', 'key': 'k'}, history, 2)[0], 429)


def main(requests=REQUESTS):
    history = {}
    for request, now in requests:
        status, body = handle(request, history, now)
        print(f'{now:>3}s {str(request.get("key")):<6} -> {status} {body}')
    buf = io.StringIO()
    suite = unittest.TestLoader().loadTestsFromTestCase(TestQuality)
    result = unittest.TextTestRunner(stream=buf, verbosity=0).run(suite)
    print('tests   :', result.testsRun, 'verdict:',
          'PASSED' if result.wasSuccessful() else 'FAILED')


main()''',
       required_patterns=("import unittest", "def ", "for ", "assertEqual", "print("),
       params={"requests": ("[({'token': 't', 'key': 'a'}, 0), ({'key': 'b'}, 1), ({'token': 't', 'key': 'a'}, 2)]",
                            "[({'token': 't', 'key': 'a'}, 0)]",
                            "[({'token': 't', 'key': 'a'}, 0), ({'token': 't', 'key': 'a'}, 1), ({'token': 't', 'key': 'a'}, 2), ({}, 3)]")},
       expect=("verdict:",),
       n_variants=3),
)


WEB_BLOCKS = WEB_FOUNDATIONS + FASTAPI_APIS + DATABASES + FULLSTACK + QUALITY
