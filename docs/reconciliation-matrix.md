# Concept Reconciliation Matrix — 15 Concepts

> Canonical source of truth for concept ownership across the After Graph platform.
> Sources: TG (v2.4.1) · WE (v0.3.5) · AIE (Draft 0.3) · ISR (Q3 2026)
| Status: CANONICAL (owner-approved role distribution)
| Verified: 2026-09-04 against post-merge state

| ## Role Distribution

| Module | Role | Repo |
|---|---|---|
| Agent Workforce | User/developer-facing product layer | trust-gateway (bots/agents) |
| AIE | Normative authority/institution layer | aie |
| Trust Gateway | Runtime control/enforcement plane | trust-gateway |
| WORKS | Durable execution plane | works-execution |
| ISR | Labs/Evals/Assurance | intelligence-systems-research |

## Matrix

| # | Concept | Canonical Owner | Implementations (repo · location) | Projections | Dangerous duplicate sources | Migration needed | Cross-repo contract |
|---|---------|-----------------|-----------------------------------|-------------|----------------------------|------------------|---------------------|
| 1 | Mission | ISR (Program) | ISR: `state/lifecycle.py`; TG: mission controllers; WE: `internal/scheduler` (Mission struct); AIE: spec `missions.defaults` | ISR arch doc; WE `pkg/workgraph` | AIE MissionContract vs ISR lifecycle schema | Yes — schema alignment | mission-state/1.0 |
| 2 | Policy | AIE (Spec) | AIE: spec `policy` (engine, precedence); WE: `contracts/manifest.json`; ISR: `policies/` | WE policies dir | AIE spec vs WE manifest | Yes — unify representation | policy.engine/1.0 |
| 3 | Capability | ISR (Program) | ISR: `capabilities/dispatcher.py`; WE: `packages/capability/`; AIE: subject areas | ISR resolver; WE capability broker | ISR/WE duplicate discovery concepts | Yes — common interface | capability.registry/1.0 |
| 4 | Budget | WE/AIE | WE: `internal/scheduler/budget.go`; AIE: `BudgetLedger`; TG: BudgetStore (`src/gateway/budgets.js`) | budget services | WE/AIE/TG triple tracking | Yes — reconcile semantics | budget.ledger/1.0 |
| 5 | Identity | AIE (Spec) | AIE: `Principal`, `Role`; ISR: agent identity fields | WE lacks explicit model | — | Yes — WE needs model | identity.schema/1.0 |
| 6 | Delegation | ISR (Program) | ISR: `authority/delegation.py` (DelegationManager); AIE: `DelegationRecord` | WE: takeover/release | — | Yes — unify records | delegation.record/1.0 |
| 7 | Revocation | ISR (Program) | ISR: `authority/delegation.py` (revoke_subtree); AIE: `RevocationRecord` | WE: session state | — | Yes — unify records | revocation/1.0 |
| 8 | Evidence | WE/AIE | WE: `services/evidence/bundle.go` + quittance; AIE: `EvidenceRecord` | — | WE service vs AIE object | Yes — align models | evidence.schema/1.1 |
| 9 | Approval | TG (Program) | TG: ApprovalStore (`approvals`); ISR: agent approval logic | WE lacks explicit model | — | Yes — unify into core services | approval.protocol/1.0 |
| 10 | Memory | ISR (Program) | ISR: `agent/context_manager.py`; WE: session state | — | — | Yes — align memory model | memory.context/1.0 |
| 11 | Sandbox/Execution | WE/ISR | WE: `internal/sandbox/hermetic.go`, `docker.go`; ISR: `agent/execution_loop.py` | — | WE/ISR both define execution envs | Yes — align definitions | execution.contract/1.0 |
| 12 | Models | TG/WE/ISR | TG: `providers.js` (Model class); WE: model config; ISR: agent model selection | — | TG explicit Model class vs config-based | Yes — unified interface | model.routing/1.0 |
| 13 | ComputerSession | TG (Program) | TG: ComputerStore (`computer.js`); WE: session mgmt; ISR: agent sessions | — | — | Yes — unify sessions | session.protocol/1.0 |
| 14 | Artifact | WE (Program) | WE: `artifacts/` (bundle, quittance); ISR: build_submission_packages; AIE: spec artifacts | — | WE fs + AIE spec duplicate | Yes — unify representation | artifact.storage/1.0 |
| 15 | Plugin | TG (Program) | TG: PluginHub (`plugins.js`) — mature | WE/ISR pending | — | Yes — ISR/WE integration | plugin.abi/1.0 |

## Executability Rule

Executable = MAY(AIE) ∩ NEEDS(WE/WORKS) ∩ HAS(runtime/TG).
A capability absent from the intersection is not shippable regardless of which repo wants it.

## Verification Notes (2026-09-04)

**Verified EXISTS:**
- TG: budgets.js, computer.js, providers.js, plugins.js (hub.js), approvals.js

**Verified MISSING:**
- WE: internal/scheduler/budget.go (only scheduler.go exists)
- AIE: BudgetLedger class
- ISR: Not cloned locally (delegation.py, context_manager.py, execution_loop.py unverified)

**Partial:**
- AIE: Principal (in spec yaml), Role (in spec yaml)
- AIE: EvidenceRecord (in engine.py)
- AIE: revalidate (in engine.py, docs)
