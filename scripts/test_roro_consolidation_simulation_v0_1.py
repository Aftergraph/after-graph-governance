import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REALITY = ROOT / 'docs/system-reality'

class ConsolidationSimulationTests(unittest.TestCase):
    def test_candidates_cover_2_3_4_5_workspaces_exactly_once(self):
        candidates=json.loads((REALITY/'consolidation-candidates.json').read_text())
        registry=json.loads((REALITY/'component-registry.json').read_text())
        repos={x['full_name'].split('/',1)[1] for x in registry['repositories']}
        self.assertEqual({c['workspace_count'] for c in candidates['candidates']},{2,3,4,5})
        for c in candidates['candidates']:
            assigned=[r for w in c['workspaces'] for r in w['repositories']]
            self.assertEqual(set(assigned),repos,c['candidate_id'])
            self.assertEqual(len(assigned),len(set(assigned)),c['candidate_id'])

    def test_simulation_is_multidimensional_not_ranked(self):
        data=json.loads((REALITY/'consolidation-simulation.json').read_text())
        text=json.dumps(data).lower()
        self.assertNotIn('overall_score',text)
        self.assertNotIn('winner',text)
        self.assertNotIn('recommended',text)
        for c in data['candidates']:
            self.assertIn('cross_workspace_dependency_edges',c['dimensions'])
            self.assertIn('trust_boundary_colocations',c['dimensions'])
            self.assertIn('legacy_canonical_colocations',c['dimensions'])
            self.assertIn('research_production_colocations',c['dimensions'])
            self.assertIn('domain_platform_colocations',c['dimensions'])
            self.assertEqual(c['hard_blockers'],[])

    def test_visibility_purity_is_hard_invariant(self):
        data=json.loads((REALITY/'consolidation-simulation.json').read_text())
        for c in data['candidates']:
            self.assertEqual(c['dimensions']['mixed_visibility_workspaces'],0,c['candidate_id'])

    def test_more_separation_exposes_specific_tradeoffs(self):
        data=json.loads((REALITY/'consolidation-simulation.json').read_text())
        by_count={c['workspace_count']:c for c in data['candidates']}
        self.assertGreater(by_count[2]['dimensions']['research_production_colocations'],by_count[3]['dimensions']['research_production_colocations'])
        self.assertGreater(by_count[3]['dimensions']['legacy_canonical_colocations'],by_count[4]['dimensions']['legacy_canonical_colocations'])
        self.assertEqual(by_count[4]['dimensions']['legacy_canonical_colocations'],0)
        self.assertEqual(by_count[5]['dimensions']['legacy_canonical_colocations'],0)
        self.assertGreater(by_count[4]['dimensions']['trust_boundary_colocations'],by_count[5]['dimensions']['trust_boundary_colocations'])

    def test_simulator_requires_scoped_ready_gate(self):
        gate=json.loads((REALITY/'coverage-gate.json').read_text())
        self.assertEqual(gate['gate'],'SOURCE_TOPOLOGY_CONSOLIDATION')
        self.assertEqual(gate['scope'],'SOURCE_TOPOLOGY_ONLY')
        self.assertEqual(gate['decision'],'READY')
        result=subprocess.run([sys.executable,str(ROOT/'scripts/roro/simulate_consolidation.py')],cwd=ROOT,text=True,capture_output=True)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)

if __name__=='__main__':
    unittest.main(verbosity=2)

class CandidateGenerationTests(unittest.TestCase):
    def test_candidate_generator_is_deterministic(self):
        script=ROOT/'scripts/roro/generate_consolidation_candidates.py'
        before=(REALITY/'consolidation-candidates.json').read_bytes()
        r=subprocess.run([sys.executable,str(script)],cwd=ROOT,text=True,capture_output=True)
        self.assertEqual(r.returncode,0,r.stdout+r.stderr)
        self.assertEqual((REALITY/'consolidation-candidates.json').read_bytes(),before)

    def test_strict_boundary_lower_bound_is_explicit_not_recommendation(self):
        data=json.loads((REALITY/'consolidation-boundary-analysis.json').read_text())
        self.assertGreaterEqual(data['strict_hypothesis']['minimum_workspace_lower_bound'],7)
        self.assertTrue(data['policy']['lower_bound_is_not_recommendation'])
        self.assertNotIn('recommended',json.dumps(data).lower())
        reasons={x['constraint'] for x in data['strict_hypothesis']['constraints']}
        self.assertIn('visibility_purity',reasons)
        self.assertIn('legacy_isolation',reasons)
        self.assertIn('research_isolation',reasons)
        self.assertIn('trust_boundary_separation',reasons)

class ConsolidationContractTests(unittest.TestCase):
    def test_consolidation_contracts_are_registered(self):
        register=(ROOT/'docs/cross-repo-contracts.md').read_text(encoding='utf-8')
        for contract in ('roro-consolidation-candidates/0.1','roro-consolidation-simulation/0.1','roro-consolidation-boundary-analysis/0.1'):
            self.assertIn(f'`{contract}`',register)

    def test_consolidation_schemas_exist(self):
        for name in ('consolidation-candidates.schema.json','consolidation-simulation.schema.json','consolidation-boundary-analysis.schema.json'):
            path=ROOT/'docs/contracts/roro/0.1'/name
            self.assertTrue(path.is_file(),path)
            json.loads(path.read_text(encoding='utf-8'))
