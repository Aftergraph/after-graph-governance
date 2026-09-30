#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOPOLOGY = ROOT / "docs" / "platform-topology" / "2.0.json"
CONTRACT = ROOT / "docs" / "contracts" / "tool-fabric" / "0.1.json"
EXAMPLE = ROOT / "docs" / "contracts" / "tool-fabric" / "0.1.example.json"
DIGEST_VECTOR = ROOT / "docs" / "contracts" / "tool-fabric" / "registry-digest-vector-0.1.json"

doc = json.loads(CONTRACT.read_text(encoding="utf-8"))
example = json.loads(EXAMPLE.read_text(encoding="utf-8"))
vector = json.loads(DIGEST_VECTOR.read_text(encoding="utf-8"))
topology = json.loads(TOPOLOGY.read_text(encoding="utf-8"))

assert doc["properties"]["contract"]["const"] == "tool-fabric/0.1"
assert doc["properties"]["status"]["const"] == "experimental"
assert example["contract"] == "tool-fabric/0.1"
assert example["status"] == "experimental"

required_invariants = {
    "tool discovery and routing never grant authority",
    "skills and models never grant execution authority by installation or selection",
    "tool descriptors contain credential references only and never plaintext credential material",
    "plaintext credentials may materialize only inside the Trust Gateway governed provider boundary after admission and mutable-state revalidation",
    "runtime target binding may not widen admitted capability or authority",
    "unknown or unclassified consequential effects fail closed",
    "automatic failover may not replay a non-idempotent effect after execution may have started",
    "execution success does not establish verified outcome",
    "ToolExecutionReceipt integrity is independently verifiable and must state credentialMaterialExposed=false",
    "experience and observability surfaces may project ToolFabric state but may not become authority or execution truth",
    "semantic capability aliases must be explicitly registered with provenance; fuzzy or embedding similarity cannot grant or widen a capability",
    "registry sources exceeding their configured freshness TTL are quarantined from active routing until a new verified snapshot is ingested",
    "health probes must be passive or read-only and may not invoke consequential tool effects",
    "circuit breaker state influences routing eligibility only and never grants, revokes or widens authority",
}
assert required_invariants.issubset(set(example["invariants"]))
assert len(example["invariants"]) == len(set(example["invariants"]))

schema_invariants = doc["properties"]["invariants"]
encoded = {
    row["contains"]["const"]
    for row in schema_invariants.get("allOf", [])
    if isinstance(row, dict)
    and isinstance(row.get("contains"), dict)
    and isinstance(row["contains"].get("const"), str)
}
assert required_invariants.issubset(encoded)
assert schema_invariants.get("uniqueItems") is True

owners = example["owners"]
assert owners["registration"] == "Aftergraph/after-graph-governance"
assert owners["routing"] == "Aftergraph/core"
assert owners["admission"] == "Aftergraph/trust-gateway"
assert owners["runtime_binding"] == "Aftergraph/runtime"
assert owners["durable_execution"] == "Aftergraph/works-execution"
assert owners["verification"] == "Aftergraph/sentinel"

schemas = example["schemas"]
assert schemas["tool"] == "aftergraph.tool/v1"
assert schemas["resolution"] == "aftergraph.tool-resolution/v1"
assert schemas["receipt"] == "aftergraph.tool-receipt/v1"
assert schemas["telemetry"] == "aftergraph.tool-observation/v1"

assert len(example["participants"]) == len(set(example["participants"]))
assert all(p.startswith("Aftergraph/") for p in example["participants"])
topology_names = {f"Aftergraph/{row['name']}" for row in topology["repositories"]}
assert example["owners"]["routing"] in topology_names
assert all(p in topology_names for p in example["participants"])

import hashlib

canonical = json.dumps(vector["payload"], sort_keys=True, separators=(",", ":"), ensure_ascii=False)
assert canonical == vector["canonical_json"]
assert hashlib.sha256(canonical.encode("utf-8")).hexdigest() == vector["sha256"]

print("ToolFabric governance contract: PASS")
