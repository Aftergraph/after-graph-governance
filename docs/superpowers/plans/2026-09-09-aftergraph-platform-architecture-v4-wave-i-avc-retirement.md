# Aftergraph Platform Architecture V4 — Wave I AVC Retirement (Dissolution Ledger) Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development —
> fresh implementer per task, spec-compliance review first, code-quality review
> second, both must pass before the next task.

## 0. Scope (read first)

Wave I is **AVC retirement (dissolution ledger execution)** per the approved V4 design spec (§22 Wave I):

- execute the dissolution ledger;
- migrate canonical skills and Hermes adapter;
- remove active consumers;
- run Aftergraph-only Golden Mission;
- archive the legacy repository once every gate is evidenced.

Normative anchors (do not re-derive): V4 spec §9 (AVC primitive mapping — `Personal*` removed as a platform category, genericized targets `Entity`/`Relationship`/`Situation`/`Commitment`/`AttentionPolicy`/`AttentionCandidate`/`Opportunity`/`InteractionThread`/`ConsentRecord`/canonical domain policy/`AssistantAdvisor`/`AssistantProfile`); §15 brand and naming policy (`Aftergraph` masterbrand, canonical `@aftergraph/*`, no new `AVC`/`Autonomous Venture Company`/`avc-*`/`@avc/*`/`ABDE Platform` identifiers); §16 dissolution and extraction ledger (extraction baseline `18317c7b2eebcc08bb2a1b30d9118935d5832540` plus audited delta to legacy head, dispositions `MIGRATED_VERIFIED`/`MIGRATED_TRANSITIONAL`/`EXTRACT`/`RETIRE`/`HISTORY_ONLY`, machine-readable dissolution record, archive gates); §19 Golden Mission V1 (composed proof with adversarial branches); §22 Wave I scope above; §23 acceptance criteria — criterion 2 (no canonical active doc assigns platform ownership to retired AVC identities) and criterion 12 (dissolution ledger complete enough to prove every remaining active dependency or classify it as historical).

Canonical boundary (every task, no exceptions):

```text
Dissolution retires AVC identities ONLY through the ledger with every gate evidenced.
No AVC identity loses ownership while an active consumer or canonical doc still references it.
The governance repo NEVER executes archival/deletion.
The final legacy-repo archive action is REQUIRES_EXPLICIT_OWNER_AUTHORIZATION
(irreversible, outside autonomous execution).
```

Owner repos implement; governance pins ledger/gates/vectors/requests only and implements nothing in owner repos:

- `autonomous-venture-company` — phased extraction source (ledger dispositions applied, delta to legacy head audited, provenance retained);
- `skills-vault` — sole active canonical skill supply-chain owner (generic reusable `avc-*` skill migration target, legacy aliases/provenance as needed; persona/product-specific skills generalized or retired);
- `runtime` / `aie` / `trust-gateway` / `works-execution` — consumer-removal owners (active `@avc/*` dependencies, canonical service/contract ownership, Hermes execution adapter migration/reconciliation, tenant/workspace lifecycle and World/Situation/Commitment/Consent/Attention primitive extraction or retirement on their seams);
- `continuum` / `sentinel` — verifier allies (independent verification evidence for the Aftergraph-only Golden Mission, never self-attestation by the migrating party).

No new repo. No `retirement-platform`, `avc-brain`, or any other top-level repository.

Plane/fabric mapping (fixed, do not reinterpret):

- Dissolution ledger = conformance/retirement record (no execution ownership, no authority transport, no archival execution);
- `skills-vault` = skill migration evidence owner (migration PASS is necessary, never self-asserted by the legacy repo);
- Runtime/AIE/Trust Gateway/WORKS = consumer-removal enforcement planes on their own seams;
- `platform-event-ref/0.1` + canonical causal identifiers = correlation-only substrate (dedupe/correlation, never retirement authority).

No retirement/migration/consumer-removal/Golden Mission claims without ledger/gate evidence. Any owner-execution-dependent characterization work is evidence-gated and marked `BLOCKED_ON_OWNER_EXECUTION` (Task 6 appendix); it is never proven with mocks and never closes an evidence-independent gate.

