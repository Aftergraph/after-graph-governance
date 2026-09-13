# Aftergraph Platform Collision Risk Register V1

**Status:** PROPOSED convergence control document  
**Date:** 2026-09-11  
**Owner:** `after-graph-governance` for boundary registration only  
**Normative sources:** `PLATFORM-ARCHITECTURE-V4.md`, `platform-topology/2.0.json`, `cross-repo-contracts.md`, `dependencies.yml`  
**Related experimental sources:** `PLATFORM-FABRICS-v0.1.md`, `golden-mission/0.1.json`

## 1. Purpose

Aftergraph now has enough independently useful subsystems that the primary architectural risk is no longer missing functionality. It is **semantic collision**: two correct components independently begin to own the same decision, state, identity, retry, approval, evidence, or verification transition.

This register does not create a new plane, contract owner, orchestration engine, event source, authority source, or verification source. It records collision risks and the boundary tests required before platform integration may be promoted.

The canonical lifecycle remains:

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

Relay is an operator/control projection across that lifecycle. It is not inserted as a new canonical execution seam and does not replace any domain owner.

## 2. Constitutional collision rule

Every consequential object must have exactly one canonical owner for each semantic question:

```text
Who may act?                    -> AIE authority semantics
May this action happen now?     -> Trust Gateway admission/enforcement
How should an agent operate?    -> Runtime
What durable work exists?       -> WORKS
What portable context moves?    -> context-continuity
What does the human see/control?-> Studio / Relay projections
Was the claimed outcome proven? -> Sentinel / registered domain verifier
```

A projection may cache, display, correlate, or request change. It may not silently become canonical truth.

## 3. Identity model used by this register

The following concepts must remain distinct even when one UI displays them together:

```text
Mission      = governed objective
Work         = durable executable unit owned by WORKS
Attempt      = one Runtime execution attempt against Work
Session      = provider/node-specific execution session
Action       = one consequential semantic capability invocation
Evidence     = provenance-bearing record about execution/effect
Verification = independent verdict over an exact subject
```

The platform MUST NOT infer equality merely because two objects share a user-visible title or local identifier.

## 4. Critical collision register

### CR-001 — Relay orchestration vs Runtime orchestration vs WORKS scheduling

**Severity:** CRITICAL  
**Collision:** Relay has mission DAG/operator orchestration; Runtime owns agent orchestration/dispatch; WORKS owns durable scheduling, workers and leases.

**Required boundary:**

- Relay records/operator-projects intent and control.
- Runtime decides how an agent attempt operates.
- WORKS decides durable Work state, lease validity, retry/recovery eligibility and committed execution effects.

**Forbidden:** any of the three independently creating a second canonical state machine for the other two.

**Gate:** a composed mission must tolerate contradictory local projections by reconciling to the canonical owner rather than "last writer wins".

### CR-002 — Relay Mission state vs WORKS Work state

**Severity:** CRITICAL  
**Collision:** Relay mission/step states can look equivalent to WORKS Work/WorkGraph state.

**Required boundary:** Relay mission state is operator-facing orchestration/projection. WORKS state is durable execution truth.

**Gate:** prove `Runtime COMPLETED`, `Relay step SUCCEEDED`, and `WORKS BLOCKED` cannot be collapsed into `VERIFIED` or overwrite WORKS truth.

### CR-003 — Studio control semantics vs Relay control semantics

**Severity:** HIGH  
**Collision:** both surfaces expose missions, approvals, Needs You, evidence, takeover and live state.

**Required boundary:** Studio is the primary user abstraction; Relay is the operator/control plane. Both must resolve to the same canonical approval, mission, action and evidence identifiers.

**Forbidden:** parallel approval objects, parallel mission truth, or independent takeover state machines.

### CR-004 — AIE authority vs Trust Gateway enforcement

**Severity:** CRITICAL  
**Collision:** both domains contain principals, policy, scopes, approvals, budgets and revocation-adjacent behavior.

**Required boundary:**

- AIE defines portable authority/delegation/budget/revocation semantics.
- Trust Gateway evaluates whether an exact action is admissible now and enforces the decision.

**Gate:** an action with valid AIE authority but failed/expired/revoked Trust admission must fail closed; a Trust session may never invent authority absent an AIE-compatible authority basis.

