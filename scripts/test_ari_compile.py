import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.ari_compile import compile_component
from scripts.ari_model import ResultState

ROOT = Path(__file__).resolve().parents[1]
APC = json.loads((ROOT / "docs/release-intelligence/apc-1.json").read_text(encoding="utf-8"))

BASE = {
    "schema": "aftergraph-component/1.0",
    "identity": {"product": "sentinel", "component": "sentinel-engine"},
    "release": {"version": "1.4.0", "lifecycle": "preview"},
    "platform": {"generation": 26, "release_train": "2026.09"},
    "compatibility": {
        "level": "APC-1",
        "profiles": ["verifier"],
        "minimum": "APC-1",
        "tested_against": "APC-1",
        "requires_edges": [
            {"component": "works", "version": "0.5.1", "commit": "2" * 40}
        ],
    },
    "contracts": {"correlation": "1.0", "evidence": "1.1"},
    "provenance": {"repository": "Aftergraph/sentinel", "commit": "1" * 40},
}


def edge(*, state="pass", level="CE3", relation="tested-with"):
    return {
        "schema": "compatibility-edge/1.0",
        "from": {"component": "sentinel-engine", "version": "1.4.0", "commit": "1" * 40},
        "to": {"component": "works", "version": "0.5.1", "commit": "2" * 40},
        "relation": relation,
        "state": state,
        "evidence_level": level,
        "evidence": [{"kind": "test-receipt", "ref": "sha256:" + "3" * 64}],
    }


class AriCompileTest(unittest.TestCase):
    def test_invalid_manifest_is_fail(self):
        manifest = copy.deepcopy(BASE)
        manifest["provenance"]["commit"] = "bad"
        result = compile_component(manifest, APC, [edge()])
        self.assertEqual(result.state, ResultState.FAIL)
        self.assertTrue(result.errors)

    def test_no_profiles_is_n_a(self):
        manifest = copy.deepcopy(BASE)
        manifest["compatibility"]["profiles"] = []
        manifest["compatibility"].pop("requires_edges")
        result = compile_component(manifest, APC, [])
        self.assertEqual(result.state, ResultState.N_A)

    def test_profile_contract_missing_is_fail(self):
        manifest = copy.deepcopy(BASE)
        manifest["contracts"].pop("correlation")
        result = compile_component(manifest, APC, [edge()])
        self.assertEqual(result.state, ResultState.FAIL)
        self.assertIn("APC-1/verifier requires contract: correlation", result.errors)

    def test_required_exact_edge_absent_is_unknown(self):
        result = compile_component(copy.deepcopy(BASE), APC, [])
        self.assertEqual(result.state, ResultState.UNKNOWN)
        self.assertEqual(result.profile_results["verifier"], ResultState.UNKNOWN)
        self.assertTrue(any("works@0.5.1" in message for message in result.unknowns))

    def test_edge_below_profile_minimum_is_unknown(self):
        result = compile_component(copy.deepcopy(BASE), APC, [edge(level="CE1")])
        self.assertEqual(result.state, ResultState.UNKNOWN)

    def test_explicit_fail_edge_is_fail(self):
        result = compile_component(copy.deepcopy(BASE), APC, [edge(state="fail", level="CE1")])
        self.assertEqual(result.state, ResultState.FAIL)
        self.assertEqual(result.profile_results["verifier"], ResultState.FAIL)

    def test_stale_edge_is_stale(self):
        result = compile_component(copy.deepcopy(BASE), APC, [edge(state="stale")])
        self.assertEqual(result.state, ResultState.STALE)

    def test_profile_requirements_and_ce3_edge_pass(self):
        result = compile_component(copy.deepcopy(BASE), APC, [edge(level="CE3")])
        self.assertEqual(result.state, ResultState.PASS)
        self.assertEqual(result.profile_results, {"verifier": ResultState.PASS})
        self.assertEqual(result.unknowns, [])

    def test_unknown_apc_profile_is_fail(self):
        manifest = copy.deepcopy(BASE)
        manifest["compatibility"]["profiles"] = ["banana"]
        result = compile_component(manifest, APC, [edge()])
        self.assertEqual(result.state, ResultState.FAIL)
        self.assertTrue(any("banana" in message for message in result.errors))

    def test_malformed_required_edge_is_fail_not_crash(self):
        manifest = copy.deepcopy(BASE)
        manifest["compatibility"]["requires_edges"][0]["commit"] = "bad"
        result = compile_component(manifest, APC, [edge()])
        self.assertEqual(result.state, ResultState.FAIL)
        self.assertTrue(any("requires_edges[0].commit" in message for message in result.errors))

    def test_cli_json_pass_and_exit_zero(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            manifest_path = tmp_path / "component.json"
            edge_path = tmp_path / "edge.json"
            manifest_path.write_text(json.dumps(BASE), encoding="utf-8")
            edge_path.write_text(json.dumps(edge()), encoding="utf-8")
            proc = subprocess.run(
                [sys.executable, str(ROOT / "scripts/ari_compile.py"), str(manifest_path), "--edge", str(edge_path), "--format", "json"],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["schema"], "aftergraph.apc-result/1")
        self.assertEqual(payload["state"], "PASS")
        self.assertEqual(payload["profiles"], {"verifier": "PASS"})

    def test_cli_unknown_exit_three(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "component.json"
            path.write_text(json.dumps(BASE), encoding="utf-8")
            proc = subprocess.run(
                [sys.executable, str(ROOT / "scripts/ari_compile.py"), str(path), "--format", "json"],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
        self.assertEqual(proc.returncode, 3)
        self.assertEqual(json.loads(proc.stdout)["state"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
