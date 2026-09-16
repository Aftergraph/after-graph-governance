#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
REALITY=ROOT/'docs/system-reality'
REG=REALITY/'component-registry.json'
GATE=REALITY/'coverage-gate.json'
OUT=REALITY/'component-semantic-projection.json'

DECLARED={
 'ag:component:work-intelligence':'SIGHTLINE',
 'ag:component:sentinel':'WITNESS',
 'ag:component:business-ops':'DOMAIN',
 'ag:component:rendetalje':'DOMAIN',
 'ag:component:studio':'EXPERIENCE',
 'ag:component:relay':'EXPERIENCE',
 'ag:component:atlas':'EXPERIENCE',
 'ag:component:docs':'COMMONS',
 'ag:component:brand':'COMMONS',
}
DRIVE={'runtime','job-runtime','runtime-host','scheduler','triggers','orchestrator','proactive-runtime','heartbeat','events','peer-protocol','agent-relay','kernel-core','company-daemon','agent-gateway','hermes-adapter','runner-bridge','runtime-orchestrator','product-installer-adapter'}
HELM={'ledger','goals','mission-graph','mission-inference','mission-routing','memory-store','portfolio','outcomes','intelligence-gateway','muse-supervisor'}
COVENANT={'invariant-registry','authorization','constitution','identity-core','invariants','tenant-core','promotion-gates','mission-graph-authority','identity-worker'}
SIGHTLINE={'observability','agent-observability','metrics','runtime-metrics','telemetry','incident'}
WITNESS={'agent-eval','agent-harness','avc-eval','plugin-deepsec','security-assurance','visual-verifier'}
REFINERY={'avc-llm','model-edge'}
EXPERIENCE={'avc-desktop','cli'}
COMMONS={'contracts','definitions','creative-assets'}
DOMAIN={'leadrescue','serviceops','serviceops-mcp'}
LOOM={'product-catalog'}


def slug(component):
    cid=component['component_id']
    if cid.startswith('ag:legacy:avc:'): return cid.rsplit(':',1)[-1]
    if cid.startswith('ag:component:'): return cid.rsplit(':',1)[-1]
    return component.get('name','').split('/')[-1]


def inferred_family(name):
    for family,names in [('DRIVE',DRIVE),('HELM',HELM),('COVENANT_SUPPORT',COVENANT),('SIGHTLINE',SIGHTLINE),('WITNESS',WITNESS),('REFINERY',REFINERY),('EXPERIENCE',EXPERIENCE),('COMMONS',COMMONS),('DOMAIN',DOMAIN),('LOOM',LOOM)]:
        if name in names: return family
    if name.startswith('veranza'): return 'WITNESS'
    return 'UNKNOWN'
def classify(component):
    cid=component['component_id']
    if cid in DECLARED:
        return DECLARED[cid],'DECLARED','explicit component/repository role in current governance topology'
    name=slug(component)
    family=inferred_family(name)
    if family!='UNKNOWN':
        basis='name/path heuristic over observed source binding; does not grant canonical semantic ownership'
        return family,'INFERRED',basis
    return 'UNKNOWN','UNKNOWN','insufficient semantic evidence; repository placement is not used as semantic truth'


def build():
    gate=json.loads(GATE.read_text(encoding='utf-8'))
    if gate.get('decision')!='READY' or gate.get('scope')!='SOURCE_TOPOLOGY_ONLY':
        raise SystemExit('SOURCE_TOPOLOGY_ONLY gate is not READY')
    registry=json.loads(REG.read_text(encoding='utf-8'))
    rows=[]
    for component in registry['components']:
        family,status,basis=classify(component)
        repos=sorted({b['repository'] for b in component.get('source_bindings',[])})
        rows.append({
            'component_id':component['component_id'],
            'name':component.get('name'),
            'component_class':component.get('component_class'),
            'semantic_family':family,
            'epistemic_status':status,
            'classification_basis':basis,
            'evidence_refs':sorted({b['evidence_ref'] for b in component.get('source_bindings',[]) if b.get('evidence_ref')}),
            'source_repositories':repos,
            'legacy':component['component_id'].startswith('ag:legacy:avc:'),
            'owns_semantic_family':False,
            'boundary_note':('Semantic support classification only; does not grant authority or replace AIE.' if family=='COVENANT_SUPPORT' else 'Semantic projection only; does not grant ownership, authority, execution, or verification rights.'),
        })
    rows.sort(key=lambda x:x['component_id'])
    return {
        'schema_version':'roro-component-semantic-projection/0.1',
        'source_snapshot_generated_at':registry['generated_at'],
        'gate_scope':'SOURCE_TOPOLOGY_ONLY',
        'policy':{
            'repository_is_not_semantic_family':True,
            'inference_does_not_grant_ownership':True,
            'unknowns_are_preserved':True,
            'projection_is_hypothesis_not_migration_plan':True,
        },
        'components':rows,
    }


def main():
    payload=build()
    OUT.write_text(json.dumps(payload,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    counts={}
    for row in payload['components']:
        counts[row['semantic_family']]=counts.get(row['semantic_family'],0)+1
    print('component semantic projection:', ' '.join(f'{k}={counts[k]}' for k in sorted(counts)))
    return 0

if __name__=='__main__':
    raise SystemExit(main())
