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
ASSERTION_SCHEMA = ROOT / "docs/contracts/world-assertion/0.1.json"
SITUATION_SCHEMA = ROOT / "docs/contracts/situation/0.1.json"
CONSENT_SCHEMA = ROOT / "docs/contracts/consent-ledger/0.1.json"
LIFECYCLE_SCHEMA = ROOT / "docs/contracts/tenant-lifecycle/0.1.json"
PROACTIVITY_SCHEMA = ROOT / "docs/contracts/proactivity/0.1.json"
ORG_DELEGATION_SCHEMA = ROOT / "docs/contracts/org-delegation/0.1.json"
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
    "assertion_id": re.compile(rf"^ast_{HEX32}$"),
    "situation_id": re.compile(rf"^sit_{HEX32}$"),
    "ledger_id": re.compile(rf"^led_{HEX32}$"),
    "lifecycle_id": re.compile(rf"^lif_{HEX32}$"),
    "sensing_id": re.compile(rf"^sen_{HEX32}$"),
    "delegation_id": re.compile(rf"^del_{HEX32}$"),
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
WA_REQUIRED = {
    "schema",
    "assertion_id",
    "subject",
    "predicate",
    "value_or_ref",
    "epistemic",
    "currentness",
    "source_refs",
    "evidence_refs",
    "observed_at",
    "evidence_observed_at",
    "asserted_at",
    "valid_until",
    "tenant_id",
    "domain",
    "classification",
    "consent_record",
    "consent_version",
    "purpose",
    "evidence_requirement",
}
WA_ALLOWED = set(WA_REQUIRED) | {"confidence"}
SIT_REQUIRED = {
    "schema",
    "situation_id",
    "entities",
    "relationships",
    "assertion_refs",
    "source_refs",
    "asserted_at",
    "tenant_id",
    "source_tenant_id",
    "governed_transfer",
    "domain",
    "classification",
}
SIT_ALLOWED = set(SIT_REQUIRED)
SIT_ENTITY_KEYS = {"entity_id", "entity_type", "ref"}
SIT_REL_KEYS = {"relationship_id", "relation", "from_ref", "to_ref", "effect_claim"}
CON_REQUIRED = {
    "schema",
    "ledger_id",
    "event",
    "subject",
    "purpose",
    "narrowed_purpose",
    "scope_tenant",
    "scope_domain",
    "ledger_record",
    "ledger_version",
    "recorded_at",
    "valid_until",
    "revoked_at",
    "use_purpose",
    "use_at",
}
CON_ALLOWED = set(CON_REQUIRED)
CONSENT_EVENTS = {"granted", "restricted", "revoked", "expired"}
TEN_REQUIRED = {
    "schema",
    "lifecycle_id",
    "tenant_id",
    "state",
    "previous_state",
    "required_owners",
    "owner_acknowledgements",
    "attempted_action",
    "recorded_at",
}
TEN_ALLOWED = set(TEN_REQUIRED)
TENANT_STATES = {"active", "suspended", "exporting", "deleting", "deleted"}
TENANT_TRANSITIONS = {
    "active": {"active", "suspended", "exporting", "deleting"},
    "suspended": {"active", "deleting"},
    "exporting": {"active", "deleted"},
    "deleting": {"deleted"},
    "deleted": set(),
}
TENANT_ACKS = {"export", "deletion", "retention"}
TENANT_ACTIONS = {"none", "grant", "ingestion", "execution", "complete_export", "complete_deletion"}
PRO_REQUIRED = {
    "schema",
    "sensing_id",
    "path",
    "native_ref",
    "candidate_kind",
    "claims_execution",
    "claims_admission",
    "admitted_by_tg",
    "correlated_paths",
    "asserted_at",
    "tenant_id",
}
PRO_ALLOWED = set(PRO_REQUIRED)
SENSING_PATHS = {"wie", "runtime", "cron"}
CANDIDATE_KINDS = {"opportunity", "attention_candidate", "commitment_candidate", "observation_update", "finding"}
ORG_REQUIRED = {
    "schema",
    "delegation_id",
    "parent_ref",
    "child_ref",
    "parent_actions",
    "child_actions",
    "parent_budget",
    "child_budget",
    "sibling_budgets",
    "self_granted",
    "declares_completion",
    "verified_by_independent",
    "asserted_at",
    "tenant_id",
}
ORG_ALLOWED = set(ORG_REQUIRED)
EPISTEMIC_STATES = {"observed", "inferred", "predicted", "unknown"}
CURRENTNESS_STATES = {"current", "stale", "disputed", "superseded"}
EVIDENCE_REQUIREMENTS = {"none", "current_observed"}


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise AssertionError(f"{path} must contain a JSON object")
    return value


def parse_rfc3339(value: Any) -> bool:
    if not isinstance(value, str) or not value or "T" not in value:
        return False
    if re.search(r"(?:Z|[+-]\d{2}:\d{2})$", value) is None:
        return False
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return False
    return parsed.utcoffset() is not None


def nonempty_string(value: Any, *, maximum: int = 512) -> bool:
    return isinstance(value, str) and 0 < len(value) <= maximum


def parse_rfc3339_dt(value: Any) -> datetime | None:
    if not parse_rfc3339(value):
        return None
    assert isinstance(value, str)
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        return datetime.fromisoformat(normalized)
    except ValueError:
        return None


def valid_id(field: str, value: Any) -> bool:
    pattern = ID_PATTERNS.get(field)
    if pattern is None:
        return nonempty_string(value, maximum=256)
    return isinstance(value, str) and pattern.fullmatch(value) is not None


