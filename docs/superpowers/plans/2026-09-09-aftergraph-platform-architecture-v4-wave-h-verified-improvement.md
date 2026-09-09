# Aftergraph Platform Architecture V4 — Wave H Verified Improvement (Promotion Gates) Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development —
> fresh implementer per task, spec-compliance review first, code-quality review
> second, both must pass before the next task.

## 0. Scope (read first)

Wave H is **verified improvement (production trace schema + challenger flow + promotion gates)** per the approved V4 design spec (§22 Wave H):

- production trace schema;
- challenger candidate flow;
- routing/skill/workflow promotion gates;
- AFM/model promotion only through model research + registry evidence.

Normative anchors (do not re-derive): Wave E EVAL binding (`docs/PROACTIVITY-ORG-V1.md` and Wave E plan) for evaluator independence — evaluators never score their own execution — inherited here, not re-derived; V4 spec §22 Wave H scope above.

Canonical boundary (every task, no exceptions):

```text
Promotion moves NOTHING without independent verification.
Challenger never promotes itself; routing/skill/workflow/model promotion
only through gates + registry evidence; evaluators never score their own
execution (inherited Wave E EVAL binding, do not re-derive).
Trace/registry correlation != promotion authority; challenger result != gate PASS.
```

Owner repos implement; governance pins contracts/vectors/requests only and implements nothing in owner repos:

