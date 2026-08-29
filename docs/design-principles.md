# Design principles

Structural defaults. Each is a default, not a law. Departing from one is
fine, and goes in `docs/decisions.md` with the reason.

## 1. Build a services layer, not an app

State, knowledge, and capability live in standalone services that any
client can consume. The frontend is a client, not the system.

The test: **if the UI disappeared tomorrow, is anything of value lost?** If
yes, too much lives in the frontend.

**Cost:** more moving parts than a monolith, and more integration surface.

## 2. Declare, apply, and separately check for drift

Three distinct operations, and the third is the one people skip:

- **Declare.** Desired state lives in git. Git is the source of truth;
  nothing is applied by hand.
- **Apply.** A reconciler moves reality toward the declaration, on a
  schedule, without anyone running a command.
- **Check.** An independent read of what is actually true, which can
  disagree with both.

Applying without checking gives you confidence proportional to your
optimism. From `kuzka/VISION.md`, where this is the stated core discipline.

**Cost:** a reconciliation loop to build and a schedule to maintain. Worth
it the first time a host silently stops converging.

## 3. Prefer native capability over a wrapper you maintain

If a service speaks the protocol natively, use that rather than wrapping
it. Every adapter is code you own, debug, and keep current.

Adopting a backend with native support let `novak` delete ~400 lines of
first-party shim. The bar for a replacement rose at the same time: it must
preserve the property the shim existed to enforce.

**Cost:** you inherit the upstream's choices, including its bugs and its
release cadence.

## 4. Keep the interesting decision in one obvious file

Every piece of editable content has exactly one home, and it's findable
without reading the codebase. `anjunatree/CONTRIBUTING.md` carries a full
table mapping "to change X, edit Y," including the non-obvious ones (the
brand geometry lives in `brandGeometry.ts` and is shared with the icon
rasteriser, so it's edited there and not in the component).

The test: can a newcomer change a label without reading the app?

**Cost:** the table has to be maintained, and a stale one is worse than
none.

## 5. Choose replaceable, and record the bar for replacement

Every adopted component gets a stated criterion for what would justify
swapping it. This turns "we use X" into "we use X because of property P,"
which is a claim a successor can evaluate.

**Cost:** more thinking up front than picking the popular option.

## 6. Say what you are not building

Every project states what's deliberately out of scope. Both `kuzka` and
`novak` do this, and `kuzka/VISION.md` goes further with "open threads,
tracked so they don't get re-derived."

An unrecorded "no" is indistinguishable from an oversight, and gets
proposed again every few months.

**Cost:** none. This is the highest-return paragraph in any design doc.

## 7. Justify building over adopting, in writing

Both source projects carry a section along the lines of "what sets this
apart from adopting something off the shelf." If that section is hard to
write, that's the finding: adopt the off-the-shelf thing instead.

**Cost:** occasionally discovering you shouldn't have started.

## 8. Uniformity cannot be a per-client setting

If a property must hold across every consumer, enforce it at a layer they
all pass through, rather than configuring each one identically and hoping.

The general failure: a setting applied in four clients is a setting that's
wrong in one of them within a month. From `novak/docs/decisions.md` #21.

**Cost:** a shared layer is a shared point of failure.

## 9. Single-homed by construction until proven otherwise

Don't build for multi-node, multi-region, or high availability before a
second node exists. Do leave an obvious place for it to go.

`snapjudgement/README.md` models this exactly. The "replicated" bucket is
documented and currently empty, existing "so future genuinely-multi-node
services have an obvious place to go instead of defaulting into the pinned
pattern."

The specific anti-pattern it names is worth generalising: never route
traffic through an intermediary just because that intermediary happens to
already be public-facing. That hairpin is a bug, not an architecture.

**Cost:** a real migration when the second node arrives. Cheaper than
maintaining unused generality.

## 10. Accessibility and correctness gates are automated or they're opinions

Where a design property can be checked by a script, it's checked by a
script, and the result is recorded next to the thing it validates.

`anjunatree` gates every theme change on a palette validator: lightness
band, chroma floor, colour-blind separation, contrast against the surface.
It records the passing results at the top of `src/themes.ts`. A colour
change that skips the validator doesn't ship.

## 11. Default to portable, narrow deliberately

A project defaults to working across ecosystems, environments, and
operating systems. Not because every project needs to run everywhere,
but because narrowing later costs a rewrite and narrowing now is a
choice, stated, not an assumption nobody decided on purpose. Don't
hardcode something that only holds on one platform (a shell that only
exists on one OS, an org name, a specific CI runner) unless the project
is genuinely scoped to one deployment, in which case say so, in
`docs/decisions.md`, the same as any other departure from a default.

This is a different axis from rule 9's "single-homed until proven
otherwise." Rule 9 is about not building operational scale (multi-node,
high availability) before you need it. This rule is about not building
in assumptions that make later portability cost a rewrite instead of a
parameter. The two coexist: stay single-homed operationally, and still
don't hardcode "us specifically" into code that would need to change
even if a second node, or a second adopter, never shows up.

Two examples already lived, not hypothetical: this project's own
scripts and hooks target bash 3.2 (macOS system bash) rather than
whatever the maintainer's own machine happens to run, at the cost of a
few idioms (no associative arrays, no `mapfile`) and the benefit of
every hook working identically on macOS and on a Linux CI runner with
nobody noticing a difference. And `docs/decisions.md` #17's reusable
workflow, built with every functional value as an input instead of
hardcoded to one org, which turned a fork-portability request three
sessions later into a five-line fix instead of a redesign; see that
decision's own addendum for the payoff stated plainly.

**Cost:** genuinely more thought at design time, for a payoff that
might never be needed. Not every project should pay it. A one-off
deployment script for one specific server is fine hardcoding that
server; the departure is the point, not a lapse, as long as it's
written down.

**Cost:** writing the validator, and occasionally losing a colour you
liked.
