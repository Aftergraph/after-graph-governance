import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACTS = ROOT / "docs" / "contracts"
ARI = ROOT / "docs" / "release-intelligence"


class AriContractsTest(unittest.TestCase):
    def load(self, path: Path):
        self.assertTrue(path.is_file(), f"missing artifact: {path.relative_to(ROOT)}")
        return json.loads(path.read_text(encoding="utf-8"))

    def test_apc_1_freezes_profile_and_evidence_vocabularies(self):
        apc = self.load(ARI / "apc-1.json")
        self.assertEqual(apc["schema"], "aftergraph.apc/1")
        self.assertEqual(apc["level"], "APC-1")
        self.assertEqual(
            apc["profiles"],
            ["authority", "service", "runtime", "execution", "verifier", "product", "model", "research"],
        )
        self.assertEqual(list(apc["evidence_levels"]), ["CE0", "CE1", "CE2", "CE3", "CE4", "CE5"])

    def test_component_schema_separates_generation_compatibility_and_version(self):
        schema = self.load(CONTRACTS / "aftergraph-component" / "1.0.json")
        props = schema["properties"]
        self.assertIn("platform", props)
        self.assertIn("compatibility", props)
        self.assertIn("release", props)
        self.assertEqual(props["platform"]["properties"]["generation"]["const"], 26)
        self.assertEqual(props["compatibility"]["properties"]["level"]["const"], "APC-1")

    def test_edge_requires_subjects_relation_state_and_evidence(self):
        schema = self.load(CONTRACTS / "compatibility-edge" / "1.0.json")
        self.assertEqual(
            schema["required"],
            ["schema", "from", "to", "relation", "state", "evidence_level", "evidence"],
        )

    def test_edge_schema_requires_nonempty_evidence(self):
        schema = self.load(CONTRACTS / "compatibility-edge" / "1.0.json")
        evidence = schema["properties"]["evidence"]
        self.assertEqual(evidence.get("minItems"), 1)

    def test_passport_requires_exact_source_and_artifact_identity(self):
        schema = self.load(CONTRACTS / "release-passport" / "1.0.json")
        provenance = schema["properties"]["provenance"]
        self.assertEqual(provenance["required"], ["repository", "commit", "artifact_digest"])


class AriDiscoverabilityTest(unittest.TestCase):
    def test_cross_repo_register_names_ari_contract_families_and_owner(self):
        register = (ROOT / "docs/cross-repo-contracts.md").read_text(encoding="utf-8")
        for contract in ("aftergraph-component/1.0", "compatibility-edge/1.0", "release-passport/1.0"):
            self.assertIn(contract, register)
        self.assertIn("after-graph-governance", register)
        self.assertIn("does not grant runtime authority", register)

    def test_readme_links_release_standard_apc_and_ari(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        for expected in (
            "Aftergraph 26 · Convergence",
            "ARS/1",
            "APC-1",
            "Release Intelligence",
            "docs/superpowers/specs/2026-09-07-aftergraph-release-lifecycle-compatibility-standard-design.md",
            "docs/superpowers/specs/2026-09-07-aftergraph-release-intelligence-plane-design.md",
            "docs/release-intelligence/apc-1.json",
        ):
            self.assertIn(expected, readme)


if __name__ == "__main__":
    unittest.main()
