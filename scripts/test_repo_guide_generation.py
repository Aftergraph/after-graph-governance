#!/usr/bin/env python3
"""Tests for the repository agent-guide generator.

Run: python scripts/test_repo_guide_generation.py
 or: python -m pytest scripts/test_repo_guide_generation.py -q

Self-contained (stdlib unittest only, no network, no git required). Each case builds a throwaway
workspace in a temporary directory and runs the generator against it, so the assertions are about the
generator's observable contract rather than its internals:

  1. a repository with a package manifest gets its own commands, not invented ones;
  2. a Makefile target is preferred where the manifest has no test script;
  3. a repository with no manifest and no recorded executed verification is told so, and no command is
     invented for it;
  4. a recorded executed verification row is quoted with its result and exact SHA;
  5. Ratchet rules survive regeneration (the failure that motivated this test: --force used to wipe them);
  6. a hand-written guide is never overwritten, and a generator-owned guide is only replaced with --force.
"""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
GENERATOR = HERE / "gen_repo_guides.py"

HEAD = "0" * 40


def write(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def make_workspace(tmp: Path, repos: dict, ci_results=None):
    """repos: name -> dict of files to create relative to that repo directory."""
    inv = {"repos": []}
    for name, files in repos.items():
        for rel, content in files.items():
            write(tmp / name / rel, content)
        inv["repos"].append({"name": name, "description": f"{name} test fixture",
                             "local": {"present": True, "head": HEAD, "branch": "main"}})
    write(tmp / "REPOSITORY_INVENTORY.json", json.dumps(inv))
    write(tmp / "CI_COMMAND_INVENTORY.json", json.dumps({"repos": [{"name": n} for n in repos]}))
    write(tmp / "CI_RESULTS.json", json.dumps({"generated_at": "2026-01-01T00:00:00+00:00",
                                               "scope": "test scope",
                                               "results": ci_results or []}))


def run_generator(root: Path, *args):
    return subprocess.run([sys.executable, str(GENERATOR), "--root", str(root), *args],
                          capture_output=True, text=True)


class GuideGenerationTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def guide(self, name):
        return (self.tmp / name / "AGENTS.md").read_text(encoding="utf-8")

    def test_package_manifest_commands_are_used_verbatim(self):
        make_workspace(self.tmp, {"node-repo": {"package.json": json.dumps(
            {"name": "x", "scripts": {"build": "tsc", "test": "vitest run", "lint": "eslint ."}})}})
        run_generator(self.tmp)
        text = self.guide("node-repo")
        self.assertIn("TEST:      npm run test", text)
        self.assertIn("BUILD:     npm run build", text)
        self.assertIn("LINT:      npm run lint", text)
        # a script that does not exist must not be invented
        self.assertIn("VERIFY:    — not detected in this repository", text)

    def test_makefile_target_is_used_when_no_manifest(self):
        make_workspace(self.tmp, {"c-repo": {"Makefile": "all:\n\techo x\ntest:\n\techo t\n"}})
        run_generator(self.tmp)
        self.assertIn("make test", self.guide("c-repo"))

    def test_repository_without_sensor_is_not_given_an_invented_command(self):
        make_workspace(self.tmp, {"docs-repo": {"README.md": "hi\n"}})
        run_generator(self.tmp)
        text = self.guide("docs-repo")
        self.assertIn("no recorded computational sensor", text)
        self.assertIn("Do not invent a build or test command", text)
        self.assertIn("BUILD:     — not detected in this repository", text)

    def test_recorded_evidence_is_quoted_with_its_sha(self):
        make_workspace(self.tmp, {"py-repo": {"README.md": "x\n"}},
                       ci_results=[{"repo": "py-repo", "command": "python3 -m pytest -q",
                                    "status": "passed", "sha": "abcdef1234567890",
                                    "note": "12 tests"}])
        run_generator(self.tmp)
        text = self.guide("py-repo")
        self.assertIn("python3 -m pytest -q", text)
        self.assertIn("passed", text)
        self.assertIn("abcdef12", text)
        self.assertNotIn("no recorded computational sensor", text)

    def test_ratchet_rules_survive_regeneration(self):
        make_workspace(self.tmp, {"node-repo": {"package.json": json.dumps({"scripts": {"test": "vitest"}})}})
        run_generator(self.tmp)
        rule = "- 2026-01-01: agent guessed `npm test` in a repository with no test script."
        text = self.guide("node-repo").replace(
            "  (none recorded yet — this guide has not yet accumulated failure-derived rules)", rule)
        write(self.tmp / "node-repo" / "AGENTS.md", text)

        run_generator(self.tmp, "--force")
        regenerated = self.guide("node-repo")
        self.assertEqual(regenerated.count(rule), 1, "the rule must survive exactly once")
        self.assertNotIn("none recorded yet", regenerated)
        evidence = json.loads((self.tmp / "GUIDE_GENERATION_EVIDENCE.json").read_text())
        self.assertEqual(evidence["results"][0]["ratchet_rules_preserved"], 1)

    def test_hand_written_guide_is_never_overwritten(self):
        make_workspace(self.tmp, {"hand-written": {"README.md": "x\n"}})
        write(self.tmp / "hand-written" / "AGENTS.md", "# hand written, no generated marker\n")
        run_generator(self.tmp, "--force")
        self.assertEqual(self.guide("hand-written"), "# hand written, no generated marker\n")

    def test_generated_guide_is_replaced_only_with_force(self):
        make_workspace(self.tmp, {"node-repo": {"package.json": json.dumps({"scripts": {"test": "vitest"}})}})
        run_generator(self.tmp)
        write(self.tmp / "node-repo" / "package.json",
              json.dumps({"scripts": {"test": "jest", "build": "tsc"}}))

        run_generator(self.tmp)
        self.assertIn("npm run test", self.guide("node-repo"))
        self.assertNotIn("BUILD:     npm run build", self.guide("node-repo"))

        run_generator(self.tmp, "--force")
        self.assertIn("BUILD:     npm run build", self.guide("node-repo"))


class ScorecardTests(unittest.TestCase):
    """The scorecard is the measurement contract: these pin its output shape, not its numbers."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        make_workspace(self.tmp, {"covered": {"README.md": "x\n"}, "uncovered": {"README.md": "y\n"}},
                       ci_results=[{"repo": "covered", "command": "make test", "status": "passed",
                                    "sha": "deadbeefcafe", "note": "fixture"}])

    def tearDown(self):
        self._tmp.cleanup()

    def scorecard(self, *args):
        out = self.tmp / "AFTERGRAPH_HARNESS_SCORECARD.json"
        proc = subprocess.run([sys.executable, str(HERE / "harness_scorecard.py"),
                               "--root", str(self.tmp), "--write", *args],
                              capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        return json.loads(out.read_text(encoding="utf-8"))

    def test_coverage_is_measured_not_asserted(self):
        run_generator(self.tmp)
        data = self.scorecard()
        self.assertEqual(data["guide_coverage"]["with_guide"], 2)
        self.assertEqual(data["guide_coverage"]["total_present"], 2)
        self.assertEqual(data["guide_coverage"]["pct"], 100.0)

    def test_repository_without_a_recorded_sensor_is_listed(self):
        data = self.scorecard()
        self.assertEqual(data["sensor_coverage"]["with_recorded_executed_verification"], 1)
        self.assertIn("uncovered", data["sensor_coverage"]["no_recorded_sensor"])

    def test_ratchet_rules_and_staleness_are_reported(self):
        run_generator(self.tmp)
        guide = self.tmp / "covered" / "AGENTS.md"
        guide.write_text(guide.read_text(encoding="utf-8").replace(
            "  (none recorded yet — this guide has not yet accumulated failure-derived rules)",
            "- 2026-01-01: agent guessed a command instead of reading this file."), encoding="utf-8")
        data = self.scorecard()
        self.assertEqual(data["ratchet_rules_total"], 1)
        self.assertIsInstance(data["guide_staleness_days_median"], float)


if __name__ == "__main__":
    unittest.main(verbosity=2)
