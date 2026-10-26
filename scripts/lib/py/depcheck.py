#!/usr/bin/env python3
"""conformIT: dependency and supply-chain checks that need registry lookups.

Called from scripts/lib/dep-checks.sh, one subcommand per check:

    depcheck.py osv-summary <osv.json> <repo>   fold osv-scanner output into findings
    depcheck.py lockfiles   <repo>              manifests with no lockfile
    depcheck.py outdated    <repo>              direct deps a major version behind
    depcheck.py deprecated  <repo>              deprecated packages recorded in lockfiles
    depcheck.py actions     <repo>              outdated, floating or deprecated-runtime Actions refs
    depcheck.py eol         <repo>              end-of-life base images and language runtimes

Output is one finding per line, `LEVEL<TAB>message`, LEVEL one of PASS, WARN,
FAIL. A subcommand prints nothing when the repo has nothing of that kind, so
an unrelated repo stays quiet. Messages carry package names, versions and
file:line only, never file contents, the same rule as every other check.

Policy, kept in one place so it is easy to change (docs/decisions.md #23):

  FAIL  known vulnerabilities; a base image or runtime past end of life
  WARN  behind by a major version; floating refs; deprecated action runtimes;
        a lookup that failed, so the result is incomplete
  PASS  checked and clean

Standard library only. Cargo.toml parsing needs Python 3.11+ (tomllib).
Network: registry.npmjs.org, pypi.org, index.crates.io, endoflife.date, and
the host of each referenced action (api.github.com, or a Forgejo's /api/v1).
A GitHub token in GH_TOKEN or GITHUB_TOKEN raises api.github.com's rate
limit; it is sent only to api.github.com and never printed.
"""
import datetime
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request

TIMEOUT = 8
LOOKUP_CAP = 100  # per ecosystem per repo, so one huge monorepo cannot run for minutes
UA = "conformIT-audit (+https://github.com/almadon/conformIT)"
TODAY = datetime.date.today()
EOL_SOON_DAYS = 120

# Actions whose ref is a selector, not a version: dtolnay/rust-toolchain@stable
# installs whatever Rust currently calls stable, so pinning it to a commit
# defeats its purpose. Not flagged as floating. flashDK's audit found this
# (STATE.md, "Findings from flashDK's application" #4); it was recorded there
# and never encoded until these checks needed it.
DELIBERATELY_FLOATING = {("dtolnay", "rust-toolchain"): {"stable", "beta", "nightly"}}

# Action runtimes GitHub has announced as deprecated. Update with the
# announcements; checked 2026-10-12, when node20 was already being forced
# onto node24 on hosted runners.
DEPRECATED_RUNTIMES = {"node12", "node16", "node20"}

SKIP_PARTS = ("node_modules/", ".venv/", "venv/", "site-packages/", "/vendor/")


def emit(level, msg):
    print(f"{level}\t{' '.join(str(msg).split())}")


class Net:
    """Tiny HTTP client: cached, with failures counted instead of raised."""

    def __init__(self):
        self.cache = {}
        self.failures = 0

    def get(self, url, auth=False, allow_404=False):
        if url in self.cache:
            return self.cache[url]
        headers = {"User-Agent": UA, "Accept": "application/json"}
        if auth:
            tok = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
            if tok:
                headers["Authorization"] = f"Bearer {tok}"
        body = None
        for attempt in range(2):
            try:
                req = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
                    body = r.read().decode("utf-8", "replace")
                break
            except urllib.error.HTTPError as e:
                if e.code == 404:
                    body = None
                    if not allow_404:
                        self.failures += 1
                    break
                if attempt == 1:
                    self.failures += 1
            except Exception:
                if attempt == 1:
                    self.failures += 1
        self.cache[url] = body
        return body

    def json(self, url, **kw):
        b = self.get(url, **kw)
        if b is None:
            return None
        try:
            return json.loads(b)
        except ValueError:
            return None


NET = Net()


def tracked_files(repo):
    try:
        out = subprocess.run(
            ["git", "-C", repo, "ls-files"], capture_output=True, text=True, timeout=30
        ).stdout
        files = [l for l in out.splitlines() if l]
    except Exception:
        files = []
    if not files:
        for root, dirs, fs in os.walk(repo):
            dirs[:] = [d for d in dirs if d != ".git"]
            for f in fs:
                files.append(os.path.relpath(os.path.join(root, f), repo))
    return [f for f in files if not any(p in "/" + f for p in SKIP_PARTS)]


