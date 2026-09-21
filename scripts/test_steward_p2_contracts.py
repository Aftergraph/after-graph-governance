import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "docs/contracts/dispatch-acceptance/2.0.json"
REGISTRY = ROOT / "docs/steward/steward-p2-contract-registry.json"


class StewardP2ContractTest(unittest.TestCase):
    def load(self, path):
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    def test_dispatch_v2_is_owned_by_works_and_additive(self):
        registry = self.load(REGISTRY)
        entry = registry["contracts"][0]
        self.assertEqual(entry["contract"], "dispatch.acceptance/2.0")
        self.assertEqual(entry["owner"], "works-execution")
        self.assertEqual(entry["compatibility"]["reads"], ["dispatch.acceptance/1.0"])
        self.assertEqual(entry["compatibility"]["writes"], "dispatch.acceptance/2.0")

    def test_dispatch_v2_has_no_authority_epoch_semantics(self):
        schema = self.load(SCHEMA)
        encoded = json.dumps(schema, sort_keys=True)
        self.assertNotIn("authority_epoch", encoded)
        request = schema["$defs"]["request"]
        self.assertIn("authority_lease_id", request["required"])
        self.assertIn("admission_decision_id", request["required"])

    def test_request_cannot_supply_works_minted_correlation_or_future_subject(self):
        request = self.load(SCHEMA)["$defs"]["request"]
        props = request["properties"]
        self.assertNotIn("execution_context_id", props)
        self.assertNotIn("trace_id", props)
        self.assertNotIn("worker_id", props)
        self.assertNotIn("verification_subject", props)
        self.assertNotIn("verification_subject", request["required"])
        self.assertFalse(request["additionalProperties"])

    def test_subject_binding_is_post_effect_exact_git_subject(self):
        schema = self.load(SCHEMA)
        binding = schema["$defs"]["subject_binding"]
        self.assertEqual(
            binding["properties"]["schema"]["const"],
            "dispatch.verification-subject/1.0",
        )
        self.assertEqual(
            binding["properties"]["subject"]["pattern"],
            r"^git:[A-Za-z0-9._-]+/[A-Za-z0-9._-]+@[a-f0-9]{40}$",
        )
        for field in ["works_execution_id", "attempt_id", "effect_id", "causal_id", "subject"]:
            self.assertIn(field, binding["required"])
        self.assertFalse(binding["additionalProperties"])

    def test_acceptance_materializes_full_execution_context(self):
        schema = self.load(SCHEMA)
        context = schema["$defs"]["execution_context"]
        self.assertEqual(context["properties"]["schema"]["const"], "execution-context/1.0")
        for field in [
            "execution_context_id", "organization_id", "tenant_id", "principal_id",
            "mission_id", "authority_lease_id", "work_id", "worker_id",
            "worker_lease_id", "admission_decision_id", "trace_id"
        ]:
            self.assertIn(field, context["required"])

    def test_worker_and_authority_lease_grammars_are_distinct(self):
        props = self.load(SCHEMA)["$defs"]["request"]["properties"]
        self.assertEqual(props["authority_lease_id"]["pattern"], "^auth_[a-f0-9]{32}$")
        self.assertEqual(props["worker_lease_id"]["pattern"], "^lse_[a-f0-9]{32}$")


if __name__ == "__main__":
    unittest.main()
