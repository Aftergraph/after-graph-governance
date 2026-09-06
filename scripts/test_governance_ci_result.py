#!/usr/bin/env python3
"""Tests for ci_result_from_gh.py — run: python scripts/test_governance_ci_result.py
or: python -m pytest scripts/test_governance_ci_result.py -q
Stdlib unittest only. Unique basename avoids pytest import-file-mismatch
with sibling checkouts (see AIE #37)."""
import json
import subprocess
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
CONVERTER = REPO_ROOT / "scripts" / "ci_result_from_gh.py"
SCHEMA_PATH = REPO_ROOT / "docs/contracts/ci-result/1.0.json"

SHA = "8e5fac2a86f39b965539ec580b08ceb331830c49"

GH_GREEN = {
    "databaseId": 34021908374, "headSha": SHA, "status": "completed",
    "conclusion": "success", "workflowName": "AIE v0.4 CI (self-hosted)",
    "url": "https://github.com/Aftergraph/aie/actions/runs/34021908374",
    "jobs": [
        {"name": "test (3.11)", "status": "completed", "conclusion": "success", "url": "https://x/1"},
        {"name": "test (3.12)", "status": "completed", "conclusion": "success", "url": "https://x/2"},
        {"name": "test (3.13)", "status": "completed", "conclusion": "success", "url": "https://x/3"},
    ],
}

GH_MIXED = {
    "databaseId": 99, "headSha": SHA, "status": "completed",
    "conclusion": "failure", "workflowName": "CI", "url": "https://x/r",
    "jobs": [
        {"name": "lint", "status": "completed", "conclusion": "failure"},
        {"name": "skipped-job", "status": "completed", "conclusion": "skipped"},
        {"name": "slow", "status": "completed", "conclusion": "timed_out"},
    ],
}

GH_RUNNING = {
    "databaseId": 100, "headSha": SHA, "status": "in_progress",
    "conclusion": "", "workflowName": "CI", "url": "https://x/r2",
    "jobs": [{"name": "test", "status": "in_progress", "conclusion": ""}],
}


def convert(gh, extra=()):
    p = subprocess.run([sys.executable, str(CONVERTER), "--repo", "Aftergraph/aie",
                        "--source", "self-hosted", "--runner", "self-hosted,linux,x64",
                        *extra],
                       input=json.dumps(gh), capture_output=True, text=True, cwd=REPO_ROOT)
    assert p.returncode == 0, p.stderr
    return json.loads(p.stdout)


class SchemaFileTest(unittest.TestCase):
    def test_schema_shape(self):
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        self.assertEqual(schema["$id"], "contract:ci-result/1.0")
        for f in ("repo", "sha", "source", "run_id", "attempt", "timestamp", "environment", "results"):
            self.assertIn(f, schema["required"])
        self.assertIn("package_installed", schema["properties"]["environment"]["properties"])


class ConverterTest(unittest.TestCase):
    def test_green_run_all_success(self):
        out = convert(GH_GREEN)
        self.assertEqual(out["repo"], "Aftergraph/aie")
        self.assertEqual(out["sha"], SHA)
        self.assertEqual(out["run_id"], "34021908374")
        self.assertEqual([r["status"] for r in out["results"]], ["success"] * 3)
        self.assertEqual(out["environment"]["runner"], "self-hosted,linux,x64")

    def test_mixed_maps_each_outcome(self):
        out = convert(GH_MIXED)
        by_ctx = {r["context"]: r["status"] for r in out["results"]}
        self.assertEqual(by_ctx["lint"], "failure")
        self.assertEqual(by_ctx["skipped-job"], "cancelled")  # never silently dropped
        self.assertEqual(by_ctx["slow"], "timeout")

    def test_running_run_never_passes(self):
        out = convert(GH_RUNNING)
        self.assertEqual(out["results"][0]["status"], "running")

    def test_attempt_and_versions(self):
        out = convert(GH_GREEN, ("--attempt", "2", "--python", "3.12"))
        self.assertEqual(out["attempt"], 2)
        self.assertEqual(out["environment"]["versions"], {"python": "3.12"})

    def test_no_jobs_falls_back_to_workflow_verdict(self):
        gh = dict(GH_GREEN, jobs=[])
        out = convert(gh)
        self.assertEqual(len(out["results"]), 1)
        self.assertEqual(out["results"][0]["status"], "success")
        self.assertEqual(out["results"][0]["context"], "AIE v0.4 CI (self-hosted)")

    def test_missing_repo_rejected(self):
        p = subprocess.run([sys.executable, str(CONVERTER), "--source", "self-hosted"],
                           input="{}", capture_output=True, text=True, cwd=REPO_ROOT)
        self.assertEqual(p.returncode, 1)

    def test_bad_source_rejected(self):
        p = subprocess.run([sys.executable, str(CONVERTER), "--repo", "a/b", "--source", "pigeon"],
                           input="{}", capture_output=True, text=True, cwd=REPO_ROOT)
        self.assertEqual(p.returncode, 1)

    def test_invalid_json_rejected(self):
        p = subprocess.run([sys.executable, str(CONVERTER), "--repo", "a/b", "--source", "manual"],
                           input="{nope", capture_output=True, text=True, cwd=REPO_ROOT)
        self.assertEqual(p.returncode, 1)


if __name__ == "__main__":
    unittest.main(verbosity=1)
