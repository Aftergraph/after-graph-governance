# Aftergraph Repository and Worktree Registry v0.1

**Status:** Draft — operating-control baseline

**Date:** 2026-09-07

**Owner:** Aftergraph portfolio control

**Purpose:** Make repository ownership, canonical sources, worktree intent, and evidence boundaries explicit before additional portfolio expansion.

---

## 1. Normative rules

1. A repository has exactly one canonical remote and one canonical branch for each release line.
2. A local checkout is not canonical merely because it is open, recent, or has a familiar directory name.
3. Every non-canonical checkout MUST have a declared purpose: `feature`, `review`, `verification`, `migration`, `incident`, or `archive`.
4. Dirty worktrees MUST be preserved and inventoried before cleanup, migration, branch deletion, or archival.
5. A release, deployment, or public claim MUST identify the exact repository, branch, and commit it represents.
6. Repository evidence does not inherit across domains. In particular, a standards, research, model, runtime, or product claim requires evidence from its own declared boundary.

## 2. Canonical organisation map

Current repository scope and roles are defined by `docs/platform-topology/2.0.json` (27 repositories; `docs/platform-topology/1.0.json` retained for historical provenance).

| Domain | Canonical repository | Role | Default branch | Evidence boundary |
|---|---|---|---|---|
| Portfolio governance | `Aftergraph/after-graph-governance` | Cross-repository contracts, ownership, terminology, release and claim boundaries | `main` | Documented decision and exact-source evidence |
| Agent runtime | `Aftergraph/runtime` | Active canonical runtime owner: agent lifecycle, orchestration, dispatch, checkpoints, metering | `main` | Exact-head test, integration and runtime evidence |
| Public entry point | `Aftergraph/aftergraph.org` | Public platform entry, launcher, health and agent index | `main` | Deployment and public-surface evidence |
| Knowledge Plane | `Aftergraph/docs` | Provenance-stamped documentation, architecture, API and context packs | `main` | Exact-source plus published-site evidence |
| Authority standard | `Aftergraph/aie` | Independent authority, delegation, lifecycle, budget, revocation and conformance semantics | `main` | Versioned conformance and external interoperability evidence |
| Research | `Aftergraph/intelligence-systems-research` | Research programme, benchmarks, experiments, papers and reference runtimes | `main` | Study, evaluation and reproduction evidence |
| Portability contract | `Aftergraph/skill-abi` | Semantic compatibility, bounded effects, degradation and conformance for portable agent skills (SABI v0.1 alpha) | `main` | Versioned spec, schemas, reference CLI, conformance and release evidence |
| Portability benchmark | `Aftergraph/skillport` | Open benchmark and evaluation suite for semantic portability of agent skills (private until publication scrub gate) | `main` | Study, evaluation and reproduction evidence |
| Runtime enforcement | `Aftergraph/trust-gateway` | Runtime trust and enforcement boundary | `main` | Exact-head test, integration and runtime evidence |
| Durable work | `Aftergraph/works-execution` | Mission lifecycle, durable execution, budgets and evidence-bearing work | `main` | Exact-head test, integration and runtime evidence |
| Work inference | `Aftergraph/wi-backend` | Source-neutral observation to canonical WorkItem inference | `main` | Exact-head test, adapter/integration and runtime evidence |
| Operator product | `Aftergraph/studio` | Product and operator-facing experience | `main` | Rendered-flow, accessibility and integrated-runtime evidence |
| Code-review product | `Aftergraph/sentinel` | Exact-head, evidence-backed code-review verdict product | `main` | Exact-HEAD review and deterministic verdict evidence |
| Verification fixture | `Aftergraph/sentinel-firetest` | Throwaway live-fire fixture; temporary membership only | `main` | Fixture-run evidence; grants no permanent responsibility |
| Scheduled observation | `Aftergraph/aftergraph-cron-fabric` | Read-only scheduled organization sensing; no execution authority | `main` | Exact-head test and gating-record evidence |
| Assurance incubation | `Aftergraph/veranza` | Internal concept under clearance hold; no public maturity implied | `main` | Incubation-record evidence |
| Model methodology | `Aftergraph/llm-research-development` | Reusable model-development methodology and evaluation/promotion contracts | `main` | Versioned methodology and evaluation-contract evidence |
| AFM programme | `Aftergraph/afm` | AFM-specific training, datasets, experiments, evaluations and model cards | `main` | Immutable artifact, experiment and evaluation evidence |
| Model registry | `Aftergraph/model-registry` | Model identity, lifecycle, aliases, artifact provenance and release metadata | `main` | Immutable manifest and promotion-record evidence |
| Shared skills | `Aftergraph/skills-vault` | Mature reusable skills and governed distribution | `main` | Versioned package, provenance and execution evidence |
| Shared brand | `Aftergraph/brand` | Shared visual identity and public assets | `main` | Approved source and published-asset evidence |
| Continuity contract | `Aftergraph/context-continuity` | Portable state-transfer capsules (Draft 0.1) | `main` | Versioned contract and boundary-proposal evidence |
| Continuity assurance | `Aftergraph/continuum` | Continuity containment verification | `main` | Verification-record evidence |
| Work experience | `Aftergraph/wi-frontend` | Work-intelligence web experience | `main` | Rendered-flow evidence |
| Legacy transition | `Aftergraph/autonomous-venture-company` | legacy-migration-source pending governed extraction; no new canonical responsibility | `main` | Migration-source evidence |
| Org infrastructure | `Aftergraph/.github` | Organization profile, shared workflows, community defaults | `main` | Shared-workflow and policy evidence |

