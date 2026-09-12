# Aftergraph Interaction Turn v0.1

`interaction-turn/0.1` is the surface-neutral Interaction Fabric contract for thread lifecycle and turn orchestration.

## Canonical ownership

- Studio owns InteractionSurface experience and AssistantProfile presentation.
- Runtime owns InteractionThread continuity and InteractionTurn orchestration.
- Trust Gateway owns admission and governed grants.
- ACC owns cross-runtime actionable-state handoff semantics.
- WORKS owns durable consequential work and effects.
- Sentinel owns independent verification.

A surface adapts this protocol. It does not become a separate identity, memory, execution, or authority universe.

## Protocol

The contract supports `thread_open`, `turn_submit`, ordered `turn_event`, `turn_cancel`, `handoff_checkpoint`, and `thread_close`. Canonical payloads from other planes are carried by references. Runtime events use per-turn sequence/cursor fields so clients can reconnect without inventing missing history.

Turn cancellation ends a turn only. Mission/work cancellation remains on the existing governed path. Cross-surface handoff carries checkpoint/correlation references and requires destination re-admission.

`voice-interaction/0.1` remains the specialized realtime voice adapter. It composes with this lineage rather than replacing the general surface-neutral protocol.
