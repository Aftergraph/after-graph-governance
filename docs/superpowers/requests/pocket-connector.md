# Build request: Pocket connector (Wie provider subsystem)

Owner: `Aftergraph/wi-backend` — Pocket provider-subsystem owner under Wie
Contract: `pocket-source/0.1` (`docs/contracts/pocket-source/0.1.json` in after-graph-governance; versioned successors keep the `pocket-source/0.x` lineage)
Seam binding: `docs/POCKET-SOURCE-V1.md` in after-graph-governance
Acceptance vectors: `PCK-001`, `PCK-002`, `PCK-003`, `PCK-004`, `PCK-005`, `PCK-006`, `PCK-007`, `PCK-010`, `PCK-011`, `PCK-012`, `PCK-013`, `PCK-014`, `PCK-015`, `PCK-016`, `PCK-017`, `PCK-020`, `PCK-021`, `PCK-022`, `PCK-023`, `PCK-024`, `PCK-025`, `PCK-026`, `PCK-027`

## What to build

Own the Pocket connector inside `Aftergraph/wi-backend` as the Pocket provider subsystem under Wie, per V4 §13 pipeline: ingest Pocket-source signals, keep derivation lineage with distinct evidentiary weights, and serve a governed consequential path for any Pocket-derived commitment. Consent revocation and source deletion invalidate downstream use per provenance without rewriting audit. No realtime-audio claims without device evidence. Forbid Pocket authority-conflation phrases (Pocket-as-principal/authority/executor/oracle, transcript-as-identity, speaker-as-authentication, spoken-command-as-permission, MCP-as-ingestion, webhook-as-truth).

## Plane mapping

REST = reconciliation; webhooks = event plane with signature/replay/dedupe guard; MCP = optional interactive plane, never canonical.

## Canonical boundary

Pocket-derived data is never canonical on its own: webhooks carry event-plane claims subject to reconciliation, and MCP answers are interactive only. The canonical boundary sits at Trust Gateway admission and reconciled projection — nothing Pocket-originated crosses it unadmitted.

## Acceptance

- `PCK-001`: gated acceptance
- `PCK-002`: gated acceptance
- `PCK-003`: gated acceptance
- `PCK-004`: gated acceptance
- `PCK-005`: gated acceptance
- `PCK-006`: gated acceptance
- `PCK-007`: gated acceptance
- `PCK-010`: gated acceptance
- `PCK-011`: gated acceptance
- `PCK-012`: gated acceptance
- `PCK-013`: gated acceptance
- `PCK-014`: gated acceptance
- `PCK-015`: gated acceptance
- `PCK-016`: gated acceptance
- `PCK-017`: gated acceptance
- `PCK-020`: gated acceptance
- `PCK-021`: gated acceptance
- `PCK-022`: gated acceptance
- `PCK-023`: gated acceptance
- `PCK-024`: gated acceptance
- `PCK-025`: gated acceptance
- `PCK-026`: gated acceptance
- `PCK-027`: gated acceptance

## Out of scope

Governance registers the contract and pins acceptance only. Governance implements nothing in `Aftergraph/wi-backend`; the canonical connector behavior belongs to the Wie owners, proven by the owner repo's own tests, PR, CI, merge queue, and exact-head evidence.

## Hardware-gated appendix: physical-device characterization

The following physical-device characterization items are explicitly marked `BLOCKED_ON_POCKET_HARDWARE` pending device evidence. No acceptance is claimed for them here.

- device audio-capture characterization — `BLOCKED_ON_POCKET_HARDWARE`
- microphone-array characterization — `BLOCKED_ON_POCKET_HARDWARE`
- realtime-audio pipeline characterization — `BLOCKED_ON_POCKET_HARDWARE`
- acoustic-environment characterization — `BLOCKED_ON_POCKET_HARDWARE`
