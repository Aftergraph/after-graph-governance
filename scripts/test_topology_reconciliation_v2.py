#!/usr/bin/env python3
"""Regression tests for the 2026-09-08 canonical topology reconciliation.

This suite deliberately checks slow-changing governance truth only. It never
asserts exact remote HEAD SHAs; those belong to generated org-state.
"""

import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
TOPOLOGY = ROOT / "docs" / "platform-topology" / "1.0.json"
ORG_STATE_SCHEMA = ROOT / "docs" / "contracts" / "org-state" / "1.0.json"
DEPENDENCIES = ROOT / "dependencies.yml"
README = ROOT / "README.md"
ARCHITECTURE = ROOT / "docs" / "PLATFORM-ARCHITECTURE-V3.md"
CONTRACTS = ROOT / "docs" / "cross-repo-contracts.md"

STALE_WI = ("work-intelligence-v2", "work-intelligence-web")


class TopologyReconciliationV2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.topology = json.loads(TOPOLOGY.read_text(encoding="utf-8"))
        cls.schema = json.loads(ORG_STATE_SCHEMA.read_text(encoding="utf-8"))
        cls.dependencies = DEPENDENCIES.read_text(encoding="utf-8")
        cls.readme = README.read_text(encoding="utf-8")
        cls.architecture = ARCHITECTURE.read_text(encoding="utf-8")
        cls.contracts = CONTRACTS.read_text(encoding="utf-8")
        cls.repos = {item["name"]: item for item in cls.topology["repositories"]}

    def test_canonical_topology_count_and_visibility(self):
        self.assertEqual(21, len(self.repos))
        public = sum(repo["visibility"] == "public" for repo in self.repos.values())
        private = sum(repo["visibility"] == "private" for repo in self.repos.values())
        self.assertEqual((12, 9), (public, private))

    def test_wie_uses_canonical_repository_slugs(self):
        self.assertIn("wi-backend", self.repos)
        self.assertIn("wi-frontend", self.repos)
        for stale in STALE_WI:
            self.assertNotIn(stale, self.repos)

    def test_runtime_is_canonical_but_not_a_conformance_claim(self):
        runtime = self.repos["runtime"]
        self.assertEqual("agent-runtime", runtime["role"])
        self.assertEqual("runtime", runtime["plane"])
        self.assertEqual("private", runtime["visibility"])
        self.assertNotIn("APC-1", runtime.get("owns", ""))

    def test_avc_is_migration_source(self):
        avc = self.repos["autonomous-venture-company"]
        self.assertEqual("migration", avc["plane"])
        self.assertEqual("migration-source", avc["role"])

    def test_org_state_schema_supports_new_role_and_legacy_snapshot(self):
        roles = self.schema["$defs"]["repository"]["properties"]["role"]["enum"]
        self.assertIn("migration-source", roles)
        self.assertIn("venture-os-consumer", roles)  # historical snapshot readability

    def test_dependencies_cover_every_canonical_repository(self):
        for name in self.repos:
            self.assertIn(f"repo: Aftergraph/{name}", self.dependencies, name)
        for stale in STALE_WI:
            self.assertNotIn(stale, self.dependencies)
        self.assertIn("role: migration-source", self.dependencies)

    def test_readme_projects_current_truth(self):
        self.assertIn("21 canonical", self.readme)
        self.assertIn("12 public / 9 private", self.readme)
        self.assertIn("Wie", self.readme)
        self.assertIn("runtime", self.readme.lower())
        self.assertIn("sentinel", self.readme.lower())
        self.assertNotIn("19 repositories", self.readme)
        for stale in STALE_WI:
            self.assertNotIn(stale, self.readme)

    def test_architecture_projects_current_boundaries(self):
        self.assertIn("Wie by Aftergraph", self.architecture)
        self.assertIn("currently 21", self.architecture)
        self.assertIn("12 public / 9 private", self.architecture)
        self.assertNotIn("to be established", self.architecture)
        self.assertNotIn("persistent context", self.architecture)
        for stale in STALE_WI:
            self.assertNotIn(stale, self.architecture)

    def test_cross_repo_boundaries_cover_current_topology(self):
        for name in ("wi-backend", "wi-frontend", "runtime", "sentinel"):
            self.assertIn(f"`{name}`", self.contracts)
        self.assertIn("migration-source", self.contracts)
        for stale in STALE_WI:
            self.assertNotIn(stale, self.contracts)


if __name__ == "__main__":
    unittest.main()
