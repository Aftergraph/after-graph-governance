#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from scripts.roro.validate_circuit_spec import validate as validate_spec

REALITY = ROOT / "docs/system-reality"
MODEL_PATH = REALITY / "circuit-boundary-model.json"
VECTORS_PATH = REALITY / "circuit-compiler-vectors.json"
OUT = REALITY / "circuit-compiler-results.json"

INTENTS = {"QUERY", "REPAIR", "IMPROVE"}
EFFECTS = {"READ_ONLY", "REVERSIBLE_WRITE", "IRREVERSIBLE_WRITE"}
RISKS = {"LOW", "MEDIUM", "HIGH", "CRITICAL"}
REALITY_STATES = {"OBSERVED", "VERIFIED", "UNKNOWN", "CONFLICTING"}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def violation(rule_id: str, message: str) -> dict:
    return {"rule_id": rule_id, "message": message}

def preflight(request: dict) -> list[dict]:
    out: list[dict] = []
    mission_id = request.get("mission_id")
    intent = request.get("intent")
    effect = request.get("effect_class")
    risk = request.get("risk_class")
    reality = request.get("reality")
    if not isinstance(mission_id, str) or not mission_id:
        out.append(violation("MALFORMED_REQUEST", "mission_id must be a non-empty string"))
    if not isinstance(reality, dict):
        out.append(violation("MALFORMED_REALITY", "reality must be an object"))
        reality = {}
    state = reality.get("epistemic_status")
    fresh = reality.get("fresh")
    if not isinstance(fresh, bool):
        out.append(violation("MALFORMED_REALITY", "reality.fresh must be boolean"))

    if intent not in INTENTS:
        out.append(violation("UNKNOWN_INTENT", f"unsupported mission intent {intent!r}"))
    if effect not in EFFECTS:
        out.append(violation("UNKNOWN_EFFECT_CLASS", f"unsupported effect class {effect!r}"))
    if risk not in RISKS:
        out.append(violation("UNKNOWN_RISK_CLASS", f"unsupported risk class {risk!r}"))
    if state not in REALITY_STATES:
        out.append(violation("UNKNOWN_REALITY_STATE", f"unsupported reality state {state!r}"))
    elif state == "UNKNOWN":
        out.append(violation("REALITY_UNKNOWN", "mission reality is unknown"))
    elif state == "CONFLICTING":
        out.append(violation("REALITY_CONFLICTING", "mission reality contains unresolved conflict"))

    consequential = effect in {"REVERSIBLE_WRITE", "IRREVERSIBLE_WRITE"}
    if consequential and fresh is False:
        out.append(violation("STALE_REALITY", "consequential compilation requires fresh reality"))
    if consequential and risk in {"HIGH", "CRITICAL"} and state != "VERIFIED":
        out.append(violation("VERIFIED_REALITY_REQUIRED", "high-risk consequential compilation requires VERIFIED reality"))
    if intent == "QUERY" and effect in EFFECTS and effect != "READ_ONLY":
        out.append(violation("INTENT_EFFECT_MISMATCH", "QUERY intent must be READ_ONLY"))
    if intent in {"REPAIR", "IMPROVE"} and effect == "READ_ONLY":
        out.append(violation("INTENT_EFFECT_MISMATCH", f"{intent} intent requires a write effect class"))
    return sorted(out, key=lambda x: (x["rule_id"], x["message"]))

def node(operator_id: str, family: str, independence_key: str) -> dict:
    return {"operator_id": operator_id, "family": family, "independence_key": independence_key}


def build_spec(request: dict) -> dict:
    mission_id = request["mission_id"]
    intent = request["intent"]
    if intent == "QUERY":
        nodes = [node("sense", "SIGHTLINE", "observe"), node("think", "HELM", "cognition")]
        mode = "READ_ONLY"
    elif intent == "REPAIR":
        nodes = [
            node("sense", "SIGHTLINE", "observe"),
            node("think", "HELM", "cognition"),
            node("admit", "COVENANT", "authority"),
            node("execute", "DRIVE", "execution"),
            node("verify", "WITNESS", "verification"),
            node("reobserve", "SIGHTLINE", "reobserve"),
        ]
        mode = "CONSEQUENTIAL"
    else:
        nodes = [
            node("sense", "SIGHTLINE", "observe"),
            node("think", "HELM", "cognition"),
            node("learn", "REFINERY", "experiment"),
            node("admit", "COVENANT", "authority"),
            node("execute", "DRIVE", "shadow-execution"),
            node("verify", "WITNESS", "verification"),
        ]
        mode = "IMPROVEMENT"
    edges = [{"from": a["operator_id"], "to": b["operator_id"]} for a, b in zip(nodes, nodes[1:])]
    return {
        "schema_version": "circuit-spec/0.1",
        "circuit_id": f"compiled-{mission_id}",
        "mode": mode,
        "consequential": request["effect_class"] != "READ_ONLY",
        "nodes": nodes,
        "edges": edges,
    }

def compile_request(request: dict, model: dict, vector_id: str) -> dict:
    violations = preflight(request)
    if violations:
        return {
            "schema_version": "circuit-compile-result/0.1",
            "vector_id": vector_id,
            "mission_id": request.get("mission_id", "unknown-mission"),
            "compile_status": "REFUSED",
            "composition_status": "NOT_RUN",
            "violations": violations,
            "circuit_spec": None,
            "execution_authorized": False,
            "authority_granted": False,
        }

    spec = build_spec(request)
    validation = validate_spec(spec, model, vector_id)
    if validation["composition_status"] != "VALID":
        return {
            "schema_version": "circuit-compile-result/0.1",
            "vector_id": vector_id,
            "mission_id": request["mission_id"],
            "compile_status": "REFUSED",
            "composition_status": "INVALID",
            "violations": validation["violations"],
            "circuit_spec": None,
            "execution_authorized": False,
            "authority_granted": False,
        }
    return {
        "schema_version": "circuit-compile-result/0.1",
        "vector_id": vector_id,
        "mission_id": request["mission_id"],
        "compile_status": "COMPILED",
        "composition_status": "VALID",
        "violations": [],
        "circuit_spec": spec,
        "execution_authorized": False,
        "authority_granted": False,
    }

def main() -> int:
    model = load(MODEL_PATH)
    vectors = load(VECTORS_PATH)["vectors"]
    results = [compile_request(item["request"], model, item["vector_id"]) for item in vectors]
    payload = {
        "schema_version": "circuit-compiler-results/0.1",
        "source_snapshot_generated_at": model["source_snapshot_generated_at"],
        "policy": {
            "compiled_is_not_execution_authorized": True,
            "compiled_grants_authority": False,
            "compiler_performs_runtime_calls": False,
            "compiler_owns_durable_state": False,
        },
        "results": results,
    }
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    compiled = sum(x["compile_status"] == "COMPILED" for x in results)
    print(f"circuit compiler: vectors={len(results)} compiled={compiled} refused={len(results)-compiled}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
