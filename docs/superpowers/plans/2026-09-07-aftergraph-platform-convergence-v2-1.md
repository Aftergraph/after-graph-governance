# Aftergraph Platform Convergence V2.1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the approved V2.1 Principal/Tenant architecture and immutable execution binding across Governance, AIE, Trust Gateway, WORKS, Studio and Context Continuity, then prove the composed seam with `GOLDEN-MISSION-001` and `CTX-001..CTX-020` without rewriting `identity/1.0` or inflating maturity claims.

**Architecture:** Ownership remains distributed. AIE owns Principal and AuthorityLease semantics. Trust Gateway resolves authenticated identities into tenant-scoped Principals and owns runtime admission/PolicyDecisionRecords. WORKS owns durable Work, WorkerLease and immutable ExecutionContext state. Governance registers contracts, owns `correlation/1.0`, and owns platform-conformance vectors. Studio and Context Continuity consume references but never mint authority. Consequential execution remains the intersection of AIE authority, Trust Gateway runtime admission and WORKS durable execution.

**Tech Stack:** JSON Schema Draft 2020-12, Python 3.11+, pytest, Node.js 22 + `node:test`, Go 1.24+, SQLite, Bash, jq, GitHub Actions / merge queue.

**Spec:** `docs/superpowers/specs/2026-09-07-aftergraph-platform-convergence-v2-1-canonical-identity-execution-context-design.md`

## Global Constraints

- Preserve `identity/1.0` byte/semantic compatibility. `identity/1.0.runtime.lease_id` never becomes an AIE AuthorityLease.
- Preserve the canonical Mission state enum. Cause codes remain in work/admission/failure records.
- `Workspace`, `Project`, `Space`, UI session, model, skill, plugin and repository membership never grant authority.
- AuthorityLease and WorkerLease remain structurally and semantically distinct.
- Every consequential action revalidates live authority immediately before consequence.
- Revocation and budget exhaustion are containment conditions, not automatic recovery loops.
- Context Continuity may transport references but never mint, extend or amplify authority.
- Evidence records what happened; evidence does not itself prove authorization.
- Unsupported major contract versions fail closed.
- Existing valid legacy IDs remain readable; new platform writes use the V2.1 prefix + 32-lowercase-hex grammar.
- Repository-local green CI is not platform conformance.
- No task upgrades standards, scientific, interoperability, production or deployment maturity from implementation evidence alone.
- Use one repository branch/PR per independently reviewable slice and respect merge-queue rules.

## Plan-time consistency finding

The approved spec currently places `WORKS creates Work + execution-context/1.0` before WorkerLease creation, while the approved ExecutionContext requires both `worker_id` and `worker_lease_id`. An immutable record cannot contain identifiers that do not exist yet.

Before Task 4 runtime code merges, amend the spec wording and Golden Mission ordering to this implementation-consistent sequence:

```text
WORKS creates Work
  ↓
WORKS grants WorkerLease
  ↓
WORKS creates immutable execution-context/1.0 for that admitted worker binding
  ↓
Consequential action may be proposed
```

A queued/unleased Work may therefore exist without an ExecutionContext. A consequential V2.1 action may not. Reauthorization under a new AuthorityLease creates a new immutable ExecutionContext with lineage to the prior context. This changes the binding point only; it does not transfer authority or ownership.

---

### Task 1: Register V2.1 families and implement Governance-owned `correlation/1.0`

**Repository:** `Aftergraph/after-graph-governance`

**Files:**
- Create: `docs/contracts/correlation/1.0.json`
- Create: `docs/contracts/platform-convergence-v2-1/registry.json`
- Create: `scripts/test_platform_convergence_v2_1_contracts.py`
- Modify: `docs/cross-repo-contracts.md`

Registry content:

```json
{
  "schema_version":"platform-convergence-v2-1/1.0",
  "families":[
    {"contract":"principal/1.0","owner":"aie","path":"spec/contracts/principal/1.0.json"},
    {"contract":"tenant/1.0","owner":"trust-gateway","path":"docs/contracts/tenant/1.0.json"},
    {"contract":"execution-context/1.0","owner":"works-execution","path":"contracts/schemas/execution-context.schema.json"},
    {"contract":"correlation/1.0","owner":"after-graph-governance","path":"docs/contracts/correlation/1.0.json"}
  ],
  "compatibility_families":["identity/1.0"]
}
```

