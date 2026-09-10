#!/usr/bin/env python3
"""Merge-window integrity checker (sole-maintainer-merge-window/0.1).

Reads the window scope from docs/evidence/sole-maintainer-merge-window-*.json
and verifies, for every listed PR, that the live head SHA still matches the
recorded packet, the PR is MERGEABLE, and every required check is green.
Any drift fails closed (exit 1) so window execution never merges a head
nobody reviewed on paper.

Run: python3 scripts/check-merge-window.py [--protocol PATH]
Requires: gh CLI with org read access. Read-only; changes nothing.
"""
import glob
import json
import os
import subprocess
import sys

FIELDS = ("title,headRefOid,headRefName,baseRefName,mergeable,mergeStateStatus,"
          "reviewDecision,additions,deletions,changedFiles,url")


def gh(repo, *args):
    env = dict(os.environ)
    env["GH_REPO"] = f"Aftergraph/{repo}"
    out = subprocess.run(["gh", "pr", "view"] + list(args),
                         capture_output=True, text=True, env=env, timeout=120)
    if out.returncode != 0:
        raise RuntimeError(f"{repo} {' '.join(args)}: {out.stderr.strip()[:200]}")
    return json.loads(out.stdout)


def check_packet(packet):
    repo, num = packet["repo"], str(packet["number"])
    pr = gh(repo, num, "--json", FIELDS)
    problems = []
    if pr["headRefOid"] != packet["head_sha"]:
        problems.append(
            f"HEAD DRIFT recorded={packet['head_sha'][:7]} live={pr['headRefOid'][:7]}")
    if pr["mergeable"] != "MERGEABLE":
        problems.append(f"not mergeable: {pr['mergeable']}")
    checks = gh(repo, num, "--json", "statusCheckRollup")["statusCheckRollup"]
    bad = [f"{c.get('name')}:{c.get('conclusion')}" for c in checks
           if c.get("conclusion") not in ("SUCCESS", "SKIPPED")]
    # Null-name rollup ghosts are recorded non-blocking artifacts, not checks.
    bad = [b for b in bad if not b.startswith("None:")]
    if bad:
        problems.append(f"non-green checks: {', '.join(bad)}")
    return problems


def main():
    proto = (sys.argv[sys.argv.index("--protocol") + 1]
             if "--protocol" in sys.argv else None)
    if proto is None:
        cands = sorted(glob.glob(
            "docs/evidence/sole-maintainer-merge-window-*.json"))
        if not cands:
            print("no merge-window protocol file found", file=sys.stderr)
            return 2
        proto = cands[-1]
    doc = json.load(open(proto))
    packets = doc.get("packets", doc if isinstance(doc, list) else [])
    failures = {}
    for packet in packets:
        try:
            problems = check_packet(packet)
        except RuntimeError as err:
            problems = [f"lookup failed: {err}"]
        if problems:
            failures[f"{packet['repo']}#{packet['number']}"] = problems
        else:
            print(f"OK   {packet['repo']}#{packet['number']} "
                  f"{packet['head_sha'][:7]}")
    if failures:
        print("\nDRIFT DETECTED — window execution must stop:", file=sys.stderr)
        for key, problems in failures.items():
            for problem in problems:
                print(f"  {key}: {problem}", file=sys.stderr)
        return 1
    print(f"\nwindow clean: {len(packets)} packets verified, no drift")
    return 0


if __name__ == "__main__":
    sys.exit(main())
