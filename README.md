# ABDE Intelligence — Platform Governance

> Infrastructure for governed autonomous intelligence.

**Brand status:** ABDE Intelligence is the current provisional company/platform candidate and has **not** completed trademark clearance.

**Namespace status:** GitHub organization `@Aftergraph` is a temporary working namespace pending final brand clearance.

**Architecture (provisional):**

```
ABDE Intelligence
├── ABDE Platform
│   ├── Agent Workforce
│   ├── Trust Gateway
│   ├── WORKS
│   └── Adaptive Workspace / Plugin Runtime
├── ABDE Research
│   └── Jonas Abde Intelligence Systems Research Program
├── AIE
│   └── independent Agentic Institution Engineering standards track
└── After Graph
    └── research thesis / initiative / narrative
```

## Modules

| Module | Repo | Role |
|--------|------|------|
| **Agent Workforce** | (in [Aftergraph/trust-gateway](https://github.com/Aftergraph/trust-gateway)) | User/developer-facing product layer |
| **Trust Gateway** | [Aftergraph/trust-gateway](https://github.com/Aftergraph/trust-gateway) | Runtime control and enforcement plane |
| **WORKS** | [Aftergraph/works-execution](https://github.com/Aftergraph/works-execution) | Durable execution plane |
| **AIE** | [Aftergraph/aie](https://github.com/Aftergraph/aie) | Independent normative authority/institution standards track |
| **ABDE Research (ISR Program)** | [Aftergraph/intelligence-systems-research](https://github.com/Aftergraph/intelligence-systems-research) | Labs / Evals / Assurance |

Canonical definitions: ABDE Platform (product), ABDE Research (research-facing identity), AIE (independent standards track), After Graph (research thesis) — see [docs/ABDE-BRAND-ARCHITECTURE-v0.2.md](docs/ABDE-BRAND-ARCHITECTURE-v0.2.md) and [docs/NAMING-STANDARD-v0.1.md](docs/NAMING-STANDARD-v0.1.md).

## Governance

Everything extensible is a plugin. Everything consequential is governed.

- **Executable = Intersection(AIE policy, WORKS execution, TG enforcement)**
- AIE MAY define policies that TG and WORKS MUST follow
- WORKS NEEDS valid authorization from AIE before persisting
- Runtime (TG) HAS the authority to block or permit based on AIE policy
- Research evaluates but does not automatically claim

Claim inheritance is unidirectional (normative → operational); runtime evidence does not automatically establish AIE conformance or scientific claims.

## Cross-Repo Contracts (normative)

cpi/1.0, rab/1.0, identity/1.0, policy.token/1.0, secret.ref/1.0, shell.contracts/1.0, link.wire/1.0, pairing/1.0, brain.ns/1.0, release.rings/1.0, evidence.schema/1.1, kernel.budget/1.0, kernel.lifecycle/1.0

## Evidence Layers (correlation: mission_id + actionId)

| Layer | Producer | Format |
|---|---|---|
| L1 Action Audit | Trust Gateway | hash-chain entry |
| L2 Execution Quittance | WORKS | content-addressed bundle |
| L3 Institutional Conformance | AIE | conformance vectors + PolicyDecisionRecord |
| L4 Scientific Evidence | ISR | STUDY-011/MISSION-Bench (Wilson CI, preregistration) |

No layer may upgrade another; promotion requires explicit owner approval + a decision record + conformance evidence.

## Key artifacts

- [docs/ABDE-BRAND-ARCHITECTURE-v0.2.md](docs/ABDE-BRAND-ARCHITECTURE-v0.2.md) — provisional brand architecture (20 sections)
- [docs/NAMING-STANDARD-v0.1.md](docs/NAMING-STANDARD-v0.1.md) — naming conventions and the no-ABDE-prefix rule
- [docs/PUBLIC-INFO-ARCHITECTURE-v0.1.md](docs/PUBLIC-INFO-ARCHITECTURE-v0.1.md) — future website IA
- [docs/reconciliation-matrix.md](docs/reconciliation-matrix.md) — 15-concept reconciliation
- [docs/evidence-layer-model.md](docs/evidence-layer-model.md) — 4-layer evidence model
- [docs/cross-repo-contracts.md](docs/cross-repo-contracts.md) — contract register
- [docs/PLATFORM-BOUNDARY-CHARTER-v0.1.md](docs/PLATFORM-BOUNDARY-CHARTER-v0.1.md) — role allocation + claim inheritance

## License

Apache-2.0

---

**Brand status:** Aftergraph / ABDE Intelligence are PROVISIONAL — NOT TRADEMARK CLEARED. No irreversible branding until clearance (see intelligence-systems-research `docs/BRAND-STATUS-2026-09-04.md`).