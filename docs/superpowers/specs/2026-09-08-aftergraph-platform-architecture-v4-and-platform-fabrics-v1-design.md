# Aftergraph Platform Architecture V4 + Platform Fabrics V1 — Design

**Status:** Owner-approved architecture direction in chat on 2026-09-08; implementation remains gated on written-spec review.

**Date:** 2026-09-08

**Owner:** Aftergraph portfolio control

**Scope:** Canonical platform architecture, ownership, cross-cutting fabrics, migration boundaries, conformance and the first composed Golden Mission. This design supersedes the architectural direction of `PLATFORM-ARCHITECTURE-V3.md` once implemented, but this file itself is a design specification and does not change runtime ownership or production behavior.

**Brand rule:** `Aftergraph` is the platform/masterbrand target. `AVC`, `Autonomous Venture Company`, `avc-*` and `@avc/*` are legacy compatibility/provenance terminology only. `ABDE Intelligence` is not the target platform/product brand. Historical academic authorship and research-program attribution may remain where accurate. Trademark/legal clearance remains a separate concern.

---

## 1. Problem

Aftergraph has grown into a 24-repository polyrepo platform with independently evolving authority, enforcement, runtime, execution, experience, continuity, assurance, model, capability, operations and research systems.

The implementation has moved ahead of the current canonical architecture documents:

- the current machine-readable topology contains 24 repositories;
- `runtime` is now active rather than a future placeholder;
- `wi-backend` and `wi-frontend` replaced older Work Intelligence repository identities;
- `context-continuity` owns portable actionable state transfer;
- `continuum` is an assurance/fault-injection system rather than the owner of ordinary session continuity;
- Platform Fabrics v0.1 already defines correlation and semantic capability seams;
- AVC is a legacy migration source whose useful primitives are partly migrated and partly still awaiting canonical ownership.

The platform therefore needs one current architecture that:

1. preserves the seven permanent semantic planes;
2. distinguishes those planes from repository/system classification;
3. makes cross-repository capabilities composable without creating duplicate authority owners;
4. assigns canonical ownership for unresolved AVC-derived primitives;
5. keeps world/context/intelligence state distinct from authority;
6. gives Pocket, voice, ambient context and agentic behavior a platform-wide home without creating a personal-AI monolith;
7. makes platform maturity testable through exact-head composition, failure, revocation and verification evidence;
8. provides a machine-verifiable path to dissolve the legacy AVC repository.

---

## 2. Architectural thesis

Aftergraph is infrastructure for intelligent systems that can perceive, understand, remember, reason, delegate, act, recover, learn and interact continuously while consequential effects remain institutionally authorized, runtime-enforced, durably executed and independently verifiable.

The permanent consequential lifecycle is:

```text
Intent / Experience
  -> Intelligence
  -> Authority
  -> Trust
  -> Runtime
  -> Execution
  -> Evidence
  -> Verification
  -> Verified Outcome
```

No observation, memory, relationship, world-state assertion, model output, skill, persona, prior approval or inferred intent may create execution authority by bypassing this path.

The architecture is deliberately compositional:

- **planes** own normative semantic responsibility;
- **domain repositories** own their canonical state and behavior;
- **fabrics** connect concerns across planes without becoming new planes or new sources of authority;
- **projections** may be rebuilt from canonical sources and never silently replace them;
- **verification** remains independent of execution.

---

## 3. Non-goals

This design does **not**:

1. create a `friday`, `personal-ai`, `world-model`, `proactivity`, `agent-society`, `pocket-platform` or `mega-brain` top-level repository;
2. create an eighth permanent authority/execution plane;
3. move AIE authority into Runtime or Trust Gateway;
4. move Trust Gateway enforcement into AIE or Runtime;
5. move WORKS durable execution into Runtime;
6. make Studio a source of canonical platform truth;
7. make ACC a memory database or mission authority;
8. make WORKS Brain the user's personal/context memory store;
9. allow World State to become writable truth or an authority source;
10. use persona, model identity, skill installation or historic approval as a capability grant;
11. represent Pocket or any future wearable as a principal, authority source or execution runtime;
12. claim production, scientific or legal maturity merely because a UI/reference implementation exists.

---

## 4. Topology model: `platform-topology/2.0`

`platform-topology/1.0` currently overloads the term `plane` for both normative architectural planes and functional repository classes such as continuity, capabilities, models and operations.

V4 introduces a topology schema that separates those concepts.

Each repository record SHOULD carry:

