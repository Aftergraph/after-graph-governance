# Aftergraph Verified Auto Execution — Design

**Status:** Proposed canonical cross-repo design, owner-approved in chat on 2026-09-08; implementation remains gated on written-spec review.

**Date:** 2026-09-08

**Owner:** Aftergraph portfolio control

**Scope:** User-facing Auto / Verified execution strategy spanning the existing Aftergraph planes. This design does not create a new platform plane, service, product runtime, or model-owning repository.

---

## 1. Problem

Aftergraph already has the primitives needed to turn intent into governed, durable and independently verified outcomes, but model selection and execution economics are not yet composed into one user-facing feature.

Today:

- Studio owns the human experience but does not expose a canonical automatic execution strategy.
- AIE owns authority, delegation and budget semantics.
- Trust Gateway owns provider/model admission and already exposes advisory model routing.
- Runtime owns agent lifecycle, orchestration, dispatch, checkpoints, metering and model-edge integration.
- WORKS owns durable execution state, WorkGraph, workers, leases, retries, receipts and canonical execution evidence.
- Sentinel owns independent exact-subject verification and stale invalidation.
- Research owns scientific evaluation and claims, not runtime authority.

The missing product capability is a governed execution strategy that automatically selects a permitted model route, keeps execution durable, escalates only when evidence requires it, and distinguishes execution completion from independently verified completion.

---

## 2. Product feature

The user-facing feature is **Verified Auto Execution**.

It appears inside Studio's existing **Work** experience rather than creating a fourth permanent top-level mode beside Chat, Work and Space.

Two execution strategies are exposed:

### Auto

Aftergraph selects the best permitted execution strategy for the mission using capability, policy, budget, data handling constraints, provider health, recent outcome telemetry and execution context.

Auto may complete without an independent verification verdict when the mission contract does not require one. Auto must never label an outcome as independently verified without a verifier receipt.

### Verified

Verified is Auto plus a mandatory independent verification requirement before the user-facing outcome may carry `VERIFIED` state.

For source-code work, the first verifier is Sentinel against the exact resulting subject SHA. Other domains may add independent verifiers later without changing the execution contract.

### User-visible controls

The initial Studio surface exposes:

- execution strategy: `auto | verified`;
- maximum authorized mission spend;
- data classification;
- whether provider training use is permitted;
- live execution state;
- accumulated model cost;
- attempt/escalation count;
- final execution evidence;
- verifier verdict and exact subject when applicable.

The ordinary user does not need to choose a provider or model. Advanced inspection may show the selected route and rationale.

---

## 3. Non-goals

This design does **not**:

1. create an `Aftergraph Model Fabric` service;
2. move provider/model routing out of Trust Gateway;
3. move orchestration out of Runtime;
4. let WORKS self-declare independent verification;
5. put third-party API models into the immutable Aftergraph-owned model lifecycle namespace;
6. make Muse Spark 1.3 Contributor a permanent champion without Aftergraph evidence;
7. market benchmark or savings claims before production-quality evidence exists;
8. allow a low-cost route to bypass AIE authority, Trust Gateway policy, WORKS durability or Sentinel independence.

---

## 4. Canonical plane ownership

The existing seven-plane lifecycle remains normative:

```text
Intent
  -> Intelligence
  -> Authority
  -> Trust
  -> Runtime
  -> Execution
  -> Evidence
  -> Verification
  -> Verified Outcome
```

Verified Auto composes the planes as follows.

### Studio — Experience

Owns:

- Auto / Verified user controls;
- budget and data-policy presentation;
- live execution and escalation visualization;
- cost display;
- evidence and verification result presentation.

Must not:

- select or admit models independently;
- mint authority;
- mutate WORKS evidence;
- manufacture a verified state.

### AIE — Authority

Owns:

- whether the principal may execute the mission;
- the authorized budget ceiling;
- delegation and revocation semantics;
- authority required for escalation when escalation expands authorized spend or capability.

Must not:

- select providers/models;
- execute workers;
- issue verification verdicts.

### Trust Gateway — Trust / Enforcement

Owns:

- provider/model eligibility;
- data-handling policy enforcement;
- training-use eligibility;
- provider health and routing-policy checks;
- route decisions and route receipts;
- break-glass admission rules;
- routing audit entries.

