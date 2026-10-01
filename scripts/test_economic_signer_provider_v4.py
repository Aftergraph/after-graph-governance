#!/usr/bin/env python3
import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PROVIDER=ROOT/"docs/contracts/economic-graph/1.0/signer-provider.schema.json"
LIFECYCLE=ROOT/"docs/contracts/economic-graph/1.0/signer-key-lifecycle.schema.json"
VECTORS=ROOT/"docs/platform-conformance/economic-signer-provider-v4/vectors.json"
READINESS=ROOT/"docs/frontier/economic-signer-provider-v4.json"
CAPS=ROOT/"docs/contracts/economic-graph/1.0/capabilities.json"

def load(p): return json.loads(p.read_text(encoding="utf-8"))

class SignerProviderV4(unittest.TestCase):
  def test_provider_schema_stays_opaque_and_zero_effect(self):
    p=load(PROVIDER)["properties"]
    self.assertFalse(p["signingMaterialExposed"]["const"])
    self.assertFalse(p["transactionPayloadSigned"]["const"])
    self.assertFalse(p["canBroadcast"]["const"])
    self.assertEqual(p["externalEffects"]["const"],0)
    self.assertEqual(p["keyStateAtSigning"]["const"],"ACTIVE")

  def test_key_lifecycle_contract_forbids_private_key_transfer(self):
    schema=load(LIFECYCLE)
    rotation=schema["oneOf"][0]["properties"]
    self.assertFalse(rotation["privateKeyMaterialTransferred"]["const"])
    self.assertEqual(rotation["oldState"]["const"],"RETIRED")
    self.assertEqual(rotation["newState"]["const"],"ACTIVE")
    self.assertEqual(rotation["externalEffects"]["const"],0)

  def test_vectors_cover_replay_rotation_revocation(self):
    by={v["id"]:v for v in load(VECTORS)["vectors"]}
    self.assertEqual(by["ESP-002"]["expected"]["reason"],"SIGNER_PROVIDER_REPLAY_REJECTED")
    self.assertEqual(by["ESP-004"]["expected"]["reason"],"SIGNER_PROVIDER_KEY_NOT_ACTIVE")
    self.assertEqual(by["ESP-005"]["expected"]["reason"],"SIGNER_PROVIDER_KEY_NOT_ACTIVE")
    self.assertFalse(by["ESP-006"]["expected"]["valid"])
    self.assertFalse(by["ESP-007"]["expected"]["valid"])
    self.assertEqual(by["ESP-008"]["expected"]["reason"],"SIGNER_PROVIDER_EFFECT_BOUNDARY_VIOLATION")

  def test_readiness_remains_experimental(self):
    r=load(READINESS)
    self.assertEqual(r["lifecycle"],"experimental")
    self.assertFalse(r["promotion_allowed"])
    self.assertFalse(r["carries_authority"])
    self.assertFalse(r["verified_design_constraints"]["private_key_export_api"])
    self.assertFalse(r["verified_design_constraints"]["broadcast"])
    self.assertEqual(r["verified_design_constraints"]["external_effects"],0)
    self.assertTrue(r["remaining"])
    caps={c["id"]:c for c in load(CAPS)["capabilities"]}
    self.assertEqual(caps["economic.transaction-signing"]["lifecycle"],"experimental")

if __name__=="__main__": unittest.main()
