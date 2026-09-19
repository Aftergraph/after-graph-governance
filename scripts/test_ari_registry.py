import copy
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.ari_model import canonical_digest
from scripts.ari_registry import Registry, RegistryConflict, RegistryError, build_registry

ROOT = Path(__file__).resolve().parents[1]

COMPONENT = {
    "schema": "aftergraph-component/1.0",
    "identity": {"product": "sentinel", "component": "sentinel-engine"},
    "release": {"version": "1.4.0", "lifecycle": "preview"},
    "platform": {"generation": 26, "release_train": "2026.09"},
    "compatibility": {
        "level": "APC-1",
        "profiles": ["verifier"],
        "minimum": "APC-1",
        "tested_against": "APC-1",
        "requires_edges": [
            {"component": "works", "version": "0.5.1", "commit": "2" * 40}
        ],
    },
    "contracts": {"correlation": "1.0", "evidence": "1.1", "verdict": "1.0"},
    "provenance": {"repository": "Aftergraph/sentinel", "commit": "1" * 40},
}

EDGE = {
    "schema": "compatibility-edge/1.0",
    "from": {"component": "sentinel-engine", "version": "1.4.0", "commit": "1" * 40},
    "to": {"component": "works", "version": "0.5.1", "commit": "2" * 40},
    "relation": "tested-with",
    "state": "pass",
    "evidence_level": "CE3",
    "evidence": [{"kind": "test-receipt", "ref": "sha256:" + "3" * 64}],
}

PASSPORT = {
    "schema": "release-passport/1.0",
    "subject": {"component": "sentinel-engine", "version": "1.4.0"},
    "platform": {"generation": 26, "release_train": "2026.09", "compatibility": "APC-1"},
    "conformance": {
        "result": "PASS",
        "profiles": {"verifier": "PASS"},
        "evidence": ["sha256:" + "3" * 64],
    },
    "provenance": {
        "repository": "Aftergraph/sentinel",
        "commit": "1" * 40,
        "artifact_digest": "sha256:" + "a" * 64,
        "manifest_digest": canonical_digest(COMPONENT),
    },
}


