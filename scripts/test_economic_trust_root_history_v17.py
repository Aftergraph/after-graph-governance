#!/usr/bin/env python3
import json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
S=ROOT/"docs/contracts/economic-graph/1.0/source-trust-root-event.schema.json"
V=ROOT/"docs/platform-conformance/economic-trust-root-history-v17/vectors.json"
R=ROOT/"docs/frontier/economic-trust-root-history-v17.json"
def load(p): return json.loads(p.read_text())
class TrustRootHistoryV17(unittest.TestCase):
  def test_event_contract_hash_bound(self):
    p=load(S)["properties"]
    self.assertEqual(p["sequence"]["minimum"],1)
    self.assertIn("ROTATED",p["decision"]["enum"])
    self.assertEqual(p["previousEventHash"]["pattern"],"^sha256:[a-f0-9]{64}$")
    self.assertEqual(p["eventHash"]["pattern"],"^sha256:[a-f0-9]{64}$")
  def test_vectors_detect_history_tampering(self):
    by={x["id"]:x for x in load(V)["vectors"]}
    self.assertTrue(by["ETH-001"]["expected"]["valid"])
    self.assertFalse(by["ETH-002"]["expected"]["newHistoryEvent"])
    for i in range(3,10): self.assertFalse(by[f"ETH-00{i}"]["expected"]["valid"])
    self.assertFalse(by["ETH-010"]["expected"]["stateMutation"])
    self.assertFalse(by["ETH-010"]["expected"]["historyAppend"])
    self.assertFalse(by["ETH-011"]["expected"]["executionAuthority"])
    self.assertEqual(by["ETH-011"]["expected"]["externalEffects"],0)
  def test_readiness_non_authoritative(self):
    r=load(R)
    self.assertEqual(r["lifecycle"],"candidate")
    self.assertEqual(r["design"]["works_schema_version"],17)
    self.assertTrue(r["design"]["same_transaction_with_current_state"])
    self.assertTrue(r["design"]["rotation_authorization_digest_bound"])
    self.assertFalse(r["design"]["executionAuthority"])
    self.assertFalse(r["promotion_allowed"])
if __name__=="__main__":unittest.main()
