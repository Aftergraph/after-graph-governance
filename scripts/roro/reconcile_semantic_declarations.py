#!/usr/bin/env python3
"""Derive declared repository semantic roles without equating repositories with components."""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REALITY = ROOT / "docs/system-reality"
TOPOLOGY = ROOT / "docs/platform-topology/2.0.json"
OUT = REALITY / "semantic-declarations.json"


def build() -> dict:
    registry = json.loads((REALITY / "component-registry.json").read_text())
    topology = json.loads(TOPOLOGY.read_text())
    live = {r["full_name"]: r for r in registry["repositories"]}
    declarations = []
    for row in topology["repositories"]:
        full = f"Aftergraph/{row['name']}"
        if full not in live:
            continue
        declarations.append({
            "repository": full,
            "semantic_role": row.get("role"),
            "system_class": row.get("system_class"),
            "architecture_plane": row.get("architecture_plane"),
            "lifecycle": row.get("lifecycle"),
            "epistemic_status": "DECLARED",
            "evidence_ref": "governance://platform-topology/2.0",
        })
    manifest_repos = {
        b["repository"]
        for component in registry["components"]
        for b in component.get("source_bindings", [])
    }
    declared_repos = {d["repository"] for d in declarations}
    uncovered = sorted(set(live) - manifest_repos - declared_repos)
    return {
        "schema_version": "roro-semantic-declarations/0.1",
        "as_of": registry["generated_at"],
        "declarations": sorted(declarations, key=lambda x: x["repository"]),
        "manifest_covered_repositories": sorted(manifest_repos),
        "uncovered_repositories": uncovered,
        "policy": {"repository_is_not_component": True},
    }


def main() -> int:
    payload = build()
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(
        f"R.O.R.O. semantic declarations: declared={len(payload['declarations'])} "
        f"uncovered={len(payload['uncovered_repositories'])}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
