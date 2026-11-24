# UI copy

The words in an interface: labels, buttons, empty states, errors, settings
text. A project with a screen follows this the way its README follows
[writing-style.md](writing-style.md). It is short on purpose.

**Plain words.** Say what a thing is in the words a user would use, not the
ones the code uses. "Paused" beats "dormant". "Waiting for the integration
that provides it" beats "needs the provider". If a technical term is
unavoidable, say it once, with a few words of explanation.

**Say what to do next.** An empty state or an error that only describes a
problem leaves the user stuck. "Nothing here yet" is a description; "No
devices yet. Add one from Settings" is help. An error names what went wrong
in plain terms and what to try, and does not show a stack trace or an
internal code as the message.

**Every error ends with the next step.** Press Refresh, reload the page, read
the container log, ask an admin for a group. Do not show a raw exception name
to a user without a sentence around it saying what it means. A banner for a
partial failure says what is still true, as in the example below.

**Paused is not broken.** When something is waiting for a condition, say
which one: "Paused: the Spotify integration is not set up, or a permission
is missing in Settings." Do not show it in the red of an error.

**Keep file names and settings out of what an end user reads.** If the
reader is a user, not an operator, an error or empty state does not name
`people.yaml` or `HINDSIGHT_URL`. Say what is missing in their terms, and
what to do. Put the operator detail in one short line for admins, ideally
behind a "details" control, so the person who needs the file name can find it
and nobody else has to read it.

**When part of a page fails, degrade; do not blank.** "Live status is
incomplete: <reason>. The inventory and links below come from the fleet
repo and are still correct." A filter with no match says "No hosts match."
and nothing more.

**One term per concept.** Pick a word for each thing and use it in the UI,
the README and the docs. If the interface says "device" and the docs say
"node", one of them is wrong.

**Keep it short.** A label is a word or two, a hint is a sentence. Sentence
case, no exclamation marks, no humour that a tired user at 2am would not
enjoy.

**Same voice as the prose.** Avoid em dashes here too, as in the docs (in UI
text that is a style preference, not something the audit checks), and keep out
filler and marketing words.
Write what you would say to a colleague standing next to the screen.

Source: the ha-propsense session, applying conformIT to a Home Assistant
integration, proposed this and supplied the "Paused" example, which it wrote
to replace "Dormant action ... needs the provider". The rules above are my
generalisation of its proposal. They have not been tried on another
project, and nothing here was checked against any UI (VERIFY).
