#!/usr/bin/env python3
"""Conformance checks for experimental labs-fabric/0.1.

These checks prove contract-level fail-closed behavior only. They do not prove
live cross-repo integration, authority, verification, promotion, or scientific
validity.
"""
from __future__ import annotations

import json
import re
import unittest
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
VECTORS = ROOT / "docs" / "platform-conformance" / "labs-fabric-v0.1" / "vectors.json"
SHA1_RE = re.compile(r"^[a-f0-9]{40}$")
SHA256_RE = re.compile(r"^[a-f0-9]{64}$")


def load_vectors() -> dict:
    return json.loads(VECTORS.read_text(encoding="utf-8"))


def validate_adapter(doc: dict) -> list[str]:
    errors: list[str] = []
    if doc.get("schemaVersion") != "aftergraph.labs-adapter/v1":
        errors.append("unsupported adapter schema")
    if not str(doc.get("id", "")).strip():
        errors.append("adapter id required")
    if not str(doc.get("repository", "")).startswith("Aftergraph/"):
        errors.append("repository must be in Aftergraph org")
    if not doc.get("capabilities"):
        errors.append("capabilities required")
    if doc.get("authorityGranted") is not False:
        errors.append("labs adapter cannot grant authority")
    if doc.get("maximumClaim") != "OBSERVED":
        errors.append("maximumClaim must be OBSERVED")
    for field in ("healthPath", "contractPath"):
        value = doc.get(field)
        if value is not None:
            if not isinstance(value, str) or not value.startswith("/"):
                errors.append(f"{field} must be an absolute path reference")
            if "://" in str(value):
                errors.append(f"{field} must not embed an origin")
    return errors


def validate_endpoint(doc: dict) -> list[str]:
    errors: list[str] = []
    adapter_id = str(doc.get("adapterId", "")).strip()
    if not adapter_id:
        errors.append("adapterId required")
    raw = str(doc.get("baseUrl", ""))
    try:
        parsed = urlparse(raw)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            errors.append("baseUrl must be absolute http(s)")
        if parsed.username or parsed.password:
            errors.append("endpoint URL must not contain credentials")
        loopback = parsed.hostname in {"127.0.0.1", "localhost", "::1"}
        if parsed.scheme == "http" and not loopback:
            errors.append("plaintext HTTP is allowed only for loopback endpoints")
        if parsed.path not in {"", "/"}:
            errors.append("baseUrl must not include a path")
    except Exception:
        errors.append("invalid baseUrl")
    expected_revision = doc.get("expectedRevision")
    if expected_revision is not None and not SHA1_RE.fullmatch(str(expected_revision)):
        errors.append("expectedRevision must be an exact 40-character git SHA")
    return errors


def validate_bundle(doc: dict) -> list[str]:
    errors: list[str] = []
    if doc.get("schemaVersion") != "aftergraph.federated-evidence-bundle/v1":
        errors.append("unsupported bundle schema")
    if not SHA256_RE.fullmatch(str(doc.get("planDigest", ""))):
        errors.append("planDigest must be sha256 hex")
    if not SHA256_RE.fullmatch(str(doc.get("bundleDigest", ""))):
        errors.append("bundleDigest must be sha256 hex")
    if not isinstance(doc.get("layers"), list):
        errors.append("layers must be an array")
    if not isinstance(doc.get("unresolvedTargets"), list):
        errors.append("unresolvedTargets must be an array")
    if doc.get("authorityGranted") is not False:
        errors.append("bundle cannot grant authority")
    if doc.get("verificationGranted") is not False:
        errors.append("bundle cannot grant verification")
    if doc.get("scientificValidityGranted") is not False:
        errors.append("bundle cannot grant scientific validity")
    if doc.get("maximumClaim") != "OBSERVED":
        errors.append("bundle maximumClaim must be OBSERVED")
    for layer in doc.get("layers", []) if isinstance(doc.get("layers"), list) else []:
        for obs in layer.get("observations", []) if isinstance(layer, dict) else []:
            if obs.get("schemaVersion") != "aftergraph.labs-observation/v1":
                errors.append("unsupported observation schema")
            if obs.get("authorityGranted") is not False:
                errors.append("observation cannot grant authority")
            if obs.get("maximumClaim") != "OBSERVED":
                errors.append("observation maximumClaim must be OBSERVED")
            if not SHA256_RE.fullmatch(str(obs.get("observationDigest", ""))):
                errors.append("observationDigest must be sha256 hex")
    return errors


def validate_eval_normalization(doc: dict) -> list[str]:
    errors: list[str] = []
    if doc.get("contract") != "FihimFrontierLabsEvidence/v1":
        errors.append("unsupported normalized evidence contract")
    if doc.get("promotion") != "HOLD":
        errors.append("frontier labs normalization must HOLD")
    if doc.get("maximumTruthClaim") != "OBSERVED":
        errors.append("maximumTruthClaim must be OBSERVED")
    if doc.get("authorityGranted") is not False:
        errors.append("normalization cannot grant authority")
    if doc.get("verificationGranted") is not False:
        errors.append("normalization cannot grant verification")
    if doc.get("scientificValidityGranted") is not False:
        errors.append("normalization cannot grant scientific validity")
    return errors



def validate_exact_head(doc: dict) -> list[str]:
    errors: list[str] = []
    expected = doc.get("expectedRevision")
    observed = doc.get("observedRevision")
    if not SHA1_RE.fullmatch(str(expected or "")):
        errors.append("expectedRevision must be an exact 40-character git SHA")
    if observed is None:
        errors.append("observed revision required when exact-head fencing is configured")
    elif not SHA1_RE.fullmatch(str(observed)):
        errors.append("observedRevision must be an exact 40-character git SHA")
    elif str(expected).lower() != str(observed).lower():
        errors.append("stale exact-head observation")
    return errors


