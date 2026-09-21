# Jev Sidecar v0.1

Status: experimental cross-repository governance contract.

Jev is a typed probabilistic decision sidecar. It is not an authority, execution, evidence, or verification plane.

Canonical law:

> Jev may choose among permitted options. Jev may never make an option permitted.

## Ownership

- Governance owns the cross-repository decision-class contract and promotion semantics.
- Runtime owns runtime orchestration and guarded arbitration.
- AIE owns authority and delegation semantics.
- Trust Gateway owns admission, policy, approvals, and revocation enforcement.
- WORKS owns durable execution and canonical execution evidence.
- Sentinel or repository-native deterministic gates own independent verification.
- Skills Vault / SABI own skill capability/effect/evidence contracts.
- ISR owns preregistered empirical evaluation and calibration evidence.

## Modes

- `disabled`: Jev is not queried.
- `shadow`: Jev is queried and observed, but cannot affect the effective choice.
- `guarded`: Jev may change the effective choice only inside a deterministic candidate set and only when class-specific promotion evidence remains qualified.

A new decision class MUST start in `shadow`. A provider/model change or invalid promotion evidence MUST downgrade effectful use to `shadow`.

## Security

Every Jev call uses a bounded state projection. Never include raw credentials, secrets, unnecessary PII, or authority grants that the model can reinterpret.

Every observation MUST state:

- `authorizes_effect: false`
- `claims_authority: false`
- `canonical_evidence: false`
- `independent_verification: false`

## Files

- `0.1.registry.json` — canonical decision-class registry.
- `0.1.observation.schema.json` — non-authoritative decision observation contract.
- `0.1.promotion.schema.json` — class-specific guarded-promotion evidence contract.

Tracked by Aftergraph/after-graph-governance#180.
