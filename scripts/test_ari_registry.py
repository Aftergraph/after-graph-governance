import copy
import json
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

    def test_registry_deduplicates_semantically_identical_document(self):
        registry = build_registry([COMPONENT, copy.deepcopy(COMPONENT)])
        self.assertEqual(len(registry["entries"]), 1)
        self.assertEqual(registry["entries"][0]["digest"], canonical_digest(COMPONENT))

    def test_registry_rejects_divergent_same_exact_component_identity(self):
        divergent = copy.deepcopy(COMPONENT)
        divergent["contracts"]["verdict"] = "1.1"
        with self.assertRaisesRegex(RegistryConflict, "sentinel-engine@1.4.0#111111111111"):
            build_registry([COMPONENT, divergent])

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


if __name__ == "__main__":
    unittest.main()
