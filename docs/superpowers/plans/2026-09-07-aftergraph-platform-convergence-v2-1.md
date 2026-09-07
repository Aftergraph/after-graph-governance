# Aftergraph Platform Convergence V2.1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the approved V2.1 canonical Principal/Tenant identity architecture and immutable execution binding across Governance, AIE, Trust Gateway, WORKS, Studio and Context Continuity, then prove the composed seam with `GOLDEN-MISSION-001` and `CTX-001..CTX-020` without rewriting `identity/1.0` or inflating maturity claims.

**Architecture:** Ownership stays distributed. AIE owns Principal and AuthorityLease semantics; Trust Gateway resolves authenticated identities into tenant-scoped Principals and performs runtime admission/revalidation; WORKS owns durable Work, WorkerLease and immutable execution-context bindings; Governance registers contracts and owns correlation/platform-conformance vectors; Studio and Context Continuity consume references but never mint authority. Consequential execution remains the intersection of AIE authority, Trust Gateway runtime admission and WORKS durable execution.

**Tech Stack:** JSON Schema Draft 2020-12, Python 3.11+, pytest, Node.js 22 + `node:test`, Go 1.24+, SQLite, Bash, jq, GitHub Actions / merge queue.

**Spec:** `docs/superpowers/specs/2026-09-07-aftergraph-platform-convergence-v2-1-canonical-identity-execution-context-design.md`

## Global Constraints

- Preserve `identity/1.0` byte/semantic compatibility. Do not reinterpret `identity/1.0.runtime.lease_id` as an AIE AuthorityLease.
- Preserve the canonical Mission state enum. V2.1 does not add `BUDGET_EXHAUSTED`, `LEASE_EXPIRED`, `POLICY_DENIED`, or other cause codes as Mission states.
- `Workspace`, `Project`, `Space`, UI session, model, skill, plugin and repository membership never grant authority.
- `AuthorityLease` and `WorkerLease` remain structurally and semantically distinct.
- Every consequential action must be revalidated against live authority immediately before consequence.
- Revocation and budget exhaustion are containment conditions, not automatic recovery loops.
- Context Continuity may transport references but must never mint, extend or amplify authority.
- Evidence records what happened; evidence does not itself prove authorization.
- Unsupported major contract versions fail closed.
- Existing valid legacy IDs remain readable; new platform writes use the V2.1 prefix + 32-lowercase-hex grammar.
- Repository-local green CI is not platform conformance.
- No task may upgrade standards, scientific, interoperability, production or deployment maturity from implementation evidence alone.
- Use one repository branch/PR per independently reviewable slice. Respect each repository's rules and merge queue.

## Plan-time consistency finding

The approved spec currently shows `WORKS creates Work + execution-context/1.0` before the WorkerLease exists while `execution-context/1.0` requires both `worker_id` and `worker_lease_id`. An immutable object cannot contain identifiers that do not exist yet.

Before Task 4 code is merged, amend the spec wording and Golden Mission ordering to the only implementation-consistent interpretation that preserves every approved invariant:

```text
WORKS creates Work
  ↓
WORKS grants WorkerLease
  ↓
WORKS creates immutable execution-context/1.0 for that admitted worker binding
  ↓
Consequential action may be proposed
```

A Work may therefore exist without an ExecutionContext while it is queued/unleased. A consequential action may not. Reauthorization under a new AuthorityLease creates a new immutable ExecutionContext for the continued execution path. This is a clarification of the binding point, not a transfer of authority or ownership.

---

### Task 1: Register V2.1 contract families and own `correlation/1.0`

**Repository:** `Aftergraph/after-graph-governance`

**Files:**
- Create: `docs/contracts/correlation/1.0.json`
- Create: `docs/contracts/platform-convergence-v2-1/registry.json`
- Create: `scripts/test_platform_convergence_v2_1_contracts.py`
- Modify: `docs/cross-repo-contracts.md`

**Contract registry interface:**

```json
{
  "schema_version": "platform-convergence-v2-1/1.0",
  "families": [
    {"contract":"principal/1.0","owner":"aie","path":"spec/contracts/principal/1.0.json"},
    {"contract":"tenant/1.0","owner":"trust-gateway","path":"docs/contracts/tenant/1.0.json"},
    {"contract":"execution-context/1.0","owner":"works-execution","path":"contracts/schemas/execution-context.schema.json"},
    {"contract":"correlation/1.0","owner":"after-graph-governance","path":"docs/contracts/correlation/1.0.json"}
  ],
  "compatibility_families": ["identity/1.0"]
}
```

