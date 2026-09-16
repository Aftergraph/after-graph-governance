import unittest

from scripts.circuit.run_golden_circuit import build_reality_case, validate_works_evidence


class GoldenCircuitHarnessTests(unittest.TestCase):
    def test_rejects_subject_drift(self):
        evidence = {
            "verification_subject": "execution-subject:" + "a" * 64,
            "effect_receipt_id": "ercpt_abc",
            "effect_receipt_sha256": "b" * 64,
            "effect_state": "APPLIED",
            "witness_result": "ACCEPT",
            "verifier_id": "witness-golden",
        }
        with self.assertRaises(ValueError):
            validate_works_evidence(evidence, "execution-subject:" + "c" * 64)

    def test_builds_post_effect_reobservation_from_exact_receipt(self):
        evidence = {
            "verification_subject": "execution-subject:" + "a" * 64,
            "effect_receipt_id": "ercpt_abc",
            "effect_receipt_sha256": "b" * 64,
            "effect_state": "APPLIED",
            "witness_result": "ACCEPT",
            "verifier_id": "witness-golden",
        }
        case = build_reality_case(evidence)
        self.assertTrue(case["effect_receipt_subject"].startswith("effect-receipt:ercpt_abc:sha256:"))
        self.assertEqual(case["intended_outcome"]["expected"], "HEALTHY")


if __name__ == "__main__": unittest.main()
