#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "docs" / "contracts" / "tool-fabric" / "0.1.json"
EXAMPLE = ROOT / "docs" / "contracts" / "tool-fabric" / "0.1.example.json"

doc = json.loads(CONTRACT.read_text(encoding="utf-8"))
example = json.loads(EXAMPLE.read_text(encoding="utf-8"))

assert doc["properties"]["contract"]["const"] == "tool-fabric/0.1"
assert doc["properties"]["status"]["const"] == "experimental"
assert example["contract"] == "tool-fabric/0.1"
assert example["status"] == "experimental"

required_invariants = {
    "tool discovery and routing never grant authority",
    "runtime target binding may not widen admitted capability or authority",
    "unknown or unclassified consequential effects fail closed",
    "execution success does not establish verified outcome",
}
assert required_invariants.issubset(set(example["invariants"]))

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

print("ToolFabric governance contract: PASS")
