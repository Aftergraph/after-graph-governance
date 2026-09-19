# Aftergraph Release Intelligence Phase 0/1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the smallest executable Aftergraph Release Intelligence slice that can represent component releases, compatibility edges, APC-1 profile conformance, and Release Passports with exact provenance without forcing lockstep repository versions.

**Architecture:** Governance owns the normative schemas and APC-1 rules. A stdlib-only Python toolchain loads component manifests and compatibility edges, compiles deterministic `PASS` / `FAIL` / `UNKNOWN` / `N/A` results, queries a provenance-aware compatibility graph, and emits a Release Passport only when the required evidence is sufficient. The implementation stays inside `Aftergraph/after-graph-governance` for the first milestone; no cross-repo rollout or runtime negotiation is included.

**Tech Stack:** JSON Schema Draft 2020-12 artifacts; Python 3 standard library (`json`, `argparse`, `dataclasses`, `enum`, `hashlib`, `pathlib`, `unittest`); GitHub Actions; existing Governance contract conventions.

**Spec:** `docs/superpowers/specs/2026-09-07-aftergraph-release-lifecycle-compatibility-standard-design.md` and `docs/superpowers/specs/2026-09-07-aftergraph-release-intelligence-plane-design.md`

## Global Constraints

- Public generation is `Aftergraph 26`; it is not a package/API/model version.
- Release trains use identifiers such as `2026.09`.
- Technical compatibility baseline is `APC-1`.
- Initial APC profiles are `authority`, `service`, `runtime`, `execution`, `verifier`, `product`, `model`, and `research`.
- Compatibility evidence levels are `CE0` through `CE5`; they apply to specific claims/edges and never imply whole-platform evidence.
- `UNKNOWN`, `INCOMPATIBLE`/`FAIL`, `STALE`, `N/A`, and `PASS` remain semantically distinct.
- `Complete != Verified` remains intact.
- A declaration is not evidence by itself.
- Runtime remains planned; do not create or claim an `APC-1/runtime` implementation merely to fill the plane.
- Sentinel remains software-domain verification; ARI does not make Sentinel the universal verifier.
- No new external Python dependency is required for the first milestone.
- Governance owns compatibility semantics; component repositories eventually own their own declarations/evidence.
- No synchronized `26.x` repository version rewrite.
- No runtime handshake, release digital twin, production telemetry, SaaS productization, or AI release authority in this milestone.

---

## File Structure

### Normative machine artifacts

- `docs/contracts/aftergraph-component/1.0.json` — JSON Schema for a component release declaration.
- `docs/contracts/compatibility-edge/1.0.json` — JSON Schema for an evidence-backed compatibility relationship.
- `docs/contracts/release-passport/1.0.json` — JSON Schema for an exact-subject Release Passport.
- `docs/release-intelligence/apc-1.json` — APC-1 common baseline, profile registry, lifecycle values, CE0-CE5 evidence levels, and minimum profile requirements.
- `docs/release-intelligence/examples/sentinel.component.json` — synthetic verifier-profile manifest used for docs/tests; no live SHA claim.
- `docs/release-intelligence/examples/sentinel-works.edge.json` — synthetic compatibility edge used for docs/tests.

### Python implementation

- `scripts/ari_model.py` — focused data loading, validation primitives, enums, deterministic canonical JSON and evidence-state helpers.
- `scripts/ari_graph.py` — compatibility graph index/query logic; no CLI policy decisions.
- `scripts/ari_compile.py` — APC compiler and CLI that evaluates manifests and required graph edges.
- `scripts/ari_passport.py` — Release Passport builder; refuses emission when required conformance/evidence is insufficient.

### Tests

- `scripts/test_ari_contracts.py` — schema/registry invariants and example-shape tests.
- `scripts/test_ari_graph.py` — graph edge indexing/query/state tests.
- `scripts/test_ari_compile.py` — PASS/FAIL/UNKNOWN/N/A compiler behavior tests.
- `scripts/test_ari_passport.py` — exact provenance and passport refusal/success tests.

### CI and discoverability

- `.github/workflows/release-intelligence.yml` — stdlib unit-test and JSON syntax gate.
- `docs/cross-repo-contracts.md` — register ARI contract families and Governance ownership.
- `README.md` — link ARS/APC/ARI and provide the canonical local verification commands.

---

