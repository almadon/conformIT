# Writing style

Documentation is written like a technical person wrote it, not like an AI
chat response got pasted into a markdown file. This matters for its own
sake, and it matters more here specifically because
[documentation-standard.md](documentation-standard.md) requires disclosing
LLM involvement. A reader who's told the project used AI assistance and then
reads prose full of AI writing tics will trust the disclosure less, not
more, because the writing itself will look unreviewed.

## No em dashes

Use a comma, a period, a colon, or parentheses instead. An em dash is almost
always standing in for one of those, and picking the right one is part of
writing the sentence, not a cosmetic swap.

Before: "The reconciler applies state on a schedule — nobody runs it by
hand."

After: "The reconciler applies state on a schedule. Nobody runs it by hand."

This is a hard rule, not a preference, because it's mechanically checkable:

```bash
grep -rn "—" docs/ README.md
```

Run that before a commit that touches documentation. It should return
nothing.

## Avoid the tells

None of these make a sentence wrong. They make it read like it was
generated rather than written, which undercuts the disclosure this standard
asks for.

- **The "it's not just X, it's Y" construction.** Say what it is. If the
  contrast matters, state both sides plainly and move on.
- **Rule-of-three lists used as a rhetorical device**, especially when the
  three items are near-synonyms padded out to sound thorough. Use a list
  when there are actually three things, not when one point wants extra
  weight.
- **Throat-clearing openers**: "It's worth noting that," "It's important to
  understand," "Let's dive into." Just say the thing.
- **Hedge-then-assert pairs**: "While X has some merit, ultimately Y."
  State the position.
- **Overuse of bold for emphasis rather than for the one load-bearing
  sentence.** If every other line is bold, none of them are.
- **Words that showed up in every AI-generated document in 2024 and 2025**:
  delve, leverage (as a verb), robust, seamless, holistic, furthermore,
  moreover, in today's fast-paced, unlock, elevate, foster, tapestry. None
  of these are banned outright. All of them are worth a second look when
  they appear.
- **Excessive scare quotes or italics for words that don't need them.**

## Write the way you'd explain it out loud

A useful test: read the sentence aloud. If nobody talks like that, rewrite
it. Technical writing can still sound like a person who knows the subject
explaining it to someone who doesn't, rather than a document performing
authority.

Contractions are fine. Starting a sentence with "and" or "but" is fine.
Varying sentence length is good; a paragraph of uniform medium-length
sentences is itself a tell.

## This is enforced, not aspirational

`grep -rn "—"` is part of what a review checks before merging documentation.
The rest of this file is judgment, not a linter, but the same review pass
applies it: if a paragraph reads like it wasn't reviewed by a person, it
gets rewritten until it does.
