# Build request: Trust Gateway Consent Ledger

Owner: `Aftergraph/trust-gateway`
Contract: `consent-ledger/0.1` (`docs/contracts/consent-ledger/0.1.json` in after-graph-governance)
Acceptance vectors: `CON-001`, `CON-002`, `CON-003`, `CON-004`
Conformance fixtures: `CONS-REV-001`, `CONS-REV-002`

## What to build

Implement the Consent Ledger state and enforcement inside
`Aftergraph/trust-gateway`: ledger records with versions, the four events
Granted/Restricted/Revoked/Expired, and use evaluation that permits or
denies processing. Consent stays a separate axis from execution authority:
the ledger never grants authority. Revocation must invalidate downstream
effective use across all six targets (new ingestion, derived memory,
context bundles, ACC projections, World State assertions, future
processing) while audit history keeps its own retention law.

## Acceptance

- `CON-001`: use within granted purpose, scope, and validity is accepted.
- `CON-002`: use where revocation ended the purpose is rejected.
- `CON-003`: use past expiry is rejected.
- `CON-004`: use outside a narrowed restricted purpose is rejected.
- `CONS-REV-001`: revoked source/purpose invalidates derived uses with audit preserved.
- `CONS-REV-002`: ingestion denied, bundles invalidated, future processing blocked.

## Out of scope

Governance registers the contract and pins acceptance only. Governance implements nothing in `Aftergraph/trust-gateway`; the canonical ledger
belongs to the Trust Gateway owners, proven by the owner repo's own tests,
PR, CI, merge queue, and exact-head evidence.
