# Aftergraph Platform Architecture V4 — Wave G Interaction (Voice Edge + Cross-Surface Continuity) Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development —
> fresh implementer per task, spec-compliance review first, code-quality review
> second, both must pass before the next task.

## 0. Scope (read first)

Wave G is **interaction (realtime voice edge + cross-surface continuity)** per the approved V4 design spec
(`docs/superpowers/specs/2026-09-08-aftergraph-platform-architecture-v4-and-platform-fabrics-v1-design.md`,
§7.1 and §14 and §22 Wave G):

- generalize interaction/presence contracts (`InteractionSurface`, `InteractionThread`,
  `InteractionTurn`, `Presence`, `AssistantProfile`, `HandoffCheckpoint`);
- add a realtime voice edge as an Interaction Fabric adapter plus cross-surface continuity;
- keep durable identity/state outside realtime sessions.

Normative anchors (do not re-derive): Interaction Fabric §7.1 (surface is an
adapter, never a separate identity/memory/authority universe; persona is
product/experience state, not authority); realtime voice placement §14
(voice is an Interaction Fabric adapter, not the owner of identity, memory,
missions or authority; live speech and durable mission execution are separate
loops; `STOP_SPEAKING` / `CANCEL_TURN` / `PAUSE_MISSION` / `CANCEL_MISSION` /
`FREEZE_AUTONOMY` with barge-in defaulting to speech/turn interruption and never
ambiguously terminating consequential execution; voice session/model identity is
disposable; durable principal, interaction state, context, mission and evidence
remain Aftergraph state); Wave G §22 scope above; Wave F binding
(`docs/POCKET-SOURCE-V1.md`) for transcript/speaker semantics, inherited here,
not re-derived.

Canonical boundary (every task, no exceptions):

```text
Voice = Interaction Fabric edge whose sessions carry observation/turns only.
Session != authority; session != durable identity/state;
correlation/provenance != moved authority;
transcript != identity; speaker != principal (inherited Wave F binding).
Session admission/egress passes Trust Gateway; durable identity/state live
outside sessions in Runtime/WORKS/consent-ledger-owned stores.
```

Owner: Studio / `wi-frontend` / `runtime` as applicable. Governance pins
contracts/vectors/requests only and implements nothing in owner repos:

- `studio` — Studio surface experience (`InteractionSurface`, `Presence`,
  `AssistantProfile` as product/experience state, `HandoffCheckpoint` rendering);
- `wi-frontend` — specialist surface adapter where a voice surface applies;
- `runtime` — Realtime Voice Edge session and `InteractionTurn` orchestration
  (disposable session/model identity, turn/stop semantics, handoff emission);
- `trust-gateway` admits/enters and exits sessions and enforces grants at runtime;
- `works-execution` owns durable work, effects, evidence and quittance;
- consent-ledger-owned stores own durable consent records referenced (never
  embedded) by sessions.

No new repo. No `voice-platform`, `personal-ai`, `mega-brain`, or any other
top-level repository.

Plane/fabric mapping (fixed, do not reinterpret):

- Interaction Fabric edge = session/turn adapter (no durable identity/state,
  no authority, no execution ownership);
- Trust Gateway = session admission/egress + grant enforcement plane;
- Runtime/WORKS/consent-ledger-owned stores = durable identity/state/evidence owners;
- `platform-event-ref/0.1` + canonical causal identifiers = correlation-only
  substrate for cross-surface continuity (dedupe/correlation, never authority transport).

No realtime raw-audio streaming claims without device/API evidence. Any realtime
raw-audio streaming, live-capture quality/latency, acoustic-model, on-device, or
provider-API streaming characterization work is evidence-gated and marked
`BLOCKED_ON_VOICE_DEVICE_API_EVIDENCE` (Task 5 appendix); it is never proven
with mocks and never closes an evidence-independent gate.

This plan covers the **governance-owned** part: experimental contract(s),
acceptance vectors, the canonical voice-interaction binding, and crisp cross-repo
build request(s). Edge, surface, session, projection, and continuity
**implementation** lives in the owner repos above and is specified here as
follow-up request(s) with exact acceptance — never implemented from this repo.

Out of scope (do not touch):

- Wave H (promotion gates, model promotion);
- Wave I (AVC dissolution ledger execution, skill/Hermes migration, archival);
- Wave F re-derivation — transcript/speaker semantics are inherited from
  `docs/POCKET-SOURCE-V1.md`, never re-derived here;
- Runtime PR #103 Muse supervision — do NOT duplicate it here; if a task
  overlaps supervision semantics, it references PR #103 and stays out.

