# P-1 System Reality Baseline and Architecture vNext Design

**Status:** OWNER-APPROVED FOR R.O.R.O. P−1 BOOTSTRAP; ARCHITECTURE vNEXT REMAINS A HYPOTHESIS
**Date:** 2026-09-16  
**Owner:** Aftergraph portfolio control  
**Purpose:** Reconstruct the actual Aftergraph system from current repository reality before defining or implementing the next platform architecture, Brain, decision-intelligence kernel, learning loop, self-improvement, or daily verified mission path.

---

## 1. Why this exists

`PLATFORM-ARCHITECTURE-V4.md` remains historically valuable, but it can no longer be treated as sufficient evidence of current system reality.

Observed drift already exists:

- `docs/platform-topology/2.0.json` carries `evidence_cut = 2026-09-10`.
- Organization state continued changing after that cut, including later governance work such as Business Ops registration.
- Repositories now present in the organization are not all represented by the current topology source; at minimum `war-room` and `rendetalje` exist in the organization but are absent from `platform-topology/2.0`.
- Existing repositories have materially evolved since the V4 architecture document was written. Examples include Runtime package expansion, WORKS Company Brain, Sentinel context/blast-radius and exact-HEAD verification, Trust Gateway provider/policy/approval surfaces, Work Intelligence production integration, Relay operator-plane work, Business Ops domain ownership, and War Room system-intelligence work.

Therefore:

> **Architecture must be derived from observed and verified implementation reality, not from the most recent architecture prose.**

This is a P-1 activity: establish system reality first; freeze architecture second; build new intelligence third.

---

## 2. Non-negotiable invariants

The baseline and subsequent architecture MUST preserve these system laws unless the owner explicitly approves a replacement with evidence:

1. `Complete != Verified`.
2. Observation does not grant authority.
3. Prediction does not equal observation.
4. Memory does not grant authority.
5. Runtime may orchestrate but may not widen authority.
6. An executor may not independently verify itself.
7. Consequential ambiguity fails closed.
8. Exact-state verification is bound to the subject actually verified; moved subjects invalidate stale evidence.
9. Repository presence, tests, or documentation do not by themselves establish composition or production maturity.
10. New intelligence may propose, predict, simulate, route, learn, and suggest; it may not redefine canonical truth or bypass authority, enforcement, durable execution, or independent verification.

---

## 3. P-1 objective

Produce a machine-readable and human-reviewable baseline answering, for every active Aftergraph repository and consequential cross-repository seam:

- What exists?
- What actually runs?
- What does the code currently own?
- What does it consume?
- What does it produce?
- Which contracts are real and active?
- Which external services/protocols are live?
- Which state is durable?
- Which state is projection-only?
- Which actions are consequential?
- Where is authority defined and where is it enforced?
- Where is evidence created?
- Who may verify what?
- Which paths are tested only locally?
- Which paths have cross-repo composition evidence?
- Which paths have adversarial evidence?
- Which paths have live evidence?
- Which claims are stale, inferred, proposed, or unknown?

No architecture-vNext claim may be promoted to canonical solely because an older architecture document says so.

---

## 4. Required reality model

The P-1 baseline SHALL model the system as typed objects and relations rather than a flat repo list.

### 4.1 Repository object

Each repository record MUST contain at least:

```text
RepositoryReality {
  repository
  exact_head
  default_branch
  visibility
  lifecycle
  observed_role
  declared_role
  canonical_owner_claims[]
  active_packages[]
  services[]
  entrypoints[]
  durable_stores[]
  external_protocols[]
  authoritative_contracts[]
  consumed_contracts[]
  produced_events[]
  consumed_events[]
  evidence_outputs[]
  verification_surfaces[]
  deployment_surfaces[]
  known_consumers[]
  known_dependencies[]
  open_migrations[]
  active_prs[]
  test_commands[]
  evidence_level
  epistemic_status
  inspected_at
}
```

### 4.2 Epistemic status

Every material baseline claim MUST use one of:

```text
VERIFIED
OBSERVED
INFERRED
DECLARED
PROPOSED
STALE
CONFLICTING
UNKNOWN
```

