# Where this got to

Working notes for conformIT itself. Delete this file once the standards
have been applied to a real project and the process has settled. Per
[documentation-standard.md](documentation-standard.md), `STATE.md` is the
one document with an expiry.

**Last updated:** 2026-08-27. Eighth session: the maintainer asked
whether reports should go to a private "meta" repo instead of
conformIT's own public job summary. Built `almadon/conformIT-reporting`
(private) plus a `--detail-dir` split in `scripts/conform.sh audit --all`
so the public summary carries counts only and the private repo carries
full per-finding detail (decision #16). Found and fixed a real gap while
building it: the email check had been printing the actual discovered
address into the public summary this whole time, unlike the secrets and
private-URL checks, which already redacted to `file:line`. **Not yet
live end to end**: the reporting repo exists and its initial commit is
pushed, but the workflow's publish step needs a
`CONFORMIT_REPORTING_TOKEN` secret (fine-grained PAT, scoped to that repo
only, `contents: write`) that the maintainer is adding themselves. Until
it exists, that step is skipped, not failed, and the workflow behaves
exactly as before.

Seventh session (previous day): surveyed
external standards for AI-assisted work and adopted two (decision #15).
`AGENTS.md` replaces `CLAUDE.md` as the required agent-instructions file
(`CLAUDE.md` is now a one-line `@AGENTS.md` import, Anthropic's own
pattern); AI-authored commits carry `Assisted-by:`, the Linux kernel's
convention, instead of `Co-Authored-By:`. Both templates built
(`templates/AGENTS.md`, `templates/CLAUDE.md`) and applied to conformIT's
own root immediately, closing the `CLAUDE.md` gap this file has tracked
since the fourth session, just not in the shape originally planned.

Sixth session, same day as the fifth: added
sensitive-content scanning (secrets via gitleaks, personal emails, private
URLs) with a CRIT severity tier that's the one exception to "audit never
fails the job" (decision #13), and a copyable README scaffold plus a
warranty-disclaimer requirement (decision #14). `docs/credits.md` now
exists for real, since gitleaks is conformIT's first adopted dependency,
narrowing decision #10 exactly the way it predicted.

Fifth session (earlier the same day): built the first real tool,
`scripts/conform.sh audit`, plus a scheduled GitHub Actions workflow that
runs it against every repo in `registry/targets.yaml` and posts a
pass/fail table to the job summary. This closed flashDK finding #1 below
("there is still no tool to run") and partially resolved the open
question about whether conformIT installs into projects: for auditing,
the answer is no, it's a reference that clones and checks a target from
outside, per decision #12. Also closed finding #2 (`security.md`/
`SECURITY.md`) and decision #10's own loose end (the required-file table
was never actually marked conditional), both from the fourth session.

**Immediately useful finding from testing the new tool against real
repos:** `almadon/novak-integracije`, `almadon/novak-konzol`, and
`almadon/consigliere` have none of the required doc set at all (no
`LICENSE`, `CLAUDE.md`, `docs/STATE.md`, `docs/decisions.md`, or
`CHANGELOG.md`), and two of the three fail the LLM-disclosure heuristic.
`flashctrl/flashDK`, the one project that got a manual pass already,
comes back nearly clean. The tool tracks reality; see the full run
recorded in decision #12's "what it cost" section for the caveats before
treating any single FAIL as certain.

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
- **flashDK is the first project conformIT has been checked against.**
  flashDK is an external, unrelated Apache-2.0 SDK (a clean-room client
  library for IP-KVM devices), audited by reading this repository's `docs/`
  directly rather than through `scripts/conform.sh`, which still doesn't
  exist. The audit produced two PRs against flashDK (adding the required
  documentation set, and separately fixing every em dash the standard's own
  grep command would have caught), both pending review at the time of this
  note, not yet merged. See "findings from flashDK's application" below for
  what the standard itself should take from it.

## What is not built yet

- **`scripts/conform.sh audit` exists and works.** `init` still doesn't;
  running it prints a message pointing here instead of silently doing
  nothing. Audit supports a local path, an `owner/repo` shorthand, and
  `--all` against `registry/targets.yaml`; the checks live in
  `scripts/lib/audit-checks.sh` so all three modes share one
  implementation.
- **`.github/workflows/audit.yml` runs it weekly** (Mondays, 13:00 UTC)
  and on manual dispatch, against the six repos currently declared in
  `registry/targets.yaml` (conformIT itself included, deliberately). Not
  yet observed running for real on a schedule, only tested by running
  the same script locally against the same repos; see decision #12.
- **`almadon/conformIT-reporting` (private) exists**, seeded with an
  initial commit, but the workflow's publish step to it hasn't run for
  real: it needs a `CONFORMIT_REPORTING_TOKEN` secret in this repo,
  fine-grained PAT, scoped to that repo only, `contents: write`, and the
  maintainer hasn't added it yet. Until it does, that step is skipped
  and everything else behaves as before; see decision #16.
- **`templates/` is partially populated.** `.githooks/commit-msg`,
  `.githooks/pre-commit` (the em-dash check), `.gitmessage`,
  `docs/README.md` (decision #14), and now `AGENTS.md` plus a `CLAUDE.md`
  stub (decision #15) exist. Still missing: skeletons for the other
  required `docs/` files, and a `.claude/settings.json` baseline.
- **The pre-commit hook exists but isn't installed anywhere, including
  here.** conformIT's own repo doesn't run it yet; per decision #10,
  `AGENTS.md` (then still `CLAUDE.md`) and `CHANGELOG.md` were
  prioritized as the open gaps first. `AGENTS.md` is done now;
  `CHANGELOG.md` is the one that's still open.
  Its scope is `docs/` and `README.md` only, matching writing-style.md's
  stated scope, which is why two pre-ban em dashes in `templates/` (a
  comment and a `.gitmessage` line, both predating decision #7) survived
  every grep run so far and were only caught by widening the check by
  hand this session. Not evidence the scope is wrong, since template
  comments aren't documentation, but worth knowing the hook wouldn't have
  caught these on its own.
- **No `CHANGELOG.md`** for conformIT itself, which its own documentation
  standard requires. Noted rather than silently excused.

## Findings from the survey worth acting on

Recorded here because they are project-level problems the standards imply
but don't themselves fix:

1. **Eight of nine repos have no `LICENSE`.** They default to all rights
   reserved, which is almost certainly not the intent for at least some of
   them. This is the single highest-value fix available and it's cheap.
2. **No repo has an agent-instructions file** (`CLAUDE.md` at the time
   this finding was written; `AGENTS.md` is the standard as of decision
   #15). Every session re-derives conventions that are already written
   down in prose the model isn't being pointed at.
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

## Findings from flashDK's application, worth acting on

The survey read nine repos that already existed. Applying the standard to a
tenth, from outside, surfaced a different kind of gap: not "this repo
doesn't do X" but "the standard doesn't say what to do when X." Recorded
here rather than folded into decisions.md, since these are observations
from one external application, not decisions the maintainer has made.

1. ~~There is still no tool to run.~~ **Fixed 2026-08-26**:
   `scripts/conform.sh audit` and the scheduled workflow exist now. It's a
   report-only script checking the required file set, the README
   heuristics, the em-dash scan, and recent commit-message conformance,
   which is a meaningful fraction of what a manual read caught, though not
   all of it: rules 3-6 below are all judgment calls a script can't make.
2. ~~`docs/security.md` and a repository's top-level `SECURITY.md` are easy
   to conflate.`~~ **Fixed 2026-08-26**: `documentation-standard.md` now
   has the disambiguating sentence directly under the required-file table.
3. **Security-posture rule 8 ("pin versions") and mainstream library
   convention in at least one ecosystem pull in opposite directions, and
   the rule doesn't acknowledge the tension.** The usual advice for a
   published Rust library is to omit its lockfile, so a downstream
   consumer's own dependency resolution controls the final build; rule 8
   argues for pinning generally, citing reproducibility and offline-outage
   risk. Both are right, for different kinds of artifact: something with
   runnable binaries wants a committed lockfile, a pure library generally
   doesn't, because its own lockfile has no effect on a consumer's build.
   flashDK's answer was that its workspace ships example binaries
   alongside the library, so it committed the lockfile for that reason
   specifically. Rule 8 doesn't currently have room for that distinction,
   and it likely isn't Rust-specific; other ecosystems draw a similar line
   between an application and a published package.
4. **Rule 8 also names "an unpinned action" as a flat failure mode, with no
   room for an action that's deliberately designed to float.**
   `dtolnay/rust-toolchain@stable` exists specifically to track whatever
   Rust currently calls "stable"; pinning it to a commit would defeat its
   purpose rather than harden it. flashDK's fix was to document the
   exception in its workflow file rather than force a pin, but a
   maintainer applying rule 8 literally for the first time could
   reasonably read it as having no exceptions. One sentence acknowledging
   that a small number of dependencies are intentionally designed to
   float, and that documenting the exception is the correct response
   rather than defeating the dependency's purpose, would have made this an
   easier call.
5. **`design-principles.md` doesn't distinguish which principles are
   infrastructure-shaped versus universal, and that matters for a project
   this document wasn't written for.** Applying it to flashDK, a client
   SDK with no server component, meant deciding that several principles (a
   services layer distinct from its clients, declare/apply/drift,
   single-homed until a second node exists) were simply not applicable,
   rather than violated. There's no documented way to record "not
   applicable, and here's why" the way `decisions.md` records a genuine
   departure, so an outside reader auditing a repository against
   `design-principles.md` can't tell the difference between a principle
   that was considered and rejected and one that never applied in the
   first place. A convention for recording inapplicability explicitly,
   perhaps as its own short section distinct from a rejected alternative,
   seems like it would generalize beyond this one case.
6. **The documentation standard's required-file table doesn't address a
   workspace or monorepo with more than one package.** flashDK is a single
   Cargo workspace with two crates, and one repository-root
   `docs/credits.md` and `docs/decisions.md` covering both worked fine
   here. That's an unstated assumption, though: a project with genuinely
   divergent per-package dependency sets, or packages published and
   versioned independently, might reasonably want per-package credits
   tables instead. Worth a line either way, even if the answer is
   "repo-root is fine unless there's a specific reason otherwise."

## Open questions

- Does conformIT install into projects for the parts other than
  auditing (a plugin, a submodule, a copied scaffold), or stay a pure
  reference? Resolved for auditing specifically (decision #12: reference,
  nothing installed, a target is cloned and thrown away). Still open for
  `init` and for `templates/`, whose whole point is to be copied into a
  target repo; those don't have the "clone and discard" option auditing
  does, so this question isn't actually closed, just narrowed.
- ~~Is `CLAUDE.md` per-repo, or one shared file plus a thin per-repo
  overlay?~~ **Resolved by decision #15**: `AGENTS.md` per repo, with
  the Rules of Engagement distilled into it rather than repeated in
  full; `templates/AGENTS.md`'s placeholder sections are exactly the
  per-repo scopes/commands/stack overlay this question was asking
  about.
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
