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

    def test_diffs_preserve_residual_drift_without_inventing_conflict(self) -> None:
        data = json.loads((REALITY / "reality-diffs.json").read_text())
        states = {item["classification"] for item in data["diffs"]}
        self.assertEqual(states, {"DRIFT"})
        self.assertEqual(data["summary"]["conflicting"], 0)
        self.assertEqual(data["summary"]["unknown"], 0)
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

    def test_source_topology_gate_is_ready_only_for_its_bounded_scope(self) -> None:
        data = json.loads((REALITY / "coverage-gate.json").read_text())
        self.assertEqual(data["schema_version"], "roro-coverage-gate/0.1")
        self.assertEqual(data["gate"], "SOURCE_TOPOLOGY_CONSOLIDATION")
        self.assertEqual(data["scope"], "SOURCE_TOPOLOGY_ONLY")
        self.assertEqual(data["decision"], "READY")
        self.assertEqual(data["blockers"], [])
        self.assertIn("RUNTIME_MIGRATION", data["excluded_migrations"])
        self.assertIn("STATE_MIGRATION", data["excluded_migrations"])
        self.assertIn("CREDENTIAL_MIGRATION", data["excluded_migrations"])



    def test_residual_reality_diffs_remain_visible_as_drift(self) -> None:
        diffs = json.loads((REALITY / "reality-diffs.json").read_text())
        self.assertEqual(diffs["summary"]["conflicting"], 0)
        self.assertEqual(diffs["summary"]["unknown"], 0)
        self.assertGreater(diffs["summary"]["total"], 0)
        self.assertEqual({x["classification"] for x in diffs["diffs"]}, {"DRIFT"})
        report = json.loads((REALITY / "coverage-report.json").read_text())
        self.assertEqual(report["dimensions"]["reality_diff"]["status"], "PARTIAL")

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
        self.assertEqual(by_service["works-api.service"]["status"], "CANONICAL_COMPOSITE_LAG")
        self.assertEqual(by_service["works-api.service"]["origin_relation"], "CANONICAL_ARTIFACT_LEGACY_WORKTREE")
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
        self.assertNotIn("deployment-source-binding", blocker_ids)

    def test_runtime_disposition_contract_registered(self) -> None:
        register = (ROOT / "docs/cross-repo-contracts.md").read_text(encoding="utf-8")
        self.assertIn("`roro-runtime-topology-disposition/0.1`", register)

    def test_runtime_mismatch_is_drift_after_bounded_disposition(self) -> None:
        diffs = json.loads((REALITY / "reality-diffs.json").read_text())
        item = next(x for x in diffs["diffs"] if x["subject"] == "runtime://vds-control-plane")
        self.assertEqual(item["classification"], "DRIFT")
        self.assertEqual(item["epistemic_status"], "OBSERVED")




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
        for contract in ("roro-route-disposition/0.1", "roro-recovery-verification/0.1", "roro-source-binding-disposition/0.1"):
            self.assertIn(f"`{contract}`", register)



    def test_works_clean_build_clears_hard_conflict_but_records_legacy_workspace(self) -> None:
        observations = json.loads((REALITY / "deployment-observations.json").read_text())
        works = next(x for x in observations["observations"] if x["service"] == "works-api.service")
        self.assertFalse(works["build_provenance"]["vcs_modified"])
        self.assertEqual(works["build_provenance"]["vcs_revision"], works["canonical_head_at_source_snapshot"])
        self.assertEqual(works["working_directory_provenance"]["relation"], "LEGACY_NON_CANONICAL_WORKTREE")
        self.assertTrue(works["working_directory_provenance"]["runtime_files_match_canonical_head"])
        diffs = json.loads((REALITY / "deployment-source-diffs.json").read_text())
        binding = next(x for x in diffs["bindings"] if x["service"] == "works-api.service")
        self.assertEqual(binding["status"], "CANONICAL_COMPOSITE_LAG")

class SemanticCoverageTests(unittest.TestCase):
    def test_source_coverage_uses_manifest_or_declared_semantics(self) -> None:
        report = json.loads((REALITY / "coverage-report.json").read_text())
        source = report["dimensions"]["source"]
        self.assertEqual(source["semantic_coverage_repositories"], 31)
        self.assertEqual(source["semantic_uncovered_repositories"], 0)
        declarations = json.loads((REALITY / "semantic-declarations.json").read_text())
        self.assertEqual(declarations["uncovered_repositories"], [])
        self.assertTrue(declarations["policy"]["repository_is_not_component"])

class FinalRealityDispositionTests(unittest.TestCase):
    def test_source_binding_dispositions_resolve_brand_vendor_copy(self) -> None:
        data = json.loads((REALITY / "source-binding-dispositions.json").read_text())
        brand = next(x for x in data["dispositions"] if x["component_id"] == "ag:component:brand")
        self.assertEqual(brand["disposition"], "VENDORED_PROJECTION")
        self.assertEqual(brand["canonical_source"], "Aftergraph/brand:.")
        diffs = json.loads((REALITY / "reality-diffs.json").read_text())
        self.assertFalse(any(x["subject"] == "ag:component:brand" and x["classification"] == "UNKNOWN" for x in diffs["diffs"]))

    def test_declared_semantics_remove_manifest_only_unknowns(self) -> None:
        diffs = json.loads((REALITY / "reality-diffs.json").read_text())
        reasons = {x["reason"] for x in diffs["diffs"]}
        self.assertNotIn("no_explicit_semantic_component_manifest_in_source_bootstrap", reasons)

    def test_data_recovery_proof_removes_works_recovery_unknown(self) -> None:
        diffs = json.loads((REALITY / "reality-diffs.json").read_text())
        self.assertFalse(any(x["subject"] == "recovery://works-backup.service" for x in diffs["diffs"]))

    def test_gate_unknown_policy_is_scoped_not_global(self) -> None:
        report = json.loads((REALITY / "coverage-report.json").read_text())
        self.assertTrue(report["policy"]["unknowns_fail_closed_within_required_dimensions"])
        self.assertNotIn("unknowns_fail_closed_for_consequential_migration", report["policy"])
        gate = json.loads((REALITY / "coverage-gate.json").read_text())
        self.assertEqual(gate["required_dimensions"], ["source", "deployment", "credentials", "routes"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
