# Verified Auto V1 — Canonical V4 Seam Binding

Status: Canonical for Verified Auto seam ownership. Topology: `docs/platform-topology/2.0.json`.

**Design rationale:** `docs/superpowers/specs/2026-09-08-aftergraph-verified-auto-execution-design.md` (rationale only; this document is normative for seam ownership).

Verified Auto composes the seven V4 planes without widening any authority
envelope. Ownership follows the repository registry; nothing here grants a
new authority, and no new verification owner is created.

| Seam | V4 owner | Binding |
| --- | --- | --- |
| Experience controls and projection | `studio` (primary), `wi-frontend` (specialist surface) | Presents Auto/Verified controls, budgets, live execution, evidence and verdicts. Mints no authority, mutates no WORKS evidence, manufactures no verified state. |
| Perception ingestion | `wi-backend` | Source-neutral observations into commitments and WorkItems. Grants no execution authority. |
| Authority envelope and revocation | `aie` | Mission authority, delegation, budget ceilings, revocation semantics. Decides whether a principal may execute; selects no providers and issues no verification verdicts. |
| Admission and enforcement | `trust-gateway` | Provider/model eligibility, data-handling enforcement, route decisions and receipts, break-glass admission. Owns no agent lifecycle, persists no durable execution state, and never independently confirms execution output. |
| Capability orchestration | `runtime` | Planner/worker lifecycle, dispatch, retry and repair orchestration, metering. Orchestrates only within admitted authority: it never bypasses Trust Gateway admission, never replaces WORKS as durable execution truth, and declares no independent verification verdicts. |
| Durable execution and evidence | `works-execution` | WorkGraph state, leases, retries, attempt history, cost records, canonical evidence and quittance. Never reinterprets route policy, never approves its own expanded authority, and never self-verifies the resulting subject. |
| Independent verification | `sentinel` (+ registered domain verifiers) | Binds WORKS evidence to the Trust Gateway admission record. Execution output is never confirmed by its own executor. Consequential effects require verification before they count as outcomes. No new verification owner is created here: `sentinel` already owns the Verification plane. |

Invariants (restated, not extended):

- Complete != Verified.
- Runtime may orchestrate but never widen authority.
- Fail closed on consequential ambiguity.
- Revocation invalidates downstream effective use.
