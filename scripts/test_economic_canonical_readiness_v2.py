#!/usr/bin/env python3
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "docs/contracts/economic-graph/1.0/canonical-readiness.schema.json"
VECTORS = ROOT / "docs/platform-conformance/economic-canonical-readiness-v2/vectors.json"
READINESS = ROOT / "docs/frontier/economic-canonical-readiness-v2.json"
CAPS = ROOT / "docs/contracts/economic-graph/1.0/capabilities.json"

def load(path):
    return json.loads(path.read_text(encoding="utf-8"))

class EconomicCanonicalReadinessV2(unittest.TestCase):
    def test_schema_forbids_effects_and_authority_overclaim(self):
        schema = load(SCHEMA)
        props = schema["properties"]
        self.assertEqual(props["externalEffects"]["const"], 0)
        self.assertFalse(props["signatureProduced"]["const"])
        self.assertFalse(props["signingMaterialExposed"]["const"])
        self.assertFalse(props["liveCustodyApiCalled"]["const"])
        self.assertFalse(props["canBroadcast"]["const"])
        self.assertFalse(props["canMoveAssets"]["const"])
        self.assertFalse(props["final"]["const"])

    def test_vectors_cover_human_control_and_recovery(self):
        vectors = load(VECTORS)
        by_id = {v["id"]: v for v in vectors["vectors"]}
        self.assertEqual(by_id["ECR-002"]["expected"]["decision"], "DENY")
        self.assertEqual(by_id["ECR-004"]["expected"]["state"], "ABORTED_BY_KILL_SWITCH")
        self.assertEqual(by_id["ECR-005"]["expected"]["state"], "ABORTED_BY_REVOCATION")
        self.assertFalse(by_id["ECR-007"]["expected"]["final"])
        self.assertEqual(by_id["ECR-007"]["expected"]["externalEffects"], 0)
        self.assertTrue(vectors["canonical_promotion_blockers"])

    def test_readiness_does_not_promote_or_enable_live_value(self):
        readiness = load(READINESS)
        self.assertEqual(readiness["lifecycle"], "candidate")
        self.assertFalse(readiness["promotion_allowed"])
        self.assertFalse(readiness["canonical_promotion_allowed"])
        self.assertFalse(readiness["carries_authority"])
        self.assertEqual(readiness["readiness"]["signature_production"], "disabled")
        self.assertEqual(readiness["readiness"]["broadcast"], "disabled")
        self.assertEqual(readiness["readiness"]["live_custody_api"], "disabled")
        self.assertEqual(readiness["readiness"]["asset_movement"], "disabled")
        self.assertEqual(readiness["readiness"]["live_value_execution"], "disabled")

    def test_consequential_capabilities_remain_noncanonical(self):
        caps = {c["id"]: c for c in load(CAPS)["capabilities"]}
        self.assertEqual(caps["economic.live-settlement"]["lifecycle"], "candidate")
        self.assertEqual(caps["economic.transaction-signing"]["lifecycle"], "experimental")
        self.assertEqual(caps["economic.custody"]["lifecycle"], "experimental")
        self.assertEqual(caps["economic.autonomous-spend"]["lifecycle"], "experimental")

if __name__ == "__main__":
    unittest.main()
