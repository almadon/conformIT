# Documentation standard

Which files a conforming project has, what belongs in each, and the
conventions that keep them honest.

The organising rule: **the diff says what changed; documentation says why.**
Anything a future reader would otherwise have to re-derive belongs in prose.

## The required set

| File | Holds | Missing means |
|---|---|---|
| `README.md` | What this is, how to run it, where to go next, project status, LLM use | Nobody can start |
| `LICENSE` | The licence, from the first commit | All rights reserved by accident |
| `CLAUDE.md` | Working agreement for AI agents in this repo | Every session re-derives the conventions |
| `docs/STATE.md` | What is true right now, including what's broken | Status lives in someone's head |
| `docs/decisions.md` | Numbered decisions with reasoning and cost | Settled questions get re-litigated |
| `docs/architecture.md` | How the pieces fit and why each is where it is | Structure is only legible by reading all the code |
| `docs/security.md` | The project's instance of the security posture | Trust boundaries are implicit |
| `docs/credits.md` | Dependencies, licences, and what was rejected | Obligations are unknown at release |
| `CHANGELOG.md` | What changed and why, including reverts | History is only in git log |

Projects with contributors add `CONTRIBUTING.md`. Projects with a long-range
shape add `VISION.md`, distinct from `architecture.md` in that it covers what
the project is and is not, rather than how it's built.

`docs/README.md` is an index of the above. A directory listing is not
navigation.

## Status and LLM disclosure

Every `README.md` states two things near the top, before the rest of the
content, not buried in a footer.

### Project status

A status line, one of:

- **In testing** (the default; see below)
- **Stable**
- **Deprecated**, with a pointer to the replacement if there is one

**A project defaults to "in testing" from its first commit.** It stays there
until the maintainer deliberately marks it otherwise. This exists because
"stable" is the claim that needs justifying, not the other way around. A
reader who finds no status line should assume "in testing" rather than
assume the author forgot to write one, but every conforming project writes
one anyway so nobody has to guess.

Moving a project to "stable" is itself worth a line in `docs/decisions.md`:
what made it stable, and what would knock it back to testing.

### LLM use

State plainly whether an LLM was used to build the project, maintain it, or
both, and roughly how. A short paragraph is enough:

> This project is built and maintained with substantial AI assistance
> (Claude Code). Architectural decisions and reviews are by a human;
> generated code is reviewed before merge.

The point is that a reader deciding whether to trust or adopt the code
should not have to guess how it was produced. This is a repo-level
disclosure, separate from the per-commit trailer described in
[commit-and-history.md](commit-and-history.md): the commit trailer says who
wrote a given change, and this says how the project as a whole is built.

## What goes outside `docs/`

Content the system consumes at runtime is not documentation about the
system, and does not live in `docs/`. `novak` separates `prompts/`
(personas the software loads) and `registry/` (declarative input a
reconciler applies) on this basis: data, not prose.

The test is simple. Does something read this file while running? Then it
isn't documentation.

## Conventions that keep documents honest

### `VERIFY` for unchecked claims

A claim believed true but unverified is marked `VERIFY` inline. It gets
grepped before release. See
[licensing-and-provenance](licensing-and-provenance.md).

### `STATE.md` is allowed to be unflattering

It records what is actually true, including the parts that don't work:

> **No models are loaded.** `/v1/models` returns an empty list, so chat will
> connect and offer nothing until a model is added.

It also carries a section along the lines of "what the previous notes got
wrong," preserved rather than deleted, because the wrong guesses are
plausible and someone will make them again.

`STATE.md` is the one document with an expiry. It says at the top when it
should be deleted, and it gets deleted then, rather than decaying into a
misleading historical record.

### Decisions are numbered and referenced by number

`decisions.md` entries are numbered and cited from elsewhere as `(#14)`. The
numbers are stable and never reused. A reversed decision gets a new entry
that supersedes the old one, and the old one stays in place.

Each entry carries what was chosen, what it cost, what was rejected, and
what would justify revisiting. An entry can end with a "still open" section.
An unresolved question that's written down is worth more than a resolved one
implied.

### Dates are absolute

Write "split out of the `rmrg` monorepo into its own repo on 2026-08-11,"
not "recently" or "last month." Relative dates in a document with no visible
edit date go stale within a quarter and nobody can tell.

### Changelog entries survive the retelling

If a change is one a user would notice, it needs a changelog entry in the
same commit. The developer-facing changelog carries the why and includes
reverts and course-corrections; don't sand those down after the fact.

Where a project has both an in-app changelog and a repository one, update
both together, and bump the version marker that tells a returning user
something is new.

### Write for someone who is not you

The target, borrowed from an existing commit message in this codebase: write
the README for people who are not you. Assume the reader has the repo, no
context, and no access to the author.

## Style

- Write like a technical person explaining something to a colleague, not
  like marketing copy and not like an AI chat response. See
  [writing-style.md](writing-style.md) for the specific rules and why they
  exist.
- Prose, not bullet fragments, wherever a reason is being given. Use tables
  for lookups and prose for reasoning.
- Bold the one sentence in a long section that actually carries the point. A
  reader skimming should land on it.
- Link between documents by relative path.
- State the cost of a thing in the same paragraph as its benefit.
