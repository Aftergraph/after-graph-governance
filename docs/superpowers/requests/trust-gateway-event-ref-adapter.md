# Build request: Trust Gateway event-ref adapter

Owner: `Aftergraph/trust-gateway`
Contract: `platform-event-ref/0.1` (correlation substrate only; never a ninth Fabric, never a universal event bus)
Acceptance vectors: `ADP-TG-001`, `ADP-TG-002`

## What to build

A Trust Gateway adapter that projects native audit admissions
(`policy.action.admitted`) to `platform-event-ref/0.1` field-for-field,
preserving native meaning and inventing no authority.

## Acceptance

- `ADP-TG-001`: full admission projection with complete correlation is accepted.
- `ADP-TG-002`: a projection that adds an authority-bearing field is rejected;
  projections are correlation-only and fail closed.

## Out of scope

Governance pins acceptance only. Governance implements nothing in
`Aftergraph/trust-gateway`; the canonical adapter behavior belongs to the
Trust Gateway owners, proven by the owner repo's own tests, PR, CI, merge
queue, and exact-head evidence.
