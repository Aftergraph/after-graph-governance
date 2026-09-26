# Build request: Golden Mission VNext live seam

**Status:** proposed implementation request

## Goal

Prove one real exact-head Aftergraph mission across the canonical V4 seams without creating a new platform owner or protocol.

Use a bounded software-change fixture and a deterministic/local Runtime implementation for the baseline. Add managed providers only after the baseline passes.

## Canonical path

```text
Studio intent/projection
  -> AIE authority
  -> Trust Gateway action-time admission
  -> Runtime execution attempt
  -> WORKS durable Work / effect / evidence
  -> Sentinel exact-subject verification
  -> Verified Outcome projection to Studio + Relay
```

Relay participates as operator/control projection across the path. It is not an additional authority, execution or verification owner.

## Existing contracts to reuse

Do not invent another identity/event protocol. Reuse the applicable existing families:

- `principal/1.0`
- `tenant/1.0`
- `execution-context/1.0`
- `correlation/1.0`
- `platform-event-ref/0.1` where an event projection is needed
- `capability-action/0.1` where semantic implementation choice is exercised
- `evidence.schema/1.1`
- `kernel.budget/1.0`
- `golden-mission/0.1` as the current runner lineage

## Baseline acceptance

The success run must prove:

1. canonical mission/principal/action identity survives every consequential seam;
2. Trust admission is bound to the exact consequential action;
3. Runtime performs an attempt without becoming durable Work truth;
4. WORKS preserves durable state/effect/evidence across Runtime restart;
5. effect replay cannot duplicate the committed side effect;
6. executor completion cannot produce `VERIFIED`;
7. Sentinel verifies the exact resulting commit and stale mutation invalidates the verdict;
8. Studio and Relay project the same canonical mission/action/approval/evidence identifiers;
9. evidence can be reconstructed from native domain owners rather than only from UI/event projection.

## Required adversarial branches

Run each independently and preserve negative results:

- principal/action identity drift -> fail closed;
- revocation after checkpoint/continuity material exists -> resumed consequential action denied;
- budget exhaustion before retry/fallback -> hard stop;
- crash after effect commit but before acknowledgement -> no duplicate effect;
- verifier unavailable -> execution may complete, outcome remains unverified;
- subject mutation after execution -> stale/invalidate;
- human takeover while active -> quiesce before control transfer;
- Relay/Studio projection mismatch -> canonical domain owner wins;
- fallback requiring broader authority -> fallback rejected.

## Baseline implementation choice

Use a deterministic/local Runtime implementation first. Do not make the first composed proof depend on a new external provider, provider-native tool path, or unmerged credential-surrogation behavior.

After this baseline passes, add OpenAI Agents API as a second Runtime implementation and prove that changing provider does not change mission, authority, budget, WORKS or verification semantics.

## Ownership

- Governance: contract registration and proof requirements only.
- AIE: authority/delegation/budget semantics.
- Trust Gateway: action-time admission/enforcement.
- Runtime: attempt lifecycle and implementation/provider selection.
- WORKS: durable Work, lease, effect and execution evidence.
- Sentinel: exact-subject software verification.
- Studio: primary user projection.
- Relay: operator/control projection and human intervention.

## Completion gate

This request is complete only when an exact-head composed run and its adversarial branches have machine-readable evidence. Repo-local tests or the existing simulated scenario do not satisfy the live-composition claim.
