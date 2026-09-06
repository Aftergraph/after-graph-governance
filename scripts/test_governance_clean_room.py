#!/usr/bin/env python3
"""Tests for verify_runner_clean_room.py — stdlib unittest."""
import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts" / "verify_runner_clean_room.py"
SHA = "8e5fac2a86f39b965539ec580b08ceb331830c49"
DEP_SHA = "b806c23a44099547f4e00adf752a4e591cf9b2e4"


def valid_record():
    return {
        "repo": "Aftergraph/aie",
        "sha": SHA,
        "run_id": "34022570023",
        "attempt": 1,
        "checkout_root": "/runner/_work/aie/aie",
        "test_root": "/runner/_work/aie/aie/tests",
        "dependency_root": "/runner/_work/aie/aie/.ci-dependencies",
        "temp_root": "/runner/_work/_temp/aie-34022570023-1",
        "cache_namespace": "aie-34022570023-1",
        "dependencies": [{
            "name": "after-graph-governance",
            "path": "/runner/_work/aie/aie/.ci-dependencies/after-graph-governance",
            "sha": DEP_SHA,
        }],
        "ports": {"isolated": True, "reserved": [18431, 18432]},
        "cleanup": {"clean_before": True, "clean_after": True, "on_failure": "retain-evidence-only"},
    }


def run(record):
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "room.json"
        path.write_text(json.dumps(record), encoding="utf-8")
        return subprocess.run([sys.executable, str(VALIDATOR), str(path)], capture_output=True, text=True, cwd=ROOT)


class CleanRoomTest(unittest.TestCase):
    def test_valid_record(self):
        result = run(valid_record())
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("OK:", result.stdout)

    def test_test_root_must_be_inside_checkout(self):
        value = valid_record()
        value["test_root"] = "/runner/_work/other/tests"
        result = run(value)
        self.assertEqual(result.returncode, 1)
        self.assertIn("inside checkout_root", result.stdout)

    def test_dependency_root_cannot_be_test_root(self):
        value = valid_record()
        value["dependency_root"] = value["test_root"]
        result = run(value)
        self.assertEqual(result.returncode, 1)
        self.assertIn("disjoint", result.stdout)

    def test_dependency_checkout_must_stay_under_dependency_root(self):
        value = valid_record()
        value["dependencies"][0]["path"] = "/runner/_work/aie/aie/tests/governance"
        result = run(value)
        self.assertEqual(result.returncode, 1)
        self.assertIn("escapes", result.stdout)

    def test_temp_root_must_be_outside_checkout(self):
        value = valid_record()
        value["temp_root"] = "/runner/_work/aie/aie/.tmp"
        result = run(value)
        self.assertEqual(result.returncode, 1)
        self.assertIn("outside checkout_root", result.stdout)

    def test_cache_namespace_must_contain_run_id(self):
        value = valid_record()
        value["cache_namespace"] = "aie-shared"
        result = run(value)
        self.assertEqual(result.returncode, 1)
        self.assertIn("run_id", result.stdout)

    def test_ports_must_be_isolated(self):
        value = valid_record()
        value["ports"]["isolated"] = False
        result = run(value)
        self.assertEqual(result.returncode, 1)
        self.assertIn("ports.isolated", result.stdout)

    def test_duplicate_ports_rejected(self):
        value = valid_record()
        value["ports"]["reserved"] = [18431, 18431]
        result = run(value)
        self.assertEqual(result.returncode, 1)
        self.assertIn("unique ports", result.stdout)

    def test_cleanup_before_required(self):
        value = valid_record()
        value["cleanup"]["clean_before"] = False
        result = run(value)
        self.assertEqual(result.returncode, 1)
        self.assertIn("clean_before", result.stdout)

    def test_cleanup_after_required(self):
        value = valid_record()
        value["cleanup"]["clean_after"] = False
        result = run(value)
        self.assertEqual(result.returncode, 1)
        self.assertIn("clean_after", result.stdout)

    def test_duplicate_dependency_name_rejected(self):
        value = valid_record()
        duplicate = copy.deepcopy(value["dependencies"][0])
        duplicate["path"] += "/other"
        value["dependencies"].append(duplicate)
        result = run(value)
        self.assertEqual(result.returncode, 1)
        self.assertIn("duplicate dependency name", result.stdout)

    def test_full_sha_required(self):
        value = valid_record()
        value["dependencies"][0]["sha"] = "b806c23"
        result = run(value)
        self.assertEqual(result.returncode, 1)
        self.assertIn("full lowercase commit SHA", result.stdout)

    def test_unknown_field_is_rejected_at_contract_boundary(self):
        value = valid_record()
        value["surprise"] = True
        result = run(value)
        self.assertEqual(result.returncode, 1)
        self.assertIn("unknown field", result.stdout)

    def test_invalid_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "room.json"
            path.write_text("{nope", encoding="utf-8")
            result = subprocess.run([sys.executable, str(VALIDATOR), str(path)], capture_output=True, text=True, cwd=ROOT)
        self.assertEqual(result.returncode, 1)
        self.assertIn("invalid JSON", result.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=1)
