# Aftergraph 26 Runtime & Wie Reconciliation Amendment

**Date:** 2026-09-08  
**Status:** Normative amendment to the approved Aftergraph 26 / ARS / APC / ARI design  
**Scope owner:** `Aftergraph/after-graph-governance`  
**Amends:** `2026-09-07-aftergraph-release-lifecycle-compatibility-standard-design.md` and its ARI companion

---

## 1. Why this amendment exists

The approved design was written against an organization cut where Aftergraph Runtime was still a target-state plane and the public Work Intelligence product name had not yet converged to **Wie by Aftergraph**.

The implementation moved before the spec merged. Governance must follow repository reality rather than preserve an already-stale snapshot for aesthetic neatness.

This amendment changes only facts that have become false. It does not reopen the approved separation between public generation, technical compatibility, component versions, contracts, models, lifecycle, or exact evidence.

---

## 2. Runtime is now canonical, not planned

Governance commit `20257c0a6e53a7ed4e70175a67451665fa2aa792` registered `Aftergraph/runtime` as the canonical Runtime repository.

The Runtime charter owns agent lifecycle, mission execution lifecycle, orchestration/dispatch, harness and tool-invocation orchestration, checkpoints/recovery hooks, scheduling/resource metering, runtime observability, model-edge integration, execution adapters, and runtime SDKs.

Runtime explicitly does **not** own:

- durable WorkGraph execution, leases, or receipts, which remain WORKS responsibilities;
- principal resolution, admission, or revocation, which remain Trust Gateway responsibilities;
- authority semantics, which remain AIE responsibilities;
- verification verdicts, which remain verifier responsibilities.

The following statements in the base design are therefore superseded:

```text
Runtime remains planned until a canonical implementation exists.
Runtime (when actually established)
No design may create a canonical Runtime implementation.
```

They are replaced by:

> **Aftergraph Runtime is an established canonical platform repository. Canonical repository existence does not itself prove `APC-1/runtime` conformance. Any runtime compatibility claim still requires exact component identity plus machine-readable conformance evidence.**

This distinction is important: topology existence is not compatibility evidence.

---

## 3. Runtime migration state

Runtime is not merely an empty charter. Wave 6 migration from `autonomous-venture-company` has begun and has already landed independently versioned packages including runtime metrics, observability, invariants, peer protocol, telemetry, incident handling, agent relay, and agent harness.

The Runtime README/status surfaces MUST be reconciled when they still claim "No runtime code yet" after package migration has landed.

The migration rule remains:

```text
AVC source responsibility
        ↓ classify ownership
canonical target repository
        ↓ migrate with tests/evidence
consumer migration
        ↓
remove active legacy responsibility
```

A copied package does not complete AVC dissolution by itself. Consumer migration and active-identifier cleanup remain required before the old responsibility is considered retired.

---

## 4. Canonical repository count

The canonical Governance topology now contains **21 platform repositories**, including Runtime.

`sentinel-firetest` remains an ephemeral proof/test repository and is outside the canonical platform topology.

Therefore the organization may contain more installed repositories than the canonical platform count. Public product identity MUST NOT be derived from either count.

Any base-design wording that describes the current state as "20 canonical platform repositories plus one ephemeral repository" is stale and is superseded by this amendment.

Canonical topology count at this evidence cut:

```text
21 canonical platform repositories
+ ephemeral/test repositories outside canonical topology where applicable
```

Counts remain generated/projection facts, not branding primitives.

---

## 5. Wie by Aftergraph is the public product identity

The public Work Intelligence experience has converged on the product identity:

```text
Wie by Aftergraph
```

The canonical implementation repository identities remain:

```text
Aftergraph/wi-backend
Aftergraph/wi-frontend
```

Historical repository names such as `work-intelligence-v2` and `work-intelligence-web` may remain only where required for compatibility aliases or exact historical provenance.

The public product-family entries in the base design are therefore amended from:

```text
Work Intelligence by Aftergraph
```

to:

```text
Wie by Aftergraph
```

with the product responsibility unchanged: source-neutral observations, WorkItem understanding/review, and the specialist least-privilege browser experience around that canonical backend state.

The boundary remains non-negotiable:

```text
Wie WorkItem != WORKS Work
UI projection != canonical backend state
approval != execution
```

Internal environment variables, service-unit names, compatibility filenames, or old identifiers do not become public product names merely because migration has not yet removed them.

