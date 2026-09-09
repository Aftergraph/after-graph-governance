#!/usr/bin/env python3
"""Conformance for Wave B cross-repo build requests.

Each request under docs/superpowers/requests/ must name its owning
repository, its exact contract, and the acceptance vector IDs gating it,
and must state that governance implements nothing in the owning repo.
A request existing on disk is not a verified capability: every named
vector ID must resolve back to docs/platform-conformance/v0.1/vectors.json.
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

VECTOR_RE = re.compile(r"\b((?:EVT|CAP|GOLDEN)-\d{3}|ADP-(?:TG|WORKS)-\d{3})\b")

EXPECTED_REQUESTS = {
    "trust-gateway-event-ref-adapter.md": {
        "owner": "Aftergraph/trust-gateway",
        "contract": "platform-event-ref/0.1",
        "vectors": ("ADP-TG-001", "ADP-TG-002"),
    },
    "works-execution-event-ref-adapter.md": {
        "owner": "Aftergraph/works-execution",
        "contract": "platform-event-ref/0.1",
        "vectors": ("ADP-WORKS-001", "ADP-WORKS-002"),
    },
    "runtime-capability-resolver-fallback.md": {
        "owner": "Aftergraph/runtime",
        "contract": "capability-action/0.1",
        "vectors": ("CAP-001", "CAP-002", "CAP-003", "CAP-004", "CAP-005"),
    },
    "golden-mission-runner.md": {
        "owner": "Aftergraph/works-execution",
        "contract": "golden-mission/0.1",
        "vectors": ("GOLDEN-001", "GOLDEN-002", "GOLDEN-003"),
    },
}


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


class WaveBRequestTests(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
