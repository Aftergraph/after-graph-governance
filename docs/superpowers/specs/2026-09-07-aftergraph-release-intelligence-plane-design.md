# Aftergraph Release Intelligence Plane — Design

**Date:** 2026-09-07  
**Status:** Approved design; pending written-spec review  
**Scope owner:** `Aftergraph/after-graph-governance`  
**Depends on:** Aftergraph Release Standard (`ARS/1`) and Aftergraph Platform Compatibility (`APC-1`)  
**Working name:** **Aftergraph Release Intelligence (`ARI`)**

---

## 1. Purpose

Aftergraph Release Intelligence turns release compatibility from documentation into an executable, evidence-backed system property.

Its job is to answer questions that ordinary semantic versioning, package manifests, and changelogs cannot answer reliably across a polyrepo intelligent-systems platform:

```text
What exists?
Which exact build is running?
Which contracts does it implement?
Which combinations have actually been tested?
Which combinations are merely declared?
What will break if this release lands?
Can this upgrade be rolled back safely?
Which compatibility edges are stale or unknown?
Which release may be promoted?
Which deployment has drifted from a verified configuration?
```

ARI is not a new source of platform authority. Governance defines the rules. Repositories produce declarations and evidence. ARI compiles, relates, tests, and projects that truth.

The target principle is:

> **Compatibility is not a label. It is a claim backed by executable evidence.**

---

## 2. Architectural position

ARI is a logical cross-cutting plane.

```text
                     AFTERGRAPH 26
                      CONVERGENCE
                           │
                           ▼
                  RELEASE INTELLIGENCE
                           │
       ┌───────────────────┼───────────────────┐
       │                   │                   │
    Registry        Compatibility Graph      Evidence
       │                   │                   │
       └────────────── APC Compiler ───────────┘
                           │
                    Semantic Diff
                           │
                  Release Simulation
                           │
                    Conformance Lab
                           │
                    Admission Gate
                           │
                   Release Passport
                           │
                        Deploy
                           │
                 Runtime Negotiation
                           │
                Compatibility Telemetry
                           │
                    Drift Detection
                           │
                 Verified Platform State
```

ARI does not replace GitHub, CI, artifact registries, Trust Gateway, WORKS, Sentinel, Continuum, model registry, or Governance. It composes their evidence and release semantics.

---

## 3. Boundary and authority rules

1. Governance owns ARS, APC levels/profiles, lifecycle policy, version-skew policy, generation declarations, and compatibility schema.
2. Source repositories own component manifests and source-specific release evidence.
3. CI/conformance tooling owns deterministic test results.
4. Sentinel may verify software-domain release subjects but is not automatically the universal ARI verifier.
5. Continuum may provide fault/continuity campaign evidence for applicable release scenarios but does not own general compatibility truth.
6. Trust Gateway remains runtime admission/enforcement. ARI release admission is a separate release-governance decision surface.
7. WORKS remains durable execution truth. ARI may consume release/work evidence but does not become the durable work system.
8. Model Registry remains the canonical registry for promoted model metadata. ARI references model records rather than replacing them.
9. AI/LLM analysis may forecast risk or explain differences, but deterministic policy/evidence decides conformance and release admission.
10. Public generation labels never substitute for exact build/evidence identity.

---

## 4. Core architecture

ARI is decomposed into independent capabilities so the system can be implemented incrementally rather than as one heroic new platform blob.

### 4.1 Release Registry

The Release Registry indexes machine-readable release declarations for products, components, contracts, models, and deployment configurations.

It stores or references:

```text
identity
version
lifecycle
generation association
release train
APC level/profile
contract requirements
provenance
artifact identity
conformance evidence references
deprecation/sunset metadata
```

It does not own repository topology. Governance topology remains canonical for repository identity and ownership.

The Registry SHOULD be content-addressable or reference immutable source/artifact identities where practical.

### 4.2 Compatibility Graph

The Compatibility Graph represents compatibility as relationships, not as a flat boolean.

All version numbers in examples in this document are illustrative unless explicitly bound to a cited exact source artifact.

Example conceptual edges:

```text
Sentinel 1.5.0
 ├── conforms-to APC-1/verifier
 ├── requires evidence >=1.1 <2.0
 ├── requires correlation >=1.0
 ├── tested-with WORKS 0.5.1
 ├── tested-with Trust Gateway 1.6.0
 └── incompatible-with evidence <1.1
```

