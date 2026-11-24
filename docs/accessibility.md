# Usability and accessibility

For anything with a screen. This is the part of a project's interface that
conformIT does fix. Colours, themes and visual character are the project's
own to choose (see [visual-style.md](visual-style.md), where the palettes are
examples, not rules). What a user can adjust, and the floor everything has to
clear, is the same everywhere, so someone who needs larger text or less
motion finds it in the same place and gets the same result in every project.

The reference is AnjunaTree, a map-based catalog explorer. Its source was
read for this, not run or audited, and where this document goes beyond it
that is said.

## The principle

**Follow the system, let the user override, remember the override.** On
first load a UI honours what the operating system already says (colour
scheme, reduced motion, and where it can, contrast). A setting in the UI
overrides that, and the override is kept on the device. Nobody should have to
find a setting to get what they already asked their computer for, and nobody
should be stuck with the system's choice.

## Options every UI offers

All in one place, called Settings or Accessibility, reachable without
scrolling through the main view.

| Option | What it does | Default |
|---|---|---|
| Text size | Scales all text. AnjunaTree offers four steps: Small (90%), Default, Large (115%), Largest (130%). Layout must survive the largest. | Default |
| High contrast | Raises secondary text to full strength, thickens borders, and adds a non-colour cue wherever colour alone marked a state (AnjunaTree strikes through a switched-off legend chip). | Off |
| Reduce motion | Stops animation and transitions. | The system's `prefers-reduced-motion`, on first load |
| Larger marks | Makes small interactive or data marks bigger, for people who find them hard to see or hit. Applies to anything that is a symbol rather than text. | Off |
| Colour scheme | Light, dark, or follow the system. A project with several named themes (AnjunaTree has four) is fine; each has to pass the checks below. | Follow the system |

**Text size is not optional.** Any UI that shows text offers a text size
control, and builds so that it works: type is sized in relative units (`rem`,
`em`, or a `--font-scale` variable on the root), not fixed pixels, so one
setting scales everything, and the layout is checked at the largest step. This
is separate from the browser's own zoom, which must also keep working: the
page has to stay usable at 200% zoom (WCAG 1.4.4, Resize Text) and reflow
without sideways scrolling at 320 CSS pixels wide (WCAG 1.4.10, Reflow). Never
disable pinch zoom.

Not every project needs every row: a UI with no small marks has no use for
Larger marks. A row that applies and is missing is a gap to record, not to
hide.

## The floor

These hold whatever the theme.

- **Keyboard.** Everything the mouse does, the keyboard does, in a sensible
  order. No keyboard trap.
- **A visible focus ring** on every interactive element, a 2px outline with
  an offset, in a colour that clears 3:1 against its surround.
- **Touch targets** of at least 44 by 44 CSS pixels where a finger is likely.
  AnjunaTree's stylesheet uses 44px for its controls.
- **Colour is never the only carrier of meaning.** A status has a word or a
  shape as well as a colour, a selected item has more than a tint.
- **Contrast is measured, not eyeballed.** Text at 4.5:1 against its
  background (3:1 for large text), and anything that is a graphic or a
  control boundary at 3:1. AnjunaTree checks every theme's data colours
  against that theme's own surface, for lightness band, chroma, separation
  under colour-vision deficiency, and the 3:1 floor, and records the passing
  figures at the top of `src/themes.ts`. That is design principle 10 in
  [design-principles.md](design-principles.md): the checks are run and the
  results sit next to the thing they validate.
- **Text can be resized** without losing content or function, in the page and
  in the UI's own control.
- **Meaningful structure.** Real buttons and links, labels on inputs, ARIA
  where a native element cannot say it, a `lang` on the page, `alt` text on
  images that carry information.
- **Words follow [ui-copy.md](ui-copy.md).** Plain labels, errors that say
  what to do next.

## Test at different viewports

A layout that works on the developer's monitor and breaks on a phone is the
usual way an interface fails the people it was meant for. Every UI is tried at
these sizes, with the text size at Largest and again at 200% browser zoom, in
light and in dark:

| Width | Stands for |
|---|---|
| 320 px | The smallest phone, and the reflow floor |
| 390 px | A current phone, portrait |
| 768 px | A tablet |
| 1280 px | A laptop, which at 200% zoom behaves like 640 px |

At each: nothing is cut off, nothing needs sideways scrolling (a map or a wide
data table may scroll inside its own frame), controls are still 44 px, the
focus ring is visible, and the main task can be completed with the keyboard.
Also a phone in landscape, where height is the scarce thing.

Do it automatically where the project has browser tests: a test file that sets
the viewport (Playwright `setViewportSize`, Cypress `cy.viewport`) and takes
a screenshot or asserts there is no horizontal overflow. Where it does not,
do it by hand and say so under "What a project states". AnjunaTree's session
shows it resizing the preview to a phone width and back while verifying a
change, and its repository has no automated viewport test; both are worth
copying in their own way, the second as the gap to close.

## Themes are free, with conditions

A project may have one theme or twelve, in any palette. The conditions are
the floor above, plus: if a colour carries identity (a category on a map, a
status), the set of colours is checked as a set, because they are on screen
together, and the result is recorded. A new theme does not ship until it has
been through the same check. Cmdr's brass and AnjunaTree's four named themes
look nothing alike and both fit.

## What a project states

In its README or `docs/decisions.md`, one short paragraph: which of the
options above it offers, which it does not and why, and what was actually
tested (a screen reader, a phone, a second browser). "Not tested" is a fine
answer and an honest one; leaving it out reads as having tested.

## Not covered, and not checked

- **System contrast and forced colours.** AnjunaTree's High contrast is a
  toggle. It does not read `prefers-contrast` or `forced-colors` (neither
  string is in its source). Honouring them is a sensible next step and is
  recommended here, not taken from a project that does it.
- **Screen reader behaviour, phone layout, and other browsers** were not
  tested for AnjunaTree as far as its repository shows, and not by me.
- **Contrast.** The audit does not measure it. The useful mechanical piece
  is a validator run against a project's own palette, which AnjunaTree
  already does. Not built.

## What the audit checks

For a repository that has a screen (markup or components, not just
stylesheets), the audit looks in the source for the signs below and warns when
it finds none. It reads text; it cannot test anything, and "not found" means
the check did not see it, not that it is absent.

- a viewport meta tag, and that it does not disable pinch zoom;
- a `lang` on every `<html>`;
- an `alt` on every `<img>` (an empty one is fine for decoration);
- reduced-motion handling wherever there are animations or transitions;
- a visible focus style wherever the default outline is removed;
- a text size control (a font or text scale in the source, or "text size"
  named in the README or docs);
- an automated test that sets a viewport size;
- a statement in the README or docs of which accessibility options are offered
  and what was tested.

The text size and viewport-test checks are keyword searches, so a project that
does the thing under another name can satisfy them by saying so in its
documentation. That is the honest limit of a source scan: it prompts the
question and reads the answer, it does not grade it. Decision #31.
