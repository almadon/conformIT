# Visual style

What a project's README and docs look like: the graphic at the top, the
colours, and how a diagram is drawn. The aim is that someone who has seen
one conforming project recognises the next one, and that none of it looks
like it was generated in a hurry.

This covers the README and the docs. It does not prescribe an app's own
interface. See "Interfaces" at the end.

## The graphic at the top

Every README opens, just under the status block, with one picture: a logo,
a screenshot, or a diagram of the whole thing. A diagram is the right
default for a service or a framework, a screenshot for something with a
screen, a logo for a small tool where neither would say more than the name.

- Centre it with the `<p align="center">` block in
  [`templates/docs/README.md`](../templates/docs/README.md), give it a
  `width` so it does not stretch, and write real `alt` text: one sentence
  that tells someone who cannot see it what it shows.
- Prefer SVG, kept in `docs/images/` (`architecture.svg` when it is an
  architecture diagram, which Novak and Consigliere both use, or `overview.svg`).
  Theme it with CSS variables and a `prefers-color-scheme: dark` block, as
  described under Diagrams below. It stays sharp, diffs as text, and can
  follow light and dark mode. A screenshot is a PNG, and it should be
  cropped to the part that matters.
- One picture at the top. A second belongs next to the section it explains.
- **Where the README is rendered outside GitHub, use an absolute URL.**
  HACS, package indexes and some mirrors show the README without the
  repository's files, so `docs/images/overview.svg` breaks there. Point the
  image at `https://raw.githubusercontent.com/OWNER/REPO/main/docs/images/overview.svg`
  instead. The ha-propsense session reports doing this for a Home Assistant
  integration; that HACS renders it is VERIFY, as is whether an SVG with
  CSS variables keeps its dark mode when served that way. If it does not,
  ship a PNG for those projects.

## Diagrams

Hand-written inline SVG, in the style of Consigliere's `docs/images/layers.svg`
(the reference), starting from
[`templates/docs/images/overview.svg`](../templates/docs/images/overview.svg).

- **Layers read top to bottom**, one coloured band each, numbered, with a
  short name and one line on what the layer is for. Parts of a layer are
  white cards inside its band, with a bold name and a quieter line under it.
- **Colour means something and stays the same across projects.** Blue is
  declaring or inputs, green is acting or running, purple is configuring,
  amber is a boundary or a warning, teal is a network or transport, red is
  something that can hurt (secrets, destructive steps). A diagram uses only
  the families it needs.
- **Each family is a pair:** a pale fill and a stronger stroke, defined as
  CSS variables at the top of the file, with a second set for dark mode
  inside `@media (prefers-color-scheme: dark)`. Never hard-code a colour in
  a shape.
- **Palette** (light, then dark), as fill and stroke:

  | Family | Light | Dark |
  |---|---|---|
  | blue | `#e8f0fd` / `#2f6fdb` | `#15233b` / `#6aa2ff` |
  | green | `#e6f5ec` / `#1f8a4c` | `#12291d` / `#4cc27f` |
  | purple | `#f1eafb` / `#7a45c9` | `#231a37` / `#b18cf0` |
  | amber | `#fdf1e0` / `#c27410` | `#33250f` / `#f0a947` |
  | teal | `#e3f4f6` / `#16808f` | `#10292e` / `#4dc1d1` |
  | red | `#fbe9ec` / `#c8374f` | `#35161c` / `#ff7a8e` |

  Text is `#16202b` on light and `#e6edf5` on dark; quiet text is `#566474`
  and `#98a6b6`. The font is the system stack, so nothing is downloaded.
- **Rounded corners** (12px bands, 8px cards), 1.5px band strokes, a viewBox
  near 960 wide so it scales evenly in a README.
- **Accessible:** `role="img"` on the `svg`, a `<title>` and a `<desc>` that
  describe the picture, and no meaning carried by colour alone: the layer
  names and numbers say it too.
- **Check it rendered.** Open the SVG in a browser in light and dark, or on
  macOS run `qlmanage -t -s 900 -o . file.svg` for a quick thumbnail (the
  Consigliere session recommends it; I rendered mine in the browser pane
  instead and have not run `qlmanage`, so that is VERIFY). A diagram that
  was never looked at is the usual way a clipped label ships.
- **Keep it to what a reader needs.** If a diagram needs a legend and a
  paragraph to decode, it is two diagrams.

Mermaid is fine for a quick sequence or flow inside `docs/`, where GitHub
renders it. It is not the README graphic: it follows the viewer's theme
rather than this palette, and it cannot do the layered look.

## Tables and callouts

Use a table when a thing has several attributes (options, hosts, files),
not as a way to make a list look serious. Put the status, warranty and LLM
statement in a blockquote under the title, as the template does. Use bold
for the one phrase a skimmer needs, sparingly.

## Prose

Write like a person explaining it to a colleague: see
[writing-style.md](writing-style.md). No em dashes (the audit checks), no
fragments standing in for sentences, no list where a sentence would do.

## Interfaces

A project with its own UI is held to the same instincts: clear hierarchy,
the same light-and-dark behaviour, nothing decorative that does not help.
What follows is how Consigliere's Cmdr interface works, written down so
another project can copy it. It comes from the Consigliere session's notes,
not from my having used Cmdr, so treat it as a worked example, not a
mandate. Where it differs from the diagram palette above, the interface
wins for the interface: the six-family palette is for documentation
diagrams, and a product UI picks one accent.

