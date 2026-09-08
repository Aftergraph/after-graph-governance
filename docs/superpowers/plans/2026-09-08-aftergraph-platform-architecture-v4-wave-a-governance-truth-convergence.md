# Aftergraph Platform Architecture V4 — Wave A Governance Truth Convergence Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make Governance expose one internally consistent, machine-validated platform truth for the approved V4 architecture before any downstream runtime, AVC extraction, World State, Pocket, voice or Golden Mission implementation begins.

**Architecture:** `docs/platform-topology/2.0.json` becomes the slow-changing canonical repository/topology source and separates `architecture_plane` from `system_class`. A zero-dependency Python validator checks topology shape, README/registry/dependency projections and legacy naming drift. `org-state-verify.sh` consumes topology/2.0 for exact GitHub truth while preserving `org-state/1.0` compatibility. The approved V4 design is promoted into a concise canonical architecture document, while V3 remains readable as superseded history.

**Tech Stack:** JSON Schema Draft 2020-12, Python 3.12 stdlib `json`/`unittest`, Bash, jq, GitHub CLI, GitHub Actions, Markdown, YAML constrained to the repository's current `dependencies.yml` shape.

**Spec:** `docs/superpowers/specs/2026-09-08-aftergraph-platform-architecture-v4-and-platform-fabrics-v1-design.md`

## Global Constraints

- Preserve exactly seven permanent semantic planes: `intelligence`, `authority`, `trust`, `runtime`, `execution`, `verification`, `experience`.
- Preserve exactly eight cross-cutting Fabrics in the approved design: Interaction, Perception, Context, World State, Proactivity, Capability, Agent Organization, Verified Improvement.
- `platform-event-ref/0.1` remains the correlation substrate, not a ninth Fabric.
- `Aftergraph` is the target platform/masterbrand. `AVC`, `Autonomous Venture Company`, `avc-*` and `@avc/*` are legacy compatibility/provenance terminology only.
- Do not rewrite historical evidence merely to remove legacy names.
- No repository gains authority, execution, verification or evidence ownership merely because it appears in topology.
- Exact Git SHAs remain generated GitHub remote truth; do not hand-author exact heads into topology or architecture files.
- `platform-topology/1.0` remains readable for historical provenance; new active Governance code consumes `platform-topology/2.0` after this wave.
- `org-state/1.0` remains schema-readable for existing snapshots; this wave does not introduce `org-state/2.0`.
- Keep validation dependency-free. Do not add PyYAML/jsonschema as mandatory runtime dependencies.
- Repository-local green tests establish Governance conformance only, not full platform integration or scientific maturity.
- Respect merge-queue rules. Do not write directly to protected `main`.

## Program decomposition after Wave A

This plan intentionally implements only Wave A. The approved platform-wide spec is too broad for a single implementation plan. Subsequent plans are created only after their prerequisites are merged:

```text
Wave A  Governance truth convergence                <- this plan
Wave B  AVC dissolution ledger + legacy owner exits <- depends on A
Wave C  Tenant/Consent/Workspace lifecycle          <- depends on A, overlaps B migration inputs
Wave D  World State + Commitment contracts          <- depends on A/B owner truth
Wave E  Capability + Verified Auto closure          <- depends on A and existing v0.1 fabrics
Wave F  Proactivity + Agent Organization            <- depends on D/E
Wave G  Perception + Pocket connector               <- depends on C/D
Wave H  Interaction + realtime voice                <- depends on C/D/E/G
Wave I  Verified Improvement + adversarial Golden Mission <- depends on B-H
```

---

### Task 1: Add `platform-topology/2.0` contract and 24-repository V4 data

**Repository:** `Aftergraph/after-graph-governance`

**Files:**
- Create: `docs/platform-topology/2.0.schema.json`
- Create: `docs/platform-topology/2.0.json`
- Preserve: `docs/platform-topology/1.0.json`
- Test: `scripts/test_platform_topology_v2.py`

**Interfaces:**
- Consumes: current `platform-topology/1.0` repository membership, approved V4 owner decisions.
- Produces: `platform-topology/2.0` consumed by all later tasks in this plan.

Use this repository mapping exactly for `architecture_plane` and `system_class`:

