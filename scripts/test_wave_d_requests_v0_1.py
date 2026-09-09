#!/usr/bin/env python3
"""Conformance for Wave D cross-repo build requests.

Each request under docs/superpowers/requests/ must name its owning
repository, its exact contract, and the acceptance vector IDs gating it,
and must state that governance implements nothing in the owning repo.
Every named vector ID must resolve back to
docs/platform-conformance/v0.1/vectors.json or the Task 3 fixtures.
"""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REQUESTS = ROOT / "docs/superpowers/requests"
VECTORS = ROOT / "docs/platform-conformance/v0.1/vectors.json"
WORLD_STATE = ROOT / "docs/platform-conformance/v0.1/world-state"

VECTOR_RE = re.compile(r"\b((?:EVT|CAP|GOLDEN|WA|SIT|CON|TEN)-\d{3}|ADP-(?:TG|WORKS)-\d{3})\b")
FIXTURE_RE = re.compile(r"\b((?:REBUILD|INVALIDATE|LAUNDER|CONS-REV)-\d{3})\b")

EXPECTED_REQUESTS = {
    "aie-human-governance.md": {
        "owner": "Aftergraph/aie",
        "contract": "human-governance authority binding",
        "vectors": (),
    },
    "trust-gateway-consent-ledger.md": {
        "owner": "Aftergraph/trust-gateway",
        "contract": "consent-ledger/0.1",
        "vectors": ("CON-001", "CON-002", "CON-003", "CON-004"),
        "fixtures": ("CONS-REV-001", "CONS-REV-002"),
    },
    "trust-gateway-tenant-lifecycle.md": {
        "owner": "Aftergraph/trust-gateway",
        "contract": "tenant-lifecycle/0.1",
        "vectors": ("TEN-001", "TEN-002", "TEN-003", "TEN-004", "TEN-005"),
    },
    "studio-workspace-experience.md": {
        "owner": "Aftergraph/studio",
        "contract": "human-governance authority binding",
        "vectors": (),
    },
}


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


class WaveDRequestTests(unittest.TestCase):
    def test_request_files_exist(self) -> None:
        for filename in EXPECTED_REQUESTS:
            self.assertTrue(
                (REQUESTS / filename).is_file(), f"{filename} is missing"
            )

    def test_requests_name_owner_contract_and_vectors(self) -> None:
        fixture = load_json(VECTORS)
        known_ids = {vector.get("id") for vector in fixture["vectors"]}
        known_fixtures = {
            path.stem for path in WORLD_STATE.glob("*.json") if path.is_file()
        }
        for filename, expected in EXPECTED_REQUESTS.items():
            with self.subTest(request=filename):
                text = (REQUESTS / filename).read_text(encoding="utf-8")
                self.assertIn(expected["owner"], text)
                self.assertIn(expected["contract"], text)
                named_ids = set(VECTOR_RE.findall(text))
                for vector_id in expected["vectors"]:
                    self.assertIn(vector_id, named_ids)
                for vector_id in named_ids:
                    self.assertIn(vector_id, known_ids)
                for fixture_id in FIXTURE_RE.findall(text):
                    self.assertIn(fixture_id, known_fixtures)
                for fixture_id in expected.get("fixtures", ()):
                    self.assertIn(fixture_id, text)

    def test_requests_disclaim_governance_implementation(self) -> None:
        for filename, expected in EXPECTED_REQUESTS.items():
            with self.subTest(request=filename):
                text = (REQUESTS / filename).read_text(encoding="utf-8")
                self.assertIn("Governance implements nothing", text)
                self.assertIn(expected["owner"], text)


if __name__ == "__main__":
    unittest.main()
