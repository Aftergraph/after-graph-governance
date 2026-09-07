# Aftergraph Release, Lifecycle & Compatibility Standard — Design v2

**Date:** 2026-09-07  
**Status:** Approved design; pending written-spec review  
**Scope owner:** `Aftergraph/after-graph-governance`  
**Public generation:** **Aftergraph 26**  
**Generation codename:** **Convergence**  
**Release standard:** **Aftergraph Release Standard (`ARS/1`)**  
**Platform compatibility:** **Aftergraph Platform Compatibility (`APC-1`)**  
**Companion design:** [`Aftergraph Release Intelligence Plane`](2026-09-07-aftergraph-release-intelligence-plane-design.md)

---

## 1. Decision

Aftergraph will present one coherent public platform generation while retaining independent technical identities for products, components, contracts, models, deployments, and exact evidence.

The approved public release family is:

```text
AFTERGRAPH 26
CONVERGENCE
```

`Aftergraph 26` is a **public platform generation**. It is not a package version, API version, model version, Git tag, deployment identifier, or instruction to force repositories into synchronized release numbers.

The technical compatibility baseline is separate:

```text
APC-1
```

The governing model is:

```text
Aftergraph 26         public platform generation
Convergence           generation narrative
2026.09               release train identifier
APC-1                 technical platform compatibility baseline
<product version>     end-user product release
<component version>   implementation version
<contract version>    machine interface version
<model version>       model identity
<commit/digest>       exact provenance and evidence subject
```

The number `26` is associated with the 2026 release family but does **not** roll automatically at a calendar boundary. A successor generation exists only when Governance explicitly declares one.

A future public generation may continue to use the same technical compatibility baseline. For example, `Aftergraph 27 / APC-1` is valid if the public generation changes without a platform-wide compatibility break.

---

## 2. Why generation and compatibility are separate

Aftergraph has different kinds of independently evolving systems: end-user products, control-plane services, runtime/execution infrastructure, contracts, models, research artifacts, developer tooling, public projections, migration sources, and ephemeral test infrastructure.

A single global version would create false equivalence between unlike things and would force meaningless synchronized releases.

Separating the public generation from technical compatibility solves two different problems:

- **Aftergraph 26** answers: *Which public platform generation does this belong to?*
- **APC-1** answers: *Which technical platform compatibility baseline does this conform to?*

This allows mixed-version deployments without sacrificing a coherent public product family.

---

## 3. Public mental model

The public system is intentionally smaller than the repository graph.

```text
                         AFTERGRAPH 26
                          CONVERGENCE

              Infrastructure for verified
                    intelligent systems

                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
     PRODUCTS              PLATFORM              RESEARCH
        │                     │                     │
     Studio                Authority                AIE
     Sentinel              Trust                    ISR
     Work Intelligence     Runtime                  AFM
     Continuum             Execution                Benchmarks
                           Evidence
                           Verification
```

The primary public product family is:

- **Studio by Aftergraph** — operate and interact with intelligent systems.
- **Sentinel by Aftergraph** — verified software review and software-domain verification.
- **Work Intelligence by Aftergraph** — understand and structure work.
- **Continuum by Aftergraph** — continuity and containment assurance.

The primary platform capability vocabulary is:

```text
Authority · Trust · Runtime · Execution · Evidence · Verification
```

Repository topology remains visible in developer and governance surfaces but is not the customer-facing product model.

---

## 4. Repository reality versus product reality

The current organization has 21 installed repositories: 20 canonical platform repositories and one ephemeral Sentinel firetest repository.

This count is an implementation/governance fact, not a branding primitive. Public copy MUST NOT depend on the repository count remaining constant.

Repository identities remain canonical for ownership and implementation. Product identities remain canonical for public navigation.

Examples:

```text
Work Intelligence
├── wi-frontend
└── wi-backend
```

`wi-backend` and `wi-frontend` are the canonical GitHub identities. Historical names may remain only as compatibility aliases or provenance where needed.

