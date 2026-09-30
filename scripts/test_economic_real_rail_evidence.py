#!/usr/bin/env python3
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
MOD_PATH=ROOT/"scripts"/"verify_economic_real_rail_evidence.py"
spec=importlib.util.spec_from_file_location("railverify",MOD_PATH)
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)

EVM={
 "schema":"aftergraph.real-rail-evidence/v1","rail":"evm","source":"fixture",
 "observation":"CONSENSUS_FINALIZED","externalEffects":0,"capturedAt":"2026-10-01T00:00:00Z",
 "transactionHash":"0x"+"a"*64,"receiptBlockNumber":"0x10","finalizedHeadNumber":"0x12"
}
CANTON={
 "schema":"aftergraph.real-rail-evidence/v1","rail":"canton","source":"fixture",
 "observation":"PARTICIPANT_LEDGER_OBSERVED","externalEffects":0,"capturedAt":"2026-10-01T00:00:00Z",
 "participantApi":"JSON Ledger API v2","version":{"version":"3.5.17"},"ledgerEnd":{"offset":0},
 "legalFinalityClaimed":False
}

class TestRailEvidence(unittest.TestCase):
  def test_pair_corrobates_without_finality(self):
    out=m.verify_pair(dict(EVM),dict(CANTON))
    self.assertEqual(out["state"],"CORROBORATED_READ_ONLY_EVIDENCE")
    self.assertFalse(out["final"])
    self.assertFalse(out["promotionAuthority"])

  def test_evm_above_finalized_rejects(self):
    bad=dict(EVM); bad["receiptBlockNumber"]="0x20"
    with self.assertRaises(SystemExit): m.verify_one(bad)

  def test_canton_legal_finality_claim_rejects(self):
    bad=dict(CANTON); bad["legalFinalityClaimed"]=True
    with self.assertRaises(SystemExit): m.verify_one(bad)

if __name__=="__main__":
  unittest.main()
