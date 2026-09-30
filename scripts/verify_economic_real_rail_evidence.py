#!/usr/bin/env python3
import json
import sys
from pathlib import Path

def fail(msg):
    print("FAIL:", msg, file=sys.stderr)
    raise SystemExit(1)

def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))

def verify_one(e):
    if e.get("schema") != "aftergraph.real-rail-evidence/v1":
        fail("bad schema")
    if e.get("externalEffects") != 0:
        fail("externalEffects must be 0")
    rail=e.get("rail")
    if rail=="evm":
        if e.get("observation")!="CONSENSUS_FINALIZED":
            fail("EVM observation must be CONSENSUS_FINALIZED")
        if not all(e.get(k) for k in ("transactionHash","receiptBlockNumber","finalizedHeadNumber")):
            fail("EVM finalized evidence incomplete")
        if int(e["receiptBlockNumber"],16) > int(e["finalizedHeadNumber"],16):
            fail("EVM receipt exceeds finalized head")
    elif rail=="canton":
        if e.get("observation")!="PARTICIPANT_LEDGER_OBSERVED":
            fail("Canton observation class invalid")
        if e.get("legalFinalityClaimed") is not False:
            fail("Canton evidence may not claim legal finality")
        if "ledgerEnd" not in e or "version" not in e:
            fail("Canton evidence incomplete")
    else:
        fail("unsupported rail")

def verify_pair(evm, canton):
    verify_one(evm); verify_one(canton)
    if {evm["rail"],canton["rail"]}!={"evm","canton"}:
        fail("two distinct rail families required")
    return {
      "schema":"economic-real-rail-verification/1.0",
      "state":"CORROBORATED_READ_ONLY_EVIDENCE",
      "final":False,
      "promotionAuthority":False,
      "rails":["evm","canton"]
    }

if __name__=="__main__":
    if len(sys.argv)!=3:
        fail("usage: verify_economic_real_rail_evidence.py evm.json canton.json")
    result=verify_pair(load(sys.argv[1]),load(sys.argv[2]))
    print(json.dumps(result,sort_keys=True))
