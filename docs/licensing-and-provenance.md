# Licensing and provenance

Not legal advice. This is an engineering procedure for keeping provenance
traceable and obligations checkable *before* they become expensive.

The governing observation, from `novak/docs/credits.md`:

> Novak is mostly other people's work wired together.

That is true of nearly every project, and it is truer when a model is writing
the code — a model's training makes it fluent in patterns whose origins it
cannot cite. Provenance therefore has to be recorded by the person adding the
thing, at the moment they add it.

## Every project has a `docs/credits.md`

A table of what the project depends on, what each is used for, and its
licence.

| Project | Used for | Licence |
|---|---|---|
| … | … | MIT |
| … | … | **VERIFY** |

### The VERIFY marker

**An unchecked licence is recorded as `VERIFY`, never guessed.** A guessed
licence is worse than a blank one, because it stops anyone from looking.

The header of the table says so explicitly:

> Licences marked VERIFY have not been checked. Do that before distributing
> this repo or any image built from it.

Resolving every `VERIFY` is a release gate. Before publication, distribution,
or any commercial use:

```bash
grep -rn "VERIFY" docs/
```

### Licences that need a second look

Flag these in the table with the obligation spelled out, not just the SPDX
identifier — the identifier is what people skim past:

- **BSL / SSPL / Elastic and other source-available licences** — often fine
  for internal use, restricted commercially, and with a delayed open-source
  conversion date. `novak` annotates Outline as *"BSL 1.1 — check before any
  commercial use."*
- **AGPL** — network use can count as distribution. Matters the moment the
  thing is reachable by someone else.
- **GPL** — affects what can be linked or bundled with it.
- **Relicensed projects** — record the licence *at the version you pinned*.
  Several well-known projects have changed licence mid-life; "it was MIT when
  I looked" is not a defence, and `novak` flags Open WebUI on exactly this
  basis.

### Also record what you rejected

A section for evaluated-and-not-adopted, with a one-line outcome and a
pointer to the decision. This is the highest-value part of the file and the
first part people leave out.

State plainly that no criticism is intended — several rejected projects are
excellent and simply aim at a different shape of problem.

## Before adding a dependency

1. Record it in `docs/credits.md` with a link and a licence (or `VERIFY`).
2. **Pin a version.** See [security-posture](security-posture.md) rule 8.
3. Check it isn't already solved in-repo — see
   [rules-of-engagement](rules-of-engagement.md) rule 7.
4. If it's under 15 lines of well-understood logic, consider not adding it.

## Your own licence, chosen deliberately

Every repo has a `LICENSE` from its first commit. **A repo with no licence is
not "open by default" — it is all-rights-reserved by default**, which is the
opposite of what people usually intend.

Currently 1 of 9 surveyed repos has one. That is the gap this standard
exists to close.

Defaults:

| Content | Licence | Why |
|---|---|---|
| Libraries, tools, templates | MIT | Maximum adoption, no obligation dragged into a consumer's codebase |
| Standards, prose, documentation | CC BY 4.0 | Attribution preserved; code licences fit prose badly |
| Applications not intended for reuse | MIT, or explicit "all rights reserved" | Either is fine — *silence is not* |

Non-commercial or fan projects state that in `CONTRIBUTING.md`, since it
changes what a contributor is agreeing to.

## Clean-room procedure

Required when reimplementing behaviour you have seen in source you cannot
legally copy from: a licence-incompatible project, decompiled or
disassembled output, leaked code, an employer's proprietary work, or a
competitor's product you have studied closely.

Not required for: reading public documentation, using a published API to its
spec, or reimplementing an idea you never saw expressed as code. Ideas,
interfaces, and facts are not the protected part — **the expression is.**

### The two roles

**Never the same person, and never the same model session.**

1. **The analyst** examines the original and writes a **specification of
   behaviour only** — inputs, outputs, states, protocol, timing, error
   conditions. No code. No variable names, function names, comments,
   structure, or ordering carried over. If a sentence would let a reader
   reconstruct the original's *code* rather than its *behaviour*, cut it.
2. **The implementer** builds from that specification alone, having never
   seen the original. They do not read the original to "check something."
   Questions go back to the analyst, who answers from the spec or amends it.

### Doing this with an AI agent

The context window is the contaminated surface. Specifically:

- The analyst's session and the implementer's session are **separate
  sessions**, not separate turns. Context carries; a fresh prompt in the same
  session is not a fresh room.
- The implementer's session must never have the original in context — not
  pasted, not fetched, not read from disk, not in a summary, not in a memory
  store that gets re-injected. Check what the harness is auto-loading.
- Transcripts are the evidence. Retain both.
- If the implementer session ever ingests the original, that session is
  burned. Discard the output and restart from the spec in a new one. There is
  no partial recovery, and this rule is the one most likely to be rationalised
  away under time pressure.

### The record

A `docs/clean-room/` directory containing:

- `spec.md` — the analyst's behavioural specification
- `procedure.md` — who did what, when, in which sessions, and what each had
  access to
- The retained transcripts

Undocumented clean-room work provides no protection. **The documentation is
the deliverable**, as much as the code is — the whole value is being able to
demonstrate, later and to someone skeptical, that the implementer never saw
the original.

## Attribution for AI-assisted work

- Substantial AI authorship is disclosed in the commit trailer, not hidden.
- **Attribution is not a licence.** A trailer records who wrote it; it does
  not resolve where the pattern came from. If a model produces something that
  looks like it was copied from a specific known source, treat it as an
  unrecorded dependency and check it.