**`correlation/1.0` required fields:**

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://aftergraph.dev/contracts/correlation/1.0.json",
  "type": "object",
  "additionalProperties": false,
  "required": ["schema","execution_context_id","tenant_id","principal_id","mission_id","authority_lease_id","work_id","admission_decision_id","trace_id","action_id"],
  "properties": {
    "schema": {"const": "correlation/1.0"},
    "execution_context_id": {"type":"string","pattern":"^ctx_[a-f0-9]{32}$"},
    "tenant_id": {"type":"string","pattern":"^ten_[a-f0-9]{32}$"},
    "principal_id": {"type":"string","pattern":"^prn_[a-f0-9]{32}$"},
    "mission_id": {"type":"string","minLength":1},
    "authority_lease_id": {"type":"string","pattern":"^auth_[a-f0-9]{32}$"},
    "work_id": {"type":"string","pattern":"^wrk_[a-f0-9]{32}$"},
    "admission_decision_id": {"type":"string","pattern":"^pdr_[a-f0-9]{32}$"},
    "trace_id": {"type":"string","pattern":"^trc_[a-f0-9]{32}$"},
    "action_id": {"type":"string","pattern":"^act_[a-f0-9]{32}$"}
  }
}
```

- [ ] RED: add `scripts/test_platform_convergence_v2_1_contracts.py` that fails because registry/schema files do not exist.
- [ ] Test that the registry has exactly four V2.1 canonical families and exactly the approved owners/paths above.
- [ ] Test that `identity/1.0` appears only under `compatibility_families`, not as a rewritten V2.1 family.
- [ ] Test every new ID pattern rejects uppercase, short, wrong-prefix and non-hex examples.
- [ ] GREEN: add `correlation/1.0`, the registry file and update `docs/cross-repo-contracts.md` with the four new families while preserving all existing rows.
- [ ] Keep Governance as registry/compatibility owner only; do not copy Principal/Tenant/ExecutionContext semantics into Governance-owned runtime code.

Verification:

```bash
python -m unittest scripts.test_platform_convergence_v2_1_contracts -v
python -m json.tool docs/contracts/correlation/1.0.json >/dev/null
python -m json.tool docs/contracts/platform-convergence-v2-1/registry.json >/dev/null
```

Expected: all tests PASS; the old `docs/contracts/frozen/identity.schema.json` content is untouched.

---

### Task 2: Add AIE-owned `principal/1.0` without rewriting the runtime Principal

**Repository:** `Aftergraph/aie`

**Files:**
- Create: `spec/contracts/principal/1.0.json`
- Create: `src/aie_runtime/principal_contract.py`
- Create: `tests/test_principal_contract.py`
- Modify: `src/aie_runtime/__init__.py`
- Preserve: `src/aie_runtime/engine.py` `Principal(id, type, identity_ref)` public behavior in this task

**Schema shape:**

```json
{
  "$schema":"https://json-schema.org/draft/2020-12/schema",
  "$id":"https://aftergraph.dev/contracts/principal/1.0.json",
  "type":"object",
  "additionalProperties":false,
  "required":["schema","principal_id","tenant_id","type","identity_ref","status"],
  "properties":{
    "schema":{"const":"principal/1.0"},
    "principal_id":{"type":"string","pattern":"^prn_[a-f0-9]{32}$"},
    "tenant_id":{"type":"string","pattern":"^ten_[a-f0-9]{32}$"},
    "type":{"enum":["human","agent","service","worker"]},
    "identity_ref":{"type":"string","minLength":1},
    "status":{"enum":["active","disabled"]}
  }
}
```

**Adapter interface:**

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

- [ ] RED: test valid human/agent/service/worker mappings and explicit legacy `bot → agent` mapping.
- [ ] RED: test unsupported runtime type fails closed rather than being passed through.
- [ ] RED: test `identity_ref` is preserved but the adapter emits no capabilities, roles, approvals or authority fields.
- [ ] RED: test malformed `prn_` and `ten_` identifiers are rejected by adapter validation.
- [ ] GREEN: implement the adapter as a compatibility boundary around the existing runtime Principal rather than adding tenant/UI concerns to `engine.Principal`.
- [ ] Export the adapter through `aie_runtime.__init__` only after its tests pass.

Verification:

```bash
PYTHONPATH=src python -m pytest tests/test_principal_contract.py tests/test_identity_conformance.py tests/test_admission.py -q
```

Expected: new principal tests PASS and existing identity/admission tests remain green.

---

### Task 3: Give Trust Gateway canonical Tenant/Principal resolution with durable legacy bindings

**Repository:** `Aftergraph/trust-gateway`

**Files:**
- Create: `docs/contracts/tenant/1.0.json`
- Create: `src/gateway/platform-identity.js`
- Create: `src/gateway/mounts/160-platform-identity.js`
- Create: `tests/platform-identity.test.js`
- Modify: `src/gateway/db.js` or its existing migration owner to create two additive mapping tables
- Reuse: `src/gateway/tenant-resolve.js`
- Reuse: `src/gateway/user-access.js`

**Do not replace existing tenant slugs.** Keep the current local `main`/slug tenant IDs and map them to new canonical IDs.

**Additive SQLite mapping tables:**

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

**Module interface:**

```js
function ensureTenantBinding({ localTenantId, organizationId }) {}
function ensurePrincipalBinding({ tenantId, identityRef, principalType }) {}
function resolvePlatformIdentity(req, gw) {}
module.exports = { ensureTenantBinding, ensurePrincipalBinding, resolvePlatformIdentity };
```

ID generation uses `crypto.randomBytes(16).toString('hex')` with the approved prefixes. `TG_PLATFORM_ORG_ID` supplies the administrative Organization ID for legacy local tenants; it must match `^org_[a-f0-9]{32}$` before a new platform binding is created. Legacy endpoints continue to work when this setting is absent, but the new platform-identity projection fails closed and does not fabricate an Organization ID.

`GET /v2/platform/identity` returns only:

```json
{
  "schema":"platform-identity-projection/1.0",
  "organization_id":"org_0123456789abcdef0123456789abcdef",
  "tenant_id":"ten_0123456789abcdef0123456789abcdef",
  "principal_id":"prn_0123456789abcdef0123456789abcdef",
  "principal_type":"human"
}
```

It MUST NOT return AuthorityLease, capabilities, approval rights or an execution token.

- [ ] RED: same local tenant maps to the same canonical `tenant_id` across gateway restarts.
- [ ] RED: same external identity in the same tenant maps to the same Principal across restarts.
- [ ] RED: same external identity in two tenants maps to two different Principals.
- [ ] RED: unknown/disabled/cross-tenant lookups preserve existing 404 anti-enumeration behavior from `tenant-resolve.js`.
- [ ] RED: missing/invalid `TG_PLATFORM_ORG_ID` prevents a new canonical binding but does not break legacy `/v2/whoami`.
- [ ] RED: platform identity response has no authority-bearing fields.
- [ ] GREEN: implement mapping store and read-only mount using the existing authenticated bot/session identity and existing tenant resolver.
- [ ] Do not replace the existing `tnt_<localTenant>_` bearer prefix in V2.1; it remains a legacy transport/auth claim and is projected to canonical `ten_...` at the new boundary.

Verification:

```bash
node --test tests/platform-identity.test.js tests/user-access.test.js tests/aie-revalidation.test.js
npm test
```

Expected: legacy tenant/auth behavior is unchanged; canonical platform identity is additive.

---

### Task 4: Add WORKS-owned immutable `execution-context/1.0` at the WorkerLease binding point

**Repository:** `Aftergraph/works-execution`

**Precondition:** apply the plan-time spec clarification above before merging this runtime slice.

**Files:**
- Create: `contracts/schemas/execution-context.schema.json`
- Modify: `contracts/gen_freeze.py`
- Regenerate: contract manifest/hash artifacts using the repository's existing freeze workflow
- Create: `packages/executioncontext/context.go`
- Create: `packages/executioncontext/context_test.go`
- Create: `services/work/store/execution_context.go`
- Create: `services/work/store/execution_context_test.go`
- Modify: `services/work/store/store.go`
- Modify: `services/work/store/leases.go`
- Modify: `services/work/store/leases_test.go`

**Go domain interface:**

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

**Store interface additions:**

```go
CreateExecutionContext(ctx context.Context, c executioncontext.Context) error
GetExecutionContext(ctx context.Context, id string) (*executioncontext.Context, error)
ActiveExecutionContextByLease(ctx context.Context, workerLeaseID string) (*executioncontext.Context, error)
```

**Additive SQLite table and schema bump:**

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

Bump `SchemaVersion` from 11 to 12 only after the migration test is RED and then GREEN.

- [ ] RED: `Context.Validate` rejects WorkerLease values in `authority_lease_id` and AuthorityLease values in `worker_lease_id` by prefix grammar.
- [ ] RED: store rejects mutation/overwrite of an existing context ID.
- [ ] RED: a queued Work without a WorkerLease may exist without an ExecutionContext.
- [ ] RED: a consequential worker execution path cannot proceed without an active WorkerLease plus matching ExecutionContext.
- [ ] RED: `CTX-007` valid WorkerLease + invalid AuthorityLease binding is representable but cannot be treated as authorization.
- [ ] RED: `CTX-008` valid AuthorityLease + wrong WorkerLease is rejected by WORKS ownership checks.
- [ ] RED: reauthorization creates a new `ctx_...` row with `prior_context_id`; the old row remains byte-identical.
- [ ] GREEN: materialize the context immediately after WORKS grants/binds the concrete WorkerLease for an admitted execution, not while the Work is merely queued.
- [ ] Keep existing Work IDs/rows readable with no historical backfill.

Verification:

```bash
go test ./packages/executioncontext ./services/work/store
make test
make e2e
```

Expected: schema migration reaches 12, old databases migrate additively, historical Works remain readable.

---

### Task 5: Make AIE/TG action-time PolicyDecisionRecord correlation first-class

**Repositories:** `Aftergraph/aie`, then `Aftergraph/trust-gateway`

#### AIE files

- Modify: `src/aie_runtime/engine.py`
- Modify: `src/aie_runtime/store.py`
- Modify: `src/aie_runtime/persistent_state.py`
- Modify: `scripts/aie_revalidate_bridge.py`
- Create: `tests/test_policy_decision_record.py`
- Modify: `tests/test_admission.py`

**AIE runtime record:**

```python
@dataclass(frozen=True)
class PolicyDecisionRecord:
    id: str
    action_id: str
    phase: str
    principal_id: str
    mission_id: str
    authority_lease_id: str
    allow: bool
    decided_at: datetime
