# Mission Continuity Program Overlay — Design

**Date:** 2026-09-14  
**Status:** Approved design for implementation planning; no runtime authority change  
**Scope owner:** `Aftergraph/after-graph-governance`  
**Parent program:** Portable Intelligence Infrastructure V1 / Governance #68  
**Depends on:** Platform Convergence V2.1, platform topology 2.0, collision-register work in PR #160, automated AGENTS work in PR #162  

## 1. Purpose

Aftergraph already has canonical repository topology, distributed ownership, Mission/authority/execution contracts, Runtime orchestration, WORKS durable execution, assurance systems and organization-state tooling. The missing capability is not another project-management system or control plane. The missing capability is a thin, machine-readable coordination overlay that answers:

```text
What program slice is active?
Which semantic seams may it touch?
Which invariants apply?
What dependencies block it?
Which agent/runtime currently claims a semantic write?
Would a proposed change PASS, WARN, BLOCK or remain UNKNOWN?
```

This design introduces a **Program Overlay** and a deterministic **Direction Compiler**. They project existing canonical truth; they do not replace it.

## 2. Non-goals

This design MUST NOT:

1. Create a second repository catalog. `docs/platform-topology/2.0.json` remains canonical for repo scope, role, lifecycle, ownership and `must_not_own`.
2. Create a second Mission store. Mission remains the governed objective and existing Mission contracts remain authoritative.
3. Create a second authority plane. AIE and Trust Gateway remain authoritative for authority and admission/enforcement.
4. Create a second durable-work engine. WORKS remains canonical for durable Work, worker leases, effects, evidence and recovery semantics.
5. Create a generic policy language. Initial compilation is deterministic Python over bounded schemas; if generic policy complexity emerges, use an established policy engine rather than inventing one.
6. Create a generic workflow engine or scheduler.
7. Treat GitHub labels, branches, issues or PRs as semantic truth. They are workflow projections.
8. Treat Telegram, Studio, Relay, AGENTS.md or generated dashboards as canonical truth. They are operator/agent projections.
9. Serialize unrelated work across the organization.
10. Standardize experimental runtime-binding or program-overlay schemas prematurely.

## 3. Governing semantic model

The existing identity/execution chain remains authoritative:

```text
Organization
→ Tenant
→ Principal
→ Authority Context
→ Mission
→ Execution Context
→ Work
→ Action
→ Evidence
→ Verified Outcome
```

Mission remains distinct from Work, Attempt, Session and Action. Runtime-native goals, tasks, sessions, workflows and threads are projections of a Mission or Work assignment; they are never canonical Mission truth.

The Program Overlay sits orthogonally to execution truth:

```text
Canonical platform truth
  topology + contracts + mission + authority + work + evidence
                │
                ▼
          Program Overlay
                │
                ▼
        Direction Compiler
                │
        PASS/WARN/BLOCK/UNKNOWN
                │
       projections / advisory gates
```

## 4. Program Overlay

A Program Overlay is a versioned, reviewable declaration of current directional intent. It references canonical objects and semantic seams without copying their state.

Initial experimental shape:

```yaml
schema: aftergraph-program/0.1
program_id: mission-continuity
parent_program: portable-intelligence-infrastructure-v1
objective: preserve a governed mission across runtime replacement through independent verification
status: active
active_slices:
  - MC-001
  - MC-002
touches:
  - repo: works-execution
    seam: seam://works/execution-context
    mode: core
  - repo: runtime
    seam: seam://runtime/runtime-binding
    mode: next
  - repo: studio
    seam: seam://studio/mission-projection
    mode: consumer
invariants:
  - runtime_completion != verification
  - revocation != recoverable_failure
  - budget_exhaustion != recoverable_failure
  - projection != canonical_truth
blocked_by:
  - contract: execution-context/1.0
success:
  - golden_mission_runtime_replacement
  - no_duplicate_effect
  - authority_lineage_preserved
  - independent_verification
```

