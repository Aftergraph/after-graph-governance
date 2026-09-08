<!-- aftergraph-brand-os:v1.0.0 -->

[![OpenSSF Scorecard](https://api.scorecard.dev/projects/github.com/Aftergraph/after-graph-governance/badge)](https://scorecard.dev/viewer/?uri=github.com/Aftergraph/after-graph-governance)

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset=".github/assets/github/hero.webp">
    <img src=".github/assets/github/hero.png" alt="Platform Governance — Architecture, contracts, terminology, and exact-head truth" width="100%">
  </picture>
</p>

# Aftergraph Platform Governance

> Canonical cross-repository topology, contracts, boundaries and exact-head truth mechanics for the Aftergraph ecosystem.

**Brand status:** Aftergraph / ABDE Intelligence naming remains provisional and has not completed trademark clearance. Repository/contract boundaries are technical governance and do not depend on final brand naming.

## Platform model

Aftergraph is a polyrepo platform. Repositories remain independently versioned and independently accountable for their runtime, conformance and scientific claims.

```text
Public / Knowledge
  aftergraph.org · docs · .github · brand
          ↓
Experience
  studio · wi-frontend · autonomous-venture-company (legacy transition)
          ↓
Intent / Work / Continuity
  wi-backend · context-continuity
          ↓
Institution / Enforcement / Runtime / Execution
  AIE → Trust Gateway → Runtime → WORKS
          ↓
Capabilities / Models
  skills-vault · llm-research-development · afm · model-registry
          ↓
Assurance / Verification
  intelligence-systems-research · continuum · sentinel
          ↓
Verified outcomes

Cross-cutting operations observation:
  aftergraph-cron-fabric

Explicit special states:
  sentinel-firetest = temporary verification fixture
  veranza = private incubation / INTERNAL HOLD
```

Cross-cutting governance lives here. The topology contract contains **24 repositories** at the 2026-09-08 reconciliation cut. Topology membership never upgrades maturity, evidence, conformance or authority.

## Canonical topology

`docs/platform-topology/1.0.json` is the slow-changing machine-readable topology contract: repository name, role, plane, canonical branch and visibility. It contains **no exact Git SHAs**.

`latest-org-state.json` is the fast-changing generated GitHub truth snapshot: exact remote HEAD, branch, protection, open PRs and contract annotations.

```text
platform-topology/1.0
        ↓ defines scope + roles
scripts/org-state-verify.sh
        ↓ queries GitHub remote truth
org-state/1.0 / latest-org-state.json
```

This separation prevents repository scope from being hard-coded into the generator while preserving the rule that exact Git state is never hand-authored.

## Core ownership boundaries

| Plane | Repository | Canonical responsibility |
|---|---|---|
| Governance | `after-graph-governance` | topology, cross-repo contracts, boundaries, exact-head generation |
| Institution | `aie` | authority, delegation, lifecycle, budget/revocation semantics |
| Enforcement | `trust-gateway` | runtime admission, approvals, policy enforcement and action audit |
| Runtime | `runtime` | agent lifecycle, orchestration, dispatch, checkpoints, metering and observability |
| Execution | `works-execution` | durable work, scheduling, workers, recovery, evidence/quittance |
| Experience | `studio` | general-purpose Chat / Work / Space human environment |
| Work Intelligence | `wi-backend` | source-neutral observations → canonical WorkItems |
| Specialist experience | `wi-frontend` | Wie browser experience and least-privilege BFF; canonical state remains backend-owned |
| Continuity | `context-continuity` | portable actionable state transfer across runtime/session boundaries |
| Assurance | `intelligence-systems-research` | SPEC-001, MISSION-Bench, scientific claims and assurance evidence |
| Assurance | `continuum` | continuity/containment fault-injection campaigns |
| Assurance | `sentinel` | exact-HEAD verified code-review verdicts |
| Capabilities | `skills-vault` | governed skill discovery, lifecycle, trust and provenance |
| Models | `llm-research-development` | reusable model R&D/evaluation/promotion methodology |
| Models | `afm` | AFM-specific model program |
| Models | `model-registry` | immutable promoted model metadata/lifecycle |
| Legacy product consumer | `autonomous-venture-company` | venture OS/Hermes/Product Cells during responsibility migration |
| Operations | `aftergraph-cron-fabric` | read-only scheduled observation, evidence gating, dedupe and escalation; no execution authority |
| Incubation | `veranza` | internal assurance-product concept under clearance hold; no public/production maturity implied |
| Temporary assurance | `sentinel-firetest` | throwaway Sentinel live-fire fixture; remove when proof purpose ends |
| Knowledge | `docs` | provenance-pinned rendering/discovery; not upstream truth owner |
| Public | `aftergraph.org` | website/front door/launcher; visibility does not upgrade evidence |
| Foundation | `brand` | visual identity, design tokens and master assets |
| Foundation | `.github` | organization/community/security/support defaults |

## Governance

> **Everything extensible is a plugin. Everything consequential is governed.**

For consequential execution the governing composition remains:

```text
Executable = Intersection(AIE authority/policy, Trust Gateway runtime admission, WORKS durable execution)
```

Runtime orchestrates agent operation inside that architecture but does not widen AIE authority, bypass Trust Gateway admission, replace WORKS durable execution or self-issue an independent verification verdict.

No UI, model, skill, plugin, research result, repo membership or textual agent declaration grants execution authority by itself.

## Cross-repo contracts

The normative register is maintained in [`docs/cross-repo-contracts.md`](docs/cross-repo-contracts.md).

Current registered families include:

`cpi/1.0`, `rab/1.0`, `identity/1.0`, `policy.token/1.0`, `secret.ref/1.0`, `shell.contracts/1.0`, `link.wire/1.0`, `pairing/1.0`, `brain.ns/1.0`, `release.rings/1.0`, `evidence.schema/1.1`, `kernel.budget/1.0`, `kernel.lifecycle/1.0`, `mission-state/1.0`, `org-state/1.0`.

A repository may participate in the platform without owning a normative contract. Topology membership and normative ownership are separate concepts.

## Org State Contract — exact-head truth

The **Org State Contract** (`docs/contracts/org-state/1.0.json`) is the machine-verifiable remote-state surface for the whole topology-defined organization.

```bash
bash scripts/org-state-verify.sh
bash scripts/org-state-verify.sh --check-local <path...>
```

The generator:

- loads repository scope and roles from `docs/platform-topology/1.0.json`;
- rejects duplicate topology entries;
- rejects canonical-branch drift;
- queries exact remote HEADs from GitHub;
- refuses a partial snapshot if any topology repository cannot be resolved;
- validates against `org-state/1.0`;
- can additionally detect local checkout divergence.

Consumers (Hermes/Codex/AVC agents, CI, reviewers) MUST verify exact heads against a fresh generated contract before gap analysis, delegation or merge decisions. A SHA in a handoff, roadmap or briefing is a claim; a fresh generated org-state is remote truth.

## Evidence layers

| Layer | Producer | Format |
|---|---|---|
| L1 Action Audit | Trust Gateway | hash-chain/action audit |
| L2 Execution Quittance | WORKS | content-addressed execution/evidence bundle |
| L3 Institutional Conformance | AIE | conformance vectors + policy/authority evidence |
| L4 Scientific Evidence | ISR | preregistered studies / MISSION-Bench / statistical analysis |

No layer automatically upgrades another:

- runtime evidence does not establish AIE conformance;
- AIE conformance does not establish scientific validity;
- scientific results do not grant runtime authority;
- public visibility does not upgrade maturity;
- exact-head state does not prove functional conformance.

## Platform Reconciliation V1

The current platform-wide reconciliation program and actionable backlog live in:

- [`docs/PLATFORM-RECONCILIATION-V1.md`](docs/PLATFORM-RECONCILIATION-V1.md) — execution ledger / P0–P2 tasks
- [`docs/platform-topology/1.0.json`](docs/platform-topology/1.0.json) — complete machine-readable repository topology
- [`dependencies.yml`](dependencies.yml) — platform dependency/ownership graph
- [`docs/cross-repo-contracts.md`](docs/cross-repo-contracts.md) — normative contract register + repository boundaries
- [`docs/reconciliation-matrix.md`](docs/reconciliation-matrix.md) — concept-level reconciliation
- [`docs/REPOSITORY-REGISTRY-v0.1.md`](docs/REPOSITORY-REGISTRY-v0.1.md) — canonical repository roles, local worktree controls, reconciliation queue
- [`docs/PLATFORM-ARCHITECTURE-V3.md`](docs/PLATFORM-ARCHITECTURE-V3.md) — seven planes, ownership, product hierarchy, namespace policy, AVC dissolution policy
- [`docs/AVC-IDENTITY-MAPPING-V1.md`](docs/AVC-IDENTITY-MAPPING-V1.md) — Wave 5 finding: AVC identity-core vs TG/AIE verdicts per entity
- [`docs/AVC-TENANT-MAPPING-V1.md`](docs/AVC-TENANT-MAPPING-V1.md) — Wave 5 finding: tenant-admin vs runtime-isolation layers, lifecycle gap

## Other key artifacts

- [`docs/ABDE-BRAND-ARCHITECTURE-v0.2.md`](docs/ABDE-BRAND-ARCHITECTURE-v0.2.md) — provisional brand architecture
- [`docs/NAMING-STANDARD-v0.1.md`](docs/NAMING-STANDARD-v0.1.md) — naming rules
- [`docs/evidence-layer-model.md`](docs/evidence-layer-model.md) — evidence separation model
- [`docs/PLATFORM-BOUNDARY-CHARTER-v0.1.md`](docs/PLATFORM-BOUNDARY-CHARTER-v0.1.md) — original platform boundary charter
- [`docs/ACC-BOUNDARY-PROPOSAL-v0.1.md`](docs/ACC-BOUNDARY-PROPOSAL-v0.1.md) — continuity boundary proposal/history

## System visuals

<p align="center">
  <img src=".github/assets/architecture/system-context.svg" alt="Platform Governance in the Aftergraph ecosystem context" width="90%">
</p>

<p align="center">
  <img src=".github/assets/architecture/architecture.svg" alt="Platform Governance system architecture" width="90%">
</p>

<p align="center">
  <img src=".github/assets/architecture/workflow.svg" alt="Platform Governance primary workflow" width="90%">
</p>

## License

Apache-2.0

---

**Brand status:** Aftergraph / ABDE Intelligence are PROVISIONAL — NOT TRADEMARK CLEARED. No irreversible naming migration should be inferred from this technical reconciliation.
