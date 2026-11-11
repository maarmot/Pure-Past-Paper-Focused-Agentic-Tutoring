"""Requirements-based tests for the public evidence checker (standard library only).

The miniature bundle is independent of the experiment's real tutor replies.
Expected counts below are literal hand counts: one case/phase, five criteria,
three or five samples/version. Corruptions edit isolated temporary copies only.
"""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


HERE = Path(__file__).resolve().parent
CHECKER = HERE / "check_results.py"
CRITERIA = {
    "correctness": "Correct under supplied facts.",
    "responsiveness": "Answer the actual question.",
    "next_action": "A useful next action when needed.",
    "help_level": "Respect requested assistance.",
    "area_requirement": "Meet this case's area requirement.",
}
FROZEN_NAMES = (
    "heldout.json", "development.json", "fixture.json", "protocol.json",
    "beam_reference.json",
)
BEAM_LITERALS = {
    "B1_initial_r": 0.04875,
    "B1_initial_error": 0.0464839094159714,
    "B1_corrected_r": 0.00195,
    "B1_corrected_error": 0.00194620490044413,
    "B2_r": 0.03192,
    "B2_error": 0.0309326304364679,
    "D2_r": 0.0866666666666667,
    "D2_error": 0.0797546012269939,
}


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8")


def refresh_freeze(root):
    write(root / "freeze.json", {
        name: hashlib.sha256((root / name).read_bytes()).hexdigest()
        for name in FROZEN_NAMES
    })


