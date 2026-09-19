import copy
import json
import unittest
from pathlib import Path

from scripts.ari_schema_check import (
    ANNOTATION_KEYWORDS,
    SUPPORTED_KEYWORDS,
    UnsupportedKeyword,
    validate,
)
from scripts.test_ari_registry import COMPONENT, EDGE, PASSPORT

ROOT = Path(__file__).resolve().parents[1]
CONTRACTS = ROOT / "docs" / "contracts"

# Every published ARI contract, keyed by the schema discriminator its documents carry.
DOCUMENT_CONTRACTS = {
    "aftergraph-component/1.0": CONTRACTS / "aftergraph-component" / "1.0.json",
    "compatibility-edge/1.0": CONTRACTS / "compatibility-edge" / "1.0.json",
    "release-passport/1.0": CONTRACTS / "release-passport" / "1.0.json",
    "release-registry/1.0": CONTRACTS / "release-registry" / "1.0.json",
    "rbom/0.1": CONTRACTS / "rbom" / "0.1.json",
}

# The draft 2020-12 vocabulary. Used only to tell a keyword apart from a property
# name that happens to spell a keyword: a contract walk sees both, and the
# intersection below keeps the surface test from mistaking one for the other.
# The single collision in the published contracts is compatibility.minimum, which
# is a supported keyword, so the invariant is unaffected either way.
DRAFT_2020_12_VOCABULARY = frozenset(
    {
        "$ref",
        "$recursiveRef",
        "$dynamicRef",
        "additionalItems",
        "additionalProperties",
        "allOf",
        "anyOf",
        "const",
        "contains",
        "contentEncoding",
        "contentMediaType",
        "contentSchema",
        "dependencies",
        "dependentRequired",
        "dependentSchemas",
        "enum",
        "exclusiveMaximum",
        "exclusiveMinimum",
        "format",
        "if",
        "items",
        "maxContains",
        "maximum",
        "minContains",
        "minItems",
        "minLength",
        "minProperties",
        "multipleOf",
        "not",
        "oneOf",
        "pattern",
        "patternProperties",
        "prefixItems",
        "properties",
        "propertyNames",
        "required",
        "then",
        "else",
        "type",
        "unevaluatedItems",
        "unevaluatedProperties",
        "uniqueItems",
        "maxItems",
        "maxProperties",
    }
)


def _collect_keywords(node, out: set) -> None:
    if isinstance(node, dict):
        for key, value in node.items():
            out.add(key)
            _collect_keywords(value, out)
    elif isinstance(node, list):
        for item in node:
            _collect_keywords(item, out)


