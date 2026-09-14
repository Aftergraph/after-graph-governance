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


if __name__ == "__main__":
    unittest.main()
