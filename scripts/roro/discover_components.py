#!/usr/bin/env python3
"""Build R.O.R.O. semantic component records from observed source manifests."""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

COMPONENT_ID_RE = re.compile(r"^ag:[a-z0-9][a-z0-9:-]*$")


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _slug(raw: str) -> str:
    value = raw.strip().lower().replace("_", "-").replace(".", "-")
    value = re.sub(r"[^a-z0-9-]+", "-", value).strip("-")
    return re.sub(r"-+", "-", value)


def component_identity(package_name: str, repository: str) -> tuple[str, str, str] | None:
    """Return (component_id, class, lifecycle) from explicit manifest identity only."""
    if package_name.startswith("@aftergraph/"):
        slug = _slug(package_name.split("/", 1)[1])
        return (f"ag:component:{slug}", "package", "ACTIVE")
    if package_name.startswith("@avc/"):
        slug = _slug(package_name.split("/", 1)[1])
        return (f"ag:legacy:avc:{slug}", "legacy-package", "LEGACY")
    if package_name.startswith("aftergraph-"):
        slug = _slug(package_name.removeprefix("aftergraph-"))
        return (f"ag:component:{slug}", "project", "ACTIVE")
    return None


def _binding(repo: dict[str, Any], manifest: dict[str, Any], observed_at: str) -> dict[str, Any]:
    manifest_path = str(manifest["path"])
    parent = str(Path(manifest_path).parent)
    if parent == ".":
        parent = "."
    return {
        "repository": repo["full_name"],
        "path": parent,
        "revision": repo["head_sha"],
        "default_branch": repo["default_branch"],
        "observer": "roro:scout:github",
        "observed_at": observed_at,
        "evidence_ref": f"github://{repo['full_name']}@{repo['head_sha']}/{manifest_path}",
    }


def discover_components(repositories: list[dict[str, Any]], observed_at: str | None = None) -> list[dict[str, Any]]:
    observed_at = observed_at or utc_now()
    grouped: dict[str, dict[str, Any]] = {}
    seen_bindings: defaultdict[str, set[tuple[str, str, str]]] = defaultdict(set)

    for repo in repositories:
        for manifest in repo.get("manifests", []):
            content = manifest.get("content") or {}
            name = content.get("name")
            if not isinstance(name, str) or not name.strip():
                continue
            identity = component_identity(name, repo["full_name"])
            if identity is None:
                continue
            component_id, component_class, lifecycle = identity
            if not COMPONENT_ID_RE.fullmatch(component_id):
                raise ValueError(f"invalid generated component id: {component_id}")
            if component_id not in grouped:
                grouped[component_id] = {
                    "component_id": component_id,
                    "name": name,
                    "component_class": component_class,
                    "lifecycle": lifecycle,
                    "epistemic_status": "OBSERVED",
                    "classification_basis": "explicit source manifest identity",
                    "source_bindings": [],
                    "aliases": [name],
                }
            component = grouped[component_id]
            if name not in component["aliases"]:
                component["aliases"].append(name)
            binding = _binding(repo, manifest, observed_at)
            key = (binding["repository"], binding["path"], binding["revision"])
            if key not in seen_bindings[component_id]:
                component["source_bindings"].append(binding)
                seen_bindings[component_id].add(key)

    for component in grouped.values():
        component["source_bindings"].sort(key=lambda b: (b["repository"], b["path"], b["revision"]))
        component["aliases"].sort()
        if len(component["source_bindings"]) > 1:
            component["epistemic_status"] = "CONFLICTING"
            component["classification_basis"] = "same semantic manifest identity observed at multiple source bindings"

    return [grouped[key] for key in sorted(grouped)]


