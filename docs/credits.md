# Credits

## Running in the audit workflow

| Project | Used for | Licence |
|---|---|---|
| [gitleaks](https://github.com/gitleaks/gitleaks) | Secret scanning in `scripts/lib/audit-checks.sh` | MIT |
| [semgrep](https://github.com/semgrep/semgrep) | Static analysis (SAST) in `scripts/lib/audit-checks.sh` | LGPL-2.1 |

**gitleaks**, pinned to v8.30.1. `.github/workflows/reusable-audit.yml`
downloads the `linux_x64` release archive and verifies it against a
sha256 confirmed at the time this file was written, using the checksums
gitleaks itself publishes with each release. A local run of
`scripts/conform.sh audit` uses whatever `gitleaks` is already on the
operator's `PATH`, or falls back to a narrower heuristic scan documented
inline in `scripts/lib/audit-checks.sh` if gitleaks isn't installed;
either way, nothing is downloaded or installed onto the operator's own
machine by this project's own code. See [decisions.md](decisions.md)
#13.

**semgrep**, pinned to v1.175.0.
`.github/workflows/reusable-audit.yml` installs it via
`pip install semgrep==1.175.0`, a version pin rather than a checksum
verification: semgrep distributes through PyPI with a real dependency
tree, not a single downloadable binary the way gitleaks is, and fully
hash-pinning the whole tree (`pip install --require-hashes`) is real,
ongoing lockfile maintenance disproportionate to what it buys here. A
lighter verification bar than gitleaks's, deliberately, relying on
PyPI's own integrity and TLS guarantees instead, the same trust model
most pip/npm-pinned dependencies already use. A local run uses whatever
`semgrep` is already on the operator's `PATH`, or skips the check
entirely (not a false pass) if it isn't installed; there's no honest
heuristic fallback for "contains a SQL injection" the way there is for
"looks like an AWS key." See [decisions.md](decisions.md) #18.

## Evaluated and not adopted

| Project | Outcome |
|---|---|
| [trufflehog](https://github.com/trufflesecurity/trufflehog) | Also a credible choice for the same secret-scanning job; gitleaks was picked for a smaller binary and a simpler single-binary release artifact, not because trufflehog is worse. Revisit if gitleaks's false-negative rate on real findings turns out to matter. |
| [CodeQL](https://codeql.github.com/) | The deeper tool for the SAST job: genuine dataflow analysis, not pattern matching. Not adopted for the generic audit specifically because it needs to know how to build the target, which has to be configured per-repo and isn't something this audit can supply for an arbitrary clone. Offered instead as a separate, opt-in template (`templates/.github/workflows/codeql.yml`) for an adopter's own CI. |

## On adding dependencies

This file exists because gitleaks was the first real, adopted
dependency this project had: see [decisions.md](decisions.md) #10,
which exempted `docs/credits.md` on the premise that conformIT had
none, and named exactly this condition as what would end the exemption.

Before adding another:

1. Record it here with a link and licence.
2. Pin a version, verified against a real checksum where the
   distribution method makes that practical (gitleaks); where it
   doesn't (semgrep), pin the version anyway and say plainly why a
   checksum wasn't practical, rather than silently pinning less
   rigorously and calling it the same thing.
3. Check it isn't already solved without a dependency, per
   [rules-of-engagement.md](rules-of-engagement.md) rule 7.
