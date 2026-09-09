#!/usr/bin/env python3
"""Conformance for Wave H cross-repo build requests (Promotion gates).

docs/superpowers/requests/promotion-gates.md must name its owning
repositories (Aftergraph/model-registry, Aftergraph/afm,
Aftergraph/llm-research-development for model promotion,
Aftergraph/skills-vault for skill supply chain, Aftergraph/runtime
for routing/workflow gates, with continuum/sentinel as verifier
allies), its exact contract (promotion-gates/0.1 or a versioned
successor) plus the seam binding (docs/PROMOTION-GATES-V1.md), and the
acceptance vector IDs gating it. Every named PROM vector ID must
resolve back to docs/platform-conformance/v0.1/vectors.json. The
request must state that governance implements nothing in the owning
repos, restate the canonical boundary (promotion moves nothing without
independent verification; challenger never promotes itself; gates +
registry evidence only; evaluators never score their own execution as
Wave E inheritance), and carry an evidence-gated appendix listing
production-trace/model characterization items marked
BLOCKED_ON_PROMOTION_EVIDENCE with no PASS claims.
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

VECTOR_RE = re.compile(r"\b(PROM-\d{3})\b")
CONTRACT_RE = re.compile(r"promotion-gates/0\.[1-9]\d*")

REQUEST = "promotion-gates.md"
OWNERS = (
    "Aftergraph/model-registry",
    "Aftergraph/afm",
    "Aftergraph/llm-research-development",
    "Aftergraph/skills-vault",
    "Aftergraph/runtime",
)
VERIFIER_ALLIES = (
    "continuum",
    "sentinel",
)
BINDING = "docs/PROMOTION-GATES-V1.md"
EXPECTED_VECTORS = (
    "PROM-001", "PROM-002", "PROM-003", "PROM-004", "PROM-005",
    "PROM-006", "PROM-007",
    "PROM-010", "PROM-011", "PROM-012", "PROM-013", "PROM-014",
    "PROM-015", "PROM-016", "PROM-017",
    "PROM-020", "PROM-021", "PROM-022", "PROM-023", "PROM-024",
    "PROM-025", "PROM-026", "PROM-027",
    "PROM-030", "PROM-031", "PROM-032", "PROM-033", "PROM-034",
    "PROM-035", "PROM-036", "PROM-037",
)
EVIDENCE_GATED_ITEMS = (
    "production-trace characterization",
    "live-model quality characterization",
    "live-model latency characterization",
    "live-model capability characterization",
)


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def appendix_of(text: str) -> str:
    match = re.search(r"evidence-gated appendix", text, re.IGNORECASE)
    assert match is not None, "evidence-gated appendix section is missing"
    return text[match.start():]


class WaveHRequestTests(unittest.TestCase):
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

    def test_request_restates_canonical_boundary(self) -> None:
        text = (REQUESTS / REQUEST).read_text(encoding="utf-8")
        self.assertRegex(text, re.compile(r"canonical boundary", re.IGNORECASE))
        self.assertIn("nothing without independent verification", text)
        self.assertIn("challenger never promotes itself", text)
        self.assertIn("registry evidence", text)
        self.assertIn("Evaluators never score their own execution", text)
        self.assertIn("Wave E", text)

    def test_request_evidence_gated_appendix(self) -> None:
        text = (REQUESTS / REQUEST).read_text(encoding="utf-8")
        appendix = appendix_of(text)
        for item in EVIDENCE_GATED_ITEMS:
            self.assertIn(item, appendix)
        self.assertGreaterEqual(
            len(re.findall(r"BLOCKED_ON_PROMOTION_EVIDENCE", appendix)),
            len(EVIDENCE_GATED_ITEMS),
        )
        self.assertNotRegex(appendix, re.compile(r"\bPASS\b"))


if __name__ == "__main__":
    unittest.main()
