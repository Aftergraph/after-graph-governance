# AVC Tenant-Core → Aftergraph Mapping V1 (Wave 5 finding)

**Status:** Analysis — no code moved. Owner decisions required before migration.
**Date:** 2026-09-07
**Sources:** `autonomous-venture-company/packages/tenant-core/src`
(repositories: Organization/ProductInstance/Tenant/Workspace + tests)
and `packages/contracts/src/tenancy.ts`, vs TG `tenant-gateway.js`,
`tenants.js`, `tenant-access.js`, `platform-identity.js`.

## Layer mismatch (the key finding)

| AVC tenant-core | TG tenants | Verdict |
|---|---|---|
| Management-plane tenant **admin**: CRUD + lifecycle (suspend/export/delete) over org → workspace → tenant → product-instance | Runtime-plane tenant **isolation**: spawned gateway processes, per-tenant jails, `tnt_<id>_` token prefixes, bindings | COMPLEMENTARY layers, not competitors. No overlap to dissolve. |

## Lifecycle model (AVC-only, fills a real gap)

- Organization: active / suspended / closing / deleted
- Workspace: active / read_only / archived (+ modes local / synced / fleet)
- Tenant: active / suspended / exporting / deleting / deleted,
  guarded transitions (`canTransitionTenant`), timestamp side-effects
  (suspendedAt / exportStartedAt / deletionRequestedAt / deletedAt)
- TG has **zero** tenant lifecycle admin: bindings are created, never
  suspended, exported, or deleted. No `suspend`/`deleteTenant` path exists.

Candidate: KEEP as the tenant-admin layer (Wave 5/8 boundary), adapted
from in-memory stub to TG's SQLite backend. Do not dissolve into
runtime bindings — different concerns (admin vs isolation).

## Identity formats (same conflict as identity mapping)

- AVC tenant IDs: uuid. TG: `ten_<32hex>` (TENANT_ID_RE).
- Same rule: ID-mapping table with provenance on migration, never
  silent reformat.

## Workspace / ProductInstance

- No Aftergraph equivalent (TG rooms ≠ workspaces; WI2 has no
  workspace entity). Classify with Studio/product-cell work (Wave 8/10):
  workspace may belong to the operator surface, ProductInstance to
  product cells — owner decision, not assumed here.

## What NOT to do

- Do not merge tenant-admin into `tenant-gateway.js` spawn logic.
- Do not invent suspend/delete semantics inside runtime isolation.
- Repository pattern (`TenantRepository` etc.) is an implementation
  detail — migrate the lifecycle state machine + transition guards,
  not the in-memory Map stub.
