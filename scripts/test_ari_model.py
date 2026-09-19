import unittest

from scripts.ari_model import (
    EvidenceLevel,
    ResultState,
    canonical_digest,
    evidence_meets,
    validate_component,
    validate_edge,
)


VALID_COMPONENT = {
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
    "contracts": {"correlation": "1.0"},
    "provenance": {
        "repository": "Aftergraph/sentinel",
        "commit": "1" * 40,
    },
}

VALID_EDGE = {
    "schema": "compatibility-edge/1.0",
    "from": {"component": "sentinel-engine", "version": "1.4.0", "commit": "1" * 40},
    "to": {"component": "works", "version": "0.5.1", "commit": "2" * 40},
    "relation": "tested-with",
    "state": "pass",
    "evidence_level": "CE3",
    "evidence": [{"kind": "test-receipt", "ref": "sha256:" + "3" * 64}],
}


class AriModelTest(unittest.TestCase):
    def test_result_states_are_distinct(self):
        self.assertEqual(ResultState.PASS.value, "PASS")
        self.assertEqual(ResultState.FAIL.value, "FAIL")
        self.assertEqual(ResultState.UNKNOWN.value, "UNKNOWN")
        self.assertEqual(ResultState.STALE.value, "STALE")
        self.assertEqual(ResultState.N_A.value, "N/A")

    def test_evidence_order_is_monotonic(self):
        self.assertTrue(evidence_meets("CE3", "CE2"))
        self.assertTrue(evidence_meets("CE2", "CE2"))
        self.assertFalse(evidence_meets("CE1", "CE2"))
        self.assertEqual(EvidenceLevel.CE5.value, 5)

    def test_digest_is_key_order_independent(self):
        self.assertEqual(
            canonical_digest({"a": 1, "b": 2}),
            canonical_digest({"b": 2, "a": 1}),
        )

    def test_component_rejects_unknown_profile(self):
        doc = {**VALID_COMPONENT, "compatibility": {**VALID_COMPONENT["compatibility"], "profiles": ["banana"]}}
        self.assertIn("unsupported APC-1 profile: banana", validate_component(doc))

    def test_component_rejects_malformed_commit(self):
        doc = {**VALID_COMPONENT, "provenance": {**VALID_COMPONENT["provenance"], "commit": "abc"}}
        self.assertIn("provenance.commit must be 40 lowercase hex characters", validate_component(doc))

    def test_component_rejects_duplicate_required_edge_targets(self):
        target = {"component": "works", "version": "0.5.1", "commit": "2" * 40}
        doc = {
            **VALID_COMPONENT,
            "compatibility": {
                **VALID_COMPONENT["compatibility"],
                "requires_edges": [target, dict(target)],
            },
        }
        self.assertIn(
            "duplicate compatibility.requires_edges target: works@0.5.1#222222222222",
            validate_component(doc),
        )

    def test_valid_component_has_no_errors(self):
        self.assertEqual(validate_component(VALID_COMPONENT), [])

    def test_edge_rejects_unknown_state_and_bad_endpoint(self):
        doc = {**VALID_EDGE, "state": "maybe", "to": {**VALID_EDGE["to"], "commit": "XYZ"}}
        errors = validate_edge(doc)
        self.assertIn("unsupported edge state: maybe", errors)
        self.assertIn("to.commit must be 40 lowercase hex characters", errors)

    def test_valid_edge_has_no_errors(self):
        self.assertEqual(validate_edge(VALID_EDGE), [])


if __name__ == "__main__":
    unittest.main()
