#!/usr/bin/env python3
"""Read-only GitHub Scout for R.O.R.O. source reality."""
from __future__ import annotations

import base64
import json
import re
import subprocess
import tomllib
from datetime import datetime, timezone
from typing import Any

MANIFEST_BASENAMES = {"package.json", "pyproject.toml", "Cargo.toml", "go.mod"}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _dependency_union(obj: dict[str, Any]) -> dict[str, Any]:
    merged: dict[str, Any] = {}
    for key in ("dependencies", "devDependencies", "peerDependencies", "optionalDependencies"):
        value = obj.get(key)
        if isinstance(value, dict):
            merged.update(value)
    return merged


def parse_manifest(path: str, raw: bytes) -> dict[str, Any]:
    name = path.rsplit("/", 1)[-1]
    if name == "package.json":
        obj = json.loads(raw.decode("utf-8"))
        return {"name": obj.get("name", ""), "description": obj.get("description", ""), "dependencies": _dependency_union(obj)}
    if name in {"pyproject.toml", "Cargo.toml"}:
        obj = tomllib.loads(raw.decode("utf-8"))
        section = obj.get("project") if name == "pyproject.toml" else obj.get("package")
        section = section if isinstance(section, dict) else {}
        deps = section.get("dependencies", {}) if name == "Cargo.toml" else obj.get("project", {}).get("dependencies", [])
        normalized: dict[str, Any] = {}
        if isinstance(deps, dict):
            normalized = dict(deps)
        elif isinstance(deps, list):
            for dep in deps:
                if isinstance(dep, str) and dep.strip():
                    normalized[re.split(r"[ <>=!~]", dep.strip(), 1)[0]] = dep
        return {"name": section.get("name", ""), "description": section.get("description", ""), "dependencies": normalized}
    if name == "go.mod":
        text = raw.decode("utf-8")
        match = re.search(r"(?m)^module\s+(\S+)", text)
        return {"name": match.group(1) if match else "", "description": "", "dependencies": {}}
    raise ValueError(f"unsupported manifest: {path}")


def _gh_json(args: list[str]) -> Any:
    proc = subprocess.run(["gh", "api", *args], check=False, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"gh api failed: {' '.join(args)}: {proc.stderr.strip()}")
    return json.loads(proc.stdout)


def _gh_bytes(repo: str, path: str, ref: str) -> bytes:
    payload = _gh_json([f"repos/{repo}/contents/{path}", "-f", f"ref={ref}", "-X", "GET"])
    encoded = str(payload.get("content", "")).replace("\n", "")
    if payload.get("encoding") != "base64":
        raise RuntimeError(f"unexpected GitHub content encoding for {repo}/{path}")
    return base64.b64decode(encoded)
def _discover_repo(repo_meta: dict[str, Any]) -> dict[str, Any]:
    full_name = repo_meta["full_name"]
    branch = repo_meta["default_branch"]
    commit = _gh_json([f"repos/{full_name}/commits/{branch}"])
    head_sha = commit["sha"]
    tree = _gh_json([f"repos/{full_name}/git/trees/{head_sha}?recursive=1"])
    manifest_paths = sorted(
        item["path"] for item in tree.get("tree", [])
        if item.get("type") == "blob" and item.get("path", "").rsplit("/", 1)[-1] in MANIFEST_BASENAMES
    )
    manifests: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []
    for path in manifest_paths:
        try:
            raw = _gh_bytes(full_name, path, head_sha)
            manifests.append({"path": path, "manifest_type": path.rsplit("/", 1)[-1], "content": parse_manifest(path, raw)})
        except Exception as exc:  # preserve discovery gap; do not fake an empty manifest
            errors.append({"path": path, "error": str(exc)})
    return {
        "full_name": full_name,
        "default_branch": branch,
        "head_sha": head_sha,
        "visibility": "private" if repo_meta.get("private") else "public",
        "archived": bool(repo_meta.get("archived")),
        "html_url": repo_meta.get("html_url"),
        "manifests": manifests,
        "manifest_errors": errors,
    }


def discover_github_org(org: str = "Aftergraph") -> tuple[list[dict[str, Any]], str]:
    observed_at = utc_now()
    repos = _gh_json([f"orgs/{org}/repos", "-X", "GET", "-f", "per_page=100", "-f", "type=all"])
    active = [repo for repo in repos if not repo.get("archived")]
    active.sort(key=lambda item: item["full_name"].lower())
    discovered = [_discover_repo(repo) for repo in active]
    return discovered, observed_at