```yaml
name: runtime
architecture_plane: runtime
system_class: agent-runtime
role: agent-runtime
lifecycle: active
owns: ...
must_not_own: ...
```

A support repository may have no permanent architecture plane:

```yaml
name: context-continuity
architecture_plane: null
system_class: continuity
role: continuity-contract
```

The seven valid non-null `architecture_plane` values are:

```text
intelligence
authority
trust
runtime
execution
verification
experience
```

`system_class` remains extensible for governance, continuity, assurance, research, capabilities, models, operations, knowledge, public, foundation, incubation and legacy-transition concerns.

The machine-readable topology becomes the source used to validate generated README topology, dependency/ownership projections, org-state and contract-owner references.

---

## 5. The seven permanent planes

### 5.1 Intelligence

**Primary canonical owner:** `Aftergraph/wi-backend`

Owns:

- source-neutral `Observation` ingestion;
- source lineage and deduplication;
- interpretation of observations into work-relevant candidates;
- `CommitmentCandidate` resolution;
- canonical `Commitment` lifecycle;
- `WorkCandidate`, resolution and `WorkItem` lifecycle;
- explicit review/approval boundaries before publication or WORKS promotion;
- provenance/evidence for its own inference decisions.

Must not own:

- AIE authority/delegation;
- Trust Gateway admission;
- agent lifecycle/orchestration;
- durable execution;
- independent verification.

Target logical progression:

```text
Signal
  -> Observation
  -> Interpretation
  -> CommitmentCandidate / WorkCandidate
  -> Commitment / WorkItem
```

An explicit user-created commitment enters the same canonical Intelligence path with stronger provenance than a model-extracted candidate. There must not be separate Studio-, Pocket- and Calendar-specific commitment truths.

### 5.2 Authority

**Canonical owner:** `Aftergraph/aie`

Owns:

- principal and authority semantics;
- delegation;
- mission authority envelopes;
- budgets as authority constraints;
- authority lifecycle;
- revocation semantics;
- human-governance authority meaning.

Human role labels such as `owner`, `reviewer`, `auditor` or `operator` MAY exist as convenience templates or experience projections, but the role label itself is not authority. AIE grants remain the authority truth.

Must not own:

- runtime enforcement;
- authenticated sessions/secrets;
- agent execution;
- durable WorkGraph state;
- independent verification.

### 5.3 Trust

**Canonical owner:** `Aftergraph/trust-gateway`

Owns:

- runtime identity/session binding;
- tenant and workspace-scope isolation;
- policy admission and enforcement;
- approvals and revocation enforcement;
- secret handling;
- provider/model eligibility and enforcement policy;
- runtime action audit;
- tenant lifecycle operational truth;
- consent ledger and consent enforcement;
- workspace-scope identity and immutable tenant binding.

Tenant lifecycle states include at least:

```text
ACTIVE
SUSPENDED
EXPORTING
DELETING
DELETED
```

Trust Gateway coordinates tenant lifecycle, but it does not own every tenant's domain data. On deletion/export, each canonical domain owner performs its own governed action and returns an acknowledgement before terminal lifecycle completion.

Consent is a separate axis from execution authority:

```text
Consent != Authority
```

Consent state changes must be eventful enough to invalidate downstream processing, not merely a local boolean.

Workspace identity/scope lives in the tenant/trust registry. Studio owns workspace experience state. Workspace tenant binding is immutable; cross-tenant movement is export/filter/new-identity/import with provenance, never an in-place `tenant_id` mutation.

Must not own:

- authority semantics;
- mission planning;
- durable work;
- organizational knowledge;
- independent verification.

### 5.4 Runtime

**Canonical owner:** `Aftergraph/runtime`

Owns:

- agent lifecycle;
- mission operation;
- orchestration and dispatch;
- agent organization/team topology;
- peer/relay runtime behavior;
- capability implementation strategy and resolution;
- model-edge integration and runtime route strategy;
- heartbeat, recovery and runtime opportunity detection;
- `AttentionDecision`;
- checkpoints;
- resource metering and observability;
- contextual/effective runtime memory;
- rebuildable World State projection.

Runtime may select an eligible implementation strategy, but a concrete action still requires applicable AIE authority and Trust Gateway admission. An implementation may not widen the semantic action's authority envelope.

Runtime Memory is operational/contextual and is never authority-eligible. It remains distinct from WORKS Brain and ACC.

World State may be cached/materialized in Runtime, but it is a rebuildable projection over provenance-bearing canonical sources. Runtime agents may propose assertion candidates; they do not receive a general-purpose API for writing effective world truth.

