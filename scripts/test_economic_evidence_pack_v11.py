#!/usr/bin/env python3
import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PACK=ROOT/"docs/contracts/economic-graph/1.0/evidence-pack.schema.json"
VERIFY=ROOT/"docs/contracts/economic-graph/1.0/evidence-pack-verification.schema.json"
VECTORS=ROOT/"docs/platform-conformance/economic-evidence-pack-v11/vectors.json"
READINESS=ROOT/"docs/frontier/economic-evidence-pack-v11.json"
CAPS=ROOT/"docs/contracts/economic-graph/1.0/capabilities.json"

def load(p):
    return json.loads(p.read_text(encoding="utf-8"))

class EvidencePackV11(unittest.TestCase):
    def test_pack_contract_is_immutable_zero_effect_and_non_authoritative(self):
        p=load(PACK)["properties"]
        self.assertTrue(p["immutable"]["const"])
        self.assertFalse(p["containsCredentials"]["const"])
        self.assertFalse(p["liveValueEnabled"]["const"])
        self.assertEqual(p["maxLiveValue"]["const"],0)
        self.assertFalse(p["final"]["const"])
        self.assertEqual(p["externalEffects"]["const"],0)
        self.assertEqual(p["sourceCaptures"]["minItems"],3)
        self.assertEqual(p["sourceCaptures"]["maxItems"],3)
        self.assertEqual(p["evidenceChain"]["minItems"],7)
        self.assertEqual(p["evidenceChain"]["maxItems"],7)

    def test_verification_contract_cannot_grant_authority(self):
        p=load(VERIFY)["properties"]
        self.assertFalse(p["executionAuthority"]["const"])
        self.assertFalse(p["liveValueEnabled"]["const"])
        self.assertEqual(p["maxLiveValue"]["const"],0)
        self.assertFalse(p["final"]["const"])
        self.assertFalse(p["promotionAuthority"]["const"])
        self.assertEqual(p["externalEffects"]["const"],0)

    def test_vectors_cover_tampering_secret_leakage_and_admission(self):
        by={v["id"]:v for v in load(VECTORS)["vectors"]}
        for i in range(2,7):
            self.assertFalse(by[f"EEP-00{i}"]["expected"]["valid"])
        self.assertEqual(by["EEP-007"]["expected"]["builder"],"REJECT")
        self.assertEqual(by["EEP-008"]["expected"]["builder"],"REJECT")
        self.assertFalse(by["EEP-009"]["expected"]["valid"])
        self.assertEqual(by["EEP-010"]["expected"]["decision"],"DENY")
        self.assertEqual(by["EEP-010"]["expected"]["reason"],"economic_live_settlement_not_canonical")

    def test_readiness_does_not_promote_candidate(self):
        r=load(READINESS)
        self.assertEqual(r["lifecycle"],"candidate")
        self.assertFalse(r["promotion_allowed"])
        self.assertFalse(r["canonical_promotion_allowed"])
        self.assertFalse(r["carries_authority"])
        self.assertFalse(r["readiness"]["executionAuthority"])
        self.assertFalse(r["readiness"]["liveValueEnabled"])
        self.assertEqual(r["readiness"]["maxLiveValue"],0)
        self.assertEqual(r["readiness"]["externalEffects"],0)
        self.assertEqual(r["status"],"VERIFIED_MERGED_IMPLEMENTATIONS")
        self.assertEqual(r["implementation_refs"]["runtime"],"224fe7e24e02be1f10df7f3baaa9588a0e96757c")
        self.assertEqual(r["implementation_refs"]["sentinel"],"709ff2477b8b02b9cb29d9263c18533c816eaa02")
        self.assertEqual(r["implementation_refs"]["trust_gateway"],"2742a9a656070ca2e294a98185e2424dec1e007c")
        self.assertTrue(r["verified"]["runtime_merged"])
        self.assertTrue(r["verified"]["sentinel_merged"])
        self.assertTrue(r["verified"]["trust_gateway_merged"])
        self.assertTrue(r["verified"]["evidence_pack_non_authoritative"])
        self.assertTrue(r["verified"]["max_live_value_zero"])
        caps={c["id"]:c for c in load(CAPS)["capabilities"]}
        self.assertEqual(caps["economic.live-settlement"]["lifecycle"],"candidate")

if __name__=="__main__":
    unittest.main()