`correlation/1.0` requires:

```text
schema = correlation/1.0
execution_context_id = ^ctx_[a-f0-9]{32}$
tenant_id            = ^ten_[a-f0-9]{32}$
principal_id         = ^prn_[a-f0-9]{32}$
mission_id           = non-empty legacy-compatible string
authority_lease_id   = ^auth_[a-f0-9]{32}$
work_id              = ^wrk_[a-f0-9]{32}$
admission_decision_id= ^pdr_[a-f0-9]{32}$
trace_id             = ^trc_[a-f0-9]{32}$
action_id            = ^act_[a-f0-9]{32}$
```

- [ ] RED: tests fail because registry/schema are absent.
- [ ] Assert exactly four V2.1 families with the approved owners/paths.
- [ ] Assert `identity/1.0` appears only as compatibility family.
- [ ] Assert wrong prefix, uppercase, short and non-hex IDs fail.
- [ ] GREEN: create strict JSON Schema with `additionalProperties:false` and update the human register without altering old rows.
- [ ] Do not copy Principal/Tenant/ExecutionContext runtime semantics into Governance.

Verification:

```bash
python -m unittest scripts.test_platform_convergence_v2_1_contracts -v
python -m json.tool docs/contracts/correlation/1.0.json >/dev/null
python -m json.tool docs/contracts/platform-convergence-v2-1/registry.json >/dev/null
```

Expected: PASS; `docs/contracts/frozen/identity.schema.json` remains untouched.

---

### Task 2: Add AIE-owned `principal/1.0` as a compatibility boundary

**Repository:** `Aftergraph/aie`

**Files:**
- Create: `spec/contracts/principal/1.0.json`
- Create: `src/aie_runtime/principal_contract.py`
- Create: `tests/test_principal_contract.py`
- Modify: `src/aie_runtime/__init__.py`
- Preserve in this task: `src/aie_runtime/engine.py` `Principal(id, type, identity_ref)` behavior

Schema required fields:

```text
schema       principal/1.0
principal_id ^prn_[a-f0-9]{32}$
tenant_id    ^ten_[a-f0-9]{32}$
type         human | agent | service | worker
identity_ref non-empty string
status       active | disabled
```

Adapter interface:

```python
def canonical_principal_type(runtime_type: str) -> str:
    mapping = {
        "human": "human",
        "agent": "agent",
        "bot": "agent",
        "service": "service",
        "worker": "worker",
    }
    if runtime_type not in mapping:
        raise ValueError("unsupported principal type")
    return mapping[runtime_type]


def principal_to_contract(*, principal, principal_id: str, tenant_id: str, status: str = "active") -> dict[str, str]:
    return {
        "schema": "principal/1.0",
        "principal_id": principal_id,
        "tenant_id": tenant_id,
        "type": canonical_principal_type(principal.type),
        "identity_ref": principal.identity_ref,
        "status": status,
    }
```

- [ ] RED: human/agent/service/worker mappings pass; legacy `bot` maps only to `agent`.
- [ ] RED: unknown runtime type fails closed.
- [ ] RED: malformed `prn_`/`ten_` IDs fail adapter validation.
- [ ] RED: output contains no capabilities, roles, approvals, budgets or authority grants.
- [ ] GREEN: implement adapter around existing Principal instead of forcing tenancy/UI concerns into the runtime dataclass.

Verification:

```bash
PYTHONPATH=src python -m pytest tests/test_principal_contract.py tests/test_identity_conformance.py tests/test_admission.py -q
```

---

### Task 3: Add durable canonical Tenant/Principal resolution in Trust Gateway

**Repository:** `Aftergraph/trust-gateway`

**Files:**
- Create: `docs/contracts/tenant/1.0.json`
- Create: `src/gateway/platform-identity.js`
- Create: `src/gateway/mounts/160-platform-identity.js`
- Create: `tests/platform-identity.test.js`
- Modify: `src/gateway/db.js`
- Reuse: `src/gateway/tenant-resolve.js`
- Reuse: `src/gateway/user-access.js`

Keep current local tenant slugs (`main`, etc.) intact and map them to canonical IDs.

Additive tables:

