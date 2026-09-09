# AVC Retirement V1 — Canonical Dissolution-Ledger Binding

Status: Canonical for retirement seams.
Topology: `docs/platform-topology/2.0.json`.

**Design rationale:** V4 spec §§9/15/16/19/22/23 (rationale only; this document is
normative for the binding). Wave H promotion-gate/trace/challenger semantics are
inherited, never re-derived here (`wi-backend` / `wi-frontend` candidate flow,
`runtime` decision stay owned by that binding); this binding adds no candidate
pipeline and re-derives none of it. Primitive mapping (§9), naming policy (§15),
dissolution ledger (§16), Golden Mission (§19), Wave I scope (§22), and acceptance
criteria (§23) stay owned by the V4 spec as rationale.

Dissolution is a conformance/retirement record: no execution ownership, no
authority transport, no archival execution. Retirement advances only through the
ledger with every gate evidenced; skill/consumer/mission retirement only through
ledger + gate evidence.

Canonical boundary: retirement only through the ledger with every gate evidenced;
no AVC identity loses ownership while an active consumer or a canonical doc still
references it; governance never executes archival/deletion; the final legacy-repo
archive action is `REQUIRES_EXPLICIT_OWNER_AUTHORIZATION` (irreversible, outside
autonomous execution). Nothing here creates a new authority, service, plane, fabric, owner, or repo.

| Seam | V4 owner | Binding |
| --- | --- | --- |
| Phased extraction | `autonomous-venture-company` | Extraction source applies ledger dispositions against baseline `18317c7b2eebcc08bb2a1b30d9118935d5832540` plus audited delta to legacy head, provenance retained. |
| Skill migration | `skills-vault` | Sole active canonical skill supply-chain owner; generic reusable `avc-*` skills migrate here with legacy alias/provenance retained, persona/product-specific skills generalized or retired; migration evidence is never self-attestation by the migrating party. |
| Consumer removal | `runtime`, `aie`, `trust-gateway`, `works-execution` | Active `@avc/*` dependencies, canonical service/contract ownership, Hermes execution adapter migration/reconciliation, and tenant/workspace lifecycle plus World/Situation/Commitment/Consent/Attention primitive extraction or retirement on their own seams. |
| Independent verification | `continuum`, `sentinel` | Verifier allies supply independent verification evidence for the Aftergraph-only Golden Mission; never the migrating party's own attestation. |
| Correlation substrate | — | `platform-event-ref/0.1` plus canonical causal identifiers stay dedupe/correlation only: never retirement authority and never a substitute for ledger or gate evidence. |
| Governance pinning | after-graph-governance | Governance pins the ledger, gates, vectors, and requests only, and implements nothing in owner repos. |

Evidence split: ledger contract, skill/Hermes migration conformance,
consumer-removal conformance, Aftergraph-only Golden Mission gate definition, and
this binding are evidence-independent and proven with fixtures. Phased extraction
execution, live migration/consumer-removal execution, live Golden Mission results
on exact heads, and the final legacy-repo archive action are marked
`BLOCKED_ON_OWNER_EXECUTION`; no such claim appears here, and none is proven with mocks.

Invariants (restated, not extended):

- Retirement advances only through the ledger with every gate evidenced.
- No AVC identity loses ownership while an active consumer or a canonical doc
  still references it.
- No canonical active doc assigns platform ownership to a retired AVC identity
  (§23 criterion 2).
- The ledger is complete enough to prove every remaining active dependency or
  classify it as historical (§23 criterion 12).
- Governance never executes archival/deletion; the final legacy-repo archive
  action is `REQUIRES_EXPLICIT_OWNER_AUTHORIZATION`, irreversible and outside
  autonomous execution.
- §9 primitive mapping inherited: `Entity` / `Relationship` / `Situation` /
  `Commitment` / `AttentionPolicy` / `AttentionCandidate` / `Opportunity` /
  `InteractionThread` / `ConsentRecord` / canonical domain policy /
  `AssistantAdvisor` / `AssistantProfile`; `Personal*` stays removed as a platform category.
- §15 naming policy inherited: `Aftergraph` masterbrand, canonical
  `@aftergraph/*`; no new AVC identifiers enter active use, and historical
  records retain old names only where provenance requires.
- Dispositions are exactly `MIGRATED_VERIFIED` / `MIGRATED_TRANSITIONAL` /
  `EXTRACT` / `RETIRE` / `HISTORY_ONLY` against the baseline above.
- No retirement/migration/removal/mission claims without ledger/gate evidence.
- Repository-local green never counts as retirement; bypass never advances
  dissolution without gate evidence.
