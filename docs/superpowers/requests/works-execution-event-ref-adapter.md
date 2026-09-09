# Build request: WORKS execution event-ref adapter

Owner: `Aftergraph/works-execution`
Contract: `platform-event-ref/0.1` (correlation substrate only; never a ninth Fabric, never a universal event bus)
Acceptance vectors: `ADP-WORKS-001`, `ADP-WORKS-002`

## What to build

A WORKS execution adapter that projects native effect commits
(`work.effect.committed`) to `platform-event-ref/0.1`, retaining the native
envelope reference so every projection stays verifiable.

## Acceptance

- `ADP-WORKS-001`: effect projection with the native envelope reference retained is accepted.
- `ADP-WORKS-002`: a projection that drops the native envelope reference is
  rejected; unverifiable projections fail closed.

## Out of scope

Governance pins acceptance only. Governance implements nothing in
`Aftergraph/works-execution`; the canonical adapter behavior belongs to the
WORKS owners, proven by the owner repo's own tests, PR, CI, merge queue,
and exact-head evidence.
