# Build request: Runtime opportunity recovery

Owner: `Aftergraph/runtime`
Contract: `proactivity/0.1` (`docs/contracts/proactivity/0.1.json` in after-graph-governance)
Acceptance vectors: `PRO-004`
Seam binding: `docs/PROACTIVITY-ORG-V1.md` in after-graph-governance

## What to build

Own Runtime-path proactivity sensing inside `Aftergraph/runtime`:
mission-state sensing projecting to opportunity/recovery candidates
that claim neither execution nor admission. This is the Runtime path
doing its own sensing over its own mission state — recovery candidates
surface; admission and execution authority stay where the bindings put
them.

## Acceptance

- `PRO-004`: Runtime mission-state sensing to an opportunity/recovery candidate claiming neither execution nor admission is accepted.

## Out of scope

Governance registers the contract and pins acceptance only. Governance implements nothing in `Aftergraph/runtime`; the canonical recovery
behavior belongs to the Runtime owners, proven by the owner repo's own
tests, PR, CI, merge queue, and exact-head evidence.
