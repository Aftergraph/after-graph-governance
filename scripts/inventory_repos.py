#!/usr/bin/env python3
"""Produce the three workspace inventories gen_repo_guides.py consumes.

Outputs (written into --root):
  REPOSITORY_INVENTORY.json  -> one row per topology repo, with live git head/branch/dirty
  CI_COMMAND_INVENTORY.json -> one row per present repo (command discovery is the generator's job)
  CI_RESULTS.json           -> honest empty record when no executed-verification feed is wired

The repository list, role and description come from docs/platform-topology/2.0.json,
the canonical source of truth, so the generator's hardcoded ROLE dict and this producer
can never drift apart on which repositories exist.

Usage: inventory_repos.py --root DIR [--topology PATH] [--ci-results PATH]
"""
from __future__ import annotations
import argparse, datetime, json, os, subprocess, sys

DEFAULT_TOPOLOGY = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "docs", "platform-topology", "2.0.json")


def sh(args, cwd):
    try:
        return subprocess.run(args, cwd=cwd, capture_output=True, text=True, timeout=30).stdout.strip()
    except Exception:
        return ""


def probe_local(name, root):
    repo_dir = os.path.join(root, name)
    if not os.path.isdir(repo_dir):
        return {"present": False}
    head = sh(["git", "rev-parse", "HEAD"], repo_dir) or "unknown"
    branch = sh(["git", "rev-parse", "--abbrev-ref", "HEAD"], repo_dir) or "unknown"
    dirty = bool(sh(["git", "status", "--porcelain"], repo_dir))
    return {"present": True, "head": head, "branch": branch, "dirty": dirty}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True, help="workspace root (repos as siblings)")
    ap.add_argument("--topology", default=DEFAULT_TOPOLOGY, help="platform-topology/2.0.json path")
    ap.add_argument("--ci-results", help="optional CI_RESULTS.json to copy through verbatim")
    args = ap.parse_args()

    root = os.path.abspath(args.root)
    topo = json.load(open(args.topology))
    repos = topo["repositories"]

    inv = {"repos": []}
    ci_cmd = {"repos": []}
    for r in sorted(repos, key=lambda x: x["name"]):
        name = r["name"]
        local = probe_local(name, root)
        inv["repos"].append({
            "name": name,
            "description": r.get("owns") or r.get("role") or "",
            "local": local,
        })
        if local.get("present"):
            ci_cmd["repos"].append({"name": name})

    existing_ci = os.path.join(root, "CI_RESULTS.json")
    if args.ci_results and os.path.exists(args.ci_results):
        ci_doc = json.load(open(args.ci_results))
    elif os.path.exists(existing_ci):
        ci_doc = json.load(open(existing_ci))
    else:
        ci_doc = {
            "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "scope": "Aftergraph local repository-native verification (no executed-verification feed wired)",
            "results": [],
        }

    with open(os.path.join(root, "REPOSITORY_INVENTORY.json"), "w") as f:
        json.dump(inv, f, indent=2)
    with open(os.path.join(root, "CI_COMMAND_INVENTORY.json"), "w") as f:
        json.dump(ci_cmd, f, indent=2)
    with open(os.path.join(root, "CI_RESULTS.json"), "w") as f:
        json.dump(ci_doc, f, indent=2)

    present = sum(1 for r in inv["repos"] if r["local"].get("present"))
    print(f"WROTE 3 inventories into {root}: {len(inv['repos'])} repos, {present} present locally, "
          f"{len(ci_doc.get('results', []))} CI result rows")


if __name__ == "__main__":
    main()
