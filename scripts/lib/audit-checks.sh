#!/usr/bin/env bash
# conformIT: the checks a single repository is audited against.
#
# Sourced by scripts/conform.sh, not run directly. Every check here is
# read-only against the target and prints only filenames, line numbers,
# and short labels, never file contents, since this can run against
# repositories this project doesn't own and the output can land in a
# public CI job summary. See docs/decisions.md #12 and #13.
#
# Portable to bash 3.2 (macOS system bash), matching every other script
# and hook in this repo.

CONFORMIT_PASS=0
CONFORMIT_WARN=0
CONFORMIT_FAIL=0
CONFORMIT_CRIT=0
CONFORMIT_DETAILS=""

_conformit_note() {
  # _conformit_note <symbol> <message>
  CONFORMIT_DETAILS="${CONFORMIT_DETAILS}- $1 $2"$'\n'
  case "$1" in
    "PASS") CONFORMIT_PASS=$((CONFORMIT_PASS + 1)) ;;
    "WARN") CONFORMIT_WARN=$((CONFORMIT_WARN + 1)) ;;
    "FAIL") CONFORMIT_FAIL=$((CONFORMIT_FAIL + 1)) ;;
    "CRIT") CONFORMIT_CRIT=$((CONFORMIT_CRIT + 1)) ;;
  esac
}

_conformit_symbol() {
  case "$1" in
    PASS) printf '%s' "✅" ;;
    WARN) printf '%s' "⚠️" ;;
    FAIL) printf '%s' "❌" ;;
    CRIT) printf '%s' "🚨" ;;
  esac
}

# Mirrors templates/.githooks/pre-commit's exclusions (fenced code, inline
# code spans, Before:/After: examples, an explicit <!-- conformit:allow -->
# marker) so a repo that passes its own copy of that hook also passes
# here. Duplicated rather than shared: the hook is meant to be dropped
# into a repo as one self-contained file, and this audit runs from
# conformIT's own checkout against a clone it doesn't control, so neither
# side can assume the other's files exist. The two must be kept in sync
# by hand; see docs/decisions.md #12.
_conformit_scan_em_dash() {
  awk -v file="$1" '
    /^[[:space:]]*(```|~~~)/ { fence = !fence; next }
    fence { next }
    /conformit:allow/ { next }
    /^[[:space:]]*(Before|After):/ { next }
    {
      line = $0
      gsub(/`[^`]*`/, "", line)
      if (index(line, "\342\200\224") > 0)
        printf "%s:%d\n", file, NR
    }
  ' "$1"
}

# The set of tracked, non-binary, reasonably-sized files worth scanning for
# sensitive content. `git ls-files` respects what's actually committed;
# binary detection is `grep -Iq`'s (a quick heuristic, not a MIME sniff);
# the size cap keeps a vendored blob from making the scan slow.
_conformit_scannable_files() {
  local repo="$1"
  ( cd "$repo" && git ls-files 2>/dev/null ) | while IFS= read -r p; do
    [ -f "$repo/$p" ] || continue
    local sz
    sz=$(wc -c < "$repo/$p" 2>/dev/null | tr -d ' ')
    [ -n "$sz" ] && [ "$sz" -gt 1000000 ] && continue
    grep -Iq . "$repo/$p" 2>/dev/null && printf '%s\n' "$p"
  done
}

# Prints "<line-number>:<content>" for a file, the same shape `grep -n`
# produces, so callers can pipe pattern matching through this instead of
# grepping the raw file directly. For markdown, strips fenced code
# blocks, inline code spans, and lines carrying an explicit
# <!-- conformit:allow --> marker first: a documentation example that
# illustrates what a leaked key or a private IP looks like is not the
# same thing as one actually being present, exactly the distinction
# _conformit_scan_em_dash already draws for prose. Found necessary by
# this repo's own private-URL check flagging its own decisions.md, which
# was quoting an example IP inside a discussion of a false positive.
# Non-markdown files pass through unfiltered: there's no "this is just an
# example" convention in source code the way there is in prose, and a
# hardcoded value in a real source file is a different kind of finding.
_conformit_prose_or_raw() {
  local file="$1"
  case "$file" in
    *.md)
      awk '
        /^[[:space:]]*(```|~~~)/ { fence = !fence; next }
        fence { next }
        /conformit:allow/ { next }
        {
          line = $0
          gsub(/`[^`]*`/, "", line)
          print NR":" line
        }
      ' "$file"
      ;;
    *)
      awk '{ print NR":" $0 }' "$file"
      ;;
  esac
}

