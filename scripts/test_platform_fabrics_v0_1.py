#!/usr/bin/env python3
"""Contract-level conformance for the first Aftergraph platform fabrics slice.

This is deliberately narrower than full platform conformance. It verifies the
machine-readable projection and semantic-action invariants introduced in v0.1
and a small causal-chain fixture set. Cross-repository runtime adapters remain a
separate gate.
"""

from __future__ import annotations

import json
import re
import unittest
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
EVENT_SCHEMA = ROOT / "docs/contracts/platform-event-ref/0.1.json"
CAPABILITY_SCHEMA = ROOT / "docs/contracts/capability-action/0.1.json"
VECTORS = ROOT / "docs/platform-conformance/v0.1/vectors.json"

HEX32 = r"[a-f0-9]{32}"
ID_PATTERNS = {
    "event_id": re.compile(rf"^evt_{HEX32}$"),
    "execution_context_id": re.compile(rf"^ctx_{HEX32}$"),
    "tenant_id": re.compile(rf"^ten_{HEX32}$"),
    "principal_id": re.compile(rf"^prn_{HEX32}$"),
    "authority_lease_id": re.compile(rf"^auth_{HEX32}$"),
    "work_id": re.compile(rf"^wrk_{HEX32}$"),
    "admission_decision_id": re.compile(rf"^pdr_{HEX32}$"),
    "action_decision_id": re.compile(rf"^pdr_{HEX32}$"),
    "trace_id": re.compile(rf"^trc_{HEX32}$"),
    "action_id": re.compile(rf"^act_{HEX32}$"),
}

EVENT_REQUIRED = {
    "schema",
    "event_id",
    "source",
    "event_type",
    "occurred_at",
    "subject_ref",
    "correlation",
    "payload_ref",
    "integrity_ref",
    "classification",
}
EVENT_ALLOWED = set(EVENT_REQUIRED)
CORRELATION_ALLOWED = {
    "execution_context_id",
    "tenant_id",
    "principal_id",
    "mission_id",
    "authority_lease_id",
    "work_id",
    "admission_decision_id",
    "trace_id",
    "action_id",
}
CORRELATION_REQUIRED = {"tenant_id", "mission_id", "trace_id", "action_id"}
EVENT_CLASSES = {"authority", "enforcement", "runtime", "execution", "verification", "research"}

CAP_REQUIRED = {
    "schema",
    "action_id",
    "mission_id",
    "semantic_capability",
    "effect_class",
    "risk_class",
    "required_authority",
    "input_ref",
    "expected_output_ref",
    "implementations",
    "selection_policy",
    "verification_required",
}
CAP_ALLOWED = set(CAP_REQUIRED)
CAPABILITY_RE = re.compile(r"^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)+$")
EFFECT_CLASSES = {"read_only", "reversible_write", "consequential_write", "external_effect"}
IMPLEMENTATION_KINDS = {
    "native_tool",
    "mcp",
    "a2a",
    "python",
    "shell",
    "browser",
    "computer",
    "database",
    "workflow",
}
IMPLEMENTATION_AVAILABILITY = {"available", "degraded", "unavailable"}
SELECTION_KEYS = {
    "prefer_verified_success",
    "minimize_cost",
    "minimize_latency",
    "minimize_context_pressure",
    "allow_fallback",
}


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise AssertionError(f"{path} must contain a JSON object")
    return value


def parse_rfc3339(value: Any) -> bool:
    if not isinstance(value, str) or not value:
        return False
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        datetime.fromisoformat(normalized)
    except ValueError:
        return False
    return True


def nonempty_string(value: Any, *, maximum: int = 512) -> bool:
    return isinstance(value, str) and 0 < len(value) <= maximum


def valid_id(field: str, value: Any) -> bool:
    pattern = ID_PATTERNS.get(field)
    if pattern is None:
        return nonempty_string(value, maximum=256)
    return isinstance(value, str) and pattern.fullmatch(value) is not None


