#!/usr/bin/env python3
"""conformIT: README and docs-link checks (decision #28).

Read-only, standard library only, no network. Prints one finding per line as
LEVEL<TAB>message, the same shape depcheck.py uses, so conform.sh can turn
them into notes. Prints only section names, counts, and file:line samples,
never file contents.

    docscheck.py readme <repo>    section presence and order, a graphic near
                                  the top, and relative links that resolve
    docscheck.py ui <repo>        usability and accessibility signals in a
                                  repo that has a screen (decision #31)

A README containing `<!-- conformit: exempt ... -->` is skipped entirely:
forks of other people's projects are not restyled (decision #28).
"""
import os
import re
import subprocess
import sys

# Canonical order of the sections a README may carry. A heading is matched to
# the first entry whose pattern fits, case-insensitively.
SECTIONS = [
    ("What it does", r"what (it|this) (does|is)|what is\b|overview|about"),
    ("Use cases", r"use cases?"),
    ("Getting started", r"getting started|install(ation)?|quick ?start"),
    ("Usage", r"usage|using\b|how to use"),
    ("Configuration", r"configuration|config|settings|options"),
    ("How it works", r"how (it|this) (works|fits)|architecture|design"),
    ("Documentation", r"documentation|docs"),
    ("Development", r"development|contributing|building"),
    ("License", r"licen[cs]e"),
]
REQUIRED = ("What it does", "Getting started", "License")
EXEMPT_RE = re.compile(r"<!--\s*conformit:\s*exempt\b", re.I)
DEPRECATED_RE = re.compile(r"\*\*\s*Status:?\s*Deprecated", re.I)
IMG_RE = re.compile(r"<img\b|<picture\b|!\[[^\]]*\]\(")
LINK_RE = re.compile(r"\]\(\s*<?([^)\s>]+)|(?:href|src)=[\"']([^\"']+)[\"']")
FENCE_RE = re.compile(r"^\s*(```|~~~)")


def emit(level, msg):
    print(f"{level}\t{' '.join(str(msg).split())}")


def tracked(repo, others=False):
    """Tracked files; with others=True also untracked, unignored ones, so a
    local run before committing does not call a new file's links broken."""
    cmd = ["git", "-C", repo, "ls-files", "-z"] + (["--cached", "--others", "--exclude-standard"] if others else [])
    try:
        out = subprocess.run(cmd, capture_output=True, timeout=30).stdout
    except Exception:
        return []
    return [f for f in out.decode("utf-8", "replace").split("\0") if f]


def lines_outside_fences(text):
    fenced = False
    for i, line in enumerate(text.splitlines(), 1):
        if FENCE_RE.match(line):
            fenced = not fenced
            continue
        if not fenced:
            yield i, line


def classify(heading):
    h = re.sub(r"[^\w\s']", " ", heading).strip().lower()
    for name, pat in SECTIONS:
        if re.match(r"^(" + pat + r")", h):
            return name
    return None


def check_links(repo, files, fset):
    broken = []
    dirs = {os.path.dirname(f) for f in files}
    for f in files:
        if not (f.lower() == "readme.md" or (f.startswith("docs/") and f.endswith(".md"))):
            continue
        try:
            with open(os.path.join(repo, f), encoding="utf-8", errors="replace") as fh:
                text = fh.read()
        except OSError:
            continue
        for i, line in lines_outside_fences(text):
            line = re.sub(r"`[^`]*`", "", line)
            for m in LINK_RE.finditer(line):
                target = (m.group(1) or m.group(2) or "").strip()
                if not target or re.match(r"^([a-z][a-z0-9+.-]*:|#|/|\{|\$|<)", target, re.I) or "://" in target:
                    continue
                target = re.split(r"[#?]", target, maxsplit=1)[0]
                if not target:
                    continue
                path = os.path.normpath(os.path.join(os.path.dirname(f), target))
                if path.startswith(".."):
                    continue
                if path in fset or path in dirs or any(x.startswith(path + "/") for x in fset):
                    continue
                broken.append(f"{f}:{i}")
    return broken


