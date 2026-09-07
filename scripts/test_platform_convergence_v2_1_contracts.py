import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "docs/contracts/platform-convergence-v2-1/registry.json"
CORRELATION = ROOT / "docs/contracts/correlation/1.0.json"

EXPECTED_FAMILIES = [
    {"contract": "principal/1.0", "owner": "aie", "path": "spec/contracts/principal/1.0.json"},
    {"contract": "tenant/1.0", "owner": "trust-gateway", "path": "docs/contracts/tenant/1.0.json"},
    {"contract": "execution-context/1.0", "owner": "works-execution", "path": "contracts/schemas/execution-context.schema.json"},
    {"contract": "correlation/1.0", "owner": "after-graph-governance", "path": "docs/contracts/correlation/1.0.json"},
]


class PlatformConvergenceV21ContractsTest(unittest.TestCase):
    def load_json(self, path: Path):
        self.assertTrue(path.is_file(), f"missing contract artifact: {path.relative_to(ROOT)}")
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    def test_registry_freezes_exact_four_contract_families_and_owners(self):
        registry = self.load_json(REGISTRY)
        self.assertEqual(registry.get("schema_version"), "platform-convergence-v2-1/1.0")
        self.assertEqual(registry.get("families"), EXPECTED_FAMILIES)

    def test_identity_1_0_is_compatibility_only(self):
        registry = self.load_json(REGISTRY)
        self.assertEqual(registry.get("compatibility_families"), ["identity/1.0"])
        contracts = {entry["contract"] for entry in registry.get("families", [])}
        self.assertNotIn("identity/1.0", contracts)

    def test_correlation_schema_is_strict_and_requires_all_v2_1_links(self):
        schema = self.load_json(CORRELATION)
        self.assertFalse(schema.get("additionalProperties", True))
        self.assertEqual(
            schema.get("required"),
            [
                "schema",
                "execution_context_id",
                "tenant_id",
                "principal_id",
                "mission_id",
                "authority_lease_id",
                "work_id",
                "admission_decision_id",
                "trace_id",
                "action_id",
            ],
        )
        self.assertEqual(schema["properties"]["schema"]["const"], "correlation/1.0")

    def test_new_identifier_patterns_reject_wrong_shapes(self):
        schema = self.load_json(CORRELATION)
        cases = {
            "execution_context_id": ("ctx_0123456789abcdef0123456789abcdef", ["CTX_0123456789abcdef0123456789abcdef", "ctx_1234", "ctx_0123456789abcdef0123456789abcdeg"]),
            "tenant_id": ("ten_0123456789abcdef0123456789abcdef", ["ten_ABCDEF0123456789abcdef0123456789", "tenant_0123456789abcdef0123456789abcdef", "ten_0123"]),
            "principal_id": ("prn_0123456789abcdef0123456789abcdef", ["prn_0123456789ABCDEF0123456789abcdef", "principal_0123456789abcdef0123456789abcdef", "prn_0"]),
            "authority_lease_id": ("auth_0123456789abcdef0123456789abcdef", ["lse_0123456789abcdef0123456789abcdef", "AUTH_0123456789abcdef0123456789abcdef", "auth_deadbeef"]),
            "work_id": ("wrk_0123456789abcdef0123456789abcdef", ["work_0123456789abcdef0123456789abcdef", "wrk_0123456789abcdef", "wrk_0123456789abcdef0123456789ABCDEf"]),
            "admission_decision_id": ("pdr_0123456789abcdef0123456789abcdef", ["pdr_0123456789abcdef", "PDR_0123456789abcdef0123456789abcdef", "dec_0123456789abcdef0123456789abcdef"]),
            "trace_id": ("trc_0123456789abcdef0123456789abcdef", ["trace_0123456789abcdef0123456789abcdef", "trc_0123456789abcdef0123456789abcde-", "trc_0123"]),
            "action_id": ("act_0123456789abcdef0123456789abcdef", ["action_0123456789abcdef0123456789abcdef", "act_0123456789ABCDEF0123456789abcdef", "act_0123"]),
        }
        for field, (valid, invalid_values) in cases.items():
            pattern = schema["properties"][field]["pattern"]
            compiled = re.compile(pattern)
            self.assertRegex(valid, compiled, field)
            for invalid in invalid_values:
                self.assertIsNone(compiled.fullmatch(invalid), f"{field} accepted {invalid!r}")


if __name__ == "__main__":
    unittest.main()
