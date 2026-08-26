# Decisions

conformIT's own record, kept to the standard it defines in
[documentation-standard.md](documentation-standard.md). Numbered, stable,
never reused. A reversed decision gets a new entry; the old one stays.

## 1. Conventional Commits is the standard, not the slug format

Two incompatible conventions existed across the surveyed repos:

- `novak/docs/commit-style.md`: Conventional Commits, hook-enforced, with a
  full type table and a documented rationale.
- `anjunatree/CONTRIBUTING.md`: lowercase hyphenated slugs
  (`feature-personal-constellation`), explicitly "no scope parentheses,"
  subject reads as a slug rather than a sentence.

**Chosen:** Conventional Commits.

**Why:** it is machine-readable, which makes changelog generation and
semantic versioning available later at no cost now. The slug format is
readable but parses to nothing. novak's version also already carries the
reasoning for the body conventions, which are the part that actually
matters.

**What it cost:** anjunatree's format is genuinely tidier to read in a
`git log --oneline`, and its author preferred it deliberately, not by
default. Subjects get longer. One repo's documented convention is
overridden by a cross-cutting standard, which is a real cost the first time
it happens and sets the precedent for every later conflict.

**What would justify revisiting:** if changelog generation and semver are
still unimplemented in a year, the machine-readability argument was
theoretical and the tidier format should win.

**Still open:** whether anjunatree migrates at all. See #2.

## 2. Existing repos are audited, never retroactively migrated

`scripts/conform.sh audit` reports divergence. It does not rewrite, and
there is no `--fix`.

**Why:** rewriting a working repo to satisfy a standard is a large diff with
no functional change, it destroys `git blame`, and it front-loads all the
cost of a standard before any of its benefit. Conformance is worth having
going forward. It is rarely worth a migration.

**What it cost:** the repos stay inconsistent, possibly for a long time. An
audit that nobody acts on is just a list. anjunatree in particular will have
non-conforming history indefinitely.

**Rejected:** an autofix mode. It would be used once, on the wrong repo, at
the wrong time.

**What would justify revisiting:** a repo being prepared for publication,
where inconsistency is externally visible.

## 3. Dual licence: CC BY 4.0 for prose, MIT for everything else

**Why:** the two halves have different purposes. The standards are meant to
be read, cited, and adapted, and attribution should survive that; CC BY is
built for it. The templates and hooks are meant to be copied into someone
else's repo, and a copyleft or attribution obligation riding along into
their codebase would stop people using them.

**What it cost:** a two-licence repo is more complicated to explain than a
one-licence repo, and someone will eventually copy a doc under the
impression it's MIT. The `README` states the split explicitly to reduce
that.

**Rejected:** MIT throughout (attribution on prose is the point, and MIT's
attribution requirement is aimed at source files). CC BY throughout (a bad
fit for code, and CC explicitly advises against it for software).

## 4. Rules are derived from repeated practice, and cite their source

A rule enters the standard only if it is either (a) observed working in more
than one existing project, or (b) a deliberate new decision recorded here
with its reasoning. Inline citations name the file it came from.

**Why:** the difference between a standard and a preference is evidence.
The citations let a reader judge each rule independently instead of
accepting or rejecting the set, and they make it obvious when a rule is one
project's habit generalised too eagerly.

**What it cost:** the documents are longer and more cluttered with paths
than a clean set of assertions would be. Some genuinely good ideas are
excluded for having only one instance behind them.

**Still open:** whether the citations should be stripped for the public
release, since they point at repos an outside reader cannot see. Current
answer is no. A reader who cannot verify a source can at least see that one
was claimed, and see which rules have none.

## 5. Every rule states its cost

**Why:** a rule that reads as free gets ignored the first time it isn't.
Naming the cost up front means the trade-off was made deliberately, and
gives anyone departing from a rule a stated basis for doing so.

**What it cost:** roughly a third of the word count, and it makes the
standards less quotable.

