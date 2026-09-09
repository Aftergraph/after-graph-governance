# Aftergraph Platform Architecture V4 — Wave E Proactivity and Organization Coordination Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development —
> fresh implementer per task, spec-compliance review first, code-quality review
> second, both must pass before the next task.

## 0. Scope (read first)

Wave E is **Proactivity and organization** per the approved V4 design spec
(`docs/superpowers/specs/2026-09-08-aftergraph-platform-architecture-v4-and-platform-fabrics-v1-design.md`,
§22):

- unify Opportunity/AttentionCandidate correlation across Wie, Runtime and
  Cron without a new service;
- strengthen Agent Organization conformance and independent evals.

Normative anchors (do not re-derive): Proactivity §7.5 (three distinct
sensing paths — Wie external-signal, Runtime mission/state, Cron scheduled
read-only sensing; native events stay native and may project into the
correlation substrate for dedupe/correlation; candidate outcomes Opportunity
/ AttentionCandidate / CommitmentCandidate / observation update; Cron Fabric
retains zero execution authority); Agent Organization §7.7 (Runtime owns
team topology, worker lifecycle, routing, recovery; AIE owns delegated
authority; Trust Gateway owns admission; WORKS owns durable work/leases/
effects; verification stays independent; manager-worker default; bounded
protocol-governed peer communication; recursive delegation never multiplies
authority or budget; child envelopes equal-or-narrower; parent budget
atomically partitioned/reserved across children; no worker self-grants
authority, administers peer authority, or self-declares verified
completion); invariants on executor self-verification and authority
envelopes.

This plan covers the **governance-owned** part: experimental contracts,
acceptance vectors, the canonical proactivity/organization binding, and
crisp cross-repo build requests. Sensing, topology, delegation, and eval
**implementation** lives in `wi-backend`, `runtime`,
`aftergraph-cron-fabric`, and verification owners, and is specified here as
follow-up requests with exact acceptance — never implemented from this
repo.

Out of scope (later waves, do not touch):

- Wave F (Pocket connector, device characterization);
- Wave G (voice edge, cross-surface continuity);
- Wave H (promotion gates, model promotion);
- Wave I (AVC dissolution ledger execution, skill/Hermes migration, archival).

No new top-level services, planes, fabrics, repos, or ownership. No new
canonical AVC identifiers. Vector namespaces `PRO-*`, `ORG-*`, and
`EVAL-*` are Wave E conformance identifiers, not canonical platform IDs.

## Global constraints (every task)

- TDD task-by-task: failing test first, prove RED, minimum change, GREEN,
  regression, inspect diff, small focused commit. No weakened tests.
- Constitutional invariants hold: Cron has zero execution authority;
  candidates never self-admit to commitments; child envelopes
  equal-or-narrower; budgets partition without multiplication; no worker
  self-grants authority, administers peer authority, or self-declares
  verified completion; verification stays independent; evaluators never
  score their own execution.
- New vector kinds extend the harness with their own tests; the oracle stays
  independent of implementation internals and fails closed.
- Repository-local green never claims cross-repo or platform conformance.

## Task 1 — proactivity/0.1 contract and acceptance vectors

- [ ] **Step 1: RED.** Failing tests for `PRO-001` (Wie external signal
  projecting a native event to an Opportunity candidate with native meaning
  preserved, accept), `PRO-002` (Cron sensing path asserting execution
  authority, reject), `PRO-003` (Wie candidate presenting as an admitted
  commitment without Trust Gateway admission, reject), `PRO-004` (Runtime
  mission-state sensing to an opportunity/recovery candidate, accept),
  `PRO-005` (same native signal via Wie and Cron correlating and deduping
  to a single AttentionCandidate, accept), `PRO-006` (Cron scheduled
  read-only sensing to a finding with zero execution authority, accept).
  Run → FAIL on missing contract/kind/vectors.
- [ ] **Step 2: GREEN.** Add `docs/contracts/proactivity/0.1.json`
  (experimental), extend the conformance harness with a `proactivity` kind
  validator plus its own tests, add the three vectors to
  `docs/platform-conformance/v0.1/vectors.json`, wire new contract paths
  into `.github/workflows/platform-fabrics.yml`. Re-run suite → PASS.
  Regression: fabrics suite, topology suite, exact-head suite.
- [ ] **Step 3: Commit** `feat(governance): pin proactivity acceptance`.

## Task 2 — org-delegation/0.1 contract and acceptance vectors

- [ ] **Step 1: RED.** Failing tests for `ORG-001` (child envelope
  equal-or-narrower than the parent with the parent budget atomically
  partitioned across children, accept), `ORG-002` (child envelope widening
  parent authority, reject), `ORG-003` (sibling partitions summing beyond
  the parent budget, reject), `ORG-004` (worker self-granting authority or
  self-declaring verified completion, reject). Run → FAIL.
