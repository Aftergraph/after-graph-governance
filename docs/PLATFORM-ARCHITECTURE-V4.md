# Aftergraph Platform Architecture V4

**Status:** Canonical
**Supersedes:** [PLATFORM-ARCHITECTURE-V3.md](PLATFORM-ARCHITECTURE-V3.md) (retained for historical provenance)
**Date:** 2026-09-08
**Owner:** Aftergraph portfolio control
**Design rationale:** `docs/superpowers/specs/2026-09-08-aftergraph-platform-architecture-v4-and-platform-fabrics-v1-design.md`

V4 is the current normative platform architecture: seven permanent semantic
planes, eight cross-cutting Platform Fabrics, and one machine-validated
repository truth in `docs/platform-topology/2.0.json`. This document states
ownership and law concisely; the approved design spec carries full rationale,
red-team analysis and delivery waves.

---

## 1. The seven permanent planes

| Plane | Canonical owner | Owns | Must not own |
|---|---|---|---|
| Intelligence | `wi-backend` | source-neutral observations → canonical commitments and WorkItems | authority, admission, orchestration, durable execution, verification |
| Authority | `aie` | principals, delegation, mission authority, budgets, revocation semantics | enforcement, sessions/secrets, execution, durable state, verification |
| Trust | `trust-gateway` | runtime identity/session binding, tenant isolation, admission, approvals, consent enforcement | authority semantics, mission planning, durable work, verification |
| Runtime | `runtime` | agent lifecycle, orchestration, dispatch, checkpoints, metering, rebuildable World State projection | authority truth, enforcement truth, durable execution, verification |
| Execution | `works-execution` | durable WorkGraph, leases, workers, retries, evidence, quittance, Company Brain | agent persona, authority semantics, admission, verification |
| Verification | `sentinel` (+ registered domain verifiers) | exact-subject verification, stale invalidation, evidence-backed verdicts | execution of the work it verifies |
| Experience | `studio` (primary), `wi-frontend` (specialist) | general-purpose Chat/Work/Space experience; specialist Wie surface/BFF | tenant binding, authority, execution, verification or world truth |

Normative lifecycle:

```text
Intent / Experience -> Intelligence -> Authority -> Trust -> Runtime
  -> Execution -> Evidence -> Verification -> Verified Outcome
```

Runtime orchestrates agent operation inside that architecture but never widens
AIE authority, bypasses Trust Gateway admission, replaces WORKS durable
execution, or self-issues an independent verification verdict.

## 2. The eight Platform Fabrics

Fabrics compose concerns across planes. A Fabric never becomes a new plane, a
new authority, or a new source of execution, evidence or transport truth.

1. **Interaction** — Studio, Runtime, Trust Gateway composition for threads, turns and presence.
2. **Perception** — multi-tenant source ingestion (including Pocket via `wi-backend`) into observations.
3. **Context** — portable actionable state transfer (`context-continuity` handshake).
4. **World State** — rebuildable projection over provenance-bearing canonical sources; never writable truth.
5. **Proactivity** — attention pipeline (signal → candidate → Runtime decision → classified disclosure).
6. **Capability** — semantic execution intent separated from provider implementation (`aftergraph-cron-fabric` senses; `skills-vault` supplies).
7. **Agent Organization** — Runtime team topology, delegation and relay behavior.
8. **Verified Improvement** — immutable learning candidates promoted only with targeted, regression, safety and independent evidence.

## 3. Correlation substrate

`platform-event-ref/0.1` remains the correlation-only projection beneath the
Fabrics. It is not a ninth Fabric and never replaces Trust Gateway audit
entries, WORKS events, telemetry spans, Wie observations or verification
evidence. A causal-identity mismatch across authority, admission, attempt,
effect, evidence and verification is a platform verification failure.

## 4. Machine truth relation

`docs/platform-topology/2.0.json` is the slow-changing canonical
repository/ownership source: 24 repositories, `architecture_plane` (one of the
seven planes, or null for support systems) kept separate from the extensible
`system_class`, plus `role`, `lifecycle`, `owns` and `must_not_own` per
repository. Topology membership never upgrades maturity, evidence,
conformance or authority.

```text
platform-topology/2.0  = slow-changing repository/ownership truth
org-state/1.0          = fast-changing exact-head GitHub truth
```

`scripts/org-state-verify.sh` derives generation scope from topology/2.0 and
emits `org-state/1.0` snapshots (`latest-org-state.json`). Exact Git SHAs are
generated remote truth only and are never hand-authored into topology or
architecture files. `dependencies.yml` (`version: 4`) and the README topology
block are validated projections of the same source.

## 5. AVC dissolution rule

`autonomous-venture-company` is present only as `system_class =
legacy-transition`, `lifecycle = legacy-transition`, `role =
legacy-migration-source`: a migration source pending governed extraction. It
owns no new canonical Aftergraph responsibility. No new `@avc/*`, `avc-*`,
AVC contracts or AVC authority semantics may be created. Historical evidence
and migration provenance that reference AVC remain legitimate and are not
rewritten.

Target masterbrand is **Aftergraph**. `AVC`, `Autonomous Venture Company` and
`ABDE Intelligence` are not active platform/product brands.

## 6. Constitutional invariants

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
18. No new top-level plane is created unless existing ownership demonstrably cannot contain the concern.

## 7. Conformance ladder L0–L6

- **L0 REGISTERED** — owner, contract identity and lifecycle registered.
- **L1 CONTRACT-CONFORMANT** — schemas, invariants and adversarial contract vectors pass.
- **L2 ADAPTER-CONFORMANT** — real producer/consumer adapters preserve semantics without reinterpretation.
- **L3 COMPOSITION-CONFORMANT** — exact-head repositories preserve semantics and causal identity across a composed path.
- **L4 ADVERSARIAL-CONFORMANT** — failure, replay, revocation, crash/recovery, stale-state and isolation cases prove fail-closed or correct recovery.
- **L5 LIVE-CHARACTERIZED** — real-environment reliability, latency, cost and operational limits measured.
- **L6 SCIENTIFICALLY-SUPPORTED** — general performance claims backed by preregistered, reproducible research evidence.

Repository-local green tests establish Governance conformance only — never
full platform integration, runtime maturity or scientific validity. A Studio
reference surface can be L1/L2 while the platform capability stays below
L4/L5; UI presence never upgrades upstream maturity by implication.
