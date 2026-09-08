import unittest

from scripts.ari_graph import CompatibilityGraph, Endpoint
from scripts.ari_model import ResultState

LEFT = Endpoint("sentinel-engine", "1.4.0", "1" * 40)
RIGHT = Endpoint("works", "0.5.1", "2" * 40)


def edge(*, relation="tested-with", state="pass", evidence_level="CE3", left=LEFT, right=RIGHT):
    return {
        "schema": "compatibility-edge/1.0",
        "from": {"component": left.component, "version": left.version, "commit": left.commit},
        "to": {"component": right.component, "version": right.version, "commit": right.commit},
        "relation": relation,
        "state": state,
        "evidence_level": evidence_level,
        "evidence": [{"kind": "test-receipt", "ref": "sha256:" + "3" * 64}],
    }


class AriGraphTest(unittest.TestCase):
    def test_ce3_pass_meets_ce2(self):
        graph = CompatibilityGraph([edge(evidence_level="CE3")])
        self.assertEqual(graph.best_state(LEFT, RIGHT, "CE2"), ResultState.PASS)

    def test_pass_below_minimum_is_unknown(self):
        graph = CompatibilityGraph([edge(evidence_level="CE1")])
        self.assertEqual(graph.best_state(LEFT, RIGHT, "CE2"), ResultState.UNKNOWN)

    def test_explicit_fail_wins(self):
        graph = CompatibilityGraph([edge(state="pass"), edge(state="fail", evidence_level="CE1")])
        self.assertEqual(graph.best_state(LEFT, RIGHT, "CE2"), ResultState.FAIL)

    def test_incompatible_relation_is_fail_closed(self):
        graph = CompatibilityGraph([edge(relation="incompatible-with", state="pass", evidence_level="CE1")])
        self.assertEqual(graph.best_state(LEFT, RIGHT, "CE2"), ResultState.FAIL)

    def test_incompatible_with_is_symmetric(self):
        graph = CompatibilityGraph([edge(relation="incompatible-with", state="pass", evidence_level="CE1")])
        self.assertEqual(graph.best_state(RIGHT, LEFT, "CE2"), ResultState.FAIL)

    def test_stale_wins_over_pass(self):
        graph = CompatibilityGraph([edge(state="pass"), edge(state="stale", evidence_level="CE3")])
        self.assertEqual(graph.best_state(LEFT, RIGHT, "CE2"), ResultState.STALE)

    def test_no_edge_is_unknown(self):
        graph = CompatibilityGraph()
        self.assertEqual(graph.best_state(LEFT, RIGHT, "CE2"), ResultState.UNKNOWN)

    def test_tested_with_is_symmetric(self):
        graph = CompatibilityGraph([edge(relation="tested-with")])
        self.assertEqual(graph.best_state(RIGHT, LEFT, "CE2"), ResultState.PASS)

    def test_directional_requires_does_not_reverse_match(self):
        graph = CompatibilityGraph([edge(relation="requires")])
        self.assertEqual(graph.best_state(RIGHT, LEFT, "CE2"), ResultState.UNKNOWN)

    def test_not_applicable_only_is_n_a(self):
        graph = CompatibilityGraph([edge(state="not-applicable", evidence_level="CE0")])
        self.assertEqual(graph.best_state(LEFT, RIGHT, "CE2"), ResultState.N_A)

    def test_invalid_edge_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "unsupported edge state"):
            CompatibilityGraph([edge(state="banana")])


if __name__ == "__main__":
    unittest.main()
