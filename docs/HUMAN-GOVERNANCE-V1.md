# Human Governance V1 — Canonical Authority and Workspace Binding

Status: Canonical for human-governance authority meaning and workspace
seams. Topology: `docs/platform-topology/2.0.json`.

**Design rationale:** V4 spec §§5.2–5.3/12 (rationale only; this document is
normative for the binding).

Human governance flows through grants and enforcement, never through labels
or surfaces. Nothing here creates a new authority, role, or owner.

| Seam | V4 owner | Binding |
| --- | --- | --- |
| Authority meaning and grants | `aie` | Owns principal/authority semantics: delegation, mission envelopes, budgets, authority lifecycle, revocation semantics, and what human governance means. AIE grants are the authority truth; a principal may execute only what a live grant covers. |
| Human role labels | `aie` | Labels such as `owner`, `reviewer`, `auditor`, `operator` are convenience templates for assigning grants. A label alone permits nothing; only the AIE grant issued under it does. Changing a label never changes authority without a corresponding grant change. |
| Admission and enforcement | `trust-gateway` | Enforces AIE grants at runtime: session binding, tenant isolation, admission, approvals, consent enforcement, tenant lifecycle truth, and the Consent Ledger. Owns no mission planning, durable work, or verification. |
| Workspace scope and binding | `trust-gateway` | The tenant/trust registry owns workspace identity, scope, membership, and the immutable tenant binding. Cross-workspace movement across tenants is governed export/filter/new-identity/import with provenance, never an in-place binding mutation. |
| Workspace experience | `studio` (primary), `wi-frontend` (specialist) | Owns workspace layout, presence, and experience state. Experience renders and organizes; it mints no grants, keeps no ledger, and changes no binding. |
| Observation intake | `wi-backend` | Source-neutral observations feed commitments and WorkItems. Intake observes; it never decides authority. |
| Execution | `runtime` | Executes only within admitted authority under live grants and consent. Revocation of the underlying grant or consent ends effective use. |

Invariants (restated, not extended):

- Role labels never equal authority.
- Consent != Authority.
- Revocation invalidates downstream effective use; audit keeps its own
  retention law and is never silently erased.
- Fail closed on consequential ambiguity.
