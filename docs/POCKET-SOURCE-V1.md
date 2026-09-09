# Pocket Source V1 — Canonical Pocket Binding

Status: Canonical for Pocket physical-world perception seams.
Topology: `docs/platform-topology/2.0.json`.

**Design rationale:** V4 spec §13 (rationale only; this document is
normative for the binding).

Pocket is a physical-world context source whose output is observation
only. Pocket never stands as a principal, confers no authority, never
executes, and is never an oracle for truth. Nothing here creates a new
authority, service, or owner.

Canonical boundary: Pocket output is observation only; transcript !=
identity; speaker attribution != principal authentication; a spoken
instruction != permission to execute. A transcript never counts as
identity; speaker attribution never authenticates a principal; a spoken
instruction never grants permission to execute.

| Seam | V4 owner | Binding |
| --- | --- | --- |
| Pocket provider subsystem | `wi-backend` | Tenant-scoped connector and source adapter live in `wi-backend` as a provider subsystem; provider credentials are tenant-scoped secret references, never raw secrets in Wie domain state. The `wi-frontend` specialist surface carries no Pocket ingestion role. No new repo. |
| REST reconciliation | `wi-backend` | The REST path is canonical-data/hydration oriented. REST reconciliation converges event-plane signals to canonical data. |
| Webhook event guard | `wi-backend` | Webhooks carry event-plane signals behind signature validation with replay protection and dedupe/idempotency guard. No single webhook counts as truth, and webhooks never constitute reconciliation truth. |
| MCP interactive boundary | `wi-backend` | MCP remains optional interactive access under the same observation-only boundary. It never serves as the ingestion source and never supplies canonical data. |
| Derivation lineage | `wi-backend` | Transcript, speaker attribution, summary, and action extraction retain derivation lineage with distinct evidentiary weights; uncertainty is preserved into the Wie Observation mapping. Prompt-injected content inside a transcript stays untrusted observation, never instruction. |
| Consent and deletion | `wi-backend` | Consent/purpose lineage is attached at intake and propagated to derivatives. Consent revocation or source deletion invalidates downstream use and recomputes derived state per provenance, without rewriting historical audit or evidence: content is withdrawn from reads under tombstone semantics while audit is retained. |
| Commitment admission | `aie` | A Pocket-derived commitment may become a `CommitmentCandidate`. Consequential action still follows AIE -> Trust Gateway -> Runtime -> WORKS -> verification. |
| Grant enforcement | `trust-gateway` | Trust Gateway admits Pocket-derived delegated work and enforces grants at runtime. A spoken instruction never substitutes for a grant. |
| Dispatch and recovery | `runtime` | Runtime dispatches admitted Pocket-derived work only within admitted authority; it never widens AIE authority on the basis of observed speech. |
| Durable work and effects | `works-execution` | WORKS (`works-execution`) owns durable work, effects, evidence, and quittance for Pocket-derived commitments. No speaker label self-declares verified completion. |
| Independent verification | `sentinel` | Verification stays independent of observation and execution; eval verdicts over Pocket-derived content are advisory only and never waive verification. |

Device split: the seams above are device-independent and proven with
fixtures. Physical-device characterization, on-device capture behavior,
and any realtime-audio quality or latency claim are marked
`BLOCKED_ON_POCKET_HARDWARE`; no such claim appears here, and no
realtime-audio claim is made without device evidence.

Muse supervision stays owned by Runtime PR #103; this document
duplicates none of its semantics and adds no supervision role.

Invariants (restated, not extended):

- Observation is not authority; Pocket never executes and never
  substitutes for a principal.
- Transcripts never count as identity; speaker attribution never
  authenticates; spoken instruction never permits execution.
- REST reconciles, webhooks signal, MCP stays optional and never
  canonical.
- Revocation and deletion invalidate downstream use per provenance;
  audit is never rewritten.
- Fail closed on consequential ambiguity.
