# Aftergraph Release Intelligence Phase 1 Proof

**Date:** 2026-09-07  
**Scope:** Synthetic executable proof of the remaining ARI Phase 1 milestone  
**Public generation:** Aftergraph 26 · Convergence  
**Compatibility baseline:** APC-1

## Thesis under test

Aftergraph can derive a deterministic Release Registry from independently versioned exact-subject release evidence, query compatibility through the same provenance-aware graph semantics, and describe an exact release composition with RBOM without turning either derived artifact into a new source of authority.

This proof uses deliberately synthetic Sentinel and WORKS identities from the Phase 1 test fixtures. It is **not** a claim about live production compatibility.

## Exact synthetic subjects

```text
Sentinel engine
component          sentinel-engine
version            1.4.0
repository         Aftergraph/sentinel
source commit      1111111111111111111111111111111111111111
manifest digest    sha256:b17361cb4fb23e06c00c93a13ad0022a91665cdd69dc517a5fa1975bc607bc77
artifact digest    sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
passport digest    sha256:6e9f42f62d4cfbecd3f48924cc5a1f3dcbffa12d726d998d5af1f0f98ccb196c
APC profile        verifier

WORKS
component          works
version            0.5.1
repository         Aftergraph/works-execution
source commit      2222222222222222222222222222222222222222
manifest digest    sha256:53790113c5fe4e9662dfbd448cfe921a0048fdd33ddd41886e52007282f1ceeb
artifact digest    sha256:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb
passport digest    sha256:c89354f4f5593e78d6486455f75232a58001feac1a5a02462fc71bbd77e2b2d3
APC profile        execution

Compatibility edge
direction          sentinel-engine -> works
relation           tested-with
state              pass
evidence level     CE3
evidence ref       sha256:3333333333333333333333333333333333333333333333333333333333333333
edge digest        sha256:76cdfecefcdc63afca0fc1995d55f4a470934ff4ea9213382c7ecb4b709dc256

Platform generation  Aftergraph 26
Release train         2026.09
Compatibility         APC-1
```

The canonical fixture definitions are exercised in `scripts/test_ari_query.py` and `scripts/test_ari_rbom.py`. The two component versions remain independent; neither is rewritten to version 26.

Every digest in this document is reproducible from the current tree rather than carried forward on assertion. The two manifests are `SENTINEL` and `WORKS` in `scripts/test_ari_rbom.py`; the edge is `EDGE` in `scripts/test_ari_query.py`, whose evidence kind is `integration-test` — the same-shaped edge in `scripts/test_ari_registry.py` carries kind `test-receipt` and hashes apart, so naming the fixture home is load-bearing; and the two passports are that module's `passport(SENTINEL, "verifier")` and `passport(WORKS, "execution")`. Building the registry from those five documents yields the registry digest below, and building the RBOM from both exact selectors yields the RBOM digest below. Both were recomputed and matched at code head `a4a7b0a`.

## Deterministic Release Registry proof

A synthetic registry composed from the two manifests, the CE3 compatibility edge, and both exact-subject Release Passports yields:

```text
schema             release-registry/1.0
entries            5
components         2
edges              1
passports          2
registry digest    sha256:69b46e2f5879c1b72c94918055317fe777a245284dae8dd210d537cad12d0cdc
```

The registry implementation canonicalizes and digest-binds every embedded source document, sorts the derived entries deterministically, deduplicates semantically identical source documents, and rejects divergent content claiming the same exact `(component, version, commit)` identity.

Merge-readiness hardening proves four mutation boundaries:

```text
caller mutates source document after build       -> stored Registry input is unchanged
caller mutates constructor input after validate  -> Registry canonical snapshot is unchanged
caller mutates an accessor result                -> internal Registry state is unchanged
caller mutates public document/digest view       -> canonical state/digest cannot be changed
```

The Registry therefore acts as a reproducible derived snapshot rather than a live reference to mutable caller objects. Its public document surface is a defensive copy and its public digest is read-only.

The exact Passport-to-Manifest binding is also fail-closed. When the matching Manifest exists, Registry rejects a Passport if any of these bindings disagree:

```text
manifest digest
source repository
release train
APC profile set
```

A positive Passport also refuses non-positive profile states such as `FAIL`, `UNKNOWN`, or `STALE`. The `release-passport/1.0` schema permits only `PASS` or `N/A` profile values, requires a non-empty profile map, and — since the wave-5 hardening (thread 6kDaNC) — demands at least one `PASS` among the eight APC-1 profile keys through an eight-branch `anyOf`; Registry enforces the same rule at ingestion (`_validate_positive_passport`), so a contract-only consumer and the reference implementation now refuse an all-`N/A` passport identically.