**The idea.** One screen answers three questions: what do I have, is it
healthy, and where do I click. It never shows something it cannot act on and
never hides a problem behind decoration.

**Page order, the same every time.** A sticky header (name, a search or
command box, refresh, theme, who is signed in). A strip of four status
tiles. A "Needs attention" row that exists only when something does. Then
the overview, the launchpad of tools, the main list with filters, and any
secondary tables. A footer saying how fresh the data is. Depth goes in a
drawer over the page, not on separate pages, and a collapsible "How to read
this" sits next to the thing it explains.

**Colour: one accent, three status colours, one muted grey.** Nothing else
carries meaning.

| Role | Dark | Light |
|---|---|---|
| background | `#0a0c11` | `#f3efe6` |
| panel | `#131721` | `#fffdf8` |
| text | `#ece8de` | `#1d1b16` |
| muted | `#8b91a1` | `#6b685d` |
| accent | `#dcb053` | `#9c6d14` |
| ok | `#3fbb7c` | `#16874f` |
| warn | `#ea9440` | `#b86a0c` |
| bad | `#f0605a` | `#c93a33` |
| unknown | `#5d6578` | `#9a9684` |

The light palette is a second design, not an inversion. The rules matter
more than the hex values: status colours mean status and never decorate;
categories get their own fixed colours that are not status colours; a card's
left edge takes its worst status, so a scan down the list finds red without
reading; status is always a dot plus words, never colour alone; the UI
follows the system light or dark setting, with a header override remembered
per browser.

**Contrast, measured here (WCAG, against the panel colour).** Dark: text
14.6, muted 5.7, accent 8.9, ok 7.4, warn 7.5, bad 5.6, unknown 3.1. Light:
text 16.9, muted 5.5, accent 4.5, ok 4.5, warn 4.1, bad 5.0, unknown 2.9.
Against the page background the light figures are lower (accent 4.0, warn
3.6, bad 4.4, unknown 2.6). So the dark palette passes the 4.5 text
threshold except `unknown`, which is only fit for a dot. In the light
palette `unknown` fails even the 3:1 floor for a graphic, and `accent`, `ok`
and `warn` fall just short of 4.5 as small text. The "dot plus words" rule
softens this if the words are set in the text colour, not the status colour,
which should be checked per project. Choose a darker light `unknown` before
copying the palette.

**Type.** Monospace for anything you could type or copy (hostnames,
commands, numbers, tags, small section labels), the system sans for
sentences. Section labels are tiny mono capitals with a `// ` prefix in the
accent. Base size 14px, line height 1.5, status-tile numbers about 30px mono.

**Components.** A status tile has a mono caps label, a big number and one
plain sentence; a red tile is a button that filters the list to the problem.
A card has a heading row, a status line and labelled sections with a narrow
label column, and leaves out empty sections. Tags are pills outlined in
their category colour; something you can open is an underlined link, so
pills never look clickable. A command palette on Ctrl or Cmd plus K, `/` to
filter, Esc to close. Copy buttons that turn into "copied". Skeleton blocks
while loading, not spinners. The page runs nothing on the user's behalf and
says so.

**Words.** See [ui-copy.md](ui-copy.md). One noun per concept, sentence
case, and empty and error states that say what is missing, why, and what to
do next. Cmdr's: "No exposure scan seen in the logs yet. It runs daily from
the scanner host; run it now with `scripts/exposure.sh run`."

**Graphic.** A rounded-square tile (corner radius about a fifth of the
width) holding one monoline mark in an accent gradient, over a soft radial
glow in the accent and faint horizontal lines. Cards use a 14px radius,
chips a full pill, shadows barely there. Charts are inline SVG sparklines in
the accent; no stock illustrations. Logo files live in `almadon/brand`
(not opened).

**Robustness.** No inline scripts or styles, so a strict content security
policy works. Anything the mouse does, the keyboard does, and focus rings use
the accent.

**Not checked.** Phone layout, a screen reader pass, and Firefox and Safari
behaviour were not tested, according to the notes. I did not open the brand
kit, run Cmdr, or confirm the README described below.

## Documentation of a module

Cmdr's README is the worked example: a title and one sentence; the
five-line contract block from
[`templates/docs/ownership.md`](../templates/docs/ownership.md) (Does,
Owns settings, Keeps state, Rolls back by, Exposes), honest where the answer
is "nothing yet"; What it is for, with one scenario; a table of where its
data comes from, with a column for what happens when a source is missing;
the page as a tour in sentences; sign-in; a settings table with defaults; a
table of what it serves, with a needs-sign-in column; and What was tested,
with VERIFY on anything unchecked. Tables for lookups, prose for reasons.

What the old README did that the standard rules out: bullets built from a
bold label and a clipped fragment, a stale status that outlived its truth, a
list that grew feature by feature in build order, and bold on every line so
nothing stands out.

## Forks

A repository that is a fork of someone else's project, kept to carry a
fix, is not restyled. Its README is theirs. Mark it so the audit leaves it
alone: put `<!-- conformit: exempt fork of OWNER/REPO -->` in its README, or
leave it out of the audit registry, which is where conformIT's own list keeps
`ha-homebox`, `memoket-ha`, `openwebui-importer` and `niimprint`. See
decisions.md #28.