The overlay MUST NOT duplicate permanent repo roles, ownership, current SHA, compatibility state or exact Git state.

## 5. Program slices

A slice is the smallest independently testable unit of program progress. Slices form a DAG, not a prose roadmap.

Initial Mission Continuity slices:

| Slice | Deliverable | Primary owner | Depends on |
|---|---|---|---|
| `MC-001` | Converged `execution-context/1.0` seam | WORKS + Governance | V2.1 contracts |
| `MC-002` | Experimental RuntimeBinding model | Runtime | MC-001 semantics |
| `MC-003` | Runtime adapter SPI + Hermes adapter | Runtime | MC-002 |
| `MC-004` | Mission-level supervision invariant + recovery ladder | Runtime | MC-002, MC-003 |
| `MC-005` | Effect-safe takeover / lost-ACK reconciliation proof | WORKS + Runtime | MC-001, MC-004 |
| `MC-006` | Golden Mission runtime replacement campaign | Continuum/ISR + domain owners | MC-005 |
| `MC-007` | Operator/Telegram projection | Relay/Cron/Studio | MC-004, MC-006 evidence |
| `MC-008` | Public adapter/conformance alpha | Governance + Runtime + ISR | MC-006 |

Multiple independent slices MAY be active concurrently if dependencies are satisfied and semantic write sets do not conflict.

## 6. Semantic seams

A semantic seam identifies a bounded meaning boundary, not a file glob.

Initial registry:

```text
seam://governance/platform-topology
seam://governance/correlation
seam://aie/authority-lease
seam://trust/action-admission
seam://works/execution-context
seam://works/effect-ledger
seam://runtime/runtime-binding
seam://runtime/mission-supervision
seam://continuity/context-transfer
seam://verification/code-review-verdict
seam://studio/mission-projection
seam://relay/operator-projection
seam://operations/cron-observation
```

Seams MUST resolve to canonical owners from topology/contracts. A seam registry is coordination metadata only; it grants no authority. Sentinel owns only the code-review verdict seam; general or domain outcome verification remains with the applicable independent domain verifier and MUST NOT be collapsed into a universal Sentinel-owned verdict seam.

## 7. Semantic claims

Agents and tasks coordinate through bounded claims:

```text
READ
WRITE
MIGRATE
VERIFY
OBSERVE
```

Initial compatibility rules:

- `WRITE + WRITE` on the same seam => conflict unless explicitly scoped to disjoint sub-resources proven by the compiler.
- `MIGRATE + WRITE` => conflict.
- `VERIFY + WRITE` => allowed only when verifier independence is preserved and the verifier cannot mutate the subject.
- `READ + WRITE` => allowed.
- `OBSERVE` cannot authorize or mutate.
- Expired claims cannot block work.
- Claims never substitute for AIE authority, Trust Gateway admission, Git branch protection, WORKS leases or human approvals.

A claim record SHOULD include:

```yaml
claim_id: clm_...
program_id: mission-continuity
slice_id: MC-002
seam: seam://runtime/runtime-binding
mode: WRITE
holder:
  principal_id: prn_...
  runtime_ref: codex:session:...
status: active
issued_at: ...
expires_at: ...
```

The first implementation MAY use file-backed fixtures and observed PR/task identity. Long-term active execution should prefer existing Work/WorkerLease semantics instead of a shadow lease service.

## 8. Direction Compiler

The Direction Compiler is a deterministic evaluator.

Inputs:

```text
Program Overlay
+ platform topology
+ contract registry
+ collision register
+ exact/observed org state
+ active semantic claims
+ optional ARI compatibility evidence
```

Output:

```json
{
  "decision": "PASS | WARN | BLOCK | UNKNOWN",
  "program_id": "mission-continuity",
  "slice_id": "MC-002",
  "reasons": [],
  "violated_invariants": [],
  "conflicting_claims": [],
  "unknowns": [],
  "evidence_refs": []
}
```