- [ ] **Step 2: GREEN.** Add `docs/contracts/org-delegation/0.1.json`
  (experimental), extend the harness with an `org_delegation` kind
  validator plus its own tests, add the four vectors, wire contract paths
  into CI. Suite → PASS. Regression: fabrics suite, topology suite,
  exact-head suite.
- [ ] **Step 3: Commit** `feat(governance): pin org-delegation acceptance`.

## Task 3 — agent-eval/0.1 contract and acceptance vectors

- [ ] **Step 1: RED.** Failing tests for `EVAL-001` (independent evaluator,
  distinct from the executor, scoring a delegation record against criteria
  with evidence references, accept), `EVAL-002` (executor scoring its own
  execution, reject), `EVAL-003` (eval verdict promoting itself, mutating
  governance, or waiving verification, reject). Run → FAIL.
- [ ] **Step 2: GREEN.** Add `docs/contracts/agent-eval/0.1.json`
  (experimental), extend the harness with an `agent_eval` kind validator
  plus its own tests, add the three vectors, wire contract paths into CI.
  Suite → PASS. Regression: fabrics suite, topology suite, exact-head
  suite.
- [ ] **Step 3: Commit** `feat(governance): pin agent-eval acceptance`.

## Task 4 — Proactivity/organization binding

- [ ] **Step 1: RED.** Extend the active-doc consistency tests to require
  `docs/PROACTIVITY-ORG-V1.md` (canonical, concise: Wie/Runtime/Cron
  sensing seams mapped to V4 owners with no new service and zero Cron
  execution authority; candidates never self-admit; organization seams —
  Runtime topology, AIE authority, TG admission, WORKS durable work,
  independent verification; manager-worker default; child envelopes
  equal-or-narrower with partitioned budgets; evaluators never score their
  own execution; nothing that grants a path, candidate, worker, or eval
  execution or verification authority) and to forbid path/worker/eval
  authority-conflation phrases. Run → FAIL.
- [ ] **Step 2: GREEN.** Add the document (sourced from the V4 spec
  §§7.5/7.7, which stay as rationale); suite → PASS; no new authority,
  service, or ownership anywhere in the diff.
- [ ] **Step 3: Commit** `docs(governance): bind proactivity-org seams`.

## Task 5 — Cross-repo build requests + Wave E close

- [ ] **Step 1: RED.** New `scripts/test_wave_e_requests_v0_1.py`
  asserting, for each of `wi-proactivity-sensing.md`,
  `runtime-opportunity-recovery.md`, `cron-observation-sensing.md`,
  `org-delegation-evals.md` under `docs/superpowers/requests/`: the file
  exists; names its owning repo (`Aftergraph/wi-backend`,
  `Aftergraph/runtime`, `Aftergraph/aftergraph-cron-fabric`,
  `Aftergraph/runtime` for delegation topology with evaluator independence
  required); names its exact contract (`proactivity/0.1`,
  `org-delegation/0.1`, `agent-eval/0.1`, or the binding); every named
  acceptance vector ID exists in
  `docs/platform-conformance/v0.1/vectors.json`; and states governance
  implements nothing in the owning repo. Run → FAIL.
- [ ] **Step 2: GREEN.** Write the four request files to satisfy the test;
  suite → PASS. A request is done only when the test reads its acceptance
  back out of `vectors.json` — "issued" alone counts for nothing.
- [ ] **Step 3:** Add `docs/evidence/platform-architecture-v4-wave-e.json`
  (`topology_v2`, `proactivity_vectors`, `delegation_vectors`,
  `eval_vectors`, `seam_binding`, `request_content`,
  `platform_fabrics_regression`; result PASS only when every gate above is
  green).
- [ ] **Step 3:** Full regression (all suites in Testing below) + commit
  `evidence(governance): close platform architecture v4 wave e`.

## Testing (every task + close)

```bash
python scripts/test_platform_topology_v2.py
python scripts/test_org_state_topology_v2.py
python scripts/test_platform_fabrics_v0_1.py
python scripts/test_golden_mission_skeleton_v0_1.py
python scripts/test_wave_b_requests_v0_1.py
python scripts/test_wave_c_requests_v0_1.py
python scripts/test_wave_d_requests_v0_1.py
python scripts/test_world_state_conformance_v0_1.py
python scripts/test_governance_exact_head_truth.py
python scripts/platform_topology.py check
python scripts/platform_topology.py check-readme
bash -n scripts/org-state-verify.sh
```

## Completion gate

Wave E closes when: Tasks 1–4 gates green on the branch, the Task 5
request-content test green (acceptance vector IDs resolved against
`vectors.json`, not merely "issued"), evidence record PASS, branch merged
through the normal queue, and a fresh `main` exact-head snapshot
regenerates. Downstream sensing/topology/delegation/eval runs are tracked
by their owning repos — their results are never claimed here. No numbered
criterion from the Wave B scheme advances here: criterion 10 (capability
fallback with no authority widening) already closed in Wave B, and
proactivity/organization composition proof belongs to later waves.
