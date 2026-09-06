#!/usr/bin/env python3
"""Tests for reduce_ci_truth.py — stdlib unittest, unique basename."""
import json
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REDUCER = ROOT / "scripts" / "reduce_ci_truth.py"
HEAD = "8e5fac2a86f39b965539ec580b08ceb331830c49"
OTHER = "efc88fc353a40000000000000000000000000000"


def record(**overrides):
    value = {
        "repo": "Aftergraph/aie",
        "sha": HEAD,
        "source": "self-hosted",
        "run_id": "34021908374",
        "attempt": 1,
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "environment": {"runner": "self-hosted,linux,x64,aie-interop", "package_installed": True},
        "results": [
            {"context": "test (3.11)", "status": "success"},
            {"context": "test (3.12)", "status": "success"},
            {"context": "test (3.13)", "status": "success"},
            {"context": "Brand Assets", "status": "success"},
        ],
    }
    value.update(overrides)
    return value


def run(value, *extra):
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "result.json"
        path.write_text(json.dumps(value), encoding="utf-8")
        return subprocess.run([sys.executable, str(REDUCER), str(path), "--head", HEAD, *extra],
                              capture_output=True, text=True, cwd=ROOT)


class ReducerTest(unittest.TestCase):
    def test_all_required_success_is_pass(self):
        result = run(record(), "--required-context", "test (3.11)", "--required-context", "test (3.12)", "--required-context", "test (3.13)")
        self.assertEqual(result.returncode, 0)
        self.assertTrue(result.stdout.startswith("PASS:"))

    def test_matching_head_is_required(self):
        result = run(record(sha=OTHER))
        self.assertEqual(result.returncode, 1)
        self.assertTrue(result.stdout.startswith("STALE:"))

    def test_stale_timestamp_is_not_pass(self):
        timestamp = (datetime.now(timezone.utc) - timedelta(hours=2)).strftime("%Y-%m-%dT%H:%M:%SZ")
        result = run(record(timestamp=timestamp))
        self.assertEqual(result.returncode, 1)
        self.assertTrue(result.stdout.startswith("STALE:"))

    def test_missing_required_context_is_incomplete(self):
        result = run(record(), "--required-context", "required-but-missing")
        self.assertEqual(result.returncode, 1)
        self.assertTrue(result.stdout.startswith("INCOMPLETE:"))

    def test_failure_blocks(self):
        results = record()["results"]
        results[1]["status"] = "failure"
        result = run(record(results=results))
        self.assertEqual(result.returncode, 1)
        self.assertTrue(result.stdout.startswith("BLOCKED:"))

    def test_timeout_blocks(self):
        results = record()["results"]
        results[1]["status"] = "timeout"
        result = run(record(results=results))
        self.assertEqual(result.returncode, 1)
        self.assertTrue(result.stdout.startswith("BLOCKED:"))

    def test_cancelled_blocks(self):
        results = record()["results"]
        results[1]["status"] = "cancelled"
        result = run(record(results=results))
        self.assertEqual(result.returncode, 1)
        self.assertTrue(result.stdout.startswith("BLOCKED:"))

    def test_running_is_in_progress(self):
        results = record()["results"]
        results[2]["status"] = "running"
        result = run(record(results=results))
        self.assertEqual(result.returncode, 1)
        self.assertTrue(result.stdout.startswith("IN_PROGRESS:"))

    def test_queued_is_in_progress(self):
        results = record()["results"]
        results[0]["status"] = "queued"
        result = run(record(results=results))
        self.assertEqual(result.returncode, 1)
        self.assertTrue(result.stdout.startswith("IN_PROGRESS:"))

    def test_json_output_is_machine_readable(self):
        result = run(record(), "--json")
        self.assertEqual(result.returncode, 0)
        output = json.loads(result.stdout)
        self.assertEqual(output["decision"], "PASS")
        self.assertEqual(output["current_head"], HEAD)

    def test_schema_missing_field_is_invalid(self):
        value = record()
        del value["environment"]
        result = run(value)
        self.assertEqual(result.returncode, 1)
        self.assertTrue(result.stdout.startswith("INVALID:"))

    def test_duplicate_context_is_invalid(self):
        results = record()["results"] + [{"context": "test (3.11)", "status": "success"}]
        result = run(record(results=results))
        self.assertEqual(result.returncode, 1)
        self.assertTrue(result.stdout.startswith("INVALID:"))

    def test_invalid_status_is_invalid(self):
        results = record()["results"]
        results[0]["status"] = "maybe"
        result = run(record(results=results))
        self.assertEqual(result.returncode, 1)
        self.assertTrue(result.stdout.startswith("INVALID:"))

    def test_no_results_is_incomplete(self):
        result = run(record(results=[]))
        self.assertEqual(result.returncode, 1)
        self.assertTrue(result.stdout.startswith("INVALID:"))

    def test_required_contexts_can_ignore_informational_extra(self):
        results = record()["results"]
        results[-1]["status"] = "failure"
        result = run(record(results=results), "--required-context", "test (3.11)")
        self.assertEqual(result.returncode, 0)
        self.assertTrue(result.stdout.startswith("PASS:"))

    def test_future_timestamp_is_invalid(self):
        timestamp = (datetime.now(timezone.utc) + timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
        result = run(record(timestamp=timestamp))
        self.assertEqual(result.returncode, 1)
        self.assertTrue(result.stdout.startswith("INVALID:"))


if __name__ == "__main__":
    unittest.main(verbosity=1)
