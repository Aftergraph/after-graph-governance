#!/usr/bin/env python3
import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
STATE=ROOT/"docs/contracts/economic-graph/1.0/source-generation-state.schema.json"
TRANSITION=ROOT/"docs/contracts/economic-graph/1.0/source-generation-transition.schema.json"
VERIFY=ROOT/"docs/contracts/economic-graph/1.0/source-generation-transition-verification.schema.json"
VECTORS=ROOT/"docs/platform-conformance/economic-source-ledger-v13/vectors.json"
READINESS=ROOT/"docs/frontier/economic-source-ledger-v13.json"
CAPS=ROOT/"docs/contracts/economic-graph/1.0/capabilities.json"

def load(p):
    return json.loads(p.read_text(encoding="utf-8"))

class SourceLedgerV13(unittest.TestCase):
    def test_state_contract_requires_monotonic_fields_and_hashes(self):
        p=load(STATE)["properties"]
        self.assertEqual(p["generation"]["minimum"],1)
        self.assertEqual(p["revision"]["minimum"],1)
        self.assertIn("version",p["cursorKind"]["enum"])
        self.assertEqual(p["stateDigest"]["pattern"],"^sha256:[a-f0-9]{64}$")

    def test_transition_is_zero_effect(self):
        p=load(TRANSITION)["properties"]
        self.assertIn("ADVANCED",p["decision"]["enum"])
        self.assertIn("IDEMPOTENT_REPLAY",p["decision"]["enum"])
        self.assertEqual(p["externalEffects"]["const"],0)

    def test_verification_cannot_grant_authority(self):
        p=load(VERIFY)["properties"]
        self.assertFalse(p["executionAuthority"]["const"])
        self.assertFalse(p["final"]["const"])
        self.assertFalse(p["promotionAuthority"]["const"])
        self.assertEqual(p["externalEffects"]["const"],0)

    def test_vectors_cover_replay_regression_equivocation_time_cursor_corruption(self):
        by={v["id"]:v for v in load(VECTORS)["vectors"]}
        self.assertEqual(by["ESL-003"]["expected"]["decision"],"IDEMPOTENT_REPLAY")
        self.assertFalse(by["ESL-003"]["expected"]["mutation"])
        self.assertEqual(by["ESL-004"]["expected"]["reason"],"generation_regression")
        self.assertEqual(by["ESL-005"]["expected"]["reason"],"generation_equivocation")
        self.assertEqual(by["ESL-006"]["expected"]["reason"],"time_regression")
        self.assertEqual(by["ESL-007"]["expected"]["reason"],"cursor_kind_change")
        self.assertEqual(by["ESL-008"]["expected"]["reason"],"state_digest_mismatch")
        self.assertEqual(by["ESL-009"]["expected"]["reason"],"concurrent_advance")
        self.assertFalse(by["ESL-010"]["expected"]["executionAuthority"])

    def test_readiness_does_not_promote_candidate(self):
        r=load(READINESS)
        self.assertEqual(r["lifecycle"],"candidate")
        self.assertFalse(r["promotion_allowed"])
        self.assertFalse(r["canonical_promotion_allowed"])
        self.assertFalse(r["carries_authority"])
        self.assertFalse(r["readiness"]["executionAuthority"])
        self.assertFalse(r["readiness"]["final"])
        self.assertFalse(r["readiness"]["promotionAuthority"])
        self.assertEqual(r["readiness"]["externalEffects"],0)
        self.assertEqual(r["status"],"VERIFIED_MERGED_IMPLEMENTATIONS")
        self.assertEqual(r["implementation_refs"]["works_execution"],"0298443864bbb2ec6b33e5806b805fecf902956f")
        self.assertEqual(r["implementation_refs"]["sentinel"],"5a6a2eb086c414de82d89ceae6756d1d7ccfdeb8")
        self.assertTrue(r["verified"]["works_schema_v15"])
        self.assertTrue(r["verified"]["works_merged"])
        self.assertTrue(r["verified"]["sentinel_merged"])
        self.assertTrue(r["verified"]["exact_replay_idempotent"])
        self.assertTrue(r["verified"]["equivocation_rejected"])
        self.assertTrue(r["verified"]["state_digest_corruption_rejected"])
        caps={c["id"]:c for c in load(CAPS)["capabilities"]}
        self.assertEqual(caps["economic.live-settlement"]["lifecycle"],"candidate")

if __name__=="__main__":
    unittest.main()
