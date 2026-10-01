# Aftergraph Platform Reconciliation V1

**Date:** 2026-09-07 (historical cut)
**Historical scope:** 19 repositories at the original 2026-09-07 cut, followed by the 24-repository V4 truth-convergence cut. Current inventory is recorded in the 2026-10-01 addendum below.
**Purpose:** convert repository growth into one governed polyrepo platform without collapsing independent evidence/authority boundaries.

## Target outcome

```text
Human intent / observations
        ↓
Work + mission + continuity
        ↓
AIE authority / institution semantics
        ↓
Trust Gateway runtime enforcement
        ↓
WORKS durable execution
        ↓
trajectory + evidence
        ↓
independent verification / assurance
        ↓
verified outcome
```

Human/public surfaces sit above that path (`studio`, specialist Work Intelligence UI, AVC, `aftergraph.org`, `docs`). Skills/models are capabilities consumed by execution, not alternative sources of authority.

## Historical V4 repository topology (24-repository cut)

| Plane | Repository | Role |
|---|---|---|
| Governance | `after-graph-governance` | canonical contracts, topology and exact-head generation |
| Institution | `aie` | normative authority/delegation semantics |
| Enforcement | `trust-gateway` | runtime admission, approvals and audit |
| Execution | `works-execution` | durable work, workers, recovery and quittance |
| Experience | `studio` | primary general-purpose human experience |
| Runtime | `runtime` | active canonical runtime owner: agent lifecycle, orchestration, dispatch |
| Experience | `wi-frontend` | specialist Work Intelligence experience/BFF |
| Work Intelligence | `wi-backend` | observations → WorkItems |
| Continuity | `context-continuity` | portable actionable state transfer |
| Assurance | `continuum` | continuity/containment fault-injection assurance; not ordinary continuity owner |
| Assurance | `sentinel` | exact-subject verification verdicts |
| Temporary assurance | `sentinel-firetest` | throwaway live-fire fixture |
| Research/Assurance | `intelligence-systems-research` | SPEC-001, MISSION-Bench, scientific claims/evidence |
| Capabilities | `skills-vault` | governed skill supply chain |
| Models | `llm-research-development` | reusable model R&D methodology |
| Models | `afm` | AFM-specific model program |
| Models | `model-registry` | immutable model lifecycle registry |
| Operations | `aftergraph-cron-fabric` | read-only scheduled observation; no execution authority |
| Incubation | `veranza` | internal hold; no public/production maturity implied |
| Legacy transition | `autonomous-venture-company` | legacy-migration-source pending governed extraction |
| Knowledge | `docs` | provenance-pinned Knowledge Plane |
| Public | `aftergraph.org` | public front door and launcher |
| Foundation | `brand` | visual identity/design system |
| Foundation | `.github` | organization/community defaults |

Machine-readable source: `docs/platform-topology/2.0.json` (`docs/platform-topology/1.0.json` retained for historical provenance).

## Current organization inventory (2026-10-01)

The live Aftergraph organization contains 44 active, unarchived repositories. The current topology registers all 44: 34 with an established topology role and 10 with `role=unclassified`, `system_class=unclassified`, and `lifecycle=classification-pending`. Those pending rows record organization membership only and declare no dependency, contract, production-maturity, authority, execution, or verification claims.

Repositories awaiting owner classification are `concord`, `demo-repository`, `engineering-crew-community`, `fihim-eval-lab`, `fihim-vnext`, `friday-mascot`, `nikkahcerti`, `Pock-bot`, `STEWARD-by-Aftergraph`, and `urban-potato-demo-repository`. Their exact default-branch heads are recorded in the generated `latest-org-state.json`; that snapshot describes live GitHub state at its generation time, not deployment or functional acceptance.

## Execution ledger

### P0 — platform truth and boundaries

- [x] Define a 19-repository machine-readable topology contract (historical 2026-09-07 cut; superseded by the later 24-repository V4 cut, which is now expanded to the 44-repository current inventory).
- [x] Expand `org-state/1.0` role vocabulary to the complete platform.
- [x] Remove the stale Work Intelligence `master`-branch exception from org-state schema documentation.
- [x] Make `org-state-verify.sh` derive repository scope from topology instead of a hard-coded nine-repo list.
- [x] Fail closed if GitHub cannot resolve every topology repository.
- [x] Fail closed if topology canonical branch diverges from GitHub default branch.
- [x] Expand `dependencies.yml` to the original 19 repositories and later 24-repository V4 cut; the 2026-10-01 projection now covers all 44 live repositories at `version: 4`, with no inferred dependencies for the 10 classification-pending entries.
- [x] Replace the five-repository framing in the cross-repo contract register with explicit platform boundaries.
- [ ] Re-run the authenticated generator after merge so `latest-org-state.json` records the merged Governance head; do not hand-edit SHAs. The 2026-10-01 branch snapshot records the live 44-repository heads before this PR is merged.

