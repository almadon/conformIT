# Security posture

Derived from `novak/docs/security.md` and generalised. The threat model is
not "keep attackers off the network." It is:

1. Preventing sensitive data from reaching a party that shouldn't hold it —
   including a model vendor.
2. Avoiding the ordinary operational failures: plaintext credentials readable
   by the model or an attacker, over-broad tool permissions, and prompt
   injection through content the model reads.

## Rule 1 — the model gets capabilities, never credentials

A model calls `search_documents`. It never sees the API token behind it.
Credentials live in the server's environment, sourced from an OS keychain or
a secrets manager at startup — not in a prompt, a chat log, or a memory
store.

**Never paste a key, password, or account number into a chat.** Sessions are
logged, summarised into memory, and re-injected into later contexts. A secret
pasted once is a secret in an unknown number of places. If you catch yourself
about to, the correct move is a new environment variable on the service, not
a paste.

## Rule 2 — least privilege, per integration

- One credential per integration, scoped as tightly as the service allows.
- **Read-only unless writing is the point.** Adding write access is a
  separate, deliberate change.
- Destructive operations off by default. Where a service has no trash, this
  is not a preference.
- Powerful integrations are allowed, but must be turned on deliberately —
  never enabled as a side effect of installing something else.
  (`novak/docs/decisions.md` #10.)

## Rule 3 — retrieved content is untrusted input

Content the system reads can contain instructions aimed at the model. In
order of importance:

1. **Capability asymmetry.** Reading tools are cheap to grant; *acting* tools
   — send, publish, pay, delete — must be rare, separate, and
   confirmation-gated. If the model cannot send, injected instructions cannot
   exfiltrate. This is the load-bearing mitigation; the rest are secondary.
2. **Confirmation gates.** Any tool with outward side effects requires an
   explicit confirmation step, surfaced to a human.
3. **Scoped sessions.** Attach powerful tools only to the conversations that
   need them, rather than registering everything everywhere.

## Rule 4 — identity comes from the connection, not from a parameter

Where data is partitioned per user or per tenant, the partition must be bound
to the connection — a per-connection URL, token, or channel — never accepted
as an argument the caller supplies.

This is what keeps one person's data out of another's context *and* out of
reach of anything the model reads: there is no argument in which to name
someone else.

`novak` rejected two otherwise-good memory backends on exactly this
criterion, and stated the bar for any replacement: it must bind identity to
the connection, or the first-party shim comes back.

**Cost:** narrows the field of adoptable software, sometimes sharply.

## Rule 5 — exposure is decided per service, and the default is inward

- Bind to LAN or loopback; forward nothing inbound by default.
- Remote access via a mesh VPN (Tailscale), not port forwarding.
- Enable auth even on the local network — LAN peers include IoT devices you
  do not control.
- A service with no rate limiting does not go on the public internet, full
  stop.
- Every genuinely public service is an individual, recorded decision.

## Rule 6 — know which of your secrets are actually secret

Not everything called a secret is one, and treating a public value as secret
wastes the mechanism you need for real ones.

The worked example from `anjunatree/docs/DEVELOPMENT.md`:

- A **PKCE client ID is not a secret** — the flow exists so browser apps need
  none. Store it as a repository *variable*.
- A **token the browser must receive is not a secret** either. Keep it in
  secret storage only to avoid pinning a rotating value into git history.
- The **`.p8` private key is the one real secret.** Never reaches a browser,
  never reaches CI, never reaches the repo.

Two corollaries:

- **Anything inlined into a client bundle at build time is public.** A
  build-time prefix (`VITE_`, `NEXT_PUBLIC_`, …) protects nothing.
- **Repo secrets are not a boundary against collaborators.** Anyone with
  write access can add a workflow that prints them. They are a boundary
  against the public and against fork PRs, and nothing more. For a real
  boundary, use a protected environment with required reviewers, or keep the
  credential in the host's dashboard rather than in the repo at all.

## Rule 7 — the stores are readable, and get audited

Whatever the system accumulates about people — memories, logs, transcripts —
has a surface where a human can read, correct, and delete it. A store nobody
can inspect is a store nobody can correct.

## Rule 8 — pin versions

A dependency fetched at runtime (`npx -y`, `:latest`, an unpinned action) is
an unreviewed change on every start and an outage when the network is down.
Pin it. `novak/docs/credits.md` records this as a known weakness in its own
stack — an honest open item, not a solved problem.

## What this does not cover

Nothing here addresses a compromised developer machine, a malicious
dependency that passes review, or a vendor breach. Those are accepted risks
at this scale, recorded so the omission is deliberate rather than overlooked.
