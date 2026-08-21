# Design principles

Structural defaults. Each is a default, not a law — departing from one is
fine, and goes in `docs/decisions.md` with the reason.

## 1 — Build a services layer, not an app

State, knowledge, and capability live in standalone services that any client
can consume. The frontend is *a* client, not *the* system.

The test: **if the UI disappeared tomorrow, is anything of value lost?** If
yes, too much lives in the frontend.

**Cost:** more moving parts than a monolith, and more integration surface.

## 2 — Declare, apply, and *separately* check for drift

Three distinct operations, and the third is the one people skip:

- **Declare** — desired state in git. Git is the source of truth; nothing is
  applied by hand.
- **Apply** — a reconciler moves reality toward the declaration, on a
  schedule, without anyone running a command.
- **Check** — an independent read of what is actually true, which can
  disagree with both.

Applying without checking gives you confidence proportional to your
optimism. From `kuzka/VISION.md`, where this is the stated core discipline.

**Cost:** a reconciliation loop to build and a schedule to maintain. Worth it
the first time a host silently stops converging.

## 3 — Prefer native capability over a wrapper you maintain

If a service speaks the protocol natively, use that rather than wrapping it.
Every adapter is code you own, debug, and keep current.

Adopting a backend with native support let `novak` delete ~400 lines of
first-party shim. The bar for a replacement rose at the same time: it must
preserve the property the shim existed to enforce.

**Cost:** you inherit the upstream's choices, including its bugs and its
release cadence.

## 4 — Keep the interesting decision in one obvious file

Every piece of editable content has exactly one home, and it's findable
without reading the codebase. `anjunatree/CONTRIBUTING.md` carries a full
table mapping *"to change X, edit Y"* — including the non-obvious ones
(geometry lives in `brandGeometry.ts` and is shared with the icon
rasteriser; edit it there, not in the component).

The test: **can a newcomer change a label without reading the app?**

**Cost:** the table has to be maintained, and a stale one is worse than none.

## 5 — Choose replaceable, and record the bar for replacement

Every adopted component gets a stated criterion for what would justify
swapping it. This turns "we use X" into "we use X because of property P,"
which is a claim a successor can evaluate.

**Cost:** more thinking up front than picking the popular option.

## 6 — Say what you are not building

Every project states what is deliberately out of scope. Both `kuzka` and
`novak` do this, and `kuzka/VISION.md` goes further with *"open threads
(tracked so they don't get re-derived)."*

An unrecorded "no" is indistinguishable from an oversight, and gets proposed
again every few months.

**Cost:** none. This is the highest-return paragraph in any design doc.

## 7 — Justify building over adopting, in writing

Both source projects carry a section named some variant of *"what sets this
apart from adopting something off the shelf."* If that section is hard to
write, that is the finding — adopt the off-the-shelf thing.

**Cost:** occasionally discovering you should not have started.

## 8 — Uniformity cannot be a per-client setting

If a property must hold across every consumer, enforce it at a layer they all
pass through, not by configuring each one identically and hoping.

The general failure: a setting applied in four clients is a setting that is
wrong in one of them within a month. From `novak/docs/decisions.md` #21.

**Cost:** a shared layer is a shared point of failure.

## 9 — Single-homed by construction until proven otherwise

Don't build for multi-node, multi-region, or high availability before a
second node exists. Do leave an obvious place for it to go.

`snapjudgement/README.md` models this exactly: the "replicated" bucket is
documented and currently empty, existing *"so future genuinely-multi-node
services have an obvious place to go instead of defaulting into the pinned
pattern."*

The specific anti-pattern it names is worth generalising: **never route
traffic through an intermediary just because that intermediary is already
public-facing.** That hairpin is a bug, not an architecture.

**Cost:** a real migration when the second node arrives. Cheaper than
maintaining unused generality.

## 10 — Accessibility and correctness gates are automated or they are opinions

Where a design property can be checked by a script, it is checked by a
script, and the result is recorded next to the thing it validates.

`anjunatree` gates every theme change on a palette validator — lightness
band, chroma floor, colour-blind separation, contrast against the surface —
and records the passing results at the top of `src/themes.ts`. A colour
change that skips it does not ship.

**Cost:** writing the validator, and occasionally losing a colour you liked.