def cmd_readme(repo):
    files = tracked(repo)
    fset = set(tracked(repo, others=True))
    readme = next((f for f in files if f.lower() == "readme.md"), None)
    if not readme:
        return  # a missing README is already reported by the required-files check
    with open(os.path.join(repo, readme), encoding="utf-8", errors="replace") as fh:
        text = fh.read()
    if EXEMPT_RE.search(text):
        emit("PASS", "README marked exempt from the house style (a fork of someone else's project), so its structure was not checked")
        return

    if DEPRECATED_RE.search(text.split("\n## ", 1)[0]):
        if re.search(r"\]\(\s*<?\S+", text):
            emit("PASS", "README is a deprecation notice with a link onward, so its section order was not checked")
        else:
            emit("WARN", "README says Deprecated but links to no replacement")
        return

    seen = []  # (canonical name, heading text, line)
    for i, line in lines_outside_fences(text):
        m = re.match(r"^##\s+(.+?)\s*#*\s*$", line)
        if m:
            name = classify(m.group(1))
            if name:
                seen.append((name, m.group(1), i))
    names = [n for n, _, _ in seen]
    order = [n for n, _ in SECTIONS]
    problems = []

    missing = [n for n in REQUIRED if n not in names]
    if missing:
        problems.append(f"README has no section for: {', '.join(missing)}")
    # "How it works" may sit anywhere before Documentation: Consigliere's README,
    # the reference, introduces the architecture before Getting started.
    fixed = [(order.index(n), h) for n, h, _ in seen if n != "How it works"]
    out_of_place = [fixed[k][1] for k in range(1, len(fixed)) if fixed[k][0] < max(r for r, _ in fixed[:k])]
    docs_at = names.index("Documentation") if "Documentation" in names else None
    if docs_at is not None and any(n == "How it works" for n in names[docs_at + 1:]):
        out_of_place.append(next(h for n, h, _ in seen[docs_at + 1:] if n == "How it works"))
    if out_of_place:
        problems.append(f"README sections are out of the standard order (what it does, use cases, getting started, usage, configuration, documentation, development, license, with how it works anywhere before documentation): {'; '.join(out_of_place[:4])}")

    top = text.split("\n## ", 1)[0]
    if not IMG_RE.search(top):
        problems.append("no logo, screenshot or diagram above the first section of the README")

    broken = check_links(repo, files, fset)
    if broken:
        problems.append(f"{len(broken)} relative link(s) in the README or docs/ point at nothing in the repo, e.g. {', '.join(broken[:3])}")

    for p in problems:
        emit("WARN", p)
    if not problems:
        emit("PASS", "README follows the standard section order, opens with a graphic, and its relative links resolve")


# --------------------------------------------------------------------- ui
#
# Docs/accessibility.md. Looks at source only and cannot test anything: it
# finds the things that are visible in text (a viewport tag, zoom disabled, a
# missing lang or alt, motion and focus handling, a text size control, viewport
# tests) and says "found nothing" rather than "fails". Every finding is a WARN.

UI_EXT = (".tsx", ".jsx", ".vue", ".svelte", ".astro", ".css", ".scss", ".html")
MARKUP_EXT = (".html", ".astro", ".vue", ".svelte", ".tsx", ".jsx")
SKIP_DIRS = ("node_modules/", "dist/", "build/", ".next/", "vendor/", "docs/", "templates/", "tests/fixtures/")
VIEWPORT_TEST_RE = re.compile(r"setViewportSize|cy\.viewport|\bviewport\s*:\s*\{|page\.setViewport|devices\[|resizeTo\(|innerWidth\s*=")
TEXT_CONTROL_RE = re.compile(r"font-?scale|text-?scale|text-?size|--font-scale|fontScale|textSize|font_size_scale", re.I)


def _read(repo, rel):
    try:
        with open(os.path.join(repo, rel), encoding="utf-8", errors="replace") as fh:
            return fh.read()
    except OSError:
        return ""


