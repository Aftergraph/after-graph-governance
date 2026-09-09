# Aftergraph Platform Architecture V4 — Wave F Physical-World Perception (Pocket Connector) Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development —
> fresh implementer per task, spec-compliance review first, code-quality review
> second, both must pass before the next task.

## 0. Scope (read first)

Wave F is **physical-world perception (Pocket connector)** per the approved V4 design spec
(`docs/superpowers/specs/2026-09-08-aftergraph-platform-architecture-v4-and-platform-fabrics-v1-design.md`,
§13 and §22 Wave F):

- add a multi-tenant Pocket connector under Wie (`wi-backend` provider subsystem);
- prove source lineage, webhook replay/dedupe, deletion, consent and cross-tenant behavior;
- run physical-device characterization only after hardware arrival (hardware-gated, not claimed here).

Normative anchors (do not re-derive): Pocket placement §13 (Pocket is a
multi-tenant Perception Fabric source through a provider subsystem in
`wi-backend`, never a new repository; REST path is canonical-data/
reconciliation oriented, webhooks are event-plane signals, MCP is optional
interactive access rather than the canonical ingestion source; Pocket output
remains untrusted observation content; speaker labels are not principal
identity; a spoken command does not directly execute; transcript, speaker
attribution, summary and action extraction retain derivation lineage with
different evidentiary weights; a Pocket-derived commitment may become a
`CommitmentCandidate` and consequential action still follows AIE -> Trust
Gateway -> Runtime -> WORKS -> verification; source deletion or consent
revocation must invalidate downstream use/recompute derived state per
provenance without rewriting historical audit/evidence); Wave F §22 scope
above.

Canonical boundary (every task, no exceptions):

```text
Pocket = physical-world context source whose output is observation only.
Pocket != authority; transcript != identity;
speaker attribution != principal authentication;
spoken instruction != permission to execute.
```

Owner: Wie / `wi-backend`. NO new repo. No `pocket-platform`, `personal-ai`,
`mega-brain`, or any other top-level repository.

Plane mapping (fixed, do not reinterpret):

- REST = reconciliation plane (canonical-data/hydration);
- webhooks = event plane (signals + signature/replay/dedupe guard);
- MCP = optional interactive plane (never the canonical ingestion source).

No realtime-audio claims without device evidence. Any realtime-audio,
live-capture, acoustic-model, or physical-device characterization work is
hardware-gated and marked `BLOCKED_ON_POCKET_HARDWARE` (Task 5 appendix);
it is never proven with mocks and never closes a device-independent gate.

This plan covers the **governance-owned** part: experimental contract(s),
acceptance vectors, the canonical Pocket binding, and crisp cross-repo build
request(s). Connector, adapter, Wie Observation, and World State projection
**implementation** lives in `wi-backend` (and consuming projection owners),
and is specified here as follow-up request(s) with exact acceptance — never
implemented from this repo.

Out of scope (do not touch):

- Wave G (voice edge, realtime voice, cross-surface continuity);
- Wave H (promotion gates, model promotion);
- Wave I (AVC dissolution ledger execution, skill/Hermes migration, archival);
- Runtime PR #103 Muse supervision — do NOT duplicate it here; if a task
  overlaps supervision semantics, it references PR #103 and stays out.

No new top-level services, planes, fabrics, repos, or ownership. No new
canonical AVC identifiers. Vector namespace `PCK-*` is a Wave F conformance
identifier, not a canonical platform ID.

Device-independent vs hardware-gated split (binding for all tasks below):

- Device-independent (prove now in governance + `wi-backend` with fixtures):
  source contract, provenance, webhook signature validation, replay
  protection, dedupe/idempotency, out-of-order/edit/deletion-tombstone
  behavior, REST reconciliation, MCP boundary, tenant scoping,
  classification, consent/purpose lineage, revocation invalidation,
  transcript/speaker uncertainty, Observation mapping, prompt-injection
  handling, cross-conversation contamination, deletion propagation, World
  State invalidation, fixtures, cross-repo requests, evidence record.
- Hardware-gated (marked `BLOCKED_ON_POCKET_HARDWARE`, never gated as PASS
  here): physical-device characterization, on-device capture behavior,
  realtime-audio quality/latency claims, acoustic/sensor calibration.

## Global constraints (every task)

- TDD task-by-task: failing test first, prove RED, minimum change, GREEN,
  regression, inspect diff, small focused commit. No weakened tests.
- Spec review + quality review gates per task: spec-compliance review first,
  code-quality review second; both must pass before the next task. Reviews
  are recorded on the branch (review-note or sign-off lines in the commit).
- Merge-queue only. No direct-to-main pushes, no bypass.
- Canonical boundary holds in every vector, doc, and fixture: Pocket output
  is observation only; transcript is not identity; speaker attribution is not
  principal authentication; spoken instruction is not permission to execute.
- REST/webhooks/MCP plane mapping is fixed per §13; MCP never becomes the
  canonical ingestion source; webhooks never become reconciliation truth.
- New vector kinds extend the harness with their own tests; the oracle stays
  independent of implementation internals and fails closed.
