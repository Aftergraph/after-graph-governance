#!/usr/bin/env python3
"""Aftergraph harness scorecard — measures guide/sensor coverage and evidence freshness.

Answers "did adding repo-level guides change anything?" with numbers computed from local evidence,
never from assertion. Writes AFTERGRAPH_HARNESS_SCORECARD.json + .md into the workspace root and
appends a row to SCORECARD_HISTORY.jsonl so growth/regression is visible over time.

Metrics
  guide_coverage          repos with a repo-level AGENTS.md / repos present locally
  ratchet_rules           recorded failure-derived rules across all guides
  ratchet_growth          rules added since the previous run (declining growth = harness maturing)
  guide_staleness_days    median days since each guide last changed
  sensor_coverage         repos with >=1 executed verification row recorded against an exact SHA
  evidence_freshness      recorded SHA vs live HEAD: current / stale / unrecorded
  not_instrumented        metrics the playbook requires that no local data can produce yet

Usage: harness_scorecard.py [--root DIR] [--write]
"""
from __future__ import annotations
import json, os, re, subprocess, sys, datetime, statistics

ROOT = "/root/workspace/aftergraph"


def sh(args, cwd):
    try:
        return subprocess.run(args, cwd=cwd, capture_output=True, text=True, timeout=60).stdout.strip()
    except Exception:
        return ""


def days_ago(path):
    try:
        return round((datetime.datetime.now().timestamp() - os.path.getmtime(path)) / 86400, 1)
    except Exception:
        return None


def ratchet_rules(text):
    m = re.search(r"^## Ratchet.*?$(.*?)(?=^## |\Z)", text, re.S | re.M)
    if not m:
        return 0
    return len([l for l in m.group(1).splitlines() if re.match(r"^\s*-\s+\S", l)])


