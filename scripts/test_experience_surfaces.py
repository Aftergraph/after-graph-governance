#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOMEOS = ROOT / "docs" / "experience-surfaces" / "homeos" / "0.1.json"
TOPOLOGY = ROOT / "docs" / "platform-topology" / "2.0.json"

homeos = json.loads(HOMEOS.read_text(encoding="utf-8"))
topology = json.loads(TOPOLOGY.read_text(encoding="utf-8"))

assert homeos["schema_version"] == "aftergraph.experience-surface/0.1"
assert homeos["surface_id"] == "homeos"
assert homeos["canonical_role"] == "primary-operator-control-surface"
assert homeos["repository_backing"]["status"] == "canonicalized-in-github"
assert homeos["repository_backing"]["repository"] == "Aftergraph/home-os"
assert homeos["repository_backing"]["canonical_commit"] == "483b1edb62a7cc003b6ef64604f09477f126c0f2"
assert homeos["local_development"]["canonical_path"] == r"C:\Aftergraph\Home-OS"
assert homeos["local_development"]["latest_known_version"] == "0.87.0-frontier"
assert homeos["local_development"]["latest_known_sha256"] == "c67fc48318b81be76271de5836de9e6aa7e541bc5281fe9f6690bf220cea12ad"
assert homeos["local_development"]["latest_repo_seed_sha256"] == "713ebfd58b809b0b11602159c9757cc1519e0ef9bcf911a6466a22de27aa82da"
assert homeos["local_development"]["verification_status"] == "PASS_WITH_EXPLICIT_BOUNDARIES"
assert "Aftergraph/war-room" in homeos["supersedes_as_primary_interface"]

names = {row["name"] for row in topology["repositories"]}
assert "home-os" in names
assert "homeos" not in names

home_repo = next(row for row in topology["repositories"] if row["name"] == "home-os")
assert home_repo["architecture_plane"] == "experience"
assert home_repo["system_class"] == "operator-control-surface"
assert home_repo["role"] == "primary-operator-control-surface"
assert "Trust Gateway" in home_repo["must_not_own"]
assert "Sentinel" in home_repo["must_not_own"]

war = next(row for row in topology["repositories"] if row["name"] == "war-room")
assert war["role"] == "operational-intelligence-backend-projection"
assert "HomeOS" in war["must_not_own"]

fihim = next(row for row in topology["repositories"] if row["name"] == "fihim")
assert fihim["role"] == "personal-agent-product"
assert "HomeOS" in fihim["must_not_own"]

print("Experience surface governance: PASS")