**Still open:** rule 9 of the Rules of Engagement claims a cost of "none."
Two design principles do the same. If several rules are genuinely free, the
convention is weaker than it looks and those may just be well-chosen. VERIFY
against real use.

## 6. Every project discloses LLM use and states a status

Added after direct instruction from the maintainer, not derived from the
surveyed repos: none of the nine currently does this.

**Why:** a reader deciding whether to trust or adopt a project shouldn't
have to guess how it was built, or whether it's ready to rely on. Both are
facts about the project that the code itself doesn't reveal, which is
exactly the kind of thing this whole standard exists to make explicit rather
than implicit.

**Why "in testing" is the default, not an option:** an unstated status reads
as an implicit claim of stability. Requiring the maintainer to actively
declare "stable" moves the burden of proof onto the claim that needs it.

**What it cost:** a small amount of README real estate on every project,
including ones where the answer is obvious to the maintainer. It isn't
obvious to a new reader, which is the point.

**What would justify revisiting:** nothing so far. This is a disclosure
requirement, not a technical trade-off, and disclosure requirements don't
generally have a cost side worth weighing against.

## 7. Em dashes are banned, and AI-sounding prose is a review target

Added alongside #6, same source.

**Why:** rule 2 of [documentation-standard.md](documentation-standard.md)
requires disclosing LLM involvement. Prose that reads as unreviewed AI
output undercuts that disclosure. It signals the opposite of what the
disclosure is meant to convey, which is that a human is accountable for
what's written.

**What it cost:** every document in this repository had to be rewritten
after the fact. At the time this rule was added, a grep across `docs/` and
`README.md` found 108 em dashes. Writing the standards and then failing them
immediately is embarrassing, and is recorded here rather than quietly
fixed, per [rules-of-engagement.md](rules-of-engagement.md) rule 4.

**What would justify revisiting:** if the em-dash rule turns out to be
theater and the softer style guidance in
[writing-style.md](writing-style.md) does the real work on its own, the hard
rule could be dropped. No evidence either way yet.

## 8. Telegraphic status fragments are a named anti-pattern

Follow-up to #7, flagged by the maintainer against a real example from
another project: a status note compressed into label-fragments and
semicolon-spliced clauses with no subjects, reading like internal shorthand
rather than something a person wrote for another person.

**Why:** dropping this rule into the general "avoid the tells" list in
[writing-style.md](writing-style.md) would have buried it. The maintainer's
example was specific enough, and different enough from the em-dash problem,
to earn its own section with a worked before/after.

