#!/usr/bin/env bash
# conformIT CLI.
#
# Usage:
#   scripts/conform.sh audit <path>          audit a local checkout
#   scripts/conform.sh audit <owner/repo>    clone (public, read-only) and audit
#   scripts/conform.sh audit --all           audit every repo in registry/targets.yaml
#   scripts/conform.sh init                  not implemented yet, see docs/STATE.md
#
# `audit` reports. It never rewrites the target and never writes anything
# back to conformIT itself. See docs/decisions.md #2 (no --fix, ever) and
# #12 (why this exists and what it doesn't cover).
#
# Portable to bash 3.2 (macOS system bash).
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"

# shellcheck source=lib/audit-checks.sh
. "$HERE/lib/audit-checks.sh"

usage() {
  sed -n '2,10p' "$0" | sed 's/^# \{0,1\}//'
}

cmd_audit_all() {
  local targets_file="$ROOT/registry/targets.yaml"
  local workdir rows_file
  workdir="$(mktemp -d)"
  rows_file="$workdir/rows.md"
  : > "$rows_file"
  # Deliberately double-quoted so $workdir expands now, capturing the
  # actual path as a literal string in the trap command. Single-quoting
  # it (shellcheck's usual advice, SC2064) defers the lookup until the
  # signal fires, and since $workdir is `local` to this function, it's
  # out of scope by then, an unbound-variable error under `set -u`. Found
  # by running this script, not by inspection.
  # shellcheck disable=SC2064
  trap "rm -rf '$workdir'" EXIT

  # A deliberately trivial subset of YAML: a flat bulleted list under
  # `targets:`. Grep/sed can parse this; a change to the file's shape
  # means updating this parser too. See registry/targets.yaml's own
  # header and docs/decisions.md #12.
  local targets
  targets="$(grep -E '^[[:space:]]*-[[:space:]]+' "$targets_file" \
    | sed -E 's/^[[:space:]]*-[[:space:]]+//' \
    | sed -E 's/[[:space:]]*#.*$//' \
    | sed '/^$/d')"

  if [ -z "$targets" ]; then
    echo "conform.sh: no targets found in $targets_file" >&2
    exit 1
  fi

  echo "# conformIT audit"
  echo
  echo "Run: $(date -u +%Y-%m-%dT%H:%MZ)"
  echo
  echo "Read-only. Public repos declared in \`registry/targets.yaml\`,"
  echo "cloned fresh for this run. Nothing is written back to any target."
  echo

  local repo clone_dir
  while IFS= read -r repo; do
    [ -z "$repo" ] && continue
    clone_dir="$workdir/$(printf '%s' "$repo" | tr '/' '_')"
    if ! git clone --quiet --depth 50 "https://github.com/${repo}.git" "$clone_dir" 2>/dev/null; then
      echo "| $repo | ❌ | n/a | n/a | clone failed |" >> "$rows_file"
      echo "### $repo"
      echo
      echo "- ❌ could not clone: repository missing, renamed, or not public"
      echo
      continue
    fi
    conformit_audit_repo "$clone_dir" "$repo" "$rows_file"
  done <<CONFORMIT_TARGETS
$targets
CONFORMIT_TARGETS

  echo "| Repo | Status | Pass | Warn | Fail |"
  echo "|---|---|---|---|---|"
  cat "$rows_file"
}

cmd_audit_one() {
  local arg="$1"
  local workdir rows_file repo_path label
  workdir="$(mktemp -d)"
  rows_file="$workdir/rows.md"
  : > "$rows_file"
  # See the matching trap in cmd_audit_all for why this is double-quoted
  # on purpose (SC2064 suppressed deliberately, not overlooked).
  # shellcheck disable=SC2064
  trap "rm -rf '$workdir'" EXIT

  if [ -d "$arg" ]; then
    repo_path="$(cd "$arg" && pwd)"
    label="$arg"
  else
    case "$arg" in
      */*)
        repo_path="$workdir/clone"
        label="$arg"
        if ! git clone --quiet --depth 50 "https://github.com/${arg}.git" "$repo_path" 2>/dev/null; then
          echo "conform.sh: could not clone https://github.com/${arg}.git (missing, renamed, or not public)" >&2
          exit 1
        fi
        ;;
      *)
        echo "conform.sh: '$arg' is not a local directory or an owner/repo shorthand" >&2
        exit 1
        ;;
    esac
  fi

  conformit_audit_repo "$repo_path" "$label" "$rows_file"
  echo "| Repo | Status | Pass | Warn | Fail |"
  echo "|---|---|---|---|---|"
  cat "$rows_file"
}

case "${1:-}" in
  audit)
    case "${2:-}" in
      --all) cmd_audit_all ;;
      "")
        echo "conform.sh: audit needs a path, an owner/repo, or --all" >&2
        exit 1
        ;;
      *) cmd_audit_one "$2" ;;
    esac
    ;;
  init)
    echo "conform.sh: init is not implemented yet. See docs/STATE.md." >&2
    exit 1
    ;;
  *)
    usage
    exit 1
    ;;
esac
