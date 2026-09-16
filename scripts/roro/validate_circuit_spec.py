#!/usr/bin/env python3
from __future__ import annotations

import json
from collections import defaultdict, deque
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REALITY = ROOT / "docs/system-reality"
MODEL_PATH = REALITY / "circuit-boundary-model.json"
VECTORS_PATH = REALITY / "circuit-spec-vectors.json"
OUT = REALITY / "circuit-validation-results.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def reachable(start: str, targets: set[str], graph: dict[str, list[str]]) -> bool:
    queue = deque([start])
    seen = {start}
    while queue:
        current = queue.popleft()
        if current in targets and current != start:
            return True
        for nxt in graph.get(current, []):
            if nxt not in seen:
                seen.add(nxt)
                queue.append(nxt)
    return False


def validate(spec: dict, model: dict, vector_id: str) -> dict:
    violations: list[dict] = []

    def add(rule_id: str, message: str):
        item = {"rule_id": rule_id, "message": message}
        if item not in violations:
            violations.append(item)

    macro = set(model["macro_families"])
    allowed = {(x["from_family"], x["to_family"]) for x in model["allowed_edges"]}
    forbidden = {(x["from_family"], x["to_family"]): x for x in model["forbidden_edges"]}

    nodes = spec.get("nodes", [])
    node_by_id: dict[str, dict] = {}
    for node in nodes:
        operator_id = node.get("operator_id")
        if operator_id in node_by_id:
            add("DUPLICATE_OPERATOR_ID", f"operator_id {operator_id!r} is duplicated")
        node_by_id[operator_id] = node
        family = node.get("family")
        if family not in macro:
            add("UNKNOWN_FAMILY", f"operator {operator_id!r} uses unknown Circuit family {family!r}")

    graph: dict[str, list[str]] = defaultdict(list)
    for edge in spec.get("edges", []):
        source = edge.get("from")
        target = edge.get("to")
        if source not in node_by_id or target not in node_by_id:
            add("UNKNOWN_OPERATOR", f"edge {source!r}->{target!r} references an unknown operator")
            continue
        graph[source].append(target)
        source_family = node_by_id[source].get("family")
        target_family = node_by_id[target].get("family")
        if source_family not in macro or target_family not in macro:
            continue
        pair = (source_family, target_family)
        if pair in forbidden:
            rule = forbidden[pair]
            add(rule["rule_id"], rule["reason"])
        elif pair not in allowed:
            add("EDGE_NOT_ALLOWED", f"Circuit edge {source_family}->{target_family} is not in the experimental allow-set")

    drives = [x for x in nodes if x.get("family") == "DRIVE"]
    covenants = {x.get("operator_id") for x in nodes if x.get("family") == "COVENANT"}
    witnesses = {x.get("operator_id") for x in nodes if x.get("family") == "WITNESS"}

    mode = spec.get("mode")
    consequential = spec.get("consequential")
    if mode == "READ_ONLY" and consequential is not False:
        add("MODE_CONSEQUENTIAL_MISMATCH", "READ_ONLY mode requires consequential=false")
    if mode in {"CONSEQUENTIAL", "IMPROVEMENT"} and consequential is not True:
        add("MODE_CONSEQUENTIAL_MISMATCH", f"{mode} mode requires consequential=true")

    if node_by_id:
        undirected: dict[str, set[str]] = {key: set() for key in node_by_id}
        for source, targets in graph.items():
            for target in targets:
                if source in undirected and target in undirected:
                    undirected[source].add(target)
                    undirected[target].add(source)
        start = next(iter(node_by_id))
        seen = {start}
        queue = deque([start])
        while queue:
            current = queue.popleft()
            for nxt in undirected[current]:
                if nxt not in seen:
                    seen.add(nxt)
                    queue.append(nxt)
        if seen != set(node_by_id):
            missing = ", ".join(sorted(set(node_by_id) - seen))
            add("DISCONNECTED_GRAPH", f"Circuit operators are not one connected composition graph; disconnected: {missing}")

    if consequential:
        if not drives:
            add("DRIVE_REQUIRED", "consequential Circuit requires at least one DRIVE operator")
        if not covenants:
            add("COVENANT_REQUIRED", "consequential Circuit requires COVENANT admission")
        if not witnesses:
            add("WITNESS_REQUIRED", "consequential Circuit requires independent WITNESS verification")

    if mode == "READ_ONLY" and drives:
        add("READ_ONLY_DRIVE_FORBIDDEN", "READ_ONLY circuits may not contain DRIVE operators")

    if spec.get("consequential"):
        for drive in drives:
            drive_id = drive.get("operator_id")
            admitted = any(reachable(covenant, {drive_id}, graph) for covenant in covenants)
            if not admitted:
                add("COVENANT_REQUIRED", f"consequential DRIVE operator {drive_id!r} is not downstream of COVENANT")
            if not reachable(drive_id, witnesses, graph):
                add("WITNESS_REQUIRED", f"consequential DRIVE operator {drive_id!r} is not followed by WITNESS")

    for drive in drives:
        drive_id = drive.get("operator_id")
        for witness_id in witnesses:
            if not reachable(drive_id, {witness_id}, graph):
                continue
            witness = node_by_id[witness_id]
            if drive.get("independence_key") == witness.get("independence_key"):
                add("VERIFIER_NOT_INDEPENDENT", f"DRIVE {drive_id!r} and WITNESS {witness_id!r} share independence_key")

    violations.sort(key=lambda x: (x["rule_id"], x["message"]))
    return {
        "schema_version": "circuit-validation/0.1",
        "vector_id": vector_id,
        "circuit_id": spec.get("circuit_id", ""),
        "composition_status": "INVALID" if violations else "VALID",
        "violations": violations,
        "execution_authorized": False,
        "authority_granted": False,
    }


def main():
    model = load(MODEL_PATH)
    vectors = load(VECTORS_PATH)["vectors"]
    results = [validate(item["spec"], model, item["vector_id"]) for item in vectors]
    payload = {
        "schema_version": "circuit-validation-results/0.1",
        "source_snapshot_generated_at": model["source_snapshot_generated_at"],
        "policy": {
            "composition_valid_is_not_execution_authorized": True,
            "composition_valid_grants_authority": False,
        },
        "results": results,
    }
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    valid = sum(x["composition_status"] == "VALID" for x in results)
    print(f"circuit validation: vectors={len(results)} valid={valid} invalid={len(results)-valid}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
