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


class OrgStateTopologyBindingTest(unittest.TestCase):
    def test_generator_uses_topology_v2(self):
        text = GENERATOR.read_text(encoding="utf-8")
        self.assertIn("docs/platform-topology/2.0.json", text)
        self.assertIn("platform-topology/2.0", text)
        self.assertNotIn('TOPOLOGY="$SCRIPT_DIR/../docs/platform-topology/1.0.json"', text)

    def test_org_state_contract_points_current_generation_to_v2(self):
        schema = json.loads(ORG_STATE_SCHEMA.read_text(encoding="utf-8"))
        self.assertIn("platform-topology/2.0", schema["description"])


if __name__ == "__main__":
    unittest.main()
