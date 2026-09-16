from __future__ import annotations
import json
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
REALITY=ROOT/'docs/system-reality'
GRAPH=REALITY/'component-dependency-graph.json'
PROJECTION=REALITY/'component-semantic-projection.json'
OUT=REALITY/'component-boundary-analysis.json'


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def build():
    graph=load(GRAPH); projection=load(PROJECTION)
    family={x['component_id']:x['semantic_family'] for x in projection['components']}
    family_edges=Counter(); cross=[]
    for e in graph['edges']:
        sf=family[e['source_component_id']]; tf=family[e['target_component_id']]
        family_edges[(sf,tf)] += 1
        if sf != tf:
            cross.append({
                'source_component_id':e['source_component_id'],
                'source_family':sf,
                'target_component_id':e['target_component_id'],
                'target_family':tf,
                'dependency_name':e['dependency_name'],
                'evidence_refs':e['evidence_refs'],
            })

    return {
        'schema_version':'roro-component-boundary-analysis/0.1',
        'source_snapshot_generated_at':graph['source_snapshot_generated_at'],
        'policy':{
            'multidimensional_only':True,
            'dependency_edges_do_not_grant_ownership':True,
            'dependency_graph_is_not_circuit_flow':True,
            'dependency_edges_grant_authority':False,
            'analysis_does_not_authorize_moves':True,
        },
        'nodes_total':len(graph['nodes']),
        'dependency_edges_total':len(graph['edges']),
        'unresolved_observations':len(graph['unresolved']),
        'cross_family_dependency_edges':len(cross),
        'within_family_dependency_edges':len(graph['edges'])-len(cross),
        'family_edges':[
            {'source_family':s,'target_family':t,'edge_count':n}
            for (s,t),n in sorted(family_edges.items())
        ],
        'cross_family_edges':sorted(cross,key=lambda x:(x['source_family'],x['target_family'],x['source_component_id'],x['target_component_id'])),
    }


def main():
    payload=build()
    OUT.write_text(json.dumps(payload,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(f"component boundary analysis: edges={payload['dependency_edges_total']} cross_family={payload['cross_family_dependency_edges']} unresolved={payload['unresolved_observations']}")
    return 0

if __name__=='__main__':
    raise SystemExit(main())
