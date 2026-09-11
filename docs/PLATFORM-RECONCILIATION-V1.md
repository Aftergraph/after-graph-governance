# Aftergraph Platform Reconciliation V1

**Date:** 2026-09-07 (historical cut; backlog maintained against current V4)  
**Scope:** complete installed `Aftergraph/*` organization as registered by `docs/platform-topology/2.0.json`; the original 2026-09-07 cut contained 19 repositories. Current repository membership is machine-managed and is not hard-coded here.  
**Purpose:** convert repository growth into one governed polyrepo platform without collapsing independent evidence/authority boundaries.

## Current V4 reconciliation note

`PLATFORM-ARCHITECTURE-V4.md` is canonical. The current consequential lifecycle is:

```text
Intent / Experience
  -> Intelligence
  -> Authority
  -> Trust
  -> Runtime
  -> Execution
  -> Evidence
  -> Verification
  -> Verified Outcome
```

`Relay` is the canonical human operator plane across that lifecycle. It is a control/projection participant, not a new authority, durable-execution owner or verifier. Collision risks and integration gates are tracked in `PLATFORM-COLLISION-RISK-REGISTER-V1.md`.

## Target outcome

```text
Human intent / observations
        ↓
Intelligence / WorkItem inference
        ↓
AIE authority / institution semantics
        ↓
Trust Gateway runtime admission / enforcement
        ↓
Runtime agent operation / provider dispatch
        ↓
WORKS durable execution
        ↓
trajectory + evidence
        ↓
independent verification / assurance
        ↓
verified outcome
```

Studio and specialist human/public surfaces project this path. Relay supervises and controls it without replacing domain truth. Skills/models are capabilities consumed by execution, not alternative sources of authority.

## Repository topology

The machine-readable source is `docs/platform-topology/2.0.json` (`docs/platform-topology/1.0.json` retained for historical provenance). The following table is a role-oriented reconciliation view, not a repository-count source.

| Plane / class | Repository | Role |
|---|---|---|
| Governance | `after-graph-governance` | canonical contracts, topology and exact-head generation |
| Authority | `aie` | normative authority/delegation semantics |
| Trust | `trust-gateway` | runtime admission, approvals and audit |
| Runtime | `runtime` | canonical agent lifecycle, orchestration and dispatch |
| Execution | `works-execution` | durable work, workers, recovery and quittance |
| Experience | `studio` | primary general-purpose human experience |
| Experience | `relay` | canonical human operator/control plane |
| Experience | `wi-frontend` | specialist Work Intelligence experience/BFF |
| Intelligence | `wi-backend` | observations → WorkItems |
| Continuity | `context-continuity` | portable actionable state transfer |
| Assurance | `continuum` | continuity/containment fault-injection assurance; not ordinary continuity owner |
| Verification | `sentinel` | exact-subject code verification verdicts |
| Temporary assurance | `sentinel-firetest`, `sentinel-firetest2` | throwaway live-fire fixtures governed by topology expiry |
| Research/Assurance | `intelligence-systems-research` | SPEC-001, MISSION-Bench, scientific claims/evidence |
| Capabilities | `skills-vault` | governed skill supply chain |
| Capabilities | `skill-abi` | skill compatibility/effect contract |
| Assurance | `skillport` | skill portability benchmark/evaluation |
| Models | `llm-research-development` | reusable model R&D methodology |
| Models | `afm` | AFM-specific model program |
| Models | `model-registry` | immutable model lifecycle registry |
| Operations | `aftergraph-cron-fabric` | read-only scheduled observation; no execution authority |
| Incubation | `veranza` | internal hold; no public/production maturity implied |
| Legacy transition | `autonomous-venture-company` | legacy migration source pending governed extraction |
| Knowledge | `docs` | provenance-pinned Knowledge Plane |
| Public | `aftergraph.org` | public front door and launcher |
| Foundation | `brand` | visual identity/design system |
| Foundation | `.github` | organization/community defaults |

## Execution ledger

### P0 — platform truth and boundaries

- [x] Define a machine-readable topology contract and preserve the original 2026-09-07 cut as historical provenance.
- [x] Expand `org-state/1.0` role vocabulary to the complete platform.
- [x] Remove the stale Work Intelligence `master`-branch exception from org-state schema documentation.
- [x] Make `org-state-verify.sh` derive repository scope from topology instead of a hard-coded repository list.
- [x] Fail closed if GitHub cannot resolve every topology repository.
- [x] Fail closed if topology canonical branch diverges from GitHub default branch.
- [x] Project `dependencies.yml` from the registered topology rather than treating a prose count as canonical truth.
- [x] Replace the five-repository framing in the cross-repo contract register with explicit platform boundaries.
- [x] Stop hard-coding current repository count in architecture/topology prose.
- [ ] Continue regenerating `latest-org-state.json` through authenticated shell/CI runs after topology changes; do not hand-edit SHAs.

### P0 — one production path

