# AVC Identity-Core → Aftergraph Mapping V1 (Wave 5 finding)

**Status:** Analysis — no code moved. Owner decisions required before migration.
**Date:** 2026-09-07
**Sources:** `autonomous-venture-company/packages/identity-core/src`
(identities, principals, roles, memberships, organizations, sessions,
invitations) vs TG `platform-identity.js` + AIE `principal/1.0`.

## Principal kinds

| AVC | TG + AIE | Verdict |
|---|---|---|
| human | human | ALREADY REPRESENTED |
| agent | agent | ALREADY REPRESENTED |
| service | service | ALREADY REPRESENTED |
| peer (crypto node, peer-protocol) | — (TG/AIE have `worker` instead) | AVC-ONLY — owner: keep peer-protocol or drop? |
| — | worker | AFTERGRAPH-ONLY — AVC agent *kinds* (executor/planner/reviewer/daemon) are a different axis, not a substitute |

## Identifiers

| AVC | Aftergraph | Verdict |
|---|---|---|
| principalId = uuid | `prn_<32hex>` (TG bindings, AIE pattern) | CONFLICTING — migration needs an ID-mapping table, never silent reformat |
| identity/principal split (person vs system rep) | TG `user:`/`bot:` identityRef prefixes | COMPATIBLE semantics, different encoding — adapter, not remodel |

## Human governance (AVC-only, fills a real gap)

AVC `roles.ts`: owner > executive_operator > reviewer > auditor > viewer
+ 8 human actions (read/write/approve/audit/manage_secrets/manage_trust/
manage_updates/manage_setup). TG has agent roles only; no human
approval-authority model exists in Aftergraph. Candidate: KEEP as the
human-governance layer (Wave 5/8 boundary), do not dissolve into agent roles.

## Memberships / organizations / sessions / invitations

Standard multi-tenant shapes (org → membership → session). TG resolves
tenants via `resolveTenant` + bindings; semantics overlap ~80%.
Migration = adapter + conformance test per entity, not remodel.
Sessions: compare TG operator-session model before moving.

## What NOT to do

- Do not rename `worker`↔`peer` to force agreement — different concepts.
- Do not reformat uuid↔prn_ IDs in flight — mapping table with provenance.
- Do not dissolve human roles into agent capabilities — separate axes
  (AVC's own code keeps them disjoint deliberately).
