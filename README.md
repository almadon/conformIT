# conformIT

Uniform engineering standards for AI-assisted software work: the rules that
should hold across every repo, regardless of language, stack, or whether a
human or a model wrote the line.

**Status: in testing.** Checked against six real repositories via the
recurring audit below; not yet enforced anywhere through installed
tooling. This project comes with no warranty or guarantee of fitness for
any purpose. Use it at your own risk. See [STATE.md](docs/STATE.md).

**LLM use:** this project is built and maintained with substantial AI
assistance (Claude Code). The standards were drafted by a model from a
survey of nine existing repos, then reviewed, corrected, and directed by the
maintainer across multiple sessions. Individual commits disclose AI
authorship in their trailers; see
[commit-and-history.md](docs/commit-and-history.md).

Two halves, and both are required:

- **`docs/`**: the standards themselves. Prose, with reasoning and cost
  stated, because a rule whose justification isn't recorded gets
  re-litigated or quietly reversed by someone who assumed it was arbitrary.
- **`templates/` + `scripts/`**: the machinery that applies them, so
  conformance is the default rather than an act of discipline. Git hooks,
  an audit tool, a README scaffold, and `AGENTS.md`/`CLAUDE.md` exist
  today. A `.claude/settings.json` baseline and `conform.sh init` are
  designed but not yet built; see [STATE.md](docs/STATE.md) for what's
  real.

Standards nobody enforces drift. Enforcement nobody understands gets
disabled. That's why neither half ships alone.

## Use cases

- You maintain several repos and want the same baseline (licence, commit
  style, disclosure, a place to record decisions) without re-deriving it
  by hand in each one.
- You're about to make a repo public and want a check for what shouldn't
  be in it (secrets, personal emails, internal URLs) before it happens
  rather than after.
- You want an AI agent working in your repos to have a written standard
  to work from, instead of re-inferring your conventions every session.

## The standards

| | |
|---|---|
| [Rules of Engagement](docs/rules-of-engagement.md) | How an AI agent is expected to work in these repos: scope, verification, honesty about what was and wasn't checked |
| [Design principles](docs/design-principles.md) | Structural defaults: services over apps, declare/apply/drift, replaceability |
| [Security posture](docs/security-posture.md) | Capabilities not credentials, least privilege, untrusted retrieved content, exposure decisions |
| [Licensing & provenance](docs/licensing-and-provenance.md) | Dependency hygiene, licence verification, attribution, and clean-room procedure |
| [Documentation standard](docs/documentation-standard.md) | Which files every project has, what belongs in each, and the honesty conventions |
| [Writing style](docs/writing-style.md) | No em dashes, no AI-sounding prose, and why that matters here specifically |
| [Commit & history](docs/commit-and-history.md) | Conventional Commits, hook-enforced, and what the body is actually for |
| [Credits](docs/credits.md) | conformIT's own adopted dependencies, pinned and checksum-verified |

## conformIT's own record

| | |
|---|---|
| [Decisions](docs/decisions.md) | Every standard that was contested, with the alternative and the cost |
| [State](docs/STATE.md) | What is real right now, and what is still a claim |

## Adopting it

```bash
scripts/conform.sh audit <path>          # a local checkout
scripts/conform.sh audit <owner/repo>    # clones a public repo and checks it
scripts/conform.sh audit --all           # every repo in registry/targets.yaml
scripts/conform.sh init                  # not implemented yet, see STATE.md
```

`audit` reports. It never rewrites the target, and existing repos are not
retroactively migrated; see decision #2. `init`, the other half of what
this section used to promise, is still just a stub; see
[STATE.md](docs/STATE.md) for what's real.

