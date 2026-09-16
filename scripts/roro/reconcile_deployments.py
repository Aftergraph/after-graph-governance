#!/usr/bin/env python3
"""Derive deployment/source relations from promoted exact deployment evidence."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
REALITY = ROOT / "docs/system-reality"
INPUT = REALITY / "deployment-observations.json"
OUTPUT = REALITY / "deployment-source-diffs.json"


def classify(item: dict[str, Any]) -> tuple[str, str]:
    revisions = item["revisions"]
    relations = {rev["relation"] for rev in revisions}
    origin_relation = item["origin_relation"]

    build = item.get("build_provenance", {})
    workspace = item.get("working_directory_provenance", {})
    if origin_relation == "NON_CANONICAL_REMOTE" and build.get("vcs_modified") is True:
        return "CONFLICTING", "Observed running binary was built from modified source and the runtime checkout origin is not the canonical Aftergraph repository."
    if origin_relation == "CANONICAL_ARTIFACT_LEGACY_WORKTREE" and build.get("vcs_modified") is False and workspace.get("relation") == "LEGACY_NON_CANONICAL_WORKTREE" and workspace.get("runtime_files_match_canonical_head") is True:
        return "CANONICAL_COMPOSITE_LAG", "Running artifact is a clean canonical build; legacy working-directory checkout remains visible as non-blocking drift and runtime-read files match the canonical head."
    if origin_relation == "NON_CANONICAL_REMOTE":
        return "CONFLICTING", "Observed runtime origin is not the canonical Aftergraph repository."
    if build.get("vcs_modified") is True:
        return "CONFLICTING", "Observed running binary was built from modified source; exact canonical source equivalence is not established."
    if not revisions or not relations <= {"MATCH", "CANONICAL_ANCESTOR"}:
        return "UNKNOWN", "Exact deployment lineage cannot be established from current evidence."
    if relations == {"MATCH"}:
        return "OBSERVED_MATCH", "Observed deployment revision matches the canonical source snapshot head."
    if len(revisions) > 1:
        return "CANONICAL_COMPOSITE_LAG", "All observed runtime/artifact revisions are canonical ancestors of the source snapshot head."
    return "CANONICAL_LAG", "Observed deployment revision is a canonical ancestor of the source snapshot head."


def primary_revision(item: dict[str, Any]) -> str | None:
    preferred = ("RUNTIME_ARTIFACT_SOURCE", "FRONTEND_ARTIFACT_SOURCE", "RELEASE_SOURCE", "RUNTIME_SOURCE", "SERVER_SOURCE")
    by_role = {rev["role"]: rev["sha"] for rev in item["revisions"]}
    for role in preferred:
        if role in by_role:
            return by_role[role]
    return item["revisions"][0]["sha"] if item["revisions"] else None


def build_binding(item: dict[str, Any]) -> dict[str, Any]:
    status, reason = classify(item)
    revisions = item["revisions"]
    primary = primary_revision(item)
    return {
        "service": item["service"],
        "canonical_repository": item["canonical_repository"],
        "canonical_head_at_source_snapshot": item["canonical_head_at_source_snapshot"],
        "observed_deployed_revision": primary,
        "observed_revisions": revisions,
        "origin_relation": item["origin_relation"],
        "status": status,
        "epistemic_status": "CONFLICTING" if status == "CONFLICTING" else item["epistemic_status"],
        "reason": reason,
        "evidence_refs": item["evidence_refs"],
    }


def build() -> dict[str, Any]:
    source = json.loads(INPUT.read_text(encoding="utf-8"))
    bindings = [build_binding(item) for item in source["observations"]]
    return {
        "schema_version": "roro-deployment-source-diffs/0.2",
        "generated_at": source["observed_at"],
        "deployment_observed_at": source["observed_at"],
        "source_snapshot_generated_at": source.get("source_snapshot_generated_at"),
        "bindings": sorted(bindings, key=lambda item: item["service"]),
    }


def main() -> int:
    payload = build()
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    counts: dict[str, int] = {}
    for item in payload["bindings"]:
        counts[item["status"]] = counts.get(item["status"], 0) + 1
    print("R.O.R.O. deployment reconciliation: " + ", ".join(f"{k}={v}" for k, v in sorted(counts.items())))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