```text
after-graph-governance        null          governance
aie                           authority     institution
trust-gateway                 trust         enforcement
runtime                       runtime       runtime
works-execution               execution     execution
studio                        experience    experience
wi-backend                    intelligence  work-intelligence
wi-frontend                   experience    specialist-experience
context-continuity            null          continuity
continuum                     null          assurance
sentinel                      verification  assurance
sentinel-firetest             null          assurance-fixture
intelligence-systems-research null          research-assurance
skills-vault                  null          capabilities
llm-research-development      null          models
afm                           null          models
model-registry                null          models
autonomous-venture-company    null          legacy-transition
aftergraph-cron-fabric        null          operations
veranza                       null          incubation
docs                          null          knowledge
aftergraph.org                null          public
brand                         null          foundation
.github                       null          foundation
```

Every repository record requires:

```json
{
  "name": "runtime",
  "canonical_branch": "main",
  "visibility": "private",
  "architecture_plane": "runtime",
  "system_class": "runtime",
  "role": "agent-runtime",
  "lifecycle": "active",
  "owns": "Agent lifecycle, orchestration, dispatch, checkpoints, metering and observability.",
  "must_not_own": "AIE authority, Trust Gateway enforcement, WORKS durable execution, organizational canonical knowledge or independent verification."
}
```

The schema must require `name`, `canonical_branch`, `visibility`, `architecture_plane`, `system_class`, `role`, `lifecycle`, `owns`, `must_not_own`; `architecture_plane` accepts either `null` or one of the seven exact values; `additionalProperties` is `false` at repository-record level.

- [ ] **Step 1: Write the failing topology test**

Create `scripts/test_platform_topology_v2.py` using stdlib `unittest`. Include these assertions:

```python
class TopologyV2DataTest(unittest.TestCase):
    def test_has_exactly_24_unique_repositories(self):
        doc = load_json(TOPOLOGY)
        names = [r["name"] for r in doc["repositories"]]
        self.assertEqual(len(names), 24)
        self.assertEqual(len(set(names)), 24)

    def test_only_seven_non_null_architecture_planes_exist(self):
        doc = load_json(TOPOLOGY)
        actual = {r["architecture_plane"] for r in doc["repositories"] if r["architecture_plane"] is not None}
        self.assertEqual(actual, {"intelligence", "authority", "trust", "runtime", "execution", "verification", "experience"})

    def test_support_system_does_not_fake_a_plane(self):
        repo = topology_index(load_json(TOPOLOGY))["context-continuity"]
        self.assertIsNone(repo["architecture_plane"])
        self.assertEqual(repo["system_class"], "continuity")
```

Add tests rejecting duplicate names, `plane` as an active v2 property, unknown architecture planes, missing `must_not_own`, non-`main` current canonical branches and exact-SHA-looking fields such as `head_sha` or `remote_head_sha`.

- [ ] **Step 2: Run the test and verify RED**

Run:

```bash
python scripts/test_platform_topology_v2.py
```

Expected: FAIL because `2.0.schema.json` and `2.0.json` do not exist.

- [ ] **Step 3: Create strict schema and V4 topology data**

Create the two JSON files. Copy repository names/visibility/roles from 1.0 where still current, apply the exact mapping above, set `schema_version` to `platform-topology/2.0`, keep `organization: Aftergraph`, and keep exact heads out of the document.

For active legacy AVC use:

```json
{
  "name": "autonomous-venture-company",
  "canonical_branch": "main",
  "visibility": "private",
  "architecture_plane": null,
  "system_class": "legacy-transition",
  "role": "legacy-migration-source",
  "lifecycle": "legacy-transition",
  "owns": "Legacy product, Hermes integration and migration-source behavior pending governed extraction.",
  "must_not_own": "New canonical Aftergraph platform responsibilities, new @avc/* contracts or new platform authority semantics."
}
```

Do not use `venture-os-consumer` as the current v2 role.

- [ ] **Step 4: Run topology tests**

```bash
python scripts/test_platform_topology_v2.py
python -m json.tool docs/platform-topology/2.0.json >/dev/null
python -m json.tool docs/platform-topology/2.0.schema.json >/dev/null
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add docs/platform-topology/2.0.json docs/platform-topology/2.0.schema.json scripts/test_platform_topology_v2.py
git commit -m "feat(governance): add platform topology v2"
```

---

### Task 2: Add one zero-dependency topology validator and README renderer

**Files:**
- Create: `scripts/platform_topology.py`
- Modify: `scripts/test_platform_topology_v2.py`
- Modify later through generated block: `README.md`

