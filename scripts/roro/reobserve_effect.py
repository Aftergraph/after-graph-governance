#!/usr/bin/env python3
from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any

_EFFECT_SUBJECT = re.compile(r"^effect-receipt:[^:]+:sha256:[a-f0-9]{64}$")


def _instant(value: str) -> datetime:
    if not isinstance(value, str) or not value:
        raise ValueError("timestamp required")
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("timestamp must be timezone-aware")
    return parsed.astimezone(timezone.utc)


def reduce_post_effect_observation(case: dict[str, Any]) -> dict[str, Any]:
    subject = case.get("effect_receipt_subject")
    if not isinstance(subject, str) or not _EFFECT_SUBJECT.fullmatch(subject):
        raise ValueError("exact effect receipt subject required")
    intended = case.get("intended_outcome")
    before = case.get("before")
    after = case.get("after")
    if not all(isinstance(x, dict) for x in (intended, before, after)):
        raise ValueError("intended_outcome, before and after are required")
    evaluated_at = _instant(case["evaluated_at"])
    observed_at = _instant(after["observed_at"])
    max_age = case.get("max_age_seconds")
    if not isinstance(max_age, int) or max_age < 0:
        raise ValueError("max_age_seconds must be non-negative integer")
    age = (evaluated_at - observed_at).total_seconds()
    after_status = after.get("epistemic_status")
    expected = intended.get("expected")
    actual = after.get("value")
    if age < 0:
        classification, epistemic = "INDETERMINATE", "UNKNOWN"
    elif age > max_age:
        classification, epistemic = "STALE", "STALE"
    elif after_status in {"UNKNOWN", "CONFLICTING"}:
        classification, epistemic = "INDETERMINATE", after_status
    elif actual == expected:
        classification, epistemic = "MATCHED", "VERIFIED"
    else:
        classification, epistemic = "DIVERGED", "OBSERVED"

    return {
        "schema_version": "roro-post-effect-observation/0.1",
        "effect_receipt_subject": subject,
        "effect_subject_preserved": True,
        "subject": intended.get("subject"),
        "predicate": intended.get("predicate"),
        "expected": expected,
        "before": before.get("value"),
        "after": actual,
        "classification": classification,
        "epistemic_status": epistemic,
        "after_observed_at": after.get("observed_at"),
        "evaluated_at": case.get("evaluated_at"),
        "age_seconds": age,
        "verification_claim": classification == "MATCHED" and epistemic == "VERIFIED",
        "authority_granted": False,
        "execution_authorized": False,
    }
