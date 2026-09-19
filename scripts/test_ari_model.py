import unittest

from scripts.ari_model import (
    EvidenceLevel,
    ResultState,
    canonical_digest,
    evidence_meets,
    validate_component,
    validate_edge,
    validate_passport,
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

    def test_component_rejects_unhashable_lifecycle_and_profile(self):
        doc = {
            **VALID_COMPONENT,
            "release": {**VALID_COMPONENT["release"], "lifecycle": ["stable"]},
            "compatibility": {**VALID_COMPONENT["compatibility"], "profiles": [{"verifier": True}]},
        }
        errors = validate_component(doc)
        self.assertTrue(any(e.startswith("unsupported lifecycle:") for e in errors), errors)
        self.assertTrue(any(e.startswith("unsupported APC-1 profile:") for e in errors), errors)

    def test_edge_rejects_unhashable_relation_and_state(self):
        doc = {**VALID_EDGE, "relation": {"requires": True}, "state": ["pass"]}
        errors = validate_edge(doc)
        self.assertTrue(any(e.startswith("unsupported edge relation:") for e in errors), errors)
        self.assertTrue(any(e.startswith("unsupported edge state:") for e in errors), errors)

    def test_passport_rejects_unhashable_conformance_state(self):
        doc = {
            "schema": "release-passport/1.0",
            "subject": {"component": "sentinel-engine", "version": "1.4.0"},
            "platform": {
                "generation": 26,
                "release_train": "2026.09",
                "compatibility": "APC-1",
            },
            "conformance": {
                "result": "PASS",
                "profiles": {"verifier": {"PASS": True}},
                "evidence": [],
            },
            "provenance": {
                "repository": "Aftergraph/sentinel",
                "commit": "1" * 40,
                "artifact_digest": "sha256:" + "a" * 64,
                "manifest_digest": "sha256:" + "b" * 64,
            },
        }
        errors = validate_passport(doc)
        self.assertTrue(
            any(e.startswith("unsupported conformance state for verifier:") for e in errors),
            errors,
        )

    def test_component_version_rejects_whitespace_and_control_characters(self):
        # thread 6kC7ar: SELECTOR_RE addresses a release through '.', which
        # cannot match a newline, and the CLI prints the version inline, so a
        # whitespace- or control-bearing version is unaddressable and forges
        # extra output lines. The grammar forbids them -- while '#' and '@'
        # stay legal, because the selector splits on its final anchor.
        for bad in ("1.4.0\n", "1.4.0 ", "1.4\t0", "1.4\r0", "1.4.0\x00", "1.4.0\x7f"):
            doc = {
                **VALID_COMPONENT,
                "release": {**VALID_COMPONENT["release"], "version": bad},
            }
            errors = validate_component(doc)
            self.assertTrue(
                any(e.startswith("release.version must match") for e in errors),
                (bad, errors),
            )
        for good in ("1.4.0#rc.1", "1.4.0@beta", "1.4.0:rc+1", "26.9.0-rc.1"):
            doc = {
                **VALID_COMPONENT,
                "release": {**VALID_COMPONENT["release"], "version": good},
            }
            self.assertEqual(validate_component(doc), [], good)

    def test_required_edge_target_version_shares_the_grammar(self):
        target = {"component": "works", "version": "0.5.1\n", "commit": "2" * 40}
        doc = {
            **VALID_COMPONENT,
            "compatibility": {
                **VALID_COMPONENT["compatibility"],
                "requires_edges": [target],
            },
        }
        errors = validate_component(doc)
        self.assertTrue(
            any("compatibility.requires_edges[0].version must match" in e for e in errors),
            errors,
        )

    def test_edge_endpoint_and_passport_subject_versions_share_the_grammar(self):
        edge = {**VALID_EDGE, "to": {**VALID_EDGE["to"], "version": "0.5.1 "}}
        errors = validate_edge(edge)
        self.assertTrue(any("to.version must match" in e for e in errors), errors)

        passport = {
            "schema": "release-passport/1.0",
            "subject": {"component": "sentinel-engine", "version": "1.4.0\n"},
            "platform": {
                "generation": 26,
                "release_train": "2026.09",
                "compatibility": "APC-1",
            },
            "conformance": {
                "result": "PASS",
                "profiles": {"verifier": "PASS"},
                "evidence": [],
            },
            "provenance": {
                "repository": "Aftergraph/sentinel",
                "commit": "1" * 40,
                "artifact_digest": "sha256:" + "a" * 64,
                "manifest_digest": "sha256:" + "b" * 64,
            },
        }
        errors = validate_passport(passport)
        self.assertTrue(any("subject.version must match" in e for e in errors), errors)


if __name__ == "__main__":
    unittest.main()
