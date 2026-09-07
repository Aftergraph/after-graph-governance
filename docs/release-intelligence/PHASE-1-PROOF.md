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

Merge-readiness hardening additionally proves three mutation boundaries:

```text
caller mutates source document after build       -> stored Registry input is unchanged
caller mutates constructor input after validate  -> Registry canonical snapshot is unchanged
caller mutates an accessor result                -> internal Registry state is unchanged
```

The Registry therefore acts as a reproducible derived snapshot rather than a live reference to mutable caller objects.

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
missing exact edge                 -> UNKNOWN
PASS edge below minimum evidence   -> UNKNOWN
stale exact edge                   -> STALE
incompatible-with, either direction -> FAIL
non-exact selector                 -> rejected
unregistered exact component       -> rejected
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

The RBOM suite separately proves `PARTIAL` for one matching passport, `UNVERIFIED` for zero matching passports, exact-selector enforcement, duplicate-selector rejection, missing-component rejection, deterministic output, contract sorting/deduplication, registry-digest binding, and refusal of mixed release trains.

## CI evidence checkpoint

Authoritative GitHub Actions PR-merge-ref verification for implementation/docs head:

```text
branch head          6c2d4d312df87cc03bc350ad4daa9fea4aca0b69
PR merge ref         770f1e3617884e9c5fc5f1767dde64d8d1b2fe9f
Release Intelligence PASS
ARI tests            90 passed, 0 failed
Governance regression 67 passed, 0 failed
Python total         157 passed, 0 failed
ARI JSON syntax gates 6 passed
Brand Assets         PASS
```

The six syntax gates cover:

```text
docs/release-intelligence/apc-1.json
docs/contracts/aftergraph-component/1.0.json
docs/contracts/compatibility-edge/1.0.json
docs/contracts/release-passport/1.0.json
docs/contracts/release-registry/1.0.json
docs/contracts/rbom/0.1.json
```

This checkpoint predates only this proof-document commit. The PR latest head must still pass the same applicable gates before merge readiness is claimed.

## PROVED

The Phase 1 implementation proves, within the synthetic evidence boundary, that Governance can:

1. construct a deterministic, digest-bound Release Registry from validated exact-subject release documents;
2. fail closed on malformed source documents, digest mismatch, divergent duplicate exact identities, and conflicting passport/manifest identity;
3. preserve Registry snapshot integrity across caller-side mutation boundaries;
4. query exact compatibility without hidden `latest` resolution and without duplicating graph state semantics;
5. preserve PASS, FAIL, UNKNOWN, STALE, and N/A distinctions;
6. build an exact RBOM for independently versioned components;
7. distinguish full, partial, and absent matching-passport coverage without inflating that state into blanket platform verification;
8. keep Release Registry and RBOM as derived release-intelligence artifacts rather than runtime authority sources.

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
