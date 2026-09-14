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
    def _inputs(self):
        module = load_module()
        return (
            module,
            module.load_json(ROOT / "docs/program-overlay/mission-continuity.json"),
            module.load_json(ROOT / "docs/platform-topology/2.0.json"),
            module.load_json(ROOT / "docs/semantic-seams/0.1.json"),
            module.load_json(ROOT / "docs/semantic-claims/empty.json"),
        )

    def test_canonical_fixture_validates(self):
        module, overlay, topology, seams, _ = self._inputs()
        self.assertEqual(module.validate_overlay(overlay, topology, seams), [])

    def test_fixture_does_not_copy_exact_git_state(self):
        overlay = json.loads((ROOT / "docs/program-overlay/mission-continuity.json").read_text())
        serialized = json.dumps(overlay)
        self.assertNotIn("remote_head_sha", serialized)
        self.assertNotIn("head_sha", serialized)
        self.assertNotIn("commit_sha", serialized)

    def test_unknown_repo_is_rejected(self):
        module, overlay, topology, seams, _ = self._inputs()
        overlay["touches"][0]["repo"] = "not-a-real-repo"
        errors = module.validate_overlay(overlay, topology, seams)
        self.assertTrue(any("unknown repo" in error for error in errors))

    def test_unknown_seam_is_rejected(self):
        module, overlay, topology, seams, _ = self._inputs()
        overlay["touches"][0]["seam"] = "seam://unknown/value"
        errors = module.validate_overlay(overlay, topology, seams)
        self.assertTrue(any("unknown seam" in error for error in errors))

    def test_forbidden_exact_git_truth_field_is_rejected(self):
        module, overlay, topology, seams, _ = self._inputs()
        overlay["head_sha"] = "0" * 40
        errors = module.validate_overlay(overlay, topology, seams)
        self.assertTrue(any("forbidden truth field" in error for error in errors))

    def test_write_write_same_seam_blocks(self):
        module = load_module()
        claims = {
            "schema": "semantic-claims/0.1",
            "claims": [
                {"claim_id": "c1", "seam": "seam://runtime/runtime-binding", "mode": "WRITE", "status": "active"},
                {"claim_id": "c2", "seam": "seam://runtime/runtime-binding", "mode": "WRITE", "status": "active"},
            ],
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
                {"claim_id": "c2", "seam": "seam://runtime/runtime-binding", "mode": "WRITE", "status": "active"},
            ],
        }
        self.assertEqual(module.claim_conflicts(claims, now=None), [])

    def test_migrate_write_same_seam_blocks(self):
        module = load_module()
        claims = {
            "schema": "semantic-claims/0.1",
            "claims": [
                {"claim_id": "c1", "seam": "seam://works/execution-context", "mode": "MIGRATE", "status": "active"},
                {"claim_id": "c2", "seam": "seam://works/execution-context", "mode": "WRITE", "status": "active"},
            ],
        }
        conflicts = module.claim_conflicts(claims, now=None)
        self.assertEqual(conflicts[0]["kind"], "MIGRATE_WRITE")

    def test_unrelated_write_claims_do_not_conflict(self):
        module = load_module()
        claims = {
            "schema": "semantic-claims/0.1",
            "claims": [
                {"claim_id": "c1", "seam": "seam://runtime/runtime-binding", "mode": "WRITE", "status": "active"},
                {"claim_id": "c2", "seam": "seam://studio/mission-projection", "mode": "WRITE", "status": "active"},
            ],
        }
        self.assertEqual(module.claim_conflicts(claims, now=None), [])

    def test_expired_write_claim_does_not_block(self):
        module = load_module()
        claims = {
            "schema": "semantic-claims/0.1",
            "claims": [
                {
                    "claim_id": "expired",
                    "seam": "seam://runtime/runtime-binding",
                    "mode": "WRITE",
                    "status": "active",
                    "expires_at": "2000-01-01T00:00:00Z",
                },
                {"claim_id": "current", "seam": "seam://runtime/runtime-binding", "mode": "WRITE", "status": "active"},
            ],
        }
        self.assertEqual(module.claim_conflicts(claims, now=None), [])

    def test_valid_no_claims_passes(self):
        module, overlay, topology, seams, claims = self._inputs()
        result = module.evaluate_direction(overlay, topology, seams, claims, now=None)
        self.assertEqual(result["decision"], "PASS")

    def test_conflicting_write_claims_block(self):
        module, overlay, topology, seams, _ = self._inputs()
        result = module.evaluate_direction(
            overlay,
            topology,
            seams,
            module.load_json(ROOT / "docs/semantic-claims/conflict-example.json"),
            now=None,
        )
        self.assertEqual(result["decision"], "BLOCK")
        self.assertTrue(result["conflicting_claims"])

    def test_invalid_or_unknown_input_is_unknown_not_pass(self):
        module, overlay, topology, seams, claims = self._inputs()
        overlay["touches"][0]["seam"] = "seam://missing/value"
        result = module.evaluate_direction(overlay, topology, seams, claims, now=None)
        self.assertEqual(result["decision"], "UNKNOWN")
        self.assertTrue(result["unknowns"])

    def test_malformed_expiry_is_unknown_not_exception(self):
        module, overlay, topology, seams, _ = self._inputs()
        claims = {
            "schema": "semantic-claims/0.1",
            "claims": [
                {
                    "claim_id": "bad-expiry",
                    "seam": "seam://runtime/runtime-binding",
                    "mode": "WRITE",
                    "status": "active",
                    "expires_at": "not-a-timestamp",
                }
            ],
        }
        result = module.evaluate_direction(overlay, topology, seams, claims, now=None)
        self.assertEqual(result["decision"], "UNKNOWN")
        self.assertTrue(any("expires_at" in item for item in result["unknowns"]))

    def test_unknown_claim_status_is_unknown_not_ignored(self):
        module, overlay, topology, seams, _ = self._inputs()
        claims = {
            "schema": "semantic-claims/0.1",
            "claims": [
                {
                    "claim_id": "bad-status",
                    "seam": "seam://runtime/runtime-binding",
                    "mode": "WRITE",
                    "status": "mystery",
                }
            ],
        }
        result = module.evaluate_direction(overlay, topology, seams, claims, now=None)
        self.assertEqual(result["decision"], "UNKNOWN")
        self.assertTrue(any("status" in item for item in result["unknowns"]))

    def test_missing_claim_id_is_unknown(self):
        module, overlay, topology, seams, _ = self._inputs()
        claims = {
            "schema": "semantic-claims/0.1",
            "claims": [
                {
                    "seam": "seam://runtime/runtime-binding",
                    "mode": "WRITE",
                    "status": "active",
                }
            ],
        }
        result = module.evaluate_direction(overlay, topology, seams, claims, now=None)
        self.assertEqual(result["decision"], "UNKNOWN")
        self.assertTrue(any("claim_id" in item for item in result["unknowns"]))

    def test_active_slices_must_be_list_of_nonempty_strings(self):
        module, overlay, topology, seams, claims = self._inputs()
        overlay["active_slices"] = "MC-001"
        result = module.evaluate_direction(overlay, topology, seams, claims, now=None)
        self.assertEqual(result["decision"], "UNKNOWN")
        self.assertTrue(any("active_slices" in item for item in result["unknowns"]))

    def test_unknown_overlay_status_is_unknown(self):
        module, overlay, topology, seams, claims = self._inputs()
        overlay["status"] = "mystery"
        result = module.evaluate_direction(overlay, topology, seams, claims, now=None)
        self.assertEqual(result["decision"], "UNKNOWN")
        self.assertTrue(any("overlay status" in item for item in result["unknowns"]))

    def test_unknown_seam_registry_schema_is_unknown(self):
        module, overlay, topology, seams, claims = self._inputs()
        seams["schema"] = "semantic-seams/999"
        result = module.evaluate_direction(overlay, topology, seams, claims, now=None)
        self.assertEqual(result["decision"], "UNKNOWN")
        self.assertTrue(any("seam registry schema" in item for item in result["unknowns"]))

    def test_unknown_seam_registry_status_is_unknown(self):
        module, overlay, topology, seams, claims = self._inputs()
        seams["status"] = "canonical"
        result = module.evaluate_direction(overlay, topology, seams, claims, now=None)
        self.assertEqual(result["decision"], "UNKNOWN")
        self.assertTrue(any("seam registry status" in item for item in result["unknowns"]))

    def test_verify_write_same_seam_without_independence_evidence_is_unknown(self):
        module, overlay, topology, seams, _ = self._inputs()
        claims = {
            "schema": "semantic-claims/0.1",
            "claims": [
                {"claim_id": "writer", "seam": "seam://runtime/runtime-binding", "mode": "WRITE", "status": "active"},
                {"claim_id": "verifier", "seam": "seam://runtime/runtime-binding", "mode": "VERIFY", "status": "active"},
            ],
        }
        result = module.evaluate_direction(overlay, topology, seams, claims, now=None)
        self.assertEqual(result["decision"], "UNKNOWN")
        self.assertTrue(any("VERIFY/WRITE independence" in item for item in result["unknowns"]))

    def test_sentinel_seam_is_code_review_specific(self):
        _, _, _, seams, _ = self._inputs()
        seam_ids = {row["id"] for row in seams["seams"]}
        self.assertIn("seam://verification/code-review-verdict", seam_ids)
        self.assertNotIn("seam://verification/outcome-verdict", seam_ids)

    def test_seam_owner_must_exist_in_topology(self):
        module, _, topology, seams, _ = self._inputs()
        seams["seams"][0]["owner_repo"] = "missing-owner"
        errors = module.validate_seam_registry(seams, topology)
        self.assertTrue(any("owner repo" in error for error in errors))

    def test_core_touch_must_match_seam_owner(self):
        module, overlay, topology, seams, _ = self._inputs()
        overlay["touches"][0]["repo"] = "runtime"
        errors = module.validate_overlay(overlay, topology, seams)
        self.assertTrue(any("core touch does not match seam owner" in error for error in errors))


    def test_declared_program_blocker_blocks_shadow_evaluation(self):
        module, overlay, topology, seams, claims = self._inputs()
        result = module.evaluate_direction(overlay, topology, seams, claims, now=None)
        self.assertEqual(result["decision"], "BLOCK")
        self.assertTrue(any("execution-context/1.0" in item for item in result["reasons"]))

    def test_cleared_program_blockers_restore_pass(self):
        module, overlay, topology, seams, claims = self._inputs()
        overlay["blocked_by"] = []
        result = module.evaluate_direction(overlay, topology, seams, claims, now=None)
        self.assertEqual(result["decision"], "PASS")
        self.assertEqual(result["reasons"], [])

    def test_malformed_blocked_by_is_unknown_not_pass(self):
        module, overlay, topology, seams, claims = self._inputs()
        overlay["blocked_by"] = [{"contract": ""}, "bad-row"]
        result = module.evaluate_direction(overlay, topology, seams, claims, now=None)
        self.assertEqual(result["decision"], "UNKNOWN")
        self.assertTrue(any("blocked_by" in item for item in result["unknowns"]))


if __name__ == "__main__":
    unittest.main()