**Interfaces:**
- Consumes: `docs/platform-topology/2.0.json`.
- Produces:
  - `load_topology(path: Path) -> dict[str, Any]`
  - `validate_topology(doc: Mapping[str, Any]) -> list[str]`
  - `topology_index(doc: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]`
  - `render_readme_table(doc: Mapping[str, Any]) -> str`
  - CLI: `python scripts/platform_topology.py check`
  - CLI: `python scripts/platform_topology.py render-readme`

- [ ] **Step 1: Extend tests for validator behavior**

Add:

```python
from platform_topology import render_readme_table, validate_topology

class TopologyValidatorTest(unittest.TestCase):
    def test_duplicate_repository_is_rejected(self):
        doc = valid_topology()
        doc["repositories"].append(dict(doc["repositories"][0]))
        self.assertIn("duplicate repository name", "\n".join(validate_topology(doc)))

    def test_non_plane_system_class_remains_allowed(self):
        doc = valid_topology()
        doc["repositories"][0]["architecture_plane"] = None
        doc["repositories"][0]["system_class"] = "governance"
        self.assertEqual(validate_topology(doc), [])

    def test_readme_render_is_deterministic(self):
        doc = load_json(TOPOLOGY)
        self.assertEqual(render_readme_table(doc), render_readme_table(doc))
```

- [ ] **Step 2: Run targeted tests and verify RED**

```bash
python scripts/test_platform_topology_v2.py
```

Expected: import failure for `platform_topology`.

- [ ] **Step 3: Implement the minimal validator/renderer**

`validate_topology()` must enforce:

```python
PLANE_VALUES = {"intelligence", "authority", "trust", "runtime", "execution", "verification", "experience"}
REQUIRED_REPO_FIELDS = {
    "name", "canonical_branch", "visibility", "architecture_plane",
    "system_class", "role", "lifecycle", "owns", "must_not_own",
}
FORBIDDEN_ACTIVE_NAME_PARTS = ("@avc/", "avc-")
```

Legacy repository name `autonomous-venture-company` is explicitly allowlisted only when `system_class == "legacy-transition"` and `lifecycle == "legacy-transition"`.

The README renderer emits this exact column order:

```text
Architecture plane | System class | Repository | Role | Lifecycle | Canonical responsibility
```

Use `Support` when `architecture_plane` is null. Sort permanent-plane rows in lifecycle order `intelligence, authority, trust, runtime, execution, verification, experience`, then support rows by repository name. Do not infer an architecture plane from `system_class`.

- [ ] **Step 4: Run tests and CLI**

```bash
python scripts/test_platform_topology_v2.py
python scripts/platform_topology.py check
python scripts/platform_topology.py render-readme >/tmp/aftergraph-topology.md
```

Expected: PASS and deterministic Markdown output.

- [ ] **Step 5: Commit**

```bash
git add scripts/platform_topology.py scripts/test_platform_topology_v2.py
git commit -m "feat(governance): validate and render topology v2"
```

---

### Task 3: Reconcile `dependencies.yml` to topology/2.0 and current repo identities

**Files:**
- Modify: `dependencies.yml`
- Modify: `scripts/platform_topology.py`
- Modify: `scripts/test_platform_topology_v2.py`

**Interfaces:**
- Consumes: topology v2 repository name/role truth.
- Produces: dependency projection whose module names are a subset equal to all 24 current topology repositories and whose `repo`/`role` match topology.

Keep `dependencies.yml` as YAML for compatibility. The validator only needs a constrained parser for fields Governance itself owns: `version`, `topology_ref`, module key, `repo`, `role`; it must not pretend to be a general YAML parser.

Add:

```python
@dataclass(frozen=True)
class DependencyModule:
    name: str
    repo: str
    role: str


def parse_dependency_projection(text: str) -> tuple[str, dict[str, DependencyModule]]:
    """Parse topology_ref and each module's repo/role from the repository's constrained YAML shape."""
```

- [ ] **Step 1: Add RED tests for current drift**

Tests must fail against current `dependencies.yml` because it references `work-intelligence-v2`, `work-intelligence-web`, omits `runtime`, and points to topology/1.0.

```python
def test_dependency_projection_matches_topology_v2(self):
    doc = load_topology(TOPOLOGY)
    topology = topology_index(doc)
    topology_ref, modules = parse_dependency_projection(DEPENDENCIES.read_text())
    self.assertEqual(topology_ref, "docs/platform-topology/2.0.json")
    self.assertEqual(set(modules), set(topology))
    for name, module in modules.items():
        self.assertEqual(module.repo, f"Aftergraph/{name}")
        self.assertEqual(module.role, topology[name]["role"])
```