**What it cost:** a re-scan of every existing document for the pattern. It
turned out clean; nothing in `docs/` used standalone label-fragments, and
the semicolons already present all join full independent clauses rather
than dropped-subject shorthand, so no rewrite was needed this time. Worth
noting because the em-dash rule (#7) did require a full rewrite and this
one didn't; the two failures aren't equally likely to recur.

**What would justify revisiting:** if this turns out to be the same
underlying problem as #7 (unreviewed first-draft output) rather than a
distinct pattern, the two sections could merge.

## 9. One standard for humans and models, not a model standard with a human exemption

Prompted by the maintainer correcting the framing of
[rules-of-engagement.md](rules-of-engagement.md), which originally read
"written at the model, but they bind the human too."

**Why:** that phrasing put the model first and treated human compliance as
an afterthought, which is backwards from the actual point. The whole
premise of this project is that good practice doesn't change based on who
is typing. A rule that only an AI needs isn't an engineering standard, it's
a leash, and this project isn't building one of those.

**What it cost:** a rewrite of the opening of
[rules-of-engagement.md](rules-of-engagement.md). Small, but worth
recording because the original framing was wrong on a point the whole
project depends on, not a style nit.

**What would justify revisiting:** if a genuinely AI-specific rule turns up
that has no human equivalent (something about context windows or session
boundaries, say), it still belongs in this document, but should be marked
as such rather than implied to be universal when it isn't.

## 10. conformIT is exempt from part of its own required-file list

Prompted by the `novak` audit (novak PR #29, the first external application
of this standard), which ran `documentation-standard.md`'s required-file
list against this repo and found `CLAUDE.md`, `CHANGELOG.md`,
`docs/architecture.md`, `docs/security.md`, and `docs/credits.md` all
absent. The audit's own text flagged this as something needing a decision
rather than a silent gap, which is the right instinct: an unrecorded
divergence from your own rule is exactly the kind of thing
[documentation-standard.md](documentation-standard.md) exists to prevent.

**Chosen:** `docs/architecture.md`, `docs/security.md`, and
`docs/credits.md` do not apply here and are not planned. `CLAUDE.md` and
`CHANGELOG.md` do apply and are open gaps, tracked in
[STATE.md](STATE.md), not exemptions.

**Why:** the first three assume a system with running components, trust
boundaries, and dependencies to declare. This repo is prose plus two git
hooks. `architecture.md` would describe two files calling each other.
`security.md` would restate `security-posture.md` with no project-specific
instance to add. `credits.md` would be a near-empty table, since the whole
point of the survey method (decision-in-progress, see the provenance
section of the README) is that the standards are derived from patterns
already observed, not built on adopted dependencies. `CLAUDE.md` and
`CHANGELOG.md` have no such argument: this repo has AI-assisted commits
that would benefit from a working agreement, and it has released versions
worth a changelog once tagging starts.

**What it cost:** the required-file list in `documentation-standard.md`
now reads as universal when three of its nine entries are conditional. That
was already implicit for `CONTRIBUTING.md` and `VISION.md`, which the same
document already marks as conditional; this makes explicit that
"required" was never meant to be read as "every file, every repo."

**What would justify revisiting:** if conformIT ever adopts a real
dependency (a linter, a CI action, a package this repo requires rather
than one it's documenting), `docs/credits.md` becomes real and this
decision narrows to cover only `architecture.md` and `security.md`.

## 11. The commit-msg hook's non-imperative check was missing two of three shapes

Found by diffing an adopting project's independently-extended fork of this
same hook against the template it started from (novak PR #29 and #30),
rather than by anyone auditing the template directly.

**What was wrong:** the template only matched past tense ("added") and
gerunds ("adding"), and only for five verbs. Third-person present forms
("adds," "fixes," "removes," "creates") passed silently, because they were
never in the list at all. novak's own hook, forked from an earlier version
of this template, already had the third-person forms; the audit in PR #29
found the template lacked the capitalisation and gerund checks novak's
hook had gained since, and in porting those back (PR #30) surfaced that
the direction ran both ways: novak's fork was ahead on third-person forms
before this project ever asked about them.

**Chosen:** extended the word list to cover all three shapes, plus two
verbs (`create`, `refactor`) that weren't in either version but are common
enough to matter, since `refactor` is also a commit type and easy to type
as the description's first word by habit.

**Why a bug like this survived:** the hook was tested against a
regression matrix at the time it was written (11 cases, later 14), and
every case passed. None of the cases exercised third-person present tense,
because the person writing the tests was also the person who wrote the
word list, and both omissions were the same blind spot. An external
fork that grew independently didn't share it.

**What it cost:** nothing to fix. The finding itself is the interesting
part: a hardcoded word list is the kind of check that looks complete when
you write it and stays that way until an independent implementation shows
you what it missed. Worth remembering the next time this hook's list
looks finished.

**What would justify revisiting:** if the word list keeps growing verb by
verb, it may be worth switching to a general "does this look like a
third-person-singular or gerund verb" pattern instead of an enumerated
list, at the cost of more false positives on words that happen to end in
"s" or "ing" without being verbs at all.

## 12. A recurring, centralized audit, scoped to a declared list of public repos

The maintainer asked for a recurring GitHub Actions audit of the projects
adopting this standard, with a readable pass/fail report. This resolves
part of the open question in STATE.md about whether conformIT installs
into projects or stays a reference: for auditing specifically, the answer
is reference. Nothing is installed into any target; conformIT clones each
one fresh, checks it from outside, and throws the clone away.

**Chosen:**

- A declared list (`registry/targets.yaml`), not auto-discovery of
  everything under an account. Auto-discovery would need to guess which
  repos are actually meant to follow this standard and would silently
  change scope every time a new repo appeared.
- Public repos only. A private target needs a deploy key or a PAT with
  read access, which this workflow doesn't have and doesn't ask for. Not
  a technical limit, a deliberate one: adding cross-repo credentials to a
  scheduled workflow is a real security-posture decision on its own
  (rule 4, identity and scope), not a side effect of wanting a report.
- Output goes to the GitHub Actions job summary only. No commit, no
  issue. Chosen over both alternatives specifically because the
  maintainer flagged wanting the report to exclude anything private or
  secret; a job summary that's regenerated every run and never persisted
  to git or to an issue thread is the smallest surface for something to
  leak into by accident. The checks themselves only ever print filenames,
  line numbers, and short labels, never file contents, for the same
  reason: some of what's audited is a repository this project doesn't
  own, and the report about it is more public than the repository itself
  needs to be aware of.
- The job always exits successfully, regardless of findings. This is a
  report, not a gate, consistent with decision #2 (audit reports, never
  rewrites, never blocks). A red status badge would invite treating a
  finding as a build failure to fix under pressure rather than a fact to
  read.
- `scripts/conform.sh audit` does triple duty: a local path, an
  `owner/repo` shorthand (clones it), or `--all` (reads the registry).
  One command and one check implementation
  (`scripts/lib/audit-checks.sh`) for all three, rather than a separate
  CI-only script duplicating the same logic, which is the same
  reuse-before-you-add argument as rules-of-engagement rule 7 applied to
  this project's own tooling.

**What it cost:**

- The em-dash scan in `scripts/lib/audit-checks.sh` duplicates the
  fence/inline-code/allow-marker exclusion logic already in
  `templates/.githooks/pre-commit`, rather than sharing it. Deliberate:
  the pre-commit hook is meant to be dropped into a repo as one
  self-contained file, and the audit runs from conformIT's own checkout
  against a clone it doesn't control, so neither side can assume the
  other's files are present to source from. The two copies must be kept
  in sync by hand, which is a real, ongoing cost, and was already
  visible during testing: the check briefly leaked full CI temp-directory
  paths into its own report until caught and fixed in the same session
  (see the file-path handling in `_conformit_scan_em_dash`'s caller).
- The README status and LLM-disclosure checks are regex heuristics, not
  a real reading of the text. Run against the five real targets during
  development, `almadon/novak-konzol` and `almadon/consigliere` both
  failed the LLM-disclosure check although both are AI-assisted projects;
  whether that's the standard correctly catching an undisclosed project
  or the heuristic missing phrasing it should have caught wasn't
  distinguished, and reading the actual READMEs is the only way to tell.
  Treat a FAIL from these two checks as "go look," not as a
  confirmed violation.
- `actions/checkout@v4` in the workflow is a floating major-version tag,
  which is exactly what security-posture rule 8 argues against. Marked
  `VERIFY` in the workflow file rather than pinned to a commit SHA,
  because this session had no way to confirm a current, correct SHA
  without network access, and a wrong guessed SHA would be worse than an
  honest floating tag with the gap flagged.
- The commit-style check counts conformance over the last 50 commits,
  which penalizes a repo for history that predates this standard
  entirely. `flashctrl/flashDK` scored 14/40 in testing for exactly this
  reason: it's a real, working project with its own prior convention,
  not evidence it's failing to adopt anything. The report doesn't
  distinguish "never adopted this" from "adopted it recently, older
  history remains," and can't from the outside.

**What would justify revisiting:** a private repo needing coverage (would
need the deploy-key question answered directly, not defaulted around);
the heuristic false-fail rate turning out high enough that the two
disclosure checks do more harm than good as an automated signal, in which
case they'd become documentation-only guidance rather than a checked item.
