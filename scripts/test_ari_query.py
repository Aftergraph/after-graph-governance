import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.ari_model import ResultState
from scripts.ari_query import QueryError, query_compat
from scripts.ari_registry import Registry, build_registry

ROOT = Path(__file__).resolve().parents[1]

LEFT = {
    "schema": "aftergraph-component/1.0",
    "identity": {"product": "sentinel", "component": "sentinel-engine"},
    "release": {"version": "1.4.0", "lifecycle": "preview"},
    "platform": {"generation": 26, "release_train": "2026.09"},
    "compatibility": {
        "level": "APC-1",
        "profiles": ["verifier"],
        "minimum": "APC-1",
        "tested_against": "APC-1",
    },
    "contracts": {"correlation": "1.0"},
    "provenance": {"repository": "Aftergraph/sentinel", "commit": "1" * 40},
}

RIGHT = {
    "schema": "aftergraph-component/1.0",
    "identity": {"product": "works", "component": "works"},
    "release": {"version": "0.5.1", "lifecycle": "preview"},
    "platform": {"generation": 26, "release_train": "2026.09"},
    "compatibility": {
        "level": "APC-1",
        "profiles": ["execution"],
        "minimum": "APC-1",
        "tested_against": "APC-1",
    },
    "contracts": {"correlation": "1.0"},
    "provenance": {"repository": "Aftergraph/works-execution", "commit": "2" * 40},
}

EDGE = {
    "schema": "compatibility-edge/1.0",
    "from": {"component": "sentinel-engine", "version": "1.4.0", "commit": "1" * 40},
    "to": {"component": "works", "version": "0.5.1", "commit": "2" * 40},
    "relation": "tested-with",
    "state": "pass",
    "evidence_level": "CE3",
    "evidence": [{"kind": "integration-test", "ref": "sha256:" + "3" * 64}],
}

LEFT_SELECTOR = "sentinel-engine@1.4.0#" + "1" * 40
RIGHT_SELECTOR = "works@0.5.1#" + "2" * 40


class AriQueryTest(unittest.TestCase):
    def registry(self, edges=None):
        return Registry(build_registry([LEFT, RIGHT, *(edges if edges is not None else [EDGE])]))

    def test_query_pass_for_exact_ce3_edge_at_ce2_minimum(self):
        result = query_compat(self.registry(), LEFT_SELECTOR, RIGHT_SELECTOR, "CE2")
        self.assertEqual(result["state"], ResultState.PASS.value)
        self.assertEqual(result["minimum_evidence"], "CE2")
        self.assertEqual(result["matching_edges"], 1)
        self.assertEqual(result["evidence"], ["sha256:" + "3" * 64])
        self.assertEqual(result["left"]["commit"], "1" * 40)
        self.assertEqual(result["right"]["commit"], "2" * 40)

    def test_query_unknown_when_exact_edge_missing(self):
        result = query_compat(self.registry(edges=[]), LEFT_SELECTOR, RIGHT_SELECTOR, "CE2")
        self.assertEqual(result["state"], ResultState.UNKNOWN.value)
        self.assertEqual(result["matching_edges"], 0)
        self.assertEqual(result["evidence"], [])

    def test_query_fail_for_reverse_incompatible_edge(self):
        edge = copy.deepcopy(EDGE)
        edge["from"], edge["to"] = edge["to"], edge["from"]
        edge["relation"] = "incompatible-with"
        edge["evidence_level"] = "CE1"
        result = query_compat(self.registry([edge]), LEFT_SELECTOR, RIGHT_SELECTOR, "CE2")
        self.assertEqual(result["state"], ResultState.FAIL.value)
        self.assertEqual(result["matching_edges"], 1)
        self.assertEqual(result["evidence"], ["sha256:" + "3" * 64])

    def test_query_stale_is_not_pass(self):
        edge = copy.deepcopy(EDGE)
        edge["state"] = "stale"
        result = query_compat(self.registry([edge]), LEFT_SELECTOR, RIGHT_SELECTOR, "CE2")
        self.assertEqual(result["state"], ResultState.STALE.value)

    def test_query_unknown_when_pass_edge_is_below_minimum(self):
        edge = copy.deepcopy(EDGE)
        edge["evidence_level"] = "CE1"
        result = query_compat(self.registry([edge]), LEFT_SELECTOR, RIGHT_SELECTOR, "CE2")
        self.assertEqual(result["state"], ResultState.UNKNOWN.value)
        self.assertEqual(result["evidence"], [])

    def test_query_rejects_non_exact_selector(self):
        with self.assertRaisesRegex(QueryError, "exact component selector"):
            query_compat(self.registry(), "sentinel-engine@1.4.0", RIGHT_SELECTOR, "CE2")

    def test_query_rejects_unregistered_exact_component(self):
        missing = "ghost@1.0.0#" + "9" * 40
        with self.assertRaisesRegex(QueryError, "component not found"):
            query_compat(self.registry(), missing, RIGHT_SELECTOR, "CE2")

    def test_query_rejects_invalid_minimum_evidence_level(self):
        with self.assertRaisesRegex(QueryError, "CE0..CE5"):
            query_compat(self.registry(), LEFT_SELECTOR, RIGHT_SELECTOR, "CE9")

    def test_cli_json_exit_codes_match_compiler_semantics(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "registry.json"
            path.write_text(json.dumps(self.registry().document), encoding="utf-8")
            base = [
                sys.executable,
                str(ROOT / "scripts/ari_query.py"),
                "compat",
                str(path),
                LEFT_SELECTOR,
                RIGHT_SELECTOR,
                "--minimum",
                "CE2",
                "--format",
                "json",
            ]
            passing = subprocess.run(base, cwd=ROOT, text=True, capture_output=True, check=False)

            unknown_registry = Path(tmp) / "unknown.json"
            unknown_registry.write_text(json.dumps(self.registry(edges=[]).document), encoding="utf-8")
            unknown_command = list(base)
            unknown_command[3] = str(unknown_registry)
            unknown = subprocess.run(unknown_command, cwd=ROOT, text=True, capture_output=True, check=False)

            fail_edge = copy.deepcopy(EDGE)
            fail_edge["relation"] = "incompatible-with"
            fail_registry = Path(tmp) / "fail.json"
            fail_registry.write_text(json.dumps(self.registry([fail_edge]).document), encoding="utf-8")
            fail_command = list(base)
            fail_command[3] = str(fail_registry)
            failing = subprocess.run(fail_command, cwd=ROOT, text=True, capture_output=True, check=False)

        self.assertEqual(passing.returncode, 0, passing.stderr)
        self.assertEqual(json.loads(passing.stdout)["state"], "PASS")
        self.assertEqual(unknown.returncode, 3, unknown.stderr)
        self.assertEqual(json.loads(unknown.stdout)["state"], "UNKNOWN")
        self.assertEqual(failing.returncode, 2, failing.stderr)
        self.assertEqual(json.loads(failing.stdout)["state"], "FAIL")


if __name__ == "__main__":
    unittest.main()
