# Build request: Cron observation sensing

Owner: `Aftergraph/aftergraph-cron-fabric`
Contract: `proactivity/0.1` (`docs/contracts/proactivity/0.1.json` in after-graph-governance)
Acceptance vectors: `PRO-002`, `PRO-006`
Seam binding: `docs/PROACTIVITY-ORG-V1.md` in after-graph-governance (zero Cron execution authority)

## What to build

Own Cron scheduled sensing inside
`Aftergraph/aftergraph-cron-fabric`: read-only observation readings
projected to finding candidates that claim no execution and no
admission. The Cron Fabric retains zero execution authority — scheduled
sensing may report findings, never execute, and never admit.

## Acceptance

- `PRO-002`: a Cron finding candidate claiming execution is rejected (zero Cron execution authority).
- `PRO-006`: a Cron scheduled read-only sensing reading reporting a finding that claims no execution is accepted.

## Out of scope

Governance registers the contract and pins acceptance only. Governance implements nothing in `Aftergraph/aftergraph-cron-fabric`; the
canonical sensing behavior belongs to the Cron Fabric owners, proven by
the owner repo's own tests, PR, CI, merge queue, and exact-head
evidence.
