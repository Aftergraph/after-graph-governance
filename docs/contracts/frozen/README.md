# Cross-Repo Contract Register — Frozen Schemas

> This directory mirrors the SHA-pinned contract schemas from
> `works-execution/contracts/` (the works-api contract freeze system).
>
> **Canonical source:** `works-execution/contracts/schemas/` — SHA-256 pinned in
> `works-execution/contracts/manifest.json`. GOV holds the mirror so the
> cross-repo contract register (see `cross-repo-contracts.md`) can point at
> concrete schema files instead of names-only.
>
> **Provenance:** `frozen/manifest.json` is a verbatim copy of the WORKS
> manifest. `frozen/manifest.sha256` is the WORKS-side integrity pin. Do not
> edit these files in GOV — changes must land in works-execution first, then
> be re-mirrored.

## Relationship to the 15-Concept Reconciliation Matrix

| Matrix Item | Frozen Schema | Status |
|---|---|---|
| #1 Mission | (this contract: `mission-state/1.0.json`) | GOV-native, not WORKS-frozen |
| #2 Policy | `policy.token.schema.json` (policy.token/1.0) | Frozen in WORKS |
| #3 Capability | `cpi.schema.json` (cpi/1.0) | Frozen in WORKS |
| #4 Budget | `kernel.budget.schema.json` (kernel.budget/1.0) | Frozen in WORKS |
| #5 Identity | `identity.schema.json` (identity/1.0) | Frozen in WORKS |
| #8 Evidence | `evidence.schema.schema.json` (evidence.schema/1.1) | Frozen in WORKS |
| #11 Sandbox/Execution | `proto.charter.schema.json` (proto.charter/1.0) | Frozen in WORKS |
| #14 Artifact | `shell.contracts.schema.json` (shell.contracts/1.0) | Frozen in WORKS |

## Register Cross-Reference

Every contract in `cross-repo-contracts.md` marked "Normative" now has a
concrete schema file in `frozen/`. The `manifest.json` `sha256` pins are the
authoritative integrity check — AIE and TG SHOULD verify against these when
consuming.
