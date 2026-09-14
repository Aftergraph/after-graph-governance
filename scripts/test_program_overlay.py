#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "program_overlay.py"


def load_module():
    spec = importlib.util.spec_from_file_location("program_overlay", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load program_overlay.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ProgramOverlayFixtureTests(unittest.TestCase):
    def test_canonical_fixture_validates(self):
        module = load_module()
        overlay = module.load_json(ROOT / "docs/program-overlay/mission-continuity.json")
        topology = module.load_json(ROOT / "docs/platform-topology/2.0.json")
        seams = module.load_json(ROOT / "docs/semantic-seams/0.1.json")
        self.assertEqual(module.validate_overlay(overlay, topology, seams), [])

    def test_fixture_does_not_copy_exact_git_state(self):
        overlay = json.loads((ROOT / "docs/program-overlay/mission-continuity.json").read_text())
        serialized = json.dumps(overlay)
        self.assertNotIn("remote_head_sha", serialized)
        self.assertNotIn("head_sha", serialized)
        self.assertNotIn("commit_sha", serialized)


if __name__ == "__main__":
    unittest.main()
