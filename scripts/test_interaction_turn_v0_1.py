import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "docs/contracts/interaction-turn/0.1.json"
BINDING = ROOT / "docs/INTERACTION-TURN-V1.md"

class InteractionTurnContractTests(unittest.TestCase):
    def load_schema(self):
        return json.loads(SCHEMA.read_text())

    def test_contract_exists_and_is_strict(self):
        schema = self.load_schema()
        self.assertEqual(schema["properties"]["schema"]["const"], "interaction-turn/0.1")
        self.assertFalse(schema["additionalProperties"])
        self.assertEqual(schema["properties"]["kind"]["enum"], [
            "thread_open", "turn_submit", "turn_event", "turn_cancel",
            "handoff_checkpoint", "thread_close"
        ])

    def test_contract_keeps_canonical_payloads_by_reference(self):
        schema = self.load_schema()
        properties = schema["properties"]
        for forbidden in ["mission", "work", "approval", "verification", "memory", "authority"]:
            self.assertNotIn(forbidden, properties)
        self.assertIn("context_refs", properties)
        self.assertIn("payload_ref", properties)
        self.assertIn("lineage_refs", properties)


class InteractionTurnSemanticTests(unittest.TestCase):
    def setUp(self):
        self.schema = json.loads(SCHEMA.read_text())

    def required_for(self, kind):
        required=set(self.schema["required"])
        for clause in self.schema["allOf"]:
            props=clause.get("if",{}).get("properties",{})
            if props.get("kind",{}).get("const")==kind and set(props)=={"kind"}:
                required.update(clause["then"].get("required",[]))
        return required

    def test_each_operation_has_owner_safe_required_fields(self):
        self.assertIn("idempotency_key",self.required_for("thread_open"))
        self.assertNotIn("thread_ref",self.required_for("thread_open"))
        self.assertTrue({"thread_ref","idempotency_key","input_parts"} <= self.required_for("turn_submit"))
        self.assertNotIn("turn_ref",self.required_for("turn_submit"))
        self.assertTrue({"thread_ref","sequence","cursor","event_type"} <= self.required_for("turn_event"))
        self.assertNotIn("turn_ref",self.required_for("turn_event"))
        self.assertTrue({"turn_ref","cancel_scope"} <= self.required_for("turn_cancel"))
        self.assertTrue({"handoff_checkpoint_ref","destination_readmission_ref"} <= self.required_for("handoff_checkpoint"))

    def test_handoff_forbids_moved_authority(self):
        self.assertEqual(self.schema["properties"]["authority_transport"], {"const": False})
        self.assertEqual(self.schema["properties"]["claims_authority"], {"const": False})

    def test_effect_requires_external_grant_reference(self):
        branch=next(x for x in self.schema["allOf"] if x.get("if",{}).get("properties",{}).get("egress_effect"))
        self.assertIn("grant_ref",branch["then"]["required"])

class InteractionTurnInstanceTests(unittest.TestCase):
    def setUp(self):
        import jsonschema
        self.jsonschema=jsonschema
        self.schema=json.loads(SCHEMA.read_text())
        self.base={
            "schema":"interaction-turn/0.1",
            "kind":"turn_submit",
            "tenant_id":"ten_"+"1"*32,
            "surface_ref":"studio:web",
            "thread_ref":"thr_01",
            "principal_ref":"prn_01",
            "admission_ref":"tg:adm:01",
            "trace_id":"trc_"+"2"*32,
            "claims_authority":False,
            "purpose":"user-request",
            "lineage_refs":["evt:root"],
            "created_at":"2026-09-12T08:00:00Z",
            "idempotency_key":"idem-01",
            "modality":"text",
            "input_parts":[{"kind":"text","text":"hello"}],
        }

    def test_valid_text_turn_submit_conforms(self):
        self.jsonschema.Draft202012Validator(self.schema).validate(self.base)

    def test_unknown_fields_and_authority_claim_fail_closed(self):
        with self.assertRaises(self.jsonschema.ValidationError):
            self.jsonschema.Draft202012Validator(self.schema).validate({**self.base,"unexpected":1})
        with self.assertRaises(self.jsonschema.ValidationError):
            self.jsonschema.Draft202012Validator(self.schema).validate({**self.base,"claims_authority":True})

    def test_effect_requires_grant_reference(self):
        with self.assertRaises(self.jsonschema.ValidationError):
            self.jsonschema.Draft202012Validator(self.schema).validate({**self.base,"egress_effect":True})
        self.jsonschema.Draft202012Validator(self.schema).validate({**self.base,"egress_effect":True,"grant_ref":"tg:grant:01"})

    def test_thread_lifecycle_events_do_not_require_turn_ref(self):
        common={k:v for k,v in self.base.items() if k not in {"idempotency_key","modality","input_parts"}}
        for event_type in ["thread_opened","thread_closed"]:
            event={**common,"kind":"turn_event","event_type":event_type,"sequence":1,"cursor":1}
            self.jsonschema.Draft202012Validator(self.schema).validate(event)
        with self.assertRaises(self.jsonschema.ValidationError):
            self.jsonschema.Draft202012Validator(self.schema).validate({**common,"kind":"turn_event","event_type":"turn_accepted","sequence":1,"cursor":1})


class InteractionTurnBindingTests(unittest.TestCase):
    def test_binding_preserves_canonical_owners(self):
        text=BINDING.read_text()
        self.assertIn("Runtime owns InteractionThread continuity and InteractionTurn orchestration",text)
        self.assertIn("Studio owns InteractionSurface experience",text)
        self.assertIn("Trust Gateway owns admission",text)
        self.assertIn("WORKS owns durable consequential work",text)

    def test_owner_requests_exist(self):
        self.assertTrue((ROOT / "docs/superpowers/requests/interaction-runtime-v1.md").is_file())
        self.assertTrue((ROOT / "docs/superpowers/requests/interaction-studio-v1.md").is_file())

if __name__ == "__main__":
    unittest.main(verbosity=2)
