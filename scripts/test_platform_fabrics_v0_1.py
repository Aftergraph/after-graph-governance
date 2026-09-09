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
EVAL_SCHEMA = ROOT / "docs/contracts/agent-eval/0.1.json"
POCKET_SCHEMA = ROOT / "docs/contracts/pocket-source/0.1.json"
VOICE_SCHEMA = ROOT / "docs/contracts/voice-interaction/0.1.json"
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
    "eval_id": re.compile(rf"^evl_{HEX32}$"),
    "pocket_id": re.compile(rf"^pck_{HEX32}$"),
    "session_id": re.compile(rf"^ses_{HEX32}$"),
    "delivery_id": re.compile(rf"^dlv_{HEX32}$"),
    "idempotency_key": re.compile(rf"^idem_{HEX32}$"),
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
EVAL_REQUIRED = {
    "schema",
    "eval_id",
    "delegation_ref",
    "executor_ref",
    "evaluator_ref",
    "criteria_refs",
    "evidence_refs",
    "verdict",
    "self_promoting",
    "mutates_governance",
    "waives_verification",
    "asserted_at",
    "tenant_id",
}
EVAL_ALLOWED = set(EVAL_REQUIRED)
EVAL_VERDICTS = {"pass", "fail", "needs_review"}
POCKET_REQUIRED = {
    "schema",
    "pocket_id",
    "tenant_id",
    "credential_scope",
    "source_ref",
    "observation_ref",
    "classification",
    "claims_principal_identity",
    "claims_principal_authentication",
    "contains_instruction",
    "self_executes",
    "claims_execution",
    "candidate_kind",
    "admitted_by_tg",
    "governed_path_complete",
    "derivations",
    "asserted_at",
}
POCKET_WEBHOOK_OPTIONAL = {
    "delivery_channel",
    "signature",
    "signature_scheme",
    "delivery_id",
    "idempotency_key",
    "sequence_number",
    "applied_sequence",
    "resurrects_superseded_content",
    "seen_delivery_ids",
    "known_idempotency_keys",
    "materialized_observations",
    "supersedes",
    "lineage_preserved",
    "tombstone",
    "withdrawn_from_reads",
    "audit_retained",
    "reconciles_to_canonical",
    "webhook_claimed_as_truth",
}
POCKET_TASK3_OPTIONAL = {
    "consent_ref",
    "purpose",
    "consent_revoked",
    "downstream_invalidated",
    "audit_rewritten",
    "source_deleted",
    "deletion_propagated",
    "projection_recomputed",
    "stale_served_as_current",
    "injection_contained",
    "conversation_scope",
    "attributed_conversation",
    "cross_conversation_lineage",
    "access_mode",
}
POCKET_ALLOWED = set(POCKET_REQUIRED) | set(POCKET_WEBHOOK_OPTIONAL) | set(POCKET_TASK3_OPTIONAL)
POCKET_CHANNELS = {"rest", "webhook"}
POCKET_ACCESS_MODES = {"interactive", "canonical"}
VOICE_REQUIRED = {
    "schema",
    "session_id",
    "tenant_id",
    "surface_ref",
    "thread_ref",
    "turn_ref",
    "observation_ref",
    "model_identity_ref",
    "session_identity_disposable",
    "classification",
    "embeds_durable_principal_identity",
    "embeds_durable_state",
    "admitted_by_tg",
    "tg_admission_ref",
    "egress_effect",
    "egress_grant_enforced",
    "claims_principal_identity",
    "claims_principal_authentication",
    "claims_authority",
    "asserted_at",
}
VOICE_OPTIONAL = {
    "principal_ref",
    "interaction_state_ref",
    "memory_ref",
    "mission_ref",
    "consent_ref",
    "turn_binding",
    "stop_verb",
    "governed_path_complete",
    "barge_in_terminates_execution",
    "contains_instruction",
    "self_executes",
    "candidate_kind",
    "session_identity_reused_as_durable_principal",
    "claims_realtime_raw_audio",
    "device_api_evidence_ref",
    "handoff_checkpoint",
    "correlation_refs",
    "destination_readmission_ref",
    "authority_transport",
    "continuity_basis",
    "purpose",
    "lineage_refs",
    "revocation_ref",
    "downstream_invalidated",
    "audit_rewritten",
    "deletion_ref",
    "withdrawn",
    "tombstone_ref",
    "source_surface_ref",
    "attributed_surface_ref",
    "injection_contained",
}
VOICE_ALLOWED = set(VOICE_REQUIRED) | set(VOICE_OPTIONAL)
VOICE_CONTINUITY_BASES = {"correlation_provenance", "conversation", "memory", "session_authority"}
VOICE_CLASSES = {"authority", "enforcement", "runtime", "execution", "verification", "research"}
VOICE_STOP_VERBS_SPEECH_ONLY = {"STOP_SPEAKING", "CANCEL_TURN"}
VOICE_STOP_VERBS_CONSEQUENTIAL = {"PAUSE_MISSION", "CANCEL_MISSION", "FREEZE_AUTONOMY"}
VOICE_STOP_VERBS = set(VOICE_STOP_VERBS_SPEECH_ONLY) | set(VOICE_STOP_VERBS_CONSEQUENTIAL)
VOICE_TURN_BINDINGS = {"disposable_session", "durable_principal"}
VOICE_CANDIDATE_KINDS = {"observation_update", "commitment_candidate"}
POCKET_SIGNATURE_SCHEMES = {"hmac-sha256"}
POCKET_CLASSES = {"authority", "enforcement", "runtime", "execution", "verification", "research"}
POCKET_CANDIDATE_KINDS = {"observation_update", "attention_candidate", "commitment_candidate", "finding"}
POCKET_DERIVATIONS = {"transcript", "speaker_attribution", "summary", "action_extraction"}
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


def _is_ref_list(value: Any) -> bool:
    return (
        isinstance(value, list)
        and 1 <= len(value) <= 32
        and all(isinstance(item, str) and 0 < len(item) <= 512 for item in value)
    )


