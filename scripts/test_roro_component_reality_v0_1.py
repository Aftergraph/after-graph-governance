#!/usr/bin/env python3
"""Conformance tests for the R.O.R.O. component-reality bootstrap.

Run: python3 scripts/test_roro_component_reality_v0_1.py
The suite is stdlib-only and uses synthetic source data for deterministic tests.
"""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACTS = ROOT / "docs/contracts/roro/0.1"
REGISTRY = ROOT / "docs/system-reality/component-registry.json"
LINEAGE = ROOT / "docs/system-reality/component-lineage.json"
GAPS = ROOT / "docs/system-reality/reality-gaps.json"

SCHEMAS = {
    "observation": CONTRACTS / "observation.schema.json",
    "component": CONTRACTS / "component.schema.json",
    "source-binding": CONTRACTS / "source-binding.schema.json",
    "reality-facet": CONTRACTS / "reality-facet.schema.json",
    "reality-diff": CONTRACTS / "reality-diff.schema.json",
}
def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def manifest(name: str, description: str = "", deps: dict | None = None) -> dict:
    return {
        "path": "packages/example/package.json",
        "content": {
            "name": name,
            "description": description,
            "dependencies": deps or {},
        },
    }


class RoroSchemaTests(unittest.TestCase):
    def test_required_schema_files_exist_and_parse(self) -> None:
        for name, path in SCHEMAS.items():
            with self.subTest(schema=name):
                self.assertTrue(path.is_file(), path)
                obj = json.loads(path.read_text(encoding="utf-8"))
                self.assertEqual(obj["$schema"], "https://json-schema.org/draft/2020-12/schema")
                self.assertIn("$id", obj)

    def test_component_id_is_stable_semantic_identity(self) -> None:
        schema = json.loads(SCHEMAS["component"].read_text(encoding="utf-8"))
        component_id = schema["properties"]["component_id"]
        self.assertEqual(component_id["pattern"], r"^ag:[a-z0-9][a-z0-9:-]*$")
        self.assertNotIn("repository", schema["required"])
        self.assertNotIn("path", schema["required"])
    def test_reality_vocabularies_are_explicit(self) -> None:
        schema = json.loads(SCHEMAS["reality-facet"].read_text(encoding="utf-8"))
        self.assertEqual(
            set(schema["$defs"]["reality_facet"]["enum"]),
            {"DECLARED", "CANONICAL", "DESIRED", "INSTALLED", "CONFIGURED",
             "RUNNING", "REACHABLE", "HEALTHY", "VERIFIED", "RECOVERABLE"},
        )
        self.assertEqual(
            set(schema["$defs"]["epistemic_status"]["enum"]),
            {"VERIFIED", "OBSERVED", "INFERRED", "DECLARED", "PROPOSED",
             "STALE", "CONFLICTING", "UNKNOWN"},
        )

    def test_source_binding_requires_exact_revision(self) -> None:
        schema = json.loads(SCHEMAS["source-binding"].read_text(encoding="utf-8"))
        props = schema["properties"]
        self.assertEqual(props["revision"]["pattern"], r"^[0-9a-f]{40}$")
        self.assertIn("repository", schema["required"])
        self.assertIn("path", schema["required"])
        self.assertIn("revision", schema["required"])

    def test_roro_contract_family_is_registered_as_experimental(self) -> None:
        register = (ROOT / "docs/cross-repo-contracts.md").read_text(encoding="utf-8")
        for contract in (
            "roro-observation/0.1", "roro-component/0.1", "roro-source-binding/0.1",
            "roro-reality-facet/0.1", "roro-reality-diff/0.1",
        ):
            self.assertIn(f"`{contract}`", register)


class DiscoveryUnitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.discovery = load_module(
            "roro_discover_components",
            ROOT / "scripts/roro/discover_components.py",
        )
        cls.lineage = load_module(
            "roro_reconcile_lineage",
            ROOT / "scripts/roro/reconcile_lineage.py",
        )
    def test_aftergraph_package_becomes_semantic_component(self) -> None:
        repo = {
            "full_name": "Aftergraph/runtime",
            "head_sha": "a" * 40,
            "default_branch": "main",
            "manifests": [manifest("@aftergraph/mission-graph", "Mission execution graph")],
        }
        components = self.discovery.discover_components([repo], observed_at="2026-09-16T00:00:00Z")
        self.assertEqual(len(components), 1)
        self.assertEqual(components[0]["component_id"], "ag:component:mission-graph")
        binding = components[0]["source_bindings"][0]
        self.assertEqual(binding["repository"], "Aftergraph/runtime")
        self.assertEqual(binding["revision"], "a" * 40)

    def test_legacy_avc_package_does_not_claim_canonical_identity(self) -> None:
        repo = {
            "full_name": "Aftergraph/autonomous-venture-company",
            "head_sha": "b" * 40,
            "default_branch": "main",
            "manifests": [manifest("@avc/mission-graph")],
        }
        components = self.discovery.discover_components([repo], observed_at="2026-09-16T00:00:00Z")
        self.assertEqual(components[0]["component_id"], "ag:legacy:avc:mission-graph")
        self.assertEqual(components[0]["epistemic_status"], "OBSERVED")

    def test_explicit_migration_is_partial_while_legacy_source_exists(self) -> None:
        legacy = manifest("@avc/mission-graph")
        legacy["repository"] = "Aftergraph/autonomous-venture-company"
        target = manifest(
            "@aftergraph/mission-graph",
            "Mission graph (migrated from @avc/mission-graph, Wave 6)",
        )
        target["repository"] = "Aftergraph/runtime"
        records = self.lineage.reconcile_lineage([legacy, target])
        record = next(r for r in records if r["legacy_package"] == "@avc/mission-graph")
        self.assertEqual(record["status"], "PARTIALLY_MIGRATED")
        self.assertEqual(record["target_package"], "@aftergraph/mission-graph")
        self.assertTrue(record["evidence_refs"])
    def test_name_match_without_migration_evidence_is_duplicate_not_migrated(self) -> None:
        legacy = manifest("@avc/foo")
        legacy["repository"] = "Aftergraph/autonomous-venture-company"
        target = manifest("@aftergraph/foo", "Independent implementation")
        target["repository"] = "Aftergraph/runtime"
        records = self.lineage.reconcile_lineage([legacy, target])
        record = next(r for r in records if r["legacy_package"] == "@avc/foo")
        self.assertEqual(record["status"], "DUPLICATED")

    def test_no_manifest_consumer_does_not_prove_orphaned(self) -> None:
        legacy = manifest("@avc/only-here")
        legacy["repository"] = "Aftergraph/autonomous-venture-company"
        records = self.lineage.reconcile_lineage([legacy])
        record = records[0]
        self.assertEqual(record["status"], "UNKNOWN")
        self.assertEqual(record["evidence_refs"], [])


class GitHubDiscoveryParserTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.github = load_module(
            "roro_discover_github",
            ROOT / "scripts/roro/discover_github.py",
        )

    def test_package_json_parser_merges_dependency_classes(self) -> None:
        raw = json.dumps({
            "name": "@aftergraph/x",
            "description": "x",
            "dependencies": {"@avc/a": "*"},
            "devDependencies": {"@avc/b": "*"},
            "peerDependencies": {"@avc/c": "*"},
        }).encode()
        parsed = self.github.parse_manifest("package.json", raw)
        self.assertEqual(parsed["name"], "@aftergraph/x")
        self.assertEqual(set(parsed["dependencies"]), {"@avc/a", "@avc/b", "@avc/c"})

    def test_pyproject_and_go_module_parsers_extract_names(self) -> None:
        pyproject = b'[project]\nname = "aftergraph-demo"\ndescription = "demo"\n'
        self.assertEqual(self.github.parse_manifest("pyproject.toml", pyproject)["name"], "aftergraph-demo")
        gomod = b"module github.com/Aftergraph/demo\n\ngo 1.24\n"
        self.assertEqual(self.github.parse_manifest("go.mod", gomod)["name"], "github.com/Aftergraph/demo")


