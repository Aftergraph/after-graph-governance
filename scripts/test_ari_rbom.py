import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.ari_model import canonical_digest
from scripts.ari_rbom import RbomError, build_rbom
from scripts.ari_registry import Registry, build_registry

ROOT = Path(__file__).resolve().parents[1]

SENTINEL = {
    "schema": "aftergraph-component/1.0",
    "identity": {"product": "sentinel", "component": "sentinel-engine"},
    "release": {"version": "1.4.0", "lifecycle": "preview"},
    "platform": {"generation": 26, "release_train": "2026.09"},
    "compatibility": {
        "level": "APC-1",
        "profiles": ["verifier"],
        "minimum": "APC-1",
        "tested_against": "APC-1",
    },
    "contracts": {"correlation": "1.0", "evidence": "1.1", "verdict": "1.0"},
    "provenance": {"repository": "Aftergraph/sentinel", "commit": "1" * 40},
}

WORKS = {
    "schema": "aftergraph-component/1.0",
    "identity": {"product": "works", "component": "works"},
    "release": {"version": "0.5.1", "lifecycle": "preview"},
    "platform": {"generation": 26, "release_train": "2026.09"},
    "compatibility": {
        "level": "APC-1",
        "profiles": ["execution"],
        "minimum": "APC-1",
        "tested_against": "APC-1",
    },
    "contracts": {"correlation": "1.0", "evidence": "1.1", "work": "1.0"},
    "provenance": {"repository": "Aftergraph/works-execution", "commit": "2" * 40},
}


def passport(manifest, profile):
    return {
        "schema": "release-passport/1.0",
        "subject": {
            "component": manifest["identity"]["component"],
            "version": manifest["release"]["version"],
        },
        "platform": {
            "generation": manifest["platform"]["generation"],
            "release_train": manifest["platform"]["release_train"],
            "compatibility": manifest["compatibility"]["level"],
        },
        "conformance": {
            "result": "PASS",
            "profiles": {profile: "PASS"},
            "evidence": ["sha256:" + "3" * 64],
        },
        "provenance": {
            "repository": manifest["provenance"]["repository"],
            "commit": manifest["provenance"]["commit"],
            "artifact_digest": "sha256:" + ("a" if profile == "verifier" else "b") * 64,
            "manifest_digest": canonical_digest(manifest),
        },
    }


SENTINEL_SELECTOR = "sentinel-engine@1.4.0#" + "1" * 40
WORKS_SELECTOR = "works@0.5.1#" + "2" * 40


class AriRbomTest(unittest.TestCase):
    def registry(self, *, sentinel_passport=True, works_passport=True, works=WORKS):
        docs = [SENTINEL, works]
        if sentinel_passport:
            docs.append(passport(SENTINEL, "verifier"))
        if works_passport:
            docs.append(passport(works, "execution"))
        return Registry(build_registry(docs))

    def test_rbom_uses_exact_component_selector(self):
        rbom = build_rbom(self.registry(), [SENTINEL_SELECTOR])
        self.assertEqual(len(rbom["components"]), 1)
        component = rbom["components"][0]
        self.assertEqual(component["component"], "sentinel-engine")
        self.assertEqual(component["version"], "1.4.0")
        self.assertEqual(component["commit"], "1" * 40)
        self.assertEqual(component["manifest_digest"], canonical_digest(SENTINEL))
        self.assertRegex(component["passport_digest"], r"^sha256:[a-f0-9]{64}$")
        self.assertEqual(component["artifact_digest"], "sha256:" + "a" * 64)

    def test_rbom_refuses_missing_selector(self):
        missing = "sentinel-engine@1.4.0#" + "9" * 40
        with self.assertRaisesRegex(RbomError, "component not found"):
            build_rbom(self.registry(), [missing])

    def test_rbom_refuses_duplicate_selector(self):
        with self.assertRaisesRegex(RbomError, "duplicate component selector"):
            build_rbom(self.registry(), [SENTINEL_SELECTOR, SENTINEL_SELECTOR])

    def test_rbom_contract_inventory_is_sorted_and_deduplicated(self):
        rbom = build_rbom(self.registry(), [WORKS_SELECTOR, SENTINEL_SELECTOR])
        self.assertEqual(
            rbom["contracts"],
            [
                {"name": "correlation", "versions": ["1.0"]},
                {"name": "evidence", "versions": ["1.1"]},
                {"name": "verdict", "versions": ["1.0"]},
                {"name": "work", "versions": ["1.0"]},
            ],
        )
        self.assertEqual([row["component"] for row in rbom["components"]], ["sentinel-engine", "works"])

    def test_rbom_verified_only_when_every_selected_component_has_matching_passport(self):
        rbom = build_rbom(self.registry(), [SENTINEL_SELECTOR, WORKS_SELECTOR])
        self.assertEqual(rbom["verification"], {"state": "VERIFIED", "passport_count": 2, "component_count": 2})

    def test_rbom_partial_when_only_some_components_have_matching_passports(self):
        rbom = build_rbom(
            self.registry(sentinel_passport=True, works_passport=False),
            [SENTINEL_SELECTOR, WORKS_SELECTOR],
        )
        self.assertEqual(rbom["verification"], {"state": "PARTIAL", "passport_count": 1, "component_count": 2})

    def test_rbom_unverified_when_no_passports_match(self):
        rbom = build_rbom(
            self.registry(sentinel_passport=False, works_passport=False),
            [SENTINEL_SELECTOR, WORKS_SELECTOR],
        )
        self.assertEqual(rbom["verification"], {"state": "UNVERIFIED", "passport_count": 0, "component_count": 2})

    def test_rbom_refuses_mixed_release_train(self):
        works = copy.deepcopy(WORKS)
        works["platform"]["release_train"] = "2026.10"
        with self.assertRaisesRegex(RbomError, "mixed platform release_train"):
            build_rbom(
                self.registry(works=works),
                [SENTINEL_SELECTOR, WORKS_SELECTOR],
            )

    def test_registry_digest_is_bound(self):
        registry = self.registry()
        rbom = build_rbom(registry, [SENTINEL_SELECTOR])
        self.assertEqual(rbom["registry_digest"], registry.digest)

    def test_cli_emits_deterministic_rbom(self):
        registry = self.registry()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "registry.json"
            path.write_text(json.dumps(registry.document), encoding="utf-8")
            command = [
                sys.executable,
                str(ROOT / "scripts/ari_rbom.py"),
                "build",
                str(path),
                "--component",
                WORKS_SELECTOR,
                "--component",
                SENTINEL_SELECTOR,
                "--format",
                "json",
            ]
            first = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
            second = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual(first.stdout, second.stdout)
        payload = json.loads(first.stdout)
        self.assertEqual(payload["schema"], "rbom/0.1")
        self.assertEqual(payload["verification"]["state"], "VERIFIED")


if __name__ == "__main__":
    unittest.main()