def _major_minor(value: object) -> str | None:
    match = re.match(r"^(?:v)?(\d+)\.(\d+)(?:\.|$)", str(value or "").strip())
    return f"{match.group(1)}.{match.group(2)}" if match else None


def validate_sut_binding(doc: dict) -> list[str]:
    errors: list[str] = []
    if doc.get("schemaVersion") != "aftergraph.labs-sut-binding/v1":
        errors.append("unsupported SUT binding schema")
    if doc.get("repository") != "Aftergraph/fihim-vnext":
        errors.append("repository must be Aftergraph/fihim-vnext")
    if not str(doc.get("sutId", "")).strip():
        errors.append("sutId required")
    requested = _major_minor(doc.get("requestedVersion"))
    packaged = _major_minor(doc.get("packageVersion"))
    if requested is None:
        errors.append("requestedVersion must include major.minor")
    if packaged is None:
        errors.append("packageVersion must include major.minor")
    if requested and packaged and requested != packaged:
        errors.append("packageVersion does not match requestedVersion major.minor")
    if requested and doc.get("directoryName") != f"fihim-vnext-v{requested}":
        errors.append("directoryName does not match FIHIM vNext discovery contract")
    if not SHA1_RE.fullmatch(str(doc.get("sourceRevision", ""))):
        errors.append("sourceRevision must be an exact 40-character git SHA")
    if not SHA256_RE.fullmatch(str(doc.get("contentDigest", ""))):
        errors.append("contentDigest must be sha256 hex")
    if not SHA256_RE.fullmatch(str(doc.get("bindingDigest", ""))):
        errors.append("bindingDigest must be sha256 hex")
    if doc.get("immutableSubject") is not True:
        errors.append("immutableSubject must be true")
    if doc.get("authorityGranted") is not False:
        errors.append("SUT binding cannot grant authority")
    if doc.get("maximumClaim") != "OBSERVED":
        errors.append("SUT binding maximumClaim must be OBSERVED")
    return errors


def validate_sut_normalization(doc: dict) -> list[str]:
    errors: list[str] = []
    if doc.get("contract") != "FihimFrontierLabsSutEvidence/v1":
        errors.append("unsupported normalized SUT evidence contract")
    if doc.get("promotion") != "HOLD":
        errors.append("SUT normalization must HOLD")
    if doc.get("maximumTruthClaim") != "OBSERVED":
        errors.append("SUT normalization maximumTruthClaim must be OBSERVED")
    if doc.get("authorityGranted") is not False:
        errors.append("SUT normalization cannot grant authority")
    if doc.get("verificationGranted") is not False:
        errors.append("SUT normalization cannot grant verification")
    if doc.get("scientificValidityGranted") is not False:
        errors.append("SUT normalization cannot grant scientific validity")
    sut = doc.get("sut")
    if not isinstance(sut, dict):
        errors.append("normalized SUT subject required")
    else:
        if sut.get("repository") != "Aftergraph/fihim-vnext":
            errors.append("normalized SUT repository mismatch")
        if not SHA1_RE.fullmatch(str(sut.get("sourceRevision", ""))):
            errors.append("normalized SUT sourceRevision must be exact")
        if not SHA256_RE.fullmatch(str(sut.get("contentDigest", ""))):
            errors.append("normalized SUT contentDigest must be sha256 hex")
        if sut.get("immutableSubject") is not True:
            errors.append("normalized SUT subject must be immutable")
    return errors

def validate_vector(vector: dict) -> list[str]:
    kind = vector.get("kind")
    doc = vector.get("input", {})
    if kind == "adapter":
        return validate_adapter(doc)
    if kind == "endpoint":
        return validate_endpoint(doc)
    if kind == "bundle":
        return validate_bundle(doc)
    if kind == "eval_normalization":
        return validate_eval_normalization(doc)
    if kind == "exact_head":
        return validate_exact_head(doc)
    if kind == "sut_binding":
        return validate_sut_binding(doc)
    if kind == "sut_normalization":
        return validate_sut_normalization(doc)
    return [f"unsupported vector kind: {kind}"]


class TestLabsFabricConformance(unittest.TestCase):
    def test_vector_set_is_complete_and_fail_closed(self) -> None:
        payload = load_vectors()
        self.assertEqual(payload["schema_version"], "labs-fabric-conformance-v0.1")
        vectors = payload["vectors"]
        self.assertEqual({v["id"] for v in vectors}, {
            "LAB-001", "LAB-002", "LAB-003", "LAB-004",
            "LAB-005", "LAB-006", "LAB-007", "LAB-008",
            "LAB-009", "LAB-010", "LAB-011", "LAB-012", "LAB-013",
        })
        for vector in vectors:
            with self.subTest(vector=vector["id"]):
                errors = validate_vector(vector)
                if vector["expected"] == "accept":
                    self.assertEqual(errors, [])
                else:
                    self.assertNotEqual(errors, [])

    def test_no_positive_vector_upgrades_truth_or_authority(self) -> None:
        for vector in load_vectors()["vectors"]:
            if vector["expected"] != "accept":
                continue
            doc = vector["input"]
            self.assertIsNot(doc.get("authorityGranted"), True)
            self.assertIsNot(doc.get("verificationGranted"), True)
            self.assertIsNot(doc.get("scientificValidityGranted"), True)
            self.assertNotEqual(doc.get("promotion"), "PROMOTE")
            self.assertNotEqual(doc.get("maximumClaim"), "VERIFIED")
            self.assertNotEqual(doc.get("maximumTruthClaim"), "VERIFIED")


if __name__ == "__main__":
    unittest.main(verbosity=2)
