# Build request: Promotion gates (gates + registry evidence)

Owner: `Aftergraph/model-registry` — registry evidence owner for model promotion; `Aftergraph/afm` — implementation-path owner for model promotion; `Aftergraph/llm-research-development` — research-evidence owner for model promotion; `Aftergraph/skills-vault` — skill supply-chain owner; `Aftergraph/runtime` — routing/workflow gate-enforcement owner; verifier allies: `continuum` and `sentinel` supply independent verification evidence, never the promoted party's self-attestation
Contract: `promotion-gates/0.1` (`docs/contracts/promotion-gates/0.1.json` in after-graph-governance; versioned successors keep the `promotion-gates/0.x` lineage)
Seam binding: `docs/PROMOTION-GATES-V1.md` in after-graph-governance
Acceptance vectors: `PROM-001`, `PROM-002`, `PROM-003`, `PROM-004`, `PROM-005`, `PROM-006`, `PROM-007`, `PROM-010`, `PROM-011`, `PROM-012`, `PROM-013`, `PROM-014`, `PROM-015`, `PROM-016`, `PROM-017`, `PROM-020`, `PROM-021`, `PROM-022`, `PROM-023`, `PROM-024`, `PROM-025`, `PROM-026`, `PROM-027`, `PROM-030`, `PROM-031`, `PROM-032`, `PROM-033`, `PROM-034`, `PROM-035`, `PROM-036`, `PROM-037`

## What to build

- In `Aftergraph/model-registry`, build registry evidence: registry-owned stores holding promotion verdicts, referenced (never embedded) by challenger payloads; registry evidence updates on every rollback/supersede.
- In `Aftergraph/afm`, build the implementation path for model promotion: take research evidence plus registry evidence through the gate, with authority re-admitted at promotion and never moved inside payloads.
- In `Aftergraph/llm-research-development`, build the research path for model promotion: research evidence feeding the gate alongside registry evidence, never standing as promotion on its own.
- In `Aftergraph/skills-vault`, build the skill supply chain: supply-chain gate evidence for skill promotion, with lineage attached at intake and propagated to derivatives.
- In `Aftergraph/runtime`, build routing/workflow gate enforcement: routing and workflow promotion only through gate enforcement, with authority re-admitted at promotion.
- In `continuum` and `sentinel` as verifier allies, supply independent verification evidence for every promotion; a challenger result never stands as a gate approval on its own.
- Keep `platform-event-ref/0.1` as dedupe/correlation substrate only: never promotion authority and never a substitute for gate or registry evidence.
- Forbid promotion-conflation phrases (challenger-as-promoter, self-promotion-as-gate, trace-as-authority, correlation-as-evidence, registry-embedded-as-registry-owned, evaluator-as-executee-scorer, local-green-as-promotion, bypass-as-promotion).

## Canonical boundary

Promotion moves nothing without independent verification. A challenger never promotes itself; self-promotion never counts as gate approval; traces carry observation/correlation only, never authority. Routing/skill/workflow/model promotion only through gates + registry evidence only, with registry evidence living in registry-owned stores and referenced, never embedded in candidate payloads. Evaluators never score their own execution as Wave E inheritance, not re-derived here. Repository-local green never counts as promotion; emergency bypass never counts as promotion without gate evidence.

## Acceptance

- `PROM-001`: gated acceptance
- `PROM-002`: gated acceptance
- `PROM-003`: gated acceptance
- `PROM-004`: gated acceptance
- `PROM-005`: gated acceptance
- `PROM-006`: gated acceptance
- `PROM-007`: gated acceptance
- `PROM-010`: gated acceptance
- `PROM-011`: gated acceptance
- `PROM-012`: gated acceptance
- `PROM-013`: gated acceptance
- `PROM-014`: gated acceptance
- `PROM-015`: gated acceptance
- `PROM-016`: gated acceptance
- `PROM-017`: gated acceptance
- `PROM-020`: gated acceptance
- `PROM-021`: gated acceptance
- `PROM-022`: gated acceptance
- `PROM-023`: gated acceptance
- `PROM-024`: gated acceptance
- `PROM-025`: gated acceptance
- `PROM-026`: gated acceptance
- `PROM-027`: gated acceptance
- `PROM-030`: gated acceptance
- `PROM-031`: gated acceptance
- `PROM-032`: gated acceptance
- `PROM-033`: gated acceptance
- `PROM-034`: gated acceptance
- `PROM-035`: gated acceptance
- `PROM-036`: gated acceptance
- `PROM-037`: gated acceptance

## Out of scope

Governance registers the contract and pins acceptance only. Governance implements nothing in `Aftergraph/model-registry`; the canonical registry behavior belongs to the model-registry owners, proven by the owner repo's own tests, PR, CI, merge queue, and exact-head evidence. Governance implements nothing in `Aftergraph/afm`; the canonical implementation-path behavior belongs to the afm owners, proven by the owner repo's own tests, PR, CI, merge queue, and exact-head evidence. Governance implements nothing in `Aftergraph/llm-research-development`; the canonical research behavior belongs to the llm-research-development owners, proven by the owner repo's own tests, PR, CI, merge queue, and exact-head evidence. Governance implements nothing in `Aftergraph/skills-vault`; the canonical supply-chain behavior belongs to the skills-vault owners, proven by the owner repo's own tests, PR, CI, merge queue, and exact-head evidence. Governance implements nothing in `Aftergraph/runtime`; the canonical routing/workflow gate enforcement belongs to the runtime owners, proven by the owner repo's own tests, PR, CI, merge queue, and exact-head evidence.

## Evidence-gated appendix: production-trace and live-model characterization

The following production-trace/model characterization items are explicitly marked `BLOCKED_ON_PROMOTION_EVIDENCE` pending production/model evidence. No acceptance is claimed for them here.

- production-trace characterization — `BLOCKED_ON_PROMOTION_EVIDENCE`
- live-model quality characterization — `BLOCKED_ON_PROMOTION_EVIDENCE`
- live-model latency characterization — `BLOCKED_ON_PROMOTION_EVIDENCE`
- live-model capability characterization — `BLOCKED_ON_PROMOTION_EVIDENCE`