class AriSchemaCheckTest(unittest.TestCase):
    """The shared evaluator is load-bearing for two contract interop proofs.

    Every rejection assertion in test_ari_registry.py and test_ari_rbom.py is
    only as strong as this module, so its own behaviour — including the loud
    failure on unimplemented keywords — is asserted here rather than assumed.
    """

    def test_accepts_a_conforming_instance(self):
        schema = {
            "type": "object",
            "required": ["a"],
            "properties": {"a": {"type": "string", "pattern": "^x+$"}},
            "additionalProperties": False,
        }
        self.assertEqual(validate({"a": "xx"}, schema), [])

    def test_rejects_missing_required_and_unexpected_property(self):
        schema = {"type": "object", "required": ["a"], "additionalProperties": False}
        self.assertTrue(validate({}, schema))
        self.assertTrue(validate({"a": 1, "b": 2}, schema))

    def test_rejects_wrong_type_const_enum_and_pattern(self):
        self.assertTrue(validate("1", {"type": "integer"}))
        self.assertTrue(validate("b", {"const": "a"}))
        self.assertTrue(validate("b", {"enum": ["a", "c"]}))
        self.assertTrue(validate("xy", {"pattern": "^x$"}))

    def test_integer_keywords_never_confuse_booleans_with_numbers(self):
        self.assertTrue(validate(True, {"type": "integer", "minimum": 0}))
        self.assertTrue(validate(False, {"const": 0}))
        self.assertEqual(validate(1, {"type": "integer", "minimum": 1, "maximum": 1}), [])
        self.assertTrue(validate(0, {"type": "integer", "minimum": 1}))
        self.assertTrue(validate(2, {"type": "integer", "maximum": 1}))

    def test_oneOf_requires_exactly_one_validating_branch(self):
        schema = {
            "oneOf": [
                {"properties": {"a": {"const": 1}}},
                {"properties": {"a": {"const": 2}}},
            ]
        }
        self.assertEqual(validate({"a": 1}, schema), [])
        self.assertTrue(validate({"a": 3}, schema))

    def test_local_ref_resolves_and_foreign_ref_is_rejected(self):
        schema = {"$defs": {"leaf": {"type": "string"}}, "properties": {"a": {"$ref": "#/$defs/leaf"}}}
        self.assertEqual(validate({"a": "s"}, schema), [])
        self.assertTrue(validate({"a": 1}, schema))
        with self.assertRaises(UnsupportedKeyword):
            validate({}, {"$ref": "https://aftergraph.dev/contracts/aftergraph-component/1.0.json"})
        with self.assertRaises(UnsupportedKeyword):
            validate({}, {"$ref": "#/$defs/absent"})

    def test_unimplemented_validation_keyword_fails_loudly(self):
        for keyword in (
            "if",
            "then",
            "else",
            "allOf",
            "format",
            "maxProperties",
            "patternProperties",
            "unevaluatedProperties",
            "unevaluatedItems",
            "dependentRequired",
            "dependentSchemas",
            "prefixItems",
            "additionalItems",
            "maxContains",
            "minContains",
            "multipleOf",
            "exclusiveMinimum",
            "exclusiveMaximum",
            "contentSchema",
        ):
            self.assertNotIn(keyword, SUPPORTED_KEYWORDS, keyword)
            with self.subTest(keyword=keyword):
                with self.assertRaises(UnsupportedKeyword):
                    validate({}, {keyword: {}})

    def test_annotation_keywords_are_ignored_without_raising(self):
        schema = {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "$id": "https://aftergraph.dev/contracts/x.json",
            "$anchor": "x",
            "$comment": "ignored",
            "title": "X",
            "description": "annotates only",
            "default": {},
            "examples": [{}],
            "deprecated": False,
            "$defs": {"unused": {"type": "string"}},
            "type": "object",
        }
        self.assertEqual(validate({}, schema), [])

    def test_array_keywords(self):
        schema = {"type": "array", "minItems": 1, "maxItems": 2, "uniqueItems": True, "items": {"type": "string"}}
        self.assertEqual(validate(["a", "b"], schema), [])
        self.assertTrue(validate([], schema))
        self.assertTrue(validate(["a", "b", "c"], schema))
        self.assertTrue(validate(["a", "a"], schema))
        self.assertTrue(validate(["a", 1], schema))

    def test_nested_error_paths_are_reported(self):
        schema = {
            "type": "object",
            "properties": {"entries": {"type": "array", "items": {"type": "object", "required": ["id"]}}},
        }
        errors = validate({"entries": [{"id": 1}, {}]}, schema)
        self.assertTrue(
            any("entries" in error and "items[1]" in error and "id" in error for error in errors),
            errors,
        )

    def test_min_properties_bounds_an_open_object(self):
        schema = {"type": "object", "minProperties": 1}
        self.assertEqual(validate({"a": 1}, schema), [])
        self.assertTrue(validate({}, schema))

    def test_property_names_constrains_keys_not_values(self):
        schema = {"propertyNames": {"pattern": "^[a-z]+$"}}
        self.assertEqual(validate({"ok": "anything"}, schema), [])
        errors = validate({"Bad": "anything"}, schema)
        self.assertTrue(any("Bad" in error and "pattern" in error for error in errors), errors)

    def test_additional_properties_as_schema_is_not_silently_permissive(self):
        # A named property is exempt from the additionalProperties schema, so
        # "known" carries any value while every other key is pinned to PASS.
        schema = {
            "type": "object",
            "properties": {"known": {}},
            "additionalProperties": {"enum": ["PASS"]},
        }
        self.assertEqual(validate({"known": "whatever", "extra": "PASS"}, schema), [])
        self.assertTrue(validate({"extra": "FAIL"}, schema))
        # and the boolean form still closes the object
        self.assertTrue(validate({"a": 1}, {"additionalProperties": False}))

    def test_boolean_subschema_is_refused_rather_than_guessed(self):
        # Draft 2020-12 allows true/false as schemas; no ARI contract uses one,
        # so the bounded evaluator names it instead of picking a semantics. The
        # instance has to carry the key: an absent property is never descended
        # into, so {} would hide the boolean subschema rather than probe it.
        with self.assertRaises(UnsupportedKeyword):
            validate({}, True)
        with self.assertRaises(UnsupportedKeyword):
            validate({"a": 1}, {"properties": {"a": True}})
        with self.assertRaises(UnsupportedKeyword):
            validate([1], {"items": False})

    def test_not_and_any_of_bound_row_evidence(self):
        schema = {"items": {"not": {"anyOf": [{"required": ["a"]}, {"required": ["b"]}]}}}
        self.assertEqual(validate([{"x": 1}], schema), [])
        self.assertTrue(validate([{"a": 1}], schema))
        self.assertTrue(validate([{"b": 1}], schema))
        self.assertEqual(validate({"a": 1}, {"anyOf": [{"required": ["a"]}, {"required": ["b"]}]}), [])
        self.assertTrue(validate({"c": 1}, {"anyOf": [{"required": ["a"]}, {"required": ["b"]}]}))

    def test_contains_is_existential_where_items_is_universal(self):
        # rbom/0.1 leans on this asymmetry: PARTIAL has to say "at least one row
        # carries the paired digests", which `items` cannot express (it would
        # demand it of every row, i.e. VERIFIED) and a oneOf branch cannot
        # retract from the base $defs/component.
        schema = {"type": "array", "contains": {"required": ["a", "b"]}}
        self.assertEqual(validate([{"b": 1}, {"a": 1, "b": 2}], schema), [])
        self.assertTrue(validate([{"a": 1}], schema))
        self.assertTrue(validate([{"c": 1}], schema))
        self.assertTrue(validate([], schema))
        # counted existence stays deliberately unimplemented
        with self.assertRaises(UnsupportedKeyword):
            validate([1], {"contains": {"type": "integer"}, "minContains": 2})

    def test_property_names_bounds_keys_while_additional_properties_bounds_values(self):
        # Both halves are load-bearing and neither substitutes for the other:
        # propertyNames alone would let {"verifier": "FAIL"} through, and
        # additionalProperties-as-schema alone would let {"future": "PASS"} in.
        schema = {
            "type": "object",
            "propertyNames": {"enum": ["verifier", "execution"]},
            "additionalProperties": {"enum": ["PASS", "N/A"]},
        }
        self.assertEqual(validate({"verifier": "PASS"}, schema), [])
        self.assertTrue(validate({"future": "PASS"}, schema))
        self.assertTrue(validate({"verifier": "FAIL"}, schema))