Edges carry provenance and compatibility-evidence level.

The graph MUST distinguish:

```text
declared
schema-compatible
contract-tested
integration-verified
fault-tested
production-observed
incompatible
unknown
```

Unknown is a first-class state. Absence of failure is not compatibility evidence.

### 4.3 APC Compiler

The APC Compiler consumes component manifests, contract schemas, compatibility rules, conformance tests, and evidence references and emits a deterministic compatibility result.

Conceptual command:

```bash
aftergraph compatibility check
```

Example output:

```text
APC-1/verifier: PASS

Contracts:
  verdict/1.0      PASS
  evidence/1.1     PASS
  correlation/1.0  PASS

Version-skew edges:
  WORKS 0.5.1      VERIFIED CE4
  TG 1.6.0         VERIFIED CE3

Unknown edges:
  Runtime 1.2.0    UNVERIFIED
```

The compiler MUST distinguish failure, unknown, not-applicable, and pass.

### 4.4 Semantic Contract Diff

ARI requires a domain-aware diff layer for changes whose semantic effect cannot be captured by line-level Git diff alone.

Examples of semantic break categories:

```text
schema break
authority break
tenancy break
identity break
evidence-binding break
verification-validity break
failure-mode break
lifecycle-policy break
```

Examples:

```yaml
before:
  required: false

after:
  required: true
```

may classify as a machine-contract breaking change.

A change from exact evidence subject binding to moving/latest subject semantics is classified as a verification-semantic break even if the JSON schema remains valid.

The deterministic semantic diff engine owns final classification where rules exist. AI may explain or flag possible semantic risk but cannot declare compatibility by itself.

### 4.5 Conformance Lab

The Conformance Lab executes APC profile tests and applicable cross-component tests.

Test classes may include:

```text
schema conformance
contract fixtures
identity/correlation propagation
authority/revocation behavior
budget denial behavior
evidence subject binding
stale-verdict invalidation
version-skew combinations
fault/continuity campaigns
upgrade/rollback scenarios
```

Conformance outputs immutable or content-addressed receipts suitable for Release Passports.

### 4.6 Release Simulator

The Release Simulator compares current and proposed platform states before promotion.

Example:

```text
CURRENT
TG 1.6.0
WORKS 0.5.1
Sentinel 1.5.0
APC-1

PROPOSED
TG 1.7.0
WORKS 0.6.0
Sentinel 1.6.0
APC-1
```

It computes:

```text
changed nodes
changed contracts
new/removed compatibility edges
required migrations
version-skew violations
missing evidence
rollback risk
fault-campaign requirements
```

The simulator may then execute or schedule deterministic conformance suites against the proposed state.

### 4.7 Release Admission Gate

The Admission Gate evaluates release policy against evidence.

Conceptual decision:

```text
APC conformance       PASS
Security              PASS
Required CI           PASS
Compatibility graph   PASS
Rollback              PASS
Evidence completeness PASS

RELEASE DECISION: ADMIT
```

or:

```text
RELEASE DECISION: DO NOT ADMIT

Reason:
TG 1.7 emits principal/1.1 while Runtime target is only verified against principal/1.0.
```

The gate is policy-driven and deterministic. It does not rely on free-form AI approval.

### 4.8 Release Passport

Every promoted release SHOULD be able to publish an immutable Release Passport.

Conceptual example:

```yaml
release:
  product: sentinel
  version: 1.5.0

platform:
  generation: 26
  release_train: "2026.09"

compatibility:
  level: APC-1
  profiles:
    - verifier

contracts:
  evidence: "1.1"
  verdict: "1.0"

provenance:
  repository: Aftergraph/sentinel
  commit: <sha>
  artifact_digest: sha256:<digest>

conformance:
  result: pass
  evidence_level: CE4
  receipt: <reference>
```

The Passport is the portable machine-readable claim. It is not a marketing badge.

### 4.9 Release Bill of Materials (`RBOM`)

ARI SHOULD define a Release Bill of Materials complementary to SBOM.

An RBOM describes the exact platform release composition:

```text
products
components
contracts
models
skills/packs where relevant
policies
schemas
release passports
artifact identities
compatibility baseline
```

Example:

```text
Aftergraph 26 / 2026.09 / APC-1
Studio            2.1.0
WI backend         1.3.0
Trust Gateway      1.6.0
WORKS              0.5.1
Sentinel           1.5.0
AFM                 0.12
Evidence contract   1.1
Correlation          1.0
```

