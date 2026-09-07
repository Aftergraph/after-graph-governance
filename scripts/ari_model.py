#!/usr/bin/env python3
"""Shared deterministic primitives for Aftergraph Release Intelligence (ARI)."""

from __future__ import annotations

import hashlib
import json
import re
from enum import Enum, IntEnum
from pathlib import Path
from typing import Any

APC_LEVEL = "APC-1"
APC_PROFILES = {
    "authority",
    "service",
    "runtime",
    "execution",
    "verifier",
    "product",
    "model",
    "research",
}
LIFECYCLE = {
    "stable",
    "preview",
    "experimental",
    "research",
    "legacy",
    "deprecated",
    "retired",
    "ephemeral",
}
EDGE_RELATIONS = {"requires", "tested-with", "incompatible-with", "conforms-to", "supports"}
EDGE_STATES = {"pass", "fail", "unknown", "stale", "not-applicable"}
COMMIT_RE = re.compile(r"^[a-f0-9]{40}$")
RELEASE_TRAIN_RE = re.compile(r"^20[0-9]{2}\.(0[1-9]|1[0-2])$")


class ResultState(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    UNKNOWN = "UNKNOWN"
    STALE = "STALE"
    N_A = "N/A"


class EvidenceLevel(IntEnum):
    CE0 = 0
    CE1 = 1
    CE2 = 2
    CE3 = 3
    CE4 = 4
    CE5 = 5


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        document = json.load(handle)
    if not isinstance(document, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return document


def canonical_digest(document: dict[str, Any]) -> str:
    payload = json.dumps(
        document,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def evidence_meets(actual: str, minimum: str) -> bool:
    try:
        return EvidenceLevel[actual] >= EvidenceLevel[minimum]
    except KeyError:
        return False


def _require_object(document: Any, name: str, errors: list[str]) -> dict[str, Any]:
    if not isinstance(document, dict):
        errors.append(f"{name} must be an object")
        return {}
    return document


def _require_fields(document: dict[str, Any], required: tuple[str, ...], prefix: str, errors: list[str]) -> None:
    for field in required:
        if field not in document:
            errors.append(f"missing required field: {prefix}{field}")


def validate_component(document: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if not isinstance(document, dict):
        return ["component manifest must be an object"]

    _require_fields(
        document,
        ("schema", "identity", "release", "platform", "compatibility", "contracts", "provenance"),
        "",
        errors,
    )
    if document.get("schema") != "aftergraph-component/1.0":
        errors.append("schema must be aftergraph-component/1.0")

    identity = _require_object(document.get("identity"), "identity", errors)
    _require_fields(identity, ("component",), "identity.", errors)
    if not isinstance(identity.get("component"), str) or not identity.get("component"):
        errors.append("identity.component must be a non-empty string")

    release = _require_object(document.get("release"), "release", errors)
    _require_fields(release, ("version", "lifecycle"), "release.", errors)
    if not isinstance(release.get("version"), str) or not release.get("version"):
        errors.append("release.version must be a non-empty string")
    if release.get("lifecycle") not in LIFECYCLE:
        errors.append(f"unsupported lifecycle: {release.get('lifecycle')}")

    platform = _require_object(document.get("platform"), "platform", errors)
    _require_fields(platform, ("generation", "release_train"), "platform.", errors)
    if platform.get("generation") != 26:
        errors.append("platform.generation must be 26")
    release_train = platform.get("release_train")
    if not isinstance(release_train, str) or not RELEASE_TRAIN_RE.fullmatch(release_train):
        errors.append("platform.release_train must match YYYY.MM")

    compatibility = _require_object(document.get("compatibility"), "compatibility", errors)
    _require_fields(compatibility, ("level", "profiles", "minimum", "tested_against"), "compatibility.", errors)
    if compatibility.get("level") != APC_LEVEL:
        errors.append("compatibility.level must be APC-1")
    if compatibility.get("minimum") != APC_LEVEL:
        errors.append("compatibility.minimum must be APC-1")
    if compatibility.get("tested_against") != APC_LEVEL:
        errors.append("compatibility.tested_against must be APC-1")
    profiles = compatibility.get("profiles")
    if not isinstance(profiles, list):
        errors.append("compatibility.profiles must be an array")
    else:
        seen: set[str] = set()
        for profile in profiles:
            if profile not in APC_PROFILES:
                errors.append(f"unsupported APC-1 profile: {profile}")
            if profile in seen:
                errors.append(f"duplicate APC-1 profile: {profile}")
            seen.add(profile)

    contracts = document.get("contracts")
    if not isinstance(contracts, dict):
        errors.append("contracts must be an object")
    else:
        for name, version in contracts.items():
            if not isinstance(name, str) or not name:
                errors.append("contract names must be non-empty strings")
            if not isinstance(version, str) or not version:
                errors.append(f"contracts.{name} must be a non-empty string")

    provenance = _require_object(document.get("provenance"), "provenance", errors)
    _require_fields(provenance, ("repository", "commit"), "provenance.", errors)
    commit = provenance.get("commit")
    if not isinstance(commit, str) or not COMMIT_RE.fullmatch(commit):
        errors.append("provenance.commit must be 40 lowercase hex characters")
    repository = provenance.get("repository")
    if not isinstance(repository, str) or repository.count("/") != 1:
        errors.append("provenance.repository must be owner/repo")

    return errors


def validate_edge(document: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if not isinstance(document, dict):
        return ["compatibility edge must be an object"]

    _require_fields(document, ("schema", "from", "to", "relation", "state", "evidence_level", "evidence"), "", errors)
    if document.get("schema") != "compatibility-edge/1.0":
        errors.append("schema must be compatibility-edge/1.0")

    for side in ("from", "to"):
        endpoint = _require_object(document.get(side), side, errors)
        _require_fields(endpoint, ("component", "version", "commit"), f"{side}.", errors)
        if not isinstance(endpoint.get("component"), str) or not endpoint.get("component"):
            errors.append(f"{side}.component must be a non-empty string")
        if not isinstance(endpoint.get("version"), str) or not endpoint.get("version"):
            errors.append(f"{side}.version must be a non-empty string")
        commit = endpoint.get("commit")
        if not isinstance(commit, str) or not COMMIT_RE.fullmatch(commit):
            errors.append(f"{side}.commit must be 40 lowercase hex characters")

    relation = document.get("relation")
    if relation not in EDGE_RELATIONS:
        errors.append(f"unsupported edge relation: {relation}")
    state = document.get("state")
    if state not in EDGE_STATES:
        errors.append(f"unsupported edge state: {state}")
    evidence_level = document.get("evidence_level")
    if not isinstance(evidence_level, str) or evidence_level not in EvidenceLevel.__members__:
        errors.append(f"unsupported evidence level: {evidence_level}")

    evidence = document.get("evidence")
    if not isinstance(evidence, list):
        errors.append("evidence must be an array")
    else:
        for index, item in enumerate(evidence):
            if not isinstance(item, dict):
                errors.append(f"evidence[{index}] must be an object")
                continue
            if not isinstance(item.get("kind"), str) or not item.get("kind"):
                errors.append(f"evidence[{index}].kind must be a non-empty string")
            if not isinstance(item.get("ref"), str) or not item.get("ref"):
                errors.append(f"evidence[{index}].ref must be a non-empty string")

    return errors
