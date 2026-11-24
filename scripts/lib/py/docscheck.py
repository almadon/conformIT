#!/usr/bin/env python3
"""conformIT: README and docs-link checks (decision #28).

Read-only, standard library only, no network. Prints one finding per line as
LEVEL<TAB>message, the same shape depcheck.py uses, so conform.sh can turn
them into notes. Prints only section names, counts, and file:line samples,
never file contents.

    docscheck.py readme <repo>    section presence and order, a graphic near
                                  the top, and relative links that resolve

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


def main(argv):
    if len(argv) != 3 or argv[1] != "readme":
        print(__doc__)
        return 2
    try:
        cmd_readme(argv[2])
    except Exception as e:  # a helper bug must never take the audit down with it
        emit("WARN", f"readme check failed internally ({type(e).__name__}); result incomplete")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