- [ ] Freeze one canonical consequential path: `Studio intent → AIE → Trust Gateway → Runtime → WORKS → Evidence → independent verifier → Verified Outcome`.
- [ ] Keep Relay as the operator/control projection across that path, never as an authority/execution/verifier substitute.
- [ ] Define request/correlation identifiers that survive the full path without semantic reinterpretation.
- [ ] Add a cross-repo conformance gate proving authority decision, runtime admission, attempt, durable execution record and verification evidence correlate to the same mission/action.
- [ ] Add failure cases: authority revoked mid-flight, budget exhausted across retry/fallback, verifier unavailable, provider/worker crash, replay/idempotency, continuity restore after revocation, takeover race and evidence mismatch.
- [ ] Execute the Golden Mission on exact heads across real service seams; simulated scenario proof remains evidence but does not satisfy this gate.

### P0 — collision control

- [ ] Freeze `Mission / Work / Attempt / Session / Action` identity mapping using existing contract families rather than inventing another identity protocol.
- [ ] Prove Relay mission/step projection cannot overwrite WORKS durable execution truth.
- [ ] Prove Studio and Relay resolve the same canonical approval/action/evidence identifiers.
- [ ] Prove Runtime provider fallback cannot widen authority or reset mission budget.
- [ ] Prove continuity restore cannot resurrect revoked authority.
- [ ] Prove provider-native consequential tools cannot bypass Trust Gateway action-time admission.
- [ ] Prove executor/process completion cannot promote itself to `VERIFIED`.

See `PLATFORM-COLLISION-RISK-REGISTER-V1.md` for the collision ledger and promotion gates.

### P0 — identity architecture

- [ ] Publish the maintained identity architecture for Human, Agent, Service, Tool and Organization principals using the existing `principal/1.0`, `tenant/1.0`, `execution-context/1.0` and `correlation/1.0` families as applicable.
- [ ] Declare canonical tenant/org identity source and how Trust RBAC, AIE Principal and WORKS subjects map to it.
- [ ] Define authentication substrate vs authorization semantics vs workload identity; do not create another identity protocol.
- [ ] Specify delegation/revocation propagation and fail-closed behavior across runtime partitions and provider migration.

### P1 — experience reconciliation

- [ ] Keep Studio as the canonical general-purpose human shell while preserving specialist deployments.
- [ ] Keep Relay as the canonical deep operator/control surface, not a second source of mission/authority/execution truth.
- [ ] Map `Chat`, `Work`, `Space`, `Needs You`, `Evidence`, `Agents`, `Connections` and operator controls to canonical backend owners.
- [ ] Keep `wi-frontend` as specialist Work Intelligence deployment/BFF, not a competing source of WorkItem truth.
- [ ] Remove active product/control dependency on AVC as migration completes; do not create new AVC platform responsibilities.

### P1 — benchmark and assurance namespaces

- [ ] ISR remains owner of scientific MISSION-Bench methodology and claims.
- [ ] Continuum versions continuity/containment campaigns without redefining ISR canonical metrics.
- [ ] ACC/`context-continuity` owns state-transfer/handshake research only.
- [ ] Publish a shared fault taxonomy mapping `MISSION-Bench ↔ Continuum ↔ CONTINUITY-Bench`, with explicit equivalence/non-equivalence.

### P1 — AVC/platform boundary

- [ ] Inventory executable overlap between legacy AVC sources and AIE/TG/Runtime/WORKS/Relay.
- [ ] For each overlapping primitive, declare canonical owner, adapter/projection and migration path.
- [ ] Preserve only legitimate migration provenance/product-specific historical behavior while eliminating dual platform truth.

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
2. `Mission != Work != Attempt != Session != Action`.
3. `Declared completion != verified outcome`.
4. A continuity capsule never grants authority.
5. Installation of a skill/plugin/model/provider never grants authority.
6. UI/operator state is a projection, not backend truth.
7. Runtime evidence does not establish AIE conformance.
8. AIE conformance does not establish scientific validity.
9. Research evidence does not grant production authority.
10. Public visibility does not upgrade evidence or maturity.
11. Runtime may select implementations but may not widen authority.
12. Exact Git state comes from generated GitHub API evidence, never manually typed SHAs.

## V1 completion definition

The original V1 truth-convergence milestone is historical. Current repository scope is whatever `docs/platform-topology/2.0.json` registers and `latest-org-state.json` resolves at an authenticated evidence cut; no prose repository count supersedes those machine sources. Runtime/Fabric/Golden Mission integration remains separately gated work and must not be described as complete merely because Governance truth is internally consistent.

## Wave A truth-convergence evidence (V4)

The original Wave A truth-convergence evidence remains historical provenance for its evidence cut:

- `docs/platform-topology/2.0.json` — canonical ownership truth;
- `latest-org-state.json` — authenticated exact-head snapshot (`org-state/1.0`);
- `docs/evidence/platform-architecture-v4-wave-a.json` — Wave A check record (`topology_v2`, `dependency_projection`, `readme_projection`, `org_state_binding`, `platform_fabrics_regression`);
- `docs/PLATFORM-ARCHITECTURE-V4.md` — canonical architecture (V3 retained as superseded history).

This evidence covers Governance truth convergence only. Runtime, Fabric, collision-control and Golden Mission waves remain separately gated and are not marked complete here.
