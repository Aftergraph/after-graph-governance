#!/usr/bin/env python3
"""Invariant validator for checked-in R.O.R.O. source-reality artifacts."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
REALITY = ROOT / "docs/system-reality"
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
COMPONENT_RE = re.compile(r"^ag:[a-z0-9][a-z0-9:-]*$")
LINEAGE_STATES = {
    "MIGRATED", "ACTIVE_LEGACY", "DUPLICATED",
    "PARTIALLY_MIGRATED", "ORPHANED", "UNKNOWN",
}
FORBIDDEN_VALUE_KEYS = {
    "secret", "secret_value", "token", "token_value", "password",
    "api_key", "private_key", "credential_value",
}


def load(name: str) -> dict[str, Any]:
    path = REALITY / name
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read {path}: {exc}") from exc
def walk_keys(value: Any, path: str = "$") -> list[str]:
    findings: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            if key.lower() in FORBIDDEN_VALUE_KEYS:
                findings.append(f"forbidden credential-value key {path}.{key}")
            findings.extend(walk_keys(child, f"{path}.{key}"))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            findings.extend(walk_keys(child, f"{path}[{index}]"))
    return findings


def validate_registry(registry: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if registry.get("schema_version") != "roro-component-registry/0.1":
        errors.append("registry schema_version")
    repos = registry.get("repositories")
    components = registry.get("components")
    if not isinstance(repos, list) or not repos:
        errors.append("registry repositories must be non-empty list")
        repos = []
    if not isinstance(components, list):
        errors.append("registry components must be list")
        components = []

    repo_names: set[str] = set()
    for repo in repos:
        name = repo.get("full_name")
        if not isinstance(name, str) or name in repo_names:
            errors.append(f"duplicate/invalid repository {name!r}")
        repo_names.add(name)
        if not SHA_RE.fullmatch(str(repo.get("head_sha", ""))):
            errors.append(f"repository {name}: invalid head_sha")
    component_ids: set[str] = set()
    binding_keys: set[tuple[str, str, str, str]] = set()
    for component in components:
        cid = component.get("component_id")
        if not isinstance(cid, str) or not COMPONENT_RE.fullmatch(cid):
            errors.append(f"invalid component_id {cid!r}")
            continue
        if cid in component_ids:
            errors.append(f"duplicate component_id {cid}")
        component_ids.add(cid)
        bindings = component.get("source_bindings")
        if not isinstance(bindings, list) or not bindings:
            errors.append(f"component {cid}: no source bindings")
            continue
        for binding in bindings:
            repo = binding.get("repository")
            path = binding.get("path")
            rev = binding.get("revision")
            if repo not in repo_names:
                errors.append(f"component {cid}: binding repo not observed: {repo}")
            if not isinstance(path, str) or not path:
                errors.append(f"component {cid}: invalid binding path")
            if not SHA_RE.fullmatch(str(rev or "")):
                errors.append(f"component {cid}: invalid binding revision")
            key = (cid, str(repo), str(path), str(rev))
            if key in binding_keys:
                errors.append(f"component {cid}: duplicate source binding")
            binding_keys.add(key)
    return errors


def validate_lineage(lineage: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if lineage.get("schema_version") != "roro-component-lineage/0.1":
        errors.append("lineage schema_version")
    records = lineage.get("lineage")
    if not isinstance(records, list):
        return errors + ["lineage records must be list"]
    seen: set[str] = set()
    for record in records:
        lid = record.get("lineage_id")
        if not isinstance(lid, str) or lid in seen:
            errors.append(f"duplicate/invalid lineage_id {lid!r}")
        seen.add(str(lid))
        status = record.get("status")
        if status not in LINEAGE_STATES:
            errors.append(f"lineage {lid}: invalid status {status!r}")
        refs = record.get("evidence_refs")
        if status != "UNKNOWN" and (not isinstance(refs, list) or not refs):
            errors.append(f"lineage {lid}: non-UNKNOWN status requires evidence_refs")
        legacy_id = record.get("legacy_component_id")
        if not isinstance(legacy_id, str) or not COMPONENT_RE.fullmatch(legacy_id):
            errors.append(f"lineage {lid}: invalid legacy_component_id")
        target_id = record.get("target_component_id")
        if target_id is not None and (not isinstance(target_id, str) or not COMPONENT_RE.fullmatch(target_id)):
            errors.append(f"lineage {lid}: invalid target_component_id")
    return errors


def validate_gaps(gaps: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if gaps.get("schema_version") != "roro-reality-gaps/0.1":
        errors.append("gaps schema_version")
    records = gaps.get("gaps")
    if not isinstance(records, list):
        return errors + ["gaps must be list"]
    for index, record in enumerate(records):
        if record.get("epistemic_status") != "UNKNOWN":
            errors.append(f"gap[{index}] must remain UNKNOWN")
        if not record.get("subject") or not record.get("reason"):
            errors.append(f"gap[{index}] missing subject/reason")
    return errors
def main() -> int:
    try:
        registry = load("component-registry.json")
        lineage = load("component-lineage.json")
        gaps = load("reality-gaps.json")
    except ValueError as exc:
        print(f"ERROR: {exc}")
        return 1

    errors = []
    errors.extend(validate_registry(registry))
    errors.extend(validate_lineage(lineage))
    errors.extend(validate_gaps(gaps))
    errors.extend(walk_keys(registry))
    errors.extend(walk_keys(lineage))
    errors.extend(walk_keys(gaps))
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(
        "R.O.R.O. registry OK: "
        f"repositories={len(registry['repositories'])} "
        f"components={len(registry['components'])} "
        f"lineage={len(lineage['lineage'])} gaps={len(gaps['gaps'])}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