For continuity:

```text
Continuum by Aftergraph
├── continuum             continuity/containment assurance and fault campaigns
└── context-continuity    actionable context/state transfer dependency
```

This grouping MUST NOT collapse ownership boundaries. `context-continuity` owns portable actionable state transfer. `continuum` owns continuity/containment assurance and fault injection.

`autonomous-venture-company` remains a Legacy/migration source and MUST NOT gain new canonical platform responsibilities during dissolution.

`sentinel-firetest` remains Ephemeral and outside canonical platform/product counts. Archive or deletion requires separate destructive approval.

---

## 5. Version identity model

Aftergraph standardizes the following independent identities.

| Identity | Example | Meaning |
|---|---|---|
| Public generation | `Aftergraph 26` | Human-facing product/platform generation |
| Generation narrative | `Convergence` | Brand/release story, non-technical |
| Release train | `2026.09` | Concrete cross-platform release/update window |
| Platform compatibility | `APC-1` | Technical compatibility baseline |
| Product release | `Sentinel 1.0` | End-user product release |
| Component version | `sentinel-engine 1.4.0` | Concrete implementation version |
| Contract version | `evidence/1.1` | Machine-facing interface promise |
| Model version | `AFM-0.12` | Model identity and lifecycle |
| Evidence identity | commit SHA / artifact digest | Exact reproducibility and subject binding |

These identities MUST NOT be silently substituted for one another.

Examples:

```text
Aftergraph 26          != APC-1
APC-1                  != Sentinel 1.0
Sentinel 1.0           != sentinel-engine 1.4.0
sentinel-engine 1.4.0  != evidence/1.1
AFM-0.12               != Aftergraph 26
Aftergraph 26          != exact commit SHA
```

Public surfaces SHOULD expose the smallest useful subset. Auditor and developer surfaces MAY expose deeper identities.

---

## 6. Release trains

Cross-platform release communication uses a separate release-train identifier rather than overloading the generation number.

Preferred machine form:

```text
2026.09
2026.10
2026.11
```

Public form may be:

```text
Aftergraph 26 — September 2026 Update
```

A release train may include product features, documentation changes, model candidates, security fixes, contract additions, and component upgrades while leaving `APC-1` unchanged.

`Aftergraph 26.1`, `Aftergraph 26.2`, and similar notation SHOULD NOT be the primary cross-platform release-train scheme because it visually conflates generation and compatibility.

---

## 7. Aftergraph Platform Compatibility (`APC`)

`APC` is the machine-facing compatibility framework.

```text
APC-1
```

means that a component conforms to the applicable baseline requirements and role-specific profile(s) for Platform Compatibility Level 1.

`APC` is not a maturity label and does not transfer authority, production status, scientific validity, or verification authority.

A public statement such as:

```text
Built for Aftergraph 26
```

is brand/product copy.

A technical statement such as:

```text
APC-1/verifier: CONFORMANT
```

is a conformance claim and requires machine-readable evidence.

---

## 8. APC common baseline

Every APC-conformant component MUST satisfy the common requirements applicable to its role.

| Capability | Baseline rule |
|---|---|
| Identity | Consequential activity can be attributed where the component participates in actor/principal semantics |
| Authority | A component cannot silently self-grant consequential authority |
| Correlation | Mission/action correlation survives relevant boundaries |
| Execution | Durable consequential work creates durable records where execution responsibility applies |
| Budget | Applicable resource constraints can halt or deny activity |
| Revocation | Enforcement participants fail closed for revoked authority |
| Evidence | Material claims can bind to attributable evidence |
| Verification | `Complete != Verified` remains preserved |
| Observability | Relevant cross-system seams are correlatable |
| Provenance | Source/build identity can be resolved for conformance evidence |
| Lifecycle | Stability state is explicit and machine-readable |

Not every repository implements every capability. Role profiles define the additional obligations that apply to a particular class of component.