The RBOM supports audit, rollback, drift detection, and reproducible deployment descriptions.

---

## 5. Compatibility evidence levels

ARI uses discrete compatibility-evidence levels with the `CE` prefix to avoid collision with research evidence classes, claim identifiers, or other project taxonomies.

```text
CE0  Declared
CE1  Schema compatible
CE2  Contract tested
CE3  Integration verified
CE4  Failure/upgrade tested
CE5  Production evidenced
```

Definitions:

- **CE0 Declared** — metadata claim exists; no independent compatibility proof.
- **CE1 Schema compatible** — deterministic structural/schema checks pass.
- **CE2 Contract tested** — normative contract fixtures/conformance tests pass.
- **CE3 Integration verified** — relevant components have been exercised together against the declared seam.
- **CE4 Failure/upgrade tested** — relevant failure, version-skew, upgrade, or rollback scenarios have passed.
- **CE5 Production evidenced** — production-observed evidence confirms the declared combination under defined conditions.

A higher level does not erase scope. `CE5` on one edge does not imply CE5 compatibility for the entire deployment.

---

## 6. Verified upgrade paths

ARI represents upgrade compatibility as a first-class artifact.

Example:

```text
VERIFIED UPGRADE PATH

FROM
TG 1.6.0
WORKS 0.5.1
Sentinel 1.5.0
APC-1

TO
TG 1.7.0
WORKS 0.6.0
Sentinel 1.6.0
APC-1

Migration        PASS
Dual-read/write  PASS
Rollback         PASS
Fault campaign   PASS
Evidence level   CE4
```

Upgrade-path evidence is bound to exact source/artifact identities.

A path MAY be declared one-way when rollback is impossible, but the reason and recovery strategy MUST be explicit.

---

## 7. Capability negotiation and runtime handshake

Build-time compatibility is necessary but not sufficient for distributed systems.

A future ARI runtime integration MAY support a capability handshake.

Illustrative declaration:

```text
Runtime supports:
  APC-1/runtime
  principal/1.0
  evidence/1.1
  correlation/1.0

WORKS requires:
  APC-1/execution
  evidence >=1.1
  correlation >=1.0
```

Negotiation result:

```text
NEGOTIATED
```

or:

```text
REFUSED
reason: evidence contract incompatible
```

Runtime negotiation MUST NOT invent adapters or reinterpret authority/evidence semantics automatically.

A compatibility adapter may participate only when it is explicitly registered, versioned, provenance-bound, and conformance-tested.

---

## 8. Compatibility adapters

ARI MAY support registered compatibility adapters for explicitly transformable seams.

Example:

```text
evidence-adapter
1.0 → 1.1
APC-1
CE4 verified
```

Adapters are prohibited from silently weakening:

```text
authority
revocation
tenant isolation
evidence subject binding
verification independence
```

when the transformation would alter normative meaning rather than representation.

A representation bridge is not permission to reinterpret a security or assurance contract.

---

## 9. Release digital twin

ARI MAY maintain a logical digital twin of a deployment or release candidate.

The twin links:

```text
products
services
contracts
models
skills
policies
deployments
release passports
compatibility edges
evidence
```

A proposed change can be applied to the twin before deployment to compute blast radius.

Example query:

```text
Upgrade evidence/1.1 → evidence/2.0
```

Expected result shape:

```text
Affected components: 7
Breaking edges: 3
Requires migration: Sentinel, WORKS, Runtime
Unaffected: Studio, AFM, Skills
Unknown: one third-party adapter
```

The digital twin is a derived model. It does not replace source-of-truth systems.

---

## 10. Golden configurations

ARI MAY publish exact Golden Configurations representing fully verified platform combinations.

Example:

```text
Aftergraph 26
Release train 2026.09
APC-1
Golden configuration G-2026.09-1
```

A Golden Configuration references exact component/model/contract identities and evidence receipts.

Potential user-facing release channels later include:

```text
Canary
Preview
Stable
Golden
```

`Golden` means a specific configuration has the strongest defined integration evidence. It does not mean every possible component combination is verified.

Long-Term Support is explicitly deferred until Aftergraph can sustain the operational support commitment.

---

## 11. Promotion and lifecycle automation

Lifecycle promotion can become partially computed rather than manually asserted.

Example policy:

```text
Experimental
   ↓ required deterministic checks
Preview
   ↓ soak/integration/compatibility evidence
Stable
```