def read(repo, rel):
    try:
        with open(os.path.join(repo, rel), encoding="utf-8", errors="replace") as fh:
            return fh.read()
    except OSError:
        return ""


def parse_ver(s):
    """(major, minor, patch) from a leading version, or None. Pre-releases -> None."""
    m = re.match(r"^[vV]?(\d+)(?:\.(\d+))?(?:\.(\d+))?(.*)$", str(s).strip())
    if not m:
        return None
    rest = m.group(4)
    if rest and re.match(r"^[-+.]?(?:[a-zA-Z]|\d*-)", rest):
        if re.search(r"(?i)(alpha|beta|rc|pre|dev|snapshot|next|canary)", rest):
            return None
    return tuple(int(x) if x else 0 for x in m.groups()[:3])


def breaking_key(v):
    """The part of a version whose change is breaking: major, or major.minor for 0.x."""
    return (v[0],) if v[0] > 0 else (0, v[1])


def sample(items, n=3):
    items = list(items)
    s = "; ".join(items[:n])
    return s + (f"; +{len(items) - n} more" if len(items) > n else "")


def ancestors(rel):
    """Directories from the file's own up to the repo root ('')."""
    d = os.path.dirname(rel)
    out = []
    while True:
        out.append(d)
        if not d:
            break
        d = os.path.dirname(d)
    return out


# ---------------------------------------------------------------- osv-summary

def cmd_osv_summary(osv_path, repo):
    try:
        data = json.load(open(osv_path))
    except Exception:
        emit("WARN", "osv-scanner produced no readable report: dependency vulnerability check incomplete")
        return
    results = data.get("results") or []
    if not results:
        return
    root = os.path.abspath(repo)

    def rel(p):
        p = p.replace(root + "/", "").lstrip("./") if p.startswith(("/", ".")) else p
        return p or "."

    by_eco = {}
    locks = set()
    for res in results:
        src = rel(res.get("source", {}).get("path", "?"))
        locks.add(src)
        for pkg in res.get("packages", []):
            vulns = pkg.get("vulnerabilities") or []
            if not vulns:
                continue
            p = pkg["package"]
            adv = len(pkg.get("groups") or []) or len(vulns)
            by_eco.setdefault(p.get("ecosystem", "?"), {})[
                (p.get("name"), p.get("version"))
            ] = (adv, src)
    if not by_eco:
        emit("PASS", f"no known vulnerabilities in {len(locks)} lockfile(s) (osv-scanner)")
        return
    for eco in sorted(by_eco):
        pk = by_eco[eco]
        advs = sum(a for a, _ in pk.values())
        worst = sorted(pk.items(), key=lambda kv: -kv[1][0])
        smp = [f"{n}@{v} ({a})" for (n, v), (a, _) in worst]
        files = sorted({s for _, s in pk.values()})
        emit(
            "FAIL",
            f"{len(pk)} {eco} package(s) with known vulnerabilities, {advs} advisories "
            f"(osv-scanner), e.g. {sample(smp)} in {sample(files, 2)}",
        )


# ------------------------------------------------------------------ lockfiles

NPM_LOCKS = ("package-lock.json", "npm-shrinkwrap.json", "yarn.lock", "pnpm-lock.yaml", "bun.lock", "bun.lockb")
PY_LOCKS = ("poetry.lock", "uv.lock", "Pipfile.lock", "pdm.lock")


def _has_lock(files, rel, names):
    fs = set(files)
    return any((os.path.join(d, n) if d else n) in fs for d in ancestors(rel) for n in names)


def _py_requirements_pinned(text):
    reqs = [
        l.split("#")[0].strip()
        for l in text.splitlines()
        if l.strip() and not l.strip().startswith(("#", "-", "git+", "http"))
    ]
    return bool(reqs) and all("==" in r for r in reqs)


