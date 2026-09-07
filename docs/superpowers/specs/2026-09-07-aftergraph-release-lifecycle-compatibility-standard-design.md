# Aftergraph Release, Lifecycle & Compatibility Standard — Design

**Date:** 2026-09-07  
**Status:** Approved design; pending written-spec review  
**Scope owner:** `Aftergraph/after-graph-governance`  
**Public generation:** **Aftergraph 26**  
**Generation codename:** **Convergence**  
**Standard identifier:** `ARLCS/1.0`  
**Platform compatibility identifier:** `agp-26`

---

## 1. Decision

Aftergraph will present one coherent platform generation publicly while retaining independent technical versioning for products, components, contracts, models, deployments, and exact evidence.

The approved public release family is:

```text
AFTERGRAPH 26
CONVERGENCE
```

`Aftergraph 26` is a **platform generation and compatibility baseline**. It is not a monorepo version, Git tag, package version, API version, model version, or instruction to force every repository into lockstep release numbering.

The number `26` identifies the 2026 release family, but it does **not** roll automatically at a calendar boundary. A new generation exists only when Governance explicitly declares and publishes a successor baseline. An `agp-26` component may therefore remain supported after 2026.

The governing principle is:

> One platform generation above; precise independent version identities below.

This design deliberately separates the customer-facing product model from the implementation topology. Aftergraph currently has 21 installed GitHub repositories: 20 canonical platform repositories plus one ephemeral Sentinel firetest repository. Those repositories remain implementation and ownership units. They are not 21 public products.

---

## 2. Why this model

Mature software and AI platforms do not normally force every internal subsystem onto one version number. They unify naming, navigation, compatibility rules, lifecycle vocabulary, documentation, and release communication while allowing APIs, SDKs, engines, models, deployments, and source builds to carry the version identity appropriate to their contract.

Aftergraph needs the same separation because its repositories represent materially different kinds of things:

- end-user products;
- runtime and control-plane infrastructure;
- normative contracts;
- research programs;
- model development and model registry state;
- documentation and public projections;
- migration sources;
- ephemeral test infrastructure.

A single semantic version across all repositories would imply compatibility and maturity that do not exist and would cause unrelated repositories to release merely to preserve numerical alignment. That is rejected.

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

The public product family is:

- **Studio by Aftergraph** — operate and interact with intelligent systems.
- **Sentinel by Aftergraph** — verified software review and software-domain verification.
- **Work Intelligence by Aftergraph** — understand and structure work.
- **Continuum by Aftergraph** — continuity and containment assurance.

The platform capability vocabulary is:

```text
Authority · Trust · Runtime · Execution · Evidence · Verification
```

The platform implementation details remain discoverable in developer and architecture surfaces but are not the primary public navigation model.

---

## 4. Version identity model

Aftergraph standardizes six distinct version identities.

| Identity | Example | Meaning |
|---|---|---|
| Platform generation | `Aftergraph 26` / `agp-26` | Public generation and compatibility baseline |
| Product release | `Sentinel 1.0` | Release of an end-user product |
| Component version | `sentinel-engine 1.4.0` | Version of a concrete implementation unit |
| Contract version | `evidence/1.1` | Machine-facing compatibility contract |
| Model version | `AFM-0.12` | Model identity/lifecycle |
| Evidence identity | commit SHA / artifact digest | Exact reproducibility and subject binding |

These identities MUST NOT be silently substituted for one another.

Examples:

```text
Aftergraph 26           != Sentinel 1.0
Sentinel 1.0            != sentinel-engine 1.4.0
sentinel-engine 1.4.0   != evidence/1.1
AFM-0.12                != Aftergraph 26
Aftergraph 26           != git SHA
```

A public release can therefore say:

```text
Sentinel by Aftergraph
Built for Aftergraph 26
```

while developer metadata may say:

```text
Product: Sentinel 1.0
Engine: sentinel-engine 1.4.0
Platform: agp-26
Verdict contract: verdict/1.0
Evidence contract: evidence/1.1
Exact source: <git-sha>
```

---

## 5. Meaning of Aftergraph 26

`Aftergraph 26` MUST mean more than a visual label.

A component, product, or integration may claim `agp-26` compatibility only when it satisfies the applicable Aftergraph 26 compatibility baseline and can point to evidence for that claim.

The baseline is capability-oriented rather than repository-oriented.

### AGP-26 baseline