def validate_event_ref(document: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(document, dict):
        return ["event reference must be an object"]

    keys = set(document)
    missing = EVENT_REQUIRED - keys
    extra = keys - EVENT_ALLOWED
    if missing:
        errors.append(f"missing event fields: {sorted(missing)}")
    if extra:
        errors.append(f"unexpected event fields: {sorted(extra)}")

    if document.get("schema") != "platform-event-ref/0.1":
        errors.append("wrong event schema")
    if not valid_id("event_id", document.get("event_id")):
        errors.append("invalid event_id")
    for field, maximum in (("source", 128), ("event_type", 160), ("subject_ref", 256)):
        if not nonempty_string(document.get(field), maximum=maximum):
            errors.append(f"invalid {field}")
    if not parse_rfc3339(document.get("occurred_at")):
        errors.append("invalid occurred_at")
    if not nonempty_string(document.get("payload_ref")):
        errors.append("invalid payload_ref")
    if not nonempty_string(document.get("integrity_ref")):
        errors.append("invalid integrity_ref")
    if document.get("classification") not in EVENT_CLASSES:
        errors.append("invalid classification")

    correlation = document.get("correlation")
    if not isinstance(correlation, dict):
        errors.append("correlation must be an object")
        return errors

    correlation_keys = set(correlation)
    missing_correlation = CORRELATION_REQUIRED - correlation_keys
    extra_correlation = correlation_keys - CORRELATION_ALLOWED
    if missing_correlation:
        errors.append(f"missing correlation fields: {sorted(missing_correlation)}")
    if extra_correlation:
        errors.append(f"unexpected correlation fields: {sorted(extra_correlation)}")

    for field, value in correlation.items():
        if field == "mission_id":
            if not nonempty_string(value, maximum=256):
                errors.append("invalid mission_id")
        elif not valid_id(field, value):
            errors.append(f"invalid {field}")

    return errors


def validate_capability_action(document: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(document, dict):
        return ["capability action must be an object"]

    keys = set(document)
    missing = CAP_REQUIRED - keys
    extra = keys - CAP_ALLOWED
    if missing:
        errors.append(f"missing capability fields: {sorted(missing)}")
    if extra:
        errors.append(f"unexpected capability fields: {sorted(extra)}")

    if document.get("schema") != "capability-action/0.1":
        errors.append("wrong capability-action schema")
    if not valid_id("action_id", document.get("action_id")):
        errors.append("invalid action_id")
    if not nonempty_string(document.get("mission_id"), maximum=256):
        errors.append("invalid mission_id")

    semantic_capability = document.get("semantic_capability")
    if not isinstance(semantic_capability, str) or CAPABILITY_RE.fullmatch(semantic_capability) is None:
        errors.append("invalid semantic_capability")
    if document.get("effect_class") not in EFFECT_CLASSES:
        errors.append("invalid effect_class")
    risk_class = document.get("risk_class")
    if not isinstance(risk_class, int) or isinstance(risk_class, bool) or not 0 <= risk_class <= 4:
        errors.append("invalid risk_class")

    parent_authority = document.get("required_authority")
    if not isinstance(parent_authority, list) or len(parent_authority) > 64:
        errors.append("required_authority must be a bounded array")
        parent_set: set[str] = set()
    elif any(not nonempty_string(item, maximum=160) for item in parent_authority):
        errors.append("required_authority contains invalid values")
        parent_set = set()
    elif len(parent_authority) != len(set(parent_authority)):
        errors.append("required_authority must be unique")
        parent_set = set(parent_authority)
    else:
        parent_set = set(parent_authority)

    for ref_name in ("input_ref", "expected_output_ref"):
        if not nonempty_string(document.get(ref_name)):
            errors.append(f"invalid {ref_name}")

    implementations = document.get("implementations")
    if not isinstance(implementations, list) or not 1 <= len(implementations) <= 32:
        errors.append("implementations must contain 1..32 entries")
    else:
        seen_ids: set[str] = set()
        for index, implementation in enumerate(implementations):
            prefix = f"implementations[{index}]"
            if not isinstance(implementation, dict):
                errors.append(f"{prefix} must be an object")
                continue
            required_keys = {"implementation_id", "kind", "binding_ref", "required_authority", "availability"}
            if set(implementation) != required_keys:
                errors.append(f"{prefix} fields are not exact")
                continue
            implementation_id = implementation["implementation_id"]
            if not isinstance(implementation_id, str) or re.fullmatch(r"^[a-z0-9][a-z0-9._:-]{0,159}$", implementation_id) is None:
                errors.append(f"{prefix}.implementation_id invalid")
            elif implementation_id in seen_ids:
                errors.append(f"{prefix}.implementation_id duplicate")
            else:
                seen_ids.add(implementation_id)
            if implementation["kind"] not in IMPLEMENTATION_KINDS:
                errors.append(f"{prefix}.kind invalid")
            if not nonempty_string(implementation["binding_ref"]):
                errors.append(f"{prefix}.binding_ref invalid")
            if implementation["availability"] not in IMPLEMENTATION_AVAILABILITY:
                errors.append(f"{prefix}.availability invalid")

            implementation_authority = implementation["required_authority"]
            if not isinstance(implementation_authority, list):
                errors.append(f"{prefix}.required_authority must be an array")
            elif any(not nonempty_string(item, maximum=160) for item in implementation_authority):
                errors.append(f"{prefix}.required_authority contains invalid values")
            elif not set(implementation_authority).issubset(parent_set):
                errors.append(f"{prefix} widens semantic authority")

    selection_policy = document.get("selection_policy")
    if not isinstance(selection_policy, dict) or set(selection_policy) != SELECTION_KEYS:
        errors.append("selection_policy fields are not exact")
    elif any(not isinstance(selection_policy[key], bool) for key in SELECTION_KEYS):
        errors.append("selection_policy values must be boolean")

    verification_required = document.get("verification_required")
    if not isinstance(verification_required, bool):
        errors.append("verification_required must be boolean")
    if document.get("effect_class") in {"consequential_write", "external_effect"} and verification_required is not True:
        errors.append("consequential/external effects require verification")

    return errors


def validate_causal_chain(document: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(document, dict):
        return ["causal chain must be an object"]
    canonical = document.get("canonical")
    stages = document.get("stages")
    if not isinstance(canonical, dict) or not canonical:
        return ["canonical causal identity must be a non-empty object"]
    if not isinstance(stages, list) or not stages:
        return ["causal chain must contain stages"]

    required_canonical = {"tenant_id", "principal_id", "mission_id", "trace_id", "action_id"}
    missing = required_canonical - set(canonical)
    if missing:
        errors.append(f"canonical chain missing: {sorted(missing)}")

    for field, value in canonical.items():
        if field == "mission_id":
            if not nonempty_string(value, maximum=256):
                errors.append("canonical mission_id invalid")
        elif field in ID_PATTERNS and not valid_id(field, value):
            errors.append(f"canonical {field} invalid")

    seen_stages: set[str] = set()
    for index, stage in enumerate(stages):
        if not isinstance(stage, dict):
            errors.append(f"stage[{index}] must be an object")
            continue
        stage_name = stage.get("stage")
        if not nonempty_string(stage_name, maximum=64):
            errors.append(f"stage[{index}] has invalid stage name")
            continue
        if stage_name in seen_stages:
            errors.append(f"duplicate stage {stage_name}")
        seen_stages.add(stage_name)

        for field, value in stage.items():
            if field == "stage" or field not in canonical:
                continue
            if canonical[field] != value:
                errors.append(f"{stage_name} drifted {field}")

        if stage_name in {"trust-gateway", "works"}:
            if stage.get("action_id") != canonical.get("action_id"):
                errors.append(f"{stage_name} missing canonical action_id")
            if stage.get("action_decision_id") != canonical.get("action_decision_id"):
                errors.append(f"{stage_name} missing action-time decision")
        if stage_name == "works":
            for field in ("execution_context_id", "work_id"):
                if stage.get(field) != canonical.get(field):
                    errors.append(f"works missing canonical {field}")
        if stage_name == "verification":
            for field in ("execution_context_id", "work_id", "action_id", "action_decision_id"):
                if stage.get(field) != canonical.get(field):
                    errors.append(f"verification missing canonical {field}")

    return errors


def validate_vector(vector: dict[str, Any]) -> list[str]:
    kind = vector.get("kind")
    document = vector.get("input")
    if kind == "event_ref":
        return validate_event_ref(document)
    if kind == "capability_action":
        return validate_capability_action(document)
    if kind == "causal_chain":
        return validate_causal_chain(document)
    return [f"unknown vector kind: {kind!r}"]


class PlatformFabricsV01Tests(unittest.TestCase):
    def test_contract_files_are_strict_and_experimental(self) -> None:
        event_schema = load_json(EVENT_SCHEMA)
        capability_schema = load_json(CAPABILITY_SCHEMA)
        for schema in (event_schema, capability_schema):
            self.assertFalse(schema.get("additionalProperties"), schema["title"])
            self.assertIn("EXPERIMENTAL", schema.get("description", ""))
            self.assertIn("authority", schema.get("description", "").lower())

        self.assertNotIn("authority_grant", event_schema["properties"])
        self.assertEqual(event_schema["properties"]["schema"]["const"], "platform-event-ref/0.1")
        self.assertEqual(capability_schema["properties"]["schema"]["const"], "capability-action/0.1")

    def test_vectors_have_unique_ids_and_expected_dispositions(self) -> None:
        fixture = load_json(VECTORS)
        self.assertEqual(fixture.get("schema_version"), "platform-conformance-v0.1")
        self.assertEqual(fixture.get("status"), "experimental")
        vectors = fixture.get("vectors")
        self.assertIsInstance(vectors, list)
        self.assertGreaterEqual(len(vectors), 8)
        ids = [vector.get("id") for vector in vectors]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertTrue(all(vector.get("expected") in {"accept", "reject"} for vector in vectors))

    def test_all_machine_vectors_match_expected_outcomes(self) -> None:
        fixture = load_json(VECTORS)
        failures: list[str] = []
        for vector in fixture["vectors"]:
            errors = validate_vector(vector)
            actual = "reject" if errors else "accept"
            if actual != vector["expected"]:
                failures.append(
                    f"{vector['id']}: expected {vector['expected']}, got {actual}; errors={errors}"
                )
        self.assertEqual(failures, [])

    def test_semantic_implementation_never_widens_authority(self) -> None:
        fixture = load_json(VECTORS)
        vector = next(item for item in fixture["vectors"] if item["id"] == "CAP-002")
        errors = validate_capability_action(vector["input"])
        self.assertTrue(any("widens semantic authority" in error for error in errors))

    def test_causal_identity_drift_fails_closed(self) -> None:
        fixture = load_json(VECTORS)
        vector = next(item for item in fixture["vectors"] if item["id"] == "GOLDEN-002")
        errors = validate_causal_chain(vector["input"])
        self.assertTrue(any("drifted principal_id" in error for error in errors))

    def test_wildcard_authority_can_narrow_without_false_widening(self) -> None:
        action = {
            "schema": "capability-action/0.1",
            "action_id": "act_aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
            "mission_id": "mis_aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
            "semantic_capability": "repository.patch",
            "effect_class": "consequential_write",
            "risk_class": 2,
            "required_authority": ["fs.write:*"],
            "input_ref": "git:sha:abc",
            "expected_output_ref": "git:patch:pending",
            "implementations": [
                {
                    "implementation_id": "native.patch.logs",
                    "kind": "native_tool",
                    "binding_ref": "runtime://patch/logs",
                    "required_authority": ["fs.write:logs"],
                    "availability": "available",
                }
            ],
            "selection_policy": {
                "prefer_verified_success": True,
                "minimize_cost": True,
                "minimize_latency": True,
                "minimize_context_pressure": True,
                "allow_fallback": True,
            },
            "verification_required": True,
        }
        self.assertEqual(validate_capability_action(action), [])

    def test_causal_stage_cannot_drop_canonical_principal(self) -> None:
        fixture = load_json(VECTORS)
        source = next(item for item in fixture["vectors"] if item["id"] == "GOLDEN-001")["input"]
        document = json.loads(json.dumps(source))
        works = next(stage for stage in document["stages"] if stage["stage"] == "works")
        del works["principal_id"]
        errors = validate_causal_chain(document)
        self.assertTrue(any("works missing canonical principal_id" in error for error in errors))

    def test_rfc3339_timestamp_requires_time_and_offset(self) -> None:
        self.assertFalse(parse_rfc3339("2026-09-08"))
        self.assertFalse(parse_rfc3339("2026-09-08T12:00:00"))
        self.assertTrue(parse_rfc3339("2026-09-08T12:00:00Z"))
        self.assertTrue(parse_rfc3339("2026-09-08T12:00:00+02:00"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
