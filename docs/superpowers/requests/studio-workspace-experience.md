# Build request: Studio workspace experience

Owner: `Aftergraph/studio`
Contract: human-governance authority binding (`docs/HUMAN-GOVERNANCE-V1.md` in after-graph-governance)

## What to build

Own the workspace experience state inside `Aftergraph/studio`: layout,
presence, and experience surfaces bound to the immutable tenant binding
held in the tenant/trust registry. Experience renders and organizes; it
mints no grants, keeps no ledger, changes no binding, and never crosses
tenants except through governed export/filter/new-identity/import.

## Acceptance

Conformance is pinned by the human-governance authority binding; the
binding's active-doc tests gate the seams. Studio proves experience
separation with its own tests, PR, CI, merge queue, and exact-head
evidence.

## Out of scope

Governance binds seams only. Governance implements nothing in
`Aftergraph/studio`; the canonical experience behavior belongs to the
Studio owners.
