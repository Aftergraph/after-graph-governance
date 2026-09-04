# After Graph — Platform Governance

> The next engineering layer after Prompt → Context → Loop → Graph is **institutional control** — authority, delegation, budgets, audit, and evidence — portable across dynamic agent graphs.

**Status: PROVISIONAL BLUEPRINT** — awaiting owner approval before any repo-transfer.

## Modules

| Module | Repo | Role |
|--------|------|------|
| **Agent Workforce** | (in trust-gateway) | User/developer-facing product layer |
| **AIE** | [JonasAbde/aie](https://github.com/JonasAbde/aie) | Normative authority/institution semantics |
| **Trust Gateway** | [JonasAbde/trust-gateway](https://github.com/JonasAbde/trust-gateway) | Runtime enforcement plane |
| **works-execution** | [JonasAbde/works-execution](https://github.com/JonasAbde/works-execution) | Durable execution plane |
| **ISR Program** | (pending bootstrap) | Labs / Evals / Assurance |

## Governance

Everything extensible is a plugin. Everything consequential is governed.

- **Executable = Intersection(AIE policy, WORKS execution, TG enforcement)**
- AIE MAY define policies that TG and WORKS MUST follow
- WORKS NEEDS valid authorization from AIE before persisting
- Runtime (TG) HAS the authority to block or permit based on AIE policy
- ISR evaluates but does not automatically claim

## Cross-Repo Contracts (normative)

cpi/1.0, rab/1.0, identity/1.0, policy.token/1.0, secret.ref/1.0, shell.contracts/1.0, link.wire/1.0, pairing/1.0, brain.ns/1.0, release.rings/1.0, evidence.schema/1.1, kernel.budget/1.0, kernel.lifecycle/1.0

## Evidence Layers (correlation: mission_id + actionId)

| Layer | Producer | Format |
|---|---|---|
| L1 Action Audit | TG | hash-chain entry |
| L2 Execution Quittance | WE | content-addressed bundle |
| L3 Institutional Conformance | AIE | conformance vectors + PolicyDecisionRecord |
| L4 Scientific Evidence | ISR | STUDY-011/MISSION-Bench (Wilson CI, preregistration) |

## License

Apache-2.0
