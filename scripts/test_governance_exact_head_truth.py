#!/usr/bin/env python3
"""Tests for verify_exact_head_truth.py — run: python scripts/test_governance_exact_head_truth.py
or: python -m pytest scripts/test_governance_exact_head_truth.py -q
Self-contained (stdlib unittest only). Unique basename avoids pytest
import-file-mismatch with sibling checkouts (see AIE #37)."""
import json
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timezone, timedelta
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = REPO_ROOT / "scripts" / "verify_exact_head_truth.py"
SCHEMA_PATH = REPO_ROOT / "docs/contracts/exact-head-truth/1.0.json"

HEAD = "8e5fac2a86f39b965539ec580b08ceb331830c49"
OTHER = "efc88fc353a40000000000000000000000000000"


def now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def valid_record(**over):
    rec = {
        "repo": "Aftergraph/aie",
        "sha": HEAD,
        "run_id": "34021908374",
        "attempt": 1,
        "timestamp": now_iso(),
        "source": "self-hosted",
        "status": "success",
        "context": "test (3.12)",
        "details_url": "https://github.com/Aftergraph/aie/actions/runs/34021908374",
    }
    rec.update(over)
    return rec


def run_validator(record_obj=None, raw=None, args=()):
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "record.json"
        if raw is not None:
            p.write_text(raw, encoding="utf-8")
        else:
            p.write_text(json.dumps(record_obj), encoding="utf-8")
        r = subprocess.run([sys.executable, str(VALIDATOR), str(p), *args],
                           capture_output=True, text=True, cwd=REPO_ROOT)
        return r


class SchemaFileTest(unittest.TestCase):
    def test_schema_parses_and_has_required(self):
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        self.assertEqual(schema["$id"], "contract:exact-head-truth/1.0")
        for f in ("repo", "sha", "run_id", "attempt", "timestamp", "source", "status", "context"):
            self.assertIn(f, schema["required"])


class ValidatorTest(unittest.TestCase):
    def test_valid_record_ok(self):
        r = run_validator(valid_record())
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("OK:", r.stdout)

    def test_valid_record_with_matching_head(self):
        r = run_validator(valid_record(), args=("--head", HEAD))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_mismatched_head_is_stale(self):
        r = run_validator(valid_record(), args=("--head", OTHER))
        self.assertEqual(r.returncode, 1)
        self.assertIn("STALE", r.stdout)

    def test_missing_required_field(self):
        rec = valid_record()
        del rec["run_id"]
        r = run_validator(rec)
        self.assertEqual(r.returncode, 1)
        self.assertIn("run_id", r.stdout)

    def test_unknown_field_rejected(self):
        r = run_validator(valid_record(extra="nope"))
        self.assertEqual(r.returncode, 1)
        self.assertIn("unknown field", r.stdout)

    def test_short_sha_rejected(self):
        r = run_validator(valid_record(sha="8e5fac2"))
        self.assertEqual(r.returncode, 1)
        self.assertIn("sha", r.stdout)

    def test_bad_repo_format(self):
        r = run_validator(valid_record(repo="not-a-repo"))
        self.assertEqual(r.returncode, 1)
        self.assertIn("repo", r.stdout)

    def test_bad_source_rejected(self):
        r = run_validator(valid_record(source="carrier-pigeon"))
        self.assertEqual(r.returncode, 1)
        self.assertIn("source", r.stdout)

    def test_bad_status_rejected(self):
        r = run_validator(valid_record(status="maybe"))
        self.assertEqual(r.returncode, 1)
        self.assertIn("status", r.stdout)

    def test_attempt_zero_rejected(self):
        r = run_validator(valid_record(attempt=0))
        self.assertEqual(r.returncode, 1)
        self.assertIn("attempt", r.stdout)

    def test_bad_timestamp_rejected(self):
        r = run_validator(valid_record(timestamp="yesterday-ish"))
        self.assertEqual(r.returncode, 1)
        self.assertIn("timestamp", r.stdout)

    def test_old_timestamp_is_stale(self):
        old = (datetime.now(timezone.utc) - timedelta(hours=5)).strftime("%Y-%m-%dT%H:%M:%SZ")
        r = run_validator(valid_record(timestamp=old))
        self.assertEqual(r.returncode, 1)
        self.assertIn("STALE", r.stdout)

    def test_future_timestamp_rejected(self):
        fut = (datetime.now(timezone.utc) + timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
        r = run_validator(valid_record(timestamp=fut))
        self.assertEqual(r.returncode, 1)
        self.assertIn("future", r.stdout)

    def test_invalid_json(self):
        r = run_validator(raw="{not json")
        self.assertEqual(r.returncode, 1)
        self.assertIn("not valid JSON", r.stdout)

    def test_missing_file(self):
        r = subprocess.run([sys.executable, str(VALIDATOR), "/nonexistent/r.json"],
                           capture_output=True, text=True, cwd=REPO_ROOT)
        self.assertEqual(r.returncode, 1)
        self.assertIn("not found", r.stdout)

    def test_intermediate_status_ok(self):
        r = run_validator(valid_record(status="running"))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("intermediate", r.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=1)
