#!/usr/bin/env python3
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FRONTIER = ROOT / "docs/contracts/frontier-lifecycle/1.0.json"
REGISTRY = ROOT / "docs/contracts/economic-graph/1.0/registry.json"
CAPS = ROOT / "docs/contracts/economic-graph/1.0/capabilities.json"
FRONTIER_DOC = ROOT / "docs/AFTERGRAPH-FRONTIER-V1.md"
ECON_DOC = ROOT / "docs/ECONOMIC-GRAPH-V1.md"
PROMOTION = ROOT / "docs/evidence/promotions/economic-graph-v1.json"
LIVE_FRONTIER = ROOT / "docs/frontier/economic-live-settlement-v1.json"
SETTLEMENT_VECTORS = ROOT / "docs/platform-conformance/economic-live-settlement-v1/vectors.json"

def load(path):
    return json.loads(path.read_text(encoding="utf-8"))

class FrontierLifecycleTest(unittest.TestCase):
    def test_frontier_is_lifecycle_not_owner(self):
        text = FRONTIER_DOC.read_text(encoding="utf-8").lower()
        self.assertIn("not a repository", text)
        self.assertIn("never executes work", text)
        self.assertIn("never carries authority", text)

    def test_lifecycle_schema_contains_required_states(self):
        schema = load(FRONTIER)
        values = set(schema["properties"]["lifecycle"]["enum"])
        self.assertTrue({"experimental","frontier","candidate","canonical","quarantined","deprecated","archived"} <= values)

class EconomicGraphTest(unittest.TestCase):
    def test_registry_has_no_new_plane_or_owner(self):
        reg = load(REGISTRY)
        self.assertEqual(reg["normative_owner"], "after-graph-governance")
        self.assertEqual(reg["semantic_owners"]["capability_discovery_routing_client"], "core")
        self.assertIn("works-execution", reg["semantic_owners"]["durable_work_execution_recovery"])
        self.assertIn("model output is never authorization truth", reg["invariants"])

    def test_maturity_is_capability_level(self):
        caps = {c["id"]: c for c in load(CAPS)["capabilities"]}
        self.assertEqual(caps["economic.simulate"]["lifecycle"], "canonical")
        self.assertEqual(caps["economic.observe"]["lifecycle"], "canonical")
        self.assertEqual(caps["economic.live-settlement"]["lifecycle"], "candidate")
        self.assertEqual(caps["economic.transaction-signing"]["lifecycle"], "experimental")
        self.assertEqual(caps["economic.custody"]["lifecycle"], "experimental")
        self.assertEqual(caps["economic.autonomous-spend"]["lifecycle"], "experimental")

    def test_core_is_client_only(self):
        doc = ECON_DOC.read_text(encoding="utf-8").lower()
        self.assertIn("non-authoritative developer facade", doc)
        self.assertIn("never grants authority", doc)

    def test_zero_effect_slice_is_canonical(self):
        reg = load(REGISTRY)
        self.assertIn("v1 runtime observation externalEffects must equal 0", reg["invariants"])

    def test_promotion_is_governance_owned_and_not_self_promoted(self):
        record = load(PROMOTION)
        self.assertEqual(record["lifecycle"], "canonical")
        self.assertFalse(record["self_promoted"])
        self.assertFalse(record["carries_authority"])
        self.assertTrue(record["verifier_refs"])
        self.assertTrue(record["gate_ref"])
        self.assertTrue(record["registry_evidence_ref"])

    def test_live_settlement_is_candidate_without_authority(self):
        record = load(LIVE_FRONTIER)
        self.assertEqual(record["lifecycle"], "candidate")
        self.assertFalse(record["self_promoted"])
        self.assertFalse(record["carries_authority"])

    def test_live_settlement_vectors_fail_closed(self):
        vectors = load(SETTLEMENT_VECTORS)
        by_id = {v["id"]: v for v in vectors["vectors"]}
        self.assertEqual(by_id["ELS-001"]["expected"]["final"], False)
        self.assertEqual(by_id["ELS-001"]["expected"]["externalEffects"], 0)
        self.assertEqual(by_id["ELS-002"]["expected"]["state"], "UNCERTAIN")
        self.assertEqual(by_id["ELS-003"]["expected"]["state"], "ABORTED")
        self.assertEqual(by_id["ELS-004"]["expected"]["decision"], "DENY")
        self.assertEqual(by_id["ELS-005"]["expected"]["decision"], "DENY")
        self.assertTrue(vectors["promotion_blockers"], "live settlement must retain explicit canonical-promotion blockers")

if __name__ == "__main__":
    unittest.main()