```

`phase` is exactly `"admission"` or `"execution"` in V2.1.

Change `AdmissionOutcome` additively:

```python
@dataclass(frozen=True)
class AdmissionOutcome:
    status: str
    error_code: str | None = None
    decision_id: str | None = None
```

Change `AdmissionEngine.revalidate(action_id)` to return the newly persisted execution-phase `PolicyDecisionRecord` after live `_resolve()` and budget checks succeed. On fail-closed authority/budget rejection, emit/persist a denial record only when the request and governing authority reference are safely resolvable; never invent a Principal/Mission/Lease to populate a record.

Bridge success output becomes:

```json
{"ok":true,"decision_id":"pdr_0123456789abcdef0123456789abcdef"}
```

#### Trust Gateway files

- Modify: `src/gateway/aie-client.js`
- Modify: `src/gateway/server.js`
- Modify: `tests/aie-revalidation.test.js`
- Add or extend the existing audit vocabulary documentation for action-time decision correlation

`aie-client.revalidate()` success becomes:

```js
{ ok: true, decision_id: 'pdr_0123456789abcdef0123456789abcdef' }
```

- [ ] RED AIE: admission produces an admission-phase PDR with unique `pdr_` ID.
- [ ] RED AIE: every successful execution-time revalidation produces a distinct execution-phase PDR.
- [ ] RED AIE: duplicate `action_id` preserves replay semantics and does not silently overwrite prior decision history.
- [ ] RED TG: malformed/missing `decision_id` from bridge is fail-closed as `AIE_UNREACHABLE`/invalid bridge output rather than accepted.
- [ ] RED TG: CTX-018 revoke authority between admission and action; dispatch count stays zero and the failed consequence is auditable.
- [ ] RED TG: successful dispatch writes the action-time `decision_id` into the action audit/correlation record.
- [ ] RED TG: CTX-020 proves initial admission ID alone is insufficient for a consequential action's complete provenance.
- [ ] GREEN: thread decision IDs through the existing bridge/client/action path without moving policy ownership out of TG or authority semantics out of AIE.

Verification:

```bash
# AIE
PYTHONPATH=src python -m pytest tests/test_policy_decision_record.py tests/test_admission.py tests/test_evidence.py -q

