# Aftergraph Platform Fabrics v0.1

**Status:** EXPERIMENTAL implementation slice  
**Date:** 2026-09-08  
**Owner:** `after-graph-governance` for registration/conformance vectors; runtime semantics remain with domain owners.

## Purpose

Aftergraph's seven-plane architecture is not expanded by this document. This slice adds cross-cutting contracts needed to prove composition across existing planes without creating new authority, execution, evidence, or transport owners.

The canonical consequential path remains:

```text
Intent / Experience
  -> Intelligence
  -> Authority (AIE)
  -> Trust (Trust Gateway)
  -> Runtime
  -> Execution (WORKS)
  -> Evidence
  -> Verification
  -> Verified Outcome
```

This slice addresses three concrete seam problems:

1. domain event envelopes are intentionally different, but need a common correlation projection;
2. model/runtime tool behavior needs a semantic intent layer that does not depend on provider-specific tool names;
3. repo-local green tests do not prove that causal identity survives a composed platform path.

## Fabric A: Event correlation

`platform-event-ref/0.1` is a correlation-only projection. It does **not** replace Trust Gateway audit entries, WORKS execution events, OpenTelemetry spans, or research evidence.

Required properties include:

- stable event identity;
- source and event type;
- subject reference;
- `correlation/1.0`-compatible identifiers;
- payload and integrity references;
- event classification.

The contract is strict. Arbitrary authority-bearing fields are rejected. Possessing a projected event never grants execution authority.

## Fabric B: Semantic capability action

`capability-action/0.1` separates semantic execution intent from concrete implementation:

```text
semantic capability
        |
        +--> native tool
        +--> MCP
        +--> Python
        +--> shell
        +--> browser/computer
        +--> database/workflow
```

The action carries an authority envelope, effect class, risk class, candidate implementations, selection preferences, and a verification requirement.

Normative experimental invariants in this slice:

1. an implementation MUST NOT widen the semantic action's required authority;
2. consequential/external effects MUST require verification;
3. implementation identity MUST remain distinct from semantic capability identity;
4. the contract MUST NOT replace MCP, A2A, Trust Gateway capability policy, or AIE authority semantics;
5. provider/runtime selection remains a Runtime responsibility.

The existing `capability/1.0` contract remains untouched. It is the governed Trust Gateway role-to-tool capability vocabulary. `capability-action/0.1` is a different axis: semantic execution intent over one or more eligible implementations.

## Fabric C: Phase-0 platform conformance

`docs/platform-conformance/v0.1/vectors.json` introduces machine-executable vectors covering:

- valid event projection;
- missing causal action identity;
- attempted authority injection into the event projection;
- valid semantic implementation alternatives;
- implementation authority widening;
- consequential execution without verification;
- canonical identifier preservation across Studio/AIE/TG/Runtime/WORKS/verification projections;
- principal drift across a consequential seam.

`scripts/test_platform_fabrics_v0_1.py` executes the vectors using the Python standard library only. The corresponding GitHub Actions workflow is `.github/workflows/platform-fabrics.yml`.

Passing this suite means **contract-level Phase-0 conformance only**.

```text
Contract conformance != runtime integration conformance
Repo verified        != platform verified
```

No production or scientific maturity claim is upgraded by these tests.

## Ownership

| Concern | Owner |
|---|---|
| Contract registration and cross-repo vector definitions | after-graph-governance |
| Authority semantics | AIE |
| Admission/enforcement/audit | Trust Gateway |
| Tool/harness/implementation selection | Runtime |
| Durable effects and execution state | WORKS |
| Independent verification | Sentinel/domain verifier |
| Scientific evaluation of tool/execution strategy | ISR + AFM research program |

## Promotion gates

`platform-event-ref/0.1` and `capability-action/0.1` MUST remain experimental until all applicable gates pass:

1. two independent domain adapters consume/produce the contract without semantic reinterpretation;
2. adverse vectors demonstrate fail-closed behavior;
3. exact-head integration evidence is recorded;
4. Runtime demonstrates implementation fallback without authority widening;
5. WORKS/TG causal evidence can be correlated without replacing either native event envelope;
6. a composed Golden Mission preserves canonical identity through consequential execution and independent verification;
7. cost/context overhead is measured rather than assumed negligible.

## Next implementation slices

The next slices are intentionally additive:

- TG adapter: native audit entry -> `platform-event-ref/0.1` projection;
- WORKS adapter: native execution event -> `platform-event-ref/0.1` projection;
- Runtime resolver: `capability-action/0.1` -> eligible implementation set, authority-preserving only;
- cross-repo Golden Mission runner using exact pinned repository heads;
- AFM/ISR observable execution-trajectory benchmark over semantic capabilities.

The fabrics are seams, not new planes. Their job is to make the existing architecture composable and falsifiable, not to become another platform inside the platform.
