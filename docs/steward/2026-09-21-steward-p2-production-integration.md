# STEWARD P2 — Production Integration Contract

Status: PROPOSED — implementation started  
Date: 2026-09-21  
Owner: Aftergraph governance  
Scope: STEWARD P1→P2 productionization across canonical platform owners.

## Purpose

This document defines the first production integration slice for STEWARD. STEWARD is a composition/product root; it does not duplicate normative ownership already held by AIE, Trust Gateway, Runtime, WORKS, Sentinel, Model Registry, Skills Vault, or governance.

The first production proof MUST replace reference adapters one boundary at a time while preserving exact ownership and fail-closed semantics.

## Exact repository baseline

| Owner | Repository | Baseline commit |
|---|---|---|
| STEWARD | `Aftergraph/STEWARD-by-Aftergraph` | `688c3e4b193f8f3ea34048044bbe4c82c26899d4` |
| Governance | `Aftergraph/after-graph-governance` | `84d3cda4c3ce669ce4d6fbb031edbd3f514a3527` |
| WORKS | `Aftergraph/works-execution` | `ab8c1d2a6cc322b3d730b1514b1141b8ee65310c` |
| Runtime | `Aftergraph/runtime` | `4bff0be654c9e32f62317295d43d7e918139f3e9` |
| AIE | `Aftergraph/aie` | `4c8b871478183557d147a6670a57c5b5e7b15024` |
| Trust Gateway | `Aftergraph/trust-gateway` | `8a2c8d66a67d036227c77904844f105b39723f58` |
| Sentinel | `Aftergraph/sentinel` | `eb51f824af2279ee3eee5daa8572bd54a34b3ca8` |

Any implementation claim made against a later head MUST refresh this baseline and repeat the relevant conformance checks. The STEWARD row is the current stacked P2 candidate on `steward/p2-sentinel-port-v0`; it is not yet a P2 PASS.

## Existing canonical seams to reuse

### Governance
- `principal/1.0`: normative actor identity owned by AIE.
- `tenant/1.0`: normative runtime-isolation identity owned by Trust Gateway.
- `execution-context/1.0`: immutable correlation/binding envelope owned by WORKS; not an authorization token.
- Workspace, Project, session, model, skill, plugin, repository membership never grant authority.
- Every consequential action revalidates live authority immediately before consequence.
- AuthorityLease and WorkerLease remain distinct.

### WORKS
Existing production primitives include:
- durable Work and event journal,
- leases and owner-bound mutating lease verbs,
- idempotency,
- handoff/checkpoint persistence,
- Runtime→WORKS dispatch acceptance seam `dispatch.acceptance/1.0`,
- WORKS-minted `execution_context_id` and `trace_id`,
- execution-policy correlation,
- verification gating that does not allow SUCCEEDED to become VERIFIED without verification.

### AIE
Existing production primitives include:
- capability attenuation,
- resource-prefix attenuation,
- delegation depth,
- budget conservation,
- execution-time revalidation design,
- explicit distinction between identity and authority.

### Trust Gateway
Existing production primitives include:
- governed egress,
- adapter-bound scoped handles,
- fail-closed authority/approval checks,
- tenant-scoped credential lifecycle,
- trusted mission/authority context resolver,
- write-ahead audit prior to dispatch.

### Runtime
Runtime remains the orchestration/dispatch/checkpoint owner. STEWARD MUST integrate through the canonical Runtime boundary and MUST NOT become a second scheduler or execution-truth owner.

### Sentinel
Sentinel remains the independent exact-subject verification owner. STEWARD MUST consume verdicts and project them; it MUST NOT self-promote execution completion into verification.

## P2 canonical vertical slice

```text
Natural-language goal
    ↓
STEWARD intent/specification
    ↓
Mission
    ↓
Runtime orchestration request
    ↓
WORKS dispatch acceptance
    ↓
WORKS-minted execution_context_id + trace_id
    ↓
Runtime/Habitat prepares proposed effect
    ↓
Trust Gateway V2.1 execution action
    ↓
current identity + immutable WORKS execution context
    ↓
AIE live authority revalidation(action_id)
    ↓
TG execution-phase PDR
    ↓
PDR correlation persisted back to WORKS
    ↓
effect dispatch
    ↓
candidate immutable subject (Git SHA for coding slice)
    ↓
WORKS evidence correlation
    ↓
Sentinel exact-subject verification
    ↓
MissionAcceptance
    ↓
VerifiedOutcome
    ↓
STEWARD projection
```

## Required invariants