`UNKNOWN` is first-class. Missing or stale evidence MUST NOT be silently treated as PASS.

Initial compiler behavior MUST be bounded to high-confidence deterministic checks. It MUST NOT perform LLM-only policy decisions for blocking outcomes.

## 9. Invariant classes

### Structural

```text
S-01 one canonical owner per semantic concern
S-02 projection cannot become source of truth
S-03 program overlay may reference but not redefine topology ownership
```

### Authority

```text
A-01 RuntimeBinding grants no authority
A-02 consequential action requires live revalidation
A-03 semantic claim grants no execution authority
```

### Recovery

```text
R-01 revocation is containment, not retryable failure
R-02 budget exhaustion is containment, not retryable failure
R-03 irreversible/non-idempotent effects are never blindly replayed
R-04 recovery success requires measurable new progress or reconciled safe state
```

### Verification

```text
V-01 executor completion != verified outcome
V-02 verifier must evaluate the exact subject/evidence generation
V-03 stale evidence cannot promote a current head/outcome
V-04 independent verifier cannot be replaced by executor self-assertion
```

### Coordination

```text
C-01 conflicting WRITE claims cannot coexist
C-02 expired claims cannot block
C-03 OBSERVE cannot mutate
C-04 unrelated seams remain concurrently executable
```

## 10. RuntimeBinding boundary

RuntimeBinding is an experimental Runtime-owned primitive linking one Mission revision to one runtime-native object.

Proposed shape:

```yaml
runtime_binding:
  binding_id: rb_...
  mission_id: mis_...
  mission_revision: 7
  generation: 3
  prior_binding_id: rb_...
  runtime:
    family: hermes
    instance_id: hermes-vds-01
  native:
    kind: goal
    session_id: ...
    native_ref: ...
  role: executor
  capabilities:
    native_goal: true
    pause_resume: true
    persistent_state: true
    native_wait: true
    checkpoint_resume: false
    structured_progress: partial
  state:
    projection_status: running
    last_observed_at: ...
```

Rules:

1. RuntimeBinding carries no authority.
2. Runtime replacement creates a new generation; historical generations remain immutable/superseded.
3. Runtime-native `done`, `complete`, `success` or equivalent cannot write VERIFIED.
4. Assignment selects the runtime; Mission is not broadcast to every available runtime.
5. Capability synchronization is semantic; command parity is not required.
6. RuntimeBinding remains experimental until at least Hermes plus one framework runtime plus one durable-workflow runtime pass conformance.

## 11. Mission supervision

A Mission-level supervisor evaluates this invariant:

> Every ACTIVE Mission has at least one of: recent meaningful progress, active owned execution, durable wait, pending governed recovery, explicit blocker, or verification in progress.

If none exists, the Mission is unmanaged/stalled.

Recovery ladder:

```text
R0 observe
R1 native continuation
R2 reconstruct canonical checkpoint/context
R3 repair runtime/session
R4 replace runtime/provider
R5 specialist recovery
R6 human escalation
```

Every recovery attempt requires:

```text
authority check
budget check
effect-safety check
idempotency/reconcile check
recovery ownership/lease
runtime dispatch
acknowledgement
progress verification
```

Revocation and budget exhaustion hard-stop the ladder until a new governed decision exists.

## 12. Shadow mode first

The Program Overlay and Direction Compiler MUST launch in observation mode.

Phases:

```text
OBSERVE
→ WARN
→ SOFT BLOCK
→ HARD BLOCK
```

Initial shadow run: 14 days or sufficient event volume, whichever is longer to obtain useful labels.

Measure:

```text
true collisions caught
false positives
missed collisions
UNKNOWN rate
operator minutes
bootstrap latency
CI latency
claim churn
unrelated-work interference
```

Hard blocking is permitted only for deterministic, high-precision invariants with measured evidence.

## 13. Agent context projection

The existing AGENTS generation pipeline remains the projection mechanism. Do not introduce a second `AGENT-BOOTSTRAP.md` system.