Must not:

- own agent lifecycle;
- persist durable WorkGraph execution state;
- independently verify execution output.

### Runtime — Agent operation

Owns:

- planner/worker lifecycle;
- dispatch;
- model-session creation;
- route stickiness during an execution context;
- retry and repair orchestration;
- escalation requests at defined boundaries;
- runtime metering and observability.

Must not:

- bypass Trust Gateway routing/admission;
- replace WORKS as durable execution truth;
- declare independent verification.

### WORKS — Durable execution

Owns:

- WorkGraph and durable Work state;
- workers, leases, retries and recovery;
- attempt history;
- attached route-receipt references;
- actual execution cost records;
- canonical execution evidence and quittance.

Must not:

- reinterpret route policy;
- self-approve expanded authority;
- self-verify the resulting subject.

### Sentinel — Verification

Owns for code workloads:

- exact-subject verification;
- stale invalidation;
- evidence-backed `SHIP | DO_NOT_SHIP | STALE` verdicts;
- verification receipts.

Must not:

- execute or repair the code it verifies inside the same verification authority boundary;
- silently verify a different subject after the execution target moves.

### Research — Evidence and evaluation

Owns:

- experiments comparing execution strategies;
- CPVO/VSR/FCR/HEVO measurement;
- scientific claims and falsification discipline.

Must not:

- become a runtime authority source;
- promote an execution strategy from anecdotal results.

---

## 5. Model ownership and third-party catalog boundary

`Aftergraph/model-registry` continues to own immutable lifecycle records for Aftergraph-owned model families such as AFM.

Third-party provider/model operational metadata belongs to Trust Gateway's provider catalog or another Trust-owned generated catalog. It must not be represented as an Aftergraph model release merely because Aftergraph can route to it.

A future shared machine-readable external-model catalog may be introduced only if Governance assigns a canonical owner and consumers stop maintaining competing sources of truth.

Initial implementation therefore extends Trust Gateway's existing provider/router surfaces rather than repurposing `model-registry`.

---

## 6. Execution modes

Canonical values:

```text
auto
verified
```

No `economy`, `deep`, `premium` or provider-branded user modes are introduced in V1. Cost/quality preferences remain internal routing policy or advanced configuration until evidence shows a user-facing need.

### Auto semantic

`auto` means:

> Select and execute the best currently permitted strategy within authority, policy and budget, using evidence-driven escalation when required.

### Verified semantic

`verified` means:

> Execute under Auto semantics, then require an independent verifier receipt bound to the exact result before the outcome may be presented as VERIFIED.

`verified` does not imply that every intermediate model call was independently checked.

---

## 7. Data handling policy

Routing must not reduce data governance to repository visibility alone.

Canonical V1 data classes:

```text
public
internal
confidential
restricted
```

The route request also carries:

```text
provider_training_allowed: boolean
```

Rules:

1. `provider_training_allowed=false` excludes any route whose terms allow provider use of submitted input/output for model improvement or training in a way prohibited by policy.
2. `restricted` defaults to no external training-eligible route and may require local or explicitly approved private processing.
3. Secrets are not model payload data. Secret references stay outside model context and are resolved only at authorized tool boundaries.
4. Public data does not automatically imply training permission.
5. A lower-cost route never overrides a stricter data-policy constraint.

Muse Spark 1.3 Contributor may initially be eligible only when the Trust policy records that contributor use is permitted for the workload.

---

## 8. Route request

Trust Gateway's existing `POST /v2/router/route` remains backward compatible.

The extended request accepts:

```json
{
  "capability": "code",
  "budget_tier": "economy",
  "execution_mode": "verified",
  "data_class": "public",
  "provider_training_allowed": true,
  "max_cost_usd": 2.0,
  "verification": "exact_head",
  "execution_context_id": "ctx_0123456789abcdef0123456789abcdef"
}
```

V1 compatibility law:

- callers that send only `capability` and `budget_tier` receive the existing advisory behavior;
- new policy fields may only narrow eligibility, never silently widen it;
- malformed or unsupported restrictive policy fields fail closed rather than being ignored.

---

## 9. Route receipt

A successful policy-aware route emits a durable, auditable `RouteReceipt`.

Logical shape:

