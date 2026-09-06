#!/usr/bin/env python3
"""Verify Exact-Head Truth records (contract:exact-head-truth/1.0).

Usage:
  python scripts/verify_exact_head_truth.py <record.json> [--head <sha>] [--max-age-seconds N]

Checks:
 1. record parses as JSON object and satisfies the contract schema
    (required fields, types, enums, sha/repo/timestamp formats)
 2. with --head: record.sha must equal the claimed current head,
    otherwise the status is STALE and rejected
 3. with --max-age-seconds (default 3600): record.timestamp must not be
    older than the window, otherwise STALE

Exit 0 + "OK" on truth; exit 1 with reasons otherwise.
Stdlib only.
"""
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = json.loads((ROOT / "docs/contracts/exact-head-truth/1.0.json").read_text(encoding="utf-8"))

SHA_RE = re.compile(r"^[a-f0-9]{40}$")
REPO_RE = re.compile(r"^[a-zA-Z0-9_-]+/[a-zA-Z0-9_.-]+$")
SOURCES = {"github-actions", "self-hosted", "works-control-plane", "manual", "agent"}
STATUSES = {"success", "failure", "cancelled", "timeout", "queued", "running"}
TERMINAL = {"success", "failure", "cancelled", "timeout"}


def fail(errors, msg):
    errors.append(msg)


def validate_schema(rec):
    """Hand-rolled check of the contract schema (stdlib; no jsonschema dep)."""
    errors = []
    if not isinstance(rec, dict):
        return ["record must be a JSON object"]
    allowed = set(SCHEMA["properties"])
    for f in SCHEMA["required"]:
        if f not in rec:
            fail(errors, f"missing required field: {f}")
    for f in rec:
        if f not in allowed:
            fail(errors, f"unknown field: {f}")
    if "repo" in rec and not (isinstance(rec["repo"], str) and REPO_RE.match(rec["repo"])):
        fail(errors, "repo must match org/repo format")
    if "sha" in rec and not (isinstance(rec["sha"], str) and SHA_RE.match(rec["sha"])):
        fail(errors, "sha must be a 40-char lowercase hex commit SHA")
    if "run_id" in rec and not (isinstance(rec["run_id"], str) and rec["run_id"]):
        fail(errors, "run_id must be a non-empty string")
    if "attempt" in rec and not (isinstance(rec["attempt"], int) and not isinstance(rec["attempt"], bool) and rec["attempt"] >= 1):
        fail(errors, "attempt must be an integer >= 1")
    if "timestamp" in rec:
        if not isinstance(rec["timestamp"], str) or not parse_ts(rec["timestamp"]):
            fail(errors, "timestamp must be ISO8601 UTC (e.g. 2026-09-06T08:00:00Z)")
    if "source" in rec and rec["source"] not in SOURCES:
        fail(errors, f"source must be one of {sorted(SOURCES)}")
    if "status" in rec and rec["status"] not in STATUSES:
        fail(errors, f"status must be one of {sorted(STATUSES)}")
    if "context" in rec and not (isinstance(rec["context"], str) and rec["context"]):
        fail(errors, "context must be a non-empty string")
    if "details_url" in rec and not (isinstance(rec["details_url"], str) and re.match(r"^https?://", rec["details_url"])):
        fail(errors, "details_url must be an http(s) URI")
    if "freshness_window_seconds" in rec and not (isinstance(rec["freshness_window_seconds"], int) and not isinstance(rec["freshness_window_seconds"], bool) and rec["freshness_window_seconds"] >= 0):
        fail(errors, "freshness_window_seconds must be an integer >= 0")
    return errors


def parse_ts(s):
    try:
        if s.endswith("Z"):
            s = s[:-1] + "+00:00"
        dt = datetime.fromisoformat(s)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except (ValueError, TypeError):
        return None


def main(argv):
    if len(argv) < 2 or argv[1] in ("-h", "--help"):
        print(__doc__.strip().splitlines()[0])
        print("usage: verify_exact_head_truth.py <record.json> [--head <sha>] [--max-age-seconds N]")
        return 2 if len(argv) < 2 else 0
    path = Path(argv[1])
    head = None
    max_age = 3600
    i = 2
    while i < len(argv):
        if argv[i] == "--head" and i + 1 < len(argv):
            head = argv[i + 1]
            i += 2
        elif argv[i] == "--max-age-seconds" and i + 1 < len(argv):
            try:
                max_age = int(argv[i + 1])
            except ValueError:
                print(f"FAIL: --max-age-seconds must be an integer, got {argv[i + 1]!r}")
                return 1
            i += 2
        else:
            print(f"FAIL: unknown argument {argv[i]!r}")
            return 1
    try:
        rec = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        print(f"FAIL: record not found: {path}")
        return 1
    except json.JSONDecodeError as e:
        print(f"FAIL: record is not valid JSON: {e}")
        return 1

    errors = validate_schema(rec)
    if errors:
        for e in errors:
            print(f"FAIL: {e}")
        return 1

    # ponytail: per-record window overrides the CLI default; CLI flag wins if explicitly passed
    window = rec.get("freshness_window_seconds", max_age if "--max-age-seconds" in argv else 3600)
    if "--max-age-seconds" in argv:
        window = max_age

    ts = parse_ts(rec["timestamp"])
    age = (datetime.now(timezone.utc) - ts).total_seconds()
    if age < -60:
        print(f"FAIL: timestamp is in the future ({rec['timestamp']})")
        return 1
    if age > window:
        print(f"FAIL: STALE — record age {int(age)}s exceeds window {window}s")
        return 1

    if head is not None:
        if not SHA_RE.match(head):
            print("FAIL: --head must be a 40-char lowercase hex commit SHA")
            return 1
        if rec["sha"] != head:
            print(f"FAIL: STALE — record binds to {rec['sha'][:12]}, current head is {head[:12]}")
            return 1

    terminal = "terminal" if rec["status"] in TERMINAL else "intermediate"
    print(f"OK: {rec['repo']}@{rec['sha'][:12]} {rec['context']}={rec['status']} ({terminal}, via {rec['source']}, run {rec['run_id']}#{rec['attempt']})")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