def cmd_ui(repo):
    files = [f for f in tracked(repo) if not any(f.startswith(d) or ("/" + d) in ("/" + f) for d in SKIP_DIRS)]
    ui = [f for f in files if f.endswith(UI_EXT)]
    # a repo with only stylesheets is not necessarily an app: want markup or components
    if not any(f.endswith(MARKUP_EXT) for f in ui):
        return
    markup = [f for f in ui if f.endswith(MARKUP_EXT)]
    css = [f for f in ui if f.endswith((".css", ".scss"))]
    mtext = {f: _read(repo, f) for f in markup}
    ctext = {f: _read(repo, f) for f in css}
    alltext = "\n".join(list(mtext.values()) + list(ctext.values()))
    problems = []

    if not re.search(r"name\s*=\s*[\"']viewport[\"']", alltext):
        problems.append("no viewport meta tag found, so a phone will render the page at desktop width")
    zoom = [f for f, t in mtext.items() if re.search(r"user-scalable\s*=\s*(no|0)|maximum-scale\s*=\s*1(\.0)?\b", t)]
    if zoom:
        problems.append(f"pinch zoom is switched off by the viewport tag, which locks out people who need larger text: {', '.join(zoom[:3])}")
    nolang = [f for f, t in mtext.items() if f.endswith(".html") and re.search(r"<html\b(?![^>]*\blang\s*=)", t)]
    if nolang:
        problems.append(f"{len(nolang)} HTML file(s) with no lang attribute on <html>, so screen readers guess the language: {', '.join(nolang[:3])}")

    noalt = []
    for f, t in mtext.items():
        for m in re.finditer(r"<img\b[^>]*>", t, re.S):
            tag = m.group(0)
            if "{..." in tag or re.search(r"\balt\s*=", tag):
                continue
            noalt.append(f"{f}:{t.count(chr(10), 0, m.start()) + 1}")
    if noalt:
        problems.append(f"{len(noalt)} <img> tag(s) with no alt attribute (use alt=\"\" for a purely decorative image), e.g. {', '.join(noalt[:3])}")

    ctext_all = "\n".join(ctext.values())
    if re.search(r"\b(animation|transition)\s*:", ctext_all) and not re.search(r"prefers-reduced-motion|data-motion|reduce-motion|reduceMotion", alltext):
        problems.append("animations or transitions with no reduced-motion handling (prefers-reduced-motion or a setting)")
    if re.search(r"outline\s*:\s*(none|0)\b", ctext_all) and not re.search(r":focus-visible|:focus\s*\{[^}]*(outline|box-shadow)", ctext_all):
        problems.append("the focus outline is removed with no visible replacement, so keyboard users cannot see where they are")

    src_all = alltext
    docs = "\n".join(_read(repo, f) for f in files if f.lower() == "readme.md") + "\n" + "\n".join(
        _read(repo, f) for f in tracked(repo) if f.startswith("docs/") and f.endswith(".md"))
    if not (TEXT_CONTROL_RE.search(src_all) or re.search(r"(?i)text size|font size", docs)):
        problems.append("no text size control found (searched the source for a font or text scale, and the README and docs for \"text size\"); see docs/accessibility.md")

    tests = [f for f in tracked(repo) if re.search(r"(playwright|cypress|wdio|vitest)\.?(config)?|\.(spec|test|e2e)\.[jt]sx?$|/e2e/|/tests?/", f)]
    vp = any(VIEWPORT_TEST_RE.search(_read(repo, f)) for f in tests[:200])
    if not vp:
        problems.append("no automated viewport test found (searched test and browser-test files for a set viewport size); test at phone, tablet and desktop widths and at the largest text size")

    if not re.search(r"(?i)accessib", docs):
        problems.append("no statement of which accessibility options are offered and what was tested, in the README or docs")

    for p_ in problems:
        emit("WARN", p_)
    if not problems:
        emit("PASS", "viewport tag, lang, alt text, motion and focus handling, a text size control and viewport tests all found")


def main(argv):
    cmds = {"readme": cmd_readme, "ui": cmd_ui}
    if len(argv) != 3 or argv[1] not in cmds:
        print(__doc__)
        return 2
    try:
        cmds[argv[1]](argv[2])
    except Exception as e:  # a helper bug must never take the audit down with it
        emit("WARN", f"{argv[1]} check failed internally ({type(e).__name__}); result incomplete")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
