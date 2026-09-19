#!/usr/bin/env python3
"""Bounded standard-library validator for the published ARI contracts.

The Release Intelligence gate installs no ``jsonschema`` and the repository
carries an explicit convention against the dependency (``platform_topology.py``,
``verify_exact_head_truth.py`` and ``reduce_ci_truth.py`` all hand-roll their
contract checks). The interop boundary the contracts claim — that a
cross-repository consumer validating only the published schema rejects what the
reference implementation rejects — therefore has to be provable with the
standard library alone.

This module implements exactly the validation keywords the ARI contracts use and
raises :class:`UnsupportedKeyword` on anything else. The loud failure is the
point: a contract that grows ``if``/``then``, ``format`` or ``contains`` cannot
silently validate as permissive and turn a passing interop test into a lie.

That the surface really does cover the contracts is not a claim a reader has to
take on faith. ``test_ari_schema_check.ContractSurfaceTest`` walks every
published contract, collects the validation keywords it uses, and fails if any
of them falls outside :data:`SUPPORTED_KEYWORDS`. A contract that grows a new
keyword therefore breaks the build instead of quietly widening what a
schema-only consumer accepts.
"""

from __future__ import annotations

import re
from typing import Any

# Keywords that annotate rather than validate. Ignoring these is correct.
ANNOTATION_KEYWORDS = frozenset(
    {
        "$schema",
        "$id",
        "$anchor",
        "$comment",
        "$defs",
        "definitions",
        "title",
        "description",
        "default",
        "examples",
        "deprecated",
        "readOnly",
        "writeOnly",
    }
)

# The complete validation surface this evaluator implements. Extending it is a
# deliberate act: every entry here is exercised by test_ari_schema_check.py, and
# the surface test fails if a published contract uses anything not listed.
SUPPORTED_KEYWORDS = frozenset(
    {
        "$ref",
        "additionalProperties",
        "anyOf",
        "const",
        "contains",
        "enum",
        "items",
        "maxItems",
        "maximum",
        "minItems",
        "minProperties",
        "minimum",
        "minLength",
        "not",
        "oneOf",
        "pattern",
        "properties",
        "propertyNames",
        "required",
        "type",
        "uniqueItems",
    }
)

_TYPE_MATCHERS: dict[str, Any] = {
    "object": lambda value: isinstance(value, dict),
    "array": lambda value: isinstance(value, list),
    "string": lambda value: isinstance(value, str),
    "integer": lambda value: isinstance(value, int) and not isinstance(value, bool),
    "number": lambda value: isinstance(value, (int, float)) and not isinstance(value, bool),
    "boolean": lambda value: isinstance(value, bool),
    "null": lambda value: value is None,
}


class UnsupportedKeyword(Exception):
    """Raised when a contract uses a keyword this bounded evaluator lacks.

    A silent pass here would make every rejection assertion in the contract
    interop tests vacuously satisfiable, so the evaluator refuses to guess.
    """


def _type_name(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, dict):
        return "object"
    if isinstance(value, list):
        return "array"
    if isinstance(value, str):
        return "string"
    if isinstance(value, int):
        return "integer"
    return "number"


def _equal(left: Any, right: Any) -> bool:
    """JSON equality, so that ``true`` never compares equal to ``1``."""
    if isinstance(left, bool) != isinstance(right, bool):
        return False
    if isinstance(left, dict) and isinstance(right, dict):
        return left.keys() == right.keys() and all(_equal(left[k], right[k]) for k in left)
    if isinstance(left, list) and isinstance(right, list):
        return len(left) == len(right) and all(_equal(a, b) for a, b in zip(left, right))
    return left == right


def _resolve(ref: str, root: Any) -> Any:
    if not isinstance(ref, str) or not ref.startswith("#/"):
        raise UnsupportedKeyword(
            "only local $ref pointers are implemented, so a contract cannot bind "
            "a document body owned elsewhere: " + repr(ref)
        )
    target = root
    for token in ref[2:].split("/"):
        token = token.replace("~1", "/").replace("~0", "~")
        if not isinstance(target, dict) or token not in target:
            raise UnsupportedKeyword("unresolvable local $ref pointer: " + repr(ref))
        target = target[token]
    return target