1. selected ≠ authorized.
2. completed ≠ verified.
3. identity ≠ authority.
4. Project/workspace/session/repository membership never grants authority.
5. AuthorityLease ≠ WorkerLease.
6. `execution-context/1.0` ≠ authorization token.
7. every consequential action revalidates live authority immediately before consequence.
8. child authority MUST attenuate parent authority.
9. runtime dispatch ≠ durable WORKS acceptance.
10. tool result ≠ trusted observation.
11. Git branch name ≠ immutable verification subject; exact commit SHA is the subject for the coding slice.
12. new/rebased HEAD invalidates subject-bound verification until reverified.
13. Sentinel verdict ≠ builder self-report.
14. UI/projected state ≠ canonical execution truth.
15. STEWARD MUST NOT persist raw long-lived credentials in Agent/Habitat context.

## P2 contracts

### steward.intent/0.1
STEWARD-owned interaction envelope carrying:
- principalRef
- projectRef
- user intent
- input refs
- requested mode
- output preference
- correlation hint

This contract MUST NOT carry authority grants.

### steward.mission-binding/0.1
Projection binding between:
- Steward Mission
- canonical WORKS Work
- Runtime dispatch
- execution-context/1.0
- root trace

This is correlation only.

### steward.git-subject/0.1
For coding work:
- repositoryRef
- baseCommit
- candidateCommit
- optional branchRef
- optional pullRequestRef
- verificationSubject = candidateCommit

### steward.verification-projection/0.1
Read-only projection of:
- subjectRef
- Sentinel verdictRef
- evidenceRefs
- verifiedAt
- staleReason

STEWARD cannot mint the verdict.

## Required production adapters

1. **WORKS adapter**
   - create/read Work through canonical API,
   - accept/propagate WORKS-minted correlation,
   - follow durable events,
   - suspend/resume only through canonical checkpoint binding.

2. **Runtime adapter**
   - submit MissionGraph/Work unit to canonical runtime,
   - follow dispatch/checkpoint state,
   - never mint execution truth locally.

3. **AIE execution-time integration — enforced through Trust Gateway**
   - STEWARD carries action/context references but MUST NOT become the execution-side AIE client,
   - Trust Gateway invokes AIE live revalidation by action ID immediately before consequence,
   - fail closed on stale/revoked/exhausted/unreachable authority,
   - the revalidated authority lease MUST match the immutable WORKS execution context.

4. **Trust Gateway adapter** — implementation started in `Aftergraph/STEWARD-by-Aftergraph#4`
   - use the canonical Platform V2.1 `POST /v1/actions` path with mandatory `execution_context_id`,
   - enforce current identity + immutable WORKS context + AIE revalidation,
   - persist execution-phase PDR correlation back to WORKS before dispatch,
   - use scoped handles/credential surrogation for governed egress,
   - fail closed when mission/authority/context/correlation is absent,
   - STEWARD MUST NOT select the legacy no-context execution path.

5. **Sentinel adapter** — projection port implemented in `Aftergraph/STEWARD-by-Aftergraph#5`; live verifier transport still pending
   - request/observe independent exact-subject verification,
   - bind verdict to immutable subject,
   - invalidate projection when subject changes.

## Acceptance criteria

P2 is PASS only when one real coding Mission demonstrates all of the following:

- [ ] Mission is created from STEWARD and bound to canonical WORKS Work.
- [ ] Runtime dispatches through its canonical boundary.
- [ ] WORKS durably accepts the dispatch.
- [ ] `execution_context_id` and `trace_id` are WORKS-minted, not client-selected.
- [ ] AIE authority is revalidated immediately before the consequential Git effect.
- [ ] Trust Gateway enforces the execution-phase decision and governed egress.
- [ ] Builder operates in an isolated Worktree bound to the Work/Attempt.
- [ ] Candidate commit SHA is immutable and recorded.
- [ ] Independent verification runs against that exact SHA.
- [ ] A new SHA demonstrably makes the prior verification projection stale.
- [ ] Mission is not accepted until required verification passes.
- [ ] Trace links intent→mission→work→attempt→git subject→evidence→verdict→outcome.
- [ ] Failure of AIE/TG/Sentinel integration fails closed.
- [ ] No long-lived repository credential is exposed to the model context.

## Non-goals for P2

- No multi-agent optimization yet.
- No Verified RSI promotion yet.
- No new authority system.
- No replacement for WORKS or Runtime.
- No new verification owner.
- No attempt to make Project or repository membership an authority root.

## Integration sequence

1. Lock exact repository heads and refresh contract inventory.
2. Land this governance integration contract.
3. Implement WORKS binding first.
4. Add Runtime adapter against WORKS dispatch acceptance.
5. Add AIE revalidation at consequence boundary.
6. Add Trust Gateway execution-phase enforcement and scoped egress.
7. Add Git/Worktree exact-subject adapter.
8. Add Sentinel exact-SHA verification projection.
9. Run negative/falsification gates.
10. Record evidence bundle and only then claim P2 PASS.