### CR-005 — Runtime execution vs WORKS durable execution

**Severity:** CRITICAL  
**Collision:** both can appear to "run the job".

**Required boundary:** WORKS owns durable Work, lease and execution effect state. Runtime owns an agent attempt used to perform work.

**Invariant:** provider/session/attempt failure must not delete or reinterpret durable Work truth.

### CR-006 — Runtime routing vs Relay Fleet placement

**Severity:** HIGH  
**Collision:** Relay knows node availability/capabilities; Runtime knows mission/provider requirements.

**Required boundary:** Relay Fleet supplies controlled execution inventory and node/session controls. Runtime selects the eligible implementation/target under authority, risk, availability and budget constraints.

**Forbidden:** Relay widening a semantic capability because a more privileged node happens to be available.

### CR-007 — AIE budget vs Trust budget enforcement vs WORKS budget state vs Billing

**Severity:** CRITICAL  
**Collision:** multiple components legitimately need budget information.

**Required semantic split:**

- AIE: what spend/resource authority exists.
- Trust Gateway: action-time budget admission/enforcement.
- WORKS: durable reservations/consumption linked to Work and attempts where applicable.
- Runtime: raw metering observations.
- Billing: commercial settlement/invoicing.

**Gate:** retries/fallbacks must consume the same mission budget lineage; a new provider attempt cannot silently reset the budget.

### CR-008 — Runtime checkpoint vs Continuity capsule vs WORKS state

**Severity:** CRITICAL  
**Collision:** all three carry state sufficient to appear resumable.

**Required boundary:**

- Runtime checkpoint = runtime-local operational resume material.
- Continuity capsule = inert, portable actionable context/state transfer.
- WORKS = durable execution truth.

**Forbidden:** restoring a capsule by overwriting canonical WORKS/AIE/Trust state.

### CR-009 — Revocation vs continuity restore

**Severity:** CRITICAL  
**Collision:** a capsule/checkpoint may preserve authority context created before revocation.

**Required behavior:** portable authority context is descriptive, never current authority. Every resumed consequential path re-evaluates authority/admission before action.

**Adversarial vector:** create capsule -> revoke authority -> restore elsewhere -> consequential action MUST be denied.

### CR-010 — Provider-native tools vs Trust Gateway

**Severity:** CRITICAL  
**Collision:** managed runtimes can call MCP/tools/functions directly and thereby bypass the Aftergraph enforcement path.

**Required boundary:** every consequential tool/effect either passes through Trust Gateway action-time admission or uses a purpose-bound, short-lived credential/token whose scope cannot exceed the admitted semantic capability.

**Forbidden:** vendor/provider-native write capability as an ambient escape hatch.

### CR-011 — Provider/subagent topology vs AIE delegation

**Severity:** CRITICAL  
**Collision:** Runtime/provider may create subagents internally while AIE owns delegation semantics.

**Rule:**

- reasoning-only provider workers without independent consequential authority may remain opaque implementation detail;
- any worker receiving distinct tools, credentials, delegated scope, budget or consequential authority must be represented by a governed principal/delegation boundary.

**Gate:** subagent creation cannot multiply parent privilege or reset budget.

### CR-012 — Retry/recovery vs irreversible effects

**Severity:** CRITICAL  
**Collision:** Runtime/WORKS recovery semantics can duplicate non-idempotent external effects.

**Required behavior:** retry eligibility is effect-aware.

```text
read-only/idempotent                    -> automatic retry may be allowed
write with stable idempotency contract  -> bounded retry may be allowed
non-idempotent consequential effect     -> never blind retry
containment event                       -> hard stop, not recovery
```

### CR-013 — WORKS success vs verification

**Severity:** CRITICAL  
**Collision:** a successful process, Work, or provider result can be misrepresented as a verified outcome.

**Required state separation:**

```text
EXECUTION_COMPLETED
EVIDENCE_READY
VERIFYING
VERIFIED | VERIFICATION_FAILED | VERIFICATION_UNAVAILABLE
```

Only an independent verifier may promote an exact subject to a verified state.

### CR-014 — Audit vs execution evidence vs verification evidence vs telemetry

**Severity:** HIGH  
**Collision:** all are event-like records and can be accidentally collapsed into a generic event ledger.

