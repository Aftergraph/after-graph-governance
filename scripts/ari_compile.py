#!/usr/bin/env python3
"""Deterministic APC compiler for Aftergraph Release Intelligence."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.ari_graph import CompatibilityGraph, Endpoint  # noqa: E402
from scripts.ari_model import ResultState, load_json, validate_component  # noqa: E402


@dataclass(slots=True)
class CompileResult:
    state: ResultState
    component: str
    version: str
    profile_results: dict[str, ResultState] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)
    unknowns: list[str] = field(default_factory=list)
    evidence_refs: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "schema": "aftergraph.apc-result/1",
            "state": self.state.value,
            "component": self.component,
            "version": self.version,
            "profiles": {name: state.value for name, state in self.profile_results.items()},
            "errors": list(self.errors),
            "unknowns": list(self.unknowns),
            "evidence": list(self.evidence_refs),
        }


def _aggregate(states: Iterable[ResultState]) -> ResultState:
    values = list(states)
    if not values:
        return ResultState.N_A
    for state in (ResultState.FAIL, ResultState.STALE, ResultState.UNKNOWN):
        if state in values:
            return state
    if all(state == ResultState.N_A for state in values):
        return ResultState.N_A
    return ResultState.PASS


def _edge_label(target: Endpoint) -> str:
    return f"{target.component}@{target.version}#{target.commit[:12]}"


def compile_component(manifest: dict, apc: dict, edge_documents: Iterable[dict]) -> CompileResult:
    identity = manifest.get("identity") if isinstance(manifest, dict) else {}
    release = manifest.get("release") if isinstance(manifest, dict) else {}
    component = identity.get("component", "<unknown>") if isinstance(identity, dict) else "<unknown>"
    version = release.get("version", "<unknown>") if isinstance(release, dict) else "<unknown>"

    errors = validate_component(manifest)
    if apc.get("schema") != "aftergraph.apc/1":
        errors.append("APC registry schema must be aftergraph.apc/1")
    if apc.get("level") != "APC-1":
        errors.append("APC registry level must be APC-1")

    if errors:
        return CompileResult(ResultState.FAIL, component, version, errors=errors)

    compatibility = manifest["compatibility"]
    profiles: list[str] = compatibility["profiles"]
    if not profiles:
        return CompileResult(ResultState.N_A, component, version)

    profile_requirements = apc.get("profile_requirements")
    if not isinstance(profile_requirements, dict):
        return CompileResult(
            ResultState.FAIL,
            component,
            version,
            errors=["APC registry profile_requirements must be an object"],
        )

    try:
        graph = CompatibilityGraph(edge_documents)
    except ValueError as exc:
        return CompileResult(ResultState.FAIL, component, version, errors=[str(exc)])

    source = Endpoint(component, version, manifest["provenance"]["commit"])
    required_targets = [Endpoint.from_document(target) for target in compatibility.get("requires_edges", [])]
    profile_results: dict[str, ResultState] = {}
    unknowns: list[str] = []
    evidence_refs: list[str] = []

    for profile in profiles:
        requirement = profile_requirements.get(profile)
        if not isinstance(requirement, dict):
            errors.append(f"missing APC-1 profile requirement: {profile}")
            profile_results[profile] = ResultState.FAIL
            continue

        required_contracts = requirement.get("required_contracts", [])
        if not isinstance(required_contracts, list):
            errors.append(f"APC-1/{profile} required_contracts must be an array")
            profile_results[profile] = ResultState.FAIL
            continue
        missing_contracts = [name for name in required_contracts if name not in manifest["contracts"]]
        if missing_contracts:
            for name in missing_contracts:
                errors.append(f"APC-1/{profile} requires contract: {name}")
            profile_results[profile] = ResultState.FAIL
            continue

        minimum = requirement.get("minimum_edge_evidence", "CE0")
        edge_states: list[ResultState] = []
        for target in required_targets:
            state = graph.best_state(source, target, minimum)
            edge_states.append(state)
            if state == ResultState.UNKNOWN:
                unknowns.append(
                    f"APC-1/{profile} required edge {_edge_label(source)} -> {_edge_label(target)} lacks {minimum} evidence"
                )
            elif state == ResultState.FAIL:
                errors.append(
                    f"APC-1/{profile} required edge {_edge_label(source)} -> {_edge_label(target)} is incompatible"
                )

            if state == ResultState.PASS:
                for edge in graph.between(source, target):
                    if edge.state == "pass":
                        evidence_refs.extend(ref for _, ref in edge.evidence)

        profile_results[profile] = _aggregate(edge_states) if required_targets else ResultState.PASS

    state = _aggregate(profile_results.values())
    if errors and state != ResultState.FAIL:
        state = ResultState.FAIL
    return CompileResult(
        state=state,
        component=component,
        version=version,
        profile_results=profile_results,
        errors=errors,
        unknowns=unknowns,
        evidence_refs=sorted(set(evidence_refs)),
    )


def _render_text(result: CompileResult, apc: dict) -> str:
    lines: list[str] = []
    for profile, state in result.profile_results.items():
        lines.append(f"APC-1/{profile}: {state.value}")
    if not result.profile_results:
        lines.append(f"APC-1: {result.state.value}")
    lines.append(f"component: {result.component}@{result.version}")
    if result.profile_results:
        minima = {
            apc["profile_requirements"][profile]["minimum_edge_evidence"]
            for profile in result.profile_results
            if profile in apc.get("profile_requirements", {})
        }
        if len(minima) == 1:
            lines.append(f"minimum edge evidence: {next(iter(minima))}")
    lines.append(f"unknown required edges: {len(result.unknowns)}")
    lines.append(f"errors: {len(result.errors)}")
    for message in result.errors:
        lines.append(f"error: {message}")
    for message in result.unknowns:
        lines.append(f"unknown: {message}")
    return "\n".join(lines)


def _exit_code(state: ResultState) -> int:
    if state in {ResultState.PASS, ResultState.N_A}:
        return 0
    if state == ResultState.FAIL:
        return 2
    return 3


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Compile Aftergraph APC-1 component conformance")
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--edge", action="append", default=[], type=Path, help="compatibility-edge/1.0 JSON; repeatable")
    parser.add_argument("--apc", type=Path, default=ROOT / "docs/release-intelligence/apc-1.json")
    parser.add_argument("--format", choices=("json", "text"), default="text")
    args = parser.parse_args(argv)

    try:
        manifest = load_json(args.manifest)
        apc = load_json(args.apc)
        edges = [load_json(path) for path in args.edge]
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"schema": "aftergraph.apc-result/1", "state": "FAIL", "errors": [str(exc)]}))
        return 2

    result = compile_component(manifest, apc, edges)
    if args.format == "json":
        print(json.dumps(result.to_dict(), sort_keys=True))
    else:
        print(_render_text(result, apc))
    return _exit_code(result.state)


if __name__ == "__main__":
    raise SystemExit(main())
