import json
import unittest
from pathlib import Path

from scripts.ari_model import IDENTIFIER_RE, VERSION_RE

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

    def test_passport_requires_exact_source_artifact_and_manifest_identity(self):
        schema = self.load(CONTRACTS / "release-passport" / "1.0.json")
        provenance = schema["properties"]["provenance"]
        self.assertEqual(
            provenance["required"],
            ["repository", "commit", "artifact_digest", "manifest_digest"],
        )

    def test_passport_schema_only_allows_positive_profile_states(self):
        schema = self.load(CONTRACTS / "release-passport" / "1.0.json")
        profiles = schema["properties"]["conformance"]["properties"]["profiles"]
        self.assertEqual(profiles.get("minProperties"), 1)
        self.assertEqual(profiles["additionalProperties"]["enum"], ["PASS", "N/A"])

    def test_passport_profile_keys_are_pinned_to_the_frozen_apc_1_vocabulary(self):
        # Three surfaces name the APC-1 profile set: apc-1.json freezes it, the
        # component contract pins it as an array enum, and the passport contract
        # has to pin it as object key names. Asserting all three against the
        # frozen list is what stops them drifting apart silently.
        apc = self.load(ARI / "apc-1.json")
        frozen = apc["profiles"]

        passport = self.load(CONTRACTS / "release-passport" / "1.0.json")
        profiles = passport["properties"]["conformance"]["properties"]["profiles"]
        self.assertEqual(profiles["propertyNames"]["enum"], frozen)

        component = self.load(CONTRACTS / "aftergraph-component" / "1.0.json")
        self.assertEqual(
            component["properties"]["compatibility"]["properties"]["profiles"]["items"]["enum"],
            frozen,
        )

    def test_passport_subject_component_shares_the_identifier_grammar(self):
        # validate_passport() runs subject.component through _validate_identifier
        # (scripts/ari_model.py:318), so the published contract has to demand the
        # same grammar or a contract-valid passport is refused at Registry
        # ingestion (thread 6kC1X6). The component contract has always pinned
        # identity.component to IDENTIFIER_RE; the passport contract was the weak
        # sibling. Comparing against IDENTIFIER_RE.pattern rather than a literal
        # is what keeps the three surfaces from drifting apart silently.
        passport = self.load(CONTRACTS / "release-passport" / "1.0.json")
        subject_component = passport["properties"]["subject"]["properties"]["component"]
        component = self.load(CONTRACTS / "aftergraph-component" / "1.0.json")
        identity_component = component["properties"]["identity"]["properties"]["component"]
        self.assertEqual(subject_component["pattern"], IDENTIFIER_RE.pattern)
        self.assertEqual(identity_component["pattern"], IDENTIFIER_RE.pattern)

    def test_every_published_version_field_shares_the_selector_compatible_grammar(self):
        # thread 6kC7ar: the exact selector is component@version#40hexcommit and
        # its version group is '.', which cannot match a newline. Every contract
        # version field therefore has to carry the same whitespace/control-free
        # grammar the reference implementation enforces, or a registry-valid
        # document becomes unaddressable. Comparing against VERSION_RE.pattern
        # rather than a literal is what keeps the five fields and the model from
        # drifting apart silently.
        component = self.load(CONTRACTS / "aftergraph-component" / "1.0.json")
        edge = self.load(CONTRACTS / "compatibility-edge" / "1.0.json")
        passport = self.load(CONTRACTS / "release-passport" / "1.0.json")
        rbom = self.load(CONTRACTS / "rbom" / "0.1.json")
        fields = {
            "release.version": component["properties"]["release"]["properties"]["version"],
            "requires_edges.version": component["properties"]["compatibility"]["properties"]["requires_edges"]["items"]["properties"]["version"],
            "endpoint.version": edge["$defs"]["endpoint"]["properties"]["version"],
            "subject.version": passport["properties"]["subject"]["properties"]["version"],
            "rbom.component.version": rbom["$defs"]["component"]["properties"]["version"],
        }
        self.assertEqual(len(fields), 5)
        for label, schema in fields.items():
            with self.subTest(field=label):
                self.assertEqual(schema["pattern"], VERSION_RE.pattern)

    def test_ari_workflow_path_filters_cover_every_discoverability_gated_document(self):
        # AriDiscoverabilityTest reads the cross-repo register and two frozen ARI
        # design specs. A PR touching only those files matched neither trigger, so
        # the suite protecting them was skipped (thread 6kC1X9). Partition the file
        # on the indented push key -- a bare 'push:' substring also occurs inside
        # 'pull_request:' -- and demand each gated path in both sections.
        workflow = (
            ROOT / ".github" / "workflows" / "release-intelligence.yml"
        ).read_text(encoding="utf-8")
        gated = (
            "docs/cross-repo-contracts.md",
            "docs/superpowers/specs/2026-09-07-aftergraph-release-intelligence-plane-design.md",
            "docs/superpowers/specs/2026-09-07-aftergraph-release-lifecycle-compatibility-standard-design.md",
        )
        pull_request_section, _, push_section = workflow.partition("\n  push:")
        self.assertIn("  pull_request:", pull_request_section)
        self.assertTrue(push_section.strip(), "the push trigger section is empty")
        for path in gated:
            with self.subTest(path=path):
                self.assertIn(f"'{path}'", pull_request_section)
                self.assertIn(f"'{path}'", push_section)

    def test_release_registry_contract_is_derived_and_digest_bound(self):
        schema = self.load(CONTRACTS / "release-registry" / "1.0.json")
        self.assertEqual(schema["properties"]["schema"]["const"], "release-registry/1.0")
        entry = schema["$defs"]["entry"]
        self.assertEqual(entry["required"], ["kind", "digest", "document"])
        self.assertFalse(entry["additionalProperties"])
        self.assertEqual(entry["properties"]["digest"]["pattern"], "^sha256:[a-f0-9]{64}$")

    def test_release_registry_entry_binds_kind_to_the_document_schema_discriminator(self):
        schema = self.load(CONTRACTS / "release-registry" / "1.0.json")
        entry = schema["$defs"]["entry"]
        self.assertEqual(entry["properties"]["document"]["required"], ["schema"])
        self.assertEqual(
            {
                branch["properties"]["kind"]["const"]:
                    branch["properties"]["document"]["properties"]["schema"]["const"]
                for branch in entry["oneOf"]
            },
            {
                "component": "aftergraph-component/1.0",
                "edge": "compatibility-edge/1.0",
                "passport": "release-passport/1.0",
            },
        )

    def test_rbom_contract_separates_inventory_from_verification(self):
        schema = self.load(CONTRACTS / "rbom" / "0.1.json")
        self.assertEqual(schema["properties"]["schema"]["const"], "rbom/0.1")
        self.assertIn("verification", schema["properties"])
        self.assertEqual(
            schema["properties"]["verification"]["properties"]["state"]["enum"],
            ["VERIFIED", "PARTIAL", "UNVERIFIED"],
        )

    def test_rbom_contract_binds_each_verification_state_to_its_passport_evidence(self):
        schema = self.load(CONTRACTS / "rbom" / "0.1.json")
        bound = {
            branch["properties"]["verification"]["properties"]["state"]["const"]: branch[
                "properties"
            ]["verification"]["properties"]["passport_count"]
            for branch in schema["oneOf"]
        }
        self.assertEqual(bound, {
            "VERIFIED": {"type": "integer", "minimum": 1},
            "PARTIAL": {"type": "integer", "minimum": 1},
            "UNVERIFIED": {"const": 0},
        })
        by_state = {
            branch["properties"]["verification"]["properties"]["state"]["const"]: branch
            for branch in schema["oneOf"]
        }
        self.assertEqual(
            by_state["VERIFIED"]["properties"]["components"]["items"]["required"],
            ["artifact_digest", "passport_digest"],
        )
        # UNVERIFIED must forbid the digests on the rows, not just on the count:
        # a consumer reading only the verification object would otherwise accept
        # passport evidence that contradicts the declared absence of evidence.
        self.assertEqual(
            by_state["UNVERIFIED"]["properties"]["components"]["items"]["not"],
            {
                "anyOf": [
                    {"required": ["artifact_digest"]},
                    {"required": ["passport_digest"]},
                ]
            },
        )
        # PARTIAL is existential, not universal: at least one row must carry the
        # paired digests, while which rows do stays owned by the reference
        # builder. `contains` says that; `items` would collapse PARTIAL into
        # VERIFIED.
        self.assertEqual(
            by_state["PARTIAL"]["properties"]["components"]["contains"],
            {"required": ["artifact_digest", "passport_digest"]},
        )
        self.assertNotIn("items", by_state["PARTIAL"]["properties"]["components"])
        self.assertEqual(schema["properties"]["platform"]["properties"]["generation"]["const"], 26)
        self.assertEqual(schema["properties"]["platform"]["properties"]["compatibility"]["const"], "APC-1")


