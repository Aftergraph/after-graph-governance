#!/usr/bin/env python3
import json, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
VECTORS=ROOT/"docs/platform-conformance/economic-right-source-readonly-v8/vectors.json"
READINESS=ROOT/"docs/frontier/economic-right-source-readonly-v8.json"
RECORDS=ROOT/"docs/contracts/economic-graph/1.0/legal-records.schema.json"
def load(p): return json.loads(p.read_text(encoding="utf-8"))
class RightSourceReadonlyV8(unittest.TestCase):
  def test_vectors_lock_read_only_transport(self):
    by={v["id"]:v for v in load(VECTORS)["vectors"]}
    self.assertEqual(by["ERS-001"]["expected"]["method"],"GET")
    self.assertEqual(by["ERS-002"]["expected"]["reason"],"ECONOMIC_RIGHT_SOURCE_HTTPS_REQUIRED")
    self.assertFalse(by["ERS-004"]["expected"]["credentialPresentInEvidence"])
    self.assertEqual(by["ERS-005"]["expected"]["reason"],"ECONOMIC_RIGHT_SOURCE_RESPONSE_TOO_LARGE")
    self.assertEqual(by["ERS-007"]["expected"]["reason"],"ECONOMIC_RIGHT_SOURCE_PATH_INVALID")
    self.assertTrue(by["ERS-008"]["expected"]["evidenceHashComputedByRuntime"])
    self.assertFalse(by["ERS-009"]["expected"]["final"])
    self.assertEqual(by["ERS-009"]["expected"]["externalEffects"],0)
  def test_readiness_does_not_create_authority(self):
    r=load(READINESS)
    self.assertEqual(r["lifecycle"],"candidate")
    self.assertFalse(r["promotion_allowed"])
    self.assertFalse(r["canonical_promotion_allowed"])
    self.assertFalse(r["carries_authority"])
    self.assertEqual(r["readiness"]["external_effects"],0)
    self.assertFalse(r["readiness"]["final"])
    self.assertFalse(r["runtime_ref"]["merge_required"])
    self.assertEqual(r["runtime_ref"]["merge_sha"],"c5a75498eb308eded3bb08cbaa2b2de739b9499c")
    self.assertEqual(r["status"],"VERIFIED_MERGED_RUNTIME")
    self.assertTrue(r["verified"]["runtime_build"])
    self.assertTrue(r["verified"]["runtime_tests"])
    self.assertTrue(r["verified"]["runtime_merged"])
    self.assertTrue(r["remaining"])
  def test_v8_outputs_are_v7_legal_record_schemas(self):
    schemas=set()
    for variant in load(RECORDS)["oneOf"]:
      schemas.add(variant["properties"]["schema"]["const"])
    expected={
      "aftergraph.authoritative-asset-registry-record/v1",
      "aftergraph.custodial-right-record/v1",
      "aftergraph.ledger-asset-representation-record/v1"
    }
    self.assertEqual(schemas,expected)
if __name__=="__main__": unittest.main()