- [ ] **Step 2: Run RED test**

```bash
python scripts/test_platform_topology_v2.py
```

Expected: mismatch showing stale Work Intelligence names and missing Runtime/current repos.

- [ ] **Step 3: Update dependency projection to all 24 repositories**

Required current module identities include:

```text
runtime
wi-backend
wi-frontend
sentinel
sentinel-firetest
aftergraph-cron-fabric
veranza
```

Replace old active names:

```text
work-intelligence-v2  -> wi-backend
work-intelligence-web -> wi-frontend
```

Set:

```yaml
version: 4
topology_ref: docs/platform-topology/2.0.json
```

For AVC set role `legacy-migration-source` and describe only migration/legacy outputs. Do not add new consumers of AVC.

Do not invent dependencies merely to make every module connected. Preserve known `consumes`/`provides`, correct renamed references, and use empty lists where the architecture does not establish a dependency.

- [ ] **Step 4: Run projection tests**

```bash
python scripts/test_platform_topology_v2.py
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add dependencies.yml scripts/platform_topology.py scripts/test_platform_topology_v2.py
git commit -m "fix(governance): reconcile dependency projection with topology v2"
```

---

### Task 4: Move exact-head generation to topology/2.0 without breaking org-state/1.0

**Files:**
- Modify: `scripts/org-state-verify.sh`
- Modify: `docs/contracts/org-state/1.0.json`
- Create: `scripts/test_org_state_topology_v2.py`

**Interfaces:**
- Consumes: topology/2.0 `name`, `role`, `canonical_branch`.
- Produces: unchanged `org-state/1.0` snapshot format in `latest-org-state.json`.

- [ ] **Step 1: Write source-level RED tests**

The test reads `org-state-verify.sh` and schema text without calling GitHub:

```python
class OrgStateTopologyBindingTest(unittest.TestCase):
    def test_generator_uses_topology_v2(self):
        text = GENERATOR.read_text(encoding="utf-8")
        self.assertIn("docs/platform-topology/2.0.json", text)
        self.assertIn('platform-topology/2.0', text)
        self.assertNotIn('TOPOLOGY="$SCRIPT_DIR/../docs/platform-topology/1.0.json"', text)

    def test_org_state_contract_points_current_generation_to_v2(self):
        schema = json.loads(ORG_STATE_SCHEMA.read_text(encoding="utf-8"))
        self.assertIn("platform-topology/2.0", schema["description"])
```

- [ ] **Step 2: Run and verify RED**

```bash
python scripts/test_org_state_topology_v2.py
```

Expected: FAIL on 1.0 references.

- [ ] **Step 3: Update generator**

Set:

```bash
TOPOLOGY="$SCRIPT_DIR/../docs/platform-topology/2.0.json"
```

Replace envelope validation with:

```bash
jq -e '.schema_version == "platform-topology/2.0"
       and .organization == "Aftergraph"
       and (.repositories | type == "array")
       and (.repositories | length > 0)' "$TOPOLOGY"
```

Continue deriving `repo role canonical_branch` from topology. Do not use `architecture_plane` to generate authority or runtime behavior. Preserve all existing GitHub API/full-snapshot fail-closed mechanics.

Update `org-state/1.0` descriptions from “current topology is 1.0” to “current generation scope is platform-topology/2.0; historical snapshots remain schema-readable”. Keep role compatibility enum values needed for old snapshots.

- [ ] **Step 4: Run local structural gates**

```bash
python scripts/test_org_state_topology_v2.py
bash -n scripts/org-state-verify.sh
python -m json.tool docs/contracts/org-state/1.0.json >/dev/null
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add scripts/org-state-verify.sh docs/contracts/org-state/1.0.json scripts/test_org_state_topology_v2.py
git commit -m "fix(governance): bind org-state generation to topology v2"
```

---

### Task 5: Promote the approved V4 design into canonical architecture docs and mark stale docs historical

**Files:**
- Create: `docs/PLATFORM-ARCHITECTURE-V4.md`
- Modify: `docs/PLATFORM-ARCHITECTURE-V3.md`
- Modify: `docs/PLATFORM-RECONCILIATION-V1.md`
- Modify: `docs/cross-repo-contracts.md`
- Modify: `docs/REPOSITORY-REGISTRY-v0.1.md`

