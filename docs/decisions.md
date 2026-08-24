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
