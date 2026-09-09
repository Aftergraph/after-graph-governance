# Build request: Voice edge (Interaction Fabric edge)

Owner: `Aftergraph/studio` — surface experience owner; `Aftergraph/wi-frontend` — specialist adapter owner; `Aftergraph/runtime` — edge session + turn orchestration owner; durable owners: `trust-gateway` admission, `works-execution` durable execution, and consent-ledger-owned stores for durable consent
Contract: `voice-interaction/0.1` (`docs/contracts/voice-interaction/0.1.json` in after-graph-governance; versioned successors keep the `voice-interaction/0.x` lineage)
Seam binding: `docs/VOICE-INTERACTION-V1.md` in after-graph-governance
Acceptance vectors: `VOI-001`, `VOI-002`, `VOI-003`, `VOI-004`, `VOI-005`, `VOI-006`, `VOI-007`, `VOI-010`, `VOI-011`, `VOI-012`, `VOI-013`, `VOI-014`, `VOI-015`, `VOI-016`, `VOI-017`, `VOI-020`, `VOI-021`, `VOI-022`, `VOI-023`, `VOI-024`, `VOI-025`, `VOI-026`, `VOI-027`

## What to build

- In `Aftergraph/studio`, build the surface experience: voice surface rendering, turn/stop/barge-in controls, and handoff presentation per section 14, with no durable identity/state held in the surface.
- In `Aftergraph/wi-frontend`, build the specialist adapter: map voice turns into structured specialist input and render specialist output back into voice turns, preserving consent/purpose lineage on every turn.
- In `Aftergraph/runtime`, build edge session + turn orchestration: ephemeral voice sessions carrying correlation IDs and provenance only, turn/stop/barge-in semantics per section 14, `HandoffCheckpoint` + `platform-event-ref/0.1` continuity.
- Admit every session through `trust-gateway` admission and enforce egress there; nothing voice-originated crosses the boundary unadmitted.
- Execute all durable effects in `works-execution` durable execution only; sessions never execute authoritatively themselves.
- Hold durable consent, revocation, and deletion state in consent-ledger-owned stores only; consent revocation and deletion invalidate downstream use per provenance without rewriting audit.
- Forbid voice authority-conflation phrases (session-as-identity/state/authority, handoff-as-grant, transcript-as-identity, speaker-as-principal, spoken-command-as-permission, correlation-as-authority, surface-as-authority-universe, persona-as-authority).

## Canonical boundary

Voice is the Interaction Fabric edge. Sessions carry no durable identity and no durable state in sessions: all durable identity/state lives outside in Runtime/WORKS/consent-ledger-owned stores. Continuity runs via correlation/provenance with never moved authority — correlation never transports authority. transcript != identity and speaker != principal as Wave F inheritance, not re-derived. The canonical boundary sits at Trust Gateway session admission/egress through Trust Gateway: nothing voice-originated crosses it unadmitted.

## Acceptance

- `VOI-001`: gated acceptance
- `VOI-002`: gated acceptance
- `VOI-003`: gated acceptance
- `VOI-004`: gated acceptance
- `VOI-005`: gated acceptance
- `VOI-006`: gated acceptance
- `VOI-007`: gated acceptance
- `VOI-010`: gated acceptance
- `VOI-011`: gated acceptance
- `VOI-012`: gated acceptance
- `VOI-013`: gated acceptance
- `VOI-014`: gated acceptance
- `VOI-015`: gated acceptance
- `VOI-016`: gated acceptance
- `VOI-017`: gated acceptance
- `VOI-020`: gated acceptance
- `VOI-021`: gated acceptance
- `VOI-022`: gated acceptance
- `VOI-023`: gated acceptance
- `VOI-024`: gated acceptance
- `VOI-025`: gated acceptance
- `VOI-026`: gated acceptance
- `VOI-027`: gated acceptance

## Out of scope

Governance registers the contract and pins acceptance only. Governance implements nothing in `Aftergraph/studio`; the canonical surface behavior belongs to the studio owners, proven by the owner repo's own tests, PR, CI, merge queue, and exact-head evidence. Governance implements nothing in `Aftergraph/wi-frontend`; the canonical adapter behavior belongs to the wi-frontend owners, proven by the owner repo's own tests, PR, CI, merge queue, and exact-head evidence. Governance implements nothing in `Aftergraph/runtime`; the canonical edge session and turn orchestration belongs to the runtime owners, proven by the owner repo's own tests, PR, CI, merge queue, and exact-head evidence.

## Evidence-gated appendix: realtime streaming and device/API characterization

The following realtime raw-audio streaming and device/API characterization items are explicitly marked `BLOCKED_ON_VOICE_DEVICE_API_EVIDENCE` pending device/API evidence. No acceptance is claimed for them here.

- realtime raw-audio streaming characterization — `BLOCKED_ON_VOICE_DEVICE_API_EVIDENCE`
- device audio-capture characterization — `BLOCKED_ON_VOICE_DEVICE_API_EVIDENCE`
- microphone-array characterization — `BLOCKED_ON_VOICE_DEVICE_API_EVIDENCE`
- voice device-API characterization — `BLOCKED_ON_VOICE_DEVICE_API_EVIDENCE`
