#!/usr/bin/env python3
"""Experimental zero-dependency Program Overlay validator and shadow evaluator."""
from __future__ import annotations

import argparse
import json
import sys
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
OVERLAY_STATUSES = {"proposed", "active", "paused", "complete", "superseded"}
TOUCH_MODES = {"core", "next", "consumer", "observer"}
CLAIM_MODES = {"READ", "WRITE", "MIGRATE", "VERIFY", "OBSERVE"}
CLAIM_STATUSES = {"active", "released", "expired", "superseded"}


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


def parse_utc_timestamp(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("timestamp must include timezone")
    return parsed.astimezone(timezone.utc)


def validate_seam_registry(seams: Mapping[str, Any], topology: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    repos = topology_index(topology)
    seen: set[str] = set()
    rows = seams.get("seams", [])
    if not isinstance(rows, list):
        return ["seams must be a list"]
    for row in rows:
        if not isinstance(row, Mapping):
            errors.append("seam entry must be an object")
            continue
        seam_id = row.get("id")
        owner = row.get("owner_repo")
        if not isinstance(seam_id, str) or not seam_id:
            errors.append("seam id must be a non-empty string")
            continue
        if seam_id in seen:
            errors.append(f"duplicate seam id: {seam_id}")
        seen.add(seam_id)
        if owner not in repos:
            errors.append(f"unknown seam owner repo: {owner!r}")
    return errors


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

    status = overlay.get("status")
    if status not in OVERLAY_STATUSES:
        errors.append(f"unknown overlay status: {status!r}")

    active_slices = overlay.get("active_slices")
    if not isinstance(active_slices, list) or any(
        not isinstance(item, str) or not item.strip() for item in active_slices
    ):
        errors.append("active_slices must be a list of non-empty strings")

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
        elif mode in {"core", "next"} and repo != seam_map[seam].get("owner_repo"):
            errors.append(
                f"{mode} touch does not match seam owner: repo={repo!r}, "
                f"seam={seam!r}, owner={seam_map[seam].get('owner_repo')!r}"
            )
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
    seen_ids: set[str] = set()
    for row in rows:
        if not isinstance(row, Mapping):
            errors.append("claim must be an object")
            continue
        claim_id = row.get("claim_id")
        if not isinstance(claim_id, str) or not claim_id.strip():
            errors.append("claim_id must be a non-empty string")
        elif claim_id in seen_ids:
            errors.append(f"duplicate claim_id: {claim_id}")
        else:
            seen_ids.add(claim_id)
        if row.get("seam") not in seam_map:
            errors.append(f"unknown seam in claim: {row.get('seam')!r}")
        if row.get("mode") not in CLAIM_MODES:
            errors.append(f"unknown claim mode: {row.get('mode')!r}")
        status = row.get("status")
        if status not in CLAIM_STATUSES:
            errors.append(f"unknown claim status: {status!r}")
        expires_at = row.get("expires_at")
        if expires_at is not None:
            if not isinstance(expires_at, str):
                errors.append("expires_at must be an ISO-8601 string")
            else:
                try:
                    parse_utc_timestamp(expires_at)
                except ValueError:
                    errors.append(f"invalid expires_at timestamp: {expires_at!r}")
    return errors


def active_claims(claims: Mapping[str, Any], now: datetime | None) -> list[Mapping[str, Any]]:
    current = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    result: list[Mapping[str, Any]] = []
    for claim in claims.get("claims", []):
        if not isinstance(claim, Mapping) or claim.get("status") != "active":
            continue
        expires_at = claim.get("expires_at")
        if isinstance(expires_at, str):
            expires = parse_utc_timestamp(expires_at)
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


def evaluate_direction(
    overlay: Mapping[str, Any],
    topology: Mapping[str, Any],
    seams: Mapping[str, Any],
    claims: Mapping[str, Any],
    now: datetime | None = None,
) -> dict[str, Any]:
    seam_errors = validate_seam_registry(seams, topology)
    overlay_errors = validate_overlay(overlay, topology, seams)
    claim_errors = validate_claims(claims, seams)
    conflicts = claim_conflicts(claims, now) if not claim_errors else []

    unknowns = seam_errors + overlay_errors + claim_errors
    if unknowns:
        decision = "UNKNOWN"
    elif conflicts:
        decision = "BLOCK"
    else:
        decision = "PASS"

    active_slices_value = overlay.get("active_slices", [])
    active_slices = list(active_slices_value) if isinstance(active_slices_value, list) else []
    return {
        "decision": decision,
        "program_id": overlay.get("program_id"),
        "active_slices": active_slices,
        "reasons": [],
        "violated_invariants": [],
        "conflicting_claims": conflicts,
        "unknowns": unknowns,
        "evidence_refs": ["docs/platform-topology/2.0.json"],
        "mode": "shadow",
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("check", help="validate default Program Overlay inputs")
    evaluate = sub.add_parser("evaluate", help="evaluate direction in shadow mode")
    evaluate.add_argument("--claims", type=Path, default=DEFAULT_CLAIMS)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    overlay = load_json(DEFAULT_OVERLAY)
    topology = load_json(DEFAULT_TOPOLOGY)
    seams = load_json(DEFAULT_SEAMS)
    claims_path = getattr(args, "claims", DEFAULT_CLAIMS)
    claims = load_json(claims_path)

    seam_errors = validate_seam_registry(seams, topology)
    overlay_errors = validate_overlay(overlay, topology, seams)
    claim_errors = validate_claims(claims, seams)
    if args.command == "check":
        errors = seam_errors + overlay_errors + claim_errors
        if errors:
            print(json.dumps({"decision": "UNKNOWN", "unknowns": errors}, indent=2, sort_keys=True))
            return 3
        print(json.dumps({"decision": "PASS", "mode": "shadow"}, indent=2, sort_keys=True))
        return 0

    result = evaluate_direction(overlay, topology, seams, claims)
    print(json.dumps(result, indent=2, sort_keys=True))
    return {"PASS": 0, "WARN": 0, "BLOCK": 2, "UNKNOWN": 3}[result["decision"]]


if __name__ == "__main__":
    sys.exit(main())