| Capability | Requirement |
|---|---|
| Identity | Consequential activity can be attributed to a principal/actor |
| Authority | A component cannot self-grant consequential authority |
| Correlation | Mission/action identity survives relevant system boundaries |
| Execution | Consequential durable work produces a durable record where required |
| Budget | Applicable resource constraints can stop execution |
| Revocation | Revoked authority fails closed where the component participates in enforcement |
| Evidence | Material claims can bind to attributable evidence |
| Verification | `Complete != Verified` remains preserved |
| Observability | Cross-system activity can be correlated at defined seams |
| Provenance | Source/build identity is available for compatibility evidence |
| Lifecycle | Stability state is explicitly declared |

Not every repository implements every capability. Compatibility is assessed against the subset applicable to the component's role. A documentation repository, model artifact, verifier, and runtime gateway therefore do not satisfy the baseline in identical ways.

Compatibility MUST NOT transfer authority. Being `agp-26` compatible does not by itself grant runtime admission, scientific validity, verification authority, or production maturity.

---

## 6. Lifecycle vocabulary

Aftergraph adopts one shared lifecycle vocabulary across public and developer surfaces:

| State | Meaning |
|---|---|
| **Stable** | Supported production interface with stated compatibility guarantees |
| **Preview** | Intended for evaluation or limited production use; may evolve under published rules |
| **Experimental** | No compatibility guarantee; behavior or interfaces may change materially |
| **Research** | Scientific/research artifact; no implied production authority |
| **Legacy** | Maintained primarily for migration or compatibility |
| **Deprecated** | Replacement exists or retirement is planned |
| **Retired** | No longer supported |
| **Ephemeral** | Temporary proof/test infrastructure outside canonical platform topology |

Lifecycle is independent of platform generation.

Examples:

```text
Sentinel                     Stable or Preview according to product evidence
AIE                          Research/Preview according to normative maturity
ACC                          Research while still a research prototype
AVC                          Legacy / migration source
sentinel-firetest            Ephemeral
```

No repository may be upgraded from Research/Experimental/Preview to Stable merely because it is included in Aftergraph 26.

---

## 7. Repository topology versus product topology

The repository graph remains canonical for ownership and implementation. The product graph is canonical for public navigation.

### 7.1 Products

```text
Studio
└── studio

Sentinel
└── sentinel

Work Intelligence
├── wi-frontend
└── wi-backend

Continuum
├── continuum
└── context-continuity   # continuity/state-transfer dependency, not a duplicate product
```

`context-continuity` remains the owner of actionable context/state transfer. `continuum` remains the assurance/fault-injection system for continuity and containment. Public grouping MUST NOT collapse those ownership boundaries.

### 7.2 Core platform

```text
Authority
└── aie

Trust
└── trust-gateway

Execution
└── works-execution

Runtime
└── Aftergraph Runtime   # planned target state; no canonical runtime repo yet
```

Runtime remains a planned target-state plane until a canonical implementation repository is established. Public presentation MUST NOT imply that a currently nonexistent canonical runtime repository is already shipped.

### 7.3 Intelligence and capabilities

```text
skills-vault
model-registry
afm
llm-research-development
```

These remain independent technical/research programs. They may declare `agp-26` compatibility or baseline membership without being renamed to `Skills 26`, `AFM 26`, or equivalent.

### 7.4 Research and assurance

```text
intelligence-systems-research
```

Scientific claims remain governed by their own evidence, protocol, benchmark, and reproducibility versions. Inclusion in the Aftergraph 26 research baseline does not upgrade scientific claims.

### 7.5 Foundation and public projection

```text
after-graph-governance
docs
brand
.github
aftergraph.org
```

These repositories govern, render, or project platform truth. They do not become public products merely because they are canonical repositories.

### 7.6 Migration and ephemeral infrastructure

```text
autonomous-venture-company   Legacy / migration source
sentinel-firetest            Ephemeral
```

AVC remains subject to the canonical dissolution policy and must not receive new canonical platform responsibility during migration.

`sentinel-firetest` is explicitly outside the canonical 20-repository platform topology. Its existence can be recorded as installed/ephemeral without advertising it as an Aftergraph 26 product or canonical component. Destructive archive/delete actions require separate owner approval.

---

## 8. Product naming standard

The masterbrand hierarchy is:

```text
AFTERGRAPH
    ↓
AFTERGRAPH 26
    ↓
CONVERGENCE
    ↓
PRODUCT / PLATFORM CAPABILITY / RESEARCH PROGRAM
```

### Public product naming

Preferred:

```text
Studio by Aftergraph
Sentinel by Aftergraph
Work Intelligence by Aftergraph
Continuum by Aftergraph
```

Preferred compatibility line:

```text
Built for Aftergraph 26
```

or, when evidence supports a stronger technical claim:

