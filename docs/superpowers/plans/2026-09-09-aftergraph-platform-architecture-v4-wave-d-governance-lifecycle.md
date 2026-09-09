# Aftergraph Platform Architecture V4 — Wave D Governance and Lifecycle Gaps Coordination Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development —
> fresh implementer per task, spec-compliance review first, code-quality review
> second, both must pass before the next task.

## 0. Scope (read first)

Wave D is **Governance and lifecycle gaps** per the approved V4 design spec
(`docs/superpowers/specs/2026-09-08-aftergraph-platform-architecture-v4-and-platform-fabrics-v1-design.md`,
§22):

- resolve human-governance authority through AIE + TG enforcement;
- implement tenant/workspace lifecycle protocol;
- implement Consent Ledger events and downstream invalidation semantics.

Normative anchors (do not re-derive): AIE §5.2 (AIE owns principal/authority
semantics, delegation, mission envelopes, budgets, authority lifecycle,
revocation semantics, human-governance authority meaning; role labels such as
`owner`/`reviewer`/`auditor`/`operator` are convenience templates, never
authority; AIE grants are the authority truth); Trust §5.3 (TG owns tenant
lifecycle operational truth ACTIVE/SUSPENDED/EXPORTING/DELETING/DELETED,
Consent Ledger state and enforcement, workspace-scope identity and immutable
tenant binding; `DELETING` denies new grants/ingestion/execution; terminal
completion needs every required owner's acknowledgement; audit retention is
distinct); §12 (workspace experience owned by Studio; cross-tenant movement
is governed export/filter/new-identity/import, never in-place mutation;
Consent events Granted/Restricted/Revoked/Expired; revocation invalidates
six downstream categories; historic audit/evidence keeps its own retention
law and is never silently erased); invariants Consent != Authority and
revocation invalidates downstream use.

This plan covers the **governance-owned** part: experimental contracts,
acceptance vectors, revocation-invalidation conformance, the canonical
human-governance binding, and crisp cross-repo build requests. Ledger,
lifecycle, and workspace **implementation** lives in `aie`,
`trust-gateway`, `studio` (and domain owners for export/deletion
acknowledgements) and is specified here as follow-up requests with exact
acceptance — never implemented from this repo.

Out of scope (later waves, do not touch):

- Wave E (proactivity unification, Agent Organization evals);
- Wave F (Pocket connector, device characterization);
- Wave G (voice edge, cross-surface continuity);
- Wave H (promotion gates, model promotion);
- Wave I (AVC dissolution ledger execution, skill/Hermes migration, archival).

No new top-level services, planes, fabrics, repos, or ownership. No new
canonical AVC identifiers. Vector namespaces `CON-*` and `TEN-*`, and
fixture namespace `CONS-REV-*`, are Wave D conformance identifiers, not
canonical platform IDs.

## Global constraints (every task)

- TDD task-by-task: failing test first, prove RED, minimum change, GREEN,
  regression, inspect diff, small focused commit. No weakened tests.
- Constitutional invariants hold: Consent != Authority; Observation/Memory/
  Relationship/Consent/Prediction != Authority; revocation invalidates
  downstream effective use while audit keeps its own retention law; role
  labels never equal authority; cross-tenant movement is export/filter/
  new-identity/import, never in-place mutation.
- New vector kinds extend the harness with their own tests; the oracle stays
  independent of implementation internals and fails closed.
- Repository-local green never claims cross-repo or platform conformance.

## Task 1 — consent-ledger/0.1 contract and acceptance vectors

- [ ] **Step 1: RED.** Failing tests for `CON-001` (ConsentGranted with
  subject, purpose, scope, ledger record/version, accept), `CON-002`
  (use of already-derived contextual memory where a ConsentRevoked record
  ends the purpose, reject), `CON-003` (use past ConsentExpired validity,
  reject). Run → FAIL on missing contract/kind/vectors.
- [ ] **Step 2: GREEN.** Add `docs/contracts/consent-ledger/0.1.json`
  (experimental), extend the conformance harness with a `consent_ledger`
  kind validator plus its own tests, add the three vectors to
  `docs/platform-conformance/v0.1/vectors.json`, wire new contract paths
  into `.github/workflows/platform-fabrics.yml`. Re-run suite → PASS.
  Regression: fabrics suite, topology suite, exact-head suite.
- [ ] **Step 3: Commit** `feat(governance): pin consent-ledger acceptance`.

## Task 2 — tenant-lifecycle/0.1 contract and acceptance vectors

