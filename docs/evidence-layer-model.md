# Evidence Layer Model — 4 Layers, Common Correlation IDs

> Canonical evidence taxonomy for the After Graph platform.
> Principle: write-ahead admission/audit (L1) is SEPARATE from post-effect verification/settlement (L2+).

## Layers

| Layer | Name | Producer | Format | Retention | Correlation |
|---|---|---|---|---|---|
| L1 | Action Audit | TG hash-chain | `{seq, prevHash, ts, payload, hash}` (append-only, tamper-evident) | Indefinite | `mission_id` + `actionId` in payload |
| L2 | Execution Quittance | works-execution | `evidence bundle` + `quittance` (content-addressed, HMAC-SHA256 signed) | Configurable TTL (compliance ~7y) | bundle metadata carries `mission_id` + `actionId` |
| L3 | Institutional Conformance | AIE | conformance vectors + PolicyDecisionRecord | Policy lifecycle (~5–10y) | same pair |
| L4 | Scientific Evidence | ISR (STUDY-011, MISSION-Bench) | preregistration + records + Wilson CI / McNemar analyses | Permanent (scientific record) | same pair |

## Rules

1. Every evidence item carries `mission_id` + `actionId` — end-to-end traceability, cross-layer queries.
2. L1 is written BEFORE the action executes (write-ahead admission); L2 is produced AFTER the effect (post-effect verification). They are never merged into one record.
3. No layer may upgrade another: L4 scientific claims never become platform-wide runtime claims automatically (ISR evaluates, does not claim).
4. L1 chain integrity is verifiable independently (`GET /v2/audit/export` in TG).

## Claim Inheritance

- ISR results (L4) do NOT auto-promote to platform claims (L3).
- Promotion requires explicit owner approval + a decision record (DEC-xxx) + conformance evidence (L3).
