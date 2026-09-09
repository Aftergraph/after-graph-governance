# Build request: Runtime memory separation

Owner: `Aftergraph/runtime`
Contract: memory-acc-brain separation binding (`docs/MEMORY-ACC-BRAIN-V1.md` in after-graph-governance)

## What to build

Enforce the Runtime Memory side of the separation binding inside
`Aftergraph/runtime`: Runtime Memory stays operational and contextual,
scoped to the live execution context, never persisted as truth, and never
eligible to decide what a principal may do. Purify transitional packages
so Runtime recreates neither AIE, Trust Gateway, WORKS, nor ACC inside
itself.

## Acceptance

Conformance is pinned by the memory-acc-brain separation binding; the
binding's active-doc tests gate the seams. Runtime proves separation with
its own tests, PR, CI, merge queue, and exact-head evidence.

## Out of scope

Governance binds seams only. Governance implements nothing in
`Aftergraph/runtime`; the canonical memory behavior belongs to the Runtime
owners.
