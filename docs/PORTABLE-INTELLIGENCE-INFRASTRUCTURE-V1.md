# Portable Intelligence Infrastructure V1

Status: PROGRAM DRAFT
Umbrella: #68
Evidence cut: platform-topology/2.0 (2026-09-08), org-state generated 2026-09-09T00:19:36Z

## Decision

Aftergraph will not optimize for becoming another vertically integrated personal-agent product. The platform direction is the portable infrastructure beneath persistent autonomous systems:

```text
human goal / client
        ↓
Studio / specialist experience
        ↓
AIE authority semantics
        ↓
Trust Gateway admission + enforcement
        ↓
Runtime orchestration + isolated execution
        ↓
WORKS durable execution + recovery + quittance
        ↓
independent verification
        ↓
verified outcome
```

External systems such as Meta Muse are treated as dated prior art and architecture comparators. Their existence supports the importance of the system-pressure problem; it does not establish AIE conformance, SPEC-001 empirical validity, or Aftergraph novelty.

## Program invariants

1. Model reasoning never grants authority.
2. Runtime execution never grants authority.
3. Authority semantics and runtime enforcement remain separate.
4. Runtime workers are replaceable; durable work truth is not.
5. Execution completion never upgrades itself to independent verification.
6. Secrets should not be exposed to agent reasoning when a brokered/surrogate form can be used.
7. Consequential egress is a governed action.
8. Human attention is exception-first: Goals, Progress, Needs You, takeover, verified outcome.
9. Cross-runtime portability is a design objective; vendor implementation details are not canonical semantics.
10. Research claims advance only when evidence advances.

## P0 execution wave

| Owner | Work item | Issue | Exit condition |
|---|---|---|---|
| Governance | Program coordination and boundary preservation | #68 | program map + cross-repo closure evidence |
| Trust Gateway | Credential surrogation + network egress admission | Aftergraph/trust-gateway#80 | secrets brokered after admission; replay/expiry/mismatch/unknown-egress tests green |
| Runtime | OS-isolated execution target + lineage hooks | Aftergraph/runtime#104 | isolation ADR + adversarial proof + enforced TG egress seam |
| AIE | Muse prior art + novelty boundary tightening | Aftergraph/aie#55 | claims narrowed to portable institution semantics/conformance where evidence supports them |
| ISR | Prior art + STUDY-011 evidence discipline | Aftergraph/intelligence-systems-research#49 | source/claim registries updated; no empirical overclaim |
| Studio | Goal/outcome-first human work loop | Aftergraph/studio#46 | Goals → Progress → Needs You → Artifact/Evidence → Verified Outcome flow |
| WORKS | Runtime→WORKS→verifier durable contract | Aftergraph/works-execution#68 | restart/revocation/budget/verifier integration tests green |
| Continuum | Failure-class vs injection-mode split | Aftergraph/continuum#13 | versioned taxonomy + mapping + reports distinguish stimulus from observed failure |
| Sentinel | Naming/confusion decision | Aftergraph/sentinel#7 | retain/rename decision + migration plan if required |

## P1 follow-through

### Data-flow provenance / taint
Canonical seam, not a new authority service:

```text
source provenance + sensitivity
        ↓
Runtime lineage metadata
        ↓
Trust Gateway egress policy input
        ↓
WORKS/audit/evidence correlation
```

AIE defines authority consequences only where the data classification changes legitimate action scope. Runtime carries lineage; TG enforces; WORKS preserves durable execution evidence.

### Skills supply chain
Self-created/generated skills are capabilities, never self-granted authority. `skills-vault` remains the provenance/trust/lifecycle/distribution owner. Generated capabilities must enter the same quarantine/candidate/stable lifecycle as human-authored ones before privileged use unless a narrowly scoped ephemeral policy explicitly permits them.

### Context continuity
`context-continuity` continues to own portable state transfer across model/agent/session/runtime boundaries. It must not become memory, authority, durable work truth or verification. The program should use ACC handshakes for runtime/model replacement experiments where continuity is material.

### Cron fabric
`aftergraph-cron-fabric` remains read-only scheduled observation. Execution schedules/triggers belong to Runtime/WORKS. No program requirement grants Cron Fabric new execution authority.

### Models
`llm-research-development`, `afm`, and `model-registry` remain model methodology/program/lifecycle concerns. Persistent-agent product capability must not depend on one model family. Model promotion evidence remains separate from runtime/institution conformance.