---

## 6. APC profile mapping after reconciliation

The illustrative APC mapping is now:

| System | Primary APC profile | Reconciliation note |
|---|---|---|
| AIE | `authority` | unchanged |
| Trust Gateway | `service` | unchanged |
| Aftergraph Runtime | `runtime` | canonical repository exists; conformance still requires evidence |
| WORKS | `execution` | unchanged |
| Sentinel | `verifier` | software-domain verifier, not universal verifier |
| Studio | `product` | unchanged |
| Wie frontend/backend | `product` and/or `service` | repository role determines applicable profile |
| AFM / promoted models | `model` | unchanged |
| ISR/AIE research artifacts | `research` where meaningful | research status does not imply production compatibility |

No row in this table is itself a conformance receipt.

---

## 7. Sentinel reconciliation

Sentinel has continued to mature materially after the original design cut, including additional deterministic rules, security hardening, benchmark cases, receipt/console work, and self-dogfood verification.

That maturity does **not** alter its architectural boundary:

> Sentinel remains the software-domain verifier. Platform Verification remains an extensible capability and may use other independent verifiers for non-software subjects.

Release Intelligence may consume Sentinel evidence for software release subjects without granting Sentinel universal release authority.

---

## 8. AVC lifecycle reconciliation

`autonomous-venture-company` is an active migration source while responsibilities are being decomposed into canonical Aftergraph repositories.

The active canonical role `venture-os-consumer` is inconsistent with the V3 migration policy that forbids that role as a new active identifier.

Canonical Governance projections SHOULD converge on a migration-oriented lifecycle/role such as:

```text
plane: migration
role: migration-source
lifecycle: legacy
```

Historical records MAY retain `venture-os-consumer` for provenance.

This amendment does not archive or delete AVC and does not declare the migration complete.

---

## 9. ARI implications

The approved ARI Phase 0/1 implementation remains valid.

The new Runtime repository strengthens the need for ARI rather than changing its core semantics:

- Runtime can publish an exact `aftergraph-component/1.0` manifest when its release identity is ready.
- A Runtime manifest may declare the `runtime` profile only as a declaration.
- `APC-1/runtime: PASS` requires applicable conformance evidence.
- Runtime ↔ Trust and Runtime ↔ WORKS compatibility require explicit evidence-bearing edges.
- Absence of such edges remains `UNKNOWN`, never inferred `PASS` from shared branding or topology membership.
- RBOM composition may include Runtime without claiming the whole deployment is verified.

No synthetic Phase 0/1 example is retroactively promoted into a live Runtime compatibility claim.

---

## 10. Supersession map

Where the base design conflicts with this amendment, this amendment wins for current-state facts.

Specifically:

1. `Runtime planned` → **Runtime canonical; APC conformance unproven until evidenced**.
2. `20 canonical repositories` → **21 canonical topology repositories at this evidence cut**.
3. public `Work Intelligence by Aftergraph` → **Wie by Aftergraph**.
4. active AVC `venture-os-consumer` framing → **Legacy migration-source target framing**.
5. `Runtime (when established)` → **Runtime**, while preserving capability boundaries.

All other approved ARS/1, APC-1, lifecycle, version-skew, evidence, upgrade, and ARI semantics remain unchanged.

---

## 11. Immediate implementation consequences

Before the ARI stack is integrated to `main`:

1. PR #36 must carry this amendment.
2. PR #38 must stop claiming Runtime is still planned and instead state that it makes no live `APC-1/runtime` claim.
3. PR #39 remains valid because Registry/RBOM/query semantics are exact-subject and topology-independent.
4. Canonical topology/dependency projections must migrate from old Work Intelligence repository slugs to `wi-backend` / `wi-frontend`.
5. AVC canonical role must be reconciled away from the forbidden active `venture-os-consumer` identifier.
6. Generated org-state must be regenerated by its authorized exact-head workflow rather than manually edited.
7. Public/docs projections must consume normalized Governance truth instead of preserving parallel repository-name/count tables.

---

## 12. Reconciled target statement

The current target is now:

> **Aftergraph 26 · Convergence is one public generation over independently versioned products and platform components. APC-1 expresses technical compatibility. Runtime is now a canonical component of that platform, Wie is the public Work Intelligence product identity, and neither topology membership nor branding substitutes for exact compatibility evidence.**
