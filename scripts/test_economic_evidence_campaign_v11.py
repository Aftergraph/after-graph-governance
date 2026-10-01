#!/usr/bin/env python3
import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SCHEMA=ROOT/"docs/contracts/economic-graph/1.0/evidence-campaign.schema.json"
VECTORS=ROOT/"docs/platform-conformance/economic-evidence-campaign-v11/vectors.json"
READINESS=ROOT/"docs/frontier/economic-evidence-campaign-v11.json"
LEGAL=ROOT/"docs/contracts/economic-graph/1.0/legal-records.schema.json"
CAPS=ROOT/"docs/contracts/economic-graph/1.0/capabilities.json"

def load(path):
    return json.loads(path.read_text(encoding="utf-8"))

class EvidenceCampaignV11(unittest.TestCase):
    def test_pack_schema_is_strictly_non_authoritative(self):
        p=load(SCHEMA)["properties"]
        self.assertFalse(p["executionAuthority"]["const"])
        self.assertFalse(p["liveValueEnabled"]["const"])
        self.assertEqual(p["externalEffects"]["const"],0)
        self.assertFalse(p["final"]["const"])
        self.assertEqual(p["snapshots"]["minItems"],3)
        self.assertEqual(p["snapshots"]["maxItems"],3)

    def test_snapshot_contract_requires_generation_and_hash_projection(self):
        p=load(SCHEMA)["$defs"]["snapshot"]["properties"]
        self.assertEqual(p["generation"]["minimum"],1)
        self.assertEqual(p["externalEffects"]["const"],0)
        self.assertFalse(p["final"]["const"])
        self.assertEqual(p["evidenceHash"]["pattern"],"^sha256:[a-f0-9]{64}$")
        self.assertEqual(set(p["sourceClass"]["enum"]),{"registry","custody","representation"})

    def test_vectors_cover_integrity_source_separation_and_replay(self):
        by={v["id"]:v for v in load(VECTORS)["vectors"]}
        self.assertEqual(by["ECP-001"]["expected"]["verification"],"VERIFIED_EVIDENCE_CAMPAIGN")
        self.assertFalse(by["ECP-001"]["expected"]["executionAuthority"])
        self.assertEqual(by["ECP-001"]["expected"]["maxLiveValue"],0)
        for i in range(2,11):
            self.assertEqual(by[f"ECP-{i:03d}"]["expected"]["verification"],"EVIDENCE_CAMPAIGN_INVALID")

    def test_v11_outputs_match_registered_v7_source_record_schemas(self):
        legal=load(LEGAL)
        registered={
            variant["properties"]["schema"]["const"]
            for variant in legal["oneOf"]
        }
        campaign=set(load(SCHEMA)["$defs"]["snapshot"]["properties"]["recordSchema"]["enum"])
        self.assertEqual(campaign,registered)

    def test_readiness_does_not_promote_candidate(self):
        r=load(READINESS)
        self.assertEqual(r["lifecycle"],"candidate")
        self.assertFalse(r["runtime_ref"]["merge_required"])
        self.assertFalse(r["sentinel_ref"]["merge_required"])
        self.assertEqual(r["runtime_ref"]["merge_sha"],"ba399d2e89a54b4237faf0458c583ef1fde92654")
        self.assertEqual(r["sentinel_ref"]["merge_sha"],"0b105a8a20019048069b517081fb120399107fde")
        self.assertEqual(r["status"],"VERIFIED_MERGED_IMPLEMENTATIONS")
        self.assertTrue(r["verified"]["sentinel_merged"])
        self.assertTrue(r["verified"]["runtime_ci"])
        self.assertTrue(r["verified"]["runtime_sentinel_gate"])
        self.assertTrue(r["verified"]["runtime_sentinel_verdict_mergeable"])
        self.assertTrue(r["verified"]["runtime_merged"])
        self.assertEqual(r["sentinel_github_app_review"]["verdict"],"MERGEABLE")
        self.assertTrue(r["sentinel_github_app_review"]["delta_clean"])
        self.assertTrue(r["sentinel_github_app_review"]["all_required_checks_green"])
        self.assertEqual(r["sentinel_github_app_review"]["reason_codes"],[])
        self.assertFalse(r["promotion_allowed"])
        self.assertFalse(r["canonical_promotion_allowed"])
        self.assertFalse(r["carries_authority"])
        self.assertFalse(r["verified_design_constraints"]["execution_authority"])
        self.assertFalse(r["verified_design_constraints"]["live_value_enabled"])
        self.assertEqual(r["verified_design_constraints"]["max_live_value"],0)
        self.assertFalse(r["verified_design_constraints"]["final"])
        self.assertFalse(r["verified_design_constraints"]["promotion_authority"])
        self.assertEqual(r["verified_design_constraints"]["external_effects"],0)
        self.assertTrue(r["remaining"])
        caps={c["id"]:c for c in load(CAPS)["capabilities"]}
        self.assertEqual(caps["economic.live-settlement"]["lifecycle"],"candidate")

if __name__=="__main__":
    unittest.main()
