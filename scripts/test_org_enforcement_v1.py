#!/usr/bin/env python3
"""Phase 12 org-enforcement binding tests (TDD, source-level + data-level).

Run: python scripts/test_org_enforcement_v1.py

Enforces Phase 12 machine truth without making Governance runtime authority:
1. Unknown-repo detection: org-state-verify.sh must list the LIVE org repo set
   and fail closed when a live repository is absent from platform-topology.
2. Ephemeral lifetime: every lifecycle=temporary topology entry must declare
   an expires_at date (ephemeral fixtures retire or re-register, never linger).
3. Legacy pin: autonomous-venture-company must remain legacy-transition.
4. The topology gate workflow must execute this file.
"""
import json
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
GENERATOR = REPO_ROOT / "scripts" / "org-state-verify.sh"
TOPOLOGY = REPO_ROOT / "docs" / "platform-topology" / "2.0.json"
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "platform-topology.yml"


class UnknownRepoDetectionTest(unittest.TestCase):
    def test_generator_lists_live_org_repos(self):
        text = GENERATOR.read_text(encoding="utf-8")
        self.assertIn("orgs/", text)

    def test_generator_fails_on_unknown_live_repo(self):
        text = GENERATOR.read_text(encoding="utf-8")
        self.assertIn("unknown live repositories", text)
        # Must be a hard failure (exit 1), not a warning.
        self.assertRegex(text, r"unknown live repositories[\s\S]*?\n\s*exit 1",
                         "unknown live repos must fail the generator")


class EphemeralLifetimeTest(unittest.TestCase):
    def test_temporary_entries_declare_expiry(self):
        topology = json.loads(TOPOLOGY.read_text(encoding="utf-8"))
        temporary = [r for r in topology["repositories"]
                     if r.get("lifecycle") == "temporary"]
        self.assertTrue(temporary, "expected at least one temporary entry")
        for repo in temporary:
            self.assertIn("expires_at", repo, repo.get("name"))


class EphemeralLifetimeEnforcementTest(unittest.TestCase):
    def test_generator_fails_on_expired_ephemeral(self):
        text = GENERATOR.read_text(encoding="utf-8")
        self.assertIn("exceeding allowed lifetime", text)
        self.assertRegex(text, r"exceeding allowed lifetime[\s\S]*?\n\s*exit 1",
                         "expired ephemeral fixtures must fail the generator")

    def test_no_temporary_entry_already_expired(self):
        import datetime
        today = datetime.date.today().isoformat()
        topology = json.loads(TOPOLOGY.read_text(encoding="utf-8"))
        for repo in topology["repositories"]:
            if repo.get("lifecycle") == "temporary" and repo.get("expires_at"):
                self.assertGreaterEqual(repo["expires_at"], today, repo.get("name"))


class LegacyPinTest(unittest.TestCase):
    def test_avc_remains_legacy_transition(self):
        topology = json.loads(TOPOLOGY.read_text(encoding="utf-8"))
        avc = next(r for r in topology["repositories"]
                   if r["name"] == "autonomous-venture-company")
        self.assertEqual(avc["lifecycle"], "legacy-transition")


class EnforcementGateWiredTest(unittest.TestCase):
    def test_workflow_runs_enforcement_tests(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("test_org_enforcement_v1", text)


if __name__ == "__main__":
    unittest.main()
