# Where this got to

Working notes for conformIT itself. Delete this file once the standards
have been applied to a real project and the process has settled. Per
[documentation-standard.md](documentation-standard.md), `STATE.md` is the
one document with an expiry.

**Last updated:** 2026-08-21. Second session: added status/LLM disclosure
and writing-style requirements, rewrote every existing document to follow
them, then added a named rule against telegraphic status-note fragments.

**Scope confirmed by the maintainer this session:** conformIT is meant to
cover infrastructure, documentation, safety, security, privacy, design
style, and writing style for software projects generally, not just the
categories already drafted. See "gaps against that scope" below.

## What is true right now

- **Eight standards documents exist and are complete as prose:**
  rules-of-engagement, design-principles, security-posture,
  licensing-and-provenance, documentation-standard, writing-style,
  commit-and-history, plus this file and decisions.md.
- **They are derived from a survey of nine repos** under
  `~/Workspaces/Apps`: Alfred, Kisbo, anjunatree, kuzka, novak, rmrg (5
  sub-repos), snapjudgement, tooling-as. The survey read committed docs and
  configs only. Session transcripts were deliberately not mined, a call made
  at kickoff.
- **`docs/decisions.md` records nine decisions** as of 2026-08-24, including
  the one genuine conflict found between existing repos (commit format) and
  entries added across later sessions (status/LLM disclosure, writing
  style, and the one-standard-for-humans-and-models reframe). This count
  was stale here (said "seven") until the first external audit, of `novak`,
  flagged it: exactly the drift this file exists to catch, in the one
  document whose job is being current.
- **conformIT's own docs violated its own writing-style rule** on the first
  pass: 108 em dashes across the set, found by grep right after the rule was
  written, then fixed. Recorded as decision #7 rather than quietly cleaned
  up.
- **Nothing has been applied to any project.** No repo has been changed. The
  standards have never been tested against real work, which is the only
  test that matters.

## What is not built yet

- **`scripts/conform.sh` does not exist.** Both `init` and `audit` are
  described in the README as intent. The README says so. Don't let that
  drift into implying they work.
- **`templates/` is not populated.** The intended contents: a `CLAUDE.md`
  distilled from the Rules of Engagement, `docs/` skeletons for each
  required file (including a status/LLM-disclosure stub for `README.md`),
  the `commit-msg` hook, a `.gitmessage` template, and a
  `.claude/settings.json` baseline.
- **No `CHANGELOG.md`** for conformIT itself, which its own documentation
  standard requires. Noted rather than silently excused.
- **No pre-commit check for em dashes.** `writing-style.md` documents the
  grep command but nothing runs it automatically yet. Should probably live
  in the same hook as the commit-msg check, or a separate `pre-commit` hook,
  once `templates/.githooks/` grows one.

## Findings from the survey worth acting on

Recorded here because they are project-level problems the standards imply
but don't themselves fix:

1. **Eight of nine repos have no `LICENSE`.** They default to all rights
   reserved, which is almost certainly not the intent for at least some of
   them. This is the single highest-value fix available and it's cheap.
2. **No repo has a `CLAUDE.md`.** Every session re-derives conventions that
   are already written down in prose the model isn't being pointed at.
3. **No repo states a project status or discloses LLM use.** Now required
   by [documentation-standard.md](documentation-standard.md); nothing
   surveyed does it yet, conformIT included until this session's README
   update.
4. **`.claude/settings.local.json` files are ad-hoc accretions.**
   `rmrg/burne` has 30+ entries, many one-off `cp` commands frozen from a
   single session. `rmrg/xenia` has a single 400-character compound
   command. None of this grants anything useful going forward; it's noise.
   A shared baseline of genuinely reusable read-only permissions would
   replace most of it.
5. **`novak/docs/credits.md` has nine unresolved `VERIFY` licence markers.**
   That's the process working as designed, but they're a release gate, and
   novak is the most likely of these projects to be published.
6. **Unpinned runtime dependencies.** Several MCP servers in novak run
   `npx -y` at container start, fetching latest on every boot. novak
   records this as a known weakness; the standard now names it as a rule.

## Open questions

- Does conformIT install into projects (a plugin, a submodule, a copied
  scaffold), or is it purely a reference that `conform.sh` reads from? The
  README implies a scaffold. This hasn't actually been decided, and it
  determines whether standards updates propagate or have to be re-copied.
- Is `CLAUDE.md` per-repo, or one shared file plus a thin per-repo overlay?
  The Rules of Engagement are identical everywhere; only scopes, commands,
  and stack differ.
- Should the em-dash grep run as an actual hook, or stay a documented manual
  check? Leaning toward a hook, since the whole point of this project is
  that unenforced standards drift, and this is the standard that just
  proved it by drifting within one session.

## Gaps against the confirmed scope

Two categories the maintainer named explicitly aren't covered as their own
documents yet:

- **Privacy**, as distinct from security. `security-posture.md` touches
  it in passing (rule 7, on auditable stores; rule 1, on not pasting
  secrets into a chat that gets logged), but there's no treatment of user
  data handling, retention, deletion, or third-party data sharing as its
  own subject. Worth a dedicated `privacy.md`, or a clearly separated
  section inside `security-posture.md` if the two turn out not to need
  separate documents.
- **Design style** meaning visual and interaction design, not the
  structural `design-principles.md` that exists today (services layer,
  declare/apply/drift, and so on). Nothing in the survey covered UI/UX
  conventions in a generalizable way; `anjunatree`'s palette-validator
  practice is the closest example and it's cited in
  `design-principles.md` rule 10, but that's one repo's accessibility gate,
  not a style standard.

Both need the same treatment as everything else here: survey first, write
second, cite sources, state cost. Not started.