- [ ] **Step 1: RED.** Failing tests for `TEN-001` (ACTIVE tenant with TG
  operational truth and domain-owner acknowledgements recorded, accept),
  `TEN-002` (new grant/ingestion/execution admitted while DELETING,
  reject), `TEN-003` (transition to DELETED without every required owner's
  export/deletion/retention acknowledgement, reject). Run → FAIL.
- [ ] **Step 2: GREEN.** Add `docs/contracts/tenant-lifecycle/0.1.json`
  (experimental; states ACTIVE/SUSPENDED/EXPORTING/DELETING/DELETED),
  extend the harness with a `tenant_lifecycle` kind validator plus its own
  tests, add the three vectors, wire contract paths into CI. Suite → PASS.
  Regression: fabrics suite, topology suite, exact-head suite.
- [ ] **Step 3: Commit** `feat(governance): pin tenant-lifecycle acceptance`.

## Task 3 — Consent-revocation invalidation conformance

- [ ] **Step 1: RED.** Extend `scripts/test_world_state_conformance_v0_1.py`
  (or add a dedicated suite if the implementer justifies it) with
  `CONS-REV-001`: a ConsentRevoked record for one source/purpose
  invalidates derived memory, ACC projections, and World State assertions
  sourced solely from it, while unrelated uses survive and audit history is
  preserved byte-for-byte. Run → FAIL (no fixture).
- [ ] **Step 2: GREEN.** Add the fixture under
  `docs/platform-conformance/v0.1/world-state/`; suite → PASS. Fixtures
  carry consent/purpose lineage as the selection key; revocation behavior
  here is governed invalidation, not ledger implementation. Regression: all
  suites in Testing below.
- [ ] **Step 3: Commit** `feat(governance): prove consent-revocation invalidation`.

## Task 4 — Human-governance and workspace binding

- [ ] **Step 1: RED.** Extend the active-doc consistency tests to require
  `docs/HUMAN-GOVERNANCE-V1.md` (canonical, concise: human role labels map
  to AIE grants and TG enforcement; labels never equal authority; AIE
  grants are the authority truth; workspace binding immutable under the
  TG registry; Studio owns experience state only; seams mapped to V4
  owners; nothing that makes a label, surface, or workspace an authority
  source) and to forbid label-as-authority phrases. Run → FAIL.
- [ ] **Step 2: GREEN.** Add the document (sourced from the V4 spec
  §§5.2–5.3/12, which stay as rationale); suite → PASS; no new authority,
  role, or ownership anywhere in the diff.
- [ ] **Step 3: Commit** `docs(governance): bind human-governance authority`.

## Task 5 — Cross-repo build requests + Wave D close

- [ ] **Step 1: RED.** New `scripts/test_wave_d_requests_v0_1.py`
  asserting, for each of `aie-human-governance.md`,
  `trust-gateway-consent-ledger.md`, `trust-gateway-tenant-lifecycle.md`,
  `studio-workspace-experience.md` under `docs/superpowers/requests/`: the
  file exists; names its owning repo; names its exact contract
  (`consent-ledger/0.1`, `tenant-lifecycle/0.1`, or the governance
  binding); every named acceptance vector ID exists in
  `docs/platform-conformance/v0.1/vectors.json` (or the Task 3 fixture);
  and states governance implements nothing in the owning repo. Run → FAIL.
- [ ] **Step 2: GREEN.** Write the four request files to satisfy the test;
  suite → PASS. A request is done only when the test reads its acceptance
  back out of `vectors.json`/fixtures — "issued" alone counts for nothing.
- [ ] **Step 3:** Add `docs/evidence/platform-architecture-v4-wave-d.json`
  (`topology_v2`, `consent_vectors`, `lifecycle_vectors`,
  `revocation_conformance`, `governance_binding`, `request_content`,
  `platform_fabrics_regression`; result PASS only when every gate above is
  green).
- [ ] **Step 3:** Full regression (all suites in Testing below) + commit
  `evidence(governance): close platform architecture v4 wave d`.

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

Wave D closes when: Tasks 1–4 gates green on the branch, the Task 5
request-content test green (acceptance vector IDs resolved against
`vectors.json`/fixtures, not merely "issued"), evidence record PASS, branch
merged through the normal queue, and a fresh `main` exact-head snapshot
regenerates. Downstream ledger/lifecycle/workspace runs are tracked by
their owning repos — their results are never claimed here. Criteria 8
(human-governance and tenant/workspace seams) and 9 (consent revocation
produces downstream invalidation) advance here but close only with
later-wave composition proof.