## Exact compatibility query proof

Against the same two exact component identities and CE3 `tested-with` edge, the query condition is:

```text
left              sentinel-engine@1.4.0#1111111111111111111111111111111111111111
right             works@0.5.1#2222222222222222222222222222222222222222
minimum evidence  CE2
matching edges    1
result            PASS
evidence refs     1
```

The qualifying evidence reference is:

```text
sha256:3333333333333333333333333333333333333333333333333333333333333333
```

The query implementation delegates compatibility state calculation to `CompatibilityGraph`; it does not define a second precedence model. The test suite also verifies:

```text
missing exact edge                  -> UNKNOWN
PASS edge below minimum evidence    -> UNKNOWN
stale exact edge                    -> STALE
incompatible-with, either direction -> FAIL
non-exact selector                  -> rejected
unregistered exact component        -> rejected
invalid CE level                    -> rejected
```

CLI exit semantics remain aligned with the compiler family: PASS/N/A = 0, FAIL = 2, UNKNOWN/STALE = 3, invalid input = 2.

## RBOM v0 proof

Using the same exact Sentinel and WORKS manifests plus matching Release Passports produces:

```text
schema             rbom/0.1
components         2
passport coverage  2 / 2
verification       VERIFIED
release train      2026.09
compatibility      APC-1
registry digest    sha256:69b46e2f5879c1b72c94918055317fe777a245284dae8dd210d537cad12d0cdc
RBOM digest        sha256:54b9925c66650f8e9dcd101fe9f97fea8733c62607c9f4907897dd6d679b83c3
```

The derived contract inventory is deterministic:

```text
correlation  1.0
evidence     1.1
verdict      1.0
work         1.0
```

`VERIFIED` here has deliberately narrow meaning: every exact selected component has a matching Release Passport under `rbom/0.1`. It does **not** mean every relation, runtime condition, deployment property, failure mode, or scientific claim for the platform is verified.

The RBOM suite separately proves `PARTIAL` for one matching passport, `UNVERIFIED` for zero matching passports, exact-selector enforcement, duplicate-selector rejection, missing-component rejection, deterministic output, contract sorting/deduplication, registry-digest binding, and refusal of mixed release trains. The published `rbom/0.1` contract additionally binds the two passport-derived digests as a pair on every component row (thread 6kDFMp), so no verification state can carry a half-claimed passport, and the version grammar shared by all five published contracts is spelled with explicit escapes so Python and ECMA-262 consumers agree on the excluded set (thread 6kDaNH).

## CI evidence checkpoint

Authoritative GitHub Actions verification for the final code/schema head of this slice, observed on the PR branch head before the proof-document refresh on top of it:

```text
code head             a4a7b0a314da849f3070677bae4280262876b2c9
PR merge ref          0c238ad61f77332821040b7eba36c1d4a8d5d877
Release Intelligence  PASS (run 35471498815)
Platform Topology Truth PASS (run 35471498872)
Repository Agent Guides PASS (run 35471498775)
ARI tests             167 passed, 0 failed
Governance regression 67 passed, 0 failed
Python total          234 passed, 0 failed
ARI JSON syntax gates 6 passed
Brand assets          PASS (CI governance regression step; see note)
```

