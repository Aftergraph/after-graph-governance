# R.O.R.O. Component Model v0.1

**Status:** bootstrap contract for P−1 System Reality.
**Scope:** source identity and lineage only; runtime/cloud/credential/state observations follow in later R.O.R.O. slices.

## Core law

`ComponentID != Repository != SourceBinding != Build != Deployment`.

A component is a stable semantic identity. Git repositories and paths are mutable source bindings. A component can move between repositories without changing identity when migration equivalence is later proven.

R.O.R.O. does not become the native source of truth for the systems it observes. It records evidence-bound observations and contradictions. `UNKNOWN` is a valid result and must never be promoted to safe reality by omission.

## Registry structure

`component-registry.json` contains two independent collections:

- `repositories`: exact-head source observations from the live GitHub organization;
- `components`: semantic component identities discovered from explicit package/project manifests, each with exact source bindings.

Repository presence alone therefore does not create a semantic component.
## Identity rules

Canonical Aftergraph package manifests map to semantic component IDs:

```text
@aftergraph/mission-graph → ag:component:mission-graph
@aftergraph/runtime       → ag:component:runtime
```

Legacy AVC package identities are kept distinct until migration evidence exists:

```text
@avc/mission-graph → ag:legacy:avc:mission-graph
```

A matching suffix is not migration proof. `component-lineage.json` records predecessor/successor candidates and evidence separately.

## Reality vocabulary

Reality facets answer *which reality is being discussed*: `DECLARED`, `CANONICAL`, `DESIRED`, `INSTALLED`, `CONFIGURED`, `RUNNING`, `REACHABLE`, `HEALTHY`, `VERIFIED`, `RECOVERABLE`.

Epistemic status answers *how we know it*: `VERIFIED`, `OBSERVED`, `INFERRED`, `DECLARED`, `PROPOSED`, `STALE`, `CONFLICTING`, `UNKNOWN`.

These dimensions are intentionally independent. A service can be observed as RUNNING while its canonical source binding is CONFLICTING or UNKNOWN.