A Stable promotion may require:

```text
APC profile conformance
no known incompatible required edges
security gates
required CI
rollback or recovery evidence
evidence completeness
published support/deprecation terms
```

Governance owns the policy. Automation evaluates it. Humans retain explicit decision points where policy requires owner judgment.

---

## 12. Machine-readable deprecation

Deprecation metadata is part of release intelligence.

Example:

```yaml
lifecycle:
  status: deprecated
  deprecated_at: 2026-09-01
  sunset_at: 2027-09-01

replacement:
  contract: evidence/2.0

migration:
  guide: <reference>
  verified_paths:
    - <upgrade-path-reference>
```

Tooling can then surface actionable warnings such as:

```text
2 required contracts sunset within 90 days.
1 verified migration path exists.
1 component has no verified migration path.
```

---

## 13. Compatibility telemetry and drift detection

Runtime/deployment telemetry SHOULD include enough release identity to detect unsupported combinations.

Illustrative OpenTelemetry-style attributes:

```text
aftergraph.platform.generation = 26
aftergraph.release.train = 2026.09
aftergraph.compatibility.level = APC-1
aftergraph.component.name = works
aftergraph.component.version = 0.5.1
aftergraph.contract.evidence = 1.1
```

ARI may compare declared/verified state against observed deployment state.

Example:

```text
DECLARED
Golden configuration G-2026.09-1

OBSERVED
Trust Gateway upgraded independently
WORKS unchanged

RESULT
PLATFORM DRIFT
1 compatibility edge now unverified
verification state: DEGRADED
```

The system MUST distinguish health from compatibility:

```text
Running     yes
Healthy     yes
Compatible  unknown
Verified    no
```

A healthy system is not automatically a verified system.

---

## 14. Verified Platform State

ARI defines a derived deployment-state vocabulary:

```text
Configured
Running
Healthy
Compatible
Verified
Degraded
Incompatible
Unknown
```

These states are intentionally non-equivalent.

`Verified` requires the applicable evidence policy to pass for the exact declared/observed configuration.

A deployment may remain operational while its compatibility evidence is stale or incomplete; ARI must represent that honestly rather than collapsing it into a binary up/down state.

---

## 15. Platform attestation

A verified deployment MAY emit a signed machine attestation describing the exact platform state.

Conceptual form:

```text
Aftergraph Platform Attestation
Generation: 26
Release train: 2026.09
APC: 1
Configuration: G-2026.09-1
Compatibility: VERIFIED
Evidence root: <digest>
Issued against: <exact deployment identity>
```

This is not automatically a regulatory certificate or PKI identity. It is an evidence-backed platform-state attestation.

Any external compliance claim requires its own explicitly governed standard and evidence.

---

## 16. Supply-chain and provenance technology

ARI should reuse mature open standards for generic supply-chain functions rather than invent Aftergraph-specific replacements.

Candidate foundations include:

```text
SBOM formats         SPDX / CycloneDX
provenance           SLSA-compatible provenance
attestations         in-toto-style statements
artifact signing     Sigstore-compatible mechanisms
artifact transport   OCI artifacts/registries
policy               OPA/Rego or equivalent deterministic policy engine
telemetry            OpenTelemetry
```

These are implementation candidates, not automatically normative choices in this design.

Aftergraph's in-house differentiation belongs in:

```text
APC semantics
role profiles
compatibility graph
semantic contract classification
cross-component evidence levels
release simulation
verified upgrade paths
release passports/RBOM
platform drift/verified-state semantics
```

The rule is:

> Reuse commodity cryptography, packaging, telemetry, and supply-chain formats; build Aftergraph-specific compatibility semantics in-house.

---

## 17. Contracts as executable artifacts

A future implementation MAY distribute contract packages as immutable signed artifacts containing:

```text
schema
normative examples
conformance tests
compatibility metadata
migration metadata
provenance/signature
```

OCI is a candidate transport because it can carry immutable versioned artifacts and attached attestations.

The canonical contract owner remains Governance. Artifact distribution does not change normative ownership.

---

## 18. Executable standards

APC profiles should be executable where deterministic conformance is possible.

Conceptual command:

```bash
aftergraph conform APC-1/verifier
```

An executable profile may include:

```text
schema
normative rules
fixtures
negative tests
failure tests
policy assertions
expected evidence outputs
```

A Markdown claim without executable evidence is insufficient for a technical `APC-1/<profile>: CONFORMANT` label.

