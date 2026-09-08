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
| 1 | Intelligence | `wi-backend`, `context-continuity` | observation → canonical WorkItem inference; portable actionable context/state transfer | authority, enforcement, durable execution, continuity verdicts |
| 2 | Authority | `aie` | mission/principal/delegation/budget/revocation semantics | runtime enforcement |
| 3 | Trust | `trust-gateway` | principal resolution, identity, tenant isolation, admission, revocation enforcement | authority semantics |
| 4 | Runtime | `runtime` | agent lifecycle, orchestration, dispatch, checkpoints, metering, observability, model-edge integration | durable execution, trust enforcement, verification verdicts |
| 5 | Execution | `works-execution` | durable WorkGraph, leases, workers, retries, receipts, evidence | agent-operation semantics, authority semantics |
| 6 | Verification | `sentinel`, `continuum` | software-domain exact-HEAD verdicts; continuity/containment fault campaigns and assurance evidence | execution, authority, canonical context transfer |
| 7 | Experience | `studio`, `wi-frontend` | general operator surfaces; Wie specialist browser/BFF experience | canonical runtime/execution truth |

Runtime-vs-WORKS boundary (normative):

- Runtime owns **how an agent operates**.
- WORKS owns **how work becomes durable, governed, replayable execution**.
- Runtime submits execution intent; WORKS owns lease/state/evidence.
- Runtime cannot bypass WORKS where durable execution is required.
- Runtime topology membership does not itself prove any APC compatibility claim.

Context-vs-Continuum boundary (normative):

- `context-continuity` owns portable transfer of actionable context/state.
- ACC / `context-continuity` may carry mission, authority and evidence references, but it does not define success, grant authority, execute work or establish proof.
- Runtime owns in-process/session operational state; WORKS owns durable execution state; ACC owns transfer semantics between those boundaries.
- A continuity capsule is inert until admitted and acted upon by the receiving Runtime/Trust boundary.
- `continuum` owns continuity/containment fault campaigns and assurance.
- Continuum consumes continuity subjects; it does not become the canonical state-transfer layer.

Verification independence (normative):

- The system that executes work may not declare independently verified completion.
- Sentinel is the software-domain verifier; it is not universal platform verification authority.
- Continuum provides continuity/containment assurance for its campaign subjects.
- Other domains may use other independent verifiers.
- Exact-subject verdicts must preserve subject identity and stale invalidation where the verifier contract requires it.

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
| Operations | `aftergraph-cron-fabric` | sensor-first schedules, wakeups and Telegram/Ops delivery; not canonical mission, authority or runtime state |
| Migration source | `autonomous-venture-company` | Legacy AVC lineage only while responsibilities migrate to canonical Aftergraph repositories |

---

## 3. Product hierarchy (masterbrand)

Positioning: **Infrastructure for verified intelligent systems.**

Tier 1 (`X by Aftergraph`):

- Studio by Aftergraph (operator control plane)
- Sentinel by Aftergraph (software-domain verification)
- Wie by Aftergraph (work understanding and specialist work experience)
- Continuum by Aftergraph (continuity and containment assurance)

Infrastructure (no suffix required): Aftergraph Runtime, Trust Gateway,
WORKS, Aftergraph Governance, Aftergraph Skills, Aftergraph Models, ACC.

Canonical lifecycle:

```text
Intent → Intelligence → Authority → Trust → Runtime → Execution
→ Evidence → Verification → Verified Outcome
```

Portable handoff is orthogonal to that lifecycle:

```text
Runtime/session A → ACC capsule + receiver handshake → Runtime/session B
```

Continuity/containment evaluation is also orthogonal:

```text
Continuum → fault injection / recovery / containment / continuity measurement
```

Product names do not replace repository identities. `Wie by Aftergraph` maps to
`wi-backend` plus `wi-frontend`; repository slugs stay canonical for source and
provenance.

---

## 4. Namespace policy

- Package namespace: `@aftergraph/*`.
- Forbidden as new active identifiers: `AVC`, `avc-*`, `@avc/*`,
  `Autonomous Venture Company`, `venture-os-consumer`.
- Historical records may retain old names and roles for provenance.
- Canonical AVC topology role is `migration-source` while dissolution is active.
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

Runtime Wave 6 migration does not by itself complete AVC dissolution. A package
is considered migrated only after ownership, consumers, tests/evidence and stale
imports are reconciled.

---

## 6. Conformance

- Topology: `docs/platform-topology/1.0.json` (currently 21 canonical repos: 12 public / 9 private).
- Registry: `docs/REPOSITORY-REGISTRY-v0.1.md`.
- Exact-head truth: `latest-org-state.json` (regenerate, never hand-edit).
- Contracts: `docs/contracts/<name>/<version>.json`; one owner each.
- Repository topology membership is not a functional, production, scientific, or APC conformance claim.
- Every migration slice: verification section per mandate §14;
  only VERIFIED counts toward dissolution.

---

## 7. Runtime ownership purification

Wave 6 may temporarily contain migrated packages whose implementation ownership predates the canonical seven-plane split. Presence inside `Aftergraph/runtime` does not override the ownership table above.

The following responsibilities are transitional and MUST converge toward the canonical owner before Runtime can claim plane-pure completion:

| Transitional Runtime responsibility | Canonical destination / boundary |
|---|---|
| principal / identity resolution | Trust Gateway; AIE owns authority semantics |
| authorization / admission / policy enforcement | Trust Gateway |
| institutional / governance rule truth | Governance / AIE semantics; Trust Gateway enforcement |
| durable spend / budget ledger | WORKS where tied to durable execution; Runtime may emit metering observations |
| durable knowledge / institutional memory | WORKS Company Brain |
| portable session / context transfer | ACC / `context-continuity` |
| schedule / wakeup semantics | Runtime |
| provider-specific cron / Telegram operations | Cron Fabric adapter surface |

Migration is consumer-first and evidence-gated. Do not delete or move code merely to satisfy topology. First establish target contracts, migrate consumers, verify exact-head behavior, and only then retire legacy ownership.
