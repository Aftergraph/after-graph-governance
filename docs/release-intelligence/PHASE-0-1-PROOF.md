# Aftergraph Release Intelligence Phase 0/1 Proof

**Date:** 2026-09-07  
**Scope:** Synthetic executable proof of the first ARI compatibility slice  
**Public generation:** Aftergraph 26 · Convergence  
**Compatibility baseline:** APC-1

## Thesis under test

Aftergraph can compute and evidence compatibility across independently versioned components without forcing lockstep repository versions, and can fail closed when required compatibility evidence is absent.

This proof uses deliberately synthetic exact identities. It is not a claim about live Sentinel or WORKS production compatibility.

## Synthetic configuration

```text
Sentinel engine     1.4.0
Source commit       1111111111111111111111111111111111111111
APC profile         APC-1/verifier

WORKS               0.5.1
Source commit       2222222222222222222222222222222222222222

Compatibility edge tested-with
State               PASS
Evidence strength   CE3 integration-verified
Evidence ref        sha256:3333333333333333333333333333333333333333333333333333333333333333

Platform generation Aftergraph 26
Release train        2026.09
```

Neither component uses version `26`. Platform generation and component versioning remain separate.

## Positive compile proof

Command:

```bash
python scripts/ari_compile.py \
  docs/release-intelligence/examples/sentinel.component.json \
  --edge docs/release-intelligence/examples/sentinel-works.edge.json \
  --format text
```

Observed result in the implementation workspace:

```text
APC-1/verifier: PASS
component: sentinel-engine@1.4.0
minimum edge evidence: CE2
unknown required edges: 0
errors: 0
```

Exit code: `0`.

The verifier profile requires at least one declared compatibility edge and CE2-or-stronger evidence. The synthetic `tested-with` edge carries CE3 evidence, so the requirement is met.

## Release Passport proof

Command:

```bash
python scripts/ari_passport.py \
  docs/release-intelligence/examples/sentinel.component.json \
  --edge docs/release-intelligence/examples/sentinel-works.edge.json \
  --artifact-digest sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
```

Observed result included:

```json
{
  "schema": "release-passport/1.0",
  "subject": {
    "component": "sentinel-engine",
    "version": "1.4.0"
  },
  "platform": {
    "compatibility": "APC-1",
    "generation": 26,
    "release_train": "2026.09"
  },
  "conformance": {
    "result": "PASS",
    "profiles": {
      "verifier": "PASS"
    }
  }
}
```

The emitted passport also binds the claim to the synthetic exact source commit, supplied artifact digest, canonical manifest digest, and the qualifying compatibility evidence reference.

Exit code: `0`.

## Fail-closed proof

The same component was compiled without the required compatibility edge:

```bash
python scripts/ari_compile.py \
  docs/release-intelligence/examples/sentinel.component.json \
  --format text
```

Observed result:

```text
APC-1/verifier: UNKNOWN
component: sentinel-engine@1.4.0
minimum edge evidence: CE2
unknown required edges: 1
errors: 0
unknown: APC-1/verifier required edge sentinel-engine@1.4.0#111111111111 -> works@0.5.1#222222222222 lacks CE2 evidence
```

Exit code: `3`.

`ari_passport.py` refuses to emit a positive Release Passport for `UNKNOWN`, `STALE`, `FAIL`, or `N/A` compiler states. Missing evidence therefore cannot be converted into a positive compatibility claim.

## Test evidence

Fresh local verification during this proof pass:

```bash
python -m unittest discover -s scripts -p 'test_ari_*.py' -v
```

Result at the pre-proof checkpoint: **46 tests, 0 failures**. Additional fail-closed compiler tests were then added for empty required-edge declarations and evidence-threshold filtering and verified through their own RED → GREEN cycles. The final authoritative test count is the CI result for the implementation PR, not this prose snapshot.

Core JSON syntax is also gated with `python -m json.tool` for:

```text
docs/release-intelligence/apc-1.json
docs/contracts/aftergraph-component/1.0.json
docs/contracts/compatibility-edge/1.0.json
docs/contracts/release-passport/1.0.json
```

## What this proves

**PROVED:** the Governance implementation can compute `APC-1/verifier` conformance from explicit exact-subject declarations and compatibility evidence, preserve independent component versions, bind a positive result into a Release Passport, and refuse a positive result when required edge evidence is absent or insufficient.

## What this does not prove

**NOT PROVED:**

- production compatibility of live Sentinel and WORKS builds;
- whole-platform APC-1 conformance;
- live runtime capability negotiation;
- deployment drift detection;
- production-observed CE5 evidence;
- Release Simulator or digital-twin correctness;
- external customer/SaaS applicability;
- regulatory certification or compliance.

Those claims require later ARI phases and their own exact evidence.
