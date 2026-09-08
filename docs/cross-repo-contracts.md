# Cross-Repo Contract Register

> Normative contract ownership and consumption map for the Aftergraph platform.
> The original five-repository execution core remains important, but it is no
> longer the complete organization topology. Repository scope/roles are defined
> by `docs/platform-topology/1.0.json`; exact remote state is generated into
> `latest-org-state.json`.

## Normative contract register

| Contract | Normative | Owner Repo | Primary Consumer Repos |
|---|---|---|---|
| `cpi/1.0` | Yes | ISR (program) | TG, AIE, WORKS |
| `rab/1.0` | Normative | ISR (program) | TG, AIE, WORKS |
| `identity/1.0` | Normative | AIE | TG, WORKS |
| `policy.token/1.0` | Normative | TG | AIE, WORKS |
| `secret.ref/1.0` | Normative | TG | AIE, WORKS |
| `shell.contracts/1.0` | Normative | WORKS | TG, AIE |
| `link.wire/1.0` | Normative | WORKS | TG, AIE |
| `pairing/1.0` | Normative | WORKS | TG, AIE |
| `brain.ns/1.0` | Normative | AIE | TG, WORKS |
| `release.rings/1.0` | Normative | after-graph-governance | WORKS, AIE, TG |
| `evidence.schema/1.1` | Normative | WORKS | TG, AIE, ISR |
| `kernel.budget/1.0` | Normative | WORKS | TG, AIE |
| `kernel.lifecycle/1.0` | Normative | ISR | TG, WORKS, AIE |

This table records normative contracts only. A repository appearing in the
platform topology does **not** automatically become a normative contract owner.

## Platform Convergence V2.1 contract families

V2.1 adds four narrower canonical families without rewriting `identity/1.0`.
`identity/1.0` remains a preserved compatibility contract, and its
`runtime.lease_id` continues to mean the WORKS/runtime worker lease. It is never
reinterpreted as an AIE AuthorityLease.

| Contract | Normative | Owner Repo | Responsibility |
|---|---|---|---|
| `principal/1.0` | Normative | AIE | Canonical actor identity used for authority evaluation; identity does not itself grant authority. |
| `tenant/1.0` | Normative | Trust Gateway | Canonical runtime-isolation identity; workspace/project/session identity is not a tenant root. |
| `execution-context/1.0` | Normative | WORKS | Immutable correlation/binding envelope for durable execution; it is not an authorization token. |
| `correlation/1.0` | Normative | after-graph-governance | Minimal transportable cross-repo reference envelope; possession grants no execution authority. |

The machine-readable V2.1 family registry lives at
`docs/contracts/platform-convergence-v2-1/registry.json`. Governance registers
contract ownership and compatibility; runtime semantics remain in each owning
repository.

## Experimental platform fabric contracts

The following contracts are **experimental** and therefore intentionally absent
from the normative register above. They are implementation/research candidates,
not frozen platform law.

| Contract | Status | Semantic Owner | Purpose |
|---|---|---|---|
| `platform-event-ref/0.1` | Experimental | Governance registration; domain events remain TG/WORKS-owned | Correlates heterogeneous native events without replacing their envelopes or granting authority. |
| `capability-action/0.1` | Experimental | Runtime semantics; Governance registration | Separates semantic execution intent from provider/runtime-specific implementation while preserving authority bounds. |

Machine-executable Phase-0 vectors live at
`docs/platform-conformance/v0.1/vectors.json` and are exercised by
`scripts/test_platform_fabrics_v0_1.py`. Passing them establishes contract-level
conformance only. It does not establish runtime integration or platform
verification. See `docs/PLATFORM-FABRICS-v0.1.md`.

## Platform repository boundaries

| Repository | Role | Boundary |
|---|---|---|
| `after-graph-governance` | canonical-contracts | Topology, cross-repo boundaries, contract registration, exact-head generation mechanics. |
| `aie` | normative-authority | Institution/authority semantics; does not execute work. |
| `trust-gateway` | runtime-enforcement | Runtime admission/enforcement/audit; does not become durable execution truth. |
| `works-execution` | durable-execution | Durable work state, workers, recovery and execution evidence. |
| `studio` | primary-experience | General-purpose human Chat/Work/Space/control experience. |
| `work-intelligence-v2` | work-inference | Observation → WorkItem; a WorkItem is not a WORKS Work. |
| `work-intelligence-web` | work-intelligence-experience | Specialist UI/BFF projection of Work Intelligence state. |
| `context-continuity` | continuity-contract | Portable actionable state transfer; carries authority context but never grants authority. |
| `continuum` | continuity-containment-verification | Fault-injection campaigns for continuity/containment; does not redefine ISR claims. |
| `intelligence-systems-research` | research-assurance | Scientific claims, SPEC-001, MISSION-Bench, assurance and publication evidence. |
| `skills-vault` | capability-supply-chain | Skill trust/lifecycle/provenance/discovery/distribution. |
| `llm-research-development` | model-rnd-methodology | Reusable model experiment/eval/promotion methodology. |
| `afm` | model-program | AFM-specific training/data/evals/artifact manifests. |
| `model-registry` | model-lifecycle-registry | Immutable promoted model metadata and aliases. |
| `autonomous-venture-company` | venture-os-consumer | Venture OS/reference consumer; not a second canonical platform kernel. |
| `docs` | knowledge-plane | Renders/discovers repo-owned truth with provenance; owns no upstream claim. |
| `aftergraph.org` | public-front-door | Public site/launcher; visibility never upgrades evidence. |
| `brand` | brand-design-system | Visual identity/tokens/assets, not runtime semantics. |
| `.github` | organization-community | Org profile/community/security/support defaults. |

## AIE binding claims

| Binding | Description | Owner |
|---|---|---|
| MCP | Model Context Protocol binding | AIE |
| A2A | Agent-to-Agent protocol binding | AIE |
| SPIFFE-OIDC | SPIFFE + OIDC auth binding | AIE |
| OPA | Open Policy Agent integration | AIE |
| OTel | OpenTelemetry integration | AIE |
| Temporal | Temporal workflow integration | AIE |
| OWASP-ACS | OWASP Agent Control Standard alignment | AIE |

Bindings are conformance/integration claims inside AIE's evidence boundary;
they do not automatically become platform-wide scientific or production claims.

## Trust Gateway runtime guarantees

| # | Guarantee |
|---|---|
| 1 | Policy enforcement at runtime |
| 2 | Runtime compliance verification |
| 3 | Policy propagation |
| 4 | Evidence-lag handling |
| 5 | Cross-module audit trail |
| 6 | Trust boundary enforcement |

## Executability boundary

For consequential execution, the governing model remains:

```text
Executable = Intersection(AIE authority/policy, TG runtime admission, WORKS durable execution)
```

No UI, plugin, model, skill, research result or repository membership grants
execution authority by itself.

## Evidence inheritance

- runtime evidence does not establish AIE conformance;
- AIE conformance does not establish scientific validity;
- research evidence does not grant runtime authority;
- public visibility does not upgrade maturity;
- generated exact-head state does not imply functional conformance.

## Boundary charter

See `docs/PLATFORM-BOUNDARY-CHARTER-v0.1.md` for the original charter and
`docs/superpowers/specs/2026-09-07-aftergraph-platform-reconciliation-v1-design.md`
for the 19-repository reconciliation target.

The core principle remains:

> **Everything extensible is a plugin. Everything consequential is governed.**