`DECLARED` is intentionally weaker than `OBSERVED` or `VERIFIED`.

### 4.3 System relation

Cross-repo seams MUST be represented explicitly:

```text
SystemRelation {
  producer
  consumer
  relation_type
  contract
  version
  transport
  causal_identity_fields[]
  authority_boundary
  trust_boundary
  durable_boundary
  evidence_boundary
  verifier_boundary
  exact_heads[]
  conformance_level
  evidence_refs[]
}
```

Relation types include at minimum:

```text
OBSERVES
INFERS
AUTHORIZES
ADMITS
ORCHESTRATES
DISPATCHES
EXECUTES
PERSISTS
PRODUCES_EVIDENCE
VERIFIES
PUBLISHES
ROUTES
MOUNTS_CONTEXT
LEARNS_FROM
SUGGESTS
```

---

## 5. Evidence hierarchy for architecture claims

Architecture ownership SHALL be reconstructed from evidence in this order:

1. **Observed implementation** at exact HEAD.
2. **Executable contracts/tests** at exact HEAD.
3. **Cross-repository adapter/composition evidence**.
4. **Live runtime/deployment evidence**.
5. **Current machine-managed topology/registry**.
6. **Current README/docs declarations**.
7. **Historical architecture prose**.

When two sources disagree, the disagreement becomes a first-class `RealityDiff`; it is not silently resolved by preferring prose.

---

## 6. Scope of the first baseline wave

Wave P-1A covers the repositories that determine the end-to-end verified mission loop first:

```text
wi-backend
business-ops
aie
trust-gateway
runtime
works-execution
sentinel
studio
relay
war-room
context-continuity
continuum
skills-vault
skill-abi
skillport
model-registry
afm
llm-research-development
intelligence-systems-research
aftergraph-cron-fabric
after-graph-governance
```

Wave P-1B reconciles remaining product/public/domain/support repositories including `wi-frontend`, `rendetalje`, `aftergraph.org`, `docs`, `brand`, `.github`, temporary verification fixtures, legacy-transition repositories, and any repository discovered from GitHub that is absent from the registry.

The wave split is an inspection order only; no repository is excluded from final topology.

---

## 7. Required derived graphs

The baseline must generate or make possible these projections:

### 7.1 Ownership Graph

Who owns each semantic responsibility and which repository must not own it.

### 7.2 Contract Graph

Which repository produces and consumes each contract/version.

### 7.3 Execution Graph

How intent becomes durable work and side effects.

### 7.4 Authority Graph

How principal, delegation, approval, admission, revocation, and action scope propagate.

### 7.5 Evidence Graph

How observations and execution effects become evidence and verification verdicts.

### 7.6 Runtime Graph

Which hosts, workers, agents, providers, queues, processes, stores, and deployments exist.

### 7.7 Code/Module Graph

For consequential repositories, package/module/file/symbol/API/schema/test dependencies sufficient for semantic blast-radius and collision analysis.

### 7.8 Causal Identity Graph

The identity chain linking:

```text
Intent
→ Mission
→ Authority Grant
→ Admission
→ Attempt
→ Action
→ Effect
→ Evidence
→ Verification
→ Verified Outcome
```

Any consequential seam that cannot preserve or reconcile this identity is a baseline gap.

---

## 8. Architecture-vNext design direction

P-1 does not pre-approve a fixed number of planes. Instead, it will test whether the current seven-plane model still explains implementation reality without duplicated ownership or hidden systems.

The expected functional system, subject to falsification by the baseline, currently looks like:

