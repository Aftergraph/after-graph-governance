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
assert homeos["repository_backing"]["status"] == "not-yet-canonicalized-in-github"
assert homeos["repository_backing"]["repository"] is None
assert homeos["local_development"]["canonical_path"] == r"C:\Aftergraph\Home-OS"
assert homeos["local_development"]["latest_known_version"] == "0.84.0-frontier"
assert homeos["local_development"]["latest_known_sha256"] == "b2a198a1d4d5a390fd59aedfee55b438cf7439e85e8c6160c48e8779d8eae7a2"
assert homeos["local_development"]["verification_status"] == "PASS_WITH_EXPLICIT_BOUNDARIES"
assert "Aftergraph/war-room" in homeos["supersedes_as_primary_interface"]

names = {row["name"] for row in topology["repositories"]}
assert "home-os" not in names
assert "homeos" not in names

war = next(row for row in topology["repositories"] if row["name"] == "war-room")
assert war["role"] == "operational-intelligence-backend-projection"
assert "HomeOS" in war["must_not_own"]

fihim = next(row for row in topology["repositories"] if row["name"] == "fihim")
assert fihim["role"] == "personal-agent-product"
assert "HomeOS" in fihim["must_not_own"]

print("Experience surface governance: PASS")
