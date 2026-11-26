# Pinning and keeping up to date

How a conforming project stays current without adopting a release the minute
it appears. The policy is decision #26, corrected by #34. This page is how to
live with it. Items marked VERIFY have not been confirmed.

## The idea

Two risks pull in opposite directions. A dependency that is never refreshed
goes stale until a build breaks (a three-month-old cached `node:22-bookworm`
did that to burnand.shop). A dependency that floats takes whatever was
published a minute ago, including a hijacked release. The answer is four
steps, in this order.

1. **Pin** what you run, so today's build and next week's are the same.
2. **Propose** updates automatically, as pull requests, so pins do not rot.
3. **Wait** before a new release is proposed: the cooldown. Most bad releases
   are found and pulled within days.
4. **Check** in CI, then merge. A person merges.

Security fixes skip the wait.

## What the cooldown is

| Release | Wait before it is proposed |
|---|---|
| ordinary | 7 days |
| new major version | 14 days, where the updater can express it |
| security fix | none |

It delays the *proposal*. It does not remove a version you already run, and
it does not hold back a pin you change by hand.

## What to pin, and what moves it

| Thing | Pin with | Moved by |
|---|---|---|
| npm | `package-lock.json` | Dependabot or Renovate |
| pnpm | `pnpm-lock.yaml` | Dependabot or Renovate |
| Python | `==` pins with hashes, or `uv.lock` | Dependabot or Renovate |
| Cargo | `Cargo.lock` | Dependabot or Renovate |
| Actions | a version tag, or better a commit SHA with a `# vX.Y.Z` comment | Dependabot or Renovate |
| Base images | `name:tag@sha256:...` | Renovate, or Dependabot (VERIFY that it bumps digests, and that its cooldown applies to them) |
| Home Assistant `manifest.json` | `==` in `requirements` | Renovate's Home Assistant manifest manager (VERIFY it finds `custom_components/`); Dependabot does not read it (VERIFY) |
| Versions in scripts, Ansible variables, templates | the version, plus a checksum for a download | **nothing, by default** |

The last row is where staleness hides. No updater and no conformIT check sees
a version written into a role variable or a `curl` line. For each one, either
teach Renovate to read it with a custom regex manager (VERIFY on your files),
or list it in `docs/decisions.md` with a review date. conformIT's own pinned
`gitleaks` and `osv-scanner` downloads are in this row and are reviewed by
hand.

To get an image's digest, after its tag has aged past the cooldown:

```bash
docker buildx imagetools inspect node:24-alpine
```

## GitHub: Dependabot

`.github/dependabot.yml`. **Only some ecosystems accept
`semver-major-days`.** npm, pip, uv and Cargo do. GitHub Actions, Docker,
Docker Compose, Terraform, Helm and pre-commit do not (the full list is in
#34). Leave the key out where unsupported: the file may be rejected, and then
nothing updates.

```yaml
version: 2
updates:
  - package-ecosystem: npm
    directory: /
    schedule:
      interval: weekly
    cooldown:
      default-days: 7
      semver-major-days: 14
  - package-ecosystem: github-actions
    directory: /
    schedule:
      interval: weekly
    cooldown:
      default-days: 7
  - package-ecosystem: docker
    directory: /console   # the folder that holds the Dockerfile
    schedule:
      interval: weekly
    cooldown:
      default-days: 7
```

For majors of Actions and images, either set `default-days: 14` on those
entries (patches wait too), or keep 7 and have the reviewer leave a major for
another week. Pick one and write it down.

Then, in the repository settings, switch on Dependabot **security updates**.
They are not controlled by this file, and the cooldown does not apply to
them. With no `cooldown` at all, Dependabot still waits 3 days. After editing,
look for a config error on the repository's Dependabot page (Insights,
Dependency graph).

## Forgejo: Renovate

Dependabot does not run on Forgejo.

```json
{
  "$schema": "https://docs.renovatebot.com/renovate-schema.json",
  "extends": ["config:recommended"],
  "minimumReleaseAge": "7 days",
  "packageRules": [
    { "matchUpdateTypes": ["major"], "minimumReleaseAge": "14 days" }
  ],
  "osvVulnerabilityAlerts": true,
  "vulnerabilityAlerts": { "minimumReleaseAge": null }
}
```

**The security lane is weaker here.** Forgejo has no vulnerability-alert API.
`osvVulnerabilityAlerts` is experimental and covers direct dependencies only,
so a fix in a transitive package or a base image will not arrive early. Keep a
manual security review on a stated cadence and bump urgent fixes by hand.
VERIFY: a search result says Renovate before 44.3.1 did not apply the minimum
age to digest updates, so check your version before relying on it for images.
Running Renovate as a scheduled Forgejo job is also untested here.

## Your own installs wait too

The updater only governs its own pull requests. A developer's or CI's install
can still take today's release.

| Tool | Setting |
|---|---|
| npm | `.npmrc`: `min-release-age=7` (days; VERIFY it first appeared in 11.10) |
| pnpm | `pnpm-workspace.yaml`: `minimumReleaseAge: 10080` (minutes) |
| uv | `pyproject.toml`: `[tool.uv]` with `exclude-newer = "7 days"` (VERIFY: reported to need uv 0.9.17 or later) |
| pip | VERIFY: no setting confirmed here |

These settings act when versions are **chosen**, as in `npm install` or an
update. `npm ci` installs exactly what the lockfile lists, and the
ha-propsense session reports that it ignores `min-release-age` (VERIFY). So a
release that is already in the lockfile is installed however new it is. The
wait has to happen before the lockfile changes: in the updater, in the local
install that writes it, and in the review of that change.

## Runner and host images

A pinned file does nothing for an image cached on a runner. Pull on a weekly
schedule and restart the runner. Once the label carries a digest, the pull
cannot change what runs, and a new image arrives as a reviewed change to the
digest. The audit cannot see a runner's cache.

## Deliberate exceptions

Two comments record an exception where a reviewer will see it. **Both need a
reason.** A bare marker does nothing.

```text
# conformit:allow-unpinned the linter should pick up new rules
```

Goes in a `requirements*.txt`, `pyproject.toml` or `Cargo.toml` (not
`package.json`, which has no comments). The audit then lists the file as
deliberately unpinned.

```yaml
- uses: hacs/action@main # conformit:allow-floating HACS documents this ref
```

An exception also steps outside the cooldown: an unpinned tool takes the
newest release at once. Where the tool allows it, keep the delay without the
pin. For a lint requirements file installed with uv, `exclude-newer` does
that: new rules still arrive, a week late.

## The routine

| When | Do |
|---|---|
| As they arrive | Merge security updates once CI passes. Do not wait. |
| Weekly | Review the update pull requests. They have already waited. Read the notes for majors. Refresh runner images. |
| Monthly | Run the conformIT audit. Check the updater is still opening pull requests: silence can mean a broken config. On Forgejo, do the manual security review. |
| Quarterly | Re-read every exception comment and the hand-pinned list. Remove what no longer has a reason. |

## Adopting it, in order

1. Commit lockfiles.
2. Add the updater config, then confirm it is accepted.
3. Switch on security updates, or set the Forgejo review cadence.
4. Add the install-time setting.
5. Pin images by digest.
6. List what no updater sees.
7. Comment each deliberate exception.
