# Aftergraph Frontier V1 — Experimental Lifecycle and Promotion

Status: Canonical lifecycle binding.
Applies to: capabilities, protocols, models, skills, routing strategies, agent architectures, UI patterns, and cross-repo feature families.

## Purpose

Aftergraph Frontier is a lifecycle/program, not a repository, service, plane, authority, runtime, database, or execution owner.

It answers whether a candidate has earned promotion into its canonical owner. It never executes work and never carries authority.

## Lifecycle

```text
EXPERIMENTAL -> FRONTIER -> CANDIDATE -> CANONICAL
                     \-> QUARANTINED
CANONICAL -> DEPRECATED -> ARCHIVED
```

- **EXPERIMENTAL** — exploratory; no production maturity claim.
- **FRONTIER** — owner hypothesis, contracts, threat model and falsification/eval plan exist.
- **CANDIDATE** — architecture surface is stable enough for independent promotion evidence.
- **CANONICAL** — applicable promotion gates passed and canonical ownership is recorded.
- **QUARANTINED** — blocked from promotion/use pending explicit evidence or remediation.
- **DEPRECATED** — canonical but superseded; compatibility/retirement rules apply.
- **ARCHIVED** — retained only for provenance/history.

SemVer and lifecycle are independent. A package may be version 3.2.0 and still be FRONTIER; a 1.0.0 contract may be CANONICAL.

## Capability-level maturity

Promotion is per capability/contract surface, not per repository or marketing project name.

A family may therefore contain both canonical and frontier capabilities at the same time.

## Promotion law

Frontier inherits `PROMOTION-GATES-V1.md` without re-deriving it:

1. A candidate never promotes itself.
2. Repository-local green is necessary evidence, never sufficient promotion evidence.
3. Correlation/traces carry observation/provenance, never authority.
4. Registry/gate evidence is referenced from the owning store, never embedded as self-asserted PASS.
5. Evaluators never score their own execution.
6. Independent verification is required for promotion.
7. Authority is re-admitted by the canonical owner at use time; it is never transported through Frontier payloads.
8. Superseded evidence requires re-verification.

## Required Frontier record

Every FRONTIER or CANDIDATE item must declare:

- candidate id and subject class;
- proposed canonical owner(s);
- claims and explicit non-claims;
- affected contract families;
- threat/failure model;
- falsification/evaluation references;
- compatibility/rollback boundary;
- independent verifier reference when promotion is requested;
- promotion gate/registry evidence references when promoted.

## Non-ownership

Frontier MUST NOT own:

- AIE authority;
- Trust Gateway admission, secrets or approvals;
- Runtime orchestration/execution identity;
- WORKS durable work/execution;
- Sentinel/Continuum independent verification verdicts;
- canonical domain truth owned by another repository;
- HomeOS/FIHIM operator truth.

No new top-level repository is created by this lifecycle binding.

## Economic Graph graduation

Economic Graph v1 is the first capability-family using this lifecycle explicitly.

Its v1 read-only/simulation surfaces are canonical. Live settlement, transaction signing, custody and autonomous spending remain non-canonical as recorded in `docs/contracts/economic-graph/1.0/capabilities.json`.