```json
{
  "schema": "model-route/1.0",
  "route_id": "rte_0123456789abcdef0123456789abcdef",
  "execution_context_id": "ctx_0123456789abcdef0123456789abcdef",
  "provider": "meta-model-api",
  "model": "muse-spark-1.3-contributor",
  "capability": "code",
  "execution_mode": "verified",
  "data_class": "public",
  "provider_training_allowed": true,
  "budget": {
    "max_cost_usd": 2.0
  },
  "selection": {
    "reason_codes": [
      "capability_match",
      "data_policy_match",
      "budget_match",
      "provider_healthy"
    ]
  },
  "verification_required": true,
  "issued_at": "2026-09-08T00:00:00Z"
}
```

Normative properties:

1. `route_id` is immutable.
2. The receipt names the actual selected provider and model.
3. Reason codes are machine-readable and non-secret.
4. The receipt carries policy-relevant inputs required to explain selection.
5. It is not an authority token.
6. It is not a verification receipt.
7. It may be referenced by Runtime and WORKS but only Trust Gateway issues it.
8. Pricing metadata used in the decision must be separately versioned or provenance-stamped so historical cost analysis is reproducible.

The exact JSON Schema is a Governance-registered contract owned by Trust Gateway. Governance registers the family and ownership; Trust Gateway owns normative route semantics.

---

## 10. Routing policy

The router evaluates candidates in this order:

1. authority-compatible budget envelope;
2. data/training policy eligibility;
3. required capability;
4. provider availability and health;
5. mission maximum cost;
6. recent outcome telemetry for the workload class when enough evidence exists;
7. expected cost;
8. stable deterministic tie-break.

A candidate failing an earlier gate cannot regain eligibility because it scores better on a later gate.

### V1 reason codes

At minimum:

```text
capability_match
data_policy_match
training_policy_match
budget_match
provider_healthy
recent_outcome_preferred
cost_preferred
fallback
break_glass
```

### Break glass

Break-glass routing:

- is off by default;
- must be explicitly authorized;
- cannot violate data/training restrictions;
- cannot exceed authority or budget;
- is always audited;
- never changes a Verified requirement into Auto completion.

---

## 11. Session stickiness

The route is pinned to an `execution_context_id` for a normal model session.

Runtime must not reroute on every turn.

Allowed reroute boundaries:

1. selected provider becomes unavailable;
2. selected route becomes policy-ineligible;
3. retry/repair threshold is reached;
4. model context is intentionally reset;
5. authorized escalation is requested;
6. the mission moves into a verifier phase that requires an independent model or verifier.

Every reroute creates a new `RouteReceipt` linked to the same execution context and records the previous route as its predecessor.

This preserves model continuity and makes prompt-cache economics measurable.

---

## 12. Failure-driven escalation

V1 does not run a worker swarm for every task.

Default sequence for code workloads:

```text
route
  -> primary attempt
  -> deterministic tests/checks
      -> pass: continue toward completion / verification
      -> fail: repair attempt on pinned route
          -> pass: continue
          -> fail threshold reached: request escalation
              -> Trust re-routes within remaining authority/budget
              -> Runtime continues with new receipt
```

Parallel independent workers may be requested when at least one of these applies:

- workload complexity policy explicitly requests them;
- uncertainty exceeds a configured threshold backed by measurable signal;
- prior attempt failed and independent solution generation is cheaper than repeated repair;
- the mission contract requires independent implementation comparison.

V1 must not invent a complexity classifier whose output has no validation evidence. Until such evidence exists, parallelism is explicit policy or failure-driven.

---

## 13. Cost accounting

Three cost concepts remain distinct:

### Estimated route cost

Trust Gateway may use provider pricing metadata for selection.

### Actual model cost

Runtime meters model usage and emits actual provider/model consumption data. WORKS attaches the durable cost record to the Work attempt.

### Cost Per Verified Outcome (CPVO)

Research/analytics computes:

```text
sum(actual execution + verification model cost)
------------------------------------------------
number of independently verified successful outcomes
```

No UI may present estimated route price as actual cost.

No public claim may present synthetic CPVO as production CPVO.

---

## 14. Verification flow

For Verified code execution:

```text
WORKS produces candidate execution result
  -> exact subject SHA is frozen for verification request
  -> Sentinel evaluates that subject
  -> Sentinel returns verdict receipt
  -> WORKS references the receipt
  -> Studio projects status
```

