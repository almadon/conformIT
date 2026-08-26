# Credits

## Running in the audit workflow

| Project | Used for | Licence |
|---|---|---|
| [gitleaks](https://github.com/gitleaks/gitleaks) | Secret scanning in `scripts/lib/audit-checks.sh` | MIT |

Pinned to v8.30.1. `.github/workflows/audit.yml` downloads the `linux_x64`
release archive and verifies it against a sha256 confirmed at the time
this file was written, using the checksums gitleaks itself publishes with
each release. A local run of `scripts/conform.sh audit` uses whatever
`gitleaks` is already on the operator's `PATH`, or falls back to a
narrower heuristic scan documented inline in
`scripts/lib/audit-checks.sh` if gitleaks isn't installed; either way,
nothing is downloaded or installed onto the operator's own machine by
this project's own code. See [decisions.md](decisions.md) #13.

## Evaluated and not adopted

| Project | Outcome |
|---|---|
| [trufflehog](https://github.com/trufflesecurity/trufflehog) | Also a credible choice for the same job; gitleaks was picked for a smaller binary and a simpler single-binary release artifact, not because trufflehog is worse. Revisit if gitleaks's false-negative rate on real findings turns out to matter. |

## On adding dependencies

This file exists because gitleaks is the first real, adopted dependency
this project has: see [decisions.md](decisions.md) #10, which exempted
`docs/credits.md` on the premise that conformIT had none, and named
exactly this condition as what would end the exemption.

Before adding another:

1. Record it here with a link and licence.
2. Pin a version, verified against a real checksum, the way gitleaks is
   above. Don't hand-edit a hash without re-running the verification.
3. Check it isn't already solved without a dependency, per
   [rules-of-engagement.md](rules-of-engagement.md) rule 7.