No new top-level services, planes, fabrics, repos, or ownership. No new
canonical AVC identifiers. Vector namespace `VOI-*` is a Wave G conformance
identifier, not a canonical platform ID.

Evidence-independent vs evidence-gated split (binding for all tasks below):

- Evidence-independent (prove now in governance + owner repos with fixtures):
  interaction contract, disposable session identity, Trust Gateway
  admission/egress, turn/stop/barge-in semantics, `HandoffCheckpoint` +
  correlation/provenance continuity without moving authority, consent/purpose
  lineage, revocation/deletion invalidation, prompt-injection containment,
  cross-surface contamination guards, fixtures, cross-repo requests, evidence record.
- Evidence-gated (marked `BLOCKED_ON_VOICE_DEVICE_API_EVIDENCE`, never gated as
  PASS here): realtime raw-audio streaming behavior, live-capture quality/latency
  claims, acoustic/sensor calibration, on-device capture behavior, provider-API
  streaming characterization.

## Global constraints (every task)

- TDD task-by-task: failing test first, prove RED, minimum change, GREEN,
  regression, inspect diff, small focused commit. No weakened tests.
- Spec review + quality review gates per task: spec-compliance review first,
  code-quality review second; both must pass before the next task. Reviews
  are recorded on the branch (review-note or sign-off lines in the commit).
- Merge-queue only. No direct-to-main pushes, no bypass.
- Canonical boundary holds in every vector, doc, and fixture: voice edge is an
  Interaction Fabric adapter; sessions carry no durable identity/state; durable
  identity/state live outside sessions in Runtime/WORKS/consent-ledger-owned
  stores; continuity moves correlation/provenance, never authority; transcript
  is not identity and speaker is not principal (Wave F inheritance).
- Session admission/egress passes Trust Gateway in every vector, doc, and fixture.
- New vector kinds extend the harness with their own tests; the oracle stays
  independent of implementation internals and fails closed.
- No realtime raw-audio streaming or device/API characterization claims without
  device/API evidence; evidence-gated items stay `BLOCKED_ON_VOICE_DEVICE_API_EVIDENCE`.
- Do not duplicate Runtime PR #103 Muse supervision semantics.
- Do not re-derive Wave F transcript/speaker semantics; inherit the binding.
- Repository-local green never claims cross-repo or platform conformance.

## Task 1 — voice-interaction/0.1 contract and acceptance vectors (session statelessness + admission)

Evidence-independent. Fixtures only; no device/API evidence.

- [ ] **Step 1: RED.** Failing tests for `VOI-001` (realtime session carrying
  only turn/observation content with durable identity/state referenced outside
  the session in Runtime/WORKS/consent-ledger-owned stores, accept), `VOI-002`
  (session embedding durable principal identity, reject), `VOI-003` (session
  embedding durable interaction/memory/mission state, reject), `VOI-004`
  (session admitted without Trust Gateway admission, reject), `VOI-005`
  (session egress/effect bypassing Trust Gateway grant enforcement, reject),
  `VOI-006` (transcript presented as principal identity, reject — inherited
  Wave F binding), `VOI-007` (speaker attribution presented as principal
  authentication, reject — inherited Wave F binding). Run → FAIL on missing
  contract/kind/vectors.
- [ ] **Step 2: GREEN.** Add `docs/contracts/voice-interaction/0.1.json`
  (experimental: `InteractionSurface`/`InteractionThread`/`InteractionTurn`
  refs, disposable session/model identity, Trust Gateway admission/egress refs,
  durable-store refs without embedding, tenant scoping, classification,
  inherited transcript/speaker non-identity), extend the conformance harness
  with a `voice_interaction` kind validator plus its own tests, add the seven
  vectors to `docs/platform-conformance/v0.1/vectors.json`, wire new contract
  paths into `.github/workflows/platform-fabrics.yml`. Add fixtures (synthetic
  session/turn/handoff payloads with outside-session durable refs; no real
  audio captures, no live streams). Re-run suite → PASS. Regression: fabrics
  suite, topology suite, exact-head suite.
- [ ] **Step 3: Commit** `feat(governance): pin voice-interaction acceptance`.
  Spec review + quality review recorded before the next task.

## Task 2 — realtime turn/stop semantics + session guards (evidence-independent)

Evidence-independent. Fixtures only; no device/API evidence.

