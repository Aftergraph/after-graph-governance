# Aftergraph Platform Reconciliation V1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reconcile the complete 19-repository Aftergraph organization into one machine-readable governed topology and align public/system documentation to it.

**Architecture:** Governance gets a slow-changing `platform-topology/1.0` inventory; `org-state-verify.sh` derives live exact-head scope from it. Existing runtime/normative ownership remains separated. The public site consumes/mirrors governance rather than becoming a competing source of truth.

**Tech Stack:** JSON Schema 2020-12, JSON, Bash, jq, YAML, Markdown, GitHub API.

**Spec:** `docs/superpowers/specs/2026-09-07-aftergraph-platform-reconciliation-v1-design.md`

## Global Constraints

- Do not invent new runtime protocols.
- Do not hand-write exact Git SHAs into canonical truth artifacts.
- Do not upgrade research, conformance, runtime or production maturity claims.
- Preserve `Complete != Verified` and evidence-layer separation.
- All 19 installed `Aftergraph/*` repositories use canonical branch `main` at this evidence cut.
- Branch protection/merge queue must be respected even though owner authorized direct-main delivery.

---

### Task 1: Canonical 19-repository topology

**Files:**
- Create: `docs/platform-topology/1.0.json`
- Modify: `docs/contracts/org-state/1.0.json`
- Modify: `scripts/org-state-verify.sh`

- [ ] Add all 19 repositories with role, plane, canonical branch and visibility.
- [ ] Expand the org-state role enum to those roles.
- [ ] Remove the stale `work-intelligence-v2 uses master` schema note.
- [ ] Make `org-state-verify.sh` load repository names/roles from the topology JSON.
- [ ] Replace hard-coded nine-repository fallback validation with topology-derived count.

Verification after checkout:

```bash
jq -e '.schema_version == "platform-topology/1.0" and (.repositories | length) == 19' docs/platform-topology/1.0.json
bash -n scripts/org-state-verify.sh
bash scripts/org-state-verify.sh /tmp/aftergraph-org-state.json
jq -e '.repositories | length == 19' /tmp/aftergraph-org-state.json
```

### Task 2: Dependency and contract reconciliation

**Files:**
- Modify: `dependencies.yml`
- Modify: `docs/cross-repo-contracts.md`

- [ ] Upgrade dependency graph to complete 19-repo coverage.
- [ ] Correct Work Intelligence canonical branch to `main`.
- [ ] Preserve the existing normative contract owner/consumer register.
- [ ] Add platform-wide repository boundary table so non-contract repos have explicit roles without pretending they own normative contracts.

Verification:

```bash
for r in after-graph-governance aie works-execution trust-gateway intelligence-systems-research work-intelligence-v2 work-intelligence-web skills-vault autonomous-venture-company studio brand llm-research-development afm model-registry context-continuity docs aftergraph.org continuum .github; do grep -q "$r" dependencies.yml || exit 1; done
```

### Task 3: Governance front door and execution backlog

**Files:**
- Create: `docs/PLATFORM-RECONCILIATION-V1.md`
- Modify: `README.md`

- [ ] Publish the platform pipeline, 19-repo ownership table and P0/P1/P2 follow-up backlog.
- [ ] Link canonical topology, org-state generator, contract register and reconciliation program from README.
- [ ] Mark `latest-org-state.json` as a generated snapshot whose scope is defined by the topology contract.

### Task 4: Public system-map alignment

**Repository:** `Aftergraph/aftergraph.org`

**Files:**
- Modify: `SYSTEM-MAP.md`
- Modify: `ARCHITECTURE.md`

- [ ] Replace stale 18-repository audit with the 19-repository platform map.
- [ ] State explicitly that governance is canonical and `SYSTEM-MAP.md` is a public rendering/input snapshot.
- [ ] Correct deployment/maturity assertions that are contradicted by current repo READMEs.
- [ ] Route build-time architecture through governance topology + repo-owned truth + docs Knowledge Plane.

### Task 5: Merge and verify

- [ ] Open PR to `main` because repository rules require the merge queue.
- [ ] Enable auto-merge/queue where available.
- [ ] Verify merged `main` file contents and final commit status before claiming completion.
- [ ] Repeat for `aftergraph.org`; if rules allow direct main, use it, otherwise use its required queue.

## Follow-up backlog after this execution

- [ ] P0: regenerate and commit a fresh 19-repository `latest-org-state.json` from GitHub API on an authorized shell/CI runner.
- [ ] P0: define canonical Principal/Tenant/Agent/Service identity architecture.
- [ ] P0: define one production E2E path `Studio → AIE → TG → WORKS → Evidence → Verifier`.
- [ ] P1: reconcile ISR MISSION-Bench, Continuum and ACC benchmark/fault namespaces.
- [ ] P1: make Studio the canonical general-purpose human shell while preserving specialist deployments.
- [ ] P1: remove executable AVC kernel duplication where platform services now own the same concern.
- [ ] P1: have `docs` and `aftergraph.org` import platform topology automatically.
- [ ] P2: billing/entitlements, release trains, SDK packaging and platform-wide SLOs.