# --- secrets ----------------------------------------------------------------
#
# Prefers gitleaks (github.com/gitleaks/gitleaks, MIT) if it's on PATH,
# since a maintained rule set beats a handful of hand-rolled patterns for
# something this consequential. CI installs a pinned, checksum-verified
# copy (docs/credits.md); a local run uses whatever's on the operator's
# PATH, or falls back to the heuristic below with reduced coverage, noted
# as such in the report rather than presented as equivalent.
#
# Scans the working tree only (gitleaks in `dir` mode), not full git
# history. A secret already removed from HEAD but still present in an
# earlier commit is a real, separate risk this does not check for; see
# docs/decisions.md #13.
_conformit_scan_secrets_gitleaks() {
  local repo="$1"
  local report
  report="$(mktemp)"
  # Run from inside the repo against `.`, not the absolute path: gitleaks
  # reports its `File` field relative to whatever source path it was
  # given, so scanning an absolute path puts an absolute path (this
  # runner's own temp-directory layout, for a CI-cloned target) straight
  # into what's meant to be a clean, repo-relative report. Found the same
  # way as the identical em-dash-scanner bug: by actually running this
  # against a real clone, not by inspection.
  if ! ( cd "$repo" && gitleaks dir . --report-format json --report-path "$report" \
    --exit-code 0 --no-banner >/dev/null 2>&1 ); then
    rm -f "$report"
    return 1
  fi
  if command -v python3 >/dev/null 2>&1; then
    python3 - "$report" "$repo" <<'PY'
import json, sys
report_path, repo = sys.argv[1], sys.argv[2]
try:
    with open(report_path) as f:
        data = json.load(f)
except Exception:
    sys.exit(0)
for item in data or []:
    f = item.get("File", "?")
    line = item.get("StartLine", "?")
    rule = item.get("RuleID", "unknown-rule")
    print(f"{f}:{line}:{rule}")
PY
  fi
  rm -f "$report"
  return 0
}

# Well-known, high-confidence key formats only: prefixed tokens and PEM
# headers. Deliberately does not attempt generic high-entropy detection,
# which needs real analysis to avoid drowning in false positives; that
# gap is exactly what gitleaks is for. Documented as reduced coverage.
_conformit_scan_secrets_heuristic() {
  local repo="$1"
  local f
  _conformit_scannable_files "$repo" | while IFS= read -r f; do
    _conformit_prose_or_raw "$repo/$f" \
      | grep -E \
        '(AKIA[0-9A-Z]{16}|-----BEGIN[A-Z ]*PRIVATE KEY-----|gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{20,}|xox[baprs]-[A-Za-z0-9-]{10,}|AIza[0-9A-Za-z_-]{35}|sk_(live|test)_[A-Za-z0-9]{16,})' \
      | sed -E "s#^([0-9]+):.*#${f}:\1:heuristic-known-key-format#"
  done
}

_conformit_rotate_warning() {
  echo "  If genuine, treat this credential as already compromised:"
  echo "  rotate it immediately and notify every collaborator or org"
  echo "  member with access. Deleting it from this file does not undo"
  echo "  the exposure; git history and any forks may still contain it."
}