- No realtime-audio or device-characterization claims without device
  evidence; hardware-gated items stay `BLOCKED_ON_POCKET_HARDWARE`.
- Do not duplicate Runtime PR #103 Muse supervision semantics.
- Repository-local green never claims cross-repo or platform conformance.

## Task 1 — pocket-source/0.1 contract and acceptance vectors (device-independent)

Device-independent. Fixtures only; no hardware.

- [ ] **Step 1: RED.** Failing tests for `PCK-001` (tenant-scoped Pocket
  payload with source contract + provenance mapping to a Wie Observation,
  accept), `PCK-002` (payload with cross-tenant credential/secret reuse or
  missing tenant scope, reject), `PCK-003` (transcript presented as principal
  identity, reject), `PCK-004` (speaker attribution presented as principal
  authentication, reject), `PCK-005` (spoken instruction self-executing as
  permission without AIE -> Trust Gateway -> Runtime -> WORKS ->
  verification, reject), `PCK-006` (Pocket-derived `CommitmentCandidate`
  routed through the governed consequential path, accept), `PCK-007`
  (transcript/speaker/summary/action-extraction retaining distinct derivation
  lineage and evidentiary weights with uncertainty preserved into the
  Observation mapping, accept). Run → FAIL on missing contract/kind/vectors.
- [ ] **Step 2: GREEN.** Add `docs/contracts/pocket-source/0.1.json`
  (experimental: source contract, provenance, tenant scoping,
  classification, transcript/speaker uncertainty, Observation mapping),
  extend the conformance harness with a `pocket_source` kind validator plus
  its own tests, add the seven vectors to
  `docs/platform-conformance/v0.1/vectors.json`, wire new contract paths
  into `.github/workflows/platform-fabrics.yml`. Add fixtures (synthetic
  Pocket REST/webhook payloads with tenant scope, classification labels, and
  uncertainty fields; no real device captures). Re-run suite → PASS.
  Regression: fabrics suite, topology suite, exact-head suite.
- [ ] **Step 3: Commit** `feat(governance): pin pocket-source acceptance`.
  Spec review + quality review recorded before the next task.

## Task 2 — webhook event-plane guards + REST reconciliation (device-independent)

Device-independent. Fixtures only; no hardware.

- [ ] **Step 1: RED.** Failing tests for `PCK-010` (webhook with valid
  signature accepted to the event plane, accept), `PCK-011` (webhook with
  bad/missing signature, reject), `PCK-012` (replayed webhook delivery
  rejected by replay protection, reject-duplicate), `PCK-013` (duplicate
  delivery deduped by idempotency key to a single Observation, accept-once),
  `PCK-014` (out-of-order delivery reconciled to current state without
  resurrecting superseded content, accept), `PCK-015` (edit superseding the
  original with lineage preserved, accept), `PCK-016`
  (deletion-tombstone honored: content withdrawn from reads, audit retained,
  accept), `PCK-017` (REST reconciliation/hydration converging event-plane
  state to canonical data without webhooks becoming truth, accept).
  Run → FAIL.
- [ ] **Step 2: GREEN.** Extend `docs/contracts/pocket-source/0.1.json`
  (or a versioned `0.2.json` if breaking; prefer additive) with webhook
  signature/replay/dedupe/idempotency, out-of-order/edit/tombstone, and REST
  reconciliation semantics; extend the `pocket_source` harness validator plus
  its own tests; add the eight vectors; wire contract paths into CI. Suite →
  PASS. Regression: fabrics suite, topology suite, exact-head suite,
  World State conformance suite (projection-only check, Task 3 owns full
  invalidation).
- [ ] **Step 3: Commit** `feat(governance): pin pocket webhook+reconciliation
  acceptance`. Spec review + quality review recorded before the next task.

## Task 3 — consent/purpose lineage, deletion propagation, MCP boundary, adversarial handling (device-independent)

Device-independent. Fixtures only; no hardware.

- [ ] **Step 1: RED.** Failing tests for `PCK-020` (consent/purpose lineage
  attached to Pocket Observation and propagated to derivatives, accept),
  `PCK-021` (consent revocation invalidating downstream use/recomputing
  derived state per provenance without rewriting historical audit/evidence,
  accept), `PCK-022` (source deletion propagating withdrawal to reads and
  derivatives with tombstone semantics, accept), `PCK-023` (World State
  invalidation on revocation/deletion: projections recomputed/invalidated,
  never stale-served as current, accept), `PCK-024` (prompt-injection content
  inside a Pocket transcript treated as untrusted observation, never as
  instruction/authority, accept-contained), `PCK-025` (cross-conversation
  contamination: content from conversation A unattributable in conversation
  B without explicit lineage, reject-leak), `PCK-026` (MCP used as optional
  interactive access with the same observation-only boundary, accept),
  `PCK-027` (MCP presented as canonical ingestion source bypassing
  REST/webhook guards, reject). Run → FAIL.
