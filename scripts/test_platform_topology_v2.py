#!/usr/bin/env python3
"""Tests for platform-topology/2.0 — run: python scripts/test_platform_topology_v2.py
or: python -m pytest scripts/test_platform_topology_v2.py -q
Self-contained (stdlib unittest only). Topology/2.0 separates the seven
permanent semantic `architecture_plane` values from the extensible
`system_class`; exact Git SHAs never belong in topology (generated
org-state truth owns them).
"""
import copy
import json
import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from platform_topology import (
    PLANE_VALUES,
    REQUIRED_REPO_FIELDS,
    extract_marked_block,
    load_topology,
    parse_dependency_projection,
    render_readme_table,
    replace_marked_block,
    validate_topology,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
TOPOLOGY = REPO_ROOT / "docs" / "platform-topology" / "2.0.json"
SCHEMA = REPO_ROOT / "docs" / "platform-topology" / "2.0.schema.json"
DEPENDENCIES = REPO_ROOT / "dependencies.yml"
README = REPO_ROOT / "README.md"
V4_DOC = REPO_ROOT / "docs" / "PLATFORM-ARCHITECTURE-V4.md"
V3_DOC = REPO_ROOT / "docs" / "PLATFORM-ARCHITECTURE-V3.md"
RECONCILIATION_DOC = REPO_ROOT / "docs" / "PLATFORM-RECONCILIATION-V1.md"
CROSS_REPO_DOC = REPO_ROOT / "docs" / "cross-repo-contracts.md"
REGISTRY_DOC = REPO_ROOT / "docs" / "REPOSITORY-REGISTRY-v0.1.md"
VERIFIED_AUTO_DOC = REPO_ROOT / "docs" / "VERIFIED-AUTO-V1.md"
MEMORY_SEPARATION_DOC = REPO_ROOT / "docs" / "MEMORY-ACC-BRAIN-V1.md"
HUMAN_GOVERNANCE_DOC = REPO_ROOT / "docs" / "HUMAN-GOVERNANCE-V1.md"
PROACTIVITY_ORG_DOC = REPO_ROOT / "docs" / "PROACTIVITY-ORG-V1.md"
POCKET_SOURCE_DOC = REPO_ROOT / "docs" / "POCKET-SOURCE-V1.md"
VOICE_INTERACTION_DOC = REPO_ROOT / "docs" / "VOICE-INTERACTION-V1.md"
CURRENT_DOCS = (V4_DOC, RECONCILIATION_DOC, CROSS_REPO_DOC, REGISTRY_DOC, VERIFIED_AUTO_DOC, MEMORY_SEPARATION_DOC, HUMAN_GOVERNANCE_DOC, PROACTIVITY_ORG_DOC, POCKET_SOURCE_DOC, VOICE_INTERACTION_DOC)
DESIGN_SPEC_NAMES = (
    "2026-09-08-aftergraph-platform-architecture-v4-and-platform-fabrics-v1-design.md",
    "2026-09-08-aftergraph-verified-auto-execution-design.md",
)
RATIONALE_MARK = re.compile(r"rationale", re.IGNORECASE)
VERIFIED_AUTO_OWNERS = ("trust-gateway", "runtime", "works-execution", "studio", "sentinel", "aie")
MEMORY_SEPARATION_OWNERS = ("runtime", "works-execution", "context-continuity", "ACC")
FORBIDDEN_MEMORY_PHRASES = (
    "memory is authoritative",
    "authoritative memory",
    "memory grants authority",
    "brain grants authority",
    "capsule grants authority",
    "memory defines success",
)
HUMAN_GOVERNANCE_OWNERS = ("aie", "trust-gateway", "studio")
FORBIDDEN_GOVERNANCE_PHRASES = (
    "role label confers",
    "label is authority",
    "labels are authority",
    "workspace grants authority",
    "surface grants authority",
    "studio mints authority",
    "workspace is authoritative",
)
PROACTIVITY_ORG_OWNERS = ("wi-backend", "wi-frontend", "runtime", "aftergraph-cron-fabric", "aie", "trust-gateway", "works-execution", "sentinel")
FORBIDDEN_PROACTIVITY_PHRASES = (
    "cron executes work",
    "cron has execution authority",
    "candidate admits itself",
    "candidates self-admit",
    "worker grants itself authority",
    "self-declares verified completion",
    "evaluator scores its own execution",
    "verdict waives verification",
)
POCKET_SOURCE_OWNERS = ("wi-backend", "aie", "trust-gateway", "runtime", "works-execution", "sentinel")
FORBIDDEN_POCKET_PHRASES = (
    "pocket is a principal",
    "pocket is authoritative",
    "pocket executes work",
    "pocket is the oracle",
    "transcript is identity",
    "speaker attribution authenticates",
    "spoken instruction grants permission",
    "mcp is the ingestion source",
    "mcp is canonical",
    "webhook is truth",
    "webhooks are truth",
    "webhook is reconciliation truth",
)
VOICE_INTERACTION_OWNERS = ("studio", "wi-frontend", "runtime", "trust-gateway", "works-execution")
FORBIDDEN_VOICE_PHRASES = (
    "session is identity",
    "session is durable state",
    "session grants authority",
    "handoff grants authority",
    "transcript is identity",
    "speaker is the principal",
    "spoken command grants permission",
    "correlation grants authority",
    "surface is authoritative",
    "persona grants authority",
)
FORBIDDEN_AUTO_PHRASES = (
    "runtime verifies",
    "runtime approves",
    "self-approves",
    "verification owner: runtime",
    "executor verifies",
)
STALE_CURRENT_NAMES = ("work-intelligence-v2", "work-intelligence-web", "venture-os-consumer")
HISTORICAL_MARK = re.compile(r"historical|provenance|legacy|superseded|2026-09-07|19-repo", re.IGNORECASE)

PLANES = {
    "intelligence",
    "authority",
    "trust",
    "runtime",
    "execution",
    "verification",
    "experience",
}

REQUIRED_REPO_FIELDS = {
    "name",
    "canonical_branch",
    "visibility",
    "architecture_plane",
    "system_class",
    "role",
    "lifecycle",
    "owns",
    "must_not_own",
}

SHA_LIKE_KEYS = {"head_sha", "remote_head_sha", "remote_sha", "sha", "commit_sha"}
SHA_LIKE_VALUE = re.compile(r"\b[0-9a-f]{40}\b")


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise AssertionError(f"{path} must contain a JSON object")
    return value


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


class TopologyV2ShapeTest(unittest.TestCase):
    def test_envelope_identifies_topology_v2(self):
        doc = load_json(TOPOLOGY)
        self.assertEqual(doc["schema_version"], "platform-topology/2.0")
        self.assertEqual(doc["organization"], "Aftergraph")

    def test_no_record_uses_legacy_plane_property(self):
        doc = load_json(TOPOLOGY)
        for repo in doc["repositories"]:
            self.assertNotIn("plane", repo, repo.get("name"))

    def test_all_architecture_planes_known_or_null(self):
        doc = load_json(TOPOLOGY)
        for repo in doc["repositories"]:
            plane = repo["architecture_plane"]
            self.assertTrue(plane is None or plane in PLANES, repo.get("name"))

    def test_all_records_carry_required_fields(self):
        doc = load_json(TOPOLOGY)
        for repo in doc["repositories"]:
            self.assertEqual(set(repo), REQUIRED_REPO_FIELDS, repo.get("name"))

    def test_all_records_carry_must_not_own(self):
        doc = load_json(TOPOLOGY)
        for repo in doc["repositories"]:
            self.assertIsInstance(repo["must_not_own"], str, repo.get("name"))
            self.assertTrue(repo["must_not_own"].strip(), repo.get("name"))

    def test_all_canonical_branches_are_main(self):
        doc = load_json(TOPOLOGY)
        for repo in doc["repositories"]:
            self.assertEqual(repo["canonical_branch"], "main", repo.get("name"))

    def test_no_exact_sha_fields_or_values(self):
        doc = load_json(TOPOLOGY)
        for repo in doc["repositories"]:
            for key, value in repo.items():
                self.assertNotIn(key, SHA_LIKE_KEYS, repo.get("name"))
                if isinstance(value, str):
                    self.assertIsNone(SHA_LIKE_VALUE.search(value), repo.get("name"))

    def test_legacy_transition_repo_has_no_canonical_plane(self):
        doc = load_json(TOPOLOGY)
        repo = topology_index(doc)["autonomous-venture-company"]
        self.assertIsNone(repo["architecture_plane"])
        self.assertEqual(repo["system_class"], "legacy-transition")
        self.assertEqual(repo["lifecycle"], "legacy-transition")
        self.assertEqual(repo["role"], "legacy-migration-source")

    def test_schema_requires_record_fields(self):
        schema = load_json(SCHEMA)
        record = schema["$defs"]["repository"]
        self.assertEqual(set(record["required"]), REQUIRED_REPO_FIELDS)
        self.assertFalse(record["additionalProperties"])
        plane_prop = record["properties"]["architecture_plane"]
        self.assertEqual(set(plane_prop["enum"]), PLANES | {None})
        self.assertIn("null", plane_prop["type"])


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

    def test_unknown_architecture_plane_is_rejected(self):
        doc = valid_topology()
        doc["repositories"][0]["architecture_plane"] = "mega-brain"
        self.assertTrue(any("plane" in e for e in validate_topology(doc)))

    def test_legacy_avc_name_requires_transition_classification(self):
        doc = valid_topology()
        repo = topology_index(doc)["autonomous-venture-company"]
        repo["system_class"] = "products"
        self.assertTrue(validate_topology(doc))

    def test_unknown_visibility_is_rejected(self):
        doc = valid_topology()
        doc["repositories"][0]["visibility"] = "internal"
        self.assertTrue(any("visibility" in e for e in validate_topology(doc)))

    def test_non_string_system_class_is_rejected(self):
        doc = valid_topology()
        doc["repositories"][0]["system_class"] = 7
        self.assertTrue(any("system_class" in e for e in validate_topology(doc)))

    def test_non_string_owns_is_rejected(self):
        doc = valid_topology()
        doc["repositories"][0]["owns"] = 42
        self.assertTrue(any("owns" in e for e in validate_topology(doc)))

    def test_markdown_delimiters_are_escaped_in_render(self):
        doc = valid_topology()
        doc["repositories"][0]["owns"] = "A | B\nC"
        table = render_readme_table(doc)
        row = [line for line in table.splitlines() if "`after-graph-governance`" in line][0]
        self.assertIn("A \\| B<br/>C", row)

    def test_legacy_compatibility_role_is_rejected(self):
        doc = valid_topology()
        doc["repositories"][0]["role"] = "research"
        self.assertTrue(any("legacy" in e for e in validate_topology(doc)))

    def test_numeric_evidence_cut_is_rejected(self):
        doc = valid_topology()
        doc["evidence_cut"] = 20260908
        self.assertTrue(any("evidence_cut" in e for e in validate_topology(doc)))


class TopologySchemaAgreementTest(unittest.TestCase):
    def test_data_agrees_with_published_schema(self):
        schema = load_json(SCHEMA)
        record = schema["$defs"]["repository"]
        self.assertEqual(set(record["required"]), set(REQUIRED_REPO_FIELDS))
        self.assertFalse(record["additionalProperties"])
        self.assertEqual({p for p in record["properties"]["architecture_plane"]["enum"] if p is not None}, set(PLANE_VALUES))
        doc = load_json(TOPOLOGY)
        for repo in doc["repositories"]:
            self.assertEqual(set(repo), set(record["required"]))


class DependencyProjectionTest(unittest.TestCase):
    def test_dependency_projection_matches_topology_v2(self):
        doc = load_topology(TOPOLOGY)
        topology = topology_index(doc)
        topology_ref, modules = parse_dependency_projection(DEPENDENCIES.read_text(encoding="utf-8"))
        self.assertEqual(topology_ref, "docs/platform-topology/2.0.json")
        self.assertEqual(set(modules), set(topology))
        for name, module in modules.items():
            self.assertEqual(module.repo, f"Aftergraph/{name}")
            self.assertEqual(module.role, topology[name]["role"])

    def test_dependency_projection_declares_version_4(self):
        text = DEPENDENCIES.read_text(encoding="utf-8")
        match = re.search(r"^version:\s*(\S+)\s*$", text, re.M)
        self.assertIsNotNone(match)
        assert match is not None
        self.assertEqual(match.group(1), "4")


class ActiveDocConsistencyTest(unittest.TestCase):
    def test_active_docs_reference_topology_v2(self):
        for path in CURRENT_DOCS:
            text = path.read_text(encoding="utf-8")
            self.assertIn("docs/platform-topology/2.0.json", text, path.name)

    def test_active_docs_use_current_repo_identities(self):
        for path in CURRENT_DOCS:
            text = path.read_text(encoding="utf-8")
            for name in ("wi-backend", "wi-frontend", "runtime"):
                self.assertIn(name, text, f"{path.name} misses {name}")

    def test_active_docs_do_not_present_stale_ownership_as_current(self):
        for path in CURRENT_DOCS:
            for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                if any(stale in line for stale in STALE_CURRENT_NAMES):
                    self.assertRegex(line, HISTORICAL_MARK, f"{path.name}:{lineno}")

    def test_verified_auto_binding_is_a_current_doc(self):
        self.assertIn(VERIFIED_AUTO_DOC, CURRENT_DOCS)
        self.assertTrue(VERIFIED_AUTO_DOC.is_file(), "docs/VERIFIED-AUTO-V1.md is missing")

    def test_active_docs_cite_design_spec_only_as_rationale(self):
        for path in CURRENT_DOCS:
            for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                if any(name in line for name in DESIGN_SPEC_NAMES):
                    self.assertRegex(line, RATIONALE_MARK, f"{path.name}:{lineno}")

    def test_verified_auto_maps_seams_to_v4_owners(self):
        text = VERIFIED_AUTO_DOC.read_text(encoding="utf-8")
        for owner in VERIFIED_AUTO_OWNERS:
            self.assertIn(owner, text, f"seam owner {owner} is not mapped")

    def test_verified_auto_grants_no_new_authority(self):
        text = VERIFIED_AUTO_DOC.read_text(encoding="utf-8").lower()
        for phrase in FORBIDDEN_AUTO_PHRASES:
            self.assertNotIn(phrase, text, f"authority-widening phrase {phrase!r}")

    def test_memory_separation_binding_is_a_current_doc(self):
        self.assertIn(MEMORY_SEPARATION_DOC, CURRENT_DOCS)
        self.assertTrue(MEMORY_SEPARATION_DOC.is_file(), "docs/MEMORY-ACC-BRAIN-V1.md is missing")

    def test_memory_binding_maps_stores_to_v4_owners(self):
        text = MEMORY_SEPARATION_DOC.read_text(encoding="utf-8")
        for owner in MEMORY_SEPARATION_OWNERS:
            self.assertIn(owner, text, f"memory owner {owner} is not mapped")

    def test_memory_binding_grants_no_authority(self):
        text = MEMORY_SEPARATION_DOC.read_text(encoding="utf-8").lower()
        for phrase in FORBIDDEN_MEMORY_PHRASES:
            self.assertNotIn(phrase, text, f"authority-conflating phrase {phrase!r}")

    def test_human_governance_binding_is_a_current_doc(self):
        self.assertIn(HUMAN_GOVERNANCE_DOC, CURRENT_DOCS)
        self.assertTrue(HUMAN_GOVERNANCE_DOC.is_file(), "docs/HUMAN-GOVERNANCE-V1.md is missing")

    def test_human_governance_binding_maps_seams_to_v4_owners(self):
        text = HUMAN_GOVERNANCE_DOC.read_text(encoding="utf-8")
        for owner in HUMAN_GOVERNANCE_OWNERS:
            self.assertIn(owner, text, f"governance owner {owner} is not mapped")

    def test_human_governance_binding_grants_no_authority(self):
        text = HUMAN_GOVERNANCE_DOC.read_text(encoding="utf-8").lower()
        for phrase in FORBIDDEN_GOVERNANCE_PHRASES:
            self.assertNotIn(phrase, text, f"authority-conflating phrase {phrase!r}")

    def test_proactivity_org_binding_is_a_current_doc(self):
        self.assertIn(PROACTIVITY_ORG_DOC, CURRENT_DOCS)
        self.assertTrue(PROACTIVITY_ORG_DOC.is_file(), "docs/PROACTIVITY-ORG-V1.md is missing")

    def test_proactivity_org_binding_maps_seams_to_v4_owners(self):
        text = PROACTIVITY_ORG_DOC.read_text(encoding="utf-8")
        for owner in PROACTIVITY_ORG_OWNERS:
            self.assertIn(owner, text, f"proactivity owner {owner} is not mapped")

    def test_proactivity_org_binding_grants_no_authority(self):
        text = PROACTIVITY_ORG_DOC.read_text(encoding="utf-8").lower()
        for phrase in FORBIDDEN_PROACTIVITY_PHRASES:
            self.assertNotIn(phrase, text, f"authority-conflating phrase {phrase!r}")

    def test_pocket_source_binding_is_a_current_doc(self):
        self.assertIn(POCKET_SOURCE_DOC, CURRENT_DOCS)
        self.assertTrue(POCKET_SOURCE_DOC.is_file(), "docs/POCKET-SOURCE-V1.md is missing")

    def test_pocket_source_binding_maps_seams_to_v4_owners(self):
        text = POCKET_SOURCE_DOC.read_text(encoding="utf-8")
        for owner in POCKET_SOURCE_OWNERS:
            self.assertIn(owner, text, f"pocket owner {owner} is not mapped")

    def test_pocket_source_binding_grants_no_authority(self):
        text = POCKET_SOURCE_DOC.read_text(encoding="utf-8").lower()
        for phrase in FORBIDDEN_POCKET_PHRASES:
            self.assertNotIn(phrase, text, f"authority-conflating phrase {phrase!r}")

    def test_voice_interaction_binding_is_a_current_doc(self):
        self.assertIn(VOICE_INTERACTION_DOC, CURRENT_DOCS)
        self.assertTrue(VOICE_INTERACTION_DOC.is_file(), "docs/VOICE-INTERACTION-V1.md is missing")

    def test_voice_interaction_binding_maps_seams_to_v4_owners(self):
        text = VOICE_INTERACTION_DOC.read_text(encoding="utf-8")
        for owner in VOICE_INTERACTION_OWNERS:
            self.assertIn(owner, text, f"voice owner {owner} is not mapped")

    def test_voice_interaction_binding_grants_no_authority(self):
        text = VOICE_INTERACTION_DOC.read_text(encoding="utf-8").lower()
        for phrase in FORBIDDEN_VOICE_PHRASES:
            self.assertNotIn(phrase, text, f"authority-conflating phrase {phrase!r}")

    def test_v3_marked_superseded_not_deleted(self):
        lines = V3_DOC.read_text(encoding="utf-8").splitlines()[:12]
        self.assertIn("Status: Superseded by PLATFORM-ARCHITECTURE-V4.md", "\n".join(lines))


class ReadmeProjectionTest(unittest.TestCase):
    def test_readme_topology_block_matches_generated_projection(self):
        readme = README.read_text(encoding="utf-8")
        self.assertEqual(extract_marked_block(readme).strip(), render_readme_table(load_topology(TOPOLOGY)).strip())

    def test_replace_marked_block_round_trip(self):
        doc = load_topology(TOPOLOGY)
        readme = README.read_text(encoding="utf-8")
        updated = replace_marked_block(readme, render_readme_table(doc))
        self.assertEqual(extract_marked_block(updated).strip(), render_readme_table(doc).strip())


def topology_index(doc: dict) -> dict:
    return {r["name"]: r for r in doc["repositories"]}


def valid_topology() -> dict:
    return copy.deepcopy(load_json(TOPOLOGY))


if __name__ == "__main__":
    unittest.main()
