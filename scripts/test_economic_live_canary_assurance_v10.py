#!/usr/bin/env python3
import json, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SCHEMA=ROOT/"docs/contracts/economic-graph/1.0/live-canary-assurance.schema.json"
VECTORS=ROOT/"docs/platform-conformance/economic-live-canary-assurance-v10/vectors.json"
READINESS=ROOT/"docs/frontier/economic-live-canary-assurance-v10.json"
CAPS=ROOT/"docs/contracts/economic-graph/1.0/capabilities.json"
def load(p): return json.loads(p.read_text(encoding="utf-8"))
class LiveCanaryAssuranceV10(unittest.TestCase):
  def test_assurance_schema_is_non_authoritative(self):
    p=load(SCHEMA)["properties"]
    self.assertFalse(p["executionAuthority"]["const"])
    self.assertFalse(p["liveValueEnabled"]["const"])
    self.assertEqual(p["maxLiveValue"]["const"],0)
    self.assertFalse(p["final"]["const"])
    self.assertFalse(p["promotionAuthority"]["const"])
    self.assertEqual(p["externalEffects"]["const"],0)
  def test_vectors_fail_closed_and_keep_candidate_execute_denied(self):
    by={v["id"]:v for v in load(VECTORS)["vectors"]}
    self.assertTrue(by["ELA-001"]["expected"]["readyForLiveCanaryReview"])
    self.assertFalse(by["ELA-001"]["expected"]["executionAuthority"])
    self.assertEqual(by["ELA-001"]["expected"]["maxLiveValue"],0)
    for i in range(2,9):
      self.assertFalse(by[f"ELA-00{i}"]["expected"]["readyForLiveCanaryReview"])
    self.assertEqual(by["ELA-009"]["expected"]["decision"],"DENY")
    self.assertEqual(by["ELA-009"]["expected"]["reason"],"economic_live_settlement_not_canonical")
  def test_readiness_does_not_promote_candidate(self):
    r=load(READINESS)
    self.assertEqual(r["lifecycle"],"candidate")
    self.assertFalse(r["promotion_allowed"])
    self.assertFalse(r["canonical_promotion_allowed"])
    self.assertFalse(r["carries_authority"])
    self.assertFalse(r["enforced_non_capabilities"]["executionAuthority"])
    self.assertFalse(r["enforced_non_capabilities"]["liveValueEnabled"])
    self.assertEqual(r["enforced_non_capabilities"]["maxLiveValue"],0)
    self.assertEqual(r["enforced_non_capabilities"]["externalEffects"],0)
    caps={c["id"]:c for c in load(CAPS)["capabilities"]}
    self.assertEqual(r["status"],"VERIFIED_MERGED_IMPLEMENTATIONS")
    self.assertEqual(r["implementation_refs"]["sentinel"],"b1bc8cd74974d36e5a280b0fbe3630bfb367b55f")
    self.assertEqual(r["implementation_refs"]["trust_gateway"],"dd4829e81bf3f6a1637b3c12f2fadd4fb719d5c4")
    self.assertTrue(r["verified"]["sentinel_merged"])
    self.assertTrue(r["verified"]["trust_gateway_merged"])
    self.assertTrue(r["verified"]["review_readiness_non_authoritative"])
    self.assertTrue(r["verified"]["max_live_value_zero"])
    self.assertEqual(caps["economic.live-settlement"]["lifecycle"],"candidate")
if __name__=="__main__": unittest.main()