```text
SOURCES / EXTERNAL SYSTEMS
        ↓
PERCEPTION / OBSERVATION
        ↓
WORK & SYSTEM INTELLIGENCE
        ↓
WORLD MODEL / OPERATIONAL TWIN
        ↓
COGNITIVE BRAIN
  ├─ attention
  ├─ memory/context
  ├─ hypothesis generation
  ├─ reasoning
  ├─ falsification
  ├─ evidence planning
  ├─ simulation
  ├─ planning
  ├─ model/skill/agent routing
  ├─ metacognition / abstention
  └─ recovery planning
        ↓
DECISION INTELLIGENCE KERNEL
  ├─ posterior risk
  ├─ uncertainty / OOD
  ├─ semantic blast radius
  ├─ evidence coverage/independence/freshness
  ├─ expected loss / tail risk
  ├─ next-best evidence / information gain
  └─ selective autonomy decision
        ↓
AUTHORITY / TRUST / POLICY / EGAC
        ↓
RUNTIME ORCHESTRATION
        ↓
DURABLE EXECUTION
        ↓
EFFECTS
        ↓
EVIDENCE
        ↓
INDEPENDENT VERIFICATION
        ↓
VERIFIED OUTCOME
        ↓
LEARNING STORE
  ├─ outcome learning
  ├─ calibration
  ├─ agent/model trust
  ├─ recovery learning
  └─ drift detection
        ↓
SUGGESTIONS / AUTOMATION DISCOVERY
        ↓
SELF-IMPROVEMENT CANDIDATES
        ↓
EXPERIMENT → SHADOW → VERIFY → PROMOTE
        ↺
WORLD MODEL / BRAIN
```

This diagram is a hypothesis until the baseline maps each responsibility to an actual canonical owner and executable interface.

---

## 9. Brain boundary

The future Brain MUST be a cognitive orchestrator, not a new source of truth or authority.

The Brain MAY:

- interpret goals;
- query world/system state;
- form hypotheses;
- rank attention;
- retrieve governed memory/context;
- propose plans;
- invoke simulation;
- request evidence;
- choose candidate models/agents/skills;
- produce action intents;
- propose recovery;
- create learning and improvement candidates.

The Brain MUST NOT:

- mint authority;
- bypass Trust admission;
- write durable execution truth directly;
- self-issue independent verification;
- promote its own memory to canonical truth;
- deploy self-improvements without external promotion gates.

Existing WORKS Company Brain or other durable institutional-memory surfaces MUST be inspected and reused where ownership already exists; a parallel durable-memory authority must not be created merely to support the cognitive Brain.

---

## 10. Self-improvement boundary

Self-improvement SHALL be candidate-based, not self-modifying production behavior.

```text
Observed weakness
→ Learning record
→ Improvement candidate
→ Experiment
→ Offline/replay evaluation
→ Shadow mode
→ Targeted tests
→ Regression tests
→ Safety/adversarial tests
→ Independent evidence
→ Promotion decision
→ Versioned rollout
```

No model, prompt, routing strategy, planner policy, memory policy, verifier configuration, or recovery strategy may promote itself directly from observed performance.

---

## 11. Learning and suggestions

The baseline must locate the canonical storage and event seams needed to create a verified `LearningRecord`:

```text
LearningRecord {
  mission_id
  subject_state
  context_features
  agent
  model
  skills
  plan
  actions
  predictions
  authority_decisions
  costs
  latency
  evidence
  verification
  final_outcome
  recovery_attempts
  human_interventions
}
```

A Suggestions engine SHALL operate only on observed patterns and produce proposals such as:

- repeated manual intervention;
- recurring missing evidence;
- repeated recovery success;
- repeated model/agent failure by task domain;
- recurring collision/conflict;
- stale contract or topology drift;
- automation candidates;
- benchmark/research candidates.

Suggestions are proposals, not authority.

---

## 12. Daily-system proof target

Architecture vNext is not considered operationally validated merely because repositories test green.

The first platform proof target SHALL be a real `Daily Verified Mission` path:

```text
real source observation
→ inferred work
→ mission
→ authority
→ admission
→ runtime orchestration
→ durable execution
→ measurable external or system effect
→ evidence
→ independent verification
→ verified/failed outcome
→ learning record
→ operator surface
```

Acceptance for the first vertical slice:

1. One causal identity survives every consequential seam.
2. Restart does not lose durable mission/execution state.
3. Authority can be revoked mid-flight and downstream action stops/fails closed.
4. At least one injected failure exercises recovery.
5. Executor cannot self-verify.
6. Stale subject/evidence invalidates the verdict.
7. War Room/Studio shows epistemic state rather than flattening observed/inferred/verified claims.
8. The final LearningRecord is generated only from the verified/failed outcome, not from agent self-report.
9. The entire mission can be replayed/audited from recorded identifiers and evidence.
10. Cost, latency, human intervention, VSR/FCR-relevant outcome data, and verification debt are measurable.

