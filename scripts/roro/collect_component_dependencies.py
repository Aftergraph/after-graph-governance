from __future__ import annotations
import argparse
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REALITY = ROOT / 'docs/system-reality'
REGISTRY = REALITY / 'component-registry.json'
PROJECTION = REALITY / 'component-semantic-projection.json'
DISPOSITIONS = REALITY / 'source-binding-dispositions.json'
OUT = REALITY / 'component-dependency-graph.json'

DEP_KEYS = ('dependencies', 'peerDependencies', 'optionalDependencies')


def load(path: Path):
    return json.loads(path.read_text(encoding='utf-8'))


def git_has(repo: Path, sha: str) -> bool:
    return subprocess.run(['git','-C',str(repo),'cat-file','-e',sha+'^{commit}'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0


def git_show(repo: Path, sha: str, path: str) -> str | None:
    r = subprocess.run(['git','-C',str(repo),'show',f'{sha}:{path}'], text=True, capture_output=True)
    return r.stdout if r.returncode == 0 else None

def choose_repo(full_name: str, sha: str, source_root: Path, cache_root: Path) -> Path | None:
    name = full_name.split('/',1)[1]
    for root in (source_root, cache_root):
        repo = root / name
        if repo.exists() and git_has(repo, sha):
            return repo
    return None


def manifest_path(binding: dict) -> str:
    base = binding['path']
    return 'package.json' if base == '.' else f"{base.rstrip('/')}/package.json"


def build(source_root: Path, cache_root: Path) -> dict:
    registry = load(REGISTRY)
    projection = load(PROJECTION)
    dispositions = load(DISPOSITIONS)
    family = {x['component_id']: x for x in projection['components']}
    canonical_projection_sources = {
        x['component_id']: x['projection_source']
        for x in dispositions.get('dispositions', [])
        if x.get('disposition') == 'VENDORED_PROJECTION'
    }
    name_to_id: dict[str,str] = {}
    for c in registry['components']:
        name_to_id[c['name']] = c['component_id']
        for alias in c.get('aliases', []):
            name_to_id[alias] = c['component_id']

    nodes=[]; edges=[]; unresolved=[]; coverage=[]
    seen_edges=set()
    for c in registry['components']:
        cid=c['component_id']; proj=family[cid]
        nodes.append({
            'component_id': cid,
            'name': c['name'],
            'semantic_family': proj['semantic_family'],
            'semantic_epistemic_status': proj['epistemic_status'],
        })
        observed_manifests=0
        for b in c['source_bindings']:
            binding_ref=f"{b['repository']}:{b['path']}"
            if canonical_projection_sources.get(cid) == binding_ref:
                continue
            repo=choose_repo(b['repository'], b['revision'], source_root, cache_root)
            if repo is None:
                unresolved.append({'component_id':cid,'type':'SOURCE_OBJECT_UNAVAILABLE','binding':binding_ref,'revision':b['revision']})
                continue
            mpath=manifest_path(b)
            raw=git_show(repo,b['revision'],mpath)
            if raw is None:
                continue
            try: manifest=json.loads(raw)
            except json.JSONDecodeError:
                unresolved.append({'component_id':cid,'type':'MANIFEST_INVALID_JSON','binding':binding_ref,'manifest_path':mpath})
                continue
            observed_manifests += 1
            evidence=f"git://{b['repository']}@{b['revision']}/{mpath}"
            deps={}
            for key in DEP_KEYS:
                deps.update(manifest.get(key) or {})
            for dep_name in sorted(deps):
                if not (dep_name.startswith('@aftergraph/') or dep_name.startswith('@avc/')):
                    continue
                target=name_to_id.get(dep_name)
                if target is None:
                    unresolved.append({'component_id':cid,'type':'INTERNAL_DEPENDENCY_UNRESOLVED','dependency_name':dep_name,'evidence_ref':evidence})
                    continue
                ek=(cid,target,dep_name,evidence)
                if ek in seen_edges: continue
                seen_edges.add(ek)
                edges.append({'source_component_id':cid,'target_component_id':target,'dependency_name':dep_name,'epistemic_status':'OBSERVED','evidence_refs':[evidence]})
        coverage.append({'component_id':cid,'observed_manifest_count':observed_manifests})

    return {
        'schema_version':'roro-component-dependency-graph/0.1',
        'source_snapshot_generated_at': registry['generated_at'],
        'policy': {
            'exact_snapshot_manifests_only': True,
            'dependency_edge_does_not_grant_ownership': True,
            'dev_dependencies_excluded': True,
        },
        'nodes': sorted(nodes,key=lambda x:x['component_id']),
        'edges': sorted(edges,key=lambda x:(x['source_component_id'],x['target_component_id'],x['dependency_name'],x['evidence_refs'][0])),
        'coverage': sorted(coverage,key=lambda x:x['component_id']),
        'unresolved': sorted(unresolved,key=lambda x:json.dumps(x,sort_keys=True)),
    }


def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--source-root',type=Path,required=True)
    ap.add_argument('--cache-root',type=Path,required=True)
    args=ap.parse_args()
    payload=build(args.source_root,args.cache_root)
    OUT.write_text(json.dumps(payload,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(f"component dependency graph: nodes={len(payload['nodes'])} edges={len(payload['edges'])} unresolved={len(payload['unresolved'])}")
    return 0

if __name__=='__main__':
    raise SystemExit(main())