---

## 9. APC profiles

The initial APC profile set is:

```text
APC-1/authority
APC-1/service
APC-1/runtime
APC-1/execution
APC-1/verifier
APC-1/product
APC-1/model
APC-1/research
```

The profile list is intentionally capability-oriented rather than repository-oriented.

Illustrative mapping:

| System | Primary profile |
|---|---|
| AIE | `authority` |
| Trust Gateway | `service` |
| Aftergraph Runtime | `runtime` once a canonical implementation exists |
| WORKS | `execution` |
| Sentinel | `verifier` |
| Studio | `product` |
| Work Intelligence surfaces | `product` and/or `service` as applicable |
| AFM / promoted model artifacts | `model` |
| ISR/AIE research artifacts | `research` where APC participation is meaningful |

A repository does not need an APC profile merely because it exists in the organization. Brand, `.github`, and other projection/foundation repositories may remain outside APC conformance if they do not participate in runtime/platform compatibility.

Sentinel is a software-domain verifier. The platform Verification capability remains extensible to other domain verifiers.

Runtime remains a planned target-state plane until a canonical implementation exists. No current repository may claim `APC-1/runtime` merely to fill the architectural box.

---

## 10. Minimum and tested-against compatibility

A binary `compatible: true` field is insufficient.

Components SHOULD declare compatibility in a form that distinguishes minimum support from the baseline actually tested.

Example:

```yaml
compatibility:
  minimum: APC-1
  tested_against: APC-1
  profiles:
    - verifier
```

When multiple APC levels exist, a component MAY declare an explicit supported set only when each supported claim is backed by conformance evidence.

Example:

```yaml
compatibility:
  supports:
    - APC-1
    - APC-2
  tested_against: APC-2
```

A declaration is not evidence by itself.

---

## 11. Version skew policy

Aftergraph supports mixed-version deployments deliberately. Compatibility is defined by verified combinations and contracts, not by forcing all components to share a version number.

The initial platform skew rules are:

1. Authority and Trust components MUST share a compatible APC major or have an explicitly registered bridge.
2. Trust and Runtime MUST share a compatible principal/authority contract set.
3. Runtime and WORKS MUST have a registered compatibility relation for durable execution semantics.
4. WORKS and verifiers MUST agree on the evidence/subject semantics needed for independent verification.
5. Product UI and backend combinations MUST declare supported API/contract ranges.
6. Models MUST declare the runtime/capability expectations they require; model identity does not imply runtime compatibility.
7. Research compatibility MUST NOT be inherited as production compatibility.
8. An untested edge is not silently upgraded to compatible because both endpoints individually conform to the same APC level.

The Release Intelligence design defines how these edges are represented, tested, and queried.

---

## 12. Lifecycle vocabulary and guarantees

Aftergraph adopts one shared lifecycle vocabulary.

| State | Meaning | Compatibility promise |
|---|---|---|
| **Stable** | Supported production interface | No breaking change inside the same stable contract major; governed migration required |
| **Preview** | Evaluation or limited production use | Breaking change possible with migration notice |
| **Experimental** | Rapidly evolving implementation | No compatibility guarantee |
| **Research** | Scientific/research artifact | Evidence/reproducibility obligations; no production guarantee |
| **Legacy** | Maintained primarily for migration | No new canonical responsibilities |
| **Deprecated** | Replacement or retirement announced | Frozen/maintenance path until published sunset |
| **Retired** | No longer supported | No compatibility promise |
| **Ephemeral** | Temporary test/proof infrastructure | No platform compatibility guarantee |

Lifecycle is independent of public generation and APC conformance.

A component MUST NOT become Stable merely because it participates in Aftergraph 26 or passes an APC profile.

---

## 13. Deprecation and sunset policy

Deprecation is machine-readable and time-bound.

A deprecation record SHOULD include:

```yaml
lifecycle:
  status: deprecated
  deprecated_at: 2026-09-01
  sunset_at: 2027-09-01

replacement:
  contract: evidence/2.0
```

Default support policy:

- Stable platform contracts and stable public APIs: **minimum 12 months after a declared successor**, unless a security/safety emergency requires an explicitly documented exception.
- Preview interfaces: **90 days notice where practical**, unless the preview terms explicitly state a shorter experimental window.
- Experimental: no support-duration guarantee.
- Research: governed by research provenance and reproducibility rules rather than production API support promises.

A specific contract may promise longer support but MUST NOT silently promise less than the applicable default after being marked Stable.

---

## 14. Breaking-change rules

For Stable machine contracts, the following are breaking unless an existing compatibility rule explicitly proves otherwise:

- removing or renaming a field;
- changing a field type incompatibly;
- making an optional field required;
- changing authority interpretation;
- changing tenant/principal isolation semantics;
- changing evidence subject-binding semantics;
- changing verifier validity/staleness semantics;
- narrowing accepted identity formats without a bridge;
- materially changing deny/failure semantics;
- removing a previously guaranteed lifecycle behavior.

A breaking machine contract generally requires a contract major-version change.

A contract major-version change does **not** automatically require an APC major change.

`APC-2` is required only when the platform-wide compatibility baseline itself changes materially, such as a new mandatory cross-platform identity, authority, evidence, or execution invariant that cannot be satisfied under APC-1 compatibility rules.

---

## 15. Generation-change policy

A new public generation is a governed product/platform declaration, not an automatic yearly tick.

A successor generation is justified by one or more of:

- a major public platform/product family change;
- a new coherent design/experience generation;
- a major platform capability expansion;
- a new release narrative significant enough to warrant a public generation boundary;
- a major compatibility transition that should also be communicated publicly.

The valid relationships include:

```text
Aftergraph 26 / APC-1
→ Aftergraph 27 / APC-1
```

for a public-generation change without a fundamental technical break, and:

```text
Aftergraph 26 / APC-1
→ Aftergraph 27 / APC-2
```

when both public generation and technical compatibility change.

`Aftergraph 26 / APC-2` is technically possible but SHOULD trigger explicit Governance review because a platform-wide compatibility break often deserves a public-generation decision as well.

---

## 16. Upgrade model

Platform compatibility upgrades are staged rather than big-bang.

Canonical transition model:

```text
CURRENT
APC-1
   ↓
DUAL SUPPORT
APC-1 + APC-2
   ↓
TARGET TESTING
component tested against APC-2
   ↓
CONFORMANCE
APC-2 profile PASS
   ↓
PROMOTION
APC-2 becomes preferred
   ↓
DEPRECATION
APC-1 sunset announced
   ↓
RETIREMENT
APC-1 no longer supported
```

Where state/data migration is involved, an upgrade path MUST define rollback or explicitly state why rollback is impossible.

---

## 17. Machine-readable component manifest

A common component manifest SHOULD be introduced as the machine-readable release declaration.

Conceptual form:

```yaml
schema: aftergraph.component/1

identity:
  product: sentinel
  component: sentinel-engine

release:
  version: 1.4.0
  lifecycle: stable

platform:
  generation: 26
  release_train: "2026.09"

compatibility:
  level: APC-1
  profiles:
    - verifier
  minimum: APC-1
  tested_against: APC-1

contracts:
  verdict: "1.0"
  evidence: "1.1"
  correlation: "1.0"

provenance:
  repository: Aftergraph/sentinel
  commit: <exact-sha>

conformance:
  profile: APC-1/verifier
  result: pass
  evidence: <receipt-reference>
```

The schema MUST allow non-applicable fields to be absent.

The manifest MUST NOT become a second source of repository topology. Governance topology owns repository identity/ownership. The component manifest owns release, lifecycle, compatibility, contract, and provenance declarations for a component.

---

## 18. Contract versioning

Machine contracts remain independently versioned.