---

## 13. Baseline deliverables

P-1 is complete only when these artifacts exist:

```text
docs/system-reality/P-1-REALITY-BASELINE.md
docs/system-reality/repository-reality.json
docs/system-reality/system-relations.json
docs/system-reality/reality-diffs.json
docs/system-reality/daily-verified-mission-path.json
docs/system-reality/architecture-vnext-candidate.md
```

The machine-readable artifacts must be generated or validated by code. They must not be manually maintained duplicates of GitHub reality.

---

## 14. Immediate execution order after approval

1. Discover current GitHub organization membership and exact default-branch heads.
2. Diff organization membership against `platform-topology/2.0` and `latest-org-state.json`.
3. Inspect active entrypoints/packages/contracts in P-1A repositories.
4. Extract producer/consumer relations and ownership claims.
5. Reconcile actual durable-state, authority, trust, execution, evidence and verification boundaries.
6. Produce `RealityDiff` findings for stale or conflicting architecture claims.
7. Trace one candidate daily mission path end-to-end across real interfaces.
8. Define architecture-vNext from the resulting graph, not from V4 inheritance.
9. Only then write the implementation plans for Brain, Decision Intelligence Kernel, Learning/Suggestions/Self-Improvement, and War Room integration.

---

## 15. Explicit non-goals of P-1

P-1 does not:

- merge or retire repositories;
- redesign product branding;
- invent new protocols where existing contracts suffice;
- declare AGI;
- create a new top-level plane by default;
- promote testbed research claims to live production claims;
- modify production behavior while the system ownership model is unresolved.

---

## 16. Success criterion

P-1 succeeds when an independent engineer can inspect the generated baseline and answer:

> **What is Aftergraph today, which exact components own each consequential responsibility, how does one real mission traverse the system, what is actually verified, and where are the remaining unknowns?**

Only after that answer is evidence-backed should Architecture vNext and the Cognitive Control Loop become canonical implementation targets.

---

## 17. R.O.R.O. — Reality Observation, Reconciliation & Operations

P−1 SHALL use R.O.R.O. as the protocol family for system-reality observation and reconciliation. R.O.R.O. is not a new native authority or replacement database for the systems it observes.

The first invariant is:

```text
ComponentID != Repository != SourceBinding != Build != Deployment
```

Native truth remains native. GitHub owns Git state; deployment systems own deployed state; domain systems own their canonical domain state. R.O.R.O. records provenance-bound observations, relationships, contradictions and coverage over those sources.

R.O.R.O. SHALL distinguish reality facet from epistemic status. A claim can concern `RUNNING` reality while still being epistemically `OBSERVED`, `STALE`, `CONFLICTING` or `UNKNOWN`.

Initial facets are `DECLARED`, `CANONICAL`, `DESIRED`, `INSTALLED`, `CONFIGURED`, `RUNNING`, `REACHABLE`, `HEALTHY`, `VERIFIED`, `RECOVERABLE`.
The first R.O.R.O. implementation slice consists of:

- **Scout** — read-only collectors;
- **Index** — normalized component/source registry;
- **Anchor** — identity bindings across source/runtime/provider identities;
- **Diff** — explicit disagreement and drift;
- **Survey** — coverage and unknowns;
- later slices add Chronicle, Watchtower, Seal, Lens and Shadow.

`UNKNOWN` is a first-class result. Failure to observe is not equivalent to absence. A source that cannot be queried must be represented as unknown/unreachable rather than silently omitted.

The bootstrap artifacts are:

```text
docs/contracts/roro/0.1/*.schema.json
docs/system-reality/COMPONENT-MODEL.md
docs/system-reality/component-registry.json
docs/system-reality/component-lineage.json
docs/system-reality/reality-gaps.json
```

