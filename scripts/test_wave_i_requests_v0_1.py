#!/usr/bin/env python3
"""Conformance for Wave I cross-repo build requests (AVC retirement).

docs/superpowers/requests/avc-retirement.md must name its owning
repositories (Aftergraph/autonomous-venture-company for phased
extraction, Aftergraph/skills-vault for skill migration,
Aftergraph/runtime + Aftergraph/aie + Aftergraph/trust-gateway +
Aftergraph/works-execution for consumer removal, with
continuum/sentinel as verifier allies), its exact contract
(avc-dissolution/0.1 or a versioned successor) plus the binding
(docs/AVC-RETIREMENT-V1.md), and the acceptance vector IDs gating
it. Every named RET vector ID must resolve back to
docs/platform-conformance/v0.1/vectors.json. The request must state
that governance implements nothing in the owning repos and NEVER
executes archival/deletion, restate the canonical boundary
(ledger-only retirement with every gate evidenced; no ownership loss
with active consumers/canonical-doc refs; final archive action
REQUIRES_EXPLICIT_OWNER_AUTHORIZATION), and carry an evidence-gated
appendix listing owner-execution-dependent items marked
BLOCKED_ON_OWNER_EXECUTION with no PASS claims.
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

VECTOR_RE = re.compile(r"\b(RET-\d{3})\b")
CONTRACT_RE = re.compile(r"avc-dissolution/0\.[1-9]\d*")

REQUEST = "avc-retirement.md"
OWNERS = (
    "Aftergraph/autonomous-venture-company",
    "Aftergraph/skills-vault",
    "Aftergraph/runtime",
    "Aftergraph/aie",
    "Aftergraph/trust-gateway",
    "Aftergraph/works-execution",
)
VERIFIER_ALLIES = (
    "continuum",
    "sentinel",
)
BINDING = "docs/AVC-RETIREMENT-V1.md"
EXPECTED_VECTORS = (
    "RET-001", "RET-002", "RET-003", "RET-004", "RET-005",
    "RET-006", "RET-007",
    "RET-010", "RET-011", "RET-012", "RET-013", "RET-014",
    "RET-015", "RET-016", "RET-017",
    "RET-020", "RET-021", "RET-022", "RET-023", "RET-024",
    "RET-025", "RET-026", "RET-027",
    "RET-030", "RET-031", "RET-032", "RET-033", "RET-034",
    "RET-035", "RET-036", "RET-037",
)
EVIDENCE_GATED_ITEMS = (
    "phased extraction execution",
    "skill migration execution",
    "consumer-removal execution",
    "live Aftergraph-only Golden Mission execution",
    "legacy-repo archive action",
)


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def appendix_of(text: str) -> str:
    match = re.search(r"evidence-gated appendix", text, re.IGNORECASE)
    assert match is not None, "evidence-gated appendix section is missing"
    return text[match.start():]


class WaveIRequestTests(unittest.TestCase):
    def test_request_file_exists(self) -> None:
        self.assertTrue((REQUESTS / REQUEST).is_file(), f"{REQUEST} is missing")

    def test_request_names_owners_contract_binding_and_vectors(self) -> None:
        fixture = load_json(VECTORS)
        known_ids = {vector.get("id") for vector in fixture["vectors"]}
        text = (REQUESTS / REQUEST).read_text(encoding="utf-8")
        for owner in OWNERS:
            self.assertIn(owner, text)
        for ally in VERIFIER_ALLIES:
            self.assertIn(ally, text)
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
        self.assertIn("NEVER executes archival/deletion", text)

    def test_request_restates_canonical_boundary(self) -> None:
        text = (REQUESTS / REQUEST).read_text(encoding="utf-8")
        self.assertRegex(text, re.compile(r"canonical boundary", re.IGNORECASE))
        self.assertIn("through the ledger", text)
        self.assertIn("every gate evidenced", text)
        self.assertIn("loses ownership while an active consumer", text)
        self.assertIn("canonical doc", text)
        self.assertIn("REQUIRES_EXPLICIT_OWNER_AUTHORIZATION", text)

    def test_request_evidence_gated_appendix(self) -> None:
        text = (REQUESTS / REQUEST).read_text(encoding="utf-8")
        appendix = appendix_of(text)
        for item in EVIDENCE_GATED_ITEMS:
            self.assertIn(item, appendix)
        self.assertGreaterEqual(
            len(re.findall(r"BLOCKED_ON_OWNER_EXECUTION", appendix)),
            len(EVIDENCE_GATED_ITEMS),
        )
        self.assertNotRegex(appendix, re.compile(r"\bPASS\b"))


if __name__ == "__main__":
    unittest.main()