This plan covers the **governance-owned** part: experimental ledger contract(s), acceptance vectors, the canonical retirement binding, the Aftergraph-only Golden Mission gate, and crisp cross-repo build request(s). Phased extraction, skill migration, consumer removal, Hermes reconciliation, live Golden Mission runs, and archival **implementation** live in the owner repos above and are specified here as follow-up request(s) with exact acceptance — never implemented from this repo.

Out of scope (do not touch):

- Wave H re-derivation — promotion-gate/trace/challenger semantics are inherited, never re-derived here;
- Waves A–G re-derivation — topology, fabric, context/world-state, lifecycle, proactivity, perception, interaction semantics are inherited, never re-derived here;
- Governance-executed archival/deletion — the governance repo NEVER archives or deletes the legacy repository; the final archive action is `REQUIRES_EXPLICIT_OWNER_AUTHORIZATION` and stays outside autonomous execution;
- Runtime PR #103 Muse supervision — do NOT duplicate it here; if a task overlaps, it references PR #103 and stays out.

No new top-level services, planes, fabrics, repos, or ownership. NO newly-minted AVC identifiers — this wave removes them through the ledger; historical records retain old names only where required for provenance (§15). Vector namespace `RET-*` is a Wave I conformance identifier, not a canonical platform ID.

Evidence-independent vs evidence-gated split (binding for all tasks below):

- Evidence-independent (prove now in governance with fixtures): dissolution ledger contract, skill/Hermes migration conformance, consumer-removal conformance, Aftergraph-only Golden Mission gate definition, retirement binding, fixtures, cross-repo requests, evidence record.
- Evidence-gated (marked `BLOCKED_ON_OWNER_EXECUTION`, never gated as PASS here): phased extraction execution in `autonomous-venture-company`, skill migration execution in `skills-vault`, consumer-removal/Hermes-reconciliation execution in `runtime`/`aie`/`trust-gateway`/`works-execution`, live Aftergraph-only Golden Mission results on exact heads, final legacy-repo archive action (`REQUIRES_EXPLICIT_OWNER_AUTHORIZATION`), any claim requiring owner-repo execution evidence not available in governance.

## Global constraints (every task)

- TDD task-by-task: failing test first, prove RED, minimum change, GREEN, regression, inspect diff, small focused commit. No weakened tests.
- Spec review + quality review gates per task: spec-compliance review first, code-quality review second; both must pass before the next task. Reviews are recorded on the branch (review-note or sign-off lines in the commit).
- Merge-queue only. No direct-to-main pushes, no bypass.
- Canonical boundary holds in every vector, doc, and fixture: dissolution retires AVC identities ONLY through the ledger with every gate evidenced; no AVC identity loses ownership while an active consumer or canonical doc still references it; governance NEVER executes archival/deletion; the final archive action is `REQUIRES_EXPLICIT_OWNER_AUTHORIZATION`.
- New vector kinds extend the harness with their own tests; the oracle stays independent of implementation internals and fails closed.
- No retirement/migration/consumer-removal/Golden Mission claims without ledger/gate evidence; evidence-gated items stay `BLOCKED_ON_OWNER_EXECUTION`.
- Do not re-derive §9 primitive mapping, §15 naming policy, §19 Golden Mission, or Wave A–H semantics; inherit the bindings.
- Repository-local green never claims cross-repo or platform conformance.

## Task 1 — dissolution ledger contract and acceptance vectors (ledger source of truth)

Evidence-independent. Fixtures only; no owner-execution evidence.

