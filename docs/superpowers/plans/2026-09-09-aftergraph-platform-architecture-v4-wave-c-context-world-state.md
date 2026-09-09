# Aftergraph Platform Architecture V4 — Wave C Context and World State Coordination Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development —
> fresh implementer per task, spec-compliance review first, code-quality review
> second, both must pass before the next task.

## 0. Scope (read first)

Wave C is **Context and World State** per the approved V4 design spec
(`docs/superpowers/specs/2026-09-08-aftergraph-platform-architecture-v4-and-platform-fabrics-v1-design.md`,
§22):

- formalize Memory/ACC/WORKS Brain separation;
- genericize Situation/Entity/Relationship contracts;
- add `world-assertion/0.1` / `situation/0.1` experimental contracts;
- implement rebuild/currentness/invalidation conformance before production dependence.

Normative anchors (do not re-derive): non-goals §3 items 7–9 (ACC is not a
memory database or mission authority; WORKS Brain is not a personal/context
memory store; World State never becomes writable truth or an authority
source); Runtime §5.4 (Runtime Memory is operational/contextual, never
authority-eligible, distinct from WORKS Brain and ACC; World State is a
rebuildable projection; agents propose assertion candidates, never effective
truth mutations); Execution §5.5 (WORKS Brain is durable organizational
knowledge under human-stamped promotion law); Context §7.4 (Entity /
Relationship / WorldAssertion / Situation primitives, epistemic state
OBSERVED/INFERRED/PREDICTED/UNKNOWN, currentness CURRENT/STALE/DISPUTED/
SUPERSEDED, full rules list); consent/purpose lineage for selective
invalidation.

This plan covers the **governance-owned** part: experimental contracts,
acceptance vectors, the canonical separation binding, rebuild/currentness/
invalidation conformance, and crisp cross-repo build requests. Memory,
Brain, capsule, and projection **implementation** lives in `runtime`,
`works-execution`, `context-continuity`/ACC owners and source repos, and is
specified here as follow-up requests with exact acceptance — never
implemented from this repo.

Out of scope (later waves, do not touch):

- Wave D (human-governance authority, tenant/workspace lifecycle, Consent Ledger events);
- Wave E–H (proactivity unification, Pocket, voice, promotion gates);
- Wave I (AVC dissolution ledger execution, skill/Hermes migration, archival).

No new top-level services, planes, fabrics, repos, or ownership. No new
canonical AVC identifiers. Vector namespaces `WA-*` and `SIT-*` are
Wave C conformance identifiers, not canonical platform IDs.

## Global constraints (every task)

- TDD task-by-task: failing test first, prove RED, minimum change, GREEN,
  regression, inspect diff, small focused commit. No weakened tests.
- Constitutional invariants hold: Observation/Memory/Relationship/Consent/
  Prediction != Authority; World State is rebuildable projection, never
  writable canonical truth; predictions may guide planning but never silently
  satisfy consequential preconditions; stale is represented as stale/unknown,
  never refreshed by timestamp laundering; descriptive relations never become
  AIE grants; Runtime orchestrates but never widens authority.
- New vector kinds extend the harness with their own tests; the oracle stays
  independent of implementation internals and fails closed.
- Repository-local green never claims cross-repo or platform conformance.

## Task 1 — world-assertion/0.1 contract and acceptance vectors

- [ ] **Step 1: RED.** Failing tests for `WA-001` (OBSERVED + CURRENT
  assertion with subject/predicate/value-or-ref, source + evidence
  references, timing, tenant/domain/classification scope, consent-record/
  version and purpose lineage, accept), `WA-002` (PREDICTED state offered
  where current observed evidence is required, reject), `WA-003` (STALE
  assertion refreshed by timestamp laundering instead of represented as
  stale/unknown, reject). Run → FAIL on missing contract/kind/vectors.
- [ ] **Step 2: GREEN.** Add `docs/contracts/world-assertion/0.1.json`
  (experimental), extend the conformance harness with a `world_assertion`
  kind validator plus its own tests, add the three vectors to
  `docs/platform-conformance/v0.1/vectors.json`, wire new contract paths
  into `.github/workflows/platform-fabrics.yml`. Re-run suite → PASS.
  Regression: fabrics suite, topology suite, exact-head suite.
- [ ] **Step 3: Commit** `feat(governance): pin world-assertion acceptance`.

## Task 2 — situation/0.1 contract and generic Entity/Relationship shapes

- [ ] **Step 1: RED.** Failing tests for `SIT-001` (situation composing
  generic Entity/Relationship entries with full provenance, accept),
  `SIT-002` (descriptive `trusts`/`delegates_to` relation presented as an
  AIE grant, reject), `SIT-003` (situation crossing tenant scope without
  explicit governed export/import identity, reject). Run → FAIL.
- [ ] **Step 2: GREEN.** Add `docs/contracts/situation/0.1.json`
  (experimental; Entity/Relationship shapes generic, not Wie-specific),
  extend the harness with a `situation` kind validator plus its own tests,
  add the three vectors, wire contract paths into CI. Suite → PASS.
  Regression: fabrics suite, topology suite, exact-head suite.