- [ ] **Step 2: GREEN.** Extend the pocket-source contract with
  consent/purpose lineage, revocation-invalidation, deletion-propagation,
  World State invalidation expectations, prompt-injection containment, and
  the MCP boundary; extend the harness validator plus its own tests; add the
  eight vectors; wire contract paths into CI. Suite → PASS. Regression:
  fabrics suite, topology suite, exact-head suite, World State conformance
  suite, consent-ledger–adjacent suites where configured.
- [ ] **Step 3: Commit** `feat(governance): pin pocket consent/deletion/MCP
  acceptance`. Spec review + quality review recorded before the next task.

## Task 4 — Pocket binding

- [ ] **Step 1: RED.** Extend the active-doc consistency tests to require
  `docs/POCKET-SOURCE-V1.md` (canonical, concise: Pocket as physical-world
  context source with observation-only output; Pocket != authority;
  transcript != identity; speaker attribution != principal authentication;
  spoken instruction != permission to execute; owner Wie / `wi-backend`
  provider subsystem, no new repo; REST = reconciliation, webhooks = event
  plane with signature/replay/dedupe guard, MCP = optional interactive plane
  never canonical; derivation lineage with distinct evidentiary weights;
  governed consequential path for any Pocket-derived commitment; consent
  revocation and source deletion invalidate downstream use per provenance
  without rewriting audit; device-independent vs `BLOCKED_ON_POCKET_HARDWARE`
  split; no realtime-audio claims without device evidence; no duplication of
  Runtime PR #103) and to forbid Pocket authority-conflation phrases
  (Pocket-as-principal/authority/executor/oracle, transcript-as-identity,
  speaker-as-authentication, spoken-command-as-permission, MCP-as-ingestion,
  webhook-as-truth). Run → FAIL.
- [ ] **Step 2: GREEN.** Add the document (sourced from the V4 spec §13,
  which stays as rationale); suite → PASS; no new authority, service,
  plane, fabric, repo, ownership, or AVC identifier anywhere in the diff.
- [ ] **Step 3: Commit** `docs(governance): bind pocket-source seams`. Spec
  review + quality review recorded before the next task.

## Task 5 — Cross-repo build requests + Wave F close (with hardware-gated appendix)

- [ ] **Step 1: RED.** New `scripts/test_wave_f_requests_v0_1.py`
  asserting, for `pocket-connector.md` under `docs/superpowers/requests/`:
  the file exists; names its owning repo (`Aftergraph/wi-backend` as the
  Pocket provider-subsystem owner under Wie); names its exact contract
  (`pocket-source/0.1` or its versioned successor, plus the binding);
  every named acceptance vector ID (`PCK-001`…`PCK-027` as applicable)
  exists in `docs/platform-conformance/v0.1/vectors.json`; states governance
  implements nothing in the owning repo; restates the plane mapping
  (REST = reconciliation, webhooks = event, MCP = optional interactive);
  restates the canonical boundary; and carries a hardware-gated appendix
  section listing physical-device characterization items explicitly marked
  `BLOCKED_ON_POCKET_HARDWARE` with no PASS claims. Run → FAIL.
- [ ] **Step 2: GREEN.** Write the request file to satisfy the test; suite
  → PASS. A request is done only when the test reads its acceptance back
  out of `vectors.json` — "issued" alone counts for nothing.
- [ ] **Step 3:** Add `docs/evidence/platform-architecture-v4-wave-f.json`
  (`topology_v2`, `pocket_source_vectors`, `webhook_reconciliation_vectors`,
  `consent_deletion_vectors`, `seam_binding`, `request_content`,
  `hardware_gated_blocked`, `platform_fabrics_regression`; result PASS only
  when every device-independent gate above is green; `hardware_gated_blocked`
  lists each `BLOCKED_ON_POCKET_HARDWARE` item as BLOCKED, never PASS).
- [ ] **Step 4:** Full regression (all suites in Testing below) + commit
  `evidence(governance): close platform architecture v4 wave f`.

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
python scripts/test_world_state_conformance_v0_1.py
python scripts/test_governance_exact_head_truth.py
python scripts/platform_topology.py check
python scripts/platform_topology.py check-readme
bash -n scripts/org-state-verify.sh
```

## Completion gate

Wave F closes when: Tasks 1–4 gates green on the branch (device-independent
vectors resolved against `vectors.json`, fixtures only, no device claims),
the Task 5 request-content test green (acceptance vector IDs resolved against
`vectors.json`, plane mapping + canonical boundary + `wi-backend` ownership
stated, hardware-gated appendix present and marked
`BLOCKED_ON_POCKET_HARDWARE`), evidence record PASS with
`hardware_gated_blocked` BLOCKED (never PASS), branch merged through the
normal merge queue with spec + quality reviews recorded per task, and a fresh
`main` exact-head snapshot regenerates. Downstream connector/adapter runs are
tracked by `wi-backend` — their results are never claimed here. No realtime-
audio or physical-device characterization result advances here, and no
numbered criterion from the Wave B scheme advances here except as explicitly
re-tested above. Runtime PR #103 supervision semantics are not re-proven
here.
