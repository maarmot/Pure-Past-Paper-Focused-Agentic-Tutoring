"""Controlled faults against copies of the scored evidence."""
import json
from pathlib import Path
import shutil
import tempfile
import unittest

from check_results import HERE, inspect

class EvidenceTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        for filename in ("heldout.json", "development.json", "freeze.json", "protocol.json", "key.json"):
            shutil.copyfile(HERE/filename, self.root/filename)
        for directory in ("packets", "grades", "replies"):
            shutil.copytree(HERE/directory, self.root/directory)

    def mutate(self, filename, edit):
        path = self.root/filename
        doc = json.loads(path.read_text(encoding="utf-8"))
        edit(doc)
        path.write_text(json.dumps(doc), encoding="utf-8")
        with self.assertRaises((ValueError, KeyError)):
            inspect(self.root)

    def test_frozen_prompt_tampering(self):
        self.mutate("heldout.json", lambda doc: doc[1].update(prompt="wrong"))

    def test_missing_transcript(self):
        self.mutate("replies/baseline-h1.json", lambda doc: doc.pop("Q1"))

    def test_duplicate_identity(self):
        self.mutate("key.json", lambda doc: doc["Q1"].update(A=doc["Q1"]["B"]))

    def test_omitted_letter(self):
        self.mutate("grades/primary1.json", lambda doc: doc["Q1"].pop("A"))

    def test_missing_criterion(self):
        self.mutate("grades/primary1.json", lambda doc: doc["Q1"]["A"].pop())

    def test_invalid_grade(self):
        self.mutate("grades/primary1.json", lambda doc: doc["Q1"]["A"][0].__setitem__(0,"maybe"))

    def test_substituted_reply(self):
        self.mutate("packets/primary2.json", lambda doc: doc["Q8"]["responses"].update(A="another reply"))

    def test_duplicate_json_key(self):
        path = self.root/"grades"/"primary1.json"
        raw = path.read_text(encoding="utf-8")
        self.assertTrue(raw.lstrip().startswith("{"))
        path.write_text(raw.replace("{", '{"Q1": {},', 1), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
            inspect(self.root)

class FollowupEvidenceTests(unittest.TestCase):
    def rejected(self, relative_path, edit):
        import sys
        from unittest.mock import patch
        sys.path.insert(0, str(HERE/"followup"))
        import check_followup
        read = check_followup.read
        def changed(path):
            document = read(path)
            if path == check_followup.HERE/relative_path:
                edit(document)
            return document
        with patch.object(check_followup, "read", changed):
            with self.assertRaises((ValueError, KeyError)):
                check_followup.inspect()

    def test_followup_duplicate_assignment(self):
        self.rejected("key.json", lambda doc: doc["T1"].update(A=doc["T1"]["B"]))

    def test_followup_missing_grade(self):
        self.rejected("grades/second.json", lambda doc: doc["T2"].pop("B"))

    def test_followup_altered_replay(self):
        self.rejected("packets/replay1.json", lambda doc: doc["Q3"]["responses"].update(A="changed"))

if __name__ == "__main__":
    unittest.main()
