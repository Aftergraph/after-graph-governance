# Cross-Repo Contract Register

> Normative contracts for the After Graph platform — ownership and consumption map.
> Naming reconciled to the 5-repo model: trust-gateway (TG), works-execution (WE), aie (AIE),
> intelligence-systems-research (ISR), after-graph-governance (this repo).
> Note: 'avc-main' in earlier drafts maps to the ISR program workspace for program-level contracts.

## Register

| Contract | Normative | Owner Repo | Consumer Repos |
|---|---|---|---|
| `cpi/1.0` | Yes | ISR (program) | TG, AIE, WE |
| `rab/1.0` | Normative | ISR (program) | TG, AIE, WE |
| `identity/1.0` | Normative | AIE | TG, WE |
| `policy.token/1.0` | Normative | TG | AIE, WE |
| `secret.ref/1.0` | Normative | TG | AIE, WE |
| `shell.contracts/1.0` | Normative | WE | TG, AIE |
| `link.wire/1.0` | Normative | WE | TG, AIE |
| `pairing/1.0` | Normative | WE | TG, AIE |
| `brain.ns/1.0` | Normative | AIE | TG, WE |
| `release.rings/1.0` | Normative | after-graph-governance | WE, AIE, TG |
| `evidence.schema/1.1` | Normative | WE | TG, AIE, ISR |
| `kernel.budget/1.0` | Normative | WE | TG, AIE |
| `kernel.lifecycle/1.0` | Normative | ISR | TG, WE, AIE |

## AIE Binding Claims

| Binding | Description | Owner |
|---|---|---|
| MCP | Model Context Protocol binding | AIE |
| A2A | Agent-to-Agent protocol binding | AIE |
| SPIFFE-OIDC | SPIFFE + OIDC auth binding | AIE |
| OPA | Open Policy Agent integration | AIE |
| Otel | OpenTelemetry integration | AIE |
| Temporal | Temporal workflow integration | AIE |
| OWASP-ACS | OWASP ASV standard alignment | AIE |

## TG Runtime Guarantees (6)

| # | Guarantee |
|---|---|
| 1 | Policy enforcement at runtime |
| 2 | Runtime compliance verification |
| 3 | Policy propagation |
| 4 | Evidence-lag handling |
| 5 | Cross-module audit trail |
| 6 | Trust boundary enforcement |

## Boundary Charter

See `PLATFORM-BOUNDARY-CHARTER-v0.1.md` in the ISR repo (`docs/`) for the
"Everything extensible is a plugin. Everything consequential is governed." charter:
safe declarative primitives (Card/Table/Form/Chart/Timeline/Approval/Progress/Artifact)
vs sandboxed app runtime; plugins never receive authority by installation —
authority flows only through AIE (normative) + TG (enforcement) + WORKS (durable execution).
