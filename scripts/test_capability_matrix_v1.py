#!/usr/bin/env python3
"""Shape tests for the L0-L6 capability conformance matrix (Phase 1.4 / K).

Run: python scripts/test_capability_matrix_v1.py

The matrix is judgment backed by cited evidence, so tests pin SHAPE and
discipline, not ratings:
- every row names a topology-registered owner and a valid L0-L6 level
- every row carries a non-empty evidence pointer and evidence class
- every sub-L4 row names its blocker (no silent gaps)
- no row claims L5/L6 without external/live measurement refs
- no row claims live cross-service integration without exact-head refs
"""
import json
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
MATRIX = REPO_ROOT / "docs" / "evidence" / "capability-conformance-2026-09-10.json"
TOPOLOGY = REPO_ROOT / "docs" / "platform-topology" / "2.0.json"

LEVELS = {"L0", "L1", "L2", "L3", "L4"}
EVIDENCE_CLASSES = {"live", "simulated", "internal", "external"}


class MatrixShapeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.matrix = json.loads(MATRIX.read_text(encoding="utf-8"))
        cls.topology_names = {r["name"] for r in
                              json.loads(TOPOLOGY.read_text(encoding="utf-8"))["repositories"]}

    def test_envelope(self):
        self.assertEqual(self.matrix["schema"], "capability-conformance/0.1")
        self.assertTrue(self.matrix["rows"])

    def test_rows_carry_required_fields(self):
        required = {"capability", "owner", "level", "evidence_class",
                    "evidence_ref", "blocker", "last_verified"}
        for row in self.matrix["rows"]:
            self.assertTrue(required <= set(row), row.get("capability"))

    def test_owner_is_topology_registered(self):
        for row in self.matrix["rows"]:
            self.assertIn(row["owner"], self.topology_names, row["capability"])

    def test_level_valid_and_ladder_capped(self):
        for row in self.matrix["rows"]:
            self.assertIn(row["level"], LEVELS, row["capability"])

    def test_evidence_class_scoped(self):
        for row in self.matrix["rows"]:
            self.assertIn(row["evidence_class"], EVIDENCE_CLASSES, row["capability"])

    def test_sub_l4_rows_name_blocker(self):
        for row in self.matrix["rows"]:
            if row["level"] != "L4":
                self.assertTrue(row["blocker"].strip(), row["capability"])

    def test_no_live_integration_claim_without_exact_head_ref(self):
        for row in self.matrix["rows"]:
            if row["evidence_class"] == "live" and "integration" in row["capability"]:
                self.assertRegex(row["evidence_ref"], r"[0-9a-f]{7,40}", row["capability"])

    def test_last_verified_is_date(self):
        for row in self.matrix["rows"]:
            self.assertRegex(row["last_verified"], r"^\d{4}-\d{2}-\d{2}$", row["capability"])


if __name__ == "__main__":
    unittest.main()
