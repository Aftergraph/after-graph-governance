# Economic Live Settlement v1 — Candidate Readiness

Status: **FRONTIER**. Not a Candidate and not Canonical.

This record tracks whether `economic.live-settlement/v1` has accumulated enough independently verifiable evidence to be proposed for CANDIDATE status.

## Already verified

- WORKS zero-effect atomic multi-leg settlement simulator.
- Unknown leg => UNCERTAIN.
- Partial failure => ABORTED.
- Simulated all-commit does not establish real-world FINAL.
- Trust Gateway denies live execution while the capability is non-canonical.
- Caller-supplied promotion references do not count as governance promotion.
- Sentinel requires independent rail diversity and does not convert cross-rail corroboration into FINAL.

## Runtime rail characterization

The intended read-only rail implementations are:

1. **EVM JSON-RPC**
   - transaction receipt observation;
   - finalized-head observation;
   - no signing or transaction submission.

2. **Canton JSON Ledger API**
   - participant ledger-end observation;
   - update-by-offset observation;
   - classified as PARTICIPANT_LEDGER_OBSERVED, not legal/economic finality.

## Candidate blockers

Candidate status remains blocked until real endpoint evidence exists. Fixture-only or injected-fetch tests are architecture/conformance evidence, not production rail evidence.

Required next evidence:

- read-only observations from real EVM and Canton nodes;
- independent Sentinel reconciliation over those observations;
- disagreement/reorg/stale-offset campaign;
- governance-owned verifier/gate evidence.

Signing, custody, broadcasting and autonomous value transfer remain disabled throughout Candidate-readiness work.
