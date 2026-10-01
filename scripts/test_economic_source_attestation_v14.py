#!/usr/bin/env python3
import json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ATT=ROOT/"docs/contracts/economic-graph/1.0/source-attestation.schema.json"
ROOTS=ROOT/"docs/contracts/economic-graph/1.0/source-trust-root.schema.json"
V=ROOT/"docs/platform-conformance/economic-source-attestation-v14/vectors.json"
R=ROOT/"docs/frontier/economic-source-attestation-v14.json"
def load(p): return json.loads(p.read_text())
class SourceAttestationV14(unittest.TestCase):
  def test_attestation_is_read_only_non_authoritative(self):
    p=load(ATT)["properties"]
    self.assertEqual(p["sourceTransport"]["const"],"READ_ONLY")
    self.assertFalse(p["executionAuthority"]["const"])
    self.assertFalse(p["final"]["const"])
    self.assertFalse(p["promotionAuthority"]["const"])
    self.assertEqual(p["externalEffects"]["const"],0)
  def test_root_has_revocation_floor(self):
    p=load(ROOTS)["properties"]
    self.assertIn("REVOKED",p["status"]["enum"])
    self.assertEqual(p["minAttestationGeneration"]["minimum"],1)
  def test_vectors_fail_closed(self):
    by={x["id"]:x for x in load(V)["vectors"]}
    self.assertTrue(by["ESA-001"]["expected"]["sourceTrusted"])
    for i in range(2,10): self.assertFalse(by[f"ESA-00{i}"]["expected"]["valid"])
    self.assertEqual(by["ESA-010"]["expected"]["state"],"VERIFIED_SOURCE_TRUST_SET")
    self.assertFalse(by["ESA-010"]["expected"]["executionAuthority"])
  def test_readiness_stays_candidate(self):
    r=load(R)
    self.assertEqual(r["lifecycle"],"candidate")
    self.assertFalse(r["promotion_allowed"])
    self.assertFalse(r["canonical_promotion_allowed"])
    self.assertFalse(r["carries_authority"])
    self.assertFalse(r["design"]["executionAuthority"])
    self.assertEqual(r["design"]["externalEffects"],0)
    self.assertEqual(r["status"],"VERIFIED_MERGED_IMPLEMENTATIONS")
    self.assertEqual(r["implementation_refs"]["runtime"],"eb1d6ffa7717a4c10cff23ea8fd48a6e2bb6cb4a")
    self.assertEqual(r["implementation_refs"]["sentinel"],"def3625ce298e701e675bf3fe8598cf80ed7b731")
    self.assertEqual(r["sentinel_github_app"]["verdict"],"MERGEABLE")
    self.assertTrue(r["sentinel_github_app"]["delta_clean"])
    self.assertTrue(r["sentinel_github_app"]["all_required_checks_green"])
    self.assertEqual(r["sentinel_github_app"]["reason_codes"],[])
    self.assertTrue(r["verified"]["runtime_merged"])
    self.assertTrue(r["verified"]["sentinel_merged"])
if __name__=="__main__":unittest.main()
