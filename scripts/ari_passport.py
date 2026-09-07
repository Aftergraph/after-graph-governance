#!/usr/bin/env python3
"""Generate exact-subject ARI Release Passports from passing APC conformance."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.ari_compile import CompileResult, compile_component  # noqa: E402
from scripts.ari_model import ResultState, canonical_digest, load_json, validate_component  # noqa: E402

ARTIFACT_RE = re.compile(r"^sha256:[a-f0-9]{64}$")


class PassportError(ValueError):
    """Raised when a positive release passport cannot be justified."""


def build_passport(manifest: dict, compile_result: CompileResult, artifact_digest: str) -> dict:
    manifest_errors = validate_component(manifest)
    if manifest_errors:
        raise PassportError("invalid component manifest: " + "; ".join(manifest_errors))
    if compile_result.state != ResultState.PASS:
        raise PassportError(
            f"release passport requires PASS conformance, got {compile_result.state.value}"
        )
    if not ARTIFACT_RE.fullmatch(artifact_digest):
        raise PassportError("artifact digest must be sha256:<64 lowercase hex>")

    identity = manifest["identity"]
    release = manifest["release"]
    platform = manifest["platform"]
    compatibility = manifest["compatibility"]
    provenance = manifest["provenance"]

    return {
        "schema": "release-passport/1.0",
        "subject": {
            "component": identity["component"],
            "version": release["version"],
        },
        "platform": {
            "generation": platform["generation"],
            "release_train": platform["release_train"],
            "compatibility": compatibility["level"],
        },
        "conformance": {
            "result": "PASS",
            "profiles": {
                name: state.value for name, state in compile_result.profile_results.items()
            },
            "evidence": list(compile_result.evidence_refs),
        },
        "provenance": {
            "repository": provenance["repository"],
            "commit": provenance["commit"],
            "artifact_digest": artifact_digest,
            "manifest_digest": canonical_digest(manifest),
        },
    }


def _refusal_exit(state: ResultState) -> int:
    if state == ResultState.FAIL:
        return 2
    return 3


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate an Aftergraph Release Passport")
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--edge", action="append", default=[], type=Path)
    parser.add_argument("--apc", type=Path, default=ROOT / "docs/release-intelligence/apc-1.json")
    parser.add_argument("--artifact-digest", required=True)
    args = parser.parse_args(argv)

    try:
        manifest = load_json(args.manifest)
        apc = load_json(args.apc)
        edges = [load_json(path) for path in args.edge]
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"schema": "release-passport-error/1", "state": "FAIL", "error": str(exc)}, sort_keys=True))
        return 2

    result = compile_component(manifest, apc, edges)
    try:
        passport = build_passport(manifest, result, args.artifact_digest)
    except PassportError as exc:
        print(
            json.dumps(
                {
                    "schema": "release-passport-error/1",
                    "state": result.state.value,
                    "error": str(exc),
                },
                sort_keys=True,
            )
        )
        return _refusal_exit(result.state)

    print(json.dumps(passport, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
