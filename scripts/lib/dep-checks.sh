#!/usr/bin/env bash
# conformIT: dependency and supply-chain checks.
#
# Sourced by scripts/lib/audit-checks.sh, not run directly. Same ground
# rules as every other check there: read-only against the target, and the
# output carries package names, versions and file:line, never file
# contents. See docs/decisions.md #23 for what is covered, what is not,
# and why one scanner (osv-scanner) stands in for three ecosystem tools.
#
# Two kinds of check live here, and they fail differently:
#
#   Known vulnerabilities: osv-scanner reads lockfiles (package-lock.json,
#   requirements.txt, Cargo.lock, and others it supports) and matches them
#   against the OSV database. Like semgrep, its absence is a WARN, never a
#   quiet PASS: nothing was checked.
#
#   Everything else (lockfile hygiene, outdated direct dependencies,
#   deprecations, Actions refs, end-of-life images) is scripts/lib/py/
#   depcheck.py, which needs python3 and network access to the public
#   registries. A lookup that fails is reported as incomplete.
#
# Portable to bash 3.2.

CONFORMIT_DEP_LIB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Turn "LEVEL<TAB>message" lines from depcheck.py into notes. A here-doc
# rather than a pipe: a pipe would run the loop in a subshell and lose the
# counters _conformit_note keeps.
_conformit_dep_emit() {
  local out="$1" lvl msg
  [ -z "$out" ] && return 0
  while IFS=$'\t' read -r lvl msg; do
    case "$lvl" in
      PASS|WARN|FAIL) _conformit_note "$lvl" "$msg" ;;
    esac
  done <<CONFORMIT_DEP_OUT
$out
CONFORMIT_DEP_OUT
}

# Does the repo track anything osv-scanner could read? Only then is the
# absence of osv-scanner worth a WARN; a repo with no dependencies has
# nothing to say and gets no note, the way `chats/` works.
_conformit_dep_has_lockfiles() {
  ( cd "$1" && git ls-files 2>/dev/null ) \
    | grep -v 'node_modules/' \
    | grep -Eq '(^|/)(package-lock\.json|npm-shrinkwrap\.json|yarn\.lock|pnpm-lock\.yaml|requirements[^/]*\.txt|poetry\.lock|uv\.lock|Pipfile\.lock|pdm\.lock|Cargo\.lock|go\.mod|Gemfile\.lock|composer\.lock)$'
}

_conformit_dep_osv() {
  local repo="$1" report rc
  report="$(mktemp)"
  ( cd "$repo" && _conformit_timeout 300 osv-scanner scan source -r \
      --format json --output-file "$report" . >/dev/null 2>&1 )
  rc=$?
  # osv-scanner exits 0 when clean and 1 when it found vulnerabilities; both
  # leave a report. Anything else (network down, bad input) is a failure to
  # check, not a clean result.
  if [ "$rc" -le 1 ] && [ -s "$report" ]; then
    _conformit_dep_emit "$(python3 "$CONFORMIT_DEP_LIB_DIR/py/depcheck.py" osv-summary "$report" "$repo")"
  else
    _conformit_note WARN "osv-scanner failed (exit $rc), so the dependency vulnerability check did not complete"
  fi
  rm -f "$report"
}

_conformit_dep_checks() {
  local repo="$1"
  local py="$CONFORMIT_DEP_LIB_DIR/py/depcheck.py"

  if ! command -v python3 >/dev/null 2>&1; then
    _conformit_note WARN "python3 not on PATH: dependency, Actions and base-image checks did not run"
    return 0
  fi
  if [ ! -f "$py" ]; then
    _conformit_note WARN "scripts/lib/py/depcheck.py not found: dependency checks did not run"
    return 0
  fi

  if _conformit_dep_has_lockfiles "$repo"; then
    if command -v osv-scanner >/dev/null 2>&1; then
      _conformit_dep_osv "$repo"
    else
      _conformit_note WARN "osv-scanner not on PATH: dependency vulnerability check did not run"
    fi
  fi

  # These detect their own subject matter and print nothing if the repo has
  # none of it, so they run unconditionally.
  local sub
  for sub in lockfiles outdated deprecated actions eol; do
    _conformit_dep_emit "$(python3 "$py" "$sub" "$repo")"
  done
}