# Trust Gateway
node --test tests/aie-revalidation.test.js tests/authority-bridge.test.js tests/aie-client.test.js
npm test
```

---

### Task 6: Correlate WORKS evidence without turning evidence into authority

**Repository:** `Aftergraph/works-execution`

**Files:**
- Modify: `services/work/store/execution_context.go`
- Modify: `services/work/store/events.go` or the current event-record owner used by the execution path
- Modify: the existing evidence bundle producer under `services/evidence/` / `packages/evidence` if present at implementation checkout
- Modify: `docs/standards/schemas/evidence-bundle.schema.json` only if the change is a compatible optional projection; do not relabel `evidence.schema/1.1`
- Create: `services/work/store/execution_evidence_correlation_test.go`

**Required projection when all references are available:**

```json
{
  "identity_chain": {
    "organization_id":"org_0123456789abcdef0123456789abcdef",
    "tenant_id":"ten_0123456789abcdef0123456789abcdef",
    "principal_id":"prn_0123456789abcdef0123456789abcdef",
    "mission_id":"mis_0123456789abcdef0123456789abcdef",
    "authority_lease_id":"auth_0123456789abcdef0123456789abcdef",
    "execution_context_id":"ctx_0123456789abcdef0123456789abcdef",
    "work_id":"wrk_0123456789abcdef0123456789abcdef",
    "worker_id":"wrkr_0123456789abcdef0123456789abcdef",
    "worker_lease_id":"lse_0123456789abcdef0123456789abcdef",
    "admission_decision_id":"pdr_0123456789abcdef0123456789abcdef",
    "trace_id":"trc_0123456789abcdef0123456789abcdef"
  }
}
```

- [ ] RED: evidence generated from a V2.1 execution can resolve the immutable ExecutionContext and action-time PDR.
- [ ] RED: CTX-013 missing authority/execution-context correlation yields a provenance-gap result and cannot be labeled platform VERIFIED.
- [ ] RED: unauthorized/denied execution attempts remain auditable evidence and are not dropped to create a green bundle.
- [ ] RED: evidence code never treats presence of `authority_lease_id` or `decision_id` as a substitute for live authorization.
- [ ] GREEN: populate identity-chain correlation from immutable stored references only.
- [ ] Preserve existing `evidence.schema/1.1` family/version semantics; a formal evidence-contract revision remains V2.3 work.

Verification:

```bash
go test ./services/work/store ./services/evidence/... ./packages/evidence/... 2>/dev/null || go test ./services/work/store ./...
make test
```

Expected: correlation is available for V2.1 paths; legacy evidence remains readable.

---

### Task 7: Carry V2.1 references through Context Continuity without authority amplification

**Repository:** `Aftergraph/context-continuity`

**Files:**
- Modify: `schema/capsule.schema.json`
- Modify: `src/continuity.py`
- Modify: `tests/test_continuity.py`

Add an **optional** `references` object inside the existing `authority` object; do not make it required for existing v0alpha1 capsules:

```json
{
  "references": {
    "type":"object",
    "additionalProperties":false,
    "properties": {
      "tenant_id":{"type":"string","pattern":"^ten_[a-f0-9]{32}$"},
      "principal_id":{"type":"string","pattern":"^prn_[a-f0-9]{32}$"},
      "mission_id":{"type":"string","minLength":1},
      "authority_lease_id":{"type":"string","pattern":"^auth_[a-f0-9]{32}$"},
      "execution_context_id":{"type":"string","pattern":"^ctx_[a-f0-9]{32}$"},
      "trace_id":{"type":"string","pattern":"^trc_[a-f0-9]{32}$"}
    }
  }
}
```

- [ ] RED: existing capsules without `authority.references` remain valid/round-trip unchanged.
- [ ] RED: a capsule can carry the approved references byte-for-byte.
- [ ] RED: CTX-015 carries a revoked authority reference successfully as context, while continuity code never marks it active or executable.
- [ ] RED: continuity compilation cannot create a new AuthorityLease ID, extend expiry, add capabilities, or rewrite tenant/principal IDs.
- [ ] GREEN: preserve references as opaque authority context with existing integrity/provenance coverage.
- [ ] Document in code comments/tests: transport success is not execution authorization.

Verification:

```bash
python -m pytest tests/test_continuity.py tests/test_plugin.py -q
python -m json.tool schema/capsule.schema.json >/dev/null
```

---

### Task 8: Make Studio project canonical identity/execution state without minting it

**Repository:** `Aftergraph/studio`

**Files:**
- Modify: `src/integrations/trust-gateway.mjs`
- Modify: `src/integrations/works.mjs`
- Modify: `src/integrations/upstream-hub.mjs`
- Modify: `src/integrations/source-truth.mjs`
- Create: `tests/platform-identity-projection.test.mjs`
- Modify: `tests/api-client-polyrepo.test.mjs`

Add read-only adapter methods:

```js
// trust-gateway.mjs
platformIdentity:()=>http.get('/v2/platform/identity')

