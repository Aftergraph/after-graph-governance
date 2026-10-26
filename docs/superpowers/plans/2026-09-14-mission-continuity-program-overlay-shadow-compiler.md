# Mission Continuity Program Overlay Shadow Compiler Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the smallest useful Program Overlay + semantic-seam + claim-conflict evaluator that can classify Aftergraph program changes as `PASS`, `WARN`, `BLOCK`, or `UNKNOWN` in shadow mode without creating a new source of truth or enforcement plane.

**Architecture:** Add a zero-dependency, deterministic Python evaluator inside Governance. It consumes the existing canonical topology plus experimental Program Overlay, semantic seam registry and claim fixtures. The first slice produces advisory JSON only; it does not mutate GitHub, agents, Mission state, authority, WORKS, Runtime, AGENTS.md, Telegram, Studio or Relay.

**Tech Stack:** Python 3 standard library, JSON documents, existing `docs/platform-topology/2.0.json`, `unittest`.

**Spec:** `docs/superpowers/specs/2026-09-14-mission-continuity-program-overlay-design.md`

## Global Constraints

- `docs/platform-topology/2.0.json` remains canonical for repository scope, role, lifecycle, ownership and `must_not_own`.
- Program Overlay is directional coordination metadata only; it MUST NOT become Mission truth, authority, Work truth, compatibility truth, exact Git truth or verification truth.
- Semantic claims grant no authority and MUST NOT replace AIE, Trust Gateway, WORKS leases, branch protection or human approval.
- `UNKNOWN` is first-class. Missing/unsupported/stale input MUST NOT be silently upgraded to `PASS`.
- No PyYAML, `jsonschema`, OPA or other new runtime dependency in this slice. Follow the repository's existing zero-dependency governance tooling style.
- No hard PR blocking in this slice. Output is shadow/advisory only.
- Do not modify `scripts/gen_repo_guides.py` or AGENTS generation until Governance PR #162 is reconciled/merged; this avoids parallel ownership collision.
- Do not duplicate ARI compatibility graphs from open Governance PRs #38/#39.
- Do not implement RuntimeBinding, Mission Supervisor, Telegram commands or runtime replacement in this plan.
- Do not merge Governance PR #160/#162 merely to satisfy this plan. Reconcile their semantics first.

---

## Task 0: Exact-head prerequisite and collision gate

**Files:**
- Read only: `docs/platform-topology/2.0.json`
- Read only: Governance PR #160
- Read only: Governance PR #162
- Read only: Governance PRs #38 and #39
- Read only: relevant WORKS Golden Mission / execution-context work

**Interfaces:**
- Consumes: current `main`, active PR metadata, topology ownership.
- Produces: a written execution note in the PR body stating which prerequisite heads were inspected and that this slice does not modify their write sets.

- [ ] **Step 1: Record current exact heads**

Capture current Governance `main` and heads for #160, #162, #38 and #39. Also capture current relevant WORKS PR/issue heads for execution-context and Golden Mission integration.

Expected: no implementation claim uses an older head without explicitly marking it historical.

- [ ] **Step 2: Compare write sets**

Confirm the first implementation slice only creates:

```text
docs/program-overlay/*
docs/semantic-seams/*
docs/semantic-claims/*
scripts/program_overlay.py
scripts/test_program_overlay.py
```

Expected: no overlap with #162's `gen_repo_guides.py`/inventory work and no ARI compatibility implementation.

- [ ] **Step 3: Stop on collision**

If an active PR has begun writing the same paths or has already introduced equivalent Program Overlay / seam / claim evaluator semantics, stop and reconcile instead of duplicating it.

Expected: either `NO_COLLISION` with exact refs, or a documented blocker.

---

## Task 1: Add experimental Program Overlay and seam registry fixtures

**Files:**
- Create: `docs/program-overlay/0.1.schema.json`
- Create: `docs/program-overlay/mission-continuity.json`
- Create: `docs/semantic-seams/0.1.json`
- Create: `docs/semantic-claims/empty.json`
- Test: `scripts/test_program_overlay.py`

