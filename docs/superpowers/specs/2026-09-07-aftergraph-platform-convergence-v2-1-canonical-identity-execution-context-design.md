# Aftergraph Platform Convergence V2.1 — Canonical Identity & Execution Context

**Date:** 2026-09-07  
**Status:** Approved design, pending implementation plan  
**Scope owner:** `Aftergraph/after-graph-governance`  
**Primary domain owners:** `aie`, `trust-gateway`, `works-execution`  
**Experience consumer:** `studio`  
**Continuity consumer:** `context-continuity`

## 1. Purpose

V2.1 closes the first deferred convergence gap from Platform Reconciliation V1: a unified Principal/Tenant identity architecture and runtime binding across the Aftergraph polyrepo platform.

The goal is not to centralize all identity logic in one repository. The goal is to establish a small set of canonical cross-repo identities and immutable execution references while preserving existing domain ownership:

```text
Organization
  ↓
Tenant
  ↓
Principal
  ↓
Authority Context
  ↓
Mission
  ↓
Execution Context
  ↓
Work
  ↓
Action
  ↓
Evidence
  ↓
Verified Outcome
```

The governing execution law remains:

```text
Executable = Intersection(
  AIE authority/policy semantics,
  Trust Gateway runtime admission,
  WORKS durable execution
)
```

No UI, session, workspace, context transfer, model, skill, plugin, research result, or repository membership grants execution authority by itself.

## 2. Design decision

V2.1 adopts **distributed ownership with canonical envelopes**, not a central identity kernel.

### 2.1 Ownership

| Concern | Canonical owner | Responsibility |
|---|---|---|
| Contract registration/version compatibility | `after-graph-governance` | Registry, compatibility law, topology, identifier grammar, platform conformance vectors |
| Principal semantics | `aie` | Principal object semantics, authority linkage, delegation, attenuation, revocation |
| Tenant runtime isolation | `trust-gateway` | Authentication, tenant resolution, principal resolution, isolation, admission, approval, authorization enforcement |
| Durable execution binding | `works-execution` | Work identity, execution context, worker identity/lease binding, durable execution state |
| Human session/workspace projection | `studio` | Session, workspace/project projection, UI representation only |
| Actionable context transfer | `context-continuity` | Carries references without minting, extending, or amplifying authority |

### 2.2 Explicit non-ownership

- `after-graph-governance` MUST NOT become runtime identity authority.
- `studio` MUST NOT mint Principal authority.
- `workspace`, `project`, `space`, or session membership MUST NOT become tenant or authority roots.
- `autonomous-venture-company` MUST NOT become the canonical platform identity kernel.
- `context-continuity` MAY carry authority references but MUST NOT grant or amplify authority.

## 3. Existing contracts preserved

### 3.1 `identity/1.0` remains intact

V2.1 MUST NOT silently rewrite the existing frozen `identity/1.0` contract. It remains a compatibility contract with its existing shape and historical WORKS lineage.

Its current fields include:

```text
human
org
device
worker.role
runtime.work_id
runtime.lease_id
service_principal
privilege_note
```

The platform registry currently treats `identity/1.0` as a normative family consumed across AIE/TG/WORKS. V2.1 resolves the semantic drift by introducing narrower canonical contracts rather than mutating the meaning of `identity/1.0` in place.

### 3.2 Lease ambiguity is forbidden

`identity/1.0.runtime.lease_id` MUST be treated as a WORKS/runtime worker lease reference unless explicit evidence proves otherwise.

It MUST NOT be interpreted as an AIE `AuthorityLease` by prefix, position, historical usage, or convenience.

```text
worker/runtime lease
    ≠
authority lease
```

## 4. Canonical contract families

V2.1 introduces these families:

```text
principal/1.0
    owner: AIE

tenant/1.0
    owner: Trust Gateway

execution-context/1.0
    owner: WORKS

correlation/1.0
    owner: after-graph-governance
```

