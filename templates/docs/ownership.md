<!--
conformIT ownership scaffold.

Copy this to docs/ownership.md and fill in a row for each thing the project
manages. Delete this comment block when done. Skip the file only if nothing
here is running, and record the skip in docs/decisions.md.

Reasoning: docs/documentation-standard.md, "docs/ownership.md".
-->

# Ownership

What this project manages, who controls each thing, and why.

| Thing | Owner | Mechanism | Why | Where to change it | Backup |
|---|---|---|---|---|---|
| [e.g. collector config] | [this repo] | [rewritten every run] | [one source of truth] | [path in this repo] | [how it is saved and restored] |

## Synced both ways

[For each thing marked "synced both ways": the direction, what triggers it
(manual or automatic), and what wins in a conflict. Delete this section if
nothing is synced both ways.]

## Module contract block

Each module README opens with these five lines:

- **Does:** [what it does]
- **Owns settings:** [who controls its settings]
- **Keeps state:** [what it stores, and where]
- **Rolls back by:** [see design principle 12, or the recorded exception]
- **Exposes:** [ports, endpoints, files others rely on]