```sql
CREATE TABLE IF NOT EXISTS platform_tenant_bindings (
  local_tenant_id TEXT PRIMARY KEY,
  tenant_id TEXT NOT NULL UNIQUE,
  organization_id TEXT NOT NULL,
  created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS platform_principal_bindings (
  tenant_id TEXT NOT NULL,
  identity_ref TEXT NOT NULL,
  principal_id TEXT NOT NULL UNIQUE,
  principal_type TEXT NOT NULL,
  status TEXT NOT NULL,
  created_at TEXT NOT NULL,
  PRIMARY KEY (tenant_id, identity_ref)
);
```

Module interface:

```js
function ensureTenantBinding({ localTenantId, organizationId }) {}
function ensurePrincipalBinding({ tenantId, identityRef, principalType }) {}
function resolvePlatformIdentity(req, gw) {}
module.exports = { ensureTenantBinding, ensurePrincipalBinding, resolvePlatformIdentity };
```

Generate new IDs with `crypto.randomBytes(16).toString('hex')`. `TG_PLATFORM_ORG_ID` must match `^org_[a-f0-9]{32}$` before a new platform binding can be created. Missing configuration leaves legacy endpoints functional but makes the new platform projection fail closed.

`GET /v2/platform/identity` returns only organization, tenant, principal and principal type. It returns no AuthorityLease, capabilities, approval rights or execution token.

- [ ] RED: same local tenant → same canonical Tenant across restart.
- [ ] RED: same external identity + same Tenant → same Principal across restart.
- [ ] RED: same external identity + different Tenant → different Principal.
- [ ] RED: unknown/disabled/foreign Tenant preserves the existing 404 anti-enumeration posture.
- [ ] RED: missing/invalid `TG_PLATFORM_ORG_ID` cannot fabricate a canonical binding and does not break `/v2/whoami`.
- [ ] RED: response contains no authority-bearing field.
- [ ] GREEN: implement the mapping store and read-only mount on top of existing auth/tenant resolution.
- [ ] Preserve `tnt_<localTenant>_...` as legacy bearer transport; project it to canonical `ten_...` rather than renaming it in place.

Verification:

```bash
node --test tests/platform-identity.test.js tests/user-access.test.js tests/aie-revalidation.test.js
npm test
```

---

### Task 4: Add WORKS-owned immutable `execution-context/1.0` and API

**Repository:** `Aftergraph/works-execution`

**Precondition:** merge the plan-time spec binding-point clarification before this runtime slice.

**Files:**
- Create: `contracts/schemas/execution-context.schema.json`
- Modify: `contracts/gen_freeze.py`
- Regenerate: `contracts/manifest.json`, `contracts/manifest.sha256`, frozen evidence generated by the repo's existing freeze workflow
- Create: `packages/executioncontext/context.go`
- Create: `packages/executioncontext/context_test.go`
- Create: `services/work/store/execution_context.go`
- Create: `services/work/store/execution_context_test.go`
- Modify: `services/work/store/store.go`
- Create: `services/api/execution_context_handler.go`
- Create: `services/api/execution_context_handler_test.go`
- Modify: `services/api/api.go`

Go object:

```go
package executioncontext

type Context struct {
    Schema              string `json:"schema"`
    ID                  string `json:"execution_context_id"`
    PriorContextID      string `json:"prior_execution_context_id,omitempty"`
    OrganizationID      string `json:"organization_id"`
    TenantID            string `json:"tenant_id"`
    PrincipalID         string `json:"principal_id"`
    MissionID           string `json:"mission_id"`
    AuthorityLeaseID    string `json:"authority_lease_id"`
    WorkID              string `json:"work_id"`
    WorkerID            string `json:"worker_id"`
    WorkerLeaseID       string `json:"worker_lease_id"`
    AdmissionDecisionID string `json:"admission_decision_id"`
    TraceID             string `json:"trace_id"`
}
func (c Context) Validate() error
```

Store additions:

```go
CreateExecutionContext(ctx context.Context, c executioncontext.Context) error
GetExecutionContext(ctx context.Context, id string) (*executioncontext.Context, error)
ListExecutionContextsByWorkID(ctx context.Context, workID string) ([]executioncontext.Context, error)
```

Additive table and schema bump 11 → 12:

