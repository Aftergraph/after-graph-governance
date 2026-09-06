#!/usr/bin/env python3
"""Reduce a Canonical CI Result to one current-head truth decision.

Usage:
  python scripts/reduce_ci_truth.py <ci-result.json> --head <sha>
      [--required-context NAME ...] [--max-age-seconds N] [--json]

Decisions:
  PASS        exact current SHA, fresh record, every required context succeeds
  BLOCKED     exact/fresh record, at least one required context failed/timed out/cancelled
  STALE       record SHA differs from current head or record is older than the freshness window
  INCOMPLETE  a required context is absent or the result contains no contexts
  IN_PROGRESS a required context is queued or running
  INVALID     record shape or value is not a Canonical CI Result

Exit code is 0 only for PASS. Every non-PASS decision is a failing gate.
Stdlib only; no network calls and no provider defaults.
"""
import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

SHA_RE = re.compile(r"^[a-f0-9]{40}$")
REPO_RE = re.compile(r"^[a-zA-Z0-9_-]+/[a-zA-Z0-9_.-]+$")
SOURCES = {"github-actions", "self-hosted", "works-control-plane", "manual", "agent"}
STATUSES = {"success", "failure", "cancelled", "timeout", "queued", "running"}
BLOCKING = {"failure", "cancelled", "timeout"}
ACTIVE = {"queued", "running"}
REQUIRED = ("repo", "sha", "source", "run_id", "attempt", "timestamp", "environment", "results")


def parse_timestamp(value):
    try:
        normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
        parsed = datetime.fromisoformat(normalized)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)
    except (TypeError, ValueError):
        return None


def validate(record):
    """Return a list of schema errors without requiring jsonschema."""
    if not isinstance(record, dict):
        return ["record must be an object"]
    errors = [f"missing required field: {field}" for field in REQUIRED if field not in record]
    if errors:
        return errors
    if not isinstance(record["repo"], str) or not REPO_RE.fullmatch(record["repo"]):
        errors.append("repo must match org/repo format")
    if not isinstance(record["sha"], str) or not SHA_RE.fullmatch(record["sha"]):
        errors.append("sha must be a 40-character lowercase hex string")
    if record["source"] not in SOURCES:
        errors.append(f"source must be one of {sorted(SOURCES)}")
    if not isinstance(record["run_id"], str) or not record["run_id"]:
        errors.append("run_id must be a non-empty string")
    if not isinstance(record["attempt"], int) or isinstance(record["attempt"], bool) or record["attempt"] < 1:
        errors.append("attempt must be an integer >= 1")
    timestamp = parse_timestamp(record["timestamp"])
    if timestamp is None:
        errors.append("timestamp must be ISO8601")
    environment = record["environment"]
    if not isinstance(environment, dict) or not isinstance(environment.get("runner"), str) or not environment["runner"]:
        errors.append("environment.runner must be a non-empty string")
    results = record["results"]
    if not isinstance(results, list) or not results:
        errors.append("results must be a non-empty array")
    else:
        seen = set()
        for index, result in enumerate(results):
            if not isinstance(result, dict):
                errors.append(f"results[{index}] must be an object")
                continue
            context = result.get("context")
            status = result.get("status")
            if not isinstance(context, str) or not context:
                errors.append(f"results[{index}].context must be a non-empty string")
            elif context in seen:
                errors.append(f"duplicate result context: {context}")
            else:
                seen.add(context)
            if status not in STATUSES:
                errors.append(f"results[{index}].status must be one of {sorted(STATUSES)}")
    return errors


def reduce_truth(record, current_head, required_contexts=(), max_age_seconds=3600):
    """Return a deterministic decision object. Invalid records raise ValueError."""
    errors = validate(record)
    if errors:
        raise ValueError("; ".join(errors))
    if not SHA_RE.fullmatch(current_head):
        raise ValueError("current head must be a 40-character lowercase hex SHA")

    now = datetime.now(timezone.utc)
    timestamp = parse_timestamp(record["timestamp"])
    age_seconds = (now - timestamp).total_seconds()
    contexts = {result["context"]: result["status"] for result in record["results"]}
    required = list(required_contexts) if required_contexts else list(contexts)
    if not required:
        return _decision(record, current_head, "INCOMPLETE", ["no required contexts"], age_seconds, contexts, required)
    if len(set(required)) != len(required):
        raise ValueError("required contexts must be unique")

    reasons = []
    decision = "PASS"
    if record["sha"] != current_head:
        decision = "STALE"
        reasons.append(f"record SHA {record['sha'][:12]} != current HEAD {current_head[:12]}")
    elif age_seconds < -60:
        raise ValueError("timestamp is more than 60 seconds in the future")
    elif age_seconds > max_age_seconds:
        decision = "STALE"
        reasons.append(f"record age {int(age_seconds)}s exceeds freshness window {max_age_seconds}s")
    else:
        missing = [context for context in required if context not in contexts]
        if missing:
            decision = "INCOMPLETE"
            reasons.append("missing required contexts: " + ", ".join(missing))
        else:
            required_statuses = {context: contexts[context] for context in required}
            blocked = [context for context, status in required_statuses.items() if status in BLOCKING]
            active = [context for context, status in required_statuses.items() if status in ACTIVE]
            if blocked:
                decision = "BLOCKED"
                reasons.append("blocking contexts: " + ", ".join(f"{c}={required_statuses[c]}" for c in blocked))
            elif active:
                decision = "IN_PROGRESS"
                reasons.append("active contexts: " + ", ".join(f"{c}={required_statuses[c]}" for c in active))
    return _decision(record, current_head, decision, reasons, age_seconds, contexts, required)


def _decision(record, current_head, decision, reasons, age_seconds, contexts, required):
    return {
        "decision": decision,
        "repo": record.get("repo"),
        "record_sha": record.get("sha"),
        "current_head": current_head,
        "source": record.get("source"),
        "run_id": record.get("run_id"),
        "attempt": record.get("attempt"),
        "age_seconds": max(0, int(age_seconds)),
        "required_contexts": required,
        "contexts": contexts,
        "reasons": reasons,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("record", type=Path)
    parser.add_argument("--head", required=True, help="current full commit SHA")
    parser.add_argument("--required-context", action="append", default=[], help="required context; repeat")
    parser.add_argument("--max-age-seconds", type=int, default=3600)
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args(argv)
    try:
        record = json.loads(args.record.read_text(encoding="utf-8"))
        if args.max_age_seconds < 0:
            raise ValueError("max-age-seconds must be >= 0")
        outcome = reduce_truth(record, args.head, args.required_context, args.max_age_seconds)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        outcome = {"decision": "INVALID", "reasons": [str(exc)]}
    if args.as_json:
        print(json.dumps(outcome, indent=2, sort_keys=True))
    else:
        print(f"{outcome['decision']}: " + ("; ".join(outcome.get("reasons", [])) or "all required contexts succeeded"))
    return 0 if outcome["decision"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