**Required boundary:**

- Trust audit = enforcement decision history.
- WORKS evidence = durable execution/effect provenance.
- verifier evidence = basis for exact-subject verdict.
- telemetry = operational measurement.
- `platform-event-ref/0.1` / Relay event fabric = correlation projection only.

No class silently upgrades another.

### CR-015 — Relay governed event fabric vs canonical domain truth

**Severity:** HIGH  
**Collision:** Relay v0.9 can correlate/hash-chain events strongly enough to look authoritative.

**Required boundary:** Relay may reconstruct operator projection but MUST retain native `payload_ref`/integrity/source bindings and defer truth to the domain owner.

**Forbidden:** reconstructing a Trust approval, WORKS effect or verifier verdict solely from Relay UI/event state when the native owner disagrees or is unavailable.

### CR-016 — Wie WorkItem vs Mission vs WORKS Work

**Severity:** HIGH  
**Collision:** all represent "work" at different semantic stages.

**Required flow:**

```text
Observation -> WorkItem -> governed promotion/mission -> WORKS Work
```

Observation or WorkItem existence never grants execution authority.

### CR-017 — Cron/proactivity signal vs execution authority

**Severity:** HIGH  
**Collision:** a scheduled detector can be mistaken for an autonomous executor.

**Required boundary:** `aftergraph-cron-fabric` senses/deduplicates/escalates. A signal may create a candidate; consequential execution still requires the canonical authority/admission/runtime/execution path.

### CR-018 — Skill/model availability vs permission

**Severity:** CRITICAL  
**Collision:** installing a skill, model, plugin or provider can appear to grant a capability.

**Required rule:** availability is inventory, never authority.

```text
Executable action = semantic capability
                  ∩ current authority
                  ∩ Trust admission
                  ∩ eligible implementation
                  ∩ budget/resource bounds
```

### CR-019 — Model Registry truth vs Runtime selection vs Trust policy

**Severity:** HIGH  
**Collision:** Registry may rank a model best while policy forbids it for the mission/tenant/data class.

**Required boundary:** registry describes promoted model identity/evidence; Runtime selects only from Trust/AIE-admissible candidates.

### CR-020 — Search/Brain/memory vs current authority/world truth

**Severity:** HIGH  
**Collision:** old decisions and organizational memory are useful context but can be mistaken for current policy or observed world state.

**Required rule:** memory and search results are provenance-bearing context only; current authority, admission and exact-subject truth are resolved from canonical owners.

### CR-021 — Human takeover vs running agent/lease

**Severity:** HIGH  
**Collision:** UI takeover without execution quiescence creates concurrent human/agent side effects.

**Required transition:**

```text
RUNNING -> SUSPENDING -> QUIESCED -> HUMAN_CONTROLLED
```

Consequential ownership/lease transfer must be explicit; takeover is not merely a presentation flag.

### CR-022 — Graceful degradation vs fail-closed consequential behavior

**Severity:** CRITICAL  
**Collision:** normal availability engineering can accidentally weaken governance.

**Required behavior examples:**

- verifier unavailable -> `VERIFICATION_UNAVAILABLE`, never `VERIFIED`;
- Trust unavailable -> consequential action denied/blocked;
- stale authority -> re-evaluate or stop;
- projection unavailable -> canonical owner remains truth;
- preferred provider unavailable -> fallback only if authority envelope is equal-or-narrower.

### CR-023 — Public API/BFF vs internal polyrepo contracts

**Severity:** HIGH  
**Collision:** exposing WORKS/Runtime/Trust native schemas directly makes private implementation contracts de facto permanent public product contracts.

**Required boundary:** public APIs expose stable product semantics; BFF/adapters translate to internal owners while preserving canonical identifiers and status meaning.

### CR-024 — Documentation drift as runtime risk

**Severity:** HIGH  
**Collision:** agents and humans use documentation as executable context. Stale documentation can route work through superseded ownership or versions.

**Required gate:** architecture/contract/version documentation referenced by automation must carry freshness/provenance and fail or warn visibly when incompatible with exact-head machine truth.

## 5. Current convergence gaps observed from canonical artifacts

These are gaps to test, not claims of implementation failure.

