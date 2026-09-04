# ABDE BRAND ARCHITECTURE — v0.2 (PROVISIONAL)

**Status:** PROVISIONAL — ABDE Intelligence is NOT trademark cleared. No irreversible branding until clearance.
**Date:** 2026-09-04
**Authority:** Owner-approved provisional architecture (see `docs/PLATFORM-BOUNDARY-CHARTER-v0.1.md`, `intelligence-systems-research/docs/BRAND-STATUS-2026-09-04.md`).

---

## 1. Brand hierarchy

```
ABDE Intelligence                     (provisional company / institutional umbrella candidate)
├── ABDE Platform                     (user/developer product platform)
│   ├── Agent Workforce               (in trust-gateway)
│   ├── Trust Gateway                 (Aftergraph/trust-gateway)
│   ├── WORKS                         (Aftergraph/works-execution)
│   └── Adaptive Workspace / Plugin Runtime
├── ABDE Research                     (research-facing institutional identity)
│   └── Jonas Abde Intelligence Systems Research Program
├── AIE                               (independent standards track)
└── After Graph                       (research thesis / initiative / narrative)
```

## 2. Naming principles

1. One umbrella (ABDE Intelligence), few prefixed names.
2. Technical systems keep their established names (Trust Gateway, WORKS).
3. Standards keep vendor-neutral names (AIE, SPEC-*).
4. Research initiatives keep their narrative names (After Graph, MISSION-Bench).
5. Do not rename anything until the trademark-clearance gate passes (Section 17).

## 3. Public taxonomy

Public-facing names a reader encounters: ABDE Intelligence (company), ABDE Platform (product), Trust Gateway, WORKS, ABDE Research, AIE, After Graph, STUDY-*, MISSION-Bench.

## 4. Technical taxonomy

| System | Repo | Role |
|---|---|---|
| Trust Gateway | Aftergraph/trust-gateway | Runtime control and enforcement plane: policy, approvals, budgets, rate limits, tenant/auth/RBAC, secrets, audit chain, ComputerSession, plugin mounts |
| WORKS | Aftergraph/works-execution | Durable execution plane: missions, WorkGraph/DAG, scheduler, workers, leases, retry/recovery, sandboxing, execution evidence, quittance/verified settlement |
| Agent Workforce | in trust-gateway | User/developer-facing product layer (specialist bots, console) |

## 5. Research taxonomy

- **ABDE Research** = provisional research-facing identity.
- **Jonas Abde Intelligence Systems Research Program** = the named research program (repo: intelligence-systems-research).
- Studies: STUDY-### (STUDY-011 current: cross-provider replication).
- Benchmarks: MISSION-Bench.
- Boundaries: ISE / VAIE / AIE per `04-ISE-VAIE-AIE-BOUNDARIES.md`.

## 6. Standards taxonomy

- **AIE** (Agentic Institution Engineering) — independent, vendor-neutral standards track.
- **SPEC-*** — normative specifications (SPEC-001 Mission Contract).
- Conformance evidence lives with the standards track; never absorbed into platform marketing.

## 7. Company vs platform vs standards vs research distinction

| Kind | Name | Governs | Claims come from |
|---|---|---|---|
| Company (candidate) | ABDE Intelligence | Institutional umbrella | Owner decision post-clearance |
| Platform | ABDE Platform | Product surface | Runtime + execution evidence |
| Standards | AIE | Normative semantics | Conformance vectors, external interop gates |
| Research | ABDE Research / ISR program | Science | Preregistration, replication, publication lineage |

## 8. ABDE Intelligence provisional status

- LEADING PROVISIONAL BRAND CANDIDATE.
- NOT TRADEMARK CLEARED.
- May appear as "provisional" labels in docs and profiles. May NOT appear in legal claims, purchased domains, org/repo renames, or filings.

## 9. ABDE Platform role

User/developer product platform composed of Agent Workforce, Trust Gateway, WORKS, and the Adaptive Workspace / Plugin Runtime. Platform runtime evidence (L1/L2) does not automatically establish AIE conformance (L3) or scientific claims (L4).

## 10. ABDE Research role

Research-facing institutional identity associated with the ABDE Intelligence working brand. Scientific claims remain governed solely by the research repository's own evidence, study protocols, preregistrations, replication status, and publication lineage.

## 11. AIE independence

AIE is a vendor-neutral independent standards/research track. AIE participates in the broader working ABDE Intelligence research/platform ecosystem while maintaining independent standards governance, claims, conformance evidence, and publication lineage. No platform claim automatically inherits AIE evidence. AIE is NOT renamed "ABDE AIE".

## 12. After Graph role

Research thesis / initiative / intellectual narrative: "the next engineering layer after Prompt → Context → Loop → Graph is institutional control." Kept as a narrative name independent of any final company brand.

## 13. GitHub namespace status

- `@Aftergraph` = TEMPORARY GITHUB NAMESPACE pending final brand clearance.
- No org rename, no repo renames until CLEARED_FOR_MIGRATION.

## 14. Repo naming rules

- Current repo names (trust-gateway, aie, works-execution, intelligence-systems-research, after-graph-governance) remain canonical during the provisional phase.
- Future renames (if cleared) are executed only via a controlled migration plan with owner sign-off.

## 15. Website information architecture

See Section 15 detail in Phase 9 artifact (website IA):

```
ABDE Intelligence
Platform | Developers | Research | Standards | Docs | Company
```
Platform: Agents, Missions, Apps, Tools, Models, Governance, Evidence, Evals.
Research: Intelligence Systems, After Graph, Publications, Studies, Benchmarks.
Standards: AIE, Specifications, Conformance, Interoperability.

## 16. Domain strategy

No domain purchases until CLEARED_FOR_MIGRATION. Candidate domains noted at migration time only.

## 17. Trademark-clearance gate

Separate research task covering: EUIPO/TMview, WIPO, USPTO, UK IPO, Danish/Nordic registers, company-name similarity, GitHub namespace, domains, package registries, major social handles, AI/software collision analysis.

States: `BRAND_CANDIDATE` → `TRADEMARK_REVIEW_REQUIRED` → `CLEARED_FOR_MIGRATION`.

## 18. Migration triggers

Migration (org/repo rename, domain purchase, public legal claim) requires ALL of:
1. `CLEARED_FOR_MIGRATION` state.
2. Owner approval (explicit).
3. Controlled migration plan with rollback notes.

## 19. Migration non-goals

Until cleared: NO org rename, NO repository rename, NO public legal claim, NO expensive domain purchase, NO irreversible brand migration.

## 20. Claim/evidence boundaries

- Runtime evidence (TG L1, WORKS L2) does not establish AIE conformance or scientific claims.
- AIE conformance (L3) does not establish scientific claims (L4).
- ISR evaluates but does not automatically claim.
- Claim inheritance is unidirectional (AIE normative → TG/WORKS operational), never reverse (see PLATFORM-BOUNDARY-CHARTER §2).
- No document may describe any candidate brand as legally cleared.
