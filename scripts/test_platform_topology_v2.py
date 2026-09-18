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
    OPTIONAL_REPO_FIELDS,
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

PLANES = {
    "intelligence",
    "authority",
    "trust",
    "runtime",
    "execution",
    "verification",
    "experience",
}

SHA_LIKE_KEYS = {"head_sha", "remote_head_sha", "remote_sha", "sha", "commit_sha"}
SHA_LIKE_VALUE = re.compile(r"\b[0-9a-f]{40}\b")


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise AssertionError(f"{path} must contain a JSON object")
    return value


def topology_index(doc: dict) -> dict:
    return {r["name"]: r for r in doc["repositories"]}


def valid_topology() -> dict:
    return copy.deepcopy(load_json(TOPOLOGY))


class TopologyV2DataTest(unittest.TestCase):
    def test_has_exactly_33_unique_repositories(self):
        # 33 = prior 31 (incl. Rendetalje + RenOS) + fihim + war-room experience
        # projections. Both new entries are architecture_plane=experience.
        doc = load_json(TOPOLOGY)
        names = [r["name"] for r in doc["repositories"]]
        self.assertEqual(len(names), 33)
        self.assertEqual(len(set(names)), 33)

    def test_business_ops_is_registered_as_domain_not_platform_plane(self):
        repo = topology_index(load_json(TOPOLOGY))["business-ops"]
        self.assertIsNone(repo["architecture_plane"])
        self.assertEqual(repo["system_class"], "service-business-domain")
        self.assertEqual(repo["role"], "canonical-service-business-domain")
        self.assertIn("service-business", repo["owns"].lower())
        self.assertIn("authority", repo["must_not_own"].lower())
        self.assertIn("runtime", repo["must_not_own"].lower())
        self.assertIn("verification", repo["must_not_own"].lower())

    def test_rendetalje_is_registered_as_tenant_domain(self):
        repo = topology_index(load_json(TOPOLOGY))["rendetalje"]
        self.assertIsNone(repo["architecture_plane"])
        self.assertEqual(repo["system_class"], "tenant-domain")
        self.assertEqual(repo["role"], "rendetalje-reference-tenant")
        self.assertIn("cleaning", repo["owns"].lower())
        self.assertIn("authority", repo["must_not_own"].lower())

    def test_renos_is_registered_as_product_surface_not_truth_owner(self):
        repo = topology_index(load_json(TOPOLOGY))["renos"]
        self.assertIsNone(repo["architecture_plane"])
        self.assertEqual(repo["system_class"], "product-surface")
        self.assertEqual(repo["role"], "service-operations-product-surface")
        self.assertIn("operator experience", repo["owns"].lower())
        self.assertIn("domain truth", repo["must_not_own"].lower())
        self.assertIn("runtime", repo["must_not_own"].lower())
        self.assertIn("verification", repo["must_not_own"].lower())

    def test_fihim_is_registered_as_operator_cockpit_projection(self):
        repo = topology_index(load_json(TOPOLOGY))["fihim"]
        self.assertEqual(repo["architecture_plane"], "experience")
        self.assertEqual(repo["system_class"], "operator-cockpit")
        self.assertEqual(repo["role"], "operator-cockpit-projection")
        self.assertIn("projection", repo["owns"].lower())
        self.assertIn("domain truth", repo["must_not_own"].lower())
        self.assertIn("verification", repo["must_not_own"].lower())

    def test_war_room_is_registered_as_ops_intelligence_projection(self):
        repo = topology_index(load_json(TOPOLOGY))["war-room"]
        self.assertEqual(repo["architecture_plane"], "experience")
        self.assertEqual(repo["system_class"], "ops-intelligence-projection")
        self.assertEqual(repo["role"], "operational-intelligence-projection")
        self.assertIn("projection", repo["owns"].lower())
        self.assertIn("topology", repo["must_not_own"].lower())
        self.assertIn("verification", repo["must_not_own"].lower())

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
            self.assertTrue(REQUIRED_REPO_FIELDS <= set(repo), repo.get("name"))
            self.assertTrue(set(repo) - REQUIRED_REPO_FIELDS <= OPTIONAL_REPO_FIELDS, repo.get("name"))

    def test_temporary_records_carry_expiry(self):
        doc = load_json(TOPOLOGY)
        temporary = [r for r in doc["repositories"] if r.get("lifecycle") == "temporary"]
        self.assertTrue(temporary, "expected at least one temporary entry")
        for repo in temporary:
            self.assertRegex(repo.get("expires_at", ""), r"^\d{4}-\d{2}-\d{2}$", repo.get("name"))
        for repo in doc["repositories"]:
            if repo.get("lifecycle") != "temporary":
                self.assertNotIn("expires_at", repo, repo.get("name"))

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


class ReadmeProjectionTest(unittest.TestCase):
    def test_readme_topology_block_matches_generated_projection(self):
        readme = README.read_text(encoding="utf-8")
        self.assertEqual(
            extract_marked_block(readme).strip(),
            render_readme_table(load_topology(TOPOLOGY)).strip(),
        )


if __name__ == "__main__":
    unittest.main()
