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
    load_topology,
    parse_dependency_projection,
    render_readme_table,
    validate_topology,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
TOPOLOGY = REPO_ROOT / "docs" / "platform-topology" / "2.0.json"
SCHEMA = REPO_ROOT / "docs" / "platform-topology" / "2.0.schema.json"
DEPENDENCIES = REPO_ROOT / "dependencies.yml"

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


def topology_index(doc: dict) -> dict:
    return {r["name"]: r for r in doc["repositories"]}


def valid_topology() -> dict:
    return copy.deepcopy(load_json(TOPOLOGY))


if __name__ == "__main__":
    unittest.main()
