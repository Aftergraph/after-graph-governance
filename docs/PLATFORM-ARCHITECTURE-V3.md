# Aftergraph Platform Architecture V3

**Status:** Canonical — platform planes, ownership, naming.
**Date:** 2026-09-07
**Owner:** Aftergraph portfolio control
**Supersedes:** Nothing (first plane-level contract; complements
`PLATFORM-RECONCILIATION-V1.md` (execution ledger) and
`REPOSITORY-REGISTRY-v0.1.md` (repo/worktree controls)).

---

## 1. The seven planes

| # | Plane | Canonical repo(s) | Owns | Must not own |
|---|---|---|---|---|
| 1 | Intelligence | `work-intelligence-v2`, `continuum` | observation → WorkItem inference; session continuity, recovery, handoff | authority, enforcement, execution |
| 2 | Authority | `aie` | mission/principal/delegation/budget/revocation semantics | runtime enforcement |
| 3 | Trust | `trust-gateway` | principal resolution, identity, tenant isolation, admission, revocation enforcement | authority semantics |
| 4 | Runtime | `runtime` (to be established, WAVE 6) | agent lifecycle, orchestration, dispatch, checkpoints, metering, observability | durable execution, trust enforcement |
| 5 | Execution | `works-execution` | durable WorkGraph, leases, workers, retries, receipts, evidence | agent operation |
| 6 | Verification | `sentinel` | exact-subject verification, stale invalidation, evidence-backed verdicts | execution (never self-verify) |
| 7 | Experience | `studio` | missions, work, agents, evidence, approvals, incidents, costs, topology | platform runtimes |

Runtime-vs-WORKS boundary (normative):

- Runtime owns **how an agent operates**.
- WORKS owns **how work becomes durable, governed, replayable execution**.
- Runtime submits execution intent; WORKS owns lease/state/evidence.
- Runtime cannot bypass WORKS where durable execution is required.

Verification independence (normative):

- The system that executes work may not declare verified completion.
- Verdicts cite exact subject SHAs; moved subjects invalidate (STALE).

---

## 2. Cross-cutting systems

| System | Repo | Role |
|---|---|---|
| Governance | `after-graph-governance` | topology, registry, contracts, org-state, invariants |
| Models | `afm`, `llm-research-development`, `model-registry` | Research → Experiment → Evaluate → Gate → Register → Serve |
| Research | `intelligence-systems-research` | scientific claims, reproducibility; never runtime authority |
| Skills | `skills-vault` | capability supply chain (identity/version/provenance per skill) |
| Brand | `brand` | Brand OS, tokens, masterbrand hierarchy |
| Docs | `docs` | developer portal; contracts discoverable; exact-source links |
| Org control | `.github` | reusable CI, security policy, repo bootstrap/doctor |
| Public entry | `aftergraph.org` | landing, launcher, status, product routing |

---

## 3. Product hierarchy (masterbrand)

Positioning: **Infrastructure for verified intelligent systems.**

Tier 1 (`X by Aftergraph`):

- Studio by Aftergraph (operator control plane)
- Sentinel by Aftergraph (independent verification)
- Work Intelligence by Aftergraph (work understanding)
- Continuum by Aftergraph (persistent context)

Infrastructure (no suffix required): Aftergraph Runtime, Trust Gateway,
WORKS, Aftergraph Governance, Aftergraph Skills, Aftergraph Models.

Canonical lifecycle:

```text
Intent → Intelligence → Authority → Trust → Runtime → Execution
→ Evidence → Verification → Verified Outcome
```

---

## 4. Namespace policy

- Package namespace: `@aftergraph/*`.
- Forbidden as active identifiers: `AVC`, `avc-*`, `@avc/*`,
  `Autonomous Venture Company`, `venture-os-consumer`
  (legacy role — archived entries only).
- Historical records may retain old names for provenance.
- Migration order per package (§7 of mandate): consumers mapped →
  destination created → code/history moved → name established →
  consumers migrated → old dep eliminated → zero-stale-imports gate
  (`grep @avc/` clean except allowlisted provenance).

---

## 5. AVC dissolution policy

`autonomous-venture-company` is a migration source only: no new
canonical responsibilities during migration. Archive requires ALL of:

- zero active `@avc/*` (minus allowlisted provenance)
- zero active AVC services / production deploys
- zero canonical AVC contracts
- zero unclassified packages/apps/skills/ML/cells/infra
- all target mains green at exact HEAD
- topology + registry + org-state regenerated
- owner approval (§16 destructive-action policy)

---

## 6. Conformance

- Topology: `docs/platform-topology/1.0.json` (currently 20 repos).
- Registry: `docs/REPOSITORY-REGISTRY-v0.1.md`.
- Exact-head truth: `latest-org-state.json` (regenerate, never hand-edit).
- Contracts: `docs/contracts/<name>/<version>.json`; one owner each.
- Every migration slice: verification section per mandate §14;
  only VERIFIED counts toward dissolution.