class ContractSurfaceTest(unittest.TestCase):
    """The evaluator's coverage claim is a machine-checked invariant, not prose.

    ``ari_schema_check`` advertises that it implements exactly the keywords the
    ARI contracts use. Left as a comment, that claim rots the moment a contract
    grows a keyword — and the rot is invisible, because an unimplemented keyword
    either raises on a path no test walks or, worse, sits in a branch the
    evaluator never reaches. Walking every published contract and failing on any
    keyword outside the implemented surface is what makes thread eleven
    structurally impossible rather than merely unlikely.
    """

    def test_every_published_contract_exists_and_parses(self):
        for discriminator, path in DOCUMENT_CONTRACTS.items():
            with self.subTest(contract=discriminator):
                self.assertTrue(path.is_file(), path)
                contract = json.loads(path.read_text(encoding="utf-8"))
                self.assertEqual(contract["$schema"], "https://json-schema.org/draft/2020-12/schema")

    def test_no_contract_keyword_falls_outside_the_implemented_surface(self):
        used: set = set()
        for path in DOCUMENT_CONTRACTS.values():
            _collect_keywords(json.loads(path.read_text(encoding="utf-8")), used)
        vocabulary = used & DRAFT_2020_12_VOCABULARY
        self.assertTrue(vocabulary, "the contract walk collected no vocabulary at all")
        missing = vocabulary - SUPPORTED_KEYWORDS - ANNOTATION_KEYWORDS
        self.assertEqual(
            missing,
            set(),
            "published contracts use keywords the bounded evaluator does not implement: "
            + ", ".join(sorted(missing)),
        )

    def test_the_surface_test_itself_would_catch_a_new_keyword(self):
        # Guards the guard: a contract that grew `format` would have to be caught,
        # so the walk has to actually see nested keyword positions.
        used: set = set()
        _collect_keywords({"properties": {"a": {"format": "date-time"}}}, used)
        self.assertIn("format", used & DRAFT_2020_12_VOCABULARY)