Rules:

1. `SHIP` against the exact current subject can produce `VERIFIED`.
2. `DO_NOT_SHIP` cannot produce `VERIFIED`; Runtime may initiate another repair attempt if authority/budget remains.
3. `STALE` cannot produce `VERIFIED`; the moved subject must be re-verified.
4. Execution success and independent verification success are different states.
5. Sentinel must not accept a WORKS or Runtime self-assertion as verification evidence.

---

## 15. State projection

Studio V1 projects the following user-facing lifecycle without inventing a new durable owner:

```text
queued
planning
routing
executing
testing
repairing
escalating
verifying
completed
verified
needs_you
failed
```

These are presentation states derived from canonical owners. Studio must not persist a competing authoritative lifecycle.

`completed` means execution finished according to the mission's execution requirements.

`verified` means an applicable independent verifier issued a valid non-stale success receipt for the exact result.

---

## 16. Needs You

The system enters `needs_you` only for a decision that cannot be safely resolved inside existing authority/policy, including:

- additional budget approval;
- provider-training permission not already granted;
- data-classification ambiguity that changes route eligibility;
- break-glass authorization;
- destructive action requiring human approval under Trust policy.

A normal provider failure, model failure, test failure or retry is not itself a reason to involve the user if the mission already authorizes recovery.

---

## 17. Telemetry and learning

Trust Gateway already records recent provider/model outcomes. Verified Auto extends the learning target from raw provider availability toward **verified execution economics**.

Future routing evidence may include:

```text
(provider, model, workload_class)
  -> success rate
  -> verification pass rate
  -> repair rate
  -> escalation rate
  -> latency
  -> actual cost
  -> CPVO
```

V1 constraints:

1. telemetry may demote candidates only after a documented minimum sample threshold;
2. unknown models are neutral, not assumed superior;
3. provider availability telemetry and verified-outcome telemetry remain separate dimensions;
4. routing policy changes based on telemetry are auditable;
5. no black-box self-modifying policy is introduced in V1.

---

## 18. Initial Muse Spark 1.3 Contributor role

Muse Spark 1.3 Contributor is an **execution candidate**, not an Aftergraph model family or permanent champion.

Initial intended use:

- public Aftergraph repositories;
- open-source implementation;
- tests;
- refactors;
- CI investigation and repair;
- public documentation and research code;
- other workloads explicitly permitting provider training use.

Not eligible by default for:

- confidential data;
- restricted data;
- customer-sensitive private payloads;
- secrets;
- workloads whose policy forbids training-eligible providers.

Promotion to a preferred route for any workload class requires Aftergraph evidence comparing verified outcomes, not anecdotal coding quality.

---

## 19. Research validation

Before public efficiency claims, Aftergraph Research preregisters a production-adjacent experiment using real or representative Aftergraph work items.

Initial arms:

```text
A: Spark 1.3 Contributor, one attempt
B: Spark 1.3 Contributor, repair loop
C: Spark 1.3 Contributor + independent verification
D: approved premium route alone
E: adaptive Verified Auto
```

Primary measures:

- Verified Success Rate (VSR);
- False Completion Rate (FCR);
- Cost Per Verified Outcome (CPVO);
- Human Effort Per Outcome (HEVO);
- wall-clock time;
- actual input/output/cache tokens;
- repair count;
- escalation rate;
- verifier pass rate;
- route failure rate.

The experiment must distinguish provider failures from model-quality failures and execution-harness failures.

---

## 20. Security invariants

1. Route selection never grants authority.
2. Provider credentials never appear in route receipts or model payloads.
3. Secret values never enter routing telemetry.
4. Restrictive data policy fails closed.
5. Training permission is explicit policy input, not inferred from repository visibility.
6. Break glass cannot override data/training, authority or budget boundaries.
7. A model cannot mark its own output independently verified.
8. Reroutes and escalations are auditable.
9. Verification is bound to an exact subject.
10. A stale verification result cannot be silently reused.

---

## 21. Error semantics

Canonical classes for the feature:

```text
route_unavailable
route_policy_denied
route_budget_exhausted
route_provider_unhealthy
execution_failed
repair_exhausted
escalation_requires_authority
verification_failed
verification_stale
verification_unavailable
```

