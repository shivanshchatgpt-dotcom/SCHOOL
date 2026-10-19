#!/usr/bin/env python3
"""Generate standalone roadmap HTML files from _engine.html + data/<slug>.js.

Usage:  python3 build.py            # build every data/*.js
        python3 build.py web-dev    # build only these slugs
Adding a new roadmap = drop a data/<slug>.js file and run this.
"""
import json, re, sys, pathlib

ROOT = pathlib.Path(__file__).parent
ENGINE = (ROOT / "_engine.html").read_text()
PATHS = (ROOT / "data" / "paths.js").read_text().strip()

def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def block(text, name, close):
    m = re.search(r'const ' + name + r' = (.*?' + re.escape(close) + r')\s*;\s*$',
                  text, re.S | re.M)
    assert m, f"{name} not found"
    return m.group(1)

def check(txt, slug):
    """Fail loudly on broken data: duplicate keys, orphan nodes, self references."""
    keys = re.findall(r'^  "([^"]+)":\{', txt, re.M)
    dups = {k for k in keys if keys.count(k) > 1}
    secs = re.findall(
        r'\{main:"([^"]+)"[^{]*?left:\[([^\]]*)\][^{]*?right:\[([^\]]*)\]', txt)
    mains = [m for m, _, _ in secs]
    kids = [t for _, l, r in secs for t in re.findall(r'"([^"]+)"', l + "," + r)]
    problems = []
    if dups:
        problems.append(f"duplicate DETAIL keys: {sorted(dups)}")
    if len(set(mains)) != len(mains):
        problems.append(f"duplicate section mains: {mains}")
    missing = sorted({*mains, *kids} - set(keys))
    if missing:
        problems.append(f"nodes without DETAIL: {missing}")
    for m, l, r in secs:
        if m in l + r:
            problems.append(f"section '{m}' lists itself as a child")
    if problems:
        raise SystemExit(f"[{slug}] " + "\n           ".join(problems))
    return len(keys)

def main():
    data = sorted(p for p in (ROOT / "data").glob("*.js") if p.name != "paths.js")
    slugs = [p.stem for p in data]
    npths = len(re.findall(r'\["[^"]*","[^"]*"\]', PATHS))
    if len(sys.argv) > 1:
        wanted = set(sys.argv[1:])
        data = [p for p in data if p.stem in wanted]
    built = json.dumps(slugs)
    for p in data:
        txt = p.read_text()
        n = check(txt, p.stem)
        title = re.search(r'//\s*TITLE:\s*(.+)', txt).group(1).strip()
        html = (ENGINE
                .replace("__TITLE__", esc(title))
                .replace("__SLUG__", json.dumps(p.stem))
                .replace("__BUILT__", built)
                .replace("__NPATHS__", str(npths))
                .replace("__PATHS__", PATHS)
                .replace("__SECTIONS__", block(txt, "SECTIONS", "]"))
                .replace("__DETAIL__", block(txt, "DETAIL", "}")))
        assert "__" not in re.sub(r'https?://\S+', '', html), "unfilled placeholder"
        out = ROOT / f"{p.stem}-roadmap.html"
        out.write_text(html)
        print(f"  {out.name}  ({len(html)//1024} KB, {n} nodes)  <- {p.name}")

if __name__ == "__main__":
    main()