### P0 — one production path

- [ ] Freeze one canonical consequential path: `Studio → AIE → Trust Gateway → WORKS → Evidence → independent verifier`.
- [ ] Define request/correlation identifiers that survive the full path without semantic reinterpretation.
- [ ] Add a cross-repo conformance gate proving authority decision, runtime enforcement, execution record and verification evidence correlate to the same mission/action.
- [ ] Add failure cases: authority revoked mid-flight, budget exhausted, verifier unavailable, worker crash, replay/idempotency and evidence mismatch.

### P0 — identity architecture

- [ ] Publish `IDENTITY-ARCHITECTURE-v1.0`: Human, Agent, Service, Tool and Organization principals.
- [ ] Declare canonical tenant/org identity source and how TG RBAC, AIE Principal, AVC identity-core and WORKS subjects map to it.
- [ ] Define authentication substrate vs authorization semantics vs workload identity; do not create another identity protocol.
- [ ] Specify delegation/revocation propagation and fail-closed behavior across runtime partitions.

### P1 — experience reconciliation

- [ ] Declare Studio the canonical general-purpose human shell while preserving specialist deployments.
- [ ] Map `Chat`, `Work`, `Space`, `Needs You`, `Evidence`, `Agents`, `Connections` to canonical backend owners.
- [ ] Keep `wi-frontend` as specialist Work Intelligence deployment/BFF, not a competing source of WorkItem truth.
- [ ] Keep AVC Mission Control as deep venture/operator control where needed, not a second general platform shell.

### P1 — benchmark and assurance namespaces

- [ ] ISR remains owner of scientific MISSION-Bench methodology and claims.
- [ ] Continuum versions continuity/containment campaigns without redefining ISR canonical metrics.
- [ ] ACC/`context-continuity` owns state-transfer/handshake research only.
- [ ] Publish a shared fault taxonomy mapping `MISSION-Bench ↔ Continuum ↔ CONTINUITY-Bench`, with explicit equivalence/non-equivalence.

### P1 — AVC/platform boundary

- [ ] Inventory executable overlap between AVC Kernel and AIE/TG/WORKS.
- [ ] For each overlapping primitive, declare canonical owner, adapter/projection and migration path.
- [ ] Preserve AVC product-specific behavior and Product Cells while eliminating dual platform truth.

### P1 — knowledge/public automation

- [ ] Make `Aftergraph/docs` import platform topology as a pinned source and expose freshness/drift.
- [ ] Make `aftergraph.org` generate its repository/system catalog from governance topology plus repo-owned evidence.
- [ ] Never copy private repo content to public surfaces; private repos expose name/approved description only.
- [ ] Public pages render maturity/evidence class separately from repository existence or CI activity.

### P2 — commercial/platform operations

- [ ] Canonical tenant entitlements and product packaging.
- [ ] Usage/budget/cost attribution across missions, models, tools and humans.
- [ ] Platform release train and compatibility window across independently versioned repos.
- [ ] Platform SLOs for admission, execution, recovery, evidence and verification.
- [ ] SDK packaging around contracts/capabilities without creating a monolithic runtime dependency.

## Invariants

1. `WorkItem != WORKS Work`.
2. `Declared completion != verified outcome`.
3. A continuity capsule never grants authority.
4. Installation of a skill/plugin never grants authority.
5. UI state is a projection, not backend truth.
6. Runtime evidence does not establish AIE conformance.
7. AIE conformance does not establish scientific validity.
8. Research evidence does not grant production authority.
9. Public visibility does not upgrade evidence or maturity.
10. Exact Git state comes from generated GitHub API evidence, never manually typed SHAs.

## V1 completion definition

The original V1/V4 truth-convergence was defined and evidenced against the 24-repository inventory at that historical cut. It does not establish present-day full-organization coverage. The 2026-10-01 topology and exact-head snapshot extend membership to 44 live repositories, with 10 awaiting owner classification. Runtime unification tasks above remain separately gated P0/P1 work and must not be described as already complete.

## Wave A truth-convergence evidence (V4)

The following artifacts record historical 24-repository/V4 truth convergence; they are not current 44-repository or production-execution acceptance evidence:

- `docs/evidence/platform-architecture-v4-wave-a.json` — the original Wave A check record (`topology_v2`, `dependency_projection`, `readme_projection`, `org_state_binding`, `platform_fabrics_regression`);
- `docs/PLATFORM-ARCHITECTURE-V4.md` — canonical architecture (V3 retained as superseded history).

The current topology and `latest-org-state.json` supersede the old 24-repository source/snapshot for present-day inventory. Wave A evidence covers Governance truth convergence only. Runtime, Fabric and Golden Mission waves remain separately gated and are not marked complete here.