Examples:

```text
principal/1.0
correlation/1.0
mission/1.x
evidence/1.x
verdict/1.0
```

Platform generation changes do not automatically require contract major changes.

Contract changes that remain compatible with the active APC baseline may ship inside the same platform generation and APC level.

This prevents branding and release cadence from becoming protocol-breaking events.

---

## 19. Model versioning

Model identity remains independent.

Correct:

```text
AFM-0.9
AFM-0.12
Public generation association: Aftergraph 26 research baseline
Compatibility target: APC-1/model, where conformance is actually defined and evidenced
```

Rejected:

```text
AFM 26
```

unless a future model product independently adopts that product naming.

A model MAY support multiple APC levels if each claim is backed by evidence.

Model registry state, frozen references, promotion candidates, benchmark evidence, and deployment aliases remain separate from public platform generation.

---

## 20. Exact evidence and provenance

Aftergraph preserves exact-head evidence as a deeper technical identity.

A release should be resolvable through progressively stronger identity:

```text
Aftergraph 26
→ release train 2026.09
→ APC-1/verifier
→ Sentinel 1.0
→ sentinel-engine 1.4.0
→ evidence/1.1
→ exact commit
→ artifact digest
→ conformance/verification receipt
```

No generation, lifecycle, or compatibility label may replace exact-subject binding where exact evidence is required.

A moved HEAD can invalidate an exact verification receipt without invalidating the existence of the public Aftergraph 26 generation or the APC-1 standard itself.

---

## 21. Public website architecture

The public navigation SHOULD converge on:

```text
Aftergraph
Products
Platform
Developers
Research
Company
```

Hero direction:

```text
AFTERGRAPH 26
CONVERGENCE

Infrastructure for verified intelligent systems.

Build, operate and verify intelligent systems
across one governed execution platform.
```

Product section:

```text
FOUR PRODUCTS. ONE SYSTEM.

Studio
Operate intelligent systems.

Sentinel
Verify software before it ships.

Work Intelligence
Turn work into structured intelligence.

Continuum
Prove systems survive failure.
```

Platform section:

```text
Authority
Trust
Runtime
Execution
Evidence
Verification
```

The public site MUST NOT present each canonical repository as a peer end-user product.

`Built for Aftergraph 26` is acceptable brand copy. `APC-1 conformant` is a technical claim and MUST resolve to conformance evidence.

---

## 22. Developer documentation architecture

Developer documentation SHOULD expose generation and compatibility separately.

Example header:

```text
Aftergraph 26
Release train: 2026.09
Platform compatibility: APC-1
```

Recommended navigation:

```text
Overview
Quickstart

Platform
├── Identity
├── Authority
├── Trust
├── Runtime
├── Execution
├── Evidence
└── Verification

Compatibility
├── APC levels
├── Profiles
├── Version skew
├── Upgrade paths
├── Deprecations
└── Conformance

APIs
Contracts
SDKs
CLI
Lifecycle
Changelog
```

Future-generation selectors MUST display only generations that actually exist.

---

## 23. GitHub organization presentation

The `.github` organization profile SHOULD group public projects by platform meaning rather than repository count.

Recommended grouping:

```text
Products
Studio · Sentinel · Work Intelligence · Continuum

Core Platform
AIE · Trust Gateway · WORKS · Runtime (when actually established)

Models & Capabilities
AFM · Model Registry · Skills

Research
Intelligence Systems Research

Foundation
Governance · Docs · Brand
```

The profile MAY show the current public generation and active compatibility level, but repository-specific technical versions stay in repository/developer surfaces.

---

## 24. Governance authority model

Ownership remains separated:

```text
Governance
owns schemas, APC rules, lifecycle vocabulary,
generation declarations and policy

Repositories/components
own their release declarations and evidence

Automation
checks declarations against policy and evidence

Docs / website / .github
project generated or governed truth
```