def cmd_lockfiles(repo):
    files = tracked_files(repo)
    missing = []
    for f in files:
        base = os.path.basename(f)
        if base == "package.json":
            try:
                pj = json.loads(read(repo, f) or "{}")
            except ValueError:
                continue
            deps = {**pj.get("dependencies", {}), **pj.get("devDependencies", {})}
            if deps and not _has_lock(files, f, NPM_LOCKS):
                missing.append(f)
        elif base == "pyproject.toml":
            txt = read(repo, f)
            if re.search(r"(?m)^\s*dependencies\s*=\s*\[", txt) or "[tool.poetry.dependencies]" in txt:
                if not _has_lock(files, f, PY_LOCKS):
                    missing.append(f)
        elif re.match(r"^requirements.*\.txt$", base):
            if not _py_requirements_pinned(read(repo, f)) and not _has_lock(files, f, PY_LOCKS):
                missing.append(f + " (unpinned)")
        elif base == "Cargo.toml":
            txt = read(repo, f)
            if re.search(r"(?m)^\[(dev-|build-)?dependencies\]", txt) and not _has_lock(files, f, ("Cargo.lock",)):
                missing.append(f)
    if missing:
        emit(
            "WARN",
            f"{len(missing)} manifest(s) with no lockfile or unpinned versions, so what gets "
            f"installed is not reproducible and the vulnerability check cannot see it: {sample(missing)}",
        )


# ------------------------------------------------------------------- outdated

def _npm_latest(name):
    j = NET.json("https://registry.npmjs.org/" + urllib.parse.quote(name, safe="@") + "/latest")
    return parse_ver(j["version"]) if j and "version" in j else None


def _pypi_latest(name):
    j = NET.json(f"https://pypi.org/pypi/{urllib.parse.quote(name)}/json")
    return parse_ver(j["info"]["version"]) if j else None


def _crate_latest(name):
    n = name.lower()
    path = {1: f"1/{n}", 2: f"2/{n}", 3: f"3/{n[0]}/{n}"}.get(len(n), f"{n[:2]}/{n[2:4]}/{n}")
    b = NET.get("https://index.crates.io/" + path)
    best = None
    for line in (b or "").splitlines():
        try:
            j = json.loads(line)
        except ValueError:
            continue
        if j.get("yanked"):
            continue
        v = parse_ver(j.get("vers", ""))
        if v and (best is None or v > best):
            best = v
    return best


def _report_outdated(eco, checked, behind_major, behind_minor, capped_from, fail0):
    if not checked:
        return
    cap = f" (first {LOOKUP_CAP} of {capped_from})" if capped_from > LOOKUP_CAP else ""
    if behind_major:
        smp = [f"{n} {c} -> {l}" for n, c, l in behind_major]
        emit(
            "WARN",
            f"{len(behind_major)} of {len(checked)} direct {eco} dependencies are a breaking version "
            f"behind latest{cap}: {sample(smp)}",
        )
    elif len(checked) > 0:
        emit(
            "PASS",
            f"no direct {eco} dependency is a breaking version behind latest "
            f"({len(checked)} checked{cap}, {behind_minor} behind within the same major)",
        )
    if NET.failures > fail0:
        emit("WARN", f"{NET.failures - fail0} {eco} registry lookup(s) failed, so the outdated result is incomplete")


def _vs(v):
    return ".".join(str(x) for x in v)


