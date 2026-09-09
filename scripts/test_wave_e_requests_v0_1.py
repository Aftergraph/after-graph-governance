#!/usr/bin/env python3
"""Conformance for Wave E cross-repo build requests.

Each request under docs/superpowers/requests/ must name its owning
repository, its exact contract, and the acceptance vector IDs gating it,
and must state that governance implements nothing in the owning repo.
Every named vector ID must resolve back to
docs/platform-conformance/v0.1/vectors.json.
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

VECTOR_RE = re.compile(r"\b((?:EVT|CAP|GOLDEN|WA|SIT|CON|TEN|PRO|ORG|EVAL)-\d{3}|ADP-(?:TG|WORKS)-\d{3})\b")

EXPECTED_REQUESTS = {
    "wi-proactivity-sensing.md": {
        "owner": "Aftergraph/wi-backend",
        "contract": "proactivity/0.1",
        "vectors": ("PRO-001", "PRO-003", "PRO-005"),
    },
    "runtime-opportunity-recovery.md": {
        "owner": "Aftergraph/runtime",
        "contract": "proactivity/0.1",
        "vectors": ("PRO-004",),
    },
    "cron-observation-sensing.md": {
        "owner": "Aftergraph/aftergraph-cron-fabric",
        "contract": "proactivity/0.1",
        "vectors": ("PRO-002", "PRO-006"),
    },
    "org-delegation-evals.md": {
        "owner": "Aftergraph/runtime",
        "contract": "org-delegation/0.1",
        "vectors": (
            "ORG-001",
            "ORG-002",
            "ORG-003",
            "ORG-004",
            "EVAL-001",
            "EVAL-002",
            "EVAL-003",
        ),
    },
}


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


class WaveERequestTests(unittest.TestCase):
    def test_request_files_exist(self) -> None:
        for filename in EXPECTED_REQUESTS:
            self.assertTrue(
                (REQUESTS / filename).is_file(), f"{filename} is missing"
            )

    def test_requests_name_owner_contract_and_vectors(self) -> None:
        fixture = load_json(VECTORS)
        known_ids = {vector.get("id") for vector in fixture["vectors"]}
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

    def test_requests_disclaim_governance_implementation(self) -> None:
        for filename, expected in EXPECTED_REQUESTS.items():
            with self.subTest(request=filename):
                text = (REQUESTS / filename).read_text(encoding="utf-8")
                self.assertIn("Governance implements nothing", text)
                self.assertIn(expected["owner"], text)

    def test_delegation_request_requires_evaluator_independence(self) -> None:
        text = (REQUESTS / "org-delegation-evals.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("agent-eval/0.1", text)
        self.assertRegex(text, re.compile(r"evaluator independence", re.IGNORECASE))


if __name__ == "__main__":
    unittest.main()