**Interfaces:**
- Consumes: canonical repository names from topology.
- Produces: JSON fixtures consumed by `load_overlay()`, `load_seam_registry()` and `load_claims()` in Task 2.

- [ ] **Step 1: Write the failing fixture contract test**

Create `scripts/test_program_overlay.py` with the initial tests below. The import is intentionally expected to fail before Task 2 adds the implementation.

```python
#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "program_overlay.py"


def load_module():
    spec = importlib.util.spec_from_file_location("program_overlay", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load program_overlay.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ProgramOverlayFixtureTests(unittest.TestCase):
    def test_canonical_fixture_validates(self):
        module = load_module()
        overlay = module.load_json(ROOT / "docs/program-overlay/mission-continuity.json")
        topology = module.load_json(ROOT / "docs/platform-topology/2.0.json")
        seams = module.load_json(ROOT / "docs/semantic-seams/0.1.json")
        self.assertEqual(module.validate_overlay(overlay, topology, seams), [])

    def test_fixture_does_not_copy_exact_git_state(self):
        overlay = json.loads((ROOT / "docs/program-overlay/mission-continuity.json").read_text())
        serialized = json.dumps(overlay)
        self.assertNotIn("remote_head_sha", serialized)
        self.assertNotIn("head_sha", serialized)
        self.assertNotIn("commit_sha", serialized)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify RED**

Run:

```bash
python scripts/test_program_overlay.py
```

Expected: FAIL because `scripts/program_overlay.py` does not exist yet.

- [ ] **Step 3: Add `docs/program-overlay/0.1.schema.json`**

Use this bounded experimental schema descriptor:

```json
{
  "schema_version": "aftergraph-program-schema/0.1",
  "document_schema": "aftergraph-program/0.1",
  "status": "experimental",
  "required": [
    "schema",
    "program_id",
    "parent_program",
    "objective",
    "status",
    "active_slices",
    "touches",
    "invariants",
    "blocked_by",
    "success"
  ],
  "allowed_status": ["proposed", "active", "paused", "complete", "superseded"],
  "touch_modes": ["core", "next", "consumer", "observer"],
  "forbidden_truth_fields": [
    "remote_head_sha",
    "head_sha",
    "commit_sha",
    "canonical_branch",
    "owns",
    "must_not_own"
  ]
}
```

This file documents the contract; Task 2 performs standard-library validation and does not require `jsonschema`.

- [ ] **Step 4: Add `docs/semantic-seams/0.1.json`**

Create this registry:

```json
{
  "schema": "semantic-seams/0.1",
  "status": "experimental",
  "seams": [
    {"id": "seam://governance/platform-topology", "owner_repo": "after-graph-governance"},
    {"id": "seam://governance/correlation", "owner_repo": "after-graph-governance"},
    {"id": "seam://aie/authority-lease", "owner_repo": "aie"},
    {"id": "seam://trust/action-admission", "owner_repo": "trust-gateway"},
    {"id": "seam://works/execution-context", "owner_repo": "works-execution"},
    {"id": "seam://works/effect-ledger", "owner_repo": "works-execution"},
    {"id": "seam://runtime/runtime-binding", "owner_repo": "runtime"},
    {"id": "seam://runtime/mission-supervision", "owner_repo": "runtime"},
    {"id": "seam://continuity/context-transfer", "owner_repo": "context-continuity"},
    {"id": "seam://verification/code-review-verdict", "owner_repo": "sentinel"},
    {"id": "seam://studio/mission-projection", "owner_repo": "studio"},
    {"id": "seam://relay/operator-projection", "owner_repo": "relay"},
    {"id": "seam://operations/cron-observation", "owner_repo": "aftergraph-cron-fabric"}
  ]
}
```

- [ ] **Step 5: Add `docs/program-overlay/mission-continuity.json`**

Create:

```json
{
  "schema": "aftergraph-program/0.1",
  "program_id": "mission-continuity",
  "parent_program": "portable-intelligence-infrastructure-v1",
  "objective": "Preserve a governed Mission across runtime replacement through independent verification.",
  "status": "active",
  "active_slices": ["MC-001", "MC-002"],
  "touches": [
    {"repo": "works-execution", "seam": "seam://works/execution-context", "mode": "core"},
    {"repo": "runtime", "seam": "seam://runtime/runtime-binding", "mode": "next"},
    {"repo": "studio", "seam": "seam://studio/mission-projection", "mode": "consumer"}
  ],
  "invariants": [
    "runtime_completion != verification",
    "revocation != recoverable_failure",
    "budget_exhaustion != recoverable_failure",
    "projection != canonical_truth"
  ],
  "blocked_by": [
    {"contract": "execution-context/1.0"}
  ],
  "success": [
    "golden_mission_runtime_replacement",
    "no_duplicate_effect",
    "authority_lineage_preserved",
    "independent_verification"
  ]
}
```

- [ ] **Step 6: Add empty claim fixture**

Create `docs/semantic-claims/empty.json`:

```json
{
  "schema": "semantic-claims/0.1",
  "claims": []
}
```

- [ ] **Step 7: Commit fixture/test RED state**

```bash
git add docs/program-overlay docs/semantic-seams docs/semantic-claims scripts/test_program_overlay.py
git commit -m "test(program): pin overlay and seam contracts"
```

Expected: commit intentionally leaves the new tests red because implementation starts in Task 2.

---

## Task 2: Implement zero-dependency validation and loading

**Files:**
- Create: `scripts/program_overlay.py`
- Modify: `scripts/test_program_overlay.py`

**Interfaces:**
- Consumes: JSON paths from Task 1.
- Produces:
  - `load_json(path: Path) -> dict[str, Any]`
  - `topology_index(doc: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]`
  - `seam_index(doc: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]`
  - `validate_overlay(overlay, topology, seams) -> list[str]`
  - `validate_claims(claims, seams) -> list[str]`

- [ ] **Step 1: Extend tests for invalid references and forbidden truth copying**

Add these cases to `scripts/test_program_overlay.py`:

```python
    def test_unknown_repo_is_rejected(self):
        module = load_module()
        overlay = module.load_json(ROOT / "docs/program-overlay/mission-continuity.json")
        topology = module.load_json(ROOT / "docs/platform-topology/2.0.json")
        seams = module.load_json(ROOT / "docs/semantic-seams/0.1.json")
        overlay["touches"][0]["repo"] = "not-a-real-repo"
        errors = module.validate_overlay(overlay, topology, seams)
        self.assertTrue(any("unknown repo" in error for error in errors))

    def test_unknown_seam_is_rejected(self):
        module = load_module()
        overlay = module.load_json(ROOT / "docs/program-overlay/mission-continuity.json")
        topology = module.load_json(ROOT / "docs/platform-topology/2.0.json")
        seams = module.load_json(ROOT / "docs/semantic-seams/0.1.json")
        overlay["touches"][0]["seam"] = "seam://unknown/value"
        errors = module.validate_overlay(overlay, topology, seams)
        self.assertTrue(any("unknown seam" in error for error in errors))

    def test_forbidden_exact_git_truth_field_is_rejected(self):
        module = load_module()
        overlay = module.load_json(ROOT / "docs/program-overlay/mission-continuity.json")
        topology = module.load_json(ROOT / "docs/platform-topology/2.0.json")
        seams = module.load_json(ROOT / "docs/semantic-seams/0.1.json")
        overlay["head_sha"] = "0" * 40
        errors = module.validate_overlay(overlay, topology, seams)
        self.assertTrue(any("forbidden truth field" in error for error in errors))