def cmd_outdated(repo):
    files = tracked_files(repo)
    fileset = set(files)

    # npm: direct deps from package.json, resolved versions from package-lock.json
    seen, behind, minor = {}, [], 0
    f0 = NET.failures
    total = 0
    for f in files:
        if os.path.basename(f) != "package.json":
            continue
        try:
            pj = json.loads(read(repo, f) or "{}")
        except ValueError:
            continue
        lockrel = next(
            (
                os.path.join(d, "package-lock.json") if d else "package-lock.json"
                for d in ancestors(f)
                if (os.path.join(d, "package-lock.json") if d else "package-lock.json") in fileset
            ),
            None,
        )
        if not lockrel:
            continue
        try:
            lock = json.loads(read(repo, lockrel) or "{}")
        except ValueError:
            continue
        pk = lock.get("packages", {})
        pdir = os.path.dirname(f)
        for sect in ("dependencies", "devDependencies", "optionalDependencies"):
            for name, spec in (pj.get(sect) or {}).items():
                if not isinstance(spec, str) or re.match(r"^(file:|link:|git|http|workspace:|npm:|github:)", spec):
                    continue
                cur = None
                for key in (
                    (pdir + "/node_modules/" + name) if pdir else None,
                    "node_modules/" + name,
                ):
                    if key and key in pk and pk[key].get("version"):
                        cur = parse_ver(pk[key]["version"])
                        break
                if cur and name not in seen:
                    seen[name] = cur
    total = len(seen)
    for i, (name, cur) in enumerate(sorted(seen.items())):
        if i >= LOOKUP_CAP:
            break
        lat = _npm_latest(name)
        if not lat:
            continue
        if breaking_key(lat) > breaking_key(cur):
            behind.append((name, _vs(cur), _vs(lat)))
        elif lat > cur:
            minor += 1
    _report_outdated("npm", list(seen)[:LOOKUP_CAP], behind, minor, total, f0)

    # PyPI: pinned requirements only; an unpinned one has no "current" to compare
    seen, behind, minor = {}, [], 0
    f0 = NET.failures
    for f in files:
        if not re.match(r"^requirements.*\.txt$", os.path.basename(f)):
            continue
        for line in read(repo, f).splitlines():
            m = re.match(r"^\s*([A-Za-z0-9][A-Za-z0-9_.\-]*)(?:\[[^\]]*\])?\s*==\s*([^\s;#]+)", line)
            if m and parse_ver(m.group(2)):
                seen.setdefault(m.group(1).lower(), parse_ver(m.group(2)))
    total = len(seen)
    for i, (name, cur) in enumerate(sorted(seen.items())):
        if i >= LOOKUP_CAP:
            break
        lat = _pypi_latest(name)
        if not lat:
            continue
        if breaking_key(lat) > breaking_key(cur):
            behind.append((name, _vs(cur), _vs(lat)))
        elif lat > cur:
            minor += 1
    _report_outdated("PyPI", list(seen)[:LOOKUP_CAP], behind, minor, total, f0)

    # crates.io: names from Cargo.toml tables, resolved versions from Cargo.lock
    tomllib = None
    try:
        import tomllib  # Python 3.11+
    except ImportError:
        pass
    tomls = [f for f in files if os.path.basename(f) == "Cargo.toml"]
    if tomls and not tomllib:
        emit("WARN", "Cargo outdated check skipped: reading Cargo.toml needs Python 3.11 or newer")
        return
    names = set()
    for f in tomls:
        try:
            doc = tomllib.loads(read(repo, f))
        except Exception:
            continue
        tables = [doc.get(k, {}) for k in ("dependencies", "dev-dependencies", "build-dependencies")]
        tables.append(doc.get("workspace", {}).get("dependencies", {}))
        for tgt in doc.get("target", {}).values():
            tables += [tgt.get(k, {}) for k in ("dependencies", "dev-dependencies", "build-dependencies")]
        for t in tables:
            for name, spec in t.items():
                if isinstance(spec, dict):
                    if ("path" in spec or "git" in spec) and "version" not in spec:
                        continue
                    name = spec.get("package", name)
                names.add(name)
    locks = {}
    for f in files:
        if os.path.basename(f) == "Cargo.lock":
            for blk in re.findall(r'\[\[package\]\]\s*\nname = "([^"]+)"\s*\nversion = "([^"]+)"', read(repo, f)):
                v = parse_ver(blk[1])
                if v and (blk[0] not in locks or v > locks[blk[0]]):
                    locks[blk[0]] = v
    seen = {n: locks[n] for n in sorted(names) if n in locks}
    behind, minor = [], 0
    f0 = NET.failures
    total = len(seen)
    for i, (name, cur) in enumerate(seen.items()):
        if i >= LOOKUP_CAP:
            break
        lat = _crate_latest(name)
        if not lat:
            continue
        if breaking_key(lat) > breaking_key(cur):
            behind.append((name, _vs(cur), _vs(lat)))
        elif lat > cur:
            minor += 1
    _report_outdated("crates.io", list(seen)[:LOOKUP_CAP], behind, minor, total, f0)


# ----------------------------------------------------------------- deprecated

def cmd_deprecated(repo):
    out, nlocks = [], 0
    for f in tracked_files(repo):
        if os.path.basename(f) not in ("package-lock.json", "npm-shrinkwrap.json"):
            continue
        try:
            lock = json.loads(read(repo, f) or "{}")
        except ValueError:
            continue
        nlocks += 1
        for key, meta in (lock.get("packages") or {}).items():
            if key and isinstance(meta, dict) and meta.get("deprecated"):
                name = key.split("node_modules/")[-1]
                out.append(f"{name}@{meta.get('version', '?')}")
        for name, meta in (lock.get("dependencies") or {}).items():  # lockfile v1
            if isinstance(meta, dict) and meta.get("deprecated"):
                out.append(f"{name}@{meta.get('version', '?')}")
    out = sorted(set(out))
    if out:
        emit("WARN", f"{len(out)} deprecated npm package(s) recorded in lockfiles, e.g. {sample(out)}")
    elif nlocks:
        emit("PASS", f"no deprecated npm packages recorded in {nlocks} lockfile(s)")


