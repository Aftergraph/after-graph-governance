#!/usr/bin/env python3
"""Governance sensor for Business Ops P0/P1 design artifacts."""
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "docs/superpowers/specs/2026-09-15-aftergraph-business-ops-thin-domain-kernel-design.md"
ALGORITHMS = ROOT / "docs/superpowers/specs/2026-09-15-aftergraph-business-ops-algorithms-v0.1.md"
CHARGE = ROOT / "docs/contracts/business-ops/charge-fact/0.1.schema.json"
MAPPING = ROOT / "docs/contracts/business-ops/migration-mapping/0.1.schema.json"
VECTORS = ROOT / "docs/platform-conformance/business-ops/0.1/vectors.json"
READINESS = ROOT / "docs/business-ops/p1-readiness-2026-09-15.md"

class BusinessOpsP0DesignTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.spec = SPEC.read_text()
        cls.algorithms = ALGORITHMS.read_text()
        cls.charge = json.loads(CHARGE.read_text())
        cls.mapping = json.loads(MAPPING.read_text())
        cls.vectors = json.loads(VECTORS.read_text())
        cls.readiness = READINESS.read_text()

    def test_review_changes_are_machine_visible(self):
        for marker in [
            "Production deployment provenance gate",
            "read-only domain projection emitted by Business Ops",
            "status=AMBIGUOUS",
            "Aftergraph Billing domain, currently incubated in `Aftergraph/studio`",
            "### 20.1 P1 readiness gate",
        ]:
            self.assertIn(marker, self.spec)

    def test_charge_fact_excludes_financial_truth(self):
        props = set(self.charge["properties"])
        forbidden = {"invoice_id", "invoice_number", "amount_minor", "rate_minor", "tax_rate", "payment_status", "currency"}
        self.assertFalse(props & forbidden, props & forbidden)
        self.assertFalse(self.charge["additionalProperties"])
        self.assertIn("actuals_verification_ref", self.charge["required"])

    def test_ambiguous_mapping_requires_null_target(self):
        self.assertFalse(self.mapping["additionalProperties"])
        text = json.dumps(self.mapping)
        self.assertIn('"AMBIGUOUS"', text)
        self.assertRegex(text, r'"target_entity_id".*?"type": "null"')

    def test_vectors_cover_required_failure_modes(self):
        vectors = self.vectors["vectors"]
        ids = [v["id"] for v in vectors]
        self.assertEqual(len(ids), len(set(ids)))
        required = {"MAP-002", "CHG-002", "REC-001", "EVD-001", "SHD-001", "CUT-001"}
        self.assertTrue(required.issubset(ids), required - set(ids))
        ambiguous = next(v for v in vectors if v["id"] == "MAP-002")
        self.assertEqual(ambiguous["expected"]["status"], "AMBIGUOUS")
        self.assertIsNone(ambiguous["expected"]["target_entity_id"])
        self.assertFalse(ambiguous["expected"]["canonical_entity_created"])

    def test_readiness_distinguishes_planning_from_cutover(self):
        self.assertIn("p1_planning_ready: true", self.readiness)
        self.assertIn("production_cutover_ready: false", self.readiness)
        self.assertIn("production_sha_verified: false", self.readiness)
        self.assertIn("production_db_ledger_acquired: false", self.readiness)

    def test_algorithms_preserve_platform_boundaries(self):
        for marker in ["AIE authority evaluation", "Trust admission", "Runtime dispatch", "WORKS durable attempt"]:
            self.assertIn(marker, self.algorithms)
        self.assertIn("cannot create business truth", self.algorithms.lower())
        self.assertIn("do not emit rate, tax, invoice amount", self.algorithms.lower())

if __name__ == "__main__":
    unittest.main()