def authority_requirement_covered(grant: str, requirement: str) -> bool:
    if grant == "*" or grant == requirement:
        return True
    if not grant.endswith(":*"):
        return False
    prefix = grant[:-2]
    return requirement.startswith(f"{prefix}:")


def authority_envelope_covers(parent: set[str], required: list[str]) -> bool:
    return all(any(authority_requirement_covered(grant, item) for grant in parent) for item in required)


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
            elif not authority_envelope_covers(parent_set, implementation_authority):
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


def validate_world_assertion(document: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(document, dict):
        return ["world assertion must be an object"]

    keys = set(document)
    missing = WA_REQUIRED - keys
    extra = keys - WA_ALLOWED
    if missing:
        errors.append(f"missing assertion fields: {sorted(missing)}")
    if extra:
        errors.append(f"unexpected assertion fields: {sorted(extra)}")

    if document.get("schema") != "world-assertion/0.1":
        errors.append("wrong world-assertion schema")
    if not valid_id("assertion_id", document.get("assertion_id")):
        errors.append("invalid assertion_id")
    for field in ("subject", "predicate", "value_or_ref"):
        if not nonempty_string(document.get(field)):
            errors.append(f"invalid {field}")

    epistemic = document.get("epistemic")
    if epistemic not in EPISTEMIC_STATES:
        errors.append("invalid epistemic state")
    currentness = document.get("currentness")
    if currentness not in CURRENTNESS_STATES:
        errors.append("invalid currentness state")

    for field in ("source_refs", "evidence_refs"):
        refs = document.get(field)
        if (
            not isinstance(refs, list)
            or not 1 <= len(refs) <= 32
            or any(not nonempty_string(item) for item in refs)
        ):
            errors.append(f"{field} must contain 1..32 references")

    timing_ok = True
    for field in ("observed_at", "evidence_observed_at", "asserted_at", "valid_until"):
        if not parse_rfc3339(document.get(field)):
            errors.append(f"invalid {field}")
            timing_ok = False

    if not valid_id("tenant_id", document.get("tenant_id")):
        errors.append("invalid tenant_id")
    for field in ("domain", "classification", "consent_record", "purpose"):
        if not nonempty_string(document.get(field), maximum=256):
            errors.append(f"invalid {field}")
    if not nonempty_string(document.get("consent_version"), maximum=64):
        errors.append("invalid consent_version")

    confidence = document.get("confidence")
    if confidence is not None and (
        isinstance(confidence, bool)
        or not isinstance(confidence, (int, float))
        or not 0 <= confidence <= 1
    ):
        errors.append("confidence must be between 0 and 1")

    requirement = document.get("evidence_requirement")
    if requirement not in EVIDENCE_REQUIREMENTS:
        errors.append("invalid evidence_requirement")
    elif (
        requirement == "current_observed"
        and (epistemic != "observed" or currentness != "current")
    ):
        errors.append("only current observed state satisfies a current observed evidence requirement")

    if timing_ok:
        observed_at = document.get("observed_at")
        evidence_observed_at = document.get("evidence_observed_at")
        asserted_at = document.get("asserted_at")
        valid_until = document.get("valid_until")
        if observed_at > evidence_observed_at:
            errors.append("assertion observation postdates its evidence without new observation")
        if valid_until < asserted_at and currentness == "current":
            errors.append("expired validity must be represented as stale or unknown, not current")

    return errors


def validate_situation(document: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(document, dict):
        return ["situation must be an object"]

    keys = set(document)
    missing = SIT_REQUIRED - keys
    extra = keys - SIT_ALLOWED
    if missing:
        errors.append(f"missing situation fields: {sorted(missing)}")
    if extra:
        errors.append(f"unexpected situation fields: {sorted(extra)}")

    if document.get("schema") != "situation/0.1":
        errors.append("wrong situation schema")
    if not valid_id("situation_id", document.get("situation_id")):
        errors.append("invalid situation_id")

    entities = document.get("entities")
    entity_ids: set[str] = set()
    if not isinstance(entities, list) or not 1 <= len(entities) <= 32:
        errors.append("entities must contain 1..32 entries")
    else:
        for index, entity in enumerate(entities):
            prefix = f"entities[{index}]"
            if not isinstance(entity, dict) or set(entity) != SIT_ENTITY_KEYS:
                errors.append(f"{prefix} fields are not exact")
                continue
            entity_id = entity["entity_id"]
            if not nonempty_string(entity_id, maximum=160):
                errors.append(f"{prefix}.entity_id invalid")
            elif entity_id in entity_ids:
                errors.append(f"{prefix}.entity_id duplicate")
            else:
                entity_ids.add(entity_id)
            for field in ("entity_type", "ref"):
                if not nonempty_string(entity[field], maximum=512):
                    errors.append(f"{prefix}.{field} invalid")

    relationships = document.get("relationships")
    if not isinstance(relationships, list) or len(relationships) > 64:
        errors.append("relationships must contain 0..64 entries")
    else:
        for index, relationship in enumerate(relationships):
            prefix = f"relationships[{index}]"
            if not isinstance(relationship, dict) or set(relationship) != SIT_REL_KEYS:
                errors.append(f"{prefix} fields are not exact")
                continue
            if not nonempty_string(relationship["relationship_id"], maximum=160):
                errors.append(f"{prefix}.relationship_id invalid")
            if not nonempty_string(relationship["relation"], maximum=160):
                errors.append(f"{prefix}.relation invalid")
            if relationship.get("effect_claim") != "descriptive":
                errors.append(
                    f"{prefix} claims a non-descriptive effect; descriptive relations never become grants"
                )
            for field in ("from_ref", "to_ref"):
                endpoint = relationship.get(field)
                if not nonempty_string(endpoint, maximum=160):
                    errors.append(f"{prefix}.{field} invalid")
                elif endpoint not in entity_ids:
                    errors.append(f"{prefix} references unknown relationship endpoint")

    assertion_refs = document.get("assertion_refs")
    assertion_pattern = ID_PATTERNS["assertion_id"]
    if (
        not isinstance(assertion_refs, list)
        or not 1 <= len(assertion_refs) <= 32
        or any(
            not isinstance(item, str) or assertion_pattern.fullmatch(item) is None
            for item in assertion_refs
        )
    ):
        errors.append("assertion_refs must contain 1..32 world-assertion references")

    source_refs = document.get("source_refs")
    if (
        not isinstance(source_refs, list)
        or not 1 <= len(source_refs) <= 32
        or any(not nonempty_string(item) for item in source_refs)
    ):
        errors.append("source_refs must contain 1..32 references")

    if not parse_rfc3339(document.get("asserted_at")):
        errors.append("invalid asserted_at")

    tenant_id = document.get("tenant_id")
    source_tenant_id = document.get("source_tenant_id")
    if not valid_id("tenant_id", tenant_id):
        errors.append("invalid tenant_id")
    if not valid_id("tenant_id", source_tenant_id):
        errors.append("invalid source_tenant_id")
    transfer = document.get("governed_transfer")
    if tenant_id != source_tenant_id and transfer is None:
        errors.append("cross-tenant movement requires explicit governed export/import")
    elif transfer is not None:
        if not isinstance(transfer, dict) or set(transfer) != {
            "export_ref",
            "import_ref",
            "new_scope_identity",
        }:
            errors.append("governed_transfer fields are not exact")
        elif any(
            not nonempty_string(transfer[field], maximum=512)
            for field in ("export_ref", "import_ref", "new_scope_identity")
        ):
            errors.append("governed_transfer contains invalid values")

    for field in ("domain", "classification"):
        if not nonempty_string(document.get(field), maximum=256):
            errors.append(f"invalid {field}")

    return errors


def validate_consent_ledger(document: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(document, dict):
        return ["consent ledger use must be an object"]

    keys = set(document)
    missing = CON_REQUIRED - keys
    extra = keys - CON_ALLOWED
    if missing:
        errors.append(f"missing consent fields: {sorted(missing)}")
    if extra:
        errors.append(f"unexpected consent fields: {sorted(extra)}")

    if document.get("schema") != "consent-ledger/0.1":
        errors.append("wrong consent-ledger schema")
    if not valid_id("ledger_id", document.get("ledger_id")):
        errors.append("invalid ledger_id")

    event = document.get("event")
    if event not in CONSENT_EVENTS:
        errors.append("invalid consent event")

    if not nonempty_string(document.get("subject")):
        errors.append("invalid subject")
    purpose = document.get("purpose")
    if not nonempty_string(purpose, maximum=256):
        errors.append("invalid purpose")
    use_purpose = document.get("use_purpose")
    if not nonempty_string(use_purpose, maximum=256):
        errors.append("invalid use_purpose")

    if not valid_id("tenant_id", document.get("scope_tenant")):
        errors.append("invalid scope_tenant")
    for field in ("scope_domain", "ledger_record", "purpose"):
        if not nonempty_string(document.get(field), maximum=256):
            errors.append(f"invalid {field}")
    if not nonempty_string(document.get("ledger_version"), maximum=64):
        errors.append("invalid ledger_version")

    timing_ok = True
    for field in ("recorded_at", "valid_until", "use_at"):
        if not parse_rfc3339(document.get(field)):
            errors.append(f"invalid {field}")
            timing_ok = False

    revoked_at = document.get("revoked_at")
    if revoked_at is not None and not parse_rfc3339(revoked_at):
        errors.append("invalid revoked_at")
        timing_ok = False

    narrowed = document.get("narrowed_purpose")
    if event == "restricted" and not nonempty_string(narrowed, maximum=256):
        errors.append("restriction without a narrowed purpose")
    elif narrowed is not None and not isinstance(narrowed, str):
        errors.append("invalid narrowed_purpose")

    if event == "revoked" and revoked_at is None:
        errors.append("revocation without a revocation time")

    if timing_ok and event in CONSENT_EVENTS:
        use_dt = parse_rfc3339_dt(document.get("use_at"))
        recorded_dt = parse_rfc3339_dt(document.get("recorded_at"))
        valid_dt = parse_rfc3339_dt(document.get("valid_until"))
        revoked_dt = parse_rfc3339_dt(revoked_at)
        if use_dt is not None and recorded_dt is not None and use_dt < recorded_dt:
            errors.append("use predates the ledger record")
        if event == "granted":
            if use_purpose != purpose or (use_dt is not None and valid_dt is not None and use_dt > valid_dt):
                errors.append("use outside the granted purpose or validity")
        elif event == "restricted":
            if use_purpose != narrowed:
                errors.append("use outside the narrowed purpose is not permitted")
        elif event == "revoked":
            if (
                use_purpose == purpose
                and use_dt is not None
                and revoked_dt is not None
                and use_dt >= revoked_dt
            ):
                errors.append("revoked purpose no longer permits use")
        elif event == "expired":
            if use_dt is not None and valid_dt is not None and use_dt > valid_dt:
                errors.append("expired consent permits no further use")

    return errors


def validate_tenant_lifecycle(document: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(document, dict):
        return ["tenant lifecycle record must be an object"]

    keys = set(document)
    missing = TEN_REQUIRED - keys
    extra = keys - TEN_ALLOWED
    if missing:
        errors.append(f"missing lifecycle fields: {sorted(missing)}")
    if extra:
        errors.append(f"unexpected lifecycle fields: {sorted(extra)}")

    if document.get("schema") != "tenant-lifecycle/0.1":
        errors.append("wrong tenant-lifecycle schema")
    if not valid_id("lifecycle_id", document.get("lifecycle_id")):
        errors.append("invalid lifecycle_id")
    if not valid_id("tenant_id", document.get("tenant_id")):
        errors.append("invalid tenant_id")

    state = document.get("state")
    if state not in TENANT_STATES:
        errors.append("invalid lifecycle state")
    previous_state = document.get("previous_state")
    if previous_state is not None and previous_state not in TENANT_STATES:
        errors.append("invalid previous lifecycle state")
    elif (
        previous_state is not None
        and state in TENANT_STATES
        and state not in TENANT_TRANSITIONS[previous_state]
    ):
        errors.append("illegitimate lifecycle transition")

    required_owners = document.get("required_owners")
    if (
        not isinstance(required_owners, list)
        or not 1 <= len(required_owners) <= 32
        or any(not nonempty_string(item, maximum=160) for item in required_owners)
    ):
        errors.append("required_owners must contain 1..32 owners")

    acknowledgements = document.get("owner_acknowledgements")
    acked: dict[str, str] = {}
    if not isinstance(acknowledgements, list) or len(acknowledgements) > 32:
        errors.append("owner_acknowledgements must contain 0..32 entries")
    else:
        for index, entry in enumerate(acknowledgements):
            prefix = f"owner_acknowledgements[{index}]"
            if (
                not isinstance(entry, dict)
                or set(entry) != {"owner", "ack"}
                or not nonempty_string(entry.get("owner"), maximum=160)
                or entry.get("ack") not in TENANT_ACKS
            ):
                errors.append(f"{prefix} is not a valid acknowledgement")
                continue
            acked[entry["owner"]] = entry["ack"]

    action = document.get("attempted_action")
    if (
        not isinstance(action, dict)
        or set(action) != {"kind", "at"}
        or action.get("kind") not in TENANT_ACTIONS
        or not parse_rfc3339(action.get("at"))
    ):
        errors.append("invalid attempted_action")
        action_kind = None
    else:
        action_kind = action["kind"]

    if not parse_rfc3339(document.get("recorded_at")):
        errors.append("invalid recorded_at")

    if state in TENANT_STATES and action_kind is not None:
        if state == "deleting" and action_kind in {"grant", "ingestion", "execution"}:
            errors.append("deleting tenants admit no new grants, ingestion, or execution")
        elif state == "suspended" and action_kind == "execution":
            errors.append("suspended tenants admit no new execution")
        elif state == "exporting" and action_kind == "ingestion":
            errors.append("exporting tenants admit no new ingestion")
        elif state == "deleted" and action_kind != "none":
            errors.append("deleted tenants admit no further action")
        elif action_kind == "complete_deletion":
            if state != "deleting":
                errors.append("deletion completes only from deleting")
            else:
                unacked = [
                    owner
                    for owner in required_owners
                    if isinstance(required_owners, list) and owner not in acked
                ]
                if unacked:
                    errors.append(
                        f"deletion awaits owner acknowledgement: {sorted(unacked)}"
                    )
        elif action_kind == "complete_export":
            if state != "exporting":
                errors.append("export completes only from exporting")
            else:
                unacked = [
                    owner
                    for owner in required_owners
                    if isinstance(required_owners, list)
                    and acked.get(owner) != "export"
                ]
                if unacked:
                    errors.append(
                        f"export awaits export acknowledgement: {sorted(unacked)}"
                    )

    return errors


def validate_proactivity(document: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(document, dict):
        return ["proactivity sensing must be an object"]

    keys = set(document)
    missing = PRO_REQUIRED - keys
    extra = keys - PRO_ALLOWED
    if missing:
        errors.append(f"missing proactivity fields: {sorted(missing)}")
    if extra:
        errors.append(f"unexpected proactivity fields: {sorted(extra)}")

    if document.get("schema") != "proactivity/0.1":
        errors.append("wrong proactivity schema")
    if not valid_id("sensing_id", document.get("sensing_id")):
        errors.append("invalid sensing_id")

    path = document.get("path")
    if path not in SENSING_PATHS:
        errors.append("invalid sensing path")
    if not nonempty_string(document.get("native_ref")):
        errors.append("invalid native_ref")

    candidate_kind = document.get("candidate_kind")
    if candidate_kind not in CANDIDATE_KINDS:
        errors.append("invalid candidate kind")

    for field in ("claims_execution", "claims_admission", "admitted_by_tg"):
        if not isinstance(document.get(field), bool):
            errors.append(f"{field} must be a boolean")

    correlated = document.get("correlated_paths")
    if (
        not isinstance(correlated, list)
        or not 1 <= len(correlated) <= 3
        or any(item not in SENSING_PATHS for item in correlated)
    ):
        errors.append("correlated_paths must contain 1..3 sensing paths")
    elif path in SENSING_PATHS and path not in correlated:
        errors.append("sensing path must be among its correlated paths")

    if not parse_rfc3339(document.get("asserted_at")):
        errors.append("invalid asserted_at")
    if not valid_id("tenant_id", document.get("tenant_id")):
        errors.append("invalid tenant_id")

    if path == "cron" and document.get("claims_execution") is True:
        errors.append("cron fabric retains zero execution authority")
    if candidate_kind == "commitment_candidate" and document.get("admitted_by_tg") is not True:
        errors.append("candidates never self-admit to commitments")

    return errors


def _is_budget(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def _is_action_list(value: Any) -> bool:
    return (
        isinstance(value, list)
        and 1 <= len(value) <= 64
        and all(isinstance(item, str) and 0 < len(item) <= 128 for item in value)
    )


def validate_org_delegation(document: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(document, dict):
        return ["org delegation must be an object"]

    keys = set(document)
    missing = ORG_REQUIRED - keys
    extra = keys - ORG_ALLOWED
    if missing:
        errors.append(f"missing org-delegation fields: {sorted(missing)}")
    if extra:
        errors.append(f"unexpected org-delegation fields: {sorted(extra)}")

    if document.get("schema") != "org-delegation/0.1":
        errors.append("wrong org-delegation schema")
    if not valid_id("delegation_id", document.get("delegation_id")):
        errors.append("invalid delegation_id")
    if not nonempty_string(document.get("parent_ref")):
        errors.append("invalid parent_ref")
    if not nonempty_string(document.get("child_ref")):
        errors.append("invalid child_ref")

    parent_actions = document.get("parent_actions")
    child_actions = document.get("child_actions")
    if not _is_action_list(parent_actions):
        errors.append("invalid parent_actions")
    if not _is_action_list(child_actions):
        errors.append("invalid child_actions")

    parent_budget = document.get("parent_budget")
    child_budget = document.get("child_budget")
    sibling_budgets = document.get("sibling_budgets")
    if not _is_budget(parent_budget):
        errors.append("invalid parent_budget")
    if not _is_budget(child_budget):
        errors.append("invalid child_budget")
    if not isinstance(sibling_budgets, list) or any(
        not _is_budget(item) for item in sibling_budgets
    ):
        errors.append("invalid sibling_budgets")

    for field in ("self_granted", "declares_completion", "verified_by_independent"):
        if not isinstance(document.get(field), bool):
            errors.append(f"{field} must be a boolean")

    if not parse_rfc3339(document.get("asserted_at")):
        errors.append("invalid asserted_at")
    if not valid_id("tenant_id", document.get("tenant_id")):
        errors.append("invalid tenant_id")

    if (
        _is_action_list(parent_actions)
        and _is_action_list(child_actions)
        and not set(child_actions) <= set(parent_actions)
    ):
        errors.append("child envelope must stay equal-or-narrower than the parent")
    if (
        _is_budget(parent_budget)
        and _is_budget(child_budget)
        and isinstance(sibling_budgets, list)
        and all(_is_budget(item) for item in sibling_budgets)
        and child_budget + sum(sibling_budgets) > parent_budget
    ):
        errors.append("sibling partitions exceed parent budget")
    if document.get("self_granted") is True:
        errors.append("no worker self-grants authority")
    if (
        document.get("declares_completion") is True
        and document.get("verified_by_independent") is not True
    ):
        errors.append("verification stays independent: no self-declared verified completion")

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

        for field in ("tenant_id", "principal_id", "mission_id", "trace_id"):
            if field in canonical and field not in stage:
                errors.append(f"{stage_name} missing canonical {field}")

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
    if kind == "world_assertion":
        return validate_world_assertion(document)
    if kind == "situation":
        return validate_situation(document)
    if kind == "consent_ledger":
        return validate_consent_ledger(document)
    if kind == "tenant_lifecycle":
        return validate_tenant_lifecycle(document)
    if kind == "proactivity":
        return validate_proactivity(document)
    if kind == "org_delegation":
        return validate_org_delegation(document)
    if kind == "causal_chain":
        return validate_causal_chain(document)
    return [f"unknown vector kind: {kind!r}"]


def valid_world_assertion() -> dict[str, Any]:
    return {
        "schema": "world-assertion/0.1",
        "assertion_id": "ast_11111111111111111111111111111111",
        "subject": "work:commit",
        "predicate": "completed_by",
        "value_or_ref": "works:event:000007",
        "epistemic": "observed",
        "currentness": "current",
        "source_refs": ["works-execution"],
        "evidence_refs": ["works:evidence:000007"],
        "observed_at": "2026-09-08T12:00:00Z",
        "evidence_observed_at": "2026-09-08T12:00:00Z",
        "asserted_at": "2026-09-08T12:00:00Z",
        "valid_until": "2026-09-09T12:00:00Z",
        "tenant_id": "ten_11111111111111111111111111111111",
        "domain": "execution",
        "classification": "operations",
        "consent_record": "consent:ledger:000001",
        "consent_version": "v3",
        "purpose": "mission-evidence",
        "confidence": 0.9,
        "evidence_requirement": "current_observed",
    }


def valid_situation() -> dict[str, Any]:
    return {
        "schema": "situation/0.1",
        "situation_id": "sit_11111111111111111111111111111111",
        "entities": [
            {"entity_id": "worker", "entity_type": "role", "ref": "works:role:worker"},
            {"entity_id": "commit", "entity_type": "artifact", "ref": "work:commit"},
        ],
        "relationships": [
            {
                "relationship_id": "rel-001",
                "relation": "member_of",
                "from_ref": "worker",
                "to_ref": "commit",
                "effect_claim": "descriptive",
            }
        ],
        "assertion_refs": ["ast_11111111111111111111111111111111"],
        "source_refs": ["works-execution"],
        "asserted_at": "2026-09-08T12:00:00Z",
        "tenant_id": "ten_11111111111111111111111111111111",
        "source_tenant_id": "ten_11111111111111111111111111111111",
        "governed_transfer": None,
        "domain": "execution",
        "classification": "operations",
    }


def valid_consent_use() -> dict[str, Any]:
    return {
        "schema": "consent-ledger/0.1",
        "ledger_id": "led_11111111111111111111111111111111",
        "event": "granted",
        "subject": "work:memory:derived",
        "purpose": "mission-evidence",
        "narrowed_purpose": None,
        "scope_tenant": "ten_11111111111111111111111111111111",
        "scope_domain": "execution",
        "ledger_record": "consent:ledger:000001",
        "ledger_version": "v3",
        "recorded_at": "2026-09-08T12:00:00Z",
        "valid_until": "2026-09-09T12:00:00Z",
        "revoked_at": None,
        "use_purpose": "mission-evidence",
        "use_at": "2026-09-08T12:00:00Z",
    }


def valid_tenant_lifecycle() -> dict[str, Any]:
    return {
        "schema": "tenant-lifecycle/0.1",
        "lifecycle_id": "lif_11111111111111111111111111111111",
        "tenant_id": "ten_11111111111111111111111111111111",
        "state": "active",
        "previous_state": None,
        "required_owners": ["works-execution", "runtime"],
        "owner_acknowledgements": [
            {"owner": "works-execution", "ack": "retention"},
            {"owner": "runtime", "ack": "retention"},
        ],
        "attempted_action": {"kind": "grant", "at": "2026-09-08T12:00:00Z"},
        "recorded_at": "2026-09-08T12:00:00Z",
    }


def valid_proactivity() -> dict[str, Any]:
    return {
        "schema": "proactivity/0.1",
        "sensing_id": "sen_11111111111111111111111111111111",
        "path": "wie",
        "native_ref": "wie:signal:000001",
        "candidate_kind": "opportunity",
        "claims_execution": False,
        "claims_admission": False,
        "admitted_by_tg": False,
        "correlated_paths": ["wie"],
        "asserted_at": "2026-09-08T12:00:00Z",
        "tenant_id": "ten_11111111111111111111111111111111",
    }


def valid_org_delegation() -> dict[str, Any]:
    return {
        "schema": "org-delegation/0.1",
        "delegation_id": "del_11111111111111111111111111111111",
        "parent_ref": "runtime:team:000001",
        "child_ref": "runtime:worker:000001",
        "parent_actions": ["tasks.read", "tasks.write", "logs.read"],
        "child_actions": ["tasks.read", "logs.read"],
        "parent_budget": 100,
        "child_budget": 40,
        "sibling_budgets": [35, 25],
        "self_granted": False,
        "declares_completion": False,
        "verified_by_independent": False,
        "asserted_at": "2026-09-08T12:00:00Z",
        "tenant_id": "ten_11111111111111111111111111111111",
    }


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

    def test_adapter_acceptance_vectors_are_registered(self) -> None:
        fixture = load_json(VECTORS)
        by_id = {vector.get("id"): vector for vector in fixture["vectors"]}
        for vector_id, expected in (
            ("ADP-TG-001", "accept"),
            ("ADP-TG-002", "reject"),
            ("ADP-WORKS-001", "accept"),
            ("ADP-WORKS-002", "reject"),
        ):
            self.assertIn(vector_id, by_id)
            self.assertEqual(by_id[vector_id]["expected"], expected)

    def test_situation_contract_is_strict_and_experimental(self) -> None:
        schema = load_json(SITUATION_SCHEMA)
        self.assertFalse(schema.get("additionalProperties"), schema["title"])
        self.assertIn("EXPERIMENTAL", schema.get("description", ""))
        self.assertIn("authority", schema.get("description", "").lower())
        self.assertEqual(schema["properties"]["schema"]["const"], "situation/0.1")

    def test_relation_effect_must_stay_descriptive(self) -> None:
        document = valid_situation()
        self.assertEqual(validate_situation(document), [])
        document["relationships"][0]["effect_claim"] = "authority_grant"
        errors = validate_situation(document)
        self.assertTrue(
            any("never become grants" in error for error in errors)
        )

    def test_cross_tenant_requires_governed_transfer(self) -> None:
        document = valid_situation()
        document["source_tenant_id"] = "ten_22222222222222222222222222222222"
        errors = validate_situation(document)
        self.assertTrue(
            any("explicit governed export/import" in error for error in errors)
        )

    def test_situation_vectors_are_registered(self) -> None:
        fixture = load_json(VECTORS)
        by_id = {vector.get("id"): vector for vector in fixture["vectors"]}
        for vector_id, expected in (
            ("SIT-001", "accept"),
            ("SIT-002", "reject"),
            ("SIT-003", "reject"),
        ):
            self.assertIn(vector_id, by_id)
            self.assertEqual(by_id[vector_id]["expected"], expected)

    def test_consent_ledger_contract_is_strict_and_experimental(self) -> None:
        schema = load_json(CONSENT_SCHEMA)
        self.assertFalse(schema.get("additionalProperties"), schema["title"])
        self.assertIn("EXPERIMENTAL", schema.get("description", ""))
        self.assertIn("authority", schema.get("description", "").lower())
        self.assertEqual(schema["properties"]["schema"]["const"], "consent-ledger/0.1")

    def test_revoked_purpose_permits_no_further_use(self) -> None:
        document = valid_consent_use()
        self.assertEqual(validate_consent_ledger(document), [])
        document["event"] = "revoked"
        document["revoked_at"] = "2026-09-08T13:00:00Z"
        document["use_at"] = "2026-09-08T14:00:00Z"
        errors = validate_consent_ledger(document)
        self.assertTrue(
            any("no longer permits use" in error for error in errors)
        )

    def test_restricted_purpose_blocks_outside_use(self) -> None:
        document = valid_consent_use()
        document["event"] = "restricted"
        document["narrowed_purpose"] = "summarization"
        document["use_purpose"] = "personalization"
        errors = validate_consent_ledger(document)
        self.assertTrue(
            any("outside the narrowed purpose" in error for error in errors)
        )

    def test_use_predating_ledger_record_fails_closed(self) -> None:
        document = valid_consent_use()
        document["use_at"] = "2026-09-08T11:00:00Z"
        errors = validate_consent_ledger(document)
        self.assertTrue(
            any("predates the ledger record" in error for error in errors)
        )

    def test_mixed_offset_validity_compares_by_instant(self) -> None:
        # 12:00-02:00 is 14:00Z, past the 13:00Z validity end; a lexicographic
        # string compare would wrongly accept it ("12" < "13").
        document = valid_consent_use()
        document["event"] = "expired"
        document["valid_until"] = "2026-09-08T13:00:00Z"
        document["use_at"] = "2026-09-08T12:00:00-02:00"
        errors = validate_consent_ledger(document)
        self.assertTrue(
            any("permits no further use" in error for error in errors)
        )

    def test_tenant_lifecycle_contract_is_strict_and_experimental(self) -> None:
        schema = load_json(LIFECYCLE_SCHEMA)
        self.assertFalse(schema.get("additionalProperties"), schema["title"])
        self.assertIn("EXPERIMENTAL", schema.get("description", ""))
        self.assertIn("authority", schema.get("description", "").lower())
        self.assertEqual(schema["properties"]["schema"]["const"], "tenant-lifecycle/0.1")

    def test_deleting_tenant_denies_new_execution(self) -> None:
        document = valid_tenant_lifecycle()
        self.assertEqual(validate_tenant_lifecycle(document), [])
        document["state"] = "deleting"
        document["previous_state"] = "active"
        document["attempted_action"] = {"kind": "execution", "at": "2026-09-08T12:00:00Z"}
        errors = validate_tenant_lifecycle(document)
        self.assertTrue(
            any("admit no new grants, ingestion, or execution" in error for error in errors)
        )

    def test_deletion_awaits_every_owner_acknowledgement(self) -> None:
        document = valid_tenant_lifecycle()
        document["state"] = "deleting"
        document["previous_state"] = "active"
        document["owner_acknowledgements"] = [
            {"owner": "works-execution", "ack": "deletion"}
        ]
        document["attempted_action"] = {"kind": "complete_deletion", "at": "2026-09-08T12:00:00Z"}
        errors = validate_tenant_lifecycle(document)
        self.assertTrue(
            any("awaits owner acknowledgement" in error for error in errors)
        )

    def test_export_completion_requires_export_acknowledgements(self) -> None:
        document = valid_tenant_lifecycle()
        document["state"] = "exporting"
        document["previous_state"] = "active"
        document["owner_acknowledgements"] = [
            {"owner": "works-execution", "ack": "export"},
            {"owner": "runtime", "ack": "retention"},
        ]
        document["attempted_action"] = {"kind": "complete_export", "at": "2026-09-08T12:00:00Z"}
        errors = validate_tenant_lifecycle(document)
        self.assertTrue(
            any("awaits export acknowledgement" in error for error in errors)
        )
        document["owner_acknowledgements"] = [
            {"owner": "works-execution", "ack": "export"},
            {"owner": "runtime", "ack": "export"},
        ]
        self.assertEqual(validate_tenant_lifecycle(document), [])

    def test_tenant_lifecycle_vectors_are_registered(self) -> None:
        fixture = load_json(VECTORS)
        by_id = {vector.get("id"): vector for vector in fixture["vectors"]}
        for vector_id, expected in (
            ("TEN-001", "accept"),
            ("TEN-002", "reject"),
            ("TEN-003", "reject"),
            ("TEN-004", "reject"),
            ("TEN-005", "reject"),
        ):
            self.assertIn(vector_id, by_id)
            self.assertEqual(by_id[vector_id]["expected"], expected)

    def test_proactivity_contract_is_strict_and_experimental(self) -> None:
        schema = load_json(PROACTIVITY_SCHEMA)
        self.assertFalse(schema.get("additionalProperties"), schema["title"])
        self.assertIn("EXPERIMENTAL", schema.get("description", ""))
        self.assertIn("authority", schema.get("description", "").lower())
        self.assertEqual(schema["properties"]["schema"]["const"], "proactivity/0.1")

    def test_cron_path_claims_no_execution_authority(self) -> None:
        document = valid_proactivity()
        self.assertEqual(validate_proactivity(document), [])
        document["path"] = "cron"
        document["correlated_paths"] = ["cron"]
        document["claims_execution"] = True
        errors = validate_proactivity(document)
        self.assertTrue(
            any("zero execution authority" in error for error in errors)
        )

    def test_commitment_candidate_requires_tg_admission(self) -> None:
        document = valid_proactivity()
        document["candidate_kind"] = "commitment_candidate"
        document["claims_admission"] = True
        document["admitted_by_tg"] = False
        errors = validate_proactivity(document)
        self.assertTrue(
            any("never self-admit" in error for error in errors)
        )

    def test_proactivity_vectors_are_registered(self) -> None:
        fixture = load_json(VECTORS)
        by_id = {vector.get("id"): vector for vector in fixture["vectors"]}
        for vector_id, expected in (
            ("PRO-001", "accept"),
            ("PRO-002", "reject"),
            ("PRO-003", "reject"),
            ("PRO-004", "accept"),
            ("PRO-005", "accept"),
            ("PRO-006", "accept"),
        ):
            self.assertIn(vector_id, by_id)
            self.assertEqual(by_id[vector_id]["expected"], expected)

    def test_org_delegation_contract_is_strict_and_experimental(self) -> None:
        schema = load_json(ORG_DELEGATION_SCHEMA)
        self.assertFalse(schema.get("additionalProperties"), schema["title"])
        self.assertIn("EXPERIMENTAL", schema.get("description", ""))
        self.assertIn("authority", schema.get("description", "").lower())
        self.assertEqual(schema["properties"]["schema"]["const"], "org-delegation/0.1")

    def test_child_envelope_must_be_equal_or_narrower(self) -> None:
        document = valid_org_delegation()
        self.assertEqual(validate_org_delegation(document), [])
        document["child_actions"] = ["tasks.read", "logs.read", "admin.grant"]
        errors = validate_org_delegation(document)
        self.assertTrue(
            any("equal-or-narrower" in error for error in errors)
        )

    def test_sibling_partitions_cannot_exceed_parent_budget(self) -> None:
        document = valid_org_delegation()
        self.assertEqual(validate_org_delegation(document), [])
        document["child_budget"] = 60
        document["sibling_budgets"] = [30, 30]
        errors = validate_org_delegation(document)
        self.assertTrue(
            any("exceed parent budget" in error for error in errors)
        )

    def test_worker_cannot_self_grant_authority(self) -> None:
        document = valid_org_delegation()
        document["self_granted"] = True
        errors = validate_org_delegation(document)
        self.assertTrue(
            any("self-grant" in error for error in errors)
        )

    def test_worker_cannot_self_declare_verified_completion(self) -> None:
        document = valid_org_delegation()
        document["declares_completion"] = True
        document["verified_by_independent"] = False
        errors = validate_org_delegation(document)
        self.assertTrue(
            any("independent" in error for error in errors)
        )

    def test_org_delegation_vectors_are_registered(self) -> None:
        fixture = load_json(VECTORS)
        by_id = {vector.get("id"): vector for vector in fixture["vectors"]}
        for vector_id, expected in (
            ("ORG-001", "accept"),
            ("ORG-002", "reject"),
            ("ORG-003", "reject"),
            ("ORG-004", "reject"),
        ):
            self.assertIn(vector_id, by_id)
            self.assertEqual(by_id[vector_id]["expected"], expected)

    def test_consent_ledger_vectors_are_registered(self) -> None:
        fixture = load_json(VECTORS)
        by_id = {vector.get("id"): vector for vector in fixture["vectors"]}
        for vector_id, expected in (
            ("CON-001", "accept"),
            ("CON-002", "reject"),
            ("CON-003", "reject"),
            ("CON-004", "reject"),
        ):
            self.assertIn(vector_id, by_id)
            self.assertEqual(by_id[vector_id]["expected"], expected)

    def test_world_assertion_vectors_are_registered(self) -> None:
        fixture = load_json(VECTORS)
        by_id = {vector.get("id"): vector for vector in fixture["vectors"]}
        for vector_id, expected in (
            ("WA-001", "accept"),
            ("WA-002", "reject"),
            ("WA-003", "reject"),
        ):
            self.assertIn(vector_id, by_id)
            self.assertEqual(by_id[vector_id]["expected"], expected)

    def test_world_assertion_contract_is_strict_and_experimental(self) -> None:
        schema = load_json(ASSERTION_SCHEMA)
        self.assertFalse(schema.get("additionalProperties"), schema["title"])
        self.assertIn("EXPERIMENTAL", schema.get("description", ""))
        self.assertIn("authority", schema.get("description", "").lower())
        self.assertEqual(schema["properties"]["schema"]["const"], "world-assertion/0.1")

    def test_prediction_cannot_satisfy_observed_requirement(self) -> None:
        document = valid_world_assertion()
        self.assertEqual(validate_world_assertion(document), [])
        document["epistemic"] = "predicted"
        errors = validate_world_assertion(document)
        self.assertTrue(
            any("only current observed state satisfies" in error for error in errors)
        )

    def test_observation_cannot_postdate_evidence(self) -> None:
        document = valid_world_assertion()
        document["observed_at"] = "2026-09-08T14:00:00Z"
        document["asserted_at"] = "2026-09-08T14:00:01Z"
        errors = validate_world_assertion(document)
        self.assertTrue(any("postdates its evidence" in error for error in errors))

    def test_expired_validity_must_not_claim_current(self) -> None:
        document = valid_world_assertion()
        document["valid_until"] = "2026-09-08T11:00:00Z"
        errors = validate_world_assertion(document)
        self.assertTrue(any("stale or unknown, not current" in error for error in errors))

    def test_fallback_acceptance_vectors_are_registered(self) -> None:
        fixture = load_json(VECTORS)
        by_id = {vector.get("id"): vector for vector in fixture["vectors"]}
        for vector_id, expected in (
            ("CAP-004", "accept"),
            ("CAP-005", "reject"),
        ):
            self.assertIn(vector_id, by_id)
            self.assertEqual(by_id[vector_id]["expected"], expected)

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