# -------------------------------------------------------------------- actions

WORKFLOW_DIRS = {".github/workflows": "github.com", ".forgejo/workflows": "code.forgejo.org", ".gitea/workflows": "github.com"}
USES_RE = re.compile(r"^\s*(?:-\s*)?uses:\s*['\"]?([^\s'\"#]+)['\"]?\s*(?:#\s*(.*))?$")
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
_latest_cache = {}


def action_latest(host, owner, repo):
    key = (host, owner, repo)
    if key in _latest_cache:
        return _latest_cache[key]
    ver = None
    if host == "github.com":
        j = NET.json(f"https://api.github.com/repos/{owner}/{repo}/releases/latest", auth=True, allow_404=True)
        if j and j.get("tag_name"):
            ver = (parse_ver(j["tag_name"]), j["tag_name"])
        if not ver:
            tags = NET.json(f"https://api.github.com/repos/{owner}/{repo}/tags?per_page=100", auth=True)
            ver = _best_tag([t.get("name", "") for t in tags or []])
    else:
        j = NET.json(f"https://{host}/api/v1/repos/{owner}/{repo}/releases/latest", allow_404=True)
        if j and j.get("tag_name"):
            ver = (parse_ver(j["tag_name"]), j["tag_name"])
        if not ver:
            names = []
            for page in (1, 2):
                tags = NET.json(f"https://{host}/api/v1/repos/{owner}/{repo}/tags?limit=50&page={page}")
                names += [t.get("name", "") for t in tags or []]
            ver = _best_tag(names)
    _latest_cache[key] = ver if ver and ver[0] else None
    return _latest_cache[key]


def _best_tag(names):
    best = None
    for n in names:
        v = parse_ver(n)
        if v and (best is None or v > best[0]):
            best = (v, n)
    return best


def action_runtime(host, owner, repo, sub, ref):
    for fname in ("action.yml", "action.yaml"):
        path = f"{sub + '/' if sub else ''}{fname}"
        if host == "github.com":
            url = f"https://raw.githubusercontent.com/{owner}/{repo}/{ref}/{path}"
        else:
            kind = "commit" if SHA_RE.match(ref) else ("tag" if parse_ver(ref) else "branch")
            url = f"https://{host}/{owner}/{repo}/raw/{kind}/{ref}/{path}"
        body = NET.get(url, allow_404=True)
        if body:
            m = re.search(r"(?m)^\s*using:\s*['\"]?([A-Za-z0-9_]+)", body)
            return m.group(1) if m else None
    return None


