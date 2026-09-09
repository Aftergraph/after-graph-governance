# Build request: Wie proactivity sensing

Owner: `Aftergraph/wi-backend`
Contract: `proactivity/0.1` (`docs/contracts/proactivity/0.1.json` in after-graph-governance)
Acceptance vectors: `PRO-001`, `PRO-003`, `PRO-005`
Seam binding: `docs/PROACTIVITY-ORG-V1.md` in after-graph-governance

## What to build

Own Wie proactivity sensing inside `Aftergraph/wi-backend`: project
native Wie signals to sensing candidates (opportunity, attention,
commitment) that preserve native meaning and claim nothing. Candidates
never self-admit: a commitment candidate without Trust Gateway admission
fails closed. Correlate the same native signal seen via Wie and Cron
into a single deduped attention candidate.

## Acceptance

- `PRO-001`: a Wie external signal projecting its native event to an opportunity candidate that claims neither execution nor admission is accepted.
- `PRO-003`: a commitment candidate claiming admission without Trust Gateway admission is rejected (candidates never self-admit).
- `PRO-005`: the same native signal seen via Wie and Cron correlates and dedupes to a single attention candidate, accepted.

## Out of scope

Governance registers the contract and pins acceptance only. Governance implements nothing in `Aftergraph/wi-backend`; the canonical sensing
behavior belongs to the Wie owners, proven by the owner repo's own
tests, PR, CI, merge queue, and exact-head evidence.