Generated context MAY add a concise program capsule:

```text
Active program: mission-continuity
Relevant slices: MC-001, MC-002
Allowed seams: ...
Current conflicting writes: none
Hard invariants: V-01, R-01, R-02
Do not own: authority, verification truth
```

The capsule must be generated from canonical topology + Program Overlay + observed claims. It is advisory/projection state and may expire.

## 14. Telegram / operator projection

Telegram, Relay and Studio expose operator intent and decisions; they do not become Mission truth.

Desired operator requests include:

```text
What are we working on?
Continue all safe work.
Why is this blocked?
Use Codex instead.
Pause this slice.
Can I leave it unattended?
```

The operator plane should show meaningful progress, blocker, recovery, containment, verification and `Needs You` events. Raw heartbeat/log noise should remain debug-only.

Operator actions must resolve through Principal/authority/admission boundaries before consequential effects.

## 15. Golden Mission proof

The critical proof is:

```text
Human Goal
→ Mission revision
→ AIE authority
→ Trust Gateway admission
→ Runtime A binding
→ WORKS
→ external effect
→ Runtime A dies after effect but before durable acknowledgement
→ supervisor detects stalled/unmanaged state
→ reconcile external effect
→ Runtime B binding generation
→ same Mission / authority lineage / remaining budget / constraints
→ no duplicate effect
→ Evidence
→ independent verifier
→ VERIFIED
```

In parallel:

```text
Agent C attempts conflicting WRITE on same semantic seam → detected
Agent D works on unrelated Billing seam → unaffected
```

This demonstrates direction without global serialization.

## 16. Research and falsification

The implementation is not evidence of technical superiority. MISSION-Bench must compare:

```text
B0 native runtime only
B1 native runtime + ordinary glue
B2 RuntimeBinding
B3 RuntimeBinding + Mission Supervisor
B4 full authority/evidence/verification integration
```

Faults include at minimum:

```text
tool timeout
bad output
stale state
context loss
partial execution
environment change
verifier failure
model failure
revocation
budget exhaustion
runtime crash
supervisor crash
projection drift
stale mission revision
duplicate dispatch
lost ACK after external effect
provider/runtime replacement
network partition
clock skew
takeover race
verifier outage
revocation after checkpoint
budget exhaustion after retry
```

Primary metrics: VSR, FCR, CRR, recovery rate, unauthorized-action rate, evidence completeness, duplicate-effect rate, CPVO, control-plane tax, useful-action rate, retries and human minutes.

Kill/narrow condition: if a conventional baseline delivers equivalent verified success, containment and effect safety at lower complexity/cost and users prefer it, reduce or remove the overlay/supervisor layer.

## 17. Implementation prerequisites

Before behavioral implementation:

1. Reconcile active Governance PR #160 collision semantics against current main.
2. Reconcile PR #162 AGENTS/inventory automation against current main.
3. Confirm current status of ARI PRs #38/#39 so no second compatibility graph is created.
4. Confirm `execution-context/1.0` canonical implementation status in WORKS.
5. Confirm open Golden Mission / Runtime→WORKS→verifier seams and exact-head evidence.
6. Preserve all P0 security work; this program must not bypass runtime isolation, governed egress or credential handling gates.

## 18. First implementation boundary

The first code slice is intentionally narrow:

```text
Program Overlay schema + fixtures
Semantic seam registry
Claim compatibility evaluator
Direction Compiler in shadow mode
Tests
```

It does **not** implement RuntimeBinding, Mission Supervisor, Telegram actions or hard PR blocking.

Those follow only after the coordination layer proves useful and non-disruptive.

## 19. Public claim boundary

Until the cross-runtime Golden Mission is demonstrated on external runtimes and an independent implementation can pass conformance, public language must remain conservative:

> Aftergraph is experimenting with a portable institutional and assurance layer for long-running intelligent work across runtimes.

Do not claim an industry standard, novel universal goal system, or proven cross-runtime continuity before evidence supports it.