```sql
CREATE TABLE IF NOT EXISTS work_execution_contexts (
  id TEXT PRIMARY KEY,
  prior_context_id TEXT,
  work_id TEXT NOT NULL REFERENCES works(id) ON DELETE CASCADE,
  organization_id TEXT NOT NULL,
  tenant_id TEXT NOT NULL,
  principal_id TEXT NOT NULL,
  mission_id TEXT NOT NULL,
  authority_lease_id TEXT NOT NULL,
  worker_id TEXT NOT NULL,
  worker_lease_id TEXT NOT NULL,
  admission_decision_id TEXT NOT NULL,
  trace_id TEXT NOT NULL,
  created_at TEXT NOT NULL,
  UNIQUE(worker_lease_id, authority_lease_id, admission_decision_id)
);
```

API:

```text
POST /v1/works/{work_id}/execution-contexts
GET  /v1/execution-contexts/{execution_context_id}
```

POST body supplies `organization_id`, `tenant_id`, `principal_id`, `mission_id`, `authority_lease_id`, `worker_lease_id`, `admission_decision_id`, `trace_id`, and optional `prior_execution_context_id`. WORKS resolves `work_id` from the path and `worker_id` from the durable WorkerLease; clients cannot choose either field. WORKS generates the `ctx_<32hex>` ID.

- [ ] RED: context validation rejects swapped `lse_...`/`auth_...` prefixes.
- [ ] RED: POST rejects WorkerLease belonging to another Work without leaking foreign Work details.
- [ ] RED: POST derives WorkerID from the stored lease and ignores/rejects any client attempt to supply it.
- [ ] RED: duplicate/mutating write to an existing context is rejected.
- [ ] RED: queued/unleased Work may exist without context.
- [ ] RED: reauthorization creates a second `ctx_...` with `prior_context_id`; old row remains unchanged.
- [ ] RED: GET returns the immutable stored record needed by TG/Studio; no mutation route exists.
- [ ] GREEN: implement schema/store/API and additive migration.
- [ ] Keep historical Works readable with no backfill.

Verification:

```bash
go test ./packages/executioncontext ./services/work/store ./services/api
make test
make e2e
```

Expected: schema version 12; old DBs migrate additively.

---

### Task 5: Bind action-time AIE authority revalidation, WORKS execution context and TG PolicyDecisionRecord

**Repositories:** `Aftergraph/aie`, `Aftergraph/trust-gateway`

#### AIE files

- Modify: `src/aie_runtime/engine.py`
- Modify: `scripts/aie_revalidate_bridge.py`
- Modify: `tests/test_admission.py`
- Create: `tests/test_revalidation_result.py`

AIE remains the authority resolver, not the owner of TG policy decisions. Change revalidation additively to return the authority identity it actually validated:

```python
@dataclass(frozen=True)
class RevalidationResult:
    action_id: str
    authority_lease_id: str


def revalidate(self, action_id: str) -> RevalidationResult:
    request = self.state.admissions.get(action_id)
    if request is None:
        raise AIEError("AIE-AUTH-004")
    lease = self._resolve(request)
    # existing budget floor remains here
    self._emit("action.revalidated", actionId=action_id, leaseId=lease.id)
    return RevalidationResult(action_id=action_id, authority_lease_id=lease.id)
```

Bridge success output:

```json
{"ok":true,"action_id":"act_0123456789abcdef0123456789abcdef","authority_lease_id":"auth_0123456789abcdef0123456789abcdef"}
```

Legacy AIE actions/leasе IDs remain readable; the canonical prefix is required only on V2.1 platform paths.

#### Trust Gateway files

- Create: `src/gateway/works-context-client.js`
- Create: `src/gateway/policy-decision-record.js`
- Create: `tests/platform-execution-context.test.js`
- Modify: `src/gateway/aie-client.js`
- Modify: `src/gateway/server.js`
- Modify: `src/gateway/db.js`
- Modify: `tests/aie-revalidation.test.js`

Persist TG-owned PDRs:

```sql
CREATE TABLE IF NOT EXISTS platform_policy_decisions (
  id TEXT PRIMARY KEY,
  action_id TEXT NOT NULL,
  phase TEXT NOT NULL,
  tenant_id TEXT NOT NULL,
  principal_id TEXT NOT NULL,
  mission_id TEXT NOT NULL,
  authority_lease_id TEXT NOT NULL,
  execution_context_id TEXT,
  allow INTEGER NOT NULL,
  reason TEXT NOT NULL,
  decided_at TEXT NOT NULL
);
```

