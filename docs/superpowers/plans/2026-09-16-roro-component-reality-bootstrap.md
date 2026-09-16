# R.O.R.O. Component Reality Bootstrap Implementation Plan

**Date:** 2026-09-16
**Design:** `docs/superpowers/specs/2026-09-16-p-1-system-reality-and-architecture-vnext-design.md`
**Scope:** T002 Component Registry + T005 R.O.R.O. Core + first Source Reality + AVC lineage
**Safety:** Read-only discovery. No topology promotion, repo move/archive, credential read, deployment mutation, or PR merge.

## Goal

Create the first machine-generated R.O.R.O. source-reality layer where stable component identity is independent from repository/path, exact Git state is evidence-bound, AVC extraction lineage is explicit, and unresolved facts remain UNKNOWN rather than being guessed.

## Non-negotiable laws

- `ComponentID != Repository` and `ComponentID != deployment`.
- Repository/package presence does not prove canonical ownership, migration completion, runtime maturity, or verification.
- Every generated source binding carries a full exact Git SHA.
- Discovery scope comes from live GitHub org reality, not a hand-authored 31-repo list.
- Secret values are never collected or serialized.
- AVC migration states are evidence-derived and may remain `UNKNOWN`.
- Generated artifacts are observations/projections, not new native authority.
## Task 1 — Contract-first RED tests

**Files**
- Create `scripts/test_roro_component_reality_v0_1.py`
- Later create `docs/contracts/roro/0.1/*.schema.json`

Write failing tests that require:
- five R.O.R.O. contract schemas to exist and parse;
- stable component IDs matching `^ag:[a-z0-9][a-z0-9:-]*$`;
- explicit epistemic and reality-facet vocabularies;
- source bindings with full 40-character SHA and repository/path separated from component identity;
- generated registry uniqueness and no duplicate source-binding identities;
- lineage records with bounded migration-state enum and evidence refs;
- gaps artifact that reports discovered-but-unclassified repositories/components explicitly.

Run: `python3 scripts/test_roro_component_reality_v0_1.py`
Expected: FAIL because contracts/generator do not exist.

## Task 2 — R.O.R.O. Core contracts + component model

**Files**
- Create `docs/contracts/roro/0.1/observation.schema.json`
- Create `docs/contracts/roro/0.1/component.schema.json`
- Create `docs/contracts/roro/0.1/source-binding.schema.json`
- Create `docs/contracts/roro/0.1/reality-facet.schema.json`
- Create `docs/contracts/roro/0.1/reality-diff.schema.json`
- Create `docs/system-reality/COMPONENT-MODEL.md`

Define:
- Component as stable semantic identity plus lifecycle/classification, never a repo alias;
- SourceBinding as observed repository/path/revision binding with provenance;
- Observation as subject/predicate/value/evidence/time/observer without authority promotion;
- RealityFacet vocabulary: `DECLARED`, `CANONICAL`, `DESIRED`, `INSTALLED`, `CONFIGURED`, `RUNNING`, `REACHABLE`, `HEALTHY`, `VERIFIED`, `RECOVERABLE`;
- epistemic vocabulary: `VERIFIED`, `OBSERVED`, `INFERRED`, `DECLARED`, `PROPOSED`, `STALE`, `CONFLICTING`, `UNKNOWN`;
- RealityDiff as explicit disagreement between facets/claims.

Run the focused tests until the contract section is GREEN.

## Task 3 — Live GitHub source discovery

**Files**
- Create `scripts/roro/discover_github.py`
- Create `scripts/roro/discover_components.py`
- Extend `scripts/test_roro_component_reality_v0_1.py`

Discovery must query the authenticated GitHub org through `gh api`, obtain every non-archived `Aftergraph` repository, default branch, visibility and exact head SHA, then inspect source trees/manifests without a hard-coded repo-name inventory.
The component discovery layer should recognize evidence-bearing component candidates from workspace/package manifests and selected structural directories, but must not promote semantic ownership solely from a folder name.

Tests use local synthetic GitHub JSON/manifest fixtures; live network behavior is separately verified after unit tests.

## Task 4 — Registry generator + validator

**Files**
- Create `scripts/roro/validate_registry.py`
- Generate `docs/system-reality/component-registry.json`
- Generate `docs/system-reality/reality-gaps.json`

Registry rules:
- every component ID is unique;
- each source binding has repository, path, exact revision, observer and observed timestamp;
- repository root records are represented separately from subcomponents;
- topology absence becomes a gap, not implicit exclusion;
- semantic classification has explicit basis/status and may be `UNKNOWN`;
- no field accepts credential values.

Run synthetic validation tests first, then generate against the full live Aftergraph org and validate the generated artifact.

## Task 5 — AVC → Aftergraph lineage

**Files**
- Create `scripts/roro/reconcile_lineage.py`
- Generate `docs/system-reality/component-lineage.json`
- Extend tests with positive, ambiguous and conflicting lineage cases.
Lineage evidence order:
1. explicit migration text in current package metadata/docs;
2. canonical normalized package identity with explicit AVC/Aftergraph namespace transition;
3. corroborating dependency/consumer evidence;
4. name similarity only as an unresolved candidate, never automatic migration proof.

Allowed states:
`MIGRATED`, `ACTIVE_LEGACY`, `DUPLICATED`, `PARTIALLY_MIGRATED`, `ORPHANED`, `UNKNOWN`.

A matching package name alone may establish a candidate relation but cannot yield `MIGRATED` without explicit migration evidence and target presence. The generator must preserve evidence refs for every non-UNKNOWN conclusion.

## Task 6 — Spec reconciliation and final verification

Update the P-1 design with the approved R.O.R.O. bootstrap amendment:
- native truth remains native;
- `DECLARED/CANONICAL/INSTALLED/RUNNING/VERIFIED` are separate reality facets;
- Component is the stable unit; Repository is a binding;
- Circuit is future composition, not a new authority source;
- this bootstrap covers source reality only, not live runtime/cloud/credential promotion.

Verification:
- focused R.O.R.O. unittest suite;
- all governance `scripts/test_*.py` suites that run under stdlib/unittest;
- `python3 scripts/roro/validate_registry.py` against generated artifacts;
- `git diff --check`;
- secret-pattern scan over newly generated JSON/docs/scripts;
- fresh live-org regeneration comparison.

Commit conventionally, fetch the PR branch again, require fast-forward ancestry, then push `HEAD` to `architecture/p-1-system-reality-2026-09-16`. Keep PR #168 draft and unmerged.
