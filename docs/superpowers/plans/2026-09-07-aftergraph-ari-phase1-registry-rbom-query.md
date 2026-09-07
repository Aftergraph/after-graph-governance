# Aftergraph ARI Phase 1 Registry/RBOM/Query Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Complete the remaining Phase 1 ARI milestone with a deterministic derived Release Registry, RBOM v0, and exact-subject compatibility query CLI.

**Architecture:** Keep Governance as the semantic owner and keep component manifests/edges/passports as the source evidence. The Release Registry is a deterministic derived JSON artifact that embeds validated source documents with canonical digests; it is not a second source of truth. RBOM v0 derives an exact release composition from registry entries. Query tooling reads the registry and reuses the existing provenance-aware Compatibility Graph instead of inventing a second compatibility engine.

**Tech Stack:** Python 3.12 standard library; JSON Schema Draft 2020-12; existing `ari_model`, `ari_graph`, `ari_compile`, and `ari_passport`; `unittest`; GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-09-07-aftergraph-release-intelligence-plane-design.md` sections 4, 20, 23, 25, 26, 29.

## Global Constraints

- `Aftergraph 26` remains a public platform generation, not a component version.
- `APC-1` remains the technical compatibility baseline.
- Registry state is derived from source evidence and MUST be reproducible.
- Duplicate exact identities with divergent content MUST fail as `CONFLICT`; they MUST NOT silently pick a winner.
- Query results MUST preserve `PASS`, `FAIL`, `UNKNOWN`, `STALE`, and `N/A` distinctly.
- RBOM v0 is an inventory/evidence artifact, not a blanket compatibility certificate.
- No database, graph server, signing service, runtime handshake, telemetry, digital twin, or Phase 2 release simulation in this slice.
- No live Sentinel/WORKS production compatibility claim is created by synthetic fixtures.
- All new behavior follows RED → GREEN TDD.

---

## File Structure

### Contracts
- `docs/contracts/release-registry/1.0.json` — strict schema for the deterministic derived registry.
- `docs/contracts/rbom/0.1.json` — strict RBOM v0 schema.

### Implementation
- `scripts/ari_registry.py` — registry builder/validator/index; owns duplicate/conflict semantics.
- `scripts/ari_rbom.py` — exact composition builder from registry component/passport entries.
- `scripts/ari_query.py` — human/machine query CLI; delegates compatibility evaluation to `CompatibilityGraph`.

### Tests
- `scripts/test_ari_registry.py`
- `scripts/test_ari_rbom.py`
- `scripts/test_ari_query.py`
- extend `scripts/test_ari_contracts.py`

### CI/docs
- extend `.github/workflows/release-intelligence.yml`
- extend `README.md`
- extend `docs/cross-repo-contracts.md`
- add `docs/release-intelligence/PHASE-1-PROOF.md`

---

### Task 1: Freeze Release Registry and RBOM contracts

**Interfaces:**
- Produces schema IDs `release-registry/1.0` and `rbom/0.1`.
- Registry entry kind is one of `component`, `edge`, `passport`.
- Every registry entry contains `digest` plus the validated embedded `document`.
- RBOM component identity is exact: component, version, repository, commit, manifest digest; artifact/passport fields are optional unless a passport exists.

- [ ] **Step 1: Write failing schema tests**

Extend `scripts/test_ari_contracts.py` with:

```python
def test_release_registry_contract_is_derived_and_digest_bound(self):
    schema = self.load(CONTRACTS / "release-registry" / "1.0.json")
    self.assertEqual(schema["properties"]["schema"]["const"], "release-registry/1.0")
    entry = schema["$defs"]["entry"]
    self.assertEqual(entry["required"], ["kind", "digest", "document"])
    self.assertFalse(entry["additionalProperties"])


def test_rbom_contract_separates_inventory_from_verification(self):
    schema = self.load(CONTRACTS / "rbom" / "0.1.json")
    self.assertEqual(schema["properties"]["schema"]["const"], "rbom/0.1")
    self.assertIn("verification", schema["properties"])
    self.assertEqual(
        schema["properties"]["verification"]["properties"]["state"]["enum"],
        ["VERIFIED", "PARTIAL", "UNVERIFIED"],
    )
