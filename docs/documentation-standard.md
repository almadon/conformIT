# Documentation standard

Which files a conforming project has, what belongs in each, and the
conventions that keep them honest.

The organising rule: **the diff says what changed; documentation says why.**
Anything a future reader would otherwise have to re-derive belongs in prose.

## The required set

| File | Holds | Missing means |
|---|---|---|
| `README.md` | What this is, how to run it, where to go next | Nobody can start |
| `LICENSE` | The licence, from the first commit | All rights reserved by accident |
| `CLAUDE.md` | Working agreement for AI agents in this repo | Every session re-derives the conventions |
| `docs/STATE.md` | What is true *right now*, including what's broken | Status lives in someone's head |
| `docs/decisions.md` | Numbered decisions with reasoning and cost | Settled questions get re-litigated |
| `docs/architecture.md` | How the pieces fit and why each is where it is | Structure is only legible by reading all the code |
| `docs/security.md` | The project's instance of the security posture | Trust boundaries are implicit |
| `docs/credits.md` | Dependencies, licences, and what was rejected | Obligations are unknown at release |
| `CHANGELOG.md` | What changed and why, including reverts | History is only in git log |

Projects with contributors add `CONTRIBUTING.md`. Projects with a long-range
shape add `VISION.md` — distinct from `architecture.md` in that it covers
what the project *is* and is not, rather than how it's built.

`docs/README.md` is an index of the above, because a directory listing is not
navigation.

## What goes outside `docs/`

Content the *system consumes* is not documentation about the system, and does
not live in `docs/`. `novak` separates `prompts/` (personas the software
loads) and `registry/` (declarative input a reconciler applies) on exactly
this basis: **data, not prose.**

The test: does something read this file at runtime? Then it isn't
documentation.

## Conventions that keep documents honest

### `VERIFY` for unchecked claims

A claim believed true but unverified is marked `VERIFY` inline. It is grepped
before release. See [licensing-and-provenance](licensing-and-provenance.md).

### `STATE.md` is allowed to be unflattering

It records what is actually true, including the parts that don't work:

> **No models are loaded.** `/v1/models` returns an empty list … so chat will
> connect and offer nothing until a model is added.

It also carries **"what the previous notes got wrong"** — preserved, not
deleted, *"because the wrong guesses are plausible and someone will make them
again."*

`STATE.md` is the one document with an expiry. It says at the top when it
should be deleted, and it is deleted then rather than decaying into a
misleading historical record.

### Decisions are numbered and referenced by number

`decisions.md` entries are numbered and cited from elsewhere as `(#14)`. The
numbers are stable and never reused; a reversed decision gets a new entry
that supersedes the old one, and the old one stays.

Each entry carries: what was chosen, **what it cost**, what was rejected, and
what would justify revisiting. Entries may end with a **"still open"**
section — an unresolved question recorded is worth more than a resolved one
implied.

### Dates are absolute

*"Split out of the `rmrg` monorepo into its own repo on 2026-08-11"* — not
"recently", not "last month". Relative dates in a document with no visible
edit date are useless within a quarter.

### Changelog entries survive the retelling

If a change is one a user would notice, it needs a changelog entry in the
same commit. The developer-facing changelog carries the *why*, and includes
reverts and course-corrections — *"don't sand those down after the fact."*

Where a project has both an in-app changelog and a repository one, both are
updated together, and the version marker that tells a returning user
something is new gets bumped alongside.

### Write for someone who is not you

An explicit target from `novak`'s own commit log: *"rewrite README for people
who are not me."* Assume the reader has the repo, no context, and no access
to the author.

## Style

- Prose, not bullet fragments, wherever a reason is being given. Tables for
  lookups; prose for reasoning.
- Bold the load-bearing sentence in a long section. A reader skimming should
  land on the thing that matters.
- Link between documents by relative path.
- No marketing voice. State the cost of a thing in the same paragraph as its
  benefit.