Must not own:

- AIE authority truth;
- Trust Gateway enforcement/tenant truth;
- WORKS durable execution;
- canonical organizational knowledge;
- independent verification.

Transitional Runtime packages inherited during AVC migration must be purified so they do not recreate AIE, Trust Gateway, WORKS or ACC inside Runtime.

### 5.5 Execution

**Canonical owner:** `Aftergraph/works-execution`

Owns:

- durable `Work` and WorkGraph state;
- scheduler/worker/lease semantics;
- retries and recovery;
- durable execution attempts;
- execution evidence;
- receipts/quittance/settlement state;
- governed Company Brain organizational knowledge.

WORKS Brain remains distinct from Runtime Memory:

```text
Runtime Memory
= operational contextual memory

WORKS Brain
= durable organizational knowledge
```

Authoritative Company Brain state remains subject to its human-stamped promotion law.

Must not own:

- agent persona;
- AIE authority semantics;
- Trust Gateway admission;
- independent verification.

### 5.6 Verification

**Primary owner for code workloads:** `Aftergraph/sentinel`

**Additional owners:** independent domain verifiers as registered by Governance.

Owns:

- exact-subject verification;
- stale-subject invalidation;
- evidence-backed verification verdicts;
- verification receipts.

Continuum remains an assurance/fault-injection system and may test continuity/containment failures, but it does not replace the independent verifier for ordinary execution outcomes.

Terminal state must distinguish:

```text
EXECUTION_COMPLETED
VERIFICATION_PENDING
VERIFIED
VERIFICATION_FAILED
STALE
```

The executing system cannot independently issue its own verified-completion verdict.

### 5.7 Experience

**Primary canonical owner:** `Aftergraph/studio`

Owns:

- general-purpose Chat / Work / Space experience;
- canonical interaction semantics;
- `AssistantProfile` presentation/persona;
- presence UX;
- multimodal composition;
- workspace experience state;
- attention-policy UX;
- conversation experience;
- Needs You;
- takeover/hand-back;
- evidence/trajectory/control visualization.

Studio may maintain experience state such as layout, spatial state, views and recents. It must not own tenant binding, authority, execution truth, verification truth or world truth.

A reference implementation in Studio does not by itself establish platform integration maturity.

---

## 6. Cross-cutting support systems

These systems remain first-class repositories without becoming new permanent planes:

- `after-graph-governance` — topology, contracts, invariants, cross-repo conformance and generated org-state;
- `context-continuity` — portable actionable state transfer and Context Handshake;
- `continuum` — continuity/containment adversarial assurance;
- `intelligence-systems-research` — scientific claims, preregistration, benchmarks and reproducibility;
- `skills-vault` — governed skill/capability supply chain;
- `llm-research-development` — reusable model research/evaluation methodology;
- `afm` — AFM-specific model program;
- `model-registry` — immutable promoted model lifecycle registry;
- `aftergraph-cron-fabric` — read-only scheduled organization sensing;
- `docs` — provenance-pinned knowledge and developer documentation;
- `aftergraph.org` — public front door and launcher;
- `brand` — Aftergraph Brand OS and design system;
- `.github` — organization community and shared repository defaults;
- temporary/incubation repositories only as explicitly registered lifecycle exceptions.

---

## 7. Platform Fabrics V1

A Fabric is a cross-cutting composition contract across existing domain owners. It does not become a new authority, execution, evidence or transport owner.

V1 defines eight fabrics.

### 7.1 Interaction Fabric

Composes primarily Studio, Runtime, ACC and Trust Gateway.

Canonical concepts include:

```text
InteractionSurface
InteractionThread
InteractionTurn
Presence
AssistantProfile
HandoffCheckpoint
```

Surfaces may include Studio, mobile, voice, Telegram, CLI, SIP and future devices. A surface is an adapter, not a separate identity/memory/authority universe.

Assistant persona is product/experience state, not authority. A user may name an AssistantProfile `Friday`, but no platform contract or package depends on that name.

### 7.2 Perception Fabric

Composes source adapters and Wie.

Sources include Pocket, voice transcripts, email, calendars, GitHub, browser/computer observations, devices/sensors and external APIs.

Canonical output is a provenance-bearing `Observation`.

Pocket is the first targeted physical-world reference adapter. It is never a principal, authority source, execution runtime or truth oracle.

### 7.3 Context Fabric

Composes Runtime Memory, ACC, WORKS Brain and source provenance while preserving their separate ownership.

