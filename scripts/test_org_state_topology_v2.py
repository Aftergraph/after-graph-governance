#!/usr/bin/env python3
"""Binding tests: org-state generation consumes platform-topology/2.0.

Run: python scripts/test_org_state_topology_v2.py
Source-level checks only (no GitHub calls): the generator script and the
org-state/1.0 contract must point current generation scope at topology/2.0
while historical snapshots remain schema-readable.
"""
import json
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
GENERATOR = REPO_ROOT / "scripts" / "org-state-verify.sh"
ORG_STATE_SCHEMA = REPO_ROOT / "docs" / "contracts" / "org-state" / "1.0.json"
TOPOLOGY = REPO_ROOT / "docs" / "platform-topology" / "2.0.json"
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "platform-topology.yml"


class OrgStateTopologyBindingTest(unittest.TestCase):
    def test_generator_uses_topology_v2(self):
        text = GENERATOR.read_text(encoding="utf-8")
        self.assertIn("docs/platform-topology/2.0.json", text)
        self.assertIn("platform-topology/2.0", text)
        self.assertNotIn('TOPOLOGY="$SCRIPT_DIR/../docs/platform-topology/1.0.json"', text)

    def test_org_state_contract_points_current_generation_to_v2(self):
        schema = json.loads(ORG_STATE_SCHEMA.read_text(encoding="utf-8"))
        self.assertIn("platform-topology/2.0", schema["description"])

    def test_all_topology_roles_fit_org_state_enum(self):
        topology = json.loads(TOPOLOGY.read_text(encoding="utf-8"))
        schema = json.loads(ORG_STATE_SCHEMA.read_text(encoding="utf-8"))
        allowed = set(schema["$defs"]["repository"]["properties"]["role"]["enum"])
        for repo in topology["repositories"]:
            self.assertIn(repo["role"], allowed, repo.get("name"))


class TopologyWorkflowTriggerTest(unittest.TestCase):
    def test_topology_gate_runs_on_merge_group(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("merge_group", text)

    def test_topology_gate_watches_org_state_contract(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("docs/contracts/org-state/1.0.json", text)


if __name__ == "__main__":
    unittest.main()
