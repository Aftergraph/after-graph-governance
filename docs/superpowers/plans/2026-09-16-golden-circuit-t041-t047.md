# Golden Circuit T041–T047 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans task-by-task. Steps use checkbox syntax for tracking.

**Goal:** Complete the first exact-subject Aftergraph Circuit path from Runtime dispatch through durable WORKS effects, independent verification, R.O.R.O. re-observation, Golden Circuit proof, and stack reconciliation.

**Architecture:** Extend existing seams only. Runtime binds authority/approval to one exact execution subject and routes Circuit dispatches to WORKS CDA. WORKS owns EffectReceipt/outcome and exact-effect Witness attestations. R.O.R.O. owns post-effect observed reality and Golden Circuit evidence composition.

**Tech Stack:** TypeScript/pnpm/Vitest in Runtime; Go/SQLite in WORKS; Python/JSON Schema in Governance.

**Spec:** User-approved design lock in chat, 2026-09-16.

## Global Constraints
- AuthoritySubject == ApprovalSubject == DispatchSubject == EffectSubject == VerificationSubject by digest.
- Runtime never mints authority or independent verification.
- Complete != Applied != Verified.
- Unknown/stale/changed consequential subjects fail closed.
- Legacy non-Circuit dispatch remains compatible.
- No production deploy during T041–T046.
- T047 merges only after exact-head full regression and cross-repo Golden Circuit proof.
## Tasks

### T041 Runtime → CDA integration
- [ ] RED: Circuit dispatch must carry exact CircuitRun/subject binding and call a Circuit-aware WORKS acceptance port.
- [ ] GREEN: add a narrow adapter over existing Runtime dispatch seal; preserve legacy path.
- [ ] Verify focused tests + Runtime full build/test.

### T042 Exact authority + approval subject
- [ ] RED: changed Circuit/effect/authority epoch invalidates approval; approval expiry remains fail-closed.
- [ ] GREEN: canonical ExecutionSubjectDigest and subject-equality checks using existing authority decisions.
- [ ] Verify no authority/approval can be self-minted by Runtime.

### T043 EffectReceipt / outcome semantics
- [ ] RED: outcomes distinguish DISPATCHED/APPLIED/FAILED/COMPENSATED/INDETERMINATE and APPLIED != VERIFIED.
- [ ] GREEN: persist immutable/evolvable effect receipt tied to CircuitEffectBinding.
- [ ] Verify replay, contradictory terminal transition rejection, restart durability.

### T044 Witness exact-effect verification
- [ ] RED: stale/wrong effect subject and executor=self-verifier are rejected for consequential actions.
- [ ] GREEN: bind CircuitVerdict to exact EffectReceipt digest and verifier evidence.
- [ ] Verify Work/Circuit status is not silently promoted.
### T045 R.O.R.O. post-effect observation
- [ ] RED: post-effect observation requires exact effect subject, freshness, provenance, intended outcome.
- [ ] GREEN: deterministic RealityDelta reducer: MATCHED / REGRESSED / DIVERGED / INDETERMINATE.
- [ ] Verify observation never grants authority or verification by itself.

### T046 Golden Circuit end-to-end proof
- [ ] Build deterministic fixture spanning Runtime subject → WORKS CDA/effect → Witness → R.O.R.O.
- [ ] Prove happy path plus falsifiers: stale approval, changed subject, self-verifier, failed effect, stale post-observation, crash atomicity.
- [ ] Emit exact-head evidence manifest and machine-readable verdict.

### T047 Reconcile + merge stack
- [ ] Reconcile Runtime work against active safety/reality stack and current main.
- [ ] Reconcile WORKS #95→#98 + T043/T044 stack against current main.
- [ ] Reconcile Governance #168 + T045/T046 against current main.
- [ ] Run all owner suites and Golden Circuit on final candidate heads.
- [ ] Merge only in dependency order if repository rules allow and all gates are green; otherwise record the exact external merge blocker without claiming 100% completion.
