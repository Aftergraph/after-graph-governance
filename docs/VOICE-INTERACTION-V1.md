# Voice Interaction V1 — Canonical Voice-Edge Binding

Status: Canonical for realtime voice edge seams.
Topology: `docs/platform-topology/2.0.json`.

**Design rationale:** V4 spec §§7.1/14 (rationale only; this document is
normative for the binding). Transcript and speaker semantics are inherited
from the Wave F binding in `docs/POCKET-SOURCE-V1.md`, not re-derived here.

Voice is a realtime edge of the Interaction Fabric. A voice session carries
observation and turns only: sessions carry no durable identity and no durable
state. Session/model identity is disposable and never reused as a durable
principal. Durable principal, interaction state, context, mission, consent
records, and evidence live outside sessions in Runtime/WORKS/consent-ledger-owned
stores and are referenced, never embedded.

Canonical boundary: voice sessions carry observation/turns only;
transcript != identity; speaker != principal (Wave F inheritance); continuity
moves correlation/provenance, never authority; a spoken command never counts
as permission to execute. Nothing here creates a new authority, service, or
owner.

| Seam | V4 owner | Binding |
| --- | --- | --- |
| Surface adapter | `studio` | The Studio surface experience (`InteractionSurface`, `Presence`, `AssistantProfile` as product/experience state, `HandoffCheckpoint` rendering) stays an adapter: a surface never counts as a separate identity, memory, or authority universe, and persona stays product/experience state. |
| Specialist surface adapter | `wi-frontend` | Where a voice surface applies, the `wi-frontend` specialist surface adapts turns under the same observation-only boundary. Unlike the `wi-backend`-owned Pocket provider path, voice turn orchestration lives in `runtime`. No new repo. |
| Session and turn orchestration | `runtime` | Runtime orchestrates disposable sessions and `InteractionTurn` records (`InteractionThread` continuity, turn/stop semantics, handoff emission). Live speech and durable mission execution are separate loops. |
| Turn/stop/barge-in | `runtime` | Stop/cancel semantics distinguish `STOP_SPEAKING`, `CANCEL_TURN`, `PAUSE_MISSION`, `CANCEL_MISSION`, `FREEZE_AUTONOMY` per §14. `STOP_SPEAKING`/`CANCEL_TURN` interrupt speech/turn only; mission-level signals take the governed consequential path. Barge-in defaults to speech/turn interruption and never ambiguously terminates consequential execution. |
| Session admission/egress | `trust-gateway` | Trust Gateway admits/enters and exits sessions and enforces grants at runtime. A spoken command never substitutes for a grant; consequential action still follows AIE -> Trust Gateway -> Runtime -> WORKS -> verification. |
| Durable work and effects | `works-execution` | WORKS (`works-execution`) owns durable work, effects, evidence, and quittance for voice-derived commitments. |
| Continuity | `runtime` | Cross-surface continuity moves `HandoffCheckpoint` records plus `platform-event-ref/0.1` correlation only: dedupe/correlation substrate, never authority transport and never a replacement for Trust Gateway audit entries, WORKS events, or verification evidence. |
| Consent and deletion | `works-execution` | Consent/purpose lineage is attached at intake and propagated to derivatives. Consent revocation or source deletion invalidates downstream use and recomputes derived state per provenance, without rewriting historical audit or evidence: content is withdrawn from reads under tombstone semantics while audit is retained. Consent records live in consent-ledger-owned stores, referenced by sessions, never embedded in them. |
| Injection containment | `runtime` | Prompt-injected content inside a transcript stays untrusted observation, never instruction. |

Device split: the seams above are device-independent and proven with
fixtures. Realtime raw-audio streaming behavior, live-capture quality/latency,
acoustic/sensor calibration, on-device capture behavior, and provider-API
streaming characterization are marked
`BLOCKED_ON_VOICE_DEVICE_API_EVIDENCE`; no such claim appears here, and no
realtime raw-audio claim is made without device/API evidence.

Muse supervision stays owned by Runtime PR #103; this document
duplicates none of its semantics and adds no supervision role.

Invariants (restated, not extended):

- Observation and turns are not authority; sessions never execute consequential
  work and never substitute for a principal.
- Transcripts never count as identity; speaker attribution never
  authenticates; spoken command never counts as permission.
- Surfaces stay adapters; persona stays product/experience state.
- Continuity moves correlation/provenance; authority is never moved.
- Revocation and deletion invalidate downstream use per provenance;
  audit is never rewritten.
- Fail closed on consequential ambiguity; barge-in never terminates
  consequential execution.
