# Where this got to

Working notes for conformIT itself. Delete this file once the standards
have been applied to a real project and the process has settled. Per
[documentation-standard.md](documentation-standard.md), `STATE.md` is the
one document with an expiry.

**Last updated:** 2026-08-25. Third session: conformIT was checked against a
real project (flashDK, an external Apache-2.0 SDK) for the first time.
Findings from that application are appended below, and the "nothing has been
applied" line lower in this file is no longer accurate.

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
- **`docs/decisions.md` records seven decisions**, including the one genuine
  conflict found between existing repos (commit format) and the two added
  in this session (status/LLM disclosure, writing style).
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

## Findings from flashDK's application, worth acting on

The survey read nine repos that already existed. Applying the standard to a
tenth, from outside, surfaced a different kind of gap: not "this repo
doesn't do X" but "the standard doesn't say what to do when X." Recorded
here rather than folded into decisions.md, since these are observations
from one external application, not decisions the maintainer has made.

1. **There is still no tool to run.** Checking flashDK meant reading all
   eight standards documents and cross-checking a real repository against
   each by hand, including running the em-dash grep manually, since nothing
   runs it automatically. This is exactly the gap "what is not built yet"
   already names, from the other side: the first real use of conformIT
   confirms that gap costs real time, not just theoretical tidiness. Even a
   minimal, report-only script checking for the required file set and
   running the documented greps would have caught a meaningful fraction of
   what turned up, mechanically, before a human or a model read a single
   document.
2. **`docs/security.md` and a repository's top-level `SECURITY.md` are easy
   to conflate, and nothing here says they're different files.** GitHub
   gives `SECURITY.md` special handling in its own UI (the "Report a
   vulnerability" button), which is a different convention from this
   standard's `docs/security.md` ("the project's instance of the security
   posture"). A project following both conventions ends up with two
   similarly named files covering different things. flashDK resolved it by
   having each file point at the other; `documentation-standard.md` could
   save the next project that confusion with one sentence.
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
