#!/usr/bin/env python3
"""Produce exact-head contract realization observations from GitHub.

Network failures are represented as observation errors. They are never treated
as successful realization. The evaluator decides whether that becomes UNKNOWN
or BLOCK.
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REGISTRY = ROOT / "docs/contracts/platform-convergence-v2-1/registry.json"


def repo_name(owner: str) -> str:
    return f"Aftergraph/{owner}"


def parse_ref_overrides(values: list[str]) -> dict[str, str]:
    out: dict[str, str] = {}
    for value in values:
        if "=" not in value:
            raise ValueError(f"invalid --ref {value!r}; expected owner=ref")
        owner, ref = value.split("=", 1)
        if not owner or not ref:
            raise ValueError(f"invalid --ref {value!r}; expected owner=ref")
        out[owner] = ref
    return out


def ref_for(owner: str, overrides: dict[str, str]) -> str:
    return overrides.get(owner, "main")


def _headers() -> dict[str, str]:
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "aftergraph-contract-realization/0.1"}
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def _get_json(url: str) -> dict[str, Any]:
    req = urllib.request.Request(url, headers=_headers())
    with urllib.request.urlopen(req, timeout=20) as response:
        data = json.load(response)
    if not isinstance(data, dict):
        raise ValueError(f"unexpected GitHub response for {url}")
    return data


def observe_family(family: dict[str, Any], ref: str) -> dict[str, Any]:
    contract = family["contract"]
    owner = family["owner"]
    path = family["path"]
    repo = repo_name(owner)
    encoded_ref = urllib.parse.quote(ref, safe="")
    branch_url = f"https://api.github.com/repos/{repo}/commits/{encoded_ref}"
    try:
        commit = _get_json(branch_url)
        head_sha = commit.get("sha")
        if not isinstance(head_sha, str) or len(head_sha) != 40:
            raise ValueError("GitHub commit response did not contain exact SHA")
    except Exception as exc:  # network/auth/shape -> UNKNOWN in evaluator
        return {"contract": contract, "owner": owner, "path": path, "ref": ref, "present": None, "error": str(exc)}

    encoded_path = "/".join(urllib.parse.quote(part, safe="") for part in path.split("/"))
    content_url = f"https://api.github.com/repos/{repo}/contents/{encoded_path}?ref={head_sha}"
    try:
        content = _get_json(content_url)
        return {
            "contract": contract,
            "owner": owner,
            "path": path,
            "ref": ref,
            "head_sha": head_sha,
            "present": True,
            "content_sha": content.get("sha"),
            "evidence_ref": content.get("html_url") or content_url,
        }
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return {"contract": contract, "owner": owner, "path": path, "ref": ref, "head_sha": head_sha, "present": False, "evidence_ref": content_url}
        return {"contract": contract, "owner": owner, "path": path, "ref": ref, "head_sha": head_sha, "present": None, "error": f"HTTP {exc.code}: {exc.reason}"}
    except Exception as exc:
        return {"contract": contract, "owner": owner, "path": path, "ref": ref, "head_sha": head_sha, "present": None, "error": str(exc)}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    parser.add_argument("--ref", action="append", default=[], help="owner=git-ref override")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    registry = json.loads(args.registry.read_text(encoding="utf-8"))
    refs = parse_ref_overrides(args.ref)
    observations = [observe_family(dict(f), ref_for(f["owner"], refs)) for f in registry.get("families", [])]
    result = {"schema": "contract-realization-observation/0.1", "observations": observations}
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