Governance MUST NOT become a manual bottleneck for every component release. The target model is centrally governed rules with decentralized declarations and automated conformance.

Public projections MUST NOT become competing canonical truth sources.

---

## 25. Release Intelligence relationship

The companion design [`Aftergraph Release Intelligence Plane`](2026-09-07-aftergraph-release-intelligence-plane-design.md) defines the machinery that makes this standard executable rather than documentary.

It provides the target concepts for:

- Compatibility Graph;
- APC Compiler;
- semantic contract diff;
- conformance evidence;
- Release Passport;
- Release Bill of Materials;
- release simulation;
- admission policy;
- verified upgrade paths;
- runtime capability negotiation;
- production compatibility telemetry;
- platform drift detection.

This standard defines **what compatibility means**. Release Intelligence defines **how compatibility is computed, evidenced, queried, and enforced in release workflows**.

---

## 26. Non-goals

This design does not:

- merge the polyrepo into a monorepo;
- rename all repositories;
- force all technical versions to `26.x`;
- claim that every repository is APC-conformant;
- create a canonical Runtime implementation;
- turn Sentinel into a universal verifier;
- upgrade research artifacts to production maturity;
- delete AVC or `sentinel-firetest`;
- allow AI-generated compatibility judgments to replace deterministic conformance evidence.

---

## 27. Acceptance criteria

The design is successfully implemented when:

1. `Aftergraph 26 · Convergence` has one canonical Governance definition.
2. `Aftergraph 26` is explicitly separated from `APC-1`.
3. A release-train identity such as `2026.09` is independent of generation and component semver.
4. `APC-1` has machine-readable common requirements and role profiles.
5. Technical compatibility claims resolve to conformance evidence.
6. Minimum support and tested-against semantics are representable.
7. Version-skew rules are machine-readable for relevant cross-component seams.
8. Lifecycle states carry explicit compatibility promises.
9. Deprecation and sunset metadata are machine-readable.
10. Stable contracts have a defined support window and breaking-change policy.
11. Mixed-version deployments are supported through compatibility relations rather than lockstep numbering.
12. Upgrade paths can represent dual support, promotion, deprecation, rollback, and retirement.
13. Product, component, contract, model, and exact-evidence versions remain distinct.
14. No bulk conversion to `26.x` occurs.
15. Public navigation presents a small product family rather than one product per repository.
16. `wi-backend` and `wi-frontend` remain canonical GitHub identities.
17. ACC/context-continuity and Continuum boundaries remain explicit.
18. Sentinel remains software-domain verification while Verification remains extensible.
19. Runtime remains planned until a canonical implementation exists.
20. AVC remains Legacy/migration source.
21. `sentinel-firetest` remains Ephemeral and outside canonical platform counts.
22. Public projections can be generated from Governance/component metadata without becoming independent sources of truth.
23. Exact SHA/digest evidence remains available for exact-subject claims.

---

## 28. Naming freeze

Approved names for this design:

```text
Masterbrand:             Aftergraph
Public generation:       Aftergraph 26
Generation codename:     Convergence
Release standard:        Aftergraph Release Standard
Release standard ID:     ARS/1
Platform compatibility:  Aftergraph Platform Compatibility
Compatibility level:     APC-1
```

Future codenames or future APC levels remain non-normative until separately governed.

---

## 29. Final target state

The system becomes understandable at progressively deeper levels:

```text
CUSTOMER
Aftergraph 26 · Convergence
    ↓
Studio · Sentinel · Work Intelligence · Continuum

PLATFORM ARCHITECT
Authority · Trust · Runtime · Execution · Evidence · Verification
    ↓
APC-1 profiles and compatibility graph

DEVELOPER
release train · APIs · contracts · component versions · lifecycle · upgrade paths

AUDITOR / RESEARCHER
exact commit · artifact digest · conformance receipt · benchmark · provenance
```

The intended unification model is:

> **One public generation. Independent systems. Explicit compatibility. Exact evidence.**