- [ ] **Step 1: RED.** Failing tests for `RET-001` (dissolution record carrying `source_repo`/`source_ref`/`source_path`/`disposition`/`target_owner`/`target_contract`/`active_consumers`/`compatibility_aliases`/`verification`/`deletion_gate` with a valid disposition `MIGRATED_VERIFIED`/`MIGRATED_TRANSITIONAL`/`EXTRACT`/`RETIRE`/`HISTORY_ONLY` pinned to extraction baseline `18317c7b2eebcc08bb2a1b30d9118935d5832540`, accept), `RET-002` (record retiring an AVC identity while `active_consumers` is non-empty, reject), `RET-003` (record retiring an AVC identity still referenced as owner by a canonical doc fixture, reject), `RET-004` (retirement asserted outside the ledger without a dissolution record, reject), `RET-005` (record with unknown disposition or missing `deletion_gate`, reject), `RET-006` (newly-minted `avc-*`/`@avc/*`/`AVC` identifier introduced as active, reject), `RET-007` (owner-execution/extraction-completion claim without owner evidence, reject-evidence-gated). Run → FAIL on missing contract/kind/vectors.
- [ ] **Step 2: GREEN.** Add `docs/contracts/avc-dissolution/0.1.json` (experimental: machine-readable dissolution record schema, disposition enum, baseline pin + delta-audit ref, `active_consumers`/canonical-doc ownership guards, no-new-AVC-identifier rule, archive-gate refs without executing archival), extend the conformance harness with an `avc_dissolution` kind validator plus its own tests, add the seven vectors to `docs/platform-conformance/v0.1/vectors.json`, wire new contract paths into `.github/workflows/platform-fabrics.yml`. Add fixtures (synthetic ledger records per disposition with empty/non-empty consumer lists and canonical-doc refs; no real archival). Re-run suite → PASS. Regression: fabrics suite, topology suite, exact-head suite.
- [ ] **Step 3: Commit** `feat(governance): pin avc-dissolution ledger acceptance`. Spec review + quality review recorded before the next task.

## Task 2 — skill/Hermes migration conformance (skills-vault target)

Evidence-independent. Fixtures only; no owner-execution evidence.

- [ ] **Step 1: RED.** Failing tests for `RET-010` (generic reusable `avc-*` skill ledgered `MIGRATED_VERIFIED`/`MIGRATED_TRANSITIONAL` with `target_owner: skills-vault`, Aftergraph canonical identifier, legacy alias/provenance retained, zero canonical skills owned by AVC fixture, accept), `RET-011` (skill migration asserting canonical ownership while the ledger still shows AVC as skill owner, reject), `RET-012` (persona/product-specific skill carried over verbatim without generalization or `RETIRE` disposition, reject), `RET-013` (Hermes execution adapter ledgered without `target_owner` migration/reconciliation and verification refs, reject), `RET-014` (skill migration minting a new active `avc-*`/`@avc/*` identifier, reject), `RET-015` (skill migration proven by legacy-repo self-attestation without skills-vault-side evidence ref, reject), `RET-016` (canonical contract still owned by AVC in a migration PASS claim, reject), `RET-017` (live migration-completion claim without owner execution evidence, reject-evidence-gated). Run → FAIL.
- [ ] **Step 2: GREEN.** Extend `docs/contracts/avc-dissolution/0.1.json` (or a versioned `0.2.json` if breaking; prefer additive) with skill/Hermes migration semantics, canonical-identifier + alias/provenance rules, and the skills-vault evidence path; extend the `avc_dissolution` harness validator plus its own tests; add the eight vectors; wire contract paths into CI. Suite → PASS. Regression: fabrics suite, topology suite, exact-head suite.
- [ ] **Step 3: Commit** `feat(governance): pin skill-hermes migration acceptance`. Spec review + quality review recorded before the next task.

## Task 3 — consumer-removal conformance (runtime/aie/trust-gateway/works-execution)

Evidence-independent. Fixtures only; no owner-execution evidence.

