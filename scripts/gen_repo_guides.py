#!/usr/bin/env python3
"""Generate repo-level AGENTS.md for Aftergraph repositories from verified local evidence.

Evidence sources, in priority order (no invented commands):
  1. CI_RESULTS.json          -> commands actually executed, with status + exact SHA + note
  2. live probe of the repo   -> package.json scripts, Makefile targets, go.mod, pytest files
  3. nothing verified         -> the file states that explicitly instead of inventing a command

Usage: gen_repo_guides.py [--root DIR] [--dry-run] [--force] [--only NAME[,NAME...]]
"""
from __future__ import annotations
import json, os, re, subprocess, sys, datetime

ROOT = os.path.abspath(os.environ.get("AFTERGRAPH_ROOT", "/root/workspace/aftergraph"))
SCOPE = "Aftergraph local repository-native verification"
TODAY = datetime.date.today().isoformat()

ROLE = {
    "after-graph-governance": ("Governance source of truth", "contracts, schemas, terminology"),
    "trust-gateway": ("Trust boundary", "policy, approvals, audit"),
    "works-execution": ("Execution plane", "missions, WorkGraph, workers"),
    "wi-backend": ("Work intelligence", "backend"),
    "wi-frontend": ("Work intelligence", "frontend"),
    "intelligence-systems-research": ("Research", "program"),
    "aie": ("Research", "portable semantics"),
    "afm": ("Research", "foundation models"),
    "llm-research-development": ("Research", "methodology and evals"),
    "brand": ("Brand / public", "identity and design system"),
    "aftergraph.org": ("Brand / public", "public front door"),
    "docs": ("Brand / public", "knowledge plane"),
    "studio": ("Brand / public", "operator and product experience"),
    "runtime": ("Infra", "canonical runtime plane"),
    "model-registry": ("Infra", "model families and artifacts"),
    "skills-vault": ("Infra", "skill library"),
    "continuum": ("Infra", "mission bench for continuity"),
    "context-continuity": ("Infra", "continuity contract"),
    "aftergraph-cron-fabric": ("Infra", "drift monitors and event dedupe"),
    "sentinel": ("Not declared in the workspace contract", "verified code review"),
    "sentinel-firetest": ("Not declared in the workspace contract", "throwaway live-fire proof — delete after use"),
    ".github": ("Not declared in the workspace contract", "organization profile and org-wide workflows"),
    "veranza": ("Not declared in the workspace contract", "not present locally"),
}


def sh(args, cwd):
    try:
        return subprocess.run(args, cwd=cwd, capture_output=True, text=True, timeout=90).stdout
    except Exception:
        return ""


def probe(repo_dir):
    """Local conventions verified to exist on disk right now."""
    out = {"build": None, "test": None, "lint": None, "typecheck": None, "verify": None,
           "notes": [], "languages": []}
    p = lambda f: os.path.exists(os.path.join(repo_dir, f))
    scripts = {}
    if p("package.json"):
        try:
            scripts = json.load(open(os.path.join(repo_dir, "package.json"))).get("scripts") or {}
        except Exception:
            scripts = {}
        out["languages"].append("JavaScript/TypeScript (Node)")
    pm = "pnpm" if p("pnpm-lock.yaml") else ("yarn" if p("yarn.lock") else "npm")
    for key, slot in (("build", "build"), ("test", "test"), ("lint", "lint"),
                      ("typecheck", "typecheck"), ("verify", "verify")):
        if key in scripts:
            out[slot] = f"{pm} run {key}"
    if "check" in scripts and not out["typecheck"]:
        out["typecheck"] = f"{pm} run check"
    if "format:check" in scripts and not out["lint"]:
        out["lint"] = f"{pm} run format:check"

    if p("Makefile"):
        mk = open(os.path.join(repo_dir, "Makefile"), errors="ignore").read()
        targets = sorted(set(re.findall(r"^([A-Za-z0-9_.-]+):", mk, re.M)))
        for t, slot in (("test", "test"), ("lint", "lint"), ("build", "build"), ("verify", "verify")):
            if t in targets and not out[slot]:
                out[slot] = f"make {t}"
        if targets:
            out["notes"].append(f"Makefile targets: {', '.join(targets[:12])}")
    if p("go.mod"):
        out["languages"].append("Go")
        out["build"] = out["build"] or "go build ./..."
        out["test"] = out["test"] or "go test ./..."
        out["lint"] = out["lint"] or "go vet ./..."
    if p("pyproject.toml"):
        out["languages"].append("Python (pyproject.toml)")
    elif p("requirements.txt"):
        out["languages"].append("Python (requirements.txt)")
    if p("Cargo.toml"):
        out["languages"].append("Rust")

    py_tests = [t.strip() for t in sh(["bash", "-lc",
        "find . -maxdepth 3 \\( -path ./node_modules -o -path ./.git -o -path ./dist -o -path ./build "
        "-o -path ./__pycache__ -o -path ./.venv \\) -prune -o -type f -name 'test_*.py' -print "
        "-o -type f -name '*_test.py' -print 2>/dev/null | head -4"], repo_dir).strip().splitlines() if t.strip()]
    if py_tests:
        if "Python" not in " ".join(out["languages"]):
            out["languages"].append("Python (tests present)")
        out["notes"].append(f"pytest files: {', '.join(py_tests)}")

    vsh = [v.strip() for v in sh(["bash", "-lc",
        "ls scripts/*verify*.sh scripts/verify*.py 2>/dev/null | head -3"], repo_dir).strip().splitlines() if v.strip()]
    if vsh and not out["verify"]:
        out["verify"] = ("bash " + vsh[0]) if vsh[0].endswith(".sh") else ("python3 " + vsh[0])
    if vsh:
        out["notes"].append("verifier scripts: " + ", ".join(vsh))
    return out