- `model-registry` — registry evidence owner for model/challenger promotion decisions;
- `afm` + `llm-research-development` — model promotion implementation (research evidence + registry write path);
- `skills-vault` — skill supply-chain owner (skill promotion gate implementation);
- `runtime` — routing/workflow gate implementation (routing + workflow promotion enforcement);
- `continuum` / `sentinel` — verifier allies (independent verification evidence, never the promoted party's self-attestation).

No new repo. No `promotion-platform`, `model-brain`, or any other top-level repository.

Plane/fabric mapping (fixed, do not reinterpret):

- Promotion gate = conformance/verification checkpoint (no execution ownership, no authority transport);
- `model-registry` = promotion evidence owner (registry PASS is necessary, never self-asserted);
- Runtime = routing/workflow gate enforcement plane;
- `platform-event-ref/0.1` + canonical causal identifiers = correlation-only substrate (dedupe/correlation, never promotion authority).

No production-trace/model-quality/latency/capability claims without production-trace/model evidence. Any production-trace characterization, live-model quality/latency/capability, or registry-bypass promotion characterization work is evidence-gated and marked `BLOCKED_ON_PROMOTION_EVIDENCE` (Task 6 appendix); it is never proven with mocks and never closes an evidence-independent gate.

This plan covers the **governance-owned** part: experimental contract(s), acceptance vectors, the canonical promotion-gates binding, and crisp cross-repo build request(s). Trace collection, challenger execution, gate enforcement, and registry **implementation** live in the owner repos above and are specified here as follow-up request(s) with exact acceptance — never implemented from this repo.

Out of scope (do not touch):

- Wave G re-derivation — voice/interaction semantics are inherited, never re-derived here;
- Wave I (AVC dissolution ledger execution, skill/Hermes migration, archival);
- Wave E re-derivation — evaluator-independence semantics are inherited from the Wave E EVAL binding, never re-derived here;
- Runtime PR #103 Muse supervision — do NOT duplicate it here; if a task overlaps, it references PR #103 and stays out.

No new top-level services, planes, fabrics, repos, or ownership. No new canonical AVC identifiers. Vector namespace `PROM-*` is a Wave H conformance identifier, not a canonical platform ID.

Evidence-independent vs evidence-gated split (binding for all tasks below):

- Evidence-independent (prove now in governance + owner repos with fixtures): trace schema contract, challenger non-self-promotion, gate + registry-evidence enforcement for routing/skill/workflow/model, evaluator-independence (Wave E inheritance), fixtures, cross-repo requests, evidence record.
- Evidence-gated (marked `BLOCKED_ON_PROMOTION_EVIDENCE`, never gated as PASS here): production-trace characterization, live-model quality/latency/capability claims, registry-bypass promotion characterization, any claim requiring production traces or model evidence not available in governance.

## Global constraints (every task)

- TDD task-by-task: failing test first, prove RED, minimum change, GREEN, regression, inspect diff, small focused commit. No weakened tests.
- Spec review + quality review gates per task: spec-compliance review first, code-quality review second; both must pass before the next task. Reviews are recorded on the branch (review-note or sign-off lines in the commit).
- Merge-queue only. No direct-to-main pushes, no bypass.
- Canonical boundary holds in every vector, doc, and fixture: promotion moves nothing without independent verification; challenger never promotes itself; routing/skill/workflow/model promotion only through gates + registry evidence; evaluators never score their own execution (Wave E inheritance).
- New vector kinds extend the harness with their own tests; the oracle stays independent of implementation internals and fails closed.
- No production-trace/model characterization claims without production-trace/model evidence; evidence-gated items stay `BLOCKED_ON_PROMOTION_EVIDENCE`.
- Do not re-derive Wave E evaluator-independence semantics; inherit the binding.
- Repository-local green never claims cross-repo or platform conformance.

## Task 1 — promotion-trace/0.1 contract and acceptance vectors (trace schema)

Evidence-independent. Fixtures only; no production-trace/model evidence.

- [ ] **Step 1: RED.** Failing tests for `PROM-001` (production trace carrying schema'd observation/correlation content with promotion authority referenced outside the trace in gate/registry-owned stores, accept), `PROM-002` (trace embedding promotion authority/grant, reject), `PROM-003` (trace presented as gate PASS by itself without gate + registry evidence, reject), `PROM-004` (trace admitted without tenant scoping/classification, reject), `PROM-005` (trace correlation presented as registry evidence, reject), `PROM-006` (challenger trace scored by its own executor — evaluator-independence, reject, inherited Wave E binding), `PROM-007` (production-trace characterization claim without production evidence, reject-evidence-gated). Run → FAIL on missing contract/kind/vectors.
- [ ] **Step 2: GREEN.** Add `docs/contracts/promotion-gates/0.1.json` (experimental: trace schema refs, gate/registry refs without embedding authority, tenant scoping, classification, inherited evaluator-independence), extend the conformance harness with a `promotion_gates` kind validator plus its own tests, add the seven vectors to `docs/platform-conformance/v0.1/vectors.json`, wire new contract paths into `.github/workflows/platform-fabrics.yml`. Add fixtures (synthetic trace/challenger/gate payloads with outside-trace authority refs; no real production traces). Re-run suite → PASS. Regression: fabrics suite, topology suite, exact-head suite.
- [ ] **Step 3: Commit** `feat(governance): pin promotion-trace acceptance`. Spec review + quality review recorded before the next task.

## Task 2 — challenger flow (non-self-promotion + independent verification)

Evidence-independent. Fixtures only; no production-trace/model evidence.

- [ ] **Step 1: RED.** Failing tests for `PROM-010` (challenger candidate registered with disposable candidate identity and routed to an independent gate/verifier, accept), `PROM-011` (challenger promoting itself without gate + registry evidence, reject), `PROM-012` (challenger result presented as promotion without independent verification by continuum/sentinel-ally or gate, reject), `PROM-013` (challenger bypassing `model-registry` evidence for model promotion, reject), `PROM-014` (challenger scored by its own evaluator/executor, reject — inherited Wave E binding), `PROM-015` (challenger lineage attached to traces/derivatives and propagated, accept), `PROM-016` (challenger identity reused as durable authority across promotions, reject), `PROM-017` (production-trace win-rate/quality claim without production evidence, reject-evidence-gated). Run → FAIL.
- [ ] **Step 2: GREEN.** Extend `docs/contracts/promotion-gates/0.1.json` (or a versioned `0.2.json` if breaking; prefer additive) with challenger registration/flow semantics, non-self-promotion rules, and the independent-verification path; extend the `promotion_gates` harness validator plus its own tests; add the eight vectors; wire contract paths into CI. Suite → PASS. Regression: fabrics suite, topology suite, exact-head suite.
- [ ] **Step 3: Commit** `feat(governance): pin challenger-flow acceptance`. Spec review + quality review recorded before the next task.

## Task 3 — routing/skill/workflow gates (evidence-independent)

Evidence-independent. Fixtures only; no production-trace/model evidence.

- [ ] **Step 1: RED.** Failing tests for `PROM-020` (routing promotion through runtime gate + registry/verifier evidence with authority re-admitted at promotion, accept), `PROM-021` (routing promotion by challenger self-assertion, reject), `PROM-022` (skill promotion without `skills-vault` supply-chain gate evidence, reject), `PROM-023` (workflow promotion without runtime gate evidence, reject), `PROM-024` (promotion implemented by moving authority into the challenger/trace payload, reject), `PROM-025` (stale/superseded challenger evidence promoted without re-verification, reject), `PROM-026` (gate PASS claimed from repository-local green without cross-repo gate evidence, reject), `PROM-027` (production-trace-gated routing/skill/workflow quality claim without production evidence, reject-evidence-gated). Run → FAIL.
- [ ] **Step 2: GREEN.** Extend the promotion-gates contract with routing/skill/workflow gate semantics, no-authority-transport, supply-chain lineage, and re-verification rules; extend the harness validator plus its own tests; add the eight vectors; wire contract paths into CI. Suite → PASS. Regression: fabrics suite, topology suite, exact-head suite.
- [ ] **Step 3: Commit** `feat(governance): pin routing-skill-workflow gate acceptance`. Spec review + quality review recorded before the next task.

## Task 4 — model promotion gate (registry-evidence-only)

Evidence-independent. Fixtures only; no production-trace/model evidence.

- [ ] **Step 1: RED.** Failing tests for `PROM-030` (model promotion through `llm-research-development` research evidence + `afm` implementation path + `model-registry` registry PASS with independent verification, accept), `PROM-031` (model promotion without `model-registry` evidence, reject), `PROM-032` (model promotion on challenger self-attestation alone, reject), `PROM-033` (model evaluator scoring its own execution, reject — inherited Wave E binding), `PROM-034` (registry PASS forged/embedded in the challenger payload instead of registry-owned, reject), `PROM-035` (model rollback/supersede without registry evidence update, reject), `PROM-036` (live-model quality/latency/capability claim without production/model evidence, reject-evidence-gated), `PROM-037` (registry-bypass emergency promotion without gate evidence, reject). Run → FAIL.
- [ ] **Step 2: GREEN.** Extend the promotion-gates contract with model-promotion registry-evidence semantics; extend the harness validator plus its own tests; add the eight vectors; wire contract paths into CI. Suite → PASS. Regression: fabrics suite, topology suite, exact-head suite.
- [ ] **Step 3: Commit** `feat(governance): pin model-promotion acceptance`. Spec review + quality review recorded before the next task.

## Task 5 — Promotion-gates binding

- [ ] **Step 1: RED.** Extend the active-doc consistency tests to require `docs/PROMOTION-GATES-V1.md` (canonical, concise: promotion moves nothing without independent verification; challenger never promotes itself; routing/skill/workflow/model promotion only through gates + registry evidence; evaluators never score their own execution inherited from Wave E, not re-derived; owner repos model-registry/afm/llm-research-development for model promotion, skills-vault for skill supply chain, runtime for routing/workflow gates, continuum/sentinel as verifier allies; governance pins contracts/vectors/requests only; `platform-event-ref/0.1` correlation-only; evidence-independent vs `BLOCKED_ON_PROMOTION_EVIDENCE` split; no production-trace/model claims without production/model evidence) and to forbid promotion-conflation phrases (challenger-as-promoter, self-promotion-as-gate, trace-as-authority, correlation-as-evidence, registry-embedded-as-registry-owned, evaluator-as-executee-scorer, local-green-as-promotion, bypass-as-promotion). Run → FAIL.
- [ ] **Step 2: GREEN.** Add the document (sourced from the V4 spec §22 Wave H, which stays as rationale); suite → PASS; no new authority, service, plane, fabric, repo, ownership, or AVC identifier anywhere in the diff.
- [ ] **Step 3: Commit** `docs(governance): bind promotion-gates seams`. Spec review + quality review recorded before the next task.

## Task 6 — Cross-repo build requests + Wave H close (with evidence-gated appendix)

- [ ] **Step 1: RED.** New `scripts/test_wave_h_requests_v0_1.py` asserting, for `promotion-gates.md` under `docs/superpowers/requests/`: the file exists; names its owning repos (`Aftergraph/model-registry`, `Aftergraph/afm`, `Aftergraph/llm-research-development` for model promotion, `Aftergraph/skills-vault` for skill supply chain, `Aftergraph/runtime` for routing/workflow gates, with `continuum`/`sentinel` named as verifier allies); names its exact contract (`promotion-gates/0.1` or its versioned successor, plus the binding); every named acceptance vector ID (`PROM-001`…`PROM-037` as applicable) exists in `docs/platform-conformance/v0.1/vectors.json`; states governance implements nothing in the owning repos; restates the canonical boundary (promotion moves nothing without independent verification; challenger never promotes itself; gates + registry evidence only; evaluators never score their own execution as Wave E inheritance); and carries an evidence-gated appendix section listing production-trace/model characterization items explicitly marked `BLOCKED_ON_PROMOTION_EVIDENCE` with no PASS claims. Run → FAIL.
- [ ] **Step 2: GREEN.** Write the request file to satisfy the test; suite → PASS. A request is done only when the test reads its acceptance back out of `vectors.json` — "issued" alone counts for nothing.
- [ ] **Step 3:** Add `docs/evidence/platform-architecture-v4-wave-h.json` (`topology_v2`, `trace_vectors`, `challenger_vectors`, `gate_vectors`, `model_vectors`, `seam_binding`, `request_content`, `evidence_gated_blocked`, `platform_fabrics_regression`; result PASS only when every evidence-independent gate above is green; `evidence_gated_blocked` lists each `BLOCKED_ON_PROMOTION_EVIDENCE` item as BLOCKED, never PASS).
- [ ] **Step 4:** Full regression (all suites in Testing below) + commit `evidence(governance): close platform architecture v4 wave h`.

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
python scripts/test_world_state_conformance_v0_1.py
python scripts/test_governance_exact_head_truth.py
python scripts/platform_topology.py check
python scripts/platform_topology.py check-readme
bash -n scripts/org-state-verify.sh
```

## Completion gate

Wave H closes when: Tasks 1–4 gates green on the branch (evidence-independent vectors resolved against `vectors.json`, fixtures only, no production-trace/model claims), the Task 5 seam-binding test green (canonical boundary + Wave E inheritance + owner repos stated, no new plane/fabric/AVC identifier), the Task 6 request-content test green (acceptance vector IDs resolved against `vectors.json`, canonical boundary + owner repos + `promotion-gates/0.1` lineage stated, evidence-gated appendix present and marked `BLOCKED_ON_PROMOTION_EVIDENCE`), evidence record PASS with `evidence_gated_blocked` BLOCKED (never PASS), branch merged through the normal merge queue with spec + quality reviews recorded per task, and a fresh `main` exact-head snapshot regenerates. Downstream trace/challenger/gate runs are tracked by the owner repos — their results are never claimed here. No production-trace/model characterization result advances here. Wave E evaluator-independence semantics are inherited, not re-proven here.