The following distinctions are normative:

```text
Conversation != Memory
Memory != Continuity
Memory != Authority
Memory != WORKS Brain
WORKS Brain != World State
ACC != Memory
ACC != Authority
```

ACC owns transfer of actionable state and its handshake semantics only.

### 7.4 World State Fabric

Introduces generic projection primitives:

```text
Entity
Relationship
WorldAssertion
Situation
```

World State contracts are registered and conformance-tested by Governance. Runtime materializes the operational projection. Native truth stays with canonical source owners.

A `WorldAssertion` distinguishes epistemic state:

```text
OBSERVED
INFERRED
PREDICTED
UNKNOWN
```

and currentness state:

```text
CURRENT
STALE
DISPUTED
SUPERSEDED
```

It carries subject/predicate/value-or-ref, source references, evidence references, observation/validity/freshness timing, tenant/domain/classification scope, consent-record/version and processing-purpose lineage, and confidence where applicable. Consent/purpose lineage is what makes selective invalidation on consent revocation (§12) implementable without over-invalidating unrelated uses.

Rules:

- World State has no general-purpose write authority;
- agents may emit assertion candidates, not effective truth mutations;
- predicted/inferred state may guide planning but cannot silently satisfy a policy that requires current observed evidence;
- stale state is represented as stale/unknown, never refreshed by timestamp laundering;
- descriptive relations such as `trusts` or `delegates_to` do not become AIE grants;
- after Runtime failure, World State is rebuilt from canonical sources; unavailable sources yield stale/unknown state.

### 7.5 Proactivity Fabric

Composes three distinct sensing paths:

```text
Wie
= external signal -> possible work/commitment

Runtime
= mission/goal/runtime state -> opportunity/recovery

Cron Fabric
= scheduled read-only organization sensing -> finding
```

Native events remain native. They may project into a common correlation substrate for dedupe/correlation.

Candidate outcomes include `Opportunity`, `AttentionCandidate`, `CommitmentCandidate` or an ordinary observation update.

Cron Fabric retains zero execution authority.

### 7.6 Capability Fabric

Builds on existing `capability-action/0.1`.

A semantic capability action remains distinct from eligible implementations such as:

```text
native_tool
mcp
a2a
python
shell
browser
computer
database
workflow
```

Rules:

- semantic capability identity is distinct from implementation identity;
- implementation authority must fit inside the semantic action authority envelope;
- consequential and external effects require verification; a semantic contract may narrow how verification is evidenced but never waives it (frozen invariant `PLATFORM-FABRICS-v0.1` #2, enforced by conformance vector `CAP-003`);
- Runtime resolves implementation strategy;
- Trust Gateway admits/enforces the concrete operation;
- Skills Vault supplies governed capability implementations/procedures;
- fallback must never widen authority.

### 7.7 Agent Organization Fabric

Composes Runtime, AIE, Trust Gateway, WORKS and independent verification.

Runtime owns team topology, worker lifecycle, relay/peer operation, routing and recovery. AIE owns delegated authority. Trust Gateway owns admission. WORKS owns durable work/leases/effects. Verification remains independent.

Production defaults to manager-worker organization. Peer communication is bounded and protocol-governed. Recursive delegation cannot multiply authority or budget. Child envelopes are equal-or-narrower than the parent envelope, and the parent's remaining budget is atomically partitioned or reserved across all child envelopes so siblings cannot collectively spend more than the parent holds.

No worker may grant itself authority, administer peer authority or self-declare verified completion.

### 7.8 Verified Improvement Fabric

Composes Runtime traces, Agent Eval, ISR, Skills Vault, LLM R&D, AFM and Model Registry.

Learning levels may include operational/routing learning, prompt/skill/workflow candidate improvement, runtime/code candidate improvement and offline model improvement.

Durable changes are immutable candidates, not mutation of the running governing system.

Promotion requires appropriate targeted, regression, OOD, safety and independent evidence. The improvement process cannot self-change governance, mint authority, lower verification requirements or self-promote.

---

## 8. Correlation substrate

`platform-event-ref/0.1` remains a correlation-only projection beneath the fabrics. It does not replace Trust Gateway audit entries, WORKS events, OpenTelemetry spans, Wie observations or verification evidence.

Where applicable, the consequential causal chain preserves identities such as:

```text
tenant_id
principal_id
mission_id
action_id
authority_ref
attempt_id
work_id
evidence_refs
verification_id
```

Not every domain object must contain every identifier. Adapters preserve identity without semantic reinterpretation.

A mismatch in causal identity between authority, admission, runtime attempt, durable effect, evidence and verification is a platform verification failure.

---

## 9. Genericized AVC-derived primitives

V4 removes `Personal*` as a platform architecture category. Personal usage is a scope, not a separate subsystem.

| Legacy concept | V4 target |
|---|---|
| `PersonalEntity` | `Entity` |
| `PersonalRelationship` | `Relationship` |
| `SituationRoom` | `Situation` |
| `PersonalCommitment` | `Commitment` |
| `PersonalAgentAssignment` | generic delegated assignment under Agent Organization |
| `PersonalProactivity` | `AttentionPolicy`, `AttentionCandidate`, `Opportunity` |
| `PersonalConversation` | `InteractionThread` |
| `PersonalConsent` | `ConsentRecord` |
| `PersonalDomain` | canonical domain/classification policy |
| Friday Advisor | `AssistantAdvisor` capability/profile |
| Friday persona | `AssistantProfile` |

Legacy SituationRoom, entity/relationship, commitment, consent, attention and world-intelligence contracts remain provenance sources for the new generic designs. They are not copied blindly; semantics are reconciled with the current Aftergraph owners.

---

## 10. Commitment model

Wie is the canonical Commitment owner.

Two-stage admission is required:

```text
Observation / explicit assertion
  -> CommitmentCandidate
  -> resolution/admission
  -> Commitment
```

Model-extracted commitments remain candidates until accepted by the applicable resolution policy. Explicit principal assertions carry stronger provenance but still enter the same canonical system.

The lifecycle supports at least:

```text
candidate
effective
disputed
superseded
cancelled
fulfilled
```

The model preserves distinctions such as idea, wish, plan, decision, task, promise, deadline, recurring obligation and awaited response where useful.

Conflicting commitments are retained as versioned/contradictory assertions until resolved. A later correction supersedes the earlier assertion rather than silently rewriting its history.

Commitment completion does not itself prove a verified downstream outcome. Where a commitment requires digital work, it may create/promote a WorkCandidate or mission through the ordinary governed path.

---

## 11. Attention model

Attention is a four-stage pipeline:

```text
Signal / finding / opportunity
  -> AttentionCandidate
  -> Runtime AttentionDecision
  -> classification-aware disclosure projection
  -> surface delivery
```

Studio owns `AttentionPolicy` experience and principal preferences such as quiet hours, channel preference, digest behavior and interruptibility.

Runtime owns `AttentionDecision` using current mission/runtime context. Decision outputs include at least:

```text
SILENT
DIGEST
NOTIFY
ESCALATE
```

Runtime may determine urgency/when/whether to notify, but not bypass classification/purpose controls when generating delivery content. A restricted issue may result in an opaque notification on Telegram and a richer authenticated projection inside Studio.

Useful inherited dimensions include confidence, expected value, interruption cost, cooldown and maximum nudges.

---

## 12. Tenant, workspace and consent lifecycle

### Tenant lifecycle

Trust Gateway holds authoritative operational lifecycle state and coordinates transitions. Domain owners remain responsible for their own data/state.

`DELETING` immediately denies new grants, new ingestion and new execution for the tenant. Each required owner returns export/deletion/retention acknowledgement before the lifecycle reaches `DELETED`.

Audit/evidence retention obligations are distinct from source-retention or derived-state-use policy.

### Workspace

Trust/Tenant Registry owns workspace-scope identity, tenant binding and membership/access scope.

Studio owns layout, spatial state, view state, recents and experience preferences.

Workspace tenant binding is immutable. Cross-tenant migration uses governed export, filtering, new identity, import and provenance linking.

### Consent

Trust Gateway owns Consent Ledger state and enforcement. Consent events include at least:

```text
ConsentGranted
ConsentRestricted
ConsentRevoked
ConsentExpired
```

Revocation/expiry may invalidate:

- new connector ingestion;
- use of already-derived contextual memory where purpose no longer permits it;
- active context bundles;
- ACC projections;
- World State assertions derived solely from the revoked source/purpose;
- future research/personalization processing.

Historic execution/audit/evidence is handled by its own retention law and is not silently erased merely because a source or personalization consent was revoked.

---

## 13. Pocket placement

Pocket is a multi-tenant Perception Fabric source, initially through a provider subsystem in `wi-backend` rather than a new repository.

V1 integration architecture:

```text
Pocket REST / webhooks / optional MCP
  -> tenant-scoped connector
  -> webhook signature/replay/dedupe guard
  -> REST reconciliation/hydration
  -> Pocket source adapter
  -> Wie Observation
```

Provider credentials are tenant-scoped secret references, not raw secrets in Wie domain state.

Pocket's REST path is canonical-data/reconciliation oriented, webhooks are event-plane signals, and MCP is optional interactive access rather than the canonical ingestion source.

Pocket output remains untrusted observation content. Speaker labels are not principal identity. A spoken command does not directly execute. Transcript, speaker attribution, summary and action extraction retain derivation lineage and different evidentiary weights.

A Pocket-derived commitment may become a `CommitmentCandidate`; consequential action still follows AIE -> Trust Gateway -> Runtime -> WORKS -> verification.

Source deletion or consent revocation must invalidate downstream use/recompute derived state according to provenance without rewriting historical audit/evidence.

---

## 14. Realtime voice placement

Realtime voice is an Interaction Fabric adapter, not the owner of identity, memory, missions or authority.

Conceptual path:

```text
Microphone
  -> Realtime Voice Edge
  -> InteractionTurn
  -> Context/Situation
  -> Intelligence
  -> governed consequential path when needed
```

Live speech and durable mission execution are separate loops.

At minimum, stop/cancel semantics distinguish:

```text
STOP_SPEAKING
CANCEL_TURN
PAUSE_MISSION
CANCEL_MISSION
FREEZE_AUTONOMY
```

Barge-in defaults to speech/turn interruption. It must not ambiguously terminate consequential execution.

Voice session/model identity is disposable. Durable principal, interaction state, context, mission and evidence remain Aftergraph state.

---

## 15. Brand and naming policy

Target platform/masterbrand is `Aftergraph`.

Canonical active namespace:

```text
@aftergraph/*
```

No new active identifiers may use:

```text
AVC
Autonomous Venture Company
avc-*
@avc/*
ABDE Platform
ABDE Intelligence platform
```

Historical records retain old names when required for provenance. Academic authorship and the historic Jonas Abde Intelligence Systems Research Program may remain accurately attributed and must not be rewritten into false history.

Existing provisional trademark/legal notes remain a separate governance/legal task; this architecture approval does not constitute trademark clearance.

---

## 16. AVC dissolution and extraction ledger

The legacy repository is a migration source, not a target platform owner.

The extraction baseline is pinned to:

```text
18317c7b2eebcc08bb2a1b30d9118935d5832540
```

with the subsequent delta to the current legacy head audited separately.

Each legacy asset is assigned one of:

```text
MIGRATED_VERIFIED
MIGRATED_TRANSITIONAL
EXTRACT
RETIRE
HISTORY_ONLY
```

A machine-readable dissolution record contains at least:

```yaml
source_repo: autonomous-venture-company
source_ref: <sha>
source_path: <path>
disposition: <state>
target_owner: <repo-or-null>
target_contract: <contract-or-null>
active_consumers: []
compatibility_aliases: []
verification: {}
deletion_gate: []
```

The AVC repository may be archived/read-only only when all applicable gates are satisfied:

- zero active `@avc/*` package dependencies except allowlisted provenance;
- zero canonical services owned by AVC;
- zero canonical skills owned by AVC;
- zero current normative contracts owned by AVC;
- Human Governance ownership resolved;
- tenant/workspace lifecycle ownership resolved;
- Hermes execution adapter migrated/reconciled;
- World/Situation/Commitment/Consent/Attention primitives extracted or retired;
- no unclassified package/app/skill/ML/cell/infra asset remains;
- Golden Mission succeeds without an AVC dependency;
- all affected target repositories pass exact-head verification;
- provenance remains reachable after archive.

Skills Vault becomes the sole active canonical skill supply-chain owner. Generic reusable `avc-*` skills migrate to Aftergraph canonical identifiers with legacy aliases/provenance as needed; persona/product-specific skills are generalized or retired.

---

## 17. Constitutional invariants

V4 freezes these platform invariants:

1. `Complete != Verified`.
2. Observation does not grant authority.
3. Memory does not grant authority.
4. Relationship does not equal delegation.
5. Consent does not equal authority.
6. Prediction does not equal observation.
7. Experience is not canonical domain truth.
8. Runtime may orchestrate but may not widen authority.
9. An implementation may not widen the semantic capability authority envelope.
10. An executor may not independently verify itself.
11. Cross-tenant movement requires explicit export/import and new scope identity where applicable.
12. Revocation invalidates downstream use according to provenance/policy.
13. Historical approval never implies current authority.
14. Agent/model/skill installation never grants execution authority.
15. World State is a rebuildable projection, not writable truth.
16. Causal identity must survive consequential seams.
17. Consequential ambiguity fails closed.
18. No new top-level plane is created unless existing ownership is demonstrably incapable of containing the concern without violating another invariant.

---

## 18. Failure taxonomy

Cross-platform conformance and adversarial campaigns SHOULD cover at least:

```text
F01 AUTHORITY_LAUNDERING
F02 PRINCIPAL_DRIFT
F03 TENANT_DRIFT
F04 DOMAIN_LEAKAGE
F05 STALE_STATE_USE
F06 PREDICTION_AS_FACT
F07 SOURCE_REVOCATION_FAILURE
F08 CONSENT_REVOCATION_FAILURE
F09 DERIVED_STATE_RESURRECTION
F10 COMMITMENT_CONTRADICTION
F11 DUPLICATE_OPPORTUNITY
F12 EFFECT_DUPLICATION
F13 IMPLEMENTATION_AUTHORITY_WIDENING
F14 WORKSPACE_SCOPE_DRIFT
F15 NOTIFICATION_DISCLOSURE
F16 VERIFIER_UNAVAILABLE
F17 EVIDENCE_CAUSAL_MISMATCH
F18 REPLAY
F19 CONFUSED_DEPUTY
F20 WORLD_STATE_SELF_MUTATION
F21 DELEGATION_RECURSION
F22 TENANT_DELETION_PARTIAL_FAILURE
F23 HANDOFF_CONTEXT_DOWNGRADE
F24 HISTORICAL_APPROVAL_REUSE
```

The tests are owned by the domain that can best falsify the guarantee: Governance conformance vectors, Continuum fault campaigns, Trust Gateway adversarial tests, Runtime integration tests, Wie tests, WORKS tests, Sentinel verifier tests and ISR/MISSION-Bench research where scientific claims are made.

---

## 19. Golden Mission V1

The first platform-wide composed proof uses a physical/digital observation path:

```text
Physical or digital event
  -> Pocket/other source
  -> Observation
  -> Situation + Context
  -> CommitmentCandidate / WorkCandidate
  -> Mission
  -> AIE authority
  -> Trust Gateway admission
  -> Runtime CapabilityAction
  -> eligible implementation
  -> WORKS durable execution
  -> Evidence
  -> independent verification
  -> Verified Outcome
  -> Studio / voice / Telegram projection
```

The Golden Mission must preserve canonical identity across the consequential chain and exercise both successful and fail-closed branches.

Required adversarial branches include at least:

- duplicate input/webhook;
- deleted/revoked source;
- consent revocation;
- cross-tenant source or context;
- principal drift;
- stale context or stale World State;
- prediction used as fact;
- conflicting/superseded commitment;
- revoked/expired authority mid-flight;
- budget exhaustion;
- Runtime crash/rebuild;
- worker crash and retry;
- duplicate effect prevention;
- implementation authority widening;
- verifier unavailable;
- evidence/causal mismatch;
- replay;
- notification disclosure on an under-trusted surface.

A Golden Mission that proves only the happy path is a demo, not platform conformance.

---

## 20. Conformance ladder

V4 introduces a maturity ladder so `implemented` is not treated as a single binary claim.

### L0 REGISTERED

Owner, contract identity and lifecycle are registered.

### L1 CONTRACT-CONFORMANT

Schema/invariants and adversarial contract vectors pass.

### L2 ADAPTER-CONFORMANT

At least one real producer/consumer adapter path demonstrates the contract without semantic reinterpretation. Promotion of shared Fabric contracts may require two independent adapters where specified.

### L3 COMPOSITION-CONFORMANT

Multiple exact-head repositories preserve canonical semantics and causal identity across a composed path.

### L4 ADVERSARIAL-CONFORMANT

Failure, replay, revocation, crash/recovery, stale-state and isolation cases are proven fail-closed or correctly recoverable.

### L5 LIVE-CHARACTERIZED

The capability has real-environment measurements for reliability, latency, cost/context overhead and operational limits.

### L6 SCIENTIFICALLY-SUPPORTED

Where a scientific/general performance claim is made, it is backed by preregistered/reproducible research evidence appropriate to the claim.

A Studio reference surface can be L1/L2 while the platform-wide capability remains below L4/L5. UI presence never upgrades upstream maturity by implication.

---

## 21. Promotion gates for Platform Fabrics V1

A Fabric contract stays experimental until its applicable gates pass:

1. canonical owner and prohibited-owner boundaries are registered;
2. schemas/invariants and adversarial vectors pass;
3. real adapters preserve semantics and causal identity;
4. exact repository heads are recorded for composed evidence;
5. fallback/recovery paths cannot widen authority;
6. cross-tenant and revocation behavior is demonstrated;
7. Golden Mission coverage includes failure/refusal/recovery paths;
8. overhead and operational limits are measured;
9. an independent verifier or research owner evaluates claims that cannot be self-attested by the implementation owner.

---

## 22. Recommended delivery sequence

Implementation planning should decompose V4 into bounded cross-repo waves rather than attempt a 24-repository rewrite.

### Wave A — Canonical truth convergence

- create `PLATFORM-ARCHITECTURE-V4.md` from this approved design;
- introduce `platform-topology/2.0`;
- reconcile dependencies/registry/README/org-state generation;
- converge active Aftergraph naming while retaining provenance.

### Wave B — Existing Fabric closure

- complete TG and WORKS `platform-event-ref/0.1` adapters;
- complete Runtime `capability-action/0.1` resolver and authority-preserving fallback;
- bind Verified Auto seams to the V4 ownership model;
- establish Golden Mission skeleton with exact-head pins.

### Wave C — Context and World State

- formalize Memory/ACC/WORKS Brain separation;
- genericize Situation/Entity/Relationship contracts;
- add `world-assertion/0.1` / `situation/0.1` experimental contracts;
- implement rebuild/currentness/invalidation conformance before production dependence.

### Wave D — Governance and lifecycle gaps

- resolve human-governance authority through AIE + TG enforcement;
- implement tenant/workspace lifecycle protocol;
- implement Consent Ledger events and downstream invalidation semantics.

### Wave E — Proactivity and organization

- unify Opportunity/AttentionCandidate correlation across Wie, Runtime and Cron without a new service;
- strengthen Agent Organization conformance and independent evals.

### Wave F — Physical-world perception

- add multi-tenant Pocket connector under Wie;
- prove source lineage, webhook replay/dedupe, deletion, consent and cross-tenant behavior;
- run physical-device characterization after hardware arrival.

### Wave G — Interaction

- generalize interaction/presence contracts;
- add realtime voice edge and cross-surface continuity;
- keep durable identity/state outside realtime sessions.

### Wave H — Verified improvement

- production trace schema;
- challenger candidate flow;
- routing/skill/workflow promotion gates;
- AFM/model promotion only through model research + registry evidence.

### Wave I — AVC retirement

- execute the dissolution ledger;
- migrate canonical skills and Hermes adapter;
- remove active consumers;
- run Aftergraph-only Golden Mission;
- archive the legacy repository once every gate is evidenced.

---

## 23. Acceptance criteria for the architecture implementation

Architecture V4 is considered implemented, not merely documented, when:

1. topology/ownership projections agree on current repository identities and lifecycle;
2. no canonical active document assigns platform ownership to retired AVC identities;
3. all seven planes have explicit `owns` and `must_not_own` boundaries;
4. the eight Fabrics are registered without creating new authority/execution owners;
5. Runtime transitional ownership is purified or explicitly time-bounded;
6. World State is projection-only and provenance/currentness tested;
7. commitment resolution is canonical in Wie;
8. human-governance and tenant/workspace lifecycle seams are resolved;
9. consent revocation produces downstream invalidation behavior;
10. capability fallback proves no authority widening;
11. Golden Mission passes success, refusal, revocation, crash/recovery and verifier-failure branches on exact heads;
12. the legacy AVC dissolution ledger is complete enough to prove every remaining active dependency or classify it as historical;
13. platform maturity labels use the V4 conformance ladder rather than implying platform completeness from repo-local success.

---

## 24. Decision summary

### Permanent planes

```text
Intelligence
Authority
Trust
Runtime
Execution
Verification
Experience
```

### Platform Fabrics V1

```text
Interaction
Perception
Context
World State
Proactivity
Capability
Agent Organization
Verified Improvement
```

### Underlying correlation substrate

```text
platform-event-ref/0.1
+ canonical causal identifiers
```

### Core target

Aftergraph itself becomes the multimodal, persistent, proactive, governed and verifiable intelligent-system platform. Pocket, voice, ambient context, personal-assistant behavior, coding agents, multi-agent organizations and future devices are manifestations of the same platform capabilities, not separate platform architectures.

The architecture intentionally ends here. New features should compose these owners and fabrics before proposing a new plane, new truth store or new top-level service.
