# Build request: AVC retirement (dissolution ledger execution)

Owner: `Aftergraph/autonomous-venture-company` — phased extraction source for the dissolution ledger (ledger dispositions applied, delta to legacy head audited, provenance retained); `Aftergraph/skills-vault` — sole active canonical skill supply-chain owner and skill migration target (generic reusable `avc-*` skill migration, legacy aliases/provenance as needed; persona/product-specific skills generalized or retired); `Aftergraph/runtime` — consumer-removal owner on its seam (active `@avc/*` dependencies, canonical service/contract ownership, Hermes execution adapter migration/reconciliation, tenant/workspace lifecycle and World/Situation/Commitment/Consent/Attention primitive extraction or retirement); `Aftergraph/aie` — consumer-removal owner on its seam (active `@avc/*` dependencies, canonical service/contract ownership, lifecycle and primitive extraction or retirement); `Aftergraph/trust-gateway` — consumer-removal owner on its seam (active `@avc/*` dependencies, canonical service/contract ownership, Consent/lifecycle extraction or retirement); `Aftergraph/works-execution` — consumer-removal owner on its seam (active `@avc/*` dependencies, canonical service/contract ownership, Hermes execution adapter migration/reconciliation, lifecycle and primitive extraction or retirement); verifier allies: `continuum` and `sentinel` supply independent verification evidence for the Aftergraph-only Golden Mission, never self-attestation by the migrating party
Contract: `avc-dissolution/0.1` (`docs/contracts/avc-dissolution/0.1.json` in after-graph-governance; versioned successors keep the `avc-dissolution/0.x` lineage)
Seam binding: `docs/AVC-RETIREMENT-V1.md` in after-graph-governance
Acceptance vectors: `RET-001`, `RET-002`, `RET-003`, `RET-004`, `RET-005`, `RET-006`, `RET-007`, `RET-010`, `RET-011`, `RET-012`, `RET-013`, `RET-014`, `RET-015`, `RET-016`, `RET-017`, `RET-020`, `RET-021`, `RET-022`, `RET-023`, `RET-024`, `RET-025`, `RET-026`, `RET-027`, `RET-030`, `RET-031`, `RET-032`, `RET-033`, `RET-034`, `RET-035`, `RET-036`, `RET-037`

## What to build

- In `Aftergraph/autonomous-venture-company`, build phased extraction execution: apply ledger dispositions (`MIGRATED_VERIFIED`/`MIGRATED_TRANSITIONAL`/`EXTRACT`/`RETIRE`/`HISTORY_ONLY`) pinned to extraction baseline `18317c7b2eebcc08bb2a1b30d9118935d5832540`, audit the delta to legacy head, retain provenance; never retire an identity outside the ledger.
- In `Aftergraph/skills-vault`, build skill migration execution: migrate generic reusable `avc-*` skills to Aftergraph canonical identifiers with legacy alias/provenance retained, generalize or retire persona/product-specific skills, reconcile the Hermes execution adapter with verification refs; migration evidence lives skills-vault-side, never legacy-repo self-attestation.
- In `Aftergraph/runtime`, `Aftergraph/aie`, `Aftergraph/trust-gateway`, and `Aftergraph/works-execution`, build consumer-removal execution on each repo's own seam: zero active `@avc/*` package dependencies except the allowlisted provenance set, zero canonical services owned by AVC identities, zero current normative contracts owned by AVC identities, tenant/workspace lifecycle and World/Situation/Commitment/Consent/Attention primitive dispositions resolved, every package/app/skill/ML/cell/infra asset classified with a disposition.
- In `continuum` and `sentinel` as verifier allies, supply independent verification evidence for the Aftergraph-only Golden Mission: Aftergraph-only mission path, canonical identity preserved across the consequential chain, success plus fail-closed adversarial branches (refusal/revocation/crash-recovery/verifier-failure), provenance reachable after archive, exact-head repos.
- Keep `platform-event-ref/0.1` plus canonical causal identifiers as dedupe/correlation substrate only: never retirement authority and never a substitute for ledger or gate evidence.
- Forbid retirement-conflation phrases (retirement-outside-ledger, ownership-removed-with-active-consumer, canonical-doc-still-assigns-AVC-ownership, governance-executes-archival, archive-as-autonomous-action, new-avc-identifier-as-active, self-attested-migration, local-green-as-retirement, bypass-as-dissolution).

## Canonical boundary

Dissolution retires AVC identities ONLY through the ledger with every gate evidenced. No AVC identity loses ownership while an active consumer or canonical doc still references it. The governance repo NEVER executes archival/deletion. The final legacy-repo archive action is REQUIRES_EXPLICIT_OWNER_AUTHORIZATION (irreversible, outside autonomous execution). No retirement, migration, consumer-removal, or Golden Mission claim stands without ledger/gate evidence.