class AriRegistryTest(unittest.TestCase):
    def test_registry_is_deterministic_across_input_order(self):
        first = build_registry([COMPONENT, EDGE, PASSPORT])
        second = build_registry([PASSPORT, COMPONENT, EDGE])
        self.assertEqual(first, second)
        self.assertEqual(canonical_digest(first), canonical_digest(second))

    def test_registry_build_snapshots_input_documents(self):
        source = copy.deepcopy(COMPONENT)
        registry = build_registry([source])
        expected_digest = registry["entries"][0]["digest"]
        source["contracts"]["verdict"] = "9.9"
        stored = registry["entries"][0]["document"]
        self.assertEqual(stored["contracts"]["verdict"], "1.0")
        self.assertEqual(canonical_digest(stored), expected_digest)

    def test_registry_constructor_snapshots_registry_document(self):
        source = build_registry([COMPONENT])
        registry = Registry(source)
        expected_digest = registry.digest
        source["entries"][0]["document"]["contracts"]["verdict"] = "9.9"
        self.assertEqual(registry.document["entries"][0]["document"]["contracts"]["verdict"], "1.0")
        self.assertEqual(canonical_digest(registry.document), expected_digest)

    def test_registry_public_document_and_digest_are_read_only_views(self):
        registry = Registry(build_registry([COMPONENT]))
        exposed = registry.document
        exposed["entries"][0]["document"]["contracts"]["verdict"] = "9.9"
        self.assertEqual(registry.document["entries"][0]["document"]["contracts"]["verdict"], "1.0")
        self.assertEqual(canonical_digest(registry.document), registry.digest)
        with self.assertRaises(AttributeError):
            registry.document = {}
        with self.assertRaises(AttributeError):
            registry.digest = "sha256:" + "0" * 64

    def test_registry_accessors_return_isolated_documents(self):
        registry = Registry(build_registry([COMPONENT, EDGE, PASSPORT]))
        returned = registry.components()[0]
        returned["contracts"]["verdict"] = "9.9"
        exact = registry.component("sentinel-engine", "1.4.0", "1" * 40)
        self.assertEqual(exact["contracts"]["verdict"], "1.0")
        self.assertEqual(canonical_digest(registry.document), registry.digest)

    def test_registry_classifies_component_edge_and_passport(self):
        registry = Registry(build_registry([COMPONENT, EDGE, PASSPORT]))
        self.assertEqual(len(registry.components()), 1)
        self.assertEqual(len(registry.edges()), 1)
        self.assertEqual(len(registry.passports()), 1)
        self.assertEqual(registry.components()[0]["identity"]["component"], "sentinel-engine")

    def test_registry_rejects_invalid_document(self):
        invalid = copy.deepcopy(COMPONENT)
        invalid["provenance"]["commit"] = "bad"
        with self.assertRaisesRegex(RegistryError, "provenance.commit"):
            build_registry([invalid])

    def test_registry_rejects_passport_with_nonpassing_profile_state(self):
        passport = copy.deepcopy(PASSPORT)
        passport["conformance"]["profiles"]["verifier"] = "FAIL"
        with self.assertRaisesRegex(RegistryError, "PASS passport profile verifier"):
            build_registry([passport])

    def test_registry_deduplicates_semantically_identical_document(self):
        registry = build_registry([COMPONENT, copy.deepcopy(COMPONENT)])
        self.assertEqual(len(registry["entries"]), 1)
        self.assertEqual(registry["entries"][0]["digest"], canonical_digest(COMPONENT))

    def test_registry_rejects_divergent_same_exact_component_identity(self):
        divergent = copy.deepcopy(COMPONENT)
        divergent["contracts"]["verdict"] = "1.1"
        with self.assertRaisesRegex(RegistryConflict, "sentinel-engine@1.4.0#111111111111"):
            build_registry([COMPONENT, divergent])

    def test_registry_rejects_contradictory_exact_edge_states(self):
        failed = copy.deepcopy(EDGE)
        failed["state"] = "fail"
        with self.assertRaisesRegex(RegistryConflict, "conflicting compatibility edge claim"):
            build_registry([EDGE, failed])

    def test_registry_rejects_reverse_contradiction_for_symmetric_edge(self):
        reverse_failed = copy.deepcopy(EDGE)
        reverse_failed["from"], reverse_failed["to"] = (
            copy.deepcopy(EDGE["to"]),
            copy.deepcopy(EDGE["from"]),
        )
        reverse_failed["state"] = "fail"
        with self.assertRaisesRegex(RegistryConflict, "conflicting compatibility edge claim"):
            build_registry([EDGE, reverse_failed])

    def test_registry_allows_same_state_edge_with_independent_evidence(self):
        corroborating = copy.deepcopy(EDGE)
        corroborating["evidence"] = [{"kind": "second-test-receipt", "ref": "sha256:" + "4" * 64}]
        registry = build_registry([EDGE, corroborating])
        self.assertEqual(len(registry["entries"]), 2)

    def test_registry_digest_changes_when_source_document_changes(self):
        first = build_registry([COMPONENT])
        changed = copy.deepcopy(COMPONENT)
        changed["contracts"]["verdict"] = "1.1"
        second = build_registry([changed])
        self.assertNotEqual(canonical_digest(first), canonical_digest(second))

    def test_registry_rejects_entry_digest_mismatch(self):
        document = build_registry([COMPONENT])
        document["entries"][0]["digest"] = "sha256:" + "0" * 64
        with self.assertRaisesRegex(RegistryError, "entry digest mismatch"):
            Registry(document)

    def test_registry_rejects_passport_manifest_mismatch_when_component_present(self):
        passport = copy.deepcopy(PASSPORT)
        passport["provenance"]["manifest_digest"] = "sha256:" + "0" * 64
        with self.assertRaisesRegex(RegistryConflict, "passport manifest digest"):
            build_registry([COMPONENT, passport])

    def test_registry_rejects_passport_repository_mismatch_when_component_present(self):
        passport = copy.deepcopy(PASSPORT)
        passport["provenance"]["repository"] = "Elsewhere/sentinel"
        with self.assertRaisesRegex(RegistryConflict, "passport repository"):
            build_registry([COMPONENT, passport])

    def test_registry_rejects_passport_release_train_mismatch_when_component_present(self):
        passport = copy.deepcopy(PASSPORT)
        passport["platform"]["release_train"] = "2026.10"
        with self.assertRaisesRegex(RegistryConflict, "passport release_train"):
            build_registry([COMPONENT, passport])

    def test_registry_rejects_passport_profile_set_mismatch_when_component_present(self):
        passport = copy.deepcopy(PASSPORT)
        passport["conformance"]["profiles"] = {"execution": "PASS"}
        with self.assertRaisesRegex(RegistryConflict, "passport profile set"):
            build_registry([COMPONENT, passport])

    def test_cli_builds_machine_readable_registry(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            paths = []
            for name, document in (("component.json", COMPONENT), ("edge.json", EDGE), ("passport.json", PASSPORT)):
                path = root / name
                path.write_text(json.dumps(document), encoding="utf-8")
                paths.append(path)
            command = [sys.executable, str(ROOT / "scripts/ari_registry.py"), "build"]
            for path in paths:
                command.extend(["--document", str(path)])
            command.extend(["--format", "json"])
            proc = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["schema"], "release-registry/1.0")
        self.assertEqual(len(payload["entries"]), 3)


REGISTRY_CONTRACT = ROOT / "docs" / "contracts" / "release-registry" / "1.0.json"


