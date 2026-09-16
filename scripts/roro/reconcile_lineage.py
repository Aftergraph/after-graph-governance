#!/usr/bin/env python3
"""Reconcile legacy @avc package lineage against observed Aftergraph manifests."""
from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any

ALLOWED_STATES = {
    "MIGRATED", "ACTIVE_LEGACY", "DUPLICATED",
    "PARTIALLY_MIGRATED", "ORPHANED", "UNKNOWN",
}
MIGRATED_FROM_RE = re.compile(r"migrated\s+from\s+@avc/([a-z0-9._-]+)", re.IGNORECASE)


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _content(item: dict[str, Any]) -> dict[str, Any]:
    value = item.get("content")
    return value if isinstance(value, dict) else {}


def _name(item: dict[str, Any]) -> str:
    value = _content(item).get("name", "")
    return value if isinstance(value, str) else ""


def _evidence_ref(item: dict[str, Any]) -> str:
    repo = item.get("repository", "UNKNOWN")
    revision = item.get("revision", "UNKNOWN")
    path = item.get("path", "UNKNOWN")
    return f"github://{repo}@{revision}/{path}"
def _all_dependencies(item: dict[str, Any]) -> set[str]:
    deps = _content(item).get("dependencies", {})
    if not isinstance(deps, dict):
        return set()
    return {key for key in deps if isinstance(key, str)}


def reconcile_lineage(manifests: list[dict[str, Any]], observed_at: str | None = None) -> list[dict[str, Any]]:
    observed_at = observed_at or utc_now()
    legacy = [item for item in manifests if _name(item).startswith("@avc/")]
    targets = [item for item in manifests if _name(item).startswith("@aftergraph/")]

    target_by_suffix: dict[str, list[dict[str, Any]]] = {}
    explicit_targets: dict[str, list[dict[str, Any]]] = {}
    for target in targets:
        suffix = _name(target).split("/", 1)[1]
        target_by_suffix.setdefault(suffix, []).append(target)
        description = str(_content(target).get("description", ""))
        for match in MIGRATED_FROM_RE.findall(description):
            explicit_targets.setdefault(match.lower(), []).append(target)

    result: list[dict[str, Any]] = []
    for source in sorted(legacy, key=_name):
        legacy_name = _name(source)
        suffix = legacy_name.split("/", 1)[1]
        explicit = explicit_targets.get(suffix.lower(), [])
        same_name = target_by_suffix.get(suffix, [])
        candidates = explicit or same_name
        consumers = [
            item for item in manifests
            if item is not source and legacy_name in _all_dependencies(item)
        ]
        if len(candidates) > 1:
            target = None
            status = "UNKNOWN"
        elif candidates:
            target = candidates[0]
            status = "PARTIALLY_MIGRATED" if explicit else "DUPLICATED"
        else:
            target = None
            status = "ACTIVE_LEGACY" if consumers else "UNKNOWN"

        evidence_refs = [_evidence_ref(source)]
        if target is not None:
            evidence_refs.append(_evidence_ref(target))
        evidence_refs.extend(_evidence_ref(item) for item in consumers)
        evidence_refs = sorted(set(evidence_refs))

        record = {
            "lineage_id": f"lineage:avc:{suffix}",
            "legacy_component_id": f"ag:legacy:avc:{suffix.lower().replace('_', '-')}",
            "legacy_package": legacy_name,
            "target_component_id": None,
            "target_package": None,
            "status": status,
            "active_consumers": sorted({_name(item) or item.get("repository", "UNKNOWN") for item in consumers}),
            "evidence_refs": evidence_refs if status != "UNKNOWN" else [],
            "observed_at": observed_at,
        }
        if target is not None:
            target_name = _name(target)
            target_suffix = target_name.split("/", 1)[1]
            record["target_component_id"] = f"ag:component:{target_suffix.lower().replace('_', '-')}"
            record["target_package"] = target_name
        result.append(record)

    return result
