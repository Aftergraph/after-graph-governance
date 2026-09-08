# Aftergraph Platform Architecture V4 — Wave B Fabric Closure Coordination Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development —
> fresh implementer per task, spec-compliance review first, code-quality review
> second, both must pass before the next task.

## 0. Scope (read first)

Wave B is **Existing Fabric closure** per the approved V4 design spec
(`docs/superpowers/specs/2026-09-08-aftergraph-platform-architecture-v4-and-platform-fabrics-v1-design.md`,
§22):

- complete TG and WORKS `platform-event-ref/0.1` adapters;
- complete Runtime `capability-action/0.1` resolver and authority-preserving fallback;
- bind Verified Auto seams to the V4 ownership model;
- establish Golden Mission skeleton with exact-head pins.

This plan covers the **governance-owned** part: acceptance vectors, the Golden
Mission skeleton registry, the canonical Verified Auto seam binding, and
crisp cross-repo build requests. Adapter/resolver/runner **implementation**
lives in `trust-gateway`, `works-execution`, `runtime` (and verification in
`sentinel`/ISR) and is specified here as follow-up requests with exact
acceptance — never implemented from this repo.

Out of scope (later waves, do not touch):

- Wave C (Memory/ACC/Brain separation, world-assertion/situation contracts);
- Wave D (tenant lifecycle, Consent Ledger events);
- Wave E–H (proactivity, Pocket, voice, promotion gates);
- Wave I (AVC dissolution ledger execution, skill/Hermes migration, archival).
  The §16 ledger **format** stays as specified; executing it is Wave I.

No new top-level services, planes, fabrics, repos, or ownership. No new
canonical AVC identifiers. `platform-event-ref/0.1` stays a correlation
substrate, never a Fabric.

## Global constraints (every task)

- TDD task-by-task: failing test first, prove RED, minimum change, GREEN,
  regression, inspect diff, small focused commit. No weakened tests.
- Constitutional invariants hold: Observation/Memory/Relationship/Consent/
  Prediction != Authority; Runtime orchestrates but never widens authority;
  fallback never widens semantic capability authority; executor never
  self-verifies; World State stays rebuildable projection.
- Conformance-vector kinds stay within what
  `scripts/test_platform_fabrics_v0_1.py` evaluates (`event_ref`,
  `capability_action`, `causal_chain`) unless the task also extends the
  harness with tests.
- Repository-local green never claims cross-repo or platform conformance.

## Task 1 — Adapter acceptance vectors (event-ref gates 1 + 5)

- [ ] **Step 1: RED.** Extend `scripts/test_platform_fabrics_v0_1.py` (or the
  topology-adjacent suite if the implementer justifies it) with failing tests
  for: `ADP-TG-001` (TG audit entry projected field-for-field, accept),
  `ADP-TG-002` (reinterpreted effect class, reject), `ADP-WORKS-001` (WORKS
  event projected with native envelope retained alongside, accept),
  `ADP-WORKS-002` (projection that drops the native envelope reference,
  reject). Run: `python scripts/test_platform_fabrics_v0_1.py` → FAIL on the
  four missing vectors.
- [ ] **Step 2: GREEN.** Add the four vectors to
  `docs/platform-conformance/v0.1/vectors.json` following the existing
  EVT/CAP shapes; extend the harness only if a new kind is unavoidable (with
  its own tests). Re-run suite → PASS. Run
  `python scripts/test_platform_topology_v2.py` (expect 32 pass),
  `python scripts/test_governance_exact_head_truth.py` (expect 17 pass).
- [ ] **Step 3: Commit** `fix(governance): pin event-ref adapter acceptance`.

## Task 2 — Capability fallback no-widening vectors (gate 4, criterion 10)

- [ ] **Step 1: RED.** Failing tests for `CAP-004` (fallback implementation
  with equal-or-narrower authority envelope, accept) and `CAP-005` (fallback
  that widens authority or drops the verification requirement on a
  consequential effect, reject). Run → FAIL on missing vectors.
