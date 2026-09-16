import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
REALITY=ROOT/'docs/system-reality'

class ComponentSemanticProjectionTests(unittest.TestCase):
    def test_all_component_ids_project_exactly_once(self):
        reg=json.loads((REALITY/'component-registry.json').read_text())
        proj=json.loads((REALITY/'component-semantic-projection.json').read_text())
        ids=[x['component_id'] for x in proj['components']]
        self.assertEqual(len(ids),97)
        self.assertEqual(len(ids),len(set(ids)))
        self.assertEqual(set(ids),{x['component_id'] for x in reg['components']})

    def test_projection_preserves_epistemic_basis(self):
        proj=json.loads((REALITY/'component-semantic-projection.json').read_text())
        allowed={'DECLARED','OBSERVED','INFERRED','UNKNOWN'}
        for x in proj['components']:
            self.assertIn(x['epistemic_status'],allowed)
            self.assertTrue(x['classification_basis'])
            self.assertTrue(x['semantic_family'])
        inferred=[x for x in proj['components'] if x['epistemic_status']=='INFERRED']
        self.assertGreater(len(inferred),0)

    def test_critical_known_components_land_in_bounded_families(self):
        proj=json.loads((REALITY/'component-semantic-projection.json').read_text())
        by={x['component_id']:x for x in proj['components']}
        expected={
            'ag:component:work-intelligence':'SIGHTLINE',
            'ag:component:sentinel':'WITNESS',
            'ag:component:business-ops':'DOMAIN',
            'ag:component:rendetalje':'DOMAIN',
            'ag:component:studio':'EXPERIENCE',
            'ag:component:brand':'COMMONS',
            'ag:component:orchestrator':'DRIVE',
            'ag:component:memory-store':'HELM',
        }
        for cid,family in expected.items(): self.assertEqual(by[cid]['semantic_family'],family,cid)

    def test_runtime_location_does_not_imply_drive_semantics(self):
        proj=json.loads((REALITY/'component-semantic-projection.json').read_text())
        runtime=[x for x in proj['components'] if 'Aftergraph/runtime' in x['source_repositories']]
        families={x['semantic_family'] for x in runtime}
        self.assertGreaterEqual(len(families),4)
        self.assertIn('DRIVE',families)
        self.assertIn('HELM',families)
        self.assertIn('SIGHTLINE',families)

    def test_generator_is_gate_bound_and_repeatable(self):
        p=REALITY/'component-semantic-projection.json'
        before=p.read_bytes()
        r=subprocess.run([sys.executable,str(ROOT/'scripts/roro/project_component_semantics.py')],cwd=ROOT,text=True,capture_output=True)
        self.assertEqual(r.returncode,0,r.stdout+r.stderr)
        self.assertEqual(before,p.read_bytes())

if __name__=='__main__': unittest.main(verbosity=2)

class ComponentPartitionAnalysisTests(unittest.TestCase):
    def test_analysis_is_multidimensional_and_not_ranked(self):
        data=json.loads((REALITY/'component-partition-analysis.json').read_text())
        text=json.dumps(data).lower()
        for forbidden in ('overall_score','winner','recommended'):
            self.assertNotIn(forbidden,text)
        self.assertEqual(data['components_total'],97)
        self.assertGreaterEqual(data['semantic_family_count'],8)
        self.assertGreaterEqual(data['repository_family_spread']['Aftergraph/runtime']['family_count'],5)
        self.assertGreaterEqual(data['repository_family_spread']['Aftergraph/autonomous-venture-company']['family_count'],8)

    def test_partition_candidates_assign_every_component_once(self):
        data=json.loads((REALITY/'component-partition-simulation.json').read_text())
        ids={x['component_id'] for x in json.loads((REALITY/'component-semantic-projection.json').read_text())['components']}
        for candidate in data['candidates']:
            assigned=[c for w in candidate['workspaces'] for c in w['component_ids']]
            self.assertEqual(set(assigned),ids,candidate['candidate_id'])
            self.assertEqual(len(assigned),len(set(assigned)),candidate['candidate_id'])

    def test_visibility_and_legacy_constraints_are_explicit(self):
        data=json.loads((REALITY/'component-partition-simulation.json').read_text())
        by={x['candidate_id']:x for x in data['candidates']}
        self.assertGreater(by['family-only']['dimensions']['mixed_visibility_workspaces'],0)
        self.assertEqual(by['family-visibility']['dimensions']['mixed_visibility_workspaces'],0)
        self.assertEqual(by['family-visibility-legacy']['dimensions']['mixed_visibility_workspaces'],0)
        self.assertEqual(by['family-visibility-legacy']['dimensions']['legacy_canonical_colocations'],0)

    def test_component_partition_exposes_repo_false_equivalence(self):
        data=json.loads((REALITY/'component-partition-analysis.json').read_text())
        self.assertGreater(data['cross_family_colocation_pairs'],0)
        self.assertGreater(len(data['mixed_semantic_repositories']),0)
        self.assertIn('Aftergraph/runtime',data['mixed_semantic_repositories'])
        self.assertIn('Aftergraph/autonomous-venture-company',data['mixed_semantic_repositories'])

    def test_partition_generator_is_repeatable(self):
        paths=[REALITY/'component-partition-analysis.json',REALITY/'component-partition-simulation.json']
        before=[p.read_bytes() for p in paths]
        r=subprocess.run([sys.executable,str(ROOT/'scripts/roro/simulate_component_partitioning.py')],cwd=ROOT,text=True,capture_output=True)
        self.assertEqual(r.returncode,0,r.stdout+r.stderr)
        self.assertEqual(before,[p.read_bytes() for p in paths])

