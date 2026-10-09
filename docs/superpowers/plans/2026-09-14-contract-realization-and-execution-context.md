# Contract Realization and Execution Context Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Prevent declared cross-repo contracts from being treated as usable until their owner repository realizes and conforms to them, beginning with WORKS-owned `execution-context/1.0`.

**Architecture:** Keep Governance as the contract registry and evidence boundary, WORKS as the owner of durable immutable ExecutionContext state, and Program Overlay as an advisory consumer. Add no new control plane. Realization evidence is derived from exact-head owner/path observation and conformance checks; composed proof remains a separate maturity level.

**Tech Stack:** JSON Schema Draft 2020-12, Python 3.12, Go 1.24+, SQLite, GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-09-07-aftergraph-platform-convergence-v2-1-canonical-identity-execution-context-design.md`

## Global Constraints

- `execution-context/1.0` remains owned by `works-execution`.
- Work may exist without ExecutionContext; consequential V2.1 execution may not.
- WorkerLease and AuthorityLease remain structurally and semantically distinct.
- ExecutionContext is immutable; reauthorization creates a new context linked by `prior_execution_context_id`.
- Governance never owns WORKS runtime state.
- Program Overlay and semantic claims grant no authority.
- `DECLARED`, `REALIZED`, `CONFORMANT`, and `COMPOSED_PROVEN` are distinct evidence states.
- Missing owner/path evidence fails closed as `DECLARED_NOT_REALIZED` or `UNKNOWN`; it never silently becomes PASS.
- No hard org-wide enforcement is introduced in this slice.

---

### Task 1: Correct the V2.1 binding order in Governance

**Files:**
- Modify: `docs/superpowers/specs/2026-09-07-aftergraph-platform-convergence-v2-1-canonical-identity-execution-context-design.md`

**Interfaces:**
- Consumes: existing V2.1 Task 4 precondition.
- Produces: normative ordering `Work -> WorkerLease -> ExecutionContext -> consequential action`.

- [ ] Replace the two stale ordering passages that create ExecutionContext before WorkerLease.
- [ ] Preserve all authority/ownership language.
- [ ] Verify no remaining happy-path text says `Work + execution-context` before WorkerLease.
- [ ] Commit documentation-only clarification.

### Task 2: Implement WORKS `execution-context/1.0`

**Files:**
- Create: `contracts/schemas/execution-context.schema.json`
- Create: `packages/executioncontext/context.go`
- Create: `packages/executioncontext/context_test.go`
- Create: `services/work/store/execution_context.go`
- Create: `services/work/store/execution_context_test.go`
- Modify: `services/work/store/store.go`
- Modify: `contracts/gen_freeze.py`
- Regenerate: `contracts/manifest.json`, `contracts/manifest.sha256`, `contracts/FREEZE_EVIDENCE.md`

**Interfaces:**
- Produces: `executioncontext.Context`, `Validate() error`, `Store.CreateExecutionContext`, `Store.GetExecutionContext`, `Store.ListExecutionContextsByWorkID`.
- Consumes: durable Work and WorkerLease rows already owned by WORKS.

- [ ] RED: validation rejects malformed prefixes and swapped `lse_`/`auth_` identifiers.
- [ ] RED: store rejects WorkerLease belonging to another Work.
- [ ] RED: WorkerID is derived from stored WorkerLease, never accepted from caller.
- [ ] RED: duplicate/mutating context write is rejected.
- [ ] RED: reauthorization permits a new context linked to an immutable prior context.
- [ ] GREEN: add schema/type/store migration 11 -> 12 and freeze outputs.
- [ ] Run focused Go tests, then `go test ./...` or repo-equivalent full suite.
- [ ] Commit only when fresh verification is green.

### Task 3: Add WORKS API for immutable ExecutionContext

**Files:**
- Create: `services/api/execution_context_handler.go`
- Create: `services/api/execution_context_handler_test.go`
- Modify: `services/api/api.go`

**Interfaces:**
- Produces: `POST /v1/works/{work_id}/execution-contexts`, `GET /v1/execution-contexts/{execution_context_id}`.
- POST accepts organization/tenant/principal/mission/authority lease/worker lease/admission decision/trace and optional prior context; WORKS derives WorkID, WorkerID, and ContextID.

- [ ] RED: client-supplied `worker_id` or mismatched `work_id` is rejected.
- [ ] RED: foreign WorkerLease fails without leaking foreign Work details.
- [ ] RED: GET returns immutable stored record; no mutation endpoint exists.
- [ ] GREEN: implement handlers using Task 2 store methods.
- [ ] Run focused API/store tests and full repo verification.
- [ ] Commit and push isolated WORKS branch; open draft PR.

### Task 4: Add Governance contract-realization evidence

**Files:**
- Create: `scripts/contract_realization.py`
- Create: `scripts/test_contract_realization.py`
- Create: `docs/contracts/platform-convergence-v2-1/realization.schema.json`
- Modify: `.github/workflows/platform-topology-truth.yml`

**Interfaces:**
- Consumes: `docs/contracts/platform-convergence-v2-1/registry.json` plus exact-head owner repository observations supplied as JSON.
- Produces: per-family states `DECLARED_NOT_REALIZED | REALIZED | CONFORMANT | UNKNOWN` and evidence refs.

- [ ] RED: registry family with absent owner path is `DECLARED_NOT_REALIZED`.
- [ ] RED: malformed observation is `UNKNOWN`, never PASS.
- [ ] RED: present path without conformance evidence is only `REALIZED`.
- [ ] RED: valid schema/conformance evidence upgrades to `CONFORMANT`.
- [ ] GREEN: implement deterministic zero-dependency evaluator; no network calls inside core logic.
- [ ] Add CI test of evaluator fixtures; keep org-wide observation advisory in this slice.
- [ ] Commit and push isolated Governance branch; open draft PR.

### Task 5: Make Program Overlay consume realization evidence

**Files:**
- Modify on PR #163 branch after Task 4 API is stable: `scripts/program_overlay.py`
- Modify: `scripts/test_program_overlay.py`

**Interfaces:**
- Consumes: contract realization result keyed by contract family.
- Produces: unresolved required contract -> `BLOCK` or `UNKNOWN` without requiring a hand-maintained `blocked_by` row.

- [ ] RED: overlay requiring `execution-context/1.0` blocks when realization state is `DECLARED_NOT_REALIZED`.
- [ ] RED: realization `UNKNOWN` yields Direction Compiler `UNKNOWN`.
- [ ] RED: `CONFORMANT` removes the derived blocker while preserving independent claim/invariant checks.
- [ ] GREEN: derive contract blockers from realization evidence; keep explicit `blocked_by` supported for non-contract blockers.
- [ ] Run all Program Overlay and topology suites and exact-head CI.
- [ ] Do not merge until review gates are satisfied.