**Interfaces:**
- Consumes: approved design spec, topology/2.0.
- Produces: current human-readable architecture that agrees with machine topology.

- [ ] **Step 1: Add document consistency checks to topology tests**

Add checks that active docs contain `docs/platform-topology/2.0.json`, current repo identities `wi-backend`, `wi-frontend`, `runtime`, and do not present `work-intelligence-v2`, `work-intelligence-web` or `venture-os-consumer` as current canonical ownership.

V3 is exempt from historical legacy strings only if its first 12 lines contain:

```text
Status: Superseded by PLATFORM-ARCHITECTURE-V4.md
```

- [ ] **Step 2: Run RED tests**

```bash
python scripts/test_platform_topology_v2.py
```

Expected: FAIL on stale current docs.

- [ ] **Step 3: Create concise normative V4 document**

`docs/PLATFORM-ARCHITECTURE-V4.md` must include:

```text
Status: Canonical
Supersedes: PLATFORM-ARCHITECTURE-V3.md
Seven permanent planes
Eight Platform Fabrics
platform-event-ref/0.1 correlation substrate
owner + must-not-own table
platform-topology/2.0 relation
AVC dissolution rule
constitutional invariants
conformance ladder L0-L6
```

Do not copy the entire design rationale. Link to the approved design spec for rationale/red-team detail.

- [ ] **Step 4: Mark V3 superseded, not deleted**

At the top of V3 add:

```markdown
**Status:** Superseded by [`PLATFORM-ARCHITECTURE-V4.md`](PLATFORM-ARCHITECTURE-V4.md). Retained for historical provenance.
```

Do not rewrite its historical content.

- [ ] **Step 5: Update reconciliation, registry and contract register**

Required corrections:

```text
19 repos -> 24 repos/current topology language
work-intelligence-v2 -> wi-backend for current boundary rows
work-intelligence-web -> wi-frontend for current boundary rows
venture-os-consumer -> legacy-migration-source for current rows
current topology ref -> docs/platform-topology/2.0.json
Runtime must appear as active canonical runtime owner
Continuum -> assurance, not ordinary continuity owner
context-continuity -> portable state transfer
```

Historical sections may retain old repo names when explicitly labeled historical/provenance.

- [ ] **Step 6: Run documentation consistency gates**

```bash
python scripts/test_platform_topology_v2.py
```

Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add docs/PLATFORM-ARCHITECTURE-V4.md docs/PLATFORM-ARCHITECTURE-V3.md docs/PLATFORM-RECONCILIATION-V1.md docs/cross-repo-contracts.md docs/REPOSITORY-REGISTRY-v0.1.md scripts/test_platform_topology_v2.py
git commit -m "docs(governance): promote platform architecture v4"
```

---

### Task 6: Make README topology a generated/validated projection

**Files:**
- Modify: `README.md`
- Modify: `scripts/platform_topology.py`
- Modify: `scripts/test_platform_topology_v2.py`

**Interfaces:**
- Consumes: `render_readme_table()` from Task 2.
- Produces: a README ownership table that cannot silently drift from topology v2.

- [ ] **Step 1: Add markers and projection check test**

Use exact markers:

```markdown
<!-- platform-topology-v2:start -->
...
<!-- platform-topology-v2:end -->
```

Add functions:

```python
def replace_marked_block(document: str, rendered: str) -> str: ...
def extract_marked_block(document: str) -> str: ...
```

Test:

```python
def test_readme_topology_block_matches_generated_projection(self):
    readme = README.read_text(encoding="utf-8")
    self.assertEqual(extract_marked_block(readme).strip(), render_readme_table(load_topology(TOPOLOGY)).strip())