`identity/1.0` remains a preserved compatibility family.

## 5. `principal/1.0`

A Principal is the canonical platform actor identity for authority evaluation. It is not a UI account, session, device, worker lease, or role assignment.

Minimum shape:

```json
{
  "schema": "principal/1.0",
  "principal_id": "prn_<32hex>",
  "tenant_id": "ten_<32hex>",
  "type": "human",
  "identity_ref": "oidc:subject:...",
  "status": "active"
}
```

Allowed `type` values:

```text
human
agent
service
worker
```

Rules:

1. `principal_id` is stable within its tenant scope.
2. A single external `identity_ref` MAY map to different Principals in different tenants.
3. `identity_ref` identifies or resolves an actor but does not grant authority.
4. `service` and `agent` Principals MUST NOT gain human approval power merely because they exist in the same tenant.
5. Principal status is independent from AuthorityLease state.

## 6. `tenant/1.0`

A Tenant is the runtime isolation boundary. An Organization is the administrative/institutional owner.

```text
Organization = administrative / institutional ownership
Tenant       = runtime isolation boundary
```

Minimum shape:

```json
{
  "schema": "tenant/1.0",
  "organization_id": "org_<32hex>",
  "tenant_id": "ten_<32hex>",
  "status": "active"
}
```

Rules:

1. `Workspace != Tenant`.
2. `Project != Tenant`.
3. `Session != Tenant`.
4. Cross-tenant lookups MUST fail closed without leaking whether a foreign object exists.
5. Trust Gateway is responsible for runtime tenant resolution and isolation enforcement.

## 7. `execution-context/1.0`

`execution-context/1.0` is an immutable correlation/binding envelope created when WORKS materializes durable execution.

It is **not** an authorization token and does not freeze authorization state.

Minimum shape:

```json
{
  "schema": "execution-context/1.0",
  "organization_id": "org_<32hex>",
  "tenant_id": "ten_<32hex>",
  "principal_id": "prn_<32hex>",
  "mission_id": "mis_<id>",
  "authority_lease_id": "auth_<32hex>",
  "work_id": "wrk_<32hex>",
  "worker_id": "wrkr_<32hex>",
  "worker_lease_id": "lse_<32hex>",
  "admission_decision_id": "pdr_<32hex>",
  "trace_id": "trc_<32hex>"
}
```

Rules:

1. The envelope is immutable after Work creation.
2. The referenced AuthorityLease MUST still be revalidated immediately before every consequential action.
3. A valid `worker_lease_id` does not imply valid authority.
4. A valid `authority_lease_id` does not imply the caller owns the current Work lease.
5. Reauthorization creates a new AuthorityLease; the execution context records the actual lease used for a given admitted execution path and later actions must still revalidate current authority.
6. Consequential actions MUST carry a globally unique replay/action key.

## 8. `correlation/1.0`

`correlation/1.0` is a minimal cross-repo reference envelope. It is transportable across events, evidence, telemetry, continuity, audit, and UI projections.

```json
{
  "schema": "correlation/1.0",
  "tenant_id": "ten_<32hex>",
  "principal_id": "prn_<32hex>",
  "mission_id": "mis_<id>",
  "work_id": "wrk_<32hex>",
  "trace_id": "trc_<32hex>",
  "action_id": "act_<32hex>"
}
```

Possessing a correlation envelope MUST NOT grant execution authority.

## 9. Identifier grammar

### 9.1 New identifiers

New cross-repo identifiers SHOULD use:

```text
org_<32hex>
ten_<32hex>
prn_<32hex>
mis_<32hex>
auth_<32hex>
wrk_<32hex>
wrkr_<32hex>
lse_<32hex>
pdr_<32hex>
trc_<32hex>
act_<32hex>
```

### 9.2 Legacy compatibility

No mass historical rewrite is required.

