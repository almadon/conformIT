# Commit and history

The standard is [Conventional Commits](https://www.conventionalcommits.org),
enforced by a hook so it can't quietly drift.

```
type(scope): description

Why. What it cost. What you checked.

BREAKING CHANGE: only when something breaks
```

This resolves a real conflict between existing repos. See
[decisions.md](decisions.md) #1 for the alternative and why it lost.

## The subject

Lowercase type, optional scope in parentheses, colon, space, description.
72 characters or fewer, imperative mood, lowercase description, no full
stop. Non-imperative drift takes three shapes and the hook checks all of
them: past tense ("added"), third-person present ("adds"), and gerund
("adding"). Only "add" passes.

| Type | For | Version effect |
|---|---|---|
| `feat` | New capability | minor |
| `fix` | Something was broken and now isn't | patch |
| `docs` | Documentation only | none |
| `refactor` | Restructuring, no behaviour change | none |
| `perf` | Performance | patch |
| `test` | Tests | none |
| `build` | Build system, images, dependencies | none |
| `ci` | Pipeline | none |
| `chore` | Housekeeping | none |
| `style` | Formatting only, no logic | none |
| `revert` | Undoing something | none |

Breaking changes get `!` before the colon and a `BREAKING CHANGE:` footer.
The `!` is for tooling; the footer is for the person who has to deal with
it.

```
feat(memory)!: identity comes from the connection, not a tool argument

BREAKING CHANGE: clients passing user_id as a tool parameter will be
ignored. Register a per-client token in MEMORY_TOKEN_MAP instead.
```

## Scopes

Optional, but they make history searchable. Each project defines its own
set in its `docs/commit-style.md`.

**`security` earns its place as a scope in every project.** When you're
working out whether an old decision still holds, `git log --grep
'security'` showing every change that touched the trust model is worth the
small discipline of tagging them. The same argument applies to `deps`.

## The body

**The diff already says what changed. The body is for why.**

This matters more in these repos than in most, because much of what's in
them is decisions rather than code, and a decision with no recorded
reasoning gets re-litigated, or quietly reversed by someone who assumed it
was arbitrary.

Worth writing down:

- The reason, particularly if the change looks strange without context
- What you traded away, and what would justify revisiting it
- **What you verified, and what you didn't.** An untested change described
  honestly is far more useful than one implying confidence it hasn't
  earned.
- Alternatives you rejected, so nobody re-treads that ground

The hook nudges when a commit has no body, but doesn't block it. Some
changes really are one-liners.

## AI authorship

Commits with substantial model authorship carry an `Assisted-by:`
trailer:

```
Assisted-by: AGENT_NAME:MODEL_VERSION [TOOL1] [TOOL2]
```

`AGENT_NAME` is the coding tool (`Claude Code`, `Codex`, `Copilot`), not
the model vendor. `MODEL_VERSION` is the specific model. The bracketed
tools are optional, specialised analysis tools actually used (a linter, a
type checker), not ordinary development tools (`git`, a compiler, an
editor). Example:

```
Assisted-by: Claude Code:claude-sonnet-5
```

This is the [Linux kernel's own convention](https://docs.kernel.org/process/coding-assistants.html),
adopted independently by Fedora, Rocky Linux, OpenTelemetry, the Apache
Software Foundation, LLVM, and QEMU, and it replaces the older
`Co-Authored-By:` pattern for AI specifically. `Co-Authored-By:` still
means what it always meant: a human who worked on the change.

**An AI never gets a `Signed-off-by:`.** Where a project uses the
Developer Certificate of Origin, `Signed-off-by:` certifies that the
signer wrote the change or has the right to submit it under the
project's licence, and only a human can attest to that. `Assisted-by:`
documents that a tool helped; `Signed-off-by:` stays entirely human,
even on a commit an AI wrote most of.

Disclosed, not hidden, either way. See
[licensing-and-provenance](licensing-and-provenance.md) on why a trailer
isn't a provenance answer on its own.

## What this buys

Conventional Commits is machine-readable, which unlocks things later
without extra work now:

- **Changelogs** generated from history rather than maintained by hand
- **Semantic versioning**: `feat` bumps minor, `fix` bumps patch, `!` bumps
  major
- Release notes grouped by type
- Filtering, as in `git log --grep '^fix(security)'`

None of that is set up yet in any repo. The point is that history will
already be in the right shape whenever it is.

## Setup

Hooks live in `.git/hooks`, which isn't tracked, so each clone needs:

```bash
git config core.hooksPath .githooks
git config commit.template .gitmessage
```

`scripts/conform.sh init` does this. To bypass the hook once, use
`git commit --no-verify`.