```

- [ ] **Step 2: Run RED test**

```bash
python scripts/test_platform_topology_v2.py
```

Expected: marker/projection failure.

- [ ] **Step 3: Replace manual “Core ownership boundaries” table**

Generate the v2 table and place it between markers. Update nearby text to state:

```text
platform-topology/2.0 = slow-changing repository/ownership truth
org-state/1.0         = fast-changing exact-head GitHub truth
```

Keep public explanatory prose, but stop maintaining a second hand-authored ownership table.

- [ ] **Step 4: Add CLI check/write behavior**

CLI:

```bash
python scripts/platform_topology.py check-readme
python scripts/platform_topology.py write-readme
```

`check-readme` exits 1 on drift. `write-readme` only replaces the marked block.

- [ ] **Step 5: Run gates**

```bash
python scripts/platform_topology.py check
python scripts/platform_topology.py check-readme
python scripts/test_platform_topology_v2.py
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add README.md scripts/platform_topology.py scripts/test_platform_topology_v2.py
git commit -m "feat(governance): derive readme topology from canonical data"
```

---

### Task 7: Add merge-queue CI gate for topology truth convergence

**Files:**
- Create: `.github/workflows/platform-topology.yml`
- Modify: `.github/workflows/platform-fabrics.yml` only if required to include V4 canonical-doc path changes; do not combine the jobs.

**Interfaces:**
- Consumes: all Task 1-6 validators/tests.
- Produces: PR/main check `Platform Topology Truth / topology`.

- [ ] **Step 1: Create workflow**

Use:

```yaml
name: Platform Topology Truth

on:
  pull_request:
    paths:
      - 'docs/platform-topology/**'
      - 'docs/PLATFORM-ARCHITECTURE-V*.md'
      - 'docs/PLATFORM-RECONCILIATION-V1.md'
      - 'docs/cross-repo-contracts.md'
      - 'docs/REPOSITORY-REGISTRY-v0.1.md'
      - 'dependencies.yml'
      - 'README.md'
      - 'scripts/platform_topology.py'
      - 'scripts/test_platform_topology_v2.py'
      - 'scripts/test_org_state_topology_v2.py'
      - 'scripts/org-state-verify.sh'
      - '.github/workflows/platform-topology.yml'
  push:
    branches: [main]
    paths:
      - 'docs/platform-topology/**'
      - 'docs/PLATFORM-ARCHITECTURE-V*.md'
      - 'dependencies.yml'
      - 'README.md'
      - 'scripts/platform_topology.py'
      - 'scripts/test_platform_topology_v2.py'
      - 'scripts/test_org_state_topology_v2.py'
      - 'scripts/org-state-verify.sh'
      - '.github/workflows/platform-topology.yml'

permissions:
  contents: read

jobs:
  topology:
    runs-on: ubuntu-latest
    timeout-minutes: 5
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - name: Validate topology and projections
        run: |
          python scripts/test_platform_topology_v2.py
          python scripts/test_org_state_topology_v2.py
          python scripts/platform_topology.py check
          python scripts/platform_topology.py check-readme
          bash -n scripts/org-state-verify.sh
```

Do not run authenticated GitHub org-state generation in ordinary pull-request CI.

- [ ] **Step 2: Validate workflow syntax structurally**

Use local grep/Python checks already available in the repo. At minimum:

```bash
python - <<'PY'
from pathlib import Path
p = Path('.github/workflows/platform-topology.yml')
text = p.read_text()
for required in ('Platform Topology Truth', 'python-version: \'3.12\'', 'test_platform_topology_v2.py', 'test_org_state_topology_v2.py'):
    assert required in text, required