Rules:

- policy denial is not treated as provider failure;
- budget exhaustion is not treated as model failure;
- verification unavailability never degrades Verified into Auto completion;
- a transient provider failure may trigger an authorized reroute;
- deterministic test failures are execution evidence, not route-health evidence by themselves.

---

## 22. Rollout

### Phase 0 — Contract and shadow routing

- register `model-route/1.0` ownership and schema;
- extend Trust Gateway route request in backward-compatible advisory mode;
- add policy/data fields and route receipts;
- add Meta Model API / Muse candidate only if credentials and terms are explicitly configured;
- emit shadow recommendations without changing Runtime dispatch;
- collect route-choice and provider-health telemetry.

### Phase 1 — Runtime consumption

- Runtime requests and pins Trust routes;
- reroute only at defined boundaries;
- WORKS stores route receipt refs, attempt history and actual model costs;
- no Studio Verified label yet.

### Phase 2 — Verified code loop

- freeze resulting exact subject;
- invoke Sentinel independently;
- attach verification receipt;
- allow `verified` projection only on valid exact-subject success.

### Phase 3 — Studio feature

- expose Auto / Verified in Work;
- show budget, live cost, attempts, escalation and evidence;
- hide provider/model choice by default;
- expose route rationale in advanced inspection.

### Phase 4 — Research-backed optimization

- run preregistered comparison;
- tune workload-specific routing only from measured outcomes;
- publish claims only within the evidence boundary.

### Phase 5 — Public positioning

Aftergraph.org may describe Verified Auto only after the underlying capability is live and evidence-backed. The public site references canonical owners and must not upgrade implementation state or research evidence.

---

## 23. Repository implementation map

| Concern | Canonical repo | V1 change |
|---|---|---|
| Cross-repo registration | `after-graph-governance` | register route contract family and ownership |
| Provider/model routing | `trust-gateway` | Router v0.2, data/training policy, route receipts, Meta candidate, tests |
| Agent orchestration | `runtime` | route client, pinning, reroute/escalation hooks, metering |
| Durable execution | `works-execution` | route receipt reference, model-cost evidence, attempt/escalation history |
| Independent code verification | `sentinel` | exact-subject invocation/receipt seam if not already consumable |
| User experience | `studio` | Auto / Verified Work controls and outcome projection |
| Scientific evaluation | `intelligence-systems-research` | preregister and run verified execution economics study |
| Continuous triggers | `aftergraph-cron-fabric` | optional later consumer of Auto missions after core loop is stable |
| Public positioning | `aftergraph.org` | only after capability is live and supportable |

---

## 24. Acceptance criteria

The first end-to-end Verified Auto slice is complete only when all of the following are true:

1. Studio can submit a code Work with `execution_mode=verified`, budget, data class and training permission.
2. AIE authority/budget remains authoritative and can deny or constrain escalation.
3. Trust Gateway issues a policy-aware route receipt without exposing secrets.
4. Runtime pins the selected route to one execution context.
5. WORKS durably records execution attempts and actual model cost.
6. A failed attempt can repair and, at the configured boundary, reroute without losing the Work identity.
7. Sentinel verifies the exact resulting subject independently.
8. A moved subject invalidates the previous verification result.
9. Studio cannot display `VERIFIED` without a valid verifier receipt.
10. Contributor-style training-eligible routes are excluded when `provider_training_allowed=false`.
11. The existing legacy `capability + budget_tier` route request remains compatible.
12. Tests cover policy denial, budget exhaustion, provider failure, repair, reroute, verification failure and stale verification.
13. No new platform plane or duplicate durable source of truth is introduced.
14. Public marketing claims remain unchanged until research/production evidence supports them.

---

## 25. Design decision

**Adopt Verified Auto as a cross-plane product capability, not a new service.**

The system value is the composition:

```text
user intent
  -> authorized mission
  -> policy-aware model route
  -> stable runtime session
  -> durable execution and recovery
  -> exact-subject independent verification
  -> evidence-backed user outcome
```

Cheap models such as Muse Spark 1.3 Contributor improve execution economics when policy permits, but the product moat is not a specific model. It is Aftergraph's ability to separate generation, authority, durable execution and independent verification while measuring the cost of the final verified outcome.
