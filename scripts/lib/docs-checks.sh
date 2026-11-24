#!/usr/bin/env bash
# conformIT: documentation checks, delegated to scripts/lib/py/docscheck.py.
#
# Sourced by audit-checks.sh after dep-checks.sh, whose _conformit_dep_emit
# turns the helper's "LEVEL<TAB>message" lines into notes. Read-only; needs
# python3 and nothing else. Portable to bash 3.2.

CONFORMIT_DOCS_LIB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

_conformit_docs_checks() {
  local repo="$1"
  local py="$CONFORMIT_DOCS_LIB_DIR/py/docscheck.py"
  command -v python3 >/dev/null 2>&1 || return 0   # dep-checks already warned
  [ -f "$py" ] || { _conformit_note WARN "scripts/lib/py/docscheck.py not found: README checks did not run"; return 0; }
  _conformit_dep_emit "$(python3 "$py" readme "$repo")"
}
