#!/usr/bin/env python3
import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CORR=ROOT/"docs/contracts/economic-graph/1.0/same-transaction-correlation.schema.json"
RECEIPT=ROOT/"docs/contracts/economic-graph/1.0/rail-settlement-receipt.schema.json"
VECTORS=ROOT/"docs/platform-conformance/economic-correlation-v6/vectors.json"
READINESS=ROOT/"docs/frontier/economic-correlation-v6.json"
CAPS=ROOT/"docs/contracts/economic-graph/1.0/capabilities.json"

def load(p): return json.loads(p.read_text(encoding="utf-8"))

class EconomicCorrelationV6(unittest.TestCase):
  def test_correlation_contract_never_claims_finality(self):
    p=load(CORR)["properties"]
    self.assertFalse(p["final"]["const"])
    self.assertEqual(p["externalEffects"]["const"],0)
    self.assertIn("CORRELATED",p["state"]["enum"])
    self.assertIn("UNCERTAIN",p["state"]["enum"])

  def test_rail_receipt_is_hash_bound_and_zero_effect(self):
    p=load(RECEIPT)["properties"]
    self.assertEqual(p["schema"]["const"],"aftergraph.rail-settlement-receipt/v1")
    self.assertEqual(p["externalEffects"]["const"],0)
    self.assertFalse(p["final"]["const"])
    self.assertEqual(p["obligationHash"]["pattern"],"^sha256:[a-f0-9]{64}$")
    self.assertEqual(p["legalBindingHash"]["pattern"],"^sha256:[a-f0-9]{64}$")
    self.assertEqual(p["sourceEvidenceHash"]["pattern"],"^sha256:[a-f0-9]{64}$")

  def test_vectors_force_reconciliation_on_disagreement(self):
    by={v["id"]:v for v in load(VECTORS)["vectors"]}
    for i in range(2,8):
      self.assertTrue(by[f"ECT-00{i}"]["expected"]["reconciliationRequired"])
    self.assertEqual(by["ECT-008"]["expected"]["verification"],"RECONCILIATION_REQUIRED")
    self.assertFalse(by["ECT-008"]["expected"]["sameEconomicTransactionVerified"])
    self.assertFalse(by["ECT-009"]["expected"]["valid"])

  def test_readiness_does_not_promote_live_settlement(self):
    r=load(READINESS)
    self.assertEqual(r["lifecycle"],"candidate")
    self.assertFalse(r["promotion_allowed"])
    self.assertFalse(r["canonical_promotion_allowed"])
    self.assertFalse(r["carries_authority"])
    self.assertFalse(r["verified_design_constraints"]["real_world_finality"])
    self.assertEqual(r["verified_design_constraints"]["external_effects"],0)
    self.assertEqual(r["status"],"VERIFIED_PENDING_WORKS_MERGE")
    self.assertEqual(r["implementation_refs"]["works_execution_pending"]["pr"],187)
    self.assertTrue(r["implementation_refs"]["works_execution_pending"]["merge_required"])
    self.assertTrue(r["verified"]["works_go_tests"])
    self.assertTrue(r["verified"]["works_codeql"])
    self.assertTrue(r["verified"]["sentinel_independent_verifier"])
    self.assertTrue(r["remaining"])
    caps={c["id"]:c for c in load(CAPS)["capabilities"]}
    self.assertEqual(caps["economic.live-settlement"]["lifecycle"],"candidate")
    self.assertEqual(caps["economic.transaction-signing"]["lifecycle"],"experimental")
    self.assertEqual(caps["economic.custody"]["lifecycle"],"experimental")

if __name__=="__main__": unittest.main()
