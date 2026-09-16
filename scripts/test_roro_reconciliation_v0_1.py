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
        self.assertIn("CONFLICT", states)
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
        self.assertNotIn("restore-proof", blocker_ids)
        self.assertNotIn("credential-permission-drift", blocker_ids)
        self.assertIn("deployment-source-binding", blocker_ids)


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


class SchemaAlignmentTests(unittest.TestCase):
    def test_reality_diff_records_match_registered_vocabulary(self) -> None:
        schema = json.loads((CONTRACTS / "reality-diff.schema.json").read_text())
        allowed = set(schema["properties"]["classification"]["enum"])
        allowed_keys = set(schema["properties"])
        required = set(schema["required"])
        data = json.loads((REALITY / "reality-diffs.json").read_text())
        for item in data["diffs"]:
            self.assertTrue(required <= set(item), item)
            self.assertTrue(set(item) <= allowed_keys, item)
            self.assertIn(item["classification"], allowed)
            self.assertIn(item["epistemic_status"], {
                "VERIFIED", "OBSERVED", "INFERRED", "DECLARED", "PROPOSED",
                "STALE", "CONFLICTING", "UNKNOWN",
            })

    def test_deployment_reconciliation_distinguishes_lag_from_conflict(self) -> None:
        data = json.loads((REALITY / "deployment-source-diffs.json").read_text())
        by_service = {item["service"]: item for item in data["bindings"]}
        self.assertEqual(len(by_service), 8)
        self.assertEqual(by_service["works-api.service"]["status"], "CONFLICTING")
        self.assertEqual(by_service["works-api.service"]["origin_relation"], "NON_CANONICAL_REMOTE")
        for service in ("tg-gateway.service", "studio-backend.service", "wi-backend.service",
                        "aftergraph-relay.service", "aftergraph-relay-eg-mcp.service"):
            self.assertEqual(by_service[service]["status"], "CANONICAL_LAG", service)
        self.assertEqual(by_service["wi-frontend.service"]["status"], "CANONICAL_COMPOSITE_LAG")
        self.assertEqual(by_service["avc-runner-bridge.service"]["status"], "OBSERVED_MATCH")


class RuntimeTopologyDispositionTests(unittest.TestCase):
    def test_runtime_topology_has_explicit_bounded_disposition(self) -> None:
        data = json.loads((REALITY / "runtime-topology-disposition.json").read_text())
        self.assertEqual(data["disposition"], "TRANSITIONAL_ACCEPTED")
        self.assertFalse(data["target_architecture_claim"])
        self.assertFalse(data["authorizes_runtime_migration"])
        self.assertIn("source consolidation", data["scope"].lower())

    def test_runtime_disposition_removes_unknown_topology_blocker_only(self) -> None:
        gate = json.loads((REALITY / "coverage-gate.json").read_text())
        blocker_ids = {x["id"] for x in gate["blockers"]}
        self.assertNotIn("runtime-topology-disposition", blocker_ids)
        self.assertIn("deployment-source-binding", blocker_ids)

    def test_runtime_disposition_contract_registered(self) -> None:
        register = (ROOT / "docs/cross-repo-contracts.md").read_text(encoding="utf-8")
        self.assertIn("`roro-runtime-topology-disposition/0.1`", register)

    def test_runtime_mismatch_is_drift_after_bounded_disposition(self) -> None:
        diffs = json.loads((REALITY / "reality-diffs.json").read_text())
        item = next(x for x in diffs["diffs"] if x["subject"] == "runtime://vds-control-plane")
        self.assertEqual(item["classification"], "DRIFT")
        self.assertEqual(item["epistemic_status"], "OBSERVED")


if __name__ == "__main__":
    unittest.main(verbosity=2)


class BlockerReductionTests(unittest.TestCase):
    def test_credential_mapping_is_partial_not_unknown(self) -> None:
        report = json.loads((REALITY / "coverage-report.json").read_text())
        self.assertEqual(report["dimensions"]["credentials"]["consumer_mapping"], "PARTIAL")
        self.assertGreaterEqual(report["dimensions"]["credentials"]["mapped_bindings"], 19)

    def test_only_declared_route_conflict_blocks(self) -> None:
        report = json.loads((REALITY / "coverage-report.json").read_text())
        self.assertEqual(report["dimensions"]["routes"]["blocking_dispositions"], 0)
        dispositions = json.loads((REALITY / "route-dispositions.json").read_text())
        by_host = {x["host"]: x for x in dispositions["routes"]}
        self.assertEqual(by_host["wie.aftergraph.org"]["disposition"], "SUPERSEDED")
        self.assertTrue(by_host["wie.aftergraph.org"]["source_drift"])
        self.assertEqual(by_host["studio.aftergraph.org"]["disposition"], "NOT_REQUIRED")
        self.assertEqual(by_host["war-room.aftergraph.org"]["disposition"], "NOT_DECLARED_PUBLIC")

    def test_restore_proof_upgrades_only_verified_service(self) -> None:
        report = json.loads((REALITY / "coverage-report.json").read_text())
        recovery = report["dimensions"]["recovery"]
        self.assertEqual(recovery["verified_restores"], 4)
        self.assertEqual(recovery["data_recovery_verified"], 1)
        self.assertEqual(recovery["recovery_proof_coverage"], 1.0)
        self.assertEqual(recovery["status"], "PASS")

    def test_cloud_adjacent_resources_are_classified(self) -> None:
        report = json.loads((REALITY / "coverage-report.json").read_text())
        self.assertEqual(report["dimensions"]["cloud"]["aftergraph_adjacent_unclassified"], 0)

    def test_new_evidence_contracts_are_registered(self) -> None:
        register = (ROOT / "docs/cross-repo-contracts.md").read_text(encoding="utf-8")
        for contract in ("roro-route-disposition/0.1", "roro-recovery-verification/0.1"):
            self.assertIn(f"`{contract}`", register)



    def test_works_dirty_build_remains_hard_conflict(self) -> None:
        observations = json.loads((REALITY / "deployment-observations.json").read_text())
        works = next(x for x in observations["observations"] if x["service"] == "works-api.service")
        self.assertTrue(works["build_provenance"]["vcs_modified"])
        self.assertTrue(works["build_provenance"]["running_binary_matches_disk_binary"])
        diffs = json.loads((REALITY / "deployment-source-diffs.json").read_text())
        binding = next(x for x in diffs["bindings"] if x["service"] == "works-api.service")
        self.assertEqual(binding["status"], "CONFLICTING")
        self.assertIn("modified", binding["reason"].lower())

class SemanticCoverageTests(unittest.TestCase):
    def test_source_coverage_uses_manifest_or_declared_semantics(self) -> None:
        report = json.loads((REALITY / "coverage-report.json").read_text())
        source = report["dimensions"]["source"]
        self.assertEqual(source["semantic_coverage_repositories"], 31)
        self.assertEqual(source["semantic_uncovered_repositories"], 0)
        declarations = json.loads((REALITY / "semantic-declarations.json").read_text())
        self.assertEqual(declarations["uncovered_repositories"], [])
        self.assertTrue(declarations["policy"]["repository_is_not_component"])