```text
Compatible with Aftergraph 26
```

`Built for` is brand copy. `Compatible with` is a conformance claim and therefore requires machine-readable compatibility evidence.

### Infrastructure naming

Infrastructure may use names without the `by Aftergraph` suffix where the relationship is already explicit:

```text
Aftergraph Runtime
Trust Gateway
WORKS
Aftergraph Governance
Aftergraph Skills
Aftergraph Models
```

### Master positioning

The public master positioning remains:

> **Infrastructure for verified intelligent systems.**

`Convergence` is the generation narrative, not a replacement corporate tagline.

---

## 9. Machine-readable component manifest

A common manifest SHOULD be introduced as the machine-readable source for release identity, lifecycle, compatibility, contracts, and provenance.

Conceptual schema:

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
  compatibility: agp-26

contracts:
  principal: "1.0"
  correlation: "1.0"
  verdict: "1.0"
  evidence: "1.1"

provenance:
  repository: Aftergraph/sentinel
  commit: <exact-sha>
```

The schema MUST allow fields to be absent when they do not apply. For example, a model artifact may use a model identity and provenance without pretending to expose a product release; a public-site repository may project platform metadata without pretending to implement runtime contracts.

The manifest MUST NOT become a second source of canonical repository topology. Governance topology owns repository identity and ownership; the component manifest owns the release/compatibility declaration of a particular component.

---

## 10. Compatibility claim states

Aftergraph distinguishes platform membership from verified compatibility.

Recommended claim states:

```text
Native
Compatible
Transitional
Research-compatible
Not declared
```

Definitions:

- **Native** — designed as part of the current platform generation and passes the applicable generation baseline.
- **Compatible** — independently versioned component that passes the applicable generation baseline.
- **Transitional** — migration source or compatibility bridge; not a target-state owner.
- **Research-compatible** — participates in the generation's research baseline without implying production maturity.
- **Not declared** — no compatibility claim has been made or verified.

A component MUST NOT claim Native solely because it lives in the Aftergraph organization.

---

## 11. Contract versioning

Machine contracts remain separately versioned.

Examples:

```text
principal/1.0
correlation/1.0
mission/1.x
evidence/1.x
verdict/1.0
```

Platform generation changes do not automatically require contract major-version changes.

Likewise, a contract may evolve within the compatibility policy of a platform generation without forcing the public platform generation to change.

The relationship is:

```text
Aftergraph generation
    constrains an allowed compatibility set of contracts

Contract version
    defines a machine interface and compatibility promise
```

This prevents a calendar/release brand decision from becoming a protocol-breaking event.

---

## 12. Model versioning

Model identity remains independent.

Correct:

```text
AFM-0.9
AFM-0.12
Platform target: agp-26
```

Rejected:

```text
AFM 26
```

unless a future model product explicitly adopts that product naming for reasons independent of platform generation.

A model may support multiple platform generations:

```yaml
model: AFM-1.0
compatible_with:
  - agp-26
  - agp-27
```

Model registry state, frozen references, promotion candidates, and benchmark evidence remain separate from platform branding.

---

## 13. Exact evidence and provenance

Aftergraph keeps exact-head evidence as a differentiating technical layer.

A compatibility or release record SHOULD be able to resolve from human-readable generation to exact implementation evidence:

```text
Aftergraph 26
→ Sentinel 1.0
→ sentinel-engine 1.4.0
→ evidence/1.1
→ commit <sha>
→ artifact digest <sha256>
→ verification/evidence record
```

No public generation number may replace exact-subject binding where exact-subject evidence is required.

A moved HEAD can invalidate an exact verification result without invalidating the semantic existence of the Aftergraph 26 generation itself. This distinction is intentional.

---

## 14. Public website architecture

The main public navigation SHOULD converge on:

```text
Aftergraph
Products
Platform
Developers
Research
Company
```

### Hero

```text
AFTERGRAPH 26
CONVERGENCE

Infrastructure for verified intelligent systems.

Build, operate and verify intelligent systems
across one governed execution platform.
```

### Product section

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

### Platform section

```text
Authority
Who may do what?

Trust
Should this action be admitted?

Runtime
Where does intelligent execution happen?

Execution
What durable work must occur?

Evidence
What actually happened?

Verification
Can the claimed outcome be independently proven?
```

The public site MUST NOT present the 20 canonical repositories as 20 peer products.

---

## 15. Developer documentation architecture

The developer portal SHOULD present one generation-aware entry point:

```text
Documentation for Aftergraph 26
```

Recommended information architecture:

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

APIs
Contracts
SDKs
CLI
Compatibility
Lifecycle
Changelog
```