- Existing valid IDs remain readable.
- Existing `identity/1.0` organization IDs remain readable under their current grammar.
- Existing Mission IDs accepted by `mission-state/1.0` remain readable.
- New cross-repo writes SHOULD use the canonical prefix + 32 lowercase hex grammar.
- Adapters MAY expose compatibility views, but compatibility views MUST NOT mint authority.

## 10. Versioning and compatibility

Contract families use:

```text
family/MAJOR.MINOR
```

Rules:

| Change | Required version treatment |
|---|---|
| Documentation only, no semantic effect | repository revision only |
| New optional non-security field | minor |
| New required field | major |
| Field removal | major |
| Meaning/semantics change | major |
| Identifier meaning change | major |
| Authority/admission behavior change | major |
| Security-sensitive enum expansion | major |
| Namespaced extension with no core behavior change | minor |

Cross-major compatibility MUST be explicit through an adapter. Consumers MUST fail closed on an unsupported major version.

Core contracts SHOULD be strict and provide a namespaced extension surface rather than accepting arbitrary unknown fields that could later acquire authority meaning.

## 11. Runtime lifecycle

V2.1 does not replace the existing canonical mission lifecycle.

The cross-repo runtime path is:

```text
Studio session
  ↓
Trust Gateway authentication
  ↓
Tenant resolution
  ↓
Principal resolution
  ↓
Mission READY
  ↓
AIE AuthorityLease
  ↓
Mission AUTHORIZED
  ↓
Trust Gateway admission
  ↓
PolicyDecisionRecord
  ↓
WORKS Work + execution-context/1.0
  ↓
Worker + WorkerLease
  ↓
Consequential action proposed
  ↓
Trust Gateway revalidates Principal + Mission + ACTIVE AuthorityLease
  ↓
Execute or deny
  ↓
Evidence
  ↓
Mission VERIFYING
  ↓
Verifier
  ↓
VERIFIED only on accepted evidence
```

The existing mission state contract remains authoritative for mission states. Failure causes such as `BUDGET_EXHAUSTED`, `LEASE_EXPIRED`, or `POLICY_DENIED` belong in failure/admission/work records rather than expanding the Mission state enum in V2.1.

## 12. Containment semantics

`revocation` and `budget_exhaustion` are containment conditions, not ordinary retryable recovery events.

Rules:

1. Revoked authority MUST stop subsequent consequential execution.
2. Budget exhaustion MUST stop execution under that budget envelope.
3. Neither condition MAY autonomously enter a retry loop that restores execution authority.
4. Reauthorization or rebudgeting requires a new explicit authority/budget decision as applicable.
5. Context transfer MAY carry stale or revoked references for continuity, but execution MUST deny them after revalidation.

## 13. Evidence binding

V2.1 preserves existing `evidence.schema/1.1` ownership and semantics.

The current `identity_chain` field is structurally broad. V2.1 defines the canonical identity-chain projection that evidence producers SHOULD emit when all references are available:

```json
{
  "identity_chain": {
    "organization_id": "org_<32hex>",
    "tenant_id": "ten_<32hex>",
    "principal_id": "prn_<32hex>",
    "mission_id": "mis_<id>",
    "authority_lease_id": "auth_<32hex>",
    "work_id": "wrk_<32hex>",
    "worker_id": "wrkr_<32hex>",
    "worker_lease_id": "lse_<32hex>",
    "admission_decision_id": "pdr_<32hex>",
    "trace_id": "trc_<32hex>"
  }
}
```

This projection does not silently upgrade `evidence.schema/1.1` itself. A future compatible evidence revision may formalize it through the normal contract process.

Evidence that an action happened is not proof that the action was authorized. Unauthorized execution MUST remain evidentiary and auditable rather than being discarded to preserve a green outcome.

## 14. Canonical causal chain

A consequential effect SHOULD be traceable through:

```text
External identity
  ↓
Principal
  ↓
Tenant
  ↓
Mission
  ↓
AuthorityLease
  ↓
PolicyDecisionRecord
  ↓
ExecutionContext
  ↓
Work
  ↓
WorkerLease
  ↓
Action
  ↓
External Effect
  ↓
EvidenceRecord / EvidenceBundle
  ↓
Verifier
  ↓
Verified Outcome
```

