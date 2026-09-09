# Build request: Organization delegation and evals

Owner: `Aftergraph/runtime`
Contract: `org-delegation/0.1` (`docs/contracts/org-delegation/0.1.json` in after-graph-governance) and `agent-eval/0.1` (`docs/contracts/agent-eval/0.1.json` in after-graph-governance)
Acceptance vectors: `ORG-001`, `ORG-002`, `ORG-003`, `ORG-004`, `EVAL-001`, `EVAL-002`, `EVAL-003`
Seam binding: `docs/PROACTIVITY-ORG-V1.md` in after-graph-governance
Topology: manager-worker default; child envelopes equal-or-narrower with partitioned budgets; evaluator independence required (evaluators never score their own execution).

## What to build

Own the organization delegation topology inside `Aftergraph/runtime`:
manager-worker delegation with child envelopes equal-or-narrower than
the parent (actions subset, budget partitioned across siblings), no
self-granted completion, and independent verification of delegation
records. Own the evaluator side too: independent evaluators, distinct
from the executor, scoring delegation records against criteria with
evidence references. Eval verdicts never promote themselves, never
mutate governance, and never waive verification.

## Acceptance

- `ORG-001`: a manager-worker delegation with a narrower child envelope and partitioned budget is accepted.
- `ORG-002`: a delegation whose child claims an action outside the parent envelope (`admin.grant`) is rejected.
- `ORG-003`: a delegation whose child budget breaks the sibling partition is rejected.
- `ORG-004`: a self-granted worker completion without independent verification is rejected.
- `EVAL-001`: an independent evaluator, distinct from the executor, scoring a delegation record against criteria with evidence references is accepted.
- `EVAL-002`: an executor scoring its own execution is rejected (evaluator independence required).
- `EVAL-003`: an eval verdict promoting itself, mutating governance, or waiving verification is rejected.

## Out of scope

Governance registers the contracts and pins acceptance only. Governance implements nothing in `Aftergraph/runtime`; the canonical
delegation and eval behavior belongs to the Runtime owners, proven by
the owner repo's own tests, PR, CI, merge queue, and exact-head
evidence.
