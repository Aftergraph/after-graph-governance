#!/usr/bin/env python3
"""Experimental zero-dependency Program Overlay validator and shadow evaluator."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TOPOLOGY = REPO_ROOT / "docs/platform-topology/2.0.json"
DEFAULT_OVERLAY = REPO_ROOT / "docs/program-overlay/mission-continuity.json"
DEFAULT_SEAMS = REPO_ROOT / "docs/semantic-seams/0.1.json"
DEFAULT_CLAIMS = REPO_ROOT / "docs/semantic-claims/empty.json"

REQUIRED_OVERLAY_FIELDS = {
    "schema", "program_id", "parent_program", "objective", "status",
    "active_slices", "touches", "invariants", "blocked_by", "success",
}
ALLOWED_OVERLAY_FIELDS = REQUIRED_OVERLAY_FIELDS
FORBIDDEN_TRUTH_FIELDS = {
    "remote_head_sha", "head_sha", "commit_sha", "canonical_branch",
    "owns", "must_not_own",
}
TOUCH_MODES = {"core", "next", "consumer", "observer"}
CLAIM_MODES = {"READ", "WRITE", "MIGRATE", "VERIFY", "OBSERVE"}


def load_json(path: Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        doc = json.load(handle)
    if not isinstance(doc, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return doc


def topology_index(doc: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    repos = doc.get("repositories", [])
    if not isinstance(repos, list):
        raise ValueError("topology document has no repository list")
    return {entry["name"]: entry for entry in repos if isinstance(entry, Mapping) and "name" in entry}


def seam_index(doc: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    seams = doc.get("seams", [])
    if not isinstance(seams, list):
        raise ValueError("semantic seam document has no seam list")
    return {entry["id"]: entry for entry in seams if isinstance(entry, Mapping) and "id" in entry}


def validate_overlay(overlay: Mapping[str, Any], topology: Mapping[str, Any], seams: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    if overlay.get("schema") != "aftergraph-program/0.1":
        errors.append(f"unsupported overlay schema: {overlay.get('schema')!r}")
    missing = REQUIRED_OVERLAY_FIELDS - set(overlay)
    if missing:
        errors.append(f"overlay missing fields: {sorted(missing)}")
    for field in set(overlay) & FORBIDDEN_TRUTH_FIELDS:
        errors.append(f"forbidden truth field in overlay: {field}")
    for field in set(overlay) - ALLOWED_OVERLAY_FIELDS - FORBIDDEN_TRUTH_FIELDS:
        errors.append(f"unexpected overlay field: {field}")

    repos = topology_index(topology)
    seam_map = seam_index(seams)
    touches = overlay.get("touches", [])
    if not isinstance(touches, list):
        return errors + ["touches must be a list"]
    for touch in touches:
        if not isinstance(touch, Mapping):
            errors.append("touch entry must be an object")
            continue
        repo = touch.get("repo")
        seam = touch.get("seam")
        mode = touch.get("mode")
        if repo not in repos:
            errors.append(f"unknown repo in touch: {repo!r}")
        if seam not in seam_map:
            errors.append(f"unknown seam in touch: {seam!r}")
        if mode not in TOUCH_MODES:
            errors.append(f"unknown touch mode: {mode!r}")
    return errors


def validate_claims(claims: Mapping[str, Any], seams: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    if claims.get("schema") != "semantic-claims/0.1":
        errors.append(f"unsupported claims schema: {claims.get('schema')!r}")
    seam_map = seam_index(seams)
    rows = claims.get("claims", [])
    if not isinstance(rows, list):
        return errors + ["claims must be a list"]
    for row in rows:
        if not isinstance(row, Mapping):
            errors.append("claim must be an object")
            continue
        if row.get("seam") not in seam_map:
            errors.append(f"unknown seam in claim: {row.get('seam')!r}")
        if row.get("mode") not in CLAIM_MODES:
            errors.append(f"unknown claim mode: {row.get('mode')!r}")
    return errors


def active_claims(claims: Mapping[str, Any], now: datetime | None) -> list[Mapping[str, Any]]:
    current = now or datetime.now(timezone.utc)
    result: list[Mapping[str, Any]] = []
    for claim in claims.get("claims", []):
        if not isinstance(claim, Mapping) or claim.get("status") != "active":
            continue
        expires_at = claim.get("expires_at")
        if isinstance(expires_at, str):
            expires = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
            if expires <= current:
                continue
        result.append(claim)
    return result


def claim_conflicts(claims: Mapping[str, Any], now: datetime | None) -> list[dict[str, Any]]:
    rows = active_claims(claims, now)
    conflicts: list[dict[str, Any]] = []
    for i, left in enumerate(rows):
        for right in rows[i + 1:]:
            if left.get("seam") != right.get("seam"):
                continue
            pair = {left.get("mode"), right.get("mode")}
            kind = None
            if pair == {"WRITE"}:
                kind = "WRITE_WRITE"
            elif "MIGRATE" in pair and ("WRITE" in pair or "MIGRATE" in pair):
                kind = "MIGRATE_WRITE" if "WRITE" in pair else "MIGRATE_MIGRATE"
            if kind:
                conflicts.append({
                    "kind": kind,
                    "seam": left.get("seam"),
                    "claims": [left.get("claim_id"), right.get("claim_id")],
                })
    return conflicts