A missing resolvable link is a provenance gap and MUST NOT be hidden by a higher-level success label.

## 15. V2.1 invariants

The platform conformance suite SHALL encode at least these invariants:

```text
ID-01  Every consequential execution resolves a Tenant.
ID-02  Every consequential execution resolves a Principal.
ID-03  Principal belongs to the execution Tenant.
ID-04  Session identity cannot grant authority.
ID-05  Workspace membership cannot grant authority.
ID-06  Authority is ACTIVE at execution time.
ID-07  Revoked/expired authority never reaches execution.
ID-08  Reauthorization creates a new AuthorityLease.
ID-09  ExecutionContext is immutable after Work creation.
ID-10  Context transfer cannot mint or amplify authority.
ID-11  WorkItem does not imply executable Work.
ID-12  Budget exhaustion cannot auto-recover into execution.
ID-13  VERIFIED requires accepted verification evidence.
ID-14  Cross-tenant identifiers cannot escape isolation.
ID-15  Every consequential action has a globally unique replay/action key.
```

## 16. Golden Mission

V2.1 introduces platform-level `GOLDEN-MISSION-001`.

The happy path is:

```text
Studio authenticates human
  ↓
TG resolves Tenant + Principal
  ↓
Mission READY
  ↓
AIE AuthorityLease established
  ↓
TG admits execution and records PolicyDecisionRecord
  ↓
WORKS creates Work + execution-context/1.0
  ↓
Worker receives WorkerLease
  ↓
Worker proposes consequential action
  ↓
TG revalidates AuthorityLease at consequence time
  ↓
Action executes
  ↓
WORKS records evidence
  ↓
Verifier evaluates evidence
  ↓
Mission RUNNING → VERIFYING → VERIFIED
  ↓
Studio receives VERIFIED projection
```

The test passes only if required identifiers remain correctly correlated across the seam boundaries.

## 17. Adversarial conformance vectors

The initial platform suite SHALL include:

| Vector | Manipulation | Required outcome |
|---|---|---|
| `CTX-001` | valid complete chain | execute |
| `CTX-002` | unknown `principal_id` | reject |
| `CTX-003` | tenant-B Principal used in tenant A | reject |
| `CTX-004` | forged Studio Principal | reject |
| `CTX-005` | expired AuthorityLease | reject |
| `CTX-006` | AuthorityLease revoked after Work creation | reject next consequence |
| `CTX-007` | valid WorkerLease + invalid AuthorityLease | reject |
| `CTX-008` | valid AuthorityLease + invalid WorkerLease | WORKS rejects worker ownership |
| `CTX-009` | legacy `identity/1.0.runtime.lease_id` supplied as authority | reject |
| `CTX-010` | stale policy decision reused | revalidate or reject |
| `CTX-011` | duplicate `action_id` | idempotent/replay handling |
| `CTX-012` | budget exhausted | containment, no autonomous retry |
| `CTX-013` | evidence missing authority correlation | cannot promote to verified platform outcome |
| `CTX-014` | verifier INDETERMINATE | never VERIFIED |
| `CTX-015` | continuity transfer references revoked authority | transfer allowed, execution denied |
| `CTX-016` | Workspace membership only | no authority |
| `CTX-017` | cross-tenant Work lookup | fail closed without disclosure |
| `CTX-018` | authority revoked between admission and action | execution-time revalidation catches it |

`CTX-018` is the critical time-of-check/time-of-use platform vector:

```text
authorized at Work creation
    ≠
authorized at consequence time
```

## 18. Platform conformance architecture

V2.1 MUST NOT collapse all repository tests into one giant suite.

Governance owns platform vectors and expected outcomes. Domain repos own their implementations and local tests.