When multiple generations exist, the portal may expose a generation selector such as:

```text
Aftergraph 27 Preview
Aftergraph 26 Current
Aftergraph 25 Legacy
```

Only generations that actually exist may be shown. Future examples are not current product claims.

---

## 16. GitHub organization presentation

The `.github` organization profile SHOULD group repositories by platform meaning rather than present every repository as a peer product.

Recommended public grouping:

```text
Products
Studio · Sentinel · Work Intelligence · Continuum

Core Platform
AIE · Trust Gateway · WORKS · Runtime (planned)

Models & Capabilities
AFM · Model Registry · Skills

Research
Intelligence Systems Research

Foundation
Governance · Docs · Brand
```

The profile may show:

```text
Current platform generation: Aftergraph 26
```

but repository-local technical versions remain visible where relevant.

---

## 17. Release train

Aftergraph may publish platform-level coordinated release notes without forcing lockstep repository releases.

Example:

```text
Aftergraph 26.1

Products
- Sentinel improvements
- Studio improvements
- Work Intelligence improvements

Platform
- evidence/correlation compatibility updates
- Trust/Execution integration improvements

Models
- new supported model candidates

Security
- enforcement and conformance changes
```

`26.1` is a **platform update release**, not a replacement for component semver.

A platform update may include no code change in some repositories. Those repositories MUST NOT receive meaningless releases solely to match the platform update number.

---

## 18. Changelog layers

Aftergraph maintains three different changelog/evidence levels.

### Public platform changelog

```text
Aftergraph 26.1
Products · Platform · Developers · Models · Research · Security
```

### Technical component changelog

```text
sentinel-engine 1.4.1
works 0.3.x
trust-gateway x.y.z
evidence/1.1
```

### Exact evidence

```text
commit SHA
artifact digest
CI/conformance evidence
verification receipt
```

The public changelog MUST NOT be treated as exact build evidence.

---

## 19. Source-of-truth hierarchy

The standard does not create a new uncontrolled truth surface.

Canonical hierarchy:

```text
Governance topology / ownership
        ↓
Normative contract registry
        ↓
Component release + compatibility manifests
        ↓
Generated exact-head org state / evidence
        ↓
Docs / aftergraph.org / .github public projection
```

Rules:

1. `after-graph-governance` owns platform-generation definitions, topology classification, lifecycle vocabulary, and compatibility policy.
2. Product/component repositories own their concrete release identity and implementation evidence.
3. Contract owners own contract versions.
4. Model Registry owns promoted immutable model metadata.
5. ISR owns scientific claims and research evidence.
6. `docs`, `.github`, and `aftergraph.org` project canonical truth; they do not silently redefine it.
7. Volatile counts and compatibility tables SHOULD be generated from canonical sources rather than manually duplicated.
8. Exact org-state SHAs remain generated and MUST NOT be hand-edited into canonical truth.

---

## 20. Relationship to Platform Architecture V3

This design complements, rather than replaces, the plane-level platform architecture.

It also identifies several presentation/ownership corrections that must be reconciled during implementation:

- `context-continuity` owns actionable state transfer; Continuum owns continuity/containment assurance. Public product grouping must preserve this distinction.
- Sentinel is a software-domain verifier. The Verification plane is a platform interface/capability and MUST NOT automatically imply that Sentinel verifies every possible Aftergraph outcome.
- Aftergraph Runtime remains planned target-state infrastructure until a canonical implementation exists.
- AVC is a migration source, not a current peer product or canonical platform kernel.
- Canonical GitHub repository identities are `wi-backend` and `wi-frontend`; historical `work-intelligence-*` names may remain only as compatibility aliases/provenance where needed.

These corrections must be made in a dedicated reconciliation implementation plan rather than smuggled into branding-only edits.

---

## 21. Relationship to the 21 installed repositories

For platform truth, the current distinction is:

```text
21 installed repositories
= 20 canonical platform repositories
+ 1 ephemeral firetest repository
```

The public release system therefore MUST NOT use the raw installation count as a product count.

A future topology schema should explicitly distinguish at least:

```text
repo_slug
aliases
product_name
plane
role
visibility
lifecycle
```

Recommended topology lifecycle values include:

```text
canonical
migration
ephemeral
planned
```

This makes installed, canonical, legacy/migration, ephemeral, and planned target-state systems distinguishable without falsifying repository reality.

---

## 22. Non-goals

ARLCS/1.0 does **not**:

- merge the 20 canonical repositories into a monorepo;
- force all repositories onto `26.x` versions;
- rename AFM model versions to calendar versions;
- upgrade research artifacts to production maturity;
- make Sentinel the universal verifier for every domain;
- establish a runtime implementation that does not yet exist;
- archive or delete AVC;
- archive or delete `sentinel-firetest`;
- redefine exact-head evidence as a platform-generation claim;
- transfer contract ownership into Governance;
- replace semver or domain-specific version schemes where they are appropriate.

---

## 23. Initial implementation scope

The first implementation program should be truth-first and low-blast-radius.

### Phase A — canonical standard

- add the normative ARLCS document and machine schema;
- define `agp-26` and `Convergence` as the current platform generation;
- define lifecycle and compatibility vocabularies;
- define the difference between product, component, contract, model, and evidence versions.

### Phase B — topology normalization

- reconcile 21 installed vs 20 canonical vs one ephemeral;
- introduce repo slug, aliases, product grouping, lifecycle, and plane metadata;
- adopt `wi-backend` / `wi-frontend` as canonical slugs;
- classify AVC as migration/legacy and `sentinel-firetest` as ephemeral;
- keep Runtime explicitly planned until implemented.

### Phase C — repository manifests

- define and validate `aftergraph.component/1`;
- add manifests incrementally to canonical repositories;
- derive compatibility tables from manifests rather than README prose.

### Phase D — public projection

- update `.github`, `aftergraph.org`, and Docs to render the smaller product mental model;
- expose Aftergraph 26 and lifecycle labels;
- generate volatile product/topology/compatibility lists from canonical data.

### Phase E — release train

- add platform-level release notes/changelog conventions;
- preserve independent component semver/model/contract versioning;
- establish exact evidence links from platform release records to concrete source/build artifacts.

---

## 24. Acceptance criteria

The design is successfully implemented when all of the following are true:

1. `Aftergraph 26 · Convergence` has one canonical governance definition.
2. `agp-26` has a machine-readable compatibility definition.
3. Public product navigation contains a small product family rather than one tile per repository.
4. The organization can distinguish 21 installed repositories from 20 canonical platform repositories and one ephemeral repository without contradictory counts.
5. Product, component, contract, model, and exact-evidence versions are explicitly distinct in governance and developer documentation.
6. No bulk conversion of repository versions to `26.x` is performed.
7. Lifecycle states use one shared vocabulary.
8. `wi-backend` and `wi-frontend` are canonical repository identities; old names are aliases/provenance only where required.
9. ACC/context continuity and Continuum boundaries are preserved and presented accurately.
10. Sentinel is represented as software-domain verification, while the platform Verification capability remains extensible to domain verifiers.
11. Runtime is shown as planned until a canonical implementation exists.
12. AVC is represented as migration/legacy, not a second platform kernel.
13. `sentinel-firetest` is represented as ephemeral and excluded from canonical product/platform counts.
14. Compatibility tables can be generated from machine-readable sources.
15. Public release notes can describe an Aftergraph 26.x platform update without requiring meaningless synchronized component releases.
16. Exact SHA/digest evidence remains available for claims that require exact-subject binding.
17. Docs and public projections do not become competing sources of canonical platform truth.

---

## 25. Naming freeze

The following names are approved for the first generation:

```text
Masterbrand:          Aftergraph
Platform generation: Aftergraph 26
Compatibility ID:    agp-26
Codename:             Convergence
Standard:             Aftergraph Release, Lifecycle & Compatibility Standard
Standard ID:          ARLCS/1.0
```

Generation numbering is release-family based. The number is associated with the year in which the generation is introduced, but support and compatibility are not bounded to that calendar year. A successor number is activated only by a separately governed generation declaration.

Future generation names such as `Meridian`, `Lattice`, `Horizon`, or `Axiom` remain non-normative ideas until separately approved. No future generation is created by this design.

---

## 26. Final target state

The system should be understandable at progressively deeper levels:

```text
CUSTOMER
Aftergraph 26 · Convergence
    ↓
Studio · Sentinel · Work Intelligence · Continuum

PLATFORM ARCHITECT
Authority · Trust · Runtime · Execution · Evidence · Verification
    ↓
AIE · Trust Gateway · Runtime · WORKS · verifiers

DEVELOPER
APIs · contracts · SDKs · component versions · lifecycle

AUDITOR / RESEARCHER
exact commit · artifact digest · evidence · benchmark · provenance
```

This is the intended unification model:

> **One public platform. Independent systems. Explicit compatibility. Exact evidence.**

The platform becomes easier to understand without pretending that unlike systems have identical versions, maturity, authority, or evidence.
