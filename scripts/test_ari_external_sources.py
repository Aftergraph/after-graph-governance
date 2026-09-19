import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "docs/contracts/external-normative-source/0.1.json"
FIXTURES = ROOT / "docs/release-intelligence/external-sources"

REQUIRED = {
    "schema", "source_id", "kind", "title", "publisher",
    "canonical_uri", "status", "observed_at", "primary_source_ref",
}
KINDS = {"STANDARD","SPECIFICATION","PROTOCOL","PROFILE","CONVENTION","REGULATION","TCK","OTHER"}
NORMALIZED = {"DRAFT","DEVELOPMENT","EXPERIMENTAL","STABLE","APPROVED","DEPRECATED","WITHDRAWN","UNKNOWN"}


class ExternalNormativeSourceProfileTest(unittest.TestCase):
    def load_fixtures(self):
        return {
            p.name: json.loads(p.read_text(encoding="utf-8"))
            for p in sorted(FIXTURES.glob("*.json"))
        }

    def test_schema_shape_and_anchor_rule(self):
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        self.assertEqual(schema["properties"]["schema"]["const"], "external-normative-source/0.1")
        self.assertEqual(set(schema["required"]), REQUIRED)
        anchors = {tuple(x["required"]) for x in schema["anyOf"]}
        self.assertEqual(anchors, {("release_version",), ("source_revision",), ("digest",)})

    def test_all_pilot_records_are_lossless_and_bounded(self):
        fixtures = self.load_fixtures()
        self.assertEqual(
            set(fixtures),
            {
                "mcp-2026-07-28.json",
                "agent-skills-spec.json",
                "a2a-1.0.0.json",
                "a2a-tck-1.0.0.json",
                "otel-genai.json",
                "slsa-1.2.json",
            },
        )
        for name, doc in fixtures.items():
            with self.subTest(name=name):
                self.assertEqual(doc["schema"], "external-normative-source/0.1")
                self.assertTrue(REQUIRED <= set(doc))
                self.assertIn(doc["kind"], KINDS)
                self.assertTrue(any(k in doc for k in ("release_version","source_revision","digest")))
                self.assertNotIn("authority_granted", doc)
                self.assertNotIn("execution_authorized", doc)
                self.assertNotIn("conformance", doc)
                status = doc["status"]
                self.assertIsInstance(status["source_declared"], bool)
                if status["source_declared"]:
                    self.assertIsInstance(status["raw"], str)
                    self.assertTrue(status["raw"].strip())
                else:
                    self.assertIsNone(status["raw"])
                if "normalized" in status:
                    self.assertIn(status["normalized"], NORMALIZED)
                rev = doc.get("source_revision")
                if rev and rev["kind"] == "GIT_COMMIT":
                    self.assertRegex(rev["value"], r"^[0-9a-f]{40}$")

    def test_release_version_and_source_revision_are_independent(self):
        fixtures = self.load_fixtures()
        agent = fixtures["agent-skills-spec.json"]
        self.assertNotIn("release_version", agent)
        self.assertEqual(agent["source_revision"]["value"], "217be548739f21d6008915c29aefe320ea1a90af")

        tck = fixtures["a2a-tck-1.0.0.json"]
        self.assertEqual(tck["release_version"], "1.0.0")
        self.assertEqual(tck["source_revision"]["value"], "263b9cfaf16a554bdfb166a7ba5b67716e946349")

    def test_upstream_status_is_preserved_verbatim(self):
        fixtures = self.load_fixtures()
        self.assertEqual(fixtures["otel-genai.json"]["status"]["raw"], "Development")
        self.assertEqual(fixtures["slsa-1.2.json"]["status"]["raw"], "Approved")
        self.assertIsNone(fixtures["agent-skills-spec.json"]["status"]["raw"])

    def test_a2a_protocol_and_tck_are_separate_sources(self):
        fixtures = self.load_fixtures()
        spec = fixtures["a2a-1.0.0.json"]
        tck = fixtures["a2a-tck-1.0.0.json"]
        self.assertEqual(spec["kind"], "PROTOCOL")
        self.assertEqual(tck["kind"], "TCK")
        self.assertNotEqual(spec["source_id"], tck["source_id"])
        self.assertNotEqual(spec["status"]["raw"], tck["status"]["raw"])

    def test_profile_documents_dcat_prov_mapping_and_no_authority(self):
        text = (ROOT / "docs/release-intelligence/EXTERNAL-NORMATIVE-SOURCE-PROFILE.md").read_text(encoding="utf-8")
        for token in ("dcat:version", "prov:wasRevisionOf", "prov:hadPrimarySource", "grants no authority"):
            self.assertIn(token, text)


if __name__ == "__main__":
    unittest.main(verbosity=2)