```

- [ ] **Step 2: Verify RED**

Run:

```bash
python -m unittest scripts.test_ari_contracts -v
```

Expected: FAIL because both schemas are missing.

- [ ] **Step 3: Implement strict schemas**

`release-registry/1.0` top-level shape:

```json
{
  "schema": "release-registry/1.0",
  "entries": [
    {
      "kind": "component",
      "digest": "sha256:<64hex>",
      "document": {}
    }
  ]
}
```

`rbom/0.1` top-level shape:

```json
{
  "schema": "rbom/0.1",
  "platform": {"generation": 26, "release_train": "2026.09", "compatibility": "APC-1"},
  "components": [],
  "contracts": [],
  "verification": {"state": "UNVERIFIED", "passport_count": 0, "component_count": 0},
  "registry_digest": "sha256:<64hex>"
}
```

Both schemas use `additionalProperties: false` at owned boundaries and sha256 digest patterns.

- [ ] **Step 4: Verify GREEN**

Run:

```bash
python -m unittest scripts.test_ari_contracts -v
python -m json.tool docs/contracts/release-registry/1.0.json >/dev/null
python -m json.tool docs/contracts/rbom/0.1.json >/dev/null
```

Expected: PASS.

---

### Task 2: Build deterministic Release Registry

**Interfaces:**
- `build_registry(documents: Iterable[dict]) -> dict`
- `Registry(document: dict)` validates/indexes a built registry.
- `Registry.components() -> list[dict]`
- `Registry.edges() -> list[dict]`
- `Registry.passports() -> list[dict]`
- exact component key: `(component, version, commit)`.
- divergent duplicate exact component keys raise `RegistryConflict`.

- [ ] **Step 1: Write failing registry tests**

Create `scripts/test_ari_registry.py` covering:

```python
def test_registry_is_deterministic_across_input_order(): ...
def test_registry_classifies_component_edge_and_passport(): ...
def test_registry_rejects_invalid_document(): ...
def test_registry_deduplicates_byte_semantically_identical_document(): ...
def test_registry_rejects_divergent_same_exact_component_identity(): ...
def test_registry_digest_changes_when_source_document_changes(): ...
def test_cli_builds_machine_readable_registry(): ...
```

The conflict test changes a valid component contract value while retaining the same component/version/commit and expects `RegistryConflict`.

- [ ] **Step 2: Verify RED**

Run:

```bash
python -m unittest scripts.test_ari_registry -v
```

Expected: import failure because `scripts.ari_registry` does not exist.

- [ ] **Step 3: Implement registry**

Classification rules:

```python
VALIDATORS = {
    "aftergraph-component/1.0": ("component", validate_component),
    "compatibility-edge/1.0": ("edge", validate_edge),
    "release-passport/1.0": ("passport", validate_passport),
}
```

Add `validate_passport(document) -> list[str]` to `ari_model.py` only for the passport fields the contract owns. It must reject non-PASS passport conformance and malformed digest/source fields.

`build_registry()`:
1. validate each source document;
2. compute `canonical_digest(document)`;
3. dedupe exact same digest;
4. reject divergent component documents with the same `(component, version, provenance.commit)`;
5. sort entries by `(kind, stable identity, digest)`;
6. return `{"schema":"release-registry/1.0","entries":[...]}`.

CLI:

```bash
python scripts/ari_registry.py build \
  --document component.json \
  --document edge.json \
  --document passport.json \
  --format json
```

No timestamps are inserted, preserving deterministic output.

- [ ] **Step 4: Verify GREEN**

Run:

```bash
python -m unittest scripts.test_ari_registry -v
```

Expected: PASS.

---

### Task 3: Build RBOM v0

**Interfaces:**
- `build_rbom(registry: Registry, selectors: Iterable[str]) -> dict`
- selector grammar: `component@version#40hexcommit`.
- duplicate selectors are rejected.
- missing exact component is an error, never silently resolved to latest.

- [ ] **Step 1: Write failing RBOM tests**

Create `scripts/test_ari_rbom.py` covering:

```python
def test_rbom_uses_exact_component_selector(): ...
def test_rbom_refuses_ambiguous_or_missing_selector(): ...
def test_rbom_contract_inventory_is_sorted_and_deduplicated(): ...
def test_rbom_verified_only_when_every_selected_component_has_matching_passport(): ...
def test_rbom_partial_when_only_some_components_have_matching_passports(): ...
def test_rbom_unverified_when_no_passports_match(): ...
def test_rbom_refuses_mixed_generation_or_apc_level(): ...
def test_cli_emits_deterministic_rbom(): ...
```

- [ ] **Step 2: Verify RED**

Run:

```bash
python -m unittest scripts.test_ari_rbom -v
```

Expected: import failure because `scripts.ari_rbom` does not exist.

- [ ] **Step 3: Implement RBOM**

For each selected exact manifest emit:

```json
{
  "component": "sentinel-engine",
  "version": "1.4.0",
  "repository": "Aftergraph/sentinel",
  "commit": "<40hex>",
  "manifest_digest": "sha256:<64hex>",
  "artifact_digest": "sha256:<64hex or omitted>",
  "passport_digest": "sha256:<64hex or omitted>"
}
```

Aggregate contracts by contract name and sorted unique versions:

```json
{"name":"correlation","versions":["1.0"]}
```