- [ ] **Step 3: Commit** `feat(governance): pin situation acceptance`.

## Task 3 — Memory/ACC/Brain separation binding

- [ ] **Step 1: RED.** Extend the active-doc consistency tests to require
  `docs/MEMORY-ACC-BRAIN-V1.md` (canonical, concise: Runtime Memory =
  operational/contextual, never authority-eligible; WORKS Brain = durable
  organizational knowledge under human-stamped promotion; ACC = portable
  continuity transfer, never a memory database or mission authority; seams
  mapped to V4 owners; nothing that makes any store an authority source)
  and to forbid memory/authority conflation phrases. Run → FAIL.
- [ ] **Step 2: GREEN.** Add the document (sourced from the V4 spec
  §§5.4–5.5/7.4 and `docs/ACC-BOUNDARY-PROPOSAL-v0.1.md`, which stay as
  rationale); suite → PASS; no new authority, store, or ownership anywhere
  in the diff.
- [ ] **Step 3: Commit** `docs(governance): bind memory-acc-brain separation`.

## Task 4 — Rebuild/currentness/invalidation conformance

- [ ] **Step 1: RED.** New `scripts/test_world_state_conformance_v0_1.py`
  asserting over deterministic fixtures: REBUILD-001 (post-failure rebuild
  from canonical sources with one source unavailable yields stale/unknown,
  accept), INVALIDATE-001 (source deletion invalidates derived state per
  provenance without rewriting audit history, accept), LAUNDER-001
  (timestamp refresh of stale state without new observation, reject).
  Consent-revocation invalidation behavior is Wave D (§12/Consent Ledger),
  not this task: fixtures carry consent/purpose lineage as data only.
  Run → FAIL (no files, no fixtures).
- [ ] **Step 2: GREEN.** Add fixtures under
  `docs/platform-conformance/v0.1/world-state/` plus the suite; wire into
  CI; suite → PASS. Regression: all suites in Testing below.
- [ ] **Step 3: Commit** `feat(governance): prove world-state rebuild conformance`.

## Task 5 — Cross-repo build requests + Wave C close

- [ ] **Step 1: RED.** New `scripts/test_wave_c_requests_v0_1.py`
  asserting, for each of `runtime-memory-separation.md`,
  `works-brain-governance.md`, `acc-capsule-conformance.md`,
  `world-state-projection.md` under `docs/superpowers/requests/`: the file
  exists; names its owning repo (`Aftergraph/runtime`,
  `Aftergraph/works-execution`, `Aftergraph/context-continuity` for the ACC
  capsule request since no dedicated ACC repo exists and Wave C creates
  none, `Aftergraph/runtime` for the projection request); names its exact
  contract (`world-assertion/0.1`, `situation/0.1`, or the separation
  binding); every named acceptance vector ID exists in
  `docs/platform-conformance/v0.1/vectors.json` (or the Task 4 fixtures);
  and states governance implements nothing in the owning repo. Run → FAIL.
- [ ] **Step 2: GREEN.** Write the four request files to satisfy the test;
  suite → PASS. A request is done only when the test reads its acceptance
  back out of `vectors.json`/fixtures — "issued" alone counts for nothing.
- [ ] **Step 3:** Add `docs/evidence/platform-architecture-v4-wave-c.json`
  (`topology_v2`, `world_assertion_vectors`, `situation_vectors`,
  `separation_binding`, `rebuild_conformance`, `request_content`,
  `platform_fabrics_regression`; result PASS only when every gate above is
  green).
- [ ] **Step 3:** Full regression (all suites in Testing below) + commit
  `evidence(governance): close platform architecture v4 wave c`.

## Testing (every task + close)

```bash
python scripts/test_platform_topology_v2.py
python scripts/test_org_state_topology_v2.py
python scripts/test_platform_fabrics_v0_1.py
python scripts/test_golden_mission_skeleton_v0_1.py
python scripts/test_wave_b_requests_v0_1.py
python scripts/test_wave_c_requests_v0_1.py
python scripts/test_world_state_conformance_v0_1.py
python scripts/test_governance_exact_head_truth.py
python scripts/platform_topology.py check
python scripts/platform_topology.py check-readme
bash -n scripts/org-state-verify.sh
```

## Completion gate

Wave C closes when: Tasks 1–4 gates green on the branch, the Task 5
request-content test green (acceptance vector IDs resolved against
`vectors.json`/fixtures, not merely "issued"), evidence record PASS, branch
merged through the normal queue, and a fresh `main` exact-head snapshot
regenerates. Downstream memory/brain/capsule/projection runs are tracked by
their owning repos — their results are never claimed here. Criterion 6
(World State projection-only) advances here but closes only with
later-wave composition proof. Criterion 7 (commitment resolution canonical
in Wie) is untouched in Wave C.
