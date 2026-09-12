# Aftergraph Interaction Turn v0.1 Cross-Repo Plan

## Goal

Materialize the missing surface-neutral Interaction Fabric seam before Studio and Runtime implement a production text/chat adapter.

Canonical ownership remains unchanged:
- Studio owns surface experience and AssistantProfile presentation.
- Runtime owns InteractionThread continuity and InteractionTurn orchestration.
- Trust Gateway owns admission and consequential grant enforcement.
- ACC owns cross-runtime actionable-state transfer handshakes.
- WORKS owns durable consequential work/effects.
- Sentinel owns independent verification.

The new contract must not create a new authority, execution, memory, or evidence owner.

## Contract choice

Register `interaction-turn/0.1` as the surface-neutral turn protocol. It is not a chat-message database schema. It covers turn submission, ordered runtime events, turn cancellation, and cross-surface checkpoint references.

## Task 1 — Governance contract

Create `docs/contracts/interaction-turn/0.1.json` plus a dedicated stdlib conformance sensor. The schema must stay surface-neutral, carry cross-plane state by reference, preserve causal identifiers, and fail closed on unknown fields.

Required operations are `thread_open`, `turn_submit`, `turn_event`, `turn_cancel`, `handoff_checkpoint`, and `thread_close`. Runtime events use monotonic sequence and cursor values. Consequential effects require an external grant reference. Handoff never transports authority.

Gate: the dedicated interaction-turn sensor and the existing Platform Fabrics suite both pass.

## Task 2 — Runtime owner implementation

Implement the owner seam in `Aftergraph/runtime` from the registered contract. Runtime mints canonical thread and turn references, persists continuity across restart, provides idempotent submit/cancel/close operations, and exposes ordered event replay with explicit resync when retained history is insufficient.

Turn cancellation must not implicitly cancel WORKS missions or other consequential execution. Voice remains a specialized adapter over the same Interaction lineage.

## Task 3 — Studio adapter implementation

Implement the experience adapter in `Aftergraph/studio` only after the Runtime owner seam is available. Studio opens/submits/cancels through Runtime, renders ordered activity and artifacts, stores only experience metadata plus typed canonical refs, and handles reconnect/resync explicitly.

The existing `reference-local` conversation path remains non-authoritative until migration or retirement is separately proven.

## Exit gates

- Governance contract and binding committed from an exact-head baseline.
- Runtime behavioral tests cover duplicate submit, restart, cursor replay/resync, tenant isolation, cancellation semantics, and handoff readmission.
- Studio behavioral tests cover the real Runtime adapter, streaming projections, degraded/unavailable states, reconnect/resync, and no canonical thread/turn persistence.
- Each owner repo passes its repository-native full verification before cross-repo composition is claimed.
- Cross-repo composition evidence binds exact SHAs. Local green output alone is not platform conformance.
