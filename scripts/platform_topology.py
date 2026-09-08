#!/usr/bin/env python3
"""Zero-dependency platform-topology/2.0 validator and README renderer.

CLI:
    python scripts/platform_topology.py check
    python scripts/platform_topology.py render-readme

Only the standard library is used; do not add PyYAML or jsonschema as
required runtime dependencies.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any, Mapping

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TOPOLOGY = REPO_ROOT / "docs" / "platform-topology" / "2.0.json"

PLANE_VALUES = {"intelligence", "authority", "trust", "runtime", "execution", "verification", "experience"}
PLANE_ORDER = ["intelligence", "authority", "trust", "runtime", "execution", "verification", "experience"]
REQUIRED_REPO_FIELDS = {
    "name",
    "canonical_branch",
    "visibility",
    "architecture_plane",
    "system_class",
    "role",
    "lifecycle",
    "owns",
    "must_not_own",
}
FORBIDDEN_ACTIVE_NAME_PARTS = ("@avc/", "avc-")
LEGACY_REPOSITORY = "autonomous-venture-company"
SHA_LIKE_KEYS = {"head_sha", "remote_head_sha", "remote_sha", "sha", "commit_sha"}
SHA_LIKE_VALUE = re.compile(r"\b[0-9a-f]{40}\b")

README_COLUMNS = (
    "Architecture plane",
    "System class",
    "Repository",
    "Role",
    "Lifecycle",
    "Canonical responsibility",
)


def load_topology(path: Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        doc = json.load(handle)
    if not isinstance(doc, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return doc


def topology_index(doc: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    repos = doc.get("repositories", [])
    if not isinstance(repos, list):
        raise ValueError("topology document has no repository list")
    return {r["name"]: r for r in repos if isinstance(r, dict) and "name" in r}


def validate_topology(doc: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    if not isinstance(doc, Mapping):
        return ["topology document must be a JSON object"]
    if doc.get("schema_version") != "platform-topology/2.0":
        errors.append(f"unsupported schema_version: {doc.get('schema_version')!r}")
    if doc.get("organization") != "Aftergraph":
        errors.append(f"unsupported organization: {doc.get('organization')!r}")
    repos = doc.get("repositories")
    if not isinstance(repos, list) or not repos:
        return errors + ["topology document must list repositories"]
    seen: set[str] = set()
    for entry in repos:
        if not isinstance(entry, Mapping):
            errors.append("repository entry must be an object")
            continue
        name = entry.get("name", "?")
        if name in seen:
            errors.append(f"duplicate repository name: {name}")
        seen.add(name)
        missing = REQUIRED_REPO_FIELDS - set(entry)
        if missing:
            errors.append(f"repository {name} is missing fields: {sorted(missing)}")
        for field in set(entry) - REQUIRED_REPO_FIELDS:
            errors.append(f"repository {name} has unexpected field: {field}")
        plane = entry.get("architecture_plane")
        if plane is not None and plane not in PLANE_VALUES:
            errors.append(f"repository {name} has unknown architecture plane: {plane!r}")
        if entry.get("canonical_branch") != "main":
            errors.append(f"repository {name} has non-main canonical branch: {entry.get('canonical_branch')!r}")
        for key, value in entry.items():
            if key in SHA_LIKE_KEYS:
                errors.append(f"repository {name} carries exact-SHA field: {key}")
            elif isinstance(value, str) and SHA_LIKE_VALUE.search(value):
                errors.append(f"repository {name} carries exact-SHA value in field: {key}")
        if isinstance(name, str) and ("@avc/" in name or "avc-" in name):
            errors.append(f"repository {name} uses a forbidden active AVC identifier")
        if name == LEGACY_REPOSITORY and not (
            entry.get("system_class") == "legacy-transition" and entry.get("lifecycle") == "legacy-transition"
        ):
            errors.append(
                f"legacy repository {name} is allowlisted only with "
                'system_class == "legacy-transition" and lifecycle == "legacy-transition"'
            )
    return errors


def _plane_label(plane: Any) -> str:
    if plane is None:
        return "Support"
    return str(plane).capitalize()


def render_readme_table(doc: Mapping[str, Any]) -> str:
    repos = [r for r in doc.get("repositories", []) if isinstance(r, Mapping)]
    plane_rows = [r for r in repos if r.get("architecture_plane") is not None]
    support_rows = [r for r in repos if r.get("architecture_plane") is None]
    plane_rows.sort(key=lambda r: (PLANE_ORDER.index(r["architecture_plane"]), str(r.get("name", ""))))
    support_rows.sort(key=lambda r: str(r.get("name", "")))
    lines = [
        "| " + " | ".join(README_COLUMNS) + " |",
        "|" + "|".join(["---"] * len(README_COLUMNS)) + "|",
    ]
    for repo in plane_rows + support_rows:
        lines.append(
            "| " + " | ".join(
                [
                    _plane_label(repo.get("architecture_plane")),
                    str(repo.get("system_class", "")),
                    f"`{repo.get('name', '')}`",
                    str(repo.get("role", "")),
                    str(repo.get("lifecycle", "")),
                    str(repo.get("owns", "")),
                ]
            )
            + " |"
        )
    return "\n".join(lines) + "\n"


def main(argv: list[str]) -> int:
    command = argv[1] if len(argv) > 1 else "check"
    if command == "check":
        errors = validate_topology(load_topology(DEFAULT_TOPOLOGY))
        if errors:
            for error in errors:
                print(f"TOPOLOGY-FAIL: {error}", file=sys.stderr)
            return 1
        print("topology-ok: docs/platform-topology/2.0.json")
        return 0
    if command == "render-readme":
        print(render_readme_table(load_topology(DEFAULT_TOPOLOGY)), end="")
        return 0
    print(f"unknown command: {command} (expected check|render-readme)", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