---

## 19. Policy as code

Release admission SHOULD be expressible in deterministic policy.

Illustrative policy intent:

```text
Stable requires APC conformance.
Stable requires complete required provenance.
Stable cannot depend on a required incompatible edge.
Deprecated required contracts must have a migration or explicit waiver.
Unknown required compatibility edges block promotion unless policy explicitly permits a lower release ring.
```

OPA/Rego is one candidate technology; the design does not mandate a specific engine yet.

Policy decisions MUST retain the exact input/evidence references used to reach the decision.

---

## 20. Compatibility query interface

ARI SHOULD expose human and machine query surfaces.

CLI example:

```bash
aftergraph compat sentinel@1.5 works@0.5 trust-gateway@1.6
```

Possible output:

```text
COMPATIBLE
Platform: APC-1
Required edges: 4/4 verified
Minimum edge evidence: CE3
Known incompatible edges: 0
Unknown required edges: 0
```

A future query language/API may support questions such as:

```text
Which Stable components are not verified against the current evidence contract?
Which APC-1 deployments contain a Deprecated contract?
Which upgrade path gets this deployment to APC-2 with rollback support?
Which release candidates introduce an authority-semantic break?
```

---

## 21. AI-assisted release forecasting

AI may be used for advisory analysis of:

```text
open pull requests
contract diffs
historical incidents
release notes
dependency changes
model changes
unusual graph changes
```

Example advisory output:

```text
HIGH-RISK CHANGE
PR #381 may require APC-2 because it changes the mandatory principal semantics used by Trust, Runtime, and Execution.
```

This is a forecast, not a conformance decision.

AI MUST NOT:

```text
self-certify APC conformance
weaken deterministic policy
invent compatibility adapters
change authority semantics
convert unknown evidence into pass
```

---

## 22. In-house innovation candidates

The strongest Aftergraph-specific inventions to preserve as first-class concepts are:

### Compatibility Graph
A provenance-aware graph of exact compatibility relations rather than a flat version matrix.

### APC Compiler
Compilation of manifests, contracts, policies, and evidence into a deterministic conformance result.

### Semantic Contract Diff
Domain-aware breaking-change detection for authority, evidence, verification, identity, tenancy, and failure semantics.

### Release Passport
Portable exact-subject release identity plus compatibility and evidence.

### RBOM
A release-oriented bill of materials spanning components, contracts, models, policies, and evidence.

### Verified Upgrade Path
A signed/evidenced migration relation between exact platform configurations.

### Compatibility Evidence Levels
`CE0`-`CE5` evidence strength on specific graph edges.

### Verified Platform State
A separation between running, healthy, compatible, and verified deployment state.

### Release Digital Twin
A derived graph for blast-radius and migration simulation before promotion.

These concepts SHOULD remain protocol/tool-agnostic in Governance before implementation chooses storage, graph, signing, or policy engines.

---

## 23. Phased delivery

The target architecture is deliberately larger than the first implementation slice. Delivery is decomposed.

### Phase 0 — Standard and metadata foundation

Deliver:

```text
ARS/1
APC-1 common baseline
initial APC profiles
component manifest schema
lifecycle/deprecation schema
compatibility-edge schema
compatibility-evidence-level definitions
```

No runtime handshake or simulation required.

### Phase 1 — Graph, compiler, passport

Deliver:

```text
Release Registry
Compatibility Graph
APC Compiler
basic deterministic conformance
Release Passport
RBOM v0
query/CLI basics
```

This is the recommended first substantive ARI implementation milestone.

### Phase 2 — Semantic diff, simulation, admission

Deliver:

```text
Semantic Contract Diff
release candidate simulation
version-skew evaluation
verified upgrade-path artifacts
release admission policy
fault/rollback evidence integration
```

### Phase 3 — Runtime observation and drift

Deliver:

```text
capability handshake/negotiation
compatibility telemetry
deployment-state graph
drift detection
Verified Platform State
platform attestations
```

### Phase 4 — External productization

Only after internal proof:

```text
customer polyrepo ingestion
third-party compatibility graphs
external release passports
enterprise policy packs
hosted release intelligence surfaces
```

External productization is not required for internal ARI success.

---

## 24. Build-versus-reuse rule

ARI must not become an excuse to reimplement generic infrastructure.

Reuse external/open standards for:

```text
cryptographic signing
artifact storage
SBOM formats
provenance envelopes
telemetry transport
policy execution where suitable
```

