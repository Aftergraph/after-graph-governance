#!/usr/bin/env python3
"""Evaluate whether declared V2.1 contract families are actually realized.

This module does not mint contract truth. It joins the canonical Governance
registry to exact-head observations produced elsewhere. Presence may promote a
contract to REALIZED; explicit conformance evidence may promote it to
CONFORMANT. COMPOSED_PROVEN is intentionally out of scope.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REGISTRY = ROOT / "docs/contracts/platform-convergence-v2-1/registry.json"

VALID_STATES = {"UNKNOWN", "DECLARED_NOT_REALIZED", "REALIZED", "CONFORMANT"}


def load_json(path: Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return data


def _observation_index(observations: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    rows = observations.get("observations", [])
    if not isinstance(rows, list):
        return {}
    out: dict[str, Mapping[str, Any]] = {}
    for row in rows:
        if isinstance(row, Mapping) and isinstance(row.get("contract"), str):
            out[row["contract"]] = row
    return out


def evaluate_registry(registry: Mapping[str, Any], observations: Mapping[str, Any]) -> dict[str, Any]:
    families = registry.get("families", [])
    if not isinstance(families, list):
        return {"decision": "UNKNOWN", "contracts": {}, "unknowns": ["registry families must be a list"]}

    observed = _observation_index(observations)
    contracts: dict[str, dict[str, Any]] = {}
    unknowns: list[str] = []
    any_missing = False

    for family in families:
        if not isinstance(family, Mapping):
            unknowns.append("registry family must be an object")
            continue
        contract = family.get("contract")
        owner = family.get("owner")
        path = family.get("path")
        if not all(isinstance(v, str) and v for v in (contract, owner, path)):
            unknowns.append(f"malformed registry family: {family!r}")
            continue

        row = observed.get(contract)
        state = "UNKNOWN"
        reason = "no exact-head observation"
        evidence: dict[str, Any] = {}
        if row is not None:
            evidence = {k: row.get(k) for k in ("head_sha", "evidence_ref") if row.get(k) is not None}
            if row.get("owner") != owner or row.get("path") != path:
                reason = "observation owner/path does not match canonical registry"
            elif not isinstance(row.get("head_sha"), str) or len(row.get("head_sha", "")) != 40:
                reason = "observation lacks a 40-character exact head sha"
            elif row.get("present") is False:
                state = "DECLARED_NOT_REALIZED"
                reason = "canonical owner path absent at observed exact head"
                any_missing = True
            elif row.get("present") is True:
                state = "REALIZED"
                reason = "canonical owner path present at observed exact head"
                conf = row.get("conformance")
                if isinstance(conf, Mapping) and conf.get("passed") is True and isinstance(conf.get("evidence_ref"), str) and conf.get("evidence_ref"):
                    state = "CONFORMANT"
                    reason = "realized with explicit conformance evidence"
                    evidence["conformance_evidence_ref"] = conf.get("evidence_ref")
            else:
                reason = "observation present flag is not boolean"

        if state == "UNKNOWN":
            unknowns.append(f"{contract}: {reason}")
        contracts[contract] = {
            "owner": owner,
            "path": path,
            "state": state,
            "reason": reason,
            "evidence": evidence,
        }

    decision = "BLOCK" if any_missing else ("UNKNOWN" if unknowns else "PASS")
    return {"decision": decision, "contracts": contracts, "unknowns": unknowns, "mode": "contract-realization"}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    parser.add_argument("--observations", type=Path, required=True)
    args = parser.parse_args(argv)
    result = evaluate_registry(load_json(args.registry), load_json(args.observations))
    print(json.dumps(result, indent=2, sort_keys=True))
    return {"PASS": 0, "BLOCK": 2, "UNKNOWN": 3}[result["decision"]]


if __name__ == "__main__":
    raise SystemExit(main())
