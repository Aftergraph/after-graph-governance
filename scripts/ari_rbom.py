#!/usr/bin/env python3
"""Release Bill of Materials (RBOM) v0 for Aftergraph Release Intelligence."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.ari_model import canonical_digest, load_json  # noqa: E402
from scripts.ari_registry import Registry, RegistryError  # noqa: E402

SELECTOR_RE = re.compile(r"^([a-z0-9][a-z0-9-]*)@([^#]+)#([a-f0-9]{40})$")


class RbomError(ValueError):
    """Raised when an exact RBOM composition cannot be constructed."""


def parse_selector(selector: str) -> tuple[str, str, str]:
    if not isinstance(selector, str):
        raise RbomError("component selector must be a string")
    match = SELECTOR_RE.fullmatch(selector)
    if not match:
        raise RbomError(
            "component selector must match component@version#40hexcommit: " + selector
        )
    return match.group(1), match.group(2), match.group(3)


def _passport_key(document: dict) -> tuple[str, str, str]:
    return (
        document["subject"]["component"],
        document["subject"]["version"],
        document["provenance"]["commit"],
    )


def _matching_passports(registry: Registry, manifest: dict) -> list[dict]:
    key = (
        manifest["identity"]["component"],
        manifest["release"]["version"],
        manifest["provenance"]["commit"],
    )
    manifest_digest = canonical_digest(manifest)
    return sorted(
        [
            passport
            for passport in registry.passports()
            if _passport_key(passport) == key
            and passport["provenance"]["manifest_digest"] == manifest_digest
        ],
        key=canonical_digest,
    )


def build_rbom(registry: Registry, selectors: Iterable[str]) -> dict:
    selector_list = list(selectors)
    if not selector_list:
        raise RbomError("RBOM requires at least one exact component selector")
    if len(set(selector_list)) != len(selector_list):
        raise RbomError("duplicate component selector")

    manifests: list[dict] = []
    for selector in selector_list:
        component, version, commit = parse_selector(selector)
        try:
            manifest = registry.component(component, version, commit)
        except RegistryError as exc:
            raise RbomError(str(exc)) from exc
        manifests.append(manifest)

    generations = {manifest["platform"]["generation"] for manifest in manifests}
    trains = {manifest["platform"]["release_train"] for manifest in manifests}
    apc_levels = {manifest["compatibility"]["level"] for manifest in manifests}
    if len(generations) != 1:
        raise RbomError(f"mixed platform generation: {sorted(generations)}")
    if len(trains) != 1:
        raise RbomError(f"mixed platform release_train: {sorted(trains)}")
    if len(apc_levels) != 1:
        raise RbomError(f"mixed platform compatibility level: {sorted(apc_levels)}")

    rows: list[dict] = []
    passport_count = 0
    contract_versions: dict[str, set[str]] = {}

    for manifest in manifests:
        manifest_digest = canonical_digest(manifest)
        row = {
            "component": manifest["identity"]["component"],
            "version": manifest["release"]["version"],
            "repository": manifest["provenance"]["repository"],
            "commit": manifest["provenance"]["commit"],
            "manifest_digest": manifest_digest,
        }

        matching = _matching_passports(registry, manifest)
        if len(matching) > 1:
            artifact_digests = {passport["provenance"]["artifact_digest"] for passport in matching}
            if len(artifact_digests) > 1:
                label = f"{row['component']}@{row['version']}#{row['commit'][:12]}"
                raise RbomError(f"multiple matching passports with different artifacts: {label}")
        if matching:
            chosen = matching[0]
            row["artifact_digest"] = chosen["provenance"]["artifact_digest"]
            row["passport_digest"] = canonical_digest(chosen)
            passport_count += 1

        rows.append(row)
        for name, version in manifest["contracts"].items():
            contract_versions.setdefault(name, set()).add(version)

    rows.sort(key=lambda row: (row["component"], row["version"], row["commit"]))
    contracts = [
        {"name": name, "versions": sorted(versions)}
        for name, versions in sorted(contract_versions.items())
    ]

    component_count = len(rows)
    if passport_count == component_count:
        verification_state = "VERIFIED"
    elif passport_count:
        verification_state = "PARTIAL"
    else:
        verification_state = "UNVERIFIED"

    return {
        "schema": "rbom/0.1",
        "platform": {
            "generation": next(iter(generations)),
            "release_train": next(iter(trains)),
            "compatibility": next(iter(apc_levels)),
        },
        "components": rows,
        "contracts": contracts,
        "verification": {
            "state": verification_state,
            "passport_count": passport_count,
            "component_count": component_count,
        },
        "registry_digest": registry.digest,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build an exact Aftergraph RBOM")
    subparsers = parser.add_subparsers(dest="command", required=True)
    build = subparsers.add_parser("build", help="build RBOM v0 from a validated release registry")
    build.add_argument("registry", type=Path)
    build.add_argument("--component", action="append", required=True, dest="components")
    build.add_argument("--format", choices=("json", "pretty"), default="json")
    args = parser.parse_args(argv)

    try:
        registry = Registry(load_json(args.registry))
        rbom = build_rbom(registry, args.components)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(json.dumps({"schema": "rbom-error/1", "state": "FAIL", "error": str(exc)}, sort_keys=True))
        return 2

    if args.format == "pretty":
        print(json.dumps(rbom, indent=2, sort_keys=True))
    else:
        print(json.dumps(rbom, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