The ARI count rose from 99 at head `5156ca18…` to 105 at `9e8f3e61…` (the six regression tests for the selector-grammar and unhashable-state fixes), to 112 at `d6f861ce…` (the six-test registry contract interop class plus the structural kind-binding test), to 130 at `7826fbd…` (the ten-test shared evaluator suite `test_ari_schema_check.py`, the registry evaluator-loudness test, the six-test RBOM contract interop class, and the RBOM structural state-binding test), and to 167 here across four hardening waves measured on throwaway worktrees at each head: 145 at `ab30222…` (wave 1 — evaluator under-coverage, the RBOM UNVERIFIED row hole, and the machine-checked `ContractSurfaceTest`), 150 at `2058217…` (wave 2 — the RBOM PARTIAL existential and the passport `propertyNames` APC-1 pin), 153 at `2c90e5f…` (wave 3 — the passport `subject.component` IDENTIFIER_RE pin), 162 at `37c9bbf…` (wave 4 — the version grammar, the evaluator's `re.fullmatch` switch, the anchored-pattern surface invariant, and the selector/registry tie tests), and 167 here (wave 5 — the RBOM digest pair-binding, the passport at-least-one-PASS `anyOf`, and the engine-portable version grammar, each pinned by a structural and an interop test). Governance regression stayed at 67 because the new tests live in `test_ari_*.py`, which the ARI step discovers and the governance step enumerates explicitly. The standalone `Brand Assets` workflow is path-filtered to brand-owned files and did not run for this change; its validator's seven unit tests are inside the 67 that ran and passed in CI on this head, and a local read-only run of `scripts/verify_brand_assets.py` against the current assets exits 0 (`OK: Aftergraph/after-graph-governance satisfies aftergraph.brand-assets/2.0`).

The six syntax gates cover:

```text
docs/release-intelligence/apc-1.json
docs/contracts/aftergraph-component/1.0.json
docs/contracts/compatibility-edge/1.0.json
docs/contracts/release-passport/1.0.json
docs/contracts/release-registry/1.0.json
docs/contracts/rbom/0.1.json
```

This proof-document refresh changes no code, schema, or test relative to the code head above.

### What the exact-SHA evidence rule binds

The checkpoint binds the **authored** code head named above. GitHub recomputes `refs/pull/39/merge` on every push as a synthetic base⊕head preview object: it carries no authored content of its own, is never pushed by anyone, and disappears the moment the next commit lands on the branch. It is therefore recorded here only as a cross-reference to the ephemeral object the queue happened to test, never as the SHA the evidence binds. Under the repository rule that "evidence from an older SHA is stale", the operative SHA is the authored commit carrying the change — so a docs-only refresh whose tree is byte-identical in every gated path cannot invalidate gate results for the code head, because the gated paths are precisely what those gates exercise. Recording a different merge ref per push would make the checkpoint stale against itself by construction, which is a category error rather than a defect in the evidence.

The terminal authoritative evidence is the post-merge `push` to `main` run on the merged tree, which re-runs every applicable gate against the squashed content; the `pull_request` runs above are the pre-merge gate.

Release Intelligence carries no `merge_group` trigger: its merge-ref verification is the `pull_request` run computed against `refs/pull/39/merge`, and because `docs/release-intelligence/**` is inside its path filter this refresh also carries its own `pull_request` run on the branch head. Platform Topology Truth and Repository Agent Guides run both `pull_request` and `merge_group`. Authoritative merge-ref verification therefore happens via those `pull_request` checks plus the merge queue's `merge_group` enforcement at enqueue; the PR head must still pass every applicable gate before merge readiness is claimed.

## PROVED

The Phase 1 implementation proves, within the synthetic evidence boundary, that Governance can:

1. construct a deterministic, digest-bound Release Registry from validated exact-subject release documents;
2. fail closed on malformed source documents, digest mismatch, divergent duplicate exact identities, and conflicting Passport/Manifest identity;
3. preserve Registry snapshot integrity across source, constructor, accessor, and public-state mutation boundaries;
4. bind positive Passports to matching manifest digest, repository, release train, and APC profile set when the exact Manifest is present;
5. refuse positive Passports containing non-positive profile states and positive Passports carrying no `PASS` profile, at both Registry ingestion and the machine schema;
6. query exact compatibility without hidden `latest` resolution and without duplicating graph state semantics;
7. preserve PASS, FAIL, UNKNOWN, STALE, and N/A distinctions;
8. build an exact RBOM for independently versioned components;
9. distinguish full, partial, and absent matching-passport coverage without inflating that state into blanket platform verification;
10. keep Release Registry and RBOM as derived release-intelligence artifacts rather than runtime authority sources.

Together with the preceding Phase 0/1 slice, this satisfies the approved Phase 1 milestone boundary: Release Registry, Compatibility Graph, APC Compiler/basic deterministic conformance, Release Passport, RBOM v0, and query/CLI basics.

## NOT PROVED

This Phase 1 proof does **not** establish:

- live production compatibility between Sentinel and WORKS;
- whole-platform APC-1 conformance;
- customer deployment compatibility;
- release admission or promotion correctness;
- semantic breaking-change classification;
- version-skew simulation correctness;
- verified upgrade or rollback paths;
- runtime capability negotiation;
- production compatibility telemetry or drift detection;
- CE4 failure/upgrade evidence for this synthetic combination;
- CE5 production-observed compatibility evidence;
- signed platform attestations;
- Release Digital Twin correctness;
- regulatory certification or compliance;
- scientific validity beyond the separate ISR evidence boundary.

Those are later ARI phases and require their own exact evidence.
