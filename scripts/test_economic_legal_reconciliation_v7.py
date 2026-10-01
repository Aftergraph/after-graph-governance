#!/usr/bin/env python3
import json, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
RECORDS=ROOT/"docs/contracts/economic-graph/1.0/legal-records.schema.json"
RECON=ROOT/"docs/contracts/economic-graph/1.0/legal-reconciliation.schema.json"
VECTORS=ROOT/"docs/platform-conformance/economic-legal-reconciliation-v7/vectors.json"
READINESS=ROOT/"docs/frontier/economic-legal-reconciliation-v7.json"
CAPS=ROOT/"docs/contracts/economic-graph/1.0/capabilities.json"
def load(p): return json.loads(p.read_text(encoding="utf-8"))
class LegalReconciliationV7(unittest.TestCase):
  def test_record_schema_keeps_sources_zero_effect_nonfinal(self):
    s=load(RECORDS)
    common=s["$defs"]["common"]["properties"]
    self.assertEqual(common["externalEffects"]["const"],0)
    self.assertFalse(common["final"]["const"])
    self.assertIn("ACTIVE",s["$defs"]["status"]["enum"])
  def test_reconciliation_never_claims_legal_finality(self):
    p=load(RECON)["properties"]
    self.assertFalse(p["final"]["const"])
    self.assertEqual(p["externalEffects"]["const"],0)
    self.assertIn("LEGAL_RIGHT_ALIGNED",p["state"]["enum"])
    self.assertIn("LEGAL_RECONCILIATION_REQUIRED",p["state"]["enum"])
  def test_vectors_force_legal_reconciliation_on_any_disagreement(self):
    by={v["id"]:v for v in load(VECTORS)["vectors"]}
    for i in range(2,8):
      self.assertTrue(by[f"ELR-00{i}"]["expected"]["reconciliationRequired"])
    self.assertEqual(by["ELR-008"]["expected"]["verification"],"LEGAL_RECONCILIATION_REQUIRED")
    self.assertFalse(by["ELR-008"]["expected"]["legalRightAligned"])
  def test_readiness_remains_non_authoritative(self):
    r=load(READINESS)
    self.assertEqual(r["lifecycle"],"candidate")
    self.assertFalse(r["promotion_allowed"])
    self.assertFalse(r["canonical_promotion_allowed"])
    self.assertFalse(r["carries_authority"])
    self.assertTrue(r["verified_design_constraints"]["ledger_representation_not_authoritative"])
    self.assertFalse(r["verified_design_constraints"]["legal_finality"])
    self.assertEqual(r["verified_design_constraints"]["external_effects"],0)
    self.assertTrue(r["remaining"])
    caps={c["id"]:c for c in load(CAPS)["capabilities"]}
    self.assertEqual(caps["economic.live-settlement"]["lifecycle"],"candidate")
if __name__=="__main__": unittest.main()
