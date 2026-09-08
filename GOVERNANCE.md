# After Graph — Governance

## Canonical Role Allocation

| Module | Role | Repo |
|---|---|---|
| Workforce | User/developer-facing product | trust-gateway (bots/agents + Adaptive Workspace) |
| AIE | Normative authority semantics | aie |
| Trust Gateway | Runtime enforcement plane | trust-gateway |
| WORKS | Durable execution plane | works-execution |
| ISR | Labs/Evals/Assurance | intelligence-systems-research |

## Claim Inheritance Rules

| Rule | Statement |
|---|---|
| R1 | AIE MAY define policies that WF, TG, and WORKS must follow |
| R2 | WORKS NEEDS valid authorization from AIE before persisting state |
| R3 | Runtime (TG) HAS authority to block/permit based on AIE policy |
| R4 | Executable = Intersection(AIE policy, WORKS execution, TG enforcement) |

## Non-Goals

- No code absorption between modules
- No automatic claim inheritance (AIE evidence ≠ ISE validation)
- No silent renaming of concepts across repos
- Each module retains separate claims, experiments, and publication lineage

## Decision Process

1. Proposal → 2. Review window → 3. Comment disposition → 4. Owner approval → 5. Implementation

## Merge Policy (decided 2026-09-08, permanent)

`required_approving_review_count` is **0** on `main`, by explicit owner decision.
Rationale: GitHub cannot distinguish self-approval (the author cannot approve
their own PR at platform level), so a mandatory-approval rule created an
artificial blocker without adding a real second pair of eyes.

The enforced bar instead:

- PR + automated/adversarial review with all findings answered in code or
  rebutted on record;
- all review conversations resolved;
- required CI green (including merge-group validation);
- merge through the merge queue only — no direct pushes, no bypasses.

Independent review remains available and valuable as evidence, but it is not
a universal merge prerequisite. No second GitHub identity may be created or
used to simulate one.
