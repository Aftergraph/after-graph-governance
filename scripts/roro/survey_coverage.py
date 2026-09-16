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
    semantic_declarations = load("semantic-declarations.json")
    operational = load("operational-reality.json")
    operational_gaps = load("operational-reality-gaps.json")
    deployments = load("deployment-source-diffs.json")
    cloud = load("cloud-resource-classification.json")
    recovery = load("recovery-mechanisms.json")
    recovery_verifications = load("recovery-verifications.json")
    credential_map = load("credential-consumer-bindings.json")
    route_dispositions = load("route-dispositions.json")
    runtime_disposition = load("runtime-topology-disposition.json")
    diffs = load("reality-diffs.json")

    repos = registry["repositories"]
    no_manifest = [g for g in source_gaps["gaps"]
                   if g["reason"] == "no_explicit_semantic_component_manifest_in_source_bootstrap"]
    semantic_uncovered = semantic_declarations["uncovered_repositories"]
    semantic_covered = len(repos) - len(semantic_uncovered)
    dep_bindings = deployments["bindings"]
    exact_deployments = [b for b in dep_bindings if b.get("observed_deployed_revision")]
    dep_conflicts = [b for b in dep_bindings if b["status"] == "CONFLICTING"]
    dep_unknown = [b for b in dep_bindings if b["status"] == "UNKNOWN"]

    routes = operational["route_summary"]["routes"]
    resolved_routes = [r for r in routes if r["dns_state"] == "RESOLVED"]
    blocking_route_dispositions = [
        r for r in route_dispositions["routes"]
        if r["disposition"] in {"CONFLICTING_DESIRED_STATE", "UNKNOWN"}
    ]
    unknown_cloud = [r for r in cloud["resources"] if r["epistemic_status"] == "UNKNOWN"]
    adjacent_cloud = [r for r in cloud["resources"]
                      if r["owner_class"] == "AFTERGRAPH_ADJACENT_UNCLASSIFIED"]
    recovery_by_service = {v["service"]: v for v in recovery_verifications["verifications"]}
    verified_recovery = [
        m for m in recovery["mechanisms"]
        if recovery_by_service.get(m["service"], {}).get("verdict") == "RECOVERABLE_VERIFIED"
    ]
    data_verified_recovery = [
        m for m in recovery["mechanisms"]
        if recovery_by_service.get(m["service"], {}).get("verdict") == "DATA_RECOVERY_VERIFIED"
    ]
    recovery_proven = verified_recovery + data_verified_recovery

    dimensions = {
        "source": dimension(
            "PARTIAL" if semantic_uncovered else "PASS",
            observed=semantic_covered,
            total=len(repos),
            metric="semantic_manifest_or_declared_role_coverage",
            exact_repo_heads=len(repos),
            exact_head_coverage=1.0 if repos else None,
            semantic_manifest_gaps=len(no_manifest),
            semantic_coverage_repositories=semantic_covered,
            semantic_uncovered_repositories=len(semantic_uncovered),
            uncovered_repository_refs=semantic_uncovered,
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
            "BLOCKED" if blocking_route_dispositions else "PASS",
            observed=len(resolved_routes),
            total=len(routes),
            metric="route_disposition_coverage",
            unresolved=len(routes) - len(resolved_routes),
            blocking_dispositions=len(blocking_route_dispositions),
            dispositions_total=len(route_dispositions["routes"]),
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
            "BLOCKED" if operational["credential_summary"]["permission_drift_observations"] else "PARTIAL",
            consumer_mapping="PARTIAL" if credential_map["bindings"] else "UNKNOWN",
            mapped_bindings=len(credential_map["bindings"]),
            unresolved_groups=len(credential_map["unresolved"]),
            values_collected=False,
            snapshot_sprawl_observed=operational["credential_summary"]["lenovo_backup_or_snapshot_env_files"],
            permission_drift_observations=operational["credential_summary"]["permission_drift_observations"],
        ),
    }

    dimensions.update({
        "recovery": dimension(
            "BLOCKED" if len(recovery_proven) != len(recovery["mechanisms"]) else "PASS",
            observed=len(recovery_proven),
            total=len(recovery["mechanisms"]),
            metric="state_recovery_proof_coverage",
            backup_present=sum(m["recoverability"] == "BACKUP_PRESENT" for m in recovery["mechanisms"]),
            verified_restores=len(verified_recovery),
            data_recovery_verified=len(data_verified_recovery),
            recovery_proof_coverage=ratio(len(recovery_proven), len(recovery["mechanisms"])),
        ),
        "runtime": dimension(
            "PARTIAL" if runtime_disposition["disposition"] == "TRANSITIONAL_ACCEPTED" else "BLOCKED",
            active_services=operational["runtime_summary"]["active_services"],
            containers=operational["runtime_summary"]["containers"],
            self_hosted_runner_services=operational["runtime_summary"]["self_hosted_runner_services"],
            disposition=runtime_disposition["disposition"],
            disposition_epistemic_status=runtime_disposition["epistemic_status"],
            blocking=runtime_disposition["disposition"] != "TRANSITIONAL_ACCEPTED",
            target_architecture_claim=runtime_disposition["target_architecture_claim"],
            authorizes_runtime_migration=runtime_disposition["authorizes_runtime_migration"],
        ),
        "reality_diff": dimension(
            "BLOCKED" if diffs["summary"]["conflicting"] else ("PARTIAL" if diffs["summary"]["unknown"] or diffs["summary"]["total"] else "PASS"),
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
            "unknowns_fail_closed_within_required_dimensions": True,
            "gate_scope_does_not_imply_global_migration_readiness": True,
        },
    }


def build_gate(report: dict[str, Any]) -> dict[str, Any]:
    d = report["dimensions"]
    blockers: list[dict[str, str]] = []
    required_dimensions = ["source", "deployment", "credentials", "routes"]
    excluded_dimensions = ["runtime", "recovery", "cloud", "reality_diff"]

    def block(blocker_id: str, dimension_name: str, reason: str) -> None:
        blockers.append({"id": blocker_id, "dimension": dimension_name, "reason": reason})

    if d["source"]["semantic_uncovered_repositories"]:
        block("semantic-component-coverage", "source",
              "Some live repositories lack both an explicit semantic source manifest and a governance semantic declaration.")
    if d["deployment"]["conflicts"] or d["deployment"]["unknown"]:
        block("deployment-source-binding", "deployment",
              "Running deployments include source conflicts or unknown exact revisions.")
    if d["credentials"]["consumer_mapping"] == "UNKNOWN":
        block("credential-consumer-mapping", "credentials",
              "Credential consumers are not mapped sufficiently for source/topology consolidation analysis.")
    if d["credentials"]["permission_drift_observations"]:
        block("credential-permission-drift", "credentials",
              "Credential metadata shows unresolved active permission drift.")
    if d["routes"]["blocking_dispositions"]:
        block("route-disposition", "routes",
              "At least one observed route has conflicting or unknown desired-state disposition.")

    return {
        "schema_version": "roro-coverage-gate/0.1",
        "gate": "SOURCE_TOPOLOGY_CONSOLIDATION",
        "as_of": report["as_of"],
        "decision": "READY" if not blockers else "NOT_READY",
        "scope": "SOURCE_TOPOLOGY_ONLY",
        "required_dimensions": required_dimensions,
        "excluded_dimensions": excluded_dimensions,
        "excluded_migrations": ["RUNTIME_MIGRATION", "STATE_MIGRATION", "CREDENTIAL_MIGRATION", "AUTHORITY_MIGRATION", "PRODUCTION_CUTOVER"],
        "blockers": blockers,
        "rule": "Source/topology consolidation may proceed only when required dimensions are clear. READY does not authorize runtime, state, credential, authority, or production cutover migration.",
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
