#!/usr/bin/env python3
"""Verify Runner Clean-Room Contract records (contract:runner-clean-room/1.0).

Usage: python scripts/verify_runner_clean_room.py <record.json>

This validator is stdlib-only and checks both shape and boundary semantics:
- test_root is inside checkout_root;
- dependency_root is disjoint from test_root;
- dependency checkouts stay under dependency_root;
- temp_root is outside checkout_root;
- cache namespace contains run_id;
- ports are explicitly isolated;
- clean-before and clean-after are true.
"""
import json
import re
import sys
import posixpath
from pathlib import Path

SHA_RE = re.compile(r"^[a-f0-9]{40}$")
REPO_RE = re.compile(r"^[a-zA-Z0-9_-]+/[a-zA-Z0-9_.-]+$")
REQUIRED = ("repo", "sha", "run_id", "attempt", "checkout_root", "test_root", "dependency_root", "temp_root", "cache_namespace", "dependencies", "ports", "cleanup")
STATUSES = {"always", "retain-evidence-only"}


def norm(path):
    """Normalize logical runner paths without depending on host OS."""
    return posixpath.normpath(str(path).replace("\\", "/"))


def within(child, parent):
    child, parent = norm(child), norm(parent)
    return child == parent or child.startswith(parent.rstrip("/") + "/")


def validate(record):
    errors = []
    if not isinstance(record, dict):
        return ["record must be an object"]
    allowed = set(REQUIRED)
    errors.extend(f"unknown field: {field}" for field in record if field not in allowed)
    errors.extend(f"missing required field: {field}" for field in REQUIRED if field not in record)
    if errors:
        return errors
    if not isinstance(record["repo"], str) or not REPO_RE.fullmatch(record["repo"]):
        errors.append("repo must match org/repo format")
    if not isinstance(record["sha"], str) or not SHA_RE.fullmatch(record["sha"]):
        errors.append("sha must be a 40-character lowercase hex string")
    if not isinstance(record["run_id"], str) or not record["run_id"]:
        errors.append("run_id must be non-empty")
    if not isinstance(record["attempt"], int) or isinstance(record["attempt"], bool) or record["attempt"] < 1:
        errors.append("attempt must be an integer >= 1")
    roots = ["checkout_root", "test_root", "dependency_root", "temp_root"]
    for key in roots:
        if not isinstance(record[key], str) or not record[key]:
            errors.append(f"{key} must be a non-empty path")
    if not errors:
        checkout, tests, deps, temp = (norm(record[key]) for key in roots)
        if not within(tests, checkout):
            errors.append("test_root must be inside checkout_root")
        if within(deps, tests) or within(tests, deps):
            errors.append("dependency_root must be disjoint from test_root")
        if within(temp, checkout):
            errors.append("temp_root must be outside checkout_root")
        if temp in {checkout, tests, deps}:
            errors.append("temp_root must be distinct from checkout/test/dependency roots")
    if not isinstance(record["cache_namespace"], str) or not re.fullmatch(r"[A-Za-z0-9._/-]+", record["cache_namespace"]):
        errors.append("cache_namespace contains invalid characters")
    elif record["run_id"] not in record["cache_namespace"]:
        errors.append("cache_namespace must contain run_id for collision isolation")

    dependencies = record["dependencies"]
    if not isinstance(dependencies, list):
        errors.append("dependencies must be an array")
    else:
        names, paths = set(), set()
        for index, dependency in enumerate(dependencies):
            if not isinstance(dependency, dict):
                errors.append(f"dependencies[{index}] must be an object")
                continue
            for key in ("name", "path", "sha"):
                if key not in dependency:
                    errors.append(f"dependencies[{index}] missing {key}")
            name, path, sha = dependency.get("name"), dependency.get("path"), dependency.get("sha")
            if not isinstance(name, str) or not name:
                errors.append(f"dependencies[{index}].name must be non-empty")
            elif name in names:
                errors.append(f"duplicate dependency name: {name}")
            else:
                names.add(name)
            if not isinstance(path, str) or not path:
                errors.append(f"dependencies[{index}].path must be non-empty")
            else:
                normalized_path = norm(path)
                if normalized_path in paths:
                    errors.append(f"duplicate dependency path: {normalized_path}")
                paths.add(normalized_path)
                if isinstance(record.get("dependency_root"), str) and not within(normalized_path, record["dependency_root"]):
                    errors.append(f"dependency path escapes dependency_root: {path}")
            if not isinstance(sha, str) or not SHA_RE.fullmatch(sha):
                errors.append(f"dependencies[{index}].sha must be a full lowercase commit SHA")

    ports = record["ports"]
    if not isinstance(ports, dict):
        errors.append("ports must be an object")
    else:
        if ports.get("isolated") is not True:
            errors.append("ports.isolated must be true")
        reserved = ports.get("reserved")
        if not isinstance(reserved, list) or any(not isinstance(p, int) or isinstance(p, bool) or not 1 <= p <= 65535 for p in reserved):
            errors.append("ports.reserved must contain valid integer port numbers")
        elif len(set(reserved)) != len(reserved):
            errors.append("ports.reserved must contain unique ports")

    cleanup = record["cleanup"]
    if not isinstance(cleanup, dict):
        errors.append("cleanup must be an object")
    else:
        if cleanup.get("clean_before") is not True:
            errors.append("cleanup.clean_before must be true")
        if cleanup.get("clean_after") is not True:
            errors.append("cleanup.clean_after must be true")
        if cleanup.get("on_failure") not in STATUSES:
            errors.append("cleanup.on_failure must be always or retain-evidence-only")
    return errors


def main(argv=None):
    argv = argv if argv is not None else sys.argv
    if len(argv) != 2:
        print("usage: verify_runner_clean_room.py <record.json>")
        return 2
    try:
        record = json.loads(Path(argv[1]).read_text(encoding="utf-8"))
    except FileNotFoundError:
        print(f"FAIL: record not found: {argv[1]}")
        return 1
    except json.JSONDecodeError as exc:
        print(f"FAIL: invalid JSON: {exc}")
        return 1
    errors = validate(record)
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    print(f"OK: {record['repo']} clean-room run {record['run_id']}#{record['attempt']} with {len(record['dependencies'])} pinned dependencies")
    return 0


if __name__ == "__main__":
    sys.exit(main())
