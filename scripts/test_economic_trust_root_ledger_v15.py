#!/usr/bin/env python3
import json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
STATE=ROOT/"docs/contracts/economic-graph/1.0/source-trust-root-state.schema.json"
TRANS=ROOT/"docs/contracts/economic-graph/1.0/source-trust-root-transition.schema.json"
V=ROOT/"docs/platform-conformance/economic-trust-root-ledger-v15/vectors.json"
R=ROOT/"docs/frontier/economic-trust-root-ledger-v15.json"
def load(p): return json.loads(p.read_text())
class TrustRootLedgerV15(unittest.TestCase):
  def test_state_contract_has_monotonic_fields(self):
    p=load(STATE)["properties"]
    self.assertEqual(p["generation"]["minimum"],1)
    self.assertEqual(p["minAttestationGeneration"]["minimum"],1)
    self.assertEqual(p["revision"]["minimum"],1)
    self.assertIn("REVOKED",p["status"]["enum"])
  def test_transition_zero_effect(self):
    p=load(TRANS)["properties"]
    self.assertEqual(p["externalEffects"]["const"],0)
    self.assertIn("ROTATED",p["decision"]["enum"])
    self.assertIn("IDEMPOTENT_REPLAY",p["decision"]["enum"])
  def test_vectors_cover_rollback_equivocation_revival(self):
    by={x["id"]:x for x in load(V)["vectors"]}
    for i in range(3,9): self.assertFalse(by[f"ETR-00{i}"]["expected"]["valid"])
    self.assertTrue(by["ETR-009"]["expected"]["valid"])
    self.assertEqual(by["ETR-009"]["expected"]["decision"],"ROTATED")
    self.assertFalse(by["ETR-011"]["expected"]["executionAuthority"])
    self.assertFalse(by["ETR-011"]["expected"]["final"])
    self.assertEqual(by["ETR-011"]["expected"]["externalEffects"],0)
  def test_readiness_non_authoritative(self):
    r=load(R)
    self.assertEqual(r["lifecycle"],"candidate")
    self.assertFalse(r["promotion_allowed"])
    self.assertFalse(r["canonical_promotion_allowed"])
    self.assertFalse(r["carries_authority"])
    self.assertEqual(r["design"]["works_schema_version"],16)
    self.assertFalse(r["design"]["executionAuthority"])
    self.assertEqual(r["design"]["externalEffects"],0)
    self.assertEqual(r["status"],"VERIFIED_MERGED_IMPLEMENTATIONS")
    self.assertEqual(r["implementation_refs"]["works_execution"],"09f09563950d7880600703b2a662e693b4a955ba")
    self.assertEqual(r["implementation_refs"]["sentinel"],"5ffccc392ec39d250e9c3aa8f2077654f275b9bf")
    self.assertTrue(r["verified"]["works_schema_v16"])
    self.assertTrue(r["verified"]["works_integrity"])
    self.assertTrue(r["verified"]["works_codeql"])
    self.assertTrue(r["verified"]["works_merged"])
    self.assertTrue(r["verified"]["sentinel_merged"])
    self.assertTrue(r["verified"]["revoked_key_revival_rejected"])
    self.assertTrue(r["verified"]["explicit_new_key_rotation_allowed"])
if __name__=="__main__":unittest.main()