class StrictComponentPartitionTests(unittest.TestCase):
    def test_family_visibility_lifecycle_partition_clears_three_mixing_classes(self):
        data=json.loads((REALITY/'component-partition-simulation.json').read_text())
        strict=next(x for x in data['candidates'] if x['candidate_id']=='family-visibility-lifecycle')
        d=strict['dimensions']
        self.assertEqual(d['mixed_visibility_workspaces'],0)
        self.assertEqual(d['legacy_canonical_colocations'],0)
        self.assertEqual(d['cross_family_colocations'],0)
        self.assertGreater(d['workspace_count'],14)

    def test_strict_component_partition_is_not_declared_target(self):
        data=json.loads((REALITY/'component-partition-simulation.json').read_text())
        strict=next(x for x in data['candidates'] if x['candidate_id']=='family-visibility-lifecycle')
        self.assertFalse(strict['target_architecture_claim'])
        self.assertFalse(strict['authorizes_source_moves'])

class ComponentPartitionContractTests(unittest.TestCase):
    def test_component_partition_contracts_are_registered_experimental(self):
        register=(ROOT/'docs/cross-repo-contracts.md').read_text()
        for contract in ('roro-component-semantic-projection/0.1','roro-component-partition-analysis/0.1','roro-component-partition-simulation/0.1'):
            self.assertIn(f'`{contract}`',register)

    def test_component_partition_schemas_exist(self):
        base=ROOT/'docs/contracts/roro/0.1'
        for name in ('component-semantic-projection.schema.json','component-partition-analysis.schema.json','component-partition-simulation.schema.json'):
            path=base/name
            self.assertTrue(path.is_file(),path)
            json.loads(path.read_text())

class ComponentProjectionEvidenceTests(unittest.TestCase):
    def test_every_projection_carries_source_evidence_and_no_ownership_claim(self):
        data=json.loads((REALITY/'component-semantic-projection.json').read_text())
        for row in data['components']:
            self.assertTrue(row['evidence_refs'],row['component_id'])
            self.assertFalse(row['owns_semantic_family'],row['component_id'])

    def test_covenant_support_never_claims_authority(self):
        data=json.loads((REALITY/'component-semantic-projection.json').read_text())
        rows=[x for x in data['components'] if x['semantic_family']=='COVENANT_SUPPORT']
        self.assertGreater(len(rows),0)
        for row in rows:
            self.assertIn('does not grant authority',row['boundary_note'].lower())

class ComponentDependencyGraphTests(unittest.TestCase):
    def test_graph_covers_all_projected_components(self):
        proj=json.loads((REALITY/'component-semantic-projection.json').read_text())
        graph=json.loads((REALITY/'component-dependency-graph.json').read_text())
        self.assertEqual({x['component_id'] for x in proj['components']},{x['component_id'] for x in graph['nodes']})

    def test_internal_edges_resolve_to_component_ids(self):
        graph=json.loads((REALITY/'component-dependency-graph.json').read_text())
        ids={x['component_id'] for x in graph['nodes']}
        for edge in graph['edges']:
            self.assertIn(edge['source_component_id'],ids)
            self.assertIn(edge['target_component_id'],ids)
            self.assertTrue(edge['evidence_refs'])
            self.assertEqual(edge['epistemic_status'],'OBSERVED')

    def test_known_exact_manifest_edges_exist(self):
        graph=json.loads((REALITY/'component-dependency-graph.json').read_text())
        edges={(x['source_component_id'],x['target_component_id']) for x in graph['edges']}
        self.assertIn(('ag:component:mission-graph','ag:component:kernel-core'),edges)
        self.assertIn(('ag:legacy:avc:mission-graph','ag:legacy:avc:contracts'),edges)
        self.assertIn(('ag:legacy:avc:mission-graph','ag:legacy:avc:kernel-core'),edges)

    def test_boundary_analysis_exposes_cross_family_edges(self):
        data=json.loads((REALITY/'component-boundary-analysis.json').read_text())
        self.assertGreater(data['cross_family_dependency_edges'],0)
        self.assertIn('family_edges',data)
        self.assertNotIn('winner',json.dumps(data).lower())
        self.assertNotIn('recommended',json.dumps(data).lower())

    def test_analyzer_is_repeatable(self):
        p=REALITY/'component-boundary-analysis.json'; before=p.read_bytes()
        r=subprocess.run([sys.executable,str(ROOT/'scripts/roro/analyze_component_boundaries.py')],cwd=ROOT,text=True,capture_output=True)
        self.assertEqual(r.returncode,0,r.stdout+r.stderr)
        self.assertEqual(before,p.read_bytes())

class ComponentDependencyContractTests(unittest.TestCase):
    def test_dependency_contracts_are_registered_experimental(self):
        register=(ROOT/'docs/cross-repo-contracts.md').read_text()
        for contract in ('roro-component-dependency-graph/0.1','roro-component-boundary-analysis/0.1'):
            self.assertIn(f'`{contract}`',register)
            self.assertIn('Experimental',register)

    def test_dependency_schemas_exist(self):
        for name in ('component-dependency-graph.schema.json','component-boundary-analysis.schema.json'):
            self.assertTrue((ROOT/'docs/contracts/roro/0.1'/name).is_file())

    def test_boundary_analysis_keeps_import_graph_distinct_from_circuit_flow(self):
        data=json.loads((REALITY/'component-boundary-analysis.json').read_text())
        self.assertTrue(data['policy']['dependency_graph_is_not_circuit_flow'])
        self.assertFalse(data['policy']['dependency_edges_grant_authority'])