### Task 1: Freeze ARI machine contracts and APC-1 registry

**Files:**
- Create: `docs/contracts/aftergraph-component/1.0.json`
- Create: `docs/contracts/compatibility-edge/1.0.json`
- Create: `docs/contracts/release-passport/1.0.json`
- Create: `docs/release-intelligence/apc-1.json`
- Create: `docs/release-intelligence/examples/sentinel.component.json`
- Create: `docs/release-intelligence/examples/sentinel-works.edge.json`
- Create: `scripts/test_ari_contracts.py`

**Interfaces:**
- Consumes: ARS/1 and ARI design specs.
- Produces: schema identifiers `aftergraph-component/1.0`, `compatibility-edge/1.0`, `release-passport/1.0`; APC registry identifier `APC-1`; lifecycle enum; CE0-CE5 evidence vocabulary used by every later task.

- [ ] **Step 1: Write the failing contract tests**

Create `scripts/test_ari_contracts.py` with tests that assert exact normative constants before any contract files exist:

```python
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACTS = ROOT / "docs" / "contracts"
ARI = ROOT / "docs" / "release-intelligence"


class AriContractsTest(unittest.TestCase):
    def load(self, path: Path):
        self.assertTrue(path.is_file(), f"missing artifact: {path.relative_to(ROOT)}")
        return json.loads(path.read_text(encoding="utf-8"))

    def test_apc_1_freezes_profile_and_evidence_vocabularies(self):
        apc = self.load(ARI / "apc-1.json")
        self.assertEqual(apc["schema"], "aftergraph.apc/1")
        self.assertEqual(apc["level"], "APC-1")
        self.assertEqual(
            apc["profiles"],
            ["authority", "service", "runtime", "execution", "verifier", "product", "model", "research"],
        )
        self.assertEqual(list(apc["evidence_levels"]), ["CE0", "CE1", "CE2", "CE3", "CE4", "CE5"])

    def test_component_schema_separates_generation_compatibility_and_version(self):
        schema = self.load(CONTRACTS / "aftergraph-component" / "1.0.json")
        props = schema["properties"]
        self.assertIn("platform", props)
        self.assertIn("compatibility", props)
        self.assertIn("release", props)
        self.assertEqual(props["platform"]["properties"]["generation"]["const"], 26)
        self.assertEqual(props["compatibility"]["properties"]["level"]["const"], "APC-1")

    def test_edge_requires_subjects_relation_state_and_evidence(self):
        schema = self.load(CONTRACTS / "compatibility-edge" / "1.0.json")
        self.assertEqual(
            schema["required"],
            ["schema", "from", "to", "relation", "state", "evidence_level", "evidence"],
        )

    def test_passport_requires_exact_source_and_artifact_identity(self):
        schema = self.load(CONTRACTS / "release-passport" / "1.0.json")
        provenance = schema["properties"]["provenance"]
        self.assertEqual(provenance["required"], ["repository", "commit", "artifact_digest"])


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the contract test and verify RED**

Run:

```bash
python -m unittest scripts.test_ari_contracts -v
```

Expected: FAIL because the ARI contract/registry files do not exist.

- [ ] **Step 3: Create the three strict JSON Schemas**

The component schema must require:

```json
{
  "schema": "aftergraph-component/1.0",
  "identity": {"component": "sentinel-engine", "product": "sentinel"},
  "release": {"version": "1.4.0", "lifecycle": "preview"},
  "platform": {"generation": 26, "release_train": "2026.09"},
  "compatibility": {
    "level": "APC-1",
    "profiles": ["verifier"],
    "minimum": "APC-1",
    "tested_against": "APC-1"
  },
  "contracts": {},
  "provenance": {"repository": "Aftergraph/sentinel", "commit": "<40 lowercase hex>"}
}
```

Normative schema rules:

```text
additionalProperties: false at every owned object boundary
release.lifecycle enum: stable, preview, experimental, research, legacy, deprecated, retired, ephemeral
platform.generation const: 26
platform.release_train pattern: ^20[0-9]{2}\.(0[1-9]|1[0-2])$
compatibility.level/minimum/tested_against const: APC-1 for v1
profiles uniqueItems true and enum from APC-1 profiles
commit pattern: ^[a-f0-9]{40}$
contract names and versions remain strings; no implied contract compatibility
```

The compatibility-edge schema must require exact endpoint identity:

```json
{
  "schema": "compatibility-edge/1.0",
  "from": {"component": "sentinel-engine", "version": "1.4.0", "commit": "..."},
  "to": {"component": "works", "version": "0.5.1", "commit": "..."},
  "relation": "tested-with",
  "state": "pass",
  "evidence_level": "CE3",
  "evidence": [{"kind": "test-receipt", "ref": "sha256:..."}]
}
```

Allowed edge states:

```text
pass
fail
unknown
stale
not-applicable
```

Allowed relations for v1:

```text
requires
tested-with
incompatible-with
conforms-to
supports
```

The release-passport schema must require exact `repository`, `commit`, and `artifact_digest`, plus conformance result and evidence references.

- [ ] **Step 4: Create `docs/release-intelligence/apc-1.json`**

Use this exact top-level shape:

```json
{
  "schema": "aftergraph.apc/1",
  "level": "APC-1",
  "public_generation": 26,
  "profiles": ["authority", "service", "runtime", "execution", "verifier", "product", "model", "research"],
  "lifecycle": ["stable", "preview", "experimental", "research", "legacy", "deprecated", "retired", "ephemeral"],
  "evidence_levels": {
    "CE0": "declared",
    "CE1": "schema-compatible",
    "CE2": "contract-tested",
    "CE3": "integration-verified",
    "CE4": "failure-or-upgrade-tested",
    "CE5": "production-evidenced"
  },
  "profile_requirements": {
    "verifier": {"minimum_edge_evidence": "CE2", "required_contracts": ["correlation"]},
    "execution": {"minimum_edge_evidence": "CE2", "required_contracts": ["correlation"]},
    "service": {"minimum_edge_evidence": "CE1", "required_contracts": []},
    "authority": {"minimum_edge_evidence": "CE1", "required_contracts": []},
    "product": {"minimum_edge_evidence": "CE1", "required_contracts": []},
    "model": {"minimum_edge_evidence": "CE1", "required_contracts": []},
    "research": {"minimum_edge_evidence": "CE0", "required_contracts": []},
    "runtime": {"minimum_edge_evidence": "CE2", "required_contracts": ["correlation"]}
  }
}
```

These initial requirements are intentionally minimal. They prove executable APC mechanics; they do not claim the complete future conformance suite already exists.

- [ ] **Step 5: Add synthetic examples**

Use commits made only of repeated hex digits such as `1111...` and `2222...` so examples are unmistakably synthetic. Do not use live repository heads in normative examples.

- [ ] **Step 6: Run syntax and contract tests**

Run:

```bash
python -m unittest scripts.test_ari_contracts -v
python -m json.tool docs/contracts/aftergraph-component/1.0.json >/dev/null
python -m json.tool docs/contracts/compatibility-edge/1.0.json >/dev/null
python -m json.tool docs/contracts/release-passport/1.0.json >/dev/null
python -m json.tool docs/release-intelligence/apc-1.json >/dev/null
```

Expected: all tests PASS and all JSON parses successfully.

- [ ] **Step 7: Commit**

```bash
git add docs/contracts docs/release-intelligence scripts/test_ari_contracts.py
git commit -m "feat(governance): freeze APC-1 release intelligence contracts"
```

---

### Task 2: Build shared ARI validation/model primitives

**Files:**
- Create: `scripts/ari_model.py`
- Create: `scripts/test_ari_model.py`

**Interfaces:**
- Consumes: contract constants from Task 1.
- Produces:
  - `ResultState` enum with `PASS`, `FAIL`, `UNKNOWN`, `STALE`, `N_A`.
  - `EvidenceLevel` enum ordered CE0..CE5.
  - `load_json(path: Path) -> dict`.
  - `canonical_digest(document: dict) -> str` returning `sha256:<hex>`.
  - `validate_component(document: dict) -> list[str]`.
  - `validate_edge(document: dict) -> list[str]`.
  - `evidence_meets(actual: str, minimum: str) -> bool`.

- [ ] **Step 1: Write failing unit tests**

Create `scripts/test_ari_model.py` with cases for evidence ordering, strict required fields, invalid commit IDs, unknown profile names, and deterministic canonical digest:

```python
class AriModelTest(unittest.TestCase):
    def test_evidence_order_is_monotonic(self):
        self.assertTrue(evidence_meets("CE3", "CE2"))
        self.assertTrue(evidence_meets("CE2", "CE2"))
        self.assertFalse(evidence_meets("CE1", "CE2"))

    def test_digest_is_key_order_independent(self):
        self.assertEqual(canonical_digest({"a": 1, "b": 2}), canonical_digest({"b": 2, "a": 1}))
