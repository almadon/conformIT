# Security posture

Derived from `novak/docs/security.md` and generalised. The threat model
isn't "keep attackers off the network." It's:

1. Preventing sensitive data from reaching a party that shouldn't hold it,
   including a model vendor.
2. Avoiding the ordinary operational failures: plaintext credentials
   readable by the model or an attacker, over-broad tool permissions, and
   prompt injection through content the model reads.

## Rule 1. The model gets capabilities, never credentials

A model calls `search_documents`. It never sees the API token behind it.
Credentials live in the server's environment, sourced from an OS keychain
or a secrets manager at startup, not in a prompt, a chat log, or a memory
store.

**Never paste a key, password, or account number into a chat.** Sessions
are logged, summarised into memory, and re-injected into later contexts. A
secret pasted once is a secret in an unknown number of places. If you catch
yourself about to, the correct move is a new environment variable on the
service, not a paste.

## Rule 2. Least privilege, per integration

- One credential per integration, scoped as tightly as the service allows.
- **Read-only unless writing is the point.** Adding write access is a
  separate, deliberate change.
- Destructive operations off by default. Where a service has no trash,
  this isn't a preference.
- Powerful integrations are allowed, but must be turned on deliberately,
  never enabled as a side effect of installing something else
  (`novak/docs/decisions.md` #10).

## Rule 3. Retrieved content is untrusted input

Content the system reads can contain instructions aimed at the model. In
order of importance:

1. **Capability asymmetry.** Reading tools are cheap to grant. Acting
   tools, meaning send, publish, pay, delete, must be rare, separate, and
   confirmation-gated. If the model can't send, injected instructions can't
   exfiltrate anything. This is the load-bearing mitigation; the rest are
   secondary.
2. **Confirmation gates.** Any tool with outward side effects requires an
   explicit confirmation step, surfaced to a human.
3. **Scoped sessions.** Attach powerful tools only to the conversations
   that need them, rather than registering everything everywhere.

## Rule 4. Identity comes from the connection, not from a parameter

Where data is partitioned per user or per tenant, the partition must be
bound to the connection (a per-connection URL, token, or channel), never
accepted as an argument the caller supplies.

This is what keeps one person's data out of another's context and out of
reach of anything the model reads. There's no argument in which to name
someone else.

`novak` rejected two otherwise-good memory backends on exactly this
criterion, and stated the bar for any replacement: it must bind identity to
the connection, or the first-party shim comes back.

**Cost:** narrows the field of adoptable software, sometimes sharply.

## Rule 5. Exposure is decided per service, and the default is inward

- Bind to LAN or loopback. Forward nothing inbound by default.
- Remote access via a mesh VPN (Tailscale), not port forwarding.
- Enable auth even on the local network. LAN peers include IoT devices you
  don't control.
- A service with no rate limiting does not go on the public internet, full
  stop.
- Every genuinely public service is an individual, recorded decision.

## Rule 6. Know which of your secrets are actually secret

Not everything called a secret is one, and treating a public value as
secret wastes the mechanism you need for real ones.

The worked example, from `anjunatree/docs/DEVELOPMENT.md`:

- A **PKCE client ID is not a secret.** The flow exists so browser apps
  need none. Store it as a repository variable.
- A **token the browser must receive is not a secret either.** Keep it in
  secret storage only to avoid pinning a rotating value into git history.
- The **`.p8` private key is the one real secret.** It never reaches a
  browser, never reaches CI, never reaches the repo.

Two corollaries:

- **Anything inlined into a client bundle at build time is public.** A
  build-time prefix (`VITE_`, `NEXT_PUBLIC_`, and the like) protects
  nothing.
- **Repo secrets are not a boundary against collaborators.** Anyone with
  write access can add a workflow that prints them. They're a boundary
  against the public and against fork PRs, and nothing more. For a real
  boundary, use a protected environment with required reviewers, or keep
  the credential in the host's dashboard rather than in the repo at all.

## Rule 7. The stores are readable, and get audited

Whatever the system accumulates about people (memories, logs, transcripts)
needs a surface where a human can read, correct, and delete it. A store
nobody can inspect is a store nobody can correct.

## Rule 8. Pin versions

A dependency fetched at runtime (`npx -y`, `:latest`, an unpinned action)
is an unreviewed change on every start, and an outage when the network is
down. Pin it. `novak/docs/credits.md` records this as a known weakness in
its own stack, an honest open item rather than a solved problem.

## Rule 9. A public repo gets scanned for what shouldn't be in it

Secrets and personal information don't wait for someone to notice them by
eye. A public repository (or one about to become public) gets checked
for at least three things before and after publication, not just once at
the start:

- **Credentials**: API keys, tokens, private key material. A committed
  key is not "removed" by deleting it in a later commit; it's already
  public, and stays public in history and in any fork. The only correct
  response to finding one is to **rotate it immediately and tell everyone
  with access to the same credential**, then remove it from the repo as a
  separate, secondary cleanup. conformIT's own audit tool
  (`scripts/conform.sh audit`) checks for this and says so in exactly
  those terms; see [decisions.md](decisions.md) #13.
- **Personal email addresses that aren't already public via git
  authorship.** A commit author's own email is already exposed by the
  nature of a public git repo; an email address that shows up in a
  config file, a comment, or a support script is a different and
  avoidable disclosure.
- **Internal or private service URLs and non-routable addresses**
  (private IP ranges, internal DNS suffixes). These tell an attacker
  what your topology looks like even when nothing about them is a
  "secret" in the credential sense.

This is a scan for what's already public and shouldn't be, not a
guarantee nothing was missed. A regex-based check has a real false-negative
rate; treat a clean scan as "nothing obvious found," not as proof.

## What this does not cover

Nothing here addresses a compromised developer machine, a malicious
dependency that passes review, or a vendor breach. Those are accepted
risks at this scale, recorded so the omission is deliberate rather than
overlooked.
