# Aftergraph Relay v0.10 — Public Product Boundary

**Status:** Public documentation boundary

**Product role:** Human operator plane

**Architecture plane:** Experience

**Canonical implementation:** `Aftergraph/relay` (private)

**Public boundary owner:** Aftergraph Governance registers role, ownership, and must-not-own constraints; it does not replace Relay's implementation truth.

## Purpose

Aftergraph Relay is the governed human operator plane for supervising autonomous work across agents, missions, execution nodes, Runtime projection, and Aftergraph infrastructure.

Relay may project and control bounded operational state, but it does not become the canonical owner of authority, trust admission, durable execution, or independent verification.

## Governed external execution

The v0.10 product line includes a least-privilege external execution surface for intelligent-system clients. Publicly supported semantics are:

- authority is issued as an explicit, expiring, revocable execution lease;
- leases carry a principal, explicit capabilities, optional exact mission scope, and an invocation budget;
- external calls are restricted to a named operation catalog;
- observation and control authority are separate;
- mission-scoped operations fail closed outside the lease's mission;
- unknown operations do not widen into arbitrary command execution.
The external surface must not expose Relay administrator authority, raw node execution authority, peer credentials, raw terminal secrets, or direct root authority. `shell.exec` is not part of the public execution contract.

## MCP boundary

Relay may be consumed through a bounded MCP adapter. The adapter is a transport/interface projection over the same execution-lease authority; it is not a second authority model and must not invent broader capabilities than Relay grants.

The public contract is intentionally narrow: clients discover allowed operations and invoke one named operation. Authentication alone does not imply observation, control, or mission authority.

## Ownership boundary

Relay **owns** operator-facing projection, operational supervision, bounded session lifecycle control, fleet/operator views, and Relay-local audit/telemetry for those surfaces.

Relay **must not own**:

- AIE authority or delegation semantics;
- Trust Gateway runtime admission, consent, secrets, or policy authority;
- WORKS durable work/execution truth;
- Runtime's canonical agent lifecycle/orchestration truth;
- Sentinel or another registered verifier's independent verdicts.

The governing distinction remains:

```text
projection != authority != durable execution truth != independent verification
```
## Public evidence posture

The implementation repository is private, so this document deliberately publishes only the product boundary and stable interface semantics approved for public documentation. It does not publish credentials, deployment topology, host-specific paths, internal database locations, or private source excerpts.

Aftergraph's v0.10 release record classifies the governed external-execution path as production-verified. Public readers should treat that as an Aftergraph release claim, not as independently reproducible source evidence from this Governance repository.

## Knowledge Plane rule

`Aftergraph/docs` may render this public boundary with provenance pinned to the exact Governance commit containing it. The Knowledge Plane must not cite the private Relay repository as a public source or silently strengthen the evidence level described here.
