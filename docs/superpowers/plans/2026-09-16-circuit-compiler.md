# Circuit Compiler Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Compile a bounded mission/reality/risk request into the minimal composition-valid CircuitSpec without granting authority or execution permission.

**Architecture:** Add a pure deterministic compiler beside the existing Circuit validator. The compiler maps a small mission vocabulary to minimal semantic operator graphs and refuses ambiguous/stale consequential requests before validation.

**Tech Stack:** Python stdlib, JSON Schema 2020-12, unittest, existing Circuit validator.

**Spec:** `docs/superpowers/specs/2026-09-16-p-1-system-reality-and-architecture-vnext-design.md`

## Global Constraints
- Compiler has zero authority and performs no runtime calls.
- `COMPILED` means composition candidate only, never executable/authorized.
- Consequential missions require Covenant admission and independent Witness in the generated graph.
- `UNKNOWN` or `CONFLICTING` reality fails closed.
- Stale reality fails closed for consequential missions.
- This slice MUST NOT bind CircuitRun to WORKS yet.

### Task 1: Compiler contracts + RED vectors
- Create `docs/contracts/circuit/0.1/circuit-compiler-input.schema.json`.
- Create `docs/contracts/circuit/0.1/circuit-compile-result.schema.json`.
- Create `scripts/test_roro_circuit_compiler_v0_1.py`.
- Add Experimental registry rows.
- RED vectors: read-only query, reversible repair, irreversible repair, improvement, unknown reality, conflicting reality, stale consequential reality, unknown intent/effect.

### Task 2: Pure compiler
- Create `scripts/circuit/compile_circuit.py`.
- Create `docs/system-reality/circuit-compiler-vectors.json`.
- Create `docs/system-reality/circuit-compiler-results.json`.
- Generate minimal CircuitSpec candidates and immediately validate them with the existing Circuit validator.
- Refuse any candidate whose generated CircuitSpec is invalid.

### Task 3: Verification
- Validate compiler inputs/results against schemas.
- Verify deterministic regeneration.
- Run compiler tests, all `test_roro*`, topology tests and full governance regression.
- Run diff/secret hygiene, verify PR head, fast-forward push only, keep PR #168 draft/unmerged.