- [ ] **Step 1: RED.** Failing tests for `VOI-010` (`InteractionTurn` mapped
  under a disposable session/model identity, accept), `VOI-011`
  (`STOP_SPEAKING`/`CANCEL_TURN` interrupting speech/turn only, accept),
  `VOI-012` (`PAUSE_MISSION`/`CANCEL_MISSION`/`FREEZE_AUTONOMY` requiring the
  governed consequential path rather than executing from the voice edge alone,
  accept), `VOI-013` (barge-in ambiguously terminating consequential execution,
  reject), `VOI-014` (spoken instruction self-executing as permission without
  AIE -> Trust Gateway -> Runtime -> WORKS -> verification, reject),
  `VOI-015` (voice-derived `CommitmentCandidate` routed through the governed
  consequential path, accept), `VOI-016` (voice session identity reused as a
  durable principal across sessions, reject), `VOI-017` (realtime raw-audio
  streaming claim without device/API evidence, reject-evidence-gated). Run →
  FAIL.
- [ ] **Step 2: GREEN.** Extend `docs/contracts/voice-interaction/0.1.json`
  (or a versioned `0.2.json` if breaking; prefer additive) with turn/stop/
  barge-in semantics, disposable-identity rules, and the governed consequential
  path; extend the `voice_interaction` harness validator plus its own tests;
  add the eight vectors; wire contract paths into CI. Suite → PASS.
  Regression: fabrics suite, topology suite, exact-head suite.
- [ ] **Step 3: Commit** `feat(governance): pin voice turn/session acceptance`.
  Spec review + quality review recorded before the next task.

## Task 3 — cross-surface continuity via correlation/provenance + consent/deletion (evidence-independent)

Evidence-independent. Fixtures only; no device/API evidence.

- [ ] **Step 1: RED.** Failing tests for `VOI-020` (cross-surface handoff via
  `HandoffCheckpoint` plus `platform-event-ref/0.1` correlation/provenance with
  authority re-admitted at the destination, accept), `VOI-021` (continuity
  implemented by moving authority into the session/handoff, reject), `VOI-022`
  (session conversation/memory presented as continuity/authority — Conversation
  != Memory, Memory != Continuity, Memory != Authority — reject), `VOI-023`
  (consent/purpose lineage attached to voice turns/observations and propagated
  to derivatives, accept), `VOI-024` (consent revocation invalidating
  downstream voice-derived use/recomputing derived state per provenance without
  rewriting historical audit/evidence, accept), `VOI-025` (source/turn deletion
  propagating withdrawal to reads and derivatives with tombstone semantics,
  accept), `VOI-026` (cross-surface contamination: content from surface A
  attributable on surface B without explicit lineage, reject-leak), `VOI-027`
  (prompt-injection content inside a voice transcript treated as untrusted
  observation, never as instruction/authority, accept-contained). Run → FAIL.
- [ ] **Step 2: GREEN.** Extend the voice-interaction contract with handoff +
  correlation continuity, no-authority-transport, consent/purpose lineage,
  revocation-invalidation, deletion-propagation, and injection containment;
  extend the harness validator plus its own tests; add the eight vectors; wire
  contract paths into CI. Suite → PASS. Regression: fabrics suite, topology
  suite, exact-head suite, World State conformance suite (projection-only
  check), consent-ledger–adjacent suites where configured.
- [ ] **Step 3: Commit** `feat(governance): pin voice continuity/consent
  acceptance`. Spec review + quality review recorded before the next task.

## Task 4 — Voice-interaction binding

