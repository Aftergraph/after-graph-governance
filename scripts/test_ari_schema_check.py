import unittest

from scripts.ari_schema_check import SUPPORTED_KEYWORDS, UnsupportedKeyword, validate


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
        for keyword in ("not", "if", "then", "else", "allOf", "anyOf", "format", "contains", "required"):
            if keyword in SUPPORTED_KEYWORDS:
                continue
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


if __name__ == "__main__":
    unittest.main()