def _registry_schema_errors(instance, schema, root):
    """Evaluate instance against schema using only the standard library.

    Mirrors the hand-rolled contract checks in verify_exact_head_truth.py and
    reduce_ci_truth.py: the Release Intelligence gate installs no jsonschema,
    so the interop boundary this proves has to be checkable with stdlib alone.
    Supports exactly the keywords release-registry/1.0 uses — type, required,
    properties, additionalProperties, items, enum, const, pattern, oneOf, and
    a local $ref that replaces the schema (no sibling keywords occur here).
    """
    if "$ref" in schema:
        target = root
        for token in schema["$ref"].lstrip("#/").split("/"):
            target = target[token]
        return _registry_schema_errors(instance, target, root)

    expected = schema.get("type")
    if expected is not None:
        candidates = expected if isinstance(expected, list) else [expected]
        matches = {
            "object": isinstance(instance, dict),
            "array": isinstance(instance, list),
            "string": isinstance(instance, str),
        }
        if not any(matches.get(name, False) for name in candidates):
            return [f"expected type {candidates}, got {type(instance).__name__}"]

    errors: list[str] = []
    if isinstance(instance, dict):
        properties = schema.get("properties", {})
        for key in schema.get("required", ()):
            if key not in instance:
                errors.append(f"missing required property: {key}")
        for key, subschema in properties.items():
            if key in instance:
                errors.extend(_registry_schema_errors(instance[key], subschema, root))
        if schema.get("additionalProperties") is False:
            for key in instance:
                if key not in properties:
                    errors.append(f"unexpected property: {key}")
    elif isinstance(instance, list) and "items" in schema:
        for index, item in enumerate(instance):
            for error in _registry_schema_errors(item, schema["items"], root):
                errors.append(f"entries[{index}] {error}")

    if "const" in schema and instance != schema["const"]:
        errors.append(f"expected const {schema['const']!r}, got {instance!r}")
    if "enum" in schema and instance not in schema["enum"]:
        errors.append(f"{instance!r} is not one of {schema['enum']}")
    pattern = schema.get("pattern")
    if pattern is not None and isinstance(instance, str) and re.search(pattern, instance) is None:
        errors.append(f"{instance!r} does not match pattern {pattern}")
    if "oneOf" in schema:
        valid_branches = sum(
            not _registry_schema_errors(instance, branch, root)
            for branch in schema["oneOf"]
        )
        if valid_branches != 1:
            errors.append(f"{valid_branches} oneOf branches validate, expected exactly 1")
    return errors


class AriRegistryContractInteropTest(unittest.TestCase):
    """The published contract must reject what the reference Registry rejects.

    Registry._classify() dispatches on document['schema'] and Registry.__init__
    refuses a kind/schema disagreement, so an empty or kind-mismatched document
    is already a defect in Python. A cross-repository consumer validating only
    release-registry/1.0 has to refuse it too, or the published contract is
    weaker than the implementation it claims to describe.
    """

    def setUp(self):
        self.contract = json.loads(REGISTRY_CONTRACT.read_text(encoding="utf-8"))

    def errors(self, document):
        return _registry_schema_errors(document, self.contract, self.contract)

    def test_contract_rejects_an_entry_with_an_empty_document(self):
        entry = {"kind": "component", "digest": "sha256:" + "a" * 64, "document": {}}
        self.assertTrue(self.errors({"schema": "release-registry/1.0", "entries": [entry]}))

    def test_contract_rejects_a_kind_mismatched_document(self):
        entry = {
            "kind": "component",
            "digest": "sha256:" + "a" * 64,
            "document": {"schema": "compatibility-edge/1.0"},
        }
        self.assertTrue(self.errors({"schema": "release-registry/1.0", "entries": [entry]}))

    def test_contract_rejects_an_unknown_kind(self):
        entry = {
            "kind": "widget",
            "digest": "sha256:" + "a" * 64,
            "document": {"schema": "aftergraph-component/1.0"},
        }
        self.assertTrue(self.errors({"schema": "release-registry/1.0", "entries": [entry]}))

    def test_contract_accepts_every_entry_a_real_registry_emits(self):
        registry = build_registry([COMPONENT, EDGE, PASSPORT])
        self.assertEqual(self.errors(registry), [])
        self.assertEqual(
            {entry["kind"] for entry in registry["entries"]},
            {"component", "edge", "passport"},
        )

    def test_contract_bounds_shape_only_and_leaves_digest_recomputation_to_registry(self):
        tampered = build_registry([COMPONENT])
        tampered["entries"][0]["digest"] = "sha256:" + "0" * 64
        with self.assertRaises(RegistryError):
            Registry(tampered)
        self.assertEqual(self.errors(tampered), [])

    def test_evaluator_is_not_vacuously_permissive(self):
        self.assertEqual(self.errors(build_registry([COMPONENT])), [])
        self.assertTrue(
            self.errors({"schema": "release-registry/1.0", "entries": [], "extra": 1})
        )
        self.assertTrue(self.errors({"schema": "release-registry/0.9", "entries": []}))


if __name__ == "__main__":
    unittest.main()