The source registry is generated from live organization discovery. `platform-topology/2.0` is compared as a declared/canonical ownership source; it is not allowed to limit discovery scope.
---

## 18. Circuit remains a composition hypothesis

Architecture vNext may compose semantic algorithm groups as an Aftergraph Circuit, but Circuit MUST NOT become an authority, execution-truth owner, verifier, or world-truth owner.

The current hypothesis groups responsibilities as:

```text
Sightline  — perception / system reality
Helm       — cognition / planning / decision intelligence
Covenant   — governance / authority / admission
Drive      — capability resolution / runtime / durable execution
Witness    — evidence / independent assurance
Refinery   — verified learning / experimentation / promotion
```

These names describe candidate semantic composition, not repository boundaries. Existing owners such as AIE, Trust Gateway, Runtime, WORKS, Work Intelligence, ACC and independent verifiers retain their explicit boundaries unless later evidence supports a governed migration.

Circuit compilation is therefore downstream of R.O.R.O. reality coverage. Repository consolidation is also downstream: no 2/3/4/5-workspace target is canonical until component/source/deployment/state/credential relationships can be simulated against observed reality.

---

## 18. R.O.R.O. RealityDiff and Survey implementation note

The bootstrap now includes a deterministic reconciliation layer over the promoted source/operational snapshots.

`reality-diffs.json` preserves unresolved contradictions and unknowns instead of selecting a winner. Current inputs include source gaps, operational gaps, deployment/source bindings, and recovery evidence.

`coverage-report.json` reports separate dimensions for source, deployment, routes, cloud ownership, credential mapping, recovery, runtime topology, and unresolved RealityDiffs. These dimensions MUST NOT be collapsed into one platform health score.

`coverage-gate.json` is now explicitly scoped to `SOURCE_TOPOLOGY_ONLY`. Its required dimensions are source semantics, exact deployment/source binding, credential-consumer/permission posture, and route disposition. A `READY` verdict therefore means only that source/topology consolidation simulations may proceed; it does **not** authorize runtime, state, credential, authority, or production-cutover migration.

At the 2026-09-16 source cut, the scoped gate is `READY` with zero blockers after 31/31 repository semantic coverage, 8/8 exact deployment bindings, remediation of active credential permission drift, and explicit route dispositions. Residual issues remain visible as `DRIFT` rather than being erased: historical Hermes credential snapshot sprawl, stale `wie.aftergraph.org` source references, transitional VDS topology, and outer-host concentration.

R.O.R.O. remains observational/reconciliatory: native systems remain native truth, and any future runtime/state/credential/authority migration still requires a separately scoped gate plus the ordinary AIE/Trust/WORKS/independent-verification path.

## 19. R.O.R.O. Shadow source-workspace simulation

The scoped `SOURCE_TOPOLOGY_CONSOLIDATION` READY gate permits source/topology simulation only. It does not authorize any repository move or runtime/state/credential/authority migration.

`consolidation-candidates.json` declares 2/3/4/5/7/8-workspace hypotheses generated from the current 31-repository topology. Each repository is assigned exactly once and public/private visibility mixing is prohibited.

`consolidation-simulation.json` evaluates candidates separately across dependency crossings, trust-boundary co-location, legacy/canonical mixing, research/production mixing, domain/platform mixing, deployment co-location and workspace concentration. No overall score, winner, or recommendation is emitted.

Observed tradeoff at the current source cut: separation reduces legacy, trust-boundary and deployment co-location, but dependency crossings are topology-sensitive rather than monotonic in workspace count. The strict 7-workspace hypothesis has 0 trust-boundary co-locations and 51 cross-workspace dependency edges, compared with 3 and 55 respectively in the 5-workspace hypothesis. The 8-workspace hypothesis additionally reduces modeled research/production co-location to 0 at 52 dependency crossings. This is evidence for design review, not a selected architecture.

`consolidation-boundary-analysis.json` adds a strict falsification hypothesis. If visibility purity, research isolation, AVC legacy isolation, and pairwise separation of authority/trust/execution/independent-verification are all required simultaneously, the derived source-workspace lower bound is at least seven. This lower bound is explicitly not a recommendation.