def cmd_actions(repo):
    refs = []  # (workflow, line, host, owner, repo, sub, ref, comment)
    for f in tracked_files(repo):
        d = next((d for d in WORKFLOW_DIRS if f.startswith(d + "/")), None)
        is_action_file = re.match(r"^\.(github|forgejo|gitea)/actions/.+/action\.ya?ml$", f)
        if not d and not is_action_file:
            continue
        if d and not re.search(r"\.ya?ml$", f):
            continue
        default_host = WORKFLOW_DIRS[d] if d else ("code.forgejo.org" if f.startswith(".forgejo/") else "github.com")
        for i, line in enumerate(read(repo, f).splitlines(), 1):
            m = USES_RE.match(line)
            if not m:
                continue
            spec, comment = m.group(1), (m.group(2) or "")
            if spec.startswith(("./", "../", "docker://")) or "@" not in spec or "${{" in spec:
                continue
            body, ref = spec.rsplit("@", 1)
            host = default_host
            if "://" in body:
                u = urllib.parse.urlparse(body)
                host, body = u.netloc, u.path.lstrip("/")
            parts = body.split("/")
            if len(parts) < 2:
                continue
            refs.append((f, i, host, parts[0], parts[1], "/".join(parts[2:]), ref, comment))
    if not refs:
        return
    outdated, floating, nosha, deprecated, unknown = [], [], 0, [], 0
    f0 = NET.failures
    uniq = {}
    for f, i, host, o, r, sub, ref, comment in refs:
        uniq.setdefault((host, o, r, sub, ref, comment), []).append(f"{f}:{i}")
    for (host, o, r, sub, ref, comment), where in uniq.items():
        name = f"{o}/{r}" + (f"/{sub}" if sub and not sub.endswith((".yml", ".yaml")) else "")
        cur = None
        if SHA_RE.match(ref):
            cm = re.match(r"^[vV]?\d+(?:\.\d+){0,2}\b", comment.strip())
            cur = parse_ver(cm.group(0)) if cm else None
            if cur is None:
                nosha += 1
        else:
            m = re.match(r"^(?:release/)?[vV]?(\d+(?:\.\d+){0,2})$", ref)
            if m:
                cur = parse_ver(m.group(1))
            elif ref in DELIBERATELY_FLOATING.get((o, r), ()):
                pass  # a selector by design; see DELIBERATELY_FLOATING
            else:
                floating.append(f"{name}@{ref} ({where[0]})")
        if cur is not None:
            lat = action_latest(host, o, r)
            if lat is None:
                unknown += 1
            elif lat[0][0] > cur[0]:
                outdated.append(f"{name}@{ref} -> {lat[1]} ({where[0]})")
        if not (sub or "").endswith((".yml", ".yaml")):
            rt = action_runtime(host, o, r, sub, ref)
            if rt in DEPRECATED_RUNTIMES:
                deprecated.append(f"{name}@{ref[:12]} runs {rt} ({where[0]})")
    n = len(uniq)
    if outdated:
        emit("WARN", f"{len(outdated)} of {n} action reference(s) are a major version behind: {sample(outdated)}")
    else:
        emit("PASS", f"none of {n} action reference(s) is a major version behind latest")
    if floating:
        emit("WARN", f"{len(floating)} action reference(s) float on a branch or unversioned ref instead of a pinned version: {sample(floating)}")
    if nosha:
        emit("WARN", f"{nosha} action reference(s) pinned by commit SHA with no `# vX` comment, so staleness cannot be checked")
    if deprecated:
        emit("WARN", f"{len(deprecated)} action reference(s) run on a deprecated runtime: {sample(deprecated)}")
    if unknown or NET.failures > f0:
        emit("WARN", f"{unknown} action version lookup(s) found no release and {NET.failures - f0} request(s) failed, so the result above is incomplete")


# ------------------------------------------------------------------------ eol

IMAGE_PRODUCT = {
    "node": "nodejs", "python": "python", "ubuntu": "ubuntu", "debian": "debian",
    "alpine": "alpine", "postgres": "postgresql", "mysql": "mysql", "mariadb": "mariadb",
    "redis": "redis", "nginx": "nginx", "golang": "go", "rust": "rust", "php": "php",
    "ruby": "ruby", "mongo": "mongodb", "httpd": "apache-http-server", "traefik": "traefik",
    "caddy": "caddy", "memcached": "memcached",
}
VERSION_KEYS = {"python": "python", "node": "nodejs", "go": "go", "ruby": "ruby", "php": "php"}
_eol_cache = {}


def eol_cycles(product):
    if product not in _eol_cache:
        _eol_cache[product] = NET.json(f"https://endoflife.date/api/{product}.json")
    return _eol_cache[product]


def eol_status(product, version=None, codename=None):
    """(eol_date | None, label) for a version or codename, or None if unknown."""
    cycles = eol_cycles(product)
    if not cycles:
        return None
    hit = None
    if codename:
        for c in cycles:
            if (c.get("codename") or "").lower().split(" ")[0] == codename.lower():
                hit = c
                break
    elif version:
        parts = version.split(".")
        for k in range(len(parts), 0, -1):
            want = ".".join(parts[:k])
            hit = next((c for c in cycles if str(c.get("cycle")) == want), None)
            if hit:
                break
    if not hit:
        return None
    eol = hit.get("eol")
    if eol is True:
        return (TODAY, str(hit["cycle"]))
    if isinstance(eol, str):
        try:
            return (datetime.date.fromisoformat(eol), str(hit["cycle"]))
        except ValueError:
            return None
    return (None, str(hit["cycle"]))  # eol is False: no end date announced


