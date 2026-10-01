#!/usr/bin/env python3
import json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
AUTH=ROOT/"docs/contracts/economic-graph/1.0/trust-root-rotation-authorization.schema.json"
V=ROOT/"docs/platform-conformance/economic-trust-root-authorization-v16/vectors.json"
R=ROOT/"docs/frontier/economic-trust-root-authorization-v16.json"
def load(p): return json.loads(p.read_text())
class TrustRootAuthorizationV16(unittest.TestCase):
  def test_authorization_never_grants_economic_authority(self):
    p=load(AUTH)["properties"]
    self.assertFalse(p["executionAuthority"]["const"])
    self.assertFalse(p["liveValueEnabled"]["const"])
    self.assertFalse(p["final"]["const"])
    self.assertFalse(p["promotionAuthority"]["const"])
    self.assertEqual(p["externalEffects"]["const"],0)
  def test_payload_requires_real_human_and_authority_bindings(self):
    p=load(AUTH)["properties"]["payload"]["properties"]
    self.assertEqual(p["approvalProofIds"]["minItems"],2)
    self.assertTrue(p["approvalProofIds"]["uniqueItems"])
    self.assertEqual(p["priorGeneration"]["minimum"],1)
    self.assertEqual(p["newGeneration"]["minimum"],2)
  def test_vectors_fail_closed(self):
    by={x["id"]:x for x in load(V)["vectors"]}
    self.assertTrue(by["ETA-001"]["expected"]["authorized"])
    for i in range(2,8): self.assertFalse(by[f"ETA-00{i}"]["expected"]["authorized"])
    self.assertEqual(by["ETA-008"]["expected"]["verification"],"INVALID")
    self.assertEqual(by["ETA-009"]["expected"]["decision"],"AUTHORIZATION_REQUIRED")
    self.assertEqual(by["ETA-010"]["expected"]["verification"],"VERIFIED_AUTHORIZED_TRUST_ROOT_ROTATION")
    self.assertFalse(by["ETA-010"]["expected"]["executionAuthority"])
  def test_readiness_remains_candidate_and_non_authoritative(self):
    r=load(R)
    self.assertEqual(r["lifecycle"],"candidate")
    self.assertFalse(r["promotion_allowed"])
    self.assertFalse(r["canonical_promotion_allowed"])
    self.assertFalse(r["carries_authority"])
    self.assertTrue(r["design"]["legacy_rotation_path_fails_closed"])
    self.assertFalse(r["design"]["executionAuthority"])
    self.assertFalse(r["design"]["liveValueEnabled"])
    self.assertEqual(r["design"]["externalEffects"],0)
    self.assertEqual(r["status"],"VERIFIED_MERGED_IMPLEMENTATIONS")
    self.assertEqual(r["implementation_refs"]["trust_gateway"],"9d3eea888b710d08847b5737b1eebf668c9da4d7")
    self.assertEqual(r["implementation_refs"]["works_execution"],"a968911f3e2a6efb5fd5d88b88a5c398b7ba393f")
    self.assertEqual(r["implementation_refs"]["sentinel"],"99129ce1dda95ddcfc94904bed7ebf5e62e890bb")
    self.assertTrue(r["verified"]["trust_gateway_cross_repo_gate"])
    self.assertTrue(r["verified"]["works_merged"])
    self.assertTrue(r["verified"]["sentinel_merged"])
    self.assertTrue(r["verified"]["caller_ids_not_authoritative"])
    self.assertTrue(r["verified"]["legacy_rotation_path_fails_closed"])
if __name__=="__main__":unittest.main()
