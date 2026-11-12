"""Public synthetic exchange checks, using the pre-existing PPP validator as oracle."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
BRIDGE = ROOT / "scripts/export_roadmap_event.py"
sys.path.insert(0, str(ROOT / "scripts"))
from ppp_tools import validate_record


def session():
    event = {"problem_id": "public-example", "provenance": "generated", "source": None,
             "assistance": "unknown", "outcome": "partial", "evidence": "Counted edges.",
             "attribution": "learner-statement", "transfer": False}
    return {"kind": "session", "schema_version": 1, "topic": "Synthetic fixture", "date": "2026-05-01",
            "goals": ["UNRELATED-GOAL"], "duration": {"basis": "unknown", "seconds": None},
            "next_step": "UNRELATED-NEXT", "events": [event, dict(event, evidence="UNRELATED-WORK")]}


class RoadmapExchangeTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.directory = Path(temp.name)
        self.source = self.directory / "sensitive-private-file-name.json"
        self.output = self.directory / "chosen.json"
        self.original = session()
        self.write(self.original)

    def write(self, content):
        self.source.write_text(json.dumps(content), encoding="utf-8")

    def run_bridge(self, *extra, ordinal=1):
        return subprocess.run([sys.executable, "-B", str(BRIDGE), str(self.source), "--event", str(ordinal),
                               "--skill", "trace", "--output", str(self.output), *extra],
                              capture_output=True, text=True)

    def test_minimal_legacy_projection_and_collision(self):
        self.assertEqual(validate_record(self.original, self.directory), [])
        self.assertNotEqual(self.run_bridge().returncode, 0)
        self.assertFalse(self.output.exists())
        res = self.run_bridge("--id", "legacy-A")
        self.assertEqual(res.returncode, 0, res.stderr)
        data = self.output.read_text(encoding="utf-8")
        for private in ("UNRELATED", "sensitive-private-file-name", str(self.directory)):
            self.assertNotIn(private, data + res.stderr + res.stdout)
        event = json.loads(data)["event"]
        self.assertEqual(event["response_basis"], "unknown")
        self.assertEqual(event["assistance"], "unknown")
        self.assertEqual(event["activity"], "unspecified")
        self.assertEqual(event["attempt_id"], "legacy-A")
        self.assertNotEqual(self.run_bridge("--id", "other").returncode, 0)
        self.assertEqual(self.output.read_text(encoding="utf-8"), data)
        self.assertEqual(json.loads(self.source.read_text(encoding="utf-8")), self.original)

    def test_session_identity_and_invalid_records(self):
        self.original["events"][0]["attempt_id"] = "stable"
        self.write(self.original)
        self.assertNotEqual(self.run_bridge("--id", "duplicate").returncode, 0)
        self.original["events"][1]["independent_success"] = True
        self.write(self.original)
        self.assertNotEqual(self.run_bridge().returncode, 0)
        self.write({"kind": "question-bank", "schema_version": 1, "items": []})
        self.assertNotEqual(self.run_bridge().returncode, 0)
        self.assertFalse(self.output.exists())

    @unittest.skipUnless(shutil.which("node"), "Node needed for cross-runtime round trip")
    def test_actual_browser_export_passes_existing_python_session_validator_and_returns(self):
        module_url = (ROOT / "roadmap/model.mjs").as_uri()
        script = """import { exportSession } from MODULE;