- [ ] **Step 1: RED.** Extend the active-doc consistency tests to require
  `docs/VOICE-INTERACTION-V1.md` (canonical, concise: voice as Interaction
  Fabric edge; sessions carry no durable identity/state with durable stores
  outside in Runtime/WORKS/consent-ledger-owned stores; continuity via
  correlation/provenance, never by moving authority; transcript != identity and
  speaker != principal inherited from Wave F, not re-derived; session
  admission/egress through Trust Gateway; turn/stop/barge-in semantics per §14;
  `HandoffCheckpoint` + `platform-event-ref/0.1` continuity; consent revocation
  and deletion invalidate downstream use per provenance without rewriting audit;
  evidence-independent vs `BLOCKED_ON_VOICE_DEVICE_API_EVIDENCE` split; no
  realtime raw-audio streaming claims without device/API evidence; owner repos
  studio/wi-frontend/runtime as applicable; no duplication of Runtime PR #103)
  and to forbid voice authority-conflation phrases
  (session-as-identity/state/authority, handoff-as-grant,
  transcript-as-identity, speaker-as-principal, spoken-command-as-permission,
  correlation-as-authority, surface-as-authority-universe,
  persona-as-authority). Run → FAIL.
- [ ] **Step 2: GREEN.** Add the document (sourced from the V4 spec §§7.1/14,
  which stay as rationale); suite → PASS; no new authority, service, plane,
  fabric, repo, ownership, or AVC identifier anywhere in the diff.
- [ ] **Step 3: Commit** `docs(governance): bind voice-interaction seams`. Spec
  review + quality review recorded before the next task.

## Task 5 — Cross-repo build requests + Wave G close (with evidence-gated appendix)

- [ ] **Step 1: RED.** New `scripts/test_wave_g_requests_v0_1.py`
  asserting, for `voice-edge.md` under `docs/superpowers/requests/`:
  the file exists; names its owning repos (`Aftergraph/studio`,
  `Aftergraph/wi-frontend`, `Aftergraph/runtime` as applicable, with
  `trust-gateway` admission, `works-execution` durable execution, and
  consent-ledger-owned stores named as durable owners); names its exact
  contract (`voice-interaction/0.1` or its versioned successor, plus the
  binding); every named acceptance vector ID (`VOI-001`…`VOI-027` as
  applicable) exists in `docs/platform-conformance/v0.1/vectors.json`; states
  governance implements nothing in the owning repos; restates the canonical
  boundary (Interaction Fabric edge; no durable identity/state in sessions;
  continuity via correlation/provenance, never moved authority; transcript !=
  identity and speaker != principal as Wave F inheritance; Trust Gateway
  admission/egress); and carries an evidence-gated appendix section listing
  realtime raw-audio streaming and device/API characterization items explicitly
  marked `BLOCKED_ON_VOICE_DEVICE_API_EVIDENCE` with no PASS claims. Run → FAIL.
- [ ] **Step 2: GREEN.** Write the request file to satisfy the test; suite
  → PASS. A request is done only when the test reads its acceptance back
  out of `vectors.json` — "issued" alone counts for nothing.
- [ ] **Step 3:** Add `docs/evidence/platform-architecture-v4-wave-g.json`
  (`topology_v2`, `voice_interaction_vectors`, `session_turn_vectors`,
  `continuity_vectors`, `seam_binding`, `request_content`,
  `evidence_gated_blocked`, `platform_fabrics_regression`; result PASS only
  when every evidence-independent gate above is green;
  `evidence_gated_blocked` lists each `BLOCKED_ON_VOICE_DEVICE_API_EVIDENCE`
  item as BLOCKED, never PASS).
- [ ] **Step 4:** Full regression (all suites in Testing below) + commit
  `evidence(governance): close platform architecture v4 wave g`.

## Testing (every task + close)

```bash
python scripts/test_platform_topology_v2.py
python scripts/test_org_state_topology_v2.py
python scripts/test_platform_fabrics_v0_1.py
python scripts/test_golden_mission_skeleton_v0_1.py
python scripts/test_wave_b_requests_v0_1.py
python scripts/test_wave_c_requests_v0_1.py
python scripts/test_wave_d_requests_v0_1.py
python scripts/test_wave_e_requests_v0_1.py
python scripts/test_wave_f_requests_v0_1.py
python scripts/test_wave_g_requests_v0_1.py
python scripts/test_world_state_conformance_v0_1.py
python scripts/test_governance_exact_head_truth.py
python scripts/platform_topology.py check
python scripts/platform_topology.py check-readme
bash -n scripts/org-state-verify.sh
```

## Completion gate

Wave G closes when: Tasks 1–3 gates green on the branch (evidence-independent
vectors resolved against `vectors.json`, fixtures only, no device/API claims),
the Task 4 seam-binding test green (canonical boundary + Trust Gateway
admission/egress + Wave F inheritance + owner repos stated, no new
plane/fabric/AVC identifier), the Task 5 request-content test green (acceptance
vector IDs resolved against `vectors.json`, canonical boundary + owner repos +
`voice-interaction/0.1` lineage stated, evidence-gated appendix present and
marked `BLOCKED_ON_VOICE_DEVICE_API_EVIDENCE`), evidence record PASS with
`evidence_gated_blocked` BLOCKED (never PASS), branch merged through the
normal merge queue with spec + quality reviews recorded per task, and a fresh
`main` exact-head snapshot regenerates. Downstream edge/surface runs are
tracked by the owner repos — their results are never claimed here. No realtime
raw-audio streaming or device/API characterization result advances here, and no
numbered criterion from the Wave B scheme advances here except as explicitly
re-tested above. Runtime PR #103 supervision semantics are not re-proven
here. Wave F transcript/speaker semantics are inherited, not re-proven here.