print('workflow-source-ok')
PY
```

Expected: `workflow-source-ok`.

- [ ] **Step 3: Run full local Governance suite relevant to the change**

```bash
python scripts/test_platform_topology_v2.py
python scripts/test_org_state_topology_v2.py
python scripts/test_platform_fabrics_v0_1.py
python scripts/test_governance_exact_head_truth.py
bash -n scripts/org-state-verify.sh
```

Expected: all PASS.

- [ ] **Step 4: Commit**

```bash
git add .github/workflows/platform-topology.yml
git commit -m "ci(governance): gate topology truth convergence"
```

---

### Task 8: Generate fresh exact-head evidence and close Wave A

**Files:**
- Regenerate through tool/script only: `latest-org-state.json`
- Modify: `docs/PLATFORM-RECONCILIATION-V1.md`
- Create: `docs/evidence/platform-architecture-v4-wave-a.json`

**Interfaces:**
- Consumes: merged/merge-queue candidate with topology v2 and generator binding.
- Produces: exact-head evidence that all 24 topology repositories resolve and the Wave A Governance files agree.

- [ ] **Step 1: Run authenticated exact-head generation on an authorized runner**

```bash
bash scripts/org-state-verify.sh latest-org-state.json
```

Expected stderr ends with:

```text
✓ org-state written: ... (24 repos)
DONE
```

If any repository cannot resolve, branch/canonical-default differs, or role is invalid, stop. Do not hand-edit the snapshot.

- [ ] **Step 2: Verify generated snapshot has exact topology membership**

```bash
python - <<'PY'
import json
from pathlib import Path
root = Path('.')
top = json.loads((root/'docs/platform-topology/2.0.json').read_text())
org = json.loads((root/'latest-org-state.json').read_text())
expected = {f"Aftergraph/{r['name']}" for r in top['repositories']}
actual = {r['full_name'] for r in org['repositories']}
assert actual == expected, (sorted(expected-actual), sorted(actual-expected))
print('24-repo-exact-head-membership-ok')
PY
```

- [ ] **Step 3: Write evidence record**

`docs/evidence/platform-architecture-v4-wave-a.json`:

```json
{
  "schema": "platform-architecture-v4-wave-a-evidence/1.0",
  "architecture": "PLATFORM-ARCHITECTURE-V4",
  "topology": "platform-topology/2.0",
  "org_state": "org-state/1.0",
  "repository_count": 24,
  "checks": [
    "topology_v2",
    "dependency_projection",
    "readme_projection",
    "org_state_binding",
    "platform_fabrics_regression"
  ],
  "result": "PASS"
}
```

Do not embed manually copied repository SHAs in this evidence file; `latest-org-state.json` is the exact-head artifact.

- [ ] **Step 4: Update reconciliation ledger**

In `PLATFORM-RECONCILIATION-V1.md`, mark old 19-repo topology work as historical completion and add the 24-repo/V4 truth-convergence evidence reference. Do not mark runtime/Fabric waves complete.

- [ ] **Step 5: Run final local regression**

```bash
python scripts/test_platform_topology_v2.py
python scripts/test_org_state_topology_v2.py
python scripts/test_platform_fabrics_v0_1.py
python scripts/test_governance_exact_head_truth.py
python scripts/platform_topology.py check
python scripts/platform_topology.py check-readme
bash -n scripts/org-state-verify.sh
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add latest-org-state.json docs/evidence/platform-architecture-v4-wave-a.json docs/PLATFORM-RECONCILIATION-V1.md
git commit -m "evidence(governance): close platform architecture v4 wave a"
```

- [ ] **Step 7: Merge through queue only after required checks are green**

Do not bypass branch protections. Wave A is complete only when the merge-queue result is on `main` and a fresh `main` exact-head snapshot can be regenerated successfully.

---

## Plan self-review

### Spec coverage

Wave A covers the approved spec requirements that are prerequisites for all other waves:

- topology/2.0 separates `architecture_plane` from `system_class`;
- current 24-repository scope is canonical and machine validated;
- V4 seven-plane ownership becomes canonical human documentation;
- V3 remains historical rather than silently rewritten;
- dependencies, README, registry, contract register and org-state generator stop disagreeing about current repo identity;
- exact heads remain generated remote truth;
- no new authority/execution semantics are introduced in Governance.

World State, Commitment runtime behavior, Tenant/Consent implementations, AVC code movement, Pocket, voice, capability resolver, agents and Golden Mission runtime composition are deliberately outside this plan and receive later plans.

### Placeholder scan

No `TBD`, `TODO`, “implement later”, unspecified test or unnamed owner is required to execute Wave A. Deferred subsystems are explicitly excluded rather than hidden as placeholders.

### Type/name consistency

- canonical topology version: `platform-topology/2.0`;
- current exact-state output: `org-state/1.0`;
- canonical current Work Intelligence repos: `wi-backend`, `wi-frontend`;
- canonical Runtime repo: `runtime`;
- legacy repo role in v2: `legacy-migration-source`;
- topology utility module: `scripts/platform_topology.py`;
- topology test: `scripts/test_platform_topology_v2.py`;
- org-state binding test: `scripts/test_org_state_topology_v2.py`.

## Wave A completion gate

Wave A is complete only when all of the following are true on merged `main`:

```text
platform-topology/2.0 exists and validates
24 unique repositories are represented
seven and only seven permanent semantic plane values are used
dependencies.yml module/repo/role projection matches topology
README generated topology block matches topology
PLATFORM-ARCHITECTURE-V4 is canonical
PLATFORM-ARCHITECTURE-V3 is marked superseded
current contract/registry docs use current repo identities
org-state-verify.sh consumes topology/2.0
org-state/1.0 remains backwards readable
fresh authenticated 24-repo latest-org-state generation succeeds
existing Platform Fabrics v0.1 regression stays green
merge-queue checks are green on the merged head
```
