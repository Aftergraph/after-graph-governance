# Build request: ACC capsule conformance

Owner: `Aftergraph/context-continuity`
Contract: memory-acc-brain separation binding (`docs/MEMORY-ACC-BRAIN-V1.md` in after-graph-governance)
Acceptance vectors: `SIT-001`, `SIT-003`

## What to build

Implement portable continuity capsules under the continuity-contract owner
(`Aftergraph/context-continuity`; no dedicated ACC repo exists and none is
created): machine-readable capsules with delta semantics, receiver
handshake, omission manifest, and freshness. Capsules are inert data until
a runtime acts on them; they carry authority boundaries but confer none,
and never define mission success. Capsule hashes prove integrity, never
semantic truth.

## Acceptance

- `SIT-001`: capsule-carried context composing generic entities and a descriptive relationship with full provenance is accepted.
- `SIT-003`: capsule transfer crossing tenant scope without explicit governed export/import is rejected.

## Out of scope

Governance binds seams and pins acceptance only. Governance implements nothing in `Aftergraph/context-continuity`; the canonical capsule behavior
belongs to the owning repo, proven by its own tests, PR, CI, merge queue,
and exact-head evidence.