def main():
    root = ROOT
    if "--root" in sys.argv:
        root = sys.argv[sys.argv.index("--root") + 1]
    write = "--write" in sys.argv

    inv = json.load(open(os.path.join(root, "REPOSITORY_INVENTORY.json")))["repos"]
    present = [r for r in inv if (r.get("local") or {}).get("present")]

    ci_results_path = os.path.join(root, "CI_RESULTS.json")
    ci = json.load(open(ci_results_path)) if os.path.exists(ci_results_path) else {"results": []}
    recorded = {}
    for row in ci.get("results", []):
        recorded.setdefault(row.get("repo", "").split(":")[0], []).append(row)

    guides, rules, stale_days = [], 0, []
    for r in present:
        name = r["name"]
        gpath = os.path.join(root, name, "AGENTS.md")
        if os.path.exists(gpath):
            text = open(gpath, errors="ignore").read()
            guides.append(name)
            rules += ratchet_rules(text)
            d = days_ago(gpath)
            if d is not None:
                stale_days.append(d)

    sensor_covered, unrecorded, current, stale = [], [], [], []
    for r in present:
        name = r["name"]
        if name in recorded:
            sensor_covered.append(name)
            live = sh(["git", "rev-parse", "HEAD"], os.path.join(root, name))
            shas = {str(row.get("sha", ""))[:7] for row in recorded[name]}
            if live and any(live.startswith(s) or s.startswith(live[:7]) for s in shas):
                current.append(name)
            else:
                stale.append({"repo": name, "recorded": sorted(shas), "live": live[:7] or "unknown"})
        else:
            unrecorded.append(name)

    history_path = os.path.join(root, "SCORECARD_HISTORY.jsonl")
    prev_rules = None
    if os.path.exists(history_path):
        rows = [json.loads(l) for l in open(history_path) if l.strip()]
        if rows:
            prev_rules = rows[-1].get("ratchet_rules")

    # Primary metric, read from the instrument's own artifact so the history row carries the measured
    # values AND the definition that produced them. Without the definition a definition change looks like a
    # movement in the metric.
    dc = None
    dc_path = os.path.join(root, "AGENT_DISCOVERY_COST.json")
    if os.path.exists(dc_path):
        raw = json.load(open(dc_path))
        totals = raw.get("all_repos") or {}
        dc = {"definition_version": raw.get("definition_version"),
              "window_days": raw.get("window_days"),
              "slices": totals.get("slices"),
              "pct_that_verified": totals.get("pct_that_verified"),
              "pct_that_mutated_without_verifying": totals.get("pct_that_mutated_without_verifying"),
              "calls_before_verify_median": totals.get("calls_before_verify_median")}

    scorecard = {
        "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "root": root,
        "repos_in_inventory": len(inv),
        "repos_present_locally": len(present),
        "guide_coverage": {"with_guide": len(guides), "total_present": len(present),
                           "pct": round(100.0 * len(guides) / max(len(present), 1), 1),
                           "without": sorted(set(r["name"] for r in present) - set(guides))},
        "ratchet_rules_total": rules,
        "ratchet_rules_previous": prev_rules,
        "ratchet_growth": (None if prev_rules is None else rules - prev_rules),
        "guide_staleness_days_median": (statistics.median(stale_days) if stale_days else None),
        "sensor_coverage": {
            "with_recorded_executed_verification": len(sensor_covered),
            "total_present": len(present),
            "pct": round(100.0 * len(sensor_covered) / max(len(present), 1), 1),
            "ci_results_scope": ci.get("scope"),
            "ci_results_generated_at": ci.get("generated_at"),
            "no_recorded_sensor": sorted(unrecorded),
        },
        "evidence_freshness": {"current_at_live_head": sorted(current),
                               "stale_vs_live_head": stale},
        "discovery_cost": dc,
        "not_instrumented": {
            "cost_per_verified_result": "no per-task cost accounting in this workspace; trust-gateway BudgetLedger is the candidate source",
            "rework_rate": "requires PR-level attempt history (gh api check runs per head) — not collected locally",
            "escalation_rate": "requires human-intervention count per mission — not collected locally",
            "recovery_time": "requires incident start/end timestamps — not collected locally",
            "completion_rate": "requires started-vs-verified run counts from works-execution — not reduced into evidence yet",
        },
    }

    print(json.dumps(scorecard, indent=2))
    if write:
        json.dump(scorecard, open(os.path.join(root, "AFTERGRAPH_HARNESS_SCORECARD.json"), "w"), indent=2)
        with open(history_path, "a") as f:
            f.write(json.dumps({"generated_at": scorecard["generated_at"],
                                "guide_coverage_pct": scorecard["guide_coverage"]["pct"],
                                "sensor_coverage_pct": scorecard["sensor_coverage"]["pct"],
                                "ratchet_rules": rules,
                                "stale_evidence_count": len(stale),
                                "current_evidence_count": len(current),
                                "discovery_cost": dc}) + "\n")
        md = [f"# Aftergraph Harness Scorecard — {scorecard['generated_at']}", "",
              f"Repos: {len(inv)} in inventory, {len(present)} present locally", "",
              "| metric | value | direction |", "|---|---|---|",
              f"| Guide coverage | {len(guides)}/{len(present)} ({scorecard['guide_coverage']['pct']}%) | up |",
              f"| Ratchet rules recorded | {rules} | up (declining growth is the healthy signal) |",
              f"| Median guide staleness | {scorecard['guide_staleness_days_median']} days | down |",
              f"| Repos with a recorded executed sensor | {len(sensor_covered)}/{len(present)} ({scorecard['sensor_coverage']['pct']}%) | up |",
              f"| Evidence current at live HEAD | {len(current)} | up |",
              f"| Evidence stale vs live HEAD | {len(stale)} | down |", "",
              "## Repos with no recorded computational sensor", ""]
        md += [f"- {n}" for n in sorted(unrecorded)] or ["- none"]
        md += ["", "## Stale evidence (recorded SHA != live HEAD)", ""]
        md += [f"- {s['repo']}: recorded {','.join(s['recorded'])} vs live {s['live']}" for s in stale] or ["- none"]
        md += ["", "## Not instrumented yet", ""] + [f"- {k}: {v}" for k, v in scorecard["not_instrumented"].items()]
        open(os.path.join(root, "AFTERGRAPH_HARNESS_SCORECARD.md"), "w").write("\n".join(md) + "\n")
        print("\nWROTE AFTERGRAPH_HARNESS_SCORECARD.json / .md and appended SCORECARD_HISTORY.jsonl")


if __name__ == "__main__":
    main()
