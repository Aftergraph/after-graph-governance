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
Experience / Work Intelligence
  studio · wi-frontend · wi-backend
          ↓
Intent / Context
  Wie · context-continuity
          ↓
Authority / Trust
  AIE → Trust Gateway
          ↓
Runtime / Durable Execution
  Runtime → WORKS
          ↓
Evidence / Verification
  Sentinel · Continuum · domain verifiers
          ↓
Verified outcomes

Cross-cutting
  skills-vault · llm-research-development · afm · model-registry · intelligence-systems-research

Migration lineage
  autonomous-venture-company
```

The canonical Governance topology contains **21 canonical repositories** at the 2026-09-08 evidence cut: **12 public / 9 private**. Ephemeral proof/test infrastructure is outside the canonical topology and must not be folded into product identity or compatibility claims.

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

Topology membership is not evidence of functional conformance, production readiness, scientific validity or APC compatibility.

## Core ownership boundaries

| Plane | Repository | Canonical responsibility |
|---|---|---|
| Governance | `after-graph-governance` | topology, cross-repo contracts, boundaries, exact-head generation |
| Institution | `aie` | authority, delegation, lifecycle, budget/revocation semantics |
| Enforcement | `trust-gateway` | runtime admission, approvals, policy enforcement and action audit |
| Runtime | `runtime` | agent lifecycle, orchestration, dispatch, checkpoints, metering, observability and model-edge integration |
| Execution | `works-execution` | durable work, scheduling, workers, recovery, evidence/quittance |
| Experience | `studio` | general-purpose Chat / Work / Space human environment |
| Work Intelligence | `wi-backend` | source-neutral observations → canonical Wie WorkItems |
| Specialist experience | `wi-frontend` | Wie browser experience and least-privilege BFF |
| Continuity | `context-continuity` | portable actionable state transfer across runtime/session boundaries |
| Verification | `sentinel` | exact-HEAD software review and cited verification evidence |
| Assurance | `continuum` | continuity/containment fault-injection campaigns |
| Research assurance | `intelligence-systems-research` | SPEC-001, MISSION-Bench, scientific claims and assurance evidence |
| Capabilities | `skills-vault` | governed skill discovery, lifecycle, trust and provenance |
| Models | `llm-research-development` | reusable model R&D/evaluation/promotion methodology |
| Models | `afm` | AFM-specific model program |
| Models | `model-registry` | immutable promoted model metadata/lifecycle |
| Migration | `autonomous-venture-company` | Legacy migration source while responsibilities move to canonical Aftergraph repos |
| Knowledge | `docs` | provenance-pinned rendering/discovery; not upstream truth owner |
| Public | `aftergraph.org` | website/front door/launcher; visibility does not upgrade evidence |
| Foundation | `brand` | visual identity, design tokens and master assets |
| Foundation | `.github` | organization/community/security/support defaults |

## Product identity

Public product identity is intentionally smaller than repository topology.

```text
Studio by Aftergraph
Sentinel by Aftergraph
Wie by Aftergraph
Continuum by Aftergraph
```

**Wie by Aftergraph** maps to the canonical source repositories `wi-backend` and `wi-frontend`. Repository names remain canonical for source/provenance; public product naming does not rename Git history or silently rewrite compatibility identifiers.

`Wie WorkItem != WORKS Work`. The specialist UI remains a projection over canonical backend state, and approval does not itself become durable execution.

## Runtime boundary

Aftergraph Runtime is now a canonical platform repository.

```text
AIE authority
    ↓
Trust Gateway admission/enforcement
    ↓
Runtime agent operation/orchestration
    ↓
WORKS durable governed execution
    ↓
Evidence
    ↓
independent verification
```

Runtime owns how an agent operates. WORKS owns how consequential work becomes durable, governed and replayable. Trust Gateway owns runtime admission/enforcement. AIE owns authority semantics. Runtime does not self-declare independently verified completion.

The existence of the Runtime repository does not itself establish an `APC-1/runtime` claim. Compatibility remains an evidence question.

## AVC migration boundary

`autonomous-venture-company` is a **Legacy migration source**. It receives no new canonical platform responsibilities while migration is active.

The canonical topology role is `migration-source`. Historical records may retain old AVC identifiers and roles when required for provenance, but they do not become current platform naming.

Archive or destructive removal requires the separately governed dissolution gates and explicit owner approval.

## Governance

> **Everything extensible is a plugin. Everything consequential is governed.**

For consequential execution the governing composition remains:

```text
Executable = Intersection(AIE authority/policy, Trust Gateway runtime admission, WORKS durable execution)
```

Runtime orchestrates activity inside that governed boundary; it does not widen authority by existing.

No UI, model, skill, plugin, research result, repo membership or textual agent declaration grants execution authority by itself.

## Cross-repo contracts

The normative register is maintained in [`docs/cross-repo-contracts.md`](docs/cross-repo-contracts.md).

Current registered families include:

`cpi/1.0`, `rab/1.0`, `identity/1.0`, `policy.token/1.0`, `secret.ref/1.0`, `shell.contracts/1.0`, `link.wire/1.0`, `pairing/1.0`, `brain.ns/1.0`, `release.rings/1.0`, `evidence.schema/1.1`, `kernel.budget/1.0`, `kernel.lifecycle/1.0`, `principal/1.0`, `tenant/1.0`, `execution-context/1.0`, `correlation/1.0`, `mission-state/1.0`, `org-state/1.0`.

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

Consumers (Hermes/Codex/Aftergraph agents, CI, reviewers) MUST verify exact heads against a fresh generated contract before gap analysis, delegation or merge decisions. A SHA in a handoff, roadmap or briefing is a claim; a fresh generated org-state is remote truth.

`latest-org-state.json` is generated only. Topology migrations MUST NOT be implemented by manually editing its SHAs, repository entries or timestamps.

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
- exact-head state does not prove functional conformance;
- canonical topology membership does not prove APC compatibility.

## Platform reconciliation

Current governed truth is projected through:

- [`docs/platform-topology/1.0.json`](docs/platform-topology/1.0.json) — canonical machine-readable repository topology
- [`dependencies.yml`](dependencies.yml) — platform dependency/ownership graph
- [`docs/cross-repo-contracts.md`](docs/cross-repo-contracts.md) — normative contract register + repository boundaries
- [`docs/PLATFORM-ARCHITECTURE-V3.md`](docs/PLATFORM-ARCHITECTURE-V3.md) — current seven-plane ownership architecture
- [`docs/reconciliation-matrix.md`](docs/reconciliation-matrix.md) — concept-level reconciliation
- [`docs/REPOSITORY-REGISTRY-v0.1.md`](docs/REPOSITORY-REGISTRY-v0.1.md) — repository/worktree controls and historical reconciliation queue
- [`docs/AVC-IDENTITY-MAPPING-V1.md`](docs/AVC-IDENTITY-MAPPING-V1.md) — AVC identity-core vs TG/AIE mapping evidence
- [`docs/AVC-TENANT-MAPPING-V1.md`](docs/AVC-TENANT-MAPPING-V1.md) — tenant-admin vs runtime-isolation mapping evidence

Older reconciliation documents remain useful historical evidence cuts but do not override the current topology contract.

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
