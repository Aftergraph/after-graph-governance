#!/usr/bin/env python3
"""Convert `gh run view --json` output to Canonical CI Result (contract:ci-result/1.0).

Usage:
  gh run view <id> -R <org/repo> --json databaseId,headSha,conclusion,status,jobs,workflowName,url,createdAt \
    | python scripts/ci_result_from_gh.py --repo <org/repo> --source <src> [--attempt N] [--runner ...] [--python ...]

Status mapping (gh -> canonical): success->success, failure->failure,
cancelled->cancelled, timed_out->timeout, skipped/neutral->cancelled
(recorded, never silently dropped), in_progress/queued/waiting/pending/
requested->running|queued by run status. A still-running gh run yields a
non-terminal canonical status so exact-head-truth freshness treats it as
intermediate, never as PASS.

Stdlib only. Reads JSON from stdin or a file argument.
"""
import json
import sys
from datetime import datetime, timezone

STATUSES = {"success", "failure", "cancelled", "timeout", "queued", "running"}

# ponytail: explicit table beats clever inference; skipped/neutral map to
# cancelled (did not run to verdict) so no gh outcome is silently dropped.
CONCLUSION_MAP = {
    "success": "success",
    "failure": "failure",
    "cancelled": "cancelled",
    "timed_out": "timeout",
    "skipped": "cancelled",
    "neutral": "cancelled",
    "stale": "cancelled",
    "action_required": "failure",
}


def canonical_job_status(job, run_status):
    concl = (job.get("conclusion") or "").lower()
    jst = (job.get("status") or "").lower()
    if concl in CONCLUSION_MAP:
        return CONCLUSION_MAP[concl]
    if jst in ("in_progress",):
        return "running"
    if jst in ("queued", "waiting", "pending", "requested"):
        return "queued"
    if (run_status or "").lower() == "completed":
        return "failure"  # completed run, job with no verdict -> treat as failure, never PASS
    return "running"


def convert(gh, repo, source, attempt=1, runner="", versions=None):
    if source not in ("github-actions", "self-hosted", "works-control-plane", "manual", "agent"):
        raise ValueError(f"unknown source: {source!r}")
    sha = gh.get("headSha", "")
    jobs = gh.get("jobs") or []
    run_status = gh.get("status") or ""
    results = []
    for j in jobs:
        entry = {"context": j.get("name", "unknown"),
                 "status": canonical_job_status(j, run_status)}
        url = j.get("url")
        if url:
            entry["details_url"] = url
        results.append(entry)
    if not results:  # workflow-level verdict only (no jobs listed)
        concl = (gh.get("conclusion") or "").lower()
        top = CONCLUSION_MAP.get(concl, "running" if run_status.lower() != "completed" else "failure")
        entry = {"context": gh.get("workflowName", "workflow")}
        entry["status"] = top
        if gh.get("url"):
            entry["details_url"] = gh["url"]
        results.append(entry)
    env = {"runner": runner or "github-actions"}
    if versions:
        env["versions"] = versions
    return {
        "repo": repo,
        "sha": sha,
        "source": source,
        "run_id": str(gh.get("databaseId", "")),
        "attempt": attempt,
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "environment": env,
        "results": results,
    }


def main(argv):
    repo = source = None
    attempt = 1
    runner = ""
    versions = {}
    infile = None
    i = 1
    while i < len(argv):
        if argv[i] == "--repo" and i + 1 < len(argv):
            repo = argv[i + 1]; i += 2
        elif argv[i] == "--source" and i + 1 < len(argv):
            source = argv[i + 1]; i += 2
        elif argv[i] == "--attempt" and i + 1 < len(argv):
            attempt = int(argv[i + 1]); i += 2
        elif argv[i] == "--runner" and i + 1 < len(argv):
            runner = argv[i + 1]; i += 2
        elif argv[i] == "--python" and i + 1 < len(argv):
            versions["python"] = argv[i + 1]; i += 2
        elif argv[i] in ("-h", "--help"):
            print("usage: ci_result_from_gh.py --repo <org/repo> --source <src> [opts] [file.json] < gh.json")
            return 0
        elif argv[i].startswith("-"):
            print(f"FAIL: unknown argument {argv[i]!r}", file=sys.stderr)
            return 1
        else:
            infile = argv[i]; i += 1
    if not repo or not source:
        print("FAIL: --repo and --source are required", file=sys.stderr)
        return 1
    try:
        raw = open(infile, encoding="utf-8").read() if infile else sys.stdin.read()
        gh = json.loads(raw)
    except (OSError, json.JSONDecodeError) as e:
        print(f"FAIL: cannot read gh JSON: {e}", file=sys.stderr)
        return 1
    try:
        out = convert(gh, repo, source, attempt, runner, versions or None)
    except ValueError as e:
        print(f"FAIL: {e}", file=sys.stderr)
        return 1
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
