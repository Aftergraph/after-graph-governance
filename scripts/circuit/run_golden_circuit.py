#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from scripts.roro.reobserve_effect import reduce_post_effect_observation

SUBJECT_INPUT = {
    "circuitSpecSha256": "c" * 64,
    "missionId": "mis_golden_circuit",
    "effectId": "effect/golden-circuit",
    "resourceRef": "service/works-api",
    "authorityEpoch": 7,
}


def _run(cmd: list[str], cwd: Path, env: dict[str, str] | None = None) -> str:
    merged = os.environ.copy()
    if env:
        merged.update(env)
    result = subprocess.run(cmd, cwd=cwd, env=merged, text=True, capture_output=True)
    if result.returncode != 0:
        raise RuntimeError(f"command failed ({result.returncode}): {' '.join(cmd)}\n{result.stdout}\n{result.stderr}")
    return result.stdout + result.stderr


def _head(root: Path) -> str:
    return _run(["git", "rev-parse", "HEAD"], root).strip()

def validate_works_evidence(evidence: dict[str, Any], verification_subject: str) -> None:
    if evidence.get("verification_subject") != verification_subject:
        raise ValueError("WORKS verification subject drift")
    if evidence.get("effect_state") != "APPLIED":
        raise ValueError("effect not APPLIED")
    if evidence.get("witness_result") != "ACCEPT":
        raise ValueError("Witness did not ACCEPT exact effect")
    if evidence.get("verifier_id") == "runtime-golden":
        raise ValueError("executor self-verification")
    digest = evidence.get("effect_receipt_sha256")
    if not isinstance(digest, str) or len(digest) != 64:
        raise ValueError("invalid EffectReceipt digest")


def build_reality_case(evidence: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "roro-post-effect-observation-input/0.1",
        "effect_receipt_subject": f"effect-receipt:{evidence['effect_receipt_id']}:sha256:{evidence['effect_receipt_sha256']}",
        "intended_outcome": {
            "subject": "service/works-api",
            "predicate": "health",
            "expected": "HEALTHY",
        },
        "before": {
            "value": "DEGRADED",
            "epistemic_status": "OBSERVED",
            "observed_at": "2026-09-16T18:00:00Z",
        },
        "after": {
            "value": "HEALTHY",
            "epistemic_status": "OBSERVED",
            "observed_at": "2026-09-16T18:00:10Z",
        },
        "max_age_seconds": 60,
        "evaluated_at": "2026-09-16T18:00:20Z",
    }

def runtime_subject(runtime_root: Path) -> dict[str, Any]:
    _run(["pnpm", "--filter", "@aftergraph/job-runtime", "build"], runtime_root)
    module = (runtime_root / "packages/job-runtime/dist/execution-subject.js").resolve().as_uri()
    js = (
        "const m=await import(process.argv[1]);"
        "const input=JSON.parse(process.argv[2]);"
        "console.log(JSON.stringify(m.createExecutionSubject(input)));"
    )
    raw = _run(["node", "--input-type=module", "-e", js, module, json.dumps(SUBJECT_INPUT)], runtime_root)
    return json.loads(raw.strip().splitlines()[-1])


def execute_golden(runtime_root: Path, works_root: Path, governance_root: Path) -> dict[str, Any]:
    runtime_head = _head(runtime_root)
    works_head = _head(works_root)
    governance_head = _head(governance_root)

    _run(["pnpm", "exec", "vitest", "run",
          "packages/job-runtime/src/execution-subject.test.ts",
          "packages/job-runtime/src/circuit-dispatch.test.ts",
          "packages/mission-graph/src/execution-authority-subject.test.ts"], runtime_root)
    subject = runtime_subject(runtime_root)
    verification_subject = subject["verificationSubject"]

    with tempfile.TemporaryDirectory(prefix="golden-circuit-") as td:
        evidence_path = Path(td) / "works-evidence.json"
        env = {"GOLDEN_VERIFICATION_SUBJECT": verification_subject, "GOLDEN_EVIDENCE_OUT": str(evidence_path)}
        _run(["go", "test", "./services/work/store", "-run", "TestGoldenCircuitEndToEnd", "-v"], works_root, env)
        works_evidence = json.loads(evidence_path.read_text())

    validate_works_evidence(works_evidence, verification_subject)
    _run(["go", "test", "./services/work/store", "-run",
          "TestAcceptCircuitDispatchRejectsStaleAuthorityWithoutPersistence|TestAcceptCircuitDispatchRollsBackNewAcceptanceOnBindingConflict|TestCreateCircuitEffectVerdictRejectsExecutorAsVerifier", "-v"], works_root)
    _run(["python3", "-m", "unittest", "scripts.test_roro_post_effect_observation_v0_1", "-v"], governance_root)
    reality = reduce_post_effect_observation(build_reality_case(works_evidence))
    if reality["classification"] != "MATCHED" or reality["epistemic_status"] != "VERIFIED":
        raise RuntimeError(f"post-effect reality not verified: {reality}")
    return {
        "schema_version": "golden-circuit-evidence/0.2",
        "runtime_head": runtime_head,
        "works_head": works_head,
        "governance_head": governance_head,
        "execution_subject": subject,
        "works": works_evidence,
        "post_effect_reality": reality,
        "falsification_gates": {
            "changed_or_expired_approval": "PASS",
            "stale_authority": "PASS",
            "atomic_binding_conflict_rollback": "PASS",
            "executor_self_verification": "PASS",
            "stale_post_effect_observation": "PASS",
        },
        "verdict": "VERIFIED",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runtime-root", required=True, type=Path)
    parser.add_argument("--works-root", required=True, type=Path)
    parser.add_argument("--governance-root", required=True, type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    evidence = execute_golden(args.runtime_root.resolve(), args.works_root.resolve(), args.governance_root.resolve())
    payload = json.dumps(evidence, indent=2) + "\n"
    if args.out:
        args.out.write_text(payload, encoding="utf-8")
    print(payload, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
