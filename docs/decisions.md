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
- ~~`actions/checkout@v4` in the workflow is a floating major-version
  tag, marked `VERIFY` because this session had no way to confirm a
  current, correct SHA without network access.~~ **Resolved the same
  day, in the session that added decision #13**: that claim was wrong,
  not just cautious. This environment does have network access; the
  real commit was confirmed with `gh api repos/actions/checkout/git/refs/tags/v4`
  and pinned. Kept here rather than deleted, per
  [rules-of-engagement.md](rules-of-engagement.md) rule 4, since a wrong
  assumption about tool access is worth not repeating on the next one.
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

## 13. Sensitive-content scanning, with one deliberate exception to report-only

The maintainer asked for the audit to flag leaked secrets, personal email
addresses (excluding git-author ones), and private-service URLs, and to
warn collaborators/org members to rotate anything found.

**Chosen:**

- **Secrets**: [gitleaks](https://github.com/gitleaks/gitleaks) (MIT) when
  it's on `PATH`, since a maintained rule set beats hand-rolled regex for
  something this consequential; a heuristic fallback (well-known key
  formats only: AWS access keys, PEM private-key headers, GitHub/Slack/
  Google/Stripe token prefixes) when it isn't, reported as reduced
  coverage rather than presented as equivalent. CI installs a pinned,
  checksum-verified copy; see `docs/credits.md`, created by this decision.
- **Emails**: every tracked file scanned for email-shaped strings; an
  address already in this repo's own git author/committer history is
  exempted (already public by the nature of a public git repo, per the
  maintainer's own framing), as are `noreply@` addresses and RFC 2606
  example domains.
- **Private URLs**: RFC 1918 ranges and common internal-DNS suffixes
  (`.internal`, `.corp`, `.lan`, `.ts.net`), excluding loopback addresses
  and the RFC 5737 documentation ranges, both of which are expected in
  ordinary docs and not a leak.
- **A new severity tier, CRIT**, used only for secrets. PASS/WARN/FAIL
  from decision #12 all stay report-only; a CRIT finding makes
  `scripts/conform.sh audit` exit 2, and makes the scheduled workflow
  job itself fail, breaking the "always green" rule #12 established.
  Deliberate: a red status badge on a scheduled run is one of the only
  mechanisms this design has for demanding attention beyond the summary
  text, and a live credential is exactly the class of finding worth
  interrupting someone for. Emails and private URLs stay at FAIL, not
  CRIT: real disclosure risks, but not ones with an active "rotate now"
  response the way a credential has.
- The rotate-and-notify instruction is in the report text itself, not
  just in this document: any CRIT finding prints "rotate it immediately
  and notify every collaborator or org member with access," inline,
  since that's the whole point of flagging it at all.
- Scans the whole tracked tree (`git ls-files`), not just `docs/` and
  `README.md` the way the em-dash check does. A leaked key is at least as
  likely in source or config as in prose.

**What it cost:**

- Only the current working tree is scanned, not git history. A secret
  removed from HEAD in a later commit but still present in an earlier
  one is a real, separate risk this doesn't catch, and can't from a
  shallow `--depth 50` clone even if it tried. Worth stating plainly
  rather than implying broader coverage than exists: if HEAD is clean,
  that is not the same claim as "this repo has never leaked anything."
- `docs/decisions.md` #10 exempted `docs/credits.md` for this repo on the
  premise that conformIT adopts no real dependencies. gitleaks is now
  one, which is exactly the condition #10 named as ending the exemption.
  `docs/credits.md` now exists, narrowing #10 to `docs/architecture.md`
  and `docs/security.md` only, precisely as #10 predicted.
- The gitleaks install step in the workflow is a second pinned external
  artifact (the first being `actions/checkout`), each a maintenance
  surface: both need re-verification on any future version bump, by
  someone who can actually download and checksum the new release, not by
  editing the pinned values on trust.
- Local runs of `scripts/conform.sh audit` never install anything onto
  the operator's own machine, including gitleaks: silently downloading
  and running a new binary on a user's Mac as a side effect of an audit
  command crosses a line CI installing it into an ephemeral, throwaway
  runner does not. This means local audits without gitleaks pre-installed
  get the weaker heuristic path, asymmetric with what CI sees for the
  same repo.
- All three checks are heuristic to some degree, email and URL detection
  entirely so. A regex match is not a semantic read; treat a FAIL as
  "go look," and a clean scan as "nothing obvious found," never as a
  compliance certificate. Stated directly in security-posture.md rule 9,
  which this decision also added.
- **Confirmed, not hypothetical**: running this against
  `flashctrl/flashDK` flagged `10.0.10.21` in an example file's doc
  comment as a private address. Checked the actual source: it's a
  placeholder LAN IP in a usage example telling a user to point the demo
  at their own device, not a disclosed real address. The private-URL
  check has no way to tell "example IP a reader is meant to replace"
  apart from "an address that describes real infrastructure," and this
  is exactly the false-positive shape that gap produces. Left as a FAIL
  rather than special-cased, since narrowing the pattern to dodge this
  one case risks missing a real one shaped the same way; noted here so a
  human reads the hit rather than trusting the label.
- **A related, narrower false positive was fixed, not just documented**:
  this same check flagged its own bullet point above, since
  `docs/decisions.md` quotes `10.0.10.21` inside a discussion of the
  finding. The email, private-URL, and secret-heuristic scanners never
  had the fenced-code/inline-code/allow-marker exclusions
  `_conformit_scan_em_dash` already had, so any markdown file legitimately
  illustrating a pattern always tripped its own check. Fixed by adding
  `_conformit_prose_or_raw`, the same exclusion logic applied to a shared
  helper the three scanners now pipe through, for `.md` files only. This
  does not, and isn't meant to, help the flashDK case above: that hit is
  in a `.rs` doc comment, and there's no "this is just an example"
  convention in source code the way there is in prose for this check to
  key off. Found and fixed in the same session as the rest of this
  decision, before anything was committed, by running the tool against
  its own output rather than by inspection, the same way the two bugs
  during initial testing (the trap and the leaked temp path, both
  documented in the commit history around decision #12) were found.

**What would justify revisiting:** a real false-positive or false-negative
rate observed from actual use, once the workflow has run enough times to
have one, and the flashDK example above is already one data point toward
that; a private repo needing this coverage, which would need the
gitleaks-install-locally question answered on purpose rather than
avoided; git-history scanning, if working-tree-only coverage turns out to
miss findings people actually cared about.

## 14. A copyable README scaffold, not just a described structure

The maintainer asked for standardized scaffolding for a repo's README
content and style: name, description, function, use case(s), development
status with a no-warranty disclaimer, LLM disclosure.

**Chosen:** [`templates/docs/README.md`](../templates/docs/README.md), a
fill-in-the-blank file with bracketed placeholders and inline instructions,
rather than only describing the structure in prose. `documentation-
standard.md` gained a new "What a README opens with" section (name,
one-line description, function, use cases) ahead of the existing
disclosure section, which itself gained a warranty-disclaimer requirement
alongside status and LLM use. The audit gained one more heuristic check:
a use-case section heading, at WARN rather than FAIL, since detecting a
genuinely good one-line description mechanically isn't reliable enough to
fail a repo over.

**Why a template file, not just prose:** [design-principles.md](design-principles.md)
rule 4 argues for keeping the interesting decision in one obvious, copyable
place rather than a description someone reconstructs each time. A prose
description of a README's shape is exactly the kind of thing that drifts
in the retelling; a file with placeholders doesn't.

**What it cost:** the name/description/function/use-case requirements
aren't checked as rigorously as status/warranty/LLM-use, since "is this a
good description" isn't something a regex can judge. Presence of a use-
case heading is checked; the quality of what's under it isn't and can't
be, by this kind of tool.

**What would justify revisiting:** if `conform.sh init` gets built, it
should place this file directly rather than leaving it for a human to
copy by hand; until then, copying it manually is the whole mechanism.

## 15. AGENTS.md over CLAUDE.md, and Assisted-by over Co-Authored-By

Prompted by the maintainer asking whether external standards exist for
AI-assisted work, and then asking to adopt two of the findings.

**Chosen, part one:** `AGENTS.md` is the required agent-instructions
file (`documentation-standard.md`'s table), not `CLAUDE.md`. `CLAUDE.md`
becomes a one-line `@AGENTS.md` import, Anthropic's own documented
pattern, per `templates/AGENTS.md` and `templates/CLAUDE.md`.

**Why:** [AGENTS.md](https://agents.md) is a real, converged, tool-
agnostic standard: over 60,000 adopting projects, 30+ supporting agents,
stewarded by the Linux Foundation's Agentic AI Foundation since December
2025. Writing a Claude-specific file as this project's required standard
would mean every other agent (Codex, Copilot, Cursor, Gemini CLI, Aider)
reads nothing, which contradicts decision #9's whole point: one standard
for whoever does the work, not a standard for one vendor's tool. Claude
Code itself doesn't read `AGENTS.md` natively as of this writing
([anthropics/claude-code#6235](https://github.com/anthropics/claude-code/issues/6235)),
so a bare `AGENTS.md` alone would leave Claude Code sessions in this
repo without it; the one-line `CLAUDE.md` import closes that gap without
maintaining two copies of the same content.

**What it cost:** every prior reference to `CLAUDE.md` as the required
file, across `documentation-standard.md`, the audit checker, `STATE.md`,
and `README.md`, needed updating in the same change; a partial rename
would have left the standard internally inconsistent, exactly the
failure mode decision #12's "credits.md never got its footnote" already
demonstrated once. The audit gained one more check: a `CLAUDE.md` with
real content and no sibling `AGENTS.md` is flagged, since that's the
most likely way a Claude Code user misses this convention entirely
(Claude Code works fine reading `CLAUDE.md` directly, so nothing forces
the tool-agnostic file into existence on its own).

**Chosen, part two:** AI-authored commits carry `Assisted-by:
AGENT_NAME:MODEL_VERSION`, not `Co-Authored-By:`. Full format and
reasoning in
[commit-and-history.md](commit-and-history.md#ai-authorship).

**Why:** the [Linux kernel's own documentation](https://docs.kernel.org/process/coding-assistants.html)
specifies this format, and Fedora, Rocky Linux, OpenTelemetry, the
Apache Software Foundation, LLVM, and QEMU have converged on the same or
a near-identical trailer independently. `Co-Authored-By:` is GitHub's
convention for a human collaborator; using it for a tool blurs a
distinction that matters most exactly where it's blurred, which is
provenance and DCO certification. Converging on the same trailer other
projects use is also what makes `git log --grep '^Assisted-by:'`
meaningful across projects, not just within one.

**What it cost:** every commit in this project's own history before this
decision used `Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>`.
Not rewritten; rewriting history for a trailer format isn't worth the
disruption, and decision #2's own argument against retroactive migration
applies here too. Commits from this point forward carry both trailers in
this specific repository, not by choice: the Claude Code harness this
project has been built with requires a `Co-Authored-By:` trailer on
every commit it makes, a constraint on the tool, not a project decision.
`Assisted-by:` is added alongside it, and a project not built inside a
harness with that requirement should use only `Assisted-by:`, per
`commit-and-history.md`.

**What would justify revisiting:** if `AGENTS.md` loses adoption to a
successor the way `.cursorrules` and other tool-specific files have
already been superseded by `AGENTS.md` itself; if a coding-agent harness
starts requiring its own conflicting trailer the way this project's
current one requires `Co-Authored-By:`, in which case the "both
trailers" accommodation would need to generalize past a single special
case.

## 16. A private reporting repo, split by audience, not just relocated

Prompted by the maintainer asking whether reports should go to a private
"meta" repo instead of conformIT's own public job summary.

**Chosen:** `almadon/conformIT-reporting`, private, gets the full
per-finding detail (one file per target, overwritten each run so its own
git history is the trend record). conformIT's own public job summary
keeps only the summary table: pass/warn/fail/crit counts, no per-finding
samples. `scripts/conform.sh audit --all` gained a `--detail-dir <dir>`
flag to produce this split; without it, behaviour is unchanged (detail
and summary both to stdout, the useful shape for a human running this
locally).

**Why a split, not just a relocation:** moving the exact same combined
report to a private repo would fix exposure for repos in the registry,
but conformIT's own public job summary would stay a place a sample could
leak from, for any future check that isn't as careful as the current
ones. Splitting by audience closes that structurally rather than relying
on every check remembering to redact.

**Found while building this, fixed in the same change:** the email
check was the one place that hadn't learned this lesson yet. It printed
the actual discovered address as its "sample," unlike the secrets check
(file:line:rule, never the matched value) and the private-URL check
(file:line only). Fixed to match: redacted to file:line, regardless of
which report it ends up in. This was a live gap in the *public* job
summary this whole time, not a hypothetical one the private repo
happened to also fix.

**The credential:** a fine-grained GitHub PAT, scoped to
`almadon/conformIT-reporting` only, `contents: write`, nothing else,
stored as `CONFORMIT_REPORTING_TOKEN` in conformIT's repo secrets. The
maintainer is adding this themselves rather than it being minted by an
agent session; the publish step checks for it (via a job-level env var,
since [GitHub's own docs](https://docs.github.com/actions/security-guides/using-secrets-in-github-actions)
confirm secrets can't be referenced directly in a step's `if:`, caught
by checking the docs rather than assumed) and is skipped, not failed,
until it exists.

**What it cost:** a second credentialed surface (the first being the
gitleaks download in decision #13), reviewed against
[security-posture.md](security-posture.md) rule 2: one credential, this
integration only, write access to nothing but this one repo. The
reporting repo itself has none of conformIT's own required-file set
(`AGENTS.md`, `docs/decisions.md`, and so on): it's entirely machine-
written output with no human-authored content to speak to, the same
"data, not documentation" exemption `documentation-standard.md` already
gives `prompts/`/`registry/`-shaped content, applied to a whole repo
instead of a directory within one. Its own README says so, so a visitor
doesn't wonder why it doesn't follow conformIT's own rules.

**Verified the same day, once the credential existed**: triggered the
workflow by hand (`gh workflow run`) rather than waiting for Monday. Full
green run including the publish step; `almadon/conformIT-reporting` got
a real commit with all six report files and a correctly regenerated
README index; the secrets check used the real `gitleaks` engine in CI,
not the local heuristic fallback, confirming the pinned install works on
GitHub's actual infrastructure and not just in a local reproduction; the
`HAVE_REPORTING_TOKEN` job-level env var evaluated to `true` in the job
logs, confirming the fix made after catching the wrong `if: secrets.X`
draft against GitHub's own docs. Before this, verified: the
`--detail-dir` split's content shapes, tested against all six live
targets; the redacted email check, against a synthetic fixture; the
reporting repo's own initial commit and push, done by hand rather than
through the workflow.

One non-blocking finding from the real run's own annotations: GitHub
flagged the pinned `actions/checkout` SHA as targeting the deprecated
Node 20 runtime, auto-forced onto Node 24 as a compatibility shim for
now. Nothing failed. A version bump is coming due at some point; not
done here, since it's a separate, deliberate pin update per rule 8, not
a side effect of confirming this feature works.

**Found by running conformIT's own audit against its own working tree
right after writing the new workflow step, fixed in the same change**:
the email check flagged `actions@users.noreply.github.com`, the bot
identity this same workflow step sets for its own commits, since the
existing `noreply@*` exclusion only matched a literal prefix and GitHub's
own noreply convention puts the marker in the domain
(`*@users.noreply.github.com`), not the local part. Fixed by adding
`*@*.noreply.github.com` to the exclusion list. Worth noting because it's
the second time in one feature that a check flagged conformIT's own
output back at itself (the first was decisions.md quoting its own
example IP, in decision #13). Dogfooding immediately keeps finding
these, which is the argument for continuing to do it rather than
trusting a check because it looks reasonable on paper.

**What would justify revisiting:** if `--detail-dir`'s output ever needs
to differ from the plain stdout shape beyond "same content, different
destination," at which point a single shared code path stops being the
right design.