def extract_ratchet(text):
    """Body of the existing Ratchet section, so regeneration never destroys accumulated rules."""
    m = re.search(r"^## Ratchet[^\n]*$(.*?)(?=^## |\Z)", text or "", re.S | re.M)
    return m.group(1).strip("\n") if m else ""


BOILERPLATE = (
    "Every line below must trace to one observed agent failure in THIS repository.",
    "Add a dated line when an agent fails in a new way; fix the strongest layer that prevents recurrence.",
)


def ratchet_body_clean(text):
    """Drop the fixed instruction lines, keep only accumulated rules."""
    return "\n".join(l for l in (text or "").splitlines()
                      if l.strip() and l.strip() not in BOILERPLATE)


def ratchet_rules(text):
    return [l for l in (text or "").splitlines() if l.strip().startswith("- ")]


def compose(name, inv_row, ci_row, cmds, ci_hits, repo_dir, ci_scope=SCOPE, ci_rows_total=0,
            ci_date="", ratchet_body=None):
    role, role_scope = ROLE.get(name, ("Not declared in the workspace contract", "-"))
    desc = (inv_row.get("description") or "").strip()
    local = inv_row.get("local") or {}
    inv_head, inv_branch = local.get("head") or "unknown", local.get("branch") or "unknown"
    live_head = sh(["git", "rev-parse", "HEAD"], repo_dir).strip() or inv_head
    live_branch = sh(["git", "rev-parse", "--abbrev-ref", "HEAD"], repo_dir).strip() or inv_branch
    head, branch = live_head, live_branch
    drift = "" if live_head.startswith(inv_head[:7]) else (
        f"\n     NOTE: the workspace inventory recorded {inv_branch} at {inv_head}; this file was generated\n"
        f"     from the live checkout ({live_branch} at {live_head}). Re-verify against your SHA.")
    langs = ", ".join(dict.fromkeys(cmds["languages"])) or "no recognised build marker"
    kept = ratchet_body_clean(ratchet_body)
    ratchet = (kept if ratchet_rules(kept) else
               "  (none recorded yet — this guide has not yet accumulated failure-derived rules)")

    if ci_hits:
        width = max(len(str(h["command"])) for h in ci_hits)
        rows = "\n".join(
            f"  {h['command']:<{width}}  {h['status']}  {h['sha'][:8]}  {h['note']}" for h in ci_hits)
        gate = ("## Executed verification (authoritative)\n\n"
                "These commands were executed against the exact SHA shown and their result recorded in\n"
                "`CI_RESULTS.json` (workspace scope). Treat a result from a different SHA as stale.\n\n"
                f"{rows}\n\n"
                "  Re-run the row for your SHA before opening a PR. A green run at another SHA proves nothing\n"
                "  about this one.")
    else:
        gate = ("## Executed verification (authoritative)\n\n"
                "  No executed verification command is recorded for this repository in `CI_RESULTS.json`\n"
                f"  (scope: {ci_scope}, {ci_rows_total} rows{", " + ci_date if ci_date else ""}).\n"
                "  This repository therefore has no recorded computational sensor.\n"
                "  Before relying on it unattended, add one and record the executed command here with a date.\n"
                "  Do not invent a build or test command for this repository.")

    def line(label, cmd):
        return f"  {label:<10} {cmd if cmd else '— not detected in this repository'}"

    cmd_block = "\n".join([line("BUILD:", cmds["build"]), line("TEST:", cmds["test"]),
                           line("LINT:", cmds["lint"]), line("TYPECHECK:", cmds["typecheck"]),
                           line("VERIFY:", cmds["verify"])])
    notes = "\n".join(f"  - {n}" for n in cmds["notes"]) or "  - none"

    caveat = ""
    if any("Python" in l for l in cmds["languages"]):
        caveat = ("\n  Python note: interpreter and pytest availability are environment-dependent. `pytest` is not\n"
                  "  importable from `/usr/bin/python3` in this workspace as of " + TODAY + "; run under the\n"
                  "  repository's own Python environment. Record the exact interpreter prefix here once known\n"
                  "  (for example `aie` requires `PYTHONPATH=src python3 -m pytest -q`).\n")

    if name == "sentinel-firetest":
        caveat += ("\n  This repository is designated throwaway (\"delete after\" per its description).\n"
                   "  Do not add durable rules here; ask before immortalising anything from it.\n")

    return f"""# {name} — Agent Execution Contract

<!-- Generated {TODAY} from REPOSITORY_INVENTORY.json, CI_COMMAND_INVENTORY.json, CI_RESULTS.json and a
     live probe of branch {branch} at HEAD {head}. Revision 1.{drift}
     Regenerate the command blocks; hand-edit only the Ratchet section. -->

## Project

  Name        {name}
  Role        {role} — {role_scope}
  Purpose     {desc or 'no description recorded'}
  Languages   {langs}

## Local conventions (verified present on disk)

{cmd_block}
{caveat}
  Probes
{notes}

Precedence: this file beats the conversation; `/root/workspace/aftergraph/AGENTS.md` beats this file;
verified external state beats both.

{gate}

## Rules (inherited from the Aftergraph workspace contract)

  - Never commit secrets, tokens, or credentials. Never copy runtime secrets into fixtures, docs, or frontend code.
  - Conventional commits: `feat|fix|docs|refactor|test|chore(scope): description`. Sign off with a verified identity.
  - Run the repository's verification row for your SHA before opening a PR.
  - Evidence-bound: gate results tied to the exact SHA. Evidence from an older SHA is stale, not evidence.
  - Keep PRs narrow and reviewable. Preserve unrelated work. Update an existing PR rather than duplicating it.
  - Check `after-graph-governance/docs/contracts/` for relevant schemas before changing an interface.
  - Verify trust-gateway policy before touching approvals, auth, or budgets.
  - Prefer the smallest reuse-first change. Keep provider boundaries explicit and fail closed.
  - Risk surfaces (authority, permissions, audit, budgets, identity, secrets) require independent verification,
    not self-verification by the implementing agent.
  - Local green output does not prove production readiness. Do not claim completion from it.

## Ratchet — rules learned from observed failures

Every line below must trace to one observed agent failure in THIS repository.
Add a dated line when an agent fails in a new way; fix the strongest layer that prevents recurrence.

{ratchet}

Choose the strongest applicable layer:
  memory note  <  prompt instruction  <  guide rule  <  sensor (test/lint/schema)  <  environment constraint (permission, CI gate)

If a rule can be checked without human judgement, it does not belong in this list — it belongs in a sensor.

## Guide hygiene

  - Review monthly. Remove rules now enforced by automation. Consolidate rules addressing the same failure class.
  - When the same review comment appears three times, promote it to a gate that blocks the output.
  - Date every entry so stale guidance is identifiable.
  - A rule nobody can verify without subjective judgement is not a rule; rewrite or delete it.
"""


