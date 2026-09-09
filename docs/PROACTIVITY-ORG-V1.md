# Proactivity Org V1 — Canonical Proactivity and Organization Binding

Status: Canonical for proactivity sensing and agent-organization seams.
Topology: `docs/platform-topology/2.0.json`.

**Design rationale:** V4 spec §§7.5/7.7 (rationale only; this document is
normative for the binding).

Proactivity senses and proposes; organization delegates and executes.
Sensing never executes, candidates never decide, and workers never verify
their own work. Nothing here creates a new authority, service, or owner.

| Seam | V4 owner | Binding |
| --- | --- | --- |
| Wie sensing | `wi-frontend` (specialist surface), `wi-backend` (intake) | External signals become possible work or commitment candidates. Wie proposes; only Runtime decides and only admitted paths execute. |
| Runtime opportunity and recovery sensing | `runtime` | Mission/goal/runtime state becomes opportunity or recovery candidates. Runtime decides attention and dispatch only within admitted authority; it never widens AIE authority. |
| Cron observation sensing | `aftergraph-cron-fabric` | Scheduled read-only organization sensing produces findings. Cron Fabric retains zero execution authority: it senses and reports, and never executes work. |
| Candidate admission | `wi-backend` | Observation updates and candidates (`Opportunity`, `AttentionCandidate`, `CommitmentCandidate`) enter through intake; candidates never self-admit to commitments — admission follows the governed resolution path. |
| Team topology and worker lifecycle | `runtime` | Runtime owns team topology, worker lifecycle, relay/peer operation, routing and recovery. Production defaults to manager-worker organization; peer communication stays bounded and protocol-governed. |
| Delegated authority and budgets | `aie` | AIE owns delegated authority envelopes and budget ceilings. Child envelopes are equal-or-narrower than the parent envelope, and the parent's remaining budget is atomically partitioned or reserved across child envelopes so delegation never multiplies authority or budget. |
| Admission and enforcement | `trust-gateway` | Trust Gateway admits delegated work and enforces grants at runtime. No worker may grant itself authority, and no worker administers peer authority. |
| Durable work and effects | `works-execution` | WORKS owns durable work, leases, effects, evidence and quittance. No worker may self-declare verified completion; completion counts only through evidence plus independent verification. |
| Independent verification | `sentinel` (+ registered domain verifiers) | Verification stays independent of execution. Evaluators never score their own execution; eval verdicts are advisory only and never waive verification. |

Invariants (restated, not extended):

- Sensing is not execution; Cron holds zero execution authority.
- Candidates never self-admit; admission follows the governed path.
- Delegation never multiplies authority or budget; child envelopes stay
  equal-or-narrower with partitioned budgets.
- No worker holds authority it granted itself; no completion is verified
  by its own executor.
- Evaluators stay distinct from executors; eval verdicts never waive
  verification.
- Fail closed on consequential ambiguity.
