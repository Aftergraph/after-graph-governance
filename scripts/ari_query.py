#!/usr/bin/env python3
"""Exact-subject query interface for Aftergraph Release Intelligence."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.ari_graph import CompatibilityGraph, Endpoint  # noqa: E402
from scripts.ari_model import EvidenceLevel, ResultState, evidence_meets, load_json  # noqa: E402
from scripts.ari_registry import Registry, RegistryError  # noqa: E402

SELECTOR_RE = re.compile(r"^([a-z0-9][a-z0-9-]*)@([^#]+)#([a-f0-9]{40})$")


class QueryError(ValueError):
    """Raised when an exact ARI query is invalid."""


def _parse_selector(selector: str) -> Endpoint:
    if not isinstance(selector, str):
        raise QueryError("exact component selector must be a string")
    match = SELECTOR_RE.fullmatch(selector)
    if not match:
        raise QueryError(
            "exact component selector must match component@version#40hexcommit: " + selector
        )
    return Endpoint(match.group(1), match.group(2), match.group(3))


def _evidence_for_state(edges, state: ResultState, minimum: str) -> list[str]:
    refs: set[str] = set()
    for edge in edges:
        include = False
        if state == ResultState.PASS:
            include = edge.state == "pass" and evidence_meets(edge.evidence_level, minimum)
        elif state == ResultState.FAIL:
            include = edge.state == "fail" or edge.relation == "incompatible-with"
        elif state == ResultState.STALE:
            include = edge.state == "stale"
        elif state == ResultState.N_A:
            include = edge.state == "not-applicable"
        if include:
            refs.update(ref for _, ref in edge.evidence)
    return sorted(refs)


def query_compat(registry: Registry, left_selector: str, right_selector: str, minimum: str) -> dict:
    if not isinstance(minimum, str) or minimum not in EvidenceLevel.__members__:
        raise QueryError(f"minimum evidence level must be CE0..CE5, got {minimum}")

    left = _parse_selector(left_selector)
    right = _parse_selector(right_selector)
    try:
        registry.component(left.component, left.version, left.commit)
        registry.component(right.component, right.version, right.commit)
    except RegistryError as exc:
        raise QueryError(str(exc)) from exc

    graph = CompatibilityGraph(registry.edges())
    matching = graph.between(left, right)
    state = graph.best_state(left, right, minimum)
    evidence = _evidence_for_state(matching, state, minimum)

    return {
        "schema": "aftergraph.compat-query/1",
        "state": state.value,
        "left": {
            "component": left.component,
            "version": left.version,
            "commit": left.commit,
        },
        "right": {
            "component": right.component,
            "version": right.version,
            "commit": right.commit,
        },
        "minimum_evidence": minimum,
        "matching_edges": len(matching),
        "evidence": evidence,
        "registry_digest": registry.digest,
    }


def _exit_code(state: str) -> int:
    if state in {ResultState.PASS.value, ResultState.N_A.value}:
        return 0
    if state == ResultState.FAIL.value:
        return 2
    return 3


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Query exact Aftergraph compatibility relations")
    subparsers = parser.add_subparsers(dest="command", required=True)
    compat = subparsers.add_parser("compat", help="query compatibility between exact component releases")
    compat.add_argument("registry", type=Path)
    compat.add_argument("left")
    compat.add_argument("right")
    compat.add_argument("--minimum", default="CE0")
    compat.add_argument("--format", choices=("json", "text"), default="text")
    args = parser.parse_args(argv)

    try:
        registry = Registry(load_json(args.registry))
        result = query_compat(registry, args.left, args.right, args.minimum)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(json.dumps({"schema": "aftergraph.compat-query/1", "state": "FAIL", "error": str(exc)}, sort_keys=True))
        return 2

    if args.format == "json":
        print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    else:
        print(f"state: {result['state']}")
        print(
            f"left: {result['left']['component']}@{result['left']['version']}#{result['left']['commit'][:12]}"
        )
        print(
            f"right: {result['right']['component']}@{result['right']['version']}#{result['right']['commit'][:12]}"
        )
        print(f"minimum evidence: {result['minimum_evidence']}")
        print(f"matching edges: {result['matching_edges']}")
        print(f"evidence refs: {len(result['evidence'])}")
    return _exit_code(result["state"])


if __name__ == "__main__":
    raise SystemExit(main())
