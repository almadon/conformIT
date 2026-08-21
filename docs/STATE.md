# Where this got to

Working notes for conformIT itself. **Delete this file once the standards
have been applied to a real project and the process has settled** — per
[documentation-standard.md](documentation-standard.md), `STATE.md` is the one
document with an expiry.

**Last updated:** 2026-08-21. Initial skeleton, first session.

## What is true right now

- **Six standards documents exist and are complete as prose:**
  rules-of-engagement, design-principles, security-posture,
  licensing-and-provenance, documentation-standard, commit-and-history.
- **They are derived from a survey of nine repos** under
  `~/Workspaces/Apps` — Alfred, Kisbo, anjunatree, kuzka, novak, rmrg
  (5 sub-repos), snapjudgement, tooling-as. The survey read committed docs
  and configs only; session transcripts were deliberately not mined
  (chosen at kickoff).
- **`docs/decisions.md` records five decisions**, including the one genuine
  conflict found between existing repos (commit format).
- **Nothing has been applied to any project.** No repo has been changed. The
  standards have never been tested against real work, which is the only test
  that matters.

## What is not built yet

- **`scripts/conform.sh` does not exist.** Both `init` and `audit` are
  described in the README as intent. The README says so; do not let that
  drift into implying they work.
- **`templates/` is not populated.** The intended contents: a `CLAUDE.md`
  distilled from the Rules of Engagement, `docs/` skeletons for each required
  file, a `commit-msg` hook, a `.gitmessage` template, and a
  `.claude/settings.json` baseline.
- **No `CHANGELOG.md`** for conformIT itself, which its own documentation
  standard requires. Noted rather than silently excused.

## Findings from the survey worth acting on

Recorded here because they are project-level problems the standards imply but
do not themselves fix:

1. **Eight of nine repos have no `LICENSE`.** They are therefore
   all-rights-reserved by default, which is almost certainly not the intent
   for at least some of them. This is the single highest-value fix available
   and it is cheap.
2. **No repo has a `CLAUDE.md`.** Every session re-derives conventions that
   are already written down in prose the model isn't being pointed at.
3. **`.claude/settings.local.json` files are ad-hoc accretions.** `rmrg/burne`
   has 30+ entries, many one-off `cp` commands frozen from a single session;
   `rmrg/xenia` has a single 400-character compound command. These grant
   nothing useful going forward and are noise. A shared baseline of
   genuinely-reusable read-only permissions would replace most of them.
4. **`novak/docs/credits.md` has nine unresolved `VERIFY` licence markers.**
   That is the process working as designed — but they are a release gate, and
   novak is the most likely of these projects to be published.
5. **Unpinned runtime dependencies.** Several MCP servers in novak run
   `npx -y` at container start, fetching latest on every boot. novak records
   this as a known weakness; the standard now names it as a rule.

## Open questions

- Does conformIT install into projects (a plugin, a submodule, a copied
  scaffold), or is it purely a reference that `conform.sh` reads from? The
  README implies a scaffold; this has not actually been decided, and it
  determines whether standards updates propagate or have to be re-copied.
- Is `CLAUDE.md` per-repo, or one shared file plus a thin per-repo overlay?
  The Rules of Engagement are identical everywhere; only scopes, commands,
  and stack differ.
