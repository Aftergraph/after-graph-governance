#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REALITY = ROOT / 'docs/system-reality'
TOPO = ROOT / 'docs/platform-topology/2.0.json'
REG = REALITY / 'component-registry.json'
OUT = REALITY / 'consolidation-candidates.json'
BOUND = REALITY / 'consolidation-boundary-analysis.json'


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def ws(workspace_id, visibility, repositories):
    return {
        'workspace_id': workspace_id,
        'visibility': visibility,
        'repositories': sorted(repositories),
    }


def build():
    topology = load(TOPO)
    registry = load(REG)
    meta = {item['name']: item for item in topology['repositories']}
    repos = sorted(meta)
    public = [r for r in repos if meta[r]['visibility'] == 'public']
    private = [r for r in repos if meta[r]['visibility'] == 'private']
    research = {'intelligence-systems-research'}
    legacy = {r for r in repos if meta[r].get('lifecycle') == 'legacy-transition'}
    public_platform = [r for r in public if r not in research]
    private_active = [r for r in private if r not in legacy]
    control_public = {
        r for r in public_platform
        if meta[r].get('architecture_plane') in {'authority', 'trust', 'execution'}
        or r == 'after-graph-governance'
    }
    verification_experience = [r for r in public_platform if r not in control_public]
    strict_authority = {'aie'}
    strict_trust = {'trust-gateway'}
    strict_execution = {'works-execution'}
    strict_verification = {'sentinel', 'sentinel-firetest2'}
    strict_reserved = strict_authority | strict_trust | strict_execution | strict_verification | research
    strict_public_misc = [r for r in public if r not in strict_reserved]
    private_research = {r for r in private_active if meta[r].get('system_class') in {'models', 'research-assurance'}}
    private_nonresearch = [r for r in private_active if r not in private_research]

    candidates = [
        {
            'candidate_id': 'ws2-visibility-only',
            'hypothesis': 'Collapse only by GitHub visibility boundary.',
            'workspace_count': 2,
            'workspaces': [ws('public', 'public', public), ws('internal', 'private', private)],
        },
        {
            'candidate_id': 'ws3-research-isolated',
            'hypothesis': 'Separate public research identity from the public platform while retaining one private internal workspace.',
            'workspace_count': 3,
            'workspaces': [ws('platform-public', 'public', public_platform), ws('research-public', 'public', research), ws('internal', 'private', private)],
        },
        {
            'candidate_id': 'ws4-legacy-isolated',
            'hypothesis': 'Add a dedicated private legacy workspace so AVC extraction source cannot silently become part of canonical internal code.',
            'workspace_count': 4,
            'workspaces': [ws('platform-public', 'public', public_platform), ws('research-public', 'public', research), ws('internal-active', 'private', private_active), ws('legacy-private', 'private', legacy)],
        },
        {
            'candidate_id': 'ws5-verifier-split',
            'hypothesis': 'Preserve research and legacy isolation, and split public authority/execution control code from public verification/experience/foundation code.',
            'workspace_count': 5,
            'workspaces': [ws('control-public', 'public', control_public), ws('verification-experience-public', 'public', verification_experience), ws('research-public', 'public', research), ws('internal-active', 'private', private_active), ws('legacy-private', 'private', legacy)],
        },
        {
            'candidate_id': 'ws7-strict-public-boundaries',
            'hypothesis': 'Instantiate the strict lower-bound hypothesis by separating public authority, trust, execution, verification, and research while keeping active private source together and AVC isolated.',
            'workspace_count': 7,
            'workspaces': [ws('authority-foundation-public', 'public', strict_authority | set(strict_public_misc)), ws('trust-public', 'public', strict_trust), ws('execution-public', 'public', strict_execution), ws('verification-public', 'public', strict_verification), ws('research-public', 'public', research), ws('internal-active', 'private', private_active), ws('legacy-private', 'private', legacy)],
        },
        {
            'candidate_id': 'ws8-private-research-isolated',
            'hypothesis': 'Extend the strict seven-workspace hypothesis by isolating private model/research source from other active private source.',
            'workspace_count': 8,
            'workspaces': [ws('authority-foundation-public', 'public', strict_authority | set(strict_public_misc)), ws('trust-public', 'public', strict_trust), ws('execution-public', 'public', strict_execution), ws('verification-public', 'public', strict_verification), ws('research-public', 'public', research), ws('internal-active', 'private', private_nonresearch), ws('private-research', 'private', private_research), ws('legacy-private', 'private', legacy)],
        },
    ]
    payload = {
        'schema_version': 'roro-consolidation-candidates/0.1',
        'source_snapshot_generated_at': registry['generated_at'],
        'policy': {
            'candidate_is_hypothesis_not_decision': True,
            'mixed_visibility_in_one_repository_prohibited': True,
            'workspace_is_source_boundary_not_runtime_security_boundary': True,
        },
        'candidates': candidates,
    }
    boundary = {
        'schema_version': 'roro-consolidation-boundary-analysis/0.1',
        'source_snapshot_generated_at': registry['generated_at'],
        'policy': {'lower_bound_is_not_recommendation': True, 'no_overall_score': True, 'source_workspace_only': True},
        'strict_hypothesis': {
            'minimum_workspace_lower_bound': 7,
            'derivation': 'At least five public source workspaces under simultaneous trust-boundary separation plus research isolation, and at least two private workspaces under legacy isolation.',
            'constraints': [
                {'constraint': 'visibility_purity', 'effect': 'public and private sources cannot share a workspace'},
                {'constraint': 'trust_boundary_separation', 'effect': 'authority, trust, execution, and independent verification may not share a source workspace with each other under this strict hypothesis'},
                {'constraint': 'research_isolation', 'effect': 'public research does not share a source workspace with production platform code'},
                {'constraint': 'legacy_isolation', 'effect': 'legacy-transition source does not share a private workspace with canonical active source'},
            ],
        },
    }
    return payload, boundary


def main():
    payload, boundary = build()
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    BOUND.write_text(json.dumps(boundary, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    print('candidates=6 strict_lower_bound=7')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
