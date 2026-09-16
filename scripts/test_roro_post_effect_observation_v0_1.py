import json
import unittest
from pathlib import Path

from scripts.roro.reobserve_effect import reduce_post_effect_observation

ROOT = Path(__file__).resolve().parents[1]


def base_case():
    return {
        "schema_version": "roro-post-effect-observation-input/0.1",
        "effect_receipt_subject": "effect-receipt:ercpt_abc:sha256:" + "a" * 64,
        "intended_outcome": {"subject": "service/works-api", "predicate": "health", "expected": "HEALTHY"},
        "before": {"value": "DEGRADED", "epistemic_status": "OBSERVED", "observed_at": "2026-09-16T18:00:00Z"},
        "after": {"value": "HEALTHY", "epistemic_status": "OBSERVED", "observed_at": "2026-09-16T18:00:10Z"},
        "max_age_seconds": 60,
        "evaluated_at": "2026-09-16T18:00:20Z",
    }


class PostEffectObservationTests(unittest.TestCase):
    def test_matching_fresh_after_state_produces_verified_delta(self):
        out = reduce_post_effect_observation(base_case())
        self.assertEqual(out["classification"], "MATCHED")
        self.assertEqual(out["epistemic_status"], "VERIFIED")
        self.assertTrue(out["effect_subject_preserved"])

    def test_diverged_after_state_is_not_verified(self):
        case = base_case(); case["after"]["value"] = "DEGRADED"
        out = reduce_post_effect_observation(case)
        self.assertEqual(out["classification"], "DIVERGED")
        self.assertEqual(out["epistemic_status"], "OBSERVED")

    def test_stale_or_unknown_after_state_fails_closed(self):
        stale = base_case(); stale["after"]["observed_at"] = "2026-09-16T17:00:00Z"
        self.assertEqual(reduce_post_effect_observation(stale)["classification"], "STALE")
        unknown = base_case(); unknown["after"]["epistemic_status"] = "UNKNOWN"
        self.assertEqual(reduce_post_effect_observation(unknown)["classification"], "INDETERMINATE")

    def test_subject_must_be_exact_effect_receipt_subject(self):
        case = base_case(); case["effect_receipt_subject"] = "effect/1"
        with self.assertRaises(ValueError): reduce_post_effect_observation(case)

    def test_registered_contract_and_fixture_exist(self):
        register = (ROOT / "docs/cross-repo-contracts.md").read_text()
        self.assertIn("`roro-post-effect-observation/0.1`", register)
        data = json.loads((ROOT / "docs/system-reality/post-effect-observation-vectors.json").read_text())
        self.assertEqual(data["schema_version"], "roro-post-effect-observation-vectors/0.1")


if __name__ == "__main__": unittest.main()
