#!/usr/bin/env python3
import json, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SCHEMA=ROOT/"docs/contracts/economic-graph/1.0/evidence-coherence.schema.json"
VECTORS=ROOT/"docs/platform-conformance/economic-evidence-coherence-v9/vectors.json"
READINESS=ROOT/"docs/frontier/economic-evidence-coherence-v9.json"
def load(p): return json.loads(p.read_text(encoding="utf-8"))
class EvidenceCoherenceV9(unittest.TestCase):
  def test_contract_never_claims_finality_or_effects(self):
    p=load(SCHEMA)["properties"]
    self.assertFalse(p["final"]["const"])
    self.assertEqual(p["externalEffects"]["const"],0)
    self.assertIn("TEMPORALLY_COHERENT",p["state"]["enum"])
    self.assertIn("EVIDENCE_REFRESH_REQUIRED",p["state"]["enum"])
  def test_vectors_fail_closed_on_stale_replay_and_skew(self):
    by={v["id"]:v for v in load(VECTORS)["vectors"]}
    for i in range(2,8):
      self.assertTrue(by[f"EEC-00{i}"]["expected"]["refreshRequired"])
    self.assertEqual(by["EEC-008"]["expected"]["verification"],"EVIDENCE_REFRESH_REQUIRED")
    self.assertFalse(by["EEC-008"]["expected"]["temporallyCoherent"])
  def test_readiness_is_non_authoritative(self):
    r=load(READINESS)
    self.assertEqual(r["lifecycle"],"candidate")
    self.assertFalse(r["promotion_allowed"])
    self.assertFalse(r["canonical_promotion_allowed"])
    self.assertFalse(r["carries_authority"])
    self.assertTrue(r["verified_design_constraints"]["strict_generation_monotonicity"])
    self.assertTrue(r["verified_design_constraints"]["stale_evidence_fails_closed"])
    self.assertFalse(r["verified_design_constraints"]["final"])
    self.assertEqual(r["verified_design_constraints"]["external_effects"],0)
    self.assertTrue(r["remaining"])
if __name__=="__main__": unittest.main()