1. `golden-mission/0.1` is an experimental skeleton. Its success participant list contains Studio, Trust Gateway, Runtime and WORKS, while the V4 normative lifecycle also includes Authority and independent Verification. The build request states that verifier participation remains independent. A future Golden Mission revision should make all required seams and observer/projection participants explicit without inserting Relay as a new execution owner.
2. `dependencies.yml` correctly registers Relay as consuming AIE, Trust, Runtime, WORKS, Sentinel and Continuity, but its `mission-dag` and `continuity-capsules` provided surfaces are collision-sensitive and require explicit projection/orchestration boundaries against WORKS and `context-continuity`.
3. Studio currently consumes AIE, Trust Gateway and WORKS directly in the dependency projection. Before a public SaaS path is frozen, define which writes are BFF/delegated owner calls versus experience-local projection so Studio cannot become an alternative authority/execution plane.
4. AIE, Trust Gateway and WORKS all carry budget-related primitives. The platform needs one end-to-end budget lineage/reservation test across fallback and retry before paid autonomous execution is considered integrated.
5. `platform-event-ref/0.1` and `capability-action/0.1` remain experimental by design; Relay's richer governed event fabric must compose with them rather than silently supersede their correlation-only and authority-preserving constraints.
6. The 2026-09-10 convergence evidence explicitly reports that the live exact-head cross-service Golden Mission had not yet been executed; simulated fault containment is evidence, but not L3/L4 live composed proof.

## 6. Golden Mission VNext target

The next platform proof SHOULD use one exact-subject software mission because it currently has the strongest independent verifier path.

Example user intent:

> Fix a bounded GitHub issue, satisfy the declared acceptance criteria, and merge only if independent verification passes, within the mission budget.

Canonical consequential path:

```text
Studio intent
  -> AIE mission/principal/authority
  -> Trust action-time admission
  -> Runtime attempt/provider selection
  -> WORKS durable Work/lease/effect/evidence
  -> Sentinel exact-subject verification
  -> Verified Outcome projection to Studio + Relay
```

Relay participates as operator/control projection and human-intervention surface across the path, not as an additional authority/execution/verifier owner.

Required adversarial branches:

1. success;
2. explicit refusal / insufficient authority;
3. revocation after continuity/checkpoint creation;
4. mission budget exhaustion across retry/fallback;
5. provider crash and authority-preserving fallback;
6. duplicate/non-idempotent effect replay attempt;
7. human takeover during active execution;
8. principal/action/correlation drift;
9. evidence mismatch;
10. verifier unavailable;
11. stale exact subject after execution but before verification;
12. Trust unavailable during a consequential action.

## 7. Promotion gate

Do not describe the platform as fully integrated until an exact-head composed run proves at minimum:

- one canonical identity/correlation lineage survives every consequential seam;
- no projection becomes domain truth;
- Runtime fallback does not widen authority;
- revocation survives restart/continuity/provider migration;
- retries do not duplicate an irreversible effect;
- mission budget survives retries/fallbacks without reset;
- executor completion remains distinct from independent verification;
- verifier outage cannot produce a verified state;
- human takeover has a real quiescence/lease boundary;
- Studio and Relay show the same canonical mission/action/approval/evidence identifiers;
- evidence is reconstructible from native domain sources, not only from a UI/event projection.

## 8. Implementation order

1. Freeze the Mission / Work / Attempt / Session / Action identity mapping in Governance using existing contract families; do not invent another identity protocol.
2. Amend Golden Mission VNext to include the full V4 consequential seam set plus Relay as a projection/control participant.
3. Add collision vectors for revocation+continuity, budget+retry, provider-tool bypass, duplicate effects and takeover race.
4. Prove adapters on exact heads: AIE -> Trust -> Runtime -> WORKS -> verifier.
5. Add Studio + Relay projection consistency checks.
6. Run the composed success path.
7. Run adversarial branches and preserve negative results.
8. Only then promote platform integration maturity.

## 9. Non-goals

This register does not:

- create a new top-level plane;
- declare Relay, Studio, Runtime, WORKS or Governance a universal coordinator;
- create a universal event store;
- create another identity protocol;
- turn Continuity into durable execution truth;
- make Sentinel a universal verifier outside registered domains;
- claim live platform integration that has not been executed;
- upgrade contract tests, simulated campaigns or UI presence into production/scientific evidence.