TG record shape:

```js
{
  id: 'pdr_0123456789abcdef0123456789abcdef',
  action_id: 'act_0123456789abcdef0123456789abcdef',
  phase: 'execution',
  tenant_id: 'ten_0123456789abcdef0123456789abcdef',
  principal_id: 'prn_0123456789abcdef0123456789abcdef',
  mission_id: 'mis_0123456789abcdef0123456789abcdef',
  authority_lease_id: 'auth_0123456789abcdef0123456789abcdef',
  execution_context_id: 'ctx_0123456789abcdef0123456789abcdef',
  allow: true,
  reason: 'admitted'
}
```

For V2.1 actions, TG receives `execution_context_id`, fetches the immutable context from WORKS, resolves current canonical Tenant/Principal locally, verifies those IDs match the context, then invokes AIE live revalidation. TG verifies AIE returned the same `authority_lease_id` recorded in the context. Only then does TG create the execution-phase PDR and dispatch. A mismatch at any seam denies before effect.

- [ ] RED AIE: revalidate returns exactly the live lease ID it checked.
- [ ] RED AIE: revoked/expired authority still fails before a success result.
- [ ] RED TG CTX-002/003/004: unknown, cross-tenant or forged Principal rejects before dispatch.
- [ ] RED TG CTX-005/006/018: expired/revoked authority, including revoke between admission and action, dispatch count remains zero.
- [ ] RED TG CTX-007: valid WorkerLease context + invalid AIE AuthorityLease rejects.
- [ ] RED TG CTX-008: WORKS refuses context creation for wrong WorkerLease/Work ownership.
- [ ] RED TG CTX-009: legacy `identity/1.0.runtime.lease_id` cannot populate `authority_lease_id` on V2.1 path.
- [ ] RED TG CTX-010: initial/stale admission decision cannot replace action-time revalidation.
- [ ] RED TG CTX-011: duplicate `action_id` uses existing replay/idempotency semantics and does not double-dispatch.
- [ ] RED TG CTX-020: a successful V2.1 action persists an execution-phase PDR and audit correlation; initial admission ID alone is insufficient.
- [ ] GREEN: thread context/AIE result/PDR through the action path while keeping legacy action behavior available until Phase 3.

Verification:

```bash
# AIE
PYTHONPATH=src python -m pytest tests/test_revalidation_result.py tests/test_admission.py tests/test_evidence.py -q

# Trust Gateway
node --test tests/platform-execution-context.test.js tests/aie-revalidation.test.js tests/authority-bridge.test.js tests/aie-client.test.js
npm test
```

---

### Task 6: Correlate WORKS evidence without changing `evidence.schema/1.1` semantics

**Repository:** `Aftergraph/works-execution`

**Files:**
- Modify: `services/evidence/bundle.go`
- Modify: `services/api/evidence_handler.go`
- Modify: `tests/evidence/bundle_test.go`
- Modify: `services/work/store/execution_context.go`
- Create: `services/work/store/execution_evidence_correlation_test.go`
- Preserve unchanged in V2.1: `contracts/schemas/evidence.schema.schema.json` family/version semantics

When a Work has V2.1 execution context and action-time PDR references, the evidence producer fills the existing broad `identity_chain` object with:

```text
organization_id
tenant_id
principal_id
mission_id
authority_lease_id
execution_context_id
work_id
worker_id
worker_lease_id
admission_decision_id
trace_id
```

- [ ] RED: V2.1 evidence bundle resolves the immutable context and action-time PDR reference.
- [ ] RED CTX-013: missing authority/context/action-time-decision correlation produces an explicit provenance-gap result and cannot satisfy platform VERIFIED.
- [ ] RED: denied/unauthorized attempts remain auditable and are not removed to manufacture a green bundle.
- [ ] RED: presence of authority/PDR references is never used as live authorization inside evidence code.
- [ ] GREEN: populate `identity_chain` from immutable stored references only.
- [ ] Do not tighten or rename `evidence.schema/1.1` in place; formal evidence schema revision remains V2.3.

Verification:

```bash
go test ./tests/evidence ./services/work/store ./services/api
make test
```

