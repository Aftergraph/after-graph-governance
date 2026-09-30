# Economic Graph V1 — Canonical Capability-Family Binding

Status: Canonical for the v1 zero-value/read-only capability slice.

Economic Graph is a cross-repository capability family. It is not a new architecture plane, top-level service, authority, execution owner, verification owner, or repository.

## Ownership

| Concern | Canonical owner |
|---|---|
| Contract registration / lifecycle | after-graph-governance |
| Economic authority/policy | AIE |
| Admission / approvals / secrets | Trust Gateway |
| Agent orchestration / read-only observation | Runtime |
| Durable work / execution lineage / recovery | WORKS |
| Independent verification | Sentinel |
| Operator projection | FIHIM / HomeOS |
| Discovery / routing / typed client facade | CORE |

## v1 safety envelope

Canonical v1 permits simulation, read-only observation, authority binding, durable lineage binding, reconciliation semantics, verification and operator projection.

Canonical v1 does **not** claim live settlement, signing, custody or autonomous spending.

Runtime receipts in this slice require `externalEffects = 0`.

## Client package

`@aftergraph/economic-graph-client` is a non-authoritative developer facade maintained in CORE. It may discover capabilities, submit zero-effect simulation/read-only requests to configured owners, normalize events and expose typed contracts. It never grants authority or becomes canonical economic state.

The legacy `@aftergraph/agent-platform/economic-graph` entry point may remain as a compatibility re-export only.

## Promotion

Non-canonical economic capabilities follow `AFTERGRAPH-FRONTIER-V1.md` and `PROMOTION-GATES-V1.md`. Promotion is per capability, not by project/repository version.