Build in-house only where Aftergraph needs domain-specific semantics:

```text
APC model
cross-repo compatibility semantics
version-skew policy
semantic authority/evidence diffs
compatibility graph evidence model
release simulation semantics
verified platform-state logic
```

A new in-house primitive requires a documented reason that existing standards cannot express the needed semantics without loss.

---

## 25. Data and evidence model

Every material ARI output SHOULD be traceable to source evidence.

Minimum conceptual identifiers include:

```text
subject identity
source repository/commit
artifact digest
component/version
contract set
APC level/profile
compatibility edge(s)
conformance receipt(s)
policy decision
observed deployment identity where relevant
timestamp
issuer/tool version
```

Derived graph state must retain references to the evidence that produced it.

Regeneration from source evidence should be possible for canonical derived views.

---

## 26. Failure semantics

ARI fails conservatively.

Examples:

```text
missing required evidence        → UNKNOWN / BLOCK where policy requires proof
stale exact-subject evidence     → STALE / not verified
conflicting compatibility claims → CONFLICT / block promotion
registry unavailable             → no invented PASS
AI unavailable                   → deterministic system continues
telemetry incomplete             → observed state UNKNOWN, not compatible-by-default
signature invalid                → evidence rejected
```

`Unknown` and `Incompatible` remain distinct.

---

## 27. Security and trust

ARI release metadata may influence deployment/promotion decisions and is therefore security-sensitive.

The implementation must eventually cover:

```text
signed release declarations
immutable provenance references
policy tamper resistance
artifact digest verification
least-privilege registry writes
separation of producer and verifier where required
audit trail for waivers/overrides
replay/staleness protection where decisions bind to moving subjects
```

Waivers must be explicit, attributable, scoped, time-bounded where appropriate, and visible in the Release Passport/decision record.

---

## 28. Non-goals

ARI does not initially:

- replace GitHub or CI;
- replace package/model/artifact registries wholesale;
- become a second runtime orchestration system;
- make every repo use one semantic version;
- make every Aftergraph component Stable;
- infer production compatibility from research results;
- let AI issue authoritative compatibility verdicts;
- create automatic semantic adapters for authority/evidence contracts;
- promise LTS before operational support capacity exists;
- require Phase 3 runtime negotiation to deliver Phase 1 value;
- become an external commercial product before internal proof exists.

---

## 29. Acceptance criteria

The ARI architecture is successfully realized when:

1. Compatibility can be represented as evidence-backed graph edges rather than booleans.
2. APC profile conformance can be compiled deterministically from machine-readable declarations/tests/evidence.
3. Unknown, incompatible, stale, not-applicable, and pass are distinct states.
4. Release Passports bind compatibility claims to exact provenance.
5. An RBOM can describe an exact cross-platform release composition.
6. Compatibility evidence strength can be represented from CE0 through CE5 without implying more scope than was tested.
7. Semantic contract changes can classify authority/evidence/verification breaks beyond line-level diffs.
8. Mixed-version platform configurations can be evaluated against version-skew rules.
9. Upgrade paths can carry migration, rollback, and conformance evidence.
10. Release promotion can be evaluated by deterministic policy.
11. AI analysis remains advisory and cannot manufacture a PASS.
12. Runtime telemetry can eventually distinguish healthy from compatible and verified states.
13. Drift from a verified configuration can be detected without treating mere process health as compatibility proof.
14. Existing standards are reused for commodity signing, provenance, SBOM, artifact, and telemetry concerns where suitable.
15. Governance remains the source of compatibility semantics while repositories own their release declarations/evidence.
16. The implementation can begin with Phase 0/1 without requiring the full target-state architecture.

---

## 30. Recommended first implementation boundary

The first implementation plan SHOULD cover only Phase 0 and the smallest useful slice of Phase 1:

```text
1. machine schemas for component manifest, compatibility edge, and release passport
2. APC-1 common baseline plus a very small number of role profiles
3. deterministic APC Compiler skeleton
4. compatibility graph representation
5. Release Passport generation from exact source evidence
6. CLI/query that can distinguish PASS / FAIL / UNKNOWN / N/A
```

Do not begin with runtime negotiation, digital twins, production telemetry, external SaaS, or AI forecasting.

The first milestone must prove the central thesis:

> **Aftergraph can compute and evidence compatibility across independently versioned components without forcing lockstep releases.**
