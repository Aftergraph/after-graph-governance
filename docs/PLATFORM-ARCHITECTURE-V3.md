# Aftergraph Platform Architecture V3

**Status:** Canonical — platform planes, ownership, naming.
**Date:** 2026-09-08
**Owner:** Aftergraph portfolio control
**Supersedes:** Nothing (first plane-level contract; complements
`PLATFORM-RECONCILIATION-V1.md` (execution ledger) and
`REPOSITORY-REGISTRY-v0.1.md` (repo/worktree controls)).

---

## 1. The seven planes

| # | Plane | Canonical repo(s) | Owns | Must not own |
|---|---|---|---|---|
| 1 | Intelligence | `work-intelligence-v2`, `context-continuity` | observation → WorkItem inference; portable continuity/state-transfer, receiver handshake and cross-runtime handoff | authority, enforcement, durable execution, verification |
| 2 | Authority | `aie` | mission/principal/delegation/budget/revocation semantics | runtime enforcement |
| 3 | Trust | `trust-gateway` | principal resolution, identity, tenant isolation, admission, revocation enforcement | authority semantics |
| 4 | Runtime | `runtime` | agent lifecycle, orchestration, dispatch, checkpoints, metering, observability | durable execution, trust enforcement |
| 5 | Execution | `works-execution` | durable WorkGraph, leases, workers, retries, receipts, evidence | agent operation |
| 6 | Verification | `sentinel` | exact-subject verification, stale invalidation, evidence-backed verdicts | execution (never self-verify) |
| 7 | Experience | `studio` | missions, work, agents, evidence, approvals, incidents, costs, topology | platform runtimes |

Runtime-vs-WORKS boundary (normative):

- Runtime owns **how an agent operates**.
- WORKS owns **how work becomes durable, governed, replayable execution**.
- Runtime submits execution intent; WORKS owns lease/state/evidence.
- Runtime cannot bypass WORKS where durable execution is required.

Continuity boundary (normative):

- ACC / `context-continuity` owns **portable transfer of actionable context/state** across model, agent, session and runtime boundaries.
- ACC may carry mission, authority and evidence references, but it does not define success, grant authority, execute work or establish proof.
- Runtime owns in-process/session operational state; WORKS owns durable execution state; ACC owns transfer semantics between boundaries.
- A continuity capsule is inert until admitted and acted upon by the receiving runtime/trust boundary.

Verification independence (normative):

- The system that executes work may not declare verified completion.
- Verdicts cite exact subject SHAs; moved subjects invalidate (STALE).

---

## 2. Cross-cutting systems

| System | Repo | Role |
|---|---|---|
| Governance | `after-graph-governance` | topology, registry, contracts, org-state, invariants |
| Evaluation / Continuity Bench | `continuum` | fault injection, continuity/containment evaluation, recovery measurement; never canonical mission/authority/execution truth |
| Models | `afm`, `llm-research-development`, `model-registry` | Research → Experiment → Evaluate → Gate → Register → Serve |
| Research | `intelligence-systems-research` | scientific claims, reproducibility, Mission Contract research; never runtime authority |
| Skills | `skills-vault` | capability supply chain (identity/version/provenance per skill) |
| Brand | `brand` | Brand OS, tokens, masterbrand hierarchy |
| Docs | `docs` | developer portal; contracts discoverable; exact-source links |
| Org control | `.github` | reusable CI, security policy, repo bootstrap/doctor |
| Public entry | `aftergraph.org` | landing, launcher, status, product routing |
| Operations | `aftergraph-cron-fabric` | read-only/sensor-first schedules, wakeups and Telegram Ops delivery; not canonical mission/runtime state |

---

## 3. Product hierarchy (masterbrand)

Positioning: **Infrastructure for verified intelligent systems.**

Tier 1 (`X by Aftergraph`):

- Studio by Aftergraph (operator control plane)
- Sentinel by Aftergraph (independent verification)
- Work Intelligence by Aftergraph (work understanding)
- Continuum by Aftergraph (continuity and containment evaluation)

Infrastructure (no suffix required): Aftergraph Runtime, Trust Gateway,
WORKS, Aftergraph Governance, Aftergraph Skills, Aftergraph Models, ACC.

Canonical lifecycle:

```text
Intent → Intelligence → Authority → Trust → Runtime → Execution
→ Evidence → Verification → Verified Outcome
```

Portable handoff is orthogonal to this lifecycle:

```text
Runtime/session A → ACC capsule + receiver handshake → Runtime/session B
```

Evaluation is also orthogonal:

```text
Continuum → fault injection / recovery / containment / continuity measurement
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

## 7. Runtime ownership purification (2026-09-08)

Wave 6 may temporarily contain migrated packages whose implementation ownership predates the canonical seven-plane split. Presence inside `Aftergraph/runtime` does not override the ownership table above.

The following responsibilities are transitional and MUST converge toward the canonical owner before Runtime can claim plane-pure completion:

| Transitional runtime responsibility | Canonical destination / boundary |
|---|---|
| principal / identity resolution | Trust Gateway; AIE owns authority semantics |
| authorization/admission/policy enforcement | Trust Gateway |
| institutional/governance rule truth | Governance / AIE semantics; Trust Gateway enforcement |
| durable spend/budget ledger | WORKS where tied to durable execution; Runtime may emit metering observations |
| durable knowledge / institutional memory | WORKS Company Brain |
| portable session/context transfer | ACC / `context-continuity` |
| schedule/wakeup semantics | Runtime |
| provider-specific cron/Telegram operations | Cron Fabric adapter surface |

Migration is consumer-first and evidence-gated. Do not delete or move code merely to satisfy topology; first establish target contracts, migrate consumers, verify exact-head behavior, and only then retire legacy ownership.