// works.mjs
executionContext:id=>http.get(`/v1/execution-contexts/${encodeURIComponent(id)}`)
```

`upstream-hub.sync()` may project returned canonical IDs into Studio state, but it MUST NOT generate `prn_`, `ten_`, `auth_`, `ctx_`, `pdr_` or `lse_` identifiers locally.

- [ ] RED: Studio displays/projects TG-provided `tenant_id` and `principal_id` without deriving them from workspace/session IDs.
- [ ] RED: Studio reads WORKS execution-context state but cannot create or mutate it through the V2.1 adapter.
- [ ] RED: CTX-004 forged local `principal_id` does not alter the value returned by TG and cannot authorize an action.
- [ ] RED: CTX-016 workspace membership alone exposes no execution-authority method.
- [ ] RED: source-truth validation recognizes the four V2.1 families by owner while preserving `WorkItem != Work` and evidence-gated VERIFIED rules.
- [ ] GREEN: keep UI/session objects as projections; consequential writes continue through canonical owning services.
- [ ] Update `UPSTREAM_REVISIONS` only from the exact merged upstream commits when this slice is implemented; do not hand-write speculative future SHAs into the plan/spec.

Verification:

```bash
node --test tests/platform-identity-projection.test.mjs tests/api-client-polyrepo.test.mjs tests/fullstack-api-v4.test.mjs
npm test
npm run verify:polyrepo
```

---

### Task 9: Implement Governance `GOLDEN-MISSION-001` + `CTX-001..CTX-020` platform vectors

**Repository:** `Aftergraph/after-graph-governance`

**Files:**
- Create: `docs/contracts/platform-convergence-v2-1/vectors.json`
- Create: `scripts/run_platform_conformance_v2_1.py`
- Create: `scripts/test_platform_conformance_v2_1.py`
- Create: `docs/PLATFORM-CONFORMANCE-V2.1.md`

**Vector record shape:**

```json
{
  "id":"CTX-018",
  "class":"authority-toctou",
  "given":"authority revoked after initial admission and before consequential action",
  "expect":"reject-before-effect",
  "required_evidence":["initial_admission","revocation","action_time_revalidation","no_external_effect"]
}
```

`vectors.json` contains exactly `GOLDEN-MISSION-001` plus CTX-001 through CTX-020. The runner consumes machine-readable adapter results from checked-out sibling repos or explicit command paths; it does not reimplement AIE/TG/WORKS semantics inside Governance.

Runner result shape:

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

- [ ] RED: fail if any of the 21 required vector IDs is missing or duplicated.
- [ ] RED: fail if a vector reports PASS without its required evidence keys.
- [ ] RED: CTX-007/008 prove WorkerLease and AuthorityLease are independently enforced.
- [ ] RED: CTX-009 proves legacy `identity/1.0.runtime.lease_id` cannot satisfy authority.
- [ ] RED: CTX-011 proves replay/idempotency handling.
- [ ] RED: CTX-012 proves budget exhaustion containment with no auto-retry.
- [ ] RED: CTX-014 proves INDETERMINATE verifier output cannot yield VERIFIED.
- [ ] RED: CTX-017 proves cross-tenant Work lookup fails without existence disclosure.
- [ ] RED: CTX-019 proves old ExecutionContext mutation is rejected and rebinding creates lineage.
- [ ] RED: CTX-020 proves action-time PDR correlation is mandatory for full platform provenance.
- [ ] GREEN: implement adapter-driven runner and deterministic result reducer.
- [ ] Keep platform result separate from repo-local CI and scientific/standards claims.

Verification:

```bash
python -m unittest scripts.test_platform_conformance_v2_1 -v
python scripts/run_platform_conformance_v2_1.py --check-only docs/contracts/platform-convergence-v2-1/vectors.json
```

Full composed execution is run only when exact compatible repo revisions are available together; `--check-only` validates suite completeness without pretending to be functional conformance.

---

### Task 10: Phase rollout, compatibility gate and platform release status

**Repositories:** Governance first, then each participating repo's own release/CI surface as needed.

**Files:**
- Modify: `docs/PLATFORM-CONFORMANCE-V2.1.md`
- Create or modify Governance CI workflow only if repository policy permits a platform-conformance check without embedding credentials
- Update participating repo runbooks/status docs only after their code is merged and verified

Rollout phases are fixed:

```text
PHASE 0  contract registration only
PHASE 1  dual read: identity/1.0 + V2.1 contracts
PHASE 2  new writes emit canonical Principal/Tenant/ExecutionContext references
PHASE 3  consequential platform paths require ExecutionContext
PHASE 4  platform-conformance PASS required for V2.1 platform release
PHASE 5  identity/1.0 is compatibility-read-only on new platform paths
```

- [ ] Gate Phase 1 on successful legacy tests in AIE/TG/WORKS.
- [ ] Gate Phase 2 on stable canonical identity bindings plus WORKS schema v12 migration evidence.
- [ ] Gate Phase 3 on action-time revalidation + PDR correlation and CTX-005..CTX-010/018..020 passing.
- [ ] Gate Phase 4 on all 21 platform vectors passing at exact compatible revisions.
- [ ] Gate Phase 5 on a measured legacy-read test proving historical Work/identity records remain accessible.
- [ ] Report `Repo Verified / Platform Unverified` when local repos are green but composed vectors are not yet green.
- [ ] Do not label V2.1 production-ready solely from the platform-conformance runner; production deployment remains a separate evidence boundary.

Final verification bundle must record exact repo SHAs for:

```text
after-graph-governance
aie
trust-gateway
works-execution
studio
context-continuity
```

and the exact platform-conformance result generated against those revisions.

## Merge Order

1. Governance Task 1 contract registration/correlation.
2. AIE Task 2 Principal contract/adapter.
3. Trust Gateway Task 3 canonical Tenant/Principal resolution.
4. WORKS Task 4 immutable ExecutionContext + schema v12.
5. AIE + Trust Gateway Task 5 action-time PDR correlation.
6. WORKS Task 6 evidence correlation.
7. Context Continuity Task 7 reference transport.
8. Studio Task 8 projection-only adoption.
9. Governance Task 9 composed vectors/Golden Mission.
10. Task 10 phased rollout/release gate.

Do not parallel-merge contract consumers ahead of the owner contract they consume. Work can be prepared in parallel branches, but merge order must preserve a valid source-of-truth chain.

## Definition of Done

V2.1 is not complete until:

- [ ] all four canonical V2.1 families are registered with the approved owners;
- [ ] `identity/1.0` remains readable and semantically unchanged;
- [ ] new canonical identity writes are stable across restarts;
- [ ] AuthorityLease and WorkerLease separation is executable, not merely documented;
- [ ] every consequential V2.1 action has an immutable ExecutionContext and action-time PDR;
- [ ] reauthorization creates a new execution binding with lineage;
- [ ] evidence correlation exposes provenance gaps instead of hiding them;
- [ ] Context Continuity transports refs without authority amplification;
- [ ] Studio remains a projection/interaction surface, not an authority source;
- [ ] `GOLDEN-MISSION-001` and CTX-001..CTX-020 pass against one exact compatible six-repo revision set;
- [ ] platform conformance is reported independently from repo CI, standards maturity, scientific validity and production approval.
