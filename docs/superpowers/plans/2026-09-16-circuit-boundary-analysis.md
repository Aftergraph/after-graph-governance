# Circuit Boundary Analysis Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Derive an evidence-bound Circuit composition contract and validator from R.O.R.O. component semantics without turning source dependencies into Circuit flow, authority, execution truth, or verification truth.

**Architecture:** Add experimental governance artifacts only. `CircuitSpec` declares semantic operators/edges and required invariants; `CircuitValidator` evaluates composition rules. R.O.R.O. dependency evidence is used only to expose coupling and candidate placement, never to authorize a Circuit edge.

**Tech Stack:** Python stdlib, JSON Schema 2020-12, unittest, existing R.O.R.O. artifacts.

**Spec:** `docs/superpowers/specs/2026-09-16-p-1-system-reality-and-architecture-vnext-design.md`

## Global Constraints

- Circuit has zero authority and owns no durable execution state.
- AIE/Trust/WORKS intersection remains the consequential executability boundary.
- Independent verification may not be performed by the executor it verifies.
- Dependency/import edges never imply Circuit flow, ownership, authority, or permission.
- `UNKNOWN` and `INFERRED` remain first-class epistemic states.
- This slice MUST NOT deploy, migrate repositories, mutate runtime state, or merge PR #168.

---
### Task 1: Circuit contracts and RED gate

**Files:**
- Create: `scripts/test_roro_circuit_boundaries_v0_1.py`
- Create: `docs/contracts/circuit/0.1/circuit-spec.schema.json`
- Create: `docs/contracts/circuit/0.1/circuit-validation.schema.json`
- Modify: `docs/cross-repo-contracts.md`

**Interfaces:**
- Consumes: `component-semantic-projection.json`, `component-dependency-graph.json`.
- Produces: schemas `circuit-spec/0.1` and `circuit-validation/0.1`.

- [ ] Write failing tests requiring six macro families, zero-authority compiler semantics, explicit invariants, and fail-closed validation.
- [ ] Run `python3 -m unittest -v scripts.test_roro_circuit_boundaries_v0_1` and confirm RED because artifacts do not exist.
- [ ] Add the two Experimental schemas and registry rows.
- [ ] Re-run the contract subset until GREEN.

### Task 2: Deterministic Circuit boundary generator

**Files:**
- Create: `scripts/roro/generate_circuit_boundaries.py`
- Create: `docs/system-reality/circuit-boundary-model.json`

**Interfaces:**
- Consumes semantic families plus exact-cut dependency evidence.
- Produces family/operator policy, allowed composition edges, forbidden edges, and dependency coupling annotations.
- [ ] Add tests that require dependency evidence to be annotated but never copied into `allowed_edges` automatically.
- [ ] Implement a pure deterministic generator.
- [ ] Require the macro sequence vocabulary `SIGHTLINE`, `HELM`, `COVENANT`, `DRIVE`, `WITNESS`, `REFINERY`, while treating COMMONS/DOMAIN/EXPERIENCE/LOOM as orthogonal/supporting families.
- [ ] Encode forbidden shortcuts, including direct consequential `HELM→DRIVE` without Covenant admission and self-verification `DRIVE→WITNESS` when verifier independence is absent.
- [ ] Re-run focused tests and deterministic regeneration.

### Task 3: CircuitSpec validator and falsification vectors

**Files:**
- Create: `scripts/roro/validate_circuit_spec.py`
- Create: `docs/system-reality/circuit-spec-vectors.json`
- Create: `docs/system-reality/circuit-validation-results.json`

**Interfaces:**
- Consumes: `CircuitSpec` candidate JSON documents plus `circuit-boundary-model.json`.
- Produces: deterministic `VALID` / `INVALID` results with explicit violations; it grants no execution permission.

- [ ] Add RED vectors for read-only, production-repair, improvement, missing-Covenant, self-verification, and unknown-family cases.
- [ ] Implement minimal validator rules from the boundary model.
- [ ] Verify valid vectors pass and invalid vectors fail for the expected reason.
- [ ] Ensure a `VALID` result says composition-valid only, never executable/authorized.

### Task 4: Evidence, documentation, and release gate

**Files:**
- Modify: `docs/superpowers/specs/2026-09-16-p-1-system-reality-and-architecture-vnext-design.md`
- Modify: `scripts/test_roro_circuit_boundaries_v0_1.py`

- [ ] Record observed coupling separately from Circuit semantics.
- [ ] Run Circuit tests, all `test_roro*`, topology tests, schema validation, deterministic regeneration, `git diff --check`, and staged secret hygiene.
- [ ] Run the full governance unittest suite and compare any failure against the untouched prior head.
- [ ] Verify PR #168 remote head is unchanged, commit with sign-off, and normal fast-forward push only.
- [ ] Keep PR #168 draft/unmerged.
