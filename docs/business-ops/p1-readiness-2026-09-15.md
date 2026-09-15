# Aftergraph Business Ops — P1 Readiness Record

**Date:** 2026-09-15  
**Scope:** Readiness for implementation planning, not production cutover.  
**Decision:** `READY_FOR_IMPLEMENTATION_PLANNING_WITH_BLOCKERS` / `NOT_READY_FOR_PRODUCTION_CUTOVER`.

## Gate status

| Gate | Status | Evidence / action |
|---|---|---|
| Hermes independent-review changes present | PASS | PR #166 design contains production provenance gate, ChargeFact boundary, explicit ambiguity quarantine and split Billing ownership. |
| ChargeFact draft + characterization vector | PASS | `docs/contracts/business-ops/charge-fact/0.1.schema.json`; `CHG-001`, `CHG-002`. |
| Legacy ambiguity/quarantine vector | PASS | `docs/contracts/business-ops/migration-mapping/0.1.schema.json`; `MAP-002`. |
| Production deployed-source provenance strategy | PASS FOR PLANNING | Strategy below. Current production exact SHA remains unresolved and therefore blocks cutover claims. |
| Security-remediation status for flagged donors | RECORDED / BLOCKING TRANSFER | Four P−1 donor repos remain restricted until credential/history remediation is independently verified. |
| Production database migration ledger | ACCESS BLOCKER RECORDED | Current VDS has no authorized Fly/production DB client path. Acquire through an approved read-only production connection before migration execution. |
| Privacy-safe cardinality baseline definition | PASS FOR PLANNING | Count-only queries and reconciliation classes defined below; values must be captured before shadow/cutover. |
| Billing ownership location | RESOLVED | Billing is currently incubated in `Aftergraph/studio`; `docs/billing/EXTRACTION.md` defines migration to future `Aftergraph/billing`. |

## Production provenance strategy

Current production at `app.rendetalje.dk` is healthy and matches the current RenOS product fingerprint, but exact deployed Git identity is not independently proven. Historical donor docs also record that the runtime did not reliably expose `BUILD_SHA`/`FLY_IMAGE_REF` as a version endpoint.

Before any capability cutover, deployment must emit one immutable provenance tuple:

```text
repository
source_commit_sha
artifact_or_image_digest
deployed_at
environment
release_id_or_deploy_log_ref
```

Preferred implementation: inject `SOURCE_COMMIT`/`BUILD_SHA` during build, bind it to the immutable artifact digest, expose a non-secret `/api/version` or authenticated deployment-attestation endpoint, and preserve the same tuple in deployment logs. Cutover evidence must compare this tuple to the reviewed source head. A frontend asset fingerprint alone is insufficient.

## Production database ledger acquisition

The current VDS does not expose an authorized read-only connection to the Rendetalje production database, and no Fly CLI/session is available. This is intentionally recorded as a blocker rather than bypassed.

**Owner:** Rendetalje production data plane.  
**Acquisition method:** approved read-only DB session or an authenticated maintenance endpoint that returns schema/migration metadata only.  
**Required evidence:** applied migration identifiers/checksums, table/constraint/index inventory, tenant-scope columns/constraints and privacy-safe row counts.  
**Forbidden:** exporting customer rows, credentials, message bodies, access instructions or other PII into Governance evidence.

## Privacy-safe cardinality baseline

Capture counts grouped only by tenant where required and store aggregate values, not rows:

```sql
SELECT count(*) FROM customers;
SELECT count(*) FROM leads;
SELECT count(*) FROM bookings;
SELECT count(*) FROM booking_assignments;
```

If production uses different canonical table names, record the actual names in the migration inventory and map them semantically to `Customer`, `Lead`, `WorkOrder` and `Assignment`. Also record orphan counts for required FKs and duplicate counts for legacy identity keys. No count establishes semantic equivalence by itself; shadow comparison must still run.

## Security transfer blockers

The P−1 remediation queue records credential/history risk in:

- `JonasAbde/rendetalje-agent`;
- `JonasAbde/rendetalje-assistent`;
- `JonasAbde/RenOS-V5`;
- `JonasAbde/rendetalje-clawdbot`.

No affected repository, history or credential artifact may be transferred into Aftergraph until remediation is classified and independently verified. Sanitized contracts/tests may be extracted through explicit allowlisted paths.

## Planning permission

Implementation planning may proceed for the new isolated Business Ops codebase, contracts, tests, adapters and read-only shadow tooling. The following remain blocked until their evidence gates pass:

```text
production schema mutation
production data migration
provider writes through Business Ops
source-of-truth cutover
legacy repository transfer with flagged history
claims of exact-head production equivalence
```

## Machine-readable decision

```yaml
p1_planning_ready: true
production_cutover_ready: false
production_sha_verified: false
production_db_ledger_acquired: false
security_transfer_blockers: 4
charge_fact_contract: business-ops.charge-fact/0.1
migration_mapping_contract: business-ops.migration-mapping/0.1
next_action: write_and_review_implementation_plans_then_execute_non_production_foundation
```
