# Runtime request — interaction-turn/0.1

Owner: `Aftergraph/runtime`.

Implement canonical InteractionThread lifecycle and InteractionTurn orchestration for `interaction-turn/0.1`. Provide idempotent thread-open/turn-submit/cancel/close operations plus an ordered event stream with sequence/cursor reconnect semantics.

Runtime must mint/own canonical thread and turn references, preserve tenant/principal/admission/trace lineage, keep canonical domain payloads by reference, and never treat surface possession as authority.

Acceptance: contract fixtures pass; duplicate submits do not duplicate turns; event sequence is monotonic; stale cursor produces explicit resync; cancellation does not cancel mission/work execution; handoff requires destination readmission; restart preserves thread/turn continuity.
