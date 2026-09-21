import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACTS = ROOT / "docs" / "contracts" / "jev-sidecar"


class JevSidecarContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = json.loads((CONTRACTS / "0.1.registry.json").read_text())
        cls.observation = json.loads((CONTRACTS / "0.1.observation.schema.json").read_text())
        cls.promotion = json.loads((CONTRACTS / "0.1.promotion.schema.json").read_text())

    def test_registry_identity_and_law(self):
        self.assertEqual(self.registry["schema"], "jev-decision-registry/0.1")
        self.assertEqual(
            self.registry["law"],
            "Jev may choose among permitted options. Jev may never make an option permitted.",
        )
        self.assertEqual(self.registry["defaults"]["new_class_mode"], "shadow")
        self.assertTrue(
            self.registry["defaults"]["guarded_requires_class_specific_promotion"]
        )

    def test_decision_classes_are_unique_and_deterministically_bounded(self):
        classes = self.registry["classes"]
        ids = [item["id"] for item in classes]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertGreaterEqual(len(ids), 10)

        forbidden_owners = {"jev", "typesafe", "typesafe-ai"}
        for item in classes:
            self.assertEqual(item["candidate_set"]["source"], "deterministic")
            self.assertNotIn(item["owner"], forbidden_owners)
            self.assertNotIn(item["effect_owner"], forbidden_owners)
            self.assertNotIn(item["verifier_owner"], forbidden_owners)
            self.assertIn(item["initial_mode"], {"disabled", "shadow", "guarded"})

    def test_guarded_classes_are_evidence_pinned_and_limited_to_runtime_v1(self):
        guarded = [x for x in self.registry["classes"] if x["initial_mode"] == "guarded"]
        self.assertEqual(
            {x["id"] for x in guarded},
            {
                "runtime.placement.rank",
                "runtime.recovery.route",
                "runtime.topology.select",
            },
        )
        for item in guarded:
            self.assertTrue(item["promotion_evidence_ref"])
            self.assertTrue(item["promotion_evidence_ref"].startswith("runtime:"))

        shadow = [x for x in self.registry["classes"] if x["initial_mode"] == "shadow"]
        self.assertGreater(len(shadow), 0)
        for item in shadow:
            self.assertNotIn("promotion_evidence_ref", item)

    def test_observation_contract_is_non_authoritative(self):
        props = self.observation["properties"]
        for field in (
            "authorizes_effect",
            "claims_authority",
            "canonical_evidence",
            "independent_verification",
        ):
            self.assertEqual(props[field], {"const": False})
            self.assertIn(field, self.observation["required"])

        guarded_rule = self.observation["allOf"][0]
        self.assertEqual(
            guarded_rule["if"]["properties"]["effective_mode"]["const"], "guarded"
        )
        self.assertIn("promotion_evidence_ref", guarded_rule["then"]["required"])

    def test_promotion_is_class_specific_and_prospectively_bound(self):
        required = set(self.promotion["required"])
        for field in (
            "decision_class",
            "provider",
            "model",
            "source_revision",
            "artifact_digest",
            "question_contract_digest",
            "projection_contract_digest",
            "holdout_ref",
            "holdout_digest",
            "sample_size",
            "confidence_floor",
            "harmful_overrides",
            "authority_sensitive_new_errors",
            "secret_scan",
            "immutable_after_freeze",
            "status",
        ):
            self.assertIn(field, required)

        props = self.promotion["properties"]
        self.assertEqual(props["sample_size"]["minimum"], 30)
        self.assertEqual(props["secret_scan"], {"const": "clean"})
        self.assertEqual(props["immutable_after_freeze"], {"const": True})
        self.assertEqual(props["status"]["enum"], ["qualified", "rejected"])


if __name__ == "__main__":
    unittest.main()
