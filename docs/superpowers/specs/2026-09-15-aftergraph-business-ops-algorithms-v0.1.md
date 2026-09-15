# Aftergraph Business Ops Algorithms v0.1

**Status:** P1 contract/algorithm companion to the owner-approved Thin Domain Kernel design.

**Purpose:** Define deterministic, fail-closed algorithms for identity, context, charge-source facts, governed effects, reconciliation, evidence, proactive exceptions and cutover comparison. These algorithms define semantics; Runtime/Trust/WORKS/Studio remain the canonical platform owners for their respective concerns.

## Global algorithm invariants

1. Tenant scope is explicit on every domain lookup and transition.
2. Missing or ambiguous identity becomes `UNKNOWN`/`AMBIGUOUS`; it is never guessed.
3. Conversation references can nominate candidates but cannot create business truth.
4. Domain intent is not execution; provider acceptance is not reconciliation; execution completion is not verification.
5. Consequential provider effects require immutable intent identity, admission evidence, provider receipt and independent read-back.
6. Charge-source facts never become invoice, ledger or payment truth.
7. Every migration/cutover comparison is reversible until a capability-specific authority switch is explicitly recorded.

## A1 — Resolve Business Context

Input: `tenant_id`, interaction reference, optional explicit entity refs, bounded conversation refs, requested operation.

```text
1. Reject missing tenant_id.
2. Collect explicit canonical IDs from the interaction.
3. Collect conversation-linked candidate refs; mark them NON_AUTHORITATIVE.
4. Query Business Ops repositories for explicit IDs under tenant scope.
5. If an explicit ID resolves to exactly one entity, select it.
6. Otherwise query candidate entities using bounded search keys.
7. If zero candidates: return UNKNOWN with source/freshness metadata.
8. If multiple materially plausible candidates: return AMBIGUOUS; do not select one.
9. If one candidate survives deterministic rules: return RESOLVED with canonical ID.
10. Attach source, observed_at, freshness and uncertainty to every field.
```

## A2 — Map Legacy Identity / Quarantine

Input: source namespace/type/id, tenant scope, known deterministic mappings, reviewed mappings.

```text
1. Look up an existing immutable mapping by (tenant, source_system, source_type, source_id).
2. If status EXACT or REVIEWED and target still exists in tenant: return target.
3. Generate candidate targets only from declared deterministic keys/adapters.
4. If exactly one candidate satisfies all required invariants: emit EXACT mapping.
5. If zero candidates: emit AMBIGUOUS mapping with target_entity_id = null.
6. If more than one candidate: emit AMBIGUOUS mapping with target_entity_id = null.
7. AMBIGUOUS mappings never create/attach a canonical entity.
8. Downstream reads surface degraded/unknown identity until reviewed.
9. Human review may create a new REVIEWED mapping; history is append-only.
```

## A3 — Derive ChargeFact

Input: canonical WorkOrder, ExecutionActuals, applicable ServiceAgreementVersion/policy ref, EvidenceRefs.

```text
1. Require all inputs to share tenant_id.
2. Require WorkOrder state to permit billing-source derivation.
3. Require actual work minutes to be non-negative integer facts from ExecutionActuals.
4. Require an explicit actuals_verification_ref/evidence gate defined by the tenant/domain policy.
5. Require immutable policy id + version provenance.
6. Reject cancelled/voided work and unresolved correction conflicts.
7. Canonicalize the charge-source payload and compute SHA-256 provenance digest.
8. Emit immutable ChargeFact with refs, actual_work_minutes, policy_ref, evidence_refs and provenance.
9. Do NOT emit rate, tax, invoice amount, invoice number, delivery or payment state.
10. Billing adapters may serialize eligible facts into `aftergraph.billing.source.v1`; Billing remains authoritative for financial readiness and invoice lifecycle.
```

## A4 — Propose and Execute a Governed Effect

```text
Domain decision
  -> immutable ActionIntent / capability request
  -> AIE authority evaluation
  -> Trust admission + approval when required
  -> Runtime dispatch
  -> WORKS durable attempt
  -> provider call
  -> provider receipt
  -> read-back
  -> domain reconciliation
  -> EvidenceRef
```

Rules: same idempotency identity on retries; no self-approval; denied/expired authority stops before provider effect; ambiguous provider outcome remains `EXECUTING_OR_UNKNOWN` until reconciled.

## A5 — Provider Read-back Reconciliation

```text
1. No provider receipt -> do not claim executed; enter UNKNOWN/RECONCILE_REQUIRED if effect may have escaped.
2. Receipt + matching read-back -> RECONCILED.
3. Receipt + non-matching read-back -> MISMATCH exception; no false domain success.
4. Timeout during read-back -> keep pending/unknown, retry bounded reconciliation only.
5. Persist provider references in WORKS/evidence owner; Business Ops stores only domain-relevant reference/projection.
```

## A6 — EvidenceRef Integrity

For structured evidence, canonicalize keys recursively and hash UTF-8 canonical JSON. For binary evidence, hash bytes. Store digest, type, source reference, subject reference and observation time; do not copy raw secret/PII payloads into Governance or model context. A digest mismatch invalidates the reference for verification-sensitive transitions.

## A7 — Exception Deduplication and Attention

```text
key = hash(tenant_id, exception_type, canonical_subject_ref, material_condition_version)
```

Existing open key => update observation/freshness, do not create duplicate interruption. Material condition change => new version/key. Resolved key can reopen only with a new material observation. Notification policy is exception-first and separate from authority.

## A8 — Dual-read Shadow Comparison

```text
1. Read legacy and target state at bounded comparable snapshots.
2. Normalize only declared semantic fields; preserve source refs.
3. Compare identity, lifecycle state, required relationships and policy/version refs.
4. Classify SAME, EXPECTED_DIFFERENCE, MISMATCH or UNCOMPARABLE.
5. Any unexplained MISMATCH blocks capability cutover.
6. Record privacy-safe counts and mismatch classes, not customer payloads, in Governance evidence.
```

## A9 — Capability Cutover Gate

A capability may switch authority only when: target contract/version is frozen; donor characterization vectors pass; shadow comparison has no unexplained material mismatch; production release provenance can bind deployed source; relevant secret/history blockers are cleared; rollback/read-only legacy path exists; owner records the source-of-truth switch. Failure of any gate leaves current production authoritative.

## A10 — Deterministic Estimate Boundary

The generic kernel may store Estimate inputs/result/provenance but tenant-specific estimation logic remains in the Rendetalje pack until cross-tenant evidence justifies extraction. Every estimate binds estimator version + policy version + input provenance. Proposal/Agreement creation must copy the accepted commercial terms explicitly; an Estimate is never silently promoted to an Agreement.
