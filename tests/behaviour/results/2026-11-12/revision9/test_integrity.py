"""Faults must be rejected using isolated copies of the public receipts."""
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

import benchmark
import verify


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.dest = Path(temp.name)
        shutil.copytree(benchmark.HERE / "evidence", self.dest, dirs_exist_ok=True)

    def corrupt(self, file, mutator):
        path = self.dest / file
        value = benchmark.read(path)
        mutator(value)
        benchmark.write(path, value)
        with self.assertRaises(ValueError):
            benchmark.results("cycle1", self.dest)

    def test_as_published(self):
        benchmark.results("cycle1", self.dest)

    def test_freeze_requires_both_input_hashes(self):
        for name in ("protocol.json", "cases.json"):
            shutil.copyfile(benchmark.HERE / name, self.dest / name)
        receipt = benchmark.read(benchmark.HERE / "freeze.json")
        for missing in (["protocol.json"], ["cases.json"], ["protocol.json", "cases.json"]):
            hashes = {name:value for name, value in receipt["sha256"].items() if name not in missing}
            benchmark.write(self.dest / "freeze.json", {**receipt, "sha256":hashes})
            with self.subTest(missing=missing), patch.object(benchmark, "HERE", self.dest):
                with self.assertRaises(ValueError):
                    benchmark.frozen()

    def test_partial_transcript(self):
        self.corrupt("turns/r8/A2.1.json", lambda obj: obj["turns"].pop())

    def test_replaced_final_turn(self):
        self.corrupt("turns/r8/A2.1.json", lambda obj: obj["turns"][-1].update(tutor="Different answer"))

    def test_changed_prior_response(self):
        self.corrupt("turns/r8/A2.1.json", lambda obj: obj["turns"][0].update(tutor="Other history"))

    def test_wrong_grade_coverage(self):
        self.corrupt("grades/cycle1-second.json", lambda obj: obj["grade"]["items"].pop())

    def test_other_judge_prompt(self):
        self.corrupt("grades/cycle1-second.json", lambda obj: obj["metrics"].update(prompt_sha256="0"*64))

    def test_wrong_blind_key(self):
        def switch(obj):
            entry = obj["arms"]["A2.1"]
            entry["X"], entry["Y"] = entry["Y"], entry["X"]
        self.corrupt("masks/cycle1.json", switch)

    def test_missing_pair(self):
        self.corrupt("masks/cycle1.json", lambda obj: obj["arms"].pop("A1.1"))

    def test_math(self):
        verify.check_math()


if __name__ == "__main__":
    unittest.main()
