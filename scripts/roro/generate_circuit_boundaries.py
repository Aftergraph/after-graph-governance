#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REALITY = ROOT / "docs/system-reality"
BOUNDARY = REALITY / "component-boundary-analysis.json"
OUT = REALITY / "circuit-boundary-model.json"

MACRO_FAMILIES = ["SIGHTLINE", "HELM", "COVENANT", "DRIVE", "WITNESS", "REFINERY"]
SUPPORT_FAMILIES = [
    ("COMMONS", "Shared foundation; does not grant authority."),
    ("DOMAIN", "Domain semantics remain bounded from platform authority."),
    ("EXPERIENCE", "Experience surfaces do not become truth or execution owners."),
    ("LOOM", "Capability supply does not itself authorize execution."),
    ("COVENANT_SUPPORT", "Semantic proximity to policy/authority does not grant authority."),
]

ALLOWED = [
    ("SIGHTLINE", "HELM", "OBSERVE_THEN_REASON"),
    ("HELM", "COVENANT", "DECISION_THEN_ADMISSION"),
    ("HELM", "REFINERY", "HYPOTHESIS_TO_EXPERIMENT"),
    ("REFINERY", "COVENANT", "CANDIDATE_REQUIRES_ADMISSION"),
    ("COVENANT", "DRIVE", "ADMITTED_EXECUTION"),
    ("DRIVE", "WITNESS", "EXECUTION_TO_INDEPENDENT_VERIFICATION"),
    ("WITNESS", "SIGHTLINE", "VERDICT_TO_REOBSERVATION"),
    ("WITNESS", "REFINERY", "VERIFIED_OUTCOME_TO_LEARNING"),
]

FORBIDDEN = [
    ("SIGHTLINE", "DRIVE", "COVENANT_REQUIRED", "Observation cannot directly trigger consequential execution."),
    ("HELM", "DRIVE", "COVENANT_REQUIRED", "Reasoning cannot bypass Covenant admission."),
    ("REFINERY", "DRIVE", "COVENANT_REQUIRED", "A learned candidate cannot self-promote into execution."),
    ("DRIVE", "REFINERY", "VERIFIED_OUTCOME_REQUIRED", "Learning must consume verified outcomes, not raw executor success."),
    ("WITNESS", "DRIVE", "VERIFIER_CANNOT_EXECUTE", "Independent verification cannot become the executor it verifies."),
    ("DRIVE", "HELM", "REOBSERVATION_REQUIRED", "Execution feedback must be re-observed before becoming cognition input."),
]


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def build():
    evidence = load(BOUNDARY)
    observed = [
        {
            "from_family": row["source_family"],
            "to_family": row["target_family"],
            "edge_count": row["edge_count"],
            "evidence_class": "OBSERVED_DEPENDENCY",
        }
        for row in evidence["family_edges"]
    ]
    observed.sort(key=lambda x: (x["from_family"], x["to_family"]))
    return {
        "schema_version": "circuit-boundary-model/0.1",
        "source_snapshot_generated_at": evidence["source_snapshot_generated_at"],
        "policy": {
            "dependency_graph_is_not_circuit_flow": True,
            "circuit_compiler_has_authority": False,
            "circuit_owns_durable_state": False,
            "circuit_validator_grants_execution": False,
            "roro_has_circuit_authority": False,
            "consequential_drive_requires_covenant": True,
            "executor_cannot_self_verify": True,
            "valid_composition_is_not_execution_authorization": True,
        },
        "macro_families": MACRO_FAMILIES,
        "semantic_support_families": [
            {"family": family, "grants_authority": False, "boundary_note": note}
            for family, note in SUPPORT_FAMILIES
        ],
        "allowed_edges": [
            {"from_family": a, "to_family": b, "rule_id": rule}
            for a, b, rule in ALLOWED
        ],
        "forbidden_edges": [
            {"from_family": a, "to_family": b, "rule_id": rule, "reason": reason}
            for a, b, rule, reason in FORBIDDEN
        ],
        "observed_dependency_coupling": observed,
        "native_boundary_refs": {
            "COVENANT": ["Aftergraph/aie", "Aftergraph/trust-gateway"],
            "DRIVE": ["Aftergraph/runtime", "Aftergraph/works-execution", "Aftergraph/relay"],
            "WITNESS": ["Aftergraph/sentinel", "Aftergraph/continuum"],
            "SIGHTLINE": ["Aftergraph/wi-backend", "R.O.R.O."],
        },
    }


def main():
    payload = build()
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        f"circuit boundary model: macro={len(payload['macro_families'])} "
        f"allowed={len(payload['allowed_edges'])} forbidden={len(payload['forbidden_edges'])} "
        f"observed_couplings={len(payload['observed_dependency_coupling'])}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