const event={attempt_id:'actual',skill_id:'trace',date:'2026-05-01',problem_id:'sample',
provenance:'generated',source:null,assistance:'none',outcome:'correct',evidence:'Counted edges.',
attribution:'observed-work',response_basis:'reasoned',transfer:false,activity:'explain',
confidence:'low',uncertainty:'Test another phase',session_ref:'opaque-1'};
const state={kind:'roadmap',schema_version:1,field:'signals',topic:'samples',
goal:{capability:'Explain samples',context:'',aids:'',timebox:'',intensity:'',success:''},
skills:[{id:'trace',title:'Trace',description:'See dots',prerequisites:[],challenge:'Change phase'}],evidence:[event]};
console.log(JSON.stringify(exportSession(state,'actual','2026-05-10')));""".replace("MODULE", json.dumps(module_url))
        res = subprocess.run(["node", "--input-type=module", "-e", script], check=True,
                             capture_output=True, text=True)
        observed = json.loads(res.stdout)
        self.assertEqual(validate_record(observed, self.directory), [])
        self.write(observed)
        result = self.run_bridge()
        self.assertEqual(result.returncode, 0, result.stderr)
        projected = json.loads(self.output.read_text(encoding="utf-8"))["event"]
        self.assertEqual(projected["attempt_id"], "actual")
        self.assertEqual(projected["activity"], "explain")
        self.assertEqual(projected["confidence"], "low")
        self.assertEqual(projected["session_ref"], "opaque-1")

    def test_python_session_projection_derives_ordered_exposure_without_copying_the_prior_content(self):
        self.original["events"][0].update(assistance="full-solution",outcome="not-attempted",evidence="PRIVATE-SHOWN")
        self.original["events"][1].update(outcome="correct",assistance="none",attribution="observed-work",
            response_basis="reasoned",attempt_id="retry",transfer=True,roadmap={"activity":"solve"})
        self.write(self.original)
        res = self.run_bridge(ordinal=2)
        self.assertEqual(res.returncode, 0, res.stderr)
        payload = self.output.read_text(encoding="utf-8")
        self.assertNotIn("PRIVATE-SHOWN", payload)
        self.assertTrue(json.loads(payload)["event"]["previously_seen"])

    @unittest.skipUnless(shutil.which("node"), "Node needed for cross-runtime round trip")
    def test_familiar_retry_stays_familiar_across_node_python_and_independent_destination(self):
        module = json.dumps((ROOT / "roadmap/model.mjs").as_uri())
        setup = """import {exportSession,parseEvidence,recordAttempt,skillState} from MODULE;
import {readFileSync} from 'node:fs';
const base={kind:'roadmap',schema_version:1,field:'Synthetic',topic:'Trace',
goal:{capability:'Read trace',context:'',aids:'',timebox:'',intensity:'',success:''},
skills:[{id:'trace',title:'Trace',description:'Trace',prerequisites:[],challenge:'Trace'}],evidence:[]};
const old={attempt_id:'old',skill_id:'trace',date:'2026-05-01',problem_id:'p',provenance:'generated',
source:null,assistance:'hint',outcome:'partial',evidence:'Needed help.',attribution:'observed-work',
response_basis:'reasoned',transfer:false,activity:'solve'};
const later={...old,attempt_id:'retry',date:'2026-05-09',outcome:'correct',assistance:'none',transfer:true};
const day='2026-05-10';""".replace("MODULE", module)

        def use_node(script, packet=""):
            result = subprocess.run(["node", "--input-type=module", "-e", setup + script],
                                    input=packet, check=True, capture_output=True, text=True)
            return json.loads(result.stdout)

        for linked in (False, True):
            for explicit_veto in (False, True):
                with self.subTest(linked=linked, explicit_veto=explicit_veto):
                    configuration = ("later.retrieval_from='old';" if linked else "") + (
                        "later.independent_success=false;" if explicit_veto else "")
                    exported = use_node(configuration + """
const s=recordAttempt(recordAttempt(base,old,day),later,day);
console.log(JSON.stringify(exportSession(s,'retry',day)));""")
                    self.assertEqual(validate_record(exported, self.directory), [])
                    self.assertFalse(exported["events"][0]["independent_success"])
                    self.assertFalse(exported["events"][0]["transfer"])
                    self.write(exported)
                    self.output.unlink(missing_ok=True)
                    res = self.run_bridge()
                    self.assertEqual(res.returncode, 0, res.stderr)
                    imported = self.output.read_text(encoding="utf-8")
                    result = use_node("""
const item=parseEvidence(readFileSync(0,'utf8'),day);
let emptyAccepted=true;
try {recordAttempt(base,item,day);}catch {emptyAccepted=false;}
const s=recordAttempt(item.retrieval_from ? recordAttempt(base,old,day) : base,item,day);
console.log(JSON.stringify({emptyAccepted,gates:skillState(s,'trace',day).gates}));""", imported)
                    self.assertEqual(result, {"emptyAccepted": not linked,
                        "gates":{"explain":False, "solve":False, "transfer":False, "delayed":linked and not explicit_veto}})

    def test_invalid_scoped_retrieval_override_is_rejected(self):
        self.original["events"][0]["roadmap"] = {"retrieval_eligible":True, "previously_seen":True}
        self.write(self.original)
        self.assertNotEqual(self.run_bridge("--id","legacy-A").returncode, 0)
        self.assertFalse(self.output.exists())
