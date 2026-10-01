#!/usr/bin/env python3
import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CAPTURE=ROOT/"docs/contracts/economic-graph/1.0/right-capture.schema.json"
VERIFY=ROOT/"docs/contracts/economic-graph/1.0/right-capture-set-verification.schema.json"
VECTORS=ROOT/"docs/platform-conformance/economic-source-capture-v12/vectors.json"
READINESS=ROOT/"docs/frontier/economic-source-capture-v12.json"
CAPS=ROOT/"docs/contracts/economic-graph/1.0/capabilities.json"

def load(p):
    return json.loads(p.read_text(encoding="utf-8"))

class SourceCaptureV12(unittest.TestCase):
    def test_capture_contract_is_read_only_nonfinal_and_immutable(self):
        p=load(CAPTURE)["properties"]
        self.assertEqual(p["sourceTransport"]["const"],"READ_ONLY")
        self.assertTrue(p["immutable"]["const"])
        self.assertFalse(p["final"]["const"])
        self.assertEqual(p["externalEffects"]["const"],0)
        self.assertEqual(p["generation"]["minimum"],1)
        self.assertIn("offset",p["cursor"]["properties"]["kind"]["enum"])

    def test_verification_cannot_grant_authority(self):
        p=load(VERIFY)["properties"]
        self.assertFalse(p["executionAuthority"]["const"])
        self.assertFalse(p["final"]["const"])
        self.assertFalse(p["promotionAuthority"]["const"])
        self.assertEqual(p["externalEffects"]["const"],0)

    def test_vectors_cover_identity_digest_time_cursor_and_set_binding(self):
        by={v["id"]:v for v in load(VECTORS)["vectors"]}
        for i in range(2,9):
            self.assertFalse(by[f"ESC-00{i}"]["expected"]["valid"])
        self.assertEqual(
            by["ESC-009"]["expected"]["projectionFields"],
            ["sourceClass","sourceId","evidenceHash","generation","observedAtUnix"]
        )
        self.assertFalse(by["ESC-009"]["expected"]["authority"])

    def test_readiness_does_not_promote_candidate(self):
        r=load(READINESS)
        self.assertEqual(r["lifecycle"],"candidate")
        self.assertFalse(r["promotion_allowed"])
        self.assertFalse(r["canonical_promotion_allowed"])
        self.assertFalse(r["carries_authority"])
        self.assertFalse(r["readiness"]["executionAuthority"])
        self.assertFalse(r["readiness"]["final"])
        self.assertFalse(r["readiness"]["promotionAuthority"])
        self.assertEqual(r["readiness"]["externalEffects"],0)
        self.assertTrue(r["implementation_refs"]["runtime_pending"]["merge_required"])
        self.assertTrue(r["implementation_refs"]["works_pending"]["merge_required"])
        self.assertTrue(r["implementation_refs"]["sentinel_pending"]["merge_required"])
        caps={c["id"]:c for c in load(CAPS)["capabilities"]}
        self.assertEqual(caps["economic.live-settlement"]["lifecycle"],"candidate")

if __name__=="__main__":
    unittest.main()