Verification state:
- `VERIFIED` only if every component has a matching exact Release Passport.
- `PARTIAL` if at least one but not all have a matching passport.
- `UNVERIFIED` if none have a matching passport.

This state describes passport coverage only. It does not upgrade CE level or whole-platform scientific assurance.

- [ ] **Step 4: Verify GREEN**

Run:

```bash
python -m unittest scripts.test_ari_rbom -v
```

Expected: PASS.

---

### Task 4: Add exact compatibility query CLI

**Interfaces:**
- `query_compat(registry: Registry, left: str, right: str, minimum: str) -> dict`
- exact selectors required for both sides.
- delegates state calculation to `CompatibilityGraph.best_state()`.

- [ ] **Step 1: Write failing query tests**

Create `scripts/test_ari_query.py` covering:

```python
def test_query_pass_for_exact_ce3_edge_at_ce2_minimum(): ...
def test_query_unknown_when_exact_edge_missing(): ...
def test_query_fail_for_reverse_incompatible_edge(): ...
def test_query_stale_is_not_pass(): ...
def test_query_rejects_non_exact_selector(): ...
def test_query_rejects_invalid_minimum_evidence_level(): ...
def test_cli_json_exit_codes_match_compiler_semantics(): ...
```

Exit codes:
- PASS/N/A → 0
- FAIL → 2
- UNKNOWN/STALE → 3
- invalid input → 2

- [ ] **Step 2: Verify RED**

Run:

```bash
python -m unittest scripts.test_ari_query -v
```

Expected: import failure because `scripts.ari_query` does not exist.

- [ ] **Step 3: Implement query CLI**

Command:

```bash
python scripts/ari_query.py compat registry.json \
  sentinel-engine@1.4.0#1111111111111111111111111111111111111111 \
  works@0.5.1#2222222222222222222222222222222222222222 \
  --minimum CE2 \
  --format json
```

Output includes:

```json
{
  "schema":"aftergraph.compat-query/1",
  "state":"PASS",
  "left":{},
  "right":{},
  "minimum_evidence":"CE2",
  "matching_edges":1,
  "evidence":[]
}
```

Do not duplicate compatibility precedence logic outside `CompatibilityGraph`.

- [ ] **Step 4: Verify GREEN**

Run:

```bash
python -m unittest scripts.test_ari_query -v
```

Expected: PASS.

---

### Task 5: CI, docs, and executable Phase 1 proof

**Files:**
- Modify `.github/workflows/release-intelligence.yml`
- Modify `README.md`
- Modify `docs/cross-repo-contracts.md`
- Create `docs/release-intelligence/PHASE-1-PROOF.md`

- [ ] **Step 1: Extend CI path coverage and JSON gates**

Add contract paths:

```yaml
- 'docs/contracts/release-registry/**'
- 'docs/contracts/rbom/**'
```

Add JSON checks:

```bash
python -m json.tool docs/contracts/release-registry/1.0.json >/dev/null
python -m json.tool docs/contracts/rbom/0.1.json >/dev/null
```

Existing `test_ari_*.py` discovery automatically includes registry/RBOM/query tests.

- [ ] **Step 2: Register contract ownership**

Add `release-registry/1.0` and `rbom/0.1` to `docs/cross-repo-contracts.md`, owner `after-graph-governance`, explicitly described as derived release-intelligence artifacts that grant no runtime authority.

- [ ] **Step 3: Add README commands**

Document registry build, exact compatibility query, and RBOM build without claiming live cross-repo compatibility.

- [ ] **Step 4: Add Phase 1 proof**

`PHASE-1-PROOF.md` must record exact synthetic inputs, registry digest, query outcome, RBOM state, and current CI evidence. Separate `PROVED` from `NOT PROVED`.

- [ ] **Step 5: Run final verification**

Run through GitHub Actions on the PR merge ref:

```text
all test_ari_*.py
existing Governance regression suite
all six ARI JSON syntax gates
Brand Assets
```

Expected: zero failures.

- [ ] **Step 6: Open stacked PR**

Base the PR on `feat/ari-phase0-1` until PR #38 lands. Do not enable merge into the feature base. After #38 lands, retarget to `main`, verify the new merge ref, then use the repository merge queue.

---

## Self-review checklist

- Every Phase 1 deliverable missing from the prior slice maps to a task: Release Registry → Task 2; RBOM v0 → Task 3; query/CLI basics → Task 4.
- Registry is derived and deterministic; no source-of-truth inversion.
- Exact selectors prevent hidden `latest` resolution.
- Conflict is distinct from unknown/incompatible.
- RBOM verification state describes passport coverage only.
- No Phase 2/3 capability was smuggled into the milestone.
- All production behavior has a named failing test before implementation.