class AriDiscoverabilityTest(unittest.TestCase):
    def test_cross_repo_register_names_all_ari_phase1_contract_families_and_owner(self):
        register = (ROOT / "docs/cross-repo-contracts.md").read_text(encoding="utf-8")
        for contract in (
            "aftergraph-component/1.0",
            "compatibility-edge/1.0",
            "release-passport/1.0",
            "release-registry/1.0",
            "rbom/0.1",
        ):
            self.assertIn(contract, register)
        self.assertIn("after-graph-governance", register)
        self.assertIn("does not grant runtime authority", register)

    def test_canonical_surfaces_link_phase1_contracts_and_cli_surfaces(self):
        register = (ROOT / "docs/cross-repo-contracts.md").read_text(encoding="utf-8")
        release_design = (
            ROOT
            / "docs/superpowers/specs/2026-09-07-aftergraph-release-lifecycle-compatibility-standard-design.md"
        ).read_text(encoding="utf-8")
        ari_design = (
            ROOT
            / "docs/superpowers/specs/2026-09-07-aftergraph-release-intelligence-plane-design.md"
        ).read_text(encoding="utf-8")

        for expected in (
            "aftergraph-component/1.0",
            "compatibility-edge/1.0",
            "release-passport/1.0",
            "release-registry/1.0",
            "rbom/0.1",
        ):
            self.assertIn(expected, register)
        self.assertIn("APC-1", release_design)
        self.assertIn("Aftergraph Release Intelligence", ari_design)
        for path in (
            ARI / "apc-1.json",
            ROOT / "docs/contracts/release-registry/1.0.json",
            ROOT / "docs/contracts/rbom/0.1.json",
            ROOT / "scripts/ari_registry.py",
            ROOT / "scripts/ari_rbom.py",
            ROOT / "scripts/ari_query.py",
        ):
            self.assertTrue(path.is_file(), path)

    def test_release_intelligence_workflow_gates_phase1_contracts(self):
        workflow = (ROOT / ".github/workflows/release-intelligence.yml").read_text(encoding="utf-8")
        for expected in (
            "docs/contracts/release-registry/**",
            "docs/contracts/rbom/**",
            "python -m json.tool docs/contracts/release-registry/1.0.json",
            "python -m json.tool docs/contracts/rbom/0.1.json",
        ):
            self.assertIn(expected, workflow)


if __name__ == "__main__":
    unittest.main()