## Acceptance

- `RET-001`: ledger accept — dissolution record with valid disposition pinned to baseline
- `RET-002`: ledger reject — retirement with non-empty active consumers
- `RET-003`: ledger reject — retirement while a canonical doc still assigns AVC ownership
- `RET-004`: ledger reject — retirement asserted outside the ledger
- `RET-005`: ledger reject — unknown disposition or missing deletion gate
- `RET-006`: ledger reject — newly-minted active AVC identifier
- `RET-007`: ledger reject — extraction-completion claim without owner evidence (evidence-gated)
- `RET-010`: migration accept — skill ledgered to skills-vault with canonical identifier and provenance
- `RET-011`: migration reject — canonical ownership claimed while ledger still shows AVC owner
- `RET-012`: migration reject — persona/product-specific skill carried over verbatim
- `RET-013`: migration reject — Hermes adapter ledgered without migration/reconciliation and verification refs
- `RET-014`: migration reject — migration minting a new active AVC identifier
- `RET-015`: migration reject — legacy-repo self-attestation without skills-vault-side evidence
- `RET-016`: migration reject — canonical contract still owned by AVC in a migration claim
- `RET-017`: migration reject — live migration-completion claim without owner evidence (evidence-gated)
- `RET-020`: consumer accept — zero active dependencies, zero AVC-owned services, dispositions resolved
- `RET-021`: consumer reject — active dependency remains outside the provenance allowlist
- `RET-022`: consumer reject — canonical service still owned by AVC
- `RET-023`: consumer reject — current normative contract still owned by AVC
- `RET-024`: consumer reject — ownership removed while an active consumer still references the identity
- `RET-025`: consumer reject — unclassified asset left without a disposition
- `RET-026`: consumer reject — removal proven by repository-local green without cross-repo evidence refs
- `RET-027`: consumer reject — live zero-consumer/zero-ownership claim without owner evidence (evidence-gated)
- `RET-030`: mission-gate accept — Aftergraph-only Golden Mission gate with adversarial branches
- `RET-031`: mission-gate reject — `@avc/*` dependency in the mission path
- `RET-032`: mission-gate reject — happy path only without refusal/revocation/crash-recovery/verifier-failure branches
- `RET-033`: mission-gate reject — causal-identity mismatch across the consequential seam
- `RET-034`: mission-gate reject — executor self-verification without independent verification
- `RET-035`: mission-gate reject — provenance unreachable after archive in the gate fixture
- `RET-036`: mission-gate reject — mission asserted against non-exact-head repos as platform claim
- `RET-037`: mission-gate reject — live mission-success claim without exact-head owner evidence (evidence-gated)

## Out of scope

Governance pins the ledger, gates, vectors, and this request only. Governance implements nothing in `Aftergraph/autonomous-venture-company`; the phased extraction belongs to the autonomous-venture-company owners, proven by the owner repo's own tests, PR, CI, merge queue, and exact-head evidence. Governance implements nothing in `Aftergraph/skills-vault`; the skill migration belongs to the skills-vault owners, proven by the owner repo's own tests, PR, CI, merge queue, and exact-head evidence. Governance implements nothing in `Aftergraph/runtime`; the consumer removal on its seam belongs to the runtime owners, proven by the owner repo's own tests, PR, CI, merge queue, and exact-head evidence. Governance implements nothing in `Aftergraph/aie`; the consumer removal on its seam belongs to the aie owners, proven by the owner repo's own tests, PR, CI, merge queue, and exact-head evidence. Governance implements nothing in `Aftergraph/trust-gateway`; the consumer removal on its seam belongs to the trust-gateway owners, proven by the owner repo's own tests, PR, CI, merge queue, and exact-head evidence. Governance implements nothing in `Aftergraph/works-execution`; the consumer removal on its seam belongs to the works-execution owners, proven by the owner repo's own tests, PR, CI, merge queue, and exact-head evidence. The governance repo NEVER executes archival/deletion; the final legacy-repo archive action is REQUIRES_EXPLICIT_OWNER_AUTHORIZATION and stays outside autonomous execution.

## Evidence-gated appendix: owner-execution-dependent characterization

The following owner-execution-dependent items are explicitly marked `BLOCKED_ON_OWNER_EXECUTION` pending owner-repo execution evidence. No acceptance is claimed for them here.

- phased extraction execution — `BLOCKED_ON_OWNER_EXECUTION`
- skill migration execution — `BLOCKED_ON_OWNER_EXECUTION`
- consumer-removal execution — `BLOCKED_ON_OWNER_EXECUTION`
- live Aftergraph-only Golden Mission execution — `BLOCKED_ON_OWNER_EXECUTION`
- legacy-repo archive action — `BLOCKED_ON_OWNER_EXECUTION`
