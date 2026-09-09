# Build request: Runtime capability resolver and authority-preserving fallback

Owner: `Aftergraph/runtime`
Contract: `capability-action/0.1`
Acceptance vectors: `CAP-001`, `CAP-002`, `CAP-003`, `CAP-004`, `CAP-005`

## What to build

A Runtime capability resolver that selects among concrete implementations
for a semantic action, with an authority-preserving fallback path: when the
primary implementation is unavailable, a fallback may serve only within an
equal-or-narrower authority envelope.

## Acceptance

- `CAP-001`: implementations within the envelope are accepted.
- `CAP-002`: an implementation that widens the envelope is rejected.
- `CAP-003`: a consequential effect without verification is rejected.
- `CAP-004`: fallback to an available implementation with an
  equal-or-narrower envelope is accepted.
- `CAP-005`: fallback that widens the envelope is rejected, even when the
  primary is unavailable. Fallback never widens semantic capability
  authority; Runtime may orchestrate but never widen authority.

## Out of scope

Governance pins acceptance only. Governance implements nothing in
`Aftergraph/runtime`; the canonical resolver and fallback behavior belong
to the Runtime owners, proven by the owner repo's own tests, PR, CI, merge
queue, and exact-head evidence.