For a new project's `README.md`, copy
[`templates/docs/README.md`](templates/docs/README.md) by hand for now;
`init` will place it automatically once it exists (decision #14). Same
for [`templates/AGENTS.md`](templates/AGENTS.md) and
[`templates/CLAUDE.md`](templates/CLAUDE.md) (decision #15). Copy both;
`CLAUDE.md` is one line and doesn't need editing.

To run the recurring audit against your own repos, from your own
org, without forking anything: copy
[`templates/.github/workflows/conform-audit.yml`](templates/.github/workflows/conform-audit.yml).
It calls `.github/workflows/reusable-audit.yml` here, and your org
never shares a credential with conformIT or with any other adopter;
each org holds its own reporting-repo token, referenced only inside its
own job. See decision [#17](docs/decisions.md) for why this is a
reusable workflow rather than a GitHub App, and
["Reference or fork?"](#reference-or-fork) below for the deeper choice
between this and actually forking.

## Reference or fork?

Two ways to relate to this repo, and they're not a beginner/advanced
progression, they're a real choice with a real cost on each side.
Picking wrong doesn't break anything, but it does mean redoing setup
work later, so it's worth reading both before choosing.

**Reference conformIT directly** (`uses:
almadon/conformIT/.github/workflows/reusable-audit.yml@v1` in your own
workflow, per [`templates/.github/workflows/conform-audit.yml`](templates/.github/workflows/conform-audit.yml)):
you get the standards as conformIT defines them, unmodified, and the
audit tooling stays current with zero effort on your part beyond
choosing when to bump the pinned tag.

**Fork the repo**: you get your own copy of everything, `docs/`
included, to keep, edit, or delete as you choose, starting from
conformIT's own `docs/decisions.md` as the base record rather than a
blank page.

| | Reference | Fork |
|---|---|---|
| **You get** | conformIT's opinions, as published | Your own copy, editable from commit one |
| **Upgrades** | Bump the pinned tag/SHA when you choose to | Manual: merge or rebase upstream changes yourself, or don't |
| **Customizing a rule** | Not possible; the standard is what it is | Edit `docs/` and `scripts/` directly |
| **Adding your own checks** | Not possible from the caller side | Edit `scripts/lib/audit-checks.sh` directly |
| **Staying current costs** | One line (the pinned ref) to review per bump | Ongoing: every upstream change is a merge you have to evaluate |
| **Divergence is** | Impossible by construction | Your responsibility to record, the way decision #1 records anjunatree's rejected slug format instead of pretending it didn't happen |
| **Setup effort** | A three-line caller workflow, a reporting repo, a scoped PAT | The same, plus you now maintain a second copy of everything conformIT maintains |
| **Right for** | "I want these standards applied to my repos" | "I want to start from these standards and make them mine" |

**The failure mode on each side, stated plainly:**

- Referencing and never bumping the pin is the same failure as any
  unpinned-forever dependency: you stop getting fixes, silently, and
  nothing tells you you've stopped. Review the pin periodically, the
  same way you'd review any other pinned version.
- Forking and never reconciling with upstream is the same failure
  anjunatree's rejected commit format would have been if nobody wrote
  down why it diverged (decision #1): a fork with unrecorded departures
  from its base is indistinguishable, a year later, from a fork that
  just drifted by accident. If you fork, keep `docs/decisions.md`'s own
  discipline: when you diverge from something conformIT still does
  upstream, write down what you chose and why, the same way conformIT
  itself does for every departure from the repos it was derived from.

Nothing stops switching later. Forking after months of referencing just
means your first fork commit already has a real `docs/decisions.md` to
build on rather than an empty one.

## Recurring audit

A [scheduled workflow](.github/workflows/audit.yml) runs `conform.sh audit
--all` weekly against the public repos declared in
[`registry/targets.yaml`](registry/targets.yaml). It's report-only for
most findings: a target failing every compliance check doesn't fail the
job, and nothing is ever written back to a target. See decision
[#12](docs/decisions.md) for the scope (public repos only, no auto-fix)
and its caveats (the README-disclosure checks are regex heuristics, and
the commit-style check penalizes history older than this standard).

Output is split by audience, not just posted in one place. The job
summary in this repo's Actions tab (public, since this repo is public)
carries pass/warn/fail/crit counts only. The full per-finding detail,
including file:line samples for anything the sensitive-content checks
below flag, goes to `almadon/conformIT-reporting` (private), one file per
target, overwritten each run so its git history is the trend record. See
decision [#16](docs/decisions.md).

**One exception**: the audit also scans for likely secrets (via
[gitleaks](https://github.com/gitleaks/gitleaks), pinned and
checksum-verified; see [credits.md](docs/credits.md)), personal email
addresses not already public via git authorship, and private-service
URLs. A likely secret is severe enough to break the "report-only" rule
on purpose: it fails the job outright and the report tells you to rotate
the credential and notify everyone with access, immediately, before
doing anything else. See decision [#13](docs/decisions.md) for what this
does and doesn't cover (current tree only, not git history).

The audit also runs a static-analysis (SAST) pass via
[semgrep](https://github.com/semgrep/semgrep), pinned; see
[credits.md](docs/credits.md). Real but partial coverage, stated
plainly rather than oversold: tested against a fixture with both a
command-injection pattern (caught) and a string-concatenated SQL query
(missed by the two rulesets used). For genuine dataflow analysis,
[CodeQL](https://codeql.github.com/) is offered as a separate template
(`templates/.github/workflows/codeql.yml`) an adopter runs on their own
repo, since it needs per-repo build configuration this generic audit
can't supply. See decision [#18](docs/decisions.md).

## Provenance

These standards were derived from patterns already present and
independently repeated across nine of the author's projects, not invented
from scratch. The specific sources are cited inline in each document, so a
reader can judge whether a rule earned its place or is one project's habit
dressed up as a principle.

## Licence

Dual, by content type:

- **Prose in `docs/`**: [CC BY 4.0](LICENSE-docs). Use the standards, adapt
  them, keep the attribution.
- **Everything else** (templates, hooks, scripts): [MIT](LICENSE). Meant to
  be copied into your repo without dragging an attribution obligation into
  your codebase.