def _check_ref(items, product, tag, where, label):
    """items: dict of buckets to append to."""
    codename = None
    m = re.match(r"^[vV]?(\d+(?:\.\d+)*)", tag or "")
    ver = m.group(1) if m else None
    if not ver and tag:
        codename = re.split(r"[-_.]", tag)[0].lower()
    if not ver and not codename:
        return
    st = eol_status(product, ver, codename)
    if st is None:
        return
    items["checked"] += 1
    when, cycle = st
    if when is None:
        return
    days = (when - TODAY).days
    if days <= 0:
        items["eol"].append(f"{label} (EOL {when}, {where})")
    elif days <= EOL_SOON_DAYS:
        items["soon"].append(f"{label} (EOL {when}, {where})")


def cmd_eol(repo):
    items = {"checked": 0, "eol": [], "soon": [], "float": []}
    f0 = NET.failures
    for f in tracked_files(repo):
        base = os.path.basename(f)
        is_docker = base.startswith("Dockerfile") or base.endswith(".dockerfile") or base == "Containerfile"
        is_compose = re.match(r"^(docker-)?compose.*\.ya?ml$", base) or re.match(r"^docker-compose.*\.ya?ml$", base)
        is_wf = any(f.startswith(d + "/") for d in WORKFLOW_DIRS) and re.search(r"\.ya?ml$", f)
        if not (is_docker or is_compose or is_wf):
            continue
        aliases = set()
        for i, line in enumerate(read(repo, f).splitlines(), 1):
            where = f"{f}:{i}"
            image = None
            if is_docker:
                m = re.match(r"(?i)^\s*FROM\s+(?:--\S+\s+)*(\S+)(?:\s+AS\s+(\S+))?", line)
                if m:
                    image = m.group(1)
                    if m.group(2):
                        aliases.add(m.group(2).lower())
            elif is_compose:
                m = re.match(r"^\s*image:\s*['\"]?([^\s'\"#]+)", line)
                if m:
                    image = m.group(1)
            if image:
                if image.lower() in aliases or image == "scratch" or "$" in image:
                    continue
                name, digest = (image.split("@", 1) + [None])[:2]
                last = name.rsplit("/", 1)[-1]
                tag = None
                if ":" in last:
                    name, tag = name.rsplit(":", 1)
                short = re.sub(r"^(docker\.io/)?(library/)?", "", name)
                product = IMAGE_PRODUCT.get(short) if "/" not in short else None
                if not product:
                    continue
                if (tag is None or tag == "latest") and not digest:
                    items["float"].append(f"{short}:{tag or '(no tag)'} ({where})")
                    continue
                if tag:
                    _check_ref(items, product, tag, where, f"{short}:{tag}")
            if is_wf:
                m = re.match(r"^\s*(python|node|go|ruby|php)-version:\s*(.+?)\s*(?:#.*)?$", line)
                if m and "${{" not in m.group(2):
                    for v in re.findall(r"\d+(?:\.\d+)*", m.group(2)):
                        _check_ref(items, IMAGE_PRODUCT.get(m.group(1)) or VERSION_KEYS[m.group(1)], v, where, f"{m.group(1)} {v}")
    if items["eol"]:
        emit("FAIL", f"{len(items['eol'])} base image or runtime reference(s) past end of life: {sample(items['eol'])}")
    if items["soon"]:
        emit("WARN", f"{len(items['soon'])} base image or runtime reference(s) reach end of life within {EOL_SOON_DAYS} days: {sample(items['soon'])}")
    if items["float"]:
        emit("WARN", f"{len(items['float'])} base image(s) float on :latest or have no tag, so builds change underneath you: {sample(items['float'])}")
    if items["checked"] and not items["eol"] and not items["soon"]:
        emit("PASS", f"{items['checked']} base image or runtime version(s) checked, none past or near end of life")
    if NET.failures > f0:
        emit("WARN", f"{NET.failures - f0} end-of-life lookup(s) failed, so the result above is incomplete")


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    cmd, args = argv[1], argv[2:]
    table = {
        "osv-summary": (cmd_osv_summary, 2),
        "lockfiles": (cmd_lockfiles, 1),
        "outdated": (cmd_outdated, 1),
        "deprecated": (cmd_deprecated, 1),
        "actions": (cmd_actions, 1),
        "eol": (cmd_eol, 1),
    }
    if cmd not in table or len(args) != table[cmd][1]:
        print(__doc__)
        return 2
    try:
        table[cmd][0](*args)
    except Exception as e:  # a helper bug must never take the audit down with it
        emit("WARN", f"{cmd} check failed internally ({type(e).__name__}); result incomplete")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
