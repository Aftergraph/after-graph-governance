#!/usr/bin/env python3
"""Conformance for Wave G cross-repo build requests (Voice edge).

docs/superpowers/requests/voice-edge.md must name its owning
repositories (Aftergraph/studio, Aftergraph/wi-frontend, Aftergraph/runtime
as applicable, with trust-gateway admission, works-execution durable
execution, and consent-ledger-owned stores as durable owners), its exact
contract (voice-interaction/0.1 or a versioned successor) plus the seam
binding (docs/VOICE-INTERACTION-V1.md), and the acceptance vector IDs
gating it. Every named VOI vector ID must resolve back to
docs/platform-conformance/v0.1/vectors.json. The request must state that
governance implements nothing in the owning repos, restate the canonical
boundary (Interaction Fabric edge; no durable identity/state in sessions;
continuity via correlation/provenance, never moved authority;
transcript != identity and speaker != principal as Wave F inheritance;
Trust Gateway admission/egress), and carry an evidence-gated appendix
listing realtime raw-audio streaming and device/API characterization items
marked BLOCKED_ON_VOICE_DEVICE_API_EVIDENCE with no PASS claims.
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

VECTOR_RE = re.compile(r"\b(VOI-\d{3})\b")
CONTRACT_RE = re.compile(r"voice-interaction/0\.[1-9]\d*")

REQUEST = "voice-edge.md"
OWNERS = (
    "Aftergraph/studio",
    "Aftergraph/wi-frontend",
    "Aftergraph/runtime",
)
DURABLE_OWNERS = (
    "trust-gateway",
    "works-execution",
    "consent-ledger",
)
BINDING = "docs/VOICE-INTERACTION-V1.md"
EXPECTED_VECTORS = (
    "VOI-001", "VOI-002", "VOI-003", "VOI-004", "VOI-005",
    "VOI-006", "VOI-007",
    "VOI-010", "VOI-011", "VOI-012", "VOI-013", "VOI-014",
    "VOI-015", "VOI-016", "VOI-017",
    "VOI-020", "VOI-021", "VOI-022", "VOI-023", "VOI-024",
    "VOI-025", "VOI-026", "VOI-027",
)
EVIDENCE_GATED_ITEMS = (
    "realtime raw-audio streaming characterization",
    "device audio-capture characterization",
    "microphone-array characterization",
    "voice device-API characterization",
)


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def appendix_of(text: str) -> str:
    match = re.search(r"evidence-gated appendix", text, re.IGNORECASE)
    assert match is not None, "evidence-gated appendix section is missing"
    return text[match.start():]


class WaveGRequestTests(unittest.TestCase):
    def test_request_file_exists(self) -> None:
        self.assertTrue((REQUESTS / REQUEST).is_file(), f"{REQUEST} is missing")

    def test_request_names_owners_contract_binding_and_vectors(self) -> None:
        fixture = load_json(VECTORS)
        known_ids = {vector.get("id") for vector in fixture["vectors"]}
        text = (REQUESTS / REQUEST).read_text(encoding="utf-8")
        for owner in OWNERS:
            self.assertIn(owner, text)
        for durable in DURABLE_OWNERS:
            self.assertIn(durable, text)
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
        for owner in OWNERS:
            self.assertIn(owner, text)

    def test_request_restates_canonical_boundary(self) -> None:
        text = (REQUESTS / REQUEST).read_text(encoding="utf-8")
        self.assertRegex(text, re.compile(r"canonical boundary", re.IGNORECASE))
        self.assertIn("Interaction Fabric edge", text)
        self.assertIn("no durable identity", text)
        self.assertIn("correlation", text)
        self.assertIn("provenance", text)
        self.assertIn("never moved authority", text)
        self.assertIn("transcript != identity", text)
        self.assertIn("speaker != principal", text)
        self.assertIn("Wave F", text)
        self.assertIn("Trust Gateway", text)
        self.assertIn("admission", text)
        self.assertIn("egress", text)

    def test_request_evidence_gated_appendix(self) -> None:
        text = (REQUESTS / REQUEST).read_text(encoding="utf-8")
        appendix = appendix_of(text)
        for item in EVIDENCE_GATED_ITEMS:
            self.assertIn(item, appendix)
        self.assertGreaterEqual(
            len(re.findall(r"BLOCKED_ON_VOICE_DEVICE_API_EVIDENCE", appendix)),
            len(EVIDENCE_GATED_ITEMS),
        )
        self.assertNotRegex(appendix, re.compile(r"\bPASS\b"))


if __name__ == "__main__":
    unittest.main()