`Aftergraph/aie` MAY maintain a deliberately independent publication lineage. If its canonical upstream is not the Aftergraph organisation, the registry MUST state that relationship, the pinned release/import mechanism, and the conformance boundary before any release consumes it.

## 3. Local worktree record

The following record is required for every local checkout outside the one nominated canonical root. The record MUST live in a local inventory or task record; machine-specific paths and private host details MUST NOT be published in this repository.

| Field | Required value |
|---|---|
| Repository | Canonical `owner/repository` identifier |
| Local path | Machine-local path; kept out of public governance history |
| Branch and exact HEAD | Current branch/ref and full commit SHA |
| Purpose | `feature`, `review`, `verification`, `migration`, `incident`, or `archive` |
| Owner | Person accountable for resolving or preserving it |
| Dirty state | `clean` or list of changed paths |
| Remote relation | `at-head`, `behind`, `ahead`, `diverged`, or `unverified` |
| Expiry/review date | Date to reconcile, merge, archive, or renew purpose |
| Evidence boundary | What the checkout may be used to prove, if anything |

### Required handling

- Temporary clones and branch worktrees are not release roots.
- A worktree with `dirty` state is protected from cleanup until its owner records an explicit disposition.
- A worktree whose remote relation is `unverified` may be used for inspection, but not for a release, deployment, or exact-head claim.
- Legacy experiment/artifact directories are archives until their artifacts and provenance are imported or referenced by a canonical repository.

## 4. Current reconciliation queue

This queue records the first operating-control actions implied by the 2026-09-07 review. It is a planning record, not a claim that reconciliation has occurred.

| Priority | Scope | Required decision | Completion evidence |
|---|---|---|---|
| P0 | Governance | Nominate one canonical local root and `main` release line; retain the current proposal branch as a non-release worktree | Recorded root/branch and exact remote relation |
| P0 | Docs, Skills Vault | Preserve existing dirty worktrees (TG's untracked `package-lock.json` already preserved through reconciliation); assign an owner and disposition before cleanup | Inventory entry with changed paths and disposition |
| P0 | Work Intelligence | Reconciled 2026-09-07: canonical root at `49f60214` (= remote main), security pin merged (#56), main CI green | DONE 2026-09-07 — exact SHA, clean tree, CI evidence |
| P0 | Trust Gateway | Reconciled 2026-09-07: canonical root at `97ba8f6` (= remote main, 44-commit fast-forward), platform-identity 9/9 local, main CI green | DONE 2026-09-07 — exact SHA, clean tracked tree (untracked `package-lock.json` preserved) |
| P0 | WORKS Execution | Reconciled 2026-09-07: canonical root at `79914a5` (= remote main, 12-commit fast-forward), CI Go-tests green on exact SHA (no local Go toolchain) | DONE 2026-09-07 — exact SHA, clean tree, CI evidence |
| P0 | ISR | Reconciled 2026-09-07: canonical root at `08c9846` (= remote main, 20-commit fast-forward), full pytest 687 passed / 0 failed locally | DONE 2026-09-07 — exact SHA, clean tree, full-suite evidence |
| P0 | Docs, Skills Vault | Preserve existing dirty worktrees; assign an owner and disposition before cleanup | Inventory entry with changed paths and disposition |
| P1 | AIE | Decide and record independent-upstream versus Aftergraph-canonical status | Governance decision and pinned import/release rule |
| P1 | AFM | Classify legacy local artifacts separately from the canonical AFM programme repository | Artifact manifest/import or archival record |
| P1 | All active products | Name a release root, deployment boundary, and claim owner | Release record linked to exact source commit |

## 5. Enforcement path

This registry is an operating-control baseline. It becomes enforceable in three small increments:

1. Add a local, non-public inventory for machine paths and dirty-worktree dispositions.
2. Add a CI check that validates repository identifiers and required fields in this document or its successor data file.
3. Require a registry reference in release, deployment, and public-claim templates.

Until those controls exist, this document provides architecture guidance and review criteria only; it does not prove current repository, deployment, or runtime conformance.