def flatten_manifests(repositories: list[dict[str, Any]]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for repo in repositories:
        for manifest in repo.get("manifests", []):
            item = dict(manifest)
            item["repository"] = repo["full_name"]
            item["revision"] = repo["head_sha"]
            result.append(item)
    return result
def _topology_map(topology: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        f"Aftergraph/{entry['name']}": entry
        for entry in topology.get("repositories", [])
        if isinstance(entry, dict) and isinstance(entry.get("name"), str)
    }


def build_registry(repositories: list[dict[str, Any]], topology: dict[str, Any], observed_at: str) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    topo = _topology_map(topology)
    components = discover_components(repositories, observed_at=observed_at)
    repository_records: list[dict[str, Any]] = []
    gaps: list[dict[str, Any]] = []
    live_names = {repo["full_name"] for repo in repositories}

    for repo in repositories:
        entry = topo.get(repo["full_name"])
        record = {
            "full_name": repo["full_name"],
            "default_branch": repo["default_branch"],
            "head_sha": repo["head_sha"],
            "visibility": repo["visibility"],
            "archived": bool(repo.get("archived")),
            "epistemic_status": "OBSERVED",
            "observed_at": observed_at,
            "topology": None,
            "manifest_count": len(repo.get("manifests", [])),
        }
        if entry is not None:
            record["topology"] = {key: entry.get(key) for key in ("role", "lifecycle", "system_class", "architecture_plane")}
        else:
            gaps.append(_gap(repo["full_name"], "live_repository_missing_from_platform_topology_2.0", observed_at))
        repository_records.append(record)
        for error in repo.get("manifest_errors", []):
            gaps.append(_gap(
                f"{repo['full_name']}:{error.get('path', 'UNKNOWN')}",
                "manifest_fetch_or_parse_failed",
                observed_at,
            ))

    for name in sorted(set(topo) - live_names):
        gaps.append(_gap(name, "topology_repository_not_observed_in_live_org", observed_at))

    bound_repositories = {
        binding["repository"]
        for component in components
        for binding in component["source_bindings"]
    }
    for name in sorted(live_names - bound_repositories):
        gaps.append(_gap(name, "no_explicit_semantic_component_manifest_in_source_bootstrap", observed_at))

    for component in components:
        if len(component["source_bindings"]) > 1:
            gaps.append(_gap(
                component["component_id"],
                "same_component_identity_observed_at_multiple_source_bindings",
                observed_at,
            ))

    registry = {
        "schema_version": "roro-component-registry/0.1",
        "organization": "Aftergraph",
        "generated_at": observed_at,
        "observer": "roro:scout:github",
        "repositories": sorted(repository_records, key=lambda item: item["full_name"].lower()),
        "components": components,
    }
    return registry, gaps


def _gap(subject: str, reason: str, observed_at: str) -> dict[str, Any]:
    return {"subject": subject, "reason": reason, "epistemic_status": "UNKNOWN", "observed_at": observed_at}
def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate R.O.R.O. source-reality artifacts from live GitHub state")
    parser.add_argument("--org", default="Aftergraph")
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--topology", type=Path)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    output_dir = args.output_dir or root / "docs/system-reality"
    topology_path = args.topology or root / "docs/platform-topology/2.0.json"
    topology = json.loads(topology_path.read_text(encoding="utf-8"))

    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from discover_github import discover_github_org
    from reconcile_lineage import reconcile_lineage

    repositories, observed_at = discover_github_org(args.org)
    registry, gaps = build_registry(repositories, topology, observed_at)
    manifests = flatten_manifests(repositories)
    lineage_records = reconcile_lineage(manifests, observed_at=observed_at)
    lineage = {
        "schema_version": "roro-component-lineage/0.1",
        "generated_at": observed_at,
        "source_namespace": "@avc",
        "target_namespace": "@aftergraph",
        "lineage": lineage_records,
    }
    gap_doc = {
        "schema_version": "roro-reality-gaps/0.1",
        "generated_at": observed_at,
        "gaps": sorted(gaps, key=lambda item: (item["reason"], item["subject"])),
    }
    _write_json(output_dir / "component-registry.json", registry)
    _write_json(output_dir / "component-lineage.json", lineage)
    _write_json(output_dir / "reality-gaps.json", gap_doc)
    print(
        "R.O.R.O. source reality generated: "
        f"repositories={len(registry['repositories'])} "
        f"components={len(registry['components'])} "
        f"lineage={len(lineage_records)} gaps={len(gaps)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
