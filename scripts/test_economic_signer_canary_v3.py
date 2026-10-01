#!/usr/bin/env python3
import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SCHEMA=ROOT/"docs/contracts/economic-graph/1.0/signer-canary-receipt.schema.json"
VECTORS=ROOT/"docs/platform-conformance/economic-signer-canary-v3/vectors.json"
READINESS=ROOT/"docs/frontier/economic-signer-canary-v3.json"
CAPS=ROOT/"docs/contracts/economic-graph/1.0/capabilities.json"

def load(p): return json.loads(p.read_text(encoding="utf-8"))

class SignerCanaryV3(unittest.TestCase):
  def test_receipt_schema_forbids_effect_and_key_exposure(self):
    p=load(SCHEMA)["properties"]
    self.assertFalse(p["signingMaterialExposed"]["const"])
    self.assertFalse(p["transactionPayloadSigned"]["const"])
    self.assertFalse(p["canBroadcast"]["const"])
    self.assertEqual(p["externalEffects"]["const"],0)
    self.assertEqual(p["algorithm"]["const"],"Ed25519")

  def test_vectors_falsify_overclaims(self):
    by={v["id"]:v for v in load(VECTORS)["vectors"]}
    self.assertTrue(by["ESC-001"]["expected"]["cryptographicallyVerified"])
    for i in range(2,8):
      self.assertFalse(by[f"ESC-00{i}"]["expected"]["valid"])

  def test_readiness_does_not_promote_signing(self):
    r=load(READINESS)
    self.assertEqual(r["lifecycle"],"experimental")
    self.assertFalse(r["promotion_allowed"])
    self.assertFalse(r["carries_authority"])
    self.assertEqual(r["requirements"]["broadcast"],"disabled")
    self.assertEqual(r["requirements"]["external_effects"],0)
    self.assertEqual(r["status"],"VERIFIED_NON_ECONOMIC_CANARY")
    self.assertEqual(len(r["implementation_refs"]),2)
    self.assertTrue(r["verified"]["independent_signature_verification"])
    self.assertTrue(r["verified"]["tamper_rejection"])
    self.assertTrue(r["verified"]["expiry_rejection"])
    self.assertTrue(r["remaining"])
    caps={c["id"]:c for c in load(CAPS)["capabilities"]}
    self.assertEqual(caps["economic.transaction-signing"]["lifecycle"],"experimental")

if __name__=="__main__": unittest.main()
