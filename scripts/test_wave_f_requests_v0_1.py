#!/usr/bin/env python3
"""Conformance for Wave F cross-repo build requests (Pocket connector).

docs/superpowers/requests/pocket-connector.md must name its owning
repository (Aftergraph/wi-backend as the Pocket provider-subsystem owner
under Wie), its exact contract (pocket-source/0.1 or a versioned
successor) plus the seam binding (docs/POCKET-SOURCE-V1.md), and the
acceptance vector IDs gating it. Every named PCK vector ID must resolve
back to docs/platform-conformance/v0.1/vectors.json. The request must
state that governance implements nothing in the owning repo, restate the
plane mapping (REST = reconciliation, webhooks = event, MCP = optional
interactive) and the canonical boundary, and carry a hardware-gated
appendix listing physical-device characterization items marked
BLOCKED_ON_POCKET_HARDWARE with no PASS claims.
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

VECTOR_RE = re.compile(r"\b(PCK-\d{3})\b")
CONTRACT_RE = re.compile(r"pocket-source/0\.[1-9]\d*")

REQUEST = "pocket-connector.md"
OWNER = "Aftergraph/wi-backend"
BINDING = "docs/POCKET-SOURCE-V1.md"
EXPECTED_VECTORS = (
    "PCK-001", "PCK-002", "PCK-003", "PCK-004", "PCK-005",
    "PCK-006", "PCK-007",
    "PCK-010", "PCK-011", "PCK-012", "PCK-013", "PCK-014",
    "PCK-015", "PCK-016", "PCK-017",
    "PCK-020", "PCK-021", "PCK-022", "PCK-023", "PCK-024",
    "PCK-025", "PCK-026", "PCK-027",
)
HARDWARE_ITEMS = (
    "device audio-capture characterization",
    "microphone-array characterization",
    "realtime-audio pipeline characterization",
    "acoustic-environment characterization",
)


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def appendix_of(text: str) -> str:
    match = re.search(r"hardware-gated appendix", text, re.IGNORECASE)
    assert match is not None, "hardware-gated appendix section is missing"
    return text[match.start():]


class WaveFRequestTests(unittest.TestCase):
    def test_request_file_exists(self) -> None:
        self.assertTrue((REQUESTS / REQUEST).is_file(), f"{REQUEST} is missing")

    def test_request_names_owner_contract_binding_and_vectors(self) -> None:
        fixture = load_json(VECTORS)
        known_ids = {vector.get("id") for vector in fixture["vectors"]}
        text = (REQUESTS / REQUEST).read_text(encoding="utf-8")
        self.assertIn(OWNER, text)
        self.assertIn("provider subsystem", text)
        self.assertIn("Wie", text)
        self.assertRegex(text, CONTRACT_RE)
        self.assertIn(BINDING, text)
        named_ids = set(VECTOR_RE.findall(text))
        for vector_id in EXPECTED_VECTORS:
            self.assertIn(vector_id, named_ids)
        for vector_id in named_ids:
            self.assertIn(vector_id, known_ids)

    def test_request_disclaims_governance_implementation(self) -> None:
        text = (REQUESTS / REQUEST).read_text(encoding="utf-8")
        self.assertIn("Governance implements nothing", text)
        self.assertIn(OWNER, text)

    def test_request_restates_plane_mapping(self) -> None:
        text = (REQUESTS / REQUEST).read_text(encoding="utf-8")
        self.assertIn("REST = reconciliation", text)
        self.assertIn("webhooks = event", text)
        self.assertIn("MCP = optional interactive", text)

    def test_request_restates_canonical_boundary(self) -> None:
        text = (REQUESTS / REQUEST).read_text(encoding="utf-8")
        self.assertRegex(text, re.compile(r"canonical boundary", re.IGNORECASE))
        self.assertIn("never canonical", text)

    def test_request_hardware_gated_appendix(self) -> None:
        text = (REQUESTS / REQUEST).read_text(encoding="utf-8")
        appendix = appendix_of(text)
        for item in HARDWARE_ITEMS:
            self.assertIn(item, appendix)
        self.assertGreaterEqual(
            len(re.findall(r"BLOCKED_ON_POCKET_HARDWARE", appendix)),
            len(HARDWARE_ITEMS),
        )
        self.assertNotRegex(appendix, re.compile(r"\bPASS\b"))


if __name__ == "__main__":
    unittest.main()
