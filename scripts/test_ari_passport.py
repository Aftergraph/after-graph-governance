import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.ari_compile import CompileResult, compile_component
from scripts.ari_model import ResultState
from scripts.ari_passport import PassportError, build_passport

ROOT = Path(__file__).resolve().parents[1]
APC = json.loads((ROOT / "docs/release-intelligence/apc-1.json").read_text(encoding="utf-8"))

BASE = {
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
ARTIFACT = "sha256:" + "a" * 64


class AriPassportTest(unittest.TestCase):
    def test_pass_compile_emits_exact_subject_passport(self):
        manifest = copy.deepcopy(BASE)
        result = compile_component(manifest, APC, [copy.deepcopy(EDGE)])
        passport = build_passport(manifest, result, ARTIFACT)
        self.assertEqual(passport["schema"], "release-passport/1.0")
        self.assertEqual(passport["subject"], {"component": "sentinel-engine", "version": "1.4.0"})
        self.assertEqual(passport["platform"], {"generation": 26, "release_train": "2026.09", "compatibility": "APC-1"})
        self.assertEqual(passport["conformance"]["result"], "PASS")
        self.assertEqual(passport["conformance"]["profiles"], {"verifier": "PASS"})
        self.assertEqual(passport["provenance"]["repository"], "Aftergraph/sentinel")
        self.assertEqual(passport["provenance"]["commit"], "1" * 40)
        self.assertEqual(passport["provenance"]["artifact_digest"], ARTIFACT)
        self.assertRegex(passport["provenance"]["manifest_digest"], r"^sha256:[a-f0-9]{64}$")

    def test_build_refuses_compile_result_for_different_subject(self):
        forged = CompileResult(
            state=ResultState.PASS,
            component="different-component",
            version="1.4.0",
            profile_results={"verifier": ResultState.PASS},
        )
        with self.assertRaisesRegex(PassportError, "compile result subject mismatch"):
            build_passport(copy.deepcopy(BASE), forged, ARTIFACT)

    def test_unknown_compile_refuses_passport(self):
        result = compile_component(copy.deepcopy(BASE), APC, [])
        self.assertEqual(result.state, ResultState.UNKNOWN)
        with self.assertRaisesRegex(PassportError, "requires PASS"):
            build_passport(copy.deepcopy(BASE), result, ARTIFACT)

    def test_stale_compile_refuses_passport(self):
        stale = copy.deepcopy(EDGE)
        stale["state"] = "stale"
        result = compile_component(copy.deepcopy(BASE), APC, [stale])
        self.assertEqual(result.state, ResultState.STALE)
        with self.assertRaisesRegex(PassportError, "requires PASS"):
            build_passport(copy.deepcopy(BASE), result, ARTIFACT)

    def test_fail_compile_refuses_passport(self):
        failed = copy.deepcopy(EDGE)
        failed["state"] = "fail"
        result = compile_component(copy.deepcopy(BASE), APC, [failed])
        self.assertEqual(result.state, ResultState.FAIL)
        with self.assertRaisesRegex(PassportError, "requires PASS"):
            build_passport(copy.deepcopy(BASE), result, ARTIFACT)

    def test_n_a_compile_refuses_passport(self):
        manifest = copy.deepcopy(BASE)
        manifest["compatibility"]["profiles"] = []
        manifest["compatibility"].pop("requires_edges")
        result = compile_component(manifest, APC, [])
        self.assertEqual(result.state, ResultState.N_A)
        with self.assertRaisesRegex(PassportError, "requires PASS"):
            build_passport(manifest, result, ARTIFACT)

    def test_invalid_artifact_digest_refuses(self):
        result = compile_component(copy.deepcopy(BASE), APC, [copy.deepcopy(EDGE)])
        with self.assertRaisesRegex(PassportError, "artifact digest"):
            build_passport(copy.deepcopy(BASE), result, "sha256:bad")

    def test_manifest_digest_changes_when_manifest_changes(self):
        manifest = copy.deepcopy(BASE)
        result = compile_component(manifest, APC, [copy.deepcopy(EDGE)])
        first = build_passport(manifest, result, ARTIFACT)
        changed = copy.deepcopy(BASE)
        changed["contracts"]["verdict"] = "1.1"
        changed_result = compile_component(changed, APC, [copy.deepcopy(EDGE)])
        second = build_passport(changed, changed_result, ARTIFACT)
        self.assertNotEqual(first["provenance"]["manifest_digest"], second["provenance"]["manifest_digest"])

    def test_build_is_deterministic(self):
        manifest = copy.deepcopy(BASE)
        result = compile_component(manifest, APC, [copy.deepcopy(EDGE)])
        first = json.dumps(build_passport(manifest, result, ARTIFACT), sort_keys=True, separators=(",", ":"))
        second = json.dumps(build_passport(manifest, result, ARTIFACT), sort_keys=True, separators=(",", ":"))
        self.assertEqual(first, second)

    def test_cli_emits_passport_and_exit_zero(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            manifest_path = tmp_path / "component.json"
            edge_path = tmp_path / "edge.json"
            manifest_path.write_text(json.dumps(BASE), encoding="utf-8")
            edge_path.write_text(json.dumps(EDGE), encoding="utf-8")
            proc = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts/ari_passport.py"),
                    str(manifest_path),
                    "--edge",
                    str(edge_path),
                    "--artifact-digest",
                    ARTIFACT,
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["schema"], "release-passport/1.0")
        self.assertEqual(payload["conformance"]["result"], "PASS")

    def test_cli_unknown_refuses_and_exit_three(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "component.json"
            path.write_text(json.dumps(BASE), encoding="utf-8")
            proc = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts/ari_passport.py"),
                    str(path),
                    "--artifact-digest",
                    ARTIFACT,
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
        self.assertEqual(proc.returncode, 3)
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["state"], "UNKNOWN")
        self.assertIn("requires PASS", payload["error"])

    def test_cli_invalid_artifact_digest_reports_fail_and_exit_two(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            manifest_path = tmp_path / "component.json"
            edge_path = tmp_path / "edge.json"
            manifest_path.write_text(json.dumps(BASE), encoding="utf-8")
            edge_path.write_text(json.dumps(EDGE), encoding="utf-8")
            proc = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts/ari_passport.py"),
                    str(manifest_path),
                    "--edge",
                    str(edge_path),
                    "--artifact-digest",
                    "sha256:bad",
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
        self.assertEqual(proc.returncode, 2)
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["state"], "FAIL")
        self.assertEqual(payload["conformance_state"], "PASS")
        self.assertIn("artifact digest", payload["error"])


if __name__ == "__main__":
    unittest.main()
