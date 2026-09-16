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
    diffs.append({
        "id": diff_id,
        "subject": subject,
        "classification": classification,
        "dimension": dimension,
        "severity": severity,
        "reason": reason,
        "evidence_refs": sorted(set(evidence)),
    })


def build() -> dict[str, Any]:
    diffs: list[dict[str, Any]] = []
    source_gaps = load("reality-gaps.json")
    operational_gaps = load("operational-reality-gaps.json")
    deployments = load("deployment-source-diffs.json")
    recovery = load("recovery-mechanisms.json")

    for gap in source_gaps["gaps"]:
        add(
            diffs,
            diff_id=f"diff:source:{len(diffs)+1}",
            subject=gap["subject"],
            classification="UNKNOWN",
            dimension="SOURCE",
            reason=gap["reason"],
            evidence=[evidence_ref("reality-gaps.json", gap["subject"])],
            severity="MEDIUM",
        )

    for gap in operational_gaps["gaps"]:
        classification = gap.get("epistemic_status", "UNKNOWN")
        if classification not in {"CONFLICTING", "UNKNOWN", "STALE"}:
            classification = "UNKNOWN"
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
            classification=binding["status"],
            dimension="DEPLOYMENT_SOURCE",
            reason=binding["reason"],
            evidence=[evidence_ref("deployment-source-diffs.json", service)],
            severity="HIGH" if binding["status"] == "CONFLICTING" else "MEDIUM",
        )

    for mechanism in recovery["mechanisms"]:
        if mechanism["recoverability"] == "RECOVERABLE_VERIFIED":
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
        "diffs": sorted(diffs, key=lambda item: item["id"]),
        "summary": {
            "total": len(diffs),
            "conflicting": sum(d["classification"] == "CONFLICTING" for d in diffs),
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