## Complete topology disposition

| Repository | Program disposition |
|---|---|
| after-graph-governance | ACTIVE: umbrella, contracts, boundaries, exact-head reconciliation |
| aie | ACTIVE P0: portable authority/delegation novelty boundary + prior art |
| trust-gateway | ACTIVE P0: credential surrogation, egress admission, enforcement |
| runtime | ACTIVE P0: isolation target, orchestration, lineage |
| works-execution | ACTIVE P0: durable execution/recovery/evidence/settlement seam |
| studio | ACTIVE P0: primary goal/outcome human operating surface |
| wi-backend | PRESERVE: source-neutral work intelligence; integrate only via contracts |
| wi-frontend | PRESERVE: specialist experience; consume canonical goal/work state when available |
| context-continuity | ACTIVE P1: cross-runtime handoff/continuity experiments |
| continuum | ACTIVE P0: assurance taxonomy + containment/continuity campaigns |
| sentinel | ACTIVE P0: independent code verification + naming decision |
| sentinel-firetest | TEMPORARY: no permanent responsibility |
| intelligence-systems-research | ACTIVE P0: prior art, claim audit, STUDY-011 |
| skills-vault | ACTIVE P1: generated/self-authored skill supply-chain governance |
| llm-research-development | PRESERVE: reusable model R&D methodology |
| afm | PRESERVE: Aftergraph model program |
| model-registry | PRESERVE: promoted model lifecycle truth |
| autonomous-venture-company | MIGRATION SOURCE: extract remaining Hermes/persistent-agent behavior; no new canonical platform ownership |
| aftergraph-cron-fabric | PRESERVE: read-only scheduled sensing/escalation |
| veranza | HOLD: no production/public responsibility from this program |
| docs | FOLLOW: render canonical program/contracts after source merges |
| aftergraph.org | FOLLOW: positioning after architecture evidence lands; do not overclaim maturity |
| brand | FOLLOW: product naming after Sentinel decision; no irreversible rename by implication |
| .github | FOLLOW: community/process defaults only |

## Security architecture target

A persistent autonomous worker should be treated as potentially compromised.

Desired abstract boundary:

```text
Agent/Model
   │ opaque capability + credential handles only
   ▼
Runtime isolated worker
   │ proposed consequential action / egress
   ▼
Trust Gateway
   │ resolve AIE authority + policy + approval + freshness
   ▼
Privileged broker / executor
   │ inject real credential only at boundary
   ▼
External system

WORKS records durable execution/evidence.
Independent verifier decides verified outcome.
```

The contract is canonical; Linux namespaces, containers, VM isolation, eBPF or other mechanisms are implementation choices subject to platform support and threat-model evidence.

## Human experience target

Studio should make delegated work legible without requiring constant supervision:

```text
Goal
├── desired outcome
├── budget/risk projection
├── plan/workstreams
├── active agents/work
├── progress
├── Needs You
│   ├── approval
│   ├── clarification
│   ├── credential/connect
│   ├── budget decision
│   ├── policy conflict
│   └── external blocker
├── artifacts/evidence
└── outcome
    ├── declared complete
    ├── execution complete
    ├── verification pending
    └── verified
```

Chat remains an interaction stream, not durable execution truth.

## Research posture

Allowed claim:

> Contemporary autonomous-agent products independently converge on persistent execution, externalized control, scoped permissions, durable state, human approval and containment, strengthening the case that these are real systems-engineering pressure points.

Not allowed without further evidence:

> A vendor product validates AIE, SPEC-001 empirical metrics, MISSION-Bench results, or Aftergraph priority/novelty.

STUDY-008 remains audit-demoted. STUDY-011 remains the live cross-provider confirmatory gate.

## Program exit gate

V1 closes only when:

- P0 issues above are resolved with evidence on exact heads;
- Governance records the final cross-repo contracts and any version bumps;
- Studio demonstrates the full goal→verified-outcome flow against canonical upstreams, not local mocks alone;
- Runtime/TG isolation+egress architecture has adversarial proof;
- WORKS demonstrates restart/revocation/budget behavior across the integration seam;
- no execution surface can self-issue independent verification;
- ISR/AIE claim registries reflect the updated prior-art landscape;
- public docs/site state the achieved maturity, not the intended architecture.
