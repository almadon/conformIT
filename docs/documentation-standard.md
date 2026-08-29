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
| `AGENTS.md` | Working agreement for AI agents in this repo | Every session re-derives the conventions |
| `docs/STATE.md` | What is true right now, including what's broken | Status lives in someone's head |
| `docs/decisions.md` | Numbered decisions with reasoning and cost | Settled questions get re-litigated |
| `docs/architecture.md`* | How the pieces fit and why each is where it is | Structure is only legible by reading all the code |
| `docs/security.md`* | The project's instance of the security posture | Trust boundaries are implicit |
| `docs/credits.md`* | Dependencies, licences, and what was rejected | Obligations are unknown at release |
| `CHANGELOG.md` | What changed and why, including reverts | History is only in git log |

Projects with contributors add `CONTRIBUTING.md`. Projects with a long-range
shape add `VISION.md`, distinct from `architecture.md` in that it covers what
the project is and is not, rather than how it's built.

\* Conditional on having something to say. A project with no running
components, no trust boundaries to describe, and no adopted dependencies
can skip these three rather than write a near-empty file for the sake of
the table. Record the skip in `docs/decisions.md`, the way conformIT's own
does at #10, so a reader can tell "not applicable" apart from "overlooked."

`docs/security.md` is this project's own security posture and is distinct
from a top-level `SECURITY.md`, which GitHub gives special handling
("Report a vulnerability") and which covers how to report a vulnerability,
not what the trust model is. A project with both should have each point at
the other so nobody conflates them.

`AGENTS.md` is the [Linux Foundation-stewarded](https://agents.md), tool-
agnostic convention, not a Claude-specific one, and is what's actually
loaded into an agent's context: terse, operative, no fixed schema. If a
tool needs its own filename (Claude Code reads `CLAUDE.md`, not
`AGENTS.md`, as of this writing), that file is a one-line pointer,
`@AGENTS.md`, not a second copy of the content. See
[decisions.md](decisions.md) #15 and
[`templates/AGENTS.md`](../templates/AGENTS.md) /
[`templates/CLAUDE.md`](../templates/CLAUDE.md).

`docs/README.md` is an index of the above. A directory listing is not
navigation.

## What a README opens with

Before any of the disclosures below, a README opens with what the project
actually is, in a form a stranger can use without reading the code:

- **Name and a one-line description.** What it's called and what it does,
  in one sentence.
- **Function.** A short paragraph on what it actually does, mechanically:
  what it takes as input, what it produces, what it's for.
- **Use case(s).** At least one concrete scenario where someone would
  reach for this instead of something else. If none comes to mind
  easily, that's worth noticing before writing the rest of the README.

A template for this whole structure, including the disclosures below,
lives at [`templates/docs/README.md`](../templates/docs/README.md); copy
it rather than reconstructing the shape from this description each time.

## Status, warranty, and LLM disclosure

Every `README.md` states three things near the top, before the rest of
the content, not buried in a footer.

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

### No warranty

A short, plain disclaimer that the project comes with no warranty or
guarantee of fitness for any purpose. This isn't legal advice and isn't a
substitute for a real licence's own warranty language (MIT and most
open-source licences already include one, in `LICENSE`); it's a plain-
language line in the README itself, where a reader actually looks, rather
than something that only exists in a licence file most people don't open:

> This project comes with no warranty or guarantee of fitness for any
> purpose. Use it at your own risk.

Pairs naturally with the status line: a project explicitly "in testing"
disclaiming warranty is a coherent, honest pair of statements; a project
claiming "stable" while also disclaiming all warranty is a much stranger
thing to read, and is itself a signal something's off.

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

`chats/` is the other kind of exclusion: not data the system reads, but
a record no one but the project's own contributors should read, and
never through git. See
[security-posture.md](security-posture.md) rule 1 and
[decisions.md](decisions.md) #20.

## Session logs (`chats/`)

A continuous, human-readable record of AI-assisted work on the project,
one file per session:

```
chats/{tool}/YYYY-MM-DD-{project}-{shortened-topic}.md
```

`{tool}` is the coding tool (`claude`, `opencode`, `codex`, whichever
was actually used; a project using more than one tool gets more than
one subdirectory, not a merged one). `{project}` and `{shortened-topic}`
are short, filesystem-safe slugs. Markdown, not the tool's own raw
transcript format (JSONL, or whatever else): the point is something a
human, or a different tool's next session, can open and read directly,
not a re-export of what the tool already stores for itself elsewhere.

**What it's for**: continuity across sessions and across tools. A new
session, possibly in a different tool than the last one, can read what
was actually discussed and decided without re-deriving it, the same
argument [`AGENTS.md`](../AGENTS.md) makes for not re-inferring
conventions every time. It's a supplement to `docs/decisions.md`, not a
replacement: decisions.md is the curated, durable record of what was
chosen and why; `chats/` is the fuller, unedited trace of how the
conversation got there, useful when the summary in decisions.md isn't
enough.

**Never committed. Gitignored by default, in every project, no
exceptions carved out per-repo.** A session transcript can contain
anything that came up in conversation: pasted output, a stray secret
someone meant to redact and didn't, a private URL, exactly the class of
content [security-posture.md](security-posture.md) rule 1 already warns
against letting reach anywhere it shouldn't. The audit checks that a
`chats/` directory, if one exists, is actually excluded, not just that
a `.gitignore` file happens to exist somewhere in the repo; see
[decisions.md](decisions.md) #20.

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
