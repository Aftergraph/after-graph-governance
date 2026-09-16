import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REALITY = ROOT / "docs/system-reality"
CONTRACTS = ROOT / "docs/contracts/circuit/0.1"
VECTORS = REALITY / "circuit-compiler-vectors.json"
RESULTS = REALITY / "circuit-compiler-results.json"
COMPILER = ROOT / "scripts/circuit/compile_circuit.py"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


class CircuitCompilerContractTests(unittest.TestCase):
    def test_compiler_schemas_exist_and_are_registered_experimental(self):
        register = (ROOT / "docs/cross-repo-contracts.md").read_text(encoding="utf-8")
        for name in ["circuit-compiler-input.schema.json", "circuit-compile-result.schema.json"]:
            self.assertTrue((CONTRACTS / name).is_file(), name)
        self.assertIn("`circuit-compiler-input/0.1`", register)
        self.assertIn("`circuit-compile-result/0.1`", register)
        self.assertIn("Experimental", register)


class CircuitCompilerVectorTests(unittest.TestCase):
    def test_required_vectors_exist(self):
        vectors = {x["vector_id"]: x for x in load(VECTORS)["vectors"]}
        expected = {
            "query-read-only",
            "repair-reversible",
            "repair-irreversible-high-risk",
            "improve-reversible",
            "unknown-reality",
            "conflicting-reality",
            "stale-consequential",
            "unknown-intent",
            "unknown-effect",
            "high-risk-unverified",
            "missing-fresh",
        }
        self.assertEqual(expected, set(vectors))

    def test_results_match_expected_compile_status(self):
        vectors = {x["vector_id"]: x for x in load(VECTORS)["vectors"]}
        results = {x["vector_id"]: x for x in load(RESULTS)["results"]}
        self.assertEqual(set(vectors), set(results))
        for vector_id, vector in vectors.items():
            self.assertEqual(vector["expected_status"], results[vector_id]["compile_status"], vector_id)
            self.assertFalse(results[vector_id]["execution_authorized"])
            self.assertFalse(results[vector_id]["authority_granted"])


class CircuitCompilerBehaviorTests(unittest.TestCase):
    def test_minimal_family_sequences(self):
        results = {x["vector_id"]: x for x in load(RESULTS)["results"]}
        expected = {
            "query-read-only": ["SIGHTLINE", "HELM"],
            "repair-reversible": ["SIGHTLINE", "HELM", "COVENANT", "DRIVE", "WITNESS", "SIGHTLINE"],
            "repair-irreversible-high-risk": ["SIGHTLINE", "HELM", "COVENANT", "DRIVE", "WITNESS", "SIGHTLINE"],
            "improve-reversible": ["SIGHTLINE", "HELM", "REFINERY", "COVENANT", "DRIVE", "WITNESS"],
        }
        for vector_id, families in expected.items():
            spec = results[vector_id]["circuit_spec"]
            self.assertEqual(families, [x["family"] for x in spec["nodes"]], vector_id)

    def test_refusals_are_fail_closed_and_specific(self):
        results = {x["vector_id"]: x for x in load(RESULTS)["results"]}
        expected = {
            "unknown-reality": "REALITY_UNKNOWN",
            "conflicting-reality": "REALITY_CONFLICTING",
            "stale-consequential": "STALE_REALITY",
            "unknown-intent": "UNKNOWN_INTENT",
            "unknown-effect": "UNKNOWN_EFFECT_CLASS",
            "high-risk-unverified": "VERIFIED_REALITY_REQUIRED",
            "missing-fresh": "MALFORMED_REALITY",
        }
        for vector_id, rule in expected.items():
            result = results[vector_id]
            self.assertEqual("REFUSED", result["compile_status"])
            self.assertIsNone(result["circuit_spec"])
            self.assertIn(rule, [x["rule_id"] for x in result["violations"]])

    def test_compiled_specs_are_immediately_composition_validated(self):
        results = load(RESULTS)["results"]
        compiled = [x for x in results if x["compile_status"] == "COMPILED"]
        self.assertTrue(compiled)
        for result in compiled:
            self.assertEqual("VALID", result["composition_status"])
            self.assertFalse(result["execution_authorized"])
            self.assertFalse(result["authority_granted"])

    def test_compiler_is_deterministic(self):
        before = RESULTS.read_bytes()
        proc = subprocess.run(["python3", str(COMPILER)], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
        self.assertEqual(before, RESULTS.read_bytes())


if __name__ == "__main__":
    unittest.main()
