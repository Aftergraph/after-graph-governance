# Studio request — interaction-turn/0.1

Owner: `Aftergraph/studio`.

Implement the user-facing adapter for Runtime-owned `interaction-turn/0.1`. Studio submits turns and renders Runtime event projections but never persists canonical InteractionThread/InteractionTurn truth in its experience store.

Studio keeps Projects, Recents, layout, surface state, and typed references. It must support thread open, turn submit, ordered streaming activity, reconnect/resync, cancel-turn, handoff presentation, and explicit degraded/unavailable states.

Acceptance: exact Runtime adapter contract; tenant binding remains external; local reference conversations cannot masquerade as Runtime truth; reconnect from cursor is deterministic; missing history triggers resync; tool/decision/artifact payloads remain typed references to canonical owners.
