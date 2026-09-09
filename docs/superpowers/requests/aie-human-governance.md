# Build request: AIE human governance

Owner: `Aftergraph/aie`
Contract: human-governance authority binding (`docs/HUMAN-GOVERNANCE-V1.md` in after-graph-governance)

## What to build

Own the human-governance authority meaning inside `Aftergraph/aie`:
principal and authority semantics, delegation, mission envelopes, budgets,
authority lifecycle, and revocation semantics. Human role labels such as
`owner`, `reviewer`, `auditor`, `operator` remain convenience templates for
assigning grants; a label alone permits nothing, and only the AIE grant
issued under it is the authority truth.

## Acceptance

Conformance is pinned by the human-governance authority binding; the
binding's active-doc tests gate the seams. AIE proves grant semantics with
its own tests, PR, CI, merge queue, and exact-head evidence.

## Out of scope

Governance binds meaning only. Governance implements nothing in
`Aftergraph/aie`; the canonical authority behavior belongs to the AIE
owners.
