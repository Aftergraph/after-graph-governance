#!/usr/bin/env python3
"""Deterministic derived Release Registry for Aftergraph Release Intelligence."""

from __future__ import annotations

import argparse
import copy
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.ari_model import (  # noqa: E402
    canonical_digest,
    load_json,
    validate_component,
    validate_edge,
    validate_passport,
)


class RegistryError(ValueError):
    """Raised when registry input or stored registry state is invalid."""


class RegistryConflict(RegistryError):
    """Raised when two documents claim the same exact identity with divergent content."""


@dataclass(frozen=True, slots=True)
class ClassifiedDocument:
    kind: str
    document: dict
    digest: str


def _classify(document: dict) -> ClassifiedDocument:
    snapshot = copy.deepcopy(document)
    schema = snapshot.get("schema") if isinstance(snapshot, dict) else None
    if schema == "aftergraph-component/1.0":
        kind, errors = "component", validate_component(snapshot)
    elif schema == "compatibility-edge/1.0":
        kind, errors = "edge", validate_edge(snapshot)
    elif schema == "release-passport/1.0":
        kind, errors = "passport", validate_passport(snapshot)
    else:
        raise RegistryError(f"unsupported registry document schema: {schema}")
    if errors:
        raise RegistryError("; ".join(errors))
    return ClassifiedDocument(kind, snapshot, canonical_digest(snapshot))


def _component_key(document: dict) -> tuple[str, str, str]:
    return (
        document["identity"]["component"],
        document["release"]["version"],
        document["provenance"]["commit"],
    )


def _passport_key(document: dict) -> tuple[str, str, str]:
    return (
        document["subject"]["component"],
        document["subject"]["version"],
        document["provenance"]["commit"],
    )


def _identity_label(key: tuple[str, str, str]) -> str:
    component, version, commit = key
    return f"{component}@{version}#{commit[:12]}"


def _sort_key(item: ClassifiedDocument) -> tuple:
    document = item.document
    if item.kind == "component":
        return ("component", *_component_key(document), item.digest)
    if item.kind == "edge":
        left = document["from"]
        right = document["to"]
        return (
            "edge",
            left["component"], left["version"], left["commit"],
            right["component"], right["version"], right["commit"],
            document["relation"], document["state"], document["evidence_level"], item.digest,
        )
    return ("passport", *_passport_key(document), item.digest)


def _check_conflicts(items: list[ClassifiedDocument]) -> None:
    components: dict[tuple[str, str, str], ClassifiedDocument] = {}
    passports: list[ClassifiedDocument] = []

    for item in items:
        if item.kind == "component":
            key = _component_key(item.document)
            previous = components.get(key)
            if previous is not None and previous.digest != item.digest:
                raise RegistryConflict(f"conflicting component identity: {_identity_label(key)}")
            components[key] = item
        elif item.kind == "passport":
            passports.append(item)

    for passport in passports:
        key = _passport_key(passport.document)
        component = components.get(key)
        if component is None:
            continue
        claimed = passport.document["provenance"]["manifest_digest"]
        if claimed != component.digest:
            raise RegistryConflict(
                f"passport manifest digest conflicts with component {_identity_label(key)}: "
                f"passport={claimed} component={component.digest}"
            )


def build_registry(documents: Iterable[dict]) -> dict:
    """Build a deterministic registry from validated source documents."""
    by_digest: dict[str, ClassifiedDocument] = {}
    for document in documents:
        classified = _classify(document)
        by_digest.setdefault(classified.digest, classified)

    items = list(by_digest.values())
    _check_conflicts(items)
    items.sort(key=_sort_key)
    return {
        "schema": "release-registry/1.0",
        "entries": [
            {"kind": item.kind, "digest": item.digest, "document": item.document}
            for item in items
        ],
    }


class Registry:
    """Validated read-only index over a release-registry/1.0 document."""

    def __init__(self, document: dict) -> None:
        if not isinstance(document, dict):
            raise RegistryError("registry must be an object")
        unexpected = set(document) - {"schema", "entries"}
        if unexpected:
            raise RegistryError(f"unexpected registry field: {sorted(unexpected)[0]}")
        if document.get("schema") != "release-registry/1.0":
            raise RegistryError("registry schema must be release-registry/1.0")
        entries = document.get("entries")
        if not isinstance(entries, list):
            raise RegistryError("registry entries must be an array")

        classified: list[ClassifiedDocument] = []
        seen_digests: set[str] = set()
        for index, entry in enumerate(entries):
            if not isinstance(entry, dict):
                raise RegistryError(f"entry[{index}] must be an object")
            unexpected_entry = set(entry) - {"kind", "digest", "document"}
            if unexpected_entry:
                raise RegistryError(f"unexpected entry[{index}] field: {sorted(unexpected_entry)[0]}")
            for field in ("kind", "digest", "document"):
                if field not in entry:
                    raise RegistryError(f"missing entry[{index}].{field}")
            source = _classify(entry["document"])
            if source.kind != entry["kind"]:
                raise RegistryError(
                    f"entry[{index}] kind mismatch: stored={entry['kind']} actual={source.kind}"
                )
            if source.digest != entry["digest"]:
                raise RegistryError(
                    f"entry digest mismatch at index {index}: stored={entry['digest']} actual={source.digest}"
                )
            if source.digest in seen_digests:
                raise RegistryError(f"duplicate registry entry digest: {source.digest}")
            seen_digests.add(source.digest)
            classified.append(source)

        _check_conflicts(classified)
        expected = build_registry(item.document for item in classified)
        if document != expected:
            raise RegistryError("registry entries are not in canonical deterministic order")

        self.document = document
        self.digest = canonical_digest(document)
        self._entries = classified

    def components(self) -> list[dict]:
        return [item.document for item in self._entries if item.kind == "component"]

    def edges(self) -> list[dict]:
        return [item.document for item in self._entries if item.kind == "edge"]

    def passports(self) -> list[dict]:
        return [item.document for item in self._entries if item.kind == "passport"]

    def component(self, component: str, version: str, commit: str) -> dict:
        key = (component, version, commit)
        matches = [doc for doc in self.components() if _component_key(doc) == key]
        if not matches:
            raise RegistryError(f"component not found: {_identity_label(key)}")
        return matches[0]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build or inspect an Aftergraph Release Registry")
    subparsers = parser.add_subparsers(dest="command", required=True)
    build = subparsers.add_parser("build", help="build a deterministic registry")
    build.add_argument("--document", action="append", required=True, type=Path)
    build.add_argument("--format", choices=("json", "pretty"), default="json")
    args = parser.parse_args(argv)

    try:
        documents = [load_json(path) for path in args.document]
        registry = build_registry(documents)
        Registry(registry)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(json.dumps({"schema": "release-registry-error/1", "state": "FAIL", "error": str(exc)}, sort_keys=True))
        return 2

    if args.format == "pretty":
        print(json.dumps(registry, indent=2, sort_keys=True))
    else:
        print(json.dumps(registry, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
