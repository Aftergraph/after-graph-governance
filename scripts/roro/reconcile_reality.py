#!/usr/bin/env python3
"""Reduce R.O.R.O. observations into explicit RealityDiff records."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
REALITY = ROOT / "docs/system-reality"
OUT = REALITY / "reality-diffs.json"


def load(name: str) -> dict[str, Any]:
    return json.loads((REALITY / name).read_text(encoding="utf-8"))


def evidence_ref(name: str, subject: str) -> str:
    return f"roro-artifact://docs/system-reality/{name}#{subject}"


def add(diffs: list[dict[str, Any]], *, diff_id: str, subject: str,
        classification: str, dimension: str, reason: str,
        evidence: list[str], severity: str = "MEDIUM") -> None:
    epistemic_status = {
        "CONFLICT": "CONFLICTING",
        "STALE": "STALE",
        "UNKNOWN": "UNKNOWN",
        "MISSING": "UNKNOWN",
        "UNMAPPED": "UNKNOWN",
        "DRIFT": "OBSERVED",
    }[classification]
    diffs.append({
        "diff_id": diff_id,
        "subject": subject,
        "classification": classification,
        "dimension": dimension,
        "severity": severity,
        "reason": reason,
        "epistemic_status": epistemic_status,
        "evidence_refs": sorted(set(evidence)),
    })


def build() -> dict[str, Any]:
    diffs: list[dict[str, Any]] = []
    source_gaps = load("reality-gaps.json")
    operational_gaps = load("operational-reality-gaps.json")
    deployments = load("deployment-source-diffs.json")
    recovery = load("recovery-mechanisms.json")
    recovery_verifications = load("recovery-verifications.json")
    route_dispositions = load("route-dispositions.json")
    runtime_disposition = load("runtime-topology-disposition.json")
    semantic_declarations = load("semantic-declarations.json")
    source_dispositions = load("source-binding-dispositions.json")
    cloud = load("cloud-resource-classification.json")

    declared_repos = {item["repository"] for item in semantic_declarations["declarations"]}
    disposition_by_component = {item["component_id"]: item for item in source_dispositions["dispositions"]}
    for gap in source_gaps["gaps"]:
        reason = gap["reason"]
        subject = gap["subject"]
        if reason == "no_explicit_semantic_component_manifest_in_source_bootstrap" and subject in declared_repos:
            continue
        if reason == "live_repository_missing_from_platform_topology_2.0" and subject in declared_repos:
            continue
        if reason == "same_component_identity_observed_at_multiple_source_bindings":
            disposition = disposition_by_component.get(subject)
            if disposition and disposition["disposition"] in {"VENDORED_PROJECTION", "MIRROR"}:
                continue
        add(
            diffs,
            diff_id=f"diff:source:{len(diffs)+1}",
            subject=subject,
            classification="UNKNOWN",
            dimension="SOURCE",
            reason=reason,
            evidence=[evidence_ref("reality-gaps.json", subject)],
            severity="MEDIUM",
        )

    route_by_host = {r["host"]: r for r in route_dispositions["routes"]}
    cloud_adjacent_unclassified = [r for r in cloud["resources"] if r.get("owner_class") == "AFTERGRAPH_ADJACENT_UNCLASSIFIED"]
    recovery_verified_count = sum(v.get("verdict") in {"RECOVERABLE_VERIFIED", "DATA_RECOVERY_VERIFIED"} for v in recovery_verifications["verifications"])
    for gap in operational_gaps["gaps"]:
        if gap["type"] == "CLOUD_OWNERSHIP_UNCLASSIFIED" and not cloud_adjacent_unclassified:
            continue
        if gap["type"] == "CREDENTIAL_SNAPSHOT_SPRAWL":
            epistemic = "OBSERVED"
            classification = "DRIFT"
        elif gap["type"] == "HOST_CONCENTRATION":
            epistemic = "OBSERVED"
            classification = "DRIFT"
        elif gap["type"] == "RECOVERY_PROOF_UNKNOWN" and recovery_verified_count == len(recovery["mechanisms"]):
            continue
        elif gap["type"] == "PUBLIC_ROUTE_ABSENT":
            host = gap["subject"].removeprefix("route://")
            disposition = route_by_host.get(host)
            if disposition and disposition["disposition"] in {"NOT_REQUIRED", "NOT_DECLARED_PUBLIC"}:
                continue
            if disposition and disposition["disposition"] == "SUPERSEDED":
                if disposition.get("source_drift"):
                    epistemic = "OBSERVED"
                    classification = "DRIFT"
                    gap = {**gap, "reason": disposition["reason"]}
                else:
                    continue
            elif disposition and disposition["disposition"] == "CONFLICTING_DESIRED_STATE":
                epistemic = "CONFLICTING"
                classification = "CONFLICT"
                gap = {**gap, "reason": disposition["reason"]}
            else:
                epistemic = gap.get("epistemic_status", "UNKNOWN")
                classification = {"CONFLICTING": "CONFLICT", "STALE": "STALE"}.get(epistemic, "UNKNOWN")
        elif gap["type"] == "DECLARED_RUNTIME_MISMATCH" and runtime_disposition["disposition"] == "TRANSITIONAL_ACCEPTED":
            epistemic = "OBSERVED"
            classification = "DRIFT"
            gap = {**gap, "reason": runtime_disposition["reason"]}
        else:
            epistemic = gap.get("epistemic_status", "UNKNOWN")
            classification = {"CONFLICTING": "CONFLICT", "STALE": "STALE"}.get(epistemic, "UNKNOWN")
        add(
            diffs,
            diff_id=f"diff:operational:{gap['id']}",
            subject=gap["subject"],
            classification=classification,
            dimension=gap["type"],
            reason=gap["reason"],
            evidence=[evidence_ref("operational-reality-gaps.json", gap["id"])],
            severity=gap.get("severity", "MEDIUM"),
        )

    for binding in deployments["bindings"]:
        if binding["status"] not in {"CONFLICTING", "UNKNOWN"}:
            continue
        service = binding["service"]
        add(
            diffs,
            diff_id=f"diff:deployment:{service}",
            subject=f"deployment://{service}",
            classification="CONFLICT" if binding["status"] == "CONFLICTING" else "UNKNOWN",
            dimension="DEPLOYMENT_SOURCE",
            reason=binding["reason"],
            evidence=[evidence_ref("deployment-source-diffs.json", service)],
            severity="HIGH" if binding["status"] == "CONFLICTING" else "MEDIUM",
        )

    recovery_by_service = {v["service"]: v for v in recovery_verifications["verifications"]}
    for mechanism in recovery["mechanisms"]:
        if recovery_by_service.get(mechanism["service"], {}).get("verdict") in {"RECOVERABLE_VERIFIED", "DATA_RECOVERY_VERIFIED"}:
            continue
        service = mechanism["service"]
        add(
            diffs,
            diff_id=f"diff:recovery:{service}",
            subject=f"recovery://{service}",
            classification="UNKNOWN",
            dimension="RECOVERY",
            reason="Backup mechanism is observed but restore/recoverability proof is absent.",
            evidence=[evidence_ref("recovery-mechanisms.json", service)],
            severity="HIGH",
        )

    timestamps = [
        source_gaps.get("generated_at", ""),
        operational_gaps.get("generated_at", ""),
        deployments.get("generated_at", ""),
        recovery.get("generated_at", ""),
    ]
    return {
        "schema_version": "roro-reality-diffs/0.1",
        "as_of": max(t for t in timestamps if t),
        "diffs": sorted(diffs, key=lambda item: item["diff_id"]),
        "summary": {
            "total": len(diffs),
            "conflicting": sum(d["classification"] == "CONFLICT" for d in diffs),
            "unknown": sum(d["classification"] == "UNKNOWN" for d in diffs),
            "stale": sum(d["classification"] == "STALE" for d in diffs),
        },
    }


def main() -> int:
    payload = build()
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        "R.O.R.O. RealityDiffs generated: "
        f"total={payload['summary']['total']} "
        f"conflicting={payload['summary']['conflicting']} "
        f"unknown={payload['summary']['unknown']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
