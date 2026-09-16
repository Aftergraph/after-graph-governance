#!/usr/bin/env python3
from __future__ import annotations
import json
from itertools import combinations
from pathlib import Path
import yaml

ROOT=Path(__file__).resolve().parents[2]
REALITY=ROOT/'docs/system-reality'
CANDIDATES=REALITY/'consolidation-candidates.json'
OUT=REALITY/'consolidation-simulation.json'
TOPOLOGY=ROOT/'docs/platform-topology/2.0.json'
DEPS=ROOT/'dependencies.yml'
GATE=REALITY/'coverage-gate.json'

TRUST_PLANES={'authority','trust','execution','verification'}
RESEARCH_CLASSES={'research-assurance','models'}
DOMAIN_CLASSES={'service-business-domain','tenant-domain'}
LEGACY_LIFECYCLES={'legacy-transition'}


def load_json(path): return json.loads(path.read_text(encoding='utf-8'))

def workspace_index(candidate):
    return {repo:w['workspace_id'] for w in candidate['workspaces'] for repo in w['repositories']}

def count_pairs(repos, predicate_a, predicate_b=None):
    predicate_b=predicate_b or predicate_a
    n=0
    for a,b in combinations(repos,2):
        if (predicate_a(a) and predicate_b(b)) or (predicate_a(b) and predicate_b(a)):
            n+=1
    return n

def build():
    gate=load_json(GATE)
    if gate.get('decision')!='READY' or gate.get('scope')!='SOURCE_TOPOLOGY_ONLY':
        raise SystemExit('SOURCE_TOPOLOGY_ONLY gate is not READY')
    candidates=load_json(CANDIDATES)
    topo=load_json(TOPOLOGY)
    meta={r['name']:r for r in topo['repositories']}
    depdoc=yaml.safe_load(DEPS.read_text(encoding='utf-8'))
    deps={name:[x.split('.',1)[0] for x in spec.get('consumes',[]) if isinstance(x,str)] for name,spec in depdoc.get('modules',{}).items()}
    deployed={b['canonical_repository'].split('/',1)[1] for b in load_json(REALITY/'deployment-source-diffs.json')['bindings']}
    out=[]
    for c in candidates['candidates']:
        idx=workspace_index(c); hard=[]
        mixed=0
        for w in c['workspaces']:
            vis={meta[r]['visibility'] for r in w['repositories']}
            if len(vis)>1:
                mixed+=1; hard.append({'id':'mixed-visibility','workspace':w['workspace_id']})
        cross_edges=0
        for src,targets in deps.items():
            if src not in idx: continue
            for dst in targets:
                if dst in idx and idx[src]!=idx[dst]: cross_edges+=1
        trust=legacy=research=domain=deploy_pairs=0
        for w in c['workspaces']:
            repos=w['repositories']
            trust_repos=[r for r in repos if meta[r].get('architecture_plane') in TRUST_PLANES]
            trust += sum(1 for a,b in combinations(trust_repos,2) if meta[a].get('architecture_plane')!=meta[b].get('architecture_plane'))
            legacy_repos=[r for r in repos if meta[r].get('lifecycle') in LEGACY_LIFECYCLES]
            canonical=[r for r in repos if meta[r].get('lifecycle') not in LEGACY_LIFECYCLES]
            legacy += len(legacy_repos)*len(canonical)
            research_repos=[r for r in repos if meta[r].get('system_class') in RESEARCH_CLASSES]
            production=[r for r in repos if meta[r].get('system_class') not in RESEARCH_CLASSES]
            research += len(research_repos)*len(production)
            domain_repos=[r for r in repos if meta[r].get('system_class') in DOMAIN_CLASSES]
            platform=[r for r in repos if meta[r].get('system_class') not in DOMAIN_CLASSES]
            domain += len(domain_repos)*len(platform)
            d=[r for r in repos if r in deployed]
            deploy_pairs += len(d)*(len(d)-1)//2
        out.append({
            'candidate_id':c['candidate_id'],'workspace_count':c['workspace_count'],'hard_blockers':hard,
            'dimensions':{
                'mixed_visibility_workspaces':mixed,
                'cross_workspace_dependency_edges':cross_edges,
                'trust_boundary_colocations':trust,
                'legacy_canonical_colocations':legacy,
                'research_production_colocations':research,
                'domain_platform_colocations':domain,
                'deployment_colocation_pairs':deploy_pairs,
                'largest_workspace_repositories':max(len(w['repositories']) for w in c['workspaces']),
            },
            'workspace_summaries':[{'workspace_id':w['workspace_id'],'visibility':w['visibility'],'repository_count':len(w['repositories'])} for w in c['workspaces']],
        })
    return {
        'schema_version':'roro-consolidation-simulation/0.1',
        'source_snapshot_generated_at':candidates['source_snapshot_generated_at'],
        'gate_scope':'SOURCE_TOPOLOGY_ONLY',
        'policy':{
            'multidimensional_only':True,
            'candidate_is_hypothesis_not_decision':True,
            'workspace_is_not_security_boundary':True,
            'runtime_state_credential_authority_migrations_excluded':True,
        },
        'candidates':out,
    }

def main():
    payload=build(); OUT.write_text(json.dumps(payload,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    for c in payload['candidates']:
        print(c['candidate_id'],c['dimensions'])
    return 0
if __name__=='__main__': raise SystemExit(main())
