"""Controlled faults applied to copies of the exact frozen records."""
from pathlib import Path
import shutil
import tempfile
import unittest

from check import HERE, check_freeze, run
from evaluate import read, write


class EvidenceFaults(unittest.TestCase):
    def setUp(self):
        container = tempfile.TemporaryDirectory()
        self.addCleanup(container.cleanup)
        self.root = Path(container.name) / "evidence-copy"
        self.root.mkdir()
        for file in ("freeze.json","protocol.json","development.json","heldout.json","reserve.json",
                     "targeted-freeze.json","targeted.json","targeted-plan.json"):
            shutil.copyfile(HERE / file, self.root / file)
        shutil.copytree(HERE / "evidence", self.root / "evidence")

    def mutate(self, relative, action):
        p = self.root / relative
        value = read(p)
        action(value)
        write(p, value)

    def test_unmodified_records(self):
        check_freeze(self.root)
        self.assertEqual(run(self.root, "heldout")["turns_per_arm"], 14)

    def test_changed_criterion(self):
        self.mutate("heldout.json", lambda rows: rows[0]["criteria"].pop())
        with self.assertRaisesRegex(ValueError, "Changed frozen"):
            check_freeze(self.root)

    def test_changed_targeted_criterion(self):
        self.mutate("targeted.json", lambda rows: rows[0]["criteria"].pop())
        with self.assertRaisesRegex(ValueError, "Changed targeted"):
            check_freeze(self.root)

    def test_swapped_answers(self):
        self.mutate("evidence/packets/heldout.json", lambda rows: rows[1]["samples"]["X"][0].update(tutor="x"))
        with self.assertRaisesRegex(ValueError, "masked packet"):
            run(self.root, "heldout")

    def test_missing_last_turn(self):
        self.mutate("evidence/runs/baseline/H2.json", lambda item: item["turns"].pop())
        with self.assertRaisesRegex(ValueError, "Incomplete turns"):
            run(self.root, "heldout")

    def test_duplicate_grade(self):
        self.mutate("evidence/grades/heldout-primary.json", lambda g: g["grade"]["items"].append(g["grade"]["items"][0]))
        with self.assertRaisesRegex(ValueError, "Duplicate grade"):
            run(self.root, "heldout")

    def test_invalid_permutation(self):
        self.mutate("evidence/keys/heldout.json", lambda keys: keys["H2"].update(Y=keys["H2"]["X"]))
        with self.assertRaisesRegex(ValueError, "permutations"):
            run(self.root, "heldout")

    def test_wrong_grader_packet(self):
        self.mutate("evidence/grades/heldout-second.json", lambda g: g["metrics"].update(prompt_sha256="x"))
        with self.assertRaisesRegex(ValueError, "grading packet"):
            run(self.root, "heldout")

    def test_duplicate_json_key(self):
        destination = self.root / "broken.json"
        destination.write_text('{"rating":"P","rating":"F"}', encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
            read(destination)


if __name__ == "__main__":
    unittest.main()
