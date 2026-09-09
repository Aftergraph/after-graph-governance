# Build request: World State projection

Owner: `Aftergraph/runtime`
Contract: `world-assertion/0.1` (`docs/contracts/world-assertion/0.1.json` in after-graph-governance)
Acceptance vectors: `WA-001`, `WA-002`, `WA-003`
Conformance fixtures: `REBUILD-001`, `INVALIDATE-001`, `LAUNDER-001`

## What to build

Materialize the operational World State projection inside
`Aftergraph/runtime` strictly as a rebuildable projection over
provenance-bearing canonical sources. Runtime agents may propose assertion
candidates conforming to `world-assertion/0.1`; they receive no
general-purpose API for writing effective world truth.

## Acceptance

- `WA-001`: current observed state with full lineage is accepted.
- `WA-002`: predicted state offered where current observed evidence is required is rejected.
- `WA-003`: re-stamped stale state claimed current is rejected.
- `REBUILD-001`: post-failure rebuild marks unavailable sources stale/unknown.
- `INVALIDATE-001`: source deletion invalidates derived state per provenance with audit preserved.
- `LAUNDER-001`: timestamp refresh without new observation fails closed.

## Out of scope

Governance registers the contract and pins acceptance only. Governance implements nothing in `Aftergraph/runtime`; the canonical projection
belongs to the Runtime owners, proven by the owner repo's own tests, PR,
CI, merge queue, and exact-head evidence.
