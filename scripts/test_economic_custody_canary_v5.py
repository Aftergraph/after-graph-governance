#!/usr/bin/env python3
import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OBS=ROOT/"docs/contracts/economic-graph/1.0/custody-canary.schema.json"
REC=ROOT/"docs/contracts/economic-graph/1.0/custody-recovery-canary.schema.json"
VECTORS=ROOT/"docs/platform-conformance/economic-custody-canary-v5/vectors.json"
READINESS=ROOT/"docs/frontier/economic-custody-canary-v5.json"
CAPS=ROOT/"docs/contracts/economic-graph/1.0/capabilities.json"

def load(p): return json.loads(p.read_text(encoding="utf-8"))

class CustodyCanaryV5(unittest.TestCase):
  def test_observation_is_strictly_read_only(self):
    p=load(OBS)["properties"]
    self.assertTrue(p["readOnly"]["const"])
    self.assertFalse(p["liveWriteApiCalled"]["const"])
    self.assertFalse(p["canMoveAssets"]["const"])
    self.assertFalse(p["canWithdraw"]["const"])
    self.assertFalse(p["canRecoverAssets"]["const"])
    self.assertEqual(p["externalEffects"]["const"],0)

  def test_recovery_is_dry_run_two_person_and_nonfinal(self):
    p=load(REC)["properties"]
    self.assertTrue(p["dryRun"]["const"])
    self.assertTrue(p["twoPersonApprovalBound"]["const"])
    self.assertTrue(p["authorityLeaseBound"]["const"])
    self.assertFalse(p["assetMovementRequested"]["const"])
    self.assertFalse(p["assetMovementPerformed"]["const"])
    self.assertFalse(p["final"]["const"])
    self.assertEqual(p["externalEffects"]["const"],0)

  def test_vectors_cover_replay_revocation_and_movement_denial(self):
    by={v["id"]:v for v in load(VECTORS)["vectors"]}
    self.assertEqual(by["ECC-003"]["expected"]["reason"],"CUSTODY_TWO_PERSON_APPROVAL_REQUIRED")
    self.assertEqual(by["ECC-004"]["expected"]["reason"],"CUSTODY_RECOVERY_ASSET_MOVE_PAYLOAD_FORBIDDEN")
    self.assertEqual(by["ECC-005"]["expected"]["reason"],"CUSTODY_RECOVERY_REPLAY_REJECTED")
    self.assertEqual(by["ECC-006"]["expected"]["reason"],"CUSTODY_REFERENCE_NOT_ACTIVE")
    self.assertFalse(by["ECC-007"]["expected"]["valid"])

  def test_custody_remains_experimental(self):
    r=load(READINESS)
    self.assertEqual(r["lifecycle"],"experimental")
    self.assertFalse(r["promotion_allowed"])
    self.assertFalse(r["carries_authority"])
    self.assertFalse(r["verified_design_constraints"]["live_write_api"])
    self.assertFalse(r["verified_design_constraints"]["asset_movement"])
    self.assertEqual(r["verified_design_constraints"]["external_effects"],0)
    self.assertEqual(r["status"],"VERIFIED_ZERO_EFFECT_CUSTODY_CANARY")
    self.assertEqual(len(r["implementation_refs"]),2)
    self.assertTrue(r["verified"]["read_only_custody_observation"])
    self.assertTrue(r["verified"]["two_person_recovery_dry_run"])
    self.assertTrue(r["verified"]["asset_movement_overclaim_rejection"])
    self.assertTrue(r["remaining"])
    caps={c["id"]:c for c in load(CAPS)["capabilities"]}
    self.assertEqual(caps["economic.custody"]["lifecycle"],"experimental")

if __name__=="__main__": unittest.main()
