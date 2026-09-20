# Aftergraph Business Ops — Implementation Plan

**Date:** 2026-09-20
**Status:** DRAFT — requires review (this plan is the first half of `next_action` in `p1-readiness-2026-09-15.md`: `write_and_review_implementation_plans_then_execute_non_production_foundation`)
**Scope:** Non-production foundation execution only. Production cutover remains gated by the three GIVEN blockers recorded in the P1 readiness record and is NOT addressed by this plan.

## 1. Purpose and boundary

This plan sequences the remaining work to take Business Ops from "registered design + shipped alpha" to "executed non-production foundation with conformance evidence." It owns ordering, gates, and acceptance criteria. It does not create new products: reconciliation, compatibility graph, execution runtime, and verification authority remain with their existing owners (AIE, Trust Gateway, WORKS/Runtime, Sentinel/Continuum). Business Ops continues to own only canonical domain state, invariants, ChargeFact emission, migration mappings, and shadow-conformance.

## 2. Existing verified inventory (inputs, not work)

| Artifact | Location | State |
|---|---|---|
| Thin domain kernel design (745 lines) + algorithms v0.1 (A1–A10) | `Aftergraph/business-ops` (PR #1 merged) | authoritative design |
| ChargeFact + MigrationMapping contracts `0.1` | `after-graph-governance/docs/contracts/business-ops/` | registered |
| 12 conformance vectors (`business-ops-conformance/0.1`) | `after-graph-governance/docs/platform-conformance/business-ops/0.1/vectors.json` | registered |
| Deterministic TS kernel (15 algorithms, ports, ajv validator, 71 tests) | `Aftergraph/business-ops` main (PRs #1–#5 merged) | LANDED |
| Route-feasibility increment | `Aftergraph/business-ops` PR #6 (evidence-gated route feasibility) | OPEN, awaiting review |
| Alpha tarball `aftergraph-business-ops-0.1.0-alpha.0.tgz` (13379 B, sha256 `8c9593f0…`, provenance `aftergraph.vendor-provenance/1`, built_from `0bab3e4`) | vendored into ~11 `Aftergraph/rendetalje` tenant worktrees | present |
| Registration | `latest-org-state.json` (remote_head_sha 9f215f7, PR #6 open), `dependencies.yml:178–193`, `docs/platform-topology/2.0.json:341+` | done |
| P1 readiness decision | `docs/business-ops/p1-readiness-2026-09-15.md` | `READY_FOR_IMPLEMENTATION_PLANNING_WITH_BLOCKERS` |

## 3. Phase 0 — close the three technically solvable hygiene gaps (blocks everything else)

These are defects in the current foundation, not new features. They must land before Phase 1 so conformance evidence is trustworthy.

### 0.1 Wire the orphaned governance test into CI

`scripts/test_business_ops_p0_design.py` (6 methods) matches none of the `release-intelligence.yml` discovery rules (`-p 'test_ari_*.py'` pattern + explicit governance-module list + path filters). Fix: add the module to the explicit list and extend path filters to `docs/contracts/business-ops/**`, `docs/platform-conformance/business-ops/**`, and the script itself. Acceptance: the test executes and passes in a green CI run on the merge commit; a deliberate contract break turns CI red (falsification check).

### 0.2 Resolve the alpha version collision

Three byte-distinct artifacts currently claim `0.1.0-alpha.0` (digests `8793aca3…`, `ae5d4758…`, `8c9593f0…`). Fix: bump the canonical artifact to `0.1.0-alpha.1` built from a single reviewed commit, regenerate provenance (`built_from`, sha256, verify command), and update every vendored copy in the tenant worktrees to the pinned digest. Acceptance: exactly one `0.1.0-alpha.1` digest exists account-wide; `npm ci && npm run verify` reproduces it from the named commit; no worktree retains a colliding `alpha.0`.

### 0.3 Exact-head provenance for the reference tenant

Per the P1 strategy: inject `SOURCE_COMMIT`/`BUILD_SHA` at build, bind to the immutable image digest, expose a non-secret `/api/version` on `app.rendetalje.dk`, and preserve the tuple in deploy logs. This is technically solvable now and unblocks future cutover evidence (it does NOT itself authorize cutover). Acceptance: one deployment emits the full six-field provenance tuple and the endpoint's `source_commit_sha` matches the reviewed source head.

## 4. Phase 1 — execute the non-production foundation

Depends on Phase 0. The kernel is already landed on main (PRs #1–#5 merged); PR #6 (route feasibility) is an independent increment and not a Phase 1 prerequisite.

1. **Shadow-conformance harness.** Run all 12 vectors (`CTX-001`, `MAP-001/002`, `CHG-001/002`, `ACT-001`, `REC-001`, `EVD-001`, `EXC-001`, `SHD-001`, `CUT-001`, `EST-001`) against synthetic fixtures through the TS kernel's ajv validator and ports. Evidence: per-vector pass/fail with exact kernel commit and fixture digests. No production data touches the harness.
2. **ChargeFact emission dry-run.** Prove the 12 required fields (incl. `actuals_verification_ref`, `policy_ref{id,version}`, provenance quad) emit correctly and that excluded fields (invoice/amount/rate/tax/currency) are structurally impossible (`additionalProperties: false`).
3. **Migration-mapping quarantine behavior.** Prove `EXACT/REVIEWED/AMBIGUOUS/REJECTED` status flow and the null-target conditionals: ambiguous legacy inputs must quarantine, never guess.
4. **Sentinel/Continuum verification hook.** Verification of Phases 0–1 runs through the existing verification owners; this plan adds no new authority.

Acceptance for the phase: a signed-off conformance record per vector, stored under `docs/platform-conformance/business-ops/`, referencing exact kernel HEAD and artifact digest.

## 5. Phase 2 — reference-tenant integration (Aftergraph/rendetalje)

Sequence the already-open tenant work before any shadow run against tenant-shaped data:

1. Land the open route-feasibility / T4-dispatch / booking-observation PRs (workspace PRs 507/508 family and the `Aftergraph/rendetalje` feature branches behind the vendored alpha). Each lands through its normal review + CI gate; no queue bypass.
2. Re-vendor the pinned `0.1.0-alpha.1` into the tenant worktrees (Phase 0.2 dependency).
3. Run the Phase 1 harness with tenant-scoped synthetic fixtures (privacy-safe cardinality only until the DB ledger blocker is cleared by its human owner).

## 6. Human-required decisions (explicitly NOT autonomous)

| Item | Owner | Why it cannot be automated here |
|---|---|---|
| Donor-repo credential/history remediation verification (4 P−1 repos) | Jonas + independent verifier | security transfer blocker; classification requires human review |
| Production read-only DB ledger acquisition | Rendetalje production data plane | authorization boundary |
| AVC serviceops ↔ business-ops precedence | Jonas | two parallel product homes target Rendetalje mutually unaware; a duplicate-owner decision, not a technical merge |
| Production cutover authorization | Jonas | all three GIVEN blockers must clear first |

## 7. Non-goals

No new reconciliation product, bridge service, generic standards ontology, duplicate compatibility graph, duplicate execution/runtime owner, or new verification authority. No production schema mutation, data migration, provider writes, or source-of-truth cutover inside this plan's scope.

## 8. Machine-readable summary

```yaml
plan_status: DRAFT_AWAITING_REVIEW
phases: [phase0_hygiene, phase1_nonprod_foundation, phase2_reference_tenant]
phase0_items: [ci_wire_orphan_test, resolve_alpha_version_collision, exact_head_provenance]
production_cutover_in_scope: false
human_gates: [donor_remediation, db_ledger_authorization, avc_precedence, cutover_authorization]
```
