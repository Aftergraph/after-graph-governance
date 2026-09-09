# Aftergraph Convergence Mission — Final Evidence Report (2026-09-10)

Verdict: **PARTIALLY-INTEGRATED** (ledger denominator below; no percentage claimed).

Evidence cut: 2026-09-10 ~00:30 UTC. Governance base: `2c44d0e`.
Exact-head inventory taken live from GitHub API; SHAs are 12-char prefixes.

## A. Repository inventory (25 live = 25 topology, 0 unknown)

| repo | visibility | main HEAD | open PRs |
| --- | --- | --- | --- |
| after-graph-governance | public | 2c44d0e429b3 | 3 (non-mission #38/#39/#40) |
| aie | public | eea622b09ca6 | 2 |
| trust-gateway | public | 5ec9dc45b123 | 6 |
| runtime | private | 98d356dcaf73 | 41 |
| works-execution | public | 1267f03b7ae5 | 4 |
| studio | public | d332fe03d122 | 3 |
| wi-backend | public | 6d6fef9e577a | 0 |
| wi-frontend | private | e3c922ec1483 | 3 |
| context-continuity | private | 9ceeececa119 | 2 |
| continuum | private | ba25ae52654b | 3 |
| sentinel | public | 75fee89e0025 | 2 |
| sentinel-firetest | private | dd84e5257a11 | 1 |
| sentinel-firetest2 | public | e59ce2593063 | 0 |
| intelligence-systems-research | public | 650e35cce7ca | 3 |
| skills-vault | private | 83d7c4f85ca2 | 2 |
| llm-research-development | private | a4a7d460c327 | 3 |
| afm | private | e139d3e1b28b | 2 |
| model-registry | private | a0d77e5e9b1f | 3 |
| autonomous-venture-company | private | e08d3372dda3 | 56 |
| aftergraph-cron-fabric | public | 5f418ee8999a | 0 |
| veranza | private | b7936bd2c613 | 1 |
| docs | public | 1e019b9110b7 | 7 |
| aftergraph.org | public | ed9236505050 | 4 |
| brand | public | 4f8b5a771fe4 | 1 |
| .github | public | b5fe72fb5b5d | 0 |

## B. Before/after topology reconciliation

- Before: 24-repo topology vs 25 live repos; `sentinel-firetest2` (public,
  created 2026-09-08) unclassified — the exact gap Phase 0 predicted.
- After: 25-repo `platform-topology/2.0.json` on gov main `2c44d0e`;
  firetest2 classified `temporary-verification-fixture`, expires 2026-09-22;
  firetest expires 2026-09-21. Live org diff at cut: **0 unknown repos**.
- `expires_at` promoted to first-class optional field (schema + validator +
  generator): temporary requires it, permanent must not carry it.
- Machine-readable reconciliation artifact: Phase 0 evidence (gov #134).

## C. Closed gaps

1. Unknown-repo blindness: `org-state-verify.sh` now enumerates the live org
   and fails closed on unclassified repos (25-repo live run DONE).
2. Ephemeral fixtures without lifetime: expiry enforced in three layers
   (validator rejects missing/invalid, generator fails past expiry —
   functionally probed with a synthetic expired entry).
3. works-execution#71 CI failure: `TestVerificationVerdictIsIdempotentAndImmutable`
   reproduced locally; fix `6144ecd` makes conflicting re-attestation fail
   closed with `ErrVerificationVerdictConflict` (identical retry idempotent).
   CI now fully green (test, Analyze, CodeQL).
4. L0-L6 matrix missing: `docs/evidence/capability-conformance-2026-09-10.json`
   (13 rows, shape-tested, ladder pinned to V4 s7 at `2c44d0e`).

## D. Remaining blocked gaps (owner / dependency)

- REVIEW_REQUIRED (human review; cannot self-approve): trust-gateway#82/#83/#84,
  studio#47/#48, docs#19/#20, aie#58, works-execution#69/#71/#72.
  #71 is CI-green and merge-ready; the rest are green except where noted.
- Docs production deploy BLOCKED: no Cloudflare credentials in this environment;
  `deploy` check skips in CI; build-manifest `site_commit` comparison never ran
  against live https://docs.aftergraph.org. Never claimed. (Phase 1 item 2.)
- Live cross-service Golden Mission (exact-head runtime→works→verifier with
  causal identity across real seams): not run; scenario proof is simulated.
- Second runtime family for continuum (LangGraph/Temporal/Restate): not campaigned.
- AIE external gates (A2A TCK, OPA↔Cedar, federation chaos, second
  implementation): untouched. Research gates (STUDY-011/012 live discipline,
  MISSION-Bench independent reproduction): untouched.
- AVC archive: NOT READY, requires explicit owner authorization (binding).

## E. PRs / commits per repository (this mission session)

Merged 2026-09-09: gov#136 (23:24:15), continuum#15 (23:24:47), gov#134 +
gov#135 (23:25:16/17), context-continuity#6 (23:26:32), skills-vault#64
(23:26:35), works-execution#70 (23:27:12, squash), runtime#111 (23:27:45).
Pushed, CI-green, awaiting review: works-execution#71 (+`6144ecd` fix).
Prior-session landings (Phases 0-4, 6-7, 9-10) recorded in repo histories;
exact per-repo commit lists are in each repo's git log, not duplicated here.

## F. Exact test/build results (re-verified 2026-09-10)

- Governance gate: topology 59 OK, org-state 5 OK, enforcement 7 OK,
  matrix 8 OK; `platform_topology.py check` + `check-readme` OK;
  `bash -n org-state-verify.sh` OK.
- Live `org-state-verify.sh`: 25 repos, SCHEMA-OK, DONE on gov main 2c44d0e.
- Docs branch `2d9fdb0`: `validate.mjs` PASS; `golden-mission.mjs` PASS
  (10 steps, 7 faults CONTAINED), re-executed locally.
- works-execution#71 head: `go build ./...` clean, `go test ./...` 44 ok / 0 FAIL.

## G. Golden Mission evidence bundle

`docs/src/data/golden-mission.scenario.json` (10 steps incl. 4 distinct Studio
states) + `golden-mission.mjs` runner + `validate.mjs` gate in CI.
Causal mission identity is carried as explicit fields through the scenario;
second campaign injects restart, duplicate delivery, stale authority,
revocation, budget exhaustion, model/runtime replacement, verifier outage —
all 7 CONTAINED. Scope: simulated single-implementation proof, not live
cross-service integration (see D).

## H. Adversarial campaign results

- Golden Mission fault campaign: 7/7 contained (simulated).
- WORKS verdict store: conflicting re-attestation fails closed, original
  preserved (`ErrVerificationVerdictConflict`); identical retry idempotent.
- Phase 3 twelve-case seal campaign evidence lives on unmerged WE branches
  (#69/#72); not re-verified here, not claimed beyond L1.
- Continuum containment verdict: STOP scored as STOP, never as recovery (#15).

## I. Deployment evidence

None. No production deployment performed or claimed in this session;
no deployed SHAs exist to report.

## J. Docs exact-head production verification

Not performed — blocked per D (credentials). CI `deploy` job skips;
`gates` pass on docs#20 branch.

## K. L0-L6 capability matrix

`docs/evidence/capability-conformance-2026-09-10.json`: 1×L4-simulated
(golden scenario), 7×L1, 5×L0. No L2+ live-integration claim, no L5/L6 claim
anywhere. Every sub-L4 row names its blocker.

## L. Legacy AVC remaining dependency count

Recount at exact AVC main `e08d3372dda3` (2026-09-10): **46 manifests** with
`@avc/*` refs — unchanged from ledger baseline (40 pkgs / 46 manifests).
Zero legacy removals evidenced. Ledger verdict remains BASELINED; 5 rows
target_capability_proven, 2 extraction_proposed, 1 proposed.

## M. Scientific-claim boundary

No scientific (L6) claims are made. External convergence (e.g. prior-art
registrations) is architectural context, not validation. Null/negative
results preserved: containment STOP is not recovery; expired/nonexistent
fixtures fail closed; conflicting verdicts are refused, not merged.
Independent reproduction of any Aftergraph claim by an outside party: none.

## N. Final verdict

**PARTIALLY-INTEGRATED.** Intent becomes governed work (topology + enforcement
gates live), governed work survives failure (simulated campaigns + verdict
immutability), failure cannot silently widen authority (fail-closed gates
at every seam touched), completion cannot masquerade as verification
(SUCCEEDED vs VERIFIED separated in WORKS store + Studio states), and an
independent observer can reconstruct trust from the cited SHAs, CI runs, and
machine-readable artifacts. Full PLATFORM-INTEGRATED requires the D-list:
human reviews merged, live cross-service Golden Mission on exact heads,
docs production SHA proof, second-family continuum campaign, and the first
AVC consumer cutover.
