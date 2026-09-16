#!/usr/bin/env python3
from __future__ import annotations
import json
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
REALITY=ROOT/'docs/system-reality'
PROJ=REALITY/'component-semantic-projection.json'
TOPO=ROOT/'docs/platform-topology/2.0.json'
DISP=REALITY/'source-binding-dispositions.json'
ANALYSIS=REALITY/'component-partition-analysis.json'
SIM=REALITY/'component-partition-simulation.json'


def load(path): return json.loads(path.read_text(encoding='utf-8'))

def primary_source(row, dispositions):
    d=dispositions.get(row['component_id'])
    if d:
        return d['canonical_source'].split(':',1)[0]
    return sorted(row['source_repositories'])[0]

def workspace_payload(assignments, rows, visibility):
    grouped=defaultdict(list)
    for row in rows: grouped[assignments[row['component_id']]].append(row)
    out=[]
    for wid,members in sorted(grouped.items()):
        vis=sorted({visibility[primary_source(x, SOURCE_DISP)] for x in members})
        out.append({
            'workspace_id':wid,
            'visibility':vis[0] if len(vis)==1 else 'MIXED',
            'component_ids':sorted(x['component_id'] for x in members),
        })
    return out


def dimensions(workspaces, rows_by_id, primary_by_id):
    mixed=legacy_pairs=cross_family=0
    source_spread=defaultdict(set)
    largest=0
    for w in workspaces:
        members=[rows_by_id[cid] for cid in w['component_ids']]
        largest=max(largest,len(members))
        if w['visibility']=='MIXED': mixed+=1
        for a,b in combinations(members,2):
            if a['legacy'] != b['legacy']: legacy_pairs+=1
            if a['semantic_family'] != b['semantic_family']: cross_family+=1
        for m in members: source_spread[primary_by_id[m['component_id']]].add(w['workspace_id'])
    splits=sum(len(v)-1 for v in source_spread.values() if len(v)>1)
    return {
        'workspace_count':len(workspaces),
        'mixed_visibility_workspaces':mixed,
        'legacy_canonical_colocations':legacy_pairs,
        'cross_family_colocations':cross_family,
        'source_repository_split_count':splits,
        'largest_workspace_components':largest,
    }

SOURCE_DISP={}

def build():
    global SOURCE_DISP
    proj=load(PROJ)
    topo=load(TOPO)
    disp=load(DISP)
    SOURCE_DISP={x['component_id']:x for x in disp.get('dispositions',[])}
    visibility={f"Aftergraph/{x['name']}":x['visibility'] for x in topo['repositories']}
    rows=proj['components']; rows_by_id={x['component_id']:x for x in rows}
    primary={x['component_id']:primary_source(x,SOURCE_DISP) for x in rows}
    families=Counter(x['semantic_family'] for x in rows)
    spread=defaultdict(set)
    members_by_repo=defaultdict(list)
    for row in rows:
        repo=primary[row['component_id']]
        spread[repo].add(row['semantic_family']); members_by_repo[repo].append(row)
    cross_pairs=0
    for members in members_by_repo.values():
        cross_pairs += sum(a['semantic_family']!=b['semantic_family'] for a,b in combinations(members,2))
    analysis={
        'schema_version':'roro-component-partition-analysis/0.1',
        'source_snapshot_generated_at':proj['source_snapshot_generated_at'],
        'components_total':len(rows),
        'semantic_family_count':len(families),
        'semantic_family_counts':dict(sorted(families.items())),
        'repository_family_spread':{
            repo:{'family_count':len(fs),'families':sorted(fs),'component_count':len(members_by_repo[repo])}
            for repo,fs in sorted(spread.items())
        },
        'mixed_semantic_repositories':sorted(repo for repo,fs in spread.items() if len(fs)>1),
        'cross_family_colocation_pairs':cross_pairs,
        'policy':{'scalar_score_prohibited':True,'repository_is_not_semantic_boundary':True,'analysis_does_not_authorize_moves':True},
    }
    assignment_sets={
        'current-repo':{x['component_id']:primary[x['component_id']] for x in rows},
        'family-only':{x['component_id']:x['semantic_family'] for x in rows},
        'family-visibility':{x['component_id']:f"{x['semantic_family']}::{visibility[primary[x['component_id']]]}" for x in rows},
        'family-visibility-legacy':{
            x['component_id']:(f"LEGACY::{visibility[primary[x['component_id']]]}" if x['legacy'] else f"{x['semantic_family']}::{visibility[primary[x['component_id']]]}")
            for x in rows
        },
        'family-visibility-lifecycle':{
            x['component_id']:f"{x['semantic_family']}::{visibility[primary[x['component_id']]]}::{('LEGACY' if x['legacy'] else 'CANONICAL')}"
            for x in rows
        },
    }
    candidates=[]
    for cid,assignments in assignment_sets.items():
        workspaces=workspace_payload(assignments,rows,visibility)
        dims=dimensions(workspaces,rows_by_id,primary)
        candidates.append({
            'candidate_id':cid,
            'target_architecture_claim':False,
            'authorizes_source_moves':False,
            'hard_blockers':([{'id':'mixed-visibility'}] if dims['mixed_visibility_workspaces'] else []),
            'dimensions':dims,
            'workspaces':workspaces,
        })
    simulation={
        'schema_version':'roro-component-partition-simulation/0.1',
        'source_snapshot_generated_at':proj['source_snapshot_generated_at'],
        'gate_scope':'SOURCE_TOPOLOGY_ONLY',
        'policy':{
            'multidimensional_only':True,
            'no_selected_winner':True,
            'component_partition_is_hypothesis_not_move_plan':True,
            'runtime_state_credential_authority_migrations_excluded':True,
        },
        'candidates':candidates,
    }
    return analysis,simulation


def main():
    analysis,simulation=build()
    ANALYSIS.write_text(json.dumps(analysis,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    SIM.write_text(json.dumps(simulation,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(f"component partition: families={analysis['semantic_family_count']} mixed_repos={len(analysis['mixed_semantic_repositories'])} cross_family_pairs={analysis['cross_family_colocation_pairs']}")
    for c in simulation['candidates']: print(c['candidate_id'],c['dimensions'])
    return 0

if __name__=='__main__': raise SystemExit(main())