def validate(instance: Any, schema: Any, root: Any = None) -> list[str]:
    """Return the violations of ``schema`` on ``instance``; empty means conforming."""
    if root is None:
        root = schema
    if not isinstance(schema, dict):
        raise UnsupportedKeyword(
            "schema must be an object, got " + _type_name(schema)
        )

    unknown = set(schema) - SUPPORTED_KEYWORDS - ANNOTATION_KEYWORDS
    if unknown:
        raise UnsupportedKeyword(
            "keywords outside this evaluator's implemented surface: " + ", ".join(sorted(unknown))
        )

    if "$ref" in schema:
        return validate(instance, _resolve(schema["$ref"], root), root)

    expected = schema.get("type")
    if expected is not None:
        candidates = expected if isinstance(expected, list) else [expected]
        for name in candidates:
            if name not in _TYPE_MATCHERS:
                raise UnsupportedKeyword("unknown type name: " + repr(name))
        if not any(_TYPE_MATCHERS[name](instance) for name in candidates):
            return [f"expected type {candidates}, got {_type_name(instance)}"]

    errors: list[str] = []

    if isinstance(instance, dict):
        properties = schema.get("properties", {})
        for key in schema.get("required", ()):
            if key not in instance:
                errors.append(f"missing required property: {key}")
        for key, subschema in properties.items():
            if key in instance:
                errors.extend(f"{key}: {e}" for e in validate(instance[key], subschema, root))
        if "propertyNames" in schema:
            for key in sorted(instance):
                errors.extend(
                    f"{key} (name): {e}"
                    for e in validate(key, schema["propertyNames"], root)
                )
        if "minProperties" in schema and len(instance) < schema["minProperties"]:
            errors.append(
                f"expected at least {schema['minProperties']} properties, got {len(instance)}"
            )
        # additionalProperties has two forms and both are load-bearing here:
        # ``false`` closes the object, and a schema constrains every key that
        # ``properties`` did not match (release-passport pins the profile-value
        # vocabulary and aftergraph-component pins the contract-version type
        # this way). Treating only the boolean form as meaningful would leave a
        # schema-valued one silently permissive.
        additional = schema.get("additionalProperties")
        if additional is False:
            for key in sorted(instance):
                if key not in properties:
                    errors.append(f"unexpected property: {key}")
        elif isinstance(additional, dict):
            for key in sorted(instance):
                if key not in properties:
                    errors.extend(
                        f"{key}: {e}" for e in validate(instance[key], additional, root)
                    )

    elif isinstance(instance, list):
        if "minItems" in schema and len(instance) < schema["minItems"]:
            errors.append(f"expected at least {schema['minItems']} items, got {len(instance)}")
        if "maxItems" in schema and len(instance) > schema["maxItems"]:
            errors.append(f"expected at most {schema['maxItems']} items, got {len(instance)}")
        if schema.get("uniqueItems"):
            for index, item in enumerate(instance):
                if any(_equal(item, other) for other in instance[:index]):
                    errors.append(f"items[{index}] duplicates an earlier item")
                    break
        if "items" in schema:
            for index, item in enumerate(instance):
                errors.extend(
                    f"items[{index}]: {e}" for e in validate(item, schema["items"], root)
                )
        # ``contains`` is the existential counterpart of ``items``: rbom/0.1 uses
        # it to require that at least one component row carries the paired
        # passport digests under PARTIAL, which ``items`` (universal) cannot say
        # and a oneOf branch cannot retract. minContains/maxContains stay
        # unimplemented on purpose — no published contract needs a counted
        # existence, and the loud guard keeps that from silently widening later.
        if "contains" in schema:
            if not any(not validate(item, schema["contains"], root) for item in instance):
                errors.append("contains: no item validates against the contains subschema")

    elif isinstance(instance, str):
        if "minLength" in schema and len(instance) < schema["minLength"]:
            errors.append(f"expected minLength {schema['minLength']}, got {len(instance)}")
        pattern = schema.get("pattern")
        if pattern is not None and re.search(pattern, instance) is None:
            errors.append(f"{instance!r} does not match pattern {pattern}")

    elif isinstance(instance, int) and not isinstance(instance, bool):
        if "minimum" in schema and instance < schema["minimum"]:
            errors.append(f"expected minimum {schema['minimum']}, got {instance}")
        if "maximum" in schema and instance > schema["maximum"]:
            errors.append(f"expected maximum {schema['maximum']}, got {instance}")

    if "const" in schema and not _equal(instance, schema["const"]):
        errors.append(f"expected const {schema['const']!r}, got {instance!r}")
    if "enum" in schema and not any(_equal(instance, option) for option in schema["enum"]):
        errors.append(f"{instance!r} is not one of {schema['enum']}")

    if "anyOf" in schema:
        if not any(not validate(instance, branch, root) for branch in schema["anyOf"]):
            errors.append("anyOf: no branch validates")
    if "oneOf" in schema:
        validating = sum(not validate(instance, branch, root) for branch in schema["oneOf"])
        if validating != 1:
            errors.append(f"{validating} oneOf branches validate, expected exactly 1")
    if "not" in schema:
        if not validate(instance, schema["not"], root):
            errors.append("not: the subschema validates, but must not")

    return errors