- [ ] **Step 1: RED.** Failing tests for `RET-020` (consumer ledgered with zero active `@avc/*` package dependencies except allowlisted provenance, zero canonical services owned by AVC, tenant/workspace lifecycle and World/Situation/Commitment/Consent/Attention primitive dispositions resolved, accept), `RET-021` (retirement PASS claimed while an active `@avc/*` dependency fixture remains outside the provenance allowlist, reject), `RET-022` (retirement PASS claimed while a canonical service is still owned by AVC, reject), `RET-023` (retirement PASS claimed while a current normative contract is still owned by AVC, reject), `RET-024` (ownership removed while an active consumer fixture still references the AVC identity, reject), `RET-025` (unclassified package/app/skill/ML/cell/infra asset fixture left without a disposition, reject), `RET-026` (consumer removal proven by repository-local green without cross-repo consumer evidence refs, reject), `RET-027` (live zero-consumer/zero-ownership claim without owner execution evidence, reject-evidence-gated). Run → FAIL.
- [ ] **Step 2: GREEN.** Extend the avc-dissolution contract with consumer-removal gate semantics, provenance-allowlist refs, and cross-repo evidence-ref rules; extend the harness validator plus its own tests; add the eight vectors; wire contract paths into CI. Suite → PASS. Regression: fabrics suite, topology suite, exact-head suite.
- [ ] **Step 3: Commit** `feat(governance): pin consumer-removal acceptance`. Spec review + quality review recorded before the next task.

## Task 4 — Aftergraph-only Golden Mission gate

Evidence-independent gate definition. Fixtures only; no live-mission evidence.

- [ ] **Step 1: RED.** Failing tests for `RET-030` (Golden Mission gate defined as Aftergraph-only: mission fixtures carry zero AVC dependencies, canonical identity preserved across the consequential chain, success plus fail-closed adversarial branches per §19 listed, accept), `RET-031` (Golden Mission PASS claimed with an `@avc/*` dependency in the mission path, reject), `RET-032` (Golden Mission proving only the happy path without refusal/revocation/crash-recovery/verifier-failure branches, reject), `RET-033` (Golden Mission with causal-identity mismatch across the consequential seam presented as PASS, reject), `RET-034` (Golden Mission verified by its own executor without independent verification, reject), `RET-035` (provenance unreachable after archive in the gate fixture, reject), `RET-036` (mission asserted against non-exact-head repos as platform PASS, reject), `RET-037` (live Aftergraph-only Golden Mission success claim without exact-head owner-repo evidence, reject-evidence-gated). Run → FAIL.
- [ ] **Step 2: GREEN.** Extend the avc-dissolution contract with the Aftergraph-only Golden Mission gate semantics (Aftergraph-only dependency rule, §19 adversarial branch list, causal-identity preservation, independent-verification and exact-head requirements, provenance-reachable-after-archive rule); extend the harness validator plus its own tests; add the eight vectors; wire contract paths into CI. Suite → PASS. Regression: fabrics suite, topology suite, exact-head suite.
- [ ] **Step 3: Commit** `feat(governance): pin aftergraph-only golden-mission gate`. Spec review + quality review recorded before the next task.

## Task 5 — Retirement binding

- [ ] **Step 1: RED.** Extend the active-doc consistency tests to require `docs/AVC-RETIREMENT-V1.md` (canonical, concise: dissolution retires AVC identities ONLY through the ledger with every gate evidenced; no AVC identity loses ownership while an active consumer or canonical doc still references it; governance NEVER executes archival/deletion; final legacy-repo archive action is `REQUIRES_EXPLICIT_OWNER_AUTHORIZATION` — irreversible, outside autonomous execution; owner repos `autonomous-venture-company` phased extraction, `skills-vault` skill migration target, `runtime`/`aie`/`trust-gateway`/`works-execution` consumer removal, `continuum`/`sentinel` verifier allies; governance pins ledger/gates/vectors/requests only; §9 primitive mapping + §15 no-new-AVC-identifiers + baseline `18317c7b2eebcc08bb2a1b30d9118935d5832540` + dispositions `MIGRATED_VERIFIED`/`MIGRATED_TRANSITIONAL`/`EXTRACT`/`RETIRE`/`HISTORY_ONLY` + §23 criteria 2 and 12; evidence-independent vs `BLOCKED_ON_OWNER_EXECUTION` split; no retirement/migration/removal/mission claims without ledger/gate evidence) and to forbid retirement-conflation phrases (retirement-outside-ledger, ownership-removed-with-active-consumer, canonical-doc-still-assigns-AVC-ownership, governance-executes-archival, archive-as-autonomous-action, new-avc-identifier-as-active, self-attested-migration, local-green-as-retirement, bypass-as-dissolution). Run → FAIL.
- [ ] **Step 2: GREEN.** Add the document (sourced from the V4 spec §§9/15/16/19/22/23, which stay as rationale); suite → PASS; no new authority, service, plane, fabric, repo, ownership, or AVC identifier anywhere in the diff.
- [ ] **Step 3: Commit** `docs(governance): bind avc-retirement seams`. Spec review + quality review recorded before the next task.