```

Include a manifest fixture where `compatibility.profiles = ["banana"]`; expect `validate_component()` to report `unsupported APC-1 profile: banana`.

- [ ] **Step 2: Run RED**

```bash
python -m unittest scripts.test_ari_model -v
```

Expected: FAIL because `scripts.ari_model` does not exist.

- [ ] **Step 3: Implement minimal stdlib model helpers**

Use enums rather than free-form strings:

```python
class ResultState(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    UNKNOWN = "UNKNOWN"
    STALE = "STALE"
    N_A = "N/A"


class EvidenceLevel(IntEnum):
    CE0 = 0
    CE1 = 1
    CE2 = 2
    CE3 = 3
    CE4 = 4
    CE5 = 5
```

Canonical digest must use:

```python
payload = json.dumps(document, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
return "sha256:" + hashlib.sha256(payload).hexdigest()
```

Validation remains hand-rolled and stdlib-only, matching existing Governance practice. It must reject missing required fields and malformed identifiers even when the optional `jsonschema` package is unavailable.

- [ ] **Step 4: Run GREEN**

```bash
python -m unittest scripts.test_ari_model -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add scripts/ari_model.py scripts/test_ari_model.py
git commit -m "feat(governance): add ARI validation primitives"
```

---

### Task 3: Implement provenance-aware Compatibility Graph

**Files:**
- Create: `scripts/ari_graph.py`
- Create: `scripts/test_ari_graph.py`

**Interfaces:**
- Consumes: `validate_edge`, `EvidenceLevel`, `ResultState` from `ari_model.py`.
- Produces:
  - `Endpoint(component: str, version: str, commit: str)`.
  - `CompatibilityEdge` dataclass.
  - `CompatibilityGraph.add(edge_doc: dict) -> None`.
  - `CompatibilityGraph.between(left: Endpoint, right: Endpoint) -> list[CompatibilityEdge]`.
  - `CompatibilityGraph.best_state(left, right, minimum_evidence) -> ResultState`.

- [ ] **Step 1: Write failing graph tests**

Required cases:

```text
CE3 pass edge + minimum CE2 -> PASS
CE1 pass edge + minimum CE2 -> UNKNOWN (claim exists but proof is insufficient)
explicit fail edge -> FAIL
stale edge -> STALE
no edge -> UNKNOWN
reverse endpoint query must not match a directional `requires` edge
```

- [ ] **Step 2: Run RED**

```bash
python -m unittest scripts.test_ari_graph -v
```

Expected: FAIL because graph implementation does not exist.

- [ ] **Step 3: Implement graph indexing**

Index by full exact endpoint tuple, not only version strings:

```python
(component, version, commit)
```

For v1, `tested-with` may be treated as symmetric for lookup; `requires`, `supports`, `incompatible-with`, and `conforms-to` remain directional.

State precedence when multiple exact edges exist:

```text
FAIL > STALE > PASS > UNKNOWN
```

A PASS below the requested CE threshold yields `UNKNOWN`, never PASS.

- [ ] **Step 4: Run GREEN**

```bash
python -m unittest scripts.test_ari_graph -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add scripts/ari_graph.py scripts/test_ari_graph.py
git commit -m "feat(governance): add ARI compatibility graph"
```

---

### Task 4: Implement the APC Compiler and CLI

**Files:**
- Create: `scripts/ari_compile.py`
- Create: `scripts/test_ari_compile.py`

**Interfaces:**
- Consumes: component manifest, APC registry, optional compatibility-edge documents, graph/model helpers.
- Produces:
  - `CompileResult(state: ResultState, profile_results: dict[str, ResultState], errors: list[str], unknowns: list[str])`.
  - `compile_component(manifest, apc, edges) -> CompileResult`.
  - CLI: `python scripts/ari_compile.py component.json --edge edge.json --format json|text`.

- [ ] **Step 1: Write compiler tests before implementation**

Required deterministic cases:

```text
invalid component manifest                              -> FAIL
unknown requested APC profile                           -> FAIL
no applicable profile                                   -> N/A
profile requirements met + sufficient edges             -> PASS
required exact edge absent                              -> UNKNOWN
edge exists but below profile minimum CE level           -> UNKNOWN
explicit incompatible/fail required edge                -> FAIL
stale exact-subject edge                                -> STALE
```

Use synthetic manifests in temporary directories so tests do not depend on moving repository HEADs.

- [ ] **Step 2: Run RED**

```bash
python -m unittest scripts.test_ari_compile -v
```

Expected: FAIL because compiler does not exist.

- [ ] **Step 3: Implement compile order exactly**

Compiler evaluation order:

```text
1. validate manifest shape
2. validate APC level == APC-1
3. validate declared profiles
4. check profile-required contracts are declared
5. build exact-endpoint graph from provided edges
6. evaluate explicit required edges from manifest compatibility.requires_edges, if present
7. apply profile minimum evidence threshold
8. aggregate without converting UNKNOWN/STALE to PASS
```

Add optional manifest field in the component schema:

```json
"requires_edges": [
  {
    "component": "works",
    "version": "0.5.1",
    "commit": "2222222222222222222222222222222222222222"
  }
]
```

If this schema addition is required by compiler tests, update Task 1 schema and tests in the same implementation commit as the compiler so schema and behavior remain atomic.

- [ ] **Step 4: Implement CLI output**

Text output example:

```text
APC-1/verifier: PASS
component: sentinel-engine@1.4.0
required edges: 1
minimum edge evidence: CE2
unknown required edges: 0
errors: 0
```

JSON output must include stable keys:

```json
{
  "schema": "aftergraph.apc-result/1",
  "state": "PASS",
  "component": "sentinel-engine",
  "version": "1.4.0",
  "profiles": {"verifier": "PASS"},
  "errors": [],
  "unknowns": []
}
```

Exit codes:

```text
0 PASS or N/A
2 FAIL
3 UNKNOWN or STALE
```

- [ ] **Step 5: Run GREEN and CLI smoke**

```bash
python -m unittest scripts.test_ari_compile -v
python scripts/ari_compile.py docs/release-intelligence/examples/sentinel.component.json --edge docs/release-intelligence/examples/sentinel-works.edge.json --format json
```

Expected: tests PASS; example compile returns deterministic JSON and exit 0.

- [ ] **Step 6: Commit**

```bash
git add docs/contracts/aftergraph-component/1.0.json scripts/ari_compile.py scripts/test_ari_compile.py
git commit -m "feat(governance): compile APC-1 component conformance"
```

---

### Task 5: Generate exact-subject Release Passports

**Files:**
- Create: `scripts/ari_passport.py`
- Create: `scripts/test_ari_passport.py`

**Interfaces:**
- Consumes: validated component manifest, `CompileResult`, exact artifact digest supplied by caller.
- Produces:
  - `build_passport(manifest: dict, compile_result: CompileResult, artifact_digest: str) -> dict`.
  - CLI: `python scripts/ari_passport.py component.json --artifact-digest sha256:<64hex> [--edge ...]`.

- [ ] **Step 1: Write failing passport tests**

Required cases:

```text
compile PASS + exact 40-hex commit + valid sha256 artifact -> passport emitted
compile UNKNOWN                                           -> refusal
compile STALE                                             -> refusal
compile FAIL                                              -> refusal
invalid artifact digest                                   -> refusal
passport provenance commit differs from manifest          -> impossible by construction
passport contains canonical manifest digest               -> yes
```

- [ ] **Step 2: Run RED**

```bash
python -m unittest scripts.test_ari_passport -v
```

Expected: FAIL because passport builder does not exist.

- [ ] **Step 3: Implement passport refusal semantics**

Only `ResultState.PASS` may emit a v1 Release Passport. `N/A` is not enough because a Release Passport is a positive technical release/conformance claim.

Passport payload must include:

```json
{
  "schema": "release-passport/1.0",
  "subject": {
    "component": "sentinel-engine",
    "version": "1.4.0"
  },
  "platform": {
    "generation": 26,
    "release_train": "2026.09",
    "compatibility": "APC-1"
  },
  "conformance": {
    "result": "PASS",
    "profiles": {"verifier": "PASS"}
  },
  "provenance": {
    "repository": "Aftergraph/sentinel",
    "commit": "1111111111111111111111111111111111111111",
    "artifact_digest": "sha256:<64hex>",
    "manifest_digest": "sha256:<64hex>"
  }
}
```

- [ ] **Step 4: Run GREEN and deterministic repeat test**

Run the same passport generation twice and compare output bytes after canonical JSON formatting:

```bash
python -m unittest scripts.test_ari_passport -v
```

Expected: PASS including deterministic-output assertion.

- [ ] **Step 5: Commit**

```bash
git add scripts/ari_passport.py scripts/test_ari_passport.py
git commit -m "feat(governance): generate evidence-bound release passports"
```

---

### Task 6: Add repository-wide verification gate and documentation registry

**Files:**
- Create: `.github/workflows/release-intelligence.yml`
- Modify: `docs/cross-repo-contracts.md`
- Modify: `README.md`

**Interfaces:**
- Consumes: all Task 1-5 artifacts.
- Produces: CI enforcement and canonical discoverability for ARS/APC/ARI.

- [ ] **Step 1: Add a failing discoverability assertion to `scripts/test_ari_contracts.py`**

Test that `docs/cross-repo-contracts.md` names all three ARI contract families and declares `after-graph-governance` as owner, and that README links both design specs plus `docs/release-intelligence/apc-1.json`.

- [ ] **Step 2: Run RED**

```bash
python -m unittest scripts.test_ari_contracts -v
```

Expected: FAIL until docs are updated.

- [ ] **Step 3: Register the contract families**

Add rows/entries to `docs/cross-repo-contracts.md` for:

```text
aftergraph-component/1.0   owner: after-graph-governance
compatibility-edge/1.0     owner: after-graph-governance
release-passport/1.0       owner: after-graph-governance
```

State explicitly that these contracts govern release metadata/compatibility evidence and do not transfer runtime authority or scientific validity.

- [ ] **Step 4: Add README entry point**

Add a compact section:

```text
Aftergraph 26 · Convergence
Release standard: ARS/1
Platform compatibility: APC-1
Release Intelligence: ARI
```

Link the two specs, APC registry, and local commands.

- [ ] **Step 5: Add CI workflow**

Use Python 3.12 and only stdlib commands:

```yaml
name: Release Intelligence
on:
  pull_request:
    paths:
      - 'docs/contracts/aftergraph-component/**'
      - 'docs/contracts/compatibility-edge/**'
      - 'docs/contracts/release-passport/**'
      - 'docs/release-intelligence/**'
      - 'scripts/ari_*.py'
      - 'scripts/test_ari_*.py'
      - '.github/workflows/release-intelligence.yml'
  push:
    branches: [main]
    paths:
      - 'docs/contracts/aftergraph-component/**'
      - 'docs/contracts/compatibility-edge/**'
      - 'docs/contracts/release-passport/**'
      - 'docs/release-intelligence/**'
      - 'scripts/ari_*.py'
      - 'scripts/test_ari_*.py'
      - '.github/workflows/release-intelligence.yml'

jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: python -m unittest discover -s scripts -p 'test_ari_*.py' -v
      - run: python -m json.tool docs/release-intelligence/apc-1.json >/dev/null
      - run: python -m json.tool docs/contracts/aftergraph-component/1.0.json >/dev/null
      - run: python -m json.tool docs/contracts/compatibility-edge/1.0.json >/dev/null
      - run: python -m json.tool docs/contracts/release-passport/1.0.json >/dev/null
```

- [ ] **Step 6: Run full local ARI verification**

```bash
python -m unittest discover -s scripts -p 'test_ari_*.py' -v
python -m json.tool docs/release-intelligence/apc-1.json >/dev/null
python -m json.tool docs/contracts/aftergraph-component/1.0.json >/dev/null
python -m json.tool docs/contracts/compatibility-edge/1.0.json >/dev/null
python -m json.tool docs/contracts/release-passport/1.0.json >/dev/null
```

Expected: all PASS.

- [ ] **Step 7: Run existing Governance regression tests**

```bash
python -m unittest \
  scripts.test_platform_convergence_v2_1_contracts \
  scripts.test_governance_ci_result \
  scripts.test_governance_ci_truth_reducer \
  scripts.test_governance_clean_room \
  scripts.test_governance_exact_head_truth \
  scripts.test_verify_brand_assets -v
```

Expected: existing suite remains green. If a pre-existing test fails on the untouched base, record it separately rather than weakening ARI assertions.

- [ ] **Step 8: Commit**

```bash
git add .github/workflows/release-intelligence.yml README.md docs/cross-repo-contracts.md scripts/test_ari_contracts.py
git commit -m "ci(governance): gate release intelligence contracts"
```

---

### Task 7: End-to-end proof of the Phase 0/1 thesis

**Files:**
- Create: `docs/release-intelligence/PHASE-0-1-PROOF.md`
- Test: reuse `scripts/test_ari_*.py`

**Interfaces:**
- Consumes: the complete Phase 0/1 implementation.
- Produces: a reproducible proof that independently versioned components can receive an evidence-backed compatibility result and Release Passport without synchronized versions.

- [ ] **Step 1: Define a synthetic mixed-version proof configuration**

Use:

```text
Sentinel engine 1.4.0 / commit 111... / APC-1/verifier
WORKS 0.5.1          / commit 222... / APC-1/execution
compatibility edge   / tested-with / CE3 / PASS
release train         2026.09
```

Neither component uses version `26`.

- [ ] **Step 2: Run compiler against the proof configuration**

```bash
python scripts/ari_compile.py \
  docs/release-intelligence/examples/sentinel.component.json \
  --edge docs/release-intelligence/examples/sentinel-works.edge.json \
  --format text
```

Expected:

```text
APC-1/verifier: PASS
```

- [ ] **Step 3: Generate a passport**

Use a deterministic synthetic artifact digest:

```text
sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
```

Run:

```bash
python scripts/ari_passport.py \
  docs/release-intelligence/examples/sentinel.component.json \
  --edge docs/release-intelligence/examples/sentinel-works.edge.json \
  --artifact-digest sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
```

Expected: exit 0 and a valid `release-passport/1.0` JSON document.

- [ ] **Step 4: Prove fail-closed unknown behavior**

Repeat compile without `--edge`.

Expected: `UNKNOWN`, exit 3, and no Release Passport can be emitted.

- [ ] **Step 5: Document the exact proof commands and outcomes**

`PHASE-0-1-PROOF.md` must state only what the synthetic proof establishes:

```text
PROVED: the Governance implementation can compute APC-1/verifier conformance from explicit exact-subject declarations and compatibility evidence and refuse a positive result when required edge evidence is absent.

NOT PROVED: production compatibility of live Sentinel/WORKS builds, runtime negotiation, deployment drift detection, or whole-platform APC-1 conformance.
```

- [ ] **Step 6: Run all verification again**

```bash
python -m unittest discover -s scripts -p 'test_ari_*.py' -v
python scripts/ari_compile.py docs/release-intelligence/examples/sentinel.component.json --edge docs/release-intelligence/examples/sentinel-works.edge.json --format json
```

Expected: all green and deterministic.

- [ ] **Step 7: Commit**

```bash
git add docs/release-intelligence/PHASE-0-1-PROOF.md
git commit -m "docs(governance): record ARI phase 0-1 executable proof"
```

---

## Plan self-review

### Spec coverage

- ARS/APC identity separation: Tasks 1 and 6.
- APC-1 common/profile registry: Task 1.
- Machine component manifest: Tasks 1-2.
- Compatibility Graph: Task 3.
- Deterministic APC Compiler: Task 4.
- PASS/FAIL/UNKNOWN/STALE/N/A separation: Tasks 2-4.
- Release Passport and exact provenance: Task 5.
- CE0-CE5 scoped evidence: Tasks 1-4.
- Mixed-version compatibility without lockstep: Tasks 3, 4, and 7.
- Fail-closed missing evidence: Tasks 4, 5, and 7.
- CI enforcement and canonical discoverability: Task 6.
- Runtime negotiation, digital twin, telemetry, simulation, external SaaS: intentionally deferred per spec.

### Type consistency

The plan uses one canonical state enum (`ResultState`), one evidence enum (`EvidenceLevel`), exact endpoint tuples `(component, version, commit)`, and one compile result object across graph/compiler/passport tasks.

### Scope check

This plan deliberately implements only Phase 0 plus the smallest useful Phase 1 slice. Semantic Contract Diff, Release Simulator, Admission Gate, production telemetry, drift detection, OCI/Sigstore integration, and customer productization require later plans after this proof lands.
