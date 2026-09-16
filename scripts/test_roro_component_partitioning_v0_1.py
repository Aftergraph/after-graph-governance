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
