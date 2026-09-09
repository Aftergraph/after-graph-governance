#!/usr/bin/env python3
"""Rebuild/currentness/invalidation conformance for World State.

World State is a rebuildable projection over provenance-bearing canonical
sources, never writable truth. These tests assert deterministic fixture
outcomes: post-failure rebuild marks unavailable sources stale/unknown,
source deletion invalidates derived state per provenance without rewriting
audit history, timestamp refresh without new observation fails closed, and
consent revocation invalidates downstream use selected by consent/purpose
lineage while audit history is preserved byte-for-byte.
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "docs/platform-conformance/v0.1/world-state"

REBUILD = "REBUILD-001"
INVALIDATE = "INVALIDATE-001"
LAUNDER = "LAUNDER-001"
CONS_REV_DERIVED = "CONS-REV-001"
CONS_REV_DOWNSTREAM = "CONS-REV-002"


def load_fixture(name: str) -> Any:
    with (FIXTURES / name).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def rebuild_projection(fixture: dict[str, Any]) -> list[dict[str, Any]]:
    availability = {
        source["source"]: source["available"] for source in fixture["sources"]
    }
    rebuilt = []
    for assertion in fixture["projection_before"]:
        if availability.get(assertion["source"]):
            rebuilt.append(dict(assertion))
        else:
            rebuilt.append(
                {
                    "assertion_id": assertion["assertion_id"],
                    "source": assertion["source"],
                    "epistemic": "unknown",
                    "currentness": "stale",
                }
            )
    return rebuilt


def apply_source_deletion(fixture: dict[str, Any]) -> dict[str, Any]:
    deleted = fixture["event"]["deleted_source"]
    derived = [
        entry
        for entry in fixture["derived_before"]
        if deleted not in entry["provenance"]
    ]
    return {"derived_after": derived, "audit_after": list(fixture["audit_before"])}


def apply_consent_revocation(fixture: dict[str, Any]) -> dict[str, Any]:
    revocation = fixture["revocation"]
    revoked_source = revocation["source"]
    revoked_purpose = revocation["purpose"]
    derived_after = [
        entry
        for entry in fixture.get("derived_before", [])
        if not (
            entry["source"] == revoked_source and entry["purpose"] == revoked_purpose
        )
    ]
    ingestion_after = [
        {"source": attempt["source"], "admitted": attempt["source"] != revoked_source}
        for attempt in fixture.get("ingestion_before", [])
    ]
    bundles_after = [
        bundle
        for bundle in fixture.get("bundles_before", [])
        if not (
            revoked_source in bundle["sources"] and revoked_purpose in bundle["purposes"]
        )
    ]
    future_after = [
        {
            "source": item["source"],
            "purpose": item["purpose"],
            "blocked": item["source"] == revoked_source and item["purpose"] == revoked_purpose,
        }
        for item in fixture.get("future_before", [])
    ]
    return {
        "derived_after": derived_after,
        "ingestion_after": ingestion_after,
        "bundles_after": bundles_after,
        "future_after": future_after,
        "audit_after": list(fixture.get("audit_before", [])),
    }


def laundering_errors(assertion: dict[str, Any]) -> list[str]:
    errors = []
    if assertion["observed_at"] > assertion["evidence_observed_at"]:
        errors.append("assertion observation postdates its evidence without new observation")
    if assertion["currentness"] == "current":
        errors.append("re-stamped state must be represented as stale or unknown, not current")
    return errors


class WorldStateConformanceTests(unittest.TestCase):
    def test_rebuild_marks_unavailable_sources_stale_unknown(self) -> None:
        fixture = load_fixture(f"{REBUILD}.json")
        self.assertEqual(fixture["expected"], "accept")
        self.assertEqual(rebuild_projection(fixture), fixture["projection_after"])

    def test_source_deletion_invalidates_derived_state_only(self) -> None:
        fixture = load_fixture(f"{INVALIDATE}.json")
        self.assertEqual(fixture["expected"], "accept")
        result = apply_source_deletion(fixture)
        self.assertEqual(result["derived_after"], fixture["derived_after"])
        self.assertEqual(result["audit_after"], fixture["audit_before"])

    def test_timestamp_refresh_without_observation_fails_closed(self) -> None:
        fixture = load_fixture(f"{LAUNDER}.json")
        self.assertEqual(fixture["expected"], "reject")
        self.assertTrue(laundering_errors(fixture["assertion"]))

    def test_revocation_invalidates_derived_per_lineage(self) -> None:
        fixture = load_fixture(f"{CONS_REV_DERIVED}.json")
        self.assertEqual(fixture["expected"], "accept")
        result = apply_consent_revocation(fixture)
        self.assertEqual(result["derived_after"], fixture["derived_after"])
        self.assertEqual(result["audit_after"], fixture["audit_before"])

    def test_revocation_denies_ingestion_bundles_future_processing(self) -> None:
        fixture = load_fixture(f"{CONS_REV_DOWNSTREAM}.json")
        self.assertEqual(fixture["expected"], "accept")
        result = apply_consent_revocation(fixture)
        self.assertEqual(result["ingestion_after"], fixture["ingestion_after"])
        self.assertEqual(result["bundles_after"], fixture["bundles_after"])
        self.assertEqual(result["future_after"], fixture["future_after"])
        self.assertEqual(result["audit_after"], fixture["audit_before"])


if __name__ == "__main__":
    unittest.main()
