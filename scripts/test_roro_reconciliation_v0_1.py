import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REALITY = ROOT / "docs/system-reality"
CONTRACTS = ROOT / "docs/contracts/roro/0.1"


class RealityDiffEngineTests(unittest.TestCase):
    def test_reality_diff_artifact_exists_and_is_typed(self) -> None:
        path = REALITY / "reality-diffs.json"
        self.assertTrue(path.is_file(), path)
        data = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(data["schema_version"], "roro-reality-diffs/0.1")
        self.assertIsInstance(data["diffs"], list)
        self.assertGreater(len(data["diffs"]), 0)

    def test_diffs_preserve_unknown_and_conflict(self) -> None:
        data = json.loads((REALITY / "reality-diffs.json").read_text())
        states = {item["classification"] for item in data["diffs"]}
        self.assertIn("CONFLICTING", states)
        self.assertIn("UNKNOWN", states)
        for item in data["diffs"]:
            self.assertIn("subject", item)
            self.assertIn("evidence_refs", item)


class SurveyCoverageTests(unittest.TestCase):
    def test_coverage_contract_and_report_exist(self) -> None:
        schema = CONTRACTS / "coverage-report.schema.json"
        report = REALITY / "coverage-report.json"
        self.assertTrue(schema.is_file(), schema)
        self.assertTrue(report.is_file(), report)
        json.loads(schema.read_text(encoding="utf-8"))
        data = json.loads(report.read_text(encoding="utf-8"))
        self.assertEqual(data["schema_version"], "roro-coverage-report/0.1")
        self.assertIn("dimensions", data)
        self.assertIn("source", data["dimensions"])
        self.assertIn("deployment", data["dimensions"])
        self.assertIn("recovery", data["dimensions"])
        self.assertIn("credentials", data["dimensions"])

    def test_migration_gate_fails_closed_on_known_unknowns(self) -> None:
        data = json.loads((REALITY / "coverage-gate.json").read_text())
        self.assertEqual(data["schema_version"], "roro-coverage-gate/0.1")
        self.assertEqual(data["gate"], "CONSOLIDATION_MIGRATION")
        self.assertEqual(data["decision"], "NOT_READY")
        self.assertGreater(len(data["blockers"]), 0)
        blocker_ids = {item["id"] for item in data["blockers"]}
        self.assertIn("restore-proof", blocker_ids)
        self.assertIn("credential-consumer-mapping", blocker_ids)


class ReconciliationCommandTests(unittest.TestCase):
    def test_reconcile_and_survey_commands_are_repeatable(self) -> None:
        for script in ("reconcile_reality.py", "survey_coverage.py"):
            result = subprocess.run(
                [sys.executable, str(ROOT / "scripts/roro" / script)],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


# Contract registration is part of the governance boundary, not optional prose.
class ContractRegistrationTests(unittest.TestCase):
    def test_survey_contracts_are_registered_experimental(self) -> None:
        register = (ROOT / "docs/cross-repo-contracts.md").read_text(encoding="utf-8")
        for contract in ("roro-coverage-report/0.1", "roro-coverage-gate/0.1"):
            self.assertIn(f"`{contract}`", register)

    def test_no_single_overall_reality_score(self) -> None:
        report = json.loads((REALITY / "coverage-report.json").read_text())
        self.assertTrue(report["policy"]["overall_scalar_score_prohibited"])
        self.assertNotIn("score", report)
        self.assertNotIn("overall_score", report)

if __name__ == "__main__":
    unittest.main(verbosity=2)