```text
after-graph-governance
  platform vectors + contract versions
        ↓
AIE adapter
TG adapter
WORKS adapter
Studio projection adapter
        ↓
platform-conformance runner
```

A repository can therefore be locally verified while the composed platform remains unverified.

```text
Repo Verified
Platform Unverified
```

This is a valid state and MUST be reportable without maturity inflation.

## 19. Migration strategy

V2.1 uses additive convergence, not a flag-day rewrite.

```text
PHASE 0  Contract registration only; no runtime behavior change
PHASE 1  Dual read: identity/1.0 + new canonical contracts
PHASE 2  New writes emit principal/1.0, tenant/1.0, execution-context/1.0
PHASE 3  Consequential execution requires the new execution binding
PHASE 4  Platform conformance gate required for platform release
PHASE 5  identity/1.0 becomes compatibility-read-only for new platform paths
```

Historical Work records remain readable. Compatibility projections MUST be marked and MUST NOT mint authority.

## 20. Scope of direct implementation

V2.1 directly changes only the repos needed to close the seam:

- `after-graph-governance`: contract registry, schemas, compatibility matrix, platform vectors, release gate definition.
- `aie`: Principal contract/adapters and authority-binding conformance.
- `trust-gateway`: Tenant/Principal resolution, admission binding, execution-time revalidation integration.
- `works-execution`: execution-context contract, worker-vs-authority lease separation, durable binding/evidence correlation.
- `studio`: projection/session boundary updates; no authority minting.
- `context-continuity`: reference transport rules; no authority amplification.

Other repositories consume only when they have a real dependency. V2.1 does not create ceremonial churn across all 19 repositories.

## 21. Non-goals

V2.1 does not:

- replace AIE authority semantics;
- replace Trust Gateway authentication/RBAC/policy enforcement;
- replace WORKS durable execution semantics;
- change the existing Mission state enum;
- merge AuthorityLease and WorkerLease;
- turn Workspace or Studio session into an authority root;
- create a new evidence family when `evidence.schema/1.1` already exists;
- rewrite historical IDs or Work records;
- promote research evidence into runtime authority;
- claim platform conformance from repository-local green tests alone;
- require all 19 repositories to change.

## 22. Acceptance criteria

V2.1 is complete only when all of the following are demonstrably true:

1. `identity/1.0` remains readable and unchanged in meaning.
2. `principal/1.0` is registered and owned by AIE.
3. `tenant/1.0` is registered and owned by Trust Gateway.
4. `execution-context/1.0` is registered and owned by WORKS.
5. `correlation/1.0` is registered and owned by governance.
6. AuthorityLease and WorkerLease are structurally and semantically distinct.
7. New consequential execution paths carry a canonical execution context.
8. Trust Gateway revalidates authority immediately before consequence.
9. Cross-tenant references fail closed without object-existence leakage.
10. Revocation and budget exhaustion remain containment events, not automatic recovery paths.
11. Evidence can correlate the execution chain without treating evidence as authority.
12. `GOLDEN-MISSION-001` passes end to end.
13. `CTX-001` through `CTX-018` are machine-executable and pass their required outcomes.
14. Platform conformance is a distinct release gate from repository-local CI.
15. Studio remains projection-only for authority semantics.
16. Context Continuity transports references without minting or amplifying authority.
17. Legacy compatibility works without a mass historical rewrite.
18. No implementation or documentation claim upgrades scientific, standards, or production maturity without corresponding evidence.

## 23. Follow-on sequence

V2.1 is the prerequisite for:

```text
V2.2 Mission Lifecycle Convergence
  ↓
V2.3 Evidence Envelope Formalization
  ↓
V2.4 Cross-Repo Golden Mission Expansion
  ↓
V2.5 Platform Conformance Suite
  ↓
V2.6 Studio Production Federation
```

V2.2 MUST NOT reinterpret V2.1 identity or authority semantics as part of lifecycle cleanup. Any such change requires a new explicit contract review.