class DocumentContractInteropTest(unittest.TestCase):
    """The stdlib checker validates the real document contracts end to end.

    Registry interop only ever exercised ``release-registry/1.0``, whose entry
    body is deliberately opaque. The three source contracts carry the actual
    vocabulary — ``minProperties``, ``propertyNames`` and a schema-valued
    ``additionalProperties`` — and each of those was, until now, either
    loud-failing or silently permissive. The mutations below are the precise
    holes: each one is rejected only by the keyword that motivated the fix, so a
    regression in any of them fails here rather than in a reviewer's thread.
    """

    def contract(self, discriminator):
        return json.loads(DOCUMENT_CONTRACTS[discriminator].read_text(encoding="utf-8"))

    def test_reference_implementation_documents_validate_against_their_contracts(self):
        for discriminator, document in (
            ("aftergraph-component/1.0", COMPONENT),
            ("compatibility-edge/1.0", EDGE),
            ("release-passport/1.0", PASSPORT),
        ):
            with self.subTest(contract=discriminator):
                self.assertEqual(document["schema"], discriminator)
                self.assertEqual(validate(copy.deepcopy(document), self.contract(discriminator)), [])

    def test_property_names_rejects_a_malformed_contract_key(self):
        # `contracts` is an open object, so only propertyNames can pin its keys;
        # additionalProperties-as-schema alone would wave this through.
        document = copy.deepcopy(COMPONENT)
        document["contracts"] = {"Verdict": "1.0"}
        errors = validate(document, self.contract("aftergraph-component/1.0"))
        self.assertTrue(errors)
        self.assertTrue(any("propertyNames" in str(errors) or "Verdict" in error for error in errors), errors)

    def test_additional_properties_schema_pins_the_passport_profile_vocabulary(self):
        # A PASS passport carrying a FAIL profile is refused by the reference
        # implementation; the contract has to refuse it too, and only the
        # schema-valued additionalProperties can.
        document = copy.deepcopy(PASSPORT)
        document["conformance"]["profiles"] = {"verifier": "FAIL"}
        self.assertTrue(validate(document, self.contract("release-passport/1.0")))

    def test_min_properties_rejects_an_empty_passport_profile_set(self):
        document = copy.deepcopy(PASSPORT)
        document["conformance"]["profiles"] = {}
        errors = validate(document, self.contract("release-passport/1.0"))
        self.assertTrue(errors)
        self.assertTrue(any("minProperties" in error or "properties" in error for error in errors), errors)

    def test_property_names_restricts_passport_profile_keys_to_apc_1(self):
        # validate_passport() already refuses a profile outside APC_PROFILES
        # (scripts/ari_model.py:344), so a contract-only consumer was the weaker
        # of the two and accepted a passport that Registry ingestion rejects.
        document = copy.deepcopy(PASSPORT)
        document["conformance"]["profiles"] = {"future-profile": "PASS"}
        errors = validate(document, self.contract("release-passport/1.0"))
        self.assertTrue(errors)
        self.assertTrue(any("future-profile" in error for error in errors), errors)

        # Control: the value pin still has to work on its own, so the key pin did
        # not mask it — an in-vocabulary key with a non-positive state is refused
        # by additionalProperties and not by propertyNames.
        document = copy.deepcopy(PASSPORT)
        document["conformance"]["profiles"] = {"verifier": "FAIL"}
        errors = validate(document, self.contract("release-passport/1.0"))
        self.assertTrue(errors)
        self.assertTrue(
            any("FAIL" in error and "(name)" not in error for error in errors), errors
        )

    def test_passport_subject_component_is_pinned_to_the_identifier_grammar(self):
        # Document-level mirror of the structural pattern-tie test: a passport
        # whose component name leaves the APC-1 identifier grammar is now refused
        # by the published contract, not only by validate_passport()
        # (thread 6kC1X6). Before the pin, every one of these validated against
        # release-passport/1.0 while Registry ingestion rejected it.
        for bad in ("Bad_Name", "UPPERCASE", "-leading-hyphen", "with space", "under_score"):
            document = copy.deepcopy(PASSPORT)
            document["subject"]["component"] = bad
            with self.subTest(component=bad):
                self.assertTrue(validate(document, self.contract("release-passport/1.0")))
        # Control: the reference fixture still conforms, so the pin closes the
        # hole without closing truth.
        self.assertEqual(
            validate(copy.deepcopy(PASSPORT), self.contract("release-passport/1.0")), []
        )

    def test_edge_evidence_still_bounds_its_own_contract(self):
        document = copy.deepcopy(EDGE)
        document["evidence"] = []
        self.assertTrue(validate(document, self.contract("compatibility-edge/1.0")))
        document = copy.deepcopy(EDGE)
        document["evidence"] = [{"kind": "test-receipt"}]
        self.assertTrue(validate(document, self.contract("compatibility-edge/1.0")))


if __name__ == "__main__":
    unittest.main()