## Task 6 — Cross-repo build requests + Wave I close (with evidence-gated appendix)

- [ ] **Step 1: RED.** New `scripts/test_wave_i_requests_v0_1.py` asserting, for `avc-retirement.md` under `docs/superpowers/requests/`: the file exists; names its owning repos (`Aftergraph/autonomous-venture-company` for phased extraction, `Aftergraph/skills-vault` for skill migration, `Aftergraph/runtime` + `Aftergraph/aie` + `Aftergraph/trust-gateway` + `Aftergraph/works-execution` for consumer removal, with `continuum`/`sentinel` named as verifier allies); names its exact contract (`avc-dissolution/0.1` or its versioned successor, plus the binding); every named acceptance vector ID (`RET-001`…`RET-037` as applicable) exists in `docs/platform-conformance/v0.1/vectors.json`; states governance implements nothing in the owning repos and NEVER executes archival/deletion; restates the canonical boundary (ledger-only retirement with every gate evidenced; no ownership loss with active consumers/canonical-doc refs; final archive action `REQUIRES_EXPLICIT_OWNER_AUTHORIZATION`); and carries an evidence-gated appendix section listing owner-execution-dependent items explicitly marked `BLOCKED_ON_OWNER_EXECUTION` with no PASS claims. Run → FAIL.
- [ ] **Step 2: GREEN.** Write the request file to satisfy the test; suite → PASS. A request is done only when the test reads its acceptance back out of `vectors.json` — "issued" alone counts for nothing.
- [ ] **Step 3:** Add `docs/evidence/platform-architecture-v4-wave-i.json` (`topology_v2`, `ledger_vectors`, `migration_vectors`, `consumer_vectors`, `golden_mission_gate`, `seam_binding`, `request_content`, `evidence_gated_blocked`, `platform_fabrics_regression`; result PASS only when every evidence-independent gate above is green; `evidence_gated_blocked` lists each `BLOCKED_ON_OWNER_EXECUTION` item as BLOCKED, never PASS).
- [ ] **Step 4:** Full regression (all suites in Testing below) + commit `evidence(governance): close platform architecture v4 wave i`.

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
python scripts/test_wave_h_requests_v0_1.py
python scripts/test_wave_i_requests_v0_1.py
python scripts/test_world_state_conformance_v0_1.py
python scripts/test_governance_exact_head_truth.py
python scripts/platform_topology.py check
python scripts/platform_topology.py check-readme
bash -n scripts/org-state-verify.sh
```

## Completion gate

Wave I closes when: Tasks 1–4 gates green on the branch (evidence-independent vectors resolved against `vectors.json`, fixtures only, no owner-execution claims), the Task 5 seam-binding test green (canonical boundary + owner repos + §§9/15/16/19/22/23 lineage stated, no new plane/fabric/repo/ownership/AVC identifier), the Task 6 request-content test green (acceptance vector IDs resolved against `vectors.json`, canonical boundary + owner repos + `avc-dissolution/0.1` lineage stated, governance-never-archives + `REQUIRES_EXPLICIT_OWNER_AUTHORIZATION` stated, evidence-gated appendix present and marked `BLOCKED_ON_OWNER_EXECUTION`), evidence record PASS with `evidence_gated_blocked` BLOCKED (never PASS), branch merged through the normal merge queue with spec + quality reviews recorded per task, and a fresh `main` exact-head snapshot regenerates. The archive gate is satisfied short of the separately-authorized archive action: every ledger/consumer/mission gate evidenced, provenance reachable, with the irreversible legacy-repo archive left to explicit owner authorization outside autonomous execution. Downstream extraction/migration/removal/mission runs are tracked by the owner repos — their results are never claimed here. No owner-execution result advances here.