def main():
    global ROOT
    if "--root" in sys.argv:
        ROOT = os.path.abspath(sys.argv[sys.argv.index("--root") + 1])
    dry = "--dry-run" in sys.argv
    only = None
    if "--only" in sys.argv:
        only = set(sys.argv[sys.argv.index("--only") + 1].split(","))
    inv = {r["name"]: r for r in json.load(open(os.path.join(ROOT, "REPOSITORY_INVENTORY.json")))["repos"]}
    ci = {r["name"]: r for r in json.load(open(os.path.join(ROOT, "CI_COMMAND_INVENTORY.json")))["repos"]}
    ci_res = {}
    ci_doc = json.load(open(os.path.join(ROOT, "CI_RESULTS.json")))
    ci_scope = ci_doc.get("scope") or SCOPE
    ci_total = len(ci_doc.get("results", []))
    ci_date = (ci_doc.get("generated_at") or "")[:10]
    for row in ci_doc.get("results", []):
        base = row.get("repo", "").split(":")[0]
        ci_res.setdefault(base, []).append(row)

    results = []
    for name, inv_row in sorted(inv.items()):
        if only and name not in only:
            continue
        local = inv_row.get("local") or {}
        repo_dir = os.path.join(ROOT, name)
        if not local.get("present"):
            print(f"SKIP    {name}: not present locally")
            results.append({"repo": name, "action": "skipped", "reason": "not present locally"})
            continue
        guide = os.path.join(repo_dir, "AGENTS.md")
        force = "--force" in sys.argv
        existing = open(guide, errors="ignore").read() if os.path.exists(guide) else ""
        if os.path.exists(guide):
            existing = open(guide, errors="ignore").read()
            regenerable = "<!-- Generated " in existing and "hand-edit only the Ratchet section" in existing
            if not (force and regenerable):
                why = ("AGENTS.md already exists (not generator-owned)" if not regenerable
                       else "AGENTS.md already exists; pass --force to regenerate")
                print(f"SKIP    {name}: {why}")
                results.append({"repo": name, "action": "skipped", "reason": why})
                continue
            print(f"REGEN   {name}: generator-owned guide, overwriting")
        prior_ratchet = extract_ratchet(existing) if (os.path.exists(guide) and force) else None
        cmds = probe(repo_dir)
        hits = ci_res.get(name, [])
        content = compose(name, inv_row, ci.get(name, {}), cmds, hits, repo_dir,
                         ci_scope=ci_scope, ci_rows_total=ci_total, ci_date=ci_date,
                         ratchet_body=prior_ratchet)
        print(f"{'PLAN' if dry else 'WRITE'}    {name:<32} executed_rows={len(hits)} "
              f"local_cmds={sum(1 for k in ('build','test','lint','typecheck','verify') if cmds[k])}")
        if not dry:
            with open(os.path.join(repo_dir, "AGENTS.md"), "w") as f:
                f.write(content)
        lh = sh(["git", "rev-parse", "HEAD"], repo_dir).strip() or (local.get("head") or "unknown")
        lb = sh(["git", "rev-parse", "--abbrev-ref", "HEAD"], repo_dir).strip() or (local.get("branch") or "unknown")
        results.append({"repo": name, "action": "dry-run" if dry else "written",
                        "branch_live": lb, "head_live": lh, "head_inventory": (local.get("head") or "unknown"),
                        "preexisting_dirty": bool(local.get("dirty")),
                        "executed_verification_rows": len(hits),
                        "local_commands_detected": {k: cmds[k] for k in
                                                    ("build", "test", "lint", "typecheck", "verify") if cmds[k]},
                        "languages": cmds["languages"],
                        "ratchet_rules_preserved": len(ratchet_rules(prior_ratchet))})
    if not dry:
        out = os.path.join(ROOT, "GUIDE_GENERATION_EVIDENCE.json")
        json.dump({"generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                   "generator": "/root/aftergraph-guide-generation/gen_repo_guides.py",
                   "workspace_root": ROOT,
                   "ci_results_source_scope": json.load(open(os.path.join(ROOT, "CI_RESULTS.json"))).get("scope"),
                   "results": results}, open(out, "w"), indent=2)
        print(f"\nWROTE {out} rows={len(results)}")
    print(f"written={sum(1 for r in results if r['action']=='written')} "
          f"skipped={sum(1 for r in results if r['action']=='skipped')} "
          f"planned={sum(1 for r in results if r['action']=='dry-run')}")


if __name__ == "__main__":
    main()