def make_bundle(root):
    fixture = {"status": "Entirely synthetic validator test fixture."}
    protocol = {
        "baseline_commit": "a" * 40,
        "grading": "PASS/PARTIAL/FAIL under supplied criteria.",
        "second_grader_cases": ["A3"],
        "frozen_inputs": ["heldout.json", "development.json", "fixture.json",
                          "beam_reference.json"],
        "improvement_rule": (
            "For each area, stronger if PASS>=baseline and FAIL<=baseline "
            "with at least one strict difference, and correctness/help-level "
            "failures do not increase. Equal profile unchanged; conflicting "
            "differences mixed; Pareto deterioration weaker."
        ),
    }
    write(root / "fixture.json", fixture)
    write(root / "protocol.json", protocol)
    write(root / "beam_reference.json", {"literal_reference": BEAM_LITERALS})
    write(root / "instruction-manifest.json", {
        "baseline": {"commit": "a" * 40, "files": {"SKILL.md": "b" * 64}},
        "candidate": {"base_commit": "a" * 40, "files": {"SKILL.md": "c" * 64}},
        "conditions": {"model": "Test fixture only."},
    })
    for phase, case_id, sample_count in (
            ("heldout", "A3", 3), ("development", "D1", 5)):
        case = {"id": case_id, "area": "essay", "messages": ["Question?"],
                "expected_facts": ["A test fact."], "criteria": CRITERIA}
        write(root / (phase + ".json"), [case])
        replies, key, ratings = {}, {}, {}
        for index in range(2 * sample_count):
            slot = chr(ord("A") + index)
            version = "baseline" if index < sample_count else "candidate"
            sample = index % sample_count + 1
            replies[slot] = {
                "turns": ["Exact reply %s %s %s." % (phase, version, sample)],
                "actions": {"files_read": [], "commands": [], "files_written": []},
            }
            key[slot] = {"version": version, "sample": sample}
            ratings[slot] = {name: {"rating": "PASS", "reason": "Supplied evidence."}
                             for name in CRITERIA}
        # Deliberate non-PASS values produce nontrivial, hand-countable totals.
        if phase == "heldout":
            ratings["A"]["area_requirement"]["rating"] = "PARTIAL"
            ratings["B"]["next_action"]["rating"] = "FAIL"
        public = {"case": case, "replies": replies, "key": key,
                  "ratings": ratings}
        blind_row = {"case": case, "replies": replies}
        packet = {"fixture": fixture, "grading": protocol["grading"],
                  "cases": [blind_row]}
        write(root / "packets" / phase / "essay.json", packet)
        if phase == "heldout":
            public["second_ratings"] = copy.deepcopy(ratings)
            public["second_ratings"]["B"]["next_action"]["rating"] = "PARTIAL"
            write(root / "packets" / phase / "second-review.json", packet)
        write(root / phase / (case_id + ".json"), public)
    refresh_freeze(root)


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        make_bundle(self.root)

    def tearDown(self):
        self.temp.cleanup()

    def run_checker(self):
        return subprocess.run([sys.executable, str(CHECKER), "--root", str(self.root)],
                              capture_output=True, text=True, encoding="utf-8")

    def expect_rejection(self, diagnostic):
        result = self.run_checker()
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertTrue(result.stdout.strip().startswith("{"),
                        "Expected JSON validation diagnostic, got: " + result.stderr)
        error = json.loads(result.stdout)
        self.assertFalse(error["valid"])
        self.assertIn(diagnostic, "\n".join(error["errors"]))

    def edit(self, relative, mutate):
        path = self.root / relative
        data = read(path)
        mutate(data)
        write(path, data)

    def test_valid_bundle_recomputes_literal_counts_and_retains_disagreement(self):
        # Dropping a rating or suppressing the second reviewer breaks these counts.
        result = self.run_checker()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        report = json.loads(result.stdout)
        self.assertTrue(report["valid"])
        heldout = report["phases"]["heldout"]
        self.assertEqual(heldout["by_area"]["essay"]["baseline"],
                         {"PASS": 13, "PARTIAL": 1, "FAIL": 1})
        self.assertEqual(heldout["by_area"]["essay"]["candidate"],
                         {"PASS": 15, "PARTIAL": 0, "FAIL": 0})
        self.assertEqual(heldout["by_criterion"]["next_action"]["baseline"],
                         {"PASS": 2, "PARTIAL": 0, "FAIL": 1})
        self.assertEqual(report["phases"]["development"]["aggregate"]["baseline"],
                         {"PASS": 25, "PARTIAL": 0, "FAIL": 0})
        self.assertEqual(heldout["comparisons"]["essay"]["classification"], "stronger")
        self.assertEqual(len(report["second_review"]["disagreements"]), 1)
        disagreement = report["second_review"]["disagreements"][0]
        self.assertEqual((disagreement["case"], disagreement["slot"],
                          disagreement["criterion"], disagreement["primary"]["rating"],
                          disagreement["secondary"]["rating"]),
                         ("A3", "B", "next_action", "FAIL", "PARTIAL"))
        # These are hand-reduced fractions, independent of the checker helpers.
        self.assertEqual(report["beam_check"]["B1_initial"]["r_exact"], "39/800")
        self.assertEqual(report["beam_check"]["B1_initial"]["error_exact"], "39/839")
        self.assertEqual(report["beam_check"]["B2"]["r_exact"], "399/12500")
        self.assertEqual(report["beam_check"]["B2"]["error_exact"], "399/12899")
        self.assertEqual(report["beam_check"]["D2"]["error_exact"], "13/163")

    def test_rejects_missing_criterion_grade(self):
        self.edit("heldout/A3.json", lambda d: d["ratings"]["A"].pop("correctness"))
        self.expect_rejection("criterion")

    def test_rejects_duplicate_version_sample_mapping(self):
        self.edit("heldout/A3.json", lambda d: d["key"].update(A=d["key"]["B"]))
        self.expect_rejection("version/sample")

    def test_rejects_public_reply_changed_after_blind_packet(self):
        self.edit("heldout/A3.json", lambda d: d["replies"]["A"]["turns"].__setitem__(0, "Changed."))
        self.expect_rejection("packet")

    def test_rejects_packet_changed_after_public_reply(self):
        self.edit("packets/heldout/essay.json", lambda d: d["cases"][0]["replies"]["A"]["turns"].__setitem__(0, "Changed."))
        self.expect_rejection("packet")

    def test_rejects_altered_frozen_input(self):
        self.edit("fixture.json", lambda d: d.update(status="Changed."))
        self.expect_rejection("SHA-256")

    def test_rejects_empty_reason(self):
        self.edit("heldout/A3.json", lambda d: d["ratings"]["A"]["correctness"].update(reason="  "))
        self.expect_rejection("reason")

    def test_rejects_invalid_rating(self):
        self.edit("heldout/A3.json", lambda d: d["ratings"]["A"]["correctness"].update(rating="GOOD"))
        self.expect_rejection("rating")

    def test_rejects_missing_turn(self):
        self.edit("heldout/A3.json", lambda d: d["replies"]["A"].update(turns=[]))
        self.expect_rejection("turn")

    def test_rejects_missing_second_grade(self):
        self.edit("heldout/A3.json", lambda d: d["second_ratings"].pop("F"))
        self.expect_rejection("second_ratings")

    def test_rejects_second_packet_with_different_exact_reply(self):
        self.edit("packets/heldout/second-review.json", lambda d: d["cases"][0]["replies"]["F"]["turns"].__setitem__(0, "Changed."))
        self.expect_rejection("packet")

    def test_rejects_case_changed_in_public_row(self):
        self.edit("heldout/A3.json", lambda d: d["case"]["messages"].__setitem__(0, "Changed question?"))
        self.expect_rejection("frozen case")

    def test_rejects_packet_fixture_even_if_all_replies_match(self):
        self.edit("packets/heldout/essay.json", lambda d: d["fixture"].update(status="Changed."))
        self.expect_rejection("fixture")

    def test_rejects_unblinded_packet_metadata(self):
        self.edit("packets/heldout/essay.json", lambda d: d["cases"][0].update(key={"A": "candidate"}))
        self.expect_rejection("case/replies")

    def test_rejects_extra_public_case(self):
        write(self.root / "heldout" / "unexpected.json", read(self.root / "heldout/A3.json"))
        self.expect_rejection("case files")

    def test_rejects_wrong_error_denominator_despite_refrozen_reference(self):
        self.edit("beam_reference.json", lambda d: d["literal_reference"].update(B1_initial_error=0.04875))
        refresh_freeze(self.root)
        self.expect_rejection("B1_initial_error")

    def test_rejects_cantilever_coefficient_for_simply_supported_beam(self):
        # Wrong factor 3 instead of 12 gives .00798. Re-freezing prevents a hash
        # rejection from concealing a missing independent mathematical check.
        self.edit("beam_reference.json", lambda d: d["literal_reference"].update(B2_r=0.00798))
        refresh_freeze(self.root)
        self.expect_rejection("B2_r")

    def test_rejects_instruction_hash_with_invalid_hex(self):
        self.edit("instruction-manifest.json", lambda d: d["candidate"]["files"].update({"SKILL.md": "not-a-hash"}))
        self.expect_rejection("instruction-manifest")

    def test_rejects_instruction_baseline_commit_mismatch(self):
        self.edit("instruction-manifest.json", lambda d: d["baseline"].update(commit="d" * 40))
        self.expect_rejection("baseline commit")

    def test_equal_profile_with_correctness_regression_is_mixed(self):
        self.edit("heldout/A3.json", lambda d: d["ratings"]["D"]["area_requirement"].update(rating="PARTIAL"))
        self.edit("heldout/A3.json", lambda d: d["ratings"]["E"]["correctness"].update(rating="FAIL"))
        result = self.run_checker()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        comparison = json.loads(result.stdout)["phases"]["heldout"]["comparisons"]["essay"]
        self.assertEqual(comparison["classification"], "mixed")
        self.assertFalse(comparison["guard_passed"])
        self.assertEqual(comparison["guard_failures"], ["correctness"])

    def test_exact_packet_fixture_does_not_equate_boolean_with_number(self):
        # Python's ordinary object equality treats True == 1; exact retained JSON
        # must preserve the distinction rather than silently accept this change.
        self.edit("fixture.json", lambda d: d.update(flag=1))
        refresh_freeze(self.root)
        for relative in ("packets/heldout/essay.json", "packets/heldout/second-review.json",
                         "packets/development/essay.json"):
            self.edit(relative, lambda d: d["fixture"].update(flag=True))
        self.expect_rejection("fixture")

    def test_rejects_duplicate_json_keys_in_public_results(self):
        path = self.root / "heldout/A3.json"
        text = path.read_text(encoding="utf-8")
        path.write_text(text.replace('"ratings": {', '"ratings": {}, "ratings": {', 1),
                        encoding="utf-8")
        self.expect_rejection("Duplicate JSON object key")

    def test_rejects_nonscalar_protocol_input_names_with_json_diagnostic(self):
        self.edit("protocol.json", lambda d: d.update(frozen_inputs=[["heldout.json"]]))
        refresh_freeze(self.root)
        self.expect_rejection("Frozen protocol input list")

    def test_rejects_nonobject_beam_reference_with_json_diagnostic(self):
        write(self.root / "beam_reference.json", [])
        refresh_freeze(self.root)
        self.expect_rejection("beam_reference")

    def add_rubric_review(self):
        """Only this independent temporary fixture supplies review expectations."""
        row = read(self.root / "heldout/A3.json")
        grades = copy.deepcopy(row["ratings"])
        grades["A"]["area_requirement"] = {"rating": "PASS", "reason": "Clarified test interpretation."}
        grades["B"]["next_action"] = {"rating": "PASS", "reason": "Clarified test interpretation."}
        review = {"case_id": "A3", "interpretation": "Synthetic clarified reading.",
                  "ambiguity": "Two synthetic readings were possible.",
                  "grades": {"A3": grades}, "explanation": "Optional explanatory metadata."}
        write(self.root / "rubric-review.json", review)
        packet = read(self.root / "packets/heldout/essay.json")
        write(self.root / "rubric-review/packet.json", packet)

    def test_optional_rubric_review_reports_sensitivity_without_replacing_primary(self):
        self.add_rubric_review()
        result = self.run_checker()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        report = json.loads(result.stdout)
        self.assertIn("rubric_review", report)
        review = report["rubric_review"]
        literal_primary = {"PASS": 13, "PARTIAL": 1, "FAIL": 1}
        self.assertEqual(report["phases"]["heldout"]["aggregate"]["baseline"], literal_primary)
        self.assertEqual(review["original_case_summary"]["aggregate"]["baseline"], literal_primary)
        self.assertEqual(review["clarified_case_summary"]["aggregate"]["baseline"],
                         {"PASS": 15, "PARTIAL": 0, "FAIL": 0})
        self.assertEqual(review["heldout_sensitivity"]["aggregate"]["baseline"],
                         {"PASS": 15, "PARTIAL": 0, "FAIL": 0})
        self.assertEqual(review["case_id"], "A3")
        self.assertEqual(review["interpretation"], "Synthetic clarified reading.")
        self.assertEqual(review["ambiguity"], "Two synthetic readings were possible.")
        disagreements = report["second_review"]["disagreements"]
        self.assertEqual(len(disagreements), 1)
        self.assertEqual(disagreements[0]["primary"]["rating"], "FAIL")
        self.assertEqual(disagreements[0]["secondary"]["rating"], "PARTIAL")

    def test_rejects_changed_rubric_review_packet(self):
        self.add_rubric_review()
        self.edit("rubric-review/packet.json", lambda d: d["cases"][0]["replies"]["A"]["turns"].__setitem__(0, "Changed."))
        self.expect_rejection("rubric-review/packet.json")

    def test_rejects_incomplete_rubric_review_grade(self):
        self.add_rubric_review()
        self.edit("rubric-review.json", lambda d: d["grades"]["A3"]["A"].pop("help_level"))
        self.expect_rejection("criterion")

    def test_rejects_rubric_review_with_missing_case_id(self):
        self.add_rubric_review()
        self.edit("rubric-review.json", lambda d: d.pop("case_id"))
        self.expect_rejection("case_id")

    def test_rejects_rubric_review_with_unknown_case_id(self):
        self.add_rubric_review()
        self.edit("rubric-review.json", lambda d: d.update(case_id="unknown"))
        self.expect_rejection("heldout case")

    def test_rejects_orphan_rubric_review_packet(self):
        self.add_rubric_review()
        (self.root / "rubric-review.json").unlink()
        self.expect_rejection("without rubric-review.json")

    def test_rejects_rubric_review_without_packet(self):
        self.add_rubric_review()
        (self.root / "rubric-review/packet.json").unlink()
        self.expect_rejection("rubric-review/packet.json")

    def test_rejects_blank_rubric_review_interpretation(self):
        self.add_rubric_review()
        self.edit("rubric-review.json", lambda d: d.update(interpretation=" "))
        self.expect_rejection("interpretation")

    def test_rejects_blank_rubric_review_ambiguity(self):
        self.add_rubric_review()
        self.edit("rubric-review.json", lambda d: d.update(ambiguity=" "))
        self.expect_rejection("ambiguity")


if __name__ == "__main__":
    unittest.main(verbosity=2)
