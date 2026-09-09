# Promotion Gates V1 — Canonical Promotion-Gate Binding

Status: Canonical for promotion-gate seams.
Topology: `docs/platform-topology/2.0.json`.

**Design rationale:** V4 spec §§7.8/21/22 (rationale only; this document is
normative for the binding). Evaluator independence is inherited
from the Wave E binding in `docs/PROACTIVITY-ORG-V1.md`, not re-derived here.
Candidate-pipeline semantics stay owned by that binding (`wi-backend` /
`wi-frontend` candidate flow, `runtime` decision); this binding adds no
candidate pipeline and re-derives none of it.

A promotion gate is a conformance/verification checkpoint: no execution
ownership, no authority transport. Promotion moves nothing without independent
verification; routing/skill/workflow/model promotion only through gates +
registry evidence.

Canonical boundary: a challenger never promotes itself; self-promotion never
counts as gate approval; traces carry observation/correlation only, never
authority; correlation never counts as evidence; a registry PASS embedded in a
candidate payload never counts as registry-owned evidence; evaluators never
score their own execution (Wave E inheritance); repository-local green never
counts as promotion; emergency bypass never counts as promotion without gate
evidence. Nothing here creates a new authority, service, owner, or repo.

| Seam | V4 owner | Binding |
| --- | --- | --- |
| Model promotion | `model-registry`, `afm`, `llm-research-development` | Model promotion only through research evidence plus a registry-owned PASS with independent verification; a candidate payload never carries its own PASS. |
| Skill supply chain | `skills-vault` | Skill promotion only through supply-chain gate evidence; lineage is attached at intake and propagated to derivatives. |
| Routing/workflow gates | `runtime` | Routing and workflow promotion only through gate enforcement with authority re-admitted at promotion, never moved inside payloads. |
| Independent verification | `continuum`, `sentinel` | Verifier allies supply verification evidence; never the promoted party's self-attestation. |
| Correlation substrate | — | `platform-event-ref/0.1` stays dedupe/correlation only: never promotion authority and never a substitute for gate or registry evidence. |
| Governance pinning | after-graph-governance | Governance pins the experimental contract, acceptance vectors, and cross-repo requests only, and implements nothing in owner repos. |

Evidence split: trace schema, non-self-promotion, gate + registry-evidence
enforcement, and Wave E evaluator independence are evidence-independent and
proven with fixtures. Production-trace characterization, live-model
quality/latency/capability claims, and registry-bypass promotion
characterization are marked `BLOCKED_ON_PROMOTION_EVIDENCE`; no such claim
appears here, and none is proven with mocks.

Invariants (restated, not extended):

- Promotion moves nothing without independent verification.
- A challenger never promotes itself; a challenger result never stands as
  a gate PASS on its own.
- Routing/skill/workflow/model promotion only through gates + registry evidence.
- Evaluators never score their own execution (inherited, not re-derived).
- Trace/registry correlation moves observation/provenance, never authority.
- Registry-owned evidence lives in registry-owned stores and is referenced,
  never embedded.
- Repository-local green never advances a promotion; bypass never advances one
  without gate evidence.
- No production-trace/model claim without production/model evidence.
