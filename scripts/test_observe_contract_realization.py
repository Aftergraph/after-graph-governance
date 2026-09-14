import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "scripts" / "observe_contract_realization.py"


def load_module():
    spec = importlib.util.spec_from_file_location("observe_contract_realization", MODULE)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load observe_contract_realization.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class ObserveContractRealizationTests(unittest.TestCase):
    def test_owner_repo_url_is_aftergraph_repo(self):
        mod = load_module()
        self.assertEqual(mod.repo_name("works-execution"), "Aftergraph/works-execution")
        self.assertEqual(mod.repo_name("after-graph-governance"), "Aftergraph/after-graph-governance")

    def test_ref_override_is_owner_scoped(self):
        mod = load_module()
        refs = mod.parse_ref_overrides(["works-execution=execution-context-v2-1-20260914"])
        self.assertEqual(refs["works-execution"], "execution-context-v2-1-20260914")
        self.assertEqual(mod.ref_for("aie", refs), "main")

    def test_malformed_ref_override_fails(self):
        mod = load_module()
        with self.assertRaises(ValueError):
            mod.parse_ref_overrides(["missing-separator"])


if __name__ == "__main__":
    unittest.main()