def validate_agent_eval(document: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(document, dict):
        return ["agent eval must be an object"]

    keys = set(document)
    missing = EVAL_REQUIRED - keys
    extra = keys - EVAL_ALLOWED
    if missing:
        errors.append(f"missing agent-eval fields: {sorted(missing)}")
    if extra:
        errors.append(f"unexpected agent-eval fields: {sorted(extra)}")

    if document.get("schema") != "agent-eval/0.1":
        errors.append("wrong agent-eval schema")
    if not valid_id("eval_id", document.get("eval_id")):
        errors.append("invalid eval_id")
    if not valid_id("delegation_id", document.get("delegation_ref")):
        errors.append("invalid delegation_ref")
    if not nonempty_string(document.get("executor_ref")):
        errors.append("invalid executor_ref")
    if not nonempty_string(document.get("evaluator_ref")):
        errors.append("invalid evaluator_ref")

    if not _is_ref_list(document.get("criteria_refs")):
        errors.append("scoring requires explicit criteria: criteria_refs must contain 1..32 references")
    if not _is_ref_list(document.get("evidence_refs")):
        errors.append("scoring requires evidence references: evidence_refs must contain 1..32 references")

    if document.get("verdict") not in EVAL_VERDICTS:
        errors.append("invalid verdict")

    for field in ("self_promoting", "mutates_governance", "waives_verification"):
        if not isinstance(document.get(field), bool):
            errors.append(f"{field} must be a boolean")

    if not parse_rfc3339(document.get("asserted_at")):
        errors.append("invalid asserted_at")
    if not valid_id("tenant_id", document.get("tenant_id")):
        errors.append("invalid tenant_id")

    executor_ref = document.get("executor_ref")
    evaluator_ref = document.get("evaluator_ref")
    if (
        isinstance(executor_ref, str)
        and executor_ref
        and evaluator_ref == executor_ref
    ):
        errors.append("evaluators never score their own execution")
    if document.get("self_promoting") is True:
        errors.append("eval verdict is advisory only: it never declares its own authority")
    if document.get("mutates_governance") is True:
        errors.append("eval verdict is advisory only: it mutates no governance state")
    if document.get("waives_verification") is True:
        errors.append("eval verdict is advisory only: it waives no verification requirement")

    return errors


def valid_unit_weight(value: object) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and 0 <= value <= 1


def validate_pocket_source(document: object) -> list[str]:
    errors: list[str] = []
    if not isinstance(document, dict):
        return ["pocket source must be an object"]

    keys = set(document)
    missing = POCKET_REQUIRED - keys
    extra = keys - POCKET_ALLOWED
    if missing:
        errors.append(f"missing pocket-source fields: {sorted(missing)}")
    if extra:
        errors.append(f"unexpected pocket-source fields: {sorted(extra)}")

    if document.get("schema") != "pocket-source/0.1":
        errors.append("wrong pocket-source schema")
    if not valid_id("pocket_id", document.get("pocket_id")):
        errors.append("invalid pocket_id")
    if not valid_id("tenant_id", document.get("tenant_id")):
        errors.append("invalid tenant_id")
    if not valid_id("tenant_id", document.get("credential_scope")):
        errors.append("invalid credential_scope")
    elif document.get("credential_scope") != document.get("tenant_id"):
        errors.append("cross-tenant credential reuse is forbidden")
    if not nonempty_string(document.get("source_ref")):
        errors.append("invalid source_ref")
    if not nonempty_string(document.get("observation_ref")):
        errors.append("invalid observation_ref")
    if document.get("classification") not in POCKET_CLASSES:
        errors.append("invalid classification")

    for field in (
        "claims_principal_identity",
        "claims_principal_authentication",
        "contains_instruction",
        "self_executes",
        "claims_execution",
        "admitted_by_tg",
        "governed_path_complete",
    ):
        if not isinstance(document.get(field), bool):
            errors.append(f"{field} must be a boolean")

    if document.get("claims_principal_identity") is True:
        errors.append("transcript is not principal identity")
    if document.get("claims_principal_authentication") is True:
        errors.append("speaker attribution is not principal authentication")
    if document.get("claims_execution") is True:
        errors.append("pocket source retains zero execution authority")
    if document.get("self_executes") is True:
        errors.append("spoken instruction never self-executes")

    candidate_kind = document.get("candidate_kind")
    if candidate_kind not in POCKET_CANDIDATE_KINDS:
        errors.append("invalid candidate kind")
    if candidate_kind == "commitment_candidate" and document.get("admitted_by_tg") is not True:
        errors.append("candidates never self-admit to commitments")
    if (
        document.get("contains_instruction") is True
        and candidate_kind == "commitment_candidate"
        and document.get("governed_path_complete") is not True
    ):
        errors.append("spoken instruction requires AIE -> Trust Gateway -> Runtime -> WORKS -> verification")

    derivations = document.get("derivations")
    if not isinstance(derivations, list) or not 1 <= len(derivations) <= 4:
        errors.append("derivations must contain 1..4 derivation entries")
    else:
        seen_kinds: set[str] = set()
        seen_lineage: set[str] = set()
        for entry in derivations:
            if not isinstance(entry, dict):
                errors.append("derivation entry must be an object")
                continue
            if set(entry) != {"derivation", "weight", "uncertainty", "lineage_ref"}:
                errors.append("unexpected derivation entry fields")
            derivation = entry.get("derivation")
            if derivation not in POCKET_DERIVATIONS:
                errors.append("invalid derivation kind")
            elif derivation in seen_kinds:
                errors.append("derivations must retain distinct derivation lineage")
            else:
                seen_kinds.add(derivation)
            if not valid_unit_weight(entry.get("weight")):
                errors.append("derivation weight must be a number in [0, 1]")
            if not valid_unit_weight(entry.get("uncertainty")):
                errors.append("derivation uncertainty must be a number in [0, 1]")
            lineage = entry.get("lineage_ref")
            if not nonempty_string(lineage):
                errors.append("invalid derivation lineage_ref")
            elif lineage in seen_lineage:
                errors.append("derivations must retain distinct derivation lineage")
            else:
                seen_lineage.add(lineage)

    if not parse_rfc3339(document.get("asserted_at")):
        errors.append("invalid asserted_at")

    channel = document.get("delivery_channel")
    if channel is not None and channel not in POCKET_CHANNELS:
        errors.append("invalid delivery_channel")
    if document.get("delivery_id") is not None and not valid_id(
        "delivery_id", document.get("delivery_id")
    ):
        errors.append("invalid delivery_id")
    if document.get("idempotency_key") is not None and not valid_id(
        "idempotency_key", document.get("idempotency_key")
    ):
        errors.append("invalid idempotency_key")
    scheme = document.get("signature_scheme")
    if scheme is not None and scheme not in POCKET_SIGNATURE_SCHEMES:
        errors.append("invalid signature_scheme")
    signature = document.get("signature")
    if signature is not None and not nonempty_string(signature):
        errors.append("invalid signature")
    if channel == "webhook":
        if (
            not nonempty_string(signature)
            or scheme not in POCKET_SIGNATURE_SCHEMES
            or not valid_id("delivery_id", document.get("delivery_id"))
        ):
            errors.append("webhook delivery requires a bound signature and delivery_id")
        elif document.get("delivery_id") not in signature:
            errors.append("webhook signature is not bound to delivery_id")
        seen = document.get("seen_delivery_ids")
        if seen is not None:
            if not isinstance(seen, list) or any(
                not valid_id("delivery_id", entry) for entry in seen
            ):
                errors.append("invalid seen_delivery_ids")
            elif document.get("delivery_id") in seen:
                errors.append("replayed webhook delivery rejected by replay protection")

    known = document.get("known_idempotency_keys")
    if known is not None:
        if not isinstance(known, list) or any(
            not valid_id("idempotency_key", entry) for entry in known
        ):
            errors.append("invalid known_idempotency_keys")
    materialized = document.get("materialized_observations")
    if materialized is not None and (
        isinstance(materialized, bool)
        or not isinstance(materialized, int)
        or materialized < 1
    ):
        errors.append("invalid materialized_observations")
    key = document.get("idempotency_key")
    if (
        key is not None
        and valid_id("idempotency_key", key)
        and isinstance(known, list)
        and key in known
        and materialized != 1
    ):
        errors.append("duplicate delivery must dedupe to a single Observation")
    sequence = document.get("sequence_number")
    if sequence is not None and (
        isinstance(sequence, bool) or not isinstance(sequence, int) or sequence < 0
    ):
        errors.append("invalid sequence_number")
    applied = document.get("applied_sequence")
    if applied is not None and (
        isinstance(applied, bool) or not isinstance(applied, int) or applied < 0
    ):
        errors.append("invalid applied_sequence")
    resurrects = document.get("resurrects_superseded_content")
    if resurrects is not None and not isinstance(resurrects, bool):
        errors.append("resurrects_superseded_content must be a boolean")
    if (
        isinstance(sequence, int)
        and not isinstance(sequence, bool)
        and isinstance(applied, int)
        and not isinstance(applied, bool)
        and sequence < applied
        and resurrects is True
    ):
        errors.append("superseded content must never be resurrected")
    supersedes = document.get("supersedes")
    if supersedes is not None and not valid_id("delivery_id", supersedes):
        errors.append("invalid supersedes")
    lineage = document.get("lineage_preserved")
    if lineage is not None and not isinstance(lineage, bool):
        errors.append("lineage_preserved must be a boolean")
    if (
        supersedes is not None
        and valid_id("delivery_id", supersedes)
        and lineage is not True
    ):
        errors.append("superseding edit must preserve lineage")
    for field in ("tombstone", "withdrawn_from_reads", "audit_retained"):
        if document.get(field) is not None and not isinstance(document.get(field), bool):
            errors.append(f"{field} must be a boolean")
    if document.get("tombstone") is True:
        if document.get("withdrawn_from_reads") is not True:
            errors.append("tombstone must withdraw content from reads")
        if document.get("audit_retained") is not True:
            errors.append("tombstone must retain audit")
    reconciles = document.get("reconciles_to_canonical")
    if reconciles is not None and not isinstance(reconciles, bool):
        errors.append("reconciles_to_canonical must be a boolean")
    claimed = document.get("webhook_claimed_as_truth")
    if claimed is not None and not isinstance(claimed, bool):
        errors.append("webhook_claimed_as_truth must be a boolean")
    if claimed is True:
        errors.append("webhooks are event-plane signals, never reconciliation truth")

    consent_ref = document.get("consent_ref")
    if consent_ref is not None and not nonempty_string(consent_ref, maximum=256):
        errors.append("invalid consent_ref")
    purpose = document.get("purpose")
    if purpose is not None and not nonempty_string(purpose, maximum=256):
        errors.append("invalid purpose")
    revoked = document.get("consent_revoked")
    if revoked is not None and not isinstance(revoked, bool):
        errors.append("consent_revoked must be a boolean")
    invalidated = document.get("downstream_invalidated")
    if invalidated is not None and not isinstance(invalidated, bool):
        errors.append("downstream_invalidated must be a boolean")
    if revoked is True and invalidated is not True:
        errors.append("consent revocation invalidates downstream use per provenance")
    rewritten = document.get("audit_rewritten")
    if rewritten is not None and not isinstance(rewritten, bool):
        errors.append("audit_rewritten must be a boolean")
    if rewritten is True:
        errors.append("historical audit/evidence is never rewritten")
    deleted = document.get("source_deleted")
    if deleted is not None and not isinstance(deleted, bool):
        errors.append("source_deleted must be a boolean")
    propagated = document.get("deletion_propagated")
    if propagated is not None and not isinstance(propagated, bool):
        errors.append("deletion_propagated must be a boolean")
    if deleted is True:
        if propagated is not True:
            errors.append("source deletion propagates withdrawal to reads and derivatives")
        if document.get("withdrawn_from_reads") is not True:
            errors.append("source deletion withdraws content from reads")
    recomputed = document.get("projection_recomputed")
    if recomputed is not None and not isinstance(recomputed, bool):
        errors.append("projection_recomputed must be a boolean")
    stale = document.get("stale_served_as_current")
    if stale is not None and not isinstance(stale, bool):
        errors.append("stale_served_as_current must be a boolean")
    if stale is True:
        errors.append("projections never stale-served as current")
    contained = document.get("injection_contained")
    if contained is not None and not isinstance(contained, bool):
        errors.append("injection_contained must be a boolean")
    scope = document.get("conversation_scope")
    if scope is not None and not nonempty_string(scope):
        errors.append("invalid conversation_scope")
    attributed = document.get("attributed_conversation")
    if attributed is not None and not nonempty_string(attributed):
        errors.append("invalid attributed_conversation")
    cross_lineage = document.get("cross_conversation_lineage")
    if cross_lineage is not None and not isinstance(cross_lineage, bool):
        errors.append("cross_conversation_lineage must be a boolean")
    if (
        scope is not None
        and attributed is not None
        and nonempty_string(scope)
        and nonempty_string(attributed)
        and attributed != scope
        and cross_lineage is not True
    ):
        errors.append("cross-conversation attribution without lineage rejected")
    access = document.get("access_mode")
    if access is not None and access not in POCKET_ACCESS_MODES:
        errors.append("invalid access_mode")
    if access == "canonical":
        errors.append("MCP is optional interactive access, never canonical ingestion")

    return errors


def validate_voice_interaction(document: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(document, dict):
        return ["voice interaction must be an object"]

    keys = set(document)
    missing = VOICE_REQUIRED - keys
    extra = keys - VOICE_ALLOWED
    if missing:
        errors.append(f"missing voice-interaction fields: {sorted(missing)}")
    if extra:
        errors.append(f"unexpected voice-interaction fields: {sorted(extra)}")

    if document.get("schema") != "voice-interaction/0.1":
        errors.append("wrong voice-interaction schema")
    if not valid_id("session_id", document.get("session_id")):
        errors.append("invalid session_id")
    if not valid_id("tenant_id", document.get("tenant_id")):
        errors.append("invalid tenant_id")
    for field in (
        "surface_ref",
        "thread_ref",
        "turn_ref",
        "observation_ref",
        "model_identity_ref",
        "tg_admission_ref",
    ):
        if not nonempty_string(document.get(field)):
            errors.append(f"invalid {field}")
    if document.get("classification") not in VOICE_CLASSES:
        errors.append("invalid classification")

    for field in (
        "session_identity_disposable",
        "embeds_durable_principal_identity",
        "embeds_durable_state",
        "admitted_by_tg",
        "egress_effect",
        "egress_grant_enforced",
        "claims_principal_identity",
        "claims_principal_authentication",
        "claims_authority",
    ):
        if not isinstance(document.get(field), bool):
            errors.append(f"{field} must be a boolean")

    if document.get("session_identity_disposable") is not True:
        errors.append("voice session/model identity is disposable")
    if document.get("embeds_durable_principal_identity") is True:
        errors.append("sessions carry no durable principal identity; durable identity lives outside sessions")
    if document.get("embeds_durable_state") is True:
        errors.append("sessions carry no durable interaction/memory/mission state; durable state lives outside sessions")
    if document.get("admitted_by_tg") is not True:
        errors.append("session admission passes Trust Gateway")
    if (
        document.get("egress_effect") is True
        and document.get("egress_grant_enforced") is not True
    ):
        errors.append("session egress/effects require Trust Gateway grant enforcement")
    if document.get("claims_principal_identity") is True:
        errors.append("transcript is not principal identity (inherited Wave F binding)")
    if document.get("claims_principal_authentication") is True:
        errors.append("speaker attribution is not principal authentication (inherited Wave F binding)")
    if document.get("claims_authority") is True:
        errors.append("voice sessions confer no authority")

    for field in (
        "governed_path_complete",
        "barge_in_terminates_execution",
        "contains_instruction",
        "self_executes",
        "claims_realtime_raw_audio",
        "session_identity_reused_as_durable_principal",
    ):
        if document.get(field) is not None and not isinstance(document.get(field), bool):
            errors.append(f"{field} must be a boolean")

    turn_binding = document.get("turn_binding")
    if turn_binding is not None:
        if turn_binding not in VOICE_TURN_BINDINGS:
            errors.append("invalid turn_binding")
        elif turn_binding != "disposable_session":
            errors.append("InteractionTurn binds to the disposable session/model identity, never a durable principal")

    stop_verb = document.get("stop_verb")
    if stop_verb is not None:
        if stop_verb not in VOICE_STOP_VERBS:
            errors.append("invalid stop_verb")
        elif stop_verb in VOICE_STOP_VERBS_CONSEQUENTIAL:
            if document.get("governed_path_complete") is not True:
                errors.append("consequential stop verbs require the governed consequential path; the voice edge never executes PAUSE_MISSION/CANCEL_MISSION/FREEZE_AUTONOMY alone")

    if document.get("barge_in_terminates_execution") is True:
        errors.append("barge-in interrupts speech/turn only; barge-in never terminates consequential execution")

    if (
        document.get("contains_instruction") is True
        and document.get("self_executes") is True
    ):
        errors.append("spoken instruction never self-executes; permission requires AIE -> Trust Gateway -> Runtime -> WORKS -> verification")

    candidate_kind = document.get("candidate_kind")
    if candidate_kind is not None:
        if candidate_kind not in VOICE_CANDIDATE_KINDS:
            errors.append("invalid candidate kind")
        elif candidate_kind == "commitment_candidate" and (
            document.get("admitted_by_tg") is not True
            or document.get("governed_path_complete") is not True
        ):
            errors.append("voice-derived CommitmentCandidate requires the governed consequential path; candidates never self-admit to commitments")

    if document.get("session_identity_reused_as_durable_principal") is True:
        errors.append("disposable session identity is never reused as a durable principal across sessions")

    if document.get("claims_realtime_raw_audio") is True:
        if not nonempty_string(document.get("device_api_evidence_ref")):
            errors.append("realtime raw-audio streaming claims require device/API evidence (evidence-gated)")
    elif document.get("device_api_evidence_ref") is not None and not nonempty_string(
        document.get("device_api_evidence_ref")
    ):
        errors.append("invalid device_api_evidence_ref")

    for field in (
        "principal_ref",
        "interaction_state_ref",
        "memory_ref",
        "mission_ref",
    ):
        if document.get(field) is not None and not nonempty_string(document.get(field)):
            errors.append(f"invalid {field}")
    consent_ref = document.get("consent_ref")
    if consent_ref is not None and not nonempty_string(consent_ref, maximum=256):
        errors.append("invalid consent_ref")

    if not parse_rfc3339(document.get("asserted_at")):
        errors.append("invalid asserted_at")

    for field in (
        "handoff_checkpoint",
        "destination_readmission_ref",
        "revocation_ref",
        "deletion_ref",
        "tombstone_ref",
        "source_surface_ref",
        "attributed_surface_ref",
    ):
        if document.get(field) is not None and not nonempty_string(document.get(field)):
            errors.append(f"invalid {field}")
    purpose = document.get("purpose")
    if purpose is not None and not nonempty_string(purpose, maximum=256):
        errors.append("invalid purpose")
    for field in ("correlation_refs", "lineage_refs"):
        refs = document.get(field)
        if refs is not None and (
            not isinstance(refs, list)
            or not 1 <= len(refs) <= 32
            or any(not nonempty_string(item) for item in refs)
        ):
            errors.append(f"{field} must contain 1..32 refs")
    for field in (
        "authority_transport",
        "downstream_invalidated",
        "audit_rewritten",
        "withdrawn",
        "injection_contained",
    ):
        if document.get(field) is not None and not isinstance(document.get(field), bool):
            errors.append(f"{field} must be a boolean")

    continuity_basis = document.get("continuity_basis")
    if continuity_basis is not None:
        if continuity_basis not in VOICE_CONTINUITY_BASES:
            errors.append("invalid continuity_basis")
        elif continuity_basis != "correlation_provenance":
            errors.append("Conversation != Memory != Continuity != Authority; session conversation/memory is never continuity or authority")

    if document.get("handoff_checkpoint") is not None:
        if not document.get("correlation_refs"):
            errors.append("cross-surface handoff carries platform-event-ref/0.1 correlation/provenance refs; correlation is never authority")
        if not nonempty_string(document.get("destination_readmission_ref")):
            errors.append("handoff authority is re-admitted at the destination; handoffs transport correlation/provenance only")

    if document.get("authority_transport") is True:
        errors.append("continuity never moves authority into the session/handoff; handoff transports correlation/provenance only")

    lineage_refs = document.get("lineage_refs")
    if lineage_refs is not None and not nonempty_string(purpose, maximum=256):
        errors.append("consent/purpose lineage requires a purpose; derivatives inherit purpose lineage")

    if document.get("revocation_ref") is not None and document.get("downstream_invalidated") is not True:
        errors.append("consent revocation invalidates downstream voice-derived use per provenance")
    if document.get("downstream_invalidated") is True and document.get("revocation_ref") is None:
        errors.append("downstream invalidation cites its revocation per provenance")
    if document.get("audit_rewritten") is True:
        errors.append("revocation and deletion never rewrite historical audit/evidence")

    if document.get("withdrawn") is True:
        if not nonempty_string(document.get("deletion_ref")):
            errors.append("turn deletion withdrawal cites its deletion")
        if not nonempty_string(document.get("tombstone_ref")):
            errors.append("turn deletion propagates withdrawal with tombstone semantics")

    source_surface = document.get("source_surface_ref")
    attributed_surface = document.get("attributed_surface_ref")
    if (
        source_surface is not None
        and attributed_surface is not None
        and source_surface != attributed_surface
        and not lineage_refs
    ):
        errors.append("cross-surface attribution without explicit lineage leaks surface content")

    if document.get("contains_instruction") is True:
        if document.get("injection_contained") is not True:
            errors.append("voice transcript content is untrusted observation; prompt-injection is contained, never instruction or authority")

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
    if kind == "agent_eval":
        return validate_agent_eval(document)
    if kind == "pocket_source":
        return validate_pocket_source(document)
    if kind == "voice_interaction":
        return validate_voice_interaction(document)
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


def valid_agent_eval() -> dict[str, Any]:
    return {
        "schema": "agent-eval/0.1",
        "eval_id": "evl_11111111111111111111111111111111",
        "delegation_ref": "del_11111111111111111111111111111111",
        "executor_ref": "runtime:worker:000001",
        "evaluator_ref": "verification:eval:000001",
        "criteria_refs": ["org:delegation:envelope-narrower", "org:delegation:budget-partition"],
        "evidence_refs": ["works:evidence:000007"],
        "verdict": "pass",
        "self_promoting": False,
        "mutates_governance": False,
        "waives_verification": False,
        "asserted_at": "2026-09-08T12:00:00Z",
        "tenant_id": "ten_11111111111111111111111111111111",
    }


def valid_pocket_source() -> dict[str, Any]:
    return {
        "schema": "pocket-source/0.1",
        "pocket_id": "pck_11111111111111111111111111111111",
        "tenant_id": "ten_11111111111111111111111111111111",
        "credential_scope": "ten_11111111111111111111111111111111",
        "source_ref": "pocket:rest:observations:000001",
        "observation_ref": "wie:observation:000001",
        "classification": "research",
        "claims_principal_identity": False,
        "claims_principal_authentication": False,
        "contains_instruction": False,
        "self_executes": False,
        "claims_execution": False,
        "candidate_kind": "observation_update",
        "admitted_by_tg": False,
        "governed_path_complete": False,
        "derivations": [
            {
                "derivation": "transcript",
                "weight": 0.7,
                "uncertainty": 0.3,
                "lineage_ref": "pocket:transcript:000001",
            }
        ],
        "asserted_at": "2026-09-08T12:00:00Z",
    }



def valid_voice_interaction() -> dict[str, Any]:
    return {
        "schema": "voice-interaction/0.1",
        "session_id": "ses_11111111111111111111111111111111",
        "tenant_id": "ten_11111111111111111111111111111111",
        "surface_ref": "interaction:surface:voice:000001",
        "thread_ref": "interaction:thread:000001",
        "turn_ref": "interaction:turn:000001",
        "observation_ref": "wie:observation:000001",
        "model_identity_ref": "voice:model:ephemeral:000001",
        "session_identity_disposable": True,
        "classification": "runtime",
        "embeds_durable_principal_identity": False,
        "embeds_durable_state": False,
        "admitted_by_tg": True,
        "tg_admission_ref": "tg:admission:000001",
        "egress_effect": False,
        "egress_grant_enforced": False,
        "claims_principal_identity": False,
        "claims_principal_authentication": False,
        "claims_authority": False,
        "principal_ref": "runtime:principal:000001",
        "interaction_state_ref": "runtime:interaction-state:000001",
        "memory_ref": "runtime:memory:000001",
        "mission_ref": "works:mission:000001",
        "consent_ref": "consent:ledger:000001",
        "asserted_at": "2026-09-08T12:00:00Z",
    }


def valid_pocket_webhook() -> dict[str, Any]:
    document = valid_pocket_source()
    document.update(
        {
            "source_ref": "pocket:webhook:deliveries:000010",
            "observation_ref": "wie:observation:000010",
            "delivery_channel": "webhook",
            "signature": "hmac-sha256:dlv_aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa:opaque010",
            "signature_scheme": "hmac-sha256",
            "delivery_id": "dlv_aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
            "idempotency_key": "idem_aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
            "sequence_number": 7,
            "seen_delivery_ids": [],
            "known_idempotency_keys": [],
            "materialized_observations": 1,
        }
    )
    return document


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

    def test_pocket_source_contract_is_strict_and_experimental(self) -> None:
        schema = load_json(POCKET_SCHEMA)
        self.assertFalse(schema.get("additionalProperties"), schema["title"])
        self.assertIn("EXPERIMENTAL", schema.get("description", ""))
        self.assertIn("authority", schema.get("description", "").lower())
        self.assertEqual(schema["properties"]["schema"]["const"], "pocket-source/0.1")

    def test_pocket_source_rejects_cross_tenant_credential_reuse(self) -> None:
        document = valid_pocket_source()
        self.assertEqual(validate_pocket_source(document), [])
        document["credential_scope"] = "ten_22222222222222222222222222222222"
        errors = validate_pocket_source(document)
        self.assertTrue(
            any("cross-tenant credential reuse" in error for error in errors)
        )
        document = valid_pocket_source()
        del document["credential_scope"]
        self.assertTrue(validate_pocket_source(document))

    def test_pocket_source_denies_identity_and_execution_authority(self) -> None:
        document = valid_pocket_source()
        document["claims_principal_identity"] = True
        self.assertTrue(
            any("not principal identity" in e for e in validate_pocket_source(document))
        )
        document = valid_pocket_source()
        document["claims_principal_authentication"] = True
        self.assertTrue(
            any("not principal authentication" in e for e in validate_pocket_source(document))
        )
        document = valid_pocket_source()
        document["contains_instruction"] = True
        document["self_executes"] = True
        self.assertTrue(
            any("never self-executes" in e for e in validate_pocket_source(document))
        )

    def test_pocket_source_vectors_are_registered(self) -> None:
        fixture = load_json(VECTORS)
        by_id = {vector.get("id"): vector for vector in fixture["vectors"]}
        for vector_id, expected in (
            ("PCK-001", "accept"),
            ("PCK-002", "reject"),
            ("PCK-003", "reject"),
            ("PCK-004", "reject"),
            ("PCK-005", "reject"),
            ("PCK-006", "accept"),
            ("PCK-007", "accept"),
            ("PCK-010", "accept"),
            ("PCK-011", "reject"),
            ("PCK-012", "reject"),
            ("PCK-013", "accept"),
            ("PCK-014", "accept"),
            ("PCK-015", "accept"),
            ("PCK-016", "accept"),
            ("PCK-017", "accept"),
            ("PCK-020", "accept"),
            ("PCK-021", "accept"),
            ("PCK-022", "accept"),
            ("PCK-023", "accept"),
            ("PCK-024", "accept"),
            ("PCK-025", "reject"),
            ("PCK-026", "accept"),
            ("PCK-027", "reject"),
        ):
            self.assertIn(vector_id, by_id)
            self.assertEqual(by_id[vector_id]["expected"], expected)

    def test_pocket_consent_purpose_lineage_accepted(self) -> None:
        document = valid_pocket_source()
        document["consent_ref"] = "consent:ledger:000020"
        document["purpose"] = "personalization"
        self.assertEqual(validate_pocket_source(document), [])
        document["consent_ref"] = ""
        self.assertTrue(
            any("invalid consent_ref" in e for e in validate_pocket_source(document))
        )

    def test_pocket_consent_revocation_invalidates_without_rewriting_audit(self) -> None:
        document = valid_pocket_source()
        document["consent_ref"] = "consent:ledger:000021"
        document["purpose"] = "personalization"
        document["consent_revoked"] = True
        document["downstream_invalidated"] = True
        self.assertEqual(validate_pocket_source(document), [])
        document = valid_pocket_source()
        document["consent_revoked"] = True
        self.assertTrue(
            any("invalidates downstream use" in e for e in validate_pocket_source(document))
        )
        document = valid_pocket_source()
        document["consent_revoked"] = True
        document["downstream_invalidated"] = True
        document["audit_rewritten"] = True
        self.assertTrue(
            any("never rewritten" in e for e in validate_pocket_source(document))
        )

    def test_pocket_source_deletion_propagates_with_tombstone(self) -> None:
        document = valid_pocket_source()
        document["source_deleted"] = True
        document["deletion_propagated"] = True
        document["tombstone"] = True
        document["withdrawn_from_reads"] = True
        document["audit_retained"] = True
        self.assertEqual(validate_pocket_source(document), [])
        document = valid_pocket_source()
        document["source_deleted"] = True
        self.assertTrue(
            any("propagates withdrawal" in e for e in validate_pocket_source(document))
        )

    def test_pocket_world_state_invalidation_never_stale(self) -> None:
        document = valid_pocket_source()
        document["consent_revoked"] = True
        document["downstream_invalidated"] = True
        document["projection_recomputed"] = True
        document["stale_served_as_current"] = False
        self.assertEqual(validate_pocket_source(document), [])
        document["stale_served_as_current"] = True
        self.assertTrue(
            any("never stale-served" in e for e in validate_pocket_source(document))
        )

    def test_pocket_prompt_injection_contained_never_instruction(self) -> None:
        document = valid_pocket_source()
        document["contains_instruction"] = True
        document["self_executes"] = False
        document["claims_execution"] = False
        document["injection_contained"] = True
        self.assertEqual(validate_pocket_source(document), [])
        document["self_executes"] = True
        self.assertTrue(
            any("never self-executes" in e for e in validate_pocket_source(document))
        )
        document = valid_pocket_source()
        document["contains_instruction"] = True
        document["claims_execution"] = True
        self.assertTrue(
            any("zero execution authority" in e for e in validate_pocket_source(document))
        )

    def test_pocket_cross_conversation_leak_rejected(self) -> None:
        document = valid_pocket_source()
        document["conversation_scope"] = "pocket:conversation:00AA"
        document["attributed_conversation"] = "pocket:conversation:00BB"
        self.assertTrue(
            any("without lineage" in e for e in validate_pocket_source(document))
        )
        document["cross_conversation_lineage"] = True
        self.assertEqual(validate_pocket_source(document), [])
        document = valid_pocket_source()
        document["conversation_scope"] = "pocket:conversation:00AA"
        document["attributed_conversation"] = "pocket:conversation:00AA"
        self.assertEqual(validate_pocket_source(document), [])

    def test_pocket_mcp_interactive_accepted_canonical_rejected(self) -> None:
        document = valid_pocket_source()
        document["access_mode"] = "interactive"
        self.assertEqual(validate_pocket_source(document), [])
        document["access_mode"] = "canonical"
        self.assertTrue(
            any("never canonical ingestion" in e for e in validate_pocket_source(document))
        )

    def test_pocket_webhook_valid_signature_accepted(self) -> None:
        self.assertEqual(validate_pocket_source(valid_pocket_webhook()), [])

    def test_pocket_webhook_bad_signature_rejected(self) -> None:
        document = valid_pocket_webhook()
        del document["signature"]
        self.assertTrue(validate_pocket_source(document))
        document = valid_pocket_webhook()
        document["signature_scheme"] = "none"
        self.assertTrue(validate_pocket_source(document))
        document = valid_pocket_webhook()
        document["signature"] = "hmac-sha256:dlv_ffffffffffffffffffffffffffffffff:opaque"
        self.assertTrue(
            any("not bound to delivery_id" in e for e in validate_pocket_source(document))
        )

    def test_pocket_webhook_replay_rejected(self) -> None:
        document = valid_pocket_webhook()
        document["seen_delivery_ids"] = [document["delivery_id"]]
        self.assertTrue(any("replay" in e for e in validate_pocket_source(document)))

    def test_pocket_webhook_duplicate_deduped_to_single_observation(self) -> None:
        document = valid_pocket_webhook()
        document["known_idempotency_keys"] = [document["idempotency_key"]]
        document["materialized_observations"] = 1
        self.assertEqual(validate_pocket_source(document), [])
        document["materialized_observations"] = 2
        self.assertTrue(
            any("single Observation" in e for e in validate_pocket_source(document))
        )

    def test_pocket_webhook_out_of_order_never_resurrects(self) -> None:
        document = valid_pocket_webhook()
        document["sequence_number"] = 3
        document["applied_sequence"] = 5
        document["resurrects_superseded_content"] = False
        self.assertEqual(validate_pocket_source(document), [])
        document["resurrects_superseded_content"] = True
        self.assertTrue(
            any("never be resurrected" in e for e in validate_pocket_source(document))
        )

    def test_pocket_edit_supersedes_with_lineage(self) -> None:
        document = valid_pocket_webhook()
        document["supersedes"] = "dlv_eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"
        document["lineage_preserved"] = True
        self.assertEqual(validate_pocket_source(document), [])
        document["lineage_preserved"] = False
        self.assertTrue(
            any("preserve lineage" in e for e in validate_pocket_source(document))
        )

    def test_pocket_tombstone_withdraws_but_retains_audit(self) -> None:
        document = valid_pocket_webhook()
        document["tombstone"] = True
        document["withdrawn_from_reads"] = True
        document["audit_retained"] = True
        self.assertEqual(validate_pocket_source(document), [])
        document["withdrawn_from_reads"] = False
        self.assertTrue(
            any("withdraw content from reads" in e for e in validate_pocket_source(document))
        )
        document["withdrawn_from_reads"] = True
        document["audit_retained"] = False
        self.assertTrue(
            any("retain audit" in e for e in validate_pocket_source(document))
        )

    def test_pocket_rest_reconciliation_converges_without_webhook_truth(self) -> None:
        document = valid_pocket_source()
        document["delivery_channel"] = "rest"
        document["reconciles_to_canonical"] = True
        document["webhook_claimed_as_truth"] = False
        self.assertEqual(validate_pocket_source(document), [])
        document["webhook_claimed_as_truth"] = True
        self.assertTrue(
            any("never reconciliation truth" in e for e in validate_pocket_source(document))
        )

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

    def test_agent_eval_contract_is_strict_and_experimental(self) -> None:
        schema = load_json(EVAL_SCHEMA)
        self.assertFalse(schema.get("additionalProperties"), schema["title"])
        self.assertIn("EXPERIMENTAL", schema.get("description", ""))
        self.assertIn("authority", schema.get("description", "").lower())
        self.assertEqual(schema["properties"]["schema"]["const"], "agent-eval/0.1")

    def test_independent_evaluator_scoring_a_delegation_accepts(self) -> None:
        document = valid_agent_eval()
        self.assertEqual(validate_agent_eval(document), [])

    def test_executor_cannot_score_own_execution(self) -> None:
        document = valid_agent_eval()
        self.assertEqual(validate_agent_eval(document), [])
        document["evaluator_ref"] = document["executor_ref"]
        errors = validate_agent_eval(document)
        self.assertTrue(
            any("never score their own execution" in error for error in errors)
        )

    def test_eval_scoring_requires_criteria_and_evidence(self) -> None:
        document = valid_agent_eval()
        document["criteria_refs"] = []
        errors = validate_agent_eval(document)
        self.assertTrue(
            any("explicit criteria" in error for error in errors)
        )
        document = valid_agent_eval()
        document["evidence_refs"] = []
        errors = validate_agent_eval(document)
        self.assertTrue(
            any("evidence references" in error for error in errors)
        )

    def test_eval_verdict_stays_advisory_only(self) -> None:
        for field, marker in (
            ("self_promoting", "advisory only"),
            ("mutates_governance", "mutates no governance"),
            ("waives_verification", "waives no verification"),
        ):
            with self.subTest(field=field):
                document = valid_agent_eval()
                document[field] = True
                errors = validate_agent_eval(document)
                self.assertTrue(
                    any(marker in error for error in errors),
                    f"{field} must fail closed",
                )

    def test_agent_eval_vectors_are_registered(self) -> None:
        fixture = load_json(VECTORS)
        by_id = {vector.get("id"): vector for vector in fixture["vectors"]}
        for vector_id, expected in (
            ("EVAL-001", "accept"),
            ("EVAL-002", "reject"),
            ("EVAL-003", "reject"),
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

    def test_voice_interaction_contract_is_strict_and_experimental(self) -> None:
        schema = load_json(VOICE_SCHEMA)
        self.assertFalse(schema.get("additionalProperties"), schema["title"])
        self.assertIn("EXPERIMENTAL", schema.get("description", ""))
        self.assertIn("authority", schema.get("description", "").lower())
        self.assertEqual(schema["properties"]["schema"]["const"], "voice-interaction/0.1")
        self.assertEqual(set(schema["required"]), VOICE_REQUIRED)
        for prop in (
            "turn_binding",
            "stop_verb",
            "governed_path_complete",
            "barge_in_terminates_execution",
            "contains_instruction",
            "self_executes",
            "candidate_kind",
            "session_identity_reused_as_durable_principal",
            "claims_realtime_raw_audio",
            "device_api_evidence_ref",
            "handoff_checkpoint",
            "correlation_refs",
            "destination_readmission_ref",
            "authority_transport",
            "continuity_basis",
            "purpose",
            "lineage_refs",
            "revocation_ref",
            "downstream_invalidated",
            "audit_rewritten",
            "deletion_ref",
            "withdrawn",
            "tombstone_ref",
            "source_surface_ref",
            "attributed_surface_ref",
            "injection_contained",
        ):
            self.assertIn(prop, schema["properties"])
            self.assertNotIn(prop, schema["required"])

    def test_voice_session_stateless_with_outside_durable_refs_accepts(self) -> None:
        document = valid_voice_interaction()
        self.assertEqual(validate_voice_interaction(document), [])

    def test_voice_session_embedding_durable_principal_rejected(self) -> None:
        document = valid_voice_interaction()
        self.assertEqual(validate_voice_interaction(document), [])
        document["embeds_durable_principal_identity"] = True
        errors = validate_voice_interaction(document)
        self.assertTrue(
            any("no durable principal identity" in error for error in errors)
        )

    def test_voice_session_embedding_durable_state_rejected(self) -> None:
        document = valid_voice_interaction()
        self.assertEqual(validate_voice_interaction(document), [])
        document["embeds_durable_state"] = True
        errors = validate_voice_interaction(document)
        self.assertTrue(
            any("no durable interaction/memory/mission state" in error for error in errors)
        )

    def test_voice_session_without_tg_admission_rejected(self) -> None:
        document = valid_voice_interaction()
        document["admitted_by_tg"] = False
        errors = validate_voice_interaction(document)
        self.assertTrue(
            any("passes Trust Gateway" in error for error in errors)
        )

    def test_voice_egress_effect_without_grant_enforcement_rejected(self) -> None:
        document = valid_voice_interaction()
        document["egress_effect"] = True
        document["egress_grant_enforced"] = False
        errors = validate_voice_interaction(document)
        self.assertTrue(
            any("grant enforcement" in error for error in errors)
        )
        document["egress_grant_enforced"] = True
        self.assertEqual(validate_voice_interaction(document), [])

    def test_voice_transcript_and_speaker_claim_no_identity(self) -> None:
        document = valid_voice_interaction()
        document["claims_principal_identity"] = True
        self.assertTrue(
            any("not principal identity" in e for e in validate_voice_interaction(document))
        )
        document = valid_voice_interaction()
        document["claims_principal_authentication"] = True
        self.assertTrue(
            any("not principal authentication" in e for e in validate_voice_interaction(document))
        )

    def test_voice_session_confers_no_authority(self) -> None:
        document = valid_voice_interaction()
        document["claims_authority"] = True
        errors = validate_voice_interaction(document)
        self.assertTrue(
            any("confer no authority" in error for error in errors)
        )

    def test_voice_session_identity_is_disposable(self) -> None:
        document = valid_voice_interaction()
        document["session_identity_disposable"] = False
        errors = validate_voice_interaction(document)
        self.assertTrue(
            any("is disposable" in error for error in errors)
        )

    def test_voice_turn_bound_to_disposable_session_identity_accepts(self) -> None:
        document = valid_voice_interaction()
        document["turn_binding"] = "disposable_session"
        self.assertEqual(validate_voice_interaction(document), [])

    def test_voice_speech_only_stop_verbs_interrupt_speech_or_turn_accept(self) -> None:
        for verb in ("STOP_SPEAKING", "CANCEL_TURN"):
            document = valid_voice_interaction()
            document["stop_verb"] = verb
            document["barge_in_terminates_execution"] = False
            self.assertEqual(validate_voice_interaction(document), [], verb)

    def test_voice_consequential_stop_verbs_require_governed_path(self) -> None:
        for verb in ("PAUSE_MISSION", "CANCEL_MISSION", "FREEZE_AUTONOMY"):
            document = valid_voice_interaction()
            document["stop_verb"] = verb
            document["governed_path_complete"] = False
            errors = validate_voice_interaction(document)
            self.assertTrue(
                any("governed consequential path" in error for error in errors),
                verb,
            )
        for verb in ("PAUSE_MISSION", "CANCEL_MISSION", "FREEZE_AUTONOMY"):
            document = valid_voice_interaction()
            document["stop_verb"] = verb
            document["governed_path_complete"] = True
            self.assertEqual(validate_voice_interaction(document), [], verb)

    def test_voice_barge_in_terminating_execution_rejected(self) -> None:
        document = valid_voice_interaction()
        document["stop_verb"] = "STOP_SPEAKING"
        document["barge_in_terminates_execution"] = True
        errors = validate_voice_interaction(document)
        self.assertTrue(
            any("never terminates consequential execution" in error for error in errors)
        )

    def test_voice_spoken_instruction_self_execution_rejected(self) -> None:
        document = valid_voice_interaction()
        document["contains_instruction"] = True
        document["self_executes"] = True
        document["governed_path_complete"] = False
        errors = validate_voice_interaction(document)
        self.assertTrue(
            any("never self-executes" in error for error in errors)
        )
        self.assertTrue(
            any(
                "AIE -> Trust Gateway -> Runtime -> WORKS -> verification" in error
                for error in errors
            )
        )

    def test_voice_commitment_candidate_through_governed_path_accepts(self) -> None:
        document = valid_voice_interaction()
        document["candidate_kind"] = "commitment_candidate"
        document["governed_path_complete"] = True
        document["egress_effect"] = True
        document["egress_grant_enforced"] = True
        self.assertEqual(validate_voice_interaction(document), [])
        document = valid_voice_interaction()
        document["candidate_kind"] = "commitment_candidate"
        document["governed_path_complete"] = False
        errors = validate_voice_interaction(document)
        self.assertTrue(
            any("governed consequential path" in error for error in errors)
        )

    def test_voice_session_identity_reuse_as_durable_principal_rejected(self) -> None:
        document = valid_voice_interaction()
        document["session_identity_reused_as_durable_principal"] = True
        errors = validate_voice_interaction(document)
        self.assertTrue(
            any("never reused as a durable principal" in error for error in errors)
        )

    def test_voice_realtime_raw_audio_claim_is_evidence_gated(self) -> None:
        document = valid_voice_interaction()
        document["claims_realtime_raw_audio"] = True
        errors = validate_voice_interaction(document)
        self.assertTrue(
            any("device/API evidence" in error for error in errors)
        )
        document["device_api_evidence_ref"] = "device:audio-api:evidence:000001"
        self.assertEqual(validate_voice_interaction(document), [])

    def test_voice_handoff_with_correlation_and_readmission_accepts(self) -> None:
        document = valid_voice_interaction()
        document.update(
            {
                "handoff_checkpoint": "voice:handoff:000001",
                "correlation_refs": [
                    "platform-event-ref:evt_11111111111111111111111111111111"
                ],
                "destination_readmission_ref": "tg:admission:000002",
                "authority_transport": False,
                "continuity_basis": "correlation_provenance",
            }
        )
        self.assertEqual(validate_voice_interaction(document), [])

    def test_voice_handoff_without_correlation_or_readmission_rejected(self) -> None:
        document = valid_voice_interaction()
        document["handoff_checkpoint"] = "voice:handoff:000001"
        errors = validate_voice_interaction(document)
        self.assertTrue(
            any("correlation/provenance" in error for error in errors)
        )
        self.assertTrue(
            any("re-admitted at the destination" in error for error in errors)
        )

    def test_voice_authority_transport_rejected(self) -> None:
        document = valid_voice_interaction()
        document.update(
            {
                "handoff_checkpoint": "voice:handoff:000001",
                "correlation_refs": [
                    "platform-event-ref:evt_11111111111111111111111111111111"
                ],
                "destination_readmission_ref": "tg:admission:000002",
                "authority_transport": True,
            }
        )
        errors = validate_voice_interaction(document)
        self.assertTrue(
            any("never moves authority" in error for error in errors)
        )

    def test_voice_conversation_memory_continuity_rejected(self) -> None:
        for basis in ("conversation", "memory", "session_authority"):
            document = valid_voice_interaction()
            document["continuity_basis"] = basis
            errors = validate_voice_interaction(document)
            self.assertTrue(
                any("Conversation != Memory" in error for error in errors),
                basis,
            )

    def test_voice_consent_purpose_lineage_accepts(self) -> None:
        document = valid_voice_interaction()
        document.update(
            {
                "purpose": "care-coordination",
                "lineage_refs": ["voice:turn:lineage:000001"],
            }
        )
        self.assertEqual(validate_voice_interaction(document), [])

    def test_voice_revocation_invalidates_downstream_without_audit_rewrite(self) -> None:
        document = valid_voice_interaction()
        document.update(
            {
                "revocation_ref": "consent:revocation:000001",
                "downstream_invalidated": True,
                "audit_rewritten": False,
            }
        )
        self.assertEqual(validate_voice_interaction(document), [])
        document = valid_voice_interaction()
        document.update(
            {
                "revocation_ref": "consent:revocation:000001",
                "downstream_invalidated": True,
                "audit_rewritten": True,
            }
        )
        errors = validate_voice_interaction(document)
        self.assertTrue(
            any("never rewrite historical audit" in error for error in errors)
        )

    def test_voice_deletion_withdrawal_with_tombstone_accepts(self) -> None:
        document = valid_voice_interaction()
        document.update(
            {
                "deletion_ref": "voice:deletion:000001",
                "withdrawn": True,
                "tombstone_ref": "voice:tombstone:000001",
            }
        )
        self.assertEqual(validate_voice_interaction(document), [])
        document = valid_voice_interaction()
        document.update({"deletion_ref": "voice:deletion:000001", "withdrawn": True})
        errors = validate_voice_interaction(document)
        self.assertTrue(
            any("tombstone" in error for error in errors)
        )

    def test_voice_cross_surface_attribution_without_lineage_rejected(self) -> None:
        document = valid_voice_interaction()
        document.update(
            {
                "source_surface_ref": "interaction:surface:voice:000001",
                "attributed_surface_ref": "interaction:surface:chat:000002",
            }
        )
        errors = validate_voice_interaction(document)
        self.assertTrue(
            any("without explicit lineage" in error for error in errors)
        )
        document["lineage_refs"] = ["voice:turn:lineage:000001"]
        document["purpose"] = "care-coordination"
        self.assertEqual(validate_voice_interaction(document), [])

    def test_voice_prompt_injection_contained_as_observation(self) -> None:
        document = valid_voice_interaction()
        document.update(
            {
                "contains_instruction": True,
                "self_executes": False,
                "injection_contained": True,
            }
        )
        self.assertEqual(validate_voice_interaction(document), [])
        document = valid_voice_interaction()
        document.update({"contains_instruction": True, "self_executes": True})
        errors = validate_voice_interaction(document)
        self.assertTrue(
            any("never self-executes" in error for error in errors)
        )
        document = valid_voice_interaction()
        document["contains_instruction"] = True
        errors = validate_voice_interaction(document)
        self.assertTrue(
            any("untrusted observation" in error for error in errors)
        )

    def test_voice_interaction_vectors_are_registered(self) -> None:
        fixture = load_json(VECTORS)
        by_id = {vector.get("id"): vector for vector in fixture["vectors"]}
        for vector_id, expected in (
            ("VOI-001", "accept"),
            ("VOI-002", "reject"),
            ("VOI-003", "reject"),
            ("VOI-004", "reject"),
            ("VOI-005", "reject"),
            ("VOI-006", "reject"),
            ("VOI-007", "reject"),
            ("VOI-010", "accept"),
            ("VOI-011", "accept"),
            ("VOI-012", "accept"),
            ("VOI-013", "reject"),
            ("VOI-014", "reject"),
            ("VOI-015", "accept"),
            ("VOI-016", "reject"),
            ("VOI-017", "reject"),
            ("VOI-020", "accept"),
            ("VOI-021", "reject"),
            ("VOI-022", "reject"),
            ("VOI-023", "accept"),
            ("VOI-024", "accept"),
            ("VOI-025", "accept"),
            ("VOI-026", "reject"),
            ("VOI-027", "accept"),
        ):
            self.assertIn(vector_id, by_id)
            self.assertEqual(by_id[vector_id]["expected"], expected)

    def test_rfc3339_timestamp_requires_time_and_offset(self) -> None:
        self.assertFalse(parse_rfc3339("2026-09-08"))
        self.assertFalse(parse_rfc3339("2026-09-08T12:00:00"))
        self.assertTrue(parse_rfc3339("2026-09-08T12:00:00Z"))
        self.assertTrue(parse_rfc3339("2026-09-08T12:00:00+02:00"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