---

### Task 7: Carry V2.1 refs through Context Continuity without authority amplification

**Repository:** `Aftergraph/context-continuity`

**Files:**
- Modify: `schema/capsule.schema.json`
- Modify: `src/continuity.py`
- Modify: `tests/test_continuity.py`

Add optional `authority.references` to the existing v0alpha1 capsule. Do not make it required:

```text
tenant_id             ^ten_[a-f0-9]{32}$
principal_id          ^prn_[a-f0-9]{32}$
mission_id            non-empty string
authority_lease_id    ^auth_[a-f0-9]{32}$
execution_context_id  ^ctx_[a-f0-9]{32}$
trace_id              ^trc_[a-f0-9]{32}$
```

- [ ] RED: old capsules without refs remain valid and round-trip unchanged.
- [ ] RED: refs round-trip byte-for-byte.
- [ ] RED CTX-015: revoked AuthorityLease ref can be transported but is never marked active/executable.
- [ ] RED: compiler cannot mint AuthorityLease IDs, extend expiry, add capabilities or rewrite Tenant/Principal refs.
- [ ] GREEN: treat refs as opaque continuity context covered by existing integrity/provenance.

Verification:

```bash
python -m pytest tests/test_continuity.py tests/test_plugin.py -q
python -m json.tool schema/capsule.schema.json >/dev/null
```

---

### Task 8: Make Studio projection-only for canonical identity/execution context

**Repository:** `Aftergraph/studio`

**Files:**
- Modify: `src/integrations/trust-gateway.mjs`
- Modify: `src/integrations/works.mjs`
- Modify: `src/integrations/upstream-hub.mjs`
- Modify: `src/integrations/source-truth.mjs`
- Create: `tests/platform-identity-projection.test.mjs`
- Modify: `tests/api-client-polyrepo.test.mjs`

Read-only adapter methods:

```js
// trust-gateway.mjs
platformIdentity:()=>http.get('/v2/platform/identity')

// works.mjs
executionContext:id=>http.get(`/v1/execution-contexts/${encodeURIComponent(id)}`)
```

- [ ] RED: Studio projects TG-provided Tenant/Principal IDs and never derives them from workspace/session IDs.
- [ ] RED: Studio reads ExecutionContext but exposes no V2.1 mutation method for it.
- [ ] RED CTX-004: forged local Principal does not alter TG source truth or authorize action.
- [ ] RED CTX-016: workspace membership alone exposes no execution-authority method.
- [ ] RED: source-truth validation recognizes the four V2.1 family owners while preserving `WorkItem != Work` and evidence-gated VERIFIED.
- [ ] GREEN: project upstream state only; consequential writes remain delegated to canonical owners.
- [ ] Update `UPSTREAM_REVISIONS` only from exact merged upstream SHAs during implementation, never from speculative values.

Verification:

```bash
node --test tests/platform-identity-projection.test.mjs tests/api-client-polyrepo.test.mjs tests/fullstack-api-v4.test.mjs
npm test
npm run verify:polyrepo
```

---

### Task 9: Implement `GOLDEN-MISSION-001` and CTX-001..CTX-020 platform vectors

**Repository:** `Aftergraph/after-graph-governance`

**Files:**
- Create: `docs/contracts/platform-convergence-v2-1/vectors.json`
- Create: `scripts/run_platform_conformance_v2_1.py`
- Create: `scripts/test_platform_conformance_v2_1.py`
- Create: `docs/PLATFORM-CONFORMANCE-V2.1.md`

Vector shape:

```json
{
  "id":"CTX-018",
  "class":"authority-toctou",
  "given":"authority revoked after initial admission and before consequential action",
  "expect":"reject-before-effect",
  "required_evidence":["initial_admission","revocation","action_time_revalidation","no_external_effect"]
}
```

The file contains exactly 21 vector IDs: `GOLDEN-MISSION-001` plus `CTX-001` through `CTX-020`. The runner consumes machine-readable results from checked-out exact repo revisions; Governance does not reimplement domain semantics.

Result shape:

```json
{
  "schema":"platform-conformance-result/1.0",
  "suite":"platform-convergence-v2.1",
  "status":"PASS",
  "vectors_total":21,
  "vectors_passed":21,
  "repository_results":{},
  "evidence_refs":[]
}
```

