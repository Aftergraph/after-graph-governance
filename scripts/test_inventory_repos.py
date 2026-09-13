#!/usr/bin/env python3
"""Tests for the workspace inventory producer.

Run: python scripts/test_inventory_repos.py
Self-contained (stdlib unittest only, no network). Each case builds a throwaway
workspace in a temporary directory and runs the producer against it, asserting
about the producer's observable contract, not its internals:

  1. every topology repo gets a REPOSITORY_INVENTORY row;
  2. a present repo records a live head/branch and dirty=false on a clean checkout;
  3. an absent repo is marked present=false and skipped from CI_COMMAND_INVENTORY;
  4. CI_RESULTS.json is always written and is valid JSON with a results list;
  5. a provided --ci-results file is passed through verbatim.
"""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
PRODUCER = HERE / "inventory_repos.py"
TOPOLOGY = HERE.parent / "docs" / "platform-topology" / "2.0.json"


def write(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def init_git(repo: Path):
    repo.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.email", "t@t"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.name", "t"], cwd=repo, check=True)
    write(repo / "README.md", "x\n")
    subprocess.run(["git", "add", "-A"], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-qm", "init"], cwd=repo, check=True)


def run_producer(root: Path, *args):
    return subprocess.run([sys.executable, str(PRODUCER), "--root", str(root), *args],
                          capture_output=True, text=True)


class InventoryTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def test_every_topology_repo_gets_an_inventory_row(self):
        topo = json.loads(TOPOLOGY.read_text())
        names = {r["name"] for r in topo["repositories"]}
        run_producer(self.tmp)
        inv = json.loads((self.tmp / "REPOSITORY_INVENTORY.json").read_text())
        self.assertEqual({r["name"] for r in inv["repos"]}, names)

    def test_present_repo_records_live_head_branch_and_clean(self):
        repo = self.tmp / "aie"
        init_git(repo)
        run_producer(self.tmp)
        inv = json.loads((self.tmp / "REPOSITORY_INVENTORY.json").read_text())
        row = next(r for r in inv["repos"] if r["name"] == "aie")
        self.assertTrue(row["local"]["present"])
        self.assertEqual(len(row["local"]["head"]), 40)
        self.assertEqual(row["local"]["branch"], "master")
        self.assertFalse(row["local"]["dirty"])
        ci_cmd = json.loads((self.tmp / "CI_COMMAND_INVENTORY.json").read_text())
        self.assertIn("aie", {r["name"] for r in ci_cmd["repos"]})

    def test_absent_repo_marked_not_present_and_excluded_from_ci_cmd(self):
        run_producer(self.tmp)
        inv = json.loads((self.tmp / "REPOSITORY_INVENTORY.json").read_text())
        row = next(r for r in inv["repos"] if r["name"] == "trust-gateway")
        self.assertFalse(row["local"]["present"])
        ci_cmd = json.loads((self.tmp / "CI_COMMAND_INVENTORY.json").read_text())
        self.assertNotIn("trust-gateway", {r["name"] for r in ci_cmd["repos"]})

    def test_ci_results_always_written_and_valid(self):
        run_producer(self.tmp)
        doc = json.loads((self.tmp / "CI_RESULTS.json").read_text())
        self.assertIn("results", doc)
        self.assertIsInstance(doc["results"], list)
        self.assertIn("scope", doc)

    def test_provided_ci_results_passed_through_verbatim(self):
        repo = self.tmp / "aie"
        init_git(repo)
        feed = self.tmp / "feed.json"
        feed.write_text(json.dumps({
            "generated_at": "2026-01-01T00:00:00+00:00",
            "scope": "test feed",
            "results": [{"repo": "aie", "command": "python3 -m pytest -q",
                         "status": "passed", "sha": "0" * 40, "note": "n"}]}))
        run_producer(self.tmp, "--ci-results", str(feed))
        doc = json.loads((self.tmp / "CI_RESULTS.json").read_text())
        self.assertEqual(doc["scope"], "test feed")
        self.assertEqual(len(doc["results"]), 1)


if __name__ == "__main__":
    unittest.main()
