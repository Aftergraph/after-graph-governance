# Memory / ACC / Brain Separation V1 — Canonical V4 Binding

Status: Canonical for memory separation. Topology: `docs/platform-topology/2.0.json`.

**Design rationale:** V4 spec §§5.4–5.5/7.4 and `docs/ACC-BOUNDARY-PROPOSAL-v0.1.md`
(rationale only; this document is normative for separation).

Three stores, three owners, no overlap. No store is eligible to hold or
confer authority, and nothing here creates a new store or owner.

| Store | V4 owner | Binding |
| --- | --- | --- |
| Runtime Memory | `runtime` | Operational and contextual working state for the live execution only: checkpoints, metering, retry context. It is scoped to the execution context, never persists beyond it as truth, and never decides what a principal may do. |
| WORKS Brain | `works-execution` | Durable organizational knowledge: settled evidence, quittance, and promoted know-how. Promotion into the Brain follows the human-stamped promotion law; the Brain never absorbs live personal context and never substitutes for mission authority. |
| ACC transfer | `context-continuity` | Portable continuity capsules moving actionable context across model/agent/session/runtime boundaries: deltas, receiver handshake, omission manifest, freshness. Capsules are inert data until a runtime acts on them; ACC carries authority boundaries but confers none, and never defines what counts as mission success. |
| Observation intake | `wi-backend` | Source-neutral observations feed commitments and WorkItems. Intake writes observations, never memory truth. |
| Render surfaces | `wi-frontend` (via `studio`) | Surfaces render projections of memory and Brain state. Rendering reads; it owns no memory and changes no stored state. |

Invariants (restated, not extended):

- Memory != Authority.
- Prediction != Observation.
- A capsule hash proves integrity, never semantic truth.
- Stale state is represented as stale/unknown, never refreshed by re-stamping.
- Revocation of the underlying consent or authority invalidates downstream
  effective use; invalidation behavior itself is a later wave, not this binding.