```

- [ ] **Step 2: Run tests to verify RED**

```bash
python scripts/test_program_overlay.py
```

Expected: FAIL because validator functions are missing.

- [ ] **Step 3: Implement minimal loader/index/validator**

Create `scripts/program_overlay.py` with this structure:

```python
#!/usr/bin/env python3
"""Experimental zero-dependency Program Overlay validator and shadow evaluator."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TOPOLOGY = REPO_ROOT / "docs/platform-topology/2.0.json"
DEFAULT_OVERLAY = REPO_ROOT / "docs/program-overlay/mission-continuity.json"
DEFAULT_SEAMS = REPO_ROOT / "docs/semantic-seams/0.1.json"
DEFAULT_CLAIMS = REPO_ROOT / "docs/semantic-claims/empty.json"

REQUIRED_OVERLAY_FIELDS = {
    "schema", "program_id", "parent_program", "objective", "status",
    "active_slices", "touches", "invariants", "blocked_by", "success",
}
ALLOWED_OVERLAY_FIELDS = REQUIRED_OVERLAY_FIELDS
FORBIDDEN_TRUTH_FIELDS = {
    "remote_head_sha", "head_sha", "commit_sha", "canonical_branch",
    "owns", "must_not_own",
}
TOUCH_MODES = {"core", "next", "consumer", "observer"}
CLAIM_MODES = {"READ", "WRITE", "MIGRATE", "VERIFY", "OBSERVE"}


def load_json(path: Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        doc = json.load(handle)
    if not isinstance(doc, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return doc


def topology_index(doc: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    repos = doc.get("repositories", [])
    if not isinstance(repos, list):
        raise ValueError("topology document has no repository list")
    return {entry["name"]: entry for entry in repos if isinstance(entry, Mapping) and "name" in entry}


def seam_index(doc: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    seams = doc.get("seams", [])
    if not isinstance(seams, list):
        raise ValueError("semantic seam document has no seam list")
    return {entry["id"]: entry for entry in seams if isinstance(entry, Mapping) and "id" in entry}


def validate_overlay(overlay: Mapping[str, Any], topology: Mapping[str, Any], seams: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    if overlay.get("schema") != "aftergraph-program/0.1":
        errors.append(f"unsupported overlay schema: {overlay.get('schema')!r}")
    missing = REQUIRED_OVERLAY_FIELDS - set(overlay)
    if missing:
        errors.append(f"overlay missing fields: {sorted(missing)}")
    for field in set(overlay) & FORBIDDEN_TRUTH_FIELDS:
        errors.append(f"forbidden truth field in overlay: {field}")
    for field in set(overlay) - ALLOWED_OVERLAY_FIELDS - FORBIDDEN_TRUTH_FIELDS:
        errors.append(f"unexpected overlay field: {field}")

    repos = topology_index(topology)
    seam_map = seam_index(seams)
    touches = overlay.get("touches", [])
    if not isinstance(touches, list):
        return errors + ["touches must be a list"]
    for touch in touches:
        if not isinstance(touch, Mapping):
            errors.append("touch entry must be an object")
            continue
        repo = touch.get("repo")
        seam = touch.get("seam")
        mode = touch.get("mode")
        if repo not in repos:
            errors.append(f"unknown repo in touch: {repo!r}")
        if seam not in seam_map:
            errors.append(f"unknown seam in touch: {seam!r}")
        if mode not in TOUCH_MODES:
            errors.append(f"unknown touch mode: {mode!r}")
    return errors


def validate_claims(claims: Mapping[str, Any], seams: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    if claims.get("schema") != "semantic-claims/0.1":
        errors.append(f"unsupported claims schema: {claims.get('schema')!r}")
    seam_map = seam_index(seams)
    rows = claims.get("claims", [])
    if not isinstance(rows, list):
        return errors + ["claims must be a list"]
    for row in rows:
        if not isinstance(row, Mapping):
            errors.append("claim must be an object")
            continue
        if row.get("seam") not in seam_map:
            errors.append(f"unknown seam in claim: {row.get('seam')!r}")
        if row.get("mode") not in CLAIM_MODES:
            errors.append(f"unknown claim mode: {row.get('mode')!r}")
    return errors
```

Do not add evaluation logic yet.

- [ ] **Step 4: Run focused tests**

```bash
python scripts/test_program_overlay.py
```

Expected: PASS for loader/validation tests.

- [ ] **Step 5: Run existing topology checks**

```bash
python scripts/platform_topology.py check
python scripts/platform_topology.py check-readme
```

Expected: PASS; the new overlay must not alter topology truth.

- [ ] **Step 6: Commit**

```bash
git add scripts/program_overlay.py scripts/test_program_overlay.py
git commit -m "feat(program): validate experimental overlay inputs"
```

---

## Task 3: Implement claim conflict semantics

**Files:**
- Modify: `scripts/program_overlay.py`
- Modify: `scripts/test_program_overlay.py`
- Create: `docs/semantic-claims/conflict-example.json`

**Interfaces:**
- Consumes: validated claim document.
- Produces:
  - `active_claims(claims, now) -> list[Mapping[str, Any]]`
  - `claim_conflicts(claims, now) -> list[dict[str, Any]]`

- [ ] **Step 1: Write conflict tests**

Add tests for the compatibility matrix:

```python
    def test_write_write_same_seam_blocks(self):
        module = load_module()
        claims = {
            "schema": "semantic-claims/0.1",
            "claims": [
                {"claim_id": "c1", "seam": "seam://runtime/runtime-binding", "mode": "WRITE", "status": "active"},
                {"claim_id": "c2", "seam": "seam://runtime/runtime-binding", "mode": "WRITE", "status": "active"}
            ]
        }
        conflicts = module.claim_conflicts(claims, now=None)
        self.assertEqual(len(conflicts), 1)
        self.assertEqual(conflicts[0]["kind"], "WRITE_WRITE")

    def test_read_write_same_seam_is_allowed(self):
        module = load_module()
        claims = {
            "schema": "semantic-claims/0.1",
            "claims": [
                {"claim_id": "c1", "seam": "seam://runtime/runtime-binding", "mode": "READ", "status": "active"},
                {"claim_id": "c2", "seam": "seam://runtime/runtime-binding", "mode": "WRITE", "status": "active"}
            ]
        }
        self.assertEqual(module.claim_conflicts(claims, now=None), [])

    def test_migrate_write_same_seam_blocks(self):
        module = load_module()
        claims = {
            "schema": "semantic-claims/0.1",
            "claims": [
                {"claim_id": "c1", "seam": "seam://works/execution-context", "mode": "MIGRATE", "status": "active"},
                {"claim_id": "c2", "seam": "seam://works/execution-context", "mode": "WRITE", "status": "active"}
            ]
        }
        conflicts = module.claim_conflicts(claims, now=None)
        self.assertEqual(conflicts[0]["kind"], "MIGRATE_WRITE")

    def test_unrelated_write_claims_do_not_conflict(self):
        module = load_module()
        claims = {
            "schema": "semantic-claims/0.1",
            "claims": [
                {"claim_id": "c1", "seam": "seam://runtime/runtime-binding", "mode": "WRITE", "status": "active"},
                {"claim_id": "c2", "seam": "seam://studio/mission-projection", "mode": "WRITE", "status": "active"}
            ]
        }
        self.assertEqual(module.claim_conflicts(claims, now=None), [])
```

- [ ] **Step 2: Run tests to verify RED**

```bash
python scripts/test_program_overlay.py
```

Expected: FAIL because `claim_conflicts` does not exist.

- [ ] **Step 3: Implement minimal conflict evaluator**

Add:

```python

def active_claims(claims: Mapping[str, Any], now: datetime | None) -> list[Mapping[str, Any]]:
    current = now or datetime.now(timezone.utc)
    result: list[Mapping[str, Any]] = []
    for claim in claims.get("claims", []):
        if not isinstance(claim, Mapping) or claim.get("status") != "active":
            continue
        expires_at = claim.get("expires_at")
        if isinstance(expires_at, str):
            expires = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
            if expires <= current:
                continue
        result.append(claim)
    return result


def claim_conflicts(claims: Mapping[str, Any], now: datetime | None) -> list[dict[str, Any]]:
    rows = active_claims(claims, now)
    conflicts: list[dict[str, Any]] = []
    for i, left in enumerate(rows):
        for right in rows[i + 1:]:
            if left.get("seam") != right.get("seam"):
                continue
            pair = {left.get("mode"), right.get("mode")}
            kind = None
            if pair == {"WRITE"}:
                kind = "WRITE_WRITE"
            elif "MIGRATE" in pair and ("WRITE" in pair or "MIGRATE" in pair):
                kind = "MIGRATE_WRITE" if "WRITE" in pair else "MIGRATE_MIGRATE"
            if kind:
                conflicts.append({
                    "kind": kind,
                    "seam": left.get("seam"),
                    "claims": [left.get("claim_id"), right.get("claim_id")],
                })
    return conflicts
```

- [ ] **Step 4: Add representative conflict fixture**

Create `docs/semantic-claims/conflict-example.json` with two active `WRITE` claims on `seam://runtime/runtime-binding` and one unrelated `WRITE` claim on `seam://studio/mission-projection`.

- [ ] **Step 5: Run tests**

```bash
python scripts/test_program_overlay.py
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add scripts/program_overlay.py scripts/test_program_overlay.py docs/semantic-claims/conflict-example.json
git commit -m "feat(program): detect semantic write collisions"
```

---

## Task 4: Implement shadow Direction Compiler decision output

**Files:**
- Modify: `scripts/program_overlay.py`
- Modify: `scripts/test_program_overlay.py`

**Interfaces:**
- Consumes: overlay, topology, seams, claims.
- Produces:
  - `evaluate_direction(overlay, topology, seams, claims, now=None) -> dict[str, Any]`
  - CLI `python scripts/program_overlay.py check`
  - CLI `python scripts/program_overlay.py evaluate [--claims PATH]`

- [ ] **Step 1: Add decision tests**

Add:

```python
    def test_valid_no_claims_passes(self):
        module = load_module()
        result = module.evaluate_direction(
            module.load_json(ROOT / "docs/program-overlay/mission-continuity.json"),
            module.load_json(ROOT / "docs/platform-topology/2.0.json"),
            module.load_json(ROOT / "docs/semantic-seams/0.1.json"),
            module.load_json(ROOT / "docs/semantic-claims/empty.json"),
            now=None,
        )
        self.assertEqual(result["decision"], "PASS")

    def test_conflicting_write_claims_block(self):
        module = load_module()
        result = module.evaluate_direction(
            module.load_json(ROOT / "docs/program-overlay/mission-continuity.json"),
            module.load_json(ROOT / "docs/platform-topology/2.0.json"),
            module.load_json(ROOT / "docs/semantic-seams/0.1.json"),
            module.load_json(ROOT / "docs/semantic-claims/conflict-example.json"),
            now=None,
        )
        self.assertEqual(result["decision"], "BLOCK")
        self.assertTrue(result["conflicting_claims"])

    def test_invalid_or_unknown_input_is_unknown_not_pass(self):
        module = load_module()
        overlay = module.load_json(ROOT / "docs/program-overlay/mission-continuity.json")
        overlay["touches"][0]["seam"] = "seam://missing/value"
        result = module.evaluate_direction(
            overlay,
            module.load_json(ROOT / "docs/platform-topology/2.0.json"),
            module.load_json(ROOT / "docs/semantic-seams/0.1.json"),
            module.load_json(ROOT / "docs/semantic-claims/empty.json"),
            now=None,
        )
        self.assertEqual(result["decision"], "UNKNOWN")
        self.assertTrue(result["unknowns"])
```

- [ ] **Step 2: Run tests to verify RED**

```bash
python scripts/test_program_overlay.py
```

Expected: FAIL because `evaluate_direction` is missing.

- [ ] **Step 3: Implement decision reducer**

Add:

```python

def evaluate_direction(
    overlay: Mapping[str, Any],
    topology: Mapping[str, Any],
    seams: Mapping[str, Any],
    claims: Mapping[str, Any],
    now: datetime | None = None,
) -> dict[str, Any]:
    overlay_errors = validate_overlay(overlay, topology, seams)
    claim_errors = validate_claims(claims, seams)
    conflicts = claim_conflicts(claims, now) if not claim_errors else []

    unknowns = overlay_errors + claim_errors
    if unknowns:
        decision = "UNKNOWN"
    elif conflicts:
        decision = "BLOCK"
    else:
        decision = "PASS"

    return {
        "decision": decision,
        "program_id": overlay.get("program_id"),
        "active_slices": list(overlay.get("active_slices", [])),
        "reasons": [],
        "violated_invariants": [],
        "conflicting_claims": conflicts,
        "unknowns": unknowns,
        "evidence_refs": ["docs/platform-topology/2.0.json"],
        "mode": "shadow",
    }
```

Do not emit `WARN` yet merely to exercise the enum. `WARN` will be introduced only when a deterministic warning condition is defined and tested.

- [ ] **Step 4: Add CLI**

Implement `main(argv=None)` with:

```text
check     validate overlay/seams/claims and exit 0/1
evaluate  print stable sorted/indented JSON decision and exit 0 for PASS/WARN, 2 for BLOCK, 3 for UNKNOWN
```

Default files are the canonical experimental fixtures from Task 1. `--claims` may point to another claims JSON document.

- [ ] **Step 5: Run focused tests and CLI**

```bash
python scripts/test_program_overlay.py
python scripts/program_overlay.py check
python scripts/program_overlay.py evaluate
python scripts/program_overlay.py evaluate --claims docs/semantic-claims/conflict-example.json; test $? -eq 2
```

Expected:
- tests PASS;
- `check` exits 0;
- default evaluate prints `"decision": "PASS"`;
- conflict example prints `"decision": "BLOCK"` and exits 2.

- [ ] **Step 6: Commit**

```bash
git add scripts/program_overlay.py scripts/test_program_overlay.py
git commit -m "feat(program): add shadow direction compiler"
```

---

## Task 5: Add ownership consistency checks without duplicating topology

**Files:**
- Modify: `scripts/program_overlay.py`
- Modify: `scripts/test_program_overlay.py`

**Interfaces:**
- Consumes: topology owner role + semantic seam `owner_repo`.
- Produces: validation that seam owners exist and core/next touches do not silently redefine ownership.

- [ ] **Step 1: Write failing ownership tests**

```python
    def test_seam_owner_must_exist_in_topology(self):
        module = load_module()
        seams = module.load_json(ROOT / "docs/semantic-seams/0.1.json")
        topology = module.load_json(ROOT / "docs/platform-topology/2.0.json")
        seams["seams"][0]["owner_repo"] = "missing-owner"
        errors = module.validate_seam_registry(seams, topology)
        self.assertTrue(any("owner repo" in error for error in errors))

    def test_core_touch_must_match_seam_owner(self):
        module = load_module()
        overlay = module.load_json(ROOT / "docs/program-overlay/mission-continuity.json")
        topology = module.load_json(ROOT / "docs/platform-topology/2.0.json")
        seams = module.load_json(ROOT / "docs/semantic-seams/0.1.json")
        overlay["touches"][0]["repo"] = "runtime"
        errors = module.validate_overlay(overlay, topology, seams)
        self.assertTrue(any("core touch does not match seam owner" in error for error in errors))
```

- [ ] **Step 2: Run RED**

```bash
python scripts/test_program_overlay.py
```

Expected: FAIL because ownership validation is not implemented.

- [ ] **Step 3: Implement `validate_seam_registry` and core/next ownership checks**

Add:

```python

def validate_seam_registry(seams: Mapping[str, Any], topology: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    repos = topology_index(topology)
    seen: set[str] = set()
    for row in seams.get("seams", []):
        if not isinstance(row, Mapping):
            errors.append("seam entry must be an object")
            continue
        seam_id = row.get("id")
        owner = row.get("owner_repo")
        if seam_id in seen:
            errors.append(f"duplicate seam id: {seam_id}")
        seen.add(str(seam_id))
        if owner not in repos:
            errors.append(f"unknown seam owner repo: {owner!r}")
    return errors
```

In `validate_overlay`, when `mode` is `core` or `next`, require `touch.repo == seam.owner_repo`. `consumer` and `observer` touches may reference a seam owned elsewhere.

- [ ] **Step 4: Re-run tests**

```bash
python scripts/test_program_overlay.py
python scripts/program_overlay.py check
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add scripts/program_overlay.py scripts/test_program_overlay.py
git commit -m "feat(program): enforce topology-backed seam ownership"
```

---

## Task 6: Verification and PR evidence package

**Files:**
- Modify only if needed for discovered deterministic defects in the files created by Tasks 1–5.
- Do not broaden scope.

**Interfaces:**
- Consumes: completed first slice.
- Produces: exact-head evidence attached to the draft PR.

- [ ] **Step 1: Run focused suite**

```bash
python scripts/test_program_overlay.py
```

Expected: all Program Overlay tests PASS.

- [ ] **Step 2: Run existing Governance checks most likely to catch boundary regression**

```bash
python scripts/platform_topology.py check
python scripts/platform_topology.py check-readme
python scripts/test_governance_clean_room.py
python scripts/test_governance_exact_head_truth.py
python scripts/test_golden_mission_skeleton_v0_1.py
```

Expected: PASS. If any pre-existing test fails on clean `main`, record the exact pre-existing failure instead of attributing it to this change.

- [ ] **Step 3: Run syntax validation**

```bash
python -m py_compile scripts/program_overlay.py scripts/test_program_overlay.py
```

Expected: PASS.

- [ ] **Step 4: Validate Git diff scope**

```bash
git diff --check main...HEAD
git diff --name-only main...HEAD
```

Expected changed paths only:

```text
docs/program-overlay/*
docs/semantic-seams/*
docs/semantic-claims/*
docs/superpowers/specs/2026-09-14-mission-continuity-program-overlay-design.md
docs/superpowers/plans/2026-09-14-mission-continuity-program-overlay-shadow-compiler.md
scripts/program_overlay.py
scripts/test_program_overlay.py
```

- [ ] **Step 5: Update draft PR body with evidence**

Record:

```text
base SHA
head SHA
commands run
pass/fail counts
known prerequisite PR heads inspected
collision result
explicit non-claims:
- no RuntimeBinding implemented
- no Mission Supervisor implemented
- no hard enforcement
- no AGENTS generator modification
- no authority/execution semantics changed
```

- [ ] **Step 6: Keep PR draft**

Do not mark ready until prerequisite reconciliation confirms the semantic seam registry does not conflict with #160, #162 or ARI work.

---

## Task 7: Post-prerequisite integration with AGENTS generation — separate follow-up PR

**Files:**
- Modify after #162 lands: `scripts/gen_repo_guides.py`
- Modify after #162 lands: its corresponding contract tests
- Consume only: Program Overlay evaluation output

**Interfaces:**
- Consumes: merged #162 topology-sourced AGENTS generator and stable Program Overlay output.
- Produces: concise generated program capsule in relevant repo guides.

This task is intentionally **not implemented in the first PR**. After #162 is canonical, write a new TDD plan/PR that injects only:

```text
active program IDs
relevant slice IDs
allowed/relevant semantic seams
active conflicting claims
hard invariants
explicit must-not-own reminders
```

It MUST NOT introduce another agent bootstrap file or source of truth.

---

## Self-review result

### Spec coverage

The first implementation boundary from the design is covered:

- Program Overlay schema + fixture: Tasks 1–2.
- Semantic seam registry: Tasks 1 and 5.
- Claim compatibility evaluator: Task 3.
- Direction Compiler in shadow mode: Task 4.
- Topology ownership reuse: Task 5.
- No AGENTS duplication: Global Constraints + Task 7 deferred.
- No hard enforcement: Global Constraints + Task 4.
- No RuntimeBinding/Supervisor/Telegram implementation: Global Constraints.
- Exact-head/collision prerequisites: Task 0 and Task 6.

### Placeholder scan

No `TBD`, `TODO`, generic “add tests”, or unspecified implementation steps remain in Tasks 0–6.

### Type consistency

The plan consistently defines and reuses:

```text
load_json(Path) -> dict[str, Any]
topology_index(Mapping) -> dict[str, Mapping]
seam_index(Mapping) -> dict[str, Mapping]
validate_overlay(...) -> list[str]
validate_seam_registry(...) -> list[str]
validate_claims(...) -> list[str]
active_claims(..., datetime | None) -> list[Mapping]
claim_conflicts(..., datetime | None) -> list[dict[str, Any]]
evaluate_direction(...) -> dict[str, Any]
```

No task requires a dependency or authority surface not defined by an earlier task.