- [ ] RED: missing/duplicate vector ID fails.
- [ ] RED: PASS without required evidence keys fails.
- [ ] RED: CTX-007/008 independently exercise AuthorityLease vs WorkerLease.
- [ ] RED: CTX-009 rejects legacy runtime lease as authority.
- [ ] RED: CTX-011 validates replay/idempotency.
- [ ] RED: CTX-012 validates budget containment/no auto-retry.
- [ ] RED: CTX-014 validates INDETERMINATE never becomes VERIFIED.
- [ ] RED: CTX-017 validates cross-tenant Work lookup without existence leakage.
- [ ] RED: CTX-019 validates immutable old context + new lineage binding.
- [ ] RED: CTX-020 validates action-time PDR provenance.
- [ ] GREEN: implement adapter-driven runner and deterministic reducer.
- [ ] Keep `--check-only` suite-shape verification clearly separate from composed functional conformance.

Verification:

```bash
python -m unittest scripts.test_platform_conformance_v2_1 -v
python scripts/run_platform_conformance_v2_1.py --check-only docs/contracts/platform-convergence-v2-1/vectors.json
```

---

### Task 10: Roll out by compatibility phase and gate the platform release

**Primary repository:** `Aftergraph/after-graph-governance`; participating repos update their own runbooks/status only after verified merges.

**Files:**
- Modify: `docs/PLATFORM-CONFORMANCE-V2.1.md`
- Add a Governance CI workflow only if it can run without embedding runtime credentials.

Fixed phases:

```text
PHASE 0  contract registration only
PHASE 1  dual read: identity/1.0 + V2.1 contracts
PHASE 2  new writes emit canonical Principal/Tenant/ExecutionContext refs
PHASE 3  consequential V2.1 actions require ExecutionContext + action-time PDR
PHASE 4  all 21 platform vectors PASS for V2.1 platform release
PHASE 5  identity/1.0 is compatibility-read-only on new platform paths
```

- [ ] Gate Phase 1 on legacy AIE/TG/WORKS tests.
- [ ] Gate Phase 2 on stable TG bindings + WORKS schema-12 migration evidence.
- [ ] Gate Phase 3 on context/AIE/PDR action-time enforcement and CTX-005..010/018..020.
- [ ] Gate Phase 4 on all 21 vectors at one exact compatible revision set.
- [ ] Gate Phase 5 on measured legacy reads for historical Work/identity records.
- [ ] Report `Repo Verified / Platform Unverified` whenever local repos are green but the composed suite is not.
- [ ] Never label V2.1 production-ready solely from platform conformance; deployment evidence is separate.

Final verification bundle records exact SHAs for:

```text
after-graph-governance
aie
trust-gateway
works-execution
studio
context-continuity
```

plus the exact platform-conformance result produced against those revisions.

## Merge Order

1. Governance contract registration + `correlation/1.0`.
2. AIE `principal/1.0` adapter.
3. Trust Gateway canonical Tenant/Principal resolution.
4. WORKS immutable ExecutionContext + schema 12/API.
5. AIE live revalidation result + TG WORKS-context/PDR enforcement.
6. WORKS evidence correlation.
7. Context Continuity reference transport.
8. Studio projection-only adoption.
9. Governance Golden Mission / CTX suite.
10. Compatibility-phase release gate.

Branches may be prepared in parallel, but consumers do not merge ahead of their owner contract/source seam.

## Definition of Done

- [ ] Four V2.1 families registered with approved owners.
- [ ] `identity/1.0` readable and semantically unchanged.
- [ ] Canonical Tenant/Principal mappings stable across restart.
- [ ] AuthorityLease/WorkerLease separation executable, not prose-only.
- [ ] Every consequential V2.1 action carries immutable ExecutionContext and execution-phase PDR.
- [ ] Reauthorization creates a new context with lineage.
- [ ] Evidence exposes provenance gaps rather than hiding them.
- [ ] Context Continuity transports refs without authority amplification.
- [ ] Studio remains projection/interaction surface, not authority source.
- [ ] `GOLDEN-MISSION-001` + CTX-001..CTX-020 pass against one exact six-repo revision set.
- [ ] Platform conformance remains separate from repo CI, standards maturity, scientific validity and production approval.
