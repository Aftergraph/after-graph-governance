# Economic Live Settlement v1 — Candidate Readiness

Status: **CANDIDATE**. Not Canonical. Live execution remains disabled.

This record records the evidence that advanced `economic.live-settlement/v1` to CANDIDATE status. Candidate is a maturity state only; it carries no authority and does not enable live execution.

## Already verified

- WORKS zero-effect atomic multi-leg settlement simulator.
- Unknown leg => UNCERTAIN.
- Partial failure => ABORTED.
- Simulated all-commit does not establish real-world FINAL.
- Trust Gateway denies live execution while the capability is non-canonical.
- Caller-supplied promotion references do not count as governance promotion.
- Sentinel requires independent rail diversity and does not convert cross-rail corroboration into FINAL.

## Runtime rail characterization

Runtime read-only rail adapters are merged at `f3ca0e0a9fff25328cb42b2f00aedda0de3f63dc` with canonical Runtime CI green.

The implemented read-only rail surfaces are:

1. **EVM JSON-RPC**
   - transaction receipt observation;
   - finalized-head observation;
   - no signing or transaction submission.

2. **Canton JSON Ledger API**
   - participant ledger-end observation;
   - update-by-offset observation;
   - classified as PARTICIPANT_LEDGER_OBSERVED, not legal/economic finality.

## Candidate blockers

Candidate evidence now includes real read-only Ethereum finalized observations, a real Canton 3.5.17 sandbox participant, independent Sentinel verification, and real-response boundary falsification. These are promotion-to-CANDIDATE evidence only.

Canonical promotion remains blocked on same-economic-transaction settlement evidence, signer/custody boundaries, human authorization/revocation/kill-switch/compensation evidence, legal/custodial reconciliation, and bounded live-value canaries.

Candidate evidence completed:

- real EVM finalized receipt observation;
- real Canton 3.5.17 participant JSON Ledger API observation;
- independent Sentinel verification;
- EVM pre-finality and finalized-head non-regression falsification;
- Canton ahead-of-ledger offset rejection;
- cross-rail correlation disagreement => UNCERTAIN;
- governance-owned candidate promotion record.

Signing, custody, broadcasting and autonomous value transfer remain disabled. Canonical promotion requires a separate governance decision and materially stronger live-value evidence.
