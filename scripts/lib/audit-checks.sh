#!/usr/bin/env bash
# conformIT: the checks a single repository is audited against.
#
# Sourced by scripts/conform.sh, not run directly. Every check here is
# read-only against the target and prints only filenames, line numbers,
# and short labels, never file contents, since this can run against
# repositories this project doesn't own and the output can land in a
# public CI job summary. See docs/decisions.md #12.
#
# Portable to bash 3.2 (macOS system bash), matching every other script
# and hook in this repo.

CONFORMIT_PASS=0
CONFORMIT_WARN=0
CONFORMIT_FAIL=0
CONFORMIT_DETAILS=""

_conformit_note() {
  # _conformit_note <symbol> <message>
  CONFORMIT_DETAILS="${CONFORMIT_DETAILS}- $1 $2"$'\n'
  case "$1" in
    "PASS") CONFORMIT_PASS=$((CONFORMIT_PASS + 1)) ;;
    "WARN") CONFORMIT_WARN=$((CONFORMIT_WARN + 1)) ;;
    "FAIL") CONFORMIT_FAIL=$((CONFORMIT_FAIL + 1)) ;;
  esac
}

_conformit_symbol() {
  case "$1" in
    PASS) printf '%s' "✅" ;;
    WARN) printf '%s' "⚠️" ;;
    FAIL) printf '%s' "❌" ;;
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

conformit_audit_repo() {
  # conformit_audit_repo <repo-path> <label> <rows-file>
  # Prints a markdown "details" section to stdout. Appends one summary row
  # to <rows-file>.
  local REPO="$1"
  local LABEL="$2"
  local ROWS_FILE="$3"

  CONFORMIT_PASS=0
  CONFORMIT_WARN=0
  CONFORMIT_FAIL=0
  CONFORMIT_DETAILS=""

  # --- required files, per docs/documentation-standard.md -----------------
  local f
  for f in README.md LICENSE CLAUDE.md docs/STATE.md docs/decisions.md CHANGELOG.md; do
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

  # --- tooling presence, informational -------------------------------------
  # A read-only clone can confirm the hook file exists to be pointed at;
  # it can't confirm core.hooksPath is actually set in anyone's working
  # copy, since that's local git config and never committed.
  if [ -f "$REPO/.githooks/commit-msg" ]; then
    _conformit_note PASS "commit-msg hook present in repo (not confirmed installed)"
  else
    _conformit_note WARN "no commit-msg hook found in repo"
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
  printf '%s' "$CONFORMIT_DETAILS"
  echo

  local status="PASS"
  [ "$CONFORMIT_WARN" -gt 0 ] && status="WARN"
  [ "$CONFORMIT_FAIL" -gt 0 ] && status="FAIL"

  echo "| $LABEL | $(_conformit_symbol "$status") | $CONFORMIT_PASS | $CONFORMIT_WARN | $CONFORMIT_FAIL |" \
    >> "$ROWS_FILE"
}