# --- email addresses ---------------------------------------------------------
#
# "Excluding git author ones," per the maintainer's request: the allow
# list is every author and committer email in this repo's own history,
# since those are already public by the nature of a public git repo and
# aren't a new leak. noreply addresses and RFC 2606 example domains are
# excluded too, as conventional placeholders rather than real contacts.
_conformit_scan_emails() {
  local repo="$1"
  local allowed
  allowed="$(cd "$repo" && git log --all --format='%ae%n%ce' 2>/dev/null \
    | tr '[:upper:]' '[:lower:]' | sort -u)"

  local f numbered ln content email lower
  _conformit_scannable_files "$repo" | while IFS= read -r f; do
    _conformit_prose_or_raw "$repo/$f" | while IFS= read -r numbered; do
      ln="${numbered%%:*}"
      content="${numbered#*:}"
      printf '%s\n' "$content" \
        | grep -oE '[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}' \
        | while IFS= read -r email; do
          lower="$(printf '%s' "$email" | tr '[:upper:]' '[:lower:]')"
          case "$lower" in
            noreply@*|no-reply@*) continue ;;
            *@example.com|*@example.org|*@example.net|*@test.com|*@domain.com|*@yourdomain.com) continue ;;
          esac
          if ! printf '%s\n' "$allowed" | grep -qxF "$lower"; then
            printf '%s:%s:%s\n' "$f" "$ln" "$email"
          fi
        done
    done
  done
}

# --- private-service URLs and non-routable addresses -------------------------
#
# RFC 1918 private ranges and common internal-DNS suffixes. Excludes
# localhost/loopback (ubiquitous in dev docs, not a leak) and the RFC
# 5737 documentation ranges (192.0.2.0/24, 198.51.100.0/24,
# 203.0.113.0/24), which exist specifically so examples don't need to
# borrow a real address.
_conformit_scan_private_urls() {
  local repo="$1"
  local f
  _conformit_scannable_files "$repo" | while IFS= read -r f; do
    _conformit_prose_or_raw "$repo/$f" \
      | grep -E \
        '(\b10\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\b|\b172\.(1[6-9]|2[0-9]|3[01])\.[0-9]{1,3}\.[0-9]{1,3}\b|\b192\.168\.[0-9]{1,3}\.[0-9]{1,3}\b|[A-Za-z0-9-]+\.(internal|corp|lan|ts\.net)\b)' \
    | grep -vE '\b(127\.0\.0\.1|0\.0\.0\.0|192\.0\.2\.[0-9]{1,3}|198\.51\.100\.[0-9]{1,3}|203\.0\.113\.[0-9]{1,3})\b' \
    | sed -E "s#^([0-9]+):.*#${f}:\1#"
  done
}