class GeneratedArtifactTests(unittest.TestCase):
    def test_checked_in_artifacts_exist(self) -> None:
        for path in (REGISTRY, LINEAGE, GAPS):
            self.assertTrue(path.is_file(), path)

    def test_registry_has_unique_component_ids_and_40_char_source_shas(self) -> None:
        registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
        ids = [item["component_id"] for item in registry["components"]]
        self.assertEqual(len(ids), len(set(ids)))
        for component in registry["components"]:
            for binding in component["source_bindings"]:
                self.assertRegex(binding["revision"], r"^[0-9a-f]{40}$")

    def test_live_scope_is_not_hard_coded_to_topology(self) -> None:
        registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
        names = {r["full_name"] for r in registry["repositories"]}
        self.assertIn("Aftergraph/war-room", names)
        self.assertIn("Aftergraph/rendetalje", names)
    def test_lineage_states_are_bounded(self) -> None:
        lineage = json.loads(LINEAGE.read_text(encoding="utf-8"))
        allowed = {
            "MIGRATED", "ACTIVE_LEGACY", "DUPLICATED",
            "PARTIALLY_MIGRATED", "ORPHANED", "UNKNOWN",
        }
        for record in lineage["lineage"]:
            self.assertIn(record["status"], allowed)
            if record["status"] != "UNKNOWN":
                self.assertTrue(record["evidence_refs"])

    def test_gaps_are_explicit_records(self) -> None:
        gaps = json.loads(GAPS.read_text(encoding="utf-8"))
        self.assertEqual(gaps["schema_version"], "roro-reality-gaps/0.1")
        self.assertIsInstance(gaps["gaps"], list)
        for gap in gaps["gaps"]:
            self.assertIn("subject", gap)
            self.assertIn("reason", gap)
            self.assertIn("epistemic_status", gap)
            self.assertEqual(gap["epistemic_status"], "UNKNOWN")

    def test_validator_accepts_generated_artifacts(self) -> None:
        validator = ROOT / "scripts/roro/validate_registry.py"
        result = subprocess.run(
            [sys.executable, str(validator)],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("R.O.R.O. registry OK", result.stdout)


class OperationalRealityTests(unittest.TestCase):
    def test_operational_contracts_exist(self) -> None:
        base = ROOT / "docs/contracts/roro/0.1"
        for name in (
            "deployment-binding.schema.json",
            "credential-binding.schema.json",
            "state-store.schema.json",
            "route-observation.schema.json",
        ):
            path = base / name
            self.assertTrue(path.is_file(), path)
            json.loads(path.read_text(encoding="utf-8"))

    def test_operational_snapshot_is_sanitized_and_typed(self) -> None:
        path = ROOT / "docs/system-reality/operational-reality.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(data["schema_version"], "roro-operational-reality/0.1")
        self.assertEqual(data["credential_summary"]["values_collected"], False)
        self.assertGreaterEqual(data["runtime_summary"]["active_services"], 1)
        self.assertGreaterEqual(data["cloud_summary"]["pages_projects"], 1)
        raw = path.read_text(encoding="utf-8")
        self.assertNotIn("C:\\Users\\", raw)
        self.assertNotIn("/root/agent-workforce/data/gateway.env", raw)

    def test_operational_gaps_encode_observed_drift(self) -> None:
        path = ROOT / "docs/system-reality/operational-reality-gaps.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        types = {item["type"] for item in data["gaps"]}
        self.assertIn("DECLARED_RUNTIME_MISMATCH", types)
        self.assertNotIn("CREDENTIAL_PERMISSION_DRIFT", types)
        self.assertIn("CREDENTIAL_SNAPSHOT_SPRAWL", types)
        self.assertIn("RECOVERY_PROOF_UNKNOWN", types)
        self.assertIn("PUBLIC_ROUTE_ABSENT", types)

    def test_route_snapshot_preserves_absence_vs_unobserved(self) -> None:
        data = json.loads((ROOT / "docs/system-reality/operational-reality.json").read_text(encoding="utf-8"))
        routes = {item["host"]: item for item in data["route_summary"]["routes"]}
        self.assertEqual(routes["work-intelligence.aftergraph.org"]["https_status"], 200)
        self.assertEqual(routes["wie.aftergraph.org"]["dns_state"], "UNRESOLVED")
        self.assertEqual(routes["studio.aftergraph.org"]["dns_state"], "UNRESOLVED")
        self.assertEqual(routes["war-room.aftergraph.org"]["dns_state"], "UNRESOLVED")

class OperationalReconciliationTests(unittest.TestCase):
    def test_deployment_source_diffs_are_explicit(self) -> None:
        path = ROOT / "docs/system-reality/deployment-source-diffs.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        by_service = {item["service"]: item for item in data["bindings"]}
        self.assertIn("works-api.service", by_service)
        self.assertEqual(by_service["works-api.service"]["canonical_repository"], "Aftergraph/works-execution")
        self.assertEqual(by_service["works-api.service"]["status"], "CANONICAL_COMPOSITE_LAG")
        for item in data["bindings"]:
            self.assertIn(item["status"], {"VERIFIED_MATCH", "OBSERVED_MATCH", "CANONICAL_LAG", "CANONICAL_COMPOSITE_LAG", "CONFLICTING", "UNKNOWN"})

    def test_cloud_resources_are_classified_without_overclaiming(self) -> None:
        path = ROOT / "docs/system-reality/cloud-resource-classification.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(data["resource_counts"]["pages"], 11)
        self.assertEqual(data["resource_counts"]["d1"], 7)
        self.assertTrue(any(x["owner_class"] == "LEGACY_AVC" for x in data["resources"]))
        self.assertTrue(any(x["owner_class"] == "COHOSTED_OTHER_OR_UNKNOWN" for x in data["resources"]))
        for item in data["resources"]:
            self.assertIn(item["epistemic_status"], {"OBSERVED", "INFERRED", "UNKNOWN"})

    def test_recovery_mechanisms_do_not_equate_backup_with_restore(self) -> None:
        path = ROOT / "docs/system-reality/recovery-mechanisms.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        for item in data["mechanisms"]:
            self.assertIn(item["recoverability"], {"BACKUP_PRESENT", "UNKNOWN", "RECOVERABLE_VERIFIED"})
            if item["recoverability"] == "RECOVERABLE_VERIFIED":
                self.assertTrue(item.get("restore_evidence_refs"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
