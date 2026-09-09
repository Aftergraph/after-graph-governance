# Build request: Trust Gateway tenant lifecycle

Owner: `Aftergraph/trust-gateway`
Contract: `tenant-lifecycle/0.1` (`docs/contracts/tenant-lifecycle/0.1.json` in after-graph-governance)
Acceptance vectors: `TEN-001`, `TEN-002`, `TEN-003`, `TEN-004`, `TEN-005`

## What to build

Implement the tenant lifecycle operational truth inside
`Aftergraph/trust-gateway` across ACTIVE/SUSPENDED/EXPORTING/DELETING/
DELETED: admission gating per state (DELETING denies new grants,
ingestion, and execution; SUSPENDED denies execution; EXPORTING denies
ingestion), coordination of per-owner export/deletion/retention actions,
and terminal completion only after every required owner's
acknowledgement. Trust Gateway coordinates but never owns tenants' domain
data; audit retention stays distinct.

## Acceptance

- `TEN-001`: ACTIVE tenant with recorded acknowledgements admits grants.
- `TEN-002`: DELETING denies new grants, ingestion, and execution.
- `TEN-003`: DELETED transition without all owner acknowledgements is rejected.
- `TEN-004`: SUSPENDED denies new execution.
- `TEN-005`: EXPORTING denies new ingestion.

## Out of scope

Governance registers the contract and pins acceptance only. Governance implements nothing in `Aftergraph/trust-gateway`; the canonical lifecycle
belongs to the Trust Gateway owners, proven by the owner repo's own tests,
PR, CI, merge queue, and exact-head evidence.
