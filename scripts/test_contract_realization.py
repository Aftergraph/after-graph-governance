import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "scripts" / "contract_realization.py"


def load_module():
    spec = importlib.util.spec_from_file_location("contract_realization", MODULE)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load contract_realization.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


REGISTRY = {
    "schema_version": "platform-convergence-v2-1/1.0",
    "families": [
        {"contract": "execution-context/1.0", "owner": "works-execution", "path": "contracts/schemas/execution-context.schema.json"},
        {"contract": "correlation/1.0", "owner": "after-graph-governance", "path": "docs/contracts/correlation/1.0.json"},
    ],
}


class ContractRealizationTests(unittest.TestCase):
    def test_missing_observation_is_unknown(self):
        mod = load_module()
        out = mod.evaluate_registry(REGISTRY, {"observations": []})
        self.assertEqual(out["contracts"]["execution-context/1.0"]["state"], "UNKNOWN")
        self.assertEqual(out["decision"], "UNKNOWN")

    def test_absent_owner_path_is_declared_not_realized_and_blocks(self):
        mod = load_module()
        obs = {"observations": [
            {"contract": "execution-context/1.0", "owner": "works-execution", "path": "contracts/schemas/execution-context.schema.json", "head_sha": "a" * 40, "present": False},
            {"contract": "correlation/1.0", "owner": "after-graph-governance", "path": "docs/contracts/correlation/1.0.json", "head_sha": "b" * 40, "present": True},
        ]}
        out = mod.evaluate_registry(REGISTRY, obs)
        self.assertEqual(out["contracts"]["execution-context/1.0"]["state"], "DECLARED_NOT_REALIZED")
        self.assertEqual(out["decision"], "BLOCK")

    def test_present_path_is_realized_not_conformant(self):
        mod = load_module()
        obs = {"observations": [
            {"contract": "execution-context/1.0", "owner": "works-execution", "path": "contracts/schemas/execution-context.schema.json", "head_sha": "a" * 40, "present": True},
            {"contract": "correlation/1.0", "owner": "after-graph-governance", "path": "docs/contracts/correlation/1.0.json", "head_sha": "b" * 40, "present": True},
        ]}
        out = mod.evaluate_registry(REGISTRY, obs)
        self.assertEqual(out["contracts"]["execution-context/1.0"]["state"], "REALIZED")
        self.assertEqual(out["decision"], "PASS")

    def test_explicit_conformance_evidence_can_promote_to_conformant(self):
        mod = load_module()
        obs = {"observations": [
            {"contract": "execution-context/1.0", "owner": "works-execution", "path": "contracts/schemas/execution-context.schema.json", "head_sha": "a" * 40, "present": True, "conformance": {"passed": True, "evidence_ref": "ci://works/123"}},
            {"contract": "correlation/1.0", "owner": "after-graph-governance", "path": "docs/contracts/correlation/1.0.json", "head_sha": "b" * 40, "present": True},
        ]}
        out = mod.evaluate_registry(REGISTRY, obs)
        self.assertEqual(out["contracts"]["execution-context/1.0"]["state"], "CONFORMANT")
        self.assertNotEqual(out["contracts"]["execution-context/1.0"]["state"], "COMPOSED_PROVEN")

    def test_mismatched_owner_or_path_is_unknown(self):
        mod = load_module()
        obs = {"observations": [{"contract": "execution-context/1.0", "owner": "runtime", "path": "wrong.json", "head_sha": "a" * 40, "present": True}]}
        out = mod.evaluate_registry(REGISTRY, obs)
        self.assertEqual(out["contracts"]["execution-context/1.0"]["state"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
