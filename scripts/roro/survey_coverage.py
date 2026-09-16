#!/usr/bin/env python3
"""Build multidimensional R.O.R.O. coverage and a fail-closed migration gate."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
REALITY = ROOT / "docs/system-reality"
REPORT = REALITY / "coverage-report.json"
GATE = REALITY / "coverage-gate.json"


def load(name: str) -> dict[str, Any]:
    return json.loads((REALITY / name).read_text(encoding="utf-8"))


def ratio(observed: int, total: int) -> float | None:
    if total == 0:
        return None
    return round(observed / total, 4)


def dimension(status: str, observed: int | None = None,
              total: int | None = None, **extra: Any) -> dict[str, Any]:
    result: dict[str, Any] = {"status": status}
    if observed is not None:
        result["observed"] = observed
    if total is not None:
        result["total"] = total
        result["coverage"] = ratio(observed or 0, total)
    result.update(extra)
    return result


def build_report() -> dict[str, Any]:
    registry = load("component-registry.json")
    source_gaps = load("reality-gaps.json")
    operational = load("operational-reality.json")
    operational_gaps = load("operational-reality-gaps.json")
    deployments = load("deployment-source-diffs.json")
    cloud = load("cloud-resource-classification.json")
    recovery = load("recovery-mechanisms.json")
    diffs = load("reality-diffs.json")

    repos = registry["repositories"]
    no_manifest = [g for g in source_gaps["gaps"]
                   if g["reason"] == "no_explicit_semantic_component_manifest_in_source_bootstrap"]
    dep_bindings = deployments["bindings"]
    exact_deployments = [b for b in dep_bindings if b.get("observed_deployed_revision")]
    dep_conflicts = [b for b in dep_bindings if b["status"] == "CONFLICTING"]
    dep_unknown = [b for b in dep_bindings if b["status"] == "UNKNOWN"]

    routes = operational["route_summary"]["routes"]
    resolved_routes = [r for r in routes if r["dns_state"] == "RESOLVED"]
    unknown_cloud = [r for r in cloud["resources"] if r["epistemic_status"] == "UNKNOWN"]
    adjacent_cloud = [r for r in cloud["resources"]
                      if r["owner_class"] == "AFTERGRAPH_ADJACENT_UNCLASSIFIED"]
    verified_recovery = [m for m in recovery["mechanisms"]
                         if m["recoverability"] == "RECOVERABLE_VERIFIED"]

    dimensions = {
        "source": dimension(
            "PARTIAL" if no_manifest else "PASS",
            observed=len(repos) - len(no_manifest),
            total=len(repos),
            metric="semantic_manifest_coverage",
            exact_repo_heads=len(repos),
            exact_head_coverage=1.0 if repos else None,
            semantic_manifest_gaps=len(no_manifest),
        ),
        "deployment": dimension(
            "BLOCKED" if dep_conflicts or dep_unknown else "PASS",
            observed=len(exact_deployments),
            total=len(dep_bindings),
            metric="exact_deployment_revision_coverage",
            conflicts=len(dep_conflicts),
            unknown=len(dep_unknown),
        ),
        "routes": dimension(
            "PARTIAL" if len(resolved_routes) != len(routes) else "PASS",
            observed=len(resolved_routes),
            total=len(routes),
            metric="dns_resolution_coverage",
            unresolved=len(routes) - len(resolved_routes),
        ),
        "cloud": dimension(
            "PARTIAL" if adjacent_cloud or unknown_cloud else "PASS",
            observed=len(cloud["resources"]) - len(unknown_cloud),
            total=len(cloud["resources"]),
            metric="ownership_evidence_coverage",
            epistemically_unknown=len(unknown_cloud),
            aftergraph_adjacent_unclassified=len(adjacent_cloud),
        ),
        "credentials": dimension(
            "BLOCKED",
            consumer_mapping="UNKNOWN",
            values_collected=False,
            snapshot_sprawl_observed=operational["credential_summary"]["lenovo_backup_or_snapshot_env_files"],
            permission_drift_observations=operational["credential_summary"]["permission_drift_observations"],
        ),
    }

    dimensions.update({
        "recovery": dimension(
            "BLOCKED" if len(verified_recovery) != len(recovery["mechanisms"]) else "PASS",
            observed=len(verified_recovery),
            total=len(recovery["mechanisms"]),
            metric="restore_verified_coverage",
            backup_present=sum(m["recoverability"] == "BACKUP_PRESENT" for m in recovery["mechanisms"]),
        ),
        "runtime": dimension(
            "BLOCKED" if any(g["type"] == "DECLARED_RUNTIME_MISMATCH" for g in operational_gaps["gaps"]) else "PASS",
            active_services=operational["runtime_summary"]["active_services"],
            containers=operational["runtime_summary"]["containers"],
            self_hosted_runner_services=operational["runtime_summary"]["self_hosted_runner_services"],
        ),
        "reality_diff": dimension(
            "BLOCKED" if diffs["summary"]["conflicting"] or diffs["summary"]["unknown"] else "PASS",
            observed=diffs["summary"]["total"],
            conflicts=diffs["summary"]["conflicting"],
            unknowns=diffs["summary"]["unknown"],
            stale=diffs["summary"]["stale"],
        ),
    })

    timestamps = [
        registry.get("generated_at", ""),
        operational.get("generated_at", ""),
        deployments.get("generated_at", ""),
        cloud.get("generated_at", ""),
        recovery.get("generated_at", ""),
        diffs.get("as_of", ""),
    ]
    return {
        "schema_version": "roro-coverage-report/0.1",
        "as_of": max(t for t in timestamps if t),
        "dimensions": dimensions,
        "policy": {
            "overall_scalar_score_prohibited": True,
            "unknowns_fail_closed_for_consequential_migration": True,
        },
    }


def build_gate(report: dict[str, Any]) -> dict[str, Any]:
    d = report["dimensions"]
    blockers: list[dict[str, str]] = []

    def block(blocker_id: str, dimension_name: str, reason: str) -> None:
        blockers.append({"id": blocker_id, "dimension": dimension_name, "reason": reason})

    if d["source"]["semantic_manifest_gaps"]:
        block("semantic-component-coverage", "source",
              "Some live repositories still lack explicit semantic component manifests.")
    if d["deployment"]["conflicts"] or d["deployment"]["unknown"]:
        block("deployment-source-binding", "deployment",
              "Running deployments include source conflicts or unknown exact revisions.")
    if d["credentials"]["consumer_mapping"] == "UNKNOWN":
        block("credential-consumer-mapping", "credentials",
              "Credential consumers are not yet fully mapped to stable component identities.")
    if d["credentials"]["permission_drift_observations"]:
        block("credential-permission-drift", "credentials",
              "Credential metadata shows unresolved permission drift.")
    if d["recovery"]["status"] != "PASS":
        block("restore-proof", "recovery",
              "Observed backups do not yet have independent restore/recoverability proof.")
    if d["runtime"]["status"] != "PASS":
        block("runtime-topology-disposition", "runtime",
              "Declared and running control-plane topology are not yet reconciled.")
    if d["routes"]["unresolved"]:
        block("route-disposition", "routes",
              "Unresolved public routes still require desired/superseded/retired disposition.")
    if d["cloud"]["aftergraph_adjacent_unclassified"]:
        block("cloud-ownership", "cloud",
              "Aftergraph-adjacent cloud resources remain ownership-unclassified.")

    return {
        "schema_version": "roro-coverage-gate/0.1",
        "gate": "CONSOLIDATION_MIGRATION",
        "as_of": report["as_of"],
        "decision": "READY" if not blockers else "NOT_READY",
        "blockers": blockers,
        "rule": "Consequential migration fails closed while required reality dimensions contain unresolved blockers.",
    }


def main() -> int:
    report = build_report()
    gate = build_gate(report)
    REPORT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    GATE.write_text(json.dumps(gate, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        "R.O.R.O. Survey generated: "
        f"decision={gate['decision']} blockers={len(gate['blockers'])}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
