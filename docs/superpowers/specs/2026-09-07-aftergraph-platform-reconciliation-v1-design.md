# Aftergraph Platform Reconciliation V1 — Design

**Date:** 2026-09-07  
**Status:** Approved for execution by owner instruction  
**Scope owner:** `Aftergraph/after-graph-governance`

## Goal

Make the current Aftergraph organization operate as one governed polyrepo platform instead of a growing set of partially reconciled repositories.

The V1 target is:

```text
19 repositories
→ one canonical topology
→ one ownership graph
→ one contract registry
→ one generated exact-head truth surface
→ one public system map
```

This reconciliation does **not** merge repositories, invent new runtime protocols, or transfer scientific/normative evidence between repos.

## Architecture

Aftergraph remains polyrepo internally and presents one platform externally.

```text
Public / Knowledge
  aftergraph.org · docs · .github · brand
          ↓
Experience
  studio · work-intelligence-web · autonomous-venture-company
          ↓
Intent / Work / Continuity
  work-intelligence-v2 · context-continuity
          ↓
Institution / Enforcement / Execution
  aie → trust-gateway → works-execution
          ↓
Capabilities / Models
  skills-vault · llm-research-development · afm · model-registry
          ↓
Assurance / Verification
  intelligence-systems-research · continuum
          ↓
Verified outcomes

Cross-cutting owner: after-graph-governance
```

## Canonical boundaries

- `after-graph-governance` owns platform topology, cross-repo boundaries, contract registration and generated org-state mechanics.
- `aie` owns normative institution/authority semantics; it does not execute work.
- `trust-gateway` owns runtime admission/enforcement; it does not become durable execution truth.
- `works-execution` owns durable execution, work state and execution evidence.
- `studio` is the general-purpose human experience/reference shell; specialist surfaces remain valid.
- `work-intelligence-v2` owns observation → WorkItem inference; `WorkItem != WORKS Work`.
- `context-continuity` owns portable actionable state transfer only; it neither grants authority nor verifies outcomes.
- `intelligence-systems-research` owns scientific claims, SPEC-001/MISSION-Bench methodology and assurance evidence.
- `continuum` owns continuity/containment verification campaigns; it must not silently redefine ISR scientific benchmarks.
- `skills-vault` owns governed skill discovery/supply-chain metadata.
- `llm-research-development` owns reusable model R&D methodology; `afm` owns the AFM program; `model-registry` owns promoted immutable model metadata.
- `autonomous-venture-company` is a product/reference consumer of platform infrastructure, not a second canonical platform kernel.
- `docs` renders/discovers source truth; it does not own source truth.
- `aftergraph.org` owns the public front door; visibility never upgrades evidence.
- `brand` owns visual tokens/assets; `.github` owns organization/community defaults.

## Machine-readable topology

Create `docs/platform-topology/1.0.json` as the non-SHA topology input. It records the complete repository set, canonical branch, role, plane and visibility.

`latest-org-state.json` remains generated remote truth. The generator must derive its repository scope from the topology file instead of a hard-coded nine-repo array.

This separates:

```text
platform topology (human-governed, slow-changing)
!=
remote exact-head state (GitHub-generated, fast-changing)
```

## Evidence and authority rules

1. `Complete != Verified` remains intact.
2. Runtime evidence does not establish AIE conformance.
3. AIE conformance does not establish scientific validity.
4. Scientific results do not grant runtime authority.
5. Public visibility does not upgrade maturity.
6. No hand-written SHA becomes canonical org truth.

## Public presentation

`aftergraph.org` should describe one platform with specialized modules, not imply every repository is an independent end-user product. Its system map must consume or mirror the governance topology without claiming to be the source of truth.

## V1 acceptance criteria

- Exactly 19 currently installed `Aftergraph/*` repositories are represented in the topology contract.
- `org-state-verify.sh` derives scope from the topology contract and has no hard-coded `9` repository validation.
- `org-state/1.0` accepts all V1 platform roles and no longer documents `work-intelligence-v2` as a `master`-branch exception.
- `dependencies.yml` covers the same 19 repositories.
- Cross-repo contract docs no longer describe the organization as a five-repository platform.
- Governance README links the topology and reconciliation artifacts.
- `aftergraph.org/SYSTEM-MAP.md` no longer claims to be source-of-truth and reflects the 19-repository organization.
- `aftergraph.org/ARCHITECTURE.md` states governance topology → public rendering flow.

## Deferred after V1

- unified Principal/Tenant identity architecture and runtime binding;
- Studio production connections to every canonical backend;
- billing/entitlements and commercial tenant control;
- cross-repo end-to-end production mission conformance;
- benchmark naming/versioning reconciliation across ISR, Continuum and ACC;
- removal of duplicated AVC-vs-platform kernel semantics where executable overlap remains;
- automated site generation directly from `platform-topology/1.0` plus live org-state.