- [ ] **Step 2: GREEN.** Add both vectors; re-run suite → PASS. Regression:
  fabrics suite, topology suite, exact-head suite.
- [ ] **Step 3: Commit** `fix(governance): pin capability fallback acceptance`.

## Task 3 — Golden Mission skeleton registry (criterion 11)

- [ ] **Step 1: RED.** Failing test
  `scripts/test_golden_mission_skeleton_v0_1.py` asserting
  `docs/golden-mission/0.1.json` exists with branches `success`, `refusal`,
  `revocation`, `crash-recovery`, `verifier-failure`, each naming
  participating repos + required vector IDs, plus a `pins` map for exact-head
  SHAs (empty until the first skeleton run; pins are generated, never
  hand-authored). Run → FAIL (file missing).
- [ ] **Step 2: GREEN.** Add `docs/golden-mission/0.1.json` and
  `GOLDEN-003` (causal chain with broken canonical identity across a
  consequential seam, reject) to `vectors.json`; suite → PASS. The
  cross-repo **runner** is a downstream follow-up (Task 5), not this task.
- [ ] **Step 3: Commit** `feat(governance): register golden mission skeleton`.

## Task 4 — Verified Auto canonical seam binding

- [ ] **Step 1: RED.** Extend the active-doc consistency tests to require
  `docs/VERIFIED-AUTO-V1.md` (canonical, concise: seams mapped to V4 owners,
  nothing that widens Runtime authority or creates verification ownership)
  and forbid presenting the design spec as the normative reference in
  current-ownership rows. Run → FAIL.
- [ ] **Step 2: GREEN.** Add the document (sourced from
  `docs/superpowers/specs/2026-09-08-aftergraph-verified-auto-execution-design.md`,
  which stays as rationale); suite → PASS; no new authority or execution
  ownership anywhere in the diff.
- [ ] **Step 3: Commit** `docs(governance): bind verified auto seams to v4`.

## Task 5 — Cross-repo build requests + Wave B close

- [ ] **Step 1: RED.** Add `scripts/test_wave_b_requests_v0_1.py` asserting,
  for each of `trust-gateway-event-ref-adapter.md`,
  `works-execution-event-ref-adapter.md`,
  `runtime-capability-resolver-fallback.md`, `golden-mission-runner.md` under
  `docs/superpowers/requests/`: the file exists; names its owning repo;
  names its exact contract (`platform-event-ref/0.1`,
  `capability-action/0.1`, or the mission registry); every named acceptance
  vector ID exists in `docs/platform-conformance/v0.1/vectors.json`; and
  states governance implements nothing in the owning repo. Run → FAIL (no
  files, no test).
- [ ] **Step 2: GREEN.** Write the four request files to satisfy the test;
  suite → PASS. A request is done only when the test reads its acceptance
  back out of `vectors.json` — "issued" alone counts for nothing.
- [ ] **Step 3:** Add `docs/evidence/platform-architecture-v4-wave-b.json`
  (`topology_v2`, `adapter_vectors`, `fallback_vectors`, `mission_skeleton`,
  `verified_auto_binding`, `request_content`,
  `platform_fabrics_regression`; result PASS only when every gate above is
  green).
- [ ] **Step 3:** Full regression (all suites in Testing below) + commit
  `evidence(governance): close platform architecture v4 wave b`.

## Testing (every task + close)

```bash
python scripts/test_platform_topology_v2.py
python scripts/test_org_state_topology_v2.py
python scripts/test_platform_fabrics_v0_1.py
python scripts/test_governance_exact_head_truth.py
python scripts/platform_topology.py check
python scripts/platform_topology.py check-readme
bash -n scripts/org-state-verify.sh
```

## Completion gate

Wave B closes when: Tasks 1–4 gates green on the branch, the Task 5
request-content test green (acceptance vector IDs resolved against
`vectors.json`, not merely "issued"), evidence record PASS, branch merged
through the normal queue, and a fresh `main` exact-head snapshot
regenerates. Downstream adapter/resolver/runner runs are tracked by their
owning repos — their results are never claimed here. Criterion 11+ (live
mission branches) close in later waves.
