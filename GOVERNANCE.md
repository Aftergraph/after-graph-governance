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
