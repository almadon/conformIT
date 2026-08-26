# conformIT

Uniform engineering standards for AI-assisted software work: the rules that
should hold across every repo, regardless of language, stack, or whether a
human or a model wrote the line.

**Status: in testing.** Checked against six real repositories via the
recurring audit below; not yet enforced anywhere through installed
tooling. See [STATE.md](docs/STATE.md).

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
  conformance is the default rather than an act of discipline. Git hooks
  and an audit tool exist today. A `CLAUDE.md`, a settings baseline, doc
  scaffolding, and `conform.sh init` are designed but not yet built; see
  [STATE.md](docs/STATE.md) for what's real.

Standards nobody enforces drift. Enforcement nobody understands gets
disabled. That's why neither half ships alone.

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

## Recurring audit

A [scheduled workflow](.github/workflows/audit.yml) runs `conform.sh audit
--all` weekly against the public repos declared in
[`registry/targets.yaml`](registry/targets.yaml), and posts a readable
pass/fail table to the run's job summary in the Actions tab. It's
report-only: a target failing every check doesn't fail the job, and
nothing is ever written back to a target or committed here. See decision
[#12](docs/decisions.md) for the scope (public repos only, no auto-fix,
no persisted report) and its caveats (the README-disclosure checks are
regex heuristics, and the commit-style check penalizes history older than
this standard).

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