conformit_audit_repo() {
  # conformit_audit_repo <repo-path> <label> <rows-file>
  # Prints a markdown "details" section to stdout. Appends one summary row
  # to <rows-file>. Sets CONFORMIT_CRIT before returning so the caller can
  # decide whether this run should fail loudly.
  local REPO="$1"
  local LABEL="$2"
  local ROWS_FILE="$3"

  CONFORMIT_PASS=0
  CONFORMIT_WARN=0
  CONFORMIT_FAIL=0
  CONFORMIT_CRIT=0
  CONFORMIT_DETAILS=""

  # --- required files, per docs/documentation-standard.md -----------------
  local f
  for f in README.md LICENSE AGENTS.md docs/STATE.md docs/decisions.md CHANGELOG.md; do
    if [ -f "$REPO/$f" ]; then
      _conformit_note PASS "\`$f\` present"
    else
      _conformit_note FAIL "\`$f\` missing"
    fi
  done

  # Conditional: only required if the project has running components,
  # trust boundaries, or dependencies to describe. An outside audit can't
  # know that on its own, so a missing conditional file warns rather than
  # fails, unless the project's own decisions.md names the file, the way
  # this repo's own #10 does.
  for f in docs/architecture.md docs/security.md docs/credits.md; do
    if [ -f "$REPO/$f" ]; then
      _conformit_note PASS "\`$f\` present"
    elif [ -f "$REPO/docs/decisions.md" ] \
      && grep -qi "$(basename "$f")" "$REPO/docs/decisions.md" 2>/dev/null; then
      _conformit_note PASS "\`$f\` absent, exemption recorded in decisions.md"
    else
      _conformit_note WARN "\`$f\` missing (conditional; no exemption recorded)"
    fi
  done

  # --- README disclosure, per docs/documentation-standard.md ---------------
  # Heuristic: a regex match, not a semantic read. A README that mentions
  # "AI" only in an unrelated sentence would false-positive here; flagged
  # as heuristic in the report itself, not presented as a certain result.
  if [ -f "$REPO/README.md" ]; then
    if grep -qiE '\b(in testing|stable|deprecated)\b' "$REPO/README.md"; then
      _conformit_note PASS "README states a project status (heuristic match)"
    else
      _conformit_note FAIL "README has no recognizable status line"
    fi
    if grep -qiE '\b(no warranty|without warranty|as.is|no guarantee)\b' "$REPO/README.md"; then
      _conformit_note PASS "README disclaims warranty (heuristic match)"
    else
      _conformit_note WARN "README has no recognizable warranty disclaimer"
    fi
    if grep -qiE '^##+[[:space:]]*use cases?\b' "$REPO/README.md"; then
      _conformit_note PASS "README has a use-case section (heuristic match)"
    else
      _conformit_note WARN "README has no recognizable use-case section"
    fi
    if grep -qiE '\b(llm|ai assist|ai-assisted|claude|copilot)\b' "$REPO/README.md"; then
      _conformit_note PASS "README discloses LLM use (heuristic match)"
    else
      _conformit_note FAIL "README has no recognizable LLM-use disclosure"
    fi
  fi

  # --- writing style: em dashes in docs/ and README.md ----------------------
  # Report paths relative to the repo, not the absolute clone path: an
  # absolute path is unreadable in a report and, for a CI-cloned target,
  # exposes the runner's own temp-directory layout for no reason.
  local hits=""
  local found
  for f in "$REPO/README.md" "$REPO"/docs/*.md; do
    [ -f "$f" ] || continue
    found="$(_conformit_scan_em_dash "$f")"
    found="${found//$REPO\//}"
    [ -n "$found" ] && hits="${hits}${found}"$'\n'
  done
  hits="$(printf '%s' "$hits" | sed '/^$/d')"
  if [ -z "$hits" ]; then
    _conformit_note PASS "no em dashes in docs/ or README.md"
  else
    local count sample
    count=$(printf '%s\n' "$hits" | grep -c .)
    sample=$(printf '%s\n' "$hits" | head -5 | paste -sd, -)
    _conformit_note FAIL "$count em dash line(s), e.g. $sample"
  fi

  # --- sensitive content: secrets, emails, private URLs ---------------------
  # Whole tracked tree, not just docs/: a leak is at least as likely in
  # code or config as in prose. See docs/decisions.md #13 for what this
  # does and does not cover (working tree only, not history; heuristic
  # fallback when gitleaks isn't on PATH).
  local secret_hits engine
  if command -v gitleaks >/dev/null 2>&1; then
    secret_hits="$(_conformit_scan_secrets_gitleaks "$REPO")"
    engine="gitleaks"
  else
    secret_hits="$(_conformit_scan_secrets_heuristic "$REPO")"
    engine="heuristic fallback, gitleaks not on PATH: reduced coverage"
  fi
  secret_hits="$(printf '%s' "$secret_hits" | sed '/^$/d')"
  if [ -z "$secret_hits" ]; then
    _conformit_note PASS "no likely secrets found ($engine)"
  else
    local count sample
    count=$(printf '%s\n' "$secret_hits" | grep -c .)
    sample=$(printf '%s\n' "$secret_hits" | head -3 | paste -sd '; ' -)
    _conformit_note CRIT "$count possible secret(s) ($engine), e.g. $sample"
    CONFORMIT_DETAILS="${CONFORMIT_DETAILS}$(_conformit_rotate_warning)"$'\n'
  fi

  local email_hits
  email_hits="$(_conformit_scan_emails "$REPO" | sed '/^$/d')"
  if [ -z "$email_hits" ]; then
    _conformit_note PASS "no unexpected email addresses found"
  else
    local count sample
    count=$(printf '%s\n' "$email_hits" | grep -c .)
    sample=$(printf '%s\n' "$email_hits" | head -3 | paste -sd '; ' -)
    _conformit_note FAIL "$count email address(es) not in this repo's git history, e.g. $sample"
  fi

  local url_hits
  url_hits="$(_conformit_scan_private_urls "$REPO" | sed '/^$/d')"
  if [ -z "$url_hits" ]; then
    _conformit_note PASS "no private/internal addresses found"
  else
    local count sample
    count=$(printf '%s\n' "$url_hits" | grep -c .)
    sample=$(printf '%s\n' "$url_hits" | head -3 | paste -sd '; ' -)
    _conformit_note FAIL "$count private address(es)/hostname(s), e.g. $sample"
  fi

  # --- tooling presence, informational -------------------------------------
  # A read-only clone can confirm the hook file exists to be pointed at;
  # it can't confirm core.hooksPath is actually set in anyone's working
  # copy, since that's local git config and never committed.
  if [ -f "$REPO/.githooks/commit-msg" ]; then
    _conformit_note PASS "commit-msg hook present in repo (not confirmed installed)"
  else
    _conformit_note WARN "no commit-msg hook found in repo"
  fi

  # A CLAUDE.md with real content instead of an `@AGENTS.md` import is the
  # most likely way this convention gets missed: Claude Code reads
  # CLAUDE.md natively, so it's easy to write everything there and never
  # create the tool-agnostic file other agents actually read. Only
  # checked when AGENTS.md is missing; if both exist, assume it's set up
  # correctly rather than parsing CLAUDE.md's content to be sure.
  if [ -f "$REPO/CLAUDE.md" ] && [ ! -f "$REPO/AGENTS.md" ]; then
    _conformit_note WARN "CLAUDE.md exists with no AGENTS.md; content may need to move, see documentation-standard.md"
  fi

  # --- recent commit subjects vs Conventional Commits -----------------------
  if [ -d "$REPO/.git" ]; then
    local TYPES='feat|fix|docs|refactor|perf|test|build|ci|chore|style|revert'
    local total=0 ok=0 subj
    while IFS= read -r subj; do
      [ -z "$subj" ] && continue
      total=$((total + 1))
      case "$subj" in
        "Merge "*|"Revert \""*|"fixup!"*|"squash!"*) ok=$((ok + 1)); continue ;;
      esac
      if printf '%s' "$subj" | grep -Eq "^(${TYPES})(\([a-z0-9._/-]+\))?!?: .+"; then
        ok=$((ok + 1))
      fi
    done <<CONFORMIT_LOG
$(cd "$REPO" && git log -50 --format=%s 2>/dev/null)
CONFORMIT_LOG
    if [ "$total" -gt 0 ]; then
      if [ "$ok" -eq "$total" ]; then
        _conformit_note PASS "commit style: $ok/$total of last $total subjects conform"
      else
        _conformit_note WARN "commit style: $ok/$total of last $total subjects conform"
      fi
    fi
  fi

  # --- emit ------------------------------------------------------------
  echo "### $LABEL"
  echo
  if [ "$CONFORMIT_CRIT" -gt 0 ]; then
    echo "🚨 **CRITICAL: possible secret(s) found. See below and rotate immediately.**"
    echo
  fi
  printf '%s' "$CONFORMIT_DETAILS"
  echo

  local status="PASS"
  [ "$CONFORMIT_WARN" -gt 0 ] && status="WARN"
  [ "$CONFORMIT_FAIL" -gt 0 ] && status="FAIL"
  [ "$CONFORMIT_CRIT" -gt 0 ] && status="CRIT"

  echo "| $LABEL | $(_conformit_symbol "$status") | $CONFORMIT_PASS | $CONFORMIT_WARN | $CONFORMIT_FAIL | $CONFORMIT_CRIT |" \
    >> "$ROWS_FILE"
}
