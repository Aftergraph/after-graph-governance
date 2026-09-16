import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REALITY = ROOT / "docs/system-reality"
CONTRACTS = ROOT / "docs/contracts/circuit/0.1"
MODEL = REALITY / "circuit-boundary-model.json"
VECTORS = REALITY / "circuit-spec-vectors.json"
RESULTS = REALITY / "circuit-validation-results.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


class CircuitContractTests(unittest.TestCase):
    def test_contracts_are_experimental_and_separate_from_roro_ownership(self):
        register = (ROOT / "docs/cross-repo-contracts.md").read_text(encoding="utf-8")
        self.assertIn("`circuit-spec/0.1`", register)
        self.assertIn("`circuit-validation/0.1`", register)
        self.assertNotIn("`roro-circuit-spec/0.1`", register)
        self.assertNotIn("`roro-circuit-validation/0.1`", register)

    def test_circuit_schemas_exist(self):
        for name in ("circuit-spec.schema.json", "circuit-validation.schema.json"):
            self.assertTrue((CONTRACTS / name).is_file(), name)


class CircuitBoundaryModelTests(unittest.TestCase):
    def test_macro_families_and_non_authority_policy_are_explicit(self):
        data = load(MODEL)
        self.assertEqual(
            set(data["macro_families"]),
            {"SIGHTLINE", "HELM", "COVENANT", "DRIVE", "WITNESS", "REFINERY"},
        )
        policy = data["policy"]
        self.assertTrue(policy["dependency_graph_is_not_circuit_flow"])
        self.assertFalse(policy["circuit_compiler_has_authority"])
        self.assertFalse(policy["circuit_owns_durable_state"])
        self.assertFalse(policy["circuit_validator_grants_execution"])
        self.assertFalse(policy["roro_has_circuit_authority"])
        self.assertTrue(policy["consequential_drive_requires_covenant"])
        self.assertTrue(policy["executor_cannot_self_verify"])

    def test_covenant_support_is_not_covenant_authority(self):
        data = load(MODEL)
        support = {x["family"]: x for x in data["semantic_support_families"]}
        self.assertIn("COVENANT_SUPPORT", support)
        self.assertFalse(support["COVENANT_SUPPORT"]["grants_authority"])
        self.assertIn("does not grant", support["COVENANT_SUPPORT"]["boundary_note"].lower())

    def test_dependency_hotspot_does_not_become_allowed_circuit_shortcut(self):
        data = load(MODEL)
        observed = {(x["from_family"], x["to_family"]): x["edge_count"] for x in data["observed_dependency_coupling"]}
        allowed = {(x["from_family"], x["to_family"]) for x in data["allowed_edges"]}
        self.assertGreater(observed[("HELM", "DRIVE")], 0)
        self.assertNotIn(("HELM", "DRIVE"), allowed)
        forbidden = {(x["from_family"], x["to_family"]): x["rule_id"] for x in data["forbidden_edges"]}
        self.assertEqual(forbidden[("HELM", "DRIVE")], "COVENANT_REQUIRED")


class CircuitValidationTests(unittest.TestCase):
    def test_required_falsification_vectors_exist(self):
        data = load(VECTORS)
        ids = {x["vector_id"] for x in data["vectors"]}
        self.assertTrue({
            "read-only-valid",
            "production-repair-valid",
            "improvement-valid",
            "missing-covenant-invalid",
            "self-verification-invalid",
            "unknown-family-invalid",
            "mode-mismatch-invalid",
            "missing-drive-invalid",
            "disconnected-invalid",
        } <= ids)

    def test_validator_results_match_expected_vectors(self):
        vectors = {x["vector_id"]: x for x in load(VECTORS)["vectors"]}
        results = {x["vector_id"]: x for x in load(RESULTS)["results"]}
        self.assertEqual(set(vectors), set(results))
        for vector_id, vector in vectors.items():
            result = results[vector_id]
            self.assertEqual(result["composition_status"], vector["expected_status"], vector_id)
            self.assertFalse(result["execution_authorized"], vector_id)
            self.assertFalse(result["authority_granted"], vector_id)

    def test_invalid_vectors_fail_for_specific_invariants(self):
        results = {x["vector_id"]: x for x in load(RESULTS)["results"]}
        rules = lambda vector_id: {x["rule_id"] for x in results[vector_id]["violations"]}
        self.assertIn("COVENANT_REQUIRED", rules("missing-covenant-invalid"))
        self.assertIn("VERIFIER_NOT_INDEPENDENT", rules("self-verification-invalid"))
        self.assertIn("UNKNOWN_FAMILY", rules("unknown-family-invalid"))
        self.assertIn("MODE_CONSEQUENTIAL_MISMATCH", rules("mode-mismatch-invalid"))
        self.assertIn("DRIVE_REQUIRED", rules("missing-drive-invalid"))
        self.assertIn("DISCONNECTED_GRAPH", rules("disconnected-invalid"))

    def test_validator_is_deterministic(self):
        before = RESULTS.read_bytes()
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts/roro/validate_circuit_spec.py")],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(before, RESULTS.read_bytes())


if __name__ == "__main__":
    unittest.main(verbosity=2)
